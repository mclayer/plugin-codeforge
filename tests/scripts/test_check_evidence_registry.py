#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_check_evidence_registry.py
CFP-881 Phase 2 / ADR-060 Amendment 26 §8.1 — evidence-registry-structure 게이트의 **명명 테스트**
(RTM authoritative). Change Plan §8.1 이 명명한 normative 테스트(AC-1/2/3/4/7b/9/11/12/13/14)가
여기서 **실 def**(stub 아님, mutation-verified RED)로 실재해야 게이트의 자기 Phase 2 PR 이
ac-traceability Hop1/Hop3(§8 ↔ 실 symbol, ast resolve)를 통과한다. 함수명은 §8.1 RTM 과 1:1 정합.

pytest 가 Python SSOT ``validate_registry`` / ``load_and_validate`` / ``_UniqueKeyLoader`` 를 **직접
import**(subprocess 아님) — tests/conftest.py 가 scripts/lib 를 sys.path 주입.

discriminating fixture: 각 fixture 는 정확히 1개 규칙만 위반 → 그 규칙 assertion off 시 fixture green
(clean mutation-kill). dup-key fixture(F5b/P2)는 captured-golden — canary/deployment 실 corruption
shape 를 firsthand 캡처(합성 아님).
"""
import os
from pathlib import Path

import pytest
import yaml

import check_evidence_registry as cer  # scripts/lib (conftest.py sys.path 주입)

# tests/scripts/ → tests/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_REGISTRY = REPO_ROOT / "docs" / "evidence-checks-registry.yaml"

# known 13-tuple (entry-name, key) — canary 7 + deployment 6 (§3.2 / firsthand
# git show origin/main:docs/evidence-checks-registry.yaml 재확인). identity(count 아님).
#   canary-compatibility-check: CFP-963 + CFP-991 병렬 collision → 7 key 2×
#   deployment-schema-check:     CFP-1117 + CFP-1059-S5 collision → 6 key 2× (modal_anti 부재)
KNOWN_DUP_LOCI = {
    ("canary-compatibility-check", "carrier_adr"),
    ("canary-compatibility-check", "introduced_by"),
    ("canary-compatibility-check", "introduced_date"),
    ("canary-compatibility-check", "modal_anti_pattern_dictionary"),
    ("canary-compatibility-check", "owner_adr"),
    ("canary-compatibility-check", "recurrence"),
    ("canary-compatibility-check", "status"),
    ("deployment-schema-check", "carrier_adr"),
    ("deployment-schema-check", "introduced_by"),
    ("deployment-schema-check", "introduced_date"),
    ("deployment-schema-check", "owner_adr"),
    ("deployment-schema-check", "recurrence"),
    ("deployment-schema-check", "status"),
}


def _write(tmp_path, text):
    p = tmp_path / "reg.yaml"
    p.write_text(text, encoding="utf-8", newline="\n")
    return str(p)


# ─────────────────────── AC-1 (F6): 파싱 실패 감지 + exit 1 ───────────────────

def test_tab_indent_parse_fails(tmp_path):
    # tab 들여쓰기 = YAML spec 금지 → ScannerError → validation FAIL(exit 1).
    path = _write(tmp_path, "schema_version: \"1.5\"\nentries:\n\t- name: a\n")
    result = cer.load_and_validate(path)
    assert result.parse_error is not None
    assert result.exit_code == 1


# ─────────────────────── AC-2 (F1): 최상위 allowlist orphan FAIL ──────────────

def test_toplevel_allowlist_rejects_orphan():
    # col-0 orphan: entry 내부여야 할 owner_adr 가 최상위로 승격 → allowlist 이탈.
    data = {
        "schema_version": "1.5",
        "introduced_by": "CFP-389",
        "last_updated": "2026-07-20",
        "entries": [{"name": "a", "current_tier": "warning"}],
        "owner_adr": "ADR-060",  # orphan 승격 키
    }
    problems = cer.validate_registry(data)
    assert any("allowlist" in p for p in problems)


# ─────────────────────── AC-3 (F2/F3/F3b): entries=list + name(non-empty)-dict ─

def test_entries_must_be_list():
    problems = cer.validate_registry({"entries": {"name": "a"}})
    assert any("list" in p for p in problems)


def test_entry_requires_name():
    problems = cer.validate_registry({"entries": [{"current_tier": "warning"}]})
    assert any("name 키 부재" in p for p in problems)


def test_empty_name_rejected():
    for bad in ("", "   ", None):
        problems = cer.validate_registry({"entries": [{"name": bad, "current_tier": "warning"}]})
        assert any("non-empty" in p for p in problems), "empty-name not rejected: %r" % bad


# ─────────────────────── AC-4 (F4): current_tier enum case-sensitive ──────────

def test_current_tier_enum_member():
    data = {"entries": [
        {"name": "a", "current_tier": "blocking"},   # prefix typo (enum 아님)
        {"name": "b", "current_tier": "Warning"},     # case boundary (case-sensitive)
    ]}
    problems = cer.validate_registry(data)
    assert sum("current_tier enum 이탈" in p for p in problems) == 2


# ─────────────────────── AC-7b (P1): clean self-inclusive PASS ────────────────

def test_gate_passes_on_clean_self_inclusive_fixture(tmp_path):
    path = _write(tmp_path,
        "schema_version: \"1.5\"\n"
        "introduced_by: CFP-389\n"
        "last_updated: 2026-07-20\n"
        "entries:\n"
        "  - name: some-existing-check\n"
        "    current_tier: warning\n"
        "  - name: evidence-registry-structure-verify\n"
        "    current_tier: warning\n")
    result = cer.load_and_validate(path)
    assert result.ok
    assert result.exit_code == 0
    assert result.entry_count == 2


# ─────────────────────── AC-9 (F7/F8): vacuous-PASS 회피 ──────────────────────

def test_empty_entries_not_vacuous():
    problems = cer.validate_registry({"entries": []})
    assert any("빈 리스트" in p for p in problems)


def test_none_document_fails():
    problems = cer.validate_registry(None)
    assert problems
    assert any("mapping" in p for p in problems)


def test_absent_entries_fails():
    problems = cer.validate_registry({"schema_version": "1.5"})
    assert any("entries 키 부재" in p for p in problems)


# ─────────────────────── AC-11 (F5): NEW dup-key on NEW entry ─────────────────

def test_new_duplicate_key_fails(tmp_path):
    path = _write(tmp_path,
        "schema_version: \"1.5\"\n"
        "introduced_by: CFP-881\n"
        "last_updated: 2026-07-20\n"
        "entries:\n"
        "  - name: brand-new-check\n"
        "    current_tier: warning\n"
        "    status: warning\n"
        "    status: Active\n")   # NEW dup key on NEW entry
    result = cer.load_and_validate(path)
    assert ("brand-new-check", "status") in result.dup_loci
    assert result.exit_code == 1


# ─────────────────────── AC-12 (P2/F5b): identity-oracle + (entry,key) 입도 ───

def test_live_registry_dup_key_loci_equals_known_set():
    # live registry 의 (entry-name, key) dup locus set == known 13-tuple (identity, not count).
    # 신규 (entry,key) dup 유입 → identity mismatch → self-test RED (regression fence).
    result = cer.load_and_validate(str(LIVE_REGISTRY))
    assert set(result.dup_loci) == KNOWN_DUP_LOCI, (
        "live dup-key locus set drift — got %s, known %s"
        % (sorted(result.dup_loci), sorted(KNOWN_DUP_LOCI))
    )
    # 계층 B(schema)는 clean — dup-key surface 외 orphan/name/tier problem 0.
    assert result.problems == [], "live registry schema problem: %s" % result.problems


def test_new_dup_key_on_grandfathered_entry_new_key_fails(tmp_path):
    # F5b captured-golden: canary-compatibility-check(grandfathered entry name)에 NEW dup key
    #   (description 2×) → (canary, description) ∉ known-13 → identity-oracle 이 잡는 신규 (entry,key).
    path = _write(tmp_path,
        "schema_version: \"1.5\"\n"
        "introduced_by: CFP-881\n"
        "last_updated: 2026-07-20\n"
        "entries:\n"
        "  - name: canary-compatibility-check\n"
        "    description: first-value\n"
        "    description: second-value\n"   # NEW dup key on grandfathered entry name
        "    current_tier: warning\n")
    result = cer.load_and_validate(path)
    assert ("canary-compatibility-check", "description") in result.dup_loci
    assert ("canary-compatibility-check", "description") not in KNOWN_DUP_LOCI
    assert result.exit_code == 1


# ─────────────────────── AC-13 (F9): name 전역 unique ─────────────────────────

def test_duplicate_entry_name_fails():
    data = {"entries": [
        {"name": "dup-name", "current_tier": "warning"},
        {"name": "dup-name", "current_tier": "warning"},
    ]}
    problems = cer.validate_registry(data)
    assert any("전역 중복" in p for p in problems)


# ─────────────────────── AC-14 (F-SEC): loader-safety (unsafe tag BLOCKED) ────

def test_unsafe_python_tag_blocked():
    payload = "!!python/object/apply:os.system ['echo pwned']"
    with pytest.raises(yaml.constructor.ConstructorError):
        yaml.load(payload, Loader=cer._UniqueKeyLoader)
    # loader-safety invariant (1): base = SafeLoader (Loader/FullLoader/UnsafeLoader swap 금지)
    assert issubclass(cer._UniqueKeyLoader, yaml.SafeLoader)
    # loader-safety invariant (2): add_constructor 0 (stock SafeLoader 대비 신규 constructor 부재)
    added = set(cer._UniqueKeyLoader.yaml_constructors) - set(yaml.SafeLoader.yaml_constructors)
    assert added == set()


# ─────────────────────── AC-5 (declared belt): file-absent meta-error exit 2 ──

def test_missing_registry_meta_error(tmp_path):
    result = cer.load_and_validate(str(tmp_path / "does-not-exist.yaml"))
    assert result.meta_message is not None
    assert result.exit_code == 2
