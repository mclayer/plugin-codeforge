# RESUME NOTICE — 2026-05-20 KST (Sequential 조건 만족, 본 CFP 재진입)

> 본 file = 직전 commit `5b2cdac` (ON HOLD 산출물 보존) 의 STALE 정정. ESCALATION-PROMPT.md 의 "CFP-1086 LAND 대기" 가정 = trivially 만족. Sequential 조건 충족 + 본 CFP scope 정정 후 진행.

## 1. CFP-1086 LAND verify 완료 (2026-05-20 KST)

| fact | source | 결과 |
|---|---|---|
| CFP-1086 Epic state | `gh issue view 1086` | **CLOSED** (phase:완료 + gate:retro-complete) |
| ADR-086 Accepted | `docs/adr/ADR-086-deputy-creation-decision-framework.md` (main 반영) | Accepted, 2026-05-20 KST, carrier CFP-1086-S1 |
| ADR-042 Amendment 8 | wrapper main grep | **본문 grep 0건 — ADR-RESERVATION 박제 vs main file mismatch** (별 issue) |
| plugin-codeforge-design/agents/ | `git pull origin main` 후 ls | **15 file** (10→15) |
| W1 S1 PR | `gh pr list CFP-1086 in:title` | #1095 wrapper / #51 design `[CFP-1086-S1] 4 agent file + CLAUDE.md + arch doc 7+3+1 roster` MERGED |
| W1 S2 PR | 〃 | #52 design `[CFP-1086-S2] APIContractArchitect mandate body 심화` MERGED |
| W2 S3 PR | 〃 | #1097 wrapper / #53 design RACI 4-way overlap zone MERGED |
| W2 S4 PR | 〃 | #1098 wrapper / #54 design ArchitectAgent chief tie-break ladder MERGED |
| W3 S5 PR | 〃 | #1099 wrapper Cross-Story 통합 검증 MERGED |
| W3 S6 | Epic close 자체 = S6 = retro | retro PR `cef7ca9` 추정 |

## 2. 15 agent baseline (post-CFP-1086)

`c:/workspace/mclayer/plugin-codeforge-design/agents/` 현 file list:

**7 permanent**:
1. ArchitectPLAgent (PL)
2. ArchitectAgent (Chief Author)
3. AggregateArchitectAgent **(신설 Sonnet, CFP-1086-S1)** — RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound aggregate boundary
4. APIContractArchitectAgent **(신설 Sonnet, CFP-1086-S1+S2)** — transport (REST/GraphQL/gRPC/WebSocket) + API versioning + DTO + OpenAPI/GraphQL + contract testing
5. ModuleArchitectAgent **(rename ← CodeArchitectAgent, CFP-1086-S1)** — module boundary + dependency direction + layered/hexagonal/clean + DDD bounded context (module-level)
6. DataArchitectAgent **(축소 ← DataMigrationArchitectAgent, CFP-1086-S1)** — 빅데이터 OLAP only (Parquet/객체 저장소/DuckDB/streaming), RDB 영역 제거
7. SecurityArchitectAgent (기존)
8. InfraOperationalArchitectAgent **(rename ← OperationalRiskArchitectAgent, CFP-676)**
9. TestContractArchitectAgent (기존)

(7 permanent 자체 count = ArchitectPL + ArchitectAgent + 7 SubAgent = 9 → 단 design lane SSOT 의 "7 permanent" 카운팅은 ArchitectPL/Architect 제외 SubAgent only — 즉 SecurityArch / InfraOpArch / TestContractArch / AggregateArch / APIContractArch / ModuleArch / DataArch = 7)

**3+1 CONDITIONAL**:
- LiveOpsDeputyAgent
- LiveOrderingDeputyAgent
- ProductionEvidenceDeputyAgent **(신설 Sonnet, CFP-72 / CFP-1086 cross-ref)**
- AggregateArch CONDITIONAL applicability P2 (frontend-only / API-only consumer non-applicable)

**4-tuple sub-tuple** (ArchitectAgent flat spawn 그룹, deputy 아님):
- CodebaseMapperAgent
- RefactorAgent
- ArchitectAnalystAgent **(rename ← PriorArtAgent, CFP-676)**

= 총 file 15 (7 permanent SubAgent + ArchitectPL + ArchitectAgent + 3+1 CONDITIONAL + 3 sub-tuple), AggregateArch CONDITIONAL applicability 표시 별도 marker.

## 3. 본 CFP scope 정정 (derived default declare, 사용자 정정 의무)

### Before (stale)
- 가정: "10 agent 가 DDD 어휘 0건, ADR + glossary + frontmatter + template + lint + golden-path 6 Story 로 vocabulary 도입"
- gap: CFP-1086 가 이미 7+3+1+4-tuple 재편 + AggregateArch / ModuleArch 가 이미 DDD-adjacent vocab 사용

### After (정정)
- **baseline**: 15 agent (post-CFP-1086) + 4-way RACI matrix (Security/InfraOp/TestContract × Aggregate/Data/Module/APIContract)
- **본 CFP scope**: **systematic DDD vocabulary layer 부착** — 단순 어휘 도입 아닌 (a) 기존 DDD-adjacent vocab 명시화 + (b) Bounded Context governance SSOT + (c) Ubiquitous Language SSOT (glossary) + (d) cross-cutting enforcement (template lint + review-verdict enum + agent frontmatter field)
- **agent 신설 0 / rename 0** (CFP-1086 이미 처리)
- **agent frontmatter field 추가 만**: `bounded_context` + `ddd_pattern` (15 agent 전수)

## 4. 사용자 confirm 3건 (보존, 정정 0)

| # | 결정 | 채택 |
|---|---|---|
| Q1 | Golden-path 시연 대상 ADR | mctrader **ADR-031** data-domain-decoupling |
| Q2 | CFP 분해 형태 | **Mega-CFP-1107 단일 + 6 Story 내부 분해 + Phase 1 docs PR + Phase 2 PR1~PR5 sequential** |
| Q3 | downstream 진입 시점 | upstream Phase 2 PR5 (golden-path) LAND + worked example 시연 PASS 후 |

(CFP 번호 1104 → 1107 정정, 1104~1106 점유)

## 5. CFP-1107 6 Story 분해 (정정된 baseline 위)

| Story | 산출물 | LAND order |
|---|---|---|
| S1 | ADR-087 architectlane-ddd-vocabulary-governance 신규 + `plugin-codeforge/docs/glossary.md` 신규 (50+ DDD term SSOT) + concept/ 신규 4 entry (bounded-context, ubiquitous-language, aggregate, 4-layer-architecture) | Phase 1 docs PR |
| S2 | **15 agent frontmatter** `bounded_context` + `ddd_pattern` field + role-by-role description DDD term injection (vocab harmonize, 신설/rename 0) | Phase 2 PR1 |
| S3 | Story template `§ubiquitous_language` + Change Plan template `§bounded_context_boundary` + `§affected_aggregates` block + lint script | Phase 2 PR2 |
| S4 | review-verdict v4 (현재 v4.7) → v4.8 `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` enum 추가 MINOR | Phase 2 PR3 |
| S5 | **skills/deputy-mandate/SKILL.md** Subdomain Specialist mapping layer (CFP-1086 4-way RACI matrix 위에) + 3+1 CONDITIONAL spawn trigger 어휘 transition (perspective-contributor → subdomain specialist) | Phase 2 PR4 |
| S6 (golden-path) | mctrader ADR-031 before/after worked example — Story field + deputy spawn rationale + Change Plan DDD field + review-verdict finding 전수 박제 → `examples/ddd-golden-path-mct031.md` + FINAL VERDICT (vocabulary theater 차단 evidence) | Phase 2 PR5 |

## 6. ADR-087 신규 (carrier_story = CFP-1107-S1)

frontmatter `mechanical_enforcement_actions[]` 의무 (ADR-040 Amendment 3):
- `ubiquitous-language-drift-check` (warning tier, evidence-checks-registry entry)
- `bounded-context-presence-check` (warning tier)
- `ddd-pattern-frontmatter-check` (warning tier)

amendment 대상 (정정):
- ADR-080 agent-role-terminology-deputy-subagent — DDD pattern 매핑 박제 amendment
- ADR-064 + ADR-068 — DDD enforcement layer integration amendment
- (ADR-004/006/007/014 = CFP-1086 이미 처리, 본 CFP amendment 면제)
- (ADR-042 Amendment 8 main file mismatch = 별 issue, 본 CFP 영역 외)

## 7. 다음 actionable (autonomous progress)

1. **ArchitectAgent direct write spawn** — 6 산출물 single packet:
   - spec file `docs/superpowers/specs/2026-05-20-CFP-1107-architectlane-ddd-vocabulary.md`
   - ADR-087 draft `docs/adr/ADR-087-architectlane-ddd-vocabulary-governance.md`
   - glossary 초안 `docs/glossary.md` (50+ DDD term SSOT)
   - Epic Issue body `.tmp-cfp1107/epic-body.md`
   - 6 Story sub-issue body `.tmp-cfp1107/s{1..6}-body.md`
   - 모두 본 worktree 안 write (commit pending)
2. **CFP-1107 Epic issue create** (gh issue create — Epic body draft → live)
3. **6 Story sub-issue create** (parent:CFP-1107 label)
4. **새 worktree create** `cfp-1107-architectlane-ddd-vocab` (origin/main fresh) — Phase 1 PR target
5. **본 worktree 산출물 cherry-pick** 본 brainstorm artifact 만 보존, ADR/spec/glossary 는 새 worktree 로 transfer
6. **Phase 1 docs PR open** (ADR-087 + glossary + concept 4 entry)

## 8. verify-via

- `gh issue view 1086 --json state,labels`: CLOSED + phase:완료
- `git -C c:/workspace/mclayer/plugin-codeforge-design pull origin main`: 15 file post-pull
- `head c:/workspace/mclayer/plugin-codeforge/docs/adr/ADR-086-*.md`: Accepted frontmatter
- `gh pr list CFP-1086 in:title --state all`: 5 PR MERGED (S1/S2/S3/S4/S5)
