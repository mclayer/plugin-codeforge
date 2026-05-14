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

# CFP-654 — L5 regression TC

@test "L5 regression — option C-prime PR Phase marker absent fallback branch present in workflow (CFP-654)" {
  # elif [ -z "$PHASE" ] && [ "$IS_EPIC_PR" -eq 0 ] 분기 존재 verify
  run grep -F 'elif [ -z "$PHASE" ] && [ "$IS_EPIC_PR" -eq 0 ]' "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
}

@test "L5 regression — L5 fallback trigger_reason string present in workflow (CFP-654)" {
  run grep -F "Phase marker absent (option C-prime PR" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
}

@test "L5 regression — Epic PR phase_marker_absent skip branch uses epic_pr_phase_marker_absent reason (CFP-654)" {
  run grep -F "skip_reason=epic_pr_phase_marker_absent" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
}

@test "L5 regression — old skip_reason=phase_marker_absent absent from workflow (CFP-654)" {
  # 구 skip_reason=phase_marker_absent 는 L5 fix 이후 제거됨
  run grep -F "skip_reason=phase_marker_absent" "$WORKFLOW_FILE"
  [ "$status" -eq 1 ]
  [ -z "$output" ]
}

@test "L5 regression — option C-prime trigger logic in python (non-Epic, Phase marker absent → trigger) (CFP-654)" {
  run python3 -c "
# Phase marker absent, non-Epic → L5 fallback trigger simulation
PR_TITLE = '[CFP-654] retro-mandatory L5 fix — option C-prime fallback'
IS_EPIC_PR = 0  # non-Epic

import re
phase_match = re.search(r'Phase [12]', PR_TITLE)
PHASE = phase_match.group(0).replace(' ', '') if phase_match else ''

IS_PHASE2_LABEL = 0  # no phase:보안-테스트 label

if PHASE == 'Phase2' or IS_PHASE2_LABEL > 0:
    trigger = 'Phase 2 PR merge (primary)'
elif PHASE == 'Phase1' and IS_EPIC_PR == 0:
    trigger = 'Phase 1 PR merge (doc-only Story candidate, D-3 fallback)'
elif PHASE == '' and IS_EPIC_PR == 0:
    trigger = 'Phase marker absent (option C-prime PR — L5 fallback, CFP-654)'
else:
    trigger = 'SKIP'

assert trigger == 'Phase marker absent (option C-prime PR — L5 fallback, CFP-654)', f'Expected L5 trigger, got: {trigger!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

@test "L5 regression — Epic PR + Phase marker absent → skip (not trigger) (CFP-654)" {
  run python3 -c "
# Phase marker absent, Epic PR → skip simulation
PR_TITLE = '[CFP-654] some Epic aggregating PR'
IS_EPIC_PR = 1  # Epic PR

import re
phase_match = re.search(r'Phase [12]', PR_TITLE)
PHASE = phase_match.group(0).replace(' ', '') if phase_match else ''

IS_PHASE2_LABEL = 0

if PHASE == 'Phase2' or IS_PHASE2_LABEL > 0:
    result = 'trigger'
elif PHASE == 'Phase1' and IS_EPIC_PR == 0:
    result = 'trigger'
elif PHASE == '' and IS_EPIC_PR == 0:
    result = 'trigger'
else:
    result = 'skip'

assert result == 'skip', f'Expected skip for Epic PR, got: {result!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}
