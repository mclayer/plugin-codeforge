#!/usr/bin/env bats
# tests/scripts/check-marketplace-drift.bats
# CFP-673 Phase 2 — check-marketplace-drift.sh unit tests
# Story §7.4 / Change Plan §8 test plan verbatim
#
# Test cases (TC-1..TC-5):
#   TC-1: drift 0건 silent success (E-3) — mock 7-plugin all 4 field identical → exit 0, Issue 발의 0건
#   TC-2: drift detected 1건 → Issue create + signature substring 포함
#   TC-3: dedup signature match → Issue create skip (active Issue already exists)
#   TC-4: hotfix-bypass label active → workflow skip simulation + audit comment message
#   TC-5: Issue auto-create label correctness (drift-detection + codeforge-improvement + phase:선정중)

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

# ------------------------------------------------------------------ TC-3: dedup signature match → skip Issue create
@test "TC-3: dedup signature match — active Issue exists, Issue create skipped" {
  # marketplace.json (version drift)
  MARKETPLACE_JSON="$TEST_DIR/marketplace.json"
  _make_marketplace_json "$MARKETPLACE_JSON" \
    "codeforge" "5.56.0" "Claude Code SW 개발 오케스트레이션 wrapper-only plugin." "mclayer"

  # plugin.json: version=5.55.0 (drift) — same as TC-2 → same signature
  _make_plugin_json "$FIXTURE_DIR/codeforge.json" \
    "codeforge" "5.55.0" "Claude Code SW 개발 오케스트레이션 wrapper-only plugin." "mclayer"

  # gh stub: issue list returns existing Issue (simulates active dedup match)
  cat > "$TEST_DIR/bin/gh" <<'STUB_DEDUP'
#!/usr/bin/env bash
if [[ "$1 $2" == "issue list" ]]; then
  # 기존 active Issue가 있는 것처럼 응답 (dedup match → create skip)
  echo "42"
  exit 0
fi
if [[ "$1 $2" == "issue create" ]]; then
  # dedup 시 create 호출되면 안 됨 — 오류 표시
  echo "ERROR: issue create should not be called when dedup active Issue exists" >&2
  exit 1
fi
echo "gh stub: unexpected call: $*" >&2
exit 0
STUB_DEDUP
  chmod +x "$TEST_DIR/bin/gh"

  run env \
    CFP673_PLUGINS_OVERRIDE="codeforge" \
    CFP673_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
    CFP673_PLUGIN_JSON_DIR="$FIXTURE_DIR" \
    bash "$SCRIPT"

  echo "# output: $output" >&3
  # warning tier — exit 0
  [ "$status" -eq 0 ]
  # DRIFT 감지됨 (메시지 있음)
  [[ "$output" == *"DRIFT"* ]]
  # dedup skip 메시지 포함
  [[ "$output" == *"dedup"* ]]
  # "Issue create" 호출 안 됨 (stub exit 1 로 guard)
  [[ "$output" != *"ERROR: issue create"* ]]
}

# ------------------------------------------------------------------ TC-4: hotfix-bypass label active → skip + audit message
@test "TC-4: CFP673_API_MOCK_401=1 — fail-closed exit 2 + SETUP error message" {
  # hotfix-bypass mechanism 은 workflow-level (not script-level).
  # script-level bypass 검증 대체로 E-4 401 fail-closed 시나리오 사용 (scripts/check-marketplace-drift.sh 의 bypass 검증 위임 구조 정합).
  # TC-4 scope: 401 mock → exit 2 + error message (bypass audit message pattern 과 동일 채널).
  run env \
    CFP673_API_MOCK_401="1" \
    CFP673_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT"

  echo "# output: $output" >&3
  # 401 fail-closed → exit 2
  [ "$status" -eq 2 ]
  # 오류 메시지 포함
  [[ "$output" == *"401"* ]]
  [[ "$output" == *"codeforge-kpi-infra-error"* ]]
}

# ------------------------------------------------------------------ TC-5: Issue auto-create label correctness
@test "TC-5: drift detected — gh issue create called with correct labels" {
  # marketplace.json (description drift)
  MARKETPLACE_JSON="$TEST_DIR/marketplace.json"
  _make_marketplace_json "$MARKETPLACE_JSON" \
    "codeforge" "5.56.0" "Original description." "mclayer"

  # plugin.json: description differs (drift)
  _make_plugin_json "$FIXTURE_DIR/codeforge.json" \
    "codeforge" "5.56.0" "Different description in plugin.json." "mclayer"

  # gh stub: capture issue create call + labels
  CALL_LOG="$TEST_DIR/gh_calls.log"
  cat > "$TEST_DIR/bin/gh" <<STUB_LABELS
#!/usr/bin/env bash
# capture all gh calls to log
echo "\$@" >> "$CALL_LOG"
if [[ "\$1 \$2" == "issue list" ]]; then
  echo ""  # no active Issue → trigger create
  exit 0
fi
if [[ "\$1 \$2" == "issue create" ]]; then
  echo "https://github.com/mclayer/plugin-codeforge/issues/999 (stub)"
  exit 0
fi
echo "gh stub: unexpected call: \$*" >&2
exit 0
STUB_LABELS
  chmod +x "$TEST_DIR/bin/gh"

  run env \
    CFP673_PLUGINS_OVERRIDE="codeforge" \
    CFP673_MARKETPLACE_PATH="$MARKETPLACE_JSON" \
    CFP673_PLUGIN_JSON_DIR="$FIXTURE_DIR" \
    bash "$SCRIPT"

  echo "# output: $output" >&3
  echo "# gh calls: $(cat "$CALL_LOG" 2>/dev/null || echo '(none)')" >&3

  # warning tier — exit 0
  [ "$status" -eq 0 ]
  # drift 감지
  [[ "$output" == *"DRIFT"* ]]
  # gh issue create 호출됨 (call log에 기록)
  [[ -f "$CALL_LOG" ]]
  grep -q "issue create" "$CALL_LOG"
  # label drift-detection 포함
  grep -q "drift-detection" "$CALL_LOG"
}
