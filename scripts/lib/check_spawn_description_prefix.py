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
# Bypass (surface-specific — F5/CFP-2587 FIX-2): --inject 모드는 `--bypass-env <NAME>` 로 표면별
#   bypass env 를 수령(Agent=BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE / Bash=BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT;
#   disjoint — cross-surface bleed 없음). --description-stdin 모드는 아래 유지:
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

# ── --inject 모드 KST stamp 유효성 (CFP-2587 Phase 2) ─────────────────────────
#   컴팩트 `MM/DD HH:MM` 만 인정 (ADR-143 §결정 2/3). anchored·bounded (ReDoS-safe).
#   invalid stamp → build_injected_description 이 None 반환(KST-fail skip, degradation rung 4).
RE_KST_STAMP = re.compile(r'^\d{2}/\d{2} \d{2}:\d{2}$')

# _sanitize_subject '' fallback (G2)
UNKNOWN_AGENT = "unknown-agent"

# subject 최대 길이 (RE_PREFIX `[^\]]{1,64}` bound 정합)
SUBJECT_MAX_LEN = 64


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


# ── CFP-2587 Phase 2 — description INJECTION 순수 함수 (mechanical, non-mutation-caller) ──

def _sanitize_subject(raw: str) -> str:
    """
    subject(raw agent_type / subagent_type) 를 프리픽스 안전 토큰으로 정규화 (G2).

    규칙 (순서 고정):
      1. namespace strip: ':' 있으면 마지막 ':' 뒤만 (예: "codeforge-requirements:ResearcherAgent" → "ResearcherAgent")
      2. '[' , ']' 문자 전부 제거 (RE_PREFIX `[^\\]]` 파괴 방지)
      3. strip()
      4. ≤64 자 truncate (RE_PREFIX bound 정합)
      5. '' → "unknown-agent" fallback
    """
    if not isinstance(raw, str):
        raw = ""
    if ':' in raw:
        raw = raw.rsplit(':', 1)[-1]
    raw = raw.replace('[', '').replace(']', '')
    # ★ F6 (CFP-2587 FIX-2 / CFP-2599 P2-1): 개행·제어문자 → 공백. str.splitlines() 경계 전체
    #   (ASCII C0 개행 \n\v\f\r\x1c-\x1e + Unicode NL U+0085 NEL/U+2028 LS/U+2029 PS) 를 커버해
    #   단일 라인 라벨 보장 (splitlines 경계 과소 0). 클래스는 splitlines 경계가 아닌 C0 나머지 +
    #   DEL(0x7f) 도 접는 pre-existing 무해 superset (제어문자는 라벨 부적합 — 표시 위생상 바람직).
    raw = re.sub(r'[\x00-\x1f\x7f\x85\u2028\u2029]+', ' ', raw)
    raw = raw.strip()
    if len(raw) > SUBJECT_MAX_LEN:
        raw = raw[:SUBJECT_MAX_LEN]
    if raw == "":
        return UNKNOWN_AGENT
    return raw


def build_injected_description(subject: str, kst_stamp: str, original: str):
    """
    렌더-줄 프리픽스 주입 description 을 생성 — 실패/skip 조건이면 None 반환 (fail-open, non-emit).

    반환:
      str  — `[<sanitized>] <MM/DD HH:MM> - <내용>` (RE_PREFIX-conformant 보장)
      None — skip (updatedInput 미emit): 아래 5 조건 중 하나
        · original 이 공백/빈 문자열 (§7.7-1)
        · original 이 이미 프리픽스-conformant (idempotent, AC-11/AC-12 — check_description SSOT 재사용)
        · kst_stamp 형식 오류 (KST-fail skip, degradation rung 4)
        · 생성 문자열이 RE_PREFIX 미매칭 (안전망 — non-conformant 절대 emit 금지)
    """
    if not isinstance(original, str):
        return None
    # §7.7-1: 빈/공백 description 은 skip (leaf 빈 description 은 위반 아님)
    if original.strip() == "":
        return None
    # idempotent: 이미 conformant 면 재주입 금지 (check_description 단일 regex SSOT 재사용)
    # ★ F2 (CFP-2587 FIX-2): 판정 표면을 주입 표면(original.lstrip())과 일치 — leading-ws +
    #   이미 conformant original 이 가드 통과 후 double-stamp 되던 비대칭 봉합 (§11.6 f(f(x))=f(x)).
    res = check_description(original.lstrip())
    if res["description_prefix_conformant"] and not res["empty"]:
        return None
    # KST-fail skip: stamp 형식 오류 → None (rung 4 degradation)
    if not RE_KST_STAMP.match(kst_stamp or ""):
        return None
    sanitized = _sanitize_subject(subject)
    # lstrip 으로 `- ` 직후 `\\S` 보장 → RE_PREFIX-conformant
    content = original.lstrip()
    built = "[%s] %s - %s" % (sanitized, kst_stamp, content)
    # 안전망 post-check: RE_PREFIX 미매칭이면 절대 emit 안 함 (non-conformant 방지)
    if RE_PREFIX.match(built) is None:
        return None
    return built


# ── argv 파싱 (positional-safe single-pass 스캐너 — CFP-2599 P2-2) ─────────────
#   VALUE_FLAGS 는 바로 다음 토큰을 값으로 소비(그 값 토큰은 flag 로 재해석 안 함);
#   BOOL_FLAGS 는 flag-위치에서만 present 마킹. subject 값이 sibling flag 리터럴과
#   문자열이 같아도 값-위치로 소비돼 flag 오인 부재 — first-match value-shadow +
#   position-blind 멤버십 2 shadowing 클래스 동시 봉합. argparse 기각(flag-like 값에
#   sys.exit(2) → G5 exit-0-always 위반). scope = run_inject argv 파싱 한정 (main() dispatch
#   모드 selector 는 caller-고정 leading flag → subject 미도달, non-realizable — §7.2 F3).
VALUE_FLAGS = ("--subject", "--kst-stamp", "--bypass-env")
BOOL_FLAGS = ("--inject", "--transition-reminder", "--subject-absent", "--description-stdin")


def _scan_argv(argv: list):
    """argv 를 좌→우 1회 스캔 → (values dict, bools set). positional-safe.

    VALUE_FLAGS: 바로 다음 토큰을 값으로 소비(재해석 금지, first-match 우선 = argv.index 동형).
    BOOL_FLAGS: flag-위치에서만 present 마킹.
    값-위치 리터럴(예 subject 값 '--transition-reminder')이 flag 로 오인되지 않음.
    """
    values: dict = {}
    bools: set = set()
    i = 0
    n = len(argv)
    while i < n:
        tok = argv[i]
        if tok in VALUE_FLAGS:
            if i + 1 < n:
                if tok not in values:          # first-match 우선 (argv.index 동형)
                    values[tok] = argv[i + 1]
                i += 2                          # 값 토큰 소비 — flag 재해석 금지
            else:
                values.setdefault(tok, "")      # flag 가 argv 끝 → 값 '' (현행 보존)
                i += 1
        elif tok in BOOL_FLAGS:
            bools.add(tok)
            i += 1
        else:
            i += 1                              # 소비된 값 토큰 / 미지 positional → skip
    return values, bools


def _inject_arg_value(argv: list, flag: str) -> str:
    """argv 에서 flag 값 반환, 없으면 '' — positional-safe(_scan_argv SSOT 위임, CFP-2599).
    값-위치 리터럴이 flag 로 오인되지 않음(first-match value-shadow 봉합). VALUE_FLAGS 용."""
    return _scan_argv(argv)[0].get(flag, "")


def _load_build_context():
    """
    sibling 모듈 agent_spawn_transition_reminder._build_context 를 import (reminder SSOT 재사용).
    반환: callable | None (ImportError 등 실패 시 None → reminder skip, fail-open).
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from agent_spawn_transition_reminder import _build_context
        return _build_context
    except Exception:
        return None


def run_inject(argv: list) -> int:
    """
    --inject 모드: stdin=PreToolUse payload JSON → description 프리픽스 updatedInput 주입
    (+ --transition-reminder 시 additionalContext 병합). exit 0 ALWAYS (fail-open, G5).

    불변식:
      · G3 whole-echo: updatedInput = tool_input 전체 복사 + description 만 교체 (REPLACE-safe).
      · G4: permissionDecision 절대 미emit (bare updatedInput).
      · G1: 출력은 json.dumps (f-string/template JSON 금지).
      · §7.3 LOAD-BEARING: --transition-reminder 시 additionalContext 는 injected None 이어도 UNCONDITIONAL emit.
    """
    # ★ CFP-2599 (P2-2): positional-safe single-pass 스캐너 단일 SSOT — argv.index first-match +
    #   position-blind 멤버십(--transition-reminder / --subject-absent) 2 shadowing 클래스 봉합.
    values, bools = _scan_argv(argv)
    reminder_requested = "--transition-reminder" in bools
    # ★ F3 (CFP-2587 FIX-2): subject FIELD 부재 → injection SKIP (reminder 는 유지). 표면(hook)이
    #   자기 subject-source 키 presence 를 판정해 이 flag 로 전달 (Bash shell EXCLUDE 와 대칭).
    #   present-but-empty 는 flag 미전달 → build_injected_description 의 G2 unknown-agent fallback.
    subject_absent = "--subject-absent" in bools
    try:
        subject = values.get("--subject", "")
        kst_stamp = values.get("--kst-stamp", "")

        # ★ F5 (CFP-2587 FIX-2): surface-specific bypass env — 표면이 자기 env 이름 전달
        #   (Agent=BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE / Bash=BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT).
        #   default = Agent env (backward-compat). Agent bypass 가 Bash injection 을 억제하던 bleed 봉합.
        bypass_env = values.get("--bypass-env", "") or "BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE"
        # Bypass: updatedInput 주입 skip (no injection); reminder 는 여전히 emit.
        bypass = os.environ.get(bypass_env, "") == "1"

        injected = None
        tool_input = {}
        if not bypass and not subject_absent:
            try:
                raw = sys.stdin.read(1 << 20)  # bounded ≤1 MiB
            except Exception:
                raw = ""
            payload = json.loads(raw) if raw else {}
            if not isinstance(payload, dict):
                payload = {}
            tool_input = payload.get("tool_input", {})
            if not isinstance(tool_input, dict):
                tool_input = {}
            original = tool_input.get("description", "")
            injected = build_injected_description(subject, kst_stamp, original)

        hso = {"hookEventName": "PreToolUse"}
        if injected is not None:
            updated = dict(tool_input)         # G3 whole-echo of ENTIRE tool_input
            updated["description"] = injected
            hso["updatedInput"] = updated      # G4: NO permissionDecision

        if reminder_requested:
            ctx = _load_build_context()
            if ctx is not None:
                # §7.3 UNCONDITIONAL — injected None 이어도 reminder emit
                hso["additionalContext"] = ctx(subject)

        if "updatedInput" in hso or "additionalContext" in hso:
            print(json.dumps({"hookSpecificOutput": hso}, ensure_ascii=False))  # G1
        return 0
    except Exception:
        # fail-open — 어떤 예외도 tool block 안 함. reminder 요청 시 reminder-only emit.
        if reminder_requested:
            try:
                ctx = _load_build_context()
                if ctx is not None:
                    print(json.dumps({
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "additionalContext": ctx(values.get("--subject", "")),
                        }
                    }, ensure_ascii=False))
            except Exception:
                pass
        return 0


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: list) -> int:
    """
    --description-stdin 모드: stdin 에서 description 읽기 → 프리픽스 형식 DETECT.
    stdout JSON. exit 0 ALWAYS (warning-tier, non-mutation).

    --inject 모드 (CFP-2587 Phase 2): stdin=PreToolUse payload → updatedInput 주입 (run_inject).
    """
    # --inject 모드 우선 dispatch (자체 bypass·fail-open 규약 — run_inject 참조)
    if "--inject" in argv:
        return run_inject(argv)

    # Bypass check (--description-stdin 모드 전용)
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
