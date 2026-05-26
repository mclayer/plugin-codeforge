"""
scripts/lib/check_adr_dual_block_parity.py
CFP-1648 / ADR-082 Amendment 28 sub-scope 1-Q — ADR dual-block parity lint SSOT
CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S — single-block exemption + H2/H3 detection + scan cap fix

기능:
  docs/adr/ADR-*.md 파일의 frontmatter amendments[] / amendment_log[] 와
  body ## Amendment N / ### Amendment N (H2/H3) section 의 양방향 parity 를 검증한다.

  F-DR-001 P0 origin sentinel scenario:
    frontmatter amendment_log[] entry 존재 but body ## Amendment N section 부재
    → WARNING exit 1

Detection logic:

  Single-block mode (ADR-082 Amendment 30 sub-scope 1-S):
    amendments[] 부재 AND amendment_log[] 존재 → single-block ADR (e.g. ADR-045)
    Block 1 skip (amendments[] empty — meaningless)
    Block 3 skip (amendments[] empty — always mismatch)
    Block 2 retain (amendment_log[] ↔ body — F-DR-001 P0 sentinel, unconditional)

  Dual-block mode (amendments[] + amendment_log[] both present):
    Block 1: amendments[] parity
      - frontmatter amendments[] count ↔ body ## Amendment N H2/H3 count
      - 모든 frontmatter amendment_id 에 대응 body section 존재 여부
      - 모든 body ## Amendment N 에 대응 frontmatter row 존재 여부

    Block 2: amendment_log[] parity  ← F-DR-001 P0 origin
      - frontmatter amendment_log[] count ↔ body ## Amendment N H2/H3 count (동일 invariant)
      - frontmatter amendment_log[] entry 마다 body section 존재 여부 (sentence-level)
      - amendment_log[] 의 amendment_id 추출 → body section 매핑

    Block 3: amendments[] ↔ amendment_log[] cross-count parity

Exit code 3-tier (ADR-060 §결정 15):
  0 PASS: all ADR files parity verified
  1 WARNING: 1+ ADR with parity drift
  2 ENVIRONMENT_ERROR: file unreadable OR YAML parse error

BYPASS:
  BYPASS_ADR_DUAL_BLOCK_PARITY=1 — unconditional skip, exit 0 + audit marker

Test seam (mock env):
  CFP1648_ADR_GLOB_MOCK=<glob>     — ADR glob override (file path glob pattern)
  CFP1648_ADR_DIR_MOCK=<dir>       — ADR dir override (scan target dir)
  CFP1648_MOCK_ENV=1               — mock mode (subprocess cross-verify skip)

ADR-061 Amd 3 §결정 11 CodeQL ReDoS guard:
  - PER_LANE_EVIDENCE_SCAN_CAP = 30 line per section
  - anchored simple single-line regex 의무
  - line-by-line scan 의무
  - nested quantifier regex 절대 금지

CFP-1581 / CFP-1612 / CFP-1647 byte-pattern precedent 답습:
  - Windows cp949 reconfigure
  - SCRIPT_NAME / BYPASS_ENV / MOCK_ENV constants
  - argparse --mode (audit/strict) + --adr-glob flag
  - Anchored simple regex with ReDoS guard
  - Graceful degradation 3 fail-mode
"""

import argparse
import glob
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_adr_dual_block_parity"
BYPASS_ENV = "BYPASS_ADR_DUAL_BLOCK_PARITY"
ADR_GLOB_MOCK_ENV = "CFP1648_ADR_GLOB_MOCK"
ADR_DIR_MOCK_ENV = "CFP1648_ADR_DIR_MOCK"
MOCK_ENV = "CFP1648_MOCK_ENV"

# PER_LANE_EVIDENCE_SCAN_CAP: ReDoS guard — line-by-line scan 최대 라인 수 per section
PER_LANE_EVIDENCE_SCAN_CAP = 30

# ADR file default glob
DEFAULT_ADR_GLOB = "docs/adr/ADR-*.md"

# Exit codes (ADR-060 §결정 15)
EXIT_PASS = 0
EXIT_WARNING = 1
EXIT_ENV_ERROR = 2


# ---------------------------------------------------------------------------
# Simple anchored regex patterns (ReDoS guard: no nested quantifier)
# ---------------------------------------------------------------------------

# frontmatter block detection (YAML --- delimiters)
# Simple: line starting with exactly "---"
FRONTMATTER_DELIM = re.compile(r"^---\s*$")

# amendments[] array item: "  - amendment_id: N"
# Simple anchored pattern (no nested quantifier)
AMENDMENTS_ID_PATTERN = re.compile(r"^\s+-\s+amendment_id:\s+([0-9]+)")

# amendment_log[] array item: "  - amendment_id: N" (list item with dash)
# Matches both:
#   "  - amendment_id: 1"  (amendment_log[] list item — same format as amendments[])
#   "    amendment_id: 1"  (indented field within list item)
# Simple: line with optional dash + amendment_id key under amendment_log block
AMENDMENT_LOG_ID_PATTERN = re.compile(r"^\s+-?\s*amendment_id:\s+([0-9]+)")

# amendment_log[] block start marker
# Simple: line starting the amendment_log array
AMENDMENT_LOG_START_PATTERN = re.compile(r"^amendment_log:")

# amendments[] block start marker
AMENDMENTS_START_PATTERN = re.compile(r"^amendments:")

# Body section H2/H3 header: "## Amendment N ..." or "### Amendment N ..."
# Fix B (CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S):
#   Detect both H2 (##) and H3 (###) amendment headings.
#   Bounded {2,3} quantifier — H1 and H4+ are NOT matched.
#   Anchored simple regex (ADR-061 Amd 3 §결정 11 ReDoS guard — no nested quantifier).
#   Duplicate headings (e.g. "### Amendment 8 적용 evidence") collapse via set() in parity check.
BODY_AMENDMENT_PATTERN = re.compile(r"^#{2,3}\s+Amendment\s+([0-9]+)")


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

def _extract_frontmatter_lines(lines: List[str]) -> List[str]:
    """
    Extract frontmatter lines between first and second --- delimiters.
    Returns empty list if frontmatter not found.
    """
    in_frontmatter = False
    fm_lines: List[str] = []
    delim_count = 0

    # Fix C (CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S):
    # Use a generous safety cap (5000 lines) instead of PER_LANE_EVIDENCE_SCAN_CAP * 10 (300).
    # The real boundary is the 2nd "---" delimiter (loop break below).
    # ADR-082's frontmatter 2nd "---" delimiter is at line ~548 — cap 300 silently truncated
    # amendment_log[] entries 22+ causing false CROSS_BLOCK_COUNT_MISMATCH + BODY_ONLY_NO_LOG.
    # This is a correctness fix, NOT a ReDoS-relevant regex change.
    for line in lines[:5000]:  # safety cap — real boundary = 2nd "---" delimiter
        if FRONTMATTER_DELIM.match(line):
            delim_count += 1
            if delim_count == 1:
                in_frontmatter = True
                continue
            elif delim_count == 2:
                break
        if in_frontmatter:
            fm_lines.append(line)

    return fm_lines


def _extract_amendments_ids(fm_lines: List[str]) -> List[int]:
    """
    Extract amendment_id values from frontmatter amendments[] block.

    Parses:
      amendments:
        - amendment_id: 1
        - amendment_id: 2
        ...

    Returns sorted list of amendment_id integers.
    """
    ids: List[int] = []
    in_amendments = False

    for line in fm_lines:
        # Detect amendments: block start
        if AMENDMENTS_START_PATTERN.match(line):
            in_amendments = True
            continue

        # Detect another top-level key = exit amendments block
        if in_amendments and re.match(r"^[a-z_]", line) and not line.startswith(" "):
            in_amendments = False
            continue

        if in_amendments:
            m = AMENDMENTS_ID_PATTERN.match(line)
            if m:
                ids.append(int(m.group(1)))

    return sorted(ids)


def _extract_amendment_log_ids(fm_lines: List[str]) -> List[int]:
    """
    Extract amendment_id values from frontmatter amendment_log[] block.

    Parses:
      amendment_log:
        - amendment_id: 1
          ...
        - amendment_id: 2
          ...

    Returns sorted list of amendment_id integers.
    """
    ids: List[int] = []
    in_amendment_log = False

    for line in fm_lines:
        # Detect amendment_log: block start
        if AMENDMENT_LOG_START_PATTERN.match(line):
            in_amendment_log = True
            continue

        # Detect another top-level key = exit amendment_log block
        if in_amendment_log and re.match(r"^[a-z_]", line) and not line.startswith(" "):
            in_amendment_log = False
            continue

        if in_amendment_log:
            m = AMENDMENT_LOG_ID_PATTERN.match(line)
            if m:
                ids.append(int(m.group(1)))

    return sorted(ids)


def _extract_body_amendment_ids(lines: List[str]) -> List[int]:
    """
    Extract amendment IDs from body ## Amendment N / ### Amendment N sections.

    Fix B (CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S):
      Now detects both H2 (##) and H3 (###) amendment headings via BODY_AMENDMENT_PATTERN.
      H4+ (#### §D-N etc.) are excluded by the {2,3} upper bound.
      Duplicate headings (e.g. "### Amendment 8 적용 evidence") collapse harmlessly
      via set() in _check_adr_parity — no special dedup needed here.

    Scans entire file body (after frontmatter) for:
      ## Amendment N
      ## Amendment N — ...
      ### Amendment N
      ### Amendment N — ...

    Returns sorted list of amendment IDs found in body.
    """
    ids: List[int] = []
    in_frontmatter = False
    past_frontmatter = False
    delim_count = 0

    for line in lines:
        # Track frontmatter delimiters
        if FRONTMATTER_DELIM.match(line):
            delim_count += 1
            if delim_count == 1:
                in_frontmatter = True
                continue
            elif delim_count == 2:
                in_frontmatter = False
                past_frontmatter = True
                continue

        if not past_frontmatter:
            continue

        # Body: scan for ## Amendment N / ### Amendment N patterns (H2/H3, not H4+)
        m = BODY_AMENDMENT_PATTERN.match(line)
        if m:
            ids.append(int(m.group(1)))

    return sorted(ids)


# ---------------------------------------------------------------------------
# Parity checker
# ---------------------------------------------------------------------------

class ParityResult:
    """Result of a single ADR file parity check."""

    def __init__(self, adr_path: str):
        self.adr_path = adr_path
        self.amendments_ids: List[int] = []
        self.amendment_log_ids: List[int] = []
        self.body_ids: List[int] = []
        self.violations: List[str] = []

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    def add_violation(self, msg: str) -> None:
        self.violations.append(msg)


def _check_adr_parity(adr_path: str) -> ParityResult:
    """
    Check dual-block parity for a single ADR file.

    Returns ParityResult with violations list.
    """
    result = ParityResult(adr_path)

    try:
        with open(adr_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        result.add_violation(f"FILE_READ_ERROR: {e}")
        return result

    # Strip newlines for pattern matching
    lines_stripped = [line.rstrip("\n").rstrip("\r") for line in lines]

    # Extract frontmatter
    fm_lines = _extract_frontmatter_lines(lines_stripped)

    # Extract amendment IDs from both frontmatter blocks
    result.amendments_ids = _extract_amendments_ids(fm_lines)
    result.amendment_log_ids = _extract_amendment_log_ids(fm_lines)

    # Extract body amendment IDs
    result.body_ids = _extract_body_amendment_ids(lines_stripped)

    # Skip ADR files with no amendments (PASS trivially)
    if (not result.amendments_ids and
            not result.amendment_log_ids and
            not result.body_ids):
        return result

    # Fix A (CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S):
    # Single-block mode: amendments[] absent AND amendment_log[] present.
    # These are valid single-block ADRs (e.g. ADR-045) — no amendments[] block by convention.
    # Block 1 and Block 3 are meaningless (amendments[] is empty), so skip them.
    # Block 2 (F-DR-001 P0 sentinel) is always retained — unconditional.
    single_block_mode = (
        not result.amendments_ids and bool(result.amendment_log_ids)
    )

    amendments_set = set(result.amendments_ids)
    body_set = set(result.body_ids)

    if not single_block_mode:
        # -------------------------------------------------------------------
        # Block 1: amendments[] ↔ body parity (dual-block mode only)
        # -------------------------------------------------------------------

        # frontmatter amendments[] has entry but body section missing
        missing_in_body_from_amendments = amendments_set - body_set
        for aid in sorted(missing_in_body_from_amendments):
            result.add_violation(
                f"AMENDMENTS_FRONTMATTER_ONLY: Amendment {aid} in frontmatter "
                f"amendments[] but body ## Amendment {aid} section missing"
            )

        # body section exists but frontmatter amendments[] missing
        missing_in_amendments_from_body = body_set - amendments_set
        for aid in sorted(missing_in_amendments_from_body):
            result.add_violation(
                f"BODY_ONLY_NO_AMENDMENTS: Amendment {aid} in body ## Amendment "
                f"section but frontmatter amendments[] row missing"
            )

    # -----------------------------------------------------------------------
    # Block 2: amendment_log[] ↔ body parity (F-DR-001 P0 sentinel)
    # Unconditionally retained in both single-block and dual-block mode.
    # -----------------------------------------------------------------------
    log_set = set(result.amendment_log_ids)

    # F-DR-001 P0 origin: frontmatter amendment_log[] entry but body section missing
    missing_in_body_from_log = log_set - body_set
    for aid in sorted(missing_in_body_from_log):
        result.add_violation(
            f"AMENDMENT_LOG_FRONTMATTER_ONLY: Amendment {aid} in frontmatter "
            f"amendment_log[] but body ## Amendment {aid} section missing "
            f"(F-DR-001 P0 origin sentinel)"
        )

    # body section exists but frontmatter amendment_log[] missing
    missing_in_log_from_body = body_set - log_set
    for aid in sorted(missing_in_log_from_body):
        result.add_violation(
            f"BODY_ONLY_NO_LOG: Amendment {aid} in body ## Amendment "
            f"section but frontmatter amendment_log[] entry missing"
        )

    if not single_block_mode:
        # -------------------------------------------------------------------
        # Block 3: amendments[] ↔ amendment_log[] count parity (dual-block only)
        # -------------------------------------------------------------------
        if len(result.amendments_ids) != len(result.amendment_log_ids):
            result.add_violation(
                f"CROSS_BLOCK_COUNT_MISMATCH: amendments[] count "
                f"{len(result.amendments_ids)} != amendment_log[] count "
                f"{len(result.amendment_log_ids)}"
            )

    return result


# ---------------------------------------------------------------------------
# Main scan logic
# ---------------------------------------------------------------------------

def _collect_adr_files(adr_glob_pattern: str) -> List[str]:
    """
    Collect ADR file paths matching the glob pattern.
    Supports mock env override.
    """
    mock_glob = os.environ.get(ADR_GLOB_MOCK_ENV, "")
    mock_dir = os.environ.get(ADR_DIR_MOCK_ENV, "")

    if mock_glob:
        return sorted(glob.glob(mock_glob))
    if mock_dir:
        return sorted(glob.glob(os.path.join(mock_dir, "ADR-*.md")))
    return sorted(glob.glob(adr_glob_pattern))


def _emit_pass(msg: str) -> None:
    """Emit PASS line to stdout."""
    print(f"[{SCRIPT_NAME}] PASS: {msg}")


def _emit_warning(msg: str) -> None:
    """Emit WARNING line to stdout."""
    print(f"[{SCRIPT_NAME}] WARNING: {msg}")


def _emit_error(msg: str) -> None:
    """Emit ERROR line to stderr."""
    print(f"[{SCRIPT_NAME}] ERROR: {msg}", file=sys.stderr)


def main() -> int:
    """Main entry point. Returns exit code."""

    # BYPASS check
    if os.environ.get(BYPASS_ENV, "").strip() == "1":
        print(
            f"[{SCRIPT_NAME}] bypass invoked "
            f"(BYPASS_ADR_DUAL_BLOCK_PARITY=1) — skip all checks, exit 0"
        )
        return EXIT_PASS

    # Argument parsing
    parser = argparse.ArgumentParser(
        description="ADR dual-block parity lint (CFP-1648 / ADR-082 sub-scope 1-Q)"
    )
    parser.add_argument(
        "--mode",
        choices=["audit", "strict"],
        default="audit",
        help="audit = warn only; strict = exit 1 on first violation",
    )
    parser.add_argument(
        "--adr-glob",
        default=DEFAULT_ADR_GLOB,
        help=f"ADR file glob pattern (default: {DEFAULT_ADR_GLOB})",
    )
    args = parser.parse_args()

    adr_files = _collect_adr_files(args.adr_glob)

    if not adr_files:
        _emit_pass(
            f"No ADR files matched glob '{args.adr_glob}' — "
            f"nothing to check. exit 0"
        )
        return EXIT_PASS

    all_results: List[ParityResult] = []
    env_error_count = 0

    for adr_path in adr_files:
        try:
            result = _check_adr_parity(adr_path)
            all_results.append(result)
        except Exception as e:
            _emit_error(f"Unexpected error processing {adr_path}: {e}")
            env_error_count += 1

    # Tally
    violation_adrs = [r for r in all_results if r.has_violations]
    pass_adrs = [r for r in all_results if not r.has_violations]

    # File read errors = environment error tier
    file_error_results = [
        r for r in all_results
        if any("FILE_READ_ERROR" in v for v in r.violations)
    ]
    if file_error_results or env_error_count > 0:
        for r in file_error_results:
            for v in r.violations:
                _emit_error(f"{r.adr_path}: {v}")
        return EXIT_ENV_ERROR

    # Report violations
    if violation_adrs:
        for r in violation_adrs:
            for v in r.violations:
                _emit_warning(f"{r.adr_path}: {v}")

        total_violations = sum(len(r.violations) for r in violation_adrs)
        _emit_warning(
            f"{len(violation_adrs)} ADR file(s) with dual-block parity drift "
            f"({total_violations} violation(s) total). "
            f"PASS: {len(pass_adrs)} / WARNING: {len(violation_adrs)} "
            f"of {len(adr_files)} files scanned."
        )
        return EXIT_WARNING

    # All PASS
    _emit_pass(
        f"All {len(adr_files)} ADR file(s) dual-block parity verified. "
        f"amendments[] ↔ body ↔ amendment_log[] parity OK."
    )
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
