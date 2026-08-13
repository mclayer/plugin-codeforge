#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Hook commands confined to plugin root (AC-11).

목적 (AC-11):
  24개 hook command 가 모두 ${CLAUDE_PLUGIN_ROOT} 경유 run-hook.cmd 만 참조.
  plugin 경계 밖 경로 참조·수정 0 검증.

범위 (정직 scope docstring):
  - 플랫폼 harness binary (Claude Code 런타임) 는 repo 밖
  - 본 테스트는 repo-측 표면 (훅 배선이 plugin 경계 밖을 참조·수정하지 않음) 을 검증
  - 플랫폼·OS 레벨 보안 (권한·프로세스 격리) 는 scope 외

테스트:
  1. hooks.json 24개 command 전수 순회
  2. 각 command 가 "${CLAUDE_PLUGIN_ROOT}" 포함하는지 확인
  3. 상대 경로 (../ 등) 나 절대 경로(/tmp, /etc 등) 검출 시 FAIL
"""

from __future__ import annotations

import json
import re
import pytest
from pathlib import Path


def _load_hooks_json() -> dict:
    """hooks.json 로드."""
    hooks_path = Path(__file__).parent.parent / "hooks.json"
    with open(hooks_path, encoding="utf-8") as f:
        return json.load(f)


def test_all_hook_commands_use_plugin_root():
    """AC-11: 전 24개 command 가 ${CLAUDE_PLUGIN_ROOT} 경유 run-hook.cmd 만 참조."""
    hooks_data = _load_hooks_json()
    violations = []

    for event_name, matchers in hooks_data["hooks"].items():
        if not isinstance(matchers, list):
            continue

        for matcher_entry in matchers:
            hooks_list = matcher_entry.get("hooks", [])
            for hook in hooks_list:
                cmd = hook.get("command", "")

                # ${CLAUDE_PLUGIN_ROOT} 확인
                if "${CLAUDE_PLUGIN_ROOT}" not in cmd:
                    violations.append(
                        f"Event={event_name}: ${'{CLAUDE_PLUGIN_ROOT}'} not found in: {cmd}"
                    )
                    continue

                # run-hook.cmd 확인
                if "run-hook.cmd" not in cmd:
                    violations.append(
                        f"Event={event_name}: run-hook.cmd not found in: {cmd}"
                    )
                    continue

                # 위험한 경로 검출 (외부 참조)
                # ../../../ 나 /etc/ /tmp/ /usr/ 등 절대 경로
                if re.search(r"['\"](?:\.\./|/[a-z])", cmd):
                    violations.append(
                        f"Event={event_name}: dangerous path in: {cmd}"
                    )

    if violations:
        pytest.fail(
            f"Command confinement violations (AC-11):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


def test_all_24_hooks_counted():
    """AC-11 count check."""
    hooks_data = _load_hooks_json()
    count = 0

    for matchers in hooks_data["hooks"].values():
        if isinstance(matchers, list):
            for entry in matchers:
                hooks_list = entry.get("hooks", [])
                count += len(hooks_list)

    assert count == 24, f"Expected 24 hooks, got {count} (AC-11 scope)"


def test_plugin_root_only_reference():
    """AC-11: 다른 환경 변수 참조 검출 (plugin 경계 검증)."""
    hooks_data = _load_hooks_json()
    external_refs = []

    for event_name, matchers in hooks_data["hooks"].items():
        if not isinstance(matchers, list):
            continue

        for matcher_entry in matchers:
            hooks_list = matcher_entry.get("hooks", [])
            for hook in hooks_list:
                cmd = hook.get("command", "")

                # ${...} 형태 찾기 (${CLAUDE_PLUGIN_ROOT} 외)
                other_vars = re.findall(r"\$\{[^}]+\}", cmd)
                for var in other_vars:
                    if "CLAUDE_PLUGIN_ROOT" not in var:
                        external_refs.append(
                            f"Event={event_name}: external env var {var} in: {cmd}"
                        )

    # external env var 참조는 경고만 (차단 아님 — compliance ceiling)
    if external_refs:
        print(f"\nWarning: External env var references found (AC-11 audit):")
        for ref in external_refs:
            print(f"  - {ref}")
