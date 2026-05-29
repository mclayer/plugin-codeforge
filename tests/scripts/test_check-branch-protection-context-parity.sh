#!/usr/bin/env bats
# tests/scripts/test_check-branch-protection-context-parity.sh
# CFP-1807 — branch-protection-context-parity bats fixture (Wave 2 mechanical wire)
# ADR-024 §결정 6.A / ADR-060 §결정 5 warning-tier default
# CFP-1334 §8.4 precedent — RED→GREEN stash proof pattern
#
# Test cases:
#   T-1: 8 plugin family list closed-enum sentinel (PLUGIN_FAMILY constant verbatim)
#   T-2: parity PASS scenario (mock gh CLI with byte-identical contexts) → exit 0 + 0 warning
#   T-3: parity FAIL scenario (mock with drift) → exit 0 (warning-tier) + warning markdown table emit
#   T-4: hotfix-bypass label present → workflow skip + audit comment (workflow-level, this fixture covers script invariants only)
#
# Production code binding (memory feedback_test_must_bind_to_production):
#   실제 scripts/lib/check_branch_protection_context_parity.py 호출.
#   sed-extract 금지, inline hand-copy 금지.
#
# Mock strategy:
#   gh CLI = shim in TEST_DIR/bin prepended to PATH; emits stub contexts per slug.
#   CLAUDE.md = fixture override via --claude-md flag.
#   --plugins flag restricts to mock-able subset for deterministic test.
#
# Windows Git Bash compatibility (CFP-418 evidence):
#   single-quoted heredoc for fixture content.

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-branch-protection-context-parity.sh"
PY_SSOT="$REPO_ROOT/scripts/lib/check_branch_protection_context_parity.py"

setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

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

  # CLAUDE.md fixture — minimal table reproducing 6 lane plugin SSOT structure
  cat > "$TEST_DIR/CLAUDE.md" <<'CLAUDE_MD_EOF'
# Test CLAUDE.md fixture

Some prefix content.

**6 lane plugin branch protection contexts SSOT (test fixture)**: anchor line.

| plugin | required_status_checks contexts | 비고 |
|--------|--------------------------------|------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","check-gate"]` | wrapper |
| codeforge-design | `["phase-gate-mergeable","check-gate"]` | — |
| codeforge-test | `["phase-gate-mergeable","check-gate"]` | — |
| codeforge-deploy | NOT PROTECTED | new |

After table content.
CLAUDE_MD_EOF

  # gh CLI shim — emits stubbed contexts based on SLUG path.
  # GH_SHIM_RESPONSES file controls response per slug.
  # Windows: Python subprocess.run CreateProcess cannot exec .sh directly;
  # we use a Python shim script (gh_shim.py) and route via GH_CLI_BIN env override.
  mkdir -p "$TEST_DIR/bin"
  cat > "$TEST_DIR/bin/gh_shim.py" <<'GH_SHIM_EOF'
#!/usr/bin/env python3
# gh CLI shim for CFP-1807 bats fixture (Python — cross-platform; Windows CreateProcess compatible)
# Reads response from GH_SHIM_RESPONSES env (JSON: { "owner/repo": ["ctx1","ctx2"] } or "404")
# Mocks: `gh api repos/<owner>/<repo>/branches/main/protection/required_status_checks --jq '.contexts[]'`
import json
import os
import re
import sys

argv = sys.argv[1:]
if len(argv) >= 2 and argv[0] == "api":
    m = re.match(r"^repos/(.+)/branches/main/protection/required_status_checks$", argv[1])
    if m:
        slug = m.group(1)
        responses_path = os.environ.get("GH_SHIM_RESPONSES", "")
        if not responses_path or not os.path.isfile(responses_path):
            print("Not Found (HTTP 404)", file=sys.stderr)
            sys.exit(1)
        with open(responses_path) as f:
            data = json.load(f)
        v = data.get(slug)
        if v == "404" or v is None:
            print("Not Found (HTTP 404)", file=sys.stderr)
            sys.exit(1)
        for c in v:
            print(c)
        sys.exit(0)

print(f"shim: unsupported gh invocation: {argv}", file=sys.stderr)
sys.exit(127)
GH_SHIM_EOF

  # Wrapper: subprocess.run(GH_CLI_BIN) must be directly executable.
  # We invoke python3 explicitly via a one-line wrapper script that subprocess.run can exec.
  # Approach: GH_CLI_BIN points to python3 itself; first arg is the shim script.
  # Production script then issues: [python3, gh_shim.py, "api", "repos/...", "--jq", ".contexts[]"]
  # The shim ignores "--jq" trailing args.
  python_exe="$(command -v python3)"
  if [ -z "$python_exe" ]; then
    skip "python3 not on PATH"
  fi
  # CFP-1807: we override GH_CLI_BIN to invoke python3 directly with the shim script.
  # Production script signature: subprocess.run([GH_CLI_BIN, "api", "<endpoint>", "--jq", ".contexts[]"])
  # → we need GH_CLI_BIN to be an executable that prepends `gh_shim.py` as effective arg.
  # Simplest: wrap python3 + shim invocation in a bash script invoked via cmd /c on Windows.
  # Alternative simpler: set GH_CLI_BIN_PRELUDE so production prepends args.
  # We use the prelude approach — modify production to support it (already done if needed).
  export GH_SHIM_SCRIPT="$TEST_DIR/bin/gh_shim.py"
  export GH_CLI_BIN_OVERRIDE_MODE="python_shim"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ───────────────────────────────────────────────────────────── T-1
@test "T-1: PLUGIN_FAMILY constant = 9 plugin closed-enum (wrapper + 8 sibling, mclayer/plugin-codeforge-*)" {
  # Verify the constant defined in production script via temp probe script.
  # ADR-061 Amd 3 §결정 11 정합 — anchored simple read.
  # Use PYTHONPATH env (not sys.path.insert with embedded literal) to avoid Windows backslash escaping.
  cat > "$TEST_DIR/probe_plugin_family.py" <<'PROBE_EOF'
from check_branch_protection_context_parity import PLUGIN_FAMILY
print(len(PLUGIN_FAMILY))
for s in PLUGIN_FAMILY:
    print(s)
PROBE_EOF
  PYTHONPATH="$REPO_ROOT/scripts/lib" run python3 "$TEST_DIR/probe_plugin_family.py"
  [ "$status" -eq 0 ]
  # Count == 9 (wrapper + 8 lane plugin per CLAUDE.md Development Agent Team 표)
  # Pattern match (not literal eq) — accommodates Windows \r\n line endings.
  [[ "${lines[0]}" =~ ^9 ]]
  [[ "$output" == *"mclayer/plugin-codeforge"* ]]
  [[ "$output" == *"mclayer/plugin-codeforge-design"* ]]
  [[ "$output" == *"mclayer/plugin-codeforge-deploy-review"* ]]
}

# ───────────────────────────────────────────────────────────── T-2
@test "T-2: parity PASS — actual contexts == SSOT (3 plugin checked) → exit 0 + PASS message" {
  cat > "$TEST_DIR/responses.json" <<'JSON_EOF'
{
  "mclayer/plugin-codeforge": ["phase-gate-mergeable","invariant-check","check-gate"],
  "mclayer/plugin-codeforge-design": ["phase-gate-mergeable","check-gate"],
  "mclayer/plugin-codeforge-test": ["phase-gate-mergeable","check-gate"]
}
JSON_EOF
  export GH_SHIM_RESPONSES="$TEST_DIR/responses.json"

  run python3 "$PY_SSOT" \
    --claude-md "$TEST_DIR/CLAUDE.md" \
    --plugins mclayer/plugin-codeforge mclayer/plugin-codeforge-design mclayer/plugin-codeforge-test

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"WARNING"* ]]
  [[ "$output" != *"drift detected"* ]]
}

# ───────────────────────────────────────────────────────────── T-3
@test "T-3: parity FAIL — actual contexts has drift → exit 0 (warning-tier) + markdown table emit" {
  # codeforge-design SSOT expects `[phase-gate-mergeable, check-gate]` but actual has `[phase-gate-mergeable]` only
  cat > "$TEST_DIR/responses.json" <<'JSON_EOF'
{
  "mclayer/plugin-codeforge-design": ["phase-gate-mergeable"]
}
JSON_EOF
  export GH_SHIM_RESPONSES="$TEST_DIR/responses.json"

  run python3 "$PY_SSOT" \
    --claude-md "$TEST_DIR/CLAUDE.md" \
    --plugins mclayer/plugin-codeforge-design

  # warning tier: exit 0 even on drift
  [ "$status" -eq 0 ]
  [[ "$output" == *"WARNING"* ]]
  [[ "$output" == *"drift detected"* ]]
  # markdown table header
  [[ "$output" == *"| plugin |"* ]]
  [[ "$output" == *"check-gate"* ]]  # listed in missing column
  # ADR-060 §결정 5 warning tier footer
  [[ "$output" == *"ADR-060"* ]]
}

# ───────────────────────────────────────────────────────────── T-4
@test "T-4: NOT PROTECTED SSOT row + 404 actual → parity OK (no drift); SSOT protected + 404 actual → drift" {
  # codeforge-deploy SSOT = NOT PROTECTED, actual = 404 → parity OK
  cat > "$TEST_DIR/responses.json" <<'JSON_EOF'
{
  "mclayer/plugin-codeforge-deploy": "404"
}
JSON_EOF
  export GH_SHIM_RESPONSES="$TEST_DIR/responses.json"

  run python3 "$PY_SSOT" \
    --claude-md "$TEST_DIR/CLAUDE.md" \
    --plugins mclayer/plugin-codeforge-deploy

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]

  # Inverse: SSOT says protected (codeforge-design) but actual is 404 → drift
  cat > "$TEST_DIR/responses.json" <<'JSON_EOF'
{
  "mclayer/plugin-codeforge-design": "404"
}
JSON_EOF

  run python3 "$PY_SSOT" \
    --claude-md "$TEST_DIR/CLAUDE.md" \
    --plugins mclayer/plugin-codeforge-design

  [ "$status" -eq 0 ]
  [[ "$output" == *"WARNING"* ]]
  [[ "$output" == *"not_protected"* ]]
}
