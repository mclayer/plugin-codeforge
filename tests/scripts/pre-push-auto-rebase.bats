#!/usr/bin/env bats
# tests/scripts/pre-push-auto-rebase.bats
# CFP-477 Phase 2 — pre-push-auto-rebase.sh.sample unit tests
# Story §7.2 / Change Plan §8 test plan verbatim
#
# Test cases (TC-1..TC-5):
#   TC-1: PRE_PUSH_AUTO_REBASE unset → no-op exit 0 (silent)
#   TC-2: branch up-to-date with origin/main → no-op exit 0
#   TC-3: branch behind origin/main by N commits → abort exit 1 + 4-line guidance
#   TC-4: origin fetch failure → graceful warning + exit 0 (no false-block)
#   TC-5: detached HEAD → safe skip exit 0
#
# bats 4.x syntax. mock git via PATH override pattern (CFP-447 pre-push.bats verbatim).

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../templates/.claude/hooks/pre-push-auto-rebase.sh.sample"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # git mock dir (prepend to PATH)
  mkdir -p "$TEST_DIR/bin"
  export PATH="$TEST_DIR/bin:$PATH"

  # Default git stub: safe fallback (most TCs override specific subcommands)
  cat > "$TEST_DIR/bin/git" <<'STUB'
#!/usr/bin/env bash
# git stub for pre-push-auto-rebase.bats
case "$1 $2" in
  "rev-parse --abbrev-ref")
    echo "feature-branch"
    exit 0
    ;;
  "fetch origin")
    exit 0
    ;;
  "rev-parse origin/main")
    exit 0
    ;;
  "rev-list --count")
    echo "0"
    exit 0
    ;;
esac
# fallback for unmatched: silent success
exit 0
STUB
  chmod +x "$TEST_DIR/bin/git"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------ TC-1: env unset → no-op
@test "TC-1: PRE_PUSH_AUTO_REBASE unset → exit 0 silent (no-op)" {
  unset PRE_PUSH_AUTO_REBASE

  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  # silent: no output expected
  [ -z "$output" ]
}

# ------------------------------------------------------------------ TC-2: up-to-date → no-op
@test "TC-2: branch up-to-date with origin/main → exit 0 no-op" {
  # git stub: BEHIND = 0
  cat > "$TEST_DIR/bin/git" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "rev-parse --abbrev-ref")
    echo "feature-branch"
    exit 0
    ;;
  "fetch origin")
    exit 0
    ;;
  "rev-parse origin/main")
    exit 0
    ;;
  "rev-list --count")
    echo "0"
    exit 0
    ;;
esac
exit 0
STUB
  chmod +x "$TEST_DIR/bin/git"

  PRE_PUSH_AUTO_REBASE=1 run bash "$SCRIPT"

  [ "$status" -eq 0 ]
}

# ------------------------------------------------------------------ TC-3: behind → abort + 4-line guidance
@test "TC-3: branch behind origin/main by 3 commits → exit 1 + 4-line guidance" {
  # git stub: BEHIND = 3
  cat > "$TEST_DIR/bin/git" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "rev-parse --abbrev-ref")
    echo "cfp-477-phase-2"
    exit 0
    ;;
  "fetch origin")
    exit 0
    ;;
  "rev-parse origin/main")
    exit 0
    ;;
  "rev-list --count")
    echo "3"
    exit 0
    ;;
esac
exit 0
STUB
  chmod +x "$TEST_DIR/bin/git"

  PRE_PUSH_AUTO_REBASE=1 run bash "$SCRIPT"

  [ "$status" -eq 1 ]

  # 4-line guidance: all 4 key strings present in stderr (combined output via run)
  [[ "$output" == *"BEHIND"* ]]
  [[ "$output" == *"3"* ]]
  [[ "$output" == *"rebase"* ]]
  [[ "$output" == *"abort"* ]]
  [[ "$output" == *"bypass"* ]]
  [[ "$output" == *"PRE_PUSH_AUTO_REBASE=0"* ]]
}

# ------------------------------------------------------------------ TC-4: fetch failure → graceful warning + exit 0
@test "TC-4: origin fetch failure → graceful warning + exit 0 (no false-block)" {
  # git stub: fetch fails (network error simulation)
  cat > "$TEST_DIR/bin/git" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "rev-parse --abbrev-ref")
    echo "feature-branch"
    exit 0
    ;;
  "fetch origin")
    # simulate network failure
    echo "fatal: unable to connect to origin" >&2
    exit 1
    ;;
  "rev-parse origin/main")
    exit 0
    ;;
  "rev-list --count")
    echo "5"
    exit 0
    ;;
esac
exit 0
STUB
  chmod +x "$TEST_DIR/bin/git"

  PRE_PUSH_AUTO_REBASE=1 run bash "$SCRIPT"

  # MUST NOT block push on fetch failure
  [ "$status" -eq 0 ]
  # warning present
  [[ "$output" == *"fetch"* ]] || [[ "$output" == *"fetch 실패"* ]]
}

# ------------------------------------------------------------------ TC-5: detached HEAD → safe skip
@test "TC-5: detached HEAD → exit 0 (safe skip)" {
  # git stub: HEAD detached
  cat > "$TEST_DIR/bin/git" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "rev-parse --abbrev-ref")
    echo "HEAD"
    exit 0
    ;;
esac
exit 0
STUB
  chmod +x "$TEST_DIR/bin/git"

  PRE_PUSH_AUTO_REBASE=1 run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"detached HEAD"* ]] || [[ "$output" == *"HEAD"* ]]
}
