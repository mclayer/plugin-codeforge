#!/usr/bin/env python3
"""
validate_config.py — `.claude/_overlay/project.yaml` schema validator

Usage:
    python3 validate_config.py <path/to/project.yaml>

Exit codes:
    0 — valid (or file absent — treated as warning)
    1 — usage error
    2 — dependency missing (PyYAML)
    3 — file present but malformed (YAML parse failure)
    4 — schema violation (missing required field, type mismatch)

Schema SSOT: docs/project-config-schema.md §2.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: PyYAML required. Install: pip install pyyaml\n")
    sys.exit(2)


# -----------------------------------------------------------------------------
# Schema definition (in code — intentionally no external JSON Schema dep)
# -----------------------------------------------------------------------------

# Each rule: (path, required, type_check, description)
#   path: dotted path e.g. "github.codeowners.architect_team"
#   required: bool
#   type_check: callable(value) -> bool  (True if type OK)
#   description: human-readable description


def _is_str(v: Any) -> bool:
    return isinstance(v, str) and len(v) > 0


def _is_list_of_str(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and len(x) > 0 for x in v)


SCHEMA_RULES: list[tuple[str, bool, Any, str]] = [
    # (path, required, type_check, description)
    ("project", True, dict, "project section (mapping)"),
    ("project.name", True, _is_str, "project.name (non-empty string)"),
    ("github", True, dict, "github section (mapping)"),
    ("github.org", True, _is_str, "github.org (non-empty string)"),
    ("github.repo", True, _is_str, "github.repo (non-empty string)"),
    ("github.default_branch", True, _is_str, "github.default_branch (non-empty string)"),
    ("github.pr_title_prefix_template", True, _is_str,
     "github.pr_title_prefix_template (non-empty string)"),
    ("github.story_key_prefix", True, _is_str,
     "github.story_key_prefix (non-empty string, e.g. 'TM')"),
    ("github.codeowners", True, dict, "github.codeowners section (mapping)"),
    ("github.codeowners.architect_team", True, _is_str,
     "github.codeowners.architect_team (non-empty string, e.g. '@acme/architects')"),
    ("github.codeowners.domain_expert_team", True, _is_str,
     "github.codeowners.domain_expert_team (non-empty string)"),
    ("github.discussions", True, dict, "github.discussions section (mapping)"),
    ("github.discussions.domain_kb_category", True, _is_str,
     "github.discussions.domain_kb_category (non-empty string)"),
    ("github.milestone", True, dict, "github.milestone section (mapping)"),
    ("github.milestone.epic_naming_pattern", True, _is_str,
     "github.milestone.epic_naming_pattern (non-empty string)"),
    ("labels", False, dict, "labels section (mapping), optional"),
    ("labels.components", False, _is_list_of_str,
     "labels.components (list of non-empty strings), optional"),
]


def _get_path(data: Any, dotted: str) -> tuple[bool, Any]:
    """Return (present, value). present=False if any intermediate missing."""
    cur = data
    for key in dotted.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return False, None
        cur = cur[key]
    return True, cur


def validate(data: Any) -> list[str]:
    """Return list of error messages. Empty = valid."""
    errors: list[str] = []

    if not isinstance(data, dict):
        errors.append("root is not a YAML mapping")
        return errors

    for path, required, type_check, description in SCHEMA_RULES:
        present, value = _get_path(data, path)
        if not present:
            if required:
                errors.append(f"missing required field: {path} — expected {description}")
            continue

        # present — type check
        if type_check is dict:
            if not isinstance(value, dict):
                errors.append(f"{path}: expected mapping, got {type(value).__name__}")
        elif callable(type_check):
            if not type_check(value):
                errors.append(f"{path}: type mismatch — expected {description}, got {value!r}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: validate_config.py <path/to/project.yaml>\n")
        return 1

    path = Path(sys.argv[1])

    if not path.exists():
        # Missing file is a warning, not an error — consumer may be in initial setup
        sys.stderr.write(
            f"[validate-config] WARN: {path} not found. "
            f"GitHub 워크플로우 기능이 제한됩니다. "
            f"overlay/_overlay/project.yaml.example을 복사해 시작하세요.\n"
        )
        return 0

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        sys.stderr.write(f"[validate-config] ERROR: {path} — YAML parse failure: {e}\n")
        return 3

    errors = validate(data)
    if errors:
        sys.stderr.write(f"[validate-config] ERROR: {path} schema violations:\n")
        for err in errors:
            sys.stderr.write(f"  - {err}\n")
        sys.stderr.write(
            "\n  Schema: docs/project-config-schema.md §2\n"
        )
        return 4

    sys.stderr.write(f"[validate-config] OK: {path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
