#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_workspace_residue_discovery.py — 세션 잔재 발견(discovery) 스캐너 orchestrator + CLI
#
# Carrier: CFP-2822 Phase 2 (구현) — 세션 잔재 수명 규약 (ADR-169 §결정 2, ③ discovery 스캐너)
# 설계 SSOT: change-plan cfp-2822 §3.2③ (5-함수 파이프라인) / §3.4 (파일 상태 스키마) /
#           §3.5 (flat sibling) / §3.6 (bypass) / §4.1 (CLI 계약) / §5.3 (lock/멱등 3중) /
#           §7.1 (TB-3) / Story AC-8/8a/11/12/14/15 / INV-1~9.
#
# ── 5-함수 파이프라인 (§3.2③) ────────────────────────────────────────────────────────
#   discover() -> list[Candidate]           # 순수 읽기 (등록 worktree = subprocess 위임 인식-후-제외)
#   classify() -> list[ClassifiedCandidate] # 3축 분류 신호 (등록/git존재/상태검사) — 삭제 여부 미결정
#   judge()    -> list[Verdict]             # REMOVE|KEEP + reason + age (순수 판정, 삭제 syscall 0)
#   execute()  -> list[ExecResult]          # REMOVE verdict 만 소비 삭제 (mode 로 제어 — INV-9)
#   report()   -> None                      # emit_aging_realert(AC-8) + emit_metrics_summary(AC-8a)
#
#   ★ judge/execute 분리 (Refactor D-1): discover/classify/judge/report = 순수 읽기(잠금 불요),
#     execute 만 삭제. INV-9 2단계 = scan_root mode 값 하나(observe-only)로 execute 억제.
#
# ── scan_roots 4-mode (§3.2③ root-walker 파라미터화) ────────────────────────────────
#   ~/.claude/worktrees/  mode=cross-check-only  → 등록부 subprocess 위임 대조 후 제외(재판정 X)
#   <workspace-root>      mode=discover+classify  → _wt-* 류 (execute 대상 = allowed_roots 봉쇄)
#   ~ (home 직하)          mode=discover+classify  → 독립 clone (git-dir 판정축, execute 미허용=가시화)
#   %TEMP%/claude/        mode=observe-only        → INV-9 삭제 실행 0 (2단계 = 이 mode 승격)
#
# 출력 계약(§4.1): 마지막 줄 "[residue-scan] DONE: scanned=N flagged=M", exit always 0 (advisory).
#   기존 [stale-check]/[completion-clean] 과 disjoint 네임스페이스 → INV-5 물리 무접촉.
#
# Bypass: BYPASS_WORKSPACE_RESIDUE_SCAN=1 → audit echo + exit 0 (§3.6, 기존 31개 disjoint).

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Optional

_SELF_DIR = os.path.dirname(os.path.abspath(__file__))
if _SELF_DIR not in sys.path:
    sys.path.insert(0, _SELF_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# base substrate + 사이블링 (import DAG: 1 → {2,3,4}, 2 는 사이블링 미import = 사이클 없음).
import check_orphan_worktree_classify as base  # noqa: E402
import check_stash_aging_census as stash_axis  # noqa: E402
import check_harness_temp_residue as temp_axis  # noqa: E402

SCRIPT_NAME = "residue-scan"
BYPASS_ENV = "BYPASS_WORKSPACE_RESIDUE_SCAN"

# ── 상태 스키마 (§3.4 — codeforge-scratch 밖 self-exemption) ──────────────────────────
GC_STATE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "worktree-gc-state")
AGING_STATE_FILE = os.path.join(GC_STATE_DIR, "residue-aging.jsonl")
STATE_SCHEMA_VERSION = 1

# 재알림 지수 backoff (§3.4 / §7.4.1): base=7d → max=90d (7→14→28→56→90…).
BACKOFF_BASE_DAYS = 7
BACKOFF_MAX_DAYS = 90

# aging 사이드카 soft cap (self-referential 축적 방지 — §3.4 로그 rotate/cap).
_AGING_LINE_CAP = 5000

# 용량 임계 경고 (AC-15). Temp/scratch 총량 임계 (proposal — 수치 lock-in 금지, tunable).
CAPACITY_ALERT_BYTES = int(os.environ.get("GC_CAPACITY_ALERT_BYTES", str(10 * 1024 ** 3)))  # 10GB


# ═══════════════════════════════ dataclasses ═══════════════════════════════════════
@dataclass
class Candidate:
    path: str
    source: str                 # worktrees-base | workspace-root | home-direct | temp
    mode: str                   # cross-check-only | discover+classify | observe-only


@dataclass
class ClassifiedCandidate:
    path: str
    source: str
    mode: str
    registered: bool            # 3축 ① 등록여부 (등록 worktree = discover 에서 이미 제외)
    git_exists: bool            # 3축 ② git 존재
    needs_state_check: bool     # 3축 ③ 상태검사 필요여부
    temp_info: Optional[dict] = None   # temp 소스만 (File 4 git-aware 관측 결과)


@dataclass
class Verdict:
    path: str
    source: str
    mode: str
    decision: str               # REMOVE | KEEP
    reason: Optional[str]       # dirty|unpushed-N|locked|pin|network-inconclusive|
    #                             temp-git-worktree|unregistered-location|None
    age: Optional[int]          # seconds (INV-3 — 보존 = 사유 + 나이)


@dataclass
class ExecResult:
    path: str
    action: str                 # removed | skipped | blocked | dry-run
    ok: bool
    note: str


@dataclass
class ScanState:
    scanned: int = 0
    flagged: int = 0
    verdicts: list = field(default_factory=list)
    exec_results: list = field(default_factory=list)


# ═══════════════════════════════ scan_roots ═══════════════════════════════════════
def default_scan_roots(repo_root=None):
    """production scan_roots (§3.2③). 비-Windows Temp = tempfile.gettempdir() 자동 해소
    (하드코딩 금지 — Windows %TEMP%/claude, POSIX $TMPDIR|/tmp /claude 동일 코드 경로)."""
    home = os.path.expanduser("~")
    main_wt = base.registered_main_worktree(repo_root) or (repo_root or os.getcwd())
    workspace_root = os.path.dirname(os.path.abspath(main_wt))
    worktrees_base = os.path.join(home, ".claude", "worktrees")
    temp_root = os.path.join(tempfile.gettempdir(), "claude")
    return [
        {"path": worktrees_base, "mode": "cross-check-only", "source": "worktrees-base"},
        {"path": workspace_root, "mode": "discover+classify", "source": "workspace-root"},
        {"path": home, "mode": "discover+classify", "source": "home-direct"},
        {"path": temp_root, "mode": "observe-only", "source": "temp"},
    ]


def _delete_allowed_roots(scan_roots):
    """execute 삭제 허용 root (TB-3 allowlist fail-closed). INV-1 보수:
    workspace-root 하위만 filesystem-direct 삭제 허용 — home(~) 직하는 광역 위험이라
    가시화만(REMOVE verdict 은 outside-allowlist 로 차단됨). temp/worktrees-base 미포함."""
    return [os.path.expanduser(s["path"]) for s in scan_roots
            if s.get("source") == "workspace-root"]


# ═══════════════════════════════ 5-함수 파이프라인 ═══════════════════════════════════
def _story_match(path, story_key):
    """--story-key 필터 (완료-게이트 재사용). key 부재 → 전량 통과."""
    if not story_key:
        return True
    sk = story_key.strip().lower()
    return sk in os.path.basename(path).lower() or sk in path.lower()


def discover(scan_roots, repo_root=None, story_key=None):
    """1) 후보 열거 (순수 읽기). 등록 worktree = subprocess 위임 집합 대조로 인식-후-제외."""
    registered = base.list_registered_worktrees(repo_root)   # anti-corruption (파싱 재구현 X)
    candidates = []
    seen = set()
    for spec in scan_roots:
        root = os.path.expanduser(spec["path"])
        mode, source = spec["mode"], spec.get("source", "")
        if not os.path.isdir(root):
            continue
        try:
            names = sorted(os.listdir(root))
        except OSError:
            continue
        for name in names:
            full = os.path.join(root, name)
            if not os.path.isdir(full):
                continue
            nkey = base._norm(full)
            if nkey in seen:
                continue
            # 등록 worktree = 인식-후-제외 (재판정 X — backstop 전담)
            if nkey in registered:
                continue
            if source in ("workspace-root", "home-direct"):
                if not base.matches_residue_pattern(name, source):
                    continue
            if not _story_match(full, story_key):
                continue
            seen.add(nkey)
            candidates.append(Candidate(path=full, source=source, mode=mode))
    return candidates


def classify(candidates):
    """2) 3축 분류 (신호로만 — 삭제 여부 미결정, AC-12)."""
    out = []
    for c in candidates:
        if c.source == "temp":
            info = temp_axis.classify_temp_entry(c.path)
            out.append(ClassifiedCandidate(
                path=c.path, source=c.source, mode=c.mode,
                registered=False, git_exists=info["is_git"],
                needs_state_check=info["is_git"], temp_info=info))
        else:
            cls = base.classify_orphan(c.path, c.source)
            out.append(ClassifiedCandidate(
                path=c.path, source=c.source, mode=c.mode,
                registered=cls["registered"], git_exists=cls["git_exists"],
                needs_state_check=cls["needs_state_check"]))
    return out


def judge(classified):
    """3) REMOVE|KEEP + reason + age 판정 (순수 — 삭제 syscall 0)."""
    verdicts = []
    for cc in classified:
        if cc.source == "temp":
            # observe-only: 1단계 삭제 0 → 항상 KEEP. git-aware preserve 사유 부착(INV-3).
            info = cc.temp_info or {}
            reason = info.get("reason") if info.get("preserve") else None
            verdicts.append(Verdict(path=cc.path, source=cc.source, mode=cc.mode,
                                    decision="KEEP", reason=reason, age=info.get("age")))
            continue
        if cc.mode == "cross-check-only":
            # worktrees-base 미등록 잔여 = 가시화만(재판정 X) → KEEP unregistered-location.
            verdicts.append(Verdict(path=cc.path, source=cc.source, mode=cc.mode,
                                    decision="KEEP", reason="unregistered-location",
                                    age=base.age_seconds(cc.path)))
            continue
        decision, reason, age = base.judge_orphan(cc.path, cc.source, cc.git_exists)
        verdicts.append(Verdict(path=cc.path, source=cc.source, mode=cc.mode,
                                decision=decision, reason=reason, age=age))
    return verdicts


def execute(verdicts, allowed_roots, dry_run=None):
    """4) REMOVE verdict 만 소비 삭제. mode 로 제어 — observe-only/cross-check-only = skip(INV-9).

    §5.3 double-delete 0 = 3중: (lock=Dev-Guards ⑤) + 존재 재확인 + idempotent
      → safe_remove 안에 존재 재확인(IDEM-3) + graceful. TB-3 6-guard 전량 safe_remove 경유."""
    results = []
    for v in verdicts:
        if v.decision != "REMOVE":
            continue
        if v.mode != "discover+classify":
            # observe-only(temp) / cross-check-only(worktrees-base) = 삭제 미도달 (INV-9 코드강제)
            results.append(ExecResult(v.path, "skipped", True, "mode=%s (no-delete)" % v.mode))
            continue
        ok, note = base.safe_remove(v.path, allowed_roots, dry_run=dry_run)
        if ok:
            action = "removed"
        elif note.startswith("dry-run"):
            action = "dry-run"
        elif note.startswith("skip"):
            action = "skipped"
        else:
            action = "blocked"       # guard-reject/remove-failed → INV-1 보존 방향
        results.append(ExecResult(v.path, action, ok, note))
    return results


# ── report() 하위 (tier 상이 — Refactor P-1) ──────────────────────────────────────
def _ensure_state_dir():
    try:
        os.makedirs(GC_STATE_DIR, exist_ok=True)
        return True
    except OSError:
        return False


def _load_aging_state():
    """JSONL 사이드카 → key 별 최신 레코드 (§3.4). 파일 부재 = v0(빈 상태). corruption = skip."""
    latest = {}
    if not os.path.isfile(AGING_STATE_FILE):
        return latest
    try:
        with open(AGING_STATE_FILE, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue    # corruption tolerant — 개별 라인 skip
                k = rec.get("key")
                if k:
                    latest[k] = rec
    except OSError:
        pass
    return latest


def _append_aging_records(records):
    """JSONL append (in-place truncate 금지 — 크래시 alert storm 방어, §3.4 IDEM-4).
    soft cap 초과 시 최신분만 원자 재작성(temp+rename)으로 compaction."""
    if not records:
        return
    if not _ensure_state_dir():
        return
    try:
        with open(AGING_STATE_FILE, "a", encoding="utf-8", errors="replace") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        return
    # soft-cap compaction (per-key 최신만 남김) — 순수 파생데이터라 최악=재알림 재발화만.
    try:
        with open(AGING_STATE_FILE, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        if len(lines) > _AGING_LINE_CAP:
            latest = _load_aging_state()
            tmp = AGING_STATE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8", errors="replace") as fh:
                for rec in latest.values():
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            os.replace(tmp, AGING_STATE_FILE)
    except OSError:
        pass


def _backoff_due(rec, now):
    """지수 backoff 재알림 판정: (now-last_alert) >= min(base*2^count, max)."""
    count = int(rec.get("alert_count", 0))
    last = int(rec.get("last_alert_epoch", 0))
    interval_days = min(BACKOFF_BASE_DAYS * (2 ** max(0, count - 1)), BACKOFF_MAX_DAYS)
    return (now - last) >= interval_days * 86400


def emit_aging_realert(verdicts, now=None):
    """AC-8 정규 재알림 — item+reason dedup + 지수 backoff. 원자 JSONL append 상태.
    보존(KEEP + reason) 항목만 대상. 반환: 이번 발화 건수."""
    n = base.now_epoch() if now is None else now
    prior = _load_aging_state()
    new_records = []
    fired = 0
    for v in verdicts:
        if v.decision != "KEEP" or not v.reason:
            continue    # INV-3: 사유있는 보존만 aging 대상 (temp non-git reason=None 제외)
        reason_class = v.reason.split("-")[0] if v.reason.startswith("unpushed") else v.reason
        key = base.key_hash(v.path, reason_class)
        rec = prior.get(key)
        disp = base.sanitize(v.path)
        age_d = (v.age or 0) // 86400
        if rec is None:
            fired += 1
            new_records.append({
                "schema_version": STATE_SCHEMA_VERSION, "key": key,
                "display_path": disp, "reason": v.reason,
                "first_seen_epoch": n, "last_alert_epoch": n,
                "alert_count": 1, "age_days": age_d,
            })
            print("[%s] AGING-ALERT (신규 보존): reason=%s age=%dd %s"
                  % (SCRIPT_NAME, base.sanitize(v.reason), age_d, disp), file=sys.stderr)
        elif _backoff_due(rec, n):
            fired += 1
            new_records.append({
                "schema_version": STATE_SCHEMA_VERSION, "key": key,
                "display_path": disp, "reason": v.reason,
                "first_seen_epoch": int(rec.get("first_seen_epoch", n)),
                "last_alert_epoch": n,
                "alert_count": int(rec.get("alert_count", 1)) + 1, "age_days": age_d,
            })
            print("[%s] AGING-REALERT (backoff): reason=%s age=%dd count=%d %s"
                  % (SCRIPT_NAME, base.sanitize(v.reason), age_d,
                     int(rec.get("alert_count", 1)) + 1, disp), file=sys.stderr)
        # else: dedup 창 내 → 무발화 (alert fatigue 억제)
    _append_aging_records(new_records)
    return fired


def emit_metrics_summary(verdicts, exec_results, temp_obs, stash_cen, prefix=SCRIPT_NAME):
    """AC-8a 순수 집계 advisory — 클래스/사유별 건수 + 최고령 + 용량 임계. 재알림과 tier 분리."""
    by_reason = {}
    oldest = 0
    for v in verdicts:
        if v.decision == "KEEP" and v.reason:
            by_reason[v.reason] = by_reason.get(v.reason, 0) + 1
        oldest = max(oldest, v.age or 0)
    removed = sum(1 for r in exec_results if r.action == "removed")
    blocked = sum(1 for r in exec_results if r.action == "blocked")
    reason_str = " ".join("%s=%d" % (base.sanitize(k), n) for k, n in sorted(by_reason.items())) or "none"
    print("[%s] METRICS: preserved-by-reason[%s] removed=%d blocked=%d oldest=%dd"
          % (prefix, reason_str, removed, blocked, oldest // 86400), file=sys.stderr)
    # AC-14 stash 가시화 1줄
    if stash_cen:
        print("[%s] METRICS: stash total=%d repos=%d oldest=%dd (삭제 0 — 가시화)"
              % (prefix, stash_cen.get("total_stashes", 0), stash_cen.get("repos_with_stash", 0),
                 (stash_cen.get("oldest_age", 0) or 0) // 86400), file=sys.stderr)
    # AC-15 용량 임계 경고 (Temp 총량)
    if temp_obs and temp_obs.get("total_size", 0) > CAPACITY_ALERT_BYTES:
        gb = temp_obs["total_size"] / (1024 ** 3)
        print("[%s] METRICS: CAPACITY-ALERT Temp=%.1fGB > 임계 (회수 강행 0 — INV-1/2 가시화)"
              % (prefix, gb), file=sys.stderr)


def _temp_metrics_from_classified(classified):
    """classified 의 temp 엔트리에서 용량/나이 집계 도출 (단일 walk — observe_temp 재-walk 회피,
    Perf S1). temp scan_root 부재 시 None."""
    temp_entries = [cc.temp_info for cc in classified
                    if cc.source == "temp" and cc.temp_info is not None]
    if not temp_entries:
        return None
    total_size = sum(e.get("size", 0) for e in temp_entries)
    oldest = max((e.get("age") or 0) for e in temp_entries) if temp_entries else 0
    return {"total_size": total_size, "entry_count": len(temp_entries), "oldest_age": oldest}


def report(verdicts, exec_results, temp_obs=None, stash_cen=None, now=None):
    """5) 보고 = 재알림(AC-8) + 집계(AC-8a) 별도 하위함수 (tier 상이)."""
    try:
        emit_aging_realert(verdicts, now=now)
    except Exception as e:   # 축 격리 — 재알림 실패가 집계 abort 안 함
        print("[%s] WARN: aging-realert 실패 (non-blocking): %s"
              % (SCRIPT_NAME, base.strip_control(str(e))[:120]), file=sys.stderr)
    try:
        emit_metrics_summary(verdicts, exec_results, temp_obs, stash_cen)
    except Exception as e:
        print("[%s] WARN: metrics 실패 (non-blocking): %s"
              % (SCRIPT_NAME, base.strip_control(str(e))[:120]), file=sys.stderr)


# ═══════════════════════════════ orchestration ═══════════════════════════════════
def run_scan(scan_roots=None, repo_root=None, story_key=None, dry_run=None):
    """전체 파이프라인 조립 (축 격리 — 한 축 실패가 다른 축 abort 안 함, §3.5)."""
    if repo_root is None:
        cp = base._git(["rev-parse", "--show-toplevel"])
        repo_root = (cp.stdout.strip() if cp and cp.returncode == 0 and cp.stdout else os.getcwd())
    if scan_roots is None:
        scan_roots = default_scan_roots(repo_root)
    allowed = _delete_allowed_roots(scan_roots)

    st = ScanState()
    # discover → classify → judge (순수 읽기)
    classified = []
    try:
        candidates = discover(scan_roots, repo_root=repo_root, story_key=story_key)
        classified = classify(candidates)
        verdicts = judge(classified)
    except Exception as e:
        print("[%s] WARN: discover/classify/judge 실패 (non-blocking): %s"
              % (SCRIPT_NAME, base.strip_control(str(e))[:160]), file=sys.stderr)
        verdicts = []
    st.verdicts = verdicts
    st.scanned = len(verdicts)
    st.flagged = sum(1 for v in verdicts if v.reason is not None or v.decision == "REMOVE")

    # execute (삭제 — mode observe-only/cross-check-only skip)
    try:
        st.exec_results = execute(verdicts, allowed, dry_run=dry_run)
    except Exception as e:
        print("[%s] WARN: execute 실패 (non-blocking): %s"
              % (SCRIPT_NAME, base.strip_control(str(e))[:160]), file=sys.stderr)

    # temp 관측 metrics (INV-9 삭제 0) — classify 단일 walk 재사용 (observe_temp 재-walk 회피)
    temp_obs = None
    try:
        temp_obs = _temp_metrics_from_classified(classified)
    except Exception:
        pass

    # stash census (AC-14 — 삭제 0) — git-bearing 후보 + workspace repo
    stash_cen = None
    try:
        repo_paths = [v.path for v in verdicts if base.has_git_dir(v.path)]
        repo_paths.append(repo_root)
        stash_cen = stash_axis.stash_census(repo_paths)
    except Exception:
        pass

    # report (재알림 + 집계)
    report(verdicts, st.exec_results, temp_obs=temp_obs, stash_cen=stash_cen)
    return st


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="세션 잔재 발견 스캐너 (advisory, always exit 0)")
    ap.add_argument("--story-key", default=None,
                    help="cfp-NNN — 완료-게이트 Story-scoped 모드 (해당 Story 잔재만)")
    ap.add_argument("--dry-run", action="store_true",
                    help="파괴적 동작 preview (GC_DRY_RUN=1 과 동형)")
    args = ap.parse_args(argv)

    # Bypass (§3.6 — audit 한 줄 + exit 0)
    if os.environ.get(BYPASS_ENV) == "1":
        print("[%s] %s=1 — 스캔 skip (audit)" % (SCRIPT_NAME, BYPASS_ENV), file=sys.stderr)
        print("[%s] DONE: scanned=0 flagged=0" % SCRIPT_NAME)
        return 0

    dry = True if args.dry_run else None   # None → base.GC_DRY_RUN env 판정 위임
    try:
        st = run_scan(story_key=args.story_key, dry_run=dry)
    except Exception as e:
        # 최상위 fail-safe — 어떤 예외에도 DONE 마커 + exit 0 (INV-5)
        print("[%s] WARN: 스캔 최상위 예외 (non-blocking): %s"
              % (SCRIPT_NAME, base.strip_control(str(e))[:160]), file=sys.stderr)
        print("[%s] DONE: scanned=0 flagged=0" % SCRIPT_NAME)
        return 0

    print("[%s] DONE: scanned=%d flagged=%d" % (SCRIPT_NAME, st.scanned, st.flagged))
    return 0


if __name__ == "__main__":
    sys.exit(main())
