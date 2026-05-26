---
id: ADR-9993
title: "Test ADR — body section present but frontmatter row missing (CFP-1648 bats TC-3)"
status: Accepted
category: governance
is_transitional: false
amendments: []
amendment_log: []
mechanical_enforcement_actions: []
---

# ADR-9993: Test ADR body-only fixture

## 목적

CFP-1648 bats TC-3 fixture — body ## Amendment 1 section exists
but frontmatter amendments[] AND amendment_log[] rows are EMPTY/MISSING.

This should trigger WARNING exit 1:
  BODY_ONLY_NO_AMENDMENTS: Amendment 1 in body section but frontmatter amendments[] row missing
  BODY_ONLY_NO_LOG: Amendment 1 in body section but frontmatter amendment_log[] entry missing

## 결정

### §결정 1

테스트 결정 내용.

## Amendment 1 — Body section only (no frontmatter entry)

이 Amendment 1 body section 은 frontmatter amendments[] 와 amendment_log[] 에
대응 entry 가 없다. parity drift = WARNING 발화.
