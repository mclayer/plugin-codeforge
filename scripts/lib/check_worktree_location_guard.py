r"""
scripts/lib/check_worktree_location_guard.py
CFP-2822 — worktree 생성위치 PreToolUse(Bash) 가드 판정 SSOT (AC-10)

기능:
  PreToolUse(Bash) 훅에서 호출 — `git worktree add <path>` 의 target 이 표준
  관리 위치(`worktree_base()` 포트가 정의하는 `$HOME/.claude/worktrees/`) 밖이면
  worktree 가 workspace 루트·홈 직하·임의 경로에 흩어지는 것을 예방한다.
  2026-07-23~24 실측 정리에서 표준 밖 worktree 산개가 22GB 축적 근본원인의 하나였다.

  판정 SSOT 만 담당(this file). dispatch/hook 배선은 InfraEng 담당
  (`hooks/worktree-location-guard` polyglot + `scripts/check-worktree-location-guard.sh`
  8-line thin wrapper). 본 파일 = 위치 판정 로직.

책임 경계:
  - 책임: `git worktree add <path>` 의 target 이 표준 관리 루트 밖인지 판정 →
          tier(warn|block)에 따라 exit 0(경고) 또는 exit 2(차단).
  - 비책임: 그 외 명령(non-Bash / worktree add 아님)·경로 정리·삭제 = scope 외
          (통과). worktree 삭제/GC 는 별도 backstop(check-worktree-stale.sh) 소관.

worktree_base() 포트 소비 (Refactor D-2, 인라인 하드코딩 금지):
  표준 위치 문자열(`.claude/worktrees`)을 이 파일에 **인라인 복제하지 않는다**
  (5번째 카피 방지). 대신 `templates/scripts/worktree-path-util.sh` 의
  `worktree_base()` 포트를 subprocess 로 source 해 값을 얻고, 그 **부모**
  (managed root = `$HOME/.claude/worktrees`)를 표준 루트로 쓴다.
  부모를 쓰는 이유: 포트는 항상 `$HOME/.claude/worktrees/<repo>` 를 반환하므로
  그 dirname 은 repo·cwd(=worktree 안에서 실행)와 무관하게 항상 managed root →
  cwd 가 worktree 내부여도 견고. 목적 = "관리 루트 밖 산개" 예방(특정 repo
  subdir 여부는 위협 아님).

정직 경계 (§7.6 T-GUARD — over-claim 금지):
  본 가드는 **1차 예방(best-effort, fail-open)** 이다. matcher 회피(비-Bash
  경로: 네이티브 worktree 생성/IDE) + 명령 난독화(변수 간접/서브셸/base64)로
  **완전차단은 구조적으로 불가**. AC-10 "기계적 차단" ≠ 완전봉인. 놓친 표준 밖
  worktree 의 2차 검출 = ③ discovery 스캐너(AC-11)가 사후 가시화(예방⊕검출).
  파싱/판정 실패는 통과(fail-open) — false-negative 가 false-positive 보다 안전.

resource-safety (§7.6 T-REGEX honest-ceiling — ADR-168 §결정 16 (구 ADR-082 §결정 16, 재제정 CFP-2840)):
  경로/명령 파싱은 정규식이 아니라 `shlex` 토큰 분해 + 토큰 비교를 쓴다 →
  untrusted 입력에 대한 정규식 backtracking 표면을 두지 않는 설계(best-effort).
  "임의 입력 무해"를 단정하지 않는다 — bounded degradation 지향.

Bypass:
  BYPASS_WORKTREE_LOCATION_GUARD=1 — stderr audit 한 줄(UTC ISO) + exit 0.

tier:
  WORKTREE_LOCATION_GUARD_TIER=warn|block (default=warn).
    warn  — 표준 밖 → stderr 경고 + exit 0 (허용, 도입기).
    block — 표준 밖 → stderr 차단 안내 + exit 2 (승격기).

PreToolUse block contract (Claude Code):
  exit 2 + stderr = block (Claude 재시도 판단). exit 0 = allow.
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
import time

# Windows cp949 stdout/stderr encoding 차단 (ADR-061 standardize).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_NAME = "check_worktree_location_guard"
BYPASS_ENV = "BYPASS_WORKTREE_LOCATION_GUARD"
TIER_ENV = "WORKTREE_LOCATION_GUARD_TIER"

# `git worktree add` 에서 값을 뒤따라 소비하는 옵션(그 다음 토큰은 옵션 값이지 path 아님).
#   보수적으로 잘 확립된 것만 — 나머지 `--flag`/`-x` 는 값 없는 flag 로 취급.
#   오파싱 시 최악 = 가드 미발화(fail-open 안전 방향).
_VALUE_OPTS = {"-b", "-B", "--reason"}


def _norm(p):
    """경로 정규화 — normcase + normpath + realpath 3단 (repo-confinement `_norm()`
    동형, T-DEL-2 문자열 prefix 매칭 우회[case/8.3/UNC] 방지). 예외 시 realpath 생략."""
    try:
        return os.path.normcase(os.path.normpath(os.path.realpath(p)))
    except OSError:
        return os.path.normcase(os.path.normpath(p))


def _read_input():
    """stdin = PreToolUse JSON payload. dict 반환 (실패 시 빈 dict — fail-open).
    git-branch-delete-merge-gate.py `_read_input()` 관행 모방 (Refactor I-3)."""
    try:
        if sys.stdin.isatty():
            return {}
    except Exception:
        pass
    try:
        raw = sys.stdin.read(1 << 20)  # bounded ≤1 MiB
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw.strip())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def _resolve_port():
    """worktree-path-util.sh (worktree_base 포트 SSOT) 경로 해소. 부재 시 None."""
    here = os.path.dirname(os.path.abspath(__file__))
    # scripts/lib/ → repo_root/templates/scripts/worktree-path-util.sh
    cand = os.path.normpath(
        os.path.join(here, "..", "..", "templates", "scripts", "worktree-path-util.sh")
    )
    return cand if os.path.isfile(cand) else None


def _managed_root_via_port(cwd=None):
    """worktree_base() 포트를 source 해 관리 루트 도출 (Refactor D-2 SSOT 소비).

    bare-name `bash` 대신 `shutil.which("bash")` 절대경로로 실행 → Windows 에서 PATH 선두
      WSL bash(`execvpe(/bin/bash) failed`, rc=1) 오해소를 회피(F-CR-003 1차 원인).
    반환: 포트 출력의 부모(= `$HOME/.claude/worktrees`) 또는 None(포트/bash 불능)."""
    port = _resolve_port()
    if not port:
        return None
    bash_bin = shutil.which("bash")
    if not bash_bin:
        return None
    try:
        proc = subprocess.run(
            [bash_bin, "-c", 'source "$1"; worktree_base', "bash", port],
            cwd=(cwd or None),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    base = (proc.stdout or "").strip()
    if not base:
        return None
    # 포트는 항상 `$HOME/.claude/worktrees/<repo>` → 부모 = managed root (repo/cwd 불변).
    return os.path.dirname(base)


def _is_native_abs(p):
    """p 가 **현 플랫폼 네이티브 절대경로**인가 (MSYS POSIX 경로 배제).

    Windows: drive-letter(`C:`) 또는 UNC(`\\\\`) 여야 함. bash 포트가 반환하는 MSYS 경로
      (`/c/Users/...`)는 drive 부재(`os.path.splitdrive` → `('', ...)`) → False → 채택 배제
      (POSIX↔Windows `_norm` 불일치로 인한 false-positive 원천 차단, F-CR-003).
    POSIX: 절대경로면 네이티브."""
    if not p or not os.path.isabs(p):
        return False
    if os.name == "nt":
        drive, _ = os.path.splitdrive(p)
        return bool(drive)  # drive-letter/UNC 만 네이티브 (leading-slash MSYS 경로 배제)
    return True


def managed_root(cwd=None):
    """표준 관리 루트(`$HOME/.claude/worktrees`) — **항상 non-None**(가드 무발화 사각지대 제거).

    F-CR-003 fix (AC-10 hollow no-op 제거): 종전 구현은 bare `bash` subprocess 단독 의존 →
      Windows 에서 WSL bash 오해소(rc=1) → None → is_nonstandard_location 항상 False →
      block tier 조차 silent no-op(가드 미발화). 나아가 Git Bash 절대경로로 source 해도 포트가
      MSYS POSIX 경로(`/c/Users/...`)를 반환 → Windows `_norm` 이 `c:\\c\\Users\\...` 로
      오정규화 → 표준 target 을 nonstandard 로 오탐(false-positive). 두 모드 모두 결함.

    2단 도출:
      1차 — worktree_base() 포트 source(_managed_root_via_port, 절대경로 bash). 산출이
            **현 플랫폼 네이티브 절대경로 && 실재 디렉터리**면 채택. Windows 에서 포트가 뱉는
            MSYS 경로(`/c/...`)는 _is_native_abs 로 배제(isdir 만으로는 이 env 에서 `/c/...` 를
            통과시켜 false-positive 재현 — 실측). 포트가 유효한 플랫폼(Linux/macOS)에서는 SSOT 를
            계속 소비(Refactor D-2 유지).
      2차 fallback — 포트 불능/비-네이티브/부적합 → 결정론 파생. 포트 SSOT 불변식
            (`$HOME/.claude/worktrees/<repo>`)의 **부모** = `$HOME/.claude/worktrees`
            (본 파일 도입부 문서 · repo/cwd 불변)을 그대로 재현. `.claude/worktrees` 리터럴은
            이 fallback 1곳에만 존재하며(worktree_base() SSOT tail 미러 — 동기 유지 대상), 포트가
            유효한 플랫폼에서는 1차가 계속 SSOT 를 소비하므로 Refactor D-2 의도(SSOT 단일 소비)를
            포트-가용 플랫폼에서 보존한다."""
    root = _managed_root_via_port(cwd=cwd)
    if root and _is_native_abs(root) and os.path.isdir(root):
        return root
    # fallback — 결정론(silent no-op 제거). 포트 부모의 불변($HOME/.claude/worktrees) 재현.
    return os.path.join(os.path.expanduser("~"), ".claude", "worktrees")


def _parse_worktree_add_target(cmd):
    """cmd 에서 첫 `git worktree add <path>` 의 target path 를 추출. 없으면 None.
    shlex 토큰 분해(정규식 backtracking 표면 회피). 파싱 실패 → None (fail-open)."""
    try:
        tokens = shlex.split(cmd)
    except Exception:
        return None
    n = len(tokens)
    # `git worktree add` subcommand 위치 탐색 (env prefix / 경로형 git 허용).
    add_idx = -1
    for i in range(n - 2):
        tok = tokens[i]
        if (tok == "git" or tok.endswith("/git") or tok.endswith("\\git")) and (
            tokens[i + 1] == "worktree" and tokens[i + 2] == "add"
        ):
            add_idx = i + 2
            break
    if add_idx == -1:
        return None

    args = tokens[add_idx + 1 :]
    skip_next = False
    for tok in args:
        if skip_next:
            skip_next = False
            continue
        if tok in _VALUE_OPTS:
            skip_next = True  # 다음 토큰 = 옵션 값 (path 아님)
            continue
        if tok.startswith("-"):
            continue  # 값 없는 flag (--force/--detach/--checkout 등)
        return tok  # 첫 bare positional = <path>
    return None


def is_nonstandard_location(cmd, *, base=None, cwd=None):
    """`git worktree add <path>` 의 target 이 표준 관리 루트 밖이면 True.

    cmd 가 worktree add 가 아니거나 target 미파싱 → False(가드 무관).
    base 미주입 시 worktree_base() 포트에서 managed root 도출.
    base 도출 실패(포트/bash/repo 불능) → False (fail-open — §3.2① 파싱실패=통과).

    base: 테스트 주입용 표준 관리 루트(생략 시 포트 도출).
    cwd : 상대경로 target 해소 + 포트 실행 컨텍스트.
    """
    target = _parse_worktree_add_target(cmd)
    if not target:
        return False

    root = base if base is not None else managed_root(cwd=cwd)
    if not root:
        return False  # fail-open — 표준 루트 판정 불능 시 통과

    # target 절대화: 상대경로면 cwd 기준, `~` 확장.
    t = os.path.expanduser(target)
    if not os.path.isabs(t):
        t = os.path.join(cwd or os.getcwd(), t)

    nt = _norm(t)
    nr = _norm(root)
    if not nr:
        return False  # fail-open

    # 경로 경계 인지 containment (raw string prefix 금지 — normcase 후 sep 경계).
    #   nt == nr (루트 자체) 또는 nt 가 nr + sep 하위 → 표준(내부).
    if nt == nr or nt.startswith(nr + os.sep):
        return False  # 표준 위치 안 → 위반 아님
    return True  # 표준 관리 루트 밖 → 위반


def main():
    # 1. Bypass — audit trail 의무 (§3.6 T-ENV)
    if os.environ.get(BYPASS_ENV) == "1":
        audit_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(
            f"[{SCRIPT_NAME}] {BYPASS_ENV}=1 — worktree 위치 가드 suppressed at {audit_ts}",
            file=sys.stderr,
        )
        sys.exit(0)

    payload = _read_input()
    if not payload:
        sys.exit(0)  # fail-open

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command")
    if not cmd or not isinstance(cmd, str):
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()

    if not is_nonstandard_location(cmd, cwd=cwd):
        sys.exit(0)

    # 표준 밖 worktree 생성 감지 — tier 에 따라 warn / block.
    tier = (os.environ.get(TIER_ENV) or "warn").strip().lower()
    target = _parse_worktree_add_target(cmd) or "(target 미상)"

    if tier == "block":
        print(
            f"[{SCRIPT_NAME}] BLOCKED — 표준 관리 위치 밖 worktree 생성 차단 (CFP-2822 AC-10).\n"
            f"\n"
            f"target: {target}\n"
            f"사유: worktree 는 `$HOME/.claude/worktrees/<repo>/` 아래(관리 루트)에만\n"
            f"  생성해야 합니다. workspace 루트·홈 직하·임의 경로 산개는 GC 사각지대를\n"
            f"  만들어 잔재 축적의 근본원인이 됩니다(2026-07 실측).\n"
            f"\n"
            f"해소:\n"
            f"  - `codeforge:worktree-lifecycle` 규약대로 worktree-create.sh 경유 생성\n"
            f"    (표준 base 로 자동 배치).\n"
            f"  - 표준 base 아래 절대경로를 target 으로 명시.\n"
            f"\n"
            f"bypass (의도된 표준 밖 생성 확신 시): {BYPASS_ENV}=1 환경변수 설정.\n"
            f"한계(정직): 본 가드는 best-effort 예방 — 완전차단 아님(§7.6 T-GUARD).\n"
            f"참조: CFP-2822 worktree 위치 가드.",
            file=sys.stderr,
        )
        sys.exit(2)

    # warn tier (default) — 경고만, 통과.
    print(
        f"[{SCRIPT_NAME}] WARN — 표준 관리 위치 밖 worktree 생성 감지 (CFP-2822 AC-10, 도입기 warn).\n"
        f"  target: {target}\n"
        f"  worktree 는 `$HOME/.claude/worktrees/<repo>/` 아래에 두는 것을 권장합니다.\n"
        f"  (관리 루트 밖 산개 = GC 사각지대). {TIER_ENV}=block 승격 시 차단됩니다.\n"
        f"  bypass: {BYPASS_ENV}=1.",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
