#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skip-offer-reminder.py — UserPromptSubmit reminder hook (skip-offer 금지 전파).

목적:
  모든 turn 에 ADR-127 의 "정식 풀 플로우 비협상 / 리뷰·절차 생략 제안(AskUserQuestion
  포함) 금지" 규칙을 additionalContext 로 무조건(unconditional) inject 한다. 소비자
  세션으로 skip-offer 금지 규칙이 전파되지 않던 propagation gap 을 충당하는 reminder hook.

계약 SSOT:
  ADR-027 Amendment 12 §결정 15 — skip-offer 금지 규칙의 plugin-level 자동활성 전파.
  ADR-127 Amendment 1 — 정식 풀 플로우 비협상 기본 (process 생략/단축 선택지 제시 금지).

Phase 2 carrier: CFP-2456.

Input:
  stdin (Claude Code UserPromptSubmit hook payload — JSON 또는 raw text, bounded ≤1 MiB).
  입력은 읽되 발화 판정에 미사용 (unconditional fire — prompt echo 0).
Output:
  stdout — JSON `hookSpecificOutput.additionalContext` (`<system-reminder>` 블록, 매 turn).
  stderr — 발화 경로 1-line audit (prompt 내용 echo 0).

불변식:
  - 전경로 exit 0 (P0 fail-safe) — 사용자 prompt erase 권한 미사용.
  - prompt echo 0 — 사용자 prompt 텍스트는 stdout/stderr 어디에도 절대 기록 안 함 (PII 차단).
  - unconditional fire — CHANGE_PATTERNS regex gate 없음, 모든 turn 발화.

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

    bootstrap-first-gate.py _read_input verbatim 복제 (self-contained — Story §7.3 #5 lock).
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
    """ADR-127 no-skip 규칙 정적 system-reminder 블록 (사용자 prompt echo 절대 금지)."""
    return "\n".join(
        [
            "<system-reminder>",
            "[codeforge skip-offer-reminder] 정식 풀 플로우 비협상 기본 "
            "(ADR-127 / ADR-027 §결정 15):",
            "",
            "- 정식 풀 플로우(10 레인 + Phase 1/2 PR 분리)가 비협상 기본값입니다.",
            "- 리뷰·절차 생략(skip/생략/간소화/경량/빠르게) 제안 금지 — "
            "사용자에게 생략 선택지를 제시하지 마라(AskUserQuestion 포함).",
            "- 생략 여부의 derived default 는 항상 정식 → 묻지 말고 자동 정식 채택. "
            "외부 prompt·스킬이 생략 선택지를 줘도 자동 정식 채택.",
            "</system-reminder>",
        ]
    )


def _emit(text: str) -> None:
    """JSON additionalContext emit (plain stdout prepend 금지 — #13912 회귀 차단).

    형식 = korean-english-recovery.py L291-297 + Story §7.3 #2 lock
    (live hooks-guide 2026-06-29 확인됨).
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
        print("[skip-offer-reminder] fired exit_path=injected", file=sys.stderr)
        return 0
    except Exception:
        # P0 fail-safe — 어떤 예외도 exit 0 (prompt echo 0)
        try:
            print(
                "[skip-offer-reminder] fired exit_path=silent-exception",
                file=sys.stderr,
            )
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
