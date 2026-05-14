#!/usr/bin/env bats
# tests/scripts/test_check_marketplace_description_verbatim.bats
# CFP-631 Phase 2 — check-marketplace-description-verbatim.sh unit + integration tests
# Story §8.5 / Change Plan §8 test plan verbatim
#
# Test cases:
#   TC1: byte-identical PASS
#   TC2: trailing whitespace drift FAIL
#   TC3: missing plugin entry in marketplace FAIL
#   TC4: extra field in plugin.json (description unchanged) → PASS
#   TC5: escaped quote handling (quotes inside description)
#   TC6: multiline description
#   TC7: special characters (Unicode, Korean)
#   IT1: mock marketplace.json fixture — PASS case
#   IT2: mock marketplace.json fixture — length drift FAIL
#   IT3: mock marketplace.json fixture — exact first-char difference

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-marketplace-description-verbatim.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # jq 필수
  if ! command -v jq &>/dev/null; then
    skip "jq not available"
  fi

  # gh stub (marketplace fetch を local override で回避するので不要だが念のため)
  mkdir -p "$TEST_DIR/bin"
  cat > "$TEST_DIR/bin/gh" <<'STUB'
#!/usr/bin/env bash
# gh stub — should not be called when CFP631_MARKETPLACE_PATH is set
echo "gh stub called unexpectedly: $*" >&2
exit 2
STUB
  chmod +x "$TEST_DIR/bin/gh"
  export PATH="$TEST_DIR/bin:$PATH"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# helper: create plugin.json with given description
make_plugin_json() {
  local desc="$1"
  local path="$TEST_DIR/plugin.json"
  jq -n --arg desc "$desc" '{name:"codeforge",version:"1.0.0",description:$desc,author:{name:"Josh"}}' > "$path"
  echo "$path"
}

# helper: create marketplace.json with given description for plugin "codeforge"
make_marketplace_json() {
  local desc="$1"
  local path="$TEST_DIR/marketplace.json"
  jq -n --arg desc "$desc" '{plugins:[{name:"codeforge",version:"1.0.0",description:$desc,author:{name:"Josh"}}]}' > "$path"
  echo "$path"
}

# ------------------------------------------------------------------ TC1: byte-identical PASS
@test "TC1: byte-identical description → exit 0 PASS" {
  DESC="Claude Code SW 개발 오케스트레이션 wrapper-only plugin."
  PLUGIN_JSON="$(make_plugin_json "$DESC")"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC2: trailing whitespace drift FAIL
@test "TC2: trailing whitespace drift → exit 1 DRIFT" {
  DESC_PLUGIN="Claude Code SW 개발 오케스트레이션."
  DESC_MARKET="Claude Code SW 개발 오케스트레이션.  "  # trailing spaces

  PLUGIN_JSON="$(make_plugin_json "$DESC_PLUGIN")"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC_MARKET")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 1 ]
  [[ "$output" == *"DRIFT"* ]]
}

# ------------------------------------------------------------------ TC3: missing plugin entry FAIL
@test "TC3: missing plugin entry in marketplace → exit 1 FAIL" {
  DESC="Some description."
  PLUGIN_JSON="$(make_plugin_json "$DESC")"

  # marketplace.json with a different plugin name
  MARKETPLACE_JSON="$TEST_DIR/marketplace.json"
  jq -n '{plugins:[{name:"other-plugin",version:"1.0.0",description:"other",author:{name:"X"}}]}' > "$MARKETPLACE_JSON"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 1 ]
  [[ "$output" == *"not registered"* ]]
}

# ------------------------------------------------------------------ TC4: extra field in plugin.json (description unchanged) → PASS
@test "TC4: extra field in plugin.json, description unchanged → exit 0 PASS" {
  DESC="Same description for both."
  PLUGIN_JSON="$TEST_DIR/plugin.json"
  # plugin.json has extra field "keywords"
  jq -n --arg desc "$DESC" '{name:"codeforge",version:"1.0.0",description:$desc,author:{name:"Josh"},keywords:["a","b"]}' > "$PLUGIN_JSON"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC5: escaped quote handling
@test "TC5: description with double quotes → byte-identical PASS" {
  DESC='This description has "quoted" content and it'\''s fine.'
  PLUGIN_JSON="$(make_plugin_json "$DESC")"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC6: multiline description (newlines via \n in JSON)
@test "TC6: multiline description byte-identical → exit 0 PASS" {
  # jq -r で\nが実際の改行になる
  PLUGIN_JSON="$TEST_DIR/plugin.json"
  MARKETPLACE_JSON="$TEST_DIR/marketplace.json"
  # Use printf to get a real multiline string
  DESC="$(printf 'Line one.\nLine two.\nLine three.')"
  jq -n --arg desc "$DESC" '{name:"codeforge",version:"1.0.0",description:$desc,author:{name:"Josh"}}' > "$PLUGIN_JSON"
  jq -n --arg desc "$DESC" '{plugins:[{name:"codeforge",version:"1.0.0",description:$desc,author:{name:"Josh"}}]}' > "$MARKETPLACE_JSON"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC7: special characters (Unicode, Korean)
@test "TC7: Korean + Unicode description byte-identical → exit 0 PASS" {
  DESC="Claude Code SW 개발 오케스트레이션 wrapper-only plugin. ζ arc 완료 (CFP-40). 에이전트 0개. 🚀"
  PLUGIN_JSON="$(make_plugin_json "$DESC")"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC7b: Korean description drift
@test "TC7b: Korean description drift → exit 1 DRIFT" {
  DESC_PLUGIN="Claude Code SW 개발 오케스트레이션 wrapper."
  DESC_MARKET="Claude Code SW 개발 오케스트레이션 wrapper-only."  # 달라진 부분

  PLUGIN_JSON="$(make_plugin_json "$DESC_PLUGIN")"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC_MARKET")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 1 ]
  [[ "$output" == *"DRIFT"* ]]
}

# ------------------------------------------------------------------ IT1: integration — mock fixture PASS
@test "IT1: full fixture mock — byte-identical PASS" {
  LONG_DESC="$(python3 -c "print('CFP-631 description. ' * 100)")"

  PLUGIN_JSON="$(make_plugin_json "$LONG_DESC")"
  MARKETPLACE_JSON="$(make_marketplace_json "$LONG_DESC")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ IT2: integration — length drift FAIL
@test "IT2: fixture length drift — marketplace description longer → exit 1 DRIFT" {
  BASE_DESC="CFP-631 description."
  PLUGIN_JSON="$(make_plugin_json "$BASE_DESC")"
  MARKETPLACE_JSON="$(make_marketplace_json "${BASE_DESC} extra suffix added in marketplace.")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 1 ]
  [[ "$output" == *"DRIFT"* ]]
  # length difference should be reported
  [[ "$output" == *"chars"* ]]
}

# ------------------------------------------------------------------ IT3: integration — first-char difference
@test "IT3: fixture first-char difference → exit 1 DRIFT with position report" {
  DESC_PLUGIN="Aello World plugin description."
  DESC_MARKET="Hello World plugin description."  # 첫 글자 A→H

  PLUGIN_JSON="$(make_plugin_json "$DESC_PLUGIN")"
  MARKETPLACE_JSON="$(make_marketplace_json "$DESC_MARKET")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
  run bash "$SCRIPT"

  [ "$status" -eq 1 ]
  [[ "$output" == *"DRIFT"* ]]
  # first difference position should be reported
  [[ "$output" == *"First difference"* ]] || [[ "$output" == *"char position"* ]]
}

# ------------------------------------------------------------------ meta: setup error — plugin.json missing
@test "meta: missing plugin.json → exit 2 SETUP error" {
  CFP631_PLUGIN_JSON="/nonexistent/path/plugin.json" \
  CFP631_MARKETPLACE_PATH="/dev/null" \
  run bash "$SCRIPT"

  [ "$status" -eq 2 ]
  [[ "$output" == *"not found"* ]]
}

# ------------------------------------------------------------------ meta: setup error — marketplace path not found
@test "meta: marketplace override path not found → exit 2 SETUP error" {
  PLUGIN_JSON="$(make_plugin_json "Some description.")"

  CFP631_PLUGIN_JSON="$PLUGIN_JSON" \
  CFP631_MARKETPLACE_PATH="/nonexistent/marketplace.json" \
  run bash "$SCRIPT"

  [ "$status" -eq 2 ]
  [[ "$output" == *"not found"* ]]
}
