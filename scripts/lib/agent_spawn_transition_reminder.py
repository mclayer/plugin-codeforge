#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""agent_spawn_transition_reminder.py — PreToolUse(Agent) 자명-진행 자율 reminder SSOT helper (채널 2).

목적:
  PreToolUse(Agent) hook(pretooluse-agent-spawn-gate)이 매 Agent spawn 직전 호출하는 self-contained
  stdlib python 모듈. Agent spawn = autonomous 전환 창 priming 이므로, ADR-071 §결정 22 / ADR-144 §결정 3
  의 자명-진행 자율 norm ("Story 전환 + lane 경계 + 완료-후 자동 이어서 진행 default, over-halt/over-ask/
  vague-pause 금지(정당 멈춤 3종 예외)")을 `hookSpecificOutput.additionalContext` 로 non-block inject 한다.
  scope 는 ADR-144 §결정 3 로 "Story 전환 한정"에서 모든 자명-진행 지점으로 일반화.

  tier: [advisory / priming]
    (taxonomy 명명·priming; NEVER deny — permissionDecision 키 미emit(= allow). ADR-144 §결정 3/7)

계약 SSOT:
  ADR-071 §결정 22 (Amendment 13/14) — 채널 2 = PreToolUse(Agent) additionalContext priming.
  ADR-144 §결정 3 — 자명-진행 priming scope 확장 (전환 → 모든 자명-진행 지점).

Phase 2 carrier: CFP-2567 (scope 확장 carrier: CFP-2573).

불변식:
  - NEVER deny — `permissionDecision` 키를 절대 emit 하지 않는다(미설정 = allow). Wave1 spawn 무손상.
  - 전경로 exit 0 (fail-open) — payload parse 실패/예외 포함 어떤 경우도 spawn block 안 함.

Input:
  stdin (PreToolUse tool_input JSON payload — bounded ≤1 MiB). parse 실패 시 {} (fail-open).
Output:
  stdout — JSON `hookSpecificOutput.additionalContext` (전환-자율 priming 문자열).

Required 의존: 없음 (표준 라이브러리만 사용).
"""

from __future__ import annotations

import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SPAWN_MARKER = "[codeforge story-transition-autonomy]"


def _read_payload() -> dict:
    """stdin 을 bounded(≤1 MiB) 로 읽어 json.loads → dict 반환, 실패 시 {} (fail-open)."""
    try:
        raw = sys.stdin.read(1 << 20)  # bounded ≤1 MiB
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def _extract_subagent_type(payload: dict) -> str:
    """payload["tool_input"]["subagent_type"] str 반환, 없으면 ""."""
    try:
        tool_input = payload.get("tool_input", {})
        if isinstance(tool_input, dict):
            st = tool_input.get("subagent_type", "")
            if isinstance(st, str):
                return st
    except Exception:
        pass
    return ""


def _is_lane_pl(subagent_type: str) -> bool:
    """lane-PL class 판별 (over-fire 완화용 targeting)."""
    st = subagent_type or ""
    return "PL" in st or st.endswith("PLAgent")


def _build_context(subagent_type: str) -> str:
    """전환-자율 priming 문자열 반환. SPAWN_MARKER 로 시작. lane-PL 이면 targeting 문장 1개 추가."""
    base = (
        "[codeforge story-transition-autonomy] Agent spawn = autonomous 전환 창 priming "
        "(ADR-071 §결정 22 / ADR-144 §결정 3): Story 전환·lane 경계·작업 완료-후 어느 자명-진행 지점도 "
        "자동 이어서 진행이 default. over-halt(무발화 정지)·over-ask(\"다음 진행할까요?\") 금지 + "
        "vague-pause(\"한 숨 쉬어가자\" = 잔여작업 有 + 결정 payload=0 + volitional 발화) 금지 "
        "(decision-null pause, ADR-144 §결정 2 / ADR-025 §결정 7 Amendment 3) — 정당 멈춤 3종"
        "(① 요구 애매 / ② 진짜 가치 trade-off / ③ 비가역·고비용) 만 예외. session-swap 은 "
        "disjoint 축(§결정 18)."
    )
    if _is_lane_pl(subagent_type):
        base += (
            " (lane-PL spawn — 다음 Story/Phase 전환 지점에서도 별도 확인 없이 자동 이어서 진행.)"
        )
    return base


def _emit(text: str) -> None:
    """PreToolUse additionalContext emit — permissionDecision 키 절대 미포함(NEVER deny = allow)."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": text,
                }
            },
            ensure_ascii=False,
        )
    )


def main() -> int:
    """payload 읽고 subagent_type 추출 후 emit — 전경로 exit 0 (예외도 exit 0)."""
    try:
        payload = _read_payload()
        st = _extract_subagent_type(payload)
        _emit(_build_context(st))
        return 0
    except Exception:
        # fail-open — 어떤 예외도 spawn block 안 함
        return 0


if __name__ == "__main__":
    sys.exit(main())
