---
kind: contract
contract: deploy_review_output
contract_version: "0.1"
status: Active  # Phase 1 = placeholder declare only (CFP-1059 / ADR-088). Body wire = S3 sub-Story carrier.
canonical_repo: mclayer/plugin-codeforge-deploy-review  # TBD — lane plugin seed 신설 후 wire
canonical_path: docs/inter-plugin-contracts/
created_by: CFP-1059
created_date: 2026-05-20  # KST
related_adrs:
  - ADR-088  # Deploy Review lane 신설 carrier
  - ADR-087  # Deploy lane (upstream producer of deploy-output, deploy-review-output consumer)
  - ADR-068  # boundary completeness invariants (I-5 dimensional empirical grounding — 성능 측정 기준)
  - ADR-059  # debate-protocol-v1 (성능 미충족 시 cross-module debate trigger)
  - ADR-072  # ProductionEvidenceDeputy mandate (ownership 이관 mirror)
  - ADR-008  # inter-plugin contract versioning
  - ADR-010  # sibling sync policy
authors:
  - CFP-1059 — Phase 1 placeholder declare only (2026-05-20)
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-deploy (upstream producer of deploy-output)
  - codeforge-deploy-review (lane plugin, producer — TBD S3 carrier)
---

# deploy-review-output-v1

**상위 SSOT 위치**: `mclayer/plugin-codeforge-deploy-review/docs/inter-plugin-contracts/deploy-review-output-v1.md` (TBD — S3 sub-Story 신설 후 wire)

## 상태

**Phase 1 placeholder declare (CFP-1059 Epic Story-1)**. Body 본문 = S3 sub-Story carrier 영역 (codeforge-deploy-review plugin seed 신설 후 actual schema wire).

## 컨텍스트

CFP-1059 / [ADR-088](../adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) 가 Deploy Review lane (codeforge-deploy-review plugin) 정식 신설. DeployReviewPLAgent / DeployReviewWorkerAgent output → Orchestrator handoff schema 가 본 contract 영역.

## Phase 1 declarative anchor

본 file 은 Phase 1 declarative anchor only — actual schema (`deploy_review_output_v1` JSONSchema body) = S3 sub-Story carrier 가 wire. MANIFEST.yaml `contracts` block 안 `deploy_review_output` entry 가 본 file path 와 contract_version 0.1 (Draft) declare.

## 예상 schema field (S3 actual wire 영역)

S3 에서 다음 field group 이 정식 schema 로 author 될 영역:

- `smoke_verdict` — 양방향 호환 smoke (ADR-089 §결정 4) 결과 (PASS / FIX / PARTIAL)
- `performance_comparison` — production runtime measure ↔ pre-deploy baseline 비교 결과 (latency / throughput / error_rate 3-tuple, `[empirical-source: ...]` annotation 의무 — ADR-068 I-5 정합)
- `cutover_post_evidence_quad` — ProductionEvidenceDeputy 4 prerequisite measurement source (ADR-072 §결정 1-2 — functional / security / monitoring / testing)
- `debate_artifact_ref` — performance 미충족 시 debate-protocol-v1 transcript anchor (Story §9 link)
- `fix_dispatch_target` — FIX 발생 시 routing (DeveloperPL / ArchitectPL / RequirementsPL — debate-protocol-v1 multi-round 가능)
- `production_evidence_deputy_ownership_transfer_log` — codeforge-design CONDITIONAL → codeforge-deploy-review 정식 이관 audit (ADR-088 §결정 3)

## Versioning

- Phase 1 (본 file) = `0.1 Draft` (placeholder).
- Phase 2 (S3 sub-Story) = `1.0 Active` MAJOR bump (initial schema codify).
- ADR-008 §결정 1 정합: Draft → Active 전환 = MAJOR.

## Sibling sync (ADR-010)

본 contract = `canonical_repo: mclayer/plugin-codeforge-deploy-review` (lane plugin seed 신설 후 confirm). sibling sync 영역 9 plugin family (CFP-1059 후) 안에서 cross-plugin schema 의무 — S3 wire 시 ADR-010 §결정 1 정합.

## debate-protocol-v1 trigger (ADR-088 §결정 4)

DeployReviewPL = debate-protocol-v1 (CFP-391 / ADR-059) trigger 의무 — performance 미충족 시 RequirementsPL ↔ ArchitectPL ↔ DeveloperPL 3-way multi-round adversarial debate 자동 발동. 본 contract output 의 `debate_artifact_ref` field 가 transcript anchor link 보유 (Story §9 append-only 영역).

## ProductionEvidenceDeputy ownership 이관 (ADR-088 §결정 3)

ADR-072 정의 ProductionEvidenceDeputy = 현재 codeforge-design CONDITIONAL deputy. CFP-1059 / ADR-088 §결정 3 가 ownership 을 codeforge-deploy-review 로 정식 이관:

- mandate body 자체는 보존 (ADR-072 §결정 1-7 그대로 — 4 prerequisite measurement source enforcement)
- ownership 만 이전 (axis 정합: production 환경 평가 = production 환경 lane 영역, 설계 lane 의 design 결정 layer 와 axis 불일치)

## 본 Phase 1 의 deliverable

- `docs/inter-plugin-contracts/MANIFEST.yaml` 안 `contracts` block 신규 entry `deploy_review_output` declare (Phase 1 commit).
- 본 file path placeholder declare (body 본문 0 — Phase 1 anchor).
- S3 sub-Story carrier follow-up 의무 명시.
