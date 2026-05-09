<!-- DO NOT EDIT - auto-generated from docs/doc-locations.yaml -->
<!-- Regenerate: ./scripts/check-doc-locations.sh --regen -->

# Doc Location Registry (auto-generated)

**Source SSOT**: [`docs/doc-locations.yaml`](doc-locations.yaml)  
**schema_version**: 1.0  
**Last regen**: 2026-05-09T13:25:28Z  
**Registered doc types**: 10

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
  - mctrader-hub/docs/stories/MCT-112.md (multi_repo_hub — story_scope: hub, CFP-342 / ADR-050)
  - mctrader-data/docs/stories/MCT-001.md (multi_repo_impl — story_scope: repo, CFP-342 / ADR-050)
  - mclayer/codeforge-internal-docs/wrapper/stories/CFP-273.md (dogfood)

  **notes**:
  > §1 Issue 본문 verbatim invariant (story-section-1-immutable.yml).
  > ADR-020 Mode A: 각 작업 repo 가 자체 보유. Mode B: hub 가 모두 보유.
  > ADR-013: codeforge family = internal-docs <plugin>/stories/.
  > CFP-342 / ADR-050: multi_repo_hub (story_scope: hub) + multi_repo_impl (story_scope: repo)
  > = ADR-020 Mode B 의 automation backbone. Hub repo 의 project.yaml 에 codeforge.stories.repos[]
  > 블록 활성 시 trigger. mode_b vs multi_repo_hub 구분 = 자동화 layer 활성 여부 (mode_b = manual,
  > multi_repo_hub = automation). 향후 Phase 2 mechanism 구현 후 mode_b → multi_repo_hub
  > 자연스러운 evolution.
  > <impl-repo> placeholder = project.yaml codeforge.stories.repos[].name (ADR-050 §결정 1).

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

  **notes**:
  > Mode-agnostic. DomainAgent self-write owner path (CFP-26 Phase 0a).

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

