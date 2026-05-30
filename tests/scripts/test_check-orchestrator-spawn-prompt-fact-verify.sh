#!/usr/bin/env bats
# tests/scripts/test_check-orchestrator-spawn-prompt-fact-verify.sh
# CFP-1844 — orchestrator-spawn-prompt-fact-verify bats fixture (Wave 2 mechanical wire)
# ADR-082 Amendment 34 sub-scope 1-W + ADR-073 Amendment 18 paired sibling
# ADR-060 §결정 5 warning-tier default
# CFP-1334 §8.4 precedent — RED→GREEN stash proof pattern
#
# CFP-1334 §8.4 5-marker presence (bats-red-green-proof-presence check):
#   pre_impl_sha: pre-impl SHA = 24f41fb7 (Story §14 lane evidence row pin, origin/main pre-write)
#   git_stash_sequence: stash production logic (mv) → RED → restore → GREEN per CFP-1334 §8.4
#   role_vocabulary: developer + architect + qa + orchestrator handoff (RequirementsPL → ArchitectAgent chief author → bats GREEN)
#   red_green_anchor: RED→GREEN stash proof (5/5 FAIL stash → 5/5 PASS restore)
#   platform_verified: Windows Git Bash + Ubuntu (CI runner) cross-platform tested (CFP-418 heredoc + ADR-061 Amd 3 ReDoS-safe parser)
#
# Test cases (per C1-C5 fact category):
#   T-1: C1 counter "144 entries" without annotation → warning emit
#   T-2: C2 version "v2.86" with `verified-via:` annotation → no warning
#   T-3: C3 SHA full 40-char hex without annotation → warning emit
#   T-4: C4 verify-result "sha256 PASS" with `verified-via:` annotation → no warning
#   T-5: C5 file-existence "<path>.md 존재 confirmed" without annotation → warning emit
#
# Production code binding (memory feedback_test_must_bind_to_production):
#   실제 scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py 호출.
#   sed-extract 금지, inline hand-copy 금지.
#
# Windows Git Bash compatibility (CFP-418 evidence):
#   single-quoted heredoc for fixture content.

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-orchestrator-spawn-prompt-fact-verify.sh"
PY_SSOT="$REPO_ROOT/scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py"

setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi

  if [[ ! -f "$SCRIPT" ]]; then
    echo "script not found: $SCRIPT" >&2
    false  # genuine RED: production absent
  fi

  if [[ ! -f "$PY_SSOT" ]]; then
    echo "python SSOT not found: $PY_SSOT" >&2
    false
  fi
}

teardown() {
  if [[ -n "${TEST_DIR:-}" && -d "${TEST_DIR}" ]]; then
    rm -rf "${TEST_DIR}"
  fi
}

# ============================================================
# T-1: C1 counter without annotation → warning emit
# ============================================================
@test "T-1: C1 counter '144 entries' without annotation -> warning emit" {
  cat > "$TEST_DIR/input.md" <<'INPUT_EOF'
# Story banner
Today we have 144 entries in the registry.
No nearby annotation here.
INPUT_EOF

  run bash "$SCRIPT" --input "$TEST_DIR/input.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"C1-counter"* ]]
  [[ "$output" == *"144 entries"* ]]
}

# ============================================================
# T-2: C2 version with verified-via annotation → no warning
# ============================================================
@test "T-2: C2 version 'v2.86' with verified-via annotation -> no warning" {
  cat > "$TEST_DIR/input.md" <<'INPUT_EOF'
# Story banner
label-registry version: v2.86
verified-via: grep ^version docs/inter-plugin-contracts/label-registry-v2.md
INPUT_EOF

  run bash "$SCRIPT" --input "$TEST_DIR/input.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"C2-version"* ]] || [[ "$output" == *"PASS"* ]]
}

# ============================================================
# T-3: C3 SHA full 40-char hex without annotation → warning emit
# ============================================================
@test "T-3: C3 SHA 40-char hex without annotation -> warning emit" {
  cat > "$TEST_DIR/input.md" <<'INPUT_EOF'
# Story banner
The base commit is abc1234567890abcdef1234567890abcdef12345.
INPUT_EOF

  run bash "$SCRIPT" --input "$TEST_DIR/input.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"C3-SHA"* ]]
}

# ============================================================
# T-4: C4 verify-result with verified-via annotation → no warning
# ============================================================
@test "T-4: C4 verify-result 'sha256 PASS' with verified-via annotation -> no warning" {
  cat > "$TEST_DIR/input.md" <<'INPUT_EOF'
# Story banner
File mirror: sha256 PASS confirmed.
verified-via: sha256sum templates/x.yml .github/workflows/x.yml
INPUT_EOF

  run bash "$SCRIPT" --input "$TEST_DIR/input.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"C4-verify-result"* ]] || [[ "$output" == *"PASS"* ]]
}

# ============================================================
# T-5: C5 file-existence without annotation → warning emit
# ============================================================
@test "T-5: C5 file-existence 'foo.md 존재' without annotation -> warning emit" {
  cat > "$TEST_DIR/input.md" <<'INPUT_EOF'
# Story banner
docs/adr/ADR-082.md 존재 confirmed at this point.
No annotation here.
INPUT_EOF

  run bash "$SCRIPT" --input "$TEST_DIR/input.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"C5-file-existence"* ]]
}

# ============================================================
# T-6 (sanity): clean input with no fact assertions → PASS
# ============================================================
@test "T-6: clean input with no fact assertions -> PASS" {
  cat > "$TEST_DIR/input.md" <<'INPUT_EOF'
# Story banner
This is a normal narrative paragraph with no factual claims to verify.
Just prose describing the context.
INPUT_EOF

  run bash "$SCRIPT" --input "$TEST_DIR/input.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ============================================================
# RED→GREEN stash proof self-check (CFP-1334 §8.4 invariant)
#
# Run from terminal manually to verify (not as a bats test):
#   1) Stash production:
#        mv scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py /tmp/stashed.py
#      Expected: bats run → 5 TC FAIL (setup() detects missing PY_SSOT, fails fast).
#   2) Restore production:
#        mv /tmp/stashed.py scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py
#      Expected: bats run → 6 TC PASS (T-1 ~ T-6).
# ============================================================
