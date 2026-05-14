#!/usr/bin/env bats
# CFP-662 Phase 2 — bootstrap-labels.yml workflow TDD (T-1~T-8)
# QADeveloperAgent RED test — workflow file 미존재 시 전부 FAIL 의도.
# bats-core 필요: https://github.com/bats-core/bats-core

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"
TEMPLATE_FILE="$REPO_ROOT/templates/github-workflows/bootstrap-labels.yml"
GITHUB_FILE="$REPO_ROOT/.github/workflows/bootstrap-labels.yml"

# T-1: PR open 트리거 — on.pull_request.types: [opened] 존재
@test "T-1: on.pull_request.types includes opened only (no synchronize)" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run python3 -c "
import yaml, sys
with open('$TEMPLATE_FILE', encoding='utf-8') as f:
    doc = yaml.safe_load(f)
# YAML 1.1: 'on' keyword -> True (boolean). GitHub Actions 'on:' trigger key.
on_key = True if True in doc else 'on'
trigger = doc.get(on_key, {})
types = trigger.get('pull_request', {}).get('types', []) if isinstance(trigger, dict) else []
assert 'opened' in types, f'opened not in types: {types}'
assert 'synchronize' not in types, f'synchronize must NOT be in types (chicken-and-egg/loop risk): {types}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# T-2: 기존 label 보존 (idempotent) — script 호출 single step 구조
@test "T-2: workflow calls bootstrap-labels.sh (idempotent script invocation)" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run grep -E "bootstrap-labels\.sh" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
}

# T-3: concurrency.group 존재 (재실행 idempotent + dual-fire 차단)
@test "T-3: concurrency.group per PR number present" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run grep -E "concurrency" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
  run python3 -c "
import yaml, sys
with open('$TEMPLATE_FILE', encoding='utf-8') as f:
    doc = yaml.safe_load(f)
conc = doc.get('concurrency', {})
group = conc.get('group', '') if isinstance(conc, dict) else ''
assert 'bootstrap-labels' in group, f'concurrency.group missing bootstrap-labels: {group!r}'
assert 'pull_request.number' in group or \"github.event.pull_request.number\" in group or \"pull_request.number\" in group, f'concurrency.group must contain PR number: {group!r}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# T-4: hotfix-bypass conditional skip + audit comment 2-step pattern
#   Step A: gh pr comment 직접 발의 (ADR-024 Amendment 3 §결정 6.C)
#   Step B: check-bypass-audit-comment.sh assertion verify (comment 존재 검증)
@test "T-4: hotfix-bypass:bootstrap-labels 2-step pattern — Step A gh pr comment + Step B assertion verify" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  # hotfix-bypass:bootstrap-labels label 감지 조건 존재
  run grep -E "hotfix-bypass:bootstrap-labels" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
  # Step A verify: gh pr comment 직접 발의 step 존재 (audit comment inline post)
  run grep -E "gh pr comment" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
  # Step B verify: check-bypass-audit-comment.sh assertion step 존재 (comment 존재 verify)
  run grep -E "check-bypass-audit-comment\.sh" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
  # 2-step 구조: Emit step name + Audit assertion step name 모두 존재 (grep by name prefix)
  run grep -E "Emit bypass audit comment" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
  run grep -E "Audit assertion" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
}

# T-5: PAT fallback to GITHUB_TOKEN
@test "T-5: CODEFORGE_CROSS_REPO_PAT token with GITHUB_TOKEN fallback" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run grep -E "CODEFORGE_CROSS_REPO_PAT" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
  run grep -E "GITHUB_TOKEN" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
}

# T-6: continue-on-error: true (chicken-and-egg deadlock 회피, ADR-060 §결정 5 warning tier)
@test "T-6: continue-on-error true at job level (warning tier, deadlock avoidance)" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run python3 -c "
import yaml, sys
with open('$TEMPLATE_FILE', encoding='utf-8') as f:
    doc = yaml.safe_load(f)
jobs = doc.get('jobs', {})
assert jobs, 'no jobs defined'
for job_name, job in jobs.items():
    coe = job.get('continue-on-error', False)
    assert coe is True, f'job {job_name}: continue-on-error must be true (got {coe!r})'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# T-7: timeout-minutes: 5 강제
@test "T-7: timeout-minutes 5 present" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run grep -E "timeout-minutes:[[:space:]]*5" "$TEMPLATE_FILE"
  [ "$status" -eq 0 ]
}

# T-8: workflow permissions block — issues:write + pull-requests:write (ADR-060 Amendment 8 / CFP-530)
@test "T-8: permissions block has pull-requests write and issues write" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run python3 -c "
import yaml, sys
with open('$TEMPLATE_FILE', encoding='utf-8') as f:
    doc = yaml.safe_load(f)
perms = doc.get('permissions', {})
assert perms.get('pull-requests') == 'write', f'pull-requests:write missing: {perms}'
assert perms.get('issues') == 'write' or perms.get('contents') == 'read', f'permissions incomplete: {perms}'
print('PASS')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# T-meta-1: YAML 파싱 성공
@test "T-meta-1: YAML parses successfully" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  run python3 -c "import yaml; yaml.safe_load(open('$TEMPLATE_FILE', encoding='utf-8'))"
  [ "$status" -eq 0 ]
}

# T-meta-2: template byte-identical with .github/workflows (ADR-005 self-app invariant)
@test "T-meta-2: template byte-identical with .github/workflows/bootstrap-labels.yml" {
  [ -f "$TEMPLATE_FILE" ] || skip "bootstrap-labels.yml 미존재 (RED state)"
  [ -f "$GITHUB_FILE" ] || skip ".github/workflows/bootstrap-labels.yml 미존재 (RED state)"
  run diff "$TEMPLATE_FILE" "$GITHUB_FILE"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}
