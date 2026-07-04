#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2574 / ADR-143 §결정 4 — PreToolUse(Agent) spawn description-format DETECT verifier
# ADR-061 Amendment 3 §결정 11 — Python script-writing convention + CodeQL ReDoS guard
#
# 목적 (범위① Agent spawn 최상위 헤더 description):
#   Agent spawn 의 tool_input.description 이 렌더-줄 프리픽스 형식
#   `[에이전트명] MM/DD HH:MM - 내용` 인지 DETECT (warning-tier, exit 0 ALWAYS, rewrite/mutation 0).
#   SecurityArch §7.1 non-mutation invariant 상속 — description 을 읽되 되쓰지 않고 exit code advisory-only.
#
# Entry-point:
#   python3 check_spawn_description_prefix.py --description-stdin
#     stdin: spawn description 문자열
#   stdout JSON: {"description_prefix_conformant": <bool>, "empty": <bool>, "checked": "<앞 80자>"}
#   exit 0: ALWAYS (conformant 든 아니든). nonconformant 시 stderr 에 warning 1줄.
#
# Bypass:
#   BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 →
#     stdout JSON {"bypass": true, "description_prefix_conformant": true}, exit 0.
#
# 판정 규칙 (ADR-143 §결정 2):
#   - RE_PREFIX = ^\[[^\]]{1,64}\] \d{2}/\d{2} \d{2}:\d{2} - \S (anchored, bounded, ReDoS-safe)
#     · re.match() 선두 앵커 / 부정 문자 클래스 [^\]] 비중첩 / open-ended .* 부재 / 양화사 중첩 부재.
#     · 이 regex 가 자동으로 AC-3(정확히 ` - ` 단일공백-하이픈-공백) · AC-4(offset `+09:00` 있으면 미매칭) ·
#       AC-15(컴팩트 MM/DD HH:MM) 를 강제.
#   - 빈 description (strip 후 "") → empty:true, description_prefix_conformant:true (leaf 빈 description 은 위반 아님, AC-10).
#
# SSOT carrier: CFP-2574 Phase 2 (ADR-143 §결정 4)

import sys
import re
import os
import json

# Windows console 호환 — UTF-8 강제 (check_spawn_prompt_format.py 관례 답습)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── 상수 ─────────────────────────────────────────────────────────────────────

SCRIPT_NAME = "[check-spawn-description-prefix]"

# checked 미리보기 길이 (앞 N자)
CHECKED_PREVIEW_LEN = 80

# ── Anchored simple regex (CodeQL ReDoS guard 준수, ADR-061 Amd3 §결정 11) ────
#
# 규칙:
#   - re.match() 사용 (선두 앵커 — '^' 명시)
#   - 부정 문자 클래스 [^\]] 단일 (중첩·sentinel 부재)
#   - 양화사 중첩 금지: (?:...)*? / (.+)+ 등 부재
#   - open-ended .* 부재 (bounded {1,64})
#
# 프리픽스: [<에이전트명 1~64자, ] 미포함>] <MM>/<DD> <HH>:<MM> - <내용 1자+>
#   `] `(닫는 대괄호+공백) → `\d{2}/\d{2}`(날짜, / 구분자) → ` ` → `\d{2}:\d{2}`(시각) → ` - `(공백-하이픈-공백) → `\S`(내용 최소 1 non-ws)
# ADR-143 §결정 2 `- 내용` nonempty 정합 — 끝 `\S` 로 empty-content(`- ` 뒤 빈/trailing space)를 nonconformant 로 tighten.
#   빈 필드(프리픽스 자체 부재, strip=="")는 check_description 의 별도 empty 분기(regex 미도달)로 conformant 보존.
RE_PREFIX = re.compile(r'^\[[^\]]{1,64}\] \d{2}/\d{2} \d{2}:\d{2} - \S')


# ── 핵심 검증 함수 ────────────────────────────────────────────────────────────

def check_description(description: str) -> dict:
    """
    spawn description 의 렌더-줄 프리픽스 형식 conformance DETECT.

    반환:
      {
        "description_prefix_conformant": <bool>,
        "empty": <bool>,
        "checked": "<앞 80자>",
      }
    """
    checked = description[:CHECKED_PREVIEW_LEN]

    # 빈 description (strip 후 "") — leaf 빈 description 은 위반 아님 (AC-10)
    if description.strip() == "":
        return {
            "description_prefix_conformant": True,
            "empty": True,
            "checked": checked,
        }

    conformant = RE_PREFIX.match(description) is not None
    return {
        "description_prefix_conformant": conformant,
        "empty": False,
        "checked": checked,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: list) -> int:
    """
    --description-stdin 모드: stdin 에서 description 읽기 → 프리픽스 형식 DETECT.
    stdout JSON. exit 0 ALWAYS (warning-tier, non-mutation).
    """
    # Bypass check
    if os.environ.get("BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE", "") == "1":
        print(json.dumps({"bypass": True, "description_prefix_conformant": True}))
        print(
            f"{SCRIPT_NAME} BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 — description-prefix detect suppressed",
            file=sys.stderr,
        )
        return 0

    if "--description-stdin" not in argv:
        print(
            f"{SCRIPT_NAME} ERROR: --description-stdin flag required. "
            "Usage: python3 check_spawn_description_prefix.py --description-stdin",
            file=sys.stderr,
        )
        # advisory detector — usage 오류도 exit 0 (spawn 무차단, warning-tier)
        print(json.dumps({"description_prefix_conformant": True, "empty": True, "checked": ""}))
        return 0

    # stdin 읽기 — graceful degradation: 실패 시 빈 문자열 (empty 처리 = conformant)
    try:
        description = sys.stdin.read()
    except Exception as e:
        print(
            f"{SCRIPT_NAME} WARN: stdin read error ({e}) — treating description as empty",
            file=sys.stderr,
        )
        description = ""

    result = check_description(description)

    # stdout JSON 출력 (hook wrapper 가 parse)
    print(json.dumps(result))

    # nonconformant (non-empty) 시 stderr warning 1줄 — 절대 exit 비-0 아님 (advisory)
    if not result["description_prefix_conformant"]:
        print(
            f"{SCRIPT_NAME} WARN: spawn description prefix nonconformant — "
            f"expected [<agent_type>] MM/DD HH:MM - <내용> (ADR-143, advisory)",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
