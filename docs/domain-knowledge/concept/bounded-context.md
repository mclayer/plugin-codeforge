---
kind: concept_definition
type: domain-knowledge
slug: bounded-context
title: Bounded Context — 도메인 모델 일관성 경계, 동음이의 회피 forcing function
status: Active
updated: 2026-05-20
carrier_story: CFP-1117-S1
related_adrs:
  - ADR-091  # ArchitectLane DDD vocabulary governance — 본 개념의 normative SSOT (§결정 3 / §결정 4 / §결정 5)
  - ADR-013  # codeforge-family-dogfood-out-policy — Published Language 분리 정합 (codeforge ↔ mctrader 양 SSOT)
  - ADR-086  # Deputy 신설 결정 framework — Aggregate decision boundary 사례
related_files:
  - docs/glossary.md  # Bounded Context entry SSOT (line 77-82)
  - docs/domain-knowledge/concept/aggregate.md  # 2-layer separate sibling
  - docs/domain-knowledge/concept/ubiquitous-language.md  # BC 내부 어휘 SSOT sibling
tags:
  - bounded-context
  - ddd
  - strategic-design
  - governance-bc
  - published-language
  - vocabulary-governance
---

# Bounded Context (BC)

## 정의

`Bounded Context` (BC) = **도메인 모델이 일관성 있게 적용되는 명시적 경계**. 같은 용어가 다른 BC 에서 다른 의미를 가질 수 있으며, BC 사이 통신은 explicit (Context Map + Published Language) 의무. DDD Strategic Design 의 핵심 building block.

**한국어 표기**: `한정된 컨텍스트` / `경계 컨텍스트` (영어 표기 권장 — 한국어 번역 비표준). SSOT = [`docs/glossary.md` Bounded Context entry](../../glossary.md#bounded-context-bc).

## 컨텍스트

### codeforge 도입 동인

codeforge governance BC 는 mctrader application BC 와의 cross-repo Story 진행 중 **동음이의 (homonym) 충돌** 누적 사례 (MCT-170 / MCT-177 / MCT-179 / MCT-180 / MCT-184 / MCT-185 Phase 0 verify pattern 6회 재현) 가 동인. 암묵적 BC/Aggregate 결정이 ADR 에 명시 안 됨 → 신규 agent / member 합류 시 interpretation drift surface.

특히 "Aggregate" 어휘가 codeforge governance BC (supervised authority cluster — ArchitectPLAgent metaphor) 와 mctrader application BC (DDD Aggregate root in domain model — Order / Position / MarketSnapshot 등) 양쪽에서 사용되면서 cross-repo Story 진행 시 의미 혼동 reproducible. ADR-091 §결정 3 이 본 동음이의 차단을 forcing function 으로 명시화.

### 적용 trigger

- ArchitectLane 산출물 (Change Plan + ADR draft) 에서 DDD 어휘 사용 시 → 본 entry SSOT 인용 의무
- 신규 agent / member 합류 시 onboarding context (which BC am I working in?)
- cross-repo Story (codeforge ↔ mctrader) 진행 시 Published Language 경유 의무
- consumer project 도메인 BC 와의 통신 mechanism 결정 시

### cross-repo 사례 (codeforge ↔ mctrader)

mctrader-hub 의 ADR-031 (4-Layer Architecture) 가 codeforge governance BC 의 4-Layer entry 와 cross-reference. 양 BC 가 4-Layer 패턴 답습하지만 **도메인 영역 disjoint** — codeforge governance BC = process-oriented (agent orchestration), mctrader application BC = data-oriented (시장 데이터 + 거래 execution).

## 핵심 규칙

### R-1: codeforge = single governance BC

codeforge 자체 = **single Bounded Context** (governance domain). codeforge wrapper plugin 6 lane (requirements / design / develop / review / test / pmo) = single BC 안 **sub-module** (DDD Module sense).

**근거**:
- 전체 codeforge family 가 단일 Ubiquitous Language (`docs/glossary.md`) 공유 — 모든 agent / ADR / Change Plan / Story file 안 어휘 SSOT 동일.
- 7 plugin 사이 통신 = **Shared Kernel** 패턴 (inter-plugin contracts: review-verdict-v4 / fix-event-v1 / label-registry-v2 등). 양쪽 동시 합의 의무 (ADR-008 versioning + ADR-010 sibling sync).
- codeforge governance BC 의 도메인 = **Story 단위 governance decision-making** (Architect lane 의 chief author 통합 + deputy advocacy synthesis + FIX root-cause 판정).

### R-2: Subdomain 분류 (codeforge governance BC 안)

| Subdomain 분류 | codeforge governance BC 적용 |
|---|---|
| **Core** | ArchitectLane decision-making (chief author 통합 + deputy advocacy synthesis) — `codeforge-design` plugin 핵심 |
| **Supporting** | lane evidence tracking (Story §14) + retro automation (PMOAgent) + FIX Ledger 관리 |
| **Generic** | GitHub MCP API integration + git worktree management + label/milestone CRUD |

### R-3: Module ↔ Bounded Context 관계 (ADR-091 §결정 5)

ADR-091 §결정 5 = **15 agent frontmatter 의무 field 2종**:

```yaml
bounded_context: codeforge-governance  # governance BC | application BC (downstream) | shared-kernel | ...
ddd_pattern: Authority Pair | Domain Service | Subdomain Specialist  # §결정 1 enum
```

- `bounded_context` = 어느 BC 안에서 작동하는지 explicit declare
- `ddd_pattern` = 어느 DDD role enum 인지 explicit declare

S2 LAND 시 15 agent 전수 field 채워짐 (null 금지). lint script `scripts/check-ddd-pattern-frontmatter.sh` (warning tier, S3 신설) 가 cross-validate.

**중요**: 1 plugin ≠ 1 BC. plugin 은 module 수준 분류 (DDD Module pattern), BC 는 도메인 일관성 경계 (DDD Strategic Design). codeforge family 전체가 단일 BC 인 이유 = 모든 plugin 이 동일 Ubiquitous Language `docs/glossary.md` (wrapper SSOT) 정합 의무.

### R-4: 동음이의 회피 표 (Aggregate governance BC ↔ application BC)

BC 의 핵심 가치 = **동음이의 (homonym) 충돌 차단**. codeforge 의 첫 적용 사례:

| 용어 | codeforge governance BC 안 의미 | mctrader application BC 안 의미 |
|---|---|---|
| **Aggregate** | supervised authority cluster — ArchitectPLAgent 의 metaphor only | DDD Aggregate root in domain model — Entity + Value Object 집합, transactionally consistent |
| **Module** | codeforge family 7 plugin (wrapper + 6 lane) high-cohesion grouping | 도메인 module — layered/hexagonal/clean 안 high-cohesion grouping |
| **Repository** | 부재 (직접 file Read/Write) | DDD Repository pattern — Aggregate 단위 collection abstraction |

ADR-091 §결정 3 가 본 동음이의 차단을 forcing function 으로 명시화. 양 BC 의 Aggregate entry 가 `docs/glossary.md` 안 2 distinct entry 로 explicit separate.

### R-5: Published Language 분리 의무 (ADR-091 §결정 4)

BC 사이 통신 = **Published Language** 의무. content duplication 금지 — link only.

| BC | Published Language SSOT |
|---|---|
| codeforge governance BC | [`plugin-codeforge/docs/glossary.md`](../../glossary.md) (본 ADR-091 Story-1 신규) |
| mctrader application BC | `mctrader-hub/docs/glossary.md` (downstream Epic, 별 CFP) |

양 glossary 가 cross-reference (link only). 동음이의 (Aggregate / Module / Repository 등) 의 의미 충돌 차단.

**Content duplication 금지 근거** (ADR-013 정합): codeforge family 가 자신 사용 ≠ 외부 discipline 채택 = self-application 위반 0. mctrader 의 application detail 을 codeforge governance SSOT 안 명시 = governance BC ↔ application BC 동음이의 충돌 + ADR-013 dogfood-out policy 위반.

## 경계

### 영역 안 (codeforge governance BC SSOT scope)

- codeforge family 7 plugin (wrapper + 6 lane) 의 governance domain
- ArchitectLane 산출물 (Change Plan + ADR draft + §8 Test Contract + §11 데이터 마이그레이션)
- inter-plugin contracts (review-verdict-v4 / fix-event-v1 / label-registry-v2 / debate-protocol-v1 / git-ops-event-v1 등)
- 본 plugin-codeforge repo 안 모든 도메인 knowledge 문서 (`docs/domain-knowledge/`)
- agent file 본문 (15 agent in `plugin-codeforge-design/agents/`)
- ADR 본문 + Change Plan + Story file + skill file + CLAUDE.md (wrapper + lane plugin)

### 영역 외 (mctrader application BC 및 downstream Epic 영역)

- mctrader 의 실 Aggregate 분류 (Order / Position / MarketSnapshot 등 domain model definition)
- mctrader 의 Aggregate Root invariant + Repository per Aggregate 구현 detail
- 거래소 (Bithumb / Binance 등) API adapter 구현 detail
- mctrader-hub `docs/glossary.md` 안 application BC term 정의 SSOT
- consumer project 의 자체 도메인 BC (overlay 영역만 codeforge SSOT 와 contact)

### Published Language 경유 통신

양 BC 사이 통신 시 본 BC entry 안 mctrader application detail 명시 금지. pointer + verbatim cite only:
- mctrader BC link 만 (예: `mctrader-hub/docs/glossary.md`)
- 양 BC 가 동시 답습하는 패턴 (예: 4-Layer Architecture) 은 verbatim cite + cross-ref 형식

### 적용 사례: ModuleArchitectAgent (aggregate-level) 의 "RDB OLTP aggregate invariant"

ModuleArchitectAgent (aggregate-level — 구 AggregateArchitectAgent, CFP-1126 / ADR-042 Amd 10 통합) 의 mandate = **consumer aggregate boundary 설계 advocacy** (application BC 안 design task 영역).

**중요 사례**: ModuleArchitectAgent (aggregate-level) 가 codeforge governance BC 안 agent 이지만, 그 mandate (RDB OLTP aggregate invariant / 트랜잭션 경계) 는 **application BC reference** 이다. codeforge governance BC 의 agent 가 application BC 의 design decision 영역에서 specialized judgment contributor 로 작동.

**Authority Pair (ArchitectPL + ArchitectAgent)** 가 final author authority — ModuleArchitectAgent (aggregate-level) 는 specialized advocacy 만 contribute. 본 BC boundary = "agent 가 어느 BC 안에서 작동하는가" (codeforge governance BC) ≠ "agent mandate 의 적용 대상 BC" (consumer application BC) — 2 distinct dimension.

## 관련 ADR

- [ADR-091 §결정 3](../../../archive/adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Aggregate metaphor 2-layer explicit separate
- [ADR-091 §결정 4](../../../archive/adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Published Language 분리 (codeforge + mctrader 2 SSOT)
- [ADR-091 §결정 5](../../../archive/adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Bounded Context governance + 15 agent frontmatter field 의무
- [ADR-013](../../../archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md) — codeforge-family-dogfood-out-policy (Published Language 분리 정합)
- [ADR-086](../../../archive/adr/ADR-086-deputy-creation-decision-framework.md) — Deputy 신설 결정 framework (Aggregate decision boundary 사례)
- [`docs/glossary.md`](../../glossary.md) — Bounded Context entry SSOT (line 77-82)
- [`docs/domain-knowledge/concept/aggregate.md`](aggregate.md) — Aggregate 2-layer separate sibling
- [`docs/domain-knowledge/concept/ubiquitous-language.md`](ubiquitous-language.md) — BC 내부 어휘 SSOT sibling
- [`docs/domain-knowledge/concept/4-layer-architecture.md`](4-layer-architecture.md) — mctrader ADR-031 4-Layer 모델 cross-ref

## 변경 이력

- 2026-05-20 KST — CFP-1117 Story-1 carrier 신규 작성 (ArchitectAgent direct write per ADR-070)
