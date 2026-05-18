#!/usr/bin/env bats
# tests/integration/test_reconcile_overlay_result_fidelity.bats
#
# CFP-900 Phase 2 — Integration tests for result_fidelity_binding
# reconcile-protocol-v1 v1.10 §4.13 hook_integration
#
# Test cases (7 TC):
#   TC-INT-RF-1: reconcile-overlay.sh syntax valid (bash -n)
#   TC-INT-RF-2: post-mirror stage 도달 verify (§4.13 hook_integration — step_4)
#   TC-INT-RF-3: S1 fail-closed exit → result FAILED (MARKER_NONE dep-closure abort path)
#   TC-INT-RF-4: S2 abort exit → result FAILED (unknown repo_kind path)
#   TC-INT-RF-5: all OK → result SUCCESS (정직 기록 verify)
#   TC-INT-RF-6: result-fidelity-aggregator.py 자체 실행 가능 확인 (ADR-061)
#   TC-INT-RF-7: dry-run mode → result field 미적용 (EC-2)
#
# F-CR-899-6 류 방지: reconcile-overlay.sh 실 실행 검증 (proxy-only 회피)
# mock consumer overlay fixture + post-mirror stage 도달 verify
#
# Framework: bats (codeforge convention)
# ADR-061 정합: 외부 .py 파일만 사용 (heredoc-python 0)

AGGREGATOR_PY="$(dirname "$BATS_TEST_FILENAME")/../../templates/scripts/result-fidelity-aggregator.py"
RECONCILE_SH="$(dirname "$BATS_TEST_FILENAME")/../../scripts/reconcile-overlay.sh"
REPO_ROOT="$(dirname "$BATS_TEST_FILENAME")/../.."

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-1: reconcile-overlay.sh bash syntax 검증 (CFP-900 수정 후)
# §4.13 hook_integration 삽입 후 syntax 유지 invariant
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-1: reconcile-overlay.sh bash -n syntax valid after CFP-900 modifications" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"
  run bash -n "${RECONCILE_SH}"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-2: post-mirror sanity stage 도달 verify
# F-CR-899-6 교훈: reconcile-overlay.sh 실 실행 검증, proxy-only 회피
# mock consumer overlay fixture + §4.13 _AGG_OUTPUT/_AGG_EC 코드 경로 verify
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-2: §4.13 post-mirror sanity stage reached in reconcile-overlay.sh" {
  [[ -f "${RECONCILE_SH}" ]] || skip "reconcile-overlay.sh not found"
  [[ -f "${AGGREGATOR_PY}" ]] || skip "result-fidelity-aggregator.py not found"

  # mock wrapper dir (consumer==wrapper → idempotency check가 통과하지 않도록 분리)
  local tmp_wrapper tmp_consumer
  tmp_wrapper="$(mktemp -d)"
  tmp_consumer="$(mktemp -d)"

  # wrapper에 파일 1개 생성 (MARKER_NONE branch 진입용)
  mkdir -p "${tmp_wrapper}"
  echo "name: test" > "${tmp_wrapper}/test.yml"
  # consumer는 비어있음 → 파일 복사 대상 (MARKER_NONE wholesale mirror)

  # mock detect-repo-kind.py (plugin 반환 → S2 filter skip)
  local tmp_detect
  tmp_detect="$(mktemp -d)"
  cat > "${tmp_detect}/detect-repo-kind.py" <<'PYEOF'
#!/usr/bin/env python3
import sys
print("plugin")
sys.exit(0)
PYEOF

  # mock mirror-dependency-closure.py (success 반환)
  cat > "${tmp_detect}/mirror-dependency-closure.py" <<'PYEOF'
#!/usr/bin/env python3
import sys
sys.exit(0)
PYEOF

  # RESULT_FIDELITY_OUTPUT_FILE 설정 → result artifact 생성 확인
  local result_file
  result_file="$(mktemp).json"

  # reconcile-overlay.sh 실행 (MARKER_NONE branch → post-mirror stage)
  run env \
    RECONCILE_OVERLAY_WRAPPER_DIR="${tmp_wrapper}" \
    RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR="${tmp_consumer}" \
    RECONCILE_OVERLAY_SNAPSHOT_DIR="${tmp_consumer}/.snapshots" \
    MIRROR_DEP_PY="${tmp_detect}/mirror-dependency-closure.py" \
    FILTER_REPO_KIND_PY="${tmp_detect}/detect-repo-kind.py" \
    RESULT_FIDELITY_AGGREGATOR_PY="${AGGREGATOR_PY}" \
    RESULT_FIDELITY_OUTPUT_FILE="${result_file}" \
    bash "${RECONCILE_SH}" --apply

  # F-CR-900-1 회귀 방지: reconcile-overlay.sh 가 §4.13 abort (exit 1 = set -e trigger) 로 종료하지 않아야 함
  # 허용 exit code: 0 (완료) 또는 2 (WHOLESALE MIRROR loss — OVERALL_EXIT=2 정상 경로)
  # 금지 exit code: 1 (§4.13 블록 내 local 키워드 set -e abort = F-CR-900-1 regression)
  [ "$status" -ne 1 ]

  # §4.13 post-mirror stage 도달 검증: "result:" echo 가 output 에 포함되어야 함
  # (F-CR-900-1 미fix 상태 = local top-level → set -e abort 전 echo 미도달 → 이 assertion FAIL → 회귀 검출)
  [[ "$output" == *"result:"* ]]

  # result artifact 생성 확인 (RESULT_FIDELITY_OUTPUT_FILE 기록 — §4.13 honest record)
  [[ -f "${result_file}" ]]

  # Cleanup
  rm -rf "${tmp_wrapper}" "${tmp_consumer}" "${tmp_detect}"
  rm -f "${result_file}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-3: S1 fail-closed path → FAILED 기록
# §4.13 degradation_propagation: S1 exit 1 → FAILED
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-3: aggregator S1=1 → result FAILED (S1 fail-closed)" {
  [[ -f "${AGGREGATOR_PY}" ]] || skip "result-fidelity-aggregator.py not found"

  local tmp_w tmp_c
  tmp_w="$(mktemp -d)"
  tmp_c="$(mktemp -d)"
  echo "name: t" > "${tmp_w}/t.yml"
  echo "name: t" > "${tmp_c}/t.yml"

  # S1 exit 1 = dependency missing fail-closed → FAILED
  run python3 "${AGGREGATOR_PY}" \
    --s1-exit 1 \
    --s2-exit 0 \
    --wrapper-dir "${tmp_w}" \
    --consumer-dir "${tmp_c}"

  # exit code = 1 (FAILED)
  [ "$status" -eq 1 ]
  # output JSON에 FAILED 포함
  [[ "$output" == *"FAILED"* ]]

  rm -rf "${tmp_w}" "${tmp_c}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-4: S2 abort path → FAILED 기록
# §4.13 degradation_propagation: S2 exit 1 → FAILED
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-4: aggregator S2=1 → result FAILED (S2 filter abort)" {
  [[ -f "${AGGREGATOR_PY}" ]] || skip "result-fidelity-aggregator.py not found"

  local tmp_w tmp_c
  tmp_w="$(mktemp -d)"
  tmp_c="$(mktemp -d)"
  echo "name: t" > "${tmp_w}/t.yml"
  echo "name: t" > "${tmp_c}/t.yml"

  # S2 exit 1 = unknown repo_kind abort → FAILED
  run python3 "${AGGREGATOR_PY}" \
    --s1-exit 0 \
    --s2-exit 1 \
    --wrapper-dir "${tmp_w}" \
    --consumer-dir "${tmp_c}"

  [ "$status" -eq 1 ]
  [[ "$output" == *"FAILED"* ]]

  rm -rf "${tmp_w}" "${tmp_c}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-5: all OK path → SUCCESS 정직 기록
# upgrade_event_honest_record: result=SUCCESS (mock overlay complete)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-5: aggregator S1=0 S2=0 sanity-pass → result SUCCESS (honest record)" {
  [[ -f "${AGGREGATOR_PY}" ]] || skip "result-fidelity-aggregator.py not found"

  local tmp_w tmp_c
  tmp_w="$(mktemp -d)"
  tmp_c="$(mktemp -d)"
  # wrapper == consumer → sanity PASS
  echo "name: ok" > "${tmp_w}/ok.yml"
  echo "name: ok" > "${tmp_c}/ok.yml"

  run python3 "${AGGREGATOR_PY}" \
    --s1-exit 0 \
    --s2-exit 0 \
    --wrapper-dir "${tmp_w}" \
    --consumer-dir "${tmp_c}"

  [ "$status" -eq 0 ]
  [[ "$output" == *"SUCCESS"* ]]
  # SUCCESS hardcode 검증: output 안 result 값이 실제 SUCCESS여야 함
  [[ "$output" != *'"result": "FAILED"'* ]]

  rm -rf "${tmp_w}" "${tmp_c}"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-6: result-fidelity-aggregator.py ADR-061 invariant
# 외부 .py 파일 / shebang / 실행 가능 확인
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-6: result-fidelity-aggregator.py ADR-061 invariant (external .py, shebang, runnable)" {
  [[ -f "${AGGREGATOR_PY}" ]] || skip "result-fidelity-aggregator.py not found"

  # shebang 확인
  local first_line
  first_line="$(head -1 "${AGGREGATOR_PY}")"
  [[ "${first_line}" == "#!/usr/bin/env python3" ]]

  # stdlib only 확인 (import 제 3자 패키지 없어야 함)
  run grep -E "^import (requests|pyyaml|yaml|boto3|numpy|pandas)" "${AGGREGATOR_PY}"
  [ "$status" -ne 0 ]  # 3rd party import 없어야 함

  # --help 실행 가능 확인
  run python3 "${AGGREGATOR_PY}" --help
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-INT-RF-7: dry-run mode → result field 미적용 (EC-2)
# §4.13 closed_set_invariant EC-2: dry-run = result field 미적용
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-INT-RF-7: aggregator --dry-run → EC-2 result field 미적용" {
  [[ -f "${AGGREGATOR_PY}" ]] || skip "result-fidelity-aggregator.py not found"

  local tmp_w tmp_c
  tmp_w="$(mktemp -d)"
  tmp_c="$(mktemp -d)"
  echo "name: d" > "${tmp_w}/d.yml"
  echo "name: d" > "${tmp_c}/d.yml"

  run python3 "${AGGREGATOR_PY}" \
    --s1-exit 1 \
    --s2-exit 0 \
    --wrapper-dir "${tmp_w}" \
    --consumer-dir "${tmp_c}" \
    --dry-run

  # dry-run = exit 0 (preview only)
  [ "$status" -eq 0 ]
  # JSON output 없음 (result field 미적용)
  [[ "$output" != *'"result"'* ]]

  rm -rf "${tmp_w}" "${tmp_c}"
}
