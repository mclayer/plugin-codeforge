---
spec_id: CFP-1117
title: ArchitectLane DDD vocabulary governance — systematic DDD layer 부착 (15 agent baseline + 4-way RACI matrix 위)
date: 2026-05-20
status: Draft
authors:
  - ArchitectAgent (chief author direct write per ADR-070 / CFP-578 precedent)
related_adrs:
  - ADR-087  # 본 spec 의 charter ADR (carrier_story = CFP-1117-S1)
  - ADR-086  # Deputy 신설 결정 framework — 본 CFP 가 agent 신설 0건이지만 5-checklist self-application 의무
  - ADR-080  # agent-role-terminology-deputy-subagent — DDD pattern 매핑 amendment 대상 (S1 carrier)
  - ADR-064  # decision principle mandate — 본 spec 작성 시 Trace 1/3 정합
  - ADR-068  # boundary completeness invariants — Amendment 후보 (Story-1 packet 안 평가)
  - ADR-042  # agent model selection policy — 신설 0건이므로 amendment 면제 (확인 의무)
  - ADR-013  # codeforge-family-dogfood-out-policy — Published Language 분리 정합
  - ADR-079  # KST display layer — 본 spec governance display layer 정합
  - ADR-082  # write-time self-write verification — lint enforcement (S3 carrier)
parent_epic: CFP-1117
sibling_specs: []
---

# CFP-1117 — ArchitectLane DDD vocabulary governance (systematic layer)

## 1. What + Why

### What

codeforge **ArchitectLane (codeforge-design plugin) 15 agent baseline** (post-CFP-1086 LAND 정합 — 7 permanent SubAgent + ArchitectPL + ArchitectAgent + 3+1 CONDITIONAL deputy + 3 sub-tuple) 위에 **systematic Domain-Driven Design (DDD) vocabulary layer** 부착. 단순 어휘 도입 아닌 4 영역 동시 시공:

1. **agent frontmatter field 의무** — `bounded_context` + `ddd_pattern` (15 agent 전수)
2. **Ubiquitous Language SSOT** — `plugin-codeforge/docs/glossary.md` 신규 (50+ DDD term, codeforge governance BC 적용 사례 박제)
3. **Bounded Context governance + template field 의무** — Story template `§ubiquitous_language` + Change Plan template `§bounded_context_boundary` + `§affected_aggregates` + lint script
4. **review-verdict-v4 enum 확장** — `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` finding type 신설 (v4.7 → v4.8 MINOR bump)
5. **Subdomain Specialist mapping layer** — skills/deputy-mandate/SKILL.md 의 4-way RACI matrix 위에 (CFP-1086 inheritance) "which subdomain under threat" 어휘 transition
6. **Golden-path worked example** — mctrader ADR-031 (data-domain-decoupling, 4-Layer 모델 line 499-524 + Open Host Service + Anti-Corruption Layer 동시 보유) before/after 시연으로 5 영역 박제 (Story field / deputy spawn rationale / Change Plan DDD field / review-verdict finding / ADR acceptance criteria)

### Why (3 layer)

**Layer 1 — empirical 동인 (runtime lesson 6회 누적, RESUME-NOTICE §1 박제)**:
- mctrader/codeforge 의 cross-repo Story 진행 중 차등 해석 + FIX 루프 누적 (MCT-170 / MCT-177 / MCT-179 / MCT-180 / MCT-184 / MCT-185 Phase 0 verify lesson)
- 암묵적 BC/Aggregate 결정이 ADR 에 명시 안 됨 → 신규 agent / member 합류 시 interpretation drift surface

**Layer 2 — Codex BIG CONCERN 차단 (vocabulary theater 위험)**:
- 단순 "agent description 에 DDD 단어 박는" 작업은 실패 — agent 가 DDD 어휘 emit 하면서 기존 implicit decision flow 유지하면 restructure = document 만 향상 / runtime 6회 lesson 해소 = 0
- **forcing function 의무**: 어휘 emit 이 (a) spawn decision (b) review findings (c) ADR acceptance criteria 를 실제로 변경해야 함 — 본 spec 의 INV-5 (FINAL VERDICT § 9 별도 정의)

**Layer 3 — CFP-1086 LAND 정합 (15 agent baseline 위)**:
- CFP-1086 = 4-way RACI matrix (Security/InfraOp/TestContract × Aggregate/Data/Module/APIContract) 완료. AggregateArch / ModuleArch 가 이미 DDD-adjacent vocab 사용 (aggregate invariant / bounded context / layered/hexagonal/clean)
- 본 CFP = 그 위에 **explicit DDD layer 부착** (CFP-1086 가 그 토대를 이미 깐 형태, 본 CFP 가 어휘 격상 + governance SSOT codify)
- agent **신설 0 / rename 0** (CFP-1086 이미 처리). agent frontmatter field 추가만.

## 2. Acceptance Criteria

| AC | 설명 | Story binding | 검증 방법 |
|---|---|---|---|
| AC-1 | ADR-087 신규 발의 (charter ADR — Hybrid mapping + Subdomain Specialist + Aggregate metaphor 2-layer + Published Language 분리 + Bounded Context governance + enforcement layer + INV-5 forcing function) | S1 | `Read(docs/adr/ADR-087-*.md)` + frontmatter `status: Accepted` + 7 §결정 cover |
| AC-2 | `docs/glossary.md` 신규 50+ DDD term SSOT — 한국어/영어 병기 + definition + plugin-codeforge governance BC 적용 사례 | S1 | `wc -l docs/glossary.md` ≥ 400 + grep `## ` count ≥ 50 |
| AC-3 | concept/ 신규 4 entry — `bounded-context.md` / `ubiquitous-language.md` / `aggregate.md` / `4-layer-architecture.md` | S1 | `ls docs/domain-knowledge/concept/{bounded-context,ubiquitous-language,aggregate,4-layer-architecture}.md` |
| AC-4 | 15 agent 전수 frontmatter `bounded_context` + `ddd_pattern` field — value 채워짐 (null 금지) | S2 | `for f in plugin-codeforge-design/agents/*.md; do grep "^bounded_context:" $f; done` ≥ 15 hit |
| AC-5 | role-by-role description DDD term injection — Subdomain Specialist 어휘 transition (perspective-contributor → "which subdomain under threat") 가 3+1 CONDITIONAL deputy 4 agent 본문 반영 | S2 | grep "subdomain" / "bounded context" 카운트 4 agent 각 ≥ 1 |
| AC-6 | Story template `§ubiquitous_language` 신설 + Change Plan template `§bounded_context_boundary` + `§affected_aggregates` block | S3 | `grep "§ubiquitous_language" templates/story-page-structure.md` + `grep "§bounded_context_boundary" plugin-codeforge-design/templates/change-plan.md` |
| AC-7 | lint script — `scripts/check-ddd-vocabulary.sh` (warning tier, evidence-checks-registry entry `ubiquitous-language-drift-check` + `bounded-context-presence-check` + `ddd-pattern-frontmatter-check` 3 신설) | S3 | exit code 0/1/2 + registry yaml row append |
| AC-8 | review-verdict-v4 → v4.8 MINOR bump — finding type 3 enum 추가 (`bc_violation` / `aggregate_violation` / `ubiquitous_language_drift`) | S4 | `grep "bc_violation" docs/inter-plugin-contracts/review-verdict-v4.md` + version frontmatter bump |
| AC-9 | skills/deputy-mandate/SKILL.md Subdomain Specialist mapping layer — 4-way RACI matrix (CFP-1086) 위에 layer 추가 (4-way 본문 변경 0) + 3+1 CONDITIONAL spawn trigger 어휘 transition | S5 | grep "Subdomain Specialist" + "which subdomain under threat" 본 SKILL 안 |
| AC-10 | mctrader ADR-031 golden-path worked example — `examples/ddd-golden-path-mct031.md` 신규 + 5 영역 박제 (Story field / deputy spawn rationale / Change Plan DDD field / review-verdict finding / ADR acceptance criteria) before/after | S6 | `Read(examples/ddd-golden-path-mct031.md)` + 5 sub-section 각 행 |
| **INV-5** | **vocabulary theater 차단 FINAL VERDICT** — S6 의 5 영역 박제가 (a) spawn decision 변경 evidence (b) review findings type 변경 evidence (c) ADR acceptance criteria 변경 evidence 3 enumeration 의무. **본 CFP의 핵심 forcing function — Codex BIG CONCERN 정합** | S6 | S6 acceptance criteria 안 §"FINAL VERDICT: vocabulary theater 차단 evidence" 섹션 explicit |

## 3. Scope

### In scope

- codeforge upstream **wrapper plugin-codeforge + plugin-codeforge-design** 2 repo만
- ADR-087 신규 발의
- `docs/glossary.md` 신규 (wrapper 단독 SSOT)
- agent frontmatter field 추가 (codeforge-design/agents/ 15 file)
- template field 추가 (templates/story-page-structure.md + plugin-codeforge-design/templates/change-plan.md)
- review-verdict-v4 enum 확장 (docs/inter-plugin-contracts/review-verdict-v4.md, 본 wrapper SSOT)
- skills/deputy-mandate/SKILL.md Subdomain Specialist layer
- examples/ddd-golden-path-mct031.md
- ADR-080 / ADR-064 / ADR-068 amendment 후보 (Story-1 packet 안 결정, ratchet 강화 방향만)

### Out of scope (downstream)

- mctrader 6 repo BC charter 박제 — 별 CFP (downstream Epic, upstream Phase 2 PR5 LAND + worked example 시연 PASS 후 진입)
- mctrader Top 10 ADR (ADR-029~033 + 추가 5) retroactive annotation — 별 CFP
- mctrader `docs/glossary.md` SSOT 신규 — 별 CFP (Published Language 분리 정합, 본 CFP 가 codeforge 단독 SSOT 작성, mctrader 측은 별 SSOT)
- consumer CI gate (consumer project 측 DDD lint enforcement) — 별 CFP (Codex Q6 "premature" 합의)
- agent 신설 / rename — N/A (CFP-1086 이미 처리)
- ADR-042 Amendment — N/A (신설 0건이므로)
- ADR-004 / ADR-006 / ADR-007 / ADR-014 amendment — N/A (RESUME-NOTICE §6 정정 — CFP-1086 이미 처리, 본 CFP 면제)

## 4. Assumptions

- **A1**: CFP-1086 Epic 완료 + 15 agent baseline 안정 (verify-via `ls plugin-codeforge-design/agents/` = 15 file, RESUME-NOTICE 2026-05-20 KST verified)
- **A2**: ADR-086 Accepted (verify-via `Read(docs/adr/ADR-086-*.md)` frontmatter status)
- **A3**: 4-way RACI matrix in skills/deputy-mandate/SKILL.md 활성 (Security/InfraOp/TestContract × Aggregate/Data/Module/APIContract)
- **A4**: mctrader ADR-031 line 499-524 4-Layer 모델 + RELOCATE markers + 순환 0 명시 (verify-via Read 2026-05-20 KST verified)
- **A5**: review-verdict-v4 현재 v4.7 (CLAUDE.md 본문 = v4.5, MEMORY.md 본문 = v4.5 — 본 spec 작성 시 wrapper SSOT MANIFEST.yaml read 후 정확 version pin 의무, S4 진입 시점에 verify-before-trust)
- **A6**: 사용자 confirm 3건 (Q1 ADR-031 / Q2 Mega-CFP 단일 + 6 Story 내부 분해 + Phase 1 docs PR + Phase 2 PR1~PR5 sequential / Q3 upstream Phase 2 PR5 LAND + worked example 시연 PASS 후 downstream)
- **A7**: Codex Q2-Q6 합의 (Hybrid / Top 10 / Subdomain Specialist + "which subdomain under threat" / Aggregate metaphor 2-layer / Prompt + Template lint + review-verdict enum / consumer CI gate 별 CFP)

## 5. Dependencies

| ID | 의존 | 종류 | Block / Inform |
|---|---|---|---|
| D1 | CFP-1086 Epic LAND | precedent | Block (S1-S6 전수, 본 CFP 의 baseline) |
| D2 | ADR-086 Accepted | precedent | Block (5-checklist self-application 의무) |
| D3 | ADR-079 KST display layer | runtime | Inform (본 spec governance display layer 정합) |
| D4 | ADR-082 write-time self-write verification | runtime | Inform (S3 lint enforcement 첫 사례) |
| D5 | mctrader ADR-031 (data-domain-decoupling, line 499-524) | external read | Inform (S6 golden-path worked example, read-only reference, mctrader-hub repo) |
| D6 | review-verdict-v4 (현재 v4.7) | runtime | Block S4 (정확 version verify-before-trust 의무) |
| D7 | ADR-080 / ADR-064 / ADR-068 cross-ref + amendment 후보 | runtime | Inform (S1 packet 안 amendment 결정, ratchet 강화 방향만) |
| D8 | label-registry-v2 v2.37 | runtime | Inform (필요 시 신규 hotfix-bypass label 추가, S3 lint warning tier) |

## 6. Risks (Top 5)

| # | Risk | Severity | Likelihood | Mitigation | Carrier |
|---|---|---|---|---|---|
| R1 | **Vocabulary theater** — DDD 어휘 emit 만, spawn decision / review findings / ADR criteria 실제 변경 0 = Codex BIG CONCERN | P0 | HIGH | INV-5 forcing function (AC-INV-5 + S6 FINAL VERDICT 5 영역 박제) — Phase 2 PR5 LAND gate | S6 |
| R2 | **Subdomain 분류 정치적 합의 어려움** — Core / Supporting / Generic 어느 subdomain 인지 의견 발산 | P1 | MED | upstream = 분류 기준 SSOT 만 / downstream (별 CFP) = repo-by-repo 실 분류 | S1 |
| R3 | **self-reference paradox** — codeforge 가 DDD 채택 = codeforge 가 codeforge 자신 사용? (ADR-013 / ADR-005 충돌 우려) | P3 | LOW | non-blocker — DDD = 외부 design discipline. 채택 ≠ self-application. ADR-013 / ADR-005 위반 0 (Researcher Phase 0 verified) | S1 |
| R4 | **cross-repo coupling drift** — codeforge BC 어휘 변경 시 mctrader downstream 의도와 분리 안 됨 | P2 | MED | Published Language 분리 (codeforge `docs/glossary.md` 단독 SSOT + mctrader 별 SSOT 후속 CFP). 동음이의 (Aggregate 등) glossary 안 explicit separate | S1 |
| R5 | **9 ADR amendment ripple** — ADR-080 + ADR-064 + ADR-068 amendment 가 보호되지 않는 ratchet 약화 | P2 | LOW | ADR-058 §결정 5 정합 — amendment 시 sunset_justification 의무 + ratchet 강화 방향만 허용. ADR-087 본문에 명시 | S1 |

**Note on R1 — vocabulary theater forcing function**: AC-INV-5 가 본 CFP 의 핵심. 6 Story 전수 acceptance criteria 각각 "어휘 emit ↔ spawn/review/ADR criteria 변경" 검증항목 1건 이상 의무. S6 FINAL VERDICT 가 5 영역 박제로 evidence enumeration.

## 7. Open Questions

본 spec 작성 시점 미해결 결정점 (S1 진입 직전 Phase 1 packet 안 결정 의무):

| OQ | 결정점 | 후보 | 권고 default |
|---|---|---|---|
| OQ-1 | ADR-064 Trace 1 forbid-list dictionary 확장 여부 | 어휘 자체 forbid 아님 / anti-pattern 만 (careful framing) | Anti-pattern만 forbid (예: "Big Ball of Mud" 가 design intent 로 채택 표현 금지). ADR-087 §결정 7 안 명시 |
| OQ-2 | ADR-068 boundary completeness invariants 위에 DDD I-6 신설 여부 | 추가 invariant `bounded_context_explicit` (Story 가 multi-BC 가로지를 시 explicit declare 의무) | I-6 신설 검토. S1 Phase 1 packet 안 결정 (Codex feedback 수렴 의무) |
| OQ-3 | Codex Q6 enforcement layer 의 mechanical_enforcement_actions[] Wave 1 채택 vs declaration-only | (a) lint 3 entry 동시 wire / (b) declaration-only 1차 + Wave 2 wire (ADR-082 / ADR-076 / ADR-070 precedent 답습) | declaration-only Wave 1 (ADR-082 precedent 답습) + S3 가 lint 3 script 신설 + S4 wire (label-registry-v2 hotfix-bypass entry 추가) — vocabulary theater 차단 정합 (Wave 1 부터 실제 mechanism 부착) |

## 8. Implementation phases

### Phase 1 — docs PR (Story-1 S1 LAND)
- spec file (본 file)
- ADR-087 draft → Accepted
- glossary.md 신규
- concept/ 4 entry 신규
- ADR-080 / ADR-064 / ADR-068 amendment commit (필요 시)

### Phase 2 — sequential PR1~PR5 (Story-2~6)
- PR1 (S2): 15 agent frontmatter field 추가 + role-by-role DDD term injection
- PR2 (S3): template field + lint script
- PR3 (S4): review-verdict-v4 → v4.8 MINOR bump
- PR4 (S5): skills/deputy-mandate Subdomain Specialist layer
- PR5 (S6): mctrader ADR-031 golden-path worked example + FINAL VERDICT INV-5 evidence enumeration

## 9. Test strategy

### Unit (S3 lint script)
- `scripts/check-ddd-vocabulary.sh` test fixture — 15 agent frontmatter `bounded_context` field 부재 시 exit 1 + warning message
- `scripts/check-bounded-context-presence.sh` test fixture — Change Plan template 안 `§bounded_context_boundary` 부재 시 exit 1
- `scripts/check-ddd-pattern-frontmatter.sh` test fixture — agent frontmatter `ddd_pattern` value enum 비non-DDD 시 exit 1

### Integration (S6 golden-path)
- mctrader ADR-031 read + before/after worked example 작성 → review-verdict-v4 v4.8 enum 3 신설 finding emit 시 5 영역 박제 cross-validation
- 본 worked example 자체가 INV-5 evidence enumeration

### evidence-check-registry entry 신설 (S3)
- `ubiquitous-language-drift-check` (warning tier, `hotfix-bypass:ubiquitous-language-drift` 47번째 family member)
- `bounded-context-presence-check` (warning tier, `hotfix-bypass:bounded-context-presence` 48번째 family member)
- `ddd-pattern-frontmatter-check` (warning tier, `hotfix-bypass:ddd-pattern-frontmatter` 49번째 family member)

## 10. Documentation impact

### 변경 영역

- **신규**:
  - `docs/adr/ADR-087-architectlane-ddd-vocabulary-governance.md`
  - `docs/glossary.md`
  - `docs/domain-knowledge/concept/{bounded-context,ubiquitous-language,aggregate,4-layer-architecture}.md`
  - `examples/ddd-golden-path-mct031.md`
  - `scripts/check-ddd-vocabulary.sh` + `scripts/check-bounded-context-presence.sh` + `scripts/check-ddd-pattern-frontmatter.sh`
  - `templates/github-workflows/{ubiquitous-language-drift,bounded-context-presence,ddd-pattern-frontmatter}.yml`

- **갱신**:
  - `plugin-codeforge-design/agents/*.md` × 15 (frontmatter field 추가)
  - `templates/story-page-structure.md` (`§ubiquitous_language` 추가)
  - `plugin-codeforge-design/templates/change-plan.md` (`§bounded_context_boundary` + `§affected_aggregates` 추가)
  - `docs/inter-plugin-contracts/review-verdict-v4.md` (v4.7 → v4.8 MINOR bump + finding type 3 enum)
  - `docs/inter-plugin-contracts/MANIFEST.yaml` (v4.8 row update)
  - `skills/deputy-mandate/SKILL.md` (Subdomain Specialist layer)
  - `docs/evidence-checks-registry.yaml` (3 row append, warning tier)
  - `docs/inter-plugin-contracts/label-registry-v2.md` (v2.37 → v2.38 MINOR bump + 3 hotfix-bypass label entry)
  - `CLAUDE.md` (ArchitectLane 단락 DDD 어휘 정렬 amendment)

### Amendment 후보 (S1 Phase 1 packet 안 결정)

- **ADR-080** — agent-role-terminology-deputy-subagent 의 DDD pattern 매핑 박제 (deputy / SubAgent ↔ Authority Pair / Domain Service / Subdomain Specialist)
- **ADR-064** — Trace 1 forbid-list dictionary 확장 1건 (OQ-1 결정 후, anti-pattern only)
- **ADR-068** — boundary completeness 5 invariants 위에 DDD I-6 신설 후보 (OQ-2 결정 후)

## 11. Rollback plan

본 CFP 는 **governance + documentation layer + frontmatter field 추가**. 코드 변경 0건 (lint script 제외). Rollback = 6 PR revert sequential reverse order (PR5 → PR4 → PR3 → PR2 → PR1 → Phase 1 docs PR). 단:

- AC-INV-5 forcing function = vocabulary theater 차단 진입 후 rollback 시 어휘 retain 위험 → rollback 시 agent frontmatter field `bounded_context` / `ddd_pattern` revert + glossary.md 제거 + template field 제거 atomic 의무
- review-verdict-v4 v4.8 → v4.7 downgrade = ADR-008 sibling sync 6 plugin 의무 (codeforge-design / codeforge-develop / codeforge-review / codeforge-test / codeforge-requirements / codeforge-pmo)
- ADR-087 status: Accepted → Deprecated 전이 (revert 가 아닌 sunset 자취 보존)

## 12. Verification (ADR-070 verify-before-trust)

본 spec 작성 직후 verification:

- [x] CFP-1086 Epic CLOSED + 15 agent baseline (verify-via `gh issue view 1086` + `ls plugin-codeforge-design/agents/` = 15 file)
- [x] ADR-086 Accepted (verify-via `Read(docs/adr/ADR-086-*.md)` frontmatter)
- [x] mctrader ADR-031 line 499-524 4-Layer 모델 verified (verify-via `Read(c:/workspace/mclayer/mctrader-hub/docs/adr/ADR-031-data-domain-decoupling.md)` line 499-524)
- [x] docs/glossary.md 부재 = 신규 생성 의무 (verify-via `ls c:/workspace/mclayer/plugin-codeforge/docs/glossary.md` MISSING)
- [x] ADR-087 슬롯 OK = 다음 신규 ADR (verify-via `ls docs/adr/ADR-*.md` max = ADR-086)
- [x] templates/adr.md + change-plan.md 구조 read 완료 (codeforge-design SSOT)
- [x] 사용자 confirm 3건 + Codex Q2-Q6 합의 박제 (ESCALATION-PROMPT §4-§5 verbatim)
- [ ] CFP-1117 issue create + 6 sub-issue create (별 turn, Orchestrator 의무)
- [ ] Phase 1 PR open (Story-1 S1 LAND 후 진입)
