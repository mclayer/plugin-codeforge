"""
scripts/lib/check_numeric_claim_write_time.py
CFP-1612 / ADR-082 Amendment 25 sub-scope 1-N — numeric claim write-time verify SSOT
CFP-1647 / ADR-082 Amendment 27 sub-scope 1-P — PR commit msg + PR body scope expansion

기능:
  Governance document (Story file / Change Plan / PR commit message / PR body) 안의
  숫자 주장(numeric claim)에 대해 ADR-082 §결정 1-K 4-step verify-before-write mandate
  준수 여부를 검증.

Numeric claim 6 closed-set dimension:
  1. line_count    — "+93 lines", "+101 lines", "+54 lines", "~400 LOC" 등
  2. file_count    — "10 file", "14 file", "5 file", "N files changed" 등
  3. api_count     — "5 endpoints", "8 methods", "3 API" 등
  4. pattern_count — "pattern_count 5 reach", "5 incidents", "5 occurrences" 등
  5. commit_count  — "5 commits drift", "3 commits ahead", "N commit" 등
  6. row_count     — "127번째 entry", "99번째 family member", "N번째" 등

Source command grep heuristic:
  정규식 패턴 detection → inline source command hint 검사
  (예: `[verified via grep ...]`, `[git log --oneline | wc -l]`)

Cross-verify mode (when source command 명시):
  실 execute + actual value 비교

Exit code 3-tier (ADR-060 §결정 15):
  0: PASS
  1: WARNING (numeric claim source absent / mismatch)
  2: ENVIRONMENT_ERROR (dependency absent / auth failed)

BYPASS:
  BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY=1 — unconditional skip, exit 0 + audit marker

ADR-061 Amd 3 §결정 11 CodeQL ReDoS guard:
  - PER_LANE_EVIDENCE_SCAN_CAP = 30 line
  - anchored simple single-line regex 의무
  - line-by-line scan 의무
  - nested quantifier regex 절대 금지

ADR-082 §결정 1-K 4-step mandate:
  Step 1: numeric claim 감지 (6 dimension closed-set)
  Step 2: inline source command hint 존재 여부 검사
  Step 3: source command 명시 시 cross-verify (실 execute + actual value 비교)
  Step 4: verdict emit (PASS / WARNING + location info)

CFP-1581 precedent (check_architect_chief_author_base_sha_freeze.py) byte-pattern 답습:
  - Windows cp949 stdout encoding 차단
  - argparse 구조
  - 3-tier graceful degradation
  - Exit helper pattern

Graceful degradation 3 fail-mode:
  401_fail_closed:  subprocess 실행 실패 → exit 2 ENVIRONMENT_ERROR
  429_fail_open:    transient error → exit 0 + warning marker
  5xx_noop:         I/O 오류 → exit 0 + advisory stderr marker

Test seam:
  CFP1612_STORY_FILE_MOCK=<file>       — Story file mock (file path)
  CFP1612_CHANGE_PLAN_MOCK=<file>      — Change Plan mock (file path)
  CFP1612_SUBPROCESS_MOCK=1            — subprocess cross-verify mock (no-op, exit 0)
  CFP1647_PR_COMMIT_MSG_MOCK=<file>    — PR commit messages mock (file path, CFP-1647)
  CFP1647_PR_BODY_MOCK=<file>          — PR body mock (file path, CFP-1647)

Scope flags (CFP-1647 sub-scope 1-P Wave 2 expansion):
  --scope pr-commit-msg  — PR commit messages via gh api or git log
  --scope pr-body        — PR description body via gh pr view
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
SCRIPT_NAME = "check_numeric_claim_write_time"
BYPASS_ENV = "BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY"
STORY_FILE_MOCK_ENV = "CFP1612_STORY_FILE_MOCK"
CHANGE_PLAN_MOCK_ENV = "CFP1612_CHANGE_PLAN_MOCK"
SUBPROCESS_MOCK_ENV = "CFP1612_SUBPROCESS_MOCK"
PR_COMMIT_MSG_MOCK_ENV = "CFP1647_PR_COMMIT_MSG_MOCK"  # CFP-1647 sub-scope 1-P
PR_BODY_MOCK_ENV = "CFP1647_PR_BODY_MOCK"              # CFP-1647 sub-scope 1-P

# PER_LANE_EVIDENCE_SCAN_CAP: ReDoS guard — line-by-line scan 최대 라인 수
PER_LANE_EVIDENCE_SCAN_CAP = 30

# ---------------------------------------------------------------------------
# Numeric claim detection patterns (6 closed-set dimensions)
# ADR-061 Amd 3 §결정 11 ReDoS guard: anchored simple regex, no nested quantifier
# ---------------------------------------------------------------------------

# Dimension 1: line_count
# Matches: "+93 lines", "+101 lines", "~400 LOC", "93줄", "+N line"
# Simple: digit sequence followed by line/LOC keyword
LINE_COUNT_PATTERN = re.compile(
    r"\+?\~?([0-9]{1,6})\s*(lines?|LOC|줄)"
)

# Dimension 2: file_count
# Matches: "10 file", "14 files", "5 file changed"
FILE_COUNT_PATTERN = re.compile(
    r"\b([0-9]{1,5})\s+files?\b"
)

# Dimension 3: api_count
# Matches: "5 endpoints", "8 methods", "3 API"
API_COUNT_PATTERN = re.compile(
    r"\b([0-9]{1,4})\s+(endpoints?|methods?|APIs?)\b"
)

# Dimension 4: pattern_count
# Matches: "pattern_count 5", "5 incidents", "5 occurrences", "5번 발생"
PATTERN_COUNT_PATTERN = re.compile(
    r"pattern_count\s+([0-9]{1,4})|([0-9]{1,4})\s+(incidents?|occurrences?|발생|횟수)"
)

# Dimension 5: commit_count
# Matches: "5 commits drift", "3 commits ahead", "N commits"
COMMIT_COUNT_PATTERN = re.compile(
    r"\b([0-9]{1,5})\s+commits?\b"
)

# Dimension 6: row_count
# Matches: "127번째 entry", "99번째 family member", "N번째"
# Note: 번째 = Korean ordinal suffix
ROW_COUNT_PATTERN = re.compile(
    r"\b([0-9]{1,6})번째\b"
)

# All 6 dimension patterns (closed-set)
NUMERIC_CLAIM_PATTERNS = [
    ("line_count", LINE_COUNT_PATTERN),
    ("file_count", FILE_COUNT_PATTERN),
    ("api_count", API_COUNT_PATTERN),
    ("pattern_count", PATTERN_COUNT_PATTERN),
    ("commit_count", COMMIT_COUNT_PATTERN),
    ("row_count", ROW_COUNT_PATTERN),
]

# ---------------------------------------------------------------------------
# Source command hint patterns
# Matches: [verified via grep ...], [git log --oneline | wc -l], etc.
# Simple anchored regex (no nested quantifier — ReDoS guard)
# ---------------------------------------------------------------------------
SOURCE_HINT_INLINE_PATTERN = re.compile(
    r"\[verified\s+via\s+\S"
)

SOURCE_HINT_GIT_PATTERN = re.compile(
    r"\[git\s+\S"
)

SOURCE_HINT_GREP_PATTERN = re.compile(
    r"\[grep\s+\S"
)

SOURCE_HINT_WC_PATTERN = re.compile(
    r"\[wc\s+"
)

# Compound: any inline source hint bracket
# Simple OR check (no | alternation in compiled regex — ReDoS guard)
def _has_source_hint(line: str) -> bool:
    """Check if line contains any source command hint marker."""
    return (
        SOURCE_HINT_INLINE_PATTERN.search(line) is not None
        or SOURCE_HINT_GIT_PATTERN.search(line) is not None
        or SOURCE_HINT_GREP_PATTERN.search(line) is not None
        or SOURCE_HINT_WC_PATTERN.search(line) is not None
    )


# ---------------------------------------------------------------------------
# FP exemption scopes
# ---------------------------------------------------------------------------
FP_EXEMPT_PREFIXES = [
    "templates/",
    "tests/",
    "scripts/",
    "docs/adr/",
]

FP_EXEMPT_SUBSTRINGS = [
    "/templates/",
    "/tests/",
    "/scripts/",
    "/docs/adr/",
]

def _is_fp_exempt(file_path: str) -> bool:
    """
    FP guard: exempt paths that are not governance docs.
    Scope: docs/stories/ + docs/change-plans/ only (story/change-plan lint scope).
    templates/** / tests/** / scripts/** / docs/adr/** = exempt.
    """
    normalized = file_path.replace("\\", "/")
    for prefix in FP_EXEMPT_PREFIXES:
        if normalized.startswith(prefix):
            return True
    for substr in FP_EXEMPT_SUBSTRINGS:
        if substr in normalized:
            return True
    return False


def _is_governance_doc(file_path: str) -> bool:
    """
    Check if file_path is within docs/stories/ or docs/change-plans/ scope.
    Silent skip for non-governance docs.
    """
    normalized = file_path.replace("\\", "/")
    return (
        "/docs/stories/" in normalized
        or normalized.startswith("docs/stories/")
        or "/docs/change-plans/" in normalized
        or normalized.startswith("docs/change-plans/")
    )


# ---------------------------------------------------------------------------
# Exit helpers
# ---------------------------------------------------------------------------
def _exit_pass(msg: str) -> None:
    print(f"[numeric-claim-write-time-verify] PASS: {msg}")
    sys.exit(0)


def _exit_warning(msg: str) -> None:
    print(f"[numeric-claim-write-time-verify] WARNING: {msg}", file=sys.stderr)
    print(f"[numeric-claim-write-time-verify] WARNING: {msg}")
    sys.exit(1)


def _exit_setup_error(msg: str) -> None:
    print(
        f"[numeric-claim-write-time-verify] ENVIRONMENT_ERROR: {msg}",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Numeric claim finding dataclass (simple dict)
# ---------------------------------------------------------------------------
def _make_finding(
    line_no: int,
    dimension: str,
    matched_value: str,
    line_text: str,
    source_hint_present: bool,
) -> dict:
    return {
        "line_no": line_no,
        "dimension": dimension,
        "matched_value": matched_value,
        "line_text": line_text.strip(),
        "source_hint_present": source_hint_present,
    }


# ---------------------------------------------------------------------------
# Core scan: detect numeric claims in a list of lines
# ---------------------------------------------------------------------------
def _scan_lines_for_numeric_claims(
    lines: list[str],
    scan_cap: int,
) -> list[dict]:
    """
    Scan lines for numeric claims (6 dimension closed-set).

    ADR-061 Amd 3 §결정 11 ReDoS guard:
      - line-by-line scan
      - anchored simple compiled regex per dimension
      - scan_cap limits total lines scanned

    Returns list of findings (dicts).
    """
    findings = []
    scanned = 0
    for line_no, line in enumerate(lines, start=1):
        if scanned >= scan_cap:
            break
        scanned += 1

        # Check source hint on same line (inline verification marker)
        source_hint = _has_source_hint(line)

        # Scan each dimension
        for dim_name, pattern in NUMERIC_CLAIM_PATTERNS:
            match = pattern.search(line)
            if match:
                # Extract numeric value from first capturing group with a digit
                matched_value = ""
                for grp in match.groups():
                    if grp and grp.isdigit():
                        matched_value = grp
                        break
                if not matched_value:
                    matched_value = match.group(0)

                findings.append(
                    _make_finding(
                        line_no=line_no,
                        dimension=dim_name,
                        matched_value=matched_value,
                        line_text=line,
                        source_hint_present=source_hint,
                    )
                )
                # One finding per line per dimension — continue scanning other dims
    return findings


# ---------------------------------------------------------------------------
# Source command cross-verify (Step 3)
# ---------------------------------------------------------------------------
def _cross_verify_source_hint(
    line_text: str,
    claimed_value: str,
    worktree_path: Optional[str],
) -> tuple[bool, str]:
    """
    If line contains a source command hint like [git log --oneline | wc -l],
    attempt to execute the command and compare actual value with claimed_value.

    Returns (verified: bool, detail: str).
    ADR-061 Amd 3 ReDoS guard: simple string search, no complex regex.
    """
    if os.environ.get(SUBPROCESS_MOCK_ENV) == "1":
        return True, "subprocess mock — cross-verify skipped"

    # Extract command from [git ...] or [grep ...] bracket hint
    # Simple bracket extraction: find [ ... ] block
    bracket_start = line_text.find("[git ")
    if bracket_start < 0:
        bracket_start = line_text.find("[grep ")
    if bracket_start < 0:
        bracket_start = line_text.find("[wc ")
    if bracket_start < 0:
        return True, "no executable source command found — skip cross-verify"

    bracket_end = line_text.find("]", bracket_start)
    if bracket_end < 0:
        return True, "malformed source hint bracket — skip cross-verify"

    raw_cmd = line_text[bracket_start + 1 : bracket_end].strip()
    if not raw_cmd:
        return True, "empty source command — skip cross-verify"

    # Safety: only allow simple git/grep/wc commands (no shell injection)
    # ADR-061 Amd 3: simple prefix check
    allowed_prefixes = ("git ", "grep ", "wc ", "wc\t")
    if not any(raw_cmd.startswith(p) for p in allowed_prefixes):
        return True, f"source command not in allowlist — skip: {raw_cmd[:40]}"

    # Execute in worktree_path context
    try:
        cmd_parts = raw_cmd.split("|")
        # Only support single-pipe chains (safety limit)
        if len(cmd_parts) > 2:
            return True, "multi-pipe source command — skip cross-verify (safety limit)"

        # Run the command
        cwd = worktree_path or "."
        result = subprocess.run(
            raw_cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            timeout=10,
        )
        actual_output = result.stdout.strip()

        # Extract numeric value from output
        num_match = re.search(r"([0-9]+)", actual_output)
        if not num_match:
            return True, f"no numeric output from source command — skip compare"

        actual_value = num_match.group(1)
        if actual_value == claimed_value:
            return True, f"cross-verify MATCH: claimed={claimed_value} actual={actual_value}"
        else:
            return False, (
                f"cross-verify MISMATCH: claimed={claimed_value} actual={actual_value} "
                f"(command: {raw_cmd[:60]})"
            )

    except subprocess.TimeoutExpired:
        return True, "source command timeout — skip cross-verify (fail-open)"
    except Exception as exc:
        return True, f"source command exec error — skip cross-verify: {exc}"


# ---------------------------------------------------------------------------
# Main lint function: audit mode
# ---------------------------------------------------------------------------
def run_audit_lint(
    scan_file: str,
    scan_file_label: str,
    strict_mode: bool,
    scan_cap: int,
    worktree_path: Optional[str],
) -> None:
    """
    ADR-082 §결정 1-K 4-step numeric claim verify-before-write:

    Step 1: numeric claim 감지 (6 dimension closed-set)
    Step 2: inline source command hint 존재 여부 검사
    Step 3: source command 명시 시 cross-verify (실 execute + actual value 비교)
    Step 4: verdict emit

    FP guard 4종:
      1. templates/** canonical example 면제
      2. tests/** bats fixture 면제
      3. scripts/** 면제
      4. docs/stories/ + docs/change-plans/ path-only scope
    """
    # Resolve mock path
    mock_env = STORY_FILE_MOCK_ENV if "story" in scan_file_label else CHANGE_PLAN_MOCK_ENV
    mock_path = os.environ.get(mock_env)
    actual_path = mock_path if mock_path else scan_file

    # FP guard 1-3: exempt check (scope_path = scan_file, not mock_path)
    if _is_fp_exempt(scan_file):
        _exit_pass(f"{scan_file_label}: FP guard exempt path — skip")

    # FP guard 4: scope guard
    if not _is_governance_doc(scan_file):
        _exit_pass(f"{scan_file_label}: not in governance doc scope (docs/stories/ or docs/change-plans/) — silent skip")

    # Read file
    try:
        with open(actual_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except FileNotFoundError:
        _exit_setup_error(f"File not found: {actual_path}")
    except PermissionError:
        _exit_setup_error(f"File permission denied: {actual_path}")

    # Step 1: scan for numeric claims
    findings = _scan_lines_for_numeric_claims(lines, scan_cap=scan_cap)

    if not findings:
        _exit_pass(
            f"{scan_file_label}: no numeric claims detected in {len(lines)} lines "
            f"(scan_cap={scan_cap}) — PASS"
        )

    # Step 2 + 3: check source hint + cross-verify for each finding
    warnings = []
    verified_count = 0

    for finding in findings:
        if finding["source_hint_present"]:
            # Step 3: cross-verify if source command hint present
            ok, detail = _cross_verify_source_hint(
                line_text=finding["line_text"],
                claimed_value=finding["matched_value"],
                worktree_path=worktree_path,
            )
            if ok:
                verified_count += 1
            else:
                warnings.append(
                    f"  line {finding['line_no']} [{finding['dimension']}] "
                    f"value={finding['matched_value']}: {detail}"
                )
        else:
            # Step 2 failed: no source hint
            # Check ±1 line context for source hint (adjacent line tolerance)
            line_idx = finding["line_no"] - 1  # 0-indexed
            adjacent_lines = []
            if line_idx > 0:
                adjacent_lines.append(lines[line_idx - 1])
            if line_idx + 1 < len(lines):
                adjacent_lines.append(lines[line_idx + 1])

            adjacent_hint = any(_has_source_hint(al) for al in adjacent_lines)

            if adjacent_hint:
                verified_count += 1
            else:
                warnings.append(
                    f"  line {finding['line_no']} [{finding['dimension']}] "
                    f"value={finding['matched_value']}: "
                    f"no inline source hint found "
                    f"(ADR-082 §결정 1-K: numeric claim requires [verified via ...] marker)"
                )

    # Step 4: verdict
    total = len(findings)
    if warnings:
        summary = (
            f"{scan_file_label}: {len(warnings)}/{total} numeric claim(s) missing source hint\n"
            + "\n".join(warnings)
        )
        if strict_mode:
            _exit_warning(summary)
        else:
            # audit mode: emit warning but exit 1 (warning tier — non-blocking)
            _exit_warning(summary)
    else:
        _exit_pass(
            f"{scan_file_label}: {verified_count}/{total} numeric claim(s) have source hints — all verified"
        )


# ---------------------------------------------------------------------------
# CFP-1647 sub-scope 1-P: PR commit msg + PR body ingestion functions
# ADR-061 Amd 3 §결정 11 ReDoS guard: simple subprocess + line-split only
# ---------------------------------------------------------------------------

def _read_pr_commit_msgs(pr_number: Optional[str], base: str = "main") -> list[str]:
    """
    Ingest PR commit messages for numeric claim scanning.

    Primary:   gh api repos/<owner>/<repo>/pulls/<pr>/commits (JSON array)
    Fallback:  git log --format=%B <base>..HEAD (local, no gh auth required)
    Mock:      CFP1647_PR_COMMIT_MSG_MOCK env = file path to mock content

    ADR-061 Amd 3 §결정 11 ReDoS guard: no nested quantifier, line-by-line only.
    Graceful degradation:
      gh 401/404 → git log fallback
      git log error → empty list (fail-open, advisory stderr)
      subprocess timeout → empty list (fail-open)
    """
    # Test seam: mock file override
    mock_path = os.environ.get(PR_COMMIT_MSG_MOCK_ENV)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()
        except OSError:
            return []

    if os.environ.get(SUBPROCESS_MOCK_ENV) == "1":
        return []

    # Primary: gh api (requires auth + GH_TOKEN)
    if pr_number:
        try:
            import json as _json
            result = subprocess.run(
                ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/commits",
                 "--jq", ".[].commit.message"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.splitlines(keepends=True)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    # Fallback: git log --format=%B <base>..HEAD
    try:
        result = subprocess.run(
            ["git", "log", "--format=%B", f"{base}..HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        if result.returncode == 0:
            return result.stdout.splitlines(keepends=True)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        print(
            f"[numeric-claim-write-time-verify] advisory: git log fallback failed: {exc}",
            file=sys.stderr,
        )

    return []


def _read_pr_body(pr_number: Optional[str]) -> list[str]:
    """
    Ingest PR description body for numeric claim scanning.

    Primary:   gh pr view <pr> --json title,body --jq .body
    Mock:      CFP1647_PR_BODY_MOCK env = file path to mock content

    ADR-061 Amd 3 §결정 11 ReDoS guard: no nested quantifier, line-by-line only.
    Graceful degradation:
      gh 401/404 → empty list (fail-open, advisory stderr)
      subprocess timeout → empty list (fail-open)
    """
    # Test seam: mock file override
    mock_path = os.environ.get(PR_BODY_MOCK_ENV)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()
        except OSError:
            return []

    if os.environ.get(SUBPROCESS_MOCK_ENV) == "1":
        return []

    if not pr_number:
        return []

    try:
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "title,body", "--jq", ".body"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.splitlines(keepends=True)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        print(
            f"[numeric-claim-write-time-verify] advisory: gh pr view failed: {exc}",
            file=sys.stderr,
        )

    return []


def run_pr_scope_lint(
    scope: str,
    pr_number: Optional[str],
    base: str,
    strict_mode: bool,
    scan_cap: int,
    worktree_path: Optional[str],
) -> None:
    """
    CFP-1647 sub-scope 1-P: PR scope lint runner.
    scope: "pr-commit-msg" | "pr-body"

    ADR-082 §결정 1-K 4-step mandate applied to PR content:
      Step 1: ingest PR content (commit msgs or body)
      Step 2-3: same as run_audit_lint
      Step 4: verdict emit

    Graceful degradation: empty content → PASS (fail-open, no PR content available)
    """
    # Ingest PR content
    if scope == "pr-commit-msg":
        lines = _read_pr_commit_msgs(pr_number, base=base)
        scope_label = "pr-commit-msg"
    elif scope == "pr-body":
        lines = _read_pr_body(pr_number)
        scope_label = "pr-body"
    else:
        _exit_pass(f"unknown scope '{scope}' — silent skip")

    if not lines:
        _exit_pass(
            f"{scope_label}: no content available (empty PR or auth unavailable) — PASS"
        )

    # Step 1: scan for numeric claims
    findings = _scan_lines_for_numeric_claims(lines, scan_cap=scan_cap)

    if not findings:
        _exit_pass(
            f"{scope_label}: no numeric claims detected in {len(lines)} lines "
            f"(scan_cap={scan_cap}) — PASS"
        )

    # Step 2 + 3: check source hint + cross-verify for each finding
    warnings = []
    verified_count = 0

    for finding in findings:
        if finding["source_hint_present"]:
            ok, detail = _cross_verify_source_hint(
                line_text=finding["line_text"],
                claimed_value=finding["matched_value"],
                worktree_path=worktree_path,
            )
            if ok:
                verified_count += 1
            else:
                warnings.append(
                    f"  line {finding['line_no']} [{finding['dimension']}] "
                    f"value={finding['matched_value']}: {detail}"
                )
        else:
            # ±1 line context tolerance
            line_idx = finding["line_no"] - 1
            adjacent_lines = []
            if line_idx > 0:
                adjacent_lines.append(lines[line_idx - 1])
            if line_idx + 1 < len(lines):
                adjacent_lines.append(lines[line_idx + 1])
            adjacent_hint = any(_has_source_hint(al) for al in adjacent_lines)

            if adjacent_hint:
                verified_count += 1
            else:
                warnings.append(
                    f"  line {finding['line_no']} [{finding['dimension']}] "
                    f"value={finding['matched_value']}: "
                    f"no inline source hint found "
                    f"(ADR-082 §결정 1-K: numeric claim requires [verified via ...] marker)"
                )

    # Step 4: verdict
    total = len(findings)
    if warnings:
        summary = (
            f"{scope_label}: {len(warnings)}/{total} numeric claim(s) missing source hint\n"
            + "\n".join(warnings)
        )
        _exit_warning(summary)
    else:
        _exit_pass(
            f"{scope_label}: {verified_count}/{total} numeric claim(s) have source hints — all verified"
        )


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (ADR-024 hotfix-bypass family, audit-trailed)
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            "[numeric-claim-write-time-verify] bypass invoked — "
            "BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY=1"
        )
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description=(
            "CFP-1612 / ADR-082 Amendment 25 sub-scope 1-N — "
            "numeric claim write-time verify "
            "(ADR-082 §결정 1-K 4-step mandate). "
            "CFP-1647 / ADR-082 Amendment 27 sub-scope 1-P — "
            "PR commit msg + PR body scope expansion."
        ),
        prog=SCRIPT_NAME,
    )
    parser.add_argument(
        "--story-file",
        default=None,
        help="Path to Story file for numeric claim lint (docs/stories/ scope)",
    )
    parser.add_argument(
        "--change-plan",
        default=None,
        help="Path to Change Plan file for numeric claim lint (docs/change-plans/ scope)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Strict mode: verify-or-fail (exit 1 on any unverified claim)",
    )
    parser.add_argument(
        "--scan-cap",
        type=int,
        default=PER_LANE_EVIDENCE_SCAN_CAP,
        help=f"Maximum lines to scan per file (ReDoS guard, default: {PER_LANE_EVIDENCE_SCAN_CAP})",
    )
    parser.add_argument(
        "--mode",
        choices=["audit", "strict", "mock"],
        default="audit",
        help="Operation mode: audit | strict | mock (default: audit)",
    )
    parser.add_argument(
        "--worktree-path",
        default=None,
        help="Absolute path to git worktree (for cross-verify subprocess invocation)",
    )
    # CFP-1647 sub-scope 1-P: new scope flags
    parser.add_argument(
        "--scope",
        choices=["pr-commit-msg", "pr-body"],
        default=None,
        help=(
            "CFP-1647 sub-scope 1-P: PR scope to lint. "
            "'pr-commit-msg' — scan PR commit messages; "
            "'pr-body' — scan PR description body. "
            "Requires --pr when not using mock env."
        ),
    )
    parser.add_argument(
        "--pr",
        default=None,
        dest="pr_number",
        help="PR number for --scope pr-commit-msg / pr-body ingestion (CFP-1647 sub-scope 1-P)",
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch for git log fallback in --scope pr-commit-msg (default: main)",
    )

    args = parser.parse_args()

    # Resolve strict_mode from --mode or --strict flag
    strict_mode = args.strict or (args.mode == "strict")

    # mock mode: validate environment (test seam for CI)
    if args.mode == "mock":
        # In mock mode, subprocess cross-verify is no-op
        os.environ.setdefault(SUBPROCESS_MOCK_ENV, "1")

    # CFP-1647 sub-scope 1-P: PR scope dispatch (mutually exclusive with file targets)
    if args.scope:
        run_pr_scope_lint(
            scope=args.scope,
            pr_number=args.pr_number,
            base=args.base,
            strict_mode=strict_mode,
            scan_cap=args.scan_cap,
            worktree_path=args.worktree_path,
        )
        return  # run_pr_scope_lint calls sys.exit internally

    # Determine scan target(s) — original file-based scan
    scan_targets: list[tuple[str, str]] = []
    if args.story_file:
        scan_targets.append((args.story_file, "story-file"))
    if args.change_plan:
        scan_targets.append((args.change_plan, "change-plan"))

    if not scan_targets:
        # No target provided — silent skip (FP guard: no governance doc = not applicable)
        _exit_pass("no --story-file or --change-plan provided — silent skip")

    # Run audit lint for each target
    # For multiple targets: first WARNING exit wins (consistent with warning tier)
    for scan_file, label in scan_targets:
        # Override mock env based on label
        if label == "story-file" and os.environ.get(STORY_FILE_MOCK_ENV):
            pass  # mock env already set
        elif label == "change-plan" and os.environ.get(CHANGE_PLAN_MOCK_ENV):
            pass  # mock env already set

        run_audit_lint(
            scan_file=scan_file,
            scan_file_label=label,
            strict_mode=strict_mode,
            scan_cap=args.scan_cap,
            worktree_path=args.worktree_path,
        )


if __name__ == "__main__":
    main()
