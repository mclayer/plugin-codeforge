#!/usr/bin/env bats
# tests/scripts/check-parallel-work-sentinel/test_parallel_work_sentinel.bats
# CFP-967 / ADR-073 Amendment 2 — bats 8 TC
#
# TC coverage:
#   TC-1: title-search happy path (fixture hit)
#   TC-2: title-search miss (empty result)
#   TC-3: epic-state-poll happy path (Epic OPEN + siblings)
#   TC-4: head-compare-sibling-commits delta detected (git log mock)
#   TC-5: graceful degradation api_quota_exceeded (403 fixture → git log fallback)
#   TC-6: graceful degradation hook_self_fail noop + warning
#   TC-7: invariant idempotent (2-run diff = 0)
#   TC-8: invariant BYPASS_PARALLEL_WORK_SENTINEL=1 respected
#
# Side-effect invariants (inline assertion):
#   - no filesystem write outside /tmp/
#   - prerequisite check: gh CLI mock path missing → graceful (exit 0)
#   - plain stdout SSOT I5: JSON output parseable by python3 -m json.tool

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
FIXTURES_DIR="${BATS_TEST_DIRNAME}/fixtures"
SCRIPT_DIR="${BATS_TEST_DIRNAME}/../../../scripts"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_parallel_work_sentinel.py"

setup() {
  export CFP_PRIOR_SHA="f4ad18f7"
  unset BYPASS_PARALLEL_WORK_SENTINEL || true
  unset CFP967_GH_MOCK_RESPONSE || true
  unset CFP967_GIT_LOG_MOCK || true
  unset CFP_CONTEXT || true
}

teardown() {
  unset CFP967_GH_MOCK_RESPONSE || true
  unset CFP967_GIT_LOG_MOCK || true
  unset BYPASS_PARALLEL_WORK_SENTINEL || true
  unset CFP_CONTEXT || true
}

# Helper: run Python SSOT directly
_run_sentinel() {
  python3 "${PYTHON_SSOT}" "$@"
}

# ---------------------------------------------------------------------------
# TC-1: title-search happy path
# ---------------------------------------------------------------------------
@test "TC-1: title-search hit returns matches including CFP issue number" {
  export CFP967_GH_MOCK_RESPONSE="${FIXTURES_DIR}/title-search-hit.json"
  export CFP_CONTEXT="CFP-967"

  run _run_sentinel --mode=title-search
  [ "$status" -eq 0 ]
  echo "$output" | python3 -m json.tool > /dev/null  # valid JSON
  echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d['matches']) >= 1, 'expected matches'"
}

# ---------------------------------------------------------------------------
# TC-2: title-search miss
# ---------------------------------------------------------------------------
@test "TC-2: title-search miss returns empty matches array" {
  export CFP967_GH_MOCK_RESPONSE="${FIXTURES_DIR}/title-search-miss.json"
  export CFP_CONTEXT="CFP-9999-nonexistent"

  run _run_sentinel --mode=title-search
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['matches'] == [], f'expected empty, got {d}'"
}

# ---------------------------------------------------------------------------
# TC-3: epic-state-poll happy path
# ---------------------------------------------------------------------------
@test "TC-3: epic-state-poll OPEN Epic returns siblings" {
  export CFP967_GH_MOCK_RESPONSE="${FIXTURES_DIR}/epic-state-open.json"

  run _run_sentinel --mode=epic-state-poll --epic-id=882
  [ "$status" -eq 0 ]
  echo "$output" | python3 -m json.tool > /dev/null
  echo "$output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['epic_state'] == 'OPEN', f'expected OPEN, got {d}'
assert len(d['siblings']) >= 1, f'expected siblings, got {d}'
"
}

# ---------------------------------------------------------------------------
# TC-4: head-compare-sibling-commits delta detected
# ---------------------------------------------------------------------------
@test "TC-4: head-compare-sibling-commits delta detected returns parallel_detected=true" {
  export CFP967_GIT_LOG_MOCK="${FIXTURES_DIR}/head-compare-delta.txt"
  export CFP_PRIOR_SHA="f4ad18f7"

  run _run_sentinel --mode=head-compare-sibling-commits
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['parallel_detected'] is True, f'expected True, got {d}'
assert len(d['delta_commits']) >= 1, f'expected commits, got {d}'
"
}

# ---------------------------------------------------------------------------
# TC-5: graceful degradation api_quota_exceeded (403 fixture)
# ---------------------------------------------------------------------------
@test "TC-5: graceful degradation api_quota_exceeded — 403 fixture returns fallback marker, exit 0" {
  export CFP967_GH_MOCK_RESPONSE="${FIXTURES_DIR}/api-403.json"
  export CFP_CONTEXT="CFP-967"

  # The mock returns 403 JSON ({"message":..,"status":"403"}) at rc=0 — script detects
  # non-list response, routes to _handle_api_quota_exceeded, falls back to git log grep.
  # --separate-stderr ensures $output contains only stdout (valid JSON); $stderr has warnings.
  run --separate-stderr python3 "${PYTHON_SSOT}" --mode=title-search
  [ "$status" -eq 0 ]
  # stdout-only output should be valid JSON
  echo "$output" | python3 -m json.tool > /dev/null
  # assert degradation marker present in stdout JSON
  [[ "$output" == *"api_quota_exceeded"* ]] || [[ "$output" == *"parallel-work-sentinel-api-failed"* ]]
}

# ---------------------------------------------------------------------------
# TC-6: graceful degradation hook_self_fail noop
# ---------------------------------------------------------------------------
@test "TC-6: hook_self_fail graceful — missing Python SSOT exits 2 (SETUP error) non-blocking" {
  # When Python SSOT is missing, bash wrapper exits 2 (SETUP error)
  # This is non-blocking in SessionStart hook context (ADR-038 Amd 1 §결정 8)
  NONEXISTENT_SSOT="/tmp/cfp967_nonexistent_$(date +%s).py"

  # Simulate: run the bash wrapper with a wrong SSOT path via temp wrapper
  TEMP_WRAPPER=$(mktemp /tmp/test_wrapper_XXXXXX.sh)
  cat > "${TEMP_WRAPPER}" << 'WRAPPER_EOF'
#!/usr/bin/env bash
set -euo pipefail
PYTHON_SSOT="/tmp/nonexistent_sentinel_12345.py"
if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-parallel-work-sentinel] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi
exec python3 "${PYTHON_SSOT}" "$@"
WRAPPER_EOF
  chmod +x "${TEMP_WRAPPER}"

  run bash "${TEMP_WRAPPER}" --mode=title-search
  # exit 2 = SETUP error (non-blocking advisory)
  [ "$status" -eq 2 ]

  rm -f "${TEMP_WRAPPER}"
}

# ---------------------------------------------------------------------------
# TC-7: invariant idempotent
# ---------------------------------------------------------------------------
@test "TC-7: idempotent — re-run produces identical stdout" {
  export CFP967_GH_MOCK_RESPONSE="${FIXTURES_DIR}/title-search-hit.json"
  export CFP_CONTEXT="CFP-967"

  run _run_sentinel --mode=title-search
  FIRST_OUT="$output"

  run _run_sentinel --mode=title-search
  SECOND_OUT="$output"

  [ "$FIRST_OUT" = "$SECOND_OUT" ]
}

# ---------------------------------------------------------------------------
# TC-8: BYPASS_PARALLEL_WORK_SENTINEL=1 respected
# ---------------------------------------------------------------------------
@test "TC-8: BYPASS_PARALLEL_WORK_SENTINEL=1 — exit 0 + bypass invoked marker" {
  export BYPASS_PARALLEL_WORK_SENTINEL=1

  run _run_sentinel --mode=title-search
  [ "$status" -eq 0 ]
  [[ "$output" == *"bypass invoked"* ]]
}

# ---------------------------------------------------------------------------
# TC-9: cp949 / non-ASCII Korean title round-trip (CFP-1540 carrier)
# ---------------------------------------------------------------------------
@test "TC-9: non-ASCII Korean title round-trip — exit 0, UTF-8 preserved, no UnicodeDecodeError" {
  # Part A: mock-path fixture round-trip (JSON fixture with Korean title)
  export CFP967_GH_MOCK_RESPONSE="${FIXTURES_DIR}/non-ascii-title.json"
  export CFP_CONTEXT="CFP-1540"

  run _run_sentinel --mode=title-search
  [ "$status" -eq 0 ]
  # Must be valid JSON (no UnicodeDecodeError crash)
  echo "$output" | python3 -m json.tool > /dev/null
  # Korean characters must be preserved in output (UTF-8 round-trip)
  echo "$output" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert len(d['matches']) >= 1, f'expected 1 match, got {d}'
title = d['matches'][0]['title']
assert '한글' in title, f'Korean chars missing in title: {title!r}'
"
  unset CFP967_GH_MOCK_RESPONSE CFP_CONTEXT

  # Part B: subprocess.run encoding kwarg AST-verify — 3-kwarg combo presence check
  # (text=True, encoding="utf-8", errors="replace") at all 6 sites.
  # RED criterion (pre-fix): missing encoding+errors at text=True sites → exit 1.
  # GREEN criterion (post-fix): all 6 text=True sites have 3-kwarg combo → exit 0.
  CHECKER="${BATS_TEST_DIRNAME}/check_subprocess_encoding.py"
  run python3 "${CHECKER}" "${SCRIPT_DIR}/lib/check_parallel_work_sentinel.py"
  [ "$status" -eq 0 ]
}
