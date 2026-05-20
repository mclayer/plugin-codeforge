---
kind: registry
registry: reconcile-protocol
version: "1.13"
status: Deprecated
deprecated_carrier_cfp: CFP-1125 (CFP-1111-W1-S1)
sunset_target_cfp: CFP-1111-Wave-4-Story-11
imperative_walker_protocol_carrier: imperative-walker-protocol-v1 (Wave 1 Story-3 codify)
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/reconcile-protocol-v1.md
date: 2026-05-15
authors:
  - ArchitectAgent (CFP-701 Wave 1 Story-1 carrier — declarative reconciliation upgrade flow schema SSOT)
  - DeveloperPLAgent (CFP-702 Wave 1 Story-2 Phase 2 — §4.3 (b) trigger 발동, marker_block_syntax_* fields 확장)
  - ArchitectPLAgent (CFP-743 Wave 2 Story-3 — §4.3 (c) trigger 발동, mechanical_implementation_binding block 신설 + KEY cross-ref 정정 CFP-703→CFP-743)
  - ArchitectPLAgent (CFP-744 Wave 2 Story-4 — §4.3 (d) trigger 발동, atomicity_boundary_runtime per_plugin → family_7_plugin ratchet 활성 + stale placeholder 정정 v1.0→v1.1 → v1.2→v1.3)
  - ArchitectPLAgent (CFP-745 Wave 2 Story-5 — §4.3 (g) trigger 신설 발동, §4.7 overlay_reconcile_implementation_binding block 신설 + marker_block_syntax.json carrier → realized_in cross-ref (§2.5 FORM 옵션 (i)))
  - ArchitectPLAgent (CFP-820 Wave 3 Story-6 — §4.3 (e) trigger 발동, version_handshake placeholder_reserve → active + 3 stale placeholder 정정 (becomes_normative_at_version v1.1→v1.5 / validation_status_v1_0→validation_status_v1_5 rename / field_schema_future v1.0→v1.1 comment → v1.4→v1.5 active schema) + §4.8 version_handshake_3way_binding block 신설 (ADR-063 Amendment 5 §결정 15 carrier))
  - ArchitectPLAgent (CFP-821 Wave 3 Story-7 — §4.3 (h) trigger 신설 발동, §4.9 coverage_fan_out_implementation_binding block 신설 (D1 Issue/PR template fan-out + D2 branch protection setup helper FORM (b) + D3 script boundary taxonomy). ADR-027 Amendment 5 §결정 9 + ADR-076 §결정 2 표 PR template row carrier)
  - ArchitectAgent (CFP-906 Wave 4 sub-Epic #1 Story-1 — §4.3 (i) trigger 신설 발동, §4.10 multi_version_channel_pin_binding block 신설 (3-tier channel taxonomy declare layer + `family_7_plugin_atomic × channel pin invariant` + per-channel marketplace.json channels[] matrix). ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17 carrier. reconcile_strategy.enum_reserved_wave_4[multi_version_channel_pin] placeholder → partial active (codemod_apply / uninstall_cleanup 2 entry 무변경). §4.8 version_handshake placeholder → active 단독 promotion 선례 답습.)
  - ArchitectPLAgent (CFP-898 Wave 4 sub-Epic Epic CFP-858 S1 — §4.3 (i) trigger 신설 발동 + §4.11 dependency_bundle_integrity_binding block 신설. ADR-076 Amendment 2 §결정 2 11번째 row append + §결정 6 fail-closed clause sub-section carrier. mctrader-data#81 14 failing checks evidence)
  - ArchitectAgent (CFP-932 Wave 4 sub-Epic #1 Story-2 — §4.10 status schema_declared_phase1 → runtime_active 전환 + registry_channel_matrix.story_1_scope_declare_only A2 정정 (channels[] populate carrier = Story-4, Story-2 = read-only drift source — Issue #932 OOS formal contract-pin 상충 해소, DataMigrationArch §11.7 load-bearing dissent 채택). channel_drift_detection / three_way_channel_invariant runtime_carrier ACTIVE 반영. schema shape 무변경. MINOR bump (kind:registry sibling sync 면제, plugin.json bump 0 = marketplace_sync_declared:false).)
  - ArchitectPLAgent (CFP-899 Wave 4 sub-Epic CFP-858 S2 — §4.3 (j) trigger 신설 발동 + §4.12 consumer_applicability_filter_binding block 신설. ADR-083 신규 §결정 1-6 + ADR-027 Amendment 6 §결정 10 sibling carrier. mctrader-data#81 14 failing checks horizontal filter layer (CFP-898 vertical closure resolver 와 sequential composition). 9 sub-field schema: truth_table_schema / repo_kind_detection_signals / whitelist_file_format / mixed_repo_handling / fail_closed_unknown / self_app_exemption / hook_integration / out_of_scope / ratchet_invariant_preserved. MINOR bump (kind:registry sibling sync 면제, plugin.json bump 0 = marketplace_sync_declared:false). [FIX iter 1 — F-DR-899-3 narrative 6 field → 9 sub-field 정정 (body 정확, ADR-068 I-4 wording SSOT 정합 — fact 영향 0 추적성만).])
  - ArchitectAgent (CFP-991 Wave 4 sub-Epic #1 Story-4 — §4.3 (l) trigger 신설 발동, §4.14 `canary_compatibility_check_binding` block 신설 (7 field: enabled / promotion_criteria_4tuple / family_7_atomic_canary_pin / canary_consumer_evidence_origin enum closed-set + open_extension:false / inter_plugin_contract_backward_compat_verify / promotion_gate_failure_mode enum + bypass_label / downgrade_asymmetry_marker placeholder_reserve). §4.10 A3 정정 entry append (`registry_channel_matrix.story_4_scope_write_carrier`, forward-effective only — v1.8 A2 정정 의 realize point, CFP-906 §11.4 historical record immutable 보존 두 layer 분리, DataMigrationArch §11.7 load-bearing dissent verbatim 채택). ADR-72 amendment_log Amendment 3 + label-registry-v2 v2.34 → v2.35 MINOR (4 신규 entry: 1 hotfix-bypass:canary-promotion-criteria + 3 gate:channel-{canary,beta,stable}-promotion) sibling carrier. promotion criteria 4-tuple SSOT = ADR-076 §결정 9.6 (Chrome 3-channel Stable/Beta/Canary + npm dist-tag + Rust 3-channel + K8s 3-stage 4 industry exemplar verbatim cite). wrapper-self-app Tier-1 exemption + consumer canary→beta promotion Tier-2 admin-tier 권장 (boundary 2-tier, ADR-72 §결정 6 wrapper-self-app N/A invariant 정합). ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING cross-ref §7.6 T-4.1 4-tuple measurement spoofing mitigation. MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — declare+runtime → enforcement, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 / (k) v1.10 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).)
  - ArchitectAgent (CFP-1014 Wave 4 sub-Epic #1 Story-5 — §4.3 (m) trigger 신설 발동 + §4.14 `downgrade_asymmetry_marker.status: placeholder_reserve → wired` 단독 promotion (§4.8 version_handshake placeholder_reserve→active 단독 promotion 선례 verbatim 답습 — partial-active state 도입 0, field shape 변경 0, closed_enum length=2 invariant). `carrier_story: "CFP-991-Story-5" → "CFP-1014"` carrier→realized 정정 (CFP-744 carrier→realized 패턴 답습, fact 영향 0 추적성만 ADR-068 I-4 wording SSOT 정합). `closed_enum` 에 `open_extension: false` 명시 추가 (SecurityArch ratchet 강화 권고 — closed_enum invariant 명시화, ADR-064 §self-application 정합). `activation_protocol` tense 갱신 (Phase 1 = wired 활성 완료 forward-effective). `sunset_justification` 본문 무변경 (DataMigrationArch risk surface 3 — asymmetry = directional ratchet 강화 0 invariant 보존). §4.14 L1160 `out_of_scope` `downgrade_path_runtime` comment "(Story-5 carrier placeholder_reserve)" → "(wired 활성 완료, downgrade execution runtime = 별 carrier)" 갱신 (placeholder→wired transition 반영). §4.4 ratchet 보존 의무 7번째 row append — `canary_compatibility_check_binding.downgrade_asymmetry_marker.status: wired → placeholder_reserve` 역방향 약화 차단 (ADR-058 §결정 5 sunset_justification 3-tuple 의무, ratchet 강화 only). 5 production-cutover cross-ref atomic sync (promotion-criteria-4tuple.md L86-L88 + rollback-protocol.md L75 + L91 + README.md L48 + section-ownership.yaml CFP-1014 entry append). Wave 4 sub-Epic #882 close marker (Story-5 = 5/5 Story complete carrier, §3 production cutover stage 5 downgrade asymmetry final state). production_cutover_touching: FALSE (Story-3 CFP-954 가 production cutover declare layer carrier 완료, Story-5 = declare-only disjoint declarative SSOT — ADR-72 §결정 6 wrapper-self-app N/A invariant 정합). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — downgrade asymmetry invariant wired 활성, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 / (k) v1.10 / (l) v1.11 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i) — string flip only, partial-active state 도입 회피 = minimal-change).)
  - ArchitectPLAgent (CFP-900 Wave 4 sub-Epic CFP-858 S3 — §4.3 (k) trigger 신설 발동 + §4.13 result_fidelity_binding block 신설. ADR-076 Amendment 3 §결정 3 sub-clause (transaction 사후 sanity check 위 result fidelity false SUCCESS 차단 clause) + ADR-026 Amendment 5 §결정 7 (`.github/` fast-pass content sanity 1차 신호 orthogonal warning layer) sibling carrier. Epic CFP-858 마지막 Story — S1 CFP-898 vertical dependency closure (mirror-전) + S2 CFP-899 horizontal consumer-applicability filter (mirror-전) 위 honest result reporting layer (mirror-후, 3-layer composite 완결). 6 sub-field schema: result_enum_schema (4-value SUCCESS/SUCCESS_WITH_DEGRADATION/PARTIAL_FAILURE/FAILED closed-set) / degradation_propagation (S1 §4.11 fail-closed → PARTIAL_FAILURE·FAILED / S2 §4.12 abort → FAILED) / post_mirror_sanity_check (ImpactReport diff, filesystem-only, syntax-level 1차 신호) / fast_pass_content_sanity (phase-gate-mergeable `.github/` 의존 script reference mismatch warning tier) / upgrade_event_honest_record (false SUCCESS 차단) / out_of_scope + ratchet_invariant_preserved. silent false SUCCESS 차단 invariant (exit code → result enum deterministic mapping). MINOR bump (kind:registry sibling sync 면제, plugin.json bump 0 Phase 1 = marketplace_sync_declared:false / Phase 2 v5.91.0 동반 예상). CFP-898 §4.11 + CFP-899 §4.12 binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).)
version_history:
  - { version: "1.0", date: 2026-05-15, carrier: CFP-701, change: "initial — declarative reconciliation upgrade flow schema SSOT. 9 영역 desired state enumeration + dry-run/snapshot/transaction 3 mode enum + customization preservation entry (marker block, Story-2 prerequisite) + version_handshake / reconcile_strategy placeholder reserve (Wave 4 carrier)." }
  - { version: "1.1", date: 2026-05-15, carrier: CFP-702, change: "§4.3 (b) trigger 발동 — Wave 1 Story-2 marker block syntax 확정. customization_preservation_entry 영역 확장: marker_block_syntax_* 4 fields 정식화 (comment prefix per-filetype / nesting_policy / lint_behavior / migration_script). ADR-027 Amendment 3 §결정 7.A-7.E verbatim cross-ref." }
  - { version: "1.2", date: 2026-05-15, carrier: CFP-743, change: "§4.3 (c) trigger 발동 — Wave 2 Story-3 UpgradeAgent + CLI 실 implementation hook (`scripts/codeforge-upgrade.{sh,ps1}` 신설). mechanical_implementation_binding block 신설 (§4.5 reference → CLI 3 mode entrypoint + UpgradeAgent Plan+Apply 책임 binding + reconcile PR open scope = ADR-066 Amendment 3 cross-ref). KEY cross-ref 정정: §4.3 (c) `CFP-703` → `CFP-743` (Wave 1 작성 시점 placeholder drift — 동일 Story, fact 영향 0 추적성 정정). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 invariant / atomicity_boundary semantic / transaction.completion_criterion 무변경 (ratchet 강화 only — ADR-064 §self-application 정합)." }
  - { version: "1.3", date: 2026-05-16, carrier: CFP-744, change: "§4.3 (d) trigger 발동 완료 — Wave 2 Story-4 7-plugin family atomic upgrade runtime (`scripts/atomic-upgrade-7-plugins.sh` 신설). `transaction.atomicity_boundary_runtime_v1` per_plugin → `atomicity_boundary_runtime_future` family_7_plugin runtime catch-up ACTIVE (ADR-076 §결정 8 pre-designated ratchet). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — runtime catch-up only). ADR-037 Amendment 1 (atomic upgrade 후 0 drift invariant) carrier 동반. stale placeholder 정정: 본 contract line 144 comment + ADR-076 line 147 의 'MINOR bump v1.0 → v1.1 의무' (Wave 1 작성 시점 placeholder — v1.1/v1.2 신설 전 작성된 stale text) → 실제 'v1.2 → v1.3 (Wave 2 Story-4)' 정정 (CFP-743 CFP-703→CFP-743 정정 패턴 답습, fact 영향 0 추적성만 — ADR-068 I-4 wording SSOT 정합). schema field 명 `_future` 유지 (field-name stability — ratchet 활성은 comment + version_history + §4.3 (d) marker 로 표기, §4.3 (c) v1.2 패턴 동형). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary_semantic_invariant / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — ADR-064 §self-application 정합)." }
  - { version: "1.4", date: 2026-05-16, carrier: CFP-745, change: "§4.3 (g) trigger 신설 발동 완료 — Wave 2 Story-5 overlay 영역 (skill/agent/hook) 3-way merge reconcile runtime (`scripts/reconcile-overlay.sh` 신설, Phase 2 carrier). §4.7 `overlay_reconcile_implementation_binding` block 신설 (per-file 3-way merge layer base/wrapper-new/consumer-current + marker_preserve_binding marker 안=wrapper-new mirror·밖=consumer-current byte-identical preserve + sidecar_manifest_schema RFC 6901 JSON Pointer key-path allowlist + base_acquisition_binding Story-3 snapshot wrapper-managed 영역 재사용). marker_block_syntax.comment_prefix_per_filetype.json `carrier: \"Wave 2 Story-5\"` → `realized_in: \"§4.7 overlay_reconcile_implementation_binding.sidecar_manifest_schema\"` cross-ref 추가 (carrier reservation → realized — ADR-027 §결정 7.A.1 carrier 실현, AC-10 contract integration OUTCOME). carrier key 유지 (field-name stability — consumer schema key 의존 보존, ADR-068 I-4). Story-3 §4.5/§4.6 (c)/(d) trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — overlay coverage 확장, ADR-064 §self-application 정합). [FIX Iter 2 — Codex TP#2 P1 verified-true: base_acquisition_binding 에 orthogonality_invariant + base_state_resolution(base_ok/base_corrupt/base_absent) 추가 + base_absent_first_reconcile 정정 (base 가용성 ≠ marker scope orthogonal 분리 — base 부재+MARKER_VALID = marker-aware 2-way first-reconcile marker 밖 byte-identical preserve / MARKER_NONE base무관 = wholesale_mirror / base corrupt = abort. 초기 'base 부재 = marker 부재 fallback 동형' conflation 정정). v1.4 schema 정정 — MINOR 유지, ratchet 강화 only (base_absent 가 marker_absent 와 분리됨을 명시 = 강화, marker_block_absent_behavior/user_decision_branches:0 무변경).]" }
  - { version: "1.7", date: 2026-05-17, carrier: CFP-906, change: "§4.3 (i) trigger 신설 발동 완료 — Wave 4 sub-Epic #1 Story-1 (Epic CFP-882) `multi-version channel pin declare layer`. §4.10 `multi_version_channel_pin_binding` block 신설 (3-tier channel taxonomy stable/beta/canary + consumer `.claude/_overlay/project.yaml codeforge.channel` field SSOT + `family_7_plugin_atomic × channel pin invariant` + per-channel marketplace.json channels[] matrix + 3-way channel invariant publisher↔registry↔consumer 확장 — ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17 carrier). `reconcile_strategy.enum_reserved_wave_4[multi_version_channel_pin]` placeholder → partial active (`codemod_apply` Wave 4 sub-Epic #2 / `uninstall_cleanup` Wave 4 sub-Epic #3 2 entry 무변경 — CFP scope unitary ADR-064 §결정 1.3 정합). `reconcile_strategy.status: \"placeholder_reserve\"` field-level 유지 (partial activation invariant — §4.8 `version_handshake.status: placeholder_reserve → active` 단독 promotion 선례 답습, partial-active state 도입 회피 = minimal-change). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — `channel pin` = runtime catch-up layer 확장만, 의미 invariant 자체는 ADR-016 Amendment 3 가 family scope 의 channel 차원 declare). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — `multi-version channel pin coverage` 확장, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)). Live touching: FALSE (declare layer scope — Story-1 = schema SSOT only, runtime UpgradeAgent multi-channel dispatch = Wave 4 sub-Epic #1 Story-2 carrier, ProductionEvidence canary tier activation = Wave 4 sub-Epic #1 Story-3 carrier — ADR-72 §결정 1 정합)." }
  - { version: "1.8", date: 2026-05-18, carrier: CFP-932, change: "Wave 4 sub-Epic #1 Story-2 (Epic CFP-882) `multi-version channel pin runtime activation`. §4.10 `status: schema_declared_phase1` → `runtime_active` 전환 (D1 `codeforge-upgrade.sh --channel` runtime resolve + D2 `atomic-upgrade-7-plugins.sh` per-family channel bump mixed channel detection→abort-before-touch + D3 `infer-channel-from-version.sh` migration tool write-0 invariant + D4 consumer-guide §2g.3 + D5 `channel-drift-detection.yml`/`check-channel-drift.sh` 3-tuple drift). **`registry_channel_matrix.story_1_scope_declare_only` A2 정정** — 종전 '실 marketplace.json channels[] field 추가 = Story-2 carrier' → 'populate = Story-4 carrier, Story-2 = read-only drift source (D5 (c) leg)' (Issue #932 OOS 와 formal contract-pin 상충 해소, DataMigrationArch §11.7 load-bearing dissent frozen-SHA verify 후 채택 — live contract forward-effective 정정, CFP-906 §11.4 line 454 historical record immutable 보존 두 layer 분리). `channel_drift_detection.runtime_carrier`/`story_1_scope` + `three_way_channel_invariant.runtime_carrier` ACTIVE 반영 (OQ-5 check-3way-version-parity.sh channel 확장 scope 포함, ADR-076 §결정 9.2 verbatim 정합). schema shape 무변경 (field 추가/삭제/타입 0 — §4.8 version_handshake placeholder_reserve→active 단독 promotion 선례 답습). SecurityArch OQ-3 M-1b/M-7 채택 (`canary_tier_authority` contract-pin 정합 — silent canary uptake via CLI 차단). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — declare → runtime 전환, ADR-064 §self-application 정합). Live touching: FALSE (canary tier resolve 만, ProductionEvidence activation = Story-3 carrier OOS — ADR-72 §결정 1)." }
  - { version: "1.6", date: 2026-05-17, carrier: CFP-821, change: "§4.3 (h) trigger 신설 발동 완료 — Wave 3 Story-7 coverage fan-out (D1+D2+D3, Epic CFP-699). §4.9 `coverage_fan_out_implementation_binding` block 신설 (D1 Issue/PR template fan-out: `templates/.github/ISSUE_TEMPLATE/*.yml` 5 forms + config.yml + `templates/.github/PULL_REQUEST_TEMPLATE.md` byte-identical mirror, D4 marker form-level wrap ADR-027 §결정 7.A.1 / D2 branch protection setup helper FORM (b): `templates/scripts/setup-branch-protection.sh` manifest 합성 + dry-run preview only — API write 0, 실 등록 = consumer admin operator manual OOS / D3 script boundary taxonomy: `docs/script-boundary.md` 3 category declarative (wrapper SSOT / consumer overlay / mixed-zone distributed templates)). reconcile semantic = §4.7 overlay_reconcile_implementation_binding (marker-aware 2-way / wholesale_mirror_with_user_visible_loss_report) SSOT 재사용 (D1 `.github/` 영역 area handler 추가, algorithm 재구현 0). ADR-027 Amendment 5 §결정 9 (Issue Forms enumeration 정정 3종 → 5 forms + config.yml + D4 marker cross-ref) + ADR-076 §결정 2 표 PR template row append carrier 동반. ADR-066 무변경 (FORM (b) — Administration:write grant 0, F-P1-A 해소 = scope-down OOS, least-privilege ratchet-safe). § \"Amendment / version 번호 정정\": ADR-027 carrier = Amendment 5 §결정 9 (Story §1-§6 RequirementsPL synthesis 의 'Amendment 4' = frontmatter 미검증 — CFP-820 이 ADR-027 amendment 4 / §결정 8 점유, 설계 lane strict-verify direct Read 후 Amendment 5 §결정 9 정정) / 본 contract version = v1.6 (Story-7 §3.5/§4.3 의 'v1.5' = Story-6 collision 점유 — CFP-820 이 v1.5 §4.3 (e) 점유, 설계 lane strict-verify origin/main direct Read 후 v1.6 §4.3 (h) 정정, Codex TP#2 verify-before-trust 8-mirror 교훈). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — D1/D2/D3 coverage fan-out 확장, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i))." }
  - { version: "1.5", date: 2026-05-17, carrier: CFP-820, change: "§4.3 (e) trigger 발동 완료 — Wave 3 Story-6 3-way version atomic invariant 확장 (B2, Epic CFP-699). `version_handshake.status: placeholder_reserve → active` 활성화 (Wave 1 Story-1 CFP-701 사전 declare `carrier_story: CFP-Wave-3-Story-6` 실현). §4.8 `version_handshake_3way_binding` block 신설 (publisher plugin.json ↔ registry marketplace.json ↔ consumer project.yaml codeforge.version_pin 3-way byte-identical invariant + warning-first→blocking fallback orthogonality + read-only lint scope + sanity guard 6-tuple + ADR-063 Amendment 5 §결정 15 carrier). 3 stale placeholder 정정 (CFP-744 v1.0→v1.1→v1.2→v1.3 / CFP-745 carrier→realized 정정 패턴 답습 — fact 영향 0 추적성만, ADR-068 I-4 wording SSOT 정합): (1) `becomes_normative_at_version: \"v1.1\" → \"v1.5\"` (Wave 1 작성 시점 placeholder, 현재 v1.4 → carrier 시점 v1.5 정정) (2) `validation_status_v1_0:` key → `validation_status_v1_5:` rename + value `non_normative_placeholder_reserve` → `normative — v1.5 consumer enforce (3-way version parity validator active)` (3) `field_schema_future: \"TBD (...v1.0 → v1.1)\"` → active field schema (3-way binding semantic, comment \"v1.4 → v1.5\"). marker_block_syntax / 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` (ADR-016 §결정 1) 변경 0 — `consumer pin` layer = runtime catch-up only (publisher↔registry 영역 무변경). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). user_decision_branches: 0 / atomicity_boundary semantic / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote / marker_block_absent_behavior 무변경 (ratchet 강화 only — 3-way version invariant 확장, ADR-064 §self-application 정합). § \"Amendment 번호 정정\": ADR-063 carrier = Amendment 5 §결정 15 (Story §1-§6 RequirementsPL synthesis 의 'Amendment 4' = frontmatter 미검증 — CFP-686 이 amendment:4 점유, 설계 lane strict-verify direct Read 후 Amendment 5 정정, Codex TP#2 verify-before-trust 8-mirror 교훈)." }
  - { version: "1.7", date: 2026-05-17, carrier: CFP-898, change: "§4.3 (i) trigger 신설 발동 완료 — Wave 4 sub-Epic CFP-858 S1 carrier (Epic CFP-858 S1 base layer — S2 CFP-899 / S3 CFP-900 prerequisite). §4.11 `dependency_bundle_integrity_binding` block 신설 (workflow yml + 의존 `scripts/check-*.sh` + `templates/scripts/*.py` closure resolve + missing 시 fail-closed + atomic bundle invariant). closure_resolve_algorithm=regex_primary AM-1 (stdlib only, pyyaml 의존 0) / transitive_depth_limit=1 AM-2 (false-positive 폭증 회피) / dependency_scope=shell_script_only_v1 AM-3 (.sh + .py 패턴, runtime 의존 + dynamic fetch out-of-scope) / self_app_exemption=templates/scripts/mirror-dependency-closure.py AM-4 (consumer-distributable, ADR-005 byte-identical mirror rule 면제 영역, self-loop 0 invariant) / fail_closed_behavior=exit_1_with_error_log (silent_skip_0_invariant 강화) / dry_run_behavior=preview_only_with_return_0 (ADR-076 §결정 3 dry-run semantic 정합) / hook_integration=scripts/reconcile-overlay.sh line 437 직전 MARKER_NONE branch first-line + return 2 abort pattern (MARKER_LINT 답습). ADR-076 Amendment 1 §결정 6 fail-closed clause 추가 동반 (의미 invariant `marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report` 무변경 — sub-clause 1 추가 = ratchet 강화 only, ADR-064 §self-application 정합). mctrader-data#81 14 failing checks evidence (Epic CFP-858 §1 motivation verbatim — wholesale_mirror 시 silent partial bundle 의 real harm). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote / marker_block_absent_behavior 의미 무변경 (CFP-743 §4.5 mechanical_implementation_binding 패턴 + CFP-821 §4.9 SSOT 재사용 패턴 verbatim 답습). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i))." }
  - { version: "1.9", date: 2026-05-18, carrier: CFP-899, change: "§4.3 (j) trigger 신설 발동 완료 — Wave 4 sub-Epic CFP-858 S2 carrier (Epic CFP-858 결함 2 horizontal filter layer — S1 CFP-898 vertical closure resolver 와 sequential composition). §4.12 `consumer_applicability_filter_binding` block 신설 (9 sub-field schema: truth_table_schema / repo_kind_detection_signals / whitelist_file_format / mixed_repo_handling / fail_closed_unknown / self_app_exemption / hook_integration / out_of_scope / ratchet_invariant_preserved). ADR-083 신규 §결정 1-6 (wrapper-side filter mechanism SSOT — 4-way enum + positive whitelist + mixed exemption + fail-closed unknown + hook insertion) + ADR-027 Amendment 6 §결정 10 (consumer-side signal SSOT — filesystem-only 2-signal cross-product 4-way truth-table + boundary disjoint invariant) sibling carrier. mctrader-data#81 14 failing checks evidence (wrapper-only workflow 무차별 유입 silent harm super-class — CFP-898 closure missing 차단의 dual axis). 9 sub-field schema verbatim cross-ref ADR-083 §결정 1-6 + §4.12 body (FIX iter 1 — F-DR-899-3 narrative 6 field → 9 sub-field 정정, body 정확). hook_integration=scripts/reconcile-overlay.sh line 437 직전 (CFP-898 §4.11 hook pattern 답습 + sequential composition: CFP-898 closure resolver hook → CFP-899 consumer-applicability filter hook → cp). exit_code_contract: 0=filter OK proceed / 1=filter abort (unknown repo_kind) → return 1 ABORT / 2=filter warning degraded (Phase 2 reserve). filesystem-only invariant (network call 0 / gh api 0 / marketplace.json membership check 0) — offline-first + trust boundary 명확 + primary signal 단일 read 비용 < 1ms. user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote / marker_block_absent_behavior 의미 무변경 (CFP-898 §4.11 vertical closure resolver hook 패턴 verbatim 답습 + sequential composition layer 1 추가만, algorithm 재구현 0). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i))." }
  - { version: "1.10", date: 2026-05-19, carrier: CFP-990, change: "§4.13 `impact_report_diff_scope` EC-4 enumeration 확장 — consumer-customization-preserve 영역에 (b) `.claude/_overlay/` prefix + wrapper SSOT 미존재 path 추가 (Epic CFP-858 retro ADR-045 §D-9 emission FU-4 P-4 non-blocking precision refinement). 종전 single-clause `marker block 안 customization preserve 영역` → 명시적 2-clause enumeration ((a) marker block 안 inside-marker + (b) `.claude/_overlay/` prefix + wrapper SSOT 미존재 path consumer-only customization). ADR-027 consumer adoption protocol §결정 1 SSOT 정합 (consumer 자기 customization layer disjoint, wrapper desired state 와 별 layer). HONEST vs precision 분리 — CFP-986 inverse-defect (false `FAILED`, P0) 와 disjoint axis: 본 정정 = HONEST but precision-low (정상 consumer reconcile perpetual `SUCCESS_WITH_DEGRADATION` 보고 회피 — extra 영역 `.claude/_overlay/project.yaml` 등 consumer 자기 SSOT 파일이 wrapper desired state 와 disjoint 라는 explicit boundary enumeration). NO version bump — body 정확화, fact 영향 0, F-CR-900-3 'no version bump — body 정확화, fact 영향 0' 패턴 verbatim 답습 (ADR-068 I-4 wording SSOT 정합). 의미 invariant 무변경 (기존 'EC-4 false-positive 차단' + 'consumer customization preserve' 의 enumeration 확장 = ratchet 강화 only, ADR-064 §self-application 정합). Phase 2 (별 PR, Develop lane) carrier: `templates/scripts/result-fidelity-aggregator.py` `_actual_path_set()` (line 190-232) consumer-customization-preserve `.claude/_overlay/` prefix exclude pattern 추가 (existing `.snapshots/` prefix exclude pattern 동형, algorithm 재구현 0) + `tests/integration/test_reconcile_overlay_result_fidelity.bats` consumer fixture discriminating test (consumer `.claude/_overlay/project.yaml` 존재 → `result: SUCCESS` NOT `SUCCESS_WITH_DEGRADATION`)." }
  - { version: "1.11", date: 2026-05-19, carrier: CFP-991, change: "§4.3 (l) trigger 신설 발동 완료 — Wave 4 sub-Epic #1 Story-4 (Epic CFP-882) canary promotion criteria enforcement layer. §4.14 `canary_compatibility_check_binding` block 신설 (7 field: enabled / promotion_criteria_4tuple (functional + security + monitoring + testing 4-tuple measurement source SSOT — ADR-076 §결정 9.6 Chrome 3-channel verbatim) / family_7_atomic_canary_pin (publisher_versions[] length_invariant: 7 + member_enum codeforge family 7 plugin + three_way_match: bool publisher↔registry↔consumer) / canary_consumer_evidence_origin (enum [wrapper_self, consumer_self, mixed] open_extension: false closed-set) / inter_plugin_contract_backward_compat_verify (minor_only_rule_passed: bool ADR-008 §결정 2 invariant guard) / promotion_gate_failure_mode (enum [warning_first, blocking_on_pr] default warning_first + bypass_label: hotfix-bypass:canary-promotion-criteria) / downgrade_asymmetry_marker (status: placeholder_reserve, carrier_story: CFP-991-Story-5 단독 promotion 선례 §4.8 답습)). §4.3 (l) trigger 신설 발동 — Story-4 = §4.10 `registry_channel_matrix.story_4_scope_write_carrier` A3 정정 entry forward-effective realize point. §4.10 A3 정정 entry append — v1.8 A2 정정 ('populate = Story-4 carrier, Story-2 = read-only drift source') 의 realize → enact transition (v1.8 = predict / v1.11 = actualize, 두 statement 일관성 invariant). CFP-906 §11.4 line 454 historical record immutable 보존 (Layer-1 historical record = PMO retro 영역, Layer-2 live contract = forward-effective 정정 영역, DataMigrationArch §11.7 load-bearing dissent verbatim 채택). 5 threat × mitigation matrix carrier — T-1.1 wrapper Tier-1 declare-time bypass (canary_consumer_evidence_origin 명시 의무) / T-2.1 silent canary uptake CFP-906 답습 (canary_compatibility_check_binding 가 promotion gate 시점 declare runtime 효력 확인) / T-3.1 gate:channel-*-promotion label mis-attach (label-registry v2.35 attach_owner_plugin: consumer_repo_only + workflow `if: github.repository != 'mclayer/plugin-codeforge'` mechanical guard) / T-4.1 4-tuple measurement spoofing (minor_only_rule_passed + three_way_match + evidence_origin annotation, ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING cross-ref) / T-5.1 downgrade asymmetry (placeholder_reserve Story-5 carrier). label-registry-v2 v2.34 → v2.35 MINOR sibling carrier (4 신규 entry: 1 hotfix-bypass:canary-promotion-criteria + 3 gate:channel-{canary,beta,stable}-promotion). ADR-72 amendment_log Amendment 3 carrier (§결정 1 표 wrapper governance row append + §결정 5 표 row append). wrapper-self-app Tier-1 exemption invariant 보존 (ADR-72 §결정 6) — wrapper PR 자체 = declare-time 영역 (code 0 + runtime 0 + secret/credential 0 변경 invariant), consumer canary→beta promotion = Tier-2 admin-tier 권장 (advisory only). reconcile_strategy.status: 'placeholder_reserve' field-level 유지 (§4.8 version_handshake placeholder_reserve→active 단독 promotion 선례 답습 — partial-active state 도입 회피 = minimal-change). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — canary promotion criteria = enforcement layer wrapper-side declare, 의미 invariant 자체는 ADR-016 Amendment 3 가 family scope 의 channel 차원 declare). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — declare+runtime → enforcement, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 / (k) v1.10 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)). Live touching: TRUE (consumer canary→beta promotion gate enforcement) / production_cutover_touching: TRUE (ProductionEvidenceDeputy mandate first activation declare scope, ADR-72 §결정 1 정합) / marketplace_publish_touching: best_effort_declare (channels[] real populate carrier — Story-4 가 marketplace.json channels[] field 실 write/populate)." }
  - { version: "1.12", date: 2026-05-19, carrier: CFP-1014, change: "§4.3 (m) trigger 신설 발동 완료 — Wave 4 sub-Epic #1 Story-5 (Epic CFP-882 마지막 Story, 5/5 complete) downgrade asymmetry invariant 활성. §4.14 `downgrade_asymmetry_marker.status: 'placeholder_reserve' → 'wired'` 단독 promotion (§4.8 `version_handshake.status: placeholder_reserve → active` 단독 promotion 선례 verbatim 답습 — partial-active state 도입 0, field shape 변경 0, closed_enum length=2 invariant 보존). `carrier_story: 'CFP-991-Story-5' → 'CFP-1014'` carrier→realized 정정 (CFP-744 / CFP-745 carrier→realized 정정 패턴 답습, fact 영향 0 추적성만 ADR-068 I-4 wording SSOT 정합). `closed_enum: ['placeholder_reserve', 'wired']` 에 `open_extension: false` 명시 추가 (SecurityArch ratchet 강화 권고 — closed_enum invariant 명시화, downgrade_asymmetry_marker 의 enum 확장 차단 boundary 명문화). `activation_protocol` tense 갱신 (Story-5 Phase 1 = wired 활성 완료 forward-effective — '활성 완료' wording 으로 Phase 1 carrier post-merge state 반영). `sunset_justification` 본문 무변경 (DataMigrationArch risk surface 3 verbatim 채택 — asymmetry = directional ratchet 강화 0 invariant 보존, ADR-058 §결정 5 영역 외). §4.14 `out_of_scope.downgrade_path_runtime` comment '(Story-5 carrier placeholder_reserve)' → '(wired 활성 완료, downgrade execution runtime = 별 carrier)' 갱신 (placeholder→wired transition forward-effective 반영, runtime execution layer = sequential carrier disjoint declarative). §4.4 ratchet 보존 의무 row 7 append — `canary_compatibility_check_binding.downgrade_asymmetry_marker.status: wired → placeholder_reserve` 역방향 약화 차단 (ADR-058 §결정 5 sunset_justification 3-tuple 의무, ratchet 강화 only). 5 production-cutover cross-ref atomic sync sibling carrier (promotion-criteria-4tuple.md `downgrade scope 외` 영역 wired 갱신 + rollback-protocol.md Step 5a + CSC-4 wired cross-ref + README.md L48 Stage 5 MERGED transition + parallel-work/section-ownership.yaml CFP-1014 entry append + CLAUDE.md L263 + L289 cross-ref wired 갱신). Wave 4 sub-Epic #882 close marker — Story-5 = 5/5 Story complete carrier (predecessor lineage: CFP-906 v1.7 declare → CFP-932 v1.8 runtime activation → CFP-954 v2.34 production cutover → CFP-991 v1.11 promotion criteria → CFP-1014 v1.12 downgrade asymmetry final state). production_cutover_touching: FALSE (Story-3 CFP-954 가 production cutover declare layer carrier 완료, Story-5 = declare-only disjoint declarative SSOT only — ADR-72 §결정 6 wrapper-self-app N/A invariant 정합, ProductionEvidenceDeputy spawn 영역 외). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — downgrade asymmetry = directional ratchet declarative SSOT invariant 활성 only, family scope 무관). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — downgrade asymmetry invariant wired 활성 = forward-only ratchet 의 reverse-path 차단 declarative invariant 활성, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 / (k) v1.10 / (l) v1.11 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i) — string flip only, partial-active state 도입 회피 = minimal-change). Live touching: FALSE (Story-3 production cutover declare carrier 완료, Story-5 = declare-only disjoint declarative SSOT — runtime downgrade execution path = 별 future carrier OOS). marketplace_publish_touching: FALSE (channels[] real populate carrier = Story-4 CFP-991 forward-effective realize point, Story-5 = downgrade asymmetry declarative invariant 활성 only). consumer_impact_blast_radius: declare_only_no_runtime_demotion_execution (declarative SSOT only, runtime demotion execution path 부재 = invariant violation 0)." }
  - version: "1.13"
    date: 2026-05-21
    cfp: CFP-1125 (CFP-1111-W1-S1)
    change_type: status_transition
    summary: "status Active → Deprecated. CFP-1111 (Imperative changelog walk paradigm 도입) carrier. 3 binding (§4.3 (k)/(l)/(m) + §4.13/4.14 + §4.8) sunset declarative 동반 (Task 7/8/9 commit 874730f / 1847329 / 59ba458). imperative-walker-protocol-v1 (Wave 1 Story-3 codify) 가 후속 carrier."
    backward_compat: "PATCH bump (Deprecated marker only, semantic 변경 0)"
  - { version: "1.10", date: 2026-05-18, carrier: CFP-900, change: "§4.3 (k) trigger 신설 발동 완료 — Wave 4 sub-Epic CFP-858 S3 carrier (Epic CFP-858 마지막 Story — result fidelity honest reporting layer, mirror-후 temporal-post). §4.13 `result_fidelity_binding` block 신설 (6 sub-field schema: result_enum_schema / degradation_propagation / post_mirror_sanity_check / fast_pass_content_sanity / upgrade_event_honest_record / out_of_scope + ratchet_invariant_preserved). result enum 4-value closed-set (SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED) — exit code → result enum deterministic mapping (silent false SUCCESS 차단, Terraform `plan -detailed-exitcode` + Ansible `changed_when` honest reporting 동형). degradation_propagation: S1 §4.11 `fail_closed_behavior.on_dependency_missing: exit_1` → result FAILED·PARTIAL_FAILURE (부분 mirror 산출물 commit forbidden 정합) / S2 §4.12 `exit_code_contract: 1 = filter abort` → result FAILED / S1·S2 exit 2 degraded → result SUCCESS_WITH_DEGRADATION. post_mirror_sanity_check: ImpactReport diff (expected = wrapper SSOT path list S2 whitelist filter 적용 후, actual = consumer mirrored set, marker block 안 customization preserve 영역 제외) — filesystem-only invariant (network call 0 / gh api 0), syntax-level 1차 신호 (file 존재성 + path set diff + workflow yml `bash -n`/yaml parse OK, AM-3 derived default), pure read-only verify (idempotent — DataMigrationArch §11.6). fast_pass_content_sanity: phase-gate-mergeable `.github/workflows/*.yml` 의존 script reference mismatch detect — warning tier (AM-1 derived default, fast-pass OR-gate `isEpicLabel||isSiblingPr||isDocOnly||isPostMergeFix` 무변경 = orthogonal warning layer, blocking 승격 = evidence-checks-registry tier gate 충족 후 future CFP). upgrade_event_honest_record: result field 미기록/`SUCCESS` hardcode = forbidden, exit code → result enum mapping 의무 (CFP-898 silent_skip_invariant: 0 + ADR-076 §결정 6 wholesale_mirror_with_user_visible_loss_report honest reporting 강화 패턴 답습). hook_integration=scripts/reconcile-overlay.sh wholesale_mirror cp **후** post-mirror sanity check stage (S1 closure resolver hook → S2 filter hook → cp → post-mirror sanity check + result enum 집계 — mirror-전 S1/S2 vs mirror-후 sanity layer 분리 invariant). ADR-076 Amendment 3 §결정 3 sub-clause (transaction 사후 sanity check 위 result fidelity false SUCCESS 차단 clause — 의미 invariant marker_block_absent_behavior 무변경, sub-clause append = ratchet 강화 only) + ADR-026 Amendment 5 §결정 7 (`.github/` fast-pass content sanity 1차 신호 orthogonal warning layer — fast-pass OR-gate 무변경, gate 강화 방향) sibling carrier. mctrader-data#81 14 failing checks class 재발 차단 (post-mirror verify) + Epic CFP-858 §1 motivation 'upgrade-event 로그 result: SUCCESS 가 결함을 가린다' / 'fast-pass PASS → 전체 CI 마비 P0' 직접 해소. status: schema_declared_phase1 — Phase 1 = schema binding declare / Phase 2 (별 PR, Develop lane) = result enum 집계 + post-mirror sanity check + 실 rollback runtime (AM-4 derived default — Phase 1 over-commit 회피, CFP-898 §4.11 schema_declared_phase1 패턴 답습). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote / marker_block_absent_behavior 의미 무변경 (CFP-898 §4.11 + CFP-899 §4.12 binding block 패턴 verbatim 답습 + temporal-post result fidelity layer 1 추가만, algorithm 재구현 0 — ratchet 강화 only ADR-064 §self-application 정합). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, Phase 1 plugin.json bump 0 = marketplace_sync_declared:false / Phase 2 v5.91.0 3-file atomic 동반 예상). Live touching: FALSE (result fidelity = filesystem-only invariant, runtime 집계 = Phase 2 PR Develop lane carrier OOS). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)). [Phase 2 F-CR-900-3 clarification (no version bump — body 정확화, fact 영향 0, CFP-899 F-DR-899-3 'narrative 정정 body 정확' 패턴 답습, ADR-068 I-4 wording SSOT 정합): `post_mirror_sanity_check.impact_report_diff_scope` 에 actual-side 도 동일 S2 whitelist 기준 적용 명시 + `whitelist_symmetry_invariant` field 신설 — expected whitelist 적용 ↔ actual whitelist 미적용 비대칭 금지 (consumer mirror 된 whitelist 미등재 .yml 이 extra 에 항상 잔존 → false SUCCESS_WITH_DEGRADATION 차단). 의미 invariant 무변경 (기존 'EC-4 false-positive 차단' + 'S2 whitelist filter 결과 정합성 1차 검사' spec 의 actual-side 처리 explicit enumeration — ratchet 강화 only, ADR-064 §self-application 정합. ArchitectPL F-CR-900-3 root-cause 판정 = 구현 단일 수정 충분 (a), 명세 명확성 보강은 재발방지 동반 — 설계 결정 변경 0).]" }
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
  - ADR-070  # Codex verify-before-trust — §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING cross-ref §4.14 T-4.1 mitigation
  - ADR-72   # ProductionEvidenceDeputy mandate + EPIC cutover gate evidence quad — §4.14 §결정 5 production cutover gate semantic SSOT (CFP-991 Story-4 carrier — Amendment 3 carrier)
  - ADR-083  # consumer-applicability filter — wrapper-side filter mechanism SSOT (v1.9 §4.12 carrier ADR, CFP-899 sibling)
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
- version_handshake 3-way binding (Wave 3 Story-6 CFP-820 carrier — v1.5 active, §4.8 version_handshake_3way_binding block. ADR-063 Amendment 5 §결정 15)
- coverage fan-out D1/D2/D3 (Wave 3 Story-7 CFP-821 carrier — v1.6 active, §4.9 coverage_fan_out_implementation_binding block. ADR-027 Amendment 5 §결정 9 + ADR-076 §결정 2 표 PR template row)
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
    status: "active"   # CFP-820 Wave 3 Story-6 §4.3 (e) trigger 발동 — placeholder_reserve → active (Wave 1 Story-1 CFP-701 사전 declare 실현)
    validation_status_v1_5: "normative — v1.5 consumer enforce (3-way version parity validator active). validator (scripts/check-3way-version-parity.sh Phase 2 carrier) 가 publisher↔registry↔`consumer pin` 3-way byte-identical version 검증"  # CFP-820 정정: 旧 validation_status_v1_0 "non_normative_placeholder_reserve — v1.0 consumer ignore" → v1.5 normative rename (3 stale placeholder 정정 (2) — CFP-744/745 stale 정정 패턴, fact 영향 0 추적성만 ADR-068 I-4)
    becomes_normative_at_version: "v1.5 (CFP-820 Wave 3 Story-6 carrier MINOR bump 시점 — 旧 stale \"v1.1\" 정정: Wave 1 작성 시점 placeholder, 현재 v1.4 → carrier 시점 v1.5. CFP-744 v1.0→v1.1 stale 정정 precedent 답습, fact 영향 0 추적성만)"
    carrier_story: "CFP-820"  # 3-way version atomic invariant 확장 (旧 placeholder "CFP-Wave-3-Story-6" → 실제 Issue KEY CFP-820 실현. Wave 1 Story-1 CFP-701 사전 declare 의 carrier 확정 — carrier reservation → realized, ADR-027 §결정 7.A.1 carrier 실현 패턴 동형)
    semantic_intent: "publisher (wrapper .claude-plugin/plugin.json .version) ↔ registry (mclayer/marketplace .claude-plugin/marketplace.json .plugins[name=codeforge].version) ↔ consumer (.claude/_overlay/project.yaml .codeforge.version_pin.version) 3-way byte-identical version handshake (ADR-063 Amendment 5 §결정 15 carrier)"
    field_schema_active: "§4.8 version_handshake_3way_binding block (3-way binding semantic — CFP-820 v1.4 → v1.5. 旧 stale field_schema_future \"TBD (...v1.0 → v1.1)\" → active schema 정정, CFP-745 carrier→realized 정정 패턴 답습)"
  
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
      - "codemod_apply"  # Wave 4 sub-Epic #2 carrier (jscodeshift-inspired) — status: placeholder_reserve (unchanged, CFP-906 partial activation 영역 외)
      - "multi_version_channel_pin"  # Wave 4 sub-Epic #1 carrier (3-tier channel taxonomy stable/beta/canary) — status: ACTIVE (CFP-906 §4.3 (i) trigger v1.7 발동, §4.10 multi_version_channel_pin_binding block carrier). reconcile_strategy.status field-level "placeholder_reserve" 유지 = partial activation invariant (§4.8 version_handshake.status placeholder_reserve → active 단독 promotion 선례 답습 — partial-active state 도입 회피 = minimal-change ADR-064)
      - "uninstall_cleanup"  # Wave 4 sub-Epic #3 carrier (reverse direction) — status: placeholder_reserve (unchanged, CFP-906 partial activation 영역 외)

# === Placeholder field validation semantic SSOT (FIX iter 1 / Codex TP#2 F-003 — CFP-820 v1.5 갱신) ===
# contract validator (`scripts/check-inter-plugin-contracts.sh`) 의 placeholder field skip 의무:
# - status: "placeholder_reserve" 보유 field = validator schema validation skip (non-normative)
# - validation_status_v1_<N> 명시 의무 (active 시 "normative — v1.<N> consumer enforce" / placeholder 시 "non_normative_placeholder_reserve — v1.<N> consumer ignore" 또는 동등)
# - becomes_normative_at_version 명시 의무 (활성 carrier version)
# CFP-820 Wave 3 Story-6 §4.3 (e) trigger 발동 후 상태:
# - version_handshake: status "active" (v1.5 normative — §4.8 version_handshake_3way_binding block. carrier_story CFP-820 실현)
# - reconcile_strategy: status "placeholder_reserve" 유지 (enum_reserved_wave_4 = Wave 4 sub-Epic carrier, becomes_fully_normative_at_version v2.0)
# 본 SSOT = placeholder → active promotion path 의 검증 prerequisite (version_handshake 가 첫 promotion 실현 사례 — CFP-820).
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
- **ADR-063 Amendment 5 §결정 15 (3-way version atomic invariant — CFP-820)**: 본 contract §4.8 `version_handshake_3way_binding` block 의 carrier ADR. version_handshake placeholder → active 활성 + publisher↔registry↔`consumer pin` 3-way byte-identical invariant + warning-first→blocking fallback orthogonality. (Story §1-§6 'Amendment 4' = frontmatter 미검증 — CFP-686=amendment:4 점유, 설계 lane strict-verify Amendment 5 정정.)
- **ADR-027 Amendment 4 (consumer adoption protocol — CFP-820)**: 본 contract §4.8 `consumer pin` (`codeforge.version_pin`) schema detection 의 cross-ref. project-config-schema MINOR + validate_config.py validator (Phase 2 carrier).
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
- (e) Wave 3 Story-6 (CFP-820) merge — `version_handshake` field 활성. **v1.5 발동 완료 (본 contract)** — `version_handshake.status: placeholder_reserve → active` + §4.8 `version_handshake_3way_binding` block 신설 (publisher↔registry↔`consumer pin` 3-way byte-identical invariant + warning-first→blocking fallback orthogonality + read-only lint scope + sanity guard 6-tuple — ADR-063 Amendment 5 §결정 15 carrier). 3 stale placeholder 정정 (`becomes_normative_at_version: "v1.1" → "v1.5"` / `validation_status_v1_0` key → `validation_status_v1_5` rename + value normative / `field_schema_future` "TBD v1.0→v1.1" → `field_schema_active` §4.8 reference — CFP-744 v1.0→v1.1→v1.2→v1.3 / CFP-745 carrier→realized 정정 패턴 답습, fact 영향 0 추적성만 ADR-068 I-4 wording SSOT). carrier_story placeholder "CFP-Wave-3-Story-6" → 실제 Issue KEY "CFP-820" 실현 (Wave 1 Story-1 CFP-701 사전 declare 의 carrier 확정). 의미 invariant 변경 0 (3-way version invariant = runtime catch-up, ADR-016 §결정 1 SSOT 무변경). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).
- (f) Wave 4 sub-Epic merge — `reconcile_strategy.enum_reserved_wave_4` 값 활성
- (g) Wave 2 Story-5 (CFP-745) merge — overlay 영역 (skill/agent/hook) 3-way merge reconcile runtime (`scripts/reconcile-overlay.sh` 신설, Phase 2 carrier). **v1.4 발동 완료 (본 contract)** — §4.7 `overlay_reconcile_implementation_binding` block 신설 (per-file 3-way merge layer + marker_preserve_binding + sidecar_manifest_schema + base_acquisition_binding). marker_block_syntax.comment_prefix_per_filetype.json `carrier: "Wave 2 Story-5"` → `realized_in` cross-ref (carrier reservation → realized — ADR-027 §결정 7.A.1 carrier 실현, AC-10 contract integration OUTCOME). §1 out-of-scope "3-way merge runtime (overlay reconcile, Wave 2 Story-5 carrier)" = 본 trigger 발동으로 carrier-declare → realized (단 §1 OOS 표기는 "Wave 2 Story-5 carrier" 추적성 유지 — carrier 가 §4.7 로 realized 됨을 표기). 의미 invariant 변경 0 (overlay reconcile = runtime catch-up, ADR-076 §결정 1 SSOT). §4.3 (c) v1.2 / (d) v1.3 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).
- (h) Wave 3 Story-7 (CFP-821) merge — coverage fan-out D1/D2/D3 (Issue/PR template fan-out + branch protection setup helper FORM (b) + script boundary taxonomy, Phase 2 carrier 실 file). **v1.6 발동 완료 (본 contract)** — §4.9 `coverage_fan_out_implementation_binding` block 신설 (D1 `templates/.github/ISSUE_TEMPLATE/*.yml` 5 forms + config.yml + `templates/.github/PULL_REQUEST_TEMPLATE.md` byte-identical mirror + D4 marker form-level wrap §결정 7.A.1 / D2 `templates/scripts/setup-branch-protection.sh` manifest 합성 + dry-run preview only — API write 0 / D3 `docs/script-boundary.md` 3 category declarative taxonomy). reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` (marker-aware 2-way / wholesale_mirror_with_user_visible_loss_report) SSOT 재사용 (D1 `.github/` 영역 area handler 추가, algorithm 재구현 0). ADR-027 Amendment 5 §결정 9 (Issue Forms enumeration 정정 3종 → 5 forms + config.yml + D4 marker cross-ref) + ADR-076 §결정 2 표 PR template row append carrier 동반. ADR-066 무변경 (FORM (b) — Administration:write grant 0, F-P1-A 해소 = scope-down OOS, least-privilege ratchet-safe). 의미 invariant 변경 0 (coverage fan-out = self-app enumeration 확장, ADR-076 §결정 1/§결정 2 SSOT). § "Amendment / version 번호 정정": ADR-027 carrier = Amendment 5 §결정 9 (Story §1-§6 'Amendment 4' = frontmatter 미검증 — CFP-820 이 amendment 4 / §결정 8 점유, 설계 lane strict-verify Amendment 5 §결정 9 정정) / 본 contract version = v1.6 §4.3 (h) (Story-7 §3.5 'v1.5 §4.3 (h)' = Story-6 collision 점유, CFP-820 이 v1.5 §4.3 (e) 점유 → 설계 lane strict-verify origin/main direct Read 후 v1.6 §4.3 (h) 정정, Codex TP#2 verify-before-trust 8-mirror 교훈, CFP-820 §4.3 (e) Amendment 번호 정정 패턴 답습). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).
- (i) Wave 4 sub-Epic #1 Story-1 (CFP-906) merge — `multi-version channel pin declare layer` (Epic CFP-882). **v1.7 발동 완료 (본 contract, 1st carrier)** — `reconcile_strategy.enum_reserved_wave_4[multi_version_channel_pin]` placeholder → ACTIVE (partial activation — `codemod_apply` / `uninstall_cleanup` 2 entry 무변경, CFP scope unitary ADR-064 §결정 1.3 정합). §4.10 `multi_version_channel_pin_binding` block 신설 (3-tier channel taxonomy stable/beta/canary + consumer `.claude/_overlay/project.yaml codeforge.channel` field SSOT + `family_7_plugin_atomic × channel pin invariant` + per-channel marketplace.json channels[] matrix + 3-way channel invariant publisher↔registry↔consumer 확장). ADR-076 §결정 9 (3-tier channel taxonomy declaration) + ADR-016 Amendment 3 (`family_7_plugin_atomic × channel pin invariant`) + ADR-063 Amendment 6 §결정 17 (mirrored field × channel matrix) + project-config-schema MINOR (codeforge.channel field 신설) + label-registry-v2 v2.29 → v2.30 MINOR (channel:stable / channel:beta / channel:canary 3 신규 label + 신규 category enum `channel`) carrier 동반. `reconcile_strategy.status: "placeholder_reserve"` field-level 유지 (§4.8 `version_handshake.status: placeholder_reserve → active` 단독 promotion 선례 답습 — partial-active state 도입 회피 = minimal-change). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — `channel pin` = runtime catch-up layer 확장만, 의미 invariant 자체는 ADR-016 Amendment 3 가 family scope 의 channel 차원 declare). MINOR bump (kind:registry sibling sync 면제). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — `multi-version channel pin coverage` 확장, ADR-064 §self-application 정합). Live touching: FALSE (declare layer scope — Story-1 = schema SSOT only, runtime UpgradeAgent multi-channel dispatch = Wave 4 sub-Epic #1 Story-2 carrier, ProductionEvidence canary tier activation = Wave 4 sub-Epic #1 Story-3 carrier — ADR-72 §결정 1 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).
- (i) Wave 4 sub-Epic CFP-858 S1 (CFP-898) merge — dependency bundle integrity (closure resolver fail-closed semantic). **v1.7 발동 완료 (본 contract, 2nd carrier — CFP-906 §4.3 (i) 1st carrier 와 같은 version v1.7, 두 trigger 동일 번호 공동 적용)** — §4.11 `dependency_bundle_integrity_binding` block 신설 (MARKER_NONE wholesale_mirror branch 진입 전 workflow yml + 의존 `scripts/check-*.sh` / `templates/scripts/*.py` closure atomic bundle invariant + missing 시 fail-closed exit 1 + visible error log + 부분 mirror 산출물 commit 금지). reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` (MARKER_NONE wholesale_mirror branch) SSOT 재사용 (closure resolver layer 1 추가, algorithm 재구현 0). ADR-076 Amendment 2 §결정 2 11번째 row append (`scripts/` workflow_dependency_closure, bundled_with_referencing_workflow) + §결정 6 fail-closed clause sub-section carrier 동반 (의미 invariant `marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report` 무변경 — sub-clause 1 추가 = ratchet 강화 only, ADR-064 §self-application 정합). closure_resolve_algorithm: regex_primary (AM-1 derived default — stdlib only) / transitive_depth_limit: 1 (AM-2 — false-positive 폭증 회피) / dependency_scope: shell_script_only_v1 (AM-3 — .sh + .py 패턴, runtime 의존 + dynamic fetch out-of-scope) / self_app_exemption: templates/scripts/mirror-dependency-closure.py (AM-4 — consumer-distributable, ADR-005 byte-identical mirror rule 면제 영역, self-loop 0 invariant). mctrader-data#81 14 failing checks evidence (Epic CFP-858 §1 motivation verbatim). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2). 의미 invariant family_7_plugin_atomic 변경 0 (ADR-016 §결정 1 SSOT 무변경 — closure resolve = wholesale_mirror atomic bundle 강화 only). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).
- (k) Wave 4 sub-Epic CFP-858 S3 (CFP-900) merge — result fidelity (upgrade-event 정직 + post-mirror sanity check + phase-gate fast-pass content sanity, mirror-후 temporal-post honest reporting layer). **v1.10 발동 완료 (본 contract)** — §4.13 `result_fidelity_binding` block 신설 (result enum 4-value closed-set `SUCCESS`/`SUCCESS_WITH_DEGRADATION`/`PARTIAL_FAILURE`/`FAILED` + exit code → result enum deterministic mapping + post-mirror ImpactReport diff sanity check filesystem-only syntax-level 1차 신호 + phase-gate-mergeable `.github/` 의존 script reference content sanity warning tier orthogonal layer + upgrade-event honest record false SUCCESS 차단). degradation_propagation: S1 §4.11 fail-closed (exit 1) → result `FAILED`·`PARTIAL_FAILURE` (부분 mirror 산출물 commit forbidden 정합) / S2 §4.12 abort (exit 1) → result `FAILED` / S1·S2 exit 2 degraded → result `SUCCESS_WITH_DEGRADATION` (silent SUCCESS 거짓 기록 차단). reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` (MARKER_NONE wholesale_mirror branch) SSOT 재사용 — result fidelity layer 1 추가 (post-mirror sanity check + result enum 집계 stage, algorithm 재구현 0). CFP-898 §4.11 vertical closure resolver (mirror-전) + CFP-899 §4.12 horizontal consumer-applicability filter (mirror-전) 위 stacked — mirror-**후** temporal-post layer (3-layer composite 완결, Epic CFP-858 마지막 Story). hook order: CFP-898 closure resolver → CFP-899 consumer-applicability filter → cp → CFP-900 post-mirror sanity check + result enum 집계. ADR-076 Amendment 3 §결정 3 sub-clause (transaction 사후 sanity check 위 result fidelity false SUCCESS 차단 clause — 의미 invariant `marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report` 무변경, sub-clause append = ratchet 강화 only, ADR-064 §self-application 정합) + ADR-026 Amendment 5 §결정 7 (`.github/` fast-pass content sanity 1차 신호 orthogonal warning layer — fast-pass OR-gate 무변경, gate 강화 방향) sibling carrier. closure semantic 재사용 + sequential composition layer 1 추가만, algorithm 재구현 0. status: schema_declared_phase1 — Phase 1 = schema binding declare / Phase 2 (별 PR, Develop lane) = result enum 집계 + post-mirror sanity check + 실 rollback runtime (AM-4 derived default — Phase 1 over-commit 회피, CFP-898 §4.11 schema_declared_phase1 패턴 답습). result_enum_schema: 4-value (AM-2 derived default file path set diff syntax-level / AM-3 derived default syntax-level 1차 신호 stdlib only) / fast_pass_content_sanity: warning tier (AM-1 derived default — fast-pass 정책 약화 = ADR-064 ratchet 위배 회피). filesystem-only invariant (network call 0 / gh api 0 — post-mirror diff = consumer 권한 area, trust surface 0, SecurityArch primary). mctrader-data#81 14 failing checks class 재발 차단 (post-mirror verify) + Epic CFP-858 §1 motivation verbatim ('upgrade-event 로그 `result: SUCCESS` ... 가 결함을 가린다' / 'fast-pass PASS → 전체 CI 마비 P0급 피해'). 의미 invariant family_7_plugin_atomic 변경 0 (ADR-016 §결정 1 SSOT 무변경 — result fidelity = wholesale_mirror branch temporal-post honest reporting layer 1 추가만). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, Phase 1 plugin.json bump 0 = marketplace_sync_declared:false / Phase 2 v5.91.0 3-file atomic 동반 예상). 신규 ADR 미신설 (S3 = ADR-026 Amd5 + ADR-076 Amd3 ratchet 강화로 충분 — S1 ADR-076 Amd2 / S2 ADR-083 신규 와 비대칭, Architect lane minimal-change 결정. ADR-RESERVATION max row 83 = CFP-899 점유, row 84 reserve 불요). user_decision_branches: 0 / atomicity_boundary_semantic_invariant: family_7_plugin_atomic / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote / marker_block_absent_behavior 의미 무변경 (CFP-898 §4.11 + CFP-899 §4.12 binding block 패턴 verbatim 답습 — ratchet 강화 only, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).
- (m) Wave 4 sub-Epic #1 Story-5 (CFP-1014) merge — downgrade asymmetry invariant wired 활성 (Epic CFP-882 마지막 Story, 5/5 complete). **v1.12 발동 완료 (본 contract)** — §4.14 `downgrade_asymmetry_marker.status: placeholder_reserve → wired` 단독 promotion (§4.8 `version_handshake.status: placeholder_reserve → active` 단독 promotion 선례 verbatim 답습 — partial-active state 도입 0, field shape 변경 0, closed_enum length=2 invariant 보존). `carrier_story: 'CFP-991-Story-5' → 'CFP-1014'` carrier→realized 정정 (CFP-744 / CFP-745 carrier→realized 정정 패턴 답습 — fact 영향 0 추적성만, ADR-068 I-4 wording SSOT 정합). `closed_enum` 에 `open_extension: false` 명시 추가 (SecurityArch ratchet 강화 권고 — closed_enum invariant 명시화, downgrade_asymmetry_marker enum 확장 차단 boundary 명문화, ADR-064 §self-application 정합 강화 방향). `activation_protocol` tense 갱신 (Story-5 Phase 1 = wired 활성 완료 forward-effective). `sunset_justification` 본문 무변경 (DataMigrationArch risk surface 3 verbatim — asymmetry = directional ratchet 강화 0 invariant, ADR-058 §결정 5 영역 외). §4.14 `out_of_scope.downgrade_path_runtime` comment 갱신 (placeholder→wired transition forward-effective, runtime execution layer = sequential carrier disjoint declarative). §4.4 ratchet 보존 의무 row 7 append — `canary_compatibility_check_binding.downgrade_asymmetry_marker.status: wired → placeholder_reserve` 역방향 약화 차단 (ADR-058 §결정 5 sunset_justification 3-tuple 의무, ratchet 강화 only). 5 production-cutover cross-ref atomic sync sibling carrier (promotion-criteria-4tuple.md L86-L88 + rollback-protocol.md L75 Step 5a + L91 CSC-4 + README.md L48 Stage 5 + section-ownership.yaml CFP-1014 entry append). Wave 4 sub-Epic #882 close marker (Story-5 = 5/5 Story complete final state). 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경 — downgrade asymmetry = directional ratchet declarative SSOT invariant 활성 only, family scope 무관). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — downgrade asymmetry invariant wired 활성 = forward-only ratchet 의 reverse-path 차단 declarative invariant, ADR-064 §self-application 정합). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 / (k) v1.10 / (l) v1.11 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i) — string flip only). Live touching: FALSE (Story-3 production cutover declare carrier 완료, Story-5 = declare-only disjoint declarative SSOT only — runtime downgrade execution path = 별 future carrier OOS). production_cutover_touching: FALSE (Story-3 CFP-954 carrier 완료 disjoint, ADR-72 §결정 6 wrapper-self-app N/A invariant 정합) / marketplace_publish_touching: FALSE (channels[] real populate carrier = Story-4 CFP-991 forward-effective realize point) / consumer_impact_blast_radius: declare_only_no_runtime_demotion_execution.

- (l) Wave 4 sub-Epic #1 Story-4 (CFP-991) merge — canary promotion criteria enforcement layer (Epic CFP-882). **v1.11 발동 완료 (본 contract)** — §4.14 `canary_compatibility_check_binding` block 신설 (7 field). 본 trigger = Story-4 = §4.10 `registry_channel_matrix.story_4_scope_write_carrier` A3 정정 entry forward-effective realize point — v1.8 A2 정정 ('populate = Story-4 carrier, Story-2 = read-only drift source') 의 realize → enact transition. CFP-906 §11.4 line 454 historical record immutable 보존 (Layer-1 historical record = PMO retro 영역 / Layer-2 live contract = forward-effective 정정 영역, DataMigrationArch §11.7 load-bearing dissent verbatim 채택). 5 threat × mitigation matrix carrier (T-1.1/T-2.1/T-3.1/T-4.1/T-5.1) — 5 field 가 schema layer carrier. label-registry-v2 v2.34 → v2.35 MINOR sibling carrier (4 신규 entry). ADR-72 amendment_log Amendment 3 carrier. ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING cross-ref §7.6 T-4.1 mitigation. wrapper-self-app Tier-1 exemption invariant 보존 (ADR-72 §결정 6) — wrapper PR 자체 = declare-time 영역, consumer canary→beta promotion = Tier-2 admin-tier 권장. 의미 invariant `atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT 무변경). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). user_decision_branches: 0 / atomicity_boundary semantic / marker_block_absent_behavior / snapshot_reset_disjoint_layer / transaction.completion_criterion / adr_053_d2_verbatim_quote 무변경 (ratchet 강화 only — declare+runtime → enforcement). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 / (j) v1.9 / (k) v1.10 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)). Live touching: TRUE (consumer canary→beta promotion gate enforcement) / production_cutover_touching: TRUE (ProductionEvidenceDeputy mandate first activation declare scope, ADR-72 §결정 1 정합) / marketplace_publish_touching: best_effort_declare.

- (j) Wave 4 sub-Epic CFP-858 S2 (CFP-899) merge — consumer-applicability filter (repo-kind detection truth-table + positive whitelist horizontal filter layer). **v1.9 발동 완료 (본 contract)** — §4.12 `consumer_applicability_filter_binding` block 신설 (4-way enum closed-set `plugin`/`consumer`/`mixed`/`unknown` + positive whitelist `consumer_applicable_workflows.txt` + mixed repo full workflow set exemption + fail-closed unknown semantic + hook insertion point CFP-898 §4.11 hook pattern 답습 sequential composition). ADR-083 신규 §결정 1-6 (wrapper-side filter mechanism SSOT — 4-way enum + positive whitelist + mixed exemption + fail-closed unknown + hook insertion point + wrapper self-app verify) + ADR-027 Amendment 6 §결정 10 (consumer-side signal SSOT — filesystem-only 2-signal cross-product `.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 4-way truth-table + signal semantic invariant + wrapper self-app exemption + fail-closed unknown + boundary disjoint invariant) sibling carrier. CFP-898 §4.11 vertical closure resolver 와 sequential composition (filter 먼저 → closure 다음 = hook order: CFP-898 closure resolver → CFP-899 consumer-applicability filter → cp). exit_code_contract: 0 = filter OK + proceed to cp / 1 = filter abort (unknown repo_kind / detect-repo-kind.py error) → return 1 ABORT (CFP-898 return 2 와 분리 — filter 는 return 1) / 2 = filter warning (degraded — Phase 2 reserve). filesystem-only invariant (network call 0 / gh api 0 / marketplace.json membership check 0 — offline-first + trust boundary 명확 + primary signal 단일 read 비용 < 1ms, SecurityArch + OpRiskArch deputy primary recommendation). mctrader-data#81 14 failing checks horizontal filter layer evidence (Epic CFP-858 결함 2 root cause — wrapper-only workflow 무차별 유입 silent harm super-class — CFP-898 closure missing 차단의 dual axis). MINOR bump (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 2, plugin.json bump 0 = marketplace_sync_declared:false). 의미 invariant family_7_plugin_atomic 변경 0 (ADR-016 §결정 1 SSOT 무변경 — consumer-applicability filter = wholesale_mirror branch horizontal gating layer 1 추가만). §4.3 (c) v1.2 / (d) v1.3 / (g) v1.4 / (e) v1.5 / (h) v1.6 / (i) v1.7 trigger + binding block 패턴 verbatim 답습 (§2.5 FORM 옵션 (i)).

### §4.3 (k) sunset boundary (CFP-1111 carrier)

본 binding (dependency_bundle_integrity_binding, v1.10 CFP-900 carrier) 는 CFP-1111 walker paradigm 으로 carry.

- **metric**: walker 의 walk entry 가 dependency bundle integrity check 동일 enforce + bundle 부분 적용 0건 / N walk
- **who**: imperative-walker-protocol-v1 walker schema field `dependency_bundle_check` + UpgradeAgent
- **how**: walker integration test 안 dependency bundle integrity semantic equivalent + ADR-076 sunset 후 carrier 이전 (Wave 1 Story-3)

### §4.3 (l) sunset boundary

본 binding (consumer-applicability binding, v1.11) 는 ADR-083 sunset 정합 — walker `applicable_to` field 로 carry. ADR-083 sunset_justification 참조 (Task 2 commit `1da0b2e`).

### §4.3 (m) sunset boundary

본 binding (result_fidelity_binding, v1.10 §4.13 사전 carrier) 는 ADR-026 Amendment 5 sibling carrier role sunset 정합 — walker `walk_result` 4-value enum carry. Task 3 commit `f1c4c97` 참조.

### 4.4 Ratchet 보존 의무 (downgrade 차단)

본 contract 의 모든 Amendment 는 강화 방향만 허용 (ADR-064 top-down self-application). 약화 방향 차단:

- `user_decision_branches: 0` invariant 약화 = ADR-058 §결정 5 sunset_justification 3-tuple 차단
- `snapshot_reset_disjoint_layer.declared: true → false` = 차단 (ADR-067 cross-pollinate risk)
- `transaction.completion_criterion.adr_053_d2_cross_ref: true → false` = 차단 (consumer 배포 누락 risk)
- `transaction.completion_criterion.adr_053_d2_verbatim_quote` modification = 차단 (FIX iter 1 / Codex TP#2 F-004 — verbatim weakening risk, ADR-053 §D2 SSOT 정합)
- `transaction.atomicity_boundary_semantic_invariant: family_7_plugin_atomic` 약화 = ADR-016 §결정 1 변경 trigger 의무 (별도 carrier)
- `desired_state_domains[]` row 삭제 = 차단 (자기 영역 축소 = self-app coverage 후퇴)
- `canary_compatibility_check_binding.downgrade_asymmetry_marker.status: wired → placeholder_reserve` 역방향 약화 = 차단 (v1.12 CFP-1014 Story-5 carrier — directional ratchet 강화 only, demotion declarative invariant 활성 회귀 차단, ADR-058 §결정 5 sunset_justification 3-tuple 의무. SecurityArch T-5.1 mitigation core field 의 wired 상태 보존 — closed_enum 확장 0 invariant 동반 보호)

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
    semantic: "7 plugin `version pin` sync = 단일 atomic unit (부분 실패 = 전체 7 plugin atomic rollback, Epic EPIC-AC-3 verbatim)"
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

### 4.8 Wave 3 Story-6 version_handshake 3-way binding (v1.5 — CFP-820 §4.3 (e) trigger 발동, ADR-063 Amendment 5 §결정 15 carrier)

본 §4.5 (per-plugin) / §4.6 (per-family) / §4.7 (overlay) mechanical_implementation_binding 위에 **version_handshake 3-way binding layer** 1단을 추가한다. version_handshake placeholder (Wave 1 Story-1 CFP-701 사전 declare `carrier_story: CFP-Wave-3-Story-6`) 의 realized 영역 (placeholder_reserve → active, ADR-027 §결정 7.A.1 carrier 실현 패턴 동형). per-plugin/per-family/overlay reconcile semantic = §4.5/§4.6/§4.7 SSOT 재사용 (변경 0), version provenance 3-way invariant 만 신설.

```yaml
version_handshake_3way_binding:   # v1.5 신설, CFP-820 §4.3 (e) 발동
  carrier_story: CFP-820  # Wave 3 Story-6 (Epic CFP-699 B2 — 3-way version atomic invariant)
  carrier_adr: "ADR-063 Amendment 5 §결정 15"   # 설계 lane strict-verify 정정: Story §1-§6 'Amendment 4' = frontmatter 미검증 (CFP-686=amend:4 점유) → Amendment 5 (Codex TP#2 verify-before-trust 8-mirror 교훈)
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = scripts/check-3way-version-parity.sh 실 구현
  entrypoint: "scripts/check-3way-version-parity.sh"   # 3-way read-only version parity lint (per-plugin = §4.5 / per-family = §4.6 / overlay = §4.7 SSOT 재사용, semantic 분산 0). check-version-bump-atomic.sh 166-line 2-way pattern 답습 + `consumer pin` sub-check 1 추가
  three_way_layers:
    publisher: ".claude-plugin/plugin.json .version (plugin repo 예: mclayer/plugin-codeforge — same-repo local read, auth 불요)"
    registry: ".claude-plugin/marketplace.json .plugins[name=codeforge].version (mclayer/marketplace — gh api repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json, ADR-066 §결정 2 marketplace contents:read reuse)"
    consumer_pin: ".claude/_overlay/project.yaml .codeforge.version_pin.version (consumer project repo — same-repo local read, consumer-authored, codeforge agent write 금지 invariant 절대 보존 project-config-schema §4b)"
  changelog_exclusion: "CHANGELOG.md 3-way 미포함 — wrapper plugin.json same-PR sibling (기존 invariant-check workflow plugin.json↔CHANGELOG version field 이미 enforce, ADR-063 §결정 1 base scope). 4-way = 중복 coverage (ADR-064 minimal-change 위배). 3-way (publisher↔registry↔`consumer pin`) = 최소 충분 set"
  invariant: "3 layer byte-identical version string (exact-string match — semver normalize 안 함: 5.81.0 ≠ 5.81 ≠ v5.81.0 모두 mismatch. publisher SSOT canonical, consumer verbatim mirror 의무)"
  orthogonality_invariant: "`pin` 가용성 (consumer 가 codeforge.version_pin 등록했는가 = enforce 가능 여부) 과 version 정합성 (`pin` 값이 publisher/registry 와 일치하는가 = drift 존재 여부) 은 ORTHOGONAL 2 조건 — 동일 fallback 에 conflate 금지 (CFP-745 FIX Iter 2 base-absent≠marker-absent verified-true precedent 답습. conflate 시 결함: `pin` 미등록 신규 consumer 즉시 blocking = onboarding 마찰 false-positive / `pin` 등록 consumer 실 drift 가 warning 약화 false-negative)"
  fallback_semantic:   # 사용자 confirm 2026-05-17 KST — ADR-027 Amendment 2 bootstrap.fallback_mode 패턴 답습
    pin_absent: "warning-first (lint skip + warn message '`consumer pin` SSOT 미등록 — codeforge.version_pin 등록 후 3-way enforce 활성' + exit 0). `pin` 부재 = mismatch 판정 불성립 (비교 대상 없음, false-positive 차단). onboarding 마찰 0"
    pin_present_match: "PASS (exit 0)"
    pin_present_mismatch: "blocking FAIL (exit 1, blocking-on-pr). drift 0 strict enforce (등록 영역). mismatch layer 명시 (wrapper-only / marketplace-only / `consumer-pin-only` / 2-layer)"
  read_only_scope:
    write_surface: 0   # publisher↔registry 무변경 + `consumer pin` = consumer-authored + lint = compare-only
    pat_scope: "ADR-066 §결정 2 5-scope set 중 marketplace contents:read (Amendment 2 이미 grant) reuse. Amendment 3 reconcile-target-repos contents:write+pull_requests:write 미사용 (lint = compare-only, write 0, PR open 0). 추가 PAT grant 0 invariant (least-privilege)"
  sanity_guard_6tuple:   # CFP-745 retro carry (i) marketplace_sync_5_81.py 6-guard pattern 답습 (첫 carrier reference impl, ADR-070 verify-before-trust + carry (j) gh api blob sha empty-detection 사전 단계)
    - "(1) size > 40000 (empty-blob/truncated fetch 방어 — CFP-745 P0 gh api blob sha empty-blob e69de29b incident lineage)"
    - "(2) JSON parse (malformed JSON 방어)"
    - "(3) 4-field parity (codeforge entry name/version/description/author — ADR-016 mirrored field 정합)"
    - "(4) 6 non-codeforge byte-identical (sister plugin entry untouched verify — read-only invariant 자기증명)"
    - "(5) git diff stat single-line (version 변경 single-line edit invariant — Phase 2 self-app PR)"
    - "(6) global version pattern unique (multi-version collision detect — wrong-match 차단)"
  fetch_failure_3branch:   # ADR-068 I-3 guard placement intent — §결정 13 E-4 패턴 답습 (single fail-closed 추상화 회피)
    "401": "fail-closed (PAT expired manual blocker, exit 2 actionable). 다음 run 자연 회복 불가"
    "429": "fail-open (rate-limit, warning log + exit 0 다음 run 회복). false-negative 24h delay < false-positive Issue 발의"
    "5xx_network": "fail-closed-with-retry (in-run 3회 exponential backoff 1s/2s/4s 후 exit 2). transient spike 회복 patch"
  reconcile_pr_scope_binding:
    cross_ref: "본 lint = compare-only — ADR-066 Amendment 3 reconcile-target write scope 무관 (read-only). §4.5 reconcile_pr_scope_binding 과 disjoint layer"
    pr_open: false   # lint = PR-time CI check (read-only), PR open 행위 0
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.5 = 강화 only (3-way version invariant 확장), weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 — 3-way version invariant = runtime catch-up only)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (ADR-027 §결정 7.C)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden (`consumer pin` = consumer-authored, snapshot layer 무관)
    adr_053_d2_verbatim_quote: unchanged               # L150-151 weakening 차단
```

Phase 1 (CFP-820) merge 시 본 §4.8 binding block 활성 (schema declare — version_handshake placeholder_reserve → active). Phase 2 (별 PR) merge 시 `scripts/check-3way-version-parity.sh` 실 구현 + `templates/github-workflows/version-3way-atomic.yml` + `.github/workflows/version-3way-atomic.yml` byte-identical self-app + `docs/evidence-checks-registry.yaml` `version-3way-atomic` entry (blocking-on-pr) + consumer `.claude/_overlay/project.yaml codeforge.version_pin` 실 등록 시 3-way version parity mechanical 활성.

### §4.8 sunset boundary (CFP-1111 carrier)

본 binding (version_handshake_3way_binding, v1.5 CFP-820 carrier — ADR-063 Amendment 5 §결정 15 정합) 는 CFP-1111 walker paradigm 으로 carry.

- **metric**: walker step 의 version bump trigger 시 3-way (publisher `plugin.json` ↔ registry `marketplace.json` ↔ consumer `project.yaml codeforge.version_pin`) byte-identical invariant 정확 enforce + 3-way mismatch 0 silent pass / N walk + sanity guard 6-tuple 재현
- **who**: walker schema field `version_consistency_check: {publisher, registry, consumer}` + `gate_failure_mode: warning_first / blocking_on_pr` enum
- **how**: walker integration test 안 3-way mismatch detection 검증 + warning-first → blocking fallback orthogonal verify

**single promote pattern carry**: 본 §4.8 의 `version_handshake.status: placeholder_reserve → active` 단독 promotion 선례 (§4.14 답습) = walker schema ADR (Wave 1 Story-3) 안 structural precedent 재사용. β2 audit Anchor 9 LOSSLESS 판정.

### 4.9 Wave 3 Story-7 coverage fan-out D1/D2/D3 binding (v1.6 — CFP-821 §4.3 (h) trigger 신설 발동, ADR-027 Amendment 5 §결정 9 + ADR-076 §결정 2 표 PR template row carrier)

본 §4.5 (per-plugin) / §4.6 (per-family) / §4.7 (overlay) / §4.8 (version 3-way) binding 위에 **coverage fan-out D1/D2/D3 binding layer** 1단을 추가한다. ADR-076 §결정 2 9 영역 enumeration 표 중 3 영역 (Issue templates / PR template / Branch protection) 의 reconcile responsibility fan-out 영역 — D1 Issue/PR template fan-out + D2 branch protection setup helper (FORM (b)) + D3 script boundary taxonomy. D1 reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` (marker-aware 2-way / wholesale_mirror_with_user_visible_loss_report) SSOT 재사용 (변경 0, `.github/` 영역 area handler path 매핑만 신설). D2 = read-only manifest 합성 + dry-run preview (API write 0 — FORM (b) 핵심). D3 = declarative taxonomy doc (mechanical lint = §3.3 OOS 별도 follow-up Issue).

```yaml
coverage_fan_out_implementation_binding:   # v1.6 신설, CFP-821 §4.3 (h) 발동
  carrier_story: CFP-821  # Wave 3 Story-7 (Epic CFP-699 D1+D2+D3 — coverage fan-out)
  carrier_adr: "ADR-027 Amendment 5 §결정 9"   # 설계 lane strict-verify 정정: Story §1-§6 'Amendment 4' = frontmatter 미검증 (CFP-820=amendment:4 / §결정 8 점유) → Amendment 5 §결정 9 (Codex TP#2 verify-before-trust 8-mirror 교훈)
  carrier_adr_table_row: "ADR-076 §결정 2 표 PR template row append (Amendment 아닌 표 1행 additive — Issue templates row 동형 `template export — consumer overlay 시점 byte-identical mirror`)"
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = templates/.github/* + setup-branch-protection.sh + docs/script-boundary.md 실 구현
  d1_issue_pr_template_fan_out:
    issue_forms: "templates/.github/ISSUE_TEMPLATE/{audit,bug,story,discussion,codeforge-improvement}.yml (5 forms) + config.yml (Issue selector controller). audit + bug = 기존 .github/ 에서 SSOT 승격. prior art = microsoft/TypeScript 5 forms + config.yml 패턴"
    pr_template: "templates/.github/PULL_REQUEST_TEMPLATE.md = 현 .github/PULL_REQUEST_TEMPLATE.md byte-identical mirror (consumer-distributable SSOT, ADR-005 self-app)"
    d4_marker_form_level_wrap: "Issue Form yaml = form 전체 `# BEGIN/END wrapper-managed` (whole-line anchored, ADR-027 §결정 7.D.3) — body[] sub-block partial marker 금지 (flat only §결정 7.D.1, yaml structure 파편화 회피). PR template .md = `<!-- BEGIN/END wrapper-managed -->`. marker 안 = wrapper SSOT desired state / 밖 = consumer customization preserve"
    reconcile_reuse: "§4.7 overlay_reconcile_implementation_binding marker-aware 2-way / wholesale_mirror_with_user_visible_loss_report SSOT 재사용 — `.github/` 영역 area handler 추가 (algorithm 재구현 0, path 매핑만 신규). consumer marker 부재 시 first-reconcile = wholesale mirror + loss report (silent overwrite 0, EPIC-AC-4)"
  d2_branch_protection_setup_helper:
    form: "FORM (b) — manifest 합성 + dry-run preview only (사용자 confirm 2026-05-17 KST)"
    script: "templates/scripts/setup-branch-protection.sh (mixed-zone distributed — D3 category 3, consumer operator 대상)"
    responsibilities: "(1) manifest 합성 (templates/branch-protection-manifest.yaml wrapper SSOT + consumer overlay .claude/_overlay/branch-protection-manifest.yaml extends, core 4 삭제 불허 invariant 검증) (2) dry-run preview (gh api GET repos/{owner}/{repo}/branches/main/protection/required_status_checks read + manifest 비교 → drift summary stdout)"
    api_write: 0   # 실 gh api PUT = consumer admin operator manual step (Administration:write = consumer org admin 영역, codeforge 권한 영역 외). ADR-024 Amendment 2 §결정 C 운영 규칙 mechanical helper (step 1 manifest+dry-run 자동화, step 2 PUT = operator)
    cli_contract: "--dry-run (default — drift preview) / --manifest-out <path> (합성 manifest 출력). exit 0 (no drift) / 2 (drift detected — informational, NOT CI fail FORM (b)) / 1 (error: manifest invalid / core 4 누락 / gh auth 부재). sync-required-workflows.sh / sync-rulesets.sh 동형 패턴 차용"
    adr_066_unchanged: "GitHub API write 자체 0 → fine-grained PAT Administration:write 불요. ADR-066 §결정 2 scope 5종 무변경. Amendment 4 신설 회피 = ADR-064 minimal-change + least-privilege ratchet-safe (Codex TP#4 F-P1-A 해소 = scope-down OOS)"
  d3_script_boundary_taxonomy:
    doc: "docs/script-boundary.md (declarative taxonomy, Phase 2 carrier). prior art = Helm template/values + Ansible roles/playbooks 동형"
    categories:
      - "(1) Wrapper SSOT — ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/*.sh — upgrade 시 wholesale mirror (consumer touch 0)"
      - "(2) Consumer overlay — consumer repo scripts/*.sh (자기 작성) — upgrade 시 wrapper 무관 (consumer 자기 책임)"
      - "(3) Mixed-zone (distributed templates) — wrapper templates/scripts/*.sh → consumer cp scripts/*.sh (CFP-125 bootstrap-consumer.sh 패턴) — bootstrap 시 cp -n no-clobber, upgrade 시 reconcile (D4 marker 안=wrapper SSOT mirror / 밖=consumer customize preserve)"
    category_disjoint_invariant: "3 category 상호 disjoint — 한 path 가 2 category 소속 = TC-D3-1 FAIL. ADR-039 subagent vs inline context 영역 정합 (declarative SSOT only)"
    adr_cross_ref: "ADR-039 (subagent context 영역) + ADR-061 (Python heredoc 외부 분리 + bash top-level local 금지). codeforge-improvement (k) bash top-level local lint = 별도 follow-up Issue (§3.3 — ADR-064 minimal-change, Story scope creep 회피)"
  read_only_scope:
    write_surface: 0   # D1 = template export (Phase 2) / D2 = manifest+dry-run only (API write 0) / D3 = declarative doc. Phase 1 = pure design-SSOT (script/template/doc 실 file 0건 — §3.6 over-correction 선제 차단)
    pat_scope: "ADR-066 §결정 2 5-scope set 무변경 — D2 dry-run = gh auth GET (read) only, Administration:write grant 0 (FORM (b)). Amendment 4 신설 회피 (추가 PAT grant 0 invariant, least-privilege)"
  phase_split:
    phase_1: "pure design-SSOT — ADR-027 Amendment 5 §결정 9 + ADR-076 §결정 2 표 PR template row + reconcile-protocol-v1 v1.6 §4.3 (h) + MANIFEST.yaml row + change-plan + Story §3.1/§7/§11 미러링 (CFP-743/744/745/820 선례 정합 — script/template/yaml 실 file 0건)"
    phase_2: "구현 lane 별 PR — templates/.github/ISSUE_TEMPLATE/*.yml 5종 + config.yml + templates/.github/PULL_REQUEST_TEMPLATE.md + .github/ byte-identical self-app + templates/scripts/setup-branch-protection.sh + docs/script-boundary.md + consumer-guide §N operator manual + evidence-checks-registry entry (선택)"
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.6 = 강화 only (D1/D2/D3 coverage fan-out 확장), weakening 0
    user_decision_branches_0: unchanged   # D2 dry-run/manifest-out = 정보 제공만, 실 등록 결정 = consumer governance gate (operator manual, internal-decision-branch 아님)
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 — coverage fan-out = self-app enumeration 확장, 무변경)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (ADR-027 §결정 7.C — D1 first-reconcile 재사용)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden
    adr_053_d2_verbatim_quote: unchanged               # L150-151 weakening 차단
```

Phase 1 (CFP-821) merge 시 본 §4.9 binding block 활성 (schema declare — D1/D2/D3 coverage fan-out 영역 enumeration). Phase 2 (별 PR, 구현 lane) merge 시 `templates/.github/ISSUE_TEMPLATE/*.yml` 5종 + `config.yml` + `templates/.github/PULL_REQUEST_TEMPLATE.md` + `.github/` byte-identical self-app + `templates/scripts/setup-branch-protection.sh` (FORM (b) — manifest+dry-run only) + `docs/script-boundary.md` 3 category declarative taxonomy + `docs/consumer-guide.md` §N D2 operator manual 절차 + reconcile-overlay.sh `.github/` area handler 실 연계 + `docs/evidence-checks-registry.yaml` `branch-protection-sync` entry (선택, warning-tier).

### 4.10 Wave 4 sub-Epic #1 `multi-version channel pin` (v1.7 declare layer Story-1 / v1.8 runtime active Story-2 — CFP-906 §4.3 (i) trigger 신설 발동, ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17 carrier)

> **v1.8 (CFP-932 Wave 4 sub-Epic #1 Story-2 runtime activation)**: `status: schema_declared_phase1` → `runtime_active` 전환 (D1 `codeforge-upgrade.sh --channel` + D2 `atomic-upgrade-7-plugins.sh` per-family channel bump + D3 `infer-channel-from-version.sh` + D5 `channel-drift-detection` workflow/script 실 carrier). `registry_channel_matrix.story_1_scope_declare_only` A2 정정 (channels[] populate carrier = Story-4, Story-2 = read-only drift source — Issue #932 OOS 정합). kind:registry MINOR bump (sibling sync 면제 ADR-010 §결정 2, plugin.json bump 0 = `marketplace_sync_declared: false`).

본 §4.5 (per-plugin) / §4.6 (per-family) / §4.7 (overlay) / §4.8 (version 3-way) / §4.9 (coverage fan-out D1/D2/D3) binding 위에 **`multi-version channel pin layer`** 1단을 추가한다. consumer `.claude/_overlay/project.yaml codeforge.channel` field 가 family 7 plugin 동시 channel resolve trigger. 3-tier enum (stable/beta/canary) closed-enum invariant + `family_7_plugin_atomic × channel pin invariant` (per-plugin channel override 거부) + 3-way channel invariant (publisher↔registry↔`consumer pin` byte-identical) 3 invariant 동시 declare. Story-1 = declare layer SSOT only (runtime UpgradeAgent multi-channel dispatch = Wave 4 sub-Epic #1 Story-2 carrier / ProductionEvidence canary tier activation = Story-3 carrier / promotion criteria + canary coord = Story-4 carrier / downgrade invariant = Story-5 carrier).

```yaml
multi_version_channel_pin_binding:   # v1.7 신설 (CFP-906 §4.3 (i) 발동, Wave 4 sub-Epic #1 Story-1) / v1.8 runtime active (CFP-932 Story-2), Epic CFP-882
  carrier_story: "CFP-906 (declare layer Story-1) + CFP-932 (runtime active Story-2)"
  carrier_adr: "ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17"
  status: runtime_active   # v1.8 (CFP-932 Story-2) — schema_declared_phase1 → runtime_active 전환. D1 codeforge-upgrade.sh --channel + D2 atomic-upgrade-7-plugins.sh per-family channel bump + D3 infer-channel-from-version.sh + D5 channel-drift-detection workflow/script 실 carrier. schema shape 무변경 (§4.8 version_handshake placeholder_reserve→active 선례 답습)
  consumer_channel_field:
    location: ".claude/_overlay/project.yaml codeforge.channel"
    enum: ["stable", "beta", "canary"]   # 3-tier closed-enum strict (undeclared 값 = validator FAIL Wave 4 Story-2 runtime carrier)
    default: "stable"                    # 미선언 consumer overlay = stable 자연 fallback (backward-compat invariant, onboarding 마찰 0)
    backward_compat: "field 미선언 = stable 자연 fallback (warning 0, lint skip 0). 기존 consumer overlay 영향 0 (additive only — project-config-schema schema rule §1.1 선택 필드 추가)."
    write_boundary: "consumer-authored (project-config-schema §4b verbatim — '모든 에이전트는 .claude/_overlay/project.yaml write 금지'). codeforge agent write 0 invariant 절대 보존."
    tier_semantic:
      stable: "current active channel (기존 consumer 기본값). LOW risk class. developer self-service OK."
      beta: "opt-in incremental track. MEDIUM risk class. developer + reviewer awareness 충분."
      canary: "preview + production-impact tier. HIGH risk class (production cutover). admin tier 권장 (consumer-side 책임). canary tier 선언 시 Wave 4 sub-Epic #1 Story-3 ProductionEvidenceDeputy spawn trigger 영역 (ADR-72 §결정 1 정합)."
  family_atomic_channel_invariant:
    semantic: "`family_7_plugin_atomic × channel pin` (ADR-016 §결정 1 family scope 7 plugin = wrapper + 6 lane plugin SSOT + Amendment 3 channel 차원 확장)"
    rule: "consumer codeforge.channel: <C> 선언 시 family 7 plugin (wrapper + codeforge-{requirements, design, develop, test, review, pmo}) 모두 동일 channel <C> 으로 resolve"
    per_plugin_override_forbidden: true   # mixed channel 운영 = ADR-016 §결정 1 family scope invariant 위배. Wave 4 sub-Epic #1 Story-2 runtime UpgradeAgent 가 mixed channel detection + abort 의무 (declare layer = mandate semantic, runtime detection = Story-2 carrier).
    rationale: "ADR-064 §결정 1.3 CFP scope unitary + ADR-016 §결정 1 family atomic unit — channel mix 시 6 lane plugin 간 contract version skew 발생, inter-plugin contract MANIFEST invariant 위배 risk"
  registry_channel_matrix:
    location: "mclayer/marketplace/.claude-plugin/marketplace.json plugins[name=codeforge].channels[]"
    schema: "[{tier: <enum stable|beta|canary>, version: <semver string>}, ...]"
    mirrored_field_split:   # ADR-063 Amendment 6 §결정 17 mirrored field × channel matrix
      name: "channel 별 분리 안 함 (불변 — identity 영역)"
      version: "channel 별 분리 (per-channel snapshot — 본 Amendment 6 §결정 17 핵심)"
      description: "channel 별 분리 안 함 (불변 — ADR-063 §결정 11 description verbatim PR-time lint 정합)"
      author: "channel 별 분리 안 함 (불변 — identity 영역)"
    carrier_adr: "ADR-063 Amendment 6 §결정 17 (CFP-906) — marketplace.json plugins[name=codeforge].channels[] array 신설 + per-channel version snapshot"
    story_1_scope_declare_only: "Story-1 (CFP-906) = declare layer SSOT only. 실 marketplace.json channels[] field 추가 (populate) = Wave 4 sub-Epic #1 Story-4 carrier 영역. Story-2 (CFP-932) = channels[] read-only drift source (D5 (c) leg membership lookup) only — write/populate 0 (Issue #932 OOS 정합). marketplace_sync_declared: false (Story-1/Story-2 모두 ADR/contract MINOR bump only, plugin.json bump 0 — Story-1 declare-layer scope / Story-2 runtime activation kind:registry MINOR scope). [v1.8 A2 정정 — CFP-932: 종전 'Story-2 carrier 영역' 표기가 Issue #932 OOS('populate = Story-4')와 formal contract-pin 상충 → live contract forward-effective 정정. CFP-906 §11.4 line 454 historical record 는 immutable 보존 (PMO retro 영역, 두 데이터 layer 분리 — DataMigrationArch §11.7 load-bearing dissent 채택)] [v1.11 A3 정정 — CFP-991: Story-4 = canary promotion criteria enforcement layer carrier 가 marketplace.json channels[] field 의 forward-effective realize point (v1.8 A2 = predict / v1.11 A3 = enact). Story-1 declare-layer SSOT + Story-2 read-only drift source 변경 0 (immutable preserve). forward-effective only — CFP-906 §11.4 / CFP-932 A2 historical record 보존 (두 layer 분리 invariant 유지). story_4_scope_write_carrier entry below = A3 정정 의 explicit semantic SSOT.]"
    story_4_scope_write_carrier:
      semantic: "Story-4 (CFP-991) = Wave 4 sub-Epic #1 canary promotion criteria enforcement layer carrier. marketplace.json channels[] field 의 forward-effective realize point — Story-1 declare-only / Story-2 read-only drift source → Story-4 enforcement (canary→beta promotion gate evaluation). Story-4 가 §4.14 `canary_compatibility_check_binding` block 활성 + 4-tuple measurement source SSOT + family_7_atomic_canary_pin 3-way match invariant + enum closed-set 보장."
      forward_effective_from_version: "v1.11"
      relation_to_v1_8_a2: "v1.8 A2 정정 (Story-2 OOS 'populate = Story-4') 의 realize point. v1.8 = predict (Story-2 commit 시점 forward predicate), v1.11 = enact (Story-4 commit 시점 actualize). 두 statement 일관성 invariant (DataMigrationArch §11.7 load-bearing dissent verbatim 채택, CFP-932 frozen-SHA verify 후 채택 패턴 답습)."
      historical_record_immutability: "CFP-906 §11.4 line 454 historical record 본문 변조 0 invariant. forward-effective 정정 = entry append only (Layer-2 live contract 영역, Layer-1 historical record 영역 미touch)."
  three_way_channel_invariant:
    semantic: "ADR-063 Amendment 5 §결정 15 (publisher↔registry↔consumer 3-way version atomic invariant) × channel 차원 확장"
    rule: "consumer codeforge.channel: <C> 선언 시 publisher <C>-branch version ↔ registry marketplace.json channels[tier=<C>].version ↔ consumer .codeforge.version_pin.version 3-way byte-identical (semver normalize 안 함: 5.83.0 ≠ 5.83 ≠ v5.83.0 모두 mismatch — publisher SSOT canonical, consumer verbatim mirror)"
    orthogonality_invariant: "`pin` 가용성 (channel 미선언 = warning-first stable fallback) ≠ version 정합성 (channel 선언 후 3-way mismatch = blocking-on-pr) — conflate 금지 (§4.8 version_handshake orthogonality_invariant 답습)"
    runtime_carrier: "Wave 4 sub-Epic #1 Story-2 (CFP-932) ACTIVE — runtime UpgradeAgent multi-channel dispatch + scripts/check-3way-version-parity.sh 의 channel 차원 확장 (OQ-5 scope 포함 확정, ADR-076 §결정 9.2 verbatim + 본 contract-pin 정합)"
  partial_activation_invariant:   # ADR-064 §결정 1.3 CFP scope unitary
    activated_in_v1_7: ["multi_version_channel_pin"]   # Wave 4 sub-Epic #1 carrier 단독 activation
    placeholder_reserve_continued: ["codemod_apply", "uninstall_cleanup"]   # Wave 4 sub-Epic #2 / #3 carrier 영역 — 무변경
    rationale: "ADR-064 §결정 1.3 CFP scope unitary — 한 CFP 안 '경량 → full' 단계 채택 금지. Wave 4 sub-Epic #1 (multi_version_channel_pin) / #2 (codemod_apply) / #3 (uninstall_cleanup) sequential ordering (ADR-067 §결정 4 정합)."
    state_field_decision: "reconcile_strategy.status: 'placeholder_reserve' field-level 유지 (per-entry status marker 도입 회피 = minimal-change). partial activation = §4.8 version_handshake.status 'placeholder_reserve → active' 단독 promotion 선례 답습 (partial-active state 도입 회피 = wholesale field shape 변경 회피)."
  channel_drift_detection:   # OpRiskArch §7.4 §1 — v1.8 (CFP-932 Story-2) runtime ACTIVE
    required: true
    runtime_carrier: "Wave 4 sub-Epic #1 Story-2 (CFP-932) ACTIVE — channel-drift-detection.yml workflow + check-channel-drift.sh script 실 carrier (ADR-063 Amendment 3 §결정 13 marketplace-drift-detection.yml precedent byte-pattern 답습 — 24h cron + workflow_dispatch + Issue auto-create + signature dedup + E-4 3-branch)"
    detection_target: "3-tuple drift — (a) consumer .claude/_overlay/project.yaml codeforge.channel field declared value ↔ (b) 실 install plugin .claude-plugin/plugin.json .version ↔ (c) registry marketplace.json plugins[name=codeforge].channels[*].versions[] membership"
    failure_mode_default: "warning-first (ADR-060 §결정 5 default + §4.8 version_handshake fallback orthogonality 답습). (c) leg 미populate (Story-4 전) = warning-first exit 0 graceful (blocking 0, transitional valid)"
    story_1_scope: "[v1.8 정정 — CFP-932] declare placeholder (Story-1) → runtime active (Story-2). evidence-checks-registry.yaml `channel-drift-detection` entry append = CFP-932 Story-2 완료 (warning tier, current_tier: warning)."
  canary_tier_authority:
    semantic: "advisory only (semantic mandate, mechanical enforce = consumer CODEOWNERS path 영역)"
    recommendation: "admin_review_recommended — canary tier 선언 PR 의 consumer CODEOWNERS auto-review path 권장 (consumer-side 책임, codeforge wrapper 영역 외)"
    rationale: "SecurityArch §2 T-2.1 — canary tier production-impact decision authority asymmetry. silent canary uptake (developer self-service via PR edit) risk 차단 = consumer governance gate"
  channel_demotion_warning:
    required: true
    semantic: "canary → beta → stable demotion 시 feature regression warning 의무 (Wave 4 sub-Epic #1 Story-5 downgrade invariant carrier 영역)"
    runtime_carrier: "Wave 4 sub-Epic #1 Story-2 (dry-run preview warning) + Story-5 (downgrade invariant declarative carrier)"
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.7 = 강화 only (`multi-version channel pin coverage` 확장), weakening 0
    user_decision_branches_0: unchanged   # channel field 선언 = consumer 1회 결정, family 7 plugin 자동 resolve (internal-decision-branch 0)
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 — `channel pin` = runtime catch-up layer 확장만, 의미 invariant 자체는 ADR-016 Amendment 3 가 channel 차원 declare)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (ADR-027 §결정 7.C — channel field 무관)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden
    adr_053_d2_verbatim_quote: unchanged               # L150-151 weakening 차단
```

Story-1 (CFP-906, v1.7) merge 시 본 §4.10 binding block declare 활성 (schema declare — 3-tier channel taxonomy + family atomic channel invariant + 3-way channel invariant + partial activation invariant + canary tier authority advisory + channel drift detection placeholder + channel demotion warning). **Story-2 (CFP-932, v1.8) merge 시 runtime active 전환**: D1 `codeforge-upgrade.sh --channel` runtime resolve + D2 `atomic-upgrade-7-plugins.sh` per-family channel bump (mixed channel detection → abort-before-touch) + D3 `infer-channel-from-version.sh` migration tool (write-0 invariant) + D4 consumer-guide §2g.3 + D5 `channel-drift-detection.yml` workflow self-app + `check-channel-drift.sh` 3-tuple drift + `docs/evidence-checks-registry.yaml` `channel-drift-detection` entry (warning-tier) + `scripts/check-3way-version-parity.sh` 의 channel 차원 확장 (OQ-5 scope, ADR-076 §결정 9.2 정합). 후속 Story sequential carrier: marketplace.json channels[] 실 populate (Story-4) + ProductionEvidenceDeputy canary tier activation (Story-3, ADR-72 §결정 1) + promotion criteria mechanical lint (Story-4) + downgrade invariant declarative carrier (Story-5).

### 4.11 Wave 4 sub-Epic CFP-858 S1 dependency bundle integrity binding (v1.7 — CFP-898 §4.3 (i) trigger 신설 발동, ADR-076 Amendment 2 §결정 2 11번째 row + §결정 6 fail-closed clause carrier)

본 §4.5 (per-plugin) / §4.6 (per-family) / §4.7 (overlay) / §4.8 (version 3-way) / §4.9 (coverage fan-out) binding 위에 **dependency bundle integrity binding layer** 1단을 추가한다. ADR-076 §결정 2 enumeration 표 11번째 row (`scripts/` workflow_dependency_closure, `bundled_with_referencing_workflow`) 의 reconcile semantic carrier — MARKER_NONE wholesale_mirror branch 진입 전 workflow yml 의 의존 `scripts/check-*.sh` + `templates/scripts/*.py` closure resolve + missing 시 fail-closed. reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` SSOT 재사용 (MARKER_NONE branch, wholesale_mirror_with_user_visible_loss_report) — closure resolver layer 1 추가 (algorithm 재구현 0). evidence: mctrader-data#81 14 failing checks (Epic CFP-858 §1 motivation verbatim).

```yaml
dependency_bundle_integrity_binding:   # v1.7 신설, CFP-898 §4.3 (i) 발동, ADR-076 Amendment 2 carrier
  carrier_story: CFP-898  # Wave 4 sub-Epic CFP-858 S1 base layer (S2 CFP-899 / S3 CFP-900 prerequisite)
  carrier_adr: "ADR-076 Amendment 2 §결정 2 11번째 row append + §결정 6 fail-closed clause sub-section"
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = templates/scripts/mirror-dependency-closure.py + scripts/reconcile-overlay.sh hook 실 구현 (Develop lane)
  scope: "MARKER_NONE wholesale_mirror branch — wrapper-side workflow yml 의 의존 `scripts/check-*.sh` + `templates/scripts/*.py` closure atomic bundle 적용 영역"
  closure_resolve_algorithm: regex_primary
  closure_resolve_algorithm_rationale: "AM-1 derived default — stdlib only (pyyaml 의존 0). false-negative 회피 = regex pattern 광범위 + multi-line bash heredoc cover (TC-DEP-6/7). consumer 측 pyyaml 가용성 미보장 영역 cover. trade-off: regex 가 pyyaml AST 대비 multi-line edge case 부정확 — 但 codeforge family workflow 패턴 standardized (TC-DEP-15 false-positive 차단 검증)."
  transitive_depth_limit: 1
  transitive_depth_limit_rationale: "AM-2 derived default — wrapper-side script.sh 내부 sub-script 호출은 wrapper SSOT 가 보장 (consumer 측에서 transitive 깊이 2+ 검증 시 false-positive 폭증). codeforge `scripts/check-*.sh` 60+ 의 cross-reference 망 — depth 2 시 transitive graph cardinality O(N^2) 폭증."
  dependency_scope: shell_script_only_v1
  dependency_scope_definition:
    include_patterns:
      - "scripts/check-[a-z0-9-]+\\.sh"
      - "templates/scripts/[a-z0-9-]+\\.py"
    exclude_patterns:
      - "(runtime 의존 — Python venv / Node_modules / OS package — EC-4 out-of-scope)"
      - "(dynamic script fetch — `bash -c \"$(curl ...)\"` — EC-5 out-of-scope, codeforge family invariant)"
    rationale: "AM-3 (a) shell script only — Phase 0 Analyst AC-1 verbatim + Story §5.2 derived default. .py 파일 (templates/scripts/*.py) 포함 — workflow yml run: block 안 `python3 templates/scripts/*.py` 패턴 직접 의존. version v2.0 (Wave 4 sub-Epic 영역) ratchet 가능 — scope 확장은 별 Story carrier."
  self_app_exemption:
    closure_resolver_script: "templates/scripts/mirror-dependency-closure.py"
    reason: "ADR-005 dual-channel template ↔ live byte-identical mirror rule 면제 영역 — consumer 측 실행 only (wrapper-side `scripts/` 미존재, consumer-side `.claude/_overlay/` 또는 `scripts/` 으로만 deploy). Hint-3 정합. AM-4 derived default (self-loop 0 invariant — 본 .py file 이 workflow yml 안 의존되지 않으면 self-ref edge case 미발생)."
    adr_005_exemption_declared: true
    self_loop_invariant: "본 file 자체가 workflow yml 안 의존되지 않음 (Phase 2 TC-DEP-14 assertion on grep result)"
  fail_closed_behavior:
    on_dependency_missing: exit_1_with_error_log
    error_log_format: "[ERR] Dependency missing: <relative_script_path> (referenced by: <workflow_yml_relative_path>)"
    upgrade_event_log_result: FAILED   # S3 (CFP-900) prerequisite — SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE 신설은 S3 scope
    partial_mirror_commit: forbidden    # atomic bundle invariant — 의존 closure 불완전 → 본 file mirror skip
    silent_skip_invariant: 0           # silent_skip_0_invariant 강화 — ADR-076 §결정 6 Amendment 1 ratchet 강화
  dry_run_behavior:
    on_dependency_missing: preview_only_with_return_0
    preview_format: "[dry-run] missing deps: <list>"
    return_code: 0
    rationale: "ADR-076 §결정 3 dry-run semantic — 정보 제공만, 실 변경 0. abort 영역 외. AM-4 / EC-6 derived default."
  hook_integration:
    file: "scripts/reconcile-overlay.sh"
    invocation_point: "line 437 직전 (MARKER_NONE branch first-line, cp 직전)"
    pattern: "if [[ -n \"${MIRROR_DEP_PY:-}\" ]] && [[ -x \"${MIRROR_DEP_PY}\" || -f \"${MIRROR_DEP_PY}\" ]]; then ... fi"
    exit_code_contract:
      "0": "closure OK + proceed to cp"
      "1": "dependency missing → return 2 (ABORT) from reconcile-overlay.sh — MARKER_LINT return 2 pattern 답습"
      "2": "lint warning (degraded — Phase 2 reserve, e.g., malformed workflow yml) → exit 0 from caller + warning log"
    env_passthrough:
      MIRROR_DEP_PY: "templates/scripts/mirror-dependency-closure.py absolute path"
      WRAPPER_ROOT: "reconcile-overlay.sh detected wrapper plugin root"
    caller_pattern_evidence: "현재 caller 가 `return 1` / `return 0` / `return 2` 분기 (FIX_NEEDED / OK / ABORT, MARKER_LINT 정합) — 자연 통합 가능 [verified: scripts/reconcile-overlay.sh line 422-449]"
    development_lane_phase: "Phase 2 PR 영역 (본 Phase 1 PR scope 외 — Develop lane DeveloperAgent 영역)"
  out_of_scope:
    - runtime_dependencies   # EC-4 — Python venv / Node_modules / system package 등 file 존재성 외 영역
    - dynamic_script_fetch   # EC-5 — `bash -c \"$(curl ...)\"` 등 (codeforge family invariant — internal workflow 0건)
    - monorepo_workflow_dirs # EC-2 — `apps/*/.github/workflows/` 등 (Wave 4 sub-Epic 영역)
    - marker_valid_branch    # EC-3 — MARKER_VALID branch 진입 시 closure resolver 미invoke (caller responsibility, reconcile-overlay.sh top-level guard)
  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.7 = 강화 only (closure 검증 추가), weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 SSOT — 본 binding 은 wholesale_mirror 단위 ratchet 강화, family scope 무변경)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (의미 invariant 무변경 + fail-closed clause 추가는 ratchet 강화 방향, ADR-076 §결정 6 Amendment 2 SSOT)
    transaction_completion_criterion: unchanged
    snapshot_reset_disjoint_layer: unchanged
    adr_053_d2_verbatim_quote: unchanged
```

Phase 1 (CFP-898) merge 시 본 §4.11 binding block 활성 (schema declare — dependency bundle integrity 영역 declaration). Phase 2 (별 PR, Develop lane) merge 시 `templates/scripts/mirror-dependency-closure.py` 신설 (Python stdlib only, regex_primary AM-1 algorithm, 60+ workflow yml × < 50ms per-file budget) + `scripts/reconcile-overlay.sh` line 437 직전 hook insertion (MARKER_LINT return 2 abort pattern 답습) + `tests/test_mirror_dependency_closure.py` 15 TC unit tests + `tests/integration/test_reconcile_overlay_dep_closure.bats` 통합 테스트 (TC-DEP-5/9 self-app) + `docs/evidence-checks-registry.yaml` `dependency-closure-self-test` entry (선택, warning-tier) + `CHANGELOG.md` row append.

### 4.12 Wave 4 sub-Epic CFP-858 S2 consumer-applicability filter binding (v1.9 — CFP-899 §4.3 (j) trigger 신설 발동, ADR-083 신규 + ADR-027 Amendment 6 §결정 10 carrier)

본 §4.11 (CFP-898 vertical closure resolver) 위에 **horizontal consumer-applicability filter layer** 1단을 추가한다. ADR-083 신규 §결정 1-6 + ADR-027 Amendment 6 §결정 10 sibling carrier — wrapper-only workflow yml 가 consumer repo 로 무차별 유입 silent harm super-class 차단 (Epic CFP-858 결함 2, mctrader-data#81 14 failing checks evidence). reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` (MARKER_NONE wholesale_mirror branch) SSOT 재사용 (filter resolver layer 1 추가, algorithm 재구현 0). CFP-898 §4.11 vertical closure resolver 와 sequential composition (filter 먼저 → closure 다음).

```yaml
consumer_applicability_filter_binding:   # v1.9 신설, CFP-899 §4.3 (j) 발동, ADR-083 §결정 1-6 + ADR-027 Amendment 6 §결정 10 carrier
  carrier_story: CFP-899  # Wave 4 sub-Epic CFP-858 S2 base layer (S3 CFP-900 prerequisite)
  carrier_adrs:
    - "ADR-083 §결정 1-6 (wrapper-side filter mechanism SSOT)"
    - "ADR-027 Amendment 6 §결정 10 (consumer-side signal SSOT — boundary disjoint)"
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = templates/scripts/detect-repo-kind.py + templates/consumer_applicable_workflows.txt populate + scripts/reconcile-overlay.sh hook insertion + test suite (Develop lane)
  scope: "MARKER_NONE wholesale_mirror branch — wrapper `.github/workflows/*.yml` consumer copy 영역 한정 (CFP-898 §4.11 dependency bundle integrity binding 의 horizontal counterpart, sequential composition layer 추가)"

  truth_table_schema:   # ADR-083 §결정 1 + ADR-027 Amendment 6 §결정 10.A verbatim cross-ref
    type: "4-way enum closed-set (open-set 확장은 별 ADR carrier — 본 contract scope 외)"
    enum_values:
      plugin:
        signal_a_plugin_json: present   # .claude-plugin/plugin.json 존재
        signal_b_overlay_yaml: absent    # .claude/_overlay/project.yaml 부재
        semantic: "wrapper-only repo (codeforge family plugin 자체) — full workflow set 적용 (filter skip)"
        copy_behavior: full_workflow_set
      consumer:
        signal_a_plugin_json: absent
        signal_b_overlay_yaml: present
        semantic: "consumer repo (codeforge plugin 사용자) — positive whitelist filter 적용"
        copy_behavior: whitelist_filtered
      mixed:
        signal_a_plugin_json: present
        signal_b_overlay_yaml: present
        semantic: "dogfood repo (codeforge wrapper repo 자체 — plugin SSOT + 자기 자신의 consumer overlay self-app) — plugin 분류 우선 (filter skip)"
        copy_behavior: full_workflow_set   # mixed = plugin 우선 적용 invariant (ADR-083 §결정 3 sibling carrier)
      unknown:
        signal_a_plugin_json: absent
        signal_b_overlay_yaml: absent
        semantic: "signal 부재 (consumer bootstrap 미완료 또는 비-codeforge repo) — fail-closed"
        copy_behavior: abort_no_copy   # fail-closed unknown invariant (ADR-083 §결정 4 + ADR-027 Amendment 6 §결정 10.E sibling carrier)

  repo_kind_detection_signals:   # ADR-027 Amendment 6 §결정 10.B/10.C verbatim cross-ref
    filesystem_only_invariant: true   # network call 0 / gh api 0 / marketplace.json membership check 0
    rationale:
      - "Offline-first invariant — ADR-066 PAT scope 최소화 정합 (cross-repo PAT 의존 영역 차단)"
      - "Trust boundary 명확 — filesystem-only = consumer 권한 area only, cross-repo trust surface 0"
      - "Primary signal 단일 read 비용 < 1ms — `Test-Path` / `[[ -f ... ]]` O(1) syscall"
    signal_a:
      path: ".claude-plugin/plugin.json"
      schema_ssot: "Claude Code plugin spec (external — anthropic 제공)"
      detection_mechanism: "file existence check only ([[ -f ... ]]) — content parsing 미요구"
      semantic: "본 repo = Claude Code plugin SSOT"
    signal_b:
      path: ".claude/_overlay/project.yaml"
      schema_ssot: "ADR-027 §결정 1 / Amendment 4 §결정 8 (codeforge.version_pin schema)"
      detection_mechanism: "file existence check only ([[ -f ... ]]) — content parsing 미요구"
      semantic: "본 repo = codeforge consumer (consumer overlay bootstrap 완료)"
    existence_check_only_invariant: "content parsing (예: plugin.json name field / project.yaml codeforge.version_pin) = 본 binding scope 외 — ADR-027 §결정 1 (check-bootstrap.{sh,ps1} Phase 2) + Amendment 4 §결정 8 별 trigger 영역. Signal detection = file existence 만 (분리 invariant)."

  whitelist_file_format:   # ADR-083 §결정 2 verbatim cross-ref + DataMigrationArch §11 schema
    path: "templates/consumer_applicable_workflows.txt"
    format: plain_text
    line_format: "1-per-line, relative filename only (디렉토리 prefix 0)"
    comment_prefix: "#"   # comment line
    blank_line_behavior: skip   # blank = skip
    encoding: utf-8_lf
    positive_list_invariant: "whitelist 안 = consumer copy / whitelist 밖 = consumer skip. default = skip (fail-closed unknown semantic 동형). 반대 (blacklist) 금지 — 새 workflow 신설 시 blacklist 부재 = consumer silent 유입 silent harm 재발 (Epic CFP-858 결함 2 root cause 재발)."
    self_app_exemption:
      adr_005_dual_channel: exempt   # ADR-005 byte-identical mirror rule 면제 영역 (consumer-distributable SSOT only, wrapper-side `.github/workflows/*.yml` mirror 부재)
      rationale: "AM-3 derived default (CFP-898 §4.11 self_app_exemption 패턴 답습)"

  mixed_repo_handling:   # ADR-083 §결정 3 + §결정 6 + ADR-027 Amendment 6 §결정 10.D verbatim cross-ref
    classification_priority_invariant: "mixed = plugin 우선 적용 (filter skip — full workflow set 적용)"
    wrapper_self_app_exemption: "본 wrapper repo (mclayer/plugin-codeforge) = mixed 분류 (Signal A + Signal B 양 존재) — full 76 .github/workflows/*.yml 모두 적용 보존 (self-app dogfood 변경 0 invariant)"
    self_loop_bug_prevention: "consumer 분류 false-positive 차단 — Signal A (.claude-plugin/plugin.json) 존재 보장으로 mixed 우선 분류 → wrapper dogfood workflow 손실 0"
    verify_phase_2_tc: "TC-CAF-MIXED-1 — 본 wrapper repo 에서 detect-repo-kind.py 실행 → `mixed` 출력 + reconcile-overlay.sh 실행 → 76 .yml 모두 적용 + 0 file skip"

  fail_closed_unknown:   # ADR-083 §결정 4 + ADR-027 Amendment 6 §결정 10.E verbatim cross-ref
    behavior: abort_with_error_log_no_copy
    error_log_format: |
      [ERR] Consumer-applicability filter: repo_kind=unknown (.claude-plugin/plugin.json absent + .claude/_overlay/project.yaml absent)
      [ERR] Reconcile-overlay aborted. Initialize consumer overlay (codeforge bootstrap) or run from a known repo kind.
      [ERR] Exit code 1.
    silent_default_blocked_rationale:
      - "(a) silent default → wrapper-only 무차별 유입 silent harm 재발 (Epic CFP-858 결함 2 root cause)"
      - "(b) 명시적 fail = consumer-side 명시적 bootstrap 의무 (ADR-027 consumer adoption protocol 정합)"
      - "(c) ADR-076 §결정 6 Amendment 1 fail-closed clause 패턴 답습 (CFP-898 closure resolver silent_skip_invariant: 0)"
    exception_zero_invariant: "`--force-unknown-as-consumer` flag 신설 금지 — hotfix-bypass:consumer-applicability-filter-detection label 영역 외 (bypass label = PR-time mechanical enforcement 회피용, runtime fail-closed 회피는 위배 vector). 사용자가 unknown 영역에 reconcile 강제 적용 필요 시 = .claude/_overlay/project.yaml minimal bootstrap (consumer signal 활성) 의무."

  self_app_exemption:   # ADR-083 §결정 5 self_app_exemption verbatim cross-ref + CFP-898 §4.11 pattern 답습
    closure_resolver_script: "templates/scripts/detect-repo-kind.py"
    whitelist_file: "templates/consumer_applicable_workflows.txt"
    reason: "ADR-005 dual-channel template ↔ live byte-identical mirror rule 면제 영역 — consumer 측 실행 only (wrapper-side `scripts/` 미존재, consumer-side `.claude/_overlay/` 또는 `scripts/` 으로만 deploy). CFP-898 §4.11 mirror-dependency-closure.py 동형 패턴."
    adr_005_exemption_declared: true
    self_loop_invariant: "본 detect-repo-kind.py + consumer_applicable_workflows.txt 자체가 workflow yml 안 의존되지 않음 (Phase 2 TC 검증 의무 — TC-CAF-SELFLOOP-1: grep -r 'detect-repo-kind\\|consumer_applicable_workflows' .github/workflows/*.yml = 0 hits)"

  hook_integration:
    file: "scripts/reconcile-overlay.sh"
    invocation_point: "line 437 직전 (CFP-898 §4.11 closure resolver hook 직후, cp 직전 추가 layer — sequential composition order: closure → filter → cp)"
    sequential_composition_order:
      - step_1: "CFP-898 §4.11 closure resolver hook (closure missing 시 fail-closed return 1)"
      - step_2: "CFP-899 §4.12 consumer-applicability filter hook (closure full but consumer-non-applicable 시 skip 또는 fail-closed unknown 시 return 1)"
      - step_3: "cp 실행 (filter PASS 시점)"
    pattern: "if [[ -n \"${FILTER_REPO_KIND_PY:-}\" ]] && [[ -x \"${FILTER_REPO_KIND_PY}\" || -f \"${FILTER_REPO_KIND_PY}\" ]]; then ... fi"
    exit_code_contract:
      "0": "filter OK + proceed to cp"
      "1": "filter abort (unknown repo_kind / detect-repo-kind.py error) → return 1 (ABORT) from reconcile-overlay.sh — CFP-898 MARKER_LINT return 2 와 분리 (filter 는 return 1, closure 는 return 2)"
      "2": "filter warning (degraded — Phase 2 reserve, e.g., malformed whitelist file) → exit 0 from caller + warning log"
    classification_severity_disjoint_invariant: "본 exit_code_contract 의 0/1/2 = **filter decision severity channel** (proceed / abort / degraded) — `detect-repo-kind.py` 의 **classification exit code** (0=plugin / 1=consumer / 2=mixed / 3=unknown, §4.12 truth_table_schema) 와 **disjoint channel**. detect-repo-kind classification exit (`_ec`) 는 `_S2_MAX_EXIT` (severity 집계 변수, §4.13 degradation_propagation 입력) 에 **무조건 전파 금지** — classification exit 의 numeric 값 (특히 consumer=1 / mixed=2) 이 severity channel 의 1=abort / 2=degraded 와 우연히 동일 numeric space 를 공유하므로 conflation 위험 (CFP-986 post-merge defect evidence). 정확한 mapping: classification `plugin`(0) / `consumer`(1) / `mixed`(2) = filter proceed → severity **0** (정상 valid 분류, abort 아님). classification `unknown`(3) = fail-closed abort → severity **1**. detect-repo-kind crash / 알 수 없는 exit (>3) = fail-closed abort → severity **1**. enum 오염 (validated `_ec` 이나 stdout `_repo_kind` 비정상) = fail-closed abort → severity **1**. severity 집계는 오직 filter 의 **결정** (proceed/skip=0, abort=1, degraded=2) 만 입력 — classification 자체는 severity 입력 아님 (ratchet 강화 only, 기존 'exit_code_contract 1=filter abort' semantic explicit enumeration — 의미 invariant 무변경, ADR-064 §self-application 정합)."
    env_passthrough:
      FILTER_REPO_KIND_PY: "templates/scripts/detect-repo-kind.py absolute path"
      CONSUMER_APPLICABLE_WHITELIST: "templates/consumer_applicable_workflows.txt absolute path"
      CONSUMER_ROOT: "reconcile-overlay.sh detected consumer repo root"
    caller_pattern_evidence: "CFP-898 §4.11 hook 동형 패턴 — `return 1` / `return 0` / `return 2` 분기 (FIX_NEEDED / OK / ABORT, MARKER_LINT 정합) 자연 통합 가능 [hypothesis — verify in Phase 2 PR implementation step, CFP-898 hook precedent 의존]"
    development_lane_phase: "Phase 2 PR 영역 (본 Phase 1 PR scope 외 — Develop lane DeveloperAgent 영역)"

  out_of_scope:
    - cross_repo_marketplace_membership_check   # marketplace.json 안 codeforge plugin family 검사 (network call 영역, 본 binding filesystem-only invariant 위배) — 별 ADR carrier 영역
    - open_set_repo_kind_extension   # library / monorepo / archived 등 4-way enum closed-set 확장 — 별 ADR carrier 영역
    - content_parsing_signal_validation   # plugin.json schema 검증 / project.yaml codeforge.version_pin 검증 — ADR-027 §결정 1 + Amendment 4 §결정 8 별 trigger 영역
    - marker_valid_branch                # MARKER_VALID branch 진입 시 filter 미invoke (caller responsibility, reconcile-overlay.sh top-level guard — CFP-898 §4.11 동형 pattern)

  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.9 = 강화 only (consumer-applicability filter layer 추가), weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 SSOT — 본 binding 은 wholesale_mirror branch horizontal gating, family scope 무변경)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (의미 invariant 무변경 + filter layer 추가는 ratchet 강화 방향, ADR-076 §결정 6 Amendment 1 SSOT)
    transaction_completion_criterion: unchanged
    snapshot_reset_disjoint_layer: unchanged
    adr_053_d2_verbatim_quote: unchanged
```

Phase 1 (CFP-899) merge 시 본 §4.12 binding block 활성 (schema declare — consumer-applicability filter 영역 declaration). Phase 2 (별 PR, Develop lane) merge 시 `templates/scripts/detect-repo-kind.py` 신설 (Python stdlib only, ADR-061 외부 .py file 의무, file existence check primary signal + 4-way enum classification + < 10ms latency budget) + `templates/consumer_applicable_workflows.txt` populate (76 wrapper workflows 검수 후 consumer-applicable subset 결정) + `scripts/reconcile-overlay.sh` line 437 직전 hook insertion (CFP-898 §4.11 hook pattern 답습 + sequential composition) + `tests/test_detect_repo_kind.py` 20 TC unit tests (4-way matrix × 4 base + 6 EC + whitelist edge 5 + integration 3 + mixed self-app 1 + self-loop 1) + `tests/integration/test_reconcile_overlay_consumer_filter.bats` 통합 테스트 (TC-CAF-MIXED-1 wrapper self-app verify + TC-CAF-SELFLOOP-1 self-loop 0 invariant) + `docs/evidence-checks-registry.yaml` `consumer-applicability-filter-detection` entry (warning-tier) + `CHANGELOG.md` row append.

### 4.13 Wave 4 sub-Epic CFP-858 S3 result fidelity binding (v1.10 — CFP-900 §4.3 (k) trigger 신설 발동, ADR-076 Amendment 3 §결정 3 sub-clause + ADR-026 Amendment 5 §결정 7 carrier)

본 §4.11 (CFP-898 vertical closure resolver, mirror-전) + §4.12 (CFP-899 horizontal consumer-applicability filter, mirror-전) 위에 **temporal-post result fidelity layer** 1단을 추가한다. ADR-076 Amendment 3 §결정 3 sub-clause (transaction 사후 sanity check 위 result fidelity false SUCCESS 차단 clause) + ADR-026 Amendment 5 §결정 7 (`.github/` fast-pass content sanity 1차 신호 orthogonal warning layer) sibling carrier — upgrade-event 로그 `result: SUCCESS` 거짓 기록이 S1 fail-closed / S2 abort / degraded 결함을 가리는 super-class 차단 (Epic CFP-858 부가 결함, mctrader-data#81 14 failing checks class 재발 차단). reconcile semantic = §4.7 `overlay_reconcile_implementation_binding` (MARKER_NONE wholesale_mirror branch) SSOT 재사용 (result fidelity layer 1 추가 = post-mirror sanity check + result enum 집계 stage, algorithm 재구현 0). CFP-898 §4.11 closure resolver + CFP-899 §4.12 consumer-applicability filter 와 sequential composition (mirror-전 S1/S2 → cp → mirror-후 sanity check + result enum 집계 — layer 분리 invariant, Epic CFP-858 마지막 Story 3-layer composite 완결: vertical / horizontal / temporal-post).

```yaml
result_fidelity_binding:   # v1.10 신설, CFP-900 §4.3 (k) 발동, ADR-076 Amendment 3 §결정 3 sub-clause + ADR-026 Amendment 5 §결정 7 carrier
  carrier_story: CFP-900  # Wave 4 sub-Epic CFP-858 S3 (Epic CFP-858 마지막 Story — honest result reporting layer, mirror-후 temporal-post)
  carrier_adrs:
    - "ADR-076 Amendment 3 §결정 3 sub-clause (transaction 사후 sanity check 위 result fidelity false SUCCESS 차단 clause — semantic declare)"
    - "ADR-026 Amendment 5 §결정 7 (`.github/` fast-pass content sanity 1차 신호 orthogonal warning layer — semantic declare)"
  status: schema_declared_phase1   # Phase 1 = schema binding declare / Phase 2 = result enum 집계 + post-mirror sanity check + 실 rollback runtime (Develop lane, CFP-898 §4.11 schema_declared_phase1 패턴 답습)
  scope: "MARKER_NONE wholesale_mirror branch — cp **후** post-mirror sanity check + upgrade-event log result enum 집계 영역 한정 (CFP-898 §4.11 vertical closure resolver + CFP-899 §4.12 horizontal filter 의 temporal-post counterpart, 3-layer composite 완결)"

  result_enum_schema:   # ADR-076 Amendment 3 §결정 3 sub-clause + DataMigrationArch §11 schema verbatim cross-ref
    type: "4-value enum closed-set (open-set 확장은 별 ADR carrier — 본 contract scope 외)"
    enum_values:
      SUCCESS:
        semantic: "전 영역 mirror + 0 degradation"
        trigger: "S1 closure OK (§4.11 exit 0) + S2 filter OK (§4.12 exit 0) + post-mirror sanity check PASS"
      SUCCESS_WITH_DEGRADATION:
        semantic: "mirror 완료 but warning tier 발생 (silent SUCCESS 거짓 기록 차단)"
        trigger: "S1/S2 exit 2 (degraded — malformed workflow yml lint warning + cp 진행) OR post-mirror sanity check warning"
      PARTIAL_FAILURE:
        semantic: "일부 영역 skip (atomic bundle invariant 보존)"
        trigger: "S1 closure partial (atomic skip — §4.11 partial_mirror_commit: forbidden 정합) OR post-mirror sanity check 일부 mismatch"
      FAILED:
        semantic: "mirror abort"
        trigger: "S1 dependency missing fail-closed (§4.11 on_dependency_missing: exit_1) OR S2 unknown repo_kind abort (§4.12 exit_code_contract: 1)"
    closed_set_invariant: "result field 미기록 / `SUCCESS` hardcode = forbidden — exit code → result enum deterministic mapping 의무. EC-1 (S1+S2 동시 발생) = `FAILED` 우선 (가장 심각 enum 우선, abort > partial). EC-2 (dry-run mode) = result field 미적용 (preview only, ADR-076 §결정 3 dry-run semantic 정합, CFP-898 §4.11 dry_run_behavior 동형). EC-3 (wrapper self-app mixed repo) = S2 filter skip + S1 closure OK → result `SUCCESS`."
    backward_compat: "기존 binary 가정 (`SUCCESS`/`FAILED`) → 3 신규 enum (`SUCCESS_WITH_DEGRADATION`/`PARTIAL_FAILURE`) = additive (기존 `SUCCESS` retain default semantic 보존 — 기존 SUCCESS-가정 consumer 코드 무영향, 신규 enum = 신규 honest reporting granularity. DataMigrationArch §11.4 migration backward-compat 영역)."
    external_pattern_alignment: "Terraform `plan -detailed-exitcode` tri-state (0=no-changes / 1=error / 2=changes) + Ansible `changed_when`/`failed_when` (changed/ok/failed/skipped) + Helm `--atomic` release status (FAILED) honest reporting 동형 (ResearcherAgent §6.1 carry-over)."

  degradation_propagation:   # exit code → result enum deterministic mapping (silent false SUCCESS 차단 core invariant)
    s1_fail_closed:
      source: "CFP-898 §4.11 fail_closed_behavior.on_dependency_missing: exit_1_with_error_log → reconcile-overlay.sh return 2 (ABORT)"
      result_enum: "FAILED (dependency missing fail-closed) — 부분 mirror 산출물 commit forbidden invariant (§4.11 partial_mirror_commit: forbidden) 정합. atomic skip 시 PARTIAL_FAILURE."
    s2_filter_abort:
      source: "CFP-899 §4.12 exit_code_contract: 1 = filter abort (unknown repo_kind / detect-repo-kind.py error) → reconcile-overlay.sh return 1 (ABORT)"
      result_enum: "FAILED (unknown repo_kind abort)"
      classification_not_severity_clause: "**S2 severity 입력 (`_S2_MAX_EXIT`) = filter decision 만** — detect-repo-kind classification exit 그대로의 전파 forbidden (§4.12 classification_severity_disjoint_invariant SSOT cross-ref). valid classification `plugin`/`consumer`/`mixed` (filter proceed/skip) = S2 severity **0** → result `SUCCESS` 방향 (정상 mirror, no degradation invariant 정합). 오직 `unknown`(classification 3) abort / detect-repo-kind crash / enum 오염 catch-all 만 S2 severity **1** → result `FAILED`. **CFP-986 post-merge defect**: reconcile-overlay.sh 가 classification exit `_ec` (consumer=1) 를 `_S2_MAX_EXIT` 에 무조건 전파 → `s2_exit_to_result(1)=FAILED` → 정상 consumer reconcile (sanity PASS, 0 loss, codeforge PRIMARY use case) 가 false `result: FAILED` 기록 (Epic CFP-858 §1 honest-reporting mandate 직접 위반, false SUCCESS 의 inverse — false FAILED). 본 clause = 기존 's2_filter_abort = unknown repo_kind abort → FAILED' semantic 의 explicit boundary enumeration (valid classification ≠ abort) — ratchet 강화 only, 의미 invariant 무변경 (ADR-064 §self-application 정합). 회귀 차단 discriminating test 의무: consumer fixture end-to-end → result `SUCCESS` (NOT FAILED) + unknown fixture → result `FAILED` (genuine abort 보존)."
    degraded_proceeded:
      source: "S1 §4.11 exit 2 (lint warning degraded) OR S2 §4.12 exit 2 (malformed whitelist degraded) — cp 진행"
      result_enum: "SUCCESS_WITH_DEGRADATION (silent SUCCESS 거짓 기록 차단 — EC-7 핵심 invariant)"
    sanity_check_outcome:
      sanity_warning: "SUCCESS_WITH_DEGRADATION"
      sanity_partial_mismatch: "PARTIAL_FAILURE"
      sanity_pass: "SUCCESS (S1/S2 모두 exit 0 전제)"
    deterministic_mapping_invariant: "exit code 조합 → result enum = pure function (집계 stage, side-effect 0). silent_skip_invariant: 0 (CFP-898 §4.11 silent_skip_invariant: 0 + ADR-076 §결정 6 wholesale_mirror_with_user_visible_loss_report honest reporting 강화 패턴 답습)."

  post_mirror_sanity_check:   # AC-2 SSOT — ADR-076 §결정 3 line 177-178 'snapshot → apply → 사후 sanity check 단일 unit' verbatim 정합
    invocation_stage: "wholesale_mirror cp 완료 직후 (S1 closure resolver hook → S2 filter hook → cp → 본 post-mirror sanity check + result enum 집계 — mirror-전 S1/S2 vs mirror-후 layer 분리 invariant)"
    impact_report_diff_scope: "expected (wrapper SSOT path list, S2 §4.12 whitelist filter 적용 후 set) vs actual (consumer-side mirrored file set, **동일 S2 §4.12 whitelist filter 기준 적용 후 set** — expected ↔ actual symmetric whitelist 기준) diff — **consumer customization preserve 영역 제외 (EC-4 false-positive 차단)**. consumer-customization-preserve 영역 enumeration: (a) marker block 안 inside-marker 영역 (CFP-899 §4.12 + ADR-076 §결정 6 marker preserve 정합) (b) **consumer `.claude/_overlay/` prefix 영역 안 wrapper SSOT 미존재 path** (consumer 자기 customization layer — ADR-027 consumer adoption protocol §결정 1 SSOT 정합, wrapper desired state 와 disjoint 영역. **prefix-based + wrapper SSOT 미존재 영역 cross-product check**: path `.claude/_overlay/` 접두로 시작 AND expected set 미포함 → consumer-only customization 분류 → exclude. wrapper SSOT 충돌 path = expected set 안 존재 → diff check 영역 보존, ADR-027 explicit consumer override 영역 별 carrier EC-5 분리)"
    whitelist_symmetry_invariant: "expected set 과 actual set 은 **동일 whitelist 기준**으로 산출 의무 — whitelist 가 전달된 경우 (reconcile 통합 경로, reconcile-overlay.sh S2 filter 적용 mirror) expected 가 whitelist 미등재 `.yml` 을 제외하면 actual 도 동일하게 whitelist 미등재 `.yml` 을 제외 (또는 extra 분류 시 일관 skip). **비대칭 금지** — expected whitelist 적용 + actual whitelist 미적용 = consumer mirror 된 whitelist 미등재 `.yml` 이 `extra = actual - expected` 에 항상 잔존 → false WARNING → false `SUCCESS_WITH_DEGRADATION` (정상 mirror = no degradation invariant 위반, EC-4 false-positive 차단 spec 위배). CFP-900 Phase 2 F-CR-900-3 evidence — `_expected_path_set` whitelist 적용 ↔ `_actual_path_set` whitelist 미적용 비대칭이 false `SUCCESS_WITH_DEGRADATION` 유발. 본 invariant = EC-4 false-positive 차단 의도의 explicit enumeration (의미 invariant 무변경 — ratchet 강화 only, 기존 spec '정상 mirror = no degradation' + 'S2 whitelist filter 결과 정합성 1차 검사' 의 actual-side 처리 명시화. ADR-064 §self-application 정합)."
    sanity_check_depth: syntax_level_v1
    sanity_check_depth_definition:
      include:
        - "file 존재성 (expected set 의 각 file 이 consumer-side 존재)"
        - "path set diff (expected path set vs actual path set symmetric difference)"
        - "workflow yml `bash -n` / yaml parse OK (syntax-level 1차 신호)"
      exclude:
        - "(semantic-level — workflow logic equivalence diff — AM-3 derived default 외, future CFP separate, CFP scope unitary ADR-064 §결정 1.3)"
      rationale: "AM-3 derived default — syntax-level 1차 신호 (CFP-898 §4.11 AM-1 stdlib only 패턴 답습, parser dependency 0). semantic depth = future CFP separate scope."
    filesystem_only_invariant: true   # network call 0 / gh api 0 — post-mirror diff = consumer 권한 area only, trust surface 0 (SecurityArch primary, CFP-899 §4.12 filesystem_only_invariant 동형)
    idempotency_invariant: "post-mirror sanity check = pure read-only verify (write 0, side-effect 0, 반복 = 동일 result — DataMigrationArch §11.6 idempotent invariant)"
    sanity_check_failure_behavior:
      phase_1_scope: "schema/binding declare only (실 rollback runtime = Phase 2 carrier — AM-4 derived default, CFP-898 §4.11 schema_declared_phase1 패턴 답습)"
      adr_076_alignment: "ADR-076 §결정 3 line 178 verbatim '사후 sanity check 실패 시 자동 rollback' 정합 — runtime rollback = Phase 2 over-commit 회피 (Phase 1 = schema declare scope)"
    mctrader_data_81_class_prevention: "workflow yml mirror 후 consumer-side 의존 script 존재성 + S2 whitelist filter 결과 정합성 1차 검사 (S1 closure resolver = mirror-전 vertical / 본 sanity check = mirror-후 post-verify horizontal — layer 분리 invariant). mctrader-data#81 14 failing checks class 재발 차단 (Epic CFP-858 §1 motivation verbatim)"

  fast_pass_content_sanity:   # AC-3 SSOT — ADR-026 Amendment 5 §결정 7 carrier
    target: "templates/github-workflows/phase-gate-mergeable.yml (+ .github/workflows/phase-gate-mergeable.yml byte-identical self-app mirror, ADR-005) 의 `.github/` 경로 fast-pass (isDocOnly line 180 `f.filename.startsWith('.github/')` + isSiblingPr line 173)"
    signal_scope: "변경된 `.github/workflows/*.yml` 안 의존 script reference (`run: bash scripts/check-*.sh` / `python3 templates/scripts/*.py`) 가 동일 PR diff 안 존재 OR repo 안 존재하는지 mismatch detect — S1 closure resolver (CFP-898 §4.11) 의 phase-gate-mergeable layer mirror (mirror-time vertical vs gate-time signal — layer 분리 invariant)"
    severity: warning_tier
    severity_rationale: "AM-1 derived default — fast-pass PASS 자체 보존 (fast-pass 정책 약화 = ADR-064 ratchet 위배). content mismatch 시 1차 warning emit + PR comment. blocking 승격 = evidence-checks-registry tier 승격 gate AND condition 충족 후 future CFP separate"
    fast_pass_or_gate_unchanged_invariant: "fast-pass OR-gate (isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix) 자체 변경 0 — content sanity = orthogonal warning layer 1단 추가 (ADR-026 Amendment 4 §결정 6 3-source → 4-source ratchet 강화 패턴 답습, gate 약화 0). EC-5 (fast-pass 이미 PASS 후 content mismatch 발견) = warning tier emit (fast-pass PASS 자체 보존)"
    ci_advisory_pattern_alignment: "GitHub required vs optional check pattern (optional = warning emit but merge 미차단) 동형 (ResearcherAgent §6.1 carry-over). consumer 가 'fast-pass PASS = 안전' 오인으로 전체 CI 마비 P0 차단 (Epic CFP-858 §1 motivation verbatim)"

  upgrade_event_honest_record:   # ADR-076 Amendment 3 §결정 3 sub-clause core invariant
    artifact: "docs/upgrade-events/<date>-<version>.md (ADR-076 §결정 3 line 170 snapshot layer event log mirror schema — 실 artifact 생성 = Phase 2 carrier, Phase 1 = schema declare)"
    result_field_invariant: "result: <enum> field 의무 — 미기록 / `SUCCESS` hardcode = forbidden. exit code → result enum deterministic mapping 의무 (degradation_propagation SSOT)"
    false_success_blocked_rationale:
      - "(a) silent `SUCCESS` 거짓 기록 → S1 fail-closed / S2 abort / degraded 결함 은폐 (Epic CFP-858 §1 motivation verbatim — 'upgrade-event 로그 result: SUCCESS ... 가 결함을 가린다')"
      - "(b) 명시적 result enum = upgrade 자동화 신뢰성 (Epic §1 WHY '한 번 명령 = 끝까지 정합, 다시 손댈 필요 없음')"
      - "(c) CFP-898 §4.11 silent_skip_invariant: 0 + ADR-076 §결정 6 wholesale_mirror_with_user_visible_loss_report honest reporting 강화 패턴 답습"

  hook_integration:
    file: "scripts/reconcile-overlay.sh"
    invocation_point: "wholesale_mirror cp **후** (CFP-898 §4.11 closure resolver hook → CFP-899 §4.12 consumer-applicability filter hook → cp → 본 post-mirror sanity check + result enum 집계 — sequential composition order temporal-post layer 추가)"
    sequential_composition_order:
      - step_1: "CFP-898 §4.11 closure resolver hook (closure missing 시 fail-closed return 2)"
      - step_2: "CFP-899 §4.12 consumer-applicability filter hook (closure full but consumer-non-applicable 시 skip 또는 fail-closed unknown 시 return 1)"
      - step_3: "cp 실행 (filter PASS 시점)"
      - step_4: "CFP-900 §4.13 post-mirror sanity check + S1/S2 exit code → result enum 집계 (mirror-후 temporal-post)"
    result_enum_aggregation: "S1 (step_1 exit code) + S2 (step_2 exit code) + sanity check (step_4 outcome) → result enum deterministic mapping (degradation_propagation SSOT). pure function, side-effect 0"
    development_lane_phase: "Phase 2 PR 영역 (본 Phase 1 PR scope 외 — Develop lane DeveloperAgent 영역). caller_pattern_evidence: CFP-898 §4.11 + CFP-899 §4.12 hook 동형 패턴 — `return 1` / `return 0` / `return 2` 분기 자연 통합 가능 [hypothesis — verify in Phase 2 PR implementation step, CFP-898/CFP-899 hook precedent 의존]"

  out_of_scope:
    - semantic_level_sanity_check   # AM-3 derived default 외 — workflow logic equivalence diff (future CFP separate, CFP scope unitary ADR-064 §결정 1.3)
    - fast_pass_content_sanity_blocking_tier   # AM-1 derived default 외 — evidence-checks-registry tier 승격 gate AND condition 충족 후 future CFP separate
    - post_mirror_sanity_check_runtime_rollback   # AM-4 derived default 외 — Phase 2 carrier (Phase 1 = schema declare only, ADR-076 §결정 3 line 178 자동 rollback runtime 은 Phase 2)
    - dry_run_mode_result_field   # EC-2 — dry-run = 실 변경 0 → result field 미적용 (preview only, ADR-076 §결정 3 dry-run semantic 정합)
    - marker_valid_branch   # MARKER_VALID branch 진입 시 post-mirror sanity check 미invoke (caller responsibility, reconcile-overlay.sh top-level guard — CFP-898 §4.11 / CFP-899 §4.12 동형 pattern)
    - mctrader_data_81_backfill_remediate   # cross-repo, Epic CFP-858 close 후 별 work (Epic §위험 신호 verbatim)
    - new_adr_084   # S3 = ADR-026 Amd5 + ADR-076 Amd3 ratchet 강화로 충분 (S1 ADR-076 Amd2 / S2 ADR-083 신규 와 비대칭, Architect lane minimal-change 결정 — ADR-RESERVATION row 84 reserve 불요)

  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.10 = 강화 only (result fidelity layer 추가), weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 SSOT — 본 binding 은 wholesale_mirror branch temporal-post honest reporting, family scope 무변경)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (의미 invariant 무변경 + result fidelity sub-clause 추가는 ratchet 강화 방향, ADR-076 §결정 6 Amendment 1 SSOT)
    transaction_completion_criterion: unchanged
    snapshot_reset_disjoint_layer: unchanged
    adr_053_d2_verbatim_quote: unchanged
```

Phase 1 (CFP-900) merge 시 본 §4.13 binding block 활성 (schema declare — result fidelity 영역 declaration). Phase 2 (별 PR, Develop lane) merge 시 `scripts/reconcile-overlay.sh` wholesale_mirror cp 후 post-mirror sanity check stage 추가 (S1/S2 exit code → result enum deterministic mapping 집계) + `docs/upgrade-events/` 디렉토리 + result enum 4-value event log artifact schema 실 생성 + `templates/github-workflows/phase-gate-mergeable.yml` (+ `.github/workflows/` byte-identical mirror, ADR-005) 의 `.github/workflows/*.yml` 의존 script reference content sanity 1차 신호 (warning tier, fast-pass OR-gate 무변경 orthogonal layer) + `tests/test_reconcile_sanity_check.py` (또는 reconcile-overlay.sh inline — Architect minimal-change 결정 영역) post-mirror sanity check + result enum mapping unit TC + `tests/integration/test_reconcile_overlay_result_fidelity.bats` 통합 테스트 (wholesale_mirror + S1 fail-closed/S2 abort → result enum 정직 반영 + EC-1~7) + `tests/workflows/test_phase-gate-mergeable-yml.sh` content sanity 1차 신호 assertion 추가 + `.claude-plugin/plugin.json` + `CHANGELOG.md` + `marketplace.json` v5.91.0 3-file atomic (ADR-063 mirrored field 4종 atomic invariant + ADR-016 marketplace parity) + `CHANGELOG.md` row append.

### §4.13 sunset boundary (CFP-1111 carrier)

본 binding (result_fidelity_binding, v1.10 CFP-900 carrier) 는 CFP-1111 walker paradigm 으로 carry.

- **metric**: walker walk_result 4-value enum (SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED) 정확 enforce + silent false SUCCESS 0건 / N walk + post-mirror diff sanity check 동등 semantic
- **who**: imperative-walker-protocol-v1 walker schema field `walk_result` + `exit_code_to_walk_result_mapping` rule
- **how**: walker integration test 안 4-value enum honest record verify + exit code → result enum deterministic mapping verify

closed_enum invariant: walker schema 안 `walk_result` field 의 `open_extension: false` 명시 의무 (Wave 1 Story-2 ADR-α2 carry). β2 audit (#1113) 3 carry-over 설계 주의 사항 #1 정합.

### 4.14 Wave 4 sub-Epic #1 Story-4 / Story-5 canary compatibility check binding (v1.11 — CFP-991 §4.3 (l) trigger 신설 발동, ADR-72 amendment_log Amendment 3 + ADR-076 §결정 9.2 / §결정 9.6 + ADR-070 §결정 D6 (CFP-988 Amendment 4) + label-registry-v2 v2.34 → v2.35 carrier · v1.12 — CFP-1014 §4.3 (m) trigger 신설 발동, downgrade_asymmetry_marker.status: placeholder_reserve → wired 단독 promotion 활성 완료, §4.8 단독 promotion 선례 verbatim 답습, Wave 4 sub-Epic #882 close marker 5/5 Story complete final state)

본 §4.10 (`multi-version channel pin declare layer` + runtime active) + §4.11 (dependency bundle integrity vertical mirror-전) + §4.12 (consumer-applicability filter horizontal mirror-전) + §4.13 (result fidelity temporal-post mirror-후) binding 위에 **canary promotion criteria enforcement layer** 1단을 추가한다. §4.10 = channel state binding (현재 어떤 channel) ↔ §4.14 = canary promotion gate (어떻게 promote) **axis disjoint** invariant 보존 — embedding_forbidden: true (RefactorAgent C-4 cross-block 명시). Story-4 = §4.10 `registry_channel_matrix.story_4_scope_write_carrier` A3 정정 entry forward-effective realize point (v1.8 A2 = predict / v1.11 A3 = enact transition, DataMigrationArch §11.7 load-bearing dissent verbatim 채택). 5 threat × mitigation matrix carrier (SecurityArch §7.2 5 threat T-1.1/T-2.1 답습/T-3.1/T-4.1/T-5.1 schema field layer carrier). ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING cross-ref T-4.1 4-tuple measurement spoofing mitigation. Live touching: TRUE / production_cutover_touching: TRUE / marketplace_publish_touching: best_effort_declare. wrapper-self-app Tier-1 exemption invariant 보존 (ADR-72 §결정 6) — wrapper PR 자체 = declare-time 영역, consumer canary→beta promotion = Tier-2 admin-tier 권장.

```yaml
canary_compatibility_check_binding:   # v1.11 신설, CFP-991 §4.3 (l) 발동, ADR-72 amendment_log Amendment 3 + ADR-076 §결정 9.2/9.6 + ADR-070 §결정 D6 carrier
  carrier_story: CFP-991  # Wave 4 sub-Epic #1 Story-4 (Epic CFP-882)
  carrier_adrs:
    - "ADR-72 amendment_log Amendment 3 (§결정 1 표 wrapper governance row append + §결정 5 표 row append)"
    - "ADR-076 §결정 9.2 `channel-aware version pin` + §결정 9.6 promotion criteria 4-tuple SSOT empirical anchor (4 industry exemplar: Chrome 3-channel Stable/Beta/Canary + npm dist-tag + Rust 3-channel + K8s 3-stage)"
    - "ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING — §7.6 T-4.1 4-tuple measurement spoofing mitigation cross-ref"
    - "ADR-016 §결정 1 family_7_plugin_atomic SSOT + Amendment 3 channel 차원 확장"
    - "ADR-063 Amendment 5 §결정 15 publisher↔registry↔consumer 3-way version atomic invariant"
  status: schema_declared_phase1   # Phase 1 = schema binding declare + workflow + scripts/lib (warning tier 활성) / Phase 2 (별 PR, Develop lane) = blocking-on-pr 승격 + consumer canary→beta promotion runtime evaluation 영역
  scope: "consumer canary→beta promotion gate evaluation 영역 한정 — Story-4 carrier = wrapper Tier-1 declare-time exemption (§결정 6 wrapper-self-app N/A invariant 정합) + consumer Tier-2 runtime measurement (canary tier 활성 consumer Story carrier)"
  axis_disjoint_declaration:   # RefactorAgent C-4 (§4.10 ↔ §4.14 interface separation)
    channel_state_axis: "§4.10 multi_version_channel_pin_binding — channel tier resolve + `family atomic pin` + 3-way drift detect (현재 어떤 channel)"
    promotion_gate_axis: "§4.14 canary_compatibility_check_binding — promotion criteria evaluation + transition gate (어떻게 canary → beta → stable promote)"
    embedding_forbidden: true   # §4.10 블록 내 §4.14 로직 inline embed = SRP 위반 (RefactorAgent A-2 명시)
    prerequisite_binding_ref: "§4.10 multi_version_channel_pin_binding (channel state SSOT — 현재 어떤 channel, read-only import)"

  enabled:
    default: true                       # canary tier consumer 활성 시 자연 enabled
    consumer_opt_out: false              # consumer override 불가 — promotion criteria = wrapper Tier-1 SSOT (canary tier 활성 자체가 admin tier 권장 advisory)
    workflow_self_app_exemption: "production_cutover_touching=true AND repo=wrapper AND code_change=0 triple-AND fast-PASS (Tier-1 exemption, ADR-72 §결정 6 정합)"

  promotion_criteria_4tuple:   # ADR-076 §결정 9.6 SSOT 4 industry exemplar verbatim cite — Chrome 3-channel primary + npm dist-tag / Rust 3-channel / K8s 3-stage 보조
    semantic: "canary → beta promotion gate evaluation 의 4 measurement source (functional + security + monitoring + testing) SSOT — 각 criterion 별 measurement_source + gate_state enum (pass/fail/n_a) 의무. 4-tuple all PASS = promotion gate proceed / 1+ fail = promotion abort (warning tier — Phase 1 default warning_first)"
    sub_fields:
      functional:
        measurement_source: "consumer Story functional test pass-rate (bats GREEN ratio + integration test PASS evidence)"
        gate_state_enum: ["pass", "fail", "n_a"]
        evidence_origin_annotation_required: true   # T-1.1 elevation 차단 — wrapper_self vs consumer_self vs mixed 명시 의무
      security:
        measurement_source: "consumer Story SecurityTestPLAgent verdict + ProductionEvidenceDeputy spawn evidence (consumer canary tier 활성 Story carrier 영역)"
        gate_state_enum: ["pass", "fail", "n_a"]
        evidence_origin_annotation_required: true
      monitoring:
        measurement_source: "consumer production-side monitoring metric (Prometheus rate / drainage rate / WAL sample — ADR-72 §결정 5 evidence quad 정합)"
        gate_state_enum: ["pass", "fail", "n_a"]
        evidence_origin_annotation_required: true
      testing:
        measurement_source: "consumer Story IntegrationTestAgent verdict (Epic-level baseline v2 promotion criteria 4-tuple executable — ADR-055 Amendment 3 §결정 1 cross-ref)"
        gate_state_enum: ["pass", "fail", "n_a"]
        evidence_origin_annotation_required: true
    aggregation_rule: "4 sub all 'pass' OR ('pass' + 'n_a' 조합) = promotion gate proceed (exit 0) / 1+ 'fail' = promotion abort (exit 1 warning_first / blocking_on_pr 승격 후 exit 2)"
    backward_compat: "canary 미선언 consumer (codeforge.channel.tier ≠ canary OR field 부재) = workflow skip mode exit 0 PASS (additive only, project-config-schema §1.1 선택 필드 invariant 정합 — DataMigrationArch §11.9 backward-compat AC-26~AC-30)"

  family_7_atomic_canary_pin:   # RefactorAgent C-3 (length_invariant + member_enum schema-level 선언) — INV-3 (TestContractArch / DataMigrationArch INV-C)
    semantic: "ADR-016 §결정 1 family_7_plugin_atomic + Amendment 3 channel 차원 확장 — canary tier 활성 시 family 7 plugin 모두 동시 canary tier 활성 의무 (mixed channel 차단)"
    publisher_versions:
      type: "array"
      length_invariant: 7   # codeforge family 7 plugin 고정 (wrapper + 6 lane plugin)
      length_violation_behavior: "validator FAIL exit 2 — ADR-016 §결정 1 family scope invariant 위배 (RefactorAgent C-3)"
      member_enum: ["codeforge", "codeforge-requirements", "codeforge-design", "codeforge-develop", "codeforge-test", "codeforge-review", "codeforge-pmo"]
      schema: "[{plugin_name: <member_enum>, plugin_json_version: <semver string>}, ...]"
    three_way_match:
      semantic: "publisher 7 plugin × registry marketplace.json channels[tier=canary].version[] × consumer .codeforge.channel.tier=canary 3-way byte-identical (ADR-063 Amendment 5 §결정 15 cross-ref)"
      check_command: "scripts/check-canary-compatibility.sh (3-tier exit code: 0=PASS / 1=warning missing / 2=mechanical anchor invalid)"
      detect_target: "(a) publisher plugin.json `.version` (7 plugin × 1 each) ↔ (b) registry marketplace.json `plugins[name=<plugin>].channels[tier=canary].version` ↔ (c) consumer `.claude/_overlay/project.yaml codeforge.channel.tier=canary` declared"
      failure_mode: "3-way mismatch detect → fail-loud exit 2 (CFP-932 D2 atomic-upgrade-7-plugins.sh mixed channel detection 패턴 답습)"
    rationale: "ADR-016 §결정 1 family atomic unit — canary tier 가 family 7 plugin 부분 활성 시 inter-plugin contract MANIFEST invariant 위배 risk + 6 lane plugin 간 contract version skew 발생"

  canary_consumer_evidence_origin:   # RefactorAgent C-1 (open_extension: false closed-set enum 명시 강화) — SecurityArch T-1.1 wrapper Tier-1 declare-time bypass mitigation core field
    enum: ["wrapper_self", "consumer_self", "mixed"]
    open_extension: false   # closed-enum invariant — ADR-064 §self-application ratchet 강화 only (RefactorAgent C-1)
    extension_protocol: "enum 확장 시 reconcile-protocol-v1 MINOR bump + scripts/lib/canary-compatibility-helpers.sh::_validate_enum_closed_set() helper 갱신 + label-registry-v2 sibling carrier 의무 (별 CFP)"
    semantic:
      wrapper_self: "wrapper PR scope (Tier-1 declare-time exemption) — code 0 risk class, developer self-service. 사용 영역 = ADR-72 §결정 6 wrapper-self-app N/A invariant 정합 (영구 fast-PASS scope)"
      consumer_self: "consumer canary tier 활성 Story scope (Tier-2 runtime measurement) — HIGH risk class, admin-tier 권장 advisory. 사용 영역 = consumer Live touching Epic carrier (ProductionEvidenceDeputy spawn 영역)"
      mixed: "wrapper + consumer 양 source 혼합 (예: wrapper PR 가 schema declare + consumer가 4-tuple evidence runtime 측정) — boundary axis 명시 의무, mixed 시 양 source 별도 trust state annotation 의무"
    annotation_format: "promotion_criteria_4tuple sub_fields[*].evidence_origin = <enum value> annotation 의무 — T-1.1 elevation 차단 (wrapper-side declare → consumer-side measurement 의무 elevation 금지)"
    threat_mitigation: "SecurityArch §7.2 T-1.1 (wrapper Tier-1 declare-time bypass) core mitigation field — wrapper_self 선언 시 Tier-1 exemption 한정 / consumer_self 선언 시 Tier-2 boundary 분리 / mixed 선언 시 양 source separate trust state"

  inter_plugin_contract_backward_compat_verify:   # SecurityArch §7.2 T-4.1 4-tuple measurement spoofing mitigation field
    minor_only_rule_passed:
      type: "bool"
      semantic: "ADR-008 §결정 2 MINOR-only invariant guard — promotion gate evaluation 시점 inter-plugin contract (review-verdict-v4 / label-registry-v2 / reconcile-protocol-v1 / 기타 kind:registry) MAJOR bump 없는지 verify"
      check_command: "scripts/check-canary-compatibility.sh::verify_inter_plugin_contract_minor_only (MANIFEST.yaml + frontmatter version diff 확인)"
      failure_mode: "MAJOR bump detect → fail-loud exit 2 (ADR-008 §결정 2 SemVer 2-tier rule 위배 = schema breaking change, canary tier 활성 영역 진입 차단)"
    three_way_match_field_reference: "family_7_atomic_canary_pin.three_way_match (위 field 재참조 — single source of truth 보존, RefactorAgent A-2 SRP 정합)"
    rationale: "T-4.1 4-tuple measurement spoofing → ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING 4-tuple ((a) CR-own discriminating revert / (b) reconcile-integration path / (c) DevPL pasted stdout 미신뢰 / (d) single-aggregator/single-unit bypass forbidden) cross-ref — promotion gate evaluation 시점 single-aggregator bypass 금지 + real execution evidence direct verify 의무"

  promotion_gate_failure_mode:   # RefactorAgent C-2 (closed-set enum + escalation_path 명시 강화) — ADR-060 §결정 5 default
    enum: ["warning_first", "blocking_on_pr"]
    open_extension: false
    default: "warning_first"   # ADR-060 §결정 5 default 정합 — Phase 1 = warning tier 활성
    escalation_path: "warning_first → blocking_on_pr (ADR-060 evidence-enforceable 4-tier promotion gate 정합, 역방향 약화 = ADR-058 §결정 5 sunset_justification 의무) — Phase 2 (별 PR, Develop lane) = warning → blocking-on-pr 승격 carrier (별 follow-up CFP)"
    bypass_label: "hotfix-bypass:canary-promotion-criteria"   # label-registry-v2 v2.37 신규 entry (46번째 family member)
    bypass_audit_lint: "bash scripts/check-bypass-audit-comment.sh (audit comment 자동 발의 — reuse 패턴, 기존 entry 동일)"

  downgrade_asymmetry_marker:   # RefactorAgent B-2 (§4.8 placeholder_reserve → active 단독 promotion 선례 답습) — SecurityArch T-5.1 mitigation core field, v1.12 CFP-1014 Story-5 carrier wired 활성 완료
    status: "wired"   # v1.12 (CFP-1014 Story-5) — placeholder_reserve → wired 단독 promotion 완료 (§4.8 version_handshake 단독 promotion 선례 verbatim 답습, partial-active state 도입 0, field shape 변경 0)
    carrier_story: "CFP-1014"   # v1.12 carrier→realized 정정 (v1.11 = 'CFP-991-Story-5' placeholder, v1.12 = 'CFP-1014' realized — CFP-744 / CFP-745 carrier→realized 정정 패턴 답습, fact 영향 0 추적성만 ADR-068 I-4 wording SSOT 정합)
    closed_enum: ["placeholder_reserve", "wired"]   # length=2 invariant (Story-4 placeholder_reserve only / Story-5 wired 활성 완료), open_extension: false 명시 (SecurityArch ratchet 강화)
    open_extension: false   # v1.12 (CFP-1014) — closed_enum invariant 명시화, downgrade_asymmetry_marker enum 확장 차단 boundary 명문화 (SecurityArch ratchet 강화 권고, ADR-064 §self-application 강화 방향 정합)
    rationale: "stable → beta demotion 또는 beta → canary demotion 가 promotion 역방향 path — asymmetry marker 가 declare 영역에서 wired 형태로 명시되어 downgrade path 가 promotion symmetry assumption 으로 우회될 가능성 차단 (SecurityArch T-5.1 mitigation core field, v1.12 CFP-1014 Story-5 carrier 가 wired 활성 완료)"
    activation_protocol: "Story-5 Phase 1 = status: placeholder_reserve → wired 단독 전환 활성 완료 (§4.8 version_handshake placeholder_reserve → active 단독 promotion 선례 verbatim 답습 완료 — partial-active state 도입 0, field shape 변경 0, closed_enum length=2 invariant 보존, v1.12 CFP-1014 forward-effective)"
    sunset_justification: "Story-5 carrier 가 wired 전환 시 ADR-058 §결정 5 sunset_justification 영역 외 (asymmetry = directional ratchet 강화 0)"

  hook_integration:
    file: "scripts/check-canary-compatibility.sh"
    helper_lib: "scripts/lib/canary-compatibility-helpers.sh"   # RefactorAgent A-3 + B-3 (thin orchestrator + helper lib extraction CFP-954 gh-api-helpers.sh 선례 답습)
    workflow: "templates/github-workflows/canary-promotion-criteria.yml (+ .github/workflows/canary-promotion-criteria.yml byte-identical mirror, ADR-005)"
    trigger_modes: ["pull_request_open", "workflow_dispatch"]   # ADR-72 §결정 5 production-cutover-evidence.yml D2 consensus 답습 (event-driven not continuous monitoring, cron 24h 미권고)
    helpers:   # RefactorAgent B-3 (4 helper extraction)
      - "_extract_4tuple_measurement_source()"   # promotion_criteria_4tuple 각 sub의 measurement_source 파싱
      - "_enumerate_family_7_canary_versions()"   # publisher_versions[7] array enumerate (length=7 invariant 검증 포함)
      - "_three_way_version_diff()"               # publisher ↔ registry ↔ consumer 3-way version diff (§4.8 orthogonality invariant 재사용)
      - "_validate_enum_closed_set()"             # canary_consumer_evidence_origin / promotion_gate_failure_mode 양 enum closed-set 검증
    mock_seam:   # TestContractArch mock seam `_CFP991_MOCK_*` namespace (CFP-932 `_CFP932_MOCK_*` 답습)
      env_vars:
        - "_CFP991_MOCK_MARKETPLACE_CHANNELS"   # cross-repo gh api mock
        - "_CFP991_MOCK_FAMILY_VERSIONS"         # 7-plugin version array mock
        - "_CFP991_MOCK_DRIFT_THRESHOLD"         # configurable threshold mock
      scope: "bats test fixture 안에서만 활성 + setup/teardown export — production runtime 안 NEVER read"
      probe_sandbox_env: "scripts/check-probe-sandbox-env.sh (CFP-843) + bats setup/teardown export 패턴 답습"
    exit_code_contract:
      "0": "PASS (3-way match + 4-tuple all 'pass' OR 'n_a')"
      "1": "warning (missing data / network 일시 실패 / sandbox-bound fetch fail) — advisory only, hotfix-bypass:canary-promotion-criteria bypass 가능"
      "2": "mechanical anchor invalid (schema breach / real divergence) — hard fail + Issue auto-create + on-call notification"
    sequential_composition_order:
      - step_1: "wrapper-self-app Tier-1 exemption fast-PASS check (triple-AND: production_cutover_touching=true AND repo=wrapper AND code_change=0 → exit 0)"
      - step_2: "_validate_enum_closed_set() — canary_consumer_evidence_origin + promotion_gate_failure_mode 양 enum closed-set verify"
      - step_3: "_enumerate_family_7_canary_versions() — publisher_versions[] length_invariant=7 + member_enum verify"
      - step_4: "_extract_4tuple_measurement_source() — promotion_criteria_4tuple 각 sub measurement_source + evidence_origin annotation verify"
      - step_5: "_three_way_version_diff() — publisher↔registry↔consumer 3-way match verify (ADR-063 Amendment 5 §결정 15 cross-ref)"
      - step_6: "promotion_gate_failure_mode 평가 → exit 0/1/2 deterministic mapping"

  out_of_scope:
    - downgrade_path_runtime   # v1.12 (CFP-1014 Story-5) — wired 활성 완료, downgrade execution runtime = 별 future carrier (declarative SSOT only / runtime execution layer = sequential carrier disjoint declarative — Story-5 declare-only)
    - blocking_on_pr_tier      # Phase 2 carrier (별 PR, Develop lane — escalation_path warning → blocking)
    - consumer_4tuple_runtime_measurement   # consumer Story carrier 영역 (Tier-2 runtime, wrapper Story-4 scope 외)
    - marketplace_channels_populate_runtime   # Story-4 = declare layer + helper lib scope, marketplace.json channels[] real populate (cross-repo write) = sequential carrier (Story-4 forward-effective realize point declare only, real cross-repo write = consumer marketplace governance gate)
    - wrapper_self_app_runtime_4tuple_measurement   # ADR-72 §결정 6 wrapper-self-app N/A invariant 정합 (영구 fast-PASS scope)

  ratchet_invariant_preserved:   # ADR-064 §self-application — v1.11 = 강화 only (canary promotion criteria enforcement layer 추가) / v1.12 (CFP-1014 Story-5) = 강화 only (downgrade_asymmetry_marker wired 활성 + closed_enum open_extension:false 명시 + §4.4 row 7 역방향 약화 차단 row append), weakening 0
    user_decision_branches_0: unchanged
    atomicity_boundary_semantic_invariant: unchanged   # family_7_plugin_atomic (ADR-016 §결정 1 SSOT 무변경 — canary promotion criteria = enforcement layer wrapper-side declare, family scope 무변경)
    marker_block_absent_behavior: unchanged             # wholesale_mirror_with_user_visible_loss_report (ADR-027 §결정 7.C — canary tier 무관)
    transaction_completion_criterion: unchanged        # ADR-053 §D2 verbatim
    snapshot_reset_disjoint_layer: unchanged           # ADR-067 cross-pollinate forbidden
    adr_053_d2_verbatim_quote: unchanged               # L150-151 weakening 차단
```

Phase 1 (CFP-991) merge 시 본 §4.14 binding block 활성 (schema declare + workflow + scripts/lib warning tier 활성) — declaration + mechanical lint enforcement carrier. **v1.12 (CFP-1014 Story-5)** merge 시 `downgrade_asymmetry_marker.status: placeholder_reserve → wired` 단독 promotion 완료 (§4.8 단독 promotion 선례 verbatim 답습, partial-active state 도입 0 / field shape 변경 0 / closed_enum length=2 invariant 보존). Phase 2 (별 PR, Develop lane) merge 시 promotion_gate_failure_mode `warning_first → blocking_on_pr` 승격 + consumer canary→beta promotion runtime 4-tuple evaluation 실 carrier 영역 + downgrade execution runtime path (별 future carrier — Story-5 = declare-only disjoint declarative SSOT only, runtime demotion execution path = sequential carrier). Sibling carrier: ADR-72 amendment_log Amendment 3 + label-registry-v2 v2.34 → v2.35 MINOR (4 신규 entry) + `docs/evidence-checks-registry.yaml` `canary-compatibility-check` entry (warning tier) + `docs/domain-knowledge/domain/production-cutover/promotion-criteria-4tuple.md` 신설 (CFP-28 6-section schema, 4 industry exemplar verbatim cite) + `docs/parallel-work/section-ownership.yaml` `canary_compatibility_check` row append + `docs/doc-locations.yaml` 16번째 entry `promotion_criteria_4tuple_artifact` 신설.

### §4.14 sunset boundary (CFP-1111 carrier)

본 binding (canary_compatibility_check_binding + downgrade_asymmetry_marker, v1.11→v1.12 chain) 는 CFP-1111 walker paradigm 으로 carry.

- **metric**: walker step 의 `directionality: forward_only` + `downgrade_path_forbidden: true` field 정확 enforce + downgrade 방향 시도 0건 (silently 통과) / N walk + canary→beta→stable 7-tuple consistency 동등 enforce
- **who**: walker schema field `directionality` + `downgrade_path_forbidden` + `gate_failure_mode`
- **how**: walker integration test 안 forward-only directionality verify + reverse path 시도 시 walk_result = FAILED 정확 분류

closed_enum invariant: walker schema 안 `directionality` enum 의 `open_extension: false` 명시 의무. β2 audit 3 carry-over 설계 주의 사항 #1 정합.


