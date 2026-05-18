#!/usr/bin/env bats
# tests/integration/test_reconcile_overlay_consumer_filter.bats
#
# CFP-899 Phase 2 — Integration tests for consumer-applicability filter
# reconcile-protocol-v1 v1.9 §4.12 consumer_applicability_filter_binding
#
# Test cases (7 TC + 4 CFP-986 end-to-end TCs):
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
# CFP-986 FIX — classification↔severity disjoint end-to-end TCs (4 TC):
#   TC-INT-RF-CONSUMER: consumer fixture → reconcile-overlay.sh end-to-end → result SUCCESS
#     (RED pre-fix / GREEN post-fix: proves classification _ec=1 no longer poisons _S2_MAX_EXIT)
#   TC-INT-RF-UNKNOWN:  unknown fixture → result FAILED (genuine fail-closed preserved)
#   TC-INT-RF-PLUGIN:   plugin fixture  → result SUCCESS
#   TC-INT-RF-MIXED:    mixed fixture   → result SUCCESS
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

# ─────────────────────────────────────────────────────────────────────────────
# CFP-986 FIX — classification↔severity disjoint end-to-end TCs
# reconcile-protocol-v1 v1.10 §4.12/§4.13 disjoint invariant
#
# Helper: _cfp986_make_mock_detect
#   exit_code: detect-repo-kind.py mock exit code 주입
# ─────────────────────────────────────────────────────────────────────────────
_cfp986_make_mock_detect() {
  # $1 = dest dir, $2 = kind string, $3 = exit code
  local dest_dir="$1" kind="$2" ec="$3"
  cat > "${dest_dir}/detect-repo-kind.py" <<PYEOF
#!/usr/bin/env python3
import sys
print("${kind}")
sys.exit(${ec})
PYEOF
  # mock mirror-dependency-closure.py — 항상 성공
  cat > "${dest_dir}/mirror-dependency-closure.py" <<PYEOF
#!/usr/bin/env python3
import sys
sys.exit(0)
PYEOF
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-CONSUMER: consumer fixture → reconcile-overlay.sh end-to-end
#   CFP-986 핵심 TC: pre-fix = result FAILED (RED), post-fix = result SUCCESS (GREEN)
#   § disjoint 증명: classification _ec=1 (consumer) 이 _S2_MAX_EXIT 에 전파되지 않아야 함
#
#   reconcile-overlay.sh 전체 경로 실행 (aggregator unit bypass NOT used)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-CONSUMER: consumer fixture → reconcile-overlay.sh end-to-end → result SUCCESS" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"
  [[ -f "${DETECT_SCRIPT}" ]] || skip "detect-repo-kind.py not found"

  local tmp_wrapper tmp_consumer tmp_detect tmp_result
  tmp_wrapper="$(mktemp -d)"
  tmp_consumer="$(mktemp -d)"
  tmp_detect="$(mktemp -d)"
  tmp_result="$(mktemp).json"

  # wrapper: .yml 파일 1개 (MARKER_NONE → wholesale mirror path)
  echo "name: reconcile-test" > "${tmp_wrapper}/test.yml"

  # consumer: .claude/_overlay/project.yaml (consumer signal)
  mkdir -p "${tmp_consumer}/.claude/_overlay"
  echo "story_key_prefix: TEST" > "${tmp_consumer}/.claude/_overlay/project.yaml"

  # mock detect: consumer (exit 1) — CFP-986 핵심: classification exit 1 이 severity 에 전파되면 FAILED
  _cfp986_make_mock_detect "${tmp_detect}" "consumer" 1

  run env \
    RECONCILE_OVERLAY_WRAPPER_DIR="${tmp_wrapper}" \
    RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="${tmp_consumer}" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="${tmp_consumer}/.snapshots" \
    MIRROR_DEP_PY="${tmp_detect}/mirror-dependency-closure.py" \
    FILTER_REPO_KIND_PY="${tmp_detect}/detect-repo-kind.py" \
    RESULT_FIDELITY_AGGREGATOR_PY="${REPO_ROOT}/templates/scripts/result-fidelity-aggregator.py" \
    CONSUMER_APPLICABLE_WHITELIST="${WHITELIST_FILE}" \
    RESULT_FIDELITY_OUTPUT_FILE="${tmp_result}" \
    bash "${RECONCILE_SH}" --apply

  # §4.13 disjoint invariant: consumer reconcile 정상 완료 = result non-FAILED
  # (CFP-986 pre-fix: _S2_MAX_EXIT=1 → aggregator FAILED = 오분류)
  # post-fix: _S2_MAX_EXIT=0 → s2_exit=0 → SUCCESS 또는 SUCCESS_WITH_DEGRADATION
  # (sanity WARNING = extra consumer files in overlay → SUCCESS_WITH_DEGRADATION 정상)
  # 핵심 invariant: result: FAILED 포함 금지 (classification↔severity disjoint 확인)
  [[ "$output" != *"result: FAILED"* ]]
  # s2_exit=0 확인 (classification _ec=1 이 severity 에 전파되지 않음 직접 증명)
  [[ "$output" == *'"s2_exit": 0'* ]]

  rm -rf "${tmp_wrapper}" "${tmp_consumer}" "${tmp_detect}"
  rm -f "${tmp_result}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-UNKNOWN: unknown fixture → reconcile-overlay.sh end-to-end
#   genuine fail-closed abort PRESERVED — CFP-986 FIX 후 과억제 없음 확인
#   _S2_MAX_EXIT=1 은 unknown) 분기에서 여전히 올바르게 세팅됨 → result FAILED
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-UNKNOWN: unknown fixture → reconcile-overlay.sh end-to-end → result FAILED (genuine abort preserved)" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"

  local tmp_wrapper tmp_consumer tmp_detect tmp_result
  tmp_wrapper="$(mktemp -d)"
  tmp_consumer="$(mktemp -d)"
  tmp_detect="$(mktemp -d)"
  tmp_result="$(mktemp).json"

  # wrapper: .yml 파일 1개
  echo "name: reconcile-test" > "${tmp_wrapper}/test.yml"

  # consumer overlay: 빈 디렉터리 (신호 없음 = unknown)
  # mock detect: unknown (exit 3) → §4.12 fail-closed abort → _S2_MAX_EXIT=1
  _cfp986_make_mock_detect "${tmp_detect}" "unknown" 3

  # unknown 분기 = return 1 abort → reconcile-overlay.sh 는 per-file abort 후 OVERALL_EXIT!=0
  # result: FAILED 출력 여부만 확인 (exit code 자체는 0 또는 1 모두 가능 — loss report 경로 차이)
  run env \
    RECONCILE_OVERLAY_WRAPPER_DIR="${tmp_wrapper}" \
    RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="${tmp_consumer}" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="${tmp_consumer}/.snapshots" \
    MIRROR_DEP_PY="${tmp_detect}/mirror-dependency-closure.py" \
    FILTER_REPO_KIND_PY="${tmp_detect}/detect-repo-kind.py" \
    RESULT_FIDELITY_AGGREGATOR_PY="${REPO_ROOT}/templates/scripts/result-fidelity-aggregator.py" \
    CONSUMER_APPLICABLE_WHITELIST="${WHITELIST_FILE}" \
    RESULT_FIDELITY_OUTPUT_FILE="${tmp_result}" \
    bash "${RECONCILE_SH}" --apply || true  # exit != 0 예상, bats status 무시

  # genuine abort preserved: result FAILED (과억제 없음 invariant)
  [[ "$output" == *"result: FAILED"* ]]

  rm -rf "${tmp_wrapper}" "${tmp_consumer}" "${tmp_detect}"
  rm -f "${tmp_result}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-PLUGIN: plugin fixture → reconcile-overlay.sh end-to-end → result SUCCESS
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-PLUGIN: plugin fixture → reconcile-overlay.sh end-to-end → result SUCCESS" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"

  local tmp_wrapper tmp_consumer tmp_detect tmp_result
  tmp_wrapper="$(mktemp -d)"
  tmp_consumer="$(mktemp -d)"
  tmp_detect="$(mktemp -d)"
  tmp_result="$(mktemp).json"

  echo "name: reconcile-test" > "${tmp_wrapper}/test.yml"
  # mock detect: plugin (exit 0) — plugin|mixed branch → _S2_MAX_EXIT=0 (변경 없음)
  _cfp986_make_mock_detect "${tmp_detect}" "plugin" 0

  run env \
    RECONCILE_OVERLAY_WRAPPER_DIR="${tmp_wrapper}" \
    RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="${tmp_consumer}" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="${tmp_consumer}/.snapshots" \
    MIRROR_DEP_PY="${tmp_detect}/mirror-dependency-closure.py" \
    FILTER_REPO_KIND_PY="${tmp_detect}/detect-repo-kind.py" \
    RESULT_FIDELITY_AGGREGATOR_PY="${REPO_ROOT}/templates/scripts/result-fidelity-aggregator.py" \
    CONSUMER_APPLICABLE_WHITELIST="${WHITELIST_FILE}" \
    RESULT_FIDELITY_OUTPUT_FILE="${tmp_result}" \
    bash "${RECONCILE_SH}" --apply

  [[ "$output" == *"result: SUCCESS"* ]]
  [[ "$output" != *"result: FAILED"* ]]

  rm -rf "${tmp_wrapper}" "${tmp_consumer}" "${tmp_detect}"
  rm -f "${tmp_result}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-MIXED: mixed fixture → reconcile-overlay.sh end-to-end → result SUCCESS
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-MIXED: mixed fixture → reconcile-overlay.sh end-to-end → result SUCCESS" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"

  local tmp_wrapper tmp_consumer tmp_detect tmp_result
  tmp_wrapper="$(mktemp -d)"
  tmp_consumer="$(mktemp -d)"
  tmp_detect="$(mktemp -d)"
  tmp_result="$(mktemp).json"

  echo "name: reconcile-test" > "${tmp_wrapper}/test.yml"
  # mock detect: mixed (exit 2) — plugin|mixed branch → _S2_MAX_EXIT=0 (변경 없음)
  _cfp986_make_mock_detect "${tmp_detect}" "mixed" 2

  run env \
    RECONCILE_OVERLAY_WRAPPER_DIR="${tmp_wrapper}" \
    RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="${tmp_consumer}" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="${tmp_consumer}/.snapshots" \
    MIRROR_DEP_PY="${tmp_detect}/mirror-dependency-closure.py" \
    FILTER_REPO_KIND_PY="${tmp_detect}/detect-repo-kind.py" \
    RESULT_FIDELITY_AGGREGATOR_PY="${REPO_ROOT}/templates/scripts/result-fidelity-aggregator.py" \
    CONSUMER_APPLICABLE_WHITELIST="${WHITELIST_FILE}" \
    RESULT_FIDELITY_OUTPUT_FILE="${tmp_result}" \
    bash "${RECONCILE_SH}" --apply

  [[ "$output" == *"result: SUCCESS"* ]]
  [[ "$output" != *"result: FAILED"* ]]

  rm -rf "${tmp_wrapper}" "${tmp_consumer}" "${tmp_detect}"
  rm -f "${tmp_result}"
}
