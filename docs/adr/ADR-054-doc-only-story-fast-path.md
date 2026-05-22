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
  - amendment_id: 2
    date: 2026-05-22
    carrier_story: CFP-1247
    title: "doc-only fast-path Category 2 → ADR-052 Codex 6-touchpoint dispatch 면제 explicit declare"
    description: |
      §결정 7 신설 — doc-only fast-path (Category 2) Story 는 lane spawn 0 (단일 PR,
      6-lane gate 면제) 이므로 ADR-052 Codex 6 touchpoint (lane stage 발동 — TP#1
      AskUserQuestion 직전 / TP#2 ArchitectAgent §3 직후 mandatory CFP-532 / TP#3
      DeveloperPL FIX 2+ / TP#4 RequirementsPL §1-§6 / TP#5 ArchitectPL root cause /
      TP#6 ArchitectAgent ADR 초안) 가 자연히 0회 발동한다. 본 면제가 implicit (lane
      부재의 귀결) 이고 정책 SSOT 에 explicit 미명시 — CFP-1125 (9-ADR sunset doc-only)
      retro 가 TP#0~#6 0회 발동을 의도된 design 으로 확인 (§6 escalation 후보 (a)).
      §결정 7 = 이 면제를 explicit codify (ambiguity 차단). ADR-052 cross-ref.
    sunset_justification: |
      metric — doc-only fast-path Category 2 Story 의 Codex touchpoint dispatch 0회
        (lane spawn 0 = touchpoint 발동 지점 0, CFP-1125 retro TP#0~#6 0회 sentinel).
      who — Orchestrator (Story 분류 시 doc-only fast-path 판정 = touchpoint 면제 동반).
      how — Story 분류 시 doc-only fast-path (Category 2) 판정 시 ADR-052 6-touchpoint
        dispatch skip (lane spawn 부재 = 자연 귀결). full-lane / Phase 2 src 변경 Story =
        touchpoint mandatory 영역 retain (§결정 7 면제 = doc-only Category 2 한정).
      NOTE — 본 Amendment = explicit codify (기존 implicit 동작 명시화, 약화 0 — 면제
        영역이 lane spawn 0 의 자연 귀결이므로 ratchet 중립, ADR-058 §결정 5 정합).
related_stories:
  - CFP-357
  - CFP-358
  - CFP-363
  - CFP-364
related_adrs:
  - ADR-013
  - ADR-024
  - ADR-052
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

### §결정 7 — Amendment 2: doc-only fast-path Category 2 → ADR-052 Codex 6-touchpoint dispatch 면제 (explicit declare)

**Amendment 2 (2026-05-22 KST, carrier_story: CFP-1247)**: doc-only fast-path (§결정 1 "doc-only fast-path" 분류 = Category 2) Story 는 lane spawn 0 (§결정 3 — 단일 PR, 구현 lane spawn 금지, 6-lane gate 면제) 이므로, **ADR-052 Codex 6 touchpoint 의 mandatory dispatch 가 자연히 0회 발동**한다. 본 면제를 explicit codify — ratchet 중립 (기존 implicit 동작 명시화, 약화 0).

**면제 근거 (lane gate 면제의 자연 귀결)**:

ADR-052 6 touchpoint 는 모두 **lane stage 에서 발동**한다:

| touchpoint | 발동 지점 (lane stage) | doc-only fast-path 발동 여부 |
|---|---|---|
| TP#1 | `AskUserQuestion` 직전 | 면제 (해당 시 dialog turn — lane 무관, optional 영역) |
| TP#2 | ArchitectAgent §3 완료 직후 (**mandatory** CFP-532) | **면제** (doc-only = §3 N/A, ArchitectAgent §3 산출물 부재) |
| TP#3 | DeveloperPLAgent FIX 2+ 감지 | 면제 (구현 lane spawn 0 = FIX loop 부재) |
| TP#4 | RequirementsPLAgent §1-§6 완료 직후 (multi-round debate) | 면제 (경량 요구사항 — debate 발동 영역 외) |
| TP#5 | ArchitectPLAgent root cause 판정 직후 | 면제 (FIX 부재 = root cause 판정 부재) |
| TP#6 | ArchitectAgent ADR 초안 완료 직후 | **면제 단 조건부** — 신규 ADR 도입 = §결정 4 full-lane 강제 (doc-only fast-path 제외) → TP#6 가 doc-only 영역에서 발동할 ADR 초안 = 기존 ADR Amendment only (신규 ADR 아님) |

→ doc-only fast-path Category 2 = lane spawn 0 = 6 touchpoint 발동 지점 0. 특히 **TP#2 mandatory (CFP-532)** 도 doc-only 에서는 §3 (도입할 설계) 산출물 자체가 `N/A — doc-only fast-path` (§결정 3) 이므로 dispatch 대상 부재.

**면제 boundary (Category 2 한정)**:

- 면제 = **doc-only fast-path (Category 2) 한정**. full-lane Story (신규 ADR / src·tests 변경 / `templates/github-workflows/**`) = ADR-052 6 touchpoint mandatory 영역 **retain** (특히 TP#2 mandatory CFP-532).
- §결정 6 (Amendment 1) declarative seed fast-path 영역도 본 면제 적용 (doc-only fast-path 의 sub-영역 — lane spawn 0 동일).
- **신규 ADR 도입 시 TP#6 영역**: §결정 4 가 신규 ADR = full-lane 강제 이므로, doc-only fast-path 안에서 ADR 초안 = 기존 ADR Amendment only → 신규 ADR 의 TP#6 mandatory 는 full-lane 경로에서 retain (모순 없음).

**SSOT 위임**: ADR-052 본문은 본 §결정 7 을 doc-only fast-path 면제 SSOT 로 cross-ref only (중복 codification 회피, ADR-065 §결정 5 정합). 본 ADR-054 §결정 7 = 면제 영역 anchor.

**mechanical enforcement N/A**: 면제는 lane spawn 0 의 자연 귀결 (touchpoint 발동 지점 부재) 이므로 별도 enforce 불요. declaration-only (CFP-1125 retro TP#0~#6 0회 sentinel 이 이미 의도된 design 확인).

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
