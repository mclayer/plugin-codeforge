---
adr_number: 81
title: Codex worker prompt boilerplate composition SSOT (3 mandatory section + verify-before-trust scope + 3-lane partition)
status: Accepted
category: workflow-policy
date: 2026-05-17
carrier_story: CFP-819
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    cfp: CFP-844
    date: 2026-05-17
    scope: "신규 §결정 D6 (Codex worker severity calibration rubric) append — Codex finding severity ↔ PL synthesis severity bidirectional calibration anchor (over-rate 금지 + security-relevant under-rate 금지). ground truth = DesignReviewPL final verdict severity (primary) / CodeReviewPL standalone fallback / 양쪽 dispatch 시 higher severity 기준. boundary-completeness exception (Codex P0 boundary-completeness × DesignReview P1 = over-rate 아님, +1 tier 허용). codex_severity_inflation (calibration) ≠ codex_false_positive_tally (accuracy) disjoint axis — full fp 0 chain sentinel 무영향. tracking = 기존 Story §9/§10 prose marker (`[codex-severity-inflation: ...]`, review-verdict-v4 contract field 신설 0 — doc-only fast-path 유지, ADR-081 §D5 declaration-only retain precedent verbatim 정합). D1-D5 본문 의미 변경 0건 — §결정 D6 sub-section append only. ADR-052 Amendment 7 + ADR-070 Amendment 2 cross-ref sibling. is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only, §결정 D6.e known-limitation explicit binding — ADR-040 Amendment 3 DesignReview missing flag 회피)."
    status: applied
    ref: "## Amendment 1 / 본문 ### D6 + 거절된 대안 D6"
    sunset_justification: "ratchet 강화 방향 (verify-before-trust scope 에 severity calibration 차원 추가 — over-rate + security-relevant under-rate bidirectional anchor 신설). 약화 영역 0건 (D1-D5 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 3
    cfp: CFP-946
    date: 2026-05-18
    scope: "신규 §결정 D1.D (sandbox_network_required toggle) append — Codex worker spawn prompt 가 sandbox-restricted network operation (gh api / git fetch cross-repo / 외부 HTTP) 필요 여부 declare 의무 codify. CFP-946 option 1 (Codex CLI sandbox 모드 토글 정의 + Orchestrator spawn prompt 의무 field) carrier. true = substitution path activate 영역 (ADR-052 Amendment 8 3-enum cross-matrix 정합), false = sandbox-내부 file scope only verify 완결 영역. D1.A (dogfood-out path) + D1.B (current lane/phase) + D1.C (sandbox_outside_paths) + D1.D (sandbox_network_required) = 4 mandatory boilerplate field. D1.A-C 본문 의미 변경 0건 — D1.D disjoint append only. mechanical injection layer 부재 (declaration-only retain — Amendment 1/2 family pattern 정합). cross-ref ADR-052 Amendment 8 + ADR-070 Amendment 3 (substitution-side mechanism) — 양 면 chain 완결 (option 1 + option 2 + option 3 통합). is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent 정합)."
    status: applied
    ref: "## Amendment 3 / 본문 ### D1.D + cross-ref"
    sunset_justification: "ratchet 강화 방향 (spawn prompt boilerplate 4번째 mandatory field 신설 — sandbox network requirement explicit declaration 의무 codify). 약화 영역 0건 (D1.A-C 본문 의미 변경 0, scope 축소 0, Amendment 1/2 D6/D7 영향 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 2
    cfp: CFP-892
    date: 2026-05-17
    scope: "신규 §결정 D7 (Codex worker digest-parse self-verification + quantitative P0/P1/P2/P3 severity grading rubric + ground-truth divergence escape hatch explicit declaration) append — D6 calibration anchor 의 mechanical pre-screen 보완. (1) D7.a digest-parse self-verification step (yaml/json indentation re-check before issuing severity rating, ANCHOR-2 FP class 차단 — Story-4 CFP-834 digest-indentation 오독 carrier), (2) D7.b quantitative P0/P1/P2/P3 grading rubric (block / blocker / improvement / nit 4-tier explicit criteria, D6.b ground truth severity 의 정량화), (3) D7.c ground-truth divergence escape hatch (Codex P0 + PL divergence 시 ADR-070 strict-verify-gate 자동 trigger — declaration-only, mechanical lint 부재). D1-D6 본문 의미 변경 0건 — §결정 D7 sub-section append only. is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent 정합)."
    status: applied
    ref: "## Amendment 2 / 본문 ### D7 + 거절된 대안 D7"
    sunset_justification: "ratchet 강화 방향 (severity calibration rubric quantification + digest-parse pre-screen + escape hatch declaration). 약화 영역 0건 (D1-D6 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 4
    cfp: CFP-963
    date: 2026-05-19
    scope: "§결정 D1.D body 확장 — `sandbox_network_required: <bool>` boolean toggle → `network_scope: <4-tier enum>` strict ratchet-up codify. 4-tier enum value SSOT: `offline` (file-IO-only sandbox 영역 verify 완결) / `repo-fetch-only` (own-repo file-IO + own-repo git fetch 한정) / `web-fetch` (external HTTP / cross-repo gh api / git fetch cross-repo 허용 — 기존 boolean true 의 broad path) / `offline_substitution_declared` (Codex CLI 미가용 / sandbox network-block 확정 → Orchestrator substitution path activate, boolean equivalent 부재 — strict ratchet-up). Boolean → enum backward-compat mapping (advisory grace): `false ↔ offline` / `true ↔ web-fetch` (default broad path) / `true ↔ repo-fetch-only` (narrower variant explicit declare). Boolean legacy grace window = open-ended until ratchet trigger (declarative-only `ratchet_trigger`: `pr_cumulative_min: 20` enum-only window — ADR-060 §결정 6(b) default precedent-aligned per ADR-068 I-5 dimensional empirical grounding / OR explicit user/PMO escalation — manual proposal on trigger reach, auto-firing 부재). 본 Amendment 4 = enum 도입; boolean 폐기 = 별 follow-up Amendment 5 reservation. unconditional guard placement (ADR-068 I-3): boolean grace = unconditional advisory (lint emits `[legacy-boolean-detected]` comment but exits 0 unconditionally during grace window — no lint flag gating). declaration-only retain invariant **유지** (§D5 precedent — mechanical injection layer 부재). 단 `mechanical_enforcement_actions[]` 신설: `codex-network-scope-presence` warning-tier evidence-checks-registry entry binding (ADR-040 Amendment 3 §결정 7.A 의무 — declaration ≠ presence check 영역 분리, CFP-722 story-section-ownership / CFP-841 corpus-claim-verify precedent 동형). D1.A-C 본문 의미 변경 0건. D6/D7 영역 영향 0. is_transitional false 유지 (permanent governance)."
    status: applied
    ref: "## Amendment 4 / 본문 ### D1.D 확장"
    sunset_justification: "ratchet 강화 방향 (boolean 2-state → 4-state enum, 정보 손실 0, scope 축소 0 + declaration-only retain → +mechanical presence-grep warning lint binding = ADR-040 Amendment 3 §결정 7.A self-application). 약화 영역 0건 (D1.A-C/D6/D7 본문 의미 변경 0, boolean legacy grace 미축소 — open-ended until ratchet trigger). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 5
    cfp: CFP-1003
    date: 2026-05-19
    scope: "§결정 D1.A-D 4 mandatory boilerplate field 의 적용 scope codify — proactive 6 touchpoint scope 한정 (codeforge 강제 invariant) explicit anchor + reactive `codex:rescue` 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역) best-effort 가이드 anchor 확장 적용. 기존 D1.A (dogfood-out Story path) + D1.B (current lane / phase) + D1.C (sandbox_outside_paths) + D1.D (`network_scope: <4-tier enum>`) 4 mandatory field 의미 변경 0건 — proactive 영역 codeforge 강제 invariant 정합 보존. 추가 SSOT: reactive 영역 4 field 채택 = 사용자 자율 선택 (codeforge 강제 0 invariant 보존, ADR-070 D1 L110 `사용자 책임 영역 (적용 외)` 정합). ADR-052 Amendment 9 + ADR-070 Amendment 5 chain — Codex TP#4 CX-963 deferred scope (CFP-963 §6.3 OOS + §3 EC-2) closure. D1.A-D / D2 / D3 / D4 / D5 / D6 / D7 본문 의미 변경 0건 — proactive/reactive scope 적용 영역 표 본문 강화 only (D1 sub-section new row). `mechanical_enforcement_actions[]` 변경 0건 (Amendment 4 의 `codex-network-scope-presence` entry retain, scope expansion = Wave 2 별 CFP carrier 분리 ADR-064 §결정 1 unitary 정합). declaration-only retain invariant 유지 (§D5 precedent — mechanical injection layer 부재 + Wave 2 reactive mechanical lint = 별 CFP carrier). is_transitional false 유지 (permanent governance, ratchet 강화 방향 only — proactive 영역 codeforge 강제 invariant + reactive 영역 사용자 책임 영역 invariant 양립 보존)."
    status: applied
    ref: "## Amendment 5 / 본문 ### D1 적용 scope (proactive/reactive 표)"
    sunset_justification: "ratchet 강화 방향 (D1.A-D 4 mandatory boilerplate field 적용 scope codify — proactive 6 touchpoint scope 한정 explicit anchor + reactive 영역 best-effort 가이드 anchor 확장 적용). 약화 영역 0건 (D1.A-D / D2-D7 본문 의미 변경 0, codeforge 강제 영역 축소 0, mechanical_enforcement_actions[] Amendment 4 entry retain). reactive 영역 codeforge 강제 = 사용자 책임 영역 invariant 위배 → best-effort 가이드 anchor 채택 = ADR-070 D1 L110 정합 + ratchet 강화 양립. ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 6
    cfp: CFP-1244
    date: 2026-05-22
    scope: "신규 §결정 D8 (Codex worker dispatch file-redirect mandate) append — codeforge Orchestrator/lane 이 Codex CLI worker check 호출 시 file-redirect 형식 `codex exec --sandbox read-only < <promptfile>` 의무 codify (composed worker prompt 를 file 로 write 후 stdin redirect). direct stdin-pipe / inline-arg invocation = TTY 부재 시 sandbox 안 0-byte stall (>5min) → 금지. 결과 = output file 경유 수신, Orchestrator 는 bounded window 초과 synchronous block-wait 금지 — 다음 step 진행 후 result file pickup (CFP-1187 S7 ArchitectPL stream idle-timeout after 40 tool_uses → redo evidence). Codex CLI v0.125.0 확인. evidence = Issue #1244 + CFP-1187 운영 phase Epic S4/S5 early stall → substitution / S5/S6/S7 file-redirect 성공 / S7 stream timeout redo. D1.A-D 4 mandatory boilerplate field 무변경 — dispatch invocation 영역이지 prompt field 신설 아님. D1-D7 본문 의미 변경 0건 — §결정 D8 sub-section append only. is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent chain — ADR-070 §D5 + ADR-082 §결정 6 + ADR-081 §D5/§D6.e + ADR-070 Amd 5 + ADR-081 Amd 5 정합)."
    status: applied
    ref: "## Amendment 6 / 본문 ### D8 + 거절된 대안 D8"
    sunset_justification: "ratchet 강화 방향 (Codex worker dispatch reliability hardening — file-redirect invocation 형식 의무 + result-via-file + synchronous block-wait 금지 codify, dispatch invocation 영역 신규 normative anchor). 약화 영역 0건 (D1.A-D 4 mandatory boilerplate field 무변경, D1-D7 본문 의미 변경 0, scope 축소 0, prompt field 신설 0 — dispatch invocation 영역 additive). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 7
    cfp: CFP-1286
    date: 2026-05-23
    scope: "ADR-070 Amendment 8 (§결정 D1 expansion fail-mode enum 8 → 9 확장, 9번째 value `codex_truncated_no_verdict`) cross-ref. fail-mode 영역 = §결정 D8 file-redirect dispatch 정상 invocation 후 sandbox + Windows PowerShell encoding policy reject + 대용량 artifact processing 누적 → reasoning budget 소진 → output 안 verdict analysis 부재. post-invocation reasoning-exhausted path = §D8 file-redirect (stall 1차 회피층) 의 disjoint sub-domain (file-redirect ↔ stream-stall ↔ reasoning-exhausted 3 disjoint failure mode). CFP-604 retro F2 follow-up realized (single sample escalate_user). 본 ADR-081 line 525 (D8 표) + 530 (D7-D8 본문) + 532 (orthogonal 정의) 의 fail-mode 9-enum reference → 9-enum 동기 정정. D1.A-D 4 mandatory boilerplate field 무변경, D1-D8 본문 의미 변경 0건 — fail-mode reference 표기 갱신 only (additive enum expansion 정합). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent chain). is_transitional: false (permanent), sunset_justification N/A (강화 방향, scope 축소 0). ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-1286)."
    status: applied
    ref: "## Amendment 7 / 본문 fail-mode enum 9-enum 동기 정정"
    sunset_justification: "ratchet 강화 방향 (closed-enum expansion 8 → 9, additive, 정보 손실 0, 기존 8 value 의미 변경 0). 약화 영역 0건 (D1.A-D 무변경, D1-D8 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합."
  - amendment_id: 8
    cfp: CFP-1383
    date: 2026-05-24
    scope: "신규 §결정 D9 (Codex worker dispatch prompt body origin/main fetch directive mandate) append — Codex worker spawn prompt body 안 `[ORIGIN-MAIN-DIRECTIVE]` block 의무 codify (ground_truth_source: origin/main / verbatim_command_pattern: git show origin/main:<path> / working_tree_avoidance: true / sandbox_pre_fetch). working tree file path direct reference 금지 — stale local checkout state 회피 normative anchor. CFP-1333 §9.1 DesignReviewPL verdict 의 Codex worker 5/5 FALSE POSITIVE evidence (working tree HEAD bfc4806 5 commits behind state direct Read) + CFP-1384 sibling Story 의 5/5 TRUE POSITIVE empirical validation (prompt body 안 git show origin/main:<path> verbatim file content 첨부) disjoint outcome 결정 factor formalization (closing-the-loop empirical validation). own-repo origin/main fetch directive 한정 — cross-repo state = D1.C sandbox_outside_paths 영역 + D1.D network_scope: web-fetch 영역 분리. D1.A-D 4 mandatory boilerplate field 무변경 (Amendment 6-B 거절 대안 '신규 5번째 mandatory field 추가' 정합 — D9 = sub-section append, mandatory field 추가 0). D8 dispatch invocation 무변경. D1-D8 본문 의미 변경 0건 — §결정 D9 sub-section append only (3-axis disjoint: D1 prompt content / D8 invocation / D9 prompt body directive). is_transitional: false (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent chain 8번째 instance — ADR-070 §D5 → ADR-082 §결정 6 → ADR-081 §D5/§D6.e → ADR-070 Amd 5 → ADR-081 Amd 5 → ADR-081 Amd 6 → ADR-081 Amd 7 → 본 Amd 8). Phase 2 mechanical wire (dispatch prompt body 안 `[ORIGIN-MAIN-DIRECTIVE]` block presence-grep lint + `verbatim_command_pattern` value match + bats fixture + workflow + label entry + evidence-checks-registry entry) = 별 sub-CFP carrier 영역 (ADR-064 §결정 1 CFP scope unitary 정합, CFP-1384 sibling Wave 2 split pattern 답습). ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-1383)."
    status: applied
    ref: "## Amendment 8 / 본문 ### D9 + 거절된 대안 D9"
    sunset_justification: "ratchet 강화 방향 (Codex worker dispatch prompt body origin/main fetch directive normative anchor 신설 — working tree file 우회 + stale local checkout state 회피 invariant codify, prompt body directive 영역 신규 normative anchor §결정 D9). 약화 영역 0건 (D1.A-D 4 mandatory boilerplate field 무변경, D8 dispatch invocation 무변경, D1-D8 본문 의미 변경 0, scope 축소 0, mandatory field 추가 0 — sub-section append additive). CFP-1384 closing-the-loop empirical validation (5/5 TP outcome) evidence 가 ratchet 강화 정당성. ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 9
    cfp: CFP-2458
    date: 2026-06-29
    scope: "신규 §결정 D10 (merge-time severity rubric) append — ADR-052 Amendment 15 touchpoint #7 (merge-time adversarial gate) sibling. §결정 D6 (Codex worker severity calibration rubric) 의 ground truth severity 우선순위 (primary = DesignReviewPL final verdict / fallback = CodeReviewPL standalone / 양쪽 = higher) 가 **merge-time 엔 닫혀 있음** — 머지 직전은 모든 review lane 종료 후라 review-lane verdict 가 ground truth 로 재사용 불가 (review lane = 머지 직전 폐쇄). 본 §결정 D10 = merge-time 전용 P0/P1/P2 severity rubric 신설 — review-lane verdict 대신 **머지 차단 영향 (merge-block impact)** 을 ground truth 축으로 재정의: P0 = 정확성/보안/데이터 무결성 결함 (배포 시 incident, 무조건 머지 보류) / P1 = 요구사항·AC 미충족 또는 설계의도 위반 (머지 보류 — Story §1/§3/§5 대비) / P2 = 스타일·minor·cosmetic·nice-to-have (비차단, 기록 후 진행). critic 의 severity 발화 자체는 `[hypothesis]` — Orchestrator 가 D6 bidirectional calibration (over-rate 금지 + security-relevant under-rate 금지) + verify-before-trust (ADR-070 Amendment 9) 통과 후 merge-time rubric 으로 최종 확정. boundary-completeness exception (D6.c) merge-time 정합 유지. D1-D9 본문 의미 변경 0건 — 신규 §결정 D10 sub-section append only. ADR-052 Amendment 15 + ADR-039 Amendment 6 + ADR-070 Amendment 9 sibling cross-ref. mechanical_enforcement_actions[] 변경 0건 (Amendment 4/8 entry retain, declaration-only retain — §D5 precedent chain 9번째 instance). is_transitional: false, sunset_justification N/A (강화 방향 — merge-time severity ground truth 재정의 신설, D6 review-lane rubric 무손상 보존, scope 축소 0). ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-2458)."
    status: applied
    ref: "## Amendment 9 / 본문 ### D10 + 거절된 대안 D10"
    sunset_justification: "ratchet 강화 방향 (merge-time severity rubric 신설 — review-lane verdict 가 머지 직전 닫힌 영역에 merge-block impact ground truth 축 신설). 약화 영역 0건 (§결정 D6 review-lane severity calibration rubric 무손상, D1-D9 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 10
    cfp: CFP-2464
    date: 2026-06-29
    scope: "신규 §결정 D11 (mutation surviving-mutant severity rubric) + §결정 D12 (mutation prompt payload split) append — ADR-052 Amendment 16 touchpoint #8 (mutation peer) sibling. Epic CFP-2457 Story B. 2축 신설 — (1) §결정 D11 = surviving-mutant 의 P0/P1/P2 severity 를 **hollow-gate 영향 (이 검사연극이 방치되면 어떤 실 결함을 못 잡는가)** ground truth 축으로 재정의: P0 = 정확성/보안/데이터 무결성 검증 갭 (이 게이트가 hollow 라 실 incident-급 결함을 못 잡음) / P1 = 요구사항·AC·설계의도 검증 갭 (Story §1/§3/§5 동작을 검증 못함) / P2 = 스타일·minor·cosmetic 변이 갭 (동작·요구사항 영향 없음 — 비차단, 기록 후 진행). critic severity = `[hypothesis]` → Orchestrator/PL 가 D6 bidirectional calibration + verify-before-trust(ADR-070 Amd 10) + 재현 falsify + equivalent/flaky 배제 통과 후 D11 rubric 최종 확정. **단 P0/P1 승격 = 재현된 hollow-gate(`hollow_gate_verified`) 한정** — `undetermined`(equivalent/flaky 의심)는 severity 미부여(불확정 보류). (2) §결정 D12 = mutation prompt payload split — mutation prompt(대상 코드 + 해당 테스트 스위트 + mutant 명세 + baseline)는 ADR-070 Amd 8 `codex_truncated_no_verdict`(~46KB artifact reasoning budget 소진) 상시 위험 영역이라 **mutant 묶음을 소수 고가치 단위로 분할 dispatch** 의무 (전수 금지 — concept M-4 diff-based + 소수 고가치 LLM-targeted). D8 file-redirect + D1.A-D 4 mandatory field + D2 verbatim 무손상. D1-D10 본문 의미 변경 0건 — 신규 §결정 D11/D12 sub-section append only. ADR-052 Amendment 16 + ADR-070 Amendment 10 sibling cross-ref. mechanical_enforcement_actions[] 변경 0건 (Amendment 4/8 entry retain, declaration-only retain — §D5 precedent chain 10번째 instance). is_transitional: false, sunset_justification N/A (강화 방향 — mutation severity rubric + payload split 신설, D6/D10 무손상, scope 축소 0). ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-2464)."
    status: applied
    ref: "## Amendment 10 / 본문 ### D11 + ### D12 + 거절된 대안"
    sunset_justification: "ratchet 강화 방향 (mutation surviving-mutant severity rubric [hollow-gate 영향 ground truth] + payload split 신설). 약화 영역 0건 (§결정 D6 review-lane / §결정 D10 merge-time rubric 무손상, D1-D10 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 11
    cfp: CFP-2477
    date: 2026-06-30
    scope: "신규 §결정 D13 (Codex worker execution dispatch — 실행형 재리뷰 dispatch 형식 + execution ground-truth axis) append — ADR-070 Amendment 11 (review-lane execution scope + §결정 D9 disposition) sibling. Epic CFP-2476 E1. 2축 신설 — (1) §결정 D13 = execution dispatch 형식: 실행 검증 dispatch = `adversarial-review`(read-only 고정 turn, focus 지원) primary / `task --write`(workspace-write toggle) 예외 — 둘 다 §결정 D8 file-redirect (`codex exec --sandbox ... < <promptfile>`) 형식 정합 (turn 기반 stall 회피층 상속). 현 `review --focus` 는 native reviewer 가 custom focus 거부 (validateNativeReviewRequest throws) = 죽은 경로 → 교체. 실행 주체 = Codex CLI 자체 sandbox (read-only 기본 / network-off / `.git`·`.codex` 보호 / OS 격리) — lane worker own-Bash 직접 실행 아님 (CodexReviewAgent Bash allowlist 미확대, OWASP LLM06 최소권한). (2) §결정 D3 3-lane partition 에 execution ground-truth axis 추가: Codex worker scope = factual citation (file:line + verbatim + grep count + ADR §결정 번호 + cross-repo SHA) **∪ execution ground-truth (실행 exit code + stdout = 재현 가능 객관 사실)** — 양축 모두 verify-before-trust scope (ADR-070 D1/D2/D3 + Amendment 11 §결정 D9). D1.A-D 4 mandatory boilerplate field 무변경 (D8 dispatch invocation 영역 — execution dispatch 가 D8 정합임을 declare, prompt field 신설 0). D1-D12 본문 의미 변경 0건 — 신규 §결정 D13 sub-section append + §결정 D3 axis 추가 only. ADR-070 Amendment 11 + ADR-044 정합 declare (user_request_only = producer 한정, execution-bias 는 worker behavior 지 dispatch 발동 조건 아님) sibling cross-ref. mechanical_enforcement_actions[] 변경 0건 (declaration-only retain — §D5 precedent chain 11번째 instance). is_transitional: false, sunset_justification N/A (강화 방향 — execution dispatch 형식 + execution ground-truth axis 신설, D1-D12 무손상, scope 축소 0). ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-2477)."
    status: applied
    ref: "## Amendment 11 / 본문 ### D13 + §결정 D3 execution axis"
    sunset_justification: "ratchet 강화 방향 (Codex worker execution dispatch 형식 + execution ground-truth axis 신설 — 실행형 재리뷰 dispatch normative anchor §결정 D13 + 3-lane partition factual citation ∪ execution axis 확장). 약화 영역 0건 (D1.A-D 4 mandatory field 무변경, D8 dispatch invocation 무변경, D1-D12 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 12
    cfp: CFP-2545
    date: 2026-07-01
    scope: "신규 §결정 D14 (Codex companion 브로커 경로 wall-clock ceiling mandate) append — §결정 D8 file-redirect (Amendment 6, `codex exec ... < <promptfile>` 0-byte TTY stall 방어층) 이 codeforge-owned companion 브로커 경로 `node codex-companion.mjs adversarial-review --wait` (CodexReviewAgent.md:89, 4 리뷰 lane 공유 워커) 의 wall-clock process-level hang 을 미포함하는 gap 보완. companion request() 는 응답 라인 도착/프로세스 종료로만 resolve (deadline 부재) → 모델·브로커가 final answer 전 stall 시 completion promise 영구 미settle → node·Bash·worker·Orchestrator 순차 무한 대기. 본 §결정 D14 = codeforge 소유 companion 호출부에 wall-clock ceiling `timeout <N> --kill-after=<K>` 배선 의무 + exit 124 → 기존 fail-mode enum #8 `dispatch_stall_or_stream_timeout` 재사용 marker `[codex-sandbox-fallback: dispatch_stall_or_stream_timeout]` + fail-open 금지 (verdict=inconclusive, PASS 자동승격 금지 — ADR-119 §결정10 outcome-honesty 상속) + Orchestrator liveness 게이트 소유 (worker 자가-spawn 금지, ADR-039). fail-mode enum #8 trigger 정의를 'codex exec TTY 0-byte stall' + 'companion adversarial-review --wait wall-clock 초과' 양쪽으로 명시 확장 (신규 enum value 0 — closed-set 크기 무변경, ADR-052/070/081 3 ADR 정정 불요). timeout N < Orchestrator liveness max-wait 순서 정합 의무. D1.A-D 4 mandatory boilerplate field 무변경 (D8 dispatch invocation 영역 — companion 경로 wall-clock 이 D8 axis sub-domain 임을 declare, prompt field 신설 0). D1-D13 본문 의미 변경 0건 — 신규 §결정 D14 sub-section append only (D8 dispatch-reliability axis 의 companion sub-domain 확장). AC-1 mechanical 강제 (dispatch 발화 `timeout <N>` prefix presence-grep lint) = Phase 2 carrier (Wave 1 선언 = 본 §결정 D14 + playbook §3.10 companion sub-paragraph + agent md prefix / Wave 2 mechanical lint script + workflow + bats fixture — ADR-081 Amd6-E 예고 패턴, ADR-064 §결정 1 unitary). ADR-052 Amendment 12 (fail-mode enum #8) + ADR-070 (verify-before-trust substitution) + ADR-039 (liveness 게이트 Orchestrator 소유) + ADR-119 Amendment 2 (fail-open 금지) sibling cross-ref. mechanical_enforcement_actions[] 신설 3번째 entry `codex-companion-timeout-presence` (deferred-followup, Phase 2 wire — ADR-040 Amendment 3 §결정 7.A + Amendment 4/8 precedent verbatim). is_transitional: false, sunset_justification N/A (강화 방향 — companion wall-clock ceiling mandate 신설, D8 file-redirect + D1-D13 무손상, scope 축소 0). ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-2545, dogfood wrapper-self)."
    status: applied
    ref: "## Amendment 12 / 본문 ### D14 + 거절된 대안 D14"
    sunset_justification: "ratchet 강화 방향 (Codex companion 브로커 경로 wall-clock ceiling mandate 신설 — §결정 D8 file-redirect 0-byte stall 방어층이 미포함한 companion process-level wall-clock hang 방어 + fail-open 금지 outcome-honesty + Orchestrator liveness 게이트 소유, dispatch-reliability axis 의 companion sub-domain 확장). 약화 영역 0건 (D1.A-D 4 mandatory boilerplate field 무변경, D8 file-redirect invocation 무변경, fail-mode enum closed-set 크기 무변경 — trigger 정의 의미 확장만, D1-D13 본문 의미 변경 0, scope 축소 0). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
related_stories:
  - CFP-819  # carrier
  - CFP-770  # baseline fp 8
  - CFP-771  # baseline fp 8 (CFP-770 동반)
  - CFP-786  # carry-over fp 0 #1
  - CFP-801  # carry-over fp 0 #2
  - CFP-792  # carry-over fp 0 #3
  - CFP-795  # carry-over fp 0 #4
  - CFP-810  # carry-over fp 0 #5 (sentinel reach)
  - CFP-844  # Amendment 1 — 신규 §결정 D6 severity calibration rubric (CFP-825 retro §6 후보 2)
  - CFP-1003 # Amendment 5 — D1.A-D 4 mandatory field 적용 scope codify (proactive 강제 + reactive best-effort 가이드, ADR-052 Amd 9 + ADR-070 Amd 5 chain — Codex TP#4 CX-963 deferred scope closure)
  - CFP-1244 # Amendment 6 — 신규 §결정 D8 Codex worker dispatch file-redirect mandate (codex exec --sandbox read-only < promptfile + result-via-file + synchronous block-wait 금지, CFP-1187 S4/S5/S6/S7 evidence)
  - CFP-1286 # Amendment 7 — ADR-070 Amendment 8 cross-ref (fail-mode enum 9-set sync, codex_truncated_no_verdict 9번째 value)
  - CFP-1383 # Amendment 8 — 신규 §결정 D9 Codex worker dispatch prompt body origin/main fetch directive mandate (working tree file 우회 + stale local checkout state 회피, CFP-1333 5/5 FP + CFP-1384 5/5 TP closing-the-loop empirical validation)
  - CFP-2458 # Amendment 9 — 신규 §결정 D10 merge-time severity rubric (review-lane verdict 닫힌 영역 merge-block impact ground truth 재정의, ADR-052 touchpoint #7 sibling). Epic CFP-2457 Story A.
  - CFP-2464 # Amendment 10 — 신규 §결정 D11 mutation surviving-mutant severity rubric (hollow-gate 영향 ground truth) + §결정 D12 mutation prompt payload split (codex_truncated 회피, 전수 금지 diff-based). ADR-052 touchpoint #8 sibling. Epic CFP-2457 Story B.
  - CFP-2477 # Amendment 11 — 신규 §결정 D13 Codex worker execution dispatch (adversarial-review/task file-redirect + Codex sandbox 실행) + §결정 D3 3-lane partition execution ground-truth axis 추가. ADR-070 Amendment 11 sibling. Epic CFP-2476 E1.
  - CFP-2545 # Amendment 12 — 신규 §결정 D14 Codex companion 브로커 경로 wall-clock ceiling mandate (adversarial-review --wait 무한 대기 근절 — §D8 file-redirect 0-byte stall 방어층 미포함 companion process wall-clock hang 방어 + fail-open 금지 + Orchestrator liveness 게이트). ADR-052 Amd12 fail-mode #8 재사용 + ADR-039 + ADR-119 Amd2 sibling. dogfood wrapper-self.
related_adrs:
  - ADR-052  # Codex Proactive Check 6 touchpoints (parent — Amendment 6 + Amendment 7 (CFP-844) cross-ref + Amendment 15 (CFP-2458) touchpoint #7 merge-time gate)
  - ADR-077  # Amendment 9 (CFP-2458) — §결정 7 정보 무결성 invariant (fact-check marker 무검증 승격 금지) (critic severity hypothesis→verified 확정 절차 reuse)
  - ADR-070  # verify-before-trust pattern (sibling — D1/D2/D5 cross-ref + Amendment 2 (CFP-844) D6 보완)
  - ADR-082  # write-time self-write verification mandate (D5 declaration-only retain 선례 super-class)
  - ADR-058  # ADR sunset criteria mandate (§결정 1/2/3 정합)
  - ADR-060  # evidence-enforceable promotion framework (declaration-only retain)
  - ADR-064  # decision principle mandate (active amendment + forbid-list)
  - ADR-068  # boundary completeness invariants (3-lane partition cross-ref)
  - ADR-073  # verify-before-assert (Orchestrator self-assertion layer 자매)
  - ADR-045  # PMOAgent cross-story pattern adr trigger (forcing function)
  - ADR-079  # KST timestamp display mandate
  - ADR-039  # default subagent context
  - ADR-054  # doc-only fast-path (§결정 1 신규 ADR full-lane 강제)
related_files:
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/adr/ADR-070-codex-verify-before-trust.md
  - docs/orchestrator-playbook.md
  - CLAUDE.md
is_transitional: false
mechanical_enforcement_actions:
  # Amendment 4 (CFP-963, 2026-05-19) — D1.D `network_scope: <4-tier enum>` 확장 시
  # ADR-040 Amendment 3 §결정 7.A 의무 발효 (D1-D7 본문 의미 변경 0, declaration-only retain
  # 유지하면서 presence-grep mechanical lint layer 추가 = CFP-722 story-section-ownership /
  # CFP-841 corpus-claim-verify 선례 동형). registry yaml row + workflow yml = Phase 2 PR scope.
  - action: codex-network-scope-presence
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint script + workflow wire = Phase 2 PR scope
    target_section: §결정 D1.D    # spawn prompt 안 network_scope field presence-grep heuristic (4-tier enum value OR boolean legacy advisory grace)
  # Amendment 8 (CFP-1383, 2026-05-24) — D9 Codex worker dispatch prompt body
  # origin/main fetch directive 신설 시 ADR-040 Amendment 3 §결정 7.A 의무 발효
  # (D1-D8 본문 의미 변경 0, declaration-only retain 유지하면서 presence-grep
  # mechanical lint layer 추가 = Amendment 4 precedent verbatim 답습).
  # CFP-1412 Phase 2 mechanical wire carrier — lint script (scripts/check-codex-
  # origin-main-directive-presence.sh + scripts/lib/check_codex_origin_main_
  # directive_presence.py Python SSOT) + bats fixture pair (≥6 assertion +
  # RED→GREEN stash proof per CFP-1334 §8.4) + 3 bats fixture text files +
  # workflow byte-identical mirror (templates/ + .github/workflows/ ADR-005) +
  # evidence-checks-registry codex-origin-main-directive-check entry (17 field
  # schema, status: Active, tier: warning) + label-registry-v2 v2.54 → v2.55
  # MINOR + hotfix-bypass:codex-origin-main-directive-check 76번째 family
  # member append (META self-application 3rd applied case, raw active 75 +
  # new 1 = 76 정합) + 본 frontmatter list append 2번째 entry.
  # ADR-082 §결정 1 Layer 1 chief-author write-time verify 적용 — ArchitectAgent
  # 가 origin/main 67a541a 안 mechanical_enforcement_actions[] state direct
  # verify 후 list append (Story §2.1 row 4 stale framing 정정, intent invariant
  # 보존 — `codex-origin-main-directive-check` 신규 entry 진입은 정합 그대로).
  - action: codex-origin-main-directive-check
    status: deferred-followup     # CFP-1412 Phase 2 wire activation 시 evidence-checks-registry status: Active (workflow PR-time fire) — 본 ADR frontmatter status 는 Amendment 4 precedent 답습 (deferred-followup retain, registry yaml = Active)
    target_section: §결정 D9      # spawn prompt body 안 [ORIGIN-MAIN-DIRECTIVE] block presence-grep heuristic + closed-set 3 enum fallback marker (network_scope_offline / legacy_prompt_format / intentional_working_tree_verify)
  # Amendment 12 (CFP-2545, 2026-07-01) — D14 Codex companion 브로커 경로 wall-clock
  # ceiling mandate 신설 시 ADR-040 Amendment 3 §결정 7.A 의무 발효 (D1-D13 본문 의미
  # 변경 0, declaration-only retain 유지하면서 presence-grep mechanical lint layer 추가
  # = Amendment 4/8 precedent verbatim 답습). Phase 2 mechanical wire carrier (CFP-2545
  # Phase 2) — lint script (scripts/check-codex-companion-timeout-presence.sh +
  # scripts/lib/check_codex_companion_timeout_presence.py Python SSOT) + bats fixture
  # pair (RED→GREEN discriminating: timeout prefix 존재→GREEN / 제거 mutation→RED /
  # dispatch 발화 0건→exit 1 hollow-gate 차단) + fixture text files + workflow
  # byte-identical mirror (templates/ + .github/workflows/ ADR-005) +
  # evidence-checks-registry entry (status: Active, tier: warning) + label-registry
  # hotfix-bypass entry + 본 frontmatter list append 3번째 entry.
  - action: codex-companion-timeout-presence
    status: deferred-followup     # CFP-2545 Phase 2 wire activation 시 evidence-checks-registry status: Active (workflow PR-time fire) — 본 ADR frontmatter status 는 Amendment 4/8 precedent 답습 (deferred-followup retain, registry yaml = Active)
    target_section: §결정 D14     # codeforge-owned companion dispatch 발화(node ... codex-companion ... adversarial-review/--wait/task --write) 안 `timeout <N>` prefix presence-grep heuristic + dispatch 발화 건수 ≥1 검사 (발화 0건 → exit 1 hollow-gate 차단)
---

# ADR-081: Codex worker prompt boilerplate composition SSOT (3 mandatory section + verify-before-trust scope + 3-lane partition)

## 상태

Accepted (2026-05-17 KST, CFP-819 carrier).

## 컨텍스트

[verified] CFP-810 retro §6 후보 1 verbatim 인용 (`wrapper/retros/2026-05-17-cfp-810-kst-paren-exempt.md` L110):

> "Codex worker prompt boilerplate 표준화 + verify-before-trust ground-truth contract"

ADR-052 (Codex Proactive Check 6 touchpoints) + ADR-070 (verify-before-trust pattern) 은 두 가지 정책을 명문화했다:

- **ADR-052 D2** = "6 touchpoint 자동 활성, opt-in 없음" — dispatch 발동 자체의 normative anchor
- **ADR-070 D2** = "file content verbatim 첨부 의무" — artifacts payload 형식의 normative anchor

그러나 **Codex worker prompt 본문의 mandatory section composition** 영역은 normative anchor 부재 — playbook §3.10 dispatch prompt template 이 SSOT 역할을 도덕적 강제로 수행 중. 본 ADR 발의 직전까지 boilerplate 구성 룰이 어디서 정합한지 SSOT 없음. 즉 "어떤 정보가 prompt 안에 의무 첨부되어야 하는가"의 영역이 ADR-052 Amendment 5 (D2 cross-ref) 와 ADR-070 D2 (verbatim 의무) 사이 cross-document 분산 상태였다.

### 6-Story carry-over evidence sentinel (boilerplate 도입 효과 측정)

**"6-Story" 정의 (label vs file count disambiguation)** — 6-Story = **1 baseline cluster (CFP-770/771 paired carrier, same fp:8 incident) + 5 consecutive fp-0 (CFP-786/801/792/795/810)** = 총 **6 units** (1 cluster + 5 individual Story). file count 차원 = 7 retro file (cluster 안 2 file + 5 individual 1 file 씩).

[verified] 7 retro file 본 worktree 안 존재 (`Glob` + `ls` 결과, codeforge-internal-docs `wrapper/retros/` 영역):

| retro file | Story | codex_fp_tally | boilerplate evidence |
|---|---|---|---|
| `wrapper/retros/2026-05-16-cfp-770-kst-timestamp-display-mandate.md` | CFP-770 | 일부 (771 합산 = 8) | **baseline pre-boilerplate** |
| `wrapper/retros/2026-05-16-cfp-771-kst-timestamp-mechanical-lint.md` | CFP-771 | 일부 (770 합산 = 8) | **baseline pre-boilerplate** |
| `wrapper/retros/2026-05-17-cfp-786-main-baseline-ci-debt-cleanup.md` | CFP-786 | **0** | carry-over boilerplate 적용 시작 |
| `wrapper/retros/2026-05-17-cfp-801-claude-md-line-cap-normalization.md` | CFP-801 | **0** | carry-over boilerplate 정합 |
| `wrapper/retros/2026-05-17-cfp-792-canonical-sibling-sync.md` | CFP-792 | **0** | carry-over boilerplate 정합 |
| `wrapper/retros/2026-05-17-cfp-795-post-merge-fix-exemption.md` | CFP-795 | **0** + TRUE positive 적중 100% | carry-over boilerplate + 정확 적중 |
| `wrapper/retros/2026-05-17-cfp-810-kst-paren-exempt.md` | CFP-810 | **0** + cosmetic TRUE positive 적중 | carry-over boilerplate + carrier 5/7 sentinel reach YES |

**6-Story 누적 evidence (1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0)**: CFP-770/771 (fp 8 baseline cluster, paired carrier) → CFP-786/801/792/795/810 (5 consecutive fp 0 carry-over). 6 units 차원 = 1 cluster + 5 individual. file count 차원 = 7 retro file. boilerplate codification 정당성 충족.

### ADR-045 Amendment 5 §D-9 forcing function trace

PMOAgent `cross_story_pattern_adr_trigger` (pattern_count ≥ 2 → §6 ADR 후보 발의 의무) 의 forcing function 충족:

- pattern_count = 5 consecutive carry-over Story (threshold reach YES)
- anchor_id = `codex_worker_prompt_boilerplate_drift`
- escalation_action = `adr_draft_emitted` → 본 ADR-081
- cross-Story chain: [CFP-770/771 (1 baseline cluster, paired carrier)] + CFP-786/801/792/795/810 (5 consecutive fp-0) → CFP-819 (carrier). 6 units 차원 (1 cluster + 5) / 7 retro file 차원.

### Amendment 5 ↔ 본 ADR 영역 분리 (Story §2.4 PL synthesis verbatim)

| 영역 | ADR-052 Amendment 5 (CFP-578) | ADR-070 (CFP-578) | 본 ADR-081 (CFP-819) |
|---|---|---|---|
| dispatch 발동 (자동/optional) | ✅ D2 + Amd 1-5 (강화) | — | — |
| artifacts payload **형식** (verbatim vs path) | ✅ A1 (verbatim 의무) | ✅ D2 (verbatim 의무) | — (cross-ref) |
| verify-before-trust **흐름** (verify+reject) | — | ✅ D1/D3 | — (cross-ref) |
| prompt 본문 **mandatory section composition** | ❌ | ❌ | ✅ §결정 D1 (3 mandatory boilerplate 영역) |
| verify-before-trust **scope 분리** (file/dir/cross-repo) | ❌ | — | ✅ §결정 D2 (5 sub-scope 명세) |
| 3-lane partition (Codex / DesignReview / CodeReview disjoint) | ❌ | ❌ | ✅ §결정 D3 (3-lane disjoint scope 표) |

본 ADR-081 = ADR-052 Amendment 5 + ADR-070 D2 의 cross-document 분산 영역을 단일 SSOT 로 통합. ADR-052/070 본문 정책 의미 변경 0건 (Story §1 OOS 정합).

## 결정

본 ADR 은 declaration only — mechanical lint 부재 (D5 declaration-only retain 정합, ADR-070 §D5 precedent verbatim). 본문 normative anchor SSOT 만.

### D1. 3 mandatory boilerplate 영역

Codex worker spawn 시 ProactiveCheckPacket `artifacts` 필드 + prompt body 안 다음 3 mandatory section 의무:

#### D1.A — dogfood-out Story path (verbatim 첨부)

codeforge family 의 Story file 영역 (`mclayer/codeforge-internal-docs/<plugin-folder>/stories/CFP-NNN.md`) 의 verify 대상 §섹션 verbatim 첨부 의무. file path reference 만 사용 금지 (ADR-070 D2 / ADR-052 Amendment 5 A1 정합).

| 영역 | 운영적 정의 | 예시 verbatim |
|---|---|---|
| §1 사용자 요구사항 | story-section-1-immutable.yml SSOT, 변조 금지 invariant — 항상 verbatim 첨부 | `## §1. 사용자 요구사항 (verbatim)\n\n**발의 배경**: ...` |
| §2-§6 PL synthesis 본문 | RequirementsPL synthesis (도메인 해석 + 요구사항 확장) — touchpoint #4 review scope | `## §2. 도메인 해석\n...` |
| §7 설계 서사 | ArchitectAgent synthesis — touchpoint #2 review scope | `## §7. 설계 서사\n...` |
| §10 FIX Ledger | Orchestrator append 영역 — FIX 분석 시 verify scope | `## §10. FIX Ledger\n...` |

cap 초과 시 partial 첨부 허용 (verify 대상 영역만 verbatim + 나머지 `[partial: lines NN-NN]` marker, ADR-052 Amendment 5 A1 정합).

#### D1.B — lane stage 표기 (current_lane + phase)

Codex worker 가 어느 lane / phase 영역의 산출물을 verify 하는지 명시 의무:

```yaml
current_lane: <requirements|design|design-review|develop|code-review|security-test|integration-test>
phase: <phase:요구사항|phase:설계|phase:설계-리뷰|phase:구현|phase:구현-리뷰|phase:보안-테스트|phase:통합-테스트>
```

운영적 정의:

- Codex finding severity / category 가 lane scope 와 정합한지 cross-check 영역
- 3-lane partition (D3) 적용 영역 식별 — Codex factual citation 영역 vs DesignReview boundary completeness 영역 vs CodeReview style 영역 disjoint scope

#### D1.C — sandbox boundary 명시 (sandbox_outside_paths)

Codex sandbox 영역 외 file path enumerate 의무 (cross-repo / cross-plugin path 포함):

```yaml
sandbox_outside_paths:
  - mclayer/codeforge-internal-docs/wrapper/stories/CFP-NNN.md  # internal-docs (cross-repo)
  - mclayer/plugin-codeforge-{requirements,design,develop,review,test,pmo}/...  # sibling plugin (cross-plugin)
  - mclayer/marketplace/marketplace.json  # cross-repo
  - docs/inter-plugin-contracts/MANIFEST.yaml  # wrapper internal (sandbox 영역 가능성)
```

운영적 정의:

- Codex worker 가 own working directory 안 Read 불가 영역 식별
- 모든 sandbox_outside_paths file content = verbatim 첨부 의무 (ADR-070 D2 + ADR-052 Amendment 5 A1 정합)
- mechanical injection layer 부재 — Orchestrator turn 내 verbatim composition 수동 (declaration-only retain 정합)

#### D1.D — sandbox network requirement 명시 (`sandbox_network_required` toggle, Amendment 3 CFP-946 option 1)

Codex worker 가 spawn 시점에 sandbox-restricted 네트워크 operation (`gh api` / `git fetch` cross-repo / 외부 HTTP) 필요 여부를 명시적으로 declare 의무. CFP-946 option 1 (Codex CLI sandbox 모드 토글) carrier.

```yaml
sandbox_network_required: <bool>
```

운영적 정의:

- **`sandbox_network_required: true`** — Codex worker 가 cross-repo state / external resource fetch 필요 영역. 실패 시 Orchestrator-side substitution path activate 의무 (ADR-052 Amendment 8 3-enum: `inline_orchestrator_verify` default / `manual_substitution_declare` / `fallback_skip_with_marker` cross-matrix 정합).
- **`sandbox_network_required: false`** — Codex worker 가 sandbox-내부 file scope (Read / Grep / Glob) 만으로 verify 완결 영역. 즉시 finding emit 가능, substitution path 비활성.

운영적 정합:

- Codex CLI 자체 sandbox 모드 toggle 가능성은 codex@openai-codex plugin runtime 영역 — 본 field 는 codeforge 측 spawn prompt declaration only (mechanical injection layer 부재, declaration-only retain — Amendment 1/2 family pattern 정합)
- `true` declare 시 Orchestrator 는 dispatch 직후 sandbox failure mode 대응 plan 활성 (ADR-070 §결정 1 expansion substitution scope 3-path enum SSOT)
- `false` declare 시 sandbox failure = unexpected (Codex worker 가 unexpected sandbox restriction 발화 시 ADR-070 strict-verify-gate trigger — ADR-081 D7.c escape hatch 정합)
- D1.A (dogfood-out story path) + D1.B (current lane / phase) + D1.C (sandbox_outside_paths) + D1.D (sandbox_network_required) = 4 mandatory boilerplate field (Amendment 1/2 D1.A-C 영역 + 본 Amendment 3 D1.D 영역 disjoint append, D1.A-C 본문 의미 변경 0건)

cross-ref:

- ADR-052 Amendment 8 (CFP-946-A) — substitution path 3-enum SSOT (Orchestrator 측 dispatch policy)
- ADR-070 Amendment 3 (CFP-946-A) — §결정 1 expansion (substitution scope codify, Orchestrator inline verify-before-trust 자동화)
- ADR-081 D7.c (Amendment 2) — ground-truth divergence escape hatch (sandbox failure / strict-verify-gate trigger SSOT)
- 본 D1.D = spawn-prompt-side declaration / ADR-052 Amd 8 + ADR-070 Amd 3 = substitution-side mechanism. 양 면 chain 완결 (CFP-946 option 1 + option 2 + option 3 통합).

### D2. verify-before-trust scope 분리 (5 sub-scope)

Orchestrator 가 Codex finding evidence 의 ground truth verify 시 scope 별로 verify 방법 분리 의무 (ADR-070 D1 + ADR-073 정합):

#### D2.A — file scope verify (single file 안 grep count)

- **scope**: single file 안 anchor / line / 문자열 영역
- **verify 도구**: `Grep -n <pattern> <file>` 또는 `Read(<file>, offset, limit)` 직접 추출
- **claim 형식**: `[verified] <file>:<line> "<verbatim quote>"` (anchor + line + quote 3-tuple)
- **mismatch 처리**: ADR-070 D3 reject 흐름

#### D2.B — dir scope verify (recursive grep)

- **scope**: dir tree 안 file enumerate / pattern occurrence count
- **verify 도구**: `Glob` + `Grep` recursive (예: `Glob("docs/adr/ADR-*.md") + Grep("pattern", glob="docs/adr/*.md", output_mode="count")`)
- **claim 형식**: `[verified] <dir>/**/<file_pattern>: <N> matches` (dir + pattern + count 3-tuple)
- **mismatch 처리**: ADR-070 D3 reject 흐름

#### D2.C — cross-repo scope verify (gh api / git fetch origin)

- **scope**: sibling plugin / cross-repo (marketplace.json / internal-docs) file 영역
- **verify 도구**: `mcp__github__get_file_contents` 또는 `git fetch origin <repo>; git show origin/main:<path>` (ADR-073 정합)
- **claim 형식**: `[verified-cross-repo:<org>/<repo>@<branch>:<commit>] <file>:<line>` (repo + branch + commit + file + line 5-tuple)
- **mismatch 처리**: ADR-070 D3 reject 흐름 + ADR-073 D1 cross-repo verify 의무

#### D2.D — grep count claim verify (active vs historical 차원 명시 의무)

Codex 발화 "ADR-NNN 안 N 곳 에 X 단어 발화" claim 영역 = active scope vs historical scope 차원 명시 의무:

| 차원 | 운영적 정의 | 검증 방법 |
|---|---|---|
| **active scope** | 현재 효력 영역 — Amendment 본문 / 결정 본문 + 인용 영역 모두 포함 | `Grep("pattern", file)` 전체 count |
| **historical scope** | retro / archived ADR / FIX Ledger / Story 진행 이력 — 인용 영역 보존 의도 영역 | active count 와 분리 명시 ("active: M, historical: N") |
| **citation scope** | cross-ref 영역 (e.g. "ADR-052 §결정 D2") — 단어 발화 vs 인용 별도 | citation source = file:line 명시 |

claim mismatch 차원 = active vs historical 혼동 시 ADR-070 D3 reject + false positive count tally.

#### D2.E — ADR §결정 번호 정확성 verify

Codex 발화 "ADR-NNN §결정 N (또는 D-N)" claim 영역 = 실제 ADR file 안 해당 §결정 anchor 존재 확인 의무:

- **verify 도구**: `Glob("docs/adr/ADR-NNN-*.md") + Grep -nE "^### (D|결정) ?N" <file>`
- **claim 형식**: `[verified] <ADR file>:<line> "### <결정 N anchor>"` (anchor 존재 확인 + line + verbatim)
- **mismatch 처리**: ADR-070 D3 reject (false §결정 번호 발화 = false positive 영역)

### D3. 3-lane partition (Codex / DesignReview / CodeReview disjoint scope)

Codex worker output 영역 vs lane review agent (DesignReviewPL / CodeReviewPL) review 영역 disjoint scope 분리 의무. cosmetic detection 영역 type 분리.

| Lane | scope | mechanical anchor | 영역 type |
|---|---|---|---|
| **Codex worker** | factual citation — file:line evidence + verbatim quote + grep count + ADR §결정 번호 + cross-repo commit SHA **∪ execution ground-truth — 실행 exit code + stdout(semantic) = 재현 가능 객관 사실 (Amendment 11 / CFP-2477, §결정 D13)** | ADR-081 D2 (5 sub-scope) + ADR-070 D1/D2/D3 + Amendment 11 §결정 D9 + ADR-073 | **factual ground truth ∪ execution ground-truth** (verify-before-trust scope) |
| **DesignReviewPL** | boundary completeness — API contract semantic (I-1) + cross-module propagation (I-2) + conditional guard placement intent (I-3) + wording SSOT (I-4) + dimensional empirical grounding (I-5) | ADR-068 4 invariants + Amendment 1 I-5 | **boundary completeness self-audit** (review-verdict-v4 v4.4 carrier) |
| **CodeReviewPL** | post-impl style + historical reference 보존성 영역 — Story §10 P2-defer row 안 historical 5 refs 인용 영역 보존 의도 | review-verdict-v4 v4.5 (CFP-810 P2 C-002 precedent) | **style + history preservation** (post-impl review scope) |

**disjoint invariant**: 동일 anchor_id 영역에서 Codex + DesignReview + CodeReview 셋 모두 발화 시 = scope type mismatch 신호. 처리:

- Codex 발화 = factual citation **∪ execution ground-truth** 영역만 (`[verified]` marker 의무 — 실행 결과는 PL 직접 재실행 falsify 통과 시만 승격, ADR-070 Amendment 11 §결정 D9)
- DesignReview 발화 = boundary completeness 영역만 (4 invariant 안 분류)
- CodeReview 발화 = style + history 영역만 (post-impl scope)

영역 중복 발화 시 dedup → severity 높은 쪽 채택 (codeforge `review-responsibility` skill SSOT 정합).

### D4. ADR-052 / ADR-070 본문 정책 SSOT 보존 invariant

본 ADR-081 = cross-ref + downstream codification 만. ADR-052 D1-D4 + Amendment 1-5 본문 의미 변경 0. ADR-070 D1-D5 본문 의미 변경 0. Story §1 OOS "ADR-052/070 본문 정책 변경 금지" 정합.

ADR-052 Amendment 6 sub-section append (본 ADR-081 신규 영역 cross-ref 1 paragraph만) = 의미 변경 없음 (sub-section append 패턴 Amendment 1-5 정합).

### D5. evidence-enforceable framework entry append 면제 (declaration-only retain)

ADR-070 §결정 D5 precedent verbatim 정합. mechanical lint 가 검출 가능한 sentinel signal 영역의 후보 모두 robustness risk 보유:

| 후보 signal | 검출 가능성 | 메커니즘 | 적용 risk |
|---|---|---|---|
| (a) Codex spawn prompt 안 3 mandatory section 존재 검출 (regex) | HIGH | static regex on prompt body | false positive — prompt body 형식 자유도 (boilerplate template 절대값 부재) |
| (b) Codex worker output 안 5 sub-scope marker `[verified]` 발화 검출 | MEDIUM | output regex | locale 의존 + Codex output schema 영역 외 (안정성 risk) |
| (c) 3-lane partition 영역 disjoint scope 자동 비교 (Codex / DesignReview / CodeReview output cross-validation) | LOW | runtime probe (3 verdict packet anchor_id cross-diff) | platform inherent runtime probe 영역, mechanical lint 영역 외 |
| (d) **declaration-only ADR (mechanical lint 부재, 본 ADR 본문 SSOT)** | **HIGH** | 본 ADR 본문 normative anchor 만 | manual gate 의존 (의식 필요) |

**채택 = (d) declaration-only retain**. evidence-checks-registry.yaml entry append 면제 (ADR-070 §결정 D5-C 거절된 대안 정합 — "declaration-only retain 영역에서도 evidence-checks-registry entry append (warning tier 0-validation) = registry schema scope 침해").

**근거**:

1. (a)/(b)/(c) 모두 robustness risk 보유 — false positive 차단 cost 가 boilerplate 도입 cost 보다 큼
2. ADR-060 evidence-enforceable promotion framework 의 mechanical lint forcing function 확장 패턴 (CFP-389 → CFP-449 → CFP-481 → CFP-506 → CFP-530 carrier loop) 은 **static doc analysis 영역** (ADR frontmatter / forbid-list 어휘 / branch name parse / line count / yml structure) — 본 ADR 영역 (boilerplate composition / verify scope marker / 3-lane partition disjoint) 과 영역 type mismatch
3. 후속 carrier sentinel 조건 = 2 회 이상 mechanical lint 검출 가능 sample 누적 시 carrier 발의 (sentinel) — 현재 0 sample 누적

**거절된 대안 D5**:

- (D5-A) (a) static regex 채택 (Codex spawn prompt 안 3 mandatory section 존재 검출) — false positive 차단 cost 가 정당성 부재 (boilerplate template 형식 자유도 영역)
- (D5-B) (c) runtime probe 자동화 (3 verdict packet anchor_id cross-diff layer) — platform inherent 영역 침범 (Codex output schema parsing layer 신설 = 별도 carrier 영역)
- (D5-C) declaration-only retain 영역에서도 evidence-checks-registry entry append (warning tier 0-validation) — registry schema scope 침해 (ADR-070 §D5-C 거절된 대안 정합)
- (D5-D) marker 어휘 신설 (예: `[verified-file]` / `[verified-dir]` / `[verified-cross-repo]`) — CFP-810 retro §6 후보 5 정합, **별 carrier** 분리. 본 ADR scope = verify scope 분리 의무 본문 명시만, marker 어휘 변경 없음

---

## Amendment 1 (2026-05-17, CFP-844)

### Context (Amendment 1)

CFP-825 retro §6 후보 2 (PMOAgent `cross_story_pattern_adr_trigger`, `escalation_action: adr_draft_emitted`) carrier. D2 (verify-before-trust 5 sub-scope) 는 Codex finding **factual citation 정확성** (file:line / verbatim / grep count / ADR §결정 번호) 을 다룬다 — finding 의 **사실 근거** 검증 layer. 그러나 finding 의 **severity 경중 calibration** 영역 (Codex 가 발화한 P0/P1/P2 가 실제 review lane ground truth severity 와 정합하는가) 은 D1-D5 normative anchor 부재였다.

[verified] review-verdict-v4 v4.5 에 `codex_severity_inflation` field 미존재 (verified-via: `git show origin/main:docs/inter-plugin-contracts/review-verdict-v4.md` grep empty, `contract_version: "4.5"` CFP-597). 즉 severity calibration 추적 영역은 contract surface 부재 — 기존 prose channel (Story §9 verdict / §10 FIX Ledger 비고) 만 활용 가능. 본 Amendment 는 이 영역을 declaration-only normative anchor (신규 §결정 D6) 로 승격한다. D1-D5 본문 의미 변경 0건 — §결정 D6 sub-section append only (Amendment 패턴 = ADR-052 Amendment 1-6 / ADR-070 Amendment 1 정합).

### D6. Codex worker severity calibration rubric (declaration-only normative anchor)

ADR-081 §D5 declaration-only retain invariant (ADR-070 §D5 precedent verbatim) 정합 — §결정 D6 = declaration-only normative anchor, mechanical lint 부재. codex_severity_inflation tracking = 기존 Story §9/§10 prose marker (신규 review-verdict-v4 contract field 신설 0 — contract bump 회피, doc-only fast-path 유지).

#### D6.a — bidirectional severity anchor

Codex finding severity ↔ PL synthesis severity **양방향** calibration 의무:

1. **over-rate 금지**: Codex severity > PL synthesis severity (factual citation scope = D2.A-E) 시 PL 이 ground truth severity 로 calibrate. Codex sensitivity inflation 차단.
2. **security-relevant under-rate 금지**: Codex severity < 실제 보안 경중 시 PL 이 실제 severity 로 calibrate. over-rate 만 anchor 시 보안 blind spot 발생 risk (Researcher Unknown #2) — bidirectional anchor 가 차단 (ADR-064 broad coverage 정합).

#### D6.b — ground truth severity 우선순위

| 차원 | ground truth | 근거 |
|---|---|---|
| **primary** | DesignReviewPL final verdict severity | 설계 lane Codex proactive check (touchpoint #2) 표준 path |
| **fallback** | CodeReviewPL standalone severity | touchpoint #3 단독 dispatch 시 (DesignReview 미경유) |
| **양쪽 dispatch** | higher severity PL 기준 | codeforge `review-responsibility` skill dedup rule SSOT 정합 (ADR-081 D3 3-lane partition 정합) |

#### D6.c — boundary-completeness exception

Codex P0 boundary-completeness finding (review-verdict-v4 `findings[].type="boundary-completeness"`, ADR-068 I-1~I-5) × DesignReviewPL P1 final verdict = over-rate **아님** (PL incomplete audit 신호 — Codex sensitivity 정상, +1 tier 허용). 단 factual citation scope (D2.A-E) severity 불일치 = 순수 calibration 대상 (exception 미적용).

#### D6.d — disjoint axis preservation invariant

`codex_severity_inflation` (calibration axis) ≠ `codex_false_positive_tally` (accuracy axis) — 별개 axis. carry-over fp 0 chain sentinel (CFP-770/771 baseline → CFP-786/801/792/795/810 5 consecutive fp 0; ADR-081 6-Story sentinel) 무영향 — severity calibration 은 finding accuracy 와 무관 (finding 자체는 TRUE positive 이되 severity 만 mis-rate 한 경우 fp 0 chain 영향 0).

#### D6.e — tracking = 기존 Story §9/§10 prose marker (declaration-only)

PL 이 verdict 시 Codex finding severity ↔ PL synthesis severity delta 를 Story §9 verdict prose 또는 §10 FIX Ledger 비고에 marker 기재:

```
[codex-severity-inflation: Codex:P0 vs PL:P1 <scope>]
```

기존 prose channel 활용 — 신규 review-verdict-v4 contract field 신설 0 (contract bump 회피, doc-only fast-path 유지, ADR-081 §D5 declaration-only retain precedent verbatim 정합). mechanical lint = 별개 후속 carrier (sentinel 조건 = 2+ mechanical-detectable sample 누적 시, 현재 0 sample). **§결정 D6.e known-limitation explicit binding** — `mechanical_enforcement_actions[]=[]` retain 이 의도된 declaration-only 선택임을 명시 (ADR-040 Amendment 3 DesignReview missing-flag 회피, ADR-082 §결정 6 / ADR-070 §D5 선례 정합).

#### D6.f — sunset trigger 아님 명시

`codex_severity_inflation` count 자체 = calibration 추적 metric, ADR-081 유효성 indicator 아님. `is_transitional: false` (permanent governance). metric 0 수렴 = Codex accuracy 향상 + PL calibration 정착 둘 다 정상 (ADR-081 폐기 트리거 아님 — accuracy axis sunset gate 와 disjoint, D6.d 정합).

### 거절된 대안 D6

- (D6-A) review-verdict-v4 신규 `codex_severity_inflation` contract field 신설 (structured severity delta surface) — contract MINOR bump + sibling sync (ADR-008/010) + Phase 2 PR 필요 = doc-only fast-path 이탈. ADR-081 §D5 declaration-only retain precedent 위배. prose marker 채택 (mechanical lint 부재 영역 = contract surface 부적합, ADR-070 §D5-C 정합).
- (D6-B) over-rate 단방향 anchor (Codex severity > PL 만 차단) — security-relevant under-rate blind spot 미차단 (Researcher Unknown #2). bidirectional 채택 (ADR-064 broad coverage).
- (D6-C) boundary-completeness exception 미도입 (Codex P0 × DesignReview P1 = 무조건 over-rate) — ADR-068 I-1~I-5 incomplete audit 신호 (Codex sensitivity 정상) 를 false over-rate 로 오분류. +1 tier exception 채택 (D6.c).
- (D6-D) codex_severity_inflation 을 ADR-081 sunset metric 으로 채택 — accuracy axis (`codex_false_positive_tally`) 와 disjoint (D6.d). severity calibration metric 0 수렴 = 정상 (폐기 신호 아님). is_transitional false 유지 (D6.f).

### 결과 (Amendment 1)

- Codex finding severity ↔ PL synthesis severity bidirectional calibration normative anchor 신설 — D6 SSOT (declaration-only retain, §D5 precedent)
- ground truth severity 우선순위 (DesignReviewPL primary / CodeReviewPL fallback / higher PL 양쪽) 명시 — D6.b SSOT
- boundary-completeness exception (Codex P0 × DesignReview P1 = over-rate 아님, +1 tier) — D6.c SSOT
- disjoint axis preservation invariant (calibration ≠ accuracy, fp 0 chain 무영향) — D6.d SSOT
- tracking = 기존 Story §9/§10 prose marker (`[codex-severity-inflation: ...]`, contract field 신설 0) — D6.e SSOT
- D1-D5 본문 의미 변경 0건 — §결정 D6 sub-section append only (ADR-052 Amendment 1-6 / ADR-070 Amendment 1 패턴 정합, §D4 SSOT 보존 invariant 정합)
- ADR-052 Amendment 7 (D6 cross-ref sub-section append) + ADR-070 Amendment 2 (D6 보완 관계 cross-ref-only) sibling
- CLAUDE.md L170 blockquote severity calibration cross-ref 1 줄 추가 (line-cap 320 invariant 정합)
- ADR-RESERVATION 무접촉 (Amendment 영역 — row 81 = CFP-819 active 유지, ADR file 동일)
- `mechanical_enforcement_actions[]=[]` retain (declaration-only, §결정 D6.e known-limitation explicit binding)

## Amendment 2 (CFP-892)

CFP-892 carrier (Epic A close follow-up CFP 후보 1/6, PMO retro Story-4/5 carry-over). Issue #892 §3 sub-pattern 분류 verbatim — 3 outstanding gap:

1. **Codex digest-indentation 오독** (ANCHOR-2 FP class, Story-4 CFP-834) — Codex 가 yaml block 안 nested key indentation 잘못 읽음. D6 calibration anchor 가 severity calibration 영역 cover 하나 digest-parse mechanical pre-screen 부재.
2. **Codex severity over-claim** — D6.a/b/c 가 이미 cover. 단 quantitative P0/P1/P2/P3 grading 정량 기준 부재 — D6.b 의 ground truth severity ordering 만 있고 per-tier criteria 없음.
3. **ground-truth divergence escape hatch** — ADR-070 strict-verify-gate 가 이미 작동 중이나 ADR-081 § 안 explicit cross-ref 부재.

본 Amendment 2 = D6 보완 (D6 의미 변경 0건, §결정 D7 sub-section append only).

### D7. Codex worker digest-parse + severity rubric + escape hatch (declaration-only normative anchor)

ADR-081 §D5 declaration-only retain invariant 정합 — §결정 D7 = declaration-only normative anchor (mechanical lint 부재, D6 정합).

#### D7.a — digest-parse self-verification step (ANCHOR-2 FP class 차단)

Codex worker 가 yaml / json / markdown table 영역 finding 발화 직전 **indentation re-check** 의무:

- yaml block 안 nested key 의 indentation 을 visually verbatim re-read
- "이 contract_version 이 reinvestigation_tracking top-level block 의 일부인가, 아니면 contract-level field 인가" 류 ambiguous structural 판정 시 finding 발화 보류 + Story 본문 directly cite (file:line + 7 line 전후 context)
- self-verification 발화 marker: `[digest-parsed: <field-path> @ L<N> (indent <level>)]` Story §10 prose 안 inline

본 step 은 ANCHOR-2 FP class (Story-4 CFP-834 F-DESIGNREVIEW-CFP834-1 digest-indentation 오독) directly 차단 forcing function. CFP-892 §3 sub-pattern 1 carrier.

#### D7.b — quantitative P0/P1/P2/P3 grading rubric (D6.b 정량화)

| Tier | 의미 | criteria (Codex finding) | examples |
|---|---|---|---|
| **P0 (block)** | ship 차단 | (a) 정책 SSOT 위반 + verbatim grep 가능 evidence / (b) 보안 boundary 침해 (auth / secret / injection) / (c) data integrity invariant 위반 (rollback path 부재 schema bump) | "phase-gate-mergeable.yml 안 required check 명단 변경 시 ADR-024 §결정 위반 가능", "API key plaintext logging" |
| **P1 (blocker)** | ship 강력 차단 (PL 재량 review) | (a) ADR-068 boundary-completeness 4 invariant 부재 + Story §3 영향 area 명시 / (b) §7.4 OperationalRisk N/A 사유 부재 / (c) §8 Test Contract coverage 0 boundary | "P1 — design lane §3 cross-module propagation completeness 미충족 (I-2 위반)" |
| **P2 (improvement)** | defer 허용 (severity ≠ ship 차단) | (a) refactor 권장 / (b) wording 정확성 / (c) documentation gap (정책 SSOT 영역 외) / (d) historical pattern reference 보존 (CodeReview style+history) | "P2 — README example outdated, defer 가능", "P2 — comment 정확성 개선 권장" |
| **P3 (nit / cosmetic)** | non-blocking | (a) 어휘 선택 / (b) markdown formatting / (c) self-meta text precision (lint 자체 spec 인용 등) | "P3-cosmetic — section header 어휘 선택" |

**boundary-completeness exception (D6.c 정합)** — Codex P0 boundary-completeness × DesignReview P1 = +1 tier 허용 (PL incomplete audit 신호, calibration over-rate 아님).

**security-relevant under-rate 차단 (D6.a 정합)** — Codex 가 보안 영역 P2 / P3 발화 시 PL 이 실제 severity 로 calibrate (security blind spot 차단).

본 표 = D6.b ground truth severity ordering (DesignReviewPL primary / CodeReviewPL fallback) 의 per-tier criteria. ADR-064 broad coverage 정합 (4-tier criteria → grading ambiguity 차단).

#### D7.c — ground-truth divergence escape hatch (ADR-070 cross-ref explicit)

Codex P0 claim 시 Orchestrator strict-verify-gate (ADR-070 verify-before-trust) 가 **자동 trigger** — Codex P0 finding 의 ground truth (file content / grep / ADR §결정 verbatim) 를 Orchestrator 가 direct Read 로 verify. mismatch 감지 시:

- 1차: Codex finding reject + Story §10 false positive count tally + override rationale prose
- 2차: review-verdict-v4 v4.5 `codex_false_positive_tally` count + 1

본 escape hatch = ADR-070 §결정 1 mandate (Codex finding evidence ground-truth direct verify) 의 ADR-081 D6/D7 calibration framework 안 explicit cross-ref. 신규 mechanism 아님 — ADR-070 기존 mechanism 의 declaration-only 명시화 (declaration-only retain precedent §D5 정합).

#### D7.d — disjoint axis preservation (D6.d 재확인)

D7.a (digest-parse), D7.b (P0/P1/P2/P3 rubric), D7.c (escape hatch) 셋 모두 D6.d disjoint axis invariant 정합:

- `codex_severity_inflation` (calibration axis, D6) ≠ `codex_false_positive_tally` (accuracy axis, ADR-070) — 별개 measurement
- D7.a digest-parse FP 는 **accuracy axis** 영향 (FP count +1) — calibration 무관
- D7.b severity rubric 정량화 는 **calibration axis** 강화 — accuracy 무관
- D7.c escape hatch 는 **accuracy axis** layer (FP detection forcing function) — calibration 영역 외

fp 0 chain sentinel (CFP-770/771 baseline → CFP-786/801/792/795/810 5 consecutive fp 0) 무영향 (D7 = declaration-only, mechanical detection 부재).

### 거절된 대안 D7

- (D7-A) review-verdict-v4 신규 `codex_severity_grade` enum field (P0/P1/P2/P3) 신설 — contract MINOR bump + sibling sync. doc-only fast-path 이탈. D6.e prose marker 채택 precedent 정합 (declaration-only retain).
- (D7-B) digest-parse self-verification mechanical lint (Codex worker output 안 `[digest-parsed: ...]` marker grep) — D6.e mechanical lint 부재 invariant 위반. declaration-only retain.
- (D7-C) ADR-070 §결정 1 본문 amend (ADR-081 D7.c escape hatch 를 ADR-070 안 직접 codify) — ADR-070 본문 의미 변경 (D5 SSOT 보존 invariant 위반). cross-ref-only 채택.
- (D7-D) P0/P1/P2/P3 + P4 (5-tier) 확장 — codeforge ground-truth 4-tier (review-verdict-v4 + severity-propagation-v1 v1.0) 와 mismatch. 4-tier 유지 (contract surface 정합).

### 결과 (Amendment 2)

- Codex worker digest-parse self-verification step normative anchor — D7.a SSOT (ANCHOR-2 FP class directly 차단)
- quantitative P0/P1/P2/P3 grading rubric (4-tier criteria) — D7.b SSOT (D6.b 정량화)
- ground-truth divergence escape hatch ADR-070 cross-ref explicit — D7.c SSOT (declaration-only)
- disjoint axis preservation invariant (D6.d 재확인) — D7.d SSOT
- D1-D6 본문 의미 변경 0건 — §결정 D7 sub-section append only (Amendment 1 패턴 정합)
- `mechanical_enforcement_actions[]=[]` retain (declaration-only, §D5 + D6.e precedent)
- is_transitional false 유지 (permanent governance, ratchet 강화 only)

## Amendment 3 (CFP-946, 2026-05-18 KST)

### Context (Amendment 3)

CFP-946 carrier (option 1 — Codex CLI sandbox 모드 토글 정의 + Orchestrator spawn prompt 의무 field). PR #962 merge 직후 본 ADR-081 frontmatter `amendments[]` 에 `amendment_id: 3` entry 가 declare 되었으나 body `## Amendment 3` 헤더 backfill 누락 — CFP-963 ArchitectPL discovery (2026-05-19 KST, ADR-064 §결정 1 derived default 정합 per scope unitary, CFP-963 ratchet-up D1.D 본문 확장 carrier 영역과 disjoint). CFP-1001 Story Tier-A scope (ADR amendment_log drift cleanup) 가 본 backfill carrier — 본문 의미 변경 0건 invariant 보존 (frontmatter L19-L25 `scope` field verbatim 반영).

### 결정 (Amendment 3 verbatim scope, frontmatter L19-L25 mirror)

신규 §결정 D1.D (sandbox_network_required toggle) append — Codex worker spawn prompt 가 sandbox-restricted network operation (gh api / git fetch cross-repo / 외부 HTTP) 필요 여부 declare 의무 codify. CFP-946 option 1 (Codex CLI sandbox 모드 토글 정의 + Orchestrator spawn prompt 의무 field) carrier. true = substitution path activate 영역 (ADR-052 Amendment 8 3-enum cross-matrix 정합), false = sandbox-내부 file scope only verify 완결 영역. D1.A (dogfood-out path) + D1.B (current lane/phase) + D1.C (sandbox_outside_paths) + D1.D (sandbox_network_required) = 4 mandatory boilerplate field. D1.A-C 본문 의미 변경 0건 — D1.D disjoint append only. mechanical injection layer 부재 (declaration-only retain — Amendment 1/2 family pattern 정합). cross-ref ADR-052 Amendment 8 + ADR-070 Amendment 3 (substitution-side mechanism) — 양 면 chain 완결 (option 1 + option 2 + option 3 통합). is_transitional false 유지 (permanent governance). mechanical_enforcement_actions[]=[] retain (§D5 declaration-only precedent 정합).

### 결과 (Amendment 3)

- §결정 D1.D `sandbox_network_required: <bool>` boolean toggle Codex worker spawn prompt mandatory field 신설 (4번째 boilerplate field — D1.A/D1.B/D1.C 동반)
- ADR-052 Amendment 8 (6 touchpoint × substitution path 3-enum cross-matrix) + ADR-070 Amendment 3 (substitution-side §결정 D1 expansion) chain 완결 — option 1 (본 Amendment) + option 2 (ADR-070) + option 3 (ADR-052) 통합
- D1.A-C / D6 / D7 본문 의미 변경 0건 — D1.D disjoint append only (Amendment 1/2/4 패턴 정합)
- `mechanical_enforcement_actions[]=[]` retain (§D5 declaration-only, mechanical injection layer 부재)
- is_transitional false 유지 (permanent governance)

### Cross-ref note (CFP-963 ArchitectPL discovery — body header backfill carrier)

본 `## Amendment 3` 헤더 본문 = CFP-946 PR #962 merge 시점 frontmatter `amendments[]` L19-L25 entry 와 동시 작성되었어야 하나 누락. CFP-963 ArchitectPL spawn 시점 discovery (2026-05-19 KST) → ADR-064 §결정 1 (CFP scope unitary) 정합 deferred = CFP-1001 carrier 분리 (CFP-963 = D1.D ratchet-up 본문 확장 scope, CFP-1001 = ADR amendment_log drift cleanup scope, 양 CFP disjoint). 본 carrier 의 effect = frontmatter `amendments[]` ↔ body `## Amendment N` 2-way sync invariant 복원 (ADR-068 I-1 API contract semantic completeness 정합 — body declaration ↔ frontmatter array 2-way sync scoped to ADR-081 Amendment 3).

## Amendment 4 (CFP-963, 2026-05-19 KST)

### Context (Amendment 4)

PR #962 merge (CFP-946 closing) 가 §결정 D1.D `sandbox_network_required: <bool>` boolean toggle 을 spawn-prompt boilerplate 4번째 mandatory field 로 codify. 도입 시점부터 boolean 2-state (true / false) 가 substitution path 3-enum (`inline_orchestrator_verify` / `manual_substitution_declare` / `fallback_skip_with_marker`, ADR-052 Amendment 8) 의 입력 신호로 작동 — 단 boolean 표현력이 **codex CLI 실제 sandbox network 행위 폭** 을 cover 하지 못한다.

Researcher Phase 0 evidence [verified] (`github.com/openai/codex` README + `docs/sandbox.md` cross-ref via CFP-946-A): codex CLI 는 `--allow-network` flag + `sandbox.network_access` config 노출, file IO ↔ network egress disjoint control. 즉 spawn-prompt declaration layer 도 (a) **file-IO-only sandbox 영역** (codex 자체 sandbox 안 own working directory file Read 만 verify) vs (b) **own-repo git fetch 한정 영역** (cross-repo 미허용) vs (c) **broad external egress 영역** (gh api / cross-repo git fetch / 외부 HTTP) vs (d) **fallback substitution path activated 영역** (codex CLI 미가용 / sandbox network-block 확정 → Orchestrator substitution) 4-tier semantics 분리가 정합한 표현.

boolean 2-state (true ↔ {b, c} ambiguous / false ↔ a only) 는 (b) / (c) / (d) 영역 disambiguation 부재. CFP-963 = boolean → 4-tier enum strict ratchet-up (정보 손실 0, scope 축소 0). D1.A-C 본문 의미 변경 0건 — D1.D 본문만 확장.

또한 ADR-040 Amendment 3 §결정 7.A self-application: 본 Amendment 4 가 신규 lint carrier (`codex-network-scope-presence`, ADR-060 Amendment 14) 도입 → `mechanical_enforcement_actions[]` frontmatter binding 의무 발효 (Amendment 1/2 D6/D7 영역 = declaration-only retain mechanical_enforcement_actions[]=[] 정합, 본 Amendment 4 만 신규 lint carrier 이므로 ADR-040 Amendment 3 §결정 7.A mandate 적용 — `[]` → list[object] 전환).

### D1.D 확장 — `network_scope: <4-tier enum>` (boolean → 4-tier strict ratchet-up)

기존 §결정 D1.D 본문 (`sandbox_network_required: <bool>`) 의 in-place 확장. boolean field 명 (`sandbox_network_required`) 폐기 + 신규 field 명 (`network_scope`) 으로 rename + type change. 단 backward-compat grace 윈도우 의무 (아래 §D1.D.legacy_grace_window 정합).

```yaml
network_scope: <4-tier enum value>
```

#### D1.D 운영적 정의 (4-tier enum value SSOT)

| Enum value | Semantics | spawn-prompt declare 조건 | substitution path 3-enum mapping (ADR-052 Amd 8) |
|---|---|---|---|
| `offline` | codex CLI sandbox 안 own working directory file Read 만으로 verify 완결. network egress 0. | Codex worker 가 single file 영역 grep / quote / line-anchor verify task — sandbox-내부 file scope 만 | `inline_orchestrator_verify` (default) — codex worker output 정상 수신 + finding evidence 영역 = own working directory 안 |
| `repo-fetch-only` | codex CLI sandbox 안 own-repo file Read + own-repo `git fetch` 허용. cross-repo egress 0. | Codex worker 가 own-repo 안 dir scope recursive grep / commit-anchor verify task — own-repo file history 영역 | `inline_orchestrator_verify` (default — own-repo 영역 = Orchestrator working directory 인접) |
| `web-fetch` | codex CLI sandbox 가 cross-repo `gh api` / cross-repo `git fetch` / 외부 HTTP egress 허용. external egress 활성. | Codex worker 가 cross-repo state (sibling plugin / marketplace.json / internal-docs) verify task — cross-repo state 5-tuple verify scope (ADR-081 §결정 D2.C 정합) | `manual_substitution_declare` (sandbox 영역 외 file verify task 필요 시) |
| `offline_substitution_declared` | codex CLI 자체 미가용 / sandbox network-block 확정 / 8+ occurrence sentinel reentrant 위험 영역 → Orchestrator substitution path activate. spawn 자체 skip. | Codex CLI 미가용 (api_missing / version_skew / enterprise_blocked, fail-mode 9-enum 정합) | `fallback_skip_with_marker` (codex worker spawn 자체 skip + Orchestrator verify-before-trust 5 sub-scope 全 적용) |

#### D1.D 운영적 정합

- `offline` / `repo-fetch-only` / `web-fetch` = codex worker **spawn 활성** 영역 (codex CLI 가용). codex spawn-prompt 본문에 `network_scope` declare → codex CLI 자체 sandbox toggle (codex@openai-codex plugin runtime) 의 입력 신호.
- `offline_substitution_declared` = codex worker **spawn 자체 skip** 영역 (codex CLI 미가용). Orchestrator inline substitution path (verify-before-trust 5 sub-scope D2.A-E 단독 수행). Story §10 marker `[codex-sandbox-fallback: <fail-mode>]` 동반 의무 (fail-mode 9-enum 정합).
- 4 enum value 모두 codeforge 측 spawn-prompt declaration only — **declaration-only retain 유지 (§D5 precedent)**, codex CLI sandbox 자체 행위 변경 = codex@openai-codex plugin runtime 영역 (codeforge 비소유).
- `network_scope` value semantic ↔ ADR-070 substitution scope 3-enum / fail-mode 9-enum 사이 orthogonal:
  - `network_scope` = **WHAT scope** (4-tier: offline / repo-fetch-only / web-fetch / offline_substitution_declared)
  - substitution path = **HOW substitute** (3-enum: inline_orchestrator_verify / manual_substitution_declare / fallback_skip_with_marker)
  - fail-mode = **WHY failed** (6-enum: api_missing / version_skew / enterprise_blocked / gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only)
  - 3-축 disjoint, 1 spawn 안 동시 declare 가능 (orthogonal — 의미 overlap 0).

#### D1.D.legacy_grace_window — boolean → 4-tier enum backward-compat 운영 정합

PR #962 merge 후 (CFP-946) `sandbox_network_required: <bool>` boolean field 가 codified — 본 Amendment 4 적용 시점에 신규 Story 가 이미 boolean 사용 가능성 존재 (Story §4.1.3 파괴적 변경 후보 verify 영역). backward-compat grace 운영:

- **boolean → enum advisory mapping** (read-side, lint 영역):
  - `sandbox_network_required: false` ↔ `network_scope: offline` (file-IO-only 영역 정합)
  - `sandbox_network_required: true` ↔ `network_scope: web-fetch` (default broad path) **OR** `network_scope: repo-fetch-only` (narrower variant, explicit declare 필요 — boolean → enum mapping ambiguous, 신규 declare 시 explicit recommendation)
  - `offline_substitution_declared` = boolean equivalent 부재 (strict ratchet-up — Amendment 4 신규 영역)
- **write-side recommendation**: 본 Amendment 4 merge 후 신규 Codex worker spawn-prompt 작성 시 `network_scope: <4-tier enum>` 형식 권장 (boolean legacy 회피).
- **lint 운영** (`codex-network-scope-presence` warning tier, ADR-060 Amendment 14 carrier):
  - `network_scope: <4-tier enum>` present = PASS
  - `sandbox_network_required: <bool>` legacy present + `network_scope` absent = **advisory warn** `[legacy-boolean-detected]` PR comment, **exit 0 unconditionally** (warning tier first, ADR-068 I-3 unconditional guard placement 정합 — 본 grace 는 lint flag gating 없이 무조건 advisory)
  - 둘 다 absent = **advisory warn** (presence missing) PR comment, exit 0
  - 둘 다 present + value 정합 = PASS (legacy coexist 정합)
- **grace window 종료 trigger** (declarative-only, manual proposal on trigger reach — auto-firing 부재):
  - **`pr_cumulative_min: 20`** (ADR-060 §결정 6(b) default precedent-aligned per ADR-068 I-5 dimensional empirical grounding — `dimension category: count, units: merged-PR-count-with-enum-only-network-scope-usage, empirical-source: ADR-060 §결정 6(b) STANDARD threshold 22 entry retroactive verified prior art, conservative ratchet`) 안 enum-only 사용 PR count = 20 reach + boolean usage = 0 의 OR
  - **explicit user/PMO escalation** (사용자 directive 또는 PMO retro carrier)
- **grace window 종료 시 별 follow-up Amendment 5 reservation**: boolean field name 폐기 + lint hard-fail 승격. 본 Amendment 4 = 4-tier enum 도입만 (CFP scope unitary ADR-064 §결정 1 정합 — "경량 → full" 단계 차단).

#### D1.D 결정 영역 (cross-ref)

- ADR-052 Amendment 8 (CFP-946-A) — substitution path 3-enum SSOT (Orchestrator 측 dispatch policy). `network_scope` 4-tier ↔ substitution 3-enum 표준 mapping 위 D1.D 운영적 정의 표.
- ADR-070 Amendment 3 (CFP-946-A) — §결정 1 expansion (substitution scope codify, Orchestrator inline verify-before-trust 자동화). graceful degradation step (b) base SSOT.
- ADR-081 D7.c (Amendment 2) — ground-truth divergence escape hatch. `offline_substitution_declared` value 의 substitution scope 3-path enum trigger 영역 = D7.c escape hatch 자동 trigger.
- playbook §3.10 (CFP-963 graceful degradation step pair (a)(b)(c) sub-section) — step (a) detect (codex --help / codex --version / gh api /rate_limit) → step (b) declare `network_scope: offline_substitution_declared` + verify-before-trust 5 sub-scope full apply → step (c) Story §10 marker + §14 `network_scope_actual` field.
- 본 D1.D = spawn-prompt-side declaration / ADR-052 Amd 8 + ADR-070 Amd 3 = substitution-side mechanism. 양 면 chain 완결 (CFP-946 option 1 + option 2 + option 3 통합 + CFP-963 mechanical layer = closing-the-loop).

### 거절된 대안 D1.D-amend

- (D1.D-A) boolean retain + 4-tier enum 신설 (양 field coexist 영구) — surface 분기 + grace window 무한 = scope 모호. 4-tier enum 으로 단일 source (boolean legacy grace = open-ended until trigger) 채택 (ADR-064 broad coverage).
- (D1.D-B) 4-tier 대신 5-tier 확장 (`offline` + `repo-fetch-only` + `cross-repo-fetch-only` + `web-fetch` + `offline_substitution_declared`) — cross-repo / external HTTP 분리. codex CLI 자체 toggle 영역에서 cross-repo vs external HTTP disambiguation 부재 (codex CLI sandbox 단일 toggle, `--allow-network` 만 노출) → 추가 분기 의미 없음. 4-tier 유지 (CFP-966 lesson "신규 unique drift value 회피" 정합).
- (D1.D-C) boolean → enum 즉시 폐기 (grace window 0) — PR #962 merge 직후 환경에서 신규 Story breaking change risk. open-ended grace window (declarative-only `pr_cumulative_min: 20` enum-only + manual escalation) 채택.
- (D1.D-D) `codex-network-scope-presence` lint mechanical injection layer 신설 (declaration-only retain invariant 폐기) — §D5 declaration-only retain precedent 위반 + mechanical injection layer = codex@openai-codex plugin runtime 영역 침범. **declaration-only retain 유지 + presence-grep warning lint (ADR-060 framework entry)** 채택 — 보완 관계 (declaration ≠ presence verification axis), CFP-722 story-section-ownership / CFP-841 corpus-claim-verify 선례 동형.
- (D1.D-E) ADR-052 Amendment 9 신설 (fail-mode 6-enum mechanical detection cross-ref) — Amendment 8 cross-matrix 이미 codify, 신규 enum value 0. cross-ref-only (ADR-081 D1.D 본문에 정합) 채택 (CFP-966 lesson "신규 unique drift value 회피" 정합, §결정 1 CFP scope unitary).

### 결과 (Amendment 4)

- §결정 D1.D body 확장 — `network_scope: <4-tier enum>` strict ratchet-up codify (boolean 2-state → 4-state, 정보 손실 0)
- 4-tier enum value SSOT 표 (offline / repo-fetch-only / web-fetch / offline_substitution_declared + substitution-path mapping + fail-mode orthogonality) — D1.D 운영적 정의 SSOT
- backward-compat grace window 운영 정합 — D1.D.legacy_grace_window SSOT (boolean → enum advisory mapping, `[legacy-boolean-detected]` warn + exit 0 unconditional, `pr_cumulative_min: 20` enum-only ratchet trigger + manual escalation)
- `mechanical_enforcement_actions[]` 전환 — frontmatter list[object] entry `codex-network-scope-presence` (status: deferred-followup, target_section: §결정 D1.D) 신설. ADR-040 Amendment 3 §결정 7.A self-application 정합 (Amendment 1/2 D6/D7 영역 = declaration-only retain mechanical_enforcement_actions[]=[] 정합 별도 보존, 본 Amendment 4 = 신규 lint carrier 영역만 list[object] 전환).
- declaration-only retain invariant **유지** (§D5 precedent — mechanical injection layer 부재, presence-grep warning lint 은 ADR-060 framework 의 별 entry 영역, CFP-722 / CFP-841 선례 동형 — 보완 관계 = 상충 0)
- D1.A-C / D2 / D3 / D4 / D5 / D6 / D7 본문 의미 변경 0건 — §결정 D1.D body 확장 only
- ADR-052 Amendment 8 + ADR-070 Amendment 3 + playbook §3.10 (CFP-963 graceful degradation step pair sub-section) cross-ref chain 완결 — CFP-946 option 1+2+3 + CFP-963 mechanical layer = closing-the-loop
- is_transitional false 유지 (permanent governance, ratchet 강화 only — ADR-058 §결정 5 sunset_justification 통과)

## Amendment 5 (CFP-1003, 2026-05-19 KST)

### Context (Amendment 5)

본 ADR-081 의 §결정 D1.A-D 4 mandatory boilerplate field (D1.A dogfood-out Story path / D1.B current lane / phase / D1.C sandbox_outside_paths / D1.D `network_scope: <4-tier enum>`) 는 Codex worker spawn prompt 본문 안 의무 선언 영역으로 codify. 단 본 4 field 의 적용 scope = ADR-052 6 touchpoint proactive dispatch 영역 (codeforge 강제 invariant 정합).

CFP-963 Codex TP#4 가 reactive `codex:rescue` 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역, ADR-070 D1 L110 `사용자 책임 영역 (적용 외)`) 의 boilerplate composition deferred 결정 (CFP-963 Story §6.3 OOS row L374 verbatim `Codex CLI reactive channel (codex:rescue) network_scope lint = OUT (derived default) proactive 6 touchpoint spawn 한정 (ADR-052 proactive/reactive 분리) — reactive 확장 = 별 CFP` + §3 EC-2 L328 동형). 본 deferred scope = CFP-1003 carrier closure.

본 Amendment 5 = **D1.A-D 4 mandatory field 의 적용 scope codify** (proactive 영역 codeforge 강제 invariant explicit anchor + reactive 영역 best-effort 가이드 anchor 확장 적용). D1.A-D / D2-D7 본문 의미 변경 0건 — sub-section append 패턴 (Amendment 1-4 정합).

ADR-052 Amendment 9 + ADR-070 Amendment 5 + 본 ADR-081 Amendment 5 = chain (ADR-052 = proactive 채널 SSOT 본문 보존 cross-ref / ADR-070 = reactive 영역 substitution scope + sandbox boundary normative anchor / ADR-081 = reactive 영역 spawn prompt boilerplate 4 mandatory field 확장 적용).

### 결정 (Amendment 5)

**A1. D1.A-D 4 mandatory field 의 적용 scope 표 (proactive 강제 + reactive best-effort)**

기존 §결정 D1.A-D 본문 의미 변경 0건. 본 Amendment 5 = D1.A-D 4 field 의 적용 scope explicit codify:

| Field | proactive 6 touchpoint (codeforge 강제) | reactive `codex:rescue` (사용자 ad-hoc, ADR-022 Deprecated default + ADR-070 D1 L110 사용자 책임 영역) |
|---|---|---|
| **D1.A — dogfood-out Story path verbatim 첨부** | **강제 invariant** (ADR-052 Amendment 5 본문 SSOT 정합) | **best-effort 가이드 anchor** (사용자 자율 선택, codeforge 강제 0) — 사용자 ad-hoc invocation 시 verify 대상 §섹션 verbatim 첨부 권장 |
| **D1.B — current_lane / phase 표기** | **강제 invariant** (ADR-052 6 touchpoint behavior SSOT 정합) | **best-effort 가이드 anchor** — 사용자 ad-hoc invocation 시 current_lane / phase 명시 권장 (사용자 자율 선택) |
| **D1.C — sandbox_outside_paths enumerate** | **강제 invariant** (ADR-070 D2 verbatim 첨부 의무 정합) | **best-effort 가이드 anchor** — 사용자 ad-hoc invocation 시 sandbox 영역 외 file path enumerate 권장 (사용자 자율 선택) |
| **D1.D — `network_scope: <4-tier enum>` declare** | **강제 invariant** (4-tier enum 의무 — offline / repo-fetch-only / web-fetch / offline_substitution_declared) | **best-effort 가이드 anchor** — 사용자 ad-hoc invocation 시 4-tier enum 채택 권장 (사용자 자율 선택, codeforge 강제 0) |

본 표 = D1.A-D 4 mandatory field 적용 scope SSOT. proactive 영역 = codeforge 강제 invariant (Amendment 1-4 정합) + reactive 영역 = best-effort 가이드 anchor (사용자 자율 선택, ADR-070 D1 L110 사용자 책임 영역 invariant 보존). D1.A-D 본문 의미 변경 0건.

**A2. reactive 영역 best-effort 가이드 anchor 본문 (사용자 ad-hoc invocation 시 4 field 채택 권장)**

reactive `codex:rescue` 채널 사용자 ad-hoc invocation 시 D1.A-D 4 mandatory field 채택 권장 (codeforge 강제 미발효, 사용자 자율 선택 영역):

1. **D1.A 채택 권장** — spawn prompt 본문 안 verify 대상 §섹션 verbatim 첨부 (ADR-070 D2 best-effort 가이드 anchor 정합). 부재 시 risk: silent fallback 외부 web fetch 또는 GPT-5.4 training data 기반 finding 발화 risk (ADR-070 §컨텍스트 sentinel 1-3 evidence 동일).
2. **D1.B 채택 권장** — current_lane / phase 표기 (예: `current_lane: design-review / phase: phase:설계-리뷰`). Codex finding severity / category 의 review lane scope 정합성 cross-check 영역. 부재 시 risk: 3-lane partition (Codex / DesignReview / CodeReview, ADR-081 §결정 D3) scope mismatch.
3. **D1.C 채택 권장** — sandbox_outside_paths enumerate (cross-repo / cross-plugin path 포함). 부재 시 risk: Codex worker 가 own working directory 안 Read 불가 영역 식별 부재 → sandbox failure 시 substitution path activate trigger 모호.
4. **D1.D 채택 권장** — `network_scope: <4-tier enum>` declare (offline / repo-fetch-only / web-fetch / offline_substitution_declared). 부재 시 risk: TH-1 (sandbox bypass misdeclaration — sandbox-restricted network operation 발화 가능성) + TH-2 (PAT exposure — Codex worker 가 cross-repo state verify task 수행 시 CODEFORGE_CROSS_REPO_PAT 또는 user gh CLI auth context 노출).

본 4-anchor = reactive 영역 best-effort 가이드. 사용자 ad-hoc invocation 시점에 anchor 채택 / 비채택 = 사용자 책임 영역. codeforge 측 강제 미발효 invariant retain (ADR-070 D1 L110 `사용자 책임 영역 (적용 외)` 본문 정합).

**A3. reactive 영역 mechanical lint scope = Wave 2 carrier 분리 (ADR-064 §결정 1 unitary)**

`codex-network-scope-presence` lint (Amendment 4 의 `mechanical_enforcement_actions[]` entry, evidence-checks-registry entry SSOT) 의 mechanical detection scope = proactive 6 touchpoint spawn prompt 한정 (CFP-963 Story §6.3 OOS row L374 derived default 정합) — reactive 영역 mechanical lint 확장 = 별 CFP carrier 분리 (Wave 2). ADR-064 §결정 1 (CFP scope unitary) 정합. 본 Amendment 5 = `mechanical_enforcement_actions[]` 변경 0건 (Amendment 4 entry retain, scope expansion = Wave 2 carrier).

Wave 2 follow-up CFP scope (별 carrier 분리):

- evidence-checks-registry entry description scope 확장 — proactive 6 touchpoint + reactive 채널 양면 (현재 entry description 본문 patch = Amendment 5 Wave 1 declarative-only scope 영역)
- `scripts/lib/check_codex_network_scope.py` reactive spawn prompt detection logic 확장 (mechanical lint scope expansion)
- bats fixture pair (reactive spawn prompt with/without 4 field) — discriminating
- Story §10 marker 신규 enum value 또는 disjoint marker (`[codex-rescue-fallback: <fail-mode>]` reactive variant)

본 Wave 2 carrier = CFP-1003 retro 발의 시점 (또는 사용자 directive 시점) 별 CFP 분리.

**A4. D1.A-D 본문 의미 변경 0건 + D2-D7 + Amendment 1-4 본문 의미 변경 0건**

본 Amendment 5 = D1 sub-section 안 적용 scope 표 본문 강화 only (proactive 강제 + reactive best-effort 가이드 2-column). D1.A-D 본문 의미 변경 0건 (codeforge 강제 invariant 정합 보존) + D2/D3/D4/D5/D6/D7 + Amendment 1/2/3/4 본문 의미 변경 0건 — sub-section append 패턴 (Amendment 1-4 정합).

**A5. ADR-081 §D5 declaration-only retain precedent chain 6번째 instance**

`mechanical_enforcement_actions[]` Amendment 4 의 `codex-network-scope-presence` entry retain (변경 0건). reactive 영역 mechanical lint scope expansion = Wave 2 carrier 분리 (A3 SSOT) — 본 Amendment 5 = declaration-only normative anchor only. ADR-082 §결정 6 known-limitation rationale precedent chain 6번째 instance (ADR-070 D5 → ADR-082 §6 → ADR-081 D5/D6.e → ADR-070 Amd 5 → ADR-081 Amd 5).

**A6. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

- `is_transitional: false` 본 ADR 유지 (permanent governance, D1.A-D 4 mandatory field 적용 scope codify = permanent strengthening — proactive codeforge 강제 + reactive best-effort 가이드 양립)
- `sunset_justification: "N/A — permanent strengthening (D1.A-D 4 mandatory field 적용 scope codify, proactive 6 touchpoint codeforge 강제 invariant + reactive `codex:rescue` 사용자 책임 영역 invariant 양립 보존, 약화 영역 0. ADR-081 §D5 declaration-only retain precedent chain 6번째 instance — mechanical_enforcement_actions[] Amendment 4 entry retain, scope expansion = Wave 2 별 CFP carrier 분리 ADR-064 §결정 1 unitary 정합)"`
- 약화 방향 영역 0건 (D1.A-D / D2-D7 + Amendment 1-4 본문 의미 변경 0, codeforge 강제 영역 축소 0, mechanical_enforcement_actions[] Amendment 4 entry retain)

**A7. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-963 Codex TP#4 deferred scope closure (active amendment ratchet 강화 방향)
- 적용 영역 = D1.A-D 4 mandatory field × {proactive 강제, reactive best-effort 가이드} 2-column scope (full-scope, 단일 field 한정 아님)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A8. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 5 자체 = ADR-081 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1003) = ADR-052 Amendment 9 + ADR-070 Amendment 5 + ADR-081 Amendment 5 + registry entry description patch + playbook §3.10 reactive variant codify = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests 무변경) doc-only fast-path 단일 PR 적격.

### 결과 (Amendment 5)

- D1.A-D 4 mandatory field 적용 scope 표 본문 codify (proactive 강제 + reactive best-effort 가이드 2-column) — A1 SSOT
- reactive 영역 4-anchor best-effort 가이드 본문 명시 (사용자 ad-hoc invocation 시 4 field 채택 권장, codeforge 강제 0 invariant 보존) — A2 SSOT
- reactive 영역 mechanical lint scope = Wave 2 carrier 분리 (ADR-064 §결정 1 unitary, mechanical_enforcement_actions[] Amendment 4 entry retain) — A3 SSOT
- D1.A-D / D2-D7 + Amendment 1-4 본문 의미 변경 0건 (sub-section append 패턴) — A4 SSOT
- ADR-081 §D5 declaration-only retain precedent chain 6번째 instance — A5 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A — permanent strengthening) — A6 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A7 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 5 자체) — A8 SSOT

### 거절된 대안 (Amendment 5)

- (Amendment 5-A) **reactive 영역 D1.A-D codeforge 강제 적용** (사용자 책임 영역 invariant 폐기) — ADR-022 Deprecated default + ADR-070 D1 L110 `사용자 책임 영역 (적용 외)` invariant 위배. codex:rescue subagent 자체 = codex@openai-codex plugin runtime 영역, codeforge 강제 권한 외. 사용자 책임 영역 retain + best-effort 가이드 anchor 강화 채택 (ADR-064 §결정 7 top-down ratchet 정합 — 약화 방향 = 사용자 책임 영역 폐기, 차단).
- (Amendment 5-B) **reactive 영역 mechanical lint inline 본 Amendment 5** (Wave 1 + Wave 2 단일 CFP 통합) — ADR-064 §결정 1 (CFP scope unitary) 위배. Wave 1 declarative + Wave 2 mechanical 별 CFP 분리 채택 (CFP-963 Phase 1+2 패턴 답습).
- (Amendment 5-C) **reactive 영역 normative anchor 자체 부재 invariant 보존** (D1.A-D 적용 scope = proactive 한정, reactive 영역 anchor 도입 0) — Codex TP#4 CX-963 deferred scope closure 책무 부재 → CFP-963 retro deferred scope 영구 미해소 risk. best-effort 가이드 anchor (사용자 자율 선택, codeforge 강제 0) 채택 = ADR-064 ratchet 강화 방향 + 사용자 책임 영역 invariant 보존 양립.
- (Amendment 5-D) **D1.A-D 신규 5번째 field (예: D1.E reactive_authorization_token) 추가** — D1.A-D 4 field 의미 변경 0건 invariant 위배. reactive 영역 normative anchor 강화 = D1.A-D 4 field 의 적용 scope codify (proactive 강제 + reactive best-effort) only, 신규 field 도입 0 (CFP-966 lesson "신규 unique drift value 회피" 정합). 4-field exhaustive retain.
- (Amendment 5-E) **ADR-052 본문 또는 ADR-070 본문 inline reactive boilerplate scope** (ADR-081 Amendment 5 회피) — 영역 type mismatch. ADR-081 = boilerplate composition SSOT (D1.A-D 4 mandatory field), ADR-052 = touchpoint behavior SSOT (proactive 채널 한정), ADR-070 = verify-before-trust pattern SSOT (substitution scope + sandbox boundary). 3 ADR normative anchor 분리 정합 — ADR-081 Amendment 5 본문 SSOT (reactive 영역 boilerplate field 채택) + ADR-052 Amendment 9 + ADR-070 Amendment 5 = cross-ref-only 채택.

## Amendment 6 (CFP-1244, 2026-05-22 KST)

### Context (Amendment 6)

본 ADR-081 의 §결정 D1.A-D 4 mandatory boilerplate field 는 Codex worker spawn prompt 본문 **안** 의무 선언 영역 (어떤 정보가 prompt 에 첨부되어야 하는가) 을 codify 한다. 그러나 그 composed prompt 를 **어떤 invocation 형식으로 Codex CLI 에 전달하는가** (dispatch invocation 영역) 의 normative anchor 는 부재했다 — playbook §3.10 dispatch 패턴이 도덕적 강제로 SSOT 역할을 수행 중.

[verified] CFP-1187 운영 phase Epic single autonomous session evidence — Codex CLI v0.125.0 가 `codex exec` 로 invoke 될 때 prompt 를 stdin 으로 직접 pipe 하면 sandbox 안 TTY 부재 → 0-byte stall (>5min). S4/S5 early stall → substitution path activate. **file-redirect** invocation `codex exec --sandbox read-only < <promptfile>` (composed worker prompt 를 file 로 write 후 stdin redirect) 는 stall 을 회피하고 genuine dual-perspective review 산출 — S5/S6/S7 file-redirect 성공. 추가로 long synchronous Codex wait 가 Orchestrator/agent stream idle-timeout risk 보유 — CFP-1187 S7 ArchitectPL stream timeout after 40 tool_uses → redo evidence.

본 Amendment 6 = **Codex worker dispatch file-redirect mandate** (§결정 D8 신설). D1.A-D 4 mandatory boilerplate field 의미 변경 0건 — dispatch invocation 영역이지 prompt field 신설 아님 (D1.A-D 4-field exhaustive retain, Amendment 5-D 거절 대안 정합). D1-D7 본문 의미 변경 0건 — §결정 D8 sub-section append only.

### 결정 (Amendment 6)

**A1. §결정 D8 — Codex worker dispatch file-redirect mandate 신설**

codeforge Orchestrator/lane 이 Codex CLI worker check 를 invoke 할 때 (proactive 6 touchpoint dispatch — ADR-052 D2 + reactive `codex:rescue` best-effort 가이드 anchor — Amendment 5 A2):

1. **file-redirect invocation 의무** — composed worker prompt (D1.A-D 4 mandatory boilerplate field 포함) 를 file 로 write 후 file-redirect 형식 `codex exec --sandbox read-only < <promptfile>` 로 invoke. direct stdin-pipe (prompt 를 stdin 으로 직접 pipe) / inline-arg invocation 금지 — TTY 부재 sandbox 안 0-byte stall (>5min) systemic 원인 (CFP-1187 S4/S5 early stall evidence).
2. **result-via-file 수신** — Codex worker 결과는 output file 경유 수신. Orchestrator 는 Codex stream 을 bounded window 초과 synchronous block-wait 금지 — bounded window 초과 시 다음 step 진행 후 result file pickup. long synchronous Codex wait 가 Orchestrator/agent stream idle-timeout 유발 risk (CFP-1187 S7 ArchitectPL stream timeout after 40 tool_uses → redo evidence) 차단.
3. **substitution path 정합** — file-redirect invocation 후에도 stall / stream idle-timeout 발생 시 ADR-052 Amendment 8 substitution path 3-enum (`fallback_skip_with_marker`) + Story §10 marker `[codex-sandbox-fallback: <fail-mode>]` 진입 (ADR-052 Amendment 12 가 fail-mode enum 7번째 value `dispatch_stall_or_stream_timeout` 신설 — cross-ref).

본 §결정 D8 = dispatch invocation 영역 normative anchor. D1.A-D 4 mandatory boilerplate field (prompt 본문 안 의무 선언 영역) 와 disjoint axis — D1 = prompt content 영역, D8 = prompt 전달 invocation 영역.

**A2. D1.A-D 4 mandatory boilerplate field 무변경 (신규 field 도입 0)**

§결정 D8 = dispatch invocation 형식 (file-redirect + result-via-file + synchronous block-wait 금지) — Codex worker spawn prompt 안 mandatory field 가 아니다. D1.A (dogfood-out Story path) / D1.B (current_lane / phase) / D1.C (sandbox_outside_paths) / D1.D (`network_scope: <4-tier enum>`) 4-field exhaustive retain (Amendment 5-D 거절 대안 "신규 5번째 field 추가" 정합 — 4-field 의미 변경 0).

**A3. ADR-052 Amendment 12 cross-ref binding (fail-mode enum 7-set)**

본 Amendment 6 carrier Story (CFP-1244) = ADR-081 Amendment 6 (dispatch SSOT) + ADR-052 Amendment 12 (fail-mode enum 6 → 7 확장 — dispatch-stall / stream-idle-timeout fail-mode + ADR-081 Amendment 6 cross-ref) paired. dispatch invocation mandate SSOT = 본 ADR-081 §결정 D8 (ADR-052 Amendment 12 는 cross-ref-only, 본문 중복 codify 0).

**A4. ADR-081 §D5 declaration-only retain precedent chain 7번째 instance**

`mechanical_enforcement_actions[]` = Amendment 4 의 `codex-network-scope-presence` entry retain (변경 0건). dispatch file-redirect invocation 의 mechanical lint (예: dispatch 발화 안 `< <promptfile>` 형식 presence-grep) = 별 follow-up CFP carrier (Wave 2, ADR-064 §결정 1 unitary). 본 Amendment 6 = declaration-only normative anchor only — ADR-070 §D5 → ADR-082 §결정 6 → ADR-081 §D5/§D6.e → ADR-070 Amd 5 → ADR-081 Amd 5 declaration-only retain precedent chain 7번째 instance.

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향 (ratchet 강화):

- `is_transitional: false` 본 ADR 유지 (permanent governance — Codex worker dispatch file-redirect mandate = Codex CLI invocation 영구 invariant, dispatch reliability hardening)
- `sunset_justification: "ratchet 강화 방향 (Codex worker dispatch reliability hardening — file-redirect invocation 형식 의무 + result-via-file + synchronous block-wait 금지 codify, dispatch invocation 영역 신규 normative anchor §결정 D8). 약화 영역 0건 (D1.A-D 4 mandatory boilerplate field 무변경, D1-D7 본문 의미 변경 0, scope 축소 0, prompt field 신설 0 — dispatch invocation 영역 additive). ADR-058 §결정 5 + ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."`
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (dispatch file-redirect mandate 축소 또는 invocation 의무 약화) 에만 발효 → 본 Amendment 는 면제

**A6. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-1187 운영 phase Epic S4/S5/S6/S7 dispatch stall + stream timeout evidence 누적 후 즉시 (active amendment ratchet 강화 방향)
- 적용 영역 = proactive 6 touchpoint dispatch + reactive `codex:rescue` 채널 모두 (full-scope — Codex CLI worker check invocation 전 영역)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A7. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 6 자체 = ADR-081 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1244) = ADR-081 Amendment 6 + ADR-052 Amendment 12 + playbook §3.10 patch + CLAUDE.md cross-ref = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests/workflow 무변경) doc-only fast-path 단일 PR 적격.

**A8. D1-D7 본문 의미 변경 없음 + Amendment 1-5 본문 의미 변경 없음**

기존 §결정 D1 (3 mandatory boilerplate 영역) / D2 (verify-before-trust scope 5 sub-scope) / D3 (3-lane partition) / D4 (ADR-052/070 본문 SSOT 보존) / D5 (declaration-only retain) / D6 (severity calibration rubric) / D7 (digest-parse self-verification + grading rubric) + Amendment 1-5 본문 의미 변경 없음. 본 Amendment 6 = §결정 D8 (dispatch invocation 영역) sub-section append only — sub-section append 패턴 (Amendment 1-5 패턴 정합).

### 결과 (Amendment 6)

- §결정 D8 신설 — Codex worker dispatch file-redirect mandate (`codex exec --sandbox read-only < <promptfile>` invocation 의무 + result-via-file 수신 + synchronous block-wait 금지) — A1 SSOT
- D1.A-D 4 mandatory boilerplate field 무변경 (dispatch invocation 영역, 신규 field 도입 0) — A2 SSOT
- ADR-070 Amendment 7 + ADR-052 Amendment 12 cross-ref binding (fail-mode enum 7 → 8 확장, dispatch SSOT = 본 ADR-081 §결정 D8) — A3 SSOT
- ADR-081 §D5 declaration-only retain precedent chain 7번째 instance — A4 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification additive ratchet 강화 — dispatch reliability hardening) — A5 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A6 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 6 자체) — A7 SSOT
- D1-D7 + Amendment 1-5 본문 의미 변경 0건 (sub-section append 패턴) — A8 SSOT

### 거절된 대안 (Amendment 6)

- (Amendment 6-A) **direct stdin-pipe invocation retain (file-redirect 의무 미codify)** — CFP-1187 S4/S5 early stall evidence (TTY 부재 sandbox 안 0-byte stall >5min) — direct stdin-pipe = systemic stall 원인. file-redirect invocation `< <promptfile>` 의무 codify 채택 (S5/S6/S7 성공 evidence).
- (Amendment 6-B) **D1.A-D 5번째 mandatory field (예: D1.E `dispatch_form`) 로 dispatch 형식 codify** — D1.A-D 4-field 의미 변경 0건 invariant 위배 (Amendment 5-D 거절 대안 "신규 5번째 field 추가" 정합). dispatch invocation 형식 = prompt 본문 안 field 가 아니라 invocation 영역 — §결정 D8 disjoint sub-section append 채택 (D1 = prompt content axis, D8 = invocation axis).
- (Amendment 6-C) **synchronous block-wait retain (Codex stream 완료까지 대기)** — CFP-1187 S7 ArchitectPL stream idle-timeout after 40 tool_uses → redo evidence. long synchronous Codex wait = Orchestrator/agent stream idle-timeout risk. result-via-file + bounded window 초과 시 다음 step 진행 후 result file pickup 채택.
- (Amendment 6-D) **dispatch file-redirect mandate 를 ADR-052 본문 inline** (ADR-081 §결정 D8 회피) — 영역 type mismatch. ADR-052 = touchpoint behavior SSOT (dispatch 발동 시점 / 결과 처리), ADR-081 = Codex worker prompt boilerplate + invocation SSOT. dispatch invocation 형식 = prompt composition 영역 자매 (ADR-081 §결정 D1 prompt content 의 invocation 짝). ADR-081 §결정 D8 SSOT + ADR-052 Amendment 12 cross-ref-only 채택 (Amendment 6/7/8 cross-ref-only 패턴 정합).
- (Amendment 6-E) **dispatch file-redirect invocation mechanical lint inline 본 Amendment 6** (Wave 1 + Wave 2 단일 CFP 통합) — ADR-064 §결정 1 (CFP scope unitary) 위배. Wave 1 declarative (본 §결정 D8) + Wave 2 mechanical (dispatch 발화 안 `< <promptfile>` presence-grep lint) 별 CFP 분리 채택 — ADR-081 §D5 declaration-only retain precedent 정합.

## 결과

- Codex worker spawn prompt 안 3 mandatory boilerplate 영역 (dogfood-out Story path / lane stage / sandbox boundary) normative anchor SSOT 신설 — D1 SSOT
- verify-before-trust scope 5 sub-scope (file / dir / cross-repo / grep count active vs historical / ADR §결정 번호) 분리 normative anchor — D2 SSOT
- 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style + history) disjoint scope normative anchor — D3 SSOT
- ADR-052 / ADR-070 본문 정책 SSOT 보존 invariant (의미 변경 0건) — D4 SSOT
- evidence-enforceable framework entry append 면제 (declaration-only retain, ADR-070 §D5 precedent) — D5 SSOT
- ADR-052 Amendment 6 sub-section append (본 ADR 신규 영역 cross-ref 1 paragraph) — ADR-052 본문 patch (의미 변경 0)
- CLAUDE.md L170 blockquote cross-ref 1 줄 추가 (line-cap 320 invariant 정합)
- playbook §3.10 anchor 본문 cross-ref 1 줄 추가 (boilerplate SSOT anchor)
- ADR-RESERVATION row 81 append (active 직접, ADR-079/080 precedent 정합)

## Amendment 7 (CFP-1286, 2026-05-23 KST)

**ADR-070 Amendment 8 cross-ref — fail-mode enum 8 → 9 확장, 9번째 value `codex_truncated_no_verdict` 신설. 본 ADR-081 fail-mode reference 표기 9-enum 동기 정정.**

### Context (Amendment 7)

CFP-604 Phase 2 CodeReview Iter 1 evidence — Codex worker 가 §결정 D8 file-redirect dispatch (`codex exec --sandbox read-only < <promptfile>`) 정상 invocation 후 sandbox + Windows PowerShell `[Console]::OutputEncoding` policy reject + 대용량 artifact (~46KB) processing 누적 → reasoning budget 소진 → output 안 verdict analysis 부재 (file content dump + git diff help dump 만 stdout). `network_scope_actual: offline` (file-redirect 정상). 기존 8 fail-mode value 어디에도 mapping 불가 — post-invocation reasoning-exhausted path 의 disjoint sub-domain (§D8 file-redirect ↔ stream-stall ↔ reasoning-exhausted 3 disjoint failure mode).

### 결정 (Amendment 7)

**A1. ADR-070 Amendment 8 cross-ref** — fail-mode 본문 SSOT = ADR-070 §결정 D1 expansion (Amendment 8, 9번째 value `codex_truncated_no_verdict`). 본 ADR-081 = cross-ref-only (Amendment 1-6 cross-ref / single-mandate body patch pattern 정합).

**A2. fail-mode 9-enum 표기 동기 정정** — 본 ADR-081 안 fail-mode reference 표기 `fail-mode 8-enum` → `fail-mode 9-enum` 전수 replace (line 525 §D8 표 + line 530/532 본문). 동시에 ADR-052 Amendment 13 §A3 cross-ref 표 9-enum 동기 정정.

**A3. §결정 D8 file-redirect dispatch 후속 영역 disjoint sub-domain 표기** — file-redirect (Amendment 6 §D8) = stall 1차 회피층. file-redirect 적용 후에도 reasoning budget 소진 path 잔존 가능 → 신규 fail-mode `codex_truncated_no_verdict` value 가 그 sub-domain cover. disjoint 3 단계: (i) file-redirect / (ii) stream-stall (Amendment 6 cross-ref CFP-1244, `dispatch_stall_or_stream_timeout`) / (iii) reasoning-exhausted (본 Amendment 7 cross-ref CFP-1286, `codex_truncated_no_verdict`).

**A4. ratchet 정합 + declaration-only retain**

closed-enum expansion (8 → 9, additive, 정보 손실 0, 기존 8 value 의미 변경 0) = strengthening. D1.A-D 4 mandatory boilerplate field 무변경, D1-D8 본문 의미 변경 0건. `mechanical_enforcement_actions[]=[]` retain (§D5 declaration-only precedent chain). is_transitional: false (permanent), sunset_justification N/A (강화 방향, scope 축소 0).

**A5. doc-only fast-path (ADR-054 §결정 1)**

본 Amendment 7 = ADR-081 본문 patch (frontmatter amendments[] row append + sub-section append + line 525/530/532 fail-mode reference 표기 정정) — doc-only fast-path 적격. carrier Story CFP-1286 = ADR-070 Amendment 8 + ADR-052 Amendment 13 + 본 ADR-081 Amendment 7 = 단일 PR (ADR-070/052/081 trio Amendment + plugin.json + CHANGELOG + marketplace sync).

### 결과 (Amendment 7)

- ADR-070 Amendment 8 cross-ref (fail-mode 본문 SSOT 위임) — A1 SSOT
- 본 ADR-081 fail-mode 8-enum → 9-enum 전수 표기 정정 — A2 SSOT
- file-redirect ↔ stream-stall ↔ reasoning-exhausted 3 disjoint failure mode sub-domain 정합 — A3 SSOT
- ratchet 강화 방향 + declaration-only retain precedent chain (§D5) — A4 SSOT
- doc-only fast-path 영역 정합 — A5 SSOT

## Amendment 8 (CFP-1383, 2026-05-24 KST)

**신규 §결정 D9 (Codex worker dispatch prompt body origin/main fetch directive mandate) append — working tree file 우회 + stale local checkout state 회피 normative anchor. CFP-1333 5/5 FP + CFP-1384 5/5 TP closing-the-loop empirical validation evidence carrier.**

### Context (Amendment 8)

CFP-1333 §9.1 DesignReviewPL verdict block 의 Codex worker **5/5 FALSE POSITIVE** evidence — Codex worker 가 wrapper plugin-codeforge local working tree HEAD `bfc4806` (origin/main `d24ab28` 보다 **5 commits behind**) 에서 direct Read 수행, CFP-1302 array form migration (PR #1311 merged) + CFP-1319 ADR-073 Amendment 7 (merged) state 미인지. 5 finding 모두 actual ground truth (origin/main HEAD) 와 mismatch — `codex_severity_inflation=5`, `codex_false_positive_tally=5`.

PL inline_orchestrator_verify dual-source 가 5 FP 모두 reject 했으나, Codex worker 자체의 **fetch directive precision** 가 stale local state 우회 logic 부재 — ADR-073 Amendment 7 `stale_local_main_checkout` 의 **3rd-order reproduction** (Orchestrator pre-Read 1st + wrapper main HEAD same-session drift 2nd + Codex external verifier own stale 3rd).

**Disjoint outcome evidence (CFP-1333 5/5 FP vs CodeReview 0 FP vs CFP-1384 5/5 TP)**:

| Story | Codex worker outcome | 결정 factor |
|---|---|---|
| CFP-1333 §9.1 (DesignReview lane) | **5/5 FALSE POSITIVE** | working tree HEAD `bfc4806` direct Read, 5 commits behind |
| CFP-1333 Phase 2 (CodeReview lane) | **0 FP convergent** | Phase 2 PR head `ef45ef2` direct cover |
| CFP-1384 (DesignReview lane iter 1) | **5/5 TRUE POSITIVE** | prompt body 안 `git show origin/main:docs/adr/ADR-073-...md` verbatim file content 첨부 |

동일 `dispatch_mode: file-redirect` (Amendment 6 §D8) + 동일 `network_scope: repo-fetch-only` (Amendment 4 §D1.D) 임에도 outcome disjoint — 결정 factor = **prompt body fetch directive precision** (verbatim file content vs path reference). CFP-1384 = 본 Amendment 8 mitigation 가설 의 closing-the-loop empirical validation (5/5 TP outcome).

### 결정 (Amendment 8)

**A1. §결정 D9 — Codex worker dispatch prompt body origin/main fetch directive mandate 신설**

Codex worker spawn 시 ProactiveCheckPacket `artifacts` 필드 + prompt body 안 `[ORIGIN-MAIN-DIRECTIVE]` block 의무:

```
[ORIGIN-MAIN-DIRECTIVE]
ground_truth_source: origin/main
verbatim_command_pattern: git show origin/main:<path>
working_tree_avoidance: true
sandbox_pre_fetch:
  - cd <repo_root> && git fetch origin main
```

운영적 정의:

- **ground_truth_source** = `origin/main` (own-repo origin/main HEAD) — fixed value 의무
- **verbatim_command_pattern** = `git show origin/main:<path>` (working tree file 우회) — Codex worker 가 file content 첨부 시 사용 명시 의무
- **working_tree_avoidance** = `true` (working tree file path direct reference 금지)
- **sandbox_pre_fetch** = bash trampoline 안 `git fetch origin main` 선행 (network_scope `repo-fetch-only` 이상 영역 의무, `offline` 영역 N/A)

own-repo origin/main fetch directive 한정 — cross-repo state 영역 분리:

| 영역 | ground truth source | 첨부 방법 |
|---|---|---|
| own-repo file | `origin/main` (§결정 D9 신설) | `git show origin/main:<path>` direct fetch (working tree 우회) |
| cross-repo file | D1.C `sandbox_outside_paths` 영역 | Orchestrator 가 verbatim 첨부 (`mcp__github__get_file_contents` 또는 `git fetch origin <repo>` + `git show`) |
| external resource (HTTP) | D1.D `network_scope: web-fetch` 영역 | substitution path activate (ADR-052 Amendment 8 3-enum) |

fallback path (directive 미적용 시) — audit trail marker 의무:

```
[origin-main-directive-fallback: <reason>]
```

reason enum (closed-set):
- `network_scope_offline` — D1.D `network_scope: offline` declare (`git fetch` 영역 외)
- `legacy_prompt_format` — Amendment 8 발효 이전 형식 (advisory grace window, 별 Wave 2 sub-CFP carrier)
- `intentional_working_tree_verify` — working tree HEAD state 자체가 verify 대상 영역 (예: Phase 2 PR diff verify)

reason 부재 + directive 부재 = ADR-070 D3 reject + Story §10 false positive count tally.

**A2. D1.A-D 4 mandatory boilerplate field 무변경 (신규 field 도입 0)**

§결정 D9 = prompt body directive 영역 (working tree avoidance + sandbox_pre_fetch + verbatim_command_pattern) — Codex worker spawn prompt 안 **mandatory field 가 아니다**. D1.A (dogfood-out Story path) / D1.B (current_lane / phase) / D1.C (sandbox_outside_paths) / D1.D (`network_scope: <4-tier enum>`) 4-field exhaustive retain (Amendment 6-B 거절 대안 "신규 5번째 mandatory field 추가" 정합 — D9 = sub-section append, mandatory field 추가 0).

**A3. 3-axis disjoint preservation (D1 prompt content / D8 invocation / D9 prompt body directive)**

| 축 | scope | normative anchor |
|---|---|---|
| **D1 prompt content axis** | Codex worker spawn prompt 본문 안 4 mandatory boilerplate field (D1.A-D) | §결정 D1 |
| **D8 invocation axis** | Codex CLI worker check 호출 형식 (file-redirect `codex exec --sandbox read-only < <promptfile>` + result-via-file + synchronous block-wait 금지) | §결정 D8 (Amendment 6) |
| **D9 prompt body directive axis (본 Amendment 8 신설)** | Codex worker prompt body 안 `git show origin/main:<path>` direct fetch instruction 영역 (working tree file 우회, stale local checkout state 회피 normative anchor) | §결정 D9 |

D1.A-D 4 mandatory boilerplate field 무변경. D8 dispatch invocation 무변경. D1-D8 본문 의미 변경 0건.

**A4. ADR-081 §D5 declaration-only retain precedent chain 8번째 instance**

`mechanical_enforcement_actions[]` = Amendment 4 의 `codex-network-scope-presence` entry retain (변경 0건). §결정 D9 fetch directive presence-grep mechanical lint (예: dispatch 발화 안 `[ORIGIN-MAIN-DIRECTIVE]` block presence-grep + `verbatim_command_pattern` value match) = 별 follow-up CFP carrier (Wave 2, ADR-064 §결정 1 unitary). 본 Amendment 8 = declaration-only normative anchor only — ADR-070 §D5 → ADR-082 §결정 6 → ADR-081 §D5/§D6.e → ADR-070 Amd 5 → ADR-081 Amd 5 → ADR-081 Amd 6 → ADR-081 Amd 7 → 본 Amd 8 declaration-only retain precedent chain 8번째 instance.

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향 (ratchet 강화):

- `is_transitional: false` 본 ADR 유지 (permanent governance — Codex worker dispatch prompt body origin/main fetch directive mandate = Codex CLI invocation 영구 invariant, ground truth source precision hardening)
- `sunset_justification` = "ratchet 강화 방향 (Codex worker dispatch prompt body origin/main fetch directive normative anchor 신설 — working tree file 우회 + stale local checkout state 회피 invariant codify, prompt body directive 영역 신규 normative anchor §결정 D9). 약화 영역 0건 (D1.A-D 4 mandatory boilerplate field 무변경, D8 dispatch invocation 무변경, D1-D8 본문 의미 변경 0, scope 축소 0, mandatory field 추가 0 — sub-section append additive). CFP-1384 closing-the-loop empirical validation (5/5 TP outcome) evidence 가 ratchet 강화 정당성."
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향 (fetch directive mandate 축소 또는 directive 의무 약화) 에만 발효 → 본 Amendment 는 면제

**A6. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-1333 §9.1 Codex 5/5 FP evidence + CFP-1384 5/5 TP closing-the-loop empirical validation 누적 후 즉시 (active amendment ratchet 강화 방향)
- 적용 영역 = proactive 6 touchpoint dispatch + reactive `codex:rescue` 채널 모두 (full-scope — Codex CLI worker check invocation 전 영역, Amendment 5 §D1 적용 scope 정합)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A7. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 8 자체 = ADR-081 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1383) = ADR-081 Amendment 8 + Story + Change Plan + CLAUDE.md L195 1줄 cross-ref = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests/workflow 무변경) doc-only fast-path 단일 PR 적격.

**A8. D1-D8 본문 의미 변경 없음 + Amendment 1-7 본문 의미 변경 없음**

기존 §결정 D1 (3 mandatory boilerplate 영역) / D2 (verify-before-trust scope 5 sub-scope) / D3 (3-lane partition) / D4 (ADR-052/070 본문 SSOT 보존) / D5 (declaration-only retain) / D6 (severity calibration rubric) / D7 (digest-parse self-verification + grading rubric) / D8 (dispatch file-redirect mandate) + Amendment 1-7 본문 의미 변경 없음. 본 Amendment 8 = §결정 D9 (prompt body directive 영역) sub-section append only — sub-section append 패턴 (Amendment 1-7 패턴 정합).

### 결과 (Amendment 8)

- §결정 D9 신설 — Codex worker dispatch prompt body origin/main fetch directive mandate (`[ORIGIN-MAIN-DIRECTIVE]` block + ground_truth_source: origin/main + verbatim_command_pattern + working_tree_avoidance + sandbox_pre_fetch + fallback marker `[origin-main-directive-fallback]`) — A1 SSOT
- D1.A-D 4 mandatory boilerplate field 무변경 (prompt body directive 영역, 신규 field 도입 0, Amendment 6-B 거절 대안 정합) — A2 SSOT
- 3-axis disjoint preservation (D1 prompt content / D8 invocation / D9 prompt body directive) — A3 SSOT
- ADR-081 §D5 declaration-only retain precedent chain 8번째 instance — A4 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification additive ratchet 강화 — ground truth source precision hardening) — A5 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A6 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 8 자체) — A7 SSOT
- D1-D8 + Amendment 1-7 본문 의미 변경 0건 (sub-section append 패턴) — A8 SSOT

### 거절된 대안 (Amendment 8)

- (Amendment 8-A) **D1.A-D 5번째 mandatory field (예: D1.E `origin_main_fetch_required`) 로 fetch directive codify** — D1.A-D 4-field 의미 변경 0건 invariant 위배 (Amendment 6-B 거절 대안 "신규 5번째 field 추가" 정합). prompt body directive 영역 = prompt 본문 안 field 가 아니라 verbatim content composition 영역 — §결정 D9 disjoint sub-section append 채택 (D1 = prompt content axis, D9 = prompt body directive axis).
- (Amendment 8-B) **origin/main fetch directive 를 ADR-070 §결정 D1 expansion sub-domain 으로 codify** (ADR-081 §결정 D9 회피) — 영역 type mismatch. ADR-070 = verify-before-trust pattern SSOT (외부 worker output ground truth verify, Codex worker output 영역). ADR-081 = Codex worker prompt boilerplate + invocation SSOT (Codex worker spawn-time input prompt 영역). 본 carrier = spawn-time prompt body directive 영역 (Codex worker input 영역) — ADR-081 axis 자연 정합. Amendment 6-D 거절 대안 "dispatch file-redirect mandate 를 ADR-052 본문 inline" 정합.
- (Amendment 8-C) **working tree HEAD direct Read retain (origin/main fetch directive 미codify)** — CFP-1333 §9.1 Codex 5/5 FP evidence (working tree HEAD 5 commits behind state mis-bind) + CFP-1384 5/5 TP closing-the-loop empirical validation. working tree direct Read = systemic stale state risk. `git show origin/main:<path>` direct fetch + working_tree_avoidance: true 의무 채택.
- (Amendment 8-D) **cross-repo file 영역 까지 §결정 D9 scope 확장** (own-repo + cross-repo 통합) — D1.C `sandbox_outside_paths` 영역 + D1.D `network_scope: web-fetch` 영역 두 axis 와 scope overlap. cross-repo file = D1.C verbatim 첨부 영역 (mcp__github__get_file_contents 또는 git fetch origin <repo> + git show), external resource = D1.D substitution path 영역. §결정 D9 scope = own-repo origin/main fetch directive 한정 채택 (3 axis disjoint 보존).
- (Amendment 8-E) **fetch directive presence-grep mechanical lint inline 본 Amendment 8** (Wave 1 + Wave 2 단일 CFP 통합) — ADR-064 §결정 1 (CFP scope unitary) 위배. Wave 1 declarative (본 §결정 D9) + Wave 2 mechanical (dispatch 발화 안 `[ORIGIN-MAIN-DIRECTIVE]` block presence-grep lint + `verbatim_command_pattern` value match + bats fixture + workflow + label entry + evidence-checks-registry entry) 별 CFP 분리 채택 — ADR-081 §D5 declaration-only retain precedent 정합 + CFP-1384 sibling Wave 2 split pattern 답습.

---

## Amendment 9 (CFP-2458, 2026-06-29 KST)

**신규 §결정 D10 (merge-time severity rubric) append — ADR-052 Amendment 15 touchpoint #7 (merge-time adversarial gate) sibling.**

### Context (Amendment 9)

§결정 D6 (Codex worker severity calibration rubric, Amendment 1) 의 ground truth severity 우선순위 (D6.b: primary = DesignReviewPL final verdict / fallback = CodeReviewPL standalone / 양쪽 = higher) 는 **review lane verdict 를 ground truth 로 재사용**한다. 그러나 ADR-052 Amendment 15 touchpoint #7 (merge-time adversarial gate) 는 구현리뷰 PASS + CI gate PASS **이후** (모든 review lane 종료 후) dispatch — 머지 직전 시점엔 review-lane verdict 가 이미 닫혀 ground truth 로 재사용 불가 (review lane 폐쇄). D6 의 severity 우선순위 표가 merge-time 엔 적용 불능 (Story §4.2 ADR-081 Amendment 지적 / FeasibilityAgent H). 본 Amendment 가 merge-time 전용 severity rubric (D10) 을 신설한다.

### D10. merge-time severity rubric (review-lane verdict 닫힌 영역의 ground truth 재정의)

merge-time adversarial gate (touchpoint #7) finding 의 P0/P1/P2 severity 는 review-lane verdict 대신 **merge-block impact** (이 결함이 머지되면 어떤 영향인가) 를 ground truth 축으로 확정.

| severity | merge-time 운영적 정의 (merge-block impact ground truth) | 머지 disposition |
|---|---|---|
| **P0** | 정확성 / 보안 / 데이터 무결성 결함 — 배포 시 incident (런타임 실패 / 데이터 손상 / 보안 노출 / 금융 invariant 위반). | **머지 보류 + FIX 루프 회부** (무조건) |
| **P1** | 요구사항·AC 미충족 또는 설계의도 위반 — diff ↔ Story §1(요구사항) / §3(설계의도) / §5(AC) 불일치 (배포는 되나 약속한 동작 미충족). | **머지 보류 + FIX 루프 회부** (Story §1/§3/§5 대비 falsify 후) |
| **P2** | 스타일 / minor / cosmetic / nice-to-have — 동작·요구사항 영향 없음. | **비차단 — 기록 후 진행** (Orchestrator 진행 판단, P2 진행 주체 = Story §7 사용자 확인 후보) |

#### D10.a — critic severity = `[hypothesis]`, PL 확정 절차

critic 의 P0/P1/P2 발화 자체는 `[hypothesis]` 지위 (ADR-077 §결정 7 정보 무결성 invariant reuse). Orchestrator 확정 절차:

1. **verify-before-trust** (ADR-070 Amendment 9 merge-time scope) — finding evidence(file:line) ground truth Read verify. mismatch → reject (P0 발화여도 머지 보류 trigger 아님, false-positive tally).
2. **D6 bidirectional calibration** (over-rate 금지 + security-relevant under-rate 금지) — Amendment 1 §결정 D6 정합. critic severity > 실제 merge-block impact → down-calibrate / security-relevant under-rate → up-calibrate.
3. **D10 rubric 최종 확정** — verify + calibrate 통과 후 merge-block impact 표로 P0/P1/P2 최종 분류 → disposition 결정.

#### D10.b — boundary-completeness exception merge-time 정합

§결정 D6.c (Codex P0 boundary-completeness × review P1 = over-rate 아님, +1 tier 허용) merge-time 정합 유지 — 단 ground truth = review-lane verdict 대신 merge-block impact. boundary-completeness finding (ADR-068 I-1~I-5) 이 merge-block impact 상 정확성/요구사항 영향이면 P0/P1 retain (down-calibrate 아님).

#### D10.c — D6 review-lane rubric 무손상 (disjoint axis)

- §결정 D6 (review-lane severity calibration, review verdict ground truth) = lane-time (touchpoint #2/#3) 영역 — 무손상 보존.
- §결정 D10 (merge-time severity rubric, merge-block impact ground truth) = merge-time (touchpoint #7) 영역 — 신설.
- 두 rubric disjoint axis (review-lane verdict 재사용 가능 ↔ 닫힘). ground truth source 만 다름, calibration discipline (bidirectional / boundary-completeness exception) 은 공유.

#### D10.d — declaration-only retain

`mechanical_enforcement_actions[]` Amendment 4/8 entry retain — D10 = declaration-only normative anchor (§D5 precedent chain 9번째 instance). merge-time severity mechanical lint = Phase 2 별 carrier 영역 (ADR-064 §결정 1 unitary).

### cross-ref (Amendment 9)

- **ADR-052 Amendment 15** — touchpoint #7 merge-time adversarial gate (severity 결과 처리 = 본 D10 rubric).
- **ADR-039 Amendment 6** — inline whitelist 6번째 entry (merge-time dispatch).
- **ADR-070 Amendment 9** — verify-before-trust merge-time scope + fail-mode disposition (D10.a step 1 cross-ref).

### 거절된 대안 (Amendment 9)

- (Amendment 9-A) **review-lane verdict 를 merge-time 까지 carry-forward 해 D6 재사용** — review lane 종료 후 verdict 는 머지 직전 diff (FIX 반영 후) 와 mismatch 가능 (stale). merge-time 은 새 diff 대상이라 review verdict 재사용 불가. merge-block impact ground truth 축 신설 채택.
- (Amendment 9-B) **merge-time severity 를 P0/P1 2-tier 로 단순화 (P2 제거)** — Story §1 verbatim "P2 는 기록 후 진행 판단" 명시. P2 비차단 tier 보존 (cry-wolf 차단 — P2 자동 차단 시 false-block 양산). 3-tier 채택.
- (Amendment 9-C) **D6 rubric 자체를 merge-time 포함하도록 확장 (D10 신설 회피)** — ground truth source 가 disjoint (review verdict ↔ merge-block impact). D6 표 확장 시 review-lane verdict 우선순위 표가 merge-time 에 적용 불능 (닫힘) → 의미 mismatch. 별 §결정 D10 채택 (D6 무손상).

---

## Amendment 10 (CFP-2464, 2026-06-29 KST)

**신규 §결정 D11 (mutation surviving-mutant severity rubric) + §결정 D12 (mutation prompt payload split).** ADR-052 Amendment 16 touchpoint #8 (mutation peer) sibling cross-ref. Epic CFP-2457 Story B. 2축 신설.

### Context (Amendment 10)

ADR-052 Amendment 16 가 구현리뷰 lane-time mutation peer (touchpoint #8) 를 신설했다. surviving mutant 가 재현된 hollow-gate 로 승격될 때 그 P0/P1/P2 severity 를 무엇으로 정하는가 — review-lane verdict (§결정 D6) 도 merge-block impact (§결정 D10) 도 mutation 영역에 직접 mapping 되지 않는다. mutation 의 severity 축은 **"이 검사연극(hollow-gate)이 방치되면 어떤 실 결함을 못 잡는가"** (hollow-gate 영향) 다 — detector adequacy 의 갭이 어떤 종류의 결함을 통과시키는가. 또 mutation prompt (대상 코드 + 테스트 스위트 + mutant 명세 + baseline) 는 ADR-070 Amendment 8 `codex_truncated_no_verdict` (~46KB artifact reasoning budget 소진) 상시 위험 영역 — payload 분할 전략 필요. 본 Amendment 가 두 gap 을 codify.

### D11. mutation surviving-mutant severity rubric (hollow-gate 영향 ground truth)

재현된 hollow-gate (`hollow_gate_verified`, ADR-070 Amd 10 §결정 D8) 의 P0/P1/P2 severity 는 review-lane verdict 대신 **hollow-gate 영향** (이 검사연극이 방치되면 어떤 실 결함을 못 잡는가) 을 ground truth 축으로 확정.

| severity | mutation 운영적 정의 (hollow-gate 영향 ground truth) | 처리 |
|---|---|---|
| **P0** | 정확성/보안/데이터 무결성 **검증 갭** — 이 게이트가 hollow 라 incident-급 결함(런타임 실패/데이터 손상/보안 노출/금융 invariant 위반)을 못 잡는다 (surviving mutant 가 그 결함 class 를 모사). | **결함 승격 + FIX 루프 회부** (테스트 보강) |
| **P1** | 요구사항·AC·설계의도 **검증 갭** — 이 게이트가 hollow 라 Story §1(요구사항)/§3(설계의도)/§5(AC) 가 약속한 동작을 검증 못한다 (surviving mutant 가 그 동작을 깨도 통과). | **결함 승격 + FIX 루프 회부** (재현된 hollow-gate 한정) |
| **P2** | 스타일/minor/cosmetic 변이 갭 — 동작·요구사항 영향 없는 변이만 살아남음 (nice-to-have 검증 강화). | **비차단 — 기록 후 진행** (cry-wolf 차단, 자동 차단 금지) |

#### D11.a — critic severity = `[hypothesis]`, PL 확정 절차 (Story A D10.a 동형)

critic 의 P0/P1/P2 발화 자체는 `[hypothesis]` (ADR-077 §결정 7 reuse). Orchestrator/PL 확정 절차:

1. **verify-before-trust** (ADR-070 Amendment 10 mutation scope) — surviving-mutant evidence(위치 + baseline/post-mutation + 동작차이) ground truth Read verify. mismatch → reject.
2. **PL/QADev 재현 + equivalent/flaky 배제** (ADR-070 Amd 10 §결정 D8) — `hollow_gate_verified` 통과 시만 severity 부여. `undetermined`(equivalent/flaky 의심) = severity 미부여(불확정 보류).
3. **D6 bidirectional calibration** (over-rate 금지 + security-relevant under-rate 금지) 적용.
4. **D11 rubric 최종 확정** — hollow-gate 영향 표로 P0/P1/P2 분류.

#### D11.b — P2 비차단 (cry-wolf 차단, concept M-5 상속)

P2급 저영향 surviving mutant 는 자동 차단·FIX 승격 금지 (기록 후 진행). 차단·FIX 승격 권한 = P0/P1 + 재현된 hollow-gate 한정. mutation FP 억제 책임은 calibration 표현이 아니라 equivalence 식별 + flaky 격리 구조 전처리 (ADR-070 Amd 10 §결정 D8). Codex = 차단·승인 권한 없는 신호원.

#### D11.c — D6/D10 무손상 (disjoint axis)

- §결정 D6 (review-lane severity, review verdict ground truth) — lane-time review (#2/#3) 영역, 무손상.
- §결정 D10 (merge-time severity, merge-block impact ground truth) — merge-time (#7) 영역, 무손상.
- §결정 D11 (mutation severity, hollow-gate 영향 ground truth) — 구현리뷰 lane-time mutation (#8) 영역, 신설.
- 세 rubric disjoint axis (ground truth source 만 다름: review verdict ↔ merge-block impact ↔ hollow-gate 영향). calibration discipline (bidirectional / boundary-completeness exception / P2 비차단) 공유.

### D12. mutation prompt payload split (codex_truncated 회피 + 전수 금지)

mutation prompt (대상 코드 + 해당 테스트 스위트 + mutant 명세 + baseline GREEN 결과) 는 ADR-070 Amendment 8 `codex_truncated_no_verdict` (~46KB artifact reasoning budget 소진 → verdict 미생산) 상시 위험. 처리:

1. **소수 고가치 단위 분할 dispatch 의무** — mutant 묶음을 작은 고가치 단위로 분할해 dispatch (전수 금지 — concept M-4 비용 N배 폭증, 산업 전원 전수 포기). diff-based (변경 코드 한정) + 소수 고가치 LLM-targeted 변이 (Meta ACH: fewer/realistic/highly-specific).
2. **D8 file-redirect + D1.A-D 4 mandatory field + D2 verbatim 무손상** — payload split 은 dispatch 단위 분할이지 boilerplate field 변경 아님. 각 분할 dispatch 도 `codex exec --sandbox read-only < <promptfile>` (D8) + 4 mandatory field (D1.A-D) + verbatim 첨부 (D2) 정합.
3. **partial 첨부** — 단일 mutant 단위에서도 대상 코드/테스트가 큰 경우 verify 대상 영역 verbatim + 나머지 `[partial: lines NN-NN]` marker (D1.A / ADR-070 D2 정합).

### cross-ref (Amendment 10)

- **ADR-052 Amendment 16** — touchpoint #8 mutation peer (severity 결과 처리 = D11 rubric, payload = D12 split).
- **ADR-070 Amendment 10** — verify-before-trust mutation scope + surviving-mutant disposition (D11.a step 1/2 cross-ref).
- **concept** = `docs/domain-knowledge/concept/mutation-based-hollow-gate-detection.md` (M-4 비용 모델 / M-5 cry-wolf).

### 거절된 대안 (Amendment 10)

- (Amendment 10-A) **D6 또는 D10 rubric 재사용 (D11 신설 회피)** — ground truth source disjoint (review verdict / merge-block impact ↔ hollow-gate 영향). review/merge severity 는 *산출물 결함* 축, mutation 은 *detector 검증 갭* 축. 별 §결정 D11 채택 (D6/D10 무손상).
- (Amendment 10-B) **mutation severity 를 P0/P1 2-tier (P2 제거)** — P2 비차단 보존 = cry-wolf 차단 (P2 자동 차단 시 false-block 양산, concept M-5). 3-tier 채택 (D11.b).
- (Amendment 10-C) **payload split 없이 전수 mutant 단일 prompt dispatch** — `codex_truncated_no_verdict` 상시 + 전수 비용 폭증 (concept M-4). 소수 고가치 분할 채택 (D12).
- (Amendment 10-D) **`undetermined` mutant 에도 severity 부여** — equivalent/flaky 의심에 severity = cry-wolf (충족 불가능 요구). `hollow_gate_verified` 한정 severity 채택 (D11.a step 2).

## Amendment 11 (CFP-2477, 2026-06-30 KST)

**신규 §결정 D13 (Codex worker execution dispatch — 실행형 재리뷰 dispatch 형식) + §결정 D3 3-lane partition execution ground-truth axis 추가.** ADR-070 Amendment 11 (review-lane execution scope + §결정 D9 disposition) sibling. Epic CFP-2476 E1 (Codex 실행형 재리뷰). 2축 신설.

### Context (Amendment 11)

CFP-2477 = 리뷰 lane Codex peer(CodexReviewAgent)를 정적 비평가 → 실행 검증자로 전환한다. 그러나 (1) 현 dispatch `review --wait --focus "<lane prompt>"` 는 [verified: codex-companion.mjs origin install] native reviewer 가 custom focus 를 거부 (`validateNativeReviewRequest` L268-273 throws) = **이미 죽은 경로** (E1 이전부터 lane focus 미동작). (2) §결정 D3 3-lane partition 의 Codex worker scope = "factual citation" 한정이라 실행 검증 결과(exit/stdout)를 담을 axis 가 부재. 본 Amendment 가 execution dispatch 형식 normative anchor + execution ground-truth axis 를 codify.

### A1. §결정 D13 — Codex worker execution dispatch (실행형 재리뷰 dispatch 형식)

1. **dispatch 형식** [verified: codex-companion.mjs origin install]: 실행 검증 dispatch = **`adversarial-review`(read-only 고정 turn, focus 지원, L411) primary / `task --write`(workspace-write toggle, L488) 예외**. 현 `review --focus` 죽은 경로 → 교체 (AC-1). 둘 다 §결정 D8 file-redirect 형식 (`codex exec --sandbox ... < <promptfile>`) 정합 — turn 기반이라 D8 stall 회피층 상속.
2. **실행 주체 = Codex CLI 자체 sandbox** (read-only 기본 / network-off / `.git`·`.codex` write 보호 / OS 격리 macOS Seatbelt·Linux Landlock+Seccomp [source: developers.openai.com/codex/concepts/sandboxing]) — **lane worker(CodexReviewAgent) own-Bash 직접 실행 아님**. CodexReviewAgent Bash allowlist 미확대 (python/pytest 추가 0) — 실행은 Codex sandbox 안. 근거: ADR-001 "읽기·분석·보고만" 표면 충돌 회피 + injection 공격면을 Claude harness 권한으로 안 끌어옴 (OWASP LLM06 최소권한).
3. **write 예외**: fixture/temp/lockfile 쓰는 게이트만 `task --write`(workspace-write) + 명시 예외 declare + `[exec-verify-write-mode: <check>]` marker (게이트 자체 idempotent 책임).
4. **D8/D1.A-D 무손상**: 본 §결정 D13 = dispatch invocation 영역 (D8 file-redirect 가 어느 subcommand 호출하는지 명시) — D1.A-D 4 mandatory boilerplate field 무변경, prompt field 신설 0.

### A2. §결정 D3 3-lane partition execution ground-truth axis 추가

Codex worker scope = factual citation (file:line + verbatim + grep count + ADR §결정 번호 + cross-repo SHA) **∪ execution ground-truth (실행 exit code[primary] + stdout[semantic, body 첨부] = 재현 가능 객관 사실)**. 양축 모두 verify-before-trust scope — 실행 결과 finding = `[hypothesis]` → PL 직접 재실행 falsify 통과 시만 `[verified]` 승격 (ADR-070 Amendment 11 §결정 D9). 정적 인용 axis 와 disjoint (정적 = "코드가 어떻게 보이는가" / execution = "코드가 실제 무엇을 하는가").

### A3. E2/E3 재사용 인터페이스 (execution-dispatch-pattern-v1) + declaration-only retain

- **execution-dispatch-pattern-v1**: §결정 D13 + ADR-070 Amendment 11 §결정 D9 가 함께 codify 하는 실행 dispatch + 신뢰 승격 + disposition = Epic CFP-2476 E2(주장→증거 감사)/E3(정책게이트팩 + FIX ground-truth replay)가 그대로 재사용 (SSOT = concept `execution-based-review-verification.md` X-6 + ADR-070 Amd11 B3).
- **declaration-only retain**: `mechanical_enforcement_actions[]` 변경 0건 (§D5 precedent chain 11번째 instance). ratchet 강화 방향 (execution dispatch 형식 + execution ground-truth axis 신설, D1-D12 무손상, scope 축소 0). ADR-070 Amendment 11 + ADR-044 정합 declare sibling cross-ref.

### 거절된 대안 (Amendment 11)

- (Amendment 11-A) **`review --focus` 죽은 경로 유지 (dispatch 무변경)** — native reviewer 가 custom focus 거부 = 현행 장애 (AC-1). adversarial-review/task 교체 채택.
- (Amendment 11-B) **lane worker own-Bash 직접 실행 (allowlist 에 python/pytest 확대)** — ADR-001 표면 충돌 + injection 공격면을 Claude harness 권한 확대 (LLM06) + Codex sandbox 격리 부재. Codex CLI 자체 sandbox 안 실행 채택 (allowlist 미확대). [load-bearing: discriminating 11종 중 8종 Python 의존/자체 실측 — Python 실행은 Codex sandbox python3 가용이 게이트, CodexReviewAgent allowlist 아님.]
- (Amendment 11-C) **execution ground-truth 를 별 lane partition 신설** — Codex worker scope 의 axis 확장이지 새 lane 아님 (DesignReview/CodeReview partition 무손상). Codex worker factual ∪ execution axis 통합 채택.

## Amendment 12 (CFP-2545, 2026-07-01 KST)

**신규 §결정 D14 (Codex companion 브로커 경로 wall-clock ceiling mandate) append — §결정 D8 file-redirect (0-byte TTY stall 방어층) 이 미포함한 codeforge-owned companion 브로커 경로(`node codex-companion.mjs adversarial-review --wait`) 의 wall-clock process-level hang 방어. dogfood wrapper-self carrier (CFP-2545). ADR-052 Amendment 12 fail-mode enum #8 재사용 + ADR-039 liveness 게이트 Orchestrator 소유 + ADR-119 Amendment 2 fail-open 금지 sibling cross-ref.**

### Context (Amendment 12)

CFP-2545 Orchestrator 실측 진단 — codeforge 소유 실 리뷰 worker 호출부 `plugins/codeforge-review/agents/CodexReviewAgent.md:89` `node "$CMD" adversarial-review --wait "<focus>"` (4 리뷰 lane — 요구사항리뷰·설계·구현·보안 공유 워커) 가 companion 브로커 경로로 codex 를 호출한다. companion `request()` 는 응답 라인 도착/프로세스 종료로만 resolve (turn 완료 대기의 유일 타이머 = final-answer 감지 후 inferred-completion 디바운스뿐, deadline 부재) → 모델·브로커가 final answer 전 stall 시 completion promise 영구 미settle → node·Bash·worker·Orchestrator 순차 **무한 대기**. 4 lane 공유 워커라 worker 1개 stall = 4 lane blast radius. 기록된 재발 사고 = `docs/orchestrator-communication-incidents.md` Iter 4/5 (~2h silent hang).

[verified] §결정 D8 (Amendment 6, file-redirect mandate) 은 `codex exec --sandbox read-only < <promptfile>` invocation 을 대상으로 rationale 을 "TTY 부재 sandbox 0-byte stall (>5min)" 에 앵커한다. 그러나 companion 브로커(`adversarial-review --wait`)는 file-redirect 가 아닌 **별도 dispatcher** 이므로 §D8 의 "file-redirect 의무" 문구가 문법적으로 도달하지 못하고, §D8 이 다루는 fail-mode 는 0-byte TTY stall 이지 **wall-clock process-level hang** 이 아니다 (disjoint sub-failure-mode). 즉 규정(§D8)↔실 호출 경로(companion 브로커) divergence — companion 경로 wall-clock 상한이 미배선 (review plugin 전체 grep: timeout/wall-clock/max-wait 0건, origin/main 실측). #763 liveness carrier (CFP-750/751) 3 후보 중 어느 것도 실 리뷰 worker companion 호출부에 배선되지 않음 → 본 Amendment 12 = §D8 lineage + #763 liveness 두 선행 arc 의 미완 gap 연장.

본 Amendment 12 = **Codex companion 브로커 경로 wall-clock ceiling mandate** (§결정 D14 신설). D1.A-D 4 mandatory boilerplate field 의미 변경 0건 — dispatch invocation 영역(D8 axis)의 companion sub-domain 확장이지 prompt field 신설 아님. D1-D13 본문 의미 변경 0건 — §결정 D14 sub-section append only.

### 결정 (Amendment 12)

**A1. §결정 D14 — Codex companion 브로커 경로 wall-clock ceiling mandate 신설**

codeforge Orchestrator/lane 이 Codex CLI worker check 를 **companion 브로커 경로**(`node codex-companion.mjs adversarial-review --wait` / `task --write` / 등가 `--wait` 동기 block) 로 invoke 할 때:

1. **wall-clock ceiling 의무** — companion 호출부에 wall-clock 상한 `timeout <N> --kill-after=<K> node <companion.mjs> adversarial-review --wait ...` 배선. companion `request()` 는 deadline 부재라 호출부 `timeout` 이 companion 프로세스를 **외부에서 종료하는 유일 안전판**. `--kill-after=<K>` (TERM 후 KILL) 로 detached app-server 자식(node) 좀비 방지. N = 전역 default (env `CODEX_REVIEW_TIMEOUT_SEC`, 제안 300초) + lane override (`CODEX_REVIEW_TIMEOUT_SEC_<LANE>`) 허용, consumer overlay 재정의 시 무한대기 방지 목적 파괴 방지 위해 상한 hardcap 권고. **암묵 무한 금지 — 상한은 하드코딩/env/문서 중 하나로 명시적 특정 가능해야 함.**

2. **stall → 기존 fail-mode #8 marker 재사용** — deadline 초과 (GNU `timeout` exit 124) 시 substitution path `fallback_skip_with_marker` 진입 + Story §10 marker `[codex-sandbox-fallback: dispatch_stall_or_stream_timeout]` (fail-mode enum #8, ADR-070 Amendment 7 / ADR-052 Amendment 12). **신규 9번째 enum value 발의 안 함** — fail-mode enum #8 trigger 정의를 "codex exec TTY 0-byte stall" + "companion `adversarial-review --wait` wall-clock 초과" 양쪽으로 명시 확장 (companion `--wait` hang = `codex exec` dispatch stall 과 동형 class = 외부 프로세스 무한 대기, closed-set 크기 무변경 → ADR-052/070/081 3 ADR 정정 불요, ADR-064 §결정 1 unique drift value 회피).

3. **fail-open 금지 (ADR-119 §결정10 outcome-honesty 상속)** — fallback 종료가 게이트 verdict 를 **PASS 로 자동 승격하지 않는다.** exit 124 → verdict = inconclusive/미획득. exit 0 + verdict 필드 부재 = inconclusive (PASS-only-if-explicit: verdict == "PASS" 명시 문자열일 때만 PASS). 부분 stall (4 lane 중 일부) → ANY(inconclusive) → 전체 inconclusive (완료분 기준 전체 PASS 승격 금지). marker emit ≠ PASS 승격 — hollow-gate 재생산 (게이트가 무한 hang 으로 outcome 미측정을 pending 위장) 차단.

4. **Orchestrator liveness 게이트 소유 (ADR-039)** — 호출부 `timeout` (1차 process wall-clock 상한) 을 보조하는 Orchestrator liveness 게이트 (2차 관측 — worker 진행 마커 부재 max-wait 분 초과 → stall 판정·다음 step). 게이트 spawn 주체 = **Orchestrator 고정** — worker(CodexReviewAgent) 자가 liveness 게이트 spawn = "워커는 직접 다른 subagent 스폰 불가"(`plugins/codeforge-review/CLAUDE.md:46`) 위반. **값 순서 정합**: `timeout N < liveness max-wait` (호출부 timeout 이 먼저 터져 marker 를 남기고 게이트가 그 이후를 관측 — 역순이면 게이트가 marker 없이 먼저 fail).

본 §결정 D14 = §결정 D8 dispatch invocation 영역의 companion sub-domain 확장. D8 (`codex exec` file-redirect 0-byte stall) 과 disjoint sub-failure-mode (companion `--wait` wall-clock process hang) — 동일 dispatch-reliability axis.

**A2. D1.A-D 4 mandatory boilerplate field 무변경 (신규 field 도입 0)**

§결정 D14 = companion 경로 wall-clock ceiling (dispatch invocation 영역, D8 axis) — Codex worker spawn prompt 안 mandatory field 가 아니다. D1.A-D 4-field exhaustive retain (Amendment 6-B 거절 대안 "신규 5번째 mandatory field 추가" 정합 — dispatch invocation 형식은 prompt content field 가 아님).

**A3. fail-mode enum closed-set 크기 무변경 (trigger 정의 의미 확장)**

fail-mode enum #8 `dispatch_stall_or_stream_timeout` 은 이미 존재 (Amendment 6/7 cross-ref, ADR-052 Amendment 12). 본 Amendment 12 = 신규 9번째 value 발의 아님 — enum #8 의 trigger 정의(적용 조건)를 companion `--wait` wall-clock 초과까지 명시 확장. closed-set 크기 8 유지 → ADR-052/070/081 3 ADR fail-mode 표기 정정 불요 (Amendment 7 의 8→9 enum expansion 과 disjoint — 본 Amendment 는 enum 확장 아닌 기존 #8 의미 확장).

**A4. ADR-081 §D5 declaration-only retain precedent chain 12번째 instance**

`mechanical_enforcement_actions[]` = Amendment 4 (`codex-network-scope-presence`) + Amendment 8 (`codex-origin-main-directive-check`) entry retain (변경 0건) + 본 Amendment 12 신설 3번째 entry `codex-companion-timeout-presence` (deferred-followup, Phase 2 wire — Amendment 4/8 precedent verbatim). companion wall-clock ceiling 의 mechanical lint (dispatch 발화 `timeout <N>` prefix presence-grep + 발화 건수 ≥1 검사) = CFP-2545 Phase 2 carrier. 본 Amendment 12 자체 = declaration-only normative anchor.

**A5. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

본 Amendment = 강화 방향 (ratchet 강화):

- `is_transitional: false` 유지 (permanent governance — companion 브로커 wall-clock ceiling = Codex CLI companion invocation 영구 invariant, dispatch reliability hardening)
- `sunset_justification` = frontmatter entry verbatim (약화 영역 0건: D1.A-D 무변경, D8 file-redirect 무변경, fail-mode enum closed-set 크기 무변경, D1-D13 본문 의미 변경 0, scope 축소 0)
- ADR-058 §결정 5 sunset_justification 의무는 약화 방향에만 발효 → 본 Amendment 면제

**A6. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-2545 요구사항 lane PASS + Orchestrator 실측 진단 (companion 무한 대기 재발 evidence Iter 4/5) 후 즉시 (active amendment ratchet 강화 방향)
- 적용 영역 = codeforge 소유 companion 브로커 호출부 전 (`adversarial-review --wait` / `task --write` / 등가 `--wait` block) — 4 리뷰 lane 공유 워커
- forbid-list 어휘 사용 0 건 self-attest

**A7. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 12 자체 = ADR-081 본문 patch (Amendment row append + sub-section append + frontmatter 3 list append) — doc-only fast-path 적격. carrier Story CFP-2545 (dogfood wrapper-self) = ADR-081 Amendment 12 + orchestrator-playbook §3.10 companion sub-paragraph patch + CodexReviewAgent.md dispatch prefix + (Phase 2) lint script/workflow/bats.

**A8. D1-D13 본문 의미 변경 없음 + Amendment 1-11 본문 의미 변경 없음**

기존 §결정 D1-D13 (D8 dispatch file-redirect / D9 origin-main directive / D13 execution dispatch 포함) + Amendment 1-11 본문 의미 변경 없음. 본 Amendment 12 = §결정 D14 (D8 axis 의 companion sub-domain) sub-section append only — sub-section append 패턴 (Amendment 1-11 패턴 정합).

### 결과 (Amendment 12)

- §결정 D14 신설 — Codex companion 브로커 경로 wall-clock ceiling mandate (`timeout <N> --kill-after=<K>` 배선 의무 + exit 124 → fail-mode #8 marker 재사용 + fail-open 금지 verdict=inconclusive + Orchestrator liveness 게이트 소유, timeout N < liveness max-wait 순서) — A1 SSOT
- D1.A-D 4 mandatory boilerplate field 무변경 (companion wall-clock = D8 axis sub-domain, 신규 field 0) — A2 SSOT
- fail-mode enum closed-set 크기 무변경 (기존 #8 trigger 정의 companion 경로 의미 확장, ADR-052/070/081 3 ADR 정정 불요) — A3 SSOT
- ADR-081 §D5 declaration-only retain precedent chain 12번째 instance + mechanical_enforcement_actions[] 3번째 entry `codex-companion-timeout-presence` (deferred-followup, Phase 2 wire) — A4 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, companion dispatch reliability hardening) — A5 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 어휘 사용 0 건) — A6 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 12 자체) — A7 SSOT
- D1-D13 + Amendment 1-11 본문 의미 변경 0건 (sub-section append 패턴) — A8 SSOT
- ADR-052 Amendment 12 (fail-mode #8 재사용) + ADR-070 (verify-before-trust substitution) + ADR-039 (liveness Orchestrator 소유) + ADR-119 Amendment 2 (fail-open 금지 outcome-honesty) sibling cross-ref

### 거절된 대안 (Amendment 12)

- (Amendment 12-A) **신규 ADR (ADR-14x "codex-companion broker path wall-clock liveness gate") 발의** — ADR-064 §결정 1 (CFP scope unitary, 신규 ADR = full 10-lane 강제) + SSOT 분산 위험. ADR-081 이 이미 companion 경로를 Amendment 11 (§결정 D13) 에서 인용하므로 동일 ADR extension = SSOT 분산 0. Amendment-first 채택 (CFP-2445 ADR-042 Amd17 / CFP-2477 Amendment 11 선례).
- (Amendment 12-B) **fail-mode enum 9번째 value `companion_wait_timeout` 신설** — companion `--wait` wall-clock hang = `codex exec` dispatch stall 과 동형 class (외부 프로세스 무한 대기). 신규 value = ADR-064 §결정 1 unique drift value 회피 위배 + ADR-052/070/081 3 ADR 동기 정정 부담. 기존 #8 `dispatch_stall_or_stream_timeout` trigger 정의 의미 확장 채택 (closed-set 크기 무변경).
- (Amendment 12-C) **2안 — 리뷰 worker 를 `codex exec < promptfile` file-redirect 경로로 전환해 §D8 일원화** — companion job 관리(background/status/native review 파싱, `runAppServerReview`) 통째 상실 → 4 리뷰 lane blast radius 확대 (§2 D-4 증폭). review 커맨드 재작성 = 큰 변경. 1안 (호출부 wall-clock 가드, 최소 변경 codeforge 소유 표면만) 채택 — companion job 관리 보존.
- (Amendment 12-D) **companion wall-clock ceiling mandate 를 ADR-052 본문 inline** (ADR-081 §결정 D14 회피) — 영역 type mismatch. ADR-052 = touchpoint behavior SSOT, ADR-081 = Codex worker prompt boilerplate + invocation SSOT. dispatch invocation 형식 (§D8 axis) = ADR-081 SSOT. ADR-081 §결정 D14 SSOT + ADR-052 Amendment 12 fail-mode #8 cross-ref-only 채택 (Amendment 6-D 패턴 정합).
- (Amendment 12-E) **wall-clock ceiling mechanical lint (dispatch 발화 `timeout <N>` presence-grep) inline 본 Amendment 12** (Wave 1 + Wave 2 단일 통합) — ADR-081 Amd6-E 예고 패턴 정합상 Wave 1 declarative (본 §결정 D14 + playbook + agent md prefix) + Wave 2 mechanical (presence-grep lint script + workflow + bats) 분리. 단 CFP-2545 는 dogfood wrapper-self 라 Wave 1/Wave 2 를 Phase 1 문서 PR + Phase 2 구현 PR 로 분리 (ADR-127 Phase 1/2 PR 분리 무조건) — 별 CFP 분리 아닌 동일 Story Phase 분리 채택 (mechanical lint = Phase 2 carrier).

## 해소 기준

N/A — permanent policy (boilerplate composition + verify-before-trust scope + 3-lane partition = Codex worker 사용 영구 invariant, ADR-070 §D5 precedent 정합).

**ADR-058 §결정 1/2/3 정합**:

| 항목 | 값 |
|---|---|
| `is_transitional` (§결정 1) | `false` (permanent governance) |
| `## 해소 기준` 섹션 본문 (§결정 2) | `N/A — permanent strengthening (6-Story carry-over evidence ratchet 정합 — 1 baseline cluster CFP-770/771 paired + 5 consecutive fp-0 CFP-786/801/792/795/810; 6 units / 7 retro file)` |
| metric (§결정 3) | `codex_false_positive_tally` — Story §10 FIX Ledger row append count |
| who (§결정 3) | Orchestrator (verify-before-trust 단계 / ADR-070 D3 정합) — Story §10 FIX Ledger row append 주체 |
| how (§결정 3) | Story §10 FIX Ledger row 안 `[codex-false-positive]` sub-tag (fix-event-v1 MINOR bump 별 carrier) — `mcp__github__get_file_contents("internal-docs/wrapper/stories/CFP-NNN.md") + Grep "codex-false-positive"` |

ADR-058 §결정 5 (Amendment justification) 발효 영역 부재 — 본 ADR = 신규 ADR, Amendment 영역 아님. 향후 Amendment 시 §결정 5 정합 의무 (sunset_justification ratchet 강화 방향만 amendment 허용, ADR-064 §결정 7 top-down ratchet 정합).

영역 변경 시 (codex@openai-codex plugin sandbox 모델 변경 또는 codex CLI runtime working directory inject 추가) 본 ADR amendment 검토 영역.

## 관련 파일

- [`docs/adr/ADR-052-codex-proactive-check-touchpoints.md`](ADR-052-codex-proactive-check-touchpoints.md) — Amendment 6 sub-section append (cross-ref 1 paragraph)
- [`docs/adr/ADR-070-codex-verify-before-trust.md`](ADR-070-codex-verify-before-trust.md) — D1/D2/D5 cross-ref source
- [`docs/adr/ADR-058-adr-sunset-criteria-mandate.md`](ADR-058-adr-sunset-criteria-mandate.md) — §결정 1/2/3 frontmatter + 해소 기준 + 3-tuple 의무 source
- [`docs/adr/ADR-068-boundary-completeness-invariants.md`](ADR-068-boundary-completeness-invariants.md) — 3-lane partition 표 안 DesignReview 영역 (4 invariants + Amendment 1 I-5)
- [`docs/adr/ADR-073-orchestrator-verify-before-assert.md`](ADR-073-orchestrator-verify-before-assert.md) — verify-before-trust 자매 (Orchestrator self-assertion layer)
- [`docs/adr/ADR-045-story-retro-mandatory-trigger.md`](ADR-045-story-retro-mandatory-trigger.md) — §D-9 cross_story_pattern_adr_trigger forcing function (본 ADR 발의 trace)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §3.10 dispatch prompt template SSOT (boilerplate cross-ref anchor)
- [`CLAUDE.md`](../../CLAUDE.md) — 오케스트레이션 규칙 § "Codex Proactive Check" blockquote SSOT (L170 cross-ref anchor)
- [`docs/adr/ADR-RESERVATION.md`](ADR-RESERVATION.md) — row 81 active 직접 등록
- [`docs/evidence-checks-registry.yaml`](../evidence-checks-registry.yaml) — declaration-only retain 정합 (entry append 면제)
