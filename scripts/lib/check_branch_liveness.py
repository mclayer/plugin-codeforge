#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [observability]
# check_branch_liveness.py — CFP-2772 Phase 2: 외부 watchdog 3-state 판정 SSOT (D2/D3)
#
# 설계 SSOT: ADR-164 §결정 5(monotonic seq 3-state + watchdog-own-clock + fail-open 금지) /
#   §결정 6(lane 임계 baseline PROPOSAL + waiting-external idle-relaxation + INV-L1 total-deadline ceiling) /
#   §결정 7(meta-observer Tier 2 last-run marker) / §결정 8(born-safe bound — byte/line-cap, no backtracking)
#   + internal-docs change-plan cfp-2772 §4.2/§4.3(parse 계약) / §7 T-HB-2/T-HB-8 / §8(테스트 계약).
#
# 역할 (D2 watchdog + D3 3-state):
#   Jira per-branch heartbeat relay 코멘트 본문(⟦cf-orch⟧ HEARTBEAT …)을 read-only 로 파싱해,
#   watchdog 자기 수신시각(OWN clock) + durable ack cursor 로 브랜치별 3-state 를 판정한다.
#   thin wrapper(scripts/check-branch-liveness.sh, ADR-061 — Infra 소유)가 본 SSOT 를 호출한다.
#
# 핵심 불변식(crux):
#   1. seq strict-advance = 유일 "live" 증거(clock-무관). 과거 heartbeat replay → seq unchanged →
#      stalled/unknown → alive 위조 불가(§7 T-HB-2).
#   2. freshness 는 watchdog OWN clock(cursor.observed_at) 로만 — `now - emitter_ts`(코멘트 ts) cross-host
#      diff 는 절대 계산하지 않는다(§결정 5 F-5 skew trap). 코멘트 ts = 표시 전용.
#   3. fail-open 금지: unknown(부재/판독불능/malformed/regress/write-fail) ≠ fresh/PASS 자동승격
#      (§결정 5 F-6 / AC-9). unknown → verdict inconclusive, exit 0.
#   4. record-only / exit 0 ALWAYS — detection surface(게이트 아님). workflow 가 surfacing 결정.
#
# HONEST-CEILING (ADR-119 / §결정 8): "ReDoS-safe/DoS-proof/임의입력 무해" 단정 없음 — born-safe bound
#   (byte-cap 4096 / line-cap / anchored non-backtracking regex / non-blocking exit0)만 명시.

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows cp949 인코딩 차단 (ADR-061 portability). stdin 도 재구성 — '--comments -' 경로가 UTF-8
# sentinel(⟦cf-orch⟧)·한글 lane 을 default codec(cp949)로 misdecode 하면 sentinel 필터 탈락→heartbeat
# 유실. Linux/CI 는 locale UTF-8 이라 무해하나 cross-platform 강건성 위해 명시 재구성.
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_NAME = "check_branch_liveness"

# sentinel SSOT (echo-guard.sh CF_ORCH_SENTINEL byte-동일) + HEARTBEAT 토큰(MIRROR 분별, §7 T-HB-8).
CF_ORCH_SENTINEL = "⟦cf-orch⟧"
HEARTBEAT_TOKEN = "HEARTBEAT"

# born-safe bound (§결정 8) — 파서 입력 상한. anchored·non-backtracking 필드 추출.
_BYTE_CAP = 4096   # 코멘트 본문 byte 상한 초과 → skip(unparseable, never fresh).
_LINE_CAP = 8      # heartbeat = 단일 라인. 초과 → skip.

# anchored 단일-패스 필드 추출(catastrophic backtracking 없음 — 고정 접두 + bounded char-class).
_RE_BRANCH = re.compile(r"branch=([a-z0-9-]{1,200})")
_RE_SEQ = re.compile(r"seq=([0-9]{1,18})")
_RE_STORY = re.compile(r"story=([A-Za-z0-9._-]{1,64})")
_RE_LANE = re.compile(r"lane=([^\s]{1,64})")
_RE_TS = re.compile(r"ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)")
_RE_STATE = re.compile(r"state=(active|idle-yield|waiting-external(?::[a-z0-9-]+)?)")

# ── lane stale 임계 baseline (전부 PROPOSAL — §결정 6, lock-in 0) ──────────────────────
# TODO(empirical-calibration, CFP-2772 Phase 2 residual): 아래 수치는 proposal 이며 Phase 2 이후
#   실측(no-false-positive/no-false-negative)으로 보정 대상. ADR-139 도 max-wait 수치 empirical
#   미실증 인정. 어떤 "정확/최적 임계" 단정도 하지 않는다(honest-ceiling).
# floor ≈ 2× poller-jitter-upper(GH cron 5min base + peak jitter 15~30min) → 30~60min.
_FLOOR_MIN = 30
# lane(및 lane-class) → minutes. specific lane 명 + class alias 둘 다 수용.
_LANE_THRESHOLD_PROPOSAL_MIN = {
    # short / mechanical (commit·bump·single-file·swap) ≈ 30–45min
    "short": 45, "mechanical": 45,
    "배포": 45,
    # medium (구현/설계 authoring) ≈ 2–3h
    "medium": 180,
    "요구사항": 180, "설계": 180, "구현": 180, "통합테스트": 180,
    # long review (설계리뷰/구현리뷰/보안테스트 dual-peer/deep-research/Codex adversarial) ≈ 3–4h
    "long": 240, "review": 240, "deep-research": 240,
    "요구사항리뷰": 240, "설계리뷰": 240, "구현리뷰": 240, "보안테스트": 240, "배포리뷰": 240,
}
_DEFAULT_THRESHOLD_MIN = 180  # 미지 lane → medium 보수 default.
# INV-L1 total-deadline ceiling (§결정 6) — generous, ≫ lane threshold. waiting-external self-attestation
#   이 이 ceiling 을 비활성화하지 못한다(무한 외부대기도 결국 unknown 으로 표면화). PROPOSAL.
_TOTAL_DEADLINE_MIN = 1440  # 24h.

_STALL_MIN_UNCHANGED_POLLS = 2  # seq unchanged ≥2 연속 poll (AND elapsed>임계) — 둘 다 필요.


def _warn(msg: str) -> None:
    sys.stderr.write(f"[{SCRIPT_NAME}] WARN: {msg}\n")


def _parse_iso(s):
    """ISO8601(Z 또는 offset) → tz-aware datetime. 실패 → None(방어적)."""
    if not s or not isinstance(s, str):
        return None
    t = s.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _now_default() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── comment 로드 ──────────────────────────────────────────────────────────────────────
def load_comment_bodies(spec):
    """--comments 입력 → 코멘트 본문 문자열 list. '-'=stdin. JSON array(문자열/dict) 또는 JSONL 수용.
    파싱 불능은 raise 하지 않고 best-effort(honest-degrade) — 어떤 입력도 watchdog 를 crash 시키지 않음."""
    if spec == "-":
        raw = sys.stdin.read()
    else:
        try:
            raw = Path(spec).read_text(encoding="utf-8")
        except Exception as exc:
            _warn(f"--comments 판독 실패 {spec}: {exc}")
            return []
    return _coerce_bodies(raw)


def _coerce_bodies(raw: str):
    bodies = []
    stripped = raw.strip()
    if not stripped:
        return bodies
    # ① whole-JSON 시도 (array 우선)
    try:
        obj = json.loads(stripped)
    except json.JSONDecodeError:
        obj = None
    if isinstance(obj, list):
        for el in obj:
            b = _body_of(el)
            if b is not None:
                bodies.append(b)
        return bodies
    if isinstance(obj, (str, dict)):
        b = _body_of(obj)
        if b is not None:
            bodies.append(b)
        return bodies
    # ② JSONL / raw-line fallback
    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            el = json.loads(line)
            b = _body_of(el)
            bodies.append(b if b is not None else line)
        except json.JSONDecodeError:
            bodies.append(line)  # raw 본문 라인
    return bodies


def _body_of(el):
    """list/JSONL 원소 → 본문 문자열. str → 그대로 / dict → body|comment|text 키 추출 / 그 외 → None."""
    if isinstance(el, str):
        return el
    if isinstance(el, dict):
        for k in ("body", "comment", "text"):
            v = el.get(k)
            if isinstance(v, str):
                return v
    return None


# ── heartbeat 파서 (born-safe) ─────────────────────────────────────────────────────────
def parse_heartbeat(body):
    """단일 코멘트 본문 → heartbeat dict 또는 None(우리 것 아님) 또는 {'_malformed': True, 'branch': ...}.
    필터: sentinel 선두(선행 공백 허용) + HEARTBEAT 토큰. born-safe: byte/line-cap + anchored regex."""
    if not isinstance(body, str) or not body:
        return None
    if len(body.encode("utf-8", errors="replace")) > _BYTE_CAP:
        return None  # oversized → unparseable(우리 heartbeat 아님으로 취급, never fresh)
    if body.count("\n") + 1 > _LINE_CAP:
        return None
    lead = body.lstrip()
    if not lead.startswith(CF_ORCH_SENTINEL):
        return None  # non-sentinel → skip
    if HEARTBEAT_TOKEN not in lead:
        return None  # MIRROR 등 다른 sentinel 코멘트 → skip (§7 T-HB-8)
    mb = _RE_BRANCH.search(lead)
    ms = _RE_SEQ.search(lead)
    if not mb:
        # HEARTBEAT 인데 branch 미추출 → 귀속 불가 malformed(집계 불가, drop 로그).
        _warn("HEARTBEAT 코멘트에서 branch 추출 실패 — 귀속 불가(skip)")
        return None
    branch = mb.group(1)
    if not ms:
        # branch 는 알지만 seq malformed → 해당 branch unknown(silently drop 금지).
        return {"_malformed": True, "branch": branch}
    hb = {
        "_malformed": False,
        "branch": branch,
        "seq": int(ms.group(1)),
    }
    mt = _RE_STORY.search(lead)
    ml = _RE_LANE.search(lead)
    mts = _RE_TS.search(lead)
    mstate = _RE_STATE.search(lead)
    hb["story"] = mt.group(1) if mt else None
    hb["lane"] = ml.group(1) if ml else None
    hb["ts"] = mts.group(1) if mts else None  # 표시 전용 — staleness 계산에 미사용(F-5).
    hb["state"] = mstate.group(1) if mstate else "active"
    return hb


def collect_latest_per_branch(bodies):
    """본문 list → {branch: heartbeat}. 같은 branch 다수 → 최고 seq 채택(malformed 는 seq 없는 것으로
    최저 우선순위). malformed-only branch 는 malformed 마커 보존."""
    latest = {}
    for body in bodies:
        hb = parse_heartbeat(body)
        if hb is None:
            continue
        br = hb["branch"]
        cur = latest.get(br)
        if cur is None:
            latest[br] = hb
            continue
        # 유효(seq 보유) > malformed. 둘 다 유효면 최고 seq.
        if hb["_malformed"]:
            continue
        if cur["_malformed"] or hb["seq"] >= cur.get("seq", -1):
            latest[br] = hb
    return latest


# ── threshold ─────────────────────────────────────────────────────────────────────────
def load_thresholds(path):
    """built-in PROPOSAL + optional {lane: minutes} override(merge). floor clamp 적용."""
    table = dict(_LANE_THRESHOLD_PROPOSAL_MIN)
    src = "builtin-proposal"
    if path:
        try:
            override = json.loads(Path(path).read_text(encoding="utf-8"))
            if isinstance(override, dict):
                for k, v in override.items():
                    try:
                        table[str(k)] = int(v)
                    except (TypeError, ValueError):
                        _warn(f"lane-thresholds 무효 값 무시: {k}={v!r}")
                src = f"builtin-proposal+override:{path}"
            else:
                _warn(f"lane-thresholds 최상위 dict 아님 — 무시: {path}")
        except Exception as exc:
            _warn(f"lane-thresholds 판독 실패 {path}: {exc} — builtin proposal 사용")
    return table, src


def threshold_for(lane, table):
    """lane → 임계(min). 미지 lane → default. floor(30min) clamp — quota 낭비 방지 하한."""
    base = table.get(lane, _DEFAULT_THRESHOLD_MIN) if lane else _DEFAULT_THRESHOLD_MIN
    try:
        base = int(base)
    except (TypeError, ValueError):
        base = _DEFAULT_THRESHOLD_MIN
    return max(base, _FLOOR_MIN)


def _is_idle_state(state):
    if not state:
        return False
    return state == "idle-yield" or state == "waiting-external" or state.startswith("waiting-external:")


# ── 3-state 판정 ───────────────────────────────────────────────────────────────────────
def evaluate(latest, cursor, now_dt, thresholds):
    """브랜치별 3-state 판정 + cursor in-place 갱신. 반환 (results:dict, updated_cursor:dict).
    branches = (이번 poll 관측 ∪ cursor 추적) union — cursor 추적 중 부재 branch 도 surface(unknown)."""
    updated = dict(cursor) if isinstance(cursor, dict) else {}
    results = {}
    branches = set(latest.keys()) | set(updated.keys())

    for br in sorted(branches):
        prev = updated.get(br) if isinstance(updated.get(br), dict) else {}
        prev_last_seq = prev.get("last_seq")
        prev_observed_at = _parse_iso(prev.get("observed_at"))
        prev_unchanged = prev.get("unchanged_polls", 0)
        try:
            prev_unchanged = int(prev_unchanged)
        except (TypeError, ValueError):
            prev_unchanged = 0

        hb = latest.get(br)

        # (A) 부재 — cursor 추적 중이나 이번 poll heartbeat 없음 → unknown(fail-safe, never fresh).
        if hb is None:
            results[br] = _mk_result(
                verdict="unknown", reason="heartbeat-absent",
                seq=None, last_seq=prev_last_seq, seq_advanced=False,
                lane=prev.get("lane"), story=prev.get("story"), state=prev.get("state"),
                threshold_min=None, elapsed_min=_elapsed_min(prev_observed_at, now_dt),
                unchanged_polls=prev_unchanged, idle_relaxed=False,
            )
            # cursor 는 last_seq/observed_at 보존(진행 이력 소실 금지).
            updated[br] = prev
            continue

        # (B) malformed — branch 는 알지만 판독불능 → unknown(silently drop 금지).
        if hb.get("_malformed"):
            results[br] = _mk_result(
                verdict="unknown", reason="malformed-heartbeat",
                seq=None, last_seq=prev_last_seq, seq_advanced=False,
                lane=prev.get("lane"), story=prev.get("story"), state=prev.get("state"),
                threshold_min=None, elapsed_min=_elapsed_min(prev_observed_at, now_dt),
                unchanged_polls=prev_unchanged, idle_relaxed=False,
            )
            updated[br] = prev
            continue

        seq_new = hb["seq"]
        lane = hb.get("lane")
        story = hb.get("story")
        state = hb.get("state") or "active"
        thr = threshold_for(lane, thresholds)

        # (C) 최초 관측 or strict-advance → fresh (진행이 seq 로 증명, clock-무관).
        if prev_last_seq is None or seq_new > _as_int(prev_last_seq):
            updated[br] = {
                "last_seq": seq_new,
                "observed_at": _iso(now_dt),
                "unchanged_polls": 0,
                "lane": lane, "story": story, "state": state,
            }
            results[br] = _mk_result(
                verdict="fresh", reason=("first-sighting" if prev_last_seq is None else "seq-advance"),
                seq=seq_new, last_seq=prev_last_seq, seq_advanced=True,
                lane=lane, story=story, state=state,
                threshold_min=thr, elapsed_min=0.0, unchanged_polls=0, idle_relaxed=False,
            )
            continue

        # (D) seq regress (seq_new < last_seq) → anomaly → unknown(not fresh).
        if seq_new < _as_int(prev_last_seq):
            updated[br] = {
                "last_seq": prev_last_seq,  # 되돌림 금지(monotonic 보존)
                "observed_at": prev.get("observed_at"),
                "unchanged_polls": prev_unchanged,
                "lane": lane, "story": story, "state": state,
            }
            results[br] = _mk_result(
                verdict="unknown", reason="seq-regress",
                seq=seq_new, last_seq=prev_last_seq, seq_advanced=False,
                lane=lane, story=story, state=state,
                threshold_min=thr, elapsed_min=_elapsed_min(prev_observed_at, now_dt),
                unchanged_polls=prev_unchanged, idle_relaxed=False,
            )
            continue

        # (E) seq unchanged (seq_new == last_seq) → stalled 후보. 이번 poll 로 unchanged_polls++.
        unchanged_now = prev_unchanged + 1
        elapsed = _elapsed_min(prev_observed_at, now_dt)
        idle = _is_idle_state(state)
        updated[br] = {
            "last_seq": prev_last_seq,
            "observed_at": prev.get("observed_at"),  # last seq-advance 시각 유지
            "unchanged_polls": unchanged_now,
            "lane": lane, "story": story, "state": state,
        }

        # INV-L1 total-deadline ceiling — waiting-external/idle-yield self-attestation 도 무한 면제 불가.
        if elapsed is not None and elapsed > _TOTAL_DEADLINE_MIN:
            results[br] = _mk_result(
                verdict="unknown", reason="total-deadline-ceiling-breached",
                seq=seq_new, last_seq=prev_last_seq, seq_advanced=False,
                lane=lane, story=story, state=state,
                threshold_min=thr, elapsed_min=elapsed, unchanged_polls=unchanged_now,
                idle_relaxed=idle,
            )
            continue

        # elapsed 계산 불능(cursor.observed_at 손상) + unchanged → 판정 불가 → unknown(fail-safe).
        if elapsed is None:
            results[br] = _mk_result(
                verdict="unknown", reason="observed-at-unparseable",
                seq=seq_new, last_seq=prev_last_seq, seq_advanced=False,
                lane=lane, story=story, state=state,
                threshold_min=thr, elapsed_min=None, unchanged_polls=unchanged_now,
                idle_relaxed=False,
            )
            continue

        # idle-relaxation (§결정 6) — waiting-external/idle-yield 는 elapsed 단독으로 stalled 미판정.
        if idle:
            results[br] = _mk_result(
                verdict="fresh", reason="idle-relaxed-within-ceiling",
                seq=seq_new, last_seq=prev_last_seq, seq_advanced=False,
                lane=lane, story=story, state=state,
                threshold_min=thr, elapsed_min=elapsed, unchanged_polls=unchanged_now,
                idle_relaxed=True,
            )
            continue

        # stalled = unchanged_polls≥2 AND elapsed>lane 임계 (둘 다 필요).
        if unchanged_now >= _STALL_MIN_UNCHANGED_POLLS and elapsed > thr:
            results[br] = _mk_result(
                verdict="stalled", reason="seq-frozen-past-threshold",
                seq=seq_new, last_seq=prev_last_seq, seq_advanced=False,
                lane=lane, story=story, state=state,
                threshold_min=thr, elapsed_min=elapsed, unchanged_polls=unchanged_now,
                idle_relaxed=False,
            )
            continue

        # unchanged 이나 아직 patience 창 이내(<2 polls 또는 elapsed≤임계) → 비경보(seq 미진행은 명시).
        results[br] = _mk_result(
            verdict="fresh", reason="within-patience-window",
            seq=seq_new, last_seq=prev_last_seq, seq_advanced=False,
            lane=lane, story=story, state=state,
            threshold_min=thr, elapsed_min=elapsed, unchanged_polls=unchanged_now,
            idle_relaxed=False,
        )

    return results, updated


def _as_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return -1


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _elapsed_min(observed_at_dt, now_dt):
    """watchdog OWN clock elapsed(min) = now - cursor.observed_at. observed_at 없음/손상 → None.
    ★ emitter_ts(코멘트 ts)는 절대 사용하지 않는다(§결정 5 F-5 cross-host skew trap)."""
    if observed_at_dt is None:
        return None
    return (now_dt - observed_at_dt).total_seconds() / 60.0


def _mk_result(**kw):
    if kw.get("elapsed_min") is not None:
        kw["elapsed_min"] = round(kw["elapsed_min"], 3)
    return kw


# ── marker (meta-observer Tier 2, §결정 7) ──────────────────────────────────────────────
def write_marker(path, now_iso, results):
    """watchdog own last-run marker — 부재(>2× cron)가 곧 경보(§결정 7). \\n 개행 CRLF-safe."""
    try:
        summary = _summarize(results)
        payload = {
            "run_ts": now_iso,
            "branches_evaluated": len(results),
            "summary": summary,
            "note": "watchdog last-run liveness marker (Tier 2 meta-observer). 부재>2×cron = 경보.",
        }
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(f"{p.name}.tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        import os
        os.replace(tmp, p)
    except Exception as exc:
        _warn(f"marker write 실패 {path}: {exc}")


def write_cursor(path, cursor):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(f"{p.name}.tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cursor, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        import os
        os.replace(tmp, p)
    except Exception as exc:
        _warn(f"cursor write 실패 {path}: {exc}")


def _summarize(results):
    summary = {"fresh": 0, "stalled": 0, "unknown": 0}
    for r in results.values():
        v = r.get("verdict")
        if v in summary:
            summary[v] += 1
    return summary


def load_cursor(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception as exc:
        _warn(f"cursor 판독 실패 {path}: {exc} — 빈 cursor 로 진행(신규 생성)")
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="CFP-2772 external branch-liveness watchdog — 3-state(fresh/stalled/unknown), exit 0 always",
    )
    parser.add_argument("--comments", required=True,
                        help="heartbeat relay 코멘트 본문 JSON array(또는 JSONL); '-'=stdin")
    parser.add_argument("--cursor", required=True,
                        help="durable ack cursor JSON {slug:{last_seq,observed_at,unchanged_polls}} — 부재 시 생성")
    parser.add_argument("--now", default=None,
                        help="watchdog OWN-clock 수신시각 ISO8601 (기본 UTC now). ★emitter_ts 와 절대 비교 안 함")
    parser.add_argument("--lane-thresholds", default=None,
                        help="optional JSON {lane: minutes} override (built-in PROPOSAL merge)")
    parser.add_argument("--marker-out", default=None,
                        help="meta-observer own last-run marker 파일(Tier 2)")
    parser.add_argument("--json", action="store_true", help="verdict JSON 을 stdout 으로")
    args = parser.parse_args()

    now_iso = args.now if args.now else _now_default()
    now_dt = _parse_iso(now_iso)
    if now_dt is None:
        _warn(f"--now 파싱 실패 '{args.now}' — UTC now 로 대체")
        now_iso = _now_default()
        now_dt = _parse_iso(now_iso)

    bodies = load_comment_bodies(args.comments)
    latest = collect_latest_per_branch(bodies)
    thresholds, thr_src = load_thresholds(args.lane_thresholds)
    cursor = load_cursor(args.cursor)

    results, updated_cursor = evaluate(latest, cursor, now_dt, thresholds)

    # durable ack cursor in-place 갱신 (restart 생존 SoT).
    write_cursor(args.cursor, updated_cursor)
    if args.marker_out:
        write_marker(args.marker_out, now_iso, results)

    summary = _summarize(results)
    verdict_top = "ok"
    if summary["unknown"] > 0:
        verdict_top = "inconclusive"  # unknown 존재 → fail-open 금지: PASS 승격 금지(AC-9).
    elif summary["stalled"] > 0:
        verdict_top = "stalled-detected"

    out = {
        "now": now_iso,
        "clock_basis": "watchdog-own-clock (cursor.observed_at) — emitter_ts 미사용(F-5)",
        "thresholds_source": thr_src,
        "verdict": verdict_top,
        "summary": summary,
        "branches": results,
        "honest_ceiling": (
            "lane 임계 = PROPOSAL(empirical 미실증, lock-in 0). born-safe bound(byte-cap 4096/line-cap/"
            "anchored non-backtracking regex/non-blocking exit0)만 보장 — ReDoS-safe/DoS-proof 단정 없음."
        ),
    }

    if args.json:
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(
            f"[{SCRIPT_NAME}] now={now_iso} verdict={verdict_top} "
            f"fresh={summary['fresh']} stalled={summary['stalled']} unknown={summary['unknown']}\n"
        )
        for br in sorted(results):
            r = results[br]
            sys.stdout.write(
                f"  - {br}: {r['verdict']} ({r['reason']}) seq={r['seq']} "
                f"elapsed_min={r['elapsed_min']} thr={r['threshold_min']}\n"
            )

    return 0  # record-only / detection surface — exit 0 ALWAYS (stalled/unknown 여도).


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover — 최종 non-blocking 안전망(exit 0 always)
        sys.stderr.write(f"[{SCRIPT_NAME}] WARN: unexpected — {exc}\n")
        sys.stdout.write(json.dumps({"verdict": "inconclusive", "error": str(exc)}) + "\n")
        sys.exit(0)
