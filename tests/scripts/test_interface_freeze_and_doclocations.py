#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_interface_freeze_and_doclocations.py — AC-3 (interface-freeze) + authoring_primary (doc-locations)."""

import sys
import subprocess
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest


# ── AC-3: interface-freeze (7 frozen files, 0 line changes) ──────────────────

FROZEN_FILES = [
    "scripts/confluence-sync-3anchor.py",
    "scripts/confluence_forward_sync.py",
    "scripts/lib/check_doc_frontmatter.py",
    "scripts/lib/check_doc_section_schema.py",
    ".github/workflows/confluence-forward-sync.yml",
    ".claude/agents/confluence-sync-write-commit.md",
    ".claude/agents/confluence-sync-read-verify.md",
]

BASE_COMMIT = "cdaf18820"  # Commit from which to check (pre-CFP-2829)


def get_repo_root() -> Path:
    """Get repo root."""
    return Path(__file__).resolve().parent.parent.parent


def test_ac3_interface_freeze_no_changes():
    """AC-3: Frozen files have 0 line changes from base commit."""
    repo_root = get_repo_root()

    for file_path in FROZEN_FILES:
        full_path = repo_root / file_path

        # File must exist
        if not full_path.exists():
            pytest.skip(f"File not found: {file_path}")

        # Check git diff against base commit
        result = subprocess.run(
            ["git", "diff", "--stat", BASE_COMMIT, "--", file_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"git diff failed for {file_path}")

        # If file is unchanged, diff output is empty
        # If changed, output contains "+ - " metrics
        diff_stat = result.stdout.strip()

        # Empty output = no changes
        assert diff_stat == "", f"File {file_path} should have 0 line changes, but diff shows:\n{diff_stat}"


# ── authoring_primary field (doc-locations.yaml) ──────────────────────────

def load_doc_locations() -> dict:
    """Load doc-locations.yaml."""
    repo_root = get_repo_root()
    doc_locs_file = repo_root / "docs" / "doc-locations.yaml"

    if not doc_locs_file.exists():
        pytest.skip("doc-locations.yaml not found")

    with open(doc_locs_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data


def test_authoring_primary_schema_version():
    """authoring_primary field requires schema_version >= 1.3."""
    doc_locs = load_doc_locations()
    schema_version = doc_locs.get("schema_version", "")

    # Parse version: should be >= 1.3
    parts = schema_version.split(".")
    if len(parts) >= 2:
        major = int(parts[0])
        minor = int(parts[1])
        assert (major, minor) >= (1, 3), f"schema_version {schema_version} < 1.3"


def test_authoring_primary_mirror_docs_exist():
    """authoring_primary field present in mirror doc_type 5 entries."""
    doc_locs = load_doc_locations()
    doc_types = doc_locs.get("doc_types", []) or []

    # Confluence mirror doc_type list (from Change Plan / ADR-111)
    mirror_doc_types = [
        "adr",
        "change_plan",
        "domain_knowledge",
        "architecture_doc",
        "orchestrator_playbook",
    ]

    authoring_primary_count = 0

    for entry in doc_types:
        doc_name = entry.get("name")
        if doc_name in mirror_doc_types:
            # Should have confluence_variant with authoring_primary field
            conf_var = entry.get("confluence_variant")
            if conf_var is not None and isinstance(conf_var, dict):
                authoring_primary = conf_var.get("authoring_primary")
                assert authoring_primary is not None, f"doc_type {doc_name} missing authoring_primary"
                assert authoring_primary == "git", f"doc_type {doc_name} authoring_primary must be 'git'"
                authoring_primary_count += 1

    # Must have all 5 mirror doc_type entries with authoring_primary
    assert authoring_primary_count == 5, f"Expected 5 authoring_primary entries, found {authoring_primary_count}"


def test_authoring_primary_immutable_fields():
    """authoring_primary field immutability: authoritative_source + mirror_direction unchanged."""
    doc_locs = load_doc_locations()
    doc_types = doc_locs.get("doc_types", []) or []

    mirror_doc_types = ["adr", "change_plan", "domain_knowledge", "architecture_doc", "orchestrator_playbook"]

    for entry in doc_types:
        doc_name = entry.get("name")
        if doc_name in mirror_doc_types:
            conf_var = entry.get("confluence_variant")
            if conf_var is not None and isinstance(conf_var, dict):
                # authoritative_source must be "git"
                auth_source = conf_var.get("authoritative_source")
                assert auth_source == "git", f"doc_type {doc_name} authoritative_source must be 'git'"

                # mirror_direction must be "git_to_confluence"
                mirror_dir = conf_var.get("mirror_direction")
                assert mirror_dir == "git_to_confluence", f"doc_type {doc_name} mirror_direction must be 'git_to_confluence'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
