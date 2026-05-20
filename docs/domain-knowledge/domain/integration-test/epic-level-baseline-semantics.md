---
kind: domain_fact
type: domain-knowledge
area: integration-test
topic_slug: epic-level-baseline-semantics
title: Integration Test — Epic-level baseline 자동 승격 semantic
status: Active
tags:
  - integration-test
  - epic-level-baseline
  - incremental-promotion
  - frozen-sha-pin
  - cross-story-consistency
  - cfp-954
related_adrs:
  - ADR-055  # Amendment 3 carrier (Epic-level baseline first activation)
  - ADR-044  # §결정 5 IntegrationTestAgent single-shot
  - ADR-073  # verify-before-assert (`frozen-SHA pin` discipline)
  - ADR-082  # write-time self-write verification
related_stories:
  - CFP-882  # parent Epic (Wave 4 sub-Epic)
  - CFP-954  # 본 carrier Story (Story-3)
  - CFP-906  # Wave 4 sub-Epic #882 Story-1 (baseline v1 story_keys 원천)
  - CFP-932  # Wave 4 sub-Epic #882 Story-2 (baseline v1 story_keys 원천)
created: 2026-05-18
updated: 2026-05-18
---

# Integration Test — Epic-level baseline 자동 승격 semantic

## 정의

Epic-level integration test baseline 의 **incremental promotion semantic** = Wave 4 sub-Epic #882 첫 사례 (CFP-954 carrier). 1 Epic 안 N Story 의 cross-Story consistency check 를 baseline yaml 로 stratified 고정 하고, Story 진행에 따라 v1 → v2 → v3 으로 append-only 승격하는 패턴.

본 entry = ADR-055 Amendment 3 의 narrative SSOT — IntegrationTestAgent / ArchitectAgent / QADeveloperAgent / 후속 Wave carrier 가 참조하는 단일 정의.

## 컨텍스트

이전 Wave 1/2/3 Epic = Story-level integration test only (Epic-level baseline 부재). Wave 4 sub-Epic #882 = 처음으로 Epic-level cross-Story consistency check baseline 도입. 향후 Epic 의 standard pattern 영역 (ADR-055 Amendment 3 SSOT).

3-step incremental promotion (Helm chart versioning + Pact contract version 답습):

| Stage | Story | Baseline version | scope |
|---|---|---|---|
| **declare** | Story-3 (CFP-954, 본 Story) | v1 | declarative-only (story_keys 3 + frozen_shas + CSC 3 entry, executable bats/pytest 0) |
| **runtime** | Story-4 (TBD) | v2 | promotion criteria 4-tuple executable baseline (canary→beta promotion gate) |
| **최종 고정** | Story-5 (TBD) | v3 | downgrade asymmetry invariant executable + Wave 4 sub-Epic close gate |

## 핵심 규칙

### 1. Frozen-SHA 고정 discipline (ADR-073 verify-before-assert)

baseline yaml 안 `frozen_shas` 4-tuple (wrapper main + wrapper cfp-<key> merge + internal-docs main + internal-docs cfp-<key> merge) — direct `gh api repos/.../commits/<sha> --jq .sha` verify 의무 (self-claim SHA 금지).

Wave 4 sub-Epic #882 baseline v1 (CFP-954):
- CFP-906 wrapper merge: `126fa6ab` (verified via memory project_cfp_906_phase_1_pr_open + project_cfp_882_wave4_brainstorm)
- CFP-906 internal-docs merge: `2e6e6446`
- CFP-932 wrapper admin-merge: `72f9bfc6` (memory project_cfp_932_design_lane_pause)
- CFP-932 internal-docs merge: `a5bdbb24`
- CFP-954 wrapper merge: `TBD` (populate at Phase 2 PR merge time, OpRiskArch §D.1 race window catch)
- CFP-954 internal-docs merge: `TBD`

### 2. Append-only stratified 고정 pattern (DataMigrationArch §G.5)

baseline v1 / v2 / v3 schema = **append-only stratified 고정**:
- v2 = v1.frozen_shas verbatim copy + Story-4 own frozen_shas append
- v3 = v2.frozen_shas verbatim copy + Story-5 own frozen_shas append + Wave 4 sub-Epic close gate evidence

Story-4 carrier script (Phase 2 carrier 영역) = v2 generation 시점 v1 content immutable verify 의무 — baseline self-hash invariant (OpRiskArch §G.4 권고 — `baseline_yaml_sha: <self-content-sha256>` self-hash field, Story-4 carrier).

### 3. Cross-Story consistency check 3 entry (CSC-1/2/3)

baseline-v1-cfp-954.yaml 의 declarative-only check 3 entry (mandate activation scope only, 실 verify = Story-4 promotion script):

- **CSC-1: label-registry-v2 sequential MINOR bump** — v2.30 (CFP-906) → v2.31 (CFP-932) → v2.32 (CFP-923, parallel sibling 영역 외 Wave 4) → v2.33 (CFP-954). sequential MINOR sequence integrity + 4 bump rows in amendment_log.
- **CSC-2: ADR-72 amendment_log monotonic increment** — Amendment 1 (CFP-651, 2026-05-14) → Amendment 2 (CFP-954, 2026-05-18). carrier_story field monotonic invariant + amendment_number monotonic.
- **CSC-3: reconcile-protocol-v1 schema version cross-Story consistency** — v1.7 (CFP-906 + CFP-898 dual-carrier) → v1.8 (CFP-932) → 본 Story-3 = v1.8 cross-ref only (변경 0건). Story-3 = production cutover layer disjoint axis (declare scope, runtime UpgradeAgent multi-channel dispatch = Story-2 영역).

## 경계

### Race window catch (OpRiskArch §D.1)

Story-4 / Story-5 carrier 시점 baseline v2 / v3 promotion script 가 v1 frozen_shas reference → race window 3종:
1. **Wrapper main HEAD advance race**: Story-3 merge 후 다른 PR (CFP-953 etc) 가 wrapper main 진행 → baseline-v1 `wrapper_main` SHA = stale → Story-4 promotion 시점 stale-base check
2. **Internal-docs main HEAD advance race**: 동일 패턴 internal-docs
3. **Cross-repo atomicity gap**: wrapper PR merge ↔ internal-docs PR merge 시간차 (sequential ADR-008 §결정 2 정합) → 두 main SHA pair 가 다른 timestamp

Mitigation: baseline yaml schema `pin_timestamp_kst` + `pin_verified_via` field (declarative SSOT) + Story-4 promotion script SHA 고정 verify (`baseline_yaml_sha` self-hash invariant 영역).

### Story-level vs Epic-level disjoint

Story-level integration test (`tests/integration/<story-key>/`, QADeveloperAgent Phase 2 PR, per-Story FIX 루프) 와 Epic-level baseline (`tests/integration/stories/<EPIC_KEY>/`, IntegrationTestAgent single-shot, Epic close gate) 은 양 layer disjoint axis. 본 entry = Epic-level 한정. Story-level 은 README.md 표 참조.

## 관련 ADR

- **ADR-055 Amendment 3** — Epic-level baseline first activation SSOT (CFP-954 carrier)
- **ADR-044 §결정 5** — IntegrationTestAgent single-shot pattern (test lane = single subagent)
- **ADR-073** — verify-before-assert (`frozen-SHA pin` discipline, self-claim SHA 금지)
- **ADR-082** — write-time self-write verification mandate (frozen_shas value 사실성 source direct verify)

## 변경 이력

| 날짜 (KST) | Story | 변경 |
|---|---|---|
| 2026-05-18 | CFP-954 | 최초 작성 — Wave 4 sub-Epic #882 Story-3 Epic-level baseline 자동 승격 semantic 정의 (3-step incremental promotion + frozen-SHA 고정 + append-only stratified 고정 + CSC 3 entry + race window catch) |
