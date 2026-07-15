#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# PreToolUse capture adapter — dev-process-event-v1 Port A (hook) — CFP-2687 Phase 2 D2
#
# 설계 SSOT: ADR-155 §결정 4(capture 이원화 — hook Port A) + change-plan §3.4(NON-ambient lane)
#           + §7.4(record-only non-blocking exit0, ADR-115) + §결정 5(INV-8b).
#
# 책임:
#   - tool_name==Agent → event_type=prompt_input (content=spawn prompt, lane←subagent_type map).
#   - 그 외 tool       → event_type=tool_call    (content=call args, lane←agent_type map).
#   - content(prompt/args) → capture_blob(INV-8b) 경유(dev_process_hook_capture.record_hook_event).
#     index 는 blob_ref-only(content-blind). emit_source="hook".
#
# ★NON-ambient(Barrier #2): lane 은 payload agent_type/subagent_type 에서만 파생. 미등재 → "없음"
#   honest vacuous(consistent 위장 금지). Stop-hook lane ambient 기대 안 함.
#
# ★record-only / non-blocking / exit 0 ALWAYS(ADR-115): capture 실패는 tool call 을 절대 차단하지
#   않는다. 모든 경로 sys.exit(0). stdout 미방출(PreToolUse 결정 protocol 무오염 — updatedInput/
#   permissionDecision 절대 미emit).

import json
import os
import sys


def _resolve_lib():
    """scripts/lib 경로 해석(CLAUDE_PLUGIN_ROOT 우선, hooks/../scripts/lib fallback)."""
    here = os.path.dirname(os.path.abspath(__file__))
    roots = []
    pr = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if pr:
        roots.append(pr)
    roots.append(os.path.dirname(here))  # plugin root = hooks/ 의 부모
    for r in roots:
        lib = os.path.join(r, "scripts", "lib")
        if os.path.isdir(lib) and lib not in sys.path:
            sys.path.insert(0, lib)


def _pre_tool_content(tool_name, tool_input):
    """PreToolUse tool_call content(args) 컴팩트화 — redaction/bound 은 capture_blob 소관.

    Write/Edit 전체 file content 는 PostToolUse diff 로 잡으므로 여기선 file_path 만(중복·팽창 회피).
    """
    if not isinstance(tool_input, dict):
        return None
    if tool_name == "Bash":
        cmd = tool_input.get("command")
        return cmd if isinstance(cmd, str) and cmd.strip() else None
    if tool_name in ("Write", "Edit", "MultiEdit"):
        fp = tool_input.get("file_path") or ""
        return ("%s: %s" % (tool_name, fp)) if fp else None
    try:
        s = json.dumps(tool_input, ensure_ascii=False)
    except Exception:
        s = str(tool_input)
    return s or None


def main():
    # UTF-8 강제 — Windows 로케일(cp949 등)로 stdin 이 디코드되어 한글/멀티바이트 payload 가
    # 손상되는 것을 방지(binary read + utf-8 decode). 손상 시 redaction/noise 판정도 오작동.
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except Exception:
        try:
            raw = sys.stdin.read()
        except Exception:
            return 0
    if not raw:
        return 0

    try:
        data = json.loads(raw)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0

    _resolve_lib()
    try:
        from dev_process_hook_capture import record_hook_event
    except Exception:
        return 0  # lib 부재 → fail-open(record-only)

    try:
        tool_name = data.get("tool_name", "") or ""
        tool_input = data.get("tool_input", {})
        if not isinstance(tool_input, dict):
            tool_input = {}
        agent_type = data.get("agent_type")
        if not isinstance(agent_type, str):
            agent_type = None

        if tool_name == "Agent":
            subagent_type = tool_input.get("subagent_type")
            if not isinstance(subagent_type, str):
                subagent_type = None
            prompt = tool_input.get("prompt")
            content = prompt if isinstance(prompt, str) and prompt.strip() else None
            # lane ← subagent_type(spawn target) NON-ambient
            record_hook_event(
                "prompt_input", content=content,
                subagent_type=subagent_type, agent_type=agent_type,
            )
        else:
            content = _pre_tool_content(tool_name, tool_input)
            # lane ← agent_type(self) NON-ambient
            record_hook_event("tool_call", content=content, agent_type=agent_type)
    except Exception:
        return 0  # 어떤 실패도 non-blocking(record-only)
    return 0


if __name__ == "__main__":
    # exit 0 ALWAYS — capture 실패가 tool call 을 절대 차단하지 않는다(ADR-115)
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
