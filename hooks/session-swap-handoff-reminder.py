#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""session-swap-handoff-reminder.py — UserPromptSubmit reminder hook (세션 전환 권유 시 자족 handoff 프롬프트 선제 생성).

목적:
  세션 전환(별도 세션 인계)을 권유하려는 순간, 그 권유 발화 前에 자족(self-contained) handoff
  프롬프트를 먼저 생성·동반하라는 ADR-071 §결정 24 controlled-path norm 을 매 turn additionalContext 로
  무조건(unconditional) inject 한다. handoff 미동반 bare reflex 전환("context 가득 → 새 세션")은
  §결정 18 anti-pattern 그대로 차단 대상 — 본 hook 은 그 차단을 우회하지 않고, 정당 trigger 도
  handoff 의무를 지도록 선제 priming 한다.

  tier: [advisory / priming]
    (taxonomy 명명·priming; NEVER block — 본 reminder hook 은 절대 deny/block 안 함. ADR-144 §결정 3/7)

계약 SSOT:
  ADR-071 §결정 24 — session-swap controlled-path (handoff 6 필수요소 + 자족성 + advisory ceiling).
  docs/consumer-guide.md §7.6 — Session-swap controlled-path 상속 (cross-ref anchor).

Phase 2 carrier: CFP-2742 (Phase 1 정책 prose 상속 = §7.6 forward-note, Phase 2 = 본 reminder-hook 자동전파).

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
    """ADR-071 §결정 24 session-swap controlled-path 정적 system-reminder 블록.

    STATIC (runtime value interpolation 금지, no PII) — 사용자 prompt echo 절대 금지.
    """
    return "\n".join(
        [
            "<system-reminder>",
            "[codeforge session-swap-handoff] 세션 전환 권유 시 자족 handoff 프롬프트 선제 생성 (ADR-071 §결정 24):",
            "",
            "- context/메모리 포화 등으로 세션 전환(별도 세션 인계)을 권유하려면, 권유 발화 前 자족 "
            "handoff 프롬프트를 먼저 생성·동반하라.",
            "- handoff 6 필수요소: ① 진행 Story/PR·Epic 번호 ② 완료 vs 남은 lane·단계 ③ worktree·브랜치 "
            "경로 ④ 기결정=재논의 금지 목록 ⑤ 이번 세션 gotcha ⑥ 다음 세션 첫 액션 1문.",
            "- 자족성: 현 세션 참조 0(다음 세션이 0-context 재개) + 복붙 1회 완결.",
            "- handoff 미동반 bare reflex 전환('context 가득 → 새 세션')은 여전히 §결정 18 anti-pattern "
            "차단. 정당 trigger(구조변경 재구동 / 모델 fallback)도 handoff 의무.",
            "- advisory priming — 전환 자체를 장려하지 않음(/compact·MEMORY.md 슬림화 대체 path 우선). "
            "handoff 는 전환이 발생할 때의 손실 방지 의무.",
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
            "[session-swap-handoff-reminder] fired exit_path=injected",
            file=sys.stderr,
        )
        return 0
    except Exception:
        # P0 fail-safe — 어떤 예외도 exit 0 (prompt echo 0)
        try:
            print(
                "[session-swap-handoff-reminder] fired exit_path=silent-exception",
                file=sys.stderr,
            )
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
