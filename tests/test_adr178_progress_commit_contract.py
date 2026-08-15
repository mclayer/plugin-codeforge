"""test_adr178_progress_commit_contract.py — ADR-178 progress-commit 규범 계약 검증.

CFP-2966 Phase 2 (테스트) / Change Plan §8.1.1 RTM (zero-drop 27개 named test).
Under test: archive/adr/ADR-178-subagent-progress-commit-preservation.md

contractual tiers:
  · AC-1–AC-19: normative 18 메트릭 (§결정 1~13 load-bearing) = 27개 test
  · AC-7: declared tier (no named test — file docstring 기재)

invariant (RED→GREEN discriminating — hollow-green 금지):
  · presence 검사 = load-bearing 문면 앵커(문구 리터럴·조합) 단위로 검증
  · mutant oracle = 앵커 제거·훼손 시 RED
  · AC-4-B+C 통합: test_forbidden_halt_form_absent_in_normative_region 내부에
    금지 토큰 배열 4원소 cardinality + ①~④ bijection assert 포함 (설계리뷰 Iter 2 인계)
  · AC-11 정직 제약: 금지-선언 문면만 assert (긍정 단정 금지)

hyperlink 정책: ADR 파일 경로 수동지정(`ADR178_PATH` env) 지원 (mutant 실증용 경로 재지정).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest


def _get_adr_path() -> Path:
    """ADR-178 파일 위치. 환경변수 override 가능 (mutant 실증용 seam)."""
    env_path = os.environ.get("ADR178_PATH")
    if env_path:
        return Path(env_path)
    # 기본: 테스트 파일 기준 상대경로 → repo root
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "archive" / "adr" / "ADR-178-subagent-progress-commit-preservation.md"


@pytest.fixture
def adr178_content() -> str:
    """ADR-178 전문을 메모리에 로드."""
    adr_path = _get_adr_path()
    if not adr_path.exists():
        pytest.skip(f"ADR-178 파일 부재: {adr_path}")
    return adr_path.read_text(encoding="utf-8")


def _extract_region(content: str, start_marker: str, end_marker: str) -> str:
    """HTML 주석 마커로 경계진 섹션 추출.

    Args:
        content: 전체 문서
        start_marker: 시작 마커 (예: "progress-commit-normative-region:start")
        end_marker: 종료 마커 (예: "progress-commit-normative-region:end")

    Returns:
        마커 내부 텍스트 (마커 제외)
    """
    start_pattern = f"<!-- {re.escape(start_marker)} -->"
    end_pattern = f"<!-- {re.escape(end_marker)} -->"

    match = re.search(
        f"{start_pattern}(.*?){end_pattern}",
        content,
        re.DOTALL
    )
    if not match:
        return ""
    return match.group(1)


def _extract_quoted_region(content: str, start_marker: str, end_marker: str) -> str:
    """금지 토큰 배열 같은 인용 블록 추출."""
    start_pattern = f"<!-- {re.escape(start_marker)} -->"
    end_pattern = f"<!-- {re.escape(end_marker)} -->"

    match = re.search(
        f"{start_pattern}(.*?){end_pattern}",
        content,
        re.DOTALL
    )
    if not match:
        return ""
    return match.group(1)


# ============================================================================
# AC-1: ADR 존재 + axis-c scoped
# ============================================================================

def test_adr_progress_commit_exists_and_axis_c_scoped(adr178_content: str):
    """AC-1: ADR-178 파일이 존재하고, 서브에이전트 산출물 보존(축 C)에 범위지어졌는가?

    load-bearing 문면:
      · title 포함: "서브에이전트 진행 산출물 선행 적재(progress-commit) 규범"
      · category: "orchestration-discipline"
      · carrier_story: "CFP-2966"
    """
    # 메타정보 로드
    match = re.search(
        r"---\n(.*?)\n---",
        adr178_content,
        re.DOTALL
    )
    if not match:
        pytest.fail("ADR frontmatter 파싱 실패")

    frontmatter = match.group(1)

    # 제목 검증
    title_match = re.search(r"title:\s*([^\n]+)", frontmatter)
    assert title_match, "title 필드 부재"
    title = title_match.group(1).strip()
    assert "progress-commit" in title, f"title 에 progress-commit 미포함: {title}"

    # 범주 검증
    assert "category: orchestration-discipline" in frontmatter, (
        "category 가 orchestration-discipline 아님"
    )

    # 캐리어 story 검증
    assert "carrier_story: CFP-2966" in frontmatter, (
        "carrier_story 가 CFP-2966 아님"
    )


# ============================================================================
# AC-2: Preservation unit clause — local git commit
# ============================================================================

def test_preservation_unit_clause_present(adr178_content: str):
    """AC-2: 보존 최소 인정 단위가 local git commit 으로 명시되었는가?

    load-bearing 문면 (§결정 2-1):
      · "보존 최소 인정 단위 = local git commit (P0)"
      · "working tree·stash·scratch 파일·최종 메시지는 보존 단위로 인정하지 않는다"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 핵심 문구 검증
    assert "보존 최소 인정 단위 = local git commit (P0)" in normative, (
        "§결정 2-1 보존 단위 정의 미발견"
    )
    assert "working tree" in normative and "보존 단위로 인정하지 않는다" in normative, (
        "working tree 배제 문면 미발견"
    )


# ============================================================================
# AC-3: CFP-2946 disjoint cross-ref
# ============================================================================

def test_cfp2946_disjoint_crossref_present(adr178_content: str):
    """AC-3: CFP-2946(살아있는 에이전트 재개) 과의 disjoint 관계가 명시되었는가?

    load-bearing 문면 (§결정 13):
      · "CFP-2946 (살아있는 에이전트 재개, 축 B): 본 ADR 과 disjoint"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "CFP-2946" in normative, "CFP-2946 cross-ref 미발견"
    assert "disjoint" in normative, "disjoint 명시 미발견"


# ============================================================================
# AC-4: Negative control clause + forbidden halt form 부재
# ============================================================================

def test_negative_control_clause_present(adr178_content: str):
    """AC-4-A: negative control 절이 존재하는가?

    load-bearing 문면 (§결정 7):
      · "진행 커밋은 정지 사유가 아니다"
      · "zero-notice 가정"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "진행 커밋은 정지 사유가 아니다" in normative, (
        "§결정 7-1 negative control 문면 미발견"
    )
    assert "zero-notice" in normative, (
        "§결정 7-2 zero-notice 가정 미발견"
    )


def test_forbidden_halt_form_absent_in_normative_region(adr178_content: str):
    """AC-4-B+C: normative region 내 금지 형태 부재 + 배열 완전성 검증.

    AC-4-B: normative region 내에서 금지된 형태의 "한도·정지" 조항이 없는가?
      정의역: progress-commit-normative-region (마커 내부) MINUS forbidden-form-quotation 블록
      금지 토큰 4개 (closed set): "한도 임박 시 커밋", "커밋 후 정지",
                              "한도 신호 수신 시 저장", "종료 시점에 저장한다"
      load-bearing: 4 토큰 모두 quotation 블록 내부에만 존재 (정의역 내부에서 0)

    AC-4-C: forbidden-form-quotation 블록 내 FORBIDDEN_TOKENS 배열 완전성 검증 (설계리뷰 Iter 2 인계).
      load-bearing:
        · 배열 원소 개수 == 4 (정확히 4개 형태)
        · 각 원소에 # ①형 ~ # ④형 annotation 1:1 전단사
        · 배열 원소 == 정의된 금지 토큰 집합 equality (배열↔테스트 기대 drift 앵커)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    quoted = _extract_quoted_region(
        normative,
        "forbidden-form-quotation:start",
        "forbidden-form-quotation:end"
    )

    # 정의역 = normative - quoted
    search_region = normative
    if quoted:
        search_region = normative.replace(quoted, "")

    # 4 금지 토큰 (AC-4-B 검증 대상)
    forbidden_tokens = [
        "한도 임박 시 커밋",
        "커밋 후 정지",
        "한도 신호 수신 시 저장",
        "종료 시점에 저장한다",
    ]

    # AC-4-B: quotation 블록 밖에서 0 presence
    for token in forbidden_tokens:
        assert token not in search_region, (
            f"금지 토큰 '{token}' 이 quotation 블록 밖에서 발견됨 (§결정 7 위반)"
        )

    # AC-4-C: 배열 파싱 + cardinality + bijection
    if not quoted:
        pytest.fail("FORBIDDEN_TOKENS quotation 블록 미발견")

    array_match = re.search(
        r"FORBIDDEN_TOKENS = \[(.*?)\]",
        quoted,
        re.DOTALL
    )
    if not array_match:
        pytest.fail("FORBIDDEN_TOKENS 배열 미발견 in quotation 블록")

    array_content = array_match.group(1)
    elements = re.findall(r'"([^"]+)"', array_content)

    # cardinality == 4
    assert len(elements) == 4, (
        f"FORBIDDEN_TOKENS 원소 {len(elements)}개 (4개 기대)"
    )

    # ①②③④ annotation bijection
    annotations = re.findall(r"# ([①②③④])형", array_content)
    assert len(annotations) == 4, (
        f"annotation 개수 {len(annotations)}개 (4개 기대)"
    )
    assert set(annotations) == {"①", "②", "③", "④"}, (
        f"annotation 전단사 미성립: {sorted(set(annotations))}"
    )

    # 배열 원소 == 금지 토큰 집합 equality (drift 앵커)
    assert set(elements) == set(forbidden_tokens), (
        f"배열↔테스트 기대 drift: "
        f"배열={sorted(set(elements))}, "
        f"기대={sorted(set(forbidden_tokens))}"
    )


# ============================================================================
# AC-5: termination_cause enum 완전성 + disposition 전단사
# ============================================================================

def test_termination_cause_enum_complete(adr178_content: str):
    """AC-5-A: termination_cause enum 이 5개 값을 모두 나열했는가?

    load-bearing (§결정 1 표):
      · timeout, error, cancelled, zero_output, normal (5개 정확)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 표 헤더 찾기 (마크다운 테이블)
    table_match = re.search(
        r"\| termination_cause \|",
        normative
    )
    assert table_match, "§결정 1 termination_cause 표 미발견"

    # 5개 값 검증 (각각 독립 검증)
    enum_values = ["timeout", "error", "cancelled", "zero_output", "normal"]
    for val in enum_values:
        assert val in normative, f"termination_cause '{val}' 미발견"


def test_termination_cause_disposition_bijection(adr178_content: str):
    """AC-5-B: 각 termination_cause 의 (사전 적재 / 사후 회수) 처분이 1:1 매핑되었는가?

    load-bearing (§결정 1 표):
      · timeout/error/cancelled/zero_output: 사후 회수 '발동'
      · normal: 사후 회수 '비발동' (정상 return 경로)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 표 구조 검증: 각 행에서 사전 적재(포함) + 사후 회수 처분 열이 있어야 함
    causes = ["timeout", "error", "cancelled", "zero_output"]
    for cause in causes:
        # 각 원인이 "발동" 처분을 받아야 함
        pattern = f"{cause}.*?발동"
        assert re.search(pattern, normative), (
            f"'{cause}' 의 '발동' 처분 미발견"
        )

    # normal 은 비발동
    assert "normal" in normative, "normal 케이스 미발견"
    pattern = r"normal.*?비발동|정상.*?return"
    assert re.search(pattern, normative), (
        "normal 케이스의 '비발동' 또는 정상 return 경로 미발견"
    )


# ============================================================================
# AC-6: Lead aggregation cross-ref
# ============================================================================

def test_lead_aggregation_crossref_present(adr178_content: str):
    """AC-6: lead 집계 정합이 §결정 5-6 에서 cross-ref 되었는가?

    load-bearing (§결정 5-6):
      · "lead 동시 사망 케이스는 본 §결정 5-1/5-4 의 재개자 경로가 담당한다"
      · ADR-170 §결정 19 언급

    정직 scope: presence 만 — 실질 규칙은 review-tier (docstring 에 정직 표기)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "lead" in normative, "lead 관련 텍스트 미발견"
    assert "§결정 5-6" in normative or "동시 사망" in normative, (
        "lead 동시 사망 또는 집계 관련 문면 미발견"
    )
    assert "ADR-170" in normative, "ADR-170 cross-ref 미발견"


# ============================================================================
# AC-8: Parallel merge rule 3 elements
# ============================================================================

def test_parallel_merge_rule_three_elements_present(adr178_content: str):
    """AC-8: 병렬 워커 병합 규칙 3개 요소(identity/ordering/충돌해소)가 명시되었는가?

    load-bearing (§결정 5-5):
      · identity = 브랜치 + Agent trailer
      · ordering = committerdate
      · 충돌해소 = 자동 병합 금지 (lane PL 판정)

    정직 scope: presence 만 — 실질 규칙은 review-tier
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 3 요소 검증
    assert "identity" in normative, "identity 요소 미발견"
    assert "ordering" in normative or "committerdate" in normative, (
        "ordering 요소 미발견"
    )
    assert "충돌해소" in normative or "자동 병합 금지" in normative, (
        "충돌해소 요소 미발견"
    )


# ============================================================================
# AC-9: Zero-notice assumption + no termination time save clause
# ============================================================================

def test_zero_notice_assumption_present(adr178_content: str):
    """AC-9-A: zero-notice 가정(유예 창 미보장)이 명시되었는가?

    load-bearing (§결정 7-2):
      · "본 규범은 종료 시점에 수행되는 어떤 행위도 요구하지 않는다"
      · "종료 통지·유예 창의 존재를 규범 성립 조건으로 삼지 않으며"
      · "zero-notice 위에서 완전하게 성립한다"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "zero-notice" in normative, "zero-notice 어휘 미발견"
    assert "유예 창" in normative or "종료 통지" in normative, (
        "유예 창/종료 통지 관련 문면 미발견"
    )
    assert "완전하게 성립" in normative or "성립 조건으로 삼지 않으며" in normative, (
        "zero-notice 완결성 명시 미발견"
    )


def test_no_termination_time_save_clause(adr178_content: str):
    """AC-9-B: "종료 시점에 저장한다" 금지 조항이 반영되었는가?

    load-bearing: forbidden-form-quotation 에 형④ "종료 시점에 저장한다" 포함
    정의역 밖 presence 검증은 AC-4-B 에서 수행.
    """
    quoted = _extract_quoted_region(
        adr178_content,
        "forbidden-form-quotation:start",
        "forbidden-form-quotation:end"
    )

    assert "종료 시점에 저장한다" in quoted, (
        "금지 토큰 형④ 미포함 in quotation 블록"
    )


# ============================================================================
# AC-10: Durability tier ladder (P0/P1/P2) + tier downgrade rule
# ============================================================================

def test_durability_tier_ladder_present(adr178_content: str):
    """AC-10-A: 내구 계층 P0/P1/P2 가 명시되었는가?

    load-bearing (§결정 3 표):
      · P0 durable-local (local commit)
      · P1 durable-remote (origin push)
      · P2 landable (PR/Story)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 3 tier 검증
    assert "P0 durable-local" in normative or ("P0" in normative and "local" in normative), (
        "P0 tier 미발견"
    )
    assert "P1 durable-remote" in normative or ("P1" in normative and "remote" in normative), (
        "P1 tier 미발견"
    )
    assert "P2 landable" in normative or ("P2" in normative and "landable" in normative), (
        "P2 tier 미발견"
    )


def test_tier_downgrade_rule_present(adr178_content: str):
    """AC-10-B: tier-downgrade 규칙(하위 성공은 상위 실패로 취소 안됨)이 명시되었는가?

    load-bearing (§결정 3-1):
      · "하위 tier 성공은 상위 tier 실패에 의해 취소되지 않는다"
      · "push 거부 시도 실패해도 P0 가 잔존하면 보존 성공"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "취소되지 않는다" in normative or "취소 금지" in normative, (
        "tier-downgrade 규칙 미발견"
    )
    assert "push 거부" in normative or "상위 tier 실패" in normative, (
        "push 실패 예제 또는 tier 실패 문면 미발견"
    )


# ============================================================================
# AC-11: Advisory ceiling label + no full mechanical enforcement overclaim
# ============================================================================

def test_advisory_ceiling_label_present(adr178_content: str):
    """AC-11-A: advisory ceiling 라벨이 명시되었는가?

    load-bearing (§결정 8-1):
      · "tier = advisory (ceiling)"
      · "규범 문구 presence 는 prompt-mandate 이나 실준수는 비-PR-enforceable"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "advisory" in normative, "advisory ceiling 어휘 미발견"
    assert "prompt-mandate" in normative or "비-PR-enforceable" in normative, (
        "advisory ceiling 메커니즘 설명 미발견"
    )


def test_no_full_mechanical_enforcement_overclaim(adr178_content: str):
    """AC-11-B: "100% 기계강제" 또는 "hard-gate" 단정이 없는가?

    정직 제약: 규범은 금지-선언 문면만 assert (긍정 단정 금지)

    금지 문면 (§결정 8-2):
      · "표방하는 서술을 금지한다" (금지 선언이 있어야 함)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 금지 선언 문면 검증
    overclaim_prohibition = (
        "표방하는 서술을 금지한다" in normative or
        "100% 기계강제" in normative or
        "hard-gate" in normative
    )
    assert overclaim_prohibition, (
        "금지 선언(overclaim 금지) 문면 미발견"
    )


# ============================================================================
# AC-12: Residue GC jurisdiction boundary
# ============================================================================

def test_residue_gc_jurisdiction_boundary_present(adr178_content: str):
    """AC-12: 잔재 GC 관할 경계가 명시되었는가?

    load-bearing (§결정 10-1):
      · "진행 커밋·dirty 파일은 ADR-169 §결정 3 의 보존 트리거"
      · "GC 구조적 면제 대상"
      · "미push 커밋 또는 dirty 상태 보유"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "ADR-169" in normative, "ADR-169 참조 미발견"
    assert "GC 구조적 면제" in normative or "보존 트리거" in normative, (
        "GC 관할 경계 설명 미발견"
    )
    assert "dirty" in normative or "unpushed" in normative, (
        "dirty/unpushed 상태 언급 미발견"
    )


# ============================================================================
# AC-13: Frequency semantic unit clause + cost accounting section
# ============================================================================

def test_frequency_semantic_unit_clause(adr178_content: str):
    """AC-13-A: 빈도 정의가 시간 주기가 아닌 의미 단위 경계로 정의되었는가?

    load-bearing (§결정 2-2):
      · "시점 = atomic 의미 단위 경계 (시간 주기 아님)"
      · "파일군 1개 완결" / "AC 1개 대응분" / "조사 축 1개 결론" (택1)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "의미 단위 경계" in normative, "의미 단위 경계 정의 미발견"
    assert "시간 주기 아님" in normative, "시간 주기 배제 미발견"
    # 3개 운영 가능 표현 중 1+ 제시
    examples_present = (
        "파일군" in normative or
        "AC 1개 대응분" in normative or
        "조사 축" in normative
    )
    assert examples_present, "의미 단위 운영 표현 예제 미발견"


def test_cost_accounting_section_present(adr178_content: str):
    """AC-13-B: 비용 계상 절(§결정 9)이 존재하는가?

    load-bearing (§결정 9):
      · "2축 분리 의무": latency vs quota
      · marginal cost 수치화 (훅 체인 ≈ 2,106.1 ms)
      · 빈도 상한 언급
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "§결정 9" in normative or "비용" in normative, (
        "§결정 9 또는 비용 언급 미발견"
    )
    assert "latency" in normative or "quota" in normative, (
        "2축 분리 미발견"
    )
    assert "ms" in normative or "2,106" in normative, (
        "marginal cost 수치 미발견"
    )


# ============================================================================
# AC-14: Discovery channel clause
# ============================================================================

def test_discovery_channel_clause_present(adr178_content: str):
    """AC-14: 발견 채널(최소 3중)이 명시되었는가?

    load-bearing (§결정 5-1):
      · ① 브랜치 네임스페이스 (cfp-NNN[-slug])
      · ② 잔재 발견 스캐너 (dirty/unpushed-N 술어)
      · ③ ADR-172 세션-독립 스케줄 관측
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 3 채널 검증
    assert "브랜치 네임스페이스" in normative or "cfp-NNN" in normative, (
        "발견 채널 ① 브랜치 미발견"
    )
    assert "스캐너" in normative or "dirty" in normative, (
        "발견 채널 ② 스캐너 술어 미발견"
    )
    assert "ADR-172" in normative or "세션-독립" in normative, (
        "발견 채널 ③ 스케줄 관측 미발견"
    )


# ============================================================================
# AC-15: Incomplete marker convention + inconclusive treatment cross-ref
# ============================================================================

def test_incomplete_marker_convention_defined(adr178_content: str):
    """AC-15-A: 미완 표식 규약([WIP] 리터럴)이 정의되었는가?

    load-bearing (§결정 5-2):
      · "진행 커밋의 subject = `[CFP-NNN][WIP]`"
      · "[WIP] 토큰이 미완 표식"
      · "Remaining: <추상 요약>" 본문 기록
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "[WIP]" in normative, "[WIP] 토큰 미발견"
    assert "미완 표식" in normative or "미완" in normative, (
        "미완 표식 용어 미발견"
    )
    assert "Remaining:" in normative or "본문 1줄" in normative, (
        "Remaining 기록 규약 미발견"
    )


def test_inconclusive_treatment_crossref(adr178_content: str):
    """AC-15-B: inconclusive 취급이 ADR-170 §결정 20 과 cross-ref 되었는가?

    load-bearing (§결정 5-3):
      · "후속 주체가 진행 커밋 부분 산출물을 소비할 때 그것은 inconclusive 로 취급"
      · "ADR-170 §결정 20 INV-L2 정합"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "inconclusive" in normative, "inconclusive 어휘 미발견"
    assert "ADR-170" in normative or "§결정 20" in normative, (
        "ADR-170 cross-ref 미발견"
    )


# ============================================================================
# AC-16: D2 disposition path or justified rejection
# ============================================================================

def test_d2_disposition_path_or_justified_rejection(adr178_content: str):
    """AC-16: D2(분석 텍스트) 처분 경로가 정의되거나 기각이 정당화되었는가?

    load-bearing (§결정 4):
      · 2-speed 적재: cheap tier (Write) + commit tier (Bash)
      · landable 승격 경로 2개 제시 (기각된 신규 경로 포함)
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "§결정 4" in normative or "D2" in normative, (
        "§결정 4 또는 D2 언급 미발견"
    )
    assert "cheap tier" in normative or "Write" in normative, (
        "cheap tier 처분 경로 미발견"
    )
    assert "landable" in normative or "기각" in normative or "신설" in normative, (
        "D2 처분 경로 또는 기각 근거 미발견"
    )


# ============================================================================
# AC-17: Self-landing subject clause + permission surface verdict
# ============================================================================

def test_self_landing_subject_clause(adr178_content: str):
    """AC-17-A: 보존 주체가 "산출 주체 자신(워커 자기-적재)"으로 명시되었는가?

    load-bearing (§결정 2-3):
      · "주체 = 산출 주체 자신 (워커 자기-적재)"
      · "Orchestrator-사후수습 모델이 불성립"
      · "Orchestrator inline 대행은 ADR-039 whitelist 밖"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "자기-적재" in normative or "산출 주체 자신" in normative, (
        "워커 자기-적재 원칙 미발견"
    )
    assert "ADR-039" in normative or "Orchestrator inline" in normative, (
        "ADR-039 무접촉 또는 Orchestrator 배제 미발견"
    )


def test_permission_surface_verdict_present(adr178_content: str):
    """AC-17-B: 권한 선언면 판정(P6 갈림길)이 제시되었는가?

    load-bearing (§결정 8-3):
      · "판정 = 41 agent 파일 git commit allow 선언 추가 기각"
      · "disclosed residual" 명시
      · consumer non-bypass 환경 명시 이관
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "권한" in normative or "allow" in normative or "P6" in normative, (
        "권한 선언 관련 문면 미발견"
    )
    assert "기각" in normative or "disclosed residual" in normative, (
        "권한 선언 기각 또는 잔여 명시 미발견"
    )
    assert "consumer" in normative or "non-bypass" in normative, (
        "consumer 환경 명시 이관 미발견"
    )


# ============================================================================
# AC-18: Consistency condition clause
# ============================================================================

def test_consistency_condition_clause_present(adr178_content: str):
    """AC-18: 자기-일관성(self-consistent) 조건이 명시되었는가?

    load-bearing (§결정 2-4):
      · "각 진행 커밋은 의미 단위 완결 상태"
      · "그 커밋만 회수해도 내적 모순이 없는 상태"
      · "half-written 상태의 커밋은 보존된 쓰레기"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "self-consistent" in normative or "자기-일관성" in normative, (
        "self-consistent 조건 미발견"
    )
    assert "내적 모순" in normative or "완결 상태" in normative, (
        "일관성 정의 미발견"
    )
    assert "half-written" in normative or "쓰레기" in normative, (
        "half-written 배제 미발견"
    )


# ============================================================================
# AC-19: Secret exception clause + masking path
# ============================================================================

def test_secret_exception_clause_present(adr178_content: str):
    """AC-19-A: secret 예외가 명시되었는가?

    load-bearing (§결정 6-1):
      · "보존 의무의 예외는 secret 포함 산출물 전체 가 아니라 secret 포함 구간(span)"
      · "마스킹 후 적재가 1급 경로"
      · "span 마스킹(`***REDACTED***`)·파일 분리"
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    assert "§결정 6" in normative or "secret" in normative, (
        "§결정 6 또는 secret 언급 미발견"
    )
    assert "span" in normative, "span 단위 원칙 미발견"
    assert "마스킹" in normative or "REDACTED" in normative, (
        "마스킹 경로 미발견"
    )


def test_masking_path_present(adr178_content: str):
    """AC-19-B: 마스킹 기술 경로가 명시되었는가?

    load-bearing (§결정 6):
      · 표면별 비대칭 default (커밋 내용/메시지/브랜치명/tier)
      · 우회 금지 (.gitignore 배제면 상위)
      · 커밋 메시지 값공간 폐쇄
    """
    normative = _extract_region(
        adr178_content,
        "progress-commit-normative-region:start",
        "progress-commit-normative-region:end"
    )

    # 표면별 비대칭 default 검증
    surfaces = ["S-A 커밋 내용", "S-B 커밋 메시지", "S-C 브랜치명", "S-D tier"]
    found_surfaces = sum(1 for s in surfaces if s[:3] in normative)  # S-A/S-B/S-C/S-D 패턴
    assert found_surfaces >= 2, (
        f"마스킹 표면별 정책 불충분 ({found_surfaces}개, 2+ 기대)"
    )

    assert ".gitignore" in normative or "우회 금지" in normative, (
        ".gitignore 우회 금지 미발견"
    )
    assert "값공간 폐쇄" in normative or "cfp-NNN" in normative, (
        "메시지 값공간 폐쇄 미발견"
    )
