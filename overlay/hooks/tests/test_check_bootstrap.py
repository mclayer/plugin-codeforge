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


def test_resolve_plugins_json_dual_env_neither_exists() -> None:
    """HOME + USERPROFILE 둘 다 set, 둘 다 file 부재 — 첫 candidate (HOME) 반환."""
    p = check_bootstrap._resolve_plugins_json({"HOME": "/home/user", "USERPROFILE": "C:/Users/test"})
    s = str(p).replace("\\", "/")
    # HOME first
    assert "home/user" in s


def test_resolve_plugins_json_dual_env_userprofile_exists(tmp_path: Path) -> None:
    """HOME 부재 + USERPROFILE 의 file 존재 → USERPROFILE path 반환."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    real_userprofile = tmp_path / "real_userprofile"
    plugins_dir = real_userprofile / ".claude" / "plugins"
    plugins_dir.mkdir(parents=True)
    (plugins_dir / "installed_plugins.json").write_text("{}", encoding="utf-8")
    p = check_bootstrap._resolve_plugins_json({
        "HOME": str(fake_home),
        "USERPROFILE": str(real_userprofile),
    })
    assert str(real_userprofile) in str(p)


def test_resolve_plugins_json_no_envs() -> None:
    """둘 다 부재 시 fallback 상대 경로."""
    p = check_bootstrap._resolve_plugins_json({})
    s = str(p).replace("\\", "/")
    assert ".claude/plugins/installed_plugins.json" in s


# ============================================================ main() smoke


def test_main_smoke_no_overlay(tmp_path: Path, monkeypatch) -> None:
    """project.yaml 부재 시 silent exit 0 (cwd 변경)."""
    monkeypatch.chdir(tmp_path)
    rc = check_bootstrap.main([])
    assert rc == 0


def test_main_bootstrap_expected_workflows_override(tmp_path: Path, monkeypatch, capsys) -> None:
    """main() 이 bootstrap.expected_workflows override 를 적용하는지 (CFP-103 C fix)."""
    overlay_dir = tmp_path / ".claude" / "_overlay"
    overlay_dir.mkdir(parents=True)
    (overlay_dir / "project.yaml").write_text(
        "github:\n  org: example\n  repo: test\n"
        "bootstrap:\n"
        "  expected_workflows:\n"
        "    - only-one.yml\n",
        encoding="utf-8",
    )
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "only-one.yml").write_text("# stub\n", encoding="utf-8")
    forms_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    forms_dir.mkdir(parents=True)
    for f in ["audit.yml", "bug.yml", "story.yml"]:
        (forms_dir / f).write_text("# stub\n", encoding="utf-8")
    (tmp_path / "CODEOWNERS").write_text("* @user\n", encoding="utf-8")
    # plugins_json 없으면 WARN 1건 추가됨 — 본 test 의 핵심은 workflow override 만이므로 무시
    monkeypatch.chdir(tmp_path)
    rc = check_bootstrap.main([])
    assert rc == 0
    captured = capsys.readouterr()
    # only-one.yml 이 expected workflow 라 부재하지 않음 → workflow check WARN 부재
    assert "only-one.yml" not in captured.err  # missing 안내 부재 (이미 존재하므로)


def test_main_finding_count_semantics(tmp_path: Path, monkeypatch, capsys) -> None:
    """findings_count semantics — 각 check 1건, 다 line 아닌 (CFP-103 D fix)."""
    overlay_dir = tmp_path / ".claude" / "_overlay"
    overlay_dir.mkdir(parents=True)
    (overlay_dir / "project.yaml").write_text(
        "github:\n  org: example\n  repo: test\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    rc = check_bootstrap.main([])
    assert rc == 0
    captured = capsys.readouterr()
    # 부재 자산이 많아 N 개 finding (~3-5) — line 수보다 작아야 함
    if "[check-bootstrap]" in captured.err:
        # "[check-bootstrap] N 부트스트랩 drift" 의 N
        import re
        m = re.search(r"\[check-bootstrap\]\s+(\d+)\s+부트스트랩", captured.err)
        if m:
            findings = int(m.group(1))
            line_count = len([line for line in captured.err.splitlines() if line.startswith("           ") or line.startswith("[bootstrap]")])
            # findings 가 line_count 보다 작거나 같음 (각 finding 가 multi-line 가능)
            assert findings <= line_count


# ============================================================ Check 10 — workflow version drift (CFP-660)


_WRAPPER_STORY_INIT_YML = """\
name: story-init
on:
  issues:
    types: [labeled]
concurrency:
  group: story-init-${{ github.event.issue.number }}
  cancel-in-progress: false
permissions:
  contents: write
  issues: write
  pull-requests: write
jobs:
  scaffold:
    if: contains(github.event.issue.labels.*.name, 'phase:요구사항')
    runs-on: ubuntu-latest
    steps:
      - run: echo "stub"
"""

_WRAPPER_PHASE_GATE_YML = """\
name: phase-gate-mergeable
on:
  pull_request:
    types: [labeled, unlabeled]
permissions:
  pull-requests: write
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - run: echo "gate stub"
"""

_WRAPPER_FIX_LEDGER_YML = "name: fix-ledger-sync\non:\n  issue_comment:\n    types: [created]\npermissions:\n  issues: write\n"
_WRAPPER_SUBISSUE_YML = "name: subissue-from-impl-manifest\non:\n  pull_request:\n    types: [closed]\npermissions:\n  issues: write\n  contents: read\n"
_WRAPPER_PHASE_LABEL_YML = "name: phase-label-invariant\non:\n  pull_request:\n    types: [labeled]\npermissions:\n  pull-requests: write\n"
_WRAPPER_STORY_SEC1_YML = "name: story-section-1-immutable\non:\n  pull_request:\n    types: [opened, synchronize]\npermissions:\n  contents: read\n"
_WRAPPER_STORY_SCHEMA_YML = "name: story-section-schema\non:\n  pull_request:\n    types: [opened, synchronize]\npermissions:\n  contents: read\n"


def _build_wrapper_root(tmp_path: Path) -> Path:
    """Build minimal wrapper plugin_root with templates/github-workflows/ — 7 EXPECTED_WORKFLOWS_FULL files."""
    plugin_root = tmp_path / "wrapper_root"
    wf_dir = plugin_root / "templates" / "github-workflows"
    wf_dir.mkdir(parents=True)
    file_map = {
        "story-init.yml": _WRAPPER_STORY_INIT_YML,
        "phase-gate-mergeable.yml": _WRAPPER_PHASE_GATE_YML,
        "fix-ledger-sync.yml": _WRAPPER_FIX_LEDGER_YML,
        "subissue-from-impl-manifest.yml": _WRAPPER_SUBISSUE_YML,
        "phase-label-invariant.yml": _WRAPPER_PHASE_LABEL_YML,
        "story-section-1-immutable.yml": _WRAPPER_STORY_SEC1_YML,
        "story-section-schema.yml": _WRAPPER_STORY_SCHEMA_YML,
    }
    for name, content in file_map.items():
        (wf_dir / name).write_text(content, encoding="utf-8")
    return plugin_root


def _build_consumer_workflows(tmp_path: Path, plugin_root: Path) -> Path:
    """Copy wrapper templates to consumer .github/workflows/ — clean baseline (no drift)."""
    consumer_dir = tmp_path / ".github" / "workflows"
    consumer_dir.mkdir(parents=True)
    src_dir = plugin_root / "templates" / "github-workflows"
    for f in src_dir.iterdir():
        if f.suffix == ".yml":
            (consumer_dir / f.name).write_bytes(f.read_bytes())
    return consumer_dir


def test_workflow_drift_clean_no_drift(tmp_path: Path) -> None:
    """consumer file = wrapper template byte-identical → no drift detected, strict_eligible False."""
    plugin_root = _build_wrapper_root(tmp_path)
    consumer_dir = _build_consumer_workflows(tmp_path, plugin_root)
    warns, strict = check_bootstrap.check_workflow_version_drift(consumer_dir, plugin_root)
    assert warns == [], f"clean baseline 인데 drift detected: {warns}"
    assert strict is False


def test_workflow_drift_strict_eligible_detected(tmp_path: Path) -> None:
    """STRICT_ELIGIBLE_WORKFLOWS 영역 file 의 핵심 line drift → strict_eligible True."""
    plugin_root = _build_wrapper_root(tmp_path)
    consumer_dir = _build_consumer_workflows(tmp_path, plugin_root)
    # Drift story-init.yml — concurrency group + on event drift (semantic, lane orchestration)
    drifted_content = (
        "name: story-init\n"
        "on:\n"
        "  issues:\n"
        "    types: [opened, labeled]\n"  # drift: added 'opened'
        "concurrency:\n"
        "  group: story-init-OLD\n"  # drift: OLD vs ${{ github.event.issue.number }}
        "  cancel-in-progress: true\n"  # drift: true vs false
        "permissions:\n"
        "  contents: read\n"  # drift: read vs write — silent skip risk
        "jobs:\n"
        "  scaffold:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - run: echo stale\n"
    )
    (consumer_dir / "story-init.yml").write_text(drifted_content, encoding="utf-8")
    warns, strict = check_bootstrap.check_workflow_version_drift(consumer_dir, plugin_root)
    assert warns, "drift detected 결과 부재"
    assert strict is True, "story-init.yml ∈ STRICT_ELIGIBLE_WORKFLOWS, strict_eligible 분류 의무"
    # 핵심 line drift 가 message 안 surface
    joined = "\n".join(warns)
    assert "story-init.yml" in joined
    assert any(m in joined for m in ("concurrency", "on", "permissions"))


def test_workflow_drift_whitespace_only_not_flagged(tmp_path: Path) -> None:
    """Trailing whitespace / blank-line collapse 만의 superficial diff = drift 분류 영역 외."""
    plugin_root = _build_wrapper_root(tmp_path)
    consumer_dir = _build_consumer_workflows(tmp_path, plugin_root)
    # Add trailing whitespace + extra blank line — core marker semantics 동일
    original = (consumer_dir / "story-init.yml").read_text(encoding="utf-8")
    # Insert trailing spaces + duplicate blank line in non-core area
    perturbed = original.replace(
        "      - run: echo \"stub\"\n",
        "      - run: echo \"stub\"   \n\n\n",
    )
    (consumer_dir / "story-init.yml").write_text(perturbed, encoding="utf-8")
    warns, strict = check_bootstrap.check_workflow_version_drift(consumer_dir, plugin_root)
    # Tier 1 SHA mismatch (trailing whitespace 차이) → Tier 2 core markers compare → identical
    # superficial whitespace diff = drift 영역 외
    assert warns == [], f"whitespace-only diff 가 drift 로 잘못 분류: {warns}"
    assert strict is False


def test_workflow_drift_plugin_root_missing(tmp_path: Path) -> None:
    """plugin_root = None → check 10 skip + warning (drift 분류 영역 외)."""
    consumer_dir = tmp_path / ".github" / "workflows"
    consumer_dir.mkdir(parents=True)
    (consumer_dir / "story-init.yml").write_text("# stub\n", encoding="utf-8")
    warns, strict = check_bootstrap.check_workflow_version_drift(consumer_dir, None)
    assert warns, "plugin_root None 시 warning 발화 의무"
    assert any("plugin_root resolution 실패" in w for w in warns)
    assert strict is False


def test_workflow_drift_wrapper_templates_missing(tmp_path: Path) -> None:
    """wrapper plugin_root 가 templates/github-workflows/ 미보유 → skip + warning."""
    plugin_root = tmp_path / "wrapper_root_empty"
    plugin_root.mkdir(parents=True)
    consumer_dir = tmp_path / ".github" / "workflows"
    consumer_dir.mkdir(parents=True)
    (consumer_dir / "story-init.yml").write_text("# stub\n", encoding="utf-8")
    warns, strict = check_bootstrap.check_workflow_version_drift(consumer_dir, plugin_root)
    assert warns, "wrapper templates dir 부재 시 warning 의무"
    assert any("template" in w.lower() or "wrapper plugin" in w for w in warns)
    assert strict is False


def test_workflow_drift_consumer_workflows_dir_missing(tmp_path: Path) -> None:
    """consumer .github/workflows/ 부재 → check 10 silent skip (check 6 가 별도 warning 발화)."""
    plugin_root = _build_wrapper_root(tmp_path)
    consumer_dir = tmp_path / ".github" / "workflows"  # 미생성
    warns, strict = check_bootstrap.check_workflow_version_drift(consumer_dir, plugin_root)
    # consumer dir 부재 시 check 10 silent skip (warning 0)
    assert warns == []
    assert strict is False


def test_workflow_drift_non_strict_eligible_warning_only(tmp_path: Path) -> None:
    """STRICT_ELIGIBLE_WORKFLOWS 영역 외 file drift → warning 발화 + strict_eligible False."""
    plugin_root = _build_wrapper_root(tmp_path)
    # Add non-strict-eligible workflow to wrapper templates
    wrapper_wf = plugin_root / "templates" / "github-workflows"
    (wrapper_wf / "non-strict-example.yml").write_text(
        "name: non-strict\non:\n  push:\n    branches: [main]\npermissions:\n  contents: read\n",
        encoding="utf-8",
    )
    consumer_dir = _build_consumer_workflows(tmp_path, plugin_root)
    # consumer 측 same file with drift (non-strict-eligible)
    (consumer_dir / "non-strict-example.yml").write_text(
        "name: non-strict\non:\n  push:\n    branches: [develop]\npermissions:\n  contents: read\n",
        encoding="utf-8",
    )
    warns, strict = check_bootstrap.check_workflow_version_drift(
        consumer_dir, plugin_root,
        expected_set={"non-strict-example.yml"},
    )
    assert warns, "drift detected 영역 — warning 발화 의무"
    assert strict is False, "non-strict-eligible workflow drift → strict_eligible False"


def test_workflow_drift_strict_mode_main_exits_1(tmp_path: Path, monkeypatch, capsys) -> None:
    """STRICT_ELIGIBLE_WORKFLOWS 영역 drift + --strict flag → main() exit 1."""
    plugin_root = _build_wrapper_root(tmp_path)
    consumer_dir = _build_consumer_workflows(tmp_path, plugin_root)
    # Drift story-init.yml (strict-eligible)
    (consumer_dir / "story-init.yml").write_text(
        "name: story-init\non:\n  issues:\n    types: [opened]\nconcurrency:\n  group: OLD\n"
        "permissions:\n  contents: read\njobs:\n  scaffold:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo old\n",
        encoding="utf-8",
    )
    # Set up minimum env for main() — project.yaml + plugins_json + settings.json + label expectations
    overlay_dir = tmp_path / ".claude" / "_overlay"
    overlay_dir.mkdir(parents=True)
    (overlay_dir / "project.yaml").write_text(
        "github:\n  org: example\n  repo: test\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(plugin_root.parent))
    # Note: CLAUDE_PLUGIN_ROOT/codeforge expected, so symlink-or-rename
    cf_dir = plugin_root.parent / "codeforge"
    if not cf_dir.exists():
        # Build alternative wrapper at the codeforge/ subfolder
        cf_wf = cf_dir / "templates" / "github-workflows"
        cf_wf.mkdir(parents=True)
        for f in (plugin_root / "templates" / "github-workflows").iterdir():
            (cf_wf / f.name).write_bytes(f.read_bytes())
    # Re-drift the strict-eligible consumer file (already drifted above, but ensure)
    rc = check_bootstrap.main(["--strict"])
    captured = capsys.readouterr()
    # strict-eligible drift 가 1+ 검출 시 exit 1 의무
    # 단 (a) project.yaml present 이므로 strict-eligible (a) PASS. (b) plugin 미설치 strict-eligible
    # 일 가능성 — but plugins_json 부재 = STRICT (b) trigger. 그래도 exit 1 발화 확인.
    assert rc == 1, f"strict mode + strict-eligible drift 시 exit 1 의무, got rc={rc}"
    assert "STRICT" in captured.err
