#!/usr/bin/env bats
# CFP-645 — retro-mandatory.yml regression test (secrets context if-conditional 차단)
# 3 TC: secrets grep / YAML parse / template byte-identical
# bats-core 필요: https://github.com/bats-core/bats-core

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"
WORKFLOW_FILE="$REPO_ROOT/.github/workflows/retro-mandatory.yml"
TEMPLATE_FILE="$REPO_ROOT/templates/github-workflows/retro-mandatory.yml"

@test "no 'secrets.X != ...' job/step-level if expression (CFP-645 regression)" {
  run grep -E "secrets\.[A-Z_]+[[:space:]]*!=[[:space:]]*''" "$WORKFLOW_FILE"
  [ "$status" -eq 1 ]
  [ -z "$output" ]
}

@test "YAML parses successfully (python yaml.safe_load)" {
  run python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_FILE', encoding='utf-8'))"
  [ "$status" -eq 0 ]
}

@test "template byte-identical with .github/workflows" {
  run diff "$TEMPLATE_FILE" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

# CFP-650 — L3 + L4 regression TC

@test "L3 regression — outcome=missing_file_despite_gate present in workflow (CFP-650)" {
  run grep -F "outcome=missing_file_despite_gate" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
}

@test "L4 regression — Auto-attach gate:retro-complete label step present in workflow (CFP-650)" {
  run grep -F "Auto-attach gate:retro-complete label" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
}

@test "L3 naming convention — cfp-NNN.md match (case-insensitive, CFP-650)" {
  # jq test pattern cfp-NNN (case-insensitive "i" flag) must cover cfp-650.md
  run python3 -c "
import re
name = 'cfp-650.md'
pattern = r'cfp-650'
assert re.search(pattern, name, re.IGNORECASE), f'No match: {name!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

@test "L3 naming convention — EPIC-RESULTS-CFP-NNN.md match (case-insensitive, CFP-650)" {
  run python3 -c "
import re
name = 'EPIC-RESULTS-CFP-650.md'
pattern = r'cfp-650'
assert re.search(pattern, name, re.IGNORECASE), f'No match: {name!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

@test "L3 naming convention — cfp-NNN-slug.md match (case-insensitive, CFP-650)" {
  run python3 -c "
import re
name = 'cfp-650-retro-mandatory-fix.md'
pattern = r'cfp-650'
assert re.search(pattern, name, re.IGNORECASE), f'No match: {name!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

@test "L3 naming convention — Cfp-NNN.md (mixed-case) match (case-insensitive, CFP-650)" {
  run python3 -c "
import re
name = 'Cfp-650.md'
pattern = r'cfp-650'
assert re.search(pattern, name, re.IGNORECASE), f'No match: {name!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}
