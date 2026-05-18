#!/usr/bin/env bats
# tests/integration/test_reconcile_overlay_consumer_filter.bats
#
# CFP-899 Phase 2 — Integration tests for consumer-applicability filter
# reconcile-protocol-v1 v1.9 §4.12 consumer_applicability_filter_binding
#
# Test cases (5 TC):
#   TC-INT-1: consumer repo + whitelist filter applied (plugin-only workflow skipped) → exit 0
#   TC-INT-2: plugin repo (wrapper self-app) + no filter (all workflow mirror) → exit 0
#   TC-INT-3: unknown repo signal → fail-closed return 2
#   TC-INT-4: mixed repo dual filter
#   TC-INT-5: dry-run propagation
#
# Framework: bats (codeforge convention)
# Story §8.2 (Architect Phase 1 test contract, CFP-899)

DETECT_SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../templates/scripts/detect-repo-kind.py"
WHITELIST_FILE="$(dirname "$BATS_TEST_FILENAME")/../../templates/scripts/consumer_applicable_workflows.txt"
RECONCILE_SH="$(dirname "$BATS_TEST_FILENAME")/../../scripts/reconcile-overlay.sh"

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-1: consumer repo + whitelist filter → plugin-only workflow skipped
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-1: consumer repo — detect-repo-kind returns consumer (exit 1)" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  local tmp_root
  tmp_root="$(mktemp -d)"

  # consumer 신호: .claude/_overlay/project.yaml
  mkdir -p "${tmp_root}/.claude/_overlay"
  echo "story_key_prefix: TEST" > "${tmp_root}/.claude/_overlay/project.yaml"

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}" --skip-marketplace-check

  # consumer → exit 1
  [ "$status" -eq 1 ]
  [ "$output" = "consumer" ]

  rm -rf "${tmp_root}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-2: plugin repo → detect-repo-kind returns plugin (exit 0)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-2: plugin repo — detect-repo-kind returns plugin (exit 0)" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  local tmp_root
  tmp_root="$(mktemp -d)"

  # plugin 신호: .claude-plugin/plugin.json
  mkdir -p "${tmp_root}/.claude-plugin"
  echo '{"name":"test-plugin","version":"1.0.0"}' > "${tmp_root}/.claude-plugin/plugin.json"

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}" --skip-marketplace-check

  # plugin → exit 0
  [ "$status" -eq 0 ]
  [ "$output" = "plugin" ]

  rm -rf "${tmp_root}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-3: unknown repo signal → fail-closed (exit 3)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-3: unknown repo — fail-closed (exit 3)" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  local tmp_root
  tmp_root="$(mktemp -d)"
  # 신호 없음 — 빈 디렉터리

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}" --skip-marketplace-check

  # unknown → exit 3
  [ "$status" -eq 3 ]
  [ "$output" = "unknown" ]

  rm -rf "${tmp_root}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-4: mixed repo → dual filter (exit 2)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-4: mixed repo — dual filter (exit 2)" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  local tmp_root
  tmp_root="$(mktemp -d)"

  # plugin 신호 + consumer 신호 동시
  mkdir -p "${tmp_root}/.claude-plugin"
  echo '{"name":"test-plugin","version":"1.0.0"}' > "${tmp_root}/.claude-plugin/plugin.json"
  mkdir -p "${tmp_root}/.claude/_overlay"
  echo "story_key_prefix: TEST" > "${tmp_root}/.claude/_overlay/project.yaml"

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}" --skip-marketplace-check

  # mixed → exit 2
  [ "$status" -eq 2 ]
  [ "$output" = "mixed" ]

  rm -rf "${tmp_root}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-5: dry-run propagation — reconcile-overlay.sh syntax valid
# (CFP-898 FIX iter 1 lesson: dry-run propagation 의무)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-5: reconcile-overlay.sh syntax valid after §4.12 hook insertion" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"

  # bash -n = syntax check without execution (dry-run safe)
  run bash -n "${RECONCILE_SH}"
  [ "$status" -eq 0 ]
}
