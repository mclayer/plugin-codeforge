---
name: deputy-mandate
description: 7 permanent + 3+1 CONDITIONAL deputy mandate matrix. §3/§7/§11/§13 sub별 ownership (SecurityArch·InfraOperationalArch·TestContractArch·DataArch·ModuleArch·AggregateArch·APIContractArch + CONDITIONAL LiveOps·LiveOrdering·ProductionEvidence + AggregateArch applicability P2). ArchitectAnalyst = 4-tuple sub-tuple (deputy 아님). 설계 lane ArchitectPLAgent deputy spawn 결정 전 Orchestrator 호출 의무. CFP-1086 / ADR-042 Amendment 8 — BackendArchEpic Phase 2 design lane 7+3+1 roster 재편.
tools: Read
---

# Deputy Mandate 매트릭스 (codeforge-design lane)

> 참조 테이블 skill — 내용을 읽고 deputy spawn 결정 및 §3/§7/§11/§13 책임 분담에 적용하세요.

## 호출 시점

설계 lane 진입 시. ArchitectPLAgent가 5 → 8(+ProductionEvidence=9) deputy parallel spawn 여부를 결정하기 전 호출.

추가 trigger (CFP-681 / W1 S2):
- ArchitectPLAgent 가 4-tuple sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst — chief author 포함) flat spawn 을 결정하기 전. 본 skill 의 "4-tuple sub-tuple spawn 가이드" 섹션 + playbook §12.8 (deputy 영역별 specialized Context Packet 4종 spec) cross-ref.
- doc-only fast-path mechanism codify Story 진입 시 (실 설계 결정 0) — 본 skill 매트릭스 + 4-tuple 가이드를 읽고 chief author 중심 + 자기 mandate deputy consult 만으로 codify 범위를 확정.

## 4-tuple sub-tuple spawn 가이드 (CFP-681 / W1 S2 — ADR-044 CFP-676 reaffirm)

> **deputy column 아님 — flat spawn 논리적 그룹핑**. 본 가이드는 deputy mandate 매트릭스 (5 permanent + 3 CONDITIONAL) 와 disjoint 한 별개 축이다. 4-tuple = ArchitectAgent (chief author, Opus — multi-source synthesizer) + CodebaseMapper (Sonnet, existing codebase fact) + Refactor (Sonnet, decoupling/pattern advocacy) + **ArchitectAnalyst** (Sonnet, PriorArtAgent rename — 변경 전 기존 설계 ADR/Change Plan/Story 분석 단일 축). single-mandate advocacy 패턴 (ADR-042 Amendment 7 SSOT — `abcd92bf`).

**"4-tuple = 논리적 그룹핑" 정의**: 4-tuple 은 어느 sub-agent 가 어느 deputy 영역 Context Packet 으로 spawn 됐는지를 표기하는 **논리적 그룹핑**일 뿐 **물리적 spawn 계층(nested)이 아니다**. 4 component 모두 Orchestrator 가 flat spawn (재귀 spawn 금지 — platform inherent / nested team 금지 / sub-lead 격상 0건 — ADR-044 CFP-676 reaffirm 단락 + ADR-009 §결정 1 + ADR-039 정합). "4-level nested spawn" 오해 차단 (Story §1 deliverable 3 verbatim — CFP-681 EC-6).

**spawn 주체·시점**:
- spawn 주체 = **Orchestrator** (flat spawn, ADR-039 §결정 1 default subagent context). ArchitectPLAgent 는 PL synthesizer 역할 — 4-tuple 산출물 통합 검수만, sub-agent 를 재귀 spawn 하지 않는다 (env=0 fallback = Orchestrator 직접 spawn one-shot).
- Context Packet = spawn-time **동적** 주입 (매 spawn — playbook §12.8). consumer overlay SessionStart merge (정적 desired state) 와 명시적 구분.

**chief author 포함 의미**: ArchitectAgent (chief author) 는 4-tuple 의 component 이지만 deputy 가 아니다. deputy 5 permanent + 3 CONDITIONAL (자기 mandate 단일 축 advocacy) 산출물 + 나머지 3 sub-tuple (Mapper/Refactor/ArchitectAnalyst) 산출물을 **multi-source synthesis** 하는 Opus chief 역할. ArchitectAnalyst (Sonnet) 는 chief 가 아니라 "기존 설계 분석 단일 축" advocate.

## Deputy mandate 매트릭스 — 7 permanent + 3+1 CONDITIONAL (CFP-1086 / ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086 신설)

ADR-014 (+ Amendment 4) + ADR-012 §3 4번째 SSOT 예외 + ADR-72 + ADR-086 (Deputy 신설 결정 framework). design lane deputy가 §3/§7/§11/§13 sub별 owning 범위 명시 — H17 책임 분쟁 차단.

### CFP-1086 Story-1 재편 (ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086 신설 atomic carrier)

BackendArchEpic Phase 2 — 5+3 → 7+3+1 roster 재편 (axis 명확화):

- **AggregateArch** 신설 (§3 aggregate + §11 RDB OLTP 전체: aggregate boundary + 트랜잭션 경계 + persistence-bound + Alembic 정책 7 원칙). Sonnet (single-mandate advocacy — ADR-042 §결정 1 Sonnet (a)). **CONDITIONAL applicability** (`project.yaml aggregate_arch.applicable: bool` — frontend-only / API-only / external-managed consumer non-applicable). Tool scope B — 9-enum `aggregate_arch.migration_tool` override (default alembic).
- **APIContractArch** 신설 (§3 API + §8 contract testing: REST/GraphQL/gRPC/WebSocket + versioning + DTO + OpenAPI/GraphQL schema + contract testing). Sonnet (single-mandate advocacy). skeleton at S1 / body 심화 = S2 별 PR.
- **CodeArch → ModuleArch rename + mandate 정정** (axis 명확화 — "코드 구조 일반" → "module / package boundary + dependency direction"). 도메인 모델 invariant 영역 = AggregateArch 분리. Sonnet 유지.
- **DataArch mandate 축소** — RDB OLTP 영역 제거 (PostgreSQL / SQLAlchemy / Alembic / 트랜잭션 경계 / 도메인 모델 모두 AggregateArch 분리). 빅데이터 OLAP only (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계). Opus 유지.
- 5 permanent → **7 permanent** (2 신설). 3 CONDITIONAL → **3+1 CONDITIONAL** (AggregateArch applicability P2 추가).
- **chief tie-break ladder 3 단계** (ADR-068 Amendment 2): (1) RACI matrix lookup → (2) ADR-068 invariant (I-1~I-5) → (3) chief judgement + ADR Amendment carrier 발의 (axis disjoint + 5-checklist 의무).
- **DDDArchitectAgent 신설 reject 명문화** (Phase 1 Q4-prime — axis 미정합 method/학파 layer + ModuleArch wording overlap + consumer applicability 축소). 미도입 결정, ratchet 위반 아님.

### CFP-1026 S1 재편 (ADR-042 Amendment 7 / ADR-014 Amendment 4 atomic carrier — historical layer)

CFP-1086 Amendment 8 이전 baseline (5+3 roster):
- DataMigrationArch → **DataArch** rename + mandate 확장 (§3 data + §11 전체 데이터 구조). Opus 유지. **(CFP-1086 Amendment 8 에서 mandate 축소 — RDB OLTP 영역 제거)**
- OperationalRiskArch → **InfraOperationalArch** rename (§7.4 DR / disconnect / clock / rate / env / container — mandate scope 보존). Opus 유지.
- **CodeArch** 신설 (§3 code: layered / hexagonal / clean / DDD bounded context / module boundary / dependency direction). Sonnet. **(CFP-1086 Amendment 8 에서 ModuleArch rename + mandate 정정)**
- 6 permanent → **5 permanent** (DataMigration→Data 흡수 rename, 순삭제 0). **(CFP-1086 Amendment 8 에서 5 → 7 permanent — AggregateArch + APIContractArch 신설)**
- **ArchitectAnalyst** (PriorArtAgent rename, Sonnet) = CodebaseMapper / Refactor 와 함께 **4-tuple sub-tuple** (chief author 포함 — flat spawn 논리적 그룹핑, deputy column 아님). CFP-1086 Amendment 8 변경 0건 (sub-tuple invariant 보존).

### CFP-1086 7+3+1 primary axis matrix (Amendment 8 정합 — 본 matrix 가 canonical SSOT)

| Change Plan sub-section | owner deputy (primary R) | model |
|---|---|---|
| §2 현재 구조 (변경 전 기존 설계 컨텍스트) | CodebaseMapperAgent + ArchitectAnalystAgent (4-tuple sub-tuple) | Sonnet |
| §3 code module-level (module boundary + dependency direction + layered/hexagonal/clean module-level + DDD bounded context module placement) | **ModuleArchitectAgent** (CFP-1086 — CodeArch rename + mandate 정정) | Sonnet |
| §3 aggregate (RDB OLTP — aggregate invariant + 트랜잭션 경계 + persistence-bound) | **AggregateArchitectAgent** (CFP-1086 신설, CONDITIONAL applicability) | Sonnet |
| §3 API contract (transport + versioning + DTO + OpenAPI/GraphQL) | **APIContractArchitectAgent** (CFP-1086 신설, skeleton S1 / body 심화 S2) | Sonnet |
| §3 빅데이터 OLAP (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계) | **DataArchitectAgent** (CFP-1086 mandate 축소 — RDB OLTP 영역 제거) | Opus |
| §3 도입할 설계 (refactor 시각) + §6 리팩토링 선행 | RefactorAgent (4-tuple sub-tuple) | Sonnet |
| §7.1-§7.3 / §7.5-§7.6 보안 | SecurityArchitectAgent | Opus |
| §7.4 운영 리스크 (DR / disconnect / clock / rate / env / container) + §11.6 idempotency consult (AggregateArch primary) | InfraOperationalArchitectAgent (CFP-1026 rename) | Opus |
| §8 Test Contract (커버리지 + 경계 + invariant + §8.5/§8.6) | TestContractArchitectAgent | Opus |
| §8.6 contract testing (Pact / Spring Cloud Contract — API consumer-provider) | **APIContractArchitectAgent** primary + TestContractArchitectAgent consult | Sonnet (APIContract) |
| §11.1-§11.6 RDB OLTP (schema 변경 / migration / rollback / integrity / backfill / idempotency primary) + Alembic 정책 7 원칙 | **AggregateArchitectAgent** (CFP-1086 신설 primary) | Sonnet |
| §11 OLAP schema 진화 (Parquet schema / partition / column evolution) | **DataArchitectAgent** (CFP-1086 OLAP only) | Opus |
| §11 ELT/ETL/CDC cross-layer boundary (deferred — sibling Epic 산출 후 carrier 결정) | DataArchitectAgent + AggregateArchitectAgent co-author | (deferred) |
| §13 Live Operational Discipline (CONDITIONAL Live touching) | LiveOpsDeputy | Opus |
| §11 ledger reconcile + §8.5 order replay + §11.6 idempotency (order side, CONDITIONAL Live touching) | LiveOrderingDeputy | Opus |
| Production evidence quad + EPIC CLOSED gate + post-cutover wiring + Family 7 canary pin (CONDITIONAL production cutover) | ProductionEvidenceDeputy | Opus inherit |

**axis disjoint 검증** (ADR-086 §결정 1 정합):
- ModuleArch (module-level) ↔ AggregateArch (aggregate-level) — module boundary ↔ aggregate boundary mapping = consult 영역 (chief tie-break ladder 적용)
- AggregateArch (RDB OLTP) ↔ DataArch (빅데이터 OLAP) — ELT/ETL/CDC cross-layer = co-author 영역 (deferred carrier)
- APIContractArch (transport surface) ↔ ModuleArch (module placement) — module public API ↔ transport contract = co-author 영역
- SecurityArch (PII 정책) ↔ AggregateArch (PII persistence schema) — column type / encryption-at-rest schema = co-author 영역

### CFP-676 historical 5+3 matrix (CFP-1086 Amendment 8 이전 baseline — historical layer 보존)

> 본 matrix = CFP-676 / ADR-042 Amendment 7 시점 baseline. CFP-1086 Amendment 8 에서 superseded — 본 matrix 의 CodeArch / DataArch 영역은 CFP-1086 정합으로 ModuleArch / DataArch (축소) 로 변경됨. AggregateArch / APIContractArch column 미존재 (CFP-1086 신설).

| §3 / §7 / §11 / §13 sub | SecurityArch | **InfraOperationalArch** | TestContractArch | **DataArch** (~~RDB+OLAP~~ → OLAP only per CFP-1086) | **CodeArch** (~~code 일반~~ → ModuleArch per CFP-1086) | **LiveOps** (CONDITIONAL) | **LiveOrdering** (CONDITIONAL) | **ProductionEvidence** (CONDITIONAL) |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| §3 Code 설계 (layered/hexagonal/clean/DDD/module boundary/dependency direction) | — | — | — | — | ✅ | — | — | — |
| §3 Data 구조 (entity/aggregate/VO/persistence model/데이터 흐름) | — | — | — | ✅ | (consult module boundary) | — | — | — |
| §7.1 Trust boundary | ✅ **(+container network mode / secret mount)** | (consult) | — | — | — | (consult Live API) | — | (consult prod env) |
| §7.2 Threat model | ✅ | — | — | — | — | — | — | — |
| §7.3 Auth/authz | ✅ | — | — | — | — | (consult operator approval) | — | — |
| **§7.4 DR / disconnect / rate limit / env isolation / container** | (consult) | **✅ (primary 4-sub: DR §7.4.1 / Clock §7.4.3 / Env §7.4.5 / Container §7.4.6 — restart policy / volume DR / health check / network mode; cross-ref shell 2-sub: Rate §7.4.4 / Disconnect §7.4.2 evidence-driven)(+environment containment owner)** | — | — | — | (consult Live failure) | (consult exchange rate-limit) | **(consult — evidence axis, production cutover Story)** |
| **§7.4 Clock sync (CONDITIONAL)** | (consult) | **✅** | — | — | — | — | — | (consult drift 실측) |
| §7.5 민감 데이터 분류 | ✅ **(+container secret mount / image layer 누설)(+credential threat owner: vault path / runtime injection / key permission)** | (consult containment) | — | — | — | (consult API key) | — | — |
| §7.6 위협↔완화 매핑 | ✅ | (DR↔failover consult) | — | — | — | (consult kill switch) | — | — |
| **§11 Idempotency (CONDITIONAL)** | — | (consult)(+N줄 memo input — §7.4.2 disconnect 짝) | — | **✅ (+cell primary author)** | — | — | (consult order idempotency) | — |
| §11 Schema/Migration/Rollback + 전체 데이터 구조 | — | — | — | ✅ **(+DB container volume / data persistence / event schema / DTO / API contract data)** | (consult module boundary) | — | — | — |
| **§11 Ledger reconcile / partial fill / fee invariant (CONDITIONAL Live)** | — | (consult) | — | (consult §11) | — | — | **✅** | — |
| **§8.5 Stateful / restart invariant** | — | (consult §7.4 짝) | **✅** | (consult §11.6 짝) | — | — | (consult order replay) | — |
| **§13 Live Operational Discipline (CONDITIONAL Live touching)** | (consult §7.5) | (consult kill switch) | — | (consult §11) | — | **✅** | (consult §11 ledger) | (consult cutover evidence) |
| **Production evidence quad / EPIC CLOSED gate / post-cutover wiring (CONDITIONAL production cutover)** | (consult §7.5) | **(consult — policy SSOT axis)** | — | — | — | (consult) | (consult) | **✅ (evidence SSOT axis — ADR-72 §결정 2/4)** |

✅ = primary owner / (consult) = secondary input.

## CONDITIONAL deputy 활성 정책 (CFP-77 / ADR-72)

- **LiveOpsDeputy + LiveOrderingDeputy** = Live touching Story만 active (real funds / live exchange API / production credential / live order placement 중 하나 이상). Backtest/Paper-only Story = 미spawn.
- **ProductionEvidenceDeputy** (ADR-72 §결정 1/3) = Live touching Story **OR** production cutover 영향 Story 만 active (Change Plan §13 `production_cutover_touching: true` 선언 또는 §13 Live Operational Discipline 본문 보유). wrapper-self-app N/A (ADR-72 §결정 6 — ADR-005 `plugin-meta-na`).
- ArchitectPLAgent가 Story의 §13 CONDITIONAL trigger 검토 후 spawn 결정:
  - Backtest/Paper-only: 5 permanent deputy
  - Live touching pre-cutover: 8 (5 + LiveOps + LiveOrdering + [4-tuple sub-tuple])
  - Production cutover: 9 (5 + LiveOps + LiveOrdering + ProductionEvidence)
- 활성 시: ArchitectAgent chief가 전 deputy 산출물 + 4-tuple sub-agent (CodebaseMapper / Refactor / ArchitectAnalyst) 산출물 통합 (multi-source synthesis — Opus).

**InfraOperationalArch ↔ ProductionEvidence disjoint axis (ADR-72 §결정 4 / ADR-014 Amendment 4 §결정 3)**: policy SSOT (InfraOperationalArch §7.4 invariant 정의 — design-time) vs evidence SSOT (ProductionEvidence production grounding 실측 명시 — runtime). consumer production cutover Story 에서 dual-spawn 가능 (영역 disjoint). wrapper-self-app 시 ProductionEvidence N/A.

§7.4 schema 자체는 codeforge-design plugin SSOT. wrapper는 본 매트릭스만 SSOT 보유 ([ADR-014](../../docs/adr/ADR-014-operational-risk-ssot-distribution.md) + Amendment 4, [ADR-72](../../docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md), [ADR-042 Amendment 7](../../docs/adr/ADR-042-agent-model-selection-policy.md)).

> **W1 S2 보강 완료 (CFP-681 — state dependency on CFP-676 S1 해소)**: S1 (CFP-676, wrapper main `abcd92bf`) 이 5+3 mandate matrix 본문 + frontmatter + §13 Live Discipline 행을 full 재작성 완료. 본 S2 = **매트릭스 본문 재작성 0 (S1 산출물 보존)** + additive 보강만: (a) "호출 시점" 4-tuple spawn trigger 추가 (b) 신규 "4-tuple sub-tuple spawn 가이드" 섹션 (CodebaseMapper/Refactor/ArchitectAnalyst + chief author — flat spawn 논리적 그룹핑, nested 금지 reaffirm) (c) playbook §12.8 (deputy 영역별 specialized Context Packet 4종 spec) + ADR-039 §결정 1 cross-ref (d) CLAUDE.md "Deputy mandate 매트릭스" 단락 (`abcd92bf` L229-233) 과 deputy 명칭 5종 + 3 CONDITIONAL + ArchitectAnalyst sub-tuple 표현 byte-consistent 재확인. "full 재작성" 의 §1 의도 = S1+S2 누적으로 5+3 매트릭스 + 4-tuple/Context Packet spec 최종 형태 SSOT 존재 — 충족 (CFP-681 §2.5 상충 조정 / AC-1). agent file 실 신설/rename = W2 S3 (codeforge-design sibling).

> **CFP-1086 Story-1 보강 완료 (BackendArchEpic Phase 2 — 7+3+1 roster 재편)**: CFP-1086 / ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086 신설 atomic carrier 가 5+3 → 7+3+1 (AggregateArch + APIContractArch 신설 + ModuleArch rename + DataArch 축소 + AggregateArch CONDITIONAL applicability P2) 재편. 본 SKILL.md 보강: (a) frontmatter description 갱신 (5+3 → 7+3+1) (b) "Deputy mandate 매트릭스" 단락 header CFP-1086 layer 추가 (c) "CFP-1086 7+3+1 primary axis matrix" 신규 단락 (canonical SSOT — owner deputy per Change Plan sub-section + axis disjoint 검증 4 영역) (d) CFP-676 historical 5+3 matrix retain (superseded marker 추가) (e) "RACI 표준 row 형식 (Story-3 carrier skeleton)" 신규 단락 (4-column R/A/C/I body 채움 = Story-3 별 PR). agent file 실 신설/rename = 본 Story-1 codeforge-design plugin sibling PR (doc-only fast-path ADR-054 5-repo atomic).

## RACI 표준 row 형식 (Story-3 — 4-way overlap zone body)

CFP-1086 / ADR-068 Amendment 2 chief tie-break ladder 3 단계 의 **1단계 (RACI matrix lookup)** 입력 SSOT — 4-way overlap zone 의 명시적 R/A/C/I 4-column row 형식. 본 단락 body = **CFP-1086 Wave 2 Story-3 carrier** (skeleton → body 전환 완료).

### 4-column 열 정의

- **Responsible (R)** — primary 결정권자 (single role per row, 결정 권한 owner). 실 author / 산출물 1차 작성 책임.
- **Accountable (A)** — approver / final sign-off (chief tie-break ladder 3단계 trigger 영역 — **ArchitectAgent chief author**). 모든 row 의 A = ArchitectAgent (chief tie-break ladder ADR-068 Amendment 2 §결정 1).
- **Consulted (C)** — co-author / 협업 (mandate scope 가 partial overlap, input 제공). 결정권 없으나 행위 결정 전 양방향 dialog 의무.
- **Informed (I)** — notified only (mandate scope 외, 변경 영향 인지 의무). 일방향 통지 — dialog 없음.

### 4-way overlap zone (3 sub-axis × 4 cross-axis = 12 cells)

본 12-cell matrix = CFP-1086 §7+3+1 primary axis matrix 의 cross-axis 영역 보강. primary single-axis 결정은 §primary axis matrix lookup, **다축 overlap 영역**만 본 RACI lookup 으로 처리.

| Sub-axis ↓ \\ Cross-axis → | Aggregate (RDB OLTP) | Data (빅데이터 OLAP) | Module (boundary + dependency) | APIContract (transport + DTO) |
|---|---|---|---|---|
| **Security** (PII / 권한 / audit log / threat) | Cell 1.1 | Cell 1.2 | Cell 1.3 | Cell 1.4 |
| **InfraOp** (DR / clock / rate / env / container) | Cell 2.1 | Cell 2.2 | Cell 2.3 | Cell 2.4 |
| **TestContract** (커버리지 / 경계 / invariant / §8.5/§8.6) | Cell 3.1 | Cell 3.2 | Cell 3.3 | Cell 3.4 |

### Row 1 — Security cross-axis (Cell 1.1 ~ Cell 1.4)

#### Cell 1.1 — Security × Aggregate (PII column type / encryption-at-rest / RDB audit log schema)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | PII 분류 정책 + 권한 모델 + audit log invariant 정의 (what / who / why) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 — RACI lookup PASS 영역 |
| **C** | AggregateArchitectAgent | RDB OLTP column type / encryption-at-rest schema co-author + Alembic migration 정합 (how stored) |
| **I** | TestContractArchitectAgent | §8 PII redaction test + audit log 커버리지 인지 |

#### Cell 1.2 — Security × Data (OLAP PII 익명화 / 보존 정책 / Parquet column 마스킹)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | OLAP PII 정책 (익명화 알고리즘 + 보존 기간 + GDPR/CCPA 정합 + downstream re-identification 차단) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | DataArchitectAgent | Parquet column 마스킹 / partition pruning / OLAP query plan PII 영역 격리 (how realized in OLAP) |
| **I** | TestContractArchitectAgent | §8 OLAP PII 통합 테스트 fixture redaction 인지 |

#### Cell 1.3 — Security × Module (trust boundary module 배치 / dependency direction)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | trust boundary 정의 + threat model — 어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | ModuleArchitectAgent | trust boundary 가 module / package 경계와 정합인지 + dependency direction (untrusted → trusted 일방향) 보장 |
| **I** | InfraOperationalArchitectAgent | §7.4.1 trust boundary 의 runtime container / network mode 영역 인지 |

#### Cell 1.4 — Security × APIContract (auth / authz / rate limit / input validation)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | §7.3 auth/authz 정책 + §7.6 위협↔완화 매핑 (OWASP API Security Top 10) + token / session / scope 정의 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | APIContractArchitectAgent | API endpoint 별 auth scheme (OAuth2 / JWT / mTLS) + rate limit header 표준 (RFC 6585 + X-RateLimit-*) + input validation schema (OpenAPI / JSON Schema) co-author |
| **I** | InfraOperationalArchitectAgent | §7.4.4 rate limit runtime enforcement (transport-level retry / circuit breaker) 인지 |

### Row 2 — InfraOp cross-axis (Cell 2.1 ~ Cell 2.4)

#### Cell 2.1 — InfraOp × Aggregate (connection pool / replica / advisory lock)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | §7.4 운영 파라미터 — connection pool size / replica failover / DB advisory lock timeout / restart policy (DR 영역) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | AggregateArchitectAgent | 트랜잭션 경계 / isolation level / aggregate boundary 가 pool / replica / lock 정책과 정합인지 (semantics 영역) |
| **I** | TestContractArchitectAgent | §8.5 stateful test (restart invariant + replica failover scenario) 인지 |

#### Cell 2.2 — InfraOp × Data (OLAP scan / streaming throttle / batch window)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | OLAP 운영 파라미터 — scan timeout / streaming backpressure / batch window 정책 / 백필 rate (DR + 7.4.4 rate 영역) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | DataArchitectAgent | OLAP query plan / partition strategy / streaming pipeline lineage 가 운영 파라미터와 정합인지 |
| **I** | TestContractArchitectAgent | §8.5 streaming replay / backfill idempotency test 인지 |

#### Cell 2.3 — InfraOp × Module (runtime module 분리 / hot reload)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | runtime container 분리 (§7.4.6 container) + hot reload 정책 + module 단위 process boundary |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | ModuleArchitectAgent | module / package boundary 가 runtime process boundary 와 정합인지 + dependency direction 이 deploy 단위 정합인지 |
| **I** | SecurityArchitectAgent | runtime container secret mount / image layer 누설 영역 (§7.5) 인지 |

#### Cell 2.4 — InfraOp × APIContract (transport-level retry / circuit breaker / timeout / cancel-on-disconnect)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | §7.4.2 disconnect / §7.4.4 rate limit — transport retry policy (exponential backoff + jitter) + circuit breaker 임계 + connection timeout + cancel-on-disconnect 정합 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | APIContractArchitectAgent | API contract level retry-safety (idempotent verb 정합 + retry header + 5xx vs 4xx mapping + GraphQL persisted query retry semantics) co-author |
| **I** | TestContractArchitectAgent | §8.5 stateful test (cancel-on-disconnect + circuit breaker open/close transition) 인지 |

### Row 3 — TestContract cross-axis (Cell 3.1 ~ Cell 3.4)

#### Cell 3.1 — TestContract × Aggregate (migration forward/backward + idempotency test)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | TestContractArchitectAgent | §8 test contract — migration forward + reverse + idempotency 커버리지 / invariant assertion / §11.6 idempotency test scope |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | AggregateArchitectAgent | Alembic 정책 7 원칙 정합 test seed (양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) + test fixture 의 aggregate boundary 정합 |
| **I** | InfraOperationalArchitectAgent | §8.5 stateful migration restart scenario 인지 |

#### Cell 3.2 — TestContract × Data (OLAP fixture / streaming replay / lineage test)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | TestContractArchitectAgent | §8 OLAP test contract — Parquet fixture seed + streaming replay scenario + lineage test invariant + 백필 idempotency 커버리지 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | DataArchitectAgent | OLAP schema 진화 test (Parquet schema evolution + partition pruning + column rename) + streaming pipeline replay seed |
| **I** | SecurityArchitectAgent | OLAP fixture PII redaction (Cell 1.2 cross-ref) 인지 |

#### Cell 3.3 — TestContract × Module (module boundary test / dependency test)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | TestContractArchitectAgent | §8 module boundary test — dependency direction assertion (ArchUnit / depcheck / dependency-cruiser) + module public API surface 커버리지 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | ModuleArchitectAgent | module / package boundary 정의 + dependency direction 정합 (layered/hexagonal/clean module-level) test seed 제공 |
| **I** | APIContractArchitectAgent | module public API ↔ transport contract 정합 (Cell 3.4 cross-ref) 인지 |

#### Cell 3.4 — TestContract × APIContract (contract testing — Pact / OpenAPI / GraphQL schema validate)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | APIContractArchitectAgent | §8.6 contract testing **primary** (CFP-1086 §7+3+1 primary axis matrix row 정합) — Pact consumer-driven / Spring Cloud Contract provider-driven / Schemathesis schema-based 3 paradigm |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | TestContractArchitectAgent | §8.6 통합 테스트 CI placement + orchestration + test orchestration 책임 (contract format ≠ CI placement disjoint axis) |
| **I** | InfraOperationalArchitectAgent | Pact broker 운영 + contract testing CI 인프라 인지 |

### Cell selection heuristic (chief author 적용 ladder 1단계)

1. **single-axis 결정** (단축 영역 only) → §primary axis matrix 직접 lookup. RACI 미적용.
2. **2-axis 이상 overlap** detected → 본 4-way matrix 의 해당 Cell row 활성:
   - R deputy 가 산출물 1차 author
   - C deputy 가 양방향 dialog (input 제공 / 영역별 정합 검토)
   - A = chief author (ArchitectAgent) 가 R+C 합의 사후 sign-off
   - I deputy 는 일방향 통지 (PR description / Story §3/§7/§11 mirror)
3. **R+C 합의 부재** → chief tie-break ladder 2단계 (ADR-068 invariant 적용) 진입
4. **invariant 적용 후에도 미해소** → chief tie-break ladder 3단계 (chief judgement + ADR Amendment carrier 발의)

### Cross-ref

- **ADR-068 Amendment 2** (CFP-1086 / Story-1) — chief tie-break ladder 3 단계: (1) RACI matrix lookup (본 단락 body 4-way 12-cell SSOT) → (2) ADR-068 invariant 적용 → (3) chief judgement + ADR Amendment 발의
- **ADR-086** (CFP-1086 / Story-1 신설) — Deputy 신설 결정 framework §결정 1 axis 분석 + §결정 2 5-checklist self-app. RACI codify = mechanism gap 해소 ratchet (chief tie-break 3단계 → 1단계로 Move-left)
- **review-verdict-v4 v4.6** (CFP-1086 carrier) — `boundary_completeness_self_check_passed` scope expansion (Amendment 2 ladder 3단계 mechanism 통과 의무)
- **CFP-1086 Story-2** — APIContractArch mandate body 심화 (Cell 1.4 / 2.4 / 3.4 의 C/R 영역 detail SSOT)
- **codeforge-design `CLAUDE.md`** — RACI section mirror (wrapper skill SSOT 참조)

본 RACI 4-way 12-cell codify = ratchet 강화 방향 (1단계 RACI matrix lookup 영역 확장 → 3단계 chief judgement 영역 축소). ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합. additive only — Story-1 skeleton 영역 보존 + Story-3 body 12-cell 채움.
