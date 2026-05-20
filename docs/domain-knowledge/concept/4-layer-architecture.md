---
kind: concept_definition
type: domain-knowledge
slug: 4-layer-architecture
title: 4-Layer Architecture — Hexagonal/Onion 의 codeforge/mctrader 변형, OHS + ACL 동시 보유 사례
status: Active
updated: 2026-05-20
carrier_story: CFP-1117-S1
related_adrs:
  - ADR-091  # ArchitectLane DDD vocabulary governance — 본 개념의 normative SSOT (§결정 4 / §결정 7 evidence 영역 5)
related_files:
  - docs/glossary.md  # 4-Layer Architecture entry SSOT (line 299-312)
  - mctrader-hub/docs/adr/ADR-031  # mctrader 4-Layer 원본 SSOT (line 499-524, downstream Epic 영역)
  - docs/domain-knowledge/concept/bounded-context.md  # BC sibling (Published Language 분리)
tags:
  - 4-layer
  - architecture-style
  - hexagonal
  - onion
  - acl
  - ohs
  - mctrader-cross-ref
---

# 4-Layer Architecture

## 정의

`4-Layer Architecture` = **Hexagonal / Onion architecture 의 codeforge/mctrader 적용 변형**. mctrader application BC 의 ADR-031 (line 499-524) 의 verbatim 인용 — Foundation (Layer 0) + Adapter (Layer 1) + Data Storage (Layer 2) + Pure Consumer (Layer 2') 4 layer 분리. data-free + exchange-agnostic pure consumer 구조.

**핵심 특성**:
- dependency rule = **inner layer 가 outer layer 비의존** (Hexagonal / Onion 정합)
- **OHS (Open Host Service) + ACL (Anti-Corruption Layer) 동시 보유** 사례 (보기 드문 패턴)
- 순환 의존 0 (Layer 0 → 누구도 비의존, Layer 2 → 0 + 1 의존, Layer 2' → 0 + REST 의존)
- SSOT = [`docs/glossary.md` 4-Layer Architecture entry](../../glossary.md#4-layer-architecture-mctrader-적용)

## 컨텍스트

### codeforge 도입 동인

codeforge governance BC ↔ mctrader application BC 의 cross-repo Story 진행 중, mctrader 의 4-Layer 모델 (ADR-031 line 499-524) 이 codeforge governance BC 의 ArchitectLane 산출물 검증 시 worked example 로 인용 누적. 양 BC 가 같은 4-Layer 패턴 답습하면서도 **도메인 영역 disjoint** — codeforge governance BC = process-oriented (agent orchestration), mctrader application BC = data-oriented (시장 데이터 + 거래 execution).

mctrader 의 4-Layer 모델이 **OHS (Open Host Service) + ACL (Anti-Corruption Layer) 동시 보유** 보기 드문 사례 — Layer 1 = ACL pattern, Layer 2 = OHS pattern. codeforge governance BC 의 inter-plugin contract 영역 + ACL 영역 (`mcp__github__*` tool layer) 과 직접 대응 가능.

### 적용 trigger

- ArchitectLane 산출물 (Change Plan + ADR draft) 에서 architectural style 결정 시
- ModuleArchitectAgent (deputy) 의 module boundary advocacy 시 (Layered / Hexagonal / Clean / Onion 4 style enum)
- mctrader cross-repo Story 진행 시 worked example reference
- ADR-091 §결정 7 INV-5 영역 5 (ADR acceptance criteria 변경 evidence) 의 4-Layer 모델 cross-ref

### 관련 사건 (mctrader ADR-031 의 OHS + ACL 동시 보유 사례)

mctrader ADR-031 line 499-524 의 4-Layer 모델 (verbatim, 본 entry §"mctrader ADR-031 4-Layer 모델 verbatim 인용" 단락 참조) 이 BC 사이 통신 패턴 (ACL: 외부 BC → 자기 BC translation / OHS: 자기 BC → multiple consumer publishing) 2 종을 단일 architectural style 에 동시 보유. codeforge governance BC 안 동일 패턴 시연:
- ACL = `mcp__github__*` tool layer (GitHub REST API model → codeforge governance BC model)
- OHS = codeforge inter-plugin contracts (review-verdict-v4 / fix-event-v1 등 — codeforge family 7 plugin 동시 consume)

## 핵심 규칙

### R-1: 4 Layer 분리 의무 (mctrader ADR-031 verbatim, codeforge cross-ref)

본 4-Layer 의 원본 정의 = **mctrader application BC 의 ADR-031** (line 499-524, downstream Epic 영역). codeforge governance BC 안 본 entry = pointer + verbatim cite only (ADR-091 §결정 4 Published Language 분리 정합).

**verbatim 인용** (mctrader ADR-031 line 499-524):

```
Layer 0 ─ mctrader-market (FOUNDATION, 의존 0, 순수 pydantic/sqlalchemy, data 비의존)
Layer 1 ─ 거래소 어댑터 (각각 → market 만, market Protocol 구현) [ACL pattern]
Layer 2 ─ mctrader-data (DATA-STORAGE 영역 단독 소유, → market + → 어댑터들) [OHS pattern, /v1 API endpoint]
Layer 2'─ mctrader-engine (PURE CONSUMER, mctrader_data=0, mctrader_market_*=0)
```

**순환 의존 분석** (mctrader ADR-031 verbatim):
- 영원히 없음
- Layer 0 (market) → 누구도 의존 안 함
- Layer 1 (어댑터) → market 만 의존
- Layer 2 (data) → market + 어댑터 의존
- Layer 2' (engine) → market + REST API 의존 (REST = OHS interface, direct module import 0)

### R-2: Layer 별 책임 + DDD pattern 매핑

#### Layer 0 — Foundation (mctrader-market)

- **역할**: 순수 도메인 model (pydantic / sqlalchemy schema). data 비의존, 외부 의존 0.
- **DDD pattern 매핑**: Domain Layer (Layered Architecture 의 가장 안쪽) — Entity + Value Object + Domain Service definition.
- **codeforge governance BC 유사 사례**: `docs/inter-plugin-contracts/` registry (pure schema definition, 외부 의존 0).

#### Layer 1 — Adapter (거래소 어댑터, ACL pattern)

- **역할**: 각 거래소 (Bithumb / Binance / 별 거래소) 의 REST API + websocket 을 market Protocol 으로 normalize. data ↔ exchange transform.
- **DDD pattern 매핑**: **Anti-Corruption Layer (ACL)** — 외부 BC (거래소 API model) 가 자기 BC (mctrader market domain model) 오염 차단. translator + adapter + facade 조합.
- **codeforge governance BC 유사 사례**: `mcp__github__*` tool layer = ACL (GitHub REST API model → codeforge governance BC model). GitHub API 의 raw response 가 codeforge 의 Story / Issue / PR model 로 normalize.

#### Layer 2 — Data Storage (mctrader-data, OHS pattern)

- **역할**: 데이터 영속 영역 단독 소유. /v1 REST API endpoint 제공 (Arrow IPC 표준 — multiple consumer 동시 access 지원).
- **DDD pattern 매핑**: **Open Host Service (OHS)** — multiple BC consumer 에게 well-documented protocol 으로 서비스 제공. conformist 보다 multiple consumer 동시 지원.
- **codeforge governance BC 유사 사례**: codeforge inter-plugin contracts (review-verdict-v4 / fix-event-v1 등) = OHS (codeforge family 7 plugin 동시 consume).

#### Layer 2' — Pure Consumer (mctrader-engine)

- **역할**: data + market `_*` 모듈 import 0 — REST API endpoint 만 access. exchange-agnostic 으로 pure consumer 역할.
- **DDD pattern 매핑**: Application Service layer — use case orchestration + transaction 경계 + domain logic 호출. domain logic 자체는 Layer 0 안 Domain Service 에 위임.
- **codeforge governance BC 유사 사례**: Orchestrator (top-level Claude session) = Application Service (use case orchestration + Story-scoped transaction 경계).

### R-3: dependency direction (안쪽 = 도메인 / 바깥 = 인프라)

DDD Hexagonal / Onion / Clean Architecture 의 핵심 dependency rule = **inner layer 가 outer layer 비의존**:

```
Layer 0 (Foundation, 가장 안쪽) ← domain 가장 순수
   ↑
Layer 1 (Adapter, ACL)
   ↑
Layer 2 (Data Storage, OHS) + Layer 2' (Pure Consumer)  ← infrastructure 가장 바깥
```

- Layer 0 = 안쪽 (domain 가장 순수, 외부 의존 0)
- Layer 2 / Layer 2' = 바깥 (infrastructure / use case orchestration)
- arrow direction = 의존 방향 (outer → inner) — Layer 2' 가 Layer 0 의존, 역방향 0

**framework / 외부 시스템 비의존 invariant**: Layer 0 (domain core) 가 framework / 외부 시스템 비의존 — Hexagonal Architecture 의 dependency inversion principle 정합.

### R-4: Layer 별 Aggregate 위치 (Layer 2 안 Aggregate Root)

**핵심 invariant**: mctrader application BC 의 Aggregate Root 는 **Layer 0 (Foundation, mctrader-market)** 안 domain model 로 정의 + **Layer 2 (Data Storage, mctrader-data)** 안 persistence layer 로 영속. transaction atomic boundary = Layer 2 의 Repository per Aggregate.

| Layer | Aggregate 관계 |
|---|---|
| Layer 0 (Foundation) | Aggregate **definition** (domain model) — Entity + Value Object + Domain Service + Aggregate Root identity definition |
| Layer 1 (Adapter / ACL) | Aggregate **외부 → domain transform** — 거래소 raw data 가 Aggregate Root (Order / MarketSnapshot 등) 로 normalize |
| Layer 2 (Data Storage / OHS) | Aggregate **persistence + 외부 export** — Repository per Aggregate + /v1 REST API 가 Aggregate Root 단위 read/write endpoint 노출 |
| Layer 2' (Pure Consumer) | Aggregate **read-only consume** — REST API 경유 Aggregate Root read 만 (write 0, eventually consistent) |

**중요**: 본 Aggregate 위치는 **mctrader application BC** 의 application detail. codeforge governance BC 안 본 entry = pointer + verbatim cite only (ADR-091 §결정 4 Published Language 분리). 실 Aggregate Root 분류 + invariant 정의 = downstream Epic (별 CFP, 본 codeforge SSOT 영역 외).

### R-5: Layered / Hexagonal / Clean / Onion 비교

DDD architectural style 의 4 variant 비교 (glossary entry cross-ref):

| Style | 핵심 원칙 | layer 수 | dependency rule | codeforge 사례 |
|---|---|---|---|---|
| [`Layered Architecture`](../../glossary.md#layered-architecture) | Presentation / Application / Domain / Infrastructure 4 layer | 4 | 상위 → 하위 의존 (역방향 금지) | ModuleArchitectAgent 책임 영역 (traditional default) |
| [`Hexagonal Architecture`](../../glossary.md#hexagonal-architecture-ports--adapters) | Ports & Adapters — domain core 가 port 정의, adapter 가 외부 connect | 가변 (domain core + N adapter) | inner (domain) ← outer (adapter) | codeforge governance BC 부분 적용 (agent = domain core, Orchestrator = adapter) |
| [`Clean Architecture`](../../glossary.md#clean-architecture) | Entities / Use Cases / Interface Adapters / Frameworks & Drivers 4 ring | 4 | inner ring ← outer ring | ModuleArchitectAgent 책임 영역 (Robert C. Martin 통합 model) |
| [`Onion Architecture`](../../glossary.md#onion-architecture) | 동심원 layer (Domain Model → Domain Services → Application Services → Infrastructure) | 4 | inner ← outer | ModuleArchitectAgent 책임 영역 (Jeffrey Palermo variant) |
| **4-Layer Architecture** (본 entry) | Foundation + Adapter (ACL) + Data Storage (OHS) + Pure Consumer | 4 (Layer 0 / 1 / 2 / 2') | inner ← outer (순환 0) | mctrader application BC ADR-031 (codeforge governance BC 유사 variant) |

**4-Layer 특수성** (Hexagonal / Onion 변형 대비):
- OHS + ACL 동시 보유 사례 (보기 드문 패턴) — Layer 1 = ACL, Layer 2 = OHS
- Layer 2' (Pure Consumer) = data + market `_*` 모듈 import 0 invariant (exchange-agnostic)
- 순환 의존 0 invariant 명시 (Layer 0 → 누구도 비의존)

## 경계

### 영역 안 (codeforge governance BC SSOT scope)

- 4-Layer 패턴 의 codeforge governance BC 적용 사례 (inter-plugin contract = Layer 0 / `mcp__github__*` = Layer 1 ACL / lane plugin = Layer 2 OHS / Orchestrator = Layer 2' Pure Consumer)
- mctrader ADR-031 line 499-524 의 verbatim 인용 (pointer + cross-ref)
- OHS / ACL 동시 보유 사례 의 pattern reference
- ADR-091 §결정 7 INV-5 영역 5 anchor (ADR acceptance criteria 변경 evidence)
- ModuleArchitectAgent 의 architectural style enum 안 4-Layer variant 포함

### 영역 외 (mctrader application BC application detail)

- mctrader 의 실 Aggregate Root 분류 (Order / Position / MarketSnapshot 등 domain model definition)
- mctrader 의 Repository per Aggregate 구현 detail
- 거래소 (Bithumb / Binance) adapter 구현 detail + Arrow IPC 표준 적용 사례
- mctrader 의 Layer 2 /v1 REST API endpoint 구현 detail

### Published Language 경계 (codeforge governance BC ↔ mctrader application BC)

본 entry 의 4-Layer 적용 detail (Aggregate Root 분류 + Repository pattern + 실 Bithumb / Binance adapter 구현 + Arrow IPC 표준 적용 사례) = **mctrader downstream Epic 영역** (별 CFP). 본 codeforge governance BC SSOT 안 application detail 명시 금지 (ADR-091 §결정 4 Published Language 분리 정합).

본 entry 의 codeforge governance BC scope = **pattern 의 cross-reference SSOT** (mctrader 적용 사례를 codeforge governance BC discipline 의 worked example 로 인용). golden-path worked example file (`examples/ddd-golden-path-mct031.md`, ADR-091 Story-6 신설 예정) 가 본 entry 의 mctrader cross-ref 를 evidence enumeration 5 영역 (ADR-091 §결정 7 INV-5 영역 5) 안에서 명문화한다.

### codeforge 적용 사례 (governance Layer 분류)

codeforge governance BC 의 4-Layer 유사 구조 (variant — mctrader application BC 4-Layer 와 보기 패턴 동형이지만 도메인 영역 disjoint):

| codeforge Layer | 역할 | mctrader Layer mapping |
|---|---|---|
| **Layer 0 — inter-plugin contracts registry** | pure schema definition (review-verdict-v4 / fix-event-v1 / label-registry-v2 / debate-protocol-v1 / git-ops-event-v1 등 6 contract + 6 registry) | Layer 0 (Foundation) |
| **Layer 1 — codeforge wrapper plugin = ACL** | GitHub API / git CLI / codex CLI / mcp__github__* tool → codeforge governance BC model normalize | Layer 1 (Adapter / ACL) |
| **Layer 2 — lane plugin 6 (requirements / design / develop / review / test / pmo) = OHS** | review-verdict-v4 / inter-plugin contract endpoint 제공 — codeforge family 7 plugin 동시 consume | Layer 2 (Data Storage / OHS) |
| **Layer 2' — Orchestrator (top-level Claude session) = Pure Consumer** | lane plugin Published Language 만 access (lane plugin internal direct 호출 0 — inter-plugin contract registry 경유) | Layer 2' (Pure Consumer) |

**중요 boundary**: codeforge governance BC = **process-oriented BC** (agent orchestration + lane spawn + FIX Ledger). mctrader application BC = **data-oriented BC** (시장 데이터 + 거래 execution + persistence). 양 BC 가 4-Layer 패턴 답습하지만 도메인 영역 disjoint — pattern reuse ≠ BC merge (ADR-091 §결정 4 Published Language 분리 invariant 보존).

**codeforge governance Layer 2 — Published Language interface**:
- codeforge wrapper plugin = governance Layer 2 (decision boundary supplier)
- lane plugin = governance Layer 2' (Published Language interface — inter-plugin contract 경유 통신)
- consumer projects = governance Layer 2' beyond (overlay 만, 직접 lane plugin 호출 0)

## 관련 ADR

- [ADR-091 §결정 4](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Published Language 분리 (codeforge + mctrader 2 SSOT)
- [ADR-091 §결정 7 영역 5](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — ADR acceptance criteria 변경 evidence (4-Layer 모델 cross-ref)
- [`docs/glossary.md` 4-Layer Architecture entry](../../glossary.md#4-layer-architecture-mctrader-적용) — SSOT (line 299-312)
- [`docs/glossary.md` Anti-Corruption Layer (ACL)](../../glossary.md#anti-corruption-layer-acl) — Layer 1 패턴 SSOT
- [`docs/glossary.md` Open Host Service (OHS)](../../glossary.md#open-host-service-ohs) — Layer 2 패턴 SSOT
- [`docs/glossary.md` Layered / Hexagonal / Clean / Onion Architecture](../../glossary.md#layered-architecture) — sibling architectural style
- `mctrader-hub/docs/adr/ADR-031.md` — mctrader 4-Layer 원본 SSOT (line 499-524, downstream Epic 영역)
- [`docs/domain-knowledge/concept/bounded-context.md`](bounded-context.md) — BC sibling (Published Language 분리 invariant)

## ADR-091 §결정 7 evidence enumeration 영역 5 정합

본 4-Layer entry = **ADR-091 §결정 7 INV-5 evidence enumeration 영역 5 anchor**:

> 5. **ADR acceptance criteria 변경 evidence** — 본 ADR-091 § 결정 N + golden-path before/after diff 가 mctrader ADR-031 의 4-Layer 모델 (line 499-524) 위에 OHS (Layer 2 data /v1 REST API endpoint) + ACL (Layer 1 거래소 어댑터 → market Protocol 구현) 시연

본 entry 의 verbatim cite + OHS / ACL 동시 보유 사례 인용이 영역 5 의 mechanical anchor.

## 변경 이력

- 2026-05-20 KST — CFP-1117 Story-1 carrier 신규 작성 (ArchitectAgent direct write per ADR-070). forbid-list 어휘 wording sweep 동반 (5 occurrence → `verbatim 인용` / `명시 금지` / `명문화` / `cite` 로 정정 — ADR-064 Amendment 5 / wording-dictionary 카테고리 (a) 정합).
