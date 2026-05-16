---
kind: registry
registry: reconcile-protocol
version: "1.4"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/reconcile-protocol-v1.md
date: 2026-05-15
authors:
  - ArchitectAgent (CFP-701 Wave 1 Story-1 carrier — declarative reconciliation upgrade flow schema SSOT)
  - DeveloperPLAgent (CFP-702 Wave 1 Story-2 Phase 2 — §4.3 (b) trigger 발동, marker_block_syntax_* fields 확장)
  - ArchitectPLAgent (CFP-743 Wave 2 Story-3 — §4.3 (c) trigger 발동, mechanical_implementation_binding block 신설 + KEY cross-ref 정정 CFP-703→CFP-743)
  - ArchitectPLAgent (CFP-744 Wave 2 Story-4 — §4.3 (d) trigger 발동, atomicity_boundary_runtime per_plugin → family_7_plugin ratchet 활성 + stale placeholder 정정 v1.0→v1.1 → v1.2→v1.3)
  - ArchitectPLAgent (CFP-745 Wave 2 Story-5 — §4.3 (g) trigger 신설 발동, §4.7 overlay_reconcile_implementation_binding block 신설 + marker_block_syntax.json carrier → realized_in cross-ref (§2.5 FORM 옵션 (i)))
version_history:
  - { version: "1.0", date: 2026-05-15, carrier: CFP-701, change: "initial — declarative reconciliation upgrade flow schema SSOT. 9 영역 desired state enumeration + dry-run/snapshot/transaction 3 mode enum + customization preservation entry (marker block, Story-2 prerequisite) + version_handshake / reconcile_strategy placeholder reserve (Wave 4 carrier)." }
  - { version: "1.1", date: 2026-05-15, carrier: CFP-702, change: "§4.3 (b) trigger 발동 — Wave 1 Story-2 marker block syntax 확정. customization_preservation_entry 영역 확장: marker_block_syntax_* 4 fields 정식화 (comment prefix per-filetype / nesting_policy / lint_behavior / migration_script). ADR-027 Amendment 3 §결정 7.A-7.E verbatim cross-ref." }
  - { version: "1.2", date: 2026-05-15, carrier: CFP-743, change: "§4.3 (c) trigger 발동 — Wave 2 Story-3 UpgradeAgent + CLI 실 implementation hook (`scripts/codeforge-upgrade.{sh,ps1}` 신설). mechanical_implementation_binding block 신설 (§4.5 reference → CLI 3 mode entrypoint + UpgradeAgent Plan+Apply 책임 binding + reconcile PR open scope = ADR-066 Amendment 3 cross-ref). KEY cross-ref 정정: §4.3 (c) `CFP-703` → `CFP-743` (Wave 1 작성 시점 placeholder drift — 동일 Story, fact 영향 0 추적성 정정). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 invariant / atomicity_boundary semantic / transaction.completion_criterion 무변경 (ratchet 강화 only — ADR-064 §self-application 정합)." }
  - { version: "1.3", date: 2026-05-16, carrier: CFP-744, change: "§4.3 (d) trigger 발동 완료 — Wave 2 Story-4 7-plugin family atomic upgrade runtime (`scripts/atomic-upgrade-7-plugins.sh` 신설). `transaction.atomicity_boundary_runtime_v1` per_plugin → `atomicity_boundary_runtime_future` family_7_plugin runtime catch-up ACTIVE (ADR-076 §결정 8 pre-designated ratchet). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — runtime catch-up only). ADR-037 Amendment 1 (atomic upgrade 후 0 drift invariant) carrier 동반. stale placeholder 정정: 본 contract line 144 comment + ADR-076 line 147 의 'MINOR bump v1.0 → v1.1 의무' (Wave 1 작성 시점 placeholder — v1.1/v1.2 신설 전 작성된 stale text) → 실제 'v1.2 → v1.3 (Wave 2 Story-4)' 정정 (CFP-743 CFP-703→CFP-743 정정 패턴 답습, fact 영향 0 추적성만 — ADR-068 I-4 wording SSOT 정합). schema field 명 `_future` 유지 (field-name stability — ratchet 활성은 comment + version_history + §4.3 (d) marker 로 표기, §4.3 (c) v1.2 패턴 동형). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary_semantic_invariant / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — ADR-064 §self-application 정합)." }
  - { version: "1.4", date: 2026-05-16, carrier: CFP-745, change: "§4.3 (g) trigger 신설 발동 완료 — Wave 2 Story-5 overlay 영역 (skill/agent/hook) 3-way merge reconcile runtime (`scripts/reconcile-overlay.sh` 신설, Phase 2 carrier). §4.7 `overlay_reconcile_implementation_binding` block 신설 (per-file 3-way merge layer base/wrapper-new/consumer-current + marker_preserve_binding marker 안=wrapper-new mirror·밖=consumer-current byte-identical preserve + sidecar_manifest_schema RFC 6901 JSON Pointer key-path allowlist + base_acquisition_binding Story-3 snapshot wrapper-managed 영역 재사용). marker_block_syntax.comment_prefix_per_filetype.json `carrier: \"Wave 2 Story-5\"` → `realized_in: \"§4.7 overlay_reconcile_implementation_binding.sidecar_manifest_schema\"` cross-ref 추가 (carrier reservation → realized — ADR-027 §결정 7.A.1 carrier 실현, AC-10 contract integration OUTCOME). carrier key 유지 (field-name stability — consumer schema key 의존 보존, ADR-068 I-4). Story-3 §4.5/§4.6 (c)/(d) trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — overlay coverage 확장, ADR-064 §self-application 정합). [FIX Iter 2 — Codex TP#2 P1 verified-true: base_acquisition_binding 에 orthogonality_invariant + base_state_resolution(base_ok/base_corrupt/base_absent) 추가 + base_absent_first_reconcile 정정 (base 가용성 ≠ marker scope orthogonal 분리 — base 부재+MARKER_VALID = marker-aware 2-way first-reconcile marker 밖 byte-identical preserve / MARKER_NONE base무관 = wholesale_mirror / base corrupt = abort. 초기 'base 부재 = marker 부재 fallback 동형' conflation 정정). v1.4 schema 정정 — MINOR 유지, ratchet 강화 only (base_absent 가 marker_absent 와 분리됨을 명시 = 강화, marker_block_absent_behavior/user_decision_branches:0 무변경).]" }
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

본 contract = `결정 트리 박제` (CFP-699 §1 WHY verbatim) 의 mechanical SSOT carrier 로, 사용자 결정 분기를 정해진 자리에 명문화한다 — dry-run/snapshot/transaction 3 mode enum + 결정 분기 0 invariant + customization preservation entry boundary.

### Cross-channel boundary

reconcile 어휘는 다음 영역에 동시 등장:

1. **wrapper plugin self-app**: `templates/github-workflows/*.yml` ↔ `.github/workflows/*.yml` byte-identical mirror (ADR-005)
2. **consumer overlay**: `.claude/_overlay/*` consumer customization ↔ wrapper SSOT desired state diff (ADR-027 boundary)
3. **plugin install state**: `.claude/plugins/installed_plugins.json` family 7 plugin version `pin` ↔ marketplace SSOT (ADR-016 + ADR-063)
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
      atomicity_boundary_runtime_v1: "per_plugin"  # Story-3 (CFP-743, MERGED) runtime SSOT — UpgradeAgent + CLI per-plugin atomic unit (`scripts/codeforge-upgrade.{sh,ps1}`).
      atomicity_boundary_runtime_future: "family_7_plugin"  # Wave 2 Story-4 (CFP-744) ratchet ACTIVE — `scripts/atomic-upgrade-7-plugins.sh` 신설 시점, 본 contract MINOR bump v1.2 → v1.3 발동 완료 (CFP-744). [stale placeholder 정정: 旧 comment "본 contract MINOR bump v1.0 → v1.1 의무" = Wave 1 작성 시점 placeholder (v1.1/v1.2 신설 전 작성된 stale text) → 실제 v1.2 → v1.3 (Wave 2 Story-4) 정정, CFP-743 CFP-703→CFP-743 정정 패턴 답습, fact 영향 0 추적성만 — ADR-068 I-4 wording SSOT 정합. 의미 invariant `family_7_plugin_atomic` 변경 0 — ADR-016 §결정 1 SSOT (field 명 `_future` 유지 = schema field-name stability, ratchet 활성은 comment + version_history + §4.3 (d) marker 로 표기 — §4.3 (c) v1.2 패턴 동형).]
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
      json: { kind: "sidecar_manifest", path: ".claude/_overlay/.wrapper-managed-manifest.json", carrier: "Wave 2 Story-5", realized_in: "§4.7 overlay_reconcile_implementation_binding.sidecar_manifest_schema (CFP-745 v1.4 — carrier reservation → realized, RFC 6901 JSON Pointer key-path allowlist 실 schema. carrier key 유지 = field-name stability ADR-068 I-4)" }
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
- (d) Wave 2 Story-4 (CFP-744) merge — `transaction.atomicity_boundary_runtime_v1` per_plugin → `atomicity_boundary_runtime_future` family_7_plugin ratchet. **v1.3 발동 완료 (본 contract)** — `scripts/atomic-upgrade-7-plugins.sh` 신설 + ADR-037 Amendment 1 (atomic upgrade 후 0 drift invariant) carrier 동반. 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — runtime catch-up only). (Wave 1 작성 시점 §3 transaction 영역 + ADR-076 line 147 의 stale placeholder "v1.0 → v1.1 의무" → 실제 v1.2 → v1.3 정정 동반 — fact 영향 0 추적성만, ADR-068 I-4 wording SSOT 정합. CFP-743 §4.3 (c) CFP-703→CFP-743 정정 패턴 답습.)
- (e) Wave 3 Story-6 merge — `version_handshake` field 활성 (현재 placeholder_reserve, validation_status_v1_0: non_normative_placeholder_reserve)
- (f) Wave 4 sub-Epic merge — `reconcile_strategy.enum_reserved_wave_4` 값 활성
- (g) Wave 2 Story-5 (CFP-745) merge — overlay 영역 (skill/agent/hook) 3-way merge reconcile runtime (`scripts/reconcile-overlay.sh` 신설, Phase 2 carrier). **v1.4 발동 완료 (본 contract)** — §4.7 `overlay_reconcile_implementation_binding` block 신설 (per-file 3-way merge layer + marker_preserve_binding + sidecar_manifest_schema + base_acquisition_binding). marker_block_syntax.comment_prefix_per_filetype.json `carrier: "Wave 2 Story-5"` → `realized_in` cross-ref (carrier reservation → realized — ADR-027 §결정 7.A.1 carrier 실현, AC-10 contract integration OUTCOME). §1 out-of-scope "3-way merge runtime (overlay reconcile, Wave 2 Story-5 carrier)" = 본 trigger 발동으로 carrier-declare → realized (단 §1 OOS 표기는 "Wave 2 Story-5 carrier" 추적성 유지 — carrier 가 §4.7 로 realized 됨을 표기). 의미 invariant 변경 0 (overlay reconcile = runtime catch-up, ADR-076 §결정 1 SSOT). §4.3 (c) v1.2 / (d) v1.3 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).

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
    path_form_normalization:   # v1.2 FIX iter 2 ACCEPT-5 — Change Plan §4.5 canonical 규칙 contract-level SSOT (구현 lane binding). ratchet 강화 only (path_form_invariant 의 명시화 — weakening 0).
      accepted_input_forms:    # 정규화 함수 수용 의무 6종 (Change Plan §4.5 enumeration verbatim)
        - msys2_posix              # /c/Users/...
        - windows_backslash        # C:\Users\...
        - windows_forward_slash    # C:/Users/...
        - relative                 # ./ ../ root 기준 resolve
        - whitespace_containing    # 공백 포함 path (raw 보존, shell 전달 시점만 quote)
        - non_ascii_utf8           # UTF-8 segment byte-level 보존 (locale-dependent 변환 금지)
      canonical_output_rule:
        base: "repo_root (consumer project root) 기준 절대 경로"
        separator: "forward_slash_single"    # backslash → / 변환, drive 환경별 일관 mapping
        encoding: "utf8_explicit"            # non-ASCII byte-level 보존
        relative_resolution: "root_기준_absolute (symlink 미해소 — 정책 단순화)"
        precedent: "CFP-702 _to_canonical() 함수 semantic 동형 (신규 발명 금지)"
      parity_obligation: "sh ↔ ps1 동일 canonical 함수 semantic (동일 입력 → byte-identical output). divergence = post-apply sanity check 검출 → automatic_rollback_to_snapshot."
      failure_behavior: "abort_before_touch"   # 정규화 불가 입력 = filesystem touch 0 상태에서 abort (snapshot 무생성, dry_run filesystem_touch:false 정합). Change Plan §7.4.1(e) DR entry 정합.
      adr_061_cross_ref: "정규화 로직 > 5줄 / backslash escape 포함 시 외부 .py helper 의무 (sh↔ps1 single source parity 구조적 강제) — ADR-061 Python script convention."
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

### 4.6 Wave 2 Story-4 per-family mechanical implementation 참조 (v1.3 — CFP-744 §4.3 (d) binding 발동)

본 §4.5 mechanical_implementation_binding (v1.2, per-plugin) 위에 **per-family transaction layer** 1단을 추가한다. per-plugin reconcile semantic = §4.5 SSOT 재사용 (변경 0), per-family orchestration 만 신설.

```yaml
family_atomic_implementation_binding:   # v1.3 신설, CFP-744 §4.3 (d) 발동
  carrier_story: CFP-744  # Wave 2 Story-4
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = scripts/atomic-upgrade-7-plugins.sh 실 구현
  entrypoint: "scripts/atomic-upgrade-7-plugins.sh"   # per-family runtime (per-plugin = §4.5 codeforge-upgrade.{sh,ps1} SSOT 재사용)
  family_scope:          # codeforge family 7 plugin 한정 (codex/superpowers 외부 marketplace 제외 — ADR-037 Amendment 1 결정 A1-2)
    - codeforge
    - codeforge-requirements
    - codeforge-design
    - codeforge-review
    - codeforge-develop
    - codeforge-test
    - codeforge-pmo
  per_family_transaction_boundary:
    semantic: "7 plugin version pin sync = 단일 atomic unit (부분 실패 = 전체 7 plugin atomic rollback, Epic EPIC-AC-3 verbatim)"
    snapshot_layer: "per-family snapshot tar (per-plugin Story-3 snapshot 위 1 layer — DataMigrationArch §11 SSOT)"
    partial_failure_behavior: "automatic_rollback_to_pre_atomic_family_snapshot"  # per-plugin rollback (§4.5) 재사용 + per-family 전체 atomic
    per_plugin_delegation: "Story-3 UpgradeAgent per-plugin invocation 재사용 (ADR-039 §결정 1 one-shot, semantic 분산 0)"
  zero_drift_invariant_binding:   # ADR-037 Amendment 1 결정 A1-1/A1-3
    post_atomic_verification: "bash scripts/check-codeforge-version-drift.sh --plugin <codeforge-N> 7회 invocation (7-family 명단) 후 종합"
    drift_script_change: 0   # --plugin filter (line 62) reuse — F-002 옵션 A (옵션 B `--family` flag 신설 미채택, drift script SSOT mutation 회피)
    drift_gt_0_behavior: "transaction 실패 분류 → 전체 7 plugin atomic rollback (0 drift invariant — ADR-037 Amendment 1 결정 A1-1)"
    evidence_check_entry: "atomic-upgrade-zero-drift"   # FIX Iter 2 (Codex TP#2 F-P1) — ADR-037 Amendment 1 전용 evidence-checks-registry entry (旧 marketplace-parity mismapping 정정, 의미 disjoint: marketplace-parity = wrapper-side publishing-time mirrored-field / 본 entry = consumer-side runtime 0-drift). owner_adr: ADR-037, current_tier: warning, status: deferred-followup (Phase 2 atomic-upgrade-7-plugins.sh Active 전환)
    external_marketplace_exclusion: "codex (openai-codex) / superpowers (claude-plugins-official) = atomic upgrade 비대상 — 7-name loop 가 구조적 배제 (false rollback 0)"
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.3 = 강화 only, weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 — runtime catch-up only, 의미 invariant 변경 0)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden
    adr_053_d2_verbatim_quote: unchanged               # L150-151 weakening 차단
```

Phase 1 (CFP-744) merge 시 본 §4.6 binding block 활성 (schema declare). Phase 2 (별 PR) merge 시 `scripts/atomic-upgrade-7-plugins.sh` 실 구현 + per-family transaction mechanical 활성.

### 4.7 Wave 2 Story-5 overlay reconcile mechanical implementation 참조 (v1.4 — CFP-745 §4.3 (g) binding 발동)

본 §4.5 (per-plugin) / §4.6 (per-family) mechanical_implementation_binding 위에 **overlay 영역 (skill/agent/hook) 3-way merge reconcile layer** 1단을 추가한다. per-plugin/per-family reconcile semantic = §4.5/§4.6 SSOT 재사용 (변경 0), overlay 영역 customization-preserving 3-way merge orchestration 만 신설. marker_block_syntax.comment_prefix_per_filetype.json `carrier: "Wave 2 Story-5"` 의 realized 영역 (carrier reservation → 실 schema, ADR-027 §결정 7.A.1 carrier 실현, AC-10 contract integration OUTCOME).

```yaml
overlay_reconcile_implementation_binding:   # v1.4 신설, CFP-745 §4.3 (g) 발동
  carrier_story: CFP-745  # Wave 2 Story-5 (overlay 영역 3-way merge reconcile)
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = scripts/reconcile-overlay.sh 실 구현
  entrypoint: "scripts/reconcile-overlay.sh"   # overlay 영역 3-way merge orchestration shell (per-plugin = §4.5 / per-family = §4.6 SSOT 재사용, semantic 분산 0)
  scope: "consumer .claude/ overlay (skill / agent md / hook sh / settings.json) — wrapper SSOT mirror 영역 + D4 customization marker block"
  mode_dispatch:
    "--apply": "base 확보 → overlay file 분류 → per-file 3-way merge → customization integrity 검증 → 단일 reconcile unit (no_prompt_invariant: true, user_decision_branches: 0)"
    "--dry-run": "overlay 영역 desired (wrapper SSOT) vs current diff + 3-way merge preview, filesystem touch 0 (dry_run_classified_as_decision_branch: false)"
    "--rollback": "Story-3 snapshot restore SSOT 재사용 (overlay reconcile = Story-3 snapshot scope 안 — 별 entrypoint 불요)"
  three_way_merge_binding:
    base: "Story-3 snapshot infra (.claude/_snapshots/<UTC>-<ver>.tar.gz) 의 wrapper-managed 영역 = 3-way merge ancestor (ADR-076 §결정 3 snapshot granularity = marker block 밖 wrapper SSOT mirror 영역, consumer customization marker block 안은 snapshot scope 외 — base 에 consumer customization 미혼입)"
    wrapper_new: "wrapper plugin 현재 overlay template (desired SSOT)"
    consumer_current: "consumer 현재 overlay file content"
    text_merge: "git merge-file 차용 (3-way text merge) — conflict = 명시적 보고 (silent overwrite 0, EPIC-AC-4)"
    binary_fallback: "git merge-file 불가 (image/pdf) = wholesale mirror + user-visible loss report (skip 미채택 — '빠짐' 통증 직접 해소, silent corrupt 0)"
    agent_frontmatter_delegation: "merge.py (overlay/hooks/merge.py) agent-fm 2-way merge SSOT 위임 (reconcile-overlay.sh 가 frontmatter deep-merge 로직 재구현 절대 금지 — semantic 분산 0)"
    three_way_scope: "marker block 안 영역 한정 — marker block 밖 = base 비교 skip + consumer-current 무조건 preserve (2-way, base 불요). 3-way merge 는 marker 안만 적용 (base-stale risk 표면 축소)"
  marker_preserve_binding:
    inside_marker: "wrapper-new mirror (wrapper SSOT — wrapper 변경분 누락 0, '빠짐' 직접 해소)"
    outside_marker: "consumer-current byte-identical preserve (customization 침범 0 — EPIC-AC-4 silent overwrite 0)"
    boundary_identification: "whole-line anchored (ADR-027 §결정 7.D.3 — substring 위조 marker `# BEGIN wrapper-managed-evil` injection 차단)"
    malformed_marker: "check-wrapper-managed-block.sh (CFP-702 SSOT) exit_nonzero → reconcile abort-before-touch (filesystem touch 0). reconcile-overlay.sh = marker lint 로직 재구현 절대 금지 (CFP-702 SSOT 호출만)"
    customization_integrity_invariant: "marker block 밖 = reconcile 전/후 byte-identical (AC-9(c)). 위반 = silent loss = Story-3 snapshot rollback + 명시적 escalation. base-stale edge (snapshot 이후 marker 밖→안 이동) 의 명시적 안전망"
  sidecar_manifest_schema:   # marker_block_syntax.comment_prefix_per_filetype.json carrier="Wave 2 Story-5" → realized (ADR-027 §결정 7.A.1 carrier 실현)
    path: ".claude/_overlay/.wrapper-managed-manifest.json"
    rationale: "JSON 주석 불가 → in-file marker 불가 (ADR-027 §결정 7.A.1). sidecar manifest 가 wrapper-managed key-path 를 RFC 6901 JSON Pointer 로 allowlist. allowlist 안 = 3-way merge mirror (wrapper SSOT), 밖 = consumer preserve (marker block 안/밖 semantic 의 JSON 등가, Kustomize patchesStrategicMerge target path 패턴 동형)"
    schema:
      schema_version: "string (현재 \"1\")"
      managed_paths: "list[string] — RFC 6901 JSON Pointer (예: /hooks/SessionStart/0/command, /permissions/allow/-). allowlist 안 path = 3-way merge mirror, 밖 = consumer preserve"
    absent_or_malformed_behavior: "wholesale_mirror_with_user_visible_loss_report (sidecar 부재/JSON parse fail/JSON Pointer syntax 위반/managed_paths[] 부재 = marker 부재 fallback 과 동형 — silent loss 0, ADR-027 §결정 7.C 정합. partial key-path merge 진입 절대 금지)"
    path_traversal_guard: "RFC 6901 JSON Pointer syntax bound (filesystem path 아님 = path traversal surface 0)"
  base_acquisition_binding:
    source: "Story-3 snapshot infra (.claude/_snapshots/) 재사용 — 신규 state artifact 신설 0 (ADR-064 minimal-change + snapshot ↔ base cross-pollinate 회피, snapshot_reset_disjoint_layer 정합)"
    orthogonality_invariant: "base 가용성 (3-way ancestor 존재 = 3-way 가능 여부) 과 marker/sidecar 유효성 (preservation scope 존재) 은 ORTHOGONAL 2 조건 — 동일 fallback 에 conflate 금지 (CFP-745 FIX Iter 2 Codex TP#2 P1 verified-true: conflate 시 valid marker 보유 consumer 첫 reconcile = marker 밖 customization wholesale overwrite = marker_preserve_binding hybrid invariant + EPIC-AC-4 silent overwrite 0 위반)"
    integrity: "Story-3 §11.4 tarball checksum verify 재사용. checksum verify 완료 전 per-file 3-way merge 진입 금지 (partial-state 0)"
    base_state_resolution:   # base 가용성 3-state (marker scope 와 독립 판정)
      base_ok: "snapshot 존재 + checksum OK → 3-way merge 경로 (MARKER_VALID 시)"
      base_corrupt: "tarball checksum fail → abort-before-touch + 명시 보고 (corrupt base 진입 절대 금지, partial-state 0 — Story-3 §4.5 failure_behavior. 현 설계 sound 유지)"
      base_absent: "snapshot 부재 (첫 reconcile) → marker scope 와 교차 (아래 base_absent_first_reconcile)"
    base_absent_first_reconcile: "snapshot 부재 (첫 reconcile) + marker/sidecar 유효 (MARKER_VALID) = marker-aware 2-way first-reconcile (3-way 아님 — base 없음): marker 안 = wrapper-new mirror + prior inside-marker consumer 편집 loss report 명시 / marker 밖 = consumer-current byte-identical preserve (base 불요 — marker 밖 base 비교 자체 불필요) / JSON sidecar managed_paths = wrapper mirror + 그 외 JSON key = consumer-current preserve. marker/sidecar 부재·malformed (MARKER_NONE — base 가용성 무관) = wholesale_mirror_with_user_visible_loss_report (진짜 fallback — preservation scope 자체 부재가 사유, base-absent 아님). base corrupt = abort-before-touch (base_state_resolution.base_corrupt). 다음 reconcile 부터 snapshot = base_ok (3-way 정상). CFP-745 FIX Iter 2 정정 — base-absent ≠ marker-absent 분리 (orthogonality_invariant 정합. v1.4 schema 정정 — MINOR 유지, ratchet 강화 only: marker_block_absent_behavior 무변경 / user_decision_branches:0 무변경 / base_absent 가 marker_absent 와 분리됨을 명시 = 강화)"
  failure_modes:   # Change Plan §7.4.1 (a)-(h) overlay reconcile DR 8 failure mode SSOT cross-ref
    - "(a) base 부재/corrupt — base 가용성 ≠ marker scope orthogonal 분리 (FIX Iter 2): base corrupt → abort-before-touch / base 부재+MARKER_VALID → marker-aware 2-way first-reconcile (marker 밖 preserve, wholesale 아님) / MARKER_NONE(base무관) → wholesale_mirror (silent loss 0)"
    - "(b) 3-way merge conflict (marker 안 wrapper-new ↔ consumer-current) → 명시적 보고 (silent overwrite 0)"
    - "(c) binary file git merge-file 불가 → wholesale mirror + loss report (silent corrupt 0)"
    - "(d) marker malformed (orphan/reversed/nested) → check-wrapper-managed-block.sh exit_nonzero → reconcile abort"
    - "(e) idempotent re-run (overlay 이미 wrapper SSOT 일치) → no-op 정상 종료 (snapshot 미생성)"
    - "(f) sidecar manifest 부재/malformed → wholesale_mirror fallback (partial key-path merge 금지)"
    - "(g) customization 영역 침범 (marker 밖 byte-diff) → Story-3 snapshot rollback + 명시적 escalation"
    - "(h) cross-platform path encoding → Story-3 §4.5 path_form_normalization SSOT 재사용 (overlay layer 신규 detection 0)"
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.4 = 강화 only (overlay coverage 확장), weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 — overlay reconcile = runtime catch-up only)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (ADR-027 §결정 7.C)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden (base = Story-3 snapshot 재사용, 신규 layer 0)
    adr_053_d2_verbatim_quote: unchanged               # L150-151 weakening 차단
```

Phase 1 (CFP-745) merge 시 본 §4.7 binding block 활성 (schema declare — marker_block_syntax.json carrier reservation → realized). Phase 2 (별 PR) merge 시 `scripts/reconcile-overlay.sh` 실 구현 + `.claude/_overlay/.wrapper-managed-manifest.json` sidecar manifest 실 형식 + overlay 3-way merge mechanical 활성.

