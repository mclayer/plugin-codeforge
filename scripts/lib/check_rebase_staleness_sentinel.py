"""
scripts/lib/check_rebase_staleness_sentinel.py
CFP-2784 / FU-1588-R — Rebase staleness sentinel SSOT (독립 재구현, stdlib-only)

기능:
  현재 브랜치가 origin/main 대비 몇 커밋 뒤처졌는지(commits-behind N)를 측정하고,
  N 을 tier(none/tier1/tier2)로 매핑해 advisory recommendation 문자열을 stdout JSON 으로 방출.
  본 sentinel 은 관측·추천만 수행하며 어떤 mutation 도 스스로 실행하지 않는다(INV-5 / AC-7).
  subprocess 는 fetch + rev-list 2종만 사용(원시 관측). advance/merge 류 mutation 호출 부재.

Mode enum (argparse --mode):
  head-compare (유일 유효 mode):
    Input:  optional --branch (default origin/main)
    Output: exit 0 + stdout JSON
      정상:   {"commits_behind": N, "recommended_tier": "<none|tier1|tier2>",
               "recommendation": "<text>", "observed_scope": "tier1/2 (tier3/4 = Orchestrator inline)"}
      degrade: {"commits_behind": null, "recommended_tier": "none",
               "degradation": "git_fetch_failed", "marker": "[rebase-staleness-sentinel-api-failed]",
               "stderr_excerpt": "<발췌>"}

Tier 매핑 (INV-1/2/3):
  N == 0            → "none"  (recommendation "" — zero-staleness, false-positive 0)
  1 <= N <= 2       → "tier1" (auto-merge 계열 advisory)
  N >= 3            → "tier2" (pre-emptive rebase 계열 advisory)
  recommended_tier ∈ {none, tier1, tier2} ONLY — tier3/tier4 방출 금지 (INV-3).

BYPASS:
  BYPASS_REBASE_STALENESS_SENTINEL=1 — unconditional skip, exit 0 + audit marker.

Exit-code 2-tier (로컬 계약):
  0: PASS 또는 honest-degrade (stdout JSON degradation 필드로 식별)
  2: SETUP error — git 미설치(FileNotFoundError handled → error_kind git_not_installed, Traceback 무노출)
  2 (argparse native): usage 오류 (무효 --mode 등) — stderr = argparse usage 텍스트

Test seam (test-only):
  REBASE_REVLIST_MOCK=<숫자>   — commits-behind N 주입 (실 git 우회)
  REBASE_GIT_MOCK_RC=<int>     — git returncode 주입 (degrade 경로 테스트, rc!=0 → degrade)
  REBASE_GIT_MOCK_STDERR=<str> — git stderr 주입 (degrade payload stderr_excerpt)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Optional, Tuple

# Windows cp949 stdout encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_rebase_staleness_sentinel"
BYPASS_ENV = "BYPASS_REBASE_STALENESS_SENTINEL"

# degradation 어휘 단일 선언 (sibling parity — DEGRADATION_LABELS 연속성).
#   git_fetch_failed 만 실배선(git-only core). 나머지 3은 gh enrichment 배선 시 활성 위한 선언만.
DEGRADATION_LABELS = ("api_quota_exceeded", "gh_command_failed", "gh_payload_invalid", "git_fetch_failed")
MARKER_API_FAILED = "[rebase-staleness-sentinel-api-failed]"

# Test seam env keys (self-test discriminating 계약 — 정확히 이 3종 노출)
REVLIST_MOCK_ENV = "REBASE_REVLIST_MOCK"        # commits-behind N 주입
GIT_MOCK_RC_ENV = "REBASE_GIT_MOCK_RC"          # git returncode 주입
GIT_MOCK_STDERR_ENV = "REBASE_GIT_MOCK_STDERR"  # git stderr 주입

# tier 경계 (magic number 하드코딩 회피 — named 상수, off-by-one mutation surface)
TIER1_MAX = 2  # 1 <= N <= TIER1_MAX → tier1, N >= TIER1_MAX+1 → tier2

# stderr 토큰 마스킹 정규식 (classic gh[pousr]_ / fine-grained github_pat_ prefix).
#   sibling parity + defense-in-depth (best-effort — 공식 prefix 형식 외 비정형 비밀 미커버).
_TOKEN_MASK_RE = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{36,})")


# ---------------------------------------------------------------------------
# Pure leaves
# ---------------------------------------------------------------------------
def _stderr_excerpt(stderr: str) -> str:
    """stderr 발췌 — 토큰 마스킹 선행 → cap 후행 (첫 8줄 ∧ 1024B 중 먼저 도달).

    마스킹→cap 순서: cap 선행 시 절단 경계 토큰 분할로 정규식 미포착 leak → 마스킹 선행이 구조적 봉인.
    """
    if not stderr:
        return ""
    masked = _TOKEN_MASK_RE.sub("[REDACTED]", stderr)
    capped = "\n".join(masked.splitlines()[:8])  # 첫 8줄
    encoded = capped.encode("utf-8")
    if len(encoded) > 1024:                       # 1024B cap (byte-safe decode)
        capped = encoded[:1024].decode("utf-8", errors="ignore")
    return capped


def _map_tier(n: int) -> Tuple[str, str]:
    """commits-behind N → (recommended_tier, recommendation). INV-1/2/3.

    출력 tier ∈ {none, tier1, tier2} ONLY (tier3/4 방출 금지). recommendation 은 서술 문자열일 뿐 —
    py 가 스스로 어떤 명령도 실행하지 않는다 (INV-5).
    """
    if n <= 0:
        return "none", ""
    if n <= TIER1_MAX:
        return "tier1", "auto-merge 추천 (--auto) — main advance 시 자동 rebase 반영"
    return "tier2", "pre-emptive rebase 추천 (fetch + rebase origin/main + force-push)"


# ---------------------------------------------------------------------------
# commit-count-behind 원시연산 (독립 구현 — parallel-work import 0)
# ---------------------------------------------------------------------------
def _get_commits_behind(branch: str = "origin/main") -> Tuple[Optional[int], Optional[str], str]:
    """commits-behind 측정 → (n, degrade, stderr_excerpt).

    성공: (N, None, "").  degrade: (None, "git_fetch_failed", <excerpt>).
    FileNotFoundError(git 미설치)는 catch 하지 않고 상위(main)로 전파 → exit 2 SETUP.
    """
    # 1. REBASE_REVLIST_MOCK — commits-behind N 직접 주입 (실 git 우회)
    revlist_mock = os.environ.get(REVLIST_MOCK_ENV)
    if revlist_mock is not None:
        try:
            return int(revlist_mock), None, ""
        except ValueError:
            return None, "git_fetch_failed", ""

    # 2. REBASE_GIT_MOCK_RC — git returncode 주입 (rc!=0 → degrade, rc==0 → 통과)
    rc_mock = os.environ.get(GIT_MOCK_RC_ENV)
    if rc_mock is not None:
        try:
            rc = int(rc_mock)
        except ValueError:
            rc = 0
        if rc != 0:
            stderr = os.environ.get(GIT_MOCK_STDERR_ENV, "")
            return None, "git_fetch_failed", _stderr_excerpt(stderr)
        # rc == 0 → 통과 (실 경로로 fall-through)

    # 3. 실 경로 — git fetch (best-effort, rc 무시) → git rev-list --count HEAD..<branch>
    #    FileNotFoundError 는 미catch → 상위 전파 (git 미설치 = exit 2 SETUP).
    subprocess.run(["git", "fetch", "origin"], capture_output=True)
    result = subprocess.run(
        ["git", "rev-list", "--count", f"HEAD..{branch}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return None, "git_fetch_failed", _stderr_excerpt(result.stderr)
    try:
        return int(result.stdout.strip()), None, ""
    except ValueError:
        return None, "git_fetch_failed", ""


# ---------------------------------------------------------------------------
# Emit helpers
# ---------------------------------------------------------------------------
def _exit_pass(payload: dict) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def _emit_degrade(label: str, stderr_excerpt: str) -> None:
    """honest-degrade — stderr 2줄(WARNING + MARKER) + stdout 계약 payload + exit 0."""
    print(
        f"[rebase-staleness-sentinel] WARNING: git rev-list --count failed — "
        f"commits-behind undetermined (degrade={label}).",
        file=sys.stderr,
    )
    print(MARKER_API_FAILED, file=sys.stderr)
    print(
        json.dumps({
            "commits_behind": None,
            "recommended_tier": "none",
            "degradation": label,
            "marker": MARKER_API_FAILED,
            "stderr_excerpt": stderr_excerpt,
        })
    )
    sys.exit(0)


def _exit_git_not_installed() -> None:
    """git 미설치 handled — Traceback 무노출, stderr JSON + exit 2 SETUP."""
    print(
        json.dumps({
            "error": "git not installed — install: https://git-scm.com",
            "error_kind": "git_not_installed",
            "exit_code": 2,
        }),
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (hotfix-bypass family, audit-trailed). argparse 선행.
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            json.dumps({
                "bypass": True,
                "marker": "[hotfix-bypass] BYPASS_REBASE_STALENESS_SENTINEL=1 invoked",
                "audit_comment": "bypass invoked",
            })
        )
        print("bypass invoked")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="CFP-2784 rebase staleness sentinel (FU-1588-R)",
        prog="check_rebase_staleness_sentinel",
    )
    parser.add_argument(
        "--mode",
        default="head-compare",
        choices=["head-compare"],
        help="Sentinel mode (단일 유효 mode: head-compare)",
    )
    parser.add_argument(
        "--branch",
        default="origin/main",
        help="Compare target branch (default: origin/main)",
    )

    args = parser.parse_args()

    try:
        n, degrade, stderr_excerpt = _get_commits_behind(branch=args.branch)
    except FileNotFoundError:
        _exit_git_not_installed()
        return  # unreachable (sys.exit) — 정적 명시

    if degrade:
        _emit_degrade(degrade, stderr_excerpt)
        return  # unreachable

    tier, recommendation = _map_tier(n if n is not None else 0)
    _exit_pass({
        "commits_behind": n,
        "recommended_tier": tier,
        "recommendation": recommendation,
        "observed_scope": "tier1/2 (tier3/4 = Orchestrator inline)",
    })


if __name__ == "__main__":
    main()
