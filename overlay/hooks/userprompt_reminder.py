#!/usr/bin/env python3
"""userprompt_reminder.py — UserPromptSubmit hook (변경 착수 reminder inject).

CFP-104 (Phase 2b of CFP-96 Epic). ADR-027 §결정-2 Secondary trigger 의 wrapper-side enforcement.

Input:
  stdin (Claude Code UserPromptSubmit hook payload — JSON 또는 raw text).
Output:
  stdout — `<system-reminder>` 블록 (LLM context 에 prepend됨).
  stderr — bypass / 진단 log.

동작:
  1. stdin parse (JSON dict 의 "prompt"/"user_message"/"message"/"text"/"content" 또는 raw text).
  2. CHANGE_PATTERNS regex 검출 — 비-매칭 시 silent.
  3. Bypass env 검사 (HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON 양 set).
     - 양 set → silent skip + stderr audit log.
     - flag 만 set → reminder + WARN (REASON_MISSING).
     - 둘 다 unset → reminder.
  4. git branch 명 parse → 활성 Story key + phase (cfp-N/... or mct-N/...).
  5. Reminder 출력.

Cross-platform: POSIX bash (`userprompt-reminder.sh`) + Windows PowerShell
(`userprompt-reminder.ps1`) thin wrapper 가 본 모듈 호출.

Required 의존: 없음 (표준 라이브러리만 사용).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

CHANGE_PATTERNS = [
    re.compile(
        r"(구현|만들|수정|짜|고쳐|추가|"
        r"\bfix\b|\bimplement\b|\brefactor\b|\bcreate\b|\badd\b|"
        r"\bbuild\b|\bchange\b|\bupdate\b|\bmodify\b|\bedit\b|\bwrite\b)",
        re.IGNORECASE,
    ),
]

BRANCH_STORY_RE = re.compile(
    r"^(?P<prefix>cfp|mct)-(?P<num>\d+)(?:/(?P<phase>.+))?$",
    re.IGNORECASE,
)


def _read_input() -> str:
    """stdin 읽기 — JSON dict 우선, raw fallback."""
    try:
        if sys.stdin.isatty():
            return ""
    except Exception:
        pass
    try:
        raw = sys.stdin.read()
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


def _matches_change_intent(
    text: str,
    patterns: list[re.Pattern[str]] | None = None,
) -> bool:
    pats = patterns if patterns is not None else CHANGE_PATTERNS
    return any(p.search(text) for p in pats)


def _run_git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _detect_active_story() -> tuple[str | None, str | None]:
    """git branch 명 → Story key + phase 추정.

    branch 형식:
      - `cfp-N/<phase>` → ("CFP-N", phase)
      - `mct-N/<phase>` → ("MCT-N", phase)
      - 다른 형식 (main / detached / non-Story branch) → (None, None)
    """
    branch = _run_git_branch()
    if not branch:
        return None, None
    m = BRANCH_STORY_RE.match(branch)
    if not m:
        return None, None
    key = f"{m.group('prefix').upper()}-{m.group('num')}"
    return key, m.group("phase") or None


def _check_bypass(env: dict[str, str]) -> tuple[bool, str | None]:
    """Bypass env 검사.

    Returns:
      (True, reason) — 양 env set, bypass honored.
      (False, "REASON_MISSING") — flag 만 set, reason empty. Bypass NOT honored.
      (False, None) — 둘 다 unset.
    """
    flag = env.get("HOTFIX_BYPASS_CODEFORGE", "").strip()
    reason = env.get("HOTFIX_BYPASS_REASON", "").strip()
    if flag == "1" and reason:
        return True, reason
    if flag == "1":
        return False, "REASON_MISSING"
    return False, None


def _build_reminder(
    story_key: str | None,
    phase: str | None,
    bypass_warn: bool,
) -> str:
    lines = [
        "<system-reminder>",
        "[codeforge] 변경 요청 감지 — codeforge protocol 의무 (ADR-027 §결정-2 Secondary trigger).",
        "",
        "필수 절차:",
        "1. Story phase label 확인 (`phase:요구사항|설계|구현` 등). 미설정 시 신규 Story Issue Form 제출.",
        "2. spec / plan 갱신 → Codex 7-area review → Sonnet decider 의무 (ADR-022).",
        "3. main 직커밋 금지 — branch + PR 절차 의무.",
        "",
    ]
    if story_key:
        suffix = f" (branch phase={phase})" if phase else ""
        lines.append(f"활성 Story: {story_key}{suffix}")
    else:
        lines.append("활성 Story 미검출 — 신규 Story Issue Form (`story.yml`) 제출 후 진입.")
    if bypass_warn:
        lines.extend([
            "",
            "WARN: HOTFIX_BYPASS_CODEFORGE=1 set — but HOTFIX_BYPASS_REASON empty. Bypass NOT honored.",
            "      bypass 사용 시 양 env 모두 set 의무 (사유 추적).",
        ])
    lines.extend([
        "",
        "Bypass 절차: HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON='<incident-id 또는 사유>' 양 env 의무.",
        "</system-reminder>",
    ])
    return "\n".join(lines)


def main() -> int:
    env = dict(os.environ)
    text = _read_input()
    if not text:
        return 0
    if not _matches_change_intent(text):
        return 0
    bypassed, reason = _check_bypass(env)
    if bypassed:
        print(
            f"[userprompt-reminder] BYPASS: HOTFIX_BYPASS_CODEFORGE=1 reason={reason!r}",
            file=sys.stderr,
        )
        return 0
    bypass_warn = (reason == "REASON_MISSING")
    story_key, phase = _detect_active_story()
    print(_build_reminder(story_key, phase, bypass_warn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
