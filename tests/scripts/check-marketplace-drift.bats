#!/usr/bin/env bats
# tests/scripts/check-marketplace-drift.bats
# CFP-673 Phase 2 sub-PR (a) — check-marketplace-drift.sh unit tests
# Story §7.4 / Change Plan §8 test plan verbatim
#
# Test cases (sub-PR (a) scope = TC-1 + TC-2 of 10 total):
#   TC-1: drift 0건 silent success (E-3) — mock 7-plugin all 4 field identical → exit 0, Issue 발의 0건
#   TC-2: drift detected 1건 → Issue create + signature substring 포함

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-marketplace-drift.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # jq 필수
  if ! command -v jq &>/dev/null; then
    skip "jq not available"
  fi

  # sha256sum or shasum 필수
  if ! command -v sha256sum &>/dev/null && ! command -v shasum &>/dev/null; then
    skip "sha256sum/shasum not available"
  fi

  # gh stub — Issue create 차단 (CFP673_SKIP_ISSUE_CREATE=1 우선, stub은 보험)
  mkdir -p "$TEST_DIR/bin"
  cat > "$TEST_DIR/bin/gh" <<'STUB'
#!/usr/bin/env bash
# gh stub for check-marketplace-drift.bats
# CFP673_SKIP_ISSUE_CREATE=1 이 설정되어 있으면 여기 도달하지 않아야 함
# 도달 시 dry-run 응답 (Issue 번호 0)
if [[ "$1 $2" == "issue list" ]]; then
  echo ""  # active issue 없음 = dedup skip
  exit 0
fi
if [[ "$1 $2" == "issue create" ]]; then
  echo "https://github.com/mclayer/plugin-codeforge/issues/0 (stub)"
  exit 0
fi
echo "gh stub: unexpected call: $*" >&2
exit 0
STUB
  chmod +x "$TEST_DIR/bin/gh"
  export PATH="$TEST_DIR/bin:$PATH"

  # plugin JSON fixture dir
  FIXTURE_DIR="$TEST_DIR/fixtures"
  mkdir -p "$FIXTURE_DIR"
  export FIXTURE_DIR
}

teardown() {
  rm -rf "$TEST_DIR"
}

# helper: marketplace.json with given plugins array (jq input)
_make_marketplace_json() {
  local path="$1"
  shift
  # 인자: plugin_name version description author_name (반복 4-tuple)
  local plugins_json="[]"
  while [[ $# -ge 4 ]]; do
    local pname="$1" pver="$2" pdesc="$3" pauthor="$4"
    shift 4
    plugins_json="$(echo "$plugins_json" | jq \
      --arg n "$pname" --arg v "$pver" --arg d "$pdesc" --arg a "$pauthor" \
      '. + [{name:$n, version:$v, description:$d, author:{name:$a}}]')"
  done
  jq -n --argjson plugins "$plugins_json" '{plugins:$plugins}' > "$path"
}

# helper: plugin.json fixture file
_make_plugin_json() {
  local path="$1" pname="$2" pver="$3" pdesc="$4" pauthor="$5"
  jq -n \
    --arg n "$pname" --arg v "$pver" --arg d "$pdesc" --arg a "$pauthor" \
    '{name:$n, version:$v, description:$d, author:{name:$a}}' > "$path"
}

# ------------------------------------------------------------------ TC-1: drift 0건 silent success
@test "TC-1: all 7 plugins 4-field identical — exit 0, no Issue created" {
  # marketplace.json 생성 (codeforge + 6 lane plugins, all identical)
  MARKETPLACE_JSON="$TEST_DIR/marketplace.json"
  _make_marketplace_json "$MARKETPLACE_JSON" \
    "codeforge"              "5.56.0" "Claude Code SW 개발 오케스트레이션 wrapper-only plugin." "mclayer" \
    "codeforge-requirements" "2.10.0" "codeforge requirements lane plugin."                    "mclayer" \
    "codeforge-design"       "3.5.0"  "codeforge design lane plugin."                          "mclayer" \
    "codeforge-review"       "4.2.0"  "codeforge review lane plugin."                          "mclayer" \
    "codeforge-develop"      "1.8.0"  "codeforge develop lane plugin."                         "mclayer" \
    "codeforge-test"         "1.3.0"  "codeforge test lane plugin."                            "mclayer" \
    "codeforge-pmo"          "2.1.0"  "codeforge pmo lane plugin."                             "mclayer"

  # 7 plugin.json fixture 생성 (marketplace와 동일 값)
  _make_plugin_json "$FIXTURE_DIR/codeforge.json"              "codeforge"              "5.56.0" "Claude Code SW 개발 오케스트레이션 wrapper-only plugin." "mclayer"
  _make_plugin_json "$FIXTURE_DIR/codeforge-requirements.json" "codeforge-requirements" "2.10.0" "codeforge requirements lane plugin."                    "mclayer"
  _make_plugin_json "$FIXTURE_DIR/codeforge-design.json"       "codeforge-design"       "3.5.0"  "codeforge design lane plugin."                          "mclayer"
  _make_plugin_json "$FIXTURE_DIR/codeforge-review.json"       "codeforge-review"       "4.2.0"  "codeforge review lane plugin."                          "mclayer"
  _make_plugin_json "$FIXTURE_DIR/codeforge-develop.json"      "codeforge-develop"      "1.8.0"  "codeforge develop lane plugin."                         "mclayer"
  _make_plugin_json "$FIXTURE_DIR/codeforge-test.json"         "codeforge-test"         "1.3.0"  "codeforge test lane plugin."                            "mclayer"
  _make_plugin_json "$FIXTURE_DIR/codeforge-pmo.json"          "codeforge-pmo"          "2.1.0"  "codeforge pmo lane plugin."                             "mclayer"

  run env \
    CFP673_PLUGINS_OVERRIDE="codeforge,codeforge-requirements,codeforge-design,codeforge-review,codeforge-develop,codeforge-test,codeforge-pmo" \
    CFP673_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
    CFP673_PLUGIN_JSON_DIR="$FIXTURE_DIR" \
    CFP673_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT"

  echo "# output: $output" >&3
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  # drift warning 없음
  [[ "$output" != *"DRIFT"* ]]
}

# ------------------------------------------------------------------ TC-2: drift detected 1건 → signature 포함
@test "TC-2: 1 plugin version field mismatch — exit 0 (warning tier), signature in output" {
  # marketplace.json (codeforge version differs from plugin.json)
  MARKETPLACE_JSON="$TEST_DIR/marketplace.json"
  _make_marketplace_json "$MARKETPLACE_JSON" \
    "codeforge" "5.56.0" "Claude Code SW 개발 오케스트레이션 wrapper-only plugin." "mclayer"

  # plugin.json: version=5.55.0 (drift)
  _make_plugin_json "$FIXTURE_DIR/codeforge.json" \
    "codeforge" "5.55.0" "Claude Code SW 개발 오케스트레이션 wrapper-only plugin." "mclayer"

  run env \
    CFP673_PLUGINS_OVERRIDE="codeforge" \
    CFP673_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
    CFP673_PLUGIN_JSON_DIR="$FIXTURE_DIR" \
    CFP673_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT"

  echo "# output: $output" >&3
  # warning tier — exit 0 even on drift
  [ "$status" -eq 0 ]
  # drift 감지 메시지
  [[ "$output" == *"DRIFT"* ]]
  # field=version 언급
  [[ "$output" == *"version"* ]]
  # signature substring 포함 의무 (16자 hex)
  [[ "$output" =~ signature=[0-9a-f]{16} ]]
}
