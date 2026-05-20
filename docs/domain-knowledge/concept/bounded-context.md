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

## 동음이의 회피 (Aggregate governance BC ↔ application BC)

BC 의 핵심 가치 = **동음이의 (homonym) 충돌 차단**. codeforge 의 첫 적용 사례:

| 용어 | codeforge governance BC 안 의미 | mctrader application BC 안 의미 |
|---|---|---|
| **Aggregate** | supervised authority cluster — ArchitectPLAgent 의 metaphor only | DDD Aggregate root in domain model — Entity + Value Object 집합, transactionally consistent |
| **Module** | codeforge family 7 plugin (wrapper + 6 lane) high-cohesion grouping | 도메인 module — layered/hexagonal/clean 안 high-cohesion grouping |
| **Repository** | 부재 (직접 file Read/Write) | DDD Repository pattern — Aggregate 단위 collection abstraction |

ADR-091 §결정 3 가 본 동음이의 차단을 forcing function 으로 명시화. 양 BC 의 Aggregate entry 가 `docs/glossary.md` 안 2 distinct entry 로 explicit separate.

## codeforge 의 governance BC 정의

codeforge 자체 = **single Bounded Context** (governance domain). codeforge wrapper plugin 6 lane (requirements / design / develop / review / test / pmo) = single BC 안 **sub-module** (DDD Module sense).

**근거**:
- 전체 codeforge family 가 단일 Ubiquitous Language (`docs/glossary.md`) 공유 — 모든 agent / ADR / Change Plan / Story file 안 어휘 SSOT 동일.
- 7 plugin 사이 통신 = **Shared Kernel** 패턴 (inter-plugin contracts: review-verdict-v4 / fix-event-v1 / label-registry-v2 등). 양쪽 동시 합의 의무 (ADR-008 versioning + ADR-010 sibling sync).
- codeforge governance BC 의 도메인 = **Story 단위 governance decision-making** (Architect lane 의 chief author 통합 + deputy advocacy synthesis + FIX root-cause 판정).

**Subdomain 분류 (codeforge governance BC 안)**:
- **Core**: ArchitectLane decision-making (chief author 통합 + deputy advocacy synthesis) — `codeforge-design` plugin 핵심.
- **Supporting**: lane evidence tracking (Story §14) + retro automation (PMOAgent) + FIX Ledger 관리.
- **Generic**: GitHub MCP API integration + git worktree management + label/milestone CRUD.

## mctrader 의 application BC (downstream Epic 영역)

**별 BC** — codeforge governance BC 와 분리. mctrader application BC 는 **downstream Epic 영역** (별 CFP 의무, 본 entry = pointer only).

mctrader BC 의 특성 (참조용, 본 codeforge SSOT 영역 외):
- domain = 거래소 trade execution + 시장 데이터 관리
- Ubiquitous Language SSOT = `mctrader-hub/docs/glossary.md` (별 SSOT)
- Aggregate = DDD Aggregate root in domain model (Order / Position / MarketSnapshot 등)
- 4-Layer Architecture (mctrader ADR-031 line 499-524) — 본 codeforge governance BC 의 4-Layer entry 가 cross-ref

**Published Language 분리 의무**: 본 codeforge BC entry 안 mctrader application detail 박제 금지. link only (ADR-091 §결정 4).

## Module ↔ Bounded Context 관계 (ADR-091 §결정 5)

ADR-091 §결정 5 = **15 agent frontmatter 의무 field 2종**:

```yaml
bounded_context: codeforge-governance  # governance BC | application BC (downstream) | shared-kernel | ...
ddd_pattern: Authority Pair | Domain Service | Subdomain Specialist  # §결정 1 enum
```

- `bounded_context` = 어느 BC 안에서 작동하는지 explicit declare
- `ddd_pattern` = 어느 DDD role enum 인지 explicit declare

S2 LAND 시 15 agent 전수 field 채워짐 (null 금지). lint script `scripts/check-ddd-pattern-frontmatter.sh` (warning tier, S3 신설) 가 cross-validate.

**Module ↔ BC 관계**:
- codeforge family 7 plugin = high-cohesion **Module** (DDD module sense) — 각 plugin 이 자체 디렉토리 + agent set + skill + workflow.
- 7 plugin 전체 = **단일 BC** (codeforge governance BC) — 단일 Ubiquitous Language + 단일 Aggregate definition + 단일 Subdomain 분류.

**중요**: 1 plugin ≠ 1 BC. plugin 은 module 수준 분류 (DDD Module pattern), BC 는 도메인 일관성 경계 (DDD Strategic Design). codeforge family 전체가 단일 BC 인 이유 = 모든 plugin 이 동일 Ubiquitous Language `docs/glossary.md` (wrapper SSOT) 정합 의무.

## Published Language 분리 (ADR-091 §결정 4)

BC 사이 통신 = **Published Language** 의무. content duplication 금지 — link only.

| BC | Published Language SSOT |
|---|---|
| codeforge governance BC | [`plugin-codeforge/docs/glossary.md`](../../glossary.md) (본 ADR-091 Story-1 신규) |
| mctrader application BC | `mctrader-hub/docs/glossary.md` (downstream Epic, 별 CFP) |

양 glossary 가 cross-reference (link only). 동음이의 (Aggregate / Module / Repository 등) 의 의미 충돌 차단.

**Content duplication 금지 근거** (ADR-013 정합): codeforge family 가 자신 사용 ≠ 외부 discipline 채택 = self-application 위반 0. mctrader 의 application detail 을 codeforge governance SSOT 안 박제 = governance BC ↔ application BC 동음이의 충돌 + ADR-013 dogfood-out policy 위반.

## 적용 사례: AggregateArchitectAgent 의 "RDB OLTP aggregate invariant"

AggregateArchitectAgent 의 mandate = **consumer aggregate boundary 설계 advocacy** (application BC 안 design task 영역).

**중요 사례**: AggregateArchitectAgent 가 codeforge governance BC 안 agent 이지만, 그 mandate (RDB OLTP aggregate invariant / 트랜잭션 경계) 는 **application BC reference** 이다. codeforge governance BC 의 agent 가 application BC 의 design decision 영역에서 specialized judgment contributor 로 작동.

**Authority Pair (ArchitectPL + ArchitectAgent)** 가 final author authority — AggregateArchitectAgent 는 specialized advocacy 만 contribute. 본 BC boundary = "agent 가 어느 BC 안에서 작동하는가" (codeforge governance BC) ≠ "agent mandate 의 적용 대상 BC" (consumer application BC) — 2 distinct dimension.

## Cross-reference

- [ADR-091 §결정 3](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Aggregate metaphor 2-layer explicit separate
- [ADR-091 §결정 4](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Published Language 분리 (codeforge + mctrader 2 SSOT)
- [ADR-091 §결정 5](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Bounded Context governance + 15 agent frontmatter field 의무
- [`docs/glossary.md`](../../glossary.md) — Bounded Context entry SSOT (line 77-82)
- [`docs/domain-knowledge/concept/aggregate.md`](aggregate.md) — Aggregate 2-layer separate sibling
- [`docs/domain-knowledge/concept/ubiquitous-language.md`](ubiquitous-language.md) — BC 내부 어휘 SSOT sibling
- [`docs/domain-knowledge/concept/4-layer-architecture.md`](4-layer-architecture.md) — mctrader ADR-031 4-Layer 모델 cross-ref
