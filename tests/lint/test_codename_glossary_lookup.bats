#!/usr/bin/env bats
#
# test_codename_glossary_lookup.bats — TDD fixture for codename-glossary-lookup lint
# CFP-1764 Story-2, ADR-071 §결정 19 (Amendment 8) mechanical wire
# RED phase: 3 scenarios (script 부재로 fail 예상)
#
# Test cases:
#   scenario 1: codename + 평이 풀이 동반 = pass (exit 0)
#   scenario 2: codename only (평이 풀이 없음) = warning (exit 1)
#   scenario 3: bypass label 부착 = pass (exit 0)
#
# ADR-061 §결정 11 ReDoS-safe: line-by-line scan, anchored simple patterns
# ADR-060 §결정 15 exit codes: 0=pass, 1=warning, 2=error

setup() {
  export TMPDIR_FIX
  TMPDIR_FIX=$(mktemp -d)
  export SCRIPT_PATH="${BATS_TEST_DIRNAME}/../../scripts/check-codename-glossary-lookup.sh"
}

teardown() {
  rm -rf "${TMPDIR_FIX}"
}

@test "scenario 1: codename + 평이 풀이 동반 = pass (exit 0)" {
  cat > "${TMPDIR_FIX}/sample.md" <<'EOF'
Story ("작업 단위") 진행 시 ADR (결정 기록) 참조.
EOF
  run bash "${SCRIPT_PATH}" --file "${TMPDIR_FIX}/sample.md"
  [ "${status}" -eq 0 ]
}

@test "scenario 2: codename only = warning (exit 1)" {
  cat > "${TMPDIR_FIX}/sample.md" <<'EOF'
Story 진행 시 ADR drift 검사.
EOF
  run bash "${SCRIPT_PATH}" --file "${TMPDIR_FIX}/sample.md"
  [ "${status}" -eq 1 ]
}

@test "scenario 3: bypass label = pass (exit 0)" {
  cat > "${TMPDIR_FIX}/sample.md" <<'EOF'
Story 진행 시 ADR drift 검사.
EOF
  run bash "${SCRIPT_PATH}" --file "${TMPDIR_FIX}/sample.md" --bypass-label="hotfix-bypass:codename-glossary-lookup"
  [ "${status}" -eq 0 ]
}
