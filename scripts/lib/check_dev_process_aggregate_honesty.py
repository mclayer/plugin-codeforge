#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_dev_process_aggregate_honesty.py — dev-process 지표 aggregate honest-degrade / 산식-parity lint
#
# Carrier: CFP-2688 Phase 2 (구현) — Epic #2686 Story B / ADR-156 (dev-process metric aggregation)
# SSOT: docs/change-plans/2026-07-15-cfp-2688-dev-process-metrics.md §8.6 (execution-backed lint) /
#       §3.6 INV-B5 (honest-degrade) / §4.5 AC-19 / §4.6 AC-21/22 / §11.6 (idempotency 2축)
#
# 책임 (각 검증 = execution-backed — 실 A port(query_with_stats) round-trip 후 산출 관측치 대조.
#   presence-grep-as-oracle 금지 · mock-seam 금지, CFP-2635/CFP-2545 lesson):
#   본 lint 는 aggregate_dev_process_event 의 6 지표 산출을 **실제로 실행**해(synthetic dev-process
#   ledger 를 temp 파일로 emit → REAL query_with_stats(ledger_path=…) round-trip → aggregate_rows)
#   honest-degrade 불변식을 산출 결과 위에서 assert 한다. grep 이 아니라 실 값 판정.
#
# 검사 불변식 (Change Plan §8.6 / §3.6 INV-B5 / §4):
#   I1 measured-0 ≠ dormant   : empty ledger → status=pending/measured_at=null;
#                               measured-0(row≥1, metric count 0) → status=measured/count 0 (AC-5).
#   I2 no over-claim wording   : 산출 blob 에 _FORBIDDEN_POSITIVE_CLAIMS(exact-count/guaranteed-
#                               unique/…) 등장 0 (AC-4).
#   I3 stats propagation       : 각 snapshot.stats.honesty_note 전파 present (AC-4).
#   I4 pattern uncomputable    : trend.pattern_status == 'uncomputable_missing_key' (DEFAULT) +
#                               pattern_count is None (AC-19, edge 아님).
#   I5 token honest-null       : token-cost total_weighted_cost_usd is None(actuals 有에도) +
#                               upstream_gap_flags ⊇ {per_call_missing, cache_ttl_split_missing} (AC-22).
#   I6 no blob deref keys       : 산출 blob 에 '_blob'/'_blob_deref_available' 키 0 (§7.5).
#   I7 cycletime label          : cycletime.label == 'lane residency' ∧ 'time-to-PASS' 라벨 0 (AC-7).
#   I8 no escalation action     : trend snapshot 에 adr_draft_emitted/escalate_user 필드 0 (INV-B3/AC-17).
#   I9 strip-set = code constant: _IDENTITY_STRIP_KEYS == ('generated_at_kst',) 모듈 상수 +
#                               same-input 2-run 의 유일 diff (§11.6 X⊆X tautology 회피).
#   I10 order-preserving neg-dur: reverse-order fixture → negative_duration_count>0 (ts 재정렬 금지 —
#                               clock-step 신호 소실 방지, §7.4.3).
#
# ★discriminating power (born-broken guard / false-oracle 금지): --selftest 는 positive control
#   (실 aggregate → 전 검증 GREEN) + NC1~NC10(각 불변식을 in-memory 로 위반시킨 산출 → 대응 검증
#   RED)로 판별성을 실증한다. presence-grep 이면 mutation 에도 GREEN(false-oracle) — 본 lint 는 실
#   값 assert 라 mutation 시 RED 발화(discriminating).
#
# 불변식: 0 API call, local read only(temp ledger emit 후 삭제). 3-tier exit: 0 PASS / 1 violation /
#   2 setup error. under-test aggregate 원본 무수정(READ-ONLY import).
#
# 사용:
#   python3 check_dev_process_aggregate_honesty.py            # check (real round-trip → 전 불변식)
#   python3 check_dev_process_aggregate_honesty.py --selftest # discriminating negative-control

import argparse
import copy
import json
import os
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def _import_under_test():
    """aggregate_dev_process_event(agg) + query_dev_process_event(qdp) 동적 import.

    import 실패(모듈/sibling 부재) → setup error(exit 2) — vacuous pass 금지.
    """
    import importlib
    agg = importlib.import_module("aggregate_dev_process_event")
    qdp = importlib.import_module("query_dev_process_event")
    return agg, qdp


# ─────────────────────── synthetic fixture (18-field dev-process row) ─────────────────

def _row(event_type, story_key, lane_label, event_id, ts,
         consumer_scope="wrapper", defect_id=None, fix_id=None,
         defect_family=None, defect_type=None, time_to_detection=None,
         detecting_lane=None):
    return {
        "event_id": event_id, "schema_version": "dev-process-event-v1",
        "event_type": event_type, "emit_source": "agent", "timestamp_utc": ts,
        "story_key": story_key, "lane_label": lane_label, "consumer_scope": consumer_scope,
        "defect_id": defect_id, "fix_id": fix_id, "blob_ref": None,
        "redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": [],
        "defect_family": defect_family, "defect_type": defect_type,
        "time_to_detection": time_to_detection, "detecting_lane": detecting_lane,
    }


def _valid_rows():
    """cycletime handoff + defect + recurrence 혼합 fixture (measured 산출용)."""
    return [
        _row("lane_transition", "S1", "설계", "v1", "2026-07-15T10:00:00Z"),
        _row("lane_transition", "S1", "설계-리뷰", "v2", "2026-07-15T10:00:10Z"),
        _row("final_artifact", "S1", "설계-리뷰", "v3", "2026-07-15T10:00:40Z"),
        _row("defect_finding", "S1", "구현", "v4", "2026-07-15T10:01:00Z",
             defect_id="D1", defect_family="doc-integrity", defect_type="section",
             detecting_lane="설계-리뷰", time_to_detection="1"),
        _row("defect_finding", "S1", "구현", "v5", "2026-07-15T10:02:00Z",
             defect_id="D1", defect_family="doc-integrity", defect_type="section",
             detecting_lane="설계-리뷰", time_to_detection="1"),  # 재출현
    ]


def _reverse_duration_rows():
    """clock-step(anchor.ts < entry.ts) — emission order 보존 시 negative_duration_count>0."""
    return [
        _row("lane_transition", "S9", "구현", "r1", "2026-07-15T10:00:30Z"),
        _row("final_artifact", "S9", "구현", "r2", "2026-07-15T10:00:00Z"),  # 역순 ts
    ]


def _synthetic_spawn_rows():
    """spawn-event replay row (token actuals 有) — honest-null 이 dormant 때문이 아님을 강제."""
    return [{
        "event_id": "sp1", "consumer_scope": "wrapper", "model": "claude-opus-4",
        "input_tokens": 1000, "output_tokens": 500,
        "cache_creation_input_tokens": 200, "cache_read_input_tokens": 4000,
    }]


def _write_ledger(path, rows):
    """synthetic dev-process ledger emit (newline='\\n' — Windows CRLF 회피)."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ─────────────────────── real round-trip (mock-seam 금지 — 실 A port 경유) ──────────────

def real_aggregate(agg, qdp):
    """REAL query_with_stats(ledger_path=…) round-trip → aggregate_rows. 산출 dict 묶음 반환.

    empty / measured-0 / valid 3 ledger 를 실제 temp 파일로 emit 후 port 로 read (mock 아님).
    """
    tmpdir = tempfile.mkdtemp(prefix="devproc-agg-lint-")
    try:
        empty_path = os.path.join(tmpdir, "empty.jsonl")
        m0_path = os.path.join(tmpdir, "measured0.jsonl")
        valid_path = os.path.join(tmpdir, "valid.jsonl")
        _write_ledger(empty_path, [])
        _write_ledger(m0_path, [_row("prompt_input", "SM", "구현", "m1", "2026-07-15T10:00:00Z")])
        _write_ledger(valid_path, _valid_rows())

        # ★REAL port round-trip (no mock-seam) — query_with_stats 가 실제 ledger 파일 read.
        e_rows, e_stats = qdp.query_with_stats(ledger_path=empty_path)
        m_rows, m_stats = qdp.query_with_stats(ledger_path=m0_path)
        v_rows, v_stats = qdp.query_with_stats(ledger_path=valid_path)

        spawn_rows = _synthetic_spawn_rows()
        empty_snaps = agg.aggregate_rows(e_rows, e_stats, spawn_rows=[])
        measured0_snaps = agg.aggregate_rows(m_rows, m_stats, spawn_rows=[])
        valid_snaps = agg.aggregate_rows(v_rows, v_stats, spawn_rows=spawn_rows)
        return {
            "empty": empty_snaps,
            "measured0": measured0_snaps,
            "valid": valid_snaps,
            "e_rows_n": len(e_rows), "m_rows_n": len(m_rows), "v_rows_n": len(v_rows),
        }
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def _blob(snaps):
    return json.dumps(snaps, ensure_ascii=False, sort_keys=True)


# ─────────────────────── 불변식 검증 (pure — 산출 입력, 재실행 금지) ─────────────────────

def check_measured0_not_dormant(empty_snaps, measured0_snaps, metric_names, violations):
    """I1 — empty→pending/null; measured-0(row≥1, count 0)→measured/count 0 (AC-5)."""
    for name in metric_names:
        s = empty_snaps[name]
        if not (s.get("status") == "pending" and s.get("measured_at") is None):
            violations.append(
                "(I1/measured-0≠dormant) empty ledger '%s' status=%r/measured_at=%r "
                "— pending/null 아님 (dormant 위장 금지, AC-5)"
                % (name, s.get("status"), s.get("measured_at"))
            )
    ct = measured0_snaps["cycletime"]
    if not (ct.get("status") == "measured" and ct.get("measured_at") is not None
            and ct.get("overall", {}).get("interval_count") == 0):
        violations.append(
            "(I1/measured-0≠dormant) measured-0 cycletime status=%r/measured_at=%r/interval=%r "
            "— measured+count0 아님 (측정된 0 을 dormant 로 위장, AC-5)"
            % (ct.get("status"), ct.get("measured_at"),
               ct.get("overall", {}).get("interval_count"))
        )


def check_no_overclaim(blob, forbidden_claims, violations):
    """I2 — 산출 blob 에 exact-count/guaranteed-unique positive-claim 등장 0 (AC-4)."""
    for claim in forbidden_claims:
        if claim in blob:
            violations.append(
                "(I2/over-claim) 금지 positive-claim 산출 등장: %r (exact-count/guaranteed-unique "
                "주장 금지 — port 관측치 상속, AC-4)" % claim
            )


def check_stats_propagation(snaps, metric_names, violations):
    """I3 — 각 snapshot.stats.honesty_note 전파 present (AC-4)."""
    for name in metric_names:
        note = snaps[name].get("stats", {}).get("honesty_note")
        if note is None:
            violations.append(
                "(I3/stats-propagation) '%s' snapshot.stats.honesty_note 전파 실패(None) — "
                "port 관측치 상속 서술 부재 (AC-4)" % name
            )


def check_pattern_uncomputable_default(valid_snaps, violations):
    """I4 — trend pattern_status=uncomputable_missing_key(DEFAULT) + pattern_count None (AC-19)."""
    tr = valid_snaps["trend"]
    if tr.get("pattern_status") != "uncomputable_missing_key" or tr.get("pattern_count") is not None:
        violations.append(
            "(I4/pattern-uncomputable) trend pattern_status=%r/pattern_count=%r — "
            "uncomputable_missing_key(DEFAULT)+null 아님 (anchor_id/root_cause_class substrate "
            "부재 = PRIMARY 경로, edge 아님, AC-19)"
            % (tr.get("pattern_status"), tr.get("pattern_count"))
        )


def check_token_honest_null(valid_snaps, violations):
    """I5 — token-cost total_weighted_cost_usd None(actuals 有에도) + 3-gap flags (AC-22)."""
    tc = valid_snaps["token-cost"]["overall"]
    if tc.get("total_weighted_cost_usd") is not None:
        violations.append(
            "(I5/token-honest-null) token-cost total_weighted_cost_usd=%r ≠ None — 3-gap 미해소 "
            "인데 파생 production 값 fabricate (honest-null 위반, AC-22)"
            % tc.get("total_weighted_cost_usd")
        )
    flags = set(tc.get("upstream_gap_flags") or [])
    need = {"per_call_missing", "cache_ttl_split_missing"}
    if not need <= flags:
        violations.append(
            "(I5/token-honest-null) upstream_gap_flags=%r 가 {per_call_missing, "
            "cache_ttl_split_missing} 미포함 — 구조적 3-gap 표기 누락 (AC-22)"
            % sorted(flags)
        )
    if tc.get("token_class_counts", {}).get("cache_write_1h") is not None:
        violations.append(
            "(I5/token-honest-null) cache_write_1h class = non-null — cost_usd 단일 1.25× 배수로 "
            "유도 불가(honest-null 이어야, AC-21)"
        )


def check_no_blob_deref(blob, violations):
    """I6 — 산출 blob 에 _blob/_blob_deref_available 키 0 (§7.5 include_blob=False)."""
    for needle in ("_blob_deref_available", "_blob"):
        if needle in blob:
            violations.append(
                "(I6/no-blob-deref) 산출에 blob deref 키 등장: %r — include_blob=False 위반 "
                "(index-tier-derived only emit, §7.5)" % needle
            )
            return  # _blob 은 _blob_deref_available 의 substring — 1회만 보고


def check_cycletime_label(valid_snaps, violations):
    """I7 — cycletime.label == 'lane residency' ∧ 'time-to-PASS' positive-claim 0 (AC-7).

    ★honest 부정형("time-to-PASS 아님") 은 정당 — over-claim 판정에서 제외(false-oracle 회피).
    positive 등장 = 총 등장 − 부정형 등장 > 0 (label 위조 등 정형 긍정 단정만 검출).
    """
    ct = valid_snaps["cycletime"]["overall"]
    if ct.get("label") != "lane residency":
        violations.append(
            "(I7/cycletime-label) cycletime.label=%r ≠ 'lane residency' — 6-point transition_point "
            "subtype 부재이므로 residency 라벨만 (AC-7)" % ct.get("label")
        )
    ct_blob = _blob({"x": ct})
    positive = ct_blob.count("time-to-PASS") - ct_blob.count("time-to-PASS 아님")
    if positive > 0:
        violations.append(
            "(I7/cycletime-label) cycletime 산출에 'time-to-PASS' 긍정 단정 등장(honest 부정형 제외) "
            "— coarse residency 를 time-to-PASS 로 over-claim (AC-7)"
        )


def check_no_escalation_action(valid_snaps, violations):
    """I8 — trend snapshot 에 escalation ACTION 필드 0 (B=producer, INV-B3/AC-17)."""
    tr_snap = valid_snaps["trend"]
    tr_overall = tr_snap.get("overall", {})
    for field in ("adr_draft_emitted", "escalate_user"):
        if field in tr_snap or field in tr_overall:
            violations.append(
                "(I8/no-escalation-action) trend 산출에 escalation ACTION 필드 %r 존재 — "
                "B=pattern producer, escalation dispatch=PMOAgent decider (INV-B3/AC-17)" % field
            )


def check_strip_set_constant_and_idempotent(agg, violations):
    """I9 — _IDENTITY_STRIP_KEYS 모듈 상수 + same-input 2-run 유일 diff (§11.6 X⊆X 회피)."""
    strip = getattr(agg, "_IDENTITY_STRIP_KEYS", None)
    if strip != ("generated_at_kst",):
        violations.append(
            "(I9/strip-constant) _IDENTITY_STRIP_KEYS=%r ≠ ('generated_at_kst',) — 산출서 역산 아닌 "
            "코드 상수여야 (X⊆X tautology 회피, §11.6)" % (strip,)
        )
        return
    rows = _valid_rows()
    stats = {"rows_total": len(rows), "rows_deduped": len(rows),
             "duplicates_collapsed": 0, "honesty_note": "lint"}
    snap_a = agg.aggregate_rows(rows, stats, spawn_rows=[],
                                generated_at_kst="2026-07-15T19:00:00+09:00")["cycletime"]
    snap_b = agg.aggregate_rows(rows, stats, spawn_rows=[],
                                generated_at_kst="2026-07-15T20:00:00+09:00")["cycletime"]
    diff = {k for k in set(snap_a) | set(snap_b) if snap_a.get(k) != snap_b.get(k)}
    if diff != set(strip):
        violations.append(
            "(I9/idempotency) same-input 2-run diff 필드 %s ≠ strip-set {generated_at_kst} — "
            "wall-clock 외 필드가 run 간 변동 (content-derived 위반, §11.6)" % sorted(diff)
        )


def check_order_preserving_negative_duration(agg, violations, compute_fn=None):
    """I10 — reverse-order fixture → negative_duration_count>0 (emission order 보존, §7.4.3).

    compute_fn 주입 가능(negative-control: ts-정렬 wrapper → count 0 → RED).
    """
    fn = compute_fn or agg.compute_cycletime
    stats = {"rows_total": 2, "rows_deduped": 2, "duplicates_collapsed": 0, "honesty_note": "lint"}
    out = fn(_reverse_duration_rows(), stats)
    if not (out.get("negative_duration_count", 0) > 0 and out.get("closed_interval_count") == 0):
        violations.append(
            "(I10/order-preserving) reverse-order fixture negative_duration_count=%r/closed=%r — "
            "emission order 보존 시 clock-step 이 negative_duration 으로 표면화해야 (ts 재정렬 = "
            "신호 소실, §7.4.3)"
            % (out.get("negative_duration_count"), out.get("closed_interval_count"))
        )


# ─────────────────────── check 오케스트레이션 (실 산출 위) ──────────────────────────────

def run_checks(agg, bundle):
    """실 round-trip 산출 위에서 전 불변식 검증 → violations list."""
    violations = []
    metric_names = list(agg._METRIC_NAMES)
    forbidden = tuple(agg._FORBIDDEN_POSITIVE_CLAIMS)

    empty_snaps = bundle["empty"]
    measured0_snaps = bundle["measured0"]
    valid_snaps = bundle["valid"]
    valid_blob = _blob(valid_snaps)
    all_blob = valid_blob + _blob(empty_snaps) + _blob(measured0_snaps)

    check_measured0_not_dormant(empty_snaps, measured0_snaps, metric_names, violations)
    check_no_overclaim(all_blob, forbidden, violations)
    check_stats_propagation(valid_snaps, metric_names, violations)
    check_pattern_uncomputable_default(valid_snaps, violations)
    check_token_honest_null(valid_snaps, violations)
    check_no_blob_deref(all_blob, violations)
    check_cycletime_label(valid_snaps, violations)
    check_no_escalation_action(valid_snaps, violations)
    check_strip_set_constant_and_idempotent(agg, violations)
    check_order_preserving_negative_duration(agg, violations)
    return violations


def cmd_check(_args):
    try:
        agg, qdp = _import_under_test()
    except Exception as e:  # noqa: BLE001 — import 실패 = 판정불가 setup error
        print("[check-dev-process-aggregate-honesty-setup-error] under-test import 실패: %s" % e,
              file=sys.stderr)
        return 2
    try:
        bundle = real_aggregate(agg, qdp)
    except Exception as e:  # noqa: BLE001
        print("[check-dev-process-aggregate-honesty-setup-error] real round-trip 실패: %s" % e,
              file=sys.stderr)
        return 2

    violations = run_checks(agg, bundle)

    print("[check-dev-process-aggregate-honesty] real query_with_stats round-trip: "
          "empty=%d / measured-0=%d / valid=%d rows"
          % (bundle["e_rows_n"], bundle["m_rows_n"], bundle["v_rows_n"]))
    if violations:
        for v in violations:
            print("::warning::check-dev-process-aggregate-honesty: VIOLATION — %s" % v)
        print("")
        print("check-dev-process-aggregate-honesty: %d violation — honest-degrade/산식-parity 위반 "
              "(§8.6 execution-backed, INV-B5)." % len(violations))
        return 1

    print("check-dev-process-aggregate-honesty: PASS — I1 measured-0≠dormant / I2 no-over-claim / "
          "I3 stats-propagation / I4 pattern-uncomputable-DEFAULT / I5 token-honest-null / "
          "I6 no-blob-deref / I7 cycletime='lane residency' / I8 no-escalation-action / "
          "I9 strip-set=CODE-CONST(2-run 유일 diff) / I10 order-preserving negative_duration>0. "
          "★execution-backed(실 port round-trip, mock-seam 아님) — presence-grep false-oracle 아님.")
    return 0


# ─────────────────────── --selftest (discriminating negative-control) ─────────────────

def _selftest(_args):
    """positive control(실 aggregate → GREEN) + NC1~NC10(각 불변식 위반 산출 → 대응 검증 RED).

    각 NC 는 실 산출을 in-memory 로 mutate(원본 무수정) → 대응 검증이 RED 발화함을 증명
    (presence-grep 이면 mutation 에도 GREEN = false-oracle; 실 값 assert 라 discriminating).
    """
    try:
        agg, qdp = _import_under_test()
        bundle = real_aggregate(agg, qdp)
    except Exception as e:  # noqa: BLE001
        print("[selftest-setup-error] %s" % e, file=sys.stderr)
        return 2

    metric_names = list(agg._METRIC_NAMES)
    forbidden = tuple(agg._FORBIDDEN_POSITIVE_CLAIMS)
    results = []  # (label, expect_red, violations)

    # ── POSITIVE: 실 산출 → 전 검증 GREEN ──
    results.append(("POSITIVE (real aggregate → 전 불변식 GREEN)", False, run_checks(agg, bundle)))

    # ── NC1: measured-0≠dormant — empty snapshot status 를 'measured' 로 위조 → I1 RED ──
    e_mut = copy.deepcopy(bundle["empty"])
    for name in metric_names:
        e_mut[name]["status"] = "measured"          # dormant 를 measured 로 위장
        e_mut[name]["measured_at"] = "2026-07-15T10:00:00Z"
    v = []
    check_measured0_not_dormant(e_mut, bundle["measured0"], metric_names, v)
    results.append(("NC1 (empty→measured 위조 → I1 RED)", True, v))

    # ── NC2: over-claim — blob 에 금지 positive-claim 주입 → I2 RED ──
    v = []
    check_no_overclaim(_blob(bundle["valid"]) + " guaranteed-unique count ", forbidden, v)
    results.append(("NC2 (over-claim 주입 → I2 RED)", True, v))

    # ── NC3: stats-propagation — honesty_note strip → I3 RED ──
    s_mut = copy.deepcopy(bundle["valid"])
    for name in metric_names:
        s_mut[name]["stats"]["honesty_note"] = None
    v = []
    check_stats_propagation(s_mut, metric_names, v)
    results.append(("NC3 (stats.honesty_note strip → I3 RED)", True, v))

    # ── NC4: pattern default — pattern_status=computable 위조 → I4 RED ──
    p_mut = copy.deepcopy(bundle["valid"])
    p_mut["trend"]["pattern_status"] = "computable"
    p_mut["trend"]["pattern_count"] = 5
    v = []
    check_pattern_uncomputable_default(p_mut, v)
    results.append(("NC4 (pattern computable 위조 → I4 RED)", True, v))

    # ── NC5: token honest-null — total_weighted_cost_usd fabricate → I5 RED ──
    t_mut = copy.deepcopy(bundle["valid"])
    t_mut["token-cost"]["overall"]["total_weighted_cost_usd"] = 1.23
    v = []
    check_token_honest_null(t_mut, v)
    results.append(("NC5 (token total_weighted_cost fabricate → I5 RED)", True, v))

    # ── NC6: no-blob-deref — blob 에 _blob_deref_available 주입 → I6 RED ──
    v = []
    check_no_blob_deref(_blob(bundle["valid"]) + ' "_blob_deref_available": true ', v)
    results.append(("NC6 (_blob_deref_available 주입 → I6 RED)", True, v))

    # ── NC7: cycletime label — 'time-to-PASS' 로 위조 → I7 RED ──
    c_mut = copy.deepcopy(bundle["valid"])
    c_mut["cycletime"]["overall"]["label"] = "time-to-PASS"
    v = []
    check_cycletime_label(c_mut, v)
    results.append(("NC7 (cycletime label 'time-to-PASS' 위조 → I7 RED)", True, v))

    # ── NC8: escalation action — trend 에 adr_draft_emitted 주입 → I8 RED ──
    a_mut = copy.deepcopy(bundle["valid"])
    a_mut["trend"]["adr_draft_emitted"] = True
    v = []
    check_no_escalation_action(a_mut, v)
    results.append(("NC8 (trend adr_draft_emitted 주입 → I8 RED)", True, v))

    # ── NC9: strip-set constant — strip 상수 override(빈 tuple) → I9 RED ──
    class _ShimEmptyStrip:
        _IDENTITY_STRIP_KEYS = ()
        aggregate_rows = staticmethod(agg.aggregate_rows)
    v = []
    check_strip_set_constant_and_idempotent(_ShimEmptyStrip, v)
    results.append(("NC9 (_IDENTITY_STRIP_KEYS=() override → I9 RED)", True, v))

    # ── NC10: order-preserving — ts-정렬 wrapper 주입(clock-step 신호 소실) → I10 RED ──
    def _sorting_compute(rows, stats):
        ordered = sorted(rows, key=lambda r: r.get("timestamp_utc") or "")  # 인과 순서 파괴
        return agg.compute_cycletime(ordered, stats)
    v = []
    check_order_preserving_negative_duration(agg, v, compute_fn=_sorting_compute)
    results.append(("NC10 (ts-정렬 wrapper → negative 소실 → I10 RED)", True, v))

    all_ok = True
    print("[check-dev-process-aggregate-honesty --selftest] discriminating negative-control")
    print("=" * 80)
    for label, expect_red, viols in results:
        got_red = len(viols) > 0
        ok = (got_red == expect_red)
        all_ok = all_ok and ok
        print("  [%s] %-56s → %s" % ("OK" if ok else "FAIL", label, "RED" if got_red else "GREEN"))
        for vv in viols:
            print("        · %s" % vv)
    print("=" * 80)
    if all_ok:
        print("[check-dev-process-aggregate-honesty --selftest] PASS — positive GREEN + "
              "NC1~NC10 전부 RED (discriminating: 각 honest-degrade 불변식이 실 값 assert 로 "
              "mutation 을 죽임 — presence-grep false-oracle 아님).")
        return 0
    print("[check-dev-process-aggregate-honesty --selftest] FAIL — 판별성 위반 (위 FAIL 행 참조).")
    return 1


def main():
    p = argparse.ArgumentParser(
        description="dev-process aggregate honest-degrade/산식-parity lint "
        "(CFP-2688 Phase 2 — execution-backed real port round-trip, §8.6)"
    )
    p.add_argument("--selftest", action="store_true",
                   help="discriminating negative-control (positive GREEN + NC1~NC10 RED 증명)")
    args = p.parse_args()
    if args.selftest:
        return _selftest(args)
    return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main())
