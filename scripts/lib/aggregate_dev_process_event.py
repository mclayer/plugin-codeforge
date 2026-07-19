#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# aggregate_dev_process_event.py — dev-process-event-v1 지표 aggregation (record-only, B lane)
#
# Carrier: CFP-2688 Phase 2 (구현) — Epic #2686 Story B / ADR-156 (dev-process metric aggregation)
# SSOT: docs/change-plans/2026-07-15-cfp-2688-dev-process-metrics.md §3/§4/§7/§8.6/§11.6
#       + docs/inter-plugin-contracts/dev-process-event-v1.md §9 (A substrate, FROZEN)
#
# 책임:
#   - A(#2687) 가 freeze 한 dev-process-event-v1 substrate 를 query port 경유 **read-only 소비**
#     → 6 지표(cycletime·fixloop·defect-attribution·selfref-recurrence·trend+§D-9·token-cost)
#     산식·집계·KPI dual-file(history.jsonl append-only + snapshot.json) 저장.
#   - B = 측정·집계 ONLY. PASS/FAIL·verdict·임계·차단 미산출(그건 C #2689 — INV-B3).
#
# 불변식 (binding — Change Plan §3.6):
#   - INV-B1 port-only read: dev-process read = query()/query_with_stats() 단독. 원장 직접 파싱 0.
#   - INV-B2 5th boundary re-record ban: token/cost accounting 을 dev-process ledger 로 re-record 금지.
#   - INV-B3 B ⊥ C disjoint: PASS/FAIL·verdict 미산출.
#   - INV-B4 metric⑥ spawn JOIN = event_id 상관만 (replay reader 경유, raw JSONL parse 금지).
#   - INV-B5 honest-degrade: measured-0 ≠ dormant. fabricated 0 금지. stats 관측치 동반.
#   - INV-B6 dual-file KPI: history.jsonl(content-hash append) + snapshot.json(atomic overwrite).
#
# ★clone-with-care (KST 함정 — Change Plan §3.3):
#   archetype aggregate_stop_event._parse_iso_aware 는 naive ts 를 KST(+09:00)로 승격한다.
#   dev-process index 는 timestamp_utc(UTC Z) 저장 → clone 시 9시간 skew(silent). 본 모듈은
#   자체 _parse_utc_z(naive-fallback = UTC, KST 아님)를 정의한다. port private _parse_utc_z 도 import 금지.
#
# ★honest-degrade (ADR-119, binding):
#   "정확한 사이클타임 / exact FIX count / 정밀 should-have-caught 귀속 / 비-null token 비용"
#   over-claim 금지. exact-count/guaranteed-unique 주장 금지(port 관측치 상속). "leak-proof"/
#   "DoS-proof" 주장 금지 — cycletime forward-scan 은 per-story bounded degradation(worst-case
#   quadratic in per-story event count), 임의 입력 무해 아님(DoS-proof 아님). seen-set dedup = port 소유.
#
# 사용:
#   python3 aggregate_dev_process_event.py [--ledger PATH] [--kpi-dir DIR]
#                                          [--since ISO] [--until ISO] [--no-write] [--json]
#   python3 aggregate_dev_process_event.py --self-test
#
# stdlib only (json / hashlib / datetime / argparse / pathlib / os / sys / subprocess / tempfile).
# 정규식 미사용(regex 파싱 경로 부재 — ReDoS backtracking 표면 자체가 없음, 별도 반증 대상 아님).

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Windows cp949 인코딩 회피 (ADR-061 portability — scripts/lib 관례 재사용)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── sibling import (INV-B1 port-only / INV-B4 spawn pricing REUSE — ADR-140 no-duplication) ──
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from query_dev_process_event import query_with_stats  # noqa: E402  (A mining port — B 유일 read 진입점)
from spawn_event_pricing import cost_usd  # noqa: E402  (spawn-event-v1 pricing helper — REUSE)


# ─────────────────────── 상수 (enum · 매핑 · 가중 · strip-set) ───────────────────────

_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))  # scripts/lib → scripts → repo root

# 6 지표 KPI 파일 basename stem (docs/kpi/dev-process-<metric>-{history.jsonl,snapshot.json})
_METRIC_NAMES = (
    "cycletime", "fixloop", "defect-attribution",
    "selfref-recurrence", "trend", "token-cost",
)

# ★idempotency / history-dedup CODE CONSTANT strip-set (Change Plan §8.6/§11.6 — X⊆X tautology 회피).
#   산출 결과에서 역산하지 않고 사전 고정. generated_at_kst = 유일 wall-clock 각인 field.
_IDENTITY_STRIP_KEYS = ("generated_at_kst",)

# capture_subject 매핑 (AC-12 advisory heuristic — review-responsibility lane↔mechanism 근사).
#   사람 리뷰 lane → 'lane' / 기계 CI 게이트 lane → 'gate' / 그 외·미등재 → 'undetermined'(honest-degrade).
#   substrate 에 capture-mechanism 필드 부재 → detecting_lane 로 근사(ground-truth 아님).
_CAPTURE_SUBJECT_LANE = frozenset({
    "요구사항-리뷰", "설계-리뷰", "구현-리뷰", "보안-테스트", "배포-리뷰",
})
_CAPTURE_SUBJECT_GATE = frozenset({
    "구현-테스트",  # 기계 test-runner CI 게이트 lane (TestAgent) — machine-executed
})

# self-ref-prone family (AC-15 advisory heuristic — substrate 에 Story-purpose↔family alignment 부재).
#   governance/meta 성 결점군만 self-ref candidate 후보로 분리 표기(general recurrence 와 disjoint 라벨).
_SELF_REF_PRONE_FAMILIES = frozenset({"process-discipline", "doc-integrity"})

# token-cost 4 class 가중 (AC-21 — read-time 가중, flat-sum 금지. Anthropic prompt-caching 요율).
#   ★cache_write_1h(2×) = spawn substrate 단일 cache_creation + cost_usd 단일 1.25× 배수로 유도 불가
#     → honest-null (cache_ttl_split_missing). 아래는 documented 가중(적용 규칙), 원천 count 는 별개.
_TOKEN_CLASS_WEIGHTS = {
    "uncached_input": 1.0,
    "cache_read": 0.1,
    "cache_write_5m": 1.25,
    "cache_write_1h": 2.0,   # documented 가중 — 원천 count 는 substrate 부재로 honest-null
}

# time_to_detection DERIVED sentinel (append_dev_process_event._TTD_UNATTRIBUTED 정합)
_TTD_UNATTRIBUTED = "unattributed"

# ★over-claim 금지 positive-claim 토큰 (AC-4 negative-control — 출력에 절대 등장 금지).
#   honesty note 의 부정형("exact-count 아님")과 구분되는 긍정 단정만 금지.
_FORBIDDEN_POSITIVE_CLAIMS = (
    "guaranteed-unique count", "guaranteed_unique", "정확한 사이클타임",
    "exact FIX count", "정밀 귀속", "DoS-proof", "leak-proof",
)

_SPAWN_STATS_HONESTY = (
    "spawn-event read-time dedup(event_id) best-effort — exact-count/guaranteed-unique 아님. "
    "token 값 3-gap 미해소 → honest-null(INV-B4 event_id JOIN correlation-only)."
)

_HONESTY_TIER = (
    "[measurement] tier STRICT — dev-process 지표는 관측치일 뿐 인과/verdict 아님. "
    "measured-0 ≠ dormant(미측정). exact-count/guaranteed-unique 주장 금지(port 관측치 상속)."
)
_HONESTY_DEGRADE = (
    "substrate gap → honest-degrade: transition_point/anchor_id/root_cause_class/origin-lane 부재. "
    "cycletime=coarse residency, should-have-caught=advisory heuristic, pattern_count=uncomputable(default), "
    "token-cost=honest-null(3-gap). null+uncomputable_reason 로 표기, fabricated 0 금지."
)


# ─────────────────────── 시각 헬퍼 ────────────────────────────────────────────────────

def _kst_now_iso():
    """KST ISO 8601 wall-clock 각인 (ADR-079 display layer KST). snapshot identity/history dedup 제외."""
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    return utc_now.astimezone(kst).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def _parse_utc_z(value):
    """dev-process timestamp_utc = 'YYYY-MM-DDTHH:MM:SS(.mmm)Z' (UTC Z) → aware dt.

    'Z' → '+00:00' 치환 후 fromisoformat. ★naive-fallback = UTC (KST 아님 — archetype
    _parse_iso_aware 의 KST 승격 clone 시 9h skew silent, 그 함정 회피). 실패 시 None.
    """
    if not isinstance(value, str) or not value:
        return None
    s = value.strip()
    try:
        iso = s[:-1] + "+00:00" if s.endswith("Z") else s
        dt = datetime.datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)  # ★UTC (NOT KST)
    return dt


# ─────────────────────── 공통 유틸 (pure) ─────────────────────────────────────────────

def _canonical_hash(payload, exclude_keys=()):
    """canonical JSON(sort_keys) → sha256. exclude_keys 제외(strip-set)."""
    d = {k: v for k, v in payload.items() if k not in exclude_keys}
    return hashlib.sha256(
        json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _measured_at_of(rows, ts_field="timestamp_utc"):
    """content-derived measured_at ≡ max(rows.<ts_field>) — wall-clock 무관, same-input 불변.

    집계 포함 row 0(dormant/empty) → None (measured-0 위장 금지, AC-5). 원본 문자열 반환.
    """
    best = None  # (parsed_dt, original_str)
    for r in rows:
        raw = r.get(ts_field)
        dt = _parse_utc_z(raw)
        if dt is None:
            continue
        cand = (dt, raw)
        if best is None or cand > best:
            best = cand
    return best[1] if best is not None else None


def _status_of(input_row_count):
    """status — 관측 row ≥1 → measured(측정, count 0 포함) / 0 → pending(dormant). AC-5 measured-0≠dormant."""
    return "measured" if input_row_count > 0 else "pending"


def _scoped_stats(stats, scoped_rows):
    """per-scope 경량 stats (honesty_note 전파 + scope row 수). port stats 는 전역이라 근사."""
    return {
        "rows_total": len(scoped_rows),
        "rows_deduped": len(scoped_rows),
        "duplicates_collapsed": 0,
        "honesty_note": stats.get("honesty_note") if isinstance(stats, dict) else None,
    }


def _partition_rows_by_scope(rows):
    """consumer_scope 로 row partition (§4.4/§7.4.5 — port filter 키 아님, raw row read + group).

    missing/미등재 scope → scope_unknown bucket.
    """
    buckets = {"wrapper": [], "consumer": [], "scope_unknown": []}
    for r in rows:
        sc = r.get("consumer_scope")
        if sc == "wrapper":
            buckets["wrapper"].append(r)
        elif sc == "consumer":
            buckets["consumer"].append(r)
        else:
            buckets["scope_unknown"].append(r)
    return buckets


def _rows_of_type(rows, *event_types):
    ets = set(event_types)
    return [r for r in rows if r.get("event_type") in ets]


# ═══════════════════════ 지표① cycletime — lane residency (§4.1, AC-7/8) ═══════════════

def compute_cycletime(rows, stats):
    """지표① lane residency (pure fn). 동일 story_key 내 lane 진입 → 종료 앵커까지 residency.

    종료 앵커 우선순위 = next-different-lane lane_transition > final_artifact > verdict > open.
    재진입 = 별 구간. negative/reverse-duration → EXCLUDE + count. 라벨 = "lane residency"(NOT time-to-PASS).
    """
    anchor_events = _rows_of_type(rows, "lane_transition", "final_artifact", "verdict")

    by_story = {}
    for r in anchor_events:
        by_story.setdefault(r.get("story_key"), []).append(r)

    interval_count = 0
    open_interval_count = 0
    negative_duration_count = 0
    unparseable_entry_count = 0
    residency_seconds = []
    anchor_kind_counts = {"next_different_lane": 0, "final_artifact": 0, "verdict": 0}
    by_group = {}

    # unparseable ts 를 가진 lane_transition 진입 (timing 불가) 별도 관측
    for r in _rows_of_type(rows, "lane_transition"):
        if _parse_utc_z(r.get("timestamp_utc")) is None:
            unparseable_entry_count += 1

    for story, evs in by_story.items():
        # ★append(emission) order 보존 — ts 재정렬 금지. 종료 앵커 = 다음 사건(인과 순서). clock-step
        #   시 anchor.ts < entry.ts → negative residency 관측 가능(ts 재정렬 시 이 신호 소실).
        for i, e in enumerate(evs):
            if e.get("event_type") != "lane_transition":
                continue
            lane = e.get("lane_label")
            t_entry = _parse_utc_z(e.get("timestamp_utc"))
            interval_count += 1
            gkey = "%s::%s" % (story, lane)
            grp = by_group.setdefault(gkey, {
                "interval_count": 0, "open_interval_count": 0,
                "negative_duration_count": 0, "closed_interval_count": 0,
                "residency_seconds_sum": 0.0,
            })
            grp["interval_count"] += 1

            anchor_ev = None
            anchor_kind = None
            first_final = None
            first_verdict = None
            for e2 in evs[i + 1:]:
                et2 = e2.get("event_type")
                if et2 == "lane_transition" and e2.get("lane_label") != lane:
                    anchor_ev, anchor_kind = e2, "next_different_lane"
                    break  # append 순서 최초 different-lane = 최우선 앵커(priority > final/verdict)
                if first_final is None and et2 == "final_artifact":
                    first_final = e2
                elif first_verdict is None and et2 == "verdict":
                    first_verdict = e2
            if anchor_ev is None:
                if first_final is not None:
                    anchor_ev, anchor_kind = first_final, "final_artifact"
                elif first_verdict is not None:
                    anchor_ev, anchor_kind = first_verdict, "verdict"

            if anchor_ev is None:
                open_interval_count += 1
                grp["open_interval_count"] += 1
                continue
            t_anchor = _parse_utc_z(anchor_ev.get("timestamp_utc"))
            if t_entry is None or t_anchor is None:
                open_interval_count += 1  # timing 불가(unparseable) → duration 집계 제외
                grp["open_interval_count"] += 1
                continue
            dur = (t_anchor - t_entry).total_seconds()
            if dur < 0:
                negative_duration_count += 1  # reverse/clock-step → EXCLUDE + count (§7.4.3)
                grp["negative_duration_count"] += 1
                continue
            anchor_kind_counts[anchor_kind] += 1
            residency_seconds.append(dur)
            grp["closed_interval_count"] += 1
            grp["residency_seconds_sum"] += dur

    closed = len(residency_seconds)
    residency_summary = {
        "count": closed,
        "min_seconds": round(min(residency_seconds), 3) if closed else None,
        "max_seconds": round(max(residency_seconds), 3) if closed else None,
        "sum_seconds": round(sum(residency_seconds), 3) if closed else None,
        "mean_seconds": round(sum(residency_seconds) / closed, 3) if closed else None,
    }
    return {
        "metric": "cycletime",
        "label": "lane residency",  # NOT time-to-PASS (transition_point subtype 부재)
        "interval_count": interval_count,
        "closed_interval_count": closed,
        "open_interval_count": open_interval_count,
        "negative_duration_count": negative_duration_count,
        "clock_anomaly_count": negative_duration_count,  # reverse-duration = clock 이상 신호
        "unparseable_ts_entry_count": unparseable_entry_count,
        "residency_seconds": residency_summary,
        "end_anchor_kind_counts": anchor_kind_counts,
        "by_group": by_group,
        "honesty_note": (
            "lane residency = coarse(transition_point 부재 → 진입/PASS/재진입 6-point 미구분). "
            "wall-clock best-effort — host clock-adjust 시 negative/inflated 가능(negative → EXCLUDE + count). "
            "time-to-PASS 아님. forward-scan = per-story bounded degradation(임의 입력 무해 보장 아님)."
        ),
    }


# ═══════════════════════ 지표② fixloop — attempt + iteration (§4.2, AC-9/10) ═══════════

def compute_fixloop(rows, stats):
    """지표② FIX loop (pure fn). 2 분리 관측 라벨 (attempt ≥ iteration, distinct fix_id ≠ iteration).

    fix_attempt_count = count(distinct non-null fix_id) per (story, lane) — per-defect attempt.
    fix_iteration_count = count(fix_transition events) per (story, lane) — §10 re-entry proxy.
    fix_id=null fix_transition row → attempt 제외 + fix_id_missing_rows (AC-10). (iteration 은 계수)
    """
    by_group = {}
    fix_id_missing_rows = 0

    def _grp(story, lane):
        return by_group.setdefault("%s::%s" % (story, lane), {
            "fix_ids": set(), "fix_iteration_count": 0,
        })

    # attempt: 모든 event 의 non-null fix_id (상관 field — 특정 event_type 에 종속 안 함)
    for r in rows:
        fid = r.get("fix_id")
        if isinstance(fid, str) and fid:
            _grp(r.get("story_key"), r.get("lane_label"))["fix_ids"].add(fid)

    # iteration: fix_transition event 수 (§10 monopoly re-entry unit proxy)
    for r in _rows_of_type(rows, "fix_transition"):
        g = _grp(r.get("story_key"), r.get("lane_label"))
        g["fix_iteration_count"] += 1
        fid = r.get("fix_id")
        if not (isinstance(fid, str) and fid):
            fix_id_missing_rows += 1  # null fix_id fix_transition → attempt 제외(AC-10)

    groups = {}
    total_attempt = 0
    total_iteration = 0
    invariant_holds = True
    for gkey, g in by_group.items():
        attempt = len(g["fix_ids"])
        iteration = g["fix_iteration_count"]
        total_attempt += attempt
        total_iteration += iteration
        if attempt < iteration:
            invariant_holds = False  # 관측 — 구조 보장 아님(honest)
        groups[gkey] = {"fix_attempt_count": attempt, "fix_iteration_count": iteration}

    return {
        "metric": "fixloop",
        "label_attempt": "fix_attempt_count = distinct non-null fix_id (per-defect attempt)",
        "label_iteration": "fix_iteration_count = fix_transition event 수 (§10 re-entry proxy)",
        "by_group": groups,
        "total_fix_attempt_count": total_attempt,
        "total_fix_iteration_count": total_iteration,
        "fix_id_missing_rows": fix_id_missing_rows,
        "attempt_ge_iteration_observed": invariant_holds,
        "honesty_note": (
            "attempt(distinct fix_id) 와 iteration(fix_transition 수)은 독립 관측 축 — distinct fix_id 를 "
            "iteration 으로 라벨링 금지. iteration = §10 re-entry proxy(transition_point 부재 → coarse). "
            "attempt≥iteration 은 관측(구조 보장 아님)."
        ),
    }


# ═══════════════════════ 지표③ defect-attribution (§4.3, AC-11/12/13) ══════════════════

def _capture_subject(detecting_lane):
    """detecting_lane → capture_subject {lane, gate, undetermined} (AC-12 advisory heuristic).

    사람 리뷰 lane → 'lane' / 기계 CI 게이트 lane → 'gate' / 미매핑 → 'undetermined'(honest-degrade).
    """
    if detecting_lane in _CAPTURE_SUBJECT_LANE:
        return "lane"
    if detecting_lane in _CAPTURE_SUBJECT_GATE:
        return "gate"
    return "undetermined"


def compute_defect_attribution(rows, stats):
    """지표③ 결점 귀속 + capture-subject + should-have-caught (pure fn).

    count group-by detecting_lane × defect_family × defect_type (AC-11).
    lane_label='없음'(NON-ambient) → review-lane 분모 제외 + non_ambient_defect_rows.
    capture_subject ∈ {lane,gate,undetermined} (AC-12). should-have-caught = advisory(AC-13).
    """
    defects = _rows_of_type(rows, "defect_finding")

    attribution_counts = {}
    capture_subject_counts = {"lane": 0, "gate": 0, "undetermined": 0}
    non_ambient_defect_rows = 0
    review_lane_denominator = 0
    shc_computable = 0
    shc_unattributed = 0
    shc_by_detecting_lane = {}

    for r in defects:
        dl = r.get("detecting_lane")
        fam = r.get("defect_family")
        typ = r.get("defect_type")
        key = "%s|%s|%s" % (dl, fam, typ)
        attribution_counts[key] = attribution_counts.get(key, 0) + 1

        capture_subject_counts[_capture_subject(dl)] += 1

        if r.get("lane_label") == "없음":
            non_ambient_defect_rows += 1  # NON-ambient — 리뷰 lane 효용 분모 제외
        else:
            review_lane_denominator += 1

        # should-have-caught (advisory — origin/expected-lane 부재 → ground-truth 단정 금지)
        ttd = r.get("time_to_detection")
        if ttd == _TTD_UNATTRIBUTED or ttd is None:
            shc_unattributed += 1  # uncomputable
        else:
            shc_computable += 1
            bucket = shc_by_detecting_lane.setdefault(str(dl), {"computable": 0})
            bucket["computable"] += 1

    return {
        "metric": "defect-attribution",
        "attribution_counts": attribution_counts,  # detecting_lane × defect_family × defect_type
        "defect_finding_rows": len(defects),
        "capture_subject_counts": capture_subject_counts,
        "non_ambient_defect_rows": non_ambient_defect_rows,
        "review_lane_denominator": review_lane_denominator,
        "should_have_caught": {
            "label": "advisory heuristic — NOT ground-truth expected-lane",
            "computable_count": shc_computable,
            "unattributed_uncomputable_count": shc_unattributed,
            "by_detecting_lane": shc_by_detecting_lane,
        },
        "honesty_note": (
            "capture_subject = review-responsibility lane↔mechanism 근사(capture-mechanism field 부재) — "
            "미매핑 detecting_lane → undetermined(honest-degrade). should-have-caught = advisory heuristic "
            "(origin/expected-lane substrate 부재 → 기대 lane ground-truth 단정 금지). "
            "time_to_detection=unattributed → uncomputable. 외부 매핑(DRE/PCE)은 origin_lane fallible estimate."
        ),
    }


# ═══════════════════════ 지표④ selfref-recurrence (§4.4, AC-14/15) ═════════════════════

def compute_selfref_recurrence(rows, stats):
    """지표④ 재발 (pure fn). 동일 defect_id 재출현(선행 관측 존재) → recurrence event.

    집계 키 = {defect_family, defect_type, time_to_detection, detecting_lane} 4-tuple (AC-14).
    general recurrence(기계) 와 self-ref candidate(heuristic) 분리. defect_id=null → 별도 count.
    """
    # ★append(emission) order = 인과 선행 관측 truth (port ledger order 보존). ts 재정렬 금지
    #   (clock-step 시 ts 순서 ≠ 인과 순서 → "선행 관측 존재" 판정 왜곡 회피).
    defects = _rows_of_type(rows, "defect_finding")

    seen_defect_ids = set()
    recurrence_count = 0
    self_ref_candidate_count = 0
    defect_id_missing_rows = 0
    profiles = {}  # 4-tuple key → occurrences

    for r in defects:
        did = r.get("defect_id")
        if not (isinstance(did, str) and did):
            defect_id_missing_rows += 1
            continue
        if did in seen_defect_ids:
            recurrence_count += 1
            fam = r.get("defect_family")
            typ = r.get("defect_type")
            ttd = r.get("time_to_detection")
            dl = r.get("detecting_lane")
            tup = "%s|%s|%s|%s" % (fam, typ, ttd, dl)  # 4-tuple (never boolean-flag-only)
            profiles[tup] = profiles.get(tup, 0) + 1
            if fam in _SELF_REF_PRONE_FAMILIES:
                self_ref_candidate_count += 1  # advisory heuristic subset
        else:
            seen_defect_ids.add(did)

    return {
        "metric": "selfref-recurrence",
        "recurrence_count": recurrence_count,  # general (기계 산출)
        "recurrence_profiles_4tuple": profiles,  # {family|type|ttd|detecting_lane: occurrences}
        "self_ref_candidate_count": self_ref_candidate_count,  # heuristic (advisory)
        "distinct_defect_ids": len(seen_defect_ids),
        "defect_id_missing_rows": defect_id_missing_rows,
        "honesty_note": (
            "recurrence = 관측 재발률(exact 아님). defect_id = sha256(family‖type‖normalized-location) "
            "best-effort — normalized-location 안정성 무보장. self-ref candidate = heuristic(substrate 에 "
            "Story-purpose↔family alignment 부재) — general recurrence(기계) 와 분리 라벨, ground-truth 아님."
        ),
    }


# ═══════════════════════ 지표⑤ trend + §D-9 feed (§4.5, AC-16/17/18/19) ════════════════

def compute_trend(rows, stats):
    """지표⑤ 추세(bucketed observational, NO forecast) + §D-9 pattern feed (pure fn).

    pattern_count = count(distinct story_key) for same {anchor_id, root_cause_class} within window.
    ★anchor_id/root_cause_class = _ROW_KEYS 18-field 부재 → pattern_count=null +
      pattern_status='uncomputable_missing_key' 가 DEFAULT 경로(edge 아님, AC-19).
    escalation action(adr_draft_emitted/escalate_user) 미포함 — B=producer, PMO=decider(INV-B3).
    within-scope only (cross-scope union 금지).
    """
    time_series = {}
    for r in rows:
        dt = _parse_utc_z(r.get("timestamp_utc"))
        bucket = dt.strftime("%Y-%m-%d") if dt is not None else "unparseable"
        b = time_series.setdefault(bucket, {"total": 0, "by_event_type": {}})
        b["total"] += 1
        et = r.get("event_type")
        b["by_event_type"][et] = b["by_event_type"].get(et, 0) + 1

    # §D-9 pattern feed — anchor_id/root_cause_class 키 substrate 존재 여부 관측
    has_anchor = any(r.get("anchor_id") is not None for r in rows)
    has_rcc = any(r.get("root_cause_class") is not None for r in rows)
    if has_anchor and has_rcc:
        # (미도래 경로 — 현재 substrate 18-field 에 부재. within-scope distinct story_key count)
        grouping = {}
        for r in rows:
            a = r.get("anchor_id")
            c = r.get("root_cause_class")
            if a is None or c is None:
                continue
            grouping.setdefault((a, c), set()).add(r.get("story_key"))
        pattern_count = max((len(v) for v in grouping.values()), default=0)
        pattern_status = "computable"
        anchor_id = None
        root_cause_class = None
    else:
        pattern_count = None  # ★DEFAULT — uncomputable_missing_key
        pattern_status = "uncomputable_missing_key"
        anchor_id = None
        root_cause_class = None

    return {
        "metric": "trend",
        "time_series": time_series,  # bucketed observational (NO forecast/prediction/projection)
        "bucket_unit": "date_utc",
        # §D-9 feed 필드 (schema-pin 대상 — snapshot top-level 로도 승격)
        "pattern_count": pattern_count,
        "pattern_status": pattern_status,
        "anchor_id": anchor_id,
        "root_cause_class": root_cause_class,
        "honesty_note": (
            "observational time-series only — forecast/prediction/projection 필드 부재(negative control). "
            "pattern_count = anchor_id/root_cause_class substrate 부재 → uncomputable_missing_key(DEFAULT, "
            "edge 아님). §D-9 feed = producer-defined, currently uncomputable-by-substrate. escalation ACTION "
            "미산출(B=producer, PMOAgent=decider — INV-B3). within-scope only(cross-scope union 금지)."
        ),
    }


# ═══════════════════════ 지표⑥ token-cost (§4.6, AC-20/21/22) ══════════════════════════

def compute_token_cost(spawn_rows, stats):
    """지표⑥ token-cost / context (pure fn). spawn-event-v1 소비 (INV-B4 event_id 상관만).

    ★3-gap 미해소 → honest-null + upstream_gap_flags REGARDLESS (per_call_missing 구조 /
      cache_ttl_split_missing 구조 / actuals_missing 데이터). raw class count 저장 + read-time 가중
      (flat-sum 금지). cache_write_1h(2×) = cost_usd 단일 1.25× 배수로 유도 불가 → honest-null.
      B 내부 spawn-event capture-fix row 생성 금지(spawn-event-v1/ADR-163·043 소관).
    """
    # raw class count 누적 (spawn row = per-agent replay event; token actuals 대개 null=unattributed)
    class_sums = {"uncached_input": 0, "cache_read": 0, "cache_write_5m": 0}  # 1h class = 유도 불가
    any_actual = False
    weighted_cost_sum = 0.0
    any_derivable_cost = False

    for r in spawn_rows:
        it = r.get("input_tokens")
        ot = r.get("output_tokens")
        cc = r.get("cache_creation_input_tokens")  # 단일 (5m/1h split 부재)
        cr = r.get("cache_read_input_tokens")
        if isinstance(it, int):
            class_sums["uncached_input"] += it
            any_actual = True
        if isinstance(cr, int):
            class_sums["cache_read"] += cr
            any_actual = True
        if isinstance(cc, int):
            class_sums["cache_write_5m"] += cc  # 단일 cache_creation → 5m rate(1.25×)로만 해석
            any_actual = True
        # read-time 가중 cost (flat-sum 금지 — cost_usd = input 1× / output rate / cc 1.25× / cr 0.1×)
        model = r.get("model")
        if model and None not in (it, ot, cc, cr):
            c = cost_usd(model, it, ot, cc, cr)
            if c is not None:
                weighted_cost_sum += c
                any_derivable_cost = True

    # upstream_gap_flags — per_call/cache_ttl 는 구조적(상시), actuals 는 데이터 조건
    upstream_gap_flags = ["per_call_missing", "cache_ttl_split_missing"]
    if not any_actual:
        upstream_gap_flags.append("actuals_missing")

    # honest-null: 파생 headline 값은 null (per_call_missing → per-call peak 유도 불가)
    token_class_counts = {
        "uncached_input": class_sums["uncached_input"] if any_actual else None,
        "cache_read": class_sums["cache_read"] if any_actual else None,
        "cache_write_5m": class_sums["cache_write_5m"] if any_actual else None,
        "cache_write_1h": None,  # ★honest-null — cache_ttl_split_missing (유도 불가)
    }
    return {
        "metric": "token-cost",
        "spawn_rows_observed": len(spawn_rows),
        "token_cost_status": "honest_null",
        "peak_context_tokens": None,          # per_call_missing → per-call peak 유도 불가
        "total_weighted_cost_usd": None,      # honest-null (3-gap 미해소 — 파생 production 값 fabricate 금지)
        "class_weighted_cost_probe_usd": (round(weighted_cost_sum, 6)
                                          if any_derivable_cost else None),  # 가중 규칙 시연치(≠production)
        "token_class_counts": token_class_counts,  # raw class count (read-time 가중 대상)
        "class_weights": dict(_TOKEN_CLASS_WEIGHTS),  # documented 가중 (flat-sum 금지 증빙)
        "upstream_gap_flags": upstream_gap_flags,
        "honesty_note": (
            "token-cost = honest-null(3-gap 미해소): per-call not per-agent / cache 5m·1h split 부재 / "
            "actuals null=unattributed. cache_write_1h(2×) = cost_usd 단일 1.25× 배수로 유도 불가 → null. "
            "raw class count 저장 + read-time 가중(flat-sum 금지, 최대 ~20× 오차 회피). event_id JOIN "
            "correlation-only(INV-B4) — dev-process 로 token accounting re-record 금지(INV-B2). "
            "spawn-event capture-fix row 미생성. class_weighted_cost_probe = 가중 규칙 시연치(production 아님)."
        ),
        "no_capture_fix": True,  # B 는 spawn-event capture-fix row 생성 안 함 (AC-22)
    }


# ═══════════════════════ orchestrator (port read 1x + fan-out + KPI dual write) ═════════

_COMPUTE_FNS = {
    "cycletime": compute_cycletime,
    "fixloop": compute_fixloop,
    "defect-attribution": compute_defect_attribution,
    "selfref-recurrence": compute_selfref_recurrence,
    "trend": compute_trend,
}


def _build_snapshot(metric_name, overall, partition, stats, measured_at,
                    status, generated_at_kst=None):
    """지표 body → §4.7 de-facto snapshot schema 조립 (generated_at_kst 주입 가능 — 테스트용)."""
    snap = {
        "schema_note": (
            "dev-process-%s-v1 (de-facto local KPI schema, NOT inter-plugin contract)" % metric_name
        ),
        "generated_at_kst": generated_at_kst if generated_at_kst is not None else _kst_now_iso(),
        "measured_at": measured_at,      # content-derived pin (max timestamp_utc) | null
        "status": status,               # measured | pending
        "metric": metric_name,
        "overall": overall,
        "consumer_scope_partition": partition,
        "stats": {
            "rows_total": stats.get("rows_total"),
            "rows_deduped": stats.get("rows_deduped"),
            "duplicates_collapsed": stats.get("duplicates_collapsed"),
            "honesty_note": stats.get("honesty_note"),
        },
        "tier_honesty": [_HONESTY_TIER, _HONESTY_DEGRADE],
    }
    # trend: §D-9 feed 필드 snapshot top-level 승격 (schema-pin 대상)
    if metric_name == "trend":
        snap["pattern_count"] = overall.get("pattern_count")
        snap["pattern_status"] = overall.get("pattern_status")
        snap["anchor_id"] = overall.get("anchor_id")
        snap["root_cause_class"] = overall.get("root_cause_class")
    return snap


def aggregate_rows(rows, stats, spawn_rows=None, spawn_stats=None, generated_at_kst=None):
    """6 지표 compute + 6 snapshot 조립 (KPI write 안 함 — pure aggregate). Returns {metric: snapshot}.

    ①-⑤ = dev-process rows partition-by-scope. ⑥ = spawn rows (INV-B4). generated_at_kst 주입 가능.
    """
    spawn_rows = spawn_rows or []
    spawn_stats = spawn_stats or {"rows_total": len(spawn_rows), "rows_deduped": len(spawn_rows),
                                  "duplicates_collapsed": 0, "honesty_note": _SPAWN_STATS_HONESTY}
    measured_at_dp = _measured_at_of(rows)
    status_dp = _status_of(len(rows))
    scope_buckets = _partition_rows_by_scope(rows)

    snapshots = {}
    for name, fn in _COMPUTE_FNS.items():
        overall = fn(rows, stats)
        partition = {
            sc: fn(scoped, _scoped_stats(stats, scoped))
            for sc, scoped in scope_buckets.items()
        }
        snapshots[name] = _build_snapshot(
            name, overall, partition, stats, measured_at_dp, status_dp,
            generated_at_kst=generated_at_kst,
        )

    # 지표⑥ token-cost — spawn rows (별 timestamp field / status)
    tc_overall = compute_token_cost(spawn_rows, spawn_stats)
    tc_partition = {
        sc: compute_token_cost([r for r in spawn_rows if r.get("consumer_scope") == sc]
                               if sc != "scope_unknown"
                               else [r for r in spawn_rows
                                     if r.get("consumer_scope") not in ("wrapper", "consumer")],
                               spawn_stats)
        for sc in ("wrapper", "consumer", "scope_unknown")
    }
    snapshots["token-cost"] = _build_snapshot(
        "token-cost", tc_overall, tc_partition, spawn_stats,
        _measured_at_of(spawn_rows), _status_of(len(spawn_rows)),
        generated_at_kst=generated_at_kst,
    )
    return snapshots


def _atomic_write_json(path, payload):
    """temp → os.replace atomic write (torn-write 안전). newline='\\n' (Windows CRLF 회피)."""
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-kpi-", suffix=".json", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _existing_history_hashes(history_path):
    """history.jsonl 기존 row 의 canonical hash(strip generated_at_kst) set — dedup 판정용."""
    hashes = set()
    if not os.path.exists(history_path):
        return hashes
    try:
        text = Path(history_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return hashes
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            hashes.add(_canonical_hash(row, exclude_keys=_IDENTITY_STRIP_KEYS))
    return hashes


def _write_kpi_dual(kpi_dir, metric_name, snapshot):
    """snapshot.json atomic overwrite + history.jsonl content-hash-guarded append (INV-B6).

    dedup key = payload canonical hash EXCLUDING generated_at_kst (§11.6, X⊆X tautology 회피 —
    strip-set = CODE CONSTANT). unchanged ledger 재실행 → history +0. changed input → +1.
    Returns (snapshot_path, history_path, history_appended: bool).
    """
    os.makedirs(kpi_dir, exist_ok=True)
    snap_path = os.path.join(kpi_dir, "dev-process-%s-snapshot.json" % metric_name)
    hist_path = os.path.join(kpi_dir, "dev-process-%s-history.jsonl" % metric_name)

    _atomic_write_json(snap_path, snapshot)

    new_hash = _canonical_hash(snapshot, exclude_keys=_IDENTITY_STRIP_KEYS)
    existing = _existing_history_hashes(hist_path)
    appended = False
    if new_hash not in existing:
        line = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
        with open(hist_path, "a", encoding="utf-8", newline="\n") as f:  # append-only (prefix byte 불변)
            f.write(line + "\n")
        appended = True
    return snap_path, hist_path, appended


def _read_spawn_rows(spawn_ledger_path=None):
    """spawn-event rows via 승인된 replay reader CLI(json mode) — INV-B4 raw parse 금지. graceful → []."""
    replay = os.path.join(_HERE, "replay_spawn_event.py")
    if not os.path.exists(replay):
        return []
    cmd = [sys.executable, replay, "--format", "json"]
    if spawn_ledger_path:
        cmd += ["--ledger-path", str(spawn_ledger_path)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except Exception:
        return []
    if out.returncode != 0 or not out.stdout.strip():
        return []
    try:
        payload = json.loads(out.stdout)
    except ValueError:
        return []
    events = payload.get("events") if isinstance(payload, dict) else None
    return events if isinstance(events, list) else []


def aggregate_file(ledger_path=None, kpi_dir=None, since=None, until=None,
                   write=True, spawn_ledger_path=None):
    """orchestrator — port read 1회 + 6 지표 fan-out + KPI dual write. Returns summary dict."""
    rows, stats = query_with_stats(ledger_path=ledger_path, since=since, until=until)  # INV-B1 (include_blob=False default)
    spawn_rows = _read_spawn_rows(spawn_ledger_path)
    snapshots = aggregate_rows(rows, stats, spawn_rows=spawn_rows)

    written = {}
    if write:
        kd = kpi_dir or os.path.join(_REPO_ROOT, "docs", "kpi")
        for name in _METRIC_NAMES:
            snap_path, hist_path, appended = _write_kpi_dual(kd, name, snapshots[name])
            written[name] = {"snapshot": snap_path, "history": hist_path, "history_appended": appended}
    return {
        "rows_deduped": stats.get("rows_deduped"),
        "spawn_rows_observed": len(spawn_rows),
        "measured_at": _measured_at_of(rows),
        "status": _status_of(len(rows)),
        "snapshots": snapshots,
        "written": written,
    }


# ─────────────────────── 렌더 (stdout, local only — 0 API call) ───────────────────────

def render(summary):
    lines = []
    lines.append("=" * 72)
    lines.append("dev-process-event 지표 aggregate — tier [measurement] (B lane, record-only)")
    lines.append("=" * 72)
    lines.append("rows_deduped        : %s" % summary["rows_deduped"])
    lines.append("spawn_rows_observed : %s" % summary["spawn_rows_observed"])
    lines.append("measured_at         : %s" % summary["measured_at"])
    lines.append("status              : %s" % summary["status"])
    lines.append("-" * 72)
    for name in _METRIC_NAMES:
        w = summary["written"].get(name)
        if w:
            lines.append("  %-20s snapshot=%s history+%s"
                         % (name, os.path.basename(w["snapshot"]), int(w["history_appended"])))
        else:
            lines.append("  %-20s (no-write)" % name)
    lines.append("-" * 72)
    lines.append("HONESTY: " + _HONESTY_TIER)
    lines.append("HONESTY: " + _HONESTY_DEGRADE)
    lines.append("=" * 72)
    return "\n".join(lines)


# ─────────────────────── self-test (execution-backed, independent-oracle, hollow 금지) ──

def _mk_row(event_type, story_key, lane_label, event_id, ts,
            consumer_scope="wrapper", defect_id=None, fix_id=None,
            defect_family=None, defect_type=None, time_to_detection=None,
            detecting_lane=None):
    """18-field dev-process index row (self-test fixture — composition-derived)."""
    return {
        "event_id": event_id, "schema_version": "dev-process-event-v1",
        "event_type": event_type, "emit_source": "agent", "timestamp_utc": ts,
        "story_key": story_key, "lane_label": lane_label, "consumer_scope": consumer_scope,
        "defect_id": defect_id, "fix_id": fix_id, "blob_ref": None,
        "redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": [],
        "defect_family": defect_family, "defect_type": defect_type,
        "time_to_detection": time_to_detection, "detecting_lane": detecting_lane,
    }


def _self_test():
    """inline synthetic fixtures 로 실제 compute/write 호출 후 관측 대조.

    composition-derived expected(자기 계산값 self-match 금지) + metamorphic cross-run + 대칭 fail-closed
    (3축) + idempotency 2축(strip-set=CODE CONSTANT) + no-blob-deref. AC-4~23 Phase-2 커버.
    """
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    zero_stats = {"rows_total": 0, "rows_deduped": 0, "duplicates_collapsed": 0,
                  "honesty_note": "test-stats"}

    # ── _parse_utc_z: UTC-Z vs naive negative-control (KST clone 9h skew 부재, §3.3) ──
    dt_z = _parse_utc_z("2026-07-15T10:00:00Z")
    dt_naive = _parse_utc_z("2026-07-15T10:00:00")
    check(dt_z is not None and dt_naive is not None
          and (dt_z - dt_naive).total_seconds() == 0.0,
          "[parse] naive-fallback ≠ UTC (KST 9h skew clone 함정)")

    # ═══ AC-7: cycletime ordered fixtures (handoff / terminal final / terminal verdict) ═══
    ct_rows = [
        # story S1: 설계(entry) → 설계-리뷰(next-different-lane 앵커) → final_artifact
        _mk_row("lane_transition", "S1", "설계", "c1", "2026-07-15T10:00:00Z"),
        _mk_row("lane_transition", "S1", "설계-리뷰", "c2", "2026-07-15T10:00:10Z"),
        _mk_row("final_artifact", "S1", "설계-리뷰", "c3", "2026-07-15T10:00:40Z"),
        # story S2: 구현(entry) → verdict (terminal verdict 앵커, no next lane)
        _mk_row("lane_transition", "S2", "구현", "c4", "2026-07-15T10:00:00Z"),
        _mk_row("verdict", "S2", "구현", "c5", "2026-07-15T10:00:05Z"),
    ]
    ct = compute_cycletime(ct_rows, zero_stats)
    # composition-derived expected: S1 설계 = 10s(next-different-lane), S1 설계-리뷰 = 30s(final),
    #   S2 구현 = 5s(verdict). closed=3, sum=45.
    check(ct["closed_interval_count"] == 3, "[AC-7] closed_interval %s != 3" % ct["closed_interval_count"])
    check(ct["residency_seconds"]["sum_seconds"] == 45.0,
          "[AC-7] residency sum %s != 45" % ct["residency_seconds"]["sum_seconds"])
    check(ct["end_anchor_kind_counts"]["next_different_lane"] == 1
          and ct["end_anchor_kind_counts"]["final_artifact"] == 1
          and ct["end_anchor_kind_counts"]["verdict"] == 1,
          "[AC-7] end-anchor priority 분류 오류: %s" % ct["end_anchor_kind_counts"])
    check(ct["label"] == "lane residency", "[AC-7] label ≠ lane residency")

    # ═══ AC-8: open-ended → open_interval_count only ═══
    open_rows = [_mk_row("lane_transition", "S3", "배포", "o1", "2026-07-15T10:00:00Z")]
    ct_open = compute_cycletime(open_rows, zero_stats)
    check(ct_open["open_interval_count"] == 1 and ct_open["closed_interval_count"] == 0,
          "[AC-8] open-ended → open only 아님: %s" % ct_open)

    # ── cycletime 대칭 fail-closed (b) negative-duration → EXCLUDE + count ──
    neg_rows = [
        _mk_row("lane_transition", "S4", "구현", "n1", "2026-07-15T10:00:30Z"),
        _mk_row("final_artifact", "S4", "구현", "n2", "2026-07-15T10:00:00Z"),  # 역순 ts
    ]
    ct_neg = compute_cycletime(neg_rows, zero_stats)
    check(ct_neg["negative_duration_count"] == 1 and ct_neg["closed_interval_count"] == 0,
          "[fail-closed] negative-duration EXCLUDE 아님: %s" % ct_neg)

    # ── metamorphic cross-run (하드코딩 방어): +1 interval → closed +1 ──
    ct_plus = compute_cycletime(ct_rows + [
        _mk_row("lane_transition", "S5", "구현", "c6", "2026-07-15T10:00:00Z"),
        _mk_row("verdict", "S5", "구현", "c7", "2026-07-15T10:00:07Z"),
    ], zero_stats)
    check(ct_plus["closed_interval_count"] - ct["closed_interval_count"] == 1,
          "[metamorphic-ct] closed delta != 1 (하드코딩 의심)")

    # ═══ AC-9: 1 iteration → many fix_id (attempt ≥ iteration) ═══
    fx_rows = [
        # 1 fix_transition (iteration=1) + defect_finding 2건이 별 fix_id 보유 → attempt=3
        _mk_row("fix_transition", "S6", "구현-리뷰", "f1", "2026-07-15T10:00:00Z", fix_id="FIXA"),
        _mk_row("defect_finding", "S6", "구현-리뷰", "f2", "2026-07-15T10:00:01Z",
                fix_id="FIXB", defect_id="d1", defect_family="correctness", defect_type="logic"),
        _mk_row("defect_finding", "S6", "구현-리뷰", "f3", "2026-07-15T10:00:02Z",
                fix_id="FIXC", defect_id="d2", defect_family="correctness", defect_type="logic"),
    ]
    fx = compute_fixloop(fx_rows, zero_stats)
    g6 = fx["by_group"]["S6::구현-리뷰"]
    check(g6["fix_attempt_count"] == 3 and g6["fix_iteration_count"] == 1,
          "[AC-9] attempt=3/iteration=1 아님: %s" % g6)
    check(fx["attempt_ge_iteration_observed"] is True, "[AC-9] attempt≥iteration 관측 실패")

    # ═══ AC-10: null fix_id fix_transition → fix_id_missing_rows ═══
    fx_null = compute_fixloop([
        _mk_row("fix_transition", "S7", "구현", "fn1", "2026-07-15T10:00:00Z", fix_id=None),
    ], zero_stats)
    check(fx_null["fix_id_missing_rows"] == 1 and fx_null["total_fix_attempt_count"] == 0,
          "[AC-10] null fix_id → missing_rows 아님: %s" % fx_null)

    # ── fixloop metamorphic: +1 distinct fix_id → attempt +1 ──
    fx_plus = compute_fixloop(fx_rows + [
        _mk_row("defect_finding", "S6", "구현-리뷰", "f4", "2026-07-15T10:00:03Z",
                fix_id="FIXD", defect_id="d3", defect_family="correctness", defect_type="logic"),
    ], zero_stats)
    check(fx_plus["by_group"]["S6::구현-리뷰"]["fix_attempt_count"] - g6["fix_attempt_count"] == 1,
          "[metamorphic-fx] attempt delta != 1")

    # ═══ AC-11: mixed-lane + '없음' (non_ambient 분리) ═══
    da_rows = [
        _mk_row("defect_finding", "S8", "구현", "a1", "2026-07-15T10:00:00Z",
                defect_id="da1", defect_family="design-boundary", defect_type="coupling",
                detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk_row("defect_finding", "S8", "없음", "a2", "2026-07-15T10:00:01Z",
                defect_id="da2", defect_family="process-discipline", defect_type="gate",
                detecting_lane="구현-테스트", time_to_detection=_TTD_UNATTRIBUTED),
        _mk_row("defect_finding", "S8", "구현", "a3", "2026-07-15T10:00:02Z",
                defect_id="da3", defect_family="correctness", defect_type="logic",
                detecting_lane="unmapped-lane-x", time_to_detection="2"),
    ]
    da = compute_defect_attribution(da_rows, zero_stats)
    check(da["non_ambient_defect_rows"] == 1 and da["review_lane_denominator"] == 2,
          "[AC-11] non_ambient/denominator 분리 오류: %s / %s"
          % (da["non_ambient_defect_rows"], da["review_lane_denominator"]))
    check(len(da["attribution_counts"]) == 3,
          "[AC-11] attribution group %s != 3" % len(da["attribution_counts"]))

    # ═══ ★AC-12: capture_subject 3-branch {lane, gate, undetermined} execution-backed ═══
    check(_capture_subject("설계-리뷰") == "lane", "[AC-12] review lane → lane 아님")
    check(_capture_subject("구현-테스트") == "gate", "[AC-12] machine gate lane → gate 아님")
    check(_capture_subject("unmapped-lane-x") == "undetermined",
          "[AC-12] 미매핑 → undetermined 아님")
    # 위 da fixture 3-branch 정확 분류 (설계-리뷰=lane / 구현-테스트=gate / unmapped=undetermined)
    check(da["capture_subject_counts"] == {"lane": 1, "gate": 1, "undetermined": 1},
          "[AC-12] capture_subject_counts 오류: %s" % da["capture_subject_counts"])

    # ═══ AC-13: should-have-caught mapping-present + unattributed advisory ═══
    check(da["should_have_caught"]["computable_count"] == 2
          and da["should_have_caught"]["unattributed_uncomputable_count"] == 1,
          "[AC-13] should-have-caught computable/unattributed 오류: %s" % da["should_have_caught"])
    check("advisory" in da["should_have_caught"]["label"], "[AC-13] advisory 라벨 부재")

    # ═══ AC-14/15: repeated defect_id + 4-tuple + honesty ═══
    rec_rows = [
        _mk_row("defect_finding", "S9", "구현-리뷰", "r1", "2026-07-15T10:00:00Z",
                defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
                detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk_row("defect_finding", "S9", "구현-리뷰", "r2", "2026-07-15T11:00:00Z",
                defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
                detecting_lane="설계-리뷰", time_to_detection="1"),  # 재출현
        _mk_row("defect_finding", "S9", "구현-리뷰", "r3", "2026-07-15T12:00:00Z",
                defect_id=None, defect_family="correctness", defect_type="logic",
                detecting_lane="구현-리뷰"),  # null defect_id
    ]
    rec = compute_selfref_recurrence(rec_rows, zero_stats)
    check(rec["recurrence_count"] == 1, "[AC-14] recurrence %s != 1" % rec["recurrence_count"])
    check(rec["recurrence_profiles_4tuple"].get("doc-integrity|section|1|설계-리뷰") == 1,
          "[AC-14] 4-tuple profile 오류: %s" % rec["recurrence_profiles_4tuple"])
    check(rec["self_ref_candidate_count"] == 1,  # doc-integrity ∈ self-ref-prone
          "[AC-15] self_ref_candidate %s != 1" % rec["self_ref_candidate_count"])
    check(rec["defect_id_missing_rows"] == 1, "[AC-15] defect_id_missing_rows != 1")
    check("normalized-location" in rec["honesty_note"], "[AC-15] honesty note(무보장) 부재")

    # ── recurrence metamorphic: 동일 defect_id 1건 더 → recurrence +1 ──
    rec_plus = compute_selfref_recurrence(rec_rows + [
        _mk_row("defect_finding", "S9", "구현-리뷰", "r4", "2026-07-15T13:00:00Z",
                defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
                detecting_lane="설계-리뷰", time_to_detection="1"),
    ], zero_stats)
    check(rec_plus["recurrence_count"] - rec["recurrence_count"] == 1,
          "[metamorphic-rec] recurrence delta != 1")

    # ═══ AC-16/17/19: trend negative-control + no-action + pattern uncomputable(DEFAULT) ═══
    tr_rows = [
        _mk_row("lane_transition", "SA", "구현", "t1", "2026-07-15T10:00:00Z"),
        _mk_row("lane_transition", "SB", "설계", "t2", "2026-07-16T10:00:00Z"),
    ]
    tr = compute_trend(tr_rows, zero_stats)
    # AC-16 negative control: forecast/prediction/projection 필드 부재
    tr_keys = " ".join(tr.keys()).lower()
    check(not any(k in tr_keys for k in ("forecast", "predict", "projection")),
          "[AC-16] forecast/prediction 필드 존재(negative control 위반)")
    # AC-17: escalation ACTION 필드 부재 (B=producer)
    check("adr_draft_emitted" not in tr and "escalate_user" not in tr,
          "[AC-17] escalation action 필드 존재(INV-B3 위반)")
    # AC-19 DEFAULT: anchor_id/root_cause_class 부재 → pattern_count null + uncomputable_missing_key
    check(tr["pattern_count"] is None and tr["pattern_status"] == "uncomputable_missing_key",
          "[AC-19] pattern uncomputable DEFAULT 아님: %s/%s" % (tr["pattern_count"], tr["pattern_status"]))
    check(len(tr["time_series"]) == 2, "[trend] bucket %s != 2" % len(tr["time_series"]))

    # ═══ AC-21/22: token-cost class-weighted 4-class + 3-gap flags + no capture-fix ═══
    # 대칭 fail-closed (a) computable class-weight 시연 (synthetic actuals) — flat-sum 금지 확인
    tc_rows = [{
        "event_id": "sp1", "consumer_scope": "wrapper", "model": "claude-opus-4",
        "input_tokens": 1000, "output_tokens": 500,
        "cache_creation_input_tokens": 200, "cache_read_input_tokens": 4000,
    }]
    tc = compute_token_cost(tc_rows, zero_stats)
    # raw class count: uncached=1000 / cache_read=4000 / cache_write_5m=200 / 1h=None(honest-null)
    check(tc["token_class_counts"]["uncached_input"] == 1000
          and tc["token_class_counts"]["cache_read"] == 4000
          and tc["token_class_counts"]["cache_write_5m"] == 200
          and tc["token_class_counts"]["cache_write_1h"] is None,
          "[AC-21] class count/1h-honest-null 오류: %s" % tc["token_class_counts"])
    # flat-sum 금지 증빙: weighted probe ≠ 단순 합(가중 1×/0.1×/1.25× 적용 → 값 상이)
    flat_sum_tokens = 1000 + 500 + 200 + 4000
    probe = tc["class_weighted_cost_probe_usd"]
    check(probe is not None, "[AC-21] class-weight probe null (cost_usd 경로 미작동)")
    # opus input 15/1M, output 75/1M, cc 1.25×15/1M, cr 0.1×15/1M → composition-derived expected
    exp_probe = round(1000 * 15.0 / 1e6 + 500 * 75.0 / 1e6
                      + 200 * (15.0 * 1.25) / 1e6 + 4000 * (15.0 * 0.1) / 1e6, 6)
    check(probe == exp_probe, "[AC-21] weighted probe %s != expected %s" % (probe, exp_probe))
    check(abs(probe - flat_sum_tokens) > 1e-9, "[AC-21] flat-sum 과 동일(가중 미적용)")
    # AC-22: 3-gap flags(per_call/cache_ttl 구조) + no capture-fix. actuals present → actuals_missing 제외
    check("per_call_missing" in tc["upstream_gap_flags"]
          and "cache_ttl_split_missing" in tc["upstream_gap_flags"]
          and "actuals_missing" not in tc["upstream_gap_flags"],
          "[AC-22] gap flags(actuals present) 오류: %s" % tc["upstream_gap_flags"])
    check(tc["no_capture_fix"] is True, "[AC-22] no_capture_fix 아님")
    check(tc["total_weighted_cost_usd"] is None and tc["peak_context_tokens"] is None,
          "[AC-22] honest-null headline 아님")
    # 대칭 fail-closed (c) honest-null-flag: dormant spawn → all null + actuals_missing
    tc_dormant = compute_token_cost([], zero_stats)
    check(tc_dormant["token_class_counts"]["uncached_input"] is None
          and "actuals_missing" in tc_dormant["upstream_gap_flags"]
          and tc_dormant["class_weighted_cost_probe_usd"] is None,
          "[AC-22] dormant honest-null 아님: %s" % tc_dormant)

    # ═══ AC-5: empty / missing / malformed-only → measured-0 ≠ dormant ═══
    empty_snaps = aggregate_rows([], zero_stats, spawn_rows=[])
    for name in _METRIC_NAMES:
        s = empty_snaps[name]
        check(s["status"] == "pending" and s["measured_at"] is None,
              "[AC-5] %s dormant → pending/null 아님: %s/%s" % (name, s["status"], s["measured_at"]))
    # measured-0 (rows 존재하나 특정 metric count 0) — status measured + measured_at 非null
    measured0_rows = [_mk_row("prompt_input", "SM", "구현", "m1", "2026-07-15T10:00:00Z")]
    m0_stats = {"rows_total": 1, "rows_deduped": 1, "duplicates_collapsed": 0, "honesty_note": "x"}
    m0_snaps = aggregate_rows(measured0_rows, m0_stats, spawn_rows=[])
    check(m0_snaps["cycletime"]["status"] == "measured"
          and m0_snaps["cycletime"]["measured_at"] == "2026-07-15T10:00:00Z"
          and m0_snaps["cycletime"]["overall"]["interval_count"] == 0,
          "[AC-5] measured-0 ≠ dormant 실현 실패: %s" % m0_snaps["cycletime"]["status"])

    # ═══ AC-4: stats propagation + no exact-count/positive-claim wording ═══
    prop_snaps = aggregate_rows(ct_rows, {"rows_total": 5, "rows_deduped": 5,
                                          "duplicates_collapsed": 0,
                                          "honesty_note": "exact-count/guaranteed-unique 아님(port)"},
                                spawn_rows=[])
    for name in _METRIC_NAMES:
        s = prop_snaps[name]
        check(s["stats"]["honesty_note"] is not None and "아님" in s["stats"]["honesty_note"],
              "[AC-4] %s stats.honesty_note 전파 실패" % name)
    blob = json.dumps(prop_snaps, ensure_ascii=False)
    for claim in _FORBIDDEN_POSITIVE_CLAIMS:
        check(claim not in blob, "[AC-4] 금지 positive-claim 등장: %s" % claim)

    # ═══ no-blob-deref: 출력에 _blob/_blob_deref_available 부재 + 코드에 blob-deref 활성화 부재 ═══
    check("_blob" not in blob and "_blob_deref_available" not in blob,
          "[no-blob] 출력에 blob deref 키 존재")
    src = Path(os.path.abspath(__file__)).read_text(encoding="utf-8", errors="replace")
    _blob_true_needle = "include_blob=" + "True"  # 조립 — 소스에 리터럴 자기참조 회피
    check(_blob_true_needle not in src, "[no-blob] B code path 에 include_blob True 존재")

    # ═══ AC-6 + idempotency 2축 (§8.6/§11.6 — strip-set = CODE CONSTANT, X⊆X tautology 회피) ═══
    import shutil
    tmpdir = tempfile.mkdtemp(prefix="devproc-agg-selftest-")
    try:
        snaps = aggregate_rows(ct_rows, m0_stats, spawn_rows=[],
                               generated_at_kst="2026-07-15T19:00:00+09:00")
        snap = snaps["cycletime"]
        # run1 write
        _, hist_path, ap1 = _write_kpi_dual(tmpdir, "cycletime", snap)
        check(ap1 is True, "[AC-6] run1 history append 아님")
        hist_after_1 = Path(hist_path).read_bytes()
        snap_path = os.path.join(tmpdir, "dev-process-cycletime-snapshot.json")
        raw1 = Path(snap_path).read_bytes()

        # run2 SAME input, DIFFERENT generated_at_kst (axis-2 를 non-vacuous 로 강제)
        snap2 = aggregate_rows(ct_rows, m0_stats, spawn_rows=[],
                               generated_at_kst="2026-07-15T20:00:00+09:00")["cycletime"]
        _, _, ap2 = _write_kpi_dual(tmpdir, "cycletime", snap2)
        check(ap2 is False, "[AC-6/idem] run2 history +0 아님 (dedup 실패)")  # history +0
        hist_after_2 = Path(hist_path).read_bytes()
        check(hist_after_1 == hist_after_2, "[AC-6] history prefix byte 불변 아님 (append-only 위반)")
        raw2 = Path(snap_path).read_bytes()

        # axis-1: generated_at_kst strip 후 snapshot byte-identical
        d1 = json.loads(raw1.decode("utf-8"))
        d2 = json.loads(raw2.decode("utf-8"))
        stripped1 = json.dumps({k: v for k, v in d1.items() if k not in _IDENTITY_STRIP_KEYS},
                               sort_keys=True, ensure_ascii=False)
        stripped2 = json.dumps({k: v for k, v in d2.items() if k not in _IDENTITY_STRIP_KEYS},
                               sort_keys=True, ensure_ascii=False)
        check(stripped1 == stripped2, "[idem-axis1] strip 후 byte-identical 아님")
        # axis-2: strip 전 diff 필드 == 사전-고정 {generated_at_kst} (그 외 필드 변하면 FAIL)
        diff_keys = {k for k in set(d1) | set(d2) if d1.get(k) != d2.get(k)}
        check(diff_keys == set(_IDENTITY_STRIP_KEYS),
              "[idem-axis2] diff 필드 %s != {generated_at_kst} (다른 필드 run-간 변동)" % diff_keys)
        # measured_at content-derived pin — same-input 재실행 불변
        check(d1["measured_at"] == d2["measured_at"] == "2026-07-15T10:00:40Z",
              "[idem] measured_at content-derived pin 불변 아님")

        # changed input → history +1 + measured_at 반영
        snap3 = aggregate_rows(ct_rows + [
            _mk_row("lane_transition", "SZ", "구현", "z1", "2026-07-17T10:00:00Z"),
            _mk_row("verdict", "SZ", "구현", "z2", "2026-07-17T10:00:09Z"),
        ], m0_stats, spawn_rows=[], generated_at_kst="2026-07-15T21:00:00+09:00")["cycletime"]
        _, _, ap3 = _write_kpi_dual(tmpdir, "cycletime", snap3)
        check(ap3 is True, "[idem] changed input → history +1 아님")
        check(snap3["measured_at"] == "2026-07-17T10:00:09Z", "[idem] changed measured_at 반영 아님")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    # ═══ AC-23: per-story 기본 vs cross-story = §D-9(pattern) 만 ═══
    # 지표①-④ = per-group(story×lane) — cross-story union 안 함. trend pattern = §D-9(uncomputable).
    multi_story = compute_defect_attribution([
        _mk_row("defect_finding", "SX", "구현", "x1", "2026-07-15T10:00:00Z",
                defect_id="p1", defect_family="correctness", defect_type="logic",
                detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk_row("defect_finding", "SY", "구현", "x2", "2026-07-15T10:00:00Z",
                defect_id="p2", defect_family="correctness", defect_type="logic",
                detecting_lane="설계-리뷰", time_to_detection="1"),
    ], zero_stats)
    # 동일 (detecting_lane|family|type) 이나 story 무관 count = 2 (attribution 은 detecting-lane 축)
    check(multi_story["attribution_counts"].get("설계-리뷰|correctness|logic") == 2,
          "[AC-23] attribution cross-story count 오류")

    if failures:
        print("[aggregate_dev_process_event --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[aggregate_dev_process_event --self-test] PASS "
        "(parse-utc-z no-KST-skew; AC-7 anchor-priority 45s/3-closed; AC-8 open-only; "
        "AC-9 attempt3/iter1; AC-10 null-fix-id; AC-11 non_ambient/denom 1/2; "
        "AC-12 capture_subject lane/gate/undetermined 1/1/1; AC-13 shc 2/1 advisory; "
        "AC-14 recur1 4-tuple; AC-15 self-ref1/missing1; AC-16 no-forecast; AC-17 no-action; "
        "AC-19 pattern uncomputable-DEFAULT; AC-21 class-weighted probe != flat-sum, 1h honest-null; "
        "AC-22 3-gap flags/no-capture-fix/honest-null; AC-5 measured-0≠dormant; AC-4 stats-propagation; "
        "no-blob-deref; AC-6 append-only; idem-2axis(strip=CODE-CONST); AC-23 per-story)"
    )
    return 0


# ─────────────────────── CLI ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="dev-process-event 지표 aggregate — tier [measurement] (CFP-2688 Phase 2, B lane)"
    )
    p.add_argument("--ledger", default=None,
                   help="dev-process-event.jsonl 경로 (default: <repo>/.claude/ledger/…)")
    p.add_argument("--spawn-ledger", default=None,
                   help="spawn-event.jsonl 경로 (default: replay reader 규칙)")
    p.add_argument("--kpi-dir", default=None, help="KPI 산출 디렉터리 (default: <repo>/docs/kpi)")
    p.add_argument("--since", default=None, help="window 시작 (ISO 8601 UTC Z)")
    p.add_argument("--until", default=None, help="window 종료 (ISO 8601 UTC Z)")
    p.add_argument("--no-write", action="store_true", help="KPI 파일 write 없이 render 만")
    p.add_argument("--json", action="store_true", help="summary JSON emit")
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    args = p.parse_args()

    if args.self_test:
        return _self_test()

    ledger = args.ledger
    if ledger is None:
        ledger = os.path.join(_REPO_ROOT, ".claude", "ledger", "dev-process-event.jsonl")

    summary = aggregate_file(
        ledger_path=ledger, kpi_dir=args.kpi_dir, since=args.since, until=args.until,
        write=not args.no_write, spawn_ledger_path=args.spawn_ledger,
    )
    if args.json:
        printable = {k: v for k, v in summary.items() if k != "snapshots"}
        print(json.dumps(printable, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(render(summary))
    # non-blocking advisory — 항상 exit 0 (record-only 측정 채널)
    return 0


if __name__ == "__main__":
    sys.exit(main())
