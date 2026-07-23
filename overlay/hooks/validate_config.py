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


def _is_bool(v: Any) -> bool:
    return isinstance(v, bool)


def _is_number(v: Any) -> bool:
    """int 또는 float (bool 제외 — YAML 에서 true/false 가 int 로 오인되지 않게)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_list_of_str_or_empty(v: Any) -> bool:
    """list of non-empty str (빈 list 허용 — atlassian.mirror_targets 등)."""
    return isinstance(v, list) and all(isinstance(x, str) and len(x) > 0 for x in v)


def _is_mapping_of_mappings(v: Any) -> bool:
    """dict whose every value is also a dict — 자식키는 자유(OPEN_MAPPING)이나 값은 mapping 형태.

    infra_resources.execution_units 용 — 동적 unit *이름*은 OPEN_MAPPING 으로 자유 허용하되,
    각 unit 값의 *형태*(required[]/resource_modes{})는 mapping 이어야 함을 강제한다.
    unit 값이 str/scalar/list 면 malformed (silent-pass 클래스 폐쇄 — bare `dict` type_check 시
    isinstance(v, dict) 만 봐 자식 값 형태를 안 봄).
    깊은 semantic(required[] 원소 존재·resource-id 유효성 등)은 D1 소관
    (scripts/lib/check_infra_manifest_schema.py) — 여기선 값 mapping-ness 만.
    """
    return isinstance(v, dict) and all(isinstance(u, dict) for u in v.values())


def _is_per_doc_type_override(v: Any) -> bool:
    """atlassian.confluence.per_doc_type_override — OPEN MAPPING.

    arbitrary doc-type key (adr / change-plan / story / ...) → dict 값.
    각 값은 optional `parent_page_id` (str) 등 자식을 가질 수 있다 (자식 키 자유).
    SHAPE 만 검증: dict 이고, 모든 값이 dict 여야 한다 (string 등 비-dict 값은 malformed).

    Schema SSOT: docs/project-config-schema.md §atlassian per_doc_type_override (~L503,
    `per_doc_type_override: <map>` — 예: {adr: {parent_page_id: "12345"}}).
    """
    if not isinstance(v, dict):
        return False
    for value in v.values():
        if not isinstance(value, dict):
            return False
    return True


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


def _is_list_of_responsibility_entries(v: Any) -> bool:
    """list of dict, each = 1 책임 배치 entry; 4 필수 필드 + unknown child key reject.

    Schema SSOT: docs/project-config-schema.md repo_topology + ADR-131 §결정2 (4 메타불변식 schema layer).
    - responsibility: required non-empty string
    - owner_repo: required non-empty string (메타불변식 ①: 정확히 1 소유레포 — 단일 string field 라 구조적 충족)
    - rationale: required non-empty string
    - linked_artifact: required list of non-empty str, len>=1 (메타불변식 ④ — 빈 list = 무효)
    - 위 4 키 외 자식 키 = unknown reject (per-entry fixed shape).
    NOTE: cross-entry 고아/중복 검사는 Story 2 carrier — 여기서는 per-entry 구조만 검증.
    """
    if not isinstance(v, list):
        return False
    allowed = {"responsibility", "owner_repo", "rationale", "linked_artifact"}
    for entry in v:
        if not isinstance(entry, dict):
            return False
        # required non-empty str: responsibility / owner_repo / rationale
        for field in ("responsibility", "owner_repo", "rationale"):
            if not _is_str(entry.get(field)):
                return False
        # required: linked_artifact (list of non-empty str, len>=1)
        if "linked_artifact" not in entry:
            return False
        linked = entry["linked_artifact"]
        if not _is_list_of_str(linked) or len(linked) < 1:
            return False
        # unknown child key reject (4 키만 허용)
        for key in entry:
            if key not in allowed:
                return False
    return True


def _is_list_of_marker_entries(v: Any) -> bool:
    """list of dict, each = 1 책임 마커 entry (L1 코드→책임); path/responsibility 필수 + repo 선택.

    Schema SSOT: docs/project-config-schema.md §repo_topology.responsibility_markers +
      ADR-131 Amendment 1 (CFP-2428, Epic CFP-2418 deferred FU — declared-marker layer L1).
    - path: required non-empty string (경로 또는 module glob — 파일별 주석 아님, polyglot-safe AC-5)
    - responsibility: required non-empty string (join-key — repo_topology.responsibilities[].responsibility
        byte-identical 동일 namespace 의무 AC-1; 의미 내용 검사 안 함)
    - repo: optional non-empty string (지정 시 불일치(b) 검사 대상, 미지정 시 비대상 — 역방향 추론 안 함)
    - 위 3 키 외 자식 키 = unknown reject (per-entry fixed shape).
    NOTE: cross-entry drift 3종(unmarked/불일치/stale)·join-key 일관성 검사는 drift 게이트 carrier
      (scripts/lib/check_responsibility_marker_drift.py) — 여기서는 per-entry 구조만 검증.
    미주입/빈맵 tolerate (optional block — drift fix 선례, L2 _is_list_of_responsibility_entries 동형).
    """
    if not isinstance(v, list):
        return False
    allowed = {"path", "responsibility", "repo"}
    for entry in v:
        if not isinstance(entry, dict):
            return False
        # required non-empty str: path / responsibility
        for field in ("path", "responsibility"):
            if not _is_str(entry.get(field)):
                return False
        # optional: repo (지정 시 non-empty str)
        if "repo" in entry and not _is_str(entry["repo"]):
            return False
        # unknown child key reject (3 키만 허용)
        for key in entry:
            if key not in allowed:
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
    # CFP-658 Phase 2 / ADR-027 Amendment 2 §결정 6.A — fallback_mode enum
    # Trigger (A): enterprise GitHub Actions default_workflow_permissions:read 차단 환경
    # Trigger (C): Issue 발의자 ad-hoc override (`fallback:manual` label, 우선순위 (C) > (A))
    # Default = "auto" (field 부재 시 적용, 에러 없음)
    ("bootstrap.fallback_mode", False,
     lambda v: isinstance(v, str) and v in ("auto", "action_blocked"),
     "bootstrap.fallback_mode ('auto' | 'action_blocked'), optional, default 'auto' — "
     "ADR-027 Amendment 2 §결정 6.A. 'action_blocked' = enterprise Actions 차단 환경 "
     "agent direct write fallback path 활성화"),
    # CFP-114 / ADR-029 — progress narration verbosity
    ("progress_narration_verbosity", False, _is_progress_narration_verbosity,
     "progress_narration_verbosity ('full' | 'lane_only'), optional, default 'full'"),
    # CFP-128 / ADR-033 — Docker-first Infra Engineering (infra_strategy enum)
    ("infra_strategy", False, lambda v: isinstance(v, str) and v in ("docker_first", "legacy_systemd", "none"),
     "infra_strategy ('docker_first' | 'legacy_systemd' | 'none'), optional, default 'docker_first'"),
    ("infra_strategy_extras", False, dict, "infra_strategy_extras section (mapping), optional"),
    ("infra_strategy_extras.k8s_preset_enabled", False, lambda v: isinstance(v, bool),
     "infra_strategy_extras.k8s_preset_enabled (boolean, default false), optional"),
    # CFP-2700 / ADR-157 §결정1 — 인프라 자원 선언 manifest (2-plane, D5 consumer 전파).
    # 문서 스키마(project-config-schema.md §infra_resources)를 런타임 검증기에 배선(선언≠배선 갭 정정).
    # 깊은 의미검증(id/canonical_env 필수·자원 커버리지)은 dedicated validator 소관
    # (scripts/lib/check_infra_manifest_schema.py D1 + D3 scanner) — 여기선 2-plane 구조 shape 만.
    ("infra_resources", False, dict, "infra_resources section (mapping), optional — CFP-2700/ADR-157 2-plane manifest"),
    # resources = list predicate (bare builtin `list` 은 validate() 에서 predicate 가 아닌 생성자
    # 로 호출돼 scalar/None 크래시·str silent-pass·[] false-reject 를 유발 — G4 FIX iter2).
    ("infra_resources.resources", False, lambda v: isinstance(v, list), "infra_resources.resources (list of resource dicts: id/canonical_env/aliases), optional"),
    # execution_units = OPEN_MAPPING(동적 unit 이름 자유) + 값-형태(각 unit 값이 mapping) 강제.
    ("infra_resources.execution_units", False, _is_mapping_of_mappings, "infra_resources.execution_units (mapping: unit-name → required[]/resource_modes{} mapping), optional — 동적 unit 키 (OPEN_MAPPING), 각 unit 값은 mapping"),
    ("infra_resources.startup_validation", False, dict, "infra_resources.startup_validation section (mapping), optional — D2 채택 선언"),
    ("infra_resources.startup_validation.adopted", False, lambda v: isinstance(v, bool), "infra_resources.startup_validation.adopted (boolean), optional"),
    ("infra_resources.startup_validation.reason", False, _is_str, "infra_resources.startup_validation.reason (string, adopted=false 시 사유), optional"),
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
    # CFP-820 / ADR-063 Amendment 5 §결정 15 — 3-way version atomic invariant consumer pin
    # Consumer 가 version_pin 블록을 선언하면 `check-3way-version-parity.sh` 가
    # publisher(plugin.json) ↔ registry(marketplace.json) ↔ consumer(project.yaml) 3-way 검증.
    # 블록 부재 = warning-first (exit 0, orthogonality invariant — PIN_ABSENT ≠ PIN_MISMATCH).
    ("codeforge.version_pin", False, dict, "codeforge.version_pin section (mapping), optional — "
     "ADR-063 Amendment 5 §결정 15 consumer side of 3-way version atomic invariant"),
    ("codeforge.version_pin.version", False, _is_str,
     "codeforge.version_pin.version (non-empty string, e.g. '5.82.0'), optional — "
     "must match publisher plugin.json + registry marketplace.json version"),
    # CFP-609 / ADR-064 Amendment 1 — Parallel Dispatch Protocol consumer overlay
    # SSOT: docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md (kind:registry)
    # ADR-064 §결정 7 ratchet — evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무).
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

    # -------------------------------------------------------------------------
    # CFP — consumer-guide 가 안내하지만 SCHEMA_RULES 미등록이던 5 블록 (doc↔validator drift 수정)
    # 문서(813줄)·consumer-guide 가 사용을 안내하는데도 _check_unknown_keys 가 exit 4 → SessionStart abort.
    # 문서 스키마대로 OPTIONAL(required=False) 등록. 자식 키도 명시 등록 → 문서 외 자식 키는 여전히 unknown reject.
    # 모든 블록 = consumer-authored only (§4b write 금지 invariant 보존, codeforge agent read-only).
    # -------------------------------------------------------------------------

    # [선택] aggregate_arch — AggregateArchitect deputy applicability + migration tool
    # Schema SSOT: docs/project-config-schema.md §aggregate_arch (~L229-345) · consumer-guide §1m
    ("aggregate_arch", False, dict, "aggregate_arch section (mapping), optional"),
    ("aggregate_arch.applicable", False, _is_bool,
     "aggregate_arch.applicable (boolean, default true — AggregateArch deputy 활성 여부), optional"),
    ("aggregate_arch.migration_tool", False,
     lambda v: isinstance(v, str) and v in (
         "alembic", "prisma-migrate", "typeorm", "goose", "golang-migrate",
         "flyway", "liquibase", "sqlx-migrate", "custom"),
     "aggregate_arch.migration_tool (9-enum: alembic|prisma-migrate|typeorm|goose|"
     "golang-migrate|flyway|liquibase|sqlx-migrate|custom, default alembic), optional"),

    # [선택] atlassian — Atlassian suite 재결합 (CFP-1215 / ADR-100 / ADR-111)
    # Schema SSOT: docs/project-config-schema.md §atlassian (~L468-555) · consumer-guide §1o
    ("atlassian", False, dict, "atlassian section (mapping), optional"),
    ("atlassian.enabled", False, _is_bool, "atlassian.enabled (boolean), optional"),
    ("atlassian.confluence", False, dict, "atlassian.confluence section (mapping), optional"),
    ("atlassian.confluence.base_url", False, _is_str,
     "atlassian.confluence.base_url (non-empty string, NOT secret), optional"),
    ("atlassian.confluence.space_key", False, _is_str,
     "atlassian.confluence.space_key (non-empty string, NOT secret), optional"),
    ("atlassian.confluence.api_token_env", False, _is_str,
     "atlassian.confluence.api_token_env (env-key reference string — 평문 token 금지), optional"),
    ("atlassian.confluence.user_email_env", False, _is_str,
     "atlassian.confluence.user_email_env (env-key reference string), optional"),
    ("atlassian.confluence.instance", False, _is_str,
     "atlassian.confluence.instance (non-empty string, NOT secret), optional"),
    ("atlassian.confluence.homepage_id", False, _is_str,
     "atlassian.confluence.homepage_id (string page ID), optional"),
    ("atlassian.confluence.mirror_targets", False,
     lambda v: isinstance(v, list) and all(
         isinstance(x, str) and x in (
             "adr", "architecture_doc", "change_plan",
             "domain_knowledge", "orchestrator_playbook") for x in v),
     "atlassian.confluence.mirror_targets (list, closed-enum 5: adr|architecture_doc|"
     "change_plan|domain_knowledge|orchestrator_playbook), optional"),
    # OPEN MAPPING — 자식 doc-type 키(adr/change-plan/story/...) 자유.
    # _check_unknown_keys 가 OPEN_MAPPING_PATHS 로 재귀를 건너뛴다 (자식키 EXIT 4 차단).
    # type_check = SHAPE 검증 (dict-of-dict). Schema SSOT: project-config-schema.md ~L503.
    ("atlassian.confluence.per_doc_type_override", False, _is_per_doc_type_override,
     "atlassian.confluence.per_doc_type_override (open mapping: doc-type → {parent_page_id: str}), optional"),
    ("atlassian.jira", False, dict, "atlassian.jira section (mapping), optional"),
    ("atlassian.jira.project_key", False, _is_str,
     "atlassian.jira.project_key (non-empty string, NOT secret), optional"),

    # [선택] runtime — Windows external session auto-resume (CFP-1355 / ADR-110)
    # Schema SSOT: consumer-guide §1j (~L347-422). project.yaml: runtime.auto_resume.enabled
    ("runtime", False, dict, "runtime section (mapping), optional"),
    ("runtime.auto_resume", False, dict, "runtime.auto_resume section (mapping), optional"),
    ("runtime.auto_resume.enabled", False, _is_bool,
     "runtime.auto_resume.enabled (boolean — Windows auto-resume opt-in), optional"),

    # [선택] security — consumer 자체 cross-repo PAT rotation cadence override (ADR-066 §결정 7)
    # Schema SSOT: consumer-guide §1g (~L242). 강화 방향만 (90 days 미만 short rotation 허용).
    ("security", False, dict, "security section (mapping), optional"),
    ("security.pat_rotation_cadence_days", False, _is_int,
     "security.pat_rotation_cadence_days (int days — PAT rotation cadence override, 강화 방향만), optional"),

    # -------------------------------------------------------------------------
    # CFP-2419 / ADR-131 — doc↔validator drift 수정: repo_topology 신규 optional 블록
    # docs/project-config-schema.md 가 repo_topology 사용을 안내하는데 validator 미등록 →
    # _check_unknown_keys 가 exit 4 → SessionStart abort. 문서 스키마대로 OPTIONAL 등록.
    # layer 분리: applicable=false/absent = 메타불변식 게이트 PASS (비차단). consumer-authored only.
    # 주의: 본 블록 = SCHEMA SELF-CONSISTENCY 만 — 고아/중복/cross-repo 메타불변식 hard-block 은 Story 2.
    # -------------------------------------------------------------------------

    # [선택] repo_topology — Cross-repo 책임 배치 토폴로지 SSOT
    # Schema SSOT: docs/project-config-schema.md §repo_topology (~L585-597) · consumer-authored
    ("repo_topology", False, dict,
     "repo_topology section (mapping), optional — CFP-2419 / ADR-131 cross-repo 책임 배치 토폴로지 SSOT"),
    ("repo_topology.applicable", False, _is_bool,
     "repo_topology.applicable (bool, default false — false/absent = 메타불변식 게이트 PASS), optional"),
    ("repo_topology.responsibilities", False, _is_list_of_responsibility_entries,
     "repo_topology.responsibilities (list of {responsibility, owner_repo, rationale, linked_artifact[>=1]} dicts), optional — "
     "applicable=true 시 per-consumer 책임 배치 맵"),

    # [선택] responsibility_markers — declared-marker layer L1 코드→책임 (CFP-2428 / ADR-131 Amendment 1)
    # Schema SSOT: docs/project-config-schema.md §repo_topology.responsibility_markers · consumer-authored
    # 미주입/빈맵 = PASS (fail-open, L2 responsibilities[] 동형). drift 3종 hard-block 은 별 게이트 carrier.
    ("repo_topology.responsibility_markers", False, _is_list_of_marker_entries,
     "repo_topology.responsibility_markers (list of {path, responsibility, repo?} dicts), optional — "
     "applicable=true 시 per-repo 코드→책임 마커 manifest (join-key=responsibility byte-identical namespace)"),
]


# OPEN MAPPING parent paths — 자식 키가 schema-free arbitrary mapping 인 경로.
# _check_unknown_keys 가 이 경로 아래로는 재귀하지 않는다 (자식 키를 unknown 으로 reject 금지).
# SHAPE 검증은 해당 path 의 SCHEMA_RULES type_check 가 담당 (예: _is_per_doc_type_override).
# 신규 open mapping 추가 시 여기에 dotted-path 등록 + SCHEMA_RULES 에 shape type_check 등록.
OPEN_MAPPING_PATHS: set[str] = {
    "atlassian.confluence.per_doc_type_override",
    "infra_resources.execution_units",
}


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
        # OPEN MAPPING — 자식 doc-type 키 자유. 재귀 건너뜀 (SHAPE 는 type_check 가 검증).
        if full_path in OPEN_MAPPING_PATHS:
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
