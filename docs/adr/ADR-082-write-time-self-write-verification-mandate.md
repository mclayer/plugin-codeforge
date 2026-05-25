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
    summary: "§결정 1 layer 1 sub-scope (1-H) 신설 — Orchestrator self-write §10 FIX Ledger row resolution field claim source/evidence verify mandate. §10 FIX Ledger = Orchestrator monopoly (fix-event-v1 contract, CFP-32) — 기존 sub-scope (1-A cross-repo state verify / 1-B Issue body authorship / 1-C user-utterance verbatim / 1-D cross-repo label-write authority / 1-E spawn prompt SHA-anchor pre-spawn pin / 1-F mid-spawn periodic origin re-pin / 1-G amendment-slot pre-reservation) 7종 외 codify gap closure. 4 의무: (a) Orchestrator 가 §10 FIX Ledger row resolution field 작성 시 인용 source / evidence (예: 'wrap 실행 완료, advisory 0 verified' / 'lint EXIT_CODE=0 verified' / 'grep count N verified') 가 실 실행 결과인지 write-time verify 의무 (b) measurable evidence (file path 인용 + grep count + lint exit code + diff hash 등) 가 claim 안 명시되면 해당 evidence source 가 실 검증된 결과인지 verify-via direct execution 의무 (cached/inferred 사용 금지) (c) resolution field 안 verified-via annotation (예: `verified-via: Read <path> + grep count = N + exit code = 0`) 의무 (write-time semantic truth 정합) (d) wrap-style 자동화 영역 (예: idempotent Python script 실행 후 verify) = 실 실행 결과 stdout / exit code / grep diff 확인 후 작성 의무. 본 sub-scope 1-H = sub-scope 1-A/1-B/1-C/1-D/1-E/1-F/1-G 와 disjoint axis (Orchestrator monopoly §10 FIX Ledger resolution field write-time semantic truth verify axis — fix-event-v1 contract level write authority 영역의 source-claim verify mandate). 동인 = CFP-1316 retro F2 Optional carrier — CFP-1316 iter 1 §10 FIX Ledger row resolution field 작성 시 'CHANGELOG.md 45 occurrence mirrored field wrap (Python idempotent script 실행 완료, advisory 0 verified)' claim 영역 = Orchestrator self-write monopoly 영역 의 ADR-082 §결정 1 layer 1 sub-scope 명시적 codify 부재 risk pattern. wrap 미실행 영역에서 작성됐다면 false declare = §결정 1 layer 1 위배 (sub-scope 1-A~1-G 와 disjoint axis pattern). 본 Amendment 18 가 (1-H) 로 명시 codify. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `fix-ledger-resolution-source-verify` warning-tier deferred-followup — fix-event-v1 contract emit-time pre-check pattern, S6 별 sub-CFP carrier). Wave 2 mechanical lint = 별 CFP carrier (deferred-followup, ADR-082 §결정 6 retain pattern 답습). doc-only fast-path ADR-054 Cat 1 단일 PR (script / workflow / bats wire 0건). minimal-applicability: §10 FIX Ledger resolution field write monopoly 영역 = Orchestrator only (CFP-32, fix-event-v1 contract) — lane agent / PL agent / chief author 영역 0 (sub-scope (1-B) 일반 lane agent self-write 와 disjoint axis). 본 Amendment 18 자체가 META-self-applied (§결정 10.D 13th applied case): 본 Amendment 번호(18) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main 11bf2d95e47be364438cc293812f6066dc07ed0f max=17 — CFP-1341 Amd 17 merge 후 base, 정확 next-slot = 18) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-25 KST 기준 origin/main 11bf2d95 pinned_at: 11bf2d95). ADR-RESERVATION amendments_reserved[] row pre-append 완료 (adr_number 82 amendment_id 18 reserved_by_cfp CFP-1342 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope (1-G) pre-reservation strict claim mandate META 1st applied case."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G) → (1-H Orchestrator §10 FIX Ledger resolution field claim source/evidence verify) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. META-self-applied (§결정 10.D 13th applied case + Amendment 17 sub-scope 1-G pre-reservation strict claim mandate 1st applied case)."
  - amendment_id: 21
    carrier_story: CFP-1578
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-J) 신설 — cross-repo worktree target authority verify mandate. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint — content verify vs target authority verify, 동시 발의 race). 본 Amendment 21 = worktree mis-target 첫 catch carrier (CFP-1539+CFP-1540 batch retro §4.1 #2 mandatory follow-up). 4-tuple primitive: (a) chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 worktree target authority verify-before-write 의무 — `git -C <worktree_abs_path> remote -v` 실행하여 expected repo (예: wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 확인 / (b) spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 명시 (write-target authority anchor block — sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block + sub-scope 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습) / (c) cross-repo 작업 sequence 시 명시적 worktree switch 의무 — wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별 worktree 분리, ADR-040 worktree convention 정합) / (d) verified-via annotation — spawn prompt 안 `worktree_target_authority_verified: <bool>` field 의무 명시. 본 sub-scope 1-J = sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) / 1-E (spawn prompt SHA-anchor) / 1-F (spawn-internal periodic drift) / 1-G (amendment-slot pre-reservation) / 1-H (Orchestrator §10 FIX Ledger resolution field source/evidence) / 1-I (pre-spawn-prompt-finalize) 와 disjoint axis (cross-repo worktree target authority axis — wrapper plugin-codeforge ↔ internal-docs cross-repo write-target boundary, 1-D cross-repo label-write authority 와 가장 인접하나 verify 대상 disjoint: 1-D label-write authority vs 1-J worktree write-target authority). 동인 = CFP-1539+CFP-1540 batch retro §4.1 #2 (PMOAgent retro spawn 시 internal-docs PR target 작성 시 wrapper repo plugin-codeforge worktree 안에서 git worktree add 시도 후 정정 발생 — wrapper repo worktree mis-target 첫 catch occurrence). ADR-013 dogfood-out internal-docs SSOT path + ADR-040 worktree convention 정합 영역 codify 부재 super-class gap closure. RequirementsPL verdict Alternative C 채택 (Issue #1578 out-of-scope `ADR 신설` = new ADR file scope, ADR-082 sub-scope Amendment 영역과 disjoint axis — sub-scope 신설로 ADR Amendment 영역 적합). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `worktree-target-authority-verify` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 Wave 1→Wave 2 split precedent 답습). 본 Amendment 21 자체가 META-self-applied (§결정 10.D 16th applied case): 본 Amendment 번호(21) 가 target ADR-082 frontmatter `amendments:` Read verify (worktree HEAD 4000440 origin/main amendments[] max=19 — CFP-FU-A Amd 19 merge 후 base + paired sibling CFP-1559 Amd 20 pre-claim gating → 정확 next-slot for CFP-1578 = 21) 후 결정. ADR-RESERVATION amendments_reserved[] row pre-append 완료 (adr_number 82 amendment_id 21 reserved_by_cfp CFP-1578 reservation_date 2026-05-25 KST status active) — Amendment 17 sub-scope 1-G pre-reservation strict claim mandate META 2nd applied case (Amendment 18 CFP-1342 1st applied case 직전 precedent 답습)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I) → (1-J cross-repo worktree target authority verify) 확장). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. META-self-applied (§결정 10.D 16th applied case)."
  - amendment_id: 19
    carrier_story: CFP-FU-A
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-I) 신설 — pre-spawn-prompt-finalize verify layer mandate. Parallel session race 11th occurrence (CFP-1420 Sub-A S1.2 STAND_DOWN_DUPLICATE per PR #1441 prior merge 2026-05-24T03:07:53Z) escalate_user pattern_count 11 ≫ ADR-045 §D-9 threshold 2 Mandatory escalation 산물 + 12th meta-occurrence (CFP-1342 ADR-082 Amd 18 + sub-scope 1-H collision detected during pre-merge window of THIS Story PR #1527 post-open, recovery via renumber Amd 18→19 + sub-scope 1-H→1-I + 4-file cross-ref rebase on origin/main HEAD ca1c20e — recursive dogfooding evidence for #1476 sub-decisions 1+2+3 race window 영역 직접 reproduce: worktree create T0 → spawn prompt finalize T1 → ArchitectAgent commit T2 → ~30-60s gap → CFP-1342 merge T3 → PR #1527 open T4 → collision T5 → recovery T6) — sub-decision 3 (Race condition window 단축) carrier within CFP-FU-A. paired sibling = ADR-073 Amendment 13 (sub-decision 1 polling cadence 1→3, 12+13번째 transition trigger entries `pre_git_operation` + `pre_push`) + ADR-073 Amendment 14 (sub-decision 2 OR→AND composition layer §결정 1-P primitive AND aggregate) = 3 ADR Amendment 동시 발의 axis disjoint complement 3-set (event timing cadence + composition layer + window narrowing), ADR-064 §결정 1 CFP scope unitary 정합. 4-tuple primitive: (a) pre-spawn-prompt-finalize verify mandate — worktree create 후 spawn prompt content 작성 직전 (즉 `git worktree add` 완료 timestamp ~ `[USER-UTTERANCE-VERBATIM]` block emit timestamp 안 window ~30-60s) 1회 추가 polling 의무 (b) 3-source 동시 invoke + AND aggregate verify — `git fetch origin main --quiet` + `gh issue list --search` + `gh pr list --search \"head:<branch>\"` 3-source 동시 invoke + 모두 PASS verify (sub-decision 2 AND composition layer 정합) (c) race window ~30-60s 단축 mandate — worktree create timestamp ~ spawn prompt emit timestamp 안 polling 1회 의무 binding (d) verified-via annotation — spawn prompt 안 `pre_spawn_prompt_finalize_verified: <bool>` field 의무 명시. 본 sub-scope 1-I = sub-scope 1-A / 1-B / 1-C / 1-D / 1-E / 1-F / 1-G / 1-H 와 disjoint axis (pre-spawn-prompt-finalize window verify axis — spawn prompt finalize 직전 window 영역, Amd 15 1-E spawn-time SHA fetch 시점 + Amd 16 1-F mid-spawn drift 시점 + Amd 18 1-H Orchestrator §10 FIX Ledger resolution field source/evidence verify 와 disjoint complement). Amd 15 (1-E pre-spawn pin) = spawn-time SHA fetch 시점만 cover, Amd 16 (1-F mid-spawn drift) = spawn-internal periodic check 만 cover, Amd 18 (1-H) = Orchestrator FIX Ledger resolution field self-write verify 만 cover (Orchestrator monopoly axis), 본 Amd 19 (1-I) = chief author spawn pre-prompt-finalize window covered (worktree create 후 ~ spawn prompt finalize 직전, ArchitectAgent / chief author / deputy spawn 영역) = 4-layer temporal defense forcing function 완결 (pre-spawn-fetch + pre-spawn-prompt-finalize + mid-spawn-periodic + Orchestrator §10 source-claim). ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent + sub-scope 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습 (spawn-time anchor block normative pattern 동형). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `pre-spawn-prompt-finalize-verify` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 Wave 1→Wave 2 split precedent 답습). 본 Amendment 19 자체가 META-self-applied (§결정 10.D 14th applied case + collision recovery 1st applied case): 본 Amendment 번호(19) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main ca1c20eefd3f3db35a85604ec320f8f6cb2919ff max=18 — CFP-1342 Amd 18 merge 후 base post-CFP-1343 fetch verified, 정확 next-slot = 19) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-25 KST 기준 origin/main HEAD ca1c20e post-collision-recovery rebase)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H) → (1-I pre-spawn-prompt-finalize verify layer) 확장). ADR-064 §결정 7 symmetric evidence-gated 정합. parallel session race 11th occurrence escalate_user pattern_count 11 ≫ threshold 2 Mandatory ADR-045 §D-9 산물 + 12th meta-occurrence (CFP-1342 collision recovery in-flight). META-self-applied (§결정 10.D 14th applied case + collision recovery 1st applied case)."
  - amendment_id: 20
    carrier_story: CFP-1559
    date: 2026-05-25
    summary: "§결정 15 신설 — Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate. 4 sub-pattern closed-set enumeration: (a) PR #NNNN merge state (CLOSED/MERGED stale) — Issue body author 가 sibling PR state mention 시 stale 가능 (b) CFP-NNNN MERGED/CLOSED state stale — Issue body author 가 sibling CFP state mention 시 stale 가능 (c) count number stale — 'X VIOLATIONs' / 'Y defect' / 'pattern_count Z' 등 quantitative count cite 시 verify-after-the-fact 시 obsolete (d) sister carrier origin claim stale — 'CFP-NNNN carrier' / 'sibling CFP-NNNN' 등 sister origin attribution 시 실제 다른 carrier 영역. 본 Amendment 20 = super-class scope (Issue body content 영역 broader stale-reference pattern). CFP-1216 Phase 2 wired `amendment-number-frontmatter-verify` lint (sub-class — ADR-NNN Amd M regex citation only) extension super-class declarative anchor. paired sibling CFP-1558 = amendment-number sub-class declarative ratchet (axis disjoint, 본 ADR Amendment 21 점유 예정 chronologically — CFP-1559 발의 first, CFP-1558 = Amendment 21 sequential allocation). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `issue-body-claim-pre-screen` warning-tier deferred-followup append). Wave 2 mechanical wire (`scripts/lib/check_issue_body_claim_pre_screen.py` Python SSOT per ADR-061 + `scripts/check-issue-body-claim-pre-screen.sh` bash thin wrapper + `templates/github-workflows/issue-body-claim-pre-screen.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-issue-body-claim-pre-screen.bats` fixture RED→GREEN stash proof per ADR-082 §결정 11.A + ContinuityAgent agent file cross-plugin sync ADR-010) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split precedent 답습). pattern_count 7+ reach Mandatory ADR-045 §D-9 escalation 산물: CFP-FU-B Issue #1477 5-defect 3 PIVOT (#2 description text stale / #4 count '4 VIOLATIONs' stale / #5 origin claim 'CFP-1303' stale = 60% stale rate) + CFP-1041/1050 RequirementsPL spawn packet stale claim lineage 4 evidence trail = 합산 ≥ 7 reach. ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated ratchet 강화 방향 정합. False-positive 완화 guards (code-span EXEMPT / quoted-text EXEMPT / templates/** EXEMPT / docs/stories/§9 transcript EXEMPT) = Wave 2 lint design 시 결정 — Phase 1 declarative scope 외. ContinuityAgent verify-before-trust 8-tuple matrix scope expansion (RequirementsPL spawn prompt `issue_body_pre_screen_warnings` field 추가) = Wave 2 cross-plugin ADR-010 sibling sync 시점. axis disjoint with sister carriers CFP-1437/1436/1497 3-layer defense (spawn lifecycle axis) — 본 Amendment 20 = Issue body content verify-before-trust write-time axis (lifecycle 단계 비교: 본 Amd 20 = Issue body authored 시점 / CFP-1437 Amd 15 = chief author spawn-time SHA pin / CFP-1436 Amd 16 = spawn-internal periodic / CFP-1435 Amd 17 = amendment slot reservation lifecycle / CFP-1342 Amd 18 = Orchestrator §10 FIX Ledger source-claim / CFP-FU-A Amd 19 = pre-spawn-prompt-finalize window). 본 Amendment 20 자체가 META-self-applied (§결정 10.D 15th applied case): 본 Amendment 번호(20) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main HEAD `4000440ee2c31c35b042dd0e5220be5c2f3aaefd` max=19 — CFP-FU-A Amd 19 merge 후 base, 정확 next-slot = 20) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-25 KST 기준 origin/main HEAD 4000440 post-CFP-FU-A merge 11bf2d95→ca1c20e→4000440 fetch verified) + ADR-082 Amendment 17 §결정 1-G strict claim mandate 2nd applied case (chief author body write 전 ADR-RESERVATION row pre-append + commit + push 완료 verified)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: ADR-082 super-class scope (Issue body authorship verify Amendment 2 §결정 1 layer 1 sub-scope 1-A) → Issue body content broader stale-claim super-class (4 sub-pattern enumeration: PR merge state / CFP merge state / count number / sister carrier origin) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 15 = 7 reach (CFP-FU-B 3 PIVOT + CFP-1041/1050 lineage 4). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 15th applied case + Amendment 17 §결정 1-G strict claim mandate 2nd applied case after CFP-1492)."
  - amendment_id: 22
    carrier_story: CFP-1601
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-K) 신설 — numeric claim write-time strict claim mandate. ArchitectAgent (chief author) / Orchestrator (spawn packet) / lane PL write-time 영역 안 numeric claim (line count / file count / API count / pattern_count / commit count / row count — 6 closed-set numeric claim dimensions) 의 source command / actual value / claim↔actual cross-verify 4-step write-time strict mandate. 동인 = ADR-045 §D-9 Mandatory escalation 산물 (CFP-1571 §3.2 line count drift '+93→+101' 3 location 정정 + CFP-1581 §3.2 file count drift '10→14' actual, pattern_count 2 reach forcing function 활성). axis disjoint: Amendment 17 §결정 1-G (amendment-slot row append scope) + Amendment 20 §결정 15 (Issue body 4 sub-pattern content scope — PR merge state / CFP state / count cite / sister carrier origin) — 본 Amendment 22 = write-time governance docs (ADR text / Change Plan / Story / spawn packet wording / Issue body) 안 numeric claim source/value strict claim mandate, axis 인접 (1-G row append axis 와 슬롯 reservation lifecycle 공유 / 1-J cross-repo worktree target authority axis 와 별 mechanism). 4-step verify-before-write mandate: (a) source command identify — claim 의 ground truth source command 명시 의무 (예: `grep -c '^  - amendment_id:' <file>` / `wc -l <file>` / `git diff --shortstat` / `find <dir> -name '*.md' | wc -l`) (b) direct execute — 작성 직전 source command 실행 + actual value 획득 의무 (cached value / 추정 / planning-time stale value 사용 금지) (c) claim↔actual cross-verify — claim value 와 actual value 1:1 일치 verify (semantic ambiguity (예: `grep -c` line-occurrence count vs YAML max amendment_id slot semantic) 발견 시 source command 정밀화 의무) (d) write only on match — match 시에만 write, mismatch 시 abort + Orchestrator escalate. 본 sub-scope 1-K = sub-scope 1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J 와 disjoint axis (numeric claim source/value strict claim axis — claim 의 quantitative ground truth verify-before-write). Numeric claim closed-set 6종 enumeration: (i) line count (file line count / patch line count) (ii) file count (touched file count / dir file count) (iii) API count (mcp__github__* call count / agent spawn count) (iv) pattern_count (cross-Story pattern repetition count, ADR-045 §D-9 base) (v) commit count (commits-behind / commits-ahead) (vi) row count (yaml row / md table row / contract field). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `numeric-claim-write-time-verify` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435/1559/1578 Wave 1→Wave 2 split precedent 답습). 본 Amendment 22 자체가 META-self-applied (§결정 10.D 17th applied case + numeric-claim verify-before-write 1st applied case META first applied): 본 Amendment 번호(22) 가 target ADR-082 frontmatter `amendments:` Read verify (worktree HEAD 0a19e6a origin/main amendments[] max=21 — CFP-1578 Amd 21 merge 후 base, 정확 next-slot = 22) 후 결정 + spawn packet `amendments[] count = 21` claim 의 source command `grep -c '^  - amendment_id:' <file>` actual result = 41 (line occurrence count) vs semantic intent (max amendment_id slot) divergence 직접 발견 = numeric-claim source command 의 정밀화 의무 4-step (b)(c) 의 1st applied empirical evidence — recursive dogfooding self-evidence (spawn packet 자체 안 numeric claim ambiguity catch). ADR-082 Amendment 17 §결정 1-G strict pre-reservation mandate META 3rd applied case (ADR-RESERVATION amendments_reserved[] row 82 amendment_id 22 reserved_by_cfp CFP-1601 reservation_date 2026-05-25 KST status active pre-append 의무 충족)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J) → (1-K numeric claim write-time strict claim mandate) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 layer 1 sub-scope 1-K = 2 reach (CFP-1571 §3.2 line count drift +93→+101 3 location 정정 + CFP-1581 §3.2 file count drift 10→14 actual = pattern_count 2 ≥ ADR-045 §D-9 threshold 2 Mandatory escalation 산물). is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 17th applied case + numeric-claim verify-before-write 1st applied case META first applied: spawn packet 자체 안 numeric claim source command result divergence 직접 catch — recursive dogfooding self-evidence)."
  - amendment_id: 23
    carrier_story: CFP-1590
    date: 2026-05-25
    summary: "§결정 1 layer 1 sub-scope (1-L) 신설 — spawn prompt fact verify-before-trust mandate (upstream-inherited stale fact carrier super-class). axis disjoint from 1-A (cross-repo state) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim block 형식 의무 Amd 5) / 1-D (cross-repo label-write authority Amd 14) / 1-E (PRE-SPAWN-ORIGIN-MAIN-SHA pre-spawn pin Amd 15) / 1-F (mid-spawn periodic origin re-pin Amd 16) / 1-G (amendment-slot pre-reservation strict claim Amd 17) / 1-H (Orchestrator §10 FIX Ledger resolution source/evidence Amd 18) / 1-I (pre-spawn-prompt-finalize window race shortening Amd 19) / 1-J (cross-repo worktree target authority Amd 21) / 1-K (numeric claim write-time strict claim mandate Amd 22 CFP-1601). 본 sub-scope 1-L = spawn prompt content 안 인용 fact (numeric claim / state claim / count claim / sister carrier carrier_story claim) 의 **upstream-inherited fact verify axis** — Orchestrator 또는 chief author 가 spawn prompt 작성 시 사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file 로부터 inherit 된 fact 를 직접 verify 의무 (cached / synthesized / inherited-without-verify 사용 금지). Amd 5 (1-C user-utterance verbatim block 의무) 와 axis 인접하나 disjoint complement: 1-C = 사용자 발화 content 전달 형식 verbatim 의무 (block 형식 axis, content 변조 차단), 1-L = 인용된 fact 자체의 truthfulness verify (content fact verify axis, stale inheritance 차단). Amd 20 (§결정 15 Issue body stale-claim super-class write-time pre-screen, 4 sub-pattern a-d) 와 axis 인접하나 disjoint complement: Amd 20 = self-write content stale claim 영역 (Issue body author 자기 작성 content 안 stale claim, 작성자 책임 write-time pre-screen), 1-L = upstream-inherited stale fact 영역 (spawn prompt 작성 시 upstream source 로부터 inherit 된 fact, synthesizer / Orchestrator / chief author 책임 spawn-time verify). Amd 22 (1-K numeric claim write-time strict claim mandate CFP-1601) 와 axis 인접하나 disjoint complement: Amd 22 1-K = own author write-time 안 numeric claim source/value strict verify (6-dimension closed-set line/file/API/pattern/commit/row count), 1-L = spawn prompt 안 upstream source 로부터 inherit 된 fact 자체 verify (numeric 영역 외 state / sister carrier / count / wording claim 포함). 4-tuple primitive: (a) **upstream-inherited fact 식별 의무** — spawn prompt 안 인용 numeric / state / count / sister carrier claim 이 (i) 사용자 발화 (ii) sibling Issue body (iii) sister PR commit message (iv) 별 carrier retro file 로부터 inherit 된 경우 식별 / (b) **direct source verify 의무** — verify source 명시 + 직접 fetch 의무: `verified-via: <gh issue view N --json body | gh pr view N --json commits | Read <file_path> | git show <SHA>:<path>>` annotation spawn prompt 안 명시 (cached / synthesized 사용 금지) / (c) **stale 검출 시 정정 declare** — verify 결과 stale 검출 시 spawn prompt 안 fact 정정 + `[fact-correction: <claim> stale, verified <correct-value>, source: <verify-source>]` marker 의무 명시 / (d) **verified-via annotation field 의무** — spawn prompt 안 `spawn_prompt_fact_verified: <bool>` field 명시 (write-time semantic truth verify). 본 sub-scope 1-L = 4-layer temporal defense (Amd 15 pre-spawn-fetch + Amd 19 pre-spawn-prompt-finalize + Amd 16 mid-spawn-periodic + Amd 18 Orchestrator §10 source-claim) 의 **content fact axis 5th layer** 신설 — temporal axis 와 disjoint (when verify) vs (what verify): 1-L = spawn prompt 안 인용 fact content 자체의 truthfulness verify axis. 동인 = CFP-1590 ADR-045 §D-9 Mandatory escalation pattern_count 3 reach (PMOAgent CFP-1523 retro carry-over): **occurrence 1** = CFP-1493 S2.3 PR #1520 commit message stale defer 사유 inheritance ('284 MCP call token cost very high' 단언 — 실 6 atomic, 47x over-estimate, Confluence REST cascade primitive 미선재 → CFP-1523 carrier 안 Researcher Phase 0 발견 시점 정정) / **occurrence 2** = CFP-1523 사용자 spawn prompt fact 4건 모두 stale (ADR lane field 1/117 실 0/117 + binding 53 실 59 + 142 page 실 corpus 148 + 284 MCP call 실 6) — DomainAgent + ResearcherAgent dual verify 후 정정 / **occurrence 3** = CFP-1591 Issue body canonical/sibling 역할 반전 (단언 'canonical (codeforge-review) v4.11 vs sibling (wrapper) v4.9' — 실 reverse direction: canonical = wrapper v4.11, sibling = codeforge-review v4.9, ADR-010 §결정 1 canonical-first invariant 위배 detect, Orchestrator 가 CI lint 출력 잘못 해석 후 Issue #1591 body 발의 시 stale interpretation inherit). PMOAgent §5 inline ADR draft = ADR-NNN new ADR 권장 (Orchestrator → ArchitectAgent spawn carry-over) — ArchitectAgent chief author **자율 결정 Option B (ADR-082 Amendment 23 super-class scope expansion)** 채택 + **mid-flight CFP-1601 collision recovery** (initial spawn pinned origin/main `ec2fc349` + amendments[] max=21 → CFP-1601 Amd 22+1-K merge 후 base shift to `4c668913` + amendments[] max=22 → renumber Amd 22→23 + sub-scope 1-K→1-L on rebase). axis 정합 rationale: super-class 안 sub-scope axis disjoint 누적 1-L = governance hygiene + ratchet 강화 방향 (Option A new ADR fragmentation 회피). PMOAgent §5 inline ADR draft scope 3-form (Phase 0 brainstorm spawn-prompt fact verify + PR commit message defer rationale verify + follow-up Issue body 발의 시 fact verify) = 본 1-L 4-tuple primitive (a) upstream-inherited fact 식별 영역 4 sub-source (i-사용자 발화 / ii-sibling Issue body / iii-sister PR commit message / iv-별 carrier retro file) 안 완전 cover. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-fact-verify` warning-tier deferred-followup append). Wave 2 mechanical wire (`scripts/lib/check_spawn_prompt_fact_verify.py` Python SSOT per ADR-061 + bash thin wrapper + workflow yml + `.github/workflows/` self-app + bats fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 hotfix-bypass label MINOR + evidence-checks-registry warning-tier initial registration) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split precedent 답습). False-positive 완화 guards (code-span EXEMPT / quoted-text EXEMPT / templates/** EXEMPT / docs/stories/§9 transcript EXEMPT) = Wave 2 lint design 시 결정 — Phase 1 declarative scope 외. 본 Amendment 23 자체가 META-self-applied (§결정 10.D 18th applied case + Amendment 17 §결정 1-G strict claim mandate 4th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + 본 carrier 의 mid-flight collision recovery rebase): 본 Amendment 번호(23) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main HEAD `4c6689130e06262d42cae8ddea0d55a447b3b223` amendments[] max=22 — CFP-1601 Amd 22 merge 후 base post-collision-recovery, 정확 next-slot for CFP-1590 = 23) 후 결정 + ADR-RESERVATION amendments_reserved[] row pre-append + commit + PR open + post-CFP-1601-merge rebase + rename 22→23 + 1-K→1-L (verified-via: `git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md` frontmatter amendments[] 2026-05-25 KST 기준 origin/main HEAD `4c6689130e06262d42cae8ddea0d55a447b3b223` PRE-SPAWN-ORIGIN-MAIN-SHA re-pinned post-collision-recovery). doc-only fast-path ADR-054 Cat 1 단일 PR (script / workflow / bats wire 0건, ADR Amendment + CLAUDE.md cross-ref + ADR-RESERVATION row + evidence-checks-registry yaml row append only)."
    direction: strengthening
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K) → (1-L spawn prompt fact verify-before-trust mandate upstream-inherited stale fact super-class) 확장, forbid scope 축소 0건). ADR-064 §결정 7 (CFP-1149 Amendment 8) symmetric evidence-gated 정합. pattern_count evidence: §결정 1 sub-scope 1-L = 3 reach (CFP-1493 PR #1520 commit message defer 사유 / CFP-1523 사용자 spawn prompt 4 fact / CFP-1591 Issue body canonical/sibling 역할 반전) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation 산물. is_transitional: false 유지 (permanent governance policy). META-self-applied (§결정 10.D 18th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 4th applied case + mid-flight collision recovery 2nd applied case after CFP-FU-A Amd 19)."
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
    note: "CFP-FU-A sub-decision 3 carrier — Race window 단축 layer. **COLLISION RECOVERY**: 본 Amd 19 = 원래 Amd 18 / sub-scope (1-H) 점유 plan 이 CFP-1342 (ADR-082 Amd 18 + 1-H, origin/main commit 94b2289 merged in 11bf2d95→ca1c20e drift window) 와 collision detected post-PR-#1527-open → rebase on ca1c20e + renumber Amd 18→19 + sub-scope (1-H)→(1-I) + 4-file cross-ref update recovery. parallel session race 11th occurrence (CFP-1420 Sub-A S1.2 STAND_DOWN_DUPLICATE per PR #1441 prior merge 2026-05-24T03:07:53Z) escalate_user pattern_count 11 ≫ ADR-045 §D-9 threshold 2 Mandatory escalation 산물 + 12th meta-occurrence (CFP-1342 collision recovery in-flight — recursive dogfooding evidence for #1476 sub-decisions 1+2+3 race window 직접 reproduce: T0 worktree create → T1 spawn prompt finalize → T2 ArchitectAgent commit → ~30-60s gap → T3 CFP-1342 merge → T4 PR #1527 open → T5 collision detected → T6 recovery). 4-tuple primitive: (a) pre-spawn-prompt-finalize verify mandate (worktree create 후 spawn prompt content 작성 직전 ~30-60s window 안 1회 추가 polling 의무) / (b) 3-source 동시 invoke + AND aggregate verify (git fetch origin main + gh issue list search + gh pr list search head:<branch> 3-source 동시, sub-decision 2 AND composition layer 정합) / (c) race window ~30-60s 단축 mandate (worktree create timestamp ~ spawn prompt emit timestamp 안) / (d) verified-via annotation (`pre_spawn_prompt_finalize_verified: <bool>` field). 본 sub-scope 1-I = 1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H 와 disjoint axis (pre-spawn-prompt-finalize window verify axis). Amd 15 (1-E pre-spawn pin spawn-time SHA fetch 시점) + Amd 16 (1-F mid-spawn drift spawn-internal periodic) + Amd 18 (1-H Orchestrator §10 FIX Ledger resolution field source/evidence verify Orchestrator monopoly axis) + 본 Amd 19 (1-I pre-spawn-prompt-finalize 두 시점 사이 window chief author spawn 영역) = 4-layer temporal defense forcing function 완결 (pre-spawn-fetch + pre-spawn-prompt-finalize + mid-spawn-periodic + Orchestrator §10 source-claim). ADR-082 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block + sub-scope 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습 (spawn-time anchor block pattern). paired sibling carriers within CFP-FU-A: ADR-073 Amendment 13 (sub-decision 1 polling cadence 1→3, 12+13번째 transition trigger entries `pre_git_operation` + `pre_push`) + ADR-073 Amendment 14 (sub-decision 2 OR→AND composition layer §결정 1-P primitive AND aggregate) = 3 ADR Amendment 동시 발의 axis disjoint complement 3-set (event timing cadence + composition layer + window narrowing), ADR-064 §결정 1 CFP scope unitary 정합. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `pre-spawn-prompt-finalize-verify` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR bump + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습). 본 Amendment 19 자체가 META-self-applied (§결정 10.D 14th applied case + collision recovery 1st applied case): 본 Amendment 번호(19) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main ca1c20eefd3f3db35a85604ec320f8f6cb2919ff max=18 — CFP-1342 Amd 18 merge 후 base post-CFP-1343 fetch verified, 정확 next-slot = 19) 후 결정 (verified-via: `git show origin/main:docs/adr/ADR-082-...md` frontmatter amendments[] 2026-05-25 KST 기준 origin/main HEAD ca1c20e post-collision-recovery rebase). Lane plugin agent md cross-ref (codeforge-design ArchitectAgent.md spawn prompt template + codeforge-pmo GitOpsAgent.md) = follow-up defer (wrapper-only ADR-010 sibling sync 면제)."
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
    note: "CFP-1601 carrier — numeric-claim write-time strict claim mandate 1st applied case. 4-step verify-before-write mandate: (a) source command identify — claim 의 ground truth source command 명시 의무 (예: `grep -c '^  - amendment_id:' <file>` / `wc -l <file>` / `git diff --shortstat` / `find <dir> -name '*.md' | wc -l`) / (b) direct execute — 작성 직전 source command 실행 + actual value 획득 의무 (cached value / 추정 / planning-time stale value 사용 금지) / (c) claim↔actual cross-verify — claim value 와 actual value 1:1 일치 verify (semantic ambiguity (예: `grep -c` line-occurrence count vs YAML max amendment_id slot semantic) 발견 시 source command 정밀화 의무) / (d) write only on match — match 시에만 write, mismatch 시 abort + Orchestrator escalate. Numeric claim closed-set 6종 enumeration: (i) line count (file line count / patch line count) / (ii) file count (touched file count / dir file count) / (iii) API count (mcp__github__* call count / agent spawn count) / (iv) pattern_count (cross-Story pattern repetition count, ADR-045 §D-9 base) / (v) commit count (commits-behind / commits-ahead) / (vi) row count (yaml row / md table row / contract field). 본 sub-scope 1-K = sub-scope 1-A (cross-repo state verify) / 1-B (Issue body authorship) / 1-C (user-utterance verbatim) / 1-D (cross-repo label-write authority) / 1-E (spawn prompt SHA-anchor) / 1-F (spawn-internal periodic drift) / 1-G (amendment-slot pre-reservation) / 1-H (Orchestrator §10 FIX Ledger source/evidence) / 1-I (pre-spawn-prompt-finalize) / 1-J (cross-repo worktree target authority) 와 disjoint axis (numeric claim source/value strict claim axis — claim 의 quantitative ground truth verify-before-write). 가장 인접한 sub-scope = 1-G (amendment-slot pre-reservation — 동일 row append strict claim axis 안, numeric value = amendment_id slot 인 경우 1-G 와 overlap 영역이 있으나 1-G 는 reservation lifecycle 자체, 1-K 는 일반 numeric claim 의 source/value verify). 1-J 와는 disjoint (1-J = filesystem write-target authority, 1-K = numeric value source command). 동인 = ADR-045 §D-9 Mandatory escalation 산물 (CFP-1571 §3.2 line count drift '+93→+101' 3 location 정정 + CFP-1581 §3.2 file count drift '10→14' actual, pattern_count 2 reach forcing function 활성). spawn packet 자체 안 numeric claim ambiguity catch — recursive dogfooding META first applied evidence: spawn packet declared 'sub-scope (1-J)' (CFP-1601 numeric claim) ↔ actual ADR-082 frontmatter occupied sub-scope 1-J by Amendment 21 (CFP-1578) → 정확 next-letter = 1-K, source command `grep '1-J' docs/adr/ADR-082-...md | head -5` 실행 verify 후 정정. spawn packet claim `amendments[] count = 21` source command `grep -c '^  - amendment_id:' <file>` actual result = 41 (line occurrence count) vs semantic intent (max amendment_id slot value) divergence 직접 발견 = numeric-claim source command 정밀화 의무 4-step (b)(c) 의 1st applied empirical evidence. Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `numeric-claim-write-time-verify` warning-tier deferred-followup). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435/1559/1578 Wave 1→Wave 2 split 답습). 본 Amendment 22 자체가 META-self-applied (§결정 10.D 17th applied case + numeric-claim verify-before-write 1st applied case META first applied): 본 Amendment 번호(22) 가 target ADR-082 frontmatter `amendments:` Read verify (worktree HEAD 0a19e6a origin/main amendments[] max=21 — CFP-1578 Amd 21 merge 후 base, 정확 next-slot = 22) 후 결정. ADR-RESERVATION amendments_reserved[] row pre-append (adr_number 82 amendment_id 22 reserved_by_cfp CFP-1601 reservation_date 2026-05-25 KST status active) 의무 충족 — Amendment 17 sub-scope 1-G pre-reservation strict claim mandate META 3rd applied case (Amendment 18 CFP-1342 1st applied + Amendment 21 CFP-1578 2nd applied precedent 답습)."
  - amendment_id: 23
    carrier_story: CFP-1590
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1 layer 1 sub-scope 1-L (신설)"]
    nature: ratchet-up  # §결정 1 layer 1 sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I/1-J/1-K) → (1-L spawn prompt fact verify-before-trust mandate upstream-inherited stale fact super-class) 확장 (ADR-058 §결정 5 강화 방향). PMOAgent CFP-1523 retro §5 inline ADR draft Orchestrator → ArchitectAgent spawn carry-over — chief author 자율 결정 Option B 채택 (super-class scope expansion). mid-flight CFP-1601 collision recovery (initial Amd 22+1-K spawn pinned origin/main `ec2fc349` + amendments[] max=21 → CFP-1601 Amd 22+1-K merge 후 base shift to `4c668913` + max=22 → renumber 22→23 + 1-K→1-L on rebase).
    note: "CFP-1590 carrier — ADR-045 §D-9 Mandatory escalation pattern_count 3 reach 산물 (anchor_id `stale_fact_inheritance_at_lane_spawn` / root_cause_class `verify-before-trust-at-spawn-prompt`). 3 occurrences: (1) CFP-1493 S2.3 PR #1520 commit message stale defer 사유 inheritance ('284 MCP call token cost very high' 단언 — 실 6 atomic, 47x over-estimate, Confluence REST cascade primitive 미선재 → CFP-1523 carrier Researcher Phase 0 발견 시점 정정) / (2) CFP-1523 사용자 spawn prompt fact 4건 모두 stale (ADR lane field 1/117 실 0/117 + binding 53 실 59 + 142 page 실 corpus 148 + 284 MCP call 실 6) / (3) CFP-1591 Issue body canonical/sibling 역할 반전 (단언 'canonical (codeforge-review) v4.11 vs sibling (wrapper) v4.9' — 실 reverse direction: canonical = wrapper v4.11, sibling = codeforge-review v4.9, ADR-010 §결정 1 canonical-first invariant 위배). ArchitectAgent chief author 자율 결정 Option B (ADR-082 Amendment 23 super-class scope expansion) vs Option A (새 ADR 신설) — axis 정합 rationale: super-class 안 sub-scope axis disjoint 누적 1-L = governance hygiene + ratchet 강화 방향, Option A new ADR fragmentation 회피 (ADR-082 already permanent governance anchor verify-before-trust 4-layer 의 internal lane agent self-write super-class SSOT 영역). axis 분리 vs Amd 5 1-C (사용자 발화 content 전달 형식 verbatim 의무) + Amd 20 §결정 15 (self-write Issue body stale-claim super-class write-time pre-screen) + Amd 22 1-K (own author write-time numeric claim source/value strict, 6-dimension closed-set CFP-1601): 1-C = content 전달 형식 / 1-L = content fact truthfulness / Amd 20 = self-write content stale / 1-K = numeric claim own author write-time / 1-L = upstream-inherited stale fact at spawn-time (4 sub-source identify). 4-tuple primitive: (a) upstream-inherited fact 식별 (4 sub-source: 사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) / (b) direct source verify (`verified-via:` annotation, cached/synthesized 금지) / (c) stale 검출 시 `[fact-correction: <claim> stale, verified <correct-value>, source: <verify-source>]` marker / (d) `spawn_prompt_fact_verified: <bool>` field 명시. 4-layer temporal defense (Amd 15+16+18+19) 의 content fact axis 5th layer 신설 — temporal axis disjoint (when verify vs what verify). Wave 1 = declaration-only behavioral mandate (`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-fact-verify` warning-tier deferred-followup append). Wave 2 mechanical wire (Python SSOT lint + bash wrapper + workflow + bats RED→GREEN stash proof + label-registry MINOR + evidence-checks-registry) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split precedent 답습). 본 Amendment 23 자체가 META-self-applied (§결정 10.D 18th applied case + Amendment 17 §결정 1-G strict claim mandate 4th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + mid-flight collision recovery 2nd applied case after CFP-FU-A Amd 19): 본 Amendment 번호(23) 가 target ADR-082 frontmatter `amendments:` Read verify (origin/main HEAD `4c6689130e06262d42cae8ddea0d55a447b3b223` amendments[] max=22 — CFP-1601 Amd 22 merge 후 base post-collision-recovery, 정확 next-slot for CFP-1590 = 23) 후 결정 + ADR-RESERVATION amendments_reserved[] row pre-append + post-collision-recovery rebase + atomic renumber 22→23 + 1-K→1-L — strict pre-claim mandate 정합 (PRE-collision pre-claim row preserved + post-collision renumber). doc-only fast-path ADR-054 Cat 1 단일 PR (ADR Amendment + CLAUDE.md cross-ref + ADR-RESERVATION row + evidence-checks-registry yaml row append only, script/workflow/bats wire 0건)."
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
    status: deferred-followup     # Phase 1 declare (본 Amendment 22 CFP-1601) / Phase 2 actual wire = 별 sub-CFP carrier (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry)
    target_section: §결정 1 layer 1 sub-scope (1-K)       # numeric claim write-time strict claim mandate — ArchitectAgent / Orchestrator / lane PL write-time 영역 안 numeric claim 의 4-step verify-before-write 의무 (a-source command identify (e.g. `grep -c <pat> <file>` / `wc -l` / `git diff --shortstat` / `find ... | wc -l`) / b-direct execute + actual value 획득 (cached/추정/planning-time stale 사용 금지) / c-claim↔actual cross-verify (semantic ambiguity (line-occurrence count vs max amendment_id slot 등) 발견 시 source command 정밀화 의무) / d-write only on match). Numeric claim closed-set 6종: line count / file count / API count / pattern_count / commit count / row count. 동인 = ADR-045 §D-9 Mandatory escalation 산물 (CFP-1571 §3.2 line count drift +93→+101 3 location 정정 + CFP-1581 §3.2 file count drift 10→14 actual, pattern_count 2 reach). paired sibling axis = Amendment 17 §결정 1-G (row append amendment-slot scope) + Amendment 20 §결정 15 (Issue body content scope, 4 sub-pattern enumeration). META first applied case: 본 ADR Amendment 22 spawn packet 자체 안 numeric claim ambiguity catch (sub-scope letter 1-J→1-K 정정 + amendments[] count semantic disambiguation 41 grep occurrences vs max slot 21).
  - action: spawn-prompt-fact-verify
    status: deferred-followup     # Phase 1 declare (본 Amendment 23 CFP-1590) / Phase 2 actual wire = 별 sub-CFP carrier (Python SSOT lint per ADR-061 `scripts/lib/check_spawn_prompt_fact_verify.py` + `scripts/check-spawn-prompt-fact-verify.sh` bash thin wrapper + `templates/github-workflows/spawn-prompt-fact-verify.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-spawn-prompt-fact-verify.bats` fixture RED→GREEN stash proof per §결정 11.A + label-registry-v2 hotfix-bypass label MINOR + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합)
    target_section: §결정 1 layer 1 sub-scope (1-L)       # spawn prompt fact verify-before-trust mandate (upstream-inherited stale fact carrier super-class) — Orchestrator 또는 chief author 가 lane agent spawn prompt 작성 시 인용 fact (numeric / state / count / sister carrier claim) 가 (i) 사용자 발화 (ii) sibling Issue body (iii) sister PR commit message (iv) 별 carrier retro file 로부터 inherit 된 경우 직접 verify 의무 + verified-via annotation + stale 검출 시 fact-correction marker + verified-via field 명시. 본 1-L = 4-layer temporal defense (Amd 15 pre-spawn-fetch + Amd 19 pre-spawn-prompt-finalize + Amd 16 mid-spawn-periodic + Amd 18 Orchestrator §10 source-claim) 의 content fact axis 5th layer (when verify vs what verify disjoint). axis 분리 vs Amd 5 1-C (content 전달 형식 axis) + Amd 20 §결정 15 (self-write Issue body stale-claim super-class) + Amd 22 1-K (own author write-time numeric claim source/value strict). 동인 = CFP-1590 ADR-045 §D-9 Mandatory escalation pattern_count 3 reach (CFP-1493 commit message defer 사유 + CFP-1523 사용자 spawn prompt 4 fact + CFP-1591 Issue body canonical/sibling 역할 반전). PMOAgent CFP-1523 retro §5 inline ADR draft Orchestrator → ArchitectAgent spawn carry-over chief author 자율 결정 Option B 채택 + mid-flight CFP-1601 collision recovery (initial Amd 22+1-K → renumber Amd 23+1-L).
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

**후속 carrier 발의 의무 — Amendment 1 (CFP-841) 충족**: ~~scope (d) verify source 의 mechanical-queryable registry 화 (cross-plugin ownership registry + lint) = 별 후속 CFP carrier 분리 발의 (escalation_action `escalate_user`, CFP-776 merge 후 발의 권장). scope (a) corpus annotation mechanical lint (ADR-068 I-5 패턴 재사용) = 동일 후속 carrier 또는 별 CFP 분리 — brainstorm 단계 결정.~~ → **CFP-841 단일 통합 carrier 로 충족** (brainstorm 단계 결정 = scope (a) + scope (d) 단일 carrier, ADR-064 §결정 1 unitary scope). 본 §결정 6 = Wave 1 behavioral mandate + Wave 2 (Amendment 1) deferred-followup mechanical declaration. actual lint script + workflow wire = CFP-841 Phase 2 carrier (Change Plan §3 SSOT).

**self-referential trap 회피 (EC-3 self-protection)**: ADR-082 자체가 corpus #1a/#1b/#2/#3 (CFP-746 D-7 corpus slip / CFP-531 정정-2nd-slip / CFP-770 CR-004 `is_transitional` 거짓 단언 / §결정 8 Phase 0 cross-plugin 추정) 패턴을 본문에 인용/포함한다. ADR-082 frontmatter `is_transitional: false` + `## 해소 기준` = `N/A (permanent)` 선언은 §결정 2 verify 대상이 *아니다* (ADR-058 §결정 5 약화 방향 발의 차단 logic 통과 = permanent 정책 선언, source verify 가 적용될 mutable value 아님). 본 self-referential 면제가 §결정 본문에 명문화된 self-protection — DesignReview 가 "ADR-082 가 자기 frontmatter 를 verify 안 했다" 로 flag 하지 않도록. **Amendment 1 (CFP-841) 확장**: scope 2(a) corpus annotation lint 의 4번째 FP-완화 guard (self-referential exemption) 가 본 EC-3 를 verbatim 재사용 — ADR-082 본문 / CFP-776 Story / CFP-841 Story·Change Plan 의 corpus #1a/#1b/#2/#3 패턴 인용은 lint self-flag 차단 (file allowlist 정합, Change Plan §3.1 guard 4).

### §결정 7 — scope (e) FIX 명세 depth-aware 분리 (scope 외)

scope (e) FIX 명세 depth-aware scope 필드 (CFP-770 §8 제안 — broken-link/path 정정 FIX 명세 시 directory depth + 정정 규칙 범위 의무 필드) 는 **본 ADR scope 외 (별 CFP 분리)**. super-class write-time verify mandate (a-d) ↔ FIX 명세 depth-aware (e) = disjoint 관심사 — 전자 = write-time truth verify (behavioral) / 후자 = fix-event-v1 schema 필드 확장 (ADR-008 contract bump + ADR-010 sibling sync 동반 = 사용자 가치 판단 영역). 동일 Story 묶음 시 CFP-scope-unitary (ADR-064 §결정 1) 위반. (e) = CFP-770 §8 reservation Issue carrier (escalation_action `escalate_user`, CFP-776 merge 후 발의 권장).

### §결정 8 — per-area 분할 (scope a/b/c/d 각 별 ADR) 거부 (scope 외)

4 scope = 단일 super-class 결함의 4 layer 표현. §결정 1 layer disjoint 표가 공통 anchor. ADR-064 §결정 1 정합 — 단일 super-class = unitary scope (영역별 분할 아님). per-area 분할 시 super-class anchor 가 4 ADR 로 분절되어 cross-Story pattern aggregation (ADR-045 §D-9) 의 forcing function 약화.

### §결정 9 — Amendment 번호 citation plan-time staleness 차단 (Amendment 6 신설, CFP-1198 — Amendment 7 양방향 확장, CFP-1312)

**forcing function**: 거버넌스 artifact (β-issue body / spec / change-plan / PR body / ADR amendment 본문) 안에서 특정 ADR 또는 inter-plugin contract 의 amendment 번호를 인용할 때, 인용 직전 target artifact 의 frontmatter `amendments:` 목록 (또는 `amendment_log`) 을 `Read` 도구로 직접 확인한 후 **정확 next-slot `M = max(amendment_id) + 1` 만 사용한다**. `M > max + 1` (forward-staleness — off-by-one / 계산 오류) 또는 `M ≤ max` (backward-staleness — 이미 land 된 slot 인용) 모두 stale citation (Amendment 7 확장, CFP-1312).

**verify-before-cite 의무**:

1. target ADR / contract 파일의 frontmatter `amendments:` 또는 `amendment_log` 항목을 직접 Read 한다.
2. 현재 최대 `amendment_id` 값 (`max`) 을 확인한다.
3. 새 amendment 번호 = **정확히 `max + 1`** 로 결정한다 (Amendment 7 명시 — `M = max+1` 외 모두 stale). forward (M > max+1) / backward (M ≤ max) 양방향 staleness 차단.
4. 인용 위치에 `verified-via: <frontmatter Read 경로 및 시각>` annotation 을 부착한다 (§결정 2(b) `[verified: git show origin/main:<path>]` annotation 형식 준용).

**scope**: 본 §결정 9 는 §결정 2(b) ("ArchitectAgent §3 / §7 corpus enumeration + ADR frontmatter value 인용 시 verify") 의 sub-specialization 이다. §결정 2(b) 가 이미 "ADR frontmatter value 인용 시 verify" 를 포괄하나, amendment 번호 citation 이 plan-time (β-issue / spec / change-plan 작성 시점) 에 발생하는 점 — 즉 §결정 2(b) 의 lane agent write-time 보다 이른 시점 — 을 명시적으로 언급하기 위해 별 결정으로 codify.

**적용 대상 layer**:

| artifact 종류 | 주체 | 적용 layer |
|---|---|---|
| β-issue body, ADR brainstorm Phase 0 spec, change-plan | Orchestrator-authored | ADR-073 (Orchestrator verify-before-assert) ∩ 본 §결정 9 동시 적용 |
| ADR amendment 본문, design lane Change Plan | ArchitectAgent (internal lane agent) authored | 본 ADR §결정 2(b) + §결정 9 동시 적용 |
| spec / plan 기타 planning artifact | 해당 lane PL authored | 본 §결정 9 적용 |

**disjoint layer 관계**: β-issue = Orchestrator-authored artifact 이므로 ADR-073 §결정 1 (Orchestrator cross-repo state / assumption verify) 가 동시 적용된다. 단, ADR-073 와 본 ADR 의 axis disjoint (verify subject: Orchestrator cross-repo state assertion ↔ internal lane agent self-write value assertion) 가 본 §결정 9 의 plan-time 영역에서 overlap 하는 구조임을 명시 — 각 ADR scope 침범 아님 (동일 artifact 에 두 layer 가 독립적으로 적용). ADR-073 cross-ref: `docs/adr/ADR-073-orchestrator-verify-before-assert.md` §결정 1 (Orchestrator verify-before-assert — β-issue 작성 시 amendment 번호 cite 가 cross-repo state assertion 에 해당).

**known-limitation**: 본 §결정 9 = behavioral directive (Wave 1). Wave 2 mechanical lint (`amendment-number-frontmatter-verify` script + workflow + bats fixture) = CFP-1216 Phase 2 (별 sub-carrier 로 land 완료, 2026-05-22 KST). **Amendment 7 (CFP-1312)** 가 Wave 2 lint Check (b) coverage gap (forward only → 양방향) 보강 — `cited_m != max_id + 1` 양방향 비교 + `[FORWARD-STALE]` / `[BACKWARD-STALE]` 출력 format 분리 + self-reference exemption (ADR file 자체) + templates/** path filter. frontmatter `mechanical_enforcement_actions:` 의 `amendment-number-frontmatter-verify` entry status warning retain (scope expand only, tier 변경 0).

**pattern evidence (ADR-045 §D-9 Mandatory, pattern_count = 3 — Amendment 7 확장)**:

| # | 출처 | stale citation | actual (verified) | staleness 방향 | catch layer |
|---|---|---|---|---|---|
| 1 | CFP-1177 β-issue (#1115) | "ADR-027 Amendment 7" | ADR-027 실제 max = Amendment 8 (CFP-1059 점유) → 실제 slot = Amendment 9 | forward (M > max+1) | Amendment 6 Wave 1 behavioral catch |
| 2 | CFP-1179 β-issue (#1114) | "ADR-063 Amendment 6/7" | ADR-063 실제 max = Amendment 7 (CFP-906/CFP-1059 점유) → 실제 slot = Amendment 8 | forward (M > max+1) | Amendment 6 Wave 1 behavioral catch |
| 3 | CFP-1293 retro (#1293) | "ADR-083 Amendment 2" | ADR-083 실제 max = Amendment 2 시점, 정확 next-slot = 3 → cited_m=2 ≤ max=2 | backward (M ≤ max) | Amendment 6 Wave 1 catch + CFP-1216 lint Check (b) forward-only coverage gap escape — **Amendment 7 motivation** |

세 케이스 모두 write-time 에 caught (plan land 후 escaped 0) 이나, root cause = (1)/(2) plan-time read verify 부재 + (3) lint coverage gap (`M > max+1` forward-only 비교). Amendment 7 = 양방향 mechanical wire 보강 (Wave 2 escape catch).

**ADR-068 I-4 (wording SSOT) 연계**: amendment 번호는 governance artifact 전체에서 동일 식별자로 참조되는 wording SSOT 대상이다. stale 번호가 planning artifact 에 기록되면 후속 ADR 본문 / CLAUDE.md / retro 와 wording drift 가 발생 — I-4 위반 원인이 된다.

### §결정 10 — ArchitectAgent write-time discipline 4 sub-scope expansion (Amendment 8 신설, CFP-1329)

ADR-082 §결정 1 layer 1 (Orchestrator scope) + §결정 2 scope (a-d) (internal lane agent self-write scope) 의 write-time verify mandate 가 ArchitectAgent (codeforge-design chief author) 의 4 write-time discipline 영역까지 확장 적용된다. 4 sub-decisions 모두 별 axis disjoint 이며, 같은 super-class (verify-before-trust write-time semantic truth) 아래 단일 carrier 통합 (ADR-064 §결정 5 unitary 정합).

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

**META-ROOT pattern_count 1** (CFP-1025 bootstrap-labels.sh:53-55): codify rationale forward-prevention (META-ROOT severity = mis-diagnosis 전파 chain risk, recurrence ≥ 2 wait 시 P1 propagation 영역 — CFP-1006 mis-diagnosis lineage verified). codeforge-wide grep audit = follow-up CFP carrier (별 sweep). ADR-058 §결정 5 forward-prevention 영역 적격, ADR-064 §결정 7 CFP-1149 Amendment 8 symmetric evidence-gated 면제.

#### §결정 11 — disjoint axis with Amendment 8 §결정 10

| Amendment | scope | write-time artifact axis | layer |
|---|---|---|---|
| Amendment 8 §결정 10 | ArchitectAgent write-time discipline 4 sub-scope (A/B/C/D) | 거버넌스 artifact (Story / Change Plan / ADR / memory) | governance write-time |
| **Amendment 9 §결정 11** | **Code-level write-time discipline 2 sub-scope (A/B)** | **코드 artifact (test code / script error path)** | **code write-time** |

두 Amendment 가 ADR-082 super-class (write-time semantic truth verify) 의 disjoint layer expansion. Amendment 8 = chief author scope / Amendment 9 = Code-level scope. CFP scope unitary (ADR-064 §결정 5) 정합 — 단일 super-class 안 disjoint axis 분리.

**Wave 1 = declaration-only**: 2 sub-decisions 모두 behavioral directive. Wave 2 mechanical wire (CodeReviewPL audit dedicated points: tautology smell grep + `Grep '2>/dev/null' scripts/**` resource-creating/state-changing audit + codeforge-wide grep audit sweep) = 별 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

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

**Wave 1 = declaration-only**: 2 sub-decisions 모두 behavioral directive. Wave 2 mechanical wire (RequirementsPL §2.1 verified state table lint + retro empirical-verify-required marker) = 별 sub-carrier 분리 (deferred-followup, ADR-082 Wave 1 declaration-only precedent 답습).

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

- **(D-A) scope (e) 본 ADR 흡수** — disjoint 관심사 (fix-event-v1 schema 변경 동반 사용자 가치 판단 영역), CFP-scope-unitary 위반 → §결정 7 별 CFP 분리.
- **(D-B) per-area 분할 (scope a/b/c/d 각 별 ADR)** — super-class anchor 4 ADR 분절, ADR-045 §D-9 pattern aggregation 약화 → §결정 8 단일 super-class 거부.
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

Wave 1 (CFP-776) §결정 6 은 `mechanical_enforcement_actions: []` empty 를 명시적 known-limitation 으로 결정하면서 **후속 carrier 발의 의무**를 본문에 명문화했다 (scope (d) mechanical-queryable registry 화 + scope (a) corpus annotation lint = 별/동일 후속 carrier, brainstorm 단계 결정). CFP-776 retro §6 후보 1 escalation_action `escalate_user` → 사용자 "Carrier 6+7 escalation 전체 발의" 승인 (2026-05-16 KST). brainstorm 단계 결정 = scope (a) + scope (d) **단일 통합 carrier** (ADR-064 §결정 1 unitary scope — scope (a) 만 부분 codify 시 §결정 6 rationale 2 super-class anchor 분절 위반).

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
- scope 2(e) = §결정 7 별 CFP 분리 결정 유지 (fix-event-v1 schema 동반 가치 판단 영역)
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
| Wave 3 (cross-repo, 후순위 ratchet) | RequirementsPL spawn prompt template (`mclayer/plugin-codeforge-requirements`) explicit verify-before-trust mandate | cross-repo PR (canonical sibling sync, CFP-1002 precedent) | 별 canonical CFP carrier (wrapper-only Wave 1 우선, sibling sync 후순위 ratchet) |

Wave 2/3 = deferred-followup, 본 Amendment 2 frontmatter `mechanical_enforcement_actions[]` 갱신 0건 (Wave 1 = behavioral mandate + template codification, mechanical lint 자체는 Wave 2 carrier). Amendment 1 의 `corpus-claim-verify` + `cross-plugin-ownership-verify` 2 entry 유지 — 본 Amendment 2 scope (1-B) 와 disjoint sub-decision.

#### A2-3 — scope_boundary (out-of-scope)

본 Amendment 2 **포함**: §결정 1 layer 1 (Orchestrator scope) verify scope 의 (1-B) Issue body authorship time 명시적 codify + Wave 1 behavioral + template (a) + playbook (b).

본 Amendment 2 **out-of-scope** (유지/별 carrier):

- **(c) RequirementsPL spawn prompt template** mandate (canonical-side `mclayer/plugin-codeforge-requirements` repo) — cross-repo sibling sync 동반 가치 판단 영역, CFP-1002 precedent 정합 (wrapper-only Story 우선, cross-repo sibling sync 후순위 ratchet) → 별 canonical CFP carrier.
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
- 후속 carrier (Wave 2 mechanical lint) = 별 CFP, brainstorm 단계 결정
- 후속 canonical carrier (Wave 3 cross-repo) = 별 CFP, RequirementsPL spawn prompt template mandate

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

- **codeforge-design lane fan-out 축소** (chief + 5 deputy + 4-tuple = 10+ agent → 핵심 4-5 축소) — fidelity vs coverage trade, 별 가치 판단 영역 → 별 CFP carrier (brainstorm 단계 결정).
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
- 후속 carrier (codeforge-design lane fan-out 축소 — 가치 판단 영역) = 별 CFP, brainstorm 단계 결정

---

## Amendment 6 — Amendment 번호 citation plan-time staleness 차단 forcing function (CFP-1198, 2026-05-22 KST)

### 컨텍스트

ADR-045 §D-9 Mandatory escalation 산물 (pattern_count 2 ≥ threshold 2). 동일 세션 안에서 두 건의 plan-time amendment 번호 stale citation 이 발생 (write-time caught, land escaped 0):

- **CFP-1177 β-issue #1115**: 계획 "ADR-027 Amendment 7" → target ADR-027 frontmatter 미검증 → 실제 slot = Amendment 9 (Amendment 7·8 이미 CFP-1059 등 점유). stale citation 이 β-issue body 에 기재됨.
- **CFP-1179 β-issue #1114**: 계획 "ADR-063 Amendment 6/7" → target ADR-063 frontmatter 미검증 → 실제 slot = Amendment 8 (Amendment 6·7 이미 CFP-906/CFP-1059 점유). stale citation 이 β-issue body 에 기재됨.

두 케이스 모두 공통 root cause = **plan-time citation staleness** — governance artifact 작성 전 target ADR frontmatter `amendments:` 목록을 Read verify 하지 않은 채 amendment 번호를 기재. 기존 §결정 2(b) ("ADR frontmatter value 인용 시 verify") 가 이 영역을 포괄하나, plan-time artifact 에 대한 명시적 언급이 없어 forcing function 으로서 약했음 — 별 §결정 9 로 명시적 codify.

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

status `deferred-followup` = Phase 1 declare (본 Amendment 6) / Phase 2 actual wire = 별 CFP-1198 Phase 2 sub-carrier (ADR-060 §결정 5 모든 신규 entry warning 시작 강제 + ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain 정합).

#### A6-3 — ADR-073 cross-ref (Orchestrator-authored β-issue 적용 명시)

§결정 9 본문 내 disjoint layer 관계 표에 ADR-073 cross-ref 명시:
- β-issue body = Orchestrator-authored → ADR-073 §결정 1 (Orchestrator verify-before-assert) 동시 적용
- 본 ADR scope = internal lane agent self-write + planning artifact 포함 (§결정 9 신설)
- 두 ADR axis disjoint (verify subject overlap 아님) — 동일 artifact 에 독립 적용

본 Amendment 6 는 ADR-073 frontmatter 를 수정하지 않는다 (prose cross-ref only, ADR-073 frontmatter amendment 신설 0 — ADR-073 axis 침범 회피).

#### A6-4 — scope_boundary (out-of-scope)

본 Amendment 6 **포함**: §결정 9 신설 + `mechanical_enforcement_actions[]` 신규 entry + ADR-073 cross-ref prose.

본 Amendment 6 **out-of-scope** (유지 / 별 carrier):

- **Wave 2 mechanical lint** (`amendment-number-frontmatter-verify` script + workflow + bats fixture) = 별 CFP-1198 Phase 2 sub-carrier (deferred-followup).
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

ADR-082 Amendment 6 (CFP-1198, 2026-05-22 KST) 가 §결정 9 신설 + `amendment-number-frontmatter-verify` deferred-followup entry declare. CFP-1216 Phase 2 (2026-05-22 KST) 가 별 sub-carrier 로 Wave 2 mechanical lint 를 land 완료 — `scripts/lib/check_amendment_number_stale.py` (Python SSOT) + `scripts/check-amendment-number-stale.sh` (thin wrapper, ADR-061 §결정 6.A) + `templates/github-workflows/amendment-number-frontmatter-verify.yml` + `.github/workflows/amendment-number-frontmatter-verify.yml` (self-app) + `tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats` + `docs/evidence-checks-registry.yaml` entry (warning tier).

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
| TC-B-TEMPLATE-EXEMPT | templates/test-fixture.md 안 `ADR-999 Amendment 99` 인용 | PASS no [WARN] (또는 별 path exclusion) | templates/** canonical example 면제 (path filter guard 2) |

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
- PMOAgent false-positive tally 별 axis carrier = OOS (Story §6.2 OOS-1, 별 ADR escalation candidate).
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

`mechanical_enforcement_actions[]` 신규 entry `cross-repo-label-sync` warning-tier deferred-followup append. Wave 2 mechanical wire (workflow runtime activation + bats fixture + bidirectional sync state lint) = 별 sub-carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — ADR-070 D5 retain 패턴 / ADR-076 / ADR-086).

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
- `templates/github-workflows/cross-repo-label-sync.yml` — bidirectional sync workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — `[cross-repo-label-sync]` audit comment prefix 신설 (Amendment 14 audit trail anchor)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:cross-repo-label-sync` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/security/pat-rotation-log.md` — Amendment 14 동반 placeholder (PAT scope `issues:write` rotation evidence)
- `docs/evidence-checks-registry.yaml` — `cross-repo-label-sync` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별 sub-carrier)
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
- `templates/github-workflows/spawn-prompt-head-pin-check.yml` — spawn prompt SHA-anchor write-time verify workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:spawn-prompt-head-pin-presence` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/evidence-checks-registry.yaml` — `spawn-prompt-head-pin-presence` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별 sub-carrier)
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
- `templates/github-workflows/mid-spawn-drift-detection-check.yml` — spawn-internal periodic origin re-pin protocol workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:mid-spawn-drift-detection` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/evidence-checks-registry.yaml` — `mid-spawn-drift-detection` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별 sub-carrier)
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
- `templates/github-workflows/amendment-slot-reservation-check.yml` — amendment-slot pre-reservation strict claim workflow skeleton (Wave 1 declaration-only / Wave 2 mechanical wire 별 sub-carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` — `hotfix-bypass:amendment-slot-reservation-check` family member append (Wave 2 carrier — declaration-only Wave 1)
- `docs/evidence-checks-registry.yaml` — `amendment-slot-reservation-check` entry warning-tier deferred-followup (Phase 1 declare / Phase 2 actual wire 별 sub-carrier)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1435-amendment-slot-prereservation.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy + `docs/change-plans/` gitignored)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-082 Amendment 17 sub-scope 1-G + ADR-050 cross-ref 1 line append (CFP-506 line cap 정합)
- `<internal-docs>/plugin-codeforge/stories/CFP-1435.md` — Story file (Sub-CFP C carrier, Phase 1 declarative)

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

#### §결정 1 layer 1 sub-scope (1-J) 신설 — cross-repo worktree target authority verify mandate (Amendment 21, CFP-1578)

sub-scope (1-A/1-B/1-C/1-D/1-E/1-F/1-G/1-H/1-I) precedent 답습 (closed-set ratchet 강화). 본 Amendment 21 = sub-scope (1-J) append. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint, 동시 발의 race).

> sub-scope 1-J = cross-repo worktree target authority verify axis 신설 — wrapper plugin-codeforge ↔ internal-docs cross-repo write-target boundary 영역 (1-D cross-repo label-write authority 와 가장 인접하나 verify 대상 disjoint: 1-D label state write authority ↔ 1-J filesystem write-target (worktree path↔remote URL) authority).

#### 1-J 4-tuple primitive — cross-repo worktree target authority verify mandate

chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 4 의무:

1. **worktree target authority verify-before-write 의무** — `git -C <worktree_abs_path> remote -v` 실행하여 expected repo (예: wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 확인. mismatch 시 write 차단 + sentinel 발화.
2. **spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 명시** — write-target authority anchor block 형식 (sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block + sub-scope 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습 — spawn-time anchor block normative pattern 동형). enum: `wrapper` (`plugin-codeforge`) / `internal-docs` (`codeforge-internal-docs`) / `marketplace` / `consumer-<name>` (mctrader 등). field 부재 시 sentinel 발화.
3. **cross-repo 작업 sequence 시 명시적 worktree switch 의무** — wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (각 repo 별 worktree 분리, ADR-040 worktree convention 정합). cross-repo write 필요 시 별 worktree explicit create + cwd switch + write 의무 (single worktree 안 cross-repo write 차단).
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

closed-set 정의: 본 6 dimension 외 numeric claim (예: timing latency / memory size / token count) 은 write-time strict mandate scope 외 (별 carrier 필요 시 ADR-082 별 Amendment 발의, ratchet 강화 방향 only).

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

- **Option A (새 ADR-NNN 신설)**: 새 ADR `ADR-NNN-spawn-prompt-fact-verify-before-trust-mandate` 신설 — verify axis disjoint axis 신설 (Amd 5 1-C user-utterance verbatim 형식 axis 와 별 ADR file). **REJECT 사유**: super-class fragmentation 위험 (ADR-082 already permanent governance anchor verify-before-trust 4-layer 의 internal lane agent self-write super-class SSOT) + governance hygiene 위배.
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

