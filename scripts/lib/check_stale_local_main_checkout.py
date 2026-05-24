"""
scripts/lib/check_stale_local_main_checkout.py
CFP-1410 Phase 2 / ADR-073 Amendment 7+9 — stale-local-main-checkout divergence check SSOT

기능:
  SessionStart 훅에서 호출 — 로컬 main 브랜치가 origin/main 대비 stale(diverged)한지 검사.
  divergence ≥ threshold 시 경고 메시지 + EnterWorktree guidance 출력 (advisory, non-blocking).
  feature branch (HEAD != main) 시 silent skip (EC-5: 정상 divergence 영역).
  offline graceful degradation: fetch fail → warning + exit 0 (non-blocking).

BYPASS:
  BYPASS_STALE_LOCAL_MAIN_CHECKOUT=1 — unconditional skip, exit 0 + audit marker

Exit-code 3-tier (ADR-060 §결정 15):
  0: PASS / skip / advisory warning (non-blocking)
  1: reserved (not used)
  2: SETUP error (Python dependency absent — 현재 stdlib only, 실사용 없음)

환경 변수:
  CODEFORGE_STALE_THRESHOLD        — divergence 판정 임계값 (default: 1)
  CODEFORGE_STALE_FETCH_TIMEOUT_SEC — git fetch timeout 초 (default: 10)
  BYPASS_STALE_LOCAL_MAIN_CHECKOUT  — bypass flag

Test seam:
  STALE_LOCAL_GIT_MOCK_REV_LIST=<숫자>    — git rev-list --count 결과 mock
  STALE_LOCAL_GIT_MOCK_BRANCH=<브랜치명>  — git rev-parse --abbrev-ref HEAD mock
  STALE_LOCAL_GIT_MOCK_FETCH_FAIL=1       — git fetch 실패 mock (graceful degradation 테스트)
"""

import os
import subprocess
import sys
import time
from typing import Optional

# Windows cp949 stdout encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_stale_local_main_checkout"
BYPASS_ENV = "BYPASS_STALE_LOCAL_MAIN_CHECKOUT"
DEFAULT_THRESHOLD = 1
DEFAULT_FETCH_TIMEOUT_SEC = 10

# Test seam env keys
MOCK_REV_LIST_ENV = "STALE_LOCAL_GIT_MOCK_REV_LIST"
MOCK_BRANCH_ENV = "STALE_LOCAL_GIT_MOCK_BRANCH"
MOCK_FETCH_FAIL_ENV = "STALE_LOCAL_GIT_MOCK_FETCH_FAIL"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_threshold() -> int:
    """CODEFORGE_STALE_THRESHOLD 환경 변수 (default 1)."""
    raw = os.environ.get("CODEFORGE_STALE_THRESHOLD", str(DEFAULT_THRESHOLD))
    try:
        val = int(raw)
        return val if val >= 1 else DEFAULT_THRESHOLD
    except ValueError:
        return DEFAULT_THRESHOLD


def _get_fetch_timeout() -> int:
    """CODEFORGE_STALE_FETCH_TIMEOUT_SEC 환경 변수 (default 10)."""
    raw = os.environ.get("CODEFORGE_STALE_FETCH_TIMEOUT_SEC", str(DEFAULT_FETCH_TIMEOUT_SEC))
    try:
        val = int(raw)
        return val if val >= 1 else DEFAULT_FETCH_TIMEOUT_SEC
    except ValueError:
        return DEFAULT_FETCH_TIMEOUT_SEC


def _get_current_branch() -> Optional[str]:
    """현재 HEAD 브랜치명 반환. Test seam: STALE_LOCAL_GIT_MOCK_BRANCH."""
    mock_val = os.environ.get(MOCK_BRANCH_ENV)
    if mock_val is not None:
        return mock_val

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _fetch_origin_main(timeout_sec: int) -> bool:
    """git fetch origin main 실행. 성공 시 True, 실패 시 False.
    Test seam: STALE_LOCAL_GIT_MOCK_FETCH_FAIL=1 → 즉시 False 반환."""
    if os.environ.get(MOCK_FETCH_FAIL_ENV) == "1":
        return False

    try:
        result = subprocess.run(
            ["git", "fetch", "origin", "main", "--quiet"],
            capture_output=True, text=True, timeout=timeout_sec,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _get_divergence_count() -> Optional[int]:
    """git rev-list --count HEAD..origin/main 결과. Test seam: STALE_LOCAL_GIT_MOCK_REV_LIST."""
    mock_val = os.environ.get(MOCK_REV_LIST_ENV)
    if mock_val is not None:
        try:
            return int(mock_val)
        except ValueError:
            return None

    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return None


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Bypass check
    if os.environ.get(BYPASS_ENV) == "1":
        audit_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(
            f"[{SCRIPT_NAME}] {BYPASS_ENV}=1 — divergence check skipped at {audit_ts}",
            file=sys.stderr,
        )
        sys.exit(0)

    threshold = _get_threshold()
    fetch_timeout = _get_fetch_timeout()

    # 2. EC-5: feature branch (HEAD != main) → silent skip
    current_branch = _get_current_branch()
    if current_branch is not None and current_branch != "main":
        # feature branch divergence = 정상 영역, silent skip
        sys.exit(0)

    # 3. git fetch origin main
    fetch_ok = _fetch_origin_main(fetch_timeout)
    if not fetch_ok:
        # offline graceful degradation: non-blocking warning
        print(
            f"[{SCRIPT_NAME}] WARNING: git fetch origin main failed "
            f"(offline or timeout={fetch_timeout}s) — divergence check skipped (advisory)",
            file=sys.stderr,
        )
        sys.exit(0)

    # 4. divergence count
    divergence = _get_divergence_count()
    if divergence is None:
        print(
            f"[{SCRIPT_NAME}] WARNING: could not determine divergence count — check skipped",
            file=sys.stderr,
        )
        sys.exit(0)

    # 5. threshold 비교
    if divergence >= threshold:
        print(
            f"[{SCRIPT_NAME}] WARNING: local main is {divergence} commit(s) behind origin/main "
            f"(threshold={threshold})."
        )
        print(
            f"[{SCRIPT_NAME}] Run `git -C <repo> fetch origin && git -C <repo> merge origin/main` "
            f"or use EnterWorktree (ADR-040) to work in a fresh worktree."
        )
        print(
            f"[{SCRIPT_NAME}] Evidence-checks-registry entry: "
            f"stale-local-main-checkout-divergence-check (ADR-073 Amendment 9)"
        )
        # advisory — non-blocking (warning tier)
        sys.exit(0)

    # silent PASS (divergence < threshold)
    sys.exit(0)


if __name__ == "__main__":
    main()
