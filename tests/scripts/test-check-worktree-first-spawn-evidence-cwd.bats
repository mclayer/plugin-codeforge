#!/usr/bin/env bats
# tests/scripts/test-check-worktree-first-spawn-evidence-cwd.bats
# CFP-843 Phase 2 — write-target-path worktree-membership lint + CBL_SKIP_ISSUE_CREATE probe env TC
# Change Plan §6 Test Contract verbatim (6 TC) + FIX-1 no-offset TC (TC-3a/TC-3b)
#
# Test cases:
#   TC-1: write target = worktree root membership → PASS (exit 0, no WARN)
#   TC-2: write target = main repo working tree (cwd reset 재현) → FAIL (WARN emitted, exit 0 — warning tier)
#   TC-3: enforce-from filter — Z-suffix future ENFORCE_FROM → skip (false-positive 0)
#   TC-3a: no-offset future ENFORCE_FROM (no Z/+HH:MM) → exit 0, skip (not TypeError exit 1)
#   TC-3b: no-offset past ENFORCE_FROM → exit 0, enforce (violation WARN emitted)
#   TC-4: BYPASS_WORKTREE_FIRST=1 → short-circuit (exit 0, no scan)
#   TC-5: common-dir skip — worktree common-dir ambiguity → skip (exit 0, no WARN)
#   TC-6: env-scoped probe — CBL_SKIP_ISSUE_CREATE=1 → live Issue create skip (#836 재현 차단)
#
# Mock strategy:
#   WRITE_TARGET_PATHS env (newline-delimited) → override write target list
#   EXPECTED_WORKTREE_ROOT env → override expected worktree root
#   ENFORCE_FROM env → override enforce-from timestamp
#   BYPASS_WORKTREE_FIRST=1 → short-circuit
#   CBL_SKIP_ISSUE_CREATE=1 → probe side-effect suppression (TC-6)
#   CBL_MOCK_ISSUE_CREATE_CALLED path → file written when create called (TC-6 sentinel)
#
# TDD RED 선행 (discriminating fixture genuine fail 입증):
#   TC-2 / TC-6 = genuine fail 대상. 구현 전 RED 확인 의무 (memory feedback_tdd_red_proof_via_stash).
#
# ADR-061 정합: 본 bats 파일 = 5+ 줄 test 로직 → external file (본 file).
# Windows Git Bash 호환: single-quoted heredoc, export 패턴.

WRITE_MEMBERSHIP_SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-write-target-membership.sh"
PROBE_SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-probe-sandbox-env.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR
  # 기본 bypass 비활성
  unset BYPASS_WORKTREE_FIRST || true
  unset CBL_SKIP_ISSUE_CREATE || true
}

teardown() {
  rm -rf "$TEST_DIR"
  unset BYPASS_WORKTREE_FIRST || true
  unset CBL_SKIP_ISSUE_CREATE || true
}

# ------------------------------------------------------------------ TC-1: worktree root membership PASS
@test "TC-1: write target = worktree root path → PASS (no WARN)" {
  # worktree path 형식 = ${HOME}/.claude/worktrees/<repo>/<branch-flat>
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  MOCK_WRITE_TARGET="$MOCK_WORKTREE_ROOT/scripts/check-worktree-first-spawn-evidence-cwd.sh"

  run env \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2020-01-01T00:00:00Z" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier — always exit 0
  [ "$status" -eq 0 ]
  # WARN 미발화
  [[ "$output" != *"WARN"* ]] || [[ "$output" != *"violation"* ]]
}

# ------------------------------------------------------------------ TC-2: main repo violation FAIL (RED target)
@test "TC-2: write target = main repo working tree → WARN violation emitted (RED target)" {
  # main repo path (worktree 아님) = cwd reset 재현
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  # main working tree = worktree 아닌 일반 경로
  MOCK_WRITE_TARGET="/c/workspace/mclayer/plugin-codeforge/scripts/some-script.sh"

  run env \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2020-01-01T00:00:00Z" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier exit 0 유지
  [ "$status" -eq 0 ]
  # WARN 발화 의무 (membership FAIL 감지)
  [[ "$output" == *"WARN"* ]] || [[ "$output" == *"violation"* ]] || [[ "$output" == *"FAIL"* ]]
}

# ------------------------------------------------------------------ TC-3: enforce-from filter boundary
@test "TC-3: enforce-from filter — future ENFORCE_FROM → all targets skipped (false-positive 0)" {
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  # main repo (violation 대상) write target — 하지만 ENFORCE_FROM 이 미래 = skip
  MOCK_WRITE_TARGET="/c/workspace/mclayer/plugin-codeforge/scripts/some-script.sh"

  run env \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2099-01-01T00:00:00Z" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # enforce-from 미래 → skip (exit 0, WARN 없음)
  [ "$status" -eq 0 ]
  [[ "$output" != *"violation"* ]]
}

# ------------------------------------------------------------------ TC-4: BYPASS_WORKTREE_FIRST=1 short-circuit
@test "TC-4: BYPASS_WORKTREE_FIRST=1 → short-circuit (exit 0, no scan)" {
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  MOCK_WRITE_TARGET="/c/workspace/mclayer/plugin-codeforge/scripts/some-script.sh"

  run env \
    BYPASS_WORKTREE_FIRST="1" \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2020-01-01T00:00:00Z" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  # BYPASS 메시지 출력 확인 (5-layer layer 4)
  [[ "$output" == *"BYPASS"* ]] || [[ "$output" == *"skip"* ]]
}

# ------------------------------------------------------------------ TC-5: common-dir skip
@test "TC-5: common-dir path → skip (no WARN, 5-layer layer 5)" {
  # .git/common 경로 = worktree common-dir ambiguity
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  # common-dir path (ambiguous — skip 의무)
  MOCK_WRITE_TARGET="$MOCK_WORKTREE_ROOT/.git/common/ORIG_HEAD"

  run env \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2020-01-01T00:00:00Z" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  # common-dir 경로는 violation WARN 미발화
  [[ "$output" != *"violation"* ]]
}

# ------------------------------------------------------------------ TC-6: CBL_SKIP_ISSUE_CREATE probe env (RED target)
@test "TC-6: CBL_SKIP_ISSUE_CREATE=1 → probe live Issue create suppressed (#836 재현 차단)" {
  # probe-sandbox-env script: CBL_SKIP_ISSUE_CREATE=1 시 Issue create 호출 안 함
  # sentinel: CBL_MOCK_ISSUE_CREATE_CALLED 파일 경로 → create 호출 시 touch
  SENTINEL="$TEST_DIR/issue-create-called.sentinel"

  run env \
    CBL_SKIP_ISSUE_CREATE="1" \
    CBL_MOCK_ISSUE_CREATE_CALLED="$SENTINEL" \
    bash "$PROBE_SCRIPT" --mock-create

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  # sentinel 파일 미생성 = Issue create 호출 안 됨 (#836 차단 확인)
  [ ! -f "$SENTINEL" ]
}

# ------------------------------------------------------------------ TC-3a: no-offset future ENFORCE_FROM → exit 0 (FIX-1 RED target)
@test "TC-3a: no-offset future ENFORCE_FROM (no Z/+HH:MM) → exit 0 skip (not TypeError)" {
  # FIX-1 RED target: 현 parse_iso8601 는 offset-naive datetime 반환 → line-91 aware 비교 TypeError → exit 1
  # 수정 후: offset-naive → UTC 가정 attach → aware 비교 → future → skip, exit 0
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  MOCK_WRITE_TARGET="/c/workspace/mclayer/plugin-codeforge/scripts/some-script.sh"

  run env \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2099-01-01T00:00:00" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # 수정 전: exit 1 (TypeError) → 수정 후: exit 0 (future → skip)
  [ "$status" -eq 0 ]
  # future → skip, violation WARN 없음
  [[ "$output" != *"violation"* ]]
}

# ------------------------------------------------------------------ TC-3b: no-offset past ENFORCE_FROM → exit 0 + enforce
@test "TC-3b: no-offset past ENFORCE_FROM → exit 0 + violation WARN emitted (enforce active)" {
  # 수정 후: offset-naive past → UTC 가정 → past → enforce → violation WARN (exit 0 유지)
  MOCK_WORKTREE_ROOT="/c/Users/test/.claude/worktrees/plugin-codeforge/cfp-843-phase2"
  MOCK_WRITE_TARGET="/c/workspace/mclayer/plugin-codeforge/scripts/some-script.sh"

  run env \
    WRITE_TARGET_PATHS="$MOCK_WRITE_TARGET" \
    EXPECTED_WORKTREE_ROOT="$MOCK_WORKTREE_ROOT" \
    ENFORCE_FROM="2020-01-01T00:00:00" \
    bash "$WRITE_MEMBERSHIP_SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier — exit 0 유지
  [ "$status" -eq 0 ]
  # past ENFORCE_FROM → enforce active → violation WARN 발화 의무
  [[ "$output" == *"WARN"* ]] || [[ "$output" == *"violation"* ]] || [[ "$output" == *"FAIL"* ]]
}
