#!/usr/bin/env bats
# CFP-1302 — phase-gate-auto-cleanup.yml schema + invariant test
# 8 TC + T-meta (sibling-workflow-parity)
# ADR-061 Amd 2 §결정 9: production-scale invariant
# prior art: test_retro_mandatory_yml.bats + test_bootstrap_labels_workflow.bats
# bats-core: https://github.com/bats-core/bats-core

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"
WORKFLOW_FILE="$REPO_ROOT/.github/workflows/phase-gate-auto-cleanup.yml"
TEMPLATE_FILE="$REPO_ROOT/templates/github-workflows/phase-gate-auto-cleanup.yml"

# ──────────────────────────────────────────────────────────
# T-1: on: trigger schema
# pull_request: types: [labeled, synchronize] + issues: types: [labeled]
# ──────────────────────────────────────────────────────────
@test "T-1: on.pull_request.types includes labeled and synchronize (EC-1)" {
  # GitHub Actions YAML 의 'on:' 키는 yaml.safe_load 에서 True 로 파싱 (YAML 1.1 quirk).
  # grep 방식으로 trigger schema 확인.
  run grep -A5 "pull_request:" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [[ "$output" == *"labeled"* ]]
  [[ "$output" == *"synchronize"* ]]
}

@test "T-1b: on.issues.types includes labeled (Story Issue bidirectional sync)" {
  # grep 방식 — YAML 1.1 'on' = True parse quirk 우회.
  run grep -A5 "issues:" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [[ "$output" == *"labeled"* ]]
}

# ──────────────────────────────────────────────────────────
# T-2: concurrency group namespace 분리 + cancel-in-progress: false
# phase-gate-mergeable- vs phase-gate-auto-cleanup- 분리 확인 (§7.4.4)
# ──────────────────────────────────────────────────────────
@test "T-2: concurrency.group = phase-gate-auto-cleanup-\${{ pr.number || issue.number }}" {
  run python3 -c "
import yaml, sys
data = yaml.safe_load(open('$WORKFLOW_FILE', encoding='utf-8'))
concurrency = data.get('concurrency', {})
group = concurrency.get('group', '')
assert 'phase-gate-auto-cleanup' in group, f'wrong namespace: {group!r}'
cancel = concurrency.get('cancel-in-progress', True)
assert cancel == False, f'cancel-in-progress must be false: {cancel}'
print('OK')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OK"* ]]
}

@test "T-2b: concurrency namespace disjoint from phase-gate-mergeable (race avoidance)" {
  # phase-gate-mergeable.yml 의 concurrency group name 과 달라야 함
  MERGEABLE_CONCURRENCY=$(grep "group:" "$REPO_ROOT/.github/workflows/phase-gate-mergeable.yml" | head -1 | awk '{print $2}')
  CLEANUP_CONCURRENCY=$(grep "group:" "$WORKFLOW_FILE" | head -1 | awk '{print $2}')

  # 두 concurrency group 이 다르면 OK
  [ "$MERGEABLE_CONCURRENCY" != "$CLEANUP_CONCURRENCY" ]
}

# ──────────────────────────────────────────────────────────
# T-3: guard label — hotfix-bypass:auto-cleanup-stale-gate + hotfix-bypass:phase-gate-mergeable
# ──────────────────────────────────────────────────────────
@test "T-3: if: guard — hotfix-bypass:auto-cleanup-stale-gate skip" {
  run grep -c "hotfix-bypass:auto-cleanup-stale-gate" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-3b: if: guard — hotfix-bypass:phase-gate-mergeable skip (T-1 위협 완화)" {
  run grep -c "hotfix-bypass:phase-gate-mergeable" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-3c: if: guard — startsWith(github.event.label.name, 'phase:') 존재" {
  run grep -c "startsWith.*phase:" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-4: removeLabel API + audit comment 2-step pattern
# try/catch 404 silent ok + [auto-cleanup: ... at <KST>] format
# ──────────────────────────────────────────────────────────
@test "T-4: removeLabel API call 존재 (stage 3)" {
  run grep -c "removeLabel" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-4b: try/catch 404 silent ok — idempotency invariant (§7.4.2)" {
  run grep -c "e\.status === 404" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-4c: audit comment format — [auto-cleanup: gate:<X> removed at <KST>] (ADR-079 §7.4.3)" {
  run grep -c "auto-cleanup:.*removed at" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-4d: KST timestamp — +09:00 offset 변환 (ADR-079 display layer mandate)" {
  # kstOffset = 9 * 60 + kstDate + +09:00 pattern
  run grep -c "+09:00" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-5: AC-4 safety-first — gate absent 시 auto-fix 아닌 alert comment
# ──────────────────────────────────────────────────────────
@test "T-5: AC-4 safety-first — gate absent 시 removeLabel 호출 안 함 + alert comment" {
  # hasGateToRemove 변수 + !hasGateToRemove 조건 분기
  run grep -c "hasGateToRemove" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 2 ]  # 선언 + 조건 사용

  # alert comment body — Manual decision required
  run grep -c "Manual decision required" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-5b: AC-4 — gate absent 시 action_required 또는 alert 명시 (NOT auto-fix)" {
  run grep -c "gate absent" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-6: GITHUB_TOKEN only — PAT secret 참조 부재 (D-4 결정)
# ──────────────────────────────────────="I-4 self-trigger 차단"
# ──────────────────────────────────────────────────────────
@test "T-6: GITHUB_TOKEN only — secrets.CODEFORGE_CROSS_REPO_PAT 0 occurrence (D-4 결정)" {
  run grep -c "secrets\.CODEFORGE_CROSS_REPO_PAT" "$WORKFLOW_FILE"
  # grep -c returns 0 when no match found (exit code 1) — invert
  [ "$status" -eq 1 ]
}

@test "T-6b: GITHUB_TOKEN 참조 존재 (workflow 자동 발급)" {
  run grep -c "secrets\.GITHUB_TOKEN" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-7: cross-repo orphan guard — Related: #N marker 부재 시 skip (EC-2)
# ──────────────────────────────────────────────────────────
@test "T-7: EC-2 cross-repo orphan guard — Related marker 부재 시 skip" {
  run grep -c "hasRelatedMarker" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-7b: ALLOWED_HUB_REPOS guard — consumer overlay 확장 가능 (ADR-057)" {
  run grep -c "ALLOWED_HUB_REPOS" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-meta: sibling-workflow-parity (templates ↔ .github/workflows byte-identical)
# I-7 invariant (ADR-005 self-application byte-identical mirror)
# ──────────────────────────────────────────────────────────
@test "T-meta: templates ↔ .github/workflows phase-gate-auto-cleanup.yml byte-identical" {
  run diff "$TEMPLATE_FILE" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "T-meta-b: YAML parses successfully (python yaml.safe_load) — template" {
  run python3 -c "import yaml; yaml.safe_load(open('$TEMPLATE_FILE', encoding='utf-8'))"
  [ "$status" -eq 0 ]
}

@test "T-meta-c: YAML parses successfully (python yaml.safe_load) — .github/workflows" {
  run python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_FILE', encoding='utf-8'))"
  [ "$status" -eq 0 ]
}
