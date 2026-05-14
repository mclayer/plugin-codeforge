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
