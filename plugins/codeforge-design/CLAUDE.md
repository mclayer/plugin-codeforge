# CLAUDE.md (codeforge-design)

codeforge ζ arc Design lane plugin (LAST extraction). 6 permanent + 3+1 CONDITIONAL SubAgent + 4-tuple sub-tuple + change-plan/adr templates. 현재 roster = 6 permanent (AggregateArch 가 ModuleArch boundary axis 로 통합됨). 개정 출처는 문서 끝 「관련 ADR」 블록 참조.

## Plugin position

codeforge core (>= 5.0.0) 의존.

## Inter-plugin contracts

- `design_output v2` — wrapper repo 루트 `docs/inter-plugin-contracts/design-output-v2.md` (canonical — S2/CFP-2158 단일 원본 승격. 설치 캐시 기준 plugin 디렉터리 외부 — 링크 비제공) (Active. v2.0 BREAKING from v1 — CFP-46 / ADR-014. v2.1 additive minor — CFP-47 §8.5 / ADR-015 [후속 PR-D])
- `design_output v1` — wrapper repo 루트 `docs/inter-plugin-contracts/design-output-v1.md` (canonical, Archived 2026-04-30)

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

## 6 permanent + 3+1 CONDITIONAL SubAgent + 4-tuple sub-tuple

**SubAgent 수 = 6 permanent + 3+1 CONDITIONAL + 4-tuple sub-tuple**. wrapper SSOT (CLAUDE.md "Deputy mandate 매트릭스" / skills/deputy-mandate/SKILL.md) 와 byte-consistent. AggregateArchitectAgent 는 deprecate 되어 ModuleArchitectAgent 가 boundary axis 단일 advocate 로 mandate 흡수.

**6 permanent deputy** (모든 설계 lane 진입 시 병렬 spawn — CONDITIONAL applicability 확인):

| Deputy | 입장 | 핵심 질문 | model tier |
|---|---|---|---|
| **SecurityArchitectAgent** | 위협 — 공격자 관점 | "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가" | Opus |
| **InfraOperationalArchitectAgent** | 운영 리스크 + infra — production-readiness 변호자 | "끊겼을 때·실패했을 때·과부하일 때 어떻게 되는가, 스테이징/프로덕션 누설 차단되는가" | Opus |
| **TestContractArchitectAgent** | QA perspective contributor | §8 커버리지 후보·경계·invariant — 대립 비참여. **Epic 소속 Story 시 §8.6에 `story_key: <KEY>` + `suite: "story"` 필수** (IntegrationTestAgent Story Suite 자동 생성 연동) | Opus |
| **DataArchitectAgent** | 빅데이터 OLAP 영역 변호자 (RDB OLTP 영역 제외) | "Parquet schema 가 어떻게 진화하는가, 객체저장소 / DuckDB / streaming pipeline 정합인가, OLAP rollback (re-derivation strategy) 가능한가" | Opus |
| **ModuleArchitectAgent** | §3 code boundary axis (module-level + aggregate-level) advocate — single-mandate | "module / package boundary + dependency direction + layered/hexagonal/clean module-level 정합인가 + (CONDITIONAL aggregate_arch.applicable) aggregate boundary 어디인가, 트랜잭션 경계 어디까지 atomic 인가, Alembic 정책 7 원칙 (양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) 정합인가" | Sonnet |
| **APIContractArchitectAgent** | API transport contract advocate — single-mandate | "REST/GraphQL/gRPC/WebSocket 어떤 transport, API versioning 정책 (semver/URI/header), DTO contract / OpenAPI 또는 GraphQL schema / contract testing (Pact 등)" | Sonnet |

**3+1 CONDITIONAL deputy** (Story trigger 충족 시 추가 spawn):

| Deputy | trigger 조건 | 핵심 질문 |
|---|---|---|
| **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만) | real funds / live exchange API / production credential / live order placement 1+ touching | "operator approval / kill switch / incident response 가 충족되는가, OperationEvent audit trail 이 보존되는가" |
| **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만) | LiveOps 동일 trigger | "order submit / partial fill / cancel race / rejection mapping / ledger reconcile invariant 이 정합인가" |
| **ProductionEvidenceDeputy** | — | codeforge-deploy-review 로 이관 완료 (ADR-088 §결정 4) — 본 lane 은 spawn 하지 않음 (canonical = `plugins/codeforge-deploy-review/agents/ProductionEvidenceDeputyAgent.md`) |
| **ModuleArch aggregate-level CONDITIONAL applicability** | `project.yaml aggregate_arch.applicable: bool` (default `true`). non-applicable consumer = frontend-only / API-only / external-managed RDB | "본 consumer 가 RDB OLTP schema 제어권 보유하는가 — aggregate-level 영역 (ModuleArch mandate 8-13) 만 conditional, module-level 영역 (1-7) 은 무조건 applicable" |

## 4-tuple sub-tuple (deputy 아님 — ADR-044 CFP-676 reaffirm)

**4-tuple = 논리적 그룹핑** (deputy column 아님, flat spawn 패턴). wrapper SKILL.md "4-tuple sub-tuple spawn 가이드" 단락 정합.

- **ArchitectAgent** (chief author, Opus — multi-source synthesizer) — deputy 산출물 + 나머지 3 sub-tuple 산출물 통합
- **CodebaseMapperAgent** (Sonnet — existing codebase fact)
- **RefactorAgent** (Sonnet — decoupling / pattern / interface 분리 advocacy 구조 3축 + repo-분해 구조 escalation. 측정 축(중복/재사용)은 구현 리팩터링 Story C 이관 — CFP-2539)
- **ArchitectAnalystAgent** (Sonnet) — 변경 전 기존 설계 (ADR / Change Plan / Story §3/§7/§11) 분석 단일 축

**flat spawn 의미**: Orchestrator 가 4 component 모두 평행 spawn. 재귀 spawn 금지 / nested team 금지 / sub-lead 격상 0건. 4-tuple = 어느 sub-agent 가 어느 deputy 영역 Context Packet 으로 spawn 됐는지를 표기하는 **논리적 그룹핑**일 뿐 **물리적 spawn 계층 (nested) 이 아니다**.

**InfraArchitect 신설 철회**: Docker-first + AWS 없음 환경 — InfraArchitect 미도입 결정. InfraOperationalArchitect 가 §7.4.6 Container considerations 영역 cover.

**DDDArchitect 신설 reject**: axis 미정합 (method / 학파 layer + ModuleArch wording overlap + consumer applicability 축소) — 미도입 결정.

## 4-way 이념 대립 (대립 참여 roster)

ArchitectPLAgent 가 SubAgent 를 **병렬 spawn**. 대립 참여 = CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ (DataArch 또는 ModuleArch). TestContract / InfraOperational / APIContract = single-mandate 단일 축 (대립 비참여). LiveOps / LiveOrdering = CONDITIONAL 단일 축 (대립 비참여).

- **RDB OLTP 영역 대립**: CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ ModuleArch (aggregate-level) (4-way)
- **빅데이터 OLAP 영역 대립**: CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ DataArch (4-way)
- **Cross-layer (ELT/ETL/CDC) 영역**: ModuleArch (aggregate-level) + DataArch co-author (deferred carrier)

**독립 관점 유지**: 모든 SubAgent 원 소스 (코드 + ADR + Change Plan 초안 + Story §1-7) 직접 읽기. 한쪽이 다른 쪽의 요약에 의존하지 않음.

**충돌 해소**: 관점 충돌 시 ArchitectAgent (chief author) 가 결정 근거와 함께 Change Plan §2 · §3 · §7 · §7.4 · §11 에 명시. **chief tie-break ladder 3 단계**: (1) RACI lookup → (2) ADR-068 invariant 적용 → (3) chief judgement + ADR Amendment carrier 발의.

**DesignReviewPL 교차 체크**: ArchitectAgent 통합 판정 + ArchitectPLAgent 검수가 각 변호 근거를 근거 있게 일축·수용했는가 / 요건 범위를 넘지 않았는가 / §7 보안 설계와 §7.4 운영 리스크와 §11 데이터 마이그레이션이 충실히 반영되었는가 / ModuleArch (aggregate-level) ↔ DataArch cross-layer boundary 명시했는가.

## RACI 3-way overlap zone (wrapper SSOT mirror)

> **wrapper canonical SSOT** = [`skills/deputy-mandate/SKILL.md`](https://github.com/mclayer/plugin-codeforge/blob/main/skills/deputy-mandate/SKILL.md) `## RACI 표준 row 형식 (3-way overlap zone body)` 단락. 9-cell matrix (3 sub-axis × 3 cross-axis: Security/InfraOp/TestContract × DataOLAP/Module/APIContract) + 4-column R/A/C/I 정의 + cell selection heuristic 은 wrapper skill 이 canonical. 본 단락 = chief tie-break ladder 1단계 (RACI lookup) 입력 pointer. single-axis 결정은 wrapper `6+3+1 primary axis matrix` 직접 lookup.

**Cell 3.3 예외** (TestContract × APIContract): `R = APIContractArch` (primary, §8.6 contract testing primary axis 정합) / `C = TestContractArch` (CI placement + orchestration). contract format ≠ CI placement disjoint axis.

## Sub-agent fan-out (ArchitectPL → 6 permanent + 3+1 CONDITIONAL SubAgent 병렬 + 4-tuple sub-tuple)

| Deputy / Component | Spawn 시점 | 산출물 → chief author 통합 위치 |
|---|---|---|
| CodebaseMapperAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §2 현재 구조 |
| RefactorAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §3 도입할 설계 (refactor 시각 — decoupling / pattern / interface 분리 구조 3축) + §6 (repo-분해 구조 advocacy, escalation-tier — 경계 확정: repo-level 분해=ArchitectAgent chief authority, module/aggregate-level=ModuleArch authority). 측정 축(중복제거·공통추출)은 구현 리팩터링 Story C 이관 (CFP-2539) |
| ArchitectAnalystAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §2 (변경 전 기존 설계 컨텍스트) |
| SecurityArchitectAgent (deputy) | 설계 lane 진입 즉시 | §7.1-§7.3, §7.5-§7.7 보안 설계 |
| **DataArchitectAgent** (deputy) | 설계 lane 진입 즉시 | **§3 빅데이터 OLAP (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계) + §11 OLAP schema 진화 / OLAP rollback / OLAP integrity invariant** |
| **APIContractArchitectAgent** (deputy) | 설계 lane 진입 즉시 | **§3 API contract (REST/GraphQL/gRPC/WebSocket + versioning + DTO + OpenAPI/GraphQL) + §8 contract testing (Pact 등)** |
| TestContractArchitectAgent (deputy) | 설계 lane 진입 즉시 | §8 Test Contract (**Epic 소속 Story 시 §8.6에 `story_key: <KEY>`, `suite: "story"` 필수**) |
| **InfraOperationalArchitectAgent** (deputy) | 설계 lane 진입 즉시 | **§7.4 운영 리스크 6 항목 + §11.6 idempotency consult (ModuleArch aggregate-level primary 영역 협업)** |
| **ModuleArchitectAgent** (deputy — AggregateArch 통합 흡수) | 설계 lane 진입 즉시 (aggregate-level 영역 = CONDITIONAL applicability `project.yaml aggregate_arch.applicable` 확인) | **§3 code boundary axis: module-level (module boundary + dependency direction + layered/hexagonal/clean + DDD bounded context module placement) + aggregate-level (DDD aggregate boundary + 트랜잭션 경계 + persistence-bound, CONDITIONAL) + §11.1-§11.6 RDB OLTP (Alembic 정책 7 원칙: 양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit)** |
| **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만) | ArchitectPL 의 §13 CONDITIONAL trigger 검토 후 spawn | **§13 Live Operational Discipline (operator approval / kill switch / incident response / OperationEvent audit) + §7.5 (live API key) consult** |
| **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만) | ArchitectPL 의 §13 CONDITIONAL trigger 검토 후 spawn | **§11 Ledger reconcile / partial fill / fee invariant + §8.5 (order replay) + §11.6 idempotency (order side) consult** |

ArchitectPLAgent prompt:
- **Backtest/Paper-only Story (default, ModuleArch aggregate-level applicable=true)**: "6 permanent deputy 병렬 spawn (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch / APIContractArch) + 3 4-tuple sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst) flat spawn (ArchitectAgent chief 포함). ArchitectAgent (chief author) 가 9 (6 + 3 sub-tuple) 산출물 통합 후 Change Plan §1-§13 author. ModuleArch = boundary axis (module-level + aggregate-level RDB OLTP) 통합 산출."
- **Frontend-only / API-only / external-managed consumer (`project.yaml aggregate_arch.applicable: false`)**: "ModuleArch aggregate-level 영역 N/A (module-level 영역 retain — 항상 spawn). 6 permanent deputy + 3 sub-tuple = 9 산출물 통합 (ModuleArch 산출물 = module-level only)."
- **Live touching Story (CONDITIONAL active)**: "위 + LiveOpsDeputy + LiveOrderingDeputy spawn. ArchitectAgent chief 가 11 산출물 통합 후 Change Plan §1-§13 + Story §13 author."

CONDITIONAL trigger 판정 (ArchitectPL 의 의무):
- ModuleArch aggregate-level applicability: consumer `project.yaml aggregate_arch.applicable: bool` 확인 (default `true`). 미정의 시 `true` 가정. frontend-only / API-only / external-managed RDB consumer 만 `false` (ModuleArch 항상 spawn — aggregate-level 영역만 conditional, module-level 영역 무조건)
- Live touching: Story 가 real funds / live exchange API / production credential / live order placement 중 하나 이상 touching 인지 검토
- Production cutover: Change Plan §13 `production_cutover_touching: true` 선언 OR §13 Live Operational Discipline 본문 보유. wrapper-self-app N/A
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

- ADR-008 — Inter-plugin contract versioning (design-output v1 → v2 BREAKING bump)
- ADR-009 — Wrapper-only decomposition (ζ arc parent)
- ADR-010 — Inter-plugin contract sibling sync (design-output v2)
- ADR-012 — Wrapper CLAUDE.md SSOT boundary (§3 4번째 예외 = operational risk / decision row / mandate 경계)
- ADR-014 (+Amd 4) — §7.4 schema SSOT, OperationalRiskArch → InfraOperationalArch rename + §7.4 primary/shell 분류 + ProductionEvidence dual-spawn disjoint axis
- ADR-042 (+Amd 7/8) — design lane agent model tier SSOT + roster 재편 (APIContractArch/ModuleArch 등 + DataArch mandate 축소 + InfraArchitect·DDDArchitect 신설 reject)
- ADR-044 — Phase-scoped sequential team (flat spawn / nested team·재귀 spawn·sub-lead 격상 금지)
- ADR-068 (+Amd 2) — Boundary completeness invariants + chief tie-break ladder 3 단계 (RACI → invariant → judgement+Amendment)
- ADR-72 — ProductionEvidenceDeputy + Epic cutover gate (ADR-088 §결정 4 로 codeforge-deploy-review 이관 완료 — 본 lane spawn 0, CFP-2170 design 본 파일 삭제)
- ADR-078 — Living architecture doc SSOT (`docs/architecture/codeforge-design.md` 갱신 의무)
- ADR-086 — Deputy 신설 결정 framework P7 (axis 분석 + 5-checklist self-application). agent file 신설/rename/축소 모두 self-application 의무.

## Dogfood policy (CFP-45)

본 plugin repo 는 runtime SSOT 만 보유. dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 단일 monorepo SSOT. 본 plugin 폴더는 `codeforge-internal-docs/design/`. 상세 정책 + Story workflow 흐름은 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) canonical SSOT 참조 + [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (PR-I 머지 후 Adopted).

Plugin repo 측 GitHub Issue 와 internal-docs 측 Story file 의 binding:
- Issue body frontmatter: `story_uri: <internal-docs URL>`
- Story file frontmatter: `story_issues: [{repo: "mclayer/plugin-codeforge", number: <N>}]`
- `.github/workflows/phase-gate-mergeable.yml` (본 repo) 가 cross-repo Story fetch via GitHub App
