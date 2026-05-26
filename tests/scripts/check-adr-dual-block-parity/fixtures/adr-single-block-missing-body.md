---
id: ADR-9996
title: "Test ADR — single-block missing body section WARNING (CFP-1688 bats TC-10)"
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment_id: 1
    date: "2026-01-01"
    title: "Amendment 1 title"
    carrier_cfp: CFP-1688
  - amendment_id: 2
    date: "2026-01-02"
    title: "Amendment 2 title — body section intentionally MISSING"
    carrier_cfp: CFP-1688
mechanical_enforcement_actions: []
---

# ADR-9996: Test ADR single-block missing body WARNING fixture

## 목적

CFP-1688 bats TC-10 fixture.

Single-block ADR (no amendments[] block, amendment_log[] only).
Amendment 1 has corresponding H3 body section.
Amendment 2 body section is INTENTIONALLY MISSING.

Expected: Block 2 retained → WARNING exit 1
  AMENDMENT_LOG_FRONTMATTER_ONLY: Amendment 2 in frontmatter amendment_log[]
  but body section missing (F-DR-001 P0 origin sentinel)

This verifies that Fix A does NOT weaken Block 2 (F-DR-001 P0 sentinel).
Single-block mode skips Block 1 and Block 3 but Block 2 fires correctly.

## 결정

### §결정 1

테스트 결정 내용.

### Amendment 1 — First amendment (CFP-1688)

Amendment 1 본문 섹션. amendment_log[1] 와 parity OK.

(intentionally missing ### Amendment 2 body section — Block 2 WARNING expected)
