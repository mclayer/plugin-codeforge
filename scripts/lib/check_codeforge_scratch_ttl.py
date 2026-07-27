r"""
scripts/lib/check_codeforge_scratch_ttl.py
CFP-2822 — codeforge-scratch TTL purge SSOT (AC-5)

기능:
  `~/.claude/codeforge-scratch/` 내부에 쌓이는 **순수 loose 파일**(top-level
  regular file) 중 age > TTL 인 것만 자동 삭제한다. 2026-07 실측에서 codeforge-scratch
  가 TTL 로직 0 으로 431개/12.3GB 축적된 사각지대를 해소한다.
  dispatch(thin wrapper)·manifest 배선은 InfraEng 담당 — 본 파일 = purge 판정+집행 SSOT.

대상/비대상 (AC-5, INV-1 data-loss 가드):
  - 삭제 O: top-level **순수 loose 파일**, age>TTL, 아래 보호조건 전부 통과.
  - 삭제 X (`.git` 보유 디렉터리): clone/worktree/export 는 TTL 삭제 **제외** →
    AC-12 orphan 경로로 **회부**(회부 = 사유 기록/리포트, 삭제 절대 금지, INV-1 class 5).
  - 삭제 X (그 외 디렉터리): 진행 중 작업 산출물 가능 → KEEP(디렉터리는 ② 삭제 scope 밖,
    loose-file only). 광역 발견/분류는 ③ discovery(AC-8/12/15) 소관.
  - 삭제 X (상태/로그 self-exemption): `~/.claude/worktree-gc-state/` 는 codeforge-scratch
    **밖**이라 자연 제외. 기존 `worktree-stale-gc.log`(codeforge-scratch 안, session-end
    영속 로그)는 하위호환 위해 **명시 제외**.

age (TZ-safe, Windows/CI gotcha):
  age = now_epoch(time.time()) - mtime_epoch(st_mtime). 절대 epoch 뺄셈 —
  `date -d` 문자열 math 금지(Git Bash tzdata 부재 UTC gotcha 회피). DST 무관.
  mtime 은 age 신호이지만 **mtime 단독 삭제가 아니다**(§7.6 T-DEL-3): 삭제는
  age>TTL ∧ (아래 TB-3 보호 5종) 다중조건 통과 시에만. 용량임계/최근접근 정교화는
  ③(AC-15) 소관 — 본 파일은 loose-file TTL 축(honest ceiling).

TB-3 filesystem-direct 삭제 가드 (§7.1/§7.6 — git-mediated 아닌 직접 삭제 표면):
  현행 backstop 은 삭제를 git machinery 에 위임해 "표준 밖 실데이터 삭제 경로"가
  구조적으로 없었다. loose scratch 삭제는 filesystem-direct(os.remove) 라 그 면역이
  깨진다 → 아래 6종 강제:
    (1) realpath 재해소 후 표준 prefix(codeforge-scratch canonical) 재검증, 이탈=거부.
    (2) symlink/junction/reparse-point 제외(os.path.islink / lstat 비-regular = 거부).
    (3) normcase allowlist(canonical base) fail-closed — 판정 불능 시 삭제 안 함.
    (4) 빈 경로/비정상 이름(경로 구분자 포함) 가드.
    (5) `.git` 보유·`.git` 이름 오삭제 금지.
    (6) 정규 파일만(디렉터리·특수파일 삭제 금지).

Bypass:
  BYPASS_CODEFORGE_SCRATCH_TTL=1 — stderr audit 한 줄 + exit 0.

GC_DRY_RUN=1 — preview(실 삭제 0, would-purge 만 보고). 기존 GC preview flag 재사용.

Output contract (신규 네임스페이스 — 기존 output contract 무접촉, INV-5):
  stdout 마지막 줄: "[scratch-ttl] DONE: purged=N kept=M". exit always 0 (advisory).
"""

import os
import sys
import time

# Windows cp949 stdout/stderr encoding 차단 (ADR-061 standardize).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_NAME = "scratch-ttl"
BYPASS_ENV = "BYPASS_CODEFORGE_SCRATCH_TTL"

# codeforge-scratch 안에 있으나 TTL purge 명시 제외(하위호환 — session-end 영속 로그).
EXCLUDED_NAMES = {
    "worktree-stale-gc.log",
    ".git",  # 방어 — loose file 로 `.git` 이름이 와도 삭제 안 함.
}

# 기본 TTL(일) — env override 가능. 하드확정 아님(tunable, worktree STALE_DAYS=7 정합).
_DEFAULT_TTL_DAYS = 7


def _norm(p):
    """경로 정규화 — normcase + normpath + realpath 3단 (repo-confinement `_norm()`
    동형, T-DEL-2 case/8.3/UNC 우회 방지). 예외 시 realpath 생략."""
    try:
        return os.path.normcase(os.path.normpath(os.path.realpath(p)))
    except OSError:
        return os.path.normcase(os.path.normpath(p))


def _scratch_root():
    """codeforge-scratch 루트 경로(존재 여부 무관)."""
    return os.path.join(os.path.expanduser("~"), ".claude", "codeforge-scratch")


def _ttl_seconds():
    """TTL(초) — env CODEFORGE_SCRATCH_TTL_DAYS override, 기본 7일."""
    raw = os.environ.get("CODEFORGE_SCRATCH_TTL_DAYS")
    days = _DEFAULT_TTL_DAYS
    if raw:
        try:
            days = float(raw)
        except (TypeError, ValueError):
            days = _DEFAULT_TTL_DAYS
    if days < 0:
        days = _DEFAULT_TTL_DAYS
    return days * 86400.0


def _has_git(dir_path):
    """디렉터리가 `.git`(파일=worktree/디렉터리=repo) 을 보유하는지 — clone/worktree/export 판별."""
    return os.path.exists(os.path.join(dir_path, ".git"))


def _safe_to_purge(full, name, canonical_root, now, ttl_secs):
    """loose 파일 삭제 안전성 종합 판정 (TB-3 6종 + age). True 면 삭제 후보.

    반환 False 사유는 상위가 KEEP 처리(사유 미분류 = 보수적 보존, INV-1)."""
    # (4) 빈 경로/비정상 이름 가드.
    if not name or not full:
        return False
    if os.sep in name or (os.altsep and os.altsep in name):
        return False
    # (5) 명시 제외(.git / 상태로그).
    if name in EXCLUDED_NAMES:
        return False
    # (2) symlink/junction/reparse-point 제외 + (6) 정규 파일만.
    #   os.path.islink → symlink/일부 reparse-point 검출. lstat 로 실체 확인(follow 금지).
    try:
        if os.path.islink(full):
            return False
        st = os.lstat(full)  # follow 안 함 — symlink 타깃 접근 금지.
    except OSError:
        return False
    import stat as _stat

    if not _stat.S_ISREG(st.st_mode):
        return False  # 디렉터리·특수파일 = 삭제 scope 밖.
    # age = now - mtime (절대 epoch, TZ-safe). age<=TTL → 아직 어리다 = KEEP.
    age = now - st.st_mtime
    if age <= ttl_secs:
        return False
    # (1)(3) realpath 재해소 후 canonical base 재검증 fail-closed.
    cf = _norm(full)
    if not cf or not canonical_root:
        return False  # 판정 불능 = 삭제 안 함(fail-closed).
    if not (cf == canonical_root or cf.startswith(canonical_root + os.sep)):
        return False  # 표준 prefix 이탈(링크 미해소 잔여 등) = 거부.
    return True


def run():
    root = _scratch_root()
    canonical_root = _norm(root)
    now = time.time()
    ttl_secs = _ttl_seconds()
    dry_run = os.environ.get("GC_DRY_RUN") == "1"

    purged = 0
    kept = 0
    would = 0

    try:
        entries = os.listdir(root)
    except OSError:
        # 루트 부재/접근 불가 → 대상 없음.
        print(f"[{SCRIPT_NAME}] DONE: purged=0 kept=0")
        return

    for name in sorted(entries):
        full = os.path.join(root, name)

        # 디렉터리 처리: `.git` 보유 → orphan 회부(삭제 금지), 그 외 → KEEP.
        try:
            is_dir = os.path.isdir(full) and not os.path.islink(full)
        except OSError:
            is_dir = False
        if is_dir:
            kept += 1
            if _has_git(full):
                print(
                    f"[{SCRIPT_NAME}] REFER-ORPHAN (.git 보유 — AC-12 orphan 회부, 삭제 안 함): {full}",
                    file=sys.stderr,
                )
            continue

        # loose 파일 — 삭제 안전성 종합 판정.
        if not _safe_to_purge(full, name, canonical_root, now, ttl_secs):
            kept += 1
            continue

        if dry_run:
            print(f"[{SCRIPT_NAME}] DRY_RUN would-purge (age>TTL): {full}")
            would += 1
            kept += 1  # 실제로 안 지웠으므로 kept 로 집계(purged 는 실 삭제만).
            continue

        try:
            os.remove(full)
            print(f"[{SCRIPT_NAME}] PURGED (age>TTL loose file): {full}")
            purged += 1
        except OSError as exc:
            print(
                f"[{SCRIPT_NAME}] WARN: remove 실패 (skip, 보존): {full} ({exc})",
                file=sys.stderr,
            )
            kept += 1

    if dry_run:
        print(f"[{SCRIPT_NAME}] DRY_RUN: would_purge={would} (no removal)", file=sys.stderr)
    print(f"[{SCRIPT_NAME}] DONE: purged={purged} kept={kept}")


def _print_help():
    """--help/-h 시 사용법만 stdout 출력하고 실 스캔(파괴적 purge)은 미실행.

    GAP3 fix: argparse 미도입 조기 가드 — 이 모듈의 advisory fail-open 불변식('어떤 실패도
    exit 0 + DONE')을 지키기 위해 argparse 의 unknown-arg exit(2) 회피. 정상(무인자) 실행의
    '[scratch-ttl] DONE: purged=N kept=M' 출력 계약은 무손상(--help 만 조기 분기)."""
    print(
        "usage: check_codeforge_scratch_ttl.py [-h | --help]\n"
        "\n"
        "codeforge-scratch TTL purge (CFP-2822 AC-5) — ~/.claude/codeforge-scratch/ 내부\n"
        "top-level loose 파일 중 age>TTL 인 것만 자동 삭제한다. `.git` 보유 디렉터리(clone/\n"
        "worktree/export)와 상태로그(worktree-stale-gc.log)는 삭제 제외.\n"
        "\n"
        "options:\n"
        "  -h, --help    이 도움말을 출력하고 종료(실 스캔·삭제 미실행).\n"
        "\n"
        "env:\n"
        "  CODEFORGE_SCRATCH_TTL_DAYS      TTL(일), 기본 7.\n"
        "  GC_DRY_RUN=1                    preview(실 삭제 0, would-purge 만 보고).\n"
        "  BYPASS_CODEFORGE_SCRATCH_TTL=1  스캔 전면 skip + stderr audit + exit 0.\n"
        "\n"
        "output contract: 마지막 줄 '[scratch-ttl] DONE: purged=N kept=M', exit always 0."
    )


def main():
    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        # help 는 실 스캔 전에 조기 분기 — 파괴적 purge 미실행. (DONE 계약은 실 스캔 전용.)
        _print_help()
        sys.exit(0)

    if os.environ.get(BYPASS_ENV) == "1":
        audit_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(
            f"[{SCRIPT_NAME}] {BYPASS_ENV}=1 — scratch TTL purge suppressed at {audit_ts}",
            file=sys.stderr,
        )
        # bypass 시에도 output contract 유지(downstream 안정).
        print(f"[{SCRIPT_NAME}] DONE: purged=0 kept=0")
        sys.exit(0)

    try:
        run()
    except Exception as exc:  # noqa: BLE001 — advisory, 어떤 실패도 exit 0 + DONE 보장.
        print(f"[{SCRIPT_NAME}] WARN: 예외 (fail-safe, 보존): {exc}", file=sys.stderr)
        print(f"[{SCRIPT_NAME}] DONE: purged=0 kept=0")
    sys.exit(0)


if __name__ == "__main__":
    main()
