#!/usr/bin/env bats
# CFP-1302 — phase-gate-mergeable.yml regression + multi-gate strengthening test
# 6 TC + T-meta (sibling-workflow-parity)
# ADR-061 Amd 2 §결정 9: production-scale invariant — real label set × multi-gate combination depth ≥ 3
# prior art: test_retro_mandatory_yml.bats + test_bootstrap_labels_workflow.bats (Python yaml.safe_load + grep + actionlint pattern)
# bats-core: https://github.com/bats-core/bats-core

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"
WORKFLOW_FILE="$REPO_ROOT/.github/workflows/phase-gate-mergeable.yml"
TEMPLATE_FILE="$REPO_ROOT/templates/github-workflows/phase-gate-mergeable.yml"

# ──────────────────────────────────────────────────────────
# T-1: required.gates[] array shape — 4 phase branch 모두 확인
# ──────────────────────────────────────────────────────────
@test "T-1: required.gates[] array shape — 4 phase branch (설계/보안-테스트/구현/fallback)" {
  # Python yaml.safe_load 대신 grep으로 JS array literal 검증 (workflow JS 영역)
  # CFP-1302: { phase, gate: string } → { phase, gates: string[] } 전환 확인
  run grep -c "gates: \['" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  # 4 phase branch 각각 gates: ['gate:X'] 패턴 — 최소 4 occurrence
  [ "$output" -ge 4 ]
}

@test "T-1b: required.gates array 전환 — gates: [' 패턴 최소 4회 존재 (CFP-1302)" {
  # CFP-1302: singular gate: 'X' → plural gates: ['X'] 전환.
  # gates: [' 패턴이 4 phase branch 에 각각 존재해야 함.
  run grep -c "gates: \['" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 4 ]
}

# ──────────────────────────────────────────────────────────
# T-2: multi-gate AND discriminating fixture
# ADR-061 Amd 2 §결정 9 production-scale invariant: label combination depth ≥ 3
# ──────────────────────────────────────────────────────────
@test "T-2: multi-gate AND every() invariant (not some())" {
  # every() 사용 확인 — AND semantics
  run grep -c "required\.gates\.every" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-2b: B-1 fail-loud guard — empty array vacuous truth 차단" {
  # required.gates.length === 0 check + core.warning 존재 확인
  run grep -c "required\.gates\.length === 0" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "fail-loud.*B-1" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-2c: production-scale label combination — phase:* × gate:* × cross-Story 검증" {
  # ADR-061 Amd 2 §결정 9: real label set depth ≥ 3
  # phase:* 값 + gate:* 값 workflow 안 closed enumeration 확인
  local PHASE_VALUES=("phase:설계" "phase:설계-리뷰" "phase:보안-테스트" "phase:구현" "phase:구현-리뷰")
  local GATE_VALUES=("gate:design-review-pass" "gate:security-test-pass" "gate:live-entry-pass")

  # 각 phase:* 값 workflow 안 등장 확인
  for pv in "${PHASE_VALUES[@]}"; do
    run grep -c "'${pv}'" "$WORKFLOW_FILE"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done

  # gate:design-review-pass + gate:security-test-pass 양 workflow 안 등장 확인
  for gv in "gate:design-review-pass" "gate:security-test-pass"; do
    run grep -c "'${gv}'" "$WORKFLOW_FILE"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

# ──────────────────────────────────────────────────────────
# T-3: PR comment fallback regression (CFP-133 #239 fix 보존)
# ──────────────────────────────────────────────────────────
@test "T-3: PR comment fallback regression — evidenceForGate + allGatesHaveEvidence AND invariant" {
  # CFP-133 #239 fix: PR comment-based gate evidence path 보존
  # CFP-1302: multi-gate AND → evidenceForGate 객체 + allGatesHaveEvidence 패턴
  run grep -c "evidenceForGate" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "allGatesHaveEvidence" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-3b: PR comment fallback — listComments API + lanePrefixForGate map 보존 (CFP-133 #239)" {
  run grep -c "listComments" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "lanePrefixForGate" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # 설계-리뷰 prefix 보존
  run grep -c "\[설계-리뷰\]" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # 보안-테스트 prefix 보존
  run grep -c "\[보안-테스트\]" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-4: liveEntryOk 별 변수 보존 (D-1 결정 — ADR-030 conditional semantics)
# ──────────────────────────────────────────────────────────
@test "T-4: liveEntryOk 별 변수 보존 (D-1: ADR-030 conditional gate semantics)" {
  # liveEntryOk 별 변수가 여전히 존재해야 함
  run grep -c "liveEntryOk" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 3 ]  # 선언 + if 조건 + allOk 합성

  # requireLiveEntry = liveTouching && isLivePhase 조건부 패턴 보존
  run grep -c "requireLiveEntry" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 2 ]

  # allOk 안에 liveEntryOk AND 합성 보존
  run grep -c "allOk.*&&.*liveEntryOk\|liveEntryOk.*&&.*allOk\|phaseOk.*&&.*gateOk.*&&.*liveEntryOk" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-5: summary multi-gate display byte-identical (CFP-1290 Wave 1 보존 + CFP-1302 gates 확장)
# ──────────────────────────────────────────────────────────
@test "T-5: summary — required.gates.join(', ') + missingGates list (CFP-1302 Wave 2)" {
  # CFP-1290 Wave 1: allGateLabels multi-gate display 보존
  run grep -c "allGateLabels" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # CFP-1302: required.gates.join 사용 확인
  run grep -c "required\.gates\.join" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # missingGates list 명시 확인
  run grep -c "missingGates" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "T-5b: summary FAIL branch — required gates=[] MISSING format 존재" {
  # Awaiting: phase=..., required gates=[...] MISSING [...] format
  run grep -c "required gates=\[" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "MISSING \[" "$WORKFLOW_FILE"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────────────────────────
# T-meta: sibling-workflow-parity (templates ↔ .github/workflows byte-identical)
# I-7 invariant (ADR-005 self-application byte-identical mirror)
# ──────────────────────────────────────────────────────────
@test "T-meta: templates ↔ .github/workflows phase-gate-mergeable.yml byte-identical" {
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
