"""AC-6 — N9 schema amendment 정합 (23-field 계약↔runtime parity).

Change Plan §8.1.1 RTM AC-6 (4 named test). phase1.
  - 23-field 계약↔runtime parity (초과/누락 0).
  - additive MINOR backward-compat (v1.0 19-field reader 가 4 신규 field skip).
  - ★F-CR-015: 기존 19-field **순서** 불변 + 계약 §2 표 실순서 parity (set 비교 무방어 축).
  - ADR-043 Allow-list amendment 존재 (silent expansion 차단).

[RED-until-landed] dev-core append_spawn_event.py _ROW_KEYS 19→23 확장 +
  spawn-event-v1 계약 Amendment 4 + ADR-043 Amendment (Phase 2 적용).
"""

from __future__ import annotations

from pathlib import Path

import append_spawn_event  # 실 production 모듈 (SSOT _ROW_KEYS)
import check_spawn_event_schema as _css  # 실 production §2 표 parser (재구현 금지 — ADR-140)
import _expect as _cf  # CONTRACT_19_FIELDS / NEW_4_FIELDS / CONTRACT_23_FIELDS

REPO_ROOT = Path(__file__).resolve().parents[3]
ADR_043 = REPO_ROOT / "archive" / "adr" / "ADR-043-codeforge-telemetry-privacy-policy.md"
CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "spawn-event-v1.md"


def test_ac6_contract_runtime_row_keys_parity_23field():
    """runtime _ROW_KEYS == 23-field 계약 set (초과/누락 0).

    [RED-until-landed: _ROW_KEYS 19→23 확장]
    additive: 기존 19 순서·의미 불변 + 4 신규(total_tokens/model/outcome/termination_cause) append.
    """
    runtime_keys = set(append_spawn_event._ROW_KEYS)
    expected = set(_cf.CONTRACT_23_FIELDS)
    # 측정 assertion: 정확 일치 (초과/누락 0)
    # ★F-CR-018: 뒤따르던 issubset 2건 제거 — 정확일치(==)가 이미 양방향 포함을 함의하므로
    #   논리적 항진(사문) assertion 이었다. additive 성질은 아래 test_ac6_additive_minor_...
    #   (added == NEW_4) 와 test_ac6_row_keys_order_preserved_... (순서 축) 가 실제로 판정한다.
    assert runtime_keys == expected, (
        f"23-field parity 불일치:\n  누락: {expected - runtime_keys}\n  초과: {runtime_keys - expected}"
    )


def test_ac6_additive_minor_v10_reader_skip():
    """additive MINOR backward-compat — v1.0 19-field reader 가 4 신규 field skip 가능.

    [RED-until-landed: 23-field runtime]
    additive 성질: runtime keys ⊇ 19 core (제거·재배열 0), 신규 = keys − 19core = 4 optional.
    v1.0 reader 가 19 core 만 읽고 4 신규를 무시해도 valid.
    """
    runtime_keys = set(append_spawn_event._ROW_KEYS)
    core_19 = set(_cf.CONTRACT_19_FIELDS)
    # 측정 assertion: 19 core 는 여전히 subset (제거·rename 0 → backward-compat)
    assert core_19.issubset(runtime_keys), "v1.0 19-field 는 제거·rename 없이 보존 (reader skip 가능)"
    # 신규 field 는 정확히 4 (additive only, 초과 확장 아님)
    added = runtime_keys - core_19
    assert added == set(_cf.NEW_4_FIELDS), (
        f"신규 field 는 정확히 4 additive 여야 함 (v1.0 reader skip 대상), got {added}"
    )


def test_ac6_row_keys_order_preserved_19_then_4():
    """(★F-CR-015, disc) 기존 19-field **순서** 불변 + 신규 4 는 그 뒤 (set 비교 무방어 축 봉인).

    Change Plan §11.1 불변식 = "기존 19 field 순서·의미 불변". 그런데 기존 parity 검증은 전부
    **set 비교**라 19 field 를 뒤섞어도(예: actor 와 event_id 자리 교환) 전부 GREEN 이었다.
    JSONL row 는 dict 라 key 순서가 의미론적 계약(§2 표 순서 = reader/문서 대조 순서)이며,
    순서 drift 는 diff·문서 대조·additive 판정을 모두 흔든다.

    doc↔runtime 순서 parity 는 계약 §2 표를 **실파싱**해 대조한다 —
    production parser `check_spawn_event_schema.parse_section2_fields` REUSE (ADR-140:
    테스트가 표 파서를 재구현하지 않는다).
    mutation: _ROW_KEYS 앞 19 순서 교환 / 신규 4 를 중간 삽입 / 계약 표 행 순서 변경 → RED.
    """
    row_keys = tuple(append_spawn_event._ROW_KEYS)
    # 측정 assertion (a): 앞 19 = 계약 원 순서 그대로 (list 순서 비교 — set 아님)
    assert row_keys[:19] == tuple(_cf.CONTRACT_19_FIELDS), (
        f"기존 19-field 순서 drift:\n  runtime: {row_keys[:19]}\n  contract: {tuple(_cf.CONTRACT_19_FIELDS)}"
    )
    # (b): 신규 4 는 그 뒤에 순서대로 append (중간 삽입 = 기존 순서 파괴)
    assert row_keys[19:] == tuple(_cf.NEW_4_FIELDS), (
        f"신규 4 field 는 19 뒤에 순서대로 와야 함(additive), got {row_keys[19:]}"
    )

    # (c): 계약 §2 표 실순서 ↔ runtime 순서 완전 일치 (doc-parse, 상수 대조 tautology 아님)
    fm, body = _css._split_frontmatter(CONTRACT.read_text(encoding="utf-8"))
    doc_order = tuple(name for name, _type in _css.parse_section2_fields(body))
    assert doc_order, "계약 §2 표 파싱 결과가 공집합 — 순서 대조가 vacuous (파서/표 형상 붕괴)"
    assert doc_order == row_keys, (
        f"계약 §2 표 순서 ↔ runtime _ROW_KEYS 순서 불일치:\n"
        f"  doc:     {doc_order}\n  runtime: {row_keys}"
    )


def test_ac6_allow_list_amendment_present():
    """ADR-043 Allow-list amendment 존재 — 4 신규 field 명시 (silent expansion 차단).

    [RED-until-landed: ADR-043 Amendment (CFP-2850) Phase 2 적용]
    """
    text = ADR_043.read_text(encoding="utf-8")
    # 측정 assertion: CFP-2850 amendment + 4 신규 field 명시
    assert "CFP-2850" in text, "ADR-043 에 CFP-2850 Allow-list amendment 등재 필요"
    for field in _cf.NEW_4_FIELDS:
        assert field in text, f"ADR-043 amendment 에 신규 field '{field}' 명시 필요 (Allow-list 확장)"
