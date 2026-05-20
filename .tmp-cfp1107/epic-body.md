# [EPIC] CFP-1117 — ArchitectLane DDD vocabulary governance (systematic DDD layer 부착)

> **Mega-CFP 단일 + 6 Story 내부 분해 + Phase 1 docs PR + Phase 2 PR1~PR5 sequential** (사용자 confirm Q2 정합)

## WHY

codeforge ArchitectLane (codeforge-design plugin) **15 agent baseline** (post-CFP-1086 LAND 정합 — 7 permanent SubAgent + ArchitectPL + ArchitectAgent + 3+1 CONDITIONAL deputy + 3 sub-tuple) 위에 **systematic DDD vocabulary layer** 부착. 단순 어휘 도입 아닌 4 영역 동시 시공:

1. agent frontmatter field 의무 (`bounded_context` + `ddd_pattern`)
2. Ubiquitous Language SSOT (`plugin-codeforge/docs/glossary.md`, 50+ DDD term)
3. Bounded Context governance + template field 의무 + lint script
4. review-verdict-v4 enum 확장 (`bc_violation` / `aggregate_violation` / `ubiquitous_language_drift`)
5. Subdomain Specialist mapping layer (skills/deputy-mandate/SKILL.md, 4-way RACI matrix 위)
6. Golden-path worked example (mctrader ADR-031 before/after, 5 영역 박제 INV-5)

### 동기 (3 layer)

**Layer 1 — empirical 동인**: mctrader/codeforge cross-repo Story 진행 중 차등 해석 + FIX 루프 lesson 6회 누적 (MCT-170 / MCT-177 / MCT-179 / MCT-180 / MCT-184 / MCT-185 Phase 0 verify pattern 재현). 암묵적 BC/Aggregate 결정이 ADR 에 명시 안 됨 → interpretation drift surface.

**Layer 2 — CFP-1086 LAND 정합**: CFP-1086 4-way RACI matrix (Security/InfraOp/TestContract × Aggregate/Data/Module/APIContract) 위에 layer. AggregateArch / ModuleArch 가 이미 DDD-adjacent vocab 사용. 본 CFP = 그 위에 explicit DDD layer 부착 (agent 신설 0 / rename 0).

**Layer 3 — Vocabulary theater 차단 (Codex BIG CONCERN)**: 어휘 emit 이 spawn decision / review findings / ADR acceptance criteria 를 실제로 변경해야 함. INV-5 forcing function 의무.

## scope_manifest

```yaml
<!-- scope_manifest -->
parent_epic: CFP-1117
phase_1_pr_count: 1
phase_2_pr_count: 5
total_pr_count_estimate: 6

planned_adrs:
  - ADR-087-architectlane-ddd-vocabulary-governance  # Story-1 carrier (charter ADR)

planned_files:
  # Story-1 (Phase 1 docs PR)
  - docs/adr/ADR-087-architectlane-ddd-vocabulary-governance.md
  - docs/glossary.md
  - docs/domain-knowledge/concept/bounded-context.md
  - docs/domain-knowledge/concept/ubiquitous-language.md
  - docs/domain-knowledge/concept/aggregate.md
  - docs/domain-knowledge/concept/4-layer-architecture.md

  # Story-2 (Phase 2 PR1)
  - plugin-codeforge-design/agents/ArchitectPLAgent.md  # frontmatter + role description DDD term
  - plugin-codeforge-design/agents/ArchitectAgent.md
  - plugin-codeforge-design/agents/SecurityArchitectAgent.md
  - plugin-codeforge-design/agents/InfraOperationalArchitectAgent.md
  - plugin-codeforge-design/agents/TestContractArchitectAgent.md
  - plugin-codeforge-design/agents/AggregateArchitectAgent.md
  - plugin-codeforge-design/agents/APIContractArchitectAgent.md
  - plugin-codeforge-design/agents/ModuleArchitectAgent.md
  - plugin-codeforge-design/agents/DataArchitectAgent.md
  - plugin-codeforge-design/agents/CodebaseMapperAgent.md
  - plugin-codeforge-design/agents/RefactorAgent.md
  - plugin-codeforge-design/agents/ArchitectAnalystAgent.md
  - plugin-codeforge-design/agents/LiveOpsDeputyAgent.md
  - plugin-codeforge-design/agents/LiveOrderingDeputyAgent.md
  - plugin-codeforge-design/agents/ProductionEvidenceDeputyAgent.md

  # Story-3 (Phase 2 PR2)
  - templates/story-page-structure.md  # §ubiquitous_language
  - plugin-codeforge-design/templates/change-plan.md  # §bounded_context_boundary + §affected_aggregates
  - scripts/check-ddd-vocabulary.sh
  - scripts/check-bounded-context-presence.sh
  - scripts/check-ddd-pattern-frontmatter.sh
  - templates/github-workflows/ubiquitous-language-drift.yml
  - templates/github-workflows/bounded-context-presence.yml
  - templates/github-workflows/ddd-pattern-frontmatter.yml
  - docs/evidence-checks-registry.yaml  # 3 row append
  - docs/inter-plugin-contracts/label-registry-v2.md  # v2.37 → v2.38 MINOR bump

  # Story-4 (Phase 2 PR3)
  - docs/inter-plugin-contracts/review-verdict-v4.md  # v4.7 → v4.8 MINOR bump
  - docs/inter-plugin-contracts/MANIFEST.yaml  # version field update

  # Story-5 (Phase 2 PR4)
  - skills/deputy-mandate/SKILL.md  # Subdomain Specialist mapping layer
  - CLAUDE.md  # ArchitectLane 단락 amendment

  # Story-6 (Phase 2 PR5)
  - examples/ddd-golden-path-mct031.md

planned_inter_plugin_contracts:
  - review-verdict-v4 (MINOR v4.7 → v4.8)

planned_label_registry_bumps:
  - label-registry-v2 (MINOR v2.37 → v2.38, 3 신규 entry)

planned_claude_md_sections:
  - "Development Agent Team" 표 안 ArchitectLane 어휘 DDD 정렬 (Story-5)
  - "Deputy mandate 매트릭스 (codeforge-design lane)" 단락 안 Subdomain Specialist layer 추가 (Story-5)
  - "오케스트레이션 규칙" 안 deputy spawn rationale 어휘 transition (Story-5)

cross_section_conflict_detection: true

sibling_epic_cross_ref:
  - CFP-1086  # baseline (이미 close, 본 Epic = 그 위에 layer)
  - CFP-676   # InfraOperational rename precedent (이미 close)
  # downstream Epic = 별 CFP, upstream Phase 2 PR5 LAND + worked example 시연 PASS 후 진입

mechanical_enforcement_actions:
  - ubiquitous-language-drift-check       # Wave 1 wire (declaration-only 1차 + S3 wire — ADR-087 §결정 6 정합)
  - bounded-context-presence-check        # Wave 1 wire
  - ddd-pattern-frontmatter-check         # Wave 1 wire
```

## 6 Story 분해

| Story | 산출물 | LAND order | dependency |
|---|---|---|---|
| **S1** [CFP-1117-S1] charter ADR + glossary | ADR-087 신규 + `docs/glossary.md` 신규 (50+ DDD term SSOT) + concept/ 4 entry 신규 + (optional) ADR-080/064/068 amendment 후보 결정 | Phase 1 docs PR | (none — precedent CFP-1086 close 확인) |
| **S2** [CFP-1117-S2] agent frontmatter | 15 agent 전수 frontmatter `bounded_context` + `ddd_pattern` field + role-by-role description DDD term injection (vocab harmonize, 신설/rename 0) | Phase 2 PR1 | S1 |
| **S3** [CFP-1117-S3] template + lint | Story template `§ubiquitous_language` + Change Plan template `§bounded_context_boundary` + `§affected_aggregates` block + lint script 3 + workflow 3 + label-registry v2.37 → v2.38 MINOR | Phase 2 PR2 | S1 |
| **S4** [CFP-1117-S4] review-verdict enum | review-verdict-v4 v4.7 → v4.8 MINOR bump (`bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` enum) + MANIFEST.yaml row update + 6 plugin sibling sync (ADR-010 의무) | Phase 2 PR3 | S1, S3 |
| **S5** [CFP-1117-S5] Subdomain Specialist layer | skills/deputy-mandate/SKILL.md Subdomain Specialist mapping layer (CFP-1086 4-way RACI matrix 위) + 3+1 CONDITIONAL spawn trigger 어휘 transition (perspective-contributor → "which subdomain under threat") + CLAUDE.md amendment | Phase 2 PR4 | S1, S2, S4 |
| **S6** [CFP-1117-S6] golden-path worked example | mctrader ADR-031 before/after worked example — `examples/ddd-golden-path-mct031.md` + **FINAL VERDICT INV-5 evidence enumeration** (5 영역 박제: Story field / deputy spawn rationale / Change Plan DDD field / review-verdict finding / ADR acceptance criteria) | Phase 2 PR5 | S1, S2, S3, S4, S5 |

## ADR-086 5-checklist self-application (의무)

본 CFP 가 agent 신설 0건이지만 ADR-086 framework 통과 confirm 의무 (5-checklist self-application).

| Axis | Check | 결과 |
|---|---|---|
| 1. 결정 영역 axis | 본 CFP 가 어느 axis 결정인지? | **agent vocabulary layer** (신설/rename/축소 아님) — 5-checklist axis 1 영역 외 |
| 2. cost analysis | 신규 agent 신설 시 cost? | **N/A** — 신설 0건 |
| 3. consumer impact | consumer overlay 변경 영향? | **N/A** — wrapper 단독 SSOT, consumer CI gate 제외 (Codex Q6 합의) |
| 4. sibling cross-ref | sibling ADR conflict? | ADR-080 / ADR-064 / ADR-068 amendment 후보 = **ratchet 강화 방향만** (충돌 0, ADR-058 §결정 5 정합) |
| 5. deferred carrier path | 본 CFP 후속 carrier? | **mctrader downstream Epic** (별 CFP, BC charter + Top 10 ADR annotation + mctrader glossary SSOT, upstream Phase 2 PR5 LAND + worked example 시연 PASS 후 진입) |

**5-checklist 통과 (P7 framework self-application)** — agent 신설 0건이므로 framework axis 1 영역 외, axis 4 sibling cross-ref + axis 5 deferred carrier path 만 substantive 적용. 본 Epic 진행 가능.

## Risks Top 5

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Vocabulary theater (어휘 emit 만, decision flow 변경 0) | P0 | INV-5 forcing function (5 영역 박제 S6 evidence enumeration) — Phase 2 PR5 LAND gate |
| R2 | Subdomain 분류 정치적 합의 어려움 | P1 | upstream = 분류 기준만 / downstream = repo-by-repo 실 분류 |
| R3 | self-reference paradox (codeforge ↔ codeforge 자기 사용) | P3 | non-blocker — DDD = 외부 design discipline. ADR-013 / ADR-005 위반 0 |
| R4 | cross-repo coupling drift (codeforge BC ↔ mctrader BC) | P2 | Published Language 분리 (2 SSOT 동음이의 explicit separate) |
| R5 | 9 ADR amendment ripple (ADR-080/064/068) | P2 | ADR-058 §결정 5 정합 — ratchet 강화 방향만, sunset_justification 의무 |

## Phase 일정 (sequential, Q2 confirm)

```
Phase 1 docs PR (S1) → LAND
  ↓
Phase 2 PR1 (S2) → LAND
  ↓
Phase 2 PR2 (S3) → LAND
  ↓
Phase 2 PR3 (S4) → LAND  (review-verdict-v4 v4.8 MINOR + 6 plugin sibling sync)
  ↓
Phase 2 PR4 (S5) → LAND  (Subdomain Specialist layer + CLAUDE.md amendment)
  ↓
Phase 2 PR5 (S6) → LAND  (golden-path worked example + INV-5 FINAL VERDICT)
  ↓
Epic close + retro (PMOAgent autonomous trigger, ADR-045)
  ↓
downstream Epic (별 CFP) 진입 — mctrader BC charter + Top 10 ADR annotation + mctrader glossary
```

## Acceptance criteria (Epic-level)

- [ ] AC-1 — ADR-087 신규 발의 (charter ADR, status: Accepted)
- [ ] AC-2 — `docs/glossary.md` 신규 50+ DDD term SSOT
- [ ] AC-3 — concept/ 신규 4 entry
- [ ] AC-4 — 15 agent 전수 frontmatter `bounded_context` + `ddd_pattern` field
- [ ] AC-5 — role-by-role description DDD term injection (3+1 CONDITIONAL deputy 4 agent)
- [ ] AC-6 — Story template `§ubiquitous_language` + Change Plan template `§bounded_context_boundary` + `§affected_aggregates`
- [ ] AC-7 — lint script 3 + workflow 3 + evidence-checks-registry 3 row append + label-registry-v2 v2.38
- [ ] AC-8 — review-verdict-v4 v4.8 MINOR bump + 3 finding type enum + 6 plugin sibling sync
- [ ] AC-9 — skills/deputy-mandate Subdomain Specialist layer
- [ ] AC-10 — mctrader ADR-031 golden-path worked example
- [ ] **INV-5 — vocabulary theater 차단 FINAL VERDICT evidence enumeration** (5 영역 박제)
- [ ] Epic retro (PMOAgent autonomous, ADR-045)

## 참조

- spec file: `docs/superpowers/specs/2026-05-20-CFP-1117-architectlane-ddd-vocabulary.md`
- ADR draft: `docs/adr/ADR-087-architectlane-ddd-vocabulary-governance.md`
- 사용자 confirm: ESCALATION-PROMPT.md §4 + RESUME-NOTICE-2026-05-20.md §4
- Codex Q2-Q6 합의: ESCALATION-PROMPT.md §5 (verbatim)
- baseline: CFP-1086 Epic close, ADR-086 Accepted (2026-05-20 KST)
- mctrader ADR-031 line 499-524 (4-Layer 모델 + OHS + ACL)
