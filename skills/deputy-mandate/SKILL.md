---
name: deputy-mandate
description: 6 permanent + 3+1 CONDITIONAL deputy mandate matrix. §3/§7/§11/§13 sub별 ownership (SecurityArch·InfraOperationalArch·TestContractArch·DataArch·ModuleArch·APIContractArch + CONDITIONAL LiveOps·LiveOrdering·ProductionEvidence + ModuleArch aggregate-level applicability P2). ArchitectAnalyst = 4-tuple sub-tuple (deputy 아님). 설계 lane ArchitectPLAgent deputy spawn 결정 전 Orchestrator 호출 의무. CFP-1086 / ADR-042-agent-model-selection-policy Amendment 8 — BackendArchEpic Phase 2 design lane 7+3+1 roster 재편. CFP-1126 / ADR-042-agent-model-selection-policy Amendment 10 + ADR-091 Amendment 1 — AggregateArch deprecated + ModuleArch boundary axis unified (7+3+1 → 6+3+1), RACI matrix 4-way → 3-way 전면 재편 (CFP-1168 realized).
tools: Read
---

# Deputy Mandate 매트릭스 (codeforge-design lane)

> 참조 테이블 skill — deputy spawn 결정 + §3/§7/§11/§13 책임 분담에 적용. normative SSOT = ADR-014(+Amd 4) · ADR-042(+Amd 7/8/10) · ADR-068(+Amd 2) · ADR-086 · ADR-091(+Amd 1) · ADR-072 · ADR-088.

## 호출 시점

- 설계 lane 진입 시 — ArchitectPLAgent 가 6 → 8(+ProductionEvidence=9) deputy parallel spawn 여부를 결정하기 전 (CFP-1126 — 6 permanent).
- ArchitectPLAgent 가 4-tuple sub-tuple flat spawn 을 결정하기 전 (CFP-681) — 아래 "4-tuple sub-tuple spawn 가이드" + playbook §12.8 (deputy 영역별 specialized Context Packet 4종 spec) cross-ref.
- 거버넌스 codify Story 진입 시 (실 설계 결정 0) — 매트릭스 + 4-tuple 가이드를 읽고 chief author 중심 + 자기 mandate deputy consult 만으로 codify 범위 확정. (deputy 무-target N/A 는 ADR-127 §결정 5 의 "산출물 target 부재 N/A" — 단축 아닌 정식 분류 결과.)

## 4-tuple sub-tuple spawn 가이드 (CFP-681 / ADR-044 CFP-676 reaffirm)

> **deputy column 아님 — flat spawn 논리적 그룹핑** (물리적 spawn 계층(nested) 아님 — "4-level nested spawn" 오해 차단). 4-tuple = ArchitectAgent (chief author, Opus — multi-source synthesizer) + CodebaseMapper (haiku, existing codebase fact — ADR-141 Amendment 1) + Refactor (Sonnet, decoupling / pattern / interface 분리 advocacy 구조 3축 + repo-분해 구조 escalation; 측정 축은 구현 리팩터링 Story C 이관 — CFP-2539) + **ArchitectAnalyst** (Sonnet, 기존 설계 분석 단일 축).

- **spawn gate**: 4 component 모두 Orchestrator 가 **flat spawn** — 재귀 spawn 금지 (platform inherent) / nested team 금지 / sub-lead 격상 0건 (ADR-044 + ADR-009 §결정 1 + ADR-039 정합).
- ArchitectPLAgent = PL synthesizer — 산출물 통합 검수만, sub-agent 재귀 spawn 금지 (env=0 fallback = Orchestrator 직접 spawn one-shot).
- Context Packet = spawn-time **동적** 주입 (매 spawn — playbook §12.8). consumer overlay SessionStart merge (정적) 와 구분.
- chief author 는 4-tuple component 이나 deputy 아님 — deputy + sub-tuple 산출물 multi-source synthesis (Opus). ArchitectAnalyst dual-read = primary git `docs/architecture/<plugin>.md` + fallback Confluence (CFP-1428, divergence 시 PMO retro F8 emit).

## Deputy mandate 매트릭스 — 6 permanent + 3+1 CONDITIONAL

ADR-014 (+ Amendment 4) + ADR-012 §3 4번째 SSOT 예외 + ADR-072 + ADR-086 (Deputy 신설 결정 framework). design lane deputy 가 §3/§7/§11/§13 sub별 owning 범위 명시 — H17 책임 분쟁 차단.

**roster 재편 연혁 (요약 — 상세 = 각 ADR Amendment SSOT)**:

- CFP-1026 (ADR-042 Amd 7 + ADR-014 Amd 4): DataMigrationArch→DataArch + OperationalRiskArch→InfraOperationalArch rename + CodeArch·ArchitectAnalyst(sub-tuple) 신설 (5+3 baseline).
- CFP-1086 (ADR-042 Amd 8 + ADR-068 Amd 2 + ADR-086): 5+3 → 7+3+1 — AggregateArch·APIContractArch 신설 + CodeArch→ModuleArch rename + DataArch 축소 (RDB OLTP 제거 → 빅데이터 OLAP only) + **chief tie-break ladder 3 단계** 신설 (ADR-068 Amd 2 — Cell selection heuristic 단락 정의 참조) + **DDDArchitectAgent 신설 reject 명문화** (미도입 결정 — reject 영역 보존).
- CFP-1126 (ADR-042 Amd 10 + ADR-091 Amd 1): **AggregateArch deprecated** — mandate carry-over to **ModuleArch (boundary axis 단일 advocate — module-level + aggregate-level 통합)**, 7 → **6 permanent**. **CONDITIONAL applicability carry-over**: `project.yaml aggregate_arch.applicable: bool` (key 보존, consumer overlay backward-compat) — non-applicable consumer (frontend-only / API-only / external-managed RDB) 는 aggregate-level 영역만 conditional, module-level 은 무조건 applicable. `aggregate_arch.migration_tool` 9-enum override (default alembic) 동반. RACI 4-way → 3-way 재편 = CFP-1168 realized.

### 6+3+1 primary axis matrix (canonical SSOT — CFP-1126 / ADR-042 Amendment 10 정합)

| Change Plan sub-section | owner deputy (primary R) | model |
|---|---|---|
| §2 현재 구조 (변경 전 기존 설계 컨텍스트) | CodebaseMapperAgent + ArchitectAnalystAgent (4-tuple sub-tuple) | haiku (Mapper — Amd1) / sonnet (Analyst — Amd2) |
| §3 code module-level (module boundary + dependency direction + layered/hexagonal/clean module-level + DDD bounded context module placement) | **ModuleArchitectAgent** (CFP-1086 — CodeArch rename + mandate 정정) | Sonnet |
| §3 aggregate (RDB OLTP — aggregate invariant + 트랜잭션 경계 + persistence-bound) | **ModuleArchitectAgent** (CFP-1126 — boundary axis unified, AggregateArch carry-over; CONDITIONAL `aggregate_arch.applicable`) | Sonnet |
| §3 API contract (transport + versioning + DTO + OpenAPI/GraphQL) | **APIContractArchitectAgent** (CFP-1086 신설, skeleton S1 / body 심화 S2) | Sonnet |
| §3 빅데이터 OLAP (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계) | **DataArchitectAgent** (CFP-1086 mandate 축소 — RDB OLTP 영역 제거) | Opus |
| §3 도입할 설계 (refactor 시각 — decoupling + pattern + interface 분리 구조 3축) + §6 리팩토링 선행 (repo-분해 구조 advocacy, escalation-tier) — 측정 축(중복제거/공통추출)은 구현 리팩터링 Story C 이관 (CFP-2539) — **결정 방식 = Codex proponent↔Claude opponent debate (blanket_designrefactor, per-Story, verdict judge=ArchitectAgent chief; RefactorAgent = advocacy input provider) — CFP-2543/ADR-138** | RefactorAgent (4-tuple sub-tuple) | Sonnet |
| §7.1-§7.3 / §7.5-§7.6 보안 | SecurityArchitectAgent | Opus |
| §7.4 운영 리스크 (DR / disconnect / clock / rate / env / container) + §11.6 idempotency consult (ModuleArch aggregate-level primary) | InfraOperationalArchitectAgent (CFP-1026 rename) | Opus (high-stakes) / Sonnet (low-stakes 4-AND) ※ |
| §8 Test Contract (커버리지 + 경계 + invariant + §8.5/§8.6 + **discriminating fixture mandate / RED→GREEN proof — CFP-1334** + **§8.7 production-venue shape fidelity CONDITIONAL — ADR-006 Amendment 1** [외부 venue/시계열 의존 시 captured-golden / 실형상-justified fixture, synthetic-only 불충분; §8.5 push_interval 수치 축과 disjoint] + **엣지 케이스 체계적 도출 기법 always-active — ADR-006 Amendment 2** [tier A EP/BVA/enum/collection 항상 + tier B Decision Table/State Transition/Pairwise/Property-based/Metamorphic 조건부; wrapper-self 코드 touch Story active — §8.7 항상 N/A 와 반대 방향; 케이스 *완결성* 축 — §8.7 *형상 정확성* 축과 disjoint]) | TestContractArchitectAgent | Opus |
| §8.6 contract testing (Pact / Spring Cloud Contract — API consumer-provider) | **APIContractArchitectAgent** primary + TestContractArchitectAgent consult | Sonnet (APIContract) |
| §11.1-§11.6 RDB OLTP (schema 변경 / migration / rollback / integrity / backfill / idempotency primary) + Alembic 정책 7 원칙 | **ModuleArchitectAgent** (CFP-1126 — boundary axis unified primary, AggregateArch carry-over) | Sonnet |
| §11 OLAP schema 진화 (Parquet schema / partition / column evolution) | **DataArchitectAgent** (CFP-1086 OLAP only) | Opus |
| §11 ELT/ETL/CDC cross-layer boundary (deferred — sibling Epic 산출 후 carrier 결정) | DataArchitectAgent + ModuleArchitectAgent (aggregate-level) co-author | (deferred) |
| §13 Live Operational Discipline (CONDITIONAL Live touching) | LiveOpsDeputy | Opus |
| §11 ledger reconcile + §8.5 order replay + §11.6 idempotency (order side, CONDITIONAL Live touching) | LiveOrderingDeputy | Opus |
| Production evidence quad + EPIC CLOSED gate + post-cutover wiring + Family 7 canary pin (CONDITIONAL production cutover) | ProductionEvidenceDeputy | Opus inherit |

> ※ **InfraOperationalArchitectAgent Story-shape 조건부 tier** (CFP-2432 / ADR-042 Amendment 16): frontmatter `model: opus` = fail-safe default. Orchestrator 가 low-stakes 4-AND shape(실자금 없음 ∧ production cutover 없음 ∧ 신규 신뢰경계 없음 ∧ live 외부 API 호출 없음)에서만 `opts.model: sonnet` fresh spawn override(SendMessage resume 금지), high-stakes 는 opus 보존. 판정 SSOT = `scripts/check-stakes-tier-gating.sh`(4-AND + `max(floor,overlay)` clamp). 배선 절차 = orchestrator-playbook §3.0.12a. consumer overlay 는 보수 방향(opus 강제)만 — down-tier 거부(확장-only).
>
> ※ **DomainAgent Story-shape 조건부 tier** (CFP-2445 / ADR-042 Amendment 17 — Amd16 §결정3 예약 자리 충족): DomainAgent 는 **요구사항 lane** spawn(본 설계 lane deputy 표 밖이나 동일 메커니즘). frontmatter `model: opus` = fail-safe default. flip 조건 = **(4-AND low-stakes) AND (financial-invariant-0 shape)** 2-predicate AND — financial-invariant-0 = stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축의 별 predicate(`STAKES_FINANCIAL_INVARIANT_ZERO`). DomainAgent 가 백테스트 결과 숫자를 생성·변형·해석하지 않을 때만 financial invariant 해석 표면 0(sonnet cover), 데이터·엔진·전략 접촉 시 opus 보존. 판정 = wrapper Orchestrator spawn-전 외부 shape(§1 원문 + directive 경로 키워드 — §4.1 미존재, 닭-달걀 회피). 판정 SSOT = `scripts/check-stakes-tier-gating.sh`(STAKES_AGENT=DomainAgent 분기). 배선 = orchestrator-playbook §3.0.12a. catalog = `docs/domain-knowledge/domain/backtesting-discipline/financial-correctness-invariant-catalog.md`(11 invariant + A/B). mandate 표면 재정의 = `DomainAgent.md` "financial-invariant-0 shape mandate 표면" 섹션(§결정2 invariant, 순수 model downgrade 금지).

**axis disjoint 검증** (ADR-086 §결정 1 정합 — CFP-1126 통합 후 boundary axis 단일 advocate):
- ModuleArch (boundary axis unified — module-level + aggregate-level) — module boundary ↔ aggregate boundary mapping = **단일 advocate 내부 정합 (CFP-1126 통합 — AggregateArch 자기 통합으로 cross-deputy consult 영역 제거)**
- ModuleArch (aggregate-level RDB OLTP) ↔ DataArch (빅데이터 OLAP) — ELT/ETL/CDC cross-layer = co-author 영역 (deferred carrier)
- APIContractArch (transport surface) ↔ ModuleArch (module placement) — module public API ↔ transport contract = co-author 영역
- SecurityArch (PII 정책) ↔ ModuleArch (aggregate-level PII persistence schema) — column type / encryption-at-rest schema = co-author 영역
- RefactorAgent (decoupling/pattern/interface **advocacy** 구조 3축 + repo-분해 구조 **advocacy** — repo-split pressure) ↔ ModuleArch (boundary **authority** — 경계 placement) = disjoint (CFP-2364 / ADR-042 Amendment 13; CFP-2539 / Amendment 18 — 측정 축은 구현 리팩터링 Story C 이관, disjoint 원칙은 잔여 구조 3축 + repo-분해에 상속). RefactorAgent 는 pressure 를 escalation-tier 로 제안만. 경계 확정 권한: module/aggregate-level 경계 = ModuleArch authority / **repo-level 분해 경계 = ArchitectAgent chief authority** (macro-architecture, ModuleArch mandate 초과 — ModuleArch consult).

> ⚠ **AggregateArch deprecated footnote** (CFP-1126 / ADR-042 Amd 10 + ADR-091 Amd 1, CFP-1168 realized): mandate carry-over to ModuleArch (boundary axis unified) 완료 — 본 matrix owner + axis disjoint 4 영역 + RACI 3-way 9-cell 모두 재편 완료 상태. agent file 실 deprecate = Wave 2 별 CFP carrier.

### CFP-676 historical 5+3 matrix

> superseded (CFP-1086 / CFP-1126) — historical 5+3 matrix 본문은 git history (pre-CFP-2234 본 파일) + ADR-042 Amendment 7 참조. 현행 lookup = 위 6+3+1 primary axis matrix 단일.

## CONDITIONAL deputy 활성 정책 (CFP-77 / ADR-072)

- **LiveOpsDeputy + LiveOrderingDeputy** = Live touching Story만 active (real funds / live exchange API / production credential / live order placement 중 하나 이상). Backtest/Paper-only Story = 미spawn.
- **ProductionEvidenceDeputy** (ADR-072 §결정 1/3) = Live touching Story **OR** production cutover 영향 Story 만 active (Change Plan §13 `production_cutover_touching: true` 선언 또는 §13 Live Operational Discipline 본문 보유). wrapper-self-app N/A (ADR-072 §결정 6 — ADR-005 `plugin-meta-na`). **Ownership 이관 (CFP-1059 / ADR-088 §결정 3)**: codeforge-design CONDITIONAL → codeforge-deploy-review 정식 이관 — mandate body 보존 (ADR-072 §결정 1-7 그대로), ownership 만 이전. 이관 후 = codeforge-deploy-review 의 정규 deputy.
- ArchitectPLAgent가 Story의 §13 CONDITIONAL trigger 검토 후 spawn 결정:
  - Backtest/Paper-only: 5 permanent deputy
  - Live touching pre-cutover: 8 (5 + LiveOps + LiveOrdering + [4-tuple sub-tuple])
  - Production cutover: 9 (5 + LiveOps + LiveOrdering + ProductionEvidence)
- 활성 시: ArchitectAgent chief가 전 deputy 산출물 + 4-tuple sub-agent (CodebaseMapper / Refactor / ArchitectAnalyst) 산출물 통합 (multi-source synthesis — Opus).

**InfraOperationalArch ↔ ProductionEvidence disjoint axis (ADR-072 §결정 4 / ADR-014 Amendment 4 §결정 3)**: policy SSOT (InfraOperationalArch §7.4 invariant 정의 — design-time) vs evidence SSOT (ProductionEvidence production grounding 실측 명시 — runtime). consumer production cutover Story 에서 dual-spawn 가능 (영역 disjoint). wrapper-self-app 시 ProductionEvidence N/A.

§7.4 schema 자체는 codeforge-design plugin SSOT. wrapper는 본 매트릭스만 SSOT 보유 (ADR-014 + Amendment 4 / ADR-072 / ADR-042 Amendment 7).

## DDD pattern mapping (ADR-091 §결정 1/2 — CFP-1117 S5)

> ArchitectLane agent ↔ DDD role Hybrid mapping. Published Language SSOT = [`docs/glossary.md`](../../docs/glossary.md). **단일 DDD 패턴 전 agent 강제 = false precision → 거부 (3 role 만 — ADR-091 §결정 1 rationale)**.

### 1. Authority Pair (ArchitectPLAgent + ArchitectAgent)

- **ArchitectPLAgent** = Authority Pair **Layer A** (Aggregate Root metaphor — governance BC, PL metaphor): supervised authority cluster. Story 단위 plan consistency boundary 의 supervisor. **deputy spawn 결정 주체** — 6 permanent + 3+1 CONDITIONAL spawn 여부 + 4-tuple flat spawn 결정.
- **ArchitectAgent** (chief author) = Authority Pair **Layer B** (산출물 = real Aggregate): multi-source synthesizer. Change Plan + ADR draft + §8 Test Contract + §11 = **real consistency boundary** — §1-§11 + BC classification + aggregate impacts 가 handoff 전 cohere 의무.

> Layer A (metaphor only) ↔ Layer B (real consistency boundary) explicit separate = 동음이의 (governance BC ↔ application BC) 충돌 차단 의무 (ADR-091 §결정 3). consumer application BC 의 DDD Aggregate = 별 BC — `docs/glossary.md` 3 distinct semantics entry 분리.

### 2. Domain Service (6 permanent SubAgent + 3 sub-tuple)

다음 = **Domain Service** — "specialized judgment contributor — **BC Owner 아님** (Story 가 multiple BC 가로지를 수 있음 → advisory expertise ≠ contextual authority)":

| Agent | Domain Service 영역 |
|---|---|
| SecurityArchitectAgent | 보안 설계 (§7.1-§7.3 / §7.5-§7.6) |
| InfraOperationalArchitectAgent | 운영 리스크 (§7.4 DR / disconnect / clock / rate / env / container) |
| TestContractArchitectAgent | §8 Test Contract |
| APIContractArchitectAgent | transport (REST/GraphQL/gRPC/WebSocket) + API versioning + §8.6 contract testing |
| ModuleArchitectAgent (boundary axis unified) | module-level boundary + aggregate-level boundary 통합 (layered / hexagonal / clean / DDD bounded context module placement + module boundary + dependency direction + RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound + Alembic 정책 7 원칙 — AggregateArch carry-over per CFP-1126) |
| DataArchitectAgent | 빅데이터 OLAP (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계) |
| CodebaseMapperAgent (sub-tuple) | fact source 변호자 — file structure / API surface / dependency graph 만 인용 |
| RefactorAgent (sub-tuple) | refactoring 옹호자 — decoupling / pattern / interface 분리 (구조 3축) + repo-분해 구조 pressure(escalation-tier). 측정 축(중복제거·공통추출)은 구현 리팩터링 Story C 이관 (CFP-2539) **결정 방식 = blanket_designrefactor debate (Codex proponent↔Claude opponent, verdict judge=ArchitectAgent chief) — CFP-2543/ADR-138. advocacy input provider(verdict 주체 아님).** |
| ArchitectAnalystAgent (sub-tuple) | prior art / industry pattern analyst |

> sub-tuple 3 = Domain Service role 이지만 **deputy column 아님** (4-tuple flat spawn 논리적 그룹핑). `bounded_context: codeforge-governance`, `ddd_pattern: Domain Service` (ADR-091 §결정 5 frontmatter field).

### 3. Subdomain Specialist (3+1 CONDITIONAL) — "which subdomain under threat" 어휘 transition

3+1 CONDITIONAL deputy = **Subdomain Specialist**. ADR-091 §결정 2 spawn rationale 어휘 transition: "perspective-contributor" → **"which subdomain under threat"** (subdomain decision is at risk → Subdomain Specialist spawn).

| Deputy | spawn rationale 어휘 (ArchitectPL spawn 결정 input) | spawn trigger (실 영향) |
|---|---|---|
| LiveOpsDeputy | "which subdomain under threat = **live ops**" | Live touching Story (real funds / live exchange API / production credential / live order placement 중 1+) — live ops subdomain decision at risk 시 spawn |
| LiveOrderingDeputy | "which subdomain under threat = **live ordering**" | Live touching Story 의 order side (ledger reconcile / partial fill / fee invariant / order idempotency) — live ordering subdomain decision at risk 시 spawn |
| ProductionEvidenceDeputy | "which subdomain under threat = **production evidence**" | production cutover 영향 Story (Change Plan §13 `production_cutover_touching: true` 또는 §13 Live Operational Discipline 본문 보유) — production evidence subdomain decision at risk 시 spawn. ownership = codeforge-deploy-review (ADR-088 §결정 3 이관 declarative) |

> **vocabulary theater 차단 (INV-5 — ADR-091 §결정 7)**: 본 "which subdomain under threat" 어휘는 **단순 nominal 명칭이 아니라 ArchitectPL 의 CONDITIONAL spawn 결정 input 에 실제 반영**된다. ArchitectPL 이 CONDITIONAL spawn 결정 (Backtest/Paper-only: 미spawn / Live touching: LiveOps + LiveOrdering / Production cutover: + ProductionEvidence) 시, **어느 subdomain decision 이 risk 에 처했는가** (live ops / live ordering / production evidence) 를 판정해 그 enum 어휘를 spawn rationale 로 명시 출력해야 한다. **어휘 emit ↔ spawn decision 결합 = forcing function**. Deputy = contributor 유지 (BC Owner 아님 — deputy = BC Owner = overreach 거부, ADR-091 §결정 2 rationale).

연혁 주석 (각 1줄 — 상세 = git history + ADR Amendment):
- W1 S2 보강 완료 (CFP-681) — S1 (CFP-676) 매트릭스 본문 위 additive 보강 (4-tuple 가이드 + Context Packet cross-ref).
- CFP-1086 Story-1 보강 완료 — 7+3+1 재편 반영 (ADR-042 Amendment 8 SSOT).
- CFP-1168 RACI 재편 완료 — 4-way 12-cell → 3-way 9-cell (ADR-042 Amendment 10 + ADR-091 Amendment 1 SSOT).

## RACI 표준 row 형식 (3-way overlap zone body)

chief tie-break ladder (ADR-068 Amendment 2) **1단계 (RACI matrix lookup)** 입력 SSOT — 3-way overlap zone 의 명시적 R/A/C/I 4-column row 형식 (CFP-1086 Story-3 body + CFP-1168 재편).

### 4-column 열 정의

- **Responsible (R)** — primary 결정권자 (single role per row, 결정 권한 owner). 실 author / 산출물 1차 작성 책임.
- **Accountable (A)** — approver / final sign-off (chief tie-break ladder 3단계 trigger 영역 — **ArchitectAgent chief author**). 모든 row 의 A = ArchitectAgent (ADR-068 Amendment 2 §결정 1).
- **Consulted (C)** — co-author / 협업 (mandate scope 가 partial overlap, input 제공). 결정권 없으나 행위 결정 전 양방향 dialog 의무.
- **Informed (I)** — notified only (mandate scope 외, 변경 영향 인지 의무). 일방향 통지 — dialog 없음.

### 3-way overlap zone (3 sub-axis × 3 cross-axis = 9 cells)

primary single-axis 결정은 §primary axis matrix lookup, **다축 overlap 영역**만 본 RACI lookup 으로 처리. (CFP-1168: 구 4-way 12-cell 의 Aggregate cross-axis column 을 ModuleArch aggregate-level 로 흡수.)

| Sub-axis ↓ \\ Cross-axis → | Data (빅데이터 OLAP) | Module (boundary + dependency + aggregate-level RDB OLTP, unified) | APIContract (transport + DTO) |
|---|---|---|---|
| **Security** (PII / 권한 / audit log / threat) | Cell 1.1 | Cell 1.2 | Cell 1.3 |
| **InfraOp** (DR / clock / rate / env / container) | Cell 2.1 | Cell 2.2 | Cell 2.3 |
| **TestContract** (커버리지 / 경계 / invariant / §8.5/§8.6) | Cell 3.1 | Cell 3.2 | Cell 3.3 |

### Row 1 — Security cross-axis

#### Cell 1.1 — Security × Data (OLAP PII 익명화 / 보존 정책 / Parquet column 마스킹)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | OLAP PII 정책 (익명화 알고리즘 + 보존 기간 + GDPR/CCPA 정합 + downstream re-identification 차단) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 — RACI lookup PASS 영역 |
| **C** | DataArchitectAgent | Parquet column 마스킹 / partition pruning / OLAP query plan PII 영역 격리 (how realized in OLAP) |
| **I** | TestContractArchitectAgent | §8 OLAP PII 통합 테스트 fixture redaction 인지 |

#### Cell 1.2 — Security × Module (trust boundary module 배치 / dependency direction + aggregate-level PII column / encryption-at-rest)

> CFP-1168 흡수 — 구 Security × Aggregate cell 통합 (ModuleArch aggregate-level).

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | trust boundary 정의 + threat model — 어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가 + PII 분류 정책 + 권한 모델 + audit log invariant (what / who / why) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | ModuleArchitectAgent (boundary axis unified) | (module-level) trust boundary 가 module / package 경계와 정합인지 + dependency direction (untrusted → trusted 일방향) 보장 / (aggregate-level RDB OLTP) PII column type / encryption-at-rest schema co-author + Alembic migration 정합 (how stored) |
| **I** | InfraOperationalArchitectAgent | §7.4.1 trust boundary 의 runtime container / network mode 영역 인지 + (TestContract cross-ref) §8 PII redaction test / audit log 커버리지 인지 |

#### Cell 1.3 — Security × APIContract (auth / authz / rate limit / input validation)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | SecurityArchitectAgent | §7.3 auth/authz 정책 + §7.6 위협↔완화 매핑 (OWASP API Security Top 10) + token / session / scope 정의 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | APIContractArchitectAgent | API endpoint 별 auth scheme (OAuth2 / JWT / mTLS) + rate limit header 표준 (RFC 6585 + X-RateLimit-*) + input validation schema (OpenAPI / JSON Schema) co-author |
| **I** | InfraOperationalArchitectAgent | §7.4.4 rate limit runtime enforcement (transport-level retry / circuit breaker) 인지 |

### Row 2 — InfraOp cross-axis

#### Cell 2.1 — InfraOp × Data (OLAP scan / streaming throttle / batch window)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | OLAP 운영 파라미터 — scan timeout / streaming backpressure / batch window 정책 / 백필 rate (DR + 7.4.4 rate 영역) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | DataArchitectAgent | OLAP query plan / partition strategy / streaming pipeline lineage 가 운영 파라미터와 정합인지 |
| **I** | TestContractArchitectAgent | §8.5 streaming replay / backfill idempotency test 인지 |

#### Cell 2.2 — InfraOp × Module (runtime module 분리 / hot reload + aggregate-level connection pool / replica / advisory lock)

> CFP-1168 흡수 — 구 InfraOp × Aggregate cell 통합 (ModuleArch aggregate-level).

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | runtime container 분리 (§7.4.6 container) + hot reload 정책 + module 단위 process boundary + §7.4 운영 파라미터 (connection pool size / replica failover / DB advisory lock timeout / restart policy — DR 영역) |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | ModuleArchitectAgent (boundary axis unified) | (module-level) module / package boundary 가 runtime process boundary 와 정합인지 + dependency direction 이 deploy 단위 정합인지 / (aggregate-level) 트랜잭션 경계 / isolation level / aggregate boundary 가 pool / replica / lock 정책과 정합인지 (semantics 영역) |
| **I** | SecurityArchitectAgent | runtime container secret mount / image layer 누설 영역 (§7.5) 인지 + (TestContract cross-ref) §8.5 stateful test (restart invariant + replica failover scenario) 인지 |

#### Cell 2.3 — InfraOp × APIContract (transport-level retry / circuit breaker / timeout / cancel-on-disconnect)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | InfraOperationalArchitectAgent | §7.4.2 disconnect / §7.4.4 rate limit — transport retry policy (exponential backoff + jitter) + circuit breaker 임계 + connection timeout + cancel-on-disconnect 정합 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | APIContractArchitectAgent | API contract level retry-safety (idempotent verb 정합 + retry header + 5xx vs 4xx mapping + GraphQL persisted query retry semantics) co-author |
| **I** | TestContractArchitectAgent | §8.5 stateful test (cancel-on-disconnect + circuit breaker open/close transition) 인지 |

### Row 3 — TestContract cross-axis

#### Cell 3.1 — TestContract × Data (OLAP fixture / streaming replay / lineage test)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | TestContractArchitectAgent | §8 OLAP test contract — Parquet fixture seed + streaming replay scenario + lineage test invariant + 백필 idempotency 커버리지 |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | DataArchitectAgent | OLAP schema 진화 test (Parquet schema evolution + partition pruning + column rename) + streaming pipeline replay seed |
| **I** | SecurityArchitectAgent | OLAP fixture PII redaction (Cell 1.1 cross-ref) 인지 |

#### Cell 3.2 — TestContract × Module (module boundary test / dependency test + aggregate-level migration forward/backward + idempotency test)

> CFP-1168 흡수 — 구 TestContract × Aggregate cell 통합 (ModuleArch aggregate-level).

| Role | Deputy | 책임 |
|---|---|---|
| **R** | TestContractArchitectAgent | §8 module boundary test — dependency direction assertion (ArchUnit / depcheck / dependency-cruiser) + module public API surface 커버리지 + (aggregate-level) migration forward + reverse + idempotency 커버리지 / invariant assertion / §11.6 idempotency test scope |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | ModuleArchitectAgent (boundary axis unified) | (module-level) module / package boundary 정의 + dependency direction 정합 (layered/hexagonal/clean module-level) test seed 제공 / (aggregate-level) Alembic 정책 7 원칙 정합 test seed (양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) + test fixture 의 aggregate boundary 정합 |
| **I** | APIContractArchitectAgent | module public API ↔ transport contract 정합 (Cell 3.3 cross-ref) 인지 + (InfraOp cross-ref) §8.5 stateful migration restart scenario 인지 |

#### Cell 3.3 — TestContract × APIContract (contract testing — Pact / OpenAPI / GraphQL schema validate)

| Role | Deputy | 책임 |
|---|---|---|
| **R** | APIContractArchitectAgent | §8.6 contract testing **primary** (6+3+1 primary axis matrix row 정합) — Pact consumer-driven / Spring Cloud Contract provider-driven / Schemathesis schema-based 3 paradigm |
| **A** | ArchitectAgent | chief tie-break ladder 3단계 |
| **C** | TestContractArchitectAgent | §8.6 통합 테스트 CI placement + orchestration 책임 (contract format ≠ CI placement disjoint axis) |
| **I** | InfraOperationalArchitectAgent | Pact broker 운영 + contract testing CI 인프라 인지 |

### Cell selection heuristic (chief author 적용 ladder 1단계)

1. **single-axis 결정** (단축 영역 only) → §primary axis matrix 직접 lookup. RACI 미적용.
2. **2-axis 이상 overlap** detected → 본 3-way matrix 의 해당 Cell row 활성:
   - R deputy 가 산출물 1차 author
   - C deputy 가 양방향 dialog (input 제공 / 영역별 정합 검토)
   - A = chief author (ArchitectAgent) 가 R+C 합의 사후 sign-off
   - I deputy 는 일방향 통지 (PR description / Story §3/§7/§11 mirror)
3. **R+C 합의 부재** → chief tie-break ladder 2단계 (ADR-068 invariant 적용) 진입
4. **invariant 적용 후에도 미해소** → chief tie-break ladder 3단계 (chief judgement + ADR Amendment carrier 발의)

Cross-ref (1줄): ladder 3 단계 = ADR-068 Amendment 2 / 6+3+1 재편 = ADR-042 Amendment 10 + ADR-091 Amendment 1 / Deputy 신설 framework = ADR-086 / review-verdict `boundary_completeness_self_check_passed` = CFP-1086 carrier / codeforge-design `CLAUDE.md` = 본 단락 mirror (wrapper skill canonical).
