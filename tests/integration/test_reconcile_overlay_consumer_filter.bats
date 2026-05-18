#!/usr/bin/env bats
# tests/integration/test_reconcile_overlay_consumer_filter.bats
#
# CFP-899 Phase 2 — Integration tests for consumer-applicability filter
# reconcile-protocol-v1 v1.9 §4.12 consumer_applicability_filter_binding
#
# Test cases (7 TC):
#   TC-INT-1: consumer repo → detect-repo-kind exit 1
#   TC-INT-2: plugin repo → detect-repo-kind exit 0
#   TC-INT-3: unknown repo signal → fail-closed exit 3
#   TC-INT-4: mixed repo → exit 2 (full set, ADR-083 §결정 5/6)
#   TC-INT-5: reconcile-overlay.sh syntax valid after §4.12 hook insertion
#   TC-CAF-MIXED-1: wrapper self-app (mixed) → 0 skip (ADR-083 §결정 6)
#   TC-CAF-SELFLOOP-1: detect-repo-kind.py 자신은 workflow yml 의존 없음
#
# FIX iter 1 (F-CR-899-5/6):
#   - --skip-marketplace-check flag 제거 (filesystem_only_invariant)
#   - TC-CAF-MIXED-1 신설: wrapper self-app 76 .yml = skip 0
#   - TC-CAF-SELFLOOP-1 신설: self-loop 0 direct verify
#
# Framework: bats (codeforge convention)
# Story §8.2 (Architect Phase 1 test contract, CFP-899)

DETECT_SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../templates/scripts/detect-repo-kind.py"
WHITELIST_FILE="$(dirname "$BATS_TEST_FILENAME")/../../templates/scripts/consumer_applicable_workflows.txt"
RECONCILE_SH="$(dirname "$BATS_TEST_FILENAME")/../../scripts/reconcile-overlay.sh"
REPO_ROOT="$(dirname "$BATS_TEST_FILENAME")/../.."

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

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}"

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

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}"

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

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}"

  # unknown → exit 3
  [ "$status" -eq 3 ]
  [ "$output" = "unknown" ]

  rm -rf "${tmp_root}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-4: mixed repo → exit 2 (full set per ADR-083 §결정 5/6)
# F-CR-899-2 fix verify: mixed = plugin + overlay → full set (0 skip)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-4: mixed repo — exit 2 (full workflow set, 0 skip, ADR-083 §결정 5/6)" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  local tmp_root
  tmp_root="$(mktemp -d)"

  # plugin 신호 + consumer 신호 동시
  mkdir -p "${tmp_root}/.claude-plugin"
  echo '{"name":"test-plugin","version":"1.0.0"}' > "${tmp_root}/.claude-plugin/plugin.json"
  mkdir -p "${tmp_root}/.claude/_overlay"
  echo "story_key_prefix: TEST" > "${tmp_root}/.claude/_overlay/project.yaml"

  run python3 "${DETECT_SCRIPT}" --repo-root "${tmp_root}"

  # mixed → exit 2 (full set: filter 적용 없음)
  [ "$status" -eq 2 ]
  [ "$output" = "mixed" ]

  rm -rf "${tmp_root}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-5: reconcile-overlay.sh syntax valid after §4.12 hook insertion
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-5: reconcile-overlay.sh syntax valid after §4.12 hook insertion" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"

  # bash -n = syntax check without execution (dry-run safe)
  run bash -n "${RECONCILE_SH}"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-CAF-MIXED-1: wrapper self-app (mixed) → skip count = 0
# ADR-083 §결정 6: wrapper self-app 76 .yml 모두 적용 + 0 skip invariant
# F-CR-899-6 신설 / F-CR-899-6-remaining FIX: proxy 검증 → 실 실행 검증 강화
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-CAF-MIXED-1: wrapper self-app mixed → reconcile-overlay.sh dry-run skip count = 0" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"

  # 1) detect-repo-kind.py 출력 proxy 검증 (기존)
  run python3 "${DETECT_SCRIPT}" --repo-root "${REPO_ROOT}"
  [ "$status" -eq 2 ]
  [ "$output" = "mixed" ]

  # 2) reconcile-overlay.sh 실 실행 검증 (F-CR-899-6-remaining FIX)
  #    mixed → hook plugin|mixed branch → [FILTER] skip 라인 0개 invariant
  #    env 주입:
  #      CONSUMER_ROOT          = wrapper root (mixed 신호 위치)
  #      FILTER_REPO_KIND_PY    = 본 테스트 DETECT_SCRIPT
  #      CONSUMER_APPLICABLE_WHITELIST = 본 테스트 WHITELIST_FILE
  #    --dry-run: filesystem touch 0 (preview only)
  local skip_count
  skip_count=$(
    CONSUMER_ROOT="${REPO_ROOT}" \
    FILTER_REPO_KIND_PY="${DETECT_SCRIPT}" \
    CONSUMER_APPLICABLE_WHITELIST="${WHITELIST_FILE}" \
      bash "${RECONCILE_SH}" --dry-run 2>&1 | grep -c '\[FILTER\] skip' || true
  )

  # ADR-083 §결정 6: mixed = 0 skip invariant
  [ "${skip_count}" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-CAF-SELFLOOP-1: detect-repo-kind.py 자신은 workflow yml 의존 없음
# §4.12 self_app_exemption direct verify
# F-CR-899-6 신설
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-CAF-SELFLOOP-1: detect-repo-kind.py not referenced in workflow ymls (self-loop 0)" {
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  # .github/workflows/*.yml 안 detect-repo-kind 또는 consumer_applicable_workflows 참조 = 0
  local hit_count
  hit_count=$(grep -rl 'detect-repo-kind\|consumer_applicable_workflows' \
    "${REPO_ROOT}/.github/workflows/"*.yml 2>/dev/null | wc -l || echo 0)

  # self-loop 0 invariant: workflow yml 안 detect 스크립트 자기 참조 0
  [ "${hit_count}" -eq 0 ]
}
