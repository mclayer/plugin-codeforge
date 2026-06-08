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
