#!/usr/bin/env bash
# scripts/lib/canary-compatibility-helpers.sh — canary promotion criteria 4-tuple verify helpers
#
# CFP-991 (Wave 4 sub-Epic #1 Story-4 — canary promotion criteria enforcement layer)
# Carrier ADR: ADR-72 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14
# RefactorAgent B-3 + A-3 (thin orchestrator + helper lib extraction CFP-954 gh-api-helpers.sh 선례 답습)
#
# 4 helper function:
#   1. _extract_4tuple_measurement_source()       — promotion_criteria_4tuple sub measurement_source 파싱
#   2. _enumerate_family_7_canary_versions()      — publisher_versions[7] array enumerate (length=7 invariant)
#   3. _three_way_version_diff()                  — publisher↔registry↔consumer 3-way version diff
#   4. _validate_enum_closed_set()                — closed-enum 값 검증 (canary_consumer_evidence_origin / promotion_gate_failure_mode)
#
# Test override env (_CFP991_MOCK_* namespace, ADR-040 Amendment 6 §결정 7.D probe sandbox env scoping):
#   _CFP991_MOCK_MARKETPLACE_CHANNELS  — cross-repo gh api /repos/mclayer/marketplace/contents/marketplace.json mock (channels[] verbatim 주입)
#   _CFP991_MOCK_FAMILY_VERSIONS       — 7-plugin version array mock (codeforge / codeforge-{requirements,design,develop,review,test,pmo})
#   _CFP991_MOCK_DRIFT_THRESHOLD       — configurable threshold mock (default 24h, test 0s override)
#
# Exit codes (3-tier, ADR-060 §결정 15 정합):
#   0 = PASS (success)
#   1 = warning (missing data / network 일시 실패 / sandbox-bound fetch fail — advisory only, hotfix-bypass:canary-promotion-criteria bypass 가능)
#   2 = mechanical anchor invalid (schema breach / real divergence — hard fail + Issue auto-create)

# Idempotent source guard (multi-source 시 redefine 회피) — gh-api-helpers.sh 패턴 답습
if declare -f _validate_enum_closed_set >/dev/null 2>&1; then
  return 0
fi

# Family 7 plugin member enum (codeforge family scope SSOT — ADR-016 §결정 1 + Amendment 3)
readonly _CFP991_FAMILY_MEMBER_ENUM=(
  "codeforge"
  "codeforge-requirements"
  "codeforge-design"
  "codeforge-develop"
  "codeforge-test"
  "codeforge-review"
  "codeforge-pmo"
)
readonly _CFP991_FAMILY_LENGTH_INVARIANT=7

# Closed-set enum SSOT (reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding fields)
readonly _CFP991_CANARY_EVIDENCE_ORIGIN_ENUM=("wrapper_self" "consumer_self" "mixed")
readonly _CFP991_PROMOTION_GATE_FAILURE_MODE_ENUM=("warning_first" "blocking_on_pr")

# ----------------------------------------------------------------------
# Helper 1: _extract_4tuple_measurement_source()
# Usage: _extract_4tuple_measurement_source "<yaml-path>" "<sub-field>"
#   $1 = yaml file path (예: reconcile-protocol-v1.md frontmatter 또는 schema yaml block)
#   $2 = sub-field name (functional / security / monitoring / testing)
# Output: stdout = measurement_source string (정상 시) / stderr = error log (실패 시)
# Exit: 0 = PASS / 1 = warning (field 부재 — additive only invariant) / 2 = mechanical fail (yaml parse error)
# ----------------------------------------------------------------------
_extract_4tuple_measurement_source() {
  local yaml_path="$1"
  local sub_field="$2"

  if [[ ! -f "$yaml_path" ]]; then
    echo "[canary-compat] WARNING: yaml path not found — $yaml_path" >&2
    return 1
  fi

  # Validate sub_field enum
  case "$sub_field" in
    functional|security|monitoring|testing) ;;
    *)
      echo "[canary-compat] ERROR: invalid sub-field '$sub_field' — expected one of: functional / security / monitoring / testing" >&2
      return 2
      ;;
  esac

  # ADR-061 §결정 1 — 외부 Python 파일 위임 (inline heredoc 금지, Windows Git Bash $var 치환 충돌 해소)
  # extract_4tuple_measurement_source.py: POSIX/Windows 경로 양형 지원 + sub_field enum 검증 포함
  local _extract_py="${_CFP991_SCRIPT_DIR:-$(dirname "${BASH_SOURCE[0]}")}/extract_4tuple_measurement_source.py"
  if [[ ! -f "$_extract_py" ]]; then
    # Fallback: lib 디렉토리 상대 탐색
    _extract_py="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/extract_4tuple_measurement_source.py"
  fi

  if [[ ! -f "$_extract_py" ]]; then
    echo "[canary-compat] ERROR: extract_4tuple_measurement_source.py not found" >&2
    return 2
  fi

  # F-CR-991-C FIX: python3 미존재 / 인터프리터 오류(rc≥3) → exit 2 (hard fail)
  # rc=127 = interpreter absent, rc=1 = generic error — 모두 warning(exit 1) 오분류 차단
  command -v python3 >/dev/null 2>&1 || {
    echo "[canary-compat] ERROR: python3 unavailable — interpreter-absent는 data-gap(warning)이 아닌 tool-fail(hard fail)" >&2
    return 2
  }

  local result rc
  result=$(python3 "$_extract_py" "$yaml_path" "$sub_field" 2>/dev/null)
  rc=$?

  if [[ $rc -eq 2 ]]; then
    echo "[canary-compat] ERROR: measurement_source parse error for '$sub_field' in $yaml_path" >&2
    return 2
  fi

  # rc >= 3: 예상 외 인터프리터 오류 → hard fail (3-tier contract: 0/1/2 외 rc = 설명불가 오류)
  if [[ $rc -ge 3 ]]; then
    echo "[canary-compat] ERROR: python3 unexpected rc=$rc (not in 3-tier contract 0/1/2) — hard fail" >&2
    return 2
  fi

  if [[ $rc -ne 0 ]] || [[ -z "$result" ]]; then
    echo "[canary-compat] WARNING: measurement_source for '$sub_field' not found in $yaml_path" >&2
    return 1
  fi

  echo "$result"
  return 0
}

# ----------------------------------------------------------------------
# Helper 2: _enumerate_family_7_canary_versions()
# Usage: _enumerate_family_7_canary_versions [<consumer-channel>]
#   $1 = consumer channel tier (optional, default: "canary")
# Output: stdout = "<plugin>:<version>" lines × 7 (member_enum order)
# Exit: 0 = PASS (7 entries enumerated, length_invariant=7 met)
#       1 = warning (mock env active or partial data — additive only)
#       2 = mechanical fail (length_invariant=7 breach OR member enum mismatch)
# ----------------------------------------------------------------------
_enumerate_family_7_canary_versions() {
  local channel="${1:-canary}"
  local count=0
  local plugin

  # Mock env override (test-only — production NEVER read)
  if [[ -n "${_CFP991_MOCK_FAMILY_VERSIONS:-}" ]]; then
    echo "$_CFP991_MOCK_FAMILY_VERSIONS"
    # Count lines for length invariant check
    count=$(echo "$_CFP991_MOCK_FAMILY_VERSIONS" | grep -c "^")
    if [[ "$count" -ne "$_CFP991_FAMILY_LENGTH_INVARIANT" ]]; then
      echo "[canary-compat] ERROR: mock family_versions length=$count != invariant=$_CFP991_FAMILY_LENGTH_INVARIANT (RefactorAgent C-3 / DataMigrationArch INV-C)" >&2
      return 2
    fi
    # F-CR-991-B FIX: mock path 안 plugin name enum 검증
    # 라인별 <name>:<version> 파싱 후 name ∈ _CFP991_FAMILY_MEMBER_ENUM 확인
    # 임의 이름(random-plugin-*) 주입 시 exit 2 hard fail — member_enum open_extension:false 정합
    local line name
    while IFS= read -r line; do
      name="${line%%:*}"
      local found=0
      local member
      for member in "${_CFP991_FAMILY_MEMBER_ENUM[@]}"; do
        if [[ "$name" == "$member" ]]; then
          found=1
          break
        fi
      done
      if [[ $found -eq 0 ]]; then
        echo "[canary-compat] ERROR: mock plugin name '$name' NOT in member_enum — closed-set invariant 위배 (F-CR-991-B fix)" >&2
        return 2
      fi
    done <<< "$_CFP991_MOCK_FAMILY_VERSIONS"
    return 1  # warning: mock env active
  fi

  # Production: enumerate family 7 plugin from member_enum SSOT
  for plugin in "${_CFP991_FAMILY_MEMBER_ENUM[@]}"; do
    # Default: emit placeholder version (real fetch = consumer-side runtime, wrapper Story-4 scope 외)
    echo "${plugin}:tier=${channel}:version_pending_runtime_fetch"
    count=$((count + 1))
  done

  # Length invariant check (RefactorAgent C-3 — length_invariant=7 strict)
  if [[ "$count" -ne "$_CFP991_FAMILY_LENGTH_INVARIANT" ]]; then
    echo "[canary-compat] ERROR: family_7 enumeration count=$count != length_invariant=$_CFP991_FAMILY_LENGTH_INVARIANT (ADR-016 §결정 1 family scope invariant 위배)" >&2
    return 2
  fi

  return 0
}

# ----------------------------------------------------------------------
# Helper 3: _three_way_version_diff()
# Usage: _three_way_version_diff "<publisher-version>" "<registry-version>" "<consumer-version>"
#   $1 = publisher .claude-plugin/plugin.json .version
#   $2 = registry marketplace.json plugins[name=<plugin>].channels[tier=canary].version
#        (mock override: _CFP991_MOCK_MARKETPLACE_CHANNELS — channels[] verbatim 주입)
#   $3 = consumer .codeforge.channel.tier=canary declared (placeholder OR actual)
# Output: stdout = "MATCH" (3-way byte-identical) OR "MISMATCH: <details>" (stderr 동반)
# Exit: 0 = MATCH / 1 = warning (mock env active OR drift within threshold)
#       2 = MISMATCH (ADR-063 Amendment 5 §결정 15 invariant 위배)
# §4.8 orthogonality_invariant 재사용 — pin 가용성 ≠ version 정합성 conflate 금지
# _CFP991_MOCK_MARKETPLACE_CHANNELS mock env: cross-repo gh api fetch 대체 (test-only)
# _CFP991_MOCK_DRIFT_THRESHOLD mock env: configurable threshold override (default 24h=86400s, test 0s override)
# ----------------------------------------------------------------------
_three_way_version_diff() {
  local pub_v="$1"
  local reg_v="$2"
  local con_v="$3"

  # F-CR-991-G FIX: _CFP991_MOCK_MARKETPLACE_CHANNELS mock env wire
  # production: registry version = marketplace.json channels[tier=canary].version (cross-repo gh api fetch)
  # test-only: _CFP991_MOCK_MARKETPLACE_CHANNELS 주입 시 reg_v 를 mock channels[] 에서 파싱
  if [[ -n "${_CFP991_MOCK_MARKETPLACE_CHANNELS:-}" ]]; then
    # mock channels[] 에서 canary tier version 추출 (format: "tier=canary version=<ver>" 단순 KV)
    local mock_canary_ver
    mock_canary_ver=$(echo "$_CFP991_MOCK_MARKETPLACE_CHANNELS" | grep "tier=canary" | grep -o "version=[^[:space:]]*" | cut -d= -f2)
    if [[ -n "$mock_canary_ver" ]]; then
      reg_v="$mock_canary_ver"
      echo "[canary-compat] WARNING: _CFP991_MOCK_MARKETPLACE_CHANNELS active — registry version mock-injected: $reg_v" >&2
    fi
  fi

  # F-CR-991-G FIX: _CFP991_MOCK_DRIFT_THRESHOLD mock env wire
  # production: drift threshold = 86400s (24h default, ADR-040 Amendment 6 §결정 7.D probe sandbox env scoping)
  # test-only: 0s override for instant drift detection in discriminating fixture
  local drift_threshold="${_CFP991_MOCK_DRIFT_THRESHOLD:-86400}"
  # drift_threshold 범위 검증 (0 이상 정수 — 음수 및 비정수 = warning tier, override 적용 안 함)
  if ! [[ "$drift_threshold" =~ ^[0-9]+$ ]]; then
    echo "[canary-compat] WARNING: _CFP991_MOCK_DRIFT_THRESHOLD invalid='$drift_threshold' — falling back to default 86400s" >&2
    drift_threshold=86400
  fi
  # drift_threshold read 확인 (production run 시 default 24h 적용 — 테스트 0s override 경로 분기)
  if [[ "$drift_threshold" -eq 0 ]]; then
    echo "[canary-compat] WARNING: drift_threshold=0s (test override active — instant detection mode)" >&2
  fi

  # Empty input handling (warning tier — Phase 1 = data 부재 OK)
  if [[ -z "$pub_v" || -z "$reg_v" || -z "$con_v" ]]; then
    echo "[canary-compat] WARNING: 3-way input partial (pub='$pub_v' reg='$reg_v' con='$con_v') — Phase 1 warning_first" >&2
    echo "MISMATCH: partial input (data 부재 영역, 영구 Tier-2 runtime carrier)"
    return 1
  fi

  # Byte-identical match (semver normalize 안 함 — 5.83.0 ≠ 5.83 ≠ v5.83.0 모두 mismatch)
  if [[ "$pub_v" == "$reg_v" && "$reg_v" == "$con_v" ]]; then
    echo "MATCH"
    return 0
  fi

  echo "[canary-compat] ERROR: 3-way mismatch (publisher='$pub_v' registry='$reg_v' consumer='$con_v') — ADR-063 Amendment 5 §결정 15 invariant 위배" >&2
  echo "MISMATCH: publisher=$pub_v registry=$reg_v consumer=$con_v"
  return 2
}

# ----------------------------------------------------------------------
# Helper 4: _validate_enum_closed_set()
# Usage: _validate_enum_closed_set "<enum-name>" "<value>"
#   $1 = enum-name (canary_consumer_evidence_origin / promotion_gate_failure_mode)
#   $2 = value to validate
# Output: stdout = "VALID" (정상) / "INVALID: <details>" (실패, stderr 동반)
# Exit: 0 = VALID / 2 = INVALID (open_extension: false closed-set invariant 위배)
# RefactorAgent C-1 + C-2 (open_extension: false closed-set strict)
# ----------------------------------------------------------------------
_validate_enum_closed_set() {
  local enum_name="$1"
  local value="$2"
  local valid_values=()

  case "$enum_name" in
    canary_consumer_evidence_origin)
      valid_values=("${_CFP991_CANARY_EVIDENCE_ORIGIN_ENUM[@]}")
      ;;
    promotion_gate_failure_mode)
      valid_values=("${_CFP991_PROMOTION_GATE_FAILURE_MODE_ENUM[@]}")
      ;;
    *)
      echo "[canary-compat] ERROR: unknown enum '$enum_name' — expected one of: canary_consumer_evidence_origin / promotion_gate_failure_mode" >&2
      return 2
      ;;
  esac

  local v
  for v in "${valid_values[@]}"; do
    if [[ "$value" == "$v" ]]; then
      echo "VALID"
      return 0
    fi
  done

  # Closed-set invariant 위배 (RefactorAgent C-1 / C-2 — open_extension: false)
  local joined
  joined=$(IFS=,; echo "${valid_values[*]}")
  echo "[canary-compat] ERROR: enum '$enum_name' value '$value' NOT in closed-set [$joined] — RefactorAgent C-1/C-2 open_extension: false invariant 위배" >&2
  echo "INVALID: '$value' not in [$joined]"
  return 2
}
