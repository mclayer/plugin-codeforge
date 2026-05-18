#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
templates/scripts/detect-repo-kind.py

CFP-899 Phase 2 — Consumer-applicability filter repo-kind detector
reconcile-protocol-v1 v1.9 §4.12 consumer_applicability_filter_binding
ADR-083 Wave-1 declaration → Wave-2 runtime implementation

§4.12 truth-table (4-way matrix):
  - plugin.json 존재 (overlay 무관)        = plugin   (exit 0)
  - plugin.json 존재 + overlay 존재        = mixed    (exit 2)
  - plugin.json 부재 + overlay project.yaml = consumer (exit 1)
  - 신호 없음                               = unknown  (exit 3, fail-closed)

CLI:
  python3 detect-repo-kind.py [--repo-root <path>] [--check-signal <signal>]

Exit codes:
  0 = plugin
  1 = consumer
  2 = mixed
  3 = unknown (fail-closed abort signal)

Output (stdout): one of: plugin / consumer / mixed / unknown

ADR-061 정합: 외부 .py 파일, explicit absolute path
ADR-083 §결정 1: consumer_applicability_filter_detection (Wave-1 declaration)
ADR-083 §결정 2: filesystem_only_invariant = true (cross-repo marketplace check = out_of_scope)
ADR-027 Amendment 6 §결정 10: 4-way truth-table signals
reconcile-protocol-v1 v1.9 §4.12 repo_kind_detection_signals

F-CR-899-5 FIX: marketplace membership check 제거 (filesystem_only_invariant 위반)
  - _has_marketplace_membership() 함수 제거
  - --skip-marketplace-check flag 제거
  - marketplace_membership signal 제거
  - filesystem-only: .claude-plugin/plugin.json + .claude/_overlay/project.yaml 2 signal only
"""

import argparse
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────────────────────────
_SIGNAL_PLUGIN_JSON = "plugin_json"
_SIGNAL_OVERLAY_PROJECT_YAML = "overlay_project_yaml"

_VALID_SIGNALS = (
    _SIGNAL_PLUGIN_JSON,
    _SIGNAL_OVERLAY_PROJECT_YAML,
)


# ─────────────────────────────────────────────────────────────────────────────
# 신호 탐지 함수 (filesystem-only, ADR-083 §결정 2)
# ─────────────────────────────────────────────────────────────────────────────


def _has_plugin_json(repo_root: Path) -> bool:
    """Primary signal 1: .claude-plugin/plugin.json 존재 여부.

    §4.12 repo_kind_detection_signals Primary 1:
      `.claude-plugin/plugin.json` 존재.

    latency: Path.exists() = O(1) syscall, < 1ms (empirically <0.1ms on NVMe).
    """
    return (repo_root / ".claude-plugin" / "plugin.json").exists()


def _has_overlay_project_yaml(repo_root: Path) -> bool:
    """Primary signal 2: .claude/_overlay/project.yaml 존재 여부.

    §4.12 repo_kind_detection_signals Primary 3:
      `.claude/_overlay/project.yaml`.

    latency: Path.exists() = O(1) syscall, < 1ms (empirically <0.1ms on NVMe).
    """
    return (repo_root / ".claude" / "_overlay" / "project.yaml").exists()


# ─────────────────────────────────────────────────────────────────────────────
# 4-way 분류 함수
# ─────────────────────────────────────────────────────────────────────────────


def detect_repo_kind(repo_root: Path) -> str:
    """§4.12 truth-table 4-way 분류 (filesystem-only).

    Returns: 'plugin' | 'consumer' | 'mixed' | 'unknown'

    ADR-083 §결정 5 pseudocode:
      if has_plugin and has_overlay → mixed
      if has_plugin                 → plugin
      if has_overlay                → consumer
      else                          → unknown (fail-closed)
    """
    has_plugin = _has_plugin_json(repo_root)
    has_overlay = _has_overlay_project_yaml(repo_root)

    # mixed: plugin.json 존재 + overlay 존재
    if has_plugin and has_overlay:
        return "mixed"

    # plugin: plugin.json 존재 (overlay 없음)
    if has_plugin:
        return "plugin"

    # consumer: plugin.json 부재 + overlay project.yaml 존재
    if has_overlay:
        return "consumer"

    # unknown: 신호 없음 → fail-closed
    return "unknown"


def _check_single_signal(repo_root: Path, signal: str) -> str:
    """단일 신호 probe (--check-signal 옵션).

    Returns: 'present' | 'absent'
    """
    if signal == _SIGNAL_PLUGIN_JSON:
        return "present" if _has_plugin_json(repo_root) else "absent"
    elif signal == _SIGNAL_OVERLAY_PROJECT_YAML:
        return "present" if _has_overlay_project_yaml(repo_root) else "absent"
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
        description=(
            "Detect repo kind for CFP-899 consumer-applicability filter (§4.12). "
            "filesystem-only: 2 primary signals only (ADR-083 §결정 2)."
        ),
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
        help="Single signal probe (plugin_json | overlay_project_yaml)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if args.check_signal:
        # 단일 신호 probe 모드
        result = _check_single_signal(repo_root, signal=args.check_signal)
        print(result)
        return 0

    # 4-way 분류 모드
    kind = detect_repo_kind(repo_root)
    print(kind)
    return _EXIT_CODE_MAP[kind]


if __name__ == "__main__":
    sys.exit(main())
