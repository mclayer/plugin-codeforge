---
adr_number: 86
title: Deputy 신설 결정 framework — axis 분석 + 5-checklist self-application + deferred carrier path
status: Accepted
category: governance
date: 2026-05-20
carrier_story: CFP-1086-S1
parent_epic: CFP-1086
related_stories:
  - CFP-1086
related_adrs:
  - ADR-042  # Amendment 8 = 본 framework self-application 첫 사례 (CFP-1086 Story-1 sibling carrier)
  - ADR-058  # sunset criteria mandate — 본 framework = governance permanent, ratchet 강화 방향만 amendment
  - ADR-060  # evidence-enforceable promotion framework — declaration-only 1차 도입 (mechanical_enforcement_actions: []), 후속 evidence-check entry 발의 시 row append
  - ADR-064  # decision principle mandate — §결정 1 CFP scope unitary + §결정 3 룰 5 가치 판단 한정 AskUserQuestion (3단계 사용자 escalation 정합)
  - ADR-067  # max FIX 3/3 cap — 5-checklist FAIL 시 ArchitectAgent re-spawn (FIX 의무), 3회 후 implementability reassessment trigger
  - ADR-068  # boundary completeness invariants — Amendment 2 (CFP-1086 / Story-1 sibling carrier) tie-break ladder 3단계 가 본 framework §결정 1/2 trigger
  - ADR-070  # Codex verify-before-trust — chief author direct write precedent (본 ADR self-write)
  - ADR-076  # declarative reconciliation upgrade — 3-layer 패턴 (desired / current / converge) governance domain 동형 답습
  - ADR-082  # write-time self-write verification — 본 ADR §본 Epic self-app 첫 사례 의 evidence enumeration 정합
related_files:
  - docs/adr/ADR-042-agent-model-selection-policy.md  # Amendment 8 = self-application 첫 사례
  - docs/adr/ADR-068-boundary-completeness-invariants.md  # Amendment 2 tie-break ladder cross-ref
  - skills/deputy-mandate/SKILL.md  # 7+3+1 roster mandate matrix SSOT
  - CLAUDE.md  # Deputy mandate 매트릭스 (codeforge-design lane) 단락
mechanical_enforcement_actions: []  # declaration-only Wave 1 (ADR-076 / ADR-070 / ADR-082 precedent 답습) — 후속 evidence-check-registry entry 발의 시 row append
amendment_log: []
amendments: []
is_transitional: false  # permanent governance — 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 정합)
---

# ADR-086 — Deputy 신설 결정 framework (axis 분석 + 5-checklist self-application + deferred carrier path)

## 상태

`Accepted (2026-05-20 KST)` — BackendArchEpic CFP-1086 Story-1 carrier (메타 산출물). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합.

## 컨텍스트

### 동인

codeforge 설계 lane 의 deputy roster 변경 / 신설 / rename 결정이 누적되며 동질 결정 패턴이 반복:

- CFP-46 (2026-04-30) — OperationalRiskArchitectAgent 6번째 deputy 신설 (axis: 운영 리스크)
- CFP-632 / ADR-072 (2026-05-13) — ProductionEvidenceDeputyAgent CONDITIONAL 신설 (axis: production evidence)
- CFP-676 (2026-05-19 / ADR-042 Amendment 7) — CodeArchitectAgent + ArchitectAnalystAgent 신설 + DataMigration → Data rename + OperationalRisk → InfraOperational rename (axis: §3 code single-mandate advocacy + 4-tuple sub-tuple PriorArt rename + 데이터 mandate 확장 + infra rename)
- CFP-1086 Story-1 (본 carrier, 2026-05-20) — AggregateArchitectAgent + APIContractArchitectAgent 신설 + CodeArchitect → ModuleArchitect rename + DataArchitect 축소 (axis: RDB OLTP aggregate + API transport + module-level dependency direction + 빅데이터 OLAP)

5 차례 deputy roster 변경 누적 evidence — 결정 절차 SSOT 부재 시 매번 ad-hoc 결정 + ADR Amendment carrier 발의 + Story 단위 retro 의무. mechanism gap 명백.

### Brainstorm Phase 1 dialog 결과 (Q4-prime DDDArch reject 사례)

CFP-1086 Phase 1 Q4-prime — 사용자 발의 DDDArchitectAgent 신설 reject 의 결정 trail 이 axis 분석 부재 ad-hoc 결정 형태. 본 ADR-086 = 동질 결정 패턴의 framework codify carrier — 5번째 deputy roster 변경 (CFP-1086) 시 의무 self-application 의 메타 산출물.

### 미도입 결정 vs 신설 결정 disjoint axis

본 framework = **결정 절차 SSOT only**. 신설 / 미도입 / rename / 축소 모두 동일 framework 적용 (5-checklist self-app 통과 시 결정). 미도입 결정 = scope 축소 ratchet 위반 아님 (ADR-042 Amendment 7 InfraArchitect 신설 철회 + Amendment 8 DDDArchitect 신설 reject 정합).

## 결정

### §결정 1 — axis 분석 의무 (orthogonal axis 검증)

신설 deputy 후보 발의 시 기존 deputy 와의 **axis 분석** 의무. axis 정의:

- **axis** = orthogonal 한 결정 차원 (mandate scope dimension)
- **disjoint axis** = 신설 정당 (signal: 새 mandate scope 영역, 기존 deputy 가 cover 안 함)
- **overlapping axis** = 신설 부정 (signal: 기존 deputy 의 mandate scope 안에 포함 또는 wording-only 차이)
- **method/학파 layer** = axis 미정합 (DDDArch reject 사례 — Domain-Driven Design 은 mandate scope 가 아닌 방법론 layer, ModuleArch + AggregateArch axis 와 orthogonal 하지 않음)

axis enumeration 의무 (Story 또는 Epic spec §axis 분석 section 명시):

1. **기존 N deputy axis enumeration** (각 deputy 의 mandate scope dimension 명시 — 예: SecurityArch = "보안 정책", InfraOperationalArch = "운영 리스크 정책", TestContractArch = "test contract", DataArch = "빅데이터 OLAP", AggregateArch = "RDB OLTP aggregate", APIContractArch = "transport contract", ModuleArch = "module boundary + dependency direction")
2. **후보 deputy axis 명시** (한 문장 — 예: "RDB OLTP aggregate invariant + 트랜잭션 경계 + Alembic 정책")
3. **disjoint 검증** — 기존 N deputy axis 와 후보 axis 가 orthogonal 한가? 1+ overlap = 신설 부정 또는 mandate scope 정정 의무
4. **wording-only superset 검증** — wording 만 superset / 다른 deputy axis cover 영역 / consumer applicability 축소 / method 학파 layer 4종 발견 시 신설 부정 (예: DDDArchitect = wording-only superset, AggregateArch + ModuleArch 가 이미 cover)

### §결정 2 — 5-checklist self-application

신설 결정 직전 5 항목 self-check 의무. 1+ FAIL = 신설 보류 + deferred carrier path 진입 (§결정 3).

| # | Check | 통과 기준 | 사례 (CFP-1086 Story-1 Amendment 8 self-app) |
|---|---|---|---|
| 1 | **axis disjoint** | 신설 deputy 가 기존 deputy 와 axis 중복 0 (§결정 1 검증 통과) | PASS — AggregateArch (RDB OLTP) / APIContract (transport) / ModuleArch (module-level) / DataArch (빅데이터 OLAP) 모두 disjoint axis |
| 2 | **cost-token budget** | spawn count 증가 시 ADR-068 I-5 dimensional empirical grounding 의무 (10 dimension `count` 의 quantitative parameter `[empirical-source: <ref> \| TBD]` annotation) | PASS — 평균 22→28 (1.27배) / full 34→40 (1.18배) 명시 + `[empirical-source: TBD]` annotation (Mitigation 2 explicit TBD) |
| 3 | **consumer carrier** | consumer overlay 필드 명시 (CONDITIONAL applicability / tool override). `project.yaml` schema 신설 또는 갱신 의무 | PASS — `project.yaml aggregate_arch.{applicable, migration_tool}` schema 신설 (Tool scope B + 9-enum migration_tool override default alembic) |
| 4 | **sibling Epic align** | 진행 중 sibling Epic 과 RACI 충돌 0 또는 cross-ref 명시 | PASS — CFP-1079 (OpsExecutionArch sibling Epic) Phase 1 PR open 시점 OPEN PR 0건 명시 → 본 Amendment 8 선점 + CFP-1079 후속 = Amendment 9 |
| 5 | **deferred trigger 명시** | 후속 carrier 별도 CFP 명시 (sub-tuple expansion / CONDITIONAL P3 / consumer schema lint / RACI codify 등 follow-up 영역 enumeration) | PASS — 8 follow-up CFP enumeration (a)~(h) 명시 (sub-tuple 5-tuple expansion / CONDITIONAL P3 trigger / consumer schema lint / RACI mechanical / sibling Epic 통합 / consumer API schema lint / RACI mechanical enforcement / chief tie-break ladder mechanical) |

self-app 산출물 = Story spec §axis 분석 + §5-checklist self-app 표 (carrier Story 안 명시 의무).

### §결정 3 — deferred carrier path

§결정 2 5-checklist 의 1+ FAIL 영역 = **신설 보류 + deferred carrier 의무**.

deferred carrier path:

1. **별도 follow-up CFP 발의** — FAIL 영역 해소 carrier (예: consumer carrier FAIL → consumer schema sub-Epic carrier 별도 CFP)
2. **sibling Epic align** — sibling Epic 과 RACI 충돌 시 — sibling Epic close 후 carrier 진입 또는 cross-ref 명시 후 본 Epic 진행
3. **axis 미확정 영역** — axis 분석 (§결정 1) 통과 안 됨 시 — 별도 brainstorm 단위 (codeforge:brainstorm skill Phase 0+1+2) 후 axis 명확화 carrier 별도 CFP

deferred carrier path 진입 시 본 Story 의 신설 결정 = 보류 (chief author 가 결정 lock + 사용자 escalation 의무, ADR-064 §결정 3 룰 5 가치 판단 한정 `AskUserQuestion` 정합).

### §결정 4 — verdict packet field (review-verdict-v4 v4.6 carrier)

본 framework self-application 결과를 verdict packet 에 explicit marker — `deputy_axis_restructure_self_check_passed` optional bool field (review-verdict-v4 v4.5 → v4.6 MINOR bump):

- **true** = 5-checklist 모두 통과 + axis 분석 통과 = 신설 정당
- **false** = 1+ FAIL = 신설 보류 (deferred carrier path 진입) → ArchitectAgent re-spawn (FIX 의무)
- **omit** = 본 framework 미적용 carrier Story (deputy roster 변경 0건 — v4.5 이전 consumer backward-compat)

적용 lane = **design lane only** (deputy roster 변경 carrier Story 만 적용). code / security / test lane 모두 omit.

### §결정 5 — Mechanical enforcement actions (declaration-only Wave 1)

본 ADR-086 frontmatter `mechanical_enforcement_actions: []` 유지 — declaration-only Wave 1 carrier. ADR-076 / ADR-070 / ADR-082 precedent 답습 (ratchet 강화 방향 evidence-check-registry entry 발의 시 row append).

후속 evidence-check entry 후보 (Wave 2 별 sub-CFP carrier):

- `deputy-axis-restructure-self-check-presence` — review-verdict-v4 packet 안 `deputy_axis_restructure_self_check_passed` field presence-grep (warning-tier)
- `deputy-spawn-count-empirical-grounding` — ADR-068 I-5 backref entry, spawn count quantitative parameter `[empirical-source]` annotation presence-grep (warning-tier, evidence-checks-registry.yaml row append at S1)

본 §결정 5 `mechanical_enforcement_actions: []` retain rationale = (a) Wave 1 declaration-only — 본 ADR-086 자체 적용 deputy roster carrier (CFP-1086 Story-1 Amendment 8) 가 self-application 첫 사례, evidence 누적 후 mechanical wire 결정 / (b) ADR-076 / ADR-070 / ADR-082 retain pattern 4 precedent + 1 new = 5 instance → behavioral / declarative-only retain 정합 (ADR-082 §결정 6 rationale 답습) / (c) ADR-040 Amendment 3 §결정 7.D self-application missing flag 회피.

## 본 Epic self-application 첫 사례 (CFP-1086 Story-1 Amendment 8)

본 ADR-086 의 self-application 첫 사례 = CFP-1086 Story-1 ADR-042 Amendment 8 (7+3+1 roster 재편). brainstorm Phase 0+1+2 + Phase 2 PMO 2nd pass 결과 — 6 Story 모두 self-app PASS / N/A 정상 (Epic 진입 readiness 충족).

### 6 Story self-app 결과 (spec §8 표 verbatim)

| Story | axis disjoint | cost-token | consumer carrier | sibling align | deferred trigger | 종합 |
|---|---|---|---|---|---|---|
| **S1 (본 Story, ADR-086 신설 carrier)** | PASS | PASS (22→28, I-5 carrier) | PASS (P2 + Tool=B) | PASS w/ cross-ref (CFP-1079) | PASS (8 follow-up enumerate) | **READY** |
| S2 (APIContractArch mandate body 심화) | PASS | PASS (S1 포함) | N/A | PASS w/ cross-ref | PASS (consumer API schema lint sub-Epic) | **READY** |
| S3 (4-way overlap zone RACI codify) | PASS (meta-axis) | N/A (codify only) | N/A | PASS | PASS (RACI lint mechanical) | **READY** |
| S4 (ArchitectAgent chief 통합 mechanism) | PASS (meta-layer chief) | PASS (S1 포함) | N/A | PASS w/ cross-ref (P4) | PASS (tie-break ladder lint) | **READY** |
| S5 (Cross-Story 통합 검증) | N/A (verification) | PASS (IntegrationTest baseline) | PASS (consumer-guide) | PASS (Wave 4 sub-Epic align) | PASS (IntegrationTest PASS marker) | **READY** |
| S6 (Epic close + retro) | N/A (retro) | PASS (close only) | N/A | PASS (8 follow-up enumerate) | PASS (Epic close marker) | **READY** |

**6 Story 전건 PASS / N/A 정상 — Epic 진입 readiness 충족** — 본 framework self-application 첫 사례.

## ADR-076 declarative reconciliation 3-layer 동형 답습

본 framework = ADR-076 declarative reconciliation upgrade 의 3-layer 패턴 (desired / current / converge) 의 governance domain 동형 답습:

| Layer | ADR-076 (upgrade domain) | 본 ADR-086 (deputy decision domain) |
|---|---|---|
| **desired state** | wrapper SSOT (`.claude-plugin/plugin.json` 본 release version) | 후보 deputy axis + mandate scope (axis 분석 결과) |
| **current state** | consumer overlay + plugin install 상태 | 기존 N deputy axis enumeration (deputy-mandate skill 매트릭스) |
| **converge** | 3 mode enum (`dry-run` / `snapshot` / `transaction`) | 5-checklist self-app + deferred carrier path |

ratchet 강화 방향 invariant 동형 — desired 우선, current = override 아님, converge = mechanism 명시. ADR-076 §결정 9 multi-version channel declare layer 와 본 §결정 3 deferred carrier path 패턴 동형 (sequential composition).

## 관련 ADR

| ADR | 관계 |
|---|---|
| ADR-042 Amendment 8 (CFP-1086 Story-1 sibling carrier) | **본 framework self-application 첫 사례** — 7+3+1 roster 재편 결정 (axis 분석 + 5-checklist self-app + deferred carrier path 모두 본 ADR-086 §결정 1/2/3 verbatim 적용). 본 Amendment 8 = 본 ADR-086 의 first usage evidence. |
| ADR-068 Amendment 2 (CFP-1086 Story-1 sibling carrier) | **tie-break ladder 3단계 trigger** — Amendment 2 §3단계 (chief judgement + ADR Amendment carrier 발의) 가 본 ADR-086 §결정 1 axis 분석 + §결정 2 5-checklist self-app 의무 발동. Iterative ratchet 강화 (RACI 미codify 영역 → ADR Amendment carrier → 다음 Story 의 1단계 RACI lookup 입력). |
| ADR-064 §결정 1 (CFP scope unitary) | **CFP scope unitary 정합** — 본 ADR-086 = CFP-1086 단일 Story-1 carrier. axis 분석 + 5-checklist + deferred carrier path 3 결정 atomic, unitary scope. |
| ADR-064 §결정 3 룰 5 (가치 판단 한정 AskUserQuestion) | **3단계 사용자 escalation 의무 정합** — §결정 3 deferred carrier path 의 사용자 escalation 발화는 가치 판단 영역 한정 (deputy 신설 = 미공개 컨텍스트 가치 판단). |
| ADR-067 (max FIX 3/3 implementability reassessment cap) | **FIX 의무 정합** — `deputy_axis_restructure_self_check_passed: false` 시 ArchitectAgent re-spawn (FIX 의무), 3회 후 implementability reassessment trigger. |
| ADR-076 (declarative reconciliation upgrade) | **3-layer 패턴 동형 답습** — desired / current / converge governance domain instantiation. ratchet 강화 방향 invariant 동형. |
| ADR-070 / CFP-578 (chief author direct write precedent) | **본 ADR self-write 정합** — ArchitectAgent direct write `docs/adr/ADR-086-deputy-creation-decision-framework.md`. ADR-RESERVATION row 86 `reserved` → `accepted` 전환. |
| ADR-082 (write-time self-write verification) | **§본 Epic self-app 표 evidence 정합** — 6 Story self-app 표 = corpus enumeration write-time verify scope. 본 ADR-086 §본 Epic self-application 첫 사례 표 = CFP-1086 spec §8 verbatim 답습. |
| ADR-058 (ADR sunset criteria mandate) | **`is_transitional: false` (governance permanent) 정합** — §결정 7 보안/governance default presumption. sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 정합). 약화 방향 (axis 분석 의무 약화 / 5-checklist 항목 축소 / deferred carrier path skip) 차단. |
| ADR-060 (evidence-enforceable promotion framework) | **declaration-only Wave 1 carrier** — `mechanical_enforcement_actions: []` retain (ADR-076 / ADR-070 / ADR-082 precedent 답습). 후속 evidence-check entry 발의 시 row append. |

## 해소 기준

N/A — permanent policy. 본 ADR-086 = `is_transitional: false` (governance permanent — ADR-058 §결정 7 보안/governance default presumption 정합).

Amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 sunset_justification 차단):

- scope 확장 (5-checklist → 6+ checklist 추가)
- 강도 강화 (declaration-only → warning-tier evidence-check 승격)
- enforcement surface 확장 (design lane → 다른 lane 적용 확장 별도 CFP)

약화 방향 (axis 분석 의무 약화 / 5-checklist 항목 축소 / deferred carrier path skip / `mechanical_enforcement_actions: []` retain 약화) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

## 결과

- 본 framework = CFP-1086 Story-1 Amendment 8 (7+3+1 roster 재편) self-application 첫 사례 — 6 Story 전건 PASS / N/A 정상 (Epic 진입 readiness 충족)
- review-verdict-v4 v4.5 → v4.6 MINOR carrier (`deputy_axis_restructure_self_check_passed` optional bool field 신설, sibling ADR-042 Amendment 8 동반 atomic)
- ADR-068 Amendment 2 tie-break ladder 3단계 trigger 본 framework §결정 1/2 의무 발동 (iterative ratchet 강화 — RACI 미codify → ADR Amendment carrier → 다음 Story RACI lookup 입력)
- `mechanical_enforcement_actions: []` declaration-only Wave 1 retain — ADR-076 / ADR-070 / ADR-082 precedent 답습 (5 instance 누적, behavioral / declarative-only retain 정합)
- 8 follow-up CFP enumeration (a)~(h) deferred carrier path 정합 (sub-tuple expansion / CONDITIONAL P3 / consumer schema lint / RACI mechanical / sibling Epic 통합 / consumer API schema lint / RACI mechanical enforcement / chief tie-break ladder mechanical)

## 변경이력

- **2026-05-20 v1 (Accepted, CFP-1086)**: 초기 결정 — axis 분석 의무 (§결정 1) + 5-checklist self-application (§결정 2) + deferred carrier path (§결정 3) + verdict packet field 신설 (§결정 4) + declaration-only Wave 1 retain (§결정 5). 본 Epic self-application 첫 사례 6 Story 전건 PASS / N/A 정상. sibling carriers — ADR-042 Amendment 8 (7+3+1 roster 재편) + ADR-068 Amendment 2 (wording SSOT chief tie-break ladder) atomic.

## 관련 파일

- `docs/adr/ADR-042-agent-model-selection-policy.md` (Amendment 8 = 본 framework self-application 첫 사례)
- `docs/adr/ADR-068-boundary-completeness-invariants.md` (Amendment 2 tie-break ladder 3단계 trigger)
- `docs/adr/ADR-RESERVATION.md` (row 86 `reserved` → `accepted` 전환)
- `docs/inter-plugin-contracts/review-verdict-v4.md` (v4.5 → v4.6 MINOR bump — `deputy_axis_restructure_self_check_passed` field 신설)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (review-verdict-v4 version row 갱신)
- `skills/deputy-mandate/SKILL.md` (5+3 → 7+3+1 roster 갱신 + RACI 표준 row 형식 skeleton, body = Story-3)
- `CLAUDE.md` (Deputy mandate 매트릭스 (codeforge-design lane) — 5+3 → 7+3+1)
- `docs/project-config-schema.md` (`aggregate_arch.{applicable, migration_tool}` schema 신설)
- `docs/consumer-guide.md` (`aggregate_arch.*` field 문서화)
- `docs/inter-plugin-contracts/label-registry-v2.md` (v2.40 → v2.41 MINOR — 4 axis label + 1 hotfix-bypass family member)
- `docs/evidence-checks-registry.yaml` (`deputy-spawn-count-empirical-grounding` warning-tier entry append)
- `docs/parallel-work/section-ownership.yaml` (deputy mandate section row append)
