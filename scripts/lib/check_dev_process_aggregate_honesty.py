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
#   I4 pattern substrate-dir   : ★CFP-2985 D-14 로 **방향 반전**. 정의역 2분할 —
#                               substrate 有(root_cause_distribution non-empty) → computable 의무
#                               (uncomputable = silent drop). substrate 無 → uncomputable_missing_key
#                               + null 이 정직-null (computable = fabricate). (AC-19)
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
#   (실 aggregate → 전 검증 GREEN) + NC1~NC10+NC4b(각 불변식을 in-memory 로 위반시킨 산출 → 대응 검증
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


# ─────────────────────── synthetic fixture (20-field dev-process row) ─────────────────

def _row(event_type, story_key, lane_label, event_id, ts,
         consumer_scope="wrapper", defect_id=None, fix_id=None,
         defect_family=None, defect_type=None, time_to_detection=None,
         detecting_lane=None, root_cause_class=None, anchor_id=None):
    return {
        "event_id": event_id, "schema_version": "dev-process-event-v1",
        "event_type": event_type, "emit_source": "agent", "timestamp_utc": ts,
        "story_key": story_key, "lane_label": lane_label, "consumer_scope": consumer_scope,
        "defect_id": defect_id, "fix_id": fix_id, "blob_ref": None,
        "redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": [],
        "defect_family": defect_family, "defect_type": defect_type,
        "time_to_detection": time_to_detection, "detecting_lane": detecting_lane,
        "root_cause_class": root_cause_class, "anchor_id": anchor_id,
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


def _trend_field(tr, key):
    """trend snapshot 에서 필드 1개 조회 — **승격분과 overall 원본을 모두 본다**.

    ★ CFP-2985 — `_build_snapshot` 은 §D-9 feed 4필드(pattern_count / pattern_status /
      anchor_id / root_cause_class)만 top-level 로 승격하고 `root_cause_distribution` ·
      `honesty_note` 는 `overall` 에만 둔다. 두 층을 구분 없이 top-level 로만 읽으면
      **정의역이 어긋난다** — 실 snapshot 에서 substrate 는 언제나 부재로 보이고,
      substrate 가 실재하게 되는 날 `pattern_status`(승격)만 computable 로 바뀌어
      I4 가 정상 산출을 fabricate 로 오판한다(born-wrong false positive).
    """
    if key in tr:
        return tr.get(key)
    return (tr.get("overall") or {}).get(key)


def check_pattern_uncomputable_default(valid_snaps, violations):
    """I4 — pattern 산출 정직성. ★CFP-2985 D-14 로 **방향 반전** (AC-19).

    반전 전 방향은 "uncomputable 이 DEFAULT 여야 정직" 이었다. 그것은 anchor_id/
    root_cause_class 가 `_ROW_KEYS` 에 **부재**하던 시절의 방향이며, D-12 로 substrate 가
    실재하는 지금 그 방향을 유지하면 **집계가 되는 것 자체가 위반**이 된다.

    반전 후 = 정의역 2분할 (negative-domain 대조군 보존 — 검출력 감소 0):
      · substrate 有(root_cause_distribution non-empty) → computable 의무.
        uncomputable 이면 **silent drop** — 관측 가능한 것을 안 냈다.
      · substrate 無(빈 분포)                          → uncomputable_missing_key + null 이 정직-null.
        computable 이면 **fabricate** — 없는 substrate 로 값을 지어냈다.
    ★ 함수명은 유지한다 — 호출자(cmd_check/_selftest)와 RTM 오라클이 이 이름으로 지목한다.
    """
    tr = valid_snaps["trend"]
    status = tr.get("pattern_status")
    count = tr.get("pattern_count")
    substrate_present = bool(_trend_field(tr, "root_cause_distribution") or {})

    if substrate_present:
        if status != "computable" or count is None:
            violations.append(
                "(I4/pattern-silent-drop) trend pattern_status=%r/pattern_count=%r — "
                "root_cause_class substrate 가 실재(root_cause_distribution non-empty)하는데 "
                "computable 이 아니다. 관측 가능한 것을 산출하지 않은 silent drop "
                "(CFP-2985 D-14 반전 후 PRIMARY 경로, AC-19)"
                % (status, count)
            )
    else:
        if status != "uncomputable_missing_key" or count is not None:
            violations.append(
                "(I4/pattern-fabricate) trend pattern_status=%r/pattern_count=%r — "
                "substrate 부재(root_cause_distribution 빈 dict)인데 uncomputable_missing_key+null 이 "
                "아니다. 없는 substrate 로 값을 fabricate (negative-domain 대조군 — 반전 전 "
                "검출력을 그대로 보존, AC-19)"
                % (status, count)
            )


def check_trend_note_matches_state(agg, valid_snaps, violations):
    """I11 — trend.honesty_note 의 substrate 서술이 실 pattern_status 와 정합 (CFP-2985).

    직전 판의 note 는 **정적 문자열**이라 substrate 가 실재하는 computable 경로에서도
    "substrate 부재 → uncomputable" 을 계속 주장했다. 산출이 자기 자신에 대해 내는 거짓이며
    본 Story 가 표적하는 계보다(ADR-181 INV-D).

    양 방향 모두 위반이다 — 한쪽만 보면 hollow:
      · computable   인데 부재 문구  → 산출을 깎아내리는 거짓(under-claim)
      · uncomputable 인데 실재 문구  → 없는 substrate 를 있다고 하는 거짓(over-claim)
    """
    tr = valid_snaps["trend"]
    status = _trend_field(tr, "pattern_status")
    note = _trend_field(tr, "honesty_note") or ""
    present_tok = agg._TREND_NOTE_SUBSTRATE_PRESENT
    absent_tok = agg._TREND_NOTE_SUBSTRATE_ABSENT
    want, unwanted = ((present_tok, absent_tok) if status == "computable"
                      else (absent_tok, present_tok))
    if want not in note:
        violations.append(
            "(I11/note-state-mismatch) trend pattern_status=%r 인데 honesty_note 에 %r 서술 부재 "
            "— 산출 상태와 문면이 어긋난다 (정적 문자열 의심, CFP-2985)" % (status, want)
        )
    if unwanted in note:
        violations.append(
            "(I11/note-state-mismatch) trend pattern_status=%r 인데 honesty_note 가 반대 상태 "
            "서술 %r 을 주장한다 — 성립하지 않는 주장 (CFP-2985)" % (status, unwanted)
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

def _unwired_invariants(run_checks_src, declared_names):
    """선언된 check_* 중 run_checks 본문에서 호출되지 않는 이름 (pure — 대조군 가능)."""
    return sorted(n for n in declared_names if (n + "(") not in run_checks_src)


def check_all_invariants_wired(violations):
    """I12 — 선언된 불변식이 전부 run_checks 에 **배선**돼 있는가 (CFP-2985).

    ★ 왜 필요한가 (firsthand): NC 대조군은 check 함수를 **직접** 호출하므로 배선을 보지 못한다.
      임의의 check_* 를 run_checks 에서 지워도 --selftest 와 shell 스위트가 전건 GREEN 이었다
      (본 Story 가 신설한 I11 뿐 아니라 선재 `check_token_honest_null` 로도 재현). 즉 "검사가
      존재하는 것" 과 "검사가 돌아가는 것" 사이에 관측 채널이 없었다.

    ★ 정직 천장: 이것은 **소스 구조 검사**이지 동작 검사가 아니다. "선언됐는데 호출 0" class 만
      잡는다. 호출은 하되 인자를 틀리게 주거나 결과를 버리는 class 는 못 잡는다 — over-claim 금지.
    """
    import inspect
    declared = [n for n, o in globals().items()
                if n.startswith("check_") and inspect.isfunction(o)
                and n != "check_all_invariants_wired"]
    missing = _unwired_invariants(inspect.getsource(run_checks), declared)
    if missing:
        violations.append(
            "(I12/unwired-invariant) 선언됐지만 run_checks 에 배선되지 않은 불변식: %s "
            "— 검사가 존재하는 것과 돌아가는 것은 다르다 (CFP-2985)" % ", ".join(missing)
        )


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
    check_trend_note_matches_state(agg, valid_snaps, violations)
    check_token_honest_null(valid_snaps, violations)
    check_no_blob_deref(all_blob, violations)
    check_cycletime_label(valid_snaps, violations)
    check_no_escalation_action(valid_snaps, violations)
    check_strip_set_constant_and_idempotent(agg, violations)
    check_order_preserving_negative_duration(agg, violations)
    check_all_invariants_wired(violations)
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
          "I3 stats-propagation / I4 pattern-substrate-directional / I5 token-honest-null / "
          "I6 no-blob-deref / I7 cycletime='lane residency' / I8 no-escalation-action / "
          "I9 strip-set=CODE-CONST(2-run 유일 diff) / I10 order-preserving negative_duration>0. "
          "★execution-backed(실 port round-trip, mock-seam 아님) — presence-grep false-oracle 아님.")
    return 0


# ─────────────────────── --selftest (discriminating negative-control) ─────────────────

def _selftest(_args):
    """positive control(실 aggregate → GREEN) + NC1~NC10+NC4b(각 불변식 위반 산출 → 대응 검증 RED).

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
    results.append(("NC4 (substrate 無인데 computable 위조 → I4 RED / fabricate)", True, v))

    # ── NC4b: ★CFP-2985 D-14 반전으로 생긴 **신 방향** 대조군 —
    #    substrate 가 실재하는데 uncomputable 이면 silent drop 이다.
    #    이 대조군이 없으면 반전된 분기가 무검증으로 남는다(hollow).
    q_mut = copy.deepcopy(bundle["valid"])
    q_mut["trend"]["overall"]["root_cause_distribution"] = {"설계": 2}
    v = []
    check_pattern_uncomputable_default(q_mut, v)
    results.append(("NC4b (substrate 有인데 uncomputable → I4 RED / silent drop)", True, v))

    # ── NC11a/NC11b: ★CFP-2985 — honesty_note 가 실 상태에서 유도되는지 **양 방향** 대조군.
    #    한쪽만 두면 hollow 다: 정적 문자열은 한 방향에서는 우연히 맞기 때문이다.
    #    (분기 자체의 실증은 실 compute_trend 를 substrate 有/無 rows 로 각각 돌리는 아래 pair)
    st_probe = {"rows_total": 2, "rows_deduped": 2, "duplicates_collapsed": 0,
                "honesty_note": "probe"}
    rows_absent = [{"timestamp_utc": "2026-08-19T01:00:00Z", "event_type": "e", "story_key": "S1"}]
    rows_present = [
        {"timestamp_utc": "2026-08-19T01:00:00Z", "event_type": "e", "story_key": "S1",
         "anchor_id": "A", "root_cause_class": "설계"},
        {"timestamp_utc": "2026-08-19T02:00:00Z", "event_type": "e", "story_key": "S2",
         "anchor_id": "A", "root_cause_class": "설계"},
    ]
    # NC11a — substrate 無 산출에 substrate-有 서술을 주입 → I11 RED (over-claim 방향)
    a_mut = copy.deepcopy(bundle["valid"])
    a_mut["trend"] = agg.compute_trend(rows_absent, st_probe)
    a_mut["trend"]["honesty_note"] = a_mut["trend"]["honesty_note"].replace(
        agg._TREND_NOTE_SUBSTRATE_ABSENT, agg._TREND_NOTE_SUBSTRATE_PRESENT)
    v = []
    check_trend_note_matches_state(agg, a_mut, v)
    results.append(("NC11a (substrate 無인데 실재 서술 → I11 RED / over-claim)", True, v))

    # NC11b — substrate 有 산출에 substrate-無 서술을 주입 → I11 RED (under-claim 방향)
    b_mut = copy.deepcopy(bundle["valid"])
    b_mut["trend"] = agg.compute_trend(rows_present, st_probe)
    b_mut["trend"]["honesty_note"] = b_mut["trend"]["honesty_note"].replace(
        agg._TREND_NOTE_SUBSTRATE_PRESENT, agg._TREND_NOTE_SUBSTRATE_ABSENT)
    v = []
    check_trend_note_matches_state(agg, b_mut, v)
    results.append(("NC11b (substrate 有인데 부재 서술 → I11 RED / under-claim)", True, v))

    # POSITIVE-11 — 손대지 않은 실 산출 양 분기는 GREEN 이어야 한다 (항진 아님을 여기서 막는다)
    for tag, rr, expect_status in (("無", rows_absent, "uncomputable_missing_key"),
                                   ("有", rows_present, "computable")):
        p_snap = copy.deepcopy(bundle["valid"])
        p_snap["trend"] = agg.compute_trend(rr, st_probe)
        v = []
        if p_snap["trend"].get("pattern_status") != expect_status:
            v.append("(setup) substrate %s 인데 pattern_status=%r (기대 %r)"
                     % (tag, p_snap["trend"].get("pattern_status"), expect_status))
        check_trend_note_matches_state(agg, p_snap, v)
        results.append(("POSITIVE-11%s (substrate %s 실 산출 → I11 GREEN)"
                        % ("a" if tag == "無" else "b", tag), False, v))

    # ── NC12: ★CFP-2985 — 배선 검사(I12) 자체의 대조군. pure fn 이라 소스 텍스트로 통제한다.
    v = []
    if _unwired_invariants("check_a(x)\n", ["check_a", "check_b"]) != ["check_b"]:
        pass  # 미검출 = 아래 append 없음 → 대조군이 GREEN 으로 떨어져 FAIL 표시된다
    else:
        v.append("(I12/unwired-invariant) 배선 누락 검출: check_b")
    results.append(("NC12 (run_checks 배선 누락 → I12 RED)", True, v))
    v = []
    if _unwired_invariants("check_a(x)\ncheck_b(y)\n", ["check_a", "check_b"]):
        v.append("(setup) 전건 배선인데 누락으로 판정")
    results.append(("POSITIVE-12 (전건 배선 → I12 GREEN)", False, v))

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
        # ★ CFP-2985 — 요약 문면을 **실 results 에서 유도**한다. 직전 판은 negative-control
        #   명부를 정적 리터럴("NC1~NC10+NC4b")로 적었고, 그래서 대조군을 목록에서 빼도
        #   요약은 그 이름을 계속 주장했다(firsthand mutant: NC4b 등재 제거 → 행은 사라지는데
        #   요약 문자열은 불변). 성립하지 않는 주장을 문면에 남기지 않는다.
        nc_roster = [label.split(" ", 1)[0] for label, expect_red, _ in results if expect_red]
        print("[check-dev-process-aggregate-honesty --selftest] PASS — positive GREEN + "
              "negative-control %d종 [%s] 전부 RED (discriminating: 각 honest-degrade 불변식이 "
              "실 값 assert 로 mutation 을 죽임 — presence-grep false-oracle 아님)."
              % (len(nc_roster), " ".join(nc_roster)))
        return 0
    print("[check-dev-process-aggregate-honesty --selftest] FAIL — 판별성 위반 (위 FAIL 행 참조).")
    return 1


def main():
    p = argparse.ArgumentParser(
        description="dev-process aggregate honest-degrade/산식-parity lint "
        "(CFP-2688 Phase 2 — execution-backed real port round-trip, §8.6)"
    )
    p.add_argument("--selftest", action="store_true",
                   help="discriminating negative-control (positive GREEN + 전 negative-control RED 증명 — 명부는 산출에서 유도)")
    args = p.parse_args()
    if args.selftest:
        return _selftest(args)
    return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main())
