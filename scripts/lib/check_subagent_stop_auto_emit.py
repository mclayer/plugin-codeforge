#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_subagent_stop_auto_emit.py — CFP-2926 NG-16 SubagentStop hook + stop_event append.

stop-event-v1.md §3.5 검증:
  1. SubagentStop hook 등록 여부 (hooks.json)
  2. stop_event JSONL 레져 append 여부 (.claude/ledger/stop-event.jsonl)
  3. 완료된 subagent stop 이벤트 최소 1개 이상

조건:
  - PASS: hooks/subagent-stop 핸들러 등록 + stop-event.jsonl 최소 1개 로우
  - RED: hook 미등록 또는 ledger append 미수행
  - INCONCLUSIVE: 빈 세션(0 subagent stop) → 판정 불가

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import json
import os
import sys

from gate_verdict import GateResult, emit, RED, PASS, INCONCLUSIVE, empty_target

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-16"


def _check_hooks_registration(repo_root):
    """hooks.json 에서 SubagentStop hook 등록 확인.

    Returns: (is_registered, hook_config_or_none)
    """
    hooks_json_path = os.path.join(repo_root, "hooks.json")
    if not os.path.isfile(hooks_json_path):
        return False, None

    try:
        with open(hooks_json_path, "r", encoding="utf-8") as f:
            hooks = json.load(f)
    except Exception:
        return False, None

    # SubagentStop hook 찾기 (hooks 배열 또는 단일 object)
    if isinstance(hooks, list):
        for hook in hooks:
            if isinstance(hook, dict):
                if hook.get("event_type") == "SubagentStop":
                    return True, hook
    elif isinstance(hooks, dict):
        # { "subagent-stop": {...} } 형식
        if "SubagentStop" in hooks:
            return True, hooks["SubagentStop"]
        # hooks.hooks 배열 형식
        if "hooks" in hooks and isinstance(hooks["hooks"], list):
            for hook in hooks["hooks"]:
                if isinstance(hook, dict) and hook.get("event_type") == "SubagentStop":
                    return True, hook

    return False, None


def _check_stop_event_ledger(repo_root):
    """stop-event.jsonl 레져 확인.

    Returns: (has_ledger, row_count)
    """
    ledger_path = os.path.join(repo_root, ".claude", "ledger", "stop-event.jsonl")

    if not os.path.isfile(ledger_path):
        return False, 0

    # 레져 라인 카운트 (최소 1개 이상 필수)
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            row_count = sum(1 for line in f if line.strip())
        return True, row_count
    except Exception:
        return False, 0


def main(argv=None):
    """Main entry point.

    CLI:
      python check_subagent_stop_auto_emit.py --repo-root <path>

    Exit codes:
      0 = PASS (hook registered + ledger rows present)
      1 = RED (hook not registered OR ledger absent/empty)
      3 = INCONCLUSIVE (empty session, no stop events yet)
    """
    parser = argparse.ArgumentParser(
        prog="check_subagent_stop_auto_emit.py",
        description="SubagentStop hook registration + stop_event ledger append check.",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)

    # 1. hooks.json SubagentStop 등록 확인
    hook_registered, hook_config = _check_hooks_registration(repo_root)

    # 2. stop-event.jsonl 레져 확인
    ledger_exists, row_count = _check_stop_event_ledger(repo_root)

    trace = {
        "hook_registered": hook_registered,
        "ledger_exists": ledger_exists,
        "ledger_row_count": row_count,
    }

    # 판정 로직
    if not hook_registered:
        # Hook 미등록 = RED (필수 조건)
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="subagent_stop_hook_not_registered",
            trace=trace,
            identity_probe={"repo_root": repo_root},
        )
        return emit(result)

    if not ledger_exists:
        # Ledger 부재 = 아직 stop event 미발생 (empty session) → INCONCLUSIVE
        result = empty_target(
            gate_id=GATE_ID,
            reason="stop_event_ledger_absent",
            trace=trace,
            identity_probe={"repo_root": repo_root},
        )
        return emit(result)

    if row_count == 0:
        # Ledger 파일 존재하지만 빈 상태 (empty session) → INCONCLUSIVE
        result = empty_target(
            gate_id=GATE_ID,
            reason="stop_event_ledger_empty",
            trace=trace,
            identity_probe={"repo_root": repo_root},
        )
        return emit(result)

    # PASS: hook 등록 + ledger 에 최소 1개 이상 행
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="subagent_stop_hook_and_ledger_present",
        trace=trace,
        identity_probe={"repo_root": repo_root},
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
