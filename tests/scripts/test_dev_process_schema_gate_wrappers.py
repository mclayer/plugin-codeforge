"""test_dev_process_schema_gate_wrappers.py — AC-3/5/11/24 doc-lint invariant tests-root wrapper.

CFP-2687 Phase 2 (구현) — RTM proxy-anchor 해소.

기존 RTM(change-plan §8.1.1) 의 AC-3/5/11/24 4행은 doc-lint self-test
(`check_dev_process_event_schema.py` / `check_dev_process_activation_manifest.py`)에 proxy
매핑돼 tests-root 실 행위 test 가 없었다. 본 wrapper 는 각 AC invariant 를 tests-root 행위
test 로 노출한다 — doc-lint self-test 의 순수 검증 함수(RC 재사용)를 호출해 실 계약에 대해
invariant 를 직접 assert 한다.

각 AC = **discriminating**(hollow 금지 증명):
  (1) 실 계약 파싱 → invariant 충족(violations 공집합) → GREEN
  (2) in-memory mutation → 동일 검증이 RED 발화 → parity 판별성 실증

QADev 경계: 본 파일 = tests/** 만 작성. under-test = scripts/lib doc-lint self-test 순수 함수
(READ-ONLY import). 계약 파일(dev-process-event-v1.md)은 doc anchor(read).
"""

from __future__ import annotations

import re
from pathlib import Path

import check_dev_process_event_schema as ces

# tests/scripts/ → tests/ → repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "dev-process-event-v1.md"


def _contract_body() -> str:
    """실 계약 파일 본문(frontmatter 제거) — doc-lint self-test 파서 입력과 동일 전처리."""
    assert CONTRACT.exists(), f"계약 파일 부재: {CONTRACT}"
    return ces._split_frontmatter(CONTRACT.read_text(encoding="utf-8"))


# ─── AC-11 관계 매트릭스(§10) 검증 함수 — doc-lint self-test 미보유 seam(로컬 검증) ───
# check_dev_process_event_schema.py 는 §3.2/§4.1/§11 만 검증(관계 매트릭스 §10 파서 부재).
# 따라서 AC-11 은 §10 을 로컬 parser 로 검증 — 단일 함수를 positive/negative 양쪽에서 재사용해
# discriminating 판별성을 확보(hollow 금지).
_EXISTING_SIBLINGS = ("stop-event-v1", "spawn-event-v1", "fix-event-v1", "review-verdict-v4")


def _check_relationship_matrix(section10: str, violations: list) -> None:
    """§10 관계 매트릭스 = new-sibling ∧ normative non-overlap ∧ 4 기존 계약 행 존재 검증.

    AC-11 invariant: 기존 stop/spawn/fix/lane-output 계약과의 관계를 계약별 명시(default=new-sibling).
    """
    if not section10:
        violations.append("(AC-11) §10 관계 매트릭스 섹션 부재")
        return
    if "new-sibling" not in section10:
        violations.append("(AC-11) §10 new-sibling 관계 표기 부재 (supersede-drift 의심)")
    if "normative" not in section10:
        violations.append("(AC-11) §10 normative non-overlap 표기 부재")
    for existing in _EXISTING_SIBLINGS:
        if existing not in section10:
            violations.append(f"(AC-11) §10 관계 매트릭스에 {existing} 행 부재")


def _extract_section10(body: str) -> str:
    return ces._extract_section(body, r"(?m)^##\s*10\.\s", r"(?m)^##\s*11\.\s") or ""


# ══════════════════════════════ AC-3 — noise-discard closed-list = 5 (§3.2) ════════════════════════

def test_noise_discard_closed_list_is_exactly_five():
    """[AC-3 GREEN] 실 계약 §3.2 noise-discard closed-list = 정확히 5 항목 + 기대 멤버 일치.

    RTM proxy-anchor 해소: doc-lint self-test(check_dev_process_event_schema.py §3.2 (d)) 의
    check_noise_closed 를 실 계약에 대해 호출 → violations 공집합 GREEN.
    """
    body = _contract_body()
    noise = ces.parse_noise_list(body)
    assert noise, "§3.2 noise-discard closed-list 파싱 실패 (공집합)"
    violations: list = []
    ces.check_noise_closed(noise, violations)
    assert violations == [], f"실 계약 noise-5-closed 위반: {violations}"
    assert set(noise) == ces._EXPECTED_NOISE_5, (
        f"noise 멤버 불일치 got={sorted(noise)} expect={sorted(ces._EXPECTED_NOISE_5)}"
    )


def test_noise_sixth_item_triggers_closed_red():
    """[AC-3 discriminating / RC3 재사용] noise 6번째 추가 → closed RED (hollow 아님 증명)."""
    body = _contract_body()
    noise = set(ces.parse_noise_list(body)) | {"sixth_noise_item"}
    violations: list = []
    ces.check_noise_closed(noise, violations)
    assert violations, "noise 6번째 추가에도 RED 미발화 — vacuous/hollow test"


# ══════════════════════════════ AC-5 — 4 상관 ID freeze 표기 (§4.1) ══════════════════════════════

def test_four_correlation_ids_frozen_and_marked():
    """[AC-5 GREEN] 실 계약 §4.1 4 상관 ID(story/lane/defect/fix) present ∧ FREEZE 표기.

    RTM proxy-anchor 해소: doc-lint self-test §4.1 (d) 의 check_freeze 를 실 계약에 대해 호출.
    """
    body = _contract_body()
    ids, freeze_marked = ces.parse_correlation_ids(body)
    assert freeze_marked, "§4.1 FREEZE 표기 부재 — freeze 계약 미선언"
    violations: list = []
    ces.check_freeze(ids, freeze_marked, violations)
    assert violations == [], f"실 계약 4-ID freeze 위반: {violations}"
    assert ces._REQUIRED_CORRELATION_IDS <= set(ids), (
        f"4 상관 ID 누락: {sorted(ces._REQUIRED_CORRELATION_IDS - set(ids))}"
    )


def test_removing_correlation_id_triggers_freeze_red():
    """[AC-5 discriminating / RC2 재사용] defect_id 제거 → freeze RED (hollow 아님 증명)."""
    body = _contract_body()
    ids, freeze_marked = ces.parse_correlation_ids(body)
    mutated = set(ids) - {"defect_id"}
    violations: list = []
    ces.check_freeze(mutated, freeze_marked, violations)
    assert violations, "defect_id 제거에도 RED 미발화 — vacuous/hollow test"


# ══════════════════════════════ AC-11 — 관계 매트릭스 new-sibling (§10) ════════════════════════════

def test_relationship_matrix_is_new_sibling_normative():
    """[AC-11 GREEN] 실 계약 §10 관계 매트릭스 = new-sibling ∧ normative ∧ 4 기존 계약 행.

    RTM proxy-anchor 해소: §10 관계 매트릭스(new-sibling normative non-overlap)를 tests-root
    행위 test 로 직접 assert(doc-lint self-test 미보유 seam → 로컬 parser).
    """
    body = _contract_body()
    section10 = _extract_section10(body)
    violations: list = []
    _check_relationship_matrix(section10, violations)
    assert violations == [], f"실 계약 §10 관계 매트릭스 위반: {violations}"
    # new-sibling 관계 행이 4 기존 계약 각각에 대해 최소 1회 이상 명시
    assert len(re.findall(r"new-sibling", section10)) >= 4, (
        f"new-sibling 관계 행 {len(re.findall(r'new-sibling', section10))} < 4"
    )


def test_relationship_matrix_supersede_downgrade_triggers_red():
    """[AC-11 discriminating] new-sibling → supersede drift 시뮬 → RED (hollow 아님 증명)."""
    body = _contract_body()
    section10 = _extract_section10(body)
    mutated = section10.replace("new-sibling", "supersede")
    violations: list = []
    _check_relationship_matrix(mutated, violations)
    assert violations, "new-sibling→supersede drift 에도 RED 미발화 — vacuous/hollow test"


def test_relationship_matrix_missing_sibling_triggers_red():
    """[AC-11 discriminating] 기존 계약 행 제거(stop-event-v1) → RED (판별성 실증)."""
    body = _contract_body()
    section10 = _extract_section10(body)
    mutated = section10.replace("stop-event-v1", "XXX")
    violations: list = []
    _check_relationship_matrix(mutated, violations)
    assert violations, "stop-event-v1 행 제거에도 RED 미발화 — vacuous/hollow test"


# ══════════════════════════════ AC-24 — gap motivation-only / honesty (§11) ══════════════════════

def test_section11_gap_honesty_and_no_auto_resolve():
    """[AC-24 GREEN] 실 계약 §11 정직성 — AC-23/24 anchor + drift FACT + '자동 해소 주장 안 함'
    + landing≠activation(gap motivation-only).

    RTM proxy-anchor 해소: doc-lint self-test §11 (d) 의 check_honesty 를 실 계약에 대해 호출.
    """
    body = _contract_body()
    section11 = ces.extract_ac23_narrative(body)
    assert section11, "§11 정직성 섹션 파싱 실패"
    violations: list = []
    ces.check_honesty(section11, violations)
    assert violations == [], f"실 계약 §11 honesty 위반: {violations}"
    # AC-24 전용 anchor: gap motivation-only + landing≠activation 정직 서술 present
    assert "AC-24" in section11, "§11 AC-24 gap-honesty anchor 부재"
    assert "landing" in section11 and "activation" in section11, (
        "§11 landing≠activation 정직 서술 부재 (gap motivation-only over-claim 방지)"
    )


def test_stripping_honesty_narrative_triggers_red():
    """[AC-24 discriminating / RC4 재사용] AC-23 + '자동 해소' strip → honesty RED (hollow 아님 증명)."""
    body = _contract_body()
    section11 = ces.extract_ac23_narrative(body)
    mutated = re.sub(r"자동\s*해소", "XXX", section11).replace("AC-23", "XXX")
    violations: list = []
    ces.check_honesty(mutated, violations)
    assert violations, "AC-23/자동해소 strip 에도 RED 미발화 — vacuous/hollow test"
