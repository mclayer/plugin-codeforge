---
kind: registry
registry: reconcile-protocol
version: "1.2"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/reconcile-protocol-v1.md
date: 2026-05-15
authors:
  - ArchitectAgent (CFP-701 Wave 1 Story-1 carrier — declarative reconciliation upgrade flow schema SSOT)
  - DeveloperPLAgent (CFP-702 Wave 1 Story-2 Phase 2 — §4.3 (b) trigger 발동, marker_block_syntax_* fields 확장)
  - ArchitectPLAgent (CFP-743 Wave 2 Story-3 — §4.3 (c) trigger 발동, mechanical_implementation_binding block 신설 + KEY cross-ref 정정 CFP-703→CFP-743)
version_history:
  - { version: "1.0", date: 2026-05-15, carrier: CFP-701, change: "initial — declarative reconciliation upgrade flow schema SSOT. 9 영역 desired state enumeration + dry-run/snapshot/transaction 3 mode enum + customization preservation entry (marker block, Story-2 prerequisite) + version_handshake / reconcile_strategy placeholder reserve (Wave 4 carrier)." }
  - { version: "1.1", date: 2026-05-15, carrier: CFP-702, change: "§4.3 (b) trigger 발동 — Wave 1 Story-2 marker block syntax 확정. customization_preservation_entry 영역 확장: marker_block_syntax_* 4 fields 정식화 (comment prefix per-filetype / nesting_policy / lint_behavior / migration_script). ADR-027 Amendment 3 §결정 7.A-7.E verbatim cross-ref." }
  - { version: "1.2", date: 2026-05-15, carrier: CFP-743, change: "§4.3 (c) trigger 발동 — Wave 2 Story-3 UpgradeAgent + CLI 실 implementation hook (`scripts/codeforge-upgrade.{sh,ps1}` 신설). mechanical_implementation_binding block 신설 (§4.5 reference → CLI 3 mode entrypoint + UpgradeAgent Plan+Apply 책임 binding + reconcile PR open scope = ADR-066 Amendment 3 cross-ref). KEY cross-ref 정정: §4.3 (c) `CFP-703` → `CFP-743` (Wave 1 작성 시점 placeholder drift — 동일 Story, fact 영향 0 추적성 정정). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 invariant / atomicity_boundary semantic / transaction.completion_criterion 무변경 (ratchet 강화 only — ADR-064 §self-application 정합)." }
owner_adr: ADR-076
carrier_story: CFP-701
sibling_sync_exempt: true
related_adrs:
  - ADR-076  # 본 contract 의 carrier ADR
  - ADR-008  # versioning (registry MINOR/PATCH sibling sync 면제)
  - ADR-010  # sibling sync (kind:registry exempt)
  - ADR-016  # codeforge family scope 7 plugin atomic
  - ADR-027  # consumer adoption protocol (boundary disjoint)
  - ADR-038  # SessionStart hook static invariant
  - ADR-053  # 구조적 변경 재구동 + consumer 배포 (transaction completion prerequisite)
  - ADR-058  # ADR sunset criteria mandate
  - ADR-063  # marketplace atomic invariant
  - ADR-064  # decision principle mandate
  - ADR-067  # FIX ledger RESET (disjoint layer anchor)
related_files:
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md
  - docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md
  - docs/adr/ADR-016-marketplace-registration-policy.md
  - docs/adr/ADR-053-structural-change-restart-prerequisite.md
  - docs/adr/ADR-067-fix-ledger-implementability-escalation.md
related_plugins:
  - codeforge (wrapper, owner of reconcile execution semantic)
  - codeforge-requirements
  - codeforge-design
  - codeforge-review
  - codeforge-develop
  - codeforge-test
  - codeforge-pmo
---

# reconcile-protocol-v1 — Inter-plugin Contract Registry

codeforge family upgrade 의 declarative reconciliation 의 schema SSOT. wrapper SSOT 영역 (desired state) ↔ consumer overlay + plugin install (current state) ↔ customization marker block (preserved layer) 간 reconcile semantic + mode enum + placeholder field 정의.

**kind**: registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합)

## 1. 목적

### CFP-699 Epic §1 WHY carrier

사용자 directive (2026-05-14 KST):

> "한 번 명령 = 끝까지 자동 + 사용자 결정은 정해진 자리에서만 (= 0 자리). 단순 누락 방지가 아니라 결정 트리 자체를 박제 해서 매번 다르게 묻지 않게 하는 일."

본 contract = 결정 트리 박제의 mechanical SSOT carrier — dry-run/snapshot/transaction 3 mode enum + 결정 분기 0 invariant + customization preservation entry boundary.

### Cross-channel boundary

reconcile 어휘는 다음 영역에 동시 등장:

1. **wrapper plugin self-app**: `templates/github-workflows/*.yml` ↔ `.github/workflows/*.yml` byte-identical mirror (ADR-005)
2. **consumer overlay**: `.claude/_overlay/*` consumer customization ↔ wrapper SSOT desired state diff (ADR-027 boundary)
3. **plugin install state**: `.claude/plugins/installed_plugins.json` family 7 plugin version pin ↔ marketplace SSOT (ADR-016 + ADR-063)
4. **CI gate label**: phase:* ↔ gate:* ↔ severity:* (label-registry-v2 / severity-propagation-v1) — workflow desired state 정합

본 contract 4 영역의 reconcile semantic 일관성 보장 — drift 시 단일 진입점 (`scripts/codeforge-upgrade.{sh,ps1}` Wave 2 carrier) 의미 무너짐.

### 본 contract 의 범위 (in scope)

- 9 영역 desired state enumeration (ADR-076 §결정 2 verbatim mirror)
- dry-run / snapshot / transaction 3 mode enum semantic
- customization preservation entry boundary (marker block prerequisite — Story-2 carrier)
- snapshot ↔ ADR-067 RESET disjoint layer declare
- version_handshake placeholder (Wave 3 Story-6 carrier reserve)
- reconcile_strategy placeholder enum (Wave 4 E1/E2/E3 carrier reserve)
- atomicity_boundary semantic (per-plugin Story-1 scope, per-family Wave 2 Story-4 carrier)

### 본 contract 의 범위 외 (out of scope)

- marker syntax / lint script / migration script (Wave 1 Story-2 carrier — D4 customization marker)
- UpgradeAgent agent md / CLI script implementation (Wave 2 Story-3 carrier)
- 7 plugin atomic upgrade `scripts/atomic-upgrade-7-plugins.sh` (Wave 2 Story-4 carrier)
- 3-way merge runtime (overlay reconcile, Wave 2 Story-5 carrier)
- snapshot 안 sensitive data redaction policy (Wave 3 Story-7 carrier — branch protection)
- multi-version channel / codemod registry / uninstall (Wave 4 sub-Epic)

## 2. Schema

```yaml
# reconcile-protocol-v1 schema (declarative SSOT)
reconcile_protocol:
  version: "1.0"
  
  # === Desired state enumeration (ADR-076 §결정 2 verbatim) ===
  # domain_count: 9  [empirical-source: ADR-076 §결정 2 verbatim 9 영역 enumeration — FIX iter 1 / Codex TP#2 F-002 annotation]
  desired_state_domains:
    - { name: "github_workflow", source: "templates/github-workflows/*.yml", target: ".github/workflows/*.yml", mode: "byte_identical_mirror" }
    - { name: "session_start_hook", source: "hooks/hooks.json + hooks/session-start", target: "consumer overlay byte-identical", mode: "template_export" }
    - { name: "label_taxonomy", source: "docs/inter-plugin-contracts/label-registry-v2.md", target: "consumer bootstrap-labels.sh apply", mode: "declare_only_with_apply_script" }
    - { name: "settings_json_toggle", source: "templates/.claude/settings.json.sample", target: "consumer .claude/settings.json", mode: "template_export_with_merge" }
    - { name: "codeowners", source: "templates/CODEOWNERS.template", target: "consumer .github/CODEOWNERS", mode: "template_export_manual_instantiate" }
    - { name: "issue_templates", source: "templates/.github/ISSUE_TEMPLATE/*.yml", target: "consumer .github/ISSUE_TEMPLATE/*.yml", mode: "byte_identical_mirror" }
    - { name: "branch_protection", source: ".github/branch-protection-manifest.json", target: "consumer gh api apply", mode: "api_call_required" }
    - { name: "plugin_json_mirrored", source: ".claude-plugin/plugin.json [name, version, description, author]", target: "marketplace.json plugins[name=codeforge]", mode: "atomic_sync_required" }
    - { name: "changelog", source: "CHANGELOG.md", target: "wrapper repo SSOT", mode: "append_only_with_version_bump" }
  
  # === 3 mode enum (ADR-076 §결정 3 verbatim) ===
  mode_enum:
    dry_run:
      semantic: "desired state diff current state 계산 + 결과 preview (실 변경 0)"
      filesystem_touch: false
      network_call_allowed: true  # Helm-inspired `helm diff` pattern
      user_decision_branches: 0   # 정보 제공만, 후속 명령 사용자 별도 invocation
      scope: "9 desired_state_domains 모두"
      
    snapshot:
      semantic: "upgrade transaction pre-state sentinel — rollback 입력 state"
      automatic_creation_trigger: "--apply 직전"
      granularity_unit: "per_plugin"  # Story-1 scope runtime unit. per-family = Wave 2 Story-4 carrier ratchet 영역. [empirical-source: ADR-076 §결정 8 runtime v1.0 implementation table — FIX iter 1 / Codex TP#2 F-002 annotation]
      persistence_locations:
        primary: "consumer .claude/_snapshots/<UTC-timestamp>-<version-pre>.tar.gz"
        mirror: "wrapper docs/upgrade-events/<date>-<version>.md (event log audit trail)"
        secondary_future: "git tag (Wave 4 E1 multi-version channel carrier)"
      retention_policy:
        default: "N_most_recent"
        default_N: 5  # [empirical-source: derived default — Helm release history N=10 보다 보수적, codeforge family 7 plugin × N=5 = 35 file 보존 비용 vs rollback 가용성 절충, FIX iter 1 / Codex TP#2 F-002 annotation]
        configurable_via: "consumer .claude/_overlay/project.yaml upgrade.snapshot_retention_count"
        per_major_version: "Wave 4 E1 carrier reserve"
      coverage_scope: "9 desired_state_domains union (wrapper SSOT) - marker_block_inside (consumer customization)"
      
    transaction:
      semantic: "upgrade atomic unit — snapshot 생성 → apply → 사후 sanity check 단일 unit"
      # === atomicity_boundary 3-field split (FIX iter 1 / Codex TP#2 F-001 re-frame, 2026-05-15 KST) ===
      # 의미 invariant vs runtime implementation 두 영역 분리 declare (ADR-076 §결정 8 verbatim)
      atomicity_boundary_semantic_invariant: "family_7_plugin_atomic"  # [empirical-source: ADR-016 §결정 1 — wrapper + 6 lane plugin SSOT]. 본 invariant 자체는 본 contract 신설 영역 외 (ADR-016 SSOT).
      atomicity_boundary_runtime_v1: "per_plugin"  # Story-1 scope semantic SSOT only — Wave 2 Story-3 (UpgradeAgent + CLI) runtime carrier 영역.
      atomicity_boundary_runtime_future: "family_7_plugin"  # Wave 2 Story-4 carrier ratchet (`scripts/atomic-upgrade-7-plugins.sh` 신설 시점, 본 contract MINOR bump v1.0 → v1.1 의무).
      partial_failure_behavior: "automatic_rollback_to_snapshot"
      post_apply_sanity_check_failure_behavior: "automatic_rollback_to_snapshot"
      user_decision_branches: 0  # --apply 단일 명령
      completion_criterion:
        adr_053_d2_cross_ref: true
        adr_053_d2_verbatim_quote: |
          해당 구조적 변경이 codeforge plugin 자체의 변경인 경우, 재구동 범위에 consumer 배포 완료가 포함된다. consumer 배포 완료 전에는 consumer Story 작업 진입이 차단된다.
        # ADR-053 §D2 verbatim 정합 — FIX iter 1 / Codex TP#2 F-004 verbatim quote 분리. 동등 phrasing weakening 차단.
        marketplace_sync_pr_merged: required
        consumer_install_completed: required  # verbatim 명령 "/plugins install codeforge@mclayer" 또는 동등 effect (VSCode UI / npm script 등)
        version_drift_check_passed: required  # `bash scripts/check-codeforge-version-drift.sh` PASS
        dogfood_out_exemption: "codeforge-internal-docs scope (Wave 2 Story 패턴 — consumer 미배포 영역 N/A 명시 가능)"
  
  # === Customization preservation entry (Story-2 prerequisite cross-ref) ===
  customization_preservation_entry: "marker_block"  # Wave 1 Story-2 carrier (CFP-702) — D4 customization marker
  marker_block_syntax_carrier: "CFP-702"  # §4.3 (b) trigger 발동 완료 — marker syntax 확정
  marker_block_absent_behavior: "wholesale_mirror_with_user_visible_loss_report"
  # consumer 가 marker block 도입 전 customization 영역 = 본 Story-1 scope 안 fallback 정의 의무.
  # Story-2 carrier 의 retroactive migration script (scripts/migrate-existing-customization.sh) 가 사후 marker wrap mitigation.
  # === §4.3 (b) trigger 발동 — marker_block_syntax 영역 확장 (CFP-702 Phase 2, v1.0 → v1.1) ===
  marker_block_syntax:
    # ADR-027 Amendment 3 §결정 7.A.1 Axis 1 — file-type별 comment prefix variant
    comment_prefix_per_filetype:
      yml_yaml_sh: { begin: "# BEGIN wrapper-managed", end: "# END wrapper-managed" }
      md: { begin: "<!-- BEGIN wrapper-managed -->", end: "<!-- END wrapper-managed -->" }
      json: { kind: "sidecar_manifest", path: ".claude/_overlay/.wrapper-managed-manifest.json", carrier: "Wave 2 Story-5" }
    # ADR-027 Amendment 3 §결정 7.D.1 Axis 2 — nesting 정책
    nesting_policy: "flat_only"  # nested marker = lint reject (BEGIN...BEGIN...END...END = malformed)
    # ADR-027 Amendment 3 §결정 7.D — lint 행동
    lint_behavior:
      orphan_begin: "exit_nonzero"   # BEGIN 만 있고 END 없음 = malformed
      orphan_end: "exit_nonzero"     # END 만 있고 BEGIN 없음 = malformed
      reversed_order: "exit_nonzero" # END 가 BEGIN 보다 앞 = malformed
      nested: "exit_nonzero"         # nested marker pair = malformed
      normal_pair: "exit_zero"       # BEGIN ... END 정상 pair = PASS
    lint_script: "scripts/check-wrapper-managed-block.sh"
    lint_tier: "blocking-on-pr"      # ADR-027 §결정 7.F + ADR-060 §결정 5
    # ADR-027 Amendment 3 §결정 7.E.1 Axis 3 — migration false-positive boundary
    migration_script: "scripts/migrate-existing-customization.sh"
    migration_false_positive_boundary: "byte_diff_zero_AND_manifest_registered"
    migration_idempotency: "n_runs_equals_1_run_effect"  # Ansible blockinfile 동형
    dry_run_classified_as_decision_branch: false  # reconcile-protocol-v1 §4.3 + Epic §1 WHY "0 자리" 정합
  
  # === Snapshot ↔ ADR-067 RESET disjoint layer (Invariant carrier, ADR-076 §결정 4 verbatim) ===
  snapshot_reset_disjoint_layer:
    declared: true
    rationale: "같은 단어 RESET 이 다른 layer 에서 다른 의미. ADR-068 §결정 1 I-2 cross-module propagation completeness gap 회피."
    layer_mapping:
      adr_067_reset:
        layer: "story_progression"
        location: "Story §10 FIX Ledger RESET? column"
        meaning: "lane FIX cycle 의 cycle 재시작 표기 (RESET <lane> / cross-lane-pause:<lane>)"
      adr_076_snapshot:
        layer: "upgrade_transaction"
        location: "consumer .claude/_snapshots/ + wrapper docs/upgrade-events/"
        meaning: "upgrade pre-state sentinel — rollback 입력 state"
    cross_pollinate_forbidden: true
    declaration_locations:
      - "docs/adr/ADR-076-declarative-reconciliation-upgrade.md §결정 4"
      - "docs/inter-plugin-contracts/reconcile-protocol-v1.md (본 contract) snapshot_reset_disjoint_layer block"
      - "docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md Invariant 2"
  
  # === User decision branch = 0 invariant (CFP-699 Epic §1 WHY verbatim) ===
  user_decision_branches: 0
  cli_argument_fix:
    apply: "--apply"
    dry_run: "--dry-run"
    rollback: "--rollback <version>"
    no_prompt_invariant: true
    dry_run_classified_as_decision_branch: false  # 정보 제공만, 결정 분기 아님
  
  # === codeforge family scope (ADR-016 §결정 1 cross-ref) ===
  family_scope:
    unit_count: 7  # [empirical-source: ADR-016 §결정 1 — wrapper + 6 lane plugin (codeforge-requirements/design/review/develop/test/pmo) SSOT, FIX iter 1 / Codex TP#2 F-002 annotation]
    plugins:
      - codeforge          # wrapper
      - codeforge-requirements
      - codeforge-design
      - codeforge-review
      - codeforge-develop
      - codeforge-test
      - codeforge-pmo
    atomicity_carrier_story:
      story_1_scope: "per_plugin atomicity runtime v1.0 (semantic SSOT only)"
      wave_2_story_4_carrier: "family_7_plugin atomicity runtime ratchet (의미 invariant 변경 0 — ADR-016 §결정 1 unchanged)"
  
  # === Placeholder field (Wave 3/4 carrier reserve) ===
  # validation_status_v1_0 + becomes_normative_at_version 의무 (FIX iter 1 / Codex TP#2 F-003 — v1.0 validation semantic 명시)
  version_handshake:
    status: "placeholder_reserve"
    validation_status_v1_0: "non_normative_placeholder_reserve — v1.0 consumer ignore (validator skip 의무)"  # FIX iter 1 / Codex TP#2 F-003 annotation
    becomes_normative_at_version: "v1.1 (Wave 3 Story-6 carrier MINOR bump 시점)"
    carrier_story: "CFP-Wave-3-Story-6"  # 3-way version atomic invariant 확장
    semantic_intent: "wrapper plugin major version ↔ 6 lane plugin major version ↔ marketplace SSOT 3-way handshake"
    field_schema_future: "TBD (Wave 3 Story-6 carrier 시점 본 contract MINOR bump v1.0 → v1.1)"
  
  reconcile_strategy:
    status: "placeholder_reserve"
    validation_status_v1_0: "enum_current_v1_0 = normative (validator enforce). enum_reserved_wave_4 = non_normative_placeholder_reserve — v1.0 consumer ignore (validator skip 의무)"  # FIX iter 1 / Codex TP#2 F-003 annotation
    becomes_fully_normative_at_version: "v2.0 (Wave 4 sub-Epic carrier 시점 enum_reserved_wave_4 활성)"
    enum_current_v1_0:
      - "byte_identical_mirror"
      - "template_export"
      - "template_export_with_merge"
      - "declare_only_with_apply_script"
      - "api_call_required"
      - "atomic_sync_required"
      - "append_only_with_version_bump"
      - "template_export_manual_instantiate"
    enum_reserved_wave_4:
      - "codemod_apply"  # Wave 4 E2 carrier (jscodeshift-inspired)
      - "multi_version_channel_pin"  # Wave 4 E1 carrier (LTS vs latest)
      - "uninstall_cleanup"  # Wave 4 E3 carrier (reverse direction)

# === Placeholder field validation semantic SSOT (FIX iter 1 / Codex TP#2 F-003) ===
# 본 v1.0 contract validator (`scripts/check-inter-plugin-contracts.sh`) 의 placeholder field skip 의무:
# - status: "placeholder_reserve" 보유 field = validator schema validation skip (non-normative)
# - validation_status_v1_0 명시 의무 ("non_normative_placeholder_reserve — v1.0 consumer ignore" 또는 동등)
# - becomes_normative_at_version 명시 의무 (활성 carrier version)
# 본 SSOT = Wave 3 Story-6 carrier 시점 validator promotion path 의 prerequisite.
```

## 3. 항목

### 3.1 Mode enum behavior 규칙

#### Rule 3.1.1 — dry-run filesystem invariant

dry-run mode 에서 filesystem touch 0 — preview 출력만. consumer working tree 변경 0 보장. 본 invariant 위반 = HIGH severity (silent state mutation = user surprise).

#### Rule 3.1.2 — snapshot 자동 생성 의무

`--apply` 호출 시 snapshot 생성 = atomic transaction 의 첫 step. snapshot 생성 실패 시 apply 진행 금지 (rollback path 부재 = abort).

#### Rule 3.1.3 — transaction atomic boundary

partial 실패 시 자동 rollback. 사후 sanity check 실패 시 자동 rollback. 사용자 prompt 0 — `--apply` 단일 명령 안에서 모든 결정 진행.

### 3.2 Customization preservation 규칙

#### Rule 3.2.1 — marker block 안 영역 preserve invariant

`# BEGIN wrapper-managed` / `# END wrapper-managed` marker block 안 영역 = wrapper SSOT desired state target. marker block 밖 영역 = consumer customization = preserve.

본 marker syntax 정의 = Wave 1 Story-2 carrier (CFP-702). 본 contract = 영역 declare only, syntax 영역 외.

#### Rule 3.2.2 — marker block 부재 fallback

consumer 가 D4 marker block 도입 전 customization 영역 보유 시:
- snapshot 안 해당 file 전체 보존 (full backup)
- wholesale mirror 후 user-visible loss report 생성 (`docs/upgrade-events/<date>-<version>.md` 안 `## Wholesale mirror losses` § 명시)
- consumer 가 retroactive marker wrap 가능 (Wave 1 Story-2 carrier 의 `scripts/migrate-existing-customization.sh`)

### 3.3 Cross-references

- **ADR-076 §결정 1-8** (`docs/adr/ADR-076-declarative-reconciliation-upgrade.md`): 본 contract 의 carrier ADR. 모든 schema field 의 §결정 N verbatim mirror.
- **ADR-067 §결정 4 (Story progression layer RESET)**: 본 contract `snapshot_reset_disjoint_layer` block 의 cross-pollinate forbidden anchor.
- **ADR-053 §D2 (consumer 배포 포함)**: 본 contract `transaction.completion_criterion` 의 prerequisite 정의.
- **ADR-016 §결정 1 (codeforge family 7 plugin)**: 본 contract `family_scope` 의 unit_count = 7 정합.
- **ADR-063 §결정 5 (marketplace ↔ plugin.json atomic invariant)**: 본 contract `plugin_json_mirrored` domain 의 atomic_sync_required mode 정합.
- **ADR-038 Amendment 3 §결정 12 (SessionStart hook static invariant)**: 본 contract 의 detect/execute boundary 정합 — hook = detect only, UpgradeAgent + CLI = execute.
- **ADR-027 (consumer adoption protocol)**: trigger 시점 disjoint — ADR-027 = bootstrap detection + 3-trigger enforcement / 본 contract = upgrade event reconcile.
- **domain-knowledge `upgrade-flow/declarative-reconciliation.md`**: 본 contract 의 narrative SSOT anchor (3 Invariant + 4 책임 분리 + External pattern reference).

## 4. 변경 규칙

### 4.1 Versioning Policy

- **kind:registry**: MINOR / PATCH bump = sibling sync 면제 (ADR-010 §결정 2)
- **MAJOR bump**: 본 contract breaking change 시 별도 ADR Amendment 의무 (ADR-058 §결정 5 sunset_justification 적용)
- **Amendment trigger**: ratchet 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application)

### 4.2 SemVer rule (ADR-008 §결정 2 정합)

- **MAJOR**: `mode_enum` 3-value (dry-run/snapshot/transaction) 자체 breaking 변경 / `desired_state_domains` 영역 의미 breaking 변경 / `user_decision_branches: 0` invariant 약화 (= ADR-058 sunset_justification 차단) / `atomicity_boundary_semantic_invariant` 변경 (= ADR-016 §결정 1 변경 trigger 의무)
- **MINOR**: `desired_state_domains[]` row append (새 영역 enumeration) / `reconcile_strategy.enum_*` 값 추가 / `version_handshake` placeholder 활성화 (Wave 3 Story-6 carrier 시점) / `transaction.atomicity_boundary_runtime_v1` → `atomicity_boundary_runtime_future` ratchet (per_plugin → family_7_plugin Wave 2 Story-4 carrier 시점, 의미 invariant 변경 0)
- **PATCH**: 오타 / 설명 보강 / 예시 추가 / quantitative parameter empirical-source annotation 정정

### 4.3 Amendment trigger 조건

- (a) ADR-076 Amendment 시 (carrier ADR 변경 동반 의무)
- (b) Wave 1 Story-2 (CFP-702) merge — marker block syntax 확정 시 `customization_preservation_entry` 영역 확장
- (c) Wave 2 Story-3 (CFP-743) merge — UpgradeAgent + CLI 영역 mode_enum 실 implementation hook (`scripts/codeforge-upgrade.{sh,ps1}` 신설). **v1.2 발동 완료 (본 contract)** — §4.5 mechanical_implementation_binding block 신설. (Wave 1 작성 시점 placeholder `CFP-703` → 실제 발의 Issue `CFP-743` 정정. 동일 Story, fact 영향 0, 추적성만 정정 — ADR-068 I-4 wording SSOT 정합.)
- (d) Wave 2 Story-4 merge — `transaction.atomicity_boundary_runtime_v1` per_plugin → `atomicity_boundary_runtime_future` family_7_plugin ratchet (의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0)
- (e) Wave 3 Story-6 merge — `version_handshake` field 활성 (현재 placeholder_reserve, validation_status_v1_0: non_normative_placeholder_reserve)
- (f) Wave 4 sub-Epic merge — `reconcile_strategy.enum_reserved_wave_4` 값 활성

### 4.4 Ratchet 보존 의무 (downgrade 차단)

본 contract 의 모든 Amendment 는 강화 방향만 허용 (ADR-064 top-down self-application). 약화 방향 차단:

- `user_decision_branches: 0` invariant 약화 = ADR-058 §결정 5 sunset_justification 3-tuple 차단
- `snapshot_reset_disjoint_layer.declared: true → false` = 차단 (ADR-067 cross-pollinate risk)
- `transaction.completion_criterion.adr_053_d2_cross_ref: true → false` = 차단 (consumer 배포 누락 risk)
- `transaction.completion_criterion.adr_053_d2_verbatim_quote` modification = 차단 (FIX iter 1 / Codex TP#2 F-004 — verbatim weakening risk, ADR-053 §D2 SSOT 정합)
- `transaction.atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 약화 = ADR-016 §결정 1 변경 trigger 의무 (별도 carrier)
- `desired_state_domains[]` row 삭제 = 차단 (자기 영역 축소 = self-app coverage 후퇴)

### 4.5 Wave 2 Story-3 mechanical implementation 참조 (v1.2 — CFP-743 binding 발동)

본 contract 의 mechanical enforcement = `scripts/codeforge-upgrade.{sh,ps1}` (Wave 2 Story-3 carrier — CFP-743).

검증 mechanism (Wave 2 carrier 영역):
- mechanical pre-screen (9 영역 desired state diff)
- snapshot atomicity verification (per-plugin tarball integrity)
- transaction rollback path verification (snapshot restore dry-run)
- post-apply sanity check (workflow lint / hook signature / label registry 정합)

Phase 1 (CFP-743) merge 시 본 §4.5 binding block 활성 (schema declare). Phase 2 (별 PR) merge 시 CLI/UpgradeAgent 실 구현 + mechanical lint 활성.

#### mechanical_implementation_binding (v1.2 신설, CFP-743 §4.3 (c) 발동)

```yaml
mechanical_implementation_binding:
  carrier_story: CFP-743  # Wave 2 Story-3 (Wave 1 placeholder CFP-703 정정)
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = 실 script 구현
  cli_entrypoint:
    posix: "scripts/codeforge-upgrade.sh"
    powershell: "scripts/codeforge-upgrade.ps1"
    parity_invariant: "두 script 동일 reconcile semantic (9 desired_state_domains 동일 / 3 mode 동일 / user_decision_branches: 0 동일). parity 차이 = post-apply sanity check 검출 영역."
    path_form_invariant: "MSYS2 / Git-Bash `/c/` path-form 일관 정규화 의무 (CFP-702 normalize_path bug precedent 회피 — path-form mismatch = silent reconcile target miss = HIGH severity)."
  mode_dispatch:  # reconcile-protocol-v1 §2 mode_enum verbatim binding
    "--dry-run": "mode_enum.dry_run (filesystem_touch: false, network_call_allowed: true) — Helm `helm diff` 동형"
    "--apply": "mode_enum.transaction (snapshot 생성 → 9 영역 reconcile → post-apply sanity check 단일 atomic unit, partial_failure_behavior: automatic_rollback_to_snapshot)"
    "--rollback <version>": "mode_enum.snapshot restore (동일 snapshot scope re-application)"
  upgrade_agent_binding:
    agent_file: "templates/agents/UpgradeAgent.md"
    responsibility: "Plan + Apply (ADR-076 §결정 5 — SessionStart hook detect 책임 침범 0 invariant)"
    spawn_model: "Orchestrator default subagent one-shot (ADR-039 §결정 1 — 재귀 spawn 금지 platform inherent)"
  reconcile_pr_scope_binding:
    cross_ref: "ADR-066 Amendment 3 §결정 2 — reconcile-target-repos contents:write + pull_requests:write"
    pr_open_only: true   # silent direct push 금지 — consumer PR review gate 보존 (ADR-024 + ADR-027 정합)
    affected_domains:    # 9 desired_state_domains 중 consumer .github/ PR open 요구 영역
      - github_workflow            # byte_identical_mirror
      - issue_templates            # byte_identical_mirror
      - codeowners                 # template_export_manual_instantiate
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.2 = 강화 only, weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden
```

