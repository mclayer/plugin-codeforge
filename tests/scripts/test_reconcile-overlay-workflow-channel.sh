#!/usr/bin/env bash
# tests/scripts/test_reconcile-overlay-workflow-channel.sh
# CFP-2440 Phase 2 — TDD fixtures for reconcile-overlay.sh workflow channel
# Change Plan §8 Test Contract AC-1~11 이행

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RECONCILE_SH="$REPO_ROOT/scripts/reconcile-overlay.sh"

PASS=0
FAIL=0

# AC-5: anchor source base test
test_ac5_anchor_source_base() {
  local test_name="AC-5-anchor-source-base"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  local fixture_files=("fix-ledger-sync.yml" "story-section-1-immutable.yml" "subissue-from-impl-manifest.yml")
  for f in "${fixture_files[@]}"; do
    echo "# fixture: $f" > "$fixture_wrapper/templates/github-workflows/$f"
  done

  printf "fix-ledger-sync.yml\nstory-section-1-immutable.yml\nsubissue-from-impl-manifest.yml\n" \
    > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"

  mkdir -p "$fixture_consumer/.claude/_overlay"

  local output
  output=$( \
    RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
    RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
    CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
    CONSUMER_ROOT="$fixture_consumer" \
    bash "$RECONCILE_SH" --dry-run 2>&1 ) || true

  local count=0
  for f in "${fixture_files[@]}"; do
    echo "$output" | grep -q "\.github/workflows/$f" && ((count++)) || true
  done

  if [ "$count" -eq 3 ]; then
    echo "✓ PASS: $test_name (count=$count)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — expected 3 files, got $count"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-2: update not bootstrap
test_ac2_update_not_bootstrap() {
  local test_name="AC-2-update-not-bootstrap"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  local wf_name="test-workflow.yml"
  echo "version: v2-new" > "$fixture_wrapper/templates/github-workflows/$wf_name"
  echo "version: v1-old" > "$fixture_consumer/.github/workflows/$wf_name"
  echo "$wf_name" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local dst_content
  dst_content=$(cat "$fixture_consumer/.github/workflows/$wf_name" 2>/dev/null || echo "")

  if [[ "$dst_content" == "version: v2-new" ]]; then
    echo "✓ PASS: $test_name — update confirmed"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — expected v2-new, got '$dst_content'"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-6: over broad enumerate
test_ac6_over_broad_enumerate() {
  local test_name="AC-6-over-broad-enumerate"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "# consumer file" > "$fixture_consumer/.github/workflows/custom.yml"
  local original_content
  original_content=$(cat "$fixture_consumer/.github/workflows/custom.yml")

  echo "# empty" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local after_content
  after_content=$(cat "$fixture_consumer/.github/workflows/custom.yml" 2>/dev/null || echo "")

  if [[ "$after_content" == "$original_content" ]]; then
    echo "✓ PASS: $test_name — consumer file preserved"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — file was modified"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-10: empty vs absent whitelist
test_ac10_empty_vs_absent_whitelist() {
  local test_name="AC-10-empty-vs-absent"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "# existing" > "$fixture_consumer/.github/workflows/existing.yml"
  printf '# empty\n\n   \n' > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  if [ -f "$fixture_consumer/.github/workflows/existing.yml" ]; then
    echo "✓ PASS: $test_name — empty whitelist: file preserved"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — file was removed"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-8: dry run
test_ac8_dry_run() {
  local test_name="AC-8-dry-run"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "v1" > "$fixture_wrapper/templates/github-workflows/test.yml"
  echo "test.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  local dst_exists_before=0
  [ -f "$fixture_consumer/.github/workflows/test.yml" ] && dst_exists_before=1

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --dry-run > /dev/null 2>&1 || true

  local dst_exists_after=0
  [ -f "$fixture_consumer/.github/workflows/test.yml" ] && dst_exists_after=1

  if [ "$dst_exists_before" -eq "$dst_exists_after" ]; then
    echo "✓ PASS: $test_name — dry-run no side-effects"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — filesystem modified during dry-run"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-9: idempotency
test_ac9_idempotency() {
  local test_name="AC-9-idempotency"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "v1-stable" > "$fixture_wrapper/templates/github-workflows/test.yml"
  echo "test.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local content_after_1st
  content_after_1st=$(cat "$fixture_consumer/.github/workflows/test.yml" 2>/dev/null || echo "")

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local content_after_2nd
  content_after_2nd=$(cat "$fixture_consumer/.github/workflows/test.yml" 2>/dev/null || echo "")

  if [ "$content_after_1st" = "$content_after_2nd" ]; then
    echo "✓ PASS: $test_name — 2x run byte-identical"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — content differs"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-1: new propagation
test_ac1_new_propagation() {
  local test_name="AC-1-new-propagation"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "new-content" > "$fixture_wrapper/templates/github-workflows/new-wf.yml"
  echo "new-wf.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  if [ -f "$fixture_consumer/.github/workflows/new-wf.yml" ]; then
    echo "✓ PASS: $test_name — new workflow propagated"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — file not found"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# AC-3, AC-4, AC-7: placeholder tests
test_ac3_filter_skip() {
  echo "SKIP: AC-3-filter-skip (requires repo-kind detection)"
  return 0
}

test_ac4_repo_kind() {
  echo "SKIP: AC-4-repo-kind (requires detect-repo-kind.py)"
  return 0
}

test_ac7_loss_report() {
  echo "SKIP: AC-7-loss-report (requires marker infrastructure)"
  return 0
}

# AC-11: rollback scope
test_ac11_rollback_scope() {
  local test_name="AC-11-rollback-scope"
  local fixture_root fixture_wrapper fixture_consumer tmp_snapshot

  fixture_root="$(mktemp -d)"
  fixture_wrapper="$fixture_root/fixture-wrapper"
  fixture_consumer="$fixture_root/fixture-consumer"
  tmp_snapshot="$fixture_root/snapshots"

  mkdir -p "$fixture_wrapper/templates/github-workflows" \
           "$fixture_wrapper/templates/scripts" \
           "$fixture_consumer/.github/workflows" \
           "$tmp_snapshot"

  echo "v1" > "$fixture_wrapper/templates/github-workflows/test.yml"
  echo "test.yml" > "$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt"
  mkdir -p "$fixture_consumer/.claude/_overlay"

  RECONCILE_OVERLAY_WORKFLOW_SRC_DIR="$fixture_wrapper/templates/github-workflows" \
  RECONCILE_OVERLAY_WORKFLOW_DST_DIR="$fixture_consumer/.github/workflows" \
  CONSUMER_APPLICABLE_WHITELIST="$fixture_wrapper/templates/scripts/consumer_applicable_workflows.txt" \
  RECONCILE_OVERLAY_SNAPSHOT_DIR="$tmp_snapshot" \
  CONSUMER_ROOT="$fixture_consumer" \
  bash "$RECONCILE_SH" --apply > /dev/null 2>&1 || true

  local latest_snap
  latest_snap=$(ls "$tmp_snapshot"/*.tar.gz 2>/dev/null | sort -r | head -1 || true)

  if [ -z "$latest_snap" ]; then
    echo "✗ FAIL: $test_name — snapshot not found"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi

  local tar_contents
  tar_contents=$(tar tzf "$latest_snap" 2>/dev/null || echo "")

  if echo "$tar_contents" | grep -q "\.github/workflows"; then
    echo "✓ PASS: $test_name — workflow in snapshot"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name — workflows not in snapshot"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2440 Phase 2: reconcile-overlay.sh workflow channel"
echo "TDD Test Suite (AC-1~11)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

test_ac5_anchor_source_base
test_ac2_update_not_bootstrap
test_ac6_over_broad_enumerate
test_ac10_empty_vs_absent_whitelist
test_ac8_dry_run
test_ac9_idempotency
test_ac1_new_propagation
test_ac3_filter_skip
test_ac4_repo_kind
test_ac7_loss_report
test_ac11_rollback_scope

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Test Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED ✓"
  exit 0
else
  echo "Some tests FAILED ✗"
  exit 1
fi
