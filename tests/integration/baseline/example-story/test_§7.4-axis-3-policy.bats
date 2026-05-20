#!/usr/bin/env bats
# CFP-1088 — §7.4 Axis 3 policy 결정 evidence pointer template bats fixture (Axis 3 = ArchitectLane post-measurement scope)

setup() {
    EVIDENCE="${BATS_TEST_DIRNAME}/§7.4-measurement-evidence.md"
}

@test "TC-1: Axis 3 policy 결정 evidence pointer section present" {
    grep -q "## Axis 3 policy 결정 evidence pointer" "${EVIDENCE}"
}

@test "TC-2: Axis 3 cross-ref (Axis 2 본 lane vs Axis 3 ArchitectLane disjoint) explicit" {
    grep -q "Axis 3 policy 결정 영역 본 lane 책임 외" "${EVIDENCE}"
    grep -q "ArchitectLane post-measurement" "${EVIDENCE}"
}

@test "TC-3: policy_id + measured_value M-row ref + proposed_policy + follow_up_carrier 6-column schema" {
    grep -q "policy_id.*pointer.*measured_value.*proposed_policy_value.*rationale_ref.*follow_up_carrier" "${EVIDENCE}"
}

@test "TC-4: cross-ref ADR-014 Amendment 4 + ADR-068 Amendment 3 + review-verdict-v4 v4.7 + CFP-1089" {
    grep -q "ADR-014 Amendment 4" "${EVIDENCE}"
    grep -q "ADR-068 Amendment 3" "${EVIDENCE}"
    grep -q "review-verdict-v4 v4.7" "${EVIDENCE}"
    grep -q "CFP-1089" "${EVIDENCE}"
}

@test "TC-5: Usage section path declaration 정합" {
    grep -q "tests/integration/baseline/<STORY-KEY>/§7.4-measurement-evidence.md" "${EVIDENCE}"
}
