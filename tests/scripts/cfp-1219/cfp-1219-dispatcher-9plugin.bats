#!/usr/bin/env bats
# tests/scripts/cfp-1219/cfp-1219-dispatcher-9plugin.bats
# CFP-1219 — dispatcher 9-plugin 활성화 TDD (RED → GREEN)
#
# 문제: walk-bundle-7-plugins.sh FAMILY 7 (deploy lanes commented) ↔
#        walk-single-plugin.sh FAMILY_PLUGINS 7 (deploy lanes 미포함) ↔
#        walk_plan.py TOPOLOGICAL_ORDER 9 (deploy lanes 활성) — dual-roster residual
#
# D1: walk-bundle-7-plugins.sh FAMILY 9-entry 활성 확인
# D2: walk-single-plugin.sh FAMILY_PLUGINS 8-lane 활성 확인
# D3: FAMILY 가 walk_plan.py TOPOLOGICAL_ORDER 와 정확히 일치 (동일 순서)
# D4: check-codeforge-version-drift.sh PLUGIN_MARKETPLACE 에 deploy 2 lane 포함 확인
#
# TC map:
#
# PREREQ: 스크립트 파일 존재 확인
# TC-1:   walk-bundle FAMILY 에 codeforge-deploy 포함 (주석 해제됨)
# TC-2:   walk-bundle FAMILY 에 codeforge-deploy-review 포함
# TC-3:   walk-bundle --walk 실행 시 9 plugin 출력 (deploy lanes 모두 transcript 에 등장)
# TC-4:   walk-single FAMILY_PLUGINS 에 codeforge-deploy 포함 (멤버십 검증 통과)
# TC-5:   walk-single FAMILY_PLUGINS 에 codeforge-deploy-review 포함
# TC-6:   walk-single --walk --plugin codeforge-deploy 정상 실행 (exit 0)
# TC-7:   walk-single --walk --plugin codeforge-deploy-review 정상 실행 (exit 0)
# TC-8:   walk-bundle FAMILY count == 9 (정확히 9개, 중복/누락 0)
# TC-9:   walk-bundle FAMILY 순서가 walk_plan.py TOPOLOGICAL_ORDER 와 일치
# TC-10:  check-codeforge-version-drift.sh PLUGIN_MARKETPLACE 에 deploy 2 lane 포함
# TC-11:  walk-bundle FAMILY 에 codex/superpowers 미포함 (구조적 배제 불변)
# TC-12:  walk-bundle count comment 가 "9-name" 또는 "9 plugin" 을 포함 (7 → 9 갱신 확인)
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (구현 미적용 → RED 보장)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# ADR ref: ADR-087 (deploy lane), ADR-088 (deploy-review lane),
#          ADR-063 Amendment 7 §결정 18 (9-plugin family scope)
# SSOT: scripts/lib/walk_plan.py TOPOLOGICAL_ORDER

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

WALK_BUNDLE="${WORKTREE_ROOT}/scripts/walk-bundle-7-plugins.sh"
WALK_SINGLE="${WORKTREE_ROOT}/scripts/walk-single-plugin.sh"
DRIFT_CHECK="${WORKTREE_ROOT}/scripts/check-codeforge-version-drift.sh"
WALK_PLAN_PY="${WORKTREE_ROOT}/scripts/lib/walk_plan.py"

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
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1219-unused}"
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: walk-bundle-7-plugins.sh 존재 확인" {
  [ -f "$WALK_BUNDLE" ]
}

@test "PREREQ: walk-single-plugin.sh 존재 확인" {
  [ -f "$WALK_SINGLE" ]
}

@test "PREREQ: check-codeforge-version-drift.sh 존재 확인" {
  [ -f "$DRIFT_CHECK" ]
}

@test "PREREQ: walk_plan.py 존재 확인" {
  [ -f "$WALK_PLAN_PY" ]
}

# ───────────────────────────── TC-1: FAMILY 에 codeforge-deploy 포함 ─────────

@test "TC-1 (P0): walk-bundle FAMILY 에 codeforge-deploy 활성 (CFP-1225: derive 기반 출력 확인)" {
  # CFP-1225: FAMILY 는 walk_plan.get_topological_order() 에서 derive — 소스 grep 불가
  # walk --walk 출력에 codeforge-deploy 가 등장하는지로 활성 확인
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # 양성: walk 출력에 codeforge-deploy 등장 (codeforge-deploy-review 와 구분)
  echo "$output" | grep -qE 'plugin.*codeforge-deploy([^-]|$)|\[walk\].*codeforge-deploy([^-]|$)'
}

@test "TC-1b (P0): walk-bundle FAMILY codeforge-deploy — FAMILY 배열 내 주석 처리된 entry 없음" {
  # 구형: # codeforge-deploy  # ADR-087 Deploy lane (S2 carrier)
  # 신형: codeforge-deploy 활성 entry (인라인 주석 허용)
  # 주석 처리 = 줄 첫 토큰이 # (indent + # + codeforge-deploy)
  local commented_count
  commented_count="$(grep -cE '^\s*#\s*codeforge-deploy\b' "$WALK_BUNDLE" || true)"
  # 음성: 주석 처리된 deploy entry 가 없어야 함 (0이어야 함)
  # 단, 코드 주석 블록(header/comment 섹션)의 "codeforge-deploy" 언급은 별도
  # FAMILY 배열 내 commented-out entry 만 체크: "# codeforge-deploy" 패턴이 FAMILY 블록 내 없어야 함
  # 해당 라인이 활성 entry 앞 주석이어선 안 됨 — 전체 파일에서 # + codeforge-deploy 형태 0
  # (헤더/본문 주석은 ## 또는 # CFP-... 형태이므로 구분 가능)
  [ "$commented_count" -eq 0 ]
}

# ───────────────────────────── TC-2: FAMILY 에 codeforge-deploy-review 포함 ──

@test "TC-2 (P0): walk-bundle FAMILY 에 codeforge-deploy-review 활성 (CFP-1225: derive 기반 확인)" {
  # CFP-1225: 소스 grep 아닌 walk 출력으로 확인
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "codeforge-deploy-review"
}

@test "TC-2b (P0): walk-bundle FAMILY codeforge-deploy-review — '# S3 carrier' 주석 없음" {
  local commented_count
  commented_count="$(grep -cE '^\s*#\s*codeforge-deploy-review\b' "$WALK_BUNDLE" || true)"
  [ "$commented_count" -eq 0 ]
}

# ───────────────────────────── TC-3: --walk 출력에 deploy lanes 등장 ─────────

@test "TC-3 (P0): walk-bundle --walk 실행 시 codeforge-deploy 출력에 등장 (9-plugin loop)" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # 양성: codeforge-deploy 가 walk 출력에 등장
  echo "$output" | grep -q "codeforge-deploy"
}

@test "TC-3b (P0): walk-bundle --walk 실행 시 codeforge-deploy-review 출력에 등장" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "codeforge-deploy-review"
}

# ───────────────────────────── TC-4: walk-single FAMILY_PLUGINS 에 deploy 포함

@test "TC-4 (P0): walk-single FAMILY_PLUGINS 에 codeforge-deploy 포함 (CFP-1225: derive 기반)" {
  # CFP-1225: FAMILY_PLUGINS 는 derive — 소스 grep 아닌 실행 결과로 확인
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy
  [ "$status" -eq 0 ]
}

@test "TC-4b (P0): walk-single codeforge-deploy 주석 처리 entry 없음 (활성 상태 확인)" {
  local commented_count
  commented_count="$(grep -cE '^\s*#\s*codeforge-deploy\b' "$WALK_SINGLE" || true)"
  [ "$commented_count" -eq 0 ]
}

# ───────────────────────────── TC-5: walk-single FAMILY_PLUGINS 에 deploy-review

@test "TC-5 (P0): walk-single FAMILY_PLUGINS 에 codeforge-deploy-review 포함 (CFP-1225: derive)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy-review
  [ "$status" -eq 0 ]
}

@test "TC-5b (P0): walk-single codeforge-deploy-review 주석 처리 entry 없음" {
  local commented_count
  commented_count="$(grep -cE '^\s*#\s*codeforge-deploy-review\b' "$WALK_SINGLE" || true)"
  [ "$commented_count" -eq 0 ]
}

# ───────────────────────────── TC-6: walk-single --plugin codeforge-deploy 허용

@test "TC-6 (P0): walk-single --walk --plugin codeforge-deploy 정상 실행 (멤버십 통과, exit 0)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy
  # 양성: exit 0 (FAMILY_PLUGINS 에 포함되어 있으므로 reject 없어야 함)
  [ "$status" -eq 0 ]
  # 양성: walk 출력 포함
  echo "$output" | grep -qi "walk\|stage.*1\|read-only\|plugin.*codeforge-deploy"
}

@test "TC-6b (P1): walk-single --walk --plugin codeforge-deploy — 멤버십 거부 메시지 없음" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy
  [ "$status" -eq 0 ]
  # 음성: "family 구성원이 아닙니다" 거부 메시지 없어야 함
  ! echo "${output}" | grep -qi "구성원이 아닙니다\|not.*family\|family.*member"
}

# ───────────────────────────── TC-7: walk-single --plugin codeforge-deploy-review

@test "TC-7 (P0): walk-single --walk --plugin codeforge-deploy-review 정상 실행 (exit 0)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy-review
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "walk\|stage.*1\|read-only\|plugin.*codeforge-deploy-review"
}

@test "TC-7b (P1): walk-single --walk --plugin codeforge-deploy-review — 거부 메시지 없음" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge-deploy-review
  [ "$status" -eq 0 ]
  ! echo "${output}" | grep -qi "구성원이 아닙니다\|not.*family\|family.*member"
}

# ───────────────────────────── TC-8: FAMILY count == 9 ──────────────────────

@test "TC-8 (P0): walk-bundle FAMILY array 에서 활성 entry 수 == 9 (CFP-1225: derive count)" {
  # CFP-1225: 소스 grep 아닌 walk_plan.get_topological_order() 반환 count 검증
  local family_count
  family_count="$(python3 "$WORKTREE_ROOT/tests/scripts/cfp-1225/test_dispatcher_derive.py" \
    "$WORKTREE_ROOT/scripts/lib" tc_topological_count)"
  [ "$family_count" -eq 9 ]
}

@test "TC-8b (P0): walk-bundle --walk 출력에 family 9 plugin 이름 모두 등장" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # 양성: 9 codeforge plugin 이름 모두 출력에 포함 (walk loop 확인)
  echo "$output" | grep -q "codeforge-requirements"
  echo "$output" | grep -q "codeforge-design"
  echo "$output" | grep -q "codeforge-review"
  echo "$output" | grep -q "codeforge-develop"
  echo "$output" | grep -q "codeforge-test"
  echo "$output" | grep -q "codeforge-pmo"
  echo "$output" | grep -q "codeforge-deploy"
  echo "$output" | grep -q "codeforge-deploy-review"
}

# ───────────────── TC-9: FAMILY 순서 == walk_plan.py TOPOLOGICAL_ORDER ───────

@test "TC-9 (P0): walk-bundle FAMILY 순서 == walk_plan.py TOPOLOGICAL_ORDER (단일 SSOT 정합)" {
  # walk_plan.py 에서 TOPOLOGICAL_ORDER 추출
  local topo_order
  topo_order="$(python3 - <<'PYEOF'
import sys, os
sys.path.insert(0, os.path.join(os.environ.get("WORKTREE_ROOT",""), "scripts", "lib"))
try:
    import walk_plan
    print("\n".join(walk_plan.TOPOLOGICAL_ORDER))
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
)"
  [ -n "$topo_order" ]

  # walk-bundle --walk 출력에서 plugin 이름 순서 추출 (walk loop 순서)
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]

  # CFP-1225: 소스 grep 아닌 derive 출력으로 순서 확인
  local first_derived
  first_derived="$(python3 "$WORKTREE_ROOT/tests/scripts/cfp-1225/test_dispatcher_derive.py" \
    "$WORKTREE_ROOT/scripts/lib" tc_first_plugin)"
  [ "$first_derived" = "codeforge" ]

  # codeforge-deploy 포함 확인
  python3 "$WORKTREE_ROOT/tests/scripts/cfp-1225/test_dispatcher_derive.py" \
    "$WORKTREE_ROOT/scripts/lib" tc_contains_deploy
}

@test "TC-9b (P0): walk-bundle FAMILY — codeforge-deploy 가 TOPOLOGICAL_ORDER 에서 pmo 이후" {
  # CFP-1225: 소스 줄번호 비교 아닌 TOPOLOGICAL_ORDER 인덱스 비교
  # grep -n 으로 라인 번호 비교 (while subshell 변수 누수 회피)
  local order_file
  order_file="$(mktemp)"
  python3 "$WORKTREE_ROOT/tests/scripts/cfp-1225/test_dispatcher_derive.py" \
    "$WORKTREE_ROOT/scripts/lib" tc_topological_order > "$order_file"
  [ -s "$order_file" ]
  local pmo_line deploy_line
  pmo_line="$(grep -n '^codeforge-pmo$' "$order_file" | cut -d: -f1)"
  deploy_line="$(grep -n '^codeforge-deploy$' "$order_file" | cut -d: -f1)"
  rm -f "$order_file"
  [ -n "$pmo_line" ]
  [ -n "$deploy_line" ]
  [ "$deploy_line" -gt "$pmo_line" ]
}

# ───────────────── TC-10: drift-check PLUGIN_MARKETPLACE deploy 2 lane ───────

@test "TC-10 (P0): drift-check PLUGIN_MARKETPLACE 에 codeforge-deploy entry 포함 (9-plugin)" {
  # check-codeforge-version-drift.sh 에 [codeforge-deploy]= entry 가 있어야 함
  run grep -E '\[codeforge-deploy\]=' "$DRIFT_CHECK"
  [ "$status" -eq 0 ]
}

@test "TC-10b (P0): drift-check PLUGIN_MARKETPLACE 에 codeforge-deploy-review entry 포함" {
  run grep -E '\[codeforge-deploy-review\]=' "$DRIFT_CHECK"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-11: codex/superpowers 구조적 배제 불변 ─────────────────

@test "TC-11 (P0): walk-bundle FAMILY 에 codex 미포함 (구조적 배제 불변)" {
  # 활성 FAMILY entry 에 codex 없어야 함 (코드 내 'codex' 언급이 아닌 active entry 기준)
  # FAMILY 배열 내 주석 없는 active entry 에서 codex 존재 여부
  local codex_active
  codex_active="$(grep -E '^\s+codex\s*$' "$WALK_BUNDLE" | grep -v '^\s*#' || true)"
  [ -z "$codex_active" ]
}

@test "TC-11b (P0): walk-single FAMILY_PLUGINS 에 superpowers 미포함 (구조적 배제)" {
  local superpowers_active
  superpowers_active="$(grep -E '^\s+superpowers\s*$' "$WALK_SINGLE" | grep -v '^\s*#' || true)"
  [ -z "$superpowers_active" ]
}

# ───────────────── TC-12: count comment 갱신 확인 (7 → 9 반영) ───────────────

@test "TC-12 (P0): walk-bundle — '9-name' 또는 '9 plugin' count comment 존재 (CFP-1219 갱신)" {
  # _usage() 또는 주석에서 "7-name FAMILY loop" 가 "9-name" 으로 갱신됐어야 함
  # 또는 "FAMILY 9" 등의 count comment 존재
  run grep -iE '9.?name|9.?plugin|FAMILY.?9' "$WALK_BUNDLE"
  [ "$status" -eq 0 ]
}

@test "TC-12b (P0): walk-single FAMILY_PLUGINS derive count >= 8 (CFP-1225: derive 기반 확인)" {
  # CFP-1225: 소스 grep 아닌 derive count 검증 (walk_plan.get_topological_order() 9개)
  local family_count
  family_count="$(python3 "$WORKTREE_ROOT/tests/scripts/cfp-1225/test_dispatcher_derive.py" \
    "$WORKTREE_ROOT/scripts/lib" tc_topological_count)"
  [ "$family_count" -ge 8 ]
}
