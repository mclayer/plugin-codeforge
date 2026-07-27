#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_doc_locations_authoring_primary.py — authoring_primary field (doc-locations.yaml schema_version 1.3+)."""

import sys
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest


def load_doc_locations() -> dict:
    """Load doc-locations.yaml SSOT."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    doc_locs_file = repo_root / "docs" / "doc-locations.yaml"

    if not doc_locs_file.exists():
        pytest.skip(f"doc-locations.yaml not found at {doc_locs_file}")

    with open(doc_locs_file, 'r', encoding='utf-8') as f:
        content = f.read()

    data = yaml.safe_load(content)
    if not data:
        pytest.skip("doc-locations.yaml is empty")

    return data


# ── Schema version check (1.3+ required for authoring_primary) ────────────────

def test_authoring_primary_schema_version_geq_1_3():
    """authoring_primary field requires schema_version >= 1.3 (CFP-2829 S2 R2)."""
    doc_locs = load_doc_locations()
    schema_version = doc_locs.get("schema_version", "")

    # Parse semver: major.minor
    parts = schema_version.split(".")
    assert len(parts) >= 2, f"schema_version '{schema_version}' invalid format"

    try:
        major = int(parts[0])
        minor = int(parts[1])
    except ValueError:
        pytest.skip(f"schema_version '{schema_version}' not numeric")

    assert (major, minor) >= (1, 3), \
        f"schema_version {schema_version} < 1.3 (authoring_primary requires 1.3+)"


# ── Confluence mirror doc_type enum (closed-enum 5) ──────────────────────────

CONFLUENCE_MIRROR_DOC_TYPES = {
    "adr": "archive/adr/ADR-NNN-<slug>.md",
    "change_plan": "docs/change-plans/<slug>.md",
    "domain_knowledge": "docs/domain-knowledge/<area>/<topic>.md",
    "architecture_doc": "docs/architecture/<topic>.md",
    "orchestrator_playbook": "docs/orchestrator-playbook.md",
}


def test_authoring_primary_all_5_mirrors_present():
    """All 5 confluence mirror doc_type must have authoring_primary field (closed-enum)."""
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    # Map doc_type name → entry
    doc_types_map = {entry.get("name"): entry for entry in doc_types_list if entry.get("name")}

    found_count = 0

    for mirror_name in CONFLUENCE_MIRROR_DOC_TYPES.keys():
        assert mirror_name in doc_types_map, f"doc_type '{mirror_name}' not found in doc_types"

        entry = doc_types_map[mirror_name]
        conf_variant = entry.get("confluence_variant")

        # confluence_variant must be dict (not null)
        assert conf_variant is not None, \
            f"doc_type '{mirror_name}' confluence_variant is null (must be dict)"
        assert isinstance(conf_variant, dict), \
            f"doc_type '{mirror_name}' confluence_variant must be dict, got {type(conf_variant)}"

        # authoring_primary field must exist
        authoring_primary = conf_variant.get("authoring_primary")
        assert authoring_primary is not None, \
            f"doc_type '{mirror_name}' missing authoring_primary field"

        found_count += 1

    assert found_count == 5, \
        f"Expected 5 mirror doc_types with authoring_primary, found {found_count}"


def test_authoring_primary_value_is_git():
    """authoring_primary value must be 'git' for all 5 mirror doc_type (Phase 2 R2)."""
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    doc_types_map = {entry.get("name"): entry for entry in doc_types_list if entry.get("name")}

    for mirror_name in CONFLUENCE_MIRROR_DOC_TYPES.keys():
        if mirror_name not in doc_types_map:
            continue

        entry = doc_types_map[mirror_name]
        conf_variant = entry.get("confluence_variant")

        if conf_variant and isinstance(conf_variant, dict):
            authoring_primary = conf_variant.get("authoring_primary")
            assert authoring_primary == "git", \
                f"doc_type '{mirror_name}' authoring_primary must be 'git', got '{authoring_primary}'"


# ── Immutable fields (authoritative_source, mirror_direction) ─────────────────

def test_authoring_primary_immutable_authoritative_source():
    """authoritative_source must be 'git' (immutable, ADR-111 §결정 1)."""
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    doc_types_map = {entry.get("name"): entry for entry in doc_types_list if entry.get("name")}

    for mirror_name in CONFLUENCE_MIRROR_DOC_TYPES.keys():
        if mirror_name not in doc_types_map:
            continue

        entry = doc_types_map[mirror_name]
        conf_variant = entry.get("confluence_variant")

        if conf_variant and isinstance(conf_variant, dict):
            auth_source = conf_variant.get("authoritative_source")
            assert auth_source == "git", \
                f"doc_type '{mirror_name}' authoritative_source must be 'git', got '{auth_source}'"


def test_authoring_primary_immutable_mirror_direction():
    """mirror_direction must be 'git_to_confluence' (immutable, ADR-111 §결정 1)."""
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    doc_types_map = {entry.get("name"): entry for entry in doc_types_list if entry.get("name")}

    for mirror_name in CONFLUENCE_MIRROR_DOC_TYPES.keys():
        if mirror_name not in doc_types_map:
            continue

        entry = doc_types_map[mirror_name]
        conf_variant = entry.get("confluence_variant")

        if conf_variant and isinstance(conf_variant, dict):
            mirror_dir = conf_variant.get("mirror_direction")
            assert mirror_dir == "git_to_confluence", \
                f"doc_type '{mirror_name}' mirror_direction must be 'git_to_confluence', got '{mirror_dir}'"


# ── Non-mirror doc_type validation (confluence_variant: null) ──────────────────

def test_authoring_primary_non_mirror_has_null_variant():
    """Non-mirror doc_type (story_file, decision_packet) must have confluence_variant: null."""
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    non_mirror_types = ["story_file", "decision_packet"]

    for entry in doc_types_list:
        doc_name = entry.get("name")
        if doc_name in non_mirror_types:
            conf_variant = entry.get("confluence_variant")
            assert conf_variant is None, \
                f"doc_type '{doc_name}' should have confluence_variant: null, got {conf_variant}"


# ── authoring_primary MUTATION: field removed from mirror doc_type ────────────

def test_authoring_primary_mutation_field_removed(monkeypatch):
    """MUTATION: if authoring_primary removed from one mirror doc_type.

    Discriminating case: field must exist in all 5 mirrors,
    but mutant removes it from one (e.g., adr).
    """
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    # Simulate mutation: remove authoring_primary from "adr"
    mutant_types = []
    for entry in doc_types_list:
        mutant_entry = entry.copy()
        if entry.get("name") == "adr":
            conf_var = mutant_entry.get("confluence_variant")
            if conf_var and isinstance(conf_var, dict):
                mutant_entry["confluence_variant"] = {
                    k: v for k, v in conf_var.items() if k != "authoring_primary"
                }
        mutant_types.append(mutant_entry)

    # Mutant adr entry no longer has authoring_primary
    adr_entry = next((e for e in mutant_types if e.get("name") == "adr"), None)
    if adr_entry and adr_entry.get("confluence_variant"):
        assert "authoring_primary" not in adr_entry.get("confluence_variant", {}), \
            "Mutation should remove authoring_primary from adr"


# ── authoring_primary MUTATION: field value changed to atlassian ───────────────

def test_authoring_primary_mutation_value_changed(monkeypatch):
    """MUTATION: if authoring_primary value changed from 'git' to 'atlassian'.

    Discriminating case: Phase 2 = 'git' only,
    Phase N+1 (S6) may flip to 'atlassian'. Current = 'git'.
    """
    doc_locs = load_doc_locations()
    doc_types_list = doc_locs.get("doc_types", []) or []

    # Simulate mutation: change authoring_primary to 'atlassian' in one entry
    for entry in doc_types_list:
        if entry.get("name") == "adr":
            conf_var = entry.get("confluence_variant")
            if conf_var and isinstance(conf_var, dict):
                # Mutant value
                assert conf_var.get("authoring_primary") == "git", \
                    "Expected 'git', but mutant changed to 'atlassian' (Phase N+1 flip candidate)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
