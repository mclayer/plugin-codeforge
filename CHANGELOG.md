# Changelog

`codeforge-design` plugin 릴리스 이력.

## [0.12.1] - 2026-05-16

### Changed (CFP-751 Phase 2 sibling — deputy 일반 명사 → SubAgent sweep, ADR-010 paired sync)

- **13 file / 142 mechanical replacements** — `docs/**` + `CLAUDE.md` + `agents/**` + `templates/**` 영역의 lowercase 일반 명사 `deputy` → `SubAgent`. wrapper carrier `mclayer/plugin-codeforge` Phase 2 PR ADR-080 §결정 1-2 sibling sync (ADR-010 §결정 2 paired ordering).
- **Class-B 보존 verified** — 6 `*DeputyAgent` cross-refs (LiveOpsDeputyAgent / LiveOrderingDeputyAgent CamelCase identifiers + filename preservation) / 17 `Deputy` capitalized concept. agent files (`agents/*DeputyAgent.md`) 본문 lowercase 일반 명사만 swept, identifier 0 변경.
- **`.claude-plugin/plugin.json`** — 0.12.0 → 0.12.1 PATCH (doc-only mirror sync — ADR-037 PATCH 결정). marketplace atomic sync 동반 (ADR-063).

## [0.12.0] - 2026-05-14

### Added

- `design-output-v2` contract v2.2 → v2.3 MINOR — `chief_author_artifact.spec_invariant_measurement_required: bool` field 신설 (CFP-662 / Issue mclayer/plugin-codeforge#669, Epic CFP-620 sibling, codeforge-develop PR #25 canonical 정합, doc-only fast-path ADR-054).

## [0.11.0] - 2026-05-13

### CFP-582 — ADR-059 Amendment 2 / debate-protocol-v1 v1.2 sibling sync — Blanket Adversarial Debate Trigger (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge CFP-582 — Wave 4 ADR-059 Amendment 2) 의 canonical sibling sync. DesignLane cross-module Story 진입 시 adversarial debate 자동 발동.

### CFP-597 — ArchitectAgent §5.7 marketplace sync proactive self-check trigger (ADR-063 Amendment 1)

ArchitectAgent Phase 1 산출물 commit 직전 plugin.json mirrored field diff 감지 + Change Plan §13 declarative declare 의무화. review-verdict-v4 v4.5 `marketplace_sync_declared` optional bool field 정합.

#### Changed (CFP-582)

- `agents/ArchitectPLAgent.md` — `Phase 0.5: Blanket Adversarial Debate Trigger` 섹션 신설

#### Added (CFP-597)

- `agents/ArchitectAgent.md` — `§5.7 Marketplace sync proactive self-check trigger (ADR-063 Amendment 1 / CFP-597)` 섹션 신설
- `templates/change-plan.md` — §13.N Marketplace sync self-check sub-row schema 추가

#### Compatibility

- **Wire**: agent prompt block 신설. 기존 동작 single-module Story 불변.
- **marketplace sync**: mclayer/marketplace#91 (merged 선행 — ADR-063 §결정 2 ordering).

## [0.10.0] - 2026-05-13

### CFP-528 — ADR-068 Amendment 1 I-5 dimensional empirical grounding self-check sibling sync (Wave 2B sibling, MINOR)

ADR-068 Amendment 1 (wrapper plugin-codeforge) sibling 적용 — Wave 2B carrier. ArchitectAgent (chief author) §3 / §7 작성 시 10 dimension enum quantitative parameter (latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count) 마다 `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 의무화. #319 RETRO-MCT-104 carrier (WS push interval 30s 가정 → 실측 200ms, 150x 오류) failure-class super-class 차단.

#### Added

- `agents/ArchitectAgent.md` — `§5.6.1 Phase 1 commit-time dimensional empirical grounding self-check (ADR-068 Amendment 1 / CFP-528 — Wave 2B 신설)` 섹션 신설:
  - 10 dimension enum (latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count)
  - Trigger 4종 (empirical-absent default / synthetic guess / industry-assumption transplant / legacy inertia)
  - Mitigation 4종 (empirical-first / explicit TBD 박제 / range-bound default / dimensional checklist)
  - Justification 조건 (well-defined SLA / standardized protocol RFC / vendor doc explicit guarantee 3종 부재 시 의무)
  - Exemption (Story §1 명시 선언)
  - Verification format = empirical-source-annotation (value / unit / empirical_source 3-key)
  - PASS / NA / FAIL 분류 + Change Plan §13 C 항목 명시 의무 + verdict packet forward 의무
  - ADR-065 §5.5 + ADR-068 §5.6 와 disjoint — 3 boolean field 동시 PASS 의무
- `agents/ArchitectPLAgent.md` — `Phase 3.6: Dimensional empirical grounding cross-validate (ADR-068 Amendment 1 — CFP-528)` 섹션 신설:
  - `dimensional_empirical_self_check_passed: bool` (review-verdict-v4 v4.4 schema MINOR optional field) forward 의무
  - false 시 FIX 처리 절차 (`pl_recommendation: FIX` + findings[] dimensional-empirical-gap row each + ArchitectAgent re-spawn)
  - DesignReviewPL (Tier B) + CodeReviewPL (Tier C) dual-binding 정합
  - 3 boolean field (`mechanical_self_check_passed` / `boundary_completeness_self_check_passed` / `dimensional_empirical_self_check_passed`) 셋 모두 true 일 때만 Phase 1 commit

#### Changed

- `.claude-plugin/plugin.json` — version 0.9.1 → 0.10.0 MINOR (agent definition schema 변경, ADR-037 정합). description CFP-528 entry append.

#### Sibling sync

- Source carrier: mclayer/plugin-codeforge#575 (CFP-528 Wave 2B, ADR-068 Amendment 1)
- Canonical contract: mclayer/plugin-codeforge-review#31 (review-verdict-v4 v4.4 + review-pl-base §3 I-5 rule)
- ADR-010 §4 sibling sync follow-up (wrapper merge 후, canonical 영역 = review-verdict-v4 in codeforge-review)

#### Why

#319 RETRO-MCT-104 dimensional extension anti-pattern (WS push interval 30s 가정 → 실측 200ms, 150x 오류) systemic super-class 차단. authoring-time enforce (Tier A, design lane) — DesignReview (Tier B) + CodeReview (Tier C) cross-lane dual-binding 의 첫 layer. 10 dimension enum + empirical-source-annotation verification format 으로 ArchitectAgent §3/§7 quantitative decision 모두 evidence-backed 강제.

#### Cross-ref

- Wrapper SSOT: [ADR-068 Amendment 1](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-068-boundary-completeness-invariants.md)
- Wrapper Phase 1 PR (MERGED): https://github.com/mclayer/plugin-codeforge/pull/575
- Canonical sibling sync: plugin-codeforge-review review-verdict-v4 v4.4 MINOR bump (#31 MERGED)

## [0.9.1] - 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection. CFP-438 4 PR merge 시 codeforge-review/design 에서 `phase-gate-mergeable` required check name mismatch ACTION_REQUIRED 실증 → branch protection 임시 변경 / 복원 우회 패턴 발생.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. drift 1건 (CFP-499 `isSiblingPr` 조건 누락) 해소.

#### Why

ADR-010 sibling sync 의무. wrapper Story 가 sibling repo 에 mechanical mirror sync PR 생성 시 sibling-pr label fast-pass 활성. 본 sibling repo PR 도 사용 가능 (Story §8 self-app — eat-own-dogfood).

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier (현재 scope 외).

## [0.9.0] - 2026-05-13

### CFP-438 — ArchitectAgent Phase 1 commit-time mechanical sync self-check + verdict packet schema (MINOR)

ADR-065 (wrapper plugin-codeforge) sibling 적용. ArchitectAgent (chief author) Phase 1 산출물 commit 직전 7-item mechanical sync self-check 의무화 — CFP-393 iter 1 3건 + iter 3 1건 + CFP-411 phase-gate path 결함의 root cause (사전 정의된 checklist 부재) 해소. marketplace 영역 self-check 는 ADR-063 SSOT (cross-ref only, 중복 codification 회피).

#### Added

- `agents/ArchitectAgent.md` — `§5.5 Phase 1 commit-time mechanical sync self-check (ADR-065 / CFP-438 — non-marketplace 영역)` 섹션 신설:
  - 7-item checklist (label-registry sync / doc-locations regen / workflow self-app / link target Phase 분배 / MANIFEST.yaml 갱신 / section-ownership row / doc-locations row)
  - 각 항목 PASS / NA / FAIL 분류 + Change Plan §13 명시 의무 + verdict packet forward 의무
  - CFP-378 §3.5 self-lint (input 표면 mechanical) 와 분리 — §5.5 = outer mechanical sync (Phase 1 산출물 commit 직전)
- `agents/ArchitectPLAgent.md` — `Phase 3.5: verdict packet 작성` 섹션 신설:
  - `mechanical_self_check_passed: bool` (review-verdict-v4 v4.2 schema MINOR optional field) forward 의무
  - false 시 FIX 처리 절차 (`pl_recommendation: FIX` + findings[] mechanical 누락 항목 each row + ArchitectAgent re-spawn)
  - 적용 lane: design lane 만 (code/security = omit 허용)
- `templates/change-plan.md` — `§13. Phase 1 산출물 self-check 결과 (ADR-065 / CFP-438 — non-marketplace 영역)` 섹션 신설:
  - 7-item 표 + Overall (`mechanical_self_check_passed: <true | false>`) 선언
  - chief author 가 commit 직전 결과 명시 의무

#### Changed

- `.claude-plugin/plugin.json` — version 0.8.0 → 0.9.0 MINOR (agent definition + template schema 변경, ADR-037 정합). description CFP-438 entry append.

#### Why

매 Story 마다 사후 CI lint fail 로 잡히는 mechanical sync 결함을 chief author 의 commit 직전 forcing function 으로 차단. 사전 정의된 checklist + Change Plan §13 표 + verdict packet explicit marker = 3-layer evidence trail. 7 항목 한정 (Change Plan 본문 변경 0건 영역만) — overhead 최소화. CFP-378 §3.5 (input 표면) 와 본 §5.5 (outer mechanical sync) 의 명시적 분리로 review-pl-base.md §3 P2 noise 증가 위험 mitigation.

#### Cross-ref

- Wrapper SSOT: [ADR-065](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-065-architect-phase1-mechanical-self-check.md)
- Wrapper PR (Phase 1, paired sibling): https://github.com/mclayer/plugin-codeforge/pulls
- Canonical sibling sync: plugin-codeforge-review review-verdict-v4 v4.2 MINOR bump

## [0.8.0] - 2026-05-12

### CFP-448 — CodebaseMapperAgent · RefactorAgent Opus → Sonnet rollback + mandate text 재정의 (MINOR)

ADR-057 Amendment 3 (wrapper plugin-codeforge PR #488 merged, 2026-05-12) selective rollback 의 sibling sync. CFP-379 (Amendment 4) 의 6 agent Opus 상향 중 본 lane plugin 의 2 agent (CodebaseMapperAgent / RefactorAgent) Sonnet 복귀 — ADR-042 §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 정합으로 mandate text 재정의 동시 산출물 의무 (CFP-448 §5.3 EC-9 tie-break 정합).

#### Changed

- `agents/CodebaseMapperAgent.md`:
  - `model:` field `claude-opus-4-7` → `claude-sonnet-4-6`
  - `description` frontmatter: "기존 코드베이스 변호자" → "기존 코드베이스 **사실** 변호자 — file structure / API surface / 의존성 그래프 등 명시적 fact source 만 인용. 추론·해석·synthesis 금지 (chief author 영역)"
  - 본문 신규 section "## Mandate boundary (Sonnet tier 정합 — ADR-057 Amendment 3 / ADR-042 Amendment 5)" 추가:
    - **허용 영역**: file structure / API surface / 의존성 그래프 / git blame·log / 기존 ADR / 현재 패턴 — 모두 명시적 fact source 인용만
    - **금지 영역**: 추론·해석·synthesis (chief author) / to-be 설계 (Refactor) / 보안 위협 (SecurityArch) / 데이터 무결성 (DataMigrationArch) / 운영 리스크 (OpRisk) / §7.4·§7.5·§11 mirror write
    - **Structured output template 의무**: fact-only template (`fact source citation` + `유지 근거 추적` + `변경 영향 지도`) — 자유 서술 / opinion / suggestion 금지
- `agents/RefactorAgent.md`:
  - `model:` field `claude-opus-4-7` → `claude-sonnet-4-6`
  - `description` frontmatter: "리팩터링 옹호자" → "리팩터링 옹호자 — **decoupling / pattern / 인터페이스 분리 3 카테고리** 안에서 advocacy. 카테고리 외 영역 (security / data integrity / op risk) 발화 금지 (해당 deputy 영역)"
  - 본문 신규 section "## Advocacy axis boundary (Sonnet tier 정합 — ADR-057 Amendment 3 / ADR-042 Amendment 5)" 추가:
    - **허용 advocacy 3 카테고리**: (a) Decoupling (b) Pattern (c) Interface separation — 표 형식으로 각 카테고리 핵심 1줄 + 산출물 형식 명시
    - **금지 영역**: security / data integrity / op risk / test contract / 요건 범위 외 advocacy / 추론 기반 fact 주장
    - **Structured output template 의무**: 3 카테고리 (a/b/c) 분류 형식 + 카테고리 외 영역 self-check 항목
- `.claude-plugin/plugin.json` — version 0.7.0 → 0.8.0 MINOR (mandate text 재정의 = agent definition signature 변경, ADR-037 정합). description CFP-448 entry append.

#### Why

axis-A (operational cost) — ADR-042 §결정 2 original Sonnet 분류 정합 회복. axis-B (mandate 깊이) — single-mandate advocacy pattern (CodebaseMapper = fact citation / Refactor = 3 카테고리 advocacy). CFP-379 Codex review finding (CodebaseMapper symbol resolution 정확도 / Refactor advocacy 품질) 은 mandate text 재정의 동시 산출물로 해소 (단순 model field downgrade 금지 — CFP-448 §5.3 EC-9 tie-break). axis-C (SSOT alignment) — CLAUDE.md L127 8종 정합 회복 (CL-6 사용자 확정 Option (i)).

#### Compatibility

- **Wire**: codeforge wrapper >= 5.22.1 (Phase 2 PR pair atomic — wrapper 5.22.1 + requirements 0.5.1 + 본 0.8.0 + Story §8 internal-docs).
- **Codex re-review**: **의무 (in-scope)** — Story §5.3 EC-2 정합. mandate text 재정의 후 Sonnet cover 가능성 검증 (Phase 2 PR Codex re-review = PASS, SUFFICIENT). FIX verdict 시 rollback reject + Opus 복귀 ADR carrier 발의 (현 PASS).
- **Backward compat**: agent prompt structure 자체 변경 (mandate boundary section 신규) — 기존 deputy spawn 절차 변경 0건. 5 deputy 병렬 스폰 + ArchitectAgent (chief author) 통합 패턴 정합 (CodebaseMapper fact-only output + Refactor 3 카테고리 output 가 통합 단계 입력으로 자연 부합).
- **ADR-053 재구동**: agent definition + mandate text 변경 = 구조적 변경. consumer 측 `/plugins install codeforge-design@mclayer` 의무.

## [0.7.0] - 2026-05-11

### CFP-387 / ADR-058 — ADR template sunset criteria + transitional 분류 frontmatter (MINOR)

Wrapper canonical ADR-058 (안전망 ADR 영구 부채화 차단) 의 cross-plugin Phase 2. ADR template canonical SSOT 갱신 — consumer-facing 의미 변경 → MINOR bump (ADR-037 룰).

### Added

- `templates/adr.md` frontmatter `is_transitional: true | false` 필드 (ADR-058 §결정 1 의무화) — 미선언 default `true` (안전망 추정, safe direction, §결정 4)
- `templates/adr.md` body `## 해소 기준` 섹션 (`## 결과` 직후 / `## 다이어그램 (선택)` 직전) — `is_transitional: true` 시 의무 / `false` 시 "N/A — permanent policy" 1줄
- 측정성 3-tuple (metric / who / how) 정량 명시 의무 — 모달 어휘 ("충분히 안정화되면", "임시로", "한시적", "until further notice") 금지
- frontmatter `amendments[]` schema — `sunset_justification` 필수 (ADR-058 §결정 5 ratchet 차단)
- 보안 ADR default presumption = `is_transitional: false` (ADR-058 §결정 7)
- 예시 3종 inline: (1) rate-limit 안전망 패턴 — ADR-057 fallback rate mirror / (2) platform SLA 발표 패턴 — 외부 신호 기반 / (3) full-rollout 완료 패턴 — 내부 milestone 기반

### Why

ADR-058 (wrapper canonical carrier, CFP-387) — 측정 기준 없는 영구 안전망 ADR 차단 forcing function. ADR-057 (Orchestrator Opus 필수화 + Sonnet→Opus fallback) 이 측정 기준 없는 영구 안전망으로 굳어지는 위험이 brainstorming (Opus×Codex 3라운드, 2026-05-11) 에서 식별 → 합의 원칙 5 "안전망 측정가능 종료" forcing function.

본 plugin = ADR template canonical SSOT — frontmatter + body schema 갱신 carrier.

### Compatibility

- **Wire**: codeforge >= 5.11.0 (sibling 동기 권장 — wrapper CLAUDE.md ADR 섹션 ADR-058 cross-ref 추가)
- **Template surface**: backward compatible — 기존 ADR 의 frontmatter 미선언 = default `true` 안전망 추정 (declaration only, mechanical enforcement 부재 = CFP-B 잠정 carrier)
- **Sibling sync**: wrapper repo `templates/adr.md` sibling 사본 0건 → canonical-only single source (ADR-010 sync 무발화)
- **Marketplace sync**: mirrored field 4종 (`name`/`version`/`description`/`author`) 중 `version` + `description` 변경 → marketplace sync PR 의무 (Phase 2 PR merge 직후, ADR-016)

### Cross-plugin coordination

- wrapper PR (Phase 2): `CLAUDE.md` ADR 섹션 + `plugin.json` 5.10.0 → 5.11.0 + `CHANGELOG.md`
- wrapper canonical ADR: `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` (Phase 1 PR #399 merged)
- Mode B hub-centralized (ADR-020 Amendment 1) — wrapper hub, codeforge-design worker plugin

## [0.4.0] - 2026-05-07

### CFP-128 / ADR-033 — Docker-first infra mandate sync (MINOR)

Wrapper canonical ADR-033 (amends ADR-014) 의 sibling sync. OpRiskArch agent + design-output-v2 contract 갱신.

### Added

- `agents/OperationalRiskArchitectAgent.md` §7.4.6 Container considerations (Docker-first infra orientation; deputy mandate 추가)
- `docs/inter-plugin-contracts/design-output-v2.md` `contract_version: 2.1 → 2.2` (additive minor — Container considerations field)

### Why

ADR-033 (CFP-128 carrier, wrapper canonical) — Docker-first infra orientation 을 OpRiskArch deputy mandate 에 명시 + design-output-v2 contract 에 surface. ADR-014 (OpRisk SSOT distribution) 의 amendment.

### Compatibility

- **Wire**: codeforge >= 5.0.0 (no break)
- **Contract version**: design-output-v2 2.1 → 2.2 (additive minor — backward compatible)
- **Sibling sync**: D2 PR #21 (commit fcf1666) merged

## [0.1.0] - 2026-04-29

### CFP-40 (codeforge ζ arc LAST) — Initial extraction (NEW)

codeforge ζ arc 마지막 lane plugin 추출 (parent §5.10). 7 agent + 2 templates (change-plan, adr).

### Added

- 7 agents 이전: ArchitectPLAgent, ArchitectAgent (chief author), CodebaseMapperAgent, RefactorAgent, SecurityArchitectAgent, TestContractArchitectAgent, DataMigrationArchitectAgent
- templates 이전: change-plan.md, adr.md
- docs/inter-plugin-contracts/design-output-v1.md (canonical)
- overlay/hooks/{regen-agents,session-start-deps-check}.sh
- README + CLAUDE.md

### Why

ζ arc §5.10: 가장 큰 표면 (5 deputies + chief + PL + 2 templates + Story §3/§7/§11 mirror + design review packet + FIX 재진입). Codex round 2 sequencing 권고 — 다른 5 plugin (review v2 + pmo + req + test + develop) 검증 후 마지막 진입으로 split-brain 위험 회피.

### Compatibility

- **Wire**: codeforge >= 5.0.0
- **Final extraction**: codeforge wrapper 가 본 PR 머지 후 agent 0개 (DocsAgent 동시 삭제) — wrapper-only 모델 완성
