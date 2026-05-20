# [CFP-1117-S4] review-verdict-v4 enum 확장 (Phase 2 PR3)

**parent_epic**: CFP-1117  
**LAND order**: Phase 2 PR3 (depends on S1, S3)

## WHY

`docs/inter-plugin-contracts/review-verdict-v4.md` 현재 v4.7 → v4.8 MINOR bump. finding type 3 enum 신설:

- `bc_violation` — review-verdict-v4 finding 이 BC boundary 위반 감지
- `aggregate_violation` — Aggregate consistency boundary 위반 감지 (governance BC Layer A Authority Pair invariant 또는 application BC DDD Aggregate root invariant 위반)
- `ubiquitous_language_drift` — Ubiquitous Language SSOT (glossary.md) 와 agent / Story / Change Plan / ADR 안 어휘 drift 감지

**Vocabulary theater 차단 evidence (INV-5 binding)**: review-verdict finding type 3 enum 신설 = "review findings type 변경 evidence" 직접 박제. semantic accountability mechanism — 어휘 emit 만 아닌 reviewer 가 검출 가능한 explicit finding type.

## Acceptance criteria

| AC | 설명 | 검증 |
|---|---|---|
| AC-4.1 | `docs/inter-plugin-contracts/review-verdict-v4.md` v4.7 → v4.8 MINOR bump + frontmatter `version: 4.8` + amendment_log entry | `grep "version: 4.8" docs/inter-plugin-contracts/review-verdict-v4.md` |
| AC-4.2 | finding type 3 enum 신설 — `findings[].type` enum 안 `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` 추가 | `grep "bc_violation\|aggregate_violation\|ubiquitous_language_drift" docs/inter-plugin-contracts/review-verdict-v4.md` ≥ 3 hit |
| AC-4.3 | `docs/inter-plugin-contracts/MANIFEST.yaml` review-verdict-v4 row version field 4.7 → 4.8 update | yaml-lint pass + version field match |
| AC-4.4 | 6 plugin sibling sync (ADR-010 §결정 1 의무) — codeforge-design / codeforge-develop / codeforge-review / codeforge-test / codeforge-requirements / codeforge-pmo 안 review-verdict-v4 reference 갱신 | 6 plugin grep `review-verdict-v4` version reference = v4.8 |
| AC-4.5 | DesignReviewPL + CodeReviewPL + SecurityTestPL 3 PL 가 3 신규 finding type emit 가능 — review-pl-base.md (codeforge-review templates/) verbatim update | `grep "bc_violation\|aggregate_violation\|ubiquitous_language_drift" plugin-codeforge-review/templates/review-pl-base.md` ≥ 3 |
| **AC-INV-5-S4** | **review-verdict finding type 3 enum 신설 = review findings type 변경 evidence (INV-5 5 영역 중 4번째 영역 직접 박제)** | golden-path S6 안 실 emit 사례 1건 이상 cross-validation |

## Test contract

- review-verdict-v4 schema = JSON Schema v0.4 validation pass (3 신규 enum literal valid)
- 6 plugin sibling sync = ADR-010 §결정 1 + sibling_dependencies field 의무
- MANIFEST.yaml version field bump = sibling sync window 의무 (ADR-008 §결정 1)
- review-pl-base.md update = ADR-007 review responsibility 정합

## Dependencies

- S1 LAND (ADR-087 §결정 6 enforcement layer 3-tier 정합)
- S3 LAND (lint warning tier wire 후 review-verdict enum 발화 검출 가능 보장)
- precedent: review-verdict-v4 v4.7 + 6 plugin atomic sibling sync 패턴 안정 (CFP-1086 / CFP-991 등 정합)

## Scope

### In
- review-verdict-v4 v4.7 → v4.8 MINOR bump
- MANIFEST.yaml row update
- 6 plugin sibling sync
- review-pl-base.md update

### Out
- template field (S3)
- skills/deputy-mandate Subdomain Specialist layer (S5)
- golden-path worked example (S6)
- consumer CI gate (별 CFP)

## 5-checklist self-application

| Axis | 결과 |
|---|---|
| 1. 결정 영역 | inter-plugin contract MINOR bump — axis 1 영역 외 |
| 2. cost | N/A |
| 3. consumer impact | 6 plugin 동시 LAND 의무 (sibling sync, ADR-010) |
| 4. sibling cross-ref | ADR-087 + ADR-008 (versioning) + ADR-010 (sibling sync) |
| 5. deferred carrier | consumer CI gate (별 CFP) |

**통과**.
