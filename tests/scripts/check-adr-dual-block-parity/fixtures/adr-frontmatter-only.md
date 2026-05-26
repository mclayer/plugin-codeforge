---
id: ADR-9992
title: "Test ADR — frontmatter amendment body section missing (CFP-1648 bats TC-2)"
status: Accepted
category: governance
is_transitional: false
amendments:
  - amendment_id: 1
    summary: "Amendment 1 summary"
    carrier_cfp: CFP-0003
amendment_log:
  - amendment_id: 1
    date: "2026-01-01"
    title: "Amendment 1 title"
    carrier_cfp: CFP-0003
mechanical_enforcement_actions: []
---

# ADR-9992: Test ADR frontmatter-only fixture

## 목적

CFP-1648 bats TC-2 fixture — frontmatter amendments[] has Amendment 1 entry
but body ## Amendment 1 section is MISSING.

This should trigger WARNING exit 1:
  AMENDMENTS_FRONTMATTER_ONLY: Amendment 1 in frontmatter amendments[] but body section missing
  AMENDMENT_LOG_FRONTMATTER_ONLY: Amendment 1 in frontmatter amendment_log[] but body section missing

## 결정

### §결정 1

테스트 결정 내용.

(intentionally missing ## Amendment 1 body section)
