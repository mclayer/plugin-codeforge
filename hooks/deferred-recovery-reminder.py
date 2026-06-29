#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deferred-recovery-reminder.py — UserPromptSubmit phase:완료 reminder hook.

목적:
  phase:완료 근접 컨텍스트(회고/완료/후속/deferred 등 키워드)에서
  "retro/Story 서사의 deferred 항목 각각을 (추적 Issue 전환) 또는
  (관찰-only + 사유 명시) 으로 명시 판정하라" 환기 reminder 를 inject 한다.
  silent drop 금지 게이트 (ADR-128 Amendment 1 / CFP-2470).

계약 SSOT:
  ADR-128 Amendment 1 — deferred 판정 의무화 entry-gate.
    (intent 감지 범위 = "완료/retro/회고/deferred/후속/미해결/phase:완료" 류 키워드)
    (발화 = `<system-reminder>` inject only, 모든 경로 exit 0, 사용자 prompt echo 0)
    (PAT/성공/실패 = 모두 silent fallback, audit stderr 1-line only)

Phase 2 carrier: CFP-2470.

Input:
  stdin (Claude Code UserPromptSubmit hook payload — JSON 또는 raw text, bounded ≤1 MiB).
Output:
  stdout — `<system-reminder>` 블록 (발화 시에만, LLM context 에 prepend).
  stderr — 발화 경로 1-line audit (prompt 내용 echo 0).

불변식:
  - 모든 경로 exit 0 (P0 fail-safe).
  - 사용자 prompt 텍스트는 stderr/stdout audit 에 절대 기록 안 함 (PII/secret leak 차단).
"""

from __future__ import annotations

import json
import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# intent 감지 enum (ReDoS-free 단순 alternation — 중첩 quantifier 금지)
# ─────────────────────────────────────────────────────────────────────────────

# phase:완료 / retro / 회고 / deferred / 후속 / 미해결 등 키워드
# 한글 substring + 영어 \b word-boundary, IGNORECASE.
# bootstrap-first-gate 와 유사 패턴이나 성격이 다름: 완료/회고 특화.
_COMPLETION_KEYWORD_RE = re.compile(
    r"(완료|retro|회고|deferred|후속|미해결|"
    r"\bphase:완료\b|\bclosure\b|\bwrapup\b|"
    r"deferred|pending|follow.?up)",
    re.IGNORECASE,
)


def _read_input() -> str:
    """stdin 읽기 — bounded ≤1 MiB, JSON dict 우선, raw fallback."""
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


def _matches_intent(text: str) -> bool:
    """intent 계약 — 완료/회고/후속 류 키워드 매칭."""
    return bool(_COMPLETION_KEYWORD_RE.search(text))


def _build_reminder() -> str:
    """deferred 판정 의무화 system-reminder 블록 (사용자 prompt echo 절대 금지)."""
    return "\n".join(
        [
            "<system-reminder>",
            "[deferred-recovery-reminder] phase:완료 또는 회고(retro) 컨텍스트 감지 — "
            "ADR-128 Amendment 1 (CFP-2470) deferred 판정 의무화 환기.",
            "",
            "**Action required**: retro 서사 또는 완료 기록에서 'deferred'·'후속'·'미해결' 표시된 항목 각각을",
            "다음 중 하나로 명시 판정하세요 (silent drop 금지):",
            "  ① 추적 Issue 로 전환 — GitHub Issue 또는 Story 로 격상해서 별도 스토리 계획에 포함.",
            "  ② 관찰-only + 사유명시 — '관찰됨, 조치 미필요 (사유: ...)' 형태로 기록 (ADR-128).",
            "",
            "silent drop(무음소각) = 기록은 있으나 액션 계획 없는 경우 — 본 환기가 차단.",
            "더 자세한 정보: ADR-128 Amendment 1 / docs/decisions/ADR-128-*.md",
            "</system-reminder>",
        ]
    )


def main() -> int:
    """intent 매칭 → 발화 또는 silent pass. 모든 경로 exit 0 (P0 fail-safe)."""
    try:
        text = _read_input()

        # 입력 없음 → exit 0
        if not text:
            return 0

        # intent 미매치 → early-exit 0 (audit 생략)
        if not _matches_intent(text):
            return 0

        # intent 매치 → 발화
        print(_build_reminder())
        print(
            "[deferred-recovery-reminder] fired exit_path=warn-injected",
            file=sys.stderr,
        )
        return 0

    except Exception:
        # P0 fail-safe — 어떤 예외도 exit 0
        try:
            print(
                "[deferred-recovery-reminder] fired exit_path=silent-exception",
                file=sys.stderr,
            )
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
