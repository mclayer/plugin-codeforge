"""Tests for overlay/hooks/validate_config.py.

Schema reference: docs/project-config-schema.md §2.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

import validate_config as vc

HOOKS_DIR = Path(vc.__file__).resolve().parent
SCRIPT = HOOKS_DIR / "validate_config.py"


# -----------------------------------------------------------------------------
# Unit: validate() — returns list of error messages
# -----------------------------------------------------------------------------


def _minimal_valid_data() -> dict:
    return {
        "project": {"name": "x"},
        "github": {
            "org": "acme",
            "repo": "task-manager",
            "default_branch": "main",
            "pr_title_prefix_template": "[{key}] {title}",
            "story_key_prefix": "TM",
            "codeowners": {
                "architect_team": "@acme/architects",
                "domain_expert_team": "@acme/domain-experts",
            },
            "discussions": {"domain_kb_category": "Domain Q&A"},
            "milestone": {"epic_naming_pattern": "Epic-{key}-{slug}"},
        },
    }


class TestValidateMinimal:
    def test_minimal_required_fields_valid(self):
        assert vc.validate(_minimal_valid_data()) == []

    def test_with_optional_labels_valid(self):
        data = _minimal_valid_data()
        data["labels"] = {"components": ["api", "ui"]}
        assert vc.validate(data) == []

    def test_root_not_mapping_error(self):
        errs = vc.validate(["just a list"])
        assert errs == ["root is not a YAML mapping"]


class TestMissingRequiredFields:
    def test_missing_project_section(self):
        data = _minimal_valid_data()
        del data["project"]
        errs = vc.validate(data)
        assert any("project" in e for e in errs)

    def test_missing_project_name(self):
        data = _minimal_valid_data()
        del data["project"]["name"]
        errs = vc.validate(data)
        assert any("project.name" in e for e in errs)

    def test_missing_github_section(self):
        data = _minimal_valid_data()
        del data["github"]
        errs = vc.validate(data)
        assert any("github" in e for e in errs)

    def test_missing_github_org(self):
        data = _minimal_valid_data()
        del data["github"]["org"]
        errs = vc.validate(data)
        assert any("github.org" in e for e in errs)

    def test_missing_github_repo(self):
        data = _minimal_valid_data()
        del data["github"]["repo"]
        errs = vc.validate(data)
        assert any("github.repo" in e for e in errs)

    def test_missing_default_branch(self):
        data = _minimal_valid_data()
        del data["github"]["default_branch"]
        errs = vc.validate(data)
        assert any("github.default_branch" in e for e in errs)

    def test_missing_story_key_prefix(self):
        data = _minimal_valid_data()
        del data["github"]["story_key_prefix"]
        errs = vc.validate(data)
        assert any("story_key_prefix" in e for e in errs)

    def test_missing_codeowners_architect_team(self):
        data = _minimal_valid_data()
        del data["github"]["codeowners"]["architect_team"]
        errs = vc.validate(data)
        assert any("architect_team" in e for e in errs)

    def test_missing_codeowners_domain_expert_team(self):
        data = _minimal_valid_data()
        del data["github"]["codeowners"]["domain_expert_team"]
        errs = vc.validate(data)
        assert any("domain_expert_team" in e for e in errs)

    def test_missing_pr_title_template(self):
        data = _minimal_valid_data()
        del data["github"]["pr_title_prefix_template"]
        errs = vc.validate(data)
        assert any("pr_title_prefix_template" in e for e in errs)

    def test_missing_discussions_category(self):
        data = _minimal_valid_data()
        del data["github"]["discussions"]["domain_kb_category"]
        errs = vc.validate(data)
        assert any("domain_kb_category" in e for e in errs)

    def test_missing_milestone_pattern(self):
        data = _minimal_valid_data()
        del data["github"]["milestone"]["epic_naming_pattern"]
        errs = vc.validate(data)
        assert any("epic_naming_pattern" in e for e in errs)


class TestTypeChecks:
    def test_empty_string_name_invalid(self):
        data = _minimal_valid_data()
        data["project"]["name"] = ""
        errs = vc.validate(data)
        assert any("project.name" in e and "type" in e for e in errs)

    def test_name_as_integer_invalid(self):
        data = _minimal_valid_data()
        data["project"]["name"] = 123
        errs = vc.validate(data)
        assert any("project.name" in e for e in errs)

    def test_org_empty_invalid(self):
        data = _minimal_valid_data()
        data["github"]["org"] = ""
        errs = vc.validate(data)
        assert any("github.org" in e for e in errs)

    def test_components_must_be_list_of_strings(self):
        data = _minimal_valid_data()
        data["labels"] = {"components": [1, 2, 3]}
        errs = vc.validate(data)
        assert any("components" in e for e in errs)


# -----------------------------------------------------------------------------
# E2E: subprocess — exit codes per schema doc §main()
# -----------------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class TestE2E:
    def test_missing_file_warns_exit_0(self, tmp_path: Path):
        missing = tmp_path / "nope.yaml"
        res = _run(str(missing))
        assert res.returncode == 0
        assert "WARN" in res.stderr
        assert "not found" in res.stderr

    def test_valid_file_exit_0(self, tmp_path: Path):
        path = tmp_path / "project.yaml"
        path.write_text(
            dedent(
                """\
                project:
                  name: sample
                github:
                  org: acme
                  repo: sample
                  default_branch: main
                  pr_title_prefix_template: "[{key}] {title}"
                  story_key_prefix: SA
                  codeowners:
                    architect_team: "@acme/architects"
                    domain_expert_team: "@acme/domain-experts"
                  discussions:
                    domain_kb_category: "Domain Q&A"
                  milestone:
                    epic_naming_pattern: "Epic-{key}-{slug}"
                """
            ),
            encoding="utf-8",
        )
        res = _run(str(path))
        assert res.returncode == 0, res.stderr
        assert "OK" in res.stderr

    def test_malformed_yaml_exit_3(self, tmp_path: Path):
        path = tmp_path / "bad.yaml"
        path.write_text("project: [unclosed\n", encoding="utf-8")
        res = _run(str(path))
        assert res.returncode == 3
        assert "parse failure" in res.stderr.lower()

    def test_missing_required_exit_4(self, tmp_path: Path):
        path = tmp_path / "missing.yaml"
        path.write_text("project:\n  name: x\n", encoding="utf-8")
        res = _run(str(path))
        assert res.returncode == 4
        assert "missing required field" in res.stderr.lower()

    def test_no_args_exit_1(self):
        res = _run()
        assert res.returncode == 1
        assert "Usage" in res.stderr

    def test_bundled_examples_validate(self):
        """All example project.yaml files must pass the validator."""
        repo_root = HOOKS_DIR.parent.parent
        for yaml_path in [
            repo_root / "examples/webapp-minimal/.claude/_overlay/project.yaml",
            repo_root / "examples/cli-tool-minimal/.claude/_overlay/project.yaml",
            repo_root / "examples/library-minimal/.claude/_overlay/project.yaml",
            repo_root / "overlay/_overlay/project.yaml.example",
        ]:
            assert yaml_path.exists(), f"fixture missing: {yaml_path}"
            res = _run(str(yaml_path))
            # Examples have <REPLACE — ...> placeholders, which are non-empty strings,
            # so validation passes (placeholders treated as valid filler, not enforced
            # value validation).
            assert res.returncode == 0, f"validator failed on {yaml_path}: {res.stderr}"


# -----------------------------------------------------------------------------
# CFP-658 Phase 2 — bootstrap.fallback_mode enum validator tests (TDD red phase)
# ADR-027 Amendment 2 §결정 6.A — fallback_mode enum: "auto" | "action_blocked"
# -----------------------------------------------------------------------------


class TestBootstrapFallbackMode:
    """bootstrap.fallback_mode enum 검증 테스트 (CFP-658 Phase 2 / ADR-027 Amendment 2 §결정 6.A).

    fallback_mode:
        - field 부재 = default "auto" (no error, no warning)
        - "auto" = PASS
        - "action_blocked" = PASS
        - 그 외 문자열 = error (exit 4 / validate() 반환 비어있지 않음)
    """

    def test_fallback_mode_absent_default_auto(self):
        """bootstrap.fallback_mode 부재 시 에러 없음 — default auto 적용."""
        data = _minimal_valid_data()
        data["bootstrap"] = {}  # fallback_mode 없이 bootstrap 섹션만
        assert vc.validate(data) == []

    def test_fallback_mode_auto_valid(self):
        """bootstrap.fallback_mode: auto 는 유효."""
        data = _minimal_valid_data()
        data["bootstrap"] = {"fallback_mode": "auto"}
        assert vc.validate(data) == []

    def test_fallback_mode_action_blocked_valid(self):
        """bootstrap.fallback_mode: action_blocked 는 유효."""
        data = _minimal_valid_data()
        data["bootstrap"] = {"fallback_mode": "action_blocked"}
        assert vc.validate(data) == []

    def test_fallback_mode_invalid_value_raises(self):
        """bootstrap.fallback_mode: 허용 외 값 → 오류."""
        data = _minimal_valid_data()
        data["bootstrap"] = {"fallback_mode": "invalid_value"}
        errs = vc.validate(data)
        assert errs, "invalid fallback_mode 은 반드시 오류를 반환해야 한다"
        assert any("fallback_mode" in e for e in errs)

    def test_fallback_mode_strict_mode_coexist_valid(self):
        """bootstrap.strict_mode: true + bootstrap.fallback_mode: action_blocked 동시 유효."""
        data = _minimal_valid_data()
        data["bootstrap"] = {"strict_mode": True, "fallback_mode": "action_blocked"}
        assert vc.validate(data) == []

    def test_fallback_mode_uppercase_invalid(self):
        """bootstrap.fallback_mode: 'AUTO' (대문자) 는 enum 불일치 → 오류."""
        data = _minimal_valid_data()
        data["bootstrap"] = {"fallback_mode": "AUTO"}
        errs = vc.validate(data)
        assert errs, "'AUTO' 는 허용 값이 아니다"
        assert any("fallback_mode" in e for e in errs)

    def test_fallback_mode_empty_string_invalid(self):
        """bootstrap.fallback_mode: '' (빈 문자열) 는 허용 값 아님 → 오류."""
        data = _minimal_valid_data()
        data["bootstrap"] = {"fallback_mode": ""}
        errs = vc.validate(data)
        assert errs, "빈 문자열은 허용 값이 아니다"
        assert any("fallback_mode" in e for e in errs)


# -----------------------------------------------------------------------------
# 문서화된 5 config 블록 (deploy/atlassian/runtime/security/aggregate_arch) 검증
# project-config-schema 문서·consumer-guide 가 안내하지만 SCHEMA_RULES 미등록이던 drift 수정.
# Schema SSOT: docs/project-config-schema.md §aggregate_arch/§deploy/§atlassian + consumer-guide §1g/§1j
# -----------------------------------------------------------------------------


class TestDocumentedOptionalBlocks:
    """문서가 안내하는 5 블록이 validate clean(exit 0) — 이전엔 _check_unknown_keys exit 4."""

    def test_all_five_blocks_valid(self):
        data = _minimal_valid_data()
        data["aggregate_arch"] = {"applicable": True, "migration_tool": "alembic"}
        data["deploy"] = {
            "host_mapping": [{"host": "deploy-01.acme.io", "containers": ["acme/api:latest"]}],
            "docker_hub": {"org": "acme", "image_prefix": "acme-app-",
                           "auth_secret_env": "DOCKER_HUB_TOKEN"},
            "traefik": {"enabled": True, "network": "acme-public",
                        "domain_pattern": "{service}.acme.io"},
            "1password": {"enabled": True, "connect_host_env": "OP_CONNECT_HOST",
                          "connect_token_env": "OP_CONNECT_TOKEN", "vault": "Production"},
            "ssh_targets": [{"host": "deploy-01.acme.io", "user": "deploy",
                             "key_secret_env": "SSH_DEPLOY_KEY", "port": 22}],
            "auto_rollback": {"enabled": True, "error_rate_threshold": 0.02, "window": 3600},
        }
        data["atlassian"] = {
            "enabled": True,
            "confluence": {"base_url": "https://myorg.atlassian.net/wiki", "space_key": "CGOV",
                           "api_token_env": "ATLASSIAN_API_TOKEN",
                           "user_email_env": "ATLASSIAN_USER_EMAIL",
                           "mirror_targets": ["adr", "architecture_doc"]},
            "jira": {"project_key": "PROJ"},
        }
        data["runtime"] = {"auto_resume": {"enabled": True}}
        data["security"] = {"pat_rotation_cadence_days": 90}
        assert vc.validate(data) == []

    def test_each_block_individually_valid(self):
        for block, payload in [
            ("aggregate_arch", {"applicable": False, "migration_tool": "prisma-migrate"}),
            ("deploy", {"traefik": {"enabled": False}}),
            ("atlassian", {"enabled": True}),
            ("runtime", {"auto_resume": {"enabled": True}}),
            ("security", {"pat_rotation_cadence_days": 30}),
        ]:
            data = _minimal_valid_data()
            data[block] = payload
            assert vc.validate(data) == [], f"{block} 블록이 validate clean 이어야 한다"

    def test_aggregate_arch_invalid_migration_tool_rejected(self):
        data = _minimal_valid_data()
        data["aggregate_arch"] = {"migration_tool": "not-a-real-tool"}
        errs = vc.validate(data)
        assert any("migration_tool" in e for e in errs)

    def test_atlassian_invalid_mirror_target_rejected(self):
        data = _minimal_valid_data()
        data["atlassian"] = {"confluence": {"mirror_targets": ["bogus_type"]}}
        errs = vc.validate(data)
        assert any("mirror_targets" in e for e in errs)

    def test_unknown_child_under_allowed_block_still_rejected(self):
        """이제 허용된 블록 안의 문서 외 자식 키는 여전히 unknown reject."""
        data = _minimal_valid_data()
        data["atlassian"] = {"enabled": True, "bogus_child_key": 42}
        errs = vc.validate(data)
        assert any("bogus_child_key" in e for e in errs)

    def test_genuinely_unknown_top_level_block_still_rejected(self):
        """진짜 unknown top-level 키는 가드 무손상 — 여전히 reject."""
        data = _minimal_valid_data()
        data["totally_made_up_block"] = 1
        errs = vc.validate(data)
        assert any("totally_made_up_block" in e for e in errs)

    # -------------------------------------------------------------------------
    # F-CR-1932-1 — per_doc_type_override OPEN MAPPING (구현리뷰 P1)
    # 문서화된 형태 {adr: {parent_page_id: ...}} 가 _check_unknown_keys 재귀로
    # 자식 doc-type 키 → unknown key → EXIT 4 되던 잔존 결함 수정.
    # Schema SSOT: docs/project-config-schema.md §atlassian per_doc_type_override (~L503).
    # -------------------------------------------------------------------------

    def test_per_doc_type_override_documented_form_valid(self):
        """문서화된 per_doc_type_override (자식 doc-type 키들) 가 validate clean."""
        data = _minimal_valid_data()
        data["atlassian"] = {
            "confluence": {
                "per_doc_type_override": {
                    "adr": {"parent_page_id": "12345"},
                    "change-plan": {"parent_page_id": "67890"},
                }
            }
        }
        assert vc.validate(data) == []

    def test_per_doc_type_override_arbitrary_doc_types_valid(self):
        """adr/change-plan 외 임의 doc-type 키도 허용 (open mapping)."""
        data = _minimal_valid_data()
        data["atlassian"] = {
            "confluence": {
                "per_doc_type_override": {
                    "story": {"parent_page_id": "111"},
                    "domain_knowledge": {"parent_page_id": "222"},
                    "any_future_doc_type": {"parent_page_id": "333"},
                }
            }
        }
        assert vc.validate(data) == []

    def test_per_doc_type_override_empty_mapping_valid(self):
        """빈 per_doc_type_override 도 유효 (자식 0개)."""
        data = _minimal_valid_data()
        data["atlassian"] = {"confluence": {"per_doc_type_override": {}}}
        assert vc.validate(data) == []

    def test_per_doc_type_override_malformed_non_dict_value_rejected(self):
        """doc-type 값이 dict 가 아니면 (예: string) malformed → reject."""
        data = _minimal_valid_data()
        data["atlassian"] = {
            "confluence": {"per_doc_type_override": {"adr": "not-a-dict"}}
        }
        errs = vc.validate(data)
        assert any("per_doc_type_override" in e for e in errs)

    def test_per_doc_type_override_non_dict_rejected(self):
        """per_doc_type_override 자체가 dict 가 아니면 reject."""
        data = _minimal_valid_data()
        data["atlassian"] = {"confluence": {"per_doc_type_override": ["adr"]}}
        errs = vc.validate(data)
        assert any("per_doc_type_override" in e for e in errs)


# -----------------------------------------------------------------------------
# CFP-2700 / ADR-157 §결정1 — infra_resources 2-plane manifest 런타임 배선 (G4 FIX)
# 문서 스키마(project-config-schema.md §infra_resources)를 validate_config 에 배선한다.
# 선언 plane(resources / execution_units / startup_validation)은 판별 — 오타 키 reject;
# execution_units 아래 동적 unit 키만 OPEN_MAPPING 으로 허용(blanket open-map 아님).
# Schema SSOT: docs/project-config-schema.md §infra_resources.
# -----------------------------------------------------------------------------


class TestInfraResourcesManifest:
    """infra_resources 2-plane manifest (CFP-2700 D5 consumer 전파) shape 검증."""

    def _valid_infra_resources(self) -> dict:
        # webapp-minimal 형태 — plane A resources[] + plane B execution_units{} + startup_validation.
        return {
            "resources": [
                {"id": "app-database", "canonical_env": "DATABASE_URL",
                 "aliases": {"accepted": []}},
                {"id": "app-redis", "canonical_env": "REDIS_URL",
                 "aliases": {"accepted": []}},
            ],
            "execution_units": {
                "web": {
                    "required": ["app-database", "app-redis"],
                    "resource_modes": {"app-database": "required", "app-redis": "required"},
                },
            },
            "startup_validation": {
                "adopted": False,
                "reason": "데모 템플릿 — 실 consumer 는 web startup 에 reference impl 채택 후 adopted: true",
            },
        }

    def test_infra_resources_two_plane_valid(self):
        """유효 2-plane block 이 validate clean(exit 0 경로) — positive."""
        data = _minimal_valid_data()
        data["infra_resources"] = self._valid_infra_resources()
        assert vc.validate(data) == []

    def test_infra_resources_dynamic_execution_unit_key_allowed(self):
        """execution_units 아래 동적 unit 키(임의 이름)는 OPEN_MAPPING 으로 허용."""
        data = _minimal_valid_data()
        infra = self._valid_infra_resources()
        infra["execution_units"]["customworker"] = {
            "required": ["app-database"],
            "resource_modes": {"app-database": "required"},
        }
        data["infra_resources"] = infra
        assert vc.validate(data) == []

    def test_infra_resources_declared_plane_typo_rejected(self):
        """선언 plane 오타 키는 reject — blanket open-map 아니라 declared plane 은 판별함 (negative).

        (a) resources 형제 위치의 오타 plane 키 → unknown key
        (b) startup_validation 고정키 오타 → unknown key
        """
        # (a) 선언 plane 레벨 오타
        data = _minimal_valid_data()
        infra = self._valid_infra_resources()
        infra["resourcezz"] = []
        data["infra_resources"] = infra
        errs = vc.validate(data)
        assert any("infra_resources.resourcezz" in e for e in errs), errs

        # (b) startup_validation 고정키 오타
        data2 = _minimal_valid_data()
        infra2 = self._valid_infra_resources()
        infra2["startup_validation"] = {"adoptedd": True}
        data2["infra_resources"] = infra2
        errs2 = vc.validate(data2)
        assert any("infra_resources.startup_validation.adoptedd" in e for e in errs2), errs2


# -----------------------------------------------------------------------------
# CFP-2419 Phase 2 — repo_topology 책임 배치 토폴로지 검증
# ADR-131 §결정2 (4 메타불변식 + layer 분리) / Story §5.2 AC-3, §5.3 EC-1/EC-2
# Schema SSOT: docs/project-config-schema.md §repo_topology
# Spec Invariants: meta-invariant (①-④) + layer separation (EC-1, EC-2) + schema constraint
# Mapping Table Entry Format: [test method | tests/<path>:<line> | spec invariant | assertion line]
# -----------------------------------------------------------------------------


class TestRepoTopology:
    """repo_topology 책임 배치 거버넌스 검증 테스트.

    CFP-2419 Phase 2 / ADR-131 §결정2 (4 메타불변식 + layer 분리):
      - 메타불변식 ①: 모든 책임 정확히 1 소유레포
      - 메타불변식 ②: 주인없는 책임 0
      - 메타불변식 ③: 중복소유 0
      - 메타불변식 ④: linked_artifact ≥1 (SSOT 추적성)
      - EC-1: applicable=false (또는 섹션 부재) → PASS (비차단)
      - EC-2: applicable=true 후 responsibilities=[] (공백) → 스키마 유효성만 검사, PASS

    Schema SSOT: docs/project-config-schema.md repo_topology (§4 라인 585-597, 섹션설명 650-674)
    """

    # --------- LAYER SEPARATION: Layer-1 PASS cases (absent, empty, or valid) ---------

    def test_repo_topology_section_absent_valid(self):
        """repo_topology 섹션 미주입 (기존 동작 보존) → PASS [EC-1].

        backend-compat invariant: 섹션 부재 = applicable 미입력 시 default false.
        """
        data = _minimal_valid_data()
        # repo_topology 전혀 안 넣음
        assert vc.validate(data) == []

    def test_repo_topology_empty_dict_valid(self):
        """repo_topology: {} (빈 dict) → applicable 기본값 false, PASS [EC-1].

        모든 필드 미입력 = default 적용, 유효.
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {}
        assert vc.validate(data) == []

    def test_repo_topology_applicable_false_valid(self):
        """repo_topology.applicable: false (명시) → 메타불변식 게이트 PASS [EC-1].

        false 이면 responsibilities 무관 (검사 안 함).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {"applicable": False}
        assert vc.validate(data) == []

    def test_repo_topology_applicable_true_no_responsibilities_valid(self):
        """repo_topology.applicable: true, responsibilities 키 없음 → PASS [EC-2].

        applicable=true 이지만 responsibilities 미주입 = 정책값 공백.
        스키마 유효성만 검사하고 맵 내용 공백은 PASS (layer separation: ADR-131 §결정2).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {"applicable": True}
        assert vc.validate(data) == []

    def test_repo_topology_applicable_true_empty_responsibilities_valid(self):
        """repo_topology.applicable: true, responsibilities: [] (공백 배열) → PASS [EC-2].

        responsibilities=[] = 정책 내용 공백, 스키마 유효, PASS
        (layer separation: 정책값 공백 = wrapper 구조검증 layer ≠ consumer 정책주입 layer).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {"applicable": True, "responsibilities": []}
        assert vc.validate(data) == []

    # --------- SCHEMA: Fully well-formed entry (all 4 fields + ≥1 linked_artifact) ---------

    def test_repo_topology_fully_wellformed_entry_valid(self):
        """1개 책임, 모든 필수 필드 + linked_artifact≥1 → PASS [AC-3].

        메타불변식 ①②③④ 모두 만족하는 정상 케이스.
        스키마 정의 예시: responsibility (non-empty str) + owner_repo (non-empty str)
                        + rationale (non-empty str) + linked_artifact (list of non-empty str, ≥1).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "risk-metrics-sharpe-mdd",
                    "owner_repo": "mclayer/mctrader-engine",
                    "rationale": "risk domain owns Sharpe/MDD metrics calculation",
                    "linked_artifact": ["CFP-2418", "ADR-131"],
                }
            ],
        }
        assert vc.validate(data) == []

    # --------- SCHEMA CONSTRAINT VIOLATIONS ---------

    def test_repo_topology_missing_linked_artifact_invalid(self):
        """책임 항목에서 linked_artifact 키 미주입 → INVALID [메타불변식 ④].

        linked_artifact 필수, ≥1 배열 요소 필요 (추적성).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "order-execution",
                    "owner_repo": "mclayer/mctrader-engine",
                    "rationale": "engine executes orders",
                    # linked_artifact 없음
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "linked_artifact 미주입은 오류를 반환해야 한다"
        assert any(
            "responsibilities" in e or "linked_artifact" in e for e in errs
        ), "에러 메시지에 책임 또는 linked_artifact 언급 필요"

    def test_repo_topology_empty_linked_artifact_list_invalid(self):
        """linked_artifact: [] (공백 배열) → INVALID [메타불변식 ④].

        KEY DISCRIMINATING CASE: ≥1 요구사항 구분 (list-of-str ≠ list with ≥1).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "portfolio-valuation",
                    "owner_repo": "mclayer/mctrader-data",
                    "rationale": "data team computes portfolio values",
                    "linked_artifact": [],  # ★ 공백 배열
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "linked_artifact: [] 는 오류를 반환해야 한다 (≥1 요구사항)"
        assert any("linked_artifact" in e for e in errs), "에러 메시지에 linked_artifact 언급"

    def test_repo_topology_missing_owner_repo_invalid(self):
        """책임 항목에서 owner_repo 키 미주입 → INVALID [메타불변식 ②].

        owner_repo 필수 (주인 지정).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "market-data-sync",
                    "rationale": "fetch market data from exchange",
                    "linked_artifact": ["CFP-2418"],
                    # owner_repo 없음
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "owner_repo 미주입은 오류를 반환해야 한다"
        assert any("owner_repo" in e for e in errs)

    def test_repo_topology_missing_responsibility_invalid(self):
        """책임 항목에서 responsibility 키 미주입 → INVALID.

        responsibility 필수 (책임 식별자).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "owner_repo": "mclayer/mctrader-engine",
                    "rationale": "core execution",
                    "linked_artifact": ["CFP-2418"],
                    # responsibility 없음
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "responsibility 미주입은 오류를 반환해야 한다"
        assert any("responsibility" in e for e in errs)

    def test_repo_topology_missing_rationale_invalid(self):
        """책임 항목에서 rationale 키 미주입 → INVALID.

        rationale 필수 (배치 근거 텍스트).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "signal-generation",
                    "owner_repo": "mclayer/mctrader-signals",
                    "linked_artifact": ["ADR-131"],
                    # rationale 없음
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "rationale 미주입은 오류를 반환해야 한다"
        assert any("rationale" in e for e in errs)

    def test_repo_topology_empty_string_owner_repo_invalid(self):
        """owner_repo: "" (빈 문자열) → INVALID.

        owner_repo non-empty str 요구.
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "notification-service",
                    "owner_repo": "",  # 빈 문자열
                    "rationale": "sends notifications",
                    "linked_artifact": ["CFP-2418"],
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "owner_repo='' 는 오류를 반환해야 한다"
        assert any("owner_repo" in e for e in errs)

    def test_repo_topology_empty_string_responsibility_invalid(self):
        """responsibility: "" (빈 문자열) → INVALID.

        responsibility non-empty str 요구.
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "",  # 빈 문자열
                    "owner_repo": "mclayer/mctrader-ui",
                    "rationale": "frontend presentation",
                    "linked_artifact": ["ADR-131"],
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "responsibility='' 는 오류를 반환해야 한다"
        assert any("responsibility" in e for e in errs)

    def test_repo_topology_empty_string_rationale_invalid(self):
        """rationale: "" (빈 문자열) → INVALID.

        rationale non-empty str 요구.
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "logging-aggregation",
                    "owner_repo": "mclayer/mctrader-logging",
                    "rationale": "",  # 빈 문자열
                    "linked_artifact": ["CFP-2418"],
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "rationale='' 는 오류를 반환해야 한다"
        assert any("rationale" in e for e in errs)

    def test_repo_topology_unknown_extra_child_key_invalid(self):
        """책임 항목에 문서 외 키(예: bogus_key) → INVALID.

        Schema: 정확히 4개 키만 허용 (responsibility, owner_repo, rationale, linked_artifact).
        Unknown 키 reject (guard preserved — existing test_unknown_child_under_allowed_block_still_rejected 패턴).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "cache-management",
                    "owner_repo": "mclayer/mctrader-cache",
                    "rationale": "manages distributed cache",
                    "linked_artifact": ["CFP-2418"],
                    "bogus_key": 1,  # ★ unknown 키
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "unknown 키 (bogus_key) 는 오류를 반환해야 한다"
        assert any("bogus_key" in e for e in errs)

    def test_repo_topology_linked_artifact_empty_string_element_invalid(self):
        """linked_artifact 배열이 빈 문자열 요소 포함 → INVALID.

        linked_artifact 는 non-empty str 요소만 허용 (예: "" ≠ 유효한 작업단위/ADR/change-plan).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "api-versioning",
                    "owner_repo": "mclayer/mctrader-api",
                    "rationale": "API layer handles versioning",
                    "linked_artifact": ["CFP-2418", ""],  # ★ 빈 문자열 요소
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "linked_artifact 에 빈 문자열이 있으면 오류를 반환해야 한다"
        assert any("linked_artifact" in e for e in errs)

    def test_repo_topology_linked_artifact_non_string_element_invalid(self):
        """linked_artifact 배열이 비-string 요소 포함 → INVALID.

        linked_artifact 는 string 배열 (예: 123 ≠ "CFP-2418").
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [
                {
                    "responsibility": "metrics-collection",
                    "owner_repo": "mclayer/mctrader-metrics",
                    "rationale": "collect and aggregate metrics",
                    "linked_artifact": ["CFP-2418", 123],  # ★ 숫자 요소
                }
            ],
        }
        errs = vc.validate(data)
        assert errs, "linked_artifact 에 non-string 요소가 있으면 오류를 반환해야 한다"
        assert any("linked_artifact" in e for e in errs)

    def test_repo_topology_unknown_key_under_repo_topology_invalid(self):
        """repo_topology 직속에 unknown 키 (예: bogus_setting) → INVALID.

        Schema: repo_topology 는 applicable + responsibilities 만 허용.
        Unknown 키 reject (guard preserved — existing test_unknown_child_under_allowed_block_still_rejected 패턴).
        """
        data = _minimal_valid_data()
        data["repo_topology"] = {
            "applicable": True,
            "responsibilities": [],
            "bogus_setting": True,  # ★ unknown 키
        }
        errs = vc.validate(data)
        assert errs, "unknown 키는 repo_topology 직속에서도 reject되어야 한다"
        assert any("bogus_setting" in e for e in errs)
