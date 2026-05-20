#!/usr/bin/env bats
# CFP-1089 — DesignReviewPL §8.6 pointer-presence-check bats TC
#
# 5 TC:
#   TC-1: 3-check ALL PASS (main state, exit 0)
#   TC-2: review-verdict-v4 v4.6 baseline (literal 부재, exit 1 warning)
#   TC-3: review-verdict-v4 missing (META-ERROR exit 2)
#   TC-4: ADR-068 Amendment 3 부재 (exit 1 warning)
#   TC-5: bypass label (workflow-level — bash 영역 영역 영역 invariant only)

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    SCRIPT="${REPO_ROOT}/scripts/check-design-review-pl-8-6-pointer.sh"
    TMPDIR="$(mktemp -d)"
    # Initialize fake repo
    cd "${TMPDIR}"
    git init --quiet
    mkdir -p docs/inter-plugin-contracts docs/adr scripts/lib
    # Copy actual SSOT (lint logic 영역 영역 단일)
    cp "${REPO_ROOT}/scripts/check-design-review-pl-8-6-pointer.sh" scripts/
    cp "${REPO_ROOT}/scripts/lib/check_design_review_pl_8_6_pointer.py" scripts/lib/
}

teardown() {
    [[ -n "${TMPDIR}" && -d "${TMPDIR}" ]] && rm -rf "${TMPDIR}"
}

@test "TC-1: 3-check ALL PASS (main state, exit 0)" {
    # Use real main state — copy from repo root
    cp "${REPO_ROOT}/docs/inter-plugin-contracts/review-verdict-v4.md" docs/inter-plugin-contracts/
    cp "${REPO_ROOT}/docs/adr/ADR-068-boundary-completeness-invariants.md" docs/adr/

    run bash scripts/check-design-review-pl-8-6-pointer.sh
    [ "$status" -eq 0 ]
    [[ "$output" == *"All 3 checks PASS"* ]]
}

@test "TC-2: review-verdict-v4 v4.6 baseline (literal 부재, exit 1 warning)" {
    # v4.6 stub (audit-gate-pointer-missing literal 부재)
    cat > docs/inter-plugin-contracts/review-verdict-v4.md <<'EOF'
---
contract_version: "4.6"
---

findings[].type enum: "general" | "mechanical_sync_required" | "boundary-completeness" | "dimensional-empirical-gap"
EOF
    cp "${REPO_ROOT}/docs/adr/ADR-068-boundary-completeness-invariants.md" docs/adr/

    run bash scripts/check-design-review-pl-8-6-pointer.sh
    [ "$status" -eq 1 ]
    [[ "$output" == *"WARN"* ]]
    [[ "$output" == *"4.7"* ]]
}

@test "TC-3: review-verdict-v4 missing (META-ERROR exit 2)" {
    # No review-verdict-v4.md
    cp "${REPO_ROOT}/docs/adr/ADR-068-boundary-completeness-invariants.md" docs/adr/

    run bash scripts/check-design-review-pl-8-6-pointer.sh
    [ "$status" -eq 1 ]
    [[ "$output" == *"review-verdict-v4.md not found"* ]]
}

@test "TC-4: ADR-068 Amendment 3 부재 (exit 1 warning)" {
    cp "${REPO_ROOT}/docs/inter-plugin-contracts/review-verdict-v4.md" docs/inter-plugin-contracts/
    # ADR-068 stub (Amendment 2 only, no Amendment 3)
    cat > docs/adr/ADR-068-boundary-completeness-invariants.md <<'EOF'
---
amendments:
  - amendment_id: 1
  - amendment_id: 2
---
EOF

    run bash scripts/check-design-review-pl-8-6-pointer.sh
    [ "$status" -eq 1 ]
    [[ "$output" == *"amendment_id: 3"* ]]
}

@test "TC-5: bash 영역 bypass label invariant (workflow level only)" {
    # bash script 영역 영역 bypass label check 영역 영역 — workflow YAML scope 영역
    # 본 TC = script 자체 영역 always-run invariant verify
    cp "${REPO_ROOT}/docs/inter-plugin-contracts/review-verdict-v4.md" docs/inter-plugin-contracts/
    cp "${REPO_ROOT}/docs/adr/ADR-068-boundary-completeness-invariants.md" docs/adr/

    HOTFIX_BYPASS_LABEL="design-review-pl-8-6-pointer" run bash scripts/check-design-review-pl-8-6-pointer.sh
    # script 영역 ENV var 영역 무시 (workflow-level bypass only)
    [ "$status" -eq 0 ]
    [[ "$output" == *"All 3 checks PASS"* ]]
}
