---
kind: concept_definition
type: domain-knowledge
slug: aggregate
title: Aggregate — 2-layer explicit separate (governance metaphor ↔ application real boundary), 동음이의 차단
status: Active
updated: 2026-05-20
carrier_story: CFP-1117-S1
related_adrs:
  - ADR-091  # ArchitectLane DDD vocabulary governance — 본 개념의 normative SSOT (§결정 1 / §결정 3)
  - ADR-086  # Deputy 신설 결정 framework — codeforge governance Aggregate decision boundary 사례
related_files:
  - docs/glossary.md  # Aggregate entries SSOT (governance BC line 186-190 + application BC line 192-196)
  - plugin-codeforge-design/agents/AggregateArchitectAgent.md  # AggregateArch deputy mandate
  - docs/domain-knowledge/concept/bounded-context.md  # BC sibling
tags:
  - aggregate
  - ddd
  - tactical-design
  - governance-metaphor
  - consistency-boundary
  - homonym-disambiguation
---

# Aggregate

## 정의

`Aggregate` = **consistency boundary + transaction boundary + invariant enforcement scope**. DDD Tactical Design 의 핵심 building block — Entity + Value Object 의 cluster + 외부 진입점 (Aggregate Root) 단일 + 외부 reference 는 Aggregate Root 만 + transaction atomic = Aggregate 단위.

**핵심 invariant** (Eric Evans 2003):
- 1 Aggregate = 1 transaction unit (atomic save / atomic load)
- 외부에서 Aggregate 내부 entity 직접 접근 금지 — Aggregate Root 경유 의무
- Aggregate 안 invariant (예: 잔액 ≥ 0) 는 Aggregate Root 가 enforcement

## 컨텍스트

### codeforge 도입 동인

codeforge governance BC ↔ mctrader application BC 의 **동음이의 (homonym) 충돌** 누적 (MCT-170 / MCT-177 / MCT-179 / MCT-180 / MCT-184 / MCT-185 Phase 0 verify pattern 6회 재현). 동일 어휘 "Aggregate" 가 양 BC 에서 의미 분기:

- codeforge governance BC: supervised authority cluster (ArchitectPLAgent metaphor only)
- mctrader application BC: DDD Aggregate root in domain model (transactionally consistent)

cross-repo Story 진행 시 양 의미 혼동 → ADR 의 결정 영역이 model object 인지 process actor 인지 분기 차이 surface. ADR-091 §결정 3 이 2-layer explicit separate forcing function 부착.

### 적용 trigger

- ArchitectPLAgent 가 Story 단위 supervisor 역할 명시 시 (Layer A metaphor 적용)
- ArchitectAgent 의 산출물 (Change Plan + ADR draft + §8 + §11) author 시 (Layer B real Aggregate)
- AggregateArchitectAgent (deputy) 의 consumer aggregate boundary advocacy 시 (application BC reference)
- cross-repo Story (codeforge ↔ mctrader) 진행 시 동음이의 충돌 차단

### 관련 사건 (Codex Q5 합의)

Codex Q5 verbatim (ADR-091 발의 시점):

> PL = Aggregate Root 는 supervised authority 의 metaphor only. Change Plan + ADR draft 산출물 자체는 real consistency boundary. 핵심 invariant: §1-§11 + BC classification + aggregate impacts + language choices + risks + ADR rationale 가 handoff 전 cohere. CFP 가 "agent control metaphor" vs "artifact consistency boundary" 를 explicit separate 의무.

## 핵심 규칙

### R-1: 2-layer separate (ADR-091 §결정 3 verbatim)

ADR-091 §결정 3 의 핵심 forcing function — "Aggregate" 어휘 2 layer 로 explicit separate. **동음이의 (homonym) 충돌 차단 의무**.

| Layer | Aggregate 의미 | 적용 BC | 검증 mechanism |
|---|---|---|---|
| **Layer A — governance BC PL metaphor** | **supervised authority cluster** — ArchitectPLAgent 가 6 deputy + chief author 산출물 통합하는 supervisor 의 metaphor only | codeforge governance BC | ArchitectPLAgent role description 안 명시 (S2 agent frontmatter `ddd_pattern: Authority Pair (Aggregate Root metaphor)`) |
| **Layer B — governance BC ArchitectLane 산출물 = real Aggregate** | Change Plan + ADR draft + §8 Test Contract + §11 데이터 마이그레이션 = **real consistency boundary**. §1-§11 + BC classification + aggregate impacts + language choices + risks + ADR rationale 가 handoff 전 cohere 의무 | codeforge governance BC | ArchitectAgent 산출물 검증 — DesignReviewPL 의 review-verdict-v4 finding type `aggregate_violation` (S4 신설) cross-validate |

mctrader application BC 의 Aggregate (DDD Aggregate root in domain model) 은 **별 BC**. `docs/glossary.md` 안 3 distinct entry 로 명시 분리:
- [`Aggregate (governance BC)`](../../glossary.md#aggregate-governance-bc) — Layer A metaphor only
- [`Aggregate (mctrader application BC)`](../../glossary.md#aggregate-mctrader-application-bc) — application DDD Aggregate root
- [`Aggregate Root`](../../glossary.md#aggregate-root) — Layer A authority pair supervisor side

### R-2: Layer A 적용 — ArchitectPLAgent = Aggregate Root metaphor

ArchitectPLAgent 의 role = **supervisor of supervised authority cluster**. 6 SubAgent deputy + chief author (ArchitectAgent) 산출물 통합 책임.

**metaphor only 의 의미**:
- ArchitectPL = process participant (agent process), DDD Aggregate Root = domain object
- "Agent ↔ domain object" 강한 매핑 거부 (Codex Q2 합의)
- metaphor 사용은 **role description level** 에만 (frontmatter `ddd_pattern: Authority Pair (Aggregate Root metaphor)`)
- literal Aggregate Root invariant (예: identity persistence + lifecycle) 적용 안 함

**Authority Pair** (ADR-091 §결정 1 첫 enum):
- ArchitectPLAgent = supervisor side (Aggregate Root metaphor)
- ArchitectAgent = chief author side (산출물 = real Aggregate 의 author)

### R-3: Layer B 적용 — ArchitectLane 산출물 = real Aggregate

**진짜 consistency boundary**:
- Change Plan (§1-§11) + ADR draft + §8 Test Contract + §11 데이터 마이그레이션
- 단일 transaction unit = Story 단위 Phase 1 PR LAND
- atomic invariant: handoff 전 cohere — §1-§11 + BC classification + aggregate impacts + language choices + risks + ADR rationale

**Aggregate Root 역할** = ArchitectAgent (chief author):
- 6 deputy advocacy 산출물 verbatim 통합 (`§3.5` self-lint mechanical pre-check)
- final wording SSOT 결정 (deputy 간 충돌 시 chief tie-break ladder)
- §1-§11 + ADR draft author (외부 진입점 단일)

**boundary 검증** (Layer B real Aggregate invariant):
- DesignReviewPL 의 review-verdict-v4 finding type `aggregate_violation` (S4 신설, v4.7 → v4.8 MINOR bump)
- `aggregate_violation` = Change Plan §affected_aggregates 안 명시된 aggregate boundary 와 Story §1 실 영향 boundary 사이 inconsistency

### R-4: Aggregate Root 의 의무 (DDD literal, application BC 에서만 strict)

DDD literal definition (application BC 에서만 strict 적용):

1. **invariant 보호** — Aggregate 안 모든 entity / value object 의 state invariant enforcement 책임
2. **boundary 안 entity 만 access** — 외부에서 internal entity 직접 reference 금지. Aggregate Root 가 method delegate 또는 read-only view 제공
3. **Repository per Aggregate** — 1 Aggregate = 1 Repository. multi-Aggregate save = application service 의 multi-transaction (또는 Saga pattern)
4. **identity stable** — Aggregate Root identity = persistence identity (DB primary key 또는 UUID), 변경 안 됨
5. **transaction atomic** — 1 transaction = 1 Aggregate (cross-Aggregate transaction = eventually consistent, domain event 경유)

**codeforge governance BC 의 Layer A 적용 (metaphor only)**:
- ArchitectPLAgent = "invariant 보호" metaphor (deputy 간 wording 충돌 시 final tie-break)
- "boundary 안 entity 만 access" = ArchitectPL 가 deputy 직접 통신 차단 (chief author 경유 의무, ADR-039 default subagent context 정합)
- "Repository per Aggregate" = N/A (codeforge governance BC = Repository 패턴 부재, 직접 file Read/Write)

### R-5: Aggregate vs Entity vs Value Object (tactical pattern 표)

DDD Tactical Design 의 3 building block 분류:

| 패턴 | identity | mutability | equality | lifecycle | codeforge governance BC 사례 |
|---|---|---|---|---|---|
| **Aggregate** | Aggregate Root 가 보유 | mutable (Root method 경유) | Root identity-equal | Root lifecycle 따름 | ArchitectLane 산출물 (Change Plan + ADR draft) |
| **Entity** | 고유 identity | mutable | identity-equal (attribute-equal 아님) | 생성 / 변경 / 삭제 | Story (Story-key + phase lifecycle) / Change Plan / ADR file |
| **Value Object** | identity 없음 | **immutable** | **attribute-equal** | 변경 시 새 instance 생성 | inter-plugin contract payload (review-verdict / fix-event) / severity enum / phase enum |

**핵심 차이**:
- Entity = identity, Value Object = value
- Aggregate = consistency boundary, Entity / Value Object = building block of Aggregate
- 1 Aggregate Root = 1 Entity (but 1 Entity ≠ 1 Aggregate Root — non-root entity 는 Aggregate 내부 element)

## 경계

### 영역 안 (codeforge governance BC Aggregate scope)

- Layer A metaphor — ArchitectPLAgent role description + frontmatter `ddd_pattern` field
- Layer B real Aggregate — ArchitectLane 산출물 (Change Plan + ADR draft + §8 Test Contract + §11)
- ADR-086 5-checklist self-application = codeforge governance Aggregate decision boundary 사례
- AggregateArchitectAgent 의 process-participant role (codeforge governance BC 안 agent)

### 영역 외 (mctrader application BC Aggregate)

- mctrader 의 실 Aggregate 분류 (Order / Position / MarketSnapshot 등 domain model definition)
- mctrader 의 Aggregate Root invariant + Repository per Aggregate 구현 detail
- mctrader application BC 안 transactionally consistent boundary 의 RDB OLTP 구현
- consumer project 자체 도메인 BC 의 Aggregate (overlay 영역만 codeforge SSOT 와 contact)

### AggregateArchitectAgent 의 영역 boundary (process-participant vs mandate)

**중요 boundary**: AggregateArchitectAgent 가 codeforge governance BC 안 agent (process-participant 영역) 이지만, 그 mandate (RDB OLTP aggregate invariant / 트랜잭션 경계) 는 **application BC reference** (mandate 영역). codeforge governance BC 의 agent 가 application BC 의 design decision 영역에서 specialized judgment contributor 로 작동.

mctrader application BC 의 실 Aggregate 분류 + Aggregate Root 명세 + invariant 정의 = downstream Epic (별 CFP) — 본 codeforge SSOT 영역 외.

### 적용 사례: ADR-086 framework = codeforge governance Aggregate decision boundary

ADR-086 = **Deputy 신설 결정 framework** (5-checklist self-application).

**ADR-086 자체가 codeforge governance BC 의 Aggregate decision boundary 사례**:
- decision scope = Deputy 신설 (axis 1) / cost analysis (axis 2) / consumer impact (axis 3) / sibling cross-ref (axis 4) / deferred carrier path (axis 5)
- 5 axis 가 single consistency boundary — 1 Deputy 신설 결정이 5 axis 모두 통과 의무 (atomic, partial pass 금지)
- decision invariant: 5 axis 통과 = OK / 1+ axis 실패 = NOT OK (binary outcome)
- decision Aggregate Root = ADR-086 §결정 1 + §결정 2 self-application 표 (single entry point)

**Layer A metaphor 적용**:
- ArchitectPLAgent 가 ADR-086 5-checklist self-application 시 Aggregate Root metaphor 역할 (5 axis 통합 supervisor)
- decision artifact (ADR-086 5-checklist 표) = real Aggregate (consistency boundary)

**본 ADR-091 의 self-application 사례** (ADR-091 §결정 영역):
- agent 신설 0건이므로 framework axis 1 (결정 영역) 영역 외
- axis 4 (sibling cross-ref) + axis 5 (deferred carrier path) 만 적용
- 5-checklist 통과 = 본 CFP-1117 진행 가능 (ADR-091 amendment_log + amendments 참조)

## 관련 ADR

- [ADR-091 §결정 1](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — agent ↔ DDD pattern Hybrid mapping (Authority Pair / Domain Service / Subdomain Specialist enum)
- [ADR-091 §결정 3](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Aggregate metaphor 2-layer explicit separate (Layer A / Layer B)
- [ADR-086](../../adr/ADR-086-deputy-creation-decision-framework.md) — Deputy 신설 결정 framework (5-checklist self-application) = codeforge governance Aggregate decision boundary 사례
- [`docs/glossary.md` Aggregate (governance BC)](../../glossary.md#aggregate-governance-bc) — Layer A SSOT
- [`docs/glossary.md` Aggregate (mctrader application BC)](../../glossary.md#aggregate-mctrader-application-bc) — application BC SSOT (별 BC)
- [`docs/glossary.md` Aggregate Root](../../glossary.md#aggregate-root) — Authority Pair supervisor metaphor
- [`docs/domain-knowledge/concept/bounded-context.md`](bounded-context.md) — BC sibling (동음이의 차단 동인)

## 변경 이력

- 2026-05-20 KST — CFP-1117 Story-1 carrier 신규 작성 (ArchitectAgent direct write per ADR-070)
