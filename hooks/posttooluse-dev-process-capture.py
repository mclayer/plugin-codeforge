#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# PostToolUse capture adapter (NET-NEW hook surface) — dev-process-event-v1 Port A — CFP-2687 Phase 2 D3
#
# 설계 SSOT: ADR-155 §결정 4(capture 이원화 — PostToolUse net-new) + change-plan §3.4
#           + §7.4(record-only non-blocking exit0, ADR-115) + §결정 5(INV-8b)
#           + §3.3(5 noise-discard) + Story §5.4(noise false-negative — 무변경/0-byte 보존).
#
# 책임 (net-new PostToolUse — 이전 PostToolUse hook 0):
#   - tool_name in {Write,Edit,MultiEdit} → event_type=diff  (content=변경 내용, 무변경 → content=None).
#   - 그 외(Bash 등)                       → event_type=tool_call (content=결과 출력, noise filter 적용).
#   - diff/output content → capture_blob(INV-8b) 경유. index 는 blob_ref-only(content-blind). emit_source="hook".
#
# ★noise-discard(§3.3) — 5 규칙(진행 스피너/토큰중복/의존성설치로그/무변경파일목록/저신호 verbose):
#   pure noise 는 **content blob 만 억제**(→ None). 이벤트(fact)는 그대로 index 기록.
#   ★over-discard 금지(§5.4): diff 0-byte / 파일 0("수정 시도했으나 무변경") = content=None 이어도
#   diff 이벤트를 기록해 "무변경 사실"을 보존한다.
#
# ★record-only / non-blocking / exit 0 ALWAYS(ADR-115): 모든 경로 sys.exit(0). stdout 미방출.

import json
import os
import sys


def _resolve_lib():
    here = os.path.dirname(os.path.abspath(__file__))
    roots = []
    pr = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if pr:
        roots.append(pr)
    roots.append(os.path.dirname(here))
    for r in roots:
        lib = os.path.join(r, "scripts", "lib")
        if os.path.isdir(lib) and lib not in sys.path:
            sys.path.insert(0, lib)


def _diff_content(tool_name, tool_input):
    """편집 도구 변경 내용 → capture 대상 str. 무변경/빈 변경 → None(fact 는 이벤트로 보존).

    redaction/bound 은 capture_blob 소관 — 여기선 변경 본문만 구성.
    """
    if not isinstance(tool_input, dict):
        return None
    if tool_name == "Write":
        c = tool_input.get("content")
        return c if isinstance(c, str) and c.strip() else None
    if tool_name == "Edit":
        old = tool_input.get("old_string") or ""
        new = tool_input.get("new_string") or ""
        if old == new:
            return None  # 무변경 → content=None(이벤트는 보존 → 수정시도-무변경 fact)
        body = "--- old\n%s\n+++ new\n%s" % (old, new)
        return body if body.strip() else None
    if tool_name == "MultiEdit":
        edits = tool_input.get("edits")
        if not edits:
            return None
        try:
            return json.dumps(edits, ensure_ascii=False)
        except Exception:
            return str(edits) or None
    return None


def _stringify_response(resp):
    """tool_response → capture 대상 str(없으면 None). dict/list 는 JSON 직렬화(redaction 은 capture_blob)."""
    if resp is None:
        return None
    if isinstance(resp, str):
        return resp if resp.strip() else None
    try:
        s = json.dumps(resp, ensure_ascii=False)
    except Exception:
        s = str(resp)
    return s if s and s.strip() and s not in ("{}", "[]", "null") else None


def main():
    # UTF-8 강제 — Windows 로케일(cp949 등) stdin 디코드로 한글/멀티바이트 payload 손상 방지
    # (손상 시 diff/output redaction·noise 판정 오작동).
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
        return 0  # lib 부재 → fail-open

    try:
        tool_name = data.get("tool_name", "") or ""
        tool_input = data.get("tool_input", {})
        if not isinstance(tool_input, dict):
            tool_input = {}
        tool_response = data.get("tool_response")
        agent_type = data.get("agent_type")
        if not isinstance(agent_type, str):
            agent_type = None

        if tool_name in ("Write", "Edit", "MultiEdit"):
            # diff — 무변경이면 content=None 이나 이벤트는 기록(§5.4 fact 보존). noise filter 미적용(편집=noise 아님).
            content = _diff_content(tool_name, tool_input)
            record_hook_event(
                "diff", content=content, agent_type=agent_type, apply_noise_filter=False,
            )
        else:
            # tool_call 결과 — 출력 content 에 noise filter 적용(스피너/설치로그 등 blob 억제, 이벤트 보존)
            content = _stringify_response(tool_response)
            record_hook_event(
                "tool_call", content=content, agent_type=agent_type, apply_noise_filter=True,
            )
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
