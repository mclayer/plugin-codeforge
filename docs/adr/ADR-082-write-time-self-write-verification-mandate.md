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
  - amendment_id: 5
    carrier_story: CFP-1110
    date: 2026-05-20  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1"]
    nature: ratchet-up  # §결정 1 layer 1 (Orchestrator scope) sub-scope (1-C) Lane PL spawn prompt user-utterance verbatim anchor 확장 (ADR-058 §결정 5 강화 방향)
    note: "사용자 직권 minimal path 첫 적용 (codeforge process 가 lane traversal fidelity loss source 라는 평가 결과 채택 정합 — Researcher net 35% 정당화 / Codex ROI indeterminate-부정쪽 confidence medium 수렴, 2026-05-20 KST). pattern corpus 누적 evidence: synthesizer-stale-reference 6 (CFP-722/801/792/810/819/825) + Researcher 12 occurrence 정정 (CFP-698) + scope 재확대 금지 invariant 6+ 위치 (CFP-758) + unverified-self-write-claim super-class 5. minimal path 정합: Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 (사용자 승인 2026-05-20 KST) — closed-loop break 외부 결정 채널. Wave 1 = behavioral mandate (lane PL spawn prompt 첫 줄 anchor block 의무) — Wave 2 mechanical lint = 별 CFP carrier (deferred-followup). sister Amendment = ADR-071 Amendment 6 (back-translation gate binding, lane return 직후 verify, CFP-1110 paired Amendment carrier)."
related_stories:
  - CFP-776  # carrier (super-class 통합 결정 — escalation_action escalate_user)
  - CFP-841  # Amendment 1 carrier (§결정 6 behavioral→mechanical 전환 후속 carrier)
  - CFP-1016 # Amendment 2 carrier (§결정 1 layer 1 Orchestrator scope Issue-body verify 확장)
  - CFP-1041 # Amendment 3 carrier (ADR-085 disjoint complement — verify axis ↔ coordination axis cross-ref)
  - CFP-1110 # Amendment 5 carrier (§결정 1 layer 1 sub-scope (1-C) Lane PL spawn prompt user-utterance verbatim anchor — 사용자 직권 minimal path first application, paradox-break)
  - CFP-746  # pattern corpus #1a/#1b (corpus slip + 정정-2nd-slip)
  - CFP-770  # pattern corpus #2/#3 (§9 evidence stale + Phase 0 cross-plugin 추정)
  - CFP-1000 # Amendment 2 corpus #4 (Issue body 3 inversions: prod-cutover-deputy-evidence INVERTED + baseline stale + path incorrect)
  - CFP-1001 # Amendment 2 corpus #5 (Issue body L189 lint output verbatim FP transcribe)
  - CFP-1002 # Amendment 2 corpus #6 (Issue body ADR-054 filename missing 'story' word)
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

## 해소 기준

N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — write-time verify scope 확장. **Amendment 1 = behavioral→mechanical scope 확장 = 강화 방향 정합, sunset_justification 면제**). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. `is_transitional: false` (영구 정책 — Amendment 1 후에도 유지). **self-referential 주의**: 본 §해소 기준 부재 (`N/A — permanent`) 선언 자체가 §결정 2 write-time verify 대상이 *아니다* (§결정 6 EC-3 self-protection — permanent 정책 선언은 source verify 가 적용될 mutable value 아님).

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
