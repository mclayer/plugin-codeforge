# [CFP-1117-S1] charter ADR + glossary + concept (Phase 1 docs PR)

**parent_epic**: CFP-1117  
**LAND order**: Phase 1 docs PR (sequential precedent — S2~S6 모두 본 Story LAND 의존)

## WHY

CFP-1117 Epic 의 charter Story — ADR-087 (Hybrid mapping + Subdomain Specialist + Aggregate metaphor 2-layer + Published Language 분리 + Bounded Context governance + enforcement layer + vocabulary theater 차단 forcing function) + Ubiquitous Language SSOT (`docs/glossary.md`, 50+ DDD term) + concept/ 4 entry 신설.

**Vocabulary theater 차단 evidence (INV-5 binding)**: 본 Story 의 charter ADR-087 §결정 7 가 6 Story 전수 forcing function 정의. Story-1 LAND 자체 = vocabulary theater anti-pattern 의 explicit forbid declaration.

## Acceptance criteria

| AC | 설명 | 검증 |
|---|---|---|
| AC-1.1 | `docs/adr/ADR-087-architectlane-ddd-vocabulary-governance.md` 신규 + frontmatter `status: Accepted` 전이 + 7 §결정 cover (Hybrid mapping / Subdomain Specialist / Aggregate metaphor 2-layer / Published Language 분리 / Bounded Context governance / enforcement layer / vocabulary theater forcing function) | `Read(docs/adr/ADR-087-*.md)` + grep `## §결정` count = 7 |
| AC-1.2 | `docs/glossary.md` 신규 + 50+ DDD term entry (`## ` heading count ≥ 50) + 한국어/영어 병기 + plugin-codeforge 적용 사례 | `wc -l docs/glossary.md` ≥ 400 + grep `^### ` count ≥ 50 |
| AC-1.3 | concept/ 4 entry 신규 — `bounded-context.md` / `ubiquitous-language.md` / `aggregate.md` / `4-layer-architecture.md` | `ls docs/domain-knowledge/concept/{bounded-context,ubiquitous-language,aggregate,4-layer-architecture}.md` |
| AC-1.4 | ADR-080 amendment 결정 (DDD pattern 매핑 박제 — deputy/SubAgent ↔ Authority Pair/Domain Service/Subdomain Specialist) | ADR-080 amendments[] entry 추가 OR sunset_justification 명시 |
| AC-1.5 | OQ-1 (ADR-064 forbid-list 확장 anti-pattern only) + OQ-2 (ADR-068 I-6 신설) 결정 — Phase 1 packet 안 Codex feedback 수렴 후 amendment 또는 defer 명시 | Story Issue comment + Phase 1 PR description 안 결정 trail |
| **AC-INV-5-S1** | **ADR-087 §결정 7 forcing function 정의 자체가 vocabulary theater anti-pattern 의 explicit declaration evidence** | ADR-087 본문 grep "vocabulary theater" + INV-5 forcing function 5 영역 enumeration |

## Test contract

- ADR-087 본문 grep — 7 §결정 + INV-5 (5 영역 enumeration) + Codex Q2-Q6 verbatim 박제
- glossary.md entry count ≥ 50 + 한국어/영어 병기 + plugin-codeforge 적용 사례 의무
- concept/ 4 entry 본문 길이 ≥ 30 line each
- ADR-080 amendment 시 ratchet 강화 방향 확인 (terminology 정확도 향상)

## Dependencies

- precedent: CFP-1086 Epic CLOSED + 15 agent baseline + ADR-086 Accepted (verify-via `gh issue view 1086 --json state,labels`)
- no sibling block

## Scope

### In
- ADR-087 신규 발의 + Accepted 전이
- glossary.md 신규
- concept/ 4 entry 신규
- (optional) ADR-080 amendment commit (ratchet 강화 방향)
- (Phase 1 packet 안 결정) ADR-064 + ADR-068 amendment 후보

### Out
- agent frontmatter field 추가 (S2 scope)
- template field 추가 (S3 scope)
- review-verdict-v4 enum 확장 (S4 scope)
- skills/deputy-mandate Subdomain Specialist layer (S5 scope)
- golden-path worked example (S6 scope)
- mctrader downstream Epic (별 CFP)

## 5-checklist self-application (ADR-086, 본 Story 영역)

| Axis | 결과 |
|---|---|
| 1. 결정 영역 | governance / charter ADR — 신설/rename/축소 아님 (axis 1 영역 외) |
| 2. cost | N/A (agent 신설 0건) |
| 3. consumer impact | N/A (wrapper SSOT, consumer CI 별 CFP) |
| 4. sibling cross-ref | ADR-080/064/068 amendment 후보 = ratchet 강화 방향만 |
| 5. deferred carrier | mctrader downstream Epic (별 CFP) |

**통과**.
