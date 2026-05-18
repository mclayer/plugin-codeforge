#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
templates/scripts/detect-repo-kind.py

CFP-899 Phase 2 — Consumer-applicability filter repo-kind detector
reconcile-protocol-v1 v1.9 §4.12 consumer_applicability_filter_binding
ADR-083 Wave-1 declaration → Wave-2 runtime implementation

§4.12 truth-table (4-way matrix):
  - plugin.json 존재 + marketplace member  = plugin   (exit 0)
  - plugin.json 부재 + overlay project.yaml = consumer (exit 1)
  - plugin.json 존재 + .claude/_overlay 존재 = mixed   (exit 2)
  - 신호 없음                               = unknown  (exit 3, fail-closed)

CLI:
  python3 detect-repo-kind.py [--repo-root <path>] [--check-signal <signal>]
                               [--skip-marketplace-check]

Exit codes:
  0 = plugin
  1 = consumer
  2 = mixed
  3 = unknown (fail-closed abort signal)

Output (stdout): one of: plugin / consumer / mixed / unknown

ADR-061 정합: 외부 .py 파일, explicit absolute path
ADR-083 §결정 1: consumer_applicability_filter_detection (Wave-1 declaration)
ADR-027 Amendment 6 §결정 10: 4-way truth-table signals
reconcile-protocol-v1 v1.9 §4.12 repo_kind_detection_signals
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────────────────────────
_SIGNAL_PLUGIN_JSON = "plugin_json"
_SIGNAL_OVERLAY_PROJECT_YAML = "overlay_project_yaml"
_SIGNAL_MARKETPLACE_MEMBERSHIP = "marketplace_membership"

_VALID_SIGNALS = (
    _SIGNAL_PLUGIN_JSON,
    _SIGNAL_OVERLAY_PROJECT_YAML,
    _SIGNAL_MARKETPLACE_MEMBERSHIP,
)

# marketplace.json 위치 (wrapper repo root 기준 — SSOT: mclayer/marketplace)
_MARKETPLACE_REPO = "mclayer/marketplace"
_MARKETPLACE_PATH = "marketplace.json"


# ─────────────────────────────────────────────────────────────────────────────
# 신호 탐지 함수
# ─────────────────────────────────────────────────────────────────────────────


def _has_plugin_json(repo_root: Path) -> bool:
    """Primary signal 1: .claude-plugin/plugin.json 존재 여부.

    §4.12 repo_kind_detection_signals Primary 1:
      `.claude-plugin/plugin.json` 존재.
    """
    return (repo_root / ".claude-plugin" / "plugin.json").exists()


def _has_overlay_project_yaml(repo_root: Path) -> bool:
    """Primary signal 3: .claude/_overlay/project.yaml 존재 여부.

    §4.12 repo_kind_detection_signals Primary 3:
      `.claude/_overlay/project.yaml`.
    """
    return (repo_root / ".claude" / "_overlay" / "project.yaml").exists()


def _has_marketplace_membership(repo_root: Path, skip: bool) -> bool | None:
    """Primary signal 2: marketplace.json membership check.

    §4.12 repo_kind_detection_signals Primary 2:
      `marketplace.json` membership (cross-repo gh api, ADR-066 PAT).

    Returns:
      True  = membership 확인
      False = 비멤버
      None  = 확인 불가 (skip or API 실패)
    """
    if skip:
        return None

    # plugin.json 에서 name 추출
    plugin_json = repo_root / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        return False

    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        plugin_name = data.get("name", "")
    except (json.JSONDecodeError, OSError):
        return None

    if not plugin_name:
        return None

    # gh api 로 marketplace.json content 조회
    pat = os.environ.get("CODEFORGE_CROSS_REPO_PAT", "")
    env = {**os.environ}
    if pat:
        env["GH_TOKEN"] = pat

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{_MARKETPLACE_REPO}/contents/{_MARKETPLACE_PATH}",
                "--jq",
                f'.content | @base64d | fromjson | .plugins[] | select(.name == "{plugin_name}") | .name',
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 4-way 분류 함수
# ─────────────────────────────────────────────────────────────────────────────


def detect_repo_kind(repo_root: Path, skip_marketplace: bool) -> str:
    """§4.12 truth-table 4-way 분류.

    Returns: 'plugin' | 'consumer' | 'mixed' | 'unknown'
    """
    has_plugin = _has_plugin_json(repo_root)
    has_overlay = _has_overlay_project_yaml(repo_root)

    # mixed: plugin.json 존재 + overlay 존재
    if has_plugin and has_overlay:
        return "mixed"

    # plugin: plugin.json 존재 (overlay 없음)
    if has_plugin:
        # marketplace membership check (ADR-066 PAT)
        membership = _has_marketplace_membership(repo_root, skip=skip_marketplace)
        # skip 또는 확인 불가 시 plugin.json 단독으로 판정 (offline fallback)
        return "plugin"

    # consumer: plugin.json 부재 + overlay project.yaml 존재
    if has_overlay:
        return "consumer"

    # unknown: 신호 없음 → fail-closed
    return "unknown"


def _check_single_signal(repo_root: Path, signal: str, skip_marketplace: bool) -> str:
    """단일 신호 probe (--check-signal 옵션).

    Returns: 'present' | 'absent' | 'unknown'
    """
    if signal == _SIGNAL_PLUGIN_JSON:
        return "present" if _has_plugin_json(repo_root) else "absent"
    elif signal == _SIGNAL_OVERLAY_PROJECT_YAML:
        return "present" if _has_overlay_project_yaml(repo_root) else "absent"
    elif signal == _SIGNAL_MARKETPLACE_MEMBERSHIP:
        result = _has_marketplace_membership(repo_root, skip=skip_marketplace)
        if result is True:
            return "present"
        elif result is False:
            return "absent"
        else:
            return "unknown"
    else:
        raise ValueError(f"알 수 없는 signal: {signal}")


# ─────────────────────────────────────────────────────────────────────────────
# Exit code 매핑
# ─────────────────────────────────────────────────────────────────────────────

_EXIT_CODE_MAP = {
    "plugin": 0,
    "consumer": 1,
    "mixed": 2,
    "unknown": 3,
}


# ─────────────────────────────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect repo kind for CFP-899 consumer-applicability filter (§4.12)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path.cwd()),
        help="Repo root path (default: cwd)",
    )
    parser.add_argument(
        "--check-signal",
        choices=list(_VALID_SIGNALS),
        help="Single signal probe (plugin_json | overlay_project_yaml | marketplace_membership)",
    )
    parser.add_argument(
        "--skip-marketplace-check",
        action="store_true",
        help="Skip cross-repo marketplace API check (offline / consumer self-managed)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if args.check_signal:
        # 단일 신호 probe 모드
        result = _check_single_signal(
            repo_root,
            signal=args.check_signal,
            skip_marketplace=args.skip_marketplace_check,
        )
        print(result)
        return 0

    # 4-way 분류 모드
    kind = detect_repo_kind(repo_root, skip_marketplace=args.skip_marketplace_check)
    print(kind)
    return _EXIT_CODE_MAP[kind]


if __name__ == "__main__":
    sys.exit(main())
