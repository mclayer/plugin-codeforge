# CLAUDE.md (codeforge-design)

codeforge ζ arc Design lane plugin (LAST extraction). 6 permanent + 3+1 CONDITIONAL SubAgent + 4-tuple sub-tuple + change-plan/adr templates. CFP-1086 / ADR-042 Amendment 8 — BackendArchEpic Phase 2 design lane 7+3+1 roster 재편 (AggregateArch + APIContractArch 신설 / CodeArch → ModuleArch rename / DataArch mandate 축소). **CFP-1126 / ADR-042 Amendment 10 — AggregateArch + ModuleArch 통합 (boundary axis 단일 advocate, 7→6 permanent, ratchet 축소 first applied carrier ADR-058 §결정 5).**

## Plugin position

codeforge core (>= 5.0.0) 의존.

## Inter-plugin contracts

- `design_output v2` — [`docs/inter-plugin-contracts/design-output-v2.md`](docs/inter-plugin-contracts/design-output-v2.md) (Active. v2.0 BREAKING from v1 — CFP-46 / ADR-014. v2.1 additive minor — CFP-47 §8.5 / ADR-015 [후속 PR-D])
- `design_output v1` — [`docs/inter-plugin-contracts/design-output-v1.md`](docs/inter-plugin-contracts/design-output-v1.md) (Archived 2026-04-30)

## Owner doc paths

- `docs/change-plans/**` — ArchitectAgent direct write (CFP-26 Phase 0a 보존)
- `docs/adr/**` — ArchitectAgent direct write (CFP-26 Phase 0a 보존)

## Self-write 책임

| Path | 책임 agent |
|---|---|
| `docs/change-plans/<slug>.md` (§7.4 운영 리스크 + §11.6 idempotency consult 통합 포함) | ArchitectAgent |
| `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent |
| `docs/stories/<KEY>.md §3 ADR list mirror` | ArchitectAgent |
| `docs/stories/<KEY>.md §7 보안 + §7.4 운영 리스크 mirror` | ArchitectAgent |
| `docs/stories/<KEY>.md §11 데이터 마이그레이션 mirror` | ArchitectAgent |
| GitHub comment `[설계]` prefix | ArchitectPLAgent |
| `phase:설계` → `phase:설계-리뷰` transition | ArchitectPLAgent |
| `docs/architecture/<path>.md` | ArchitectAgent (lane gate — ADR-078 §결정 1 4 영역 갱신 의무, 매 Change Plan merge 시) |

## 6 permanent + 3+1 CONDITIONAL SubAgent + 4-tuple sub-tuple (CFP-1086 — ADR-042 Amendment 8 / ADR-068 Amendment 2 / ADR-086; **CFP-1126 — ADR-042 Amendment 10 AggregateArch + ModuleArch 통합 7→6**)

**SubAgent 수 = 6 permanent + 3+1 CONDITIONAL + 4-tuple sub-tuple**. wrapper SSOT (CLAUDE.md "Deputy mandate 매트릭스" / skills/deputy-mandate/SKILL.md) 와 byte-consistent. **CFP-1126 Amendment 10 = AggregateArchitectAgent deprecate + ModuleArchitectAgent mandate 흡수 (boundary axis 단일 advocate, ratchet 축소 first applied carrier — ADR-058 §결정 5). RACI matrix 4→3 column 재편 = 별 CFP carrier (CFP scope unitary, 본 CFP-1126 = agent 통합 + roster count 정정만, RACI dangling reference 는 pointer note).**

**6 permanent deputy** (모든 설계 lane 진입 시 병렬 spawn — CONDITIONAL applicability 확인):

| Deputy | 입장 | 핵심 질문 | model tier |
|---|---|---|---|
| **SecurityArchitectAgent** | 위협 — 공격자 관점 | "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가" | Opus |
| **InfraOperationalArchitectAgent** (CFP-1026 S1 rename, OperationalRiskArch → Infra...) | 운영 리스크 + infra — production-readiness 변호자 | "끊겼을 때·실패했을 때·과부하일 때 어떻게 되는가, 스테이징/프로덕션 누설 차단되는가" | Opus |
| **TestContractArchitectAgent** | QA perspective contributor | §8 커버리지 후보·경계·invariant — 대립 비참여. **Epic 소속 Story 시 §8.6에 `story_key: <KEY>` + `suite: "story"` 필수** (IntegrationTestAgent Story Suite 자동 생성 연동 — CFP-371 / ADR-055 Amendment 2) | Opus |
| **DataArchitectAgent** (CFP-1086 Amendment 8 mandate 축소 — RDB OLTP 영역 제거, 빅데이터 OLAP only) | 빅데이터 OLAP 영역 변호자 | "Parquet schema 가 어떻게 진화하는가, 객체저장소 / DuckDB / streaming pipeline 정합인가, OLAP rollback (re-derivation strategy) 가능한가" | Opus |
| **ModuleArchitectAgent** (CFP-1086 Amendment 8 CodeArch rename; **CFP-1126 Amendment 10 — AggregateArch 통합 흡수, boundary axis 단일 advocate**) | §3 code boundary axis (module-level + aggregate-level) advocate — single-mandate | "module / package boundary + dependency direction + layered/hexagonal/clean module-level 정합인가 + (CONDITIONAL aggregate_arch.applicable) aggregate boundary 어디인가, 트랜잭션 경계 어디까지 atomic 인가, Alembic 정책 7 원칙 (양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) 정합인가" | Sonnet |
| **APIContractArchitectAgent** (CFP-1086 Amendment 8 신설 — skeleton at S1 / body 심화 = S2) | API transport contract advocate — single-mandate | "REST/GraphQL/gRPC/WebSocket 어떤 transport, API versioning 정책 (semver/URI/header), DTO contract / OpenAPI 또는 GraphQL schema / contract testing (Pact 등)" | Sonnet |

**3+1 CONDITIONAL deputy** (Story trigger 충족 시 추가 spawn):

| Deputy | trigger 조건 | 핵심 질문 |
|---|---|---|
| **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | real funds / live exchange API / production credential / live order placement 1+ touching | "operator approval / kill switch / incident response 가 충족되는가, OperationEvent audit trail 이 보존되는가" |
| **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | LiveOps 동일 trigger | "order submit / partial fill / cancel race / rejection mapping / ledger reconcile invariant 이 정합인가" |
| **ProductionEvidenceDeputy** (CONDITIONAL — production cutover Story 만, ADR-72) | Change Plan §13 `production_cutover_touching: true` 선언 OR §13 Live Operational Discipline 본문 보유. wrapper-self-app N/A (ADR-72 §결정 6) | "production evidence quad (functional / security / monitoring / testing) 4 source 충족하는가, EPIC CLOSED gate evidence 정합인가, Family 7 atomic canary pin length_invariant=7 정합인가" |
| **ModuleArch aggregate-level CONDITIONAL applicability** (CFP-1086 P2 신설 — 3+1; **CFP-1126 carry-over from AggregateArch**) | `project.yaml aggregate_arch.applicable: bool` (default `true`). non-applicable consumer = frontend-only / API-only / external-managed RDB | "본 consumer 가 RDB OLTP schema 제어권 보유하는가 — aggregate-level 영역 (ModuleArch mandate 8-13) 만 conditional, module-level 영역 (1-7) 은 무조건 applicable" |

## 4-tuple sub-tuple (deputy 아님 — ADR-044 CFP-676 reaffirm)

**4-tuple = 논리적 그룹핑** (deputy column 아님, flat spawn 패턴). wrapper SKILL.md "4-tuple sub-tuple spawn 가이드" 단락 정합.

- **ArchitectAgent** (chief author, Opus — multi-source synthesizer) — deputy 산출물 + 나머지 3 sub-tuple 산출물 통합
- **CodebaseMapperAgent** (Sonnet — existing codebase fact)
- **RefactorAgent** (Sonnet — decoupling / pattern advocacy)
- **ArchitectAnalystAgent** (Sonnet, CFP-1026 S1 신설 — PriorArtAgent conceptual rename, file move 0) — 변경 전 기존 설계 (ADR / Change Plan / Story §3/§7/§11) 분석 단일 축

**flat spawn 의미**: Orchestrator 가 4 component 모두 평행 spawn. 재귀 spawn 금지 (platform inherent) / nested team 금지 (ADR-044) / sub-lead 격상 0건 (ADR-009 §결정 1 + ADR-039 정합). 4-tuple = 어느 sub-agent 가 어느 deputy 영역 Context Packet 으로 spawn 됐는지를 표기하는 **논리적 그룹핑**일 뿐 **물리적 spawn 계층 (nested) 이 아니다**.

**InfraArchitect 신설 철회** (CFP-1026 S1 — ADR-042 Amendment 7 SSOT): Docker-first + AWS 없음 환경 — InfraArchitect 미도입 결정. InfraOperationalArchitect 가 §7.4.6 Container considerations 영역 cover.

**DDDArchitect 신설 reject** (CFP-1086 / ADR-042 Amendment 8 §DDDArchitectAgent reject 명문화): Phase 1 Q4-prime 사용자 발의 — axis 미정합 (method / 학파 layer + ModuleArch wording overlap + consumer applicability 축소). 미도입 결정, ratchet 위반 아님 (ADR-058 §결정 5 sunset_justification 불필요).

## 4-way 이념 대립 (7 permanent 중 대립 참여 — CFP-1086 정합)

ArchitectPLAgent 가 6 (또는 8/9/10) SubAgent 를 **병렬 spawn**. 대립 참여 = CodebaseMapper (4-tuple) ↔ Refactor (4-tuple) ↔ SecurityArch ↔ DataArch (OLAP 영역) / ModuleArch (aggregate-level RDB OLTP 영역, CFP-1126 통합). TestContractArch / InfraOperationalArch / APIContractArch = single-mandate advocacy / contributor 단일 축 — 대립 비참여. LiveOps / LiveOrdering / ProductionEvidence = CONDITIONAL contributor 단일 축 — 대립 비참여.

**CFP-1086 정합 4-way 영역 분리 (CFP-1126 통합 후)**:
- **RDB OLTP 영역 대립**: CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ ModuleArch (aggregate-level, CFP-1126 AggregateArch 흡수) (4-way)
- **빅데이터 OLAP 영역 대립**: CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ DataArch (4-way)
- **Cross-layer (ELT/ETL/CDC) 영역**: ModuleArch (aggregate-level) + DataArch co-author (deferred carrier — sibling Epic 산출 후 결정)

**독립 관점 유지**: 모든 SubAgent 원 소스 (코드 + ADR + Change Plan 초안 + Story §1-7) 직접 읽기. 한쪽이 다른 쪽의 요약에 의존하지 않음.

**충돌 해소**: 관점 충돌 시 ArchitectAgent (chief author) 가 결정 근거와 함께 Change Plan §2 (현재 구조) · §3 (도입할 설계 — code + aggregate + API + OLAP) · §7 (보안 설계) · §7.4 (운영 리스크) · §11 (데이터 마이그레이션 — RDB OLTP / 빅데이터 OLAP 분리) 에 명시. **chief tie-break ladder 3 단계** (ADR-068 Amendment 2): (1) RACI lookup → (2) ADR-068 invariant 적용 → (3) chief judgement + ADR Amendment carrier 발의.

**DesignReviewPL 교차 체크**: ArchitectAgent 통합 판정 + ArchitectPLAgent 검수가 각 변호 근거를 근거 있게 일축·수용했는가 / 요건 범위를 넘지 않았는가 / §7 보안 설계와 §7.4 운영 리스크와 §11 데이터 마이그레이션이 충실히 반영되었는가 / ModuleArch (aggregate-level) ↔ DataArch cross-layer boundary 명시했는가.

## RACI 4-way overlap zone (CFP-1086 Story-3 — wrapper SSOT mirror)

> **wrapper canonical SSOT** = [`skills/deputy-mandate/SKILL.md`](https://github.com/mclayer/plugin-codeforge/blob/main/skills/deputy-mandate/SKILL.md) `## RACI 표준 row 형식 (Story-3 — 4-way overlap zone body)` 단락. 본 단락 = 1-row summary mirror (각 Cell detail = wrapper skill 참조).

chief tie-break ladder 3 단계 (ADR-068 Amendment 2) 의 **1단계 (RACI matrix lookup)** 입력 SSOT. 다축 overlap 영역만 본 matrix 활성 — single-axis 결정은 wrapper SKILL.md `CFP-1086 7+3+1 primary axis matrix` 직접 lookup.

### 12-cell summary (3 sub-axis × 4 cross-axis)

> **CFP-1126 통합 note**: Aggregate column 의 C=AggregateArch → **C=ModuleArch (aggregate-level)** carry-over (AggregateArch deprecate, ModuleArch boundary axis 통합). 4-column → 3-column 정식 재편 (Aggregate + Module 통합) = **별 CFP carrier** (CFP scope unitary — 본 CFP-1126 = agent 통합 + roster count 정정, RACI full 재편은 design lane governance 변경 별 영역). 아래 표는 transitional state (Aggregate column 의 C=ModuleArch pointer 정정만, column 구조 보존).

| Sub-axis ↓ \\ Cross-axis → | Aggregate (R/C/I, CFP-1126 → ModuleArch aggregate-level) | Data OLAP (R/C/I) | Module (R/C/I) | APIContract (R/C/I) |
|---|---|---|---|---|
| **Security** | R=SecurityArch / C=ModuleArch / I=TestContract | R=SecurityArch / C=DataArch / I=TestContract | R=SecurityArch / C=ModuleArch / I=InfraOp | R=SecurityArch / C=APIContract / I=InfraOp |
| **InfraOp** | R=InfraOp / C=ModuleArch / I=TestContract | R=InfraOp / C=DataArch / I=TestContract | R=InfraOp / C=ModuleArch / I=SecurityArch | R=InfraOp / C=APIContract / I=TestContract |
| **TestContract** | R=TestContract / C=ModuleArch / I=InfraOp | R=TestContract / C=DataArch / I=SecurityArch | R=TestContract / C=ModuleArch / I=APIContract | **R=APIContract** / C=TestContract / I=InfraOp |

**Cell 3.4 예외**: `R = APIContractArch` (primary, §8.6 contract testing primary axis 정합) / `C = TestContractArch` (CI placement + orchestration). contract format ≠ CI placement disjoint axis (CFP-1086 §7+3+1 primary axis matrix row 정합).

### 4-column 열 정의 (전 row 공통)

- **R** (Responsible) — primary 결정권자 / 산출물 1차 author
- **A** (Accountable) — 모든 row = **ArchitectAgent** chief tie-break ladder 3단계 (ADR-068 Amendment 2)
- **C** (Consulted) — co-author / 양방향 dialog 의무
- **I** (Informed) — 일방향 통지 (PR description / Story §3/§7/§11 mirror)

### Cell selection heuristic

1. single-axis 결정 → wrapper skill `primary axis matrix` 직접 lookup (RACI 미적용)
2. 2-axis 이상 overlap → 본 12-cell row 활성 (R+C dialog, A sign-off, I 통지)
3. R+C 합의 부재 → chief tie-break ladder 2단계 (ADR-068 invariant)
4. invariant 적용 후 미해소 → ladder 3단계 (chief judgement + ADR Amendment 발의)

### Related ADRs

- ADR-068 Amendment 2 — chief tie-break ladder 3 단계 (RACI lookup → invariant → judgement+Amendment)
- ADR-086 — Deputy 신설 결정 framework P7 axis 분석 + 5-checklist self-app
- review-verdict-v4 v4.6 — `boundary_completeness_self_check_passed` scope expansion

## Sub-agent fan-out (ArchitectPL → 6 permanent + 3+1 CONDITIONAL SubAgent 병렬 + 4-tuple sub-tuple, CFP-1126 7→6)

| Deputy / Component | Spawn 시점 | 산출물 → chief author 통합 위치 |
|---|---|---|
| CodebaseMapperAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §2 현재 구조 |
| RefactorAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §3 도입할 설계 (refactor 시각) + §6 |
| ArchitectAnalystAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §2 (변경 전 기존 설계 컨텍스트) |
| SecurityArchitectAgent (deputy) | 설계 lane 진입 즉시 | §7.1-§7.3, §7.5-§7.7 보안 설계 |
| **DataArchitectAgent** (deputy, CFP-1086 mandate 축소) | 설계 lane 진입 즉시 | **§3 빅데이터 OLAP (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계) + §11 OLAP schema 진화 / OLAP rollback / OLAP integrity invariant** |
| **APIContractArchitectAgent** (deputy, CFP-1086 신설 skeleton — S2 body 심화) | 설계 lane 진입 즉시 | **§3 API contract (REST/GraphQL/gRPC/WebSocket + versioning + DTO + OpenAPI/GraphQL) + §8 contract testing (Pact 등)** |
| TestContractArchitectAgent (deputy) | 설계 lane 진입 즉시 | §8 Test Contract (**Epic 소속 Story 시 §8.6에 `story_key: <KEY>`, `suite: "story"` 필수**) |
| **InfraOperationalArchitectAgent** (deputy, CFP-1026 S1 rename) | 설계 lane 진입 즉시 | **§7.4 운영 리스크 6 항목 + §11.6 idempotency consult (ModuleArch aggregate-level primary 영역 협업, CFP-1126)** |
| **ModuleArchitectAgent** (deputy, CFP-1086 CodeArch rename + **CFP-1126 AggregateArch 통합 흡수**) | 설계 lane 진입 즉시 (aggregate-level 영역 = CONDITIONAL applicability `project.yaml aggregate_arch.applicable` 확인) | **§3 code boundary axis: module-level (module boundary + dependency direction + layered/hexagonal/clean + DDD bounded context module placement) + aggregate-level (DDD aggregate boundary + 트랜잭션 경계 + persistence-bound, CONDITIONAL) + §11.1-§11.6 RDB OLTP (Alembic 정책 7 원칙: 양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit, CFP-1126 흡수)** |
| **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | ArchitectPL 의 §13 CONDITIONAL trigger 검토 후 spawn | **§13 Live Operational Discipline (operator approval / kill switch / incident response / OperationEvent audit) + §7.5 (live API key) consult** |
| **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | ArchitectPL 의 §13 CONDITIONAL trigger 검토 후 spawn | **§11 Ledger reconcile / partial fill / fee invariant + §8.5 (order replay) + §11.6 idempotency (order side) consult** |
| **ProductionEvidenceDeputy** (CONDITIONAL — production cutover Story 만, ADR-72) | ArchitectPL 의 §13 production_cutover trigger 검토 후 spawn (wrapper-self-app N/A) | **§13 Production Evidence Quad (MS-1 live_touching / MS-2 production_cutover_touching dual-source AND / MS-3 marketplace_publish_touching / MS-4 consumer_impact_blast_radius) + EPIC CLOSED gate + post-cutover wiring + Family 7 atomic canary pin** |

ArchitectPLAgent prompt (CFP-1086 + CFP-1126 정합):
- **Backtest/Paper-only Story (default, ModuleArch aggregate-level applicable=true)**: "6 permanent deputy 병렬 spawn (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch / APIContractArch) + 3 4-tuple sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst) flat spawn (ArchitectAgent chief 포함). ArchitectAgent (chief author) 가 9 (6 + 3 sub-tuple) 산출물 통합 후 Change Plan §1-§13 author. ModuleArch = boundary axis (module-level + aggregate-level RDB OLTP) 통합 산출."
- **Frontend-only / API-only / external-managed consumer (`project.yaml aggregate_arch.applicable: false`)**: "ModuleArch aggregate-level 영역 N/A (module-level 영역 retain — 항상 spawn). 6 permanent deputy + 3 sub-tuple = 9 산출물 통합 (ModuleArch 산출물 = module-level only)."
- **Live touching Story (CFP-77 CONDITIONAL active)**: "위 + LiveOpsDeputy + LiveOrderingDeputy spawn. ArchitectAgent chief 가 11 산출물 통합 후 Change Plan §1-§13 + Story §13 author."
- **Production cutover Story (ADR-72 CONDITIONAL active)**: "위 + ProductionEvidenceDeputy spawn (wrapper-self-app N/A 시 미spawn). ArchitectAgent chief 가 12 산출물 통합."

CONDITIONAL trigger 판정 (ArchitectPL 의 의무):
- ModuleArch aggregate-level applicability: consumer `project.yaml aggregate_arch.applicable: bool` 확인 (default `true`). 미정의 시 `true` 가정. frontend-only / API-only / external-managed RDB consumer 만 `false` (ModuleArch 항상 spawn — aggregate-level 영역만 conditional, module-level 영역 무조건, CFP-1126)
- Live touching: Story 가 real funds / live exchange API / production credential / live order placement 중 하나 이상 touching 인지 검토
- Production cutover: Change Plan §13 `production_cutover_touching: true` 선언 OR §13 Live Operational Discipline 본문 보유. wrapper-self-app N/A (ADR-72 §결정 6)
- 모호 시 default = active (CONDITIONAL deputy spawn). 미spawn = ArchitectPL 의 명시적 §13 N/A 판정 의무

## ArchitectPLAgent 라이프사이클 (stateless 재스폰)

- 매 트리거마다 Orchestrator 가 신규 spawn — 세션 유지 없음
- Story file §1-8 재로딩으로 콘텍스트 복원
- 토큰 비용: 재스폰 당 ~5-10k tokens. FIX 3회 가정 시 15-30k overhead ([codeforge wrapper playbook §8](https://github.com/mclayer/plugin-codeforge/blob/main/docs/orchestrator-playbook.md) 참조). SubAgent 통합 token cost ~5-10k 추가.
- **ArchitectAgent (chief author)** 도 각 설계 lane 진입마다 stateless 재스폰 — SubAgent 산출물 입력 수령 후 Change Plan §1-§13 author. ArchitectPLAgent RETURN 시에도 재스폰

## 설계 lane Deputy Freshness

모든 SubAgent 공통:
- **매 설계 lane 진입 시 재스폰** (이전 Story 산출물 재사용 금지)
- 리뷰·테스트에서 설계 lane 복귀 시에도 재스폰 (구현 lane 에서 코드 변경 전제)
- base_sha / scope_paths frontmatter 갱신 의무

## 관련 ADR

- ADR-008 (Inter-plugin Contract Versioning) — design-output v1 → v2 BREAKING bump (CFP-46 PR-E)
- ADR-009 (Wrapper-only Decomposition) — ζ arc parent (5 SubAgent 구조 출처)
- ADR-010 (Inter-plugin Contract Sibling Sync) — design-output v2 sibling sync
- ADR-012 (Wrapper CLAUDE.md SSOT Boundary) — §3 4번째 예외 (operational risk 매트릭스 / decision row / mandate 경계)
- ADR-014 (Operational Risk SSOT Distribution) + **Amendment 4** (CFP-676 / S1) — 본 plugin §7.4 schema SSOT, OperationalRiskArch → InfraOperationalArch rename + §7.4 primary/shell 분류 + ProductionEvidence dual-spawn disjoint axis
- ADR-042 (Agent model selection policy) + **Amendment 7** (CFP-676 / S1) — design lane agent 구조 재편 model tier SSOT (CodeArchitect / ArchitectAnalyst Sonnet 신설 + DataArchitect / InfraOperationalArchitect rename Opus 유지 + InfraArchitect 신설 철회) + **Amendment 8** (CFP-1086 / Story-1) — BackendArchEpic Phase 2 design lane 7+3+1 roster 재편 (AggregateArch + APIContractArch Sonnet 신설 + CodeArch → ModuleArch rename + DataArch mandate 축소 RDB OLTP 영역 제거 + AggregateArch CONDITIONAL applicability P2 + DDDArchitect 신설 reject 명문화)
- ADR-044 (Phase-scoped sequential team) — flat spawn / nested team 금지 / 재귀 spawn 금지 / sub-lead 격상 0건 (CFP-676 reaffirm 단락)
- **ADR-068** (Boundary completeness invariants) + **Amendment 2** (CFP-1086 / Story-1 sibling) — wording SSOT chief tie-break ladder 3 단계 (RACI lookup → ADR-068 invariant → chief judgement + ADR Amendment 발의)
- **ADR-72** (ProductionEvidenceDeputy + Epic cutover gate) — CONDITIONAL deputy 3번째 (production cutover Story 만)
- ADR-078 (Living architecture doc SSOT) — `docs/architecture/codeforge-design.md` 본 doc 영역 갱신 의무 (CFP-969)
- **ADR-086** (CFP-1086 / Story-1 신설) — Deputy 신설 결정 framework P7 (axis 분석 의무 + 5-checklist self-application + deferred carrier path codify). 본 plugin agent file 신설 / rename / 축소 모두 본 framework self-application 의무.

## Dogfood policy (CFP-45)

본 plugin repo 는 runtime SSOT 만 보유. dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 단일 monorepo SSOT. 본 plugin 폴더는 `codeforge-internal-docs/design/`. 상세 정책 + Story workflow 흐름은 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) canonical SSOT 참조 + [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (PR-I 머지 후 Adopted).

Plugin repo 측 GitHub Issue 와 internal-docs 측 Story file 의 binding:
- Issue body frontmatter: `story_uri: <internal-docs URL>`
- Story file frontmatter: `story_issues: [{repo: "mclayer/plugin-codeforge-design", number: <N>}]`
- `.github/workflows/phase-gate-mergeable.yml` (본 repo) 가 cross-repo Story fetch via GitHub App
