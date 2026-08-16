#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Hook commands confined to plugin root (AC-11).

목적 (AC-11):
  25개 hook command 가 모두 ${CLAUDE_PLUGIN_ROOT} 경유 run-hook.cmd 만 참조.
  plugin 경계 밖 경로 참조·수정 0 검증.

범위 (정직 scope docstring):
  - 플랫폼 harness binary (Claude Code 런타임) 는 repo 밖
  - 본 테스트는 repo-측 표면 (훅 배선이 plugin 경계 밖을 참조·수정하지 않음) 을 검증
  - 플랫폼·OS 레벨 보안 (권한·프로세스 격리) 는 scope 외

테스트:
  1. hooks.json 25개 command 전수 순회
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
    """AC-11: 전 25개 command 가 ${CLAUDE_PLUGIN_ROOT} 경유 run-hook.cmd 만 참조."""
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


def test_all_hooks_counted_matches_pin():
    """AC-11 count check."""
    hooks_data = _load_hooks_json()
    count = 0

    for matchers in hooks_data["hooks"].values():
        if isinstance(matchers, list):
            for entry in matchers:
                hooks_list = entry.get("hooks", [])
                count += len(hooks_list)

    assert count == 25, f"Expected 25 hooks, got {count} (AC-11 scope)"


def test_plugin_root_only_reference():
    """AC-11: ${CLAUDE_PLUGIN_ROOT} 외 환경변수 참조 0 — print 경고 → FAIL 승격.

    구 코드는 위반을 print 로만 흘렸다. pytest 는 통과를 찍고, 그 경고는 `-s` 로
    stdout 을 들여다볼 때만 보인다 — 게이트로서 판별력 0(위반이 있어도 GREEN).
    plugin 경계 참조는 AC-11 이 판정하겠다고 선언한 대상이므로 FAIL 로 승격한다.

    승격 안전성 실측 (2026-08-14 firsthand): 현행 hooks.json 25 command 의
    external env var 참조 = 0건 → 승격해도 GREEN (born-red 아님).
    """
    hooks_data = _load_hooks_json()
    external_refs = []
    scanned = 0

    for event_name, matchers in hooks_data["hooks"].items():
        if not isinstance(matchers, list):
            continue

        for matcher_entry in matchers:
            hooks_list = matcher_entry.get("hooks", [])
            for hook in hooks_list:
                cmd = hook.get("command", "")
                scanned += 1

                # ${...} 형태 찾기 (${CLAUDE_PLUGIN_ROOT} 외)
                other_vars = re.findall(r"\$\{[^}]+\}", cmd)
                for var in other_vars:
                    if "CLAUDE_PLUGIN_ROOT" not in var:
                        external_refs.append(
                            f"Event={event_name}: external env var {var} in: {cmd}"
                        )

    # 정의역 비공허 — 0건을 훑고 "위반 없음" 을 말하면 공허한 통과다.
    assert scanned == 25, f"검사 대상 command 25 기대, 실제 {scanned} (AC-11 scope)"

    if external_refs:
        pytest.fail(
            "AC-11 위반 — ${CLAUDE_PLUGIN_ROOT} 밖 환경변수 참조:\n"
            + "\n".join(f"  - {ref}" for ref in external_refs)
        )
