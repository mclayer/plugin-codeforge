---
kind: contract
contract: deploy_output
contract_version: "0.1"
status: Active  # Phase 1 = placeholder declare only (CFP-1059 / ADR-087). Body wire = S2 sub-Story carrier.
canonical_repo: mclayer/plugin-codeforge-deploy  # TBD — lane plugin seed 신설 후 wire
canonical_path: docs/inter-plugin-contracts/
created_by: CFP-1059
created_date: 2026-05-20  # KST
related_adrs:
  - ADR-087  # Deploy lane 신설 carrier
  - ADR-088  # Deploy Review lane (downstream consumer of deploy-output)
  - ADR-089  # Schema 변경 7 원칙 (deploy_output schema field 자체에도 적용)
  - ADR-008  # inter-plugin contract versioning
  - ADR-010  # sibling sync policy
authors:
  - CFP-1059 — Phase 1 placeholder declare only (2026-05-20)
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-deploy (lane plugin, producer — TBD S2 carrier)
  - codeforge-deploy-review (downstream consumer)
---

# deploy-output-v1

**상위 SSOT 위치**: 본 파일이 단일 원본 (canonical) — CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5. 기존 "TBD — lane seed 신설 후 wire" 는 monorepo 통합으로 계획 자체가 소멸 (해소). status Draft 유지 — Active 복귀는 deploy lane 별 carrier.

## 상태

**Phase 1 placeholder declare (CFP-1059 Epic Story-1)**. Body 본문 = S2 sub-Story carrier 영역 (codeforge-deploy plugin seed 신설 후 actual schema wire).

## 컨텍스트

CFP-1059 / [ADR-087](../../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) 가 Deploy lane (codeforge-deploy plugin) 정식 신설. DeployPLAgent / DeployWorkerAgent output → Orchestrator handoff schema 가 본 contract 영역.

## Phase 1 declarative anchor

본 file 은 Phase 1 declarative anchor only — actual schema (`deploy_output_v1` JSONSchema body) = S2 sub-Story carrier 가 wire. MANIFEST.yaml `contracts` block 안 `deploy_output` entry 가 본 file path 와 contract_version 0.1 (Draft) declare.

## 예상 schema field (S2 actual wire 영역)

S2 에서 다음 field group 이 정식 schema 로 author 될 영역:

- `repo_deploys[]` — 배포된 repo 단위 entry (image / atomic_swap_succeeded / healthcheck_result / rollback_triggered)
- `deploy_sequence_timeline[]` — blue-green sequence event timeline (KST `+09:00` ISO 8601, ADR-079 정합)
- `secret_provider_invocation[]` — 1Password Connect / .env fallback lookup audit
- `traefik_label_flip` — atomic swap event metadata
- `retention_window_timer` — 3-시간 보존 expiry timer (epoch + KST display)
- `auto_rollback_decision` — 자동 rollback trigger 여부 + 사유

## Versioning

- Phase 1 (본 file) = `0.1 Draft` (placeholder).
- Phase 2 (S2 sub-Story) = `1.0 Active` MAJOR bump (initial schema codify).
- ADR-008 §결정 1 정합: Draft → Active 전환 = MAJOR (semantically backward-compat starts at 1.0).

## Sibling sync (ADR-010)

본 contract = `canonical_repo: mclayer/plugin-codeforge-deploy` (lane plugin seed 신설 후 confirm). sibling sync 영역 7 plugin family (CFP-1059 후 9 plugin) 안에서 cross-plugin schema 의무 — S2 wire 시 ADR-010 §결정 1 정합.

## 본 Phase 1 의 deliverable

- `docs/inter-plugin-contracts/MANIFEST.yaml` 안 `contracts` block 신규 entry `deploy_output` declare (Phase 1 commit).
- 본 file path placeholder declare (body 본문 0 — Phase 1 anchor).
- S2 sub-Story carrier follow-up 의무 명시.
