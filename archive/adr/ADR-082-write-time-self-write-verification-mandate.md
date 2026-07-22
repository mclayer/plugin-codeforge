---
adr_number: 82
title: Write-time self-write verification mandate — internal lane agent §9 evidence / Phase 0 mapping / corpus enumeration verify super-class
status: Accepted
category: governance
date: 2026-05-17
carrier_story: CFP-776
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    carrier_story: CFP-841
    date: 2026-05-17
    summary: "§결정 6 behavioral→mechanical 전환 — mechanical_enforcement_actions[] empty → 2-entry (corpus-claim-verify scope 2(a) / cross-plugin-ownership-verify scope 2(d)). §결정 6 rationale 1 partial-stale 정정 (lane-self-write-ownership-matrix.yaml 실재 — registry 부재 아닌 cross-plugin 영역 확장 + lint binding)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: behavioral mandate → mechanical enforcement scope 확장, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 2
    carrier_story: CFP-1016
    date: 2026-05-19
    summary: "§결정 1 layer 1 (Orchestrator scope) 확장 — Orchestrator-authored Issue body pre-publish verify mandate. 3 occurrences pattern_count (CFP-1000 inversions / CFP-1001 lint output verbatim FP / CFP-1002 ADR-054 filename missing 'story') ≥ ADR-045 §D-9 threshold 2 escalation. Wave 1 mechanical = (a) story-page-structure.md template §2.1 codification + issue_origin frontmatter 신설 + (b) playbook §3.17 behavioral mandate. scope (c) RequirementsPL spawn prompt template = 별 canonical CFP (CFP-1002 precedent)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 Orchestrator scope verify-before-trust 가 Issue-body authorship 영역으로 확장, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 3
    carrier_story: CFP-1041
    date: 2026-05-20
    summary: "ADR-085 cross-ref 보완 관계 명시 (disjoint complement — verify axis ↔ coordination axis). ADR-082 = internal lane agent self-write 한정 (§9 evidence / Phase 0 mapping / corpus enumeration / Issue body authorship write-time semantic truth verify, verify axis) ↔ ADR-085 = 복수 Claude Code session 동시 작업 시 ownership 결정 / 분담 / handoff (coordination axis, pre-hoc cross-session). 두 layer axis 자체가 다름 — verify 가 충족되어도 coordination axis 부재 시 parallel race 발생, coordination 결정 후에도 verify 미수행 시 false claim. 둘 다 필요한 orthogonal layer. ADR-085 §결정 1 5-layer 표 anchor 가 본 ADR §결정 1 4-layer 표 verbatim 답습 base (5번째 row Multi-session coordination 신설). cross-ref-only — 본 ADR §결정 1-8 + Amendment 1-2 + 본문 §결정 / mechanism 의미 변경 0. ADR-073 Amendment 4 동형 precedent (verify axis ↔ coordination axis disjoint complement cross-ref-only pattern)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-085 cross-ref 보완 관계 disjoint complement 명시 — coordination axis layer 추가, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 4
    carrier_story: CFP-1058
    date: 2026-05-20
    summary: "ADR-RESERVATION schema `amendments_reserved[]` sub-tree 신설 cross-ref — Amendment id slot reservation 형식화 (CFP-1041 vs CFP-689 Amendment id race precedent evidence). ADR-RESERVATION 가 ADR number reservation field 보유하나 Amendment id reservation field 부재 영역 (race-winner-takes-it convention informal) → 본 Amendment 가 schema codify cross-ref. ADR-082 본문 §결정 1-8 + Amendment 1-3 본문 의미 변경 0건. ADR-054 §결정 1 doc-only fast-path 적격."
    sunset_justification: "N/A — ratchet 강화 방향 (Amendment id slot reservation schema codify)."
  - amendment_id: 5
    carrier_story: CFP-1110
    date: 2026-05-20
    summary: "§결정 1 layer 1 (Orchestrator scope) sub-scope (1-C) 신설 — Orchestrator-authored lane PL spawn prompt user-utterance verbatim anchor. lane traversal fidelity loss 차단 — Orchestrator 가 lane PL agent 를 spawn 할 때 spawn prompt 첫 줄에 사용자 발화 원문 verbatim block 의무 부착 (재합성 / 요약 / paraphrase 금지). 사용자 직권 minimal path 첫 적용 (codeforge process 가 fidelity loss source 라는 평가 결과 정합 — Researcher 35% 정당화 / Codex ROI indeterminate-부정쪽 confidence medium 수렴, 2026-05-20 KST). pattern corpus 누적: synthesizer-stale-reference 6 (CFP-722/801/792/810/819/825) + Researcher 12 occurrence 정정 (CFP-698) + scope 재확대 금지 invariant 6+ 위치 (CFP-758) + unverified-self-write-claim super-class 5 — ADR-045 §D-9 pattern_count ≥ threshold 2 escalation 정합. Wave 1 = behavioral mandate (lane PL spawn prompt 첫 줄 anchor block 의무) — Wave 2 mechanical lint = 별 CFP carrier (deferred-followup). minimal path 정합: Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 (사용자 승인 2026-05-20 KST) — closed-loop break 외부 결정 채널."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A lane spawn cross-repo state / 1-B Issue body authorship) → (1-C) lane PL spawn prompt user-utterance verbatim 확장, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy). 사용자 직권 minimal path = closed-loop break 외부 결정 채널, ratchet 강화 self-application 정직 명시 — 본 Amendment 자체가 monotonic-increasing governance 의 부분 (verify-before-trust 영역 안 — Researcher 평가 net positive 35% 영역 직접 확장)."
  - amendment_id: 6
    carrier_story: CFP-1198
    date: 2026-05-22
    summary: "§결정 2 scope (b) 확장 — ADR/contract amendment 번호 인용 시 대상 파일 frontmatter amendments: 목록 Read-verify 후 max+1 사용 의무 (amendment-number-frontmatter-verify). plan-time citation staleness 차단 forcing function. scope: 거버넌스 artifact (β-issue body / spec / change-plan / PR body / ADR amendment) 안 amendment 번호 인용 전 target ADR frontmatter Read 의무. 2 occurrence pattern_count (CFP-1177 ADR-027 Amendment 7 → 실제 Amendment 9 / CFP-1179 ADR-063 Amendment 6/7 → 실제 Amendment 8) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation 산물. ADR-073 cross-ref (β-issue = Orchestrator-authored scope — Orchestrator 행위 한정 verify-before-assert layer 동반 적용). mechanical_enforcement_actions[] 신규 entry amendment-number-frontmatter-verify deferred-followup declare (Wave 2 lint script + workflow + bats = 별 CFP-1198 Phase 2 sub-carrier)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 2 scope (b) 의 verify 대상 확장 — ADR frontmatter value 인용 시 write-time verify 범위에 amendment 번호 citation 추가, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 7
    carrier_story: CFP-1312
    date: 2026-05-23
    summary: "§결정 9 verify-before-cite 의무 scope 양방향 확장 — Wave 1 (Amendment 6) `M = max+1` (forward 정합) only → Wave 2 (본 Amendment 7) `M = max+1` ∧ `M > max` 미만 stale 인용 차단 (backward + forward 양방향). recurrence evidence: CFP-1293 stale citation `ADR-083 Amendment 2` (실제 max=2 인 시점 — 정확 next slot = 3, 즉 `M ≤ max` backward-staleness) 가 ADR-082 Amendment 6 Wave 1 behavioral mandate land 후 발생 → Wave 1 behavioral 단독 차단 불충분 evidence 아닌 CFP-1216 Phase 2 mechanical lint Check (b) `M > max+1` forward-only coverage gap 으로 escape. CFP-1216 lint Check (b) 본 Amendment 7 = backward-staleness 추가 catch wire (CFP-1216 SSOT extend, naming dedup ADR-068 I-4). pattern_count 3 reach (CFP-1177 + CFP-1179 + CFP-1293) ADR-045 §D-9 Mandatory escalation 산물 — forcing function 강화 carrier (axis 중복 신설 영역 아님: §결정 9 wording scope 확장 + Wave 2 lint coverage gap 보강 dual-carrier). mechanical_enforcement_actions[] `amendment-number-frontmatter-verify` entry summary 갱신 (status warning retain, scope expand)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 9 verify-before-cite scope (forward only) → (forward + backward) 양방향 확장. forbid scope 확장 (M = max+1 정확 next-slot 외 모두 stale). lint coverage gap 보강 = mechanical enforcement scope 확장, 약화 0건. ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 8
    carrier_story: CFP-1329
    date: 2026-05-24
    summary: "§결정 10 신설 (ArchitectAgent write-time discipline 4 sub-scope) — Codex TP#2 inline FIX 8-anchor mirror coverage checklist (§결정 10.A) + mid-author partial revert propagation gap (§결정 10.B sentinel codify rationale) + ArchitectAgent self-introduced script-behavior claim verify (§결정 10.C pattern_count 2 reach) + META self-application pattern (§결정 10.D pattern_count 2 reach). 4 memory entry normative 승격 carrier (memory `feedback_codex_tp2_verify_before_trust_pattern` / `feedback_mid_author_partial_revert_propagation_gap` / `feedback_architect_script_behavior_claim_verify` / `feedback_meta_self_application_pattern`). ADR-082 §결정 1 layer 1 + §결정 2 scope (a-d) write-time verify mandate sub-domain expansion — verify-before-trust super-class 안 ArchitectAgent chief author write-time discipline 영역 codify. ADR-039 lane self-write boundary 정합 (lane plugin agent md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제). doc-only fast-path (ADR-054)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 §결정 1 layer 1 + §결정 2 scope (a-d) write-time verify mandate 가 ArchitectAgent chief author write-time discipline 4 sub-scope 영역으로 확장, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy). pattern_count evidence: §결정 10.A=1 (CFP-795 sentinel codify rationale, dogfood inversion P1 prevention 도구적 가치) / §결정 10.B=1 (CFP-1009 sentinel) / §결정 10.C=2 (CFP-1006 F-DR-1006-1 + CFP-1025 hypothesis refuted) / §결정 10.D=2 (CFP-1016 1st applied + CFP-1340 Amendment 2 §결정 15 Story file initial scaffold = 2nd applied case). ≥ 2 reach (10.C+10.D) + sentinel forward-prevention (10.A+10.B) 혼합 ratchet — ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합."
  - amendment_id: 9
    carrier_story: CFP-1330
    date: 2026-05-24
    summary: "§결정 11 신설 — Code-level write-time semantic truth verify expansion: §결정 11.A (test code production binding verify, sed-extract real fn, sentinel forward-prevention CFP-1025 F-CR-1025-2) + §결정 11.B (script error visibility audit, 2>/dev/null mis-diagnosis amplifier META-ROOT, sentinel forward-prevention CFP-1025 bootstrap-labels.sh:53-55). 2 memory entry normative 승격 carrier (memory `feedback_test_must_bind_to_production` / `feedback_error_mask_metaroot`). ADR-082 super-class write-time semantic truth verify scope expansion — Amendment 8 ArchitectAgent write-time discipline + 본 Amendment 9 Code-level (test + script) write-time discipline. ADR-039 lane self-write boundary 정합 (CodeReviewAgent.md / QADeveloperAgent.md lane plugin cross-ref = follow-up defer)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 write-time verify scope 가 Architect write-time (Amendment 8 §결정 10) + Code-level write-time (본 Amendment 9 §결정 11) layer 양 layer expansion, forbid scope 축소 아님). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 11.A=1 (CFP-1025 F-CR-1025-2 sentinel forward-prevention) / §결정 11.B=1 (CFP-1025 META-ROOT sentinel forward-prevention, CFP-1006 mis-diagnosis lineage verified)."
  - amendment_id: 10
    carrier_story: CFP-1332
    date: 2026-05-24
    summary: "§결정 12 신설 — RequirementsPL + retro-time verify-before-trust expansion: §결정 12.A (Orchestrator-authored Issue body §2.1 verified state table mandate strengthening — pattern_count 2 reach CFP-1000 INVERSE drift + CFP-1001 lint output FP) + §결정 12.B (Retro-time wave_defer empirical verify — pattern_count 2 reach CFP-1006 Wave-defer rationale falsified post-merge + CFP-1025 corrective closure pattern WORKING). 2 memory entry normative 승격 carrier (memory `feedback_issue_body_verify_before_trust` / `feedback_wave_defer_empirical_verify`). ADR-082 super-class scope expansion = Amendment 2 (Issue-body authorship verify §결정 1 layer 1) RequirementsPL §2.1 codify strengthening + retro-time verify-before-trust axis 추가 (write-time + retro-time disjoint verify layer)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 write-time verify scope 가 write-time (Amendment 1-9) + retro-time empirical verify (본 Amendment 10 §결정 12.B) 양 lifecycle expansion, forbid scope 축소 아님). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 12.A=2 (CFP-1000 INVERSE drift + CFP-1001 lint output FP) / §결정 12.B=2 (CFP-1006 Wave-defer rationale falsified + CFP-1025 corrective closure pattern WORKING evidence)."
  - amendment_id: 11
    carrier_story: CFP-1338
    date: 2026-05-24
    summary: "§결정 13 신설 — GitOps verify-before-trust discipline 3 sub-scope A/B/C (main_drift_bypass HIGH pattern_count 5 + HEAD SHA pin step 0 sentinel + branch protection worktree cleanup discipline). 3 memory entry normative 승격 carrier (memory feedback_main_drift_bypass_audit_pattern / feedback_verify_pin_head_sha / feedback_branch_protection_worktree_cleanup). ADR-082 GitOps coordination layer expansion."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향, ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 정합)."
  - amendment_id: 12
    carrier_story: CFP-1339
    date: 2026-05-24
    summary: "§결정 14 신설 — PMOAgent retro batch closure pattern (carrier: memory `feedback_cfp_retro_batch_closure_pattern` pattern_count 2 reach with CFP-963 retro 4-batch + CFP-1340/1329/1330/1332/1338 본 5-batch 2nd applied case). Multi-CFP retro emission → batch-create simultaneously + sequential doc-only fast-path execution single session pattern codify. 1 memory entry normative 승격 carrier — workflow pattern reusability evidence ~6h cumulative for 4 consecutive Stories (CFP-963 precedent) → ~10h for 5 consecutive Stories (본 batch CFP-1340/1329/1330/1332/1338 + 본 CFP-1339)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 super-class scope expansion to retro-emission batch closure workflow layer, forbid scope 축소 아님). pattern_count evidence: §결정 14=2 reach (CFP-963 retro 4-batch + CFP-1340/1329/1330/1332/1338 본 5-batch 2nd applied case). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합."
  - amendment_id: 13
    carrier_story: CFP-1390
    date: 2026-05-24
    summary: "§결정 10.D META self-application pattern Wave 2 mechanical wire declarative anchor (CFP-1346 retro F2-FU Optional follow-up carrier). pattern_count cumulative 5 reach: CFP-1016 1st applied / CFP-1340 §결정 15 2nd applied / CFP-1329 Amendment 8 3rd applied (META self-applied by codifying itself) / CFP-1346 ADR-108 §결정 6 4th applied (description '74번째' claim = raw post-append count 74 PARITY) / 본 Amendment 13 5th applied (META self-applied — 본 Amendment 가 §결정 10.D pattern 의 declarative ratchet 강화 carrier). Wave 2 actual mechanical wire (detection logic for Story-self codification 1st applied case) = 별 sub-CFP carrier deferred-followup. `mechanical_enforcement_actions: [meta-self-application-wire]` 신설 placeholder declarative-only (실 wire = Wave 2). 본 Issue = declaration-only anchor + amendment_log entry 갱신 only — actual lint script + workflow + bats fixture wire = 별 sub-CFP."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 §결정 10.D META self-application pattern normative codify의 mechanical wire declarative placeholder Wave 1, forbid scope 축소 아님). pattern_count evidence: 5 reach (CFP-1016+1340+1329+1346+1390 sequential applied). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 14
    carrier_story: CFP-1336
    date: 2026-05-24
    summary: "§결정 1 layer 1 sub-scope (1-D) 신설 — cross-repo label-write authority verify mandate. Orchestrator (또는 GitOpsAgent) 가 cross-repo label state 변경 직전 authority 검증 의무: (a) wrapper Story Issue label 변경 → impl repo PR label sync write 권한 (CODEFORGE_CROSS_REPO_PAT scope `issues:write` 정합 ADR-066 §결정 2 Amendment 4 cross-ref) (b) impl repo PR label 변경 → wrapper Story Issue label sync write 권한 (sender.type ≠ Bot OR actor-allowlist 정합) (c) cross-org sync 차단 (mclayer org only) (d) verified-via annotation 의무 (모든 cross-repo label state 인용 옆 [verified-via: <gh api / direct read> pinned_at: <SHA/timestamp>] tag). 본 sub-scope 1-D = sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) 와 disjoint axis (label-write authority verify axis). ADR-073 Amendment 10 §결정 1 transition trigger `label_change` 와 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `cross-repo-label-sync` warning-tier deferred-followup). Wave 2 mechanical wire = 별 sub-carrier. **Amendment slot history (verify-before-cite META-self-application)**: spawn prompt Amd 8 → 10 → 12 → 13 → 14 → 14 FINAL (5 collisions, pattern_count 11+ reach CFP-1336 lineage). ADR-073 paired Amendment 슬롯 도 9 → 10 renumber (CFP-1384 mid-session collision, 6th collision)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C) → (1-D cross-repo label-write authority) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. META-self-applied (§결정 10.D 9th applied case)."
  - amendment_id: 15
    carrier_story: CFP-1437
    date: 2026-05-24
    summary: "§결정 1 layer 1 sub-scope (1-E) 신설 — spawn prompt SHA-anchor write-time verify mandate. Orchestrator (또는 PL agent / chief author) 가 lane PL / chief author / deputy / 4-tuple sub-tuple subagent spawn prompt 작성 시 4 의무: (a) spawn prompt 첫 줄 `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 형식 명시 (literal block, regex `^\\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{40}\\]$`) (b) SHA 값이 작성 시점 `git rev-parse origin/main` 결과와 일치 verify (cached SHA 사용 금지) (c) parent → child cascade spawn 시 SHA 재pin 의무 (parent SHA verbatim carry 금지, mid-flight merge 가능성으로 fresh re-fetch 의무) (d) verified-via annotation `pre_spawn_pin_verified: <bool>` field spawn prompt 안 명시 (write-time semantic truth verify). 본 sub-scope 1-E = sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) 와 disjoint axis (spawn-time SHA-anchor write-time verify axis). ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent 답습 (spawn-time anchor block pattern, block 형식 verbatim 답습). ADR-073 Amendment 11 §결정 1 transition trigger `spawn_prompt_emit` 와 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-head-pin-presence` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier. 동인 = CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence preventive solution carrier — chief author / deputy stale-at-planning 차단 forcing function. CFP-1336 single Story 안 4 reach (Amd 8 → 10 → 12 → 13 → 14, 5 collisions) + cross-Story 누적 (CFP-1293 + CFP-1303 + CFP-1318 + CFP-1336-iter1~iter4 + CFP-1390) ≥ ADR-045 §D-9 Mandatory threshold. paired sibling ADR-073 Amendment 11 = 2 ADR Amendment 동시 발의 (axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합). 본 Amendment 15 자체가 META-self-applied (§결정 10.D 10th applied case): 본 Amendment 번호(15) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main 67a541aa6999d91fed0314589c7cbd83bded7d37 max=14 — CFP-1336 Amd 14 merge 후 base, 정확 next-slot = 15) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-24 KST 기준 origin/main 67a541aa pinned_at: 67a541aa)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D) → (1-E spawn prompt SHA-anchor write-time verify) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. META-self-applied (§결정 10.D 10th applied case)."
  - amendment_id: 16
    carrier_story: CFP-1436
    date: 2026-05-24
    summary: "§결정 1 layer 1 sub-scope (1-F) 신설 — spawn-internal periodic origin re-pin protocol. Sub-CFP B of CFP-1389 (paired sibling of Sub-CFP A CFP-1437) — preventive (Sub-CFP A pre-spawn pin) + reactive (Sub-CFP B mid-spawn drift detection) 2-layer defense forcing function 완결. chief author / deputy / 4-tuple sub-tuple subagent 가 작업 중간 (spawn-internal time, 예: 매 N file edit 또는 매 Edit/Write tool 호출 후) 4 의무: (a) periodic check trigger 의무 (매 N file edit 또는 매 Edit/Write tool 호출 후 / timer-based 일정 interval, Wave 1 = subagent 자체 판단 / Wave 2 mechanical hook) — `git fetch origin main --quiet` + `git rev-parse origin/main` 실행 (b) PRE-SPAWN-ORIGIN-MAIN-SHA block 값과 current origin/main SHA 비교 (drift comparison) (c) drift threshold (≥ N commits behind, default N=1 즉 any merge) 초과 시 subagent RETURN early with `drift_detected: true` flag + payload (`pre_spawn_sha`, `current_origin_main_sha`, `commits_drift`, `drift_detected_at_step`) (d) verified-via annotation — RETURN payload 안 `mid_spawn_drift_verified: <bool>` field 의무 (write-time semantic truth verify, RETURN flag 정합성). 본 sub-scope 1-F = sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) / 1-E (spawn prompt SHA-anchor pre-spawn pin) 와 disjoint axis (mid-spawn time periodic drift detection + return early authority axis). 본 Amendment 16 = mid-spawn-time layer (reactive complement to Sub-CFP A pre-spawn-time layer) — Amendment 15 (1-E pre-spawn pin) + Amendment 16 (1-F mid-spawn re-pin) = paired complementary defense. ADR-073 Amendment 12 §결정 1 transition trigger `mid_spawn_origin_drift_detected` 와 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `mid-spawn-drift-detection` warning-tier deferred-followup). Wave 2 mechanical wire (subagent runtime hook + lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier. 동인 = Sub-CFP A 단독으로 catch 못 하는 mid-flight drift 영역 reactive layer 신설 — CFP-1336 9+ collisions evidence 공유 (preventive + reactive 2-layer defense 결정). paired sibling ADR-073 Amendment 12 = 2 ADR Amendment 동시 발의 (axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합). 본 Amendment 16 자체가 META-self-applied (§결정 10.D 11th applied case): 본 Amendment 번호(16) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main a1316f67d920dcc28fe40dec7cb69547ab60e025 max=15 — CFP-1437 Amd 15 merge 후 base, 정확 next-slot = 16) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-24 KST 기준 origin/main a1316f67 pinned_at: a1316f67)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E) → (1-F spawn-internal periodic origin re-pin protocol) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. META-self-applied (§결정 10.D 11th applied case)."
  - amendment_id: 17
    carrier_story: CFP-1435
    date: 2026-05-24
    summary: "§결정 1 layer 1 sub-scope (1-G) 신설 — amendment-slot pre-reservation strict claim mandate. Sub-CFP C of CFP-1389 (paired sibling of Sub-CFP A CFP-1437 preventive + Sub-CFP B CFP-1436 reactive, 3-layer defense forcing function 완결). ADR-RESERVATION `amendments_reserved[]` sub-tree (CFP-1058 Amendment 4 codify) 가 reactive — agent commit time 점유 후 row append (race-winner-takes-it convention). Sub-CFP C = strict claim BEFORE chief author write — chief author / deputy spawn 시점에 amendments_reserved[] row 의무 pre-append + spawn prompt 안 `pre_reserved_amendment_slots: [{adr: ADR-NNN, amendment_id: M}]` field 의무. 4-tuple primitive: (a) pre-reservation row pre-append 의무 (chief author / deputy spawn 전 ADR-RESERVATION amendments_reserved[] row append + commit) (b) spawn prompt block 안 pre_reserved_amendment_slots field 의무 (planned amendment_id list 전달 — chief author 가 spawn 시점에 reservation row 와 cross-verify) (c) reservation row ↔ actual write cross-verify (chief author 가 ADR Amendment write 직전 ADR-RESERVATION row 존재 + own carrier_story 매핑 확인) (d) verified-via annotation (`pre_reservation_verified: <bool>` field spawn prompt 안 명시). 본 sub-scope 1-G = sub-scope 1-A / 1-B / 1-C / 1-D / 1-E / 1-F 와 disjoint axis (amendment slot reservation lifecycle pre-claim axis — slot reservation lifecycle 의 pre-write phase vs runtime verify phase). Sub-CFP A (1-E pre-spawn SHA pin) + Sub-CFP B (1-F mid-spawn drift detection) + Sub-CFP C (1-G amendment slot pre-reservation) = 3-layer defense forcing function 완결 (preventive SHA + reactive drift + preventive slot). ADR-050 (parallel epic conflict coordination) §결정 1 ADR-RESERVATION carrier 의 fine-grained amendment slot extension — ADR number reservation (ADR-050 §결정 1) 와 amendment slot reservation (CFP-1058 Amendment 4 + 본 Amendment 17) 가 동일 race coordination 패턴. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `amendment-slot-reservation-check` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + ADR-RESERVATION schema strict validation + concurrent reservation conflict detection + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier. 동인 = CFP-1336 9+ collisions evidence 의 preventive complement — Sub-CFP A SHA pin 단독으로는 amendment_id race 직접 차단 불가 (spawn-time SHA fresh fetch 후에도 multi-session concurrent spawn 시 race 가능), slot reservation lifecycle pre-claim 으로 race 직접 차단. ADR-RESERVATION schema enhancement = frontmatter `schema_version` field 신설 (1.0 → 1.1) + `amendments_reserved[]` row required fields documentation (adr_number / amendment_id / reserved_by_cfp / reservation_date / status: reserved|active|abandoned). 본 Amendment 17 자체가 META-self-applied (§결정 10.D 12th applied case): 본 Amendment 번호(17) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main b32a731a5e858224afce72b0e6fc86ce86ee1483 max=16 — CFP-1436 Amd 16 merge 후 base, 정확 next-slot = 17) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-24 KST 기준 origin/main b32a731a pinned_at: b32a731a)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F) → (1-G amendment-slot pre-reservation strict claim) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. META-self-applied (§결정 10.D 12th applied case)."
  - amendment_id: 18
    carrier_story: CFP-1342
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-H) 신설 — Orchestrator self-write §10 FIX Ledger row resolution field claim source/evidence verify mandate. §10 FIX Ledger = Orchestrator monopoly (fix-event-v1 contract, CFP-32) — 기존 sub-scope 1-A~1-G 7종 외 codify gap closure. 4 의무: (a) resolution field 작성 시 인용 source/evidence ('wrap 실행 완료' / 'lint EXIT_CODE=0' / 'grep count N') 가 실 실행 결과인지 write-time verify / (b) measurable evidence (file path + grep count + exit code + diff hash) verify-via direct execution (cached/inferred 금지) / (c) `verified-via:` annotation / (d) wrap-style 자동화 영역 실 stdout/exit code/grep diff 확인 후 작성. axis disjoint vs 1-A~1-G (Orchestrator monopoly §10 FIX Ledger resolution field write-time semantic truth verify). 동인 = CFP-1316 retro F2 Optional carrier (iter 1 'CHANGELOG.md 45 occurrence wrap' claim Orchestrator self-write monopoly codify gap). Wave 1 declaration-only (`mechanical_enforcement_actions: fix-ledger-resolution-source-verify` warning-tier). Wave 2 별 CFP. minimal-applicability: §10 FIX Ledger = Orchestrator only (CFP-32, lane/PL/chief 영역 0). META-self-applied §결정 10.D 13th + Amd 17 1-G 1st (verified-via origin/main `11bf2d95` max=17 → next=18). doc-only fast-path."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G) → (1-H Orchestrator §10 FIX Ledger resolution field claim source/evidence verify) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. META-self-applied (§결정 10.D 13th applied case + Amendment 17 sub-scope 1-G pre-reservation strict claim mandate 1st applied case)."
  - amendment_id: 21
    carrier_story: CFP-1578
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-J) 신설 — cross-repo worktree target authority verify mandate. paired sibling CFP-1559 Amd 20 (Issue body stale claim pre-screen, axis disjoint). worktree mis-target 첫 catch (CFP-1539+1540 batch retro §4.1 #2). 4-tuple primitive: (a) `git -C <worktree> remote -v` expected repo (wrapper ↔ internal-docs) vs actual 일치 verify / (b) spawn prompt `worktree_target_repo: <repo>` field / (c) cross-repo 작업 시 명시적 worktree switch (wrapper worktree 안 internal-docs PR 금지, ADR-040) / (d) `worktree_target_authority_verified: <bool>`. axis disjoint vs 1-A~1-I (cross-repo write-target boundary, 1-D label-write authority 와 가장 인접하나 disjoint). RequirementsPL Alternative C (ADR-082 sub-scope, not new ADR). Wave 1 declaration-only (`mechanical_enforcement_actions: worktree-target-authority-verify` warning-tier). Wave 2 별 sub-CFP. META-self-applied §결정 10.D 16th + Amd 17 1-G 2nd (verified-via worktree HEAD `4000440` max=19 + CFP-1559 Amd 20 pre-claim → next=21)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I) → (1-J cross-repo worktree target authority verify) 확장). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. META-self-applied (§결정 10.D 16th applied case)."
  - amendment_id: 19
    carrier_story: CFP-FU-A
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-I) 신설 — pre-spawn-prompt-finalize verify layer mandate (race window ~30-60s 단축 carrier). 동인 = parallel session race 11th occurrence (CFP-1420) pattern_count 11 ≫ §D-9 threshold 2 + 12th meta-occurrence (CFP-1342 collision recovery 18→19, 1-H→1-I). paired sibling ADR-073 Amd 13 (polling cadence) + Amd 14 (OR→AND composition) = 3 ADR Amendment 동시 발의 axis disjoint 3-set. 4-tuple primitive: (a) worktree create ~ prompt emit window 1회 polling / (b) `git fetch origin main` + `gh issue list --search` + `gh pr list --search head:<branch>` 3-source AND / (c) race window 단축 mandate / (d) `pre_spawn_prompt_finalize_verified: <bool>` annotation. 4-layer temporal defense complete (pre-spawn-fetch Amd 15 + pre-spawn-prompt-finalize 본 + mid-spawn-periodic Amd 16 + Orchestrator §10 Amd 18). Wave 1 declaration-only — Wave 2 mechanical wire 별 sub-CFP. META-self-applied §결정 10.D 14th + collision recovery 1st (verified-via origin/main `ca1c20e` max=18 → next=19 post-CFP-1342)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H) → (1-I pre-spawn-prompt-finalize verify layer) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. parallel session race 11th occurrence escalate_user pattern_count 11 ≫ threshold 2 Mandatory ADR-045 §D-9 산물 + 12th meta-occurrence (CFP-1342 collision recovery in-flight). META-self-applied (§결정 10.D 14th applied case + collision recovery 1st applied case)."
  - amendment_id: 20
    carrier_story: CFP-1559
    date: 2026-05-25
    summary: "§결정 15 신설 — Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate. 4 sub-pattern closed-set: (a) PR #NNNN merge state stale / (b) CFP-NNNN MERGED/CLOSED state stale / (c) count number stale ('X VIOLATIONs' / 'pattern_count Z') / (d) sister carrier origin claim stale ('CFP-NNNN carrier'). super-class scope (Issue body content broader stale-reference). CFP-1216 `amendment-number-frontmatter-verify` lint (sub-class) extension. paired sibling CFP-1558 (amendment-number sub-class). pattern_count 7+ reach Mandatory (CFP-FU-B #1477 5-defect 3 PIVOT 60% stale rate + CFP-1041/1050 spawn packet 4 evidence). axis disjoint with CFP-1437/1436/1497 3-layer (Issue body authored 시점 ↔ spawn lifecycle). Wave 1 declaration-only (`mechanical_enforcement_actions: issue-body-claim-pre-screen` warning-tier). Wave 2 별 sub-CFP. META-self-applied §결정 10.D 15th + Amd 17 1-G 2nd (verified-via origin/main HEAD `4000440` amendments[] max=19 → next=20 post-CFP-FU-A)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 super-class scope (Issue body authorship verify Amendment 2 §결정 1 layer 1 sub-scope 1-A) → Issue body content broader stale-claim super-class (4 sub-pattern enumeration: PR merge state / CFP merge state / count number / sister carrier origin) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 15 = 7 reach (CFP-FU-B 3 PIVOT + CFP-1041/1050 lineage 4). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 15th applied case + Amendment 17 §결정 1-G strict claim mandate 2nd applied case after CFP-1492)."
  - amendment_id: 22
    carrier_story: CFP-1601
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-K) 신설 — numeric claim write-time strict claim mandate (ArchitectAgent / Orchestrator spawn packet / lane PL write-time numeric claim source/value 4-step verify). 6 dimension closed-set: line/file/API/pattern/commit/row count. 동인 = pattern_count 2 (CFP-1571 §3.2 line drift '+93→+101' + CFP-1581 §3.2 file drift '10→14'). 4-step: (a) source command identify (`grep -c` / `wc -l` / `git diff --shortstat` / `find | wc -l`) / (b) direct execute actual value (cached/stale 금지) / (c) claim↔actual cross-verify (semantic ambiguity 시 source command 정밀화) / (d) write only on match. axis disjoint vs 1-G (reservation lifecycle) + 1-J (worktree target authority). Wave 1 declaration-only (`mechanical_enforcement_actions: numeric-claim-write-time-verify` warning-tier). Wave 2 별 sub-CFP. META-self-applied §결정 10.D 17th + numeric-claim 1st + Amd 17 1-G 3rd (verified-via worktree HEAD `0a19e6a` amendments[] max=21 → next=22, `grep -c` actual=41 vs semantic max=21 divergence recursive dogfooding)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J) → (1-K numeric claim write-time strict claim mandate) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 layer 1 sub-scope 1-K = 2 reach (CFP-1571 §3.2 line count drift +93→+101 3 location 정정 + CFP-1581 §3.2 file count drift 10→14 actual = pattern_count 2 ≥ ADR-045 §D-9 threshold 2 Mandatory escalation 산물). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 17th applied case + numeric-claim verify-before-write 1st applied case META first applied: spawn packet 자체 안 numeric claim source command result divergence 직접 catch — recursive dogfooding self-evidence)."
  - amendment_id: 23
    carrier_story: CFP-1590
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-L) 신설 — spawn prompt fact verify-before-trust mandate (upstream-inherited stale fact carrier super-class). axis disjoint vs 1-A~1-K (1-C 사용자 발화 content 전달 형식 verbatim ↔ 1-L upstream-inherited fact truthfulness verify / 1-K own author numeric strict ↔ 1-L upstream source state/sister/count/wording fact). 4-tuple primitive: (a) upstream-inherited fact 식별 4 sub-source (사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) / (b) direct source verify `verified-via:` annotation 의무 (cached/synthesized 금지) / (c) stale 검출 시 `[fact-correction: <claim> stale, verified <correct>, source: <src>]` marker / (d) `spawn_prompt_fact_verified: <bool>` annotation. 4-layer temporal defense (Amd 15+16+18+19) 의 content fact axis 5th layer (when verify ↔ what verify disjoint). 동인 = pattern_count 3 reach (CFP-1493 commit msg defer 사유 / CFP-1523 사용자 prompt 4 fact / CFP-1591 Issue body canonical/sibling 역할 반전). ArchitectAgent Option B super-class scope expansion + mid-flight CFP-1601 collision recovery (Amd 22+1-K → renumber 23+1-L). Wave 1 declaration-only (`mechanical_enforcement_actions: spawn-prompt-fact-verify` warning-tier). Wave 2 mechanical wire = 별 sub-CFP. META-self-applied §결정 10.D 18th + Amd 17 1-G 4th (verified-via origin/main `4c668913` amendments[] max=22 → next=23 post-CFP-1601 collision recovery)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K) → (1-L spawn prompt fact verify-before-trust mandate upstream-inherited stale fact super-class) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 sub-scope 1-L = 3 reach (CFP-1493 PR #1520 commit message defer 사유 / CFP-1523 사용자 spawn prompt 4 fact / CFP-1591 Issue body canonical/sibling 역할 반전) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation 산물. is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 18th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 4th applied case + mid-flight collision recovery 2nd applied case after CFP-FU-A Amd 19)."
  - amendment_id: 24
    carrier_story: CFP-1589
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-M) 신설 — own-author synthesis 보고 vs actual git commit gap verify mandate (F-DR-003 carrier). axis disjoint vs 1-L upstream-inherited (input verify) ↔ 본 1-M = own-author downstream output verify (synthesis output ↔ artifact gap). axis 분리 vs Amd 18 1-H (Orchestrator §10 FIX Ledger source) = ArchitectPL/Dev/lane PL synthesis own-write axis. 4-tuple primitive: (a) synthesis 보고 시점 `git -C <worktree> log --oneline origin/main..HEAD` direct execute actual commit verify (claim 'Artifacts written' = actual commit hash 매핑) / (b) review-verdict-v4 optional `artifact_commits[]` field future MINOR / (c) Story §14 Lane Evidence row append 시 actual commit verify (ADR-073 + ADR-082 dual binding) / (d) `synthesis_vs_commit_gap_verified: <bool>` annotation. 동인 = CFP-1523 F-DR-002 P0 finding (verdict 'Artifacts written' ≠ actual commit, DesignReviewPL git status detect, FIX iter 1 dispatch). Wave 1 declaration-only (`mechanical_enforcement_actions: synthesis-vs-commit-gap-check` warning-tier). Wave 2 별 sub-CFP. META-self-applied §결정 10.D 19th + Amd 17 1-G 5th (verified-via origin/main HEAD `f2e78b1` amendments[] max=23 → next=24). doc-only fast-path."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L) → (1-M own-author synthesis 보고 vs actual git commit gap verify) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 sub-scope 1-M = 1 reach (CFP-1523 carrier F-DR-002 P0 finding ArchitectPL verdict packet 'Artifacts written' ≠ actual git commit, DesignReviewPL audit detect FIX iter 1 dispatch) — deferred-followup carrier (Wave 1 declaration-only mandate, ADR-082 §결정 6 retain pattern 답습 — pattern_count 누적 시 follow-up CFP MUST promote to mechanical lint). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 19th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 5th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590)."
  - amendment_id: 25
    carrier_story: CFP-1612
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-N) 신설 — numeric claim write-time verify Wave 2 mechanical enforcement wire (1-K Amd 22 Wave 1→Wave 2). axis disjoint vs Amd 22 1-K = mandate 자체 (4-step + 6 dimension) ↔ 본 1-N = mechanical wire SSOT (script+workflow+bats binding). 4-tuple primitive: (a) lint script SSOT `scripts/lib/check_numeric_claim_write_time.py` ADR-061 + bash thin wrapper / (b) 6 dimension (line/file/API/pattern/commit/row count) Python dict SSOT regex+source command / (c) FP guard 4종 (code-span / quoted / templates/** / docs/stories/§9) + PER_BLOCK_SCAN_CAP=50 ReDoS / (d) workflow + `hotfix-bypass:numeric-claim-write-time-verify` + evidence-checks-registry warning-tier. Wave 1→Wave 2 split 11th instance. Wave 1 declarative SSOT (본 Phase 1) / Wave 2 actual script+workflow+bats Phase 2 별 sub-carrier. META-self-applied §결정 10.D 20th + Amd 22 1-K 1st (source command precision `grep -oE '^  - amendment_id: [0-9]+' | tail -1` actual=24 → next=25) + Amd 17 1-G 6th + mid-flight collision recovery 3rd (initial pin f2e78b16 max=23 → CFP-1589 merge 5b5c9f7b max=24 → renumber 24→25 + 1-M→1-N + ADR-082 §1-L spawn packet fact verify 1st recursive dogfooding). doc-only fast-path."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M) → (1-N numeric claim write-time verify Wave 2 mechanical enforcement wire — 1-K declaration-only → mechanical lint enforce) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 sub-scope 1-N = 2 reach (CFP-1571 §3.2 line count drift '+93→+101' 3 location 정정 + CFP-1581 §3.2 file count drift '10→14' actual, 1-K 와 동일 evidence base inherit — Wave 1 declarative → Wave 2 mechanical enforce 의 동일 root pattern). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 20th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 6th applied case + Amendment 22 §결정 1-K numeric claim verify-before-write 1st applied for Wave 2 wire carrier + Amendment 23 §결정 1-L spawn prompt fact verify-before-trust 1st applied case recursive dogfooding mid-flight collision recovery 3rd applied case after CFP-FU-A Amd 19 + CFP-1590 Amd 23)."
  - amendment_id: 26
    carrier_story: CFP-1637
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-O) 신설 — PR commit message + PR body numeric claim write-time strict claim mandate (PR-level artifact layer, 3rd axis disjoint vs 1-K governance docs + 1-N mechanical wire). 동인 = CFP-1612 retro Pattern 2 meta-self-application-accuracy-violation pattern_count 2 reach: (i) CFP-1601 §13.C '11' vs actual 15 (Story scope 1-K) + (ii) CFP-1612 PR #1631 commit msg '29/~470/~155' vs canonical '30/605/183' (PR scope 1-O NEW). same 6 dimension + 4-step verify-before-write inherit from 1-K. Wave 1 declaration-only — Wave 2 mechanical wire `scripts/lib/check_numeric_claim_write_time.py` scope 확장 to PR commit msg + PR body 별 sub-CFP (CFP-1647 = 13th instance Wave 1→Wave 2). META-self-applied §결정 10.D 21st + Amd 17 1-G 7th + Amd 22 1-K 2nd (verified-via origin/main HEAD `d1c629f0` amendments[] max=25 → next=26). doc-only fast-path."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M/1-N) → (1-O PR commit message + PR body 안 numeric claim write-time strict claim mandate, axis disjoint from 1-K write-time governance docs scope + 1-N Wave 2 mechanical wire scope; 본 1-O = PR commit msg + PR body 3rd axis declaration-only Wave 1) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 sub-scope 1-O = 2 reach (CFP-1601 §13.C row 3 Story scope claim '11' vs actual 15 + CFP-1612 PR #1631 commit message + PR body claim '29 / ~470 / ~155' vs canonical actual '30 / 605 / 183' — meta-self-application-accuracy-violation pattern_count 2 reach ≥ ADR-045 §D-9 threshold 2 Mandatory escalation 산물). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 21st applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 7th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590 + Amd 24 CFP-1589 + Amd 25 CFP-1612 + 본 carrier + Amendment 22 §결정 1-K numeric claim verify-before-write 2nd applied case after Amd 25 first wave 2 wire carrier)."
  - amendment_id: 27
    carrier_story: CFP-1647
    date: 2026-05-26
    summary: "§결정 1 layer 1 sub-scope (1-P) 신설 — 1-O (Amd 26 CFP-1637) Wave 2 mechanical enforcement wire (PR-level artifact scope). axis disjoint vs 1-N Amd 25 = governance docs scope (ADR/Change Plan/Story/spawn packet/Issue body) ↔ 본 1-P = PR commit msg + PR body (git/GitHub layer, 1-O scope 확장). 4-quadrant matrix: (1-K Amd 22, 1-N Amd 25) governance docs pair + (1-O Amd 26, 1-P 본 Amd 27) PR-level artifact pair. 4-tuple primitive: (a) `scripts/lib/check_numeric_claim_write_time.py` Python SSOT (CFP-1612 wired) detection scope 확장 to PR commit msg + PR description + `gh pr view --json title,body,commits` ingestion + bash `--scope pr-commit-msg|pr-body|all` flag / (b) 6 dimension dict 재사용 (line/file/API/pattern/commit/row count) / (c) PR-level source ingestion 추가 + FP guard 4종 재사용 + PER_BLOCK_SCAN_CAP=50 / (d) workflow PR trigger 확장 + bypass label 재사용 (label-registry MINOR 0) + evidence-checks-registry target_section 갱신 (1-K+1-N+1-O+1-P). Wave 1→Wave 2 split 13th instance. Wave 1 declarative SSOT (본 Phase 1) / Wave 2 actual script+workflow+bats Phase 2 별 sub-carrier. META-self-applied §결정 10.D 22nd + Amd 17 1-G 8th + Amd 22 1-K 3rd + Amd 23 1-L 2nd + Amd 24 1-M 1st (verified-via origin/main HEAD `e1e2b751` source command `grep -oE '^  - amendment_id: [0-9]+' | tail -1` actual=26 → next=27)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M/1-N/1-O) → (1-P 1-O Wave 2 mechanical enforcement wire scope — declaration-only behavioral mandate 1-O 의 mechanical lint enforce, declaration → mechanical enforce promotion path) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 sub-scope 1-P = 2 reach (1-O 와 동일 evidence base inherit — CFP-1601 §13.C row 3 Story scope claim '11' vs actual 15 + CFP-1612 PR #1631 commit msg LOC drift '29 / ~470 / ~155' vs '30 / 605 / 183', meta-self-application-accuracy-violation pattern_count 2 reach Mandatory ≥ ADR-045 §D-9 threshold 2). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 22nd applied case + Amendment 17 §결정 1-G 8th applied case + Amendment 22 §결정 1-K 3rd applied case for Wave 2 wire carrier + Amendment 23 §결정 1-L 2nd applied case for spawn packet fact verify + Amendment 24 §결정 1-M 1st applied case for inline self-verify recursive dogfooding)."
  - amendment_id: 28
    carrier_story: CFP-1648
    date: 2026-05-26
    summary: "§결정 1 layer 1 sub-scope (1-Q) 신설 — ADR dual-block parity 3-invariant forward-prevention lint (F-DR-001 P0 origin sentinel mechanical carrier). F-DR-001 P0 origin: Amendment N frontmatter amendment_log[] entry present but body ## Amendment N section missing (CFP-1637 retro발견 — Amendment 26 case). Combined Phase 1+2 (no Wave split). 3-invariant check: Block 1 (amendments[] ↔ body H2 parity) / Block 2 (amendment_log[] ↔ body H2 parity — F-DR-001 P0 sentinel) / Block 3 (amendments[] ↔ amendment_log[] cross-count parity). axis disjoint from 1-A through 1-P (dual-block ADR structural parity axis — not numeric claim / not cross-repo state / not spawn prompt / not ownership). Python SSOT `scripts/lib/check_adr_dual_block_parity.py` (ADR-061 thin wrapper convention, anchored simple regex CodeQL ReDoS guard, line-by-line parse, PER_LANE_EVIDENCE_SCAN_CAP=30, Windows cp949 reconfigure) + bash thin wrapper `scripts/check-adr-dual-block-parity.sh` + D2 dual trigger workflow `templates/github-workflows/adr-dual-block-parity.yml` + `.github/workflows/adr-dual-block-parity.yml` byte-identical mirror (ADR-005) + bats 8 TC RED→GREEN stash proof (CFP-1334 §8.4 5 markers) + evidence-checks-registry warning-tier initial registration + label-registry-v2 MINOR bump v2.77 → v2.78 (`hotfix-bypass:adr-dual-block-parity` 103번째 hotfix-bypass:* family member) + MANIFEST.yaml label_registry version 갱신. ADR-060 §결정 5 first introduction = warning mode (continue-on-error: true). META-self-applied (본 Amendment 자체가 F-DR-001 P0 sentinel forward-prevention 의 첫 META applied case — amendments[] entry + amendment_log[] entry + body ## Amendment 28 section 3-block parity 동시 write, 즉 F-DR-001 을 forward-prevent 하는 lint 가 자기 자신의 Amendment 에 META self-application 적용 = recursive dogfooding integrity verify)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/…/1-P) → (1-Q ADR dual-block parity 3-invariant forward-prevention lint) 신설, forbid scope 축소 0건). ADR-064 §결정 7 symmetric evidence-gated 정합. pattern_count evidence: F-DR-001 P0 origin = CFP-1637 retro sentinel (Amendment 26 amendment_log[] entry present but body section missing, 1-occurrence 기록 — retro §5 F-DR-001 escalation 산물). is_transitional: false 유지 (permanent governance policy). META-self-applied: 본 Amendment 28 자체가 amendments[] + amendment_log[] + body 3-block dual-write via forward-prevention lint being enforced on its own carrier ADR."
  - amendment_id: 29
    carrier_story: CFP-1683
    date: 2026-05-26
    summary: "§결정 1 layer 1 sub-scope (1-R) 신설 — mid-Story FIX-loop re-verification mandate. FIX iter ≥ 2 시점 reslot calculus 의무 (amendment_id slot + label-registry MINOR bump version + bypass family member raw count 3-tuple 재verify) + per-iter mid-spawn drift detection (ArchitectPL re-engage prompt 안 3 field presence: `amendment_slot_revalidated` / `registry_version_revalidated` / `bypass_count_revalidated`) + slot collision recheck (origin/main fetch + amendment_log[] / contract_version / hotfix-bypass:* grep count 재verify). axis disjoint from 1-G (CFP-1435 Amendment 17 strict pre-reservation claim — Story 시작 시점 only) — 본 1-R = FIX-loop intra-Story window 영역. CFP-1646 직접 evidence: 1st attempt FIX iter 1 → iter 2 → iter 3 spawn cycle 사이 amendment slot + version + bypass count 재verify 부재 → CFP-1657 Amd 16 slot collision + CFP-1648 v2.78 + 103번째 slot collision 발생 (ESCALATE_PACKET_INCOMPLETE outcome). Wave 1 declarative — Wave 2 mechanical wire (`scripts/lib/check_fix_loop_reverify.py` + bash thin wrapper + workflow body wire + bats RED→GREEN stash proof + boundary fixture pair) = 별 sub-CFP carrier."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/…/1-Q) → (1-R mid-Story FIX-loop re-verification) 신설). pattern_count evidence: `sister_session_race_in_design_lane` cumulative ≥ 5 (CFP-684 + CFP-698 + CFP-1041 + CFP-1591 + CFP-1646 3 sub-events) — ADR-045 §D-9 Mandatory escalation 산물. is_transitional: false 유지 (permanent governance policy)."
  - amendment_id: 30
    carrier_story: CFP-1688
    date: 2026-05-26
    summary: "§결정 1 layer 1 sub-scope (1-S) 신설 — ADR frontmatter block convention SSOT codify + sub-scope 1-Q (CFP-1648 dual-block parity lint) single-block ADR 면제 scope clarification. Two ADR frontmatter conventions 명문화: (1) single-block = `amendment_log[]` block only (no `amendments[]` block) — 일부 ADR 의 valid convention (예: ADR-045, amendment_log[] only + body `### Amendment N` H3 heading) / (2) dual-block = `amendments[]` + `amendment_log[]` 둘 다 (예: ADR-082 본 ADR, F-DR-001 mandate 정합). sub-scope 1-Q lint scope correction (3 fix, 동일 parser-correctness false-positive class): Fix A (single-block mode — amendments[] block 부재 시 Block 1 + Block 3 skip, Block 2 amendment_log[] ↔ body parity F-DR-001 P0 sentinel 만 적용) + Fix B (body section detection H2 `## Amendment N` AND H3 `### Amendment N` both-level, bounded `{2,3}` H4 차단) + Fix C (frontmatter scan cap — `_extract_frontmatter_lines` 의 `lines[:PER_LANE_EVIDENCE_SCAN_CAP*10]` 300-line slice 가 long-frontmatter ADR (ADR-082 자신 2nd `---` line 548) 의 amendment_log[] entry 22-29 절단 → slice cap 확대 (예: 5000) 으로 full frontmatter scan, `---` delimiter break 가 실 boundary retain, ReDoS 무관 correctness fix). 3 root cause (CFP-1680 retro CFP-FU-C #1688 + Orchestrator verify-before-trust ADR-073/ADR-082 direct extraction FIX iter 1): (1) ADR-045 single-block + H3 body → BODY_H2_AMENDMENT_PATTERN (H2 only) body_ids empty → 11 amendments AMENDMENT_LOG_FRONTMATTER_ONLY false-positive + (2) H3 미detect + (3) ADR-082 long-frontmatter 절단 → false CROSS_BLOCK_COUNT_MISMATCH 30 != 20 + false BODY_ONLY_NO_LOG Amendment 30 (amendment_log[] line 353 cap 너머). 모두 warning-tier non-blocking but PR check output pollution. lint scope correction = 신규 check 아닌 1-Q scope 정정 → 기존 `adr-dual-block-parity` evidence-checks-registry entry + `hotfix-bypass:adr-dual-block-parity` label 재사용 (신규 entry / 신규 label 0). Combined Phase 1+2 (ADR amendment Phase 1 + lint fix Phase 2 develop lane dispatch, CFP-1648 combined precedent 답습). axis disjoint from 1-A through 1-R (ADR structural-parity-lint scope correction axis — 1-Q sub-domain refinement, not a new verify subject). META-self-applied (§결정 10.D 13th applied case + Amendment 17 §결정 1-G strict pre-reservation 6th applied case): 본 Amendment 30 = ADR-082 dual-block convention 의 exemplar 이며, 1-S 가 clarify 하는 lint 가 본 ADR-082 자신의 dual-block structure (amendments[] + amendment_log[] + body ## Amendment 30) 위에서 false-positive 없이 PASS 해야 하는 recursive dogfooding (Fix C 가 enabler — Fix C 없이 lint 가 amendment_log[] line 353 see 못해 false-fail). verified-via: `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] max=29 (CFP-1683 Amendment 29 merge 후 base) → 정확 next-slot = 30, 2026-05-26 KST 기준 origin/main 506f7cfc (PRE-SPAWN-ORIGIN-MAIN-SHA verified, pre_spawn_pin_verified: true). ADR-RESERVATION row pre-append + commit dad73ec5 (pre_reservation_verified: true)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/…/1-R) → (1-S ADR frontmatter block convention SSOT + 1-Q single-block/H3/frontmatter-scan-cap 3-fix scope correction) 신설. 본 Amendment 는 lint scope correction (false-positive 차단) 이나 forbid scope 축소 아님 — Block 2 (F-DR-001 P0 sentinel) 검증 retain + single-block ADR 도 amendment_log[] ↔ body parity 계속 enforce + Fix C 적용 후 long-frontmatter ADR 의 genuine body-section drift (amendments 8-13/18-21 frontmatter-only) 가 정당 surface (FP 차단이 genuine warning 을 enable, 약화 아님). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합 — false-positive 정정 = accuracy 강화 (over-rate 차단 = ADR-081 §결정 D6 severity calibration 정합), guard 약화 0건. ADR-073/ADR-082 Orchestrator verify-before-trust 가 Fix C (bug #3) 를 FIX iter 1 에서 catch — same-class parser-correctness FP). pattern_count evidence: CFP-1680 retro (single-block + H3 11 amendments false-positive 직접 lint 실행 확인) + bug #3 frontmatter scan cap (ADR-082 self direct extraction, FIX iter 1 catch). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 13th applied case)."
  - amendment_id: 31
    carrier_story: CFP-1684
    date: 2026-05-26
    summary: "§결정 1 layer 1 sub-scope (1-T) 신설 — PMOAgent retro write-time verify-before-trust mandate (META recursive evidence carrier). retro file write 시 cited fact (commit SHA + label-registry version + bypass family count + cross-Story memory pattern_count) source direct verify 의무. axis disjoint from §결정 9 verify-at-write-time (CFP-1312 Amendment 7 — ArchitectAgent + Orchestrator scope) — 본 1-T = PMOAgent retro write scope. (slot 재배정: CFP-1688 가 Amendment 30 + sub-scope 1-S 점유 → 본 CFP-1684 = Amendment 31 + sub-scope 1-T 재배정, ADR-082 Amendment 29 §결정 1-R mid-Story FIX-loop re-verification mandate self-application — 4th parallel race CFP-1688 slot collision detect 후 reslot.) META self-application: CFP-1646 retro write-time PMOAgent 자체 `stale_fact_inheritance` 진입 (Story spec wrapper merge SHA claim `e84f0460` Phase 1 commit vs actual `00641695` merge commit + internal-docs `0b37a71` vs actual `33fff4cf`) — 본 retro 안 verified-via correction 의 root carrier. Wave 1 declarative — Wave 2 mechanical wire (`scripts/lib/check_retro_fact_verify.py` SHA pattern + version pattern presence-grep + verify trace presence) = 별 sub-CFP carrier."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/…/1-S) → (1-T PMOAgent retro write-time verify) 신설). pattern_count evidence: CFP-1646 retro write-time stale fact (2 commit SHA claim mismatch — wrapper + internal-docs) META recursive direct evidence. is_transitional: false 유지 (permanent governance policy). META self-application: 본 Amendment 31 자체가 PMOAgent retro write-time verify mandate carrier — ADR-082 Amendment 28 dual-block parity self-apply + Amendment 29 §결정 1-R mid-Story FIX-loop re-verification self-apply (CFP-1688 slot collision reslot)."
  - amendment_id: 32
    carrier_story: CFP-1734
    date: 2026-05-26
    summary: "§결정 1 layer 1 sub-scope (1-U) 신설 — sub-scope 1-Q (CFP-1648 dual-block parity lint) scope 를 dual-block-only ADR 로 narrow. **Amendment 30 sub-scope 1-S Fix A (single-block mode — amendment_log[]-only → Block 2 만 적용) supersede**: dual-block gate 신설 — `_check_adr_parity` top 에서 `amendments_ids` non-empty AND `amendment_log_ids` non-empty (= dual-block ADR, 예 ADR-082) 일 때만 Block 1/2/3 적용 (Fix B H2/H3 body detection + Fix C frontmatter scan cap RETAIN), 그 외 (single-block 양방향 = amendment_log[]-only 또는 amendments[]-only / no-amendments) 면제 → trivial PASS (Block 2 도 미적용 — Fix A single-block-Block-2 narrow to single-block-EXEMPT). 동인 = Orchestrator verify-before-trust 직접 ADR census: frontmatter amendments[]/amendment_log[] 보유 82 ADR 중 lint body detection (`## Amendment N` / `### Amendment N` H2/H3, post-1688) 이 검출하는 convention 은 39개뿐, 35개는 THIRD convention `## §결정 N. <title> (Amendment M, CFP-XXX)` (§결정 heading 안 parens-안 amendment 번호, 예 ADR-071 `## §결정 12. ... (Amendment 1, CFP-777)`) 미검출 — 이들이 lint 가 못 보는 valid convention. dual-block-only narrow 가 1-Q 의 original F-DR-001 intent (dual-block ADR-082 consistency) 와 정합하며 convention-mismatch false-positive 를 깨끗이 제거. 효과: #1734 amendments[]-only ADR (parens-convention ADR-071 포함) 면제 → FP 0 / #1735 narrow to dual-block-only ADR (ADR-082 = 유일 genuine drift dual-block ADR, amendments 8-13/18/20-21 body 부재 + amendment_log[] entry 13 부재) — 'ADR-082-only genuine drift: backfill vs accept' 별 smaller 결정 (본 CFP scope 외) / ADR-045 (single-block amendment_log[]-only) 면제 → genuine body-gap warning (amendments 1/7/10/11) 소멸, Option A 정합 (lint 가 single-block convention 미policing). lint scope correction = 신규 check 아닌 1-Q scope narrow → 기존 `adr-dual-block-parity` evidence-checks-registry entry + `hotfix-bypass:adr-dual-block-parity` label 재사용 (신규 entry / 신규 label 0, label-registry MINOR bump 0). Combined Phase 1+2 (ADR amendment Phase 1 + lint scope narrow Phase 2 develop lane dispatch, CFP-1648/CFP-1688 combined precedent 답습). axis disjoint from 1-A through 1-S (ADR structural-parity-lint scope refinement axis — 1-S Fix A supersede sub-refinement, 1-Q sub-domain 의 second narrow). user decision Option A (2026-05-26 KST, 'dual-block 전용으로 축소 (권장)'). META-self-applied (§결정 10.D 14th applied case + Amendment 17 §결정 1-G strict pre-reservation 7th applied case): 본 Amendment 32 = ADR-082 = dual-block exemplar 이며 narrow 후 lint 가 ADR-082 자신의 dual-block structure 위에서 false-positive 없이 PASS 해야 하는 recursive dogfooding (post-change lint 가 여전히 dual-block ADR-082 검사 — Amendment 32 의 amendments[] + amendment_log[] + body ## Amendment 32 3-block parity 필수, dual-block gate 가 ADR-082 를 면제 안 함). verified-via: `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] max=30 (CFP-1688 Amendment 30 merge 후 base) → next-slot = 31 at pre-spawn, 2026-05-26 KST 기준 origin/main 1d004935 (PRE-SPAWN-ORIGIN-MAIN-SHA verified, pre_spawn_pin_verified: true). **RESLOT 31 → 32 / sub-scope 1-T → 1-U post-CFP-1684 Amendment 31 + sub-scope 1-T mid-flight collision** (parallel race detect during re-rebase on origin/main — amendment_number_stale_at_planning pattern, ADR-082 Amendment 29 §1-R mid-Story FIX-loop re-verification self-apply; CFP-1684 PMOAgent retro write-time verify mandate took 31/1-T). ADR-RESERVATION row pre-append + commit 7926974d (pre_reservation_verified: true, reslot 32 applied)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 방향: §결정 1 layer 1 sub-scope (1-A/…/1-S) → (1-U dual-block gate narrow — 1-Q lint scope 를 dual-block-only ADR 로 정밀화) 신설. 본 Amendment 는 lint scope narrow (single-block ADR 면제) 이나 forbid scope 축소 아님 — narrow 의 효과는 (a) convention-mismatch false-positive 제거 = accuracy 강화 (over-rate 차단, ADR-081 §결정 D6 severity calibration 정합) + (b) dual-block ADR 의 F-DR-001 P0 sentinel (Block 2) 검증 retain — dual-block-only narrow 가 F-DR-001 보호를 약화하지 않음 (F-DR-001 origin 자체가 dual-block ADR-082 Amendment 26 case). single-block ADR 의 body-gap 은 Option A 결정상 lint policing 대상 아님 (35 parens-convention + ADR-045 single-block = lint 가 정확히 read 못하는 valid convention, FP 만 양산 → policing 가치 < FP 비용). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합 — false-positive narrow = accuracy 강화, guard 약화 0건 (dual-block ADR genuine drift surface 보존). pattern_count evidence: Orchestrator verify-before-trust 직접 ADR census (82 frontmatter-amendment ADR 중 lint 검출 39 / parens-convention 미검출 35) — convention diversity 가 1-S Fix A single-block-Block-2 approach 와 fundamental mismatch (Fix A 를 amendments[]-only 로 symmetric 확장 시 parens-convention 35 ADR 에 FP). is_transitional: false 유지 (permanent governance policy). user decision Option A. META-self-applied (§결정 10.D 14th applied case)."
  - amendment_id: 33
    carrier_story: CFP-1787
    date: 2026-05-27
    summary: "§결정 1 layer 1 sub-scope (1-V) 신설 — execution_context_reconciliation (verdict packet write-time execution context state declare). PMOAgent / retro write-target / chief author / deputy verdict packet 안 `execution_context_state` 5 sub-field 명시 declare 의무: (a) `working_dir_abs_path` (derivable via `pwd` — sub-scope 1-J + ADR-040 worktree convention 정합) (b) `target_write_repo` (derivable via `git -C <wt> remote -v` — sub-scope 1-J `worktree_target_repo` 와 axis-adjacent disjoint: 1-J = chief author worktree-level cross-repo target verify / 1-V = packet-level after-the-fact declare) (c) `staged_files_required[]` (novel axis — intent declaration, derive 불가능: 본 write 산출물이 staged 상태로 만들어야 하는 file 목록) (d) `branch_required` (derivable via `git branch --show-current` — ADR-040 / ADR-024 `cfp-NNN[-<slug>]` binding) (e) `remote_sync_required` (novel axis — pre-write intent enum: pull / fetch / N/A). 5 field 중 3 derivable + 2 novel — derive primitive cross-ref 본문 표 명시 (ratchet density 보호, ADR-068 I-4 wording SSOT). 본 sub-scope 1-V = sub-scope 1-A~1-U 22 entry 와 disjoint axis (packet-level execution context state declare axis). paired_sibling_base = Amendment 31 (1-T) — axis-adjacent supplementary clause (retro write fact verify ↔ execution context state declare). Wave 1 = declaration-only behavioral mandate (mechanical_enforcement_actions[] 신규 entry `execution-context-state-presence` warning-tier) + Wave 2 mechanical wire (scripts/lib/check_execution_context_state.py + templates/github-workflows/execution-context-state-check.yml + tests/wave2-mechanical-wire/check-execution-context-state.bats + label-registry-v2 v2.84 → v2.85 MINOR `hotfix-bypass:execution-context-state-presence` 110번째 family member + evidence-checks-registry entry) single Story combined PR (CFP-1648/1688/1734/1755 combined precedent 답습). 동인 = cluster anchor pattern_count 4 reach (CFP-1735 §6 + CFP-1753 §6 + CFP-1755 §6 + CFP-1764 §4.5 self) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation. ADR-073 paired Amendment 不要 (sub-scope 1-V axis disjoint complement from Orchestrator verify-before-assert axis — sub-scope 1-E/1-F precedent 와 차이). ADR-045 별도 Amendment 신설 不要 (cross-ref only, Amendment 10 §결정 12 precedent 답습). META self-applied (§결정 10.D 12th applied case): Amendment 번호(33) 가 target frontmatter `amendments:` Read verify 후 결정 (verified-via `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] max=32 2026-05-27 KST 기준 origin/main 1b08d2f4). dogfood self-application — 본 carrier Story 자체 spec frontmatter `pre_lookup_evidence[]` 안 `execution_context_state` 5 field declare 정합 (1-V sub-scope 의 1st applied case = self)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A~1-U) → (1-V execution_context_reconciliation) 확장, forbid scope 축소 아님). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. is_transitional: false 유지 (permanent governance policy). pattern_count evidence: cluster anchor 4 reach (CFP-1735 §6 + CFP-1753 §6 + CFP-1755 §6 + CFP-1764 §4.5 self) ≥ ADR-045 §D-9 threshold 2. META-self-applied (§결정 10.D 12th applied case + sub-scope 1-G 18th + sub-scope 1-L spawn prompt fact verify)."
  - amendment_id: 34
    carrier_story: CFP-1842
    date: 2026-05-29
    sub_scope: "1-W"
    scope: "§결정 1 layer 1 (Orchestrator scope) sub-scope 1-W `orchestrator_spawn_prompt_fact_verify_before_embed` 신설 — Orchestrator 가 subagent (lane PL / chief author / deputy / 4-tuple sub-tuple) spawn 직전 spawn prompt 안 fact 단언 (counter 값 / version / SHA / sha256 verify PASS / line count / 파일 존재 등) 발화 시점 verify-before-embed 의무. 5종 fact category (C1-C5) closed-enum: C1 counter (label-registry / evidence-checks / hotfix-bypass family count 등) / C2 version (label-registry-v2 version / plugin metadata version / marketplace.json version) / C3 SHA (origin/main HEAD / pre-spawn pin / file sha256) / C4 verify-result (sha256 byte-identical PASS / sub-agent claim PASS) / C5 file-existence (path 존재 + line count). 5종 모두 spawn prompt embed 직전 direct Read / git api / file system call verify 의무. axis disjoint vs sub-scope 1-L (CFP-1590) — 1-L = worker self-write spawn prompt fact (worker→worker handoff), 1-W = Orchestrator-side (Orchestrator→subagent handoff). pattern_count 3 reach Mandatory ADR-045 §D-9: 1차 CFP-1808 F-005 (sha256 PASS claim verify 없이 embed) + 2차 CFP-1807 F-002 (baseline counter stale 단언) + 3차 META (본 carrier 본 자체 ADR-082 Amd 번호 stale 단언). Wave 1 declarative-only — mechanical wire (lint script + workflow + bats + label-registry MINOR `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` + evidence-checks-registry entry) = CFP-1842-W2 별 sub-CFP carrier. precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 23 prior Amendment Wave 1→Wave 2 split chain. paired sibling ADR-073 Amendment 18 (transition trigger 16번째 entry `pre_spawn_prompt_fact_assertion` — 같은 cadence axis). ADR-058 §결정 5 ratchet 강화 only (sub-scope 22→23, scope 확장). ADR-064 §결정 5 CFP scope unitary (2 paired Amendment 단일 carrier 정합, axis 동형 sub-domain)."
    status: applied
    ref: "## Amendment 34 + sub-scope 1-W row"
    sunset_justification: null
  - amendment_id: 35
    carrier_story: CFP-822
    date: 2026-05-30
    sub_scope: "1-X"
    scope: "§결정 1 layer 1 (Orchestrator scope) sub-scope 1-X `subagent_self_report_post_task_verify` 신설 — Orchestrator 가 subagent 'DONE / success / PASS / MERGED' 보고 receive 후 critical artifact (ADR / Story / RETRO / scope_manifest / spec / plan / code FIX) 의 actual existence + content verify-before-trust 의무. 6종 critical artifact category closed-enum: ARTIFACT-1 ADR (docs/adr/ADR-*.md) / ARTIFACT-2 Story (Story file path) / ARTIFACT-3 RETRO (retro file) / ARTIFACT-4 scope_manifest (scope_manifests/*.yaml) / ARTIFACT-5 spec / plan (spec/plan path) / ARTIFACT-6 code FIX (production source file). Verify methods 5종: ls <path> + Read <path> (line 1-N) + wc -l + grep <expected keyword> + git status --short <path>. axis disjoint vs sub-scope 1-W (CFP-1842, Orchestrator → subagent pre-spawn fact verify cadence) — 1-X = subagent → Orchestrator post-task verify cadence (claim-receive trust gate). paired sibling ADR-073 Amendment 19 (transition trigger 17번째 entry `post_subagent_task_completion`, axis 동형 sub-domain cadence codify). pattern_count: mctrader MCT-189 + MCT-190 origin evidence N=2 reach (2026-05-17, #822 HIGH priority 12-day pre-existing). 본 carrier scope = wrapper-actionable §2 only (#822 §1 superpowers:subagent-driven-development implementer-prompt.md external claude-plugins-official defer + §3 mctrader-hub ADR-032 external defer). Wave 1 declarative-only — mechanical wire (lint script + workflow + bats + label-registry MINOR `hotfix-bypass:subagent-self-report-post-task-verify` + evidence-checks-registry entry) = CFP-822-W2 별 sub-CFP carrier. precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 24 prior Amendment Wave 1→Wave 2 split chain. ADR-058 §결정 5 ratchet 강화 only (sub-scope 23→24, scope 확장). ADR-064 §결정 5 CFP scope unitary (2 paired Amendment 단일 carrier 정합, axis 동형 sub-domain). META-self-applied: 본 carrier Orchestrator 가 본 ArchitectAgent spawn 'DONE' 보고 receive 후 5 file actual edit verify (ls + git status --short + Read) 의무 — 1-X 첫 적용 사례 = self."
    status: applied
    ref: "## Amendment 35 + sub-scope 1-X row"
    sunset_justification: null
  - amendment_id: 36
    carrier_story: CFP-1613
    date: 2026-06-01
    sub_scope: "1-Y"
    scope: "§결정 1 layer 1 (Orchestrator scope) sub-scope 1-Y `amendment_array_ordering_convention` 신설 — ADR frontmatter `amendments[]` + `amendment_log[]` array row-append ordering convention SSOT (hybrid: primary key amendment_id ascending + tie-break reservation_date ascending for paired-sibling concurrent reservation). 2 추가 codify: (a) sub-scope letter (1-A..1-Y) ↔ amendment_id (1..36) NOT guaranteed synchronized — reslot race decouple (CFP-1684 → Amd 31/sub-scope 1-T precedent), mapping resolution = amendment_log[] entry 의 `sub_scope` field SSOT (id↔sub-scope 동기 가정 금지, entry field 직접 read 의무) / (b) paired-sibling-race row-append decision tree 4-step ladder (pre-reservation per 1-G → collision 미발생 id ascending → collision 시 reservation_date tie-break reslot (reslotted = higher id) → reservation_date 동일 시 carrier CFP 번호 ascending final tie-break). dual-block-parity lint (sub-scope 1-Q/1-S, Amd 28/30) 는 set parity 만 검증 → 순서 axis 는 본 1-Y 가 codify (order-check 는 Wave 2 lint). axis disjoint vs sub-scope 1-S (CFP-1688 Amd 30, block convention SSOT — '어떤 block') — 1-Y = block 내부 row ordering ('어떤 순서'), 1-S sub-domain refinement. 동인 = CFP-1601 retro F-DR-1601-2 P2 (paired sibling race CFP-1559 Amd 20 ↔ CFP-1578 Amd 21 chronological-vs-id ordering ambiguity). MEDIUM Wave 1 declarative-only — mechanical wire (array-ordering lint script + workflow + bats + label-registry MINOR `hotfix-bypass:adr-amendment-array-ordering` + evidence-checks-registry entry) = CFP-1613-W2 별 sub-CFP carrier. precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 25 prior Amendment Wave 1→Wave 2 split chain. ADR-058 §결정 5 ratchet 강화 only (sub-scope 24→25, convention codify scope 확장). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. ADR-054 §결정 1 doc-only fast-path 적격 (단일 PR, scripts/tests 무변경). META-self-applied: 본 Amd 36 = sub-scope 1-Y 첫 적용 사례 — 본 carrier 가 id-ascending convention 을 자신의 amendments[] + amendment_log[] row append 에 적용 (max=35 → next-slot=36 id ascending 최하단 append, source command verify `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-*.md | tail -1` actual = amendment_id: 35 [verified])."
    status: applied
    ref: "## Amendment 36 + sub-scope 1-Y row"
    sunset_justification: null
  - amendment_id: 37
    carrier_story: CFP-2383
    date: 2026-06-20
    sub_scope: "1-Z"
    scope: "§결정 1 layer 1 sub-scope 1-L (Amd 23, CFP-1590) Wave 1 declaration-only → Wave 2 mechanical wire SSOT — `spawn-prompt-fact-verify` PR-body-proxy static presence-only lint binding (script + workflow + test). 설계 결정 5종 codify: (1) wire 메커니즘 = S2(`issue-body-claim-pre-screen`) 구조 답습 (line-by-line in_fence toggle masking + strip_inline_code + PER_BLOCK_SCAN_CAP=50 + ANNOTATION_MARKER 정적 substring `[verified-via:` + exit 0=PASS/1=FLAG/2=SETUP) 위에 삭제된 1-W source(`c84fadf3:scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py`)의 C1-C5 PATTERNS (C1 counter / C2 version / C3 SHA / C4 verify-result / C5 file-existence, ReDoS-safe nested-quantifier 0) 이식 + trigger/event/body-source = `tier-downgrade-guard.yml` 답습 (`on: pull_request: types:[opened,synchronize,reopened]` + `paths:[docs/...]` + `permissions: contents:read,pull-requests:read` + `env: <X>: ${{ github.event.pull_request.body }}` env 경유만, inline 보간 금지). (2) 1-W orphan = de-bloat 제거 상태 유지 — 1-W 파일 복원 금지 (ADR-058 ratchet 위배), 본 wire 는 1-L 최초 배선 (1-L 한 번도 wired 안 됨). axis disjoint 보존: 1-L = worker→worker handoff spawn prompt fact / 1-W = Orchestrator→subagent. (3) PR-body-proxy 한계 명시 — PR body 는 spawn prompt 의 proxy 일 뿐 실 spawn prompt 아님 (inherit fact 가 PR body 에 transcribe 된 경우만 검출, spawn prompt 직접 검사 아님). warning-tier advisory 유지 — blocking 승격 시 `[verified-via:` 위조 false-PASS 구조적 가능 → 보안 통제로 신뢰 금지. (4) FP guard 4종 EXEMPT (in_fence / inline code-span / blockquote / SELF_SOURCE — S2 답습, PR body 도 markdown). (5) deferral 명문화 — retro-fact-verify-mandate (Amd 31 / sub-scope 1-T, CFP-1684) + fix-loop-reverify-mandate (Amd 29 / sub-scope 1-R, CFP-1683) 2건 미배선 + #2166 부분 close 좌표. Phase 1 = ADR Amendment + mechanical_enforcement_actions[] `spawn-prompt-fact-verify` entry status flip 만 (실 script/workflow/test/registry detect_command·workflow 실파일·label-registry MINOR = Phase 2 구현 lane). axis disjoint vs 1-L 본문 (1-L = declaration-only mandate 정의 / 1-Z = 그 1-L 의 Wave 2 mechanical enforcement wire SSOT, numeric-claim 1-K↔1-N precedent 답습). 동인 = CFP-2380 S3 Epic — S1 deferred-followup-reconcile FLAG 2건 중 CFP-2383 가 해소하는 유일 대상 FLAG (`spawn-prompt-fact-verify` 3/3 auto_blocking; 다른 1건 `stale-local-main-checkout-divergence-check` 8/3 = 별 carrier scope 외). precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 26 prior Amendment Wave 1→Wave 2 split chain + S2(Amd 20 CFP-1559 → CFP-2382) 동형 직전 precedent. ADR-058 §결정 5 ratchet 강화 only (sub-scope 25→26, Wave 2 mechanical enforcement 추가, forbid scope 축소 0). ADR-060 §결정 5 warning mode first wire. ADR-054 §결정 1 doc-only fast-path 적격 (Phase 1 단일 PR, scripts/tests 무변경 — change-plan 면제, S1/S2 precedent 답습). paired sibling ADR-073 Amendment 不要 (sub-scope 1-Z = 1-L 의 mechanical wire complement, worker→worker axis — Orchestrator verify-before-assert axis 와 disjoint, 1-N/1-P precedent 답습). META-self-applied: 본 Amd 37 = sub-scope 1-Z 첫 적용 — id ascending convention (max=36 → next-slot=37, source command verify `grep -oE '^  - amendment_id: [0-9]+' archive/adr/ADR-082-*.md | tail -1` actual = amendment_id: 36 [verified]) + dual-block parity (amendments[] + amendment_log[] + body ## Amendment 37 3-block)."
    status: applied
    ref: "## Amendment 37 + sub-scope 1-Z row"
    sunset_justification: null
  - amendment_id: 38
    carrier_story: CFP-2646
    date: 2026-07-13
    summary: "§결정 16 신설 — resource-safety-claim ↔ proof-link write-time 정직 discipline (write-time verify super-class 의 3번째 presence-lint carrier). governance/보안 tooling(evidence-check 게이트·보안 script·워크플로 YAML)의 docstring·inline 주석·워크플로 YAML 주석에 resource-safety/복잡도/DoS-guard 안전성-claim(catastrophic backtracking 0 / ReDoS-safe / DoS 가드 / resource exhaustion 방어 / scan cap = bound / nested quantifier 0 류)을 쓸 때 (a) paired proof-reference(reproducer / wall-clock 벤치마크 / 복잡도 회귀 self-test 링크) 동반 또는 (b) honest-ceiling('bounded degradation, 임의 입력 무해 아님') downgrade 를 mandate. lint 은 이 proof-ref/ceiling 의 **presence** 만 검사 — claim 의 **참됨(truth)** 미강제(honesty-ceiling ADR-151 §결정7 상속, verify ⊋ presence disjoint). super-class 관계: §결정 11(code-level artifact write-time verify) + §결정 15(claim closed-set → paired annotation presence lint, issue-body-claim-pre-screen) 의 artifact-class 인스턴스 확장 — 신규 mechanism CLASS 아님. 원천 = CFP-2635 retro escalate_user 후보 A (pattern_count 2: CFP-2635 masking tool O(n²) DoS over-claim + CFP-2591 carrier-lint ReDoS over-claim, ADR-045 §D-9 forcing function). 2-layer: Layer 1 write-time declaration mandate(roster/skill prose, governance-tool 작성 주체 SecurityArch/dev/QADev — ADR-140 §결정3 hybrid 착지) + Layer 2 presence lint 5-piece chain(Python SSOT check_resource_safety_claim_proof.py + thin wrapper + byte-identical workflow pair + discriminating self-test + registry warning-tier entry + hotfix-bypass label + grandfather baseline). ★ 자기참조 DoS 회피(메타-재귀): 본 lint 도 파일 regex 스캔 = CFP-2635 SF-1 동일 표면 — 4-axis born-safe bound(T-1 anchored bounded regex nested-quantifier 0 / T-2 index-advance O(n) tokenize slice-in-loop 0 = check_shell_test_masking.py:235-252 / check_spawn_prompt_fact_verify.py 답습 / T-3 MAX_PHYSICAL_LINE_LEN per-physical-line truncate = count-cap 별개 축 / T-4 islice read cap) 처음부터 배선(CFP-2635 는 T-2 algorithmic + T-3 line-length 축 enumeration 누락으로 O(n²)). 본 lint 자기 docstring 정직 = 자기 resource-safety over-claim 금지(presence≠truth, bounded degradation) + AC-3 self-application(본 Story 산출물 전량 self-PASS = 자기 게이트 통과, self-referential 결함 재발 차단). tier = warning(continue-on-error, PR merge 무차단) — blocking 승격(FP 실측 ADR-060 evidence-gate 후)은 별 named carrier(`CFP-TBD` 금지, deferral-carrier-declared no-TBD lint 대상). precision 기법 = check-tier-honesty.py affirmative-context closed-set 매칭(정직한 부정 서술·정의부·정책 열거 EXEMPT — raw grep 금지) + issue-body-claim-pre-screen.py EXEMPT guard(code-span/fenced/blockquote) + grandfather baseline new-only subtract(legacy 27-file 동결). A2-5 판정 = 신규 ADR 아님(over-fragmentation) — ADR-082 Amendment 정합(disjoint 축 verify⊋presence 는 §결정 15/11 presence-lint carrier 로 ADR-082 안에 이미 해소). Phase 1 = ADR + write-time mandate roster prose + registry declarative anchor + change-plan(wrapper/change-plans/cfp-2646-resource-safety-claim-proof-lint.md); Phase 2 = 5-piece mechanical wire + registry status Active + label-registry MINOR. ADR-058 §결정5 ratchet 강화 only(sub-scope/carrier 추가, forbid scope 축소 0). ADR-060 §결정5 warning mode first wire. precedent 답습 ADR-082 §결정 15(CFP-1559→CFP-2382) + §결정 11 + 27 prior Amendment Wave1→Wave2 split chain. META-self-applied: 본 Amd 38 = §결정 16 첫 적용 — id ascending (max=37 → next-slot=38, source `grep -oE '^  - amendment_id: [0-9]+' archive/adr/ADR-082-*.md | tail -1` actual = amendment_id: 37 [verified 2026-07-13 KST base 6.82.0]) + dual-block parity(amendments[] + amendment_log[] + body ## Amendment 38 3-block). commit-time Orchestrator max+1 재검증 의무(병렬세션 reslot 대비)."
    direction: strengthening
    status: applied
    ref: "## Amendment 38 + §결정 16 신설"
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: write-time verify super-class scope 가 resource-safety-claim artifact class 로 확장, §결정 15 issue-body / §결정 11 code-level presence-lint carrier 에 3번째 carrier 추가 — forbid scope 축소 0). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy). pattern_count evidence: §결정 16 = 2 reach (CFP-2635 O(n²) DoS over-claim + CFP-2591 ReDoS over-claim, ADR-045 §D-9 threshold 2)."
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-841
    date: 2026-05-17  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 6"]
    nature: ratchet-up  # behavioral→mechanical scope 확장 (ADR-058 §결정 5 강화 방향)
    note: "§결정 6 known-limitation rationale 1 partial-stale 정정 (lane-self-write-ownership-matrix.yaml CFP-722 §13.A 실재 verified) + mechanical_enforcement_actions[] 2-entry deferred-followup + ADR-024 Amendment 7 (hotfix-bypass:corpus-claim-verify 34번째 / cross-plugin-ownership-verify 35번째) + label-registry-v2 v2.25 MINOR + evidence-checks-registry 2 entry warning tier 동반. ADR-068 I-5 directly-analogous pattern 재사용 (cross-ref only, I-5 본문 0건 변경)."
  - amendment_id: 2
    carrier_story: CFP-1016
    date: 2026-05-19  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1", "§결정 2"]
    nature: ratchet-up  # §결정 1 layer 1 (Orchestrator scope) Issue-body authorship 영역 확장 (ADR-058 §결정 5 강화 방향)
    note: "ADR-045 §D-9 pattern_count 3 ≥ threshold 2 forcing function 산물 (escalation_action escalate_user). 3 corpus occurrences: CFP-1000 (3 inversions in Issue body verified at Story §2.1 table) / CFP-1001 (L189 lint output FP verbatim transcribe in Issue body verified at §2.1 Pivot 1) / CFP-1002 (ADR-054 filename `-fast-path.md` cited but actual `-story-fast-path.md` verified at §2.1 row 2). Wave 1 mechanical: (a) story-page-structure.md template §2.1 verified state table codification + issue_origin frontmatter field 신설 (mechanically lint-enforceable wrapper-side) + (b) playbook §3.17 behavioral mandate section (Orchestrator self-discipline). scope (c) RequirementsPL spawn prompt template = 별 canonical CFP carrier 분리 (CFP-1002 precedent — wrapper-only Story 우선, cross-repo sibling sync 후순위 ratchet). 본 Amendment 자체가 META-self-applied: 본 ADR carrier Story CFP-1016 의 Issue body 가 Orchestrator-authored (CFP-1002 retro time), Story §2.1 verified state table 이 4 claims (CFP-1000 inversions / CFP-1001 lint output / CFP-1002 filename / ADR-082 next amendment_id) 검증 — eating the dog food."
  - amendment_id: 3
    carrier_story: CFP-1041
    date: 2026-05-20  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1"]
    nature: cross-ref-only  # ADR-085 disjoint complement (verify axis ↔ coordination axis) cross-ref 보완 관계 명시 — 본 ADR §결정 / mechanism 의미 변경 0 (ADR-073 Amendment 4 동형 precedent)
    note: "ADR-085 (Multi-session collaboration protocol) 신설로 verify axis (ADR-073/070/082/045 §D 4-layer) ↔ coordination axis (ADR-085 신설 5번째 layer) disjoint complement 관계 codify. 본 ADR §결정 1 layer disjoint 4-layer 표가 ADR-085 §결정 1 5-layer 표의 verbatim 답습 base — 5번째 row Multi-session coordination 신설 (ADR-082 본문 0건 변경 invariant 보존). 8 parallel race incidents single session lineage (CFP-953/946/949/932/954/991/967/1014, 2026-05-18 ~ 2026-05-19 KST) 가 ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach escalation_action adr_draft_emitted 산물 — verify axis 가 모두 충족되어도 coordination axis 부재 시 parallel race 차단 불가 evidence anchor. ADR-073 Amendment 4 동형 precedent (cross-ref-only Amendment, mechanism scope 침범 0, ADR-082 Amendment 1 ADR-073 cross-ref pattern verbatim 답습)."
  - amendment_id: 4
    carrier_story: CFP-1058
    date: 2026-05-20  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 (cross-ref only)"]
    nature: cross-ref-only  # ADR-RESERVATION schema amendments_reserved[] sub-tree 신설 cross-ref (Amendment id race convention 형식화) — ADR-082 본문 §결정 1-8 + Amendment 1-3 본문 의미 변경 0건
    note: "ADR-RESERVATION schema `amendments_reserved[]` sub-tree 신설 cross-ref — Amendment id slot reservation 형식화 (CFP-1041 vs CFP-689 Amendment id race precedent evidence, race-winner-takes-it informal convention → schema codify). ADR-082 본문 §결정 1-8 + Amendment 1-3 의미 변경 0 (ADR-054 §결정 1 doc-only fast-path 적격, ADR-073 Amendment 4 동형 cross-ref-only pattern). pre-existing baseline gap retroactive backfill (CFP-1312 retro F-004 finding, DesignReviewPL identified) — 본 backfill 자체 = ADR-082 §결정 9 forcing function (Amendment 6+7) retroactive correction (frontmatter `amendments[]` ↔ `amendment_log[]` consistency, ADR-068 I-4 wording SSOT 정합 — frontmatter SSOT drift 누적 시 Wave 2 mechanical lint `amendment-number-frontmatter-verify` Check (a) gap advisory False Negative 위험 차단)."
  - amendment_id: 5
    carrier_story: CFP-1110
    date: 2026-05-20  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1"]
    nature: ratchet-up  # §결정 1 layer 1 (Orchestrator scope) sub-scope (1-C) Lane PL spawn prompt user-utterance verbatim anchor 확장 (ADR-058 §결정 5 강화 방향)
    note: "사용자 직권 minimal path 첫 적용 (codeforge process 가 lane traversal fidelity loss source 라는 평가 결과 채택 정합 — Researcher net 35% 정당화 / Codex ROI indeterminate-부정쪽 confidence medium 수렴, 2026-05-20 KST). pattern corpus 누적 evidence: synthesizer-stale-reference 6 (CFP-722/801/792/810/819/825) + Researcher 12 occurrence 정정 (CFP-698) + scope 재확대 금지 invariant 6+ 위치 (CFP-758) + unverified-self-write-claim super-class 5. minimal path 정합: Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 (사용자 승인 2026-05-20 KST) — closed-loop break 외부 결정 채널. Wave 1 = behavioral mandate (lane PL spawn prompt 첫 줄 anchor block 의무) — Wave 2 mechanical lint = 별 CFP carrier (deferred-followup). sister Amendment = ADR-071 Amendment 6 (back-translation gate binding, lane return 직후 verify, CFP-1110 paired Amendment carrier)."
  - amendment_id: 6
    carrier_story: CFP-1198
    date: 2026-05-22  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 2", "§결정 9 (신설)"]
    nature: ratchet-up  # §결정 2 scope (b) verify 대상 확장 + §결정 9 신설 (amendment-number citation verify forcing function, ADR-058 §결정 5 강화 방향)
    note: "ADR-045 §D-9 pattern_count 2 ≥ threshold 2 Mandatory escalation 산물 (CFP-1177: ADR-027 Amendment 7 계획 → 실제 Amendment 9 stale / CFP-1179: ADR-063 Amendment 6/7 계획 → 실제 Amendment 8 stale). plan-time citation staleness 근본 원인 = target ADR frontmatter amendments: 목록 미검증 상태에서 번호 인용. §결정 2 scope (b) 의 'ADR frontmatter value 인용 시 verify' 범위가 amendment 번호 인용을 명시적으로 포함하도록 확장 — §결정 9 별도 결정으로 codify (scope (b) 의 sub-specialization). ADR-073 cross-ref: β-issue = Orchestrator-authored artifact (ADR-073 layer 1 scope) — 두 layer (ADR-073 Orchestrator-authored / ADR-082 internal lane agent self-write) 동시 적용 구조. mechanical_enforcement_actions[] 신규 entry amendment-number-frontmatter-verify deferred-followup 추가 (Phase 2 lint = 별 CFP-1198 Phase 2 sub-carrier). 본 Amendment 6 자체가 META-self-applied: 본 Amendment 번호(6) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(5)+1=6 으로 결정 (verified-via: Read ADR-082 frontmatter amendments[] 2026-05-22 KST)."
  - amendment_id: 7
    carrier_story: CFP-1312
    date: 2026-05-23  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 9"]
    nature: ratchet-up  # §결정 9 verify-before-cite scope (forward only → forward + backward 양방향) 확장 + CFP-1216 lint Check (b) backward-staleness 추가 wire (ADR-058 §결정 5 강화 방향)
    note: "ADR-045 §D-9 pattern_count 3 ≥ threshold 2 Mandatory escalation 산물 — CFP-1293 (#3 occurrence) 가 ADR-082 Amendment 6 Wave 1 behavioral mandate land 후 발생 (CFP-1198 2026-05-22 → CFP-1293 2026-05-23). stale citation = `ADR-083 Amendment 2` (실제 max=2 시점, 정확 next-slot = 3) — `M ≤ max` backward-staleness 패턴. CFP-1216 Phase 2 mechanical lint Check (b) 현 implementation `cited_m > max_id + 1` (forward only) 으로 backward-staleness escape. root cause = Wave 1 behavioral 단독 불충분 아닌 mechanical lint Check (b) coverage gap. dual-carrier (axis 동일, ADR-064 §결정 1 CFP scope unitary 정합): (1) §결정 9 wording 본문에 `M = max+1` 정확 next-slot 외 모두 stale ([WARN]) 명시 + (2) CFP-1216 lint script `scripts/lib/check_amendment_number_stale.py` Check (b) `cited_m != max_id + 1` 양방향 비교로 확장 + `[FORWARD-STALE]` / `[BACKWARD-STALE]` 출력 format 분리 + bats fixture `tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats` backward-staleness TC 3+ 추가 (TC-A-BWD-EXACT / TC-B-BWD-DEEP / TC-C-FWD-EXACT-NEXT pass guard) + self-reference exemption (ADR file 자체 §Amendment N 본문 안 자기 인용 = lint scope 제외, EC-3 self-protection 정합) + templates/** path filter (FP-완화 canonical example). evidence-checks-registry `amendment-number-frontmatter-verify` entry summary 갱신 (Check (b) 양방향 codify, status warning retain). 본 Amendment 7 자체가 META-self-applied: 본 Amendment 번호(7) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(6)+1=7 으로 결정 (verified-via: Read worktree ADR-082 frontmatter amendments[] 2026-05-23 KST 기준 origin/main bfc4806)."
  - amendment_id: 8
    carrier_story: CFP-1329
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 10 (신설)"]
    nature: ratchet-up  # §결정 10 신설 (ArchitectAgent write-time discipline 4 sub-scope A/B/C/D) — §결정 1 layer 1 + §결정 2 scope (a-d) write-time verify mandate sub-domain expansion (ADR-058 §결정 5 강화 방향)
    note: "ADR-082 super-class (write-time semantic truth verify) 안 ArchitectAgent chief author write-time discipline 4 sub-scope codify. 4 memory entry normative 승격 carrier: (1) `feedback_codex_tp2_verify_before_trust_pattern` (CFP-795 F-1 sentinel) — Codex TP#2 inline FIX 8-anchor mirror coverage checklist / (2) `feedback_mid_author_partial_revert_propagation_gap` (CFP-1009 dogfood inversion P1 sentinel) — body normative correction ↔ frontmatter inline comment / appendix / table cell propagation 의무 / (3) `feedback_architect_script_behavior_claim_verify` (CFP-1006 F-DR-1006-1 + CFP-1025 hypothesis refuted, pattern_count 2 reach) — script behavior assertion write-time empirical verify + DesignReviewPL audit point / (4) `feedback_meta_self_application_pattern` (CFP-1016 1st applied + CFP-1340 Amendment 2 §결정 15 2nd applied, pattern_count 2 reach) — Story introduces codification → carrier Story 자체에 1st applied. pattern_count evidence 혼합: §결정 10.A=1 (sentinel forward-prevention) / §결정 10.B=1 (sentinel forward-prevention) / §결정 10.C=2 reach / §결정 10.D=2 reach. ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated ratchet 정합 — sentinel forward-prevention (10.A+10.B) = 도구적 가치 evidence base, recurrence threshold 2 reach (10.C+10.D) = standard pattern_count base. 혼합 ratchet 정직 명시. 본 Amendment 8 자체가 META-self-applied (§결정 10.D 3rd applied case): 본 Amendment 번호(8) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(7)+1=8 으로 결정 (verified-via: Read worktree docs/adr/ADR-082-...md frontmatter amendments[] 2026-05-24 KST 기준 origin/main d24ab28). Wave 1 = declaration-only (4 sub-decisions 모두 behavioral directive). Wave 2 mechanical wire (DesignReviewPL audit dedicated points + ArchitectAgent self-discipline grep self-check) = 별 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습)."
  - amendment_id: 10
    carrier_story: CFP-1332
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 12 (신설)"]
    nature: ratchet-up  # §결정 12 신설 (RequirementsPL + retro-time verify-before-trust 2 sub-scope A/B) — ADR-082 super-class write-time verify scope expansion to retro-time empirical verify lifecycle (ADR-058 §결정 5 강화 방향)
    note: "ADR-082 super-class scope expansion = Amendment 2 (Issue-body authorship verify §결정 1 layer 1) RequirementsPL §2.1 codify strengthening + retro-time verify-before-trust axis 추가. 2 memory entry normative 승격 carrier: (1) `feedback_issue_body_verify_before_trust` (CFP-1000 INVERSE drift + CFP-1001 lint output FP, pattern_count 2 reach) — RequirementsPL spawn prompt MUST include explicit verify-before-trust mandate + §2.1 verified state table 의무 + Issue-body claim direct verify (reproduce lint / file Read line numbers / gh CLI probe gh-side state / file existence check) / (2) `feedback_wave_defer_empirical_verify` (CFP-1006 Wave-defer falsified + CFP-1025 corrective closure, pattern_count 2 reach) — retro time PMOAgent/Orchestrator 가 deferral rationale empirical verify (workflow X actual produced state post-merge / lint Y actually catches deferred concern / backward-compat scenario actual run). pattern_count 2 reach 양 sub-decision evidence-gate 통과. ADR-082 super-class disjoint axis expansion (write-time + retro-time, 단일 super-class 안 disjoint lifecycle layer). 본 Amendment 10 자체가 META-self-applied (§결정 10.D 5th applied case): 본 Amendment 번호(10) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(9)+1=10 으로 결정 (verified-via: Read worktree docs/adr/ADR-082-...md frontmatter amendments[] L11-57 max=9 2026-05-24 KST 기준 origin/main 38fc8ff — CFP-1330 Amendment 9 merge 후 base). Wave 1 = declaration-only behavioral mandate. Wave 2 mechanical wire (RequirementsPL §2.1 lint + retro empirical-verify-required marker) = 별 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습). lane plugin agent md cross-ref (codeforge-requirements RequirementsPLAgent.md / codeforge-pmo PMOAgent.md) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
  - amendment_id: 9
    carrier_story: CFP-1330
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 11 (신설)"]
    nature: ratchet-up  # §결정 11 신설 (Code-level write-time discipline 2 sub-scope A/B) — ADR-082 super-class write-time semantic truth verify scope expansion to test code + script error handling layer (ADR-058 §결정 5 강화 방향)
    note: "ADR-082 super-class (write-time semantic truth verify) 안 Code-level write-time discipline 2 sub-scope codify. 2 memory entry normative 승격 carrier: (1) `feedback_test_must_bind_to_production` (CFP-1025 F-CR-1025-2 sentinel) — regression bats/unit test = real production code source/exec 의무 (sed-extract real fn) / (2) `feedback_error_mask_metaroot` (CFP-1025 bootstrap-labels.sh:53-55 META-ROOT sentinel, CFP-1006 mis-diagnosis lineage verified) — script `2>/dev/null` 가 success/failure 보고 시 real error 마스킹 = mis-diagnosis amplifier META-ROOT. ADR-082 scope expansion = Amendment 8 (ArchitectAgent write-time discipline §결정 10) + 본 Amendment 9 (Code-level write-time discipline §결정 11) layer 양 layer 분할. pattern_count evidence: §결정 11.A=1 (CFP-1025 F-CR-1025-2 sentinel forward-prevention — test-quality regression coverage gap silent risk) / §결정 11.B=1 (CFP-1025 META-ROOT sentinel forward-prevention — META-ROOT severity = mis-diagnosis 전파 chain risk, CFP-1006 mis-diagnosis lineage downstream propagation verified). ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 정합 — sentinel forward-prevention (11.A+11.B) = 도구적 가치 evidence base (recurrence ≥ 2 wait 시 silent regression / mis-diagnosis 전파 risk). 본 Amendment 9 자체가 META-self-applied (§결정 10.D 4th applied case): 본 Amendment 번호(9) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(8)+1=9 으로 결정 (verified-via: Read worktree docs/adr/ADR-082-...md frontmatter amendments[] L11-51 max=8 2026-05-24 KST 기준 origin/main a0eb545 — CFP-1329 Amendment 8 merge 후 base). Wave 1 = declaration-only (2 sub-decisions 모두 behavioral directive). Wave 2 mechanical wire (CodeReviewPL audit dedicated points: tautology smell grep + `Grep '2>/dev/null' scripts/**` resource-creating/state-changing audit + codeforge-wide grep audit sweep) = 별 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습). lane plugin agent md cross-ref (codeforge-review CodeReviewAgent.md / codeforge-develop QADeveloperAgent.md) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
  - amendment_id: 11
    carrier_story: CFP-1338
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 13 (신설)"]
    nature: ratchet-up  # §결정 13 신설 (GitOps verify-before-trust discipline 3 sub-scope A/B/C) — ADR-082 super-class scope expansion to GitOps coordination layer (ADR-058 §결정 5 강화 방향)
    note: "GitOps verify-before-trust discipline 3 sub-scope codify (main_drift_bypass HIGH + verify_pin_head_sha + branch_protection_worktree_cleanup). 3 memory entry normative 승격 carrier: (1) `feedback_main_drift_bypass_audit_pattern` (pattern_count 5 reach HIGH — CFP-963 P1+P2 + CFP-1000 + CFP-1001 + CFP-1340/1329/1330/1332 batch 4-bypass label lineage) — 4 standard hotfix-bypass labels + [bypass-justification] audit comment template + ADR-024 Amendment 3 §결정 6.C audit trail mandate cross-ref / (2) `feedback_verify_pin_head_sha` (CFP-722 stale HEAD verification churn sentinel) — HEAD SHA pin step 0 (`gh api repos/<owner>/<repo>/commits/<branch> --jq '.sha'`) before any commit/branch verify-before-trust, ADR-073 sub-discipline cross-ref / (3) `feedback_branch_protection_worktree_cleanup` (branch protection 환경 workflow discipline) — push → PR open → merge 확인 → worktree 정리 순서 의무, ADR-024 + ADR-040 cross-ref. pattern_count 5 reach 13.A + sentinel forward-prevention 13.B/13.C. 본 Amendment 11 자체가 META-self-applied (§결정 10.D 6th applied case): 본 Amendment 번호(11) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(10)+1=11 으로 결정 (verified-via: Read worktree docs/adr/ADR-082-...md frontmatter amendments[] L11-65 max=10 2026-05-24 KST 기준 origin/main e7b7791 — CFP-1332 Amendment 10 merge 후 base). Wave 1 = declaration-only behavioral mandate. Wave 2 mechanical wire = 별 sub-carrier (deferred-followup). lane plugin agent md cross-ref (codeforge-pmo GitOpsAgent.md) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
  - amendment_id: 12
    carrier_story: CFP-1339
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 14 (신설)"]
    nature: ratchet-up  # §결정 14 신설 (PMOAgent retro batch closure pattern workflow codify) — ADR-082 super-class scope expansion to retro-emission batch closure workflow layer (ADR-058 §결정 5 강화 방향)
    note: "PMOAgent retro batch closure pattern codify. 1 memory entry normative 승격 carrier: `feedback_cfp_retro_batch_closure_pattern` (CFP-963 retro 4-batch precedent + CFP-1340/1329/1330/1332/1338/1339 본 6-CFP batch 2nd applied case — pattern_count 2 reach). 의무 절차: PMOAgent retro 시 multi follow-up CFP candidates batch-create simultaneously + sequential doc-only fast-path execution single session pattern + same lane execution pattern (Combined Req+Design lane / mechanical_fast_path_inline DesignReview / FLUID bypass label set). workflow efficiency evidence: CFP-963 ~6h for 4 Stories / 본 6-CFP batch ~10-12h for 6 consecutive Stories. ADR-082 super-class scope expansion to retro-emission batch closure workflow axis (write-time + retro-time + GitOps coordination + retro batch closure layer 4-axis 통합). 본 Amendment 12 자체가 META-self-applied (§결정 10.D 7th applied case): 본 Amendment 번호(12) 가 target ADR-082 frontmatter amendments: 목록 Read verify 후 max(11)+1=12 으로 결정 (verified-via: Read worktree docs/adr/ADR-082-...md frontmatter amendments[] L11-70 max=11 2026-05-24 KST 기준 origin/main c36ee92 — CFP-1338 Amendment 11 merge 후 base). Wave 1 = declaration-only behavioral mandate (workflow pattern codify). Wave 2 mechanical wire = 별 sub-carrier (deferred-followup). 본 Amendment 12 = CFP-1340 5-CFP batch 마지막 CFP carrier — META-self-application 7th applied case + 본 batch closure 자체가 §결정 14 pattern WORKING evidence."
  - amendment_id: 13
    carrier_story: CFP-1390
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 10.D (Wave 2 mechanical wire declarative anchor)"]
    nature: ratchet-up  # §결정 10.D META self-application pattern Wave 2 mechanical wire declarative anchor (CFP-1346 retro F2-FU Optional follow-up carrier) — ADR-058 §결정 5 강화 방향
    note: "§결정 10.D META self-application pattern Wave 2 mechanical wire declarative anchor. pattern_count cumulative 5 reach: CFP-1016 1st applied / CFP-1340 §결정 15 2nd applied / CFP-1329 Amendment 8 3rd applied (META self-applied by codifying itself) / CFP-1346 ADR-108 §결정 6 4th applied (description '74번째' claim = raw post-append count 74 PARITY) / 본 Amendment 13 5th applied (META self-applied — 본 Amendment 가 §결정 10.D pattern 의 declarative ratchet 강화 carrier). Wave 2 actual mechanical wire (detection logic for Story-self codification 1st applied case) = 별 sub-CFP carrier deferred-followup. `mechanical_enforcement_actions: [meta-self-application-wire]` 신설 placeholder declarative-only (실 wire = Wave 2). 본 Issue = declaration-only anchor + amendment_log entry 갱신 only — actual lint script + workflow + bats fixture wire = 별 sub-CFP. ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합 — META self-applied (5 reach: CFP-1016+1340+1329+1346+1390 sequential applied lineage)."
  - amendment_id: 14
    carrier_story: CFP-1336
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-D (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope 1-A/1-B/1-C → 1-D cross-repo label-write authority verify mandate 확장 (ADR-058 §결정 5 강화 방향)
    note: "CFP-1302 follow-up F2 carrier — D-4 chief dissent carry (cross-repo wrapper Issue ↔ impl repo PR labels bidirectional sync 영역). cross-repo label state 변경 직전 authority verify-before-write mandate codify (4-tuple primitive: a-wrapper→impl write authority / b-impl→wrapper write authority / c-cross-org block / d-verified-via annotation). ADR-073 Amendment 9 §결정 1 transition trigger `label_change` 와 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1336 carrier 안 paired Amendment). ADR-066 Amendment 4 (PAT scope `issues:write` cross-repo label sync 인가) 동반 — 3 ADR paired Amendment carrier (ADR-073/082/066). pattern_count evidence: cross-repo label state drift sentinel forward-prevention. Wave 1 declaration-only behavioral + evidence-checks-registry `cross-repo-label-sync` warning-tier entry (deferred-followup). Wave 2 mechanical wire = 별 sub-carrier (cross-repo-label-sync.yml workflow runtime activation + bats fixture + bidirectional sync state lint). **Amendment slot history (FIX iter chain — Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions, CFP-1390 mid-DesignReview spawn collision 추가)**: spawn Amd 8 planned → iter 1 Amd 10 → iter 2 Amd 12 → iter 3 Amd 13 → **iter 4 Amd 14 FINAL (ADR-067 max 3/3 cap EXCEED + user explicit continuation override)**. amendment_number_stale_at_planning pattern_count 8+ reach (CFP-1293/1303/1318/1336-iter1/1336-iter2/1336-iter3/1336-iter4 single Story 4 reach, 5th collision) ADR-045 §D-9 Mandatory escalation 정합. 본 Amendment 14 자체가 META-self-applied (§결정 10.D 9th applied case): 본 Amendment 번호(14) 가 target ADR-082 frontmatter amendments[] Read verify (origin/main 8fd36711 max=13 — CFP-1390 Amd 13 merge 후 base — 정확 next-slot = 14) 후 결정 (verified-via: git show origin/main:docs/adr/ADR-082-...md frontmatter amendments[] 2026-05-24 KST 기준 origin/main 8fd36711f1d5ce7c124dfb37226be1d35e142ec8 pinned_at: 8fd36711). Lane plugin agent md cross-ref (codeforge-pmo GitOpsAgent.md) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
  - amendment_id: 15
    carrier_story: CFP-1437
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-E (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope 1-A/1-B/1-C/1-D → 1-E spawn prompt SHA-anchor write-time verify mandate 확장 (ADR-058 §결정 5 강화 방향)
    note: "CFP-1389 Sub-CFP A carrier (CFP-1336 retro follow-up) — Pre-spawn HEAD-pin protocol mechanical lint Epic Wave 1 declarative-only carrier. Orchestrator (또는 PL agent / chief author) 가 lane PL / chief author / deputy / 4-tuple sub-tuple subagent spawn prompt 작성 시 4-tuple primitive (a-spawn prompt 첫 줄 `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 형식 / b-SHA 값 spawn 시점 `git rev-parse origin/main` direct fetch 일치 verify / c-parent → child cascade fresh re-fetch (parent SHA verbatim carry 금지) / d-verified-via annotation `pre_spawn_pin_verified: <bool>` field). ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent 답습 (spawn-time anchor block pattern, block 형식 verbatim 답습). ADR-073 Amendment 11 §결정 1 transition trigger `spawn_prompt_emit` 와 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier 안 paired Amendment). Wave 1 declaration-only behavioral + evidence-checks-registry `spawn-prompt-head-pin-presence` warning-tier entry (deferred-followup). Wave 2 mechanical wire = 별 sub-CFP carrier (lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry). 동인: CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence preventive solution carrier — chief author / deputy stale-at-planning 차단 forcing function. CFP-1336 single Story 안 4 reach (Amd 8 → 10 → 12 → 13 → 14, 5 collisions) + cross-Story 누적 (CFP-1293 + CFP-1303 + CFP-1318 + CFP-1336-iter1~iter4 + CFP-1390) ≥ ADR-045 §D-9 Mandatory threshold. paired sibling ADR-073 Amendment 11 = 2 ADR Amendment 동시 발의 (axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합). 본 Amendment 15 자체가 META-self-applied (§결정 10.D 10th applied case): 본 Amendment 번호(15) 가 target ADR-082 frontmatter amendments: 목록 Read verify (origin/main 67a541aa max=14 — CFP-1336 Amd 14 merge 후 base — 정확 next-slot = 15) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-24 KST 기준 origin/main 67a541aa6999d91fed0314589c7cbd83bded7d37 pinned_at: 67a541aa). Lane plugin agent md cross-ref (codeforge-pmo GitOpsAgent.md + codeforge-design chief author prompt) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
  - amendment_id: 16
    carrier_story: CFP-1436
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-F (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope 1-A/1-B/1-C/1-D/1-E → 1-F spawn-internal periodic origin re-pin protocol 확장 (ADR-058 §결정 5 강화 방향)
    note: "CFP-1389 Sub-CFP B carrier (CFP-1336 retro follow-up paired sibling of Sub-CFP A CFP-1437) — Mid-flight rebase auto-detection mechanical lint Epic Wave 1 declarative-only carrier. Sub-CFP A = preventive (pre-spawn time SHA-anchor pin) + Sub-CFP B = reactive (mid-spawn time periodic drift detection) = 2-layer defense forcing function 완결. chief author / deputy / 4-tuple sub-tuple subagent 가 작업 중간 spawn-internal time 4-tuple primitive (a-periodic check trigger 의무 매 N file edit 또는 매 Edit/Write tool 호출 후 또는 timer-based 일정 interval Wave 1 subagent 자체 판단 Wave 2 mechanical hook + `git fetch origin main --quiet` + `git rev-parse origin/main` 실행 / b-PRE-SPAWN-ORIGIN-MAIN-SHA block 값과 current origin/main SHA 비교 drift comparison / c-drift threshold ≥ N commits behind default N=1 any merge 초과 시 subagent RETURN early with `drift_detected: true` flag + payload pre_spawn_sha + current_origin_main_sha + commits_drift + drift_detected_at_step / d-verified-via annotation RETURN payload 안 `mid_spawn_drift_verified: <bool>` field 의무). ADR-082 sub-scope 1-E spawn-time anchor block pattern precedent (Amendment 15) 답습 + Amendment 15 (1-E pre-spawn pin) + Amendment 16 (1-F mid-spawn re-pin) = paired complementary defense. ADR-073 Amendment 12 §결정 1 transition trigger `mid_spawn_origin_drift_detected` 와 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier 안 paired Amendment). Wave 1 declaration-only behavioral + evidence-checks-registry `mid-spawn-drift-detection` warning-tier entry (deferred-followup). Wave 2 mechanical wire = 별 sub-CFP carrier (subagent runtime hook + lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry). 동인: Sub-CFP A 단독으로 catch 못 하는 mid-flight drift 영역 reactive layer 신설 — CFP-1336 9+ collisions evidence 공유 (preventive + reactive 2-layer defense 결정, sentinel evidence 별도 누적 0). paired sibling ADR-073 Amendment 12 = 2 ADR Amendment 동시 발의 (axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합). 본 Amendment 16 자체가 META-self-applied (§결정 10.D 11th applied case): 본 Amendment 번호(16) 가 target ADR-082 frontmatter amendments: 목록 Read verify (origin/main a1316f67 max=15 — CFP-1437 Amd 15 merge 후 base — 정확 next-slot = 16) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-24 KST 기준 origin/main a1316f67d920dcc28fe40dec7cb69547ab60e025 pinned_at: a1316f67). Lane plugin agent md cross-ref (codeforge-design chief author prompt + 모든 subagent runtime spawn) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
  - amendment_id: 17
    carrier_story: CFP-1435
    date: 2026-05-24  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-G amendment-slot pre-reservation strict claim) 확장 (ADR-058 §결정 5 강화 방향)
    note: "Sub-CFP C of CFP-1389 (CFP-1336 retro follow-up Sub-C) — Amendment-slot pre-reservation contract field codify carrier. ADR-RESERVATION `amendments_reserved[]` sub-tree (CFP-1058 Amendment 4 신설) 가 reactive — agent commit time 점유 후 row append (race-winner-takes-it convention). Sub-CFP C = strict claim BEFORE chief author write 의무 codify — chief author / deputy spawn 시점에 ADR-RESERVATION amendments_reserved[] row 의무 pre-append + spawn prompt 안 `pre_reserved_amendment_slots: [{adr: ADR-NNN, amendment_id: M}]` field 의무. 3-layer defense forcing function 완결 = Sub-CFP A (1-E preventive SHA pin) + Sub-CFP B (1-F reactive mid-spawn drift) + Sub-CFP C (1-G preventive slot pre-reservation). ADR-RESERVATION schema enhancement = frontmatter `schema_version` field 신설 (1.0 → 1.1) + amendments_reserved[] required fields documentation. paired sibling cross-ref = ADR-050 §결정 1 ADR-RESERVATION fine-grained amendment slot extension. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `amendment-slot-reservation-check` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + ADR-RESERVATION schema strict validation + concurrent reservation conflict detection + bats fixture + label-registry MINOR bump + evidence-checks-registry Active entry) = 별 sub-CFP carrier. 본 Amendment 17 자체가 META-self-applied (§결정 10.D 12th applied case): 본 Amendment 번호(17) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main b32a731a5e858224afce72b0e6fc86ce86ee1483 max=16 — CFP-1436 Amd 16 merge 후 base, 정확 next-slot = 17) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-24 KST 기준 origin/main b32a731a pinned_at: b32a731a). ADR-073 touch 0건 (Sub-CFP C 영역 외, paired sibling 부재 — ADR-082 + ADR-050 cross-ref + ADR-RESERVATION schema bump dual-binding). pattern_count evidence: CFP-1336 9+ collisions super-class evidence 공유 (Sub-CFP A/B 와 동일 base — 3-layer defense 결정 carrier)."
  - amendment_id: 18
    carrier_story: CFP-1342
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-H Orchestrator §10 FIX Ledger resolution field claim source/evidence verify) 확장 (ADR-058 §결정 5 강화 방향)
    note: "S6 Theme 5 Optional quartet — CFP-1316 retro F2 Optional carrier. Orchestrator self-write monopoly 영역 (§10 FIX Ledger resolution field — fix-event-v1 contract, CFP-32) 의 claim source/evidence verify 의무 명문화 — sub-scope 1-A/1-B/1-C/1-D/1-E/1-F/1-G 7종 외 codify gap closure (Orchestrator §10 FIX Ledger row resolution field write authority 영역 axis disjoint, fix-event-v1 contract level write-time semantic truth verify). 4 의무 codify: (a) Orchestrator §10 FIX Ledger row resolution field 작성 시 인용 source / evidence verify-via direct execution 의무 (b) measurable evidence claim 시 실 검증된 결과 verify (cached / inferred 사용 금지) (c) verified-via annotation (예: 'Read <path> + grep count = N + exit code = 0') 의무 (d) wrap-style 자동화 영역 = 실 실행 결과 stdout / exit code / grep diff 확인 후 작성. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `fix-ledger-resolution-source-verify` warning-tier deferred-followup — fix-event-v1 contract emit-time pre-check pattern). Wave 2 mechanical lint = 별 sub-CFP carrier (deferred-followup, ADR-082 §결정 6 retain pattern 답습). 동인 evidence: CFP-1316 iter 1 §10 FIX Ledger row resolution field claim 영역 'wrap 실행 완료, advisory 0 verified' 영역 = Orchestrator self-write monopoly verify-before-trust gap risk pattern (wrap 미실행 영역에서 작성됐다면 false declare = §결정 1 layer 1 위배). 본 Amendment 18 = sub-scope 1-H 명시 codify. doc-only fast-path ADR-054 Cat 1 단일 PR (script / workflow / bats wire 0건). 본 Amendment 18 자체가 META-self-applied (§결정 10.D 13th applied case + Amendment 17 sub-scope 1-G pre-reservation strict claim mandate 1st applied case): 본 Amendment 번호(18) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main 11bf2d95e47be364438cc293812f6066dc07ed0f max=17 — CFP-1341 Amd 17 merge 후 base, 정확 next-slot = 18) 후 결정 + ADR-RESERVATION amendments_reserved[] row pre-append 완료 (adr_number 82 amendment_id 18 reserved_by_cfp CFP-1342 reservation_date 2026-05-25 KST status active). minimal-applicability: §10 FIX Ledger resolution field write monopoly = Orchestrator only — lane agent / PL agent / chief author 영역 0 (sub-scope (1-B) 일반 lane agent self-write 와 disjoint axis)."
  - amendment_id: 20
    carrier_story: CFP-1559
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 15 (신설)"]
    nature: ratchet-up  # §결정 15 신설 — Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate (4 sub-pattern closed-set enumeration). ADR-082 super-class scope expansion (Amendment 2 §결정 1 layer 1 sub-scope 1-A Issue body authorship → Issue body content broader stale-claim super-class), ADR-058 §결정 5 강화 방향.
    note: "FU-CFP-D super-class carrier — Issue body stale-claim 4 sub-pattern closed-set declarative anchor. 4 sub-pattern: (a) PR #NNNN merge state stale / (b) CFP-NNNN MERGED/CLOSED state stale / (c) count number stale 'X VIOLATIONs' / 'Y defect' / 'pattern_count Z' / (d) sister carrier origin claim stale 'CFP-NNNN carrier'. CFP-1216 Phase 2 wired `amendment-number-frontmatter-verify` lint (sub-class — ADR-NNN Amd M regex citation only) extension super-class declarative anchor. paired sibling CFP-1558 = amendment-number sub-class declarative ratchet (axis disjoint, 본 ADR Amendment 21 점유 예정 — CFP-1559 발의 first chronological, CFP-1558 = Amendment 21 sequential allocation). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `issue-body-claim-pre-screen` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow + bats fixture + ContinuityAgent agent file cross-plugin) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split precedent 답습). pattern_count 7+ reach Mandatory ADR-045 §D-9 escalation 산물: CFP-FU-B Issue #1477 5-defect 3 PIVOT (60% stale rate) + CFP-1041/1050 RequirementsPL spawn packet stale claim lineage 4 = 합산 ≥ 7. ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated ratchet 강화 정합. False-positive 완화 guards (code-span / quoted-text / templates/** / §9 transcript EXEMPT) = Wave 2 lint design scope (Phase 1 declarative scope 외). axis disjoint with sister 3-layer defense (CFP-1437 spawn-time SHA pin / CFP-1436 mid-spawn drift / CFP-1435 amendment slot reservation / CFP-1342 Orchestrator §10 FIX Ledger / CFP-FU-A pre-spawn-prompt-finalize window — 본 Amendment 20 = Issue body content write-time axis). 본 Amendment 20 자체가 META-self-applied (§결정 10.D 15th applied case + Amendment 17 §결정 1-G strict claim mandate 2nd applied case after CFP-1492): 본 Amendment 번호(20) = target ADR-082 frontmatter `amendments:` Read verify (origin/main HEAD `4000440ee2c31c35b042dd0e5220be5c2f3aaefd` max=19 — CFP-FU-A Amd 19 merge 후 base, 정확 next-slot = 20) 후 결정. ADR-RESERVATION amendments_reserved[] row pre-append + commit + push 완료 verified (commit `7a7ac08`, ArchitectAgent body write 전 strict pre-claim 의무 충족)."
  - amendment_id: 19
    carrier_story: CFP-FU-A
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-I (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H) → (1-I pre-spawn-prompt-finalize verify layer) 확장 (ADR-058 §결정 5 강화 방향, renumbered from Amd 18/1-H post CFP-1342 mid-flight collision recovery)
    note: "CFP-FU-A sub-decision 3 — Race window 단축 layer. COLLISION RECOVERY: Amd 18/1-H plan ↔ CFP-1342 collision post-PR-#1527-open → rebase ca1c20e + renumber 18→19 + 1-H→1-I. 동인 = pattern_count 11 (CFP-1420) + 12th meta-occurrence (CFP-1342 in-flight recursive dogfooding: T0 worktree create → T1 prompt finalize → T2 commit → gap → T3 CFP-1342 merge → T5 collision → T6 recovery). 4-tuple primitive: (a) worktree create ~ prompt emit window 1회 polling / (b) git fetch + gh issue list + gh pr list 3-source AND / (c) race window 단축 / (d) `pre_spawn_prompt_finalize_verified` annotation. 4-layer temporal defense complete (Amd 15 pre-spawn-fetch + Amd 16 mid-spawn-periodic + Amd 18 Orchestrator §10 + 본 19 pre-spawn-prompt-finalize). paired sibling ADR-073 Amd 13 (polling cadence) + Amd 14 (OR→AND composition). Wave 1 declaration-only — Wave 2 별 sub-CFP. META-self-applied §결정 10.D 14th + collision recovery 1st (verified-via origin/main `ca1c20e` max=18 → next=19)."
  - amendment_id: 21
    carrier_story: CFP-1578
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-J (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I) → (1-J cross-repo worktree target authority verify mandate) 확장 (ADR-058 §결정 5 강화 방향). paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint, 동시 발의 race).
    note: "CFP-1578 carrier — worktree mis-target 첫 catch carrier (CFP-1539+CFP-1540 batch retro §4.1 #2 mandatory follow-up). 4-tuple primitive: (a) chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 worktree target authority verify-before-write 의무 — `git -C <worktree_abs_path> remote -v` 실행하여 expected repo (wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 확인 / (b) spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 명시 (write-target authority anchor block 형식 — sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block + sub-scope 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습) / (c) cross-repo 작업 sequence 시 명시적 worktree switch 의무 — wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별 worktree 분리, ADR-040 worktree convention 정합) / (d) verified-via annotation — spawn prompt 안 `worktree_target_authority_verified: <bool>` field 의무 명시. 본 sub-scope 1-J = sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) / 1-E (spawn prompt SHA-anchor) / 1-F (spawn-internal periodic drift) / 1-G (amendment-slot pre-reservation) / 1-H (Orchestrator §10 FIX Ledger source/evidence) / 1-I (pre-spawn-prompt-finalize) 와 disjoint axis. 가장 인접한 sub-scope = 1-D (cross-repo label-write authority — 동일 cross-repo write authority super-axis 안) 이나 verify 대상 disjoint: 1-D = label state write authority / 1-J = filesystem write-target (worktree path↔remote URL) authority. 동인 = CFP-1539+CFP-1540 batch retro §4.1 #2 (PMOAgent retro spawn 시 internal-docs PR target 작성 시 wrapper repo plugin-codeforge worktree 안에서 `git worktree add` 시도 후 정정 발생 — wrapper repo worktree mis-target 첫 catch occurrence). ADR-013 dogfood-out internal-docs SSOT path + ADR-040 worktree convention 정합 영역 codify 부재 super-class gap closure. RequirementsPL verdict Alternative C 채택 — Issue #1578 out-of-scope `ADR 신설` = new ADR file scope, ADR-082 sub-scope Amendment 영역과 disjoint axis. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `worktree-target-authority-verify` warning-tier deferred-followup). Wave 2 mechanical wire = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 Wave 1→Wave 2 split precedent 답습). 본 Amendment 21 자체가 META-self-applied (§결정 10.D 16th applied case): 본 Amendment 번호(21) 가 target ADR-082 frontmatter `amendments:` Read verify (worktree HEAD 4000440 origin/main amendments[] max=19 — CFP-FU-A Amd 19 merge 후 base + paired sibling CFP-1559 Amd 20 pre-claim gating → 정확 next-slot for CFP-1578 = 21) 후 결정. ADR-RESERVATION amendments_reserved[] row pre-append + commit + push 완료 (PRE-eee3ec6 commit on cfp-1578-wave3) — Amendment 17 sub-scope 1-G pre-reservation strict claim mandate META 2nd applied case (Amendment 18 CFP-1342 1st applied case precedent 답습)."
  - amendment_id: 22
    carrier_story: CFP-1601
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-K (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J) → (1-K numeric claim write-time strict claim mandate) 확장 (ADR-058 §결정 5 강화 방향). 동인 = ADR-045 §D-9 Mandatory escalation 산물 — CFP-1571 §3.2 line count drift '+93→+101' 3 location 정정 + CFP-1581 §3.2 file count drift '10→14' actual, pattern_count 2 reach.
    note: "CFP-1601 — numeric-claim write-time strict claim mandate 1st applied case. 4-step verify-before-write: (a) source command identify (`grep -c` / `wc -l` / `git diff --shortstat` / `find | wc -l`) / (b) direct execute actual value (cached/planning-time stale 금지) / (c) claim↔actual cross-verify (semantic ambiguity 시 source command 정밀화) / (d) write only on match. 6 dimension closed-set: line/file/API/pattern/commit/row count. axis disjoint vs 1-G (reservation lifecycle) — 1-K = generic numeric claim source/value verify. 동인 = pattern_count 2 (CFP-1571 line drift + CFP-1581 file drift). recursive dogfooding META first applied: spawn packet 'sub-scope 1-J' ↔ actual 1-J occupied (Amd 21 CFP-1578) → 1-K 정정 + `grep -c '^  - amendment_id:'` actual=41 line occurrence vs semantic max=21 divergence catch. Wave 1 declaration-only (`mechanical_enforcement_actions: numeric-claim-write-time-verify` warning-tier). Wave 2 별 sub-CFP. META-self-applied §결정 10.D 17th + Amd 17 1-G 3rd (verified-via worktree HEAD `0a19e6a` amendments[] max=21 → next=22)."
  - amendment_id: 23
    carrier_story: CFP-1590
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-L (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K) → (1-L spawn prompt fact verify-before-trust mandate upstream-inherited stale fact super-class) 확장 (ADR-058 §결정 5 강화 방향). PMOAgent CFP-1523 retro §5 inline ADR draft Orchestrator → ArchitectAgent spawn carry-over — chief author 자율 결정 Option B 채택 (super-class scope expansion). mid-flight CFP-1601 collision recovery (initial Amd 22+1-K spawn pinned origin/main `ec2fc349` + amendments[] max=21 → CFP-1601 Amd 22+1-K merge 후 base shift to `4c668913` + max=22 → renumber 22→23 + 1-K→1-L on rebase).
    note: "CFP-1590 — pattern_count 3 (anchor `stale_fact_inheritance_at_lane_spawn`): (1) CFP-1493 PR #1520 commit msg '284 MCP call' stale (실 6 atomic 47x over-estimate) / (2) CFP-1523 사용자 spawn prompt 4 fact stale / (3) CFP-1591 Issue body canonical/sibling 역할 반전. ArchitectAgent Option B (super-class scope expansion). axis disjoint: 1-C content 전달 형식 / Amd 20 self-write content stale / 1-K numeric own author / 1-L upstream-inherited stale fact at spawn-time. 4-tuple primitive: (a) 4 sub-source 식별 (사용자 발화/sibling Issue body/sister PR commit msg/별 carrier retro) / (b) `verified-via:` direct source (cached/synthesized 금지) / (c) `[fact-correction:]` marker / (d) `spawn_prompt_fact_verified: <bool>`. 4-layer temporal defense content fact axis 5th layer. Wave 1 declaration-only — Wave 2 별 sub-CFP. META-self-applied §결정 10.D 18th + Amd 17 1-G 4th + collision recovery 2nd (verified-via origin/main `4c668913` max=22 → next=23, renumber 22→23 + 1-K→1-L). doc-only fast-path."
  - amendment_id: 24
    carrier_story: CFP-1589
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-M (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L) → (1-M own-author synthesis 보고 vs actual git commit gap verify mandate) 확장 (ADR-058 §결정 5 강화 방향). F-DR-003 carrier (CFP-1523 retro carry-over). 4-tuple primitive: (a) synthesis 보고 시점 actual git commit verify 의무 (`git log origin/main..HEAD` direct execute) / (b) review-verdict-v4 packet 안 optional artifact_commits[] field 영역 (future MINOR bump 별 sub-CFP) / (c) Story §14 Lane Evidence row append 시 actual commit verify (ADR-073 verify-before-assert + ADR-082 §결정 1 layer 1 sub-scope 1-M dual binding) / (d) synthesis_vs_commit_gap_verified bool field annotation 의무. Wave 1 declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `synthesis-vs-commit-gap-check` warning-tier deferred-followup append). Wave 2 mechanical wire = 별 sub-CFP carrier 분리.
    note: "CFP-1589 carrier — F-DR-003 P1 finding (CFP-1523 retro §3 finding 3 ArchitectPL synthesis vs commit gap). pattern_count 1 deferred-followup carrier (Wave 1 declaration-only mandate, pattern_count 누적 시 Wave 2 mechanical wire 별 carrier 발의). axis 분리 vs Amd 23 1-L (upstream-inherited stale fact 4 sub-source 사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) + Amd 22 1-K (own author write-time numeric claim source/value strict 6-dimension): 1-L = upstream-inherited input verify (synthesis input 측, content fact axis) / 1-M = own-author synthesis 결과 vs actual artifact gap (synthesis output ↔ git commit downstream, own-author self-verify axis) / 1-K = own author write-time numeric claim source/value verify (own-author write-time numeric value axis). 1-L + 1-M = input-output paired axis (upstream input vs own-author output disjoint). origin = CFP-1523 carrier F-DR-002 P0 finding (Phase 1 ArchitectPL verdict packet 'Artifacts written: ...' 보고 ≠ actual git commit, DesignReviewPL audit verify-before-trust direct git status verify 후 detect, FIX iter 1 dispatch). PMOAgent retro carry-over (memory `project_cfp_1523_complete.md` 안 finding 3 박제). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `synthesis-vs-commit-gap-check` warning-tier deferred-followup append). Wave 2 mechanical wire (Python SSOT lint per ADR-061 + bash thin wrapper + workflow + bats RED→GREEN stash proof per §결정 11.A + label-registry MINOR `hotfix-bypass:synthesis-vs-commit-gap-check` + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합 + review-verdict-v4 v4.9 → v4.10 MINOR carrier 별 sub-CFP `artifact_commits[]` optional field schema 신설) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435/1559/1578/1601/1590 Wave 1→Wave 2 split precedent 답습). 본 Amendment 24 자체가 META-self-applied (§결정 10.D 19th applied case + Amendment 17 §결정 1-G strict claim mandate 5th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590): 본 Amendment 번호(24) 가 target ADR-082 frontmatter `amendments:` Read verify (worktree HEAD `f2e78b1` origin/main amendments[] max=23 — CFP-1590 Amd 23 merge 후 base, 정확 next-slot for CFP-1589 = 24) 후 결정 + ADR-RESERVATION amendments_reserved[] row pre-append commit `98ebb8c` + push (verified-via: `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] 2026-05-25 KST 기준 origin/main HEAD `f2e78b1`). doc-only fast-path ADR-054 Cat 1 단일 PR (ADR Amendment + CLAUDE.md cross-ref + ADR-RESERVATION row + evidence-checks-registry yaml row + CHANGELOG entry append only, script/workflow/bats wire 0건)."
  - amendment_id: 25
    carrier_story: CFP-1612
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-N (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M) → (1-N numeric claim write-time verify Wave 2 mechanical enforcement wire) 확장 (ADR-058 §결정 5 강화 방향). Issue #1612 HIGH FU-A from CFP-1601 retro carrier — 1-K Wave 1 declaration-only mandate (Amd 22) 의 Wave 2 mechanical enforcement wire. mid-flight CFP-1589 collision recovery (initial Amd 24+1-M spawn pinned origin/main `f2e78b16` + amendments[] max=23 → CFP-1589 Amd 24+1-M merge 후 base shift to `5b5c9f7b` + max=24 → renumber Amd 24→25 + sub-scope 1-M→1-N on rebase, ADR-082 §결정 1-L spawn packet fact verify-before-trust 1st applied case recursive dogfooding).
    note: "CFP-1612 carrier — Issue #1612 HIGH FU-A from CFP-1601 retro Wave 2 mechanical wire (1-K Amd 22 CFP-1601 declaration-only → mechanical lint enforce). 4-tuple primitive: (a) lint script SSOT (Python `scripts/lib/check_numeric_claim_write_time.py` ADR-061 multi-line Python convention + bash thin wrapper `scripts/check-numeric-claim-write-time-verify.sh`) / (b) 6 dimension detection logic (line/file/API/pattern/commit/row count) Python dict SSOT regex+source command pattern map / (c) FP guard 4종 (code-span EXEMPT + quoted-text EXEMPT + templates/** EXEMPT + docs/stories/§9 transcript EXEMPT) + PER_BLOCK_SCAN_CAP=50 CodeQL ReDoS guard / (d) workflow yml + .github/workflows/ byte-identical mirror per ADR-005 + `continue-on-error: true` warning tier + `hotfix-bypass:numeric-claim-write-time-verify` bypass label + evidence-checks-registry warning-tier initial registration. Phase 1 (본 Amendment 25) = declarative SSOT (ADR-082 §결정 1-N + ADR-RESERVATION row 25 + evidence-checks-registry warning-tier entry + label-registry-v2 MINOR + MANIFEST.yaml version bump + CHANGELOG). Phase 2 (별 sub-carrier — DeveloperPL + QADev spawn) = actual file write (scripts/lib/check_numeric_claim_write_time.py Python SSOT + scripts/check-numeric-claim-write-time-verify.sh bash wrapper + templates/github-workflows/numeric-claim-write-time-verify.yml workflow + .github/workflows/numeric-claim-write-time-verify.yml byte-identical mirror + tests/scripts/check-numeric-claim-write-time-verify/*.bats RED→GREEN stash proof per §결정 11.A). Wave 1→Wave 2 split precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589 11번째 instance. pattern_count ≥ N 추가 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리 (ADR-060 §결정 6 promotion gate AND 3/3 — PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged). 본 Amendment 25 자체가 META-self-applied (§결정 10.D 20th applied case + Amendment 17 §결정 1-G strict claim mandate 6th applied case after Amd 18/21/22/23/24 + Amendment 22 §결정 1-K numeric claim verify-before-write 1st applied for Wave 2 wire carrier + Amendment 23 §결정 1-L spawn prompt fact verify-before-trust 1st applied case recursive dogfooding mid-flight collision recovery 3rd applied case after CFP-FU-A Amd 19 + CFP-1590 Amd 23): 본 Amendment 번호(25) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main HEAD `5b5c9f7b` amendments[] max=24 — CFP-1589 Amd 24 merge 후 base post-collision-recovery, 정확 next-slot for CFP-1612 = 25) 후 결정 + ADR-RESERVATION amendments_reserved[] row pre-append (status active 직접 전환, ArchitectAgent chief author precedent — ADR-082 Amendment 24 row CFP-1589 직전 carrier 정합) + numeric claim 1-K self-apply spawn packet 'Amendment 24 + sub-scope 1-M' source command verify `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-...md | tail -1` actual = `amendment_id: 24` (Amd 24 CFP-1589 점유) → 정확 next-slot = 25 + 1-N 정정 = numeric-claim 1-K + spawn-packet-fact 1-L paired META first applied case (input-axis upstream-inherited fact verify + output-axis numeric value source command verify 동시 적용 recursive dogfooding). doc-only fast-path ADR-054 Cat 1 단일 PR (ADR Amendment + ADR-RESERVATION row + evidence-checks-registry yaml row + label-registry-v2 MINOR + MANIFEST.yaml version bump + CHANGELOG entry append only, script/workflow/bats wire 0건 = Phase 2 별 sub-carrier)."
  - amendment_id: 26
    carrier_story: CFP-1637
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-O (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/.../1-N) → (1-O PR commit msg + PR body layer numeric claim 3rd axis) 확장 (ADR-058 §결정 5 강화 방향). Issue #1637 Pattern 2 Mandatory escalation from CFP-1612 retro per ADR-045 §D-9 (pattern_count 2 reach: CFP-1601 §13.C claim 11 vs 15 + CFP-1612 commit msg LOC 29/~470/~155 vs 30/605/183). axis disjoint from 1-K (write-time governance docs scope) + 1-N (Wave 2 mechanical wire scope) — 본 1-O = PR commit message + PR body layer 3rd axis. Same 6 numeric closed-set dimension + same 4-step verify-before-write mandate inherit from 1-K. Wave 1 declaration-only — mechanical wire (Python SSOT `check_numeric_claim_write_time.py` scope expansion to commit msg/body detection) = 별 sub-CFP carrier (Wave 1 → Wave 2 split precedent 답습).
    note: "CFP-1637 carrier — Pattern 2 Mandatory escalation from CFP-1612 PMO retro §9 ADR-045 §D-9 4-field schema. pattern `meta-self-application-accuracy-violation` pattern_count 2 reach (CFP-1601 §13.C row 3 numeric drift + CFP-1612 PR #1631 commit msg LOC drift). Decision = Option α (Amendment 26 sub-scope 1-O 신설 declarative SSOT, axis disjoint codify with 1-K + 1-N 3-axis matrix). Wave 2 mechanical wire (current CFP-1612 wired Python SSOT scope 확장 to PR commit msg + PR body detection layer) = 별 sub-CFP carrier (ADR-082/070/077/078/097/CFP-1571/CFP-1581/CFP-1601/CFP-1612 Wave 1→Wave 2 split precedent 12번째 instance). META 21st applied case (CFP-1612 = 20th post-merge → CFP-1637 = 21st sequential carrier): 본 Amendment 번호(26) = target ADR-082 frontmatter `amendments:` Read verify (origin/main HEAD `d1c629f0` post-CFP-1612 Amd 25 merge + CFP-1630 fresh fetch + rebase clean state — amendments[] max=25 → 정확 next-slot for CFP-1637 = 26) 후 결정 + ADR-RESERVATION amendments_reserved[] row pre-append (status active 직접 전환, ArchitectAgent chief author precedent — ADR-082 Amendment 25 row CFP-1612 직전 carrier 정합). doc-only fast-path ADR-054 Cat 1 단일 PR (ADR Amendment + ADR-RESERVATION row + Story + Change Plan + CHANGELOG entry only, script/workflow/bats wire 0건). FIX iter 1 post-DesignReview corrections applied: amendment_log entry append (F-DR-001 P0) + CHANGELOG entry add (F-DR-002 P0) + ADR-RESERVATION row sequential placement (F-DR-003 P1)."
  - amendment_id: 27
    carrier_story: CFP-1647
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-P (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/.../1-O) → (1-P 1-O Wave 2 mechanical enforcement wire scope) 확장 (ADR-058 §결정 5 강화 방향). Issue #1647 HIGH FU-A from CFP-1637 retro — sub-scope 1-O Amd 26 CFP-1637 Wave 1 declaration-only mandate 의 Wave 2 mechanical lint enforcement wire. axis disjoint from 1-N (1-K Wave 2 wire — governance docs scope) — 본 1-P = 1-O Wave 2 wire (PR commit msg + PR body scope). 1-K ↔ 1-N pair + 1-O ↔ 1-P pair = declaration ↔ Wave 2 wire 4-quadrant matrix (governance docs / PR-level artifact × declaration / Wave 2 wire). Same 4-tuple primitive inherit from 1-N (Python SSOT scope expansion + workflow trigger 확장 + bats fixture + evidence-checks-registry entry target_section 갱신).
    note: "CFP-1647 (Issue #1647 HIGH FU-A from CFP-1637) — sub-scope 1-O Amd 26 Wave 2 mechanical enforcement wire (PR-level artifact scope). 4-tuple primitive: (a) `scripts/lib/check_numeric_claim_write_time.py` (CFP-1612 wired) scope 확장 to PR commit msg + PR body + bash `--scope pr-commit-msg|pr-body|all` / (b) 6 dimension dict 재사용 / (c) workflow trigger 확장 + `gh pr view --json title,body,commits` + `git log --format=%B` ingestion + FP guard 4종 + PER_BLOCK_SCAN_CAP=50 / (d) bypass label 재사용 (label-registry MINOR 0) + evidence-checks-registry target_section 갱신 (1-K+1-N+1-O+1-P). precedent: CFP-1601 (1-K) → CFP-1612 (1-N) → CFP-1637 (1-O) → 본 CFP-1647 (1-P) = 13번째 Wave 1→Wave 2 split. Wave 1 declarative SSOT — Wave 2 actual script+workflow+bats Phase 2 별 sub-carrier. META-self-applied §결정 10.D 22nd + Amd 17 1-G 8th + Amd 22 1-K 3rd + Amd 23 1-L 2nd + Amd 24 1-M 1st (verified-via origin/main `e1e2b751` max=26 → next=27). doc-only fast-path."
  - amendment_id: 28
    carrier_story: CFP-1648
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-Q (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/.../1-P) → (1-Q ADR dual-block parity 3-invariant forward-prevention lint) 신설 (ADR-058 §결정 5 강화 방향). Issue #1648 MEDIUM follow-up from CFP-1637 retro — F-DR-001 P0 origin sentinel mechanical carrier. Combined Phase 1+2.
    note: "CFP-1648 carrier — F-DR-001 P0 origin: Amendment N frontmatter amendment_log[] entry present but body ## Amendment N section missing (CFP-1637 retro 발견). 3-invariant check: Block 1 (amendments[] ↔ body H2 parity) / Block 2 (amendment_log[] ↔ body H2 parity — F-DR-001 P0 sentinel) / Block 3 (amendments[] ↔ amendment_log[] cross-count parity). Python SSOT `scripts/lib/check_adr_dual_block_parity.py` (ADR-061 thin wrapper, anchored simple regex CodeQL ReDoS guard ADR-061 Amendment 3 §결정 11 정합, line-by-line parse, PER_LANE_EVIDENCE_SCAN_CAP=30, Windows cp949 reconfigure) + bash thin wrapper `scripts/check-adr-dual-block-parity.sh` + D2 dual trigger workflow (pull_request paths:docs/adr/** + workflow_dispatch full-scan) + `.github/workflows/` byte-identical mirror ADR-005 + bats 8 TC RED→GREEN stash proof (CFP-1334 §8.4 5 markers: pre_impl_sha / git_stash_sequence / role_vocabulary / red_green_anchor / platform_verified) + evidence-checks-registry warning-tier initial registration (ADR-060 §결정 5 first introduction = warning mode) + label-registry-v2 MINOR bump v2.77 → v2.78 (`hotfix-bypass:adr-dual-block-parity` 103번째 hotfix-bypass:* family member, ADR-108 §결정 3 forcing function parity mandate 정합) + MANIFEST.yaml label_registry version 갱신. 본 Amendment 28 자체가 META-self-applied (F-DR-001 P0 sentinel 의 첫 META applied case — amendments[] entry + amendment_log[] entry + body ## Amendment 28 section 3-block parity 동시 write = forward-prevention lint 가 자기 자신의 Amendment 에 recursive dogfooding integrity verify 첫 적용). 본 Amendment 번호(28) = source command `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-*.md | tail -1` actual = `amendment_id: 27` (Amd 27 CFP-1647 점유) → 정확 next-slot for CFP-1648 = 28 [verified]."
  - amendment_id: 29
    carrier_story: CFP-1683
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-R (신설)"]
    nature: ratchet-up  # mid-Story FIX-loop re-verification mandate 신설 (axis disjoint from 1-G CFP-1435 Story-start pre-reservation — FIX-loop intra-Story window 영역).
    note: "CFP-1683 carrier — CFP-1646 retro F2 forcing function (`sister_session_race_in_design_lane` cumulative pattern_count ≥ 5: CFP-684 + CFP-698 + CFP-1041 + CFP-1591 + CFP-1646 3 sub-events). Direct evidence = CFP-1646 1st attempt FIX iter 1 → iter 2 → iter 3 spawn cycle 사이 amendment slot + version + bypass count 재verify 부재 → CFP-1657 Amd 16 slot + CFP-1648 v2.78/103번째 slot collision 발생 (ESCALATE_PACKET_INCOMPLETE outcome). Mandate: FIX iter ≥ 2 시점 ArchitectPL re-engage prompt 안 3-tuple 재verify 의무 (amendment_id slot + label-registry MINOR bump version + bypass family member raw count). Wave 1 declarative — Wave 2 mechanical wire (`scripts/lib/check_fix_loop_reverify.py` + bash thin wrapper + workflow body wire + bats RED→GREEN stash proof + boundary fixture pair) = 별 sub-CFP carrier. label-registry-v2 v2.80 → v2.81 (`hotfix-bypass:fix-loop-reverify-mandate` 106번째 hotfix-bypass:* family member). META-self-applied: 본 Amendment 자체가 CFP-1683 = FIX-loop re-verify mandate carrier ADR-082 dual-block parity (Amendment 28 sub-scope 1-Q) self-application — amendments[] + amendment_log[] + body 3-block dual-write."
  - amendment_id: 30
    carrier_story: CFP-1688
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-S (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/.../1-R) → (1-S ADR frontmatter block convention SSOT + 1-Q single-block/H3/frontmatter-scan-cap 3-fix scope correction) 신설 (ADR-058 §결정 5 강화 방향 — false-positive 정정 accuracy 강화, guard 약화 0건). CFP-FU-C from CFP-1680 retro Pivot 1 root cause + Orchestrator verify-before-trust FIX iter 1 (bug #3). Combined Phase 1+2.
    note: "CFP-1688 carrier — ADR frontmatter block convention SSOT codify (single-block = amendment_log[] only e.g. ADR-045 / dual-block = both e.g. ADR-082) + sub-scope 1-Q (CFP-1648 lint) scope correction (3 fix, 동일 parser-correctness false-positive class). 3 root cause: (1) ADR-045 frontmatter `amendment_log:` block ONLY (grep -cE '^amendments:' = 0, grep -cE '^amendment_log:' = 1) + body `### Amendment N` H3 heading (line 439) ↔ lint BODY_H2_AMENDMENT_PATTERN 은 `## Amendment N` H2 only detect → body_ids empty → 11 amendments 전부 Block 2 AMENDMENT_LOG_FRONTMATTER_ONLY false-positive + Block 3 CROSS_BLOCK_COUNT_MISMATCH false-fire / (2) H3 미detect / (3) frontmatter scan cap — `_extract_frontmatter_lines` 의 `lines[:PER_LANE_EVIDENCE_SCAN_CAP*10]` = 300 line slice 가 ADR-082 자신의 long frontmatter (2nd `---` = line 548) 의 amendment_log[] entry 22-29 (line 305-347, 300 초과) 절단 → false CROSS_BLOCK_COUNT_MISMATCH 30 != 20 + false BODY_ONLY_NO_LOG Amendment 30 (amendment_log[] line 353 cap 너머) — Orchestrator verify-before-trust ADR-073/ADR-082 direct extraction FIX iter 1 발견. Fix spec (Phase 2 develop lane dispatch via Change Plan §8): Fix A (single-block mode — amendments[] 부재 + amendment_log[] present 시 Block 1 + Block 3 skip, Block 2 만 적용) / Fix B (body heading `## Amendment N` H2 AND `### Amendment N` H3 both-level, bounded `{2,3}` H4 차단) / Fix C (frontmatter scan cap 확대 — `---` delimiter break 가 실 boundary, slice cap 5000 으로 full frontmatter scan, ReDoS 무관 correctness fix). lint scope correction = 기존 `adr-dual-block-parity` evidence-checks-registry entry + `hotfix-bypass:adr-dual-block-parity` label 재사용 (신규 entry / 신규 label 0, label-registry MINOR bump 0). META-self-applied: ADR-082 = dual-block exemplar — 본 Amendment 30 의 amendments[] + amendment_log[] + body ## Amendment 30 3-block parity authoring 정확, 단 lint PASS 는 Fix C 가 enabler (Fix C 없이 lint 가 amendment_log[] line 353 see 못해 false-fail). Fix C 적용 후 ADR-082 의 genuine body-section drift (amendments 8-13/18-21 frontmatter-only) = 정당 surface, body backfill = 별 follow-up CFP (out of scope). 본 Amendment 번호(30) = source command `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] actual max=29 (Amd 29 CFP-1683 점유) → 정확 next-slot for CFP-1688 = 30 [verified, origin/main 506f7cfc, PRE-SPAWN-ORIGIN-MAIN-SHA pinned]. ADR-RESERVATION row pre-append + commit dad73ec5 (pre_reservation_verified: true)."
  - amendment_id: 31
    carrier_story: CFP-1684
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-T (신설)"]
    nature: ratchet-up  # PMOAgent retro write-time verify-before-trust mandate 신설 (axis disjoint from §결정 9 CFP-1312 Amd 7 ArchitectAgent + Orchestrator scope — PMOAgent retro write scope). slot 재배정: CFP-1688 Amendment 30 + sub-scope 1-S 점유 → 본 CFP-1684 = Amendment 31 + sub-scope 1-T (4th parallel race reslot per ADR-082 Amd 29 §1-R mid-Story FIX-loop re-verification self-apply).
    note: "CFP-1684 carrier — CFP-1646 retro F3 forcing function (META recursive evidence). retro file write 시 cited fact (commit SHA + label-registry version + bypass family count + cross-Story memory pattern_count) source direct verify 의무. META self-application direct evidence: CFP-1646 retro write-time PMOAgent 자체 `stale_fact_inheritance` 진입 — Story spec wrapper merge SHA claim `e84f0460` (Phase 1 commit) vs actual `00641695` (merge commit) + internal-docs `0b37a71` vs actual `33fff4cf` — PMOAgent retro 안 verified-via correction 의 root carrier. Mandate: PMOAgent retro file write 시 SHA / version / count / pattern_count cited fact 의 `gh api` + `git log` source direct verify 의무. Wave 1 declarative — Wave 2 mechanical wire (`scripts/lib/check_retro_fact_verify.py` SHA pattern + version pattern presence-grep + verify trace presence) = 별 sub-CFP carrier. label-registry-v2 v2.81 → v2.82 (`hotfix-bypass:retro-fact-verify-mandate` 107번째 hotfix-bypass:* family member). slot 재배정 audit: CFP-1688 가 Amendment 30 + sub-scope 1-S + (v2.81 retain, label bump 0) 점유 → 본 CFP-1684 reslot Amendment 31 + sub-scope 1-T + label-registry v2.82 (CFP-1688 label bump 0 이므로 v2.81 → v2.82 retain) + 107번째 family member retain. META-self-applied: 본 ADR codify 자체가 retro write-time verify 정합 (recursive dogfooding) — amendments[] + amendment_log[] + body 3-block dual-write per Amendment 28 parity + Amendment 29 §1-R mid-Story FIX-loop re-verification self-apply (CFP-1688 slot collision detect → reslot)."
  - amendment_id: 32
    carrier_story: CFP-1734
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-U (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/…/1-S) → (1-U dual-block gate narrow — 1-Q lint scope 를 dual-block-only ADR 로 정밀화, Amendment 30 sub-scope 1-S Fix A single-block-Block-2 supersede) 신설 (ADR-058 §결정 5 강화 방향 — false-positive narrow accuracy 강화 + dual-block F-DR-001 P0 sentinel retain, guard 약화 0건). CFP-FU from CFP-1688 #1734 carrier + user Option A 결정. Combined Phase 1+2.
    note: "CFP-1734 carrier — sub-scope 1-Q (CFP-1648) dual-block parity lint scope 를 **dual-block-only ADR** 로 narrow. 동인: Orchestrator verify-before-trust 직접 ADR census — frontmatter amendments[]/amendment_log[] 보유 82 ADR 중 lint body detection (`## Amendment N` / `### Amendment N` H2/H3, post-CFP-1688 Fix B) 이 검출하는 convention 39개뿐, 35개는 THIRD body convention `## §결정 N. <title> (Amendment M, CFP-XXX)` (§결정 heading 안 parens 안 amendment 번호, 예 ADR-071 `## §결정 12. DialogFidelityAgent ... (Amendment 1, CFP-777)`) 미검출 — lint 가 read 못하는 valid convention. CFP-1688 Fix A (single-block amendment_log[]-only → Block 2 만) 를 amendments[]-only 로 symmetric 확장 시 이 35 parens-convention ADR 에 FP 발생. **Dual-block gate (Phase 2 develop spec)**: `_check_adr_parity` top 에서 `amendments_ids` non-empty AND `amendment_log_ids` non-empty (= dual-block ADR, 예 ADR-082) 일 때만 Block 1/2/3 적용 (Fix B H2/H3 body detection + Fix C frontmatter scan cap RETAIN dual-block path), ELSE (single-block 양방향 = amendment_log[]-only / amendments[]-only / no-amendments) 면제 → return PASS (no violations). 이는 CFP-1688 Fix A 의 'single-block (amendment_log[]-only) → Block 2 만' 거동을 supersede — single-block 이 이제 fully exempt (Block 2 미적용). Amendment 32 = Amendment 30 sub-scope 1-S 의 refine/narrow. 효과: (1) #1734 RESOLVED — amendments[]-only ADR (parens-convention ADR-071 포함) 면제 → FP 0 / (2) #1735 narrow — dual-block ADR 만 policing → ADR-082 = 유일 genuine drift dual-block ADR (amendments 8-13/18/20-21 body 부재 + amendment_log[] entry 13 부재), #1735 = 'ADR-082-only genuine drift: backfill vs accept' 별 smaller 결정 (본 CFP scope 외) / (3) ADR-045 (single-block amendment_log[]-only) 면제 → genuine body-gap warning (amendments 1/7/10/11) 소멸, Option A 정합 (single-block convention 미policing accept). lint scope correction = 신규 check 아닌 1-Q scope narrow → 기존 `adr-dual-block-parity` evidence-checks-registry entry + `hotfix-bypass:adr-dual-block-parity` label 재사용 (신규 entry / 신규 label 0, label-registry MINOR bump 0). bats TC 변경 (Change Plan §8 SSOT): CFP-1688 TC-9 (single-block amendment_log[]-only all body present, PASS via Fix A skip) → PASS via EXEMPT (exit code 동일, rationale 변경) / CFP-1688 TC-10 (single-block genuinely missing body, WARNING via Block 2 retain) → **PASS (EXEMPT) — exit 1 → exit 0 breaking assertion change** / CFP-1688 TC-3 (body-only ADR amendments[] [] + amendment_log[] [], WARNING) → PASS (EXEMPT, degenerate non-dual-block) / dual-block ADR (TC-1/4/7/11/14/15) UNCHANGED (Block 2 F-DR-001 sentinel retain — fixture adr-amendment-log-missing.md 는 dual-block 이므로 TC-4/TC-7 F-DR-001 sentinel 보존). Combined Phase 1+2 (CFP-1648/CFP-1688 combined precedent 답습). 본 Amendment 번호(31) = source command `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] actual max=30 (Amd 30 CFP-1688 점유) → 정확 next-slot for CFP-1734 = 31 [verified, origin/main 1d004935, PRE-SPAWN-ORIGIN-MAIN-SHA pinned]. sub-scope letter = 1-S 다음 = 1-U [verified, body sub-scope census 1-A..1-S 점유]. ADR-RESERVATION row pre-append + commit 7926974d (pre_reservation_verified: true). META-self-applied: ADR-082 = dual-block exemplar — narrow 후 lint 가 ADR-082 자신의 dual-block structure 위에서 여전히 Block 1/2/3 검사 (dual-block gate 가 면제 안 함) → Amendment 32 의 amendments[] + amendment_log[] + body ## Amendment 32 3-block parity 필수 (recursive dogfooding mandatory)."
  - amendment_id: 33
    carrier_story: CFP-1787
    date: 2026-05-27  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-V (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A~1-U) → (1-V execution_context_reconciliation) 신설 (ADR-058 §결정 5 강화 방향 — verdict packet 5 sub-field declare 의무 ratchet, forbid scope 축소 아님). audit-from-CFP-1764-retro carrier + cluster anchor pattern_count 4 reach.
    note: "CFP-1787 carrier — CFP-1764 §4.5 audit packet origin. cluster anchor pattern_count 4 reach (CFP-1735 §6 + CFP-1753 §6 + CFP-1755 §6 + CFP-1764 §4.5 self) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation. Mandate: verdict packet (PMOAgent / chief author / deputy / retro write-target) 안 `execution_context_state` 5 sub-field 명시 declare 의무 — (a) `working_dir_abs_path` derivable via `pwd` ADR-040 worktree convention 정합 / (b) `target_write_repo` derivable via `git -C <wt> remote -v` axis-adjacent disjoint sub-scope 1-J / (c) `staged_files_required[]` novel axis intent declaration derive 불가능 / (d) `branch_required` derivable via `git branch --show-current` ADR-040 / ADR-024 binding / (e) `remote_sync_required` novel axis pre-write intent enum pull/fetch/N/A. 5 field 중 3 derivable + 2 novel — derive primitive cross-ref 본문 §결정 표 명시 (ratchet density 보호, ADR-068 I-4 wording SSOT). axis disjoint statement: sub-scope 1-V vs 1-A (Orchestrator state read verify-before-cite axis) / 1-V vs 1-J (chief author worktree-level cross-repo target verify) / 1-V vs 1-T (retro fact source direct verify) / 1-V vs 1-U (sub-scope 1-T mechanical lint Wave 2 wire) — verify subject axis disjoint (fact source vs environment state, lint axis vs declarative axis). Wave 1 declarative + Wave 2 mechanical wire single Story combined PR (CFP-1648/1688/1734/1755 combined precedent 답습) — scripts/lib/check_execution_context_state.py + templates/github-workflows/execution-context-state-check.yml + tests/wave2-mechanical-wire/check-execution-context-state.bats + label-registry-v2 v2.84 → v2.85 MINOR `hotfix-bypass:execution-context-state-presence` 110번째 family member + evidence-checks-registry warning-tier entry. ADR-073 paired Amendment 不要 (sub-scope 1-V axis disjoint complement from Orchestrator verify-before-assert axis). ADR-045 cross-ref only. 본 Amendment 번호(33) = source command `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] actual max=32 (Amd 32 CFP-1734 점유) → 정확 next-slot for CFP-1787 = 33 [verified, origin/main 1b08d2f4, PRE-SPAWN-ORIGIN-MAIN-SHA pinned]. sub-scope letter = 1-U 다음 = 1-V [verified, body sub-scope census 1-A..1-U 점유]. ADR-RESERVATION row pre-append commit f16e16fd (pre_reservation_verified: true). META-self-applied (§결정 10.D 12th applied case + sub-scope 1-G 18th + sub-scope 1-L spawn prompt fact verify): ADR-082 = dual-block exemplar — Amendment 33 의 amendments[] + amendment_log[] + body ## Amendment 33 3-block parity 필수 (Amendment 32 sub-scope 1-U dual-block gate self-application recursive dogfooding). dogfood self-application — 본 carrier Story 자체 spec frontmatter `pre_lookup_evidence[]` 안 `execution_context_state` 5 field declare 정합 (1-V sub-scope 의 1st applied case = self)."
  - amendment_id: 34
    carrier_story: CFP-1842
    date: 2026-05-29  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-W (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A~1-V) → (1-W orchestrator_spawn_prompt_fact_verify_before_embed) 신설 (ADR-058 §결정 5 강화 방향 — 5종 fact category C1-C5 verify-before-embed 의무 ratchet, forbid scope 축소 아님). Mandatory ADR-045 §D-9 escalation source — pattern_count 3 reach.
    note: "CFP-1842 carrier — Mandatory ADR-045 §D-9 escalation source. pattern_count 3 reach: (1) CFP-1808 F-005 — Orchestrator → DesignReviewPL spawn 시 ArchitectAgent 'sha256 PASS' claim verify 없이 embed / (2) CFP-1807 F-002 — Orchestrator → ArchitectAgent spawn 시 baseline counter (v2.82 / 107 / 137) stale 단언 / (3) META — 본 Issue #1842 초기 body 'ADR-082 Amd 24 sub-scope 1-W' 인용 (actual Amd 33 / next 34) 동일 패턴 재발현. Mandate: Orchestrator 가 subagent (lane PL / chief author / deputy / 4-tuple sub-tuple) spawn 직전 spawn prompt 안 fact 단언 (5종 category C1-C5 — C1 counter / C2 version / C3 SHA / C4 verify-result / C5 file-existence) verify-before-embed 의무. axis disjoint vs sub-scope 1-L (CFP-1590, worker→worker handoff) — 1-W = Orchestrator-side (Orchestrator→subagent handoff). paired sibling ADR-073 Amendment 18 (transition trigger 16번째 entry `pre_spawn_prompt_fact_assertion`, axis 동형 sub-domain cadence codify). ADR-064 §결정 5 CFP scope unitary (2 paired Amendment 단일 carrier 정합). Wave 1 declarative-only — Wave 2 mechanical wire (lint script + workflow + bats + label-registry MINOR `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` + evidence-checks-registry entry) = CFP-1842-W2 별 sub-CFP carrier. precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 23 prior Amendment Wave 1→Wave 2 split chain. META-self-applied: 본 carrier Story 의 spawn prompt 자체가 사전 verify (Amd 33 + 1-V baseline 직접 Read verify 후 next-slot Amd 34 + 1-W 결정) — 1-W sub-scope 의 1st applied case = self. dual-block parity: ADR-082 = dual-block exemplar (Amd 32 sub-scope 1-U dual-block gate self-application), 본 Amd 34 의 amendments[] + amendment_log[] + body ## Amendment 34 3-block parity 보존."
  - amendment_id: 35
    carrier_story: CFP-822
    date: 2026-05-30  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-X (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A~1-W) → (1-X subagent_self_report_post_task_verify) 신설 (ADR-058 §결정 5 강화 방향 — subagent "DONE/PASS/MERGED" 보고 receive 후 critical artifact actual existence + content verify 의무 ratchet, forbid scope 축소 아님). HIGH priority pre-existing #822 (12 day) carrier. mctrader MCT-189 + MCT-190 evidence N=2 reach (2026-05-17).
    note: "CFP-822 carrier — HIGH priority 12-day pre-existing Issue. mctrader-hub MCT-189/MCT-190 origin evidence (2026-05-17). Mandate: Orchestrator 가 subagent (lane PL / chief author / deputy / 4-tuple sub-tuple) 'DONE / success / PASS / MERGED' 보고 receive 후 critical artifact (ADR / Story / RETRO / scope_manifest / spec / plan / code FIX) 의 actual existence + content verify-before-trust 의무. 6종 critical artifact category (closed-enum): (1) ARTIFACT-1 ADR (docs/adr/ADR-*.md) / (2) ARTIFACT-2 Story (Story file path) / (3) ARTIFACT-3 RETRO (retro file) / (4) ARTIFACT-4 scope_manifest (scope_manifests/*.yaml) / (5) ARTIFACT-5 spec / plan / (6) ARTIFACT-6 code FIX (production source file). Verify methods 5종: ls <path> + Read <path> (line 1-N) + wc -l + grep <expected keyword> + git status --short <path>. axis disjoint vs sub-scope 1-W (Amd 34 Orchestrator → subagent pre-spawn fact verify, Orchestrator-side pre-spawn cadence) — 1-X = subagent → Orchestrator post-task verify (Orchestrator-side post-task cadence, claim-receive trust gate). paired sibling ADR-073 Amendment 19 (transition trigger 17번째 entry `post_subagent_task_completion`, axis 동형 sub-domain cadence codify). ADR-064 §결정 5 CFP scope unitary (2 paired Amendment 단일 carrier 정합). Wave 1 declarative-only — Wave 2 mechanical wire (lint script + workflow + bats + label-registry MINOR `hotfix-bypass:subagent-self-report-post-task-verify` + evidence-checks-registry entry) = CFP-822-W2 별 sub-CFP carrier. precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 24 prior Amendment Wave 1→Wave 2 split chain. 본 carrier scope = wrapper-actionable §2 only (#822 §1 superpowers:subagent-driven-development implementer-prompt.md external claude-plugins-official + §3 mctrader-hub ADR-032 external defer). META-self-applied: 본 carrier Orchestrator 의 본 ArchitectAgent spawn 자체가 1-X 첫 적용 사례 — Orchestrator 가 ArchitectAgent 'DONE' 보고 receive 후 5 file actual edit verify (ls + diff + Read) 의무. dual-block parity: 본 Amd 35 의 amendments[] + amendment_log[] + body ## Amendment 35 3-block parity 보존 (Amd 32 sub-scope 1-U dual-block gate self-application 정합)."
  - amendment_id: 36
    carrier_story: CFP-1613
    date: 2026-06-01  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-Y (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A~1-X) → (1-Y amendment_array_ordering_convention) 신설 (ADR-058 §결정 5 강화 방향 — ADR frontmatter amendments[] + amendment_log[] array row-append ordering convention codify, forbid scope 축소 아님). MEDIUM Wave 1 declarative. CFP-1601 retro F-DR-1601-2 P2 paired-sibling-race ordering ambiguity 동인.
    note: "CFP-1613 carrier — MEDIUM Wave 1 declarative. 동인 = CFP-1601 retro F-DR-1601-2 P2 (paired sibling race CFP-1559 Amd 20 ↔ CFP-1578 Amd 21 chronological-vs-id ordering ambiguity). Mandate: ADR frontmatter `amendments[]` + `amendment_log[]` array row-append ordering convention SSOT = hybrid (primary key amendment_id ascending + tie-break reservation_date ascending for paired-sibling concurrent reservation). 2 추가 codify: (a) sub-scope letter (1-A..1-Y) ↔ amendment_id (1..36) NOT guaranteed synchronized — reslot race decouple (CFP-1684 → Amd 31/sub-scope 1-T precedent), mapping resolution = amendment_log[] entry `sub_scope` field SSOT (id↔sub-scope 동기 가정 금지, entry field 직접 read 의무) / (b) paired-sibling-race row-append decision tree 4-step ladder (pre-reservation per sub-scope 1-G → collision 미발생 시 id ascending → collision 시 reservation_date tie-break reslot (reslotted entry = higher id) → reservation_date 동일 시 carrier CFP 번호 ascending final tie-break). axis disjoint vs sub-scope 1-S (Amd 30 CFP-1688, block convention SSOT single-block vs dual-block — '어떤 block') — 1-Y = block 내부 row ordering ('어떤 순서'), 1-S sub-domain refinement. dual-block-parity lint (sub-scope 1-Q/1-S, Amd 28/30) 는 set parity (amendment_id 집합) 만 검증 → 순서 axis 는 본 1-Y codify (order-check Wave 2 lint). paired sibling ADR-073 Amendment 不要 (sub-scope 1-Y axis disjoint complement — array ordering convention, Orchestrator verify-before-assert axis 와 다름, sub-scope 1-S/1-V precedent 답습). Wave 1 declarative-only — Wave 2 mechanical wire (scripts/lib/check_adr_amendment_array_ordering.py + templates/github-workflows/adr-amendment-array-ordering.yml + bats + label-registry MINOR `hotfix-bypass:adr-amendment-array-ordering` + evidence-checks-registry entry) = CFP-1613-W2 별 sub-CFP carrier. precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 25 prior Amendment Wave 1→Wave 2 split chain. ADR-064 §결정 5 CFP scope unitary. ADR-054 §결정 1 doc-only fast-path 적격 (단일 PR, scripts/tests 무변경). META-self-applied: 본 Amd 36 = sub-scope 1-Y 첫 적용 사례 — 본 carrier 가 id-ascending convention 을 자신의 amendments[] + amendment_log[] row append 에 적용 (max=35 → next-slot=36 id ascending 최하단 append). source command verify `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-write-time-self-write-verification-mandate.md | tail -1` actual = `amendment_id: 35` (Amd 35 CFP-822 점유) → 정확 next-slot for CFP-1613 = 36 [verified]. dual-block parity: 본 Amd 36 의 amendments[] + amendment_log[] + body ## Amendment 36 3-block parity 보존 (Amd 32 sub-scope 1-U dual-block gate self-application 정합)."
  - amendment_id: 37
    carrier_story: CFP-2383
    date: 2026-06-20  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-Z (신설)", "mechanical_enforcement_actions[] spawn-prompt-fact-verify (status flip)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A~1-Y) → (1-Z spawn_prompt_fact_verify_wave2_wire_ssot) 신설 (ADR-058 §결정 5 강화 방향 — sub-scope 1-L declaration-only 의 Wave 2 mechanical enforcement wire SSOT codify, forbid scope 축소 0). Epic CFP-2380 S3.
    note: "CFP-2383 carrier (Epic CFP-2380 S3) — sub-scope 1-L (Amd 23, CFP-1590) Wave 1 declaration-only → Wave 2 mechanical wire SSOT. `spawn-prompt-fact-verify` PR-body-proxy static presence-only lint binding (Phase 1 = ADR + mechanical_enforcement_actions[] entry status flip; Phase 2 = 실 script/workflow/test/registry detect_command·workflow 실파일·label-registry MINOR 구현 lane). 설계 결정 5종: (1) wire 메커니즘 = S2(`issue-body-claim-pre-screen`) 구조 답습 (line-by-line in_fence toggle + strip_inline_code + PER_BLOCK_SCAN_CAP=50 + ANNOTATION_MARKER 정적 substring `[verified-via:` + exit 0/1/2) + 삭제된 1-W source `c84fadf3:scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py` C1-C5 PATTERNS (counter/version/SHA/verify-result/file-existence, ReDoS-safe) 이식 + trigger/event/body-source = `tier-downgrade-guard.yml` 답습 (pull_request event + paths filter + permissions contents:read,pull-requests:read + env-injection only, inline 보간 금지). (2) 1-W orphan = de-bloat 제거 유지 (복원 금지 = ADR-058 ratchet 위배), 본 wire = 1-L 최초 배선. axis disjoint 보존 (1-L worker→worker / 1-W Orchestrator→subagent). (3) PR-body-proxy 한계 명시 (실 spawn prompt 아닌 proxy, inherit fact transcribe 케이스만 검출) + warning-tier advisory (blocking 승격 시 `[verified-via:` 위조 false-PASS 구조적 가능 → 보안 통제 신뢰 금지). (4) FP guard 4종 EXEMPT (in_fence/inline/blockquote/SELF_SOURCE). (5) deferral 2건 명문화 — retro-fact-verify-mandate (Amd 31/sub-scope 1-T, CFP-1684 — cross-repo docs/retros internal-docs repo wrapper CI surface 0, 거짓 inventory 위험) + fix-loop-reverify-mandate (Amd 29/sub-scope 1-R, CFP-1683 — 3 field amendment_slot_revalidated/registry_version_revalidated/bypass_count_revalidated 가 fix-event-v1 schema 미영속, static lint = schema MINOR bump 선행 의존 본 Story scope 초과) wire 안 함, 양 entry status retain (ADR-082 ratchet 삭제 불가) + #2166 부분 close (잔여 = 외부지식 source: annotation lint + 수치 측정방법 명기, 별 carrier vs 본 Story 흡수 좌표). 동인 = CFP-2380 S1 deferred-followup-reconcile FLAG 2건 중 CFP-2383 가 해소하는 유일 대상 FLAG (firsthand: `bash scripts/check-deferred-followup-reconcile.sh` → spawn-prompt-fact-verify count=3/3 auto_blocking [verified]; 별 1건 stale-local-main-checkout-divergence-check 8/3 = 별 carrier scope 외). paired sibling ADR-073 Amendment 不要 (sub-scope 1-Z axis disjoint complement — 1-L mechanical wire, worker→worker axis ≠ Orchestrator verify-before-assert axis, 1-N/1-P precedent 답습). precedent 답습 ADR-082 §결정 6 + ADR-070 §D5 + ADR-076 §결정 6 + ADR-081 §D5 + 26 prior Amendment Wave 1→Wave 2 split chain + S2(Amd 20 CFP-1559) 동형 직전 precedent. ADR-058 §결정 5 ratchet 강화 only (sub-scope 25→26). ADR-060 §결정 5 warning mode first wire. ADR-054 §결정 1 doc-only fast-path 적격 (Phase 1 단일 PR, scripts/tests 무변경 — change-plan 면제, CFP-2381/CFP-2382 precedent firsthand: `ls docs/change-plans/ | grep -i 238x` → 0건 [verified]). META-self-applied: 본 Amd 37 = sub-scope 1-Z 첫 적용 — id ascending (max=36 → next-slot=37, source command `grep -oE '^  - amendment_id: [0-9]+' archive/adr/ADR-082-*.md | tail -1` actual = amendment_id: 36 [verified]) + dual-block parity (amendments[] + amendment_log[] + body ## Amendment 37 3-block 보존)."
  - amendment_id: 38
    carrier_story: CFP-2646
    date: 2026-07-13  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 16 (신설)", "mechanical_enforcement_actions[] resource-safety-claim-proof-presence (declarative anchor → Phase 2 wire)"]
    nature: ratchet-up  # write-time verify super-class scope → resource-safety-claim artifact class presence-lint carrier 3번째 신설 (ADR-058 §결정 5 강화 방향 — §결정 15 issue-body / §결정 11 code-level 에 이어 3번째 carrier, forbid scope 축소 0). 원천 CFP-2635 retro escalate_user 후보 A.
    note: "CFP-2646 carrier — §결정 16 신설: governance/보안 tooling docstring·주석·워크플로 YAML 주석의 resource-safety/DoS-guard 안전성-claim → paired proof-reference OR honest-ceiling presence write-time 정직 discipline. 원천 = CFP-2635 retro escalate_user 후보 A (pattern_count 2 = CFP-2635 masking tool docstring O(n²) DoS over-claim [scripts/lib/check_shell_test_masking.py:30 정정 커밋 verbatim] + CFP-2591 carrier-lint 주석 ReDoS over-claim [git show 9c13ebbc], ADR-045 §D-9 forcing function). 도메인 본질 = 자기참조 정직 갭 — over-claim/false-coverage 잡는 dogfood governance tool 이 자기 코드에서 동종 over-claim, 보안테스트 lane 이 write 후 늦게 catch (좌향 실패). obviation(Story §2.1 3-way CONFIRM): ethos(ADR-119) 조사범위 커버·detection(보안테스트 execution-backed probe) 2/2 유효·ceiling(ADR-151 §결정7) 상속 — 잔여 = write-time 정직 forcing 부재(registry 0건). 2-layer 충당: Layer 1 = write-time declaration mandate(roster/skill prose, governance-tool 작성 주체 SecurityArch/dev/QADev 안전성-claim 시 proof-ref 동반 또는 ceiling downgrade 행위 mandate, ADR-140 §결정3 hybrid 착지 — 행위는 정적 계측 불가 AC-1a declared + 리뷰 falsify) / Layer 2 = presence lint 5-piece chain(Python SSOT scripts/lib/check_resource_safety_claim_proof.py + thin wrapper scripts/check-resource-safety-claim-proof.sh + byte-identical workflow pair templates/github-workflows+/.github/workflows resource-safety-claim-proof-presence.yml [ADR-005, injection-safe pull_request+contents:read+vars.CI_RUNS_ON_LINUX_JSON self-hosted] + discriminating self-test tests/scripts/test_check-resource-safety-claim-proof.sh + registry warning-tier entry resource-safety-claim-proof-presence + hotfix-bypass:resource-safety-claim-proof-presence label + grandfather baseline docs/resource-safety-claim-baseline.yaml new-only subtract). 알고리즘 = claim closed-set(6키워드 base 확장) affirmative-context 검출(check-tier-honesty.py:8-9,57-58 긍정-토큰 closed-set 매칭 답습 — 정직한 부정 서술·정의부·정책 열거 EXEMPT, raw grep 금지) → 동일 파일 claim-adjacent paired proof-ref OR ceiling presence(issue-body-claim-pre-screen.py:51,54,70 EXEMPT guard+scan cap 구조 답습) → 부재 시 FLAG → grandfather subtract(legacy 27-file 동결, new-only). ★ 자기참조 DoS 회피(메타-재귀, CFP-2635 교훈): 위협축 enumeration 에 T-2 algorithmic-complexity + T-3 line-length 명시(CFP-2635 SF-1 이 정확히 이 두 축 누락 → O(n²) 1.5MB 단일라인 >60s) + born-safe 4-axis bound(T-1 anchored bounded regex nested-quantifier 0 / T-2 index-advance O(n) tokenize slice-in-loop 0 = check_shell_test_masking.py:235-252 답습 / T-3 MAX_PHYSICAL_LINE_LEN per-physical-line truncate = PER_FILE_SCAN_CAP count-cap 과 별개 축 / T-4 islice read cap, 총 작업량 ≤ cap×line-len 유한 bound) + 자기 docstring 정직(자기 resource-safety over-claim 금지, presence≠truth, bounded degradation, ADR-151 ceiling 상속). §8 discriminating self-test = over-claim(proof/ceiling 무) 검출 / honest denial('봉인 아님') 미검출 / proof-linked 미검출 / honest-ceiling downgrade 미검출 + mutation-kill(검출/부정문-EXEMPT/evidence-presence 로직 load-bearing) + DoS 회귀가드(1.5MB 단일라인 bounded-time) + ★ AC-3 self-application(본 Story 산출물 5종 = lint docstring/ADR §결정16/change-plan/Story §7/mandate 문구 전량 lint self-PASS — 요구사항 단계 self-referential 결함 2회 재발 대응, 자기 over-claim 시 자기 게이트 hit). A2-5 = 신규 ADR 아님(ADR-082 Amendment 정합) — disjoint 축(verify⊋presence)은 §결정 15/11 presence-lint carrier 가 ADR-082 안에 이미 해소(presence = verify 의 honesty-ceiling 기계 floor). ADR-119 §결정 specialize / ADR-140 흡수 / ADR-151 AC-7 확장 3 대안 = subject/axis disjoint 로 기각(Story §3 정합), ADR-082 = 최근접 home. Phase 1 = ADR Amendment + write-time mandate roster prose + registry declarative anchor(mechanical_enforcement_actions[] resource-safety-claim-proof-presence status flip) + change-plan; Phase 2 = 실 5-piece mechanical wire + registry status Active + label-registry MINOR. tier = warning-tier(ADR-060 §결정5) — blocking 승격은 별 named carrier(FP 실측 evidence-gate 후, CFP-TBD 금지). Live deputy(LiveOps/LiveOrdering/ProductionEvidence) N/A(wrapper-self governance, real funds/live exchange/production credential 0). InfraOp §7.4 N/A(정적 CI lint, long-running/stateful/worker/restart-aware 4조건 모두 N — §8.5_active false). schema 변경 0(§11 데이터 마이그레이션 N/A). ADR-058 §결정 5 ratchet 강화 only. ADR-054 §결정 1 doc-only fast-path 부적격(Phase 2 script/workflow/test wire 有 — change-plan 작성, CFP-2635 5-piece 선례 동형). precedent 답습 ADR-082 §결정 15(CFP-1559 Wave1 → CFP-2382 Wave2 issue-body-claim-pre-screen) + §결정 11(code-level) + ADR-060 Amendment 22(CFP-2635 shell-test-masking 5-piece 동형). META-self-applied(§결정 10.D): 본 Amd 38 = §결정 16 첫 적용 — id ascending(max=37 → next-slot=38, source `grep -oE '^  - amendment_id: [0-9]+' archive/adr/ADR-082-*.md | tail -1` actual = amendment_id: 37 [verified 2026-07-13 KST worktree cfp-2646-req base 6.82.0]) + dual-block parity(amendments[] + amendment_log[] + body ## Amendment 38 3-block 보존). Orchestrator commit-time max+1 재검증 의무(병렬세션 Amendment 점유 시 reslot)."
related_stories:
  - CFP-776  # carrier (super-class 통합 결정 — escalation_action escalate_user)
  - CFP-841  # Amendment 1 carrier (§결정 6 behavioral→mechanical 전환 후속 carrier)
  - CFP-1016 # Amendment 2 carrier (§결정 1 layer 1 Orchestrator scope Issue-body verify 확장)
  - CFP-1041 # Amendment 3 carrier (ADR-085 disjoint complement — verify axis ↔ coordination axis cross-ref)
  - CFP-1110 # Amendment 5 carrier (§결정 1 layer 1 sub-scope (1-C) Lane PL spawn prompt user-utterance verbatim anchor — 사용자 직권 minimal path first application, paradox-break)
  - CFP-1198 # Amendment 6 carrier (§결정 2 scope (b) 확장 + §결정 9 신설 — amendment 번호 citation plan-time staleness 차단 forcing function, ADR-045 §D-9 Mandatory escalation 산물)
  - CFP-1312 # Amendment 7 carrier (§결정 9 scope 양방향 확장 forward → forward+backward + CFP-1216 lint Check (b) backward-staleness wire — Wave 1 mechanical lint Check (b) coverage gap 보강 dual-carrier, ADR-045 §D-9 pattern_count 3 reach Mandatory escalation 산물)
  - CFP-1293 # Amendment 7 evidence #3 occurrence (ADR-083 Amendment 2 backward-staleness — Wave 1 behavioral mandate land 후 발생 mechanical lint coverage gap escape)
  - CFP-1332 # Amendment 10 carrier (§결정 12 신설 — RequirementsPL §2.1 verified state table mandate strengthening + retro-time wave_defer empirical verify, lifecycle expansion axis)
  - CFP-1000 # Amendment 10 §결정 12.A evidence (Issue body INVERSE drift, pattern_count 2 reach)
  - CFP-1001 # Amendment 10 §결정 12.A evidence (Issue body lint output FP, pattern_count 2 reach)
  - CFP-1006 # Amendment 10 §결정 12.B evidence (Wave-defer rationale falsified post-merge)
  - CFP-1025 # Amendment 10 §결정 12.B evidence (corrective closure pattern WORKING)
  - CFP-1216 # Amendment 7 dual-carrier sibling (CFP-1198 Phase 2 sub-carrier 점유 land — naming SSOT amendment-number-frontmatter-verify, Amendment 7 = Check (b) extend)
  - CFP-1329 # Amendment 8 carrier (§결정 10 신설 — ArchitectAgent write-time discipline 4 sub-scope A/B/C/D: Codex TP#2 8-anchor mirror / mid-author revert propagation / script-behavior claim verify / META self-application, 4 memory entry normative 승격 carrier, pattern_count evidence 혼합 ratchet ADR-064 §결정 7 symmetric)
  - CFP-795  # §결정 10.A evidence #1 sentinel (Codex TP#2 inline FIX 8-anchor mirror coverage checklist forward-prevention, dogfood inversion P1 prevention 도구적 가치)
  - CFP-1009 # §결정 10.B evidence #1 sentinel (mid-author partial revert propagation gap dogfood inversion P1, ADR-074 carrier ADR 자체 같은 defect 보유)
  - CFP-1006 # §결정 10.C evidence #1 (F-DR-1006-1 parse-hotfix-bypass-labels.py script behavior claim P2 dogfood gap)
  - CFP-1025 # §결정 10.C evidence #2 (Orchestrator hypothesis REFUTED by ArchitectPL empirical verify, pattern WORKING dogfood win)
  - CFP-1016 # §결정 10.D evidence #1 (ADR-082 Amendment 2 META-self-applied 1st occurrence — issue_origin frontmatter + §2.1 verified state table)
  - CFP-1340 # §결정 10.D evidence #2 (Amendment 2 §결정 15 Orchestrator-monopoly Story-file inline whitelist 5번째 entry META-self-applied 2nd occurrence — Story file initial scaffold + §9.1 verdict inline write)
  - CFP-1330 # Amendment 9 carrier (§결정 11 신설 — Code-level write-time discipline 2 sub-scope A/B: test code production binding verify + script error visibility audit, 2 memory entry normative 승격 carrier sentinel forward-prevention rationale)
  - CFP-1025 # §결정 11.A evidence #1 sentinel + §결정 11.B evidence (F-CR-1025-2 test tautology + 2-layer error-mask root cause META-ROOT, bootstrap-labels.sh:53-55)
  - CFP-746  # pattern corpus #1a/#1b (corpus slip + 정정-2nd-slip)
  - CFP-770  # pattern corpus #2/#3 (§9 evidence stale + Phase 0 cross-plugin 추정)
  - CFP-1000 # Amendment 2 corpus #4 (Issue body 3 inversions: prod-cutover-deputy-evidence INVERTED + baseline stale + path incorrect)
  - CFP-1001 # Amendment 2 corpus #5 (Issue body L189 lint output verbatim FP transcribe)
  - CFP-1002 # Amendment 2 corpus #6 (Issue body ADR-054 filename missing 'story' word)
  - CFP-1336 # Amendment 14 carrier (§결정 1 layer 1 sub-scope 1-D 신설 — cross-repo label-write authority verify mandate, CFP-1302 follow-up F2 carrier D-4 chief dissent carry, ADR-073 Amendment 9 + ADR-066 Amendment 4 paired carrier, FIX iter 4 FINAL per ADR-067 max 3/3 cap EXCEED + user explicit continuation override)
  - CFP-1302 # Amendment 14 origin (D-4 chief dissent — cross-repo wrapper Issue ↔ impl repo PR labels bidirectional sync 영역 별 carrier 분리 요청)
  - CFP-1339 # Amendment 12 sibling (PMOAgent retro batch closure pattern §결정 14, CFP-1336 spawn 도중 mid-flight land — amendment_number_stale_at_planning 7-reach evidence)
  - CFP-1437 # Amendment 15 carrier (§결정 1 layer 1 sub-scope 1-E 신설 — spawn prompt SHA-anchor write-time verify mandate, CFP-1389 Sub-CFP A Wave 1 declarative-only Pre-spawn HEAD-pin protocol mechanical lint Epic carrier, paired sibling ADR-073 Amendment 11 §결정 1 transition trigger `spawn_prompt_emit`, CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence preventive solution carrier — chief author / deputy stale-at-planning 차단 forcing function)
  - CFP-1389 # Amendment 15 origin (CFP-1336 retro follow-up Pre-spawn HEAD-pin protocol mechanical lint Epic — Wave 1 = CFP-1437 declarative-only Sub-CFP A carrier, Wave 2 mechanical wire = 별 sub-CFP carrier)
  - CFP-1436 # Amendment 16 carrier (§결정 1 layer 1 sub-scope 1-F 신설 — spawn-internal periodic origin re-pin protocol, CFP-1389 Sub-CFP B Wave 1 declarative-only Mid-flight rebase auto-detection mechanical lint Epic carrier, paired sibling ADR-073 Amendment 12 §결정 1 transition trigger `mid_spawn_origin_drift_detected`, reactive complement to Sub-CFP A CFP-1437 preventive — 2-layer defense forcing function 완결 (pre-spawn pin + mid-spawn drift detection))
  - CFP-1435 # Amendment 17 carrier (§결정 1 layer 1 sub-scope (1-G) — amendment-slot pre-reservation strict claim, Sub-CFP C of CFP-1389 paired sibling Sub-CFP A CFP-1437 + Sub-CFP B CFP-1436, 3-layer defense forcing function 완결)
  - CFP-1342 # Amendment 18 carrier (§결정 1 layer 1 sub-scope (1-H) — Orchestrator self-write §10 FIX Ledger row resolution field claim source/evidence verify mandate. CFP-1316 retro F2 Optional carrier — S6 Theme 5 quartet. fix-event-v1 contract level write-time semantic truth verify gap closure, Orchestrator monopoly 영역 sub-scope 1-A~1-G 7종 외 axis disjoint extension. doc-only fast-path ADR-054 Cat 1. Amendment 17 sub-scope 1-G pre-reservation strict claim mandate META 1st applied case)
  - CFP-FU-A # Amendment 19 carrier (§결정 1 layer 1 sub-scope (1-I) 신설 — pre-spawn-prompt-finalize verify layer mandate, sub-decision 3 carrier within CFP-FU-A, renumbered from Amd 18 sub-scope 1-H post CFP-1342 mid-flight collision recovery, paired sibling ADR-073 Amendment 13 + 14, 3 ADR Amendment 동시 발의 axis disjoint complement 3-set, parallel session race 11th occurrence escalate_user pattern_count 11 reach Mandatory ADR-045 §D-9 산물 + 12th meta-occurrence collision recovery in-flight evidence)
  - CFP-1420 # Amendment 19 sentinel — parallel session race 11th occurrence (Mega-Epic CFP-1415 Sub-A S1.2, PR #1442 STAND_DOWN_DUPLICATE per #1441 prior merge)
  - CFP-1342 # Amendment 19 collision sentinel — CFP-1342 ADR-082 Amd 18 + sub-scope 1-H collision detected post-PR-#1527-open, recovery via Amd 19 + sub-scope 1-I + rebase on origin/main HEAD ca1c20e (12th meta-occurrence, recursive dogfooding evidence for #1476)
  - CFP-1559 # Amendment 20 carrier (§결정 15 신설 — Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate. 4 sub-pattern closed-set enumeration: PR merge state stale / CFP merge state stale / count number stale / sister carrier origin claim stale. CFP-1216 Phase 2 wired amendment-number-frontmatter-verify lint sub-class extension super-class declarative anchor. paired sibling CFP-1558 = amendment-number sub-class declarative ratchet axis disjoint, 본 ADR Amendment 21 점유 예정. pattern_count 7+ reach Mandatory ADR-045 §D-9 escalation 산물 — CFP-FU-B 3 PIVOT + CFP-1041/1050 lineage 4)
  - CFP-1558 # Amendment 21 carrier (paired sibling — amendment-number sub-class declarative ratchet, ADR-082 Amendment 21 점유 예정 sequential allocation 후 CFP-1559)
  - CFP-1477 # Amendment 20 sentinel evidence — CFP-FU-B Issue #1477 5-defect 3 PIVOT 60% stale rate
  - CFP-1041 # Amendment 20 sentinel evidence — RequirementsPL spawn packet stale claim pattern_count lineage 4
  - CFP-1050 # Amendment 20 sentinel evidence — RequirementsPL spawn packet stale claim pattern_count lineage 4 sister CFP
  - CFP-1578 # Amendment 21 carrier (§결정 1 layer 1 sub-scope 1-J 신설 — cross-repo worktree target authority verify mandate, worktree mis-target 첫 catch carrier, CFP-1539+CFP-1540 batch retro §4.1 #2 mandatory follow-up, ADR-013 dogfood-out + ADR-040 worktree convention 정합 영역 codify gap closure)
  - CFP-1559 # Amendment 21 paired sibling (Amendment 20 carrier — Issue body stale claim pre-screen super-class, axis disjoint with 본 Amd 21 — content verify vs target authority verify, 동시 발의 race)
  - CFP-1539 # Amendment 21 origin (PMOAgent CFP-1539+CFP-1540 batch retro §4.1 #2 mandatory follow-up — wrapper repo worktree mis-target 첫 catch occurrence evidence)
  - CFP-1540 # Amendment 21 origin sibling (PMOAgent batch retro 동인, CFP-1539 paired)
  - CFP-1601 # Amendment 22 carrier (§결정 1 layer 1 sub-scope 1-K 신설 — numeric claim write-time strict claim mandate. 4-step verify-before-write: source command identify / direct execute / claim↔actual cross-verify / write only on match. 6 numeric claim closed-set dimensions: line count / file count / API count / pattern_count / commit count / row count. ADR-045 §D-9 Mandatory escalation 산물 pattern_count 2 reach (CFP-1571 line count drift + CFP-1581 file count drift). META first applied case — spawn packet 자체 안 numeric claim ambiguity catch (sub-scope letter 1-J→1-K 정정 + amendments[] count semantic disambiguation))
  - CFP-1571 # Amendment 22 sentinel evidence #1 (§3.2 line count drift '+93→+101' 3 location 정정 — chief author write-time numeric claim ground truth verify 부재 catch)
  - CFP-1581 # Amendment 22 sentinel evidence #2 (§3.2 file count drift '10→14' actual — pattern_count 2 reach Mandatory ADR-045 §D-9 escalation 산물 forcing function 활성)
  - CFP-1590 # Amendment 23 carrier (§결정 1 layer 1 sub-scope 1-L 신설 — spawn prompt fact verify-before-trust mandate upstream-inherited stale fact super-class. PMOAgent CFP-1523 retro §5 inline ADR draft Orchestrator → ArchitectAgent spawn carry-over, chief author 자율 결정 Option B 채택 (super-class scope expansion vs Option A new ADR fragmentation 회피), 4-tuple primitive upstream-inherited fact 식별 + direct source verify + stale 검출 시 fact-correction marker + verified-via annotation field, 4-layer temporal defense Amd 15+16+18+19 의 content fact axis 5th layer 신설, doc-only fast-path ADR-054 Cat 1 단일 PR + mid-flight CFP-1601 collision recovery: renumber Amd 22→23 + 1-K→1-L on post-merge rebase to origin/main `4c668913`)
  - CFP-1493 # Amendment 23 evidence #1 (S2.3 PR #1520 commit message stale defer 사유 inheritance — '284 MCP call token cost very high' 단언 실 6 atomic 47x over-estimate Confluence REST cascade primitive 미선재)
  - CFP-1523 # Amendment 23 evidence #2 + origin (CFP-1523 carrier PMOAgent retro §5 inline ADR draft anchor + 사용자 spawn prompt fact 4건 모두 stale evidence ADR lane field 1/117 + binding 53 + 142 page + 284 MCP call)
  - CFP-1591 # Amendment 23 evidence #3 (Issue body canonical/sibling 역할 반전 단언 'canonical (codeforge-review) v4.11 vs sibling (wrapper) v4.9' 실 reverse direction ADR-010 §결정 1 canonical-first invariant 위배 detect)
  - CFP-1589 # Amendment 24 carrier (§결정 1 layer 1 sub-scope 1-M 신설 — own-author synthesis 보고 vs actual git commit gap verify mandate. F-DR-003 carrier CFP-1523 retro carry-over. 4-tuple primitive: synthesis 보고 시점 actual git commit verify + review-verdict-v4 packet 안 optional artifact_commits[] field 영역 + Story §14 Lane Evidence row append 시 actual commit verify + synthesis_vs_commit_gap_verified bool annotation. axis disjoint from Amd 23 1-L upstream-inherited stale fact (input verify) ↔ 본 1-M own-author synthesis 결과 vs actual artifact gap (output self-verify). pattern_count 1 deferred-followup Wave 1 declaration-only mandate.)
  - CFP-1523 # Amendment 24 origin evidence (F-DR-002 P0 finding Phase 1 ArchitectPL verdict packet 'Artifacts written: ...' 보고 ≠ actual git commit, DesignReviewPL audit verify-before-trust direct git status verify 후 detect, FIX iter 1 dispatch — origin pattern_count 1)
  - CFP-1612 # Amendment 25 carrier (§결정 1 layer 1 sub-scope 1-N 신설 — numeric claim write-time verify Wave 2 mechanical enforcement wire. Issue #1612 HIGH FU-A from CFP-1601 retro carrier — 1-K Amd 22 Wave 1 declaration-only mandate 의 mechanical lint enforce. 4-tuple primitive: Python SSOT lint per ADR-061 + 6 dimension detection logic + FP guard 4종 + workflow + bypass + evidence-checks-registry warning-tier initial registration. Wave 1 본 Amendment = declarative SSOT (ADR Amendment + ADR-RESERVATION + evidence-checks-registry + label-registry-v2 MINOR + MANIFEST + CHANGELOG); Wave 2 별 sub-carrier = actual script/workflow/bats wire. precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589 Wave 1→Wave 2 split 11번째 instance. META-self-applied (§결정 10.D 20th + Amendment 17 §결정 1-G 6th + Amendment 22 §결정 1-K 1st applied for Wave 2 wire carrier + Amendment 23 §결정 1-L 1st applied recursive dogfooding mid-flight collision recovery 3rd applied after CFP-FU-A Amd 19 + CFP-1590 Amd 23 — initial spawn pinned origin/main f2e78b16 + amendments[] max=23 → CFP-1589 Amd 24+1-M merge 후 base shift to 5b5c9f7b + max=24 → renumber Amd 24→25 + sub-scope 1-M→1-N on rebase).
  - CFP-1601 # Amendment 25 origin carrier (sub-scope 1-K Amd 22 Wave 1 declaration-only mandate — 본 Amendment 25 Wave 2 mechanical enforcement wire 의 Wave 1 SSOT base, Issue #1612 HIGH FU-A 의 origin)
  - CFP-1637 # Amendment 26 carrier (§결정 1 layer 1 sub-scope 1-O 신설 — PR commit message + PR body 안 numeric claim write-time strict claim mandate 3rd axis declaration-only Wave 1, axis disjoint from 1-K write-time governance docs scope + 1-N Wave 2 mechanical wire scope. Pattern 2 meta-self-application-accuracy-violation pattern_count 2 reach Mandatory escalation 산물 — CFP-1601 §13.C row 3 Story scope 11 vs 15 + CFP-1612 PR #1631 commit msg LOC 29/~470/~155 vs 30/605/183. 3-axis disjoint matrix codify: 1-K governance docs scope + 1-N Wave 2 mechanical wire scope + 본 1-O PR-level artifact scope 3rd axis.)
  - CFP-1647 # Amendment 27 carrier (§결정 1 layer 1 sub-scope 1-P 신설 — sub-scope 1-O Wave 2 mechanical enforcement wire SSOT, declaration-only behavioral mandate 1-O 의 mechanical lint enforce. Issue #1647 HIGH FU-A from CFP-1637 retro carrier — Python SSOT `scripts/lib/check_numeric_claim_write_time.py` scope 확장 to PR commit msg + PR body detection layer, current Wave 2 mechanical wire (CFP-1612 wired) 의 scope expansion. 4-quadrant matrix: 1-K governance docs declaration / 1-N governance docs Wave 2 wire / 1-O PR-level artifact declaration / 1-P PR-level artifact Wave 2 wire. precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589/1612/1637 Wave 1→Wave 2 split 13번째 instance. META 22nd applied case.)
  - CFP-1637 # Amendment 27 origin carrier (sub-scope 1-O Amd 26 Wave 1 declaration-only mandate — 본 Amendment 27 Wave 2 mechanical enforcement wire 의 Wave 1 SSOT base, Issue #1647 HIGH FU-A 의 origin)
  - CFP-1648 # Amendment 28 carrier (§결정 1 layer 1 sub-scope 1-Q 신설 — ADR dual-block parity 3-invariant forward-prevention lint, F-DR-001 P0 origin sentinel mechanical carrier. Issue #1648 MEDIUM follow-up from CFP-1637 retro. Combined Phase 1+2. META-self-applied: amendments[] + amendment_log[] + body 3-block parity 동시 write = recursive dogfooding integrity verify.)
  - CFP-1637 # Amendment 28 origin carrier (F-DR-001 P0 origin: Amendment 26 amendment_log[] entry present but body section missing — CFP-1637 retro 발견, 본 Amendment 28 forward-prevention lint 의 sentinel evidence)
  - CFP-1683 # Amendment 29 carrier (§결정 1 layer 1 sub-scope 1-R 신설 — mid-Story FIX-loop re-verification mandate, sibling axis disjoint from 1-G Story-start pre-reservation)
  - CFP-1688 # Amendment 30 carrier (§결정 1 layer 1 sub-scope 1-S 신설 — ADR frontmatter block convention SSOT codify + sub-scope 1-Q single-block ADR 면제 scope clarification. CFP-FU-C from CFP-1680 retro Pivot 1 root cause. single-block (amendment_log[] only e.g. ADR-045) vs dual-block (both e.g. ADR-082) convention 명문화 + 1-Q lint single-block mode (Block 1/3 skip) + body H2/H3 both-level detection scope correction. lint scope correction = 기존 adr-dual-block-parity entry + hotfix-bypass:adr-dual-block-parity label 재사용, 신규 entry/label 0. Combined Phase 1+2 develop lane dispatch.)
  - CFP-1680 # Amendment 30 origin (CFP-1680 retro Pivot 1 root cause — sub-scope 1-Q lint false-positive on single-block ADR-045, CFP-FU-C #1688 escalation)
  - CFP-1648 # Amendment 30 sibling (sub-scope 1-Q lint origin Amendment 28 carrier — 본 Amendment 30 = 1-Q scope correction, dual-carrier naming SSOT adr-dual-block-parity)
  - CFP-1734 # Amendment 32 carrier (§결정 1 layer 1 sub-scope 1-U 신설 — sub-scope 1-Q dual-block parity lint scope 를 dual-block-only ADR 로 narrow. CFP-FU from CFP-1688 #1734 + user Option A 결정. Amendment 30 sub-scope 1-S Fix A (single-block amendment_log[]-only → Block 2 만) supersede → single-block 양방향 + amendments[]-only + parens-convention + no-amendments 면제, dual-block ADR (amendments[] AND amendment_log[] both present, 예 ADR-082) 만 Block 1/2/3 적용. 동인 = Orchestrator verify-before-trust ADR census 82 frontmatter-amendment ADR 중 lint 검출 39 / parens-convention `## §결정 N (Amendment M)` 미검출 35 (예 ADR-071) convention diversity mismatch. lint scope correction = 기존 adr-dual-block-parity entry + hotfix-bypass:adr-dual-block-parity label 재사용, 신규 entry/label 0. Combined Phase 1+2 develop lane dispatch.)
  - CFP-1688 # Amendment 32 origin (sub-scope 1-S Fix A single-block mode origin — 본 Amendment 32 = 1-S Fix A supersede (single-block-Block-2 → single-block-EXEMPT), dual-block gate narrow)
  - CFP-1787 # Amendment 33 carrier (§결정 1 layer 1 sub-scope 1-V 신설 — execution_context_reconciliation, verdict packet 5 sub-field declare 의무. cluster anchor pattern_count 4 reach (CFP-1735/1753/1755/1764 §6/§4.5) ≥ ADR-045 §D-9 Mandatory threshold 2 escalation 산물. CFP-1764 §4.5 audit packet origin. Wave 1 declarative + Wave 2 mechanical wire single PR — scripts/lib/check_execution_context_state.py + workflow + bats + label-registry-v2 v2.84→v2.85 MINOR `hotfix-bypass:execution-context-state-presence` 110번째 family + evidence-checks-registry warning-tier entry. 5 field: working_dir_abs_path / target_write_repo / staged_files_required[] / branch_required / remote_sync_required — 3 derivable + 2 novel. axis disjoint from sub-scope 1-A~1-U.)
  - CFP-1764 # Amendment 33 audit packet origin (§4.5 carrier — cluster anchor 4번째 occurrence self, CFP-1735+1753+1755 §6 reserved 3-tuple 통합 audit-from-cfp-1764-retro)
  - CFP-1735 # Amendment 33 sentinel evidence #1 (§6 reserved cluster anchor 1st — sub-scope 1-V candidate carrier)
  - CFP-1753 # Amendment 33 sentinel evidence #2 (§6 reserved cluster anchor 2nd — CFP-1735 §6 통합)
  - CFP-1755 # Amendment 33 sentinel evidence #3 (§6 reserved cluster anchor 3rd — CFP-1735 + CFP-1753 + self §4.4 통합)
  - CFP-1842 # Amendment 34 — sub-scope 1-W `orchestrator_spawn_prompt_fact_verify_before_embed` (Orchestrator-side spawn prompt fact discipline, paired ADR-073 Amd 18). Mandatory ADR-045 §D-9 escalation source — pattern_count 3 reach (CFP-1808 F-005 + CFP-1807 F-002 + META self-evidence).
  - CFP-822  # Amendment 35 — sub-scope 1-X `subagent_self_report_post_task_verify` (Orchestrator-side post-task claim verify discipline, paired ADR-073 Amd 19). HIGH priority 12-day pre-existing #822 carrier. mctrader MCT-189 + MCT-190 origin evidence N=2 reach (2026-05-17, subagent SUCCESS claim 후 actual file 부재 super-class). Wave 1 declarative-only (Wave 2 = CFP-822-W2 별 sub-CFP carrier). 본 carrier scope = wrapper-actionable §2 only (#822 §1 superpowers external + §3 mctrader-hub external defer).
  - CFP-1613 # Amendment 36 — sub-scope 1-Y `amendment_array_ordering_convention` (ADR frontmatter amendments[] + amendment_log[] array row-append ordering SSOT, hybrid: id ascending + reservation_date tie-break). MEDIUM Wave 1 declarative. CFP-1601 retro F-DR-1601-2 P2 paired-sibling-race ordering ambiguity 동인 (CFP-1559 Amd 20 ↔ CFP-1578 Amd 21). sub-scope letter ↔ amendment_id NOT synchronized 명문화 (reslot decouple, CFP-1684 → Amd 31/1-T precedent) + paired-sibling-race row-append decision tree 4-step. axis disjoint vs sub-scope 1-S (block convention) — 1-S sub-domain refinement. Wave 2 = CFP-1613-W2 별 sub-CFP carrier.
  - CFP-2383 # Amendment 37 — sub-scope 1-Z `spawn_prompt_fact_verify_wave2_wire_ssot` (sub-scope 1-L Amd 23 CFP-1590 Wave 1 declaration-only → Wave 2 mechanical wire SSOT). Epic CFP-2380 S3. PR-body-proxy static presence-only lint = S2 issue-body-claim-pre-screen 구조 + 삭제된 1-W source C1-C5 PATTERNS 이식 + tier-downgrade-guard.yml PR-event trigger. warning-tier ([verified-via: 위조 false-PASS 구조적 가능 → 보안 통제 신뢰 금지). 동인 = CFP-2380 S1 deferred-followup-reconcile FLAG 2건 중 spawn-prompt-fact-verify 3/3 auto_blocking (CFP-2383 해소 유일 대상; 별 1건 stale-local-main 8/3 = 별 carrier scope 외). Phase 1 = ADR + mechanical_enforcement_actions[] flip / Phase 2 = 실 script+workflow+test+registry flip+label-registry MINOR 별 구현 lane. deferral 2건 retain (retro-fact-verify-mandate Amd 31/1-T + fix-loop-reverify-mandate Amd 29/1-R) + #2166 부분 close. numeric-claim 1-K↔1-N / S2 Amd 20 precedent 답습.
related_adrs:
  - ADR-073  # Orchestrator cross-repo state / assumption verify (disjoint 보완 — Orchestrator 행위 한정)
  - ADR-070  # Codex external worker output verify (disjoint 보완 — 외부 worker output 한정)
  - ADR-085  # Amendment 3 — disjoint complement (verify axis ↔ coordination axis, ADR-085 §결정 1 5-layer 표 anchor = 본 ADR §결정 1 4-layer 표 verbatim 답습 base)
  - ADR-045  # §D-9 cross_story_pattern_adr_trigger (본 carrier = ADR-045 §D Mandatory escalation 산물)
  - ADR-067  # 결정 1 (max FIX 3/3 reassessment trigger) + 결정 3 (RESET vs escalation 권한) 복합 (§결정 3 정정 재귀 무한루프 cap cross-ref source)
  - ADR-058  # is_transitional + 해소 기준 의무 (false 정합 + self-referential trap 회피 anchor)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무 (governance category — §결정 6 known-limitation binding)
  - ADR-068  # I-5 empirical-source annotation (§결정 2(a) directly analogous mechanical 패턴 — Amendment 1 scope (a) lint 재사용)
  - ADR-064  # CFP scope unitary (단일 super-class = 영역별 분할 아님 — Amendment 1 scope a+d 단일 carrier 근거)
  - ADR-054  # doc-only fast-path 단일 PR (본 Story flow 근거)
  - ADR-024  # Amendment 1 동반 — Amendment 7 (hotfix-bypass:corpus-claim-verify 34번째 / cross-plugin-ownership-verify 35번째 family member)
  - ADR-060  # Amendment 1 동반 — evidence-checks-registry 2 entry warning tier (corpus-claim-verify / cross-plugin-ownership-verify, deferred-followup)
  - ADR-066  # Amendment 14 paired — PAT scope `issues:write` Amendment 4 cross-repo label sync 인가 (CFP-1336 carrier 안 3 ADR paired Amendment)
  - ADR-050  # Amendment 17 cross-ref — Parallel epic conflict coordination (ADR-RESERVATION carrier ADR, amendment slot reservation = fine-grained ADR number reservation extension)
  - ADR-013  # Amendment 21 cross-ref — codeforge family dogfood-out policy (internal-docs SSOT path 정합 영역, wrapper plugin-codeforge ↔ internal-docs cross-repo write-target boundary)
related_files:
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # cross-ref Amendment 1 (disjoint 보완)
  - docs/adr/ADR-070-codex-verify-before-trust.md  # cross-ref Amendment 1 (disjoint 보완)
  - docs/adr/ADR-045-story-retro-mandatory-trigger.md  # §D-9 적용 evidence Amendment 6 (Amendment 1) + pattern_count 3 forcing function (Amendment 2)
  - docs/adr/ADR-RESERVATION.md  # row 82 active (CFP-776)
  - docs/adr/ADR-068-boundary-completeness-invariants.md  # Amendment 1 — I-5 directly-analogous pattern 재사용 backref
  - docs/adr/ADR-024-story-scoped-branch-policy.md  # Amendment 1 — Amendment 7 (2 hotfix-bypass family member)
  - docs/inter-plugin-contracts/label-registry-v2.md  # Amendment 1 — v2.25 MINOR (2 family member)
  - docs/evidence-checks-registry.yaml  # Amendment 1 — corpus-claim-verify + cross-plugin-ownership-verify 2 entry
  - docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml  # Amendment 1 — scope (d) cross_plugin_doc_ownership sub-tree 확장 대상 (Phase 2 carrier, CFP-722 §13.A 실재)
  - CLAUDE.md  # verify-before-trust 단락 ADR-082 신입 + 4-layer 계층 + Amendment 1 cross-ref + Amendment 3 ADR-085 disjoint complement cross-ref
  - docs/orchestrator-playbook.md  # §3.10 + §3.14 cross-ref 1줄 append-safe (Amendment 1) + §3.17 신설 (Amendment 2 — Orchestrator-authored Issue body pre-publish verify mandate)
  - templates/story-page-structure.md  # Amendment 2 — §2.1 verified state table codification + issue_origin frontmatter field 신설 (alternative (a) mechanical-enforceable) + Amendment 3 — frontmatter active_sessions[] field 5-tuple row append (ADR-085 §결정 2)
  - docs/adr/ADR-085-multi-session-collaboration-protocol.md  # Amendment 3 — disjoint complement (verify axis ↔ coordination axis), §결정 1 5-layer 표 anchor = 본 ADR §결정 1 4-layer 표 verbatim 답습 base
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # Amendment 14 paired — Amendment 9 transition trigger `label_change` dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1336 carrier)
  - docs/adr/ADR-066-pat-rotation-policy.md  # Amendment 14 paired — Amendment 4 PAT scope `issues:write` cross-repo label sync 인가 (3 ADR paired Amendment)
  - templates/github-workflows/cross-repo-label-sync.yml  # Amendment 14 동반 — bidirectional sync workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
  - docs/change-plans/cfp-1336-cross-repo-label-sync.md  # Amendment 14 carrier Change Plan (CFP-1336 Phase 1 Story)
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # Amendment 15 paired — Amendment 11 transition trigger `spawn_prompt_emit` dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier)
  - templates/github-workflows/spawn-prompt-head-pin-check.yml  # Amendment 15 동반 — spawn prompt SHA-anchor write-time verify workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
  - <internal-docs>/plugin-codeforge/change-plans/cfp-1437-pre-spawn-head-pin-protocol.md  # Amendment 15 carrier Change Plan (CFP-1437 Phase 1 Story, internal-docs SSOT per ADR-013 dogfood-out policy)
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # Amendment 16 paired — Amendment 12 transition trigger `mid_spawn_origin_drift_detected` dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier)
  - templates/github-workflows/mid-spawn-drift-detection-check.yml  # Amendment 16 동반 — spawn-internal periodic origin re-pin protocol workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
  - <internal-docs>/plugin-codeforge/change-plans/cfp-1436-mid-flight-rebase-detection.md  # Amendment 16 carrier Change Plan (CFP-1436 Phase 1 Story, internal-docs SSOT per ADR-013 dogfood-out policy)
  - docs/adr/ADR-050-parallel-epic-conflict-coordination.md  # Amendment 17 cross-ref — Parallel epic conflict coordination ADR-RESERVATION carrier (amendment slot reservation = fine-grained ADR number reservation extension, CFP-1058 Amendment 4 codify + 본 Amendment 17 forcing function)
  - templates/github-workflows/amendment-slot-reservation-check.yml  # Amendment 17 동반 — Wave 1 declaration-only workflow stub (실 logic = Wave 2 별 sub-CFP carrier)
  - docs/adr/ADR-082-write-time-self-write-verification-mandate.md  # Amendment 20 self-anchor — Issue body stale-claim super-class verify-before-trust pre-screen mandate (§결정 15 신설, super-class extension of CFP-1216 amendment-number-frontmatter-verify sub-class lint)
  - <internal-docs>/plugin-codeforge/change-plans/cfp-1559-issue-body-stale-claim-super-class.md  # Amendment 20 carrier Change Plan (CFP-1559 Phase 1 Story, internal-docs SSOT per ADR-013 dogfood-out policy)
  - <internal-docs>/plugin-codeforge/stories/cfp-1559.md  # Amendment 20 carrier Story file
  - docs/cross-repo-patches/cfp-1559-marketplace-sync.patch.txt  # Amendment 20 동반 — marketplace.json sibling sync patch draft (cross-repo PR per ADR-063 §결정 2 ordering: marketplace 선행 merge)
  - docs/orchestrator-playbook.md  # Amendment 21 — §3.5 sub-section 신설 worktree target authority verify (4-tuple primitive)
  - skills/lane-self-write-boundary/SKILL.md  # Amendment 21 — column 추가 (target authority verify) cross-repo write-target boundary matrix
  - <internal-docs>/plugin-codeforge/change-plans/cfp-1578-worktree-target-authority-verify.md  # Amendment 21 carrier Change Plan (CFP-1578 Phase 1 Story, internal-docs SSOT per ADR-013 dogfood-out policy)
  - templates/github-workflows/worktree-target-authority-verify.yml  # Amendment 21 동반 — Wave 1 declaration-only workflow stub (실 logic = Wave 2 별 sub-CFP carrier)
  - <internal-docs>/plugin-codeforge/retros/2026-05-25-cfp-1523-confluence-ia-real-backfill.md  # Amendment 23 origin — PMOAgent CFP-1523 retro §5 inline ADR draft anchor (Orchestrator → ArchitectAgent spawn carry-over)
  - templates/github-workflows/spawn-prompt-fact-verify.yml  # Amendment 23 동반 — Wave 1 declaration-only workflow stub (실 logic = Wave 2 별 sub-CFP carrier)
  - templates/github-workflows/synthesis-vs-commit-gap-check.yml  # Amendment 24 동반 — Wave 1 declaration-only workflow stub (실 logic = Wave 2 별 sub-CFP carrier, review-verdict-v4 v4.9→v4.10 MINOR `artifact_commits[]` field 동반 carrier)
is_transitional: false
# Wave 1 = behavioral directive only (lane agent write-time self-discipline forcing function).
# Wave 2 (Amendment 1, CFP-841) = §결정 6 behavioral→mechanical 전환:
#   scope 2(a) corpus annotation lint (corpus-claim-verify) + scope 2(d) cross-plugin
#   ownership queryable 영역 확장 (cross-plugin-ownership-verify). 둘 다 status
#   deferred-followup (Phase 1 declare / Phase 2 actual wire — ADR-060 §결정 5 모든
#   신규 entry warning 시작 강제 정합).
# §결정 6 rationale 1 partial-stale 정정 (Amendment 1): scope 2(d) verify source 가
#   "mechanical-queryable registry 형태 부재" 라는 Wave 1 전제는 partially stale —
#   lane-self-write-ownership-matrix.yaml machine_readable_ssot 가 CFP-722 §13.A 로
#   이미 실재 (Story per-section sub-tree 한정). scope 2(d) = 신규 registry 창설 아닌
#   기존 yaml 의 cross-plugin doc-ownership 영역 확장 + lint binding (§결정 6 본문 갱신).
# §결정 2(b)/2(c) = behavioral mandate 영역 유지 (super-class anchor forcing function 보존).
# 본 ADR effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 추가될 때
# mechanical_enforcement_actions[] 갱신 + Amendment 발의 (강화 방향만 — ADR-058 §결정 5 /
# ADR-064 §self-application top-down ratchet 정합).
mechanical_enforcement_actions:
  - action: corpus-claim-verify
    status: deferred-followup     # Phase 1 declare / Phase 2 actual wire (CFP-841 §3.1 carrier)
    target_section: §결정 2(a)    # Story/Change-Plan/ADR corpus enumeration [verified: git show <ref>:<path>] annotation lint (ADR-068 I-5 directly-analogous pattern 재사용)
  - action: cross-plugin-ownership-verify
    status: deferred-followup     # Phase 1 declare / Phase 2 actual wire (CFP-841 §3.2 carrier)
    target_section: §결정 2(d)    # lane-self-write-ownership-matrix.yaml cross_plugin_doc_ownership sub-tree query 1-step lint + §13.B 4-way drift-sync invariant
  - action: amendment-number-frontmatter-verify
    status: deferred-followup     # Phase 1 declare (본 Amendment 6) / Phase 2 actual wire = 별 CFP-1198 Phase 2 sub-carrier (lint script + workflow + bats fixture)
    target_section: §결정 9       # governance artifact 안 ADR/contract amendment 번호 인용 시 target frontmatter amendments: 목록 Read-verify → max+1 사용 + verified-via annotation 의무 lint
  - action: cross-repo-label-sync
    status: deferred-followup     # Phase 1 declare (본 Amendment 14, CFP-1336) / Phase 2 actual wire = 별 sub-carrier (cross-repo-label-sync.yml workflow runtime activation + bats fixture + bidirectional sync state lint)
    target_section: §결정 1 layer 1 sub-scope 1-D  # cross-repo label state 변경 직전 authority verify-before-write mandate (4-tuple primitive a-wrapper→impl / b-impl→wrapper / c-cross-org block / d-verified-via annotation). ADR-073 Amendment 9 §결정 1 transition trigger `label_change` dual-binding.
  - action: spawn-prompt-head-pin-presence
    status: deferred-followup     # Phase 1 declare (본 Amendment 15, CFP-1437) / Phase 2 actual wire = 별 sub-CFP carrier (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry)
    target_section: §결정 1 layer 1 sub-scope 1-E  # spawn prompt SHA-anchor write-time verify-before-write mandate (4-tuple primitive a-`[PRE-SPAWN-ORIGIN-MAIN-SHA: <hex>]` block format / b-SHA spawn-time fresh fetch verify / c-cascade parent→child fresh re-fetch / d-`pre_spawn_pin_verified` annotation). ADR-073 Amendment 11 §결정 1 transition trigger `spawn_prompt_emit` dual-binding. ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent 답습.
  - action: mid-spawn-drift-detection
    status: deferred-followup     # Phase 1 declare (본 Amendment 16, CFP-1436) / Phase 2 actual wire = 별 sub-CFP carrier (subagent runtime hook + lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry)
    target_section: §결정 1 layer 1 sub-scope 1-F  # spawn-internal periodic origin re-pin protocol (4-tuple primitive a-periodic check trigger 매 N file edit/매 Edit/Write tool 호출 후 + git fetch + git rev-parse origin/main 실행 / b-PRE-SPAWN-ORIGIN-MAIN-SHA block 값과 current origin/main SHA 비교 drift comparison / c-drift threshold ≥ N commits behind 초과 시 RETURN early with drift_detected:true flag + payload / d-`mid_spawn_drift_verified` annotation). ADR-073 Amendment 12 §결정 1 transition trigger `mid_spawn_origin_drift_detected` dual-binding. ADR-082 sub-scope 1-E (Amendment 15) anchor block pattern precedent 답습 (pre-spawn pin + mid-spawn re-pin = paired complementary defense).
  - action: amendment-slot-reservation-check
    status: deferred-followup     # Phase 1 declare (본 Amendment 17 CFP-1435) / Phase 2 actual wire = 별 sub-CFP carrier (lint script + workflow yml hydrate + ADR-RESERVATION schema strict validation + concurrent reservation conflict detection + bats fixture + label-registry MINOR + evidence-checks-registry Active entry)
    target_section: §결정 1 layer 1 sub-scope (1-G)       # amendment-slot pre-reservation strict claim mandate — chief author / deputy spawn 전 ADR-RESERVATION amendments_reserved[] row 의무 pre-append + spawn prompt 안 pre_reserved_amendment_slots field 의무 (Sub-CFP C 3-layer defense closure)
  - action: pre-spawn-prompt-finalize-verify
    status: deferred-followup     # Phase 1 declare (본 Amendment 18 CFP-FU-A) / Phase 2 actual wire = 별 sub-CFP carrier (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry)
    target_section: §결정 1 layer 1 sub-scope (1-H)       # pre-spawn-prompt-finalize verify layer mandate — worktree create 후 spawn prompt content 작성 직전 ~30-60s window 안 1회 추가 polling 의무 (git fetch + gh issue list + gh pr list 3-source AND aggregate, race window 단축). paired sibling ADR-073 Amendment 13 transition trigger `pre_git_operation` + `pre_push` + Amendment 14 §결정 1-P AND composition layer (sub-decision 1+2+3 3 ADR Amendment 동시 발의 axis disjoint complement 3-set). parallel session race 11th occurrence escalate_user pattern_count 11 reach Mandatory ADR-045 §D-9 산물.
  - action: issue-body-claim-pre-screen
    status: deferred-followup     # Phase 1 declare (본 Amendment 20 CFP-1559 super-class) / Phase 2 actual wire = 별 sub-CFP carrier (lint script `scripts/lib/check_issue_body_claim_pre_screen.py` Python SSOT per ADR-061 + `scripts/check-issue-body-claim-pre-screen.sh` bash thin wrapper + `templates/github-workflows/issue-body-claim-pre-screen.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-issue-body-claim-pre-screen.bats` fixture RED→GREEN stash proof + ContinuityAgent agent file cross-plugin ADR-010 sibling sync — codeforge-requirements:ContinuityAgent.md verify-before-trust 8-tuple matrix scope expansion + RequirementsPL spawn prompt `issue_body_pre_screen_warnings` field 추가)
    target_section: §결정 15       # Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate — 4 sub-pattern closed-set enumeration (a-PR #NNNN merge state CLOSED/MERGED stale / b-CFP-NNNN MERGED/CLOSED state stale / c-count number stale 예 `X VIOLATIONs` `Y defect` `pattern_count Z` / d-sister carrier origin claim stale 예 `CFP-NNNN carrier`). CFP-1216 Phase 2 wired `amendment-number-frontmatter-verify` lint (sub-class — ADR-NNN Amd M regex citation only) extension super-class declarative anchor. paired sibling CFP-1558 = amendment-number sub-class declarative ratchet axis disjoint (본 ADR Amendment 21 점유 예정). pattern_count 7+ reach Mandatory ADR-045 §D-9 escalation 산물 (CFP-FU-B Issue #1477 3 PIVOT 60% stale rate + CFP-1041/1050 RequirementsPL spawn packet stale claim lineage 4 = 합산 ≥ 7).
  - action: worktree-target-authority-verify
    status: deferred-followup     # Phase 1 declare (본 Amendment 21 CFP-1578) / Phase 2 actual wire = 별 sub-CFP carrier (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry)
    target_section: §결정 1 layer 1 sub-scope (1-J)       # cross-repo worktree target authority verify mandate — spawn prompt 작성 또는 직접 file write 직전 worktree target authority verify-before-write 의무 (4-tuple primitive a-`git -C <worktree_abs_path> remote -v` expected repo vs actual remote URL 일치 verify / b-spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 / c-cross-repo 작업 sequence 시 명시적 worktree switch — 각 repo 별 worktree 분리 / d-`worktree_target_authority_verified: <bool>` annotation). 동인 = CFP-1539+CFP-1540 batch retro §4.1 #2 worktree mis-target 첫 catch carrier. ADR-013 dogfood-out internal-docs SSOT path + ADR-040 worktree convention 정합 영역 codify 부재 super-class gap closure. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint — content verify vs target authority verify).
  - action: numeric-claim-write-time-verify
    status: warning-tier wire complete (CFP-1612 Wave 2 governance docs scope wired; CFP-1647 Wave 2 PR-level artifact scope expansion declarative — Wave 2 actual script/workflow/bats wire 별 sub-CFP carrier)     # Phase 1 declare (Amendment 22 CFP-1601 Wave 1 declaration-only governance docs scope) → Wave 2 mechanical wire activate (Amendment 25 CFP-1612 — Python SSOT `scripts/lib/check_numeric_claim_write_time.py` governance docs scope wired + evidence-checks-registry warning-tier initial registration + label-registry-v2 hotfix-bypass:numeric-claim-write-time-verify 101st family member + workflow declarative anchor) → 본 sub-scope 1-O Wave 1 declaration-only PR-level artifact scope expansion (Amendment 26 CFP-1637) → 본 Amendment 27 (CFP-1647) Wave 2 mechanical wire SSOT for 1-O scope (Python SSOT scope expansion to PR commit msg + PR body detection layer + workflow PR trigger 확장 declarative anchor; Phase 2 별 sub-carrier = actual script + workflow PR trigger + bats fixture file write — DeveloperPL + QADev spawn)
    target_section: §결정 1 layer 1 sub-scope (1-K + 1-N + 1-O + 1-P)  # 1-K (Amd 22 CFP-1601) = numeric claim write-time strict claim mandate (4-step verify-before-write + 6 dimension closed-set) declaration-only behavioral SSOT governance docs scope / 1-N (Amd 25 CFP-1612) = 1-K Wave 2 mechanical enforcement wire SSOT governance docs scope (Python SSOT lint per ADR-061 + bash thin wrapper + workflow + bypass channel + evidence-checks-registry warning-tier initial registration) / 1-O (Amd 26 CFP-1637) = PR commit message + PR body 안 numeric claim write-time strict claim mandate declaration-only behavioral SSOT PR-level artifact scope 3rd axis (1-K mandate 의 scope target 확장) / 1-P (본 Amd 27 CFP-1647) = 1-O Wave 2 mechanical enforcement wire SSOT PR-level artifact scope (Python SSOT `check_numeric_claim_write_time.py` scope 확장 to PR commit msg + PR body detection layer + workflow PR open + sync trigger 추가 + bats fixture PR commit msg + PR body fixture pair). 4-quadrant matrix codify: governance docs / PR-level artifact × declaration / Wave 2 wire = (1-K, 1-N) governance docs pair + (1-O, 1-P) PR-level artifact pair. 4-step verify-before-write 의무 (a-source command identify (e.g. `grep -c <pat> <file>` / `wc -l` / `git diff --shortstat` / `find ... | wc -l` / `git rev-list --count <range>` / `git log --format=%B <range>` / `gh pr view --json title,body,commits`) / b-direct execute + actual value 획득 (cached/추정/planning-time stale 사용 금지) / c-claim↔actual cross-verify (semantic ambiguity (line-occurrence count vs max amendment_id slot 등) 발견 시 source command 정밀화 의무) / d-write only on match). Numeric claim closed-set 6종: line count / file count / API count / pattern_count / commit count / row count (governance docs + PR-level artifact 양 scope inherit same 6 dimension). 동인 = (1-K + 1-N) ADR-045 §D-9 Mandatory escalation 산물 (CFP-1571 §3.2 line count drift +93→+101 3 location 정정 + CFP-1581 §3.2 file count drift 10→14 actual, pattern_count 2 reach) + (1-O + 1-P) Pattern 2 meta-self-application-accuracy-violation pattern_count 2 reach Mandatory escalation 산물 (CFP-1601 §13.C row 3 Story scope claim 11 vs 15 + CFP-1612 PR #1631 commit msg LOC drift 29/~470/~155 vs 30/605/183). paired sibling axis = Amendment 17 §결정 1-G (row append amendment-slot scope) + Amendment 20 §결정 15 (Issue body content scope, 4 sub-pattern enumeration). META applied cases: Amendment 22 (1-K) 1st = spawn packet 자체 안 numeric claim ambiguity catch / Amendment 25 (1-N) 2nd = mid-flight CFP-1589 collision recovery 3rd + numeric claim 1-K source command 정밀화 self-apply (Amd 24→25 + 1-M→1-N) / Amendment 26 (1-O) = META 21st applied case (CFP-1612 = 20th post-merge → CFP-1637 = 21st sequential carrier) / 본 Amendment 27 (1-P) = META 22nd applied case (Amendment 22 §결정 1-K 3rd applied + Amendment 23 §결정 1-L 2nd applied for spawn packet fact verify + Amendment 24 §결정 1-M 1st applied for inline self-verify recursive dogfooding).
  - action: spawn-prompt-fact-verify
    status: "warning-tier wire SSOT (Amendment 37 CFP-2383 — sub-scope 1-L Wave 2 mechanical wire SSOT declarative anchor; PR-body-proxy static presence-only lint = S2 issue-body-claim-pre-screen 구조 + 1-W C1-C5 PATTERNS 이식 + tier-downgrade-guard.yml PR-event trigger; Phase 2 actual wire = 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D)"     # Phase 1 declare (Amendment 23 CFP-1590 sub-scope 1-L) → Phase 1 Wave 2 wire SSOT (Amendment 37 CFP-2383 sub-scope 1-Z) / Phase 2 actual wire = 별 sub-CFP carrier (단일-root `.github/workflows/spawn-prompt-fact-verify.yml` — single-root, templates/github-workflows/ 미사용 = CONSUMER_ONLY/invariant-check parity 불요; Python SSOT lint per ADR-061 `scripts/lib/check_spawn_prompt_fact_verify.py` + `scripts/check-spawn-prompt-fact-verify.sh` bash thin wrapper + `scripts/test-check-spawn-prompt-fact-verify.sh` discriminating test (S2 동형, file-input surface 실존 증명) + label-registry-v2 MINOR `hotfix-bypass:spawn-prompt-fact-verify` (1-L, ≠ 1-W `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` family-member name 충돌 회피) + evidence-checks-registry detect_command·workflow 실파일 flip ADR-060 §결정 5 warning-tier)
    target_section: §결정 1 layer 1 sub-scope (1-L + 1-Z)       # 1-L (Amd 23 CFP-1590) = spawn prompt fact verify-before-trust mandate declaration-only behavioral SSOT (upstream-inherited stale fact carrier super-class, worker→worker handoff 4 sub-source) / 1-Z (Amd 37 CFP-2383) = 1-L Wave 2 mechanical enforcement wire SSOT (PR-body-proxy static presence-only lint, S2 구조 + 1-W C1-C5 PATTERNS + tier-downgrade-guard PR trigger, warning-tier — blocking 승격 시 [verified-via: 위조 false-PASS 구조적 가능, 보안 통제 신뢰 금지). numeric-claim 1-K↔1-N / S2 §결정 15 issue-body precedent 답습 — Orchestrator 또는 chief author 가 lane agent spawn prompt 작성 시 인용 fact (numeric / state / count / sister carrier claim) 가 (i) 사용자 발화 (ii) sibling Issue body (iii) sister PR commit message (iv) 별 carrier retro file 로부터 inherit 된 경우 직접 verify 의무 + verified-via annotation + stale 검출 시 fact-correction marker + verified-via field 명시. 본 1-L = 4-layer temporal defense (Amd 15 pre-spawn-fetch + Amd 19 pre-spawn-prompt-finalize + Amd 16 mid-spawn-periodic + Amd 18 Orchestrator §10 source-claim) 의 content fact axis 5th layer (when verify vs what verify disjoint). axis 분리 vs Amd 5 1-C (content 전달 형식 axis) + Amd 20 §결정 15 (self-write Issue body stale-claim super-class) + Amd 22 1-K (own author write-time numeric claim source/value strict). 동인 = CFP-1590 ADR-045 §D-9 Mandatory escalation pattern_count 3 reach (CFP-1493 commit message defer 사유 + CFP-1523 사용자 spawn prompt 4 fact + CFP-1591 Issue body canonical/sibling 역할 반전). PMOAgent CFP-1523 retro §5 inline ADR draft Orchestrator → ArchitectAgent spawn carry-over chief author 자율 결정 Option B 채택 + mid-flight CFP-1601 collision recovery (initial Amd 22+1-K → renumber Amd 23+1-L).
  - action: synthesis-vs-commit-gap-check
    status: deferred-followup     # Phase 1 declare (본 Amendment 24 CFP-1589) / Phase 2 actual wire = 별 sub-CFP carrier (Python SSOT lint per ADR-061 `scripts/lib/check_synthesis_vs_commit_gap.py` + `scripts/check-synthesis-vs-commit-gap.sh` bash thin wrapper + `templates/github-workflows/synthesis-vs-commit-gap-check.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-synthesis-vs-commit-gap.bats` fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 `hotfix-bypass:synthesis-vs-commit-gap-check` MINOR bump + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합 + review-verdict-v4 v4.9 → v4.10 MINOR carrier `artifact_commits[]` optional field schema 신설)
    target_section: §결정 1 layer 1 sub-scope (1-M)       # own-author synthesis 보고 vs actual git commit gap verify mandate (F-DR-003 carrier) — ArchitectPL / Dev / lane PL 가 verdict / 산출 / 완료 보고 작성 시점 (a) `git -C <worktree> log --oneline origin/main..HEAD` direct execute actual commit list 확인 의무 (worktree modified/untracked 영역 commit 0건 미포함, 'Artifacts written' = actual commit hash 매핑 의무) / (b) review-verdict-v4 packet 안 optional `artifact_commits[]` field 영역 (40-char hex commit hash array, future MINOR bump 별 sub-CFP carrier) / (c) Story §14 Lane Evidence row append 시 actual commit verify (ADR-073 verify-before-assert + ADR-082 §결정 1 sub-scope 1-M dual binding) / (d) `synthesis_vs_commit_gap_verified: <bool>` field annotation 의무 (write-time semantic truth verify). axis 분리 vs Amd 23 1-L (upstream-inherited input verify) ↔ 본 1-M (own-author output self-verify, synthesis output ↔ git commit downstream). axis 분리 vs Amd 22 1-K (own author write-time numeric claim source/value verify) ↔ 본 1-M (own-author synthesis output ↔ actual artifact gap, numeric 영역 외 artifact identity claim 영역). axis 분리 vs Amd 18 1-H (Orchestrator monopoly §10 FIX Ledger resolution field source/evidence, fix-event-v1 contract axis) ↔ 본 1-M (lane agent self-write own-author axis, lane plugin 영역). 동인 = CFP-1523 carrier F-DR-002 P0 finding (Phase 1 ArchitectPL verdict packet 'Artifacts written: ...' 보고 ≠ actual git commit, DesignReviewPL audit verify-before-trust direct git status verify 후 detect, FIX iter 1 dispatch). pattern_count 1 deferred-followup carrier (Wave 1 declaration-only mandate, ADR-082 §결정 6 retain pattern 답습 — pattern_count 누적 시 follow-up CFP MUST promote).
  - action: execution-context-state-presence
    status: deferred-followup     # Phase 1 declare (본 Amendment 33 CFP-1787) / Phase 2 actual wire = 별 sub-CFP carrier (Python SSOT lint per ADR-061 `scripts/lib/check_execution_context_state.py` + `templates/github-workflows/execution-context-state-check.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/wave2-mechanical-wire/check-execution-context-state.bats` fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 v2.84 → v2.85 MINOR `hotfix-bypass:execution-context-state-presence` 110번째 family member + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합)
    target_section: §결정 1 layer 1 sub-scope (1-V)       # execution_context_reconciliation — PMOAgent / retro write-target / chief author / deputy verdict packet 안 `execution_context_state` 5 sub-field 명시 declare 의무 (a-`working_dir_abs_path` derivable via `pwd` ADR-040 worktree convention 정합 / b-`target_write_repo` derivable via `git -C <wt> remote -v` axis-adjacent disjoint sub-scope 1-J / c-`staged_files_required[]` novel axis intent declaration derive 불가능 / d-`branch_required` derivable via `git branch --show-current` ADR-040 / ADR-024 binding / e-`remote_sync_required` novel axis pre-write intent enum pull/fetch/N/A). 5 field 중 3 derivable + 2 novel — derive primitive cross-ref 본문 표 명시 (ratchet density 보호, ADR-068 I-4 wording SSOT). axis disjoint from sub-scope 1-A through 1-U 22 entry (packet-level execution context state declare axis, paired_sibling_base = Amendment 31 §1-T axis-adjacent supplementary clause). 동인 = cluster anchor pattern_count 4 reach (CFP-1735 §6 + CFP-1753 §6 + CFP-1755 §6 + CFP-1764 §4.5 self) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation. ADR-073 paired Amendment 不要 (sub-scope 1-V axis disjoint complement from Orchestrator verify-before-assert axis). ADR-045 cross-ref only.
  - action: orchestrator-spawn-prompt-fact-verify
    status: deferred-followup     # CFP-1842 Amendment 34 — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 3 / threshold 2 / Mandatory, actual lint script + workflow + bats + label-registry MINOR + evidence-checks-registry entry = CFP-1842-W2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합. Amendment 34 §결정 1 layer 1 sub-scope 1-W carrier — 5종 fact category C1-C5 (counter / version / SHA / verify-result / file-existence) closed-enum verify-before-embed. paired sibling ADR-073 Amendment 18 sub-decision `pre_spawn_prompt_fact_assertion` transition trigger 16번째 entry.
    target_section: §결정 1 layer 1 sub-scope (1-W)       # orchestrator_spawn_prompt_fact_verify_before_embed — Orchestrator 가 subagent (lane PL / chief author / deputy / 4-tuple sub-tuple) spawn 직전 spawn prompt 안 fact 단언 (counter / version / SHA / verify-result / file-existence 5종) 발화 시점 verify-before-embed 의무. 5종 fact category C1-C5 closed-enum: C1 counter / C2 version / C3 SHA / C4 verify-result / C5 file-existence. 5종 모두 spawn prompt embed 직전 direct Read / git api / file system call verify 의무. axis disjoint vs sub-scope 1-L (CFP-1590, worker→worker) — 1-W = Orchestrator→subagent. paired sibling ADR-073 Amendment 18 (transition trigger 16번째 entry `pre_spawn_prompt_fact_assertion`). pattern_count 3 reach Mandatory ADR-045 §D-9: CFP-1808 F-005 + CFP-1807 F-002 + META self-evidence.
  - action: subagent-self-report-post-task-verify
    status: deferred-followup     # CFP-822 Amendment 35 — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 2 / threshold 2 / Mandatory N=2 reach, actual lint script + workflow + bats + label-registry MINOR + evidence-checks-registry entry = CFP-822-W2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합. Amendment 35 §결정 1 layer 1 sub-scope 1-X carrier — 6종 critical artifact category ARTIFACT-1~6 (ADR / Story / RETRO / scope_manifest / spec/plan / code FIX) closed-enum verify-after-receive. paired sibling ADR-073 Amendment 19 sub-decision `post_subagent_task_completion` transition trigger 17번째 entry. origin: #822 HIGH priority 12-day pre-existing + mctrader MCT-189/190.
    target_section: §결정 1 layer 1 sub-scope (1-X)       # subagent_self_report_post_task_verify — Orchestrator 가 subagent (lane PL / chief author / deputy / 4-tuple sub-tuple) "DONE/PASS/MERGED" 보고 receive 후 critical artifact actual existence + content verify-before-trust 의무. 6종 critical artifact category closed-enum: ARTIFACT-1 ADR / ARTIFACT-2 Story / ARTIFACT-3 RETRO / ARTIFACT-4 scope_manifest / ARTIFACT-5 spec/plan / ARTIFACT-6 code FIX. 5종 verify methods: ls + Read line 1-N + wc -l + grep keyword + git status --short. axis disjoint vs sub-scope 1-W (CFP-1842 Orchestrator→subagent pre-spawn fact verify) — 1-X = subagent→Orchestrator post-task claim verify (opposite direction). paired sibling ADR-073 Amendment 19 (transition trigger 17번째 entry `post_subagent_task_completion`). origin pattern N=2 reach: mctrader-hub MCT-189 (subagent SUCCESS claim 후 actual file 부재) + MCT-190 (동형 reproduction 2026-05-17).
  - action: resource-safety-claim-proof-presence
    status: warning-tier wire complete (CFP-2646 Phase 2 — 5-piece mechanical wire, 단일 CFP 양 Phase)     # Phase 1 declare (Amendment 38 §결정 16, CFP-2646) → Phase 2 actual wire: Python SSOT `scripts/lib/check_resource_safety_claim_proof.py` + `scripts/check-resource-safety-claim-proof.sh` thin wrapper + byte-identical workflow pair `resource-safety-claim-proof-presence.yml` (ADR-005 sha256 2224e9fe) + discriminating self-test `tests/scripts/test_check-resource-safety-claim-proof.sh` (14/14 GREEN — TC-OC/HD/PL/CD/EX + MK-1/2/3 mutation-kill + PERF DoS 회귀가드 + AC-3 self-application) + grandfather baseline `docs/resource-safety-claim-baseline.yaml` (legacy 16 pair) + evidence-checks-registry warning-tier entry Active + label-registry-v2 v2.106 `hotfix-bypass:resource-safety-claim-proof-presence` 106th + `docs/selftest-execution-liveness-inventory.yaml` AC-1a 레코드 + Layer 1 roster prose(SecurityArch/dev/QADev/Infra). §결정 16 carrier — write-time verify super-class 3번째 presence-lint carrier. ADR-060 §결정 5 warning-tier 정합.
    target_section: §결정 16       # resource_safety_claim_proof_presence — governance/보안 tooling docstring·주석·워크플로 YAML 주석의 resource-safety/DoS-guard 안전성-claim → paired proof-reference OR honest-ceiling presence 정적 검사 (presence ≠ truth, honesty ceiling ADR-151 §결정 7 상속, verify ⊋ presence disjoint). born-safe 4-axis DoS bound (T-1 리터럴 substring 우선 nested-quantifier 0 / T-2 substring in C-level O(n) / T-3 MAX_PHYSICAL_LINE_LEN per-physical-line truncate=count-cap 별개 축 / T-4 islice read cap) — CFP-2635 SF-1 O(n²) 재발 차단 (self-test PERF-1 실측 1.5MB 단일라인 0.14s). AC-3 self-application (산출물 5종 = lint docstring/ADR §결정16/change-plan/Story §7/Layer1 mandate 전량 self-PASS). axis disjoint vs §결정 15 (issue-body claim) — resource-safety/DoS-guard claim class + docstring/주석/workflow YAML artifact class.
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책). self-referential 주의: 본 ADR 의 해소기준 부재 선언 자체가 §결정 2 verify 대상 아님 (§결정 6 EC-3 self-protection)."
pre_lookup_evidence:
  verified_files:
    - { path: "docs/adr/ADR-073-orchestrator-verify-before-assert.md", verified-via: "git show origin/main", note: "frontmatter amends:null amendments:[] is_transitional:false — 본문 Amendments 섹션 부재 → Amendment 1 신설. disjoint 보완 (Orchestrator cross-repo 한정)" }
    - { path: "docs/adr/ADR-070-codex-verify-before-trust.md", verified-via: "git show origin/main", note: "frontmatter amends:null amendments:[] is_transitional:false — 본문 Amendments 섹션 부재 → Amendment 1 신설. disjoint 보완 (외부 worker output 한정). D5 declaration-only retain 패턴 선례" }
    - { path: "docs/adr/ADR-045-story-retro-mandatory-trigger.md", verified-via: "git show origin/main", note: "amendment_log[] 최대 amendment_id:5 (CFP-665 §D-9) — 본문 Amendments 최대 Amendment 5 → Amendment 6 신설. 본 carrier = §D-9 cross_story_pattern_adr_trigger 산물 (pattern_count 3 ≥ threshold 2, escalation_action escalate_user)" }
    - { path: "docs/adr/ADR-067-fix-ledger-implementability-escalation.md", verified-via: "git show origin/main:docs/adr/ADR-067-fix-ledger-implementability-escalation.md", note: "결정 1 (max FIX 3/3 deterministic implementability reassessment trigger) + 결정 3 (ArchitectPL 재량 RESET vs escalation 결정 권한) 복합 — §결정 3 정정 재귀 무한루프 cap cross-ref source" }
    - { path: "docs/adr/ADR-RESERVATION.md", verified-via: "git show origin/main", note: "row 81 = CFP-819 active (parallel session 점유) / row 82 부재 → ADR-082 번호 가용 확정. row 79/80/81 precedent = reserved 미경유 직접 active" }
    - { path: "CLAUDE.md", verified-via: "git show origin/main / Read working tree", note: "305줄 (cap ≤320 CFP-506, 여유 15줄) / verify-before-trust 단락 = L275 single long line" }
  origin_main_sha: "d0784ae"  # spec/plan 기록 base + 본 PL git fetch origin main 재verify (row 81 CFP-819 parallel 점유 추가분 — §4.3 drift)
  last_git_fetch_timestamp: "2026-05-17T15:40+09:00"  # KST per memory feedback_time_display
---

# ADR-082: Write-time self-write verification mandate — internal lane agent §9 evidence / Phase 0 mapping / corpus enumeration verify super-class

## 상태

Accepted (2026-05-17 KST) — CFP-776 carrier. PMOAgent ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count 3 ≥ threshold 2 산물 (escalation_action `escalate_user` → 사용자 단일 super-class ADR 통합 결정 2026-05-16 KST). doc-only fast-path (ADR-054 단일 PR).

## 본질 선언

lane agent (RequirementsPL / ArchitectAgent / DeveloperPL 등) 가 §9 evidence 작성 / Phase 0 ChangeImpactAgent mapping / Story corpus enumeration 시 **write-time 에 source/value/ownership 을 verify 없이 단언**하는 것을 금지한다. 작성한 **값 자체가 사실과 일치하는가** 를 write 직전 source direct verify 후 write 한다. 본 ADR 이 충족되지 않으면 아래 §결정 mechanism 을 몇 개 쌓든 의미 없다 — 모든 §결정 은 본질을 보조하는 scaffolding.

기존 codeforge governance 의 self-write 검증 layer 는 (1) **write 권한 actor 경계** (`measurement-channel.md` — ledger write = Orchestrator monopoly) + (2) **syntactic ownership** (`lane-self-write-ownership-matrix.md` INV-DI-1/2 — non-owner destructive write / monopoly unauthorized mutation) 만 정의한다. **(3) write-time semantic truth (작성 값이 사실과 일치하는가) verify layer = 명백한 도메인 공백** (verified-via: `git show origin/main:docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.md` + `git show origin/main:docs/domain-knowledge/domain/orchestrator-discipline/measurement-channel.md`, DomainAgent Phase 0 Read — "write-time" / "semantic truth" 키워드 0건 매칭). ADR-082 가 이 (3) layer 신설 anchor.

## 컨텍스트

### pattern corpus (3 누적 — Issue #776 body verbatim)

| # | Story | 발현 | 설명 |
|---|---|---|---|
| 1a | CFP-746 | D-7 설계 corpus slip | 이전 설계 pass 가 "corpus 에 same-repo `story_issues[]` 예시 전무" 단정 → 실제 CFP-275/280/281/282/283 5건 same-repo 보유. factually FALSE corpus 단정 (ADR-052 TP#2 P1-2 적발, ADR-070 Orchestrator verify 확정) |
| 1b | CFP-746 | CFP-531 정정-2nd-slip | D-7 정정이 CFP-531 을 same-repo fixture 6번째 추가 → 실제 CFP-531 frontmatter cross-repo (`github_issue:` only, `story_issues:` block 부재). **정정 행위 자체 미검증** → 2nd unverified-corpus-claim 도입 (ADR-052 TP#2 re-check RESIDUAL P2 적발) |
| 2 | CFP-770 | CR-004 §9 evidence stale | §9 write 시 ADR-079 frontmatter `is_transitional: true` + 해소기준 3-tuple 기재 → 실제 ADR-079:7 `is_transitional: false` / N/A permanent policy. §9 evidence 자체가 source verify 없이 value 단언 |
| 3 | CFP-770 | §결정 8 Phase 0 cross-plugin 추정 | spec/Story §4.0 초안이 "5 template 전부 wrapper-local" 가정 → 실제 wrapper 2 + cross-plugin 3 (codeforge-design `adr.md`/`change-plan.md`, codeforge-pmo `retro.md`). ChangeImpactAgent Phase 0 mapping cross-plugin ownership 미검증 |

PMOAgent ADR-045 Amendment 5 §D-9 정량 임계값: pattern_count **3** ≥ threshold 2 → Mandatory framing + escalation_action `escalate_user` → 사용자 단일 super-class ADR 통합 결정.

### 현 SSOT 결격 영역

- **ADR-073** = Orchestrator 가 cross-repo state / assumption 단정 시 verify + annotation 의무 → *Orchestrator 행위* 한정 (internal lane self-write 미포함, verified-via: `git show origin/main:docs/adr/ADR-073...md` title="cross-repo ground truth + assumption verify mandate" 2026-05-17 KST).
- **ADR-070** = Codex external worker output verify 의무 → *외부 worker(Codex) output* 한정 (verified-via: `git show origin/main:docs/adr/ADR-070...md` title="Codex verify-before-trust pattern (sandbox access invariant)" 2026-05-17 KST).
- **본 super-class gap** = lane agent 가 §9 evidence 작성 / Phase 0 mapping / corpus enumeration 시 **write-time** 에 source/value/ownership 을 verify 없이 단언하는 영역 — 설계 lane, §9 write, Phase 0 agent 모두 ADR-073/070 scope 외.

## 결정

### §결정 1 — Layer disjoint 판정 표 (의무 — PMOAgent 위험 완화)

verify-before-trust governance 는 4 disjoint layer 로 구성된다. 각 layer 는 verify 대상 / 행위 주체가 서로 disjoint 하며, 본 표가 4-layer 의 공통 anchor 다.

| Layer | ADR | verify 대상 / scope |
|---|---|---|
| Orchestrator cross-repo state / assumption verify | ADR-073 | Orchestrator 행위 한정 — cross-repo state + assumption 기술 시 `git fetch` + `git show origin/main:<path>` direct verify + `verified-via` annotation |
| external worker (Codex) output verify | ADR-070 | 외부 worker output 한정 — Codex finding evidence ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject |
| **internal lane agent self-write verify (본 ADR)** | **ADR-082** | **lane agent §9 evidence / Phase 0 mapping / corpus enumeration write-time** — 작성 값 자체가 사실과 일치하는가 source direct verify 후 write |
| retro corpus enumeration (PMOAgent §5 pattern_count) | ADR-045 §D | retro pattern aggregation — cross-Story pattern_count ≥ threshold 검출 시 ADR escalation forcing function |

> **4-layer 충분 (5th row 불요)**: ADR-078 (CFP-756 design doc lifecycle living design doc) 는 verify-before-trust 와 별 axis (영속 구조 문서 lifecycle ≠ write-time semantic truth) 이며 origin/main 미존재 (verified-via: `git ls-tree origin/main docs/adr/` → ADR-078 file 부재 2026-05-17 KST). 5th row 추가 불요.

### §결정 2 — Write-time verify 의무 (scope a-d)

lane agent 가 owned section 에 아래 4 종 write 를 수행할 때 write 직전 source direct verify 후 write 한다.

- **(a) corpus / fixture enumeration** — Story / Change-Plan / ADR 본문에 "예시 N건 / 전무 / 부재 / 다수" + file-path 인용 패턴을 write 할 때 → `git show origin/main:<path>` verify 후 `[verified: git show origin/main:<path>]` annotation 부착 의무. annotation 부재 = behavioral violation. (ADR-068 I-5 dimensional empirical-source annotation 과 **directly analogous mechanical 패턴** — 동일 mechanical 패턴 재사용 가능하나, 본 ADR 은 §결정 6 known-limitation 으로 behavioral mandate only. mechanical lint 는 후속 carrier.) — corpus #1a (CFP-746 D-7) 차단.
- **(b) design-lane self-check** — ArchitectAgent §3 / §7 corpus enumeration + ADR frontmatter value 인용 시 `git show origin/main` 으로 verify 후 write. **정정 행위 자체도 동일 verify 의무** (정정이 미검증되어 2nd slip 을 도입한 corpus #1b CFP-531 동인 — §결정 3 재귀 cross-ref). — corpus #1b 차단.
- **(c) §9 evidence write-time verify** — lane agent 가 §9 verdict evidence 에 ADR frontmatter value / contract field value 를 기재할 때 → source file direct Read verify 후 write. (corpus #2 CFP-770 CR-004 동인 — §9 write 시 ADR-079 `is_transitional` value 를 source verify 없이 stale 단언.) — corpus #2 차단.
- **(d) Phase 0 cross-plugin ownership verify** — ChangeImpactAgent Phase 0 mapping 시 `templates/*` 항목을 wrapper-local 단정하기 전 cross-plugin SSOT verify 1-step 의무. verify source = `codeforge:lane-self-write-boundary` skill. (corpus #3 CFP-770 §결정 8 동인 + memory `project_stale_skill_ownership_lore` 2nd 재현 — cross-plugin ownership 추정.) **known-limitation: verify source 가 mechanical-queryable registry 형태 부재 — §결정 6 rationale binding 참조.** — corpus #3 차단.

### §결정 3 — 정정 행위 재귀 verify + 무한 루프 cap (Researcher Unknown #1)

§결정 2 verify 누락이 사후 정정될 때, **정정 write 도 새 self-write artifact 이므로 동일 §결정 2 verify 대상** (재귀). corpus #1b (CFP-746 CFP-531) 가 "정정이 미검증되어 2nd slip 도입" 의 실증 evidence.

재귀 정정 (verify the fix of the verify, of the verify, …) 무한 루프 차단 = **신규 무한루프 차단 메커니즘 미도입, 기존 layer 재사용**: ADR-067 결정 1 (max FIX 3/3 도달 시 deterministic implementability reassessment trigger) + 결정 3 (ArchitectPL 재량 RESET vs escalation 결정 권한) 복합 cross-ref. 정정 재귀가 max FIX 3/3 도달 시 ADR-067 결정 1 reassessment trigger 발동 → 결정 3 ArchitectPL 재량으로 RESET vs `escalate_to_user` 결정 (ADR-067 결정 2 escalation 의무 trigger 3종 평가 동반). 도메인상 이미 존재하는 무한루프 차단 메커니즘을 재사용 (over-engineering 회피).

### §결정 4 — Citation ≠ Assertion 경계 (Analyst E-1)

lane agent owned section 내 cross-lane 산출물에 대한 **인용(citation, 출처 명시)** 과 **단정(assertion, 값을 사실로 주장)** 은 도메인상 다른 행위다.

- **citation** = 출처 attribution 으로 충분 (예: "RequirementsPL §5 가 doc-only 적격으로 판정" — 출처 명시) → verify 면제.
- **assertion** = 값을 사실로 주장 (예: "ADR-079 frontmatter `is_transitional: false`" — 값 단언) → §결정 2 verify 의무.

§결정 2 의 verify 의무는 **assertion 에만** 적용된다. cross-lane 산출물을 출처와 함께 인용하는 행위는 verify 의무 밖 (verify 대상 = 단언된 값의 사실성, 인용된 타 lane 판정의 재검증 아님).

### §결정 5 — Provisional marker defer (Analyst E-2)

Phase 0 mapping 이 planning-phase 진행 중 (spec/plan 미완성) 일 때는 미완성 mapping 값에 `[provisional]` marker 를 부착하고 write-time verify 를 **defer** 한다. 최종 verify 의무 시점 = lane spawn 직전 (`codeforge:story-epic-flow-preflight` preflight 단계). planning-phase 초안 단계의 verify 강제는 면제 (planning 반복 cost 회피) — 단 `[provisional]` marker 부재 시 §결정 2 가 즉시 적용 (defer 면제 조건 = explicit marker).

### §결정 6 — known-limitation (`mechanical_enforcement_actions: []` empty rationale binding)

본 ADR frontmatter `mechanical_enforcement_actions: []` 가 empty 인 것은 **누락이 아니라 명시적 known-limitation 결정**이다. ADR-040 Amendment 3 §결정 7.A schema 정합 — DesignReview lane 이 본 ADR 을 "missing `mechanical_enforcement_actions[]`" 로 flag 하지 않도록 §결정 본문에 explicit binding 한다.

**rationale** (Wave 1 결정 — Amendment 1 갱신 표시 포함):

1. ~~§결정 2(d) verify source = `codeforge:lane-self-write-boundary` skill 이 cross-plugin ownership 의 verify source 이나 **mechanical-queryable registry 형태 부재**~~ → **Amendment 1 (CFP-841) partial-stale 정정**: Wave 1 의 "mechanical-queryable registry 형태 부재" 전제는 partially stale. `docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml` machine_readable_ssot 가 CFP-722 §13.A 로 **이미 실재** (verified-via: `git show origin/main:skills/lane-self-write-boundary/SKILL.md` L36 machine_readable_ssot + `git show origin/main:docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml` sections 1-12). 단 yaml = Story file per-section ownership 한정 — ADR/Change Plan/Retro/domain-knowledge cross-plugin doc owner sub-tree 부재. → scope 2(d) = **신규 registry 창설 아닌 기존 yaml 의 cross-plugin doc-ownership 영역 확장** (disjoint sub-tree append-only) + lint binding + SKILL.md §13.B 4-way drift-sync 해소 (Amendment 1 §scope 2(d) carrier).
2. §결정 2(a) corpus annotation 은 ADR-068 I-5 와 directly analogous mechanical 패턴이나, 본 super-class 결함은 (a)/(b)/(c)/(d) 4 scope 가 단일 anchor 로 묶인 unitary scope (ADR-064 §결정 1) — scope (a) 만 부분 mechanical 화 시 super-class anchor 분절. behavioral mandate 가 4 scope 공통 forcing function 으로 우선. **Amendment 1 (CFP-841) 정합 유지**: scope (a) + scope (d) **동시** mechanical 전환으로 anchor 분절 회피 (단일 carrier — scope 분리 미허용). scope 2(b)/2(c) = behavioral mandate 영역 유지 (super-class anchor 의 behavioral forcing function 보존).
3. 동일 패턴 선례 = ADR-070 §D5 declaration-only retain (Codex verify-before-trust = behavioral mandate, evidence-checks-registry entry append 면제) + ADR-RESERVATION row 81 CFP-819 (`mechanical_enforcement_actions: []` declaration-only, verified-via: `git show origin/main:docs/adr/ADR-RESERVATION.md` row 81 2026-05-17 KST). ADR-073 frontmatter 자체도 Wave 1 = `[]` empty (behavioral directive only) 선례. **Amendment 1 (CFP-841) 후 본 ADR frontmatter = 2-entry deferred-followup** (Wave 2 — ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain 정합).

**후속 carrier 발의 의무 — Amendment 1 (CFP-841) 충족**: ~~scope (d) verify source 의 mechanical-queryable registry 화 (cross-plugin ownership registry + lint) = 별도 후속 CFP carrier 분리 발의 (escalation_action `escalate_user`, CFP-776 merge 후 발의 권장). scope (a) corpus annotation mechanical lint (ADR-068 I-5 패턴 재사용) = 동일 후속 carrier 또는 별도 CFP 분리 — brainstorm 단계 결정.~~ → **CFP-841 단일 통합 carrier 로 충족** (brainstorm 단계 결정 = scope (a) + scope (d) 단일 carrier, ADR-064 §결정 1 unitary scope). 본 §결정 6 = Wave 1 behavioral mandate + Wave 2 (Amendment 1) deferred-followup mechanical declaration. actual lint script + workflow wire = CFP-841 Phase 2 carrier (Change Plan §3 SSOT).

**self-referential trap 회피 (EC-3 self-protection)**: ADR-082 자체가 corpus #1a/#1b/#2/#3 (CFP-746 D-7 corpus slip / CFP-531 정정-2nd-slip / CFP-770 CR-004 `is_transitional` 거짓 단언 / §결정 8 Phase 0 cross-plugin 추정) 패턴을 본문에 인용/포함한다. ADR-082 frontmatter `is_transitional: false` + `## 해소 기준` = `N/A (permanent)` 선언은 §결정 2 verify 대상이 *아니다* (ADR-058 §결정 5 약화 방향 발의 차단 logic 통과 = permanent 정책 선언, source verify 가 적용될 mutable value 아님). 본 self-referential 면제가 §결정 본문에 명문화된 self-protection — DesignReview 가 "ADR-082 가 자기 frontmatter 를 verify 안 했다" 로 flag 하지 않도록. **Amendment 1 (CFP-841) 확장**: scope 2(a) corpus annotation lint 의 4번째 FP-완화 guard (self-referential exemption) 가 본 EC-3 를 verbatim 재사용 — ADR-082 본문 / CFP-776 Story / CFP-841 Story·Change Plan 의 corpus #1a/#1b/#2/#3 패턴 인용은 lint self-flag 차단 (file allowlist 정합, Change Plan §3.1 guard 4).

### §결정 7 — scope (e) FIX 명세 depth-aware 분리 (scope 외)

scope (e) FIX 명세 depth-aware scope 필드 (CFP-770 §8 제안 — broken-link/path 정정 FIX 명세 시 directory depth + 정정 규칙 범위 의무 필드) 는 **본 ADR scope 외 (별도 CFP 분리)**. super-class write-time verify mandate (a-d) ↔ FIX 명세 depth-aware (e) = disjoint 관심사 — 전자 = write-time truth verify (behavioral) / 후자 = fix-event-v1 schema 필드 확장 (ADR-008 contract bump + ADR-010 sibling sync 동반 = 사용자 가치 판단 영역). 동일 Story 묶음 시 CFP-scope-unitary (ADR-064 §결정 1) 위반. (e) = CFP-770 §8 reservation Issue carrier (escalation_action `escalate_user`, CFP-776 merge 후 발의 권장).

### §결정 8 — per-area 분할 (scope a/b/c/d 각 별 ADR) 거부 (scope 외)

4 scope = 단일 super-class 결함의 4 layer 표현. §결정 1 layer disjoint 표가 공통 anchor. ADR-064 §결정 1 정합 — 단일 super-class = unitary scope (영역별 분할 아님). per-area 분할 시 super-class anchor 가 4 ADR 로 분절되어 cross-Story pattern aggregation (ADR-045 §D-9) 의 forcing function 약화.

### §결정 9 — Amendment 번호 citation plan-time staleness 차단 (Amendment 6 신설, CFP-1198 — Amendment 7 양방향 확장, CFP-1312)

**forcing function**: 거버넌스 artifact (β-issue body / spec / change-plan / PR body / ADR amendment 본문) 안에서 특정 ADR 또는 inter-plugin contract 의 amendment 번호를 인용할 때, 인용 직전 target artifact 의 frontmatter `amendments:` 목록 (또는 `amendment_log`) 을 `Read` 도구로 직접 확인한 후 **정확 next-slot `M = max(amendment_id) + 1` 만 사용한다**. `M > max + 1` (forward-staleness — off-by-one / 계산 오류) 또는 `M ≤ max` (backward-staleness — 이미 land 된 slot 인용) 모두 stale citation (Amendment 7 확장, CFP-1312).

**verify-before-cite 의무**:

1. target ADR / contract 파일의 frontmatter `amendments:` 또는 `amendment_log` 항목을 직접 Read 한다.
2. 현재 최대 `amendment_id` 값 (`max`) 을 확인한다.
3. 새 amendment 번호 = **정확히 `max + 1`** 로 결정한다 (Amendment 7 명시 — `M = max+1` 외 모두 stale). forward (M > max+1) / backward (M ≤ max) 양방향 staleness 차단.
4. 인용 위치에 `verified-via: <frontmatter Read 경로 및 시각>` annotation 을 부착한다 (§결정 2(b) `[verified: git show origin/main:<path>]` annotation 형식 준용).

**scope**: 본 §결정 9 는 §결정 2(b) ("ArchitectAgent §3 / §7 corpus enumeration + ADR frontmatter value 인용 시 verify") 의 sub-specialization 이다. §결정 2(b) 가 이미 "ADR frontmatter value 인용 시 verify" 를 포괄하나, amendment 번호 citation 이 plan-time (β-issue / spec / change-plan 작성 시점) 에 발생하는 점 — 즉 §결정 2(b) 의 lane agent write-time 보다 이른 시점 — 을 명시적으로 언급하기 위해 별도 결정으로 codify.

**적용 대상 layer**:

| artifact 종류 | 주체 | 적용 layer |
|---|---|---|
| β-issue body, ADR brainstorm Phase 0 spec, change-plan | Orchestrator-authored | ADR-073 (Orchestrator verify-before-assert) ∩ 본 §결정 9 동시 적용 |
| ADR amendment 본문, design lane Change Plan | ArchitectAgent (internal lane agent) authored | 본 ADR §결정 2(b) + §결정 9 동시 적용 |
| spec / plan 기타 planning artifact | 해당 lane PL authored | 본 §결정 9 적용 |

**disjoint layer 관계**: β-issue = Orchestrator-authored artifact 이므로 ADR-073 §결정 1 (Orchestrator cross-repo state / assumption verify) 가 동시 적용된다. 단, ADR-073 와 본 ADR 의 axis disjoint (verify subject: Orchestrator cross-repo state assertion ↔ internal lane agent self-write value assertion) 가 본 §결정 9 의 plan-time 영역에서 overlap 하는 구조임을 명시 — 각 ADR scope 침범 아님 (동일 artifact 에 두 layer 가 독립적으로 적용). ADR-073 cross-ref: `docs/adr/ADR-073-orchestrator-verify-before-assert.md` §결정 1 (Orchestrator verify-before-assert — β-issue 작성 시 amendment 번호 cite 가 cross-repo state assertion 에 해당).

**known-limitation**: 본 §결정 9 = behavioral directive (Wave 1). Wave 2 mechanical lint (`amendment-number-frontmatter-verify` script + workflow + bats fixture) = CFP-1216 Phase 2 (별도 sub-carrier 로 land 완료, 2026-05-22 KST). **Amendment 7 (CFP-1312)** 가 Wave 2 lint Check (b) coverage gap (forward only → 양방향) 보강 — `cited_m != max_id + 1` 양방향 비교 + `[FORWARD-STALE]` / `[BACKWARD-STALE]` 출력 format 분리 + self-reference exemption (ADR file 자체) + templates/** path filter. frontmatter `mechanical_enforcement_actions:` 의 `amendment-number-frontmatter-verify` entry status warning retain (scope expand only, tier 변경 0).

**pattern evidence (ADR-045 §D-9 Mandatory, pattern_count = 3 — Amendment 7 확장)**:

| # | 출처 | stale citation | actual (verified) | staleness 방향 | catch layer |
|---|---|---|---|---|---|
| 1 | CFP-1177 β-issue (#1115) | "ADR-027 Amendment 7" | ADR-027 실제 max = Amendment 8 (CFP-1059 점유) → 실제 slot = Amendment 9 | forward (M > max+1) | Amendment 6 Wave 1 behavioral catch |
| 2 | CFP-1179 β-issue (#1114) | "ADR-063 Amendment 6/7" | ADR-063 실제 max = Amendment 7 (CFP-906/CFP-1059 점유) → 실제 slot = Amendment 8 | forward (M > max+1) | Amendment 6 Wave 1 behavioral catch |
| 3 | CFP-1293 retro (#1293) | "ADR-083 Amendment 2" | ADR-083 실제 max = Amendment 2 시점, 정확 next-slot = 3 → cited_m=2 ≤ max=2 | backward (M ≤ max) | Amendment 6 Wave 1 catch + CFP-1216 lint Check (b) forward-only coverage gap escape — **Amendment 7 motivation** |

세 케이스 모두 write-time 에 caught (plan land 후 escaped 0) 이나, root cause = (1)/(2) plan-time read verify 부재 + (3) lint coverage gap (`M > max+1` forward-only 비교). Amendment 7 = 양방향 mechanical wire 보강 (Wave 2 escape catch).

**ADR-068 I-4 (wording SSOT) 연계**: amendment 번호는 governance artifact 전체에서 동일 식별자로 참조되는 wording SSOT 대상이다. stale 번호가 planning artifact 에 기록되면 후속 ADR 본문 / CLAUDE.md / retro 와 wording drift 가 발생 — I-4 위반 원인이 된다.

### §결정 10 — ArchitectAgent write-time discipline 4 sub-scope expansion (Amendment 8 신설, CFP-1329)

ADR-082 §결정 1 layer 1 (Orchestrator scope) + §결정 2 scope (a-d) (internal lane agent self-write scope) 의 write-time verify mandate 가 ArchitectAgent (codeforge-design chief author) 의 4 write-time discipline 영역까지 확장 적용된다. 4 sub-decisions 모두 별도 axis disjoint 이며, 같은 super-class (verify-before-trust write-time semantic truth) 아래 단일 carrier 통합 (ADR-064 §결정 5 unitary 정합).

#### §결정 10.A — Codex TP#2 inline FIX 8-anchor mirror coverage checklist

**carrier**: memory `feedback_codex_tp2_verify_before_trust_pattern` (CFP-795 F-1 lesson)

ArchitectAgent §3 직후 mandatory Codex proactive check touchpoint #2 (ADR-052 Amendment 4) verified-true P1 finding inline FIX 시 다음 8 anchor 동시 갱신 의무:

1. Change Plan §3 (mechanical 구현 설계 SSOT — primary anchor)
2. Change Plan §4 Risk (R-N row append)
3. Change Plan §7 Threat model (T-N row + §7.6 매핑)
4. Change Plan §10 (미해소 deputy 이견 — finding 이행 추적)
5. Story §7 mirror (Change Plan §7 mirror 영역)
6. ADR amendment_log entry 끝 (carrier reference 1-line)
7. **ADR 본문 §결정 N 표·단락 — F-1 lesson, 누락 자주 발생 anchor**
8. ADR 신규 §결정 N 본문 (조건 / 알고리즘 / fail-closed)

verbatim wording 일관 — ADR-068 I-4 wording SSOT 강제. CFP-795 lesson: 8-mirror coverage 가 default 였다면 iter 1 회피.

**sentinel codify rationale** (pattern_count 1): CFP-795 F-1 dogfood inversion P1 prevention. forward-prevention 도구적 가치 > recurrence ≥ 2 wait — ADR-058 §결정 5 정합 (sentinel forward-prevention 영역 적격, ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 면제 — 도구적 가치 evidence base).

#### §결정 10.B — Mid-author partial revert propagation gap

**carrier**: memory `feedback_mid_author_partial_revert_propagation_gap` (CFP-1009 F-DR-001 P1 dogfood inversion sentinel)

mid-author Codex TP catch + inline FIX body normative correction 직후 frontmatter inline comment / appendix narrative / table cell sync 영역까지 propagation 의무:

1. ArchitectPL mid-author FIX 직후 self-discipline: `grep -rn "<stale-label>" <touched-files>` cross-check (wider scope frontmatter comment + appendix + table cell)
2. DesignReviewPL mandatory audit point — body normative correction ↔ frontmatter inline comment + appendix + table cell 일관성 verify
3. post-FIX reverse-mutual grep cross-check 의무 (to-remove pattern grep = 0 in target + to-add pattern grep ≥ N)

**sentinel codify rationale**: pattern_count 1 (CFP-1009 dogfood inversion P1). evidence-gate wait 대신 forward prevention 가치 우선 — ADR-074 carrier ADR 자체 같은 defect 보유 = dogfood inversion P1 severity, recurrence ≥ 2 wait 시 P1 재발 risk. ADR-058 §결정 5 forward-prevention 영역 적격 (도구적 가치 > wait, ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 면제).

#### §결정 10.C — ArchitectAgent self-introduced script-behavior claim verify

**carrier**: memory `feedback_architect_script_behavior_claim_verify` (pattern_count 2 reach)

ArchitectAgent (or Combined Req+Design lane) authors a claim about codeforge-internal script behavior (e.g., "parse-X.py skips template entries", "bootstrap-labels.sh creates all labels") = write-time self-introduced assertion. 의무 empirical verify:

1. ArchitectAgent self-discipline (best-effort): codeforge script behavior claim 작성 시 `[verified-via: <command>]` annotation + empirical command run + result 명시. 미verify 시 `[unverified — DesignReview to confirm]` 명시.
2. DesignReviewPL mandatory audit point: Story / Change Plan / ADR text 안 script behavior assertion 시 dedicated audit point 추가 — script 실행 + source grep verify.
3. mutual cross-check before declaring iter complete (F-DR-1006-3 lesson): systematic wording correction 적용 시 to-remove pattern + to-add pattern 양 axis grep cross-check 의무.

**pattern_count 2 evidence**:

| # | Story | claim | actual (verified) | severity |
|---|---|---|---|---|
| 1 | CFP-1006 F-DR-1006-1 (P2) | parse-hotfix-bypass-labels.py "skips template entry" | actual gh-side rejection (mechanism mismatch) | P2 dogfood gap |
| 2 | CFP-1025 (Orchestrator hypothesis REFUTED by ArchitectPL empirical verify) | hypothesis 발화 | pattern WORKING dogfood win | P3 hypothesis refuted |

**scope**: §결정 1 layer 1 (Orchestrator scope) + 본 §결정 10.C (ArchitectAgent scope) 양 layer 동시 적용 — RequirementsPL §2.1 verified state table 이 cover 안 하는 "script behavior assertion at write-time" disjoint gap. ADR-082 §결정 1 layer 1 sub-scope (1-A Amendment 1 base / 1-B Amendment 2 CFP-1016 Issue-body authorship / 1-C Amendment 5 CFP-1110 lane PL spawn prompt user-utterance verbatim) → 본 §결정 10.C = ArchitectAgent chief author scope 추가 layer. **FIX iter 1 정정 (DesignReview F-2 P0)**: stale "Amendment 3" citation 정정 — verify-before-cite mandate (Amendment 7 §결정 9) self-application 사례.

#### §결정 10.D — META self-application pattern

**carrier**: memory `feedback_meta_self_application_pattern` (pattern_count 2 reach)

Story introduces template / codification change → apply it to carrier Story itself as 1st applied case (eat your own dog food):

1. ArchitectPL Amendment / template / mandate change 시 자문: "Does this codification apply to a Story that I am writing right now?"
2. yes 시: Story file 자체에 적용 (frontmatter field + 신규 section + 신규 procedure verbatim)
3. META self-application 명시:
   - ADR amendment body: `## Amendment N` 안 "Meta-self-application" sub-section
   - Change Plan §11 결론: "carrier Story applies the codification as 1st case"
   - Story §2.1 / §3 / §9: META context cross-ref
4. DesignReviewPL audit: META self-application validation dedicated audit point

**pattern_count 2 evidence** (+ 본 Story 3rd applied):

| # | Story | applied codification | applied site | severity |
|---|---|---|---|---|
| 1 | CFP-1016 | ADR-082 Amendment 2 (`issue_origin: orchestrator_authored_followup` frontmatter + §2.1 verified state table) | Story file 자체가 META-self-applied | 1st occurrence |
| 2 | CFP-1340 Amendment 2 §결정 15 | Orchestrator-monopoly Story-file `§9/§10/§14/phase` inline whitelist 5번째 entry | Story file initial scaffold + §9.1 verdict inline write (CFP-1340 Story §14 row 6 + row 9 verified) | 2nd occurrence |
| 3 | **CFP-1329 (본 Story)** | **Amendment 8 §결정 10.D 신설** + Story file Amendment 2 §결정 15 inline write 적용 (Story §14 row 1) | META-self-applied **3rd applied case** | 3rd occurrence |

### §결정 11 — Code-level write-time semantic truth verify expansion (Amendment 9 신설, CFP-1330)

ADR-082 super-class (write-time semantic truth verify) scope 가 Code-level write-time discipline 2 sub-scope (test code production binding + script error visibility) 영역까지 확장 적용된다. Amendment 8 §결정 10 (ArchitectAgent write-time discipline) 과 disjoint axis — Amendment 8 = 거버넌스 artifact write-time / 본 §결정 11 = 코드 artifact (test/script) write-time. 같은 super-class (write-time semantic truth) 아래 단일 carrier 통합 (ADR-064 §결정 5 unitary 정합).

#### §결정 11.A — Test code production binding verify

**carrier**: memory `feedback_test_must_bind_to_production` (CFP-1025 F-CR-1025-2 sentinel)

bug-fix bats/unit test = real production code source/exec 의무 (sed-extract real fn, NOT inline hand-copy). Inline-copy = tautology, zero regression binding (test 가 자기 자신을 검증하는 형태로 production code 변경 시 silent regression coverage gap).

**의무 절차**:

1. **DeveloperPL / QADev**: regression test 가 real artifact source/exec:
   - bash function: `sed -n '/^funcname() {/,/^}/p' "${SCRIPT}" > _fn.sh; source _fn.sh` (sed-extract real fn)
   - whole script: DRY_RUN / early-return hook 으로 target function 만 stub 대상 실행
   - **NEVER re-type / inline fixed logic** (hand-copy = tautology smell)
2. **Discriminating-fixture (RED proof)**: sed-substitute bug INTO extracted real function (e.g., `2>&1` → `2>/dev/null`), source THAT, assert test FAILS. hand-written buggy variant = tautology.
3. **CodeReviewPL audit point**: `[ -f $SCRIPT ]` existence-only guard + inline function body + hand-written `*_masked` / `*_mock` reimplementation tautology smell grep. P1 severity (test-quality regression).
4. **Acceptance**: production fix manual revert → test RED. 잔존 GREEN → tautology, unresolved.

**sentinel codify rationale** (pattern_count 1): CFP-1025 F-CR-1025-2 dogfood inversion. forward-prevention 가치 우선 (test-quality defect = silent regression coverage gap, recurrence ≥ 2 wait 시 silent regression risk). ADR-058 §결정 5 forward-prevention 영역 적격 (도구적 가치 evidence base, ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 면제).

#### §결정 11.B — Script error visibility audit

**carrier**: memory `feedback_error_mask_metaroot` (CFP-1025 bootstrap-labels.sh:53-55 META-ROOT sentinel)

Script `2>/dev/null` 가 success/failure 보고하면서 real error 마스킹 = **mis-diagnosis amplifier META-ROOT**. False-success 가 downstream Story mis-diagnose 유발 + Wave-defer rationale falsify (CFP-1006 mis-diagnosis lineage downstream propagation verified).

**의무 절차**:

1. **Design lane / ArchitectAgent**: 리소스 create / state change 보고 script 작성 시 `2>/dev/null` 금지 (error path). `err=$(cmd 2>&1)` 형태로 stderr capture + failure 시 verbatim surface. `2>/dev/null` 영역 = 진정 benign expected-noise (예: `command -v` probes) only — success/failure consumed downstream operations 영역 금지.
2. **Root-cause 진단 discipline**: predecessor Story assumption falsified 시 masked-error META-ROOT 의심. RAW signal (workflow run log, NOT script summary; admin probe, NOT CI token masked result) prior hypothesis 형성 전.
3. **CodeReview / SecurityTest audit**: `Grep '2>/dev/null' scripts/**` resource-creating/state-changing commands. mis-diagnosis-amplifier risk 표시 (severity scales by downstream consumer 수).

**META-ROOT pattern_count 1** (CFP-1025 bootstrap-labels.sh:53-55): codify rationale forward-prevention (META-ROOT severity = mis-diagnosis 전파 chain risk, recurrence ≥ 2 wait 시 P1 propagation 영역 — CFP-1006 mis-diagnosis lineage verified). codeforge-wide grep audit = follow-up CFP carrier (별도 sweep). ADR-058 §결정 5 forward-prevention 영역 적격, ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 면제.

#### §결정 11 — disjoint axis with Amendment 8 §결정 10

| Amendment | scope | write-time artifact axis | layer |
|---|---|---|---|
| Amendment 8 §결정 10 | ArchitectAgent write-time discipline 4 sub-scope (A/B/C/D) | 거버넌스 artifact (Story / Change Plan / ADR / memory) | governance write-time |
| **Amendment 9 §결정 11** | **Code-level write-time discipline 2 sub-scope (A/B)** | **코드 artifact (test code / script error path)** | **code write-time** |

두 Amendment 가 ADR-082 super-class (write-time semantic truth verify) 의 disjoint layer expansion. Amendment 8 = chief author scope / Amendment 9 = Code-level scope. CFP scope unitary (ADR-064 §결정 5) 정합 — 단일 super-class 안 disjoint axis 분리.

**Wave 1 = declaration-only**: 2 sub-decisions 모두 behavioral directive. Wave 2 mechanical wire (CodeReviewPL audit dedicated points: tautology smell grep + `Grep '2>/dev/null' scripts/**` resource-creating/state-changing audit + codeforge-wide grep audit sweep) = 별도 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

**META-self-application (§결정 10.D 4th applied case)**: 본 Amendment 9 자체가 §결정 10.D pattern self-applied — 본 Amendment 번호 9 가 target ADR-082 frontmatter `amendments:` 목록 Read verify 후 max(8)+1=9 으로 결정 (verified-via: Read worktree `docs/adr/ADR-082-...md` frontmatter `amendments[]` L11-51 max=8, 2026-05-24 KST 기준 origin/main a0eb545 — CFP-1329 Amendment 8 merge 후 base). Amendment 7 §결정 9 verify-before-cite mandate self-application 사례.

### §결정 12 — RequirementsPL + retro-time verify-before-trust 2 sub-scope expansion (Amendment 10 신설, CFP-1332)

ADR-082 super-class write-time semantic truth verify scope 가 (a) RequirementsPL §2.1 verified state table mandate strengthening + (b) retro-time empirical verify (Wave-defer rationale falsification 차단) 양 axis 동시 expansion. write-time-only → write-time + retro-time lifecycle.

#### §결정 12.A — Orchestrator-authored Issue body §2.1 verified state table mandate strengthening

**carrier**: memory `feedback_issue_body_verify_before_trust` (pattern_count 2 reach — CFP-1000 INVERSE drift + CFP-1001 lint output FP)

Orchestrator 가 follow-up CFP batch Issue body author 시 (e.g., post-retro batch creation) Issue body claim 이 parallel-session merge 사이 stale / factually inverted 가능. RequirementsPL spawn prompt **MUST include explicit verify-before-trust mandate** on each Issue body claim:

1. Reproduce any cited lint output via direct script invocation in worktree
2. Direct file Read for cited line numbers (line numbers may have shifted post-parallel-merge)
3. Direct gh CLI/API probe for cited gh-side state (label existence, baseline count, registry value)
4. Direct file existence check for cited paths (e.g., `.claude-work/` directory)

**§2.1 verified state table mandatory** (ADR-082 Amendment 2 §결정 1 layer 1 strengthening, frontmatter `issue_origin: orchestrator_authored_followup` 의무 codify). Both layers preserved: §1 verbatim Issue (immutable, story-section-1-immutable.yml) + §2 verified state (drives downstream lanes).

**pattern_count 2 evidence**:
- CFP-1000 — Issue body claim "prod-cutover-deputy-evidence not registered in gh" verified state INVERSE = REGISTERED in gh, MISSING in registry (Pivot detected, fix direction 정정)
- CFP-1001 — Issue body cite "L189 ADR-038 Amendment 6 lint output as drift" verified state = lint regex cross-context window ±5-line false-pair (paired with L185 ADR-040 Amendment 6, NOT a real drift)

#### §결정 12.B — Retro-time wave_defer empirical verify

**carrier**: memory `feedback_wave_defer_empirical_verify` (pattern_count 2 reach — CFP-1006 Wave-defer rationale falsified + CFP-1025 corrective closure pattern WORKING)

Story 가 sub-scope Wave 2/3 follow-up CFP 로 defer 시 rationale "will auto-resolve via mechanism X" = **retro time 에 empirical verify 의무** (Story-write time 가정 금지). Wave-defer = ADR-064 §결정 1 scope-unitary 정합 practice, 단 deferral *reason* 이 hypothesis ("mechanism X handles it automatically") 인 경우 FALSE 가능성 검증 의무.

**의무 절차** (retro time PMOAgent / Orchestrator):
1. Wave-deferred sub-scope 마다 deferral rationale 이 predict 하는 empirical check 실행:
   - "auto-resolves via workflow X" → workflow X 가 post-merge actual produced state predicted state 일치 verify
   - "covered by existing lint Y" → lint Y 실행, deferred concern catch 확인
   - "backward-compat preserved" → backward-compat scenario actual run
2. Retro 안 empirical result 기록:
   - 확인 → Wave N follow-up 가 precautionary/optional (deprioritize 가능)
   - 반증 → Wave N follow-up 가 genuinely required (priority 격상 + 정확 root cause re-diagnose)

**pattern_count 2 evidence**:
- CFP-1006 Wave 1 — "36 registry→gh missing entries auto-resolve via bootstrap-labels.yml CFP-598 dynamic registry-driven pattern on PR open" rationale post-merge verify: gh hotfix-bypass label count 15 unchanged from pre-CFP-1006 → rationale FALSIFIED. Wave 2 = Issue #1025 genuinely required (not precautionary)
- CFP-1025 — empirical diagnosis via raw `gh run view 26080174058 --log` REFUTED Orchestrator's pre-spawn PyYAML hypothesis (115 blanket failures = 2-layer token-gap + error-mask META-ROOT). empirical-verify discipline prevented second mis-diagnosis (pattern WORKING AS DESIGNED)

#### §결정 12 — disjoint axis with Amendment 8 §결정 10 + Amendment 9 §결정 11

| Amendment | scope | verify lifecycle axis | layer |
|---|---|---|---|
| Amendment 8 §결정 10 | ArchitectAgent write-time discipline 4 sub-scope | governance artifact write-time | governance write-time |
| Amendment 9 §결정 11 | Code-level write-time discipline 2 sub-scope | code artifact write-time | code write-time |
| **Amendment 10 §결정 12** | **RequirementsPL + retro-time verify expansion 2 sub-scope** | **Issue-body write-time + retro-time empirical verify** | **lifecycle expansion** |

3 Amendment 모두 ADR-082 super-class (write-time semantic truth verify) 의 disjoint axis expansion. Amendment 10 = lifecycle axis 추가 (write-time-only → write-time + retro-time). CFP scope unitary (ADR-064 §결정 5) 정합 — 단일 super-class 안 disjoint axis 분리.

**Wave 1 = declaration-only**: 2 sub-decisions 모두 behavioral directive. Wave 2 mechanical wire (RequirementsPL §2.1 verified state table lint + retro empirical-verify-required marker) = 별도 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

**META-self-application (§결정 10.D 5th applied case)**: 본 Amendment 10 자체가 §결정 10.D pattern self-applied — 본 Amendment 번호 10 가 target ADR-082 frontmatter `amendments:` 목록 Read verify 후 max(9)+1=10 으로 결정 (verified-via: Read worktree `docs/adr/ADR-082-...md` frontmatter `amendments[]` L11-57 max=9, 2026-05-24 KST 기준 origin/main 38fc8ff — CFP-1330 Amendment 9 merge 후 base). Amendment 7 §결정 9 verify-before-cite mandate self-application 사례.

### §결정 13 — GitOps verify-before-trust discipline 3 sub-scope expansion (Amendment 11 신설, CFP-1338)

ADR-082 super-class verify-before-trust scope 가 GitOps coordination layer 영역 expansion — main drift bypass audit + HEAD SHA pin + branch protection worktree cleanup 3 sub-scope.

#### §결정 13.A — Main drift bypass audit pattern (pattern_count 5 reach HIGH)

**carrier**: memory `feedback_main_drift_bypass_audit_pattern` — codeforge wrapper PR 가 pre-existing main drift 를 inherit 시 표준 4 hotfix-bypass labels + [bypass-justification] audit comment template 적용 (per ADR-064 §결정 1 scope unitary 정합).

**의무 절차**:
1. Pre-merge verify-before-trust: 각 failing non-required check 를 CFP-N-introduced vs pre-existing main drift 분류 — direct git diff inspection
2. 4 표준 hotfix-bypass labels gh CLI 적용 (failure 영역 별):
   - `hotfix-bypass:marketplace-description-verbatim` (CFP-1286~ description sync gap)
   - `hotfix-bypass:wording-dictionary` (CHANGELOG.md pre-existing 'ratchet' / 'pin' / '별' standalone advisory)
   - `hotfix-bypass:inter-plugin-contracts-parity` (CFP-1059 deploy_output / deploy_review_output canonical 부재)
   - `hotfix-bypass:marketplace-atomic` (description-verbatim sister)
3. `[bypass-justification]` marker comment (comment-prefix-registry-v1 v1.3 14th prefix, CFP-845 carrier): per-finding root cause + verify-before-trust evidence + ADR-024 Amendment 3 §결정 6.C audit trail mandate cross-ref
4. pattern_count tracking in PMO retro section (≥ 2 same drift class = ADR escalation candidate)

**pattern_count 5 reach evidence**: CFP-963 P1+P2 + CFP-1000 + CFP-1001 + CFP-1340/1329/1330/1332 batch (4 bypass label 동시 적용 lineage). HIGH evidence — sentinel 영역 아님 (standard pattern_count reach).

#### §결정 13.B — HEAD SHA pin step 0 (verify-before-trust precondition)

**carrier**: memory `feedback_verify_pin_head_sha` (CFP-722 stale HEAD verification churn sentinel)

Async multi-agent coordination 안 branch artifact verify-before-trust 시 의무:

1. **Step 0**: `gh api repos/<owner>/<repo>/commits/<branch> --jq '.sha'` 으로 current HEAD 해결, 그 SHA pin
2. **Content verify**: `?ref=<pinned-sha>` 형식으로 pinned SHA 안 content verify (mid-chain SHA / agent self-claim SHA blind verify 금지 — branch 가 advanced 가능)
3. **Incremental commit signal 시**: explicit HEAD re-resolve (incremental commit = stale-HEAD trigger)
4. **Stale REJECT correction**: stale SHA against correct REJECT 도 process error → 신속 withdraw (spurious re-FIX churn 회피)

**sentinel codify rationale**: CFP-722 evidence single occurrence. ADR-073 verify-before-assert sub-discipline cross-ref-sufficient. Codify rationale = forward-prevention (verifier 의 stale-ref churn risk 차단).

#### §결정 13.C — Branch protection 환경 worktree cleanup 순서

**carrier**: memory `feedback_branch_protection_worktree_cleanup` (workflow discipline)

Main branch protection active repo 영역 finishing-a-development-branch skill 실행 시:

1. Option 1 (Merge Locally) 제시 금지 (main protect 시 `git merge` + `git push` 직접 반영 불가)
2. Option 2 (Push + PR) 선택 후 worktree = **PR merge 확인 후** 별도 정리
3. PR merge 확인 = `gh pr view <number> --json mergedAt` 또는 사용자 확인
4. codeforge plugin-codeforge repo 항상 적용 (ADR-024 branch protection 강제) + consumer repo 권장 (consumer-guide §2e)

**workflow discipline codify rationale**: branch protection 환경 timing convention 정의 — premature worktree removal 시 PR 피드백 대응 불가 + late removal 시 추적 불가. ADR-024 + ADR-040 cross-ref.

#### §결정 13 — disjoint axis with Amendment 8/9/10

| Amendment | scope | verify lifecycle axis | layer |
|---|---|---|---|
| Amendment 8 §결정 10 | ArchitectAgent write-time discipline 4 sub-scope | governance artifact write-time | governance write-time |
| Amendment 9 §결정 11 | Code-level write-time discipline 2 sub-scope | code artifact write-time | code write-time |
| Amendment 10 §결정 12 | RequirementsPL + retro-time verify expansion | Issue-body + retro-time | lifecycle expansion |
| **Amendment 11 §결정 13** | **GitOps verify-before-trust discipline 3 sub-scope** | **bypass audit + HEAD SHA pin + worktree cleanup** | **GitOps coordination** |

4 Amendment 모두 ADR-082 super-class (verify-before-trust mandate) 의 disjoint axis expansion. CFP scope unitary (ADR-064 §결정 5) 정합.

**META-self-application (§결정 10.D 6th applied case)**: 본 Amendment 11 자체가 §결정 10.D pattern self-applied — 본 Amendment 번호 11 = max(10)+1 (verified-via Read frontmatter L11-65 max=10 origin/main e7b7791).

## 결과

본 ADR codify 결과:

- ADR-073 (Orchestrator cross-repo) + ADR-070 (Codex external worker) disjoint super-class layer 신설 — internal lane agent self-write write-time semantic truth verify
- §결정 1 layer disjoint 4-layer 표 = 4 ADR 공통 anchor (over-abstraction 우려 완화 — domain-knowledge 공백 = 신규 layer 정당)
- §결정 2 scope (a-d) write-time verify 의무 + 4 corpus pattern 직접 매핑 차단
- §결정 3 정정 재귀 verify + ADR-067 결정 1 (max FIX 3/3 reassessment trigger) + 결정 3 (RESET vs escalation 권한) 복합 재사용 (무한루프 차단 신규 메커니즘 미도입)
- §결정 4 citation ≠ assertion 경계 (over-verify 회피 — 인용은 verify 면제)
- §결정 5 provisional marker defer (planning-phase 반복 cost 회피)
- §결정 6 `mechanical_enforcement_actions: []` known-limitation rationale binding (ADR-040 Amendment 3 missing flag 회피) + 후속 carrier 발의 의무 + self-referential trap 회피 self-protection (EC-3)
- ADR-073/070 Amendment 1 cross-ref (disjoint 보완 1줄) + ADR-045 Amendment 6 (§D-9 적용 evidence 1줄)
- ADR-RESERVATION row 82 active (CFP-776, reserved 미경유 직접 active = ADR-079/080/081 row precedent 정합)
- CLAUDE.md verify-before-trust 단락 ADR-082 신입 + 4-layer 계층 + playbook §3.10/§3.14 cross-ref 1줄 append-safe
- 본 carrier 자체 = PMOAgent ADR-045 §D-9 pattern_count 3 ≥ threshold 2 forcing function 산물 (escalation_action escalate_user → 사용자 단일 super-class 통합 결정)

## 거절된 대안

- **(D-A) scope (e) 본 ADR 흡수** — disjoint 관심사 (fix-event-v1 schema 변경 동반 사용자 가치 판단 영역), CFP-scope-unitary 위반 → §결정 7 별도 CFP 분리.
- **(D-B) per-area 분할 (scope a/b/c/d 각 별도 ADR)** — super-class anchor 4 ADR 분절, ADR-045 §D-9 pattern aggregation 약화 → §결정 8 단일 super-class 거부.
- **(D-C) mechanical lint 즉시 enforce (Wave 1 동시 mechanical_enforcement_actions[] 신설)** — scope (d) verify source mechanical-queryable registry 부재 (Researcher Unknown #2). Wave 1 mechanical 화 시 (a) 만 부분 codify → super-class anchor 분절 (ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain 손실). → §결정 6 behavioral mandate Wave 1 + 후속 carrier 분리.
- **(D-D) 신규 무한루프 차단 메커니즘 도입 (정정 재귀 cap 자체 신설)** — ADR-067 결정 1 (max FIX 3/3 reassessment trigger) + 결정 3 (RESET vs escalation 권한) 이 도메인상 이미 존재 → §결정 3 기존 layer 재사용 (over-engineering 회피).

## 관련 파일

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 1 cross-ref (disjoint 보완: Orchestrator cross-repo ↔ ADR-082 internal lane self-write)
- `docs/adr/ADR-070-codex-verify-before-trust.md` — Amendment 1 cross-ref (disjoint 보완: external worker ↔ ADR-082 internal lane self-write)
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — Amendment 6 (§D-9 cross_story_pattern_adr_trigger 적용 evidence: 본 carrier = pattern_count 3 산물)
- `docs/adr/ADR-RESERVATION.md` — row 82 active (CFP-776)
- `CLAUDE.md` — verify-before-trust 단락 (현 ADR-073 영역) ADR-082 신입 + 4-layer 계층
- `docs/orchestrator-playbook.md` — §3.10 (Codex Proactive Check) + §3.14 (user-dialog) ADR-082 cross-ref 1줄 append-safe
- `mclayer/codeforge-internal-docs/wrapper/{stories,change-plans}/CFP-776-*` / `2026-05-17-cfp-776-*` — Story carrier (doc-only fast-path 단일 PR)

## 관련 ADR

- **ADR-073** Orchestrator verify-before-assert: disjoint 보완 — Orchestrator 행위 한정 (cross-repo state + assumption). 본 ADR = internal lane agent self-write. 충돌 0.
- **ADR-070** Codex verify-before-trust: disjoint 보완 — 외부 worker(Codex) output 한정. 본 ADR = internal lane agent self-write. D5 declaration-only retain 패턴 선례. 충돌 0.
- **ADR-045** §D-9 cross_story_pattern_adr_trigger: 본 carrier = ADR-045 §D Mandatory escalation 산물 (pattern_count 3 ≥ threshold 2, escalation_action escalate_user). Amendment 6 evidence. 보완 관계, 충돌 0.
- **ADR-067** fix-ledger implementability escalation (`docs/adr/ADR-067-fix-ledger-implementability-escalation.md`): 결정 1 (max FIX 3/3 reassessment trigger) + 결정 3 (ArchitectPL 재량 RESET vs escalation 권한) 복합 = §결정 3 정정 재귀 무한루프 cap cross-ref. 재사용 관계, 충돌 0.
- **ADR-058** is_transitional + 해소 기준: `is_transitional: false` 정합 + self-referential trap 회피 anchor (§결정 6 EC-3). 충돌 0.
- **ADR-040 Amendment 3** normative ADR `mechanical_enforcement_actions[]`: Wave 1 = `[]` empty + §결정 6 rationale binding (missing flag 회피) / **Amendment 1 (CFP-841) 후 = 2-entry deferred-followup** (Wave 2 progression chain 정합). 충돌 0.
- **ADR-068 I-5** empirical-source annotation: §결정 2(a) directly analogous mechanical 패턴 — **Amendment 1 (CFP-841) scope (a) lint 가 I-5 `[empirical-source]` annotation 패턴 verbatim 재사용** (cross-ref only, I-5 본문 0건 변경, 양방향 backref). 충돌 0.
- **ADR-064 §결정 1** CFP scope unitary: 단일 super-class = 영역별 분할 아님 (§결정 7/8 근거 + Amendment 1 scope a+d 단일 carrier 근거). 정합.
- **ADR-054** doc-only fast-path: 본 Story flow 근거 (단일 PR — CFP-776). **Amendment 1 carrier CFP-841 = 강제 Story 2-PR** (ADR 변경 — ADR-082 Amendment 1 + ADR-024 Amendment 7 + ADR-068 cross-ref, doc-only fast-path 비대상). 정합.
- **ADR-024 Amendment 7** (Amendment 1 동반): `hotfix-bypass:corpus-claim-verify` 34번째 + `hotfix-bypass:cross-plugin-ownership-verify` 35번째 family member (§결정 6.A per-entry namespace 정합). 충돌 0.
- **ADR-060** (Amendment 1 동반): evidence-checks-registry 2 entry (`corpus-claim-verify` / `cross-plugin-ownership-verify`, warning tier, deferred-followup → Phase 2 actual wire — §결정 5 모든 신규 entry warning 시작 강제 정합). 충돌 0.
- **ADR-063** §결정 1 (Amendment 7 동반): mirrored field atomic invariant — `plugin.json` PATCH bump 6.5.1 → 6.5.2 (mechanical lint coverage expand = plugin behavior 변경) → marketplace sibling sync PR (`marketplace.json` plugins[name=codeforge] `version` field). 충돌 0.
- **ADR-061 §결정 1 + §결정 6.A** (Amendment 7 동반): Python SSOT (>5줄 multi-line, heredoc 금지) + thin wrapper convention 정합 — `scripts/lib/check_amendment_number_stale.py` Check (b) 양방향 확장 retain Python SSOT pattern. 충돌 0.

## 해소 기준

N/A — permanent policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — write-time verify scope 확장. **Amendment 1 = behavioral→mechanical scope 확장 = 강화 방향 정합, sunset_justification 면제**). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. `is_transitional: false` (영구 정책 — Amendment 1 후에도 유지). **self-referential 주의**: 본 §해소 기준 부재 (`N/A — permanent`) 선언 자체가 §결정 2 write-time verify 대상이 *아니다* (§결정 6 EC-3 self-protection — permanent 정책 선언은 source verify 가 적용될 mutable value 아님).

---

## Amendment 1 — §결정 6 behavioral→mechanical 전환 (CFP-841, 2026-05-17 KST)

### 컨텍스트

Wave 1 (CFP-776) §결정 6 은 `mechanical_enforcement_actions: []` empty 를 명시적 known-limitation 으로 결정하면서 **후속 carrier 발의 의무**를 본문에 명문화했다 (scope (d) mechanical-queryable registry 화 + scope (a) corpus annotation lint = 별도/동일 후속 carrier, brainstorm 단계 결정). CFP-776 retro §6 후보 1 escalation_action `escalate_user` → 사용자 "Carrier 6+7 escalation 전체 발의" 승인 (2026-05-16 KST). brainstorm 단계 결정 = scope (a) + scope (d) **단일 통합 carrier** (ADR-064 §결정 1 unitary scope — scope (a) 만 부분 codify 시 §결정 6 rationale 2 super-class anchor 분절 위반).

### Amendment

#### A1-1 — `mechanical_enforcement_actions: []` → 2-entry deferred-followup

frontmatter `mechanical_enforcement_actions:` empty → 2 entry:

| action | target_section | status | Phase 2 carrier |
|---|---|---|---|
| `corpus-claim-verify` | §결정 2(a) | deferred-followup | CFP-841 Change Plan §3.1 — Story/Change-Plan/ADR corpus enumeration `[verified: git show <ref>:<path>]` annotation lint (ADR-068 I-5 directly-analogous pattern 재사용) |
| `cross-plugin-ownership-verify` | §결정 2(d) | deferred-followup | CFP-841 Change Plan §3.2 — `lane-self-write-ownership-matrix.yaml` cross_plugin_doc_ownership sub-tree query 1-step lint + §13.B 4-way drift-sync invariant |

status `deferred-followup` = Phase 1 declare / Phase 2 actual wire (ADR-060 §결정 5 모든 신규 entry warning 시작 강제 + ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain 정합).

#### A1-2 — §결정 6 rationale 1 partial-stale 정정

Wave 1 rationale 1 "scope 2(d) verify source mechanical-queryable registry 형태 부재" 전제는 **partially stale**: `docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml` machine_readable_ssot 가 CFP-722 §13.A 로 이미 실재 (verified-via: `git show origin/main:skills/lane-self-write-boundary/SKILL.md` L36 + `git show origin/main:docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml` sections 1-12). 단 yaml = Story file per-section ownership 한정 (ADR/Change Plan/Retro/domain-knowledge cross-plugin doc owner sub-tree 부재). → scope 2(d) = **신규 registry 창설 아닌 기존 yaml cross-plugin doc-ownership 영역 확장** (disjoint sub-tree append-only) + lint binding + SKILL.md §13.B 4-way drift-sync 해소. §결정 6 rationale 1 본문에 strikethrough + Amendment 1 정정 명문화 완료.

#### A1-3 — scope 2(b)/2(c)/2(e) 영역 유지 (scope_boundary)

본 Amendment 1 **포함**: scope 2(a) + scope 2(d) mechanical 전환 (deferred-followup declare + Phase 2 actual wire carrier).

본 Amendment 1 **out-of-scope** (유지):

- scope 2(b)/2(c) = §결정 2 behavioral mandate 영역 유지 (super-class anchor 의 behavioral forcing function 보존 — mechanical 전환 비대상)
- scope 2(e) = §결정 7 별도 CFP 분리 결정 유지 (fix-event-v1 schema 동반 가치 판단 영역)
- 신규 ADR 창설 = Amendment only (ADR-RESERVATION 신규 row 0)
- I-5 본문 정책 변경 = ADR-068 cross-ref only (directly-analogous pattern 재사용 명시, Amendment 아님)

### Compatibility

- §결정 1~5 + §결정 7~8 + §본질 선언 + §컨텍스트 (corpus 4건) 전부 유지 — 본 Amendment 1 은 §결정 6 의 behavioral→mechanical 전환 + rationale 1 정정 only.
- ADR-058 §결정 5 sunset_justification — Amendment 1 = forbid scope 확장 (behavioral mandate → mechanical enforcement scope 확장) = ratchet-up 강화 방향, `sunset_justification_required: false` (frontmatter amendments[].sunset_justification 명문). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 2-entry 보유 (Wave 1 known-limitation empty → Wave 2 deferred-followup, missing flag 비대상).

### Related (Amendment 1 동반)

- `docs/adr/ADR-068-boundary-completeness-invariants.md` — I-5 directly-analogous pattern 재사용 backref (amendment_log + 관련 ADR, I-5 본문 0건 변경)
- `docs/adr/ADR-024-story-scoped-branch-policy.md` — Amendment 7 (`hotfix-bypass:corpus-claim-verify` 34번째 + `hotfix-bypass:cross-plugin-ownership-verify` 35번째 family member)
- `docs/inter-plugin-contracts/label-registry-v2.md` — v2.24 → v2.25 MINOR (2 family member 동시 추가, kind:registry sibling sync 면제)
- `docs/evidence-checks-registry.yaml` — `corpus-claim-verify` + `cross-plugin-ownership-verify` 2 entry (warning tier, deferred-followup)
- `docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml` — scope 2(d) cross_plugin_doc_ownership sub-tree 확장 대상 (CFP-841 Phase 2 carrier)
- `CLAUDE.md` — verify-before-trust 단락 Amendment 1 cross-ref 1줄
- `mclayer/codeforge-internal-docs/wrapper/{stories,change-plans,specs,plans}/CFP-841` / `2026-05-17-cfp-841-*` — Amendment 1 carrier Story (강제 Story 2-PR)

---

## Amendment 2 — Orchestrator-authored Issue body pre-publish verify mandate (CFP-1016, 2026-05-19 KST)

### 컨텍스트

Amendment 1 (CFP-841) 후속, §결정 1 layer 1 (Orchestrator scope) 의 verify-before-trust 적용 범위에 새로운 corpus pattern 누적 — **Orchestrator 가 follow-up Issue body 를 author 할 때 (retro time / brainstorm Phase 0 후속 / ADR amendment carrier reservation 등) Issue body 본문 claim 을 source verify 없이 단언하는 패턴이 3 Story 누적**. ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count **3** ≥ threshold 2 → Mandatory framing + escalation_action `escalate_user` → 사용자 단일 super-class ADR 강화 결정 (2026-05-19 KST).

기존 ADR-073 (Orchestrator cross-repo state verify) + ADR-082 §결정 1 layer 1 (Orchestrator scope) 는 **lane 진입 시 Orchestrator 가 외부 state/assumption 을 단정할 때** verify 의무로 codify. Issue **body authorship time** (Issue 생성 직전, story-init.yml 발화 전) 은 layer 1 scope 안이나 corpus 누적 전까지 명시적 codification 부재 — 본 Amendment 2 가 explicit Issue-body authorship 영역 codify carrier.

### pattern corpus (추가 3 — Issue #1016 body verbatim, §2.1 verified)

| # | Story | 발현 | 설명 |
|---|---|---|---|
| 4 | CFP-1000 | Issue body 3 inversions | Orchestrator-authored Issue body (CFP-963 retro time) 가 `prod-cutover-deputy-evidence` registry presence INVERTED + baseline label-registry 개수 stale (42 vs verified 44) + `.claude-work/label-registry-bootstrap.json` 존재 단언 but 디렉토리 자체 부재. Story §2.1 verified state table 이 9-row drift 매핑으로 3 inversion 직접 catch (verified-via: `git show origin/main:codeforge-internal-docs/wrapper/stories/CFP-1000.md` L24-L48 2026-05-19 KST). |
| 5 | CFP-1001 | Issue body lint output verbatim FP transcribe | Orchestrator-authored Issue body 가 `check-claude-md-amendment-ref.sh` lint output 의 L189 "ADR-038 Amendment 6 phantom" 분류를 verbatim 인용. Story §2.1 Pivot 1 이 lint regex `±5-line context window` cross-paired L185 ADR-040 ↔ L189 ADR-038 → **regex cross-context FALSE POSITIVE** 진단. Issue body 자체는 lint output verbatim citation 인 점에서 citation ≠ assertion (§결정 4) but Orchestrator authorship 시점에 lint output 사실성을 verify 안 함 (verified-via: `git show origin/main:codeforge-internal-docs/wrapper/stories/CFP-1001.md` L41-L62 2026-05-19 KST). |
| 6 | CFP-1002 | Issue body ADR-054 filename missing 'story' word | Orchestrator-authored Issue body 가 ADR-084 L229 broken link 정정 대상 filename `ADR-054-doc-only-fast-path.md` 인용 but actual file = `ADR-054-doc-only-story-fast-path.md` (4-char + hyphen missing). Story §2.1 row 2 가 sed + ls direct verify 로 catch (verified-via: `git show origin/main:codeforge-internal-docs/wrapper/stories/CFP-1002.md` L38-L67 2026-05-19 KST). |

PMOAgent ADR-045 §D-9 정량 임계값: pattern_count **3** ≥ threshold 2 → Mandatory framing + escalation_action `escalate_user`.

**Meta-self-application**: 본 ADR carrier Story (CFP-1016) 의 Issue body 자체가 Orchestrator-authored at CFP-1002 retro time (2026-05-19 KST). 본 Amendment 2 carrier Story §2.1 verified state table 이 4 claims (CFP-1000 inversions / CFP-1001 lint output / CFP-1002 filename / ADR-082 next amendment_id) 검증 — eating the dog food. 패턴 4-occurrence-recovered (4-occurrence-prevent).

### Amendment

#### A2-1 — §결정 1 layer 1 (Orchestrator scope) verify scope 확장 (Issue body authorship time)

§결정 1 layer 1 (ADR-073) Orchestrator cross-repo state / assumption verify 의 적용 범위에 **Issue body authorship time** 명시적 codify:

| sub-scope | trigger | verify 의무 |
|---|---|---|
| (1-A) lane spawn / cross-repo state assertion | lane 진입 시 외부 state 단정 | `git fetch origin` + `git show origin/main:<path>` + `verified-via` annotation (Wave 1 = ADR-073) |
| **(1-B) Orchestrator-authored Issue body claim** | **Orchestrator 가 retro time / brainstorm Phase 0 후속 / ADR amendment carrier reservation / pattern_count escalation forcing function 산물로 Issue body 를 author 할 때** | **Issue body 안 모든 `claim` (file path / registry value / lint output / cross-repo state / ADR frontmatter value / amendment count 등) 을 source direct verify 후 author. Orchestrator 가 Issue body 안 fact citation 의 ground truth 를 verify-before-trust 의무 — Amendment 2 신설** |

verify mechanism (Wave 1 = behavioral mandate + Wave 1.5 = mechanical-enforceable in Story-level):

1. **behavioral mandate (playbook §3.17, Wave 1)** — Orchestrator 가 Issue body author 시 fact claim 마다 `git show <ref>:<path>` / `grep -c` / `gh issue view` / `mcp__github__get_file_contents` 등 direct verify 후 author. body 안 fact citation 어휘 사용 시 implicit verify 의무 inherited from §결정 2(c) (§9 evidence write-time verify) directly-analogous pattern.
2. **mechanical-enforceable (templates/story-page-structure.md §2.1, Wave 1 alternative (a))** — Story file frontmatter 에 신규 field `issue_origin: orchestrator_authored_followup` (vs default `user_authored_issue_form`) 도입. `issue_origin: orchestrator_authored_followup` 시 §2.1 verified state table 작성 의무 — RequirementsPL self-write 시 verify-before-trust 가 정착. 4-claim ↔ 1-row mandatory format.

#### A2-2 — Wave 1 (behavioral) + Wave 2 (mechanical) progression chain

ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain (Amendment 1 §결정 6 정합):

| Wave | scope | enforcement | carrier |
|---|---|---|---|
| Wave 1 (Amendment 2) | §결정 1 (1-B) behavioral mandate | playbook §3.17 + story-page-structure.md §2.1 codification | CFP-1016 (본 carrier) |
| Wave 2 (후속 CFP) | mechanical lint — `issue_origin: orchestrator_authored_followup` 시 §2.1 verified state table 존재 + 4-column schema 정합 lint | `scripts/check-story-section-issue-origin.sh` (deferred-followup, ADR-060 §결정 5 모든 신규 entry warning 시작 강제 정합) | 후속 CFP (별 carrier, brainstorm 단계 결정) |
| Wave 3 (cross-repo, 후순위 ratchet) | RequirementsPL spawn prompt template (`mclayer/plugin-codeforge-requirements` — 현 `plugins/codeforge-requirements/`, 구 repo 삭제됨 2026-06-12) explicit verify-before-trust mandate | cross-repo PR (canonical sibling sync, CFP-1002 precedent) | 별도 canonical CFP carrier (wrapper-only Wave 1 우선, sibling sync 후순위 ratchet) |

Wave 2/3 = deferred-followup, 본 Amendment 2 frontmatter `mechanical_enforcement_actions[]` 갱신 0건 (Wave 1 = behavioral mandate + template codification, mechanical lint 자체는 Wave 2 carrier). Amendment 1 의 `corpus-claim-verify` + `cross-plugin-ownership-verify` 2 entry 유지 — 본 Amendment 2 scope (1-B) 와 disjoint sub-decision.

#### A2-3 — scope_boundary (out-of-scope)

본 Amendment 2 **포함**: §결정 1 layer 1 (Orchestrator scope) verify scope 의 (1-B) Issue body authorship time 명시적 codify + Wave 1 behavioral + template (a) + playbook (b).

본 Amendment 2 **out-of-scope** (유지/별 carrier):

- **(c) RequirementsPL spawn prompt template** mandate (canonical-side `mclayer/plugin-codeforge-requirements` repo) — cross-repo sibling sync 동반 가치 판단 영역, CFP-1002 precedent 정합 (wrapper-only Story 우선, cross-repo sibling sync 후순위 ratchet) → 별도 canonical CFP carrier.
- **Wave 2 mechanical lint** (`scripts/check-story-section-issue-origin.sh`) = 후속 CFP carrier (deferred-followup, brainstorm 단계 결정).
- ADR-073 frontmatter `mechanical_enforcement_actions[]` 변경 = ADR-073 본문 0건 변경 (cross-ref only — Amendment 2 가 §결정 1 layer 1 sub-scope 확장 명시 within ADR-082, ADR-073 본문은 Wave 1 cross-repo state verify scope 유지).
- 신규 ADR 창설 = Amendment only (ADR-RESERVATION 신규 row 0).

### Compatibility

- §결정 1~8 + §본질 선언 + §컨텍스트 (corpus 4건 → 7건 확장) + Amendment 1 전부 유지 — 본 Amendment 2 는 §결정 1 layer 1 sub-scope (1-B) 명시 codify + corpus 4/5/6 추가 only.
- ADR-058 §결정 5 sunset_justification — Amendment 2 = forbid scope 확장 (Orchestrator verify scope 가 cross-repo state assertion → Issue body authorship time 추가) = ratchet-up 강화 방향, `sunset_justification: "N/A — ratchet 강화 방향"` (frontmatter amendments[].sunset_justification verbatim, Amendment 1 sunset_justification format 답습). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 2-entry 유지 (Amendment 1 의 corpus-claim-verify + cross-plugin-ownership-verify, Amendment 2 가 Wave 2 deferred-followup 으로 declare only, frontmatter 갱신 0).
- ADR-073 (Orchestrator cross-repo state / assumption verify) = Wave 1 base scope 유지, Amendment 2 가 ADR-082 §결정 1 layer 1 sub-scope (1-B) 로 codify (ADR-073 본문 0건 변경, cross-ref only).
- ADR-054 doc-only fast-path = 본 Amendment 2 carrier (CFP-1016) 적격 (ADR Amendment + template 추가 + playbook 추가, src/tests 무변경 3-조건 AND PASS, ADR-054 정합).

### Related (Amendment 2 동반)

- `templates/story-page-structure.md` — §2.1 verified state table codification (mandatory when `issue_origin: orchestrator_authored_followup`) + `issue_origin` frontmatter field 신설
- `docs/orchestrator-playbook.md` — §3.17 신설 (Orchestrator-authored Issue body pre-publish verify mandate)
- `mclayer/codeforge-internal-docs/wrapper/{stories,change-plans}/CFP-1016*` — Amendment 2 carrier Story (doc-only fast-path 단일 PR pair)
- 후속 carrier (Wave 2 mechanical lint) = 별도 CFP, brainstorm 단계 결정
- 후속 canonical carrier (Wave 3 cross-repo) = 별도 CFP, RequirementsPL spawn prompt template mandate

---

## Amendment 3 — ADR-085 cross-ref (disjoint complement — verify axis ↔ coordination axis, CFP-1041, 2026-05-20 KST)

### 컨텍스트

ADR-082 base + Amendment 1 + Amendment 2 는 모두 **verify axis** (internal lane agent self-write 의 write-time semantic truth verify — §9 evidence / Phase 0 mapping / corpus enumeration / Orchestrator-authored Issue body authorship 영역). 그러나 **복수 Claude Code session 이 동일 repository / Story / branch 동시 작업 시 ownership 결정 / 분담 / handoff** 영역은 ADR-082 scope 외 — verify axis 아닌 coordination axis (pre-hoc cross-session). 8 parallel race incidents single session lineage (CFP-953/946/949/932/954/991/967/1014, 2026-05-18 ~ 2026-05-19 KST) 가 ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach escalation_action `adr_draft_emitted` 산물 — verify axis (ADR-073/070/082/045 §D) 가 모두 충족되어도 coordination axis 부재 시 parallel race 차단 불가.

### Amendment

ADR-085 (Multi-session collaboration protocol) 신설로 해당 gap 을 disjoint complement coordination axis layer 로 codify. ADR-082 ↔ ADR-085 = **disjoint complement 관계** (verify axis ↔ coordination axis):

- **ADR-082 (본 ADR)** = internal lane agent self-write 한정 (§9 evidence / Phase 0 mapping / corpus enumeration / Issue body authorship write-time semantic truth verify, **verify axis**)
- **ADR-085** = 복수 Claude Code session 동시 작업 시 ownership 결정 / 분담 / handoff (**coordination axis**, pre-hoc cross-session)

두 layer 는 **axis 자체가 다름** — verify axis 가 충족되어도 coordination axis 부재 시 parallel race 발생, coordination axis 결정 후에도 verify axis 미수행 시 false claim. 둘 다 필요한 orthogonal layer.

#### Amendment 3 — §결정 1 layer disjoint 5-layer 표 anchor (ADR-085 §결정 1 답습 base)

본 ADR §결정 1 layer disjoint **4-layer** 표 (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) 가 ADR-085 §결정 1 layer disjoint **5-layer** 표의 **verbatim 답습 base** — ADR-085 § 결정 1 5-layer 표 = 본 ADR §결정 1 4-layer 표 + 5번째 row "Multi-session coordination (ADR-085, coordination axis)" 신설.

| layer | ADR | scope | axis |
|---|---|---|---|
| 1 | ADR-073 | Orchestrator cross-repo state / assumption verify | verify (post-hoc cross-repo) |
| 2 | ADR-070 | Codex external worker output verify | verify (post-hoc external) |
| 3 | **ADR-082 (본 ADR)** | Internal lane agent §9 evidence / Phase 0 mapping / corpus enumeration write-time verify | verify (write-time internal) |
| 4 | ADR-045 §D | PMOAgent retro corpus enumeration cross-Story pattern_count escalation | verify (cross-Story pattern aggregator) |
| 5 | ADR-085 | Multi-session ownership / 분담 / handoff coordination | **coordination (pre-hoc cross-session)** |

본 ADR (ADR-082) = row 3 = verify axis (write-time internal). ADR-085 = row 5 = coordination axis (axis disjoint).

#### Amendment 3 — Cross-ref-only (본문 0건 변경 invariant)

본 Amendment 3 은 **cross-ref-only** — ADR-082 §결정 1-8 + Amendment 1-2 + 본문 §결정 / mechanism 의미 변경 0. ADR-085 §결정 1 5-layer 표 anchor 가 ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row 신설 (ADR-082 본문 0건 변경 invariant 보존). ADR-082 Amendment 1 ADR-073 cross-ref pattern verbatim 답습 (disjoint 보완 관계 cross-ref-only Amendment, mechanism scope 침범 0).

### Compatibility

- §결정 1~8 + §본질 선언 + §컨텍스트 (corpus 4건) + Amendment 1 + Amendment 2 전부 유지 — 본 Amendment 3 은 ADR-085 cross-ref 보완 관계 (disjoint complement) 명시 only.
- ADR-058 §결정 5 sunset_justification — Amendment 3 = cross-ref-only (disjoint complement 명시) = ratchet-up 강화 방향, `sunset_justification: null` (forbid scope 축소 아님). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 2-entry 유지 (Amendment 1 의 corpus-claim-verify + cross-plugin-ownership-verify, Amendment 3 frontmatter 갱신 0).
- ADR-073 (Orchestrator cross-repo state / assumption verify) = Wave 1 base + Amendment 1-2 + Amendment 4 (ADR-085 cross-ref) 동형 precedent — Amendment 4 cross-ref-only pattern 동일.

### Related (Amendment 3 동반)

- `docs/adr/ADR-085-multi-session-collaboration-protocol.md` — disjoint complement (verify axis ↔ coordination axis). ADR-085 §결정 1 5-layer 표 anchor 가 본 ADR §결정 1 4-layer 표 verbatim 답습 base.
- `mclayer/codeforge-internal-docs/wrapper/stories/CFP-1041.md` — Amendment 3 carrier Story
- `mclayer/codeforge-internal-docs/wrapper/change-plans/CFP-1041-multi-session-collaboration-protocol.md` — Change Plan (Phase 1 carrier)
- 후속 carrier (Wave 2 mechanical wire — active_sessions[] presence lint + lane-entry sentinel subprocess invoke) = 별 sub-CFP, ADR-085 §결정 8 deferred-followup carrier

---

## Amendment 4 — ADR-RESERVATION `amendments_reserved[]` sub-tree cross-ref (Amendment id race convention 형식화, CFP-1058, 2026-05-20 KST)

### 컨텍스트

CFP-1041 (Multi-session collaboration protocol Story-1) 진행 중 CFP-689 (ADR-073 Amendment 3 worktree-first self-ownership verify) 와 Amendment id race 발생. CFP-1041 carrier 가 ADR-082 Amendment 3 default 인용 → CFP-689 가 동일 Amendment 3 slot 점유 → CFP-1041 inline renumber 후 Amendment 4 로 진입. **race-winner-takes-it informal convention** 적용 (Amendment 번호 reservation field 부재) — formalize 의무.

ADR-RESERVATION 가 **ADR number** reservation field 보유하나 **Amendment id** reservation field 부재 → informal convention 만 적용. Amendment id race recurrence 차단 위해 schema codify 의무.

### Amendment

ADR-RESERVATION schema `amendments_reserved[]` sub-tree 신설 (CFP-1058 carrier) cross-ref. 본 Amendment 4 = ADR-082 본문 영역 변경 0 (cross-ref-only Amendment).

#### Amendment 4 — `amendments_reserved[]` sub-tree schema codify cross-ref

```yaml
amendments_reserved:
  - adr_number: <N>
    amendment_id: <M>
    reserved_by_cfp: <CFP-NNN>
    reservation_date: <YYYY-MM-DD KST>
    status: reserved | active | superseded
```

각 ADR Amendment 신설 의도 시 ArchitectAgent (chief author) 가 commit time 점유 직전 `amendments_reserved[]` row append → race-winner-takes-it 영역 reservation-then-commit 영역으로 전환. 본 schema = ADR-RESERVATION 의 기존 ADR number reservation field 옆 sibling sub-tree (file 신설 0, 단일 SSOT 정합).

#### Amendment 4 — Cross-ref-only (본문 0건 변경 invariant)

본 Amendment 4 는 **cross-ref-only** — ADR-082 §결정 1-8 + Amendment 1-3 본문 의미 변경 0. ADR-RESERVATION schema 확장 (`amendments_reserved[]` sub-tree 신설) 만 cross-ref. ADR-082 Amendment 3 ADR-085 cross-ref-only pattern + ADR-073 Amendment 4 cross-ref-only pattern verbatim 답습 (disjoint 보완 관계 cross-ref-only Amendment, mechanism scope 침범 0).

### Compatibility

- §결정 1~8 + §본질 선언 + §컨텍스트 (corpus 4건) + Amendment 1 + Amendment 2 + Amendment 3 전부 유지 — 본 Amendment 4 는 ADR-RESERVATION `amendments_reserved[]` sub-tree cross-ref only.
- ADR-058 §결정 5 sunset_justification — Amendment 4 = cross-ref-only (schema codify 강화 방향) = ratchet-up, `sunset_justification: null` (forbid scope 축소 아님). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 2-entry 유지 (Amendment 1 의 corpus-claim-verify + cross-plugin-ownership-verify, Amendment 4 frontmatter 갱신 0).
- ADR-082 Amendment 6+7 §결정 9 forcing function 정합 — `amendments_reserved[]` schema codify = Amendment id pre-reservation enables Wave 2 mechanical lint `amendment-number-frontmatter-verify` 의 reservation-aware 후속 확장 가능 (Wave N future carrier).

### Related (Amendment 4 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` sub-tree schema 신설 (Amendment id race convention 형식화)
- `mclayer/codeforge-internal-docs/wrapper/stories/CFP-1058.md` — Amendment 4 carrier Story
- `mclayer/codeforge-internal-docs/wrapper/change-plans/CFP-1058-adr-reservation-amendment-id.md` — Change Plan
- CFP-689 PR — Amendment id race winner evidence (race-winner-takes-it convention precedent)
- 후속 carrier (Wave 2 mechanical lint — `amendments_reserved[]` presence + reservation-aware Check (a) 확장) = 별 sub-CFP, deferred-followup

---

## Amendment 5 — Lane PL spawn prompt user-utterance verbatim anchor (CFP-1110, 2026-05-20 KST)

### 컨텍스트

본 Amendment 5 = **사용자 직권 minimal path 첫 적용** (paradox-break first application). 사용자 directive 2026-05-20 KST verbatim:

> "어쨌든 시간이 오래걸리든 비용이 많이 나오든 무관하게 성능이 제일 중요하다. 근데 시간도 오래걸리는데 레인이 지날수록 내가 요구했던 요건이 흩어지고 이상한 작업만 수행하는 것 같아서 그렇다."

본질 = **lane traversal fidelity loss** — 사용자 발화 원문이 lane 통과마다 재합성되며 weight 가 희석, lane 내부 invariant 가 그 자리를 차지하는 현상. Researcher (general-purpose) + Codex 병렬 critical evaluation 결과:

- Researcher: codeforge dogfooding net 35% 정당화 (verify-before-trust + Epic gate 영역만), 나머지 80% = self-burdening sunk cost cycle
- Codex: ROI indeterminate, 부정 쪽 기울기, confidence medium — denominator (consumer-protective fraction) 측정 부재
- 수렴: sunset asymmetry (실 retire 0건 since codeforge 정상 운영 진입), self-referential dogfood paradox 만성화, mechanical layer 가 race 차단 불가 입증

### pattern corpus 누적 evidence

| # | 출처 | 패턴 | count |
|---|---|---|---|
| 7a | CFP-722/801/792/810/819/825 | synthesizer-stale-reference (synthesis layer 원본 drift) | 6 |
| 7b | CFP-698 | Researcher agent fact drift (12 occurrence 정정) | 12 |
| 7c | CFP-758 | scope 재확대 금지 invariant 6+ 위치 박제 → scope drift 만성 evidence | 6+ |
| 7d | unverified-self-write-claim super-class (CFP-746/770/1000/1001/1002) | write-time semantic truth verify 부재 → ADR-082 carrier | 5 |
| 7e | CFP-906 | DesignReviewPL cross-PL false-negative (review 가 사실과 다른 결론) | 1 |

PMOAgent ADR-045 §D-9 정량 임계값: pattern_count **≥ 6** ≫ threshold 2 → Mandatory framing + escalation_action `escalate_user` → 사용자 단일 super-class 통합 결정 (본 Amendment 5 + paired ADR-071 Amendment 6).

### 구조적 원인 (3)

1. **Story §1 원문 → §2 Why / §3 Design 재합성 손실** — 매 lane PL spawn prompt 안 anchor 가 재합성된 weight 만 흘러간다. 사용자 원문 verbatim 이 lane prompt 안 1st-class anchor 가 아님.
2. **codeforge-design lane fan-out 불균형** — chief + 5 deputy + 4-tuple sub-tuple = 10+ agent advocacy. 1 user 요구 vs 10+ deputy mandate 의 weight 비대칭, deputy 가 자기 mandate 영역 expansion 만 강화 (cross-lane requirement traceability 약화).
3. **DialogFidelityAgent read-only** (ADR-071 §결정 13) — `post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause` 3-anchor 에서 divergence 검출은 가능하나, lane 재실행 강제 못함 (verifier 자체가 binding 약함) — paired ADR-071 Amendment 6 가 binding 강화 carrier.

### Amendment

#### A5-1 — §결정 1 layer 1 (Orchestrator scope) sub-scope (1-C) 신설

§결정 1 layer 1 (ADR-073) Orchestrator cross-repo state / assumption verify 의 적용 범위에 **Lane PL spawn prompt user-utterance verbatim anchor** 명시적 codify:

| sub-scope | trigger | verify 의무 |
|---|---|---|
| (1-A) lane spawn / cross-repo state assertion | lane 진입 시 외부 state 단정 | `git fetch origin` + `git show origin/main:<path>` + `verified-via` annotation (Wave 1 = ADR-073) |
| (1-B) Orchestrator-authored Issue body claim | Orchestrator 가 retro time / brainstorm Phase 0 후속 / ADR amendment carrier reservation / pattern_count escalation forcing function 산물로 Issue body 를 author 할 때 | Issue body 안 모든 `claim` source direct verify 후 author (Wave 1 = Amendment 2) |
| **(1-C) Orchestrator-authored lane PL spawn prompt** | **Orchestrator 가 lane PL agent (RequirementsPLAgent / ArchitectPLAgent / DesignReviewPLAgent / DeveloperPLAgent / CodeReviewPLAgent / SecurityTestPLAgent 등) 를 spawn 할 때** | **spawn prompt 첫 줄에 사용자 발화 원문 verbatim block 의무 부착 — 재합성 / 요약 / paraphrase / 합성문 weight 적용 금지. lane PL 의 self-write deliverable 은 본 verbatim anchor 를 source of truth 로 referencing 의무. Amendment 5 신설** |

verbatim block 형식:

```
[USER-UTTERANCE-VERBATIM]
> <사용자 원문 발화 verbatim, 한 글자 변형 없음>
[/USER-UTTERANCE-VERBATIM]
```

복수 사용자 발화 turn 시 multiple verbatim block 또는 chronological list 형태 허용. Story §1 가 이미 verbatim 보존 SSOT 이므로 spawn prompt = Story §1 발화 chunk 직접 quote (`git show origin/main:docs/stories/<KEY>.md` 또는 `mclayer/codeforge-internal-docs/<plugin>/stories/<KEY>.md` 직접 read-and-embed).

#### A5-2 — Citation ≠ Reframing 경계

본 Amendment 5 의 verbatim 의무는 **사용자 원문** 한정. Lane PL 이 spawn prompt 안에서 사용자 원문 verbatim block 위 / 아래 / 옆에 Orchestrator 자신의 합성 컨텍스트 (Story §2 Why / §3 Design 요약 / cross-lane reference) 를 추가하는 것은 허용 (§결정 4 citation ≠ assertion 경계 정합). 단:

- verbatim block 안 사용자 원문 자체 modify = 위반 (paraphrase 금지)
- verbatim block 부재 = 위반 (anchor 없이 합성문만 전달)
- verbatim block 위치 = spawn prompt **첫 줄** (anchor priority 보존, weight 희석 차단)

#### A5-3 — Wave 1 (behavioral) + Wave 2 (mechanical) progression chain

ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain (Amendment 1 §결정 6 / Amendment 2 §A2-2 정합):

| Wave | scope | enforcement | carrier |
|---|---|---|---|
| Wave 1 (Amendment 5) | §결정 1 (1-C) behavioral mandate | playbook §3.18 신설 (Orchestrator self-discipline — lane PL spawn prompt verbatim anchor 의무) + ADR-071 Amendment 6 paired (back-translation gate binding) | CFP-1110 (본 carrier) |
| Wave 2 (후속 CFP) | mechanical lint — `Agent` tool spawn prompt 안 `[USER-UTTERANCE-VERBATIM]` block presence + Story §1 발화 chunk match check | `scripts/check-spawn-prompt-user-utterance-anchor.sh` (deferred-followup, ADR-060 §결정 5 모든 신규 entry warning 시작 강제 정합) | 후속 CFP (별 carrier, brainstorm 단계 결정) |

Wave 2 = deferred-followup, 본 Amendment 5 frontmatter `mechanical_enforcement_actions[]` 갱신 0건 (Wave 1 = behavioral mandate + playbook codification, mechanical lint 자체는 Wave 2 carrier). Amendment 1 의 `corpus-claim-verify` + `cross-plugin-ownership-verify` 2 entry 유지 — 본 Amendment 5 scope (1-C) 와 disjoint sub-decision.

#### A5-4 — scope_boundary (out-of-scope)

본 Amendment 5 **포함**: §결정 1 layer 1 (Orchestrator scope) sub-scope (1-C) Lane PL spawn prompt user-utterance verbatim anchor 명시적 codify + Wave 1 behavioral + playbook §3.18 신설.

본 Amendment 5 **out-of-scope** (유지 / 별 carrier):

- **codeforge-design lane fan-out 축소** (chief + 5 deputy + 4-tuple = 10+ agent → 핵심 4-5 축소) — fidelity vs coverage trade, 별도 가치 판단 영역 → 별도 CFP carrier (brainstorm 단계 결정).
- **Wave 2 mechanical lint** (`scripts/check-spawn-prompt-user-utterance-anchor.sh`) = 후속 CFP carrier (deferred-followup).
- **back-translation gate binding** (lane return 직후 PL reverse summary + DialogFidelityAgent divergence detection trigger lane 재실행) = paired ADR-071 Amendment 6 SSOT (본 CFP-1110 동일 carrier, ADR 분리 — disjoint axis: 본 ADR = write-time input anchor / ADR-071 = return-time output gate).
- 신규 ADR 창설 = Amendment only (ADR-RESERVATION 신규 row 0).

### Compatibility

- §결정 1~8 + §본질 선언 + §컨텍스트 (corpus 4건 → 7건 확장 — 7a-e) + Amendment 1~4 전부 유지 — 본 Amendment 5 는 §결정 1 layer 1 sub-scope (1-C) 명시 codify + corpus 7a-e 추가 only.
- ADR-058 §결정 5 sunset_justification — Amendment 5 = forbid scope 확장 (Orchestrator verify scope 가 cross-repo state assertion + Issue body authorship → Lane PL spawn prompt user-utterance verbatim anchor 추가) = ratchet-up 강화 방향, `sunset_justification: "N/A — ratchet 강화 방향"` (frontmatter amendments[].sunset_justification verbatim, Amendment 1/2 format 답습). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 2-entry 유지 (Amendment 1 의 corpus-claim-verify + cross-plugin-ownership-verify, Amendment 5 가 Wave 2 deferred-followup 으로 declare only, frontmatter 갱신 0).
- ADR-071 (Orchestrator-user dialog convergence) = paired Amendment 5 sibling carrier (back-translation gate binding, 동일 CFP-1110 carrier). 두 ADR axis disjoint complement (write-time input ↔ return-time output).
- ADR-054 doc-only fast-path = 본 Amendment 5 carrier (CFP-1110) **부적격** (사용자 직권 minimal path = doc-only fast-path 우회 — Story file 0, Phase 1+2 분리 0, src 변경은 단 CLAUDE.md cross-ref + ADR Amendment 2종 only). ADR-013 명시 위배 (사용자 승인 2026-05-20 KST). closed-loop break 외부 결정 채널 — codeforge full flow 적용 시 본 평가 결과 (fidelity loss source) 자체 위배 paradox surface 회피.

### Related (Amendment 5 동반)

- `docs/adr/ADR-071-orchestrator-user-dialog-convergence.md` — paired Amendment 5 (back-translation gate binding, lane return 직후 verify, 동일 CFP-1110 carrier)
- `CLAUDE.md` — verify-before-trust 4-layer 표 단락 ADR-082 Amendment 5 + ADR-071 Amendment 6 cross-ref 1-2줄 (Orchestration 규칙 §"Lane 진입 시 skill 호출 의무" 표 안 동반)
- `mclayer/plugin-codeforge/issues/1110` — Amendment 5 carrier Issue (Story file 0 — 사용자 직권 minimal path)
- 후속 carrier (Wave 2 mechanical lint — `scripts/check-spawn-prompt-user-utterance-anchor.sh` + workflow + evidence-checks-registry warning tier entry) = 별 sub-CFP, brainstorm 단계 결정
- 후속 carrier (codeforge-design lane fan-out 축소 — 가치 판단 영역) = 별도 CFP, brainstorm 단계 결정

---

## Amendment 6 — Amendment 번호 citation plan-time staleness 차단 forcing function (CFP-1198, 2026-05-22 KST)

### 컨텍스트

ADR-045 §D-9 Mandatory escalation 산물 (pattern_count 2 ≥ threshold 2). 동일 세션 안에서 두 건의 plan-time amendment 번호 stale citation 이 발생 (write-time caught, land escaped 0):

- **CFP-1177 β-issue #1115**: 계획 "ADR-027 Amendment 7" → target ADR-027 frontmatter 미검증 → 실제 slot = Amendment 9 (Amendment 7·8 이미 CFP-1059 등 점유). stale citation 이 β-issue body 에 기재됨.
- **CFP-1179 β-issue #1114**: 계획 "ADR-063 Amendment 6/7" → target ADR-063 frontmatter 미검증 → 실제 slot = Amendment 8 (Amendment 6·7 이미 CFP-906/CFP-1059 점유). stale citation 이 β-issue body 에 기재됨.

두 케이스 모두 공통 root cause = **plan-time citation staleness** — governance artifact 작성 전 target ADR frontmatter `amendments:` 목록을 Read verify 하지 않은 채 amendment 번호를 기재. 기존 §결정 2(b) ("ADR frontmatter value 인용 시 verify") 가 이 영역을 포괄하나, plan-time artifact 에 대한 명시적 언급이 없어 forcing function 으로서 약했음 — 별도 §결정 9 로 명시적 codify.

root cause 분류: **write-time self-write verify 부재 (본 ADR scope)** ∩ **Orchestrator-authored artifact verify 부재 (ADR-073 scope)** — 두 layer 동시 적용 구조. 본 Amendment = ADR-082 layer (internal scope 포함 planning artifact 전반) 에서 forcing function codify, ADR-073 cross-ref 로 Orchestrator-authored β-issue 적용 명시.

### Amendment

#### A6-1 — §결정 9 신설 (Amendment 번호 citation verify 의무)

§결정 9 를 본 ADR 결정 섹션에 신설 (본 Amendment 6 본문 직전 `## 결과` 앞에 추가). 상세 내용 = §결정 9 본문 참조.

요약:
- governance artifact 안 ADR/contract amendment 번호 인용 전 target frontmatter `amendments:` 직접 Read → `max + 1` 사용 의무
- `verified-via: <Read 경로 및 시각>` annotation 부착 의무
- Orchestrator-authored artifact (β-issue body 등) = ADR-073 동시 적용 (disjoint layer 독립 적용)
- plan-time (β-issue / spec / change-plan 작성 시점) 을 명시적으로 포함

#### A6-2 — `mechanical_enforcement_actions[]` 신규 entry 추가

frontmatter `mechanical_enforcement_actions:` 에 아래 entry 추가:

| action | target_section | status | Phase 2 carrier |
|---|---|---|---|
| `amendment-number-frontmatter-verify` | §결정 9 | deferred-followup | CFP-1198 Phase 2 sub-carrier — governance artifact 안 amendment 번호 인용 위치 grep + target ADR frontmatter amendments: max 대비 stale 탐지 lint script + workflow + bats fixture |

status `deferred-followup` = Phase 1 declare (본 Amendment 6) / Phase 2 actual wire = 별도 CFP-1198 Phase 2 sub-carrier (ADR-060 §결정 5 모든 신규 entry warning 시작 강제 + ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain 정합).

#### A6-3 — ADR-073 cross-ref (Orchestrator-authored β-issue 적용 명시)

§결정 9 본문 내 disjoint layer 관계 표에 ADR-073 cross-ref 명시:
- β-issue body = Orchestrator-authored → ADR-073 §결정 1 (Orchestrator verify-before-assert) 동시 적용
- 본 ADR scope = internal lane agent self-write + planning artifact 포함 (§결정 9 신설)
- 두 ADR axis disjoint (verify subject overlap 아님) — 동일 artifact 에 독립 적용

본 Amendment 6 는 ADR-073 frontmatter 를 수정하지 않는다 (prose cross-ref only, ADR-073 frontmatter amendment 신설 0 — ADR-073 axis 침범 회피).

#### A6-4 — scope_boundary (out-of-scope)

본 Amendment 6 **포함**: §결정 9 신설 + `mechanical_enforcement_actions[]` 신규 entry + ADR-073 cross-ref prose.

본 Amendment 6 **out-of-scope** (유지 / 별 carrier):

- **Wave 2 mechanical lint** (`amendment-number-frontmatter-verify` script + workflow + bats fixture) = 별도 CFP-1198 Phase 2 sub-carrier (deferred-followup).
- **evidence-checks-registry row** = Phase 2 sub-carrier (deferred-followup — entry 신설 0, action name 선언만).
- **ADR-073 frontmatter amendment** = 0 (cross-ref only, ADR-073 §결정 1 확장 0).
- **label-registry Amendment** = 0 (hotfix-bypass family member 신설 불요 — behavioral mandate only Wave 1).
- 신규 ADR 창설 = 0.

### Compatibility

- §결정 1~8 + §본질 선언 + §컨텍스트 + Amendment 1~5 전부 유지 — 본 Amendment 6 는 §결정 9 신설 + `mechanical_enforcement_actions[]` entry 추가 + ADR-073 cross-ref 추가 only.
- ADR-058 §결정 5 sunset_justification — Amendment 6 = forbid scope 확장 (§결정 2(b) verify 대상이 plan-time amendment 번호 citation 으로 명시 확장) = ratchet-up 강화 방향. `sunset_justification: "N/A — ratchet 강화 방향"` (frontmatter amendments[].sunset_justification 명문). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 3-entry 보유 (Amendment 1 의 2 entry + Amendment 6 신설 1 entry).
- ADR-068 I-4 (wording SSOT) 연계: amendment 번호 = governance artifact 전체 참조 식별자 → stale 번호 기재 시 I-4 위반 원인 → §결정 9 가 I-4 위반 upstream 차단.
- ADR-045 §D-9: 본 Amendment 6 가 pattern_count 2 Mandatory escalation 의 직접 산물 (escalation_action `adr_draft_emitted`).
- 본 Amendment 6 자체가 META-self-applied: Amendment 번호(6) 가 target ADR-082 frontmatter `amendments:` Read verify (max=5, next=6) 후 결정 — §결정 9 를 도입하는 이 Amendment 6 자체가 §결정 9 를 준수하는 첫 사례 (verified-via: Read `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] 2026-05-22 KST).

### Related (Amendment 6 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — cross-ref: β-issue = Orchestrator-authored artifact 이므로 ADR-073 §결정 1 동시 적용 (frontmatter 수정 0, prose cross-ref only)
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — §D-9 Mandatory escalation 산물 (pattern_count 2, CFP-1177+CFP-1179 lineage)
- `docs/adr/ADR-068-boundary-completeness-invariants.md` — I-4 wording SSOT upstream 차단 연계 (amendment 번호 stale → I-4 wording drift 원인)
- 후속 carrier (Wave 2 mechanical lint — `amendment-number-frontmatter-verify` script + workflow + bats fixture + evidence-checks-registry warning tier entry) = CFP-1198 Phase 2 sub-carrier (deferred-followup)

---

## Amendment 7 — §결정 9 verify-before-cite scope 양방향 확장 + CFP-1216 lint Check (b) backward-staleness wire (CFP-1312, 2026-05-23 KST)

### 컨텍스트

ADR-082 Amendment 6 (CFP-1198, 2026-05-22 KST) 가 §결정 9 신설 + `amendment-number-frontmatter-verify` deferred-followup entry declare. CFP-1216 Phase 2 (2026-05-22 KST) 가 별도 sub-carrier 로 Wave 2 mechanical lint 를 land 완료 — `scripts/lib/check_amendment_number_stale.py` (Python SSOT) + `scripts/check-amendment-number-stale.sh` (thin wrapper, ADR-061 §결정 6.A) + `templates/github-workflows/amendment-number-frontmatter-verify.yml` + `.github/workflows/amendment-number-frontmatter-verify.yml` (self-app) + `tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats` + `docs/evidence-checks-registry.yaml` entry (warning tier).

**recurrence evidence (#3 occurrence)**: CFP-1293 (#1293, 2026-05-23 KST close) 가 Amendment 6 Wave 1 behavioral mandate land + CFP-1216 Phase 2 mechanical lint active **이후** 동일 패턴 재발:

- stale citation = `ADR-083 Amendment 2`
- target ADR-083 frontmatter 실제 max = Amendment 2 시점 (이미 land)
- 정확 next-slot = `max+1 = 3` → cited_m=2 이므로 **`M ≤ max`** = **backward-staleness** 패턴 (이미 land 된 slot 인용)

CFP-1216 lint Check (b) 본문 verify (`git show origin/main:scripts/lib/check_amendment_number_stale.py` 2026-05-23 KST 기준 origin/main bfc4806):

```python
# Check (b): cross-doc citation forward-staleness
def check_doc_citations(filepath, adr_max_cache):
    ...
    if cited_m > max_id + 1:
        print(f"... possible stale-forward citation", file=sys.stderr)
        warn_count += 1
```

`cited_m > max_id + 1` 비교 = **forward-only** (M > max+1). `M ≤ max` (backward-staleness) 영역 미coverage = lint **escape evidence**. Wave 1 behavioral mandate 단독 불충분 결론 아님 — Wave 2 mechanical lint coverage gap (forward only) 으로 backward escape.

**root cause 분류**:
- **(a) Wave 1 behavioral 단독 불충분 가설** = REJECTED (CFP-1216 Phase 2 mechanical lint active 영역 verified, lint 실 wire 후 발생).
- **(b) lint coverage gap (Check (b) forward-only 비교)** = CONFIRMED (`cited_m > max_id + 1` line verified, `cited_m != max_id + 1` 양방향 비교 부재).

ADR-045 §D-9 pattern_count 3 reach (CFP-1177 + CFP-1179 + CFP-1293 #3) ≥ threshold 2 — Mandatory escalation 산물 `adr_draft_emitted`.

### Amendment

#### A7-1 — §결정 9 wording 양방향 확장 (Wave 1 behavioral mandate scope expand)

§결정 9 본문 `verify-before-cite 의무` 3번 항목 wording 양방향 확장:

**기존 (Amendment 6, CFP-1198)**:
> 3. 새 amendment 번호 = `max(amendment_id) + 1` 로 결정한다.

**Amendment 7 (CFP-1312)**:
> 3. 새 amendment 번호 = **정확히 `max + 1`** 로 결정한다 (Amendment 7 명시 — `M = max+1` 외 모두 stale). forward (M > max+1) / backward (M ≤ max) 양방향 staleness 차단.

§결정 9 본문 forcing function 첫 문장도 양방향 명시 확장 — `정확 next-slot M = max(amendment_id) + 1 만 사용한다` + `M > max + 1` (forward) / `M ≤ max` (backward) 모두 stale citation. wording 의미 변경 = forbid scope 확장 (정확 next-slot 외 모두 stale, ratchet 강화 방향).

#### A7-2 — CFP-1216 lint Check (b) 양방향 비교 확장 (Wave 2 mechanical wire — coverage gap 보강)

`scripts/lib/check_amendment_number_stale.py` `check_doc_citations()` 함수 안 `cited_m > max_id + 1` 비교를 **양방향 next-slot mismatch** 로 확장:

**기존 (CFP-1216, line 357 region)**:
```python
if cited_m > max_id + 1:
    print(f"... possible stale-forward citation", file=sys.stderr)
    warn_count += 1
```

**Amendment 7 (CFP-1312)**:
```python
if cited_m != max_id + 1:
    if cited_m > max_id + 1:
        label = "[FORWARD-STALE]"
        detail = f"M={cited_m} > max+1={max_id + 1} — forward staleness (off-by-one / 계산 오류)"
    else:  # cited_m <= max_id
        label = "[BACKWARD-STALE]"
        detail = f"M={cited_m} ≤ max={max_id} — backward staleness (이미 land 된 slot 인용)"
    print(
        f"{SCRIPT_NAME} [WARN] {filepath}: ADR-{adr_num} Amendment {cited_m} 인용 "
        f"but ADR-{adr_num} max = {max_id} (next = {max_id + 1}) — {label} {detail}",
        file=sys.stderr,
    )
    warn_count += 1
```

self-reference exemption (FP-완화 guard 1): ADR file 자체 (`docs/adr/ADR-*.md`) 의 `## Amendment N` 본문 안 자기 인용 = lint scope 제외 (Check (b) 의 non-ADR docs/** filter 가 이미 보장 — file path 기반 ADR file 식별 confirm).

templates/** path filter (FP-완화 guard 2): `templates/story-page-structure.md` / `templates/adr.md` 등 canonical example 안 amendment 인용 = lint scope 제외 (`templates/` prefix 기반 path exclusion).

#### A7-3 — bats fixture 양방향 TC 추가 (`tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats`)

기존 fixture (CFP-1216 Phase 2 land) 확장 — backward-staleness 3+ TC 추가:

| TC name | fixture | 기대 출력 | rationale |
|---|---|---|---|
| TC-B-BWD-EXACT | target ADR-999 max=3, doc cites "ADR-999 Amendment 3" | `[BACKWARD-STALE]` [WARN] exit 0 | M=max (이미 land 된 latest slot 자기 인용 backward) |
| TC-B-BWD-DEEP | target ADR-999 max=3, doc cites "ADR-999 Amendment 1" | `[BACKWARD-STALE]` [WARN] exit 0 | M < max (deep backward — historical slot 인용) |
| TC-B-FWD-EXACT-NEXT | target ADR-999 max=3, doc cites "ADR-999 Amendment 4" | PASS no [WARN] | M = max+1 (정확 next-slot — false-positive 0 verify) |
| TC-B-SELF-REF-EXEMPT | docs/adr/ADR-999.md 안 자기 `Amendment 2` 인용 | PASS no [WARN] | ADR file 자체 → Check (b) non-ADR filter 가 skip |
| TC-B-TEMPLATE-EXEMPT | templates/test-fixture.md 안 `ADR-999 Amendment 99` 인용 | PASS no [WARN] (또는 별도 path exclusion) | templates/** canonical example 면제 (path filter guard 2) |

기존 TC-B1 (Amendment 99 way-forward) / TC-B2 (Amendment 2 with max=3 정상 — Amendment 6 기존 정의에서 PASS) 는 Amendment 7 wording 정확화 후 영향:
- TC-B1 (Amendment 99 > max+1=4) → `[FORWARD-STALE]` retain (regression 0 — AC-2)
- TC-B2 (Amendment 2 with max=3) → 기존 Amendment 6 = "M ≤ max + 1 정상" 가정 → Amendment 7 = "M = max+1 만 정상, M=2 ≤ max=3 = backward stale" 으로 의미 변경. **CFP-1216 fixture rename + behavior 변경 의무 (FIX iter — TC-B2 expected output `PASS` → `[BACKWARD-STALE]` [WARN]`)**.

#### A7-4 — evidence-checks-registry entry summary 갱신 (`docs/evidence-checks-registry.yaml`)

`amendment-number-frontmatter-verify` entry `description` field summary 양방향 명시:

**기존 (CFP-1216)**:
> Check (b) cross-doc citation forward-staleness (SECONDARY): ... M > max+1 이면 [WARN] (clearly-forward only, M <= max 는 정상 인용 — skip).

**Amendment 7 (CFP-1312)**:
> Check (b) cross-doc citation 양방향 staleness (SECONDARY, Amendment 7 확장): ... M != max+1 이면 [WARN] — `M > max+1` = `[FORWARD-STALE]` / `M ≤ max` = `[BACKWARD-STALE]`. 정확 next-slot M=max+1 외 모두 stale.

`current_tier` warning retain (scope expand only, blocking-on-pr 승격 영역 외). `bypass_label` `hotfix-bypass:amendment-number-stale` retain.

#### A7-5 — scope_boundary (out-of-scope)

본 Amendment 7 **포함**:
- §결정 9 wording 양방향 확장 (Wave 1 behavioral)
- `scripts/lib/check_amendment_number_stale.py` Check (b) 양방향 비교 확장 (Wave 2 mechanical)
- `tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats` backward-staleness TC 3+ 추가 + 기존 TC-B2 expected output 정정
- `docs/evidence-checks-registry.yaml` entry summary 갱신 (양방향 codify)
- `plugin.json` PATCH bump 6.5.1 → 6.5.2 + marketplace sibling sync (ADR-063 §결정 1)
- `CHANGELOG.md` PATCH entry append

본 Amendment 7 **out-of-scope** (유지 / 별 carrier):
- `evidence-checks-registry.yaml` `current_tier` 승격 (warning → blocking-on-pr) = ADR-060 §결정 6 (d) gate 미충족 영역 (별 carrier).
- `templates/github-workflows/amendment-number-frontmatter-verify.yml` paths trigger 확대 = 0 (현재 docs/adr/ADR-*.md + docs/change-plans/** + docs/inter-plugin-contracts/** retain).
- `.github/workflows/amendment-number-frontmatter-verify.yml` self-app = byte-identical mirror retain (변경 0).
- PMOAgent false-positive tally 별도 axis carrier = OOS (Story §6.2 OOS-1, 별도 ADR escalation candidate).
- 신규 ADR 창설 = 0 (Amendment 만).
- `label-registry-v2` Amendment = 0 (`hotfix-bypass:amendment-number-stale` 67번째 family member retain).

### Compatibility

- §결정 1~8 + §결정 9 (Amendment 6 신설) + 본질 선언 + 컨텍스트 + Amendment 1~6 전부 유지 — 본 Amendment 7 는 §결정 9 wording 양방향 확장 + CFP-1216 lint Check (b) 양방향 비교 wire + bats fixture TC 추가 + registry entry summary 갱신 + plugin.json PATCH + CHANGELOG append only.
- ADR-058 §결정 5 sunset_justification — Amendment 7 = forbid scope 확장 (`M = max+1` 정확 next-slot 외 모두 stale, forward only → 양방향) = ratchet-up 강화 방향. `sunset_justification: "N/A — ratchet 강화 방향"` (frontmatter amendments[].sunset_justification 명문). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — 약화 방향 0건). §결정 5 CFP scope unitary 정합 — dual-carrier (wording + lint wire) = 동일 axis 단일 Story.
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 3-entry retain (Amendment 1 의 2 entry + Amendment 6 의 `amendment-number-frontmatter-verify` entry, Amendment 7 = 기존 entry summary 갱신 only — 신규 entry 신설 0).
- ADR-068 I-4 (wording SSOT) 연계 강화 — `M = max+1` 만 정확 next-slot 으로 wording unify (backward / forward 모호성 제거).
- ADR-045 §D-9: 본 Amendment 7 가 pattern_count 3 Mandatory escalation 의 직접 산물 (escalation_action `adr_draft_emitted`).
- ADR-061 §결정 1 + 6.A 정합 — Python SSOT 본문 수정 (>5줄 multi-line) + thin wrapper 변경 0 retain.
- ADR-063 §결정 1 atomic invariant — `plugin.json` PATCH bump → marketplace sibling sync PR 의무 (mirrored field 4종 중 `version` 변경).
- ADR-068 I-4 wording SSOT 정합 — `[FORWARD-STALE]` / `[BACKWARD-STALE]` 출력 prefix 분리 = wording dedup (FP / BWD 의미 구별 codify).
- 본 Amendment 7 자체가 META-self-applied: Amendment 번호(7) = target ADR-082 frontmatter `amendments:` Read verify (origin/main bfc4806 max=6, next=7) 후 결정 — §결정 9 Amendment 7 양방향 확장 wording 을 도입하는 본 Amendment 7 자체가 동 §결정 9 (Amendment 6 + Amendment 7) 를 준수하는 두 번째 META-self-applied 사례 (verified-via: Read `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] 2026-05-23 KST origin/main bfc4806).

### Related (Amendment 7 동반)

- `scripts/lib/check_amendment_number_stale.py` — Check (b) 양방향 비교 + `[FORWARD-STALE]` / `[BACKWARD-STALE]` 출력 format 분리
- `tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats` — backward-staleness TC 3+ 추가 + TC-B2 expected output 정정 (TC-B2 = M=2 ≤ max=3 backward) + self-ref exempt + template exempt TC
- `docs/evidence-checks-registry.yaml` — `amendment-number-frontmatter-verify` entry description 양방향 codify
- `.claude-plugin/plugin.json` — PATCH bump 6.5.1 → 6.5.2
- `CHANGELOG.md` — PATCH entry append
- `mclayer/marketplace` repo — `marketplace.json` plugins[name=codeforge] mirrored field 4종 (`version`) atomic sibling PR (ADR-063 §결정 1)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row append (ADR-082 Amendment 7 reservation → active 전환 commit time, sibling pattern ADR-083 Amendment 3 CFP-1293)
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — §D-9 pattern_count 3 evidence #3 (CFP-1293)
- `docs/adr/ADR-061-python-script-writing-convention.md` — §결정 1 (Python SSOT) + §결정 6.A (thin wrapper convention) 정합
- `docs/adr/ADR-063-marketplace-atomic-invariant.md` — §결정 1 (mirrored field atomic) 정합
- `docs/adr/ADR-068-boundary-completeness-invariants.md` — I-4 wording SSOT 연계 강화 (정확 next-slot wording unify)

---

## Amendment 8 — §결정 10 신설 (ArchitectAgent write-time discipline 4 sub-scope, CFP-1329, 2026-05-24 KST)

**결정**: ADR-082 super-class (write-time semantic truth verify) 안 ArchitectAgent chief author write-time discipline 4 sub-scope codify — §결정 10.A (Codex TP#2 inline FIX 8-anchor mirror coverage checklist) + §결정 10.B (mid-author partial revert propagation gap sentinel codify rationale) + §결정 10.C (ArchitectAgent self-introduced script-behavior claim verify) + §결정 10.D (META self-application pattern).

**근거**: 4 memory entry normative 승격 carrier — `feedback_codex_tp2_verify_before_trust_pattern` (CFP-795 F-1 sentinel — Codex TP#2 inline FIX 8-anchor mirror coverage checklist 도구적 가치) / `feedback_mid_author_partial_revert_propagation_gap` (CFP-1009 dogfood inversion P1 sentinel — body normative correction ↔ frontmatter inline comment / appendix / table cell propagation 의무) / `feedback_architect_script_behavior_claim_verify` (CFP-1006 F-DR-1006-1 + CFP-1025 hypothesis refuted, pattern_count 2 reach — script behavior assertion write-time empirical verify + DesignReviewPL audit point) / `feedback_meta_self_application_pattern` (CFP-1016 1st applied + CFP-1340 Amendment 2 §결정 15 2nd applied, pattern_count 2 reach — Story introduces codification → carrier Story 자체에 1st applied). pattern_count evidence 혼합: §결정 10.A=1 (sentinel forward-prevention) / §결정 10.B=1 (sentinel forward-prevention) / §결정 10.C=2 reach / §결정 10.D=2 reach. ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated ratchet 정합 — sentinel forward-prevention (10.A+10.B) = 도구적 가치 evidence base, recurrence threshold 2 reach (10.C+10.D) = standard pattern_count base. 혼합 ratchet 정직 명시.

**영향**: ADR-082 §결정 1 layer 1 + §결정 2 scope (a-d) write-time verify mandate 가 ArchitectAgent chief author write-time discipline 4 sub-scope 영역으로 확장 (forbid scope 축소 0건). Wave 1 = declaration-only (4 sub-decisions 모두 behavioral directive). Wave 2 mechanical wire (DesignReviewPL audit dedicated points + ArchitectAgent self-discipline grep self-check) = 별도 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

**Cross-ref**: ADR-039 lane self-write boundary 정합 (lane plugin agent md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제) / ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향) / META-self-applied (§결정 10.D 3rd applied case — 본 Amendment 8 의 본 ADR-082 frontmatter amendments[] Read verify origin/main d24ab28 max=7 → next=8 결정).

---

## Amendment 9 — §결정 11 신설 (Code-level write-time discipline 2 sub-scope, CFP-1330, 2026-05-24 KST)

**결정**: ADR-082 super-class (write-time semantic truth verify) 안 Code-level write-time discipline 2 sub-scope codify — §결정 11.A (test code production binding verify — sed-extract real fn, sentinel forward-prevention CFP-1025 F-CR-1025-2) + §결정 11.B (script error visibility audit — `2>/dev/null` mis-diagnosis amplifier META-ROOT, sentinel forward-prevention CFP-1025 bootstrap-labels.sh:53-55).

**근거**: 2 memory entry normative 승격 carrier — `feedback_test_must_bind_to_production` (CFP-1025 F-CR-1025-2 sentinel — regression bats/unit test = real production code source/exec 의무) / `feedback_error_mask_metaroot` (CFP-1025 bootstrap-labels.sh:53-55 META-ROOT sentinel + CFP-1006 mis-diagnosis lineage verified — script `2>/dev/null` 가 success/failure 보고 시 real error 마스킹 = mis-diagnosis amplifier META-ROOT). pattern_count evidence: §결정 11.A=1 (sentinel forward-prevention — test-quality regression coverage gap silent risk) / §결정 11.B=1 (sentinel forward-prevention — META-ROOT severity = mis-diagnosis 전파 chain risk, CFP-1006 mis-diagnosis lineage downstream propagation verified). ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 정합 — sentinel forward-prevention (11.A+11.B) = 도구적 가치 evidence base (recurrence ≥ 2 wait 시 silent regression / mis-diagnosis 전파 risk).

**영향**: ADR-082 super-class scope expansion = Amendment 8 (ArchitectAgent write-time discipline §결정 10) + 본 Amendment 9 (Code-level write-time discipline §결정 11) layer 양 layer 분할 (governance write-time ↔ code write-time disjoint axis). Wave 1 = declaration-only (2 sub-decisions 모두 behavioral directive). Wave 2 mechanical wire (CodeReviewPL audit dedicated points — tautology smell grep + `Grep '2>/dev/null' scripts/**` resource-creating/state-changing audit + codeforge-wide grep audit sweep) = 별도 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

**Cross-ref**: ADR-039 lane self-write boundary 정합 (codeforge-review CodeReviewAgent.md / codeforge-develop QADeveloperAgent.md lane plugin cross-ref = follow-up defer) / META-self-applied (§결정 10.D 4th applied case — 본 Amendment 9 의 본 ADR-082 frontmatter amendments[] Read verify origin/main a0eb545 max=8 → next=9 결정).

---

## Amendment 10 — §결정 12 신설 (RequirementsPL + retro-time verify-before-trust 2 sub-scope, CFP-1332, 2026-05-24 KST)

**결정**: ADR-082 super-class scope expansion = Amendment 2 (Issue-body authorship verify §결정 1 layer 1) RequirementsPL §2.1 codify strengthening + retro-time verify-before-trust axis 추가 — §결정 12.A (Orchestrator-authored Issue body §2.1 verified state table mandate strengthening, pattern_count 2 reach: CFP-1000 INVERSE drift + CFP-1001 lint output FP) + §결정 12.B (Retro-time wave_defer empirical verify, pattern_count 2 reach: CFP-1006 Wave-defer rationale falsified post-merge + CFP-1025 corrective closure pattern WORKING).

**근거**: 2 memory entry normative 승격 carrier — `feedback_issue_body_verify_before_trust` (RequirementsPL spawn prompt MUST include explicit verify-before-trust mandate + §2.1 verified state table 의무 + Issue-body claim direct verify: reproduce lint / file Read line numbers / gh CLI probe gh-side state / file existence check) / `feedback_wave_defer_empirical_verify` (retro time PMOAgent/Orchestrator 가 deferral rationale empirical verify: workflow X actual produced state post-merge / lint Y actually catches deferred concern / backward-compat scenario actual run). pattern_count 2 reach 양 sub-decision evidence-gate 통과. ADR-082 super-class disjoint axis expansion (write-time + retro-time, 단일 super-class 안 disjoint lifecycle layer).

**영향**: write-time (Amendment 1-9) + retro-time empirical verify (본 Amendment 10 §결정 12.B) 양 lifecycle expansion (forbid scope 축소 0건). Wave 1 = declaration-only behavioral mandate. Wave 2 mechanical wire (RequirementsPL §2.1 lint + retro empirical-verify-required marker) = 별도 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

**Cross-ref**: ADR-039 lane self-write boundary 정합 (codeforge-requirements RequirementsPLAgent.md / codeforge-pmo PMOAgent.md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제) / META-self-applied (§결정 10.D 5th applied case — 본 Amendment 10 의 본 ADR-082 frontmatter amendments[] Read verify origin/main 38fc8ff max=9 → next=10 결정).

---

## Amendment 11 — §결정 13 신설 (GitOps verify-before-trust discipline 3 sub-scope, CFP-1338, 2026-05-24 KST)

**결정**: GitOps verify-before-trust discipline 3 sub-scope codify — §결정 13.A (main_drift_bypass_audit_pattern, pattern_count 5 reach HIGH) + §결정 13.B (HEAD SHA pin step 0, ADR-073 sub-discipline) + §결정 13.C (branch protection worktree cleanup 순서, ADR-024+040 cross-ref).

**근거**: 3 memory entry normative 승격 carrier — `feedback_main_drift_bypass_audit_pattern` (pattern_count 5 reach HIGH: CFP-963 P1+P2 + CFP-1000 + CFP-1001 + CFP-1340/1329/1330/1332 batch 4-bypass label lineage — 4 standard hotfix-bypass labels + `[bypass-justification]` audit comment template + ADR-024 Amendment 3 §결정 6.C audit trail mandate cross-ref) / `feedback_verify_pin_head_sha` (CFP-722 stale HEAD verification churn sentinel — HEAD SHA pin step 0 `gh api repos/<owner>/<repo>/commits/<branch> --jq '.sha'` before any commit/branch verify-before-trust, ADR-073 sub-discipline cross-ref) / `feedback_branch_protection_worktree_cleanup` (branch protection 환경 workflow discipline — push → PR open → merge 확인 → worktree 정리 순서 의무, ADR-024 + ADR-040 cross-ref). pattern_count 5 reach 13.A + sentinel forward-prevention 13.B/13.C 혼합 ratchet.

**영향**: ADR-082 super-class scope expansion to GitOps coordination layer (write-time + retro-time + GitOps coordination 3-axis 통합). Wave 1 = declaration-only behavioral mandate. Wave 2 mechanical wire = 별도 sub-carrier (deferred-followup).

**Cross-ref**: ADR-039 lane self-write boundary 정합 (codeforge-pmo GitOpsAgent.md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제) / META-self-applied (§결정 10.D 6th applied case — 본 Amendment 11 의 본 ADR-082 frontmatter amendments[] Read verify origin/main e7b7791 max=10 → next=11 결정).

---

## Amendment 12 — §결정 14 신설 (PMOAgent retro batch closure pattern workflow codify, CFP-1339, 2026-05-24 KST)

**결정**: PMOAgent retro batch closure pattern codify — multi follow-up CFP candidates batch-create simultaneously + sequential doc-only fast-path execution single session pattern + same lane execution pattern (Combined Req+Design lane / mechanical_fast_path_inline DesignReview / FLUID bypass label set).

**근거**: 1 memory entry normative 승격 carrier — `feedback_cfp_retro_batch_closure_pattern` (CFP-963 retro 4-batch precedent + CFP-1340/1329/1330/1332/1338/1339 본 6-CFP batch 2nd applied case, pattern_count 2 reach). workflow efficiency evidence: CFP-963 ~6h for 4 Stories / 본 6-CFP batch ~10-12h for 6 consecutive Stories.

**영향**: ADR-082 super-class scope expansion to retro-emission batch closure workflow axis (write-time + retro-time + GitOps coordination + retro batch closure layer 4-axis 통합). Wave 1 = declaration-only behavioral mandate (workflow pattern codify). Wave 2 mechanical wire = 별도 sub-carrier (deferred-followup).

**Cross-ref**: 본 Amendment 12 = CFP-1340 5-CFP batch 마지막 CFP carrier — META-self-application 7th applied case + 본 batch closure 자체가 §결정 14 pattern WORKING evidence (§결정 10.D 7th applied case — 본 Amendment 12 의 본 ADR-082 frontmatter amendments[] Read verify origin/main c36ee92 max=11 → next=12 결정).

---

## Amendment 13 — §결정 10.D META self-application pattern Wave 2 mechanical wire declarative anchor (CFP-1390, 2026-05-24 KST)

**결정**: §결정 10.D META self-application pattern Wave 2 mechanical wire declarative anchor (CFP-1346 retro F2-FU Optional follow-up carrier). Wave 2 actual mechanical wire (detection logic for Story-self codification 1st applied case) = 별 sub-CFP carrier deferred-followup. `mechanical_enforcement_actions: [meta-self-application-wire]` 신설 placeholder declarative-only (실 wire = Wave 2).

**근거**: pattern_count cumulative 5 reach — CFP-1016 1st applied (Amendment 2 Issue-body authorship verify 본 carrier 자체 META first applied) / CFP-1340 §결정 15 2nd applied (5-CFP batch Story file initial scaffold) / CFP-1329 Amendment 8 3rd applied (§결정 10.D 본문 codify 자체가 META self-applied) / CFP-1346 ADR-108 §결정 6 4th applied (description '74번째' claim = raw post-append count 74 PARITY) / 본 Amendment 13 5th applied (META self-applied — 본 Amendment 가 §결정 10.D pattern 의 declarative ratchet 강화 carrier). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합.

**영향**: ADR-082 §결정 10.D META self-application pattern normative codify 의 mechanical wire declarative placeholder Wave 1 (forbid scope 축소 0건). 본 Issue = declaration-only anchor + amendment_log entry 갱신 only — actual lint script + workflow + bats fixture wire = 별 sub-CFP.

**Cross-ref**: ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향) / ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합 / META-self-applied (5 reach: CFP-1016+1340+1329+1346+1390 sequential applied lineage).

---

## Amendment 14 — §결정 1 layer 1 sub-scope (1-D) 신설 (cross-repo label-write authority verify mandate, CFP-1336, 2026-05-24 KST)

### 동기

CFP-1302 follow-up F2 carrier — D-4 chief dissent carry. cross-repo wrapper Issue ↔ impl repo PR labels bidirectional sync 영역에서 (1) wrapper Story Issue label 변경이 impl repo PR label 로 자동 propagate 되지 않아 drift 발생 (예: phase 전환 / FIX 라벨 / hotfix-bypass:* family member append). (2) impl repo PR label 변경이 wrapper Story Issue 로 reverse propagate 되지 않아 mirror inversion 위험. (3) cross-org sync 미차단 시 GitHub PAT scope leakage 영역 expand. (4) `verified-via` annotation 부재 시 label state ground truth verification 불가.

기존 4-layer verify-before-trust 안 layer 3 (ADR-082 §결정 1) 의 sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) 가 모두 read-time verify 또는 write 직전 fidelity check 영역. label state 변경 직전 **write authority verify** axis 는 disjoint sub-scope — 본 Amendment 가 sub-scope 1-D 신설로 anchor.

ADR-073 Amendment 9 (`label_change` transition trigger, lane-entry sentinel polling) 와 paired Amendment carrier (같은 CFP-1336 Story 안). ADR-073 = transition 시점 polling 의무 (when), ADR-082 sub-scope 1-D = write 직전 authority verify (what + who-can-write). dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair).

### Amendment

#### §결정 1 layer 1 sub-scope (1-D) 신설 — cross-repo label-write authority verify-before-write 4-tuple primitive

ADR-082 §결정 1 의 4-layer 표 안 layer 1 (Orchestrator scope) sub-scope 확장:

- **sub-scope (1-A)** = cross-repo state verify (read-time, ADR-073 base)
- **sub-scope (1-B)** = Orchestrator-authored Issue body authorship pre-publish verify (write-time, Amendment 2 신설)
- **sub-scope (1-C)** = Orchestrator-authored lane PL spawn prompt user-utterance verbatim anchor (write-time, Amendment 5 신설)
- **sub-scope (1-D) — 신설 (Amendment 14)** = cross-repo label-write authority verify-before-write (write-time, 4-tuple primitive):
  - **(a) wrapper → impl write authority**: wrapper Story Issue label 변경 → impl repo PR label sync write 권한 verify. CODEFORGE_CROSS_REPO_PAT scope `issues:write` (ADR-066 §결정 2 Amendment 4 cross-ref) 보유 확인 + repo scope membership verify.
  - **(b) impl → wrapper write authority**: impl repo PR label 변경 → wrapper Story Issue label sync write 권한 verify. `sender.type ≠ Bot` (loop prevention) OR `sender.login ∈ actor-allowlist` 정합.
  - **(c) cross-org block**: mclayer org only — `repo.owner ≠ mclayer` 시 sync skip + audit log. cross-org sync 시도는 PAT scope leakage 영역 expand 위험.
  - **(d) verified-via annotation**: 모든 cross-repo label state 인용 옆 `[verified-via: <gh api / direct read> pinned_at: <SHA/timestamp>]` tag 의무. label state ground truth verification 가능 형식.

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `cross-repo-label-sync` warning-tier deferred-followup append. Wave 2 mechanical wire (workflow runtime activation + bats fixture + bidirectional sync state lint) = 별도 sub-carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — ADR-070 D5 retain 패턴 / ADR-076 / ADR-086).

#### ADR-073 Amendment 9 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair)

ADR-073 Amendment 9 §결정 1 transition trigger enum 안 `label_change` 신규 entry — lane-entry sentinel polling 시점 label transition 발견 시 sentinel pickup 의무 (when axis). 본 ADR-082 sub-scope 1-D = label state 변경 **직전 write authority verify** (what + who-can-write axis). 두 ADR 가 같은 CFP-1336 Story 안 paired carrier 로 사용자 D-4 chief dissent carry 영역 (cross-repo label state drift 차단) 의 두 disjoint axis 동시 codify.

### 근거

- §결정 1 layer 1 4-layer 표 안 layer 1 (Orchestrator scope) sub-scope (1-A/1-B/1-C) 모두 verify axis. sub-scope (1-D) = write authority verify axis 신설 — disjoint axis 확장 (forbid scope 축소 아님, ratchet 강화 방향).
- ADR-066 Amendment 4 = PAT scope `issues:write` cross-repo label sync 인가 정합 (3 ADR paired Amendment carrier — ADR-073/082/066 같은 CFP-1336 Story 안).
- ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향 only). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만, 약화 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 4-entry (Amendment 1 의 2 + Amendment 6 의 1 + 본 Amendment 14 의 1 entry).
- ADR-039 lane self-write boundary 정합 (lane plugin agent md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제).
- pattern_count evidence: cross-repo label state drift sentinel forward-prevention — D-4 chief dissent carry (사용자 explicit decision CFP-1302 follow-up F2). 도구적 가치 evidence base (recurrence ≥ 2 wait 시 PAT scope leakage / mirror inversion / silent label drift 누적 risk).
- 본 Amendment 14 자체가 META-self-applied (§결정 10.D 9th applied case): Amendment 번호(14) = target ADR-082 frontmatter `amendments:` Read verify (origin/main 8fd36711 max=13 — CFP-1390 Amd 13 merge 후 base, 정확 next-slot = 14) 후 결정 — §결정 9 Amendment 7 양방향 wording 준수.

### Amendment slot history (verify-before-cite META-self-application 9번째 사례 — Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions, CFP-1390 mid-DesignReview spawn collision 추가)

본 Story (CFP-1336) 의 Amendment slot 은 single Story 안 4 reach 의 mid-flight collision 누적:

1. **spawn 시점 (FIX iter 0)** = Amendment 8 planned (origin/main bfc4806 base, amendments[] max=7)
2. **CFP-1329 Amendment 8 + CFP-1330 Amendment 9 mid-flight land** (chief author spawn 도중) → FIX iter 1 시점 Amendment 10 으로 renumber
3. **CFP-1332 Amendment 10 + CFP-1338 Amendment 11 추가 mid-flight land** (FIX iter 1 → iter 2 사이) → FIX iter 2 시점 Amendment 12 로 renumber
4. **CFP-1339 Amendment 12 + ArchitectPL spawn 도중 land** (FIX iter 2 → iter 3 사이) → FIX iter 3 시점 Amendment 13 으로 renumber 계획
5. **CFP-1390 Amendment 13 mid-DesignReview spawn collision land** (FIX iter 3 → iter 4 사이) → **FIX iter 4 Amendment 14 으로 renumber FINAL** (ADR-067 max FIX 3/3 cap EXCEED + user explicit "다음 작업 끝까지 수행해" continuation override authorized)

`amendment_number_stale_at_planning` pattern_count 8+ reach across CFP-1293 / CFP-1303 / CFP-1318 / CFP-1336-iter1 / CFP-1336-iter2 / CFP-1336-iter3 / CFP-1336-iter4 (single Story 4 reach, 5th collision). ADR-045 §D-9 cross_story_pattern_adr_trigger Mandatory escalation 정합 — Orchestrator retro 의무 (follow-up CFP for amendment-slot-reservation forcing function mechanism 평가).

### Related (Amendment 14 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 9 paired (transition trigger `label_change` dual-binding, verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1336 carrier)
- `docs/adr/ADR-066-pat-rotation-policy.md` — Amendment 4 paired (PAT scope `issues:write` cross-repo label sync 인가, 3 ADR paired Amendment carrier ADR-073/082/066)
- `templates/github-workflows/cross-repo-label-sync.yml` — bidirectional sync workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별도 sub-carrier)
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — `[cross-repo-label-sync]` audit comment prefix 신설 (Amendment 14 audit trail anchor)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:cross-repo-label-sync` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/security/pat-rotation-log.md` — Amendment 14 동반 placeholder (PAT scope `issues:write` rotation evidence)
- `docs/evidence-checks-registry.yaml` — `cross-repo-label-sync` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별도 sub-carrier)
- `docs/parallel-work/section-ownership.yaml` — `templates/github-workflows/cross-repo-label-sync.yml` row append (Amendment 14 owner GitOpsAgent)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 3-row append (ADR-073 Amendment 9 / ADR-082 Amendment 14 / ADR-066 Amendment 4, CFP-1336 paired carrier active 동시 점유)
- `docs/change-plans/cfp-1336-cross-repo-label-sync.md` — Change Plan SSOT (Phase 1 carrier)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 14 sub-scope 1-D cross-ref 1 line append (CFP-506 line cap 정합)
- `CHANGELOG.md` — PATCH entry append (plugin.json MINOR bump 동반 — 신규 `cross-repo-label-sync` action entry)
- `.claude-plugin/plugin.json` — MINOR bump (신규 mechanical_enforcement_actions entry = MINOR per ADR-008 §결정 2)
- `mclayer/marketplace` repo — `marketplace.json` plugins[name=codeforge] mirrored field 4종 (`version`) atomic sibling PR (ADR-063 §결정 1)

## Amendment 15 — §결정 1 layer 1 sub-scope (1-E) 신설 (spawn prompt SHA-anchor write-time verify mandate, CFP-1437, 2026-05-24 KST)

### 동기

CFP-1389 Sub-CFP A carrier (CFP-1336 retro follow-up) — Pre-spawn HEAD-pin protocol mechanical lint Epic Wave 1 declarative-only carrier. CFP-1336 Phase 1 single Story 안 amendment_number_stale_at_planning collision 4 reach (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions) + cross-Story pattern_count 누적 9+ reach (CFP-1293 / CFP-1303 / CFP-1318 / CFP-1336-iter1~iter4 / CFP-1390 mid-DesignReview) → system-level pattern continued evidence. ADR-045 §D-9 Mandatory escalation 정합 — preventive solution carrier 의무.

근본 원인 = Orchestrator (또는 PL agent / chief author) 가 lane PL / chief author / deputy / 4-tuple sub-tuple subagent 를 spawn 할 때 spawn prompt 안 baseline origin/main SHA reference 부재 (또는 stale SHA 추정 사용). spawn 직후 mid-flight 다른 Story / Amendment merge 발생 시 spawn 받은 agent / subagent 는 stale baseline 가정 위에 planning → write 시점 amendment_id collision FIX iter 진입.

기존 4-layer verify-before-trust 안 layer 3 (ADR-082 §결정 1) 의 sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) 가 모두 read-time verify 또는 write 직전 fidelity check 영역. spawn-time SHA-anchor **write-time verify** axis 는 disjoint sub-scope — 본 Amendment 가 sub-scope 1-E 신설로 anchor.

ADR-073 Amendment 11 (`spawn_prompt_emit` transition trigger, lane-spawn sentinel polling 10번째 entry) 와 paired Amendment carrier (같은 CFP-1437 Story 안). ADR-073 = transition 시점 spawn prompt SHA pin verify (when + how — Orchestrator / PL emit-time discipline), ADR-082 sub-scope 1-E = spawn prompt SHA-anchor write-time verify (what + who-can-write — internal lane agent self-write semantic truth verify). dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair).

### Amendment

#### §결정 1 layer 1 sub-scope (1-E) 신설 — spawn prompt SHA-anchor write-time verify 4-tuple primitive

ADR-082 §결정 1 의 4-layer 표 안 layer 1 (Orchestrator scope) sub-scope 확장:

- **sub-scope (1-A)** = cross-repo state verify (read-time, ADR-073 base)
- **sub-scope (1-B)** = Orchestrator-authored Issue body authorship pre-publish verify (write-time, Amendment 2 신설)
- **sub-scope (1-C)** = Orchestrator-authored lane PL spawn prompt user-utterance verbatim anchor (write-time, Amendment 5 신설)
- **sub-scope (1-D)** = cross-repo label-write authority verify-before-write (write-time, Amendment 14 신설)
- **sub-scope (1-E) — 신설 (Amendment 15)** = spawn prompt SHA-anchor write-time verify (write-time, 4-tuple primitive):
  - **(a) spawn prompt 첫 줄 `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 형식 명시**: literal block, regex `^\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{40}\]$`. ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent 답습 (spawn-time anchor block pattern, block 형식 verbatim 답습).
  - **(b) SHA 값 spawn 시점 `git rev-parse origin/main` direct fetch 일치 verify**: spawn prompt 작성 직전 `git fetch origin main --quiet` + `git rev-parse origin/main` 으로 ground truth SHA 획득 (working tree HEAD 또는 cached SHA 사용 금지).
  - **(c) parent → child cascade fresh re-fetch**: parent agent (Orchestrator / PL) 가 child agent (chief author / deputy / sub-tuple) spawn 시, 본 spawn 시점 `git rev-parse origin/main` 재실행 후 fresh SHA pin 의무. parent SHA verbatim carry 금지 (parent SHA → spawn 시점 사이 mid-flight merge 가능, fresh re-fetch 의무).
  - **(d) verified-via annotation**: spawn prompt 안 `pre_spawn_pin_verified: <bool>` field 의무. write-time semantic truth verify (작성 SHA = spawn-time origin/main 일치 단언).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-head-pin-presence` warning-tier deferred-followup append. Wave 2 mechanical wire (lint script + workflow + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — Amendment 6/8/10/14 패턴 verbatim 답습 / ADR-070 D5 retain 패턴 / ADR-076 / ADR-086).

#### ADR-073 Amendment 11 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair)

ADR-073 Amendment 11 §결정 1 transition trigger enum 안 `spawn_prompt_emit` 신규 entry — lane-spawn 시점 spawn prompt SHA pin verify 의무 (when + how axis). 본 ADR-082 sub-scope 1-E = spawn prompt body 작성 시점 **SHA-anchor block write-time verify** (what + who-can-write axis). 두 ADR 가 같은 CFP-1437 Story 안 paired carrier 로 CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach preventive solution carrier 영역 (chief author / deputy stale-at-planning 차단 forcing function) 의 두 disjoint axis 동시 codify.

### 근거

- §결정 1 layer 1 5-layer 표 안 layer 1 (Orchestrator scope) sub-scope (1-A/1-B/1-C/1-D) 모두 verify axis (read-time + write-time fidelity). sub-scope (1-E) = spawn-time write-time SHA-anchor verify axis 신설 — disjoint axis 확장 (forbid scope 축소 아님, ratchet 강화 방향).
- ADR-073 Amendment 11 = transition trigger `spawn_prompt_emit` 10번째 entry codify 정합 (paired carrier, 2 ADR Amendment 동시 발의 — axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합).
- ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향 only). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만, 약화 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 5-entry (Amendment 1 의 2 + Amendment 6 의 1 + Amendment 14 의 1 + 본 Amendment 15 의 1 entry).
- ADR-039 lane self-write boundary 정합 (lane plugin agent md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제).
- ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent 답습 (spawn-time anchor block pattern, block 형식 verbatim 답습 — anchor block normative pattern 동형).
- pattern_count evidence: CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence (CFP-1293 + CFP-1303 + CFP-1318 + CFP-1336-iter1~iter4 + CFP-1390) + preventive solution carrier (sentinel-driven + ratchet 확장 hybrid). ADR-045 §D-9 Mandatory threshold reach.
- 본 Amendment 15 자체가 META-self-applied (§결정 10.D 10th applied case): Amendment 번호(15) = target ADR-082 frontmatter `amendments:` Read verify (origin/main 67a541aa max=14 — CFP-1336 Amd 14 merge 후 base, 정확 next-slot = 15) 후 결정 — §결정 9 Amendment 7 양방향 wording 준수.

### Related (Amendment 15 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 11 paired (transition trigger `spawn_prompt_emit` dual-binding, verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier)
- `templates/github-workflows/spawn-prompt-head-pin-check.yml` — spawn prompt SHA-anchor write-time verify workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별도 sub-carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:spawn-prompt-head-pin-presence` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/evidence-checks-registry.yaml` — `spawn-prompt-head-pin-presence` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별도 sub-carrier)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 2-row append (ADR-073 Amendment 11 / ADR-082 Amendment 15, CFP-1437 paired carrier active 동시 점유)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1437-pre-spawn-head-pin-protocol.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy + `docs/change-plans/` gitignored)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 15 sub-scope 1-E + ADR-073 Amendment 11 cross-ref 1 line append (CFP-506 line cap 정합)
- `<internal-docs>/plugin-codeforge/stories/CFP-1437.md` — Story file (Sub-CFP A carrier, Phase 1 declarative)

## Amendment 16 — §결정 1 layer 1 sub-scope (1-F) 신설 (spawn-internal periodic origin re-pin protocol, CFP-1436, 2026-05-24 KST)

### 동기

CFP-1389 Sub-CFP B carrier (CFP-1336 retro follow-up, paired sibling of Sub-CFP A CFP-1437) — Mid-flight rebase auto-detection mechanical lint Epic Wave 1 declarative-only carrier. Sub-CFP A (CFP-1437 / ADR-073 Amendment 11 + ADR-082 Amendment 15) 가 spawn 직전 PRE-SPAWN-ORIGIN-MAIN-SHA block 의무로 baseline origin/main SHA 를 lock 한다 (preventive layer). 그러나 spawn 직후 ~ 작업 완료 사이 mid-flight 다른 Story / Amendment merge 가 발생하면 spawn 받은 agent 의 baseline 이 stale 가 된다 (Sub-CFP A 단독 미흡 — drift 가 spawn-internal time 에 발생).

Sub-CFP B 의 동인 = preventive layer 보강 — chief author / deputy / 4-tuple sub-tuple 작업 중간 (spawn-internal time) periodic check 의무 + drift 감지 시 fast-fail (`drift_detected: true` flag RETURN to Orchestrator) + Orchestrator 가 fresh pin 으로 re-spawn / fast-fail / escalate 결정. CFP-1336 9+ collisions evidence 의 reactive complement (preventive + reactive 2-layer defense forcing function 완결) — Sub-CFP A 단독으로 catch 못 하는 spawn-internal mid-flight drift 영역 codify.

기존 5-layer verify-before-trust 안 layer 3 (ADR-082 §결정 1) 의 sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) / 1-E (spawn prompt SHA-anchor pre-spawn pin) 가 모두 read-time / write 직전 / pre-spawn time fidelity check 영역. spawn-internal time periodic drift detection + return early authority axis 는 disjoint sub-scope — 본 Amendment 가 sub-scope 1-F 신설로 anchor.

ADR-073 Amendment 12 (`mid_spawn_origin_drift_detected` transition trigger, lane-spawn sentinel polling 11번째 entry) 와 paired Amendment carrier (같은 CFP-1436 Story 안). ADR-073 = transition 시점 mid-spawn drift 감지 의무 (when + how — chief author / deputy / sub-tuple detection time discipline), ADR-082 sub-scope 1-F = spawn-internal periodic origin re-pin protocol (what + who-can-write — internal lane agent self-write 시 RETURN early authority + payload write-time semantic truth verify). dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair).

### Amendment

#### §결정 1 layer 1 sub-scope (1-F) 신설 — spawn-internal periodic origin re-pin protocol 4-tuple primitive

ADR-082 §결정 1 의 5-layer 표 안 layer 1 (Orchestrator scope) sub-scope 확장:

- **sub-scope (1-A)** = cross-repo state verify (read-time, ADR-073 base)
- **sub-scope (1-B)** = Orchestrator-authored Issue body authorship pre-publish verify (write-time, Amendment 2 신설)
- **sub-scope (1-C)** = Orchestrator-authored lane PL spawn prompt user-utterance verbatim anchor (write-time, Amendment 5 신설)
- **sub-scope (1-D)** = cross-repo label-write authority verify-before-write (write-time, Amendment 14 신설)
- **sub-scope (1-E)** = spawn prompt SHA-anchor pre-spawn pin (write-time, Amendment 15 신설 — preventive layer)
- **sub-scope (1-F) — 신설 (Amendment 16)** = spawn-internal periodic origin re-pin protocol (spawn-internal time + write-time return-early authority, 4-tuple primitive — reactive layer):
  - **(a) periodic check trigger 의무**: chief author / deputy / 4-tuple sub-tuple subagent 가 작업 중간 매 N file edit 또는 매 Edit/Write tool 호출 후 (또는 timer-based 일정 interval, e.g. 5분) `git fetch origin main --quiet` + `git rev-parse origin/main` 실행. Wave 1 = subagent 자체 판단 (frequency = behavioral mandate), Wave 2 mechanical hook = trigger heuristic 별 sub-CFP carrier 결정 (file edit count / time interval / hybrid).
  - **(b) drift comparison**: spawn prompt 안 PRE-SPAWN-ORIGIN-MAIN-SHA block 값과 current origin/main SHA 비교. 일치 = 정상 (continue work). 불일치 = drift 감지 (다음 step).
  - **(c) drift threshold + RETURN early**: drift threshold (≥ N commits behind, default N=1 즉 any merge) 초과 시 subagent RETURN early with `drift_detected: true` flag + payload (`pre_spawn_sha: <hex>` + `current_origin_main_sha: <hex>` + `commits_drift: <N>` + `drift_detected_at_step: <description>`). Orchestrator 가 RETURN 수신 시 (a) fresh pin 으로 re-spawn / (b) fast-fail abort / (c) 사용자 escalate 3-way 결정.
  - **(d) verified-via annotation**: RETURN payload 안 `mid_spawn_drift_verified: <bool>` field 의무. write-time semantic truth verify (RETURN flag 정합성 — drift 실제 감지 여부 단언).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `mid-spawn-drift-detection` warning-tier deferred-followup append. Wave 2 mechanical wire (subagent runtime hook + lint script + workflow + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — Amendment 6/8/10/14/15 패턴 verbatim 답습 / ADR-070 D5 retain 패턴 / ADR-076 / ADR-086).

#### ADR-073 Amendment 12 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair)

ADR-073 Amendment 12 §결정 1 transition trigger enum 안 `mid_spawn_origin_drift_detected` 신규 entry — spawn-internal time mid-spawn drift 감지 의무 (when + how axis). 본 ADR-082 sub-scope 1-F = spawn-internal periodic origin re-pin 의 RETURN early authority + write-time payload semantic truth verify (what + who-can-write axis). 두 ADR 가 같은 CFP-1436 Story 안 paired carrier 로 CFP-1336 amendment_number_stale_at_planning evidence 의 reactive layer 영역 (Sub-CFP A preventive layer 단독으로 catch 못 하는 spawn-internal mid-flight drift 차단 forcing function) 의 두 disjoint axis 동시 codify.

### 근거

- §결정 1 layer 1 5-layer 표 안 layer 1 (Orchestrator scope) sub-scope (1-A/1-B/1-C/1-D/1-E) 모두 read-time / write 직전 / pre-spawn time verify axis. sub-scope (1-F) = spawn-internal time periodic drift detection + return early authority axis 신설 — disjoint axis 확장 (forbid scope 축소 아님, ratchet 강화 방향).
- ADR-073 Amendment 12 = transition trigger `mid_spawn_origin_drift_detected` 11번째 entry codify 정합 (paired carrier, 2 ADR Amendment 동시 발의 — axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합).
- ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향 only). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만, 약화 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 6-entry (Amendment 1 의 2 + Amendment 6 의 1 + Amendment 14 의 1 + Amendment 15 의 1 + 본 Amendment 16 의 1 entry).
- ADR-039 lane self-write boundary 정합 (lane plugin agent md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제).
- ADR-082 sub-scope 1-E (Amendment 15) spawn-time anchor block pattern precedent 답습 + Amendment 15 (1-E pre-spawn pin) + 본 Amendment 16 (1-F mid-spawn re-pin) = paired complementary defense (preventive + reactive 2-layer).
- pattern_count evidence: CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence 공유 (Sub-CFP A 와 같은 base, sentinel evidence 별도 누적 0 — preventive + reactive 2-layer defense 결정 carrier).
- 본 Amendment 16 자체가 META-self-applied (§결정 10.D 11th applied case): Amendment 번호(16) = target ADR-082 frontmatter `amendments:` Read verify (origin/main a1316f67d920dcc28fe40dec7cb69547ab60e025 max=15 — CFP-1437 Amd 15 merge 후 base, 정확 next-slot = 16) 후 결정 — §결정 9 Amendment 7 양방향 wording 준수.

### Related (Amendment 16 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 12 paired (transition trigger `mid_spawn_origin_drift_detected` dual-binding, verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier)
- `templates/github-workflows/mid-spawn-drift-detection-check.yml` — spawn-internal periodic origin re-pin protocol workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별도 sub-carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:mid-spawn-drift-detection` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/evidence-checks-registry.yaml` — `mid-spawn-drift-detection` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별도 sub-carrier)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 2-row append (ADR-073 Amendment 12 / ADR-082 Amendment 16, CFP-1436 paired carrier active 동시 점유)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1436-mid-flight-rebase-detection.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy + `docs/change-plans/` gitignored)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 16 sub-scope 1-F + ADR-073 Amendment 12 cross-ref 1 line append (CFP-506 line cap 정합)
- `<internal-docs>/plugin-codeforge/stories/CFP-1436.md` — Story file (Sub-CFP B carrier, Phase 1 declarative)

## Amendment 17 — §결정 1 layer 1 sub-scope (1-G) 신설 (amendment-slot pre-reservation strict claim mandate, CFP-1435, 2026-05-24 KST)

### 동기

CFP-1389 Sub-CFP C carrier (CFP-1336 retro follow-up, paired sibling of Sub-CFP A CFP-1437 + Sub-CFP B CFP-1436) — Amendment-slot pre-reservation contract field codify Epic Wave 1 declarative-only carrier. CFP-1336 single Story 안 amendment_number_stale_at_planning collision 4 reach (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions) + cross-Story pattern_count 누적 9+ reach (CFP-1293 / CFP-1303 / CFP-1318 / CFP-1336-iter1~iter4 / CFP-1390 mid-DesignReview) → system-level pattern continued evidence. ADR-045 §D-9 Mandatory escalation 정합 — preventive solution carrier 의무.

Sub-CFP A (CFP-1437 / ADR-073 Amendment 11 + ADR-082 Amendment 15) = pre-spawn time SHA pin (preventive layer — spawn 직전 baseline lock).
Sub-CFP B (CFP-1436 / ADR-073 Amendment 12 + ADR-082 Amendment 16) = spawn-internal time periodic origin re-pin (reactive complement — mid-flight drift 감지).
**Sub-CFP C (본 carrier / ADR-082 Amendment 17 + ADR-050 cross-ref + ADR-RESERVATION schema bump)** = amendment slot reservation lifecycle pre-claim (preventive complement — race-winner-takes-it convention 의 strict claim 전환).

Sub-CFP A 단독 미흡: spawn 시점 SHA fresh fetch 후에도 multi-session concurrent spawn 시 같은 ADR 같은 amendment_id slot race 가능 (SHA pin 은 mid-flight drift 감지 layer, slot ownership 직접 차단 layer 아님). Sub-CFP B 단독 미흡: drift detection 은 collision 발생 후 reactive 회수, pre-claim layer 부재.

**Sub-CFP C 의 forcing function** = chief author / deputy spawn 시점에 **ADR-RESERVATION `amendments_reserved[]` row 의무 pre-append** (commit time 점유 후 retroactive append → spawn 시점 strict claim). + spawn prompt 안 `pre_reserved_amendment_slots: [{adr: ADR-NNN, amendment_id: M}]` field 의무 (planned amendment_id list 전달 — chief author 가 spawn 시점에 reservation row 와 cross-verify).

기존 6-layer verify-before-trust 안 layer 3 (ADR-082 §결정 1) 의 sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) / 1-E (spawn prompt SHA-anchor pre-spawn pin) / 1-F (spawn-internal periodic origin re-pin) 가 모두 read-time / write 직전 / spawn-time / spawn-internal time fidelity check 영역. **amendment slot reservation lifecycle pre-claim** axis 는 disjoint sub-scope — 본 Amendment 가 sub-scope 1-G 신설로 anchor.

ADR-050 (parallel epic conflict coordination) §결정 1 ADR-RESERVATION carrier 의 fine-grained extension — ADR number reservation (ADR-050 §결정 1, GitOpsAgent monopoly sequential append) 와 amendment slot reservation (CFP-1058 Amendment 4 sub-tree codify + 본 Amendment 17 strict claim forcing function) 가 동일 race coordination 패턴. **본 Sub-CFP C 는 ADR-073 touch 0건** (Sub-CFP A/B paired Amendment pattern 와 disjoint — ADR-082 super-class + ADR-050 cross-ref + ADR-RESERVATION schema enhancement 의 triple-binding carrier).

### Amendment

#### §결정 1 layer 1 sub-scope (1-G) 신설 — amendment-slot pre-reservation strict claim 4-tuple primitive

ADR-082 §결정 1 의 6-layer 표 안 layer 1 (Orchestrator scope) sub-scope 확장:

- **sub-scope (1-A)** = cross-repo state verify (read-time, ADR-073 base)
- **sub-scope (1-B)** = Orchestrator-authored Issue body authorship pre-publish verify (write-time, Amendment 2 신설)
- **sub-scope (1-C)** = Orchestrator-authored lane PL spawn prompt user-utterance verbatim anchor (write-time, Amendment 5 신설)
- **sub-scope (1-D)** = cross-repo label-write authority verify-before-write (write-time, Amendment 14 신설)
- **sub-scope (1-E)** = spawn prompt SHA-anchor pre-spawn pin (write-time, Amendment 15 신설 — preventive SHA layer)
- **sub-scope (1-F)** = spawn-internal periodic origin re-pin protocol (spawn-internal time, Amendment 16 신설 — reactive drift layer)
- **sub-scope (1-G) — 신설 (Amendment 17)** = amendment-slot pre-reservation strict claim (spawn-time pre-claim + spawn prompt cross-verify, 4-tuple primitive — preventive slot layer):
  - **(a) pre-reservation row pre-append 의무**: chief author / deputy spawn 전 ADR-RESERVATION `amendments_reserved[]` row append + commit 의무 (commit time 점유 후 retroactive append 금지 — strict pre-claim). schema = `{adr_number, amendment_id, reserved_by_cfp, reservation_date, status: reserved}`. spawn 후 chief author 가 actual ADR Amendment write 시 status `reserved → active` 전환.
  - **(b) spawn prompt block 안 `pre_reserved_amendment_slots` field 의무**: spawn prompt body 안 `pre_reserved_amendment_slots: [{adr: ADR-NNN, amendment_id: M}, ...]` field 의무 (planned amendment_id list 전달). chief author 가 spawn 시점에 ADR-RESERVATION row 와 cross-verify (own carrier_story 매핑 확인).
  - **(c) reservation row ↔ actual write cross-verify**: chief author 가 ADR Amendment write 직전 ADR-RESERVATION `amendments_reserved[]` row 존재 verify (own `reserved_by_cfp` 일치 + own `adr_number` + own `amendment_id` 정합). mismatch 시 write abort + Orchestrator escalate.
  - **(d) verified-via annotation**: spawn prompt 안 `pre_reservation_verified: <bool>` field 의무. write-time semantic truth verify (작성 amendment_id = pre-reserved slot 일치 단언).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `amendment-slot-reservation-check` warning-tier deferred-followup append. Wave 2 mechanical wire (lint script + workflow yml hydrate + ADR-RESERVATION schema strict validation + concurrent reservation conflict detection + bats fixture + label-registry MINOR bump + evidence-checks-registry Active entry) = 별 sub-CFP carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — Amendment 6/8/10/14/15/16 패턴 verbatim 답습 / ADR-070 D5 retain 패턴 / ADR-076 / ADR-086).

#### ADR-RESERVATION schema bump (1.0 → 1.1)

ADR-RESERVATION.md frontmatter `schema_version: 1.1` field 신설 (이전 = implicit 1.0). `amendments_reserved[]` row required fields 명문화:

```yaml
schema_version: 1.1  # CFP-1435 / ADR-082 Amendment 17
amendments_reserved:
  - adr_number: NNN              # 기존 ADR number (active, integer)
    amendment_id: M              # 예약 Amendment id slot (integer, sequential within ADR)
    reserved_by_cfp: CFP-XXX     # carrier Story (string)
    reservation_date: YYYY-MM-DD KST  # ADR-079 KST format
    status: reserved | active | abandoned | superseded  # closed enum 4-value (이전 = reserved | active | superseded — abandoned 추가, superseded retain)
```

**status enum closed-set 4-value (1.1)**: `reserved` (pre-claim 직후 chief author actual write 전) / `active` (chief author actual write 후 commit time) / `abandoned` (spawn aborted or carrier_story canceled before write) / `superseded` (이전 ADR amendment 가 신규 amendment 로 덮어쓰임 — backward-compat 1.0 retain).

**1.0 → 1.1 backward-compat invariant**: 기존 1.0 amendments_reserved[] rows 무효화 0건. 신규 row 만 `status: reserved` 의무 (이전 `active` 직접 진입 row precedent 유지 = chief author commit time pre-existing pattern, 본 Amendment 17 이후 신규 carrier 만 strict claim 적용).

#### ADR-050 cross-ref (paired sibling)

ADR-050 §결정 1 (ADR-RESERVATION ADR number 원자적 예약) = ADR number reservation race coordination carrier. 본 Amendment 17 = amendment slot reservation race coordination — ADR-050 §결정 1 의 fine-grained extension. 동일 race coordination 패턴 (GitOpsAgent monopoly sequential append → conflict 시 re-sort 자동 해소). ADR-050 본문 변경 0건 (cross-ref-only). ADR-082 Amendment 17 본문 안 ADR-050 §결정 1 동일 패턴 명문화.

**3-layer defense forcing function 완결**: Sub-CFP A (Amendment 15 1-E pre-spawn SHA pin) + Sub-CFP B (Amendment 16 1-F mid-spawn drift detection) + Sub-CFP C (본 Amendment 17 1-G amendment slot pre-reservation) = `preventive SHA + reactive drift + preventive slot` 3-layer.

### 근거

- §결정 1 layer 1 6-layer 표 안 layer 1 (Orchestrator scope) sub-scope (1-A/1-B/1-C/1-D/1-E/1-F) 모두 read-time / write 직전 / spawn-time / spawn-internal time verify axis. sub-scope (1-G) = amendment slot reservation lifecycle pre-claim axis 신설 — disjoint axis 확장 (forbid scope 축소 아님, ratchet 강화 방향).
- ADR-050 §결정 1 = ADR number reservation race coordination carrier (GitOpsAgent sequential append). 본 Amendment 17 = amendment slot reservation race coordination = ADR-050 §결정 1 의 fine-grained extension (axis disjoint complement, cross-ref-only Amendment).
- ADR-RESERVATION schema 1.0 → 1.1 MINOR bump = `schema_version` field 신설 + `amendments_reserved[]` row required fields documentation + status enum 4-value 명문화. backward-compat 1.0 row 무효화 0건 (ratchet 강화 방향 only).
- CFP-1058 Amendment 4 (ADR-082 Amendment 4 cross-ref) = `amendments_reserved[]` sub-tree 초기 codify (reactive — `0 entry baseline` + 신규 reservation 만 사용 + race-winner-takes-it convention). 본 Amendment 17 = reactive → strict pre-claim 전환 forcing function (CFP-1058 Amendment 4 패턴 답습 + scope 확장).
- ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향 only). `is_transitional: false` 유지.
- ADR-064 §self-application top-down ratchet 정합 (강화 방향만, 약화 0건).
- ADR-040 Amendment 3 §결정 7.A schema 정합 — `mechanical_enforcement_actions[]` 7-entry (Amendment 1 의 2 + Amendment 6 의 1 + Amendment 14 의 1 + Amendment 15 의 1 + Amendment 16 의 1 + 본 Amendment 17 의 1 entry).
- ADR-039 lane self-write boundary 정합 (lane plugin agent md cross-ref = follow-up defer, wrapper-only ADR-010 sibling sync 면제).
- pattern_count evidence: CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence 공유 (Sub-CFP A/B 와 동일 base, sentinel evidence 별도 누적 0 — preventive + reactive + preventive 3-layer defense 결정 carrier closure).
- 본 Amendment 17 자체가 META-self-applied (§결정 10.D 12th applied case): Amendment 번호(17) = target ADR-082 frontmatter `amendments:` Read verify (origin/main b32a731a5e858224afce72b0e6fc86ce86ee1483 max=16 — CFP-1436 Amd 16 merge 후 base, 정확 next-slot = 17) 후 결정 — §결정 9 Amendment 7 양방향 wording 준수.

### Related (Amendment 17 동반)

- `docs/adr/ADR-050-parallel-epic-conflict-coordination.md` — §결정 1 ADR-RESERVATION carrier cross-ref (amendment slot reservation = fine-grained ADR number reservation extension, 동일 race coordination 패턴 — ADR-050 본문 0건 변경, cross-ref-only)
- `docs/adr/ADR-RESERVATION.md` — schema 1.0 → 1.1 MINOR bump (frontmatter `schema_version` field 신설 + `amendments_reserved[]` row required fields documentation + status enum 4-value `reserved|active|abandoned|superseded`) + `amendments_reserved[]` 1-row append (ADR-082 Amendment 17, CFP-1435 carrier active 점유)
- `templates/github-workflows/amendment-slot-reservation-check.yml` — amendment-slot pre-reservation strict claim workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별도 sub-carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:amendment-slot-reservation-check` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/evidence-checks-registry.yaml` — `amendment-slot-reservation-check` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별도 sub-carrier)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1435-amendment-slot-prereservation.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy + `docs/change-plans/` gitignored)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 17 sub-scope 1-G + ADR-050 cross-ref 1 line append (CFP-506 line cap 정합)
- `<internal-docs>/plugin-codeforge/stories/CFP-1435.md` — Story file (Sub-CFP C carrier, Phase 1 declarative)

---

### Amendment 18 — §결정 1 layer 1 sub-scope (1-H) 신설 (Orchestrator §10 FIX Ledger resolution field source/evidence verify mandate, CFP-1342, 2026-05-25 KST)

**결정**: §결정 1 layer 1 sub-scope (1-H) 신설 — Orchestrator self-write §10 FIX Ledger row resolution field claim source/evidence verify mandate. §10 FIX Ledger = Orchestrator monopoly (fix-event-v1 contract, CFP-32) — 기존 sub-scope 1-A~1-G 7종 외 codify gap closure. 4 의무 codify: (a) resolution field 작성 시 인용 source/evidence ('wrap 실행 완료' / 'lint EXIT_CODE=0' / 'grep count N') 가 실 실행 결과인지 write-time verify / (b) measurable evidence (file path + grep count + exit code + diff hash) verify-via direct execution (cached/inferred 금지) / (c) `verified-via:` annotation (예: 'Read <path> + grep count = N + exit code = 0') / (d) wrap-style 자동화 영역 = 실 실행 결과 stdout / exit code / grep diff 확인 후 작성.

**근거**: CFP-1316 retro F2 Optional carrier — iter 1 'CHANGELOG.md 45 occurrence wrap' claim Orchestrator self-write monopoly codify gap. axis disjoint vs 1-A~1-G (Orchestrator monopoly §10 FIX Ledger resolution field write-time semantic truth verify axis). S6 Theme 5 Optional quartet — Orchestrator self-write monopoly 영역 (fix-event-v1 contract emit-time pre-check pattern) 의 claim source/evidence verify 의무 명문화.

**영향**: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G) → (1-H Orchestrator §10 FIX Ledger resolution field claim source/evidence verify) 확장 (forbid scope 축소 0건). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `fix-ledger-resolution-source-verify` warning-tier deferred-followup). Wave 2 mechanical lint = 별 sub-CFP carrier (deferred-followup, ADR-082 §결정 6 retain pattern 답습). minimal-applicability: §10 FIX Ledger resolution field write monopoly = Orchestrator only — lane agent / PL agent / chief author 영역 0 (sub-scope (1-B) 일반 lane agent self-write 와 disjoint axis). doc-only fast-path ADR-054 Cat 1 단일 PR (script / workflow / bats wire 0건).

**Cross-ref**: ADR-058 §결정 5 sunset_justification N/A (ratchet 강화 방향) / ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합 / META-self-applied (§결정 10.D 13th applied case + Amendment 17 sub-scope 1-G pre-reservation strict claim mandate 1st applied case — 본 Amendment 번호 18 = target ADR-082 frontmatter `amendments:` Read verify origin/main 11bf2d95 max=17 → next=18 결정 + ADR-RESERVATION amendments_reserved[] row pre-append 완료).

---

### Amendment 19 — §결정 1 layer 1 sub-scope (1-I) pre-spawn-prompt-finalize verify layer (CFP-FU-A sub-decision 3, parallel session race 11th occurrence + 12th meta-occurrence collision recovery)

**날짜**: 2026-05-25 KST

**carrier**: CFP-FU-A (Parallel session race 11th occurrence 3-decision sub-CFP — sub-decision 3 carrier within CFP-FU-A). **COLLISION RECOVERY**: 본 Amd 19 = 원래 Amd 18 / sub-scope (1-H) 점유 plan 이 CFP-1342 (origin/main commit 94b2289 merged in 11bf2d95→ca1c20e drift window) 와 collision detected post-PR-#1527-open → rebase on ca1c20e + renumber Amd 18→19 + sub-scope (1-H)→(1-I) + 4-file cross-ref update recovery.

**paired sibling**: ADR-073 Amendment 13 (sub-decision 1 polling cadence 1→3, 12+13번째 transition trigger entries `pre_git_operation` + `pre_push`) + ADR-073 Amendment 14 (sub-decision 2 OR→AND composition layer §결정 1-P primitive AND aggregate). 3 ADR Amendment 동시 발의 = axis disjoint complement 3-set (event timing cadence + composition layer + window narrowing), ADR-064 §결정 1 CFP scope unitary 정합.

#### 동기

CFP-1420 Sub-A S1.2 parallel session race 11th occurrence (Mega-Epic CFP-1415, branch `cfp-1420-doc-locations-schema-1-2-confluence-variant`, PR #1441 prior merge 2026-05-24T03:07:53Z → 본 session PR #1442 STAND_DOWN_DUPLICATE per DesignReviewPL verdict ESCALATE_PACKET_INCOMPLETE `parallel_session_conflict_post_merge_duplicate`) sentinel.

근본 원인 분석 (Story §2.2(c)): race window pre-spawn-prompt phase — worktree create (`git worktree add` 완료 timestamp) → spawn prompt finalize (Orchestrator가 `[USER-UTTERANCE-VERBATIM]` + `[PRE-SPAWN-ORIGIN-MAIN-SHA:]` + context packet 작성 완료 timestamp) 사이 ~30-60s window. 이 window 동안 별 session의 merge 발생 가능 — Amd 15 (1-E) pre-spawn SHA pin = spawn 시점 SHA fetch 만 cover (worktree create 직후 SHA pin OK), Amd 16 (1-F) mid-spawn drift = spawn-internal periodic check 만 cover (subagent 시작 후), Amd 18 (1-H) Orchestrator §10 FIX Ledger resolution field source/evidence verify (Orchestrator monopoly axis) = FIX Ledger write-time만 cover. 세 시점 외 chief author / deputy spawn window 영역 uncovered.

본 Amendment 19 동인 = 두 시점 사이 (worktree create 후 ~ spawn prompt finalize 직전) window covered (chief author / deputy spawn 영역). ~30-60s window 안 1회 추가 polling 의무 = 4-layer temporal defense forcing function 완결 (pre-spawn-fetch + pre-spawn-prompt-finalize + mid-spawn-periodic + Orchestrator §10 source-claim).

#### Sentinel evidence (pattern_count 11 reach Mandatory ADR-045 §D-9 + 12th meta-occurrence)

Story §6.2 11 occurrences ≫ threshold 2 = Mandatory escalation. CFP-953 (label-based search miss) + CFP-946 (Epic close miss) + CFP-949 (sub-issue scope polling gap) + ... + CFP-1420 Sub-A S1.2 11th. preventive (Amd 15 / 본 Amd 19) + reactive (Amd 16) + Orchestrator monopoly (Amd 18) 4-layer 완결 carrier (sub-decision 1+2+3 통합 + Orchestrator FIX Ledger axis).

**12th meta-occurrence**: CFP-1342 ADR-082 Amd 18 + sub-scope 1-H collision detected post-PR-#1527-open — 본 carrier 의 plan-time slot reservation (worktree create T0 → spawn prompt finalize T1 → ArchitectAgent commit T2 → ~30-60s gap → CFP-1342 merge T3 → PR #1527 open T4 → collision T5 → recovery T6) 가 정확히 본 sub-scope 1-I 가 cover 하려는 race window 안에서 발생. recursive dogfooding evidence for #1476 sub-decisions 1+2+3 race window 영역 직접 reproduce.

#### §결정 1 layer 1 sub-scope (1-I) 신설 — pre-spawn-prompt-finalize verify layer mandate

sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H) precedent 답습 (closed-set ratchet 강화). 본 Amendment 19 = sub-scope (1-I) append (renumbered from 1-H post CFP-1342 collision recovery).

> sub-scope 1-I = pre-spawn-prompt-finalize window verify axis 신설 — spawn prompt finalize 직전 window 영역 (Amd 15 1-E spawn-time SHA fetch 시점 + Amd 16 1-F mid-spawn drift 시점 + Amd 18 1-H Orchestrator §10 FIX Ledger resolution field source/evidence verify 와 disjoint complement).

#### 1-I 4-tuple primitive — pre-spawn-prompt-finalize verify mandate

Orchestrator (또는 PL agent / chief author) 가 lane PL / chief author / deputy / 4-tuple sub-tuple subagent spawn prompt 작성 시 4 의무:

1. **pre-spawn-prompt-finalize verify mandate** — `git worktree add` 완료 timestamp ~ `[USER-UTTERANCE-VERBATIM]` block emit timestamp 안 window (~30-60s) 안 1회 추가 polling 의무. 이 window 가 spawn 직전 race window 의 마지막 layer.
2. **3-source 동시 invoke + AND aggregate verify** — `git fetch origin main --quiet` + `gh issue list --search` + `gh pr list --search "head:<branch>"` 3-source 동시 invoke + 모두 PASS verify. sub-decision 2 (ADR-073 Amendment 14 §결정 1-P primitive AND aggregate) 정합 — 3-source AND aggregate composition layer 동일 mandate.
3. **race window ~30-60s 단축 mandate** — worktree create timestamp ~ spawn prompt emit timestamp 안 polling 1회 의무 binding. polling 0회 시 sentinel 발화 (warning tier deferred-followup mechanical wire Wave 2 carrier).
4. **verified-via annotation** — spawn prompt 안 `pre_spawn_prompt_finalize_verified: <bool>` field 의무 명시 (write-time semantic truth verify, annotation 부재 시 sentinel 발화).

> 본 sub-scope 1-I = sub-scope (1-A / 1-B / 1-C / 1-D / 1-E / 1-F / 1-G / 1-H) 와 disjoint axis (pre-spawn-prompt-finalize window verify axis). Amd 15 (1-E pre-spawn pin) + Amd 16 (1-F mid-spawn drift) + Amd 18 (1-H Orchestrator §10 source-claim) + 본 Amd 19 (1-I pre-spawn-prompt-finalize) = 4-layer temporal defense forcing function 완결.

#### 1-I disjoint axis cross-ref

- **1-C** (`[USER-UTTERANCE-VERBATIM]` block precedent): spawn prompt 첫 줄 사용자 발화 verbatim anchor block 의무. 본 1-I = spawn prompt content 작성 직전 window 안 polling 의무 (1-C block 작성 자체 시점). spawn anchor block ↔ pre-spawn-prompt-finalize polling disjoint complement.
- **1-E** (`[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent, Amd 15): spawn 시점 SHA fetch + block 의무 (Sub-CFP A CFP-1437, preventive). 본 1-I = worktree create 후 ~ spawn prompt finalize 직전 window 안 polling 의무. spawn-time SHA pin ↔ pre-spawn-prompt-finalize window disjoint complement.
- **1-F** (spawn-internal periodic origin re-pin, Amd 16): spawn-internal periodic check (Sub-CFP B CFP-1436, reactive). 본 1-I = spawn 직전 window 안 polling (Sub-CFP A 직후 ~ Sub-CFP B 시작 전 window). pre-spawn time ↔ mid-spawn time ↔ pre-spawn-prompt-finalize window 3-layer temporal disjoint.
- **1-G** (amendment-slot pre-reservation strict claim, Amd 17): amendment slot reservation lifecycle pre-claim (Sub-CFP C CFP-1435, preventive). 본 1-I = origin/main SHA + sibling Story/PR state polling (slot reservation 영역 외). slot reservation lifecycle ↔ origin/main SHA + state polling disjoint.
- **1-H** (Orchestrator §10 FIX Ledger resolution field source/evidence verify, Amd 18 CFP-1342): Orchestrator monopoly fix-event-v1 contract write-time verify (FIX Ledger row resolution field claim source-claim verify). 본 1-I = chief author / deputy spawn pre-prompt-finalize window 영역. Orchestrator FIX Ledger axis ↔ chief author spawn window disjoint axis.

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `pre-spawn-prompt-finalize-verify` warning-tier deferred-followup append. Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

Wave 1 retain rationale: mechanical wire 의 detection logic (Orchestrator runtime 안 어떻게 spawn prompt 작성 직전 polling 발화할지 / worktree create timestamp ~ spawn prompt emit timestamp 안 polling 추적 / verified-via annotation 부재 시 sentinel 발화 trigger) = sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

#### Amendment 19 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 19 scope = 본문 §결정 1-9 + sub-scope 1-I 신설 + Amendment 1-18 강화 방향 only (sub-scope ratchet 강화 + 4-layer temporal defense forcing function 완결). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합. paired sibling ADR-073 Amendment 13 + 14 동일 carrier — 3 ADR Amendment 동시 발의 (axis disjoint complement 3-set, ADR-064 §결정 1 CFP scope unitary 정합). META-self-applied (§결정 10.D 14th applied case + collision recovery 1st applied case).

#### Related (Amendment 19 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 13 paired (transition trigger `pre_git_operation` + `pre_push` 12+13번째 entries, sub-decision 1 polling cadence 1→3) + Amendment 14 paired (§결정 1-P primitive AND aggregate composition layer, sub-decision 2 OR→AND triple-source). 3 ADR Amendment 동시 발의 axis disjoint complement 3-set.
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 3-row pre-claim append (ADR-073 Amd 13 + Amd 14 + ADR-082 Amd 19, CFP-FU-A paired carrier active 동시 점유; CFP-1342 ADR-082 Amd 18 row preserved upstream of our Amd 19 row)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-fu-a-parallel-race-3-decisions.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy)
- `templates/github-workflows/pre-spawn-prompt-finalize-verify.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)
- `<internal-docs>/plugin-codeforge/stories/CFP-FU-A.md` — Story file (CFP-FU-A carrier, Phase 1 declarative, §10 12th meta-occurrence marker)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-073 Amendment 13/14 + ADR-082 Amendment 19 cross-ref 1 line append (CFP-506 line cap 정합)

---

### Amendment 20 — §결정 15 신설 (Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate, CFP-1559, 2026-05-25 KST)

**결정**: §결정 15 신설 — Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate. 4 sub-pattern closed-set enumeration: (a) PR #NNNN merge state stale / (b) CFP-NNNN MERGED/CLOSED state stale / (c) count number stale ('X VIOLATIONs' / 'Y defect' / 'pattern_count Z') / (d) sister carrier origin claim stale ('CFP-NNNN carrier'). CFP-1216 Phase 2 wired `amendment-number-frontmatter-verify` lint (sub-class — ADR-NNN Amd M regex citation only) 의 super-class declarative anchor.

**근거**: FU-CFP-D super-class carrier — Issue body stale-claim 4 sub-pattern closed-set declarative anchor. pattern_count 7+ reach Mandatory ADR-045 §D-9 escalation 산물: CFP-FU-B Issue #1477 5-defect 3 PIVOT (60% stale rate) + CFP-1041/1050 RequirementsPL spawn packet stale claim lineage 4 = 합산 ≥ 7. ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated ratchet 강화 정합. paired sibling CFP-1558 = amendment-number sub-class declarative ratchet (axis disjoint, ADR-082 Amendment 21 점유 예정 — CFP-1559 발의 first chronological).

**영향**: ADR-082 super-class scope (Issue body authorship verify Amendment 2 §결정 1 layer 1 sub-scope 1-A) → Issue body content broader stale-claim super-class (4 sub-pattern enumeration: PR merge state / CFP merge state / count number / sister carrier origin) 확장 (forbid scope 축소 0건). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `issue-body-claim-pre-screen` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow + bats fixture + ContinuityAgent agent file cross-plugin) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split precedent 답습). False-positive 완화 guards (code-span / quoted-text / templates/** / §9 transcript EXEMPT) = Wave 2 lint design scope (Phase 1 declarative scope 외).

**Cross-ref**: axis disjoint with sister 3-layer defense (CFP-1437 spawn-time SHA pin / CFP-1436 mid-spawn drift / CFP-1435 amendment slot reservation / CFP-1342 Orchestrator §10 FIX Ledger / CFP-FU-A pre-spawn-prompt-finalize window — 본 Amendment 20 = Issue body content write-time axis). META-self-applied (§결정 10.D 15th applied case + Amendment 17 §결정 1-G strict claim mandate 2nd applied case — 본 Amendment 번호 20 = target ADR-082 frontmatter `amendments:` Read verify origin/main HEAD `4000440` max=19 → next=20 결정 + ADR-RESERVATION amendments_reserved[] row pre-append commit `7a7ac08`).

---

### Amendment 21 — §결정 1 layer 1 sub-scope (1-J) 신설 (cross-repo worktree target authority verify mandate, CFP-1578, 2026-05-25 KST)

**결정**: §결정 1 layer 1 sub-scope (1-J) 신설 — cross-repo worktree target authority verify mandate. 4-tuple primitive (chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전): (a) `git -C <worktree_abs_path> remote -v` 실행하여 expected repo (wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 verify, mismatch 시 write 차단 + sentinel 발화 / (b) spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 명시 (write-target authority anchor block, enum `wrapper` / `internal-docs` / `marketplace` / `consumer-<name>`) / (c) cross-repo 작업 sequence 시 명시적 worktree switch 의무 — wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별도 worktree 분리, ADR-040 worktree convention 정합) / (d) `worktree_target_authority_verified: <bool>` annotation 의무.

sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I) precedent 답습 (closed-set ratchet 강화). 본 Amendment 21 = sub-scope (1-J) append. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint, 동시 발의 race).

> sub-scope 1-J = cross-repo worktree target authority verify axis 신설 — wrapper plugin-codeforge ↔ internal-docs cross-repo write-target boundary 영역 (1-D cross-repo label-write authority 와 가장 인접하나 verify 대상 disjoint: 1-D label state write authority ↔ 1-J filesystem write-target (worktree path↔remote URL) authority).

#### 1-J 4-tuple primitive — cross-repo worktree target authority verify mandate

chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 4 의무:

1. **worktree target authority verify-before-write 의무** — `git -C <worktree_abs_path> remote -v` 실행하여 expected repo (예: wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 확인. mismatch 시 write 차단 + sentinel 발화.
2. **spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 명시** — write-target authority anchor block 형식 (sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block + sub-scope 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습 — spawn-time anchor block normative pattern 동형). enum: `wrapper` (`plugin-codeforge`) / `internal-docs` (`codeforge-internal-docs`) / `marketplace` / `consumer-<name>` (mctrader 등). field 부재 시 sentinel 발화.
3. **cross-repo 작업 sequence 시 명시적 worktree switch 의무** — wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별도 worktree 분리, ADR-040 worktree convention 정합). cross-repo write 필요 시 별도 worktree explicit create + cwd switch + write 의무 (single worktree 안 cross-repo write 차단).
4. **verified-via annotation** — spawn prompt 안 `worktree_target_authority_verified: <bool>` field 의무 명시 (write-time semantic truth verify, annotation 부재 시 sentinel 발화).

> 본 sub-scope 1-J = sub-scope (1-A / 1-B / 1-C / 1-D / 1-E / 1-F / 1-G / 1-H / 1-I) 와 disjoint axis (cross-repo worktree target authority axis). 가장 인접한 sub-scope = 1-D (cross-repo label-write authority — 동일 cross-repo write authority super-axis 안) 이나 verify 대상 disjoint: 1-D = label state write authority verify / 1-J = filesystem write-target (worktree path↔remote URL) authority verify.

#### 1-J disjoint axis cross-ref

- **1-A** (Orchestrator cross-repo state verify): cross-repo state assertion 시점의 source direct verify (read-side verify). 본 1-J = write-side worktree target authority verify (write-target boundary). read-side state verify ↔ write-side target authority disjoint.
- **1-D** (cross-repo label-write authority, Amd 14): cross-repo label state 변경 직전 authority verify (label-write authority axis). 본 1-J = cross-repo filesystem write-target (worktree path↔remote URL) authority verify. label-write authority ↔ filesystem write-target authority disjoint (동일 cross-repo write authority super-axis 안 2 sub-axis).
- **1-G** (amendment-slot pre-reservation strict claim, Amd 17): amendment slot reservation lifecycle pre-claim (ADR-RESERVATION schema). 본 1-J = filesystem worktree target authority verify (write-target boundary). amendment slot ↔ worktree filesystem target disjoint.
- **1-I** (pre-spawn-prompt-finalize verify layer, Amd 19): spawn prompt finalize 직전 window polling (origin/main SHA + sibling Story/PR state). 본 1-J = worktree target repo authority verify (filesystem write-target). origin/main SHA polling ↔ worktree filesystem target authority disjoint.
- **ADR-040 worktree convention** (cross-ref): worktree namespace 표준 (`${HOME}/.claude/worktrees/<repo-name>/<branch-flat>`) + worktree-first normative + mechanical enforcement 4 entry (`worktree-first-*` evidence-checks-registry). 본 1-J = worktree authority verify-before-write mandate (target repo verify) — ADR-040 convention 정합 영역 codify gap closure.
- **ADR-013 dogfood-out internal-docs SSOT** (cross-ref): codeforge family dogfood-out 정책 — Story file + Change Plan + retro = internal-docs SSOT / src + tests + workflow + ADR + CLAUDE.md = wrapper plugin-codeforge. 본 1-J = ADR-013 SSOT path 정합 영역 codify gap closure (wrapper repo worktree 안에서 internal-docs PR 생성 시도 차단 mandate).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `worktree-target-authority-verify` warning-tier deferred-followup append. Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

Wave 1 retain rationale: mechanical wire 의 detection logic (Orchestrator runtime 안 어떻게 worktree target authority verify trigger / `git -C` remote 실측 + expected target 비교 / spawn prompt field 부재 시 sentinel 발화 trigger / cross-repo PR cross-target 시도 차단 hook) = sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

#### Amendment 21 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 21 scope = 본문 §결정 1-13 + sub-scope 1-J 신설 + Amendment 1-19 강화 방향 only (sub-scope ratchet 강화 + cross-repo write authority super-axis 의 filesystem write-target layer 신설). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint — content verify vs target authority verify, 동시 발의 race). META-self-applied (§결정 10.D 16th applied case).

#### Related (Amendment 21 동반)

- `docs/orchestrator-playbook.md` — §3.5 sub-section 신설 worktree target authority verify 4-tuple primitive (1-J 본문 normative anchor mirror)
- `skills/lane-self-write-boundary/SKILL.md` — column 추가 (target authority verify) cross-repo write-target boundary matrix codify
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append (adr_number 82 amendment_id 21 reserved_by_cfp CFP-1578 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G META 2nd applied case
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1578-worktree-target-authority-verify.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy)
- `<internal-docs>/plugin-codeforge/stories/cfp-1578.md` — Story file (CFP-1578 carrier, Phase 1 declarative, paired sibling CFP-1559 race marker)
- `templates/github-workflows/worktree-target-authority-verify.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 21 sub-scope 1-J cross-ref 1 line append (CFP-506 line cap 정합)

---

## Amendment 22 — §결정 1 layer 1 sub-scope (1-K) 신설 (numeric claim write-time strict claim mandate, CFP-1601, 2026-05-25 KST)

### 동기

CFP-1571 (§3.2 line count drift `+93→+101` 3 location 정정) + CFP-1581 (§3.2 file count drift `10→14` actual) — write-time numeric claim ground truth verify 부재 catch, **pattern_count 2 reach** ≥ ADR-045 §D-9 threshold 2 = Mandatory escalation 산물.

기존 ADR-082 §결정 1 layer 1 sub-scope 10종 (1-A ~ 1-J) 안 numeric claim source/value verify-before-write 영역 codify 부재:

- sub-scope **1-G** (Amendment 17, CFP-1435) = amendment-slot pre-reservation strict claim (row append axis, slot reservation lifecycle 자체) — numeric claim 의 sub-domain 이지만 amendment_id slot 한정 영역.
- sub-scope **1-H** (Amendment 18, CFP-1342) = Orchestrator §10 FIX Ledger resolution field source/evidence verify (Orchestrator monopoly axis).
- sub-scope **15** (Amendment 20, CFP-1559) = Issue body 4 sub-pattern (PR merge state / CFP state / count cite / sister carrier origin) — Issue body content 영역 한정, write-time governance docs (ADR text / Change Plan / Story / spawn packet wording) 영역 부재.

본 Amendment 22 = 일반 numeric claim 의 write-time strict claim 영역 신설. **6 numeric claim closed-set dimensions** enumeration (line count / file count / API count / pattern_count / commit count / row count) — closed-set ratchet 강화 (forbid scope 확장 only).

**META first applied case (recursive dogfooding self-evidence)**:

본 ADR Amendment 22 spawn packet 자체 안 numeric claim ambiguity 직접 catch — write-time strict claim mandate 의 ground truth 가 본 ADR 작성 행위 자체 안 1st applied 검증된 evidence.

1. **sub-scope letter 1-J 충돌**: spawn packet declared `[USER-UTTERANCE-VERBATIM]` 본문 안 'sub-scope (1-J)' 명시 → ArchitectAgent (chief author) 가 actual ADR-082 frontmatter Read verify 시 Amendment 21 (CFP-1578) 가 이미 sub-scope 1-J 점유 (worktree target authority verify) 발견 → 정확 next-letter = **1-K** 로 정정 (source command: `grep -n 'sub-scope (1-' docs/adr/ADR-082-...md | head -20` actual result + ADR-082 amendments[] frontmatter Read verify).
2. **amendments[] count semantic disambiguation**: spawn packet declared `amendments[] count = 21 (Amd 22 next slot)` + suggested source command `grep -c '^  - amendment_id:' docs/adr/ADR-082-...md` expected result `21` → actual `grep -c` result = **41** (line occurrence count, ADR-082 file structure 안 `amendments:` top-level + amendment_log 두 군데 amendment_id rows 가짐) ↔ semantic intent (max amendment_id slot value) = **21** divergence catch → source command 정밀화 의무 (b)(c) 1st applied empirical evidence.

이 2 가지 spawn packet numeric claim 정정이 본 Amendment 22 의 write-time numeric claim strict claim mandate 의 직접 evidence — Amendment 22 자체가 본 sub-scope 1-K 의 1st applied case.

### Amendment

#### §결정 1 layer 1 sub-scope (1-K) 신설 — numeric claim write-time strict claim 4-step mandate

ADR-082 §결정 1 의 layer 1 (Orchestrator scope + ArchitectAgent chief author scope + lane PL scope) sub-scope 확장:

- **sub-scope (1-A)** = cross-repo state verify (read-time, ADR-073 base)
- **sub-scope (1-B)** = Orchestrator-authored Issue body authorship pre-publish verify (write-time, Amendment 2)
- **sub-scope (1-C)** = Orchestrator-authored lane PL spawn prompt user-utterance verbatim anchor (write-time, Amendment 5)
- **sub-scope (1-D)** = cross-repo label-write authority verify-before-write (write-time, Amendment 14)
- **sub-scope (1-E)** = spawn prompt SHA-anchor pre-spawn pin (write-time, Amendment 15)
- **sub-scope (1-F)** = spawn-internal periodic origin re-pin protocol (spawn-internal time, Amendment 16)
- **sub-scope (1-G)** = amendment-slot pre-reservation strict claim (spawn-time pre-claim + cross-verify, Amendment 17)
- **sub-scope (1-H)** = Orchestrator §10 FIX Ledger resolution field source/evidence verify (write-time, Amendment 18)
- **sub-scope (1-I)** = pre-spawn-prompt-finalize verify layer (worktree-create ~ spawn-prompt-finalize window, Amendment 19)
- **sub-scope (1-J)** = cross-repo worktree target authority verify (filesystem write-target authority, Amendment 21)
- **sub-scope (1-K) — 신설 (Amendment 22)** = numeric claim write-time strict claim mandate (numeric claim source/value verify-before-write axis, 4-step primitive):
  - **(a) source command identify**: claim 의 ground truth source command 명시 의무. 예: `grep -c '^  - amendment_id:' <file>` (row count) / `wc -l <file>` (line count) / `git diff --shortstat <ref>` (line added/removed) / `find <dir> -name '*.md' | wc -l` (file count) / `git log --oneline <ref>..<head> | wc -l` (commit count) / pattern_count cross-Story aggregate (PMOAgent retro corpus). Source command 자체가 명시 가능해야 verify 가능.
  - **(b) direct execute**: 작성 직전 source command 실행 + actual value 획득 의무. cached value / 추정 / planning-time stale value 사용 금지. 본 step 이 fresh execution = write-time semantic truth verify 의 primitive.
  - **(c) claim↔actual cross-verify**: claim value 와 actual value 1:1 일치 verify. semantic ambiguity 발견 시 source command 정밀화 의무. 예: `grep -c` line-occurrence count vs YAML frontmatter max `amendment_id` slot semantic — 같은 source command 도 query target / aggregation semantics 가 다르면 정밀화 의무.
  - **(d) write only on match**: match 시에만 write. mismatch 시 abort + Orchestrator escalate (사용자 ACK 요구 또는 source command 정밀화 + 재verify).

#### Numeric claim closed-set 6 dimensions

본 Amendment 22 의 numeric claim 영역은 6 종으로 closed-set:

| Dimension | 예시 source command | 적용 scope |
|---|---|---|
| (i) line count | `wc -l <file>` / `git diff --shortstat <ref>` | file line count / patch line count |
| (ii) file count | `find <dir> -name '*.md' \| wc -l` / `git diff --name-only \| wc -l` | touched file count / dir file count |
| (iii) API count | spawn prompt agent invoke count / `mcp__github__*` call count | agent spawn count / cross-repo API call count |
| (iv) pattern_count | PMOAgent retro corpus aggregate (cross-Story repetition) | ADR-045 §D-9 base, escalation forcing function |
| (v) commit count | `git rev-list --count <range>` / `git log --oneline ...` | commits-behind / commits-ahead |
| (vi) row count | `grep -c '^  - ' <yaml>` / md table row count | yaml row / md table row / contract field count |

closed-set 정의: 본 6 dimension 외 numeric claim (예: timing latency / memory size / token count) 은 write-time strict mandate scope 외 (별 carrier 필요 시 ADR-082 별도 Amendment 발의, ratchet 강화 방향 only).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `numeric-claim-write-time-verify` warning-tier deferred-followup append. Wave 2 mechanical wire (lint script Python SSOT per ADR-061 + bash thin wrapper + workflow yml hydrate + bats fixture + label-registry MINOR bump `hotfix-bypass:numeric-claim-write-time-verify` family member + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435/1559/1578 Wave 1→Wave 2 split 답습).

#### 1-G overlap clarification (axis 인접)

본 Amendment 22 sub-scope 1-K 와 가장 인접한 sub-scope = **1-G** (amendment-slot pre-reservation strict claim, Amendment 17, CFP-1435). axis 비교:

- **1-G** = ADR-RESERVATION `amendments_reserved[]` row append 자체 = slot reservation lifecycle. numeric value = amendment_id 인 경우 1-K dimension (vi) row count 와 sub-domain overlap, 그러나 1-G 는 reservation lifecycle 자체 (status enum 4-value `reserved | active | abandoned | superseded`) 이지 일반 numeric claim source command verify 아님.
- **1-K** = 일반 numeric claim 의 source command identify → direct execute → cross-verify → write only on match 의 generic 4-step 의무. 6 dimension closed-set 안 모든 numeric value 적용.

axis disjoint: 1-G = row append lifecycle / 1-K = numeric value source verify. 1-K 가 superset 이 아니라 generic axis — 1-G 는 reservation lifecycle 의 mechanism codify (status enum + commit timing), 1-K 는 numeric claim 의 source verify primitive codify.

#### Wave 1 retain rationale

mechanical wire 의 detection logic (Orchestrator runtime 안 어떻게 numeric claim write trigger 감지 / source command 자동 추출 / actual execution + cross-verify / sentinel 발화) = sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-1437/1436/1435/1559/1578 Wave 1→Wave 2 split 답습). 본 Amendment 22 = META first applied 자체가 forward-prevention sentinel (spawn packet 안 numeric claim ambiguity catch).

#### Amendment 22 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 22 scope = 본문 §결정 1 layer 1 sub-scope 1-K 신설 + Amendment 1-21 강화 방향 only (sub-scope ratchet 강화 + numeric claim source/value strict claim axis 신설). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합. META-self-applied (§결정 10.D 17th applied case + numeric-claim verify-before-write 1st applied case META first applied: spawn packet 자체 안 sub-scope letter + amendments[] count semantic 2 numeric claim ambiguity 직접 catch).

#### Related (Amendment 22 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append (adr_number 82 amendment_id 22 reserved_by_cfp CFP-1601 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G pre-reservation strict claim mandate META 3rd applied case (Amendment 18 CFP-1342 1st applied + Amendment 21 CFP-1578 2nd applied precedent 답습)
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — §D-9 cross_story_pattern_adr_trigger pattern_count 2 reach Mandatory escalation 산물 (CFP-1571 + CFP-1581 sentinel evidence, evidence-only cross-ref)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1601-adr082-amd-22.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy)
- `<internal-docs>/plugin-codeforge/stories/CFP-1601.md` — Story file (CFP-1601 carrier, Phase 1 declarative)
- `templates/github-workflows/numeric-claim-write-time-verify.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)
- `CHANGELOG.md` — [Unreleased] entry append ([CFP-1578] ADR-082 Amendment 21 sub-scope 1-J worktree target authority verify)

## Amendment 23 — §결정 1 layer 1 sub-scope (1-L) 신설 (spawn prompt fact verify-before-trust mandate, CFP-1590, 2026-05-25 KST)

### Trigger

**PMOAgent CFP-1523 retro §5 inline ADR draft** Orchestrator → ArchitectAgent spawn carry-over (ADR-045 §D-9 Mandatory escalation pattern_count 3 reach). anchor_id = `stale_fact_inheritance_at_lane_spawn` / root_cause_class = `verify-before-trust-at-spawn-prompt`. 3 occurrences trace:

| # | Carrier | Stale fact inheritance pattern |
|---|---|---|
| 1 | CFP-1493 S2.3 PR #1520 commit message defer 사유 inheritance | "284 MCP call token cost very high" — 실 6 MCP call atomic (cascade primitive, 47x over-estimate). Confluence REST native cascade behavior 미선재 → CFP-1523 carrier Researcher Phase 0 발견 시점 정정. |
| 2 | CFP-1523 사용자 spawn prompt fact 4건 모두 stale (DomainAgent + ResearcherAgent dual verify 후 정정) | ADR lane field `1/117` → 실 `0/117` / binding `53` → 실 `59` / `142 page` → 실 corpus `148` ADR / `284 MCP call` → 실 `6` MCP cascade atomic. |
| 3 | CFP-1591 Issue body canonical/sibling 역할 반전 (ArchitectAgent verify-before-trust 발견) | Issue body 단언 "canonical (codeforge-review) v4.11 vs sibling (wrapper) v4.9" — 실 reverse direction: canonical = wrapper v4.11, sibling = codeforge-review v4.9, ADR-010 §결정 1 canonical-first invariant 위배. Orchestrator 가 CFP-1523 carrier 안 CI lint 출력 잘못 해석 후 Issue #1591 body 발의 시 stale interpretation inherit. Issue body 자체가 stale fact carrier. |

### Mid-flight CFP-1601 collision recovery (META 2nd applied case)

본 Amendment 23 = CFP-FU-A Amd 19 (post-CFP-1342 collision recovery) precedent 2nd applied case. timeline:

1. ArchitectAgent spawn pinned origin/main `ec2fc349` + ADR-082 amendments[] max=21 (CFP-1578 Amd 21 merge 후 base) — 정확 next-slot = Amd 22
2. ADR-RESERVATION amendments_reserved[] row pre-append (adr_number 82 amendment_id 22 reserved_by_cfp CFP-1590) commit d3d307f + push (Amd 17 §결정 1-G strict pre-reservation mandate 정합)
3. ADR-082 frontmatter Amd 22 + 본문 sub-scope 1-K body write + commit 7a48a08 + push
4. PR #1615 open
5. fetch origin/main — `ec2fc349` → `4c668913` (CFP-1601 Phase 1 PR #1611 merge 2026-05-25T20:13:39+0900)
6. CFP-1601 가 Amd 22 + sub-scope 1-K 점유 (content: "numeric claim write-time strict claim mandate", 4-step verify-before-write, 6 numeric dimension)
7. race-winner-takes-it convention 정합 — 본 CFP-1590 carrier 가 양보 → renumber Amd 22→**23** + sub-scope 1-K→**1-L** on rebase
8. atomic renumber + hard-reset to origin/main `4c668913` + 5-file re-apply

본 collision recovery 자체가 본 Amendment 의 sub-scope 1-L (upstream-inherited stale fact verify) **recursive dogfooding evidence** — Orchestrator 가 PR open 후 fetch 로 origin/main state 가 변경 (Amd 22 + 1-K 가 CFP-1601 점유) 발견 → ArchitectAgent verify-before-trust 4-layer (ADR-073 fresh fetch + ADR-082 §결정 1-G strict claim mandate) 적용 → 정정.

### sub-scope 1-L axis 정합

본 Amendment 23 = sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K) precedent 답습 (closed-set ratchet 강화). 본 Amendment 23 = sub-scope (1-L) append.

> sub-scope 1-L = spawn prompt content 안 인용 fact (numeric claim / state claim / count claim / sister carrier carrier_story claim) 의 **upstream-inherited fact verify axis** 신설 — Orchestrator 또는 chief author 가 spawn prompt 작성 시 4 sub-source (사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) 로부터 inherit 된 fact 를 직접 verify 의무 (cached / synthesized / inherited-without-verify 사용 금지).

#### 1-L 4-tuple primitive — spawn prompt fact verify-before-trust mandate

Orchestrator 또는 chief author 가 lane agent / deputy / 4-tuple sub-tuple subagent spawn prompt 작성 시 4 의무:

1. **upstream-inherited fact 식별 의무** — spawn prompt 안 인용 numeric / state / count / sister carrier claim 이 (i) 사용자 발화 (ii) sibling Issue body (iii) sister PR commit message (iv) 별 carrier retro file 로부터 inherit 된 경우 식별. 4 sub-source enum closed-set.
2. **direct source verify 의무** — verify source 명시 + 직접 fetch 의무. `verified-via: <gh issue view N --json body | gh pr view N --json commits | Read <file_path> | git show <SHA>:<path>>` annotation spawn prompt 안 명시 (cached / synthesized 사용 금지).
3. **stale 검출 시 정정 declare** — verify 결과 stale 검출 시 spawn prompt 안 fact 정정 + `[fact-correction: <claim> stale, verified <correct-value>, source: <verify-source>]` marker 의무 명시. 정정 source 명시 의무.
4. **verified-via annotation field 의무** — spawn prompt 안 `spawn_prompt_fact_verified: <bool>` field 명시 (write-time semantic truth verify, annotation 부재 시 sentinel 발화).

#### 1-L disjoint axis cross-ref

- **1-C** (user-utterance verbatim block 의무, Amd 5): 사용자 발화 content 전달 **형식 verbatim 의무** (block 형식 axis — 사용자 발화 paraphrase / 요약 / 재합성 차단). 본 1-L = 인용된 fact 자체의 **truthfulness verify** (content fact verify axis — stale inheritance 차단). 형식 axis ↔ truthfulness axis disjoint.
- **Amd 20 §결정 15 (Issue body stale-claim super-class write-time pre-screen)**: Issue body author 자기 작성 content 안 stale claim (a-PR merge state / b-CFP merge state / c-count number / d-sister carrier origin) — **작성자 책임 write-time pre-screen** (self-write 영역). 본 1-L = spawn prompt 작성 시 upstream source 로부터 inherit 된 fact (synthesizer / Orchestrator / chief author 책임 spawn-time verify, upstream-inherited 영역) — self-write content ↔ upstream-inherited content disjoint.
- **Amd 22 §결정 1-K (numeric claim write-time strict claim mandate, CFP-1601)**: own author write-time 안 numeric claim source/value strict verify (6-dimension closed-set line/file/API/pattern/commit/row count). 본 1-L = spawn prompt 안 upstream source 로부터 inherit 된 fact 자체 verify (numeric 영역 외 state / sister carrier / count / wording claim 포함). own author write-time numeric ↔ upstream-inherited content fact disjoint (axis 인접하나 verify 대상 disjoint — 1-K = numeric value source command + 1-L = upstream source content fact).
- **1-E** (PRE-SPAWN-ORIGIN-MAIN-SHA pre-spawn pin, Amd 15): spawn prompt 첫 줄 SHA-anchor block 형식 + spawn-time fresh fetch verify (anchor block presence + SHA freshness axis). 본 1-L = spawn prompt content 안 인용 fact content 자체의 truthfulness verify (content fact axis). anchor SHA freshness ↔ content fact truthfulness disjoint.
- **1-F** (mid-spawn periodic origin re-pin, Amd 16): spawn-internal periodic drift detection (spawn-internal time axis, reactive complement to 1-E preventive). 본 1-L = spawn prompt 작성 시 content fact verify (spawn-time write axis). spawn-internal periodic ↔ spawn-time content fact disjoint.
- **1-H** (Orchestrator §10 FIX Ledger resolution source/evidence, Amd 18): Orchestrator monopoly §10 FIX Ledger row resolution field claim source/evidence verify (fix-event-v1 contract level Orchestrator monopoly axis). 본 1-L = spawn prompt 안 인용 fact verify (chief author / synthesizer / Orchestrator 책임, spawn-time write axis). §10 FIX Ledger ↔ spawn prompt content disjoint.
- **1-I** (pre-spawn-prompt-finalize verify layer, Amd 19): spawn prompt finalize 직전 window polling (origin/main SHA + sibling Story/PR state 3-source AND aggregate, race window 단축 axis). 본 1-L = spawn prompt content 안 인용 fact verify (content fact axis, 4 sub-source identify + verify). window polling ↔ content fact verify disjoint (when verify vs what verify).
- **4-layer temporal defense 의 content fact axis 5th layer** (cross-ref): Amd 15 (pre-spawn-fetch SHA) + Amd 16 (mid-spawn-periodic drift) + Amd 18 (Orchestrator §10 source-claim) + Amd 19 (pre-spawn-prompt-finalize window) = 4-layer temporal defense (when verify axis). 본 1-L = content fact axis 5th layer 신설 (what verify axis — temporal axis 와 disjoint).
- **ADR-073 §결정 1 verify-before-assert** (cross-ref, Orchestrator 행위 한정): Orchestrator cross-repo state assertion 시 `git fetch origin` + `git show origin/main:<path>` direct verify + `verified-via` annotation. 본 1-L = ADR-073 의 spawn prompt content 영역 확장 — Orchestrator 가 spawn prompt 작성 시 upstream-inherited fact verify (read-side cross-repo state verify ↔ write-side spawn prompt content verify 인접 axis, ADR-082 layer 영역 안 codify).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-fact-verify` warning-tier deferred-followup append. Wave 2 mechanical wire (Python SSOT lint per ADR-061 `scripts/lib/check_spawn_prompt_fact_verify.py` + `scripts/check-spawn-prompt-fact-verify.sh` bash thin wrapper + `templates/github-workflows/spawn-prompt-fact-verify.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-spawn-prompt-fact-verify.bats` fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 `hotfix-bypass:spawn-prompt-fact-verify` MINOR bump + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split 답습).

Wave 1 retain rationale: mechanical wire 의 detection logic (spawn prompt 안 inherited fact 식별 trigger / verified-via annotation 부재 sentinel / fact-correction marker presence verify / spawn_prompt_fact_verified field presence verify / False-positive 완화 guards 영역 — code-span EXEMPT / quoted-text EXEMPT / templates/** EXEMPT / docs/stories/§9 transcript EXEMPT) = sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

#### Option A vs B 결정 rationale (ArchitectAgent chief author 자율)

- **Option A (새 ADR-NNN 신설)**: 새 ADR `ADR-NNN-spawn-prompt-fact-verify-before-trust-mandate` 신설 — verify axis disjoint axis 신설 (Amd 5 1-C user-utterance verbatim 형식 axis 와 별도 ADR file). **REJECT 사유**: super-class fragmentation 위험 (ADR-082 already permanent governance anchor verify-before-trust 4-layer 의 internal lane agent self-write super-class SSOT) + governance hygiene 위배.
- **Option B (ADR-082 Amendment 23 super-class scope expansion)** — **채택**: super-class 안 sub-scope axis disjoint 누적 1-L 신설 (1-A ~ 1-K 와 disjoint axis content fact verify). axis 정합 영역 명확 (verify axis 동일 super-class 안 sub-scope 추가). ratchet 강화 방향 (11 sub-scope → 12 sub-scope, sub-scope count 무한 확장 아닌 axis disjoint 영역 누적). PMOAgent §5 inline ADR draft scope 3-form (Phase 0 brainstorm spawn-prompt fact verify + PR commit message defer rationale verify + follow-up Issue body 발의 시 fact verify) 모두 본 1-L 4-tuple primitive (a) upstream-inherited fact 식별 4 sub-source cover.

#### Amendment 23 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 23 scope = 본문 §결정 1-13 + sub-scope 1-L 신설 + Amendment 1-22 강화 방향 only (sub-scope ratchet 강화 + content fact axis 5th layer 신설 — 4-layer temporal defense 와 disjoint complement). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합 (CFP-1149 Amendment 8 symmetric evidence-gated 정합). META-self-applied (§결정 10.D 18th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 4th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + mid-flight collision recovery 2nd applied case after CFP-FU-A Amd 19).

#### Related (Amendment 23 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append + atomic renumber (adr_number 82 amendment_id 23 reserved_by_cfp CFP-1590 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G META 4th applied case (Amd 18 CFP-1342 1st + Amd 21 CFP-1578 2nd + Amd 22 CFP-1601 3rd precedent 답습 + mid-flight collision recovery 2nd applied case after CFP-FU-A Amd 19)
- `<internal-docs>/plugin-codeforge/retros/2026-05-25-cfp-1523-confluence-ia-real-backfill.md` — PMOAgent CFP-1523 retro §5 inline ADR draft anchor (Orchestrator → ArchitectAgent spawn carry-over source)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 23 sub-scope 1-L cross-ref 1 단락 append (CFP-506 line cap 정합)
- `CHANGELOG.md` — [Unreleased] Added entry append ([CFP-1590] ADR-082 Amendment 23 sub-scope 1-L spawn prompt fact verify-before-trust mandate + mid-flight CFP-1601 collision recovery)
- `docs/evidence-checks-registry.yaml` — warning-tier deferred-followup entry `spawn-prompt-fact-verify` initial registration (ADR-060 §결정 5 정합)
- `templates/github-workflows/spawn-prompt-fact-verify.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)

## Amendment 24 — §결정 1 layer 1 sub-scope (1-M) 신설 (own-author synthesis 보고 vs actual git commit gap verify mandate, CFP-1589, 2026-05-25 KST)

### Trigger

**F-DR-003 carrier** — CFP-1523 retro carry-over. ADR-082 §결정 1 layer 1 sub-scope axis disjoint super-class scope expansion. anchor_id = `synthesis_vs_commit_gap_at_lane_verdict` / root_cause_class = `own-author-output-vs-actual-artifact-gap`. pattern_count 1 deferred-followup carrier (Wave 1 declaration-only mandate, pattern_count 누적 시 Wave 2 mechanical wire 별 carrier 발의).

| # | Carrier | Synthesis vs commit gap pattern |
|---|---|---|
| 1 | CFP-1523 carrier F-DR-002 P0 finding (Phase 1 ArchitectPL verdict packet) | ArchitectPL verdict packet `Artifacts written: <file>` 보고 했으나 **실 git commit 0건** — worktree only modified/untracked, synthesis 단계 안 author 자체가 자기 작업 결과를 잘못 claim. DesignReviewPL audit verify-before-trust direct git status verify 후 detect → FIX iter 1 dispatch. memory `project_cfp_1523_complete.md` 안 finding 3 박제. |

### sub-scope 1-M axis 정합

본 Amendment 24 = sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L) precedent 답습 (closed-set ratchet 강화). 본 Amendment 24 = sub-scope (1-M) append.

> sub-scope 1-M = **own-author synthesis 보고 vs actual artifact (git commit) gap own-author verify axis** 신설 — author 자체가 자기 작성 결과를 잘못 claim ('Artifacts written: <file>' 보고 했으나 실 git commit 0건, worktree only modified/untracked) 차단. 작성 결과의 actual git commit verify mandate.

#### 1-M 4-tuple primitive — own-author synthesis 보고 vs actual git commit gap verify mandate

ArchitectPL / Dev / lane PL 가 verdict / 산출 / 완료 보고 작성 시점 4 의무:

1. **synthesis 보고 시점 actual git commit verify 의무** — author 가 verdict / 산출 / 완료 보고 작성 시점 `git -C <worktree> log --oneline origin/main..HEAD` direct execute + actual commit list 확인 의무. worktree modified/untracked 영역 commit 0건 미포함. claim 'Artifacts written: <file>' = actual commit hash 매핑 의무 (commit-bound claim, worktree-bound claim 금지).
2. **review-verdict-v4 packet 안 optional `artifact_commits[]` field 영역** — commit hash array (40-char hex), future MINOR bump v4.9 → v4.10 carrier 별 sub-CFP. packet 안 `artifacts_written[]` claim ↔ `artifact_commits[]` hash array 1:1 매핑 verify.
3. **verify-before-trust 4-layer 정합 — Story §14 Lane Evidence row append 시 actual commit verify** — lane outcome row append 시 `git log` actual commit hash 인용 의무 (ADR-073 verify-before-assert + ADR-082 §결정 1 layer 1 sub-scope 1-M dual binding). row append 시 cited commit hash = actual `git log origin/main..HEAD` 결과 매핑 verify.
4. **`synthesis_vs_commit_gap_verified: <bool>` field annotation 의무** — synthesis packet / verdict packet / 완료 보고 안 명시 (write-time semantic truth verify, annotation 부재 시 sentinel 발화).

#### 1-M disjoint axis cross-ref

- **1-L** (spawn prompt fact verify, Amd 23): spawn prompt 안 인용 fact (numeric / state / count / sister carrier claim) 의 **upstream-inherited fact verify axis** — 4 sub-source (사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) input verify (synthesis input 측). 본 1-M = author 자체가 자기 작성 결과 vs actual artifact gap own-author verify axis (synthesis output ↔ git commit downstream, own-author self-verify). 1-L + 1-M = input-output paired axis (upstream input vs own-author output disjoint complement).
- **Amd 22 §결정 1-K (numeric claim write-time strict claim mandate, CFP-1601)**: own author write-time 안 numeric claim source/value strict verify (6-dimension closed-set line/file/API/pattern/commit/row count). 본 1-M = own-author synthesis 결과 vs actual artifact gap (synthesis output ↔ git commit downstream, numeric 영역 외 artifact identity claim 영역). own author write-time numeric value verify ↔ own-author synthesis output ↔ artifact gap verify disjoint (axis 인접하나 verify 대상 disjoint — 1-K = numeric value source command + 1-M = artifact existence + identity).
- **Amd 18 §결정 1-H (Orchestrator §10 FIX Ledger resolution source/evidence, CFP-1342)**: Orchestrator monopoly §10 FIX Ledger row resolution field claim source/evidence verify (fix-event-v1 contract level Orchestrator self-write monopoly axis). 본 1-M = ArchitectPL / Dev / lane PL synthesis 보고 vs actual git commit gap (lane agent self-write own-author axis, fix-event-v1 contract 영역 외). Orchestrator monopoly axis ↔ lane PL own-author axis disjoint complement.
- **Amd 5 §결정 1-C (user-utterance verbatim block 의무)**: 사용자 발화 content 전달 **형식 verbatim 의무** (block 형식 axis — 사용자 발화 paraphrase / 요약 / 재합성 차단, upstream content content axis). 본 1-M = author 자체 own-author output ↔ actual artifact gap verify (own-author output verify axis). upstream content 형식 axis ↔ own-author output gap axis disjoint.
- **Amd 20 §결정 15 (Issue body stale-claim super-class write-time pre-screen)**: Issue body author 자기 작성 content 안 stale claim (a-PR merge state / b-CFP merge state / c-count number / d-sister carrier origin) — **작성자 책임 write-time pre-screen** (self-write content stale claim 영역). 본 1-M = author 자체 synthesis output ↔ actual artifact existence gap (자기 작성 결과 vs actual commit gap, self-write artifact identity 영역). self-write content stale claim ↔ self-write artifact identity disjoint complement.
- **ADR-073 §결정 1 verify-before-assert** (cross-ref, Orchestrator 행위 한정): Orchestrator cross-repo state assertion 시 `git fetch origin` + `git show origin/main:<path>` direct verify + `verified-via` annotation. 본 1-M = ADR-073 verify-before-assert primitive 의 lane PL synthesis-time 영역 확장 — ArchitectPL / Dev / lane PL synthesis 보고 시 actual git commit verify (read-side cross-repo state verify ↔ write-side own-author synthesis output verify 인접 axis, ADR-082 layer 영역 안 codify).

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `synthesis-vs-commit-gap-check` warning-tier deferred-followup append. Wave 2 mechanical wire (Python SSOT lint per ADR-061 `scripts/lib/check_synthesis_vs_commit_gap.py` + `scripts/check-synthesis-vs-commit-gap.sh` bash thin wrapper + `templates/github-workflows/synthesis-vs-commit-gap-check.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-synthesis-vs-commit-gap.bats` fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 `hotfix-bypass:synthesis-vs-commit-gap-check` MINOR bump + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합 + review-verdict-v4 v4.9 → v4.10 MINOR carrier 별 sub-CFP `artifact_commits[]` optional field schema 신설) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435/1559/1578/1601/1590 Wave 1→Wave 2 split 답습).

Wave 1 retain rationale: mechanical wire 의 detection logic (verdict packet 안 `artifacts_written[]` claim trigger 감지 + `git log origin/main..HEAD` actual commit list 매핑 verify + `artifact_commits[]` field presence verify + `synthesis_vs_commit_gap_verified` annotation 부재 sentinel + False-positive 완화 guards 영역 — code-span EXEMPT / quoted-text EXEMPT / templates/** EXEMPT / docs/stories/§9 transcript EXEMPT) = sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-1437/1436/1435/1559/1578 Wave 1→Wave 2 split 답습).

pattern_count 1 reach (CFP-1523 F-DR-002 single occurrence) → ADR-045 §D-9 threshold 2 미달 — declaration-only Wave 1 forcing function anchor 우선 + pattern_count 누적 시 (예 pattern_count 2+ reach) Wave 2 mechanical wire 별 carrier 발의 (ADR-082 §결정 6 retain pattern 답습 — pattern_count 누적 시 follow-up CFP MUST promote). 본 carrier = preventive declarative anchor (next occurrence 차단 forcing function).

#### Option A vs B 결정 rationale (ArchitectAgent chief author 자율)

- **Option A (새 ADR-NNN 신설)**: 새 ADR `ADR-NNN-synthesis-vs-commit-gap-verify-mandate` 신설 — verify axis disjoint axis 신설 (Amd 23 1-L upstream-inherited input axis 와 별도 ADR file). **REJECT 사유**: super-class fragmentation 위험 (ADR-082 already permanent governance anchor verify-before-trust 4-layer 의 internal lane agent self-write super-class SSOT) + governance hygiene 위배 (Amd 23 Option B precedent 답습 정합 — super-class scope expansion 우선).
- **Option B (ADR-082 Amendment 24 super-class scope expansion)** — **채택**: super-class 안 sub-scope axis disjoint 누적 1-M 신설 (1-A ~ 1-L 와 disjoint axis own-author synthesis 보고 vs actual artifact gap verify). axis 정합 영역 명확 (verify axis 동일 super-class 안 sub-scope 추가). ratchet 강화 방향 (12 sub-scope → 13 sub-scope, sub-scope count 무한 확장 아닌 axis disjoint 영역 누적). 1-L + 1-M = input-output paired complement axis. Amd 23 Option B (super-class scope expansion) precedent 답습.

#### Amendment 24 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 24 scope = 본문 §결정 1-13 + sub-scope 1-M 신설 + Amendment 1-23 강화 방향 only (sub-scope ratchet 강화 + own-author synthesis output ↔ actual artifact gap verify axis 신설 — 1-L upstream-inherited input fact verify 와 disjoint complement). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합 (CFP-1149 Amendment 8 symmetric evidence-gated 정합). META-self-applied (§결정 10.D 19th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 5th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590).

#### Related (Amendment 24 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append (adr_number 82 amendment_id 24 reserved_by_cfp CFP-1589 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G META 5th applied case (Amd 18 CFP-1342 1st + Amd 21 CFP-1578 2nd + Amd 22 CFP-1601 3rd + Amd 23 CFP-1590 4th precedent 답습)
- `<internal-docs>/plugin-codeforge/retros/2026-05-25-cfp-1523-confluence-ia-real-backfill.md` — F-DR-002 origin finding (memory `project_cfp_1523_complete.md` 안 finding 3 박제)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 24 sub-scope 1-M cross-ref 1 줄 추가 (CFP-506 line cap 정합)
- `CHANGELOG.md` — [Unreleased] Added entry append ([CFP-1589] ADR-082 Amendment 24 sub-scope 1-M synthesis vs commit gap verify mandate)
- `docs/evidence-checks-registry.yaml` — warning-tier deferred-followup entry `synthesis-vs-commit-gap-check` initial registration (ADR-060 §결정 5 정합)
- `templates/github-workflows/synthesis-vs-commit-gap-check.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)
- `docs/inter-plugin-contracts/review-verdict-v4.md` — v4.9 → v4.10 MINOR carrier 별 sub-CFP `artifact_commits[]` optional field schema 신설 declarative anchor (Wave 2 carrier 분리)


## Amendment 25 — §결정 1 layer 1 sub-scope (1-N) numeric claim write-time verify Wave 2 mechanical enforcement wire (CFP-1612 carrier)

**Issue #1612 HIGH FU-A from CFP-1601 retro carrier** — sub-scope 1-K (Amendment 22, CFP-1601) declaration-only behavioral mandate 의 Wave 2 mechanical enforcement wire. anchor_id = `numeric_claim_write_time_verify_wave2_wire` / root_cause_class = `declaration-to-mechanical-enforce-promotion`. ADR-082 §결정 1 layer 1 sub-scope axis 인접 (1-K mandate 자체 ↔ 본 1-N Wave 2 wire) — declaration mandate (1-K) ↔ mechanical enforcement scope (1-N) disjoint complement layered axis (Wave 1 declarative → Wave 2 mechanical lint enforce per ADR-060 §결정 5 default warning mode).

| # | Carrier | Wave 2 wire pattern |
|---|---|---|
| 1 | CFP-1612 carrier (Issue #1612 HIGH FU-A) | sub-scope 1-K Amd 22 CFP-1601 Wave 1 declaration-only behavioral mandate 의 mechanical enforcement 부재 영역 — lint script Python SSOT per ADR-061 + bash thin wrapper + workflow yml hydrate + `.github/workflows/` byte-identical mirror per ADR-005 + bats fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 MINOR + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합. Wave 1 → Wave 2 split precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589 11번째 instance. |

### sub-scope 1-N axis 정합

본 Amendment 25 = sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M) precedent 답습 (closed-set ratchet 강화). 본 Amendment 25 = sub-scope (1-N) append.

> sub-scope 1-N = **1-K declaration-only behavioral mandate 의 Wave 2 mechanical enforcement wire SSOT axis** 신설 — sub-scope 1-K (Amendment 22, CFP-1601) 의 4-step verify-before-write 의무 + 6 numeric claim closed-set dimension declaration mandate 를 lint script + workflow + bats fixture + label-registry MINOR + evidence-checks-registry warning-tier initial registration 로 mechanical enforce. declaration → mechanical enforce 의 promotion path codify.

#### 1-N 4-tuple primitive — numeric claim write-time verify Wave 2 mechanical wire scope

Wave 2 mechanical wire 영역 4 의무 (Phase 2 sub-carrier — DeveloperPL + QADev spawn 시):

1. **lint script SSOT (Python per ADR-061 multi-line Python convention)** — `scripts/lib/check_numeric_claim_write_time.py` Python SSOT (> 5줄 → 외부 `.py` file 의무) + `scripts/check-numeric-claim-write-time-verify.sh` bash thin wrapper (`python -m scripts.lib.check_numeric_claim_write_time "$@"` shim 형식). bash heredoc 금지 + Windows Git Bash / MSYS2 / WSL backslash escape inconsistency 차단 (ADR-061 §결정 1).
2. **6 dimension detection logic (Python dict SSOT)** — (i) **line count** (regex pattern e.g. `\d+\s*(lines?|줄)` + source command `wc -l` / `grep -c` line-occurrence) / (ii) **file count** (regex `\d+\s*(files?|파일)` + source command `find ... | wc -l` / `git diff --shortstat`) / (iii) **API count** (regex `\d+\s*(MCP\s*calls?|API\s*calls?)` + source command `grep -c mcp__github__` / agent spawn count) / (iv) **pattern_count** (regex `pattern_count\s*[:=]?\s*\d+` + source command cross-Story ADR-045 §D-9 base) / (v) **commit count** (regex `\d+\s*commits?` + source command `git rev-list --count`) / (vi) **row count** (regex `\d+\s*(rows?|entries|행)` + source command yaml row / md table row / contract field). 각 dimension 별 numeric claim regex pattern + source command pattern map (Python dict SSOT 1 file).
3. **FP guard 4종 + ReDoS guard** — (a) **code-span EXEMPT** (backtick block `` ` ``) (b) **quoted-text EXEMPT** (`>` blockquote / `'/'` quote) (c) **templates/** EXEMPT** (canonical example pattern) (d) **docs/stories/§9 transcript EXEMPT** (Round 0 verbatim cite) (e) **PER_BLOCK_SCAN_CAP=50 line CodeQL ReDoS guard** (CFP-1497 PR #1499 sentinel verbatim 답습, nested quantifier regex 절대 금지). FP guard list 본문 enumerate (Wave 2 lint design 시 결정).
4. **workflow + bypass + evidence-checks-registry binding** — `templates/github-workflows/numeric-claim-write-time-verify.yml` workflow (PR-open trigger + warning-first `continue-on-error: true`) + `.github/workflows/numeric-claim-write-time-verify.yml` byte-identical mirror per ADR-005 + `hotfix-bypass:numeric-claim-write-time-verify` bypass label per ADR-024 Amendment 6/8 §결정 6.A 5 lint chain inherit (audit-trailed exception channel) + evidence-checks-registry warning-tier initial registration `numeric-claim-write-time-verify` entry append (ADR-060 §결정 5 default warning mode, pattern_count ≥ N 추가 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리).

#### 1-N disjoint axis cross-ref

- **Amd 22 §결정 1-K (numeric claim write-time strict claim mandate, CFP-1601)**: declaration-only behavioral mandate SSOT (4-step verify-before-write + 6 numeric claim closed-set dimension enum). 본 Amendment 25 = 1-K Wave 2 mechanical enforcement wire SSOT (lint script + workflow + bats fixture binding). 1-K = behavioral mandate axis / 1-N = mechanical enforcement wire axis disjoint complement layered (declaration → enforce promotion path).
- **Amd 17 §결정 1-G (amendment-slot pre-reservation strict claim, CFP-1435)**: amendment-slot reservation lifecycle strict claim axis (status enum 4-value reserved|active|abandoned|superseded). 본 1-N = mechanical lint enforcement axis (행위 = lint script + workflow + bypass + registry initial registration). 1-G 와 axis 인접하나 verify 대상 disjoint (reservation slot vs numeric claim value mechanical enforce).
- **Amd 20 §결정 15 (Issue body stale-claim super-class write-time pre-screen, CFP-1559)**: Issue body author 자기 작성 content 안 4 sub-pattern stale claim (PR / CFP merge state / count number / sister carrier origin) write-time pre-screen. 본 1-N = numeric claim 6 dimension mechanical enforcement wire (Issue body 영역 외 wide-scope numeric claim mechanical enforce). 1-K dimension (iii) API count + (iv) pattern_count + (v) commit count + (vi) row count 등 Issue body 외 영역 cover.
- **Amd 23 §결정 1-L (spawn prompt fact verify upstream-inherited stale fact super-class, CFP-1590)**: spawn prompt content 안 인용 fact 의 upstream-inherited fact verify axis (4 sub-source: 사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file). 본 1-N = own-author write-time numeric claim mechanical enforce (1-K Wave 2 wire). 1-L = upstream input fact verify (synthesis input 측) / 1-K + 1-N = own-author output numeric value verify (synthesis output 측). 1-L + (1-K + 1-N) = input-output paired axis disjoint complement.
- **Amd 24 §결정 1-M (own-author synthesis 보고 vs actual git commit gap, CFP-1589)**: own-author synthesis output ↔ actual artifact (git commit) gap verify axis (artifact identity claim 영역). 본 1-N = numeric claim value source command mechanical enforce (6 dimension numeric value verify, 본 Amendment 25 declaration → mechanical enforce promotion). 1-M = artifact identity gap verify / 1-K + 1-N = numeric value verify disjoint (axis 인접하나 verify 대상 disjoint).

#### Wave 1 (declarative) ↔ Wave 2 (mechanical) split rationale

**Wave 1 = 본 Amendment 25 declarative SSOT** (Phase 1 PR — 본 carrier):
- ADR-082 §결정 1 layer 1 sub-scope 1-N append (본 §)
- `mechanical_enforcement_actions[]` entry `numeric-claim-write-time-verify` status `deferred-followup` → `warning-tier wire complete (CFP-1612 Wave 2 carrier)` 갱신
- `docs/adr/ADR-RESERVATION.md` amendments_reserved[] row 25 pre-append (adr_number 82 amendment_id 25 reserved_by_cfp CFP-1612 status active)
- `docs/evidence-checks-registry.yaml` warning-tier initial registration entry `numeric-claim-write-time-verify` append (ADR-060 §결정 5 정합)
- `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump v2.75 → v2.76 + `hotfix-bypass:numeric-claim-write-time-verify` 101st family member append
- `docs/inter-plugin-contracts/MANIFEST.yaml` label_registry version `2.75` → `2.76` 갱신
- `CHANGELOG.md` `[Unreleased]` Added entry append

**Wave 2 = actual mechanical wire** (Phase 2 PR 별도 sub-carrier — DeveloperPL + QADev spawn):
- `scripts/lib/check_numeric_claim_write_time.py` Python SSOT (ADR-061 multi-line Python convention)
- `scripts/check-numeric-claim-write-time-verify.sh` bash thin wrapper (`python -m ...` shim)
- `templates/github-workflows/numeric-claim-write-time-verify.yml` workflow
- `.github/workflows/numeric-claim-write-time-verify.yml` byte-identical mirror per ADR-005
- `tests/scripts/check-numeric-claim-write-time-verify/test_*.bats` fixture (5 markers + 6 dimension TCs RED→GREEN stash proof per §결정 11.A)

precedent: CFP-1437 (1-E pre-spawn pin) → Wave 2 CFP-1489 / CFP-1436 (1-F mid-spawn drift) → Wave 2 CFP-1500 / CFP-1435 (1-G slot reservation) → Wave 2 CFP-1497 / CFP-FU-A Amd 19 (1-I pre-spawn-prompt-finalize) → Wave 2 CFP-1502 / CFP-1559 (1-O Issue body stale-claim super-class) → Wave 2 별도 sub-carrier / CFP-1578 (1-J cross-repo worktree target authority) → Wave 2 별도 sub-carrier / CFP-1601 (1-K numeric claim mandate) → Wave 2 본 CFP-1612 = 8th carrier / CFP-1590 (1-L spawn prompt fact) → Wave 2 별도 sub-carrier / CFP-1589 (1-M synthesis vs commit gap) → Wave 2 별도 sub-carrier = 11번째 Wave 1→Wave 2 split instance.

#### Wave 3 escalation path

pattern_count ≥ N 추가 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리 (ADR-060 §결정 6 promotion gate AND 3/3 — (a) PR 누적 ≥ 20 + (b) bypass 외 failure = 0 + (c) sibling Story merged). 본 1-K + 1-N evidence base = CFP-1571 §3.2 line count drift + CFP-1581 §3.2 file count drift = pattern_count 2 reach (Wave 1 declaration 정합). Wave 2 mechanical enforce 후 sentinel pattern_count 추가 누적 시 Wave 3 escalation 별 carrier 발의.

#### Option A vs B 결정 rationale (ArchitectAgent chief author 자율)

- **Option A (새 ADR-NNN 신설)**: 새 ADR `ADR-NNN-numeric-claim-write-time-verify-wave2-wire` 신설 — Wave 2 mechanical enforcement wire 영역 separate ADR. **REJECT 사유**: super-class fragmentation 위험 (Wave 1 mandate Amd 22 CFP-1601 이 ADR-082 §결정 1 sub-scope 1-K 안 codify 됨 — Wave 2 wire 도 동일 super-class 안 sub-scope 1-N 으로 axis 정합). Amd 22 1-K mandate ↔ Amd 25 1-N Wave 2 wire = 동일 axis 안 declaration → mechanical enforce promotion path layered, separate ADR fragmentation 회피.
- **Option B (ADR-082 Amendment 25 sub-scope 1-N append, Wave 1 declarative SSOT + Wave 2 mechanical wire 별도 sub-carrier)** — **채택**: super-class 안 sub-scope (1-N) Wave 2 wire SSOT codify (1-K Wave 1 mandate 의 Wave 2 enforce wire). axis 정합 명확 (declaration mandate ↔ mechanical enforcement scope disjoint complement layered axis). Wave 1 → Wave 2 split precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589 11번째 instance 답습. ratchet 강화 방향 (declarative → mechanical enforce).

#### Amendment 25 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 25 scope = 본문 §결정 1-13 + sub-scope 1-N 신설 + Amendment 1-24 강화 방향 only (sub-scope ratchet 강화 + declaration-only mandate → mechanical enforcement wire promotion path). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합 (CFP-1149 Amendment 8 symmetric evidence-gated 정합). META-self-applied (§결정 10.D 20th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 6th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590 + Amd 24 CFP-1589 + Amendment 22 §결정 1-K 1st applied for Wave 2 wire carrier + Amendment 23 §결정 1-L 1st applied recursive dogfooding mid-flight collision recovery 3rd applied after CFP-FU-A Amd 19 + CFP-1590 Amd 23).

#### Related (Amendment 25 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append (adr_number 82 amendment_id 25 reserved_by_cfp CFP-1612 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G META 6th applied case (Amd 18 CFP-1342 1st + Amd 21 CFP-1578 2nd + Amd 22 CFP-1601 3rd + Amd 23 CFP-1590 4th + Amd 24 CFP-1589 5th precedent 답습)
- `docs/evidence-checks-registry.yaml` — warning-tier initial registration entry `numeric-claim-write-time-verify` append (ADR-060 §결정 5 default warning mode + ADR-024 Amendment 6/8 §결정 6.A 5 lint chain inherit)
- `docs/inter-plugin-contracts/label-registry-v2.md` — MINOR bump v2.75 → v2.76 + `hotfix-bypass:numeric-claim-write-time-verify` 101st family member append (audit-trailed exception channel)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — label_registry version `2.75` → `2.76` 갱신
- `CHANGELOG.md` — [Unreleased] Added entry append ([CFP-1612] ADR-082 Amendment 25 sub-scope 1-N numeric claim write-time verify Wave 2 mechanical enforcement wire)
- `templates/github-workflows/numeric-claim-write-time-verify.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier — actual script + bats fixture file write)
- Wave 2 별 sub-CFP carrier (Phase 2 PR scope): `scripts/lib/check_numeric_claim_write_time.py` + `scripts/check-numeric-claim-write-time-verify.sh` + `templates/github-workflows/numeric-claim-write-time-verify.yml` + `.github/workflows/numeric-claim-write-time-verify.yml` byte-identical mirror + `tests/scripts/check-numeric-claim-write-time-verify/test_*.bats` (5 markers + 6 dimension TCs RED→GREEN stash proof per §결정 11.A)


## Amendment 26 — §결정 1 layer 1 sub-scope (1-O) 신설 (PR commit message + PR body 안 numeric claim write-time strict claim mandate, CFP-1637, 2026-05-25 KST)

**ADR-045 §D-9 Pattern 2 Mandatory escalation 산물** — anchor_id = `pr_commit_body_numeric_claim_write_time_strict_claim_mandate` / root_cause_class = `meta-self-application-accuracy-violation-pr-layer`. ADR-082 §결정 1 layer 1 sub-scope (1-K Amendment 22 CFP-1601 carrier write-time governance docs scope) + (1-N Amendment 25 CFP-1612 carrier Wave 2 mechanical wire scope) ↔ 본 sub-scope **1-O** (PR commit message + PR body layer 3rd axis) axis disjoint complement.

### Pattern 2 evidence (pattern_count 2 reach — ADR-045 §D-9 Mandatory threshold)

| # | Carrier | Layer (scope axis) | claim vs actual |
|---|---|---|---|
| 1 | CFP-1601 §13.C row 3 (META 1st applied carrier of 1-K, codify carrier 자체 안 self-violation) | Story file §13.C scope (sub-scope 1-K Amd 22 territory — write-time governance docs scope: ADR text / Change Plan / Story / spawn packet wording / Issue body) | claim "**11**" vs actual **15** (Wave 2 split precedent count) |
| 2 | CFP-1612 PR #1631 commit message + PR body (META 1st applied carrier of 1-N, Wave 2 mechanical wire carrier 자체 안 self-violation) | PR commit message + PR body scope (1-K + 1-N 양 sub-scope 영역 외 — **NEW scope codify 의무 영역, 본 1-O 영역**) | claim "**29 / ~470 / ~155**" vs canonical actual **30 / 605 / 183** (commit LOC / added LOC / del LOC) |

**Pattern 2 = META self-application accuracy violation pattern_count 2 reach (ADR-045 §D-9 threshold 2 = Mandatory escalation 정합)**. 두 instance 의 sub-scope 영역 disjoint (Story scope = 1-K territory / PR commit msg + PR body scope = 본 1-O territory) 동일 root pattern (META self-application accuracy violation). Pattern 2 분류 anchor = `meta-self-application-accuracy-violation`.

### sub-scope 1-O axis 정합

본 Amendment 26 = sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M/1-N) precedent 답습 (closed-set ratchet 강화). 본 Amendment 26 = sub-scope (1-O) append.

> sub-scope 1-O = **PR commit message + PR body 안 numeric claim write-time strict claim mandate axis** 신설 — sub-scope 1-K (Amendment 22, CFP-1601) write-time governance docs scope 의 4-step verify-before-write 의무 + 6 numeric claim closed-set dimension declaration mandate 를 **PR-level artifact layer (commit message body + PR description body, git/GitHub layer)** 로 scope 확장. Wave 1 declaration-only — Wave 2 mechanical wire (current `scripts/lib/check_numeric_claim_write_time.py` Python SSOT scope 확장 to PR commit msg + PR body detection layer) = 별 sub-CFP carrier.

#### 1-O 4-tuple primitive — PR commit message + PR body numeric claim write-time strict claim scope

PR commit message + PR body 영역 4 의무 inherit from 1-K Amd 22 (axis 변경 = scope target, mandate 자체는 byte-pattern 동일):

1. **source command identify (Step 1, inherit from 1-K)** — claim 의 ground truth source command 명시 의무. 예 (PR-level artifact 영역):
   - **commit count claim** (`N commits`, `N개 commit`, etc.): source command `git rev-list --count <range>` 또는 `git log --oneline <range> | wc -l`
   - **LOC claim** (`N lines`, `+M -N LOC`, `~K lines`, etc.): source command `git diff --shortstat <range>` 또는 `git diff <range> --stat | tail -1`
   - **file count claim** (`N files changed`, etc.): source command `git diff --shortstat <range>` 또는 `git diff <range> --name-only | wc -l`
   - **pattern_count claim** (cross-Story aggregate): source command PMOAgent retro corpus enumeration
2. **direct execute (Step 2, inherit from 1-K)** — write 직전 source command 실 execute 의무. claim write 후 verify ≠ Step 2 (write 후 verify = 사후 정정, write-time strict mandate 위배).
3. **claim ↔ actual cross-verify (Step 3, inherit from 1-K)** — Step 2 actual output vs Step 1 source command 의 semantic intent 정합 verify. line-grep occurrence vs sequential entry count 등 source command 다중 semantic 영역 = source command 정밀화 (`grep -oE ... | tail -1` 등) 의무.
4. **write only on match (Step 4, inherit from 1-K)** — Step 3 match 시에만 write. mismatch 시 source command 정정 또는 claim 수정 후 Step 2 재실행. PR open 후 commit amend / PR description edit 도 동일 mandate 적용.

#### 1-O disjoint axis cross-ref

- **Amd 22 §결정 1-K (numeric claim write-time strict claim mandate, CFP-1601 — write-time governance docs scope)**: scope target docs = governance docs in-tree (ADR text / Change Plan / Story / spawn packet wording / Issue body). 본 Amendment 26 sub-scope 1-O = scope target PR-level artifact (commit message body + PR description body, git/GitHub layer). 1-K = governance docs layer / 1-O = PR-level artifact layer disjoint complement (scope target layer 3rd axis).
- **Amd 25 §결정 1-N (numeric claim write-time verify Wave 2 mechanical enforcement wire, CFP-1612)**: mechanism = mechanical lint enforce (scripts/lib + workflow + bats wire) for 1-K mandate. 본 Amendment 26 sub-scope 1-O = declaration-only Wave 1 (1-O mechanical wire = 별 sub-CFP Wave 2 carrier, 1-N Python SSOT scope 확장 to PR commit msg + PR body detection layer). 1-N = mechanism axis (mechanical wire scope) / 1-O = scope target axis (PR-level artifact layer) disjoint complement.
- **Amd 17 §결정 1-G (amendment-slot pre-reservation strict claim, CFP-1435)**: amendment-slot reservation lifecycle strict claim axis (status enum 4-value reserved|active|abandoned|superseded). 본 1-O = PR-level artifact numeric claim write-time mandate axis (PR commit msg + PR body 6 numeric dimension verify). 1-G 와 axis disjoint (reservation slot lifecycle vs PR-level numeric value).
- **Amd 23 §결정 1-L (spawn prompt fact verify upstream-inherited stale fact super-class, CFP-1590)**: spawn prompt content 안 인용 fact 의 upstream-inherited fact verify axis (4 sub-source). 본 1-O = own-author PR commit msg + PR body write-time numeric claim verify (1-K mandate 의 PR-level scope 확장). 1-L = upstream input fact verify (synthesis input) / 1-K + 1-N + 1-O = own-author output numeric value verify (write-time output, governance docs + mechanical enforce + PR-level layer 3 sub-scope). 1-L + (1-K + 1-N + 1-O) = input-output paired axis disjoint complement.
- **Amd 24 §결정 1-M (own-author synthesis 보고 vs actual git commit gap, CFP-1589)**: own-author synthesis output ↔ actual artifact (git commit) gap verify axis (artifact identity claim 영역, `git log` direct verify). 본 1-O = numeric value verify within commit message body + PR body (6 numeric dimension value verify, axis disjoint from artifact identity gap). 1-M = artifact identity gap verify / 1-O = numeric value within artifact verify (axis 인접하나 verify 대상 disjoint — artifact existence vs numeric content within artifact).

#### 1-K vs 1-N vs 1-O 3-axis disjoint matrix

| Axis | 1-K (Amd 22, CFP-1601) | 1-N (Amd 25, CFP-1612) | 1-O (Amd 26, CFP-1637) |
|---|---|---|---|
| **Scope target** | Governance docs in-tree (ADR text / Change Plan / Story / spawn packet / Issue body) | (inherits 1-K scope, mechanism layer wire) | **PR commit message body + PR description body (git/GitHub layer)** |
| **Mandate type** | 4-step verify-before-write declaration | Mechanical lint enforce (1-K Wave 2 wire) | 4-step verify-before-write declaration (inherits 1-K mandate, scope 확장) |
| **6 numeric dimension** | line / file / API / pattern / commit / row | Same 6 dimension (mechanical detection) | Same 6 dimension (declaration, inherits 1-K) |
| **Wave 1 / Wave 2** | Wave 1 declaration-only | Wave 2 mechanical wire (1-K Wave 1 promote) | **Wave 1 declaration-only (1-O Wave 2 mechanical wire = 별 sub-CFP carrier)** |
| **Forcing function source** | pattern_count 2 (CFP-1571 + CFP-1581) ADR-045 §D-9 | Issue #1612 HIGH FU-A from CFP-1601 retro | pattern_count 2 (CFP-1601 §13.C row 3 + CFP-1612 PR #1631 commit msg) ADR-045 §D-9 |

#### Wave 1 (declarative) ↔ Wave 2 (mechanical) split rationale

**Wave 1 = 본 Amendment 26 declarative SSOT** (Phase 1 PR — 본 carrier):
- ADR-082 §결정 1 layer 1 sub-scope 1-O append (본 §)
- `docs/adr/ADR-RESERVATION.md` amendments_reserved[] row 26 pre-append (adr_number 82 amendment_id 26 reserved_by_cfp CFP-1637 status active)
- Story file (`stories/CFP-1637.md`) + Change Plan (`change-plans/cfp-1637-adr082-amd-26-1o.md`) in codeforge-internal-docs
- `CHANGELOG.md` `[Unreleased]` Added entry append (declaration-only — script/workflow/bats wire 0건)

**Wave 2 = actual mechanical wire** (별 sub-CFP carrier — Phase 2 PR scope, future):
- `scripts/lib/check_numeric_claim_write_time.py` Python SSOT scope 확장 to PR commit msg + PR body detection layer (current Python SSOT 의 6 dimension detection logic 재사용 + commit message + PR body 영역 wiretap)
- `templates/github-workflows/` workflow 신설 또는 기존 `numeric-claim-write-time-verify.yml` workflow scope 확장 (PR-open trigger 안 commit message body + PR body inspection)
- `tests/scripts/` bats fixture (PR commit msg + PR body fixture RED→GREEN stash proof per §결정 11.A)
- `docs/evidence-checks-registry.yaml` entry scope 확장 또는 신규 entry (warning-tier initial registration, ADR-060 §결정 5 정합)
- `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump (Wave 2 시 family member 신설 시)

precedent: CFP-1601 (1-K declaration) → Wave 2 CFP-1612 (1-N mechanical wire) → 본 CFP-1637 (1-O scope 확장 declaration, axis 3rd) → Wave 2 별 sub-CFP carrier (1-O mechanical wire) = 12번째 Wave 1→Wave 2 split lineage extension.

#### Wave 3 escalation path

pattern_count ≥ 3 추가 reach 시 1-O Wave 1 declarative → Wave 2 mechanical wire 승격 (Wave 2 별 sub-CFP carrier 발의 trigger). 본 1-O evidence base = CFP-1601 §13.C row 3 + CFP-1612 PR #1631 commit msg = pattern_count 2 reach (ADR-045 §D-9 Mandatory escalation 정합 — Wave 1 declarative codify 의무). 추가 pattern instance 누적 시 별 carrier 발의.

#### Option α vs β 결정 rationale (ArchitectAgent chief author 자율)

- **Option α (ADR-082 Amendment 26 sub-scope 1-O append — Wave 1 declarative SSOT only, mechanical wire 별 sub-CFP carrier)** — **채택**: super-class 안 sub-scope (1-O) append (axis disjoint from 1-K + 1-N — scope target layer 3rd axis: governance docs / mechanical wire mechanism / PR-level artifact). 1-K (governance docs scope) + 1-N (mechanical wire mechanism) ↔ 본 1-O (PR-level artifact scope target) = 3-axis disjoint matrix codify. Wave 1 declaration-only 답습 precedent (CFP-1601 Wave 1 → CFP-1612 Wave 2). axis 정합 명확 + super-class 안 closed-set ratchet 강화.
- **Option β (새 ADR-NNN 신설)**: 새 ADR `ADR-NNN-pr-commit-body-numeric-claim-strict-claim-mandate` 신설. **REJECT 사유**: super-class fragmentation 위험. 본 mandate = ADR-082 §결정 1 layer 1 sub-scope 1-K (Amd 22) 의 scope 확장 (write-time numeric claim verify mandate 의 PR-level artifact layer scope) — 동일 super-class 안 sub-scope (1-O) 으로 axis 정합 명확. Amd 22 1-K mandate ↔ Amd 26 1-O = 동일 axis 안 scope target 확장 (governance docs → PR-level artifact 3rd axis disjoint complement). separate ADR fragmentation 회피.

#### Amendment 26 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 26 scope = 본문 §결정 1-13 + sub-scope 1-O 신설 + Amendment 1-25 강화 방향 only (sub-scope ratchet 강화 + scope target layer 확장 PR-level artifact). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합 (CFP-1149 Amendment 8 symmetric evidence-gated 정합). META-self-applied (§결정 10.D 21st applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 7th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590 + Amd 24 CFP-1589 + Amd 25 CFP-1612 + 본 carrier + Amendment 22 §결정 1-K 2nd applied for scope target layer 확장 PR-level artifact + Amendment 25 §결정 1-N 1st applied for Wave 2 carrier reference).

#### META 21st applied case verbatim record

본 Amendment 26 자체가 META-self-applied (§결정 10.D 21st applied case). source command + actual + cross-verify 본문 박제:

- **Source command identify (Step 1)**: `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-write-time-self-write-verification-mandate.md | tail -1` (sequential max amendment_id slot, line-grep occurrence count 아님 — 1-K Step 1 source command precision rule 적용)
- **Direct execute (Step 2)**: ArchitectAgent Phase 1 spawn 시점 직접 실행 (origin/main HEAD `d1c629f0` post-CFP-1612 Amd 25 merge fresh fetch 후 rebase clean state)
- **Actual output (Step 2 result)**: `  - amendment_id: 25` (Amd 25 CFP-1612 점유, post-rebase HEAD origin/main = `d1c629f0`)
- **Cross-verify (Step 3)**: claim "next-slot = 26" ↔ actual `amendment_id: 25` (Amd 25 점유) → next-slot = 26 match `[verified]`. 정확 next-slot for CFP-1637 = **26** + sub-scope letter = **1-O** (1-N=CFP-1612 Amd 25 다음 sequential)
- **Write (Step 4)**: match 후 write — 본 Amendment 26 + sub-scope 1-O codify (frontmatter `amendments[]` row 26 append + 본 body section append + ADR-RESERVATION row 26 append + Story file + Change Plan)

META 21st applied case = pre-write source command direct verify + claim ↔ actual match 후 write only (write-after-claim 아닌 verify-then-write 강제). META 20th = CFP-1612 Amd 25 (Wave 2 mechanical wire carrier 자체 안 numeric claim verify, line-grep vs sequential entry semantic precision rule applied) 직후 sequential carrier.

#### Related (Amendment 26 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append (adr_number 82 amendment_id 26 reserved_by_cfp CFP-1637 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G META 7th applied case (Amd 18 CFP-1342 1st + Amd 21 CFP-1578 2nd + Amd 22 CFP-1601 3rd + Amd 23 CFP-1590 4th + Amd 24 CFP-1589 5th + Amd 25 CFP-1612 6th precedent 답습)
- Story file `c:/workspace/mclayer/codeforge-internal-docs/plugin-codeforge/stories/CFP-1637.md` (codeforge-internal-docs SSOT ADR-013 dogfood-out)
- Change Plan `c:/workspace/mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1637-adr082-amd-26-1o.md` (codeforge-internal-docs SSOT ADR-013 dogfood-out)
- `CHANGELOG.md` — [Unreleased] Added entry append ([CFP-1637] ADR-082 Amendment 26 sub-scope 1-O 신설 — PR commit message + PR body numeric claim write-time strict claim mandate, Wave 1 declarative-only)
- Wave 2 별 sub-CFP carrier (future): `scripts/lib/check_numeric_claim_write_time.py` scope 확장 to PR commit msg + PR body detection layer + workflow `templates/github-workflows/` 확장 + bats fixture + evidence-checks-registry entry scope 확장 또는 신규

## Amendment 27 — §결정 1 layer 1 sub-scope (1-P) 신설 (sub-scope 1-O Wave 2 mechanical enforcement wire, CFP-1647, 2026-05-26 KST)

**Issue #1647 HIGH FU-A from CFP-1637 retro carrier** — sub-scope 1-O (Amendment 26, CFP-1637) declaration-only behavioral mandate (PR commit message + PR body 안 numeric claim write-time strict claim mandate) 의 Wave 2 mechanical enforcement wire. anchor_id = `pr_commit_body_numeric_claim_write_time_verify_wave2_wire` / root_cause_class = `declaration-to-mechanical-enforce-promotion-pr-layer`. ADR-082 §결정 1 layer 1 sub-scope axis 인접 (1-O mandate 자체 ↔ 본 1-P Wave 2 wire) — declaration mandate (1-O) ↔ mechanical enforcement scope (1-P) disjoint complement layered axis (Wave 1 declarative → Wave 2 mechanical lint enforce per ADR-060 §결정 5 default warning mode, 1-K↔1-N pattern 답습).

| # | Carrier | Wave 2 wire pattern |
|---|---|---|
| 1 | CFP-1647 carrier (Issue #1647 HIGH FU-A) | sub-scope 1-O Amd 26 CFP-1637 Wave 1 declaration-only behavioral mandate 의 mechanical enforcement 부재 영역 — current Wave 2 mechanical wire (CFP-1612 wired Python SSOT `scripts/lib/check_numeric_claim_write_time.py`) 의 scope expansion to PR commit msg + PR body detection layer + workflow PR open + sync trigger 추가 + bats fixture (PR commit msg + PR body fixture pair RED→GREEN stash proof per §결정 11.A). Wave 1 → Wave 2 split precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589/1612/1637 13번째 instance (CFP-1612 = 11th + CFP-1637 = 12th + 본 CFP-1647 = 13th sequential lineage extension). |

### sub-scope 1-P axis 정합

본 Amendment 27 = sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K/1-L/1-M/1-N/1-O) precedent 답습 (closed-set ratchet 강화). 본 Amendment 27 = sub-scope (1-P) append.

> sub-scope 1-P = **1-O declaration-only behavioral mandate 의 Wave 2 mechanical enforcement wire SSOT axis** 신설 — sub-scope 1-O (Amendment 26, CFP-1637) 의 4-step verify-before-write 의무 + 6 numeric claim closed-set dimension declaration mandate (PR commit msg + PR body layer scope) 를 Python SSOT scope expansion + workflow PR trigger + bats fixture 로 mechanical enforce. declaration → mechanical enforce 의 promotion path codify (1-K↔1-N pair pattern 답습 — 본 1-O↔1-P pair).

#### 1-P 4-tuple primitive — sub-scope 1-O Wave 2 mechanical wire scope

Wave 2 mechanical wire 영역 4 의무 (Phase 2 sub-carrier — DeveloperPL + QADev spawn 시):

1. **lint script SSOT scope 확장 (Python per ADR-061 multi-line Python convention)** — `scripts/lib/check_numeric_claim_write_time.py` Python SSOT (CFP-1612 wired, governance docs scope 활성) detection scope 확장 to **PR commit message body + PR description body layer**. current scope = Story file + Change Plan governance docs in-tree; 본 1-P scope 확장 = PR-level artifact source ingestion 추가:
   - PR commit message body inspection: `git log --format=%B <range>` subprocess primitive 또는 `gh pr view --json commits` (commit message body retrieval)
   - PR description body inspection: `gh pr view --json title,body` subprocess primitive
   - `--scope pr-commit-msg` + `--scope pr-body` flag 추가 (or unified `--scope all` default — Phase 2 mechanical wire design 시 결정)
   - `scripts/check-numeric-claim-write-time-verify.sh` bash thin wrapper scope flag passthrough
2. **6 dimension detection logic 재사용 (Python dict SSOT 재사용)** — 1-K + 1-N + 1-O + 1-P 동일 6 numeric closed-set dimension (line count / file count / API count / pattern_count / commit count / row count) Python dict SSOT regex+source command pattern map 재사용. PR-level artifact layer detection regex = governance docs regex 와 universal (예: `\d+\s*(commits?|files?|lines?|LOC)`, dimension dispatch 동일). 신규 dimension 신설 0건 (scope expansion only).
3. **PR-level source ingestion + FP guard 재사용** — workflow trigger 확장 (PR open + sync event 추가) + `gh pr view --json title,body,commits` source ingestion + FP guard 4종 재사용 (code-span EXEMPT + quoted-text EXEMPT + templates/** EXEMPT + docs/stories/§9 transcript EXEMPT — PR commit msg + PR body 영역 inspection 시에도 동일 FP guard 적용). PER_BLOCK_SCAN_CAP=50 line CodeQL ReDoS guard 재사용 (Python SSOT 안 동일 guard, nested quantifier regex 절대 금지).
4. **workflow + bypass + evidence-checks-registry binding 갱신** — `templates/github-workflows/numeric-claim-write-time-verify.yml` workflow trigger 확장 (현재 `on: pull_request` 가 governance docs 변경 시만 발동 → PR open + sync 모두 발동 + commit message body / PR body inspection job step 추가) + `.github/workflows/numeric-claim-write-time-verify.yml` byte-identical mirror per ADR-005 + 기존 `continue-on-error: true` warning tier 유지 + 기존 `hotfix-bypass:numeric-claim-write-time-verify` bypass label per ADR-024 Amendment 6/8 §결정 6.A 재사용 (bypass label 신설 0건 — scope expansion only, hotfix-bypass:* family count 변경 0) + evidence-checks-registry entry `numeric-claim-write-time-verify` target_section 갱신 (`§결정 1 layer 1 sub-scope (1-K + 1-N + 1-O + 1-P)` 4 sub-scope 정합) + label-registry MINOR bump 0건 (bypass label 재사용).

#### 1-P disjoint axis cross-ref

- **Amd 22 §결정 1-K (numeric claim write-time strict claim mandate, CFP-1601 — governance docs scope declaration)**: declaration-only behavioral mandate SSOT (4-step verify-before-write + 6 numeric closed-set dimension enum) governance docs scope. 본 Amendment 27 = 1-O Wave 2 mechanical enforcement wire SSOT PR-level artifact scope. 1-K = declaration / governance docs / 본 1-P = enforce / PR-level artifact axis 인접 layered + scope target disjoint.
- **Amd 25 §결정 1-N (numeric claim write-time verify Wave 2 mechanical enforcement wire, CFP-1612 — governance docs scope wire)**: mechanism = mechanical lint enforce SSOT for 1-K (governance docs scope). 본 1-P = 같은 mechanism axis (mechanical lint enforce) for 1-O (PR-level artifact scope). 1-N + 1-P = paired Wave 2 wire (governance docs / PR-level artifact disjoint complement).
- **Amd 26 §결정 1-O (PR commit msg + PR body numeric claim write-time strict claim mandate declaration, CFP-1637)**: declaration-only behavioral mandate SSOT PR-level artifact scope (1-K 의 scope 확장 — 3rd axis disjoint from governance docs scope). 본 1-P = 1-O 의 Wave 2 mechanical enforcement wire SSOT (declaration → enforce promotion path layered). 1-O = declaration axis / 본 1-P = enforce axis disjoint complement layered (1-K ↔ 1-N pair pattern 답습).
- **Amd 17 §결정 1-G (amendment-slot pre-reservation strict claim, CFP-1435)**: amendment-slot reservation lifecycle strict claim axis. 본 1-P = mechanical lint enforcement axis (행위 = lint script scope expansion + workflow trigger 확장 + bats fixture). 1-G 와 axis disjoint (reservation slot lifecycle vs PR-level numeric claim mechanical enforce).
- **Amd 23 §결정 1-L (spawn prompt fact verify upstream-inherited stale fact super-class, CFP-1590)**: spawn prompt content 안 인용 fact 의 upstream-inherited fact verify axis (4 sub-source). 본 1-P = own-author PR-level artifact write-time numeric claim mechanical enforce (1-O Wave 2 wire). 1-L = upstream input fact verify (synthesis input 측) / 1-K + 1-N + 1-O + 1-P = own-author output numeric value verify (write-time output, governance docs + PR-level artifact 양 scope). 1-L + (1-K + 1-N + 1-O + 1-P) = input-output paired axis disjoint complement.
- **Amd 24 §결정 1-M (own-author synthesis 보고 vs actual git commit gap, CFP-1589)**: own-author synthesis output ↔ actual artifact (git commit) gap verify axis (artifact identity claim 영역). 본 1-P = numeric claim value within commit message body + PR body mechanical enforce (6 dimension numeric value verify, axis disjoint from artifact identity gap). 1-M = artifact identity gap verify / 본 1-P = numeric value within artifact mechanical enforce (axis 인접하나 verify 대상 disjoint — artifact existence vs numeric content within artifact mechanical enforce).

#### 1-K + 1-N + 1-O + 1-P 4-quadrant matrix

| Axis | Governance docs scope | PR-level artifact scope |
|---|---|---|
| **Declaration (Wave 1)** | 1-K (Amd 22, CFP-1601) — 4-step verify-before-write + 6 dimension closed-set behavioral mandate | 1-O (Amd 26, CFP-1637) — same mandate inherit, scope expansion to PR commit msg + PR body |
| **Mechanical wire (Wave 2)** | 1-N (Amd 25, CFP-1612) — Python SSOT `check_numeric_claim_write_time.py` governance docs scope wired + workflow + bats + evidence-checks-registry warning-tier initial registration + label-registry MINOR | 1-P (본 Amd 27, CFP-1647) — Python SSOT scope expansion to PR commit msg + PR body detection layer + workflow PR open + sync trigger 추가 + bats fixture PR commit msg + PR body fixture pair + evidence-checks-registry entry target_section 갱신 (label-registry MINOR 0건, bypass label 재사용) |

4-quadrant matrix codify (governance docs / PR-level artifact × declaration / Wave 2 wire). axis 분리 명확 + super-class 안 closed-set ratchet 강화 (15 → 16 sub-scope, axis disjoint 영역 누적).

#### Wave 1 (declarative) ↔ Wave 2 (mechanical) split rationale

**Wave 1 = 본 Amendment 27 declarative SSOT** (Phase 1 PR — 본 carrier):
- ADR-082 §결정 1 layer 1 sub-scope 1-P append (본 §)
- `mechanical_enforcement_actions[]` entry `numeric-claim-write-time-verify` target_section 갱신 (1-K + 1-N + 1-O + 1-P 4 sub-scope 정합) + status 갱신 (Wave 2 PR-level artifact scope expansion declarative anchor)
- `docs/adr/ADR-RESERVATION.md` amendments_reserved[] row 27 pre-append (adr_number 82 amendment_id 27 reserved_by_cfp CFP-1647 status active)
- Story file (`stories/CFP-1647.md`) + Change Plan (`change-plans/cfp-1647-adr082-amd-27-1p.md`) in codeforge-internal-docs
- `CHANGELOG.md` `[Unreleased]` Added entry append (declaration-only — script/workflow/bats wire 0건)

**Wave 2 = actual mechanical wire** (Phase 2 PR 별도 sub-carrier — DeveloperPL + QADev spawn):
- `scripts/lib/check_numeric_claim_write_time.py` Python SSOT scope expansion to PR commit msg + PR body detection layer (current Python SSOT 의 6 dimension detection logic 재사용 + commit message + PR body 영역 wiretap subprocess primitive 추가)
- `scripts/check-numeric-claim-write-time-verify.sh` bash thin wrapper scope flag passthrough (`--scope pr-commit-msg` + `--scope pr-body` flag 또는 unified `--scope all` default)
- `templates/github-workflows/numeric-claim-write-time-verify.yml` workflow trigger 확장 (PR open + sync event 추가) + `.github/workflows/` byte-identical mirror per ADR-005
- `tests/scripts/check-numeric-claim-write-time-verify/test_*.bats` fixture 추가 (PR commit msg fixture + PR body fixture pair RED→GREEN stash proof per §결정 11.A)
- `docs/evidence-checks-registry.yaml` entry `numeric-claim-write-time-verify` target_section 갱신 (`§결정 1 layer 1 sub-scope (1-K + 1-N + 1-O + 1-P)` 4 sub-scope 정합)

precedent: CFP-1437 (1-E pre-spawn pin) → Wave 2 CFP-1489 / CFP-1436 (1-F mid-spawn drift) → Wave 2 CFP-1500 / CFP-1435 (1-G slot reservation) → Wave 2 CFP-1497 / CFP-FU-A Amd 19 (1-I pre-spawn-prompt-finalize) → Wave 2 CFP-1502 / CFP-1559 (1-O Issue body stale-claim super-class) → Wave 2 별도 sub-carrier / CFP-1578 (1-J cross-repo worktree target authority) → Wave 2 별도 sub-carrier / CFP-1601 (1-K numeric claim mandate) → Wave 2 CFP-1612 (1-N) / CFP-1590 (1-L spawn prompt fact) → Wave 2 별도 sub-carrier / CFP-1589 (1-M synthesis vs commit gap) → Wave 2 별도 sub-carrier / CFP-1637 (1-O PR-level artifact declaration) → Wave 2 본 CFP-1647 (1-P) = 13번째 Wave 1→Wave 2 split instance.

#### Wave 3 escalation path

pattern_count ≥ N 추가 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리 (ADR-060 §결정 6 promotion gate AND 3/3 — (a) PR 누적 ≥ 20 + (b) bypass 외 failure = 0 + (c) sibling Story merged). 본 1-O + 1-P evidence base = Pattern 2 meta-self-application-accuracy-violation pattern_count 2 reach (1-O 와 동일 evidence inherit — CFP-1601 §13.C row 3 Story scope 11 vs 15 + CFP-1612 PR #1631 commit msg LOC drift 29/~470/~155 vs 30/605/183 = Wave 1+2 declaration→enforce 정합 Mandatory ADR-045 §D-9 escalation 산물). Wave 2 mechanical enforce 후 sentinel pattern_count 추가 누적 시 Wave 3 escalation 별 carrier 발의.

#### Option A vs B 결정 rationale (ArchitectAgent chief author 자율)

- **Option A (새 ADR-NNN 신설)**: 새 ADR `ADR-NNN-pr-commit-body-numeric-claim-wave2-wire` 신설 — Wave 2 mechanical enforcement wire 영역 separate ADR for PR-level artifact scope. **REJECT 사유**: super-class fragmentation 위험 (Wave 1 declaration mandate Amd 26 CFP-1637 이 ADR-082 §결정 1 sub-scope 1-O 안 codify 됨 — Wave 2 wire 도 동일 super-class 안 sub-scope 1-P 으로 axis 정합, 1-K↔1-N pair pattern 답습). Amd 26 1-O mandate ↔ Amd 27 1-P Wave 2 wire = 동일 axis 안 declaration → mechanical enforce promotion path layered, separate ADR fragmentation 회피.
- **Option B (ADR-082 Amendment 27 sub-scope 1-P append, Wave 1 declarative SSOT + Wave 2 mechanical wire 별도 sub-carrier)** — **채택**: super-class 안 sub-scope (1-P) Wave 2 wire SSOT codify (1-O Wave 1 mandate 의 Wave 2 enforce wire). axis 정합 명확 (declaration mandate ↔ mechanical enforcement scope disjoint complement layered axis, 1-K↔1-N pair pattern 답습). Wave 1 → Wave 2 split precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589/1612/1637 13번째 instance 답습. ratchet 강화 방향 (declarative → mechanical enforce, 15 → 16 sub-scope).

#### Amendment 27 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 27 scope = 본문 §결정 1-13 + sub-scope 1-P 신설 + Amendment 1-26 강화 방향 only (sub-scope ratchet 강화 + 1-O declaration-only → 1-P Wave 2 mechanical enforce wire promotion path PR-level artifact scope). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합 (CFP-1149 Amendment 8 symmetric evidence-gated 정합). META-self-applied (§결정 10.D 22nd applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 8th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590 + Amd 24 CFP-1589 + Amd 25 CFP-1612 + Amd 26 CFP-1637 + 본 carrier + Amendment 22 §결정 1-K 3rd applied for Wave 2 wire carrier PR-level artifact scope + Amendment 23 §결정 1-L 2nd applied case for spawn packet fact verify + Amendment 24 §결정 1-M 1st applied case for inline self-verify recursive dogfooding).

#### META 22nd applied case verbatim record

본 Amendment 27 자체가 META-self-applied (§결정 10.D 22nd applied case). source command + actual + cross-verify 본문 박제:

- **Source command identify (Step 1)**: `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-write-time-self-write-verification-mandate.md | tail -1` (sequential max amendment_id slot, line-grep occurrence count 아님 — 1-K Step 1 source command precision rule 적용, frontmatter `amendments[]` block scope 한정)
- **Direct execute (Step 2)**: ArchitectAgent Phase 1 spawn 시점 직접 실행 (origin/main HEAD `e1e2b751` post-CFP-1637 Amd 26 merge fresh fetch 후 clean state)
- **Actual output (Step 2 result)**: `  - amendment_id: 26` (Amd 26 CFP-1637 점유, post-merge HEAD origin/main = `e1e2b7514b9ce2f7afe884734b66152952ac2291`)
- **Cross-verify (Step 3)**: claim "next-slot = 27" ↔ actual `amendment_id: 26` (Amd 26 점유) → next-slot = 27 match `[verified]`. 정확 next-slot for CFP-1647 = **27** + sub-scope letter = **1-P** (1-O=CFP-1637 Amd 26 다음 sequential)
- **Write (Step 4)**: match 후 write — 본 Amendment 27 + sub-scope 1-P codify (frontmatter `amendments[]` row 27 append + frontmatter `amendment_log[]` row 27 append + 본 body section append + ADR-RESERVATION row 27 append + Story file + Change Plan + CHANGELOG entry)

META 22nd applied case = pre-write source command direct verify + claim ↔ actual match 후 write only (write-after-claim 아닌 verify-then-write 강제). META 21st = CFP-1637 Amd 26 (sub-scope 1-O PR-level artifact declaration carrier 자체 안 numeric claim verify) 직후 sequential carrier. 본 Amendment 27 = (a) 1-K numeric claim verify 3rd applied (Wave 2 wire carrier PR-level artifact scope) + (b) 1-L spawn prompt fact verify 2nd applied (spawn packet 안 amendments[] max=26 claim verify) + (c) 1-M synthesis vs commit gap 1st applied case (inline self-verify, frontmatter dual-block parity 의무 enforce — amendments[] AND amendment_log[] 둘 다 entry append) + (d) 1-G strict pre-reservation claim mandate 8th applied (ADR-RESERVATION row pre-append precedent 답습) = 4-sub-scope paired META applied case (recursive dogfooding 완결).

#### Related (Amendment 27 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row pre-append (adr_number 82 amendment_id 27 reserved_by_cfp CFP-1647 reservation_date 2026-05-26 KST status active) — Amendment 17 sub-scope 1-G META 8th applied case (Amd 18 CFP-1342 1st + Amd 21 CFP-1578 2nd + Amd 22 CFP-1601 3rd + Amd 23 CFP-1590 4th + Amd 24 CFP-1589 5th + Amd 25 CFP-1612 6th + Amd 26 CFP-1637 7th precedent 답습)
- `mechanical_enforcement_actions[]` entry `numeric-claim-write-time-verify` — target_section 갱신 (`§결정 1 layer 1 sub-scope (1-K + 1-N + 1-O + 1-P)` 4 sub-scope 정합) + status 갱신 (Wave 2 PR-level artifact scope expansion declarative anchor; Phase 2 actual script + workflow + bats wire 별 sub-CFP carrier)
- Story file `c:/workspace/mclayer/codeforge-internal-docs/plugin-codeforge/stories/CFP-1647.md` (codeforge-internal-docs SSOT ADR-013 dogfood-out)
- Change Plan `c:/workspace/mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1647-adr082-amd-27-1p.md` (codeforge-internal-docs SSOT ADR-013 dogfood-out)
- `CHANGELOG.md` — [Unreleased] Added entry append ([CFP-1647] ADR-082 Amendment 27 sub-scope 1-P 신설 — sub-scope 1-O Wave 2 mechanical enforcement wire, declaration-only behavioral mandate 1-O 의 Wave 2 mechanical lint enforcement wire, declaration → mechanical enforce promotion path PR-level artifact scope)
- Wave 2 별 sub-CFP carrier (future): `scripts/lib/check_numeric_claim_write_time.py` Python SSOT scope expansion to PR commit msg + PR body detection layer + workflow PR open + sync trigger 추가 + bats fixture (PR commit msg + PR body fixture pair RED→GREEN stash proof per §결정 11.A) + evidence-checks-registry entry target_section 갱신 (label-registry MINOR 0건, bypass label 재사용)

## Amendment 28 — §결정 1 layer 1 sub-scope (1-Q) 신설 (ADR dual-block parity 3-invariant forward-prevention lint, CFP-1648, 2026-05-26 KST)

**Issue #1648 MEDIUM follow-up from CFP-1637 retro** — F-DR-001 P0 origin sentinel mechanical carrier. F-DR-001 P0 pattern: ADR Amendment N 이 frontmatter `amendment_log[]` entry 는 present 하나 body `## Amendment N` section 이 missing (CFP-1637 retro 발견 — Amendment 26 case). anchor_id = `adr_dual_block_parity_forward_prevention` / root_cause_class = `structural-parity-drift-lint`. ADR-082 §결정 1 layer 1 sub-scope 1-Q (disjoint from 1-A through 1-P — dual-block ADR structural parity axis, not numeric claim / not cross-repo state / not spawn prompt / not ownership / not synthesis gap / not Wave 2 wire).

### sub-scope 1-Q axis 정합

ADR dual-block parity 3-invariant check (ADR structural integrity layer, axis disjoint from 1-A/1-B/1-C/…/1-P):

- **Block 1** — `amendments[]` ↔ body `## Amendment N` H2 section parity: amendments[] 안 amendment_id N 에 대응하는 body section 존재 여부 verify
- **Block 2** — `amendment_log[]` ↔ body `## Amendment N` H2 section parity (**F-DR-001 P0 sentinel**): amendment_log[] 안 amendment_id N 에 대응하는 body section 존재 여부 verify (CFP-1637 retro origin)
- **Block 3** — `amendments[]` ↔ `amendment_log[]` cross-count parity: 두 frontmatter block 의 amendment_id set 일치 verify

### Implementation primitive

Python SSOT `scripts/lib/check_adr_dual_block_parity.py` (ADR-061 thin wrapper convention):

- anchored simple regex + line-by-line parse (CodeQL ReDoS guard, ADR-061 Amendment 3 §결정 11 정합 — no nested quantifier)
- PER_LANE_EVIDENCE_SCAN_CAP=30 line cap
- Windows cp949 stdout reconfigure (sys.stdout.reconfigure(encoding="utf-8"))
- BYPASS_ADR_DUAL_BLOCK_PARITY=1 env unconditional skip
- Test seam env vars: CFP1648_ADR_GLOB_MOCK, CFP1648_ADR_DIR_MOCK, CFP1648_MOCK_ENV
- Exit code: 0=PASS / 1=WARNING / 2=ENVIRONMENT_ERROR (ADR-060 §결정 15 3-tier)

bash thin wrapper `scripts/check-adr-dual-block-parity.sh`: POSIX dispatch only, delegates to Python SSOT.

D2 dual trigger workflow `templates/github-workflows/adr-dual-block-parity.yml` + `.github/workflows/` byte-identical mirror (ADR-005):

- pull_request trigger: paths: [docs/adr/**] — scans changed ADR files only (PR mode)
- workflow_dispatch trigger: full-scan mode (all ADR files)
- continue-on-error: true (warning tier, ADR-060 §결정 5 first introduction = warning mode)
- permissions: {} top-level deny-all + per-job least-privilege
- bypass: hotfix-bypass:adr-dual-block-parity label check

bats test suite `tests/scripts/check-adr-dual-block-parity/test_adr_dual_block_parity.bats` (8 TC):

- TC-1: PASS (full parity, exit 0)
- TC-2: WARNING amendments[] frontmatter only (exit 1, AMENDMENTS_FRONTMATTER_ONLY)
- TC-3: WARNING body only (exit 1, BODY_ONLY_NO_AMENDMENTS + BODY_ONLY_NO_LOG)
- TC-4: **F-DR-001 sentinel** — amendment_log frontmatter only (exit 1, AMENDMENT_LOG_FRONTMATTER_ONLY)
- TC-5: BYPASS env (exit 0 + "bypass invoked")
- TC-6: ENVIRONMENT_ERROR — Python SSOT missing (exit 2)
- TC-7: red_green_anchor — RED/GREEN behavioral contract (CFP-1334 §8.4)
- TC-8: platform_verified — Korean UTF-8 path, no UnicodeDecodeError

CFP-1334 §8.4 5 markers: `pre_impl_sha`, `git_stash_sequence`, `role_vocabulary`, `red_green_anchor`, `platform_verified`.

AC-6 genuine RED proved: stash/rename Python SSOT → TC-1 through TC-5 and TC-7 fail (exit 2 SSOT missing), TC-6 PASS (ENVIRONMENT_ERROR correctly detected). Restore → 8/8 GREEN.

### META self-application (F-DR-001 forward-prevention recursive dogfooding)

본 Amendment 28 자체가 F-DR-001 P0 sentinel forward-prevention 의 첫 META applied case:

- `amendments[]` entry: Amendment 28 row append (본 전)
- `amendment_log[]` entry: Amendment 28 row append (본 전, F-DR-001 P0 sentinel — amendment_log entry present 의무)
- body `## Amendment 28` section: 본 section (F-DR-001 P0 sentinel — body section present 의무)

3-block parity 동시 write = forward-prevention lint 가 자기 자신의 Amendment 에 recursive dogfooding integrity verify 첫 적용.

### Related (Amendment 28 동반)

- `scripts/check-adr-dual-block-parity.sh` + `scripts/lib/check_adr_dual_block_parity.py` — Phase 1+2 combined (no Wave split)
- `templates/github-workflows/adr-dual-block-parity.yml` + `.github/workflows/adr-dual-block-parity.yml` — D2 dual trigger
- `tests/scripts/check-adr-dual-block-parity/` — bats 8 TC + 4 fixtures
- `docs/evidence-checks-registry.yaml` — adr-dual-block-parity warning-tier entry
- `docs/inter-plugin-contracts/label-registry-v2.md` — v2.77 → v2.78, `hotfix-bypass:adr-dual-block-parity` 103번째 family member
- `docs/inter-plugin-contracts/MANIFEST.yaml` — label_registry version 갱신
- `CHANGELOG.md` — [Unreleased] Added entry append

## Amendment 29 — §결정 1 layer 1 sub-scope (1-R) 신설 mid-Story FIX-loop re-verification mandate (CFP-1683, 2026-05-26 KST)

### Context

CFP-1646 1st attempt Full lane process 진행 중 **3 parallel race events** 발생:
- FIX iter 1 (false premise) → iter 2 (3 findings) → iter 3 (ESCALATE_PACKET_INCOMPLETE)
- CFP-1657 took Amendment 16 § 6.A.8 slot during iter 1 → iter 2 window (wording-dictionary axis)
- CFP-1648 took v2.78 + 103rd family member slot during iter 2 → iter 3 window (adr-dual-block-parity axis)

Root cause = FIX-loop intra-Story window 안 **amendment slot + label-registry version + bypass family count 3-tuple 재verify 부재**. ArchitectPL re-engage prompt 가 origin/main fetch + 3-tuple recheck 없이 spawn → 기존 spawn prompt facts 답습.

ADR-082 §결정 1 layer 1 sub-scope 1-G (CFP-1435 Amendment 17) strict pre-reservation claim mandate = **Story 시작 시점** only cover. FIX-loop intra-Story window 영역 미cover.

ADR-045 §D-9 cumulative pattern_count Mandatory reach:
- `sister_session_race_in_design_lane` ≥ 5 (CFP-684 + CFP-698 + CFP-1041 + CFP-1591 + CFP-1646 3 sub-events)

### Amendment

#### §결정 1 layer 1 sub-scope 1-R: Mid-Story FIX-loop re-verification mandate

FIX iter ≥ 2 시점 ArchitectPL (또는 lane PL) re-engage 시 **3-tuple reslot calculus 재verify 의무**:

1. **amendment_id slot 재verify** — `git fetch origin main` + `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-N-*.md | tail -1` actual next-slot
2. **label-registry MINOR bump version 재verify** — `git show origin/main:docs/inter-plugin-contracts/label-registry-v2.md | head -10 | grep '^version:'` actual current version
3. **bypass family member raw count 재verify** — `git show origin/main:docs/inter-plugin-contracts/label-registry-v2.md | grep -c '^  - name: hotfix-bypass:'` actual current count

3-tuple delta detection 시 — slot collision 발생 → re-author with corrected facts (amendment_id + version + family count 모두 next-slot 정합).

#### Per-iter mid-spawn drift detection

ArchitectPL re-engage prompt 안 **3 field presence 의무**:
- `amendment_slot_revalidated: <actual_next_slot>`
- `registry_version_revalidated: <actual_current_version>`
- `bypass_count_revalidated: <actual_current_count>`

3 field 부재 시 lint warning (Wave 2 mechanical wire scope).

#### Wave 1 (Phase 1 PR scope — declarative, 본 Amendment)

- 본 ADR-082 Amendment 29 §결정 1 layer 1 sub-scope 1-R 신설
- label-registry-v2 v2.80 → v2.81 MINOR + `hotfix-bypass:fix-loop-reverify-mandate` 106번째 raw active concrete family member
- MANIFEST.yaml row sync
- evidence-checks-registry `fix-loop-reverify-mandate` warning-tier entry append (status `deferred-followup`)
- workflow Wave 1 declarative stub (`fix-loop-reverify-check.yml` templates + .github byte-identical pair)
- CHANGELOG entry

#### Wave 2 (Phase 2 PR scope — mechanical wire, future carrier)

- workflow body actual lint wire
- script `scripts/check-fix-loop-reverify.sh` thin-wrapper (ADR-061)
- script `scripts/lib/check_fix_loop_reverify.py` (ADR-061 multi-line Python external)
- bats fixture RED→GREEN stash proof (CFP-1334)
- boundary fixture pair (3-field presence PASS + 3-field absent FAIL, CFP-963 Codex TP#4)

### Axis disjoint

- §결정 1 sub-scope 1-G (Amendment 17 CFP-1435) — Story 시작 시점 pre-reservation strict claim
- §결정 1 sub-scope 1-R (본 Amendment 29) — FIX-loop intra-Story window re-verification
- Axis 분리 — Story-start ↔ intra-Story FIX-loop 시점

### Related

- CFP-1683 carrier Story
- CFP-1646 retro F2 origin (3 parallel race events direct evidence)
- ADR-082 §결정 1 sub-scope 1-G (CFP-1435 Amendment 17, sibling axis disjoint)
- ADR-085 §결정 1 multi-session collaboration protocol
- ADR-073 Amendment 6 sibling_story_handoff

## Amendment 30 — §결정 1 layer 1 sub-scope (1-S) 신설 (ADR frontmatter block convention SSOT + sub-scope 1-Q single-block 면제 scope clarification, CFP-1688, 2026-05-26 KST)

### Context

**Issue #1688 MEDIUM follow-up (CFP-FU-C from CFP-1680 retro Pivot 1 root cause)** — sub-scope 1-Q (CFP-1648 dual-block parity lint, Amendment 28) 가 **single-block ADR 에 대해 false-positive** 한다. ADR-045 에 대해 lint 직접 실행으로 확인:

- **ADR-045 frontmatter**: `amendment_log:` block ONLY — `amendments:` block 부재 (single-block convention). verified: `grep -cE "^amendments:" ADR-045 = 0`, `grep -cE "^amendment_log:" = 1`.
- **ADR-045 body**: `### Amendment N` (H3) heading 사용 (예: `### Amendment 5 — §D-9 신설`) + `#### §D-N` sub-section. 기존 lint `BODY_H2_AMENDMENT_PATTERN` 은 `## Amendment N` (H2) 만 match.
- **결과**: body_ids empty (H3 미detect) → 11 ADR-045 amendments 전부 `AMENDMENT_LOG_FRONTMATTER_ONLY` false-positive ("body ## Amendment N section missing"). Block 3 (`CROSS_BLOCK_COUNT_MISMATCH`) 도 동시 fire (amendments[]=0 != amendment_log[]=N).
- warning-tier (`continue-on-error: true`) 이므로 non-blocking 이나, 모든 PR 의 check output 을 false warning 으로 오염.

**bug #3 — frontmatter scan cap (Orchestrator verify-before-trust, ADR-073/ADR-082 direct extraction)**: `_extract_frontmatter_lines()` 가 frontmatter scan 을 `lines[:PER_LANE_EVIDENCE_SCAN_CAP * 10]` = **300 line** 으로 cap 한다. ADR-082 자신의 frontmatter 가 300 line 초과 (amendments[] + amendment_log[] verbose multi-line entry 가 2nd `---` delimiter line 548 까지 진행, related_stories: line 359) → extractor 가 2nd `---` 에 도달하기 전 silent 절단 → amendment_log[] entry 22-29 (line 305-347, 전부 300 초과) DROP. verified: origin/main `_extract_amendment_log_ids` returns max=22 (entry 23-29 DROP) / Amendment 30 edit 후 max=21 (entry 22 추가 DROP). 결과 = false `CROSS_BLOCK_COUNT_MISMATCH: amendments[] count 30 != amendment_log[] count 20` + false `BODY_ONLY_NO_LOG: Amendment 30` (30 은 amendment_log[] line 353 에 존재하나 cap 너머). loop 자체는 2nd `---` 에서 `break` (line 136-137) 하므로 block scan 은 정상 — 300-line slice cap 이 유일 원인 (redundant runaway protection mis-fire).

**triple schema heterogeneity** root cause: (1) single-block (amendment_log[] only) vs dual-block (both) + (2) body heading H3 (`###`) vs H2 (`##`) + (3) frontmatter scan cap (300 line) 가 long-frontmatter ADR (ADR-082 자신) 의 amendment_log[] 절단. 세 bug 모두 동일 class — **lint 가 real ADR convention 을 정확히 read 못함** (parser-correctness false-positive).

anchor_id = `adr_frontmatter_block_convention_single_block_exemption` / root_cause_class = `lint-scope-overbroad-single-block-fp`. ADR-082 §결정 1 layer 1 sub-scope 1-S (disjoint from 1-A through 1-R — ADR structural-parity-lint scope correction axis, 1-Q sub-domain refinement, not a new verify subject).

### Amendment

#### §결정 1 layer 1 sub-scope 1-S: ADR frontmatter block convention SSOT + 1-Q single-block 면제 scope clarification

**(1) ADR frontmatter block convention SSOT (2 valid conventions 명문화)**:

| convention | frontmatter blocks | body heading | exemplar |
|---|---|---|---|
| **single-block** | `amendment_log[]` only (no `amendments[]`) | `### Amendment N` (H3) 또는 `## Amendment N` (H2) | ADR-045 |
| **dual-block** | `amendments[]` + `amendment_log[]` 둘 다 | `## Amendment N` (H2) | ADR-082 (본 ADR) |

두 convention 모두 valid. **migration / standardization 강제 안 함** (retroactive 전면 변경은 risk 큼 — 기존 ADR frontmatter 변조 금지 invariant 정합). lint 가 두 convention 을 모두 지원한다.

**(2) sub-scope 1-Q (CFP-1648 lint) scope correction (3 fix, 동일 false-positive class)**:

- **Fix A — single-block mode**: `amendments:` block 부재 + `amendment_log:` block present 시 single-block mode 진입 → **Block 1** (amendments[] ↔ body) + **Block 3** (amendments[] ↔ amendment_log[] cross-count) **skip**, **Block 2** (amendment_log[] ↔ body parity, **F-DR-001 P0 sentinel**) **만 적용**. (single-block ADR 도 amendment_log[] ↔ body parity 는 계속 enforce — F-DR-001 P0 보호 무약화.)
- **Fix B — body heading both-level detection**: body amendment section 을 `## Amendment N` (H2) **AND** `### Amendment N` (H3) 둘 다 detect (H3 추가). ReDoS guard (ADR-061 Amendment 3 §결정 11) 정합 — anchored simple regex, no nested quantifier (예: `^#{2,3}\s+Amendment\s+([0-9]+)` — bounded `{2,3}` 가 H4 `####` 차단, 또는 H2/H3 2 pattern 분리).
- **Fix C — frontmatter scan cap (NEW, Orchestrator verify-before-trust 발견)**: `_extract_frontmatter_lines()` 의 `lines[:PER_LANE_EVIDENCE_SCAN_CAP * 10]` (300 line) slice 가 long-frontmatter ADR (ADR-082 자신, frontmatter 2nd `---` = line 548) 의 amendment_log[] 절단. fix = frontmatter delimiter 탐색 slice cap 제거 — frontmatter 는 이미 `---` delimiter 로 bounded 이므로 2nd `---` 까지 scan + 넉넉한 safety cap (예: 5000 line) 으로 runaway protection retain. correctness fix (ReDoS-relevant regex 변경 아님 — backtracking pattern 무관, slice 상한값 확대만).

**lint scope correction = 신규 check 아닌 sub-scope 1-Q scope 정정** — 기존 `adr-dual-block-parity` evidence-checks-registry entry + `hotfix-bypass:adr-dual-block-parity` label 재사용. 신규 evidence-checks-registry entry 0 / 신규 label 0 / label-registry MINOR bump 0.

#### Wave 분배 (Combined Phase 1+2 — CFP-1648 combined precedent 답습)

- **Phase 1 (본 ADR Amendment 30, design lane)**: §결정 1 layer 1 sub-scope 1-S 신설 + ADR frontmatter block convention SSOT codify + Change Plan §8 Test Contract (lint fix spec — Fix A/B/C).
- **Phase 2 (develop lane dispatch — Change Plan §8 SSOT)**: `scripts/lib/check_adr_dual_block_parity.py` lint fix (Fix A single-block mode + Fix B H2/H3 body detection + Fix C frontmatter scan cap) + bats 신규 TC (single-block PASS / single-block missing-body WARNING / dual-block 무변경 / H3 detection / H4 guard / **long-frontmatter >300 line high-numbered amendment_log entry 추출**) + 기존 4 fixture + single-block/H3/long-frontmatter fixture 추가.

### Axis disjoint

- §결정 1 sub-scope 1-Q (Amendment 28 CFP-1648) — dual-block parity 3-invariant forward-prevention lint (lint **신설**)
- §결정 1 sub-scope 1-S (본 Amendment 30 CFP-1688) — 1-Q lint single-block ADR 면제 + body H2/H3 both-level + frontmatter scan cap (Fix A/B/C) **scope correction** (lint 신설 아닌 scope 정정)
- Axis 분리 — lint 신설 (1-Q) ↔ lint scope correction / false-positive 차단 (1-S). 1-S 는 1-Q sub-domain refinement (verify subject 동일 = ADR dual-block structural parity, 적용 scope 만 정정).

### META self-application (recursive dogfooding — dual-block exemplar, Fix C 가 enabler)

본 Amendment 30 = ADR-082 의 **dual-block convention exemplar** 이며, 1-S 가 clarify 하는 lint 가 본 ADR-082 자신의 dual-block structure 위에서 false-positive 없이 PASS 해야 한다 (recursive dogfooding integrity verify):

- `amendments[]` entry: Amendment 30 row append (max=29 → next-slot=30 verified)
- `amendment_log[]` entry: Amendment 30 row append (F-DR-001 P0 sentinel — amendment_log entry present 의무, file line 353)
- body `## Amendment 30` section: 본 section (H2 — dual-block convention 정합)

**3-block parity authoring 은 정확** (3 block 전부 amendment_id 30 보유, file 상 검증 완료). 단 **bug #3 (frontmatter scan cap 300) 가 unfixed 인 현 상태에서는 lint 가 ADR-082 의 amendment_log[] line 353 을 see 하지 못해 false `BODY_ONLY_NO_LOG: Amendment 30` 산출** — 즉 recursive dogfooding PASS 는 **Fix C 가 enabler** (Fix C 적용 후에야 lint 가 full frontmatter 를 읽어 Amendment 30 parity 를 정확히 PASS). 이것이 Fix C 를 CFP-1688 scope 에 포함하는 직접 근거 — 본 Amendment 의 META self-application 자체가 Fix C 없이는 성립 불가. dual-block ADR-082 는 single-block mode 미진입 (amendments[] present) → 3-block 전부 검증 path. (META self-application — §결정 10.D 13th applied case). Amendment 17 §결정 1-G strict pre-reservation 6th applied case (ADR-RESERVATION row pre-append + commit dad73ec5, `pre_reservation_verified: true`).

### Genuine drift (out of scope — Fix C 적용 후 정당 surface)

Fix C 적용 후 lint 가 full frontmatter 를 읽으면, ADR-082 의 **body §Amendment 8-13 / 18-21 section 부재** 가 genuine drift WARNING 으로 정당 surface 한다 (해당 amendment 들은 frontmatter-only — body `## Amendment N` section 미작성). 이는 Fix C 가 의도대로 동작하는 **legitimate warning** 이며 CFP-1688 scope 외. body section backfill (또는 accept-as-historical 결정) = 별도 follow-up CFP. parser-correctness bug (Fix A/B/C, in-scope) ↔ genuine body-section drift (out-of-scope) 의 명확 분리.

### Related

- CFP-1688 carrier Story
- CFP-1680 retro Pivot 1 origin (sub-scope 1-Q lint false-positive on single-block ADR-045 root cause)
- CFP-1648 sibling (sub-scope 1-Q lint origin Amendment 28, dual-carrier naming SSOT `adr-dual-block-parity`)
- ADR-045 — single-block convention exemplar (amendment_log[] only + H3 body)
- ADR-082 (본 ADR) — dual-block convention exemplar (amendments[] + amendment_log[] + H2 body) + long-frontmatter (>300 line) Fix C 직접 sentinel
- ADR-073 / ADR-082 — Orchestrator verify-before-trust (Fix C 발견 채널 — FIX 직접 lint 실행 + extraction 검증)
- ADR-061 Amendment 3 §결정 11 — CodeQL ReDoS guard (Phase 2 lint fix regex anchored simple, no nested quantifier — Fix C 는 slice cap 확대로 ReDoS 무관)
- ADR-054 §결정 1 — doc-only fast-path 비적격 (lint fix = scripts/tests 변경 동반, Combined Phase 1+2)
- `scripts/lib/check_adr_dual_block_parity.py` — Phase 2 lint fix target (Fix A single-block mode + Fix B H2/H3 detection + Fix C frontmatter scan cap)
- `tests/scripts/check-adr-dual-block-parity/` — Phase 2 bats 신규 TC + fixture (single-block / H3 / H4 guard / long-frontmatter) 추가 target
## Amendment 31 — §결정 1 layer 1 sub-scope (1-T) 신설 PMOAgent retro write-time verify-before-trust mandate (CFP-1684, 2026-05-26 KST, META recursive evidence carrier — CFP-1688 Amendment 30 + sub-scope 1-S slot collision reslot)

### Context

CFP-1646 PMOAgent retro write-time 자체 `stale_fact_inheritance` 진입 — **META recursive evidence**:
- Story spec 본문 안 wrapper merge commit SHA claim `e84f0460` (Phase 1 commit) vs actual `00641695` (merge commit)
- internal-docs SHA claim `0b37a71` (Phase 1 commit) vs actual `33fff4cf` (merge commit)

즉 verify-before-trust mandate 를 codify 하는 retro 자체가 write-time verify gap 노출. PMOAgent retro write-time fact verify 부재 영역.

ADR-082 §결정 9 verify-at-write-time (CFP-1312 Amendment 7) = ArchitectAgent + Orchestrator scope. PMOAgent retro write scope 미cover.

### Amendment

#### §결정 1 layer 1 sub-scope 1-S: PMOAgent retro write-time verify-before-trust mandate

PMOAgent retro file write 시 cited fact source direct verify 의무:
- **commit SHA** — `gh pr view <PR#> --json mergeCommit` 또는 `git log` direct verify (Phase 1 commit SHA vs merge commit SHA disambiguation)
- **label-registry version** — `git show origin/main:docs/inter-plugin-contracts/label-registry-v2.md | grep '^version:'` direct verify
- **bypass family count** — `grep -c '^  - name: hotfix-bypass:'` direct verify
- **cross-Story memory pattern_count** — source memory entries direct cross-ref

#### Wave 1 (Phase 1 PR scope — declarative, 본 Amendment)

- 본 ADR-082 Amendment 30 §결정 1 sub-scope 1-S 신설
- label-registry-v2 v2.81 → v2.82 MINOR + `hotfix-bypass:retro-fact-verify-mandate` 107번째 family member
- MANIFEST.yaml row sync + evidence-checks-registry `retro-fact-verify-mandate` warning-tier entry
- workflow Wave 1 stub pair (ADR-005) + CHANGELOG entry

#### Wave 2 (Phase 2 PR scope — mechanical wire, future carrier)

- script `scripts/check-retro-fact-verify.sh` (ADR-061) + `scripts/lib/check_retro_fact_verify.py`
- retro file 안 SHA pattern + version pattern presence-grep + corresponding `gh api` / `git log` verify trace presence
- bats RED→GREEN stash proof (CFP-1334) + boundary fixture pair (CFP-963 Codex TP#4)

### Axis disjoint

- §결정 9 (CFP-1312 Amendment 7) — ArchitectAgent + Orchestrator write-time verify scope
- §결정 1 sub-scope 1-S (본 Amendment 30) — PMOAgent retro write scope

### META self-application

본 Amendment 30 자체가 retro write-time verify mandate carrier — ADR-082 Amendment 28 dual-block parity (amendments[] + amendment_log[] + body 3-block dual-write) self-apply. recursive dogfooding: retro write-time verify 를 codify 하면서 본 ADR Amendment 자체가 dual-block parity verify 적용.

### Related

- CFP-1684 carrier Story (META recursive evidence)
- CFP-1646 retro F3 origin (PMOAgent retro write-time 2 commit SHA claim mismatch direct evidence)
- ADR-082 §결정 9 verify-at-write-time (CFP-1312 Amendment 7, sibling axis disjoint)
- ADR-073 Amendment 2 transition trigger `session_start` cold start verify

## Amendment 32 — §결정 1 layer 1 sub-scope (1-U) 신설 (dual-block gate — 1-Q lint scope 를 dual-block-only ADR 로 narrow, 1-S Fix A supersede, CFP-1734, 2026-05-26 KST)

### Context

**Issue #1734 (CFP-FU from CFP-1688) + user Option A 결정 (2026-05-26 KST)** — sub-scope 1-Q (CFP-1648 dual-block parity lint, Amendment 28) + sub-scope 1-S (CFP-1688 single-block mode Fix A, Amendment 30) 가 real ADR convention diversity 와 **fundamentally mismatched**. Orchestrator verify-before-trust 직접 ADR census 결과:

- **82 ADR** 이 frontmatter `amendments[]` 또는 `amendment_log[]` block 보유. lint 의 body detection (`## Amendment N` / `### Amendment N` H2/H3, CFP-1688 Fix B 후) 이 match 하는 ADR 은 **39개뿐**.
- **35 ADR** 은 THIRD body convention 사용 — lint 가 못 봄: `## §결정 N. <title> (Amendment M, CFP-XXX)` (§결정 heading 안 괄호 안 amendment 번호). 예: ADR-071 `## §결정 12. DialogFidelityAgent external verifier auxiliary layer (Amendment 1, CFP-777)`. 이들은 valid convention 이나 `BODY_AMENDMENT_PATTERN` (`^#{2,3}\s+Amendment\s+([0-9]+)`) 에 match 안 됨.
- CFP-1688 Fix A 가 single-block mode (amendment_log[]-only → Block 2 만) 를 추가했는데, 이를 amendments[]-only 로 symmetric 확장하면 이 parens-convention 35 ADR 에 FP 발생 (body_ids empty → `AMENDMENTS_FRONTMATTER_ONLY` 전부 fire).

**User decision (Option A)**: lint 을 **dual-block ADR (amendments[] AND amendment_log[] 둘 다 present, ADR-082 처럼) 에만** 적용하도록 narrow. single-block (양방향) / amendments[]-only / parens-convention / no-amendments → 면제 (trivial PASS). 이는 lint 의 original F-DR-001 intent (dual-block ADR-082 consistency, Amendment 26 case origin) 와 정합하며 convention-mismatch false-positive 를 깨끗이 제거.

anchor_id = `adr_dual_block_gate_narrow` / root_cause_class = `lint-scope-overbroad-convention-diversity-fp`. ADR-082 §결정 1 layer 1 sub-scope 1-U (disjoint from 1-A through 1-S — ADR structural-parity-lint scope refinement axis, 1-S Fix A supersede sub-refinement, 1-Q sub-domain 의 second narrow — not a new verify subject).

### Amendment

#### §결정 1 layer 1 sub-scope 1-U: dual-block gate — 1-Q lint scope 를 dual-block-only ADR 로 narrow (Amendment 30 sub-scope 1-S Fix A supersede)

**Lint behavior change (Phase 2 develop spec, Change Plan §3.2 SSOT)** — `_check_adr_parity` 의 top 에 **dual-block gate** 신설:

```
dual_block = bool(amendments_ids) and bool(amendment_log_ids)
IF dual_block:                # 예: ADR-082 (amendments[] AND amendment_log[] 둘 다)
    run Block 1 / Block 2 / Block 3
    (Fix B H2/H3 body detection + Fix C frontmatter scan cap RETAIN — dual-block path 유효)
ELSE:                         # single-block 양방향 / amendments[]-only / no-amendments
    EXEMPT → return PASS (no violations)
```

- **dual-block ADR** (amendments[] AND amendment_log[] 둘 다 non-empty) → Block 1 (amendments[] ↔ body) + Block 2 (amendment_log[] ↔ body, F-DR-001 P0 sentinel) + Block 3 (amendments[] ↔ amendment_log[] cross-count). Fix B (body H2/H3) + Fix C (frontmatter scan cap 5000) RETAIN.
- **그 외** (single-block 양방향 = amendment_log[]-only 또는 amendments[]-only / parens-convention / no-amendments) → EXEMPT, return PASS.

**이는 CFP-1688 Fix A 를 supersede 한다**: Fix A 는 single-block (amendment_log[]-only) 을 "Block 2 만 적용" 했으나, Amendment 32 의 dual-block gate 는 single-block 을 **fully exempt** (Block 2 도 미적용). 즉 Amendment 32 은 Amendment 30 sub-scope 1-S 의 **refine/narrow** (single-block-Block-2 → single-block-EXEMPT).

**F-DR-001 P0 sentinel 무약화**: F-DR-001 origin (CFP-1637 retro 발견, Amendment 26 amendment_log[] entry present but body section missing) 자체가 **dual-block ADR-082** 의 case. dual-block ADR 의 Block 2 (amendment_log[] ↔ body parity) 는 retain — F-DR-001 보호 보존. single-block ADR 의 body-gap 은 Option A 결정상 policing 대상 아님 (35 parens-convention + ADR-045 single-block = lint 가 정확히 read 못하는 valid convention, FP 만 양산 → policing 가치 < FP 비용).

**lint scope correction = 신규 check 아닌 sub-scope 1-Q scope narrow** — 기존 `adr-dual-block-parity` evidence-checks-registry entry + `hotfix-bypass:adr-dual-block-parity` label 재사용. 신규 evidence-checks-registry entry 0 / 신규 label 0 / label-registry MINOR bump 0.

#### Wave 분배 (Combined Phase 1+2 — CFP-1648/CFP-1688 combined precedent 답습)

- **Phase 1 (본 ADR Amendment 32, design lane)**: §결정 1 layer 1 sub-scope 1-U 신설 + dual-block gate 결정 codify + convention census rationale (39 match / 35 parens-convention) + Change Plan §8 Test Contract (lint narrow spec — dual-block gate, TC-3/TC-9/TC-10 변경 flag).
- **Phase 2 (develop lane dispatch — Change Plan §3.2 + §8 SSOT)**: `scripts/lib/check_adr_dual_block_parity.py` `_check_adr_parity` dual-block gate 적용 (single-block 양방향 + no-amendments EXEMPT, dual-block 만 Block 1/2/3 / Fix B + Fix C RETAIN) + bats TC 변경 (TC-9 rationale 변경 / TC-10 exit 1→0 / TC-3 WARNING→PASS) + dual-block ADR regression guard (TC-1/4/7/11/14/15 UNCHANGED).

### Axis disjoint

- §결정 1 sub-scope 1-Q (Amendment 28 CFP-1648) — dual-block parity 3-invariant forward-prevention lint (lint **신설**)
- §결정 1 sub-scope 1-S (Amendment 30 CFP-1688) — 1-Q lint single-block mode (Fix A — amendment_log[]-only → Block 2 만) + body H2/H3 both-level (Fix B) + frontmatter scan cap (Fix C) **scope correction**
- §결정 1 sub-scope 1-U (본 Amendment 32 CFP-1734) — 1-Q lint scope 를 **dual-block-only ADR 로 narrow** (dual-block gate) — **1-S Fix A supersede** (single-block-Block-2 → single-block-EXEMPT). Fix B + Fix C RETAIN (dual-block path).
- Axis 분리 — lint 신설 (1-Q) ↔ lint scope correction single-block-Block-2 (1-S) ↔ lint scope narrow dual-block-only (1-U). 1-U 는 1-S 의 second narrow (verify subject 동일 = ADR dual-block structural parity, 적용 scope 만 dual-block-only 로 축소).

### META self-application (recursive dogfooding — dual-block exemplar, narrow 후에도 ADR-082 검사)

본 Amendment 32 = ADR-082 의 **dual-block convention exemplar** 이며, narrow 후 lint 가 본 ADR-082 자신의 dual-block structure 위에서 **여전히 Block 1/2/3 를 검사** 한다 (dual-block gate 가 ADR-082 를 면제 안 함 — amendments[] AND amendment_log[] 둘 다 present). 따라서 recursive dogfooding 이 mandatory:

- `amendments[]` entry: Amendment 32 row append (max=30 → next-slot=31 verified, origin/main 1d004935)
- `amendment_log[]` entry: Amendment 32 row append (F-DR-001 P0 sentinel — amendment_log entry present 의무)
- body `## Amendment 32` section: 본 section (H2 — dual-block convention 정합)

**3-block parity authoring (Amendment 32 self)** = 정확 (3 block 전부 amendment_id 31 보유). 단 ADR-082 의 **pre-existing genuine drift** (amendments 8-13/18/20-21 body section 부재 + amendment_log[] entry 13 부재) 는 narrow 후에도 dual-block ADR-082 검사에서 정당 surface 한다 — 이는 #1735 'ADR-082-only genuine drift: backfill vs accept' 별도 smaller 결정 (본 CFP scope 외, do NOT address here). Amendment 32 자체의 entry 는 모든 block 에 parity 보유하므로 Amendment 32 row 가 lint warning 을 추가하지 않음. (META self-application — §결정 10.D 14th applied case). Amendment 17 §결정 1-G strict pre-reservation 7th applied case (ADR-RESERVATION row pre-append + commit 7926974d, `pre_reservation_verified: true`).

### #1735 narrow + ADR-045 effect (out of scope — accepted per Option A)

- **#1735 narrows**: dual-block ADR 만 policing → ADR-082 = 유일 genuine drift dual-block ADR. #1735 = 'ADR-082-only genuine drift: backfill vs accept' 별도 smaller 결정 (본 CFP 미해결, separate carrier).
- **ADR-045 effect (accepted)**: ADR-045 (single-block amendment_log[]-only) 면제 → 기존 genuine body-gap warning (amendments 1/7/10/11) 소멸. Option A 정합 — lint 가 single-block convention 을 policing 안 함 (lint 가 정확히 read 못하는 valid convention 의 body-gap 은 lint 책임 외).

### Related

- CFP-1734 carrier Story
- CFP-1688 origin (sub-scope 1-S Fix A single-block mode — 본 Amendment 32 = 1-S Fix A supersede, dual-block gate narrow)
- CFP-1648 sibling (sub-scope 1-Q lint origin Amendment 28, dual-carrier naming SSOT `adr-dual-block-parity`)
- #1735 — ADR-082-only genuine drift backfill vs accept (separate smaller 결정, narrow 후 영역, 본 CFP scope 외)
- ADR-071 — parens-convention exemplar (`## §결정 N. <title> (Amendment M, CFP-XXX)`, amendments[]-only, lint 미검출 valid convention)
- ADR-045 — single-block convention (amendment_log[]-only + H3 body) — Option A narrow 후 면제 대상
- ADR-082 (본 ADR) — dual-block convention exemplar (amendments[] + amendment_log[] + H2 body) — narrow 후에도 검사 대상 (recursive dogfooding)
- ADR-073 / ADR-082 — Orchestrator verify-before-trust (ADR census 채널 — 82 frontmatter-amendment ADR convention 직접 분류)
- ADR-061 Amendment 3 §결정 11 — CodeQL ReDoS guard (Phase 2 dual-block gate 는 set membership check 만, regex 변경 0 — ReDoS 무관)
- ADR-054 §결정 1 — doc-only fast-path 비적격 (lint scope narrow = scripts/tests 변경 동반, Combined Phase 1+2)
- `scripts/lib/check_adr_dual_block_parity.py` — Phase 2 lint narrow target (`_check_adr_parity` dual-block gate, Fix A supersede, Fix B + Fix C RETAIN)
- `tests/scripts/check-adr-dual-block-parity/` — Phase 2 bats TC 변경 target (TC-9 rationale / TC-10 exit 1→0 / TC-3 WARNING→PASS / dual-block TC-1/4/7/11/14/15 regression guard)

## Amendment 33 — §결정 1 layer 1 sub-scope (1-V) execution_context_reconciliation

**Date:** 2026-05-27 KST
**Carrier:** CFP-1787 (audit:from-cfp-1764-retro)
**Direction:** strengthening
**Pattern count:** 4 reach (CFP-1735 §6 + CFP-1753 §6 + CFP-1755 §6 + CFP-1764 §4.5 self) ≥ ADR-045 §D-9 Mandatory threshold 2

### §결정

§결정 1 layer 1 (Orchestrator scope + internal lane agent write-time scope) sub-scope (1-V) 신설 — verdict packet 안 `execution_context_state` 5 sub-field declare 의무.

### 5 sub-field 명세

| # | field | derivable? | derive primitive | declare 의무 사유 |
|---|---|---|---|---|
| 1 | `working_dir_abs_path` | YES | `pwd` (absolute path) | review 가 packet 안 path 와 spawn 시점 path 비교 가능. spawn-time vs return-time drift 검출. sub-scope 1-J + ADR-040 worktree convention 정합. |
| 2 | `target_write_repo` | YES | `git -C <wt> remote -v` (origin URL → org/repo 파싱) | sub-scope 1-J `worktree_target_repo` 와 axis-adjacent **disjoint** — 1-J = chief author worktree-level cross-repo target verify (worktree HEAD ↔ expected repo) / 1-V = packet-level execution context state declare (after-the-fact). |
| 3 | `staged_files_required[]` | **NO (novel axis)** | derive 불가능 — intent declaration only | "이 write 산출물이 staged 상태로 만들어야 하는 file 목록" intent. retro file + surrounding spec/plan + ADR-RESERVATION row 등 multi-file write 누락 검출. |
| 4 | `branch_required` | YES | `git branch --show-current` (또는 `cfp-NNN[-<slug>]` derive via ADR-024) | stale branch 위 write 검출. |
| 5 | `remote_sync_required` | **NO (novel axis)** | derive 불가능 — pre-write intent enum | 3-value enum: `pull` / `fetch` / `N/A`. pre-write 시점에 declare 안 하면 stale main 위 write 후 force-push 위험. |

### Scope boundary

- **In scope (의무 영역)**: lane agent verdict packet (PMOAgent / chief author / deputy / 4-tuple sub-tuple / retro write-target). retro / spec / plan / change-plan / ADR draft 안 write 산출물.
- **Out of scope (면제 영역)**: Orchestrator inline whitelist 4-entry (사용자 dialog / TodoWrite scratchpad / Read-only Q&A / Status report) 안 self-write. §9 verdict / §10 FIX Ledger / phase transition label.
- **Cross-repo 다중 write_target 영역**: primary `target_write_repo` 1 string 강제 + optional `cross_repo_secondary_targets[]` array (3+ repo 시 declare). primary write 가 항상 1 repo invariant.

### Axis disjoint statement (ADR-068 I-4 wording SSOT 정합)

본 sub-scope 1-V 는 sub-scope 1-A~1-U 22 entry 와 disjoint axis:

- 1-A (cross-repo state verify) ↔ 1-V: 1-A = Orchestrator state read verify-before-cite axis / 1-V = lane agent packet field declare axis (write-time)
- 1-J (cross-repo worktree target authority) ↔ 1-V: 1-J = chief author worktree-level cross-repo target verify (worktree HEAD ↔ expected repo at chief-author-time) / 1-V = packet-level after-the-fact execution context declare (post-write)
- 1-T (PMOAgent retro write-time fact verify) ↔ 1-V: 1-T = retro 안 cited fact (commit SHA / label version / bypass count) source direct verify / 1-V = retro write 시점 execution context state declare (verify subject axis disjoint: fact source vs environment state)
- 1-U (1-T dual-block lint Wave 2 wire) ↔ 1-V: 1-U = sub-scope 1-T mechanical lint / 1-V = 별도 sub-scope 신설 declarative + Wave 2 wire

### Wave 분리

- **Wave 1 (본 Amendment, declarative)**: §결정 codify + frontmatter `mechanical_enforcement_actions[]` entry `execution-context-state-presence` deferred-followup 명시 + CLAUDE.md cross-ref 갱신
- **Wave 2 (combined single PR, mechanical wire)**: `scripts/lib/check_execution_context_state.py` + `templates/github-workflows/execution-context-state-check.yml` + `tests/wave2-mechanical-wire/check-execution-context-state.bats` + `docs/inter-plugin-contracts/label-registry-v2.md` v2.84 → v2.85 MINOR + `docs/evidence-checks-registry.yaml` 신규 entry
- **Wave 3+ (future, 별 sub-CFP)**: Orchestrator runtime actual-value verify (`execution_context_state` declare 값 ↔ runtime `pwd` / `git remote -v` 값 mismatch detection). 현 Wave 2 lint = packet field presence + schema validation only (offline).

### dogfood self-application (sub-scope 1-V 1st applied case)

본 carrier Story 의 spec frontmatter `pre_lookup_evidence[]` 안 본 carrier 작성 시점 execution context 4 source verify declare — 본 sub-scope 1-V 의 1st applied case = self. META self-applied (§결정 10.D 12th applied case + sub-scope 1-G 18th + sub-scope 1-L spawn prompt fact verify).

## Amendment 34 (2026-05-29 KST, CFP-1842) — sub-scope 1-W `orchestrator_spawn_prompt_fact_verify_before_embed` (Orchestrator-side spawn prompt fact discipline, paired ADR-073 Amd 18)

본 Amendment 는 §결정 1 layer 1 (Orchestrator scope) sub-scope 1-W 신설 — Orchestrator 가 subagent spawn 직전 spawn prompt 안 fact 단언 verify-before-embed 의무. ADR-058 §결정 5 ratchet 강화 only (sub-scope 22→23). pattern_count 3 reach Mandatory ADR-045 §D-9 escalation source.

### §A. 5종 fact category (C1-C5 closed-enum)

Orchestrator 가 subagent spawn prompt 안 다음 5 category fact 단언 시 verify-before-embed 의무:

| Category | 영역 | Verify method |
|---|---|---|
| C1 counter | label-registry hotfix-bypass family count / evidence-checks entry count / sub-scope letter 개수 등 | `grep -c '^pattern' file` direct |
| C2 version | label-registry-v2 version / plugin metadata version / marketplace.json version / ADR amendment id 등 | `grep '^version:' file` / `grep amendment_id:` direct |
| C3 SHA | origin/main HEAD SHA / pre-spawn pin SHA / 파일 sha256 | `git rev-parse origin/main` / `sha256sum file` direct |
| C4 verify-result | "sha256 PASS" / "byte-identical OK" / sub-agent claim "PASS" | actual command 재실행 (Orchestrator 자신이 verify, claim relay 금지) |
| C5 file-existence | 파일 path 존재 + line count | `ls file` / `wc -l file` direct |

6번째 category 확장 = 별도 CFP carrier (ADR-064 §결정 5 CFP scope unitary carve-out).

### §B. Mechanism — pre-spawn verify-before-embed protocol

Orchestrator 가 subagent spawn prompt 작성 시:

1. 단언할 fact 식별 (5 category C1-C5 분류)
2. 각 fact 의 verify method 실행 (Read / Bash / git api 직접 호출)
3. verify 결과 spawn prompt 안 embed (단언 옆 `verified-via: <method>` annotation 의무)
4. subagent → Orchestrator return 시 subagent claim relay 직접 spawn 금지 (Orchestrator 가 fresh verify 후 다음 subagent spawn)

precedent (axis disjoint): ADR-082 sub-scope 1-L (CFP-1590) = worker self-write spawn prompt fact (worker→worker). 본 1-W = Orchestrator-side (Orchestrator→subagent). axis disjoint complement.

### §C. META self-application (Mandatory carrier 본 자체)

본 Amendment 34 = META first applied case:
- 본 Story #1842 초기 Issue body 가 "ADR-082 Amd 24 sub-scope 1-W" 인용 → actual = Amd 33 → next Amd 34 (3차 pattern occurrence)
- Issue body 정정 후 본 spawn prompt 안 모든 fact (Amd 34 / sub-scope 1-W / Amd 33 / 1-V 21 letters) 단언 = pre-write verified
- 즉 본 Amendment 본문 작성 자체가 1-W 첫 적용 사례 (write-time Read verify required, claim ≠ ground truth 차단)

### §D. Wave 1 declarative-only — Wave 2 별 sub-CFP carrier

`mechanical_enforcement_actions[]` `orchestrator-spawn-prompt-fact-verify` entry = warning-tier deferred-followup. Wave 2 carrier (CFP-1842-W2 reserved):
- `scripts/check-orchestrator-spawn-prompt-fact-verify.sh` lint
- `templates/github-workflows/orchestrator-spawn-prompt-fact-verify.yml` workflow
- bats fixture (5 TC per C1-C5)
- `docs/evidence-checks-registry.yaml` warning-tier entry
- `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump — `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` family member

precedent 23-instance chain Wave 1→Wave 2 split established.

### §E. Disjoint axis cross-ref

- ADR-082 sub-scope 1-L (CFP-1590) — worker self-write spawn prompt fact axis. 1-W = Orchestrator-side complement.
- ADR-082 sub-scope 1-V (CFP-1787) — write-target agent verdict packet execution_context. 1-W = pre-spawn timing (1-V = write-time).
- ADR-073 sub-scope chain transition trigger — paired sibling ADR-073 Amd 18 16번째 entry `pre_spawn_prompt_fact_assertion` (axis 동형 sub-domain cadence codify).

### §F. sunset_justification N/A 정당

is_transitional: false 보존. Amd 34 = 강화 방향 only (sub-scope 22→23 ratchet 확장). ADR-058 §결정 5 sunset_justification ratchet 통과. ADR-064 §self-application top-down ratchet 정합 (forbid scope 확장).

### §G. Related

- `<internal-docs>/plugin-codeforge/stories/CFP-1842.md` — Story file
- `<internal-docs>/plugin-codeforge/specs/CFP-1842-orchestrator-spawn-prompt-fact-discipline.md` — Spec file
- paired sibling ADR: ADR-073 Amendment 18 (transition trigger 16번째 entry)
- sibling axis-disjoint Issue: mclayer/plugin-codeforge#822 (post-task verify discipline, HIGH priority pre-existing)
- 3 pattern occurrence retros:
  - codeforge-internal-docs/plugin-codeforge/retros/2026-05-28-cfp-1808.md F-005 (1차)
  - codeforge-internal-docs/plugin-codeforge/retros/2026-05-29-cfp-1807.md F-002 (2차)
  - 본 Issue #1842 초기 body META (3차)

## Amendment 35 (2026-05-30 KST, CFP-822) — sub-scope 1-X `subagent_self_report_post_task_verify` (Orchestrator-side subagent claim post-task verify discipline, paired ADR-073 Amd 19)

본 Amendment 는 §결정 1 layer 1 (Orchestrator scope) sub-scope 1-X 신설 — Orchestrator 가 subagent "DONE / success / PASS / MERGED" 보고 receive 후 critical artifact actual existence + content verify-before-trust 의무. ADR-058 §결정 5 ratchet 강화 only (sub-scope 23→24). mctrader MCT-189 + MCT-190 origin evidence N=2 reach (2026-05-17, #822 HIGH priority 12-day pre-existing).

### §A. 6종 critical artifact category (closed-enum)

Orchestrator 가 subagent (lane PL / chief author / deputy / 4-tuple sub-tuple) "DONE" 보고 receive 후 다음 6 category artifact 가 보고 claim 안 있을 시 actual existence + content verify-before-trust 의무:

| Category | 영역 | Verify method |
|---|---|---|
| ARTIFACT-1 ADR | docs/adr/ADR-*.md (신규 ADR / Amendment) | `ls docs/adr/ADR-*.md` + `grep -E '^## Amendment <N>' file` + `Read line 1-N` |
| ARTIFACT-2 Story | Story file path (`<internal-docs>/<plugin>/stories/CFP-N.md`) | `ls <story-path>` + `Read line 1-50` + `grep -E '^## §<N>'` |
| ARTIFACT-3 RETRO | retro file (`<internal-docs>/<plugin>/retros/YYYY-MM-DD-cfp-N.md`) | `ls <retro-path>` + `Read line 1-50` + `grep -E '^## §|^## F-'` |
| ARTIFACT-4 scope_manifest | Epic scope manifest (`scope_manifests/<epic>.yaml`) | `ls <manifest-path>` + `Read line 1-N` + `grep -E '^planned_(adrs|files|claude_md_sections)'` |
| ARTIFACT-5 spec / plan | spec / plan file (`<internal-docs>/<plugin>/specs/CFP-N-*.md` 또는 `/plans/CFP-N-*.md`) | `ls <spec-path>` + `Read line 1-N` + `grep -E '^## §|^---'` |
| ARTIFACT-6 code FIX | production source file (`src/**`, `scripts/**`, `templates/**` 등 FIX target) | `git status --short <path>` + `git diff <path>` + `Read line 1-N` |

7번째 category 확장 = 별도 CFP carrier (ADR-064 §결정 5 CFP scope unitary carve-out).

### §B. Mechanism — post-task receive-verify-before-trust protocol

Orchestrator 가 subagent return 수신 시:

1. subagent return claim parse (예: "DONE: ADR-082 Amd 35 written / ARTIFACT-1 ADR-082 + ARTIFACT-2 Story + ARTIFACT-5 spec")
2. 각 claim 의 6 category 분류 (ARTIFACT-1 ~ ARTIFACT-6)
3. category 별 verify method 실행 (Read / Bash / git status 직접 호출)
4. verify 결과 = expected fact OK 시 다음 step / mismatch 시 reject + FIX iter trigger
5. 다음 subagent spawn 또는 사용자 보고 직전 actual verify 결과 verbatim 첨부 (claim relay 직접 보고 금지)

axis disjoint vs sub-scope 1-W (CFP-1842, Orchestrator → subagent pre-spawn fact verify cadence) — 1-X = subagent → Orchestrator post-task verify cadence (claim-receive trust gate, opposite direction).

### §C. META self-application (본 carrier 본 자체)

본 Amendment 35 = META first applied case:
- 본 Orchestrator 가 본 ArchitectAgent spawn → ArchitectAgent return "DONE: 5 file edited (ADR-082 + ADR-073 + CLAUDE.md + Story + Spec)"
- Orchestrator 가 claim 수신 후 5 file actual verify 의무 (ls + git status --short + Read 첫 line 첫 last)
- 즉 본 Amendment 본문 작성 → spawn return → Orchestrator post-task verify 자체가 1-X 첫 적용 사례
- precedent: mctrader-hub MCT-189 (subagent SUCCESS claim 후 actual file 부재 발견) + MCT-190 (동형 reproduction, 2026-05-17)

### §D. Wave 1 declarative-only — Wave 2 별 sub-CFP carrier

`mechanical_enforcement_actions[]` `subagent-self-report-post-task-verify` entry = warning-tier deferred-followup. Wave 2 carrier (CFP-822-W2 reserved):
- `scripts/check-subagent-self-report-post-task-verify.sh` lint (post-tool-use hook 영역 — Agent tool return parse)
- `templates/github-workflows/subagent-self-report-post-task-verify.yml` workflow (declarative anchor)
- bats fixture (6 TC per ARTIFACT-1~6)
- `docs/evidence-checks-registry.yaml` warning-tier entry
- `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump — `hotfix-bypass:subagent-self-report-post-task-verify` family member

precedent 24-instance chain Wave 1→Wave 2 split established.

### §E. Disjoint axis cross-ref

- ADR-082 sub-scope 1-W (CFP-1842) — Orchestrator → subagent pre-spawn fact verify axis. 1-X = post-task complement (opposite direction, same Orchestrator-side).
- ADR-082 sub-scope 1-M (CFP-1589) — own-author synthesis 보고 vs actual git commit gap verify (chief author self-write). 1-X = Orchestrator post-task scope (verify subject = Orchestrator, verify object = subagent claim).
- ADR-082 sub-scope 1-V (CFP-1787) — execution_context_reconciliation verdict packet 5 sub-field declare (write-time semantic truth). 1-X = post-task receive-time (different lifecycle).
- ADR-073 sub-scope chain transition trigger — paired sibling ADR-073 Amd 19 17번째 entry `post_subagent_task_completion` (axis 동형 sub-domain cadence codify).

### §F. sunset_justification N/A 정당

is_transitional: false 보존. Amd 35 = 강화 방향 only (sub-scope 23→24 ratchet 확장). ADR-058 §결정 5 sunset_justification ratchet 통과. ADR-064 §self-application top-down ratchet 정합 (forbid scope 확장).

### §G. Related

- `<internal-docs>/plugin-codeforge/stories/CFP-822.md` — Story file
- `<internal-docs>/plugin-codeforge/specs/CFP-822-subagent-self-report-verify-gate.md` — Spec file
- paired sibling ADR: ADR-073 Amendment 19 (transition trigger 17번째 entry `post_subagent_task_completion`)
- origin Issue: mclayer/plugin-codeforge#822 (HIGH priority 12-day pre-existing, mctrader MCT-189/190 carrier)
- 2 pattern occurrence retros (external):
  - mctrader-hub retro 2026-05-17 MCT-189 (subagent SUCCESS claim 후 actual file 부재)
  - mctrader-hub retro 2026-05-17 MCT-190 (동형 reproduction, N=2 Mandatory)
- META 3rd occurrence: 본 carrier Orchestrator → ArchitectAgent return verify (META self-application)
- 본 carrier scope = wrapper-actionable §2 only:
  - #822 §1 = `superpowers:subagent-driven-development` skill `implementer-prompt.md` (external claude-plugins-official) — defer (별도 upstream PR)
  - #822 §3 = mctrader-hub ADR-032 amendment (external) — defer (별도 consumer PR)

## Amendment 36 (2026-06-01 KST, CFP-1613) — sub-scope 1-Y `amendment_array_ordering_convention` (frontmatter amendments[] + amendment_log[] array ordering SSOT, hybrid: id ascending + reservation_date tie-break)

본 Amendment 는 §결정 1 layer 1 (Orchestrator scope) sub-scope 1-Y 신설 — ADR frontmatter `amendments[]` + `amendment_log[]` array 의 **row-append ordering convention SSOT**. ADR-058 §결정 5 ratchet 강화 only (sub-scope 24→25 — convention codify, forbid scope 축소 0건). MEDIUM Wave 1 declarative. 동인 = CFP-1601 retro F-DR-1601-2 P2 (paired sibling race CFP-1559 Amd 20 ↔ CFP-1578 Amd 21 chronological-vs-id ordering ambiguity).

### Context

Amendment 30 (sub-scope 1-S) 가 ADR frontmatter **block convention** (single-block vs dual-block) 을 SSOT 화했으나, array **내부 row ordering convention** (어떤 순서로 row 를 append 하는가) 은 미codify 상태였다. CFP-1601 retro F-DR-1601-2 P2 에서 paired-sibling race (CFP-1559 Amd 20 ↔ CFP-1578 Amd 21) 동시 reservation 시 **chronological (reservation_date) vs id (amendment_id) ordering 모호성** 이 surface — 두 CFP 가 동시에 slot 을 예약하면 append 순서가 작성자별로 갈려 frontmatter array 가 비결정적 순서로 자란다. dual-block-parity lint (sub-scope 1-Q/1-S, Amendment 28/30) 는 **set parity** (amendment_id 집합 일치) 만 검증하고 **순서** 는 검증하지 않으므로, 순서 불일치는 lint-silent drift 로 누적된다.

anchor_id = `amendment_array_ordering_convention` / root_cause_class = `frontmatter-array-order-nondeterministic`. ADR-082 §결정 1 layer 1 sub-scope 1-Y (disjoint from 1-A through 1-X — array ordering convention axis. 1-S block convention 의 sub-domain refinement: 1-S = "어떤 block 을 쓰는가" / 1-Y = "그 array 안 row 를 어떤 순서로 쓰는가").

### §A. Ordering convention SSOT (hybrid — id ascending + reservation_date tie-break)

`amendments[]` + `amendment_log[]` 양 array 모두 다음 ordering 의무:

1. **Primary key — `amendment_id` ascending** (1, 2, 3, … N). 양 block 모두 amendment_id 오름차순으로 row append. 신규 amendment = max amendment_id + 1 = array 최하단 append (verify-before-trust source command = `grep -oE '^  - amendment_id: [0-9]+' <adr> | tail -1`, sub-scope 1-K precision rule 정합).
2. **Tie-break — `reservation_date` ascending** (paired-sibling-race 한정). 두 CFP 가 동일 시점 concurrent reservation 으로 amendment_id 충돌 시, 먼저 reserve 한 (이른 `reservation_date`) CFP 가 낮은 amendment_id 점유. reslot 발생 시 §B decision tree 적용.

Primary key (id ascending) 가 거의 모든 경우를 cover — reservation_date tie-break 는 concurrent collision (paired-sibling race) edge case 한정 발동.

### §B. sub-scope letter ↔ amendment_id mapping (NOT guaranteed synchronized)

sub-scope letter (1-A … 1-Y) 와 amendment_id (1 … 36) 는 **동기화 보장 안 됨** — reslot race 가 둘을 decouple 한다.

**Evidence**: CFP-1684 가 collision 후 reslot 되어 **Amd 31 / sub-scope 1-T** 가 됐다 (CFP-1688 Amd 30 + sub-scope 1-S slot collision reslot — Amendment 31 body heading 명시). 즉 amendment_id 30↔31 사이 sub-scope 가 1-S↔1-T 로 흘렀으나, 항상 `amendment_id N ⇒ sub-scope = N번째 letter` 식 직접 매핑은 성립 안 한다 (초기 Amendment 1-7 은 §결정 6 등 layer-level touch 로 sub-scope letter 미부여 — sub-scope letter 는 1-A 부터 layer 1 Orchestrator scope sub-scope 도입 후 sequential).

**읽는 법 (mapping resolution)**: `amendment_log[]` entry 가 **both** field 를 carry 한다 — `amendment_id` (정수 slot) + `sub_scope` (예 `"1-W"`) + `ref` (예 `"## Amendment 34 + sub-scope 1-W row"`). mapping 확인 시 **amendment_log[] entry 의 `sub_scope` field 가 SSOT** (body heading 의 sub-scope 표기는 human-readable mirror). amendment_id ↔ sub-scope 동기 가정 금지 — entry field 직접 read 의무 (verify-before-trust 정합).

### §C. paired-sibling-race row-append decision tree

두 CFP 가 concurrent 하게 amendment slot 을 예약할 때 (paired-sibling race) row-append ordering ladder:

1. **각 CFP 가 spawn 직전 ADR-RESERVATION `amendments_reserved[]` row pre-append** (sub-scope 1-G strict pre-reservation mandate 정합) + spawn prompt `pre_reserved_amendment_slots: [{adr, amendment_id}]` field 보유.
2. **collision 미발생 (순차 reserve)**: 먼저 reserve = 낮은 amendment_id (max+1), 나중 reserve = 그 다음 (max+2). id ascending append. 정상 case.
3. **collision 발생 (동일 max+1 을 둘이 동시 claim)**: `reservation_date` tie-break — 이른 reservation_date CFP 가 max+1 점유, 늦은 CFP 는 **reslot** (max+2 로 이동, 즉 reslotted entry 가 더 높은 id 점유). reslot 된 CFP 의 sub-scope letter 도 그에 맞춰 sequential 재배정 (CFP-1684 → Amd 31/1-T precedent).
4. **reservation_date 동일 (분 단위 충돌)**: carrier_story CFP 번호 ascending 을 final tie-break (낮은 CFP 번호 = 낮은 amendment_id). deterministic 보장.

reslot 후 commit 직전 **재verify 의무** (sub-scope 1-K Step 1 source command + sub-scope 1-V execution context): `git fetch origin main` + `grep -oE '^  - amendment_id: [0-9]+' <adr> | tail -1` actual next-slot 재확인 후 최종 row append.

### §D. Wave 1 declarative-only — Wave 2 별 sub-CFP carrier

`mechanical_enforcement_actions[]` 신규 entry 0 (convention codify — array 순서 lint 는 별 sub-CFP). Wave 2 carrier (CFP-1613-W2 reserved, 재발 시 promote):
- `scripts/lib/check_adr_amendment_array_ordering.py` lint (amendment_id ascending 검증 — dual-block-parity lint 의 set-parity 를 order-parity 로 확장하는 sub-domain)
- `templates/github-workflows/adr-amendment-array-ordering.yml` workflow (declarative anchor)
- bats fixture (id-ascending PASS / out-of-order WARNING / reslot tie-break)
- `docs/evidence-checks-registry.yaml` warning-tier entry + `hotfix-bypass:adr-amendment-array-ordering` family member

precedent 25-instance chain Wave 1→Wave 2 split established. pattern_count ≥ 2 추가 reach 시 promote.

### §E. Disjoint axis cross-ref

- ADR-082 sub-scope 1-S (CFP-1688, Amendment 30) — ADR frontmatter **block convention** SSOT (single-block vs dual-block, "어떤 block 을 쓰는가"). 1-Y = block 내부 **row ordering** ("그 array row 를 어떤 순서로"). 1-Y 는 1-S 의 sub-domain refinement (block convention → row ordering convention).
- ADR-082 sub-scope 1-Q (CFP-1648, Amendment 28) — dual-block parity **set** 검증 (amendment_id 집합 일치). 1-Y = **order** convention (set parity 가 verify 안 하는 순서 axis). lint 신설 시 1-Q sub-domain 확장.
- ADR-082 sub-scope 1-G (CFP-1435, Amendment 17) — amendment-slot strict pre-reservation mandate. 1-Y §C decision tree 가 1-G pre-reservation 을 paired-race ordering ladder 로 확장 (pre-reservation 후 collision 시 reslot rule).
- ADR-082 sub-scope 1-K (CFP-1601, Amendment 22) — numeric claim source command precision. 1-Y next-slot 계산 (`grep … | tail -1`) 이 1-K source command rule 직접 재사용.
- ADR-058 §결정 5 — sunset_justification N/A ratchet-up (convention codify, scope 축소 0). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합 (강화 방향, pattern evidence = CFP-1601 retro F-DR-1601-2 P2).

### §F. META self-application (recursive dogfooding)

본 Amendment 36 = sub-scope 1-Y 첫 적용 사례 = self:
- 본 carrier 가 §A id-ascending convention 을 본 Amendment 자신의 row append 에 적용 — `amendments[]` + `amendment_log[]` 양 block 모두 amendment_id 36 을 max(35) + 1 = 최하단 append (id ascending 준수).
- verify-before-trust: spawn 직전 `grep -oE '^  - amendment_id: [0-9]+' docs/adr/ADR-082-*.md | tail -1` actual = `amendment_id: 35` → next-slot = 36 `[verified]` (sub-scope 1-K source command + 1-V execution context 정합).
- dual-block parity: 본 Amd 36 의 amendments[] + amendment_log[] + body `## Amendment 36` 3-block parity 보존 (Amd 32 sub-scope 1-U dual-block gate self-application 정합).
- sub-scope letter = 1-Y (1-X = CFP-822 Amd 35 다음 sequential — amendment_id 36 ↔ sub-scope 1-Y 동기, 단 §B 에 따라 동기는 보장이 아닌 본 case 의 사실).

### §G. sunset_justification N/A 정당

is_transitional: false 보존. Amd 36 = 강화 방향 only (sub-scope 24→25 ratchet 확장 + array ordering convention codify). ADR-058 §결정 5 sunset_justification ratchet 통과 (forbid scope 확장, convention 명문화). ADR-064 §self-application top-down ratchet 정합.

### §H. Related

- CFP-1613 carrier Story (`<internal-docs>/plugin-codeforge/stories/CFP-1613.md`)
- CFP-1601 retro F-DR-1601-2 P2 — paired-sibling race ordering ambiguity origin (CFP-1559 Amd 20 ↔ CFP-1578 Amd 21 chronological-vs-id)
- ADR-082 Amendment 30 (sub-scope 1-S) — block convention SSOT (본 1-Y 의 parent axis)
- ADR-082 Amendment 28 (sub-scope 1-Q) — dual-block parity set-check (order-check 미포함 — 1-Y 가 보완)
- ADR-082 Amendment 17 (sub-scope 1-G) — amendment-slot strict pre-reservation (§C decision tree base)
- reslot precedent: CFP-1684 → Amd 31 / sub-scope 1-T (CFP-1688 Amd 30 / 1-S collision reslot)
- origin Issue: mclayer/plugin-codeforge#1613 (MEDIUM, Wave 1 declarative)
- ADR-054 §결정 1 — doc-only fast-path 적격 (단일 PR, scripts/tests 무변경)

## Amendment 37 (2026-06-20 KST, CFP-2383) — sub-scope 1-Z `spawn_prompt_fact_verify_wave2_wire_ssot` (sub-scope 1-L Amd 23 declaration-only → Wave 2 mechanical wire SSOT: PR-body-proxy static presence-only lint binding)

본 Amendment 는 §결정 1 layer 1 sub-scope 1-Z 신설 — sub-scope **1-L** (Amendment 23, CFP-1590) 의 Wave 1 declaration-only mandate 를 **Wave 2 mechanical enforcement wire SSOT** 로 codify 한다. ADR-058 §결정 5 ratchet 강화 only (sub-scope 25→26 — Wave 2 mechanical enforcement 추가, forbid scope 축소 0건). warning-tier. Epic CFP-2380 S3. 동인 = CFP-2380 S1 deferred-followup-reconcile FLAG 해소 (firsthand: `bash scripts/check-deferred-followup-reconcile.sh` 실행 → `spawn-prompt-fact-verify count=3/3 promotion_trigger=auto_blocking` [verified]).

> **Phase 분리**: 본 Amendment (Phase 1) = ADR Amendment + `mechanical_enforcement_actions[]` entry status flip + binding 만. 실 lint script / workflow / discriminating test / `evidence-checks-registry.yaml` detect_command·workflow 실파일 flip / `label-registry-v2` MINOR (`hotfix-bypass:spawn-prompt-fact-verify`) = **Phase 2 구현 lane** 산출 (본 Amendment 에서 작성 안 함). S1(CFP-2381)/S2(CFP-2382) Phase 1+Phase 2 split precedent 답습.

### Context

sub-scope 1-L (Amendment 23, CFP-1590) 는 "spawn prompt fact verify-before-trust mandate (upstream-inherited stale fact carrier super-class — worker→worker handoff)" 를 **Wave 1 declaration-only** 로 도입했다. `evidence-checks-registry.yaml` 의 `spawn-prompt-fact-verify` entry 가 그 anchor 인데, `detect_command` 와 `workflow` 가 실파일 없는 TBD 상태(`status: deferred-followup`)로 남아 한 번도 mechanically wired 되지 않았다. CFP-2380 S1 이 신설한 deferred-followup-reconcile 게이트가 이 entry 를 carrier_absent FLAG(count=3/3, auto_blocking)로 surface — 본 Amendment 가 그 FLAG 를 해소하는 Wave 2 mechanical wire SSOT.

anchor_id = `spawn_prompt_fact_verify_wave2_wire_ssot` / root_cause_class = `wave1-declaration-never-wired`. sub-scope 1-Z = disjoint from 1-A through 1-Y (1-L 의 mechanical enforcement wire axis — numeric-claim sub-scope 1-K(declaration)↔1-N(Wave 2 wire) precedent 동형 pairing).

### §A. 설계 결정 1 — wire 메커니즘 (3-source 합성)

PR-body-proxy static presence-only lint = 3개 선례의 합성:

1. **구조 / FP guard / exit code / test = S2 (`issue-body-claim-pre-screen`) 답습** — line-by-line `in_fence` toggle masking + `strip_inline_code` + `PER_BLOCK_SCAN_CAP = 50` + `ANNOTATION_MARKER = "[verified-via:"` (정적 substring, 정규식 아님) + exit `0=PASS / 1=FLAG / 2=SETUP`. Refactor 선택지 (b) 채택 (firsthand: `scripts/lib/check_issue_body_claim_pre_screen.py` L51/L54/L150-193 [verified]). 선택지 (a) 1-W 통째 복붙 = 부적합 (exit 0 고정 + window scan 이 S2 의 FP 개선 역행), 선택지 (c) 공통 lib 추출 = 조기 (응집력 낮음 — 3번째 PATTERNS 복본 등장 시 `fact_verify_patterns.py` 공통 추출 재검토, ModuleArch consult; escalation marker 보존).
2. **fact PATTERNS = 삭제된 1-W source 의 C1-C5 이식** — `c84fadf3:scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py` 의 PATTERNS (firsthand: `git show c84fadf3:...` L55-90 [verified]): C1 counter `\b(\d{2,})\s+(entries|...)` / C2 version `\bv\d+\.\d+(?:\.\d+)?\b` / C3 SHA `\b[0-9a-f]{40}\b|PRE-SPAWN-ORIGIN-MAIN-SHA:` / C4 verify-result `sha256 PASS|byte-identical OK|MERGED|CLEAN|drift 0` / C5 file-existence `\S+\.(md|yml|...)\s+(존재|...)|line count:\d+`. **ReDoS-safe invariant**: C1-C5 nested quantifier 0 + scan cap 50 — 신규 regex 추가 시 ReDoS invariant 명문 검증 의무.
3. **trigger / event / body-source = `tier-downgrade-guard.yml` 답습** — S2 는 `on: issues` event(PR 아님)이므로 PR-body-proxy canonical 선례 부적합. PR-event 선례 = `tier-downgrade-guard.yml` (firsthand: `.github/workflows/tier-downgrade-guard.yml` [verified]): `on: pull_request: types:[opened, synchronize, reopened]` + `paths: [docs/...]` + `permissions: contents: read` + `env: <X>: ${{ github.event.pull_request.body }}` + `run: bash scripts/check-*.sh`.

annotation marker canonical = `[verified-via:` (S2 정적 substring 형식 1개 고정). 1-L scope = worker→worker handoff, 4 sub-source (사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file).

### §B. 설계 결정 2 — PR-body-proxy 한계 명시 (anti-theater)

PR body 는 worker→worker handoff spawn prompt 의 **proxy 일 뿐 실 spawn prompt 가 아니다.** 검출 범위 = inherit fact 가 PR body 에 transcribe 된 경우만 — spawn prompt 직접 검사 아님. 이 한계를 명문화하지 않으면 surface theater (실제로 검사 안 하는 것을 검사하는 척) 위험. Phase 2 discriminating test 가 file-input 경로로 surface 실존을 증명 의무 (S2 동형, mutation 생존 0 목표). 정적 lint 이므로 §8.5 stateful test N/A + Perf Baseline N/A (TestContractArch).

### §C. 설계 결정 3 — 1-W orphan 처리 (axis disjoint 보존)

제거된 sub-scope 1-W (Amendment 34, CFP-1842) 의 entry / mandate 는 **부활하지 않는다.** 단순 1-W 파일 복원 = ADR-058 §결정 5 ratchet 위배 (de-bloat 제거 상태 유지). 본 wire 는 **1-L 의 최초 배선** (1-L 은 declaration 이후 한 번도 wired 안 됨). axis disjoint 보존:

- **1-L** (CFP-1590) = worker self-write spawn prompt fact (worker→worker handoff) — 본 Amendment 37 의 wire 대상.
- **1-W** (CFP-1842) = Orchestrator-side spawn prompt fact (Orchestrator→subagent handoff) — 별도 entry, 별도 bypass label (firsthand: `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` label-registry-v2.md L1942 등록 [verified]).

C1-C5 PATTERNS 는 1-W source 에서 이식하되, scope / trigger / handoff axis 는 1-L 용으로 재작성 (TestContractArch §B message-assert TC = Phase 2 — 1-W 잔재 없이 1-L 용 재작성 검증).

### §D. 설계 결정 4 — FP guard 4종 EXEMPT

PR body 도 markdown 이므로 S2 의 false-positive guard 4종 답습:

1. `in_fence` — fenced code block 내부 (``` toggle) 면제.
2. inline code-span — `` `...` `` (`strip_inline_code` masking) 면제.
3. blockquote — `>` prefix 행 면제.
4. SELF_SOURCE — fact 자체의 source 선언 행 면제.

`window = 5` 경계 + empty input PASS + setup error exit 2 (S2 boundary 답습).

### §E. 설계 결정 5 — deferral 명문화 + #2166 좌표

본 Story 에서 **wire 하지 않는** deferred entry 2건 (status retain — ADR-082 ratchet 삭제 불가):

- **retro-fact-verify-mandate** (Amendment 31 / sub-scope **1-T**, CFP-1684 — body heading 권위 [verified: `## Amendment 31 ... sub-scope (1-T) ... PMOAgent retro write-time verify-before-trust mandate (CFP-1684 ... CFP-1688 Amd 30/1-S slot collision reslot)`]; registry entry description 의 "Amendment 30/1-S" 표기는 reslot stale 잔재 — body heading SSOT). deferral 사유 = retro 는 cross-repo (`docs/retros` 가 internal-docs repo 에 영속 → wrapper CI surface 0 → wrapper 에서 lint 하면 거짓 inventory 위험).
- **fix-loop-reverify-mandate** (Amendment 29 / sub-scope **1-R**, CFP-1683). deferral 사유 = 3 field (`amendment_slot_revalidated` / `registry_version_revalidated` / `bypass_count_revalidated`) 가 fix-event-v1 schema 에 미영속 → static lint 하려면 schema MINOR bump 선행 의존 → 본 Story scope 초과.

**#2166 부분 close**: 본 Amendment 가 1-L (spawn-prompt-fact-verify) 를 wire 함으로써 #2166 의 해당 부분 close. 잔여 좌표 = (a) 외부지식 `source:` annotation lint + (b) 수치 측정방법 명기 lint — 위 3 entry (1-L wire + 2 deferral) 밖 잔여 (별 carrier vs 본 Epic 후속 Story 흡수 결정은 Orchestrator/PMO 좌표).

### §F. 보안 / 운영 정합

- **§7.4.5 env-isolation (P1)**: `pull_request` event (NOT `pull_request_target`) + `permissions: contents: read, pull-requests: read` (write 0, secret 0). PR body 는 env 경유만 (`run:` inline `${{ github.event.pull_request.body }}` 보간 금지 — shell injection 차단). 삭제된 1-W workflow (`c84fadf3:.github/workflows/orchestrator-spawn-prompt-fact-verify.yml:27` inline-interpolation injection 안티패턴 + `GH_TOKEN` secret fetch) 복제 금지 — S2/tier-downgrade-guard 의 env-injection + mktemp + python file-input 표준 답습.
- **§11.6 idempotency PASS** — pure presence-scan (동일 입력 동일 결과), registry / label-registry write = 1회성 declarative.
- **§11.1-§11.5 N/A** — governance document schema (append-only ratchet 지배, ADR-082 §결정 6 / ADR-008 §결정 2 / ADR-010 §결정 3), 데이터 schema 아님.
- **§7.3 auth / §7.5 민감데이터 N/A** — 인증 주체 0 / secret 0 / 입력 = repo-visible PR body.
- **보안 통제 신뢰 금지 (T5 수용)**: `[verified-via:` 위조로 우회 = presence-only lint 본질적 한계. warning-tier advisory 라 보안 게이트 아님. blocking 승격 시 위조 false-PASS 가 구조적 가능 → "보안 통제로 신뢰 금지" (blocking 승격 = 별도 follow-up CFP MUST, pattern_count >= 5 재발 trigger).
- **detect_command 단순형 유지** — `bash scripts/check-spawn-prompt-fact-verify.sh` (추가 인자 없이, resolver shell-operator 회피). FLAG 해소 메커니즘 = detect_command + workflow 실파일 실존 → carrier_absent False → FLAG 소멸 (Phase 2).

### §G. Wave 2 mechanical wire 산출물 (Phase 2 별 sub-CFP / 구현 lane)

`mechanical_enforcement_actions[]` `spawn-prompt-fact-verify` entry status flip = 본 Phase 1 binding (S1 F1 교훈 — 신규 lint carrier 면 binding 의무). Phase 2 actual wire (Epic CFP-2380 S3 Phase 2 구현 lane):

- `scripts/lib/check_spawn_prompt_fact_verify.py` (Python SSOT per ADR-061 — S2 구조 + C1-C5 PATTERNS 이식)
- `scripts/check-spawn-prompt-fact-verify.sh` (bash thin wrapper — env→mktemp→python file-input, trap cleanup)
- `.github/workflows/spawn-prompt-fact-verify.yml` (**single-root** — `templates/github-workflows/` 미사용 firsthand 확인 [verified: S2 도 single-root]; CONSUMER_ONLY_WORKFLOWS / invariant-check parity 불요. `pull_request` trigger + paths filter + permissions contents:read,pull-requests:read + env-injection)
- `scripts/test-check-spawn-prompt-fact-verify.sh` (discriminating test — S2 동형, fact category별 RED/GREEN 쌍 + FP guard 4종 + PER_BLOCK_SCAN_CAP=50 + window=5 경계 + empty PASS + setup exit2 + §B 1-W-잔재 message-assert + §C fenced 빈줄 fragmentation FP 경계)
- `docs/evidence-checks-registry.yaml` `spawn-prompt-fact-verify` detect_command·workflow 실파일 flip + status `deferred-followup`→`active` (warning-tier)
- `label-registry-v2` MINOR — `hotfix-bypass:spawn-prompt-fact-verify` (1-L) family member 추가 (≠ 1-W `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` — name 충돌 회피, primary-key disjoint) + MANIFEST.yaml version ratchet. kind:registry sibling sync 면제 (ADR-010 §결정 2). plugin.json bump 0 = marketplace_sync_declared: false (mirrored field 변경 0).

precedent 26-instance Wave 1→Wave 2 split chain established + S2 (Amendment 20 CFP-1559 → CFP-2382) 동형 직전 precedent.

### §H. Disjoint axis cross-ref

- ADR-082 sub-scope **1-L** (CFP-1590, Amendment 23) — 본 1-Z 의 declaration parent (1-L = mandate 정의, 1-Z = 그 Wave 2 mechanical enforcement wire SSOT). numeric-claim 1-K(declaration)↔1-N(Wave 2 wire) precedent 동형 pairing.
- ADR-082 sub-scope **1-W** (CFP-1842, Amendment 34) — Orchestrator→subagent axis (de-bloat 제거 유지, 복원 금지). 본 1-Z 가 그 C1-C5 PATTERNS 만 이식 (handoff axis 재작성, 부활 아님).
- ADR-082 sub-scope **1-K/1-N** (CFP-1601/CFP-1612, Amendment 22/25) — numeric-claim declaration→Wave 2 wire precedent 답습 (본 1-Z 가 동형 pairing).
- ADR-082 §결정 15 (Amendment 20, CFP-1559 — `issue-body-claim-pre-screen`) — S2, 본 1-Z 의 구조/FP guard/exit/test 답습 base (직전 동형 precedent CFP-2382).
- ADR-060 §결정 5 — warning mode first wire (presence-only, blocking 승격 별도 CFP).
- ADR-058 §결정 5 — sunset_justification N/A ratchet-up (Wave 2 enforcement 추가, scope 축소 0). ADR-064 §self-application top-down ratchet 정합.
- ADR-054 §결정 1 — Phase 1 doc-only fast-path 적격 (단일 PR, scripts/tests 무변경 — change-plan 면제). firsthand precedent: `ls docs/change-plans/ | grep -i 238x` → 0건 (CFP-2381/CFP-2382 change-plan 미작성 [verified]).
- paired sibling ADR-073 Amendment 不要 (sub-scope 1-Z = 1-L mechanical wire complement, worker→worker axis ≠ Orchestrator verify-before-assert axis — 1-N/1-P precedent 답습).

### §I. META self-application (recursive dogfooding)

본 Amendment 37 = sub-scope 1-Z 첫 적용 사례 = self:

- id ascending convention (§A Amd 36 1-Y) 적용 — `amendments[]` + `amendment_log[]` 양 block 모두 amendment_id 37 을 max(36) + 1 = 최하단 append. source command verify `grep -oE '^  - amendment_id: [0-9]+' archive/adr/ADR-082-write-time-self-write-verification-mandate.md | tail -1` actual = `amendment_id: 36` (Amd 36 CFP-1613 점유) → 정확 next-slot for CFP-2383 = 37 [verified].
- sub-scope letter = 1-Z (1-Y = CFP-1613 Amd 36 다음 sequential — amendment_id 37 ↔ sub-scope 1-Z, §B(Amd 36) 에 따라 동기는 보장이 아닌 본 case 의 사실).
- dual-block parity: 본 Amd 37 의 amendments[] + amendment_log[] + body `## Amendment 37` 3-block parity 보존 (Amd 32 sub-scope 1-U dual-block gate self-application 정합).
- 본 carrier 자체가 sub-scope 1-L (spawn prompt fact verify) 의 inherit-fact verify 를 dogfood — 본 Amendment 의 모든 수치 단언 (amendment_id 36/37 · label-registry v2.97 · FLAG 2건 · C1-C5 · S1/S2 precedent) firsthand verify 후 `[verified]` 표기 (추정 lock-in 0).

### §J. sunset_justification N/A 정당

is_transitional: false 보존. Amd 37 = 강화 방향 only (sub-scope 25→26 ratchet 확장 + 1-L Wave 2 mechanical enforcement wire codify). ADR-058 §결정 5 sunset_justification ratchet 통과 (forbid scope 확장, enforcement 추가). ADR-064 §self-application top-down ratchet 정합.

### §K. Related

- CFP-2383 carrier Story (Epic CFP-2380 S3)
- origin Issue: mclayer/plugin-codeforge#2383 (Epic CFP-2380 S3)
- CFP-2380 S1 deferred-followup-reconcile 게이트 (ADR-060 Amendment 18 §결정 32) — FLAG surface 동인
- ADR-082 Amendment 23 (sub-scope 1-L) — 본 1-Z 의 declaration parent
- ADR-082 Amendment 34 (sub-scope 1-W) — Orchestrator-side axis (C1-C5 PATTERNS source, de-bloat 제거 유지)
- ADR-082 Amendment 20 (sub-scope §결정 15, `issue-body-claim-pre-screen`) — S2 구조 base (CFP-2382 직전 precedent)
- ADR-082 Amendment 25 (sub-scope 1-N, `numeric-claim-write-time-verify`) — declaration→Wave 2 wire pairing precedent
- #2166 부분 close (잔여: 외부지식 source: annotation lint + 수치 측정방법 명기)
- deferral retain: retro-fact-verify-mandate (Amd 31/1-T) + fix-loop-reverify-mandate (Amd 29/1-R)
- ADR-054 §결정 1 — Phase 1 doc-only fast-path 적격 (단일 PR, scripts/tests 무변경 — change-plan 면제)

## Amendment 38 (2026-07-13 KST, CFP-2646) — §결정 16 신설 `resource_safety_claim_proof_presence` (governance/보안 tooling docstring·주석·워크플로 YAML 주석의 resource-safety/DoS-guard 안전성-claim → paired proof-reference OR honest-ceiling presence write-time 정직 discipline — write-time verify super-class 3번째 presence-lint carrier)

> **honesty-ceiling 자기적용 선언 (본 Amendment 전체 상속 — ADR-151 §결정7)**: 본 Amendment 이 신설하는 discipline·lint 은 안전성-claim 이 **증거를 동반하는지(presence)** 만 검사한다. claim 의 **참됨(truth)** 은 정적 도구로 증명 불가 — 본 Amendment 은 over-claim 을 "봉인/완전방지" 하지 **않는다**. lint 은 claim-without-any-proof-link 를 **작성 시점에 좌향 노출**할 뿐이다. `presence ≠ truth`. detection(보안테스트 execution-backed probe) 존치.

### §A. 컨텍스트 (원천 + obviation)

원천 = CFP-2635 retro escalate_user 후보 A. PMO cross-Story pattern_count 2 (ADR-045 §D-9 forcing function):

| CFP | 자기주장(over-claim) | 실제 결함 | 검출 lane | evidence (firsthand) |
|---|---|---|---|---|
| CFP-2635 | docstring "catastrophic backtracking 0" / "resource exhaustion 방어" / "per-file scan cap = DoS 가드" | `_leading_token` slice-in-loop + per-line length 미bound = O(n²) (1.5MB 단일라인 >60s) | 보안테스트 FIX SF-1 | `scripts/lib/check_shell_test_masking.py:30` (SF-1 정정 커밋 verbatim) |
| CFP-2591 | 주석 "nested quantifier 0" (ReDoS-safe 자칭) | `_RE_ALLOW_COUNTERFACTUAL` sequential unbounded `.*` 2연속 = quadratic backtracking (64KB=6.3s) | 보안테스트 P2 ReDoS FIX | `git show 9c13ebbc` ("nested quantifier 0" 자칭 정정, anti-theater) |

도메인 본질 = **자기참조 정직 갭** — over-claim/false-coverage 를 잡는 dogfood governance tool 이 자기 docstring/주석에서 동종 over-claim 을 내고, 보안테스트 lane 이 write **후** 늦게 catch(좌향 실패).

obviation (Story §2.1 요구사항리뷰 3-way CONFIRM): ethos(ADR-119 research-before-claims) = 조사 범위 내 커버(단 declarative-only + agent 발화 축, write-time docstring artifact 축 미명명) / detection(보안테스트 execution-backed probe) = 유효(2/2 catch, 단 좌향 실패) / ceiling(ADR-151 §결정7) = 상속 SSOT. **잔여 = write-time 정직 forcing 부재(registry 0건)**. → 신규 mechanism CLASS 아닌 **§결정 15/§결정 11 presence-lint 패턴의 artifact-class 확장**으로 충당.

### §B. §결정 16 (신설) — resource-safety-claim ↔ proof-link write-time 정직 discipline

**Mandate**: governance/보안 tooling(evidence-check 게이트·보안 script·워크플로 YAML)의 **docstring + inline 주석 + 보안 workflow YAML 주석**에 resource-safety/복잡도/DoS-guard 안전성-claim(closed-set: catastrophic backtracking 0 / ReDoS-safe / ReDoS-free / DoS 가드 / resource exhaustion 방어 / scan cap = 총 작업량 bound / nested quantifier 0 / injection-safe 정적 안전성 단정 류)을 쓸 때, 작성 주체는 (a) **paired proof-reference**(reproducer / wall-clock 벤치마크 / 복잡도 회귀 self-test 링크) 동반, **또는** (b) **honest-ceiling**('bounded degradation, 임의 입력 무해 아님') downgrade 를 수행한다. 무증거 안전성 단정 금지.

**2-layer 착지** (ADR-140 §결정3 hybrid — dev declare → review falsify):
- **Layer 1 (행위 mandate, AC-1a declared)**: write-time declaration mandate — roster/skill prose(작성 주체 = SecurityArchitectAgent / DeveloperAgent / QADeveloperAgent / InfraEngineerAgent). 행위(정직하게 쓰는가)는 **정적 계측 불가** → declaration + 리뷰(설계/구현/보안) falsify.
- **Layer 2 (artifact presence lint, AC-1b normative warning-tier)**: presence lint 5-piece chain 이 안전성-claim ↔ paired proof-ref/ceiling 의 **presence** 를 정적 검사. claim 감지 + proof-ref/ceiling 둘 다 부재 → FLAG.

**mechanism = §결정 15/§결정 11 presence-lint 답습** (신규 CLASS 아님):
- claim 검출: **affirmative-context closed-set 매칭** — `check-tier-honesty.py:8-9,57-58`(긍정 enforcement 토큰 closed-set 만 매칭, 정직한 부정 서술 미매칭, 단순 grep 금지) 기법 답습. denial('... 아님')·정의부 자기열거·정책 열거 문맥 EXEMPT.
- evidence presence: 동일 파일 claim-adjacent scan → proof-ref closed-set OR ceiling closed-set presence. `check_issue_body_claim_pre_screen.py:51,54,70`(PER_FILE_SCAN_CAP + ANNOTATION_MARKER 정적 substring + code-span/fenced/blockquote EXEMPT guard) 구조 답습.
- grandfather: `docs/resource-safety-claim-baseline.yaml` new-only subtract(legacy 27-file 동결 — `deferred-followup-baseline.yaml` 형틀). 신규 over-claim 만 surface.

**honesty-ceiling(ADR-151 §결정7 상속, verify ⊋ presence disjoint)**: lint 은 proof-ref/ceiling **presence** 만 검사 — claim **참됨** 미강제(claim-without-any-proof-link 만 좌향 노출, 불완전 proof 는 PASS). "over-claim 완전 봉인" hard-claim 금지.

**5-piece chain** (Phase 2 mechanical wire, CFP-2635 ADR-060 Amd 22 동형):
1. Python SSOT `scripts/lib/check_resource_safety_claim_proof.py`
2. thin wrapper `scripts/check-resource-safety-claim-proof.sh` (ADR-061 §결정1 python3 exec forward)
3. byte-identical workflow pair `{templates/github-workflows,.github/workflows}/resource-safety-claim-proof-presence.yml` (ADR-005 sha256, `on: pull_request`[NOT pull_request_target] + `permissions: contents:read`(+pull-requests:write comment) + `runs-on: ${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '["ubuntu-latest"]') }}` self-hosted, injection-safe env-only)
4. discriminating self-test `tests/scripts/test_check-resource-safety-claim-proof.sh`
5. registry warning-tier entry `resource-safety-claim-proof-presence` + `hotfix-bypass:resource-safety-claim-proof-presence`(label-registry MINOR)

### §C. ★ 자기참조 DoS 회피 (메타-재귀 — CFP-2635 O(n²) 교훈 필수 반영)

본 lint 도 파일 내용을 regex 스캔한다 = **CFP-2635 SF-1 과 동일 표면**. CFP-2635 는 위협 축 enumeration 에서 **algorithmic-complexity 축(T-2) + line-length 축(T-3) 을 누락**해 O(n²) DoS 를 품었다. 본 §결정 16 lint 은 4-axis bound 를 **처음부터**(사후 정정 아닌 born-safe) 배선한다:

| 축 | 위협 | 완화 (born-safe) |
|---|---|---|
| T-1 regex backtracking | nested quantifier catastrophic backtracking | 전 regex anchored + bounded quantifier, **nested quantifier 0**, closed-set 리터럴 substring 우선 |
| **T-2 algorithmic-complexity** (★ CFP-2635 누락) | slice-in-loop `t = t[m.end():]` = O(n²) | **index-advance O(n)** tokenize (`re.match(t, pos)` offset 전진, slice 재복사 0) — `check_shell_test_masking.py:235-252` / `check_spawn_prompt_fact_verify.py` 답습. claim-adjacent scan window bounded |
| **T-3 line-length** (★ CFP-2635 누락, count-cap 별개 축) | arbitrary 길이 단일라인(1.5MB) → 라인-길이 의존 경로 총 작업량 미bound | **`MAX_PHYSICAL_LINE_LEN` per-physical-line truncate-scan** — `PER_FILE_SCAN_CAP` count-cap 과 **별개 축**. CFP-2635 SF-1 이 정확히 이 축 부재로 O(n²) |
| T-4 read-path | 병리적 다행 파일 unbounded read | `itertools.islice(f, PER_FILE_SCAN_CAP)` 라인 count bound. 총 작업량 ≤ cap × line-len 유한 bound |

**자기 docstring 정직**: 본 lint 의 docstring/주석은 자기 resource-safety 를 over-claim 하지 않는다 — 완화는 CPU/메모리 총 작업량 bound 이지 "임의 입력 무해" 가 아님(bounded degradation, `check_shell_test_masking.py:39` 상속). "catastrophic backtracking 0" 서술 옆에 proof-reference(self-test ReDoS/O(n²) 회귀가드 test 경로) 동반 → **이 lint 의 docstring 자체가 자기 lint 을 통과**(AC-3 self-application).

### §D. A2-5 판정 — 신규 ADR 아님 (ADR-082 Amendment 정합)

- ADR-082 = write-time self-write verify super-class(본질 선언 `:676` "작성한 값 자체가 사실과 일치하는가 verify 후 write").
- **§결정 11** 이 이미 super-class 를 **code-level artifact write-time**(test binding / script error visibility)로 확장 — 코드 artifact write-time discipline 선례.
- **§결정 15** 가 이미 **claim closed-set → paired annotation presence lint**(issue-body-claim-pre-screen) mechanism 확립 — presence-lint carrier.
- disjoint 축 우려(verify ⊋ presence) 는 **ADR-082 안에서 이미 해소** — 기존 carrier(issue-body / spawn-prompt-fact-verify)도 presence-lint(full verify 아님)이며 presence = verify 의 honesty-ceiling 기계 floor. → 본 §결정 16 = **3번째 sibling presence-lint carrier**(새 claim class = resource-safety/DoS-guard, 새 artifact class = docstring/주석/workflow YAML) + ADR-151 ceiling 명시 상속 = **신규 mechanism CLASS 아님 → Amendment 정합**(신규 ADR = over-fragmentation).
- 흡수 기각 대안: ADR-119 §결정 specialize(declarative-only + 발화 축 → artifact 축 미명명) / ADR-140 amendment(subject = 리팩터링 hygiene disjoint, 자기모순 기각 선례 동형) / ADR-151 AC-7 확장(execution-liveness ⊥ docstring-claim disjoint, 상속만) — 3 대안 모두 subject/axis disjoint → 기각. **ADR-082 = 최근접 home**.
- atomic claim: 신규 ADR 아니므로 ADR-number OCC 불요. Amendment 38 = id ascending(max=37 firsthand → next=38). Orchestrator commit-time max+1 재검증 의무(병렬세션 reslot 대비, META-self-application §결정 10.D 관례).

### §E. Wave split (Phase 1 / Phase 2)

- **Phase 1 PR** (internal-docs #1908): 본 Amendment(ADR-082 §결정 16) + write-time mandate roster/skill prose(Layer 1) + registry declarative anchor(`mechanical_enforcement_actions[]` resource-safety-claim-proof-presence status flip) + change-plan(`wrapper/change-plans/cfp-2646-resource-safety-claim-proof-lint.md`) + Story §3/§7 + named carrier declare.
- **Phase 2 PR**: 5-piece mechanical wire(Layer 2 lint + self-test + workflow + grandfather baseline) + registry status Active + label-registry MINOR + plugin.json MINOR(신규 evidence-check capability).
- tier = warning(ADR-060 §결정5, continue-on-error, PR merge 무차단). **blocking 승격**(FP 실측 = ADR-060 evidence-gate 통과 후) + 정책문서 표면 over-claim sweep + consumer 전파 = **별도 named carrier**(`CFP-TBD` 금지 — deferral-carrier-declared no-TBD lint 대상).

### §F. Related

- CFP-2646 carrier Story (Phase 1 PR = internal-docs #1908)
- origin: mclayer/plugin-codeforge#2646 (원천 CFP-2635 retro escalate_user 후보 A)
- ADR-082 §결정 15 (Amendment 20, `issue-body-claim-pre-screen`, CFP-1559→CFP-2382) — presence-lint 구조 형틀 (P-1)
- ADR-082 §결정 11 (Amendment 9) — code-level artifact write-time discipline 선례
- ADR-144 §결정 7 (`check-tier-honesty.py`, CFP-2573) — affirmative-context closed-set 매칭 precision 기법 (P-2)
- ADR-060 Amendment 22 (CFP-2635 `shell-test-exit-masking-detect`) — 5-piece chain 동형 + DoS-safe skeleton (P-3), 원천 over-claim 실사례 1
- ADR-151 §결정 7 (honesty-ceiling) — presence ≠ truth 상한 SSOT (상속)
- ADR-119 (research-before-claims) — ethos super-class (조사 범위 커버, write-time artifact 축 미명명)
- ADR-140 §결정 3 (write-time hygiene hybrid 착지) — Layer 1 declaration mandate 형틀
- ADR-045 §D-9 — pattern_count 2 escalate_user forcing function (원천)
- ADR-054 §결정 1 — Phase 1 doc-only fast-path **부적격** (Phase 2 script/workflow/test wire 有 — change-plan 작성, CFP-2635 5-piece 선례 동형)
