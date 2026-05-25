#!/usr/bin/env bats
# tests/scripts/check-3way-version-parity/check-3way-version-parity.bats
# CFP-820 Phase 2 — check-3way-version-parity.sh bats tests
# Story §5.2 AC-9 + Change Plan §8.1 TC-1..TC-14 (14 discriminating TC)
#   FIX iter 1: TC-15..TC-19 신설 (guards 4/5/6 + 5xx/network scenarios)
#   CFP-1541: TC-20..TC-21 신설 (cleanup carrier scenario + 1024B floor defense preserve)
# TDD: RED written before script exists — each assertion is discriminating (tautology 0)
#
# TC 분류 (Change Plan §8.1 + Story §5.2 AC-9):
#   TC-1:  AC-1      3-way all match → exit 0 + "3-way PASS"
#   TC-2:  AC-1      wrapper-only mismatch → exit 1 + "wrapper" named
#   TC-3:  AC-1      marketplace-only mismatch → exit 1 + "marketplace" named
#   TC-4:  AC-1      consumer-pin-only mismatch → exit 1 + "consumer pin" named
#   TC-5:  AC-1      3-way all mismatch → exit 1 + 3 layers named
#   TC-6:  AC-2      pin missing (absent) → exit 0 + warn + no FAIL
#   TC-7:  AC-3      hotfix-bypass label → exit 0 + skip + audit msg
#   TC-8:  AC-8      marketplace fetch empty-blob → exit 2 + "truncated/empty"
#   TC-9:  AC-13     4-field parity missing (author absent) → exit 2 + "schema drift"
#   TC-10: AC-9(j)   clean-env reproduce → exit 0 (same as TC-1 input, env-independent)
#   TC-11: §7.4(b)   pin malformed (no version field) → exit 2 + "malformed"
#   TC-12: §7.4(c)   marketplace 401 → exit 2 + "PAT" or "401" (fail-closed)
#   TC-13: §7.4(c)   marketplace 429 → exit 0 + warning (fail-open)
#   TC-14: §7.4(e)   version format mismatch (v5.81.0 vs 5.81.0) → exit 1 + format hint
#   TC-15: §7.4.1(4) sister plugin entries mutation → exit 2 + guard(4) FAIL
#   TC-16: §7.4.1(5) plugin.json multi-line edit anomaly → exit 1 + guard(5) FAIL
#   TC-17: §7.4.1(6) version collision (2 entries same version) → exit 2 + guard(6) FAIL
#   TC-18: §7.4(c)   5xx error then success on retry → exit 0 (recover)
#   TC-19: §7.4(c)   5xx persistent 3 retries exhausted → exit 2 (fail-closed)
#   TC-20: CFP-1541  cleanup_carrier mode (size=21696, ≥1024) → exit 0 PASS (cleanup not flagged)
#   TC-21: CFP-1541  cleanup_carrier_below_floor mode (size=512, <1024) → exit 2 (real truncation flagged)

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../../scripts/check-3way-version-parity.sh"

# ─────────────────────────────────────────────── setup / teardown ──

setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  if ! command -v jq &>/dev/null; then
    skip "jq not available"
  fi

  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi

  # Verify PyYAML available
  if ! python3 -c "import yaml" 2>/dev/null; then
    skip "PyYAML not available (pip install pyyaml)"
  fi

  # Create fixture files
  mkdir -p "$TEST_DIR/.claude-plugin"
  mkdir -p "$TEST_DIR/.claude/_overlay"

  # Default: healthy 3-way match at 5.81.0
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'EOF'
{
  "name": "codeforge",
  "version": "5.81.0",
  "description": "Test plugin",
  "author": "mclayer"
}
EOF

  # Consumer project.yaml with version_pin 5.81.0
  cat > "$TEST_DIR/.claude/_overlay/project.yaml" <<'EOF'
project:
  name: test-project
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TST
  codeowners:
    architect_team: "@testorg/architects"
    domain_expert_team: "@testorg/domain"
  discussions:
    domain_kb_category: "Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
codeforge:
  version_pin:
    version: "5.81.0"
EOF

  # gh stub — comprehensive handler for all gh sub-commands
  # Script calls:
  #   1. gh api repos/.../contents/...  → JSON object with .size field (metadata)
  #   2. gh api -H "Accept: application/vnd.github.raw" repos/.../... → raw content JSON
  mkdir -p "$TEST_DIR/bin"
  cat > "$TEST_DIR/bin/gh" <<'STUB'
#!/usr/bin/env bash
# gh stub for check-3way-version-parity.bats

GH_STUB_MODE="${GH_STUB_MODE:-normal}"

# auth status — always succeed
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo "github.com"
  echo "  Logged in to github.com account stub-user"
  exit 0
fi

if [[ "$1" != "api" ]]; then
  echo "gh stub: unexpected command: $*" >&2
  exit 0
fi

# Detect call type:
# - raw fetch: has "-H" flag (Accept: application/vnd.github.raw)
# - meta fetch: no -H flag (returns JSON object with .sha, .size)
IS_RAW=0
for arg in "$@"; do
  if [[ "$arg" == "-H" ]]; then
    IS_RAW=1
    break
  fi
done

case "$GH_STUB_MODE" in
  empty_blob)
    # Meta fetch: return JSON with size=100 (≤40000 → triggers empty_blob error)
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":100,"name":"marketplace.json"}'
    else
      echo ""
    fi
    exit 0
    ;;

  auth_fail_401)
    echo '{"message":"Bad credentials","documentation_url":"https://docs.github.com/rest"}' >&2
    exit 1
    ;;

  rate_limit_429)
    echo '{"message":"API rate limit exceeded","documentation_url":"https://docs.github.com/rest"}' >&2
    exit 1
    ;;

  schema_drift)
    # marketplace.json missing author field
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":99999,"name":"marketplace.json"}'
    else
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin"}]}'
    fi
    exit 0
    ;;

  marketplace_version_mismatch)
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":99999,"name":"marketplace.json"}'
    else
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.80.0","description":"Test plugin","author":"mclayer"}]}'
    fi
    exit 0
    ;;

  sister_mutation)
    # TC-15: first raw fetch returns normal sister entries, second raw fetch returns mutated sister
    # Track call count via GH_CALL_COUNT_FILE env (set by test setup)
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":99999,"name":"marketplace.json"}'
      exit 0
    fi
    CALL_COUNT_FILE="${GH_CALL_COUNT_FILE:-/tmp/gh_raw_call_count_default}"
    COUNT=0
    if [[ -f "$CALL_COUNT_FILE" ]]; then
      COUNT=$(cat "$CALL_COUNT_FILE")
    fi
    COUNT=$((COUNT + 1))
    echo "$COUNT" > "$CALL_COUNT_FILE"
    if [[ "$COUNT" -eq 1 ]]; then
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin","author":"mclayer"},{"name":"s1","version":"1.0","description":"s","author":"x"},{"name":"s2","version":"1.0","description":"s","author":"x"},{"name":"s3","version":"1.0","description":"s","author":"x"},{"name":"s4","version":"1.0","description":"s","author":"x"},{"name":"s5","version":"1.0","description":"s","author":"x"},{"name":"s6","version":"1.0","description":"s","author":"x"}]}'
    else
      # Second fetch: sister entry s6 mutated
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin","author":"mclayer"},{"name":"s1","version":"1.0","description":"s","author":"x"},{"name":"s2","version":"1.0","description":"s","author":"x"},{"name":"s3","version":"1.0","description":"s","author":"x"},{"name":"s4","version":"1.0","description":"s","author":"x"},{"name":"s5","version":"1.0","description":"s","author":"x"},{"name":"s6","version":"2.0","description":"MUTATED","author":"x"}]}'
    fi
    exit 0
    ;;

  version_collision)
    # TC-17: two entries share the same version string → guard (6) detects collision
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":99999,"name":"marketplace.json"}'
    else
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin","author":"mclayer"},{"name":"other-plugin","version":"5.81.0","description":"Other","author":"other"}]}'
    fi
    exit 0
    ;;

  server_error_then_recover)
    # TC-18: first meta call fails with 502, subsequent calls succeed
    # Use GH_CALL_COUNT_FILE env var for stable cross-invocation counting
    RECOVER_COUNT_FILE="${GH_CALL_COUNT_FILE:-/tmp/gh_recover_count_default}"
    COUNT=0
    if [[ -f "$RECOVER_COUNT_FILE" ]]; then
      COUNT=$(cat "$RECOVER_COUNT_FILE")
    fi
    COUNT=$((COUNT + 1))
    echo "$COUNT" > "$RECOVER_COUNT_FILE"
    if [[ "$COUNT" -eq 1 ]]; then
      # First call: 502 error (captured via 2>&1 in script)
      echo '502 Bad Gateway'
      exit 1
    fi
    # Subsequent calls: success (recovery)
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":99999,"name":"marketplace.json"}'
    else
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin","author":"mclayer"}]}'
    fi
    exit 0
    ;;

  server_error_persistent)
    # TC-19: all calls fail with 503 (persistent 5xx) → retry exhausted → exit 2
    echo '503 Service Unavailable' >&2
    exit 1
    ;;

  cleanup_carrier)
    # TC-20: CFP-1541 cleanup carrier scenario
    # marketplace.json shrunk legitimately to ~21KB (CFP-FU-B cleanup).
    # size=21696 which is > 1024 → guard (1) PASS (cleanup not flagged)
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":21696,"name":"marketplace.json"}'
    else
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin","author":"mclayer"}]}'
    fi
    exit 0
    ;;

  cleanup_carrier_below_floor)
    # TC-21: size < 1024 → guard (1) trip → exit 2 (real truncation flagged)
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":512,"name":"marketplace.json"}'
    else
      # Should not be reached — guard (1) trips before raw fetch
      echo ""
    fi
    exit 0
    ;;

  *)
    # normal — matching 5.81.0
    if [[ "$IS_RAW" -eq 0 ]]; then
      echo '{"sha":"abc123","size":99999,"name":"marketplace.json"}'
    else
      printf '{"schema_version":"1.0","plugins":[{"name":"codeforge","version":"5.81.0","description":"Test plugin","author":"mclayer"}]}'
    fi
    exit 0
    ;;
esac
STUB
  chmod +x "$TEST_DIR/bin/gh"
  export PATH="$TEST_DIR/bin:$PATH"

  export PLUGIN_JSON_PATH="$TEST_DIR/.claude-plugin/plugin.json"
  export CONSUMER_PROJECT_YAML_PATH="$TEST_DIR/.claude/_overlay/project.yaml"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ─────────────────────────────────────────── TC-1: 3-way all match ──

@test "TC-1: 3-way all match (wrapper=marketplace=consumer pin) → exit 0 + 3-way PASS" {
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "3-way PASS" ]] || [[ "$output" =~ "PASS" ]] || false
  [[ ! "$output" =~ "❌" ]] || false
}

# ────────────────────────────────── TC-2: wrapper-only mismatch ──

@test "TC-2: wrapper-only mismatch (wrapper≠marketplace=pin) → exit 1 + wrapper named" {
  cat > "$PLUGIN_JSON_PATH" <<'EOF'
{
  "name": "codeforge",
  "version": "5.99.0",
  "description": "Test plugin",
  "author": "mclayer"
}
EOF
  # marketplace stays 5.81.0 (stub normal), consumer pin stays 5.81.0
  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ [Ww]rapper || "$output" =~ "plugin.json" ]] || false
}

# ────────────────────────────── TC-3: marketplace-only mismatch ──

@test "TC-3: marketplace-only mismatch (marketplace≠wrapper=pin) → exit 1 + marketplace named" {
  export GH_STUB_MODE=marketplace_version_mismatch
  # wrapper = 5.81.0, consumer = 5.81.0, marketplace = 5.80.0
  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ [Mm]arketplace ]] || false
}

# ─────────────────────────────── TC-4: consumer-pin-only mismatch ──

@test "TC-4: consumer-pin-only mismatch (pin≠wrapper=marketplace) → exit 1 + consumer pin named" {
  cat > "$CONSUMER_PROJECT_YAML_PATH" <<'EOF'
project:
  name: test-project
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TST
  codeowners:
    architect_team: "@testorg/architects"
    domain_expert_team: "@testorg/domain"
  discussions:
    domain_kb_category: "Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
codeforge:
  version_pin:
    version: "5.80.0"
EOF
  # wrapper = 5.81.0, marketplace = 5.81.0, consumer pin = 5.80.0
  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ [Cc]onsumer || "$output" =~ "version_pin" || "$output" =~ "5.80.0" ]] || false
}

# ────────────────────────────────── TC-5: 3-way all mismatch ──

@test "TC-5: 3-way all mismatch → exit 1 + multiple layers named" {
  cat > "$PLUGIN_JSON_PATH" <<'EOF'
{
  "name": "codeforge",
  "version": "5.99.0",
  "description": "Test plugin",
  "author": "mclayer"
}
EOF
  export GH_STUB_MODE=marketplace_version_mismatch  # returns 5.80.0

  cat > "$CONSUMER_PROJECT_YAML_PATH" <<'EOF'
project:
  name: test-project
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TST
  codeowners:
    architect_team: "@testorg/architects"
    domain_expert_team: "@testorg/domain"
  discussions:
    domain_kb_category: "Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
codeforge:
  version_pin:
    version: "5.70.0"
EOF

  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "5.99.0" || "$output" =~ "5.80.0" || "$output" =~ "5.70.0" ]] || false
  # MISMATCH must appear (multiple failures)
  [[ "$output" =~ "MISMATCH" ]] || false
}

# ────────────────────── TC-6: pin absent → warning-first exit 0 ──

@test "TC-6: consumer pin absent → exit 0 + warn + no FAIL (orthogonality invariant)" {
  cat > "$CONSUMER_PROJECT_YAML_PATH" <<'EOF'
project:
  name: test-project
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TST
  codeowners:
    architect_team: "@testorg/architects"
    domain_expert_team: "@testorg/domain"
  discussions:
    domain_kb_category: "Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
# No codeforge.version_pin block
EOF

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" =~ [Ww]arn || "$output" =~ "미등록" || "$output" =~ "version_pin" || "$output" =~ "SKIPPED" ]] || false
  [[ ! "$output" =~ "❌" ]] || false
}

# ──────────────────────── TC-7: hotfix-bypass label → skip + audit ──

@test "TC-7: hotfix-bypass:version-3way-atomic label active → exit 0 + skip + audit" {
  export BYPASS_LABEL="hotfix-bypass:version-3way-atomic"

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" =~ [Ss]kip || "$output" =~ "bypass" || "$output" =~ "BYPASS" || "$output" =~ "skipped" ]] || false
  [[ "$output" =~ "audit" || "$output" =~ "24시간" || "$output" =~ "hotfix" || "$output" =~ "sync" ]] || false
}

# ──────────────────────── TC-8: marketplace empty-blob → exit 2 ──

@test "TC-8: marketplace fetch empty-blob (size=100, ≤1024) → exit 2 + truncated/empty msg" {
  export GH_STUB_MODE=empty_blob

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ [Tt]runcated || "$output" =~ [Ee]mpty || "$output" =~ "size" ]] || false
}

# ──────────────────── TC-9: 4-field parity missing → exit 2 + schema drift ──

@test "TC-9: marketplace 4-field parity missing (author absent) → exit 2 + schema drift" {
  export GH_STUB_MODE=schema_drift

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ [Ss]chema || "$output" =~ [Dd]rift || "$output" =~ "author" || "$output" =~ "parity" ]] || false
}

# ────────────────────── TC-10: clean-env reproduce (env-independent) ──

@test "TC-10: clean-env independent reproduce → exit 0 (TC-1 input, env independence)" {
  unset BYPASS_LABEL GH_STUB_MODE || true

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ ! "$output" =~ "❌" ]] || false
}

# ──────────────────── TC-11: pin malformed (no version field) → exit 2 ──

@test "TC-11: pin malformed (version field absent) → exit 2 + malformed actionable" {
  cat > "$CONSUMER_PROJECT_YAML_PATH" <<'EOF'
project:
  name: test-project
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TST
  codeowners:
    architect_team: "@testorg/architects"
    domain_expert_team: "@testorg/domain"
  discussions:
    domain_kb_category: "Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
codeforge:
  version_pin: {}
EOF

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ [Mm]alformed || "$output" =~ "version_pin" || "$output" =~ "no_version_field" ]] || false
}

# ──────────────── TC-12: marketplace 401 → exit 2 (fail-closed) ──

@test "TC-12: marketplace fetch 401 → exit 2 + PAT/401 error (fail-closed)" {
  export GH_STUB_MODE=auth_fail_401

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "PAT" || "$output" =~ "401" || "$output" =~ [Aa]uth || "$output" =~ [Cc]redential ]] || false
}

# ──────────────── TC-13: marketplace 429 → exit 0 (fail-open) ──

@test "TC-13: marketplace fetch 429 → exit 0 + warning (fail-open)" {
  export GH_STUB_MODE=rate_limit_429

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" =~ [Ww]arn || "$output" =~ "429" || "$output" =~ [Rr]ate || "$output" =~ "rate" ]] || false
}

# ──────────── TC-14: version format mismatch (v5.81.0 vs 5.81.0) → exit 1 ──

@test "TC-14: version format mismatch (v5.81.0 prefix vs 5.81.0) → exit 1 + format hint" {
  cat > "$CONSUMER_PROJECT_YAML_PATH" <<'EOF'
project:
  name: test-project
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TST
  codeowners:
    architect_team: "@testorg/architects"
    domain_expert_team: "@testorg/domain"
  discussions:
    domain_kb_category: "Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
codeforge:
  version_pin:
    version: "v5.81.0"
EOF

  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "v5.81.0" || "$output" =~ [Ff]ormat || "$output" =~ "exact" || "$output" =~ "5.81.0" ]] || false
}

# ── TC-15: sanity guard (4) sister plugin entries mutation → exit 2 ──

@test "TC-15: guard(4) sister plugin entries mutation detected → exit 2" {
  export GH_STUB_MODE=sister_mutation
  # Provide a stable cross-invocation counter file for the stub
  export GH_CALL_COUNT_FILE="$TEST_DIR/gh_call_count_tc15"
  rm -f "$GH_CALL_COUNT_FILE"

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "guard (4)" || "$output" =~ "sister" || "$output" =~ "mutation" ]] || false
}

# ── TC-16: sanity guard (5) plugin.json multi-line edit anomaly → exit 1 ──

@test "TC-16: guard(5) plugin.json multi-line edit anomaly → exit 1" {
  # Set up a minimal git repo inside TEST_DIR for git diff to work
  GUARD5_DIR="$TEST_DIR/git_repo_tc16"
  mkdir -p "$GUARD5_DIR/.claude-plugin" "$GUARD5_DIR/.claude/_overlay"

  # Copy read_version_pin.py so SCRIPT_DIR resolution works (SCRIPT_DIR = scripts/)
  # The script resolves READ_PIN_PY relative to its own dir — no need to copy here
  # since PLUGIN_JSON_PATH and CONSUMER_PROJECT_YAML_PATH are injected

  # Initial plugin.json
  cat > "$GUARD5_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "5.80.0",
  "description": "Old description",
  "author": "mclayer"
}
PJSON
  # Consumer project.yaml (version_pin matches marketplace stub 5.81.0 — pin check irrelevant here)
  cp "$CONSUMER_PROJECT_YAML_PATH" "$GUARD5_DIR/.claude/_overlay/project.yaml"

  # Init git repo and commit the initial state
  (
    cd "$GUARD5_DIR"
    git init -q
    git config user.email "test@test.com"
    git config user.name "Test"
    git config core.autocrlf false
    git add .
    git commit -q -m "init"
  )

  # Now make a multi-line change to plugin.json (>4 changed lines to trigger guard 5)
  cat > "$GUARD5_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "5.81.0",
  "description": "New description changed substantially here",
  "author": "mclayer",
  "extra_field": "injected_value"
}
PJSON

  export PLUGIN_JSON_PATH="$GUARD5_DIR/.claude-plugin/plugin.json"
  export CONSUMER_PROJECT_YAML_PATH="$GUARD5_DIR/.claude/_overlay/project.yaml"
  # Run from within GUARD5_DIR so git diff HEAD -- .claude-plugin/plugin.json resolves
  run bash -c "cd '$GUARD5_DIR' && bash '$SCRIPT'"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "guard (5)" || "$output" =~ "multi-line" || "$output" =~ "anomaly" ]] || false
}

# ── TC-17: sanity guard (6) version collision → exit 2 ──

@test "TC-17: guard(6) marketplace version collision (2 entries same version) → exit 2" {
  export GH_STUB_MODE=version_collision
  # stub returns codeforge + other-plugin both at 5.81.0 → guard(6) detects collision

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "guard (6)" || "$output" =~ "collision" || "$output" =~ "collision" ]] || false
}

# ── TC-18: 5xx error then success on retry → exit 0 (recover) ──

@test "TC-18: 5xx error then recover on retry → exit 0 (fail-closed-with-retry recover)" {
  export GH_STUB_MODE=server_error_then_recover
  # Provide stable cross-invocation counter file for stub
  export GH_CALL_COUNT_FILE="$TEST_DIR/gh_call_count_tc18"
  rm -f "$GH_CALL_COUNT_FILE"
  # First meta call fails with 502, subsequent calls succeed — overall PASS expected

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  # Should not emit a hard failure
  [[ ! "$output" =~ "retry 후 영속 실패" ]] || false
}

# ── TC-19: 5xx persistent retry exhausted → exit 2 (fail-closed) ──

@test "TC-19: 5xx persistent retry exhausted (3 retries) → exit 2 fail-closed" {
  export GH_STUB_MODE=server_error_persistent
  # All calls fail with 503 → exponential backoff 1s/2s/4s → exit 2

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "retry" || "$output" =~ "영속 실패" || "$output" =~ "fail-closed" ]] || false
}

# ── TC-20: cleanup_carrier mode (CFP-1541) — size=21696 ≥ 1024 → PASS ──

@test "TC-20: cleanup_carrier mode (marketplace.json ~21KB, ≥1024) → exit 0 PASS (cleanup not flagged)" {
  export GH_STUB_MODE=cleanup_carrier
  # CFP-FU-B post-cleanup marketplace.json size = 21696 bytes
  # With threshold 40000 (old): 21696 ≤ 40000 → false-positive exit 2
  # With threshold 1024 (new): 21696 > 1024 → PASS (cleanup not flagged)
  # Discriminating: verifies the paradox fix — cleanup legitimately shrunk file MUST not trip guard (1)

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ ! "$output" =~ "truncated" ]] || false
  [[ ! "$output" =~ "≤ 1024" ]] || false
}

# ── TC-21: cleanup_carrier_below_floor mode (size=512 < 1024) → exit 2 ──

@test "TC-21: cleanup_carrier_below_floor mode (size=512 < 1024 floor) → exit 2 (real truncation flagged)" {
  export GH_STUB_MODE=cleanup_carrier_below_floor
  # size=512 < 1024 floor → guard (1) trip → exit 2
  # Discriminating: verifies empty-blob defense is preserved at 1024B floor
  # (genuine garbage-binary / zero-byte fetch scenario)

  run bash "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "truncated" || "$output" =~ "≤ 1024" || "$output" =~ "size" ]] || false
}
