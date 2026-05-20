---
adr_number: 42
title: Agent model selection policy — Opus / Sonnet / Haiku tier criteria
date: 2026-05-09
status: Accepted
category: governance
carrier_story: null
supersedes: []
amends: null
amendment_log:
  - amendment_id: 1
    date: 2026-05-09
    status: applied
    summary: "ResearcherAgent deferred fence resolved — mandate + model tier confirmed by ADR-046"
    ref: ADR-046
    carrier_story: "chore/researcher-role-redefinition (ADR-013 waiver)"
  - amendment_id: 2
    date: 2026-05-10
    status: applied
    summary: "Haiku 3번째 카테고리(mechanical pattern execution) 추가. InfraEngineerAgent·QADeveloperAgent·DataEngineerAgent Sonnet 4.6 → Haiku 4.5 pilot 전환. rollback 트리거 기준(30% FIX 증가/P0·P1 즉시) 및 governance 재-audit 트리거 규정."
    ref: null
    carrier_story: "cfp-360-haiku-pilot"
  - amendment_id: 3
    date: "2026-05-10"
    status: applied
    summary: "IntegrationTestAgent Sonnet tier 결정 (컴포넌트 경계 판단·외부 의존성 설계 포함)"
    ref: ADR-055
    carrier_story: cfp-367-integration-test-lane
  - amendment_id: 4
    date: "2026-05-11"
    status: applied
    summary: "Orchestrator Opus 필수화 + 6 agent Opus 상향 (FeasibilityAgent·ContinuityAgent·ChangeImpactAgent·CodebaseMapperAgent·RefactorAgent·DeveloperPLAgent Sonnet→Opus). §결정2 역전: CodebaseMapper·Refactor Opus 복원. ADR-057 carry."
    ref: ADR-057
    carrier_story: CFP-379
  - amendment_id: 5
    date: "2026-05-12"
    status: applied
    summary: "Selective rollback of Amendment 4 (3 of 6) — CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent Opus → Sonnet 복귀 (CodebaseMapper · Refactor 는 mandate text 재정의 동시 의무, DeveloperPL 은 사용자 framing verbatim + ADR-042 §결정 1 (b) implementation work 정합 회귀 — mandate 재정의 면제). FeasibilityAgent · ContinuityAgent · ChangeImpactAgent Opus 유지. ADR-057 Amendment 3 cross-ref atomic."
    ref: ADR-057
    carrier_story: CFP-448
    sunset_justification: "본 ADR 은 `is_transitional: false` (permanent policy carrier, frontmatter 정합) → Amendment 5 의 sunset_justification 은 `is_transitional: true` 인 ADR-057 의 §결정 3 selective rollback Amendment 3 의 cross-ref atomic 으로서 발화. ADR-058 §결정 5 self-application 은 ADR-057 Amendment 3 에서 1차 발화 (sunset_justification 의무 충족) → 본 row 는 ADR-042 정책 변경 0건 (결정 1 tier criteria + 결정 2 invariant + 결정 3 신규 agent ADR 의무 + 결정 4 inheritance + 결정 5 Haiku rollback + 결정 6 재-audit 모두 본문 변경 0건) 으로서 amendment_log 일관성 유지 + tier 표 갱신만 carry. 본 Amendment 5 는 ADR-042 §결정 2 invariant ('Sonnet 으로 fully cover 가능 = role 재정의 시그널') 의 정합 정합 검증 — CodebaseMapper / Refactor 의 mandate text 재정의 동시 산출물 의무 발화로 invariant 충족 (original §결정 2 Sonnet 분류 정합 복귀)."
  - amendment_id: 6
    date: "2026-05-16"
    status: applied
    summary: "DialogFidelityAgent 신규 entry 추가 (codeforge-pmo / Opus pilot tier / verifier-narrower mandate). §결정 2 invariant 적용 후 Sonnet 전환 가능 분기 명시."
    ref: ADR-071
    carrier_story: CFP-777
    sunset_justification: null
    affected_agents:
      - DialogFidelityAgent (new entry, codeforge-pmo)
  - amendment_id: 7
    date: "2026-05-19"
    status: applied
    summary: "CFP-1026 S1 ADR carrier 묶음 — design lane agent 구조 재편 model tier SSOT. CodeArchitectAgent 신설 (Sonnet, §결정 1 Sonnet (a) single-mandate advocacy — §3 code: layered/hexagonal/clean/DDD bounded context/module boundary/dependency direction) + ArchitectAnalystAgent 신설 (PriorArt rename, Sonnet, §결정 1 Sonnet (a) — 변경 전 ADR/Change Plan/Story 기존 설계 분석, 4-tuple sub-tuple component) + DataMigrationArchitectAgent → DataArchitectAgent rename + mandate 확장 (§3 data + §11 전체 데이터 구조: entity/aggregate/value object/DB schema/event schema/DTO/API contract data/persistence model/데이터 흐름 + migration) + OperationalRiskArchitectAgent → InfraOperationalArchitectAgent rename. 4종 모두 §결정 3 (신규 agent/model 변경 시 ADR 의무) 정합. model tier (Sonnet) = brainstorm Phase 0+1 ArchitectAgent+Codex 최종 확정 carry-over (재론 금지). InfraArchitect 신설 철회 명문화 (Docker-first + AWS 없음 — 미도입 결정, ratchet 위반 아님)."
    ref: CFP-676
    carrier_story: CFP-676
    sunset_justification: null
    affected_agents:
      - CodeArchitectAgent (new entry, codeforge-design — Sonnet)
      - ArchitectAnalystAgent (new entry, codeforge-design — Sonnet, PriorArtAgent rename)
      - DataArchitectAgent (DataMigrationArchitectAgent rename + mandate 확장, codeforge-design — Opus 유지)
      - InfraOperationalArchitectAgent (OperationalRiskArchitectAgent rename, codeforge-design — Opus inheritance 유지)
  - amendment_id: 8
    date: "2026-05-20"
    status: applied
    summary: "CFP-1086 Story-1 — design lane 5+3 → 7+3+1 permanent+CONDITIONAL roster 재편. AggregateArchitectAgent 신설 (Sonnet, §결정 1 Sonnet (a) single-mandate advocacy — RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound aggregate boundary + Alembic 정책 tool-agnostic policy layer) + APIContractArchitectAgent 신설 (Sonnet, §결정 1 Sonnet (a) single-mandate advocacy — transport REST/GraphQL/gRPC/WebSocket + API versioning + DTO + OpenAPI/GraphQL schema + contract testing). CodeArchitectAgent → ModuleArchitectAgent rename + mandate 정정 (도메인 모델 invariant 영역 제거 — module boundary + dependency direction + layered/hexagonal/clean module-level only, aggregate invariant 영역은 AggregateArch). DataArchitectAgent mandate 축소 (RDB 영역 제거 — 빅데이터 OLAP only: Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계. RDB OLTP 영역은 AggregateArch). AggregateArch CONDITIONAL applicability (`project.yaml aggregate_arch.applicable: bool` — frontend-only / API-only / external-managed consumer non-applicable, LiveOps/LiveOrdering/ProductionEvidence CONDITIONAL 패턴 재사용 P2). 5 permanent → 7 permanent (2 신설). 3 CONDITIONAL → 3+1 CONDITIONAL (AggregateArch applicability 추가). 4종 모두 §결정 3 (신규 agent / model 변경 시 ADR 의무) 정합. model tier (Sonnet) = brainstorm Phase 0+1 ArchitectAgent + Codex 최종 확정 carry-over (재론 금지). DDDArchitectAgent 신설 reject 명문화 (axis 미정합 — method/학파 layer + ModuleArch wording overlap + consumer applicability 축소). axis 분석 disjoint 원칙 (Amendment 7 CodeArch/ArchitectAnalyst single-mandate advocacy 패턴 답습) — AggregateArch/APIContract 모두 처음부터 single-mandate advocacy 로 정의, multi-source synthesis 책임은 ArchitectAgent chief Opus 단독 보유."
    ref: CFP-1086
    carrier_story: CFP-1086-S1
    sunset_justification: null
    affected_agents:
      - AggregateArchitectAgent (new entry, codeforge-design — Sonnet)
      - APIContractArchitectAgent (new entry, codeforge-design — Sonnet, skeleton at S1 / body 심화 = S2)
      - ModuleArchitectAgent (CodeArchitectAgent rename + mandate 정정 — 도메인 모델 invariant 영역 제거, codeforge-design — Sonnet 유지)
      - DataArchitectAgent (mandate 축소 — RDB OLTP 영역 제거, OLAP only 유지, codeforge-design — Opus 유지)
    cross_ref:
      - ADR-068 Amendment 2 (CFP-1086 / Story-1 carrier — wording SSOT chief tie-break ladder P1 sibling)
      - ADR-086 (CFP-1086 / Story-1 신설 carrier — Deputy 신설 결정 framework P7, 본 Amendment 8 = self-application 첫 사례)
      - CFP-1079 (OpsExecutionArchitect 신설 + InfraOperationalArch §7.4 mandate 보강 sibling Epic — Phase 1 PR open 시점 OPEN PR 0건, 본 Amendment 8 = 선점, CFP-1079 후속 = Amendment 9 별 session)
  - amendment_id: 9
    date: "2026-05-20"
    status: applied
    summary: "CFP-1059 Story-1 — codeforge-deploy + codeforge-deploy-review lane plugin 신설 (ADR-023 Amendment 1 / ADR-087 / ADR-088 sibling carrier). 4 신설 agent tier 결정 — (a) DeployPLAgent (codeforge-deploy lane PL, Sonnet — §결정 1 Sonnet (b) implementation/test work 정합, deploy 행위 = blue stack provision + database expand + healthcheck + traffic switch + green decommission + blue retention 단순 절차 수행, OpRiskArch 가 별도 §7.4 SSOT 보유, lane PL 추가 합성 책임 없음) / (b) DeployWorkerAgent (codeforge-deploy lane worker, Sonnet — §결정 1 Sonnet (a) single-mandate advocacy, deploy step 1 step at a time advocacy + Story §12 Deploy section author) / (c) DeployReviewPLAgent (codeforge-deploy-review lane PL, Opus — §결정 1 Opus (a) multi-source synthesis — production evidence quad 4-tuple (bucket prefix listing / WAL sample / Prometheus rate metric / drainage rate) cross-source synthesis + ADR-72 §결정 5 epic-cutover-gate-evidence-quad-check ownership ADR-088 §결정 3 carrier 이관) / (d) DeployReviewWorkerAgent (codeforge-deploy-review lane worker, Sonnet — §결정 1 Sonnet (a) single-mandate advocacy, 4-tuple evidence 개별 검증 advocacy + Story §13 Deploy Review section author). 4종 모두 §결정 3 (신규 agent / model 변경 시 ADR 의무) 정합 — ADR-087 §결정 1+§결정 2 + ADR-088 §결정 1+§결정 2+§결정 3 carrier 통과. spawn count empirical grounding (ADR-068 I-5 cross-ref) — 2 lane × 2 agent = 4 spawn point per Story (production cutover-touching Story 한정, wrapper-self-app N/A) [empirical-source: TBD — consumer mctrader production cutover Story 첫 적용 시 측정 lock-in]. ratchet 강화 방향 (agent roster 0 → 4 신설 = scope 확장 only)."
    ref: CFP-1059
    carrier_story: CFP-1059-S1
    sunset_justification: null
    affected_agents:
      - DeployPLAgent (new entry, codeforge-deploy — Sonnet)
      - DeployWorkerAgent (new entry, codeforge-deploy — Sonnet)
      - DeployReviewPLAgent (new entry, codeforge-deploy-review — Opus, §결정 1 Opus (a) multi-source synthesis 정합)
      - DeployReviewWorkerAgent (new entry, codeforge-deploy-review — Sonnet)
    cross_ref:
      - ADR-023 Amendment 1 (CFP-1059 / Story-1 sibling carrier — lane plugin 6 → 8 확장 첫 실 적용)
      - ADR-087 (CFP-1059 / Story-1 신설 carrier — Deploy lane as 7th lane plugin)
      - ADR-088 (CFP-1059 / Story-1 신설 carrier — Deploy Review lane + ProductionEvidence transfer)
      - ADR-068 §결정 1 I-5 dimensional empirical grounding (spawn count empirical-source TBD annotation)
related_stories:
  - CFP-448
  - CFP-676
  - CFP-1086
  - CFP-1059  # Amendment 9 carrier — 4 신설 agent tier (DeployPL/DeployWorker/DeployReviewPL/DeployReviewWorker)
related_adrs:
  - ADR-009
  - ADR-013
  - ADR-022
  - ADR-035
  - ADR-037
  - ADR-039
  - ADR-046
  - ADR-057
  - ADR-068  # Amendment 2 cross-ref (CFP-1086 / Story-1 carrier — wording SSOT chief tie-break ladder P1 sibling) + Amendment 9 §결정 1 I-5 cross-ref (CFP-1059 / Story-1 — spawn count empirical grounding)
  - ADR-086  # 신설 cross-ref (CFP-1086 / Story-1 — Deputy 신설 결정 framework P7, 본 Amendment 8 = self-application 첫 사례)
  - ADR-023  # Amendment 1 sibling cross-ref (CFP-1059 / Story-1 — lane plugin 6 → 8 확장)
  - ADR-087  # 신설 cross-ref (CFP-1059 / Story-1 — Deploy lane as 7th lane plugin, Amendment 9 carrier)
  - ADR-088  # 신설 cross-ref (CFP-1059 / Story-1 — Deploy Review lane + ProductionEvidence transfer, Amendment 9 carrier)
related_files:
  - .claude-plugin/plugin.json
  - CLAUDE.md
is_transitional: false
---

# ADR-042: Agent model selection policy — Opus / Sonnet / Haiku tier criteria

## 상태

**Accepted (2026-05-09)** — 본 ADR 는 [ADR-013 dogfood-out waiver](ADR-013-codeforge-family-dogfood-out-policy.md) 를 명시적으로 발동, 정식 Story 7-lane flow 를 우회하여 직접 chore PR 로 제출. 사유는 § "컨텍스트 — Story 우회 사유 (ADR-013 waiver)" 참조.

## 컨텍스트

### 동인

토큰 비용 최적화 요구. 21 codeforge agent (6 lane plugin 분산) + 2 webapp preset 의 model 할당 현황을 audit 한 결과, **role 정의가 깊은 reasoning 을 요구하면 Opus, Sonnet 으로 fully cover 가능한 얕은 mandate 만 가지면 Sonnet, 단순 wrapping / 실행만 하면 Haiku** 라는 3-tier 기준이 articulate 되어야 향후 agent 신설 / 기존 agent model 조정 시 일관된 의사 결정 가능.

### 사용자 articulated 핵심 원칙

> "Sonnet 으로 대체 가능한 수준의 얕은 역할만 맡고 있다면 역할이 제대로 잡히지 않은 것이다."

본 원칙은 model selection 이 **단순 비용 결정이 아니라 role 정의의 정합성 시그널** 이라는 의미. Sonnet 으로 충분한 agent 를 Opus 로 운영하는 것은 token waste 인 동시에, Opus 로 운영해야 잘 돌아가는 agent 를 Sonnet 으로 내리는 것은 role 결손. 양 방향 미스매치 모두 ADR scope.

### 현재 agent inventory (2026-05-09)

총 21 agent (6 lane plugin) + 2 webapp preset.

**Opus 4.7 (14, explicit `model:` field)**:
- 5 PL: RequirementsPLAgent · ArchitectPLAgent · DesignReviewPLAgent · CodeReviewPLAgent · SecurityTestPLAgent
- ArchitectAgent (chief author, multi-deputy synthesis → §1-§11 + ADR draft)
- ClaudeReviewAgent (Opus peer with Codex GPT-5)
- 5 design SubAgent: CodebaseMapperAgent · RefactorAgent · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent
- DomainAgent · ResearcherAgent · PMOAgent

**Opus 4.7 (3, inherited via no `model:` field)**: OperationalRiskArchitectAgent · LiveOpsDeputyAgent · LiveOrderingDeputyAgent

**Haiku 4.5 (6 — Amendment 2 이후)**:
- codex/external wrapper (3): TestAgent · CodexReviewAgent · RequirementsAnalystAgent
- mechanical pattern execution (3, Amendment 2): InfraEngineerAgent · QADeveloperAgent · DataEngineerAgent

**Sonnet 4.6 (4 — Amendment 2 이후)**: DeveloperPLAgent · DeveloperAgent + 2 webapp preset (BackendDeveloperAgent · FrontendDeveloperAgent)

### Story 우회 사유 (ADR-013 waiver)

본 ADR 는 Story 7-lane flow 대신 chore PR 직접 제출. ADR-013 dogfood-out waiver 발동 사유 3건:

1. **KEY collision** — `story-init.yml` Action 자동 KEY 할당 (CFP-276) 이 wrapper 의 in-flight CFP-276 (Doc Location Registry, [ADR-041](ADR-041-doc-location-registry.md)) 과 충돌. Tracked: [codeforge-internal-docs#99](https://github.com/mclayer/codeforge-internal-docs/issues/99).
2. **Action permission misconfiguration** — `story-init.yml` 의 PR creation step permission 결손. Tracked: [codeforge-internal-docs#98](https://github.com/mclayer/codeforge-internal-docs/issues/98).
3. **Cost asymmetry** — 본 ADR 의 effort scope = 정책 정리 1건 + sibling agent file 2건 (CodebaseMapperAgent + RefactorAgent model field edit). Phase 1 lane flow 진입 시 ~30 Opus agent invocation 발생 (요구사항 4 + 설계 8 + 설계리뷰 PL + 종합) — 본 ADR 가 절약하려는 Sonnet swap 가치 (months of usage) 와 비교 시 lane flow 자체가 cost negative. Lightweight path = ADR 단독 + chore PR.

Cancelled Story tracking: [codeforge-internal-docs#96](https://github.com/mclayer/codeforge-internal-docs/issues/96) (closed not_planned).

## 결정

### 결정 1: 3-tier 분류 기준 (role pattern × model)

| Tier | Model | Role pattern criteria |
|------|-------|----------------------|
| **Opus** | claude-opus-4-7 | (a) Multi-source synthesis (3+ SubAgent / lane / contract input dedup + 종합 판정) — 모든 PL · ArchitectAgent chief. (b) Independent reasoning peer to external GPT-5 (ClaudeReviewAgent — Codex 와의 의도적 reasoning depth 매칭). (c) High-stakes domain interpretation (DomainAgent — Live trading / 금융 / 헬스 데이터 등 invariant 누설 위험). (d) Security / safety boundary owner (SecurityArchitectAgent · OperationalRiskArchitectAgent · DataMigrationArchitectAgent · TestContractArchitectAgent — §7 trust boundary / §7.4 DR / §11 schema rollback / §8 perf baseline). (e) Real-funds risk owner (LiveOpsDeputyAgent · LiveOrderingDeputyAgent — CFP-77 CONDITIONAL). (f) Cross-Story pattern analysis + ADR proposal (PMOAgent). (g) Deep research with reshape mandate (ResearcherAgent — per [ADR-046](ADR-046-researcher-role-redefinition.md) (2026-05-09)). |
| **Sonnet** | claude-sonnet-4-6 | (a) Single-mandate advocacy within multi-deputy debate — read-only 조사 + 자기 mandate 측 단일 축 주장 (CodebaseMapperAgent — existing facts only, RefactorAgent — pattern advocacy only). (b) Implementation work — code write / refactor / test 구현 (DeveloperAgent · DeveloperPLAgent · 2 webapp preset). |

> **Amendment 4 (2026-05-11)**: CodebaseMapperAgent·RefactorAgent는 Opus로 복원됨 — ADR-057 참조.
>
> **Amendment 5 (2026-05-12, CFP-448)**: Amendment 4 의 6 agent 상향 중 3종 (CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent) Opus → Sonnet 복귀. 나머지 3종 (FeasibilityAgent · ContinuityAgent · ChangeImpactAgent) Opus 유지. ADR-057 Amendment 3 cross-ref.
>
> **Amendment 7 (2026-05-19, CFP-676)**: Sonnet (a) "Single-mandate advocacy within multi-deputy debate" 에 **CodeArchitectAgent** (§3 code 설계 단일 축 advocacy — layered/hexagonal/clean/DDD bounded context/module boundary/dependency direction) + **ArchitectAnalystAgent** (변경 전 기존 설계 분석 단일 축 — PriorArtAgent rename, 4-tuple sub-tuple component) 2종 추가. CodebaseMapper/Refactor 동질 패턴 (single-mandate advocate, multi-source synthesis = ArchitectAgent chief Opus). §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 충족 — 처음부터 single-mandate 정의이므로 Sonnet 적정. DataMigrationArchitectAgent → **DataArchitectAgent** rename + mandate 확장 / OperationalRiskArchitectAgent → **InfraOperationalArchitectAgent** rename — 본 § 의 Sonnet criteria 무관 (Opus tier 유지, §결정 1 (d) Security/safety boundary owner / 결정 4 inheritance). 상세 = 본 ADR `## Amendment 7` 본문 section. **CodebaseMapper / Refactor 의 mandate text 재정의 동시 산출물 의무 발화로 §결정 2 invariant 정합 — 단순 model field downgrade 금지. DeveloperPLAgent 는 사용자 framing (CFP-448) verbatim ('아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다') 직접 적용 + ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의 정합 회귀 → mandate text 재정의 면제 + Codex re-review 면제**. 자세한 결정 matrix 는 본 ADR Amendment 5 본문 + ADR-057 Amendment 3 §결정 3 표 참조.
| **Haiku** | claude-haiku-4-5 | (a) Test runner / 결과 수집 — minimal reasoning (TestAgent). (b) External tool wrapper — 본체 reasoning 은 external (Codex GPT-5 / GPT-5.4) 가 수행, Claude 는 prompt 조립 / output relay 만 (CodexReviewAgent · RequirementsAnalystAgent). (c) Mechanical pattern execution — 입력 명세(Change Plan §3 + Story §8)가 충분히 structured되어 creative/diagnostic reasoning 없이 패턴 기반 생성이 가능하고, 오류 발생 시 FIX 루프가 CI/테스트로 즉시 감지 가능한 경우 (InfraEngineerAgent · QADeveloperAgent · DataEngineerAgent — Amendment 2). |

> **Amendment 6 (2026-05-16, CFP-777)**: DialogFidelityAgent 신규 entry 추가 (codeforge-pmo / Opus pilot tier). verifier mandate = 누적 대화 fidelity 검증, 의미적 모순 판정 영역. mandate depth = 다축 (semantic match + ledger consistency + 4 차원 enum closed + Story §1 immutable cross-ref + Layer 4 incidents row inspection). single-axis 외형은 single-axis 검수이나 contradiction detection 은 deep reasoning 영역 — **Opus pilot 시작 → N=20 baseline 후 §결정 2 invariant 적용 재판정** (별도 carrier). **Codex 평행 평가 의무** (CFP-379 / CFP-448 pattern) — TP#4 dispatch 시 본 Amendment 입력 verbatim 전달, Opus vs Sonnet baseline divergence detect. ADR-071 Amendment 1 (DialogFidelityAgent external verifier auxiliary layer) cross-ref.

| **Opus pilot** | claude-opus-4-7 | DialogFidelityAgent (codeforge-pmo) — verifier-narrower-than-generator 패턴: 누적 대화 fidelity 검증 (Story §1 immutable + Layer 4 incidents + 현 turn output), 의미적 모순 판정 (deep reasoning 영역). §결정 2 invariant 재판정 trigger = N=20 spawn baseline 후 (별도 carrier). |

### 결정 2: 본 ADR 발효 시점 변경 사항 (2 sibling PR scope)

**plugin-codeforge-design sibling PR** (별도 — 본 ADR PR merge 직후):
- CodebaseMapperAgent: Opus 4.7 → **Sonnet 4.6**
- RefactorAgent: Opus 4.7 → **Sonnet 4.6**

근거: 양 agent 모두 3-way SubAgent debate (Mapper = existing codebase fact 보고, Refactor = decoupling/pattern advocacy, SecurityArch = threat) 안에서 **single-mandate advocacy** 패턴. read-only 조사 + 자기 축 단일 주장. multi-source synthesis 책임은 ArchitectAgent chief (Opus) 가 수행. Sonnet 4.6 의 reasoning depth 가 본 mandate 를 fully cover.

> **Amendment 4 역전 (2026-05-11, ADR-057)**: Codex 독립 리뷰 결과 CodebaseMapperAgent·RefactorAgent의 Sonnet mandate에서 symbol resolution 정확도 및 advocacy 품질 부족이 확인되어 Opus로 복원. 본 §결정2의 해당 배정은 Amendment 4에 의해 무효화됨.
>
> **Amendment 5 (2026-05-12, ADR-057 Amendment 3 cross-ref, CFP-448) — Amendment 4 부분 revert**: CodebaseMapperAgent·RefactorAgent 가 다시 Sonnet 으로 복귀 (original §결정 2 분류 정합 회귀). 단 단순 model field downgrade 금지 — **mandate text 재정의 동시 산출물 의무 발화** (Codex review CFP-379 finding 의 symbol resolution 정확도 / advocacy 품질 우려는 mandate text 강화로 차단). 본 §결정 2 의 original 배정 (Sonnet)으로 effective 회귀 + invariant 정합.

**ResearcherAgent** — RESOLVED by [ADR-046](ADR-046-researcher-role-redefinition.md) (2026-05-09): Concept formulation + Deep exploration + Requirement reshape. Opus tier 유지 (mandate depth 근거). 상세: ADR-046.

**Amendment 2 (2026-05-10) — Haiku pilot 전환 (codeforge-develop sibling PR)**:
- InfraEngineerAgent: Sonnet 4.6 → **Haiku 4.5** (mechanical pattern execution — Docker-first ADR-033 명세 기반)
- QADeveloperAgent: Sonnet 4.6 → **Haiku 4.5** (mechanical pattern execution — §8 Test Contract 명세 기반)
- DataEngineerAgent: Sonnet 4.6 → **Haiku 4.5** (mechanical pattern execution — §11 DataMigration 명세 기반)

근거: 3 agent 모두 입력 명세가 ArchitectAgent/deputy 산출물로 structured되어 있고 오류는 CI/통합테스트로 즉시 감지 가능. Pilot 평가 기준: 결정 5 참조.

### 결정 3: 신규 agent 도입 / 기존 agent model 변경 시 ADR 의무

신규 agent 도입 또는 기존 agent model tier 변경은 **별도 ADR amendment 또는 본 ADR cross-ref ADR 의무**. 본 ADR 의 결정 1 매트릭스의 어느 row 에 해당하는지 명시 + 해당 lane plugin agent file 의 `model:` field 와 동기.

본 의무는 [ADR-023](ADR-023-lane-plugin-lifecycle.md) (lane plugin lifecycle) 와 [ADR-037](ADR-037-plugin-version-bump-rule.md) (plugin version bump rule) 와 함께 작동: 신규 agent 도입 = lane plugin MINOR bump trigger + 본 ADR cross-ref 의무.

### 결정 4: `model:` field absent (inheritance) 정책

agent file frontmatter 의 `model:` field 부재 시 platform default 가 inherit 됨 (현재 Opus 4.7). 본 inheritance 는 **explicit Opus 결정과 의미 동일** 로 간주 — 즉 결정 1 의 Opus tier criteria 에 부합해야 함. 향후 platform default 변경 시 inheritance 영향 받는 agent 전수 audit 의무.

현재 inheritance 활용 3 agent (OperationalRiskArchitectAgent · LiveOpsDeputyAgent · LiveOrderingDeputyAgent) 는 모두 Opus tier criteria (d) (e) 부합 → 본 ADR 이후에도 inheritance 유지.

### 결정 5: Haiku pilot rollback 트리거 기준 (Amendment 2)

**평가 주기**: 전환 후 5 Story 완료 시점에 Orchestrator가 §10 FIX Ledger 집계 → 사용자 보고.

**rollback 트리거 (agent별도 독립)**:
1. **점진적 rollback**: 해당 agent 관련 FIX 루프 횟수가 전환 전 baseline 대비 30% 초과 시 → 해당 agent 단독 rollback (Sonnet 4.6 복원 + Amendment 2 해당 항목 revert)
2. **즉시 rollback**: P0·P1 severity 결함이 Haiku 전환 agent에서 발원 확인 시 → 해당 agent 즉시 rollback
3. **전체 rollback**: 3 agent 중 2개 이상 즉시 rollback 트리거 발생 시 → Amendment 2 전체 revert

### 결정 6: 재-audit 트리거 규칙 (Amendment 2)

다음 이벤트 발생 시 나머지 Sonnet agent (DeveloperPLAgent · DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent) 재평가 의무:
1. Haiku major 버전 업 (Haiku 4.x → Haiku 5.x)
2. 기존 Sonnet agent의 mandate가 "패턴 실행" 방향으로 재정의될 때 (결정 3 ADR amendment 또는 별도 ADR cross-ref 발동 시)

## 근거

### 왜 PL · ArchitectAgent chief 는 Opus 인가

PL 의 책임 = lane synthesis (3+ sub-agent finding dedup + severity 종합 + `pl_recommendation` 결정). ArchitectAgent chief 의 책임 = 6-8 SubAgent 산출물 (CodebaseMapper / Refactor / SecurityArch / OpRisk / TestContract / DataMigration + 2 CONDITIONAL Live) 통합 → Story §1-§11 + Change Plan §3 + ADR draft 작성. 양쪽 다 multi-source 가 충돌 / 누락 / 모순 케이스에서 architectural judgment 필요. Sonnet 으로 swap 시 dedup / 종합 판정 layer 가 shallow 해져 FIX root cause 오판 / responsibility leak 발생 위험 — [ADR-021](ADR-021-phase-gap-measurable-signal.md) R4 detection source 자체 약화.

### 왜 ClaudeReviewAgent 는 Opus 인가

[ADR-001](ADR-001-review-agent-unification.md) (review agent unification) 은 lane-agnostic 2-vendor (Claude + Codex) worker pattern 을 채택. Codex 측 = GPT-5 (high reasoning). Claude 측이 Sonnet 이면 reasoning depth 비대칭 → "Claude 가 Codex 의 finding 을 dedup 하지 못한다" 패턴 발생. 의도적으로 Opus = GPT-5 peer matching.

### 왜 SecurityArch / OpRisk / DataMigration / TestContract SubAgent 는 Opus 인가

[SubAgent mandate 매트릭스](../../CLAUDE.md) 에서 본 4 SubAgent 는 §7 / §7.4 / §11 / §8 의 primary owner. 각 영역의 invariant 누락 = SecurityTest / 보안 테스트 / 구현 테스트 단계에서 P0 차단 trigger. Sonnet 으로 swap 시 invariant 정의 누락 위험 ↑ — review-verdict v3 의 P0 차단이 사후 발견. 비용보다 catch-rate 우선 결정.

### 왜 DomainAgent 는 Opus 인가

DomainAgent 는 사용자 자연어 요구사항 → domain invariant translation. mctrader (codeforge 데뷔 consumer) 의 KRW 거래소 + real funds + Live ordering domain 에서 invariant 누설 (예: partial fill reconciliation invariant 누락) = real funds 손실 위험. high-stakes domain interpretation 은 token cost vs risk 비대칭 — Opus 유지.

### 왜 PMOAgent 는 Opus 인가

PMOAgent 의 mandate = (a) Epic 창설 (multi-Story dependency graph) + (b) Story 완료 retro (cross-Story 패턴 분석 → ADR proposal). (b) 가 특히 deep — 6+ Story 의 review / FIX / test outcome 을 cross-correlate → 새 ADR 가 필요한지 판단. Sonnet 의 cross-source pattern detection 은 본 mandate 에 shallow.

### 왜 CodebaseMapper · Refactor 는 Sonnet 인가

> **Amendment 4 에 의해 무효화됨 (2026-05-11) — ADR-057 참조. CodebaseMapper · RefactorAgent 는 Opus 로 복원.**
>
> **Amendment 5 에 의해 effective 회귀 (2026-05-12, CFP-448 / ADR-057 Amendment 3)**: 본 § 의 reasoning 이 다시 effective. 단 mandate text 재정의 동시 산출물 의무 발화 (CodebaseMapper / Refactor 의 description / 본문 role 정의 강화) — Codex review (CFP-379) symbol resolution 정확도 / advocacy 품질 finding 의 재발 차단 mechanism.

양 agent 모두 **single-mandate advocacy** 패턴:
- CodebaseMapperAgent: 기존 codebase fact 만 보고 (file structure / API surface / 의존성 그래프) — read-only mode
- RefactorAgent: pattern decoupling / 일관성 advocacy 만 — 자기 축 단일 주장

3-way debate 의 dedup / 종합은 ArchitectAgent chief (Opus) 가 수행. 양 SubAgent 는 자기 축 사실 / 주장만 정확히 전달하면 충분 — Sonnet 4.6 reasoning depth fully cover.

핵심 원칙 발현: "Sonnet 으로 대체 가능 = role 재정의 시그널" 의 역방향 적용 — 본 2 SubAgent 는 처음부터 single-mandate 로 정의되었으므로 Sonnet 이 적정. **Amendment 5 의 mandate text 재정의 의무는 본 invariant 의 enforcement mechanism — model field 와 role definition 의 동시 정합 보장**.

### 왜 DeveloperPLAgent · DeveloperAgent · webapp preset 은 Sonnet 인가

DeveloperPLAgent / DeveloperAgent / 2 webapp preset (BackendDeveloperAgent · FrontendDeveloperAgent) 모두 implementation work — Change Plan + Story §3·§7·§11 SSOT 로부터 코드 작성. Architecture decision 은 design lane 에서 종결, develop lane 은 그 결정을 충실히 implement. Sonnet 4.6 의 코드 생성 능력은 본 mandate 충분.

DeveloperPLAgent 가 1차 FIX root cause 진단을 수행하지만, 최종 판정은 ArchitectPLAgent (Opus) 가 수행 — 1차 진단은 Sonnet level 충분.

> **Amendment 5 (2026-05-12, CFP-448)**: DeveloperPLAgent 가 Amendment 4 (2026-05-11, ADR-057 carry) 에서 Opus 로 상향됐다가 본 Amendment 5 에서 effective 회귀. 사용자 framing (CFP-448) verbatim: "내가 보기엔 코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까? 왜냐하면 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다." — ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의 직접 복원. 본 § 의 "1차 진단은 Sonnet level 충분, 최종 판정은 ArchitectPLAgent (Opus)" 원칙이 effective 회귀 — CFP-379 의 DeveloperPL Codex finding "FIX 1차 진단 품질 개선" 은 본 원칙 정합 회귀로 거부.

> Amendment 2: QADeveloperAgent · DataEngineerAgent · InfraEngineerAgent 는 (c) Mechanical pattern execution 기준으로 Haiku 전환됨 — 결정 5 참조.

### 왜 TestAgent / CodexReviewAgent / RequirementsAnalystAgent 는 Haiku 인가

- TestAgent: 테스트 실행 + 결과 수집 + 1차 분류만 — minimal reasoning. Haiku 4.5 fully cover.
- CodexReviewAgent · RequirementsAnalystAgent: Claude 측은 codex CLI invocation wrapper. 본 reasoning 은 codex (GPT-5 / GPT-5.4) 가 수행. Claude 는 prompt 조립 + codex output relay 만 — Haiku 충분.

**Amendment 2 — InfraEngineerAgent · QADeveloperAgent · DataEngineerAgent (Haiku 4.5)**:
- InfraEngineerAgent: ADR-033 Docker-first preset 명세 기반 파일 생성 — 입력 명세(Dockerfile·compose 구조)가 구조화되어 있고 오류는 `docker build` / `compose up` CI에서 즉시 감지 가능. creative reasoning 불필요.
- QADeveloperAgent: TestContractArch §8 Given/When/Then 명세 기반 테스트 코드 생성 — 입력 명세가 structured되어 있고 테스트 누락은 CodeReviewPL 단계에서 감지. 테스트 framework 지식만 필요, diagnostic reasoning 불필요.
- DataEngineerAgent: DataMigrationArch §11 schema/port/adapter 명세 기반 구현 — 입력 명세가 structured되어 있고 schema 오류는 통합 테스트·CI schema 검증에서 감지.

3 agent 모두 (c) Mechanical pattern execution 기준 충족: ① 입력 명세 structured ② CI/테스트 즉시 오류 감지. Pilot 평가 기준: 결정 5 참조.

## 결과 (Consequences)

### 긍정

- **Token 비용 절감**: CodebaseMapperAgent + RefactorAgent Sonnet swap → design lane 매 spawn 마다 2 Opus → 2 Sonnet (대략 5-10x cost reduction per agent). 6-deputy parallel spawn 의 1/3 절약.
  > Amendment 4 (2026-05-11): CodebaseMapper·RefactorAgent가 Opus로 복원되어 해당 절감 효과는 무효화됨 — ADR-057.
- **Role 정의 명확성**: "Sonnet swap 가능 = role 재정의 필요" 원칙이 ADR 화 → 향후 agent audit / role 재검토 시 measurable signal.
- **신규 agent 도입 절차 표준화**: 결정 3 의 ADR 의무가 model selection 을 design 결정으로 격상.

### 부정 / 트레이드오프

- **Sibling PR coordination overhead**: 본 ADR + plugin-codeforge-design (Mapper · Refactor model edit) 2 PR 동기화 의무. Marketplace cross-repo sync ([ADR-016](ADR-016-marketplace-registration-policy.md)) 와 align.
- **Story 우회 (ADR-013 waiver)**: 본 ADR 자체가 정식 Story flow 를 우회 — 향후 model tier 변경 ADR 가 본 패턴을 reuse 시 KEY collision / Action permission 등 근본 원인 (codeforge-internal-docs#98 / #99) 미해결 시 또 다시 waiver 의존 우려. 정상화 후 본 ADR 도 retroactive Story 부여 검토 가능 (선택).
- **`model:` inheritance dependence (결정 4)**: 3 agent (OpRisk / LiveOps / LiveOrdering) 가 platform default 에 의존 — platform default 변경 시 audit 의무. 명시화 cost vs flexibility trade-off.

## 대안 검토

| 대안 | 기각 사유 |
|------|----------|
| **모든 agent Opus 유지** | Token cost 무한 누적. CodebaseMapper / Refactor 의 single-mandate role 정의 분명히 Sonnet 으로 fully cover — 비용 정당화 불가. |
| **모든 agent Sonnet 으로 통일 (cost 우선)** | PL synthesis / ArchitectAgent chief multi-deputy 종합 / SecurityArch invariant 정의 등이 shallow 해져 review-verdict P0 차단 catch-rate 약화. ADR-021 R4 detection source 약화. |
| **ResearcherAgent 도 본 ADR 에서 Sonnet 으로 swap** | Role 정의 자체가 underdefined — model 만 swap 시 role 결손 은폐. 분리 처리 (plugin-codeforge-requirements#12 별도 Story) 가 정합. |
| **DomainAgent Sonnet swap** | 도메인 invariant 누설 위험 (mctrader Live trading + KRW exchange + real funds 컨텍스트). high-stakes domain 은 cost vs risk 비대칭 — Opus 유지. |
| **정식 Story flow 진입 (ADR-013 waiver 미발동)** | KEY collision (codeforge-internal-docs#99) + Action permission (codeforge-internal-docs#98) 미해결 + cost asymmetry — 본 ADR scope 의 Sonnet swap 가치보다 lane flow 자체 비용이 더 큼. waiver 가 합리적. |

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) — wrapper plugin manifest (5.5.0 → 5.6.0 MINOR bump)
- [`CLAUDE.md`](../../CLAUDE.md) — Development Agent Team 섹션에 본 ADR 1줄 참조 추가
- 본 ADR scope 외 lane plugin agent file (CodebaseMapperAgent · RefactorAgent model field edit) — sibling PR [mclayer/plugin-codeforge-design#24](https://github.com/mclayer/plugin-codeforge-design/pull/24)

## 관련 ADR

- [ADR-009](ADR-009-wrapper-only-decomposition.md) — wrapper 0-agent invariant (model 할당 영역은 lane plugin agent file)
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — dogfood-out waiver (본 ADR 발동 근거)
- [ADR-022](ADR-022-sonnet-review-verdict-decider.md) — Sonnet review-verdict decider (Deprecated by CFP-134 / ADR-035) — Sonnet decider 자동 발동 무효, 사용자 ad-hoc 호출만
- [ADR-023](ADR-023-lane-plugin-lifecycle.md) — lane plugin lifecycle (신규 agent 도입 절차 cross-ref)
- [ADR-035](ADR-035-codeforge-agent-teams-epic-architecture.md) — Codeforge Agent Teams Epic Architecture (CFP-134, agent topology SSOT)
- [ADR-037](ADR-037-plugin-version-bump-rule.md) — plugin version bump rule (model tier 변경 = MINOR bump trigger)
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — Orchestrator subagent default (model tier 변경 작업 자체도 본 정책 적용)
- [ADR-046](ADR-046-researcher-role-redefinition.md) — ResearcherAgent role redefinition (resolves §결정 2 deferred fence, amendment_log[1])

### 외부 reference

- [codeforge-internal-docs#96](https://github.com/mclayer/codeforge-internal-docs/issues/96) — cancelled Story (KEY collision 으로 close not_planned)
- [codeforge-internal-docs#98](https://github.com/mclayer/codeforge-internal-docs/issues/98) — `story-init.yml` Action permission misconfiguration
- [codeforge-internal-docs#99](https://github.com/mclayer/codeforge-internal-docs/issues/99) — KEY collision tracking
- [plugin-codeforge-requirements#12](https://github.com/mclayer/plugin-codeforge-requirements/issues/12) — ResearcherAgent role 재정의 follow-up
- **Sibling PR** (codeforge-design Mapper + Refactor model edit): [mclayer/plugin-codeforge-design#24](https://github.com/mclayer/plugin-codeforge-design/pull/24) — version 0.4.0 → 0.4.1 PATCH bump 동반

---

## Amendment 3 — IntegrationTestAgent Sonnet tier (CFP-367 / ADR-055)

**날짜**: 2026-05-10

### 변경 사항

**IntegrationTestAgent**: Sonnet tier 결정.

**Haiku 제외 근거**: 통합 테스트 작성은 컴포넌트 경계 판단·외부 의존성 설계를 포함한다. ADR-042 Haiku 기준 "mechanical pattern execution (no design decision)"에 부합하지 않음. 구체적으로:
- 어떤 경계가 테스트 대상인지 §8.6을 해석해 결정
- WireMock stub 계약 정의 (외부 API 스펙 이해 필요)
- docker-compose.test.yml 환경과 테스트 코드의 정합성 판단

**Sonnet 선택 근거**: 경계 판단은 필요하나 architecture-level decision은 TestContractArchitectAgent(Sonnet)가 §8.6에서 이미 결정. IntegrationTestAgent는 §8.6 계약을 "정확히 이행"하는 역할 → Opus 불필요. Sonnet으로 충분 커버.

### 갱신된 tier 배정 (Amendment 3 이후 주요 항목)

| Agent | Tier | 변경 이력 |
|---|---|---|
| IntegrationTestAgent | Sonnet | Amendment 3 신규 (CFP-367) |
| InfraEngineerAgent | Haiku (pilot) | Amendment 2 (CFP-360) |
| QADeveloperAgent | Haiku (pilot) | Amendment 2 (CFP-360) |
| DataEngineerAgent | Haiku (pilot) | Amendment 2 (CFP-360) |

---

## Amendment 5 — Selective rollback of Amendment 4 (3 of 6 agent Opus → Sonnet, CFP-448 / ADR-057 Amendment 3 cross-ref)

**날짜**: 2026-05-12

### 변경 사항

Amendment 4 (CFP-379, 2026-05-11) 의 6 agent Sonnet → Opus 상향 중 3종 selective rollback:

| Agent | Amendment 4 (2026-05-11) | Amendment 5 (2026-05-12) | 비고 |
|---|---|---|---|
| FeasibilityAgent | Sonnet → Opus | **Opus 유지** | ADR-042 §결정 1 (e) architecture constraint 해석 정합 |
| ContinuityAgent | Sonnet → Opus | **Opus 유지** | ADR-042 §결정 1 (f) cross-Story pattern detection 정합 (PMOAgent 와 유사) |
| ChangeImpactAgent | Sonnet → Opus | **Opus 유지** | ADR-042 §결정 1 (a) 단일 축이나 전체 코드베이스 영향 분석 — 사용자 framing (CFP-448) verbatim: 'changeimpact는 내가 보기에 opus가 괜찮아보인다'. axis-A 약함 (Opus 필요) + multi-source 가능성 |
| CodebaseMapperAgent | Sonnet → Opus | **Opus → Sonnet (rollback) + mandate text 재정의 의무** | ADR-042 §결정 2 original 분류 회귀 (single-mandate advocacy) |
| RefactorAgent | Sonnet → Opus | **Opus → Sonnet (rollback) + mandate text 재정의 의무** | ADR-042 §결정 2 original 분류 회귀 (single-mandate advocacy) |
| DeveloperPLAgent | Sonnet → Opus | **Opus → Sonnet (rollback)** | ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의 직접 복원. 사용자 framing (CFP-448) verbatim: '코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까... 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다' — mandate text 재정의 면제 + Codex re-review 면제 |

### 결정 framework (ADR-057 Amendment 3 SSOT carry)

본 Amendment 5 의 결정 matrix 는 ADR-057 Amendment 3 §결정 3 표 + 6 agent decision matrix verbatim cross-ref. carrier story CFP-448 Story §7 + Change Plan §3 SSOT.

### Mandate text 재정의 동시 산출물 의무 (CodebaseMapper / Refactor)

본 Amendment 5 의 핵심 invariant 정합 mechanism — ADR-042 §결정 2 ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 충족:

1. **CodebaseMapperAgent** (`plugin-codeforge-design/agents/CodebaseMapperAgent.md`):
   - `description` frontmatter 강화 의무 — "기존 코드베이스 변호자" 추상화 표현 → "기존 코드베이스 사실 변호자 — file structure / API surface / 의존성 그래프 등 **명시적으로 정의된 fact source 만 인용**. 추론 / 해석 / synthesis 금지 (chief author 영역)"
   - 본문 mandate / 책무 / 산출물 section 의 read-only invariant + structured output template 명시 의무

2. **RefactorAgent** (`plugin-codeforge-design/agents/RefactorAgent.md`):
   - `description` frontmatter 강화 의무 — "리팩터링 옹호자" → "리팩터링 옹호자 — **decoupling / pattern / 인터페이스 분리 3 카테고리** 안에서 advocacy. 카테고리 외 영역 (security / data integrity / op risk) 발화 금지 (해당 SubAgent 영역)"
   - 본문 mandate / advocacy axis (3 카테고리) / 산출물 section 의 boundary 명시 의무

본 mandate text 재정의 산출물은 Phase 2 PR scope (sibling plugin) — codeforge-design plugin agent file edit (PATCH bump). codeforge-design plugin sibling PR 시 본 Amendment 5 cross-ref 의무.

### Codex re-review + DeveloperPLAgent exclusion (ADR-057 Amendment 3 §변경 사항 5+6 cross-ref)

본 Amendment 5 = ADR-057 Amendment 3 atomic carrier. ADR-057 §변경 사항 5+6 에서 발화된 정책의 역방향 cross-ref:

- **Codex re-review 의무 (in-scope, Story §5.3 EC-2 정합)**: mandate text 재정의 대상 2 agent (CodebaseMapper / Refactor) — Phase 2 PR open 전 또는 PR 안에 Codex re-review 발화 의무 (단순 optional follow-up 아님). 재정의된 mandate 가 Sonnet 으로 cover 가능한지 검증. FIX verdict 시 rollback reject + Opus 복귀 ADR carrier 발의 의무
- **DeveloperPLAgent exclusion criterion**: DeveloperPLAgent 는 ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의로 mandate 이미 명확. 사용자 framing (CFP-448) verbatim 직접 적용: "코드 작성 에이전트들이 sonnet이 되는게 낫지 않을까? 왜냐하면 아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다" — role 재정의 불필요 → Codex re-review 도 면제 (CFP-379 의 DeveloperPL Codex finding "FIX 1차 진단 품질 개선" 은 ADR-042 §"왜 DeveloperPLAgent · DeveloperAgent · webapp preset 은 Sonnet 인가" 원칙 정합 회귀로 거부 — 1차 진단은 Sonnet level 충분, 최종 판정 ArchitectPL Opus. 단 Phase 2 CodeReview lane 일반 model field 변경 검토는 적용)

SSOT = ADR-057 Amendment 3 §변경 사항 5+6 본문. 본 Amendment 5 = 역방향 cross-ref reference (drift 차단).

### 6 agent decision evidence (3 axis 종합 — CFP-448 §5.0)

axis-A (operational cost trade-off) × axis-B (role redefinition signal, ADR-042 §결정 2 invariant 정합) × axis-C (SSOT alignment direction, CFP-448 CL-6 사용자 확정 = Option (i) ADR-057 §결정 3 표 = SSOT) 종합:

- **Sonnet rollback 3종 (CodebaseMapper / Refactor / DeveloperPL)**: axis-A 강함 (Sonnet sufficient — 사용자 framing verbatim 'DeveloperPL 고도 추론 불필요') + axis-B single-mandate advocacy (CodebaseMapper / Refactor) 또는 implementation work (DeveloperPL — ADR-042 §결정 1 (b) verbatim) + axis-C SSOT swap (rollback)
- **Opus 유지 3종 (Feasibility / Continuity / ChangeImpact)**: axis-A 약함 (Opus 필요 — ChangeImpact 는 사용자 framing verbatim 'changeimpact는 내가 보기에 opus가 괜찮아보인다') + axis-B multi-source synthesis 또는 cross-Story pattern detection 또는 단일 축이나 전체 코드베이스 영향 분석 (ChangeImpact, multi-source 가능성) + axis-C ADR-057 §결정 3 SSOT 정합 (Opus 유지)

**EC-9 tie-break 적용** (axis-A vs axis-B 충돌, CodebaseMapper + Refactor): axis-A 1차 우선 → rollback PASS + axis-B conditional constraint = mandate text 재정의 산출물 동시 의무 발화 (위 § 참조). **DeveloperPL** 은 tie-break 미해당 — axis-A / axis-B / axis-C 3 축 모두 Sonnet rollback 방향 일치 (사용자 framing verbatim + ADR-042 §결정 1 (b) implementation work 직접 정합).

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 5 는 ADR-042 의 결정 1~6 본문 변경 0건. 변경 = (a) §결정 1 / §결정 2 / §왜 CodebaseMapper · Refactor 는 Sonnet 인가 의 inline comment (Amendment 5 발화 marker) (b) Amendment 5 본문 section (본 단락) (c) frontmatter amendment_log row 5 신설. tier criteria + invariant + 신규 agent ADR 의무 + inheritance + Haiku rollback + 재-audit 모두 정책 변경 0건.

### Cross-ref invariant (ADR-057 Amendment 3)

본 Amendment 5 + ADR-057 Amendment 3 은 atomic cross-ref pair (CFP-448 §11 단일 carrier 결정 — Option C). drift 차단 mechanism:
- 본 ADR §결정 1 tier criteria + Amendment 5 tier 표 = **agent tier 분류 기준 SSOT**
- ADR-057 §결정 3 표 + Amendment 3 = **Sonnet 잔류 명단 SSOT** (CL-6 Option (i) 정합)
- 두 ADR 본문 모순 발생 시 → mandate 분리: tier criteria 는 ADR-042, 잔류 명단은 ADR-057

### Phase 2 PR atomic scope (ADR-063 정합)

본 Amendment 5 의 Phase 2 PR scope = wrapper + 2 lane plugin sibling (codeforge-design + codeforge-develop — codeforge-requirements 변경 0건 negative evidence, ChangeImpactAgent Opus 유지) + marketplace.json single sync:
- wrapper: 본 ADR-042 Amendment 5 + ADR-057 Amendment 3 + CLAUDE.md L127 mirror + `scripts/measure-rate-limit-fallback.sh` `SONNET_AGENTS` 배열 — PATCH bump (정책 본문 변경 없음, 표 / 명단 변경만)
- codeforge-requirements: 변경 0건 (ChangeImpactAgent Opus 유지)
- codeforge-design: CodebaseMapperAgent + RefactorAgent model field + mandate text 재정의 — MINOR bump (mandate text 변경)
- codeforge-develop: DeveloperPLAgent model field — PATCH bump (사용자 framing verbatim 직접 적용, mandate text 재정의 면제 → mandate 본문 변경 없음, model field 만 변경)
- marketplace.json: wrapper + codeforge-design + codeforge-develop 3 entry version sync (ADR-063 atomic invariant)

---

## Amendment 7 — CFP-1026 S1 design lane agent 구조 재편 model tier SSOT (CFP-676)

**날짜**: 2026-05-19

### 동기

mctrader codeforge 데뷔 evidence 누적 (chief author 부담 Story §1 24 mention + CodebaseMapper/Refactor 저활용 + OperationalRiskArch §7.4.4/§7.4.2 설계만으로 결정 불가). CFP-1026 Epic 의 Story-1 (W1 backbone) 이 design lane agent 구조 재편 정책 SSOT 를 단일 atomic carrier 로 확정. 신규 agent 2종 (CodeArchitect / ArchitectAnalyst) 도입 + deputy 2종 rename (DataMigrationArchitect → DataArchitect / OperationalRiskArchitect → InfraOperationalArchitect) 의 model tier 결정 = §결정 3 (신규 agent / model 변경 시 ADR 의무) 발동.

### 변경 사항

| Agent | 변경 | model tier | §결정 1 매트릭스 row |
|---|---|---|---|
| **CodeArchitectAgent** | **신설** — §3 code 설계 단일 축 advocacy (layered / hexagonal / clean / DDD bounded context / module boundary / dependency direction) | **Sonnet** (claude-sonnet-4-6) | **Sonnet (a)** "Single-mandate advocacy within multi-deputy debate — read-only 조사 + 자기 mandate 측 단일 축 주장" |
| **ArchitectAnalystAgent** | **신설** (PriorArtAgent rename) — 변경 전 기존 설계 (ADR / Change Plan / Story) 분석 단일 축. 4-tuple sub-tuple component (deputy 아님) | **Sonnet** (claude-sonnet-4-6) | **Sonnet (a)** 동일 |
| DataMigrationArchitectAgent | **rename → DataArchitectAgent** + mandate 확장 (§3 data + §11 전체 데이터 구조: entity / aggregate / value object / DB schema / event schema / DTO / API contract data / persistence model / 데이터 흐름 + migration) | **Opus 유지** (claude-opus-4-7) — §결정 1 (d) Security / safety boundary owner (§11 schema rollback) 정합 | (d) 무변경 |
| OperationalRiskArchitectAgent | **rename → InfraOperationalArchitectAgent** (mandate scope 보존 — §7.4 DR / disconnect / clock / rate / env + Container Docker primary) | **Opus 유지** (§결정 4 inheritance — `model:` field 부재 platform default Opus, §결정 1 (d) 정합) | (d) 무변경 |

### model tier 결정 근거 (Sonnet — 재론 금지 carry-over)

CodeArchitect / ArchitectAnalyst = §결정 2 invariant ("Sonnet 으로 대체 가능한 수준의 얕은 역할만 맡고 있다면 역할이 제대로 잡히지 않은 것이다") 의 **역방향 적용** — 본 2 agent 는 처음부터 single-mandate advocacy 로 정의 (CodeArchitect = §3 code 설계 단일 축 주장 / ArchitectAnalyst = 기존 설계 분석 단일 축 보고). multi-source synthesis (deputy 산출물 dedup + 종합 판정) 책임은 ArchitectAgent chief (Opus) 단독 보유 — 본 2 agent 는 자기 축 사실 / 주장만 정확히 전달하면 충분. CodebaseMapperAgent (existing codebase fact 보고) · RefactorAgent (pattern advocacy) 와 동질 패턴 (§ "왜 CodebaseMapper · Refactor 는 Sonnet 인가" + Amendment 5 mandate text 재정의 invariant 정합). Sonnet 4.6 reasoning depth 가 본 mandate 를 fully cover.

**model tier (Sonnet) 의사결정 재수행 금지** — brainstorm Phase 0+1 (사용자 7-turn 대화) 에서 ArchitectAgent + Codex 최종 확정 carry-over. 본 Amendment 7 = codify 만 (Sonnet vs Opus 토론 텍스트 부재 — 확정 전제 기술만). DataArchitect / InfraOperationalArchitect = rename only — model tier 무변경 (Opus 유지, §결정 1 (d) + 결정 4 inheritance 정합).

### InfraArchitect 신설 철회 명문화 (미도입 결정 — ratchet 위반 아님)

설계 lane 에 별도 `InfraArchitectAgent` (AWS / K8s / multi-host topology 전담) 신설은 **철회**. 사유:

- codeforge 의 infra 영역 = **Docker-first** ([ADR-033](ADR-033-docker-first-infra-engineering.md) §결정 5) + AWS / K8s 없음 (현 consumer = mctrader Docker compose 기반)
- InfraOperationalArchitect §7.4 Container Docker sub (restart policy / volume DR / health check / network mode boundary — ADR-033 4 항목) + InfraEngineerAgent (codeforge-develop lane, Haiku — ADR-033 Docker-first preset 기반 파일 생성) 의 2-agent 분담으로 infra 영역 충분 cover
- 별도 InfraArchitect = mandate overlap (InfraOperationalArchitect §7.4 Container + InfraEngineer 구현) + agent 수 비대

**미래 재발의 trigger** (ratchet 위반 아님 — 미도입 결정이므로 ADR-058 §결정 5 sunset_justification 불필요): consumer 가 AWS / K8s / multi-host topology 도입 시 InfraArchitect 신설 carrier 재발의 trigger. 본 철회는 약화 (scope 축소) 아닌 미도입 결정 — ratchet top-down 강화 방향 무관.

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 7 은 ADR-042 의 결정 1~6 본문 변경 0건. 변경 = (a) §결정 1 inline marker (Amendment 7 발화 marker — Sonnet (a) 2 agent 추가) (b) 본 `## Amendment 7` body section (c) frontmatter amendment_log row 7 + related_stories CFP-676 append. tier criteria (결정 1) + invariant (결정 2) + 신규 agent ADR 의무 (결정 3) + inheritance (결정 4) + Haiku rollback (결정 5) + 재-audit (결정 6) 모두 정책 변경 0건. ratchet 강화 방향 (신규 agent 2종 도입 — scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불필요 (frontmatter amendment_id:7 `sunset_justification: null`).

### Scope 경계 (S1 = 정책 SSOT 만)

본 Amendment 7 = **정책 SSOT codify 만**. agent file (`.md`) 실 신설 / rename / 내용 작성 = W2 S3 (codeforge-design plugin sibling Story) 영역. ADR-042 §결정 3 의 "해당 lane plugin agent file 의 `model:` field 와 동기" 의무 = W2 S3 sibling PR 에서 충족 (codeforge-design plugin MINOR bump trigger — [ADR-023](ADR-023-lane-plugin-lifecycle.md) / [ADR-037](ADR-037-plugin-version-bump-rule.md) 정합). 본 S1 PR 의 agent file 변경 0건 invariant (doc-only fast-path — [ADR-054](ADR-054-doc-only-story-fast-path.md)).

### Cross-ref

- ADR-014 Amendment 4 (CFP-676 atomic carrier) — InfraOperationalArchitect §7.4 primary 4-sub + ProductionEvidence dual-spawn disjoint axis
- ADR-72 mirror cross-ref (CFP-676) — ProductionEvidenceDeputy ↔ InfraOperationalArchitect disjoint
- ADR-044 reaffirm 단락 (CFP-676) — CodeArchitect / ArchitectAnalyst = 4-tuple flat spawn (논리적 그룹핑)
- ADR-068 I-5 적용 declare (CFP-676) — spawn token cost dimensional empirical grounding
- CLAUDE.md "Deputy mandate 매트릭스 (codeforge-design lane)" — 6 → 5 permanent + 3 CONDITIONAL (+ ArchitectAnalyst sub-tuple)
- [ADR-046](ADR-046-researcher-role-redefinition.md) — ResearcherAgent (Opus, reshape mandate) ≠ ArchitectAnalyst (Sonnet, single-axis 기존 설계 분석) — 두 analyst 역할 disjoint (reshape vs read-only prior-art)

---

## Amendment 8 — CFP-1086 Story-1 design lane 7+3+1 roster 재편 (BackendArchEpic Phase 2)

**날짜**: 2026-05-20

### 동기

CFP-1026 W1 (Amendment 7 / `abcd92bf`) 가 5 permanent + 3 CONDITIONAL + 4-tuple sub-tuple 으로 atomic carrier 확정 후, DataArchitect deputy 가 빅데이터 OLAP (Parquet / 객체저장소 / DuckDB) + 서비스 RDB OLTP (PostgreSQL / SQLAlchemy / Alembic) 두 영역 모두 책임. 산업 표준 (데이터 엔지니어 vs 백엔드 엔지니어 직무 분리) 위배 + OLAP/OLTP mental context switch cost. 깊은 동기 — (b) 별 session 진행 중 sibling 배포 lane Epic 에서 RDB schema 정책 결정자 부재로 cross-repo 결정 막힘 (mechanism gap) + (c) §3/§7/§11 작성 시 DataArch + SecurityArch + InfraOpArch 가 RDB 영역에서 ownership 부딪힘 RACI 충돌 (mechanism gap).

본 Amendment 8 = CFP-1086 BackendArchEpic Story-1 = 7 deputy axis 확정 ADR carrier 묶음. sibling ADR carriers (ADR-068 Amendment 2 wording SSOT chief tie-break ladder P1 + ADR-086 신설 Deputy 신설 결정 framework P7) atomic 동반.

### 변경 사항

| Agent | 변경 | model tier | §결정 1 매트릭스 row |
|---|---|---|---|
| **AggregateArchitectAgent** | **신설** — RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound aggregate boundary + Alembic 정책 (tool-agnostic policy layer) | **Sonnet** (claude-sonnet-4-6) | **Sonnet (a)** "Single-mandate advocacy within multi-deputy debate — RDB OLTP 영역 단일 축 주장" |
| **APIContractArchitectAgent** | **신설** (skeleton at S1 / body 심화 = S2) — transport (REST/GraphQL/gRPC/WebSocket) + API versioning + DTO contract + OpenAPI/GraphQL schema + contract testing (Pact 등) | **Sonnet** (claude-sonnet-4-6) | **Sonnet (a)** 동일 |
| CodeArchitectAgent | **rename → ModuleArchitectAgent** + mandate 정정 (도메인 모델 invariant 영역 제거 — module boundary + dependency direction + layered/hexagonal/clean module-level only). 도메인 모델 invariant 영역 = AggregateArch primary | **Sonnet 유지** | (a) 무변경 — 명칭 정확화 + mandate scope 정정 (axis 명확화) |
| DataArchitectAgent | **mandate 축소** — RDB OLTP 영역 제거 (PostgreSQL / SQLAlchemy / Alembic / 트랜잭션 경계 / 도메인 모델 모두 AggregateArch 분리). 빅데이터 OLAP only (Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계) | **Opus 유지** (§결정 1 (d) Security / safety boundary owner — OLAP 영역에서도 schema rollback / 데이터 무결성 invariant 유지) | (d) 무변경 — mandate scope 축소만 |

### CONDITIONAL applicability 신설 (P2)

기존 3 CONDITIONAL (LiveOps / LiveOrdering / ProductionEvidence — Live touching Story 또는 production cutover Story trigger) 에 **AggregateArch applicability** 추가 (3+1 CONDITIONAL):

- **trigger**: `project.yaml aggregate_arch.applicable: bool` (default `true`)
- **non-applicable consumer 영역**: frontend-only project / API-only project (외부 RDB consume only) / external-managed RDB (consumer 가 schema 제어권 없음)
- **mechanism**: LiveOps / LiveOrdering / ProductionEvidence CONDITIONAL 패턴 재사용 (consumer overlay flag 기반 conditional spawn)
- **consumer carrier**: P7 framework §결정 2 5-checklist (3) consumer carrier 충족 — `project.yaml aggregate_arch.{applicable, migration_tool}` schema declare (Tool scope B — tool-agnostic policy layer + 9-enum migration_tool override default alembic)

### model tier 결정 근거 (Sonnet — 재론 금지 carry-over)

AggregateArch / APIContract = §결정 2 invariant ("Sonnet 으로 대체 가능한 수준의 얕은 역할만 맡고 있다면 역할이 제대로 잡히지 않은 것이다") 의 **역방향 적용** — 본 2 agent 는 처음부터 single-mandate advocacy 로 정의 (AggregateArch = RDB OLTP 영역 단일 축 주장 / APIContract = transport contract 영역 단일 축 주장). multi-source synthesis (deputy 산출물 dedup + 종합 판정) 책임은 ArchitectAgent chief (Opus) 단독 보유 — 본 2 agent 는 자기 축 사실 / 주장만 정확히 전달하면 충분. CodebaseMapper / Refactor / ArchitectAnalyst (4-tuple sub-tuple Sonnet) + CodeArchitect Amendment 7 동질 패턴. Sonnet 4.6 reasoning depth 가 본 mandate 를 fully cover.

**model tier (Sonnet) 의사결정 재수행 금지** — brainstorm Phase 0+1 (사용자 4-turn dialog: Q1 WHY → Q2 명칭 → Q2-prime ModuleArch → Q3 Tool=B → Q4 AggregateArch → Q4-prime DDDArch reject → Q5 ACK all) 에서 ArchitectAgent + Codex 최종 확정 carry-over. 본 Amendment 8 = codify 만.

ModuleArch (CodeArch rename) / DataArch (mandate 축소) = rename / scope change only — model tier 무변경 (Sonnet / Opus 각 유지).

### DDDArchitectAgent 신설 reject 명문화 (axis 미정합)

Phase 1 Q4-prime 에서 사용자 발의 — DDDArchitectAgent (Domain-Driven Design 학파 advocate). reject 사유:

- **axis 미정합** — method / 학파 layer (vs. mandate / mandate scope layer). 다른 deputy 는 mandate scope axis (RDB OLTP / OLAP / transport / module boundary / security policy / 운영 리스크 / test contract) 로 disjoint, DDD = 방법론 layer 로 axis 충돌 (orthogonal 하지 않음 — ADR-086 §결정 1 axis 분석 의무 위배)
- **ModuleArch wording overlap** — DDD bounded context + aggregate boundary 영역 이미 ModuleArch (module-level) + AggregateArch (aggregate invariant) 가 cover. DDDArch = wording-only superset, mandate scope 추가 없음
- **consumer applicability 축소** — DDD 학파 채택 consumer 만 활성 — codeforge 전체 consumer 영역 축소

본 reject 는 **약화 (scope 축소) 아닌 미도입 결정** — ratchet top-down 강화 방향 무관 (ADR-058 §결정 5 sunset_justification 불필요).

**미래 재발의 trigger** (ratchet 위반 아님): 별 consumer 가 DDD 학파 전용 mandate scope 신설 evidence 누적 시 (mandate scope disjoint 신규 영역) DDDArch 재발의 carrier 가능. 본 reject = axis 미정합 결정 — 미도입 결정 영역.

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 8 은 ADR-042 의 결정 1~6 본문 변경 0건. 변경 = (a) 본 `## Amendment 8` body section (b) frontmatter amendment_log row 8 + related_stories CFP-1086 append + related_adrs ADR-068 / ADR-086 append. tier criteria (결정 1) + invariant (결정 2) + 신규 agent ADR 의무 (결정 3) + inheritance (결정 4) + Haiku rollback (결정 5) + 재-audit (결정 6) 모두 정책 변경 0건. ratchet 강화 방향 (신규 agent 2종 도입 — scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불필요 (frontmatter amendment_id:8 `sunset_justification: null`).

### Mechanical enforcement — review-verdict-v4 v4.5 → v4.6 MINOR (deputy_axis_restructure_self_check_passed field)

본 Amendment 8 carrier = `review-verdict-v4 v4.6` MINOR bump. 신규 optional bool field `deputy_axis_restructure_self_check_passed` 추가 — ArchitectAgent (또는 후속 Amendment carrier) 가 ADR-086 §결정 2 5-checklist (axis disjoint / cost-token budget / consumer carrier / sibling Epic align / deferred trigger 명시) 통과 시 true. false 시 ArchitectAgent re-spawn (FIX 의무). 적용 lane = design lane (deputy roster 변경 carrier Story 만 적용 — Amendment 8 = 본 framework self-application 첫 사례).

### ADR-068 I-5 dimensional empirical grounding 적용 (spawn count)

본 Amendment 8 의 spawn count 변경 — CFP-1026 W1 후 평균 22 (5 permanent + 3 sub-tuple + chief author + PL = 8 평균 + 14 CONDITIONAL/contributor activation ratio) → 본 Amendment 8 후 평균 28 (7 permanent + 3 sub-tuple + chief + PL = 10 평균 + 18 CONDITIONAL ratio, 1.27배 추가). full activation 34 → 40 (1.18배). 본 spawn count 증가 = ADR-068 I-5 `count` dimension quantitative parameter — empirical-source annotation 의무.

- value: 평균 22 → 28, full 34 → 40
- unit: spawn count (deputy + sub-tuple + chief + PL 합계, lane spawn 1회당)
- empirical_source: TBD (local probe / wiretap script 부재 — ADR-068 I-5 Mitigation 2 `[empirical-source: TBD]` explicit TBD 기재). Story-1 packet sample annotation 의무 (P7 framework §결정 2 5-checklist (2) cost-token budget 충족).

본 backref = ADR-068 I-5 본문 / verdict field / 10 dimension enum / mitigation 4종 **0건 변경 invariant** (CFP-676 W1 backref 답습 패턴).

### Scope 경계 (S1 = 정책 SSOT 만)

본 Amendment 8 = **정책 SSOT codify 만**. agent file (`.md`) 실 신설 / rename / 내용 작성 = 본 Story-1 codeforge-design plugin sibling PR scope (CFP-676 W1 → W2 분리 패턴과 달리 — 본 Epic 의 S1 = ADR carrier + agent file atomic 묶음, doc-only fast-path ADR-054 정합 5-repo atomic). ADR-042 §결정 3 의 "해당 lane plugin agent file 의 `model:` field 와 동기" 의무 = 본 Story-1 atomic 5-PR (wrapper + codeforge-design + codeforge-pmo + internal-docs + marketplace) 으로 충족.

### Cross-ref

- ADR-068 Amendment 2 (CFP-1086 Story-1 sibling carrier — wording SSOT 충돌 시 chief tie-break ladder P1: RACI lookup → ADR-068 invariant → chief judgement + ADR Amendment 발의)
- ADR-086 (CFP-1086 Story-1 신설 carrier — Deputy 신설 결정 framework P7, 본 Amendment 8 = self-application 첫 사례). axis 분석 의무 + 5-checklist self-app + deferred carrier path
- ADR-014 Amendment 4 (Amendment 7 cross-ref 답습) — InfraOperationalArchitect §7.4 primary 4-sub + ProductionEvidence dual-spawn disjoint axis (본 Amendment 8 영역 외 invariant 보존)
- ADR-064 §결정 1 CFP scope unitary — 본 Amendment 8 = CFP-1086 단일 Story-1 carrier (Amendment 9 = CFP-1079 별 session)
- ADR-076 (declarative reconciliation upgrade) — 본 Amendment 8 의 P7 framework axis 분석 + 5-checklist = ADR-076 desired / current / converge 3-layer 패턴의 governance domain 동형 답습
- CFP-1079 (OpsExecutionArchitect 신설 + InfraOperationalArch §7.4 mandate 보강 sibling Epic) — 본 Phase 1 PR open 시점 OPEN, PR 0건 — 본 Amendment 8 = 선점, CFP-1079 후속 = Amendment 9 별 session
- CLAUDE.md "Deputy mandate 매트릭스 (codeforge-design lane)" — 5 → 7 permanent + 3 → 3+1 CONDITIONAL + 4-tuple sub-tuple (변경 0)
- [ADR-046](ADR-046-researcher-role-redefinition.md) — ResearcherAgent (Opus, reshape mandate) ≠ AggregateArch (Sonnet, single-axis RDB OLTP) — 두 역할 disjoint (reshape vs single-mandate advocacy)
