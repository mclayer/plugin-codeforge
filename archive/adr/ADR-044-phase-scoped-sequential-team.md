---
adr_number: 44
title: Phase-scoped sequential team SSOT (CFP-134 Epic Wave 2)
date: 2026-05-09
status: Proposed
category: orchestration
carrier_story: CFP-137
parent_epic: CFP-134
supersedes: null
amends: null
related_stories:
  - CFP-134
  - CFP-135
  - CFP-136
  - CFP-137
  - CFP-139
  - CFP-391  # Amendment 1 (2026-05-11) — dispatch_mode auto_on_divergence 추가
  - CFP-2521  # Amendment 5 (2026-06-30) — §결정 11 thin-PL context boundary mandate
  - CFP-2597  # Amendment 6 (2026-07-10) — §결정 12 check-verification-floor.sh 축③ (peer-completion falsifiability)
amendment_log:
  - date: 2026-05-11
    cfp: CFP-391
    summary: "§결정 2 dispatch_mode enum 에 auto_on_divergence 추가. ADR-059 carrier debate-protocol-v1 자동 발동 mode."
    affected_sections: ["§결정 2"]
    breaking: false
  - date: 2026-05-24
    cfp: CFP-1354
    summary: |
      team-spec yaml 7 file schema 확장 — `parallel_spawn_cap: int` (default 7, derived from parallel-dispatch-protocol-v1 §6.2 worker_count_max single SSOT cross-ref bind) + `spawn_stagger_ms: int` (optional, default 0 — no stagger, opt-in tunable) + `cascade_circuit_breaker: bool` (optional, default false) 3 field 신설. 7 team-spec yaml atomic sibling sync (ADR-010 §결정 2 kind:contract sibling sync 정합).
      Story A (CFP-1354) Phase 1 PR scope. 사용자 발화 verbatim "Server is temporarily limiting requests" (Story §1, story-section-1-immutable 강제) 의 in-process axis — Anthropic infra 429 burst 영역 surgical cap codify. ADR-109 (in-process 429 mitigation framework SSOT) §결정 4 circuit breaker 3-window AND + §결정 8 telemetry §14 Lane Evidence marker / KPI dual-tier cross-ref carrier. RefactorAgent interface 분리 권고 정합 — parallel-dispatch-protocol-v1 §6.2 worker_count_max single SSOT 와 cross-ref bind (중복 신설 0 anti-pattern guard).
      Phase 2 PR scope = 7 team-spec yaml actual schema write (`templates/team-spec-decompose.yaml` + `templates/team-spec-requirements.yaml` + `templates/team-spec-design.yaml` + `templates/team-spec-design-review.yaml` + `templates/team-spec-develop.yaml` + `templates/team-spec-code-review.yaml` + `templates/team-spec-security-test.yaml`). 본 Amendment = Phase 1 declarative declare only.
    affected_sections: ["§결정 7 team-spec yaml SSOT (schema 확장)"]
    breaking: false  # additive only (3 optional field with default), backward-compat invariant 보존
    direction: strengthening  # cap field 추가 = 강화 방향
    sunset_justification: |
      Story A 가 429 burst 영역 surgical cap 의무 codify. parallel-dispatch-protocol-v1 §6.2 worker_count_max single SSOT 와 cross-ref bind (중복 신설 0, RefactorAgent interface 분리 권고 정합). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (cap field 추가, 본문 §결정 7 sequential team SSOT 무변경 schema additive), 약화 0건.
  - amendment: 3
    date: 2026-05-24
    cfp: CFP-1438
    summary: |
      §결정 9 신설 (Multi-step chief author pattern recommendation) + team-spec yaml schema 확장 declarative (Wave 1 declare only — Phase 2 actual yaml write = 별 sub-CFP carrier).
      Multi-step chief author pattern = chief author (특히 Opus tier) 의 단일 monolithic spawn (15-40min wide drift surface) → skeleton + body + integration 3-step sequential smaller spawn (~5-7min each) 권장. team-spec yaml `chief_author_span` field schema 확장 (optional, default null = unspecified / values: monolithic | multi_step_3 | multi_step_N) — declarative Wave 1 only, Phase 2 actual write = 별 sub-CFP carrier. ADR-039 Amendment 5 paired carrier dual-binding 같은 CFP-1438 Story 안 2 ADR paired Amendment axis disjoint complement 2-set ADR-064 §결정 1 CFP scope unitary 정합 (본 ADR-044 = team-spec yaml multi-step lifecycle pattern / ADR-039 = orchestrator-side spawn span guideline body).
      Sub-CFP D of CFP-1389 Wave 1 declarative-only carrier — paired sibling of Sub-CFP A CFP-1437 (preventive SHA pin Amd 11/15) + Sub-CFP B CFP-1436 (reactive mid-spawn drift detection Amd 12/16) + Sub-CFP C CFP-1435 (preventive slot reservation strict claim Amd 17) = 4-layer defense forcing function 완결 (preventive SHA + reactive drift + preventive slot + span decomposition recommendation). CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach evidence root cause 한 측 = chief author monolithic span = wide drift window root cause.
      §결정 1 phase-scoped sequential team lifecycle invariant 무변경 + §결정 7 team-spec yaml SSOT additive only (chief_author_span field optional, backward-compat 보존). amendment_log format = numbered `amendment: 3` form 첫 도입 (이전 CFP-391 + CFP-1354 = date-form, 본 Amendment 3 부터 numbered convention 채택 — ADR-039 numbered amendment_log convention 정합 alignment).
    affected_sections: ["§결정 9 (신설 — multi-step chief author pattern)", "§결정 7 team-spec yaml SSOT (schema 확장 declarative)"]
    breaking: false  # additive only (chief_author_span field optional with default null), backward-compat invariant 보존
    direction: strengthening  # recommendation tier 추가 = 강화 방향
    sunset_justification: |
      CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach evidence root cause 한 측 (chief author monolithic span = wide drift window) 의 root cause 직접 축소 carrier. Sub-CFP A/B/C 가 race detection/claim mechanism complement, 본 Sub-CFP D = race window 자체 축소 (root cause 직접 축소). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (multi-step pattern recommendation + team-spec yaml schema additive), 약화 0건. carrier_story CFP-1438 = ADR-039 Amendment 5 + ADR-044 Amendment 3 paired sibling amendment 2-set (axis disjoint).
  - amendment: 4
    date: 2026-06-30
    cfp: CFP-2471
    summary: |
      §결정 10 신설 (lane verification floor 정합 — Codex ad-hoc ceiling 보존 명문). Epic CFP-2468 Track W / W3 (lane 검증 균질성 강제) carrier. §결정 2 (Codex ad-hoc-only / default roster = PL + Claude worker) 위에 얹히는 정합 amendment — 검증 floor = ≥1 independent peer (SoD: implementer ≠ certifier), Codex 는 floor 아닌 ceiling 임을 명문화. 4 정합 결정:
      (a) 검증 floor = ≥1 independent peer (SoD). floor 충족자 = ClaudeReviewAgent (default roster 상존). Codex = cross-model diversity ceiling — §결정 2 ad-hoc-only 와 disjoint·무충돌 (floor ≠ Codex 강제).
      (b) dual-peer 2→1 degrade = honest (ADR-094 §결정 1 (c) 동형 — degraded mode 작동 + 가시 marker/사유 강제 기록, silent 금지). silent 2→1 = 게이트 차단 대상.
      (c) review-pl-base.md:574 "CodexReviewAgent 미설치 시 lane 진입 불가·SKIPPED 불허" = "**silent degrade 금지**" 의미로 재해석 (single-peer honest degrade = 정식 floor 충족, 진입 불가 아님). team-spec-code-review.yaml:33-39 (default single-peer, Codex user_request_only) 와의 firsthand 문서 모순을 single-peer floor + Codex ceiling 방향으로 정합.
      (d) concept doc `docs/domain-knowledge/concept/lane-verification-floor.md` (CFP-2471 Phase 1 landed) + (Phase 2 예정) review-verdict-v4 degrade marker (additive MINOR) cross-ref. 축③ deputy/role:dev fan-out enforcement (PreToolUse Agent matcher) = 정확 matcher 토큰 + CLI 런타임 발동 미확정 (요구사항리뷰 P2) → enforcement 활성 채택 전 empirical 확인 전제조건 (settled 단정 금지).
      §결정 1 phase-scoped sequential team lifecycle invariant 무변경 + §결정 2 dispatch_mode SSOT 무변경 (재해석·정합만, Codex ad-hoc-only 약화 0건). Phase 2 mechanical wire (review-pl-base 정합 + verdict-v4 MINOR bump + check-verification-floor / check-lane-evidence 축③ + workflow + hook) = 별 carrier (본 Amendment = Phase 1 declarative 정합 declare).
    affected_sections: ["§결정 10 (신설 — lane verification floor 정합)", "§결정 2 (재해석 cross-ref, 본문 무변경)"]
    breaking: false  # 재해석·정합만 (Codex ad-hoc-only 결정 약화 0건), review-pl-base/team-spec 모순 해소 방향만 명문
    direction: strengthening  # 검증 floor 명문화 + silent degrade 차단 = 강화 방향
    sunset_justification: |
      mctrader (첫 비-dogfood consumer) 데뷔 감사 evidence — fidelity-critical 코드 2-peer 없이 self-audit 머지 + dual-peer silent degrade + deputy fan-out 미spawn. "검증이 가장 필요한 곳에서 빠지는" 동일 class 결함의 강제력 복구 (Track M 교정 토대). ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (floor 명문 + honest degrade + 문서 모순 정합), 약화 0건. §결정 2 Codex ad-hoc-only 는 무손상 (floor=Claude peer, Codex=ceiling 으로 disjoint axis 확정).
  - amendment: 5
    date: 2026-06-30
    cfp: CFP-2521
    summary: |
      §결정 11 신설 (Thin-PL context boundary mandate — lane-PL READ/COMPUTE 경계 codify). lane-PL synthesizer lifecycle 안 PL 의 **READ/COMPUTE 경계** (어떤 파일을 PL 이 직접 읽어 컨텍스트에 보유하나) 를 1급 mandate 로 codify. **신규 원칙 아님** — 이미 stated 된 thin-synthesizer invariant (DeveloperPLAgent.md:269 "PL은 synthesizer 유지" + 본 ADR §결정 1 lane-PL lifecycle + ADR-039 §결정 3 Ownership≠Mechanism) 의 enforcement/codification. 동인 = DeveloperPL 비용 진단 (CFP-2521 §1 측정) — 비용 94%=컨텍스트 보유, 그 97%=PL 직접 read, worker 합성 1.4%. PL 이 thin synthesizer 가 아닌 fat self-implementer 로 동작 (설계-런타임 gap). 4 결정:
      (a) **PL self-do 금지** — PL 은 비-essential 경로 (docs/stories 밖 plugin.json/scripts/*.yaml/playbook) 를 직접 Read/Bash 하지 않고 worker 요약으로만 보유. tier = **prompt-mandate (behavioral)** — permission-enforced Read-deny 아님 (Read path-scoping 은 agent frontmatter 에서 UNVERIFIED-IN-PRACTICE — fleet-wide Read(path) entry 0건 firsthand, 공식문서는 settings.json 존재만 확인 subagent honor 미확인). ADR-039 §결정 8 doc-only trust 선례 상속. permissions.allow Read/Grep/Glob 보존 (물리 제거 = FIX 진단·worker 합성 차단 over-restriction).
      (b) **essential-read/IO carve-out = CLOSED enumeration** — PL 컨텍스트 보유 유지 6 항목: READ {(1) FIX 1차진단 reads, (2) worker-prompt 합성 발췌 Change Plan §0-§5, (3) spec invariant cross-validate QADev 매핑표, (4) Pre-spawn-pin Step 0 git rev-parse origin/main} + WRITE/EXEC {(5) §8.5 Impl Manifest Edit(docs/stories/**), (6) PR pre-flight Bash}. 추가 = ADR amendment 의무 (open-ended carve-out = hollow-gate anti-pattern).
      (c) **위임 트리거 = re-read persistence (read-count 아님)** + R5 trivial-read 면제 LOCKED 비협상. 임계값 수치 = impl-measured lock (G1 deferred).
      (d) **env 캐리어 divergence + PL self-spawn 금지** — env=1 = PL→team worker SendMessage (self-contained, 본 ADR §결정 8) / env=0 = PL work-request 반환 → Orchestrator read-worker pre-spawn (PL self-spawn 금지 — re-entrancy 3종 + ADR-009 wrapper-only). D1 prose 는 절대 "PL spawns workers" 로 쓰지 않음 (env=0=ADR-009 위반). INV-1: env=0 carrier 가 self-do escape-hatch 금지 (carrier 만 다름, 비-essential read 금지 의무 동일).
      **CRITICAL invariant**: ADR-039 §결정 2 inline whitelist 4-entry closed enumeration **무변경** — PL read/compute boundary = **disjoint axis** (Orchestrator inline whitelist 과 다른 차원). 5번째 whitelist entry 신설 0. enforcement (D3) = advisory/warning-tier (ADR-039 Amendment 8 §결정 9 deferred slot) + ADR-060 evidence-gate 후 승격, 즉시 blocking 금지.
      §결정 1 phase-scoped sequential team lifecycle invariant 무변경 + §결정 8 env=0/env=1 분기 SSOT 무변경 (재해석·정합·확장만). Phase 2 = DeveloperPLAgent.md "컨텍스트 경계 규약" prose 신설 + D3 advisory lint (opt-in spawn-event-v1 enable) = 별 carrier (본 Amendment = Phase 1 declarative). is_transitional false, sunset_justification N/A.
    affected_sections: ["§결정 11 (신설 — thin-PL context boundary mandate)", "§결정 1 (cross-ref, 본문 무변경)", "§결정 8 (cross-ref env 캐리어, 본문 무변경)"]
    breaking: false  # additive (prose mandate codify), permissions 축소 0, lifecycle/env 분기 본문 무변경
    direction: strengthening  # thin-PL READ/COMPUTE 경계 codify = 강화 방향 (fat self-implementer drift 차단)
    sunset_justification: |
      §결정 1 lifecycle invariant 무변경 + §결정 8 env 분기 무변경 + ADR-039 §결정 2 4-entry closed enumeration 무변경 (disjoint axis — PL read/compute boundary ≠ Orchestrator inline whitelist). 본 amendment = thin-PL READ/COMPUTE 경계 codify (additive, 이미 stated invariant 의 enforcement) — fat self-implementer 동작 (설계-런타임 gap) 차단. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (read/compute 경계 mandate), 약화 0건. evidence = CFP-2521 §1 비용 측정 (PL context 97% PL 직접 read, worker 합성 1.4%). carrier_story CFP-2521 = ADR-044 Amendment 5 + ADR-039 Amendment 8 paired sibling amendment 2-set (axis disjoint — 본 ADR-044 = thin-PL 동작 mandate / ADR-039 = D3 enforcement deferred slot).
  - amendment: 6
    date: 2026-07-10
    cfp: CFP-2597
    summary: |
      §결정 12 신설 (check-verification-floor.sh 축③ — peer-completion falsifiability). Epic CFP-2597 (codeforge review-PL delivery-gap 기계화) Phase 2 carrier — §결정 10 (lane verification floor, Amendment 4) 의 축①(self-audit peer_count:0 verdict 무효) / 축②(silent degrade 차단) 위에 얹히는 3번째 축. ★ 명칭 disambiguation 필수: 본 축③ = **check-verification-floor.sh 의 축③ (peer-completion falsifiability)** — §결정 10 (d) 의 **check-lane-evidence.sh 축③ (deputy/role:dev fan-out enforcement)** 와 이름만 같고 대상 script·axis disjoint. full-tighten (Q) 확정:
      (a) precondition = pl_recommendation==PASS AND NOT honest-single-peer-degrade (peer_degrade.peer_count:1 ∧ degrade_acknowledged:true ∧ degrade_reason 3-조건 AND). 발동 시 review-verdict-v4 §19 peer_verdicts[] ≥1 entry ∧ 각 target (dirname(verdict_path) 기준 상대) 이 check시점 FS 실재+non-empty 임을 게이트가 독립 stat (자기단언 verify_status 불신).
      (b) 축 분담 무회귀: peer_count:0+PASS = 축① 선차단 → 축③ 미도달 / honest-single-peer-degrade = 축② 위임 → 축③ stand-down (AC-A3 무회귀). 미충족 → 위반 (warning: advisory exit0 / --strict exit1). non-version-gated (anti-evasion — 구 contract_version 선언 회피 차단). bare-PASS(peer_verdicts 부재) 및 peer_count:2-위조 재분류 = RED.
      (c) 원칙 SSOT 신설 0 — ADR-139 INV-L2 (stall≠PASS, 미측정→inconclusive) / §결정 7 (spawn-then-blind-wait 금지, collect=LEAD, INV-L4) + ADR-119 §결정 10 outcome-honesty cross-ref 만 (본 §결정 12 = mechanical 게이트 codify, 원칙 재정의 아님). review-verdict-v4 v4.15 → v4.16 MINOR (peer_verdicts[] additive) + MANIFEST mirror + review-pl-base §3/§10 collect codify + orchestrator-playbook §3.10.1 active-resume 결정론(peer transcript 직독) + I-6.6 review-lane 이식 + evidence-checks-registry peer-completion-falsifiability entry (owner_adr ADR-044 / carrier_adr ADR-060, warning-tier) 동반. all additive (T1 미발동).
      정직한 한계 (§3.4): 축③ = 위조비용 상향 + audit trail 이지 위조방지 게이트 아님. PL 이 claim(verdict)+proof(peer_verdicts) 동시저작하는 한 full falsifiability 불가 (peer_verdicts omit 시 잔존). warning-tier = 정직 상한, blocking 승격 = false assurance. full falsifiability = Epic trapdoor (stop-event 강화 or spawn-event-v1 선행 = independent-observer attestation substrate).
      §결정 1 phase-scoped sequential team lifecycle invariant 무변경 + §결정 2 dispatch_mode SSOT 무변경 + §결정 10 축①/② 무변경 (재해석·정합·확장만, 약화 0건). 실 script (scripts/check-verification-floor.sh) + workflow + test = sibling worker Phase 2 deliverable.
    affected_sections: ["§결정 12 (신설 — check-verification-floor.sh 축③ peer-completion falsifiability)", "§결정 10 (cross-ref 축①/②/③ 위상, 본문 무변경)"]
    breaking: false  # additive (verdict-v4 v4.16 optional array + warning-tier lint), 기존 축①/②·§결정 10 본문 무변경
    direction: strengthening  # 축③ 추가 = 강화 방향 (peer-completion falsifiability)
    sunset_justification: |
      Epic CFP-2597 = mctrader 데뷔 감사 delivery-gap class (fidelity-critical PASS 가 peer 완료증거 없이 새는) 의 강제력 복구 3번째 축 — 축①(self-audit) / 축②(silent degrade) 에 이어 peer-completion falsifiability. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (축③ 추가 + verdict-v4 v4.16 optional array), 약화 0건. §결정 10 축①/② 무손상. warning-tier = 정직 상한 (full falsifiability 는 PL claim+proof 동시저작 한계로 불가 — blocking 승격 = false assurance). carrier_story CFP-2597 = ADR-044 Amendment 6 + ADR-060 Amendment 21 paired sibling amendment 2-set (axis disjoint — 본 ADR-044 = 축③ 결정 SSOT / ADR-060 = warning-tier check 등록).
related_adrs:
  - ADR-009  # wrapper-only decomposition (Orchestrator 단일 lead 정합)
  - ADR-022  # Deprecated by ADR-035 — review-verdict v4 cutover 동기
  - ADR-024  # Story-scoped branch policy (Amendment 1 = hierarchical naming, ADR-040 동행)
  - ADR-031  # Lane-spawn evidence trail (§14 row append, hook 연계)
  - ADR-035  # Epic architecture SSOT (D2 phase-scoped agent teams 의 implementation level)
  - ADR-039  # Orchestrator subagent default (default subagent context vs enabled context 분기)
  - ADR-040  # Worktree convention (TeamCreate / Delete + worktree integration 의존)
  - ADR-094  # honest degrade — silent (a) 거부 / degraded+warning (c) 채택 (Amendment 4 §결정 10 dual-peer degrade 동형 anchor)
  - ADR-119  # research-before-claims Amd 2 — 게이트 verdict = outcome ground-truth (Amendment 4 self-audit verdict 무효 근거)
  - ADR-128  # 완료 단계 정식화 — local-only warning-tier + behavioral precondition (Amendment 4 W3 게이트 tier 상속)
  - ADR-060  # evidence-enforceable promotion framework — Amendment 6 축③ warning-tier check 등록 carrier (paired ADR-060 Amendment 21)
  - ADR-068  # boundary completeness invariants — Amendment 6 peer_verdicts[] entry 3-key = I-6 existence-verify-annotation (form/target/verify_status) 재사용
  - ADR-139  # background-wait liveness gate — Amendment 6 collect=LEAD (INV-L4) + INV-L2 (stall≠PASS→inconclusive) + §결정 7 (spawn-then-blind-wait 금지) 원칙 SSOT cross-ref (본 §결정 12 = mechanical 게이트 codify, 원칙 재정의 아님)
related_files:
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md
  - templates/team-spec-decompose.yaml
  - templates/team-spec-requirements.yaml
  - templates/team-spec-design.yaml
  - templates/team-spec-design-review.yaml
  - templates/team-spec-develop.yaml
  - templates/team-spec-code-review.yaml
  - templates/team-spec-security-test.yaml
  - templates/agent-teams-hook-samples/TeammateIdle.json.sample
  - templates/agent-teams-hook-samples/TaskCreated.json.sample
  - templates/agent-teams-hook-samples/TaskCompleted.json.sample
  - CLAUDE.md
  - docs/evidence-checks-registry.yaml  # Amendment 6 — peer-completion-falsifiability entry (축③ warning-tier)
  - scripts/check-verification-floor.sh  # Amendment 6 — 축③ detect (sibling worker Phase 2 deliverable)
is_transitional: false
---

# ADR-044: Phase-scoped sequential team SSOT

## 상태

**Proposed (2026-05-09)** — CFP-137 carrier, CFP-134 Epic Wave 2 (agent teams 적극 도입). Effective date = 본 ADR 가 포함된 wrapper Phase 1 PR merge timestamp + 사용자 측 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` settings.json 활성 + 신규 세션 재시작 (Story §4.3 prerequisite).

본 ADR 의 Epic-level architecture 결정 SSOT = [ADR-035](ADR-035-codeforge-agent-teams-epic-architecture.md) (D2 = Agent teams 적극 도입). 본 ADR = D2 의 **implementation level SSOT** — phase-scoped sequential team 의 lifecycle / team-spec yaml 7종 / hook 3종 / review-verdict v3 → v4 cutover / 5 권장 패턴 measurable verification 정의.

본 Story spec SSOT = [`mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md) §4.3 (CFP-137 부분).

## 컨텍스트

사용자 directive (2026-05-08, CFP-134 Epic brainstorming):

> "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다."

> "codex review와 sonnet decider를 codeforge의 일환으로 보는 것 같은데 그건 아니다. 사용자 stop이 너무 많아 내가 필요할 때마다만 요청하는 것이지 codeforge가 이를 반영해서 임의로 수행해서는 안된다."

### 현재 상태

- ADR-009 (wrapper-only decomposition, Adopted) — Orchestrator (top-level Claude 세션) 단일 lead invariant.
- ADR-022 (Sonnet decider 5-trigger 자동 발동) = **Deprecated by ADR-035** (CFP-134, 2026-05-08). 사용자 ad-hoc 호출 전용.
- ADR-024 + ADR-040 (Worktree convention) — `cfp-NNN[/<lane>[/<sub>]]` hierarchical naming + base directory + lifecycle hook contract.
- ADR-031 (Lane-spawn evidence trail) — Story §14 row append (Orchestrator self-write monopoly, Amendment 1 으로 delegate subagent 포함).
- ADR-035 (Epic architecture, Accepted) — D2 = Phase-scoped sequential team 적극 도입.
- ADR-039 (Orchestrator subagent default, Accepted) — default subagent context 의 always-spawn invariant. Inline whitelist 4-entry closed.
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env = Claude Code experimental feature 활성. TeamCreate / TeamDelete / SendMessage / TaskList / TeammateIdle hook 노출.
- `superpowers:using-git-worktrees` skill — worktree 가용 prerequisite.

### Gap

1. **Phase-scoped sequential team lifecycle SSOT 부재** — ADR-035 D2 결정 본문에 "lane 진입 시 TeamCreate, 완료 시 TeamDelete" 만 명시. lane 별도 team-spec / teammate roster / hook subscription 미정의.
2. **team-spec yaml schema 부재** — 7 lane 의 teammate roster 정의 file 없음.
3. **hook 3종 (TeammateIdle / TaskCreated / TaskCompleted) 미등록** — 현재 `templates/.claude/hooks/` 에 SessionStart × 2 만.
4. **review-verdict v3 → v4 cutover 미수행** — ADR-022 Deprecated 후 v3 의 Sonnet decider 영역 (decision_state 7 state / sonnet_final_status / decider_decision_ref / write_errors step enum) 이 NO-OP passthrough. v4 MAJOR bump 가 정식 제거 carrier — 본 ADR scope.
5. **5 권장 패턴 measurable verification 미정식화** — Anthropic 권장 패턴 (Specialization / Parallelization / Adversarial / Cross-layer / Escalation) 이 codeforge lane 매핑 명시되었으나 (Story §2.2), AC-level metric 미정의.
6. **default subagent context vs agent teams enabled context 분기 fallback 미정의** — ADR-039 default invariant 와 본 ADR 의 enabled context 활용 사이 동작 fallback 부재.

## 결정 (12)

### 결정 1 — Phase-scoped sequential team lifecycle (ADR-035 D2 implementation)

매 lane 진입 시 Orchestrator 가 다음 sequence 수행:

```
1. Preflight check (CLAUDE.md "레인 진입 전 Preflight 체크 의무")
2. (CFP-139 후) GitOpsAgent SendMessage — lane worktree 준비
3. TeamCreate(team_spec=templates/team-spec-<lane>.yaml, worktree=<path>)
4. lane 진행:
   - Lane PL → teammate dispatch (TaskCreate)
   - teammate ↔ teammate SendMessage (Adversarial / Cross-layer 패턴)
   - PL 중재 + dedup → pl_recommendation
5. TeamDelete (in-flight teammate 완료 명시 wait)
6. Orchestrator self-write (Story §9 + GitHub gate label + phase transition)
7. FIX 시 → TEAM-FIX 새 team (parallel diagnosis)
```

**Lead = Orchestrator** (Story 전 기간 fixed, ADR-035 D2 + ADR-009 정합). Phase-scoped = lane 별도 짧은 lifecycle (`/resume` no-resumption risk 회피, ADR-035 §결과 cross-ref).

**거절된 대안**:
- (B) Story-long single team — `/resume` 후 in-process teammate 미복원 위험. ADR-035 D2 §근거 정합.
- (C) Continuous team-of-teams — codeforge 정책 nested team 금지 (domain-knowledge entry §"re-entrancy 제약 3종"). team-spec yaml depth 1 강제.

### 결정 2 — team-spec yaml 7종 schema (Specialization 매핑 SSOT)

`templates/team-spec-<lane>.yaml` 7종 신설:

| File | Lane | Teammate count (default) | Teammate count (Codex on request) | Dispatch pattern |
|---|---|:-:|:-:|---|
| `team-spec-decompose.yaml` | Stage 0 (Epic 분해) | 2 (PMOAgent + Orchestrator) | 2 | sequential dialog |
| `team-spec-requirements.yaml` | 요구사항 | 4 (PL + Domain + Analyst + Researcher) | 4 | parallel sub-task fan-out |
| `team-spec-design.yaml` | 설계 | 8 (PL + chief + 6 SubAgent) | 8 (CONDITIONAL +2 Live SubAgent) | parallel SubAgent fan-out |
| `team-spec-design-review.yaml` | 설계 리뷰 | **2** (PL + Claude worker) | **3** (PL + Claude + Codex worker) | adversarial debate |
| `team-spec-develop.yaml` | 구현 | 5-7 (PL + QADev + role:dev × N) | 5-7 | cross-layer (dev ↔ QA) |
| `team-spec-code-review.yaml` | 구현 리뷰 | **2** (PL + Claude worker) | **3** (PL + Claude + Codex worker) | adversarial debate |
| `team-spec-security-test.yaml` | 보안 테스트 | **2** (PL + Claude worker) | **3** (PL + Claude + Codex worker) | adversarial + GitHub native 1차 layer 통합 |

(구현 테스트 lane = 1 agent TestAgent — team 미생성, 기존 single subagent 유지.)

**Schema (공통 base)**:

```yaml
lane: <lane-name>
teammates:
  - name: <agent-name>
    role: <PL | chief | deputy | worker | role:dev | QADev | Researcher | Analyst | Domain>
    system_prompt_path: <plugin-relative agent file path>
    model: <claude-opus-4-7 | claude-sonnet-4-6 | gpt-5-codex>
    spawn_mode: default | conditional
    dispatch_mode: default | user_request_only | auto_on_divergence  # NEW (Story §2.4 정합 / Amendment 1 CFP-391 — auto_on_divergence 추가)
    activation_condition: <expression — only when spawn_mode=conditional>
dispatch_pattern: parallel | sequential | adversarial | cross-layer | sequential-dialog
worktree_layout:
  per_teammate: bool                # true 시 각 teammate sub-worktree 보유
  base_worktree: cfp-NNN/<lane>     # parent (story root) 또는 lane sub-branch
hook_subscriptions:
  - TeammateIdle
  - TaskCreated
  - TaskCompleted
```

**dispatch_mode SSOT (Story §2.4)**: review lane 의 Codex worker = `dispatch_mode: user_request_only`. default roster = `PL + Claude worker` 2 teammate, Codex 는 사용자 explicit request 시 추가 → 3 teammate. memory `feedback_sonnet_decider_user_only.md` + ADR-022 Deprecated + 사용자 turn 7-8 directive 정합.

**Amendment 1 (2026-05-11, CFP-391 / ADR-059)** — `auto_on_divergence` 옵션 추가. ADR-059 에서 정의되는 `debate-protocol-v1` 발동 조건 — DesignReview lane 에서 Claude worker 와 Codex worker 가 동일 anchor 에 대해 (a) 서로 다른 severity 또는 (b) 서로 다른 recommendation 산출 시 자동 활성.

**우선순위 룰** (두 mode 동시 적용 시 effective mode 결정):

```
default  >  auto_on_divergence  >  user_request_only
```

- `default` 가 가장 강함 (항상 활성)
- `auto_on_divergence` = trigger 조건 (divergence) 만족 시 자동 활성
- `user_request_only` = 사용자 explicit request 만 (최약)
- 두 mode 가 동시 활성 시 더 강한 쪽이 effective. 예: `[user_request_only, auto_on_divergence]` 표기 worker 는 divergence 감지 시 자동 활성 + 사용자가 explicit request 안 한 상태에서도 발동.
- review lane Codex worker 의 권고 표기 = `dispatch_mode: [user_request_only, auto_on_divergence]` (Story 1 scope = DesignReview, Story 2 scope = Requirements 도 동일 패턴).

**`auto_on_divergence` trigger 의 lane-specific 정의**:

- DesignReview: review-verdict-v4 `findings[]` 동일 `anchor_id` 에 대해 (severity 또는 recommendation 불일치) — ADR-059 §결정 2
- Requirements (Story 2 / CFP-392 scope): RequirementsPL synthesis 와 Codex proactive check 간 semantic divergence — ADR-052 touchpoint #4 격상 Amendment 와 동행 (별도 Story)
- CodeReview / SecurityTest: deferred CFP-C scope

본 Amendment 자체는 BREAKING 아님 — `default | user_request_only` 기존 동작 보존 + enum 1 value 추가 (SemVer MINOR 정합 — ADR-008).

**거절된 대안**:
- (B) review lane default = `PL + Claude + Codex` (3 teammate) — 사용자 directive 정면 위배 (Codex review 자동 발동 = ad-hoc only).

### 결정 3 — Hook 3종 등록 + sample (TeammateIdle / TaskCreated / TaskCompleted)

`templates/agent-teams-hook-samples/` 에 신규 sample 3종 (path = wrapper repo standalone — `templates/.claude/hooks/` 디렉토리는 SessionStart 류 hook 의 standardized location, 본 agent teams 류 hook 은 별도 디렉토리에 분리해 consumer 가 명시 의식 후 install):

- `TeammateIdle.json.sample` — idle teammate detect → PL 에 nudge SendMessage 또는 TeamDelete 권유
- `TaskCreated.json.sample` — 새 task dispatch 시 Story §14 Lane Evidence row append (ADR-031 Amendment 1 정합 — Orchestrator-owned delegate write)
- `TaskCompleted.json.sample` — task outcome §14 row 채움 + (CFP-139 후) GitOpsAgent worktree merge trigger

**등록 mechanism**: consumer 측 `.claude/settings.json` `hooks.{TeammateIdle,TaskCreated,TaskCompleted}[]` 배열에 sample copy. consumer-guide §"Agent teams 적극 도입 (CFP-137)" 가 install 안내 — `cp templates/agent-teams-hook-samples/*.json.sample .claude/hooks/` 후 settings.json merge.

**Trigger 조건 (env-divergent)**:

| env | TeamCreate / SendMessage / hook | 동작 |
|---|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | 활성 | hook 3종 trigger 발화. team-spec yaml 본격 사용. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 미설정 | 미활성 | hook 3종 등록되어도 trigger 미발화. ADR-039 default subagent context fallback. team-spec yaml 미사용 (기존 one-shot Agent tool spawn 유지). |

### 결정 4 — review-verdict v3 → v4 MAJOR bump (Sonnet decider 영역 정식 제거 + worker_dialog_rounds 추가)

본 ADR carrier scope. v3 → v4 BREAKING:

- **제거 (NO-OP passthrough → 정식 제거)**:
  - `decision_state` 8-value enum 전체 (단순화: PL synthesis 후 Orchestrator self-write 단일 path)
  - `sonnet_final_status` field
  - `decider_decision_ref` field
  - `write_errors[].step` 의 Sonnet 영역 step enum (`fix_ledger_append`, `diagnosis_spawn` 의 `decider:claude_sonnet` semantics)
  - 5-step Orchestrator algorithm (review-verdict v3.md §6) — Sonnet 호출 step 3 제거 → 4-step 단순화

- **추가**:
  - `worker_dialog_rounds: int >= 0` — Adversarial debate 의 SendMessage round count (5 권장 패턴 Adversarial measurable verification, Story §5.1)
  - `pl_recommendation` (PASS / FIX / FIX_DISCRETIONARY) 가 final verdict 책무 단독 보유 (sonnet override marker 제거)

- **유지**:
  - `findings[]` schema (severity / category / file / line / evidence / suggestion)
  - `writes_completed{}` audit (Orchestrator self-write 결과)
  - `lane` / `story_key` / `iteration` / `contract_version: "4.0"`

**Cutover (Story §5.5 R3 default 채택)**: 즉시 cutover. consumer scope 0건 (mctrader debut audit 까지) 으로 backward compat 면제. wrapper Phase 1 PR merge 시:
- v3 sibling (wrapper repo) `status: Active → Archived` 동기 갱신
- v4 sibling (wrapper repo) `status: Active` 신설
- canonical sync (codeforge-review plugin) 는 sibling sync follow-up PR (ADR-010 §단계 절차 정합)
- `MANIFEST.yaml` `review_verdict.files[]` 에 v4 entry append + v3 status flip

**Migration guide**: v4 file 본문 §"v3 → v4 migration" 섹션에 verbatim — 수신자 (Orchestrator + Lane PL) 갱신 항목 명시.

**거절된 대안**:
- (B) deprecation period 6개월 — consumer scope 0이라 불필요. Story §5.5 R3 default 정합.

### 결정 5 — 5 권장 패턴 measurable verification 5종 (Story §5.1 정식화)

| 패턴 | codeforge 매핑 lane | Measurable verification | Lint / fixture 위치 |
|---|---|---|---|
| **Specialization** | 7 lane 전체 (teammate 좁은 system prompt) | team-spec yaml `system_prompt_path` 가 lane PL agent prompt line count 보다 적음 | subjective — Phase 2 e2e fixture spot-check |
| **Parallelization** | TEAM-DESIGN 6 SubAgent / 2 review worker 동시 | §14 Lane Evidence 의 `spawned_at` (SubAgent 6 row) 차이 < 60s | `scripts/check-lane-evidence.sh` lint 확장 (Phase 2 PR scope) |
| **Adversarial** | TEAM-{DESIGN,CODE,SECURITY}-REVIEW Claude vs Codex worker (Codex on request) | review-verdict v4 packet `worker_dialog_rounds: int >= 2` (Codex 활성 시) | review-verdict-v4 schema 신규 field (본 ADR 결정 4) |
| **Cross-layer** | TEAM-DEVELOP dev ↔ QA continuous coordination | develop-output v1 → v1.1 MINOR bump 후보 (`cross_layer_dialog_rounds: int >= 1`) | codeforge-develop sibling sync follow-up |
| **Escalation** | lane FIX 시 lane team → TEAM-FIX (parallel diagnosis) | §10 FIX Ledger row + §14 lane=`<원래>-fix-iter-N` row pair 동시 존재 | `scripts/check-fix-evidence.sh` 신설 후보 (Phase 2 deferred) |

본 5 metric 의 Phase 1 scope = schema 정의 (review-verdict v4 의 `worker_dialog_rounds` field 신설). 나머지 lint / fixture / develop-output bump = Phase 2 PR scope 또는 sibling sync follow-up.

### 결정 6 — `docs/orchestrator-playbook.md` §3 amendment

기존 §3 (lane spawn sequence + branch logic + FIX 진단 흐름) + §3.0 (ADR-039 spawn-default) + §3.5 (Worktree dispatch) 에 다음 sub-section 추가:

- **§3.6 TeamCreate / TeamDelete protocol** (env=1) — env 검증 + worktree path 주입 + teammate fan-out 사양 + in-flight wait
- **§3.7 SendMessage 사용 패턴** — Lane PL ↔ Worker continuous dialog 예시 (review lane Claude ↔ Codex debate)
- **§3.8 TeammateIdle nudge protocol** — idle 감지 시 PL 의 추가 dispatch 또는 TeamDelete 트리거
- **§3.9 env-divergent context fallback** — env=0 시 기존 one-shot Agent tool subagent 폴백 (ADR-039 default)

### 결정 7 — `docs/consumer-guide.md` § "Agent teams 적극 도입 (CFP-137)" 신설

본 ADR 후 consumer-guide 신규 subsection:

- prerequisite: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` settings.json env + 신규 세션 재시작
- env=0 fallback 동작 명시 (기존 one-shot subagent — ADR-039 정합)
- hook 3종 sample install 안내 (overlay merge 패턴 — SessionStart-codeforge-worktree-gc.json.sample 와 동일)
- **secret hygiene**: SendMessage body 에 secret (API key / DB credential 등) 미포함 의무 — sibling teammate 끼리 system prompt / tool output 공유. consumer 책임 영역.
- consumer 측 적용 가이드 (consumer Orchestrator 의 codeforge orchestration 시 본 정책 inheritance)

### 결정 8 — 5 권장 패턴 적용 시 default subagent context invariant 무손상

본 ADR 의 5 권장 패턴 적용 = agent teams enabled context (env=1) 한정. default subagent context (env=0 또는 미설정) = ADR-039 §결정 1 always-spawn invariant 무손상. 두 context 의 분기 SSOT = `docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md` (CFP-137 신설 entry). hook 3종도 env=1 시에만 trigger 발화 — env=0 fallback = ADR-039 default 유지.

### 결정 9 — Multi-step chief author pattern recommendation (Amendment 3, CFP-1438)

chief author (특히 ArchitectAgent Opus tier) 의 lifecycle pattern 안 **multi-step sequential smaller spawn 패턴 codify** + team-spec yaml schema 확장 (declarative-only Wave 1, Phase 2 actual yaml write = 별 sub-CFP carrier). ADR-039 Amendment 5 §결정 17 paired carrier (axis disjoint — 본 ADR-044 = team-spec yaml multi-step lifecycle pattern / ADR-039 = orchestrator-side spawn span guideline body).

**Multi-step lifecycle pattern (3-step sequential)**:

기존 §결정 1 phase-scoped sequential team lifecycle 안 chief author (ArchitectAgent Opus) spawn 단계가 단일 monolithic span (15-40min wide drift surface) 으로 진행되는 anti-pattern 을 **recommendation tier 로 multi-step decomposition** 권장:

```
chief_author_span: monolithic       # default null = unspecified → fallback to monolithic
chief_author_span: multi_step_3     # skeleton + body + integration 3-step sequential recommended
chief_author_span: multi_step_N     # N-step sequential (N >= 2, custom split)
```

3-step sequential pattern (`multi_step_3` value):

| Step | Span | Activity | Drift surface |
|---|---|---|---|
| 1. Skeleton | ~5-7min | frontmatter + section heading + placeholder + ADR-RESERVATION row append + amendments_reserved slot pre-claim | ≤ 7min single spawn |
| 2. Body | ~5-7min | substantive content (Change Plan §1-§13 본문 + ADR §결정 본문 + Story §3/§7/§11 본문). previous skeleton state passed as input | ≤ 7min single spawn |
| 3. Integration | ~5-7min | cross-refs verify + lint validation + workflow stub finalize + CLAUDE.md update + commit. previous body state passed as input | ≤ 7min single spawn |

**team-spec yaml schema 확장 (declarative-only Wave 1)**:

7 team-spec yaml file (`templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml`) 안 `chief_author_span` field optional schema 확장. Phase 1 = declarative declare only. Phase 2 actual yaml write = 별 sub-CFP carrier.

```yaml
# templates/team-spec-design.yaml (예시 schema 확장 — Phase 2 sub-CFP carrier)
teammates:
  - role: ArchitectAgent
    tier: opus
    chief_author_span: multi_step_3   # NEW Wave 1 schema field, declarative-only
    span_decomposition:
      - step: skeleton
        target_minutes: 5
        scope: [frontmatter, section_heading, placeholder, slot_reservation]
      - step: body
        target_minutes: 7
        scope: [substantive_content]
      - step: integration
        target_minutes: 5
        scope: [cross_refs, lint, workflow_stub, claude_md, commit]
```

**Backward-compat invariant**:

- `chief_author_span` field optional (default null = unspecified → fallback to monolithic, 기존 동작)
- §결정 1 phase-scoped sequential team lifecycle 본문 무변경 (lifecycle sequence 정의 무손상)
- §결정 7 team-spec yaml SSOT additive only (3 optional field with default — ADR-044 Amendment date-2026-05-24 CFP-1354 `parallel_spawn_cap` / `spawn_stagger_ms` / `cascade_circuit_breaker` 패턴 답습)
- §결정 8 default subagent context (env=0) invariant 무손상 (multi-step pattern = env=1 agent teams + env=0 default 양 context 적용 가능, mechanism level — env=1 = SendMessage continuous dialog / env=0 = sequential Agent tool 3 calls)

**Trade-off matrix** (Wave 1 declare, Wave 2 mechanical telemetry carrier deferred):

- **Benefits**: drift surface per spawn ↓ (preventive complement to ADR-073 Amd 11 SHA pin + ADR-082 Amd 15 spawn prompt anchor + ADR-073 Amd 12 mid-spawn drift detection + ADR-082 Amd 17 amendment-slot pre-reservation). race amplification 차단.
- **Costs**: number of spawns ↑ (1 → 3 typically) + coordination complexity ↑ (state passing between spawns via yaml input/output handoff) + spawn overhead ↑ (Agent tool invocation cost × 3) + risk of incomplete state transfer between spawns
- **Measurement metric (Phase 2 telemetry carrier deferred — Wave 2 별 sub-CFP)**: spawn time histogram per chief author spawn + per-spawn collision count (mid-spawn drift detection hit rate) + chief author span KPI (median/p95/max minutes per spawn) — workflow stub `templates/github-workflows/chief-author-span-telemetry.yml` declarative Wave 1 carrier 본 CFP

**ADR-039 Amendment 5 §결정 17 paired carrier dual-binding** (같은 CFP-1438 Story 안):

- 본 ADR-044 Amd 3 §결정 9 = team-spec yaml multi-step lifecycle pattern + schema 확장 (declarative-only Wave 1)
- ADR-039 Amd 5 §결정 17 = orchestrator-side spawn span guideline body (recommendation tier, declarative-only Wave 1)
- axis disjoint: team-spec yaml (본 ADR) ↔ orchestrator-side (ADR-039) — ADR-064 §결정 1 CFP scope unitary 정합 (2-set paired Amendment)

**Recommendation tier, NOT mandatory** — chief author 가 monolithic span 채택 시 결격 0 (warning tier 미부착). 단 본 amendment 의 schema 가 future Phase 2 mechanical wire 시 `chief_author_span_minutes` evidence-checks-registry warning-tier 등재 가능 (별 sub-CFP carrier, evidence-gated promote: PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged AND condition).

**META-self-application**: 본 CFP-1438 chief author spawn 자체 = guideline 첫 적용 사례. 본 spawn = skeleton + body + integration 3-step sequentially demonstrate (본 Amendment 작성 자체 = META demonstration).

**Verification evidence**:
- CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach evidence (memory `project_cfp_1318_adr073_amendment_6` 박제 — amendment_number_stale_at_planning 3+ occurrence)
- Sub-CFP A/B/C (CFP-1437/1436/1435) 3-layer race detection/claim complement evidence (각 amendment_log audit trail)
- ADR-039 §결정 17 disjoint axis pair verify (orchestrator-side ↔ team-spec yaml)
- §결정 1 / §결정 7 / §결정 8 invariant 무영향 verify

### 결정 10 — lane verification floor 정합 (Codex ad-hoc ceiling 보존 명문) — Amendment 4 (CFP-2471, Epic CFP-2468 Track W / W3)

**배경**: Epic CFP-2468 Track W3 (lane 검증 균질성 강제) 가 codeforge 의 **검증 강도 floor** 개념을 명문화한다. 동인 = mctrader (첫 비-dogfood consumer) 데뷔 감사 — fidelity-critical 코드가 2-peer 없이 self-audit 단독 머지, dual-peer 가 Codex 미가용 시 silent single-peer degrade, 설계 deputy / sonnet 구현자 fan-out 미spawn. 이 셋은 "검증이 가장 필요한 곳에서 빠지는" 동일 class 결함이다. concept SSOT = `docs/domain-knowledge/concept/lane-verification-floor.md` (CFP-2471 Phase 1 landed). 본 §결정 10 = §결정 2 (Codex ad-hoc-only) 와의 **정합 명문** — §결정 2 본문 무변경, 재해석·cross-ref 만.

**(a) 검증 floor = ≥1 independent peer (SoD), Codex 는 floor 아닌 ceiling**

검증 floor 의 본질 = **implementer ≠ certifier** (separation of duties — SLSA two-person review / four-eyes). floor 충족자 = ClaudeReviewAgent (review lane default roster 상존, §결정 2). Codex 는 cross-model diversity 이득을 더하는 **ceiling** (2nd peer) — §결정 2 가 Codex review 자동발동을 `dispatch_mode: user_request_only` ad-hoc-only 로 두는 것과 **disjoint·무충돌**. "검증 floor 강제"를 "Codex 강제"로 해석하면 §결정 2 위반이자 사용자 directive (2026-05-08 "codex review… codeforge가 임의로 수행해서는 안된다") 오독. floor=Claude peer 가 정설.
> source: SLSA v1.0 levels (https://slsa.dev/spec/v1.0/levels) — two-person review / provenance attestation, implementer ≠ certifier.

**(b) dual-peer 2→1 degrade = honest, ≠ silent, ≠ skip**

2nd peer (Codex) 미가용 시 single-peer (Claude) 로 degrade 는 정상 경로 (floor 는 여전히 충족 — (a)). 단 [ADR-094](ADR-094-consumer-legacy-version-fallback-policy.md) §결정 1 동형 — (a) silent degraded 거부 (silent harm) / (c) degraded mode 작동 + **가시 marker + 사유 강제 기록** 채택. silent 2→1 (표식 없는 degrade) = 게이트 차단 대상. degrade ≠ skip ≠ 진입불가.
> source: ADR-094 §결정 1 (archive/adr/ADR-094-...:65-78) — (c) hybrid grace = degraded mode + warning 보고 의무, silent harm (a) 거부.

**(c) review-pl-base.md:574 문서 모순 정합 — "진입불가" → "silent degrade 금지" 재해석**

firsthand 문서 모순: `plugins/codeforge-review/templates/review-pl-base.md:573-574` ("CodexReviewAgent 미설치 시 lane 진입 불가·`SKIPPED` 불허") ↔ `templates/team-spec-code-review.yaml:33-39` (`spawn_mode: conditional` / `activation_condition: user_explicit_request` / `dispatch_mode: user_request_only`, default 2-teammate single-peer). 전자는 Codex 를 필수워커로 (degrade 금지), 후자는 ad-hoc ceiling 으로 본다. **정합 방향 = single-peer floor + Codex ceiling (team-spec 방향)** — review-pl-base:574 의 "진입불가·SKIPPED 불허"는 "**silent degrade 금지**"로 재해석. single-peer honest degrade 는 진입불가가 아니라 정식 floor 충족. (이렇게 정합해야 (a) floor=Claude peer + §결정 2 Codex ad-hoc-only 무충돌. 반대 방향 (b) dual-peer 필수 유지 = consumer Codex 미설치 시 review lane 전면 마비 + §결정 2 정면 위배 → 거부.) review-pl-base.md 실 문구 정합 = Phase 2 carrier.

**(d) lane별 floor 차등 + 축③ fan-out enforcement 의 미확정 전제조건**

- **lane별 floor 차등 허용**: security lane floor 는 ≥1 peer 보다 높음 — packet 에 1차 native layer (Dependabot / CodeQL / Secret scanning / Push protection) inline + dependency manifest 필수 (`ClaudeReviewAgent.md:48`). 타 review lane (design / code / requirements-review) = 균일 ≥1 peer floor.
- **축③ deputy/role:dev fan-out 관측·강제 의 layer 분리**: 관측 baseline (SubagentStart hook + `check-lane-evidence.sh` 축③ 확장 lint) = block 불가 platform fact 라 항상 관측-only. 강제 (PreToolUse `Agent` matcher `permissionDecision:"deny"`) = block 가능 layer. **단 — 요구사항리뷰 P2 carry (확인 불가/추정)**: PreToolUse spawn-deny 의 (i) 정확 matcher 토큰 (`Agent` (구 `Task` 아님)) 과 (ii) CLI 런타임 실 발동은 **empirical 미확정**. block 능력·방향 자체는 verified (concept `orchestrator-runtime-hook-enforcement.md:49` + ADR-039), 그러나 정확 토큰·CLI 발동은 documented claim 이지 empirical 검증 미완. 따라서 enforcement layer 의 **활성 채택은 전제조건 2개 (정확 토큰 확정 + CLI 런타임 empirical 확인) 통과 후로 보류** — Phase 2 에서 이 전제 미충족 시 관측-only baseline 만 활성, enforcement 는 정의만 하고 미활성. settled 사실로 단정 금지 (ADR-119 firsthand).
> source (platform fact): concept `docs/domain-knowledge/concept/orchestrator-runtime-hook-enforcement.md:45-50` — SubagentStart=block 불가(관측만) / PreToolUse Agent matcher=block 가능. (정확 토큰·CLI 런타임 = 확인 불가/추정, empirical 검증 미완.)

**(e) degrade marker schema cross-ref (Phase 2 carrier)**

축② degrade 가시화·강제기록의 marker = `docs/inter-plugin-contracts/review-verdict-v4.md` verdict packet 확장 (additive MINOR — 현 v4.14, 8 verdict-level optional bool field + findings[].type closed-enum, additive 패턴 확립). 정확 schema (verdict-level bool `dual_peer_degrade_declared` 권장 / `peer_degrade` 3-key block `peer_count`·`degrade_reason`·`degrade_acknowledged` 대안) = Change Plan §3 결정, 실 MINOR bump = Phase 2 carrier. review-verdict-v4 = canonical 단일 (sibling sync 폐지 — ADR-118 D5).

**불변 보존 (약화 0건)**:
- §결정 1 phase-scoped sequential team lifecycle invariant 무변경.
- §결정 2 dispatch_mode SSOT 무변경 — Codex `user_request_only` ad-hoc-only 약화 0건. 본 §결정 10 = floor=Claude peer / Codex=ceiling 으로 §결정 2 와 disjoint axis 확정 (재해석·정합만).
- review lane default roster = PL + Claude worker 2-teammate 무변경. 거절된 대안 B (default 3-teammate Codex 포함) 재확인 거부.
- branch protection 6-tuple 무변경 + warning-tier 상속 (ADR-128). W3 거버넌스 게이트 중 local-only 부분은 warning-tier + behavioral precondition.

**Phase 분리**: 본 §결정 10 = Phase 1 declarative 정합 declare. Phase 2 mechanical wire = review-pl-base:574 실 문구 정합 + verdict-v4 degrade marker MINOR bump + `scripts/check-verification-floor` (축①/②) + `check-lane-evidence.sh` 축③ 확장 (stale roster 정정 → 현 6 permanent + <6 silent SKIP → WARN + shape-aware roster) + warning-tier workflow + (전제 통과 시) PreToolUse hook. 별 carrier.

**Verification evidence**:
- §결정 2 본문 무변경 verify (Codex ad-hoc-only 약화 0건 — disjoint axis 정합).
- ADR-094 §결정 1 (c) honest degrade 동형 verify (archive/adr/ADR-094-...:65-78 직접 Read).
- firsthand 문서 모순 verify (review-pl-base.md:573-574 ↔ team-spec-code-review.yaml:33-39 직접 Read).
- check-lane-evidence.sh:196 stale roster verify (구 이름 ↔ 현 6 permanent `plugins/codeforge-design/CLAUDE.md:40-45` 직접 Read 대조).
- matcher P2 미확정성 honest 표기 verify (settled 단정 0건 — (d) 전제조건으로 명시).

### 결정 11 — Thin-PL context boundary mandate (lane-PL READ/COMPUTE 경계 codify) — Amendment 5 (CFP-2521)

**배경**: lane-PL 의 책무는 worker 산출물을 합성·중재하는 **thin synthesizer** 이고(§결정 1 lifecycle), 파일 I/O(Read/Edit/Bash)는 worker 책무다. 그러나 DeveloperPL 은 런타임에서 이 경계를 벗어나 자기가 파일을 직접 읽고 명령을 실행하는 **fat self-implementer** 로 동작 중이다(CFP-2521 §1 측정: PL context 비용 94%=컨텍스트 보유, 그 97%=PL 직접 read(Read 52.9% + Bash 38.7%), worker 합성 1.4%). 기존 codeforge governance 는 WRITE 경계(`lane-self-write-boundary`)만 codify 했고 **READ/COMPUTE 경계는 공백**이었다. 본 §결정 11 = 그 공백을 채우는 codify — **신규 원칙이 아니라** 이미 stated 된 thin-synthesizer invariant(`DeveloperPLAgent.md:269` + §결정 1 + ADR-039 §결정 3)의 **enforcement/codification**(설계-런타임 gap 차단). concept SSOT = `docs/domain-knowledge/concept/context-offloading-to-ephemeral-workers.md`(CFP-2521 Phase 1 landed).

**(a) PL self-do 금지 (read/compute budget) — prompt-mandate(behavioral) tier**

lane-PL 은 비-essential 경로(docs/stories 밖 `plugin.json` / `scripts/**` / `*.yaml` / playbook)를 **직접 Read/Bash 하지 않고** 필요한 사실을 worker 요약으로만 보유한다(synthesizer_port: input={Change Plan, Story, worker 요약}, output={§8.5 Impl Manifest, PR}, raw_file_contents/bash_output 의 PL prefix 진입 금지). tier = **prompt-mandate(behavioral)** — permission-enforced Read-deny 아님: Read path-scoping(`Read(docs/**)` allow-scope)은 agent frontmatter 에서 **UNVERIFIED-IN-PRACTICE**(fleet-wide `Read(path)` entry 0건 firsthand, `Bash(...)` 는 218곳 scoped; 공식문서는 `Read(path/**)` 가 settings.json 존재만 확인 subagent-frontmatter honor 미확인). → ADR-039 §결정 8 doc-only trust 선례 상속. `permissions.allow` 의 Read/Grep/Glob 는 보존(물리 제거 = FIX 진단·worker 합성 차단 over-restriction).
> source (Anthropic pattern): orchestrator-worker / context offloading to subagents — lead 가 raw context 대신 요약만 보유 (https://www.anthropic.com/engineering/built-multi-agent-research-system). source (Read path-scoping 미확인): code.claude.com/docs/en/iam — settings.json permission, subagent-frontmatter honor 여부 미확인(추정).

**(b) essential-read/IO carve-out = CLOSED enumeration (비협상)**

전면 read-ban 은 본 mandate 자체를 모순으로 만든다(FIX 진단·worker prompt 합성·spec 합성 깨짐). PL 컨텍스트 보유 유지 6 항목(closed):

| # | essential | anchor | 사유 |
|---|---|---|---|
| 1 | FIX 1차진단 reads — review verdict packet + §8.5 Impl Manifest + Change Plan §5/§8 + commit diff | DeveloperPLAgent.md:221 | FIX 진단 직접 read 전제 |
| 2 | worker-prompt 합성 발췌 — Change Plan §0-§5 외부지식 packet | DeveloperPLAgent.md:262-266 | worker 인계 인용 원천 |
| 3 | spec invariant cross-validate — QADev 매핑표 | DeveloperPLAgent.md:97-99 | synthesizer 본연 책무 |
| 4 | Pre-spawn-pin Step 0 — `git rev-parse origin/main` 경량 Bash | DeveloperPLAgent.md:80-89 + ADR-039 §결정 14 | SHA self-pin 불변식(위임 시 신뢰 체인 붕괴) |
| 5 | §8.5 Impl Manifest Edit — `Edit(docs/stories/**)` | DeveloperPLAgent.md:178/191 | ownership-preserved write(§결정 3 Ownership≠Mechanism), read leak 아님 |
| 6 | PR pre-flight Bash — `git branch --show-current` + `gh pr create --base main` | DeveloperPLAgent.md:91-96 | PR 생성 mechanism |

**CLOSED 선언**: 추가 = ADR amendment 의무. open-ended carve-out = hollow-gate(검사연극) anti-pattern — 무한 예외 escape-hatch 차단.

**(c) 위임 트리거 = re-read persistence + R5 면제 LOCKED**

위임 트리거 = read 결과가 **N+ 잔여 PL 턴 잔존(re-read persistence)** 인가이지 read 횟수가 아니다(R1 — 잔존 시 raw 가 누적 prefix 에 superlinear 비용으로 남음). **R5 trivial-read 면제 = LOCKED 비협상** — 1회성 trivial read(잔여 턴 미잔존)는 회피 재독 ≈ 0 이라 worker spawn 고정비 > 이득 → 순손실(hollow-gate). R5 누락 시 break-even 이 silently load-bearing. **면제 임계값 수치 = impl-measured lock(G1 deferred)** — worker 1-spawn `cache_creation_input_tokens` 실측(spawn-event-v1 또는 count_tokens).

**(d) env 캐리어 divergence + PL self-spawn 금지**

PL 은 worker 를 **스스로 spawn 할 수 없다**(re-entrancy 3종: 재귀 spawn 금지·nested team 금지·one-team-per-lead — `DeveloperPLAgent.md:271` + ADR-009 wrapper-only). 위임의 실 mechanism:

| env | 위임 캐리어 |
|---|---|
| env=1(`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | PL → team worker **SendMessage** dispatch(self-contained — §결정 8 + DeveloperPLAgent.md:269) |
| env=0(미활성) | PL **work-request 반환** → **Orchestrator read-worker pre-spawn**(PL self-spawn 금지 — ADR-009 + DeveloperPLAgent.md:269) |

D1 prose 는 절대 "PL spawns workers" 로 쓰지 않는다(env=0=ADR-009 위반). 동형 precedent = §결정 9/§결정 10 chief-author multi-step "env=0 = sequential Agent tool calls(Orchestrator)". **INV-1**: env=0 carrier 가 self-do escape-hatch 금지 — Orchestrator pre-spawn 이 더 많은 step 이라는 이유로 PL 이 비-essential inline-read 금지(carrier 만 다름, 의무 동일).

**(e) tier 비대칭 — CFP-1438 확장**

CFP-1438(chief-author span 분할)은 RECOMMENDATION tier(§결정 9 + ADR-039 §결정 17 "monolithic span 채택 시 결격 0" = 미강제). 본 §결정 11 은 같은 family(fat-agent discipline)이나 DISJOINT mechanism(CFP-1438 = 시간-span 분해 / CFP-2521 = read/compute 경계) — 그 라인의 **확장(extends)**. tier = prompt-mandate(behavioral, permission 강제 불가) — enforcement 는 ADR-039 Amendment 8 §결정 9 D3 advisory + ADR-060 evidence-gate 로 deferred.

**불변 보존 (약화 0건)**:
- §결정 1 phase-scoped sequential team lifecycle invariant 무변경.
- §결정 8 env=0/env=1 분기 SSOT 무변경(재해석·정합·확장만).
- **ADR-039 §결정 2 inline whitelist 4-entry closed enumeration 무변경** — **PL read/compute boundary = disjoint axis**(Orchestrator inline whitelist 과 다른 차원). 5번째 whitelist entry 신설 0(ADR-039 §결정 2 line 161 "5번째 카테고리 추가 = ADR-039 amendment 의무" — 본 amendment 은 그것을 하지 않음, disjoint 축이므로).
- §결정 3 Ownership≠Mechanism 무손상(§8/§8.5 self-write ownership 보존, mechanism 만 변경).

**Phase 분리**: 본 §결정 11 = Phase 1 declarative. Phase 2 = DeveloperPLAgent.md "컨텍스트 경계 규약" prose 신설(D1) + D3 advisory lint(opt-in spawn-event-v1 enable, ADR-039 Amendment 8 §결정 9 slot) = 별 carrier.

**Holder generalization (cross-ref stub, Amendment 없음 — ADR-142 anchor, CFP-2572)**: 본 §결정 11 thin-PL context boundary 는 **holder=lane-PL** scope 다. 동일 mandate((a) self-do 금지 prompt-mandate / (b) essential carve-out CLOSED / (c) re-read persistence 트리거 / (d) env 캐리어)를 **holder=Orchestrator-self** 로 일반화한 것이 **ADR-142**(Orchestrator-self READ/synthesis/verbose-return 규율). ADR-142 는 본 §결정 11 을 재결정하지 않고 holder 축을 확장하는 disjoint anchor 이며, Orchestrator-self trivial-read carve-out(신규 CLOSED 6항목)을 별도 열거한다.

**Verification evidence**:
- §결정 1/§결정 8 본문 무변경 verify(lifecycle/env 분기 무손상).
- ADR-039 §결정 2 4-entry 무변경 + disjoint-axis verify(archive/adr/ADR-039-...:150-161 직접 Read — line 161 "5번째 카테고리 추가 = amendment 의무").
- essential carve-out anchor verify(DeveloperPLAgent.md:80-99/178/191/196-238/262-271 직접 Read).
- env=0 self-spawn 금지 verify(DeveloperPLAgent.md:269/271 + ADR-009 re-entrancy 3종).
- tier 비대칭 verify(ADR-039 §결정 17 "monolithic span 채택 시 결격 0" = recommendation tier 직접 Read).

### 결정 12 — check-verification-floor.sh 축③ (peer-completion falsifiability) — Amendment 6 (CFP-2597, Epic CFP-2597 review-PL delivery-gap 기계화 Phase 2)

**배경**: §결정 10 (Amendment 4) 이 lane verification floor 를 명문화하고 `check-verification-floor.sh` 에 **축①**(self-audit peer_count:0 verdict 무효) + **축②**(silent 2→1 degrade 차단) mechanical 검출을 두었다. 그러나 축①/②는 `peer_degrade` block(자기단언 int/bool)만 관측한다 — PASS verdict 이 **peer 가 실제로 완료했다는 artifact 증거**를 동반하는지는 검증하지 않는다. mctrader 데뷔 감사 delivery-gap class (fidelity-critical PASS 가 peer 완료증거 없이 새는, spawn-then-blind-wait 진원)의 강제력 복구를 위해 본 §결정 12 = `check-verification-floor.sh` 의 **3번째 축(축③ — peer-completion falsifiability)** 을 추가한다.

> **★ 명칭 disambiguation (CRITICAL)**: 본 §결정 12 의 "축③"은 **`check-verification-floor.sh` 의 축③ (peer-completion falsifiability)** 이다. §결정 10 (d) 의 **`check-lane-evidence.sh` 축③ (deputy/role:dev fan-out enforcement)** 와 이름만 같고 **대상 script·axis 가 disjoint** — 서로 다른 게이트다. 인용 시 반드시 script 명을 붙여 구별한다.

**(a) 게이트 대상 = review-verdict-v4 §19 peer_verdicts[] (v4.16, additive MINOR)**

축③의 관측 대상 = review-verdict-v4 `peer_verdicts[]` verdict-level optional array (v4.16 — 본 Amendment 6 paired MINOR bump). 각 entry 5-key = ADR-068 I-6 existence-verify-annotation 3-key (`form: file-path-reference` / `target`: peer transcript·verdict artifact 상대경로, verdict file dir 기준 / `verify_status`) + `worker`(claude|codex) + `worker_recommendation`(그 peer 의 verdict token, content-binding). `peer_verdicts[]` 는 `peer_degrade.peer_count`(int 자기단언) 를 **보강**(대체 아님) — 각 peer 발화의 artifact-backed 완료 증거.
> source: ADR-068 I-6 audit-gate-pointer-existence invariant (form/target/verify_status 3-key) 재사용. review-verdict-v4 §19 v4.16 = 본 Amendment 6 paired carrier.

**(b) 발동 조건 + 판정 (full-tighten (Q))**

- **precondition** = `pl_recommendation == PASS` **AND** NOT honest-single-peer-degrade (`peer_degrade.peer_count:1` ∧ `degrade_acknowledged:true` ∧ `degrade_reason` — 3-조건 AND).
- **발동 시 판정**: `peer_verdicts[]` ≥1 entry **AND** 각 `target` (= `dirname(verdict_path)` 기준 상대경로) 이 **check시점 FS 실재 + non-empty** 임을 게이트가 **독립 stat** — 자기단언 `verify_status` 불신 (attestation ≠ ground truth, ADR-119 §결정 10).
- **축 분담 (무회귀)**: `peer_count:0`+PASS = **축① 선차단** (self-audit verdict 무효) → 축③ 미도달. honest-single-peer-degrade = **축② 위임** (silent degrade 차단 영역) → 축③ **stand-down** (AC-A3 — honest degrade 경로 무회귀 보장).
- **위반 처리**: 미충족 → 위반. **warning-tier** = advisory (exit 0) / `--strict` = exit 1. bare-PASS (`peer_verdicts` 부재) 및 `peer_count:2`-위조 (2 주장인데 artifact 미동반) 재분류 = **RED**.
- **non-version-gated** (anti-evasion): 게이트는 `contract_version` 조건 없이 발동 — 구 버전 선언으로 회피 차단.

**(c) 원칙 SSOT 신설 0 — cross-ref only**

본 §결정 12 = mechanical 게이트 codify 이지 **원칙 재정의가 아니다**. 원칙 SSOT:
- [ADR-139](ADR-139-background-wait-liveness-gate.md) **INV-L2** (stall ≠ PASS, 미측정 → inconclusive — peer 미완료를 PASS 로 승격 금지) + **§결정 7** (spawn-then-blind-wait 금지, collect = auto-wake LEAD 소유, INV-L4 대기주체↔판정주체 분리).
- [ADR-119](ADR-119-research-before-claims.md) §결정 10 outcome-honesty (self-attestation 불신, ground-truth stat).
- **all additive** (T1 미발동) — verdict-v4 v4.16 optional array + warning-tier lint, 기존 축①/② 및 §결정 10 본문 무변경.

**(d) 정직한 한계 (hollow-gate 금지) — §3.4**

축③ = **위조비용 상향 + audit trail** 이지 **위조방지 게이트가 아니다**. PL 이 claim(verdict) 과 proof(peer_verdicts) 를 **동시 저작**하는 한 full falsifiability 는 불가 — `peer_verdicts` omit 시 (bare-PASS RED 로 잡히나 peer_count 자기단언 우회 가능성) 잔존. **warning-tier = 정직 상한** (독립 3rd-party attestation 부재 인정), blocking 승격 = **false assurance** (peer artifact 자체가 PL 저작). full falsifiability = **Epic trapdoor** (stop-event 강화 or spawn-event-v1 선행 — independent-observer attestation substrate) 로 defer.

**불변 보존 (약화 0건)**:
- §결정 1 phase-scoped sequential team lifecycle invariant 무변경.
- §결정 2 dispatch_mode SSOT 무변경 (Codex ad-hoc-only 약화 0건).
- §결정 10 축①(self-audit peer_count:0 무효) / 축②(silent degrade 차단) 무변경 — 본 축③은 그 위에 얹히는 3번째 축 (재해석·확장만).
- branch protection 6-tuple 무변경 + warning-tier 상속 (ADR-128).

**Phase 분리**: 본 §결정 12 = Phase 2 mechanical wire 의 governance-doc carrier (review-verdict-v4 v4.16 + MANIFEST mirror + review-pl-base §3/§10 + orchestrator-playbook §3.10.1 active-resume/I-6.6 + evidence-checks-registry entry + ADR-060 Amendment 21 paired). 실 script (`scripts/check-verification-floor.sh` 축③ logic) + workflow + discriminating test = sibling worker Phase 2 deliverable.

**Verification evidence**:
- §결정 10 축①/② 본문 무변경 verify (축③ = 위 append, 약화 0건).
- ADR-068 I-6 existence-verify-annotation 3-key (form/target/verify_status) 재사용 verify.
- ADR-139 INV-L2/L4 + §결정 7 collect=LEAD 원칙 SSOT cross-ref verify (원칙 신설 0 — mechanical 게이트만).
- check-lane-evidence.sh 축③ (§결정 10 (d) fan-out) ↔ check-verification-floor.sh 축③ (본 §결정 12 peer-completion) disambiguation verify (이름만 동일, script·axis disjoint).
- 정직한 한계 honest 표기 verify (warning-tier = 정직 상한, blocking 승격 = false assurance 명시 — full falsifiability = Epic trapdoor defer).

## 결과

### 긍정

- ADR-035 D2 implementation level SSOT 확보 — Phase-scoped sequential team lifecycle / team-spec yaml 7종 / hook 3종 / review-verdict v3 → v4 cutover 통합
- `/resume` no-resumption risk 회피 (Phase-scoped = lane 별도 짧은 lifecycle)
- Lane PL ↔ Worker continuous dialog 가능 (SendMessage round) — 토큰 비효율 회피 (사용자 directive turn 5+8 정합)
- Adversarial debate measurable (worker_dialog_rounds field) — 5 권장 패턴 Adversarial 검증 가능
- review-verdict v4 단순화 (Sonnet decider 영역 정식 제거) — 8-value state machine → 4-step linear path
- env-divergent fallback (env=0 시 ADR-039 default) — backward compat 보장 (env=1 미활성 사용자 영향 0)
- ADR-009 wrapper-only invariant 무손상 (lead = Orchestrator 단일 fixed)
- ADR-039 always-spawn invariant 무손상 (env=0 default 유지, env=1 시 mechanism 만 enrich)

### 부정 / 비용

- **권장 3-5 명 초과** (Design 8명, Develop 5-7명) — 25 thread 한도 내. Specialization 패턴 정합으로 허용 (ADR-035 §결과 + Story §5.1 verification matrix).
- **Experimental status (agent teams)** — production stability 미보증. mitigation = Hotfix path 유지 + SessionStart hook env 검증 + env=0 fallback 영구 유지.
- **review-verdict v4 BREAKING** — consumer scope 0건이지만 기존 v3 NO-OP passthrough annotation 정리 + canonical sync follow-up PR 의무.
- **6 lane plugin sibling sync follow-up** — wrapper Phase 1 PR merge 후 6 PR pair (ADR-010 wrapper-first, Story §5.5 B1 default 채택).

### 위험

- **TeammateIdle hook 미발화 시 idle teammate 누적** → 25 thread 한도 초과. mitigation = TeamDelete 시 in-flight 명시 wait + script GC. 본 ADR §결정 1 lifecycle step 5 명시.
- **Rate limit hit 빈도 ↑ (다수 teammate 병렬 spawn)** — agent teams enabled 시 self-evident. mitigation = team-spec yaml `teammates[]` 수 제한 (Design 8명 / Develop 5-7명). default subagent context (env=0) 에서는 자연 mitigation (one-shot 순차).
- **Codex worker 사용자 미요청 시 default 미발화** — 사용자가 explicit request 누락 시 review lane Adversarial 패턴 미발화. mitigation = consumer-guide 안내 + review verdict packet 의 `worker_dialog_rounds` 가 0인 경우 PL 단독 합의 명시. Story §2.4 정합.
- **SendMessage secret 노출** — sibling teammate 끼리 system prompt / tool output 공유 (Anthropic platform behavior). mitigation = consumer-guide §"secret hygiene" 안내 + 본 ADR 결정 7 명시.

## 회피된 대안

| 대안 | 거부 이유 |
|---|---|
| **Story-long single team** | `/resume` 후 in-process teammate 미복원 위험 (도메인 지식 entry §"`/resume` risk"). Phase-scoped = lane 별도 짧은 lifecycle 으로 mitigation. ADR-035 D2 §근거 정합. |
| **Nested team / team-of-teams** | codeforge 정책 nested team 금지 (re-entrancy 제약 3종). team-spec yaml depth 1 강제. |
| **6 lane plugin self-write 보유 sibling sync 동시 (Phase 1 PR pair)** | wrapper-first (ADR-010 §4 허용 패턴) 가 사용자 turn 11 directive ("worktree 해서 작업") + memory `feedback_internal_docs_branch_safety.md` + Story §5.5 B1 default 와 정합. 동시 7 PR pair 는 reviewer cognitive load + merge order race. wrapper-first 후 follow-up PR 6개 채택. |
| **review-verdict v4 deprecation period 6개월** | consumer scope 0이라 불필요 overhead. 즉시 cutover (Story §5.5 R3 default 채택) 가 단순. |

## ADR 정합성

- **ADR-009** (wrapper-only decomposition) — Orchestrator 단일 lead invariant 무손상 (§결정 1 lead 고정).
- **ADR-022** (Deprecated by ADR-035) — review-verdict v4 cutover 가 ADR-022 본문 잔재 cleanup 일부 (decision-packet-v2.1 / Sonnet decider 영역). 잔재 doc cleanup 은 본 ADR scope 외 (CFP-137 follow-up CFP).
- **ADR-024 + ADR-040** (worktree convention) — §결정 1 lifecycle step 2 (`(CFP-139 후) GitOpsAgent SendMessage`) 가 ADR-040 hook contract 정합.
- **ADR-031** (lane-spawn evidence) — §결정 3 hook 3종 (TaskCreated / TaskCompleted) 가 §14 row append mechanism. ADR-031 Amendment 1 (Orchestrator-owned delegate inclusion) 가 본 ADR 정합.
- **ADR-035** (Epic architecture) — D2 = Phase-scoped sequential team 의 implementation level SSOT 본 ADR. ADR-035 §amendment_log[0] = `planned → applied` flip (CFP-137 carrier 본 Story).
- **ADR-039** (Orchestrator subagent default) — env-divergent fallback (§결정 8). env=0 default subagent context = ADR-039 always-spawn invariant 유지. env=1 enabled context = mechanism enrichment (continuous dialog), ownership 무변.

## CFP-676 reaffirm — flat spawn invariant (codeforge-design lane 4-tuple)

> **reaffirm 단락 (신규 §결정 아님 — 본 ADR-044 §결정 1~8 본문 변경 0건)**. CFP-1026 S1 ([ADR-042](ADR-042-agent-model-selection-policy.md) Amendment 7 atomic carrier) 의 design lane agent 구조 재편이 CodebaseMapperAgent / RefactorAgent / ArchitectAnalystAgent (신규, PriorArtAgent rename) 를 "4-tuple" 로 그룹핑함에 따른 invariant reaffirm. **본 단락은 nested team / sub-lead 격상 / team-of-teams 의 신규 가능성 도입 0건** — 기존 flat spawn invariant 의 재확인 (reaffirm only, Codex S-CFP676-FLAT-SPAWN P2 binding).

**"4-tuple" = 논리적 그룹핑 (물리적 spawn 계층 아님)**:

CFP-1026 S1 이 CodebaseMapper / Refactor / ArchitectAnalyst 를 design lane sub-agent "4-tuple" (chief author 포함 시 4 — ArchitectAgent chief + 3 sub-agent) 로 명명하나, 이는 **어떤 sub-agent 가 어느 deputy 영역 Context Packet 으로 Orchestrator flat spawn 됐는지** 의 논리적 그룹핑 (spawn-time Context Packet specialization — overlay 정적 메커니즘과 구분, playbook §12 / [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) 정합). 물리적 spawn 계층 (sub-agent 가 sub-agent 를 spawn) 아님. deputy sub-lead 격상 0건 보존.

**flat spawn invariant SSOT (본 ADR-044 기존 보유 — CFP-676 신규 도입 0)**:

본 ADR-044 는 flat spawn invariant 를 이미 다음 위치에 보유 (CFP-676 reaffirm = 아래 anchor 의 재확인만):

- 본 ADR-044 `## 회피된 대안` 표 "Nested team / team-of-teams" row — "codeforge 정책 nested team 금지 (re-entrancy 제약 3종). team-spec yaml depth 1 강제."
- 본 ADR-044 `## 외부 fact` 단락 — "one-team-per-lead 강제 (codeforge 정책 + platform 동일) / 재귀 spawn 금지 + nested team 금지 (codeforge 정책 SSOT)"
- [ADR-009](ADR-009-wrapper-only-decomposition.md) — Orchestrator (top-level Claude 세션) **단일 lead invariant** (본 ADR-044 `## ADR 정합성` ADR-009 row 가 cross-ref)
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) §결정 1 — default subagent context 의 재귀 spawn 금지 (Lead·teammate 공통, platform inherent)

> **인용 정확성 mandate (Story §5.2 AC-7 / Codex CX-676-TP4-3 fact-check 정합)**: CFP-676 carrier 가 flat spawn / nested team 금지 / one-team-per-lead 를 인용할 때 본 ADR-044 **§결정 1 직접 인용 금지**. §결정 1 = "Phase-scoped sequential team lifecycle (ADR-035 D2 implementation)" 으로 flat spawn invariant 의 직접 근거 아님 (lifecycle sequence 정의). 정확 인용 위치 = 위 4 anchor (회피된 대안 표 + 외부 fact 단락 + ADR-009 단일 lead + ADR-039 §결정 1). §결정 1 mis-citation = wording SSOT (ADR-068 I-4) 위반 → 경량 설계리뷰 FIX.

**CFP-676 적용 사례 (4-tuple flat spawn)**:

design lane sub-agent (CodebaseMapper / Refactor / ArchitectAnalyst) 는 ArchitectPLAgent 의 deputy spawn 결정 시 Orchestrator 가 **flat spawn** (각 sub-agent 에 영역별 Context Packet 주입 — CodebaseMapper = existing codebase fact / Refactor = pattern advocacy / ArchitectAnalyst = 기존 설계 (ADR/Change Plan/Story) 분석). chief author (ArchitectAgent, Opus) 가 multi-source synthesis (sub-agent 산출물 + 5 permanent deputy 산출물 dedup + 종합). sub-agent 간 직접 통신 / sub-agent 의 추가 spawn / sub-lead 격상 0건 — 기존 invariant 무손상 (env=0 default subagent context = one-shot Agent tool, env=1 = SendMessage sibling teammate 통신 but 재귀 spawn / nested team 여전히 금지 — 본 ADR-044 §결정 1 "거절된 대안 (C)" + `## 외부 fact` SSOT 정합).

**Scope 경계**: 본 reaffirm 단락 = ADR-044 정책 SSOT 무변경 declare 만. design lane sub-agent file (ArchitectAnalystAgent 신설 등) 실 작성 = W2 S3 (codeforge-design sibling). 본 CFP-676 S1 = wrapper 정책 SSOT (ADR / CLAUDE.md / skill) 만 (doc-only fast-path — [ADR-054](ADR-054-doc-only-story-fast-path.md)).

## 외부 fact (도메인 지식 entry SSOT)

`docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md` (CFP-137 신설) 가 외부 reference SSOT. Anthropic Claude Code experimental agent teams docs 의 verbatim transcribe 가 아니라 codeforge 내부 정책 SSOT — 외부 docs link rot risk 회피.

핵심 fact:
- TeamCreate / TeamDelete / SendMessage / TaskList / TeammateIdle hook = experimental feature, env=1 시 노출
- one-team-per-lead 강제 (codeforge 정책 + platform 동일)
- 재귀 spawn 금지 + nested team 금지 (codeforge 정책 SSOT)
- `/resume` 후 in-process teammate 미복원 — Phase-scoped sequential team 채택 motivation

## Out-of-scope

- 6 lane plugin agent prompt 갱신 (sibling sync follow-up PR — ADR-010 wrapper-first 절차)
- codeforge-review plugin canonical review-verdict-v4.md write (sibling sync follow-up — wrapper Phase 1 PR merge 후)
- develop-output v1 → v1.1 MINOR bump (cross-layer measurable verification, codeforge-develop sibling sync follow-up)
- `scripts/check-lane-evidence.sh` lint 확장 + `scripts/check-fix-evidence.sh` 신설 (Phase 2 PR scope 또는 follow-up CFP)
- Phase 2 PR e2e fixture (env=1 / env=0 dry-run 검증 row, team-spec yaml schema lint, review-verdict v4 schema migration test, hook 3종 trigger 검증)
- consumer 측 적용 본격 가이드 (별도 CFP — CFP-134 spec §8 out-of-scope)
- Hotfix path 의 agent teams 통합 (hotfix-playbook.md amendment 별도)
- ADR-022 본문 잔재 cleanup (CFP-137 follow-up CFP)

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-035 (Epic architecture)](ADR-035-codeforge-agent-teams-epic-architecture.md) — D2 implementation level carrier 본 ADR. §amendment_log[0] = `planned → applied` flip 동행.
- [ADR-039 (Orchestrator subagent default)](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — default subagent context invariant. env-divergent fallback 정합.
- [ADR-040 (Worktree convention)](ADR-040-worktree-convention.md) — TeamCreate / Delete + worktree integration hook contract.
- [ADR-031 (Lane-spawn evidence)](ADR-031-lane-spawn-evidence-trail.md) — hook 3종 (TaskCreated / TaskCompleted) 가 §14 row append mechanism.
- `docs/inter-plugin-contracts/review-verdict-v4.md` — 본 ADR 결정 4 carrier (wrapper sibling, canonical = codeforge-review plugin).
- `docs/inter-plugin-contracts/MANIFEST.yaml` — review_verdict.files[] v4 entry append.
- `docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md` — 도메인 지식 entry SSOT.
- `templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml` — 7 yaml.
- `templates/.claude/hooks/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample` — 3 hook sample.
- `docs/orchestrator-playbook.md` — §3 amendment (§3.6-§3.9 신설).
- `docs/consumer-guide.md` — § "Agent teams 적극 도입 (CFP-137)" 신설.
- `CLAUDE.md` — "Agent teams enabled context 별도" 단락 expansion (1 paragraph stub → 본격 SSOT cross-ref).
- **CFP-134** — Epic carrier.
- **CFP-137** — 본 ADR carrier Story (Wave 2).
- **CFP-139** — GitOpsAgent (lifecycle 자동화 후속, Wave 3).
