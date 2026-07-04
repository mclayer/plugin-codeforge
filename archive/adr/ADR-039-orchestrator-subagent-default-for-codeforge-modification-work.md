---
adr_number: 39
title: Orchestrator subagent default for codeforge modification work
date: 2026-05-08
status: Accepted
category: orchestration-discipline
carrier_story: CFP-275
supersedes: null
amends: ADR-009
related_adrs:
  - ADR-009  # wrapper-only decomposition (amends)
  - ADR-025  # stop discipline + Epic-level continuity (motivation)
  - ADR-029  # phase execution visibility (narration interaction)
  - ADR-031  # lane-spawn evidence trail (§14 row append)
  - ADR-035  # codeforge agent teams Epic (subagent semantics)
  - ADR-139  # background-wait liveness gate (Amendment 10 §결정 20 — §결정 19 lead force-resume/TaskStop 개입 축의 정량 게이트화 cross-ref carrier SSOT, spawn-권한 기반 게이트 소유 INV-L4)
related_stories:
  - CFP-275
  - CFP-2521  # Amendment 8 (2026-06-30) — §결정 9 amend, DevPL self-read advisory detection (D3 enforcement slot)
  - CFP-2544  # Amendment 9 — §결정 9 inline-write detect hook slot UNIMPLEMENTED→IMPLEMENTED Wave1 (Write/Edit/MultiEdit 축)
  - CFP-2549  # Amendment 10 — §결정 20 신설 (background subagent spawn liveness = ADR-139 cross-ref, §결정 19 개입 축의 정량 게이트화). §결정 9 slot 미침범 (완료-감지 축 ≠ inline-write-detect 축). ADR-081 Amd13 paired sibling.
related_cfps:
  - CFP-275
  - CFP-134
  - CFP-46
  - CFP-26
  - CFP-2521
  - CFP-2544
  - CFP-2549
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/hotfix-playbook.md
  - docs/change-plans/cfp-275-orchestrator-subagent-default.md
  - docs/domain-knowledge/orchestrator-discipline/spawn-default.md
amendment_log:
  - amendment: 1
    date: 2026-05-17
    summary: §결정 14 신설 (Pre-spawn-pin mandate) — DeveloperPL + 모든 branch-creating subagent 가 새 branch 생성 시 current origin/main HEAD pin 의무 (CFP-699/702/848 3차 누적 stale-base recurrence 차단)
    direction: strengthening
    sunset_justification: N/A (ratchet — closed enumeration 확장만, 약화 0)
  - amendment: 2
    date: 2026-05-24
    carrier_story: CFP-1340
    summary: |
      §결정 15 신설 (Orchestrator-monopoly Story-file handoff inline write — partial rollback). §결정 2 inline whitelist 4-entry 표에 5번째 entry append "Orchestrator-monopoly Story-file handoff inline write" + 4-sub-scope (§9 verdict / §10 FIX Ledger / §14 Lane Evidence / phase transition) + lane agent self-write exclusion 명시. §결정 1 closed enumeration 안 "Story file write §1-§14 어느 섹션이든" → "Story file write §1-§14 (§9/§10/§14/phase 제외 — §결정 15 inline whitelist 5번째 entry scope) 어느 섹션이든" partial rollback delta. §결정 3 mechanism rationale clarification — Orchestrator-owned delegate subagent (기존) + Orchestrator inline (Amendment 2 추가) 양 mechanism 모두 valid. ADR-031 / fix-event-v1 invariant 무변. 사용자 2026-05-17 KST CFP-848 directive verbatim citation ("Orchestrator-monopoly Story-file section (§9/§10/§14/phase) handoff 시 general-purpose editor subagent 위임 reject").
      memory `feedback_orchestrator_monopoly_inline_write` normative 승격 carrier. evidence-grounded — Orchestrator-monopoly Story-file section monopoly 명목 보존 + inline cost (~60-70KB 큰 파일 inline reconstruction) = 올바른 trade-off + ADR-031 §14 Orchestrator self-write monopoly invariant + fix-event-v1 §10 row append Orchestrator monopoly invariant 정합.
    direction: weakening_partial
    sunset_justification: |
      사용자 explicit directive 2026-05-17 KST CFP-848 구현리뷰 handoff 시 general-purpose editor subagent 위임 reject — Orchestrator-monopoly Story-file section (§9/§10/§14/phase) 의 monopoly 명목 보존 + inline cost (~60-70KB 큰 파일 inline reconstruction) = 올바른 trade-off. ADR-058 §결정 5 약화 evidence-gate 통과 (CFP-1149 symmetric ratchet 정합) — partial rollback scope = §결정 1 closed enumeration 'Story file write §1-§14 = subagent spawn 의무' 의 §9/§10/§14/phase 4-sub-scope 만. 나머지 §1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13 lane agent self-write 영역 = §결정 1 유지 (binary always-spawn 보존). ADR-042 Amendment 10 deputy 7→6 precedent 답습 (evidence-gated 약화 carve-out). carrier-preserved scope split: subagent spawn mechanism 자체는 다른 영역 유지 (4-entry inline whitelist 의 5번째 entry append, closed enumeration 확장 패턴 정합).
  - amendment: 3
    date: 2026-05-24
    carrier_story: CFP-1340
    summary: |
      §결정 16 신설 (Autonomous permission UI behavior — destructive-only ask, reversible auto-proceed). destructive closed enum (≥8 항목: git reset --hard / git push --force / file delete rm-rf / branch delete / Issue mutation close-state / label create / workflow yaml 변경 / ADR row append) + 외부 visible (PR create/merge/close/comment to shared main + external notifications) = ask permission preserve. reversible closed enum (≥6 항목: local file Edit / local script run / temp-file mechanics / .claude/settings.local.json edit / git add / branch create / commit / Edit on /docs/**) = auto-proceed (no permission UI reflex prompt). reversibility test 근거 명시 (git reflog / Issue history / branch 복구 가능성). ADR-039 §결정 1 binary always-spawn 무관 (permission UI 차원, mechanism 차원 disjoint axis). 사용자 directive verbatim 2026-05-17 KST CFP-848 ("아 묻지말고 그냥 하라고" / "쓰잘데기 없는 권한 묻지말고 전부 수정하라"). memory `feedback_no_permission_prompts` normative 승격 carrier.
    direction: strengthening
    sunset_justification: null
  - amendment: 4
    date: 2026-05-24
    carrier_story: CFP-1354
    summary: |
      §결정 9 신설 (rate-limit second-order risk 측정 carryover — ADR-109 §결정 8 cross-ref). §결정 2 inline whitelist closed 4-entry enumeration 무변경 (5번째 entry 신설 0 — chief 결정, RefactorAgent pattern 2 권고 정합 retry primitive 위치 = `codeforge:rate-limit-429-mitigation` skill body). 본 carryover entry = ADR-109 in-process 429 mitigation framework SSOT 안 §결정 7 (retry primitive 위치 = skill body) + §결정 8 (telemetry SSOT §14 Lane Evidence marker + KPI dual-tier JSON+JSONL) 으로 측정 영역 흡수.
      Story A (CFP-1354) Phase 1 PR scope. 사용자 발화 verbatim "Server is temporarily limiting requests (not your usage limit)" (Story §1, story-section-1-immutable 강제) 의 in-process axis surgical mitigation framework — Anthropic infra-level temporary throttling 영역 (org tier / service-wide). retry primitive 위치 = skill body 결정 (Orchestrator inline whitelist closed 4-entry invariant 보호 우선, ADR-039 §결정 2 L110 verbatim 정합 — "5번째 카테고리 추가 = ADR-039 amendment 의무. 본 closed enumeration 가 future '429 retry inline allowed' 압박을 차단"). InfraOp D-13 advocacy "ADR-039 5번째 entry 신설" REJECTED (chief 결정).
    direction: strengthening  # rate-limit second-order risk codify (carryover marker + ADR-109 SSOT 신설), §결정 2 4-entry 무변경 (약화 0).
    sunset_justification: |
      §결정 2 inline whitelist closed 4-entry 보존 invariant 정합. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (rate-limit second-order risk codify + ADR-109 신규 SSOT 신설), 약화 0건. carrier_story CFP-1354 = ADR-109 신규 ADR (in-process 429 mitigation framework SSOT, 10 §결정 통합) + ADR-044 Amendment N (parallel_spawn_cap + spawn_stagger_ms + cascade_circuit_breaker 3 field) + ADR-064 §결정 4 Amendment N (surgical exception channel codify) 3 sibling amendment.
  - amendment: 5
    date: 2026-05-24
    carrier_story: CFP-1438
    summary: |
      §결정 17 신설 (Chief author spawn span guideline). chief author monolithic 단일 spawn (15-40min wide drift surface) 패턴 anti-pattern declare + multi-step sequential smaller spawn 권장 (skeleton + body + integration ~5-7min each) — declarative-only Wave 1 (recommendation tier, mechanical enforcement = 별 sub-CFP carrier). 본 amendment = §결정 1 binary always-spawn invariant 무관 (mechanism 차원 disjoint axis) + §결정 2 inline whitelist 4-entry closed enumeration 무변경 invariant 보존. trade-off matrix: ↓ drift surface per spawn (preventive complement to ADR-073 Amd 11 SHA pin + ADR-082 Amd 15 spawn prompt anchor + ADR-073 Amd 12 mid-spawn drift detection + ADR-082 Amd 17 amendment-slot pre-reservation) / ↑ number of spawns / ↑ coordination complexity / ↑ state passing between spawns. 측정 가능 metric (Phase 2 telemetry carrier deferred): spawn time histogram + per-spawn collision count + chief author span KPI.
      Sub-CFP D of CFP-1389 Wave 1 declarative-only carrier — paired sibling of Sub-CFP A CFP-1437 (preventive SHA pin Amd 11/15) + Sub-CFP B CFP-1436 (reactive mid-spawn drift detection Amd 12/16) + Sub-CFP C CFP-1435 (preventive slot reservation strict claim Amd 17) = 4-layer defense forcing function 완결 (preventive SHA + reactive drift + preventive slot + span decomposition recommendation). CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach evidence root cause 한 측 = chief author monolithic span = wide drift window root cause. Sub-CFP A/B/C 가 race detection / claim mechanism complement, 본 Sub-CFP D = root cause 직접 축소 (span 자체 작게).
      ADR-044 Amendment 3 paired carrier dual-binding 같은 CFP-1438 Story 안 2 ADR paired Amendment axis disjoint complement 2-set ADR-064 §결정 1 CFP scope unitary 정합 (본 ADR-039 = orchestrator-side spawn span guideline body / ADR-044 = team-spec yaml multi-step lifecycle pattern). META-self-applied (본 CFP-1438 chief author spawn 자체 = guideline 첫 적용 사례 — skeleton + body + integration 3-step 권장 sequentially demonstrate).
    direction: strengthening
    sunset_justification: |
      §결정 1 binary always-spawn invariant 무변경 + §결정 2 inline whitelist 4-entry closed enumeration 무변경 (둘 다 보존, recommendation tier 만 추가). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (chief author span guideline 추가, recommendation tier), 약화 0건. carrier_story CFP-1438 = ADR-039 Amendment 5 + ADR-044 Amendment 3 paired sibling amendment 2-set (axis disjoint).
  - amendment: 6
    date: 2026-06-29
    carrier_story: CFP-2458
    summary: |
      §결정 18 신설 (Inline whitelist **6번째 entry** — merge-time Codex adversarial gate dispatch). §결정 2 inline whitelist 표 (4 original + Amendment 2 §결정 15 entry 5 = 5-entry) 에 6번째 entry append. §결정 15 line 315 "6번째 inline whitelist entry 추가 = 별도 ADR Amendment 의무 (ADR-058 §결정 5 evidence-gate)" 충족 carrier. **H1 critical (게이트 연극화 차단)**: merge-time adversarial gate (ADR-052 Amendment 15 touchpoint #7) 의 Codex dispatch 는 **Orchestrator top-level inline 전용** — sub-agent/PL 을 게이트 owner 로 두면 ADR-039 platform-inherent 재귀 가드("subagent → Agent tool 호출 금지" L474)로 Codex spawn 이 silent fallback skip (`subagent_recursion_blocked` fail-mode, ADR-070 Amendment 6) → 게이트 무발동 = 연극화. 본 entry = mechanism 차원 (inline vs spawn) — dispatch 자체는 read-only adversarial check (verify-before-trust 무조건 적용, ADR-070 Amendment 9) 이라 §결정 1 binary always-spawn 의 "수정 작업" 정의 (file edit / GitHub state change) 와 disjoint axis. §결정 1 binary always-spawn invariant 무변경 (수정 작업 영역 spawn 의무 유지) + Amendment 2 entry 5 (Story-file handoff) 무변경. 6번째 entry exhaustiveness declare — 7번째 entry = 별도 ADR Amendment. ADR-039 Amendment 4 (CFP-1354) 의 "ADR-039 5번째 entry 신설 REJECTED (retry primitive = skill body)" 와 disjoint — 본 entry = merge-time Codex dispatch (재귀 가드 회피 mechanism 차원), retry primitive 영역 아님. is_transitional false, sunset_justification N/A (강화 방향 closed enumeration 확장 additive, 약화 0). doc-only fast-path (ADR-054 §결정 1, ADR-052 Amd 15 + ADR-070 Amd 9 + ADR-081 Amd 9 sibling Amendment, src/tests 무변경).
    direction: strengthening
    sunset_justification: |
      §결정 1 binary always-spawn invariant 무변경 + Amendment 2 §결정 15 entry 5 무변경 — 6번째 entry append (closed enumeration 확장 additive). ADR-039 §결정 15 line 315 "6번째 inline whitelist entry 추가 = 별도 ADR Amendment 의무 (ADR-058 §결정 5 evidence-gate)" 충족. evidence-gate = H1 게이트 연극화 차단 (subagent owner 면 재귀 가드 silent skip 실측 입증, Story §4.2 H1 [verified](ADR-039:474)). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (merge-time dispatch inline 예외 codify, 게이트 enforcement 확보), 약화 0건. carrier_story CFP-2458 = ADR-039 Amendment 6 + ADR-052 Amendment 15 + ADR-070 Amendment 9 + ADR-081 Amendment 9 sibling amendment 4-set (Epic CFP-2457 Story A).
  - amendment: 7
    date: 2026-06-30
    carrier_story: CFP-2488
    summary: |
      §결정 19 신설 (Story-teammate = lead 위임 per-Story Orchestrator — spawn scope 단위 위임 codify). §결정 1 binary always-spawn 의 "Orchestrator-only spawn" 불변식을 **폐기가 아니라 "Story scope 단위 위임"으로 재정의** — lead (top-level Claude 세션) 가 적격 Story 별로 background-Agent (SendMessage-addressable Story-runner) 를 dispatch, 각 Story-teammate 가 **자기 Story scope 안에서만** lane PL subagent 를 spawn (2-level 토폴로지: lead 1 + teammate N, teammate→teammate spawn 불가·lead 고정). **dispatch 메커니즘 = background-Agent-as-Story-runner (검증된 경로)** — 본 Epic dogfood 세션이 background-Agent(depth-0, SendMessage-addressable)→자기 sub-agent spawn 을 실증 (Orchestrator→PL→sub-agent depth 0→1→2 실작동). 공식문서가 침묵하는 agent-teams "teammate" 특정 경로에 의존하지 않음 명시 (요구사항-리뷰 §9 advisory UNVERIFIABLE 를 dogfood 실증으로 PASS 전환, ADR-119 검사연극 금지). **stall 마찰 정직 기술**: child(손자) 완료 통지가 parent(PL) 아닌 lead(main)로 surface → parent 무한대기 (구조적 한계). dispatch 운영절차에 lead 의 능동 모니터 + force-resume(SendMessage)/TaskStop 책임 명시 (마찰 은폐 금지). **§결정 2 closed inline whitelist (4 original + entry 5 Amd2 + entry 6 Amd6 = 현 6-entry) 무손상** — 본 amendment 는 **spawn-scope 위임 축**이고 inline whitelist 는 **inline vs spawn mechanism 축** = disjoint axis. inline whitelist entry 신설 0 (7번째 entry append 아님). §결정 1 binary always-spawn invariant 무변경 (위임받은 teammate 도 자기 scope 안 subagent spawn 의무 유지 — inline 대체 아님). ADR-134 (병렬 적격성 5조건 + merge-time 재검증 + per-Story dispatch) 의 spawn-권한 layer carrier. is_transitional false, sunset_justification N/A (강화 방향 — spawn 위임 codify additive, Orchestrator-only 명목 보존 + scope-confine, 약화 0). doc-only (ADR-039 in-place amendment + ADR-134 신규, src/tests 무변경).
    direction: strengthening
    sunset_justification: |
      §결정 1 binary always-spawn invariant 무변경 + §결정 2 closed inline whitelist 6-entry 무변경 (disjoint axis — spawn-scope 위임 ≠ inline-mechanism). 본 amendment = spawn scope 단위 위임 codify (additive) — Orchestrator-only spawn 명목 보존 (lead 가 위임 주체, teammate 는 lead 가 confine 한 Story scope 안에서만 spawn) + 2-level bounded 토폴로지 (teammate→teammate 불가 = 무한 재귀 Model A 와 구분). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (병렬 dispatch spawn-권한 codify), 약화 0건. evidence = dogfood 실증 (background-Agent depth 0→1→2 실작동, 요구사항-리뷰 UNVERIFIABLE advisory PASS 전환) + 산업 lead-worker bounded-위임 표준 (Story §6.3 [verified] WebSearch). carrier_story CFP-2488 = ADR-039 Amendment 7 + ADR-134 신규 ADR (Epic CFP-2481 Phase A E1).
  - amendment: 8
    date: 2026-06-30
    carrier_story: CFP-2521
    summary: |
      §결정 9 amend (Phase 2 enforcement/measurement deferred 목록에 **DevPL-side "PL self-read advisory detection"** 추가 — 기존 "Orchestrator inline write detect hook(PreToolUse on Write/Edit/mcp__github__*) + spawn cost telemetry" 와 동일 enforcement family slot). 동인 = CFP-2521 thin-PL context boundary mandate (ADR-044 Amendment 5 §결정 11) 의 D3 enforcement home. lane-PL(특히 DeveloperPL)이 비-essential 경로를 직접 read 하는 fat self-implementer drift 를 검출하는 advisory lint 의 deferred slot 을 §결정 9 deferred 목록 안에 명문 예약.
      **D3 = advisory/warning-tier ONLY (즉시 blocking FORBIDDEN)** — 두 측정 layer: (layer 1) delegation-ratio proxy via **spawn-event-v1 (EXISTING wired channel — SubagentStop hook wired, opt-in default-false ADR-043 §결정 1)** — DevPL 세션당 delegation-worker spawn 수 = coarse "PL 이 위임하고 있나" proxy. 신규 measurement channel/wiring 신설 0 (opt-in enable 만). granularity = 1 spawn=1 row (token/cost), per-read-path 검출 불가. (layer 2) 본 §결정 9 inline-detect hook slot — UNIMPLEMENTED (firsthand: hooks.json PreToolUse matcher = Bash/ScheduleWakeup/Agent 3종, Write/Edit/mcp__github__* 부재) AND **영구 advisory 천장** (대안 B: hook 은 Read-for-Q&A vs Read-as-modification 구별 불가 → fine per-read 정밀 검출 infeasible). 승격 = ADR-060 evidence-gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 후만.
      **CRITICAL invariant**: §결정 2 inline whitelist **4-entry closed enumeration 무변경** — PL read/compute boundary = **disjoint axis** (Orchestrator inline whitelist 과 다른 차원). 5번째 whitelist entry 신설 0 (§결정 2 line 161 "5번째 카테고리 추가 = ADR-039 amendment 의무" — 본 amendment 은 그것을 하지 않음, PL read budget 을 §결정 2 enumeration 에 붙이지 않는다 — disjoint 축이므로). §결정 1 binary always-spawn invariant 무변경 + §결정 3 Ownership≠Mechanism 무손상. D3 lint 실 impl = Phase 2 OOS (본 Amendment = §결정 9 deferred slot 예약 declarative). is_transitional false, sunset_justification N/A. doc-only (ADR-039 in-place amendment, src/tests 무변경).
    direction: strengthening
    sunset_justification: |
      §결정 2 inline whitelist 4-entry closed enumeration 무변경 (disjoint axis — PL read/compute boundary ≠ Orchestrator inline whitelist, 5번째 entry 신설 0) + §결정 1 binary always-spawn invariant 무변경. 본 amendment = §결정 9 Phase 2 enforcement deferred 목록에 DevPL self-read advisory detection 추가 (additive, 기존 inline-detect hook + spawn cost telemetry 와 동일 family). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (thin-PL enforcement deferred slot 예약), 약화 0건. evidence = CFP-2521 §1 비용 측정 (PL context 97% PL 직접 read) + firsthand substrate 확인 (hooks.json PreToolUse matcher Write/Edit 부재 = inline-detect slot 미점유 / spawn-event-v1 SubagentStop wired = delegation-ratio proxy 가용). carrier_story CFP-2521 = ADR-039 Amendment 8 + ADR-044 Amendment 5 paired sibling amendment 2-set (axis disjoint — 본 ADR-039 = D3 enforcement deferred slot / ADR-044 = thin-PL 동작 mandate).
  - amendment: 9
    date: 2026-07-02
    carrier_story: CFP-2544
    summary: |
      §결정 9 amend — "Orchestrator inline write detect hook (PreToolUse on Write/Edit/mcp__github__*)" deferred slot 의 **Write/Edit/MultiEdit 축 UNIMPLEMENTED → IMPLEMENTED (Wave1 warning-tier)** 전환. hooks.json PreToolUse 에 Write|Edit|MultiEdit matcher entry 신규 배선 + `hooks/pretooluse-inline-write-gate` polyglot hook + `scripts/lib/check_inline_write_gate.py` verifier (agent_id caller判정: non-empty string=subagent=allow / 부재·null·빈문자열=Orchestrator=block-candidate, F2 fail-safe) + `scripts/check-inline-write-gate.sh` thin wrapper (ADR-061). **"영구 advisory 천장" 은 Read 축 한정** (대안 B L465 근거 — Read-for-Q&A vs Read-as-modification 구별 불가) — Write/Edit/MultiEdit 은 mutation 자체 명백하므로 blockable, advisory 천장 미적용. 단 Wave1 = warning-tier 시작 (exit 0 + stderr, ADR-115 §결정 4/5 graceful degradation + ADR-060 §결정 6 evidence-gate). Wave2 deny (exit 2) 승격 = ADR-060 gate (PR ≥ 20 + bypass 외 failure = 0 + sibling merged) 후 별도 CFP. **§결정 2 inline whitelist 6-entry closed enumeration 무변경** (disjoint axis — D3 예외 = enforce 축(위임강제/BYPASS env/path carve-out for memory·scratch·repo-outside)이지 whitelist 확장 아님, 7번째 entry 신설 0 — Amendment 8 line98 "disjoint axis, 5번째 entry 신설 0" 어법 답습). mcp__github__* 축 + Bash-redirect 파일작성 우회(U2) = 본 Amendment 제외, 후속 CFP. F1: 버전 floor ≥ Claude Code 2.1.119 (agent_id 필드 가용성, #34692 실측). paired sibling = ADR-115 Amendment 1 (axis disjoint — 본 ADR-039 = §결정 9 slot 실현 선언 / ADR-115 = §결정 6 scope-boundary 이관 + hook-frame 재사용).
    direction: strengthening
    sunset_justification: |
      §결정 2 6-entry closed enumeration 무변경 + §결정 1 binary always-spawn 무변경. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (deferred slot 실현, mechanism enforcement 확보), 약화 0건. evidence = Story §1 실측 127건 Orchestrator 직접 repo 편집 (worktree 95 + 직접 32) = doc-only trust(§결정 8) 실패 입증 + agent_id 필드 caller判정 실현성 확정 (code.claude.com/docs/en/hooks verbatim). carrier_story CFP-2544 = ADR-039 Amendment 9 + ADR-115 Amendment 1 paired sibling 2-set (axis disjoint).
  - amendment: 10
    date: 2026-07-02
    carrier_story: CFP-2549
    summary: |
      §결정 20 신설 (background subagent spawn liveness = ADR-139 cross-ref). lead 가 background subagent/worker 응답을 대기할 때의 유한성(liveness) = §결정 19 (lead force-resume/TaskStop 개입 축)의 **정량 mechanical 게이트화**. ADR-139 (background-wait liveness gate) 이 carrier SSOT 이고, 본 §결정 20 = ADR-039 spawn-권한 기반 cross-ref (게이트 소유 = Orchestrator/lead 고정 = INV-L4 의 spawn-권한 근거). **§결정 9 slot 미침범** — §결정 9 deferred slot = "Orchestrator inline write detect hook (PreToolUse on Write/Edit/mcp__github__*)" = inline-write-detect 축 (완료 감지 축과 완전 별개, ADR-139 거절된 대안 E). background-wait liveness (완료 감지) 를 §결정 9 에 밀어넣으면 scope 오염 → 신규 §결정 20 으로 분리. **§결정 2 inline whitelist 6-entry 무손상** (disjoint axis — spawn liveness ≠ inline-mechanism, 7번째 entry 신설 0). §결정 1 binary always-spawn 무변경. §결정 19 body 무변경 (본 §결정 20 = §결정 19 개입 축의 정량 게이트화 cross-ref append). ADR-139 4 불변식 (INV-L1 wall-clock ceiling / INV-L2 fail-open 금지 inconclusive / INV-L3 "0-byte ≠ stall" 3-state / INV-L4 게이트 소유 Orchestrator 고정 + timeout N < liveness max-wait) 상속. is_transitional false, sunset_justification N/A (강화 방향 — background subagent spawn liveness 정량 게이트화 cross-ref, §결정 1/2/9/19 무손상). doc-only (ADR-039 in-place amendment, src/tests 무변경). paired sibling = ADR-081 Amendment 13 (§결정 D14 → ADR-139 first-instance cross-ref, ADR-139 §결정 6 sibling Amendment set).
    direction: strengthening
    sunset_justification: |
      §결정 2 inline whitelist 6-entry closed enumeration 무변경 (disjoint axis — spawn liveness ≠ inline-mechanism, 7번째 entry 신설 0) + §결정 1 binary always-spawn 무변경 + §결정 9 slot 미침범 (inline-write-detect 축 ≠ background-wait liveness 완료-감지 축, ADR-139 거절된 대안 E) + §결정 19 body 무변경. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (§결정 19 lead-intervention 축의 정량 liveness 게이트화 cross-ref 신설), 약화 0건. evidence = ADR-139 §컨텍스트 firsthand (lane PL background-yield 무한 정지 / DeveloperAgent 0-byte stall 오판 / 본 CFP-2549 설계 lane 6 deputy fan-out stall 재현). carrier_story CFP-2549 = ADR-039 Amendment 10 (§결정 20) + ADR-081 Amendment 13 paired sibling 2-set (axis disjoint — 본 ADR-039 = spawn-권한 기반 liveness 게이트 소유 / ADR-081 = §D14 companion first-instance cross-ref), 둘 다 ADR-139 §결정 6 sibling Amendment set.
is_transitional: false
---

# ADR-039: Orchestrator subagent default for codeforge modification work

## 상태

**Accepted (2026-05-08)** — carrier_story = CFP-275. Phase 1 trust model (doc-only / no hook enforcement / no telemetry, ADR-025 + ADR-029 precedent 정합 — Phase 1 doc-only trust pattern). Effective = 본 ADR 가 포함된 Phase 1 PR merge timestamp (retroactive 미적용 — 신규 codeforge orchestration 행위부터).

본 ADR 의 implementation plan SSOT = [`wrapper/change-plans/cfp-275-orchestrator-subagent-default.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-275-orchestrator-subagent-default.md) (internal-docs SSOT, ADR-013 dogfood-out). 본 ADR = 정책 결정 SSOT.

## 컨텍스트

### 사용자 directive 3 발화 (2026-05-08, verbatim — Story §1 source)

> "무조건 subagent만 하도록 하자. 그것 때문에 user stop이 자꾸 발생한다."

> "codeforge를 이용한 수정 작업에서는 무조건 subagent이다."

> "그러니까 story 발의해서 적용해"

### 추가 사용자 directive (ADR-035 §컨텍스트 verbatim — 토큰 trade-off)

> "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다."

본 directive 가 본 ADR 의 §결정 4 운영 risk surfacing (rate limit / token cost) 의 trade-off 수용 근거.

### 현재 상태

- ADR-009 (wrapper-only decomposition, Adopted) — wrapper agent 0개 invariant. Orchestrator (top-level Claude 세션) 가 모든 work 을 6 lane plugin 의 agent 로 spawn.
- ADR-025 (stop discipline + Epic-level continuity, Accepted) — user-stop = `policy_violation`, whitelist 5종 strict. §결정 7 의 `policy_violation_subdecision` 패턴 — "후보 A/B/C/D 중 어떤거?" / "큰 작업이라 확인 받겠습니다" / "Phase 1 완료, Phase 2 시작할까요?" 류 sub-decision stop = defect.
- ADR-029 (phase execution visibility, Accepted) — Orchestrator stderr 1-line narration 의무.
- ADR-031 (lane-spawn evidence trail, Accepted) — Story §14 row append (Orchestrator self-write monopoly).
- ADR-035 (codeforge agent teams Epic, Accepted) — D2 agent teams 활성 분기. ADR-022 deprecate.

### Gap

1. **ADR-009 의 "Orchestrator 가 모든 work spawn" 원칙이 explicit policy 로 codified 되지 않음** — 결과적으로 wrapper Orchestrator 가 매 codeforge 수정 작업마다 "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 발생. 해당 분기가 ADR-025 §결정 7 의 sub-decision stop 발화 채널.
2. **Inline whitelist 미정의** — 사용자 dialog (AskUserQuestion 등) / TodoWrite scratchpad / read-only Q&A 답변 / status report 4 카테고리가 mechanism level 분기되지만 normative table 부재.
3. **Anthropic 공식 권장 (selective spawn) 와 codeforge 정책 (always-spawn) 사이 진영 위치 미정의** — Researcher §6.B 4 framework 비교 결과 wrapper-specific binary 정책의 학계/산업 case study 부재 (Researcher §6.A fact 5).
4. **SSOT 분산점 6 곳** — CLAUDE.md L103 단락 / playbook §3 / playbook §14 / consumer-guide §"Stop discipline" / hotfix-playbook / Wrapper 위임 패턴 — collapse 필요 (RefactorAgent B1 HIGH).

## 결정 (17)

### 결정 1 — codeforge 수정 작업 = Orchestrator default subagent spawn

codeforge 를 이용한 **수정 작업** 진행 중, Orchestrator (top-level Claude 세션, ADR-009) 는 모든 work 을 `Agent` tool spawn (subagent) 으로 수행한다. inline 수행 (Orchestrator turn 안에서 Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 직접 호출) 은 §결정 2 의 4 entry whitelist 외 영역에서 금지.

**수정 작업 정의** (closed enumeration):

- file edit / write (`docs/**`, `src/**`, `templates/**` 포함)
- GitHub state change (Issue / PR / comment / label / milestone / sub-issue / branch / merge)
- Story file write (§1-§14 어느 섹션이든 — **단 §9 verdict / §10 FIX Ledger / §14 Lane Evidence / phase transition 4-sub-scope 제외, §결정 15 inline whitelist 5번째 entry scope — Amendment 2, CFP-1340 partial rollback**)
- FIX Ledger §10 row append (fix-event-v1 contract — ownership 무변, mechanism 만 spawn 또는 Orchestrator inline — Amendment 2 §결정 15)
- Lane-spawn evidence §14 row append (ADR-031 — ownership 무변, mechanism 만 spawn 또는 Orchestrator inline — Amendment 2 §결정 15)
- gate label transition (`gate:design-review-pass` 등)
- phase label transition (`phase:요구사항` → `phase:설계` 등)
- workflow yaml 수정·추가
- ADR / Change Plan / domain-knowledge 페이지 write
- **trivial Read 1건 도 spawn 의무** (사용자 verbatim 명시 — Story §2 AC-3 trivial-threshold-zero)

"이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 자체 금지 — branch logic 제거가 본 ADR 의 핵심.

### 결정 2 — Inline whitelist (closed 4-entry enumeration)

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 1 | 사용자 dialog | `AskUserQuestion` / 확답 step / 정보 요청 답변 (Yes/No / 옵션 선택) | Subagent one-shot 이라 continuous dialog 자체 mechanism 불가능 (ADR-009 §결정 + CLAUDE.md "플랫폼 제약"). DialogFidelityAgent verifier subagent spawn 은 본 entry scope 안 cognitive 보강 — 사용자 dialog 본 발화 inline 유지 + 직전/직후 verifier spawn = §결정 1 default subagent spawn 정합 (5번째 entry 신설 아님, closed enumeration 보존 — ADR-071 §결정 13 / CFP-818). (DialogFidelityAgent verifier = CFP-2236 sunset — ADR-071 Amendment 9. 본 entry #1 enum 자체는 무손상 active.) |
| 2 | TodoWrite scratchpad | progress visualization marker write | TodoWrite = file write 아님, Orchestrator scratchpad / meta progress channel — 수정 작업 enumeration 미포함. (참고: ADR-038 = TodoWrite progress visualization 도입 informational reference, 본 entry 정당화에 normative dependency 아님 — TodoWrite tool surface 자체가 file system / GitHub state mutation 미발화이므로 본 ADR 내 standalone 정당화) |
| 3 | Read-only Q&A 답변 | 사용자 정보 요청에 대한 응답 (state report / option enumeration / 도메인 설명) | 수정 작업 아님 — codeforge orchestration scope 외 |
| 4 | Status report | Phase 완료 / Story close / final report | 수정 작업 아님 (read-only synthesis) — ADR-025 Amendment 1 §결정 11 의 "1번 final report" |

4 entry **외** 의 모든 codeforge orchestration 행위 = subagent spawn 의무. **모호 시 = 수정 작업 측 분류** (안전 방향 — ADR-013 cutoff precedent 정합).

5번째 카테고리 추가 = ADR-039 amendment 의무. 본 closed enumeration 가 future "Skill 호출 / Glob / Grep / Read tool 분류 enum 확장" 압박을 차단 — 모두 4 entry 의 어느 하나로 routing 또는 수정 작업 측 분류.

### 결정 3 — Ownership ≠ Mechanism 분리

본 정책은 **mechanism (어떻게 수행)** 변경. **ownership (누가 작성권)** 무변.

- Orchestrator monopoly ownership (유지 — invariant 무손상):
  - Story §10 FIX Ledger row append (CFP-32 / fix-event-v1 contract)
  - Story §14 Lane Evidence row append (ADR-031 / CFP-126)
  - review-verdict v3 final write (Story §9 / GitHub comment / gate label / phase transition — ADR-022 deprecate 후에도 Orchestrator domain 유지)
  - branch protection / CI workflow / cross-plugin schema templates
- Mechanism (변경): 위 ownership 영역의 file write / GitHub state change 도 **subagent spawn 으로 수행** (default mechanism) **또는 Orchestrator inline write** (Amendment 2 §결정 15 inline whitelist 5번째 entry scope = §9/§10/§14/phase 4-sub-scope 한정). Orchestrator 가 "§10 row append 전용 subagent" / "§14 row append 전용 subagent" / "label transition 전용 subagent" 를 spawn 해 Edit / mcp__github__\* tool 호출 (default) — 또는 Orchestrator-monopoly Story-file 4-sub-scope 영역은 inline write 직접 수행 가능 (Amendment 2, CFP-1340).

본 분리는 ADR-031 §결과 invariant 무손상 입증 + lane plugin agent 변경 부재 입증의 핵심 근거. **Amendment 2 (CFP-1340) 후**: Orchestrator-owned delegate subagent (기존 mechanism) + Orchestrator inline (Amendment 2 추가 mechanism) 양 mechanism 모두 valid — ownership identity (Orchestrator monopoly) 보존, mechanism level 양 path 허용.

### 결정 4 — Scope = codeforge orchestration 한정

본 정책 적용 범위 = **codeforge orchestration**. 즉 wrapper Orchestrator 가 codeforge family (wrapper + 6 lane plugin) 의 spawn / docs/** / GitHub state / Story file / FIX Ledger / lane-spawn evidence 영역에서 수행하는 행위. 일반 Q&A / conversational 응답 / non-codeforge 작업 (예: 단순 정보 답변 / 사용자 dialog) 은 비적용 — §결정 2 Inline whitelist 가 boundary clarification.

### 결정 5 — Lane plugin / 6 SubAgent / inter-plugin contract = 0 변경

- 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) agent 변경 0건.
- design lane 6 SubAgent (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch) + 2 CONDITIONAL SubAgent (LiveOps / LiveOrdering) 변경 0건.
- Inter-plugin contract 6 (requirements_output / design_output / review_verdict v3 / test_verdict / develop_output / pmo_output) 변경 0건.
- ADR-009 §결과 invariant 무손상 (Writer 단독 invariant precedent — ADR-029 / ADR-031 와 동일 패턴).

### 결정 6 — Hotfix path 동일 적용 (no exception)

`docs/hotfix-playbook.md` 의 Hotfix 경로 (운영 장애 대응 / 사후 감사 의무) 도 본 정책 적용. 사용자 verbatim "무조건" — emergency 시에도 spawn 의무. Hotfix 의 fast-path 본질 (Phase skip / lane skip) 은 무변, **mechanism 만 spawn 의무**.

### 결정 7 — Consumer scope (wrapper + consumer Orchestrator 동일 적용)

본 정책 = wrapper Orchestrator + consumer Orchestrator (예: mctrader Orchestrator / 추후 다른 consumer) 모두 적용. consumer Orchestrator 가 codeforge family plugin 을 사용하는 시점부터 본 정책 inheritance — `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" 신규 subsection 가 SSOT cross-ref.

ADR-025 §결정 9 (consumer scope) 와 동일 enforcement 패턴 — Phase 1 = trust model (사용자 directive 의 directive 발화 의무 + enforcement hook 없음).

### 결정 8 — Phase 1 = doc-only trust model

본 ADR 의 effective enforcement 강도 = doc-only. 매 Orchestrator 행위 시 (1) 본 ADR-039 / (2) playbook §3.0 / (3) CLAUDE.md "Default subagent context" / (4) consumer-guide § "Subagent default" / (5) hotfix-playbook 1줄 reading 시 자체 인지. 자동 enforcement 부재.

ADR-025 / ADR-029 precedent 정합 (Phase 1 doc-only trust pattern) — Phase 2 enforcement = 별도 follow-up CFP.

### 결정 9 — Phase 2 enforcement / measurement = deferred follow-up CFP

후속 CFP (현재 미할당) 가 다음 영역 처리:

- **stop-event-v1 ledger** 도입 (ADR-025 §결정 10 deferred). Orchestrator user-stop 발화 시 ledger row append → `reason_class: policy_violation_subdecision` 발생률 측정 → 본 정책 효과 검증.
- **Orchestrator inline write detect hook** (PreToolUse on Write / Edit / mcp__github__\*). Orchestrator 직접 호출 detect → warning surface (또는 strict mode 시 차단). **Update (Amendment 9, CFP-2544)**: 이 hook slot 의 **Write/Edit/MultiEdit 축**은 UNIMPLEMENTED → **IMPLEMENTED (Wave1 warning-tier)** 전환 (superseded-for-Write/Edit/MultiEdit). 신규 배선 = hooks.json PreToolUse Write|Edit|MultiEdit matcher entry + `hooks/pretooluse-inline-write-gate` polyglot hook + `scripts/lib/check_inline_write_gate.py` verifier (agent_id caller判정: non-empty string=subagent=allow / 부재·null·빈문자열=Orchestrator=block-candidate) + `scripts/check-inline-write-gate.sh` thin wrapper. Wave1 = exit 0 + stderr (NEVER deny — ADR-115 §결정 4/5 graceful degradation). **mcp__github__\* 축 + Read 축 + Bash-redirect 파일작성 우회 = still-deferred** (별도 CFP). 아래 §결정 9 layer 2 "영구 advisory 천장" 은 **Read 축 한정** — Write/Edit/MultiEdit 은 mutation 자체 명백하므로 blockable (advisory 천장 미적용). paired sibling = ADR-115 Amendment 1.
- **spawn cost telemetry** (token / latency 정량 측정). Researcher §6.F fact gap (spawn latency 정량 데이터 부재) 충당.
- **rate-limited error → unwanted user-stop** second-order risk 측정 (OpRiskArch §7.4.4 운영 risk surfacing).
- **DevPL-side "PL self-read advisory detection"** (Amendment 8, CFP-2521 — ADR-044 Amendment 5 §결정 11 D3 enforcement home). lane-PL(특히 DeveloperPL)이 비-essential 경로(docs/stories 밖 plugin.json/scripts/*.yaml/playbook)를 직접 read 하는 fat self-implementer drift 검출. **advisory/warning-tier ONLY (즉시 blocking FORBIDDEN)** — 두 측정 layer:
  - **layer 1 — delegation-ratio proxy** via spawn-event-v1 (EXISTING wired channel — SubagentStop hook wired, opt-in default-false ADR-043 §결정 1). DevPL 세션당 delegation-worker spawn 수 = coarse "PL 이 위임하고 있나" proxy. 신규 channel/wiring 신설 0 (opt-in enable 만). granularity = 1 spawn=1 row, per-read-path 검출 불가.
  - **layer 2 — inline-detect hook** = 위 "Orchestrator inline write detect hook(PreToolUse on Write/Edit/mcp__github__*)" slot 과 동일 family. UNIMPLEMENTED (firsthand: hooks.json PreToolUse matcher = Bash/ScheduleWakeup/Agent 3종, Write/Edit/mcp__github__* 부재) AND **영구 advisory 천장** (대안 B L465: hook 은 Read-for-Q&A vs Read-as-modification 구별 불가 → fine per-read 정밀 검출 infeasible). **Update (Amendment 9, CFP-2544)**: 이 "UNIMPLEMENTED" 기술은 **Write/Edit/MultiEdit 축에 한해 superseded** — 해당 축은 IMPLEMENTED Wave1 (hooks.json Write|Edit|MultiEdit matcher + `hooks/pretooluse-inline-write-gate` + `scripts/lib/check_inline_write_gate.py`, agent_id caller判정). **"영구 advisory 천장" 은 Read 축 한정으로 재확인** — Read-for-Q&A vs Read-as-modification 구별 불가 논리는 Read 에만 적용되고, Write/Edit/MultiEdit 은 mutation 자체 명백하므로 blockable (Wave2 deny 승격 가능, ADR-060 gate). mcp__github__* 축 + Bash-redirect 우회는 여전히 UNIMPLEMENTED (후속 CFP).
  - 승격 = ADR-060 evidence-gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 후만. **§결정 2 inline whitelist 4-entry closed enumeration 무변경** — PL read/compute boundary = disjoint axis (Orchestrator inline whitelist 과 다른 차원), 5번째 entry 신설 0. D3 lint 실 impl = CFP-2521 Phase 2 OOS.
  - **Orchestrator-self realization (cross-ref stub, Amendment 없음 — ADR-142 anchor, CFP-2572)**: 위 DevPL-side advisory 는 holder=lane-PL 축이다. 동일 §결정9 Read-axis "영구 advisory 천장" 을 holder=Orchestrator-self 로 realize 한 것이 **ADR-142**(Orchestrator-self READ/synthesis/verbose-return 규율). ADR-142 는 본 §결정9 를 재결정하지 않고 위로 가리키는 disjoint anchor 이며, **§결정 2 inline whitelist(현행 6-entry closed, WRITE 축)와 disjoint axis — 7번째 entry 신설 0**. L7 self-context proxy 도 본 layer 1 delegation-ratio(spawn-event-v1) substrate 를 Orchestrator-self 로 재사용.

ROI 평가 후 enforcement 강도 결정. 본 Story scope = Phase 1 doc-only. **Update (Amendment 1, CFP-895)**: Pre-spawn-pin mandate (§결정 14 신설) = Phase 1 doc-only enforcement 의 일부분으로 자연 흡수. Phase 2 hook enforcement layer 가 발효되면 본 §결정 14 mandate 도 hook-level 자동 verify 로 격상.

### 결정 10 — ADR-009 amends 관계

본 ADR = ADR-009 (wrapper-only decomposition) 의 **자연 확장** / **explicit 격상**. 새 invariant 가 아닌 기존 invariant 의 codification. frontmatter `amends: ADR-009` 명시.

ADR-009 의 "wrapper agent 0개 → Orchestrator 가 모든 work 을 spawn" 원칙은 이미 wrapper-only decomposition 의 결과로 존재. 본 ADR 가 그 원칙을 **explicit policy 로 stamping** + branch logic 제거 + Inline whitelist 4-entry codification.

### 결정 11 — ADR-022 (Deprecated) 와의 충돌 자동 해소

ADR-022 (Sonnet decider 5-trigger 자동 발동) = Deprecated by ADR-035 (CFP-134 / ADR-035, 2026-05-08). 본 ADR 시행 후에도 Sonnet 자동 dispatch 부재 — 사용자 ad-hoc 호출 전용 도구.

사용자 ad-hoc Sonnet 호출 시에도 본 정책 적용 — Sonnet 호출 자체가 subagent spawn (Agent tool with `model:sonnet`) 이므로 자연 정합. CFP-137 / CFP-134 follow-up 의무 (ADR-022 본문 잔재 cleanup) 는 본 ADR scope 외.

### 결정 12 — Cross-ADR amendment 의무 (Ownership ≠ Mechanism normative anchoring)

§결정 3 의 Ownership ≠ Mechanism 분리 (Orchestrator-spawned subagent = Orchestrator-owned delegate) 가 normative 정합을 갖추려면 ADR-031 (lane-spawn evidence) + fix-event-v1 contract (Story §10 FIX Ledger) 의 "Orchestrator self-write" / "Writer monopoly v1: Orchestrator 단독" invariant 가 **Orchestrator-owned delegate subagent 의 self-write 행위를 explicitly cover** 해야 한다.

**Amendment 의무** (본 ADR carrier Story 안 commit 동반, ADR-010 sibling sync 패턴):

- `docs/adr/ADR-031-lane-spawn-evidence-trail.md` — **Amendment 1** 신설:
  > Orchestrator-owned delegate subagent (Orchestrator 가 §14 row append 전용으로 spawn 한 subagent) 의 §14 lane evidence write = §결정 1 의 "Wrapper Orchestrator self-write" 정의에 포함됨. mechanism level subagent 경유여도 ownership identity = Orchestrator 유지 (ADR-039 §결정 3 cross-ref).
- `docs/inter-plugin-contracts/fix-event-v1.md` — **Amendment** 신설 (`append_rules.writer` 절):
  > "Orchestrator 단독" 의 **Orchestrator 정의** = top-level Claude 세션 + Orchestrator 가 §10 row append 전용으로 spawn 한 delegate subagent 모두 포함. lane plugin agent 가 자체 임의 §10 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn). Cross-ref: ADR-039 §결정 3 + §결정 12.

본 amendment 가 본 carrier Story 안 commit 되지 않으면 §결정 3 가 ADR-031 line 49 + fix-event-v1 line 21 / line 135 invariant 와 normative 충돌 — DesignReview P0 차단 사유.

**ADR-010 sibling sync** (fix-event-v1 amendment 시): wrapper repo 만 fix-event-v1 보유 (canonical). codeforge-pmo / 기타 lane plugin sibling 부재 — sibling sync overhead 0건.

### 결정 13 — Phase 1 scope expansion (4 SSOT doc edits effective date alignment)

§결정 8 의 Phase 1 doc-only trust model 효과 = 4 SSOT doc reading 시 자체 인지. 이 효과는 4 SSOT doc 가 **본 ADR 와 동일 PR 안에서 갱신** 되어야 발효 — 별도 follow-up PR 분리 시 본 ADR Accepted 시점부터 4 SSOT doc 미반영 PR merge 시점까지 normative gap 발생 ("Accepted but not effective" — DesignReview P1 finding).

**Phase 1 PR scope 확정** (Phase 2 PR scope 에서 이동 — Story §4 정정):

- `docs/adr/ADR-039-...md` (본 file)
- `docs/adr/ADR-031-...md` (Amendment 1 — §결정 12 carrier)
- `docs/inter-plugin-contracts/fix-event-v1.md` (Amendment — §결정 12 carrier)
- `docs/change-plans/cfp-275-orchestrator-subagent-default.md` (internal-docs SSOT, ADR-013)
- `docs/domain-knowledge/orchestrator-discipline/spawn-default.md`
- **`CLAUDE.md`** — "오케스트레이션 규칙" / "플랫폼 제약" / "Wrapper 위임 패턴" 갱신 (Phase 1 이동, B1 + B2)
- **`docs/orchestrator-playbook.md`** — §3.0 normative section 신설 (Phase 1 이동, B1 HIGH)
- **`docs/consumer-guide.md`** — § "Subagent default (codeforge orchestration)" 신규 subsection (Phase 1 이동, B5 HIGH)
- **`docs/hotfix-playbook.md`** — 1줄 ADR-039 cross-ref (Phase 1 이동)

**Effective date** = 본 ADR 가 포함된 Phase 1 PR merge 시점 = 4 SSOT doc 모두 갱신된 시점 (동일 PR commit batch 보장). retroactive 미적용.

DeveloperPL Phase 2 lane 경유 안 함 — ArchitectPL 직접 4 doc edit (chief author 통과 방향 유지, 편차 제거).

### 결정 14 — Pre-spawn-pin mandate (DeveloperPL + branch-creating subagent — Amendment 1, CFP-895)

새 git branch 를 생성하는 모든 subagent (특히 DeveloperPLAgent, codeforge-develop:DeveloperAgent, 기타 codeforge-develop role:dev 가 PR 생성 시) 는 **branch 생성 직전 Step 0** 에서 current origin/main HEAD 를 explicit pin 의무. self-claim / Orchestrator packet-provided SHA / local working dir HEAD / 이전 memory SHA 무조건 신뢰 금지 ([[feedback_verify_pin_head_sha]] codification).

**의무 절차** (subagent prompt Step 0 cohort):

```bash
# Step 0 — pin current origin/main HEAD (subagent self-execution, single source of truth)
git fetch origin
MAIN_HEAD=$(git rev-parse origin/main)
# 또는: MAIN_HEAD=$(gh api repos/<org>/<repo>/commits/main --jq .sha)
echo "PINNED_MAIN_HEAD=$MAIN_HEAD"
# 모든 후속 branch 생성 + git rebase --onto + PR open 시 본 SHA 사용 의무
# packet-provided reference SHA = 단순 baseline 참고 (subagent self-pin 우선)
```

**근거** — 3차 누적 systemic incident pattern (CFP-895 §1 evidence):

| Story | DeveloperPL stale base | current origin/main at spawn time | 회복 cost |
|---|---|---|---|
| CFP-699 / Wave 1 Story-1 | (parallel session, memory 기록) | (parallel session) | strict-verify-gate 3회 적발 + 사용자 RESET trigger |
| CFP-702 / Wave 1 Story-2 | (parallel session, memory 기록) | (parallel session) | DeveloperPL 2× 거짓 self-claim → ADR-070 reject |
| **CFP-848 / Epic A Story-5** | `65901ac5` (CFP-785 #809 stale) | `eafc726` (CFP-833 Phase 2, 3 commits ahead) | FIX Iter1 rebase + 2차 mid-flight rebase (CFP-841/833 추월 additive) |

**Orchestrator post-spawn verify** (mandate codify — playbook §3.0.16 짝, 본 §결정 cross-ref):

DeveloperPL 또는 branch-creating subagent return 직후 Orchestrator 가 `mcp__github__pull_request_read get` 의 `head.sha` parent commit 을 `gh api repos/<org>/<repo>/commits/main --jq .sha` (또는 `mcp__github__list_commits main`) 와 비교. **mismatch = FIX trigger** (구현-side stale-base, RESET=NO, 동일 subagent 재dispatch with explicit current-main-HEAD pin). spurious merge gate 차단 forcing function.

**self-reset 금지** (memory `feedback_no_permission_prompts` lineage + CFP-785 InfraEng T2 self-reset 선례):

re-dispatch 시 subagent prompt 안 **"self-reset 금지 / 기존 작업 content 보존, only rebase the base"** 명시 의무. `git reset --hard origin/<branch>` 같은 destructive 회복 = 이전 작업 손실 → DeveloperPL 의 production 이력 회복 곤란 (Story-5 FIX Iter1 evidence).

**Closed enumeration (§결정 1 binary always-spawn 무손상)** — 본 amendment 는 **§결정 1 의 mechanism level 강화** (pre-spawn-pin Step 0 추가) 일 뿐, §결정 1 의 default subagent spawn 정책 자체는 무변. §결정 2 Inline whitelist 4-entry 도 무변 (closed enumeration 확장 0).

**Verification evidence**:
- 본 ADR Amendment 1 evidence 표 (위 3 row)
- CFP-895 Issue body §verified-via (memory + Story-5 PR #849 commit lineage 53c2851 parent stale-base)
- CFP-895 Issue 본문 §제안 deliverable (a/b/c 3-touchpoint codify)

### 결정 15 — Orchestrator-monopoly Story-file handoff inline write (Amendment 2, CFP-1340 partial rollback)

§결정 2 의 Inline whitelist 4-entry 표에 **5번째 entry** 추가. **partial rollback** — §결정 1 closed enumeration 안 "Story file write §1-§14 = subagent spawn 의무" 의 §9/§10/§14/phase 4-sub-scope 만 inline 허용으로 약화 (4-sub-scope 외 §1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13 = §결정 1 binary always-spawn 유지).

**Inline whitelist 4-entry → 5-entry 확장 표** (§결정 2 의 4-entry 위 추가):

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 5 | **Orchestrator-monopoly Story-file handoff inline write** (Amendment 2, CFP-1340) | Story file 의 Orchestrator-monopoly 4-sub-scope inline write — §9 verdict / §10 FIX Ledger row append / §14 Lane Evidence row append / phase transition (`phase:요구사항` → `phase:설계` 등) | Orchestrator-monopoly Story-file section 의 monopoly 명목 보존 (ADR-031 §14 + fix-event-v1 §10 contract invariant). general-purpose editor subagent 위임 시 inline cost (~60-70KB 큰 파일 inline reconstruction) + Orchestrator-monopoly intent 희석 우려 — 사용자 explicit reject (2026-05-17 KST CFP-848 directive verbatim "Orchestrator-monopoly Story-file section handoff 시 general-purpose editor subagent 위임 reject"). lane agent self-write 영역 (§1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13) = 본 entry scope 외 — §결정 1 binary always-spawn 유지. |

**4-sub-scope 명세** (closed enumeration):

1. **§9 verdict inline write** — lane verdict write / GitHub gate label transition. final pl_recommendation (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE) write 시.
2. **§10 FIX Ledger row append** — fix-event-v1 contract row append. Orchestrator 단독 monopoly (CFP-32 invariant 보존).
3. **§14 Lane Evidence row append** — ADR-031 lane-spawn evidence trail. Orchestrator self-write monopoly invariant 보존.
4. **Phase transition** — `phase:요구사항` → `phase:설계` → `phase:설계리뷰` → ... label transition (단일 label flip + Story file frontmatter `phase` field 갱신).

**Lane agent self-write exclusion 명시** — codeforge-{requirements,design,develop,review,test,pmo,deploy,deploy-review} lane plugin agent 가 owned section (§1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13) write 시 = 본 entry scope 외. §결정 1 binary always-spawn 정책 유지.

**Edge case 처리**:

- **Edge-1 — Lane agent self-write 영역 inline write claim**: lane agent owned section (§1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13) 을 Orchestrator inline 으로 write 하는 행위 = 본 entry scope 외 + §결정 1 binary always-spawn violation. ownership 정합 우선 — lane agent self-write 영역은 subagent spawn 의무 유지.
- **Edge-2 — Session 재개 시 stale state 처리**: session 재개 후 Orchestrator-monopoly 4-sub-scope state (예: 이전 §10 row append 진행 중 중단) 가 stale 한 경우 — Orchestrator 가 inline read-verify (§10 row count / 최신 timestamp) 후 inline write 재개. subagent spawn 우회 정당 (state 복원 동안 mechanism level 1-shot subagent overhead 회피).

**Ownership ≠ Mechanism 분리 (Amendment 2 confirm)** — Orchestrator monopoly ownership 보존 + mechanism level inline write 추가 (subagent spawn 과 disjoint, 양 mechanism 모두 valid).

- ADR-031 §14 row append "Orchestrator self-write monopoly" invariant 보존 — Orchestrator-owned delegate subagent (§결정 12 Amendment 의무) + Orchestrator inline (Amendment 2 추가) 양 mechanism 모두 invariant 정합.
- fix-event-v1 §append_rules.writer "Orchestrator 단독" 정의 보존 — top-level Claude 세션 (Orchestrator) + Orchestrator-owned delegate subagent + Orchestrator inline 3 mechanism 모두 cover.

**Closed enumeration (§결정 1 binary always-spawn 무손상 invariant)** — Amendment 2 partial rollback 은 §결정 2 Inline whitelist 4-entry 의 5번째 entry append 패턴 (closed enumeration 확장, ADR-058 §결정 5 evidence-gate 통과 — sunset_justification 충족). §결정 1 closed enumeration 안 "Story file write §1-§14" 항목 의 §9/§10/§14/phase 4-sub-scope 만 exception clause 형식 으로 entry 5 routing.

**5번째 entry exhaustiveness declare**: 5번째 entry 의 4-sub-scope (§9 verdict / §10 FIX Ledger / §14 Lane Evidence / phase transition) 는 **closed enum**. 5번째 sub-scope 추가 = 별도 ADR Amendment 의무 (강화 방향 ratchet 정합 단 사용자 burden 변화 영역 — sub-scope 확장 = inline write 영역 확장 = Orchestrator monopoly mechanism 영역 확장). 6번째 inline whitelist entry 추가 = 별도 ADR Amendment 의무 (ADR-058 §결정 5 evidence-gate). closed enumeration 안정성 보장.

**Verification evidence**:
- 사용자 directive 2026-05-17 KST CFP-848 verbatim (memory `feedback_orchestrator_monopoly_inline_write` carrier)
- ADR-031 §14 lane-spawn evidence "Orchestrator self-write monopoly" invariant 정합 verify
- fix-event-v1 §append_rules.writer "Orchestrator 단독" invariant 정합 verify

### 결정 16 — Autonomous permission UI behavior (Amendment 3, CFP-1340 strengthening)

Orchestrator 의 permission UI behavior normative SSOT. **destructive-only ask, reversible auto-proceed** binary 분류. §결정 1 binary always-spawn 과 disjoint axis (permission UI 차원 vs mechanism 차원).

**Destructive closed enum (≥8 항목)** — ask permission 의무 (사용자 explicit approval 후 진행):

1. `git reset --hard` (working tree / branch state 복구 불능)
2. `git push --force` / `git push --force-with-lease` (remote ref 비대화식 overwrite)
3. file delete (`rm -rf` / file system level delete — git untracked file 포함)
4. branch delete (`git branch -D` / remote branch delete `gh api -X DELETE`)
5. Issue mutation (close / state change / lock — `gh issue close` / `mcp__github__issue_write` close action)
6. label create (registry mutation — `gh label create` / `mcp__github__create_label`)
7. workflow yaml 변경 (`.github/workflows/**` add / edit / delete — CI/CD policy mutation)
8. ADR row append (`docs/adr/ADR-RESERVATION.md` yaml mutation — sequential append registry — collision rebase 영역)

**외부 visible (destructive enum 동격)** — ask permission 의무:

- PR create / merge / close / comment to shared main branch (`gh pr create / merge / close / comment` / `mcp__github__*`)
- external notification (`mcp__github__add_issue_comment` to public Issue / Discussion post / external webhook trigger)

**Reversible closed enum (≥6 항목)** — auto-proceed (no permission UI reflex prompt):

1. local file Edit (`Edit` tool — git reflog 복구 가능)
2. local script run (`python file.py` / `bash script.sh` — destructive side effect 부재 시)
3. temp-file mechanics (`.tmp-*.md` / scratchpad write — manual delete 가능)
4. `.claude/settings.local.json` edit (per-project local config, git untracked default)
5. `git add` (staging area — `git restore --staged` 복구 가능)
6. branch create (`git branch <name>` / `git checkout -b <name>` — `git branch -D` 회수 가능)
7. commit (`git commit` — `git reset --soft HEAD~1` 회수 가능)
8. Edit on `docs/**` (governance docs — git reflog + PR review process 복구 가능)

**Reversibility test 근거 명시** — 각 reversible 항목의 회복 가능 mechanism:

- git reflog (90-day default retention) — local edit / commit / branch create / git add 모두 recovery point 보유
- Issue history (GitHub immutable audit log) — comment / Issue state change 모두 history 보유 (단 destructive Issue close / lock = side effect 비례 ask)
- branch 복구 가능성 — local branch delete 시 reflog SHA 로 `git branch <name> <sha>` recovery

**ADR-039 §결정 1 binary always-spawn 무관 (disjoint axis)** — §결정 1 = mechanism 차원 (Orchestrator inline vs subagent spawn). §결정 16 = permission UI 차원 (ask vs auto-proceed). 두 axis 완전 disjoint:

| | §결정 1 binary always-spawn (mechanism) | §결정 16 autonomous permission (UI) |
|---|---|---|
| destructive + inline whitelist 4-entry | inline 허용 + ask permission | (whitelist scope 안 mechanism, destructive 여부 별도 평가) |
| destructive + 외 영역 | subagent spawn 의무 + ask permission | (subagent prompt 안 destructive action 도 ask) |
| reversible + inline whitelist 4-entry | inline 허용 + auto-proceed | (whitelist scope 안 mechanism, reversible action auto-proceed) |
| reversible + 외 영역 | subagent spawn 의무 + auto-proceed | (subagent prompt 안 reversible action 도 auto-proceed) |

**사용자 directive verbatim citation**:

- 2026-05-17 KST CFP-848: "아 묻지말고 그냥 하라고"
- 2026-05-17 KST CFP-848: "쓰잘데기 없는 권한 묻지말고 전부 수정하라"

memory `feedback_no_permission_prompts` normative 승격 carrier. 강화 ratchet — closed enumeration (destructive ≥8 / reversible ≥6 / 외부 visible 1 super-class) 확장 만, 약화 0. ADR-064 §결정 7 top-down ratchet 정합 (CFP-1149 symmetric ratchet — 강화 방향 normative anchor).

**Closed enumeration exhaustiveness declare**:

- destructive enum 8 항목 → 9번째 추가 = 별도 ADR Amendment 의무 (강화 방향, ratchet 정합).
- reversible enum 8 항목 → 9번째 추가 = 별도 ADR Amendment 의무 (사용자 burden 영향 — auto-proceed 영역 확장 = permission UI 차단 영역 확장).
- 외부 visible super-class 확장 = 별도 ADR Amendment 의무.

**Verification evidence**:
- 사용자 directive 2026-05-17 KST CFP-848 verbatim (memory `feedback_no_permission_prompts` carrier)
- destructive enum 8 항목 각각의 reversibility test 근거 (git reflog / Issue history / branch 복구 mechanism 각 verify)
- ADR-039 §결정 1 binary always-spawn 정책 무영향 verify (disjoint axis 표 4-cell 정합)


### 결정 17 — Chief author spawn span guideline (Amendment 5, CFP-1438)

Chief author (특히 ArchitectAgent Opus) 의 single spawn 안 monolithic span (15-40min wide drift surface) 패턴을 **anti-pattern declare** + multi-step sequential smaller spawn 권장 (recommendation tier, Wave 1 declarative-only — mechanical enforcement 별 sub-CFP carrier).

**Anti-pattern (declared, recommendation tier)**:

- chief author 단일 spawn 안 (a) Read + analyze deputy outputs + (b) draft Change Plan §1-§13 + (c) write ADR draft + (d) write Story file §3/§7/§11 + (e) write workflow stub + (f) update CLAUDE.md + (g) verify-before-trust 5 sub-scope all at once
- span ≈ 15-40min 단일 spawn → wide drift surface (mid-spawn origin/main 다른 sibling PR merge → stale base race amplification)
- 단일 spawn anti-pattern = CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach root cause 의 한 측 (Sub-CFP A/B/C 가 detection/claim mechanism complement 했지만, root cause 직접 축소 = span 자체 작게)

**Recommended pattern (multi-step sequential smaller spawn)**:

3-step sequential pattern (ADR-044 Amendment 3 paired carrier — team-spec yaml multi-step lifecycle pattern):

1. **Skeleton spawn** (~5-7min): frontmatter + section heading + placeholder + ADR-RESERVATION row append + amendments_reserved slot pre-claim. drift surface ≤ 7min single spawn.
2. **Body spawn** (~5-7min): substantive content (Change Plan §1-§13 본문 + ADR §결정 본문 + Story §3/§7/§11 본문). previous skeleton state passed as input. drift surface ≤ 7min single spawn.
3. **Integration spawn** (~5-7min): cross-refs verify + lint validation + workflow stub finalize + CLAUDE.md update + commit. previous body state passed as input. drift surface ≤ 7min single spawn.

**Trade-off matrix** (Wave 1 declare, Wave 2 mechanical telemetry carrier deferred):

- **Benefits**: drift surface per spawn ↓ (preventive complement to ADR-073 Amd 11 SHA pin + ADR-082 Amd 15 spawn prompt anchor + ADR-073 Amd 12 mid-spawn drift detection + ADR-082 Amd 17 amendment-slot pre-reservation). race amplification 차단.
- **Costs**: number of spawns ↑ (1 → 3 typically) + coordination complexity ↑ (state passing between spawns) + spawn overhead ↑ (Agent tool invocation cost × 3) + risk of incomplete state transfer between spawns
- **Measurement metric (Phase 2 telemetry carrier deferred — Wave 2 별 sub-CFP)**: spawn time histogram per chief author spawn + per-spawn collision count (mid-spawn drift detection hit rate) + chief author span KPI (median/p95/max minutes per spawn)

**Recommendation tier, NOT mandatory** — chief author 가 monolithic span 채택 시 결격 0 (warning tier 미부착). 단 본 amendment 의 guideline 이 recommendation tier 의 normative anchor — Phase 2 mechanical wire 시 `chief_author_span_minutes` evidence-checks-registry warning-tier 등재 가능 (별 sub-CFP carrier, evidence-gated promote: PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged AND condition).

**§결정 1 / §결정 2 무영향 invariant** (closed enumeration 보존):

- §결정 1 binary always-spawn invariant 무변경 — multi-step spawn 여전히 subagent spawn 의무 (다만 1개 → 3개 sequential)
- §결정 2 inline whitelist 4-entry closed enumeration 무변경 — recommendation tier 가 5번째 entry 신설 아님 (mechanism level recommendation, whitelist level 무관)
- ADR-031 / fix-event-v1 invariant 무변경 — span split 가 ownership 영역 변경 아님

**Disjoint axis with ADR-073 / ADR-082 4-layer defense**:

| Layer | Mechanism | Carrier | 본 Amendment 5 관계 |
|---|---|---|---|
| ADR-073 Amd 11 / ADR-082 Amd 15 | preventive SHA pin (spawn-time 의무) | CFP-1437 (Sub-CFP A) | Sub-CFP D 와 complement — span split 후에도 매 sub-spawn 마다 SHA pin 의무 |
| ADR-073 Amd 12 / ADR-082 Amd 16 | reactive mid-spawn drift detection | CFP-1436 (Sub-CFP B) | Sub-CFP D 와 complement — span split 후에도 매 sub-spawn 안 periodic drift check 의무 |
| ADR-082 Amd 17 | preventive amendment-slot pre-reservation strict claim | CFP-1435 (Sub-CFP C) | Sub-CFP D 와 complement — span split 후에도 첫 skeleton sub-spawn 안 slot pre-reservation 의무 |
| **본 ADR-039 Amd 5 / ADR-044 Amd 3** | **span 자체 축소 (root cause 직접 축소)** | **CFP-1438 (Sub-CFP D)** | **본 amendment — 4-layer defense 마지막 layer (preventive root cause 축소)** |

4-layer defense 완결 (preventive SHA + reactive drift + preventive slot + span decomposition recommendation). Sub-CFP A/B/C = race detection/claim mechanism / Sub-CFP D = race window 자체 축소 (root cause 직접 축소).

**ADR-044 Amendment 3 paired carrier dual-binding** (같은 CFP-1438 Story 안):

- 본 ADR-039 Amd 5 = orchestrator-side spawn span guideline body (recommendation tier, declarative-only Wave 1)
- ADR-044 Amd 3 = team-spec yaml multi-step lifecycle pattern + `chief_author_span` field schema 확장 declarative-only Wave 1 (Phase 2 actual team-spec yaml write = 별 sub-CFP carrier)
- axis disjoint: orchestrator-side (본 ADR) ↔ team-spec yaml (ADR-044) — ADR-064 §결정 1 CFP scope unitary 정합 (2-set paired Amendment)

**META-self-application**: 본 CFP-1438 chief author spawn 자체 = guideline 첫 적용 사례. 본 spawn = skeleton + body + integration 3-step sequentially demonstrate (본 Amendment 작성 자체 = META demonstration).

**Verification evidence**:
- CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach evidence (memory `project_cfp_1318_adr073_amendment_6` 박제 — amendment_number_stale_at_planning 3+ occurrence)
- Sub-CFP A/B/C (CFP-1437/1436/1435) 3-layer race detection/claim complement evidence (각 amendment_log audit trail)
- ADR-073 / ADR-082 disjoint axis 4-layer table 정합 verify
- §결정 1 binary always-spawn / §결정 2 closed 4-entry whitelist 무영향 verify (invariant 보존)


### 결정 18 — Inline whitelist 6번째 entry (merge-time Codex adversarial gate dispatch — Amendment 6, CFP-2458)

§결정 2 의 Inline whitelist 표 (4 original entry + Amendment 2 §결정 15 entry 5 = 현 5-entry) 에 **6번째 entry** append. §결정 15 line 315 exhaustiveness declare ("6번째 inline whitelist entry 추가 = 별도 ADR Amendment 의무 — ADR-058 §결정 5 evidence-gate") 의 충족 carrier.

**Inline whitelist 5-entry → 6-entry 확장 표** (§결정 2 의 4-entry + Amendment 2 entry 5 위 추가):

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 6 | **Merge-time Codex adversarial gate dispatch** (Amendment 6, CFP-2458) | ADR-052 Amendment 15 touchpoint #7 (merge-time adversarial gate) 의 Codex worker dispatch — 구현리뷰 PASS + CI gate PASS 후 "merge gate 진입" 직후 / `gh pr merge` 직전, Orchestrator top-level inline 에서 `codex exec --sandbox read-only < <promptfile>` (ADR-081 D8 file-redirect) 1패스 발동 + result-via-file 수신 | **재귀 가드 회피 critical (H1 게이트 연극화 차단)**. sub-agent / PL 을 게이트 owner 로 두면 ADR-039 platform-inherent 재귀 가드 ("subagent → Agent tool 호출 금지", L474 회피된 대안 C)로 Codex worker spawn 이 silent fallback skip (`subagent_recursion_blocked` fail-mode, ADR-070 Amendment 6) → 게이트 무발동 = 연극화 (Story §4.2 H1 실측 입증). 따라서 dispatch 주체 = Orchestrator top-level inline 고정 의무. dispatch 자체 = read-only adversarial check (verify-before-trust 무조건 적용 — ADR-070 Amendment 9, mismatch finding reject) 이라 §결정 1 "수정 작업" 정의 (file edit / GitHub state change) 와 disjoint axis — file/GitHub mutation 발생 0. 머지 보류·FIX 회부 등 후속 mutation 은 §결정 1/Amendment 2 영역 (별 mechanism). |

**6번째 entry 적용 범위 (closed enumeration)**:

1. **dispatch trigger**: ADR-052 touchpoint #7 (merge-time adversarial gate) 단일 — 다른 6 touchpoint (#1/#3/#4/#6 lane-time) 는 본 entry scope 외 (lane PL/Orchestrator 영역 기존 분류 유지).
2. **dispatch 형식**: ADR-081 D8 file-redirect (`codex exec --sandbox read-only < <promptfile>`) + result-via-file (synchronous block-wait 금지 — CFP-2214 non-blocking 회귀 차단 정합).
3. **mutation 0 invariant**: dispatch 행위 자체 = file write / GitHub state change 미발생 (read-only Codex check). 결과 처리(머지 보류 / FIX Ledger row / phase transition)는 §결정 1 (lane spawn) 또는 Amendment 2 entry 5 (Story-file 4-sub-scope inline) 영역 — 본 entry 와 disjoint.

**§결정 1 binary always-spawn 무손상 (disjoint axis)**:

- §결정 1 "수정 작업" 정의 (file edit / GitHub state change / Story file write / label transition / workflow yaml / ADR write) = 모두 subagent spawn 의무 유지 — 본 entry 는 read-only Codex dispatch mechanism (mutation 0) 만 inline 허용. 수정 작업 영역 spawn 정책 무변경.
- Amendment 2 §결정 15 entry 5 (Story-file handoff 4-sub-scope inline) 무변경.

**ADR-039 Amendment 4 (CFP-1354) 와 disjoint**:

Amendment 4 가 reject 한 "ADR-039 5번째 entry 신설 (rate-limit retry primitive inline)" = retry primitive 영역 (해소 = skill body 위치). 본 entry 6 = merge-time Codex dispatch 재귀 가드 회피 (mechanism 차원, retry 영역 아님). 두 영역 disjoint — Amendment 4 의 closed enumeration 보호 invariant ("future '429 retry inline allowed' 압박 차단") 무손상. 본 entry 는 새 mechanism category (merge-time read-only adversarial dispatch) 의 evidence-gated 신설이지 retry 압박 routing 아님.

**6번째 entry exhaustiveness declare**: 6번째 entry 추가 후 — 7번째 inline whitelist entry 추가 = 별도 ADR Amendment 의무 (ADR-058 §결정 5 evidence-gate). closed enumeration 안정성 보장.

**Verification evidence**:
- Story §4.2 H1 [verified](ADR-039:474 회피된 대안 C "subagent → Agent tool 호출 금지") — subagent owner 면 재귀 가드 silent skip = 게이트 연극화 실측 입증
- ADR-070 Amendment 6 `subagent_recursion_blocked` fail-mode (CFP-1041 DesignReviewPL subagent context Codex spawn 차단 evidence) — 동형 재귀 가드 fail-mode precedent
- ADR-052 Amendment 15 touchpoint #7 (merge-time adversarial gate) dispatch 주체 = Orchestrator top-level inline 정합 verify
- §결정 1 binary always-spawn / Amendment 2 entry 5 무영향 verify (invariant 보존)


### 결정 19 — Story-teammate = lead 위임 per-Story Orchestrator (spawn scope 단위 위임 — Amendment 7, CFP-2488)

§결정 1 의 "Orchestrator-only spawn" 불변식을 **폐기가 아니라 "Story scope 단위 위임"으로 재정의**한다. lead (top-level Claude 세션, ADR-009 Orchestrator) 가 적격 Story 별로 **Story-teammate** (background-Agent, SendMessage-addressable Story-runner) 를 dispatch 하고, 각 Story-teammate 는 **자기 Story scope 안에서만** lane PL subagent 를 spawn 한다. 이것이 ADR-134 (병렬 적격성 5조건 + merge-time 재검증 + Orchestrator per-Story dispatch) 의 **spawn-권한 layer** 다.

본 §결정은 **spawn-scope 위임 축** 이며, §결정 2 의 **inline vs spawn mechanism 축** 과 disjoint 다 (§아래 "§결정 2 closed inline whitelist 무손상" 참조). 따라서 inline whitelist 6-entry (4 original + entry 5 Amd2 + entry 6 Amd6) 는 본 amendment 로 **변경 0** — 본 amendment 는 7번째 inline whitelist entry append 가 **아니다**.

**dispatch 메커니즘 = background-Agent-as-Story-runner (검증된 경로)**:

dispatch 주체 = lead 가 `Agent` tool 로 spawn 한 background-Agent (run_in_background, SendMessage 로 addressable). 이 background-Agent 는 depth-0 독립 세션이므로 **자기 sub-agent tree 를 보유**한다 (lane PL → SubAgent fan-out). 본 Epic (CFP-2481 Phase A) dogfood 세션이 이 경로를 **실증**했다: Orchestrator → PL → sub-agent 의 depth 0 → 1 → 2 spawn 이 실작동 (요구사항-리뷰 §9 advisory 가 "agent-teams teammate 가 lane PL spawn 가능?"을 공식문서 UNVERIFIABLE 로 판정했으나, 본 세션 실증으로 **go/no-go = PASS** 전환 — ADR-119 검증-후-단언 정합).

- **공식문서 의존 회피 명시**: 본 §결정은 공식문서가 명시적으로 보장하는 **background-Agent → 자기 sub-agent spawn** 경로에만 의존한다. 공식문서가 침묵하는 agent-teams "teammate" 특정 dispatch 경로 (teammate semantic 으로서의 spawn 권한) 에는 의존하지 않는다 — 검증된 경로로 메커니즘을 확정 (over-claim 차단).
- **go/no-go 결론**: 거짓이었으면 요구사항 lane 재진입이었으나, 실증으로 PASS. 단 아래 stall 마찰을 본 ADR 가 인정·처리한다 (검사연극 금지 — 마찰 은폐 금지).

**2-level 토폴로지 (closed)**:

- **lead 1 + teammate N** — lead (top-level Claude 세션) 가 유일 dispatch 주체. Story-teammate 는 자기 Story scope 안에서 lane PL → SubAgent 를 spawn (depth 0→1→2).
- **teammate → teammate spawn 불가 (lead 고정)** — Story-teammate 가 다른 Story-teammate 를 spawn 하는 것은 금지. 이것이 산업 lead-worker 패턴의 **bounded 1-level 위임** 이며, 무한 재귀 중첩 (회피된 대안 D — Model A) 과 구분된다 (Story §6.3 [verified] WebSearch — resource-aware concurrency limit 이 걸린 bounded 위임).
- **scope-confine = Orchestrator-only 명목 보존** — teammate 의 spawn 권한은 "lead 가 confine 한 Story scope" 안에서만 유효. 즉 "Orchestrator(lead) 만 spawn 위임 권한 보유" 불변식은 보존되고, teammate 는 그 위임을 받아 자기 scope 안에서 실행하는 delegate 다 (ADR-039 §결정 3 Ownership ≠ Mechanism 분리 정합 — lead 가 위임한 spawn 행위의 ownership identity = lead).

**stall 마찰 정직 기술 (구조적 한계 — 은폐 금지)**:

본 dispatch 토폴로지는 1개 구조적 마찰을 동반하며, 이를 ADR 가 인정·처리한다:

- **마찰**: child (손자 = Story-teammate 가 spawn 한 lane PL 의 SubAgent) 완료 통지가 그 parent (lane PL) 가 아닌 **lead (main)** 로 surface 되는 경우 → parent (lane PL) 는 오지 않는 통지를 기다리며 무한대기 (stall). 본 Epic dogfood 세션에서 firsthand 관찰됨 (findings §dogfood 마찰).
- **처리 책임 (dispatch 운영절차 — playbook §4.5 + ADR-134 carrier)**: lead 는 dispatch 한 모든 teammate 의 진행을 **능동 모니터** 하고, stall 검출 시 **force-resume (SendMessage 로 parent 깨우기) 또는 TaskStop (회수)** 책임을 진다. 이 책임은 옵션이 아니라 dispatch 운영절차의 의무 단계 — 마찰을 메커니즘으로 완전 제거하지 못함을 정직히 기술하고 (ADR-119 검사연극 금지), lead 능동 감독으로 흡수한다.
- **Phase A 위험 흡수 (위험 A 수동감독)**: E2 (sentinel mechanical wire) / E3a·E3b (atomic claim) 가드가 아직 LIVE 가 아니므로, Phase A 병렬은 lead 의 사람-수동-감독 + ADR 번호 사전 예약 (132/133/134 lapse 흡수) 으로 위험을 흡수한다. 본 §결정의 stall 처리 책임이 그 수동 감독의 codify 다.

**§결정 2 closed inline whitelist 무손상 (disjoint axis)**:

- §결정 2 inline whitelist (4 original entry + Amendment 2 §결정 15 entry 5 + Amendment 6 §결정 18 entry 6 = 현 **6-entry**) 는 본 amendment 로 **변경 0** (`git diff` 로 §결정 2 블록 + §결정 15/18 entry append-only 회귀 확인 가능).
- **disjoint 근거**: inline whitelist 는 "Orchestrator 가 inline 으로 수행할까 vs subagent spawn 할까" (mechanism 차원) 를 다룬다. 본 §결정 19 는 "spawn 권한을 누구에게 위임할까" (spawn-scope 차원) 를 다룬다 — 두 축은 직교. 본 §결정은 teammate 에게 inline 수행 권한을 주지 않는다 (teammate 도 자기 scope 안에서 lane PL 을 **spawn** 한다, inline 대체 아님 → §결정 1 binary always-spawn 정합).
- **선례 정합**: Amendment 4 (CFP-1354) 가 "ADR-039 5번째 inline entry 신설 REJECTED" 로 closed enumeration 을 보호한 패턴과 정합 — 본 amendment 도 inline whitelist 를 확장하지 않는다 (spawn-scope 위임은 별 축).

**§결정 1 binary always-spawn 무손상**:

- §결정 1 "수정 작업 = subagent spawn 의무" 무변경. 위임받은 Story-teammate 도 자기 Story scope 안 수정 작업을 **subagent spawn 으로 수행** (lane PL → SubAgent) — inline 우회 아님.
- §결정 5 lane plugin 0 변경 invariant 무손상 — lane PL / 6 SubAgent / inter-plugin contract 변경 0. 본 §결정은 lead↔teammate dispatch 토폴로지만 codify, lane plugin 내부 행위 무변.
- ADR-031 §14 lane evidence + fix-event-v1 §10 Orchestrator monopoly 무손상 — dispatch 토폴로지 변경이 ownership 영역 변경 아님 (lead 가 위임 주체로 유지).

**ADR-009 amends 관계 정합**:

ADR-009 "wrapper agent 0 → Orchestrator 가 모든 work spawn" 원칙과 모순 없음 — "Orchestrator 가 모든 work spawn" 은 "Orchestrator 가 spawn 위임의 단일 권위" 로 정합 확장된다. Story-teammate 는 lead 가 Story scope 단위로 위임한 delegate 이며, lead 밖에서 자생적 spawn 권한을 갖지 않는다 (2-level bounded, teammate→teammate 불가).

**Verification evidence**:
- 본 Epic (CFP-2481 Phase A) dogfood 세션 firsthand 실증 — background-Agent (depth-0, SendMessage-addressable) → 자기 sub-agent spawn (depth 0→1→2) 실작동 (findings §dogfood 마찰 + go/no-go 재평가)
- 요구사항-리뷰 §9 advisory UNVERIFIABLE → dogfood 실증 PASS 전환 (ADR-119 검증-후-단언)
- Story §6.3 [verified] (WebSearch — 산업 lead-worker bounded 1-level 위임 + resource-aware concurrency limit 표준)
- §결정 1 binary always-spawn / §결정 2 closed inline whitelist 6-entry / §결정 5 lane plugin 0 변경 무영향 verify (invariant 보존)
- ADR-134 (병렬 적격성 + merge-time 재검증 + per-Story dispatch) sibling 정합 — 본 §결정 = ADR-134 의 spawn-권한 layer carrier

### 결정 20 — background subagent spawn liveness (ADR-139 cross-ref — Amendment 10, CFP-2549)

lead 가 background subagent/worker 응답을 대기할 때의 **유한성(liveness)** = §결정 19 (lead force-resume/`TaskStop` 개입 축)의 **정량 mechanical 게이트화**다. 원리 carrier SSOT = [ADR-139](ADR-139-background-wait-liveness-gate.md) (background-wait liveness gate). 본 §결정 20 = ADR-039 spawn-권한 기반 cross-ref — 게이트 소유 = Orchestrator/lead 고정(INV-L4)이 ADR-039 §결정 1/§결정 19 의 spawn-권한 위임 topology 에 근거함을 명시한다.

**ADR-139 4 불변식 (INV-L1~L4) 상속**:

- **INV-L1 (wall-clock ceiling 존재)** — background subagent 대기 지점에 명시적 max-wait 상한 (암묵 무한 금지). stall 판정 = outcome ground-truth 기반 (internal proxy loop-lag/CPU 금지, ADR-119 §결정 10 ① 상속).
- **INV-L2 (fail-open 금지)** — stall = inconclusive (PASS 자동승격 금지, PASS-only-if-explicit). 부분 stall → ANY(inconclusive) → 전체 inconclusive.
- **INV-L3 ("0-byte ≠ stall" 3-state marker)** — wall-clock ceiling + progress-marker (output mtime + content grep + task-notification). 0-byte stdout 단독 stall 단정 금지.
- **INV-L4 (게이트 소유 = Orchestrator/lead 고정)** — worker 자가-spawn 금지 (`plugins/codeforge-review/CLAUDE.md:46`). 값 순서 불변식 `timeout N < liveness max-wait`. **이 소유 고정이 ADR-039 spawn-권한 근거** — §결정 1 binary always-spawn + §결정 19 lead 위임 topology 에서 게이트 개입 주체 = lead 로 귀결 (대기 주체 ↔ 판정 주체 분리, worker self-attestation 차단).

**§결정 19 body 무변경 (본 §결정 20 = 정량 게이트화 cross-ref append)**:

§결정 19 의 "lead force-resume(SendMessage)/TaskStop 책임" 은 정성 기술이다. 본 §결정 20 = 그 개입 축을 ADR-139 4 불변식 (wall-clock 상한 + progress-marker 관측 + fail-open 금지 + re-dispatch max-retry cap 2) 로 정량화하는 cross-ref 이며, §결정 19 body 자체는 변경하지 않는다.

**§결정 9 slot 미침범 (disjoint axis — ADR-139 거절된 대안 E)**:

§결정 9 deferred slot = "Orchestrator inline write detect hook (PreToolUse on Write/Edit/mcp__github__*)" = **inline-write-detect 축** (Orchestrator 가 직접 mutation 하는지 감지). 본 §결정 20 = **background-wait liveness (완료 감지) 축** — 대기 *중* subagent 가 살아있는지 판정. 두 축은 완전 별개다. background-wait liveness 를 §결정 9 에 밀어넣으면 scope 오염 → 이후 진짜 inline-write-detect hook (Amendment 8/9 이 실현 중) 과 confusion. 따라서 본 원리는 §결정 9 를 **채우지 않고** 신규 §결정 20 으로 분리한다.

**§결정 2 inline whitelist 6-entry 무손상 (disjoint axis)**:

- §결정 2 inline whitelist (4 original + entry 5 Amd2 + entry 6 Amd6 = 현 **6-entry**) 는 본 amendment 로 **변경 0**. background-wait liveness 게이트는 "Orchestrator inline vs subagent spawn" (mechanism 차원) 이 아니라 "대기 중 subagent liveness 판정" (완료-감지 차원) 을 다룬다 — 7번째 inline whitelist entry append 아님.
- §결정 1 binary always-spawn 무변경 — background subagent 대기 대상 = 이미 spawn 된 subagent 의 응답이며, spawn 의무 자체와 무관.

**Verification evidence**:

- ADR-139 §컨텍스트 firsthand — lane PL background-yield 후 parent 무한 정지 / DeveloperAgent 0-byte output → stall 오판 / 본 CFP-2549 설계 lane ArchitectPL 6 deputy fan-out 후 4 deputy 가 lead 로 delivery-gap surface (stall 자기 재현)
- §결정 1 binary always-spawn / §결정 2 closed inline whitelist 6-entry / §결정 9 inline-write-detect slot / §결정 19 body 무영향 verify (invariant 보존)
- ADR-139 (background-wait liveness gate carrier SSOT) + ADR-081 Amendment 13 (§D14 companion first-instance cross-ref) sibling 정합 — 본 §결정 20 = ADR-139 §결정 6 sibling Amendment set (ADR-039 = spawn-권한 기반 게이트 소유 layer)


## 회피된 대안

### 대안 A — Selective inline (Anthropic 공식 권장)

Anthropic 공식 (`https://www.anthropic.com/engineering/claude-code-best-practices`) 의 "side task that would flood main conversation" criterion 기반 selective spawn.

**거부 이유**:
- 사용자 verbatim "무조건" directive 와 정면 충돌 (Story §1)
- "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 = 본 ADR motivation 의 user-stop 발화 채널 (ADR-025 §결정 7 sub-decision stop). selective spawn 정책 = 분기 자체 보존 → user-stop 회피 motivation 미충족
- selective criterion 의 정량 boundary 부재 ("flood" 정의 모호) → 매번 분기 발화

채택 = §결정 1 binary always-spawn.

### 대안 B — 즉시 hook enforcement (Phase 1 부터)

PreToolUse hook 으로 Orchestrator 직접 Write / Edit / mcp__github__\* 호출 detect → 즉시 차단.

**거부 이유**:
- ADR-025 / ADR-029 의 Phase 1 trust model precedent 위반 (doc-only / enforcement 후속 CFP)
- spawn latency 정량 데이터 부재 (Researcher §6.F fact gap) → false-positive 위험 (legitimate Read 행위 차단)
- §결정 2 Inline whitelist 4-entry 의 mechanism level boundary 가 hook code level 에서 정확 detect 불가능 (예: Read 가 Q&A 답변용인지 수정 작업의 일부인지 mechanism level 모호)

채택 = §결정 8 Phase 1 doc-only + §결정 9 Phase 2 deferred.

### 대안 C — Lane plugin 측 적용

6 lane plugin agent 자체에 spawn 의무 stamping (lane plugin 내부 행위도 spawn 으로 강제).

**거부 이유**:
- ADR-009 wrapper-only decomposition scope 위반 — wrapper Orchestrator 만 spawn 권한 invariant. Lane plugin agent 는 self-write boundary 안에서 자체 Edit / Read 호출 — 재귀 spawn limit 와 직접 충돌 (subagent → Agent tool 호출 금지, CLAUDE.md "플랫폼 제약")
- 본 ADR motivation = Orchestrator user-stop 회피. Lane plugin agent 는 user-stop 발화 채널 아님 (subagent one-shot return)

채택 = §결정 5 lane plugin 0 변경.

### 대안 D — Model A: 무제한 재귀 teammate spawn (Amendment 7 reject)

병렬 dispatch 시 Story-teammate 가 다시 다른 Story-teammate 를 spawn 할 수 있게 허용 (무한 재귀 중첩 토폴로지 — teammate→teammate→teammate ...). 또는 agent-teams "teammate" semantic 의 공식문서 미보장 dispatch 경로에 메커니즘을 의존.

**거부 이유**:
- **무한 재귀 = resource 폭주 위험** — 산업 lead-worker 표준은 bounded 1-level 위임 + resource-aware concurrency limit 으로 over-spawning 을 차단한다 (Story §6.3 [verified] WebSearch). 무제한 재귀는 quota (Anthropic API rate limit) 선형↑ 를 넘어 지수 폭주 + stall 마찰 깊이 증폭 (손자→증손자 통지 surface 경로 더 깊어짐).
- **ADR-009 단일 spawn 권위 희석** — teammate 가 자생적으로 무한 spawn 권한을 가지면 "Orchestrator(lead) 가 spawn 위임의 단일 권위" 불변식이 깨진다. §결정 19 의 scope-confine (lead 가 confine 한 Story scope 안에서만) 이 이 권위를 보존한다.
- **공식문서 미보장 경로 의존 = over-claim** — agent-teams "teammate" 특정 spawn 경로는 공식문서 침묵 (요구사항-리뷰 §9 UNVERIFIABLE). 검증된 background-Agent → 자기 sub-agent spawn 경로 (dogfood 실증) 로 메커니즘을 확정하는 것이 ADR-119 검증-후-단언 정합.

채택 = §결정 19 Model B (2-level bounded 위임 — lead 1 + teammate N, teammate→teammate 불가).

## 외부 fact (Researcher §6 reference)

본 ADR 의 §결정 정당화 + 회피된 대안 reject 근거의 외부 데이터:

1. **Anthropic multi-agent research system** — https://www.anthropic.com/engineering/multi-agent-research-system
   - Multi-agent ≈ 15× 토큰 vs single-agent chat (Anthropic 자체 측정)
   - 90.2% performance lift on multi-step research benchmark (vs single-agent baseline)
2. **Anthropic Claude Code best practices** — https://www.anthropic.com/engineering/claude-code-best-practices
   - "Side task that would flood main conversation" criterion (selective spawn 권장)
   - 본 ADR = stricter binary policy (always-spawn) — 진영 위치 codify 필요
3. **Anthropic Claude Code subagent docs** — https://docs.claude.com/en/docs/claude-code/sub-agents
   - one-shot semantics / continuous dialog 불가능 → §결정 2 Inline whitelist entry 1 의 mechanism rationale source
4. **Anthropic Claude Code metrics blog** — https://www.anthropic.com/news/claude-code (auto-mode 정당화 근거)
   - 93% approve rate / 17% false-negative — Orchestrator user-stop 회피 motivation 정합

**Fact gap (Researcher §6.F 명시)**:
- spawn latency 정량 데이터 부재 (Anthropic 정성 언급만) — Phase 2 측정 의무
- "always-spawn" binary 정책 학계/산업 case study 검색 0건 — wrapper-specific design choice (debut audit measurable signal)

## 검증 채널

Phase 1 trust model 의 검증 채널 = doc lint (TestContractArchitect §8.4 산출물 verbatim — Change Plan §8.4):

1. **Spawn-default presence lint** — 4 SSOT doc (playbook §3.0 / CLAUDE.md "Default subagent context" / consumer-guide § "Subagent default" / hotfix-playbook 1줄) 의 ADR-039 cross-ref 존재 검증 (`scripts/check-doc-section-schema.sh` 확장 또는 신규 lint script).
2. **Branch-logic absence lint** — playbook / CLAUDE.md / consumer-guide 안 "inline 으로 충분" / "trivial 이면 inline" / "subagent 가 나은가" 류 결정 분기 prompt 부재 검증 (grep deny-list).
3. **ADR-039 frontmatter schema 정합** — `amends: ADR-009` / `category: orchestration-discipline` / `status: Accepted` / `carrier_story: CFP-275` 필드 존재 검증.
4. **Cross-reference lint** — ADR-039 본문 + Change Plan §5 / §3 의 ADR-009 / ADR-025 / ADR-029 / ADR-031 cross-ref 존재 검증.
5. **Story §11 retro append schema 정합** — Phase 2 PR merge 후 PMOAgent retro append 시 schema 검증.

**현재 Phase 1 PR scope 안 lint 도입** = 후보 1 + 후보 2 만 (가능하면). 후보 3-5 = follow-up CFP.

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` (본 file)
- `docs/change-plans/cfp-275-orchestrator-subagent-default.md` (implementation plan)
- `docs/orchestrator-playbook.md` §3.0 신설 (B1 HIGH)
- `CLAUDE.md` "오케스트레이션 규칙" § "Default subagent context (수정 작업)" 1 paragraph (B2 HIGH)
- `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" 신규 subsection (B5 HIGH)
- `docs/hotfix-playbook.md` 1줄 추가 (AC-13)
- `docs/domain-knowledge/orchestrator-discipline/spawn-default.md` (DomainAgent draft commit)

### 비-영향

- 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) 변경 없음 (§결정 5 lane plugin 0 변경 invariant)
- Inter-plugin contract 6 (requirements_output / design_output / review_verdict v3 / test_verdict / develop_output / pmo_output) 변경 0건
- design lane 6 SubAgent + 2 CONDITIONAL SubAgent 변경 0건
- Stop discipline (ADR-025) 5 종 whitelist 무변 — 본 ADR 는 stop 발생 가능성을 줄이는 mechanism 이지 whitelist 자체를 변경 X
- ADR-031 §14 lane evidence write monopoly 무변 (ownership 무변, §결정 3 mechanism 분리)
- Story §10 FIX Ledger Orchestrator monopoly 무변 (ownership 무변)
- TodoWrite 흐름 무변 (§결정 2 Inline whitelist entry 2 — TodoWrite tool surface 자체 standalone 정당화, ADR-038 informational reference 만, normative dep 아님)

### Reversibility

- Yes — 본 ADR `status: Deprecated` 전환 + 영향 file revert 시 ADR-009 + ADR-025 기존 enforcement 강도 복원
- ADR-022 → ADR-035 precedent 패턴 (status flip + Deprecated marker + 회피 doc edit)

## Out-of-scope

- Phase 2 enforcement (hook / telemetry / stop-event-v1 ledger) — §결정 9 deferred
- 6 lane plugin agent 의 spawn 의무 stamping — §결정 5 lane plugin 0 변경 invariant 위반
- ADR-022 본문 잔재 cleanup — CFP-137 / CFP-134 follow-up
- Skill 호출 / Glob / Grep / Read tool 분류 enum 확장 — §결정 2 closed 4-entry 위반 (Refactor B3 over-engineering 회피)
- spawn cost ROI 분석 / 정량 boundary 도입 — Phase 2 deferred
- Multi-Story / Epic-level continuity 흐름 변경 — ADR-025 Amendment 1 무손상

## 관련 ADR

- **ADR-009** (wrapper-only decomposition) — **amends** 관계. 본 ADR = ADR-009 의 자연 확장 / explicit 격상.
- **ADR-025** (stop discipline + Epic-level continuity) — motivation. §결정 7 의 `policy_violation_subdecision` sub-class "이거 inline 으로 충분한가" stop 을 mechanism level 에서 제거. 5 종 whitelist 무변.
- **ADR-029** (phase execution visibility) — narration interaction. 매 subagent spawn / return 가 narrate 대상. Orchestrator stderr narration 의무 보존.
- **ADR-031** (lane-spawn evidence trail) — §14 row append ownership 무변, mechanism 만 spawn (§결정 3). **Amendment 1** 본 ADR carrier Story 안 commit 동반 (§결정 12) — Orchestrator-owned delegate subagent 가 self-write 정의에 포함됨 명시.
- **ADR-035** (codeforge agent teams Epic) — subagent semantics 분기. 본 ADR 의 "subagent" = default subagent context (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`) 의 one-shot subagent. Agent teams enabled context (CFP-137 deferred) 는 본 ADR 의 default 분기 외 — agent teams 활성 시에도 본 정책의 spawn 의무 유지, dialog 가능성만 확장.
- **ADR-134** (병렬 적격성 5조건 + merge-time 재검증 + Orchestrator per-Story dispatch) — **§결정 19 (Amendment 7) sibling**. ADR-134 = 병렬 dispatch 정책 SSOT, 본 ADR §결정 19 = 그 spawn-권한 layer (Story-teammate = lead 위임 per-Story Orchestrator, 2-level bounded 토폴로지). 두 ADR 은 CFP-2488 (Epic CFP-2481 Phase A E1) 안 paired carrier — ADR-134 가 적격성·merge-time·dispatch 운영절차를, 본 ADR §결정 19 가 spawn 권한 위임을 담당 (axis disjoint).
- **ADR-038** (progress visualization TodoWrite) — informational reference. 본 ADR 의 §결정 2 Inline whitelist entry 2 (TodoWrite scratchpad) 의 normative 정당화는 TodoWrite tool surface 자체 (file system / GitHub state mutation 미발화) 에서 standalone 도출 — ADR-038 normative dependency 아님 (PR merge order 무관, P0-1 fix).
- **ADR-022** (Sonnet decider 5-trigger 자동 발동) — **Deprecated by ADR-035** (CFP-134 / ADR-035, 2026-05-08). 본 ADR 시행 후 Sonnet 자동 dispatch 부재 — 사용자 ad-hoc 호출 시에도 Sonnet 호출 자체가 subagent spawn (Agent tool with `model:sonnet`) 이므로 자연 정합 (§결정 11).
- **ADR-013** (codeforge family dogfood-out policy) — spec / plan 위치 internal-docs override. 본 ADR Story spec / plan 도 internal-docs SSOT.
- **ADR-024** (Story-scoped branch policy) — 본 Story branch 명명 (`cfp-275-orchestrator-subagent-default`).
- **ADR-005** (plugin meta exempt) — N/A lane 사유 reference (Change Plan §7 / §11 / §8.5 N/A).

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/orchestrator-playbook.md` §3.0 (신설 — Phase 1 scope, §결정 13)
- `CLAUDE.md` "오케스트레이션 규칙" § "Default subagent context (수정 작업)" (Phase 1 scope, §결정 13)
- `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" (Phase 1 scope, §결정 13)
- `docs/hotfix-playbook.md` (1줄 ADR-039 cross-ref, Phase 1 scope, §결정 13)
- `docs/domain-knowledge/orchestrator-discipline/spawn-default.md`
- `docs/change-plans/cfp-275-orchestrator-subagent-default.md`
- `docs/adr/ADR-031-lane-spawn-evidence-trail.md` (Amendment 1, §결정 12)
- `docs/inter-plugin-contracts/fix-event-v1.md` (Amendment, §결정 12)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-275.md`
- `mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-275-*.md` (Researcher / DomainAgent / Analyst output SSOT)
