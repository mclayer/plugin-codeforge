#!/usr/bin/env bats
# CFP-1088 — §7.4 Axis 2 실측 evidence template bats fixture
#
# 본 fixture pair (Axis 2 + Axis 3) = template smoke test —
# IntegrationTestAgent self-write 시 evidence file schema 정합 verify.

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../../../.." && pwd)"
    EVIDENCE="${BATS_TEST_DIRNAME}/§7.4-measurement-evidence.md"
}

@test "TC-1: §7.4-measurement-evidence.md template file exists" {
    [ -f "${EVIDENCE}" ]
}

@test "TC-2: Axis 2 실측 결과 표 section present" {
    grep -q "## Axis 2 실측 결과" "${EVIDENCE}"
}

@test "TC-3: Axis 2 measurement_id + pointer + measured_value + empirical_source 6-column schema" {
    # Row schema: measurement_id | pointer (§8.6) | measured_value | unit | measurement_method | timestamp | empirical_source (7 cols)
    grep -q "measurement_id.*pointer.*measured_value.*unit.*measurement_method.*timestamp.*empirical_source" "${EVIDENCE}"
}

@test "TC-4: ADR-014 Amendment 4 §결정 2 cross-ref present" {
    grep -q "ADR-014 Amendment 4 §결정 2" "${EVIDENCE}"
}

@test "TC-5: ADR-068 Amendment 3 I-6 4-form pointer scope cross-ref" {
    grep -q "ADR-068 Amendment 3" "${EVIDENCE}"
    grep -q "4-form scope" "${EVIDENCE}"
}
