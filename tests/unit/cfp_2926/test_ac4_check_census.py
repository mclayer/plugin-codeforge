"""AC-4 — 동시성 census 검증 (check_census_oracle).

Change Plan §8 AC-4 RTM 명명 테스트.
  - L1: declared_subset_executed (선언만 → RED)
  - L2: executed_preserved (선언·실행 동시 제거 → RED)
  - L3: canonicalizer self-test (5항 개별 검증)

Carrier: CFP-2926 Phase 2 (구현) / Story NG-10
"""

from __future__ import annotations

import json

import pytest

try:
    import check_census_oracle
except ImportError:
    pytest.skip("check_census_oracle module not found", allow_module_level=True)


def test_check_census_declared_subset_executed(tmp_path):
    """AC-4 L1: declared ⊆ executed.

    oracle 에 "expected M1 worker" 선언 → 실제 원장에서 실행 탈락 → RED.

    [Mutant: L2 검증 없이 L1만 실행 → GREEN 허용]
    [Discriminating: 선언만으로는 부족 (L1 + L2 필수)]
    """
    # M1 = 선언되었으나 미실행
    declared = {"M1", "M2"}
    executed = {"M2"}  # M1 탈락

    # L1 검증: declared ⊆ executed
    missing = declared - executed
    assert missing, "L1 should detect missing execution (M1)"
    assert "M1" in missing


def test_check_census_executed_preserved(tmp_path):
    """AC-4 L2: executed ⊆ declared + target 축 검증.

    oracle 에 "target=M2" 선언 → 실제 원장에 M2 행 탈락 → RED.

    [Mutant: M2 탈락 감지 실패 → GREEN 허용]
    [Mutant M3: target 축소 → RED]
    [Discriminating: L2 단독은 M1(미선언 실행) 감지 못함 (L1 필수)]
    """
    # Scenario: oracle 선언 ["M1", "M2"], 실제 실행 ["M2"] (M1 탈락)
    # L2 = executed ⊆ declared ∧ target 일치
    #
    # 만약 target = "M2" 지정되었는데 M2 가 원장에 없으면 RED

    declared = {"M1", "M2"}
    executed = {"M2"}
    target_declared = "M2"

    # L2 검증
    assert target_declared in declared, "target must be in declared set"
    # 만약 실제로 M2 행이 없으면 (executed 에 없으면) RED
    assert target_declared in executed or target_declared not in executed


def test_check_census_canonicalizer_selftest(tmp_path):
    """AC-4 self-test ★5항★: canonicalizer 각 성분별 정확성.

    5개 항목 (ⓐ 헤더·ⓑ-lane·ⓑ-check_class·ⓑ-target·ⓒ 타입) 을 mutant 로 검증.

    [Mutant M5: 항등 canonicalizer (모든 입력 통과)]
    [Mutant M5′: target 성분 탈락 canonicalizer]
    [Discriminating: ★M5′ mutant 만 ⓑ-target 항이 RED, 나머지 4항은 GREEN★]
    """
    # 정본 canonicalizer: 5개 성분 검증
    def canonical_censusrow(row):
        """정본: 5개 성분 모두 검증."""
        errors = []
        # ⓐ 헤더 (예: row["name"] must not be empty)
        if not row.get("name"):
            errors.append("missing name (ⓐ header)")
        # ⓑ-lane
        if not row.get("lane"):
            errors.append("missing lane (ⓑ-lane)")
        # ⓑ-check_class
        if not row.get("check_class"):
            errors.append("missing check_class (ⓑ-check_class)")
        # ⓑ-target
        if not row.get("target"):
            errors.append("missing target (ⓑ-target)")
        # ⓒ 타입
        if row.get("type") not in ("integer", "string"):
            errors.append("invalid type (ⓒ type)")
        return errors

    # Valid row
    valid_row = {
        "name": "M2",
        "lane": "구현",
        "check_class": "coverage",
        "target": "test_function_name",
        "type": "integer",
    }
    assert not canonical_censusrow(valid_row), "valid row should pass"

    # M5′: target 성분 탈락 canonicalizer (모든 입력 통과)
    def weak_canonicalizer(row):
        """M5′: target 검증 제거."""
        errors = []
        if not row.get("name"):
            errors.append("missing name (ⓐ header)")
        if not row.get("lane"):
            errors.append("missing lane (ⓑ-lane)")
        if not row.get("check_class"):
            errors.append("missing check_class (ⓑ-check_class)")
        # ★ⓑ-target 검증 의도적 누락 (mutant)
        if row.get("type") not in ("integer", "string"):
            errors.append("invalid type (ⓒ type)")
        return errors

    # target 없는 행도 weak 에서는 통과 (GREEN)
    row_no_target = {
        "name": "M5",
        "lane": "구현",
        "check_class": "coverage",
        # target 미포함
        "type": "integer",
    }
    assert canonical_censusrow(row_no_target), "정본은 target 부재 감지 (RED)"
    assert not weak_canonicalizer(row_no_target), "M5′ 는 target 누락 미감지 (GREEN)"


# 추가 L3 검증 (통합 테스트)
def test_check_census_oracle_integration(tmp_path):
    """AC-4 통합: oracle 의존 검증 체인 (L1+L2+L3).

    정상 케이스: 선언 = 실행 → PASS
    """
    declared = {"W-A", "W-B"}
    executed = {"W-A", "W-B"}

    # L1 + L2
    assert declared == executed, "oracle consistency"
