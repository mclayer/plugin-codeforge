#!/usr/bin/env bash
# CFP-42 — Test harness for check-inter-plugin-contracts.sh
#
# 6 test cases (T1-T6 per CFP-42 spec §8). Each case:
#   1. Snapshot wrapper docs/inter-plugin-contracts/ + MANIFEST.yaml to tmp dir
#   2. Apply test-specific mutation
#   3. Run lint with cwd pointed at tmp dir
#   4. Assert expected exit code
#   5. Restore (no mutation to actual repo files)
#
# Usage: bash scripts/test-check-inter-plugin-contracts.sh
# Exit: 0 if all pass, 1 if any fail.

set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
LINT_SCRIPT="$REPO_ROOT/scripts/check-inter-plugin-contracts.sh"

PASS=0
FAIL=0

run_test() {
  local name="$1"
  local expected_exit="$2"
  local mutation_fn="$3"

  local tmp
  tmp=$(mktemp -d)
  trap "rm -rf '$tmp'" RETURN

  # Mirror minimum repo structure to tmp
  mkdir -p "$tmp/docs/inter-plugin-contracts" "$tmp/scripts"
  cp "$REPO_ROOT/docs/inter-plugin-contracts/"*.md "$tmp/docs/inter-plugin-contracts/"
  cp "$REPO_ROOT/docs/inter-plugin-contracts/MANIFEST.yaml" "$tmp/docs/inter-plugin-contracts/"
  cp "$REPO_ROOT/scripts/check-inter-plugin-contracts.sh" "$tmp/scripts/"

  # Apply mutation in tmp
  ( cd "$tmp" && eval "$mutation_fn" )

  # Run lint with cwd at tmp (PYTHONIOENCODING=utf-8 required on Windows/cp949 locales)
  local actual_exit=0
  ( cd "$tmp" && PYTHONIOENCODING=utf-8 bash scripts/check-inter-plugin-contracts.sh ) >/dev/null 2>&1 || actual_exit=$?

  if [ "$actual_exit" = "$expected_exit" ]; then
    echo "✓ $name (exit $actual_exit)"
    PASS=$((PASS+1))
  else
    echo "✗ $name (expected exit $expected_exit, got $actual_exit)"
    FAIL=$((FAIL+1))
  fi
}

# T1: manifest mismatch — delete one sibling file
run_test "T1 manifest mismatch (sibling delete)" 1 \
  "rm docs/inter-plugin-contracts/requirements-output-v1.md"

# T2: orphan — add unregistered kind:contract file
run_test "T2 orphan (unregistered kind:contract)" 1 \
  "cat > docs/inter-plugin-contracts/orphan-v1.md <<'EOF'
---
kind: contract
contract_version: \"1.0\"
status: Active
related_plugins: [codeforge, codeforge-orphan]
related_adrs: [ADR-008, ADR-010]
authors: [test]
---
# orphan v1 — Inter-plugin Contract
**상위 SSOT 위치**:
- canonical: nowhere
## 1. body
## 2. body
## 3. body
EOF"

# T3: ADR-010 reference 누락 (sibling)
run_test "T3 sibling without ADR-010 reference" 1 \
  "python3 -c '
import re, pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
text = re.sub(r\"  - ADR-010.*\\n\", \"\", text, count=1)
p.write_text(text, encoding=\"utf-8\")
'"

# T4: sibling marker section 누락
run_test "T4 sibling without 상위 SSOT 위치 marker" 1 \
  "python3 -c '
import re, pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
text = re.sub(r\"\\*\\*상위 SSOT 위치\\*\\*:.*?(?=\\n##|\\Z)\", \"\", text, flags=re.DOTALL, count=1)
p.write_text(text, encoding=\"utf-8\")
'"

# T5: positive — no mutation
run_test "T5 정합 상태" 0 ":"

# T6: regression — review-verdict v1+v2 + 3 kind:registry exist (default state)
# (T5 already covers 정합 상태, T6 verifies kind:registry files don't trigger orphan)
run_test "T6 kind:registry files coexist (regression)" 0 \
  "test -f docs/inter-plugin-contracts/comment-prefix-registry-v1.md && \
   test -f docs/inter-plugin-contracts/fix-event-v1.md && \
   test -f docs/inter-plugin-contracts/label-registry-v1.md"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
