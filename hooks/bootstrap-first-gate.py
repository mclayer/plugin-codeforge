#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bootstrap-first-gate.py — UserPromptSubmit entry-gate hook (bootstrap-first 불변식).

목적:
  미초기화 greenfield repo 에서 사용자가 codeforge 사용을 선언(변경동사 또는
  codeforge 고유 신호)했을 때, bootstrap 미충족 상태를 surface 하고 초기화를
  우선 유도하는 정적 system-reminder 를 inject 한다. silent fallback (Issue #2243)
  으로 brainstorm 으로 새지 않게 메우는 entry-gate.

계약 SSOT:
  ADR-027 §결정 13 (Amendment 10) — codeforge 의도 선언 + 미초기화 → bootstrap-first.
    §13.A intent 감지 범위 (변경동사 ∪ distinctive marker, generic 명사 co-occurrence)
    §13.B AND-gate (intent ∧ exit3 ∧ adr dirs 부재 ∧ not-bypassed)
    §13.C 발화 = warning inject only, 모든 경로 exit 0, stderr 1-line audit
    §13.D GitHub remote 부재 시 자동 생성 금지 (명령 surface 만)
    §13.E bypass env (HOTFIX_BYPASS_CODEFORGE + REASON / BYPASS_BOOTSTRAP_GATE)
    §13.F wrapper plugin hooks/ 배치 + shim 답습

Phase 2 carrier: CFP-2243.

Input:
  stdin (Claude Code UserPromptSubmit hook payload — JSON 또는 raw text, bounded ≤1 MiB).
Output:
  stdout — `<system-reminder>` 블록 (발화 시에만, LLM context 에 prepend).
  stderr — 발화 경로 1-line audit (prompt 내용 echo 0).

불변식:
  - 모든 경로 exit 0 (P0 fail-safe) — 사용자 prompt erase 권한 미사용 (§13.C).
  - 사용자 prompt 텍스트는 stderr/stdout audit 에 절대 기록 안 함 (PII/secret leak 차단).

Required 의존: 없음 (표준 라이브러리만 사용).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

# ─────────────────────────────────────────────────────────────────────────────
# §13.A intent 감지 enum (ReDoS-free 단순 alternation — 중첩 quantifier 금지)
# ─────────────────────────────────────────────────────────────────────────────

# 변경 동사 — 한글 substring + 영어 \b word-boundary, IGNORECASE.
# overlay/hooks/userprompt_reminder.py CHANGE_PATTERNS verbatim 정합 (L36-43).
_CHANGE_VERB_RE = re.compile(
    r"(구현|만들|수정|짜|고쳐|추가|"
    r"\bfix\b|\bimplement\b|\brefactor\b|\bcreate\b|\badd\b|"
    r"\bbuild\b|\bchange\b|\bupdate\b|\bmodify\b|\bedit\b|\bwrite\b)",
    re.IGNORECASE,
)

# codeforge-distinctive marker — 영어 \b, 한글 substring, IGNORECASE.
# 단독 매치 = intent TRUE (codeforge 선언 확정). 일상 한국어에서 의미 충돌 없음.
_DISTINCTIVE_MARKER_RE = re.compile(
    r"(\bcodeforge\b|\bstory\b|\bepic\b|\blane\b|스토리|레인)",
    re.IGNORECASE,
)

# generic 명사 — 한글 substring. 단독 매치 금지 (false-positive 억제).
# 변경동사 OR distinctive marker co-occurrence 시에만 intent 기여.
_GENERIC_NOUN_RE = re.compile(r"(설계|아키텍처)")


def _read_input() -> str:
    """stdin 읽기 — bounded ≤1 MiB, JSON dict 우선, raw fallback.

    bounded read = 본 훅 신규 강화 (overlay/hooks/userprompt_reminder.py 의
    무제한 sys.stdin.read() 대비 — Change Plan §3.2(a)). DoS/메모리 폭주 차단.
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


def _matches_intent(text: str) -> bool:
    """§13.A intent 계약.

    intent = (변경동사 매치)
             OR (distinctive 매치)
             OR (generic 매치 AND (변경동사 매치 OR distinctive 매치))

    핵심 invariant: generic 명사(설계/아키텍처) 단독은 절대 intent TRUE 안 됨.
    마지막 항은 앞 2항이 이미 OR 로 TRUE 라 사실상 redundant 지만 계약 명시.
    """
    verb = bool(_CHANGE_VERB_RE.search(text))
    distinctive = bool(_DISTINCTIVE_MARKER_RE.search(text))
    generic = bool(_GENERIC_NOUN_RE.search(text))
    return verb or distinctive or (generic and (verb or distinctive))


def _plugin_root() -> str:
    """CLAUDE_PLUGIN_ROOT 우선, 없으면 __file__ 기준 plugin root (= hooks/ 의 부모)."""
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env_root:
        return env_root
    # __file__ = <plugin_root>/hooks/bootstrap-first-gate.py → 부모의 부모 = plugin_root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _detect_repo_kind(cwd: str) -> int:
    """detect-repo-kind.py subprocess 호출 → returncode 반환.

    exit code map (무변경 재사용): 0=plugin / 1=consumer / 2=mixed / 3=unknown.
    예외 (FileNotFoundError / TimeoutExpired / 기타) 시 비-3 sentinel(-1) 반환 —
    발화 안 되게 fail-safe (P0). exit3 만 미초기화 greenfield 후보.
    """
    script = os.path.join(_plugin_root(), "templates", "scripts", "detect-repo-kind.py")
    try:
        result = subprocess.run(
            [sys.executable, script, "--repo-root", cwd],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
        )
        return result.returncode
    except Exception:
        return -1  # 비-3 sentinel → 발화 차단 (fail-safe)


def _adr_dirs_absent(cwd: str) -> bool:
    """docs/adr 부재 AND archive/adr 부재 (§13.B 조건 3)."""
    return not os.path.isdir(os.path.join(cwd, "docs", "adr")) and not os.path.isdir(
        os.path.join(cwd, "archive", "adr")
    )


def _check_bypass(env: dict) -> tuple[bool, str | None]:
    """§13.E bypass env 검사.

    Returns:
      (True, "hotfix")   — HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON(non-empty).
      (True, "advisory") — BYPASS_BOOTSTRAP_GATE=1 (reason 불요 — advisory bypass).
      (False, None)      — bypass 미적용 (발화 진행).

    HOTFIX flag 만 set + reason 빈 경우 = bypass NOT honored → (False, None).
    본 훅은 advisory 라 REASON_MISSING warn 노이즈 없음 (userprompt_reminder 와 차이).
    """
    hotfix_flag = env.get("HOTFIX_BYPASS_CODEFORGE", "").strip()
    hotfix_reason = env.get("HOTFIX_BYPASS_REASON", "").strip()
    if hotfix_flag == "1" and hotfix_reason:
        return True, "hotfix"
    if env.get("BYPASS_BOOTSTRAP_GATE", "").strip() == "1":
        return True, "advisory"
    return False, None


def _build_reminder() -> str:
    """§13.C 정적 system-reminder 블록 (사용자 prompt echo 절대 금지).

    포함: bootstrap 미충족 surface / bootstrap-consumer.sh 안내 /
          GitHub remote 부재 시 gh repo create 명령 surface + 자동생성 안 함 통보.
    """
    return "\n".join(
        [
            "<system-reminder>",
            "[codeforge bootstrap-first-gate] codeforge 사용 의도 감지 — 그러나 이 repo 는 "
            "아직 codeforge 로 초기화되지 않은 greenfield 상태입니다 (ADR-027 §결정 13).",
            "",
            "bootstrap 미충족 — 작업 진입 전 초기화를 먼저 유도합니다 (block 아님, 권고):",
            "1. 초기화 스크립트 실행: `scripts/bootstrap-consumer.sh`",
            "   → consumer overlay 골격(.claude/_overlay/project.yaml 등) + ADR 디렉터리 seed.",
            "2. GitHub remote 부재 시 (Stage 1 fatal) 아래 명령을 surface 합니다 — "
            "자동 생성하지 않습니다(사용자 확인 필요):",
            "   `gh repo create <org>/<repo> --private --source=. --remote=origin`",
            "   → 사용자 GitHub 계정에 repo 가 생성되므로 명시 동의 없이 실행 금지.",
            "",
            "초기화 없이 진행을 명시 선택하면 silent fallback 됩니다(opt-out 보존). "
            "bypass: `BYPASS_BOOTSTRAP_GATE=1`.",
            "</system-reminder>",
        ]
    )


def main() -> int:
    """§13.B AND-gate. 모든 경로 exit 0 (P0 fail-safe — try/except 로 전체 감쌈)."""
    try:
        env = dict(os.environ)
        text = _read_input()
        cwd = os.getcwd()

        # 2. 입력 자체 없음 → exit 0 (audit 없음)
        if not text:
            return 0

        # 3. §13.A 1차 미매치 → early-exit 0 (detect subprocess skip, audit 생략)
        if not _matches_intent(text):
            return 0

        # 4. bypass → silent skip + audit
        if _check_bypass(env)[0]:
            print(
                "[bootstrap-first-gate] fired exit_path=silent-bypassed",
                file=sys.stderr,
            )
            return 0

        # 5. detect-repo-kind exit != 3 → 해당 silent 경로 + audit
        rc = _detect_repo_kind(cwd)
        if rc != 3:
            label = {
                0: "silent-plugin",
                1: "silent-consumer",
                2: "silent-mixed",
            }.get(rc, "silent-detect-error")
            print(
                f"[bootstrap-first-gate] fired exit_path={label}",
                file=sys.stderr,
            )
            return 0

        # 6. exit3 BUT ADR dir 존재 (이미 초기화) → silent-initialized + audit
        if not _adr_dirs_absent(cwd):
            print(
                "[bootstrap-first-gate] fired exit_path=silent-initialized",
                file=sys.stderr,
            )
            return 0

        # 7. 4조건 충족 (intent ∧ exit3 ∧ adr dirs 부재 ∧ not-bypassed) → 발화
        print(_build_reminder())
        print(
            "[bootstrap-first-gate] fired exit_path=warn-injected",
            file=sys.stderr,
        )
        return 0
    except Exception:
        # 8. P0 fail-safe — 어떤 예외도 exit 0 (prompt echo 0)
        try:
            print(
                "[bootstrap-first-gate] fired exit_path=silent-exception",
                file=sys.stderr,
            )
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
