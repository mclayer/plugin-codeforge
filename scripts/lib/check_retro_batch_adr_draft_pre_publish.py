"""
scripts/lib/check_retro_batch_adr_draft_pre_publish.py
CFP-1632 / ADR-045 Amendment 10 — retro batch §6 ADR draft pre-publish 8-tuple verify SSOT

기능:
  PMOAgent retro file 안 §6 ADR draft section authoring 직전 8-tuple verify-before-trust
  gate 통과 여부를 검증 (ADR-045 Amendment 9 §D-10 declarative anchor Wave 2 mechanical wire).

8-tuple verify sources (presence-grep heuristic — AND gate):
  1. source_1_git_show_amendment_log    — [verified via git show origin/main:<ADR-path> ...]
  2. source_2_grep_evidence_registry    — [verified via grep <feature-name> docs/evidence-checks-registry.yaml ...]
  3. source_3_glob_scripts_check        — [verified via Glob scripts/check-<feature-pattern>* ...]
  4. source_4_gh_pr_list_search         — [verified via gh pr list --search '<feature-name> in:title' ...]
  5. source_5_gh_issue_list_search      — [verified via gh issue list --search '<feature-name> in:title' ...]
  6. source_6_git_log_path              — [verified via git log --all --oneline -- <path> ...]
  7. source_7_glob_adr_amendment_scan   — [verified via Glob docs/adr/ADR-*.md ...]
  8. source_8_retro_section_5_pattern   — [verified via §5 cross-Story pattern table ...]

Lint logic 5-step:
  1. Retro file §6 ADR draft section auto-detect (header pattern grep heuristic)
  2. 8-tuple verify source presence-grep (annotation 안 source command verbatim hint string 검증)
  3. 8-tuple AND gate evaluation — 8 source 모두 PASS → no downgrade marker
  4. [verification-out-of-scope: <사유>] reverse-explicit annotation channel (ADR-052 Amendment 3 marker)
  5. Exit code 3-tier 0/1/2

Exit code 3-tier (ADR-060 §결정 15):
  0: PASS (8-tuple AND all present, or §6 section absent = FP guard skip)
  1: WARNING (1+ source hint absent → downgrade marker emission)
  2: ENVIRONMENT_ERROR (dependency absent / retro file not found)

BYPASS:
  BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH=1 — unconditional skip, exit 0 + audit marker

FP guard 4종:
  1. templates/** canonical example 면제
  2. tests/** bats fixture 면제
  3. retro file path scope 한정 (docs/retros/** 외 = silent skip)
  4. §6 section 부재 silent skip (FP 차단)

ADR-061 Amendment 3 §결정 11 CodeQL ReDoS guard:
  - PER_LANE_EVIDENCE_SCAN_CAP = 30 line
  - anchored simple single-line regex 의무
  - line-by-line scan 의무
  - nested quantifier regex 절대 금지

CFP-1612 byte-pattern 답습:
  - Windows cp949 stdout encoding 차단
  - argparse 구조
  - 3-tier graceful degradation
  - Exit helper pattern

Graceful degradation 3 fail-mode:
  401_fail_closed:  retro file 미발견 → exit 2 ENVIRONMENT_ERROR
  429_fail_open:    transient annotation 미충족 → exit 1 WARNING (advisory)
  5xx_noop:         I/O 오류 → exit 0 + advisory stderr marker

Test seam:
  CFP1632_RETRO_FILE_MOCK=<file>       — retro file mock (file path)
  CFP1632_SUBPROCESS_MOCK=1            — subprocess cross-verify mock (no-op, exit 0)
"""

import argparse
import os
import re
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
SCRIPT_NAME = "check_retro_batch_adr_draft_pre_publish"
BYPASS_ENV = "BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH"
RETRO_FILE_MOCK_ENV = "CFP1632_RETRO_FILE_MOCK"
SUBPROCESS_MOCK_ENV = "CFP1632_SUBPROCESS_MOCK"

# PER_LANE_EVIDENCE_SCAN_CAP: ReDoS guard — line-by-line scan 최대 라인 수
PER_LANE_EVIDENCE_SCAN_CAP = 30

# ---------------------------------------------------------------------------
# §6 ADR draft section detection patterns
# 3 패턴 closed-set per codeforge-pmo templates/retro.md canonical SSOT
# ADR-061 Amd 3 §결정 11 ReDoS guard: anchored simple regex, no nested quantifier
# ---------------------------------------------------------------------------
SECTION_6_PATTERNS = [
    re.compile(r"^## §6\."),
    re.compile(r"^## 6\."),
    re.compile(r"^### §6\.1"),
]

# ---------------------------------------------------------------------------
# 8-tuple verify source hint patterns
# Each maps to: (source_key, [hint strings to search])
# presence-grep heuristic — ANY of the hint strings on same line = PASS
# ADR-061 Amd 3 §결정 11 ReDoS guard: anchored simple regex, no nested quantifier
# ---------------------------------------------------------------------------

# source_1: git show origin/main:<ADR-path> frontmatter amendment_log
SOURCE_1_PATTERNS = [
    re.compile(r"\[verified via git show"),
    re.compile(r"\[git show origin/main"),
]

# source_2: grep <feature-name> docs/evidence-checks-registry.yaml
SOURCE_2_PATTERNS = [
    re.compile(r"\[verified via grep.*evidence-checks-registry"),
    re.compile(r"\[grep.*evidence-checks-registry"),
    re.compile(r"\[verified via grep.*docs/evidence"),
]

# source_3: Glob scripts/check-<feature-pattern>*
SOURCE_3_PATTERNS = [
    re.compile(r"\[verified via Glob scripts/check"),
    re.compile(r"\[Glob scripts/check"),
    re.compile(r"\[verified via ls scripts/check"),
]

# source_4: gh pr list --search '<feature-name> in:title' --state merged
SOURCE_4_PATTERNS = [
    re.compile(r"\[verified via gh pr list"),
    re.compile(r"\[gh pr list"),
    re.compile(r"\[verified via gh pr"),
]

# source_5: gh issue list --search '<feature-name> in:title' --state all
SOURCE_5_PATTERNS = [
    re.compile(r"\[verified via gh issue list"),
    re.compile(r"\[gh issue list"),
    re.compile(r"\[verified via gh issue"),
]

# source_6: git log --all --oneline -- <path>
SOURCE_6_PATTERNS = [
    re.compile(r"\[verified via git log"),
    re.compile(r"\[git log --all"),
    re.compile(r"\[git log.*--oneline"),
]

# source_7: Glob docs/adr/ADR-*.md + frontmatter amendment_log cross-Story scan
SOURCE_7_PATTERNS = [
    re.compile(r"\[verified via Glob docs/adr"),
    re.compile(r"\[Glob docs/adr"),
    re.compile(r"\[verified via.*amendment_log"),
]

# source_8: retro §5 cross-Story pattern table anchor_id mapping
SOURCE_8_PATTERNS = [
    re.compile(r"\[verified via §5"),
    re.compile(r"\[§5 cross-Story pattern"),
    re.compile(r"\[verified via.*§5.*pattern"),
    re.compile(r"\[verified via.*pattern table"),
]

# Platform exemption marker (ADR-052 Amendment 3 marker 5종 정합)
VERIFICATION_OUT_OF_SCOPE_PATTERN = re.compile(
    r"\[verification-out-of-scope:"
)

# All 8 source slots (closed-set, AND gate)
SOURCE_SLOTS = [
    ("source_1_git_show_amendment_log", SOURCE_1_PATTERNS),
    ("source_2_grep_evidence_registry", SOURCE_2_PATTERNS),
    ("source_3_glob_scripts_check", SOURCE_3_PATTERNS),
    ("source_4_gh_pr_list_search", SOURCE_4_PATTERNS),
    ("source_5_gh_issue_list_search", SOURCE_5_PATTERNS),
    ("source_6_git_log_path", SOURCE_6_PATTERNS),
    ("source_7_glob_adr_amendment_scan", SOURCE_7_PATTERNS),
    ("source_8_retro_section_5_pattern", SOURCE_8_PATTERNS),
]


# ---------------------------------------------------------------------------
# FP exemption scopes
# ---------------------------------------------------------------------------
FP_EXEMPT_PREFIXES = [
    "templates/",
    "tests/",
    "scripts/",
]

FP_EXEMPT_SUBSTRINGS = [
    "/templates/",
    "/tests/",
    "/scripts/",
]


def _is_fp_exempt(file_path: str) -> bool:
    """
    FP guard: exempt paths that are not retro docs.
    """
    normalized = file_path.replace("\\", "/")
    for prefix in FP_EXEMPT_PREFIXES:
        if normalized.startswith(prefix):
            return True
    for substr in FP_EXEMPT_SUBSTRINGS:
        if substr in normalized:
            return True
    return False


def _is_retro_doc(file_path: str) -> bool:
    """
    Check if file_path is within docs/retros/ scope.
    Silent skip for non-retro docs.
    """
    normalized = file_path.replace("\\", "/")
    return (
        "/docs/retros/" in normalized
        or normalized.startswith("docs/retros/")
    )


# ---------------------------------------------------------------------------
# Exit helpers
# ---------------------------------------------------------------------------
def _exit_pass(msg: str) -> None:
    print(f"[retro-batch-adr-draft-pre-publish] PASS: {msg}")
    sys.exit(0)


def _exit_warning(msg: str) -> None:
    print(f"[retro-batch-adr-draft-pre-publish] WARNING: {msg}", file=sys.stderr)
    print(f"[retro-batch-adr-draft-pre-publish] WARNING: {msg}")
    sys.exit(1)


def _exit_setup_error(msg: str) -> None:
    print(
        f"[retro-batch-adr-draft-pre-publish] ENVIRONMENT_ERROR: {msg}",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# §6 section detection
# ---------------------------------------------------------------------------
def _detect_section_6_start(lines: list) -> Optional[int]:
    """
    Detect §6 ADR draft section header line index (0-indexed).
    Returns None if not found (FP guard: §6 absent = silent skip).
    ADR-061 Amd 3 §결정 11 ReDoS guard: anchored simple regex.
    """
    for idx, line in enumerate(lines):
        for pattern in SECTION_6_PATTERNS:
            if pattern.match(line.rstrip()):
                return idx
    return None


def _detect_section_6_end(lines: list, start_idx: int) -> int:
    """
    Detect end of §6 section (next ## / ### heading at same or higher level).
    Returns line index of first line after §6 content.
    ADR-061 Amd 3 §결정 11 ReDoS guard: simple prefix check.
    """
    NEXT_SECTION = re.compile(r"^##")
    for idx in range(start_idx + 1, len(lines)):
        if NEXT_SECTION.match(lines[idx].rstrip()):
            return idx
    return len(lines)


# ---------------------------------------------------------------------------
# Source hint check: any pattern in pattern_list matches the line
# ADR-061 Amd 3 §결정 11 ReDoS guard: simple compiled regex, no nested quantifier
# ---------------------------------------------------------------------------
def _line_has_any_hint(line: str, pattern_list: list) -> bool:
    """Check if line contains any of the source hint patterns."""
    for pat in pattern_list:
        if pat.search(line) is not None:
            return True
    return False


def _line_has_out_of_scope_exemption(line: str) -> bool:
    """Check if line contains [verification-out-of-scope: ...] exemption marker."""
    return VERIFICATION_OUT_OF_SCOPE_PATTERN.search(line) is not None


# ---------------------------------------------------------------------------
# 8-tuple source slot scan within §6 section lines
# ---------------------------------------------------------------------------
def _scan_section_6_for_8tuple(
    section_lines: list,
    scan_cap: int,
) -> dict:
    """
    Scan §6 section lines for 8-tuple verify source hints.

    Returns dict:
      {
        "source_results": { source_key: {"found": bool, "out_of_scope": bool} },
        "out_of_scope_global": bool,  # any out-of-scope exemption in section
      }

    ADR-061 Amd 3 §결정 11 ReDoS guard:
      - line-by-line scan
      - anchored simple compiled regex per source slot
      - scan_cap limits total lines scanned
    """
    source_results = {
        key: {"found": False, "out_of_scope": False}
        for key, _ in SOURCE_SLOTS
    }
    out_of_scope_global = False
    scanned = 0

    for line in section_lines:
        if scanned >= scan_cap:
            break
        scanned += 1

        # Check global [verification-out-of-scope:] exemption marker
        if _line_has_out_of_scope_exemption(line):
            out_of_scope_global = True

        # Check each source slot
        for source_key, pattern_list in SOURCE_SLOTS:
            if not source_results[source_key]["found"]:
                if _line_has_any_hint(line, pattern_list):
                    source_results[source_key]["found"] = True
            if not source_results[source_key]["out_of_scope"]:
                if _line_has_out_of_scope_exemption(line):
                    source_results[source_key]["out_of_scope"] = True

    return {
        "source_results": source_results,
        "out_of_scope_global": out_of_scope_global,
    }


# ---------------------------------------------------------------------------
# Main lint function
# ---------------------------------------------------------------------------
def run_audit_lint(
    retro_file: str,
    retro_file_label: str,
    scan_cap: int,
) -> None:
    """
    ADR-045 Amendment 9 §D-10 8-tuple verify-before-trust lint:

    Step 1: Retro file §6 ADR draft section auto-detect
    Step 2: 8-tuple verify source presence-grep within §6 section
    Step 3: 8-tuple AND gate evaluation
    Step 4: [verification-out-of-scope:] exemption marker channel
    Step 5: verdict emit (PASS / WARNING + downgrade recommendation)

    FP guard 4종:
      1. templates/** canonical example 면제
      2. tests/** bats fixture 면제
      3. docs/retros/ path-only scope
      4. §6 section 부재 silent skip
    """
    # Resolve mock path (test seam)
    mock_path = os.environ.get(RETRO_FILE_MOCK_ENV)
    actual_path = mock_path if mock_path else retro_file

    # FP guard 1-2: exempt paths
    if _is_fp_exempt(retro_file):
        _exit_pass(f"{retro_file_label}: FP guard exempt path — skip")

    # FP guard 3: retro scope guard
    if not _is_retro_doc(retro_file):
        _exit_pass(
            f"{retro_file_label}: not in docs/retros/ scope — silent skip"
        )

    # Read retro file
    try:
        with open(actual_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except FileNotFoundError:
        _exit_setup_error(f"Retro file not found: {actual_path}")
    except PermissionError:
        _exit_setup_error(f"Retro file permission denied: {actual_path}")

    # Step 1: detect §6 section
    section_6_start = _detect_section_6_start(lines)

    # FP guard 4: §6 absent = silent skip
    if section_6_start is None:
        _exit_pass(
            f"{retro_file_label}: §6 ADR draft section not found — FP guard skip "
            f"(retro does not contain §6 section, no ADR draft candidate present)"
        )

    # Extract §6 section lines
    section_6_end = _detect_section_6_end(lines, section_6_start)
    section_lines = lines[section_6_start:section_6_end]

    # Step 2 + 3 + 4: 8-tuple source presence-grep
    scan_result = _scan_section_6_for_8tuple(
        section_lines=section_lines,
        scan_cap=scan_cap,
    )

    source_results = scan_result["source_results"]
    out_of_scope_global = scan_result["out_of_scope_global"]

    # Evaluate AND gate
    missing_sources = []
    for source_key, _ in SOURCE_SLOTS:
        result = source_results[source_key]
        if not result["found"] and not result["out_of_scope"] and not out_of_scope_global:
            missing_sources.append(source_key)

    # Step 5: verdict
    total_sources = len(SOURCE_SLOTS)
    passed_sources = total_sources - len(missing_sources)

    if not missing_sources:
        _exit_pass(
            f"{retro_file_label}: 8-tuple verify {passed_sources}/{total_sources} sources PASS — "
            f"no downgrade marker required (§6 section lines scanned: {min(len(section_lines), scan_cap)})"
        )

    # WARNING: 1+ source hint absent → downgrade recommendation
    missing_list = "\n".join(f"  - {s}" for s in missing_sources)
    downgrade_msg = (
        f"downgrade_action recommendation: `pivot_mark` or `to_section_4_informational` "
        f"(ADR-045 Amendment 9 §D-10 — 1+ verify source hint absent)"
    )

    if out_of_scope_global:
        # Global [verification-out-of-scope:] exemption present — advisory only
        _exit_pass(
            f"{retro_file_label}: [verification-out-of-scope:] exemption marker detected — "
            f"8-tuple AND gate partially exempt (platform limit), advisory only. "
            f"Missing hints ({len(missing_sources)}/{total_sources}): {missing_list}"
        )

    summary = (
        f"{retro_file_label}: {len(missing_sources)}/{total_sources} 8-tuple verify source hint(s) absent\n"
        f"{missing_list}\n"
        f"{downgrade_msg}"
    )
    _exit_warning(summary)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (ADR-024 hotfix-bypass family, audit-trailed)
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            "[retro-batch-adr-draft-pre-publish] bypass invoked — "
            "BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH=1"
        )
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description=(
            "CFP-1632 / ADR-045 Amendment 10 — "
            "retro batch §6 ADR draft pre-publish 8-tuple verify "
            "(ADR-045 §D-10 8-tuple AND gate)"
        ),
        prog=SCRIPT_NAME,
    )
    parser.add_argument(
        "--retro-file",
        default=None,
        help="Path to retro file for 8-tuple verify lint (docs/retros/ scope)",
    )
    parser.add_argument(
        "--scan-cap",
        type=int,
        default=PER_LANE_EVIDENCE_SCAN_CAP,
        help=(
            f"Maximum lines to scan per §6 section (ReDoS guard, "
            f"default: {PER_LANE_EVIDENCE_SCAN_CAP})"
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["audit", "strict", "mock"],
        default="audit",
        help="Operation mode: audit | strict | mock (default: audit)",
    )

    args = parser.parse_args()

    # mock mode: validate environment (test seam for CI)
    if args.mode == "mock":
        os.environ.setdefault(SUBPROCESS_MOCK_ENV, "1")

    # Determine scan target
    if not args.retro_file:
        _exit_pass("no --retro-file provided — silent skip")

    run_audit_lint(
        retro_file=args.retro_file,
        retro_file_label="retro-file",
        scan_cap=args.scan_cap,
    )


if __name__ == "__main__":
    main()
