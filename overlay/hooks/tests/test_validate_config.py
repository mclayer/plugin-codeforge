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
        "project": {"name": "x", "repo": "github.com/a/b"},
        "atlassian": {
            "site": "acme.atlassian.net",
            "confluence": {
                "space_key": "AA",
                "stories_parent_page_id": 123,
                "domain_knowledge_parent_page_id": 124,
                "adr_root_page_id": 125,
            },
            "jira": {"project_key": "AA"},
        },
        "github": {"pr_title_prefix_template": "[{project_key}-{story_number}] {title}"},
    }


class TestValidateMinimal:
    def test_minimal_required_fields_valid(self):
        assert vc.validate(_minimal_valid_data()) == []

    def test_with_optional_fields_valid(self):
        data = _minimal_valid_data()
        data["atlassian"]["jira"]["transitions"] = {"to_in_progress": 21, "to_done": 31}
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

    def test_missing_atlassian_site(self):
        data = _minimal_valid_data()
        del data["atlassian"]["site"]
        errs = vc.validate(data)
        assert any("atlassian.site" in e for e in errs)

    def test_missing_space_key(self):
        data = _minimal_valid_data()
        del data["atlassian"]["confluence"]["space_key"]
        errs = vc.validate(data)
        assert any("space_key" in e for e in errs)

    def test_missing_stories_parent_page_id(self):
        data = _minimal_valid_data()
        del data["atlassian"]["confluence"]["stories_parent_page_id"]
        errs = vc.validate(data)
        assert any("stories_parent_page_id" in e for e in errs)

    def test_missing_jira_project_key(self):
        data = _minimal_valid_data()
        del data["atlassian"]["jira"]["project_key"]
        errs = vc.validate(data)
        assert any("jira.project_key" in e for e in errs)

    def test_missing_github_template(self):
        data = _minimal_valid_data()
        del data["github"]["pr_title_prefix_template"]
        errs = vc.validate(data)
        assert any("pr_title_prefix_template" in e for e in errs)


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

    def test_pageid_accepts_both_int_and_str(self):
        d1 = _minimal_valid_data()
        d1["atlassian"]["confluence"]["adr_root_page_id"] = 12345
        assert vc.validate(d1) == []

        d2 = _minimal_valid_data()
        d2["atlassian"]["confluence"]["adr_root_page_id"] = "12345"
        assert vc.validate(d2) == []

    def test_pageid_boolean_rejected(self):
        data = _minimal_valid_data()
        data["atlassian"]["confluence"]["adr_root_page_id"] = True
        errs = vc.validate(data)
        assert any("adr_root_page_id" in e for e in errs)

    def test_components_must_be_list_of_strings(self):
        data = _minimal_valid_data()
        data["labels"] = {"components": [1, 2, 3]}
        errs = vc.validate(data)
        assert any("components" in e for e in errs)

    def test_transitions_value_must_be_int(self):
        data = _minimal_valid_data()
        data["atlassian"]["jira"]["transitions"] = {"to_done": "31"}  # string not int
        errs = vc.validate(data)
        assert any("transitions" in e for e in errs)


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
                  repo: github.com/a/b
                atlassian:
                  site: acme.atlassian.net
                  confluence:
                    space_key: SA
                    stories_parent_page_id: 1
                    domain_knowledge_parent_page_id: 2
                    adr_root_page_id: 3
                  jira:
                    project_key: SA
                github:
                  pr_title_prefix_template: "[{project_key}-{story_number}] {title}"
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
            assert res.returncode == 0, f"validator failed on {yaml_path}: {res.stderr}"
