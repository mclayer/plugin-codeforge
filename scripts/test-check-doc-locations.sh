#!/usr/bin/env bash
# CFP-276 — Test harness for check-doc-locations.sh
# 6 fixture cases (T1-T6 per spec §10).
# Usage: bash scripts/test-check-doc-locations.sh
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"

PASS=0
FAIL=0

run_test() {
  local name="$1"
  local expected_exit="$2"
  local mutation_fn="$3"

  local tmp
  tmp=$(mktemp -d)

  mkdir -p "$tmp/docs" "$tmp/scripts/lib"
  cp "$REPO_ROOT/docs/doc-locations.yaml" "$tmp/docs/"
  cp "$REPO_ROOT/docs/doc-location-registry.md" "$tmp/docs/"
  cp "$REPO_ROOT/scripts/check-doc-locations.sh" "$tmp/scripts/"
  # CFP-1373 — check-doc-locations.sh is a thin wrapper (CFP-478 / ADR-061 §결정 6.A)
  # delegating to scripts/lib/check_doc_locations.py SSOT. Fixture must include the Python module.
  cp "$REPO_ROOT/scripts/lib/check_doc_locations.py" "$tmp/scripts/lib/"

  ( cd "$tmp" && eval "$mutation_fn" )

  local actual_exit=0
  ( cd "$tmp" && PYTHONIOENCODING=utf-8 bash scripts/check-doc-locations.sh --full ) >/dev/null 2>&1 || actual_exit=$?

  if [ "$actual_exit" = "$expected_exit" ]; then
    echo "PASS $name (exit $actual_exit)"
    PASS=$((PASS+1))
  else
    echo "FAIL $name (expected exit $expected_exit, got $actual_exit)"
    FAIL=$((FAIL+1))
  fi

  rm -rf "$tmp"
}

# T1: valid yaml -> expect pass
run_test "T1 valid yaml" 0 ":"

# T2: unknown variant key
run_test "T2 unknown variant key" 1 \
  "sed -i 's/      mode_a:/      mode_x:/' docs/doc-locations.yaml"

# T3: unknown placeholder
run_test "T3 unknown placeholder" 1 \
  "sed -i 's/<owner-repo>/<unknown-token>/' docs/doc-locations.yaml"

# T4: absolute path
run_test "T4 absolute path" 1 \
  "sed -i 's|<owner-repo>/docs/retros/EPIC-RESULTS|/abs/path/EPIC-RESULTS|' docs/doc-locations.yaml"

# T5: duplicate doc_type name
run_test "T5 duplicate name" 1 \
  "cat >> docs/doc-locations.yaml <<'EOF'

  - name: epic_results
    variants:
      mode_a: \"<owner-repo>/dup.md\"
    owner_agent: dup
    introduced_by: dup
EOF
"

# T6: stale registry.md
run_test "T6 stale registry.md" 1 \
  "echo 'GARBAGE_TAIL_LINE' >> docs/doc-location-registry.md"

echo ""
echo "Total: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
