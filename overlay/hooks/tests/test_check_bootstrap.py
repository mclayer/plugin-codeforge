"""CFP-103 — check_bootstrap.py 단위 테스트.

Cross-platform CI matrix (ubuntu-latest + windows-latest) 양 OS pass 의무.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_bootstrap  # noqa: E402


FIXTURES = Path(__file__).parent / "fixtures"


# ============================================================ Check 5 — 11 plugin


def test_check_plugins_installed_full_pass(tmp_path: Path) -> None:
    """11 plugin 모두 등록 시 warning 부재."""
    src = (FIXTURES / "installed_plugins_full.json").read_text(encoding="utf-8")
    p = tmp_path / "installed_plugins.json"
    p.write_text(src, encoding="utf-8")
    warns = check_bootstrap.check_plugins_installed(p)
    assert warns == []


def test_check_plugins_installed_mctrader_partial(tmp_path: Path) -> None:
    """mctrader-hub 검증 case (4 dep 만, codeforge family 0개) → 7 plugin 부재 warning."""
    src = (FIXTURES / "installed_plugins_partial.json").read_text(encoding="utf-8")
    p = tmp_path / "installed_plugins.json"
    p.write_text(src, encoding="utf-8")
    warns = check_bootstrap.check_plugins_installed(p)
    assert warns, "WARN 출력 필요"
    # 7/11 미설치 (codeforge family 7개 부재)
    assert any("7/11 plugin 미설치" in w for w in warns)
    # 설치 명령 안내 필수
    assert any("/plugins install codeforge@mclayer" in w for w in warns)


def test_check_plugins_installed_empty(tmp_path: Path) -> None:
    """11 plugin 모두 부재 시 11 미설치 warning."""
    src = (FIXTURES / "installed_plugins_empty.json").read_text(encoding="utf-8")
    p = tmp_path / "installed_plugins.json"
    p.write_text(src, encoding="utf-8")
    warns = check_bootstrap.check_plugins_installed(p)
    assert warns
    assert any("11/11 plugin 미설치" in w for w in warns)


def test_check_plugins_installed_file_missing(tmp_path: Path) -> None:
    """installed_plugins.json 파일 부재 시 warning."""
    p = tmp_path / "nonexistent.json"
    warns = check_bootstrap.check_plugins_installed(p)
    assert any("부재" in w for w in warns)


def test_check_plugins_installed_malformed(tmp_path: Path) -> None:
    """malformed JSON parse 실패 시 warning."""
    p = tmp_path / "installed_plugins.json"
    p.write_text("not valid json {{{", encoding="utf-8")
    warns = check_bootstrap.check_plugins_installed(p)
    assert any("parse 실패" in w for w in warns)


# ============================================================ Check 6 — workflows


def test_check_consumer_workflows_all_present(tmp_path: Path) -> None:
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    for w in check_bootstrap.EXPECTED_WORKFLOWS_FULL:
        (workflows_dir / w).write_text("# stub\n", encoding="utf-8")
    warns = check_bootstrap.check_consumer_workflows(workflows_dir)
    assert warns == []


def test_check_consumer_workflows_missing_5(tmp_path: Path) -> None:
    """mctrader-hub 검증 case — 7 중 2 만 (phase-gate-mergeable + phase-label-invariant)."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "phase-gate-mergeable.yml").write_text("# stub\n", encoding="utf-8")
    (workflows_dir / "phase-label-invariant.yml").write_text("# stub\n", encoding="utf-8")
    warns = check_bootstrap.check_consumer_workflows(workflows_dir)
    assert warns
    assert any("미설치" in w or "부재" in w for w in warns)


def test_check_consumer_workflows_dir_missing(tmp_path: Path) -> None:
    workflows_dir = tmp_path / "nonexistent"
    warns = check_bootstrap.check_consumer_workflows(workflows_dir)
    assert any("부재" in w for w in warns)


def test_check_consumer_workflows_override_set(tmp_path: Path) -> None:
    """expected_set override 가 적용되는지."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "only-this.yml").write_text("# stub\n", encoding="utf-8")
    warns = check_bootstrap.check_consumer_workflows(workflows_dir, expected_set={"only-this.yml"})
    assert warns == []


# ============================================================ Check 7 — Issue Forms


def test_check_consumer_issue_forms_all_present(tmp_path: Path) -> None:
    forms_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    forms_dir.mkdir(parents=True)
    for f in ["audit.yml", "bug.yml", "story.yml"]:
        (forms_dir / f).write_text("# stub\n", encoding="utf-8")
    warns = check_bootstrap.check_consumer_issue_forms(forms_dir)
    assert warns == []


def test_check_consumer_issue_forms_missing_story(tmp_path: Path) -> None:
    """mctrader-hub 검증 case — 2 만 (audit + bug, story.yml 부재)."""
    forms_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    forms_dir.mkdir(parents=True)
    (forms_dir / "audit.yml").write_text("# stub\n", encoding="utf-8")
    (forms_dir / "bug.yml").write_text("# stub\n", encoding="utf-8")
    warns = check_bootstrap.check_consumer_issue_forms(forms_dir)
    assert warns
    assert any("1/3" in w for w in warns)
    assert any("story.yml" in w for w in warns)


def test_check_consumer_issue_forms_dir_missing(tmp_path: Path) -> None:
    forms_dir = tmp_path / "nonexistent"
    warns = check_bootstrap.check_consumer_issue_forms(forms_dir)
    assert any("부재" in w for w in warns)


# ============================================================ Check 8 — CODEOWNERS


def test_check_codeowners_present(tmp_path: Path) -> None:
    co = tmp_path / "CODEOWNERS"
    co.write_text("* @mccho8865\ndocs/ @mccho8865\n", encoding="utf-8")
    warns = check_bootstrap.check_codeowners(co)
    assert warns == []


def test_check_codeowners_missing(tmp_path: Path) -> None:
    warns = check_bootstrap.check_codeowners(
        tmp_path / "CODEOWNERS",
        tmp_path / ".github" / "CODEOWNERS",
    )
    assert any("부재" in w for w in warns)


def test_check_codeowners_empty(tmp_path: Path) -> None:
    co = tmp_path / "CODEOWNERS"
    co.write_text("# only comments\n# more comments\n", encoding="utf-8")
    warns = check_bootstrap.check_codeowners(co)
    assert any("비어 있거나 invalid" in w for w in warns)


def test_check_codeowners_org_team(tmp_path: Path) -> None:
    co = tmp_path / "CODEOWNERS"
    co.write_text("docs/ @mclayer/architects\nsrc/ @mclayer/dev-team\n", encoding="utf-8")
    warns = check_bootstrap.check_codeowners(co)
    assert warns == []


def test_check_codeowners_search_priority(tmp_path: Path) -> None:
    """첫 번째 발견된 path 사용."""
    root_co = tmp_path / "CODEOWNERS"
    root_co.write_text("* @user1\n", encoding="utf-8")
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    github_co = github_dir / "CODEOWNERS"
    github_co.write_text("# empty\n", encoding="utf-8")  # 이건 평가 안 됨
    warns = check_bootstrap.check_codeowners(root_co, github_co)
    assert warns == []  # root 가 먼저 매치


# ============================================================ Check 3 — workflow_distribution


def test_check_workflow_distribution_full_pass(tmp_path: Path) -> None:
    yaml_path = tmp_path / "project.yaml"
    yaml_path.write_text("workflow_distribution:\n  mode: full\n", encoding="utf-8")
    warns = check_bootstrap.check_workflow_distribution(yaml_path)
    assert warns == []


def test_check_workflow_distribution_degraded_warns(tmp_path: Path) -> None:
    yaml_path = tmp_path / "project.yaml"
    yaml_path.write_text(
        "workflow_distribution:\n"
        "  mode: degraded\n"
        "  missing_workflows:\n"
        "    - story-init.yml\n"
        "    - fix-ledger-sync.yml\n",
        encoding="utf-8",
    )
    warns = check_bootstrap.check_workflow_distribution(yaml_path)
    assert warns
    assert any("degraded" in w for w in warns)
    assert any("story-init.yml" in w for w in warns)


# ============================================================ helpers


def test_resolve_plugins_json_linux() -> None:
    p = check_bootstrap._resolve_plugins_json({"HOME": "/home/user"})
    s = str(p)
    assert ".claude" in s and "plugins" in s and "installed_plugins.json" in s


def test_resolve_plugins_json_windows() -> None:
    p = check_bootstrap._resolve_plugins_json({"USERPROFILE": "C:/Users/test"})
    s = str(p)
    assert ".claude" in s and "plugins" in s and "installed_plugins.json" in s


# ============================================================ main() smoke


def test_main_smoke_no_overlay(tmp_path: Path, monkeypatch) -> None:
    """project.yaml 부재 시 silent exit 0 (cwd 변경)."""
    monkeypatch.chdir(tmp_path)
    rc = check_bootstrap.main()
    assert rc == 0
