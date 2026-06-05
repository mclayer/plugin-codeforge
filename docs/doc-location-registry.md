<!-- DO NOT EDIT - auto-generated from docs/doc-locations.yaml -->
<!-- Regenerate: ./scripts/check-doc-locations.sh --regen -->

# Doc Location Registry (auto-generated)

**Source SSOT**: [`docs/doc-locations.yaml`](doc-locations.yaml)  
**schema_version**: 1.2  
**Last regen**: 2026-06-05T00:54:04Z  
**Registered doc types**: 17

## Summary table

| # | doc_type | variants | owner | introduced_by |
|---|---|---|---|---|
| 1 | `epic_results` | dogfood / mode_a / mode_b / mode_c | `codeforge-pmo:PMOAgent` | CFP-83 |
| 2 | `story_file` | dogfood / mode_b / multi_repo_hub / multi_repo_impl / single_repo | `codeforge-requirements:RequirementsPLAgent` | CFP-1 |
| 3 | `adr` | confluence / dogfood / single_repo | `codeforge-design:ArchitectAgent` | CFP-26 |
| 4 | `change_plan` | confluence / dogfood / single_repo | `codeforge-design:ArchitectAgent` | CFP-7 |
| 5 | `retro` | confluence / dogfood / single_repo | `codeforge-pmo:PMOAgent` | CFP-36 |
| 6 | `domain_knowledge` | confluence / single_repo | `codeforge-requirements:DomainAgent` | CFP-37 |
| 7 | `spec` | dogfood | `orchestrator` | ADR-017 |
| 8 | `plan` | dogfood | `orchestrator` | ADR-017 |
| 9 | `decision_packet` | dogfood | `orchestrator` | CFP-61 |
| 10 | `inter_plugin_contract` | confluence / single_repo | `each_lane_plugin` | CFP-29 |
| 11 | `evidence_check_registry` | single_repo | `orchestrator` | CFP-389 |
| 12 | `upgrade_events` | single_repo | `orchestrator` | CFP-743 |
| 13 | `kpi_artifact` | single_repo | `orchestrator` | CFP-393 |
| 14 | `integration_test_baseline` | single_repo | `codeforge-test:IntegrationTestAgent` | CFP-954 |
| 15 | `architecture_doc` | confluence / dogfood / single_repo | `codeforge-design:ArchitectAgent` | CFP-919 |
| 16 | `promotion_criteria_4tuple_artifact` | single_repo | `codeforge-design:ArchitectAgent` | CFP-991 |
| 17 | `orchestrator_playbook` | confluence / single_repo | `orchestrator` | CFP-1668 |

## Per-doc-type details

### `epic_results`

- **mode_a**: `<owner-repo>/docs/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **mode_b**: `<hub-repo>/docs/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **mode_c**: `<hub-repo>/docs/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **owner_agent**: `codeforge-pmo:PMOAgent`
- **introduced_by**: CFP-83
- **naming_pattern**: `EPIC-RESULTS-[A-Z]+-[0-9]+\.md`
- **frontmatter_required**: False
- **examples**:
  - mctrader-hub/docs/retros/EPIC-RESULTS-MCT-12.md (Mode B)
  - mclayer/codeforge-internal-docs/wrapper/retros/EPIC-RESULTS-CFP-96.md (dogfood)

  **notes**:
  > Phase N+1 close PR 이 merge 되는 repo 의 docs/retros/.
  > ADR-020 Mode A → owner / Mode B/C → hub. dogfood (codeforge family) → internal-docs <plugin>/retros/.
  > mode_a/b/c + dogfood 모두 <scope>/[docs/]retros/ 단일 패턴 (ADR-041 Amendment 1, 2026-05-09).
  > EPIC-RESULTS = retro-like artifact (Epic close evidence aggregate, Codex round 1 verdict).

### `story_file`

- **single_repo**: `<owner-repo>/docs/stories/<KEY>.md`
- **mode_b**: `<hub-repo>/docs/stories/<KEY>.md`
- **multi_repo_hub**: `<hub-repo>/docs/stories/<KEY>.md`
- **multi_repo_impl**: `<impl-repo>/docs/stories/<KEY>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/stories/<KEY>.md`
- **owner_agent**: `codeforge-requirements:RequirementsPLAgent`
- **introduced_by**: CFP-1
- **naming_pattern**: `[A-Z]+-[0-9]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mctrader-hub/docs/stories/MCT-12.md (Mode B legacy hub-flat)
  - mctrader-hub/docs/stories/MCT-112.md (multi_repo_hub — story_scope: hub, CFP-342 / ADR-069)
  - mctrader-data/docs/stories/MCT-001.md (multi_repo_impl — story_scope: repo, CFP-342 / ADR-069)
  - mclayer/codeforge-internal-docs/wrapper/stories/CFP-273.md (dogfood)

  **notes**:
  > §1 Issue 본문 verbatim invariant (story-section-1-immutable.yml).
  > ADR-020 Mode A: 각 작업 repo 가 자체 보유. Mode B: hub 가 모두 보유.
  > ADR-013: codeforge family = internal-docs <plugin>/stories/.
  > CFP-342 / ADR-069: multi_repo_hub (story_scope: hub) + multi_repo_impl (story_scope: repo)
  > = ADR-020 Mode B 의 automation backbone. Hub repo 의 project.yaml 에 codeforge.stories.repos[]
  > 블록 활성 시 trigger. mode_b vs multi_repo_hub 구분 = 자동화 layer 활성 여부 (mode_b = manual,
  > multi_repo_hub = automation). 향후 Phase 2 mechanism 구현 후 mode_b → multi_repo_hub
  > 자연스러운 evolution.
  > <impl-repo> placeholder = project.yaml codeforge.stories.repos[].name (ADR-069 §결정 1).

### `adr`

- **single_repo**: `<owner-repo>/docs/adr/ADR-NNN-<slug>.md`
- **dogfood**: `archive/adr/ADR-NNN-<slug>.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-26
- **naming_pattern**: `ADR-[0-9]{3}-[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge/archive/adr/ADR-020-cross-repo-epic-pattern.md  # wrapper 자기 ADR — prune 후 archive/adr/ 로 이동
  - mctrader-hub/docs/adr/ADR-001-example.md  # 소비자 일반 관례 = docs/adr/

  **notes**:
  > Mode-agnostic. 소비자(consumer) repo 의 ADR 는 docs/adr/ 가 일반 관례.
  > 예외: plugin-codeforge(wrapper) 자기 ADR 은 prune 이후 archive/adr/ 로 이동.
  > 소비자는 dogfood 예외에 영향받지 않음 — single_repo variant(docs/adr/) 사용.
  > CODEOWNERS = architect team review 의무.
  > confluence variant (CFP-1256 / ADR-103 §결정 5 R2): git→Confluence one-way sync readable mirror.
  > 실 Confluence URL = consumer overlay project.yaml atlassian.confluence.base_url + space_key + page_id 주입.
  > git = SoR-work invariant (ADR-100 §결정 1) — Confluence 는 readable mirror 이지 SoR 아님.
  > CFP-1420 / ADR-111 §결정 1 — confluence_variant sub-tree 활성 (mirror 대상 closed-enum 4 영역). page_id stamp = Sub-B 영역 sync engine.

### `change_plan`

- **single_repo**: `<owner-repo>/docs/change-plans/<slug>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/change-plans/<slug>.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-7
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mctrader-hub/docs/change-plans/mct-12-historical-data-bridge.md
  - mclayer/codeforge-internal-docs/wrapper/change-plans/cfp-83-epic-results.md

  **notes**:
  > ADR-013: codeforge family = internal-docs <plugin>/change-plans/.
  > confluence variant (CFP-1256 / ADR-103 §결정 5 R2): dogfood-out docs (MOVE path, ADR-013) 의 Confluence readable mirror. git = SoR-work invariant.
  > CFP-1420 / ADR-111 §결정 1 — confluence_variant sub-tree 활성 (mirror 대상 closed-enum 4 영역).

### `retro`

- **single_repo**: `<owner-repo>/docs/retros/<sprint>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/retros/<sprint>.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `codeforge-pmo:PMOAgent`
- **introduced_by**: CFP-36
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/codeforge-internal-docs/wrapper/retros/zeta-arc-2026-04-29.md
  - mctrader-hub/docs/retros/EPIC-RESULTS-MCT-12.md (Mode B EPIC-RESULTS, ADR-041 Amendment 1)

  **notes**:
  > ADR-013: codeforge family dogfood. EPIC-RESULTS 도 본 디렉터리 사용 (mode_a/b/c + dogfood 통일, ADR-041 Amendment 1).
  > Sprint retro (`<sprint>.md`) 와 EPIC-RESULTS (`EPIC-RESULTS-<KEY>.md`) 는 prefix 로 명확히 구분.
  > confluence variant (CFP-1256 / ADR-103 §결정 5 R2): dogfood-out docs (MOVE path, ADR-013) 의 Confluence readable mirror. git = SoR-work invariant.

### `domain_knowledge`

- **single_repo**: `<owner-repo>/docs/domain-knowledge/<area>/<topic>.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `codeforge-requirements:DomainAgent`
- **introduced_by**: CFP-37
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mctrader-hub/docs/domain-knowledge/exchange/bithumb-rest-api.md
  - mclayer/plugin-codeforge/docs/domain-knowledge/domain/codex-collaboration/README.md (CFP-946-A — ADR-052/070/081 narrative SSOT hub)
  - mclayer/plugin-codeforge/docs/domain-knowledge/domain/codex-collaboration/substitution-scope-decision-tree.md (CFP-946-A)
  - mclayer/plugin-codeforge/docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md (CFP-1523 / CFP-1588 — DD-4 category → lane bucket mapping rule SSOT, lane filter curatorial enhancement, cross-ref Sub-Epic CFP-949 6 lane plugin self-owned architecture doc seed)

  **notes**:
  > Mode-agnostic. DomainAgent self-write owner path (CFP-26 Phase 0a).
  > CFP-946-A — `codex-collaboration/` sub-tree 신설 (ADR-052/070/081 narrative SSOT hub).
  > Write owner extension = ArchitectAgent (codex-collaboration sub-tree = governance narrative).
  > CFP-1420 / ADR-111 §결정 1 — confluence variant + confluence_variant sub-tree 신설 (mirror 대상 closed-enum 4 영역 정합). git = SoR-work invariant (ADR-100 §결정 1).
  > CFP-1588 (FU-1523-3 묶음 F-DR-010) — `governance-principle/adr-category-lane-mapping.md` example row append (curatorial enhancement, CFP-1523 카테고리 → lane bucket mapping rule SSOT). cross-ref Sub-Epic CFP-949 6 lane plugin self-owned architecture doc seed (CFP-968~973) — lane bucket allocation 의 architecture doc anchor 영역.

### `spec`

- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/specs/<slug>.md`
- **owner_agent**: `orchestrator`
- **introduced_by**: ADR-017
- **naming_pattern**: `[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/codeforge-internal-docs/wrapper/specs/2026-05-08-issue-276-doc-location-registry-design.md

  **notes**:
  > ADR-017 codeforge family override. Default 'docs/superpowers/specs/' 는 plugin repo 에서 CI fail-closed.
  > Consumer 는 default 사용.

### `plan`

- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/plans/<slug>.md`
- **owner_agent**: `orchestrator`
- **introduced_by**: ADR-017
- **naming_pattern**: `[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+\.md`
- **frontmatter_required**: False
- **examples**:
  - mclayer/codeforge-internal-docs/wrapper/plans/2026-05-08-issue-276-doc-location-registry.md

  **notes**:
  > ADR-017 codeforge family override.

### `decision_packet`

- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/decisions/<packet_id>.yaml`
- **owner_agent**: `orchestrator`
- **introduced_by**: CFP-61
- **naming_pattern**: `[a-z0-9-]+\.yaml`
- **frontmatter_required**: False
- **examples**:
  - mclayer/codeforge-internal-docs/wrapper/decisions/<packet_id>.yaml

  **notes**:
  > CFP-61 / ADR-022 Sonnet decider full v2.1 schema (decision-packet-v2.1).

### `inter_plugin_contract`

- **single_repo**: `<owner-repo>/docs/inter-plugin-contracts/<slug>-v<version>.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `each_lane_plugin`
- **introduced_by**: CFP-29
- **naming_pattern**: `[a-z0-9-]+-v[0-9]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v3.md

  **notes**:
  > Canonical 은 producer plugin repo. wrapper 는 sibling sync mirror (ADR-010).
  > MANIFEST.yaml 가 별도 SSOT — 본 entry 는 위치 룰만.
  > confluence variant (CFP-1256 / ADR-103 §결정 5 R2): wrapper governance docs (KEEP path, ADR-013) 의 Confluence readable mirror. git = SoR-work invariant.

### `evidence_check_registry`

- **single_repo**: `<owner-repo>/docs/evidence-checks-registry.yaml`
- **owner_agent**: `orchestrator`
- **introduced_by**: CFP-389
- **naming_pattern**: `evidence-checks-registry\.yaml`
- **frontmatter_required**: False
- **examples**:
  - mclayer/plugin-codeforge/docs/evidence-checks-registry.yaml

  **notes**:
  > ADR-060 carrier — evidence-enforceable promotion framework registry data SSOT.
  > Schema doc = docs/inter-plugin-contracts/evidence-check-registry-v1.md (kind:registry).
  > MANIFEST.yaml `registries:` 블록 entry = `evidence_check_registry` (versioning 추적).
  > parallel-edit policy = append-only (docs/parallel-work/section-ownership.yaml).
  > Write owner = Orchestrator + carrier Story ArchitectAgent (wrapper governance).

### `upgrade_events`

- **single_repo**: `<owner-repo>/docs/upgrade-events/<version>.md`
- **owner_agent**: `orchestrator`
- **introduced_by**: CFP-743
- **naming_pattern**: `[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9.-]+\.md`
- **frontmatter_required**: False
- **examples**:
  - mclayer/plugin-codeforge/docs/upgrade-events/2026-05-15-5.74.0.md

  **notes**:
  > CFP-743 Wave 2 Story-3 (Epic CFP-699) carrier — C2 upgrade event log artifact.
  > reconcile-protocol-v1 v1.2 snapshot.persistence_locations.mirror = 본 디렉터리
  > (`docs/upgrade-events/<date>-<version>.md` — snapshot mirror + reconcile 결과 audit trail).
  > Naming = `<date>-<version>.md` (date = upgrade transaction 시점 KST, version = 도달 plugin version).
  > Schema = `templates/upgrade-event.md` (Phase 2 carrier — UpgradeAgent 자동 생성).
  > Write owner = UpgradeAgent (`--apply` transaction 완료 시 자동 생성, 사용자 manual edit 금지).
  > marker block 부재 시 `## Wholesale mirror losses` § 포함 (reconcile-protocol-v1 Rule 3.2.2).
  > Phase 1 = doc type 등록 + `docs/upgrade-events/.gitkeep` 영역 신설 (CFP-743 Phase 1).
  > Phase 2 = `templates/upgrade-event.md` schema + UpgradeAgent 자동 생성 로직 (별 PR).
  > parallel-edit policy = append-only (event log = immutable audit trail).

### `kpi_artifact`

- **single_repo**: `<owner-repo>/docs/kpi/<slug>.json`
- **owner_agent**: `orchestrator`
- **introduced_by**: CFP-393
- **naming_pattern**: `[a-z0-9-]+\.json`
- **frontmatter_required**: False
- **examples**:
  - mclayer/plugin-codeforge/docs/kpi/rate-limit-fallback.json

  **notes**:
  > CFP-388 evidence-enforceable framework 의 runtime metric measurement 결과 JSON.
  > ADR-057 Amendment 2 (CFP-393) 가 첫 사례 — rate-limit-fallback.json.
  > Write owner = cron workflow auto-PR (사용자 manual edit 금지 — parallel-work/section-ownership.yaml
  > append-only policy + comment workflow-only-write semantic).
  > Lint scope = JSON valid (jq parse) + invariant (분자 ≤ 분모 등, aggregator 가 강제).
  > 향후 history 누적 정책 별도 carrier (CFP-393 §11 follow-up #4).

### `integration_test_baseline`

- **single_repo**: `<owner-repo>/tests/integration/stories/<EPIC_KEY>/baseline-v<N>-<carrier-key>.yaml`
- **owner_agent**: `codeforge-test:IntegrationTestAgent`
- **introduced_by**: CFP-954
- **naming_pattern**: `baseline-v[0-9]+-cfp-[0-9]+\.yaml`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge/tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml (Wave 4 sub-Epic #882 first Epic-level baseline, declarative-only)

  **notes**:
  > CFP-954 (Wave 4 sub-Epic #882 Story-3) carrier — ADR-055 Amendment 3 (Epic-level baseline first activation) + ADR-72 §결정 1 (ProductionEvidenceDeputy mandate first activation) 동반.
  > Epic-level integration test baseline 자동 승격 SSOT (Story-level vs Epic-level disjoint axis).
  > Story-level integration test (`tests/integration/<story-key>/`) ≠ Epic-level baseline (`tests/integration/stories/<EPIC_KEY>/`) — 양 layer 동시 존재 가능.
  > Naming convention: `baseline-v<N>-<carrier-key>.yaml` immutable append-only (DataMigrationArch §G.5 정합 — v1/v2/v3 incremental promotion + 기존 v1 file 보존, history immutable).
  > Story-3 = v1 (declarative-only, story_keys cross-Story consistency check 3 entry + frozen_shas 고정 discipline ADR-073 정합).
  > Story-4 = v2 (promotion criteria 4-tuple executable baseline 진입).
  > Story-5 = v3 (downgrade asymmetry invariant + Wave 4 sub-Epic close final 고정).
  > frontmatter_required = true (carrier_story + story_keys + frozen_shas + cross_story_consistency_checks + declarative_only field 의무).
  > IntegrationTestAgent single-shot pattern (ADR-044 §결정 5 정합) — declarative baseline = single-shot read-only verify (실 spawn 0건, mandate activation scope only).
  > parallel-edit policy = locked (IntegrationTestAgent monopoly + integration-test lane verdict gate).

### `architecture_doc`

- **single_repo**: `<owner-repo>/docs/architecture/<topic>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/architecture/<topic>.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-919
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge/docs/architecture/codeforge-family.md (wrapper family overview seed — CFP-919 baseline + CFP-1427 Sub-C S3.3 5-anchor expand + 7→8 plugin family update)
  - mclayer/plugin-codeforge-requirements/docs/architecture/codeforge-requirements.md (CFP-968)
  - mclayer/plugin-codeforge-design/docs/architecture/codeforge-design.md (CFP-969 + CFP-1086-S4 mctrader 5 repo cross-layer evidence)
  - mclayer/plugin-codeforge-develop/docs/architecture/codeforge-develop.md (CFP-970)
  - mclayer/plugin-codeforge-review/docs/architecture/codeforge-review.md (CFP-971)
  - mclayer/plugin-codeforge-test/docs/architecture/codeforge-test.md (CFP-972)
  - mclayer/plugin-codeforge-pmo/docs/architecture/codeforge-pmo.md (CFP-973)
  - mclayer/plugin-codeforge-deploy/docs/architecture/codeforge-deploy.md (CFP-1059 declarative Phase 1 — plugin repo 신설 = S2 sub-Story carrier, body wire deferred)
  - mclayer/plugin-codeforge-deploy-review/docs/architecture/codeforge-deploy-review.md (CFP-1059 declarative Phase 1 — plugin repo 신설 = S3 sub-Story carrier, body wire deferred)
  - mclayer/codeforge-internal-docs/wrapper/architecture/wrapper-overview.md (dogfood)

  **notes**:
  > CFP-919 (Epic B Story-1) carrier — ADR-078 (살아있는 구조 설계 문서 유지 정책 SSOT).
  > Story key 독립 (고정 경로 docs/architecture/) + 누적 현재 상태 SSOT.
  > 4 영역 closed-enum: 모듈 / 경계 / 인터페이스 계약 / 데이터 흐름.
  > 라인 수준 (클래스/함수/변수) 금지 — anti-scope guard (ADR-078 §결정 1).
  > 각 plugin self-owned (single_repo + dogfood variant 양 지원, Q1 derived default 정합).
  > ADR-076 declarative reconciliation 3-layer pattern 재사용 (desired/current/converge).
  > Change Plan (델타) 와 상보 관계 — disjoint SSOT (ADR-078 §결정 3).
  > Write owner = ArchitectAgent (codeforge-design lane chief author).
  > Phase 1 (CFP-919) = doc type 등록 + ADR-078 anchor 만. template schema = S2 (#920) carrier.
  > lane 게이트 = S3 (#921) carrier. drift lint = S4 (#923) carrier.
  > parallel-edit policy = locked (architecture_doc = ArchitectAgent monopoly + design lane verdict gate).
  > Sub-Epic CFP-949 (2026-05-18) — 6 lane plugin self-owned seed (codeforge-{requirements,design,develop,review,test,pmo}) 추가, closing-the-loop 7 seed completion (wrapper 1 + lane 6).
  > CFP-1059 / ADR-087+088 (2026-05-23) — Deploy lane + Deploy Review lane 신설 declarative Phase 1.
  > 8 lane plugin family 확장 (6 → 8). 신규 2 plugin (codeforge-deploy + codeforge-deploy-review) self-owned arch doc
  > examples row 신설 (declarative placeholder — plugin repo 신설 자체 = S2/S3 sub-Story carrier).
  > CFP-1427 (Sub-C S3.3 / Mega-Epic CFP-1415 Sub-C bundle CFP-1418) — wrapper family.md 5-anchor section schema expand
  > (ADR-078 Amendment 2 §결정 3 closed-enum: arc42 §3 Context+Scope / arc42 §5 Building Block / C4 Container /
  > C4 Component / Open Decisions Pending). 6 lane plugin self-owned arch doc 5-anchor expand = follow-up sub-CFP 6
  > carrier (cross-repo per-plugin write 영역, ADR-040 worktree-first invariant 정합 sequential carrier 분리).
  > Mermaid/PlantUML diagram-as-code 의무 (ADR-111 §결정 4 + ADR-078 Amd 2 §결정 4) — Confluence native macro 회피.

### `promotion_criteria_4tuple_artifact`

- **single_repo**: `<owner-repo>/docs/domain-knowledge/domain/production-cutover/promotion-criteria-4tuple.md`
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-991
- **naming_pattern**: `promotion-criteria-4tuple\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge/docs/domain-knowledge/domain/production-cutover/promotion-criteria-4tuple.md (CFP-991 Wave 4 sub-Epic #1 Story-4 canary promotion criteria 4-tuple SSOT — 4 industry exemplar primary Chrome 3-channel Stable/Beta/Canary + npm dist-tag + Rust 3-channel + K8s 3-stage 보조)

  **notes**:
  > CFP-991 (Wave 4 sub-Epic #1 Story-4) carrier — ADR-72 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding sibling carrier.
  > promotion criteria 4-tuple SSOT artifact = functional + security + monitoring + testing 4 measurement source 의 codeforge 도메인 mapping (canary → beta promotion gate evaluation 기준).
  > 4 industry exemplar verbatim cite (ADR-076 §결정 9.6 SSOT): Chrome 3-channel Stable/Beta/Canary primary (Chrome 4-channel 변종 도입 0건 invariant) + npm dist-tag latest/next/canary 보조 + Rust 3-channel stable/beta/nightly 보조 + K8s 3-stage GA/Beta/Alpha 보조.
  > 추가 reference (sub-bullet): K8s KEP-5241 (Implementing User Friendly Production Readiness, 2024-12) + AWS CodeDeploy Blue-Green Linear/Canary deployment + Helm release lifecycle.
  > Write owner = ArchitectAgent (codeforge-design lane chief author).
  > Phase 1 (CFP-991) = doc type 등록 + ADR-72 Amendment 3 + ADR-076 §결정 9.6 anchor.
  > Story-4 = enforcement layer carrier (declare-only) — Story-5 (별 CFP) = downgrade asymmetry invariant declarative carrier (canary → beta → stable demotion path).
  > parallel-edit policy = serialized (canary_compatibility_check section-ownership.yaml + ArchitectAgent monopoly).
  > family_7_atomic × channel × promotion gate 3-axis cross-product = wrapper Tier-1 declare-time exemption (ADR-72 §결정 6 invariant 정합) + consumer Tier-2 admin-tier 권장 (boundary 2-tier disjoint).

### `orchestrator_playbook`

- **single_repo**: `<owner-repo>/docs/orchestrator-playbook.md`
- **confluence**: `https://<confluence-instance>/wiki/spaces/<space-key>/pages/<page-id>`
- **owner_agent**: `orchestrator`
- **introduced_by**: CFP-1668
- **naming_pattern**: `orchestrator-playbook\.md`
- **frontmatter_required**: False
- **examples**:
  - mclayer/plugin-codeforge/docs/orchestrator-playbook.md (wrapper canonical)

  **notes**:
  > CFP-1668 / ADR-111 Amendment 2 §결정 1 carrier — 5번째 mirror 대상 신설.
  > wrapper canonical = mclayer/plugin-codeforge/docs/orchestrator-playbook.md (단일 SSOT).
  > consumer 는 project.yaml atlassian.confluence.mirror_targets 에 orchestrator_playbook 추가로 mirror 활성.
  > git = SoR-work invariant (ADR-100 §결정 1) — Confluence 는 readable mirror (단방향, 역방향 edit 금지).
  > confluence_variant sub-tree: consumer_applicable: true (ADR-083 §결정 1 — 4-way enum `consumer` 해당).
  > mirror 대상 closed-enum: [adr, architecture_doc, change_plan, domain_knowledge, orchestrator_playbook] 완결 (ADR-111 Amendment 2 §결정 1 5-tuple).
  > parallel-edit policy = append-only (playbook = governance narrative, Orchestrator owner).
  > Phase 1 (CFP-1668) = doc type 등록 + ADR-111 Amendment 2 §결정 1 carrier. Sub-B sync = Wave 2 별 carrier.

