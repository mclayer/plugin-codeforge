#!/usr/bin/env bats
# tests/scripts/check-3way-version-parity/check-3way-version-parity.bats
# CFP-820 Phase 2 — check-3way-version-parity.sh bats tests
# Story §5.2 AC-9 + Change Plan §8.1 TC-1..TC-14 (14 discriminating TC)
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

@test "TC-8: marketplace fetch empty-blob (size≤40000) → exit 2 + truncated/empty msg" {
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
