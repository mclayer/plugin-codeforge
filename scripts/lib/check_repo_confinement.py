r"""
scripts/lib/check_repo_confinement.py
CFP-2092 — repo-confinement PreToolUse(Bash) 가드 SSOT

기능:
  PreToolUse(Bash) 훅에서 호출 — Bash 명령이 repo 밖(홈 루트 `~`)으로 스크래치
  산출물을 누출하는 패턴을 PreToolUse 단계에서 물리 차단 (exit 2).
  dogfood 세션에서 홈 루트에 plugin 클론·`.tmp-*`·story-payload.json 등이
  누출됐던 사고(CFP-2092) 재발 방지.

  차단 대상 2종:
    (1) explicit_home_write — 쓰기 맥락(redirect/clone/tee/cp/mv)의 타깃이
        명시적 홈 루트 경로(`~/<seg>`, `$HOME/<seg>`, `%USERPROFILE%\<seg>` 등).
        `~/.claude/...` 은 carve-out (정식 허용 경로).
    (2) cwd_home_creating — cwd 가 홈 루트인 상태에서 파일 생성 동사
        (git clone/tee/touch/mkdir/cp/mv 또는 출력 redirect) 실행.
        상대경로 출력이 홈으로 새는 사고 방지. `.claude` 언급 시 면제.

책임 경계:
  - 책임: 위 2종 패턴을 exit 2 로 차단 (silent home-root leak 방지).
  - 비책임: 읽기 명령(cat/ls/grep 등 — 생성 동사·redirect 없음)·repo 내부
    cwd 작업·`~/.claude/` 타깃 = 차단 안 함 (정상 영역, false-positive 회피).

Bypass:
  BYPASS_REPO_CONFINEMENT=1 — stderr audit 한 줄(UTC ISO) + exit 0.

Fail-open:
  stdin 비거나 JSON 파싱 실패 / 비-Bash tool / command 부재 → exit 0
  (guard 는 best-effort 1차 안전망 — false-negative 가 false-positive 보다 안전).

PreToolUse block contract (Claude Code):
  exit 2 + stderr = block (Claude 재시도 판단). exit 0 = allow.
"""

import json
import os
import re
import sys
import time

# Windows cp949 stdout/stderr encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_NAME = "check_repo_confinement"
BYPASS_ENV = "BYPASS_REPO_CONFINEMENT"

# repo 밖 임시 산출물 유일 허용 경로 (carve-out)
SCRATCH_HINT = "~/.claude/codeforge-scratch/"

# 파일 생성 동사 (단어 경계). redirect 는 별도 정규식으로 검출.
_CREATE_VERB_RE = re.compile(
    r"(?:^|[;&|]|\s)(?:git\s+clone|tee|touch|mkdir|cp|mv)(?:\s|$)"
)
# 출력 redirect `>` / `>>` — 단 `2>&1` 같은 fd-dup 은 제외.
_REDIRECT_RE = re.compile(r"(?<![0-9>])>>?(?!&)")

# 명시적 홈 루트 타깃: `~/<seg>` | `$HOME/<seg>` | `${HOME}/<seg>`
#   | `%USERPROFILE%\<seg>` | `$env:USERPROFILE\<seg>` 에서 첫 세그먼트 추출.
_HOME_TARGET_RE = re.compile(
    r"(?:~|\$HOME|\$\{HOME\}|%USERPROFILE%|\$env:USERPROFILE)[/\\]"
    r"([^\s/\\;&|>'\"]+)"
)

# 쓰기 맥락 prefix — 이 뒤에 오는 홈 타깃만 explicit_home_write 로 본다.
#   redirect(`>`/`>>`) | tee | cp | mv | git clone.
#   읽기 명령(cat/ls/grep)이 `~/foo` 를 인자로 받아도 차단하지 않기 위함.
_WRITE_CONTEXT_RE = re.compile(
    r"(?:(?<![0-9>])>>?(?!&)|(?:^|[;&|]|\s)(?:tee|cp|mv|git\s+clone)(?:\s|$))"
)


def _norm(p):
    """경로 정규화 — normcase + normpath + realpath (예외 시 realpath 생략)."""
    try:
        return os.path.normcase(os.path.normpath(os.path.realpath(p)))
    except OSError:
        return os.path.normcase(os.path.normpath(p))


def _read_payload():
    """stdin = PreToolUse JSON payload. 비거나 파싱 실패 시 None (fail-open)."""
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return None
    if not raw or not raw.strip():
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def _extract_home_write_target(cmd):
    """쓰기 맥락(redirect/tee/cp/mv/git clone) 뒤에 오는 명시적 홈 루트 타깃의
    첫 세그먼트 집합을 반환. `.claude` 세그먼트는 carve-out 으로 제외."""
    segs = []
    for m in _HOME_TARGET_RE.finditer(cmd):
        seg = m.group(1)
        if seg == ".claude":
            continue  # carve-out — `~/.claude/...` 정식 허용
        # 이 홈 타깃이 쓰기 맥락(앞쪽에 redirect/tee/cp/mv/git clone)에 있는지 확인.
        prefix = cmd[: m.start()]
        if _WRITE_CONTEXT_RE.search(prefix):
            segs.append(seg)
    return segs


def main():
    # 1. Bypass — audit trail 의무
    if os.environ.get(BYPASS_ENV) == "1":
        audit_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(
            f"[{SCRIPT_NAME}] {BYPASS_ENV}=1 — repo-confinement guard suppressed at {audit_ts}",
            file=sys.stderr,
        )
        sys.exit(0)

    payload = _read_payload()
    if payload is None:
        sys.exit(0)  # fail-open

    # 2. 비-Bash tool → 통과 (guard scope 외)
    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command")
    if not cmd:
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()
    home = os.path.expanduser("~")

    # 3. explicit_home_write — 쓰기 맥락의 명시적 홈 루트 타깃
    explicit_segs = _extract_home_write_target(cmd)
    explicit_home_write = len(explicit_segs) > 0

    # 4. cwd_home_creating — 홈 루트 cwd 에서 파일 생성 명령
    is_creating = bool(_CREATE_VERB_RE.search(cmd)) or bool(_REDIRECT_RE.search(cmd))
    cwd_is_home_root = _norm(cwd) == _norm(home)
    cwd_home_creating = cwd_is_home_root and is_creating and (".claude" not in cmd)

    blocked = explicit_home_write or cwd_home_creating
    if not blocked:
        sys.exit(0)

    if explicit_home_write:
        reason = "명시적 홈 루트 타깃 쓰기"
    else:
        reason = "홈 루트(cwd)에서 파일 생성 명령 실행"

    print(
        f"[{SCRIPT_NAME}] BLOCKED — repo 밖(홈 루트) 스크래치 누출 차단 (CFP-2092).\n"
        f"\n"
        f"사유: {reason}.\n"
        f"  dogfood 세션에서 홈 루트(~)에 plugin 클론·.tmp-*·story-payload.json 등이\n"
        f"  누출됐던 사고의 재발 방지 가드입니다.\n"
        f"\n"
        f"해소:\n"
        f"  - repo / worktree 로 cd 후 실행하거나, repo 내부 절대경로를 출력 타깃으로 명시.\n"
        f"  - repo 밖 임시 산출물이 꼭 필요하면 {SCRATCH_HINT} 아래에만 쓰세요\n"
        f"    (유일 허용 경로 — 가드 carve-out).\n"
        f"\n"
        f"bypass (의도된 홈 루트 쓰기 확신 시): {BYPASS_ENV}=1 환경변수 설정.\n"
        f"참조: CFP-2092 repo-confinement guard.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
