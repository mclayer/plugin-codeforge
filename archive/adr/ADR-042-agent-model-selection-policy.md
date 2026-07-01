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
  - amendment_id: 10
    date: "2026-05-21"
    status: applied
    summary: "CFP-1126 — AggregateArchitectAgent deprecate + ModuleArchitectAgent mandate 확장 (boundary axis advocate 통합, Amendment 8 partial retroactive rollback). 7 permanent → 6 permanent + 3+1 CONDITIONAL (AggregateArch applicability → ModuleArchitect CONDITIONAL carry-over 보존, frontend-only / API-only / external-managed RDB consumer non-applicable). ModuleArchitect mandate 확장 — module-level boundary (CodeArchitect rename from Amendment 7 본 mandate) + aggregate-level boundary (AggregateArch from Amendment 8 흡수). 사용자 직권 minimal path 2번째 적용 — CFP-1110 paired Amendment paradox-break 후속 carrier. ADR-058 §결정 5 sunset_justification first applied carrier (ratchet 축소 첫 시도, 약화 방향 evidence-grounded justification). Researcher 평가 net 35% 정당화 (verify-before-trust + Epic gate 영역만 net positive) + Codex ROI indeterminate-부정쪽 confidence medium 수렴 + synthesizer-stale-reference pattern_count 6 (CFP-722/801/792/810/819/825) + ADR-082 Amendment 5 §결정 1 sub-scope (1-C) 구조적 원인 #2 직접 인용 (codeforge-design lane fan-out 불균형 chief + 7 deputy + 4-tuple = 12+ agent advocacy vs 1 user 요구 weight 비대칭). minimal path 정합 — Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 (사용자 승인 2026-05-21 KST) — closed-loop break 외부 결정 채널 2번째. Wave 1 = declarative anchor only (ADR-042 정책 SSOT). Wave 2 mechanical (codeforge-design plugin AggregateArchitectAgent agent file 실 deprecate + cross-repo sibling sync ADR-010 정합) = 별 CFP carrier (deferred-followup)."
    ref: CFP-1126
    carrier_story: CFP-1126
    sunset_justification: "ADR-058 §결정 5 first applied carrier (약화 방향 의무 — ratchet 축소 첫 시도). Amendment 8 (2026-05-20) 가 boundary axis 를 AggregateArch (RDB OLTP aggregate-level) + ModuleArch (CodeArchitect rename, module-level) 2 agent 로 axis disjoint codify했으나 본 Amendment 10 = partial rollback (AggregateArch → ModuleArch 통합 흡수, boundary axis 단일 advocate). evidence-grounded justification 3 axis — (a) **empirical evidence**: Researcher (general-purpose) + Codex (codex:rescue, GPT-5) 병렬 critical evaluation 수렴 결과 = codeforge dogfooding net 35% 정당화 (verify-before-trust + Epic gate 영역만 net positive), Codex ROI indeterminate-부정쪽 confidence medium. denominator (consumer-protective fraction) 측정 부재 + sunset asymmetry (실 retire 0건 since codeforge 정상 운영 진입) + self-referential dogfood paradox 만성화. (b) **pattern_count evidence**: synthesizer-stale-reference pattern_count 6 reach (CFP-722/801/792/810/819/825) + unverified-self-write-claim super-class 5 + scope drift 만성 6+ (CFP-758) + DesignReviewPL cross-PL false-negative (CFP-906) — ADR-082 Amendment 5 §결정 1 sub-scope (1-C) 구조적 원인 #2 직접 인용 (chief + 7 deputy + 4-tuple = 12+ agent advocacy vs 1 user 요구 weight 비대칭). (c) **single-axis sufficiency**: ModuleArchitect (boundary axis advocate) 가 module-level + aggregate-level boundary 통합 mandate cover 충분 — Amendment 8 brainstorm 4-turn 에서 사용자 정합 carrier 시점 RACI 충돌 (chief synthesis 가 두 axis dedup 비용) 가 정합 근거였으나, Researcher 평가 evidence 누적 후 chief synthesis 1 axis 압축 = fidelity loss source 직접 감소 evidence-grounded. ratchet top-down 강화 invariant (ADR-064 §self-application) 의 evidence-gated exception 첫 carrier — ADR-058 §결정 5 의 mechanical 약화 차단 logic 통과 (forbid-scope 축소 아닌 mechanism 단일화 — invariant carrier 보존, axis dedup carrier 변경 only). is_transitional: false 유지 (영구 정책, Amendment 10 = 영구 ratchet 축소)."
    affected_agents:
      - AggregateArchitectAgent (deprecated — codeforge-design, mandate carry-over to ModuleArchitectAgent. agent file 실 deprecate = Wave 2 별 CFP carrier)
      - ModuleArchitectAgent (mandate 확장 — module-level boundary + aggregate-level boundary 통합 advocate. CONDITIONAL applicability carry-over from AggregateArch — `project.yaml aggregate_arch.applicable: bool` 보존)
    cross_ref:
      - ADR-058 §결정 5 (sunset_justification first applied carrier — 약화 방향 evidence-grounded justification carrier)
      - ADR-082 Amendment 5 §결정 1 sub-scope (1-C) (구조적 원인 #2 직접 인용 — 본 Amendment 10 = 평가 결과 직접 follow-through)
      - ADR-064 §self-application top-down ratchet (evidence-gated exception 첫 carrier)
      - CFP-1110 (paired Amendment paradox-break first application — 본 CFP-1126 = 2번째 적용)
      - Amendment 8 (CFP-1086, 2026-05-20) (partial retroactive rollback — boundary axis 영역만, DataArch / APIContract 영역 보존)
  - amendment_id: 11
    date: "2026-05-21"
    status: applied
    summary: "CFP-1155 (CFP-1111 Wave 2 Story-4) — UpgradeAgent walker model tier 확정 (declarative Sonnet → imperative walk Opus 상향). ADR-098 §결정 2 model tier 재평가 의무 carry — Wave 1 declare only 였던 tier 가 Wave 2 Story-4 runtime mandate body (walk + plan + apply 3-stage) 확정 후 실 결정. tier = Opus (§결정 1 Opus (a) Multi-source synthesis). 근거: plan stage = 7-plugin self-owned CHANGELOG.md 다중 source dedup + min_prerequisite_version topological resolve (DAG) + importance_score 종합 판정 = multi-source synthesis 깊이 (§결정 1 Opus (a) '3+ ... input dedup + 종합 판정' 정합). apply stage 의 per-family atomic transaction (structured mechanical, CI/rollback 즉시 감지 — Haiku/Sonnet 신호) 단독이면 얕으나, walk+plan 의 multi-source changelog synthesis 가 §결정 2 invariant ('Sonnet 으로 fully cover 가능 = role 재정의 시그널') 의 Sonnet fully-cover 불가 영역 — Sonnet 으로 내리면 7-source dedup + topological resolve depth shallow. 기존 declarative UpgradeAgent (CFP-743) 의 model:sonnet = declarative 9-domain diff (단일 wrapper SSOT source reconcile, multi-source synthesis 없음) 정합이었으나, imperative walk paradigm 전환 후 mandate depth 상향 (paradigm shift = role 재정의 = §결정 2 invariant 적용 후 tier 재판정). ratchet 강화 방향 (Sonnet → Opus 상향 = scope 강화, ADR-058 §결정 5 정합 — 약화 0건). UpgradeAgent ownership = codeforge-pmo (ADR-098 §결정 1) — model field 동기 = codeforge-pmo sibling Story (실 agent file edit). 본 Amendment = 정책 SSOT (tier 확정) only, agent file model field edit = codeforge-pmo sibling carrier."
    ref: CFP-1155
    carrier_story: CFP-1155
    sunset_justification: null
    affected_agents:
      - UpgradeAgent (declarative Sonnet → imperative walk Opus, codeforge-pmo — ADR-098 ownership 흡수. agent file model field edit = codeforge-pmo sibling Story)
    cross_ref:
      - ADR-098 §결정 2 (model tier 재평가 의무 declare — 본 Amendment 11 이 Wave 2 Story-4 실 tier 확정 carry)
      - ADR-097 (paradigm replacement governance anchor — declarative → imperative paradigm shift = role 재정의 trigger)
      - ADR-076 (declarative UpgradeAgent runtime SSOT — paradigm replace 진행 중, model:sonnet → Opus 상향 source)
      - imperative-walker-protocol-v1 §2.F.2 (UpgradeAgent runtime ownership + model_tier_reassessment: required cross-ref)
      - ADR-068 §결정 1 I-5 (walker walk source count 7 / grace window 12mo·9mo K8s empirical grounding cross-ref)
  - amendment_id: 12
    date: "2026-05-30"
    status: applied
    summary: "CFP-1845 — model tier 정책의 버전 핀(claude-opus-4-7 / claude-sonnet-4-6 / claude-haiku-4-5)을 별칭(opus / sonnet / haiku)으로 전환. 별칭 = 플랫폼이 항상 최신 tier 버전으로 해석 → 버전 릴리스마다 전 파일 일괄 변경 chore 제거 + 자동 최신 추적. tier 분류(Opus/Sonnet/Haiku role pattern criteria) 정책 강도 불변 — 버전 표기 방식만 별칭화 (ratchet 약화 아님, ADR-058 §결정 5 정합 — tier 분류 logic 변경 0건). 사용자 directive (2026-05-30 KST) verbatim: 'opus, sonnet, haiku 모두 최신 버전으로 지칭하도록 해'. §결정 1 tier 표 4 row (Opus / Sonnet / Haiku / Opus pilot) Model 컬럼 별칭화. amendment_log·inventory 등 역사 서술의 과거 버전 언급(Opus 4.7 → Sonnet 4.6 등)은 frozen audit trail 로 보존 (Event Sourcing — 과거 결정 시점 박제 정상 영역). ADR-057 §결정 1 (Orchestrator 버전 핀) Amendment 4 동시 개정 sibling (CFP-1845 atomic). cross-repo: 6 lane plugin agent file `model:` field 별칭 전환 = follow-up PR."
    ref: CFP-1845
    carrier_story: CFP-1845
    sunset_justification: null
    affected_agents:
      - "전체 tier 표 (개별 agent tier 분류 변경 0건 — 버전 표기 방식만 별칭화)"
    cross_ref:
      - ADR-057 Amendment 4 (CFP-1845 — Orchestrator 버전 핀 → 별칭 sibling, atomic)
  - amendment_id: 13
    date: "2026-06-19"
    status: applied
    summary: "CFP-2364 — RefactorAgent Reusability 1급 축 신설 (ISO/IEC 25010 유지보수성 gap 충당). 실증 결과 RefactorAgent 가 ISO/IEC 25010 Maintainability 5축 (Modularity / Reusability / Analysability / Modifiability / Testability) 중 Modularity 1축 (decoupling / pattern / interface 분리) 만 1급으로 다루고 Reusability 명시 공백 (증거 ①~⑦). 기존 3 카테고리 (a Decoupling / b Pattern / c Interface) → 4 카테고리 (+ d Reusability) 확장 — 카테고리 (d) 신설: 중복 코드 제거 · 공통 추상 추출 · DRY/WET · 재사용 가능 단위 식별. 트리거 = rule-of-three (동일/유사 블록 3회 이상) / duplication-ratio 임계 초과 / cross-module 동형 로직 발견 시 공통화 제안. DRY/WET 는 (b) Pattern 에서 (d) 로 이관 (개념 정합 — 본질이 중복/재사용), (b) 는 아키텍처 패턴 (Hexagonal/Clean/Ports&Adapters) 만 retain. output 슬롯 (d) Reusability advocacy 신설 (중복 위치 + 추출 대상 공통 단위 + 재사용 단위 배치 ModuleArch consult 표식 + 측정 신호 + repo 분해 escalation 표식). scope guard escalation 예외 — cross-cutting 공통추출 / repo-level 분해는 본질적으로 cross-module/global 이므로 요건 범위 밖이라도 escalation-tier 제안 가능 (escalation 표식 + ArchitectAgent 판정 회부 의무, 그 외 무관한 전역 리팩터링 여전히 금지). repo-level 분해 advocacy (응집 cluster → 별 deploy/ownership 단위 분리) escalation-tier 신설. 측정 연동 — (d) 제안마다 before 신호 (duplication ratio / clone 수 / 제거 예상 중복 LOC) emit → ArchitectAgent 통합 + 구현리뷰 게이트 falsifiable 검증 (증거 ⑤ 충당). axis disjoint = RefactorAgent reusability/decoupling advocacy (중복·공통추출·repo-split pressure 식별·제안) ↔ ModuleArch boundary authority (경계 placement 결정) — RefactorAgent 는 pressure 제안만, 경계 확정은 ModuleArch + ArchitectAgent chief. RefactorAgent = 기존 sub-tuple agent 의 mandate 확장 (신설 아님) — roster 6 permanent + 3 sub-tuple 카운트 무변경, model tier Sonnet 무변경. ADR-086 axis 분석 lens adjacent-case 적용 (axis disjoint + 5-checklist as 도구 — mandate 확장은 ADR-086 explicit scope 신설/미도입/rename/축소 미열거이므로 framework 전면 self-application 주장 아님). SSOT propagation 3원본 (RefactorAgent.md + skills/deputy-mandate/SKILL.md + plugins/codeforge-design/CLAUDE.md mirror). bump 0.26.0 → 0.27.0 MINOR (mandate 확장 — ADR-037). marketplace version sync (ADR-063). ratchet 강화 방향 (카테고리 3 → 4 = scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불요."
    ref: CFP-2364
    carrier_story: CFP-2364
    sunset_justification: null
    affected_agents:
      - RefactorAgent (mandate 확장 — decoupling / pattern / interface 분리 3 카테고리 → + reusability(d) 4 카테고리, codeforge-design — Sonnet 무변경. 신설 아님 — 기존 sub-tuple agent 의 mandate scope 확장)
    cross_ref:
      - ADR-086 (CFP-2364 — Deputy 신설 결정 framework 의 axis 분석 lens adjacent-case 적용 — axis disjoint + 5-checklist as 도구. mandate 확장은 ADR-086 explicit scope 미열거이므로 framework 전면 self-application 주장 아님)
      - ADR-063 (marketplace atomic version sync — codeforge-design 0.26.0 → 0.27.0 MINOR mirrored field)
      - ADR-037 (plugin version bump rule — mandate 확장 = MINOR bump trigger)
  - amendment_id: 14
    date: "2026-06-19"
    status: applied
    summary: "CFP-2369 — RefactorAgent (d) Reusability 축 측정 연동 Phase-2 mechanical wire (warning-tier duplication-ratio 측정). CFP-2364 Amendment 13 가 (d) Reusability 축을 1급 advocacy 로 신설하되 측정은 Phase-1 declarative (RefactorAgent 가 before 신호 (duplication ratio / clone 수 / 제거 예상 중복 LOC) emit 하나 자동 측정·enforcement deferred) 로 두었음 (Amendment 13 §변경 사항 '측정 연동 (declaration-only Wave 1)' + ADR-086 5-checklist #5 deferred trigger). 본 Amendment 14 = 그 deferred 를 mechanical wire 로 실현 — warning-tier duplication-ratio 측정 도구 (scripts/check-duplication-ratio.sh) + consumer template (templates/github-workflows/duplication-check.yml) + anti-theater discriminating test (scripts/test-check-duplication-ratio.sh, stub detector 로 dirty/clean RED→GREEN 변별 실증) + evidence-check-registry entry (duplication-ratio-warning, owner_adr ADR-042 / carrier_adr ADR-060, warning tier) codify. detector 계약 = DUPLICATION_TOOL env (target dir → 중복 백분율 stdout) override 가능, 미설정 시 default jscpd (npx --yes jscpd --reporters json) total percentage 추출 — top-level key 는 `statistics`(복수, jscpd v5.0.10 실측 주 키) 이며 파서가 구 버전/문서 변종 `statistic`(단수) 도 허용 (버전 편차 흡수, parse_jscpd_percentage 함수로 추출 — jq `//` + python try-순서). DUPLICATION_THRESHOLD (default 5.0%, 비숫자면 5.0 fallback + warning) 초과 시 ::warning:: emit, 항상 exit 0 (비차단). wrapper-self = src 부재 declarative-only → graceful skip (CI 통과). RefactorAgent 역할 = Grep/Glob 로 중복 위치 식별·verbatim 인용 + 정량 ratio 는 CI 검사 결과 참조 (에이전트 권한 확장 0 — 도구 직접 실행 안 함, CI 가 구동). **여전히 warning-tier (비차단)** — blocking 승격은 evidence 누적 후 별 CFP. **repo-분해 mechanical gate 는 advisory 유지 (out-of-scope)** — 응집 cluster → repo 분리 advocacy 는 ArchitectAgent chief 판정 회부 (mechanical gate 아님). RefactorAgent.md 측정 연동 단락 deferred → tool-grounded 정정 (frontmatter / roster / 카테고리 4 / model tier Sonnet 무변경 — 본문 측정 단락만 갱신). bump 0.27.0 → 0.28.0 (codeforge-design, RefactorAgent 측정 grounding) + 6.27.0 → 6.28.0 (wrapper root codeforge, scripts/templates/workflow/registry 신규 consumer-facing surface) MINOR (ADR-037). marketplace version sync (ADR-063). ratchet 강화 방향 (declarative → mechanical 측정 = enforcement scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불요."
    ref: CFP-2369
    carrier_story: CFP-2369
    sunset_justification: null
    affected_agents:
      - RefactorAgent (측정 연동 단락 deferred → tool-grounded 정정 — mandate / 카테고리 4 / model tier Sonnet 무변경, codeforge-design. 본문 측정 단락만 갱신)
    cross_ref:
      - ADR-042 Amendment 13 (CFP-2364 — Phase-1 declarative substrate, (d) Reusability 축 신설 + 측정 연동 deferred. 본 Amendment 14 = 그 deferred trigger follow-through)
      - ADR-060 (evidence-checks-registry framework — duplication-ratio-warning entry carrier, warning tier)
      - ADR-086 5-checklist #5 (deferred trigger 명시 — CFP-2364 adjacent-case 적용 표의 후속 carrier 별 CFP 가 본 CFP-2369)
      - ADR-037 (plugin version bump rule — consumer-facing surface 신규 = MINOR bump trigger, codeforge-design 0.27.0 → 0.28.0 + wrapper 6.27.0 → 6.28.0)
      - ADR-063 (marketplace atomic version sync — codeforge-design + wrapper mirrored field version 변경)
  - amendment_id: 15
    date: "2026-06-25"
    status: applied
    summary: "CFP-2401 — 비-webapp(backend service) sonnet dev preset 신설. ServiceDeveloperAgent (codeforge-develop presets/backend-service/, model:sonnet, role:dev) new entry. §결정 1(b) Implementation work enumeration 확장 (webapp preset 에 이어 backend-service preset 추가 — 별도 row 불요, Q1). webapp preset = web shape 전용(서버/클라 이원화) + generic DeveloperAgent = ADR-117/CFP-2241 fable→opus override(sonnet 아님) → 비-webapp shape 에 sonnet 구현 tier 구조적 부재. 본 preset = 그 sonnet-구현-preset 패턴을 비-webapp(frontend-less) shape 로 확장. §결정 2 invariant 정당화 — sonnet 배정 1급 근거 = (i) webapp BackendDeveloperAgent 가 동일 구조(path-scope+shape framing→sonnet)로 §결정 1(b) 이미 승인된 선례 (ii) ADR-117 의 generic Developer=fable / webapp=sonnet 분류가 비-webapp sonnet 구현 tier 구조적 부재를 실측 뒷받침. 실 role delta = path-scope + 그 위 sonnet tier 실현으로 정직 한정 (preset-packaging/framing 은 배포·문서 포장, role delta 아님 — over-claim 정정). path-scope = web-특화 2종(templates/static) deny 만 제거, DataEngineerAgent(haiku core) 경계 2종(adapters/storage·adapters/sources) deny 는 webapp BackendDeveloperAgent 선례대로 보존(DataEng allow 경로 — 제거 시 충돌). §결정 6 재-audit 미발동 명시 (신규 추가 ≠ 기존 named Sonnet agent mandate 재정의). §결정 3 정합 (codeforge-develop MINOR bump 0.10.4→0.11.0 + marketplace sync ADR-063). inventory 본문(:234 '2 webapp preset')은 dated snapshot('현재 agent inventory (2026-05-09)')이라 본문 미수정 — 본 Amendment body 에서 preset 2→3 명시 (Amendment 12 는 model 버전 표기 freeze 의 별개 선례, preset 개수 freeze 아님). ratchet 강화 방향(preset 2→3 = scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불요. agent file 실 신설 = Phase 2 codeforge-develop sibling PR."
    ref: CFP-2401
    carrier_story: CFP-2401
    sunset_justification: null
    affected_agents:
      - ServiceDeveloperAgent (new entry, codeforge-develop presets/backend-service — Sonnet)
    cross_ref:
      - ADR-117 (surgical fable tier — generic Developer/DeveloperPL 이 fable(현 opus override)군. 신규 ServiceDeveloperAgent 는 surgical set 밖 명시 sonnet — disjoint, ADR-117 영역 무손상)
      - ADR-037 (plugin version bump rule — 신규 preset agent 추가 = codeforge-develop MINOR bump trigger 0.10.4→0.11.0)
      - ADR-063 (marketplace atomic version sync — codeforge-develop mirrored field version 변경)
      - ADR-005 (`ADR-005-plugin-self-application-na-standardization` — plugin self-application N/A 표준; §8 Test Contract declarative-only(plugin-meta-na) 분류 근거)
  - amendment_id: 16
    date: "2026-06-27"
    status: applied
    summary: "CFP-2432 — Story-shape 조건부 model tier (stakes-gated static-per-context tier). low-stakes Story shape(실자금 없음 ∧ production cutover 없음 ∧ 신규 신뢰경계 없음 ∧ live 외부 API 호출 없음 — 4-AND) 에서 InfraOperationalArchitectAgent 를 opus→sonnet spawn-time override, high-stakes shape 는 opus 유지. §결정 2 invariant 충돌 해소 = stakes 를 mandate-orthogonal 축으로 codify (tier = f(mandate depth, stakes)). opus 기준 (c)high-stakes domain / (d)safety boundary / (e)real-funds 는 stakes-conditional 근거 — Story 가 그 stakes 를 carry 할 때만 발화. 선례 = LiveOps/LiveOrdering CONDITIONAL spawn 동형 논리(deputy 의 opus depth 가 stakes 있을 때만 필요)를 permanent agent tier 선택으로 일반화. §결정 1(d) 비대칭 — safety boundary owner 4종 중 InfraOpArch 만 1급 flip 후보: §7.4.1 DR / §7.4.2 cancel-on-disconnect / §7.4.3 clock sync / §7.4.4 rate limit mandate 발현 trigger(외부 stream/endpoint/time-window 프로토콜/외부 API weight)가 live 연결 부재 shape 에서 물리적 dormant(InfraOpArch self-assessment verify). §7.4.5 env isolation / §7.4.6 container 는 잔존(secret hygiene / Docker-first 표준 설정 = sonnet single-mandate advocacy 깊이로 cover) → shape별 mandate 표면 재정의 동반 의무(순수 model 치환 = §결정 2 위반). SecurityArch=ADR-117 surgical set + 보안경계 low-stakes 상존 제외; DataArch(데이터 무결성 상존)·TestContractArch(§8 perf baseline 상존)=본 Story scope 외(별도 판정). DomainAgent=v1 제외(financial-correctness invariant 가 백테스트에도 상존 — lookahead/survivorship/fee — flip 시 sonnet 으로 새는 risk, F3 catalog) → follow-up CFP. 4번째 AND 조건 'live 외부 API 호출 없음(read-only 시세 포함)' = InfraOpArch G3 false-negative 가드(데이터 수집이 live API 호출 시 §7.4.4 재발현, RequirementsReview F4 live API read-only 경계 동시 해소). 메커니즘 신설 0 — frontmatter model:opus 보수 default(override 누락=opus fail-safe) + Orchestrator low-stakes shape 에서만 opts.model:sonnet fresh spawn(SendMessage resume 금지, ADR-057 §결정 4 선례). consumer overlay = 보수 방향(opus 강제)만, down-tier(opus→sonnet) 공격적 override 불가 — schema-gate + spawn-time clamp(max(wrapper_floor, overlay)) 2중 enforcement(ADR-127 §결정 6 확장-only 정합, SecurityArch consult). F1(P1) evidence-gate: tier-flip = provisional, sonnet 산출물 품질 ≥ opus baseline 측정 protocol(Codex 독립 review baseline 선례 = ADR-057 §결정 3 / ADR-042 Amd4 — F1 의 'ADR-057 Amd4' 는 mislabel, Amd4 = 버전핀→별칭) + 미달 시 opus 복원 trigger(누락≥1 OR P0/P1 finding OR tolerance 미달). D4 부수 정정 = ChangeImpactAgent model:sonnet 비준(파일 이미 sonnet, 정책 opus 와 drift) — ADR-042 Amd5 / ADR-057 §결정 3 의 opus 확정(사용자 verbatim 'changeimpact는 내가 보기에 opus가 괜찮아보인다')을 2026-06-27 사용자 directive('sonnet 범위 확장')로 명시 reversal(silent 금지). tier-flip(opus→sonnet)=ratchet 약화 방향 → sunset_justification(evidence) 의무(ADR-058 §결정 5 / ADR-064 §결정 7 is_transitional:false governance 약화 evidence-gate). 본 Phase 1 = ADR-042 Amd16 + change-plan + Story §7; Phase 2 = InfraOperationalArchitectAgent.md frontmatter 주석 + project.yaml story_stakes schema + gating 배선 + ChangeImpactAgent.md 정합 + plugin bump + marketplace sync."
    ref: CFP-2432
    carrier_story: CFP-2432
    sunset_justification: "opus→sonnet tier-flip = ratchet 약화 방향(reasoning depth 하향) → ADR-058 §결정 5 / ADR-064 §결정 7 (is_transitional:false governance ADR 의 약화 방향 symmetric evidence-gate) 에 따라 evidence requirement 발화. evidence-grounded justification 3 axis — (a) **stakes-gated 정제이지 flat 능력 감소 아님**: high-stakes shape(실자금/cutover/신규 신뢰경계/live API) 에서 opus 보존(§1 verbatim '무차별 opus→sonnet 강등 불가'), 하향은 stakes 4-AND 모두 미발현 shape 에 한정. InfraOpArch self-assessment 가 그 shape 에서 §7.4.1/.2/.3/.4 safety mandate 의 발현 trigger(외부 stream/endpoint/time-window/API weight)가 물리적으로 부재함을 mandate 권위로 verify — opus-급 깊은 추론을 요구하는 부분이 발현 안 되는 shape 이라 sonnet 이 잔존 mandate(§7.4.5 secret hygiene / §7.4.6 Docker-first 표준)를 fully cover(§결정 2 invariant 정합). (b) **falsifiable evidence-gate 동반**: tier-flip 은 provisional — sonnet 산출물 품질 ≥ opus baseline 측정 protocol(Codex 독립 review baseline, ADR-057 §결정 3 / ADR-042 Amd4 선례 재사용) + 미달 임계(§7.4 sub 또는 G2 invariant 누락 ≥ 1 OR Codex P0/P1 finding OR tolerance 미달) 1+ 해당 시 opus 복원(AC-9). 약화가 무근거 비용절감이 아니라 측정·복원 loop 으로 가드됨. (c) **지배적 low-stakes shape 의 비용효율 + 환경 변화 evidence**: CFP-2401 'sonnet 미사용' 진단(비-webapp 활발 개발 중 sonnet footprint 부재) follow-through — 백테스트/데이터 파이프라인/웹 UI/인터페이스 lib 등 low-stakes shape 가 지배적인 consumer(예: mctrader) 에서 InfraOpArch 가 매 설계 lane spawn 마다 opus 비용을 발생시키나 그 shape 에선 safety mandate 4축이 dormant. high-stakes 보존 + evidence-gate + 지배 shape 비용효율 = 약화 방향의 1급 정당화. is_transitional: false 유지(영구 정책 — stakes-conditional tier 는 영구 정책 정제이지 transitional pilot 아님)."
    affected_agents:
      - InfraOperationalArchitectAgent (codeforge-design — frontmatter model:opus 유지 fail-safe default + low-stakes 4-AND shape Orchestrator spawn-time opts.model:sonnet override. agent file frontmatter conditional 주석 = Phase 2 codeforge-design sibling PR)
      - ChangeImpactAgent (codeforge-requirements — D4 부수 정정: model:sonnet 비준, ADR-042 Amd5 / ADR-057 §결정 3 opus 확정의 명시 reversal. 파일 이미 model:sonnet → 정책 정합. mandate 변경 0)
      - DomainAgent (codeforge-requirements — v1 제외 명시: financial-correctness invariant 상존으로 tier-flip 정당성 약함, follow-up CFP. 본 Amendment tier 변경 0)
    cross_ref:
      - ADR-058 §결정 5 (약화 방향 sunset_justification evidence requirement — tier-flip 하향 evidence-gate 발화)
      - ADR-064 §결정 7 (is_transitional:false governance ADR 약화 방향 symmetric evidence-gate — ADR-042 is_transitional:false 에 §결정 5 적용 근거)
      - ADR-117 (surgical fable tier — SecurityArch=surgical set / generic Developer=fable override. 대상 InfraOpArch/Domain 은 surgical 10 밖 → disjoint, ADR-117 영역 무손상. silent override 금지 cross-ref)
      - ADR-057 §결정 3 / §결정 4 (Codex 독립 review baseline 선례(§결정 3 — 6 agent Sonnet vs Opus 적부 판정) + spawn-time opts.model override fresh-spawn 메커니즘 SSOT(§결정 4 fallback re-spawn))
      - ADR-127 §결정 6 (consumer overlay 확장-only — down-tier 공격적 override 불가 근거)
      - ADR-042 Amendment 5 / Amendment 15 (Amd5 = ChangeImpactAgent opus 확정 source(본 Amd16 이 reversal) + invariant enforcement 선례(mandate text 재정의) / Amd15 = CFP-2401 'sonnet 미사용' 진단 1차, 본 Story 2차 follow-through)
      - ADR-086 (axis 분석 lens — stakes axis ⊥ mandate axis disjoint 검증 도구 adjacent-case. 본 Amendment = 신설 아님(tier 분기)이라 framework 전면 self-application 주장 아님)
  - amendment_id: 17
    date: "2026-06-28"
    status: applied
    summary: "CFP-2445 (CFP-2432 follow-up) — DomainAgent financial-invariant-0 조건부 sonnet tier. Amendment 16 이 'DomainAgent v1 제외 + follow-up CFP'(§결정 3) 로 예약한 자리를 선결충족 후 채움(reversal 아님 — 예약된 확장). financial-invariant-0 = stakes 4-AND(InfraOpArch 축)와 **orthogonal 한 financial-correctness 결과접촉 축**. DomainAgent sonnet flip 조건 = (4-AND low-stakes) AND (financial-invariant-0 shape) 2-predicate AND — financial-invariant-0 은 4-AND 에 5번째로 욱여넣지 않고 **DomainAgent 전용 별 predicate**(STAKES_FINANCIAL_INVARIANT_ZERO)로 명시 분리(check-stakes-tier-gating.sh 확장, 신설 0). 판정 축 = 'DomainAgent 가 그 Story 에서 financial-correctness 결과 숫자(equity/PnL/position/체결가/universe/파라미터)를 생성·변형·해석하는가' — NO(결과 비접촉)이면 invariant-0. falsifiable 신호 = §2.3 5-AND(결과숫자 비접촉 ∧ 시간인과 비접촉 ∧ 체결/비용모델 비접촉 ∧ data lineage 비접촉 ∧ 변경경로 도메인숫자 repo 밖) — 전부 fail-safe(불확실=opus, INV-1 동형). **D1 catalog**: 백테스트 financial-correctness invariant 11건(INV-1~11: lookahead/survivorship/fee·slippage/PnL·position/PIT/overfitting/order-fill/capacity/시간경계/storytelling/outliers — 요구사항 §2.2 9건 초안 + F2 storytelling(INV-10)·outliers(INV-11) 편입) docs/domain-knowledge/domain/backtesting-discipline/ 정식화(F1 survivorship 1.4%/년 정정 — Oxford Academic rfs 9:4:1097 다출처 수렴, F2 storytelling/outliers 편입(INV-10/11) + '의도적 제외' traceability(7 Sins 1:1 매핑), F3 invariant **A(정적 falsifiable: lookahead 코드패턴/fee 누락/PnL 산술) / B(프로세스·메타데이터 의존: PIT governance/시행횟수/survivorship 완전성)** 분리). 정식 catalog 파일 = Phase 2 산출(DomainAgent write), 설계 = 구조·분류·shape 매핑 확정. **§결정 2 invariant 동반 의무**: DomainAgent.md mandate 에 'financial-invariant-0 shape 에서 DomainAgent 책임 표면 축소'(도메인 invariant 해석 부재 → 얕은 single-axis advocacy) 명시 — 순수 model downgrade 금지(CodebaseMapper/Refactor ADR-057 Amd5 / InfraOpArch Amd16 mandate-재정의 선례 답습). **메커니즘 신설 0**: frontmatter model:opus = fail-safe default(override 누락 = opus) + Orchestrator spawn-time opts.model:sonnet fresh override(ADR-057 §결정 4, SendMessage resume 금지). **spawn 시점**: DomainAgent 는 요구사항 lane spawn(InfraOpArch self-assessment 패턴 부적합 — 해석 mandate 가 shape 무관 상존) → **spawn-전 외부 shape 판정**(Story 메타·경로 allow-list, OQ-3). **F1 evidence-gate**: CFP-2432 stakes-gated-model-tier-baseline.md protocol DomainAgent 확장 — baseline 측정 대상 = '도메인 invariant 식별 완결성'(catalog cross-ref 깊이 + 식별 항목 수) 신규 정의(InfraOpArch §7.4 표 완결성과 다름, OQ-6). **ADR-117 §결정 2 cross-ref**(OQ-8): DomainAgent sonnet(하향) ⊥ ADR-117 'Domain 단기 구조적 fable 제외'(상향) = 판정축 disjoint, silent override 금지 — Amd16 §결정 3 의 cross-ref 의무 실행, ADR-117 본체 미수정(Amd17 내 언급으로 충족). ratchet 약화 방향(opus→sonnet) → sunset_justification(evidence) 의무. 본 Phase 1 = ADR-042 Amd17 + change-plan + Story §7; Phase 2 = catalog 파일 신규 + DomainAgent.md frontmatter+mandate + check-stakes-tier-gating.sh predicate 확장 + project-config-schema + playbook §3.0.12a + F1 protocol 확장 + plugin bump + marketplace sync."
    ref: CFP-2445
    carrier_story: CFP-2445
    sunset_justification: "opus→sonnet tier-flip(DomainAgent, financial-invariant-0 shape 한정) = ratchet 약화 방향(reasoning depth 하향) → ADR-058 §결정 5 / ADR-064 §결정 7 (is_transitional:false governance ADR 약화 방향 symmetric evidence-gate) evidence requirement 발화. evidence-grounded justification 3 axis — (a) **shape-gated 정제이지 flat 능력 감소 아님**: DomainAgent 의 financial invariant 해석 mandate 는 InfraOpArch safety mandate 와 달리 shape 무관 *상존*(백테스트도 financial-correctness invariant 보유 — Amd16 §결정 3 verbatim). 따라서 하향은 **financial-correctness 결과 숫자 비접촉 shape(순수 tooling/UI/infra lib/문서)에 엄격 한정** — 그 shape 에선 invariant 표면이 0(결과 정확성의 속성이 결과 비접촉 작업엔 표면 없음, §2.3 판정 원리). 데이터 파이프라인·백테스트 엔진·전략/지표 등 결과접촉 shape 는 opus 보존(financial-invariant-0 predicate false). InfraOpArch 의 '발현 trigger 물리 부재' 와 동형이되 dormant 가 아닌 '결과 비접촉으로 mandate 표면 0' 논리. (b) **falsifiable evidence-gate + indirect real-funds risk 가드**: tier-flip 은 provisional — F1 protocol(stakes-gated-model-tier-baseline.md) DomainAgent 확장으로 sonnet 산출물의 도메인 invariant 식별 완결성 ≥ opus baseline 측정 + 미달(catalog cross-ref 누락 ≥ 1 OR Codex P0/P1 OR tolerance 미달) 시 opus 복원(AC-9). 누설 = indirect real-funds risk(백테스트 결과 거짓→실자금 결정 오염, Amd16 §결정 3)이므로 fail-safe(불확실=opus) + 5-AND 전부 충족 요구 + evidence-gate 3중 가드. self-referential 판정 risk(도메인 비접촉 판정에 도메인 지식 필요)는 allow-list(순수 tooling 만 sonnet 허용) + fail-safe 로 완화, 잔존은 evidence-gate 흡수(완전 제거 아님 — OQ-2). (c) **지배적 financial-invariant-0 shape 의 비용효율**: CFP-2401 'sonnet 미사용' 진단의 follow-through 연장 — DomainAgent 가 매 요구사항 lane spawn 마다 opus 비용을 발생시키나 financial-correctness 결과 비접촉 Story(순수 UI/infra/tooling/문서)에선 financial invariant 해석 표면이 0. high-stakes/결과접촉 보존 + evidence-gate + 결과 비접촉 shape 비용효율 = 약화 방향의 1급 정당화. is_transitional: false 유지(영구 정책 정제, transitional pilot 아님 — Amd16 동형)."
    affected_agents:
      - DomainAgent (codeforge-requirements — frontmatter model:opus 유지 fail-safe default + financial-invariant-0 shape(4-AND low-stakes ∧ financial-correctness 결과 비접촉) Orchestrator spawn-time opts.model:sonnet override. agent file frontmatter conditional 주석 + mandate 표면 재정의(financial-invariant-0 shape 책임 축소 declare) = Phase 2 codeforge-requirements sibling PR. Amd16 의 'v1 제외' → CFP-2445 완료로 갱신)
    cross_ref:
      - ADR-042 Amendment 16 (CFP-2432 — §결정 3 가 'DomainAgent flip = catalog codify + 경계 falsifiable 확정 후 별 carrier' 로 본 Story 예약. Amd17 = 선결충족 확장(reversal 아님, Amd16 무효화 0). 메커니즘(opts.model override / 4-AND / F1 protocol / consumer overlay 확장-only) 전부 재사용 — 신설 0)
      - ADR-058 §결정 5 (약화 방향 sunset_justification evidence requirement — DomainAgent tier-flip 하향 evidence-gate 발화)
      - ADR-064 §결정 7 (is_transitional:false governance ADR 약화 방향 symmetric evidence-gate)
      - ADR-117 §결정 2 (Domain '단기 구조적' fable 상향 제외 = 상향 축. 본 Amendment = 하향(sonnet) 축 disjoint — 직접 모순 아님. Amd16 §결정 3 cross-ref 의무 실행, ADR-117 본체 미수정(Amd17 내 언급 충족). silent override 금지)
      - ADR-057 §결정 3 / §결정 4 (Codex 독립 review baseline 선례(F1 measurement) + spawn-time opts.model override fresh-spawn 메커니즘 SSOT(SendMessage resume 금지 상속))
      - ADR-127 §결정 6 (consumer overlay 확장-only — DomainAgent down-tier 공격적 override 불가, max(floor,overlay) clamp 재사용)
      - ADR-056 §결정 3 (요구사항 lane synthesis 순서 §5→§2→§6→PL — catalog 합성 근거) / DomainAgent write 권한 경로 docs/domain-knowledge/domain/** (concept/** deny — catalog = domain/ 만 가능)
  - amendment_id: 18
    date: "2026-07-01"
    status: applied
    summary: "CFP-2539 (Epic CFP-2533 Story B) — RefactorAgent (d) Reusability *측정* 축을 구현 리팩터링(Story C)으로 소관 이동 + repo-분해 *구조* escalation 축은 RefactorAgent 존치 (Amendment 13/14 partial re-framing, carry-over — Amendment 10 CFP-1126 선례 답습). Amendment 13(CFP-2364)이 (d) Reusability 를 1급 축으로 신설 + Amendment 14(CFP-2369)가 측정 mechanical wire 한 것을, 본 Amendment 18 이 (d)를 **두 sub-part 로 분할**: (i) **중복제거·공통추출·DRY/WET·rule-of-three·duplication-ratio 측정** = 실코드 관측 의존(중복은 코드가 생겨야 관측 — Story §2.1 도메인 근거) → RefactorAgent 설계-lane mandate 에서 out-of-mandate + 구현 리팩터링(Story C, Epic-close Codex↔Claude execute-and-falsify triage) in-scope 로 re-frame. (ii) **repo-level 분해 advocacy**(응집 cluster → 별 deploy/ownership 단위 분리 = macro-structural boundary, 설계-시점 관측 가능) = RefactorAgent 설계-시점 구조 escalation 축으로 **존치**(advocacy/제안만, 경계 확정 = ArchitectAgent chief authority — RefactorAgent.md:33 기 anchor). 순 결과: RefactorAgent = (a)decoupling / (b)pattern / (c)interface separation **구조 3축** + **repo-level 분해 구조 escalation(설계-시점)**. REMOVED = 중복/재사용 *측정* 축(duplication-ratio / clone / rule-of-three / DRY-as-duplication / 공통추출) only. **Amendment 13/14 본문 = frozen audit trail, 0 touch** (event-sourcing — 과거 결정 박제, 무효화 아닌 소관 re-framing). Amendment 13 L50 '(d) in-scope' anchor → '측정 축 out-of-mandate + 구현 리팩터링 in-scope; repo-분해 구조 escalation 존치' 로 carry-over re-frame (Amendment 10 carry-over 답습 — 삭제 아님). **ADR-131 무영향 (Amendment 2 불요)** — ADR-131 L85/L144/L146-150/L230 의 참조 대상 = RefactorAgent 의 *repo-분해 advocacy* 이지 *reusability 측정* 축이 아니며, repo-분해 존치로 L150 '무축소' premise 는 TRUE 유지. Amendment 14 deferred(duplication-ratio blocking 승격 = evidence 누적 후 별 CFP) owner_adr = ADR-060/ADR-042 governed 유지, RefactorAgent-advocacy driver 만 Story C triage context 로 relocate(도구 5파일 존치, warning-tier orphan-safe). ADR-086 explicit scope = 신설/미도입/rename/**축소** (L56 verbatim) → 본 Amendment 18(측정 축 mandate 축소)은 explicit scope 열거 대상이므로 **full self-application** (Amendment 13 mandate 확장 = adjacent-case 였던 것과 대조 — 축소는 열거됨). 5-checklist FULL: #1 axis-disjoint(측정 축 relocation ⊥ 잔여 구조 3축 ⊥ repo-분해 escalation) / #2 cost-token(marginal — output 슬롯 4→3 감소, spawn count 무변경) / #3 consumer carrier(duplication 측정 owner → Story C triage, 도구 존치 warning-tier — 신규 schema key 0) / #4 sibling Epic align(CFP-2533 Story C 수령처 cross-ref) / #5 deferred trigger(Story C mechanical wire — role_assignment/blanket_refactor 실배선). ADR-091 L193 = frozen-⚠ 역주석만(rewrite 금지 — `⚠ CFP-2539` append, `⚠ CFP-2364` 패턴 답습). RefactorAgent 존속(roster 6+3+1+3 sub-tuple 무변경), model tier Sonnet 무변경 — mandate 발화 범위만 축소. SSOT propagation 3원본(RefactorAgent.md + skills/deputy-mandate/SKILL.md + plugins/codeforge-design/CLAUDE.md) sync. bump codeforge-design 0.30.0 → 0.31.0 MINOR(agent surface 축소 — ADR-037). marketplace version sync(ADR-063). **ratchet 약화 방향(측정 축 RefactorAgent 국소 4→3 축소) → sunset_justification(evidence) 의무**(ADR-058 §결정 5 / ADR-064 §결정 7). Phase 1 = 본 Amendment 18 + change-plan + Story mirror; Phase 2 = 14-surface 3축 정합 sweep + plugin bump + marketplace sync."
    ref: CFP-2539
    carrier_story: CFP-2539
    sunset_justification: "RefactorAgent (d) Reusability *측정* 축 소관 이동(설계-lane inline advocacy → 구현 리팩터링 Story C triage) = RefactorAgent 국소로 보면 4축→3축 mandate 축소(약화 방향) → ADR-058 §결정 5 / ADR-064 §결정 7 (is_transitional:false governance ADR 약화 방향 symmetric evidence-gate) evidence requirement 발화. Amendment 10(CFP-1126) partial-rollback+carry-over 선례 답습. evidence-grounded justification 3 axis — (a) **환경 변화 evidence (relocation-강화, flat 능력 감소 아님)**: 측정 축을 강제력 없는 설계-시점 warning 에서 실코드 관측 시점(구현-후)의 execute-and-falsify 로 이동. 그 이동을 net-strengthening 으로 만드는 환경 변화 = CFP-2476 (Epic Codex 실행기반 검증 확장 — 실행형 재리뷰 + 주장→증거 감사 + 정책게이트+FIX replay, CLOSED `[verified: gh issue view 2476 state=CLOSED]`) infrastructure 가 이제 EXISTS. 중복/재사용 측정은 실코드 위에서 Codex 가 실측·반증(execute-and-falsify) 가능한 시점(Epic-close triage)에 배치될 때 강제력이 설계-시점 declarative advocacy 보다 net ↑. Story A(debate-protocol-v1 v1.3, `blanket_refactor` dispatch, merged)가 enabling contract. (b) **eval/directive evidence (강제력 비대칭 + 도메인 관측 한계)**: Epic CFP-2533 problem statement = '설계 시점 advocacy 로는 중복/재사용 관측 한계 (코드가 생겨야 진짜가 보이고 Codex 가 실측 가능)' + 강제력 비대칭 실측 — Amendment 14 check-duplication-ratio.sh 는 always exit 0 (warning-tier, 비차단) 인 반면 impl-manifest-mismatch 등은 P1 blocking. 설계-시점 측정 축이 warning-tier 로 강제력 결여인 채 남아 있는 것보다 구현-후 execute-and-falsify triage 로 이동이 강제력 net 개선. pattern_count 는 별도 catalog 부재 — eval/directive evidence 로 정직 framing(날조 금지). (c) **observation-time sufficiency (측정 축의 올바른 관측 시점 배치 = single-axis 충분 analog)**: 측정 축은 '중복은 실코드 없이 선험적으로 존재 불가'(Story §2.1 도메인 근거)라 설계-시점 falsifiable 계측이 물리 불가 — 올바른 관측 시점(구현-후)으로 배치될 때만 falsifiable. repo-분해 축은 macro-boundary 로 설계 스케치에서 관측 가능 → RefactorAgent 설계-시점 존치가 정합(관측 시점 disjoint). 따라서 국소 4→3(측정 축) 축소 ↔ policy-level elevation(설계-시점 warning → 구현-후 execute-and-falsify) trade-off 의 net 은 강화(Story §4.2 relocation-강화 framing). high-value 구조 3축 + repo-분해 구조 escalation 보존 + 측정 축의 올바른 관측 시점 배치 = 약화 방향의 1급 정당화. is_transitional: false 유지(영구 정책 정제 — 소관 이동은 영구 재배치, transitional pilot 아님. Amendment 10 동형)."
    affected_agents:
      - RefactorAgent (codeforge-design — mandate 축소: (d)reusability *측정* 축(중복제거·공통추출·DRY/WET·rule-of-three·duplication-ratio) out-of-mandate → 구현 리팩터링 Story C 이관 anchor; (a)decoupling / (b)pattern / (c)interface separation 구조 3축 유지; repo-level 분해 구조 escalation(설계-시점 advocacy) 존치. model tier Sonnet 무변경, roster 무변경. agent file 14-surface 3축 정합 sweep = Phase 2 codeforge-design sibling PR)
    cross_ref:
      - ADR-042 Amendment 13 (CFP-2364 — (d) Reusability 1급 축 신설. 본 Amendment 18 = 그 (d)를 측정 축(→Story C) + repo-분해 구조 escalation(존치)로 분할 re-frame. 본문 0 touch, L50 anchor re-framing only. 무효화 아님)
      - ADR-042 Amendment 14 (CFP-2369 — (d) 측정 mechanical wire. 도구 5파일 존치(warning-tier, orphan-safe), advocacy driver 만 Story C triage context 로 relocate. deferred blocking-승격 trigger = ADR-060/ADR-042 governed 유지)
      - ADR-042 Amendment 10 (CFP-1126 — partial retroactive rollback + carry-over + sunset_justification first applied 선례. 본 Amendment 18 = 동형 구조(부분 재편 + carry-over re-framing + 약화 방향 evidence-gate) 답습)
      - ADR-058 §결정 5 (약화 방향 sunset_justification evidence requirement — RefactorAgent 측정 축 국소 4→3 축소 evidence-gate 발화)
      - ADR-064 §결정 7 (is_transitional:false governance ADR 약화 방향 symmetric evidence-gate)
      - ADR-086 (Deputy 신설 결정 framework — explicit scope L56 '신설/미도입/rename/축소' 에 축소 열거 → 본 Amendment 18 = FULL self-application (5-checklist 완주), Amendment 13 mandate 확장 adjacent-case 와 대조)
      - ADR-091 §결정 1 (RefactorAgent DDD pattern mapping 표 L193 — frozen 보존, `⚠ CFP-2539` 역주석 append only, rewrite 금지. `⚠ CFP-2364` 패턴 답습)
      - ADR-131 §결정 1/3 (cross-repo 책임 배치 — L85/L144/L146-150/L230 의 RefactorAgent 참조 = *repo-분해 advocacy* 대상. repo-분해 존치로 L150 '무축소' premise TRUE 유지 → **ADR-131 Amendment 2 불요**. 측정 축 relocation ⊥ repo-분해 topology-SSOT chief authority 무영향)
      - ADR-037 (plugin version bump rule — agent surface 축소 = codeforge-design MINOR bump trigger, 0.30.0 → 0.31.0)
      - ADR-063 (marketplace atomic version sync — codeforge-design mirrored field version 변경, sync PR 선행 merge)
      - CFP-2476 (Epic Codex 실행기반 검증 확장 — execute-and-falsify infrastructure EXISTS = 측정 축 relocation net-strengthening 환경 변화 evidence, sunset_justification (a) axis)
      - CFP-2533 Story A (debate-protocol-v1 v1.3 `blanket_refactor` dispatch — enabling contract) / Story C (측정 축 수령처 — Epic-close triage 실배선)
related_stories:
  - CFP-448
  - CFP-676
  - CFP-1086
  - CFP-1059  # Amendment 9 carrier — 4 신설 agent tier (DeployPL/DeployWorker/DeployReviewPL/DeployReviewWorker)
  - CFP-1126  # Amendment 10 carrier — AggregateArch + ModuleArch 통합 (Amendment 8 partial retroactive rollback, ratchet 축소 첫 carrier, ADR-058 §결정 5 first applied)
  - CFP-1155  # Amendment 11 carrier — UpgradeAgent walker model tier (declarative Sonnet → imperative walk Opus, ADR-098 §결정 2 carry, CFP-1111 Wave 2 Story-4)
  - CFP-1845  # Amendment 12 carrier — model 버전 핀 → 별칭(opus/sonnet/haiku) 전환 (항상 최신 tier 지칭, ADR-057 Amendment 4 sibling atomic)
  - CFP-2364  # Amendment 13 carrier — RefactorAgent Reusability 1급 축 신설 (3 카테고리 → 4 카테고리, ISO/IEC 25010 Maintainability gap, axis disjoint advocacy ↔ ModuleArch authority, ADR-086 axis 분석 lens adjacent-case 적용)
  - CFP-2369  # Amendment 14 carrier — (d) Reusability 측정 연동 Phase-2 mechanical wire (warning-tier duplication-ratio 측정: check-duplication-ratio.sh + consumer template + evidence-registry entry, CFP-2364 deferred trigger follow-through, repo-분해 advisory 유지)
  - CFP-2401  # Amendment 15 carrier — 비-webapp(backend service) sonnet dev preset 신설 (ServiceDeveloperAgent, §결정 1(b) enumeration 확장, preset 2→3)
  - CFP-2432  # Amendment 16 carrier — Story-shape 조건부 model tier (stakes-gated static-per-context tier). low-stakes 4-AND shape 에서 InfraOperationalArchitectAgent opus→sonnet, high-stakes opus 유지. §결정 2 invariant 충돌 해소(stakes = mandate-orthogonal 축). ChangeImpactAgent sonnet 비준(Amd5 reversal) + DomainAgent v1 제외. ratchet 약화 방향 → sunset_justification(evidence) 의무
  - CFP-2445  # Amendment 17 carrier — DomainAgent financial-invariant-0 조건부 sonnet (CFP-2432 follow-up). Amd16 §결정 3 가 예약한 DomainAgent flip 자리 선결충족(catalog codify + 경계 falsifiable 확정). financial-invariant-0 = stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축, DomainAgent 전용 별 predicate. flip 조건 = (4-AND low-stakes) AND (financial-invariant-0 shape). D1 catalog 11 invariant(INV-1~11, F2 storytelling/outliers 편입 INV-10/11) + A/B 분류 + F1 1.4% 정정. mandate 표면 재정의 동반(§결정 2). ratchet 약화 방향 → sunset_justification(evidence) 의무
  - CFP-2539  # Amendment 18 carrier — RefactorAgent (d) Reusability *측정* 축(중복제거·공통추출·DRY/rule-of-three/duplication-ratio) 구현 리팩터링(Story C) 소관 이동 + repo-분해 구조 escalation(설계-시점) 존치. Amendment 13/14 partial re-framing(carry-over, 본문 0 touch — Amd10 선례). RefactorAgent 국소 4축→3축(측정 축) 축소 = 약화 방향 → sunset_justification(evidence 3 axis: CFP-2476 execute-and-falsify infra EXISTS 환경 변화 / Epic CFP-2533 강제력 비대칭 eval / 측정 축 observation-time 배치 sufficiency) 의무. ADR-131 L150 '무축소' premise TRUE 유지(repo-분해 존치) → ADR-131 Amendment 2 불요. ADR-086 explicit scope 축소 열거 → FULL self-application. Epic CFP-2533 Story B
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
  - ADR-098  # Amendment 11 cross-ref (CFP-1155 / Wave 2 Story-4 — UpgradeAgent runtime ownership + model tier 재평가 의무 declare, 본 Amendment 11 이 실 tier 확정 carry)
  - ADR-097  # Amendment 11 cross-ref (CFP-1155 — paradigm replacement governance anchor, declarative → imperative role 재정의 trigger)
  - ADR-076  # Amendment 11 cross-ref (CFP-1155 — declarative UpgradeAgent runtime SSOT, model:sonnet → Opus 상향 source paradigm)
  - ADR-063  # Amendment 15 cross-ref (CFP-2401 — marketplace atomic version sync, codeforge-develop mirrored field version 변경; Amendment 13/14 에서도 cross_ref 였으나 related_adrs 미등재 → 정합 등재)
  - ADR-117  # Amendment 15 cross-ref (CFP-2401 — surgical fable tier. generic Developer/DeveloperPL = fable(현 opus override)군, 신규 ServiceDeveloperAgent = surgical set 밖 명시 sonnet → disjoint, ADR-117 영역 무손상)
  - ADR-005  # Amendment 15 cross-ref (CFP-2401 — plugin-meta-na, §8 Test Contract declarative-only 분류 근거)
  - ADR-058  # Amendment 16 cross-ref (CFP-2432 — §결정 5 약화 방향 sunset_justification evidence requirement; tier-flip opus→sonnet 하향 evidence-gate)
  - ADR-064  # Amendment 16 cross-ref (CFP-2432 — §결정 7 is_transitional:false governance ADR 약화 symmetric evidence-gate)
  - ADR-127  # Amendment 16 cross-ref (CFP-2432 — §결정 6 consumer overlay 확장-only; down-tier 공격적 override 불가 근거)
  - ADR-056  # Amendment 17 cross-ref (CFP-2445 — 요구사항 lane synthesis 순서 §5→§2→§6→PL catalog 합성 근거 + DomainAgent write 권한 경로 docs/domain-knowledge/domain/** (concept/** deny))
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
| **Opus** | opus | (a) Multi-source synthesis (3+ SubAgent / lane / contract input dedup + 종합 판정) — 모든 PL · ArchitectAgent chief. (b) Independent reasoning peer to external GPT-5 (ClaudeReviewAgent — Codex 와의 의도적 reasoning depth 매칭). (c) High-stakes domain interpretation (DomainAgent — Live trading / 금융 / 헬스 데이터 등 invariant 누설 위험). (d) Security / safety boundary owner (SecurityArchitectAgent · OperationalRiskArchitectAgent · DataMigrationArchitectAgent · TestContractArchitectAgent — §7 trust boundary / §7.4 DR / §11 schema rollback / §8 perf baseline). (e) Real-funds risk owner (LiveOpsDeputyAgent · LiveOrderingDeputyAgent — CFP-77 CONDITIONAL). (f) Cross-Story pattern analysis + ADR proposal (PMOAgent). (g) Deep research with reshape mandate (ResearcherAgent — per [ADR-046](ADR-046-researcher-role-redefinition.md) (2026-05-09)). |
| **Sonnet** | sonnet | (a) Single-mandate advocacy within multi-deputy debate — read-only 조사 + 자기 mandate 측 단일 축 주장 (CodebaseMapperAgent — existing facts only, RefactorAgent — pattern advocacy only). (b) Implementation work — code write / refactor / test 구현 (DeveloperAgent · DeveloperPLAgent · 2 webapp preset). |

> **Amendment 4 (2026-05-11)**: CodebaseMapperAgent·RefactorAgent는 Opus로 복원됨 — ADR-057 참조.
>
> **Amendment 5 (2026-05-12, CFP-448)**: Amendment 4 의 6 agent 상향 중 3종 (CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent) Opus → Sonnet 복귀. 나머지 3종 (FeasibilityAgent · ContinuityAgent · ChangeImpactAgent) Opus 유지. ADR-057 Amendment 3 cross-ref.
>
> **Amendment 13 (2026-06-19, CFP-2364)**: Sonnet (a) single-mandate advocate **RefactorAgent** 의 mandate scope 확장 — decoupling / pattern / interface 분리 3 카테고리 → + **(d) Reusability (재사용성)** 4 카테고리 (ISO/IEC 25010 Maintainability gap 충당, 신설 아님 — 기존 sub-tuple agent mandate 확장). model tier Sonnet 무변경 (single-mandate advocacy 패턴 유지 — reusability pressure 식별·제안 단일 축, multi-source synthesis 는 ArchitectAgent chief Opus). axis disjoint = RefactorAgent reusability advocacy ↔ ModuleArch boundary authority. 상세 = 본 ADR `## Amendment 13` body section.
>
> **Amendment 14 (2026-06-19, CFP-2369)**: Amendment 13 의 (d) Reusability **측정 연동** 을 Phase-1 declarative (신호 제공까지) 에서 **Phase-2 mechanical wire (warning-tier duplication-ratio 측정)** 로 실현. model tier / roster / 카테고리 4 무변경 — RefactorAgent.md 측정 연동 단락만 deferred → tool-grounded 정정. 도구 = `scripts/check-duplication-ratio.sh` (warning-tier, 항상 exit 0) + consumer template + evidence-registry entry `duplication-ratio-warning`. RefactorAgent 권한 확장 0 (도구 구동 주체 = CI). repo-분해 mechanical gate 는 advisory 유지 (out-of-scope). 상세 = 본 ADR `## Amendment 14` body section.
>
> **Amendment 15 (2026-06-25, CFP-2401)**: Sonnet (b) Implementation work enumeration 에 **ServiceDeveloperAgent** (codeforge-develop `presets/backend-service/`, frontend-less backend service shape sonnet dev) 추가 — webapp preset(web shape)에 이어 비-webapp shape 의 sonnet 구현 tier 신설. generic DeveloperAgent(ADR-117/CFP-2241 opus override) 와 disjoint(명시 sonnet). 상세 = 본 ADR `## Amendment 15` body section.
>
> **Amendment 16 (2026-06-27, CFP-2432)**: **Story-shape 조건부 model tier (stakes-gated static-per-context tier)** 도입 — tier = f(mandate depth, **stakes**) 로 codify. Opus 기준 (c)/(d)/(e) (high-stakes domain / safety boundary / real-funds) 는 **stakes-conditional** — Story 가 그 stakes 를 carry 할 때만 발화. **low-stakes Story shape (실자금 없음 ∧ production cutover 없음 ∧ 신규 신뢰경계 없음 ∧ live 외부 API 호출 없음 — 4-AND)** 에서 **InfraOperationalArchitectAgent** 를 spawn-time `opts.model: sonnet` override (frontmatter `model: opus` = fail-safe default 보존, override 누락 = opus). high-stakes shape = opus 유지. §결정 1(d) safety boundary owner 4종 중 InfraOpArch 만 1급 flip 후보(§7.4.1/.2/.3/.4 mandate 발현 trigger 가 live 부재 shape 에서 물리적 dormant — §7.4.5/.6 잔존분은 sonnet single-mandate advocacy 깊이로 cover). SecurityArch(ADR-117 surgical + 보안경계 상존)·DataArch·TestContractArch 제외; DomainAgent v1 제외(financial invariant 상존, follow-up). §결정 2 invariant 와 양립(stakes = mandate-orthogonal 축, shape별 mandate 표면 재정의 동반 의무). ratchet 약화 방향(opus→sonnet) → sunset_justification(evidence) 의무(ADR-058 §결정 5 / ADR-064 §결정 7). 상세 = 본 ADR `## Amendment 16` body section.
>
> **Amendment 17 (2026-06-28, CFP-2445)**: Amendment 16 이 v1 제외 + follow-up 으로 예약한 **DomainAgent** 를 **financial-invariant-0 shape 한정 조건부 sonnet** 으로 채움(선결충족 확장, reversal 아님). DomainAgent sonnet flip 조건 = **(4-AND low-stakes) AND (financial-invariant-0 shape)** — financial-invariant-0 은 Amendment 16 의 stakes 4-AND(InfraOpArch 축)와 **orthogonal 한 financial-correctness 결과접촉 축**, 4-AND 에 5번째로 욱여넣지 않고 **DomainAgent 전용 별 predicate**(`STAKES_FINANCIAL_INVARIANT_ZERO`)로 분리(check-stakes-tier-gating.sh 확장, 신설 0). 판정 축 = "DomainAgent 가 그 Story 에서 financial-correctness 결과 숫자(equity/PnL/position/체결가/universe/파라미터)를 생성·변형·해석하는가" — NO(결과 비접촉)이면 invariant-0(§2.3 5-AND, fail-safe 불확실=opus). D1 catalog 11 invariant(INV-1~11 — 요구사항 §2.2 9건 + F2 storytelling(INV-10)·outliers(INV-11) 편입) docs/domain-knowledge/domain/backtesting-discipline/ 정식화 + invariant **A(정적 falsifiable) / B(프로세스·메타데이터 의존)** 분리(F3) + F1 survivorship 1.4%/년 정정. **§결정 2 invariant 동반 의무** — DomainAgent.md mandate 에 "financial-invariant-0 shape 에서 책임 표면 축소" 명시(순수 model downgrade 금지, InfraOpArch Amd16 mandate-재정의 선례). frontmatter `model: opus` = fail-safe default + Orchestrator spawn-time `opts.model: sonnet` fresh override(메커니즘 신설 0). DomainAgent = 요구사항 lane spawn → **spawn-전 외부 shape 판정**(Story 메타·경로 allow-list — InfraOpArch self-assessment 패턴 부적합, 해석 mandate shape 무관 상존). F1 evidence-gate DomainAgent 확장(baseline = 도메인 invariant 식별 완결성). ADR-117 §결정 2 cross-ref(하향 sonnet ⊥ 상향 fable disjoint, silent override 금지 — Amd16 §결정 3 의무 실행, ADR-117 본체 미수정). ratchet 약화 방향 → sunset_justification(evidence) 의무. 상세 = 본 ADR `## Amendment 17` body section.
>
> **Amendment 7 (2026-05-19, CFP-676)**: Sonnet (a) "Single-mandate advocacy within multi-deputy debate" 에 **CodeArchitectAgent** (§3 code 설계 단일 축 advocacy — layered/hexagonal/clean/DDD bounded context/module boundary/dependency direction) + **ArchitectAnalystAgent** (변경 전 기존 설계 분석 단일 축 — PriorArtAgent rename, 4-tuple sub-tuple component) 2종 추가. CodebaseMapper/Refactor 동질 패턴 (single-mandate advocate, multi-source synthesis = ArchitectAgent chief Opus). §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 충족 — 처음부터 single-mandate 정의이므로 Sonnet 적정. DataMigrationArchitectAgent → **DataArchitectAgent** rename + mandate 확장 / OperationalRiskArchitectAgent → **InfraOperationalArchitectAgent** rename — 본 § 의 Sonnet criteria 무관 (Opus tier 유지, §결정 1 (d) Security/safety boundary owner / 결정 4 inheritance). 상세 = 본 ADR `## Amendment 7` 본문 section. **CodebaseMapper / Refactor 의 mandate text 재정의 동시 산출물 의무 발화로 §결정 2 invariant 정합 — 단순 model field downgrade 금지. DeveloperPLAgent 는 사용자 framing (CFP-448) verbatim ('아키텍트가 짜준 디자인 명세에서 제한되게 움직여 고도의 추론이 필요하지 않기 때문이다') 직접 적용 + ADR-042 §결정 1 (b) "Implementation work — code write / refactor / test 구현" verbatim 정의 정합 회귀 → mandate text 재정의 면제 + Codex re-review 면제**. 자세한 결정 matrix 는 본 ADR Amendment 5 본문 + ADR-057 Amendment 3 §결정 3 표 참조.
| **Haiku** | haiku | (a) Test runner / 결과 수집 — minimal reasoning (TestAgent). (b) External tool wrapper — 본체 reasoning 은 external (Codex GPT-5 / GPT-5.4) 가 수행, Claude 는 prompt 조립 / output relay 만 (CodexReviewAgent · RequirementsAnalystAgent). (c) Mechanical pattern execution — 입력 명세(Change Plan §3 + Story §8)가 충분히 structured되어 creative/diagnostic reasoning 없이 패턴 기반 생성이 가능하고, 오류 발생 시 FIX 루프가 CI/테스트로 즉시 감지 가능한 경우 (InfraEngineerAgent · QADeveloperAgent · DataEngineerAgent — Amendment 2). |

> **Amendment 11 (2026-05-21, CFP-1155)**: Opus (a) "Multi-source synthesis" 에 **UpgradeAgent** (codeforge-pmo, imperative walk runtime) 추가 — declarative `model: sonnet` (CFP-743, 9-domain single-source diff) → imperative walk **Opus** 상향. plan stage = 7-plugin CHANGELOG.md 다중 source dedup + min_prerequisite_version topological resolve (DAG) + importance_score 종합 = multi-source synthesis 깊이 (§결정 2 invariant Sonnet fully-cover 불가). ADR-098 §결정 2 model tier 재평가 의무 carry. 상세 = 본 ADR `## Amendment 11` body section.
>
> **Amendment 6 (2026-05-16, CFP-777)**: DialogFidelityAgent 신규 entry 추가 (codeforge-pmo / Opus pilot tier). verifier mandate = 누적 대화 fidelity 검증, 의미적 모순 판정 영역. mandate depth = 다축 (semantic match + ledger consistency + 4 차원 enum closed + Story §1 immutable cross-ref + Layer 4 incidents row inspection). single-axis 외형은 single-axis 검수이나 contradiction detection 은 deep reasoning 영역 — **Opus pilot 시작 → N=20 baseline 후 §결정 2 invariant 적용 재판정** (별도 carrier). **Codex 평행 평가 의무** (CFP-379 / CFP-448 pattern) — TP#4 dispatch 시 본 Amendment 입력 verbatim 전달, Opus vs Sonnet baseline divergence detect. ADR-071 Amendment 1 (DialogFidelityAgent external verifier auxiliary layer) cross-ref.

| **Opus pilot** | opus | DialogFidelityAgent (codeforge-pmo) — verifier-narrower-than-generator 패턴: 누적 대화 fidelity 검증 (Story §1 immutable + Layer 4 incidents + 현 turn output), 의미적 모순 판정 (deep reasoning 영역). §결정 2 invariant 재판정 trigger = N=20 spawn baseline 후 (별도 carrier). |

> **Amendment 12 (2026-05-30, CFP-1845)**: 본 §결정 1 tier 표의 Model 컬럼을 버전 핀(claude-opus-4-7 / claude-sonnet-4-6 / claude-haiku-4-5)에서 **별칭(opus / sonnet / haiku)** 으로 전환. 별칭 = 플랫폼이 항상 최신 tier 버전으로 해석 — 버전 릴리스마다 전 파일 일괄 변경 chore 제거 + 자동 최신 추적. 현재 해석: opus→4.8 (실질 상향), sonnet→4.6, haiku→4.5 (현 최신 동일). **tier 분류 정책 강도 불변** (Opus/Sonnet/Haiku role pattern criteria 변경 0건, 버전 표기 방식만), ratchet 약화 아님 (ADR-058 §결정 5 정합). 사용자 directive (2026-05-30 KST) verbatim: "opus, sonnet, haiku 모두 최신 버전으로 지칭하도록 해". § "현재 agent inventory (2026-05-09)" 의 "Opus 4.7 / Sonnet 4.6 / Haiku 4.5" 표기 + amendment_log 과거 버전 언급은 frozen audit trail 로 보존 (그 시점 snapshot). ADR-057 §결정 1 (Orchestrator 버전 핀 → 별칭) Amendment 4 동시 개정 sibling (CFP-1845 atomic). 향후 신규 agent `model:` field default = 별칭. cross-repo 6 lane plugin agent file 별칭 전환 = follow-up PR.

### 결정 2: 본 ADR 발효 시점 변경 사항 (2 sibling PR scope)

**plugin-codeforge-design sibling PR** (별도 — 본 ADR PR merge 직후. 구 lane repo — 현 `plugins/codeforge-design/`, repo 삭제됨 2026-06-12):
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
- 본 ADR scope 외 lane plugin agent file (CodebaseMapperAgent · RefactorAgent model field edit) — sibling PR mclayer/plugin-codeforge-design#24

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
- plugin-codeforge-requirements#12 — ResearcherAgent role 재정의 follow-up
- **Sibling PR** (codeforge-design Mapper + Refactor model edit): mclayer/plugin-codeforge-design#24 — version 0.4.0 → 0.4.1 PATCH bump 동반

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

> **Amendment 16 reversal (2026-06-27, CFP-2432)**: 위 표의 **ChangeImpactAgent Opus 유지** 결정(Amendment 5 / ADR-057 §결정 3, 사용자 verbatim 'changeimpact는 내가 보기에 opus가 괜찮아보인다')은 **2026-06-27 사용자 directive ('sonnet 범위를 확장해야 되겠다') 로 명시 reversal** 되어 ChangeImpactAgent = **Sonnet** 으로 확정된다 (silent override 금지 — 본 reversal 명시 기록). 근거: ChangeImpactAgent 역할 = src/** 읽기전용 코드 변경 델타 매핑(AS-IS → DELTA, Story §4.1 owner) 단일 축 = §결정 1 Sonnet (a) single-mandate advocacy 정합, stakes 무관 unconditional sonnet. agent file `plugins/codeforge-requirements/agents/ChangeImpactAgent.md:3` 은 이미 `model: sonnet` (정책 drift 상태였음) → 본 reversal 로 정책↔파일 정합. D4 부수 정정 — 상세 = 본 ADR `## Amendment 16` body section §D4.
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

---

## Amendment 10 — AggregateArch + ModuleArch 통합 (Amendment 8 partial retroactive rollback, ADR-058 §결정 5 first applied carrier, CFP-1126, 2026-05-21 KST)

**날짜**: 2026-05-21

### 동기

CFP-1110 paired Amendment (ADR-082 Amendment 5 + ADR-071 Amendment 6 §결정 17, lane traversal fidelity mandate, 2026-05-20 merge) 의 카운터파트 carrier — 사용자 평가 결과 직접 follow-through. Researcher (general-purpose) + Codex (codex:rescue, GPT-5) 병렬 critical evaluation 수렴 결과:

- **Researcher net 35% 정당화** (verify-before-trust + Epic gate 영역만 net positive), 나머지 80% = self-burdening sunk cost cycle
- **Codex ROI indeterminate, 부정 쪽 기울기, confidence medium** — denominator (consumer-protective fraction) 측정 부재
- 구조적 결함 = sunset asymmetry (실 retire 0건 since codeforge 정상 운영 진입, `is_transitional: false` ADR 85개 / `decommission` 0 match) + self-referential dogfood paradox 만성화

ADR-082 Amendment 5 §결정 1 sub-scope (1-C) 의 lane traversal fidelity loss 구조적 원인 #2 직접 인용:

> codeforge-design lane fan-out 불균형 — chief + 5 deputy + 4-tuple sub-tuple = 10+ agent advocacy. 1 user 요구 vs 10+ deputy mandate 의 weight 비대칭, deputy 가 자기 mandate 영역 expansion 만 강화 (cross-lane requirement traceability 약화).

Amendment 8 (CFP-1086, 2026-05-20) 가 5 → 7 permanent + 3 → 3+1 CONDITIONAL 로 **fan-out 확대** → chief + 7 deputy + 4-tuple = 12+ agent advocacy. 평가 결과의 정면 위배 영역. 본 Amendment 10 = boundary axis 영역만 partial retroactive rollback (AggregateArch → ModuleArch 통합 흡수, DataArch / APIContract 영역 보존).

### 변경 사항

| Agent | 변경 | model tier |
|---|---|---|
| **AggregateArchitectAgent** | **deprecated** — mandate (RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound aggregate boundary + Alembic 정책 tool-agnostic policy layer) carry-over to **ModuleArchitectAgent** (boundary axis 통합 advocate). agent file 실 deprecate = Wave 2 별 CFP carrier (codeforge-design plugin cross-repo sibling sync, ADR-010 정합). | Sonnet (Amendment 8) → deprecated |
| **ModuleArchitectAgent** | **mandate 확장** — module-level boundary (Amendment 7 CodeArchitect rename 본 mandate: module boundary + dependency direction + layered/hexagonal/clean module-level) + **aggregate-level boundary 흡수** (Amendment 8 AggregateArch carry-over: RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound aggregate boundary + Alembic 정책). boundary axis 단일 advocate. CONDITIONAL applicability carry-over from AggregateArch — `project.yaml aggregate_arch.applicable: bool` 보존 (frontend-only / API-only / external-managed RDB consumer non-applicable, default `true`). | Sonnet 유지 (mandate 확장 only, tier 무변경) |

7 permanent → 6 permanent. 3+1 CONDITIONAL = applicability carry-over로 갯수 무변경 (AggregateArch applicability → ModuleArch applicability). 4-tuple sub-tuple = 무변경 (E scope out-of-scope, 별 carrier).

### ADR-058 §결정 5 first applied carrier (약화 방향 evidence-grounded justification)

본 Amendment 10 = ADR-058 §결정 5 sunset_justification 의무 **first applied carrier** — codeforge 정상 운영 진입 이후 **ratchet 축소 첫 시도** (메타 평가에서 sunset asymmetry confirmed 후 첫 break-through).

#### evidence-grounded justification 3 axis

**(a) empirical evidence (Researcher + Codex 병렬 critical evaluation 수렴)**:

Researcher 평가 = codeforge dogfooding net 35% 정당화 (verify-before-trust + Epic gate 영역만 net positive). Codex 평가 = ROI indeterminate, 부정 쪽 기울기, confidence medium. denominator (consumer-protective fraction) 측정 부재 + sunset asymmetry (실 retire 0건 since codeforge 정상 운영 진입) + self-referential dogfood paradox 만성화. 두 독립 평가 수렴 = evidence-grounded.

verify-before-trust direct grep:
- `is_transitional: false` ADR 85개 / `true` 4개
- `decommission` 0 match in docs/adr/
- `status: Deprecated|Superseded` 4건 전부 historical (ADR-022/019/018/002) — codeforge 정상 운영 진입 (~2026-05 wave) 이후 **실 retire 0건 거의 확정**

**(b) pattern_count evidence (≥ 6 ≫ threshold 2)**:

- synthesizer-stale-reference pattern_count 6 (CFP-722/801/792/810/819/825) — synthesis layer 원본 drift
- unverified-self-write-claim super-class 5 (CFP-746/770/1000/1001/1002) — write-time semantic truth verify 부재
- scope 재확대 금지 invariant 6+ 위치 (CFP-758) — scope drift 만성
- DesignReviewPL cross-PL false-negative (CFP-906) — review 가 사실과 다른 결론

ADR-082 Amendment 5 §결정 1 sub-scope (1-C) 의 구조적 원인 #2 직접 인용 — chief + 7 deputy + 4-tuple = 12+ agent advocacy vs 1 user 요구 weight 비대칭 명시 evidence.

**(c) single-axis sufficiency (boundary axis 1 advocate 충분)**:

ModuleArchitect (boundary axis advocate) 가 module-level + aggregate-level boundary 통합 mandate cover 충분. Amendment 8 brainstorm 4-turn 사용자 정합 carrier 시점 (2026-05-20) RACI 충돌 (chief synthesis 가 두 axis dedup 비용) 가 정합 근거였으나, Researcher 평가 evidence 누적 후 chief synthesis 1 axis 압축 = fidelity loss source 직접 감소 evidence-grounded. boundary axis disjoint codify (Amendment 8) ↔ boundary axis 1 advocate (Amendment 10) trade-off 에서 Amendment 10 이 fidelity 영역 net positive.

#### ADR-064 §self-application top-down ratchet 의 evidence-gated exception 첫 carrier

ADR-064 §self-application = "amendment 는 강화 방향만 허용 (scope 확장 / 강도 강화). 약화 방향은 sunset_justification 의무로 차단". 본 Amendment 10 = 약화 방향 (scope 축소 — 2 agent → 1 agent, axis disjoint codify 축소) 의 evidence-gated exception 첫 carrier. mechanism = forbid-scope 축소 아닌 invariant carrier (boundary axis advocacy mandate) 보존 + axis dedup carrier 변경 only.

ADR-058 §결정 5 의 mechanical 약화 차단 logic 통과 — Amendment 10 의 sunset_justification 본문 (위 (a)/(b)/(c) 3 axis) 가 evidence-grounded justification 충족. ratchet top-down 강화 invariant 의 **evidence-gated exception 첫 historical event** — 본 Amendment 10 = 메타 평가 결과 적용의 self-application 첫 carrier (`is_transitional: false` 유지, 영구 정책 정합).

### paradox-break minimal path 2번째 application

본 Amendment 10 carrier (CFP-1126) = **사용자 직권 minimal path 2번째 application** (CFP-1110 paired Amendment 첫 적용 후 follow-through):

- Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 1+2 분리 0 / Retro PR 0
- ADR-013 명시 위배 (사용자 승인 2026-05-21 KST)
- ADR-024 정합 의무 보존 (branch + PR + main 직접 push 금지)
- ADR-054 doc-only fast-path 적합 (ADR-042 본문 + CLAUDE.md only, src/tests 무변경)
- closed-loop break 외부 결정 채널 두 번째 적용

### Wave 1 (declarative anchor) + Wave 2 (mechanical sibling sync) progression chain

| Wave | scope | enforcement | carrier |
|---|---|---|---|
| **Wave 1 (Amendment 10)** | declarative anchor — ADR-042 정책 SSOT + CLAUDE.md Deputy mandate 단락 cross-ref | doc-only (ADR-058 §결정 5 sunset_justification 의무 충족 — first applied carrier) | CFP-1126 (본 carrier) |
| Wave 2 (deferred-followup, 별 CFP carrier) | mechanical — codeforge-design plugin 안 `AggregateArchitectAgent.md` agent file 실 deprecate (delete or status:deprecated 표시) + ModuleArchitectAgent.md mandate 본문 확장 | cross-repo sibling sync (codeforge-design plugin, ADR-010 정합) | 별 CFP carrier (brainstorm 단계 결정) |

Wave 2 = deferred-followup, 본 Amendment 10 frontmatter `mechanical_enforcement_actions[]` 갱신 없음 (Wave 1 = ADR 본문 + CLAUDE.md cross-ref only).

### Out-of-scope (별 carrier 또는 reject)

본 Amendment 10 **포함**: AggregateArch + ModuleArch 통합 (boundary axis 영역만).

본 Amendment 10 **out-of-scope** (유지 / 별 carrier):

- **APIContract 흡수** (B scope) — Amendment 8 brainstorm 4-turn 사용자 정합 carrier, retroactive overturn 부담. transport axis disjoint 유지.
- **DataArch + AggregateArch 통합** (C scope) — Amendment 8 동인의 정면 부정 (OLAP/OLTP context switch). DataArch (OLAP only) 유지.
- **SecurityArch + InfraOpArch 통합** (D scope) — CFP-1086 reject 영역, security advocacy 약화 위험.
- **4-tuple sub-tuple 축소** (E scope) — helper 영역, fidelity loss source 아님. 별 CFP carrier.
- **LiveOps + LiveOrdering CONDITIONAL 통합** (F scope) — 축소 효과 작음, 별 CFP carrier.
- **codeforge-design plugin AggregateArchitectAgent agent file 실 deprecate** = Wave 2 별 CFP carrier (cross-repo sibling sync, ADR-010 정합).
- **DDDArchitectAgent 신설 reject** (Amendment 8 §) — 본 Amendment 10 영역 외 유지.

### Cross-ref

- [ADR-058 §결정 5](ADR-058-adr-sunset-criteria-mandate.md) — sunset_justification first applied carrier (약화 방향 의무 evidence-grounded justification 첫 발화)
- [ADR-082 Amendment 5 §결정 1 sub-scope (1-C)](ADR-082-write-time-self-write-verification-mandate.md) — 구조적 원인 #2 (codeforge-design lane fan-out 불균형) 직접 인용 source
- [ADR-064 §self-application top-down ratchet](ADR-064-decision-principle-mandate.md) — evidence-gated exception 첫 carrier (약화 방향 mechanical 차단 logic 통과)
- [ADR-071 Amendment 6 §결정 17](ADR-071-orchestrator-user-dialog-convergence.md) — paired sister carrier (lane return back-translation gate binding, 동일 사용자 directive lineage)
- [Amendment 8 (CFP-1086, 2026-05-20)](#amendment-8) — partial retroactive rollback (boundary axis 영역만, DataArch / APIContract / DDDArch reject 영역 보존)
- CFP-1110 — paired Amendment paradox-break first application (본 CFP-1126 = 2번째 적용)
- ADR-068 I-5 dimensional empirical grounding — spawn count Amendment 8 평균 28 → 본 Amendment 10 평균 26 (chief + 6 deputy + 3+1 CONDITIONAL + 4-tuple = 9 base + 17 CONDITIONAL/contributor activation, 7% 감소). full activation 40 → 38 (5% 감소). `[empirical-source: TBD]` (local probe / wiretap script 부재 정합)
- CLAUDE.md "Deputy mandate 매트릭스 (codeforge-design lane)" — 7 → 6 permanent + 3+1 CONDITIONAL + 4-tuple sub-tuple (carry-over applicability 보존)

---

## Amendment 11 — CFP-1155 UpgradeAgent walker model tier (declarative Sonnet → imperative walk Opus, CFP-1111 Wave 2 Story-4)

**날짜**: 2026-05-21

### 동기

ADR-098 §결정 2 (UpgradeAgent runtime ownership, CFP-1140 / Wave 1 Story-2) 가 UpgradeAgent **model tier 재평가 의무를 declare** 했다 — "본 ADR 은 model tier 재평가 의무를 declare 하며, 실 tier 확정은 Wave 2 Story-3 (CFP-703) 영역이다 (UpgradeAgent runtime mandate body 가 확정돼야 mandate depth 근거 tier 결정 가능)". 그러나 CFP-1111 Wave 1 의 paradigm replacement (ADR-097) 확정 후, UpgradeAgent runtime mandate body 의 실 재정의 (declarative 9-domain reconcile → imperative changelog walk) carrier 는 **Wave 2 Story-4 (CFP-1155)** 다. (주의 — contract §2.F.2 / ADR-098 §결정 2 가 인용한 "CFP-703" 은 **stale forward-ref**: 실제 CFP-703 = "Codex worker role-play structural issue" (OPEN, UpgradeAgent 무관 + Epic #1111 비소속). 실 declarative UpgradeAgent.md 신설 carrier = **CFP-743** (CFP-699 Wave 2 Story-3, CLOSED). verified-via `gh issue view 703/743` — DesignReview F-DR-1155-1.) 본 Amendment 11 = CFP-1155 가 runtime mandate body (walk + plan + apply 3-stage) 확정 후 model tier 실 결정.

> verified-via: Read docs/adr/ADR-098-upgrade-agent-runtime-ownership.md §결정 2 (L77-87 — "UpgradeAgent tier 결정 시 ... multi-source synthesis (다중 ADR/contract changelog dedup + reconcile plan 종합 판정) 깊이면 Opus, structured 명세 기반 mechanical apply ... 면 Haiku, single-mandate 실행이면 Sonnet" + "본 ADR = model tier 재평가 의무 declare only — tier 값 ... 자체는 본 ADR 에서 결정하지 않는다" verbatim)
> verified-via: Read docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §2.F.2 (L249 "model_tier_reassessment: required # ADR-042 §결정 2/§결정 3 — 실 tier 확정 = Wave 2 Story-3 CFP-703 (declare only)") — R-1 stale forward-ref 정정 대상 (CFP-1155 change-plan §R-1, follow-up carrier)

### 변경 사항

| Agent | 변경 | model tier | §결정 1 매트릭스 row |
|---|---|---|---|
| **UpgradeAgent** | **model tier 상향** — declarative `model: sonnet` (CFP-743) → imperative walk **Opus**. paradigm shift (declarative 9-domain reconcile → walk + plan + apply 3-stage) = role 재정의 = §결정 2 invariant 적용 후 tier 재판정 | **Opus** (claude-opus-4-7) | **Opus (a)** "Multi-source synthesis (3+ ... input dedup + 종합 판정)" |

### model tier 결정 근거 (Opus — multi-source synthesis 깊이)

UpgradeAgent imperative walk mandate = **walk + plan + apply** 3-stage (CFP-1155 change-plan §3.1):

- **plan stage = multi-source synthesis (Opus 신호)**: 7-plugin self-owned `CHANGELOG.md` (ADR-092) 다중 source 의 changelog entry dedup + min_prerequisite_version topological resolve (7-plugin DAG, ADR-096) + importance_score 종합 판정 (Story-6 hook). 이는 §결정 1 Opus (a) "Multi-source synthesis (3+ SubAgent / lane / contract input dedup + 종합 판정)" 정합 — 7 changelog source 의 cross-source 종합.
- **apply stage = structured mechanical (Haiku/Sonnet 신호) 단독이면 얕음**: per-family atomic transaction (CI / transaction rollback 즉시 감지). 그러나 mandate 전체 tier 는 가장 깊은 stage 기준 — walk+plan 의 multi-source changelog synthesis 가 §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 의 **Sonnet fully-cover 불가 영역**. Sonnet 으로 내리면 7-source dedup + topological resolve depth 가 shallow 해져 min_prereq mismatch 오판 / changelog entry 종합 누락 위험.
- **기존 declarative `model: sonnet` 정합 (CFP-743)**: declarative UpgradeAgent 의 Plan = 9-domain diff (단일 wrapper SSOT source ↔ consumer reconcile, multi-source synthesis 없음) → Sonnet 정합이었음. imperative walk paradigm 전환 = mandate depth 상향 (9-domain single-source diff → 7-source multi-changelog synthesis) = role 재정의 → §결정 2 invariant 에 따라 tier 재판정 = Opus.

**ratchet 강화 방향 (ADR-058 §결정 5 정합)**: Sonnet → Opus 상향 = mandate depth scope 강화 (약화 0건). `sunset_justification: null` 정당 (강화 방향 — frontmatter amendment_id:11). is_transitional: false 유지 (영구 정책).

### ownership 동기 (ADR-098 §결정 1 정합)

UpgradeAgent ownership = **codeforge-pmo 흡수** (ADR-098 §결정 1, cross-cutting agent PMOAgent sibling). 본 Amendment 11 = 정책 SSOT (tier 확정) only. agent file `model:` field 실 edit (`model: sonnet` → `model: opus`) + mandate body 재정의 (declarative → walk+plan+apply) = **codeforge-pmo sibling Story** 영역 (ADR-098 ownership — UpgradeAgent.md 가 codeforge-pmo 귀속, 단 현 file 위치 `templates/agents/UpgradeAgent.md` wrapper). ADR-042 §결정 3 "해당 lane plugin agent file 의 `model:` field 와 동기" 의무 = codeforge-pmo sibling PR 충족 (lane plugin MINOR bump trigger — ADR-023 / ADR-037).

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 11 = ADR-042 결정 1~6 본문 변경 0건. 변경 = (a) frontmatter amendment_log row 11 신설 + related_stories CFP-1155 + related_adrs ADR-098/097/076 append (b) 본 `## Amendment 11` body section. tier criteria (결정 1) + invariant (결정 2) + 신규 agent ADR 의무 (결정 3) + inheritance (결정 4) + Haiku rollback (결정 5) + 재-audit (결정 6) 모두 정책 변경 0건. ratchet 강화 방향 (Sonnet → Opus 상향 = scope 강화) → sunset_justification 불요.

### Cross-ref

- [ADR-098 §결정 2](ADR-098-upgrade-agent-runtime-ownership.md) — model tier 재평가 의무 declare (본 Amendment 11 이 Wave 2 Story-4 실 tier 확정 carry)
- [ADR-097](ADR-097-paradigm-replacement-governance-anchor.md) — paradigm replacement governance anchor (declarative → imperative = role 재정의 trigger)
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — declarative UpgradeAgent runtime SSOT (paradigm replace 진행 중, model:sonnet → Opus 상향 source)
- `docs/inter-plugin-contracts/imperative-walker-protocol-v1.md` §2.F.2 — UpgradeAgent runtime ownership + `model_tier_reassessment: required` cross-ref (R-1 stale forward-ref 정정 = CFP-1155 change-plan §R-1 follow-up carrier)
- [ADR-068 §결정 1 I-5](ADR-068-boundary-completeness-invariants.md) — walker walk source count 7 / grace window 12mo·9mo K8s dimensional empirical grounding (CFP-1155 change-plan §13.C)
- CFP-1155 change-plan (`docs/change-plans/cfp-1155-upgrade-walker-runtime.md`) — UpgradeAgent walker runtime 재정의 설계 SSOT (§3 walk+plan+apply / §R model tier 근거)

---

## Amendment 13 — RefactorAgent Reusability 1급 축 신설 (ISO/IEC 25010 유지보수성 gap 충당, CFP-2364)

**날짜**: 2026-06-19

### 동기 (실증 증거 + ISO/IEC 25010 정합)

ISO/IEC 25010 Maintainability(유지보수성) 는 5 sub-characteristics — **Modularity / Reusability / Analysability / Modifiability / Testability** — 로 구성되며, 그 중 **Reusability** 는 "the potential for assets to be utilized across multiple systems"(자산이 여러 시스템에서 재사용될 잠재력) 로 명시 정의된다. source: ISO/IEC 25010:2023(en) Product quality model (https://www.iso.org/obp/ui/en/#!iso:std:78176:en).

실증 결과 RefactorAgent 는 이 5축 중 **Modularity 1축** (decoupling / pattern / interface 분리) 만 1급으로 다루고 **Reusability 는 명시 공백**. 7 증거:

1. agent file 본문에 "재사용성" 0회 등장
2. 검출이 size-only (줄수 / 메서드수 임계) 라 중복 (clone) 에 맹목 — duplication / 동형 로직 미검출
3. structured output 에 reusability 슬롯 부재
4. scope guard ("요건 범위 외 advocacy 금지") 가 cross-cutting 공통추출을 억제 — cross-module 공통화가 본질적으로 요건 범위를 넘는데 일률 금지
5. 측정 metric 부재 — 재사용성 향상 falsifiable 검증 불가
6. sibling deputy (ModuleArch 등) 도 code reusability 를 owned 축으로 보유 안 함 — orphan 영역
7. repo-level 분해 mandate 0 — 응집 cluster 의 별 repo 분리 advocacy 없음

본 Amendment 13 = RefactorAgent **기존 mandate 의 scope 확장** (신설 deputy 아님) — Sonnet (a) single-mandate advocacy 패턴 유지하에 ISO/IEC 25010 Reusability 축을 1급 advocacy 로 codify.

### 변경 사항

| Agent | 변경 | model tier | §결정 1 매트릭스 row |
|---|---|---|---|
| **RefactorAgent** | **mandate 확장** — decoupling / pattern / interface 분리 3 카테고리 → + **(d) Reusability (재사용성)** 4 카테고리. DRY/WET 를 (b) Pattern 에서 (d) 로 이관 (개념 정합 — DRY/WET 본질 = 중복/재사용), (b) 는 아키텍처 패턴 (Hexagonal/Clean/Ports&Adapters) 만 retain | **Sonnet 유지** | (a) 무변경 — single-mandate advocacy 패턴 유지 (reusability pressure 식별·제안 단일 축, multi-source synthesis 는 ArchitectAgent chief Opus) |

카테고리 (d) Reusability 핵심:

- **검출 트리거**: 동일/유사 코드 블록 **rule of three** (3회 이상 반복) 또는 **duplication ratio** (중복 라인 비율) 임계 초과 또는 cross-module 동형 로직 발견 시 공통화 제안
- **output 슬롯**: (d) Reusability advocacy — 중복/유사 위치 verbatim + 추출 대상 공통 단위 + 재사용 단위 배치 (ModuleArch consult 표식) + 측정 신호 (duplication ratio / 제거 예상 중복 LOC / clone 수) + (repo-level) 분리 단위 + 경계 근거 + escalation 표식
- **scope guard escalation 예외**: cross-cutting 공통추출 / repo-level 분해는 본질적으로 cross-module/global 이므로 요건 범위 밖이라도 **escalation-tier 제안 가능** (escalation 표식 + ArchitectAgent 판정 회부 의무). 그 외 무관한 전역 리팩터링은 여전히 금지 — escalation 예외는 reusability(d) cross-cutting/repo-level 에 한정
- **repo-level 분해 advocacy**: 응집 cluster 가 별 deploy/ownership 단위로 분리 가치 시 repo 분해 제안 (escalation-tier) — module/aggregate-level 경계 확정 = ModuleArch authority / **repo-level 분해 경계 확정 = ArchitectAgent chief authority** (macro-architecture, ModuleArch mandate 초과 — ModuleArch consult)
- **측정 연동 (declaration-only Wave 1)**: (d) 제안마다 before 신호 (duplication ratio / clone 수 / 제거 예상 중복 LOC) emit → ArchitectAgent 통합 + 구현리뷰가 before → after 를 대조할 수 있도록 정량 신호 제공 (review 적용 시 falsifiable — 증거 ⑤ 충당). **단 자동 측정·enforcement (clone-detector / duplication-ratio CI gate) 는 deferred — 후속 carrier CFP** (mechanical wire = evidence-check-registry entry 별 CFP). 현 Amendment = Phase-1 declarative policy + 신호 제공까지 (자동 게이트 강제 단언 금지).

### axis disjoint (RefactorAgent advocacy ↔ ModuleArch authority — 반드시 보존)

본 Amendment 의 핵심 설계 원칙:

- **RefactorAgent** = reusability / decoupling **advocacy** — 중복 · DRY · 공통추출 · repo-split **pressure 식별·제안**. pressure 를 제안만 한다.
- **ModuleArchitectAgent** = boundary **authority** — module / package / aggregate 경계 **placement 결정** (module/aggregate-level). 경계를 확정한다.
- 둘은 **disjoint** — RefactorAgent 가 재사용 단위 / repo 분해 pressure 를 escalation-tier 로 제안하면, 경계 **확정** 권한이 layer 별로 귀속된다: ① **module/aggregate-level 경계 = ModuleArch authority** (ModuleArch mandate 범위 내) / ② **repo-level 분해 경계 = ArchitectAgent chief authority** (macro-architecture — ModuleArch mandate 초과 영역, ModuleArch 는 consult). RefactorAgent 의 경계 단독 확정 시도 = boundary 위반.

본 disjoint 는 ADR-086 §결정 1 axis 분석 의무 정합 — reusability advocacy axis (pressure 식별) 와 boundary placement authority axis (경계 확정) 가 orthogonal.

### ADR-086 framework 적용 — scope-fit (adjacent-case, axis 분석 lens)

**scope-fit 단락 (overclaim 차단)**: ADR-086 의 explicit scope = **신설 / 미도입 / rename / 축소** (roster decision — ADR-086 "미도입 결정 vs 신설 결정 disjoint axis" 단락 실측). **mandate 확장은 explicit 4종에 미열거**. 본 변경 = 기존 agent (RefactorAgent) 에 새 advocacy axis (d) 를 추가하는 **mandate 확장** — 따라서 본 Amendment 는 ADR-086 framework 의 **전면 governance self-application 을 주장하지 않는다**. 다만 새 mandate scope dimension 도입은 ADR-086 §결정 1 axis 분석 의무의 trigger 와 동형 (orthogonal axis 검증이 필요 — 새 축이 기존 deputy axis 와 겹치는지 확인 의무) 이므로, axis-disjoint lens + 5-checklist 를 **adjacent-case 로 적용**한다. 즉 ADR-086 = axis 분석 **도구** 의 적용이지, framework 의 전면 governance 주장이 아니다.

아래 표 = ADR-086 5-checklist 의 **adjacent-case 적용** (axis 분석 lens — mandate 확장에 도구로 활용):

| # | Check | 통과 기준 | CFP-2364 adjacent-case 적용 (RefactorAgent mandate 확장) |
|---|---|---|---|
| 1 | **axis disjoint** | 확장 mandate 가 기존 deputy 와 axis 중복 0 | **PASS** — reusability advocacy (중복·공통추출·repo-split pressure 식별·제안) ↔ ModuleArch boundary authority (경계 placement 결정) disjoint. DRY/WET 이관 = RefactorAgent 내부 카테고리 재정렬 (cross-deputy 충돌 0). cross-module 공통화 pressure 와 경계 확정 = orthogonal axis. |
| 2 | **cost-token budget** | spawn count 증가 시 ADR-068 I-5 empirical grounding | **PASS (N/A 증가)** — roster 무변경 (신설 deputy 0). RefactorAgent 1 agent 의 mandate scope 확장만 — spawn count 무변경 (평균 26 / full 38 유지, Amendment 10 base). 추가 token = 단일 agent 의 output 슬롯 1개 (d) 추가분 한정 (marginal). |
| 3 | **consumer carrier** | consumer overlay 필드 명시 / `project.yaml` schema 갱신 | **N/A** — reusability advocacy 는 모든 consumer 무조건 applicable (CONDITIONAL applicability 불요 — frontend/backend/data 무관하게 중복/공통추출은 보편). duplication ratio 임계는 consumer overlay 가 향후 tune 가능하나 본 Amendment 의 default (rule-of-three) 로 충분 — 신규 schema key 신설 0. |
| 4 | **sibling Epic align** | 진행 중 sibling Epic 과 RACI 충돌 0 또는 cross-ref | **PASS** — ModuleArch (boundary authority) 와 RACI 충돌 0 (axis disjoint codify 로 명시 분리). 진행 중 sibling Epic 의 RefactorAgent / ModuleArch mandate 변경 carrier 부재 (CFP-2364 단독). |
| 5 | **deferred trigger 명시** | 후속 carrier 별 CFP 명시 | **PASS** — duplication ratio 자동 측정 도구 (clone detector LSP 연동 mechanical enforcement) 는 향후 evidence-check-registry entry 별 CFP carrier (declaration-only Wave 1 — 본 Amendment 는 정책 + agent mandate codify, 자동 측정 wire 는 후속). repo-분해 escalation 의 mechanical gate 도 deferred. |

axis 분석 (§결정 1): 기존 N deputy axis 와 RefactorAgent 확장 axis (reusability pressure) 가 orthogonal — ModuleArch = 경계 placement authority / DataArch = 빅데이터 OLAP / APIContract = transport / SecurityArch = 보안 정책 / InfraOpArch = 운영 리스크 / TestContract = test contract 어느 것도 code reusability pressure 식별을 owned 축으로 보유 안 함 (증거 ⑥ orphan 영역 → RefactorAgent 흡수 정당). RefactorAgent 내부 (a)~(d) 4 카테고리 간 = single agent 내부 정합 (DRY/WET 이관 = 내부 재정렬).

종합: **mandate 확장 — adjacent-case 적용 PASS** — axis 분석 lens (5-checklist) 1 FAIL 0, axis disjoint 통과. ADR-086 framework 의 전면 self-application 주장 아님 (mandate 확장 = explicit scope 미열거 — axis 분석 도구만 차용). 신설 deputy 가 아니므로 roster 6 permanent + 3 sub-tuple 카운트 + RefactorAgent sub-tuple 사실 무변경.

### SSOT propagation (3 원본)

본 Amendment 의 RefactorAgent mandate 서술은 3 원본에 byte-consistent 의미로 sync:

1. `plugins/codeforge-design/agents/RefactorAgent.md` — agent file SSOT (4 카테고리 표 + (d) 슬롯 + scope guard escalation 예외 + 측정 연동 + escalation 기준)
2. `skills/deputy-mandate/SKILL.md` — wrapper canonical SSOT (primary axis matrix RefactorAgent row + DDD pattern mapping + axis disjoint 검증 단락)
3. `plugins/codeforge-design/CLAUDE.md` — mirror (sibling sync — 4-tuple sub-tuple line + Sub-agent fan-out 표 row)

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 13 은 ADR-042 의 결정 1~6 본문 변경 0건. 변경 = (a) §결정 1 Sonnet 표 후 inline marker (Amendment 13 발화 marker) (b) 본 `## Amendment 13` body section (c) frontmatter amendment_log row 13 + related_stories CFP-2364 + cross_ref (ADR-086 / ADR-063 / ADR-037) append. tier criteria (결정 1) + invariant (결정 2) + 신규 agent ADR 의무 (결정 3) + inheritance (결정 4) + Haiku rollback (결정 5) + 재-audit (결정 6) 모두 정책 변경 0건. ratchet 강화 방향 (카테고리 3 → 4 = scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불요 (frontmatter amendment_id:13 `sunset_justification: null`).

### bump + marketplace sync

- `plugins/codeforge-design/.claude-plugin/plugin.json`: version **0.26.0 → 0.27.0 MINOR** (RefactorAgent mandate 확장 — ADR-037 plugin version bump rule, mandate scope 확장 = MINOR trigger)
- marketplace version sync (ADR-063 atomic invariant) — `mclayer/marketplace` 의 codeforge-design entry version mirror (sync PR 선행 merge)

### Cross-ref

- ADR-086 (CFP-2364 — axis 분석 lens adjacent-case 적용: axis disjoint + 5-checklist 를 도구로 차용. mandate 확장은 ADR-086 explicit scope 신설/미도입/rename/축소 미열거 — framework 전면 self-application 주장 아님. 위 §ADR-086 framework 적용 — scope-fit 표 참조)
- ADR-091 §결정 1 (RefactorAgent DDD pattern mapping 표 — L193 row 가 "3 카테고리" frozen 보존, `⚠ CFP-2364` 마커로 4 카테고리 transition 명시 — AggregateArch/ModuleArch transitional 마커 관행 답습)
- ADR-058 §결정 5 — ratchet 강화 방향 (3 → 4 카테고리 scope 확장) → sunset_justification 불요
- ADR-037 (plugin version bump rule — mandate 확장 = MINOR bump trigger, 0.26.0 → 0.27.0)
- ADR-063 (marketplace atomic version sync — codeforge-design mirrored field version 변경)
- ADR-091 §결정 1/5 (RefactorAgent DDD pattern mapping — `domain-service-sub-tuple` 4 카테고리 정합)
- ISO/IEC 25010:2023(en) Maintainability sub-characteristics (Reusability 정의 source — https://www.iso.org/obp/ui/en/#!iso:std:78176:en)
- `skills/deputy-mandate/SKILL.md` + `plugins/codeforge-design/CLAUDE.md` — SSOT 3 원본 propagation (sibling sync)

---

## Amendment 14 — (d) Reusability 측정 연동 Phase-2 mechanical wire (warning-tier duplication-ratio, CFP-2369)

**날짜**: 2026-06-19

### 동기 (Amendment 13 의 deferred trigger follow-through)

Amendment 13 (CFP-2364) 는 RefactorAgent 에 (d) Reusability 축을 1급 advocacy 로 신설하되, **측정은 Phase-1 declarative** 로 두었다 — RefactorAgent 가 before 신호 (duplication ratio / clone 수 / 제거 예상 중복 LOC) 를 emit 하나, **자동 측정·enforcement (clone-detector / duplication-ratio CI gate) 는 deferred** (Amendment 13 §변경 사항 "측정 연동 (declaration-only Wave 1)" + ADR-086 5-checklist #5 "deferred trigger 명시 — 향후 evidence-check-registry entry 별 CFP carrier"). 본 Amendment 14 = 그 **deferred trigger 의 follow-through** — warning-tier mechanical wire 로 실현한다.

### 변경 사항 (mechanical wire 4 산출물 + 정정)

| # | 산출물 | 내용 |
|---|---|---|
| 1 | `scripts/check-duplication-ratio.sh` (신규) | warning-tier duplication-ratio 측정 — 항상 exit 0. detector 계약: `DUPLICATION_TOOL` env (target dir → 중복 백분율 stdout) override / 미설정 시 default jscpd (`npx --yes jscpd --reporters json`) 후 total percentage 추출 (`parse_jscpd_percentage` 함수, top-level key `statistics`(복수, v5.0.10 실측) 우선 + `statistic`(단수) 변종 허용, jq → python → grep fallback). `DUPLICATION_THRESHOLD` (default 5.0%, 비숫자면 5.0 fallback + warning) 초과 시 `::warning::` emit, 이하면 무출력. graceful degradation 3종 (target source 부재 / detector 불가 / ratio ≤ threshold) 모두 exit 0 |
| 2 | `scripts/test-check-duplication-ratio.sh` (신규) | anti-theater discriminating test — **stub detector** 로 dirty(ratio 9.0 > thr 5.0)=warning ↔ clean(1.0 ≤ thr)=no-warning **RED→GREEN 변별 실증** (둘 다 warning/no-warning 이면 theater). missing-case (경계값 ratio==thr → ≤ clean 처리) + warning 문자열 수치 grounding + exit code assert 포함 |
| 3 | `templates/github-workflows/duplication-check.yml` (신규, consumer-template) | consumer 가 `.github/workflows` 로 복사해 wire 하는 seed — node setup + `check-duplication-ratio.sh` (warning-tier) + `test-...sh` 2 job. **non-required** (branch protection 무변경). wrapper-self CI 아님 |
| 4 | `docs/evidence-checks-registry.yaml` entry `duplication-ratio-warning` | tier=warning, owner_adr ADR-042 / carrier_adr ADR-060, detect_command + consumer template workflow + sibling_dependencies CFP-2364 |
| — | `plugins/codeforge-design/agents/RefactorAgent.md` 정정 | "재사용성 측정 연동" 단락 deferred → tool-grounded — 자동 측정 수단 존재 (consumer CI 의 check-duplication-ratio.sh), 본 에이전트는 Grep/Glob 로 중복 위치 verbatim 인용 + 정량 ratio 는 CI 검사 결과 참조 (**에이전트 권한 확장 0 — 도구 직접 실행 안 함**). frontmatter / roster / 카테고리 4 / model tier Sonnet 무변경 |

### warning-tier 불변 + repo-분해 out-of-scope

- **warning-tier (비차단)**: `check-duplication-ratio.sh` 는 모든 경로 exit 0 — duplication ratio 초과 시 경고만 emit, merge 미차단. "게이트가 자동으로 향상을 강제 (blocking) 검증한다" 단언 금지 — 현 단계는 mechanical 측정 + warning 까지. **blocking 승격은 evidence 누적 후 별 CFP** (ADR-060 §결정 6 promotion gate).
- **repo-분해 mechanical gate 는 advisory 유지 (out-of-scope)**: Amendment 13 의 repo-level 분해 advocacy (응집 cluster → 별 deploy/ownership 단위 분리) 는 본 Amendment 의 mechanical wire 대상이 아니다. repo-분해 경계 확정 = ArchitectAgent chief authority (macro-architecture) 로 advisory 유지 — 본 duplication-ratio 측정은 코드-수준 중복 비율만 산출하며 repo 분리 판정을 mechanical 하게 강제하지 않는다.

### RefactorAgent 권한 경계 (확장 0)

본 Amendment 는 RefactorAgent 의 permission frontmatter 를 변경하지 않는다. 측정 도구 (jscpd 등) 구동 주체 = **consumer CI** (workflow). RefactorAgent 는 `Read` / `Grep` / `Glob` 로 중복 위치를 식별·verbatim 인용하고, 정량 ratio 는 CI 검사 결과를 참조한다 — 도구를 직접 실행하지 않는다 (읽기 전용 분석·제안 역할 보존).

### ADR-086 5-checklist #5 follow-through

Amendment 13 의 ADR-086 adjacent-case 적용 표 #5 (deferred trigger 명시) 가 "duplication ratio 자동 측정 도구 (mechanical enforcement) 는 향후 evidence-check-registry entry 별 CFP carrier" 로 명시했으며, 본 CFP-2369 = 그 명시된 후속 carrier 다. 신설 deputy 0 / roster 무변경 / axis disjoint 보존 (RefactorAgent advocacy ↔ ModuleArch authority — 측정은 advocacy 정량 신호 산출일 뿐 경계 확정 권한과 무관).

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 14 는 ADR-042 의 결정 1~6 본문 변경 0건. 변경 = (a) §결정 1 Sonnet 표 후 inline marker (Amendment 14 발화 marker) (b) 본 `## Amendment 14` body section (c) frontmatter amendment_log row 14 + related_stories CFP-2369 + cross_ref (ADR-042 Amd13 / ADR-060 / ADR-086 / ADR-037 / ADR-063) append. tier criteria (결정 1) + invariant (결정 2) + 신규 agent ADR 의무 (결정 3) + inheritance (결정 4) + Haiku rollback (결정 5) + 재-audit (결정 6) 모두 정책 변경 0건. ratchet 강화 방향 (declarative → mechanical 측정 = enforcement scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불요 (frontmatter amendment_id:14 `sunset_justification: null`).

### bump + marketplace sync

- `plugins/codeforge-design/.claude-plugin/plugin.json`: version **0.27.0 → 0.28.0 MINOR** (RefactorAgent 측정 grounding — ADR-037 plugin version bump rule)
- 루트 `.claude-plugin/plugin.json` (codeforge wrapper root): version **6.27.0 → 6.28.0 MINOR** (scripts/templates/workflow/registry 신규 consumer-facing surface — ADR-037)
- marketplace version sync (ADR-063 atomic invariant) — `mclayer/marketplace` 의 codeforge-design + codeforge wrapper entry version mirror (sync PR 선행 merge)

### Cross-ref

- ADR-042 Amendment 13 (CFP-2364 — Phase-1 declarative substrate: (d) Reusability 축 신설 + 측정 연동 deferred. 본 Amendment 14 = deferred trigger follow-through)
- ADR-060 (evidence-checks-registry framework — `duplication-ratio-warning` entry carrier, warning tier)
- ADR-086 5-checklist #5 (deferred trigger 명시 — CFP-2364 adjacent-case 적용 표의 후속 carrier 가 본 CFP-2369)
- ADR-058 §결정 5 — ratchet 강화 방향 (declarative → mechanical 측정 scope 확장) → sunset_justification 불요
- ADR-037 (plugin version bump rule — consumer-facing surface 신규 = MINOR bump, codeforge-design 0.27.0 → 0.28.0 + wrapper 6.27.0 → 6.28.0)
- ADR-063 (marketplace atomic version sync — codeforge-design + wrapper mirrored field version 변경)
- ISO/IEC 25010:2023(en) Maintainability — Reusability (duplication ratio = reusability potential 의 inverse 정량 proxy, https://www.iso.org/obp/ui/en/#!iso:std:78176:en)

## Amendment 15 — 비-webapp(backend service) sonnet dev preset 신설 (ServiceDeveloperAgent, §결정 1(b) enumeration 확장, CFP-2401)

**날짜**: 2026-06-25

### 동기 (비-webapp shape 의 sonnet 구현 tier 구조적 부재)

비-webapp consumer (예: mctrader = Rust backend service) 가 구현 lane 에 진입하면 **sonnet dev agent 가 0** 이다. 원인 2갈래:

1. **sonnet dev = webapp preset 전용** — 현 codeforge-develop 의 sonnet `role:dev` agent 는 `presets/webapp/` 의 BackendDeveloperAgent · FrontendDeveloperAgent 2종뿐이며, 이들은 web shape (서버/클라이언트 이원화) 전제로 설계됐다. frontend-less backend service shape 에는 부적합 (FrontendDeveloperAgent 는 그 자체로 무의미, BackendDeveloperAgent 의 path-scope deny 는 web-특화 — `templates/static/adapters/storage/sources` — service shape 엔 해당 분할 부재).
2. **generic DeveloperAgent = sonnet 아님** — generic `DeveloperAgent` 는 ADR-117 / CFP-2241 미 정부 제약 fable→opus override 상태 (surgical fable set 이 현재 `model: opus` override). 즉 비-webapp 구현이 generic DeveloperAgent 로 떨어지면 opus tier 로 동작 — ADR-042 §결정 1(b) "구현 work = Sonnet" 원칙이 비-webapp shape 에 실현되지 않는다.

본 Amendment 15 = webapp preset 이 이미 §결정 1(b) 에 enumerate 한 **sonnet-구현-preset 패턴** 을 비-webapp(frontend-less backend service) shape 로 확장해 그 공백을 메운다.

### 변경 사항

| Agent | 변경 | model tier | §결정 1 row |
|-------|------|-----------|-------------|
| **ServiceDeveloperAgent** (new entry) | codeforge-develop `presets/backend-service/agents/ServiceDeveloperAgent.md` 신설 — frontend-less backend service shape 의 sonnet dev. language-agnostic (Rust / Go / Python service 등 공통). path-write 경계 = `Edit(src/**)`/`Write(src/**)`/`Read`/`Grep`/`Glob`/`Bash(find *)`/`Bash(ls *)` allow; **deny = `tests/**` + `docs/**` + `src/**/adapters/storage/**` + `src/**/adapters/sources/**`** (web-특화 2종 `templates/**`·`static/**` 만 제거 — service shape 엔 frontend 분할 부재; DataEngineerAgent 경계 2종 `adapters/storage`·`adapters/sources` 는 webapp BackendDeveloperAgent 선례대로 **보존** — DataEngineerAgent(haiku core role:dev) allow 경로(`DataEngineerAgent.md:11-14` 실측)라 제거 시 path 소유 충돌) | **sonnet** | (b) Implementation work enumeration |

- **단일 generic preset · 단일 agent (Q4)**: domain/adapter 분할 안 함 — backend service 레이어는 단일 Change Plan 단위 공동 수정 (ModuleArch 판정). 4 deputy + 요구사항 3 관점 모두 단일 `backend-service` preset · 단일 `ServiceDeveloperAgent` 로 수렴.
- **이름 차별화**: `ServiceDeveloperAgent` (webapp `BackendDeveloperAgent` 와 구분 — 동명 시 overlay flatten 충돌, RefactorAgent 식별).
- **§결정 1 어느 row (Q1)**: webapp preset 선례대로 §결정 1(b) Implementation work enumeration 확장 — 별도 row 불요.

### model tier 결정 근거 (Sonnet)

ServiceDeveloperAgent 는 webapp BackendDeveloperAgent 와 동질 패턴 — Change Plan §3 / Story §8 의 structured 명세 안에서 production 코드를 구현하는 **implementation work** (code write / refactor). multi-source synthesis · 깊은 진단 reasoning 영역 아님 (그 영역은 ArchitectAgent chief Opus · DeveloperPLAgent FIX 진단). §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 정합") 충족 — 처음부터 single-shape implementation 정의이므로 Sonnet 적정. §결정 1(b) verbatim 정의 ("Implementation work — code write / refactor / test 구현") 정합.

### §결정 2 invariant 정당화 (sonnet 배정 정당 — over-packaging 정정)

본 preset 의 sonnet 배정이 §결정 2 invariant("Sonnet 으로 fully cover 가능 = role 정합 시그널, 단순 model field downgrade 금지") 에 위배되지 않음을 정직하게 정당화한다.

**실 role delta (정직 축소)**: ServiceDeveloperAgent 의 generic DeveloperAgent 대비 role 차원의 실 차별점은 **path-scope (web-특화 2종 deny 제거 + DataEng 경계 2종 보존) 위에 sonnet tier 를 실현하는 것** 1.x 축이다. preset-packaging(opt-in 레시피) · consumer-communication(frontend-less framing) 2종은 role 차별화가 아니라 **배포·문서 포장** 임을 인정한다 — 이 둘을 별 "delta 축" 으로 세는 것은 over-claim 이었다.

sonnet 배정이 정당한 1급 근거 2종:

1. **선례 승인**: webapp `BackendDeveloperAgent` 가 **동일 구조** (path-scope + shape framing → sonnet preset) 로 이미 §결정 1(b) 에 승인된 선례다 (`ADR-042:234` / `:253` enumerate). ServiceDeveloperAgent 는 그 승인된 패턴을 web → backend service shape 로 옮긴 것 — 새 tier 결정이 아니라 **승인된 tier 패턴의 shape 확장**.
2. **구조적 부재의 실측 뒷받침**: ADR-117 이 generic Developer/DeveloperPL = fable(현 opus override) 군, webapp Backend/Frontend = sonnet 으로 분류 (`ADR-117 §결정 1` 표 + ADR-042 §결정 1(b)) → 비-webapp shape 에는 sonnet 구현 tier 가 **구조적으로 부재**함이 실측 뒷받침된다. ServiceDeveloperAgent 는 그 공백을 채우는 sonnet 구현 tier 이지, generic DeveloperAgent 의 무근거 sonnet 복제가 아니다.

따라서 §결정 2 invariant 의 "단순 model field downgrade 금지" 우려 비해당 — sonnet 배정은 선례 승인 + 구조적 부재 실측 2 근거로 정당하며, role delta 는 path-scope+tier 실현으로 정직하게 한정한다.

### §결정 6 재-audit 미발동 명시

§결정 6 (기존 named Sonnet agent mandate 재정의 시 재-audit) 은 본 Amendment 에서 **발동하지 않는다** — ServiceDeveloperAgent 는 **신규 추가** (new entry) 이며, 기존 named Sonnet agent (DeveloperAgent · DeveloperPLAgent · 2 webapp preset) 의 mandate 를 재정의하지 않는다. 신규 enumeration 확장은 §결정 3 (신규 agent 도입 = plugin MINOR bump + ADR cross-ref) 경로이지 §결정 6 재-audit 경로가 아니다.

### §결정 3 정합 + bump

- `plugins/codeforge-develop/.claude-plugin/plugin.json`: version **0.10.4 → 0.11.0 MINOR** (신규 preset agent 추가 = consumer-facing surface 신설 — ADR-037 plugin version bump rule). plugin.json `description` 의 preset 평문 열거 갱신 (webapp 외 backend-service preset 추가 반영).
- marketplace version sync (ADR-063 atomic invariant) — `mclayer/marketplace` 의 codeforge-develop entry version mirror (sync PR 선행 merge).
- **실 bump · 실 agent file 신설 = Phase 2 codeforge-develop sibling PR** (본 Phase 1 = ADR-042 Amendment 15 + change-plan + Story §3/§7 설계 산출물).

### ADR-117 disjoint 명시 (surgical fable set 무손상)

ADR-117 / CFP-2241 surgical fable tier set (generic Developer / DeveloperPL 등이 현재 opus override 군) 와 ServiceDeveloperAgent 는 **disjoint** 다. ServiceDeveloperAgent 는 surgical set 밖의 신규 entry 이며 명시 `model: sonnet` — ADR-117 의 surgical 10 에이전트 opus override 영역을 건드리지 않는다 (generic DeveloperAgent 파일 미접촉, OOS 준수). 비-webapp consumer 가 본 preset 을 wire 하면 ServiceDeveloperAgent (sonnet) 가 구현을 맡고, generic DeveloperAgent 는 비활성화(해결책 A — 잔여 경로 없음, ModuleArch 판정).

### 기존 정책 변경 0건 (ADR-042 본문)

본 Amendment 15 는 ADR-042 의 결정 1~6 본문 변경 0건. 변경 = (a) §결정 1 Sonnet 표 후 inline marker (Amendment 15 발화 marker) (b) 본 `## Amendment 15` body section (c) frontmatter amendment_log row 15 + related_stories CFP-2401 + related_adrs (ADR-063/ADR-117/ADR-005) + cross_ref append. tier criteria (결정 1) + invariant (결정 2) + 신규 agent ADR 의무 (결정 3) + inheritance (결정 4) + Haiku rollback (결정 5) + 재-audit (결정 6) 모두 정책 변경 0건. inventory 본문 (:234 "2 webapp preset") 은 **`현재 agent inventory (2026-05-09)` 라는 dated snapshot** 이라 **본문 미수정** (그 시점 박제 — Event Sourcing). 본 Amendment body 에서만 **preset 2 → 3** (신규 backend-service ServiceDeveloperAgent 추가) 명시. (Amendment 12 는 inventory 의 **model 버전 표기**(Opus 4.7 / Sonnet 4.6 등)를 frozen audit trail 로 보존한 별개 선례이지 preset 개수를 freeze 한 게 아님 — 본 미수정의 근거는 dated snapshot 성격이지 Amendment 12 가 아니다.) ratchet 강화 방향 (preset 2 → 3 = scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불요 (frontmatter amendment_id:15 `sunset_justification: null`).

### Scope 경계 (Phase 1 / Phase 2)

- **Phase 1 (본 산출물)**: ADR-042 Amendment 15 (frontmatter + inline marker + body) + change-plan + Story §3/§7 설계 서사. 실 agent file · preset dir 미생성.
- **Phase 2 (codeforge-develop sibling PR)**: `presets/backend-service/agents/ServiceDeveloperAgent.md` + `presets/backend-service/README.md` (충돌 방지 절 = 해결책 A) + `presets/README.md` 카탈로그 등재 + plugin.json description 갱신 · version bump 0.10.4→0.11.0 + marketplace sync + consumer-guide §3c 반영.

### Cross-ref

- ADR-117 (surgical fable tier — generic Developer/DeveloperPL = fable(현 opus override)군. 신규 ServiceDeveloperAgent = surgical set 밖 명시 sonnet → disjoint, ADR-117 영역 무손상)
- ADR-037 (plugin version bump rule — 신규 preset agent 추가 = codeforge-develop MINOR bump trigger 0.10.4→0.11.0)
- ADR-063 (marketplace atomic version sync — codeforge-develop mirrored field version 변경)
- ADR-005 (`ADR-005-plugin-self-application-na-standardization` — plugin self-application N/A 표준; §8 Test Contract declarative-only(plugin-meta-na) 분류 근거)
- ADR-058 §결정 5 — ratchet 강화 방향 (preset 2→3 = scope 확장) → sunset_justification 불요
- CFP-2241 / ADR-117 Amendment 1 (미 정부 제약 fable→opus 임시 override — generic DeveloperAgent 이 그 override 군이라 비-webapp 구현이 sonnet 아닌 opus 로 떨어지는 root cause)

---

## Amendment 16 — Story-shape 조건부 model tier (stakes-gated static-per-context tier, CFP-2432)

**날짜**: 2026-06-27

### 동기 (sonnet footprint 부재 — 2차 진단)

사용자 directive (2026-06-27 KST, verbatim): *"mctrader의 코드가 잔뜩 개발되고 있는데 sonnet이 왜 안쓰이는거야?"* + *"sonnet 범위를 확장해야 되겠다. 적극적으로 제안해봐."* — 범위 선택(AskUserQuestion) = **Story-shape 조건부 tier (권장안)**.

진단(firsthand 실측): tier 사다리 = **haiku < sonnet < opus < fable**. 현 opus 군은 대부분 §결정 1 evidence-backed (multi-source synthesis / high-stakes domain / safety boundary / real-funds) + Codex 리뷰 확정. mctrader 는 그 opus/fable 기준(금융·live 거래·데이터·op-risk)을 정통으로 때리는 도메인이라 **무차별 opus→sonnet 강등 불가**. 그러나 same agent 도 Story 의 **shape(위험)** 가 낮으면 그 opus 근거의 일부가 발현하지 않는다. 본 Amendment = 이 stakes 의존성을 tier 선택의 1급 변수로 codify. CFP-2401 Amendment 15 ("sonnet 미사용" 비-webapp 구현 tier 부재) 의 2차 follow-through.

### D1 — stakes-gated static-per-context tier (개념 정의)

- **정의**: 같은 agent role 에 대해 **결과의 위험(stakes)** 에 따라 tier(opus↔sonnet) 를 분기. **난이도(task complexity) 기반 아님** — 외부 routing 문헌(FrugalGPT / RouteLLM / cascade) 의 거의 전부가 난이도/비용 축이며, high-stakes LLM 문헌은 "위험 크면 더 강한 모델"이 아니라 abstention / reliability / calibration 을 처방한다 (source: RequirementsReview §9 외부검증 — RACER / SelectLLM / Know-Your-Limits abstention survey). 따라서 stakes 를 1급 gating 변수로 쓰는 것은 routing taxonomy 의 합법적 변종(static, context-conditional)이나 **본 정책 고유 응용** — 외부 직접 선례 빈약(요구사항리뷰 lane verified, falsify 불성립).
- **gating 단위**: per-Story-context (spawn-time static) — per-query/per-output cascade 아님. 설계가 cascade(per-query confidence escalation)로 흐르지 않게 경계.
- **low-stakes shape 판정 = 4-AND (falsifiable enum)**:
  1. **실자금 없음** — 실거래 주문 / 실계좌 잔고 변경 mutation 없음
  2. **production cutover 없음** — 코드 배포 / feature flag flip / config flip / credential rotation / 운영 절차 변경 없음
  3. **신규 신뢰경계 없음** — 아래 §D1-A 5-enum 모두 不해당
  4. **live 외부 API 호출 없음** — live exchange/외부 API 호출 부재 (**read-only 시세 수집 포함** — InfraOpArch G3 false-negative 가드)
  4개 **모두 충족** = low-stakes (sonnet 후보). **하나라도 미충족 = high-stakes (opus)**. unknown/누락 = opus (fail-safe, §D4 AC-8).

#### §D1-A — "신규 신뢰경계" falsifiable 5-enum (SecurityArch consult)

신규 신뢰경계 = TRUE if ANY (보안 관점 — SecurityTest lane SSOT, §7.1 trust boundary 정의에 등재):
1. 새 외부 의존(연동/API/메시지큐/외부 데이터소스) 신설 — **read-only 포함**
2. credential 종류 추가(새 secret/token/key class)
3. 기존 credential 권한 범위(scope) 확대
4. 데이터 분류 상향 노출 경로 신설(Public→Internal/PII/Secret 가 새 컴포넌트로 흐름)
5. trust 의존 외부 시스템의 신뢰 등급 변경(내부→3rd-party 등)

위 5 중 0건일 때만 "신규 신뢰경계 없음" 충족. 판정 granularity = Story 전체 aggregate(한 컴포넌트라도 해당 시 전체 high — §D4 mixed-shape 규칙 정합). live API read-only(잔고/계좌 조회·시세 수집)는 enum 1 + 조건 4 에 동시 해당 → high (RequirementsReview F4 경계 해소).

### D2/§결정 1 — §결정 2 invariant 충돌 해소 (1순위)

**충돌 명제**: §결정 2 invariant = "Sonnet 으로 fully cover 가능 = role 결손 신호" + "양 방향 미스매치 모두 ADR scope". opus→sonnet flip 이 이 invariant 위반인가?

**해소 = stakes 는 mandate-orthogonal 축**:

- tier = f(**mandate depth**, **stakes**). 두 축은 orthogonal — mandate depth 는 역할 구조 자체의 깊이(stakes 무관), stakes 는 그 역할이 *그 Story 에서 carry 하는 결과 위험*.
- §결정 1 Opus 기준 7종 분해: (a)multi-source synthesis / (b)GPT-5 peer / (f)cross-story pattern / (g)deep research = **stakes-무관**(역할 구조 깊이). (c)high-stakes domain / (d)safety boundary / (e)real-funds = **stakes-conditional**(Story 가 그 stakes 를 carry 할 때만 발화).
- **stakes-conditional 근거는 본질이 조건부** — opus floor 가 그 stakes 가 없는 shape 에서까지 적정하다고 단정한 적 없음. low-stakes shape 정의(실자금/cutover/신규경계/live API 4 변수 미발현)는 정확히 (e)/(d)/(c) stakes 변수를 발현 안 함 상태.
- **선례 = LiveOps/LiveOrdering CONDITIONAL 과 동형 논리**: 그 deputy 의 opus depth 가 live-touching stakes 있을 때만 *필요*하여 live Story 한정 spawn(없으면 skip). 본 Amendment = 그 CONDITIONAL 패턴을 **permanent agent 의 tier 선택으로 일반화**(skip 대신 down-tier).
- **invariant 위반이 되는 유일한 경로** = shape 분류만 하고 **mandate 표면 재정의를 동반 안 할 때**(단순 model field downgrade). 따라서 flip 은 **shape별 mandate 표면 명시 동반 의무** — low-stakes shape 에서 InfraOpArch = "§7.4.1/.2/.3/.4 N/A 발화 + §7.4.5/.6 표준 hygiene 잔존"의 mandate 표면을 명문 declare(Phase 2 agent file 주석). enforcement 선례 = Amendment 5 의 mandate text 재정의 동시 산출물 의무(§결정 2 invariant 의 enforcement mechanism).

### §결정 1(d) 비대칭 — InfraOpArch 단독 1급 flip 후보 (InfraOpArch self-assessment verify)

§결정 1(d) safety boundary owner 4종(SecurityArch / DataArch / TestContractArch / InfraOpArch) 중 InfraOpArch 만 1급 flip 후보. InfraOpArch self-assessment(mandate 권위 verify):

| §7.4 sub | 발현 trigger | low-stakes(live 0) shape 판정 |
|---|---|---|
| §7.4.1 DR / failover | 외부 endpoint 장애 모드 + in-flight 상태 복원 | **완전 dormant** — 백테스트 = idempotent 재실행 batch, in-flight 0 |
| §7.4.2 Cancel-on-disconnect | 외부 stream(WebSocket/SSE) 끊김 감지 | **완전 dormant** — live stream 부재, disconnect 개념 미성립 |
| §7.4.3 Clock sync (CONDITIONAL) | 외부 time-window 프로토콜(recvWindow/signed ts) 의존 | **완전 dormant** — 과거 데이터 재생 wall-clock 무의존 |
| §7.4.4 Rate limit / quota | 외부 API weight/IP ban 모델 | **부분 dormant** — 연산 자체 live 호출 0(단 데이터 수집 시 재발현 → 조건 4 가드) |
| §7.4.5 Env isolation | secret 분리·누설 차단 | **부분 잔존** — 데이터 소스 credential hygiene 잔존(sonnet cover 가능 — 결정론적 체크리스트) |
| §7.4.6 Container | `infra_strategy`(Docker-first, ADR-033) | **shape 무관 상존(단 stakes 와 직교)** — batch 컨테이너 표준 restart/volume(sonnet cover 가능) |

판정: safety 핵심 4축(7.4.1/.2/.3/.4)의 **발현 trigger 가 live 부재 shape 에 물리적 부재** = opus-급 깊은 추론을 요구하는 부분이 발현 안 됨 = InfraOpArch 1급 flip 정당성의 실체. 잔존 2-sub(7.4.5/.6)는 sonnet single-mandate advocacy 깊이로 fully cover(§결정 2 invariant 정합). **단 "완전 N/A"는 over-claim** — 잔존 2-sub 를 N/A 로 함께 묶으면 안 됨(D2 verbatim "DR/rate-limit/clock 사실상 N/A"가 env isolation/container 까지 N/A 로 읽히지 않게 Phase 2 문안에서 분리).

**제외 근거**:
- **SecurityArch**: ADR-117 surgical 10 set(현 opus override) 밖 OOS + 보안 trust boundary 는 low-stakes shape 에도 상존(공격 표면은 stakes 무관) → flip 불가.
- **DataArch**: 데이터 integrity invariant 가 백테스트에도 상존(데이터 정합은 1급 관심사) → 별도 판정(본 Story scope 외).
- **TestContractArch**: §8 perf baseline / coverage invariant 상시 → 별도 판정(본 Story scope 외).

### §결정 3 — DomainAgent v1 제외 (F3 반영, 보수 택1)

DomainAgent 는 InfraOpArch 보다 tier-flip 정당성이 **약하다** — InfraOpArch safety mandate 는 live 부재로 *물리적 dormant* 인 반면, DomainAgent invariant 해석 mandate 는 shape 무관하게 **상존**(백테스트도 financial-correctness invariant 보유 — lookahead bias / survivorship / fee·slippage / PnL invariant, RequirementsReview F3 catalog). 누설 = 백테스트 결과 자체가 거짓 → 그 결과로 내릴 실자금 결정이 오염(**indirect real-funds risk**). risk 직접성만 약화될 뿐 누설 가능성 자체는 0 아님.

**결정 = v1 보수: DomainAgent 제외 + follow-up CFP** (Orchestrator 권장 방향 (a)/(b) 중 (b) 택1). (a) financial-invariant surface 없는 shape(순수 tooling/UI/infra lib)로 4번째 조건 gating 하는 대안보다, (b) v1 제외가 falsifiable-conservative — 백테스트(financial invariant 보유)가 DomainAgent sonnet 으로 새지 않게 하는 안전한 경계. financial-invariant surface 의 falsifiable 경계 확정(어떤 shape 가 도메인 invariant 0 인지)이 v1 에서 충분히 닫히지 않아, premature flip 시 F3 가 경고한 risk(백테스트 invariant 누설)를 그대로 노출. → DomainAgent flip 은 financial-invariant catalog(F3) codify + 경계 falsifiable 확정 후 별 carrier.

> **[Amendment 17 fulfillment 2026-06-28, CFP-2445]**: 위 "별 carrier" = **CFP-2445 / Amendment 17**. 예약 조건(catalog codify + 경계 falsifiable 확정)을 선결충족 후 DomainAgent 를 **financial-invariant-0 shape 한정 조건부 sonnet** 으로 채움 — (4-AND low-stakes) AND (financial-invariant-0 shape) 2-predicate. financial-invariant-0 = stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축(DomainAgent 전용 별 predicate). 본 §결정 3 의 "v1 제외" 는 v1(CFP-2432) 시점 frozen 결정으로 유효(Event Sourcing) — Amd17 = v1 이후 follow-up 자리 충족(Amd16 무효화 0). 상세 = 본 ADR `## Amendment 17` body section.

> **ADR-117 결정 2 cross-ref (silent override 금지)**: ADR-117 §결정 2 가 "Domain"을 "단기 구조적 역할"로 fable 상향에서 명시 제외했으나, 그 단정 대상은 **fable 적격성(상향 축)** 뿐 — opus floor 적정성(하향 축)을 단정한 적 없음(ADR-117 전문 sonnet 하향 논의 0건, Continuity §4.3 falsifier verify). 두 ADR 이 같은 agent(DomainAgent)를 분류하므로, **본 Amendment 가 DomainAgent 를 v1 제외하되 향후 flip 시 ADR-117 §결정 2 "Domain opus 유지" 문구가 stakes-conditional 로 정제됨을 cross-ref 명시 의무** — 판정 축 disjoint(상향 fable vs 하향 sonnet), 직접 모순 아님.

### §결정 4 — conditional-model 메커니즘 (fail-safe, 신설 0)

- **frontmatter `model: opus` 보존** = fail-safe default(override 누락 = opus). 영구 정책 주석으로 conditional 표기(CFP-2241 override 주석 패턴 — 임시표식 아님).
- **Orchestrator spawn-time `opts.model: sonnet` override** = low-stakes 4-AND shape 에서만. Agent tool `model`/`opts.model` 파라미터가 frontmatter 상회("Takes precedence over the agent definition's model frontmatter" — Agent tool schema verified). **fresh `Agent` spawn 경로 필수 — SendMessage resume 금지**(원본 frontmatter `model` 재해석 → override 무효, ADR-057 §결정 4 / CFP-2236 실측 root cause). FIX 루프 재진입에서 stakes-override 가 silent 하게 풀릴 위험 → 재진입도 fresh spawn 으로 stakes 재판정.
- **메커니즘 신설 0** — opts.model override 는 ADR-057 §결정 4 fallback re-spawn 으로 이미 운영 중. 진짜 작업 = stakes 분류 enum(D1) + 판정 규칙 + spawn-time 가용성.

### consumer overlay 제약 (SecurityArch consult — 확장-only + 2중 enforcement)

- **비대칭 = 보안상 올바른 방향**: consumer overlay 는 tier 를 **보수 방향(opus 강제)만** 가능, **down-tier(opus→sonnet) 공격적 override 불가**(ADR-127 §결정 6 확장-only 정합). down-tier 차단 = consumer 가 비용 인센티브로 stakes 를 거짓 low 분류 → safety deputy 약화시키는 채널 봉쇄.
- **enforcement = 문서규칙 단독 불충분 → 2중**: (1) **schema-gate**(bootstrap strict-check 가 wrapper-floor 보다 약한 overlay tier 거부) + (2) **spawn-time clamp**(Orchestrator 가 `max(wrapper_floor, overlay_request)` 보수 방향만 반영, 더 약한 sonnet 요청은 silent drop 아닌 **명시 거부 + 로그**). 선례 `pat_rotation_cadence_days` "weaken 금지"가 문서규칙만이라 honor-system 인 약한 형태를 답습 금지.
- **stakes 자기보고 = untrusted 입력**: §7.1 진입점에 "consumer-authored stakes signal — untrusted, 확장-only clamp + fail-safe default 로 sanitize" 명기. fail-safe(누락→opus)는 omission 공격만 차단, commission(high 를 명시 low 기입)은 down-tier 차단(확장-only)이 방어선 — **AC-3 확장-only + AC-8 fail-safe 가 합쳐져야 trust model 이 닫힌다**. 적극적 high→low 거짓보고 자동 탐지는 불가 → 수용(§5.4 OOS), blast radius = consumer 자기 프로젝트 국한.

### F1 evidence-gate — sonnet ≥ opus baseline 측정 protocol (1순위, TestContractArch consult)

tier-flip = **provisional**. RequirementsReview F1(P1): sonnet 산출물 품질 ≥ opus baseline 측정 protocol + 미달 시 opus 복원 trigger 를 evidence-gate/AC 로 승격.

> **F1 인용 정정**: F1 이 인용한 "ADR-057 Amendment 4 = Codex 리뷰 sonnet 품질 저하 실측 → opus 복원" 은 **mislabel** — ADR-057 Amd4(:320-335) = 버전핀→별칭 전환(품질 무관). 실제 Codex 독립 review baseline 선례 = **ADR-057 §결정 3 / ADR-042 Amendment 4 본문**(ADR-057:60 "Codex 독립 리뷰 결과 6개 에이전트가 Sonnet 보다 Opus 기준에 더 부합" — verified). 본 Amendment 는 정정된 선례를 인용.

**4-step 측정 protocol (falsifiable)**:

| step | 항목 | 정의 |
|---|---|---|
| (a) 측정 대상 | InfraOpArch §7.4 운영 리스크 표 완결성(§7.4.1~.6 sub 6종 각 판정/근거/marker 충족 행 수) | 정량 행 수 — "충실해 보임" 주관 어휘 금지 |
| (b) opus baseline 캡처 | Codex 독립 review verdict(ADR-057 §결정 3 선례 재사용) 1차 + 가능 시 동일 Story 양 tier 대조 spawn(packet 고정) 2차 | baseline = opus 산출물의 (a) 정량값 |
| (c) "미달" 임계 (OR) | ① sonnet 산출물 §7.4 sub 누락 ≥ 1 OR ② Codex review P0/P1 finding ≥ 1 OR ③ 양 tier 대조 시 sonnet 식별 항목 < opus × tolerance | binary, falsify 가능 |
| (d) 복원 trigger 발화 | ADR-058 §결정 5 evidence-gate 입력 등재 + AC-9 + (실행 surface) `check-tier-downgrade-guard.sh` 동형 marker gate — sonnet 채택 시 commit/PR body `stakes-tier-evidence:` marker 의무 | mechanical = marker 부재 시 FAIL |

> **AC-9 (신규)**: low-stakes sonnet tier-flip 채택 시 (b) baseline + (c) 임계 측정 결과가 존재하고 (c) 3-임계 모두 不해당(누락 0 ∧ P0/P1 0 ∧ tolerance 충족)임을 evidence 로 인용. 측정 부재 또는 임계 1+ 해당 시 해당 agent **opus 복원**(fail-safe). = sunset_justification 의 evidence 실체.

### D4 — ChangeImpactAgent sonnet 비준 (명시 reversal)

ChangeImpactAgent = **Sonnet 비준 (unconditional, stakes 무관)**. 역할 = src/** 읽기전용 코드 변경 델타 매핑(AS-IS → DELTA, Story §4.1 owner) 단일 축 = §결정 1 Sonnet (a) single-mandate advocacy 정합.

**명시 reversal**: ADR-042 Amendment 5 + ADR-057 §결정 3 이 ChangeImpactAgent 를 사용자 verbatim("changeimpact는 내가 보기에 opus가 괜찮아보인다")으로 **opus 확정**했던 것을 → **2026-06-27 사용자 directive("sonnet 범위를 확장해야 되겠다")로 명시 reversal**(silent 금지 — amendment_log + 본 §D4 + §결정 1 Amendment 5 표 inline marker 3곳 투명 기록). agent file `plugins/codeforge-requirements/agents/ChangeImpactAgent.md:3` 은 이미 `model: sonnet`(정책 drift 상태) → 본 reversal 로 정책↔파일 정합(D4 drift 정정).

### §결정 6 재-audit 미발동

§결정 6(기존 named Sonnet agent mandate 가 "패턴 실행" 방향 재정의 시 재-audit)은 본 Amendment 에서 **미발동** — 본 Amendment 는 InfraOpArch 의 tier 를 stakes-conditional 로 분기할 뿐 기존 Sonnet agent 의 mandate 를 패턴 실행 방향으로 재정의하지 않는다. ChangeImpactAgent sonnet 비준도 mandate 재정의 아닌 tier 정합(역할 = single-mandate advocacy 유지).

### §8 Test Contract surface (TestContractArch consult — plugin-meta-na 정정)

본 Story 는 단순 docs-only 아님 — wrapper `scripts/check-*.sh` 가 CI gate 로 라이브 실행되는 **실행 가능 test surface 존재**(`check-tier-downgrade-guard.sh` = tier 하향 + justification marker gate 동형 선례 verified, `get_consumer_tier.py` = consumer project.yaml tier read fail-loud 선례 verified). 면제 분류 = `plugin-meta-na` 전면 아닌 **runtime-inert(agent md 정책) + shell validator 커버 후보** 혼합. discriminating test(stakes 조합 → 기대 tier truth-table 8행, 단일 변수 toggle dirty/clean) + fail-safe/mixed 경계 invariant(INV-1 fail-safe monotone / INV-2 high-absorbing / INV-3 확장-only monotone) = change-plan §8 상세. perf baseline = N/A(spawn-time 선택 정책, 런타임 latency 영향 없음).

### 기존 정책 변경 0건 (ADR-042 본문 결정 1~6)

본 Amendment 16 = ADR-042 결정 1~6 본문 **변경 0건**. 변경 = (a) §결정 1 Sonnet 표 후 inline marker(Amendment 16 발화) + Amendment 5 표 후 ChangeImpactAgent reversal marker (b) 본 `## Amendment 16` body section (c) frontmatter amendment_log row 16 + related_stories CFP-2432 + related_adrs(ADR-058/064/127) append. tier criteria(결정 1) — stakes 축은 결정 1 의 (c)(d)(e) 기준의 *조건부 발화 명시*이지 기준 자체 변경 아님. invariant(결정 2) — stakes-orthogonal 논증으로 *양립 확인*, invariant 텍스트 변경 0. 신규 agent ADR 의무(결정 3) / inheritance(결정 4) / Haiku rollback(결정 5) / 재-audit(결정 6) 모두 변경 0건.

### ratchet 방향 — 약화(evidence-gate)

opus→sonnet tier-flip = ratchet **약화 방향**(reasoning depth 하향) → `sunset_justification` evidence 의무(ADR-058 §결정 5 / ADR-064 §결정 7 is_transitional:false governance symmetric evidence-gate). frontmatter amendment_id:16 `sunset_justification` 본문 = evidence-grounded 3 axis(stakes-gated 정제 / falsifiable evidence-gate 동반 / 지배 low-stakes shape 비용효율). is_transitional: false 유지(영구 정책 정제, transitional pilot 아님). ChangeImpactAgent sonnet 비준(D4)도 약화 방향이나 그 evidence = "역할 = single-mandate advocacy 단일 축 = §결정 1 Sonnet (a) 정합 + 사용자 directive verbatim" 으로 sunset_justification 본문에 포함(별 row 불요 — 같은 carrier).

### 발효 timing — 비준(declarative) ≠ 즉시 런타임 적용(enforcement)

본 Amendment 16 의 `amendment_id:16 status: applied` 는 **정책 비준(declarative ratification)** 의미이지 즉시 런타임 발효를 뜻하지 않는다. **Phase 1(본 Amendment) = 정책 비준** — stakes-gated tier 정책 + low-stakes 4-AND enum + tier-flip 대상(InfraOpArch) 확정. **실 발효(enforcement) = Phase 2 guardrail 완비 시점** — (a) InfraOperationalArchitectAgent.md frontmatter conditional 주석(shape별 mandate 표면 declare) + (b) `project.yaml story_stakes` schema + (c) gating 배선(orchestrator-playbook §3.0 spawn-time `opts.model` 결정 로직 + deputy-mandate SKILL) + (d) `stakes-tier-evidence:` marker gate 가 모두 갖춰져야 low-stakes shape 에서 실제 opus→sonnet override 가 발화한다. guardrail 완비 전까지는 frontmatter `model: opus` fail-safe default 가 유지되어 **현행 opus 동작 무변경**(파괴적 변경 0). 이 비준↔발효 split 은 AC-9 provisional / F1 evidence-gate 정합 — tier-flip 은 측정·복원 loop 으로 가드되는 provisional 정책이므로 비준만으로 무가드 런타임 적용 금지. **선례 = Amendment 13(declarative substrate) → Amendment 14(mechanical wire) 의 declarative→mechanical split 동형** (정책 비준과 enforcement realization 의 Phase 분리).

### Scope 경계 (Phase 1 / Phase 2)

- **Phase 1 (본 산출물)**: ADR-042 Amendment 16(frontmatter + inline marker + body) + change-plan + Story §7 설계 서사.
- **Phase 2 (sibling PR)**: `InfraOperationalArchitectAgent.md` frontmatter conditional 주석(shape별 mandate 표면 declare) + `docs/project-config-schema.md` `story_stakes` 블록 신설 + gating 배선(orchestrator-playbook §3.0 + deputy-mandate SKILL) + `ChangeImpactAgent.md` 정합(이미 sonnet — 주석만) + deputy-mandate SKILL InfraOpArch row stakes 분기 각주 + consumer-guide stakes 섹션 + plugin bump(변경 plugin MINOR — ADR-037) + marketplace sync(ADR-063) + F1 baseline 측정 protocol 위치.

### Cross-ref

- ADR-058 §결정 5 — 약화 방향 sunset_justification evidence requirement(tier-flip 하향 evidence-gate, 차단 아님)
- ADR-064 §결정 7 — is_transitional:false governance ADR 약화 symmetric evidence-gate(ADR-042 is_transitional:false 에 §결정 5 적용 근거)
- ADR-117 §결정 1/2 — surgical fable tier(SecurityArch surgical set / Domain "단기 구조적" fable 제외 = 상향 축, 본 Amendment = 하향 축 disjoint, silent override 금지 cross-ref)
- ADR-057 §결정 3(Codex 독립 review baseline 선례 — F1 정정 인용) / §결정 4(spawn-time opts.model override fresh-spawn 메커니즘 SSOT)
- ADR-127 §결정 6 — consumer overlay 확장-only(down-tier 공격적 override 불가)
- ADR-042 Amendment 5(ChangeImpactAgent opus 확정 source — 본 Amd16 reversal + invariant enforcement mandate text 재정의 선례) / Amendment 15(CFP-2401 "sonnet 미사용" 진단 1차, 본 Story 2차 follow-through)
- ADR-086 — axis 분석 lens(stakes axis ⊥ mandate axis disjoint 검증 도구 adjacent-case. 본 Amendment = 신설 아닌 tier 분기 → framework 전면 self-application 주장 아님)
- CFP-2432 change-plan(internal-docs `wrapper/change-plans/`) — stakes-tier gating 설계 SSOT(§3 메커니즘 / §7 trust boundary / §8 Test Contract / §11 N/A)

---

## Amendment 17 — DomainAgent financial-invariant-0 조건부 sonnet tier (CFP-2445, CFP-2432 follow-up)

**날짜**: 2026-06-28

### 동기 — Amendment 16 가 예약한 자리

Amendment 16(CFP-2432)이 Story-shape 조건부 model tier 를 `InfraOperationalArchitectAgent` 단독 flip 으로 v1 확정하며 **DomainAgent 는 §결정 3 에서 v1 명시 제외 + follow-up CFP** 로 deferred 했다. 사유: low-stakes 4-AND shape(실자금 없음 ∧ cutover 없음 ∧ 신규 신뢰경계 없음 ∧ live 외부 API 없음)라도 **백테스트는 financial-correctness invariant 상존**(lookahead bias / survivorship / fee·slippage / PnL) → DomainAgent 를 그대로 sonnet 으로 내리면 invariant 누설 risk(InfraOpArch 의 §7.4 stakes-coupled *물리적 dormant* 와 달리 정당성 약함). 사용자 directive(2026-06-28 KST, verbatim): CFP-2432 완료 직후 *"이어서 착수해"* — Amd16 §결정 3 가 예약한 "catalog codify + 경계 falsifiable 확정 후 별 carrier" 자리를 **선결충족 후 채운다**. **reversal 아님** — Amd16 무효화 0, v1 제외(CFP-2432 자체)는 frozen 유효, 본 Amendment = v1 이후 확장.

### D1 — 백테스트 financial-correctness invariant catalog (11 invariant + A/B 분류)

D2/D3 의 입력. 백테스트의 도메인 본질 = "숫자가 그럴듯한데 틀린" **silent corruption** — 거의 모든 invariant 위반이 백테스트 수익을 *부풀린다*(낙관 편향). crash 가 아니라 "좋아 보이는 틀린 결과"라 CI·테스트가 못 잡는다. 이 silent 성격이 financial invariant 식별을 **opus급 도메인 판단의 기본값**으로 만드는 근거다(결과 비접촉 shape 에서만 표면이 0).

| # | invariant | 부류 (A 정적 / B 프로세스·메타데이터) | opus 판단 강도 |
|---|---|---|---|
| INV-1 | Lookahead bias / future-leak | **A** (시점 misalignment = 데이터 흐름 정적 패턴 falsifiable) | opus 필수 (코드 무증상, 시간 인과 추적) |
| INV-2 | Survivorship bias | **B** (universe 완전성 = 데이터 출처·시점 메타데이터 의존) | opus 필수 (데이터 출처 신뢰 판단) |
| INV-3 | Fee / commission / slippage / spread | **A** (모델 존재·값 = 정적 산술 falsifiable) + 모델 타당성은 opus | opus(모델 타당성) / sonnet(파라미터 검증) 2-층 |
| INV-4 | PnL / position state 정합 | **A** (`equity = cash + Σ(holdings × mark)` 항등식 = 정적 단위테스트) | opus(정의·엣지) / sonnet(항등식 검증) 2-층 |
| INV-5 | Point-in-time data 정합 | **B** (PIT 준수 = 시점 메타데이터·data lineage 없이 정적 falsify 불가) | opus 필수 (corporate-action·lineage) |
| INV-6 | Regime change / overfitting / curve-fitting | **B** (시행 횟수 추적 = 프로세스 invariant, 단일 산출물 정적 검사 불가) | opus 필수 (통계 일반화·표본 충분성) |
| INV-7 | Order fill 가정 (가격·시점·가능성) | **A** (fill 규칙 = 정적 코드 패턴) + INV-1 강결합 | opus 필수 (시장 미시구조 + INV-1/8 결합) |
| INV-8 | Capacity / market impact / liquidity | **A**(impact 모델 존재) + **B**(자산별 유동성 데이터 의존) 혼합 | opus 필수 (impact 강도 = 자산별 유동성 도메인) |
| INV-9 | 시간 경계 (funding/borrow, timezone, 거래시간) | **A**(timezone 정규화 정적) + **B**(funding·점검 캘린더 메타데이터) 혼합 | opus(funding·점검 정책) / sonnet(UTC 정합) 2-층 |
| INV-10 | **Storytelling / narrative-fit** (F2 편입 — 7 Sins #3) | **B** (사후 서사 적합 = 방법론 메타, 정적 falsify 불가) | opus 필수 (가설 사전성·data-snooping 도메인) |
| INV-11 | **Outliers / 비정상값 처리** (F2 편입 — 7 Sins #6) | **A**(outlier 처리 규칙 정적) + **B**(극단치 정당성 도메인) 혼합 | opus(처리 정책 타당성) / sonnet(규칙 적용 검증) 2-층 |

**F1 정정 (확정)**: INV-2 survivorship 의 mutual-fund 정량 anchor = **Elton-Gruber-Blake(1996) 1.4%/년**(요구사항리뷰 dual-peer + PL 다출처 교차 = Oxford Academic *Review of Financial Studies* 9:4:1097 수렴, "확인 완료"). 요구사항 §6.3 Gap1 의 "0.9%" 단일 약출처(susanpotter.net)는 사실 오류로 기각. (단 survivorship 1-4%/Sharpe 0.09→0.66/PIT 1.5-2.0% 는 별도 출처로 grounding — F1 은 load-bearing 아님.)

**F2 정정 (편입 + traceability)**: catalog 가 자기 인용 backbone "7 Sins of Quantitative Investing"(survivorship / look-ahead / **storytelling** / overfitting·data-snooping / turnover·transaction-cost / **outliers** / asymmetric-shorting-cost) 중 storytelling·outliers 2종 미수록 → **INV-10(storytelling) / INV-11(outliers) 편입**. 잔여 7 Sins 항목 traceability: survivorship=INV-2 / look-ahead=INV-1 / overfitting=INV-6 / transaction-cost=INV-3 / asymmetric-shorting=INV-9(borrow 비용)·INV-3 분산. **의도적 제외 0** — 7 Sins backbone 전부 1:1 매핑.

**A/B 분류 의의 (F3 / OQ-4)**: 부류 **A(정적 falsifiable)** = lookahead 코드 패턴·fee 누락·PnL 산술처럼 단일 산출물 정적 검사로 falsify 가능. 부류 **B(프로세스·메타데이터 의존)** = PIT governance·시행 횟수·survivorship 완전성·storytelling 처럼 시점 메타데이터·프로세스 추적 없이 정적 falsify 불가. **financial-invariant-0 shape predicate 자체는 A-side 메커니즘**(Story 메타·경로로 결정론적 판정 — §결정 1) 이나, invariant *식별/검증*은 A+B 전부를 cover(opus 도메인 판단). 둘은 disjoint — shape 판정(A-side)이 sonnet 가능 여부를 가르고, 가른 후 sonnet 이 cover 하는 mandate 표면은 financial-invariant-0 에선 0(결과 비접촉).

**정식 catalog 파일** = `docs/domain-knowledge/domain/backtesting-discipline/financial-correctness-invariant-catalog.md`(Phase 2 산출, DomainAgent write 권한 경로 — concept/** deny 라 domain/ 만 가능, OQ-7). 본 Amendment = 구조·분류·shape 매핑 확정.

### D2 — financial-invariant-0 shape (stakes 4-AND 와 orthogonal 한 별 축, OQ-1/OQ-5)

**판정 원리**: invariant 표면이 0 이려면 그 작업이 **백테스트 결과 숫자(equity/체결/PnL/universe/파라미터)를 생성·변형·해석하지 않아야** 한다. invariant 는 "결과 정확성"의 속성이므로 결과 비접촉 작업엔 표면이 없다. InfraOpArch §7.4 가 live 부재 shape 에서 *dormant* 인 패턴과 **동형**이되, dormant(발현 trigger 부재)가 아닌 **"결과 비접촉으로 mandate 표면 0"** 논리.

**orthogonal 축 확정 (OQ-1)**: financial-invariant-0 은 Amendment 16 의 stakes 4-AND(실자금/cutover/신규경계/live API = *stakes·safety* 축, InfraOpArch §7.4 mandate 를 끔)와 **다른 축** — *financial-correctness 결과 접촉* 축(DomainAgent financial mandate 를 끔). 두 predicate 가 끄는 mandate 표면이 다르므로 4-AND 에 5번째로 욱여넣지 않고 **DomainAgent 전용 별 predicate** 로 명시 분리. DomainAgent sonnet flip 조건 = **(4-AND low-stakes) AND (financial-invariant-0 shape)** — 2 predicate AND. 4-AND 가 false 면(live API/실자금 등) financial-invariant-0 여부와 무관하게 opus(stakes-gated 보존). 4-AND 가 true 여도 financial-invariant-0 가 false 면(결과 접촉) opus(financial mandate 살아있음).

**falsifiable 신호 (5-AND — 모두 참이어야 financial-invariant-0, OQ-5 = 영향(행위) 기준)**:

| # | 신호 | 차단 invariant |
|---|---|---|
| 1 | **결과-숫자 비접촉** — equity/PnL/position/체결가/universe/파라미터 생성·변형 안 함 | INV-3/4/7/8/10/11 |
| 2 | **시간-인과 비접촉** — 시계열 시점 정렬·join·window·리샘플 미접촉 | INV-1/5 |
| 3 | **체결/비용 모델 비접촉** — fee·slippage·fill·funding 로직 미변경 | INV-3/7/9 |
| 4 | **data lineage 비접촉** — 데이터 출처·정정·universe 구성 미변경 | INV-2/5 |
| 5 | **(보조) 변경 경로** — 도메인 숫자 repo(`-engine`/`-data`/strategy) 밖 (순수 렌더·infra·tooling·문서) | — (allow-list) |

전부 **fail-safe** — 불충족·불확실 = opus(INV-1 동형, fail-safe monotone). **판정 축 = 영향(행위) 기준 — 코드 위치 아님**(OQ-5 확정): 같은 파일이라도 financial 의미(예: UI 문구 "estimated PnL"→"realized PnL")를 건드리면 shape 0 탈락. 신호 5(경로)는 보조 allow-list 일 뿐 단독 판정 아님 — 신호 1~4(영향) 가 1차.

> **자료 출처 grounding**: 5-AND·A/B 분류·9→11 invariant 는 요구사항 §6 Researcher 14 출처(López de Prado & Bailey *Deflated Sharpe Ratio* / *Probability of Backtest Overfitting* 학술 1차 2종 + 7 Sins of Quantitative Investing 업계 표준 + CFA Level 2 + survivorship 정량 vendor 실측)로 cited grounding 완료, 요구사항리뷰 lane 외부사실 게이트 PASS(silently ungrounded 외부단정 0). 설계 lane 추가 외부 검증 불요(ADR-119 — 요구사항 §6 cited 재사용).

### §결정 2 invariant 동반 의무 — DomainAgent mandate 표면 재정의

model 필드만 조건부 처리 = §결정 2 위반(Amd16 §D2 verbatim "invariant 위반이 되는 유일한 경로 = shape 분류만 하고 mandate 표면 재정의를 동반 안 할 때"). 따라서 DomainAgent.md mandate 에 **"financial-invariant-0 shape 에서 DomainAgent 책임 표면이 무엇인가"** 를 명시 declare(Phase 2 agent file). shape별 mandate 표면:

| shape | DomainAgent financial mandate 표면 | sonnet cover |
|---|---|---|
| **financial-invariant-0** (결과 비접촉: 순수 UI 렌더/infra lib/tooling/문서) | financial invariant 해석 표면 = **0** — catalog 등재 항목 읽기·링크·분류만, 새 invariant 생성·financial rule 참/거짓 미결정 | ✅ sonnet (single-axis 분류 advocacy 깊이로 cover) |
| **financial-invariant 보유** (데이터 파이프라인 / 백테스트 엔진 / 전략·지표) | 전체 financial invariant 해석 표면 (INV-1~11 식별·정의·엣지·data lineage 판단) | — (opus 보존 — financial-invariant-0 predicate false) |

**"완전 N/A" 아닌 표면 축소** — financial-invariant-0 shape 에서도 DomainAgent 의 *일반* 도메인 해석(비-financial Entity/제약/용어)은 잔존하되, financial-correctness invariant 해석 표면만 0. 순수 model downgrade 시 도메인 invariant 해석 부재 → 얕은 single-axis advocacy 로 새는 risk 를 mandate 재정의가 차단. **선례** = CodebaseMapper/Refactor(ADR-057 Amd5 mandate text 재정의 동시 산출물 의무) + InfraOpArch(Amd16 "low-stakes shape 표면" subsection) 답습.

### §결정 3 — spawn 시점 = spawn-전 외부 shape 판정 (OQ-3)

DomainAgent 는 **요구사항 lane spawn**(InfraOpArch = 설계 lane spawn). InfraOpArch 의 self-assessment 패턴(spawn 후 mandate 권위로 §7.4 dormant verify)은 DomainAgent 에 **부적합** — DomainAgent 해석 mandate 는 shape 무관하게 상존이라 "spawn 후 self-assess 로 표면 0 declare" 가 안 맞는다(상존 mandate 를 self 가 0 으로 declare 하면 self-referential paradox). 따라서 **spawn-전 외부 shape 판정** — Orchestrator 가 Story 메타(§1 원문·§4.1 변경 델타 경로·AC 키워드)로 financial-invariant-0 5-AND 를 spawn *전*에 판정한 뒤 그 결과로 opts.model 결정. self-assessment 가 아닌 external gating(InfraOpArch 의 spawn-time gating 과 동일 구조이나, InfraOpArch 는 spawn-후 self-assess 도 보조로 가능한 반면 DomainAgent 는 external 단독).

**self-referential 판정 risk 완화 (OQ-2)**: "이 Story 가 financial domain 비접촉인가" 판정에 도메인 지식이 필요(닭과 달걀). 해소 = **allow-list**(순수 tooling/UI/infra lib/문서 = 결과 비접촉 negative-list 로 codify, 그 외 전부 opus) + **fail-safe**(불확실=opus). "순수 tooling 판정"이 한 단계 뒤로 밀릴 뿐 완전 제거는 아님 — 잔존 risk 는 F1 evidence-gate(sonnet 산출물 품질 ≥ opus baseline) 가 흡수.

### §결정 4 — 메커니즘 신설 0 (Amendment 16 재사용)

- **frontmatter `model: opus` 보존** = fail-safe default(override 누락 = opus). 영구 정책 주석으로 conditional 표기(InfraOpArch.md 선례 패턴).
- **Orchestrator spawn-time `opts.model: sonnet` override** = (4-AND low-stakes) AND (financial-invariant-0 shape) 동시 충족 시만. **fresh `Agent` spawn 필수 — SendMessage resume 금지**(원본 frontmatter `model: opus` 재해석 → override 무효, ADR-057 §결정 4 / CFP-2236 실측). FIX 재진입도 fresh spawn 으로 shape 재판정(silent 풀림 차단).
- **gating predicate 확장** = `scripts/check-stakes-tier-gating.sh` 에 `STAKES_FINANCIAL_INVARIANT_ZERO`(별 predicate) + DomainAgent 분기 추가(`STAKES_AGENT=DomainAgent` 시 4-AND ∧ financial-invariant-0 양 predicate AND). 별 스크립트 신설 아닌 기존 스크립트 확장(메커니즘 신설 0). **fail-safe 동형** — financial-invariant-0 신호 부재/파싱불가 → high(opus), INV-1 monotone 정합.
- **consumer overlay** = 확장-only(opus 강제만, down-tier 불가) + `max(floor,overlay)` clamp 재사용(ADR-127 §결정 6). DomainAgent down-tier(opus→sonnet) 공격적 override 불가.

### F1 evidence-gate — DomainAgent baseline 신규 정의 (OQ-6)

tier-flip = **provisional**. CFP-2432 F1 protocol(`docs/domain-knowledge/concept/stakes-gated-model-tier-baseline.md`) 을 DomainAgent 에 동형 적용하되, **baseline 측정 대상이 다름** — InfraOpArch 는 "§7.4 운영 리스크 표 완결성(§7.4.1~.6 충족 행 수)" 이나 DomainAgent 는 **"도메인 invariant 식별 완결성"**:

| step | DomainAgent 측정 정의 (정량 — 주관 어휘 금지) |
|---|---|
| (a) 측정 대상 | financial-invariant-0 shape Story 에서 DomainAgent 산출의 (catalog cross-ref 항목 수 + 도메인 제약·암묵 가정·지식 공백 식별 행 수) 정수 |
| (b) opus baseline 캡처 | 1차 = Codex 독립 review verdict(ADR-057 §결정 3 선례). 2차 = 동일 Story 양 tier(opus/sonnet) 대조 spawn(packet 고정) 후 (a) 정량 비교 |
| (c) "미달" 임계 (OR — falsifiable) | ① catalog cross-ref 누락 ≥ 1(opus 가 인용했는데 sonnet 이 누락) **OR** ② Codex review P0/P1 finding ≥ 1 **OR** ③ sonnet 식별 항목 수 < opus × tolerance(초기 1.0) |
| (d) 복원 trigger | (c) 1개라도 해당 시 DomainAgent opus 복원(opts.model 제거) + sonnet 채택 시 commit/PR body `financial-invariant-zero-evidence:` marker 의무(부재 시 FAIL — `check-tier-downgrade-guard.sh` 동형) |

복원 = 정책 철회 아닌 해당 shape/agent tier-flip 만 되돌림. **indirect real-funds risk 가드** — 누설 = 백테스트 결과 거짓→실자금 결정 오염이므로 fail-safe(불확실=opus) + 5-AND 전부 충족 요구 + evidence-gate 3중.

### OQ-7 / OQ-8 — catalog 위치 + ADR-117 cross-ref

- **OQ-7 (catalog 위치)**: `docs/domain-knowledge/domain/backtesting-discipline/financial-correctness-invariant-catalog.md`. area 명 = `backtesting-discipline`(invariant 이 백테스트 방법론 규율이라는 본질 반영, `financial-correctness` 후보보다 도메인 적합). DomainAgent write 권한 = `docs/domain-knowledge/domain/**` 만(concept/** = ResearcherAgent deny, ADR-056) → domain/ 만 가능.
- **OQ-8 (ADR-117 cross-ref)**: **ADR-042 Amd17 내 언급으로 충족, ADR-117 본체 미수정**. ADR-117 §결정 2 가 "Domain = 단기 구조적 역할" 로 **fable 상향**에서 명시 제외했으나, 그 단정 대상은 fable 적격성(상향 축)뿐 — opus floor 적정성(하향 sonnet 축)을 단정한 적 없음(ADR-117 전문 sonnet 하향 논의 0건). 두 ADR 이 같은 agent(DomainAgent)를 분류하므로 본 Amendment 가 **판정 축 disjoint(상향 fable vs 하향 sonnet) + "Domain opus 유지" 문구가 stakes-conditional(financial-invariant-0) 로 정제됨** 을 명시(Amd16 §결정 3 cross-ref 의무 실행). silent override 금지. ADR-117 본체에 현재 DomainAgent·financial 언급 0 → 별 amendment row 불요.

### 기존 정책 변경 0건 (ADR-042 본문 결정 1~6)

본 Amendment 17 = ADR-042 결정 1~6 본문 **변경 0건**. 변경 = (a) §결정 1 Sonnet 표 후 inline marker(Amendment 17 발화) + Amendment 16 §결정 3 body 후 fulfillment marker (b) 본 `## Amendment 17` body section (c) frontmatter amendment_log row 17 + related_stories CFP-2445 + related_adrs ADR-056 append. tier criteria(결정 1) — DomainAgent 의 (c)high-stakes domain 기준의 *financial-invariant-0 shape 조건부 발화 명시*이지 기준 자체 변경 아님. invariant(결정 2) — financial-invariant-0 = mandate-orthogonal 축 논증으로 양립 확인 + mandate 표면 재정의 동반 의무, invariant 텍스트 변경 0. 신규 agent ADR 의무(결정 3) / inheritance(결정 4) / Haiku rollback(결정 5) / 재-audit(결정 6) 모두 변경 0건. **§결정 6 미발동** — DomainAgent mandate 를 "패턴 실행" 방향으로 재정의하지 않음(financial-invariant-0 shape 표면 축소는 single-axis advocacy 정합이지 mechanical pattern 전환 아님).

### ratchet 방향 — 약화(evidence-gate)

opus→sonnet tier-flip(DomainAgent, financial-invariant-0 shape 한정) = ratchet **약화 방향** → `sunset_justification` evidence 의무(ADR-058 §결정 5 / ADR-064 §결정 7). frontmatter amendment_id:17 `sunset_justification` 본문 = evidence-grounded 3 axis(shape-gated 정제 / falsifiable evidence-gate + indirect real-funds risk 가드 / 지배 financial-invariant-0 shape 비용효율). is_transitional: false 유지(영구 정책 정제 — Amd16 동형).

### 발효 timing — 비준(declarative) ≠ 즉시 런타임 적용(enforcement)

본 Amendment 17 `status: applied` = **정책 비준(declarative ratification)** 이지 즉시 런타임 발효 아님. **Phase 1(본 Amendment) = 정책 비준** — financial-invariant-0 shape 정의 + 5-AND predicate + catalog 구조·A/B 분류·shape 매핑 + tier-flip 대상(DomainAgent) 확정. **실 발효(enforcement) = Phase 2 guardrail 완비 시점** — (a) catalog 파일 신규(DomainAgent write) + (b) DomainAgent.md frontmatter conditional 주석 + mandate 표면 재정의 + (c) `check-stakes-tier-gating.sh` predicate 확장 + (d) project-config-schema + playbook §3.0.12a 배선 + (e) F1 protocol DomainAgent 확장 + (f) `financial-invariant-zero-evidence:` marker gate 가 모두 갖춰져야 실제 override 발화. guardrail 완비 전까지 frontmatter `model: opus` fail-safe default 유지 → 현행 opus 동작 무변경(파괴적 변경 0). 선례 = Amd16 비준↔발효 split + Amendment 13→14 declarative→mechanical split 동형.

### Scope 경계 (Phase 1 / Phase 2)

- **Phase 1 (본 산출물)**: ADR-042 Amendment 17(frontmatter + inline marker + Amd16 fulfillment marker + body) + change-plan(internal-docs) + Story §7 설계 서사.
- **Phase 2 (sibling PR)**: `docs/domain-knowledge/domain/backtesting-discipline/financial-correctness-invariant-catalog.md` 신규(9→11 invariant, F1 1.4% 정정, A/B 분류 — DomainAgent write) + `DomainAgent.md` frontmatter conditional 주석 + mandate 표면 재정의(financial-invariant-0 shape 책임 축소 declare) + `scripts/check-stakes-tier-gating.sh` `STAKES_FINANCIAL_INVARIANT_ZERO` predicate + DomainAgent 분기 확장 + `tests/scripts/test-check-stakes-tier-gating.sh` DomainAgent truth-table 행(discriminating) + `docs/project-config-schema.md` DomainAgent gating 항목 + `docs/orchestrator-playbook.md` §3.0.12a DomainAgent 분기 + spawn-전 외부 shape 판정 절차 + `stakes-gated-model-tier-baseline.md` F1 protocol DomainAgent baseline 확장 + plugin bump(codeforge-requirements MINOR — mandate 표면 재정의, wrapper MINOR — scripts/schema consumer-facing surface, ADR-037) + marketplace sync(ADR-063).

### Cross-ref

- ADR-042 Amendment 16(CFP-2432) — §결정 3 가 본 Story 예약(catalog codify + 경계 falsifiable 확정 후 별 carrier). Amd17 = 선결충족 확장(reversal 아님, 무효화 0). 메커니즘(opts.model override / 4-AND / F1 protocol / consumer overlay 확장-only) 전부 재사용 — 신설 0
- ADR-058 §결정 5 — 약화 방향 sunset_justification evidence requirement(DomainAgent tier-flip 하향 evidence-gate)
- ADR-064 §결정 7 — is_transitional:false governance ADR 약화 symmetric evidence-gate
- ADR-117 §결정 2 — Domain "단기 구조적" fable 상향 제외 = 상향 축. 본 Amendment = 하향(sonnet) 축 disjoint, silent override 금지(Amd16 §결정 3 cross-ref 의무 실행, ADR-117 본체 미수정 — Amd17 내 언급 충족)
- ADR-057 §결정 3(Codex 독립 review baseline 선례 — F1 measurement) / §결정 4(spawn-time opts.model override fresh-spawn 메커니즘, SendMessage resume 금지 상속)
- ADR-127 §결정 6 — consumer overlay 확장-only(DomainAgent down-tier 공격적 override 불가)
- ADR-056 §결정 3 — 요구사항 lane synthesis 순서(catalog 합성 근거) + DomainAgent write 권한 경로 docs/domain-knowledge/domain/**(concept/** deny)
- ADR-086 — axis 분석 lens(financial-invariant-0 axis ⊥ stakes axis ⊥ mandate depth axis disjoint 검증 adjacent-case. 본 Amendment = 신설 아닌 tier 분기 → framework 전면 self-application 주장 아님)
- CFP-2445 change-plan(internal-docs `wrapper/change-plans/`) — financial-invariant-0 gating 설계 SSOT(§3 메커니즘 / §7 trust boundary / §8 Test Contract / §11 N/A)

---

## Amendment 18 — RefactorAgent (d) Reusability 측정 축 소관 이동(구현 리팩터링 Story C) + repo-분해 구조 escalation 존치 (Amendment 13/14 partial re-framing, ADR-058 §결정 5 evidence-gate, CFP-2539 / Epic CFP-2533 Story B)

**날짜**: 2026-07-01

### 동기 (리팩터링 2활동 분리 — Epic CFP-2533 도메인 이분)

Epic CFP-2533 (리팩터링 2활동 분리 — 설계 리팩터링 + 구현 리팩터링) 의 도메인 이분:

| | 설계 리팩터링 | 구현 리팩터링 |
|---|---|---|
| 대상 | 결합도·인터페이스·**경계**·패턴 = **구조** | 중복 제거·공통 추출·재사용 = **reusability 측정** |
| 관측 시점 | 코드 존재 전 (설계 스케치만으로 위반 판단 가능) | 실코드 위 (중복은 코드가 있어야 관측) |
| RefactorAgent 축 | (a)decoupling / (b)pattern / (c)interface separation **+ repo-분해(구조 escalation)** | (d) reusability **측정** |
| 발동 메커니즘 | 설계 lane inline advocacy (Claude, Mapper↔Refactor 대립) | Epic-close triage — Codex↔Claude execute-and-falsify (Story C) |

Amendment 13 (CFP-2364) 가 (d) Reusability 를 RefactorAgent 1급 축으로 신설했고 Amendment 14 (CFP-2369) 가 측정을 mechanical wire 했다. 본 Amendment 18 = 그 (d)를 **관측 시점 기준으로 두 sub-part 로 분할**한다:

1. **중복제거·공통추출·DRY/WET·rule-of-three·duplication-ratio 측정** = **실코드 관측 의존** (중복은 실코드 없이 선험적으로 존재 불가 — Story §2.1 도메인 근거) → RefactorAgent 설계-lane mandate 에서 **out-of-mandate + 구현 리팩터링(Story C) in-scope** 로 re-frame. 이것이 Epic 의 핵심 thesis (중복은 코드가 생겨야 관측 + Codex 실측 가능).
2. **repo-level 분해 advocacy** (응집 cluster → 별 deploy/ownership 단위 분리 = macro-structural boundary) = **설계-시점 관측 가능** (설계 스케치 macro-boundary 에서 판단 — 런타임 중복 관측 불요) → RefactorAgent **설계-시점 구조 escalation 축으로 존치** (advocacy/제안만; 경계 확정 = ArchitectAgent chief authority, RefactorAgent.md:33 기 anchor).

순 결과: **RefactorAgent = (a)decoupling / (b)pattern / (c)interface separation 구조 3축 + repo-level 분해 구조 escalation(설계-시점)**. REMOVED = 중복/재사용 *측정* 축(duplication-ratio / clone / rule-of-three / DRY-as-duplication / 공통추출) only.

### 변경 사항 (mandate 축소 — 측정 축 relocation, repo-분해 존치)

| Agent | 변경 | model tier | §결정 1 매트릭스 row |
|---|---|---|---|
| **RefactorAgent** | **mandate 축소** — (d) reusability *측정* 축(중복제거·공통추출·DRY/WET·rule-of-three·duplication-ratio) out-of-mandate → 구현 리팩터링(Story C) 이관. (a)decoupling / (b)pattern / (c)interface separation **구조 3축 유지** + repo-level 분해 **구조 escalation 존치**(advocacy) | **Sonnet 유지** | (a) 무변경 — single-mandate advocacy 패턴 유지 (구조 advocacy 축, multi-source synthesis 는 ArchitectAgent chief Opus) |

roster 6 permanent + 3+1 CONDITIONAL + 3 sub-tuple 카운트 무변경 (RefactorAgent 존속 — mandate 발화 범위만 축소). model tier Sonnet 무변경. spawn 메커니즘 무변경.

### Amendment 13/14 carry-over re-framing (본문 0 touch — Event Sourcing)

**Amendment 13/14 body section (본 ADR L893-1034) = frozen audit trail, 0 touch.** 본 Amendment 18 = 폐지(무효화)가 아니라 소관 **re-framing** (Amendment 10 CFP-1126 partial-rollback + carry-over 선례 답습):

- Amendment 13 L50 anchor "(d) in-scope, 금지 영역 아님" → 본 Amendment 18 에서 "**RefactorAgent 측정 축 out-of-mandate + 구현 리팩터링(Story C) in-scope; repo-분해 구조 escalation 존치**" 로 carry-over re-frame (삭제 아님 — Amendment 10 이 AggregateArch mandate 를 ModuleArch 로 carry-over 한 것과 동형).
- Amendment 14 mechanical wire 5파일 (`check-duplication-ratio.sh` / `test-...sh` / `duplication-check.yml` / evidence-registry `duplication-ratio-warning` entry / invariant-check.yml `CONSUMER_ONLY_WORKFLOWS`) = **존치** (warning-tier, 항상 exit 0 — advocacy owner 부재 상태로 남아도 orphan-safe, CI 무해). 생애주기 결정(존폐/이동) = Story C. RefactorAgent.md "재사용성 측정 연동" 단락은 "구현 리팩터링(Story C) 이관" anchor 로만 정리.
- Amendment 14 deferred trigger("duplication-ratio blocking 승격 = evidence 누적 후 별 CFP") = owner_adr ADR-060/ADR-042 governed **유지** — RefactorAgent-advocacy driver 만 Story C triage context 로 relocate (deferred 자체는 orphan 되지 않음).

### ADR-058 §결정 5 evidence-gate (약화 방향 — 측정 축 국소 4→3 축소)

측정 축 소관 이동 = RefactorAgent 국소로 4축→3축 mandate 축소(약화 방향) → ADR-058 §결정 5 / ADR-064 §결정 7 (is_transitional:false governance ADR 약화 방향 symmetric evidence-gate) evidence requirement 발화. frontmatter amendment_id:18 `sunset_justification` 본문 = evidence-grounded 3 axis (요약 아래, verbatim = frontmatter):

**(a) 환경 변화 evidence (relocation-강화, flat 능력 감소 아님)**: 측정 축을 강제력 없는 설계-시점 warning 에서 실코드 관측 시점(구현-후)의 execute-and-falsify 로 이동. net-strengthening 을 만드는 환경 변화 = **CFP-2476 (Epic Codex 실행기반 검증 확장) infrastructure 가 이제 EXISTS** `[verified: gh issue view 2476 --repo mclayer/plugin-codeforge → state=CLOSED, title "[CFP][EPIC] Codex 실행기반 검증 확장 — 실행형 재리뷰 + 주장→증거 감사 + 정책게이트 팩"]`. 중복/재사용 측정이 실코드 위에서 Codex 가 실측·반증(execute-and-falsify) 가능한 시점(Epic-close triage) 에 배치될 때 강제력이 설계-시점 declarative advocacy 보다 net ↑. Story A (debate-protocol-v1 v1.3, `blanket_refactor` dispatch, merged) 가 enabling contract.

**(b) eval/directive evidence (강제력 비대칭 + 도메인 관측 한계)**: Epic CFP-2533 problem statement = "설계 시점 advocacy 로는 중복/재사용 관측 한계 (코드가 생겨야 진짜가 보이고 Codex 가 실측 가능)" + 강제력 비대칭 실측 — Amendment 14 `check-duplication-ratio.sh` 는 always exit 0 (warning-tier, 비차단) 인 반면 impl-manifest-mismatch 등은 P1 blocking `[verified: scripts/check-duplication-ratio.sh 모든 경로 exit 0 — Amendment 14 §warning-tier 불변]`. 설계-시점 측정 축이 warning-tier 로 강제력 결여인 채 남는 것보다 구현-후 execute-and-falsify triage 로 이동이 강제력 net 개선. **pattern_count 는 별도 catalog 부재 — eval/directive evidence 로 정직 framing (pattern_count 날조 금지 — ADR-119 정합).**

**(c) observation-time sufficiency (측정 축의 올바른 관측 시점 배치 = single-axis analog)**: 측정 축은 "중복은 실코드 없이 선험적으로 존재 불가"(Story §2.1) 라 설계-시점 falsifiable 계측 물리 불가 — 올바른 관측 시점(구현-후)으로 배치될 때만 falsifiable. repo-분해 축은 macro-boundary 로 설계 스케치에서 관측 가능 → RefactorAgent 설계-시점 존치가 정합 (관측 시점 disjoint). 국소 4→3(측정 축) 축소 ↔ policy-level elevation(설계-시점 warning → 구현-후 execute-and-falsify) trade-off 의 **net 은 강화** (Story §4.2 relocation-강화 framing).

is_transitional: false 유지 (영구 정책 정제 — 소관 이동은 영구 재배치, transitional pilot 아님. Amendment 10 동형).

### ADR-086 framework 적용 — FULL self-application (축소 = explicit scope 열거)

**Amendment 13 과의 대조 (중요)**: Amendment 13 은 **mandate 확장** — ADR-086 explicit scope(신설/미도입/rename/축소, [L56 verbatim](ADR-086-deputy-creation-decision-framework.md)) 에 확장 미열거 → **adjacent-case** (axis 분석 lens 도구만 차용). 본 Amendment 18 은 **mandate 축소** — ADR-086 explicit scope 에 "**축소**" 명시 열거 → **FULL governance self-application** (5-checklist 완주 의무). 아래 5-checklist = full self-application:

| # | Check | 통과 기준 | CFP-2539 full self-application (측정 축 축소 + repo-분해 존치) |
|---|---|---|---|
| 1 | **axis disjoint** | 축소가 잔여 deputy/축과 axis 중복·충돌 0 | **PASS** — 측정 축 relocation(중복/재사용 실코드 관측) ⊥ 잔여 구조 3축(결합/패턴/인터페이스 설계-시점) ⊥ repo-분해 구조 escalation(macro-boundary 설계-시점). 세 축 관측 시점·대상 disjoint. ModuleArch(boundary authority) / DataArch(OLAP de-duplication) 무영향. |
| 2 | **cost-token budget** | spawn count 변화 시 ADR-068 I-5 empirical grounding | **PASS (marginal 감소)** — roster 무변경(신설/deprecate 0), spawn count 무변경 (평균 26 / full 38 유지, Amendment 10 base `[empirical-source: TBD — local probe 부재]`). 축소 token = RefactorAgent output 슬롯 (d) 측정 축 1개 제거분 (4→3, marginal 감소). |
| 3 | **consumer carrier** | consumer overlay 필드 / `project.yaml` schema 영향 명시 | **PASS (신규 schema key 0)** — duplication 측정 owner → Story C Epic-close triage context 로 relocate. Amendment 14 mechanical wire 5파일(consumer template `duplication-check.yml` 포함) = 존치(warning-tier, orphan-safe) — consumer 측 삭제/schema 변경 0. 신규 `project.yaml` key 신설 0. |
| 4 | **sibling Epic align** | 진행 중 sibling Epic 과 RACI 충돌 0 또는 cross-ref | **PASS** — 수령처 = Epic CFP-2533 Story C (측정 축 실배선 — role_assignment / blanket_refactor 실소비 / Epic-close triage). cross-ref 명시. Story A(debate-protocol v1.3, merged) 무의존. RACI 충돌 0. |
| 5 | **deferred trigger 명시** | 후속 carrier 별 CFP 명시 | **PASS** — Story C = 측정 축 mechanical wire 실배선 carrier (check-duplication-ratio.sh 등 5파일 생애주기 결정 + Epic-close triage 배선). Amendment 14 blocking-승격 deferred(evidence 누적 후 별 CFP) = ADR-060/ADR-042 governed 유지. |

종합: **mandate 축소 — FULL self-application PASS** (5-checklist 1 FAIL 0). ADR-086 explicit scope("축소") 열거 대상이므로 framework 전면 self-application (Amendment 13 adjacent-case 와 대조). verdict packet `deputy_axis_restructure_self_check_passed: true` (ADR-086 §결정 4).

### ADR-131 무영향 — Amendment 2 불요 (repo-분해 존치가 '무축소' premise 보존)

**핵심 blast-radius 판정**: ADR-131 (cross-repo 책임 배치 거버넌스, status: Proposed, is_transitional: false — LIVE governance decision) 은 L85 / L144 / L146-150 / L230 에서 RefactorAgent 를 참조하나, **참조 대상 = RefactorAgent 의 *repo-분해 advocacy*(escalation-tier 제안) 이지 *reusability 측정* 축이 아니다** `[verified: Read ADR-131 L85 "repo-분해 pressure 식별·제안(escalation-tier), 경계 확정은 disjoint" / L146-150 axis-disjoint #2 "RefactorAgent advisory 무축소 (verbatim 박제 — AC-5) ... RefactorAgent.md:46 ... 이 한 줄 없으면 구현리뷰가 mandate 축소로 오판한다"]`.

본 Amendment 18 이 **repo-분해 구조 escalation 축을 RefactorAgent 에 존치**하므로:
- ADR-131 L150 "RefactorAgent advisory 무축소" premise = **TRUE 유지** (repo-분해 advocacy 무손상).
- ADR-131 L144 axis-disjoint("repo-level 소유 배치 ⊥ ModuleArch 레포 내부 ⊥ RefactorAgent repo-분해 advocacy") = 3축 그대로 유효.
- → **ADR-131 Amendment 2 불요** (blast radius 최소, live Proposed ADR falsification 0).

**대안 Option Y (reject)**: (d) 전체(repo-분해 포함) 이관 시 ADR-131 L150 을 re-point 하는 **ADR-131 Amendment 2 필수** — Story §2.1 자체 도메인 기준(repo-분해 = 설계-시점, 런타임 미관측) 위배 + live Proposed ADR 불필요 amend → reject. 상세 = change-plan §2 "설계 fork 판정".

### SSOT propagation (3 원본)

본 Amendment 의 RefactorAgent mandate 서술은 Amendment 13 확립 3 원본에 byte-consistent 의미로 sync (Phase 2 sibling PR):

1. `plugins/codeforge-design/agents/RefactorAgent.md` — agent file SSOT (측정 축 제거 + repo-분해 구조 escalation 존치 + "구현 리팩터링(Story C) 이관" anchor)
2. `skills/deputy-mandate/SKILL.md` — wrapper canonical SSOT (primary axis matrix / DDD pattern / axis disjoint 단락)
3. `plugins/codeforge-design/CLAUDE.md` — mirror (sibling sync)

### bump + marketplace sync

- `plugins/codeforge-design/.claude-plugin/plugin.json`: version **0.30.0 → 0.31.0 MINOR** (RefactorAgent agent surface 축소 — ADR-037 plugin version bump rule; `mandate scope 변경` = MINOR trigger). 참고: Story §5 AC-8 의 "0.29.0 → 0.30.0" 은 stale baseline — CFP-2505 (2026-06-30) 가 이미 0.30.0 으로 bump `[verified: gh api .../codeforge-design/.claude-plugin/plugin.json?ref=main → version 0.30.0]`. 정정 target = 0.30.0 → 0.31.0.
- marketplace version sync (ADR-063 atomic invariant) — `mclayer/marketplace` codeforge-design entry version mirror (현재 main 에서 0.30.0 sync 상태 `[verified: gh api .../marketplace.json?ref=main]` → **fresh sync PR 로 0.31.0**, sync PR 선행 merge → plugin PR merge).
- plugin.json changelog: CFP-2539 entry **prepend** — 기존 CFP-2505/2369/2364 changelog 항 = frozen (0 touch).

### 외부 지식 인용 (Amendment 13 근거 재인용 — over-claim 무)

Story §2.1 시점-분리 도메인 근거의 외부 실천 근거 (Amendment 13 이 이미 인용한 근거의 재인용 — 신규 1차 출처 발굴 불요, requirements-review 확인: over-claim 무):

- **rule of three / DRY (중복은 실코드 3회 관측 후 추출 = 구현-시점 리팩터링)**: Martin Fowler, *Refactoring* (Extract Method / Extract Class 중복 제거 catalog; "rule of three" — Don Roberts 귀속). source: en.wikipedia.org/wiki/Rule_of_three_(computer_programming). "3회 관측 후 추출, premature abstraction 회피" = 측정 축이 구현-시점 성격이라는 근거.
- **ISO/IEC 25010 Maintainability sub-characteristics (Modularity ↔ Reusability 별 축)**: Modularity(=decoupling/pattern/interface = 구조 3축) 와 Reusability(=측정 축) 가 별 sub-characteristic. source: ISO/IEC 25010:2023(en) Product quality model (https://www.iso.org/obp/ui/en/#!iso:std:78176:en).

### 기존 정책 변경 0건 (ADR-042 본문 결정 1~6)

본 Amendment 18 = ADR-042 결정 1~6 본문 **변경 0건**. 변경 = (a) frontmatter amendment_log row 18 신설 + related_stories CFP-2539 append (b) 본 `## Amendment 18` body section. tier criteria(결정 1) — RefactorAgent Sonnet 분류 무변경(mandate scope 축소이지 tier 변경 아님). invariant(결정 2) — Sonnet single-mandate advocacy 패턴 유지, mandate 표면 재정의 동반(측정 축 out-of-mandate declare — 순수 축소 아닌 소관 명시). 신규 agent ADR 의무(결정 3) / inheritance(결정 4) / Haiku rollback(결정 5) / 재-audit(결정 6) 모두 변경 0건.

### Cross-ref

- [Amendment 13 (CFP-2364)](#amendment-13) — (d) Reusability 1급 축 신설. 본 Amendment 18 = 측정 축(→Story C) + repo-분해 구조 escalation(존치) 분할 re-frame. 본문 0 touch, L50 anchor re-framing only
- [Amendment 14 (CFP-2369)](#amendment-14) — (d) 측정 mechanical wire. 도구 5파일 존치(warning-tier orphan-safe), advocacy driver 만 Story C relocate. deferred blocking-승격 = ADR-060/ADR-042 governed 유지
- [Amendment 10 (CFP-1126)](#amendment-10) — partial retroactive rollback + carry-over + sunset_justification first applied 선례. 본 Amendment 18 동형 구조 답습
- [ADR-058 §결정 5](ADR-058-adr-sunset-criteria-mandate.md) — 약화 방향 sunset_justification evidence requirement (측정 축 국소 4→3 축소 evidence-gate 발화)
- [ADR-064 §결정 7](ADR-064-decision-principle-mandate.md) — is_transitional:false governance ADR 약화 방향 symmetric evidence-gate
- [ADR-086 §결정 2 5-checklist](ADR-086-deputy-creation-decision-framework.md) — explicit scope L56 "축소" 열거 → FULL self-application (Amendment 13 adjacent-case 와 대조)
- [ADR-091 §결정 1 L193](ADR-091-architectlane-ddd-vocabulary-governance.md) — RefactorAgent DDD pattern mapping frozen 보존, `⚠ CFP-2539` 역주석 append only
- [ADR-131 §결정 1/3](ADR-131-cross-repo-responsibility-placement-governance.md) — L85/L144/L146-150/L230 RefactorAgent 참조 = repo-분해 advocacy 대상. repo-분해 존치 → L150 "무축소" premise TRUE → **Amendment 2 불요**
- ADR-037 (plugin version bump rule — agent surface 축소 = MINOR bump, 0.30.0 → 0.31.0)
- ADR-063 (marketplace atomic version sync — codeforge-design mirrored field version 변경)
- CFP-2476 (Epic Codex 실행기반 검증 확장 — execute-and-falsify infra EXISTS = 측정 축 relocation net-strengthening 환경 변화 evidence)
- CFP-2533 Story A (debate-protocol-v1 v1.3 enabling contract) / Story C (측정 축 수령처)
- CFP-2539 change-plan (internal-docs `wrapper/change-plans/CFP-2539-refactoragent-axis-split.md`) — RefactorAgent 축 분할 설계 SSOT
