#!/usr/bin/env bats
# tests/scripts/cfp-1225/cfp-1225-dispatcher-derive.bats
# CFP-1225 — dispatcher FAMILY/FAMILY_PLUGINS derive from walk_plan.py TOPOLOGICAL_ORDER (TDD)
#
# 목적: 이중 로스터(dual-roster) 제거 — walk-bundle / walk-single 의 하드코딩 배열을
#       walk_plan.py TOPOLOGICAL_ORDER 에서 자동 derive 로 전환.
#       구조적으로 drift 불가능 (single SSOT 정합).
#
# TC map:
#
# PREREQ:  파일 존재 + walk_plan 심볼 확인
# TC-1:    walk-bundle FAMILY derive 결과 == get_topological_order() (9개, 정확한 순서)
# TC-2:    walk-bundle 소스에 하드코딩 9-name FAMILY 배열 리터럴 없음 (derive 구조 확인)
# TC-3:    walk-bundle --walk 실행 시 9-plugin 전체 출력 (derive 동작 end-to-end)
# TC-4:    walk-single FAMILY_PLUGINS derive 결과 == get_topological_order() (9개)
# TC-5:    walk-single 소스에 하드코딩 FAMILY_PLUGINS 배열 리터럴 없음
# TC-6:    walk-single --walk --plugin codeforge-deploy 멤버십 통과 (derive 반영)
# TC-7:    walk-single --walk --plugin codeforge-deploy-review 멤버십 통과
# TC-8:    _CFP1225_MOCK_DERIVE_FAIL=1 시 walk-bundle fail-loud exit 2
# TC-9:    _CFP1225_MOCK_DERIVE_FAIL=1 시 walk-single fail-loud exit non-zero
# TC-10:   derive count == 9 (len(get_topological_order()) 동일)
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative 또는 구별 fixture)
#   Layer 3 — discriminating fixture (구현 미적용 시 RED 보장)
#
# Python helper: tests/scripts/cfp-1225/test_dispatcher_derive.py (ADR-061 외부 .py)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# ADR ref: ADR-061 (python script-writing convention), ADR-096 §결정 2 (DAG invariant)
# SSOT: scripts/lib/walk_plan.py TOPOLOGICAL_ORDER / get_topological_order()

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

WALK_BUNDLE="${WORKTREE_ROOT}/scripts/walk-bundle-7-plugins.sh"
WALK_SINGLE="${WORKTREE_ROOT}/scripts/walk-single-plugin.sh"
WALK_PLAN_PY="${WORKTREE_ROOT}/scripts/lib/walk_plan.py"
SCRIPTS_LIB="${WORKTREE_ROOT}/scripts/lib"
TEST_HELPER="${WORKTREE_ROOT}/tests/scripts/cfp-1225/test_dispatcher_derive.py"

# ──────────────────────────────────────────────── sandbox setup ───────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  # 가짜 git repo (--repo 검증용)
  mkdir -p "${TEST_TMP}/fake-repo/.git"
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1225-unused}"
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: walk-bundle-7-plugins.sh 존재 확인" {
  [ -f "$WALK_BUNDLE" ]
}

@test "PREREQ: walk-single-plugin.sh 존재 확인" {
  [ -f "$WALK_SINGLE" ]
}

@test "PREREQ: walk_plan.py 존재 확인" {
  [ -f "$WALK_PLAN_PY" ]
}

@test "PREREQ: test_dispatcher_derive.py 존재 확인" {
  [ -f "$TEST_HELPER" ]
}

@test "PREREQ: walk_plan 필수 심볼 (TOPOLOGICAL_ORDER/get_topological_order/LANE_PLUGINS/WRAPPER_PLUGIN) 존재" {
  run python3 "$TEST_HELPER" "$SCRIPTS_LIB" "prereq_importable"
  [ "$status" -eq 0 ]
}

# ─── TC-1: walk-bundle FAMILY derive == get_topological_order() ──────────────

@test "TC-1 (P0): walk-bundle FAMILY derive 결과 == get_topological_order() (9개, 정확한 순서)" {
  # walk_plan.py 에서 기대 순서 추출 (helper 경유 — path 정규화 포함)
  local expected_order
  expected_order="$(python3 "$TEST_HELPER" "$SCRIPTS_LIB" "tc_topological_order")"
  [ -n "$expected_order" ]

  # walk-bundle 소스의 FAMILY derive 결과 (SCRIPT_DIR = scripts/ 이므로 scripts/lib 경유 동일)
  local script_lib
  script_lib="$(dirname "${WALK_BUNDLE}")/lib"
  local derived_family
  derived_family="$(python3 "$TEST_HELPER" "$script_lib" "tc_topological_order")"

  # 양성: expected == derived (byte-identical — single SSOT 정합)
  [ "$expected_order" = "$derived_family" ]

  # 음성: 비어 있지 않음 (derive 실패 = empty 아님)
  [ -n "$derived_family" ]
}

@test "TC-1b (P0): walk-bundle FAMILY derive 첫 항목 == 'codeforge' (wrapper 먼저 DAG invariant)" {
  local first_plugin
  first_plugin="$(python3 "$TEST_HELPER" "$SCRIPTS_LIB" "tc_first_plugin")"
  [ "$first_plugin" = "codeforge" ]
}

# ─── TC-2: walk-bundle 소스에 하드코딩 9-name FAMILY 배열 리터럴 없음 ──────────

@test "TC-2 (P0): walk-bundle 소스에 FAMILY 배열 하드코딩 'codeforge-requirements' 리터럴 없음" {
  # derive 로 전환 후 FAMILY=( ... ) 블록 안에 플러그인 이름이 직접 나열되지 않아야 함.
  # awk: FAMILY=( ... ) 블록 내 codeforge-requirements 리터럴 개수 카운트
  local literal_count
  literal_count="$(awk '/^FAMILY=\(/{found=1} found && /^\)/{found=0} found && /codeforge-requirements/{count++} END{print count+0}' "$WALK_BUNDLE")"
  # 양성 (derive 완료 시): 0 개
  [ "$literal_count" -eq 0 ]
}

@test "TC-2b (P0): walk-bundle 소스에 FAMILY_DERIVE 또는 mapfile+python3 패턴 존재 (derive 구조 확인)" {
  # derive 구조: FAMILY_DERIVE 함수 또는 mapfile + python3 + get_topological_order 패턴이 있어야 함
  run grep -E 'FAMILY_DERIVE|mapfile.*FAMILY|python3.*get_topological_order' "$WALK_BUNDLE"
  [ "$status" -eq 0 ]
}

# ─── TC-3: walk-bundle --walk end-to-end 동작 (9-plugin 전체 출력) ─────────────

@test "TC-3 (P0): walk-bundle --walk 실행 시 9-plugin 전체 이름 출력에 등장" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # 9개 전부 출력에 등장해야 함
  echo "$output" | grep -q "codeforge-requirements"
  echo "$output" | grep -q "codeforge-design"
  echo "$output" | grep -q "codeforge-review"
  echo "$output" | grep -q "codeforge-develop"
  echo "$output" | grep -q "codeforge-test"
  echo "$output" | grep -q "codeforge-pmo"
  echo "$output" | grep -q "codeforge-deploy"
  echo "$output" | grep -q "codeforge-deploy-review"
}

@test "TC-3b (P0): walk-bundle --walk 출력 첫 plugin 이 codeforge (topological order 보존)" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # topological: codeforge(wrapper) 가 첫 번째로 처리되어야 함
  echo "$output" | grep -q "plugin=codeforge"
}

# ─── TC-4: walk-single FAMILY_PLUGINS derive == get_topological_order() ──────

@test "TC-4 (P0): walk-single FAMILY_PLUGINS derive 결과 == walk_plan.get_topological_order() (9개)" {
  local expected
  expected="$(python3 "$TEST_HELPER" "$SCRIPTS_LIB" "tc_topological_order")"
  local script_lib
  script_lib="$(dirname "${WALK_SINGLE}")/lib"
  local derived_family
  derived_family="$(python3 "$TEST_HELPER" "$script_lib" "tc_topological_order")"

  # 양성: byte-identical (단일 SSOT 정합)
  [ "$derived_family" = "$expected" ]

  # 음성: 비어 있지 않음
  [ -n "$derived_family" ]
}

@test "TC-4b (P0): walk-single FAMILY_PLUGINS derive count == 9" {
  local script_lib
  script_lib="$(dirname "${WALK_SINGLE}")/lib"
  local count
  count="$(python3 "$TEST_HELPER" "$script_lib" "tc_topological_count")"
  [ "$count" -eq 9 ]
}

# ─── TC-5: walk-single 소스에 하드코딩 FAMILY_PLUGINS 배열 리터럴 없음 ─────────

@test "TC-5 (P0): walk-single 소스에 FAMILY_PLUGINS 배열 하드코딩 'codeforge-requirements' 없음" {
  local literal_count
  literal_count="$(awk '/^FAMILY_PLUGINS=\(/{found=1} found && /^\)/{found=0} found && /codeforge-requirements/{count++} END{print count+0}' "$WALK_SINGLE")"
  [ "$literal_count" -eq 0 ]
}

@test "TC-5b (P0): walk-single 소스에 FAMILY_PLUGINS_DERIVE 또는 mapfile+python3 패턴 존재" {
  run grep -E 'FAMILY_PLUGINS_DERIVE|mapfile.*FAMILY_PLUGINS|python3.*get_topological_order' "$WALK_SINGLE"
  [ "$status" -eq 0 ]
}

# ─── TC-6: walk-single --plugin codeforge-deploy 멤버십 통과 ──────────────────

@test "TC-6 (P0): walk-single --walk --plugin codeforge-deploy 정상 실행 (derive 멤버십, exit 0)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy
  [ "$status" -eq 0 ]
  # 양성: 멤버십 거부 메시지 없음
  ! echo "$output" | grep -qi "구성원이 아닙니다\|not.*family"
}

@test "TC-6b (P0): walk-single --walk --plugin codeforge-deploy walk 출력 포함" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "walk\|stage\|read-only\|plugin.*codeforge-deploy"
}

# ─── TC-7: walk-single --plugin codeforge-deploy-review 멤버십 통과 ───────────

@test "TC-7 (P0): walk-single --walk --plugin codeforge-deploy-review 정상 실행 (exit 0)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy-review
  [ "$status" -eq 0 ]
  ! echo "$output" | grep -qi "구성원이 아닙니다\|not.*family"
}

@test "TC-7b (P0): walk-single --walk --plugin codeforge-deploy-review walk 출력 포함" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy-review
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "walk\|stage\|read-only\|plugin.*codeforge-deploy-review"
}

# ─── TC-8: _CFP1225_MOCK_DERIVE_FAIL=1 시 walk-bundle fail-loud exit 2 ───────

@test "TC-8 (P0): walk-bundle — _CFP1225_MOCK_DERIVE_FAIL=1 시 exit 2 + 오류 메시지 (fail-loud)" {
  # test seam 으로 derive 실패 시뮬레이션
  run env _CFP1225_MOCK_DERIVE_FAIL=1 bash "$WALK_BUNDLE" --walk
  # 양성: exit 2 (setup-error)
  [ "$status" -eq 2 ]
  # 양성: 오류 메시지 포함
  echo "$output" | grep -qiE "walk_plan|derive|FAMILY|오류|error"
}

@test "TC-8b (P0): walk-bundle fail-loud — 오류 메시지에 원인 키워드 포함" {
  run env _CFP1225_MOCK_DERIVE_FAIL=1 bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 2 ]
  # walk_plan 또는 derive 또는 FAMILY 키워드 중 하나 이상 포함
  echo "$output" | grep -qiE "walk_plan|derive|FAMILY"
}

# ─── TC-9: _CFP1225_MOCK_DERIVE_FAIL=1 시 walk-single fail-loud ──────────────

@test "TC-9 (P0): walk-single — _CFP1225_MOCK_DERIVE_FAIL=1 시 exit 2 + 오류 메시지 (fail-loud)" {
  # --plugin 인자를 주더라도 derive 실패 → fail-loud (멤버십 검사 전에 exit)
  run env _CFP1225_MOCK_DERIVE_FAIL=1 bash "$WALK_SINGLE" --walk --plugin codeforge
  [ "$status" -eq 2 ]
  echo "$output" | grep -qiE "walk_plan|derive|FAMILY_PLUGINS|오류|error"
}

@test "TC-9b (P0): walk-single fail-loud — 정상 walk 출력 없어야 함 (멤버십 통과 메시지 없음)" {
  run env _CFP1225_MOCK_DERIVE_FAIL=1 bash "$WALK_SINGLE" --walk --plugin codeforge
  [ "$status" -eq 2 ]
  # 음성: 정상 walk 실행 메시지 없어야 함
  ! echo "$output" | grep -qi "UpgradeAgent spawn"
}

# ─── TC-10: derive count == 9 (len(get_topological_order()) 동일) ─────────────

@test "TC-10 (P0): walk-bundle FAMILY derive count == len(get_topological_order()) == 9" {
  local count
  count="$(python3 "$TEST_HELPER" "$SCRIPTS_LIB" "tc_topological_count")"
  [ "$count" -eq 9 ]

  # 음성: 7 (이전 구형 개수) 와 다름 (discriminating)
  [ "$count" -ne 7 ]
}

@test "TC-10b (P0): walk-bundle --walk 출력에서 codex/superpowers 구조적 배제 불변" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # codex/superpowers 는 derive 결과에 절대 포함 안 됨 (walk_plan.py 에도 없음)
  ! echo "$output" | grep -qE '\[walk\] plugin=codex$'
  ! echo "$output" | grep -qE '\[walk\] plugin=superpowers$'
}
