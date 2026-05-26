---
id: ADR-9994
title: "Test ADR — amendment_log frontmatter only, body missing (CFP-1648 bats TC-4 F-DR-001 sentinel)"
status: Accepted
category: governance
is_transitional: false
amendments:
  - amendment_id: 1
    summary: "Amendment 1 in amendments[]"
    carrier_cfp: CFP-0004
amendment_log:
  - amendment_id: 1
    date: "2026-01-01"
    title: "Amendment 1 — amendment_log entry (F-DR-001 P0 origin)"
    carrier_cfp: CFP-0004
mechanical_enforcement_actions: []
---

# ADR-9994: Test ADR amendment_log F-DR-001 sentinel fixture

## 목적

CFP-1648 bats TC-4 fixture — F-DR-001 P0 origin sentinel scenario:
  frontmatter amendment_log[] has Amendment 1 entry
  frontmatter amendments[] has Amendment 1 entry
  BUT body ## Amendment 1 section is MISSING

This is the exact failure pattern from CFP-1637 retro F-DR-001:
  "Amendment 26 amendment_log body section missing despite frontmatter present"

Expected violations:
  AMENDMENTS_FRONTMATTER_ONLY: Amendment 1 in frontmatter amendments[] but body section missing
  AMENDMENT_LOG_FRONTMATTER_ONLY: Amendment 1 in frontmatter amendment_log[] but body section missing (F-DR-001 P0 origin sentinel)

## 결정

### §결정 1

테스트 결정 내용.

(intentionally missing ## Amendment 1 body section — F-DR-001 sentinel)
