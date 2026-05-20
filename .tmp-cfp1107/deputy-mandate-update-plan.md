# Deputy mandate matrix — Subdomain Specialist mapping layer update plan (CFP-1117 Story-5)

> 본 file = CFP-1117 Story-5 (Phase 2 PR4) 산출물 plan. `skills/deputy-mandate/SKILL.md` 의 CFP-1086 4-way RACI matrix (12 cells × R/A/C/I) **위에 layer 만 추가** — 본문 변경 0건 invariant.

## 1. CFP-1086 baseline (변경 0)

### 4-way RACI matrix (verbatim 보존)

```
Security / InfraOp / TestContract  ×  Aggregate / Data / Module / APIContract
= 12 cells × R / A / C / I
```

| Cell | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|---|---|---|---|---|
| Security × Aggregate | (CFP-1086 정합) | (CFP-1086 정합) | (CFP-1086 정합) | (CFP-1086 정합) |
| Security × Data | ... | ... | ... | ... |
| Security × Module | ... | ... | ... | ... |
| Security × APIContract | ... | ... | ... | ... |
| InfraOp × Aggregate | ... | ... | ... | ... |
| (생략 — CFP-1086 verbatim 보존) |

**본 12 cells × 4-column body 변경 0건** — CFP-1117 Story-5 산출물 verify 의무 = `git diff skills/deputy-mandate/SKILL.md` 안 4-way RACI matrix 본문 line 변경 = 0.

## 2. Subdomain Specialist mapping layer (신규 추가)

CFP-1086 4-way RACI matrix 아래 신규 섹션:

```markdown
## Subdomain Specialist mapping layer (CFP-1117 / ADR-087 §결정 1)

ArchitectLane 15 agent 의 DDD pattern role mapping (ADR-087 §결정 1 정합):

| Agent | DDD role | spawn trigger |
|---|---|---|
| ArchitectPLAgent | Authority Pair (Aggregate Root metaphor) | Story 진입 = 항상 spawn |
| ArchitectAgent | Authority Pair (Chief Author) | Story 진입 = 항상 spawn |
| SecurityArchitectAgent | Domain Service | 항상 spawn (permanent SubAgent) |
| InfraOperationalArchitectAgent | Domain Service | 항상 spawn |
| TestContractArchitectAgent | Domain Service | 항상 spawn |
| AggregateArchitectAgent | Domain Service (CONDITIONAL applicability P2) | RDB OLTP touching Story spawn / frontend-only / API-only consumer non-applicable |
| APIContractArchitectAgent | Domain Service | 항상 spawn |
| ModuleArchitectAgent | Domain Service | 항상 spawn |
| DataArchitectAgent | Domain Service | 항상 spawn (OLAP 영역) |
| CodebaseMapperAgent | Domain Service (sub-tuple) | 4-tuple flat spawn |
| RefactorAgent | Domain Service (sub-tuple) | 4-tuple flat spawn |
| ArchitectAnalystAgent | Domain Service (sub-tuple) | 4-tuple flat spawn |
| LiveOpsDeputyAgent | **Subdomain Specialist** | "which subdomain under threat = live ops" — Live touching Story 활성 시만 spawn |
| LiveOrderingDeputyAgent | **Subdomain Specialist** | "which subdomain under threat = live ordering" — Live ordering touching Story 활성 시만 spawn |
| ProductionEvidenceDeputyAgent | **Subdomain Specialist** | "which subdomain under threat = production evidence" — production cutover touching Story 활성 시만 spawn |

### Subdomain Specialist spawn rationale 어휘 transition (ADR-087 §결정 2)

- **Before (perspective-contributor)**: "보수 perspective / 혁신 perspective / 위협 perspective 필요"
- **After (which subdomain under threat)**: "subdomain decision is at risk — Subdomain Specialist spawn"

**enum value 3 종 한정** (현재 3+1 CONDITIONAL deputy roster 정합):
- `live ops` (LiveOpsDeputyAgent)
- `live ordering` (LiveOrderingDeputyAgent)
- `production evidence` (ProductionEvidenceDeputyAgent)

신규 Subdomain enum 추가 시 ADR-086 5-checklist self-application 의무 + ADR-087 §결정 1 amendment 동반.

### Authority Pair invariant

ArchitectPLAgent + ArchitectAgent = Authority Pair — 양 agent 가 Story 진입 시 항상 spawn. PL = supervisor (deputy spawn 결정 + FIX root-cause 판정) / Architect = chief author (multi-source synthesis + 산출물 author). Authority Pair 의 산출물 (Change Plan + ADR draft) = real Aggregate (consistency boundary, ADR-087 §결정 3 Layer B).

### Domain Service 의 specialized judgment contributor role

7 permanent SubAgent + 3 sub-tuple = Domain Service — specialized judgment contributor. operation-centric (boundary advocacy, noun 아님). stateless (re-spawn 시 context 재load). single-mandate 영역 (CFP-1086 mandate matrix 정합).
```

## 3. CFP-1086 4-way RACI matrix 위 layer 관계

```
┌──────────────────────────────────────────────────────────────────┐
│ CFP-1086 baseline (변경 0)                                          │
│                                                                  │
│   4-way RACI matrix                                              │
│   Security / InfraOp / TestContract  ×                           │
│   Aggregate / Data / Module / APIContract                        │
│   = 12 cells × R / A / C / I                                     │
└──────────────────────────────────────────────────────────────────┘
                            ▲
                            │  Subdomain Specialist mapping layer
                            │  (CFP-1117 신규 추가)
                            │
┌──────────────────────────────────────────────────────────────────┐
│ Subdomain Specialist mapping layer (ADR-087 §결정 1)                │
│                                                                  │
│   15 agent ↔ DDD role mapping                                    │
│   (Authority Pair / Domain Service / Subdomain Specialist)       │
│                                                                  │
│   3+1 CONDITIONAL deputy spawn trigger:                          │
│     "which subdomain under threat" enum 3 종 한정                  │
│       (live ops / live ordering / production evidence)           │
│                                                                  │
│   AggregateArchitectAgent CONDITIONAL applicability P2:           │
│     frontend-only / API-only consumer non-applicable             │
└──────────────────────────────────────────────────────────────────┘
```

## 4. CLAUDE.md amendment (동반)

### 4.1 "Development Agent Team" 표 ArchitectLane row 갱신

Before (Current CLAUDE.md L106-L107):
```
| 설계 | codeforge-design | PL + ArchitectAgent chief + 5 permanent SubAgent + 3 CONDITIONAL + 4-tuple sub-tuple (CFP-676 / ADR-042 Amd 7 — 정확 roster·count SSOT = codeforge-design CLAUDE.md, agent file 실 신설 = W1 S2/W2 S3) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
```

After (CFP-1117 / ADR-087 §결정 1 정합):
```
| 설계 | codeforge-design | PL + ArchitectAgent chief (**Authority Pair**) + 7 permanent SubAgent (**Domain Service**) + 3+1 CONDITIONAL (**Subdomain Specialist**) + 4-tuple sub-tuple (CFP-1086 / ADR-042 Amd 8 — 정확 roster·count SSOT = codeforge-design CLAUDE.md; DDD role mapping SSOT = ADR-087 §결정 1) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
```

### 4.2 "Deputy mandate 매트릭스 (codeforge-design lane)" 단락 amendment

Before — CFP-1086 4-way RACI matrix 만 명시.  
After — CFP-1086 4-way RACI matrix + **CFP-1117 Subdomain Specialist mapping layer** + "which subdomain under threat" 어휘 transition + ADR-087 §결정 1/2 cross-ref.

### 4.3 "오케스트레이션 규칙" 단락 amendment

Before — deputy spawn rationale 어휘 "perspective-contributor" 사용.  
After — deputy spawn rationale 어휘 "which subdomain under threat" 사용 (ADR-087 §결정 2 정합).

## 5. lint enforcement (S3 Wave 1 wire 정합)

본 update 가 LAND 후 다음 lint 가 자동 검출:

- `ubiquitous-language-drift-check` (Wave 1 wire, warning tier) — agent file 본문 안 "Subdomain Specialist" / "Authority Pair" / "Domain Service" 어휘가 glossary.md 정의와 drift 시 emit warning
- `ddd-pattern-frontmatter-check` (Wave 1 wire, warning tier) — agent frontmatter `ddd_pattern` field enum 비non-DDD 시 emit warning
- `bounded-context-presence-check` (Wave 1 wire, warning tier) — Change Plan §bounded_context_boundary 부재 시 emit warning

## 6. INV-5 forcing function evidence (Story-5 contribution)

본 update = INV-5 5 영역 박제 중 **영역 2 (deputy spawn rationale 변경 evidence)** 직접 박제:

- skills/deputy-mandate/SKILL.md = ArchitectPLAgent 가 매 Story 진입 시 호출하는 skill SSOT
- 본 skill 안 "which subdomain under threat" enum 명시 = spawn decision 의 mechanical 변경 (Codex Q4 합의 정합)
- 4-way RACI matrix 본문 변경 0 = CFP-1086 baseline 보존 + layer 만 추가 (ratchet 강화 방향, ADR-058 §결정 5 정합)
- S6 golden-path worked example 의 영역 2 박제가 본 layer 의 실 적용 사례 cross-validation

## 7. 검증 cross-check (S5 LAND 직후)

```bash
# 4-way RACI matrix 본문 변경 0 verify
git diff origin/main -- skills/deputy-mandate/SKILL.md \
  | grep -E "^[+-]" \
  | grep -v "^+++\|^---" \
  | grep -E "RACI|Aggregate|InfraOp|TestContract" \
  || echo "OK — RACI matrix body unchanged"

# Subdomain Specialist mapping layer 추가 verify
grep "Subdomain Specialist" skills/deputy-mandate/SKILL.md \
  && grep "which subdomain under threat" skills/deputy-mandate/SKILL.md \
  && echo "OK — Subdomain Specialist layer added"

# CLAUDE.md amendment verify
grep "Authority Pair" CLAUDE.md \
  && grep "Subdomain Specialist" CLAUDE.md \
  && grep "which subdomain under threat" CLAUDE.md \
  && echo "OK — CLAUDE.md amendment applied"
```
