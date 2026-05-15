#!/usr/bin/env bash
# test-check-wrapper-managed-block.sh — CFP-702 D4 customization marker lint self-test
# QADeveloperAgent — Change Plan §8 Test Contract 8-axis 정합
#
# Test axes covered:
#   TC-1: lint BEGIN/END pairing (orphan BEGIN → exit ≠ 0, orphan END → exit ≠ 0, pair → exit 0)
#   TC-2: lint 순서 invariant (reversed order → exit ≠ 0)
#   TC-3: lint flat-only nesting (nested → exit ≠ 0)
#   TC-4: migration idempotency (N회 실행 = 1회 effect)
#   TC-5: migration false-positive 0 (consumer customize = wrap 대상 아님)
#   TC-6: self-app byte-identical (templates/ ↔ .github/workflows/)
#   TC-7: dry-run filesystem touch 0
#
# Exit code:
#   0 — all PASS
#   1 — 1+ FAIL

set -u

REPO_ROOT="${1:-$(pwd)}"
LINT="$REPO_ROOT/scripts/check-wrapper-managed-block.sh"
MIGRATE="$REPO_ROOT/scripts/migrate-existing-customization.sh"
TEMPLATE_WF="$REPO_ROOT/templates/github-workflows/wrapper-managed-block.yml"
SELFAPP_WF="$REPO_ROOT/.github/workflows/wrapper-managed-block.yml"

PASS_COUNT=0
FAIL_COUNT=0
TMPDIR_BASE="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_BASE"' EXIT

pass() { echo "[TC] PASS: $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "[TC] FAIL: $1" >&2; FAIL_COUNT=$((FAIL_COUNT + 1)); }

require_file() {
  if [ ! -f "$1" ]; then
    echo "[self-test] SKIP: $2 (file not found: $1)" >&2
    return 1
  fi
  return 0
}

# ── TC-0: 의존 파일 존재 확인 ──────────────────────────────────────────────
if ! require_file "$LINT" "lint script"; then
  echo "[self-test] ERROR: lint script 없음 — TC-1/2/3 skip" >&2
  FAIL_COUNT=$((FAIL_COUNT + 3))
fi
LINT_PRESENT=$?

# ── TC-1: BEGIN/END pairing ───────────────────────────────────────────────────
if [ "$LINT_PRESENT" -eq 0 ]; then
  TMP1="$TMPDIR_BASE/tc1"
  mkdir -p "$TMP1"

  # 정상 pair → exit 0
  cat > "$TMP1/normal.yml" <<'EOF'
name: test
# BEGIN wrapper-managed
some_content: true
# END wrapper-managed
EOF
  bash "$LINT" "$TMP1/normal.yml" >/dev/null 2>&1
  [ $? -eq 0 ] && pass "TC-1a: 정상 pair → exit 0" || fail "TC-1a: 정상 pair → exit 0"

  # orphan BEGIN → exit ≠ 0
  cat > "$TMP1/orphan_begin.yml" <<'EOF'
name: test
# BEGIN wrapper-managed
some_content: true
EOF
  bash "$LINT" "$TMP1/orphan_begin.yml" >/dev/null 2>&1
  [ $? -ne 0 ] && pass "TC-1b: orphan BEGIN → exit ≠ 0" || fail "TC-1b: orphan BEGIN → exit ≠ 0"

  # orphan END → exit ≠ 0
  cat > "$TMP1/orphan_end.yml" <<'EOF'
name: test
some_content: true
# END wrapper-managed
EOF
  bash "$LINT" "$TMP1/orphan_end.yml" >/dev/null 2>&1
  [ $? -ne 0 ] && pass "TC-1c: orphan END → exit ≠ 0" || fail "TC-1c: orphan END → exit ≠ 0"

  # no marker → exit 0 (marker 미사용 = 합법)
  cat > "$TMP1/no_marker.yml" <<'EOF'
name: test
content: hello
EOF
  bash "$LINT" "$TMP1/no_marker.yml" >/dev/null 2>&1
  [ $? -eq 0 ] && pass "TC-1d: marker 없는 파일 → exit 0" || fail "TC-1d: marker 없는 파일 → exit 0"

  # .md HTML comment variant → exit 0
  cat > "$TMP1/normal.md" <<'EOF'
# Title
<!-- BEGIN wrapper-managed -->
content
<!-- END wrapper-managed -->
EOF
  bash "$LINT" "$TMP1/normal.md" >/dev/null 2>&1
  [ $? -eq 0 ] && pass "TC-1e: .md HTML comment pair → exit 0" || fail "TC-1e: .md HTML comment pair → exit 0"
fi

# ── TC-2: 순서 invariant ─────────────────────────────────────────────────────
if [ "$LINT_PRESENT" -eq 0 ]; then
  TMP2="$TMPDIR_BASE/tc2"
  mkdir -p "$TMP2"

  # reversed order (END before BEGIN) → exit ≠ 0
  cat > "$TMP2/reversed.yml" <<'EOF'
name: test
# END wrapper-managed
some_content: true
# BEGIN wrapper-managed
EOF
  bash "$LINT" "$TMP2/reversed.yml" >/dev/null 2>&1
  [ $? -ne 0 ] && pass "TC-2: 역전 marker → exit ≠ 0" || fail "TC-2: 역전 marker → exit ≠ 0"
fi

# ── TC-3: flat-only nesting 금지 ──────────────────────────────────────────────
if [ "$LINT_PRESENT" -eq 0 ]; then
  TMP3="$TMPDIR_BASE/tc3"
  mkdir -p "$TMP3"

  # nested markers (2 BEGIN) → exit ≠ 0
  cat > "$TMP3/nested.yml" <<'EOF'
name: test
# BEGIN wrapper-managed
content_outer: true
# BEGIN wrapper-managed
content_inner: true
# END wrapper-managed
# END wrapper-managed
EOF
  bash "$LINT" "$TMP3/nested.yml" >/dev/null 2>&1
  [ $? -ne 0 ] && pass "TC-3: nested marker → exit ≠ 0 (flat-only 위반)" || fail "TC-3: nested marker → exit ≠ 0 (flat-only 위반)"
fi

# ── TC-4: migration idempotency ───────────────────────────────────────────────
if require_file "$MIGRATE" "migration script"; then
  TMP4="$TMPDIR_BASE/tc4"
  TMP4_REPO="$TMP4/consumer"
  TMP4_PLUGIN="$TMP4/plugin"
  mkdir -p "$TMP4_REPO/scripts" "$TMP4_PLUGIN/scripts" "$TMP4_PLUGIN/templates"

  # consumer-scripts.manifest 생성 (plugin root)
  cat > "$TMP4_PLUGIN/templates/consumer-scripts.manifest" <<'EOF'
scripts/sample.sh
EOF

  # plugin template file (wrapper SSOT)
  echo 'echo "hello"' > "$TMP4_PLUGIN/scripts/sample.sh"

  # consumer file = byte-identical to template (wrap 대상)
  cp "$TMP4_PLUGIN/scripts/sample.sh" "$TMP4_REPO/scripts/sample.sh"

  # 1차 실행
  bash "$MIGRATE" --repo-root "$TMP4_REPO" --plugin-root "$TMP4_PLUGIN" >/dev/null 2>&1
  HASH1="$(sha256sum "$TMP4_REPO/scripts/sample.sh" 2>/dev/null | awk '{print $1}')"

  # 2차 실행 (idempotency)
  bash "$MIGRATE" --repo-root "$TMP4_REPO" --plugin-root "$TMP4_PLUGIN" >/dev/null 2>&1
  HASH2="$(sha256sum "$TMP4_REPO/scripts/sample.sh" 2>/dev/null | awk '{print $1}')"

  if [ "$HASH1" = "$HASH2" ] && [ -n "$HASH1" ]; then
    pass "TC-4: migration idempotency (2차 실행 = 1차 hash 동일)"
  else
    fail "TC-4: migration idempotency (HASH1=$HASH1 vs HASH2=$HASH2)"
  fi
fi

# ── TC-5: migration false-positive 0 ─────────────────────────────────────────
if require_file "$MIGRATE" "migration script"; then
  TMP5="$TMPDIR_BASE/tc5"
  TMP5_REPO="$TMP5/consumer"
  TMP5_PLUGIN="$TMP5/plugin"
  mkdir -p "$TMP5_REPO/scripts" "$TMP5_PLUGIN/scripts" "$TMP5_PLUGIN/templates"

  cat > "$TMP5_PLUGIN/templates/consumer-scripts.manifest" <<'EOF'
scripts/customized.sh
EOF

  # plugin template
  echo 'echo "original"' > "$TMP5_PLUGIN/scripts/customized.sh"

  # consumer = MODIFIED (byte-diff ≠ 0) → false-positive 0 invariant
  echo 'echo "consumer customized"' > "$TMP5_REPO/scripts/customized.sh"
  ORIGINAL_CONTENT="$(cat "$TMP5_REPO/scripts/customized.sh")"

  bash "$MIGRATE" --repo-root "$TMP5_REPO" --plugin-root "$TMP5_PLUGIN" >/dev/null 2>&1

  AFTER_CONTENT="$(cat "$TMP5_REPO/scripts/customized.sh")"

  # consumer customize 영역 = wrap 대상 아님 (marker 삽입 0)
  if echo "$AFTER_CONTENT" | grep -q "BEGIN wrapper-managed"; then
    fail "TC-5: false-positive 위반 — consumer customize 영역이 wrap 됨"
  else
    pass "TC-5: false-positive 0 — consumer customize 영역 wrap 안 됨"
  fi
fi

# ── TC-6: self-app byte-identical ─────────────────────────────────────────────
if require_file "$TEMPLATE_WF" "templates workflow" && require_file "$SELFAPP_WF" "self-app workflow"; then
  if diff -q "$TEMPLATE_WF" "$SELFAPP_WF" >/dev/null 2>&1; then
    pass "TC-6: templates/ ↔ .github/workflows/ byte-identical (ADR-065 §결정 1 정합)"
  else
    fail "TC-6: templates/ ↔ .github/workflows/ NOT byte-identical"
    diff "$TEMPLATE_WF" "$SELFAPP_WF" >&2 || true
  fi
fi

# ── TC-7: dry-run filesystem touch 0 ─────────────────────────────────────────
if require_file "$MIGRATE" "migration script"; then
  TMP7="$TMPDIR_BASE/tc7"
  TMP7_REPO="$TMP7/consumer"
  TMP7_PLUGIN="$TMP7/plugin"
  mkdir -p "$TMP7_REPO/scripts" "$TMP7_PLUGIN/scripts" "$TMP7_PLUGIN/templates"

  cat > "$TMP7_PLUGIN/templates/consumer-scripts.manifest" <<'EOF'
scripts/unchanged.sh
EOF
  echo 'echo "original"' > "$TMP7_PLUGIN/scripts/unchanged.sh"
  cp "$TMP7_PLUGIN/scripts/unchanged.sh" "$TMP7_REPO/scripts/unchanged.sh"

  BEFORE_HASH="$(sha256sum "$TMP7_REPO/scripts/unchanged.sh" 2>/dev/null | awk '{print $1}')"

  bash "$MIGRATE" --dry-run --repo-root "$TMP7_REPO" --plugin-root "$TMP7_PLUGIN" >/dev/null 2>&1

  AFTER_HASH="$(sha256sum "$TMP7_REPO/scripts/unchanged.sh" 2>/dev/null | awk '{print $1}')"

  if [ "$BEFORE_HASH" = "$AFTER_HASH" ]; then
    pass "TC-7: dry-run filesystem touch 0 (reconcile-protocol-v1 §4.3 정합)"
  else
    fail "TC-7: dry-run 이 filesystem 을 변경함 (BEFORE=$BEFORE_HASH vs AFTER=$AFTER_HASH)"
  fi
fi

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo "[test-check-wrapper-managed-block] Summary: $PASS_COUNT pass, $FAIL_COUNT fail"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi
exit 0
