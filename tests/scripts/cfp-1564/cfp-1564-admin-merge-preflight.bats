#!/usr/bin/env bats
# tests/scripts/cfp-1564/cfp-1564-admin-merge-preflight.bats
# CFP-1564 — ADR-113 Wave 2 mechanical wire — admin-merge pre-flight gate bats fixture.
# ADR-113 §결정 1 (5-step procedure) / §결정 5 (failure mode enum 4-fail) / §결정 8 (Wave 2 carrier).
# ADR-060 §결정 5 warning-tier default. ADR-082 §결정 11.A — RED→GREEN stash proof.
# CFP-1334 §8.4 / CFP-1807 precedent — RED→GREEN stash proof pattern + python_shim gh injection.
#
# CFP-1334 §8.4 5-marker presence (bats-red-green-proof-presence check):
#   pre_impl_sha: pre-impl SHA = 294b23d3 (Story §14 lane evidence row pin — worktree base origin/main)
#   git_stash_sequence: stash production logic (git stash push) → RED → restore (git stash pop) → GREEN per CFP-1334 §8.4
#   role_vocabulary: discriminating fixture — regression_guard against ACTION_REQUIRED silent override (developer + architect + qa + orchestrator handoff)
#   red_green_anchor: RED→GREEN stash proof (TC all FAIL at pre-impl HEAD stash → all PASS restore)
#   platform_verified: Windows Git Bash + Ubuntu (CI runner) cross-platform (CFP-418 + ADR-061 Amd 3 ReDoS-safe parser)
#
# Test cases (>=6 TC per CFP-1564 scope):
#   TC-1: all-green (모든 required check completed/success) → exit 0 + PASS + admin merge ALLOW
#   TC-2: ACTION_REQUIRED detection → exit 0 (warning-tier) + ABORT + recovery procedure emit
#   TC-3: head SHA mismatch (PR head ↔ check_run head) → exit 0 + ABORT (stale check)
#   TC-4: attempt cap exceeded (per-PR counter >= 3) → exit 0 + STOP + escalate
#   TC-5: bypass label present (hotfix-bypass:admin-merge-preflight-gate) → exit 0 + ALLOW + audit marker
#   TC-6: meta-error — gh unavailable (fail-1 API call failure) → exit 2 (meta-error)
#   TC-7: state enum unknown (closed-set 외 value) → fail-closed (ABORT, fail-2 semantic)
#
# Production code binding (memory feedback_test_must_bind_to_production):
#   실제 scripts/lib/check_admin_merge_preflight.py 호출. sed-extract / inline hand-copy 금지.
#
# Mock strategy (CFP-1807 답습):
#   gh CLI = python_shim via GH_CLI_BIN_OVERRIDE_MODE=python_shim + GH_SHIM_SCRIPT.
#   shim reads GH_SHIM_CHECKS (gh pr checks JSON) + GH_SHIM_LABELS (gh pr view labels) + GH_SHIM_PR_HEAD (PR headRefOid).
#   Windows: Python subprocess.run CreateProcess cannot exec .sh directly → python3 shim script.

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-admin-merge-preflight.sh"
PY_SSOT="$REPO_ROOT/scripts/lib/check_admin_merge_preflight.py"

setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi

  if [[ ! -f "$SCRIPT" ]]; then
    echo "script not found: $SCRIPT (RED expected pre-impl)" >&2
    false  # genuine RED: production absent
  fi
  if [[ ! -f "$PY_SSOT" ]]; then
    echo "python SSOT not found: $PY_SSOT (RED expected pre-impl)" >&2
    false
  fi

  # python_shim for gh CLI — cross-platform (Windows CreateProcess compatible).
  # Mocks: `gh pr checks <N> --json ...` / `gh pr view <N> --json labels` /
  #        `gh pr view <N> --json headRefOid`.
  mkdir -p "$TEST_DIR/bin"
  cat > "$TEST_DIR/bin/gh_shim.py" <<'GH_SHIM_EOF'
#!/usr/bin/env python3
# gh CLI shim for CFP-1564 bats fixture (Python — cross-platform).
# Routes:
#   gh pr checks <N> --json name,state,bucket,link,description --jq ...  → GH_SHIM_CHECKS file (raw JSON array)
#   gh pr view <N> --json labels --jq ...                               → GH_SHIM_LABELS file (raw JSON)
#   gh pr view <N> --json headRefOid --jq ...                           → GH_SHIM_PR_HEAD env (sha string)
import json
import os
import sys

argv = sys.argv[1:]
# unavailable simulation: GH_SHIM_UNAVAILABLE=1 → exit 127 (command not found semantic)
if os.environ.get("GH_SHIM_UNAVAILABLE", "") == "1":
    print("gh: command not found", file=sys.stderr)
    sys.exit(127)

def emit_file(path):
    if not path or not os.path.isfile(path):
        print("[]", end="")
        return
    with open(path, encoding="utf-8") as f:
        sys.stdout.write(f.read())

if len(argv) >= 2 and argv[0] == "pr" and argv[1] == "checks":
    emit_file(os.environ.get("GH_SHIM_CHECKS", ""))
    sys.exit(0)
if len(argv) >= 2 and argv[0] == "pr" and argv[1] == "view":
    if "headRefOid" in " ".join(argv):
        sys.stdout.write(os.environ.get("GH_SHIM_PR_HEAD", ""))
        sys.exit(0)
    if "labels" in " ".join(argv):
        emit_file(os.environ.get("GH_SHIM_LABELS", ""))
        sys.exit(0)
print(f"shim: unsupported gh invocation: {argv}", file=sys.stderr)
sys.exit(127)
GH_SHIM_EOF

  export GH_SHIM_SCRIPT="$TEST_DIR/bin/gh_shim.py"
  export GH_CLI_BIN_OVERRIDE_MODE="python_shim"
  # attempt-counter file per test (per-PR + per-Story counter persistence)
  export ADMIN_MERGE_ATTEMPT_FILE="$TEST_DIR/attempts.json"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ───────────────────────────────────────────────────────────── TC-1
@test "TC-1: all-green required checks → exit 0 + PASS + admin merge ALLOW" {
  cat > "$TEST_DIR/checks.json" <<'JSON_EOF'
[
  {"name":"phase-gate-mergeable","state":"SUCCESS","bucket":"pass","link":"x"},
  {"name":"invariant-check","state":"SUCCESS","bucket":"pass","link":"y"}
]
JSON_EOF
  export GH_SHIM_CHECKS="$TEST_DIR/checks.json"
  export GH_SHIM_PR_HEAD="abc123"

  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 0 ]
  [[ "$output" == *"ALLOW"* ]]
  [[ "$output" == *"PASS"* ]]
}

# ───────────────────────────────────────────────────────────── TC-2
@test "TC-2: ACTION_REQUIRED detection → exit 0 (warning-tier) + ABORT + recovery procedure" {
  cat > "$TEST_DIR/checks.json" <<'JSON_EOF'
[
  {"name":"phase-gate-mergeable","state":"ACTION_REQUIRED","bucket":"pending","link":"x"}
]
JSON_EOF
  export GH_SHIM_CHECKS="$TEST_DIR/checks.json"
  export GH_SHIM_PR_HEAD="abc123"

  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 0 ]
  [[ "$output" == *"ABORT"* ]]
  [[ "$output" == *"action_required"* ]]
  # Step 3 fresh commit recovery procedure surfaced
  [[ "$output" == *"--allow-empty"* ]]
}

# ───────────────────────────────────────────────────────────── TC-3
@test "TC-3: head SHA mismatch (PR head != provided) → exit 0 + ABORT (stale)" {
  cat > "$TEST_DIR/checks.json" <<'JSON_EOF'
[
  {"name":"phase-gate-mergeable","state":"SUCCESS","bucket":"pass","link":"x"}
]
JSON_EOF
  export GH_SHIM_CHECKS="$TEST_DIR/checks.json"
  export GH_SHIM_PR_HEAD="deadbeef"

  # provided head-sha differs from PR head → stale, must abort even though checks green
  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 0 ]
  [[ "$output" == *"ABORT"* ]]
  [[ "$output" == *"head"* ]]
}

# ───────────────────────────────────────────────────────────── TC-4
@test "TC-4: attempt cap exceeded (per-PR >= 3) → exit 0 + STOP + escalate" {
  cat > "$TEST_DIR/checks.json" <<'JSON_EOF'
[
  {"name":"phase-gate-mergeable","state":"ACTION_REQUIRED","bucket":"pending","link":"x"}
]
JSON_EOF
  export GH_SHIM_CHECKS="$TEST_DIR/checks.json"
  export GH_SHIM_PR_HEAD="abc123"
  # pre-seed attempt counter at cap (per-PR 1564 = 3)
  cat > "$ADMIN_MERGE_ATTEMPT_FILE" <<'JSON_EOF'
{"per_pr": {"1564": 3}, "per_story": {"CFP-1564": 3}}
JSON_EOF

  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 0 ]
  [[ "$output" == *"STOP"* ]]
  [[ "$output" == *"escalat"* ]]
  [[ "$output" == *"3/3"* ]]
}

# ───────────────────────────────────────────────────────────── TC-5
@test "TC-5: bypass label present → exit 0 + ALLOW + audit marker" {
  cat > "$TEST_DIR/checks.json" <<'JSON_EOF'
[
  {"name":"phase-gate-mergeable","state":"ACTION_REQUIRED","bucket":"pending","link":"x"}
]
JSON_EOF
  export GH_SHIM_CHECKS="$TEST_DIR/checks.json"
  export GH_SHIM_PR_HEAD="abc123"
  # gh pr view --json labels --jq "[.labels[].name]" → flat name list (real output form)
  cat > "$TEST_DIR/labels.json" <<'JSON_EOF'
["hotfix-bypass:admin-merge-preflight-gate","phase:구현"]
JSON_EOF
  export GH_SHIM_LABELS="$TEST_DIR/labels.json"

  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 0 ]
  [[ "$output" == *"ALLOW"* ]]
  [[ "$output" == *"bypass"* ]]
  [[ "$output" == *"audit"* ]]
}

# ───────────────────────────────────────────────────────────── TC-6
@test "TC-6: meta-error — gh unavailable (fail-1 API call failure) → exit 2" {
  export GH_SHIM_UNAVAILABLE="1"
  export GH_SHIM_PR_HEAD="abc123"

  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 2 ]
  [[ "$output" == *"meta-error"* ]] || [[ "$output" == *"fail-1"* ]] || [[ "$output" == *"gh"* ]]
}

# ───────────────────────────────────────────────────────────── TC-7
@test "TC-7: state enum unknown (closed-set 외) → fail-closed ABORT (fail-2 semantic)" {
  cat > "$TEST_DIR/checks.json" <<'JSON_EOF'
[
  {"name":"phase-gate-mergeable","state":"FLUMMOXED","bucket":"unknown","link":"x"}
]
JSON_EOF
  export GH_SHIM_CHECKS="$TEST_DIR/checks.json"
  export GH_SHIM_PR_HEAD="abc123"

  run python3 "$PY_SSOT" --pr 1564 --story CFP-1564 --head-sha abc123
  [ "$status" -eq 0 ]
  [[ "$output" == *"ABORT"* ]]
  [[ "$output" == *"fail-closed"* ]]
  [[ "$output" == *"unknown"* ]]
}
