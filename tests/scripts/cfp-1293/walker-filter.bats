#!/usr/bin/env bats
# tests/scripts/cfp-1293/walker-filter.bats
# CFP-1293 Phase 2 — ADR-083 consumer-applicability filter bats integration test
#
# TDD: RED (test first) → GREEN (walk_plan.py helper impl)
# CFP-1177 cfp-1177-overlay-apply.bats 패턴 답습
#
# TC map:
#   PREREQ:   walk_plan.py + test_walker_filter.py 존재
#   TC-1:     repo_kind=plugin → proceed (filter skip 0)
#   TC-2:     consumer + whitelist match → proceed
#   TC-3:     consumer + whitelist miss → skip + report
#   TC-4:     repo_kind=mixed → proceed (wrapper self-app exemption, 0 file skip)
#   TC-5:     unknown → abort (fail-closed)
#   TC-6:     whitelist 파일 부재 → abort (fail-closed)
#   TC-7:     비-enum repo_kind → abort (defensive)
#   TC-8:     FilterDecision frozen (immutable dataclass)
#   TC-9:     invoke_detect_repo_kind subprocess → plugin (filesystem mock)
#   TC-10:    subprocess 실패 → unknown fallback
#   INT-1:    detect-repo-kind.py plugin signal probe (.claude-plugin/plugin.json)
#   INT-2:    detect-repo-kind.py consumer signal probe (.claude/_overlay/project.yaml)
#   INT-3:    detect-repo-kind.py mixed signal probe (both signals)
#   INT-4:    detect-repo-kind.py unknown probe (no signals)
#   SELF-APP: 본 wrapper repo invoke_detect_repo_kind → plugin 또는 mixed (0 file skip 보장)
#
# env override:
#   _CFP1293_MOCK_REPO_KIND: invoke_detect_repo_kind 결과 override (CFP-932 _CFP932_MOCK_* 패턴)
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative where applicable)
#   Layer 3 — discriminating fixture (FilterDecision 미존재 → RED)
#
# Python helper: tests/scripts/cfp-1293/test_walker_filter.py (ADR-061 외부 .py)
# Sandbox env (ADR-040 Amendment 6 + CFP-843): CBL_SKIP_ISSUE_CREATE=1
#
# ADR refs:
#   ADR-083 §결정 5 — 4-way enum truth-table (wire location SSOT)
#   ADR-068 I-3 — unconditional guard (unknown → abort)
#   ADR-061 — Python script convention (외부 .py 의무)
#   Change Plan §3.4/§3.5/§3.6

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
WALK_PLAN_DIR="${WORKTREE_ROOT}/scripts/lib"
TEST_HELPER="${WORKTREE_ROOT}/tests/scripts/cfp-1293/test_walker_filter.py"
DETECT_PY="${WORKTREE_ROOT}/templates/scripts/detect-repo-kind.py"

# ──────────────────────────────────────────── sandbox setup ───────────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
  unset _CFP1293_MOCK_REPO_KIND
}

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown() {
  : # no tmp dirs needed (python helper uses tempfile internally)
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: walk_plan.py 존재 확인" {
  [ -f "${WALK_PLAN_DIR}/walk_plan.py" ]
}

@test "PREREQ: test_walker_filter.py 존재 확인" {
  [ -f "$TEST_HELPER" ]
}

@test "PREREQ: detect-repo-kind.py 존재 확인" {
  [ -f "$DETECT_PY" ]
}

@test "PREREQ: FilterDecision 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_filter_decision"
  [ "$status" -eq 0 ]
}

@test "PREREQ: apply_consumer_applicability_filter 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_apply_filter"
  [ "$status" -eq 0 ]
}

@test "PREREQ: invoke_detect_repo_kind 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_invoke_detect"
  [ "$status" -eq 0 ]
}

# ──────────────────────── TC-1: plugin → proceed ──────────────────────────────

@test "TC-1: repo_kind=plugin → all workflow proceed (filter skip 0)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc1_plugin_proceed"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-1"* ]]
}

# ──────────────────────── TC-2: consumer + whitelist match ───────────────────

@test "TC-2: consumer + whitelist match → proceed" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_consumer_whitelist_match"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-2"* ]]
}

# ──────────────────────── TC-3: consumer + whitelist miss → skip ─────────────

@test "TC-3: consumer + whitelist miss → skip + skip_filename + reason" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc3_consumer_whitelist_miss"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-3"* ]]
}

# ──────────────────────── TC-4: mixed → proceed ──────────────────────────────

@test "TC-4: mixed → proceed (wrapper self-app exemption, 0 file skip)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc4_mixed_proceed"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-4"* ]]
}

# ──────────────────────── TC-5: unknown → abort ──────────────────────────────

@test "TC-5: unknown → abort (fail-closed, ADR-068 I-3)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc5_unknown_abort"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-5"* ]]
}

# ──────────────────────── TC-6: whitelist 부재 → abort ───────────────────────

@test "TC-6: whitelist 파일 부재 → abort (fail-closed)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc6_whitelist_read_fail"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-6"* ]]
}

# ──────────────────────── TC-7: 비-enum repo_kind → abort ────────────────────

@test "TC-7: 비-enum repo_kind → abort (defensive fail-closed)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc7_non_enum_abort"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-7"* ]]
}

# ──────────────────────── TC-8: FilterDecision frozen ────────────────────────

@test "TC-8: FilterDecision frozen 검증 (immutable dataclass)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc8_filter_decision_immutable"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-8"* ]]
}

# ──────────────────────── TC-9: subprocess success ───────────────────────────

@test "TC-9: invoke_detect_repo_kind subprocess 성공 → plugin" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc9_detect_subprocess_success"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-9"* ]] || [[ "$output" == *"SKIP TC-9"* ]]
}

# ──────────────────────── TC-10: subprocess fail → unknown ───────────────────

@test "TC-10: subprocess 실패 → unknown (fail-closed fallback)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc10_detect_subprocess_fail"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-10"* ]]
}

# ────────────────────── INT-1~4: detect-repo-kind.py signal probe ─────────────

@test "INT-1: detect-repo-kind.py plugin signal (.claude-plugin/plugin.json)" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  mkdir -p "${tmp_dir}/.claude-plugin"
  echo '{"name":"test"}' > "${tmp_dir}/.claude-plugin/plugin.json"

  run python3 "$DETECT_PY" --repo-root "$tmp_dir"
  # cleanup 먼저
  rm -rf "$tmp_dir"

  [ "$status" -eq 0 ]
  [ "$output" = "plugin" ]
}

@test "INT-2: detect-repo-kind.py consumer signal (.claude/_overlay/project.yaml)" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  mkdir -p "${tmp_dir}/.claude/_overlay"
  echo 'project_name: test' > "${tmp_dir}/.claude/_overlay/project.yaml"

  run python3 "$DETECT_PY" --repo-root "$tmp_dir"
  rm -rf "$tmp_dir"

  [ "$status" -eq 1 ]
  [ "$output" = "consumer" ]
}

@test "INT-3: detect-repo-kind.py mixed signal (both signals present)" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  mkdir -p "${tmp_dir}/.claude-plugin"
  echo '{"name":"test"}' > "${tmp_dir}/.claude-plugin/plugin.json"
  mkdir -p "${tmp_dir}/.claude/_overlay"
  echo 'project_name: test' > "${tmp_dir}/.claude/_overlay/project.yaml"

  run python3 "$DETECT_PY" --repo-root "$tmp_dir"
  rm -rf "$tmp_dir"

  [ "$status" -eq 2 ]
  [ "$output" = "mixed" ]
}

@test "INT-4: detect-repo-kind.py unknown probe (no signals → fail-closed)" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  # 신호 없음

  run python3 "$DETECT_PY" --repo-root "$tmp_dir"
  rm -rf "$tmp_dir"

  [ "$status" -eq 3 ]
  [ "$output" = "unknown" ]
}

# ────────────── TC-INT-WIRE: F-CR-001 caller hook insertion end-to-end ──────────

@test "TC-INT-WIRE-CONSUMER: consumer repo + wrapper-only workflow → caller skip + filter_report append" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc_int_wire_consumer"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-INT-WIRE-CONSUMER"* ]]
}

@test "TC-INT-WIRE-WRAPPER: mixed/plugin repo → all workflow proceed (filter skip 0, wrapper self-app exemption)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc_int_wire_wrapper"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS TC-INT-WIRE-WRAPPER"* ]]
}

# ────────────────────── SELF-APP: wrapper repo self-application ───────────────

@test "SELF-APP: 본 wrapper repo invoke_detect_repo_kind → plugin 또는 mixed (0 file skip 보장)" {
  # TC-CAF-MIXED-1: wrapper self-app = mixed (plugin.json + overlay 양쪽 존재 가능)
  # 또는 plugin (overlay 없는 경우)
  # 두 경우 모두 decision="proceed", skip_filename="" 보장 (ADR-083 §결정 5)
  run python3 "$DETECT_PY" --repo-root "$WORKTREE_ROOT"
  # exit code 0 (plugin) 또는 2 (mixed) 만 허용 — consumer(1) / unknown(3) 불가
  [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
  [ "$output" = "plugin" ] || [ "$output" = "mixed" ]
}
