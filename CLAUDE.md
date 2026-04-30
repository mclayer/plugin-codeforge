# CLAUDE.md (codeforge-design)

codeforge ζ arc Design lane plugin (LAST extraction). 8 agent + change-plan/adr templates.

## Plugin position

codeforge core (>= 5.0.0) 의존.

## Inter-plugin contracts

- `design_output v1` — [`docs/inter-plugin-contracts/design-output-v1.md`](docs/inter-plugin-contracts/design-output-v1.md)
  - **CFP-46 PR-E 머지 후 v2 로 BREAKING bump 예정** (§7.4 운영 리스크 5 sub-item + §11 idempotency CONDITIONAL + 6 deputy 산출물 통합 표 추가). 현 placeholder 유지.

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

## 4-way 이념 대립 — 6 deputy 의 독립 관점

**deputy 수 = 6, 이념 대립 축 = 4-way (Mapper ↔ Refactor ↔ SecurityArch ↔ DataMigrationArch). TestContractArch / OpRiskArch 는 contributor / production-readiness 단일 축 — 대립 비참여.**

ArchitectPLAgent 가 6 deputy 를 **병렬 spawn** — 넷은 4-way 이념 대립 (Mapper ↔ Refactor ↔ SecurityArch ↔ DataMigrationArch), TestContractArch 는 §8 author input contributor (대립 비참여), OperationalRiskArch 는 production-readiness 단일 축 contributor (대립 비참여 — ADR-014).

| Deputy | 입장 | 핵심 질문 |
|---|---|---|
| **CodebaseMapperAgent** | 보수 — as-is 변호자 | "기존 패턴 유지, 변경 영향 최소화" |
| **RefactorAgent** | 혁신 — to-be 옹호자 | "결합도 감소, 인터페이스 분리, 패턴화" |
| **SecurityArchitectAgent** | 위협 — 공격자 관점 | "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가" |
| **DataMigrationArchitectAgent** | 데이터 무결성 — 변호자 | "schema 가 어떻게 변하는가, 기존 데이터는 어떻게 처리되는가, 실패 시 어떻게 복구하는가" |
| TestContractArchitectAgent | QA perspective contributor | §8 커버리지 후보·경계·invariant — 대립 비참여 |
| **OperationalRiskArchitectAgent** | 운영 리스크 — production-readiness 변호자 (ADR-014) | "끊겼을 때·실패했을 때·과부하일 때 어떻게 되는가, 스테이징/프로덕션 누설 차단되는가" |

**독립 관점 유지**: 6 deputy 모두 원 소스 (코드 + ADR + Change Plan 초안 + Story §1-7) 직접 읽기. 한쪽이 다른 쪽의 요약에 의존하지 않음 — 서로 산출물에 오염되지 않도록 독립.

**충돌 해소**: 4 관점 충돌 시 ArchitectAgent (chief author) 가 결정 근거와 함께 Change Plan §2 (현재 구조) · §3 (도입할 설계) · §7 (보안 설계) · §7.4 (운영 리스크) · §11 (데이터 마이그레이션) 에 명시. 수용·반박은 chief author 가 조정 후 기록 (deputy 간 상호 대응 방식 아님). ArchitectPLAgent 는 통합 결과 검수.

**DesignReviewPL 교차 체크**: ArchitectAgent 통합 판정 + ArchitectPLAgent 검수가 각 변호 근거를 근거 있게 일축·수용했는가 / 요건 범위를 넘지 않았는가 / §7 보안 설계와 §7.4 운영 리스크와 §11 데이터 마이그레이션이 충실히 반영되었는가 — 병렬 모델에서는 deputy 간 상호 대응하지 않으므로, 대립 해소 품질 평가는 chief author + PL 통합 결과 대상.

## Sub-agent fan-out (ArchitectPL → 6 deputy 병렬)

| Deputy | Spawn 시점 | 산출물 → chief author 통합 위치 |
|---|---|---|
| CodebaseMapperAgent | 설계 lane 진입 즉시 | §2 현재 구조 |
| RefactorAgent | 설계 lane 진입 즉시 | §3 도입할 설계 (refactor 시각) |
| SecurityArchitectAgent | 설계 lane 진입 즉시 | §7.1-§7.3, §7.5-§7.7 보안 설계 |
| DataMigrationArchitectAgent | 설계 lane 진입 즉시 | §11.1-§11.5 데이터 마이그레이션 |
| TestContractArchitectAgent | 설계 lane 진입 즉시 | §8 Test Contract |
| **OperationalRiskArchitectAgent** | 설계 lane 진입 즉시 (CFP-46) | **§7.4 운영 리스크 + §11.6 idempotency consult** |

ArchitectPLAgent prompt: "6 deputy 병렬 spawn — CodebaseMapper / Refactor / SecurityArch / DataMigrationArch / TestContractArch / **OperationalRiskArch** 각자 독립 관점. ArchitectAgent (chief author) 가 6 산출물 통합 후 Change Plan §1-§11 author."

## ArchitectPLAgent 라이프사이클 (stateless 재스폰)

- 매 트리거마다 Orchestrator 가 신규 spawn — 세션 유지 없음
- Story file §1-8 재로딩으로 컨텍스트 복원
- 토큰 비용: 재스폰 당 ~5-10k tokens. FIX 3회 가정 시 15-30k overhead ([codeforge wrapper playbook §8](https://github.com/mclayer/plugin-codeforge/blob/main/docs/orchestrator-playbook.md) 참조). 6 deputy 통합 token cost ~5-10k 추가 (ADR-014).
- **ArchitectAgent (chief author)** 도 각 설계 lane 진입마다 stateless 재스폰 — 6 deputy 산출물 입력 수령 후 Change Plan §1-§11 author. ArchitectPLAgent RETURN 시에도 재스폰

## 설계 lane Deputy Freshness

모든 deputy (CodebaseMapperAgent · RefactorAgent · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent · **OperationalRiskArchitectAgent**) 공통:
- **매 설계 lane 진입 시 재스폰** (이전 Story 산출물 재사용 금지)
- 리뷰·테스트에서 설계 lane 복귀 시에도 재스폰 (구현 lane 에서 코드 변경 전제)
- base_sha / scope_paths frontmatter 갱신 의무

## 관련 ADR

- ADR-008 (Inter-plugin Contract Versioning) — design-output v1 → v2 BREAKING bump (CFP-46 PR-E)
- ADR-009 (Wrapper-only Decomposition) — ζ arc parent (5 deputy 구조 출처)
- ADR-010 (Inter-plugin Contract Sibling Sync) — design-output v2 sibling sync
- ADR-012 (Wrapper CLAUDE.md SSOT Boundary) — §3 4번째 예외 (operational risk 매트릭스 / decision row / mandate 경계)
- **ADR-014** (Operational Risk SSOT Distribution) — 본 plugin §7.4 schema SSOT, OperationalRiskArchitect 6번째 deputy 결정

## Dogfood policy (CFP-45)

본 plugin repo 는 runtime SSOT 만 보유. dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 단일 monorepo SSOT. 본 plugin 폴더는 `codeforge-internal-docs/design/`. 상세 정책 + Story workflow 흐름은 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) canonical SSOT 참조 + [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (PR-I 머지 후 Adopted).

Plugin repo 측 GitHub Issue 와 internal-docs 측 Story file 의 binding:
- Issue body frontmatter: `story_uri: <internal-docs URL>`
- Story file frontmatter: `story_issues: [{repo: "mclayer/plugin-codeforge-design", number: <N>}]`
- `.github/workflows/phase-gate-mergeable.yml` (본 repo) 가 cross-repo Story fetch via GitHub App
