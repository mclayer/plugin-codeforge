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

Expected (ADR-082 Amendment 31 sub-scope 1-T, supersedes CFP-1688 Fix A):
  Single-block ADR (amendment_log[] only, no amendments[]) → EXEMPT via
  dual-block gate → PASS exit 0. No Block 2 check.

CFP-1688 (Fix A) previously ran Block 2 here → WARNING exit 1. Amendment 31
narrows the lint to dual-block-only ADRs, so single-block ADRs (incl. this
one) are now exempt. F-DR-001 P0 sentinel protection is preserved for
DUAL-BLOCK ADRs (see adr-amendment-log-missing.md / TC-4), not single-block.

## 결정

### §결정 1

테스트 결정 내용.

### Amendment 1 — First amendment (CFP-1688)

Amendment 1 본문 섹션. amendment_log[1] 와 parity OK.

(intentionally missing ### Amendment 2 body section — Block 2 WARNING expected)
