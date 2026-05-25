#!/usr/bin/env bats
# CFP-1341 / CFP-1316 retro F1 Mandatory carrier
# ADR-040 Amendment 6 §결정 7.J PL inline scope mechanical enforcement gap closure
# ADR-082 §결정 11.A bats RED→GREEN stash proof precedent (TDD discipline)
# CodeQL ReDoS guard: line-by-line parse only (CFP-1497 PR #1499 verbatim 답습)

# Test fixture path
FIXTURE_DIR="$BATS_TEST_DIRNAME/fixtures"
SCRIPT_BIN="$BATS_TEST_DIRNAME/../../../scripts/check-pl-inline-verify-cwd.sh"

setup() {
  # ensure script exists
  [ -f "$SCRIPT_BIN" ]
  # FP-완화 sandbox env (test 영역, MCP write disabled)
  export CBL_SKIP_ISSUE_CREATE=1
}

# ── PASS — no files (empty argv) ──────────────────────────────────────────────

@test "PASS: no files (empty argv)" {
  cd "$BATS_TEST_TMPDIR"
  run bash "$SCRIPT_BIN"
  [ "$status" -eq 0 ]
}

# ── PASS — file with cwd directive (3 forms) ──────────────────────────────────

@test "PASS: form 1 (git -C) cwd directive present" {
  run bash "$SCRIPT_BIN" "$FIXTURE_DIR/pass-form1-git-c.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"WARN-CWD-DIRECTIVE-ABSENT"* ]]
}

@test "PASS: form 2 (cd <path>) cwd directive present" {
  run bash "$SCRIPT_BIN" "$FIXTURE_DIR/pass-form2-cd.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"WARN-CWD-DIRECTIVE-ABSENT"* ]]
}

@test "PASS: form 3 ([WORKTREE-CWD] annotation) cwd directive present" {
  run bash "$SCRIPT_BIN" "$FIXTURE_DIR/pass-form3-annotation.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"WARN-CWD-DIRECTIVE-ABSENT"* ]]
}

# ── WARN — PL spawn but no cwd directive (warning-tier exit 0) ────────────────

@test "WARN: PL spawn with no cwd directive (warning-tier exit 0)" {
  run bash "$SCRIPT_BIN" "$FIXTURE_DIR/warn-no-cwd-directive.md"
  [ "$status" -eq 0 ]  # warning-tier always exit 0
  [[ "$output" == *"WARN-CWD-DIRECTIVE-ABSENT"* ]]
}

# ── PASS — bypass env ─────────────────────────────────────────────────────────

@test "PASS: bypass env HOTFIX_BYPASS_PL_INLINE_VERIFY_CWD_MANDATE=1 skips lint" {
  HOTFIX_BYPASS_PL_INLINE_VERIFY_CWD_MANDATE=1 \
    run bash "$SCRIPT_BIN" "$FIXTURE_DIR/warn-no-cwd-directive.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"BYPASS=1"* ]]
}
