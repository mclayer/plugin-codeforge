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


def _is_progress_narration_verbosity(v: Any) -> bool:
    return isinstance(v, str) and v in ("full", "lane_only")


def _is_list_of_repo_entries(v: Any) -> bool:
    """list of dict, each with required name + role; role-conditional fields validated.

    Schema SSOT: docs/project-config-schema.md §2 + Change Plan CFP-342 §3.1.
    - name: required non-empty string
    - role: required enum ('governance' | 'implementation')
    - role=implementation 시 path + github required
    - optional: story_dir (str), components (list[str]), creates_repo_stories (bool)
    """
    if not isinstance(v, list):
        return False
    seen_names: set[str] = set()
    for entry in v:
        if not isinstance(entry, dict):
            return False
        # required: name
        if "name" not in entry or not isinstance(entry["name"], str) or not entry["name"]:
            return False
        # uniqueness invariant (§8.4 경계 조건)
        if entry["name"] in seen_names:
            return False
        seen_names.add(entry["name"])
        # required: role enum
        if "role" not in entry or entry["role"] not in ("governance", "implementation"):
            return False
        # role=implementation 시 required: path, github
        if entry["role"] == "implementation":
            if "path" not in entry or not isinstance(entry["path"], str) or not entry["path"]:
                return False
            if "github" not in entry or not isinstance(entry["github"], str) or not entry["github"]:
                return False
        # optional: story_dir (str)
        if "story_dir" in entry and not isinstance(entry["story_dir"], str):
            return False
        # optional: components (list of non-empty str)
        if "components" in entry and not _is_list_of_str(entry["components"]):
            return False
        # optional: creates_repo_stories (bool)
        if "creates_repo_stories" in entry and not isinstance(entry["creates_repo_stories"], bool):
            return False
    return True


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
    # CFP-1 Story 작성 의무 정책의 consumer overlay 확장 — 안전 방향(면제 추가)만 허용,
    # 강제 항목 축소(예: 가상의 'required_categories' 키)는 schema에 정의 안 해 unknown key reject로 자동 차단.
    ("story_cutoff", False, dict, "story_cutoff section (mapping), optional"),
    ("story_cutoff.additional_exempt_categories", False, _is_list_of_str,
     "story_cutoff.additional_exempt_categories (list of non-empty strings), optional"),
    # CFP-89 workflow_distribution overlay (CFP-97 schema fix — main blocker)
    # Path A (full) vs Path B (degraded) tracking. Schema SSOT: docs/project-config-schema.md §2.
    ("workflow_distribution", False, dict, "workflow_distribution section (mapping), optional"),
    ("workflow_distribution.mode", False, _is_str,
     "workflow_distribution.mode (string: 'full' | 'degraded'), optional"),
    ("workflow_distribution.missing_workflows", False, _is_list_of_str,
     "workflow_distribution.missing_workflows (list of non-empty strings), optional"),
    # CFP-103 bootstrap section (ADR-027) — bootstrap protocol settings
    ("bootstrap", False, dict, "bootstrap section (mapping), optional"),
    ("bootstrap.expected_workflows", False, _is_list_of_str,
     "bootstrap.expected_workflows (list of non-empty strings, override EXPECTED_WORKFLOWS_FULL), optional"),
    # CFP-127 / ADR-032 amendment 1 — strict mode opt-in
    ("bootstrap.strict_mode", False, lambda v: isinstance(v, bool),
     "bootstrap.strict_mode (boolean, default false — CFP-127 / ADR-032 strict mode opt-in priority 3 (yaml < env < CLI)), optional"),
    # CFP-114 / ADR-029 — progress narration verbosity
    ("progress_narration_verbosity", False, _is_progress_narration_verbosity,
     "progress_narration_verbosity ('full' | 'lane_only'), optional, default 'full'"),
    # CFP-128 / ADR-033 — Docker-first Infra Engineering (infra_strategy enum)
    ("infra_strategy", False, lambda v: isinstance(v, str) and v in ("docker_first", "legacy_systemd", "none"),
     "infra_strategy ('docker_first' | 'legacy_systemd' | 'none'), optional, default 'docker_first'"),
    ("infra_strategy_extras", False, dict, "infra_strategy_extras section (mapping), optional"),
    ("infra_strategy_extras.k8s_preset_enabled", False, lambda v: isinstance(v, bool),
     "infra_strategy_extras.k8s_preset_enabled (boolean, default false), optional"),
    # CFP-342 / ADR-050 — Multi-repo story key system (opt-in only)
    # codeforge.stories 블록 부재 시 single-repo flat 모드 유지 (기존 동작 보존).
    # 활성화 = codeforge.stories.repos[] 에 1+ entry 선언 시.
    ("codeforge", False, dict, "codeforge section (mapping), optional"),
    ("codeforge.stories", False, dict, "codeforge.stories section (mapping), optional"),
    ("codeforge.stories.hub", False, dict, "codeforge.stories.hub section (mapping), optional"),
    ("codeforge.stories.hub.key_pattern", False, _is_str,
     "codeforge.stories.hub.key_pattern (string), optional"),
    ("codeforge.stories.hub.story_dir", False, _is_str,
     "codeforge.stories.hub.story_dir (string), optional, default 'docs/stories'"),
    ("codeforge.stories.hub.template", False, _is_str,
     "codeforge.stories.hub.template (string), optional, default 'hub-story.md'"),
    ("codeforge.stories.repo_key_pattern", False, _is_str,
     "codeforge.stories.repo_key_pattern (string), optional"),
    ("codeforge.stories.counters", False, dict,
     "codeforge.stories.counters section (mapping), optional"),
    ("codeforge.stories.counters.path", False, _is_str,
     "codeforge.stories.counters.path (string), optional, default '.codeforge/counters.json'"),
    ("codeforge.stories.counters.lock", False,
     lambda v: isinstance(v, str) and v in ("file",),
     "codeforge.stories.counters.lock ('file'), optional"),
    ("codeforge.stories.repos", False, _is_list_of_repo_entries,
     "codeforge.stories.repos (list of repo entry dicts), optional — "
     "each entry requires name (str) + role ('governance'|'implementation'); "
     "role=implementation also requires path (str) + github (str)"),
    # CFP-609 / ADR-064 Amendment 1 — Parallel Dispatch Protocol consumer overlay
    # SSOT: docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md (kind:registry)
    # ADR-064 §결정 7 ratchet — 약화 방향 차단 (강화 방향만 허용).
    ("parallel_dispatch", False, dict, "parallel_dispatch section (mapping), optional"),
    ("parallel_dispatch.pl_autonomous_parallel_authority", False,
     lambda v: isinstance(v, str) and v in ("required", "optional", "disabled"),
     "parallel_dispatch.pl_autonomous_parallel_authority "
     "('required' | 'optional' | 'disabled'), optional, default 'required'"),
    ("parallel_dispatch.plan_dag_hint_required", False,
     lambda v: isinstance(v, bool),
     "parallel_dispatch.plan_dag_hint_required (boolean), optional, default true"),
    ("parallel_dispatch.dispatch_prompt_validation", False,
     lambda v: isinstance(v, str) and v in ("warn", "block"),
     "parallel_dispatch.dispatch_prompt_validation ('warn' | 'block'), optional, default 'warn'"),
    ("parallel_dispatch.wall_clock_measurement", False,
     lambda v: isinstance(v, bool),
     "parallel_dispatch.wall_clock_measurement (boolean), optional, default true"),
]


# Unknown key reject — schema 정의 외 키는 거부
# 강제 항목 축소·우회 시도(예: story_cutoff.required_categories) 자동 차단
def _build_allowed_keys_by_parent() -> dict[str, set[str]]:
    """SCHEMA_RULES에서 parent dotted-path → set of allowed child keys 매핑 생성."""
    table: dict[str, set[str]] = {}
    for path, *_ in SCHEMA_RULES:
        parts = path.split(".")
        for i in range(len(parts)):
            parent = ".".join(parts[:i])  # "" for root
            child = parts[i]
            table.setdefault(parent, set()).add(child)
    return table


ALLOWED_KEYS_BY_PARENT: dict[str, set[str]] = _build_allowed_keys_by_parent()


def _get_path(data: Any, dotted: str) -> tuple[bool, Any]:
    """Return (present, value). present=False if any intermediate missing."""
    cur = data
    for key in dotted.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return False, None
        cur = cur[key]
    return True, cur


def _check_unknown_keys(data: Any, parent_path: str = "") -> list[str]:
    """SCHEMA_RULES에 정의되지 않은 unknown key 탐색 (recursive)."""
    if not isinstance(data, dict):
        return []
    errors: list[str] = []
    allowed = ALLOWED_KEYS_BY_PARENT.get(parent_path, set())
    for key, value in data.items():
        full_path = f"{parent_path}.{key}" if parent_path else key
        if key not in allowed:
            errors.append(
                f"unknown key: {full_path} — schema에 정의되지 않음 "
                f"(allowed at '{parent_path or '<root>'}': {sorted(allowed) or '<none>'})"
            )
            continue
        # recurse into known nested dicts only
        if isinstance(value, dict):
            errors.extend(_check_unknown_keys(value, full_path))
    return errors


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

    # Unknown key reject — schema 정의 외 키는 거부 (강제 항목 축소·우회 시도 차단)
    errors.extend(_check_unknown_keys(data))

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
