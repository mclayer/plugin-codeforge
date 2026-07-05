#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""story-transition-autonomy-reminder.py — UserPromptSubmit reminder hook (모든 자명-진행 지점 자율 진행).

목적:
  모든 turn 에 ADR-071 §결정 22 의 자명-진행 자율 norm 을 additionalContext 로 무조건(unconditional)
  inject 한다. scope = 모든 자명-진행 지점 (Story 전환 + lane 경계 + 작업 완료-후 + vague-pause 금지)
  — ADR-144 §결정 3 로 "Story 전환 한정"에서 일반화. 전환·lane 경계·완료-후 어느 지점에서든 부당하게
  멈추거나(over-halt) 확인 질문(over-ask)하거나, 잔여작업 有 + 결정 payload=0 인 vague-pause
  ("한 숨 쉬어가자")로 정지하는 것을 억제하는 reminder hook. 정당 멈춤 3종(ask-trigger)은 carve-out 보존.

  tier: [advisory / priming]
    (taxonomy 명명·priming; NEVER block — 본 reminder hook 은 절대 deny/block 안 함. ADR-144 §결정 3/7)

계약 SSOT:
  ADR-071 §결정 22 (Amendment 13/14) — 자명-진행 자율 진행 norm (채널 1 = UserPromptSubmit body).
  ADR-144 §결정 3 — 자명-진행 priming scope 확장 (전환 → 모든 자명-진행 지점), Realization = ADR-071 Amendment 14.

Phase 2 carrier: CFP-2567 (scope 확장 carrier: CFP-2573).

Input:
  stdin (Claude Code UserPromptSubmit hook payload — JSON 또는 raw text, bounded ≤1 MiB).
  입력은 읽되 발화 판정에 미사용 (unconditional fire — prompt echo 0).
Output:
  stdout — JSON `hookSpecificOutput.additionalContext` (`<system-reminder>` 블록, 매 turn).
  stderr — 발화 경로 1-line audit (prompt 내용 echo 0).

불변식:
  - 전경로 exit 0 (P0 fail-safe) — 사용자 prompt erase 권한 미사용.
  - prompt echo 0 — 사용자 prompt 텍스트는 stdout/stderr 어디에도 절대 기록 안 함 (PII 차단).
  - unconditional fire — regex gate 없음, 모든 turn 발화.

Required 의존: 없음 (표준 라이브러리만 사용).
"""

from __future__ import annotations

import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _read_input() -> str:
    """stdin 읽기 — bounded ≤1 MiB, JSON dict 우선, raw fallback.

    skip-offer-reminder.py _read_input verbatim 복제 (self-contained — 의도적 self-containment).
    """
    try:
        if sys.stdin.isatty():
            return ""
    except Exception:
        pass
    try:
        raw = sys.stdin.read(1 << 20)  # bounded ≤1 MiB
    except Exception:
        return ""
    if not raw:
        return ""
    raw_stripped = raw.strip()
    try:
        data = json.loads(raw_stripped)
        if isinstance(data, dict):
            for k in ("prompt", "user_message", "message", "text", "content"):
                v = data.get(k)
                if isinstance(v, str):
                    return v
        return raw
    except (json.JSONDecodeError, ValueError):
        return raw


def _build_reminder() -> str:
    """ADR-071 §결정 22 / ADR-144 §결정 3 자명-진행 자율 규칙 정적 system-reminder 블록.

    scope = 모든 자명-진행 지점 (전환 + lane 경계 + 완료-후 + vague-pause 금지). STATIC (runtime value
    interpolation 금지, no PII) — 사용자 prompt echo 절대 금지.
    """
    return "\n".join(
        [
            "<system-reminder>",
            "[codeforge story-transition-autonomy] 모든 자명-진행 지점 자율 진행 (ADR-071 §결정 22 / ADR-144 §결정 3):",
            "",
            "- Epic 을 한 세션에서 여러 child Story 로 진행할 때, Story N→N+1 전환 (및 단일 Story "
            "Phase1→Phase2 전환) = 자동 이어서 진행이 default. 멈춤·질문은 default 아님.",
            "- lane 경계(레인 전이)에서도 자동 진행이 default — 다음 lane 진입을 별도 확인 없이 이어서 진행.",
            "- 작업 완료-후 다음 자명 작업(backlog 후속 / 다음 자명 단계)으로도 자동 진행이 default — "
            "완료 보고 후 무발화 정지·확인 질문 금지.",
            "- 전환·lane 경계·완료-후 어느 지점에서든 무발화로 멈추거나(over-halt) \"다음 진행할까요?\" 확인 "
            "질문(over-ask) 하지 마라 — 둘 다 §결정 15(3-touchpoint)·§결정 20(ask-trigger 3종) 어디에도 미해당인 부당한 멈춤.",
            "- vague-pause(\"한 숨 쉬어가자\" 류 = 잔여작업 有 + 결정 payload=0 + volitional 발화) 금지 — "
            "decision-null pause 는 ask-trigger 3종 미해당 부당 정지 (ADR-144 §결정 2 / ADR-025 §결정 7 Amendment 3).",
            "- 정당한 멈춤 3종만 전환 지점에서도 보존(억제 대상 아님): ① 요구 자체가 애매 / "
            "② 진짜 가치 trade-off(default 비자명) / ③ 비가역·고비용.",
            "- session-swap(\"context 가득 → 별 세션\")은 별 축(§결정 18) — 본 norm 과 disjoint, "
            "cross-ref only.",
            "</system-reminder>",
        ]
    )


def _emit(text: str) -> None:
    """JSON additionalContext emit (plain stdout prepend 금지 — #13912 회귀 차단).

    형식 = skip-offer-reminder.py _emit 동형 (live hooks-guide 확인됨).
    """
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }
    }
    print(json.dumps(out, ensure_ascii=False))


def main() -> int:
    """UNCONDITIONAL fire — 전경로 exit 0 (P0 fail-safe — try/except 로 전체 감쌈)."""
    try:
        # 1. 입력은 읽되 발화 판정에 미사용 (unconditional, echo 0)
        _ = _read_input()
        # 2. text 무관 무조건 발화
        _emit(_build_reminder())
        # 3. stderr 1-line audit (prompt 텍스트 절대 미기록 — PII 차단)
        print(
            "[story-transition-autonomy-reminder] fired exit_path=injected",
            file=sys.stderr,
        )
        return 0
    except Exception:
        # P0 fail-safe — 어떤 예외도 exit 0 (prompt echo 0)
        try:
            print(
                "[story-transition-autonomy-reminder] fired exit_path=silent-exception",
                file=sys.stderr,
            )
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
