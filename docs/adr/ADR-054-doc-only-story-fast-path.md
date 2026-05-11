---
adr_number: 54
title: "doc-only Story fast-path 분류 표 + fallback 규칙"
status: Accepted
date: 2026-05-10
category: Process
carrier_story: CFP-363
parent_epic: null
supersedes: null
amends: ADR-013
amendments: []
related_stories:
  - CFP-357
  - CFP-358
  - CFP-363
  - CFP-364
related_adrs:
  - ADR-013
  - ADR-024
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
is_transitional: false
---

# ADR-054: doc-only Story fast-path 분류 표 + fallback 규칙

## 상태

**Accepted (2026-05-10)** — CFP-363 carrier story.

## 컨텍스트

CFP-357(ADR-053 신설, 정상 5-lane)과 CFP-358(playbook only, lane 단축) 두 케이스가
동일한 SSOT 문서 변경임에도 lane 진행 방식이 갈려 비일관성 발생.
판정 기준 부재가 원인 (amends ADR-013 §강제 대상 분류).

ADR-013은 Story 작성 의무의 강제/면제 기준을 정의하지만, "강제 대상인 변경 중 구현 lane 없이 처리 가능한 doc-only 케이스"에 대한 별도 경로가 없어 모든 강제 대상이 full 5-lane을 밟게 된다. 이는 doc-only 변경에 과도한 비용을 부과하고, 판정 기준 부재로 인해 Orchestrator가 임의 결정을 내리는 문제를 야기한다.

## 결정

### §결정 1 — 3-way 분류 표

| 분류 | 조건 | Lane |
|---|---|---|
| **chore** | typo·링크·lint·dependency bump (SSOT 의미 변경 없음) | Story 불필요; commit body에 `Story 면제 사유:` 명시 |
| **doc-only fast-path** | SSOT 문서 변경 + (기존 ADR Amendment 또는 ADR 없음) + src/tests 무변경 | 요구사항 → 설계 → 경량 설계리뷰 → 단일 PR close |
| **full-lane** | 신규 ADR 도입 OR src/tests 변경 OR `templates/github-workflows/**` 변경 | 기존 5-lane 전체 (Phase 1 PR + Phase 2 PR) |

### §결정 2 — 모호 시 fallback

분류 판단 불가 = **full-lane 강제**. 안전 방향 우선 (ADR-013 cutoff precedent 정합).

### §결정 3 — fast-path lane sequence

```
요구사항 lane → 설계 lane → 경량 설계리뷰 → 단일 PR merge
(구현 lane spawn 금지)
```

- **경량 설계리뷰**: DesignReviewPL가 문서 정합성(링크·frontmatter·섹션 스키마)만 검증; code quality/test 섹션 skip
- **Story file**: §1·§2·§11 필수; §3~§10은 `N/A — doc-only fast-path (ADR-054)` 선언 의무
- **Phase 분리 없음**: 단일 PR (Phase 1 / Phase 2 PR 분리 X)

### §결정 4 — 신규 ADR 도입 = full-lane 강제

ADR 자체가 설계 결정 SSOT이므로, 설계리뷰 lane 생략 시 self-review 회로 발생.
신규 ADR 도입 Story = fast-path 제외, full-lane 의무.

### §결정 5 — `templates/**` 변경 판정

- `templates/github-workflows/**` 변경 = full-lane (workflow 변경 = 구조 영향)
- 그 외 `templates/**` = ArchitectAgent 판단 (영향 범위·consumer migration 여부 기준)

## 결과

- CFP-357 vs CFP-358 유형 lane 진행 비일관성 제거
- Orchestrator가 Story 시작 시 3-way 분류 판정 의무 (§결정 1·2)
- CLAUDE.md + playbook 반영은 CFP-364 (후속 Story-2) SSOT

## 관련

- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — Story 작성 의무 강제/면제 기준 (본 ADR이 doc-only fast-path 카테고리 추가)
- [ADR-024](ADR-024-story-scoped-branch-policy.md) — Story-scoped branch policy
- CFP-357, CFP-358 — 비일관성 발생 케이스
- CFP-364 — CLAUDE.md + playbook 반영 (후속)

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) — Story 작성 의무 강제/면제 분류 섹션 (CFP-364에서 doc-only fast-path 분류 추가 예정)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — Orchestrator 3-way 분류 판정 절차 반영 (CFP-364)
