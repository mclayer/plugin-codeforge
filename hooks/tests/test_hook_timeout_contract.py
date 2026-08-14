#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 (테스트): Hook timeout contract invariant INV-T1, INV-T2.

목적:
  ∀ leaf handler in hooks.json 에 명시적 timeout int > 0 이 존재함을 검증.

정의역:
  - leaf handler = PostToolUse/PreToolUse/SessionStart/UserPromptSubmit/... entry 안의
    각 hook (type="command", command=..., timeout=...)
  - 복합 matcher (Agent|Bash|Write|Edit|MultiEdit) 를 포함한 전체 24개 entry 대상
  - AC-12: 순회 정의역이 PostToolUse + 복합 matcher entry를 포함함을 명시 검증

INV-T1: ∀ handler, timeout ∈ int AND timeout > 0
INV-T2: timeout 이 leaf level (matcher 레벨 아님) 에 위치

세부:
  - hooks.json 파싱 (실패 시 FAIL — 구조적 결함)
  - 각 handler의 timeout 필드 존재·타입·값 검증
  - count-agnostic: handler 개수를 고정하지 않고 동적 순회
  - 보고: 위반 handler 명시 표시 (찾기 용이하도록)
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path


from hook_runner_cfp2965 import load_hooks_json

# 정본 로더는 hook_runner_cfp2965.load_hooks_json (부재·구조 이상 = FAIL 계약 승계).
#   구 코드는 이 함수를 여기 사본으로 두고 test_hook_timeout_invariant_t3 가 **테스트
#   모듈 경유**로 끌어 썼다 — 수집 구성에 따라 이름 해석이 흔들리는 표면이라(CR-201)
#   인프라 심볼 출처로 부적합. 고유명 모듈로 이설하고 여기서는 별칭만 유지한다.
_load_hooks_json = load_hooks_json


def test_every_hook_handler_has_explicit_timeout():
    """INV-T1 + INV-T2: 전 24개 leaf handler 에 timeout int > 0 이 명시.

    AC-12: PostToolUse entry 및 복합 matcher entry (Agent|Bash|Write|Edit|MultiEdit)
    를 포함함을 명시 검증.
    """
    hooks_data = _load_hooks_json()
    hooks_dict = hooks_data["hooks"]

    # PostToolUse 존재 확인
    assert "PostToolUse" in hooks_dict, "PostToolUse entry missing (AC-12)"
    posttooluse_entries = hooks_dict["PostToolUse"]
    assert len(posttooluse_entries) > 0, "PostToolUse hooks list empty (AC-12)"

    # 복합 matcher entry 존재 확인
    pretooluse_entries = hooks_dict.get("PreToolUse", [])
    complex_matcher_found = False
    for entry in pretooluse_entries:
        matcher = entry.get("matcher", "")
        if "|" in matcher and all(
            tool in matcher for tool in ["Agent", "Bash", "Write", "Edit", "MultiEdit"]
        ):
            complex_matcher_found = True
            break
    assert complex_matcher_found, (
        "Complex matcher (Agent|Bash|Write|Edit|MultiEdit) not found (AC-12)"
    )

    # 모든 handler 순회
    violations = []
    handler_count = 0

    for event_name, matchers in hooks_dict.items():
        if not isinstance(matchers, list):
            continue

        for matcher_entry in matchers:
            hooks_list = matcher_entry.get("hooks")
            if not hooks_list or not isinstance(hooks_list, list):
                continue

            for hook in hooks_list:
                handler_count += 1

                # INV-T2: timeout 이 leaf level 에 위치
                if "timeout" not in hook:
                    violations.append(
                        f"Event={event_name}, hook missing timeout: {hook.get('command', '(unknown)')}"
                    )
                    continue

                timeout_val = hook["timeout"]

                # INV-T1: timeout int > 0
                if not isinstance(timeout_val, int):
                    violations.append(
                        f"Event={event_name}, timeout not int: {timeout_val} (type={type(timeout_val).__name__})"
                    )
                elif timeout_val <= 0:
                    violations.append(
                        f"Event={event_name}, timeout not > 0: {timeout_val}"
                    )

    # count-agnostic 검증 (개수 고정 안 함 — 정의역만 검증)
    assert handler_count > 0, "No hooks found in hooks.json (empty definition)"

    # 위반 보고
    if violations:
        pytest.fail(
            f"Timeout contract violations (INV-T1/T2):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    # 성공 보고
    assert (
        handler_count == 24
    ), f"Expected 24 leaf handlers, found {handler_count} (FYI, count-agnostic but verifying)"
    print(f"✓ All {handler_count} leaf handlers have explicit timeout int > 0")
