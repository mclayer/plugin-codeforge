---
id: ADR-9995
title: "Test ADR — single-block (amendment_log[] only) with H3 body sections PASS (CFP-1688 bats TC-9/12/13)"
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
    title: "Amendment 2 title"
    carrier_cfp: CFP-1688
  - amendment_id: 3
    date: "2026-01-03"
    title: "Amendment 3 title"
    carrier_cfp: CFP-1688
mechanical_enforcement_actions: []
---

# ADR-9995: Test ADR single-block H3 PASS fixture

## 목적

CFP-1688 bats TC-9/TC-12/TC-13 fixture.

Single-block ADR (no amendments[] block, amendment_log[] only) — Fix A scenario.
Body uses H3 (###) amendment headings — Fix B scenario.
H4 (#### §D-N) sub-sections present — Fix B H4 guard scenario.

All 3 amendment_log[] entries have corresponding H3 body sections → PASS expected.
No amendments[] block → single-block mode → Block 1 + Block 3 skip.
Block 2 (amendment_log[] ↔ body H3): all 3 present → no violations.

## 결정

### §결정 1

테스트 결정 내용.

#### §D-1 세부 결정

H4 sub-section. Must NOT be detected as Amendment section by lint
(BODY_AMENDMENT_PATTERN {2,3} upper bound excludes H4).

### Amendment 1 — First amendment (CFP-1688)

Amendment 1 본문 섹션. amendment_log[1] 와 parity OK (H3 heading).

#### §D-1 적용 evidence

H4 evidence sub-note. Must NOT be detected as Amendment section.

### Amendment 2 — Second amendment (CFP-1688)

Amendment 2 본문 섹션. amendment_log[2] 와 parity OK (H3 heading).

### Amendment 3 — Third amendment (CFP-1688)

Amendment 3 본문 섹션. amendment_log[3] 와 parity OK (H3 heading).
