#!/usr/bin/env python3
"""check_bootstrap.py — Consumer 환경 부트스트랩 정합 진단 (default non-blocking, strict mode opt-in).

Cross-platform Python core. POSIX bash (`check-bootstrap.sh`) + Windows
PowerShell (`check-bootstrap.ps1`) wrapper 둘 다 본 모듈을 호출.

CFP-103 (Phase 2a of CFP-96 Epic). 10 check (CFP-660 NEW check 10):
  1. Workflow permissions (org-level) — 기존 (CFP-11)
  2. 15 plugin label 존재 — 기존 (CFP-11), CFP-2250: type:* native Issue Type 이관 (type 3 row 제거)
  3. workflow_distribution.mode=degraded missing_workflows 안내 — 기존 (CFP-86/89/95)
  4. consumer-scripts manifest drift — 기존 (CFP-97)
  5. 10 plugin install (~/.claude/plugins/installed_plugins.json) — 기존 (CFP-103)
  6. consumer .github/workflows/ file 존재 — 기존 (CFP-103)
  7. consumer .github/ISSUE_TEMPLATE/ 3종 sync — 기존 (CFP-103)
  8. consumer CODEOWNERS 정합 — 기존 (CFP-103)
  9. .claude/settings.json 의 SessionStart × 2 + UserPromptSubmit × 1 hook 등록 — CFP-127
  10. consumer .github/workflows/<name>.yml SHA / 핵심 line drift vs wrapper templates — NEW (CFP-660)

Default non-blocking: 발견된 drift 는 WARN 으로만 출력 (stderr). exit 0. ADR-027 §결정 2 정합.

Strict mode opt-in (CFP-127 / ADR-032 amendment 1, CFP-660 / ADR-032 amendment 2):
  Priority CLI > env > yaml:
    1. CLI flag: `--strict`
    2. Env: `CODEFORGE_STRICT_BOOTSTRAP=1`
    3. YAML: `bootstrap.strict_mode: true` (.claude/_overlay/project.yaml)
  Strict-eligible drift (5종 — CFP-660 4 → 5 종 확장):
    (a) project.yaml 부재 → exit 1
    (b) plugin 10종 중 wrapper(1) + 6 lane(6) = 7 critical 미설치 → exit 1
    (c) settings.json 의 3 hook 미등록 → exit 1
    (d) 15 label 중 phase:* (7) + gate:* (3) = 10 critical 부재 → exit 1
    (e) consumer workflow version drift — stale `.github/workflows/<name>.yml` vs wrapper
        templates SHA / 핵심 line mismatch (CFP-660 / ADR-032 amendment 2 §결정 6) → exit 1
  Bypass precedence: HOTFIX_BYPASS_CODEFORGE=1 + REASON 양 env set → strict 무관 hook self skip.

Skip 조건 (기존):
  - gh CLI 미설치 (check 1+2 skip)
  - gh auth status 실패 (check 1+2 skip)
  - .claude/_overlay/project.yaml 부재 (default mode = silent skip / strict mode = exit 1)
  - plugin_root resolution 실패 (check 4 + check 10 skip)

Required 의존: PyYAML (project.yaml parse, validate_config.py 와 동일).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

# CFP-2250 / ADR-049 — type:epic/story/bug 는 native GitHub Issue Type (org-level) 으로 이관.
# bootstrap-labels.sh 가 더 이상 생성하지 않으므로 REQUIRED_LABELS 에 잔존 시 check 2 가 항상
# "부재" 로 오탐. type 3 row 제거 (15 종 잔존). impl-manifest 는 별 axis (sub-issue marker) 라 보존.
REQUIRED_LABELS = [
    "impl-manifest",
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
    # 3 dependencies (ADR-122 — superpowers 의존 완전 제거, discipline codeforge native 흡수):
    #   github             — GitHub MCP tool exposure
    #   codex              — CodexReviewAgent (review lane) + Sonnet decider 5-step
    #   claude-md-management — CLAUDE.md maintenance skill
    "github@claude-plugins-official",
    "codex@openai-codex",
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

# CFP-127 / ADR-032 — Strict-eligible plugin subset (7 critical = wrapper + 6 lane)
# CFP-2249 / ADR-032 amendment 3 — superpowers 제거 (ADR-122 의존 완전 제거): 8 → 7
STRICT_ELIGIBLE_PLUGINS = {
    "codeforge@mclayer",
    "codeforge-requirements@mclayer",
    "codeforge-design@mclayer",
    "codeforge-develop@mclayer",
    "codeforge-test@mclayer",
    "codeforge-review@mclayer",
    "codeforge-pmo@mclayer",
}

# CFP-127 / ADR-032 — Strict-eligible label subset (10 critical = phase:* 7 + gate:* 3)
STRICT_ELIGIBLE_LABELS = {
    "phase:요구사항", "phase:설계", "phase:설계-리뷰", "phase:구현",
    "phase:구현-리뷰", "phase:구현-테스트", "phase:보안-테스트",
    "gate:design-review-pass", "gate:security-test-pass", "gate:live-entry-pass",
}

# CFP-660 / ADR-032 amendment 2 — Strict-eligible workflow subset for check 10
# (consumer .github/workflows/<name>.yml SHA / 핵심 line drift vs wrapper templates)
# 본 set 는 EXPECTED_WORKFLOWS_FULL 의 subset — lane orchestration semantics 영향 직접인 file 만.
# story-section-schema.yml / fix-ledger-sync.yml 는 schema check / mirror 영역 — 별 set 검토.
STRICT_ELIGIBLE_WORKFLOWS = {
    "phase-gate-mergeable.yml",      # gate label transition — race-prone if stale
    "phase-label-invariant.yml",     # phase label transition invariant — silent skip vector
    "story-init.yml",                # Story scaffold + KEY 발급 atomic (ADR-036)
    "story-section-1-immutable.yml", # §1 verbatim invariant
    "subissue-from-impl-manifest.yml", # Impl Manifest sub-issue creation
    "fix-ledger-sync.yml",           # FIX Ledger mirror — counter collision vector
    "story-section-schema.yml",      # CFP-94 schema check
}

# CFP-2432 / ADR-042 Amendment 16 — Story-shape 조건부 model tier wrapper-floor SSOT.
# consumer overlay 의 story_stakes.* 는 보수 방향(opus 강제)만 honor — down-tier(opus→sonnet)
#   공격적 override 는 schema-gate (check (f)) 가 거부 (확장-only, ADR-127 §결정6).
# 본 map = "consumer 가 약화 못 하는 agent 의 wrapper floor tier" SSOT.
#   tier 사다리: haiku(1) < sonnet(2) < opus(3) — overlay 가 floor 미만 지정 = strict-eligible drift.
STORY_STAKES_TIER_RANK = {"haiku": 1, "sonnet": 2, "opus": 3}
# floor 미만 down-tier 금지 대상 agent (Amd16 = InfraOperationalArchitectAgent 단독, floor=opus).
#   향후 follow-up CFP 로 확장 가능 — 추가 = scope 확장(확장-only).
STORY_STAKES_AGENT_FLOOR = {
    "InfraOperationalArchitectAgent": "opus",
}

# CFP-660 / ADR-032 amendment 2 — Drift detection core marker lines (Tier 2 fallback when Tier 1 SHA unavailable)
# Normalized whitespace 비교 (trailing whitespace / blank line collapse) — superficial diff 무시.
WORKFLOW_CORE_MARKERS = (
    re.compile(r"^concurrency:", re.MULTILINE),
    re.compile(r"^on:", re.MULTILINE),
    re.compile(r"^permissions:", re.MULTILINE),
)


def _resolve_overlay_yaml(env: dict[str, str]) -> Path:
    raw = env.get("OVERLAY_PROJECT_YAML") or ".claude/_overlay/project.yaml"
    return Path(raw)


def _resolve_plugins_json(env: dict[str, str]) -> Path:
    """OS-aware 결정적 plugins.json path resolution (CFP-2250 결함2).

    Linux/macOS: ~/.claude/plugins/installed_plugins.json
    Windows: $env:USERPROFILE/.claude/plugins/installed_plugins.json

    WSL/dual-env (HOME ∧ USERPROFILE 둘 다 set + 양쪽 파일 존재) 비결정성 제거:
    고정 [HOME, USERPROFILE] 순서가 아니라 **OS 맥락 우선순위** 로 결정 —
      - Windows (os.name == 'nt'): USERPROFILE 우선 → HOME
      - POSIX: HOME 우선 → USERPROFILE
    동일 입력(os, env, 파일존재) → 동일 path (결정적). 우선 candidate 에 파일 존재 시 즉시 채택;
    우선 쪽 부재 + 차선 쪽 존재 시 차선 채택; 둘 다 부재 시 우선 candidate path 반환 (main 측 WARN).
    """
    home = env.get("HOME")
    userprofile = env.get("USERPROFILE")
    if os.name == "nt":
        ordered = [v for v in (userprofile, home) if v]
    else:
        ordered = [v for v in (home, userprofile) if v]
    for c in ordered:
        p = Path(c) / ".claude" / "plugins" / "installed_plugins.json"
        if p.is_file():
            return p
    # Fallback: 둘 다 file 미존재. OS-우선 candidate 반환 (결정적, main 측 WARN 처리).
    if ordered:
        return Path(ordered[0]) / ".claude" / "plugins" / "installed_plugins.json"
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
    """기존 check 2 — plugin label 존재 (len(REQUIRED_LABELS) 종, CFP-2250: type:* 제거)."""
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
                f"[bootstrap] WARN: {len(missing)}/{len(REQUIRED_LABELS)} plugin label 부재",
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


# ------------------------------------------------------------ check 11 (CFP-2432)


def check_story_stakes_overlay(yaml_path: Path) -> tuple[list[str], bool]:
    """check 11 (CFP-2432 / ADR-042 Amendment 16 / F-3) — story_stakes overlay down-tier 거부.

    Story-shape 조건부 model tier 의 schema-gate enforcement point. consumer overlay 는
      tier 를 보수 방향(opus 강제)으로만 override 가능 — down-tier(opus→sonnet) 공격적
      override 는 거부한다 (확장-only, ADR-127 §결정6 / AC-3 / INV-3).

    합법 형태 (확장-only):
      story_stakes:
        conservative_override:            # 특정 agent 를 강제 opus (보수 — 항상 허용)
          - InfraOperationalArchitectAgent

    거부 형태 (down-tier — strict-eligible drift):
      story_stakes:
        tier_override:                    # agent → floor 미만 tier 매핑 = 공격적 down-tier
          InfraOperationalArchitectAgent: sonnet   # floor=opus → sonnet 거부

    문서규칙 단독 불충분 (`pat_rotation_cadence_days` honor-system 선례 답습 금지) →
      2중 enforcement 중 (1) schema-gate 가 본 check. (2) spawn-time clamp 는
      scripts/check-stakes-tier-gating.sh (max(wrapper_floor, overlay)).

    Returns:
      (warnings_list, is_strict_eligible_drift)
      - warnings_list: empty if PASS, non-empty if down-tier 시도 검출
      - is_strict_eligible_drift: True if any down-tier override 검출 (strict mode → exit 1)
    """
    try:
        import yaml
    except ImportError:
        return ([], False)
    if not yaml_path.is_file():
        return ([], False)
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except Exception:
        # 파싱 불가 = 다른 check 가 보고. 본 check 는 보수적으로 통과 (false-positive 차단).
        return ([], False)

    ss = data.get("story_stakes")
    if not isinstance(ss, dict):
        return ([], False)   # 섹션 부재 = 현행 동작(wrapper floor 유지) — 정상 N/A

    violations: list[str] = []

    # tier_override 맵: agent → tier. floor 미만(rank 작음) 지정 = down-tier 거부.
    # F-CR-001 짝: bash check-stakes-tier-gating.sh 와 known-enum allowlist {haiku,sonnet,opus} 통일.
    #   미지 tier 는 recognized override 아님 — 양측 모두 보수 처리(bash=fail-safe opus / python=reject).
    #   기존 unknown→rank3(opus-equiv) fallback 은 garbage 토큰을 silent honor 하던 불일치 → 거부로 통일.
    tier_override = ss.get("tier_override")
    if isinstance(tier_override, dict):
        for agent, tier in tier_override.items():
            tier_norm = str(tier).strip().lower()
            floor = STORY_STAKES_AGENT_FLOOR.get(str(agent).strip(), "opus")
            floor_rank = STORY_STAKES_TIER_RANK.get(floor, 3)
            if tier_norm not in STORY_STAKES_TIER_RANK:
                # 미지 tier = recognized enum 아님 → 거부 (silent honor 차단, bash fail-safe 와 정합)
                violations.append(f"{agent}: '{tier_norm}' 미지 tier (known-enum {{haiku,sonnet,opus}} 아님)")
                continue
            req_rank = STORY_STAKES_TIER_RANK[tier_norm]
            if req_rank < floor_rank:
                violations.append(f"{agent}: {tier_norm} < wrapper_floor={floor}")

    if violations:
        warns = [
            f"[bootstrap] WARN: story_stakes overlay down-tier 거부 — {len(violations)}건 (CFP-2432 / ADR-042 Amd16, strict-eligible)",
        ]
        for v in violations:
            warns.append(f"           down-tier 시도: {v}")
        warns.extend([
            "           → consumer overlay 는 tier 를 보수 방향(opus 강제)으로만 override 가능 (확장-only, ADR-127 §결정6)",
            "           → down-tier(opus→sonnet) 공격적 override 불가 — 합법 형태 = story_stakes.conservative_override[] (강제 opus)",
            "           → low-stakes tier-flip 은 wrapper Orchestrator 의 4-AND shape 판정 전용 (consumer 자기보고 down-tier 차단)",
        ])
        return (warns, True)
    return ([], False)


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
        # CFP-2250 결함3 preflight: plugin_root 의 manifest 자체 부재 = wrapper plugin 미설치 /
        # PLUGIN_ROOT 오해석 = bootstrap 미완. silent return 대신 원인 명시 (story-init 발동 전 진단).
        return [
            "[bootstrap] WARN: wrapper plugin manifest 부재 — bootstrap 미완 또는 PLUGIN_ROOT 오해석 (CFP-2250 결함3)",
            f"           검색 위치: {manifest_path}",
            "           → wrapper plugin 설치 확인 (codeforge@mclayer) + 'bash scripts/bootstrap-consumer.sh' 1회 실행",
            "           → 미해결 시 consumer-distributable script preflight 검증 skip (story-init 의존 자산 누락 원인 불명)",
        ]

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
    """CFP-103 NEW check 5 — 10 plugin install 검사.

    codeforge family 7 (wrapper + 6 lane) + 3 dependency = 10.
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
            "           → consumer-guide §1a 'codeforge family 10 plugin install' 참조",
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


# ---------------------------------------------------------------------- check 9


def check_settings_hooks(settings_path: Path) -> tuple[list[str], bool]:
    """CFP-127 NEW check 9 — `.claude/settings.json` 의 3 hook 등록 검증.

    Strict-eligible (c): SessionStart × 2 (regen-agents + check-bootstrap) +
                         UserPromptSubmit × 1 (userprompt-reminder).

    Returns:
      (warnings_list, is_strict_eligible_drift)
      - warnings_list: empty if PASS, non-empty if drift
      - is_strict_eligible_drift: True if any of 3 hook 미등록 (strict mode → exit 1)
    """
    if not settings_path.is_file():
        return (
            [
                f"[bootstrap] WARN: {settings_path} 부재 (strict-eligible)",
                "           → CFP-125 quickstart: 'bash scripts/bootstrap-consumer.sh'",
                "           → 또는 manual: cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/settings.json.example .claude/settings.json",
                "           → 미해결 시 CFP-103/CFP-104 enforcement layer 자동 누락",
            ],
            True,
        )
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return (
            [
                f"[bootstrap] WARN: {settings_path} parse 실패 (malformed JSON, strict-eligible)",
                "           → templates/settings.json.example 정합 갱신",
            ],
            True,
        )
    hooks = data.get("hooks", {}) if isinstance(data, dict) else {}
    session_starts = hooks.get("SessionStart", []) if isinstance(hooks, dict) else []
    user_prompts = hooks.get("UserPromptSubmit", []) if isinstance(hooks, dict) else []

    found_regen = found_check = found_userprompt = False

    def _scan_entries(entries: list, found_keys: list[str]) -> list[str]:
        """Return found patterns from hook entries. Supports nested NESTED schema."""
        found = []
        if not isinstance(entries, list):
            return found
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            inner = entry.get("hooks", [])
            if isinstance(inner, list):
                for h in inner:
                    if isinstance(h, dict):
                        cmd = h.get("command", "")
                        if isinstance(cmd, str):
                            for k in found_keys:
                                if k in cmd:
                                    found.append(k)
        return found

    ss_found = _scan_entries(session_starts, ["regen-agents", "check-bootstrap"])
    up_found = _scan_entries(user_prompts, ["userprompt-reminder"])
    if "regen-agents" in ss_found:
        found_regen = True
    if "check-bootstrap" in ss_found:
        found_check = True
    if "userprompt-reminder" in up_found:
        found_userprompt = True

    missing = []
    if not found_regen:
        missing.append("SessionStart:regen-agents")
    if not found_check:
        missing.append("SessionStart:check-bootstrap")
    if not found_userprompt:
        missing.append("UserPromptSubmit:userprompt-reminder")

    if missing:
        return (
            [
                f"[bootstrap] WARN: settings.json 의 3 hook 중 {len(missing)} 개 미등록 (strict-eligible)",
                f"           누락: {' '.join(missing)}",
                "           → templates/settings.json.example 정합 갱신 (CFP-125 §2.2)",
                "           → 또는 'bash scripts/bootstrap-consumer.sh' 1회 실행",
                "           → 미해결 시 CFP-103/CFP-104 enforcement layer 자동 누락",
            ],
            True,
        )
    return ([], False)


# ---------------------------------------------------------------------- check 10


def _sha256_of_file(path: Path) -> str | None:
    """Return SHA-256 hex digest of file content, or None if read fails."""
    try:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()
    except Exception:
        return None


def _normalized_core_markers(content: str) -> dict[str, str]:
    """Extract core marker lines (concurrency / on / permissions) with normalized whitespace.

    Returns dict mapping marker_name -> normalized block content (line until next top-level key).
    Trailing whitespace stripped per line; blank lines collapsed.
    """
    result: dict[str, str] = {}
    if not isinstance(content, str):
        return result
    lines = content.splitlines()
    # Identify top-level key lines (col 0 + ends with ':' or starts with marker)
    top_level_starts: list[tuple[int, str]] = []  # (line_idx, key)
    for i, line in enumerate(lines):
        if not line:
            continue
        # Top-level key = no leading whitespace + ends with ':' (yaml grammar)
        stripped = line.rstrip()
        if stripped and not stripped.startswith((" ", "\t", "#")) and stripped.endswith(":"):
            key = stripped[:-1].strip()
            top_level_starts.append((i, key))
    # Extract block for each marker
    for marker_name in ("concurrency", "on", "permissions"):
        for idx, (line_idx, key) in enumerate(top_level_starts):
            if key == marker_name:
                end = top_level_starts[idx + 1][0] if idx + 1 < len(top_level_starts) else len(lines)
                block_lines = lines[line_idx:end]
                # Normalize: rstrip + collapse consecutive blank
                normalized = []
                prev_blank = False
                for bl in block_lines:
                    bl_stripped = bl.rstrip()
                    is_blank = not bl_stripped
                    if is_blank and prev_blank:
                        continue
                    normalized.append(bl_stripped)
                    prev_blank = is_blank
                result[marker_name] = "\n".join(normalized).rstrip()
                break
    return result


def check_workflow_version_drift(
    workflows_dir: Path,
    plugin_root: Path | None,
    expected_set: set[str] | None = None,
) -> tuple[list[str], bool]:
    """CFP-660 / ADR-032 amendment 2 — check 10 NEW: consumer workflow version drift.

    Tier 1 (primary): SHA-256 byte-identical compare consumer file vs wrapper template.
    Tier 2 (fallback when Tier 1 mismatch): core marker block (concurrency / on / permissions)
      normalized compare — surface semantic drift, suppress whitespace-only diff.

    Returns:
      (warnings_list, is_strict_eligible_drift)
      - warnings_list: empty if no drift, non-empty otherwise
      - is_strict_eligible_drift: True if any strict-eligible workflow drifted (strict mode → exit 1)

    Skip 조건 (warning + return):
      - plugin_root is None (CLAUDE_PLUGIN_ROOT unset + fallback dir 부재)
      - plugin_root/templates/github-workflows/ 부재 (wrapper templates 없음)
      - workflows_dir 부재 (consumer 측 workflow dir 자체 없음 — check 6 영역 별도)

    Args:
      workflows_dir: consumer `.github/workflows/`
      plugin_root: resolved wrapper plugin root (templates/github-workflows/ 의 parent.parent)
      expected_set: scan target workflow basenames (default = EXPECTED_WORKFLOWS_FULL)
    """
    expected = expected_set if expected_set is not None else EXPECTED_WORKFLOWS_FULL

    if plugin_root is None:
        return (
            [
                "[bootstrap] WARN: plugin_root resolution 실패 — check 10 (workflow drift) skip",
                "           → CLAUDE_PLUGIN_ROOT 환경변수 또는 fallback dir 확인",
            ],
            False,
        )

    wrapper_workflows_dir = plugin_root / "templates" / "github-workflows"
    if not wrapper_workflows_dir.is_dir():
        return (
            [
                f"[bootstrap] WARN: {wrapper_workflows_dir} 부재 — check 10 (workflow drift) skip",
                "           → wrapper plugin install 확인 (codeforge@mclayer)",
            ],
            False,
        )

    if not workflows_dir.is_dir():
        # consumer workflows dir 자체 부재 — check 6 가 별도 warning 발화. check 10 = skip.
        return ([], False)

    drifted: list[tuple[str, str, str, str]] = []  # (name, consumer_sha, wrapper_sha, tier2_diff)
    strict_eligible_drift = False

    for name in sorted(expected):
        consumer_path = workflows_dir / name
        wrapper_path = wrapper_workflows_dir / name
        if not consumer_path.is_file():
            # check 6 가 부재 warning 발화. check 10 = file 부재 시 drift 검증 skip (해당 file).
            continue
        if not wrapper_path.is_file():
            # wrapper templates 에 없는 file = consumer-defined, drift 검증 영역 외.
            continue

        # Tier 1: SHA-256
        consumer_sha = _sha256_of_file(consumer_path)
        wrapper_sha = _sha256_of_file(wrapper_path)
        if consumer_sha is None or wrapper_sha is None:
            # Read error — skip this file (best-effort)
            continue
        if consumer_sha == wrapper_sha:
            continue  # byte-identical, no drift

        # Tier 2: core marker compare (surface semantic vs whitespace-only)
        try:
            consumer_content = consumer_path.read_text(encoding="utf-8", errors="replace")
            wrapper_content = wrapper_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            consumer_content = ""
            wrapper_content = ""

        consumer_markers = _normalized_core_markers(consumer_content)
        wrapper_markers = _normalized_core_markers(wrapper_content)

        differing_markers: list[str] = []
        for marker_name in ("concurrency", "on", "permissions"):
            c_block = consumer_markers.get(marker_name, "")
            w_block = wrapper_markers.get(marker_name, "")
            if c_block != w_block:
                differing_markers.append(marker_name)

        if not differing_markers:
            # Tier 1 SHA mismatch + Tier 2 core markers identical = superficial whitespace diff.
            # 본 경우 = drift 분류 영역 외 (semantic-only invariant 영역).
            continue

        # Strict-eligible 분류: file ∈ STRICT_ELIGIBLE_WORKFLOWS → strict_eligible_drift = True
        if name in STRICT_ELIGIBLE_WORKFLOWS:
            strict_eligible_drift = True

        tier2_diff_summary = ",".join(differing_markers)
        drifted.append((name, consumer_sha[:8], wrapper_sha[:8], tier2_diff_summary))

    if not drifted:
        return ([], False)

    warns = [
        f"[bootstrap] WARN: {len(drifted)} workflow drift detected (consumer vs wrapper templates, CFP-660)",
    ]
    for (name, c_sha, w_sha, t2) in drifted[:5]:
        strict_marker = " STRICT-ELIGIBLE" if name in STRICT_ELIGIBLE_WORKFLOWS else ""
        warns.append(f"           {name}: SHA {c_sha}→{w_sha} drift markers=[{t2}]{strict_marker}")
    if len(drifted) > 5:
        warns.append(f"           ... ({len(drifted) - 5} more)")
    warns.extend([
        "           → cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/",
        "           → 또는 hotfix-bypass:workflow-version-drift label 부착 (audit-trailed channel, ADR-024 Amendment 3 §결정 6.A)",
        "           → strict mode 활성 시 (e) strict-eligible drift → exit 1",
    ])

    return (warns, strict_eligible_drift)


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


def _check_bypass_active(env: dict[str, str]) -> tuple[bool, str | None]:
    """ADR-027 §결정 3 — Bypass detection. Strict mode 보다 priority HIGHEST.

    Returns:
      (True, reason) — 양 env set, hook self skip honored
      (False, None) — 둘 다 unset (또는 reason empty)
    """
    flag = env.get("HOTFIX_BYPASS_CODEFORGE", "").strip()
    reason = env.get("HOTFIX_BYPASS_REASON", "").strip()
    if flag == "1" and reason:
        return True, reason
    return False, None


def _check_strict_mode_active(
    env: dict[str, str], cli_strict: bool, overlay_yaml: Path
) -> tuple[bool, str]:
    """CFP-127 / ADR-032 — Strict mode opt-in detection.

    Priority CLI > env > yaml.

    Returns:
      (True, source) — strict mode 활성, source ∈ {"cli", "env", "yaml"}
      (False, "") — strict mode 미활성
    """
    if cli_strict:
        return True, "cli"
    if env.get("CODEFORGE_STRICT_BOOTSTRAP", "").strip() == "1":
        return True, "env"
    if overlay_yaml.is_file():
        try:
            import yaml
            data = yaml.safe_load(overlay_yaml.read_text(encoding="utf-8")) or {}
            bs = data.get("bootstrap", {})
            if isinstance(bs, dict) and bs.get("strict_mode") is True:
                return True, "yaml"
        except Exception:
            pass
    return False, ""


def _classify_strict_eligible(
    plugins_json: Path,
    settings_path: Path,
    org: str,
    repo: str,
    gh_ready: bool,
    workflows_dir: Path | None = None,
    plugin_root: Path | None = None,
    expected_workflows: set[str] | None = None,
    overlay_yaml: Path | None = None,
) -> list[str]:
    """CFP-127 / ADR-032 — Strict-eligible drift 6종 detection (CFP-660 + CFP-2432 확장).

    6 type:
      (a) project.yaml 부재 — 별도 main() 검사
      (b) plugin 10종 중 wrapper(1) + 6 lane(6) = 7 critical 미설치
      (c) settings.json 의 3 hook 미등록 (check 9)
      (d) 15 label 중 phase:* (7) + gate:* (3) = 10 critical 부재 (gh_ready 시만)
      (e) consumer workflow drift — STRICT_ELIGIBLE_WORKFLOWS 영역 (CFP-660 NEW)
      (f) story_stakes overlay down-tier 거부 — 확장-only 위반 (CFP-2432 / ADR-042 Amd16 NEW)

    Returns:
      list of strict-eligible drift findings (multi-line, ready to print).
      empty list = no strict-eligible drift.
    """
    findings: list[str] = []

    # (b) plugin subset
    if plugins_json.is_file():
        try:
            data = json.loads(plugins_json.read_text(encoding="utf-8"))
            installed = set(data.get("plugins", {}).keys())
            missing_critical = STRICT_ELIGIBLE_PLUGINS - installed
            if missing_critical:
                findings.append(
                    f"[bootstrap] STRICT (b): {len(missing_critical)}/{len(STRICT_ELIGIBLE_PLUGINS)} critical plugin 미설치"
                )
                findings.append(f"           누락: {' '.join(sorted(missing_critical))}")
                findings.append("           → /plugins install 명령 직접 실행 (Claude Code platform-level)")
        except Exception:
            findings.append(f"[bootstrap] STRICT (b): {plugins_json} parse 실패 — plugin 설치 검증 불가")
    else:
        findings.append(f"[bootstrap] STRICT (b): {plugins_json} 부재 — Claude Code 미설치 또는 plugin 0개")

    # (c) settings.json 3 hook
    _, hook_strict = check_settings_hooks(settings_path)
    if hook_strict:
        # Detail 은 main() 에서 별도 출력
        findings.append("[bootstrap] STRICT (c): settings.json hook 미등록 — check 9 detail 참조")

    # (d) labels (gh_ready 시만)
    if gh_ready:
        try:
            result = subprocess.run(
                [
                    "gh", "label", "list", "--limit", "100", "--repo", f"{org}/{repo}",
                    "--json", "name", "-q", "[.[].name]",
                ],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                existing = set(json.loads(result.stdout))
                missing_critical = STRICT_ELIGIBLE_LABELS - existing
                if missing_critical:
                    findings.append(
                        f"[bootstrap] STRICT (d): {len(missing_critical)}/{len(STRICT_ELIGIBLE_LABELS)} critical label 부재"
                    )
                    findings.append(f"           누락: {' '.join(sorted(missing_critical))}")
                    findings.append("           → 'bash scripts/bootstrap-labels.sh <org>/<repo>' 1회 실행")
        except Exception:
            pass

    # (e) consumer workflow version drift (CFP-660 / ADR-032 amendment 2)
    if workflows_dir is not None and plugin_root is not None:
        _drift_warns, drift_strict = check_workflow_version_drift(
            workflows_dir, plugin_root, expected_workflows
        )
        if drift_strict:
            findings.append(
                "[bootstrap] STRICT (e): consumer workflow drift — STRICT_ELIGIBLE_WORKFLOWS 영역 mismatch"
            )
            findings.append("           → check 10 detail 참조 (warning 영역 본문)")
            findings.append(
                "           → cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/"
            )

    # (f) story_stakes overlay down-tier (CFP-2432 / ADR-042 Amendment 16)
    if overlay_yaml is not None:
        _stakes_warns, stakes_strict = check_story_stakes_overlay(overlay_yaml)
        if stakes_strict:
            findings.append(
                "[bootstrap] STRICT (f): story_stakes overlay down-tier 거부 — 확장-only 위반 (ADR-127 §결정6)"
            )
            findings.append("           → check 11 detail 참조 (warning 영역 본문)")
            findings.append(
                "           → 합법 형태 = story_stakes.conservative_override[] (보수 opus 강제만)"
            )

    return findings


# ----------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    """Entry point. Default non-blocking exit 0. Strict mode opt-in (CFP-127 / ADR-032) → exit 1 가능.

    CLI:
      check_bootstrap.py [--strict] [--quiet]

    Exit code:
      Default mode: 0 (advisory only, ADR-027 §결정 2 정합)
      Strict mode + strict-eligible drift 부재: 0
      Strict mode + 1+ strict-eligible drift: 1

    Bypass precedence: HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON 양 env set →
      strict mode 활성 무관 hook self skip (exit 0).
    """
    parser = argparse.ArgumentParser(
        description="Consumer 환경 부트스트랩 정합 진단 (CFP-103 + CFP-127)"
    )
    parser.add_argument("--strict", action="store_true",
                        help="CFP-127 / ADR-032 strict mode opt-in (priority 1, CLI > env > yaml)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress non-strict warning output")
    args = parser.parse_args(argv)

    env = dict(os.environ)

    # Bypass check (ADR-027 §결정 3) — priority HIGHEST, strict mode 무관
    bypass_active, bypass_reason = _check_bypass_active(env)
    if bypass_active:
        print(f"[check-bootstrap] BYPASS honored — HOTFIX_BYPASS_CODEFORGE=1 reason={bypass_reason!r}",
              file=sys.stderr)
        return 0

    overlay_yaml = _resolve_overlay_yaml(env)

    # Strict mode detection (CLI > env > yaml)
    strict_active, strict_source = _check_strict_mode_active(env, args.strict, overlay_yaml)

    # Strict-eligible (a): project.yaml 부재
    if not overlay_yaml.is_file():
        if strict_active:
            print("", file=sys.stderr)
            print(f"[check-bootstrap] STRICT mode active (source={strict_source}) — strict-eligible (a) drift:",
                  file=sys.stderr)
            print(f"           {overlay_yaml} 부재 — Orchestrator config 미인식, lane spawn 정합 불가",
                  file=sys.stderr)
            print("           → preflight: story-init 발동 전 bootstrap 필요 (project.yaml = org/repo 라우팅 SSOT, CFP-2250 결함3)",
                  file=sys.stderr)
            print("           → 'bash scripts/bootstrap-consumer.sh' 1회 실행 (CFP-125 quickstart)",
                  file=sys.stderr)
            print("           → revert: --strict flag 미사용 / unset CODEFORGE_STRICT_BOOTSTRAP / yaml strict_mode false",
                  file=sys.stderr)
            print("", file=sys.stderr)
            return 1
        # Default mode: silent skip (consumer 초기 설정 단계)
        return 0

    plugin_root = _resolve_plugin_root(env, Path(__file__).resolve())
    plugins_json = _resolve_plugins_json(env)
    org, repo = _extract_org_repo(overlay_yaml)

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

    settings_path = Path(".claude/settings.json")
    hook_warnings, _ = check_settings_hooks(settings_path)

    workflows_dir = Path(".github/workflows")
    drift_warnings, _ = check_workflow_version_drift(
        workflows_dir, plugin_root, expected_workflows
    )

    stakes_warnings, _ = check_story_stakes_overlay(overlay_yaml)   # CFP-2432 NEW check 11

    all_results: list[list[str]] = [
        check_workflow_permissions(org, repo) if gh_ready else [],
        check_plugin_labels(org, repo) if gh_ready else [],
        check_workflow_distribution(overlay_yaml),
        check_consumer_scripts_manifest(plugin_root, overlay_yaml) if plugin_root is not None else [],
        check_plugins_installed(plugins_json),
        check_consumer_workflows(workflows_dir, expected_workflows),
        check_consumer_issue_forms(Path(".github/ISSUE_TEMPLATE")),
        check_codeowners(
            Path("CODEOWNERS"),
            Path(".github/CODEOWNERS"),
            Path("docs/CODEOWNERS"),
        ),
        hook_warnings,    # CFP-127 NEW check 9
        drift_warnings,   # CFP-660 NEW check 10
        stakes_warnings,  # CFP-2432 NEW check 11 (story_stakes down-tier 거부)
    ]
    findings_count = sum(1 for r in all_results if r)
    warnings = [line for r in all_results for line in r]

    if warnings and not args.quiet:
        print(file=sys.stderr)
        print(
            f"[check-bootstrap] {findings_count} 부트스트랩 drift 발견 ({'strict mode' if strict_active else 'non-blocking'}):",
            file=sys.stderr,
        )
        for w in warnings:
            print(w, file=sys.stderr)
        print(file=sys.stderr)

    # CFP-127 / ADR-032 — Strict mode → strict-eligible drift 5종 검사 (CFP-660 Wave 2 확장)
    if strict_active:
        strict_findings = _classify_strict_eligible(
            plugins_json, settings_path, org, repo, gh_ready,
            workflows_dir=workflows_dir,
            plugin_root=plugin_root,
            expected_workflows=expected_workflows,
            overlay_yaml=overlay_yaml,
        )
        if strict_findings:
            print(f"[check-bootstrap] STRICT mode active (source={strict_source}) — strict-eligible drift detected:",
                  file=sys.stderr)
            for f in strict_findings:
                print(f, file=sys.stderr)
            print("", file=sys.stderr)
            print("           → revert: --strict flag 미사용 / unset CODEFORGE_STRICT_BOOTSTRAP / yaml strict_mode false",
                  file=sys.stderr)
            print("           → bypass: HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON='<reason>' (ADR-027 §결정 3)",
                  file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
