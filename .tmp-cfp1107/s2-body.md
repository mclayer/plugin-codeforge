# [CFP-1117-S2] agent frontmatter field + role description DDD term injection (Phase 2 PR1)

**parent_epic**: CFP-1117  
**LAND order**: Phase 2 PR1 (depends on S1)

## WHY

15 agent 전수 (`plugin-codeforge-design/agents/*.md`) frontmatter 에 `bounded_context` + `ddd_pattern` field 의무. role description 본문 안 DDD term injection (Subdomain Specialist 어휘 transition: perspective-contributor → "which subdomain under threat") — agent **신설/rename 0건** (CFP-1086 이미 처리). field 추가 + 본문 wording amendment만.

**Vocabulary theater 차단 evidence (INV-5 binding)**: agent frontmatter field 가 (a) Story 진입 시 deputy spawn 결정에 어휘 transition 사용 (`which subdomain under threat`) (b) review-verdict-v4 finding type 발화 시 agent role 가 DDD pattern enum cross-validate. 어휘 emit 만 아닌 decision flow 변경 evidence.

## Acceptance criteria

| AC | 설명 | 검증 |
|---|---|---|
| AC-2.1 | 15 agent 전수 frontmatter `bounded_context` field 추가 (value 채워짐, null 금지) — codeforge-governance / shared-kernel 등 enum value | `for f in plugin-codeforge-design/agents/*.md; do grep "^bounded_context:" $f; done` ≥ 15 hit |
| AC-2.2 | 15 agent 전수 frontmatter `ddd_pattern` field 추가 — Authority Pair / Domain Service / Subdomain Specialist enum (ADR-087 §결정 1 정합) | grep `^ddd_pattern:` count ≥ 15 + value enum 3 종 중 하나 |
| AC-2.3 | 3+1 CONDITIONAL deputy 4 agent (LiveOpsDeputyAgent / LiveOrderingDeputyAgent / ProductionEvidenceDeputyAgent + AggregateArchitectAgent CONDITIONAL P2) 본문 안 "which subdomain under threat" 어휘 명시 — perspective-contributor → Subdomain Specialist 어휘 transition | grep "which subdomain under threat" 4 agent 각 ≥ 1 hit |
| AC-2.4 | ArchitectPLAgent + ArchitectAgent 본문 안 Authority Pair / Aggregate Root metaphor / Chief Author 어휘 (ADR-087 §결정 1 정합) | grep "Authority Pair" + "Aggregate Root metaphor" + "Chief Author" 2 agent 각 ≥ 1 |
| AC-2.5 | 7 permanent SubAgent + 3 sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst) 본문 안 Domain Service 어휘 + specialized judgment contributor 어휘 | grep "Domain Service" + "specialized judgment contributor" 10 agent 각 ≥ 1 |
| **AC-INV-5-S2** | **deputy spawn rationale 어휘 transition 이 ArchitectPLAgent 본문에 explicit declare — spawn decision 변경 evidence** | grep "perspective-contributor" → "which subdomain under threat" diff in ArchitectPLAgent.md commit |

## Test contract

- 15 agent file 본문 line count delta < 30% (기존 본문 보존, frontmatter + 본문 1-2 단락 추가만)
- frontmatter YAML valid (yamllint pass)
- agent file `frontmatter` 안 `model:` field 변경 0 (ADR-042 Amendment 8 정합)
- `bounded_context` enum value 4 종 한정: `codeforge-governance` / `shared-kernel` / `infrastructure-generic` / 향후 확장 영역
- `ddd_pattern` enum value 3 종 한정: `Authority Pair` / `Domain Service` / `Subdomain Specialist`

## Dependencies

- S1 LAND (ADR-087 Accepted + glossary 신규)
- precedent: CFP-1086 LAND + 15 agent baseline 안정

## Scope

### In
- 15 agent file frontmatter field 추가
- role description 본문 안 DDD term injection (한정 영역)

### Out
- agent 신설 / rename / model 변경 (N/A — CFP-1086 이미 처리)
- template field (S3)
- lint script (S3)
- review-verdict enum (S4)
- skills/deputy-mandate Subdomain Specialist layer (S5)

## 5-checklist self-application

| Axis | 결과 |
|---|---|
| 1. 결정 영역 | agent metadata 갱신 — axis 1 영역 외 |
| 2. cost | N/A (신설 0) |
| 3. consumer impact | N/A |
| 4. sibling cross-ref | ADR-087 charter 준수 |
| 5. deferred carrier | downstream Epic |

**통과**.
