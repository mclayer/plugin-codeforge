# CLAUDE.md (codeforge-design)

codeforge ζ arc Design lane plugin (LAST extraction). 5 permanent + 3 CONDITIONAL SubAgent + change-plan/adr templates.

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

## 5 permanent + 3 CONDITIONAL SubAgent + 4-tuple sub-tuple (CFP-1026 — ADR-042 Amendment 7 / ADR-014 Amendment 4 / ADR-44 / ADR-72)

**SubAgent 수 = 5 permanent + 3 CONDITIONAL + 4-tuple sub-tuple**. wrapper SSOT (CLAUDE.md "Deputy mandate 매트릭스" L229-233 / skills/deputy-mandate/SKILL.md "5 permanent + 3 CONDITIONAL") 와 byte-consistent.

**5 permanent deputy** (모든 설계 lane 진입 시 병렬 spawn):

| Deputy | 입장 | 핵심 질문 | model tier |
|---|---|---|---|
| **SecurityArchitectAgent** | 위협 — 공격자 관점 | "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가" | Opus |
| **InfraOperationalArchitectAgent** (CFP-1026 S1 rename, OperationalRiskArch → Infra...) | 운영 리스크 + infra — production-readiness 변호자 | "끊겼을 때·실패했을 때·과부하일 때 어떻게 되는가, 스테이징/프로덕션 누설 차단되는가" | Opus |
| **TestContractArchitectAgent** | QA perspective contributor | §8 커버리지 후보·경계·invariant — 대립 비참여. **Epic 소속 Story 시 §8.6에 `story_key: <KEY>` + `suite: "story"` 필수** (IntegrationTestAgent Story Suite 자동 생성 연동 — CFP-371 / ADR-055 Amendment 2) | Opus |
| **DataArchitectAgent** (CFP-1026 S1 rename, DataMigrationArch → Data... + mandate 확장) | 데이터 무결성 + 전체 데이터 구조 — 변호자 | "schema 가 어떻게 변하는가, 기존 데이터는 어떻게 처리되는가, 실패 시 어떻게 복구하는가" + "entity / aggregate / persistence model / 데이터 흐름 어떻게 설계하는가" | Opus |
| **CodeArchitectAgent** (CFP-1026 S1 신설) | §3 code 구조 advocate — single-mandate | "layered / hexagonal / clean / DDD bounded context / module boundary / dependency direction 어떻게 정합인가" | Sonnet |

**3 CONDITIONAL deputy** (Story trigger 충족 시 추가 spawn):

| Deputy | trigger 조건 | 핵심 질문 |
|---|---|---|
| **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | real funds / live exchange API / production credential / live order placement 1+ touching | "operator approval / kill switch / incident response 가 충족되는가, OperationEvent audit trail 이 보존되는가" |
| **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | LiveOps 동일 trigger | "order submit / partial fill / cancel race / rejection mapping / ledger reconcile invariant 이 정합인가" |
| **ProductionEvidenceDeputy** (CONDITIONAL — production cutover Story 만, ADR-72) | Change Plan §13 `production_cutover_touching: true` 선언 OR §13 Live Operational Discipline 본문 보유. wrapper-self-app N/A (ADR-72 §결정 6) | "production evidence quad (functional / security / monitoring / testing) 4 source 충족하는가, EPIC CLOSED gate evidence 정합인가, Family 7 atomic canary pin length_invariant=7 정합인가" |

## 4-tuple sub-tuple (deputy 아님 — ADR-044 CFP-676 reaffirm)

**4-tuple = 논리적 그룹핑** (deputy column 아님, flat spawn 패턴). wrapper SKILL.md "4-tuple sub-tuple spawn 가이드" 단락 정합.

- **ArchitectAgent** (chief author, Opus — multi-source synthesizer) — deputy 산출물 + 나머지 3 sub-tuple 산출물 통합
- **CodebaseMapperAgent** (Sonnet — existing codebase fact)
- **RefactorAgent** (Sonnet — decoupling / pattern advocacy)
- **ArchitectAnalystAgent** (Sonnet, CFP-1026 S1 신설 — PriorArtAgent conceptual rename, file move 0) — 변경 전 기존 설계 (ADR / Change Plan / Story §3/§7/§11) 분석 단일 축

**flat spawn 의미**: Orchestrator 가 4 component 모두 평행 spawn. 재귀 spawn 금지 (platform inherent) / nested team 금지 (ADR-044) / sub-lead 격상 0건 (ADR-009 §결정 1 + ADR-039 정합). 4-tuple = 어느 sub-agent 가 어느 deputy 영역 Context Packet 으로 spawn 됐는지를 표기하는 **논리적 그룹핑**일 뿐 **물리적 spawn 계층 (nested) 이 아니다**.

**InfraArchitect 신설 철회** (CFP-1026 S1 — ADR-042 Amendment 7 SSOT): Docker-first + AWS 없음 환경 — InfraArchitect 미도입 결정. InfraOperationalArchitect 가 §7.4.6 Container considerations 영역 cover.

## 4-way 이념 대립 (5 permanent 중 대립 참여 4)

ArchitectPLAgent 가 5 (또는 8/9) SubAgent 를 **병렬 spawn**. 대립 참여 = CodebaseMapper (4-tuple) ↔ Refactor (4-tuple) ↔ SecurityArch ↔ DataArch. TestContractArch / InfraOperationalArch / CodeArch = single-mandate advocacy / contributor 단일 축 — 대립 비참여. LiveOps / LiveOrdering / ProductionEvidence = CONDITIONAL contributor 단일 축 — 대립 비참여.

**독립 관점 유지**: 모든 SubAgent 원 소스 (코드 + ADR + Change Plan 초안 + Story §1-7) 직접 읽기. 한쪽이 다른 쪽의 요약에 의존하지 않음.

**충돌 해소**: 관점 충돌 시 ArchitectAgent (chief author) 가 결정 근거와 함께 Change Plan §2 (현재 구조) · §3 (도입할 설계 — code + data) · §7 (보안 설계) · §7.4 (운영 리스크) · §11 (데이터 마이그레이션 + 전체 데이터 구조) 에 명시.

**DesignReviewPL 교차 체크**: ArchitectAgent 통합 판정 + ArchitectPLAgent 검수가 각 변호 근거를 근거 있게 일축·수용했는가 / 요건 범위를 넘지 않았는가 / §7 보안 설계와 §7.4 운영 리스크와 §11 데이터 마이그레이션이 충실히 반영되었는가.

## Sub-agent fan-out (ArchitectPL → 5 permanent + 3 CONDITIONAL SubAgent 병렬 + 4-tuple sub-tuple)

| Deputy / Component | Spawn 시점 | 산출물 → chief author 통합 위치 |
|---|---|---|
| CodebaseMapperAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §2 현재 구조 |
| RefactorAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §3 도입할 설계 (refactor 시각) + §6 |
| ArchitectAnalystAgent (4-tuple sub-tuple) | 설계 lane 진입 즉시 | §2 (변경 전 기존 설계 컨텍스트) |
| SecurityArchitectAgent (deputy) | 설계 lane 진입 즉시 | §7.1-§7.3, §7.5-§7.7 보안 설계 |
| DataArchitectAgent (deputy) | 설계 lane 진입 즉시 | §3 data (entity / aggregate / VO / persistence / 데이터 흐름) + §11.1-§11.6 데이터 마이그레이션 |
| TestContractArchitectAgent (deputy) | 설계 lane 진입 즉시 | §8 Test Contract (**Epic 소속 Story 시 §8.6에 `story_key: <KEY>`, `suite: "story"` 필수**) |
| **InfraOperationalArchitectAgent** (deputy, CFP-1026 S1 rename) | 설계 lane 진입 즉시 | **§7.4 운영 리스크 6 항목 + §11.6 idempotency consult** |
| **CodeArchitectAgent** (deputy, CFP-1026 S1 신설) | 설계 lane 진입 즉시 | **§3 code (layered / hexagonal / clean / DDD / module boundary / dependency direction)** |
| **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | ArchitectPL 의 §13 CONDITIONAL trigger 검토 후 spawn | **§13 Live Operational Discipline (operator approval / kill switch / incident response / OperationEvent audit) + §7.5 (live API key) consult** |
| **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만, CFP-77) | ArchitectPL 의 §13 CONDITIONAL trigger 검토 후 spawn | **§11 Ledger reconcile / partial fill / fee invariant + §8.5 (order replay) + §11.6 idempotency (order side) consult** |
| **ProductionEvidenceDeputy** (CONDITIONAL — production cutover Story 만, ADR-72) | ArchitectPL 의 §13 production_cutover trigger 검토 후 spawn (wrapper-self-app N/A) | **§13 Production Evidence Quad (MS-1 live_touching / MS-2 production_cutover_touching dual-source AND / MS-3 marketplace_publish_touching / MS-4 consumer_impact_blast_radius) + EPIC CLOSED gate + post-cutover wiring + Family 7 atomic canary pin** |

ArchitectPLAgent prompt:
- **Backtest/Paper-only Story (default)**: "5 permanent deputy 병렬 spawn (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / CodeArch) + 3 4-tuple sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst) flat spawn (ArchitectAgent chief 포함). ArchitectAgent (chief author) 가 8 (5 + 3 sub-tuple) 산출물 통합 후 Change Plan §1-§13 author."
- **Live touching Story (CFP-77 CONDITIONAL active)**: "위 + LiveOpsDeputy + LiveOrderingDeputy spawn. ArchitectAgent chief 가 10 산출물 통합 후 Change Plan §1-§13 + Story §13 author."
- **Production cutover Story (ADR-72 CONDITIONAL active)**: "위 + ProductionEvidenceDeputy spawn (wrapper-self-app N/A 시 미spawn). ArchitectAgent chief 가 11 산출물 통합."

CONDITIONAL trigger 판정 (ArchitectPL 의 의무):
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
- ADR-042 (Agent model selection policy) + **Amendment 7** (CFP-676 / S1) — design lane agent 구조 재편 model tier SSOT (CodeArchitect / ArchitectAnalyst Sonnet 신설 + DataArchitect / InfraOperationalArchitect rename Opus 유지 + InfraArchitect 신설 철회)
- ADR-044 (Phase-scoped sequential team) — flat spawn / nested team 금지 / 재귀 spawn 금지 / sub-lead 격상 0건 (CFP-676 reaffirm 단락)
- **ADR-72** (ProductionEvidenceDeputy + Epic cutover gate) — CONDITIONAL deputy 3번째 (production cutover Story 만)
- ADR-078 (Living architecture doc SSOT) — `docs/architecture/codeforge-design.md` 본 doc 영역 갱신 의무 (CFP-969)

## Dogfood policy (CFP-45)

본 plugin repo 는 runtime SSOT 만 보유. dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 단일 monorepo SSOT. 본 plugin 폴더는 `codeforge-internal-docs/design/`. 상세 정책 + Story workflow 흐름은 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) canonical SSOT 참조 + [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (PR-I 머지 후 Adopted).

Plugin repo 측 GitHub Issue 와 internal-docs 측 Story file 의 binding:
- Issue body frontmatter: `story_uri: <internal-docs URL>`
- Story file frontmatter: `story_issues: [{repo: "mclayer/plugin-codeforge-design", number: <N>}]`
- `.github/workflows/phase-gate-mergeable.yml` (본 repo) 가 cross-repo Story fetch via GitHub App
