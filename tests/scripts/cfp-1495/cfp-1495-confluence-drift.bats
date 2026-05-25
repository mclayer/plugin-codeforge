#!/usr/bin/env bats
# tests/scripts/cfp-1495/cfp-1495-confluence-drift.bats
# CFP-1495 / ADR-103 §결정 1 영역 — confluence-drift-detection mechanical lint TDD fixture
#
# TC map (6 TC, AC-5 5+ TC 정합):
#
# TC-1: IA tree 부재 → exit 2 (SETUP error, _emit_error path)
# TC-2: IA tree 0 page entry → exit 0 + warning emit (nothing to check)
# TC-3: MCP-direct mode (no token, no mock fixture) → exit 0 + per-page silent skip warning
# TC-4: mock fixture + drift threshold exceeded (timestamp > 7 day) → exit 0 + drift warning + Issue skip mode
# TC-5: mock fixture + title mismatch → exit 0 + drift warning (title axis)
# TC-6: mock fixture + 3-anchor stamp 부착 → exempt (no drift emit even on synthetic mismatch)
#
# 3-layer defense (always-pass pattern 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — discriminating fixture (script 미존재 → RED, exit code 정확 검증)
#   Layer 3 — sandbox 격리 (임시 dir, 실제 git repo 접촉 없음)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CFP1495_SKIP_ISSUE_CREATE=1
#
# ADR refs: ADR-103 §결정 1 영역 (Confluence-mirror sync mechanism — drift detection 영역),
#           ADR-060 (warning tier evidence-enforceable),
#           ADR-061 (bash thin wrapper + Python SSOT split),
#           ADR-082 §결정 11.A (RED→GREEN stash proof)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="$WORKTREE_ROOT/scripts/check-confluence-drift.sh"
PY_SSOT="$WORKTREE_ROOT/scripts/lib/check_confluence_drift.py"

# ──────────────────────────────────── sandbox setup ────────────────────────────────────────────

setup_file() {
  export CFP1495_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CFP1495_SKIP_ISSUE_CREATE
}

setup() {
  export CFP1495_SKIP_ISSUE_CREATE=1
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # 스크립트 + Python SSOT 를 $TEST_DIR/scripts/ + $TEST_DIR/scripts/lib/ 에 복사
  mkdir -p "$TEST_DIR/scripts/lib"
  cp "$SCRIPT" "$TEST_DIR/scripts/check-confluence-drift.sh"
  cp "$PY_SSOT" "$TEST_DIR/scripts/lib/check_confluence_drift.py"
  chmod +x "$TEST_DIR/scripts/check-confluence-drift.sh"
  chmod +x "$TEST_DIR/scripts/lib/check_confluence_drift.py"

  SCRIPT_UNDER_TEST="$TEST_DIR/scripts/check-confluence-drift.sh"
  export SCRIPT_UNDER_TEST

  # git repo 초기화 (git log -1 --format=%ct 정확도용)
  git -C "$TEST_DIR" init --quiet
  git -C "$TEST_DIR" config user.email "test@example.com"
  git -C "$TEST_DIR" config user.name "Test"

  # docs/ dir 초기화
  mkdir -p "$TEST_DIR/docs"
}

teardown() {
  if [[ -n "${TEST_DIR:-}" && -d "$TEST_DIR" ]]; then
    rm -rf "$TEST_DIR"
  fi
}

# ──────────────────────────────────── TC-1: IA tree 부재 → exit 2 ────────────────────────────────────

@test "TC-1: IA tree schema 부재 시 exit 2 (SETUP error)" {
  cd "$TEST_DIR"
  export CFP1495_IA_TREE_PATH="docs/confluence-ia-tree.yaml"  # 부재

  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 2 ]
  [[ "$output" == *"IA tree schema not found"* ]]
}

# ──────────────────────────────────── TC-2: 0 page entry → exit 0 + warning ──────────────────

@test "TC-2: IA tree 0 page entry 시 exit 0 + 'nothing to check' warning" {
  cd "$TEST_DIR"
  cat > "$TEST_DIR/docs/confluence-ia-tree.yaml" <<'YAML'
schema_version: "1.0"
ia_axis: per-plugin-top-level
pages: []
YAML
  export CFP1495_IA_TREE_PATH="$TEST_DIR/docs/confluence-ia-tree.yaml"

  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 0 ]
  [[ "$output" == *"0 page entries"* ]] || [[ "$output" == *"nothing to check"* ]]
}

# ──────────────────────────────────── TC-3: MCP-direct mode (silent skip) ───────────────────

@test "TC-3: MCP-direct mode (no token, no mock) → exit 0 + silent skip warning per page" {
  cd "$TEST_DIR"
  cat > "$TEST_DIR/docs/confluence-ia-tree.yaml" <<'YAML'
schema_version: "1.0"
ia_axis: per-plugin-top-level
pages:
  - page_id: "2098238"
    title: codeforge-requirements
    source_path: docs/architecture/codeforge-requirements.md
YAML
  export CFP1495_IA_TREE_PATH="$TEST_DIR/docs/confluence-ia-tree.yaml"
  unset ATLASSIAN_API_TOKEN || true

  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 0 ]
  # MCP-direct mode = silent skip (warning emit), PASS message 1건 emit
  [[ "$output" == *"PASS"* ]] || [[ "$output" == *"MCP-direct"* ]] || [[ "$output" == *"ATLASSIAN_API_TOKEN absent"* ]]
}

# ──────────────────────────────────── TC-4: mock drift timestamp delta > 7 day ─────────

@test "TC-4: mock fixture + timestamp delta > 7 day → drift warning emit (axis: timestamp)" {
  cd "$TEST_DIR"
  # IA tree with 1 page + source file
  mkdir -p "$TEST_DIR/docs/architecture"
  echo "test content" > "$TEST_DIR/docs/architecture/codeforge-requirements.md"
  git -C "$TEST_DIR" add docs/architecture/codeforge-requirements.md
  git -C "$TEST_DIR" commit --quiet -m "add source file"

  # git timestamp = now (recent), confluence cf timestamp = 30 day ago (drift)
  cat > "$TEST_DIR/docs/confluence-ia-tree.yaml" <<YAML
schema_version: "1.0"
ia_axis: per-plugin-top-level
pages:
  - page_id: "2098238"
    title: codeforge-requirements
    source_path: docs/architecture/codeforge-requirements.md
YAML

  # mock fixture: confluence side stale by 30 day
  OLD_TS=$(($(date +%s) - 30 * 86400))
  cat > "$TEST_DIR/mock-fixture.json" <<JSON
{
  "2098238": {
    "version": 1,
    "last_modified_ts": ${OLD_TS},
    "title": "codeforge-requirements",
    "anchors": {}
  }
}
JSON

  export CFP1495_IA_TREE_PATH="$TEST_DIR/docs/confluence-ia-tree.yaml"
  export CFP1495_MOCK_DRIFT_FIXTURE="$TEST_DIR/mock-fixture.json"
  export CFP1495_DRIFT_THRESHOLD_DAYS=7

  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 0 ]
  [[ "$output" == *"drift_type=timestamp"* ]]
  [[ "$output" == *"signature="* ]]
}

# ──────────────────────────────────── TC-5: mock title mismatch ─────────────────────────────

@test "TC-5: mock fixture + title mismatch → drift warning emit (axis: title)" {
  cd "$TEST_DIR"
  mkdir -p "$TEST_DIR/docs/architecture"
  echo "test" > "$TEST_DIR/docs/architecture/codeforge-design.md"
  git -C "$TEST_DIR" add docs/architecture/codeforge-design.md
  git -C "$TEST_DIR" commit --quiet -m "add"

  cat > "$TEST_DIR/docs/confluence-ia-tree.yaml" <<'YAML'
schema_version: "1.0"
ia_axis: per-plugin-top-level
pages:
  - page_id: "2163460"
    title: codeforge-design
    source_path: docs/architecture/codeforge-design.md
YAML

  NOW_TS=$(date +%s)
  cat > "$TEST_DIR/mock-fixture.json" <<JSON
{
  "2163460": {
    "version": 1,
    "last_modified_ts": ${NOW_TS},
    "title": "codeforge-design-OLD-DRIFTED-NAME",
    "anchors": {}
  }
}
JSON

  export CFP1495_IA_TREE_PATH="$TEST_DIR/docs/confluence-ia-tree.yaml"
  export CFP1495_MOCK_DRIFT_FIXTURE="$TEST_DIR/mock-fixture.json"

  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 0 ]
  [[ "$output" == *"drift_type=title"* ]]
  [[ "$output" == *"signature="* ]]
}

# ──────────────────────────────────── TC-6: 3-anchor stamp 부착 = exempt ─────────────────

@test "TC-6: mock fixture + 3-anchor stamp 부착 → exempt (no drift emit even on title mismatch)" {
  cd "$TEST_DIR"
  mkdir -p "$TEST_DIR/docs/architecture"
  echo "test" > "$TEST_DIR/docs/architecture/codeforge-pmo.md"
  git -C "$TEST_DIR" add docs/architecture/codeforge-pmo.md
  git -C "$TEST_DIR" commit --quiet -m "add"

  cat > "$TEST_DIR/docs/confluence-ia-tree.yaml" <<'YAML'
schema_version: "1.0"
ia_axis: per-plugin-top-level
pages:
  - page_id: "2065649"
    title: codeforge-pmo
    source_path: docs/architecture/codeforge-pmo.md
YAML

  # mock fixture: title intentionally mismatched, BUT 3-anchor stamps present → exempt
  NOW_TS=$(date +%s)
  cat > "$TEST_DIR/mock-fixture.json" <<JSON
{
  "2065649": {
    "version": 1,
    "last_modified_ts": ${NOW_TS},
    "title": "intentionally-different-but-exempt",
    "anchors": {
      "codeforge_hash_git_source": "abc123",
      "codeforge_sync_commit_sha": "def456"
    }
  }
}
JSON

  export CFP1495_IA_TREE_PATH="$TEST_DIR/docs/confluence-ia-tree.yaml"
  export CFP1495_MOCK_DRIFT_FIXTURE="$TEST_DIR/mock-fixture.json"

  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 0 ]
  # 3-anchor stamp 부착 영역 = exempt → drift_type 미출현
  [[ "$output" != *"drift_type=title"* ]]
  [[ "$output" != *"drift_type=timestamp"* ]]
  [[ "$output" == *"PASS"* ]]
}
