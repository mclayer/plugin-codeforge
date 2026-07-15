# -*- coding: utf-8 -*-
"""tests/unit/test_dev_process_aggregate.py

CFP-2688 Phase 2 (구현) — Epic #2686 Story B / ADR-156 (dev-process metric aggregation).

AC-1~AC-23 zero-drop 매핑 anchor (ac-traceability-matrix Hop3 ast-resolvable symbol).
각 test 는 `scripts/lib/aggregate_dev_process_event.py` 의 pure `compute_*(rows, stats)` /
orchestrator / `_write_kpi_dual` 를 **직접 호출**해 해당 AC invariant 를 composition-derived
expected 로 assert 한다(embedded `_self_test` 26-case 로직을 Python test surface 로 노출 —
hollow 금지, discriminating: mutation → RED). 기존 shell/embedded self-test 와 병행(대체 아님).

RTM(SSOT): docs/change-plans/2026-07-15-cfp-2688-dev-process-metrics.md §8.1.1 +
           Story CFP-2688 §7.4.1 (AC ↔ 명명 테스트 백틱 심볼).
설계 SSOT = Change Plan §3/§4/§7.4/§8.6/§11.6. B = 측정·집계 ONLY (INV-B1~B6).
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# scripts/lib 를 import path 에 주입 (aggregator + sibling query/pricing 모듈 resolve)
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_LIB = _REPO_ROOT / "scripts" / "lib"
if str(_SCRIPTS_LIB) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_LIB))

import aggregate_dev_process_event as agg  # noqa: E402  (B 집계 SUT)

_ZERO_STATS = {"rows_total": 0, "rows_deduped": 0, "duplicates_collapsed": 0,
               "honesty_note": "test-stats"}

_MODULE_SRC = Path(agg.__file__).read_text(encoding="utf-8", errors="replace")


def _mk(*args, **kwargs):
    """aggregator 의 18-field fixture helper 재사용 (composition-derived)."""
    return agg._mk_row(*args, **kwargs)


# ─────────────────────────── AC-1 (normative, P1) ────────────────────────────
def test_ac1_scope_aggregation_only_no_verdict_no_substrate_rebuild():
    """B scope = A read-only 소비 위 집계 ONLY — A substrate 재구축·C verdict(PASS/FAIL) 미포함.

    (a) 모듈은 A writer(append/emit) 를 import 하지 않고 query port(read) 만 소비(INV-B1).
    (b) 집계 산출물 어디에도 verdict/PASS/FAIL 판정 key 부재(B ⊥ C, INV-B3).
    """
    # (a) A substrate 재구축 진입점 부재 — writer/emit import 0, query port read 만.
    assert "from query_dev_process_event import query_with_stats" in _MODULE_SRC
    assert "import append_dev_process_event" not in _MODULE_SRC
    assert "import emit_dev_process_event" not in _MODULE_SRC
    # (b) verdict/판정 산출 부재 (B = 측정 tier, C = PASS/FAIL 판정)
    #     주의: cycletime end_anchor_kind_counts 의 'verdict' 는 종료-앵커 종류 counter(측정치)일 뿐 —
    #     C-lane PASS/FAIL 판정 아님. 따라서 판정 ACTION/verdict 결정 토큰만 정밀 차단한다.
    snaps = agg.aggregate_rows(
        [_mk("lane_transition", "S", "구현", "e1", "2026-07-15T10:00:00Z")],
        _ZERO_STATS, spawn_rows=[],
    )
    blob = json.dumps(snaps, ensure_ascii=False)
    for decision_token in ('"pass_fail"', '"gate_result"', '"escalate_user"',
                           '"adr_draft_emitted"', '"blocked":'):
        assert decision_token not in blob, "B 산출물에 verdict/판정 ACTION 토큰 등장 (INV-B3 위반)"
    # tier = [measurement] (verdict tier 아님 — measured-0 ≠ dormant 정직)
    assert any("measurement" in t for t in snaps["cycletime"]["tier_honesty"])


# ─────────────────────────── AC-2 (normative, P1) ────────────────────────────
def test_ac2_six_metric_families_defined():
    """6 지표 계열(cycletime/fixloop/defect-attribution/selfref-recurrence/trend/token-cost) 정의.

    각 산식 = pure `compute_*` fn 로 존재하고 orchestrator 가 6 metric snapshot 을 산출한다.
    """
    expected = ("cycletime", "fixloop", "defect-attribution",
                "selfref-recurrence", "trend", "token-cost")
    assert agg._METRIC_NAMES == expected
    for fn in (agg.compute_cycletime, agg.compute_fixloop, agg.compute_defect_attribution,
               agg.compute_selfref_recurrence, agg.compute_trend, agg.compute_token_cost):
        assert callable(fn)
    snaps = agg.aggregate_rows([], _ZERO_STATS, spawn_rows=[])
    assert set(snaps.keys()) == set(expected)
    for name in expected:
        assert snaps[name]["metric"] == name
        assert "overall" in snaps[name]


# ─────────────────────────── AC-3 (normative, P1) ────────────────────────────
def test_ac3_input_path_port_only_read_pure_compute():
    """B 입력 경로 = read-only query port 한정 — ledger 구조 변경·verdict·spawn capture 수정 무배선.

    compute_* = pure fn (부작용 0): 동일 입력 2회 호출이 동일 dict + 입력 rows mutate 0.
    """
    # A read = query port 단독 (Path B 원장 직접 파싱 reject — INV-B1)
    assert "query_with_stats(" in _MODULE_SRC
    # spawn capture 수정(write) 경로 부재 — B 는 spawn 을 read(replay reader)만
    assert "no_capture_fix" in _MODULE_SRC
    rows = [_mk("defect_finding", "S", "구현-리뷰", "p1", "2026-07-15T10:00:00Z",
                defect_id="d", defect_family="correctness", defect_type="logic",
                detecting_lane="설계-리뷰", time_to_detection="1")]
    snapshot_before = json.dumps(rows, ensure_ascii=False)
    out1 = agg.compute_defect_attribution(rows, _ZERO_STATS)
    out2 = agg.compute_defect_attribution(rows, _ZERO_STATS)
    assert out1 == out2, "compute_* 순수성 위반 (동일 입력 → 상이 출력)"
    assert json.dumps(rows, ensure_ascii=False) == snapshot_before, "compute_* 가 입력 rows 를 mutate"


# ─────────────────────────── AC-4 (normative, P2) ────────────────────────────
def test_ac4_stats_propagation_no_exact_count():
    """query_with_stats 관측치(rows_total/deduped/duplicates_collapsed) 전파 + exact-count wording 부재."""
    stats = {"rows_total": 5, "rows_deduped": 5, "duplicates_collapsed": 0,
             "honesty_note": "exact-count/guaranteed-unique 아님(port)"}
    ct_rows = [
        _mk("lane_transition", "S1", "설계", "c1", "2026-07-15T10:00:00Z"),
        _mk("lane_transition", "S1", "설계-리뷰", "c2", "2026-07-15T10:00:10Z"),
    ]
    snaps = agg.aggregate_rows(ct_rows, stats, spawn_rows=[])
    for name in agg._METRIC_NAMES:
        note = snaps[name]["stats"]["honesty_note"]
        assert note is not None and "아님" in note, "%s stats.honesty_note 전파 실패" % name
    blob = json.dumps(snaps, ensure_ascii=False)
    for claim in agg._FORBIDDEN_POSITIVE_CLAIMS:
        assert claim not in blob, "금지 positive-claim 등장: %s" % claim


# ─────────────────────────── AC-5 (normative, P2) ────────────────────────────
def test_ac5_measured_zero_not_dormant():
    """dormant(row 0) → status:pending + measured_at:null / measured-0(row present, count 0) → measured.

    "측정된 0" 과 "미측정" 을 stats 로 구분 (measured-0 위장 금지).
    """
    # dormant — 집계 포함 row 0
    dormant = agg.aggregate_rows([], _ZERO_STATS, spawn_rows=[])
    for name in agg._METRIC_NAMES:
        assert dormant[name]["status"] == "pending"
        assert dormant[name]["measured_at"] is None
    # measured-0 — row present 이나 cycletime interval count 0
    m0_rows = [_mk("prompt_input", "SM", "구현", "m1", "2026-07-15T10:00:00Z")]
    m0_stats = {"rows_total": 1, "rows_deduped": 1, "duplicates_collapsed": 0, "honesty_note": "x"}
    m0 = agg.aggregate_rows(m0_rows, m0_stats, spawn_rows=[])
    assert m0["cycletime"]["status"] == "measured"
    assert m0["cycletime"]["measured_at"] == "2026-07-15T10:00:00Z"
    assert m0["cycletime"]["overall"]["interval_count"] == 0


# ─────────────────────────── AC-6 (normative, P2) ────────────────────────────
def test_ac6_history_append_only_byte_invariant():
    """dual-file KPI — history.jsonl append-only(기존 prefix byte 불변) + snapshot.json overwrite.

    same input 재실행(diff generated_at_kst) → history +0(content-hash dedup) / prefix byte 불변.
    """
    ct_rows = [
        _mk("lane_transition", "S1", "설계", "c1", "2026-07-15T10:00:00Z"),
        _mk("lane_transition", "S1", "설계-리뷰", "c2", "2026-07-15T10:00:10Z"),
        _mk("final_artifact", "S1", "설계-리뷰", "c3", "2026-07-15T10:00:40Z"),
    ]
    m0_stats = {"rows_total": 3, "rows_deduped": 3, "duplicates_collapsed": 0, "honesty_note": "x"}
    tmpdir = tempfile.mkdtemp(prefix="devproc-agg-ac6-")
    try:
        snap1 = agg.aggregate_rows(ct_rows, m0_stats, spawn_rows=[],
                                   generated_at_kst="2026-07-15T19:00:00+09:00")["cycletime"]
        snap_path, hist_path, ap1 = agg._write_kpi_dual(tmpdir, "cycletime", snap1)
        assert ap1 is True
        assert os.path.exists(snap_path)
        hist_after_1 = Path(hist_path).read_bytes()
        snap2 = agg.aggregate_rows(ct_rows, m0_stats, spawn_rows=[],
                                   generated_at_kst="2026-07-15T20:00:00+09:00")["cycletime"]
        _, _, ap2 = agg._write_kpi_dual(tmpdir, "cycletime", snap2)
        assert ap2 is False, "same input 재실행 history +0 아님 (content-hash dedup 실패)"
        assert Path(hist_path).read_bytes() == hist_after_1, "history prefix byte 변동 (append-only 위반)"
        # changed input → history +1
        snap3 = agg.aggregate_rows(ct_rows + [
            _mk("lane_transition", "SZ", "구현", "z1", "2026-07-17T10:00:00Z"),
            _mk("verdict", "SZ", "구현", "z2", "2026-07-17T10:00:09Z"),
        ], m0_stats, spawn_rows=[], generated_at_kst="2026-07-15T21:00:00+09:00")["cycletime"]
        _, _, ap3 = agg._write_kpi_dual(tmpdir, "cycletime", snap3)
        assert ap3 is True, "changed input → history +1 아님"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ─────────────────────────── AC-7 (normative, P2) ────────────────────────────
def test_ac7_cycletime_residency_anchor_priority():
    """lane 사이클타임 = lane residency + 종료 앵커 우선순위(next-different-lane > final_artifact > verdict).

    라벨 = "lane residency" (NOT time-to-PASS — 6-point subtype 부재). 재진입 = 별 구간.
    """
    ct_rows = [
        _mk("lane_transition", "S1", "설계", "c1", "2026-07-15T10:00:00Z"),
        _mk("lane_transition", "S1", "설계-리뷰", "c2", "2026-07-15T10:00:10Z"),   # next-different-lane 10s
        _mk("final_artifact", "S1", "설계-리뷰", "c3", "2026-07-15T10:00:40Z"),     # final 30s
        _mk("lane_transition", "S2", "구현", "c4", "2026-07-15T10:00:00Z"),
        _mk("verdict", "S2", "구현", "c5", "2026-07-15T10:00:05Z"),                 # verdict 5s
    ]
    ct = agg.compute_cycletime(ct_rows, _ZERO_STATS)
    assert ct["closed_interval_count"] == 3
    assert ct["residency_seconds"]["sum_seconds"] == 45.0
    assert ct["end_anchor_kind_counts"] == {"next_different_lane": 1, "final_artifact": 1, "verdict": 1}
    assert ct["label"] == "lane residency"
    # metamorphic — +1 closed interval → closed delta 1 (하드코딩 방어)
    ct_plus = agg.compute_cycletime(ct_rows + [
        _mk("lane_transition", "S5", "구현", "c6", "2026-07-15T10:00:00Z"),
        _mk("verdict", "S5", "구현", "c7", "2026-07-15T10:00:07Z"),
    ], _ZERO_STATS)
    assert ct_plus["closed_interval_count"] - ct["closed_interval_count"] == 1


# ─────────────────────────── AC-8 (declared, P2) ─────────────────────────────
def test_ac8_open_interval_only_no_duration():
    """종료 앵커 부재 진입 → open_interval_count 만 반영, duration 집계 미포함."""
    ct_open = agg.compute_cycletime(
        [_mk("lane_transition", "S3", "배포", "o1", "2026-07-15T10:00:00Z")], _ZERO_STATS)
    assert ct_open["open_interval_count"] == 1
    assert ct_open["closed_interval_count"] == 0
    assert ct_open["residency_seconds"]["count"] == 0


# ─────────────────────────── AC-9 (normative, P2) ────────────────────────────
def test_ac9_fix_attempt_ge_iteration():
    """fix_attempt_count(distinct fix_id) 와 fix_iteration_count(§10 재진입) 분리 — attempt ≥ iteration.

    1 iteration(fix_transition 1) 이 다수 fix_id(3) 로 매핑 → 과대집계(iteration=3) 회피.
    """
    fx_rows = [
        _mk("fix_transition", "S6", "구현-리뷰", "f1", "2026-07-15T10:00:00Z", fix_id="FIXA"),
        _mk("defect_finding", "S6", "구현-리뷰", "f2", "2026-07-15T10:00:01Z",
            fix_id="FIXB", defect_id="d1", defect_family="correctness", defect_type="logic"),
        _mk("defect_finding", "S6", "구현-리뷰", "f3", "2026-07-15T10:00:02Z",
            fix_id="FIXC", defect_id="d2", defect_family="correctness", defect_type="logic"),
    ]
    fx = agg.compute_fixloop(fx_rows, _ZERO_STATS)
    g6 = fx["by_group"]["S6::구현-리뷰"]
    assert g6["fix_attempt_count"] == 3
    assert g6["fix_iteration_count"] == 1
    assert fx["attempt_ge_iteration_observed"] is True
    # 라벨이 attempt 를 iteration 으로 단일 표기하지 않음
    assert "distinct" in fx["label_attempt"] and "re-entry" in fx["label_iteration"]


# ─────────────────────────── AC-10 (declared, P2) ────────────────────────────
def test_ac10_null_fix_id_missing_rows():
    """fix_id=null fix_transition → fix_attempt_count 제외 + fix_id_missing_rows 별도 기록."""
    fx_null = agg.compute_fixloop(
        [_mk("fix_transition", "S7", "구현", "fn1", "2026-07-15T10:00:00Z", fix_id=None)], _ZERO_STATS)
    assert fx_null["fix_id_missing_rows"] == 1
    assert fx_null["total_fix_attempt_count"] == 0


# ─────────────────────────── AC-11 (normative, P2) ───────────────────────────
def test_ac11_defect_attribution_non_ambient_split():
    """결점귀속 = detecting_lane×family×type + lane_label='없음'(NON-ambient) → 분모 제외."""
    da_rows = [
        _mk("defect_finding", "S8", "구현", "a1", "2026-07-15T10:00:00Z",
            defect_id="da1", defect_family="design-boundary", defect_type="coupling",
            detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk("defect_finding", "S8", "없음", "a2", "2026-07-15T10:00:01Z",
            defect_id="da2", defect_family="process-discipline", defect_type="gate",
            detecting_lane="구현-테스트", time_to_detection="unattributed"),
        _mk("defect_finding", "S8", "구현", "a3", "2026-07-15T10:00:02Z",
            defect_id="da3", defect_family="correctness", defect_type="logic",
            detecting_lane="unmapped-lane-x", time_to_detection="2"),
    ]
    da = agg.compute_defect_attribution(da_rows, _ZERO_STATS)
    assert da["non_ambient_defect_rows"] == 1
    assert da["review_lane_denominator"] == 2
    assert len(da["attribution_counts"]) == 3


# ─────────────────────────── AC-12 (normative, P1+P2) ────────────────────────
def test_ac12_capture_subject_three_branch():
    """capture-subject 축 {lane, gate, undetermined} — 미매핑 detecting_lane → undetermined(honest-degrade)."""
    assert agg._capture_subject("설계-리뷰") == "lane"
    assert agg._capture_subject("구현-테스트") == "gate"
    assert agg._capture_subject("unmapped-lane-x") == "undetermined"
    da_rows = [
        _mk("defect_finding", "S8", "구현", "a1", "2026-07-15T10:00:00Z",
            defect_id="da1", defect_family="design-boundary", defect_type="coupling",
            detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk("defect_finding", "S8", "없음", "a2", "2026-07-15T10:00:01Z",
            defect_id="da2", defect_family="process-discipline", defect_type="gate",
            detecting_lane="구현-테스트", time_to_detection="unattributed"),
        _mk("defect_finding", "S8", "구현", "a3", "2026-07-15T10:00:02Z",
            defect_id="da3", defect_family="correctness", defect_type="logic",
            detecting_lane="unmapped-lane-x", time_to_detection="2"),
    ]
    da = agg.compute_defect_attribution(da_rows, _ZERO_STATS)
    assert da["capture_subject_counts"] == {"lane": 1, "gate": 1, "undetermined": 1}


# ─────────────────────────── AC-13 (normative, P2) ───────────────────────────
def test_ac13_should_have_caught_advisory_unattributed():
    """should-have-caught = advisory heuristic — time_to_detection='unattributed' → uncomputable."""
    da_rows = [
        _mk("defect_finding", "S8", "구현", "a1", "2026-07-15T10:00:00Z",
            defect_id="da1", defect_family="design-boundary", defect_type="coupling",
            detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk("defect_finding", "S8", "없음", "a2", "2026-07-15T10:00:01Z",
            defect_id="da2", defect_family="process-discipline", defect_type="gate",
            detecting_lane="구현-테스트", time_to_detection="unattributed"),
        _mk("defect_finding", "S8", "구현", "a3", "2026-07-15T10:00:02Z",
            defect_id="da3", defect_family="correctness", defect_type="logic",
            detecting_lane="설계-리뷰", time_to_detection="2"),
    ]
    da = agg.compute_defect_attribution(da_rows, _ZERO_STATS)
    shc = da["should_have_caught"]
    assert shc["computable_count"] == 2
    assert shc["unattributed_uncomputable_count"] == 1
    assert "advisory" in shc["label"]


# ─────────────────────────── AC-14 (normative, P2) ───────────────────────────
def test_ac14_recurrence_four_tuple_not_boolean():
    """self-ref 재발 = 동일 defect_id 재출현 → {family,type,ttd,detecting_lane} 4-tuple (boolean flag 단독 금지)."""
    rec_rows = [
        _mk("defect_finding", "S9", "구현-리뷰", "r1", "2026-07-15T10:00:00Z",
            defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
            detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk("defect_finding", "S9", "구현-리뷰", "r2", "2026-07-15T11:00:00Z",
            defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
            detecting_lane="설계-리뷰", time_to_detection="1"),
    ]
    rec = agg.compute_selfref_recurrence(rec_rows, _ZERO_STATS)
    assert rec["recurrence_count"] == 1
    assert rec["recurrence_profiles_4tuple"].get("doc-integrity|section|1|설계-리뷰") == 1
    # boolean recurrence flag 단독 표현 부재 (4-tuple profile 로만)
    blob = json.dumps(rec, ensure_ascii=False)
    assert '"recurrence_flag"' not in blob and '"is_recurrence"' not in blob


# ─────────────────────────── AC-15 (normative, P2) ───────────────────────────
def test_ac15_selfref_candidate_and_normalized_location_honesty():
    """재발 identity = defect_id best-effort(normalized-location 무보장) + self-ref candidate ⊥ 일반 recurrence."""
    rec_rows = [
        _mk("defect_finding", "S9", "구현-리뷰", "r1", "2026-07-15T10:00:00Z",
            defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
            detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk("defect_finding", "S9", "구현-리뷰", "r2", "2026-07-15T11:00:00Z",
            defect_id="RECUR1", defect_family="doc-integrity", defect_type="section",
            detecting_lane="설계-리뷰", time_to_detection="1"),
        _mk("defect_finding", "S9", "구현-리뷰", "r3", "2026-07-15T12:00:00Z",
            defect_id=None, defect_family="correctness", defect_type="logic",
            detecting_lane="구현-리뷰"),
    ]
    rec = agg.compute_selfref_recurrence(rec_rows, _ZERO_STATS)
    assert rec["self_ref_candidate_count"] == 1        # doc-integrity ∈ self-ref-prone
    assert rec["defect_id_missing_rows"] == 1
    assert "normalized-location" in rec["honesty_note"]


# ─────────────────────────── AC-16 (declared, P2) ────────────────────────────
def test_ac16_trend_no_forecast_negative_control():
    """추세 = bucketed observational time-series 만 (forecast/prediction/projection 필드 부재 negative control)."""
    tr_rows = [
        _mk("lane_transition", "SA", "구현", "t1", "2026-07-15T10:00:00Z"),
        _mk("lane_transition", "SB", "설계", "t2", "2026-07-16T10:00:00Z"),
    ]
    tr = agg.compute_trend(tr_rows, _ZERO_STATS)
    keys_blob = " ".join(tr.keys()).lower()
    assert not any(k in keys_blob for k in ("forecast", "predict", "projection"))
    assert len(tr["time_series"]) == 2
    assert tr["bucket_unit"] == "date_utc"


# ─────────────────────────── AC-17 (normative, P2) ───────────────────────────
def test_ac17_pattern_count_producer_no_action():
    """cross-story pattern_count = producer(count only) — escalation action(adr_draft/escalate_user) 판정 미포함."""
    tr = agg.compute_trend([
        _mk("lane_transition", "SA", "구현", "t1", "2026-07-15T10:00:00Z"),
    ], _ZERO_STATS)
    assert "pattern_count" in tr and "pattern_status" in tr
    assert "adr_draft_emitted" not in tr
    assert "escalate_user" not in tr


# ─────────────────────────── AC-18 (normative, P1) ───────────────────────────
def test_ac18_dev_domain_feed_extends_producer_only():
    """§D-9 dev-domain feed = EXTEND(producer/feeder) — escalation ACTION decider machinery 미복제(전 지표).

    B 는 pattern_count producer + eligibility 신호까지. escalation ACTION 디스패치(adr_draft_emitted/
    escalate_user) 는 PMOAgent §D-9 mandate → B 산출물 어디에도 escalation ACTION key 부재.
    N=2 threshold 재정의 verdict 미방출(frozen 재사용, producer↔decider 분리).
    """
    snaps = agg.aggregate_rows([
        _mk("lane_transition", "SA", "구현", "t1", "2026-07-15T10:00:00Z"),
        _mk("lane_transition", "SB", "설계", "t2", "2026-07-16T10:00:00Z"),
    ], _ZERO_STATS, spawn_rows=[])
    blob = json.dumps(snaps, ensure_ascii=False)
    for action_key in ("adr_draft_emitted", "escalate_user", "escalation_action"):
        assert action_key not in blob, "escalation ACTION decider machinery 복제 (EXTEND 위반): %s" % action_key
    # producer feed 필드는 존재 (trend snapshot top-level pattern_status 승격)
    assert snaps["trend"]["pattern_status"] == "uncomputable_missing_key"


# ─────────────────────────── AC-19 (declared, P2) ────────────────────────────
def test_ac19_pattern_uncomputable_missing_key_default():
    """anchor_id/root_cause_class substrate 부재 → pattern_count=null + pattern_status='uncomputable_missing_key' (DEFAULT)."""
    tr = agg.compute_trend([
        _mk("lane_transition", "SA", "구현", "t1", "2026-07-15T10:00:00Z"),
    ], _ZERO_STATS)
    assert tr["pattern_count"] is None
    assert tr["pattern_status"] == "uncomputable_missing_key"


# ─────────────────────────── AC-20 (normative, P1) ───────────────────────────
def test_ac20_token_cost_source_spawn_not_rerecord():
    """token-cost 원천 = spawn-event-v1 (dev-process-event 아님) — 5th boundary event_id JOIN 만, re-record 금지.

    (a) compute_token_cost 입력 = spawn_rows (dev-process rows 아님).
    (b) dev-process 지표 snapshot(①~⑤)에 token/cost accounting re-record 부재(INV-B2).
    (c) B 내부 spawn capture-fix row 미생성(no_capture_fix).
    """
    # (a) spawn source parameter
    import inspect
    assert list(inspect.signature(agg.compute_token_cost).parameters)[0] == "spawn_rows"
    # (b) 5th boundary — dev-process 지표에 token accounting re-record 0
    dp_snaps = agg.aggregate_rows([
        _mk("lane_transition", "S", "구현", "e1", "2026-07-15T10:00:00Z"),
    ], _ZERO_STATS, spawn_rows=[])
    for name in ("cycletime", "fixloop", "defect-attribution", "selfref-recurrence", "trend"):
        body = json.dumps(dp_snaps[name]["overall"], ensure_ascii=False).lower()
        for token_key in ("token", "cache_read", "cache_creation", "cost_usd"):
            assert token_key not in body, "%s 에 token accounting re-record (INV-B2 위반): %s" % (name, token_key)
    # (c) capture-fix 미생성 (spawn-event capture-fix = spawn-event-v1/ADR-042·043 소관)
    tc = agg.compute_token_cost([], _ZERO_STATS)
    assert tc["no_capture_fix"] is True
    # 원천 표기 = spawn-event replay reader (INV-B4)
    assert "replay_spawn_event" in _MODULE_SRC


# ─────────────────────────── AC-21 (normative, P2) ───────────────────────────
def test_ac21_token_cost_weighted_not_flat_sum():
    """token 비용 = 4 token class 가중(uncached 1× / cache_read 0.1× / 5m 1.25× / 1h 2×) — flat-sum 금지.

    cache_write_1h(2×) = spawn 단일 cache_creation·cost_usd 단일 1.25× 로 유도 불가 → honest-null.
    """
    tc_rows = [{
        "event_id": "sp1", "consumer_scope": "wrapper", "model": "claude-opus-4",
        "input_tokens": 1000, "output_tokens": 500,
        "cache_creation_input_tokens": 200, "cache_read_input_tokens": 4000,
    }]
    tc = agg.compute_token_cost(tc_rows, _ZERO_STATS)
    counts = tc["token_class_counts"]
    assert counts["uncached_input"] == 1000
    assert counts["cache_read"] == 4000
    assert counts["cache_write_5m"] == 200
    assert counts["cache_write_1h"] is None                    # honest-null (cache_ttl_split_missing)
    # 가중 weights documented (flat-sum 아님 증빙)
    assert tc["class_weights"]["cache_read"] == 0.1
    assert tc["class_weights"]["cache_write_1h"] == 2.0
    probe = tc["class_weighted_cost_probe_usd"]
    assert probe is not None
    exp_probe = round(1000 * 15.0 / 1e6 + 500 * 75.0 / 1e6
                      + 200 * (15.0 * 1.25) / 1e6 + 4000 * (15.0 * 0.1) / 1e6, 6)
    assert probe == exp_probe                                  # composition-derived (자기 계산값 self-match 아님)
    flat_sum_tokens = 1000 + 500 + 200 + 4000
    assert abs(probe - flat_sum_tokens) > 1e-9                 # flat-sum 과 상이 (가중 적용)


# ─────────────────────────── AC-22 (normative, P2) ───────────────────────────
def test_ac22_upstream_gap_flags_no_capture_fix():
    """spawn-event-v1 3-gap 미해소 → 파생 값 null + upstream_gap_flags + B 내부 capture-fix row 미생성."""
    # actuals present → per_call/cache_ttl 구조 gap present, actuals_missing 제외
    tc = agg.compute_token_cost([{
        "event_id": "sp1", "consumer_scope": "wrapper", "model": "claude-opus-4",
        "input_tokens": 1000, "output_tokens": 500,
        "cache_creation_input_tokens": 200, "cache_read_input_tokens": 4000,
    }], _ZERO_STATS)
    assert "per_call_missing" in tc["upstream_gap_flags"]
    assert "cache_ttl_split_missing" in tc["upstream_gap_flags"]
    assert "actuals_missing" not in tc["upstream_gap_flags"]
    assert tc["total_weighted_cost_usd"] is None
    assert tc["peak_context_tokens"] is None
    assert tc["no_capture_fix"] is True
    # dormant spawn → actuals_missing 추가 + 전 파생 null
    tc_dormant = agg.compute_token_cost([], _ZERO_STATS)
    assert "actuals_missing" in tc_dormant["upstream_gap_flags"]
    assert tc_dormant["class_weighted_cost_probe_usd"] is None


# ─────────────────────────── AC-23 (normative, P2) ───────────────────────────
def test_ac23_per_story_scope_cross_story_only_pattern():
    """지표①~④ 기본 범위 = 단일 story_key(per-story group) — cross-story 집계는 §D-9 pattern_count 만.

    fixloop by_group = story::lane 키(per-story 분리) / cross-story union 부재.
    """
    fx_rows = [
        _mk("fix_transition", "SA", "구현", "f1", "2026-07-15T10:00:00Z", fix_id="X1"),
        _mk("fix_transition", "SB", "구현", "f2", "2026-07-15T10:00:00Z", fix_id="X2"),
    ]
    fx = agg.compute_fixloop(fx_rows, _ZERO_STATS)
    assert "SA::구현" in fx["by_group"]
    assert "SB::구현" in fx["by_group"]
    # per-story 분리 — 두 story 가 하나의 group 으로 union 되지 않음
    assert fx["by_group"]["SA::구현"]["fix_attempt_count"] == 1
    assert fx["by_group"]["SB::구현"]["fix_attempt_count"] == 1
    # cross-story channel = trend pattern (uncomputable DEFAULT — 별 축으로만 분리)
    tr = agg.compute_trend(fx_rows, _ZERO_STATS)
    assert tr["pattern_status"] == "uncomputable_missing_key"
