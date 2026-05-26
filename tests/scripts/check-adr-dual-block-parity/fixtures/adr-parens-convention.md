---
id: ADR-9998
title: "Test ADR — parens-convention body (amendments[]-only, no amendment_log[]) (CFP-1734 bats TC-16)"
status: Accepted
category: governance
is_transitional: false
amendments:
  - amendment_id: 1
    summary: "Amendment 1 — parens-convention body style"
    carrier_cfp: CFP-0016
  - amendment_id: 2
    summary: "Amendment 2 — parens-convention body style"
    carrier_cfp: CFP-0017
mechanical_enforcement_actions: []
---

# ADR-9998: Test ADR parens-convention fixture

## 목적

CFP-1734 bats TC-16 fixture — amendments[]-only ADR using parens-convention body style.
No amendment_log[] block (amendments[]-only ADR).

Body uses `## §결정 N (Amendment M, CFP-XXX)` convention — e.g. ADR-071 real-world pattern.
BODY_AMENDMENT_PATTERN (`^#{2,3}\s+Amendment\s+([0-9]+)`) does NOT match this convention.

Expected behavior after Amendment 31 dual-block gate:
  amendments[]-only → dual_block = bool([1,2]) AND bool([]) = False → EXEMPT → PASS exit 0.

CFP-1688 behavior (pre-impl, RED state for TC-16):
  dual-block path entered (amendments[] non-empty) → Block 1 body detection →
  BODY_AMENDMENT_PATTERN misses parens-convention headers → body_ids = [] →
  AMENDMENTS_FRONTMATTER_ONLY for Amendment 1 and Amendment 2 → WARNING exit 1 (FP).

## 결정

### §결정 1. 기본 결정 사항 (Amendment 1, CFP-0016)

Amendment 1 본문 내용. parens-convention heading 사용.

### §결정 2. 두 번째 결정 사항 (Amendment 2, CFP-0017)

Amendment 2 본문 내용. parens-convention heading 사용.
