#!/usr/bin/env bats
# tests/scripts/test_check_retro_alerts.bats
# CFP-628 Story 2 — check-retro-alerts.sh unit tests (TDD)
# Change Plan §3.4 Layer (c) #1 + §8 Test Contract verbatim — 4 TC

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-retro-alerts.sh"

# gh stub helper — stub GH_STUB_FILE 경로의 JSON 을 stdout 출력
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR
  # stub gh binary
  export PATH="$TEST_DIR/bin:$PATH"
  mkdir -p "$TEST_DIR/bin"

  # gh stub: 환경변수 GH_STUB_RESPONSE 파일 경로 → cat 출력
  cat > "$TEST_DIR/bin/gh" <<'STUB'
#!/usr/bin/env bash
# bats gh stub — returns content of $GH_STUB_RESPONSE_FILE
if [ -n "$GH_STUB_RESPONSE_FILE" ] && [ -f "$GH_STUB_RESPONSE_FILE" ]; then
  cat "$GH_STUB_RESPONSE_FILE"
else
  echo "[]"
fi
STUB
  chmod +x "$TEST_DIR/bin/gh"

  # jq 가 없는 환경 대비 — 실제 jq 경로 확인
  if ! command -v jq &>/dev/null; then
    skip "jq not available"
  fi
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------
# TC-1: no open phase:완료 issue → exit 0 (no alert)
# ------------------------------------------------------------------
@test "TC-1: no open issue → exit 0" {
  # gh stub returns empty issue list
  export GH_STUB_RESPONSE_FILE="$TEST_DIR/stub_empty.json"
  echo '[]' > "$TEST_DIR/stub_empty.json"

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
}

# ------------------------------------------------------------------
# TC-2: open issue with [PMO] retro alert comment (created_at > 35min) → exit 1
# ------------------------------------------------------------------
@test "TC-2: open issue with [PMO] retro alert (created_at > 35min) → exit 1" {
  # 현재 시각에서 36분 전 타임스탬프 (2160초 전)
  OLD_TS="$(date -u -d '36 minutes ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-36M '+%Y-%m-%dT%H:%M:%SZ')"

  export GH_STUB_RESPONSE_FILE="$TEST_DIR/stub_alert.json"
  cat > "$TEST_DIR/stub_alert.json" <<JSON
[
  {
    "number": 101,
    "title": "CFP-999 Story 1",
    "comments": [
      {
        "body": "[PMO] retro alert: retro file not detected after 35min",
        "created_at": "$OLD_TS"
      }
    ]
  }
]
JSON

  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" == *"retro alert"* ]] || [[ "$output" == *"[PMO]"* ]]
}

# ------------------------------------------------------------------
# TC-3: open issue with [PMO] retro alert (created_at < 35min) → exit 0 (filter)
# ------------------------------------------------------------------
@test "TC-3: open issue with [PMO] retro alert (created_at < 35min) → exit 0 (filter)" {
  # 현재 시각에서 10분 전 타임스탬프 (600초 전) — 35min 미만 = retry 진행 중
  RECENT_TS="$(date -u -d '10 minutes ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-10M '+%Y-%m-%dT%H:%M:%SZ')"

  export GH_STUB_RESPONSE_FILE="$TEST_DIR/stub_recent.json"
  cat > "$TEST_DIR/stub_recent.json" <<JSON
[
  {
    "number": 102,
    "title": "CFP-998 Story 2",
    "comments": [
      {
        "body": "[PMO] retro alert: retro file not detected after 35min",
        "created_at": "$RECENT_TS"
      }
    ]
  }
]
JSON

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
}

# ------------------------------------------------------------------
# TC-4: open issue with [PMO] Retro automation failed (ESCALATE prefix) → exit 0
# TC-4 는 ESCALATE comment (별 prefix) — pickup 대상 아님 → exit 0
# ------------------------------------------------------------------
@test "TC-4: open issue with [PMO] Retro automation failed → exit 0 (별 prefix, ESCALATE)" {
  OLD_TS="$(date -u -d '60 minutes ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-60M '+%Y-%m-%dT%H:%M:%SZ')"

  export GH_STUB_RESPONSE_FILE="$TEST_DIR/stub_escalate.json"
  cat > "$TEST_DIR/stub_escalate.json" <<JSON
[
  {
    "number": 103,
    "title": "CFP-997 Story 3",
    "comments": [
      {
        "body": "[PMO] Retro automation failed after 3 retries. Please create retro manually.",
        "created_at": "$OLD_TS"
      }
    ]
  }
]
JSON

  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
}
