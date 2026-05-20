# [CFP-1117-S5] skills/deputy-mandate Subdomain Specialist mapping layer (Phase 2 PR4)

**parent_epic**: CFP-1117  
**LAND order**: Phase 2 PR4 (depends on S1, S2, S4)

## WHY

`skills/deputy-mandate/SKILL.md` 의 CFP-1086 4-way RACI matrix (Security/InfraOp/TestContract × Aggregate/Data/Module/APIContract = 12 cells × R/A/C/I) 위에 **Subdomain Specialist mapping layer 추가** — 3+1 CONDITIONAL deputy 4 agent 의 spawn trigger 어휘 transition (perspective-contributor → "which subdomain under threat"). 4-way RACI matrix **본문 변경 0건** (layer 만 추가). CLAUDE.md "ArchitectLane 단락" + "Deputy mandate 매트릭스" + "오케스트레이션 규칙" 안 deputy spawn rationale 어휘 amendment 동반.

**Vocabulary theater 차단 evidence (INV-5 binding)**: deputy spawn rationale 어휘 transition 이 `codeforge:deputy-mandate` skill 안 explicit 채택 = "deputy spawn rationale 변경 evidence" 직접 박제 (INV-5 5 영역 중 2번째 영역). ArchitectPLAgent 가 매 Story 진입 시 본 skill 호출 → "which subdomain under threat" enum 가 spawn decision 변경.

## Acceptance criteria

| AC | 설명 | 검증 |
|---|---|---|
| AC-5.1 | `skills/deputy-mandate/SKILL.md` Subdomain Specialist mapping layer 추가 — 3+1 CONDITIONAL deputy 4 agent (LiveOpsDeputyAgent / LiveOrderingDeputyAgent / ProductionEvidenceDeputyAgent + AggregateArchitectAgent CONDITIONAL P2) 의 "which subdomain under threat" enum 명시 | grep "Subdomain Specialist" + "which subdomain under threat" 본 SKILL 안 |
| AC-5.2 | 4-way RACI matrix 본문 변경 0 (CFP-1086 baseline 보존) | git diff `skills/deputy-mandate/SKILL.md` 안 RACI matrix line 본문 변경 0 (layer 만 추가) |
| AC-5.3 | `CLAUDE.md` "Deputy mandate 매트릭스 (codeforge-design lane)" 단락 amendment — Subdomain Specialist layer 추가 + 어휘 transition 명시 | grep "which subdomain under threat" CLAUDE.md ≥ 1 |
| AC-5.4 | `CLAUDE.md` "Development Agent Team" 표 ArchitectLane row DDD 어휘 정렬 — 15 agent 의 DDD role (Authority Pair / Domain Service / Subdomain Specialist) 명시 | grep "Authority Pair\|Subdomain Specialist" CLAUDE.md ≥ 2 |
| AC-5.5 | `CLAUDE.md` "오케스트레이션 규칙" 안 deputy spawn rationale 어휘 transition — perspective-contributor 어휘 → "which subdomain under threat" amendment | git diff CLAUDE.md 안 "perspective-contributor" 어휘 replace OR "which subdomain under threat" 어휘 추가 |
| **AC-INV-5-S5** | **`codeforge:deputy-mandate` skill 안 Subdomain Specialist mapping = ArchitectPLAgent 의 매 Story spawn decision 변경 evidence** | golden-path S6 안 ArchitectPL spawn rationale before/after diff cross-validation |

## Test contract

- skills/deputy-mandate/SKILL.md frontmatter version field bump (CFP-1086 baseline → CFP-1117 layer)
- 4-way RACI matrix 본문 verbatim 보존 (line-by-line diff = 0)
- Subdomain Specialist mapping layer 가 RACI matrix 아래 위치 (precedent 보존)
- CLAUDE.md amendment 가 ratchet 강화 방향 (어휘 정확도 향상, 약화 0)

## Dependencies

- S1 LAND (ADR-087 §결정 2 deputy spawn rationale 어휘 transition charter)
- S2 LAND (15 agent frontmatter `ddd_pattern` field 정합 — `Subdomain Specialist` enum value verify-via)
- S4 LAND (review-verdict-v4 v4.8 + deputy mandate cross-ref 안정)

## Scope

### In
- skills/deputy-mandate/SKILL.md Subdomain Specialist mapping layer 추가
- CLAUDE.md ArchitectLane 단락 + Deputy mandate 매트릭스 + 오케스트레이션 규칙 amendment

### Out
- 4-way RACI matrix 본문 변경 (N/A — baseline 보존)
- agent file 본문 (S2 영역)
- review-verdict enum (S4)
- golden-path worked example (S6)

## 5-checklist self-application

| Axis | 결과 |
|---|---|
| 1. 결정 영역 | skill body + CLAUDE.md amendment — axis 1 영역 외 |
| 2. cost | N/A |
| 3. consumer impact | wrapper 단독 SSOT |
| 4. sibling cross-ref | ADR-087 + ADR-064 (decision principle, deputy spawn rationale 정합) |
| 5. deferred carrier | downstream Epic |

**통과**.
