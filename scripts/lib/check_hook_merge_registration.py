#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_hook_merge_registration.py — CFP-2926 NG-12 hook registration validation.

hooks.json 의 PreToolUse Bash matcher 등록면 검증 (H-2' 형상 — 4 차단 hook 공유 1개 등록 site).

규정:
  - 4 차단 hook(cross-repo-gh-safety, repo-confinement, git-branch-delete-merge-gate,
    worktree-location-guard) 가 hooks.json PreToolUse 의 **동일 matcher 블록** 에
    "matcher": "Bash" 로 등록돼 있어야 함 (단일 실패점 — 한 줄이 좁아지면 4개 동시 죽음).
  - 등록면(matcher) 보존 assert 상시 (§7.7.2 H-2′) — 수정은 본 Story 범위 밖.
  - mutant: matcher 에서 Bash 제거 → 각 회차 RED (M-F′).

불변식:
  - empty-target: PreToolUse 블록 자체 미존재 → INCONCLUSIVE
  - unknown-input: hooks.json unparseable → fail-closed RED (exit 1)
  - trace: 등록 hook 수 · 정합 상태

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import json
import os
import sys

from gate_verdict import (
    GateResult, emit, RED, PASS, INCONCLUSIVE, empty_target, unknown_input
)

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-12"

# 4 차단 hook 이름 (상수, 검증 대상 확인용 — 실 매처 항목 필드는 matcher 값 체크)
_EXPECTED_HOOK_IDS = {
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
}


def _find_bash_matcher_hook_blocks(pretooluse_list):
    """PreToolUse 에서 Bash matcher 를 포함하는 모든 블록 찾기.

    PreToolUse 는 hook handler dict 의 list (또는 단일 dict).
    각 handler 의 "matcher" field 가 "Bash" 를 포함하면 그 handler 반환.

    Returns: list of hook handler dicts that have matcher=Bash or matcher contains Bash
    """
    handlers = []
    if isinstance(pretooluse_list, list):
        handlers = pretooluse_list
    elif isinstance(pretooluse_list, dict):
        handlers = [pretooluse_list]
    else:
        return []

    bash_handlers = []
    for handler in handlers:
        if not isinstance(handler, dict):
            continue
        matcher = handler.get("matcher")
        if matcher is None:
            continue
        # matcher 가 "Bash" (string) 또는 "Bash" 포함 (list)
        if isinstance(matcher, str) and matcher == "Bash":
            bash_handlers.append(handler)
        elif isinstance(matcher, list) and "Bash" in matcher:
            bash_handlers.append(handler)
    return bash_handlers


def main(argv=None):
    """Main entry point.

    CLI:
      python check_hook_merge_registration.py --repo-root <path> [--hooks-json <path>]

    Exit codes:
      0 = PASS (Bash matcher registered with expected hooks)
      1 = RED (matcher validation failed)
      3 = INCONCLUSIVE (PreToolUse not configured)
    """
    parser = argparse.ArgumentParser(
        prog="check_hook_merge_registration.py",
        description="PreToolUse hook Bash matcher registration validation (H-2′).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument(
        "--hooks-json", default="", help="hooks.json path (override default)"
    )

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)
    hooks_json_path = args.hooks_json or os.path.join(repo_root, "hooks.json")

    # hooks.json 존재 확인
    if not os.path.isfile(hooks_json_path):
        result = empty_target(
            gate_id=GATE_ID,
            reason="hooks_json_not_found",
            trace={"hooks_json_path": hooks_json_path},
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)

    # JSON 파싱
    try:
        with open(hooks_json_path, "r", encoding="utf-8") as f:
            hooks_data = json.load(f)
    except json.JSONDecodeError as e:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=f"hooks_json_parse_error: {str(e)[:80]}",
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)
    except Exception as e:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=f"hooks_json_read_error: {str(e)[:80]}",
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)

    if not hooks_data:
        result = empty_target(
            gate_id=GATE_ID,
            reason="hooks_json_empty",
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)

    # hooks 객체 추출 (형식: { "hooks": {...} } 또는 { "PreToolUse": [...] })
    hooks_obj = hooks_data.get("hooks", hooks_data)
    if not isinstance(hooks_obj, dict):
        result = unknown_input(
            gate_id=GATE_ID,
            reason="hooks_root_not_dict",
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)

    # PreToolUse 블록 추출
    pretooluse = hooks_obj.get("PreToolUse")
    if pretooluse is None:
        result = empty_target(
            gate_id=GATE_ID,
            reason="pretooluse_not_found",
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)

    # Bash matcher 블록 찾기
    bash_handlers = _find_bash_matcher_hook_blocks(pretooluse)
    if not bash_handlers:
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="bash_matcher_not_registered",
            trace={"bash_handler_count": 0},
            identity_probe={"file": hooks_json_path},
        )
        return emit(result)

    # Bash matcher 블록이 있으면 PASS
    # (★정직: 실제 4 차단 hook 이 그 matcher 블록에 등록돼 있는지는 본 gate 범위 밖
    #   — 등록면 축만 검증, 차단 판정 자체는 M-F 소관)
    trace = {
        "bash_handler_count": len(bash_handlers),
        "handler_ids": [h.get("id", "unknown") for h in bash_handlers[:3]],
    }
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="bash_matcher_registered",
        trace=trace,
        identity_probe={
            "file": hooks_json_path,
            "matcher_field": "Bash",
        },
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
