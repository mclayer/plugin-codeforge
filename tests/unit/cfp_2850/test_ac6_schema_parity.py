"""AC-6 — N9 schema amendment 정합 (23-field 계약↔runtime parity).

Change Plan §8.1.1 RTM AC-6 (3 named test). phase1.
  - 23-field 계약↔runtime parity (초과/누락 0).
  - additive MINOR backward-compat (v1.0 19-field reader 가 4 신규 field skip).
  - ADR-043 Allow-list amendment 존재 (silent expansion 차단).

[RED-until-landed] dev-core append_spawn_event.py _ROW_KEYS 19→23 확장 +
  spawn-event-v1 계약 Amendment 4 + ADR-043 Amendment (Phase 2 적용).
"""

from __future__ import annotations

from pathlib import Path

import append_spawn_event  # 실 production 모듈 (SSOT _ROW_KEYS)
import _expect as _cf  # CONTRACT_19_FIELDS / NEW_4_FIELDS / CONTRACT_23_FIELDS

REPO_ROOT = Path(__file__).resolve().parents[3]
ADR_043 = REPO_ROOT / "archive" / "adr" / "ADR-043-codeforge-telemetry-privacy-policy.md"


def test_ac6_contract_runtime_row_keys_parity_23field():
    """runtime _ROW_KEYS == 23-field 계약 set (초과/누락 0).

    [RED-until-landed: _ROW_KEYS 19→23 확장]
    additive: 기존 19 순서·의미 불변 + 4 신규(total_tokens/model/outcome/termination_cause) append.
    """
    runtime_keys = set(append_spawn_event._ROW_KEYS)
    expected = set(_cf.CONTRACT_23_FIELDS)
    # 측정 assertion: 정확 일치 (초과/누락 0)
    assert runtime_keys == expected, (
        f"23-field parity 불일치:\n  누락: {expected - runtime_keys}\n  초과: {runtime_keys - expected}"
    )
    # additive 불변식: 4 신규 field 존재 + 기존 19 보존
    assert set(_cf.NEW_4_FIELDS).issubset(runtime_keys), "4 신규 field 착지 필요"
    assert set(_cf.CONTRACT_19_FIELDS).issubset(runtime_keys), "기존 19-field 보존"


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


def test_ac6_allow_list_amendment_present():
    """ADR-043 Allow-list amendment 존재 — 4 신규 field 명시 (silent expansion 차단).

    [RED-until-landed: ADR-043 Amendment (CFP-2850) Phase 2 적용]
    """
    text = ADR_043.read_text(encoding="utf-8")
    # 측정 assertion: CFP-2850 amendment + 4 신규 field 명시
    assert "CFP-2850" in text, "ADR-043 에 CFP-2850 Allow-list amendment 등재 필요"
    for field in _cf.NEW_4_FIELDS:
        assert field in text, f"ADR-043 amendment 에 신규 field '{field}' 명시 필요 (Allow-list 확장)"
