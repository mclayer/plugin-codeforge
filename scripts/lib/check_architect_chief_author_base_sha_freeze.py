"""
scripts/lib/check_architect_chief_author_base_sha_freeze.py
CFP-1581 / ADR-073 Amendment 16 — ArchitectAgent chief author base SHA freeze verify SSOT

기능:
  ArchitectAgent (chief author) spawn 시점 base SHA freeze pattern 검증
  ADR-073 §결정 1-Q 4-step verify-before-assert primitive 구현:
    1. git fetch origin (cross-repo state freshness)
    2. git diff origin/main..HEAD --stat (base drift detection)
    3. drift 감지 시 mechanical rebase 권장 message (실 rebase 는 author decision)
    4. expected diff narrowed verify (PR scope 정합)

Lint 2-mode (artifact verification):
  Mode A (spawn-prompt-grep):
    Story file §14 Lane Evidence section 에서 ArchitectAgent chief author spawn marker 검출 시
    ±20 line window 안 [PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>] block presence-grep 검증.
  Mode B (lane-evidence-marker-grep):
    Story file §14 Lane Evidence 테이블 row 안 base_sha_pinned field 검증.

Exit code 3-tier (ADR-060 §결정 15):
  0: PASS
  1: WARNING (base SHA pin absent / drift detected)
  2: ENVIRONMENT_ERROR (dependency absent / auth failed)

BYPASS:
  BYPASS_ARCHITECT_CHIEF_AUTHOR_BASE_SHA_FREEZE=1 — unconditional skip, exit 0 + audit marker

ADR-061 Amd 3 §결정 11 CodeQL ReDoS guard:
  - PER_LANE_EVIDENCE_SCAN_CAP = 30 line
  - anchored simple single-line regex 의무
  - line-by-line scan 의무
  - nested quantifier regex 절대 금지

CFP-1500 precedent (check_parallel_work_sentinel.py) byte-pattern 답습:
  - Windows cp949 stdout encoding 차단
  - argparse 구조
  - 3-tier graceful degradation
  - Exit helper pattern

Graceful degradation 3 fail-mode:
  401_fail_closed:    git CLI 미인증 / 환경 오류 → exit 2 SETUP error (fail-closed semantic)
  429_fail_open:      rate-limit 등 transient error → exit 0 + warning marker
  5xx_noop:           네트워크 오류 → exit 0 + advisory stderr marker

Test seam:
  CFP1581_GIT_FETCH_MOCK=1           — git fetch mock (no-op)
  CFP1581_GIT_DIFF_MOCK=<file>        — git diff --stat mock (file contents)
  CFP1581_STORY_FILE_MOCK=<file>      — Story file mock (file path)
"""

import argparse
import os
import re
import subprocess
import sys
from typing import Optional

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants (ADR-061 Amd 3 §결정 11 CodeQL ReDoS guard)
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_architect_chief_author_base_sha_freeze"
BYPASS_ENV = "BYPASS_ARCHITECT_CHIEF_AUTHOR_BASE_SHA_FREEZE"
GIT_FETCH_MOCK_ENV = "CFP1581_GIT_FETCH_MOCK"
GIT_DIFF_MOCK_ENV = "CFP1581_GIT_DIFF_MOCK"
STORY_FILE_MOCK_ENV = "CFP1581_STORY_FILE_MOCK"

# PER_LANE_EVIDENCE_SCAN_CAP: ReDoS guard — line-by-line scan 최대 라인 수
PER_LANE_EVIDENCE_SCAN_CAP = 30

# SHA hex pattern: anchored simple regex (no nested quantifier — ReDoS guard)
SHA_HEX_PATTERN = re.compile(r"^[0-9a-f]{40}$")

# PRE-SPAWN marker line pattern: anchored, single-line scan
# Matches: [PRE-SPAWN-ORIGIN-MAIN-SHA: <40-hex>]
PRE_SPAWN_SHA_LINE_PATTERN = re.compile(
    r"^\[PRE-SPAWN-ORIGIN-MAIN-SHA:\s*([0-9a-f]{40})\]"
)

# §14 Lane Evidence base_sha_pinned field pattern (simple anchored)
BASE_SHA_PINNED_LINE_PATTERN = re.compile(
    r"^\|\s*base_sha_pinned\s*\|"
)

# ArchitectAgent chief author spawn marker in §14 table (simple anchored)
# Matches lines like: | 설계 | ... | ArchitectAgent ...
ARCH_AGENT_SPAWN_LINE_PATTERN = re.compile(
    r"ArchitectAgent\s*\(chief\s*author\)"
)


# ---------------------------------------------------------------------------
# Exit helpers
# ---------------------------------------------------------------------------
def _exit_pass(msg: str) -> None:
    print(f"[architect-chief-author-base-sha-freeze] PASS: {msg}")
    sys.exit(0)


def _exit_warning(msg: str) -> None:
    print(f"[architect-chief-author-base-sha-freeze] WARNING: {msg}", file=sys.stderr)
    print(f"[architect-chief-author-base-sha-freeze] WARNING: {msg}")
    sys.exit(1)


def _exit_setup_error(msg: str) -> None:
    print(
        f"[architect-chief-author-base-sha-freeze] ENVIRONMENT_ERROR: {msg}",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# git invocation helpers
# ---------------------------------------------------------------------------
def _run_git_fetch(worktree_path: Optional[str] = None) -> tuple[int, str]:
    """Run git fetch origin. Returns (rc, stderr)."""
    if os.environ.get(GIT_FETCH_MOCK_ENV) == "1":
        return 0, ""
    cmd = ["git"]
    if worktree_path:
        cmd += ["-C", worktree_path]
    cmd += ["fetch", "origin"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stderr


def _run_git_diff_stat(worktree_path: Optional[str] = None) -> tuple[int, str]:
    """Run git diff origin/main..HEAD --stat. Returns (rc, stdout)."""
    mock_path = os.environ.get(GIT_DIFF_MOCK_ENV)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                return 0, f.read()
        except FileNotFoundError:
            return 2, f"mock file not found: {mock_path}"
    cmd = ["git"]
    if worktree_path:
        cmd += ["-C", worktree_path]
    cmd += ["diff", "origin/main..HEAD", "--stat"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout


def _run_git_rev_parse_origin_main(worktree_path: Optional[str] = None) -> tuple[int, str]:
    """Run git rev-parse origin/main. Returns (rc, sha_line)."""
    cmd = ["git"]
    if worktree_path:
        cmd += ["-C", worktree_path]
    cmd += ["rev-parse", "origin/main"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout.strip()


# ---------------------------------------------------------------------------
# Step 1-4: ADR-073 §결정 1-Q 4-step verify-before-assert primitive
# ---------------------------------------------------------------------------
def run_4step_verify(
    worktree_path: Optional[str],
    expected_files: Optional[list[str]],
) -> None:
    """
    ADR-073 §결정 1-Q 4-step verify-before-assert primitive.

    Step 1: git fetch origin (cross-repo state freshness)
    Step 2: git diff origin/main..HEAD --stat (base drift detection)
    Step 3: drift 감지 시 mechanical rebase 권장 message
    Step 4: expected diff narrowed verify (PR scope 정합)
    """

    # Step 1: git fetch origin
    rc_fetch, stderr_fetch = _run_git_fetch(worktree_path)
    if rc_fetch != 0:
        # fail-open: git fetch 실패 = transient network issue → warning + continue
        print(
            f"[architect-chief-author-base-sha-freeze] WARNING: git fetch origin failed "
            f"(rc={rc_fetch}): {stderr_fetch.strip()} — continuing with local state",
            file=sys.stderr,
        )

    # Step 2: git diff origin/main..HEAD --stat
    rc_diff, diff_stat = _run_git_diff_stat(worktree_path)
    if rc_diff != 0:
        # ENVIRONMENT_ERROR: cannot determine drift
        _exit_setup_error(
            f"git diff origin/main..HEAD --stat failed (rc={rc_diff}) — "
            "ensure worktree is valid and origin/main is reachable"
        )

    diff_lines = diff_stat.strip().splitlines() if diff_stat.strip() else []

    # Drift detection: check if origin/main HEAD is ancestor of worktree HEAD
    # Simple heuristic: if diff_stat summary line contains "changed" with insertions/deletions
    # AND the stat contains files not in expected_files → drift may exist
    # For CFP-1581 scope: drift = origin/main has advanced beyond worktree base
    # We check via git rev-parse origin/main vs worktree merge-base
    rc_sha, current_origin_sha = _run_git_rev_parse_origin_main(worktree_path)
    if rc_sha != 0:
        # Advisory only — cannot verify origin/main SHA
        print(
            "[architect-chief-author-base-sha-freeze] ADVISORY: "
            "Cannot determine origin/main SHA — skip drift check",
            file=sys.stderr,
        )
        current_origin_sha = ""

    # Validate SHA format (anchored simple regex — ReDoS guard)
    if current_origin_sha and not SHA_HEX_PATTERN.match(current_origin_sha):
        current_origin_sha = ""  # invalid format — skip

    # Step 3: drift detection via merge-base comparison
    drift_detected = _check_merge_base_drift(worktree_path, current_origin_sha)

    if drift_detected:
        # Step 3: mechanical rebase 권장 message
        print(
            "[architect-chief-author-base-sha-freeze] WARNING: "
            "base drift detected — origin/main has advanced since worktree branch point.",
            file=sys.stderr,
        )
        print(
            "[architect-chief-author-base-sha-freeze] RECOMMENDATION: "
            f"git -C {worktree_path or '.'} rebase origin/main "
            "(if no semantic conflict, mechanical rebase safe). "
            "Actual rebase decision = author responsibility.",
            file=sys.stderr,
        )

    # Step 4: expected diff narrowed verify
    if expected_files:
        unexpected = _check_unexpected_diff_files(diff_lines, expected_files)
        if unexpected:
            _exit_warning(
                f"unexpected files in diff (PR scope drift): {unexpected}. "
                "Expected: " + ", ".join(expected_files)
            )

    if drift_detected:
        _exit_warning(
            "base drift detected — run: git rebase origin/main (mechanical, if no semantic conflict)"
        )

    _exit_pass(
        f"base SHA freeze verify OK"
        + (f" — origin/main SHA: {current_origin_sha[:12]}..." if current_origin_sha else "")
    )


def _check_merge_base_drift(
    worktree_path: Optional[str],
    origin_main_sha: str,
) -> bool:
    """
    Check if worktree HEAD is based on a stale origin/main.
    Returns True if drift detected (origin/main has advanced beyond branch point).
    """
    if not origin_main_sha:
        return False

    # Get merge-base of HEAD and origin/main
    cmd = ["git"]
    if worktree_path:
        cmd += ["-C", worktree_path]
    cmd += ["merge-base", "HEAD", "origin/main"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return False  # advisory — cannot determine

    merge_base_sha = result.stdout.strip()
    if not merge_base_sha:
        return False

    # Drift detected if merge_base != origin/main
    # (i.e., origin/main has commits beyond the branch point)
    return merge_base_sha != origin_main_sha


def _check_unexpected_diff_files(diff_lines: list[str], expected_files: list[str]) -> list[str]:
    """
    Parse diff --stat output and check for files not in expected_files list.
    Returns list of unexpected file paths found in diff.
    ADR-061 Amd 3 ReDoS guard: simple split-based parse, no regex quantifier nesting.
    """
    unexpected = []
    for line in diff_lines:
        line = line.strip()
        if not line or line.startswith("---") or line.startswith("+++"):
            continue
        # git diff --stat format: " path/to/file | N +++---"
        # or summary: " N files changed, M insertions(+), K deletions(-)"
        if "|" in line:
            # simple split at first | — no regex (ReDoS guard)
            parts = line.split("|", 1)
            file_path = parts[0].strip()
            if file_path and file_path not in expected_files:
                # Check if any expected_file matches as prefix/suffix
                matched = any(
                    ef in file_path or file_path in ef
                    for ef in expected_files
                )
                if not matched:
                    unexpected.append(file_path)
    return unexpected


# ---------------------------------------------------------------------------
# Mode B: Story file lint (spawn-prompt-grep + lane-evidence-marker-grep)
# ---------------------------------------------------------------------------
def run_story_lint(story_file: str) -> None:
    """
    Lint Story file §14 Lane Evidence for ArchitectAgent chief author base SHA pin.

    Lint 2-mode:
      Mode A (spawn-prompt-grep): §14 ArchitectAgent spawn marker ±20 line window
                                   [PRE-SPAWN-ORIGIN-MAIN-SHA: <40-hex>] presence-grep
      Mode B (lane-evidence-marker-grep): §14 base_sha_pinned field presence

    ADR-061 Amd 3 §결정 11 CodeQL ReDoS guard:
      - PER_LANE_EVIDENCE_SCAN_CAP=30 line window
      - simple anchored regex (PRE_SPAWN_SHA_LINE_PATTERN / BASE_SHA_PINNED_LINE_PATTERN)
      - line-by-line scan 의무

    FP guard 4종:
      1. templates/** canonical example 면제
      2. tests/** bats fixture 면제
      3. docs/stories/ path-only scope (Story file 아닌 모든 file = silent skip)
      4. marker 부재 silent skip (§14 섹션 없음 = not an error)
    """
    # Resolve mock path
    mock_path = os.environ.get(STORY_FILE_MOCK_ENV)
    actual_path = mock_path if mock_path else story_file

    # FP guard 1-3: scope guard 는 story_file 인수(--story-file) 경로 기준
    # (CFP1581_STORY_FILE_MOCK 은 file read 대상만 override — scope 판정 무관)
    scope_path = story_file.replace("\\", "/")
    normalized = scope_path  # alias for clarity

    # FP guard 1: templates/** canonical example 면제
    if "/templates/" in normalized or normalized.startswith("templates/"):
        _exit_pass("templates/** path — FP guard skip (canonical example)")
    # FP guard 2: tests/** bats fixture 면제
    if "/tests/" in normalized or normalized.startswith("tests/"):
        _exit_pass("tests/** path — FP guard skip (bats fixture)")
    # FP guard 3: docs/stories/ path-only scope
    if "/docs/stories/" not in normalized and not normalized.startswith("docs/stories/"):
        _exit_pass("not a Story file path — silent skip (lint scope: docs/stories/ only)")

    try:
        with open(actual_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except FileNotFoundError:
        _exit_setup_error(f"Story file not found: {actual_path}")
    except PermissionError:
        _exit_setup_error(f"Story file permission denied: {actual_path}")

    # Find §14 Lane Evidence section start
    section14_start = _find_section14_start(lines)
    if section14_start < 0:
        # FP guard 4: §14 absent = silent skip
        _exit_pass("§14 Lane Evidence section absent — silent skip")

    # Mode A: spawn-prompt-grep — find ArchitectAgent chief author spawn marker
    arch_spawn_line_idx = _find_arch_spawn_marker(lines, section14_start)

    if arch_spawn_line_idx < 0:
        # No ArchitectAgent chief author spawn marker — not applicable
        _exit_pass("ArchitectAgent (chief author) spawn marker not found in §14 — not applicable")

    # Mode A: check ±20 line window for [PRE-SPAWN-ORIGIN-MAIN-SHA: <40-hex>]
    window_start = max(0, arch_spawn_line_idx - 20)
    window_end = min(len(lines), arch_spawn_line_idx + 20)
    window_lines = lines[window_start:window_end]

    pre_spawn_sha_found = _scan_for_pre_spawn_sha(window_lines)

    # Mode B: check base_sha_pinned field in §14 section
    base_sha_pinned_found = _scan_for_base_sha_pinned(
        lines, section14_start, PER_LANE_EVIDENCE_SCAN_CAP
    )

    if not pre_spawn_sha_found and not base_sha_pinned_found:
        _exit_warning(
            f"ArchitectAgent (chief author) spawn marker found at line {arch_spawn_line_idx + 1}, "
            "but [PRE-SPAWN-ORIGIN-MAIN-SHA: <40-hex>] absent in ±20 line window "
            "AND base_sha_pinned field absent in §14 Lane Evidence "
            f"(scan cap: {PER_LANE_EVIDENCE_SCAN_CAP} lines)"
        )

    sha_info = ""
    if pre_spawn_sha_found:
        sha_info += f" [PRE-SPAWN-ORIGIN-MAIN-SHA found]"
    if base_sha_pinned_found:
        sha_info += f" [base_sha_pinned found]"

    _exit_pass(f"§14 ArchitectAgent chief author base SHA pin verified{sha_info}")


def _find_section14_start(lines: list[str]) -> int:
    """Find §14 Lane Evidence section start line index. Returns -1 if not found."""
    for idx, line in enumerate(lines):
        stripped = line.strip()
        # Simple prefix match — no regex (ReDoS guard)
        if stripped.startswith("## §14") or stripped.startswith("## 14.") or "Lane Evidence" in stripped:
            return idx
    return -1


def _find_arch_spawn_marker(lines: list[str], start_idx: int) -> int:
    """
    Find ArchitectAgent (chief author) spawn marker in lines from start_idx.
    Returns index of first matching line, or -1.
    ADR-061 Amd 3 ReDoS guard: simple compiled regex, no nested quantifier.
    """
    for idx in range(start_idx, len(lines)):
        if ARCH_AGENT_SPAWN_LINE_PATTERN.search(lines[idx]):
            return idx
    return -1


def _scan_for_pre_spawn_sha(window_lines: list[str]) -> bool:
    """
    Scan window_lines (≤40 lines, ±20 window) for [PRE-SPAWN-ORIGIN-MAIN-SHA: <40-hex>].
    ADR-061 Amd 3 ReDoS guard:
      - line-by-line scan
      - anchored simple regex PRE_SPAWN_SHA_LINE_PATTERN
      - no per-line cap needed (window is already ≤40 lines)
    """
    for line in window_lines:
        stripped = line.strip()
        if PRE_SPAWN_SHA_LINE_PATTERN.match(stripped):
            return True
    return False


def _scan_for_base_sha_pinned(
    lines: list[str], start_idx: int, cap: int
) -> bool:
    """
    Scan §14 section for base_sha_pinned field (up to cap lines from start_idx).
    ADR-061 Amd 3 ReDoS guard:
      - line-by-line scan
      - per-entry scan cap = cap lines
      - anchored simple regex BASE_SHA_PINNED_LINE_PATTERN
    """
    scanned = 0
    for idx in range(start_idx, len(lines)):
        if scanned >= cap:
            break
        if BASE_SHA_PINNED_LINE_PATTERN.match(lines[idx].strip()):
            return True
        scanned += 1
    return False


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (ADR-024 hotfix-bypass family, audit-trailed)
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            "[architect-chief-author-base-sha-freeze] bypass invoked — "
            "BYPASS_ARCHITECT_CHIEF_AUTHOR_BASE_SHA_FREEZE=1"
        )
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description=(
            "CFP-1581 / ADR-073 Amendment 16 — "
            "ArchitectAgent chief author base SHA freeze verify "
            "(ADR-073 §결정 1-Q 4-step primitive)"
        ),
        prog=SCRIPT_NAME,
    )
    parser.add_argument(
        "--worktree-path",
        default=None,
        help="Absolute path to git worktree (for git -C <path> operations)",
    )
    parser.add_argument(
        "--expected-files",
        default=None,
        help="Comma-separated list of expected diff files (Step 4 scope verify)",
    )
    parser.add_argument(
        "--story-file",
        default=None,
        help="Path to Story file for §14 Lane Evidence lint (Mode A + Mode B)",
    )
    parser.add_argument(
        "--mode",
        choices=["4step-verify", "story-lint", "both"],
        default="both",
        help="Operation mode: 4step-verify | story-lint | both (default: both)",
    )

    args = parser.parse_args()

    expected_files: Optional[list[str]] = None
    if args.expected_files:
        expected_files = [f.strip() for f in args.expected_files.split(",") if f.strip()]

    if args.mode == "story-lint":
        if not args.story_file:
            # FP guard: no story file = silent skip
            _exit_pass("--story-file not provided — silent skip (story-lint mode)")
        run_story_lint(args.story_file)
    elif args.mode == "4step-verify":
        run_4step_verify(args.worktree_path, expected_files)
    else:
        # both: run 4step-verify first, story-lint if story-file provided
        # In "both" mode, 4step-verify failure exits before story-lint
        # For workflow use: typically --mode=4step-verify or story-lint separately
        run_4step_verify(args.worktree_path, expected_files)
        # If we reach here, 4step passed; story-lint is supplementary
        if args.story_file:
            run_story_lint(args.story_file)


if __name__ == "__main__":
    main()
