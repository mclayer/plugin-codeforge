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
related_stories: []
related_adrs:
  - ADR-009
  - ADR-013
  - ADR-022
  - ADR-035
  - ADR-037
  - ADR-039
  - ADR-046
related_files:
  - .claude-plugin/plugin.json
  - CLAUDE.md
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
- 5 design deputy: CodebaseMapperAgent · RefactorAgent · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent
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
| **Opus** | claude-opus-4-7 | (a) Multi-source synthesis (3+ deputy / lane / contract input dedup + 종합 판정) — 모든 PL · ArchitectAgent chief. (b) Independent reasoning peer to external GPT-5 (ClaudeReviewAgent — Codex 와의 의도적 reasoning depth 매칭). (c) High-stakes domain interpretation (DomainAgent — Live trading / 금융 / 헬스 데이터 등 invariant 누설 위험). (d) Security / safety boundary owner (SecurityArchitectAgent · OperationalRiskArchitectAgent · DataMigrationArchitectAgent · TestContractArchitectAgent — §7 trust boundary / §7.4 DR / §11 schema rollback / §8 perf baseline). (e) Real-funds risk owner (LiveOpsDeputyAgent · LiveOrderingDeputyAgent — CFP-77 CONDITIONAL). (f) Cross-Story pattern analysis + ADR proposal (PMOAgent). (g) Deep research with reshape mandate (ResearcherAgent — per [ADR-046](ADR-046-researcher-role-redefinition.md) (2026-05-09)). |
| **Sonnet** | claude-sonnet-4-6 | (a) Single-mandate advocacy within multi-deputy debate — read-only 조사 + 자기 mandate 측 단일 축 주장 (CodebaseMapperAgent — existing facts only, RefactorAgent — pattern advocacy only). (b) Implementation work — code write / refactor / test 구현 (DeveloperAgent · DeveloperPLAgent · 2 webapp preset). |
| **Haiku** | claude-haiku-4-5 | (a) Test runner / 결과 수집 — minimal reasoning (TestAgent). (b) External tool wrapper — 본체 reasoning 은 external (Codex GPT-5 / GPT-5.4) 가 수행, Claude 는 prompt 조립 / output relay 만 (CodexReviewAgent · RequirementsAnalystAgent). (c) Mechanical pattern execution — 입력 명세(Change Plan §3 + Story §8)가 충분히 structured되어 creative/diagnostic reasoning 없이 패턴 기반 생성이 가능하고, 오류 발생 시 FIX 루프가 CI/테스트로 즉시 감지 가능한 경우 (InfraEngineerAgent · QADeveloperAgent · DataEngineerAgent — Amendment 2). |

### 결정 2: 본 ADR 발효 시점 변경 사항 (2 sibling PR scope)

**plugin-codeforge-design sibling PR** (별도 — 본 ADR PR merge 직후):
- CodebaseMapperAgent: Opus 4.7 → **Sonnet 4.6**
- RefactorAgent: Opus 4.7 → **Sonnet 4.6**

근거: 양 agent 모두 3-way deputy debate (Mapper = existing codebase fact 보고, Refactor = decoupling/pattern advocacy, SecurityArch = threat) 안에서 **single-mandate advocacy** 패턴. read-only 조사 + 자기 축 단일 주장. multi-source synthesis 책임은 ArchitectAgent chief (Opus) 가 수행. Sonnet 4.6 의 reasoning depth 가 본 mandate 를 fully cover.

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

**rollback 트리거 (agent별 독립)**:
1. **점진적 rollback**: 해당 agent 관련 FIX 루프 횟수가 전환 전 baseline 대비 30% 초과 시 → 해당 agent 단독 rollback (Sonnet 4.6 복원 + Amendment 2 해당 항목 revert)
2. **즉시 rollback**: P0·P1 severity 결함이 Haiku 전환 agent에서 발원 확인 시 → 해당 agent 즉시 rollback
3. **전체 rollback**: 3 agent 중 2개 이상 즉시 rollback 트리거 발생 시 → Amendment 2 전체 revert

### 결정 6: 재-audit 트리거 규칙 (Amendment 2)

다음 이벤트 발생 시 나머지 Sonnet agent (DeveloperPLAgent · DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent) 재평가 의무:
1. Haiku major 버전 업 (Haiku 4.x → Haiku 5.x)
2. 기존 Sonnet agent의 mandate가 "패턴 실행" 방향으로 재정의될 때 (결정 3 ADR amendment 또는 별도 ADR cross-ref 발동 시)

## 근거

### 왜 PL · ArchitectAgent chief 는 Opus 인가

PL 의 책임 = lane synthesis (3+ sub-agent finding dedup + severity 종합 + `pl_recommendation` 결정). ArchitectAgent chief 의 책임 = 6-8 deputy 산출물 (CodebaseMapper / Refactor / SecurityArch / OpRisk / TestContract / DataMigration + 2 CONDITIONAL Live) 통합 → Story §1-§11 + Change Plan §3 + ADR draft 작성. 양쪽 다 multi-source 가 충돌 / 누락 / 모순 케이스에서 architectural judgment 필요. Sonnet 으로 swap 시 dedup / 종합 판정 layer 가 shallow 해져 FIX root cause 오판 / responsibility leak 발생 위험 — [ADR-021](ADR-021-phase-gap-measurable-signal.md) R4 detection source 자체 약화.

### 왜 ClaudeReviewAgent 는 Opus 인가

[ADR-001](ADR-001-review-agent-unification.md) (review agent unification) 은 lane-agnostic 2-vendor (Claude + Codex) worker pattern 을 채택. Codex 측 = GPT-5 (high reasoning). Claude 측이 Sonnet 이면 reasoning depth 비대칭 → "Claude 가 Codex 의 finding 을 dedup 하지 못한다" 패턴 발생. 의도적으로 Opus = GPT-5 peer matching.

### 왜 SecurityArch / OpRisk / DataMigration / TestContract deputy 는 Opus 인가

[deputy mandate 매트릭스](../../CLAUDE.md) 에서 본 4 deputy 는 §7 / §7.4 / §11 / §8 의 primary owner. 각 영역의 invariant 누락 = SecurityTest / 보안 테스트 / 구현 테스트 단계에서 P0 차단 trigger. Sonnet 으로 swap 시 invariant 정의 누락 위험 ↑ — review-verdict v3 의 P0 차단이 사후 발견. 비용보다 catch-rate 우선 결정.

### 왜 DomainAgent 는 Opus 인가

DomainAgent 는 사용자 자연어 요구사항 → domain invariant translation. mctrader (codeforge 데뷔 consumer) 의 KRW 거래소 + real funds + Live ordering domain 에서 invariant 누설 (예: partial fill reconciliation invariant 누락) = real funds 손실 위험. high-stakes domain interpretation 은 token cost vs risk 비대칭 — Opus 유지.

### 왜 PMOAgent 는 Opus 인가

PMOAgent 의 mandate = (a) Epic 창설 (multi-Story dependency graph) + (b) Story 완료 retro (cross-Story 패턴 분석 → ADR proposal). (b) 가 특히 deep — 6+ Story 의 review / FIX / test outcome 을 cross-correlate → 새 ADR 가 필요한지 판단. Sonnet 의 cross-source pattern detection 은 본 mandate 에 shallow.

### 왜 CodebaseMapper · Refactor 는 Sonnet 인가

양 agent 모두 **single-mandate advocacy** 패턴:
- CodebaseMapperAgent: 기존 codebase fact 만 보고 (file structure / API surface / 의존성 그래프) — read-only mode
- RefactorAgent: pattern decoupling / 일관성 advocacy 만 — 자기 축 단일 주장

3-way debate 의 dedup / 종합은 ArchitectAgent chief (Opus) 가 수행. 양 deputy 는 자기 축 사실 / 주장만 정확히 전달하면 충분 — Sonnet 4.6 reasoning depth fully cover.

핵심 원칙 발현: "Sonnet 으로 대체 가능 = role 재정의 시그널" 의 역방향 적용 — 본 2 deputy 는 처음부터 single-mandate 로 정의되었으므로 Sonnet 이 적정.

### 왜 DeveloperPLAgent · DeveloperAgent · webapp preset 은 Sonnet 인가

DeveloperPLAgent / DeveloperAgent / 2 webapp preset (BackendDeveloperAgent · FrontendDeveloperAgent) 모두 implementation work — Change Plan + Story §3·§7·§11 SSOT 로부터 코드 작성. Architecture decision 은 design lane 에서 종결, develop lane 은 그 결정을 충실히 implement. Sonnet 4.6 의 코드 생성 능력은 본 mandate 충분.

DeveloperPLAgent 가 1차 FIX root cause 진단을 수행하지만, 최종 판정은 ArchitectPLAgent (Opus) 가 수행 — 1차 진단은 Sonnet level 충분.

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
