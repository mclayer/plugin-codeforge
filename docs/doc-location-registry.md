<!-- DO NOT EDIT - auto-generated from docs/doc-locations.yaml -->
<!-- Regenerate: ./scripts/check-doc-locations.sh --regen -->

# Doc Location Registry (auto-generated)

**Source SSOT**: [`docs/doc-locations.yaml`](doc-locations.yaml)  
**schema_version**: 1.0  
**Last regen**: 2026-05-17T23:53:35Z  
**Registered doc types**: 14

## Summary table

| # | doc_type | variants | owner | introduced_by |
|---|---|---|---|---|
| 1 | `epic_results` | dogfood / mode_a / mode_b / mode_c | `codeforge-pmo:PMOAgent` | CFP-83 |
| 2 | `story_file` | dogfood / mode_b / multi_repo_hub / multi_repo_impl / single_repo | `codeforge-requirements:RequirementsPLAgent` | CFP-1 |
| 3 | `adr` | single_repo | `codeforge-design:ArchitectAgent` | CFP-26 |
| 4 | `change_plan` | dogfood / single_repo | `codeforge-design:ArchitectAgent` | CFP-7 |
| 5 | `retro` | dogfood / single_repo | `codeforge-pmo:PMOAgent` | CFP-36 |
| 6 | `domain_knowledge` | single_repo | `codeforge-requirements:DomainAgent` | CFP-37 |
| 7 | `spec` | dogfood | `orchestrator` | ADR-017 |
| 8 | `plan` | dogfood | `orchestrator` | ADR-017 |
| 9 | `decision_packet` | dogfood | `orchestrator` | CFP-61 |
| 10 | `inter_plugin_contract` | single_repo | `each_lane_plugin` | CFP-29 |
| 11 | `evidence_check_registry` | single_repo | `orchestrator` | CFP-389 |
| 12 | `upgrade_events` | single_repo | `orchestrator` | CFP-743 |
| 13 | `kpi_artifact` | single_repo | `orchestrator` | CFP-393 |
| 14 | `architecture_doc` | dogfood / single_repo | `codeforge-design:ArchitectAgent` | CFP-919 |

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
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-26
- **naming_pattern**: `ADR-[0-9]{3}-[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge/docs/adr/ADR-020-cross-repo-epic-pattern.md

  **notes**:
  > Mode-agnostic. ADR 는 항상 plugin repo / consumer repo 의 docs/adr/.
  > CODEOWNERS = architect team review 의무.

### `change_plan`

- **single_repo**: `<owner-repo>/docs/change-plans/<slug>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/change-plans/<slug>.md`
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-7
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mctrader-hub/docs/change-plans/mct-12-historical-data-bridge.md
  - mclayer/codeforge-internal-docs/wrapper/change-plans/cfp-83-epic-results.md

  **notes**:
  > ADR-013: codeforge family = internal-docs <plugin>/change-plans/.

### `retro`

- **single_repo**: `<owner-repo>/docs/retros/<sprint>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/retros/<sprint>.md`
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

### `domain_knowledge`

- **single_repo**: `<owner-repo>/docs/domain-knowledge/<area>/<topic>.md`
- **owner_agent**: `codeforge-requirements:DomainAgent`
- **introduced_by**: CFP-37
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mctrader-hub/docs/domain-knowledge/exchange/bithumb-rest-api.md
  - mclayer/plugin-codeforge/docs/domain-knowledge/domain/codex-collaboration/README.md (CFP-946-A — ADR-052/070/081 narrative SSOT hub)
  - mclayer/plugin-codeforge/docs/domain-knowledge/domain/codex-collaboration/substitution-scope-decision-tree.md (CFP-946-A)

  **notes**:
  > Mode-agnostic. DomainAgent self-write owner path (CFP-26 Phase 0a).
  > CFP-946-A — codex-collaboration sub-tree 신설 (ADR-052/070/081 narrative SSOT hub).
  > Write owner extension = ArchitectAgent (codex-collaboration sub-tree = governance narrative).

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
- **owner_agent**: `each_lane_plugin`
- **introduced_by**: CFP-29
- **naming_pattern**: `[a-z0-9-]+-v[0-9]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v3.md

  **notes**:
  > Canonical 은 producer plugin repo. wrapper 는 sibling sync mirror (ADR-010).
  > MANIFEST.yaml 가 별도 SSOT — 본 entry 는 위치 룰만.

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

### `architecture_doc`

- **single_repo**: `<owner-repo>/docs/architecture/<topic>.md`
- **dogfood**: `mclayer/codeforge-internal-docs/<plugin-folder>/architecture/<topic>.md`
- **owner_agent**: `codeforge-design:ArchitectAgent`
- **introduced_by**: CFP-919
- **naming_pattern**: `[a-z0-9-]+\.md`
- **frontmatter_required**: True
- **examples**:
  - mclayer/plugin-codeforge/docs/architecture/codeforge-family.md
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

