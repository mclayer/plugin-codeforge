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
