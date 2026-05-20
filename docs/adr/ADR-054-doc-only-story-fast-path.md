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
amendments:
  - amendment_id: 1
    date: 2026-05-20
    carrier_story: CFP-1059
    title: "fast-path 영역 확장 — declarative seed (신규 ADR + Wave 1 declarative-only workflow / script) boundary 명확화"
    description: |
      §결정 1 3-way 분류 표의 "full-lane" 행 조건을 boundary refinement.
      신규 ADR 도입 / `templates/github-workflows/**` 변경 / `scripts/**` 변경 영역이
      Wave 1 declarative-only 상태 (실 wire = 후속 Story carrier) 인 경우 fast-path 가능
      영역으로 명확화. 실 wire 시점 = full-lane 재거침 의무 invariant 보존 (ratchet 강화).
    sunset_justification: |
      metric — declarative-only → full-lane wire promotion 시점 1:1 matching
        (Wave 1 declare 1 → 후속 Story wire 1 = full-lane 재거침 의무).
      who — ArchitectPLAgent + DesignReviewPL (각 carrier Story FIX iter 시점 verify).
      how — spec/plan 안 "Wave 1 declarative-only" 명시 + 후속 carrier Story file 안
        `wave_2_wire_carrier: <S2 또는 S3>` 명시. ADR frontmatter
        `mechanical_enforcement_actions[]` entry status `declaration-only-Wave-1 → warning`
        promotion = full-lane 거침 의무 anchor.
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

### §결정 6 — Amendment 1 boundary refinement (declarative seed = Wave 1 정합 영역)

**Amendment 1 (2026-05-20 KST, carrier_story: CFP-1059)**: §결정 4 / §결정 5 boundary
refinement — fast-path 영역 확장 (declarative seed 영역 포함). **ratchet 강화 방향** —
약화 NOT (boundary 명확화 + 실 wire 시점 full-lane 강제 retain).

**fast-path 적격 declarative seed 3 영역**:

1. **신규 ADR 도입 + Wave 1 declarative-only 결합 영역 = fast-path 가능** — 단 본 ADR 의
   `mechanical_enforcement_actions[]` 모두 `declaration-only-Wave-1` 상태 (실 wire =
   후속 carrier Story 영역 full-lane 의무). 이 조건 미충족 시 full-lane 강제 retain
   (§결정 4 default 우선).

2. **`templates/github-workflows/**` 변경 = declarative seed (Phase 1 declarative
   workflow file + actual job body placeholder echo + `continue-on-error: true`) 영역 =
   fast-path 가능** — 단 actual workflow runs jobs body + lint script + bats fixture
   pair 신설 영역 = full-lane 강제 retain (declarative-only → wire promotion = full-lane
   재거침 의무, §결정 5 default 우선).

3. **`scripts/**` 변경 = label-registry sync / atomic-upgrade sync 영역
   (declaration-only-Wave-1 정합) = fast-path 가능** — 본 영역 = mechanical sync
   (ADR-065 7-item) 의무 정합. 신규 lint script body / 실 enforcement script 신설 영역
   = full-lane 강제 retain.

**Boundary invariant** (ratchet 강화):

- declarative seed 1 → 후속 carrier Story wire 1 = full-lane 재거침 의무 (1:1 matching).
- `declaration-only-Wave-1 → warning` tier promotion 시점 = full-lane 강제 발효 anchor.
- spec/plan 안 "Wave 1 declarative-only" 명시 + 후속 carrier Story file 안
  `wave_2_wire_carrier: <S2 또는 S3>` 명시 의무.

**자기적용 사례** (carrier CFP-1059 Story-1 자체):
- ADR-087/088/089/090 신설 + Wave 1 declarative-only `mechanical_enforcement_actions[]`
  = §결정 6.1 fast-path 적격
- `templates/github-workflows/` 7 seed + `continue-on-error: true` placeholder
  = §결정 6.2 fast-path 적격
- `scripts/bootstrap-labels.sh` + `atomic-upgrade-7-plugins.sh` sync = §결정 6.3 fast-path 적격

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
