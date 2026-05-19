---
name: deputy-mandate
description: 5 permanent + 3 CONDITIONAL deputy mandate matrix. §3/§7/§11/§13 sub별 ownership (SecurityArch·TestContractArch·DataArch·InfraOperationalArch·CodeArch + CONDITIONAL LiveOps·LiveOrdering·ProductionEvidence). ArchitectAnalyst = 4-tuple sub-tuple (deputy 아님). 설계 lane ArchitectPLAgent deputy spawn 결정 전 Orchestrator 호출 의무.
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

## Deputy mandate 매트릭스 — 5 permanent + 3 CONDITIONAL (CFP-676 / ADR-042 Amendment 7)

ADR-014 (+ Amendment 4) + ADR-012 §3 4번째 SSOT 예외 + ADR-72. design lane deputy가 §3/§7/§11/§13 sub별 owning 범위 명시 — H17 책임 분쟁 차단.

**CFP-1026 S1 재편 (ADR-042 Amendment 7 / ADR-014 Amendment 4 atomic carrier)**:
- DataMigrationArch → **DataArch** rename + mandate 확장 (§3 data + §11 전체 데이터 구조: entity / aggregate / value object / DB schema / event schema / DTO / API contract data / persistence model / 데이터 흐름 + migration). Opus 유지.
- OperationalRiskArch → **InfraOperationalArch** rename (§7.4 DR / disconnect / clock / rate / env / container — mandate scope 보존). Opus 유지.
- **CodeArch** 신설 (§3 code: layered / hexagonal / clean / DDD bounded context / module boundary / dependency direction). Sonnet (single-mandate advocacy — ADR-042 §결정 1 Sonnet (a)).
- 6 permanent → **5 permanent** (DataMigration→Data 흡수 rename, 순삭제 0).
- **ArchitectAnalyst** (PriorArtAgent rename, Sonnet) = CodebaseMapper / Refactor 와 함께 **4-tuple sub-tuple** (chief author 포함 — flat spawn 논리적 그룹핑, deputy column 아님). ADR-044 CFP-676 reaffirm 단락 정합 (flat spawn / nested team 금지 / 재귀 spawn 금지 / sub-lead 격상 0건).

| §3 / §7 / §11 / §13 sub | SecurityArch | **InfraOperationalArch** | TestContractArch | **DataArch** | **CodeArch** | **LiveOps** (CONDITIONAL) | **LiveOrdering** (CONDITIONAL) | **ProductionEvidence** (CONDITIONAL) |
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
