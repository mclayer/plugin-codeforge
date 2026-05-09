#!/usr/bin/env bash
# test-check-domain-knowledge-schema.sh — smoke tests for check-domain-knowledge-schema.sh (CFP-295)
#
# Test matrix:
#   T1: valid-full.md (all required fields + Pattern section)            → PASS (exit 0)
#   T2: valid-problem-section.md (Problem section alternative to Pattern) → PASS (exit 0)
#   T3: invalid-missing-tags.md (tags field absent)                       → FAIL (exit 1)
#   T4: invalid-missing-summary.md (## Summary absent)                    → FAIL (exit 1)
#   T5: invalid-missing-pattern-and-problem.md (neither ## Pattern nor ## Problem) → FAIL (exit 1)
#   T6: invalid-bad-created-date.md (created not YYYY-MM-DD)              → FAIL (exit 1)
#   T7: real docs/domain-knowledge/** files all pass (regression)          → PASS (exit 0)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_BASE="$SCRIPT_DIR/fixtures/check-domain-knowledge-schema"
CHECK_SCRIPT="$SCRIPT_DIR/check-domain-knowledge-schema.sh"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# Run check-domain-knowledge-schema.sh against a single temporary directory
# containing only the given fixture file.
run_on_single_fixture() {
    local fixture_file="$1"
    local tmpdir
    tmpdir="$(mktemp -d)"
    # The script uses DK_ROOT = docs/domain-knowledge relative to repo root.
    # Override by running in a temp dir that mimics the structure.
    mkdir -p "$tmpdir/docs/domain-knowledge/test-area"
    cp "$fixture_file" "$tmpdir/docs/domain-knowledge/test-area/"

    # Run script from the tmpdir, capturing output
    local rc=0
    (cd "$tmpdir" && python3 -u - <<'PY' 2>&1) || rc=$?
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

DK_ROOT = Path("docs/domain-knowledge")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PATTERN_OR_PROBLEM_RE = re.compile(r"^## (Pattern|Problem)\b", re.MULTILINE)
SUMMARY_RE    = re.compile(r"^## Summary\s*$", re.MULTILINE)
USAGE_RE      = re.compile(r"^## Usage\s*$", re.MULTILINE)

def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---\n", 4)
    if end == -1:
        return [], text
    fm_block = text[4:end]
    body = text[end + 5:]
    return fm_block.splitlines(), body

def check_fm_field(fm_lines, field):
    for line in fm_lines:
        m = re.match(rf"^{re.escape(field)}\s*:\s*(.*)", line)
        if m:
            return m.group(1).strip()
    return None

def check_tags_list(fm_lines):
    in_tags = False
    for line in fm_lines:
        if re.match(r"^tags\s*:\s*$", line):
            in_tags = True
            continue
        if re.match(r"^tags\s*:\s*\[", line):
            return bool(re.search(r"\[.+\]", line))
        if in_tags:
            if re.match(r"^\s+-\s+\S", line):
                return True
            elif re.match(r"^\S", line):
                break
    return False

def check_file(md_path):
    fails = []
    text = md_path.read_text(encoding='utf-8')
    fm_lines, body = parse_frontmatter(text)
    if not fm_lines:
        fails.append(f"{md_path}: frontmatter absent")
        return fails
    for field in ["title", "area", "created"]:
        val = check_fm_field(fm_lines, field)
        if val is None:
            fails.append(f"{md_path}: missing field {field}")
        elif field == "created" and not ISO_DATE_RE.match(val):
            fails.append(f"{md_path}: created not ISO date: {val}")
    if not any(re.match(r"^tags\s*:", l) for l in fm_lines) and not check_tags_list(fm_lines):
        fails.append(f"{md_path}: missing tags")
    else:
        tags_val = check_fm_field(fm_lines, "tags")
        if tags_val == "" and not check_tags_list(fm_lines):
            fails.append(f"{md_path}: tags list empty")
    if not SUMMARY_RE.search(body):
        fails.append(f"{md_path}: missing ## Summary")
    if not PATTERN_OR_PROBLEM_RE.search(body):
        fails.append(f"{md_path}: missing ## Pattern or ## Problem")
    if not USAGE_RE.search(body):
        fails.append(f"{md_path}: missing ## Usage")
    return fails

all_fails = []
for md in sorted(DK_ROOT.rglob("*.md")):
    all_fails.extend(check_file(md))

if all_fails:
    for f in all_fails:
        print(f"  FAIL: {f}")
    sys.exit(1)
print("  PASS")
PY
    local result=$rc
    rm -rf "$tmpdir"
    return $result
}

# ─────────────────────────────────────────
# T1: valid-full.md → PASS (exit 0)
# ─────────────────────────────────────────
log "T1: valid-full.md (all required fields + Pattern) -> PASS"
rc=0
run_on_single_fixture "$FIXTURE_BASE/valid-full.md" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=0, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T2: valid-problem-section.md → PASS (exit 0)
# ─────────────────────────────────────────
log "T2: valid-problem-section.md (Problem alternative) -> PASS"
rc=0
run_on_single_fixture "$FIXTURE_BASE/valid-problem-section.md" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=0, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T3: invalid-missing-tags.md → FAIL (exit 1)
# ─────────────────────────────────────────
log "T3: invalid-missing-tags.md (tags absent) -> FAIL"
rc=0
run_on_single_fixture "$FIXTURE_BASE/invalid-missing-tags.md" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 1 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc -- correctly rejected)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=1, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T4: invalid-missing-summary.md → FAIL (exit 1)
# ─────────────────────────────────────────
log "T4: invalid-missing-summary.md (## Summary absent) -> FAIL"
rc=0
run_on_single_fixture "$FIXTURE_BASE/invalid-missing-summary.md" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 1 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc -- correctly rejected)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=1, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T5: invalid-missing-pattern-and-problem.md → FAIL (exit 1)
# ─────────────────────────────────────────
log "T5: invalid-missing-pattern-and-problem.md (neither ## Pattern nor ## Problem) -> FAIL"
rc=0
run_on_single_fixture "$FIXTURE_BASE/invalid-missing-pattern-and-problem.md" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 1 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc -- correctly rejected)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=1, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T6: invalid-bad-created-date.md → FAIL (exit 1)
# ─────────────────────────────────────────
log "T6: invalid-bad-created-date.md (created not YYYY-MM-DD) -> FAIL"
rc=0
run_on_single_fixture "$FIXTURE_BASE/invalid-bad-created-date.md" >/dev/null 2>&1 || rc=$?
if [ $rc -eq 1 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc -- correctly rejected)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=1, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T7: Real docs/domain-knowledge/** files all pass (regression check)
# ─────────────────────────────────────────
log "T7: real docs/domain-knowledge/** files all pass (regression)"
rc=0
(cd "$REPO_ROOT" && bash "$CHECK_SCRIPT" >/dev/null 2>&1) || rc=$?
if [ $rc -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (regression: real files failed check, rc=$rc)"
    (cd "$REPO_ROOT" && bash "$CHECK_SCRIPT" 2>&1) | head -20 >&2
fi

# ─────────────────────────────────────────
log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
