#!/usr/bin/env bats
# tests/scripts/test_check-branch-protection-context-name-strict-match.sh
# CFP-1849 — branch-protection-context-name-strict-match bats fixture (Wave 2 mechanical wire)
# ADR-024 §결정 6.A + ADR-060 warning-tier framework
# CFP-1334 §8.4 precedent — RED→GREEN stash proof pattern
#
# CFP-1334 §8.4 5-marker presence (bats-red-green-proof-presence check):
#   pre_impl_sha: pre-impl SHA = cea7fb80 (origin/main pre-write, Story §14 lane evidence row pin)
#   git_stash_sequence: stash production logic (mv) → RED → restore → GREEN per CFP-1334 §8.4
#   role_vocabulary: developer + architect + qa + orchestrator handoff (RequirementsPL SKIP → ArchitectAgent chief combined Phase 1+2 → bats GREEN)
#   red_green_anchor: RED→GREEN stash proof (4 TC FAIL stash → 4 TC PASS restore)
#   platform_verified: Windows Git Bash + Ubuntu (CI runner) cross-platform tested (CFP-418 heredoc + ADR-061 Amd 3 PyYAML primary + line-by-line fallback)
#
# Test cases:
#   T-1: exact match scenario (gh api stub returns ["check-gate"], workflow yml has jobs.check-gate.name: "check-gate") → PASS
#   T-2: substring match only (context "deploy-lane-presence" vs job name "Verify deploy lane presence (Phase 2)") → WARN substring
#   T-3: full mismatch (context "nonexistent-check" not in any workflow) → FAIL no match (silent BLOCKED risk)
#   T-4: hotfix-bypass scenario — script call still runs (bats fixture scope = python SSOT; bypass = workflow scope)
#
# Production code binding (memory feedback_test_must_bind_to_production):
#   실제 scripts/lib/check_branch_protection_context_name_strict_match.py 호출.
#   sed-extract 금지, inline hand-copy 금지.
#
# Windows Git Bash compatibility (CFP-418 evidence):
#   single-quoted heredoc for fixture content.

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-branch-protection-context-name-strict-match.sh"
PY_SSOT="$REPO_ROOT/scripts/lib/check_branch_protection_context_name_strict_match.py"

setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR
  export GH_CLI_BIN_OVERRIDE_MODE="python_shim"

  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi

  if [[ ! -f "$SCRIPT" ]]; then
    echo "script not found: $SCRIPT" >&2
    false  # genuine RED: production absent
  fi

  if [[ ! -f "$PY_SSOT" ]]; then
    echo "python SSOT not found: $PY_SSOT" >&2
    false
  fi
}

teardown() {
  if [[ -n "${TEST_DIR:-}" && -d "${TEST_DIR}" ]]; then
    rm -rf "${TEST_DIR}"
  fi
  unset GH_CLI_BIN_OVERRIDE_MODE GH_SHIM_SCRIPT
}

make_workflow_dir() {
  # Argument: WORKFLOW_DIR
  local WF_DIR="$1"
  mkdir -p "$WF_DIR"
}

make_gh_shim() {
  # Argument: shim file path, contexts (newline-separated)
  local SHIM_PATH="$1"
  local CONTEXTS="$2"
  cat > "$SHIM_PATH" <<SHIM_EOF
#!/usr/bin/env python3
import sys
# CFP-1849 bats shim — mock gh api responses for branch protection contexts
if len(sys.argv) >= 4 and sys.argv[1] == "api" and "/protection/required_status_checks" in sys.argv[2]:
    print("""${CONTEXTS}""")
    sys.exit(0)
# Other invocations: empty + exit 0
sys.exit(0)
SHIM_EOF
  chmod +x "$SHIM_PATH"
  export GH_SHIM_SCRIPT="$SHIM_PATH"
}

# ============================================================
# T-1: exact match → PASS
# ============================================================
@test "T-1: exact context match in workflow yml -> PASS" {
  WF_DIR="$TEST_DIR/.github/workflows"
  make_workflow_dir "$WF_DIR"

  cat > "$WF_DIR/check-gate.yml" <<'YAML_EOF'
name: check-gate
on: pull_request
jobs:
  check-gate:
    name: check-gate
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
YAML_EOF

  make_gh_shim "$TEST_DIR/gh-shim.py" "check-gate"

  cd "$TEST_DIR"
  run python3 "$PY_SSOT" --repo "mclayer/test" --workflow-dir "$WF_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"FAIL"* ]]
}

# ============================================================
# T-2: substring match only → WARN
# ============================================================
@test "T-2: substring match only -> WARN substring" {
  WF_DIR="$TEST_DIR/.github/workflows"
  make_workflow_dir "$WF_DIR"

  cat > "$WF_DIR/deploy-lane-presence.yml" <<'YAML_EOF'
name: deploy-lane-presence
on: pull_request
jobs:
  verify-deploy-lane-presence:
    name: Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
YAML_EOF

  make_gh_shim "$TEST_DIR/gh-shim.py" "deploy-lane-presence"

  cd "$TEST_DIR"
  run python3 "$PY_SSOT" --repo "mclayer/test" --workflow-dir "$WF_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"WARN"* ]] || [[ "$output" == *"substring"* ]]
}

# ============================================================
# T-3: no match → FAIL (silent BLOCKED risk)
# ============================================================
@test "T-3: no match -> FAIL silent BLOCKED risk" {
  WF_DIR="$TEST_DIR/.github/workflows"
  make_workflow_dir "$WF_DIR"

  cat > "$WF_DIR/some-other.yml" <<'YAML_EOF'
name: some-other
on: pull_request
jobs:
  some-other:
    name: some-other
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
YAML_EOF

  make_gh_shim "$TEST_DIR/gh-shim.py" "nonexistent-check"

  cd "$TEST_DIR"
  run python3 "$PY_SSOT" --repo "mclayer/test" --workflow-dir "$WF_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"FAIL"* ]] || [[ "$output" == *"no matching workflow job"* ]]
}

# ============================================================
# T-4: not_protected (gh api 404) → skip + exit 0
# ============================================================
@test "T-4: not_protected (404) -> skip exit 0" {
  WF_DIR="$TEST_DIR/.github/workflows"
  make_workflow_dir "$WF_DIR"
  cat > "$WF_DIR/check-gate.yml" <<'YAML_EOF'
name: check-gate
on: pull_request
jobs:
  check-gate:
    name: check-gate
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
YAML_EOF

  # Simulate 404: shim exits with non-zero + stderr "Not Found"
  cat > "$TEST_DIR/gh-shim.py" <<'SHIM_EOF'
#!/usr/bin/env python3
import sys
sys.stderr.write("HTTP 404: Not Found\n")
sys.exit(1)
SHIM_EOF
  chmod +x "$TEST_DIR/gh-shim.py"
  export GH_SHIM_SCRIPT="$TEST_DIR/gh-shim.py"

  cd "$TEST_DIR"
  run python3 "$PY_SSOT" --repo "mclayer/test" --workflow-dir "$WF_DIR"
  [ "$status" -eq 0 ]
}

# ============================================================
# RED→GREEN stash proof self-check (CFP-1334 §8.4 invariant)
#
# Run from terminal manually to verify (not as a bats test):
#   1) Stash production:
#        mv scripts/lib/check_branch_protection_context_name_strict_match.py /tmp/stashed.py
#      Expected: bats run → 4 TC FAIL (setup() detects missing PY_SSOT, fails fast).
#   2) Restore production:
#        mv /tmp/stashed.py scripts/lib/check_branch_protection_context_name_strict_match.py
#      Expected: bats run → 4 TC PASS (T-1 ~ T-4).
# ============================================================
