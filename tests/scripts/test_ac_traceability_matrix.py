#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_ac_traceability_matrix.py
CFP-2603 (Epic CFP-2602 G1) Phase 2 / ADR-145 §8.1 — AC-ID zero-drop 게이트의 **명명 테스트**
(RTM authoritative). 본 Story 자체가 AC-ID 규약의 첫 dogfood: Change Plan §8.1 이 명명한 9개
normative 테스트(AC-1a·AC-2..AC-9)가 여기서 **실 def**(stub 아님)로 실재해야 게이트의 자기 Phase 2 PR
이 Hop3(§8↔실 symbol, ast resolve)를 통과한다. 함수명·시그니처는 §8.1 과 1:1 정합(변경 금지).

AC-1b(declared)·AC-10(advisory)는 명명 테스트 없음 — forged machine test 금지(§5.6 RO-1 / advisory routed).

pytest 로 실행 가능(requirements.txt: pytest). 각 함수는 실제로 core/CLI 를 구동해 assert(진짜 GREEN).
subprocess fork 판정은 exit code 단독 아닌 도메인 sentinel 병행(assert_gate_fail — distinct-marker).
"""
import os
import tempfile

from _ac_matrix_fixtures import (  # 공통 helper (ADR-140)
    assert_gate_fail,
    assert_gate_nonzero,
    assert_gate_pass,
    make_tests_root,
    make_tests_root_comment_only,
    run_gate,
    write_ac_source,
    write_ac_source_countonly,
    write_ac_source_empty,
    write_rtm,
    write_rtm_notable,
    write_rtm_placeholder,
)
from ac_id import (  # SSOT leaf (Dev-A)
    AC_ID_RE,
    parse_ac_id,
    validate_ac_record,
)


def _full_record(**over):
    rec = {
        "id": "AC-1a",
        "statement": "given X when Y then Z",
        "source": "derived",
        "verification": "unit test",
        "coverage_required": ["design", "§8_test"],
        "phase": 1,
        "tier": "normative",
    }
    rec.update(over)
    return rec


# ─────────────────────────────────────────────────────────────────────────────
# AC-1a (normative) — well-formed AC-ID(sub-letter 포함) + §5.2 스키마 필드
# ─────────────────────────────────────────────────────────────────────────────
def test_ac_id_wellformed_and_schema():
    # (1) parse_ac_id — sub-letter 수용 + distinct 보존 (zero-drop CRITICAL TRAP)
    assert parse_ac_id("AC-1a") == (1, "a")
    assert parse_ac_id("AC-1b") == (1, "b")
    assert parse_ac_id("AC-1") == (1, None)
    assert parse_ac_id("AC-9") == (9, None)
    assert parse_ac_id("AC-10") == (10, None)
    # cross-Story <KEY>:AC-N (ADR-145 §결정4)
    assert parse_ac_id("CFP-2603:AC-1a") == (1, "a")
    # sub-letter 가 drop 되면 AC-1a==AC-1 로 붕괴 = zero-drop 위반 → 서로 달라야 한다
    assert parse_ac_id("AC-1a") != parse_ac_id("AC-1")
    # malformed reject
    for bad in ("AC-", "ACX-1", "AC-1A", "AC1", "AC-1ab", "", "AC-a"):
        assert parse_ac_id(bad) is None, f"{bad!r} should be rejected"
    # AC_ID_RE 자체도 SSOT 확인
    assert AC_ID_RE.match("AC-1a") and not AC_ID_RE.match("AC-1A")
    # (2) §5.2 full record → 위반 0
    assert validate_ac_record(_full_record()) == []
    # (3) 게이트 Hop1 — 표에 malformed id 면 fail-closed FAIL
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        write_ac_source(ac, [("AC-1A", "derived", "normative")])  # malformed id
        write_rtm(rtm, [("AC-1A", "normative", "test_x")])
        rc, out = run_gate(1, ac, rtm)
        assert_gate_fail(rc, out)
        # well-formed 로 고치면 PASS
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        assert_gate_pass(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-2 (normative) — Option (a) rationalized field-set (S4 / ArchitectPL gap#2):
#   required 4 {id, statement, source, tier} 누락=위반 / optional 3 {verification,
#   coverage_required, phase} 누락=OK / optional present-but-malformed=위반. 위반 메시지에 field 이름.
# ─────────────────────────────────────────────────────────────────────────────
def test_ac_schema_fields_present():
    assert validate_ac_record(_full_record()) == []
    # required 4 누락 → 위반(field 이름 포함)
    for field in ("id", "statement", "source", "tier"):
        rec = _full_record()
        del rec[field]
        errs = validate_ac_record(rec)
        assert errs, f"required {field} 누락 미검출"
        assert any(field in e for e in errs), f"{field} 위반 메시지에 field 이름 부재: {errs}"
    # optional 3 누락 = OK (위반 0) — Option(a) 핵심 (derived 부재가 false-FAIL 아님)
    for field in ("verification", "coverage_required", "phase"):
        rec = _full_record()
        del rec[field]
        assert validate_ac_record(rec) == [], f"optional {field} 누락은 위반 아님이어야: {validate_ac_record(rec)}"
    # optional present-but-malformed → 위반 (format-only)
    assert validate_ac_record(_full_record(verification="")), "빈 verification = malformed"
    assert validate_ac_record(_full_record(coverage_required="design")), "coverage_required 문자열 = malformed(list 아님)"
    assert validate_ac_record(_full_record(phase=3)), "phase=3 = malformed"
    # required enum 위반
    assert validate_ac_record(_full_record(source="bogus"))
    assert validate_ac_record(_full_record(tier="bogus"))
    # 유효 enum 변이는 통과 (phase 문자열 "2" 정규화 / source user / tier advisory)
    assert validate_ac_record(_full_record(phase="2", source="user", tier="advisory")) == []
    # gate-level 동형(F-AC2-4COL-OK): §5 4-컬럼(id/source/tier/statement, derived 3 부재)+매핑 완비 → PASS
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        write_ac_source(ac, [("AC-2", "derived", "normative")])  # 4-컬럼(statement emit) / optional 3 부재
        write_rtm(rtm, [("AC-2", "normative", "test_ac_schema_fields_present")])
        assert_gate_pass(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-3 (normative) — packet 이 정수 count 아닌 acceptance_criteria[] 항목화 전달
# ─────────────────────────────────────────────────────────────────────────────
def test_requirements_output_itemized_not_count():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        # count-only(항목화 표 부재) → 판정불가 fail-closed
        write_ac_source_countonly(ac)
        assert_gate_fail(*run_gate(1, ac, rtm))
        # 항목화 §5 표 → PASS
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        assert_gate_pass(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-4 (normative) — 모든 AC-N → ≥1 §8 명명 테스트, 미커버=0
# ─────────────────────────────────────────────────────────────────────────────
def test_all_ac_mapped_to_named_test():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        # normative AC-2 orphan(§8 미매핑) → FAIL
        write_ac_source(ac, [("AC-1a", "derived", "normative"), ("AC-2", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_a")])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # 전부 매핑 → 미커버 0 → PASS
        write_rtm(rtm, [("AC-1a", "normative", "test_a"), ("AC-2", "normative", "test_b")])
        assert_gate_pass(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-5 (normative) — Phase1 명명 fidelity 미충족=FAIL, 실파일 미검사
# ─────────────────────────────────────────────────────────────────────────────
def test_phase1_named_fidelity_failclosed():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        tests = os.path.join(d, "tests")
        # (a) 명명 fidelity 미충족(normative 명명 테스트 없음) → FAIL
        write_ac_source(ac, [("AC-5", "user", "normative")])
        write_rtm(rtm, [("AC-5", "normative", None)])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # (b) 명명은 있으나 실파일 부재 — Phase1 은 born-missing 미실행 → PASS (실파일 미검사 입증)
        write_rtm(rtm, [("AC-5", "normative", "test_ghost")])
        make_tests_root(tests, [])  # test_ghost 실 def 부재
        assert_gate_pass(*run_gate(1, ac, rtm, tests_root=tests))


# ─────────────────────────────────────────────────────────────────────────────
# AC-6 (normative) — Phase2 born-missing(ast)=FAIL
# ─────────────────────────────────────────────────────────────────────────────
def test_phase2_born_missing_failclosed():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        tests = os.path.join(d, "tests")
        write_ac_source(ac, [("AC-6", "user", "normative")])
        write_rtm(rtm, [("AC-6", "normative", "test_born_missing_sym")])
        make_tests_root(tests, [])  # symbol 부재
        assert_gate_fail(*run_gate(2, ac, rtm, tests_root=tests))
        # 실 def 착륙 → PASS
        make_tests_root(tests, ["test_born_missing_sym"])
        assert_gate_pass(*run_gate(2, ac, rtm, tests_root=tests))


# ─────────────────────────────────────────────────────────────────────────────
# AC-7 (normative) — 4 bypass vector 전부 green 탈출 불가
# ─────────────────────────────────────────────────────────────────────────────
def test_no_optout_bypass():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        # a) 빈 AC 목록
        write_ac_source_empty(ac)
        assert_gate_fail(*run_gate(1, ac, rtm))
        # b) 미선언 §8 (RTM 표 부재) + placeholder
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm_notable(rtm)
        assert_gate_fail(*run_gate(1, ac, rtm))
        write_rtm_placeholder(rtm)
        assert_gate_fail(*run_gate(1, ac, rtm))
        # c) stub 명명 회피 (plain placeholder, backtick 없음) → normative 미매핑
        write_rtm(rtm, [("AC-1a", "normative", "TODO")])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # d) phase 오선언 (invalid) → non-zero fail-closed
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        assert_gate_nonzero(*run_gate(3, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-8 (normative) — 2 잔여 정직 공개 존재 ∧ semantic 완전성 강제 안 함(over-reach kill)
# ─────────────────────────────────────────────────────────────────────────────
def test_ceiling_honesty_disclosed_no_overreach():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        tests = os.path.join(d, "tests")
        # PASS 산출물에 2 잔여(정직 공개)가 기계 판독 가능하게 박제되는지
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        rc, out = run_gate(1, ac, rtm)
        assert_gate_pass(rc, out)
        assert "완전성 미강제" in out, f"(i) test-semantic 완전성 미강제 공개 부재\n{out}"
        assert "분해완결성 미강제" in out, f"(ii) user→AC 분해완결성 미강제 공개 부재\n{out}"
        assert "완전 봉인" in out and "hard-claim" in out, f"완전봉인 hard-claim 금지 명시 부재\n{out}"
        # over-reach kill 1: declared/advisory 미커버여도 PASS (forged machine test 강제 금지)
        write_ac_source(ac, [("AC-1a", "derived", "normative"),
                             ("AC-1b", "user", "declared"), ("AC-10", "user", "advisory")])
        write_rtm(rtm, [("AC-1a", "normative", "test_x"),
                        ("AC-1b", "declared", None), ("AC-10", "advisory", None)])
        assert_gate_pass(*run_gate(1, ac, rtm))
        # over-reach kill 2: semantic 완전성 미강제 — stub 이 phase2 born-missing PASS (의미 검사 안 함)
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_semantically_trivial")])
        make_tests_root(tests, ["test_semantically_trivial"])
        assert_gate_pass(*run_gate(2, ac, rtm, tests_root=tests))


# ─────────────────────────────────────────────────────────────────────────────
# AC-9 (normative) — 게이트 invariant set 이 AC↔§8↔file 로 한정(G2/G3 미검사)
# ─────────────────────────────────────────────────────────────────────────────
def test_gate_scope_disjoint_g2_g3():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = os.path.join(d, "ac.md"), os.path.join(d, "rtm.md")
        tests = os.path.join(d, "tests")
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        rc, out = run_gate(1, ac, rtm)
        assert_gate_pass(rc, out)
        # scope 정직 공개: runtime liveness(G2)·discriminating(G3) 미검사 + disjoint 명시
        assert "runtime liveness" in out and "discriminating" in out and "disjoint" in out, \
            f"G1 scope disjoint(G2/G3 미검사) 공개 부재\n{out}"
        # G3 미침범 입증: stub(비-discriminating) 이 phase2 PASS = 게이트가 discriminating 행사 미검사
        write_rtm(rtm, [("AC-1a", "normative", "test_nondiscriminating_stub")])
        make_tests_root(tests, ["test_nondiscriminating_stub"])
        assert_gate_pass(*run_gate(2, ac, rtm, tests_root=tests))


# ─────────────────────────────────────────────────────────────────────────────
# ac_id unit (보강) — sub-letter/ malformed / validate_ac_record enum (§8.1 dogfood 외 추가 커버)
# ─────────────────────────────────────────────────────────────────────────────
def test_ac_id_subletter_and_validate_record_enums():
    # AC-1a/AC-1b/AC-9/AC-10 parse OK (spawn packet 명시)
    assert parse_ac_id("AC-1a") == (1, "a")
    assert parse_ac_id("AC-1b") == (1, "b")
    assert parse_ac_id("AC-9") == (9, None)
    assert parse_ac_id("AC-10") == (10, None)
    # malformed reject (spawn packet 명시: AC- / ACX-1 / AC-1A)
    assert parse_ac_id("AC-") is None
    assert parse_ac_id("ACX-1") is None
    assert parse_ac_id("AC-1A") is None
    # validate_ac_record — required 4 + enum + optional format (Option (a), S4)
    assert validate_ac_record(_full_record()) == []
    assert validate_ac_record({}), "빈 record 는 required 4 부재 위반"
    assert validate_ac_record(_full_record(phase=5))          # optional phase malformed
    assert validate_ac_record(_full_record(source="external"))  # required source enum 위반
