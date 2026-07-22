---
adr_number: 52
title: Codex Proactive Check — 6 Touchpoints
date: 2026-05-09
status: Proposed
category: workflow-policy
carrier_story: CFP-354
parent_epic: null
supersedes: null
amends: null
amendments:
  - id: 1
    date: 2026-05-11
    carrier_story: CFP-411
    summary: "touchpoint #4 (RequirementsPLAgent §1-§6 완료 직후 Codex proactive check) single-shot → multi-round adversarial debate (debate-protocol-v1) 격상. semantic divergence 감지 시 자동 발동. ADR-059 / ADR-044 Amendment 1 정합."
  - id: 2
    date: 2026-05-12
    carrier_story: CFP-446
    summary: "touchpoint #1 (AskUserQuestion 직전 Codex pre-question review) single-shot → iterative reformulation max 3 rounds 격상. Codex reject 기준 = 애매·컨텍스트 외 + 장황함. fall-through 시 그대로 사용자 ask. 단순 Codex self-iteration (debate-protocol-v1 lane-agnostic 미사용 — role_lock / adversarial 불필요)."
  - id: 3
    date: 2026-05-13
    carrier_story: CFP-510
    summary: "touchpoint #4 divergence detection 영역 확장 — 기존 3 semantic criteria (AC 의미 차이 / Edge Case 누락 / Why 해석 mismatch) 에 4번째 영역 = fact-check 추가. sub-criteria 4종 (registry-execution drift / pre-existing leak / file path verification / cross-repo state verification). PL self-evaluation 의무 = synthesis 작성 시 '가설' 영역 vs 'verified fact' 영역 분리 명시 + fact-check pending 시 reverse-explicit. CFP-451 / CFP-490 0-FIX chain retro 발견 evidence (PMOAgent FU-4 low). debate-protocol-v1 dispatch 흐름 변경 없음 — divergence_type 만 확장 (semantic + factual)."
  - id: 4
    date: 2026-05-13
    carrier_story: CFP-532
    summary: "touchpoint #2 (ArchitectAgent §3 완료 직후 Design Synthesis Check) optional → mandatory 전환. 6 sample success rate 100% sentinel (CFP-426 + CFP-427 + CFP-428 + CFP-429 + 2 carry-over Story) — 모든 dispatch 가 ArchitectAgent §3 산출물 결함을 review lane 진입 전 inline FIX 로 해소, review lane FIX 회피 evidence 누적. ADR-058 §결정 5 ratchet 강화 방향 + ADR-064 active amendment 정합. is_transitional=false, sunset_justification=N/A (permanent strengthening). 6 touchpoint 중 #2 단독 mandatory (#1/#3/#4/#5/#6 optional 유지). 본 Amendment scope = ADR + CLAUDE.md + playbook 갱신 (doc-only fast-path, ADR-054 §결정 1). skill orchestration code mandatory branch logic 은 별도 carrier 분리."
  - id: 5
    date: 2026-05-13
    carrier_story: CFP-578
    summary: "6 touchpoint 자동 dispatch 영역의 dispatch prompt template 안 file content verbatim 첨부 의무 본문 명시. ADR-070 (verify-before-trust pattern) §결정 D2 / D4 cross-ref. Codex worker 의 sandbox access 실패 (CFP-506 / CFP-520 / CFP-530 3 회 reproduce sentinel) 가 systemic 원인 — file path reference 만 사용 시 silent fallback 외부 source 인용 risk. 본 Amendment scope = ADR-052 본문 + playbook §3.10 dispatch prompt template patch + CLAUDE.md blockquote 갱신 (doc-only fast-path 영역, ADR-054 §결정 1 신규 ADR-070 동반 carrier 영역 정합). D1/D2/D3/D4 결정 본문 + Amendment 1/2/3/4 본문 의미 변경 없음."
  - id: 6
    date: 2026-05-17
    carrier_story: CFP-819
    summary: "Codex worker prompt boilerplate composition SSOT 영역을 신규 ADR-081 로 분리 (cross-ref). D1/D2/D3/D4 + Amendment 1-5 본문 의미 변경 없음 — boilerplate composition (3 mandatory section: dogfood-out path / lane stage / sandbox boundary) + verify-before-trust scope 분리 (file/dir/cross-repo + grep count active vs historical + ADR §결정 번호 정확성) + 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style+history disjoint) 영역의 normative anchor 가 cross-document 분산 상태였음 (ADR-052 Amendment 5 + ADR-070 D2). 6-Story carry-over evidence sentinel (1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0 CFP-786/801/792/795/810; 6 units / 7 retro file) + ADR-045 Amendment 5 §D-9 cross_story_pattern_adr_trigger forcing function (pattern_count 5 reach YES, escalation_action: adr_draft_emitted) carrier. is_transitional=false, sunset_justification=N/A (permanent strengthening, ADR-070 §D5 precedent 정합 declaration-only retain). 본 Amendment 6 scope = ADR-052 본문 sub-section append (cross-ref 1 paragraph) — D1/D2/D3/D4 + Amendment 1-5 본문 의미 변경 0건. ADR-054 §결정 1 신규 ADR-081 동반 carrier 영역 정합 (full-lane 강제)."
  - id: 7
    date: 2026-05-17
    carrier_story: CFP-844
    summary: "ADR-081 Amendment 1 (신규 §결정 D6 Codex worker severity calibration rubric) cross-ref sub-section append. D6 = Codex finding severity ↔ PL synthesis severity bidirectional calibration anchor (over-rate 금지 + security-relevant under-rate 금지) + ground truth = DesignReviewPL final verdict severity primary (CodeReviewPL fallback / higher PL 양쪽) + boundary-completeness exception (Codex P0 boundary-completeness × DesignReview P1 = over-rate 아님, +1 tier) + disjoint axis preservation (codex_severity_inflation calibration ≠ codex_false_positive_tally accuracy, fp 0 chain sentinel 무영향) + tracking = 기존 Story §9/§10 prose marker (review-verdict-v4 contract field 신설 0 — doc-only fast-path 유지, ADR-081 §D5 declaration-only retain precedent verbatim). D1/D2/D3/D4 + Amendment 1-6 본문 의미 변경 0건 — sub-section append only (Amendment 1-6 패턴 정합). is_transitional=false, sunset_justification=permanent strengthening (verify-before-trust scope 에 severity calibration 차원 추가 — ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합, 약화 영역 0). doc-only fast-path 자체 적격 — 단 carrier Story (CFP-844) 는 ADR-081 Amendment 1 (신규 §결정 D6) 동반 = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests 무변경) doc-only fast-path 단일 PR 적격."
  - id: 8
    date: 2026-05-18
    carrier_story: CFP-946-A
    summary: "6 touchpoint substitution path 3-enum cross-ref (Amendment 5 verbatim 첨부 의무 SSOT + ADR-070 §결정 1 expansion SSOT 보존). 신설 §결정 영역 = 6 touchpoint × substitution path 3-enum (inline_orchestrator_verify default / manual_substitution_declare / fallback_skip_with_marker) cross-matrix. ADR-070 §결정 1 expansion (substitution scope 3-path enum codify) SSOT 본문 cross-ref. Codex sandbox 8 occurrence sentinel (CFP-756 Epic close retro Sentinel #4 strike #8, parent_epic CFP-946) escalate_user 산물. D1/D2/D3/D4 + Amendment 1-7 본문 의미 변경 0건 — sub-section append 패턴 (Amendment 1-7 패턴 정합). is_transitional=false, sunset_justification=N/A — permanent strengthening (substitution path 3-enum codification = Codex worker sandbox 영역 변경 없으면 permanent retain). doc-only fast-path 자체 적격 — carrier Story (CFP-946-A) 는 ADR-070 §결정 1 expansion + 신규 domain-knowledge 페이지 동반 = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + 신규 domain-knowledge + src/tests 무변경) doc-only fast-path 단일 PR 적격."
  - id: 9
    date: 2026-05-19
    carrier_story: CFP-1003
    summary: "**proactive/reactive disjoint scope codify** — D1 본문 L84 'codex:rescue 사후 대응(reactive) 채널' + D1 L90 'codex:codex-rescue proactive check 채널 분리' 의 명시적 boundary anchor 강화. 본 ADR-052 의 D1-D4 + Amendment 1-8 = **proactive 6 touchpoint scope 한정** invariant explicit codify. reactive codex:rescue 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역) 의 network_scope declare 의무 + verify-before-trust + boilerplate composition = ADR-070 Amendment 5 + ADR-081 Amendment 5 본문 SSOT 위임 (본 ADR 본문은 cross-ref only). Codex TP#4 (CFP-963 §6.3 OOS row + §3 EC-2 derived default — '`codex:rescue` lint = OUT, proactive 한정') 의 deferred scope = 본 Amendment 9 + ADR-070 Amd 5 + ADR-081 Amd 5 chain 으로 closure. D1/D2/D3/D4 + Amendment 1-8 본문 의미 변경 0건 — proactive/reactive disjoint anchor 명시 cross-ref sub-section append only. mechanical lint scope 확장 = 별 CFP (Wave 2, ADR-064 §결정 1 CFP scope unitary). is_transitional=false, sunset_justification=N/A — permanent strengthening (proactive/reactive disjoint boundary explicit codify, scope 축소 0). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + src/tests 무변경)."
  - id: 10
    date: 2026-05-20
    carrier_story: CFP-1056
    summary: "ADR-070 Amendment 6 cross-ref — fail-mode 6-set → 7-set 확장 (`subagent_recursion_blocked` 7번째 enum value 추가). CFP-1041 DesignReview lane PL spawn evidence: Agent SDK subagent context 안 Codex worker subagent spawn 시 ADR-039 platform-inherent recursion guard 차단 → `fallback_skip_with_marker` 활성 + fail-mode 7-enum 정합 declare. 추가 normative anchor — DesignReviewPL spawn pattern (Orchestrator parent context 직접 spawn 권장, subagent → subagent 회피 시 Codex worker substitution path 안정성 향상). D1/D2/D3/D4 + Amendment 1-9 본문 의미 변경 0건 — cross-ref sub-section append (Amendment 1-9 패턴 정합) + Amendment 8 6 touchpoint × 3-path enum cross-matrix 의 fail-mode enum 7-set 동기 정합. is_transitional=false, sunset_justification=N/A — permanent strengthening (subagent_recursion_blocked fail-mode codify, scope 축소 0). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + ADR-070 Amendment 6 cross-ref + Story file + src/tests 무변경)."
  - id: 11
    date: 2026-05-21
    carrier_story: CFP-1131
    summary: "Codex touchpoint **wrapper-self trim** (6 → 4 conditional skip — touchpoint 2 + 5 wrapper-self 영역 conditional skip). ratchet 축소 2번째 carrier — CFP-1126 ADR-058 §결정 5 first applied paradigm 연장. Amendment 4 (CFP-532, touchpoint 2 mandatory) 의 partial rollback (wrapper-self 영역만, consumer 영역 mandatory 보존). evidence-grounded justification 3 axis — (a) **empirical**: wrapper-self Codex FP 0 streak 11+ Story (CFP-770/771/776/786/795/801/810/819/825/844/851 +) Codex calibration 정확 evidence. (b) **duplication axis**: touchpoint 5 (ArchitectPLAgent root cause 직후) = touchpoint 3 (DeveloperPLAgent FIX 2+) follow-on 중복 — ArchitectPL verdict packet 자체 fact-check marker 4종 + verify-before-trust scope 5 sub-scope (ADR-070) cover; touchpoint 2 (ArchitectAgent §3 직후) = ADR-082 §결정 2 scope (a-d) write-time verify (CFP-841 Amendment 1) + §결정 1 sub-scope (1-C) USER-UTTERANCE-VERBATIM block (CFP-1110 Amendment 5) + ADR-071 Amendment 6 §결정 17 back-translation gate (CFP-1110) cover. (c) **ratchet 축소 paradigm 연장** — CFP-1126 ADR-042 Amendment 10 first applied 의 2번째 application. retain (4 touchpoint) = #1 AskUserQuestion 직전 / #3 DeveloperPL FIX 2+ / #4 RequirementsPL §1-§6 (multi-round debate, Amendment 1) / #6 ArchitectAgent ADR 초안 (ADR audit critical). drop (2 conditional skip in wrapper-self) = #2 ArchitectAgent §3 / #5 ArchitectPLAgent root cause. scope = wrapper-self only (codeforge plugin family 자체 변경, dogfood 영역). consumer Story (mctrader 등 외부 product) = 별 carrier (evidence base 부재 — Codex FP 0 streak wrapper-self 한정). minimal path Story (CFP-1110/CFP-1126/본 CFP) = lane spawn 0 이미 touchpoint 발생 0, 본 trim 영역 외. 사용자 직권 minimal path 3번째 application (Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 사용자 승인 2026-05-21 KST). is_transitional=false, sunset_justification=ADR-058 §결정 5 second applied carrier (약화 방향 evidence-grounded — wrapper-self 영역 conditional skip codify, consumer scope 보존, mechanical 약화 차단 logic 통과). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + CLAUDE.md cross-ref + src/tests 무변경)."
  - id: 12
    date: 2026-05-22
    carrier_story: CFP-1244
    summary: "(a) ADR-081 Amendment 6 (신규 §결정 D8 Codex worker dispatch file-redirect mandate) cross-ref — codeforge Orchestrator/lane 이 Codex CLI worker check 호출 시 file-redirect 형식 `codex exec --sandbox read-only < <promptfile>` 의무 + result-via-file 수신 + synchronous block-wait 금지. dispatch invocation mandate 본문 SSOT = ADR-081 §결정 D8 (본 ADR-052 는 cross-ref-only, 본문 중복 codify 0 — Amendment 6/7/8/9 cross-ref-only 패턴 정합). (b) `[codex-sandbox-fallback: <fail-mode>]` Story §10 marker fail-mode enum 7 → 8 확장 (ADR-070 Amendment 7 SSOT cross-ref) — 8번째 value `dispatch_stall_or_stream_timeout` 신설 (기존 7 = api_missing / version_skew / enterprise_blocked / gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only / subagent_recursion_blocked, 모두 snake_case noun phrase — 신규 value 동일 naming convention) + §A3 cross-ref 표 6-stale → 8 정정 (Amendment 10 이 subagent_recursion_blocked 추가 시 §A3 표 누락한 mechanical self-check escape 반영). 신규 fail-mode 영역 = Codex `codex exec` invocation stall (TTY 부재 0-byte stall >5min) OR Orchestrator stream idle-timeout during long Codex wait → `fallback_skip_with_marker` path. evidence = Issue #1244 + CFP-1187 운영 phase Epic S4/S5 early stall + S7 ArchitectPL stream timeout after 40 tool_uses → redo + Codex CLI v0.125.0. D1/D2/D3/D4 + Amendment 1-11 본문 의미 변경 0건 — sub-section append 패턴 (Amendment 1-11 정합) + closed-enum 7 → 8 확장 (additive, 정보 손실 0). is_transitional=false, sunset_justification=ratchet 강화 방향 (closed-enum expansion = strengthening — ADR-058 §결정 5 + ADR-064 §self-application ratchet 정합, 약화 영역 0). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + ADR-081 Amendment 6 cross-ref + src/tests/workflow 무변경)."
  - id: 13
    date: 2026-05-23
    carrier_story: CFP-1286
    summary: "ADR-070 Amendment 8 (§결정 D1 expansion fail-mode enum 8 → 9 확장, 9번째 value `codex_truncated_no_verdict` 신설) cross-ref. CFP-604 retro F2 follow-up realized — single sample escalate_user 사용자 직접 채택. fail-mode 영역 = file-redirect dispatch (ADR-081 Amendment 6 §결정 D8) 정상 invocation 후 sandbox + Windows PowerShell encoding policy reject + 대용량 artifact processing 누적 → reasoning budget 소진 → output 안 verdict analysis block 부재. post-invocation reasoning-exhausted path = 기존 8 fail-mode value 어디에도 mapping 불가 (axis disjoint — file-redirect ↔ stream-stall ↔ reasoning-exhausted 3 disjoint failure mode). §A3 cross-ref 표 8 → 9 enum 동기 정정. ADR-070 Amendment 8 SSOT (본 ADR-052 cross-ref-only) + ADR-081 Amendment 7 cross-ref 동반 (file-redirect dispatch 후속 영역 disjoint sub-domain). closed-enum expansion (8 → 9, additive, 정보 손실 0, 기존 8 value 의미 변경 0) = strengthening (ADR-058 §결정 5 + ADR-064 §self-application top-down ratchet). D1/D2/D3/D4 + Amendment 1-12 본문 의미 변경 0건. is_transitional=false, sunset_justification=N/A (강화 방향, scope 축소 0). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + ADR-070 Amendment 8 cross-ref + src/tests/workflow 무변경). pattern_count=1 (single sample), 후속 sibling evidence 누적 시 mechanical detection lint 별 CFP carrier (ADR-076/082/086 precedent 답습)."
  - id: 14
    date: 2026-05-25
    carrier_story: CFP-1368
    summary: "CFP-1286 (Amendment 13 Wave 1 declarative anchor) 의 **Wave 2 mechanical wire** — 9 fail-mode enum 누적 카운터 lint mechanical enforcement layer activation. `mechanical_enforcement_actions: []` → `[codex-fallback-subclass-tally]` 전환 (declaration-only retain → warning-tier mechanical wire). evidence-checks-registry yaml entry `codex-fallback-subclass-tally` (warning tier, bypass `hotfix-bypass:codex-fallback-tally`) + scripts/lib/check_codex_fallback_tally.py + workflow yml (PR-open + daily cron `15 0 * * *` UTC) + bats fixture 9 TC (RED→GREEN stash proof, ADR-082 §결정 11.A + CFP-1334 mandate) + comment-prefix-registry-v1 v1.4 → v1.5 MINOR bump (2-entry append `[codex-sandbox-fallback]` + `[codex-substitution-scope-declared]`, PIVOT-5 NEW Q5 (a) atomic 채택, 15 → 17 prefix taxonomy) + jsonl seed `docs/kpi/codex-fallback-tally.jsonl` (ADR-013 §1 atomic rename pattern, ADR-076 misattribute 정정). ADR-045 §D-9 escalation_action `escalate_user` enum 정합 (per-enum threshold 3 strict tuning vs ADR-045 N=2 baseline, per-enum sub-domain self-tuned). first prod observation closure carrier (Wave A S1 `codex_truncated_no_verdict` first prod evidence + Wave B S3 sandbox path block sub-class disjoint evidence — retro internal-docs#811 fe8524a §6 F3). 10번째 enum candidate `codex_sandbox_path_blocked` = Out-of-scope (별 follow-up CFP carrier, ADR-064 §결정 1 scope unitary, Q1 (c) defer). PIVOT-6 META Codex calibration evidence acknowledge — Codex TP#4 F-5 self-stale 203 lines/v1.3 claim 정정 by Orchestrator FIX iter 1 ground truth 5건 direct file Read verify (ADR-052 line 812 + ls docs/observability/+kpi/ + wc comment-prefix-registry-v1.md = 219 lines/v1.4 + grep codex markers MISSING + grep bypass-justification line 178). label-registry-v2 v2.65 → v2.68 MINOR bump (sibling coordination: CFP-1306=v2.66 / CFP-1367=v2.67 / CFP-1368=v2.68 sequence, late-comer rebase invariant). marketplace atomic invariant (ADR-063 §결정 5) — plugin.json MINOR + CHANGELOG.md + marketplace.json sibling sync. dual-binding pattern 답습 (CFP-963 codex-network-scope-presence precedent — declaration source ADR-052/070/081 / enforcement source ADR-060 evidence-enforceable warning-tier framework). D1/D2/D3/D4 + Amendment 1-13 본문 의미 변경 0건 — frontmatter amendment_log + mechanical_enforcement_actions[] field 만 변경, sub-section append 패턴 정합. is_transitional=false, sunset_justification=N/A (ratchet 강화 방향 — declaration-only → warning tier mechanical enforcement layer activation, 약화 영역 0). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + mechanical_enforcement_actions[] field 만 변경 + sibling Bundle B coordination Phase 1, src/tests = Phase 2 carrier 분리)."
  - id: 15
    date: 2026-06-29
    carrier_story: CFP-2458
    summary: "**touchpoint #7 신설 (merge-time adversarial gate) — ADDITIVE 강화**. 6 touchpoint (Amendment 11 wrapper-self 6→4 conditional skip 후 잔존 #1/#3/#4/#6) 가 모두 lane 작업 *중* dispatch 라 머지 직전(shift-right 최우측, CI gate PASS 후 ~ `gh pr merge` 전) 위치가 부재 — Epic CFP-2457 Story A 가 이 빈자리에 독립 분포 LLM critic(Codex) 을 adversarial verifier 로 신설. **#2/#5 복원 아님** (Amendment 11 6→4 ratchet 무손상 — drop 된 #2 ArchitectAgent §3 / #5 ArchitectPL root cause 는 시점·대상·산출물 모두 disjoint, lane-time 영역; #7 = merge-time 영역). ADR-058 §결정 5 sunset_justification 면제 = **강화 방향** (touchpoint 신설 = closed enumeration 확장 additive, 약화 0). 핵심 reshape: critic = 신호원이지 차단 판정자 아님 — critic 의 모든 결함 주장 = `[hypothesis]` 지위, falsifiable evidence(file:line) 동반 의무 + Orchestrator 직접 falsify(ADR-070 verify-before-trust) 통과 시만 `[verified]` 승격해 머지 보류 (ADR-077 §결정 7 정보 무결성 invariant 무검증 승격 금지 + ADR-119 Amd 2 + overcorrection 증거 적대 framing 오거부율 26%→73% — arxiv 2603.00539). D1/D2/D3/D4 + Amendment 1-14 본문 의미 변경 0건 — touchpoint #7 신규 §결정 (D5 신설: merge-time adversarial gate) + ProactiveCheckPacket schema enum `<1|..|6>` → `<1|..|7>` 확장(additive) sub-section append only. dependency: ADR-039 Amendment 6 (inline whitelist 6번째 entry merge-time Codex dispatch — 재귀 가드 회피 critical) + ADR-070 Amendment 9 (verify-before-trust merge-time scope cross-ref + fail-mode/fail-closed enum) + ADR-081 Amendment 9 (merge-time severity rubric — D6 review-lane ground truth 머지직전 닫힘 대응). marketplace 무관 (plugin.json 4-field 무변경). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + 3 sibling ADR Amendment + concept 문서 + Story file, src/tests 무변경 — Phase 2 worker agent/playbook wire 는 별 carrier). is_transitional=false, sunset_justification=N/A (ADDITIVE 강화 방향, scope 축소 0)."
  - id: 16
    date: 2026-06-29
    carrier_story: CFP-2464
    summary: "**touchpoint #8 신설 (mutation peer — surviving-mutant hollow-gate 탐지) — ADDITIVE 강화**. Epic CFP-2457 Story B. Amendment 15 가 신설한 touchpoint #7(merge-time adversarial gate, *산출물(PR diff)* 을 review = review-of-output) 와 **같은 적대적 검증 family, 다른 mechanism** — touchpoint #8 = *detector(테스트 스위트)* 를 변이로 probe (probe-the-detector). Codex 가 GREEN(이미 PASS) detector 보유 산출물에 국소 결함(mutant) 명세를 제기 → lane 이 적용+suite 재실행 → surviving(주입 후에도 PASS)이면 hollow-gate(검사연극) 신호. Amendment 15 D5.f 가 명시한 'merge-time adversarial dispatch pattern' 재사용 = ProactiveCheckPacket schema + verify-before-trust 무조건 + critic=hypothesis reshape + severity→처리 매핑 4축 상속. concept SSOT = `docs/domain-knowledge/concept/mutation-based-hollow-gate-detection.md`. **#7 흡수 아님** (timing·mechanism disjoint — #7 = merge-time/review-of-output, #8 = 구현리뷰 lane-time/probe-the-detector). 핵심 reshape (Story A 상속+mutation 특유): surviving mutant 주장 = `[hypothesis]` 지위, **어떤 입력에서 어떤 동작 차이** 동반 의무 + PL/QADev 재현 falsify(해당 mutant 실제 적용 후 suite 정말 PASS 재현) 통과 시만 `[verified]` hollow-gate 승격. mutation-특유 false-positive 2원천 = equivalent mutant(4~39%, undecidable — Madeyski 2013 via arxiv 2408.01760) + flaky 오염(미처리 시 mutant-test pair 9% unknown — ShiETAL19 ISSTA 2019) → 'surviving≠hollow' 양면. D1/D2/D3/D4 + Amendment 1-15 본문 의미 변경 0건 — touchpoint #8 신규 §결정 (D6 신설: mutation peer gate) + ProactiveCheckPacket schema enum 리터럴 stale `<1|2|3|4|5|6>`(L146 본문 + L610 Amd5 verbatim) → `<1|2|3|4|5|6|7|8>` 정정 확장(A #7 누락분 + B #8, additive) sub-section append only. **Q-A 결정 = 경로 B (Codex = mutant 명세만 생성 = 신호원, lane 이 적용+실행)** — ADR-081 §결정 D8 `--sandbox read-only` 무손상 + 'Codex=신호원' 정합. dependency: ADR-070 Amendment 10 (verify-before-trust mutation scope + equivalent/flaky 불확정 disposition) + ADR-081 Amendment 10 (mutation severity rubric + payload split). **ADR-039 Amendment 불요** = mutation peer dispatch = 구현리뷰 lane worker(sub-agent)가 Bash(`node codex-companion.mjs review`)로 Codex 호출(CodexReviewAgent 동형 proven channel — Agent tool 아닌 Bash 호출이라 재귀 가드 미발동) → inline whitelist 신규 entry 0 (entry 6 merge-time 흡수 아님). marketplace 무관 (plugin.json 4-field 무변경 — Phase 1). doc-only fast-path 자체 적격 (ADR-054 §결정 1, 기존 ADR Amendment + 2 sibling ADR Amendment + concept landing + Story file, src/tests 무변경 — Phase 2 worker agent/playbook wire/dispatch contract 는 별 carrier). is_transitional=false, sunset_justification=N/A (ADDITIVE 강화 방향, scope 축소 0)."
related_stories:
  - CFP-354
  - CFP-411
  - CFP-446
  - CFP-510
  - CFP-532
  - CFP-578
  - CFP-819
  - CFP-844  # Amendment 7 — ADR-081 Amendment 1 (§결정 D6 severity calibration) cross-ref
  - CFP-946-A  # Amendment 8 — substitution path 3-enum cross-ref (parent_epic CFP-946)
  - CFP-1003   # Amendment 9 — proactive/reactive disjoint scope codify (Codex TP#4 CX-963-deferred closure, reactive codex:rescue 영역 ADR-070 Amd 5 + ADR-081 Amd 5 본문 SSOT 위임 cross-ref)
  - CFP-1056   # Amendment 10 — ADR-070 Amendment 6 cross-ref (fail-mode 7-set 확장, subagent_recursion_blocked enum value, CFP-1041 DesignReviewPL subagent context evidence)
  - CFP-1131   # Amendment 11 — Codex touchpoint wrapper-self trim (6 → 4, touchpoint 2 + 5 conditional skip, ratchet 축소 2번째 carrier, ADR-058 §결정 5 second applied, 사용자 직권 minimal path 3번째)
  - CFP-1244   # Amendment 12 — ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref + ADR-070 Amendment 7 fail-mode enum 7 → 8 확장 cross-ref (dispatch_stall_or_stream_timeout 신설) + §A3 cross-ref 표 6-stale 정정 (CFP-1187 S4/S5/S7 evidence)
  - CFP-1286   # Amendment 13 — ADR-070 Amendment 8 cross-ref (fail-mode enum 8 → 9 확장, codex_truncated_no_verdict 9번째 value) + ADR-081 Amendment 7 cross-ref. CFP-604 retro F2 realized (single sample escalate_user).
  - CFP-1368   # Amendment 14 — CFP-1286 Wave 2 mechanical wire (codex-fallback-subclass-tally lint activation, mechanical_enforcement_actions [] → [codex-fallback-subclass-tally]). first prod observation closure carrier (CFP-1317 Wave A + Wave B sub-class disjoint evidence). PIVOT-6 META Codex calibration evidence (TP#4 F-5 self-stale catch by FIX iter 1 5-source ground truth verify). comment-prefix-registry-v1 v1.4 → v1.5 + label-registry-v2 v2.65 → v2.68 + evidence-checks-registry entry. CFP-1334 RED→GREEN stash proof + ADR-082 §결정 11.A mandate. 9-enum closed-set scope retain (10번째 candidate codex_sandbox_path_blocked = Out-of-scope 별 follow-up CFP).
  - CFP-2458   # Amendment 15 — touchpoint #7 신설 (merge-time adversarial gate, ADDITIVE 강화). Epic CFP-2457 Story A. ProactiveCheckPacket enum 6→7. critic = 신호원 (hypothesis 지위, evidence 동반 + PL falsify 후 verified 승격). dependency: ADR-039 Amd 6 + ADR-070 Amd 9 + ADR-081 Amd 9. concept = merge-time-adversarial-verification-gate.md.
  - CFP-2464   # Amendment 16 — touchpoint #8 신설 (mutation peer — surviving-mutant hollow-gate 탐지, ADDITIVE 강화). Epic CFP-2457 Story B. ProactiveCheckPacket enum 7→8. probe-the-detector mechanism (#7 review-of-output 와 disjoint family). Q-A = 경로 B (Codex = mutant 명세만, lane 적용+실행). surviving mutant = hypothesis (equivalent/flaky 양면 → 재현 falsify 후 hollow-gate 승격). dependency: ADR-070 Amd 10 + ADR-081 Amd 10. ADR-039 Amendment 불요 (lane worker Bash 채널). concept = mutation-based-hollow-gate-detection.md.
related_adrs:
  - ADR-039
  - ADR-034
  - ADR-044
  - ADR-059
  - ADR-064
  - ADR-070
  - ADR-077  # Amendment 15 (CFP-2458) — §결정 7 정보 무결성 invariant (fact-check marker 무검증 승격 금지) 재사용 (critic 주장 hypothesis→verified 승격 룰 anchor)
  - ADR-081  # Amendment 6 (CFP-819) boilerplate SSOT 분리 + Amendment 7 (CFP-844) §결정 D6 severity calibration cross-ref + Amendment 9 (CFP-2458) merge-time severity rubric
  - ADR-119  # Amendment 15 (CFP-2458) — research-before-claims Amd 2 게이트 verdict ground-truth (독립 검증자 충원 동인)
related_files:
  - docs/orchestrator-playbook.md
  - docs/superpowers-integration.md
  - CLAUDE.md
is_transitional: false
mechanical_enforcement_actions:
  - codex-fallback-subclass-tally  # CFP-1368 Amendment 14 Wave 2 mechanical wire — declaration-only retain (Amendment 1-13) → warning-tier mechanical enforcement (Amendment 14, CFP-1286 Wave 1 declarative anchor mirror). 9 fail-mode enum 누적 카운터 lint (scripts/check-codex-fallback-tally.{sh,py} + templates/github-workflows/codex-fallback-tally-check.yml + tests/bats/check_codex_fallback_tally.bats + docs/kpi/codex-fallback-tally.jsonl + comment-prefix-registry-v1 v1.5 [codex-sandbox-fallback]/[codex-substitution-scope-declared] 2-entry SSOT codify). dual-binding pattern (declaration source ADR-052 Amendment 14 / enforcement source ADR-060 framework) — CFP-963 codex-network-scope-presence precedent 답습. ADR-070 §D5 + ADR-082 §결정 6 + ADR-081 §D5 + ADR-076 §결정 6 fail-closed clause precedent chain 정합 (Amendment 8 영역 fail-closed retain, Amendment 14 영역 mechanical wire activation — disjoint sub-domain).
---

# ADR-052: Codex Proactive Check — 6 Touchpoints

## 상태

**Proposed (2026-05-09)** — CFP-354 carrier story.

## 컨텍스트

Orchestrator(Claude)가 설계 레인 등에서 "꼬임" 현상이 발생한다:
- 6 SubAgent 산출물 통합 시 모순·순환 논리·누락이 생겨도 스스로 포착 불가
- AskUserQuestion 품질이 낮으면 모든 레인의 사용자 결정이 부정확해짐
- FIX root cause 판정이 단일 판정자(ArchitectPLAgent)에 의존 — 오판 시 레인 2~3개 재실행
- RequirementsPLAgent §1-§6 통합 후 설계 진입 전 독립 검증 없음

기존 `codex:rescue`는 **사후 대응(reactive)** 채널 — stuck 상황에서만 호출. 이 ADR은 **사전 예방(proactive)** 채널을 별도로 정의한다.

## 결정

### D1. Codex Proactive Check = Orchestrator inline dispatch

Orchestrator가 6개 touchpoint에서 `Agent(subagent_type="codex:codex-rescue")` 를 proactive check 용도로 자동 dispatch. 기존 codex:rescue(reactive) 와 채널 분리.

**거절된 대안**:
- (A) CodexReviewAgent 재사용: review lane 전용 설계 패턴 경계 침범
- (B) codex:rescue 확장: reactive 의미 희석, proactive/reactive 혼합으로 디버깅 어려움

### D2. 6개 touchpoint 전부 자동 활성

모든 touchpoint는 트리거 조건 충족 시 항상 자동 dispatch. opt-in 없음. 단, #3(Dev Rescue)는 "FIX 2+ 반복 동일 이슈" 조건이 트리거.

### D3. ProactiveCheckPacket v1 스키마

```yaml
touchpoint: <1|2|3|4|5|6|7|8>
purpose: <한 줄 목적>
context:
  lane: <requirements|design|develop|orchestrator>
  story_key: <CFP-NNN>
  artifacts: <첨부 산출물>
task: <Codex에게 요청할 구체적 작업>
```

출력: `{findings: [{severity: P0|P1|P2, description}], recommendation: PROCEED|ADDRESS_FIRST, rationale}`

### D4. #5 FIX Root Cause 불일치 = 사용자 에스컬레이션

Codex와 ArchitectPLAgent 판정 불일치 시 자동 proceed 금지 — 사용자가 최종 판정.

## 결과

- 6개 touchpoint playbook §3.10에 문서화
- Orchestrator 행동 변화: 각 트리거 시점에 codex:codex-rescue dispatch 의무화
- codex:rescue(reactive) 채널 동작 변경 없음
- CodexReviewAgent 역할 변경 없음
- 문서 전용 변경 (코드/agent file 변경 0건)

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §3.10 신설 (6개 touchpoint 상세)
- [`docs/superpowers-integration.md`](../superpowers-integration.md) — §2 표 6행 추가 (24→30 호출 지점)
- [`CLAUDE.md`](../../CLAUDE.md) — 오케스트레이션 규칙 섹션 Codex Proactive Check 정책 blockquote 추가

---

## Amendment 1 (2026-05-11, CFP-411)

### Context

Story 1 (CFP-391) merged 후 `debate-protocol-v1` registry + ADR-059 (5 결정 — protocol 정의 + DesignReview 자동 발동 + reasoning carryover + anchor 재발 escalation + lane-agnostic) + ADR-044 Amendment 1 (`auto_on_divergence` dispatch_mode) 가 active. DesignReview lane 은 multi-round adversarial debate 자동 발동이 적용된다.

본 Amendment 는 touchpoint #4 (RequirementsPLAgent §1-§6 완료 직후 Codex proactive check) 를 동일 protocol 의 두 번째 lane 적용처로 격상한다. ADR-059 §결정 5 (lane-agnostic 설계) 활용 — 신규 contract 신설 없음.

### 결정 (Amendment 1)

**A1. Touchpoint #4 single-shot → multi-round debate 격상**

기존 `D2` 의 "RequirementsPLAgent §1-§6 통합 완료 → `phase:설계` 진입 직전 (항상)" 트리거 동작:

- (기존) Codex `codex:codex-rescue` 1회 dispatch → `findings + recommendation + rationale` 출력 → Orchestrator 가 `PROCEED | ADDRESS_FIRST` 결정
- (Amendment 후) Codex 1회 dispatch + RequirementsPL 이 자기 synthesis (§2/§5/§6) 와 의미적 비교 → **semantic divergence 감지 시** debate-protocol-v1 자동 발동 → multi-round (min 3 / max 5 / soft default 4) → PL LLM 판정 또는 사용자 escalation → final verdict

**A2. Divergence 판정자 = RequirementsPL LLM (semantic)**

DesignReview lane (review-verdict-v4 `findings[]` structured surface) 와 달리 Requirements lane 은 verdict packet producer 아님 (synthesis lane). 따라서 divergence detection 은 PL LLM 판정 위임:

- 의미적 divergence 정의 = AC / Edge Case / why 해석 영역의 의미 차이
- `divergence_type: semantic` (debate-protocol-v1 registry §2.1 enum 이미 정의)
- false positive 차단 = PL prompt engineering 영역 (codeforge-requirements `agents/RequirementsPLAgent.md` sibling sync — Phase 2 follow-up PR)

**A3. anchor_id 형식 — Story §2/§5/§6 sub-item identifier**

Requirements lane 의 stable identifier 형식 결정 = `§<section-ref>` 형태로 review-verdict-v4 패턴 재사용 (lane-agnostic). 예:

- `§5-AC-3` — Story §5 (요구사항 확장 해석) Acceptance Criteria 번호
- `§5.2-EC-2` — Story §5.2 Edge Case 번호
- `§2-bound-1` — Story §2 (도메인 해석) 시스템 경계 항목
- `§6-source-2` — Story §6 (외부 지식 배경) source 항목

PL 이 LLM 판정으로 가장 가까운 sub-item identifier 선택. 모호 시 가장 광범위한 anchor (예: §5 전체) 사용 — debate 진입 정확도보다 진입 결정 우선 (Story §5.2 EC-4 정합).

**A4. FIX 흐름 redo 대상 = RequirementsPL 자체 (ArchitectAgent 미관여)**

debate verdict = FIX 시 redo 대상이 본 lane (Requirements) 이므로 ADR-059 §결정 3 (reasoning carryover) 의 ArchitectAgent re-run 대신 **RequirementsPL 자체 redo**. transcript 가 RequirementsPL re-spawn prompt 의 입력 packet 안에 verbatim 주입 → §2/§5/§6 재합성.

§10 FIX Ledger row append (Orchestrator self-write, fix-event-v1 1.1 정합) — `debate_artifact_ref` 필드 채움.

**A5. dispatch_mode `auto_on_divergence` 적용처 — team-spec-requirements.yaml Codex worker**

ADR-044 Amendment 1 의 enum value 활용 지점 2번째 추가 (1번째 = team-spec-design-review.yaml). Codex worker entry 신설 (현재 4 teammate — PL + Domain + Analyst + Researcher 만) + `dispatch_mode: [default, auto_on_divergence]` 적용.

**A6. D2 자동 활성 정합 보존**

기존 D2 "opt-in 없음, 6 touchpoint 자동 활성" 의미 변경 없음. debate 격상 후에도 자동 활성 유지 — sub-trigger 만 추가 (divergence 감지 시 추가 라운드).

**A7. D4 사용자 escalation 정합 보존**

기존 D4 "#5 FIX Root Cause 불일치 → 사용자 escalation" 의미 변경 없음. ADR-059 §결정 4 (anchor 재발 escalation) 와 path 독립 — 두 escalation 발생 시점 다름 (D4 = FIX root cause 판정 시점, ADR-059 = debate 자체 anchor 재발 시점).

### 결과 (Amendment 1)

- Touchpoint #4 의 단일-shot 동작 → multi-round debate dispatch 흐름 격상 (playbook §3.10.4 patch + §3.13 lane-agnostic 적용 명시)
- team-spec-requirements.yaml Codex worker entry 신설 (`dispatch_mode: [default, auto_on_divergence]`)
- codeforge-requirements plugin sibling sync follow-up PR (RequirementsPLAgent spawn 로직 divergence detection + debate dispatch 통합, ADR-010 정합)
- CLAUDE.md `Codex Proactive Check (CFP-354 / ADR-052)` blockquote 갱신 — #4 격상 명시 (다른 5 touchpoint 표기 보존)
- D1/D2/D3/D4 결정 본문 의미 변경 없음 — Amendment 1 sub-section 만 append

### 거절된 대안 (Amendment 1)

- (Amendment-A) Structured divergence detection surface 도입 (Requirements lane verdict packet schema 신설) — Requirements lane 은 verdict producer 아님, structured packet 도입은 lane scope 침해. PL LLM 판정 위임 채택 (Story §2.4 정합).
- (Amendment-B) Touchpoint #4 외 5 touchpoint 동시 격상 — CFP-B carrier (deferred). 본 Amendment 는 #4 만.
- (Amendment-C) divergence false positive 차단 위해 `auto_on_divergence` user opt-in flag 도입 — consumer overlay 정책 축소 불허 invariant 정합 (ADR-059 거절 대안 E 정합). 자동 발동 강제 유지.

---

## Amendment 2 (2026-05-12, CFP-446)

### Context

사용자 directive (2026-05-12, KST, [CFP-446 Story §1](https://github.com/mclayer/plugin-codeforge/issues/446) verbatim):

> "앞으로 모든 사용자 질문을 하기 전에 나에게 던질 질문을 codex에 리뷰 요청하여 애매하거나 그 질문의 컨텍스트 내에서 알 수 없는 질문인 경우 다시 재구성하여 리뷰한다. 이 리뷰는 최대 3회 반복할 수 있고 3회를 채우면 그냥 사용자에게 질문하라."

> "그리고 질문의 내용이 길수록 좋지 않은 질문이다. 최대한 간결하고 명확하게 핵심을 질문할 수 있도록 질문자와 리뷰어가 행동하도록 해라."

기존 touchpoint #1 (`AskUserQuestion` 직전 Codex pre-question review) = single-shot dispatch. Codex 가 "더 명확한 표현 / 더 풍부한 옵션 / 편향·누락·모호성 포착" 을 제안하면 Orchestrator 가 1 회 반영 후 즉시 `AskUserQuestion` 발화 — 재검증 channel 부재. 즉 Codex 가 제안한 reformulation 이 여전히 애매하거나 컨텍스트 외 영역을 포함한 경우에도 그대로 사용자에게 도달.

ADR-064 §결정 3 (결정 제시 5 룰 — 특히 룰 4 brevity 와 룰 5 `AskUserQuestion` 범위 제한) 의 mechanical 강화 channel 이 필요. memory `feedback_question_quality` 의 normative 승격이 ADR-064 §결정 3 룰 1·3·5 까지 다뤘으나 룰 4 brevity 의 enforcement gap 존재.

### 결정 (Amendment 2)

**A1. Touchpoint #1 single-shot → iterative reformulation 격상**

기존 `§3.10.1 Pre-question Review` 의 single-shot 동작:

- (기존) Orchestrator 질문 초안 작성 → Codex 1 회 dispatch → 제안 반영 → `AskUserQuestion` 발화
- (Amendment 2 후) Orchestrator 질문 초안 작성 → Codex iterative dispatch (max 3 rounds) → Codex `accept` 시 그대로 `AskUserQuestion` 발화 / `reject` 시 reformulation 반영 후 다음 round → 3 rounds fall-through 시 마지막 reformulation 그대로 사용자 ask

**A2. Codex reject 기준 (2 종)**

Codex 가 다음 2 종 중 1 종 이상 검출 시 `reject` + reformulation 제안 의무:

| Reject 기준 | 운영적 정의 |
|---|---|
| **ambiguity / context-external** | 질문 표현이 애매하거나, 답 추론에 필요한 정보가 현재 대화 컨텍스트에 부재 (즉 사용자가 답할 수 없는 질문) |
| **verbosity** | 질문 본문이 핵심 결정 영역 대비 장황. 사용자 발화 directive (2 문장) 의 directive: "질문의 내용이 길수록 좋지 않은 질문" |

2 기준 모두 통과 시 `accept` — Orchestrator 가 그대로 발화. 1 종이라도 검출 시 `reject` + reformulation 결과 반환 의무.

**A3. Max 3 rounds + fall-through 정책**

| Round 결과 | 다음 동작 |
|---|---|
| Round 1 `accept` | 그대로 `AskUserQuestion` 발화 (early termination) |
| Round 1 `reject` → Round 2 `accept` | Round 2 reformulation 으로 `AskUserQuestion` 발화 |
| Round 2 `reject` → Round 3 `accept` | Round 3 reformulation 으로 `AskUserQuestion` 발화 |
| Round 3 `reject` (fall-through) | Round 3 마지막 reformulation 그대로 `AskUserQuestion` 발화 — Codex 가 무한 reject 시 사용자 결정권 보존 |

사용자 발화 directive (1 문장) verbatim: "이 리뷰는 최대 3회 반복할 수 있고 3회를 채우면 그냥 사용자에게 질문하라" — fall-through 정책 SSOT.

**A4. 질문자 (Orchestrator) + 리뷰어 (Codex) brevity 행동 규범**

사용자 발화 directive (2 문장) 의 normative 승격:

| 주체 | 행동 규범 |
|---|---|
| **질문자 (Orchestrator)** | 질문 초안 작성 시 1 문장 단위 + numbered list (max 3 항목). 컨텍스트 길이 < 핵심 질문 길이 비율 유지. ADR-064 §결정 3 룰 4 정합. |
| **리뷰어 (Codex)** | `verbosity` 검출 시 reformulation 결과도 brevity 준수 의무 — 장황 reject 한 본인이 reformulation 으로 더 장황한 결과 산출 = 자기모순. round N+1 입력 질문이 round N 보다 길어진 경우 Orchestrator 가 reformulation 거부 후 round N+1 skip → fall-through 조기 진입 가능. |

**A5. debate-protocol-v1 lane-agnostic 미사용 (단순 Codex self-iteration 채택)**

본 iterative reformulation 은 `debate-protocol-v1` (CFP-391 / ADR-059) 의 multi-round adversarial debate 와 분리:

| 영역 | debate-protocol-v1 (ADR-059) | Amendment 2 iterative reformulation |
|---|---|---|
| 참여자 | 2 agent (Claude worker + Codex worker) adversarial | 1 agent (Codex single-shot self-iteration) |
| Role lock | 의무 (anti-sycophancy) | 불필요 — 단일 agent 의 동일 task 반복 |
| Anchor 재발 | escalation 채널 (anchor_recurrence_count >= 2) | N/A — round 자체가 anchor 단위 |
| Transcript 영속화 | Story §9 inline append 의무 | N/A — derived default (Orchestrator turn 내 transient) |
| Trigger | divergence 자동 감지 (severity / recommendation 불일치) | Codex `reject` decision (ambiguity / verbosity) |

`debate-protocol-v1` 채택 시 over-engineering — 본 영역은 단일 agent self-iteration 으로 충분 (사용자 발화 directive 1 문장의 "Codex 에 리뷰 요청 … 다시 재구성하여 리뷰" 패턴이 self-iteration 정합).

**A6. ADR-064 §결정 3 룰 5 정합 보존**

본 Amendment 가 적용된 후에도 ADR-064 §결정 3 룰 5 (`AskUserQuestion` 범위 제한 = 가치 판단 / 미공개 컨텍스트 2 종 한정) invariant 유지. 즉:

- derived default 도출 가능 영역 = `AskUserQuestion` 자체 발화 금지 — touchpoint #1 진입 자체 차단 (ADR-064 §결정 3 룰 1 정합)
- 진짜 `AskUserQuestion` 발화 결정된 영역에서만 touchpoint #1 iterative reformulation 진입

본 Amendment 2 는 `AskUserQuestion` 발화 결정 이후의 질문 품질 강화 channel — `AskUserQuestion` 발화 자체 의사결정은 ADR-064 §결정 3 SSOT.

**A7. ProactiveCheckPacket schema 변경 없음**

기존 D3 ProactiveCheckPacket v1 스키마 유지. iterative dispatch 의 round 별도 input/output 은 동일 schema 의 다중 dispatch 로 표현 — schema 신규 field 불필요. round 추적은 Orchestrator turn 내 inline counter (transient, persistence 불필요 — A5 의 transcript 영속화 부재 정합).

**A8. D2 자동 활성 정합 보존**

기존 D2 "opt-in 없음, 6 touchpoint 자동 활성" 의미 변경 없음. iterative 격상 후에도 touchpoint #1 자동 활성 유지 — sub-trigger 만 추가 (Codex `reject` 시 추가 round).

### 결과 (Amendment 2)

- Touchpoint #1 의 단일-shot dispatch → iterative reformulation 흐름 격상 (playbook §3.10.1 patch — max 3 rounds + fall-through 정책 명시)
- ADR-064 §결정 3 룰 4 (질문 brevity) 의 mechanical enforcement channel 신설 — `verbosity` reject 기준 SSOT
- ADR-064 §결정 3 룰 5 (`AskUserQuestion` 범위 제한) invariant 보존 — 본 Amendment 는 발화 결정 이후 영역만 다룸
- D1/D2/D3/D4 결정 본문 의미 변경 없음 — Amendment 2 sub-section 만 append (Amendment 1 패턴 정합)
- ProactiveCheckPacket schema MAJOR / MINOR bump 불필요 — round 추적은 Orchestrator inline state

### 거절된 대안 (Amendment 2)

- (Amendment-D) `debate-protocol-v1` lane-agnostic 패턴 채택 (Codex worker single + Claude worker single 형태로 adversarial debate) — 본 영역은 질문 품질 refinement 단순 self-iteration 영역, adversarial 불필요. role_lock / anchor 재발 / transcript 영속화 overhead 모두 정당성 부재. A5 비교 표 참조.
- (Amendment-E) Max 5 rounds (debate-protocol-v1 align) — 사용자 발화 directive verbatim "최대 3회 반복" SSOT. 5 rounds 채택은 사용자 directive 약화 = ADR-058 §결정 5 sunset_justification 의무 + ADR-064 §결정 7 top-down ratchet 위배.
- (Amendment-F) Round 별도 transcript Story §9 inline append (debate-protocol-v1 align) — proactive check 영역은 verdict 산출 channel 아님 (사용자 dialog 의 pre-formatting 만). FIX 흐름 reasoning carryover 도 부재 (FIX ledger row append 없음). 영속화 채널 부재 정당. A5 비교 표 참조.
- (Amendment-G) Touchpoint #1 외 5 touchpoint 동시 iterative 격상 — 다른 5 touchpoint 는 verdict producer 또는 root cause 판정 영역, 단순 question refinement 와 영역 분리. 별도 carrier 검토 필요 (현재 CFP 미할당).

---

## Amendment 3 (2026-05-13, CFP-510)

### Context

Amendment 1 (CFP-411) 이 touchpoint #4 를 multi-round adversarial debate (`debate-protocol-v1`) 영역으로 격상하면서 `divergence detection 3 criteria` 를 명시했다 — **AC 의미 차이** / **Edge Case 누락** / **Why 해석 mismatch**. 세 항목 모두 **semantic** 영역 (의미 / 가치 / 의도) 으로 PL LLM 판정에 의존.

CFP-451 (`#451`, merged) + CFP-490 (`#490`, merged) 양 Story 의 0-FIX chain 7-8번째 retro 에서 동일 패턴이 2 회 누적 evidence:

- Codex proactive check #4 가 PL synthesis 의 **사실 영역** (registry entry execution status / 이전 PR leak / file path / cross-repo state) 까지 실제로 검증하고 발견을 던졌다 — 즉 fact-check 영역은 **이미 작동 중**.
- 그러나 현 ADR-052 Amendment 1 SSOT 는 이 fact-check 영역을 명시하지 않음 — implicit 발화 상태.
- PL 이 자기 synthesis 작성 시 "가설" vs "verified fact-check pending" 영역 구분 의무 부재 → Codex 가 fact 발견을 던질 때 PL 이 "이미 verified 한 fact" 로 오인 → divergence detection LLM 판정 false negative 위험.

본 Amendment 는 이 implicit 영역을 explicit normative anchor 로 승격한다.

### 결정 (Amendment 3)

**A1. Touchpoint #4 divergence detection 영역 확장 — semantic 3 + factual 1 = 4 영역**

기존 Amendment 1 의 3 semantic criteria 유지 + 4번째 영역 **factual** 추가:

| # | 영역 | 분류 | 운영적 정의 |
|---|---|---|---|
| 1 | AC 의미 차이 | semantic | Story §5 의 AC-N 항목과 Codex 제안 AC 가 검증 가능한 분기 행동 차이 (Amendment 1 SSOT 보존) |
| 2 | Edge Case 누락 | semantic | Codex 가 제기한 edge case 가 PL synthesis §5.3 / §6 어디에도 매핑되지 않음 (Amendment 1 SSOT 보존) |
| 3 | Why 해석 mismatch | semantic | 사용자 §1 원문의 root why 에 대해 PL 과 Codex 가 다른 가치 우선순위 제시 (Amendment 1 SSOT 보존) |
| **4** | **Fact-check** | **factual** | **PL synthesis 의 사실 claim (registry entry / 이전 PR leak / file path / cross-repo state) 이 Codex 가 read-only verify 한 사실과 불일치** |

4번째 영역 hit 시 `divergence_type: factual` (debate-protocol-v1 registry §2.1 enum 확장 — 별도 follow-up CFP 가 schema MINOR bump). polyfill (본 Amendment 3 effective 시점 ~ enum 확장 CFP merge 전) = `divergence_type: semantic` 으로 통합 발화 + Story §9.0 entry 에 sub-tag `[factual]` 명시.

**A2. Fact-check sub-criteria 4종**

4번째 영역의 sub-criteria 4종 (각 sub-criterion 은 Codex worker 가 read-only verify 가능):

| Sub-criterion | 운영적 정의 | 검증 도구 |
|---|---|---|
| **registry-execution drift** | PL synthesis 가 인용한 registry entry (`docs/evidence-checks-registry.yaml` / `docs/inter-plugin-contracts/MANIFEST.yaml` 등) 의 실제 status 와 PL 인용 status 불일치 (예: PL 인용 "tier: warning" vs 실제 "tier: blocking-on-pr") | `Read` + `Grep` |
| **pre-existing leak** | PL synthesis 가 "신규 발견 issue" 로 분류한 항목이 이전 PR / 이전 Story 에서 이미 leak 된 상태 (즉 본 Story 가 fix carrier 가 아닌 audit carrier) | `gh search code` + `gh pr list` + `git log -S` |
| **file path verification** | PL synthesis 가 인용한 file path / line number / 함수명이 실제 코드베이스 상태와 불일치 (rename / move / 삭제) | `Glob` + `Read` |
| **cross-repo state verification** | PL synthesis 가 인용한 cross-plugin / cross-repo state (sibling plugin version / contract sibling sync status / marketplace.json mirrored field) 가 실제 cross-repo HEAD 와 불일치 | `gh api repos/*/contents/*` + `Read` |

본 4 sub-criterion 외 영역도 factual 일 수 있으나 (예: shell command 실행 결과 검증), Codex worker 의 `Bash(codex exec *)` 만 허용된 read-only 제약 (codex-proactive-check.md agent file) 정합 — 외부 shell 실행 영역은 Codex worker 미관여, RequirementsPL 자체 책임.

**A3. PL self-evaluation 의무 — 가설 vs verified 분리 명시**

RequirementsPLAgent 가 §2/§5/§6 synthesis 작성 시 fact claim 영역에 대해 다음 4종 marker 중 1종 의무 부착:

| Marker | 의미 | 후속 동작 |
|---|---|---|
| `[verified]` | PL 이 직접 Read/Glob/Bash 로 검증 완료 | 검증 evidence 1-line 인용 의무 (file:line 형식) |
| `[hypothesis]` | PL 이 추론한 가설 (검증 미수행) | Codex proactive check 가 verify 의무 — divergence detection 4번째 영역 trigger 가능 |
| `[fact-check-pending]` | 검증 의도는 있으나 본 turn 에서 미완료 | Codex worker 결과 수신 후 PL 이 즉시 verify + marker 갱신 의무 |
| `[user-input]` | 사용자 §1 원문 verbatim — 검증 대상 외 | 변조 금지 invariant (story-section-1-immutable.yml SSOT) |

Marker 부재 = 암묵적 `[hypothesis]` (안전 방향 default). consumer overlay 로 marker 어휘 변경 불가 (정책 축소 불허 — ADR-064 §결정 7 top-down ratchet 정합).

**A4. Reverse-explicit 의무 — 검증 불가 영역 명시**

PL 이 fact claim 영역인데 도구 한계로 검증 불가능 (예: 외부 API state / runtime measurement) 한 경우, `[fact-check-pending]` 대신 `[verification-out-of-scope: <사유>]` marker 부착. 사유 필드 verbatim 의무 (예: `[verification-out-of-scope: external API state, runtime probe required]`). 본 marker 부착 시 Codex proactive check 4번째 영역 hit 면제 (divergence detection false positive 차단).

**A5. debate-protocol-v1 dispatch 흐름 변경 없음**

Amendment 1 의 dispatch 흐름 (min 3 / max 5 / soft default 4 / PL = synthesizer / anchor_id = `cfp-NNN-requirements-divergence-N`) 그대로 적용. divergence type 만 확장:

- `divergence_type: semantic` (기존 3 criteria) — Amendment 1 SSOT 보존
- `divergence_type: factual` (4번째 criteria) — 본 Amendment 3 신설 (polyfill 시점 = `semantic` + `[factual]` sub-tag)

매 라운드 carryover input 흐름 / Story §9.0 transcript append 의무 / FIX 흐름 redo 대상 (RequirementsPL 자체) 모두 변경 없음.

**A6. ProactiveCheckPacket schema 변경 없음**

D3 ProactiveCheckPacket v1 schema 그대로 유지. findings[] 의 description 영역에 fact-check sub-criterion 명시 의무는 Codex worker prompt engineering 영역 (codex-proactive-check.md agent file 본문, sibling sync follow-up). schema MINOR bump 불필요.

**A7. D2 자동 활성 정합 보존**

D2 "opt-in 없음, 6 touchpoint 자동 활성" 의미 변경 없음. 4번째 영역 확장 후에도 touchpoint #4 자동 활성 유지 — sub-trigger 만 추가 (factual divergence 감지 시 동일 debate 흐름).

**A8. Amendment 1 SSOT 보존**

Amendment 1 의 3 semantic criteria 본문 (RequirementsPLAgent.md §"Codex Proactive Check + 의미적 divergence debate" 의 "Divergence detection 3 criteria" 단락) 의미 변경 없음. 본 Amendment 3 가 4번째 영역만 append — 기존 3 criteria 의 PASS 기준 / phrasing 차이 면제 / out-of-scope 처리 invariant 보존.

### 결과 (Amendment 3)

- Touchpoint #4 divergence detection 영역 = 3 semantic + 1 factual = 4 영역 (현재 implicit 영역의 explicit normative anchor 승격)
- RequirementsPLAgent §2/§5/§6 synthesis 작성 시 fact claim 영역 marker 4종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]`) + reverse-explicit `[verification-out-of-scope: <사유>]` 의무
- codeforge-requirements `RequirementsPLAgent.md` + `codex-proactive-check.md` sibling sync (본 Story Phase 1 PR 의 sibling)
- debate-protocol-v1 registry §2.1 enum 확장 (`divergence_type` 에 `factual` 추가) = follow-up CFP carrier (본 Story scope 외, polyfill 정책 SSOT 만 본 Amendment 보유)
- D1/D2/D3/D4 결정 본문 + Amendment 1/2 본문 의미 변경 없음 — Amendment 3 sub-section 만 append (Amendment 1/2 패턴 정합)

### 거절된 대안 (Amendment 3)

- (Amendment-H) `divergence_type` enum 확장을 본 Amendment 와 함께 동일 PR 으로 처리 — 본 Story scope 가 ADR amendment + sibling agent file sync 만 (doc-only fast-path 적용 대상). registry schema MINOR bump 는 별도 contract sibling sync + MANIFEST 갱신 의무 → 별도 CFP carrier 분리.
- (Amendment-I) Fact-check sub-criteria 를 4종 외 확장 (shell command 실행 결과 / runtime measurement 등) — Codex worker permission 제약 (read-only) 정합 외. consumer overlay 도 정책 확장만 허용 (축소 불허) 이므로 본 ADR 영역 외 sub-criterion 은 consumer 가 자체 도입 가능 (정합).
- (Amendment-J) Marker 어휘 변경 가능 (consumer overlay) — ADR-064 §결정 7 top-down ratchet 위배. Marker 어휘 SSOT = 본 ADR-052 Amendment 3 §A3 표 verbatim.
- (Amendment-K) `[hypothesis]` default 대신 `[verified]` default — 안전 방향 위반 (false negative 위험 증가). default 안전 방향 = `[hypothesis]` (Codex verify 영역 진입) 유지.

---

## Amendment 4 (2026-05-13, CFP-532)

### Context

Epic CFP-425 (worktree-first mechanical enforcement 영구화) 가 4 Story 누적 (CFP-426 + CFP-427 + CFP-428 + CFP-429) + 2 carry-over Story 로 6 sample evidence 확보. 매 Story 의 설계 lane 진입 시점에 Codex Proactive Touchpoint #2 (Design Synthesis Check — ArchitectAgent §3 Change Plan 초안 완료 직후 ArchitectPLAgent 전달 직전) 가 자동 dispatch 되었고, **6/6 dispatch 가 ArchitectAgent §3 산출물 결함을 review lane 진입 전 inline FIX 로 해소**.

가장 강한 sentinel = CFP-429 retro `sentinel_refs` (verbatim 인용):

> "ADR-052 — Codex Proactive Check Touchpoint #2 (Design Synthesis) 4 finding 발견 + ArchitectPL FIX iter 1 inline 해소 (Touchpoint #4 PROCEED 와 분리)"

EPIC-RESULTS-CFP-425 §7.2 carrier #3 verbatim (sample 6 = 100% review lane FIX 회피):

> "MEDIUM-HIGH — ADR-052 Amendment N Touchpoint #2 mandatory: CFP-429 retro §6.2 / sample 6 누적 (Story 1-4 + 2 carry-over) — 모든 review lane FIX 회피. mandatory 전환 sentinel 통계 유의 충족."

기존 D2 결정 ("opt-in 없음, 6 touchpoint 자동 활성") 는 dispatch 자체는 자동 발동 정합이나, **Orchestrator 가 dispatch 결과의 `recommendation = ADDRESS_FIRST` 발화 시 Orchestrator skip 가능 영역** 이 P1-only findings 에 대해 열려 있음 (playbook §3.10 결과 처리 표 row 3 = "P1-only → Orchestrator 판단으로 skip 가능 → story §10 기록"). 본 Amendment 는 **touchpoint #2 단독** 으로 이 skip 영역을 닫는다.

### 결정 (Amendment 4)

**A1. Touchpoint #2 optional → mandatory 전환**

기존 §3.10.2 Design Synthesis Check 동작:

- (기존) Orchestrator 가 ArchitectAgent §3 완료 직후 codex:codex-rescue dispatch → Codex `{findings, recommendation}` 수신 → Orchestrator 가 `recommendation` 기반 처리 결정 (PROCEED / ADDRESS_FIRST P0 blocking / ADDRESS_FIRST P1-only skip 가능)
- (Amendment 4 후) Orchestrator 가 ArchitectAgent §3 완료 직후 codex:codex-rescue dispatch → Codex `{findings, recommendation}` 수신 → **Orchestrator 가 모든 finding (P0 + P1) 을 의무 inline FIX (skip 영역 차단)**. P2 finding 만 Orchestrator 판단으로 Story §10 deferred 기록 가능

**A2. 6 sample success rate 100% sentinel (mandatory 전환 통계 근거)**

| Story | Touchpoint #2 dispatch | Finding count | review lane FIX 발생 여부 | inline FIX 해소 |
|---|---|---|---|---|
| CFP-426 (Epic CFP-425 Story 1, skeleton 4 entry) | 활성 | 2 finding | 미발생 | DONE (ArchitectPL FIX inline) |
| CFP-427 (Story 2, SessionStart hook 2/4 actual wire) | 활성 | 1 finding | 미발생 | DONE (ArchitectPL FIX inline) |
| CFP-428 (Story 3, git layer 2/4 actual wire) | 활성 | 2 finding | 미발생 | DONE (ArchitectPL FIX inline) |
| **CFP-429 (Story 4, story-init reminder + E4 self-test, Amendment 4 declaration carrier)** | **활성** | **4 finding (F-001 critical + F-002/F-003/F-004 major)** | **미발생** | **DONE (ArchitectPL FIX iter 1 inline 해소, retro sentinel_refs verbatim)** |
| Carry-over Story #1 (CFP-429 retro `sentinel_refs` verbatim — Story key audit anchor 미명시, retro SSOT 영역) | 활성 | 1+ finding | 미발생 | DONE |
| Carry-over Story #2 (CFP-429 retro `sentinel_refs` verbatim — Story key audit anchor 미명시, retro SSOT 영역) | 활성 | 1+ finding | 미발생 | DONE |

**누적 dispatch 수 = 6** (verified-direct 4 = CFP-426/427/428/429 + sentinel-derived 2 = carry-over retro inheritance), **review lane FIX 발생 = 0**, **inline FIX 해소율 = 100%**. ADR-060 evidence-enforceable promotion framework 의 통계 기준 (sample ≥ 6 + failure 0) 에 부합 — sentinel 통계 유의 충족.

본 통계 정의 (audit 가능성 분해):
- **분모** = touchpoint #2 dispatch 가 활성된 Story 수 (6 = direct verified 4 + sentinel-derived 2)
  - **direct verified 4** = CFP-426 (Epic CFP-425 Story 1) / CFP-427 (Story 2) / CFP-428 (Story 3) / CFP-429 (Story 4) — 4 Story 모두 Story file §9 verdict 또는 retro `sentinel_refs` 에 dispatch 활성 + inline FIX 해소 evidence 보존
  - **sentinel-derived 2** = CFP-429 retro `sentinel_refs` verbatim 인용 "sample 6 누적 (Story 1-4 + 2 carry-over)" — carry-over 2건 식별자 = retro SSOT 자체 영역 (본 Amendment scope 외, retro 작성 시점 PMOAgent 인용 anchor). 독립 검토자 audit 시 = retro 원문 verbatim 추적 의무 + carry-over 식별자 별도 follow-up 추적 가능 (본 ADR scope 외)
- **분자 (review-lane FIX 회피 성공)** = dispatch 결과 finding 을 inline FIX 로 해소한 Story 수 (6)
- **window** = CFP-426 Story 1 dispatch (Epic CFP-425 시작) ~ CFP-429 retro 작성 시점 (2026-05-13 KST)
- **재현 가능성**: direct verified 4 = Story file + retro 원문 직접 audit 가능. sentinel-derived 2 = retro `sentinel_refs` SSOT 인용 영역 — retro 자체가 PMOAgent self-write 영역 (codeforge-pmo lane scope), 본 Amendment 는 retro 인용 충실성만 보존.

**A3. 6 touchpoint 중 #2 단독 mandatory 결정 근거**

다른 5 touchpoint 와 #2 의 차별점 = **§3 Change Plan = 모든 후속 lane (구현 / 구현리뷰 / 보안테스트) 의 입력 baseline**. §3 결함이 review lane 진입 후 발견되면 ArchitectAgent re-run + Change Plan v+1 + 모든 후속 lane 재실행 = FIX 비용이 lane 수의 multiplicative growth. 본 Amendment 의 mandatory 전환은 이 multiplicative growth 의 single highest-ROI prevention point 를 closing.

| Touchpoint | Cost 회피 magnitude | mandatory 전환 적격 |
|---|---|---|
| #1 Pre-question Review | 1 사용자 dialog | LOW — Amendment 2 iterative reformulation 으로 별도 강화 채널 활성 |
| **#2 Design Synthesis Check** | **N lane re-run (multiplicative)** | **HIGH — 본 Amendment 4 mandatory 전환** |
| #3 Development Rescue | FIX 2+ 반복 (이미 trigger 가 reactive) | LOW — trigger 자체가 already-stuck 상태, optional 유지 |
| #4 Requirements Output Review | 1 lane (Requirements) re-run | MEDIUM — Amendment 1 multi-round debate 로 별도 강화 채널 활성 |
| #5 FIX Root Cause 2nd Opinion | 1 판정 (사용자 escalation 가능) | LOW — D4 가 이미 사용자 escalation channel 강제 |
| #6 ADR Draft Review | ADR re-author (single doc) | LOW — single artifact scope, blocking cost 작음 |

mandatory 전환 적격성 = **#2 단독 HIGH**. 나머지 5 touchpoint 는 별도 강화 채널 활성 또는 cost magnitude 작음 → optional 유지.

**A4. mandatory dispatch behavior — Orchestrator skip 영역 차단**

기존 playbook §3.10 결과 처리 표 (verbatim):

| recommendation | findings | 처리 |
|---|---|---|
| PROCEED | — | 그대로 다음 단계 |
| ADDRESS_FIRST | P0 포함 | 해당 agent findings 반영 후 재진행 (blocking) |
| ADDRESS_FIRST | P1-only | Orchestrator 판단으로 skip 가능 → story §10 기록 |
| 판정 불일치 (#5 전용) | — | 사용자 에스컬레이션 |

touchpoint #2 mandatory 적용 시 P1-only row 가 다음과 같이 변경:

| recommendation | findings | 처리 (touchpoint #2 mandatory) | 처리 (touchpoint #1/#3/#4/#5/#6 optional 유지) |
|---|---|---|---|
| PROCEED | — | 그대로 다음 단계 | 그대로 다음 단계 |
| ADDRESS_FIRST | P0 포함 | 해당 agent findings 반영 후 재진행 (blocking) | 동일 |
| ADDRESS_FIRST | P1-only | **inline FIX 의무 (skip 차단)** | Orchestrator 판단으로 skip 가능 → story §10 기록 |
| ADDRESS_FIRST | P2-only | Orchestrator 판단으로 Story §10 deferred 기록 가능 | 동일 |

P2 영역은 mandatory 적용 외 — P2 = nice-to-have / minor improvement / cosmetic 영역, blocking cost 정당성 부재. 6 sample evidence 도 모두 P0/P1 영역 발견 (P2-only 시 review lane FIX 발생 위험 evidence 부재).

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = **강화 방향** (optional → mandatory):
- `is_transitional: false` (permanent governance, mandatory transition = permanent strengthening)
- `sunset_justification: "N/A — mandatory transition = permanent strengthening, ADR-064 active amendment 정합"`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (mandatory → optional 또는 strict → loose) 에만 발효 → 본 Amendment 는 면제

**A6. ADR-064 §결정 (Trace 1) active amendment 정합**

ADR-064 결정 원칙 4 어휘 anchor (best-effort / broad coverage / full-scope / active amendment) 중 **active amendment** 정합:
- Amendment 발의 시점 = ratchet 강화 방향 적극 발의
- 본 Amendment **normative decision text** (§Context + §A1~§A9 결정 + §결과) forbid-list 8 어휘 사용 0건. 거절된 대안 (§Amendment-L~§Amendment-P) 영역의 forbid-list dictionary 자체 인용 (Amendment-O 등) 은 dictionary reference (meta-citation) 영역 — normative scope 외, ADR-064 §결정 2 dictionary lint scope 정합 (forbid scope = 결정 채택 영역, 거절 근거 dictionary 인용 면제). consumer overlay 정책 축소 불허 invariant 정합 보존

**A7. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment scope:
- ADR-052 본문 + frontmatter `amendments[]` row 4 append
- CLAUDE.md "Codex Proactive Check" blockquote 갱신 (touchpoint #2 mandatory marker 명시)
- playbook §3.10 결과 처리 표 + §3.10.2 표 갱신

src/** 변경 0건. tests/** 변경 0건. agent file 변경 0건. doc-only fast-path 거부 조건 (ADR-054 §결정 1) 모두 미해당 → 적용 가능.

**A8. skill orchestration code mandatory branch logic 별도 carrier 분리**

자율 prompt SSOT verbatim ("Step 5 skill orchestration code 변경은 선택 (별도 carrier 가능). 본 Story = ADR + 2 doc 갱신만") 정합. mandatory branch logic 의 skill 자체 갱신 (`codeforge:codex-proactive-check` skill 의 dispatch logic) 은 본 Story scope 외 — 별도 follow-up CFP carrier 분리. 본 Amendment effective 시점 ~ skill code 갱신 사이 = Orchestrator 가 doc SSOT 기반 mandatory 적용 의무 (도덕적 강제, mechanical enforcement 부재).

**A9. D1/D2/D3/D4 결정 본문 의미 변경 없음**

기존 D1 (codex:codex-rescue dispatch 채널) / D2 (6 touchpoint 자동 활성) / D3 (ProactiveCheckPacket v1) / D4 (#5 판정 불일치 = 사용자 escalation) 모두 의미 변경 없음. 본 Amendment 4 = §3.10.2 (touchpoint #2) 의 sub-behavior 강화만 — D1/D2/D3/D4 의미 invariant 보존 (Amendment 1/2/3 패턴 정합).

### 결과 (Amendment 4)

- Touchpoint #2 (Design Synthesis Check) optional → mandatory 전환 — Orchestrator 가 dispatch 결과 P0 + P1 finding 모두 inline FIX 의무 (skip 영역 차단)
- playbook §3.10 결과 처리 표 + §3.10.2 단락 mandatory marker 명시
- CLAUDE.md "Codex Proactive Check" blockquote 갱신 (1 mandatory + 5 optional 명시)
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A)
- ADR-064 §결정 (Trace 1) active amendment 정합 (forbid-list 8 어휘 사용 0건)
- doc-only fast-path 적용 (ADR-054 §결정 1) — src/tests/agent file 변경 0건
- skill orchestration code mandatory branch logic = 별도 carrier 분리 (후속 CFP)
- D1/D2/D3/D4 결정 + Amendment 1/2/3 본문 의미 변경 없음 — Amendment 4 sub-section 만 append

### 거절된 대안 (Amendment 4)

- (Amendment-L) **6 touchpoint 전체 동시 mandatory 전환** — 다른 5 touchpoint 는 cost magnitude 작거나 별도 강화 채널 (Amendment 1/2) 활성. 모든 touchpoint mandatory 시 dispatch 결과 P1-only finding 의 skip 차단으로 false positive blocking 비용 증가 위험. A3 비교 표 정합 — #2 단독 mandatory 채택. 다른 5 touchpoint 의 mandatory 전환은 각각 별도 evidence 누적 후 별도 Amendment carrier (CFP-TBD).
- (Amendment-M) **mandatory 적용 영역을 P0 finding 만으로 한정** — 기존 D2/§3.10 P0 blocking 처리는 이미 mandatory 동등 (Orchestrator skip 채널 부재). 본 Amendment 는 P1-only skip 영역 차단이 핵심 — P0-only mandatory 채택 시 sentinel 의미 부재 (6 sample evidence 의 4 finding F-002/F-003/F-004 major 가 P1 등급 — P0 한정 시 evidence 적용 영역 외).
- (Amendment-N) **mandatory 전환 + skill orchestration code 동시 갱신** — Story scope 확장 (doc-only fast-path 거부 트리거). 본 Amendment 의 evidence-only 영역 (doc + ADR) 과 mechanical code 영역 (skill) 분리 → 별도 carrier (CFP-TBD) 정당성 보존. skill code 갱신 시점 = Amendment 4 SSOT effective 후 follow-up carrier merge 시점, gap 기간 = Orchestrator 도덕적 강제 (mechanical enforcement 부재 의식 필요).
- (Amendment-O) **grace period 도입** (Amendment 4 effective 후 N Story 동안 mandatory soft-enforce 후 hard-enforce) — ADR-064 §결정 7 top-down ratchet 정합 외 (`임시` / `단계적` 의미 forbid-list 정합 외). 즉시 mandatory 적용 — sample 6 evidence 가 이미 ratchet 강화 정당성 충족. consumer overlay 도 정책 축소 불허 (mandatory → optional 다운그레이드 차단).
- (Amendment-P) **Touchpoint #2 mandatory 전환 + 자동 retry 채널 신설** (Codex dispatch failure / timeout 시 Orchestrator 가 자동 재시도) — codex CLI runtime 영역 (codex:codex-cli-runtime SSOT) 정합 외, retry 정책은 별도 ADR carrier 영역. 본 Amendment 4 scope = dispatch 결과 처리 mandatory 강화만.

---

## Amendment 5 (2026-05-13, CFP-578)

### Context

Codex worker (codex:codex-rescue subagent) 의 sandbox-level file system access 실패가 3 회 reproduce 누적 (CFP-506 / CFP-520 / CFP-530) — ADR-052 6 touchpoint 자동 dispatch 영역의 systemic 원인. 가장 강한 sentinel = CFP-506 retro §6 verbatim:

> "Codex sandbox file system access 실패가 false positive 의 systemic 원인 — 향후 Codex proactive check 결과 verify-before-trust 채널 필요"

3 retro reproduce evidence:

- CFP-506 touchpoint #4 file Read 시도 → ERR `경로는 존재하지 않으므로 찾을 수 없습니다` → Orchestrator 가 file content verbatim 첨부 후 re-spawn 정상 audit
- CFP-506 touchpoint #6 4 findings 발화 → direct file Read verify 결과 4 findings 모두 false positive (ADR-012 Pre-Amendment 본문 인용 = 외부 fetch / GPT-5.4 training data stale source)
- CFP-520 touchpoint 6종 모두 skip rationale 정합 (sandbox access cost 회피 derived default)
- CFP-530 touchpoint #6 skip option B Codex sandbox 실패 evidence (3 회 reproduce 누적 sentinel chain closure)

기존 D3 (ProactiveCheckPacket v1) + Amendment 1/2/3/4 (각 touchpoint 동작 강화) 는 6 touchpoint 별도 동작 강화 영역만 다룸 — Codex worker spawn prompt 안 file content **payload 형식** (file path reference vs verbatim 첨부) 의 normative anchor 부재.

본 Amendment 는 신규 ADR-070 (verify-before-trust pattern) 의 §결정 D2 (file content verbatim 첨부 의무) + §결정 D4 (ADR-052 cross-ref) 를 본 ADR-052 본문 normative anchor 로 승격한다.

### 결정 (Amendment 5)

**A1. 6 touchpoint 자동 dispatch 영역의 verbatim 첨부 의무 명시**

기존 D3 ProactiveCheckPacket v1 schema (verbatim):

```yaml
touchpoint: <1|2|3|4|5|6|7|8>
purpose: <한 줄 목적>
context:
  lane: <requirements|design|develop|orchestrator>
  story_key: <CFP-NNN>
  artifacts: <첨부 산출물>
task: <Codex에게 요청할 구체적 작업>
```

Amendment 5 후 `artifacts` 필드의 운영적 정의 명시:

| 영역 | 운영적 정의 |
|---|---|
| **artifacts 필드 본문** | file path reference 만 사용 금지. 모든 file content 가 verify task scope 인 경우 prompt payload 안 verbatim 첨부 필수 (sandbox 영역 외 file 전체) |
| **verbatim 첨부 대상** | (1) 사용자 §1 원문 (story-section-1-immutable.yml SSOT 영역, 변조 금지 invariant 정합) / (2) Story §2-§6 / §7 PL synthesis 본문 / (3) 관련 ADR / Change Plan 본문 / (4) cross-repo 인용 (sibling plugin file / marketplace.json / contract MANIFEST) |
| **partial 첨부 허용 영역** | file content cap 초과 시 (token 비용 risk) — verify 대상 영역만 verbatim 첨부 + 나머지 file path reference 표시 + `[partial: lines NN-NN]` marker 의무 |

**A2. verify-before-trust 채널 cross-ref (ADR-070 §결정 D1)**

Codex worker 결과 수신 후 Orchestrator 는 finding evidence (인용 본문 / file path / line number / commit SHA / contract version 등) 의 ground truth 를 own working directory 안 Read / Glob / Grep 으로 verify 의무. mismatch 검출 시 finding reject + Story §10 FIX Ledger row append (false positive count tally) + Orchestrator override rationale 명시 (ADR-070 §결정 D3 정합).

본 Amendment 본문 = ADR-070 §결정 D1 / D2 / D3 의 ADR-052 본문 cross-ref 만 — 결정 본문 SSOT 는 ADR-070.

**A3. dispatch prompt template patch (playbook §3.10)**

playbook §3.10 (Codex Proactive Check SSOT) 안 dispatch 패턴 본문 갱신:

| 영역 | 갱신 |
|---|---|
| **Dispatch 패턴** | 기존 `Agent(subagent_type="codex:codex-rescue", prompt=<ProactiveCheckPacket>)` 유지 |
| **ProactiveCheckPacket `artifacts` 필드** | verbatim 첨부 의무 본문 명시 (A1 표 verbatim cross-ref) |
| **결과 처리** | verify-before-trust 단계 신설 (Codex 결과 수신 후 ground truth verify 의무) — ADR-070 §결정 D3 reject 흐름 cross-ref |

**A4. 6 touchpoint 자동 dispatch 영역 invariant 보존**

기존 D2 (6 touchpoint 자동 활성, opt-in 없음) + Amendment 1/2/3/4 (각 touchpoint 동작 강화) 의미 변경 없음. 본 Amendment 5 = artifacts 필드 payload 형식 + verify-before-trust 결과 처리 추가만 — dispatch 자체 흐름 invariant 정합.

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향:

- `is_transitional: false` (permanent governance, verbatim 첨부 의무 + verify-before-trust = permanent strengthening)
- `sunset_justification: "N/A — permanent strengthening, ADR-064 active amendment 정합 — Codex sandbox 영역 변경 없으면 permanent retain"`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (verbatim 의무 → file path reference 허용 또는 verify-before-trust → trust default) 에만 발효 → 본 Amendment 는 면제

**A6. ADR-064 §결정 (Trace 1) active amendment 정합**

ADR-064 결정 원칙 4 어휘 anchor (best-effort / broad coverage / full-scope / active amendment) 중 **active amendment** + **full-scope** 정합:

- Amendment 발의 시점 = 3 회 reproduce sentinel 도달 후 즉시 (active amendment ratchet 강화 방향)
- 적용 영역 = ADR-052 6 touchpoint 모두 (full-scope, 단일 touchpoint 한정 아님)
- 본 Amendment normative decision text (§Context + §A1~§A8 결정 + §결과) forbid-list 8 어휘 사용 0 건 self-attest

**A7. doc-only fast-path 정합 (ADR-054 §결정 1)**

본 Amendment 5 = ADR-052 본문 patch (Amendment row append + sub-section append) — src/** 변경 0 건 + tests/** 변경 0 건 + agent file 변경 0 건. 단 본 carrier 는 신규 ADR-070 동반 = ADR-054 §결정 1 거부 조건 (신규 ADR 도입 Story = full-lane 강제) 영역 정합. 즉 본 Amendment 자체는 doc-only fast-path 적격이나 carrier Story (CFP-578) 전체는 full-lane 진행.

**A8. D1/D2/D3/D4 결정 본문 + Amendment 1/2/3/4 본문 의미 변경 없음**

기존 D1 (codex:codex-rescue dispatch 채널) / D2 (6 touchpoint 자동 활성) / D3 (ProactiveCheckPacket v1) / D4 (#5 판정 불일치 = 사용자 escalation) + Amendment 1/2/3/4 본문 의미 변경 없음. 본 Amendment 5 = Codex worker spawn prompt 안 payload 형식 + 결과 처리 verify-before-trust 단계 추가만 — sub-section append 패턴 정합 (Amendment 1/2/3/4 패턴 정합).

### 결과 (Amendment 5)

- 6 touchpoint 자동 dispatch 영역의 dispatch prompt template 안 file content verbatim 첨부 의무 본문 명시 — A1 SSOT
- verify-before-trust 채널 cross-ref (ADR-070 §결정 D1 / D2 / D3) — A2 SSOT
- playbook §3.10 dispatch 패턴 본문 patch (artifacts 필드 verbatim 첨부 의무 + verify-before-trust 결과 처리 단계 신설) — A3 SSOT
- 6 touchpoint 자동 dispatch invariant 보존 (Amendment 1/2/3/4 의미 변경 없음) — A4/A8 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A) — A5 SSOT
- ADR-064 §결정 (Trace 1) active amendment + full-scope 정합 (forbid-list 8 어휘 사용 0 건) — A6 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 5 자체) — carrier Story (CFP-578) 전체는 신규 ADR-070 동반 full-lane 진행 — A7 SSOT

### 거절된 대안 (Amendment 5)

- (Amendment-Q) **verbatim 첨부 의무 영역을 worktree 외 file 으로만 한정** — Codex worker 의 own working directory 와 wrapper worktree 일치 보장 부재 (ADR-040 worktree convention 영역의 cross-cutting boundary). codex CLI runtime working directory inject layer 부재 (codex:codex-cli-runtime SSOT 영역) — worktree 안 file 도 codex sandbox 영역 외 가능성 보유. 따라서 worktree 외 한정 적용은 systemic 원인 해소 영역 부족 → 전체 verbatim 첨부 의무 채택. ADR-070 §결정 D2 cross-ref.
- (Amendment-R) **자동 file content injection layer 도입** (Orchestrator 가 spawn prompt 파싱 → file path reference 자동 verbatim 변환) — Orchestrator turn 내 inline action 영역 외 (별도 carrier 필요), mechanical injection layer 신설 = 별도 ADR carrier 영역. ADR-070 §결정 D2 거절 대안 (D2-C) 정합.
- (Amendment-S) **verify-before-trust 채널 도덕적 강제로 한정** (normative anchor 부재) — 3 회 reproduce sentinel 누적 evidence 가 normative 승격 정당성 충족. ADR-070 §결정 D1 거절 대안 (D1-C) 정합.
- (Amendment-T) **mechanical lint 도입** (Codex spawn prompt 안 file path reference 검출 static regex 또는 Codex output 안 sandbox access 실패 ERR 패턴 검출) — ADR-070 §결정 D5 (declaration-only retain) 정합. (a)/(b)/(c) 4 후보 모두 robustness risk 보유. evidence-checks-registry entry append 면제.

## Amendment 6 (2026-05-17 KST, CFP-819)

### Context

ADR-052 Amendment 5 (D2 verbatim 첨부 의무) + ADR-070 D2 (file content verbatim 첨부) 가 두 가지 normative anchor 를 명문화한 이후, **Codex worker prompt 본문의 mandatory section composition** 영역의 normative anchor 가 cross-document 분산 상태로 잔존. playbook §3.10 dispatch prompt template 이 SSOT 역할을 도덕적 강제로 수행 중이었다.

6-Story carry-over evidence sentinel (**"6-Story" 정의** — 1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0 = 6 units / 7 retro file):

- baseline cluster (1 unit, paired carrier): CFP-770 / CFP-771 (fp 8 합산, same incident, 2026-05-16, boilerplate pre-application)
- carry-over fp 0 (5 units): CFP-786 / CFP-801 / CFP-792 / CFP-795 / CFP-810 (5 consecutive, 2026-05-17)
- threshold reach: CFP-810 retro §6 carrier 5/7 sentinel reach YES

ADR-045 Amendment 5 §D-9 (`cross_story_pattern_adr_trigger`, pattern_count ≥ 2 forcing function) 충족 — escalation_action: `adr_draft_emitted` 영역 진입.

### 결정 (Amendment 6)

본 Amendment scope = ADR-052 본문 sub-section append (cross-ref 1 paragraph) 만. D1/D2/D3/D4 + Amendment 1-5 본문 의미 변경 0건.

**A1. boilerplate composition SSOT 분리 — 신규 ADR-081 cross-ref**

본 ADR 의 boilerplate composition 영역 (3 mandatory section + verify-before-trust scope 분리 + 3-lane partition) 을 신규 ADR-081 (Codex worker prompt boilerplate composition SSOT) 로 분리.

ADR-081 §결정 영역:

- D1 — 3 mandatory boilerplate 영역 (D1.A dogfood-out Story path / D1.B lane stage / D1.C sandbox boundary)
- D2 — verify-before-trust scope 5 sub-scope (D2.A file / D2.B dir / D2.C cross-repo / D2.D grep count active vs historical / D2.E ADR §결정 번호 정확성)
- D3 — 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style + history disjoint)
- D4 — ADR-052 / ADR-070 본문 정책 SSOT 보존 invariant
- D5 — evidence-enforceable framework entry append 면제 (declaration-only retain, ADR-070 §D5 precedent verbatim)

**A2. ADR-052 본문 정책 SSOT 보존 invariant**

본 Amendment 6 = sub-section append 패턴 (Amendment 1/2/3/4/5 패턴 정합). D1/D2/D3/D4 결정 본문 + Amendment 1-5 본문 의미 변경 없음. Codex worker dispatch 자체 흐름 invariant 정합.

**A3. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향 (ratchet 강화):

- `is_transitional: false` 본 ADR 유지 (permanent governance)
- `sunset_justification: "N/A — permanent strengthening (6-Story carry-over evidence — 1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0 CFP-786/801/792/795/810; 6 units / 7 retro file + ADR-070 §D5 declaration-only retain precedent)"`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (boilerplate 영역 축소) 에만 발효 → 본 Amendment 는 면제

**A4. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

ADR-064 결정 원칙 4 어휘 anchor (best-effort / broad coverage / full-scope / active amendment) 중 **active amendment** + **full-scope** 정합:

- Amendment 발의 시점 = 6-Story carry-over sentinel reach 후 즉시 (1 baseline cluster + 5 consecutive fp-0 = 6 units / 7 retro file, active amendment ratchet 강화 방향)
- 적용 영역 = 6 touchpoint 모두 (full-scope, 단일 touchpoint 한정 아님)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A5. doc-only fast-path 영역 정합 (ADR-054 §결정 1)**

본 Amendment 6 자체 = ADR-052 본문 patch (sub-section append) — doc-only fast-path 적격. 단 carrier Story (CFP-819) 는 신규 ADR-081 동반 = ADR-054 §결정 1 거부 조건 (신규 ADR 도입 Story = full-lane 강제) 영역 정합 → 전체 full-lane 진행.

### 결과 (Amendment 6)

- boilerplate composition SSOT (3 mandatory section + verify-before-trust scope 5 sub-scope + 3-lane partition) 영역의 normative anchor 신규 ADR-081 로 분리 — A1 SSOT
- D1/D2/D3/D4 + Amendment 1-5 본문 의미 변경 0건 (sub-section append 패턴) — A2 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A — permanent strengthening) — A3 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A4 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 6 자체) — carrier Story (CFP-819) 전체는 신규 ADR-081 동반 full-lane 진행 — A5 SSOT

### 거절된 대안 (Amendment 6)

- (Amendment-U) **ADR-052 본문 안 boilerplate composition section 직접 inline append** (별도 ADR 신설 회피) — Amendment scope 가 크다 (cross-document 4-region 통합 영역). ADR-070 자매 패턴 (separate ADR + cross-ref) 정합성 부재. 영역 type 분리 (boilerplate composition ≠ touchpoint behavior) 차단 → 신규 ADR-081 채택 (ADR-070 자매 패턴 정합).
- (Amendment-V) **3-lane partition 표를 ADR-068 (boundary completeness invariants) 안에 inline append** — 영역 type mismatch (factual citation ≠ boundary completeness self-check). Codex output 영역 (외부 worker) vs DesignReview lane invariants (내부 lane behavior) 분리 차단 → ADR-081 안 partition 표 박제 + ADR-068 cross-ref 만 채택.
- (Amendment-W) **verify scope marker 어휘 신설 (`[verified-file]` / `[verified-dir]` / `[verified-cross-repo]`)** — CFP-810 retro §6 후보 5 정합, **별 carrier** 분리. 본 Amendment scope = verify scope 분리 의무 본문 명시만 — marker 어휘 변경 없음 → 별 carrier 영역.
- (Amendment-X) **mechanical lint 도입** (Codex spawn prompt 안 3 mandatory section 존재 검출 static regex 또는 Codex output 안 5 sub-scope marker 발화 검출) — ADR-070 §결정 D5 (declaration-only retain) 정합. ADR-081 §D5 본문 표 (a)/(b)/(c)/(d) 4 후보 모두 robustness risk 보유. evidence-checks-registry entry append 면제.

---

## Amendment 7 (2026-05-17 KST, CFP-844)

### Context (Amendment 7)

ADR-081 (Codex worker prompt boilerplate composition SSOT) 가 Amendment 1 (CFP-844) 로 신규 §결정 D6 (Codex worker severity calibration rubric) 를 도입했다. CFP-825 retro §6 후보 2 (PMOAgent `cross_story_pattern_adr_trigger`, `escalation_action: adr_draft_emitted`) carrier.

ADR-081 D2 (verify-before-trust 5 sub-scope) 는 Codex finding 의 **factual citation 정확성** (file:line / verbatim / grep count / ADR §결정 번호) 을 다룬다 — finding 사실 근거 검증 layer. 그러나 finding 의 **severity 경중 calibration** (Codex 가 발화한 P0/P1/P2 가 review lane ground truth severity 와 정합하는가) 은 ADR-081 D6 (Amendment 1) 로 신설된 신규 영역. 본 Amendment 7 = 해당 ADR-081 §결정 D6 신규 영역의 cross-ref sub-section append (ADR-081 Amendment 1 ↔ ADR-052 Amendment 6 ↔ ADR-070 Amendment 1 sibling 패턴 정합).

### 결정 (Amendment 7)

Touchpoint #2 (ArchitectAgent §3 완료 직후, mandatory — Amendment 4) + Touchpoint #3 (CodeReviewPL standalone, fallback) Codex proactive check dispatch 결과의 finding severity 처리 시, **Codex finding severity ↔ PL synthesis severity bidirectional calibration** 의무는 ADR-081 §결정 D6 SSOT 를 따른다:

- **D6.a bidirectional**: over-rate 금지 (Codex severity > PL synthesis severity, factual citation scope) + security-relevant under-rate 금지 (Codex severity < 실제 보안 경중)
- **D6.b ground truth**: DesignReviewPL final verdict severity (primary, touchpoint #2 path) / CodeReviewPL standalone (fallback, touchpoint #3 단독 dispatch) / 양쪽 dispatch 시 higher severity PL 기준
- **D6.c boundary-completeness exception**: Codex P0 boundary-completeness × DesignReview P1 = over-rate 아님 (+1 tier 허용)
- **D6.d disjoint axis**: `codex_severity_inflation` (calibration) ≠ `codex_false_positive_tally` (accuracy, ADR-052 Amendment 6 / ADR-081 6-Story sentinel) — fp 0 chain 무영향
- **D6.e tracking**: 기존 Story §9 verdict prose 또는 §10 FIX Ledger 비고 marker (`[codex-severity-inflation: Codex:P0 vs PL:P1 <scope>]`) — review-verdict-v4 신규 contract field 신설 0 (ADR-081 §D5 declaration-only retain precedent verbatim 정합, contract bump 회피)

본 Amendment 7 = sub-section append 패턴 (Amendment 1-6 패턴 정합). D1/D2/D3/D4 결정 본문 + Amendment 1-6 본문 의미 변경 없음. Codex worker dispatch 자체 흐름 invariant 정합 (severity calibration = dispatch 후 결과 처리 단계 추가만 — dispatch 발동 자체 D2 invariant 무변경).

### 결과 (Amendment 7)

- ADR-081 §결정 D6 (Codex worker severity calibration rubric) cross-ref sub-section append — ADR-081 Amendment 1 SSOT 본문 (의미 변경 0)
- Touchpoint #2/#3 Codex finding severity 처리 = ADR-081 §결정 D6 SSOT 위임 명시 (ADR-052 본문 patch — D1-D4 + Amendment 1-6 의미 변경 0)
- `codex_severity_inflation` (calibration) ≠ `codex_false_positive_tally` (accuracy, Amendment 6 sentinel) disjoint axis 명시 — Amendment 6 sentinel invariant 보존
- CLAUDE.md L170 blockquote severity calibration cross-ref 1 줄 추가 (line-cap 320 invariant 정합)
- doc-only fast-path 영역 정합 (본 Amendment 7 자체) — carrier Story (CFP-844) 는 ADR-081 Amendment 1 동반 = 신규 ADR 도입 아님 (기존 ADR Amendment + src/tests 무변경) → ADR-054 §결정 1 doc-only fast-path 단일 PR 적격 — A6 SSOT

### 거절된 대안 (Amendment 7)

- (Amendment-Y) **ADR-052 본문 안 severity calibration rubric 직접 inline append** (ADR-081 D6 cross-ref 회피) — 영역 type mismatch (touchpoint behavior ≠ Codex worker severity calibration). ADR-081 자매 패턴 (boilerplate composition SSOT 분리 — Amendment 6 정합) 정합성 부재 → ADR-081 D6 안 rubric SSOT + ADR-052 cross-ref 만 채택.
- (Amendment-Z) **severity calibration 을 새 touchpoint (#7) 로 도입** — touchpoint = dispatch 발동 지점 정의. severity calibration 은 기존 #2/#3 dispatch 후 결과 처리 단계 — 새 dispatch 지점 아님. D2 6-touchpoint invariant 보존 (touchpoint count 무변경) → 기존 #2/#3 결과 처리 단계 추가만 채택.
- (Amendment-AA) **review-verdict-v4 신규 `codex_severity_inflation` contract field 신설** — contract MINOR bump + sibling sync (ADR-008/010) + Phase 2 PR = doc-only fast-path 이탈. ADR-081 §D5 declaration-only retain precedent 위배 → 기존 Story §9/§10 prose marker 채택 (ADR-081 §결정 D6.e SSOT 정합).

---

## Amendment 8 (2026-05-18 KST, CFP-946-A)

### Context (Amendment 8)

Codex worker (codex:codex-rescue subagent) 의 sandbox-level file system access 실패가 누적 9 회 occurrence (CFP-506 / CFP-520 / CFP-530 / CFP-578 carrier 3 회 + CFP-756 Epic B 4 Story CFP-919/920/921/923 4 회 + Sentinel #4 strike #8 carrier CFP-946 Epic close retro 1 회 + 본 Story-A Phase 1 PR DesignReview lane reentrant 9th = 9 occurrence 누적, parent_epic CFP-946 P1 escalate_user). 본 Amendment 8 carrier Story (CFP-946-A) 가 Codex worker substitution path 3-enum 의 normative anchor codification.

기존 ADR-070 §결정 D1 default substitution = "Orchestrator inline verify-before-trust" (file Read / Glob / Grep direct verify) — 운영적으로 단일 substitution behavior 만 codify. 실제 운영에서 3 가지 substitution path 가 활용되어 왔으나 (sandbox 영역 외 file 의 sentinel sample 8 retro 분석 결과) normative SSOT 부재 — Codex worker spawn 결정 시점 의 substitution scope declare gap.

본 Amendment 8 = ADR-070 §결정 1 expansion (substitution scope 3-path enum codify, ADR-070 Amendment 3 동반 carrier) 의 ADR-052 본문 cross-ref. 6 touchpoint 각각의 dispatch prompt template 안 substitution path enum 명시 의무 = D2 6-touchpoint 자동 활성 invariant 의 확장 영역 (dispatch 발동 시점에 substitution scope explicit declare).

### 결정 (Amendment 8)

**A1. 6 touchpoint × substitution path 3-enum cross-matrix**

| Touchpoint | Default substitution path | manual_substitution_declare 채택 trigger | fallback_skip_with_marker 채택 trigger |
|---|---|---|---|
| #1 Pre-question Review | `inline_orchestrator_verify` | 질문 초안 인용 source 가 cross-repo / sibling plugin file (sandbox 영역 외) 인 경우 | Codex CLI 미가용 / sandbox network-block 확정 (Orchestrator 가 단독 발화) |
| #2 Design Synthesis Check (**mandatory**) | `inline_orchestrator_verify` | Change Plan 또는 ADR 본문 cross-repo state 인용 시 (예: marketplace.json mirrored field) | EC-1 recursive substitution cascade (본 Story-A 자체 Phase 1 PR DesignReview lane 의 reentrant) |
| #3 Development Rescue | `inline_orchestrator_verify` | 구현 블로커 evidence 가 worktree 외 영역 (sibling plugin 코드 / cross-repo CI log) | 일반적으로 발생 0 — DeveloperPLAgent 가 own worktree scope 안 |
| #4 Requirements Output Review (multi-round debate, Amendment 1) | `inline_orchestrator_verify` | Codex finding 의 fact-check sub-criterion (cross-repo state verification) 인 경우 | 일반적으로 발생 0 — Story §1-§6 = internal-docs path 가 sandbox 영역 외 → debate-protocol-v1 Round 0 input verbatim 첨부 의무 (Amendment 5 SSOT) |
| #5 FIX Root Cause 2nd Opinion | `inline_orchestrator_verify` | review findings evidence pack 안 cross-repo file path 인 경우 | Codex CLI 미가용 / D4 사용자 escalation 직접 진입 |
| #6 ADR Draft Review | `inline_orchestrator_verify` | ADR cross-ref ADR 본문 (sibling plugin docs/adr/ path) 인 경우 | EC-1 recursive substitution cascade (본 ADR-052 Amendment 8 자체 작성 시점 — manual_substitution_declare 사전 declare 의무) |

본 표 = ADR-070 §결정 1 expansion 본문 3-enum SSOT 의 ADR-052 본문 cross-ref. 결정 본문 SSOT = ADR-070 §결정 1 expansion (substitution path 3-enum semantics + Story §10 marker 의무 + 적용 trigger).

**A2. ProactiveCheckPacket schema 변경 없음 (Amendment 5/6/7 패턴 정합)**

기존 D3 ProactiveCheckPacket v1 schema 유지. substitution path enum 명시는 Codex worker spawn prompt 본문 안 (`task` field 본문 또는 별도 sub-field `substitution_scope`) — schema MINOR bump 불필요. ADR-070 §결정 1 expansion 의 결정 본문 SSOT 가 normative anchor — playbook §3.10 dispatch prompt template 안 본문 명시 patch.

**A3. Story §10 marker 의무 (substitution path enum 2/3 한정)**

| Enum value | Story §10 marker (FIX Ledger row) | grep 대상 |
|---|---|---|
| `inline_orchestrator_verify` (default) | (면제 — marker 부재 = 암묵 default) | N/A |
| `manual_substitution_declare` | `[codex-substitution-scope-declared: <scope-enum>]` (1 회/spawn) | sandbox 영역 외 file 인용 evidence + Orchestrator override rationale |
| `fallback_skip_with_marker` | `[codex-sandbox-fallback: <fail-mode>]` (1 회/spawn) | fail-mode enum (9-set, SSOT = ADR-070 §결정 D1) = `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` / `subagent_recursion_blocked` (ADR-070 Amendment 6 / ADR-052 Amendment 10) / `dispatch_stall_or_stream_timeout` (ADR-070 Amendment 7 / ADR-052 Amendment 12) / `codex_truncated_no_verdict` (ADR-070 Amendment 8 / ADR-052 Amendment 13) |

본 표 = ADR-070 §결정 1 expansion 의 Story §10 marker SSOT 의 cross-ref. KPI 영역 (`substitution_count` + `verify_failure_rate` 정량 측정 threshold=5 / 15%) 는 post-merge follow-up CFP carrier 영역 — 본 Amendment 8 의무 = prose tally only (Story §10 marker grep count, lint 없음).

**A4. ADR-070 §결정 1 expansion SSOT 위임 (cross-ref-only Amendment 패턴)**

본 Amendment 8 = sub-section append 패턴 (Amendment 1-7 패턴 정합). D1/D2/D3/D4 결정 본문 + Amendment 1-7 본문 의미 변경 없음. Codex worker dispatch 자체 흐름 invariant 정합 (substitution path enum 명시 = dispatch 발동 시점 substitution scope declare 단계 추가만 — dispatch 발동 자체 D2 invariant 무변경).

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향 (ratchet 강화):

- `is_transitional: false` 본 ADR 유지 (permanent governance, substitution path 3-enum codification = permanent strengthening — Codex worker sandbox 영역 변경 없으면 permanent retain)
- `sunset_justification: "N/A — permanent strengthening (substitution path 3-enum codification = ADR-070 §결정 1 expansion SSOT 의 ADR-052 본문 cross-ref. ADR-070 §D5 declaration-only retain precedent + ADR-082 §결정 6 + ADR-081 §D5/§D6.e + ADR-076 §결정 6 fail-closed clause precedent chain 5번째 link)"`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (substitution path 3-enum 축소 또는 declare 의무 약화) 에만 발효 → 본 Amendment 는 면제

**A6. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

ADR-064 결정 원칙 4 어휘 anchor (best-effort / broad coverage / full-scope / active amendment) 중 **active amendment** + **full-scope** 정합:

- Amendment 발의 시점 = 9 occurrence 누적 sentinel reach 후 즉시 (Sentinel #4 strike #8 carrier CFP-756 Epic close retro + parent_epic CFP-946 P1 escalate_user, active amendment ratchet 강화 방향)
- 적용 영역 = 6 touchpoint 모두 (full-scope, 단일 touchpoint 한정 아님)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A7. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 8 자체 = ADR-052 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. 단 carrier Story (CFP-946-A) 는 ADR-070 §결정 1 expansion + 신규 domain-knowledge 페이지 동반 = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + 신규 domain-knowledge + src/tests 무변경) doc-only fast-path 단일 PR 적격.

**A8. D1/D2/D3/D4 결정 본문 + Amendment 1-7 본문 의미 변경 없음**

기존 D1 (codex:codex-rescue dispatch 채널) / D2 (6 touchpoint 자동 활성) / D3 (ProactiveCheckPacket v1) / D4 (#5 판정 불일치 = 사용자 escalation) + Amendment 1-7 본문 의미 변경 없음. 본 Amendment 8 = 6 touchpoint × substitution path 3-enum cross-matrix 명시만 — sub-section append 패턴 (Amendment 1-7 패턴 정합).

### 결과 (Amendment 8)

- 6 touchpoint × substitution path 3-enum cross-matrix 본문 명시 — A1 SSOT
- Story §10 marker 의무 (`[codex-substitution-scope-declared]` / `[codex-sandbox-fallback]`) — A3 SSOT
- ADR-070 §결정 1 expansion SSOT 위임 (cross-ref-only Amendment 패턴) — A4 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A — permanent strengthening) — A5 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A6 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 8 자체) — A7 SSOT
- D1/D2/D3/D4 + Amendment 1-7 본문 의미 변경 0건 (sub-section append 패턴) — A8 SSOT

### 거절된 대안 (Amendment 8)

- (Amendment-AB) **substitution path 3-enum 의 normative anchor SSOT 를 ADR-052 본문에 inline 작성** (ADR-070 §결정 1 expansion 회피) — 영역 type mismatch (touchpoint behavior ↔ verify-before-trust pattern substitution scope). ADR-070 = verify-before-trust pattern 의 normative anchor SSOT (sandbox access invariant) — substitution path = verify pattern 의 sub-scope. ADR-081 자매 패턴 (boilerplate composition SSOT 분리 — Amendment 6) 정합성 부재 → ADR-070 §결정 1 expansion 안 3-enum SSOT + ADR-052 cross-ref 만 채택.
- (Amendment-AC) **substitution path 4번째 enum value 추가** (auto-retry / multi-source consensus / 외부 verify proxy 등) — 본 Story-A scope 외 (Story §5.3 verbatim "Out-of-Scope" 영역). 별도 follow-up CFP carrier 분리. 본 Amendment 8 = 3-enum exhaustive retain.
- (Amendment-AD) **review-verdict-v4 신규 `codex_substitution_path` contract field 신설** — contract MINOR bump + sibling sync (ADR-008/010) + Phase 2 PR = doc-only fast-path 이탈. ADR-070 §D5 + ADR-081 §D5 + Amendment 7 (AA) declaration-only retain precedent 위배 → Story §10 prose marker 채택 (ADR-070 §결정 1 expansion §A3 SSOT 정합).
- (Amendment-AE) **mechanical lint 도입** (Codex spawn prompt 안 substitution path enum value 명시 검출 static regex) — ADR-070 §결정 D5 (declaration-only retain) 정합. (a)/(b)/(c)/(d) 4 후보 모두 robustness risk 보유. evidence-checks-registry entry append 면제 — `mechanical_enforcement_actions: []` retain.

---

## Amendment 9 (2026-05-19 KST, CFP-1003)

### Context (Amendment 9)

본 ADR-052 의 D1 본문은 두 채널 분리를 codify 한다:

- L84 `기존 codex:rescue는 사후 대응(reactive) 채널 — stuck 상황에서만 호출. 이 ADR은 사전 예방(proactive) 채널을 별도로 정의한다.`
- L90 D1 본문 `Orchestrator가 6개 touchpoint에서 Agent(subagent_type="codex:codex-rescue") 를 proactive check 용도로 자동 dispatch. 기존 codex:rescue(reactive) 와 채널 분리.`

즉 본 ADR-052 의 결정 본문 + Amendment 1-8 전부 = **proactive 6 touchpoint scope 한정** (D1 / D2 자동 활성 / D3 ProactiveCheckPacket / D4 #5 사용자 escalation + Amendment 1 #4 multi-round debate + Amendment 2 #1 iterative reformulation + Amendment 3 #4 fact-check / Amendment 4 #2 mandatory / Amendment 5 verbatim 첨부 / Amendment 6 boilerplate cross-ref / Amendment 7 severity calibration cross-ref / Amendment 8 6 touchpoint × substitution path 3-enum cross-matrix).

CFP-963 Codex TP#4 가 reactive codex:rescue 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역, ADR-070 D1 L110 `사용자 책임 영역 (적용 외)`) 의 network_scope declare / verify-before-trust / boilerplate composition 영역 deferred 결정 (CFP-963 Story §6.3 OOS row L374 verbatim `Codex CLI reactive channel (codex:rescue) network_scope lint = OUT (derived default) proactive 6 touchpoint spawn 한정 (ADR-052 proactive/reactive 분리) — reactive 확장 = 별 CFP` + §3 EC-2 L328 동형). 본 deferred scope = CFP-1003 carrier closure.

본 Amendment 9 = **proactive/reactive disjoint scope explicit codify** + reactive 영역 SSOT 위임 cross-ref. ADR-052 본문 정책 SSOT (proactive 채널 SSOT) 보존 invariant 정합 — reactive 영역 normative anchor = ADR-070 Amendment 5 (substitution scope + sandbox boundary) + ADR-081 Amendment 5 (spawn prompt boilerplate 4 mandatory field reactive 영역 확장) 본문 SSOT 위임.

### 결정 (Amendment 9)

**A1. proactive/reactive 채널 disjoint scope explicit codify (D1 L84/L90 boundary 강화)**

기존 D1 본문 의미 변경 0건. 본 Amendment 9 = D1 L84/L90 의 proactive/reactive disjoint anchor 를 explicit Amendment level 에서 cross-ref 강화. proactive 채널 SSOT (본 ADR-052) ↔ reactive 채널 SSOT (ADR-022 Deprecated + 사용자 ad-hoc invocation + ADR-070 D1 L110 적용 외 영역) disjoint scope 표:

| 영역 | proactive 채널 | reactive 채널 |
|---|---|---|
| **dispatch trigger** | 6 touchpoint 자동 (D2 invariant) | 사용자 ad-hoc invocation (ADR-022 Deprecated default + user explicit request) |
| **normative anchor SSOT** | 본 ADR-052 D1-D4 + Amendment 1-9 | ADR-070 Amendment 5 (substitution + sandbox) + ADR-081 Amendment 5 (boilerplate) |
| **boilerplate composition (3+1 field)** | ADR-081 §결정 D1.A-D (4 mandatory field) | ADR-081 Amendment 5 본문 SSOT (reactive 영역 4 field 확장 적용) |
| **verify-before-trust** | ADR-070 §결정 D1 본문 + Amendment 3 (substitution 3-enum) | ADR-070 Amendment 5 본문 SSOT (reactive 영역 substitution scope codify) |
| **network_scope declare 의무** | ADR-081 §결정 D1.D (4-tier enum 의무) | ADR-081 Amendment 5 본문 SSOT (reactive 영역 4-tier enum 확장 적용) |
| **codex-network-scope-presence lint scope** | proactive 6 touchpoint spawn prompt 한정 (현재 scope, evidence-checks-registry entry 본문 SSOT) | scope 외 (Wave 2 mechanical lint 확장 별도 CFP carrier, ADR-064 §결정 1 unitary) |

**A2. reactive 영역 normative anchor SSOT 위임 (cross-ref-only Amendment 패턴)**

본 ADR-052 본문은 proactive 채널 SSOT (D1 분리 invariant 정합). reactive 영역 normative anchor = ADR-070 Amendment 5 + ADR-081 Amendment 5 본문 SSOT 위임. cross-ref-only pattern (Amendment 6/7/8 패턴 정합 — Amendment 6 = ADR-081 boilerplate SSOT 위임, Amendment 7 = ADR-081 §결정 D6 severity calibration cross-ref, Amendment 8 = ADR-070 §결정 1 expansion substitution 3-enum SSOT 위임).

**A3. proactive/reactive boundary preservation 적용 영역 (Wave 1 declarative-only)**

본 Amendment 9 Wave 1 적용 영역:

- 본 ADR-052 본문 Amendment 9 row + sub-section append (proactive 채널 SSOT 보존 cross-ref)
- ADR-070 Amendment 5 본문 (reactive substitution scope + sandbox boundary codify, declaration-only retain)
- ADR-081 Amendment 5 본문 (reactive spawn prompt boilerplate 4 mandatory field 확장 적용, declaration-only retain)
- `docs/evidence-checks-registry.yaml` `codex-network-scope-presence` entry description 본문 (proactive 6 touchpoint scope explicit 명시 + reactive 영역 OUT explicit codify, registry entry text 본문 patch — current_tier / detect_command / workflow 변경 없음, scope clarification only)
- `docs/orchestrator-playbook.md` §3.10 graceful degradation step pair reactive variant (declarative-only, Wave 1 mechanical lint 부재)

Wave 2 (별도 CFP carrier 분리, ADR-064 §결정 1 unitary):

- `scripts/lib/check_codex_network_scope.py` reactive spawn prompt detection logic 확장 (mechanical lint scope expansion)
- evidence-checks-registry entry description scope 확장 (proactive + reactive 양면)
- bats test fixture pair (reactive spawn prompt with/without network_scope)
- §10 Story marker 신규 enum value 또는 disjoint marker (`[codex-rescue-fallback: <fail-mode>]` reactive variant)

**A4. ADR-070 + ADR-081 본문 SSOT 위임 cross-ref binding**

본 ADR-052 ↔ ADR-070 Amendment 5 + ADR-081 Amendment 5 = **cross-ref binding** (Amendment 6/7/8 패턴 정합):

- **ADR-052 Amendment 9** = proactive 채널 SSOT 본문 보존 (D1 L84/L90 disjoint anchor 강화)
- **ADR-070 Amendment 5** = reactive 영역 substitution scope + sandbox boundary normative anchor (verify-before-trust pattern reactive 확장)
- **ADR-081 Amendment 5** = reactive 영역 spawn prompt boilerplate 4 mandatory field 확장 적용 (D1.A-D codify reactive 변형)

3 ADR 의 normative anchor 분리 — ADR-052 = touchpoint behavior SSOT (proactive 채널 한정), ADR-070 = verify-before-trust pattern SSOT (reactive 영역 substitution + sandbox), ADR-081 = boilerplate composition SSOT (reactive 영역 field 적용). scope 침범 0건.

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향:

- `is_transitional: false` 본 ADR 유지 (permanent governance, proactive/reactive disjoint boundary explicit codify = permanent strengthening)
- `sunset_justification: "N/A — permanent strengthening (proactive/reactive disjoint scope explicit codify + reactive 영역 SSOT 위임 cross-ref. ADR-052 본문 정책 SSOT (proactive 6 touchpoint scope 한정) 보존 invariant 정합, scope 축소 0 + Amendment 1-8 본문 의미 변경 0. ADR-070 §D5 + ADR-081 §D5 declaration-only retain precedent chain 연속)"`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향에만 발효 → 본 Amendment 는 면제

**A6. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-963 Codex TP#4 deferred scope closure (Codex TP#4 CX-963 deferred scope 의 별도 CFP carrier closure 책무, active amendment ratchet 강화 방향)
- 적용 영역 = proactive 6 touchpoint + reactive 채널 모두 (full-scope, 단일 채널 한정 아님 — 단 reactive 영역 SSOT 본문 위임 cross-ref pattern)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A7. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 9 자체 = ADR-052 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1003) = ADR-052 Amendment 9 + ADR-070 Amendment 5 + ADR-081 Amendment 5 + registry entry description patch + playbook §3.10 reactive variant codify = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests 무변경) doc-only fast-path 단일 PR 적격.

**A8. D1/D2/D3/D4 결정 본문 + Amendment 1-8 본문 의미 변경 없음**

기존 D1 (codex:codex-rescue dispatch 채널) / D2 (6 touchpoint 자동 활성) / D3 (ProactiveCheckPacket v1) / D4 (#5 판정 불일치 = 사용자 escalation) + Amendment 1-8 본문 의미 변경 없음. 본 Amendment 9 = proactive/reactive disjoint scope explicit codify + reactive 영역 SSOT 위임 cross-ref only — sub-section append 패턴 (Amendment 1-8 패턴 정합).

### 결과 (Amendment 9)

- proactive/reactive 채널 disjoint scope explicit codify (A1 SSOT 표) — D1 L84/L90 boundary 강화
- reactive 영역 normative anchor SSOT 위임 (ADR-070 Amendment 5 + ADR-081 Amendment 5 본문 SSOT) — A2 cross-ref-only Amendment 패턴 (Amendment 6/7/8 정합)
- proactive/reactive boundary preservation 적용 영역 Wave 1 declarative-only 명시 (A3) — Wave 2 mechanical lint scope 확장 = 별도 CFP carrier 분리 (ADR-064 §결정 1 unitary)
- ADR-052 ↔ ADR-070 Amd 5 ↔ ADR-081 Amd 5 cross-ref binding (A4 SSOT) — 3 ADR normative anchor 분리, scope 침범 0건
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A — permanent strengthening) — A5 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A6 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 9 자체) — A7 SSOT
- D1/D2/D3/D4 + Amendment 1-8 본문 의미 변경 0건 (sub-section append 패턴) — A8 SSOT

### 거절된 대안 (Amendment 9)

- (Amendment-AF) **reactive 영역 normative anchor SSOT 를 ADR-052 본문 inline** (ADR-070 Amendment 5 + ADR-081 Amendment 5 회피) — 영역 type mismatch. ADR-052 = touchpoint behavior SSOT (dispatch prompt template), reactive 영역 substitution scope + boilerplate composition = ADR-070 + ADR-081 pattern SSOT 영역. Amendment 6/7/8 cross-ref-only 패턴 (verify-before-trust pattern / boilerplate composition / substitution 3-enum SSOT 모두 본문 외 ADR 위임) 정합 → reactive 영역 SSOT 본문 위임 채택.
- (Amendment-AG) **proactive 채널 SSOT 본문 자체에 reactive 영역 SSOT inline append** (ADR-052 본문 scope 확장) — ADR-052 본문 정책 SSOT (proactive 채널 한정) 보존 invariant 위배. Amendment 1-8 정합 = proactive 채널 영역만 강화 (substitution / verbatim 첨부 / boilerplate cross-ref / severity calibration cross-ref / fact-check / mandatory 전환 / multi-round debate / iterative reformulation). reactive 영역 = ADR-022 Deprecated + ADR-070 D1 L110 적용 외 = 본 ADR 외 영역 → 별도 ADR (ADR-070/ADR-081) 본문 SSOT 위임 채택.
- (Amendment-AH) **Wave 1 + Wave 2 단일 CFP 통합** (mechanical lint 동시 도입) — ADR-064 §결정 1 (CFP scope unitary, "경량 → full" 단계 채택 금지) 위배. Wave 1 declarative + Wave 2 mechanical 별도 CFP 분리 = ADR-064 §결정 1 정합 + CFP-963 Phase 2 mechanical lint 패턴 답습 (CFP-963 = Phase 1 declare + Phase 2 mechanical).
- (Amendment-AI) **reactive 채널 deprecate** (codex:rescue 자체 폐기 + proactive 채널 단독 SSOT) — ADR-022 Deprecated 와 별개 (codex:rescue subagent 자체 존재 = codex@openai-codex plugin runtime 영역, codeforge 측 deprecate 권한 외). ADR-070 D1 L110 `사용자 책임 영역 (적용 외)` 정합 retain — reactive 영역 normative anchor 강화 (Wave 1 + Wave 2 ratchet) + 사용자 책임 영역 invariant 보존 채택.
- (Amendment-AJ) **codex-network-scope-presence lint scope 확장 (proactive + reactive 양면) inline 본 Amendment 9** — Wave 2 mechanical 영역, ADR-064 §결정 1 (CFP scope unitary) 정합 별도 CFP carrier 분리. 본 Amendment 9 Wave 1 declarative-only 영역 = registry entry description text 본문 patch (scope clarification only, detect_command / workflow / current_tier 변경 0건).

---

## Amendment 11 (2026-05-21 KST, CFP-1131)

**Codex touchpoint wrapper-self trim — touchpoint 2 + 5 conditional skip (Amendment 4 partial rollback in wrapper-self scope, ratchet 축소 2번째 carrier).**

### 컨텍스트

CFP-1110 paired Amendment (ADR-082 Amendment 5 + ADR-071 Amendment 6) merge + CFP-1126 ADR-042 Amendment 10 (AggregateArch + ModuleArch 통합, ADR-058 §결정 5 first applied carrier) merge 후 본 Amendment 11 carrier = **사용자 직권 minimal path 3번째 application** + **ratchet 축소 2번째 carrier**. Researcher (general-purpose) + Codex (codex:rescue, GPT-5) 병렬 critical evaluation 수렴 결과 direct follow-through (Researcher net 35% 정당화 + Codex ROI indeterminate-부정쪽 confidence medium).

### 결정 (Amendment 11)

#### A11-1 — wrapper-self 정식 process Story 영역 touchpoint 2 + 5 conditional skip

| Touchpoint | wrapper-self 정식 process Story 영역 | consumer Story 영역 | minimal path Story |
|---|---|---|---|
| **#1 AskUserQuestion 직전** | retain (Amendment 2 iterative reformulation max 3 rounds) | retain | retain (inline whitelist 1번 entry) |
| **#2 ArchitectAgent §3 직후 mandatory (Amendment 4)** | **conditional skip** — ADR-082 §결정 2 scope (a-d) write-time verify (CFP-841 Amendment 1) + §결정 1 sub-scope (1-C) USER-UTTERANCE-VERBATIM block (CFP-1110 Amendment 5) + ADR-071 Amendment 6 §결정 17 back-translation gate (CFP-1110) cover | retain mandatory (Amendment 4 본문) | N/A (lane spawn 0) |
| **#3 DeveloperPLAgent FIX 2+ 감지 시** | retain (FIX root cause critical) | retain | N/A (lane spawn 0) |
| **#4 RequirementsPLAgent §1-§6 완료 직후 (multi-round debate, Amendment 1)** | retain (multi-round adversarial debate 영역) | retain | N/A (lane spawn 0) |
| **#5 ArchitectPLAgent root cause 판정 직후** | **conditional skip** — touchpoint 3 의 follow-on 중복, ArchitectPL verdict packet 자체 fact-check marker 4종 + verify-before-trust scope 5 sub-scope (ADR-070) cover | retain | N/A (lane spawn 0) |
| **#6 ArchitectAgent ADR 초안 완료 직후** | retain (ADR audit critical, Amendment 5 verify-before-trust source) | retain | N/A (Opus inline 작성, lane PL spawn 0) |

**Effective**: wrapper-self 정식 process Story 영역 = 6 → 4 touchpoint (33% reduction). consumer 영역 + minimal path 영역 무변경.

#### A11-2 — evidence-grounded justification 3 axis

**(a) empirical evidence** — wrapper-self Codex FP 0 streak 11+ Story sentinel:

CFP-770 / CFP-771 / CFP-776 / CFP-786 / CFP-795 / CFP-801 / CFP-810 / CFP-819 / CFP-825 / CFP-844 / CFP-851 + 이후 (CFP-906/932/954/991/1014/1041/1086/etc.) — Codex calibration 정확 evidence. Amendment 7 (codex_severity_inflation calibration) + Amendment 8 (substitution scope 3-path enum) 가 calibration 영역 reinforce 후 FP 0 streak 유지.

**(b) duplication axis** — touchpoint 2 / 5 의 verify coverage 중복:

- touchpoint 2 (ArchitectAgent §3 mandatory) verify scope = corpus enumeration / ADR frontmatter value / cross-plugin ownership / §9 evidence 영역 → ADR-082 §결정 2 scope (a-d) write-time verify mandate (CFP-841 Amendment 1 deferred-followup → CFP-1110 Amendment 5 sub-scope (1-C) verbatim anchor) 이미 internal lane agent self-write 영역 cover. ADR-071 Amendment 6 §결정 17 back-translation gate 도 lane return divergence detection 영역 추가 cover.
- touchpoint 5 (ArchitectPLAgent root cause 판정 직후) verify scope = DeveloperPL 1차 진단 + ArchitectPL final 판정 cross-validate → touchpoint 3 (DeveloperPLAgent FIX 2+) 가 1차 verify, ArchitectPL verdict packet 자체 fact-check marker 4종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]`) + verify-before-trust scope 5 sub-scope (ADR-070 Amendment 3) cover. touchpoint 5 추가 verify = 중복.

**(c) ratchet 축소 paradigm 연장** — CFP-1126 ADR-042 Amendment 10 first applied 의 2번째 application:

CFP-1126 = ADR-058 §결정 5 sunset_justification first applied carrier (boundary axis 영역 ratchet 축소). 본 Amendment 11 = 2번째 application — Codex spawn count axis 의 ratchet 축소. paradigm 정합:
- Amendment N (확대) — Amendment 4 (CFP-532) touchpoint 2 mandatory 전환
- 평가 evidence 누적 — Researcher net 35% / Codex ROI indeterminate / wrapper-self FP 0 streak 11+
- Amendment N+M (부분 rollback) — 본 Amendment 11 = wrapper-self 영역 partial rollback (consumer 영역 invariant carrier 보존)

#### A11-3 — ADR-064 §self-application top-down ratchet evidence-gated exception 2번째 carrier

CFP-1126 Amendment 10 = 약화 방향 evidence-gated exception 첫 carrier. 본 Amendment 11 = 2번째 carrier. mechanism = forbid-scope 축소 아닌 scope conditional split (wrapper-self / consumer / minimal path 3 영역 분리, consumer 영역 invariant carrier mandatory 보존). ADR-064 §self-application 의 약화 방향 mechanical 차단 logic 통과 — 약화 영역 = wrapper-self only, consumer scope 보존 (Codex FP 0 streak evidence wrapper-self 한정).

#### A11-4 — scope_boundary (wrapper-self only)

**포함**:
- wrapper-self 정식 process Story (codeforge plugin family 자체 변경 dogfood) — touchpoint 2 + 5 conditional skip 적용
- ADR-052 본문 + CLAUDE.md cross-ref (declarative anchor)

**out-of-scope** (별 carrier 또는 reject):
- **consumer Story** (mctrader 등 외부 product) — Codex FP 0 streak evidence wrapper-self 한정, consumer 영역 별 carrier (evidence base 부재). 본 Amendment 11 의 wrapper-self trim 적용 시점 후 consumer 영역 동등 evidence 누적 가능 (Wave 3 별도 CFP carrier).
- **minimal path Story** (CFP-1110 / CFP-1126 / 본 CFP-1131) — lane spawn 0 이미 touchpoint 발생 0, 본 trim 영역 외.
- **Wave 2 mechanical lint** (`scripts/check-codex-touchpoint-wrapper-self-skip.sh`) = 별도 CFP carrier (deferred-followup, brainstorm 단계 결정). lint scope = wrapper-self Story 안 touchpoint 2 / 5 spawn 발화 발견 시 warning advisory.
- **touchpoint 1 / 3 / 4 / 6 영역 변경** = 별 carrier (본 Amendment 11 scope 외, retain 영역).

### Compatibility

- D1/D2/D3/D4 + Amendment 1-10 본문 의미 변경 0건 — sub-section append 패턴 (Amendment 1-10 정합).
- Amendment 4 (touchpoint 2 mandatory) 본문 = consumer 영역 retain (Amendment 11 wrapper-self only scope split). consumer 영역 mandatory invariant 보존.
- ADR-082 §결정 2 + §결정 1 sub-scope (1-C) cover (CFP-841 + CFP-1110) — touchpoint 2 의 verify coverage 영역 disjoint complement.
- ADR-070 Amendment 3 verify-before-trust scope 5 sub-scope — touchpoint 5 의 verify coverage 영역 disjoint complement.
- ADR-071 Amendment 6 §결정 17 (CFP-1110) — touchpoint 2 의 lane return divergence detection 영역 disjoint complement.
- ADR-064 §self-application top-down ratchet — evidence-gated exception 2번째 carrier (Amendment 10 CFP-1126 first applied 정합).
- ADR-058 §결정 5 약화 방향 sunset_justification — 본 Amendment 11 만족 (3 axis evidence-grounded justification).
- `is_transitional: false` 유지 (영구 정책, scope conditional split codify).

### Related (Amendment 11 동반)

- ADR-082 §결정 2 + §결정 1 sub-scope (1-C) (CFP-841 + CFP-1110) — touchpoint 2 verify coverage disjoint complement source
- ADR-070 Amendment 3 (verify-before-trust scope 5 sub-scope) — touchpoint 5 verify coverage disjoint complement source
- ADR-071 Amendment 6 §결정 17 (CFP-1110) — touchpoint 2 lane return divergence detection disjoint complement source
- ADR-042 Amendment 10 (CFP-1126) — ratchet 축소 first applied paradigm 정합 source
- ADR-058 §결정 5 — 약화 방향 sunset_justification 의무 mandate (second applied carrier)
- ADR-064 §self-application top-down ratchet — evidence-gated exception 2번째 carrier
- CFP-1110 — paired Amendment paradox-break first application (lineage source)
- CFP-1126 — ratchet 축소 first applied carrier (paradigm source)
- CLAUDE.md — Codex Proactive Check 단락 6 → 4 wrapper-self trim cross-ref 1줄 추가

### 결과 (Amendment 11)

- Codex touchpoint wrapper-self trim codify (6 → 4 conditional skip, touchpoint 2 + 5 wrapper-self 영역 conditional skip)
- ADR-058 §결정 5 second applied carrier (약화 방향 evidence-grounded justification 3 axis)
- ADR-064 §self-application top-down ratchet evidence-gated exception 2번째 carrier
- scope conditional split (wrapper-self / consumer / minimal path 3 영역 disjoint codify)
- consumer scope invariant 보존 (Codex FP 0 streak evidence wrapper-self 한정)
- D1/D2/D3/D4 + Amendment 1-10 본문 의미 변경 0건 (sub-section append 패턴)
- 사용자 직권 minimal path 3번째 application (Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 사용자 승인)

### 거절된 대안 (Amendment 11)

- (Amendment-AK) **6 touchpoint 전체 wrapper-self conditional skip** — over-aggressive. touchpoint 1 / 3 / 4 / 6 verify coverage 중복 axis 부재 (touchpoint 1 = 사용자 dialog quality 독립 / touchpoint 3 = FIX root cause critical / touchpoint 4 = multi-round adversarial debate (Amendment 1) / touchpoint 6 = ADR audit critical). 4 retain + 2 drop 채택.
- (Amendment-AL) **touchpoint 2 / 5 wrapper-self + consumer 양면 conditional skip** — consumer 영역 evidence base 부재 (Codex FP 0 streak wrapper-self 한정). consumer 영역 invariant carrier (touchpoint 2 mandatory) 보존 + Wave 3 별 carrier (consumer evidence 누적 후) 채택.
- (Amendment-AM) **Amendment 4 (touchpoint 2 mandatory) 전체 rollback** — Amendment 4 6 sample success rate 100% sentinel (CFP-426/427/428/429 + 2 carry-over) evidence wrapper-self / consumer 양면 적용. consumer 영역 evidence 보존 = Amendment 4 본문 retain + wrapper-self 영역 scope split 만 채택. partial rollback (wrapper-self only) 적용.
- (Amendment-AN) **Wave 1 + Wave 2 mechanical lint 단일 carrier 통합** — ADR-064 §결정 1 (CFP scope unitary) 위배. Wave 1 declarative + Wave 2 mechanical 별도 CFP 분리 채택 (CFP-963 / CFP-1126 패턴 정합).

---

## Amendment 12 (2026-05-22 KST, CFP-1244)

**ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref + `[codex-sandbox-fallback: <fail-mode>]` fail-mode enum 7 → 8 확장 (ADR-070 Amendment 7 SSOT cross-ref).**

### Context (Amendment 12)

[verified] CFP-1187 운영 phase Epic single autonomous session evidence — Codex CLI v0.125.0 가 `codex exec` 로 invoke 될 때 prompt 를 stdin 으로 직접 pipe 하면 sandbox 안 TTY 부재 → 0-byte stall (>5min). file-redirect invocation `codex exec --sandbox read-only < <promptfile>` 가 stall 을 회피 (S5/S6/S7 file-redirect 성공, S4/S5 early stall → substitution). 추가로 long synchronous Codex wait 가 Orchestrator/agent stream idle-timeout risk 보유 — S7 ArchitectPL stream timeout after 40 tool_uses → redo.

본 ADR-052 = Codex proactive check touchpoint behavior SSOT — substitution scope (Amendment 8) 의 substitution path 3-enum cross-ref. `[codex-sandbox-fallback: <fail-mode>]` Story §10 marker fail-mode enum 의 SSOT = [ADR-070 §결정 D1](ADR-070-codex-verify-before-trust.md) (본 ADR §A3 표 가 명시 — "ADR-070 §결정 1 expansion 의 cross-ref"); 본 ADR-052 §A3 표 = cross-ref mirror. 본 Amendment 12 = (a) ADR-081 Amendment 6 dispatch file-redirect mandate cross-ref + (b) ADR-070 Amendment 7 fail-mode enum 7 → 8 확장 (dispatch-stall / stream-idle-timeout fail-mode 신설) cross-ref + §A3 mirror 표 동기 정정 (Amendment 10 이 `subagent_recursion_blocked` 추가 시 §A3 표 갱신 누락 → 6-stale 로 남긴 mechanical self-check escape 를 full 8-enum 으로 정정 — ADR-065 Amendment 4 / CFP-1242 와 동일 class).

### 결정 (Amendment 12)

**A1. ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref (본문 SSOT 위임)**

codeforge Orchestrator/lane 이 Codex CLI worker check 를 invoke 할 때 file-redirect 형식 `codex exec --sandbox read-only < <promptfile>` 의무 (composed worker prompt 를 file 로 write 후 stdin redirect) + 결과 = output file 경유 수신 + Orchestrator 는 bounded window 초과 synchronous block-wait 금지 — 이 dispatch invocation mandate 의 normative anchor SSOT = [ADR-081 §결정 D8](ADR-081-codex-worker-prompt-boilerplate.md) (Amendment 6). 본 ADR-052 = cross-ref-only — dispatch invocation mandate 본문 중복 codify 0 (Amendment 6/7/8/9 cross-ref-only 패턴 정합 — Amendment 6 = ADR-081 boilerplate SSOT 위임, Amendment 8 = ADR-070 §결정 1 expansion substitution 3-enum SSOT 위임).

dispatch invocation 형식 (ADR-081 §결정 D8) ↔ substitution path 3-enum (본 ADR-052 Amendment 8) 정합: file-redirect invocation 후에도 stall / stream idle-timeout 발생 시 substitution path `fallback_skip_with_marker` 진입 (A2 fail-mode enum 8번째 value carrier).

**A2. `[codex-sandbox-fallback: <fail-mode>]` fail-mode enum 7 → 8 확장 (ADR-070 Amendment 7 SSOT)**

ADR-070 §결정 D1 fail-mode enum SSOT 는 현재 7-set (Amendment 10 / ADR-070 Amendment 6 가 `subagent_recursion_blocked` 7번째 value 추가) — 단 본 ADR-052 §A3 cross-ref 표 는 그 시점 갱신 누락으로 6-stale 상태였다. 본 Amendment 12 = ADR-070 Amendment 7 로 SSOT 를 7 → 8 확장 + §A3 mirror 표 를 full 8-enum 으로 동기 정정:

| # | fail-mode value | 영역 |
|---|---|---|
| 1 | `api_missing` | Codex CLI 미설치 / PATH 부재 (기존) |
| 2 | `version_skew` | Codex CLI 버전 비호환 (기존) |
| 3 | `enterprise_blocked` | enterprise 환경 정책 차단 (기존) |
| 4 | `gh_api_network_blocked` | sandbox network-block 으로 gh api / cross-repo fetch 불가 (기존) |
| 5 | `manual_substitution_declared` | Orchestrator manual substitution 사전 declare (기존) |
| 6 | `inline_orchestrator_verify_only` | Orchestrator inline verify 단독 수행 (기존) |
| 7 | `subagent_recursion_blocked` | subagent context 안 Codex worker subagent spawn 시 ADR-039 platform-inherent recursion guard 차단 (ADR-070 Amendment 6 / ADR-052 Amendment 10 / CFP-1056 — §A3 cross-ref 표 누락분 본 Amendment 12 에서 반영) |
| 8 | **`dispatch_stall_or_stream_timeout`** (**ADR-070 Amendment 7 / ADR-052 Amendment 12 신설**) | Codex `codex exec` invocation stall (TTY 부재 0-byte stall >5min) OR Orchestrator stream idle-timeout during long Codex wait → `fallback_skip_with_marker` path |

신규 8번째 value `dispatch_stall_or_stream_timeout` = 기존 7 value 의 naming convention 정합 (모두 snake_case noun phrase — `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` / `subagent_recursion_blocked`). 본 fail-mode 적용 영역 = (i) Codex `codex exec` invocation stall (file-redirect 적용 후에도 발생 가능 — ADR-081 §결정 D8 evidence: S4/S5 early stall) OR (ii) Orchestrator stream idle-timeout during long Codex wait (CFP-1187 S7 ArchitectPL stream timeout after 40 tool_uses → redo evidence). 양 case 공통 후속 동작 = `fallback_skip_with_marker` path (Amendment 8 §A1/§A3 SSOT — Codex worker spawn 자체 skip + Orchestrator substitution 후속 동작 단독 수행 + verify-before-trust 5 sub-scope 全 적용).

**A3. closed-enum 7 → 8 확장 = ratchet 강화 (additive) + §A3 stale 표 정정**

본 fail-mode enum 확장 = closed-enum expansion (7 → 8, 정보 손실 0, 기존 7 value 의미 변경 0). ADR-058 §결정 5 + ADR-064 §self-application top-down ratchet — closed-enum expansion = strengthening (약화 방향 = enum 축소, 본 Amendment 는 additive 확장 → 강화 방향). 동시에 Amendment 8 §A3 cross-ref 표 가 Amendment 10 (`subagent_recursion_blocked` 추가) 시점에 갱신 누락되어 6-stale 로 남은 상태를 full 8-enum 으로 정정 (mechanical self-check escape — ADR-065 Amendment 4 / CFP-1242 와 동일 class: cross-ref 표 ↔ SSOT 동기 의무).

**A4. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

- `is_transitional: false` 본 ADR 유지 (permanent governance — fail-mode enum + dispatch invocation mandate cross-ref = Codex worker dispatch 영역 영구 invariant)
- `sunset_justification: "ratchet 강화 방향 (closed-enum expansion 7 → 8 — fail-mode enum 8번째 value dispatch_stall_or_stream_timeout 신설, additive, 정보 손실 0, 기존 7 value 의미 변경 0 + ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref + §A3 cross-ref 표 6-stale → 8 정정). 약화 영역 0건 (D1/D2/D3/D4 + Amendment 1-11 본문 의미 변경 0, scope 축소 0, enum 축소 0). ADR-058 §결정 5 + ADR-064 §self-application ratchet 정합 (강화 방향만 amendment)."`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (fail-mode enum 축소 또는 dispatch mandate 약화) 에만 발효 → 본 Amendment 는 면제

**A5. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-1187 운영 phase Epic S4/S5/S6/S7 dispatch stall + stream timeout evidence 누적 후 즉시 (active amendment ratchet 강화 방향)
- 적용 영역 = 6 touchpoint × `fallback_skip_with_marker` substitution path 모두 (full-scope — fail-mode enum 은 모든 touchpoint dispatch 공통)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A6. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 12 자체 = ADR-052 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1244) = ADR-052 Amendment 12 + ADR-081 Amendment 6 + playbook §3.10 patch + CLAUDE.md cross-ref = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests/workflow 무변경) doc-only fast-path 단일 PR 적격.

**A7. D1/D2/D3/D4 결정 본문 + Amendment 1-11 본문 의미 변경 없음**

기존 D1 (codex:codex-rescue dispatch 채널) / D2 (6 touchpoint 자동 활성) / D3 (ProactiveCheckPacket v1) / D4 (#5 판정 불일치 = 사용자 escalation) + Amendment 1-11 본문 의미 변경 없음. 본 Amendment 12 = ADR-081 Amendment 6 cross-ref + ADR-070 Amendment 7 fail-mode enum 7 → 8 확장 cross-ref + §A3 cross-ref 표 6-stale → 8 정정 — sub-section append 패턴 (Amendment 1-11 패턴 정합).

### 결과 (Amendment 12)

- ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref (dispatch invocation mandate 본문 SSOT = ADR-081 §결정 D8, 본 ADR-052 cross-ref-only) — A1 SSOT
- `[codex-sandbox-fallback: <fail-mode>]` fail-mode enum 7 → 8 확장 (ADR-070 Amendment 7 SSOT, 8번째 value `dispatch_stall_or_stream_timeout` 신설) + §A3 cross-ref 표 6-stale → 8 정정 — A2 SSOT
- closed-enum 7 → 8 확장 = ratchet 강화 (additive, 정보 손실 0, 기존 7 value 의미 변경 0) — A3 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification ratchet 강화 — closed-enum expansion) — A4 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A5 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 12 자체) — A6 SSOT
- D1/D2/D3/D4 + Amendment 1-11 본문 의미 변경 0건 (sub-section append 패턴) — A7 SSOT

### 거절된 대안 (Amendment 12)

- (Amendment-AO) **dispatch file-redirect mandate 본문을 ADR-052 본문 inline codify** (ADR-081 §결정 D8 회피) — 영역 type mismatch. ADR-052 = touchpoint behavior SSOT (dispatch 발동 시점 / 결과 처리 / substitution path), ADR-081 = Codex worker prompt boilerplate + invocation SSOT. dispatch invocation 형식 = prompt composition 영역 자매. Amendment 6/7/8/9 cross-ref-only 패턴 정합 — ADR-081 §결정 D8 본문 SSOT + ADR-052 cross-ref-only 채택.
- (Amendment-AP) **fail-mode enum 에 2개 value 분리 신설** (`dispatch_stall` + `stream_idle_timeout` 별개 value) — 두 fail-mode 의 후속 동작 동일 (`fallback_skip_with_marker` path) + 운영적 구분 실익 부재 (양쪽 모두 Codex worker output 미수신). 단일 value `dispatch_stall_or_stream_timeout` 으로 통합 채택 — §A3 표 enum 최소 확장 (7 → 8) 정합.
- (Amendment-AQ) **fail-mode enum 확장 없이 기존 `gh_api_network_blocked` 또는 `api_missing` 에 흡수** — 의미 mismatch. `gh_api_network_blocked` = network-block 영역 (Codex 정상 invoke 후 cross-repo fetch 차단), `api_missing` = Codex CLI 미설치 영역. dispatch stall / stream idle-timeout = Codex CLI 설치 + network 정상이나 invocation 형식 (stdin-pipe) 또는 long wait 으로 인한 stall — disjoint 영역. 신규 8번째 value 채택.
- (Amendment-AR) **fail-mode enum 확장 + mechanical lint 동시 도입** (dispatch 발화 안 file-redirect 형식 presence-grep) — ADR-064 §결정 1 (CFP scope unitary) 위배. Wave 1 declarative (본 Amendment 12 fail-mode enum 확장 + ADR-081 §결정 D8 cross-ref) + Wave 2 mechanical (dispatch invocation presence-grep lint) 별도 CFP 분리 채택 — ADR-052 `mechanical_enforcement_actions: []` declaration-only retain precedent 정합.

## Amendment 13 (2026-05-23 KST, CFP-1286)

**ADR-070 Amendment 8 (§결정 D1 expansion fail-mode enum 8 → 9 확장, 9번째 value `codex_truncated_no_verdict`) cross-ref + §A3 cross-ref 표 8 → 9 enum 동기 정정.**

### Context (Amendment 13)

CFP-604 Phase 2 CodeReview Iter 1 evidence — Codex worker file-redirect dispatch (ADR-081 Amendment 6 §결정 D8 정합) 정상 invocation 후에도 sandbox + Windows PowerShell `[Console]::OutputEncoding` policy reject + 대용량 artifact (~46KB) processing 누적 → reasoning budget 소진 → output 안 verdict analysis 부재 (file content dump + git diff help dump 만 남음). `network_scope_actual: offline` (file-redirect 정상). 기존 8 fail-mode value 어디에도 mapping 불가 — post-invocation reasoning-exhausted path 의 disjoint sub-domain. CFP-604 retro F2 follow-up = single sample escalate_user → 사용자 직접 채택 → CFP-1286 carrier 발의 → 본 Amendment 13 realized.

### 결정 (Amendment 13)

**B1. ADR-070 Amendment 8 cross-ref** — fail-mode 본문 SSOT = ADR-070 §결정 D1 expansion (Amendment 8, 9번째 value `codex_truncated_no_verdict` 신설). 본 ADR-052 = cross-ref-only (Amendment 10/12/13 cross-ref-only 패턴 정합).

**B2. §A3 cross-ref 표 9-enum 동기 정정** — line 807 `fallback_skip_with_marker` row 의 fail-mode enum list 8 → 9 expansion (`codex_truncated_no_verdict` 9번째 append, ADR-070 Amendment 8 / ADR-052 Amendment 13 cross-ref 표기 정합). naming convention = 기존 8 value (snake_case noun phrase) 정합.

**B3. ratchet 정합** — closed-enum expansion (8 → 9, additive, 정보 손실 0, 기존 8 value 의미 변경 0) = strengthening (ADR-058 §결정 5 + ADR-064 §self-application top-down ratchet). D1/D2/D3/D4 + Amendment 1-12 본문 의미 변경 0건. `mechanical_enforcement_actions: []` declaration-only retain (Amendment 1-12 precedent).

**B4. mechanical detection deferred-followup** — Wave 1 declarative (본 Amendment 13 enum 확장 + cross-ref), Wave 2 mechanical detection lint (Codex output verdict-block presence grep + sandbox artifact size threshold heuristic) = pattern_count 2 reach 시 별도 CFP carrier (ADR-076/082/086 precedent). 현 pattern_count = 1 (CFP-604 single sample).

**B5. doc-only fast-path 적용 (ADR-054 §결정 1)** — 본 Amendment 13 = ADR-052 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1286) = ADR-052 Amendment 13 + ADR-070 Amendment 8 + ADR-081 Amendment 7 = 단일 PR 적격.

---

## Amendment 15 (2026-06-29 KST, CFP-2458)

**touchpoint #7 신설 (merge-time adversarial gate) — ADDITIVE 강화 + ProactiveCheckPacket enum `<1|..|6>` → `<1|..|7>` 확장 + critic = 신호원(hypothesis 지위) reshape.**

### Context (Amendment 15)

기존 6 touchpoint (Amendment 11 wrapper-self 6→4 conditional skip 후 잔존 = #1 AskUserQuestion 직전 / #3 DevPL FIX 2+ / #4 RequirementsPL §1-6 / #6 ArchitectAgent ADR 초안) 는 **모두 lane 작업 *중*** dispatch — 머지 직전(shift-right 최우측, 구현리뷰 PASS + CI gate `gh pr checks --required --watch` PASS 후 "merge gate 진입" ~ merge_transition sentinel polling 직전 ~ `gh pr merge` 직전) 위치가 비어 있다 [verified](archive/adr/ADR-052-codex-proactive-check-touchpoints.md:127-147 touchpoint 표 / docs/orchestrator-playbook.md merge-gate flow §3.10).

**동인 3축** (Story §1 verbatim + §3 + §6):

1. **ADR-119 Amendment 2 §결정 10** — "게이트 verdict('PASS') = internal proxy(loop-lag/CPU) 아닌 outcome ground-truth 로만 단정". 본 touchpoint #7 = 그 정책의 **독립 검증자 충원** mechanism (게이트 PASS 가 self-attest 가 아닌 외부 분포 검증을 거치게).
2. **dual-peer track record** — CFP-2244/2440/2445/2451 등 다수 Story 에서 dual-peer Codex 가 Claude-miss P0/P1 을 firsthand 반복 포착 (MEMORY.md). 본 패턴을 머지 직전 시점으로 확장.
3. **#2322 흡수** — gate 결과 = forgeable label 아닌 lane-produced artifact (SLSA separation-of-duties, implementer ≠ certifier). Orchestrator self-attests gates → preventive 로 격상.

Codex API 한도 증가가 상시화 발동 계기. concept 정립 = [`docs/domain-knowledge/concept/merge-time-adversarial-verification-gate.md`](../../docs/domain-knowledge/concept/merge-time-adversarial-verification-gate.md) (CFP-2458 ResearcherAgent Mandate 1·2 산출물, 학계+산업 cited).

### 결정 (Amendment 15)

**D5. touchpoint #7 — merge-time adversarial gate (신규 §결정)**

기존 D2 (6 touchpoint 자동 활성, opt-in 없음) 의 closed enumeration 에 **7번째 touchpoint** ADDITIVE append. ProactiveCheckPacket v1 schema (D3) 의 `touchpoint: <1|..|6>` enum → `touchpoint: <1|..|7>` 로 확장 (additive, 기존 1-6 의미 무변).

| 항목 | touchpoint #7 명세 |
|---|---|
| **trigger 시점** | 구현리뷰 PASS + CI gate (`gh pr checks --required --watch`) PASS 이후, "merge gate 진입" 직후 / merge_transition sentinel polling + `gh pr merge` 이전 (AC-1/AC-2) |
| **purpose** | merge 직전 1패스 적대적 반증 — diff ↔ Story 의도(요구사항 §1 / 설계의도 §3 / 수용기준 §5) 불일치 능동 탐색 |
| **dispatch 주체** | **Orchestrator top-level inline 전용** (ADR-039 Amendment 6 inline whitelist 6번째 entry — 재귀 가드 회피 critical, sub-agent/PL owner 면 silent fallback skip = 게이트 연극화) |
| **input** | PR diff (git) + Story context cross-repo verbatim 첨부 (ADR-081 D1.A-D 4 mandatory field + D2 verbatim + D8 file-redirect dispatch) |
| **프레이밍** | 일반 리뷰 아닌 적대적 반증 ("이 PR 이 왜 틀렸거나 불완전한지 찾아라") + anti-sycophancy (Story 서사 = "정답" 아닌 "반증 대상") |
| **출력** | ProactiveCheckPacket `{findings: [{severity: P0|P1|P2, description, evidence}], recommendation, rationale}` — **evidence(file:line) 필드 의무 (D5.a)** |
| **결과 처리** | P0/P1 + PL falsify 통과 → 머지 보류 + FIX 루프 회부 / P2 → 기록 후 진행 (ADR-081 Amendment 9 merge-time rubric) |
| **fail-mode** | Codex 미가용/sandbox 실패 = ADR-070 Amendment 9 fail-mode/substitution path (fail-closed 권장 — Story §7) |

**D5.a — critic = 신호원이지 차단 판정자 아님 (핵심 reshape, ADDITIVE invariant)**

touchpoint #7 의 Codex finding 은 **자동 머지 차단 아님**. critic 의 모든 결함 주장 = `[hypothesis]` 지위 default (ADR-052 Amendment 3 A3 marker dictionary 정합). 머지 보류로 승격하려면:

1. finding 에 **falsifiable evidence(file:line) 동반 의무** — evidence 부재 finding = 무효 (자동 폐기, 머지 보류 trigger 아님).
2. **Orchestrator 직접 falsify** (ADR-070 D1 verify-before-trust + Amendment 9 merge-time scope) 통과 시만 `[verified]` 승격 → 머지 보류.
3. mismatch (evidence 가 ground truth 와 불일치) → finding reject + Story §10 false-positive tally + override rationale 4종 (ADR-070 D3).

**근거** (overcorrection bias amplify):

- 적대적/설명요구 프롬프트는 overcorrection(false-rejection) bias 를 증폭 — "Systematic Overcorrection" GPT-4o FNR 26.2%→73.2% (HumanEval), 35.9%→87.9% (MBPP), 거부 사유 48.2% 가 falsifiable evidence 없는 Logic Error 주장 (source: arxiv 2603.00539). 따라서 적대 프롬프트의 진짜 결함 포착력은 살리되, valid 코드의 대거 over-reject 를 verify-before-trust gate 로 차단.
- ADR-077 §결정 7 정보 무결성 invariant ("fact-check marker 무검증 승격 금지") 와 동형 — critic 주장 `[hypothesis]` → PL falsify 후만 `[verified]` 승격 (ADR-077 reuse anchor).
- codeforge dogfood 실측: Codex false-positive 가 반복돼 PL runtime-test/firsthand falsify 가 필수였음 (CFP-2440 Codex 2건 fp / CFP-2449 Codex 2건 fp). critic 은 신호원이지 판정자 아님.

**D5.b — anti-sycophancy + calibration**

- Story 컨텍스트에 동조한 무비판 "looks good" 반환 차단 — 프롬프트가 diff ↔ Story 의도의 *충돌* 을 능동 탐색하도록 구성 (confirmation bias 연구: PR description redaction 이 누락 검출 68.75% 회복, source: arxiv 2603.18740).
- calibration 명시 — "결함 없으면 없다고 보고, 없는 문제 발명 금지" (cry-wolf 폐기 차단, FP 10% 미만 유지가 채택 생존 조건, source: Anthropic Code Review "<1% incorrect" + "verify findings").

**D5.c — #2/#5 복원 아님 (Amendment 11 ratchet 무손상)**

Amendment 11 (CFP-1131) 이 wrapper-self 6→4 로 drop 한 #2 (ArchitectAgent §3 직후) / #5 (ArchitectPL root cause 직후) 는 **lane-time** 영역. touchpoint #7 = **merge-time** 영역 — 시점·대상(PR-unit holistic)·산출물(머지 보류 verdict) 모두 disjoint. #2/#5 복원이 아니라 빈 위치 신설 → Amendment 11 ratchet 축소 무손상 (ADR-058 §결정 5 약화 차단 logic 통과: 본 Amendment = 강화 방향 additive, sunset_justification 면제).

**D5.d — CodexReviewAgent 와 disjoint (channel 분리)**

| 차원 | CodexReviewAgent (구현리뷰 lane) | touchpoint #7 (merge-gate) |
|---|---|---|
| lane | code (review-time) | merge-time (CI PASS 후) |
| unit | per-file src/** | PR-unit holistic |
| context | 코드 품질 (runtime bug / layer / Impl Manifest mapping) | Story-context 전체 (요구사항·설계의도·AC) adversarial |
| dispatch 주체 | CodeReviewPL | Orchestrator top-level inline |

동일 채널 취급 금지 (AC-12/AC-13). 중복 아닌 defense-in-depth (shift-left 우측에 추가).

**D5.e — ADR-022 framing 정합 (충돌 아님)**

ADR-022 (Sonnet-decider Codex review 자동발동 deprecate) scope = 구 Sonnet-decider 5-trigger 한정. 본 touchpoint #7 = proactive-check 계열 (ADR-052 #7) 로 위치 → ADR-001 (CodexReviewAgent 필수워커) + ADR-052 (proactive 자동 dispatch) 가 이미 재정립한 "리뷰/proactive 영역 자동 Codex" 와 정합. override 아님.

**D5.f — Story B 재사용 named pattern**

본 touchpoint #7 의 dispatch contract (ProactiveCheckPacket #7 + verify-before-trust 무조건 적용 + P0/P1/P2 severity → 머지 보류 매핑 + critic=hypothesis reshape) = Epic CFP-2457 Story B (변이 테스트 peer) 가 재사용할 **"merge-time adversarial dispatch pattern"** named pattern. concept 문서가 SSOT.

### cross-ref (Amendment 15)

- **ADR-039 Amendment 6** — inline whitelist 6번째 entry (merge-time Codex dispatch) 신설. 재귀 가드 회피 critical (substitution-side spawn 차단 방지).
- **ADR-070 Amendment 9** — verify-before-trust merge-time scope cross-ref + fail-mode/fail-closed enum. merge-time finding 도 D1/D3 무조건 적용.
- **ADR-081 Amendment 9** — merge-time severity rubric 신설 (D6 review-lane ground truth 머지 직전 닫힘 대응).
- concept SSOT = `docs/domain-knowledge/concept/merge-time-adversarial-verification-gate.md`.

### 결과 (Amendment 15)

- touchpoint #7 (merge-time adversarial gate) 신규 §결정 D5 — 6 touchpoint 자동 활성 영역에 7번째 ADDITIVE append (ProactiveCheckPacket enum 6→7).
- critic = 신호원(hypothesis 지위) reshape — evidence(file:line) 동반 + PL falsify 후 verified 승격 (D5.a, ADR-070/077 reuse).
- anti-sycophancy + calibration (D5.b) / #2·#5 복원 아님 (D5.c) / CodexReviewAgent disjoint (D5.d) / ADR-022 framing 정합 (D5.e) / Story B named pattern (D5.f).
- 3 sibling ADR Amendment (ADR-039 Amd 6 + ADR-070 Amd 9 + ADR-081 Amd 9) cross-ref.
- D1/D2/D3/D4 + Amendment 1-14 본문 의미 변경 0건 — 신규 §결정 D5 + enum 확장 sub-section append only (Amendment 1-14 패턴 정합).
- `mechanical_enforcement_actions` Amendment 14 entry retain (provenance enforcement Phase 2 carrier 분리 — ADR-064 §결정 1 unitary).

### 거절된 대안 (Amendment 15)

- (Amendment-AS) **touchpoint #2/#5 복원으로 머지직전 게이트 대체** — 시점·대상·산출물 disjoint (lane-time ↔ merge-time). 복원 시 Amendment 11 ratchet 축소 약화 (sunset_justification 의무 발생) + merge-time 빈자리 미해소. touchpoint #7 ADDITIVE 신설 채택.
- (Amendment-AT) **CodexReviewAgent 흡수 (merge-time mandate 추가)** — lane mismatch (review-time per-file ↔ merge-time PR-unit holistic). channel-disjoint 식별 의무 (AC-12) 위배. 별도 dispatch contract 채택 (worker agent 형태 = Phase 2 (a)/(b)/(c) 3택 설계 lane 결정).
- (Amendment-AU) **critic finding 자동 머지 차단 (PL falsify 생략)** — overcorrection bias 로 false-block 양산 → cry-wolf 폐기 (D5.a 근거). verify-before-trust 무조건 적용 (critic = 신호원) 채택.
- (Amendment-AV) **required CI check 강제 (phase-gate-mergeable.yml contexts 7-tuple)** — branch protection 6-tuple 변경 = 고비용·비가역, 본 요지 밖. inline 절차 + result-via-file 채택 (Story §4.1).
- (Amendment-AW) **debate-protocol-v1 자동 발동 (Claude↔Codex multi-round)** — 목적 = 독립 검증자 추가이지 토론체계 도입 아님 (Story §5.4 암묵가정). 1패스 single-pass 채택 (debate 기본 미발동, divergence escalate 는 별 carrier).

---

## Amendment 16 (2026-06-29 KST, CFP-2464)

**touchpoint #8 신설 (mutation peer — surviving-mutant hollow-gate 탐지) — ADDITIVE 강화 + ProactiveCheckPacket enum 리터럴 `<1|..|6>`(stale) → `<1|2|3|4|5|6|7|8>` 정정 확장(A #7 누락분 + B #8) + probe-the-detector mechanism reshape.** Epic CFP-2457 Story B.

### Context (Amendment 16)

Amendment 15 가 touchpoint #7 (merge-time adversarial gate) 를 신설하면서 *산출물(PR diff)* 을 독립 분포 critic 이 적대 review 하는 **review-of-output** 패턴을 codify 했고, D5.f 에서 "merge-time adversarial dispatch pattern" 을 **Story B 재사용 named pattern** 으로 명시 reserve 했다 [verified](archive/adr/ADR-052-codex-proactive-check-touchpoints.md Amendment 15 D5.f).

Story B 의 mechanism 은 disjoint — *detector(테스트 스위트)* 자체를 변이(mutant)로 probe 하는 **probe-the-detector**. 코드 커버리지는 "라인 실행 여부" 만 말하고 "동작 검증 여부" 는 말하지 못한다 — 100% 커버 + assertion 부재 = 0 보장. mutation testing 은 통과 코드에 의도적 국소 결함을 주입해 테스트가 PASS→FAIL(RED) 로 뒤집히는지 관찰함으로써 이 갭을 falsify 한다. surviving mutant(주입 후에도 PASS) = hollow-gate(검사연극) 신호.

**동인 3축** (Story §1 verbatim + §2 + §6):

1. **codeforge hollow-gate 만성 결함의 구조적 차단** — dogfood 실측: CFP-2451 `STORY_KEY_PREFIX` 하드코딩 hollow-gate(dual-peer 포착 → mutation-RED 차단), CFP-2426 줄번호 날조(content-anchor grep SSOT 전환) [verified](MEMORY.md). 공통 구조 = "테스트가 통과한다 ≠ 테스트가 실제 결함을 잡는다".
2. **기존 단일 mutant manual subset 의 일반화** — `docs/domain-knowledge/domain/test-discipline/red-green-stash-proof-pattern.md` 가 RED→GREEN stash proof 를 "mutation testing 의 단일 mutant manual subset" 로 framing [verified](red-green-stash-proof-pattern.md:41,53,127). CFP-2464 = QADev self-attest 단일-manual-mutant 을 **Codex 외부 분포 multi-mutant 적대 peer** 로 일반화 (separation of duties 보완).
3. **Codex API 한도 증가** = LLM-as-mutator 상시화 계기. Meta ACH 가 LLM 이 mutation 의 scale 장벽(전수 변이 폭증)을 극복함을 실증 [verified](engineering.fb.com 2025-09-30).

concept 정립 = [`docs/domain-knowledge/concept/mutation-based-hollow-gate-detection.md`](../../docs/domain-knowledge/concept/mutation-based-hollow-gate-detection.md) (CFP-2464 ResearcherAgent Mandate 1·2 산출물, 학계+산업 cited).

### 결정 (Amendment 16)

**D6. touchpoint #8 — mutation peer gate (신규 §결정)**

기존 D2 (touchpoint 자동 활성, opt-in 없음) 의 closed enumeration 에 **8번째 touchpoint** ADDITIVE append. ProactiveCheckPacket v1 schema (D3) 의 `touchpoint` enum → `touchpoint: <1|2|3|4|5|6|7|8>` 로 확장 (additive, 기존 1-7 의미 무변).

> **스키마 리터럴 정정 (본 Amendment 16)**: D3 schema 리터럴(본문 L146 + Amendment 5 verbatim 인용 L610)이 stale `<1|2|3|4|5|6>` 로 남아 있었다 — Amendment 15(Story A)가 touchpoint #7 을 신설하면서 enum 리터럴 갱신을 누락했기 때문. 본 Amendment 16 에서 A 의 #7 누락분 + B 의 #8 을 함께 `<1|2|3|4|5|6|7|8>` 로 정정한다 (additive, ratchet 무손상).

| 항목 | touchpoint #8 명세 |
|---|---|
| **trigger 시점** | 구현리뷰(code-review) lane 진입 — detector(테스트 스위트)가 이미 GREEN(CI gate PASS or 구현 lane 직후 stable green) 인 산출물 한정. detector 없으면 변이를 죽일 대상 부재 → mutation 무의미 (Story §2.4) |
| **purpose** | detector 의 adequacy 적대 falsify — GREEN 코드에 국소 결함(mutant) 주입 → suite 재실행 → surviving 이면 hollow-gate(검사연극) 신호 능동 탐색 |
| **dispatch 주체** | **구현리뷰 lane worker (sub-agent) 가 Bash(`node codex-companion.mjs review`) 로 Codex 호출** — CodexReviewAgent 동형 proven channel (재귀 가드 = subagent→**Agent tool** 호출 한정, Bash 호출은 미발동). **ADR-039 inline whitelist 신규 entry 불요** (entry 6 merge-time 흡수 아님 — D6.e) |
| **Q-A 결정 = 경로 B** | **Codex = mutant 명세(어디에 어떤 국소 결함, baseline·예상 동작차이)만 생성 = 신호원** / lane(QADev/CodeReviewPL) 이 실제 patch 적용 + suite 실행 + 재현 falsify. ADR-081 §결정 D8 `--sandbox read-only` 무손상 + "Codex=신호원" 정합 (D6.a) |
| **input** | mutation 대상 코드 + 해당 테스트 스위트 + baseline GREEN 결과 (ADR-081 D1.A-D 4 mandatory field + D2 verbatim + D8 file-redirect + payload split, Amendment 10) |
| **프레이밍** | 적대적 변이 ("이 테스트가 임의 국소 결함을 잡는가, 못 잡으면 어디서 살아남는가") + anti-sycophancy + calibration ("죽일 수 없는 변이(equivalent)면 그렇게 보고, 없는 검사연극 날조 금지") |
| **출력** | ProactiveCheckPacket `{findings: [{severity: P0|P1|P2, description, evidence: <mutant 위치 + baseline/post-mutation 결과 + 동작차이>}], recommendation, rationale}` — **falsifiable evidence(어떤 입력에서 어떤 동작 차이) 필드 의무 (D6.b)** |
| **결과 처리** | surviving mutant + PL/QADev 재현 falsify + equivalent/flaky 배제 통과 → hollow-gate 결함 승격 → P0/P1 = FIX 회부 / P2 = 기록 후 진행 (ADR-081 Amendment 10 mutation severity rubric) |
| **fail-mode** | Codex 미가용/sandbox 실패 = ADR-070 Amendment 10 fail-mode/disposition (lane-time = `fail_open_then_record_with_marker` 권장 — Story §7, merge-time fail-closed 와 disjoint) |

**D6.a — Q-A 결정: 경로 B (Codex = 신호원 mutant 명세 생성, lane 적용+실행)**

mutation 은 (코드 write + 테스트 러너 실행) 을 요구하나 ADR-081 §결정 D8 = codeforge 전체 Codex dispatch `--sandbox read-only` 의무 [verified](archive/adr/ADR-081-codex-worker-prompt-boilerplate.md:731 D8). 두 경로:

- **경로 A (거절)**: Codex writeable sandbox 모드로 자체 worktree 에서 mutation+test 실행 — D8 read-only ratchet 약화 방향 (sunset_justification 의무 + 거절 위험) + codex CLI writeable 모드 실재 불명확 + "Codex=신호원" 요구사항(§1 재사용 (2)) 위반(Codex 가 판정 실행까지 수행).
- **경로 B (채택)**: Codex 는 **mutant 명세만 생성** (어느 파일·라인에 어떤 국소 변형, baseline 상태, 예상 동작차이) → lane(QADev/CodeReviewPL/Orchestrator) 이 실제 patch 적용 + suite 실행 + 재현. D8 무손상 + Codex=신호원 정합 + separation of duties (주입자 Codex ≠ 인증자 lane).

**D6.b — surviving mutant = 신호원, PL/QADev 재현 falsify 후 승격 (critic = 판정자 아님)**

surviving mutant 주장 = `[hypothesis]` 지위 default (ADR-052 Amendment 3 A3 marker dictionary + Amendment 15 D5.a 정합). hollow-gate 결함 승격 조건:

1. finding 에 **falsifiable evidence 동반 의무** — 어떤 mutant 가 어디서 살아남았는지 + baseline/post-mutation 결과 + **어떤 입력에서 어떤 동작 차이가 관측 가능한가**. evidence 부재 finding = 무효 (자동 폐기). equivalent mutant 는 정의상 동작차이 0 → 이 evidence 의무가 자동 1차 필터.
2. **PL/QADev 직접 재현** (해당 mutant 를 실제 적용 후 suite 가 정말 PASS 재현되는지) 통과 시만 `[verified]` hollow-gate 승격.
3. 재현 실패 / equivalent 의심 / flaky 의심 → 승격 금지 ("불확정" 보류 또는 reject, ADR-070 Amendment 10).

**근거** (ADR-077 §결정 7 무검증 승격 금지 + ADR-119 Amd 2 동형 + Story A C-2/C-4 상속):

- mutation-특유 false-positive 2원천 = (i) **equivalent mutant** (구문 다르나 의미 동일 = 죽일 수 없음, 실세계 4~39% — Madeyski 2013 via arxiv 2408.01760, program equivalence undecidable). "이 테스트를 보강하라" = 충족 불가능한 요구 = cry-wolf 최악성. (ii) **flaky 오염** (미처리 시 mutant-test pair 9% unknown — ShiETAL19 ISSTA 2019). surviving≠hollow 양면 → 재현+전처리 후만 승격.
- codeforge dogfood 실측: Codex false-positive 반복돼 PL runtime-test/firsthand falsify 필수 (CFP-2440 2건 fp / CFP-2449 2건 fp). critic 은 신호원이지 판정자 아님.

**D6.c — anti-sycophancy + calibration (mutation 축)**

- Codex 가 detector 에 동조해 "테스트 충분" 무비판 반환 차단 — 프롬프트가 *국소 결함이 어디서 살아남는지* 능동 탐색하도록 구성.
- calibration 명시 — "죽일 수 없는 변이(equivalent)면 그렇게 보고, 없는 검사연극 날조 금지" (cry-wolf 폐기 차단 — FP 억제 책임이 calibration 표현 아닌 equivalence 식별 + flaky 격리 구조 전처리, concept M-5). P2급 저영향 surviving 자동 차단 금지.

**D6.d — touchpoint #7 흡수 아님 (#7 review-of-output ↔ #8 probe-the-detector disjoint)**

| 차원 | touchpoint #7 (merge-time gate, Amd 15) | touchpoint #8 (mutation peer, 본 Amd 16) |
|---|---|---|
| mechanism | review-of-output (산출물 PR diff 를 critic 이 review) | probe-the-detector (테스트 스위트를 변이로 probe) |
| trigger 시점 | merge-time (CI PASS 후 ~ `gh pr merge` 전) | 구현리뷰 lane-time (detector GREEN 시점) |
| dispatch 주체 | Orchestrator top-level inline (ADR-039 entry 6) | 구현리뷰 lane worker (sub-agent) → Codex via Bash |
| Codex 역할 | diff↔의도 불일치 발화 (read-only) | mutant 명세 생성 (read-only, 경로 B) |
| 결함 단위 | PR-unit holistic finding | surviving mutant 별 |

같은 적대적 검증 family, 다른 mechanism = defense-in-depth (중복 아님, concept boundary 명시). 동일 채널 취급 금지.

**D6.e — ADR-039 Amendment 불요 (lane worker Bash 채널 — inline whitelist 신규 entry 0)**

touchpoint #7 (Amendment 15) 은 **merge-time** 에 lane PL 부재라 Orchestrator top-level inline dispatch 가 필요했고, Codex 를 Agent tool 로 spawn 하면 재귀 가드 silent skip 되므로 ADR-039 Amendment 6 inline whitelist 6번째 entry 가 필요했다. touchpoint #8 은 **구현리뷰 lane-time** — CodeReviewPL 이 active 하고, 기존 CodexReviewAgent 가 이미 lane worker(sub-agent) 로서 **Bash(`node codex-companion.mjs review`)** 로 Codex 를 호출하는 proven channel 을 보유 [verified](plugins/codeforge-review/agents/CodexReviewAgent.md:10 `Bash(node *)` 권한 grant + :84 `node "$CMD" review` 실 invocation). 재귀 가드 = "subagent → **Agent tool** 호출 금지" (L474) 한정이라 Bash 호출 미발동. 따라서 mutation peer dispatch = lane worker spawn → Codex via Bash = ADR-039 §결정 1 binary always-spawn 정합 (수정 작업 = lane worker 가 수행) + inline whitelist 신규 entry 0 (entry 6 merge-time 흡수 아님, entry 7 신설 아님).

**D6.f — CodexReviewAgent 와 disjoint (channel 분리)**

| 차원 | CodexReviewAgent (구현리뷰) | touchpoint #8 (mutation peer) |
|---|---|---|
| 검증 대상 | 코드 산출물 품질 (runtime bug / layer / Impl Manifest mapping) | detector(테스트 스위트) adequacy |
| 방법 | per-file src** review | 변이 주입 후 survival 관찰 |
| 결함 신호 | 코드 결함 finding | surviving mutant = hollow-gate |

동일 lane(구현리뷰) 안 별도 채널 (병렬 가능, 결과 dedup 규칙 = Story §8 AC-12). 중복 아닌 defense-in-depth.

### cross-ref (Amendment 16)

- **ADR-070 Amendment 10** — verify-before-trust mutation scope (surviving mutant evidence ground truth verify) + equivalent/flaky 불확정 disposition + lane-time fail-mode (`fail_open_then_record_with_marker`).
- **ADR-081 Amendment 10** — mutation severity rubric (surviving hollow-gate → P0/P1/P2 merge-block/요구사항 impact) + payload split (대상 코드+테스트+명세 = ADR-070 Amd 8 reasoning budget 소진 회피).
- **ADR-039 (Amendment 불요)** — lane worker Bash 채널 (D6.e). inline whitelist entry 무변경.
- **concept** = `docs/domain-knowledge/concept/mutation-based-hollow-gate-detection.md` (M-1~M-5 SSOT).

### 결과 (Amendment 16)

- touchpoint #8 (mutation peer gate) 신규 §결정 D6 — touchpoint 자동 활성 영역에 8번째 ADDITIVE append (ProactiveCheckPacket enum 7→8).
- Q-A = 경로 B (Codex = mutant 명세 생성 신호원, lane 적용+실행) — D8 read-only 무손상 (D6.a).
- surviving mutant = 신호원(hypothesis) reshape — falsifiable evidence(동작차이) 동반 + PL/QADev 재현 falsify + equivalent/flaky 배제 후 hollow-gate 승격 (D6.b).
- #7 흡수 아님 (review-of-output ↔ probe-the-detector disjoint, D6.d) / ADR-039 Amendment 불요 (lane worker Bash 채널, D6.e) / CodexReviewAgent disjoint (D6.f).
- 2 sibling ADR Amendment (ADR-070 Amd 10 + ADR-081 Amd 10) cross-ref.
- D1/D2/D3/D4 + Amendment 1-15 본문 의미 변경 0건 — 신규 §결정 D6 + enum 확장 sub-section append only (Amendment 1-15 패턴 정합).
- `mechanical_enforcement_actions` Amendment 14 entry retain (mutation mechanical wire = Phase 2 별 carrier — ADR-064 §결정 1 unitary).

### 거절된 대안 (Amendment 16)

- (Amendment-AX) **신규 standalone mutation ADR 신설** — Codex touchpoint SSOT 분산 (ADR-052 가 touchpoint enumeration 단일 SSOT). Amendment 15 D5.f 가 이미 Story B 를 touchpoint 패턴 재사용처로 reserve → 기존 ADR additive amendment 채택 (altitude 정합, ADR-054 §결정 1 doc-only fast-path).
- (Amendment-AY) **경로 A (Codex writeable sandbox mutation 실행)** — D8 read-only ratchet 약화 + writeable 모드 실재 불명확 + Codex=신호원 위반 (D6.a). 경로 B 채택.
- (Amendment-AZ) **touchpoint #7 (merge-time) 흡수** — mechanism·timing disjoint (D6.d). merge-time 은 lane PL 부재 + Path B 의 lane 적용+실행 불가. 구현리뷰 lane-time touchpoint #8 신설 채택.
- (Amendment-BA) **ADR-039 inline whitelist entry 7 신설 (mutation dispatch inline)** — 구현리뷰 lane-time 은 lane worker Bash 채널로 충분 (재귀 가드 미발동, D6.e). inline entry 불요 = ADR-039 §결정 1 정합 (수정 작업 = lane worker 수행). entry 7 신설 거절.
- (Amendment-BB) **surviving mutant 자동 hollow-gate 승격 (재현·equivalent/flaky 전처리 생략)** — equivalent(4~39%, undecidable) + flaky(9% unknown) false-positive 양산 → cry-wolf 폐기 (D6.b). 재현 falsify + 전처리 후 승격 채택.
- (Amendment-BC) **전수 변이** — 변이 1개당 suite 1회 = N배 비용 폭증, 산업 전원 전수 포기 (concept M-4). diff-based + 소수 고가치 LLM-targeted 채택 (Story §7).

