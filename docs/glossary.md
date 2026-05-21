# codeforge governance BC — Ubiquitous Language SSOT (DDD glossary)

> **본 file = codeforge governance Bounded Context (BC) 의 Published Language SSOT** — DDD term 의 한국어/영어 병기 + definition + plugin-codeforge 적용 사례 명시. ADR-091 carrier story = CFP-1117-S1.
>
> **Published Language 분리** (ADR-091 §결정 4): codeforge governance BC ↔ mctrader application BC 의 동음이의 (Aggregate / Module / Repository 등) 충돌 차단. mctrader 측 SSOT = `mctrader-hub/docs/glossary.md` (downstream Epic, 별 CFP).
>
> **Status**: Active (2026-05-20 KST) — CFP-1117 Story-1 carrier. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합.

## 목차 (50+ term)

### Strategic Design (전략적 설계)
- [Bounded Context (BC)](#bounded-context-bc)
- [Subdomain (Core / Supporting / Generic)](#subdomain-core--supporting--generic)
- [Core Domain](#core-domain)
- [Supporting Subdomain](#supporting-subdomain)
- [Generic Subdomain](#generic-subdomain)
- [Ubiquitous Language](#ubiquitous-language)
- [Published Language](#published-language)
- [Context Map](#context-map)
- [Shared Kernel](#shared-kernel)
- [Customer-Supplier](#customer-supplier)
- [Conformist](#conformist)
- [Anti-Corruption Layer (ACL)](#anti-corruption-layer-acl)
- [Open Host Service (OHS)](#open-host-service-ohs)
- [Partnership](#partnership)
- [Separate Ways](#separate-ways)
- [Big Ball of Mud](#big-ball-of-mud)
- [Strategic Design (overview)](#strategic-design-overview)

### Tactical Design (전술적 설계)
- [Aggregate (governance BC)](#aggregate-governance-bc)
- [Aggregate (mctrader application BC)](#aggregate-mctrader-application-bc)
- [Aggregate Root](#aggregate-root)
- [Entity](#entity)
- [Value Object](#value-object)
- [Domain Service](#domain-service)
- [Domain Event](#domain-event)
- [Application Service](#application-service)
- [Infrastructure](#infrastructure)
- [Repository (DDD)](#repository-ddd)
- [Factory (DDD)](#factory-ddd)
- [Specification](#specification)
- [Module (DDD sense)](#module-ddd-sense)
- [Tactical Design (overview)](#tactical-design-overview)

### Architecture Style
- [Layered Architecture](#layered-architecture)
- [Hexagonal Architecture (Ports & Adapters)](#hexagonal-architecture-ports--adapters)
- [Clean Architecture](#clean-architecture)
- [Onion Architecture](#onion-architecture)
- [4-Layer Architecture (mctrader 적용)](#4-layer-architecture-mctrader-적용)
- [CQRS](#cqrs)
- [Event Sourcing](#event-sourcing)

### codeforge governance BC 의 Authority / Specialist Pattern (ADR-091 §결정 1)
- [Authority Pair](#authority-pair)
- [Aggregate Root (governance metaphor)](#aggregate-root-governance-metaphor)
- [Domain Service (governance contributor)](#domain-service-governance-contributor)
- [Subdomain Specialist](#subdomain-specialist)
- ["Which subdomain under threat" (deputy spawn rationale)](#which-subdomain-under-threat-deputy-spawn-rationale)

### Anti-pattern (Forbid-list 후보, OQ-1 결정 영역)
- [Big Ball of Mud (design intent forbid)](#big-ball-of-mud-design-intent-forbid)
- [Smart UI (anti-pattern)](#smart-ui-anti-pattern)
- [Anemic Domain Model](#anemic-domain-model)
- [Vocabulary Theater (codeforge 자체 anti-pattern)](#vocabulary-theater-codeforge-자체-anti-pattern)

### Cross-cutting / Process
- [Strategic Design Workshop](#strategic-design-workshop)
- [Event Storming](#event-storming)
- [Domain Story Telling](#domain-story-telling)

---

## Strategic Design (전략적 설계)

### Bounded Context (BC)

**영어**: Bounded Context  
**한국어**: 한정된 컨텍스트 / 경계 컨텍스트 (영어 표기 권장 — 한국어 번역 비표준)  
**정의**: 도메인 모델이 일관성 있게 적용되는 명시적 경계. 같은 용어가 다른 BC 에서 다른 의미를 가질 수 있다. BC 사이 통신은 explicit (Context Map + Published Language).  
**plugin-codeforge 적용 사례**: 본 plugin = **codeforge governance BC** (Aggregate = supervised authority cluster). mctrader application = **별 BC** (Aggregate = DDD Aggregate root in domain model). Published Language 분리 (본 glossary SSOT + mctrader `docs/glossary.md` SSOT, ADR-091 §결정 4).

### Subdomain (Core / Supporting / Generic)

**영어**: Subdomain  
**정의**: 비즈니스 도메인의 하위 영역 분류. Core (경쟁 우위) / Supporting (지원 / 차별점 없음) / Generic (일반 / 외부 솔루션 우선).  
**plugin-codeforge 적용 사례**: codeforge governance BC 자체 = (a) **Core**: ArchitectLane decision-making (chief author 통합 + deputy advocacy synthesis) (b) **Supporting**: lane evidence tracking + retro automation (c) **Generic**: GitHub API integration + worktree management. Subdomain 분류 SSOT 는 본 ADR-091 = 분류 기준만 (downstream Epic 가 repo-by-repo 실 분류).

### Core Domain

**영어**: Core Domain  
**정의**: Subdomain 분류 중 비즈니스 경쟁 우위를 결정하는 핵심 영역. 최고 인재 / 정교한 모델 / 가장 많은 투자 의무.  
**plugin-codeforge 적용 사례**: ArchitectLane (codeforge-design plugin) 의 decision-making mechanism = codeforge governance BC 의 Core Domain. 본 ADR-091 의 vocabulary governance 가 Core Domain 의 discipline mechanism 부착.

### Supporting Subdomain

**영어**: Supporting Subdomain  
**정의**: Core Domain 지원이지만 자체 경쟁 우위 무. 내부 개발 또는 외부 도구 활용.  
**plugin-codeforge 적용 사례**: lane evidence tracking (Story §14 Lane Evidence) + retro automation (PMOAgent) + FIX Ledger 관리. 차별점 없음 but Core Domain 의 운영 의무.

### Generic Subdomain

**영어**: Generic Subdomain  
**정의**: 비즈니스 차별점 없음. 외부 솔루션 / 표준 라이브러리 / SaaS 우선.  
**plugin-codeforge 적용 사례**: GitHub MCP API integration (`mcp__github__*`), git worktree management (ADR-040), label/milestone CRUD. 표준 도구 그대로 사용 — 자체 customization 0건 원칙.

### Ubiquitous Language

**영어**: Ubiquitous Language  
**한국어**: 보편 언어 / 공용 언어 (영어 표기 권장)  
**정의**: 도메인 전문가 + 개발자가 공유하는 정밀 어휘. 코드 + 문서 + 회의에서 동일 용어 사용. BC 내부 limited (BC 사이는 Published Language).  
**plugin-codeforge 적용 사례**: 본 glossary.md = codeforge governance BC 의 Ubiquitous Language SSOT. agent file 본문 + ADR + Change Plan + Story file 안 모든 DDD 어휘는 본 glossary 정의 verbatim 인용 의무. drift 차단 = `scripts/check-ubiquitous-language.sh` (ADR-091 §결정 6 lint, S3 #1120 Wave 2 mechanical wire — 구 명칭 check-ddd-vocabulary.sh 가 evidence-checks-registry entry name `ubiquitous-language-drift-check` 정합 위해 check-ubiquitous-language.sh 로 확정).

### Published Language

**영어**: Published Language  
**정의**: BC 사이 통신 시 사용되는 well-documented shared language. 양 BC 가 별도 internal Ubiquitous Language 가지지만 외부 통신 시 Published Language 경유.  
**plugin-codeforge 적용 사례**: codeforge governance BC ↔ mctrader application BC 통신 시 Published Language = (a) codeforge inter-plugin contracts (review-verdict-v4 / fix-event-v1 등) (b) Story file structure (frontmatter + §1-§14 sections) (c) 본 glossary.md ↔ `mctrader-hub/docs/glossary.md` cross-reference link. **content duplication 금지** — link only (ADR-091 §결정 4).

### Context Map

**영어**: Context Map  
**정의**: Bounded Context 간 관계 + 통신 패턴 시각화. Shared Kernel / Customer-Supplier / Conformist / ACL / OHS 등 패턴 명시.  
**plugin-codeforge 적용 사례**: codeforge governance BC ↔ mctrader application BC = Published Language (codeforge → mctrader: review-verdict + fix-event-v1 / mctrader → codeforge: Story-key cross-ref). codeforge family 7 plugin 사이 = Shared Kernel (inter-plugin contracts).

### Shared Kernel

**영어**: Shared Kernel  
**정의**: 2+ BC 가 명시 동의 후 일부 도메인 모델 공유. 변경 시 양쪽 동시 합의 의무. 자주 사용 시 BC 분리 의미 약화 — 신중 채택.  
**plugin-codeforge 적용 사례**: codeforge family 7 plugin (wrapper + 6 lane) 의 inter-plugin contracts = Shared Kernel (review-verdict-v4 / fix-event-v1 / label-registry-v2 등). ADR-008 versioning + ADR-010 sibling sync 가 governance.

### Customer-Supplier

**영어**: Customer-Supplier  
**정의**: 2 BC 가 upstream/downstream 관계. Supplier (upstream) 가 Customer (downstream) 요구 우선 수용 의무. 양쪽 모두 변경 가능.  
**plugin-codeforge 적용 사례**: codeforge wrapper (Supplier) ↔ consumer projects (Customer). consumer 가 overlay (`.claude/_overlay/`) 로 customization 가능, wrapper 가 consumer 요구를 ratchet 강화 방향만 수용 (ADR-064 §결정 1 정합).

### Conformist

**영어**: Conformist  
**정의**: Downstream BC 가 Upstream BC 모델을 그대로 따름. 변경 권한 없음. translation layer 부재.  
**plugin-codeforge 적용 사례**: consumer projects 가 codeforge upstream ADR 을 conformist 로 채택 — consumer 변경 권한 없음, overlay 로 확장만 가능 (축소 0).

### Anti-Corruption Layer (ACL)

**영어**: Anti-Corruption Layer  
**한국어**: 부패 방지 계층 / 손상 방지 계층 (영어 약자 ACL 권장)  
**정의**: BC 사이 통신 시 외부 BC 의 model 이 자기 BC 의 domain model 을 오염시키지 않도록 translation layer 배치. translator + adapter + facade 조합.  
**plugin-codeforge 적용 사례**: codeforge 가 GitHub API 호출 시 `mcp__github__*` tool layer = ACL (GitHub REST API model → codeforge governance BC model). 사례 ②: **mctrader ADR-031 4-Layer 모델의 Layer 1 거래소 어댑터** (line 508-509) = ACL — 거래소별 model 을 market Protocol 구현으로 normalize (단, 본 사례 는 application BC 안 BC 사이 ACL 패턴 시연으로 codeforge governance BC 외부 사례).

### Open Host Service (OHS)

**영어**: Open Host Service  
**정의**: BC 가 외부 BC 들에게 well-documented protocol 으로 서비스 제공. RESTful API / publish-subscribe event / gRPC endpoint 등. **conformist 보다 multiple consumer 동시 지원**.  
**plugin-codeforge 적용 사례**: codeforge inter-plugin contracts (review-verdict-v4 / fix-event-v1 등) = OHS (codeforge family 7 plugin 동시 consume). 사례 ②: **mctrader ADR-031 4-Layer 모델의 Layer 2 mctrader-data /v1 REST API** (line 514) = OHS — engine / 별 consumer 동시 access 지원 (Arrow IPC 표준).

### Partnership

**영어**: Partnership  
**정의**: 2 BC 가 mutual dependency. 한 쪽 실패 시 양쪽 실패. 강한 결합 — 명시 SLA / 협력 mechanism 의무.  
**plugin-codeforge 적용 사례**: codeforge-review ↔ codeforge-design (review-verdict feedback loop). 양쪽 동시 LAND 의무 — 한 쪽 미LAND 시 양쪽 release 차단.

### Separate Ways

**영어**: Separate Ways  
**정의**: 2 BC 가 integration 안 함. 각자 독립 implementation. integration 비용 > 가치 일 때 채택.  
**plugin-codeforge 적용 사례**: codeforge governance BC ↔ consumer project domain BC (대부분 사례). Separate Ways 가 default. 단 review-verdict / fix-event 등 inter-plugin contract 영역만 Customer-Supplier.

### Big Ball of Mud

**영어**: Big Ball of Mud  
**정의**: BC 부재 + Ubiquitous Language drift + Tangled dependencies. 도메인 모델 부재.  
**plugin-codeforge 적용 사례**: **anti-pattern 어휘** — design intent 로 채택 표현 금지 (ADR-064 forbid-list 확장 후보, OQ-1). 실 description (after-the-fact analysis) 시 사용 가능, design plan 시 사용 금지.

### Strategic Design (overview)

**영어**: Strategic Design  
**정의**: BC 식별 + Subdomain 분류 + Context Map + Ubiquitous Language + Published Language 종합. tactical design (Aggregate / Entity 등) 보다 우선 결정.  
**plugin-codeforge 적용 사례**: 본 ADR-091 = codeforge governance BC 의 Strategic Design 결정. 15 agent 의 BC + Subdomain + Ubiquitous Language SSOT 명시화.

---

## Tactical Design (전술적 설계)

### Aggregate (governance BC)

**영어**: Aggregate  
**정의 (codeforge governance BC, ADR-091 §결정 3 Layer A)**: **supervised authority cluster** — ArchitectPLAgent 가 6 deputy + chief author 산출물 통합하는 supervisor 의 metaphor only. Aggregate Root metaphor.  
**plugin-codeforge 적용 사례**: ArchitectPLAgent 가 Aggregate Root metaphor 보유 — single supervisor 가 multiple SubAgent 산출물의 consistency 책임. ArchitectPL == Aggregate Root metaphor (literal Aggregate 아님 — process participant ≠ domain object, Codex Q2 합의).

### Aggregate (mctrader application BC)

**영어**: Aggregate  
**정의 (mctrader application BC)**: DDD Aggregate root in domain model — 일관성 경계 안의 Entity + Value Object 집합. transactionally consistent.  
**plugin-codeforge 적용 사례**: N/A — 별 BC. **동음이의 충돌 차단**: codeforge governance BC 의 "Aggregate" (supervised authority cluster) ≠ mctrader application BC 의 "Aggregate" (DDD aggregate root). 본 glossary 가 2 distinct entry 로 explicit separate.

### Aggregate Root

**영어**: Aggregate Root  
**정의 (governance BC, ADR-091 §결정 3 Layer A)**: Authority Pair (ArchitectPL + Architect) 의 supervisor side metaphor. ArchitectPLAgent = supervised authority cluster 의 root.  
**plugin-codeforge 적용 사례**: ArchitectPLAgent. 정의 (application BC) = DDD Aggregate 의 외부 진입점 Entity. 본 glossary = codeforge governance BC SSOT 이므로 governance 정의 우선.

### Entity

**영어**: Entity  
**정의**: 고유 identity 보유 + lifecycle (생성 / 변경 / 삭제) + identity-equal (attribute-equal 아님). DDD tactical design 의 핵심 building block.  
**plugin-codeforge 적용 사례**: codeforge governance BC 의 Entity = Story (Story-key identity + phase lifecycle + identity-equal across PR/Issue/comment). Change Plan / ADR 도 Entity (file path identity + status lifecycle).

### Value Object

**영어**: Value Object  
**정의**: identity 없음 + attribute-equal + immutable. 변경 시 새 instance 생성. side effect 없음.  
**plugin-codeforge 적용 사례**: codeforge inter-plugin contract payload (review-verdict / fix-event) = Value Object (identity 없음 + immutable + attribute-equal). severity enum / phase enum / tier enum 도 Value Object.

### Domain Service

**영어**: Domain Service  
**정의 (DDD tactical)**: Entity / Value Object 에 자연스럽게 속하지 않는 도메인 로직. stateless. operation-centric (noun 아님).  
**정의 (codeforge governance BC, ADR-091 §결정 1)**: specialized judgment contributor — 7 permanent SubAgent + 3 sub-tuple 의 role.  
**plugin-codeforge 적용 사례**: SecurityArchitectAgent (위협 모델 contributor) / TestContractArchitectAgent (§8 Test Contract contributor) / AggregateArchitectAgent (RDB OLTP aggregate invariant contributor) 등. operation = "boundary advocacy" (noun 아님). stateless = re-spawn 시 context 재load.

### Domain Event

**영어**: Domain Event  
**정의**: 도메인 안에서 발생한 의미 있는 사실. 과거형 표기 (OrderPlaced / FixIterRecorded). 다른 BC 에 publish 가능.  
**plugin-codeforge 적용 사례**: fix-event-v1 contract (FixRowAppended / RootCauseDecided) / git-ops-event-v1 contract / stop-event-v1 (StopTimeReviewCompleted). 모든 event 가 inter-plugin contract registry 안 schema 명시.

### Application Service

**영어**: Application Service  
**정의**: use case orchestration layer. domain object 호출 + transaction 경계 + security. domain logic 0 (domain logic 은 Entity / Domain Service 안).  
**plugin-codeforge 적용 사례**: Orchestrator (top-level Claude session) = Application Service — use case orchestration (lane spawn + FIX Ledger append + retro automation) + transaction 경계 (Story-scoped branch + atomic PR sequence). domain logic = lane agent 의 specialized judgment 위임.

### Infrastructure

**영어**: Infrastructure  
**정의**: Persistence / external service integration / messaging / file I/O 등 기술 layer. domain layer 와 분리 의무 (Hexagonal Architecture port-adapter).  
**plugin-codeforge 적용 사례**: GitHub MCP API / codex CLI / `gh` CLI / git worktree / file system Read/Write/Edit. ACL (mcp__github__*) 가 Infrastructure ↔ Domain 격리.

### Repository (DDD)

**영어**: Repository  
**정의 (DDD)**: domain object collection abstraction. CRUD-like interface (save / findBy / delete) 제공, persistence 세부 hide. Aggregate 단위 access.  
**plugin-codeforge 적용 사례**: codeforge governance BC = **Repository 패턴 부재** (직접 file Read/Write 사용). Application BC (mctrader) 에서 DDD Repository 패턴 적용 — 별 SSOT.

### Factory (DDD)

**영어**: Factory  
**정의 (DDD)**: 복잡한 Aggregate / Entity 생성 책임. constructor 복잡 시 분리. Repository 와 분리.  
**plugin-codeforge 적용 사례**: PMOAgent 의 Epic 창설 / Story 분해 mechanism = Factory 패턴 (Story key 부여 + sub-Issue 생성 + label 부착 + scope_manifest 작성).

### Specification

**영어**: Specification  
**정의 (DDD pattern)**: domain rule predicate. `isSatisfiedBy()` interface. composable (AND/OR/NOT) — domain logic 분리.  
**plugin-codeforge 적용 사례**: review-verdict finding criteria = Specification 패턴 (severity Specification + boundary Specification + ratchet Specification composable). decision principle 의 forbid-list dictionary = Specification.

### Module (DDD sense)

**영어**: Module  
**정의 (DDD)**: 도메인 모델의 high-cohesion grouping. package / namespace / 디렉토리. **infrastructure module ≠ DDD module** (DDD module = domain-meaningful grouping).  
**plugin-codeforge 적용 사례**: codeforge family 7 plugin (wrapper + 6 lane) = high-cohesion module — 각 plugin 이 별 BC + Ubiquitous Language. ModuleArchitectAgent = module boundary specialist (CFP-1086 신설, layered / hexagonal / clean / DDD bounded context module-level).

### Tactical Design (overview)

**영어**: Tactical Design  
**정의**: Aggregate / Entity / Value Object / Domain Service / Domain Event / Repository / Factory / Specification 7 building block. Strategic Design (BC + Ubiquitous Language) 위에 implementation 명시.  
**plugin-codeforge 적용 사례**: codeforge governance BC 의 Tactical Design = 본 glossary 안 11 tactical term 그대로 채택. ADR-091 §결정 1 의 agent ↔ DDD pattern mapping 이 Tactical Design 의 codeforge governance 적용.

---

## Architecture Style

### Layered Architecture

**영어**: Layered Architecture  
**정의**: Presentation / Application / Domain / Infrastructure 4 layer. 상위 → 하위 의존 (역방향 금지). DDD Tactical Design 의 traditional default style.  
**plugin-codeforge 적용 사례**: ModuleArchitectAgent 의 책임 영역 — Layered / Hexagonal / Clean / Onion 4 style 가 module 결정 영역.

### Hexagonal Architecture (Ports & Adapters)

**영어**: Hexagonal Architecture / Ports & Adapters  
**정의**: domain core 가 ports (interface) 정의, adapter 가 외부 (DB / API / UI) 와 connect. domain core 가 framework / 외부 시스템 비의존. dependency inversion.  
**plugin-codeforge 적용 사례**: codeforge governance BC = Hexagonal pattern 부분 적용 — agent (domain core) 가 inter-plugin contract (port) 정의 + Orchestrator (adapter) 가 GitHub API / git / file system connect.

### Clean Architecture

**영어**: Clean Architecture  
**정의 (Robert C. Martin)**: Entities / Use Cases / Interface Adapters / Frameworks & Drivers 4 ring. dependency rule = inner ring 이 outer ring 비의존. Hexagonal + Onion 의 통합.  
**plugin-codeforge 적용 사례**: ModuleArchitectAgent 의 책임 영역 — Clean / Hexagonal / Onion / Layered 4 architectural style boundary decision.

### Onion Architecture

**영어**: Onion Architecture  
**정의 (Jeffrey Palermo)**: 동심원 layer (Domain Model → Domain Services → Application Services → Infrastructure). Hexagonal + Clean 의 변형. dependency rule 동일 (inner → outer 의존 금지).  
**plugin-codeforge 적용 사례**: ModuleArchitectAgent specialty area (Layered / Hexagonal / Clean / Onion 4 style enum).

### 4-Layer Architecture (mctrader 적용)

**영어**: 4-Layer Architecture  
**정의 (mctrader application BC 특수 사례)**: Foundation (Layer 0) / Adapter (Layer 1) / Data Storage (Layer 2) / Pure Consumer (Layer 2') — mctrader ADR-031 의 verbatim 인용. data-free + exchange-agnostic pure consumer 구조.  
**plugin-codeforge 적용 사례**: golden-path worked example 대상 (S6, `examples/ddd-golden-path-mct031.md`). mctrader ADR-031 line 499-524 verbatim 인용:

```
Layer 0 ─ mctrader-market (FOUNDATION, 의존 0, 순수 pydantic/sqlalchemy, data 비의존)
Layer 1 ─ 거래소 어댑터 (각각 → market 만, market Protocol 구현) [ACL pattern]
Layer 2 ─ mctrader-data (DATA-STORAGE 영역 단독 소유, → market + → 어댑터들) [OHS pattern, /v1 API endpoint]
Layer 2'─ mctrader-engine (PURE CONSUMER, mctrader_data=0, mctrader_market_*=0)
```

순환: 영원히 없음 (market → 누구도 의존 안 함, data → market + 어댑터, engine → market + REST). 본 4-Layer = OHS (Layer 2 /v1 REST API endpoint) + ACL (Layer 1 거래소 어댑터 → market Protocol 구현) 동시 보유 사례.

### CQRS

**영어**: CQRS (Command Query Responsibility Segregation)  
**정의**: Command (write) + Query (read) 책임 분리. command model ≠ query model.  
**plugin-codeforge 적용 사례**: codeforge governance BC 는 CQRS 미적용. mctrader application BC (CQRS Active) 는 별 SSOT.

### Event Sourcing

**영어**: Event Sourcing  
**정의**: state 가 Domain Event sequence 의 fold. event log = source of truth. snapshot = optimization.  
**plugin-codeforge 적용 사례**: codeforge FIX Ledger (Story §10) = Event Sourcing 패턴 — fix-event-v1 sequence 가 source of truth. snapshot = §0 Live Progress (advisory).

---

## codeforge governance BC 의 Authority / Specialist Pattern (ADR-091 §결정 1)

### Authority Pair

**영어**: Authority Pair  
**정의 (codeforge governance BC)**: ArchitectPLAgent (supervisor) + ArchitectAgent (chief author) 2-agent pair. plan consistency 책임 + Story 단위 산출물 (Change Plan + ADR draft) 의 final author authority. ADR-091 §결정 1 의 첫 DDD role enum.  
**plugin-codeforge 적용 사례**: Architectture lane 진입 시 ArchitectPLAgent + ArchitectAgent 동시 활성. PL = supervisor (deputy spawn + FIX root-cause 판정 + Sub-agent 산출물 통합 supervisor) / Architect = chief author (산출물 § 1-§11 + ADR draft + §8 Test Contract + §11 데이터 마이그레이션 author).

### Aggregate Root (governance metaphor)

**영어**: Aggregate Root (governance metaphor)  
**정의 (codeforge governance BC, ADR-091 §결정 3 Layer A)**: ArchitectPLAgent 의 supervised authority cluster metaphor. **metaphor only** — literal DDD Aggregate Root 아님 (Codex Q2 합의: agent = process participant ≠ domain object).  
**plugin-codeforge 적용 사례**: ArchitectPLAgent 가 6 deputy + chief author 산출물 통합 supervisor 의 metaphor. real Aggregate = ArchitectAgent 산출물 자체 (Layer B, 별 entry).

### Domain Service (governance contributor)

**영어**: Domain Service (governance contributor)  
**정의 (codeforge governance BC, ADR-091 §결정 1)**: specialized judgment contributor. 7 permanent SubAgent (SecurityArch / InfraOpArch / TestContractArch / AggregateArch / APIContractArch / ModuleArch / DataArch) + 3 sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst).  
**plugin-codeforge 적용 사례**: ArchitectPLAgent 가 deputy spawn 시 "specialized judgment contributor" role 으로 spawn. ArchitectAgent 가 chief author 로서 deputy 산출물 통합. operation-centric — boundary advocacy + specialized perspective.

### Subdomain Specialist

**영어**: Subdomain Specialist  
**정의 (codeforge governance BC, ADR-091 §결정 1)**: 3+1 CONDITIONAL deputy role — LiveOpsDeputyAgent / LiveOrderingDeputyAgent / ProductionEvidenceDeputyAgent + AggregateArch CONDITIONAL P2. "which subdomain under threat" 활성 시만 spawn.  
**plugin-codeforge 적용 사례**: ArchitectPLAgent 가 deputy spawn 결정 시 subdomain enum (live ops / live ordering / production evidence) 활성 여부 판단. Subdomain inactive = spawn 0 (PMO orchestration 절약).

### "Which subdomain under threat" (deputy spawn rationale)

**영어**: "Which subdomain under threat"  
**정의 (ADR-091 §결정 2)**: ArchitectPLAgent 의 deputy spawn rationale 어휘 — perspective-contributor (보수 / 혁신 / 위협) 어휘 transition. **subdomain decision is at risk** 시 Subdomain Specialist spawn.  
**plugin-codeforge 적용 사례**: Story 가 live trading 영역 영향 시 → "live ops subdomain under threat" → LiveOpsDeputyAgent spawn. Story 가 production cutover 영역 영향 시 → "production evidence subdomain under threat" → ProductionEvidenceDeputyAgent spawn.

---

## Anti-pattern (Forbid-list 후보, OQ-1 결정 영역)

### Big Ball of Mud (design intent forbid)

**영어**: Big Ball of Mud  
**정의 (anti-pattern)**: BC 부재 + Ubiquitous Language drift + Tangled dependencies. 도메인 모델 부재.  
**plugin-codeforge 적용 사례**: **design intent 로 채택 표현 금지** — ADR-064 forbid-list 확장 후보 (OQ-1). 실 description (after-the-fact analysis) 시 사용 가능, design plan 시 사용 금지.

### Smart UI (anti-pattern)

**영어**: Smart UI  
**정의**: 모든 logic 을 UI layer 에 집중. domain layer 부재.  
**plugin-codeforge 적용 사례**: anti-pattern reference only. codeforge governance BC 의 Application Service (Orchestrator) ↔ Domain Service (lane agent) 분리 mandate 가 Smart UI 차단.

### Anemic Domain Model

**영어**: Anemic Domain Model  
**정의**: Entity 가 attribute getter/setter 만, behavior 0. Domain Service / Application Service 가 모든 logic 담당. DDD core spirit 위반.  
**plugin-codeforge 적용 사례**: anti-pattern reference. codeforge governance BC = N/A (process-oriented BC). 단 application BC (mctrader 등) 검토 시 reference.

### Vocabulary Theater (codeforge 자체 anti-pattern)

**영어**: Vocabulary Theater  
**정의 (codeforge governance BC 자체 anti-pattern, ADR-091 §결정 7)**: 어휘 emit 만, decision flow 변경 0. agent 가 DDD 단어 emit 하면서 기존 implicit decision flow 유지 → restructure = document 만 향상 / runtime lesson 해소 = 0.  
**plugin-codeforge 적용 사례**: **ADR-091 §결정 7 forcing function 차단 대상**. INV-5 가 5 영역 명시 (Story field / deputy spawn rationale / Change Plan DDD field / review-verdict finding / ADR acceptance criteria) evidence enumeration 의무. Codex BIG CONCERN 정합.

---

## Cross-cutting / Process

### Strategic Design Workshop

**영어**: Strategic Design Workshop  
**정의**: BC 식별 + Subdomain 분류 + Context Map 결정 회의. 도메인 전문가 + 개발자 + ArchitectLane 참여.  
**plugin-codeforge 적용 사례**: codeforge brainstorm Phase 0 + Phase 1 (Codex 일괄 dispatch) = Strategic Design Workshop 의 codeforge 적용 (CFP-386 / Codex Q-by-Q stop 금지 패턴). 본 CFP-1117 brainstorm 자체가 Strategic Design Workshop 사례.

### Event Storming

**영어**: Event Storming  
**정의 (Alberto Brandolini)**: Domain Event 중심 워크샵. sticky note 로 event timeline 작성 → Aggregate / BC 식별. lightweight Strategic Design technique.  
**plugin-codeforge 적용 사례**: Story §13 (선택) Event Storming 후보 (downstream Epic mctrader 적용 시).

### Domain Story Telling

**영어**: Domain Story Telling  
**정의 (Stefan Hofer)**: Story 단위 행동 sequence 시각화. Actor / Workobject / Activity 3 element.  
**plugin-codeforge 적용 사례**: Story file §1 사용자 원문 + §2-§6 AC + §7 보안 + §8 Test Contract = Domain Story Telling 의 codeforge 적용 (Story-key 단위 actor-workobject-activity sequence).
