#!/usr/bin/env bash
# scripts/check-canary-compatibility.sh — canary promotion criteria 4-tuple verification (thin orchestrator)
#
# CFP-991 (Wave 4 sub-Epic #1 Story-4 — canary promotion criteria enforcement layer)
# Carrier ADR: ADR-072 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14
# Sibling: ADR-070 §결정 D6 (CFP-988 Amendment 4 mandatory-real-execution-evidence STANDING cross-ref T-4.1)
#
# RefactorAgent A-3 + B-3 (thin orchestrator + helper lib extraction) — CFP-954 gh-api-helpers.sh 선례 답습:
#   - business logic 0 (helper 위임만)
#   - helper lib: scripts/lib/canary-compatibility-helpers.sh
#
# 6-step sequential orchestration (reconcile-protocol-v1 §4.14 hook_integration.sequential_composition_order verbatim):
#   step_1: wrapper-self-app Tier-1 exemption fast-PASS check (triple-AND: production_cutover_touching=true AND repo=wrapper AND code_change=0)
#   step_2: _validate_enum_closed_set() — canary_consumer_evidence_origin + promotion_gate_failure_mode 양 enum closed-set verify
#   step_3: _enumerate_family_7_canary_versions() — publisher_versions[] length_invariant=7 + member_enum verify
#   step_4: _extract_4tuple_measurement_source() — 4 sub measurement_source + evidence_origin annotation verify
#   step_5: _three_way_version_diff() — publisher↔registry↔consumer 3-way match (ADR-063 Amendment 5 §결정 15)
#   step_6: promotion_gate_failure_mode 평가 → exit 0/1/2 deterministic mapping
#
# Exit codes (3-tier, ADR-060 §결정 15 정합):
#   0 = PASS (4-tuple all 'pass' OR 'n_a' + 3-way match verified)
#   1 = warning (missing data / network 일시 실패 / sandbox-bound fetch fail — advisory only, hotfix-bypass:canary-promotion-criteria bypass 가능)
#   2 = mechanical anchor invalid (schema breach / real divergence / length_invariant breach / enum closed-set breach — hard fail)

set -uo pipefail

readonly _CFP991_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly _CFP991_HELPER_LIB="${_CFP991_SCRIPT_DIR}/lib/canary-compatibility-helpers.sh"

# Idempotent helper lib source guard
if [[ ! -f "$_CFP991_HELPER_LIB" ]]; then
  echo "[canary-compat] ERROR: helper lib not found — $_CFP991_HELPER_LIB" >&2
  exit 2
fi
# shellcheck source=lib/canary-compatibility-helpers.sh
source "$_CFP991_HELPER_LIB"

# ----------------------------------------------------------------------
# Step 1: wrapper-self-app Tier-1 exemption fast-PASS check
# triple-AND: production_cutover_touching=true AND repo=wrapper AND code_change=0
# ADR-072 §결정 6 wrapper-self-app N/A invariant 정합 (영구 fast-PASS scope)
# ----------------------------------------------------------------------
_step_1_tier1_exemption_check() {
  local production_cutover_touching="${PRODUCTION_CUTOVER_TOUCHING:-false}"
  local repo_kind="${REPO_KIND:-}"
  local code_change="${CODE_CHANGE:-1}"  # default 1 (changed) — empty = changed assumption

  # GitHub Actions context detection (auto-fill defaults)
  if [[ -z "$repo_kind" && -n "${GITHUB_REPOSITORY:-}" ]]; then
    if [[ "$GITHUB_REPOSITORY" == "mclayer/plugin-codeforge" ]]; then
      repo_kind="wrapper"
    else
      repo_kind="consumer"
    fi
  fi

  # Tier-1 exemption triple-AND
  if [[ "$production_cutover_touching" == "true" && "$repo_kind" == "wrapper" && "$code_change" == "0" ]]; then
    echo "[canary-compat] PASS: Tier-1 wrapper-self-app exemption (triple-AND fast-PASS, ADR-072 §결정 6 invariant 정합)"
    return 0  # exit 0 PASS
  fi

  return 1  # not exempt — proceed to step 2+
}

# ----------------------------------------------------------------------
# Step 2-6: full orchestration (helper lib delegate, business logic 0)
# ----------------------------------------------------------------------
_step_2_enum_closed_set_verify() {
  local enum_origin="${CANARY_CONSUMER_EVIDENCE_ORIGIN:-wrapper_self}"
  local enum_failure_mode="${PROMOTION_GATE_FAILURE_MODE:-warning_first}"
  local result rc

  # canary_consumer_evidence_origin
  result=$(_validate_enum_closed_set "canary_consumer_evidence_origin" "$enum_origin")
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "[canary-compat] step_2 FAIL: $result" >&2
    return 2
  fi

  # promotion_gate_failure_mode
  result=$(_validate_enum_closed_set "promotion_gate_failure_mode" "$enum_failure_mode")
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "[canary-compat] step_2 FAIL: $result" >&2
    return 2
  fi

  echo "[canary-compat] step_2 PASS: enum closed-set verify OK (origin=$enum_origin / failure_mode=$enum_failure_mode)"
  return 0
}

_step_3_family_7_enumerate() {
  local channel="${CONSUMER_CHANNEL_TIER:-canary}"
  local result rc

  result=$(_enumerate_family_7_canary_versions "$channel" 2>&1)
  rc=$?

  if [[ $rc -eq 2 ]]; then
    echo "[canary-compat] step_3 FAIL: length_invariant=7 breach OR member_enum mismatch" >&2
    echo "$result" >&2
    return 2
  fi

  if [[ $rc -eq 1 ]]; then
    echo "[canary-compat] step_3 WARNING: mock env active or partial data" >&2
  fi

  echo "[canary-compat] step_3 PASS: family_7 enumerate OK (channel=$channel)"
  return 0
}

_step_4_4tuple_measurement_source() {
  local yaml_path="${RECONCILE_CONTRACT_PATH:-docs/inter-plugin-contracts/reconcile-protocol-v1.md}"
  local sub
  local missing=0

  for sub in functional security monitoring testing; do
    local result rc
    result=$(_extract_4tuple_measurement_source "$yaml_path" "$sub" 2>&1)
    rc=$?

    if [[ $rc -eq 2 ]]; then
      echo "[canary-compat] step_4 FAIL: sub-field '$sub' yaml parse error" >&2
      return 2
    fi

    if [[ $rc -eq 1 ]]; then
      echo "[canary-compat] step_4 WARNING: sub-field '$sub' measurement_source not found" >&2
      missing=$((missing + 1))
    fi
  done

  if [[ $missing -gt 0 ]]; then
    echo "[canary-compat] step_4 WARNING: $missing/4 measurement_source field(s) not found — additive only invariant (warning_first)"
    return 1  # warning tier
  fi

  echo "[canary-compat] step_4 PASS: 4-tuple measurement_source verify OK"
  return 0
}

_step_5_three_way_version_diff() {
  local pub_v="${PUBLISHER_VERSION:-}"
  local reg_v="${REGISTRY_VERSION:-}"
  local con_v="${CONSUMER_VERSION:-}"
  local result rc

  result=$(_three_way_version_diff "$pub_v" "$reg_v" "$con_v" 2>&1)
  rc=$?

  if [[ $rc -eq 2 ]]; then
    echo "[canary-compat] step_5 FAIL: 3-way mismatch (ADR-063 Amendment 5 §결정 15 invariant 위배)" >&2
    echo "$result" >&2
    return 2
  fi

  if [[ $rc -eq 1 ]]; then
    echo "[canary-compat] step_5 WARNING: 3-way input partial — Phase 1 warning_first (consumer Tier-2 runtime carrier 영역)"
    return 1
  fi

  echo "[canary-compat] step_5 PASS: 3-way version diff OK ($result)"
  return 0
}

_step_6_promotion_gate_evaluate() {
  local failure_mode="${PROMOTION_GATE_FAILURE_MODE:-warning_first}"
  local has_warning="${1:-0}"  # accumulated warning count from previous steps

  if [[ "$has_warning" -gt 0 ]]; then
    if [[ "$failure_mode" == "blocking_on_pr" ]]; then
      echo "[canary-compat] step_6 FAIL: warning count=$has_warning + failure_mode=blocking_on_pr → exit 2"
      return 2
    fi
    # warning_first default
    echo "[canary-compat] step_6 WARNING: warning count=$has_warning + failure_mode=warning_first → exit 1 (advisory)"
    return 1
  fi

  echo "[canary-compat] step_6 PASS: promotion gate evaluation OK (failure_mode=$failure_mode)"
  return 0
}

# ----------------------------------------------------------------------
# Main orchestration
# ----------------------------------------------------------------------
main() {
  echo "[canary-compat] CFP-991 canary promotion criteria 4-tuple verification (thin orchestrator)"
  echo "[canary-compat] reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding cross-ref"

  # Step 1: Tier-1 exemption fast-PASS check
  if _step_1_tier1_exemption_check; then
    exit 0
  fi

  local warning_count=0
  local rc

  # Step 2: enum closed-set verify
  _step_2_enum_closed_set_verify
  rc=$?
  if [[ $rc -eq 2 ]]; then exit 2; fi

  # Step 3: family_7 enumerate
  _step_3_family_7_enumerate
  rc=$?
  if [[ $rc -eq 2 ]]; then exit 2; fi
  [[ $rc -eq 1 ]] && warning_count=$((warning_count + 1))

  # Step 4: 4-tuple measurement_source verify
  _step_4_4tuple_measurement_source
  rc=$?
  if [[ $rc -eq 2 ]]; then exit 2; fi
  [[ $rc -eq 1 ]] && warning_count=$((warning_count + 1))

  # Step 5: 3-way version diff
  _step_5_three_way_version_diff
  rc=$?
  if [[ $rc -eq 2 ]]; then exit 2; fi
  [[ $rc -eq 1 ]] && warning_count=$((warning_count + 1))

  # Step 6: promotion gate evaluate (final)
  _step_6_promotion_gate_evaluate "$warning_count"
  exit $?
}

# Invocation guard (idempotent source guard)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
