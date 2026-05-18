---
title: Integration Test — Epic-level reactivation narrative SSOT hub
area: integration-test
introduced_by: CFP-954
parent_epic: CFP-882
status: active
date: 2026-05-18
related_adrs:
  - ADR-055  # Amendment 3 — Epic-level baseline first activation
  - ADR-044  # §결정 5 — IntegrationTestAgent single-shot pattern
  - ADR-048  # CI-native test execution + Amendment 1 DeveloperPL diagnosis
  - ADR-041  # doc location registry (integration_test_baseline 15th entry)
  - ADR-073  # verify-before-assert (frozen-SHA pin discipline)
  - ADR-082  # write-time self-write verification mandate
related_files:
  - docs/adr/ADR-055-integration-test-lane-policy.md
  - docs/doc-locations.yaml
  - tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml
  - docs/domain-knowledge/domain/integration-test/epic-level-baseline-semantics.md
---

# Integration Test — Epic-level reactivation narrative SSOT hub

본 페이지 = codeforge wrapper 의 **Integration Test lane Epic-level reactivation 운영 narrative SSOT** (CFP-954 carrier, Wave 4 sub-Epic #882 Story-3 — IntegrationTestAgent Epic-level reactivation first activation 영역). ADR-055 Amendment 3 + ADR-044 §결정 5 cross-ref hub.

## 1. Story-level vs Epic-level disjoint axis

ADR-055 §결정 3 (Story-level) + Amendment 3 (Epic-level) 정합 — 양 layer disjoint axis:

| 항목 | Story-level integration test | Epic-level baseline |
|---|---|---|
| Scope | 1 Story component boundary | Epic 안 N Story cross-Story consistency check |
| Path | `tests/integration/<story-key>/` | `tests/integration/stories/<EPIC_KEY>/baseline-v<N>-<carrier-key>.yaml` |
| Carrier | QADeveloperAgent (Phase 2 PR) | IntegrationTestAgent (single-shot read-only verify) |
| Trigger | CI gate post-merge | Epic close gate pre-merge |
| Schema | docker-compose.test.yml dynamic 실행 | declarative-only baseline (Story-3 v1) + executable (Story-4 v2 / Story-5 v3) |
| Verdict | test-verdict-v2.1 (per-Story) | cross_story_consistency_checks (per-Epic) |
| Failure mode | per-Story FIX 루프 (구현 vs 설계 분기) | Epic-wide regression (multi-Story dependency) |

Story-level integration test 와 Epic-level baseline 은 양 layer 동시 존재 가능 (codeforge family plugin distribution 의 양 axis 정합).

## 2. IntegrationTestAgent single-shot pattern (ADR-044 §결정 5)

ADR-044 §결정 5 — test lane = single subagent (codeforge-test plugin). IntegrationTestAgent = single-shot Agent tool spawn → return (env=0 fallback + env=1 동일).

declarative-only baseline = single-shot read-only verify (실 spawn 0건, Story-3 = mandate activation scope only). Story-4 / Story-5 carrier 시점 executable baseline 진입 (per-Story Phase 2 commit 시 IntegrationTestAgent spawn).

## 3. Epic-level baseline 자동 승격 semantic

CFP-954 carrier — Wave 4 sub-Epic #882 첫 사례:
- **Story-3 merge = baseline v1** (declarative-only, story_keys [CFP-906, CFP-932, CFP-954] + frozen_shas + CSC 3 entry)
- **Story-4 merge = baseline v2** (promotion criteria 4-tuple executable baseline)
- **Story-5 merge = baseline v3 final pin** (downgrade asymmetry invariant + Wave 4 sub-Epic close gate)

Naming convention (DataMigrationArch §G.5): `baseline-v<N>-<carrier-key>.yaml` immutable append-only (기존 v1 file 보존, history immutable, Story-4 promotion script self-hash verify 의무).

## 4. Pact contract testing precedent (Researcher §A.3 정합)

Epic-level integration test = **contract testing** (Pact precedent) framing 가능. baseline 자동 승격 = contract version pin discipline.

- Provider ↔ consumer contract verification — codeforge family plugin 의 inter-plugin-contracts versioning (`MANIFEST.yaml`) 답습
- Pact `pact_broker` = baseline yaml repository (codeforge family = git-tracked `tests/integration/stories/<EPIC_KEY>/`)
- Pact `verification_event` = Story-3 Phase 2 PR merge 시점 cross_story_consistency_checks 실행

Cross-ref additional external anchor:
- Selenium / Playwright E2E test suite — 전체 user journey test (cross-feature)
- Cypress component test vs e2e split — 1 Story = component / Epic = e2e

## 5. ADR-055 Amendment 3 (CFP-954 carrier)

ADR-055 §결정 1-9 + Amendment 1 (ADR-048 deprecated → codeforge-test 부활) + Amendment 2 (Integration Test lane policy refinement) → Amendment 3 (CFP-954 — Epic-level baseline first activation):

- doc-locations.yaml 15th entry `integration_test_baseline` 신설 (ADR-041 §결정 1 정합)
- baseline-v<N>-<carrier-key>.yaml immutable append-only naming
- Story-level vs Epic-level disjoint axis 명시
- declarative-only baseline first (Story-3) → executable (Story-4 / Story-5) incremental promotion

## 6. Cross-ref

- `epic-level-baseline-semantics.md` — Epic-level baseline 자동 승격 semantic + Wave 4 sub-Epic #882 첫 사례
- ADR-055 Amendment 3 SSOT
- ADR-044 §결정 5 single-shot pattern
- `tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml` (Epic-level baseline first entry)
- Pact contract testing documentation
