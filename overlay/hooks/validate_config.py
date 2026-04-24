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

# Each rule: (path, required, type_check, extra_check)
#   path: dotted path e.g. "atlassian.confluence.space_key"
#   required: bool
#   type_check: callable(value) -> bool  (True if type OK)
#   extra_check: optional callable(value) -> str|None  (None if OK, else error msg)


def _is_str(v: Any) -> bool:
    return isinstance(v, str) and len(v) > 0


def _is_int_or_str(v: Any) -> bool:
    return (isinstance(v, int) and not isinstance(v, bool)) or (
        isinstance(v, str) and len(v) > 0
    )


def _is_list_of_str(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and len(x) > 0 for x in v)


def _is_map_str_to_int(v: Any) -> bool:
    return isinstance(v, dict) and all(
        isinstance(k, str) and isinstance(val, int) and not isinstance(val, bool)
        for k, val in v.items()
    )


SCHEMA_RULES: list[tuple[str, bool, Any, str]] = [
    # (path, required, type_check, description)
    ("project", True, dict, "project section (mapping)"),
    ("project.name", True, _is_str, "project.name (non-empty string)"),
    ("project.repo", True, _is_str, "project.repo (non-empty string)"),
    ("atlassian", True, dict, "atlassian section (mapping)"),
    ("atlassian.site", True, _is_str, "atlassian.site (non-empty string)"),
    ("atlassian.confluence", True, dict, "atlassian.confluence section (mapping)"),
    ("atlassian.confluence.space_key", True, _is_str, "atlassian.confluence.space_key (non-empty string)"),
    ("atlassian.confluence.stories_parent_page_id", True, _is_int_or_str,
     "atlassian.confluence.stories_parent_page_id (int or non-empty string)"),
    ("atlassian.confluence.domain_knowledge_parent_page_id", True, _is_int_or_str,
     "atlassian.confluence.domain_knowledge_parent_page_id (int or non-empty string)"),
    ("atlassian.confluence.adr_root_page_id", True, _is_int_or_str,
     "atlassian.confluence.adr_root_page_id (int or non-empty string)"),
    ("atlassian.jira", True, dict, "atlassian.jira section (mapping)"),
    ("atlassian.jira.project_key", True, _is_str, "atlassian.jira.project_key (non-empty string)"),
    ("atlassian.jira.transitions", False, _is_map_str_to_int,
     "atlassian.jira.transitions (map of string → int), optional"),
    ("github", True, dict, "github section (mapping)"),
    ("github.pr_title_prefix_template", True, _is_str,
     "github.pr_title_prefix_template (non-empty string)"),
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
            f"Atlassian/Jira 기능이 제한됩니다. "
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
