#!/usr/bin/env python3
"""check_bootstrap.py — Consumer 환경 부트스트랩 정합 진단 (non-blocking).

Cross-platform Python core. POSIX bash (`check-bootstrap.sh`) + Windows
PowerShell (`check-bootstrap.ps1`) wrapper 둘 다 본 모듈을 호출.

CFP-103 (Phase 2a of CFP-96 Epic). 8 check:
  1. Workflow permissions (org-level) — 기존 (CFP-11)
  2. 18 plugin label 존재 — 기존 (CFP-11)
  3. workflow_distribution.mode=degraded missing_workflows 안내 — 기존 (CFP-86/89/95)
  4. consumer-scripts manifest drift — 기존 (CFP-97)
  5. 11 plugin install (~/.claude/plugins/installed_plugins.json) — NEW (CFP-103)
  6. consumer .github/workflows/ file 존재 — NEW (CFP-103)
  7. consumer .github/ISSUE_TEMPLATE/ 3종 sync — NEW (CFP-103)
  8. consumer CODEOWNERS 정합 — NEW (CFP-103)

Non-blocking: 발견된 drift 는 WARN 으로만 출력 (stderr). exit 0.

Skip 조건 (기존):
  - gh CLI 미설치 (check 1+2 skip)
  - gh auth status 실패 (check 1+2 skip)
  - .claude/_overlay/project.yaml 부재 (전체 skip)

Required 의존: PyYAML (project.yaml parse, validate_config.py 와 동일).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

REQUIRED_LABELS = [
    "type:epic", "type:story", "type:bug", "impl-manifest",
    "phase:요구사항", "phase:설계", "phase:설계-리뷰", "phase:구현",
    "phase:구현-리뷰", "phase:구현-테스트", "phase:보안-테스트",
    "gate:design-review-pass", "gate:security-test-pass",
    "fix:설계-리뷰-retry", "fix:구현-리뷰-retry",
    "fix:구현-테스트-retry", "fix:보안-테스트-retry",
    "audit:post-hotfix",
]

REQUIRED_PLUGINS = {
    # codeforge family 7 (wrapper + 6 lane)
    "codeforge@mclayer",
    "codeforge-requirements@mclayer",
    "codeforge-design@mclayer",
    "codeforge-develop@mclayer",
    "codeforge-test@mclayer",
    "codeforge-review@mclayer",
    "codeforge-pmo@mclayer",
    # 4 dependencies (integration SSOT: docs/superpowers-integration.md):
    #   github             — GitHub MCP tool exposure
    #   codex              — CodexReviewAgent (review lane) + Sonnet decider 5-step
    #   superpowers        — 17 lane agent x 7 skill (writing-plans / brainstorming / TDD / ...)
    #   claude-md-management — CLAUDE.md maintenance skill
    "github@claude-plugins-official",
    "codex@openai-codex",
    "superpowers@claude-plugins-official",
    "claude-md-management@claude-plugins-official",
}

EXPECTED_WORKFLOWS_FULL = {
    "phase-gate-mergeable.yml",
    "phase-label-invariant.yml",
    "story-init.yml",  # CFP-105 close 후 consumer-distributable
    "story-section-1-immutable.yml",  # CFP-105
    "subissue-from-impl-manifest.yml",  # CFP-105
    "fix-ledger-sync.yml",  # CFP-105
    "story-section-schema.yml",  # CFP-94
}

EXPECTED_FORMS = {"audit.yml", "bug.yml", "story.yml"}

CODEOWNERS_LINE_PATTERN = re.compile(r"^[^\s#]+\s+@[\w\-/]+(?:\s+@[\w\-/]+)*\s*$")


def _resolve_overlay_yaml(env: dict[str, str]) -> Path:
    raw = env.get("OVERLAY_PROJECT_YAML") or ".claude/_overlay/project.yaml"
    return Path(raw)


def _resolve_plugins_json(env: dict[str, str]) -> Path:
    """OS branch path resolution.

    Linux/macOS: ~/.claude/plugins/installed_plugins.json
    Windows: $env:USERPROFILE/.claude/plugins/installed_plugins.json
    WSL/dual-env: HOME + USERPROFILE 둘 다 set — 둘 다 try, 첫 file 존재 path 반환.
    """
    candidates: list[str] = [v for v in (env.get("HOME"), env.get("USERPROFILE")) if v]
    for c in candidates:
        p = Path(c) / ".claude" / "plugins" / "installed_plugins.json"
        if p.is_file():
            return p
    # Fallback: 둘 다 file 미존재. 첫 candidate 반환 (main 측에서 WARN 처리).
    if candidates:
        return Path(candidates[0]) / ".claude" / "plugins" / "installed_plugins.json"
    return Path(".claude") / "plugins" / "installed_plugins.json"


def _resolve_plugin_root(env: dict[str, str], script_path: Path) -> Path | None:
    """Plugin root resolution (regen-agents.sh 동일 priority).

    1. CLAUDE_PLUGIN_ROOT/codeforge
    2. script's parent ../..
    """
    cpr = env.get("CLAUDE_PLUGIN_ROOT")
    if cpr and (Path(cpr) / "codeforge").is_dir():
        return Path(cpr) / "codeforge"
    fallback = script_path.parent.parent
    if fallback.is_dir():
        return fallback
    return None


# ---------------------------------------------------------------------- check 1


def check_workflow_permissions(org: str, repo: str) -> list[str]:
    """기존 check 1 — gh api repos/<org>/<repo>/actions/permissions/workflow."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{org}/{repo}/actions/permissions/workflow"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        default_perm = data.get("default_workflow_permissions", "")
        can_approve = data.get("can_approve_pull_request_reviews", False)
        if default_perm != "write" or not can_approve:
            return [
                f"[bootstrap] WARN: Workflow permissions 미설정 (default={default_perm}, can_approve={can_approve})",
                "           → consumer-guide §2f 참조: 'Allow GitHub Actions to create and approve pull requests' 활성화",
                "           → 미해결 시 story-init.yml의 PR auto-create step이 fail",
            ]
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        pass
    return []


# ---------------------------------------------------------------------- check 2


def check_plugin_labels(org: str, repo: str) -> list[str]:
    """기존 check 2 — 18 plugin label 존재."""
    try:
        result = subprocess.run(
            ["gh", "label", "list", "--limit", "100", "--repo", f"{org}/{repo}",
             "--json", "name", "-q", "[.[].name]"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return []
        existing = set(json.loads(result.stdout))
        missing = [lbl for lbl in REQUIRED_LABELS if lbl not in existing]
        if missing:
            warns = [
                f"[bootstrap] WARN: {len(missing)}/18 plugin label 부재",
            ]
            if len(missing) <= 5:
                warns.append(f"           누락: {' '.join(missing)}")
            else:
                warns.append(f"           누락 상위 5: {' '.join(missing[:5])} ...")
            warns.extend([
                "           → 'bash scripts/bootstrap-labels.sh' 1회 실행 (또는 consumer-guide §2d 참조)",
                "           → 미해결 시 Issue Form 제출 시 'label not found' 에러",
            ])
            return warns
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------- check 3


def check_workflow_distribution(yaml_path: Path) -> list[str]:
    """기존 check 3 — workflow_distribution.mode=degraded 안내."""
    try:
        import yaml
    except ImportError:
        return []
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        wd = data.get("workflow_distribution", {})
        mode = wd.get("mode", "full")
        missing = wd.get("missing_workflows", []) or []
        if mode == "degraded":
            warns = [
                "[bootstrap] WARN: workflow_distribution.mode=degraded (CFP-86 Path B)",
            ]
            if missing:
                warns.append(f"           Missing workflows: {','.join(missing)}")
            warns.extend([
                "           → consumer-guide §2c 'Path A vs Path B' 표 manual compensating check 의무",
                "           → Path B 사용 사례: mctrader-hub (story-init / fix-ledger-sync / subissue-from-impl-manifest / story-section-1-immutable 부재)",
                "           → Path A upgrade: 'cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<missing>.yml .github/workflows/'",
            ])
            return warns
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------- check 4


def check_consumer_scripts_manifest(plugin_root: Path, overlay_yaml: Path | None = None) -> list[str]:
    """기존 check 4 — consumer-scripts manifest drift (CFP-97 / CFP-109 / CFP-110).

    CFP-109: schema 확장 `<script-path>[:<dependent-workflow-path>]` parse +
             degraded suppression (workflow basename ∈ workflow_distribution.missing_workflows).
    CFP-110: SessionStart auto-copy (regen-agents.sh) 가 정상 작동 시 자동 install →
             본 WARN 발화 = hook 미실행 / 실패 / 의도적 부재. Manual copy = fallback.
    """
    manifest_path = plugin_root / "templates" / "consumer-scripts.manifest"
    if not manifest_path.is_file():
        return []

    # CFP-109: workflow_distribution.missing_workflows for degraded suppression
    wd_missing: set[str] = set()
    if overlay_yaml is not None and overlay_yaml.is_file():
        try:
            import yaml
            data = yaml.safe_load(overlay_yaml.read_text(encoding="utf-8")) or {}
            wd = data.get("workflow_distribution", {})
            wd_missing = {x for x in (wd.get("missing_workflows") or []) if isinstance(x, str)}
        except Exception:
            pass

    missing = []
    try:
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # CFP-109: parse script-path[:dep-workflow]
            if ":" in line:
                script_path, _, dep_workflow = line.partition(":")
            else:
                script_path, dep_workflow = line, ""
            # Path traversal + leading-dash guard (CFP-97 P1 + CFP-112 AREA 4b)
            if (
                script_path.startswith("/")
                or ".." in script_path
                or not script_path
                or script_path.startswith("-")
            ):
                continue
            if Path(script_path).is_file():
                continue
            # CFP-109 degraded suppression — basename ∈ missing_workflows
            if dep_workflow and wd_missing:
                dep_basename = Path(dep_workflow).name
                if dep_basename in wd_missing:
                    continue
            missing.append(script_path)
    except Exception:
        return []

    if missing:
        return [
            f"[bootstrap] WARN: {len(missing)} consumer-distributable script(s) 부재 (CFP-97 / CFP-109 / CFP-110)",
            f"           누락: {' '.join(missing)}",
            "           → CFP-110 SessionStart auto-copy (regen-agents.sh) 가 정상 작동 시 자동 install",
            "           → 본 WARN 발화 = hook 미실행 / regen-agents.sh 실패 / 의도적 부재. fallback = consumer-guide §2c manifest-driven copy 실행",
            "           → 미해결 시 해당 script 의존 workflow (예: story-section-schema.yml) 가 lint skip + warning",
        ]
    return []


# ---------------------------------------------------------------------- check 5


def check_plugins_installed(plugins_json: Path) -> list[str]:
    """CFP-103 NEW check 5 — 11 plugin install 검사.

    codeforge family 7 (wrapper + 6 lane) + 4 dependency = 11.
    """
    if not plugins_json.is_file():
        return [
            f"[bootstrap] WARN: {plugins_json} 부재",
            "           → Claude Code 미설치 또는 plugin 0개 등록 상태",
            "           → /plugins install 명령 안내: consumer-guide §1a 참조",
        ]
    try:
        data = json.loads(plugins_json.read_text(encoding="utf-8"))
        installed = set(data.get("plugins", {}).keys())
    except (json.JSONDecodeError, Exception):
        return [
            f"[bootstrap] WARN: {plugins_json} parse 실패 (malformed JSON)",
        ]
    missing = REQUIRED_PLUGINS - installed
    if missing:
        warns = [
            f"[bootstrap] WARN: {len(missing)}/{len(REQUIRED_PLUGINS)} plugin 미설치 (CFP-103)",
        ]
        if len(missing) <= 5:
            warns.append(f"           누락: {' '.join(sorted(missing))}")
        else:
            sorted_missing = sorted(missing)
            warns.append(f"           누락 상위 5: {' '.join(sorted_missing[:5])} ... ({len(missing) - 5} more)")
        warns.append("           → 설치 명령 (각 plugin):")
        for p in sorted(missing):
            warns.append(f"              /plugins install {p}")
        warns.extend([
            "           → consumer-guide §1a 'codeforge family 11 plugin install' 참조",
            "           → superpowers 의존 SSOT: docs/superpowers-integration.md",
            "           → 미해결 시 6 lane orchestration 작동 불가, manual workaround 회귀",
        ])
        return warns
    return []


# ---------------------------------------------------------------------- check 6


def check_consumer_workflows(workflows_dir: Path, expected_set: set[str] | None = None) -> list[str]:
    """CFP-103 NEW check 6 — consumer .github/workflows/ file 존재."""
    expected = expected_set if expected_set is not None else EXPECTED_WORKFLOWS_FULL
    if not workflows_dir.is_dir():
        return [
            f"[bootstrap] WARN: {workflows_dir} 디렉토리 부재",
            "           → consumer 측 GitHub Actions workflow 0개 — phase-gate / story-flow 모두 비활성",
        ]
    existing = {p.name for p in workflows_dir.iterdir() if p.is_file() and p.suffix == ".yml"}
    missing = expected - existing
    if missing:
        return [
            f"[bootstrap] WARN: {len(missing)}/{len(expected)} consumer workflow 부재",
            f"           누락: {' '.join(sorted(missing))}",
            "           → cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<missing>.yml .github/workflows/",
            "           → 또는 project.yaml workflow_distribution.mode=degraded + missing_workflows 명시",
        ]
    return []


# ---------------------------------------------------------------------- check 7


def check_consumer_issue_forms(forms_dir: Path) -> list[str]:
    """CFP-103 NEW check 7 — consumer .github/ISSUE_TEMPLATE/ 3종 sync."""
    if not forms_dir.is_dir():
        return [
            f"[bootstrap] WARN: {forms_dir} 디렉토리 부재",
            "           → consumer 측 Issue Form 0개 — Story-flow workflow 트리거 불가",
        ]
    existing = {p.name for p in forms_dir.iterdir() if p.is_file() and p.suffix == ".yml"}
    missing = EXPECTED_FORMS - existing
    if missing:
        return [
            f"[bootstrap] WARN: {len(missing)}/3 Issue Form 부재",
            f"           누락: {' '.join(sorted(missing))}",
            "           → cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-issue-forms/<missing>.yml .github/ISSUE_TEMPLATE/",
        ]
    return []


# ---------------------------------------------------------------------- check 8


def check_codeowners(*paths: Path) -> list[str]:
    """CFP-103 NEW check 8 — consumer CODEOWNERS 정합.

    위치 candidate: repo root / .github/ / docs/ 중 하나.
    """
    found_path = None
    for p in paths:
        if p.is_file():
            found_path = p
            break
    if found_path is None:
        return [
            "[bootstrap] WARN: CODEOWNERS 부재",
            f"           검색 위치: {' / '.join(str(p) for p in paths)}",
            "           → cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/CODEOWNERS.template <위치>/CODEOWNERS",
        ]
    try:
        content = found_path.read_text(encoding="utf-8")
    except Exception:
        return [f"[bootstrap] WARN: {found_path} 읽기 실패"]
    valid_lines = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if CODEOWNERS_LINE_PATTERN.match(line):
            valid_lines += 1
    if valid_lines == 0:
        return [
            f"[bootstrap] WARN: {found_path} 비어 있거나 invalid format",
            "           → 'path @user-or-team' 형식 1줄 이상 필요",
        ]
    return []


# --------------------------------------------------------------------- helpers


def _gh_available() -> bool:
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def _extract_org_repo(yaml_path: Path) -> tuple[str, str]:
    try:
        import yaml
    except ImportError:
        return "", ""
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        gh = data.get("github", {})
        return gh.get("org", ""), gh.get("repo", "")
    except Exception:
        return "", ""


# ----------------------------------------------------------------------- main


def main() -> int:
    """Entry point. Print WARN 모음 to stderr. Exit 0 (non-blocking)."""
    env = dict(os.environ)
    overlay_yaml = _resolve_overlay_yaml(env)

    # Skip 조건: project.yaml 부재 → consumer 초기 설정 단계, silent skip.
    if not overlay_yaml.is_file():
        return 0

    plugin_root = _resolve_plugin_root(env, Path(__file__).resolve())
    plugins_json = _resolve_plugins_json(env)
    org, repo = _extract_org_repo(overlay_yaml)

    # Each check returns list[str] — empty = no finding, non-empty = 1 finding (multi-line).
    # findings_count = check 별 1건씩 (기존 sh WARN_COUNT semantic 보존, CFP-103 D fix).
    gh_ready = _gh_available() and bool(org) and bool(repo)

    # project.yaml override for expected workflows
    expected_workflows = EXPECTED_WORKFLOWS_FULL
    try:
        import yaml
        data = yaml.safe_load(overlay_yaml.read_text(encoding="utf-8")) or {}
        bs_section = data.get("bootstrap", {})
        override = bs_section.get("expected_workflows")
        if override:
            expected_workflows = set(override)
    except Exception:
        pass

    all_results: list[list[str]] = [
        check_workflow_permissions(org, repo) if gh_ready else [],
        check_plugin_labels(org, repo) if gh_ready else [],
        check_workflow_distribution(overlay_yaml),
        check_consumer_scripts_manifest(plugin_root, overlay_yaml) if plugin_root is not None else [],
        check_plugins_installed(plugins_json),
        check_consumer_workflows(Path(".github/workflows"), expected_workflows),
        check_consumer_issue_forms(Path(".github/ISSUE_TEMPLATE")),
        check_codeowners(
            Path("CODEOWNERS"),
            Path(".github/CODEOWNERS"),
            Path("docs/CODEOWNERS"),
        ),
    ]
    findings_count = sum(1 for r in all_results if r)
    warnings = [line for r in all_results for line in r]

    if warnings:
        print(file=sys.stderr)
        print(
            f"[check-bootstrap] {findings_count} 부트스트랩 drift 발견 (non-blocking):",
            file=sys.stderr,
        )
        for w in warnings:
            print(w, file=sys.stderr)
        print(file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
