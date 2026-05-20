# [CFP-1117-S3] Story / Change Plan template + lint + workflow (Phase 2 PR2)

**parent_epic**: CFP-1117  
**LAND order**: Phase 2 PR2 (depends on S1)

## WHY

Story template (`templates/story-page-structure.md`) `§ubiquitous_language` 신규 + Change Plan template (`plugin-codeforge-design/templates/change-plan.md`) `§bounded_context_boundary` + `§affected_aggregates` block 신규 + lint script 3 + workflow 3 + evidence-checks-registry 3 row append + label-registry-v2 v2.37 → v2.38 MINOR bump.

**Vocabulary theater 차단 evidence (INV-5 binding)**: template field 의무화 + lint warning tier wire = "Story field 변경 evidence" + "Change Plan DDD field 변경 evidence" 2 영역 직접 박제. mechanical forcing function (어휘 emit 만 아닌 structural enforcement).

## Acceptance criteria

| AC | 설명 | 검증 |
|---|---|---|
| AC-3.1 | `templates/story-page-structure.md` `§ubiquitous_language` 섹션 신규 (Story 가 multi-BC 가로지를 시 explicit BC declare 의무) | `grep "§ubiquitous_language" templates/story-page-structure.md` |
| AC-3.2 | `plugin-codeforge-design/templates/change-plan.md` `§bounded_context_boundary` + `§affected_aggregates` block 신규 | `grep "§bounded_context_boundary" plugin-codeforge-design/templates/change-plan.md` + grep `§affected_aggregates` |
| AC-3.3 | `scripts/check-ddd-vocabulary.sh` 신설 (warning tier, ubiquitous-language-drift-check evidence-checks-registry entry) | `bash scripts/check-ddd-vocabulary.sh` exit code 0/1/2 + Smoke fixture pass |
| AC-3.4 | `scripts/check-bounded-context-presence.sh` 신설 (warning tier, bounded-context-presence-check entry) | `bash scripts/check-bounded-context-presence.sh` exit code |
| AC-3.5 | `scripts/check-ddd-pattern-frontmatter.sh` 신설 (warning tier, ddd-pattern-frontmatter-check entry) | `bash scripts/check-ddd-pattern-frontmatter.sh` exit code |
| AC-3.6 | `templates/github-workflows/{ubiquitous-language-drift,bounded-context-presence,ddd-pattern-frontmatter}.yml` 신설 + `.github/workflows/` self-app byte-identical copy | `diff templates/github-workflows/*.yml .github/workflows/*.yml` = 0 |
| AC-3.7 | `docs/evidence-checks-registry.yaml` 3 row append (warning tier, owner_adr: ADR-087) | yaml-lint pass + 3 신규 entry name match |
| AC-3.8 | `docs/inter-plugin-contracts/label-registry-v2.md` v2.37 → v2.38 MINOR bump + 3 신규 entry (`hotfix-bypass:ubiquitous-language-drift` 47번째 / `hotfix-bypass:bounded-context-presence` 48번째 / `hotfix-bypass:ddd-pattern-frontmatter` 49번째) | label-registry v2.38 version row + 3 신규 entry |
| **AC-INV-5-S3** | **template field + lint script Wave 1 wire = mechanical structure 변경 evidence (Wave 1 declaration-only 아닌 실 mechanism)** | 3 lint workflow trigger 실 PR 에 emit evidence |

## Test contract

- lint script 3 = bash test fixture (smoke + regression) + exit code 0/1/2 enum 정합 (ADR-060 framework)
- workflow 3 = PR-open trigger + `continue-on-error: true` (warning tier) + advisory comment
- evidence-checks-registry yaml = ADR-060 v1.1 schema 정합 (current_tier: warning, owner_adr: ADR-087, sibling_dependencies 명시)
- label-registry-v2 v2.38 = 3 신규 entry attach_owner_plugin: codeforge / category enum: hotfix-bypass / ADR-024 Amendment 가 family count update (현재 46번째 → 49번째)

## Dependencies

- S1 LAND (ADR-087 §결정 6 enforcement layer 3-tier 정합)
- precedent: label-registry-v2 v2.37 (현재) + evidence-checks-registry framework (ADR-060)

## Scope

### In
- Story template field 추가
- Change Plan template block 추가
- lint script 3 신설 + workflow 3 신설
- evidence-checks-registry 3 row + label-registry-v2 MINOR bump

### Out
- agent frontmatter field (S2)
- review-verdict enum (S4)
- skills/deputy-mandate Subdomain Specialist layer (S5)
- consumer CI gate (별 CFP)

## 5-checklist self-application

| Axis | 결과 |
|---|---|
| 1. 결정 영역 | template + lint — axis 1 영역 외 |
| 2. cost | N/A |
| 3. consumer impact | template field 추가 시 consumer overlay 충돌 0 (overlay = 확장만, 축소 불가) |
| 4. sibling cross-ref | ADR-087 charter + ADR-060 framework + label-registry-v2 정합 |
| 5. deferred carrier | consumer CI gate (별 CFP) |

**통과**.
