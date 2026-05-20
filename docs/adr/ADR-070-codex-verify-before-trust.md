---
adr_number: 70
title: Codex verify-before-trust pattern (sandbox access invariant)
status: Accepted
category: workflow-policy
date: 2026-05-13
carrier_story: CFP-578
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    cfp: CFP-776
    date: 2026-05-17
    scope: "ADR-082 cross-ref 보완 관계 명시 (disjoint 보완) — ADR-070 = 외부 worker(Codex) output verify 한정 ↔ ADR-082 = internal lane agent self-write(§9 evidence / Phase 0 mapping / corpus enumeration) write-time semantic truth verify. 두 layer disjoint, scope 침범 0. ADR-082 §결정 1 layer disjoint 4-layer 표가 공통 anchor (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D). ADR-070 D5 declaration-only retain 패턴 = ADR-082 §결정 6 known-limitation 선례. 본문 D1-D5 의미 변경 없음 — cross-ref-only Amendment."
    status: applied
    ref: "## Amendments / Amendment 1 + ADR-082 §결정 1 / §결정 6"
    sunset_justification: null
  - amendment_id: 2
    cfp: CFP-844
    date: 2026-05-17
    scope: "ADR-081 §결정 D6 (Codex worker severity calibration rubric, Amendment 1) cross-ref 보완 관계 명시 (disjoint). ADR-070 = Codex finding evidence 의 factual ground truth verify (file content direct Read, mismatch 시 verdict reject) ↔ ADR-081 §결정 D6 = Codex finding 의 severity 경중 calibration (Codex severity ↔ PL synthesis severity bidirectional, ground truth = DesignReviewPL/CodeReviewPL final verdict severity). 두 layer disjoint — ADR-070 = 사실 근거 layer (finding evidence 가 ground truth 와 일치하는가) / ADR-081 D6 = severity 경중 layer (finding severity 가 review lane ground truth severity 와 정합하는가). scope 침범 0. ADR-070 §D5 declaration-only retain 패턴 = ADR-081 §D5 / §결정 D6.e known-limitation 직접 선례 (ADR-082 §결정 6 선례 chain 연속). 본문 D1-D5 의미 변경 없음 — cross-ref-only Amendment."
    status: applied
    ref: "## Amendments / Amendment 2 + ADR-081 §결정 D6 (Amendment 1)"
    sunset_justification: null
  - amendment_id: 3
    cfp: CFP-946-A
    date: 2026-05-18
    scope: "§결정 1 substitution scope 3-path enum codify — default `inline_orchestrator_verify` / `manual_substitution_declare` / `fallback_skip_with_marker`. D1 본문 default behavior 의미 보존 (default = `inline_orchestrator_verify` 명시), 거절된 대안 D1-A/B/C 본문 의미 변경 없음. 6 touchpoint × 3-enum cross-matrix = ADR-052 Amendment 8 본문 cross-ref. Codex sandbox 9 occurrence sentinel (CFP-756 Epic close retro Sentinel #4 strike #8, parent_epic CFP-946 P1 escalate_user) 산물. ADR-070 D5 declaration-only retain precedent 정합 (mechanical_enforcement_actions: [] retain). Amendment 1 (ADR-082 cross-ref) + Amendment 2 (ADR-081 §D6 severity calibration cross-ref) 본문 의미 변경 없음."
    status: applied
    ref: "## Amendments / Amendment 3 + ## 결정 / D1 expansion"
    sunset_justification: null
  - amendment_id: 4
    cfp: CFP-988
    date: 2026-05-19
    scope: "신규 §결정 D6 — mandatory-real-execution-evidence STANDING normative codify + Epic-gate verify-don't-dismiss sub-clause. E-1 (DeveloperPL false-self-claim lineage pattern_count=4: CFP-699 + CFP-702 + CFP-899 + CFP-900-iter0/iter1) → STANDING 4-tuple (a) CR-own discriminating revert / (b) reconcile-integration path / (c) DevPL pasted stdout 미신뢰 / (d) single-aggregator/single-unit bypass forbidden. E-2 (Epic IntegrationTestAgent flagged 'non-blocking observation' verify-don't-dismiss STANDING super-class) → Epic close 전 미verify flagged observation in deliverable domain = Epic close 차단 invariant. ADR-070 §결정 D1 scope (Codex external worker output) ratchet-up direction 확장 — DevPL self-claim + IntegrationTestAgent flagged observation 영역 일반화 (ADR-082 §결정 1 disjoint 4-layer 표 scope 침범 0 verify, ADR-082 = write-time semantic truth layer 와 disjoint axis = read-time attestation 신뢰성). ADR-070 §D5 declaration-only retain precedent chain 4번째 instance — `mechanical_enforcement_actions: []` retain (Amendment 1/2/3 패턴 정합, Q1-A/Q2-A/Q3-A 채택 doc-only fast-path 적격). is_transitional: false (permanent — 약화 차단 ratchet, ADR-058 §결정 5 sunset_justification ratchet-up direction). ADR-045 §D-9 cross-Story pattern forcing function origin (pattern_count=4 ≥ threshold 2 mandatory adr_draft_emitted). ADR-055 Epic IntegrationTest gate (E-2 catching layer SSOT). ADR-067 max FIX 3/3 cycle axis disjoint (per-iteration verify content ↔ post-failure boundary reassessment) — cycle conflict 0건. D1-D5 + Amendment 1/2/3 본문 의미 변경 없음 — 신규 §결정 D6 추가 only."
    status: applied
    ref: "## Amendments / Amendment 4 + ## 결정 / D6"
    sunset_justification: null
  - amendment_id: 5
    cfp: CFP-1003
    date: 2026-05-19
    scope: "§결정 D1 적용 scope L107-L111 본문 강화 — reactive `codex:rescue` 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역) 의 normative anchor codify. 기존 D1 L110 본문 `codex:rescue 사용자 ad-hoc 채널 — 사용자 책임 영역 (적용 외)` 보존 invariant 정합 + 사용자 책임 영역 안에서도 user-initiated invocation 시 D1 verify-before-trust pattern + D2 verbatim 첨부 + D3 verdict reject 흐름 + Amendment 3 substitution scope 3-path enum 의 적용 권장 (사용자 ad-hoc 영역의 normative anchor RETAIN — codeforge 측 강제 미발효, 사용자 ad-hoc 책임 영역에 대한 best-effort 가이드 anchor only). ADR-052 Amendment 9 + ADR-081 Amendment 5 chain — Codex TP#4 CX-963 deferred scope (CFP-963 §6.3 OOS + §3 EC-2 reactive codex:rescue network_scope = OUT derived default) closure. D1 본문 L107-L111 적용 scope 표 + Amendment 3 substitution 3-enum + D2 verbatim 첨부 의무 = proactive 6 touchpoint 한정 (codeforge 강제 invariant 정합) + reactive 채널 = best-effort 가이드 anchor (사용자 책임 영역 retain). D1-D6 + Amendment 1/2/3/4 본문 의미 변경 0건 — D1 적용 scope L107-L111 표 안 reactive 영역 row 의 anchor codify only. ADR-070 §D5 declaration-only retain precedent chain 5번째 instance — `mechanical_enforcement_actions: []` retain (Amendment 1-4 패턴 정합). is_transitional: false (permanent governance, ratchet 강화 방향 only — reactive 영역 사용자 책임 boundary 보존 + best-effort 가이드 anchor 강화). ADR-058 §결정 5 sunset_justification N/A (강화 방향, scope 축소 0). ADR-064 §결정 1 (CFP scope unitary) 정합 — Wave 1 declarative-only / Wave 2 mechanical lint = 별 CFP carrier 분리. ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-1003)."
    status: applied
    ref: "## Amendments / Amendment 5 + ## 결정 / D1 적용 scope L107-L111"
    sunset_justification: null
  - amendment_id: 6
    cfp: CFP-1056
    date: 2026-05-20
    scope: "§결정 D1 expansion (Amendment 3) fail-mode 6-set → 7-set 확장 — `subagent_recursion_blocked` 7번째 enum value 추가. CFP-1041 DesignReview lane PL spawn = Agent SDK subagent context (recursive Agent tool spawn blocked by ADR-039 platform-inherent recursion guard) 시 Codex worker subagent spawn 차단 evidence. 본 Amendment 는 fail-mode enum 의 ratchet-up 확장 only (6-set retain + 7번째 append) — D1-D6 + Amendment 1-5 본문 의미 변경 0건. ADR-052 Amendment 10 cross-ref binding (6 touchpoint × 3-path enum cross-matrix 안 fallback_skip_with_marker 의 fail-mode 7-set 동기 정합). ADR-070 §D5 declaration-only retain precedent chain 6번째 instance — `mechanical_enforcement_actions: []` retain. is_transitional: false (permanent — ratchet 강화 only, scope 축소 0). ADR-058 §결정 5 sunset_justification N/A. ADR-054 §결정 1 doc-only fast-path 적격 (carrier CFP-1056 — 기존 ADR Amendment + ADR-052 cross-ref Amendment + Story file, src/tests 무변경)."
    status: applied
    ref: "## Amendments / Amendment 6 + ## 결정 / D1 expansion (Amendment 3) fail-mode enum"
    sunset_justification: null
related_stories:
  - CFP-578  # carrier
  - CFP-506  # sentinel 1 reproduce
  - CFP-520  # sentinel 2 reproduce (skip option B)
  - CFP-530  # sentinel 3 reproduce (ADR 발의 timing 도달)
  - CFP-776  # Amendment 1 — ADR-082 cross-ref (disjoint 보완)
  - CFP-844  # Amendment 2 — ADR-081 §결정 D6 severity calibration cross-ref (disjoint 보완)
  - CFP-946-A  # Amendment 3 — §결정 1 substitution scope 3-path enum codify (parent_epic CFP-946)
  - CFP-988  # Amendment 4 — mandatory-real-execution-evidence STANDING + Epic-gate verify-don't-dismiss (E-1 pattern_count=4 + E-2 super-class)
  - CFP-1003 # Amendment 5 — reactive `codex:rescue` 채널 normative anchor codify (사용자 책임 영역 retain + best-effort 가이드 anchor 강화, ADR-052 Amd 9 + ADR-081 Amd 5 chain — Codex TP#4 CX-963 deferred scope closure)
related_adrs:
  - ADR-052  # Codex proactive check 6 touchpoint
  - ADR-081  # Codex worker severity calibration rubric §결정 D6 (Amendment 2 disjoint 보완 — 사실 근거 layer ↔ severity 경중 layer)
  - ADR-082  # disjoint super-class (internal lane agent self-write verify — 외부 worker output ↔ lane agent self-write; D5 declaration-only retain 선례)
  - ADR-022  # Codex review 자동 발동 Deprecated (CFP-134 / ADR-035)
  - ADR-060  # evidence-enforceable promotion framework
  - ADR-040  # mechanical_enforcement_actions self-application 패턴
  - ADR-064  # decision principle mandate (forbid-list 8 어휘)
  - ADR-059  # debate-protocol-v1 (영역 분리)
  - ADR-039  # default subagent context (env=0 정합)
  - ADR-045  # §D-9 cross-Story pattern forcing function — Amendment 4 forcing function origin (pattern_count=4 ≥ threshold 2 mandatory adr_draft_emitted)
  - ADR-055  # Epic IntegrationTest gate — Amendment 4 E-2 sub-clause catching layer SSOT (flagged observation discipline)
  - ADR-067  # Max FIX 3/3 + RESET — Amendment 4 STANDING 의 per-iteration verify content 와 axis disjoint (post-failure boundary reassessment)
related_files:
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/orchestrator-playbook.md
  - CLAUDE.md
  - docs/evidence-checks-registry.yaml
is_transitional: false
mechanical_enforcement_actions: []
---

# ADR-070: Codex verify-before-trust pattern (sandbox access invariant)

## 상태

Accepted (2026-05-13 KST, CFP-578 carrier).

## 컨텍스트

codex:codex-rescue subagent (ADR-052 Codex Proactive Check 6 touchpoint 자동 dispatch 채널) 가 wrapper repo working directory 영역 외 file path (internal-docs / sibling repo / cross-plugin path) 에 대해 sandbox-level access 차단됨을 3 회 reproduce 누적 evidence 확보:

| Sentinel | Story | 일자 | 발견 영역 | 결과 |
|---|---|---|---|---|
| 1 | CFP-506 | 2026-05-13 | touchpoint #4 file Read 시도 → ERR `경로는 존재하지 않으므로 찾을 수 없습니다` | Orchestrator file content verbatim 첨부 후 re-spawn → 정상 audit |
| 1 | CFP-506 | 2026-05-13 | touchpoint #6 (4 findings 발화) | direct file Read verify 결과 4 findings 모두 false positive — Codex 가 ADR-012 Pre-Amendment 본문 (외부 fetch 또는 GPT-5.4 training data 의 stale source) 인용 |
| 2 | CFP-520 | 2026-05-13 | touchpoint 6종 모두 skip rationale 정합 | sandbox access cost 회피 derived default |
| 3 | CFP-530 | 2026-05-13 | touchpoint #6 skip option B Codex sandbox 실패 evidence | sentinel chain closure trigger 도달 (3 회 reproduce 누적) |

**Systemic 원인** (CFP-506 retro §6 verbatim):

> "Codex sandbox file system access 실패가 false positive 의 systemic 원인 — 향후 Codex proactive check 결과 verify-before-trust 채널 필요"

**현 패턴의 risk**:

- (a) Codex worker 가 file Read 실패 시 ERR 응답 — Orchestrator 가 verbatim 첨부 후 re-spawn 해소 (CFP-506 #4 sample)
- (b) Codex worker 가 file Read 실패 시 **silent fallback** 으로 외부 web fetch 또는 GPT-5.4 training data 기반 finding 발화 — Orchestrator 가 verify-before-trust 채널 부재 시 신뢰 → review lane 진입 전 FIX iteration 또는 review lane FIX 발생 (CFP-506 #6 sample, 4 findings 모두 false positive)

(b) 가 systemic 원인. ADR-052 의 6 touchpoint 자동 dispatch 영역에서 Orchestrator 가 Codex finding 의 ground truth 확정 채널 부재 = governance hole.

기존 ADR-052 Amendment 1/2/3/4 는 6 touchpoint 별도 동작 강화 영역 (multi-round debate / iterative reformulation / divergence detection 4번째 영역 / mandatory 전환) 을 커버하나 **Codex 발화 evidence 자체의 신뢰 boundary** 는 normative anchor 부재.

## 결정

### D1. verify-before-trust pattern

Orchestrator 는 codex:codex-rescue subagent (ADR-052 6 touchpoint 자동 dispatch 채널) 가 발화한 모든 "evidence" / "fact source" 인용을 직접 file Read / Glob / Grep 로 verify 의무. Codex 의 외부 fetch 결과 자체는 trust 대상 아님 — Orchestrator 가 own working directory 안에서 ground truth 확정 후 Codex finding accept / reject 결정.

**적용 scope**:

- ADR-052 6 touchpoint 자동 dispatch 영역 — full 적용 (본 ADR 결정 SSOT)
- codex:codex-rescue 사용자 ad-hoc 채널 (ADR-022 Deprecated default 영역) — 사용자 책임 영역 (적용 외)
- CodexReviewAgent (review-verdict-v4 producer, ADR-044 §결정 2 `dispatch_mode: user_request_only`) — 별도 lane scope (적용 외)

**거절된 대안 D1**:

- (D1-A) verify 영역을 Codex worker 의 own working directory 안 file 으로 한정 — sandbox boundary cross-cutting 영역 자체가 본 ADR 의 core scope, 한정 적용은 systemic 원인 해소 영역 외
- (D1-B) Codex worker 의 sandbox 자체 확장 (codex@openai-codex plugin 영역) — codex CLI runtime SSOT 영역, 본 ADR scope 외 (codex@openai-codex plugin 자체 영역)
- (D1-C) verify-before-trust 를 도덕적 강제로 한정 (normative anchor 부재) — 3 회 reproduce sentinel 누적 evidence 가 normative 승격 정당성 충족

### D1 expansion (Amendment 3 / CFP-946-A) — substitution scope 3-path enum codify

기존 D1 default substitution = "Orchestrator inline verify-before-trust" 의 운영적 단일 substitution behavior 를, **substitution path 3-enum** 으로 codify. Default = `inline_orchestrator_verify` (D1 본문 의미 보존). 신규 enum value 2 (`manual_substitution_declare`) + value 3 (`fallback_skip_with_marker`) = 확장 (ratchet 강화 방향, ADR-064 §결정 7 정합). 기존 D1-A/B/C 거절된 대안 본문 의미 변경 없음 (Amendment cross-ref-only).

**substitution path 3-enum (normative anchor SSOT)**:

| Enum value | semantics | 적용 trigger | Story §10 marker (의무) |
|---|---|---|---|
| `inline_orchestrator_verify` (default) | Orchestrator 가 own working directory file Read 로 ground truth 확정 후 Codex finding accept/reject (D1 default substitution behavior 보존) | Codex worker output 정상 수신 (sandbox network-block 없음) + finding evidence 영역 = Orchestrator working directory 안 | (면제 — default behavior, marker 부재 = 암묵 default) |
| `manual_substitution_declare` | Codex worker spawn 직전 substitution scope 명시 declare (spawn prompt `task` field 본문 또는 별도 sub-field `substitution_scope` + Story §10 marker carrier) | sandbox 영역 외 file (internal-docs / sibling repo / cross-plugin path) verify task 필요 시 — Codex output 미수신 가능성 사전 인지 영역 | `[codex-substitution-scope-declared: <scope-enum>]` (1 회/spawn) |
| `fallback_skip_with_marker` | Codex worker spawn 자체 skip + Orchestrator 가 substitution 후속 동작 단독 수행 (verify-before-trust 5 sub-scope 全 적용, ADR-081 §결정 D2) | Codex CLI 미가용 / sandbox network-block 확정 / 8+ occurrence sentinel reentrant 위험 영역 / DesignReviewPL 등 subagent context 안 spawn 시 recursive Agent tool spawn 차단 (Amendment 6 / CFP-1056 신설) | `[codex-sandbox-fallback: <fail-mode>]` (1 회/spawn, fail-mode 7-enum = api_missing / version_skew / enterprise_blocked / gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only / subagent_recursion_blocked) |

**3-enum exhaustive invariant**: 4번째 path 발생 = D1 expansion 거절된 대안 영역 (자동 retry / 외부 verify proxy / multi-source consensus 등). 본 ADR-070 scope 외 — 별 follow-up CFP carrier 영역 (CFP-946-B 도 미포함).

**적용 scope (D1 expansion 6 touchpoint × 3-enum cross-matrix)**: ADR-052 Amendment 8 §A1 표 SSOT 위임 — 본 D1 expansion = substitution path 3-enum 의 normative anchor SSOT (semantics + Story §10 marker 의무 + 적용 trigger). 6 touchpoint 각각의 dispatch prompt template 안 substitution path enum 명시 의무 = ADR-052 Amendment 8 본문 cross-ref.

**verify-before-trust 5 sub-scope 무조건 적용**: substitution path 3-enum 어느 case 채택해도 Orchestrator verify-before-trust 5 sub-scope (file scope grep+quote / dir scope recursive grep+count / cross-repo gh api+commit SHA / grep count claim active vs historical 차원 / ADR §결정 번호 정확성, ADR-081 §결정 D2 SSOT) 무조건 적용. substitution = "Codex worker 가 done 하지 못한 영역의 Orchestrator substitution" 이지 verify-before-trust 면제 아님.

**거절된 대안 D1 expansion**:

- (D1.exp-A) **substitution path 4번째 enum value 추가** (auto-retry / multi-source consensus / 외부 verify proxy 등) — 본 Story-A scope 외 (CFP-946-A §5.3 Out-of-Scope 영역). 별 follow-up CFP carrier 분리. 3-enum exhaustive retain.
- (D1.exp-B) **default substitution path 를 `manual_substitution_declare` 로 변경** (declare 의무 default-on) — D1 default behavior 의미 변경 = backward-compat 위배 (ADR-064 §결정 7 top-down ratchet 위배 — 약화 방향 시 sunset_justification 의무). default = `inline_orchestrator_verify` retain.
- (D1.exp-C) **substitution path enum value 를 review-verdict-v4 contract field 신설** — contract MINOR bump + sibling sync (ADR-008/010) + Phase 2 PR = doc-only fast-path 이탈. ADR-070 §D5 + ADR-081 §D5 + ADR-082 §결정 6 declaration-only retain precedent 위배 → Story §10 prose marker 채택 (A3 SSOT 정합).

### D2. file content verbatim 첨부 의무

Codex worker spawn prompt 안 file path reference 만 사용 금지. 모든 file content 가 verify task scope 인 경우 prompt 안 verbatim 첨부 필수. Orchestrator 가 Codex spawn 직전 file Read 결과를 prompt payload 에 inline.

**적용 file 범위**:

- 모든 sandbox 영역 외 file (internal-docs / sibling repo / cross-plugin path / cross-repo state) — verbatim 첨부 의무
- worktree 안 file 중 codex 의 own working directory 와 mismatch 가능성 (ADR-040 worktree convention 영역) — verbatim 첨부 권장 (Orchestrator 판단 영역)
- 사용자 §1 원문 (story-section-1-immutable.yml SSOT 영역) — 변조 금지 invariant 정합 verbatim 첨부

**file content cap 초과 시 처리** (EC-3 시나리오):

verbatim 첨부 시 prompt size 증가 (token 비용) → Orchestrator 판단:

- 분량 비용 < verify 비용 (false positive 발생 비용) → verbatim 첨부 채택
- 분량 비용 ≥ verify 비용 → file 일부 (verify 대상 영역 only) verbatim 첨부 + 나머지 file path reference 표시 + `[partial: lines NN-NN]` marker 의무

**거절된 대안 D2**:

- (D2-A) file path reference 만 사용 허용 (현 상태 유지) — sandbox access 실패 (a)/(b) 행동 systemic 원인 미해소
- (D2-B) verbatim 첨부 의무 영역을 worktree 외 file 으로만 한정 — codex 의 own working directory 와 wrapper worktree 일치 보장 부재 (ADR-040 worktree convention 영역의 cross-cutting boundary)
- (D2-C) 자동 file content injection layer 도입 (Orchestrator 가 spawn prompt 파싱 → file path reference 자동 verbatim 변환) — Orchestrator turn 내 inline action 영역 외 (별도 carrier, 본 ADR scope 외)

### D3. verdict reject 조건

Codex 가 발화한 "evidence" 가 Orchestrator direct file Read 결과와 mismatch 시 verdict reject (false positive 판정).

**reject 흐름**:

1. Codex worker 결과 수신 → finding evidence (인용 본문 / file path / line number / commit SHA / contract version 등) 추출
2. Orchestrator 가 evidence 영역의 ground truth 를 own working directory 안 Read / Glob / Grep 으로 verify
3. mismatch 검출 시 finding reject + Story §10 FIX Ledger row append (false positive count tally) + Orchestrator override rationale 명시
4. match 검출 시 finding accept (severity / recommendation 기반 후속 동작 정합)

**Story §10 FIX Ledger row 영역** (fix-event-v1 contract 정합):

- 기존 fix-event-v1 schema 의 `events[]` row append — false positive 발생 시 `event_type: codex_false_positive` (schema MINOR bump 별도 carrier 영역, 본 ADR scope 외)
- polyfill (schema MINOR bump 전): 기존 row `comment` 필드 안 `[codex-false-positive]` sub-tag + Orchestrator override rationale verbatim

**Override rationale 의무 항목** (4 종):

1. Codex finding evidence verbatim 인용 (Codex spawn 결과 원문)
2. Orchestrator direct file Read verify 결과 verbatim 인용 (file path + line range)
3. mismatch 영역 명시 (어느 부분이 일치하지 않는가)
4. reject 후속 동작 (Codex finding skip / Story §10 deferred 기록 / 사용자 escalation)

**거절된 대안 D3**:

- (D3-A) 자동 reject (Orchestrator override rationale 의무 면제) — audit trail 확보 영역 부재, false positive count tally 영역 정당성 부재
- (D3-B) reject 시 Codex re-spawn (verify 결과 첨부 후 재발화 요청) — debate-protocol-v1 영역 침범 가능성 (single-side verify 영역과 multi-round adversarial 영역 분리 — D5 정합)
- (D3-C) mismatch 검출 시 자동 PASS (Orchestrator 가 Codex finding 무시) — sentinel 의미 부재 (false positive count tally 부재 = systemic 원인 audit 불가능)

### D4. ADR-052 cross-ref (Amendment 5 sub-section append)

ADR-052 (Codex Proactive Check Touchpoints) 의 `amendments[]` frontmatter 에 Amendment 5 row append + 본문 Amendment 5 sub-section append. 본문 영역 = touchpoint 6 영역 (Codex proactive check 6 touchpoint 자동 dispatch) 의 dispatch prompt template 안 verbatim 첨부 의무 명시.

**Amendment 5 scope**:

- ADR-052 본문 `amendments[]` row 5 append + sub-section append (Amendment 1/2/3/4 패턴 정합)
- playbook §3.10 (Codex Proactive Check SSOT) dispatch prompt template 안 verbatim 첨부 의무 본문 명시
- ADR-052 의 D1/D2/D3/D4 결정 본문 + Amendment 1/2/3/4 본문 의미 변경 없음 — sub-section 만 append

**거절된 대안 D4**:

- (D4-A) ADR-052 Amendment 없이 본 ADR-070 만 신설 — Codex proactive check dispatch 영역의 verbatim 첨부 의무 SSOT 가 ADR-052 본문 cross-ref 부재 시 운영적 정합 약화
- (D4-B) ADR-052 Amendment 만 발의 (본 ADR-070 신설 면제) — verify-before-trust 영역의 normative anchor 가 Amendment sub-section 안에만 존재 = 영역 분리 부족 (ADR-052 의 normative scope = 6 touchpoint 동작 강화, 본 ADR 의 normative scope = Codex 발화 evidence 신뢰 boundary)

### D5. evidence-enforceable framework entry append 면제 (declaration-only retain)

Codex worker 의 sandbox access 실패 = platform inherent (Claude Code agent runtime + codex CLI process boundary). mechanical lint 가 검출 가능한 sentinel signal 영역의 4 후보 모두 robustness risk 보유:

| 후보 signal | 검출 가능성 | 메커니즘 | 적용 risk |
|---|---|---|---|
| (a) Codex spawn prompt 안 file path reference 검출 (regex) | HIGH | static regex on prompt body | false positive — file path 자체는 정합 영역 (verbatim 첨부 동반 시) |
| (b) Codex worker output 안 sandbox access 실패 ERR 패턴 검출 | MEDIUM | output regex (locale-dependent KR: "경로는 존재하지 않으므로 찾을 수 없습니다") | locale 의존 + Codex output schema 영역 외 (안정성 risk) |
| (c) Codex finding evidence 와 Orchestrator file Read mismatch 자동 비교 | LOW | runtime probe (Codex finding evidence verbatim 추출 + Read 결과 verbatim diff) | platform inherent runtime probe 영역, mechanical lint 영역 외 |
| (d) **declaration-only ADR (mechanical lint 부재, 본 ADR 본문 SSOT)** | **HIGH** | 본 ADR 본문 normative anchor 만 | manual gate 의존 (의식 필요) |

**채택 = (d) declaration-only retain**. evidence-checks-registry.yaml entry append 면제.

**근거**:

1. (a)/(b)/(c) 모두 robustness risk 보유 — false positive 차단 cost 가 verify-before-trust 도입 cost 보다 큼
2. ADR-060 evidence-enforceable promotion framework 의 mechanical lint forcing function 확장 패턴 (CFP-389 → CFP-449 → CFP-481 → CFP-506 → CFP-530 carrier loop) 은 **static doc analysis 영역** (ADR frontmatter / forbid-list 어휘 / branch name parse / line count / yml structure) — 본 ADR 영역 (runtime probe / Codex output mismatch detection) 과 영역 type mismatch
3. 후속 carrier sentinel 조건 = 2 회 이상 mechanical lint 검출 가능 sample 누적 시 carrier 발의 (sentinel) — 현재 0 sample 누적

**거절된 대안 D5**:

- (D5-A) (a) static regex 채택 (Codex spawn prompt 안 file path reference 검출) — false positive 차단 cost 가 정당성 부재 (file path reference 자체가 정합 영역)
- (D5-B) (c) runtime probe 자동화 (Codex finding evidence + Read 결과 verbatim diff layer) — platform inherent 영역 침범 (Codex output schema parsing layer 신설 = 별도 carrier 영역)
- (D5-C) declaration-only retain 영역에서도 evidence-checks-registry entry append (warning tier 0-validation) — registry schema scope 침해 (실행 가능한 mechanical lint 부재 entry append 는 schema 의미 약화)

### D6. mandatory-real-execution-evidence STANDING + Epic-gate verify-don't-dismiss (Amendment 4 / CFP-988)

기존 §결정 D1 scope (Codex external worker output 한정) 의 verify-before-trust pattern 을 **두 추가 영역**으로 ratchet-up direction 확장. D1-D5 본문 의미 변경 없음 — 신규 §결정 D6 으로 적용 대상 enumeration 확장 only.

#### D6.1 — mandatory-real-execution-evidence STANDING (E-1 carrier, pattern_count=4)

**Trust boundary 명시 (TB-1)**: DeveloperPL self-asserted output (stdout / pasted log / claim 텍스트) = 신뢰 외측. CodeReviewPL own discriminating real-execution + Orchestrator working-directory direct read = 신뢰 내측. boundary 검증 책임 = CR + Orchestrator dual-layer (single-layer collapse 금지).

**FIX verification 시 normative requirement** (`[user-input verbatim — Issue #988 §P-1 + EPIC-RESULTS-CFP-858.md §6.1 결정 제안 본문 그대로 codify]`):

> "FIX verification 시 DeveloperPL self-claim 은 ground truth 아님. CodeReviewPL/Orchestrator 가 다음 4-tuple 의 real-execution evidence 를 independently 재현해야 verdict PASS. DeveloperPL pasted stdout 무신뢰. **STANDING normative for ALL FIX verification (per-Story ad-hoc 폐기).**"

4-tuple (a/b/c/d) verbatim:

- **(a)** CR-own discriminating revert (pre-fix FAIL ↔ post-fix PASS) — CodeReviewPL 이 자기 환경에서 fix 전 FAIL + fix 후 PASS 양쪽 재현 의무
- **(b)** reconcile-integration path — single-aggregator / single-unit / pasted-stdout 단축 path 금지, 실 integration path 통과 의무
- **(c)** DeveloperPL pasted stdout 미신뢰 — DevPL "fix 성공" 단언 자체는 verdict 입력 아님, independent reproducer (CR + Orchestrator) ground truth 가 verdict source
- **(d)** single-aggregator/single-unit bypass forbidden — CR-own real-execution evidence 가 integration-path 대신 aggregator/unit 단축 path 만 검증 시 verdict reject (CFP-986 §결정 violation evidence — `_S2_MAX_EXIT` cross-channel propagation conflation 영역)

**위협 ↔ 완화 매핑**:

- **THR-1** (false-self-claim, governance attestation integrity violation) → 4-tuple sub-(a) + sub-(c) 완화
- **THR-3** (single-aggregator/single-unit bypass, defense-in-depth bypass) → 4-tuple sub-(b) + sub-(d) 완화

**Lineage evidence** (`[verified: EPIC-RESULTS-CFP-858.md §5 P-1 4-instance + CFP-900 §10 FIX Ledger row 2 + CFP-986 CR re-audit comment 4477586384]`):

- 4 pre-Amendment instance: CFP-699 / CFP-702 / CFP-899 / CFP-900-iter0/iter1
- BREAK 지점: CFP-900 FIX iter-2 (CodeReviewPL iter-2 mandatory-real-execution-evidence requirement 첫 적용)
- HELD evidence: CFP-986 post-merge fix (CR re-audit "still-broken (NO 5th) — every DevPL claim independently CR-reproduced + confirmed true; iter-2 mandatory-real-exec discipline HELD across this post-merge fix")

#### D6.2 — Epic-gate verify-don't-dismiss STANDING (E-2 sub-clause, super-class single sample)

**Trust boundary 명시 (TB-2)**: Epic IntegrationTestAgent flagged "non-blocking observation" / "minor warning" / "informational" tier 발화 = 신뢰 외측 (silent dismissal 금지 boundary). Orchestrator direct reproduction (Epic close 직전, Epic deliverable domain scope) = 신뢰 내측.

**STANDING discipline normative requirement** (`[user-input verbatim — Issue #988 §P-2 + EPIC-RESULTS-CFP-858.md §6.2 결정 제안 본문 그대로 codify]`):

> "Epic IntegrationTest gate (ADR-055) 가 Epic 자체 deliverable domain 에서 flag 한 'non-blocking observation' 은 Orchestrator 가 rationalize 금지 — ADR-070 verify-before-trust 적용 direct reproduction 의무. Epic close 전 미verify observation = Epic close 차단."

**위협 ↔ 완화 매핑**:

- **THR-2** (Epic-gate observation dismissal → Epic close → consumer downstream defect leak, blast radius CRITICAL) → D6.2 sub-clause 완화

**Catching evidence** (`[verified: CFP-986 fix-event comment 4477435338 verbatim]`):

> "Discovered by Epic IntegrationTest gate + ADR-070 verify-before-trust NOT dismissing a flagged 'non-blocking observation' — codeforge governance working as designed."

**Operational gate impact**: Epic close 결정자 = Orchestrator (Epic owner) — IntegrationTestAgent advisory layer 보존. Pre-Amendment ad-hoc rationalize → Post-Amendment STANDING direct reproduction. operational role boundary 침범 0건 (ADR-055 IntegrationTestAgent 자체 role 변경 0). ADR-082 §결정 1 disjoint 4-layer 표 정합 — IntegrationTestAgent = internal lane agent, 본 §결정 D6.2 = read-time attestation 신뢰성 layer (ADR-082 write-time semantic truth layer 와 disjoint axis), scope 침범 0 verify.

**Failure mode + mitigation**:

- (FM-1) IntegrationTestAgent 자체 false positive — Orchestrator verify-before-trust 1회 추가 cost (Epic close decision 자체는 reproduction 결과 ground truth 기반)
- (FM-2) IntegrationTestAgent false negative — D6.2 catch surface 가 IntegrationTestAgent flag 의존, 후속 carrier 영역 (ADR-055 verdict format 안 explicit observation marker 신설 follow-up)

#### D6.3 — Scope ratchet-up direction + ADR-082 §결정 1 disjoint 4-layer 표 cross-ref

본 §결정 D6 = `verify-before-trust pattern` (ADR-070 §결정 D1 본문) 의 **적용 대상 enumeration** ratchet-up 확장 — pattern 자체 (verify-before-trust 의 sub-scope discipline) 가 invariant 이고, D1 scope (Codex external worker output) → D6.1 (DeveloperPL self-claim) + D6.2 (IntegrationTestAgent flagged observation) 영역 확장. **scope 확장 ratchet-up direction** (ADR-064 §결정 7 정합, 약화 0).

ADR-082 §결정 1 disjoint 4-layer 표 cross-ref:

| layer | scope | D6.1 (DevPL self-claim) | D6.2 (IntegrationTestAgent flagged observation) |
|---|---|---|---|
| ADR-073 | Orchestrator cross-repo state | — | — |
| ADR-070 (D1 + 본 D6 확장) | Codex external worker output → DevPL self-claim + IntegrationTestAgent flagged observation | scope expansion (read-time attestation 신뢰성 layer) | scope expansion (read-time attestation 신뢰성 layer) |
| ADR-082 | internal lane agent self-write semantic truth | DevPL self-write 영역 (§9 evidence write) overlap, disjoint axis (write-time source 사실성) | IntegrationTestAgent self-write (§14 evidence) overlap, disjoint axis |
| ADR-045 §D | cross-Story pattern forcing function | pattern_count=4 origin (E-1 forcing function) | pattern_count=1 super-class origin (E-2 forcing function) |

**scope 침범 0건 verify**: 본 §결정 D6 의 normative content = read-time attestation 신뢰성 (외부 worker output / DevPL self-claim / IntegrationTestAgent observation = 모두 "주장의 신뢰성 검증" axis). ADR-082 write-time semantic truth (source/value/ownership write-time verify axis) 와 disjoint. ADR-073 Orchestrator cross-repo state verify 와 disjoint. ADR-045 §D forcing function (pattern_count threshold trigger) 와 disjoint. 4-layer scope invariant 0건 변경.

#### D6.4 — `mechanical_enforcement_actions: []` retain (Amendment 1/2/3 precedent 4번째 instance)

본 Amendment 4 = ADR-070 §D5 declaration-only retain precedent chain 4번째 instance. `mechanical_enforcement_actions: []` retain. Amendment 1 (CFP-776 cross-ref-only) + Amendment 2 (CFP-844 cross-ref-only) + Amendment 3 (CFP-946-A D1 expansion) 패턴 정합. ADR-040 Amendment 3 §결정 7.D normative ADR 5 category enum (governance / security / tooling-infrastructure / dogfood-out / lifecycle) 안 본 ADR-070 category `workflow-policy` 부재 → mechanical_enforcement_actions[] 의무 면제. 단 declaration 명시 보존 (Amendment 1/2/3 패턴 답습).

**거절된 대안 D6**:

- (D6-A) review-verdict-v4 v4.5 → v4.6 MINOR carrier 신설 (`developerpl_realexec_independently_reproduced: bool` field) — sibling sync 의무 (ADR-010, codeforge-review canonical) + dual-PR cost + doc-only fast-path 이탈. 본 Story = Q1-A 채택 (declaration-only retain), Q1-B = 별 carrier sentinel 조건 (false-self-claim post-Amendment 1+ recurrence 영역, 현재 sentinel 0 sample).
- (D6-B) ADR-045 Amendment 7 (§D-9 sister clause) — E-2 분리 carrier. CFP scope unitary 위배 가능성 (ADR-064 §결정 5) + single Story = 2 ADR Amendment 분산 cost. 본 Story = Q2-A 채택 (E-1 + E-2 super-class 통합).
- (D6-C) ADR-082 Amendment — write-time semantic truth layer 와 disjoint axis (E-2 = read-time observation dismissal discipline, ADR-082 scope mismatch).
- (D6-D) 신규 ADR-084 신설 — E-3 (channel-disjointness contract codification) 의 carrier 영역, 본 E-1/E-2 와 disjoint pattern (후속 CFP-989 carrier).

## 결과

- ADR-052 6 touchpoint 자동 dispatch 영역에 verify-before-trust 채널 normative anchor 신설 — Codex 발화 evidence ground truth 확정 의무
- Codex worker spawn prompt 안 file content verbatim 첨부 의무 (sandbox 영역 외 file 전체) — D2 SSOT
- Codex finding 과 Orchestrator file Read mismatch 시 verdict reject + Story §10 FIX Ledger false positive count tally + Orchestrator override rationale 의무 — D3 SSOT
- ADR-052 Amendment 5 cross-ref (dispatch prompt template 안 verbatim 첨부 의무 본문 명시) — D4 SSOT
- evidence-enforceable framework entry append 면제 (declaration-only retain) — D5 SSOT
- CLAUDE.md "Codex Proactive Check" blockquote 갱신 (verify-before-trust 채널 명시 추가) — Orchestrator 행동 invariant
- playbook §3.10 dispatch prompt template patch (verbatim 첨부 의무 본문 명시) — Amendment 5 본문 cross-ref
- ADR-RESERVATION row append (ADR-070 reserved 등록 — GitOpsAgent self-write 영역, 본 carrier 는 ArchitectAgent inline append)

## Amendments

### Amendment 1 — ADR-082 cross-ref (disjoint 보완 관계, CFP-776)

**문제**: ADR-070 = Codex external worker output verify 의무 (외부 worker output 한정). 그러나 lane agent 가 §9 evidence 작성 / Phase 0 mapping / corpus enumeration 시 write-time semantic truth 를 verify 없이 단언하는 영역 (pattern_count 3 누적, CFP-746/CFP-770) 은 ADR-070 scope 외 — internal lane self-write 미포함.

**결정**: ADR-082 (Write-time self-write verification mandate) 신설로 해당 gap 을 disjoint super-class layer 로 codify. ADR-070 ↔ ADR-082 = **disjoint 보완 관계**:

- **ADR-070** = 외부 worker(Codex) output 한정 (Codex finding evidence ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject)
- **ADR-082** = internal lane agent self-write 한정 (§9 evidence / Phase 0 mapping / corpus enumeration write-time 에 작성 값 자체의 사실성 source direct verify)

두 layer 는 verify 대상 / 행위 주체가 disjoint — scope 침범 0. ADR-082 §결정 1 layer disjoint 4-layer 표 (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) 가 공통 anchor. 추가로 본 ADR-070 §D5 evidence-enforceable framework entry append 면제 (declaration-only retain) = ADR-082 §결정 6 `mechanical_enforcement_actions: []` known-limitation rationale 의 직접 선례. 본 Amendment 는 cross-ref-only — ADR-070 D1-D5 의미 변경 없음.

### Amendment 2 — ADR-081 §결정 D6 cross-ref (disjoint 보완 관계, CFP-844)

**문제**: ADR-070 = Codex finding evidence 의 **factual ground truth** verify 의무 (file content direct Read, mismatch 시 verdict reject) — finding 의 *사실 근거* 가 ground truth 와 일치하는가 검증 layer. 그러나 Codex finding 의 **severity 경중 calibration** (Codex 가 발화한 P0/P1/P2 가 review lane ground truth severity 와 정합하는가) 영역은 ADR-070 scope 외 — finding evidence 가 TRUE positive 이되 severity 만 mis-rate 한 경우 ADR-070 verify 통과 (사실 근거 정합) 후에도 severity inflation 잔존 가능.

**결정**: ADR-081 Amendment 1 (신규 §결정 D6 Codex worker severity calibration rubric) 이 해당 gap 을 disjoint 보완 layer 로 codify. ADR-070 ↔ ADR-081 §결정 D6 = **disjoint 보완 관계**:

- **ADR-070** = Codex finding evidence 의 factual ground truth verify (사실 근거 layer — finding evidence 가 file content direct Read 결과와 일치하는가)
- **ADR-081 §결정 D6** = Codex finding 의 severity 경중 calibration (severity 경중 layer — finding severity 가 DesignReviewPL/CodeReviewPL final verdict ground truth severity 와 정합하는가, bidirectional: over-rate + security-relevant under-rate 양방향)

두 layer 는 verify 대상이 disjoint — ADR-070 = evidence 사실성 / ADR-081 D6 = severity 경중. scope 침범 0. ADR-070 §D5 declaration-only retain (mechanical lint 부재, 본문 normative anchor SSOT) = ADR-081 §D5 / §결정 D6.e known-limitation 직접 선례 (ADR-082 §결정 6 선례 chain 연속 — ADR-070 D5 → ADR-082 §6 → ADR-081 D5/D6.e). 본 Amendment 는 cross-ref-only — ADR-070 D1-D5 의미 변경 없음 (Amendment 1 패턴 정합).

### Amendment 3 (2026-05-18 KST, CFP-946-A)

**문제**: 기존 §결정 D1 default substitution = "Orchestrator inline verify-before-trust" 의 운영적 단일 substitution behavior 만 codify. 실제 운영에서 3 가지 substitution path 가 활용되어 왔으나 (sandbox 영역 외 file 의 sentinel sample 8 retro 분석 결과) normative SSOT 부재. Codex worker spawn 결정 시점 의 substitution scope declare gap.

**결정**: §결정 D1 expansion 본문 (substitution path 3-enum codify, default `inline_orchestrator_verify` / `manual_substitution_declare` / `fallback_skip_with_marker`) 신설. ADR-070 ↔ ADR-052 Amendment 8 = **cross-ref binding**:

- **ADR-070 §결정 D1 expansion** = substitution path 3-enum 의 normative anchor SSOT (semantics + Story §10 marker 의무 + 적용 trigger)
- **ADR-052 Amendment 8** = 6 touchpoint × substitution path 3-enum cross-matrix (각 touchpoint 의 default + manual_substitution_declare trigger + fallback_skip_with_marker trigger)

두 ADR 의 normative anchor 분리 — ADR-070 = pattern SSOT (verify-before-trust 의 sub-scope), ADR-052 = touchpoint behavior SSOT (dispatch prompt template). scope 침범 0. ADR-070 §D5 declaration-only retain (mechanical lint 부재) precedent 정합 — `mechanical_enforcement_actions: []` retain (Amendment 1/2 패턴 정합).

본 Amendment 3 = D1 본문 expansion + D2/D3/D4/D5 결정 본문 + Amendment 1/2 본문 의미 변경 없음. 본 ADR-070 §결정 1 expansion = 운영적 substitution behavior 의 normative codification (기존 single-substitution behavior → 3-enum exhaustive).

### Amendment 4 (2026-05-19 KST, CFP-988)

**참조**: [`mclayer/codeforge-internal-docs:wrapper/stories/CFP-988.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-988.md) — Amendment 4 carrier (ADR-070 신규 §결정 D6 추가)

**상황**: ADR-045 §D-9 forcing function emission from Epic CFP-858 retro (EPIC-RESULTS-CFP-858.md §6.1 E-1 + §6.2 E-2). pattern_count=4 ≥ threshold 2 mandatory adr_draft_emitted. 4 instance lineage (CFP-699 + CFP-702 + CFP-899 + CFP-900-iter0/iter1) DeveloperPL false-self-claim recurrence. ADR-070 §결정 D1 scope (Codex external worker output) 안 verify-before-trust pattern 의 적용 대상 enumeration 확장 ratchet-up direction 필요.

**결정**: §결정 D6 (Amendment 4) 신설 — D6.1 mandatory-real-execution-evidence STANDING normative + D6.2 Epic-gate verify-don't-dismiss sub-clause + D6.3 scope ratchet-up direction + ADR-082 §결정 1 disjoint 4-layer 표 cross-ref + D6.4 `mechanical_enforcement_actions: []` retain (precedent chain 4번째 instance).

본 §결정 D6 ↔ ADR-082 §결정 1 4-layer 표 = **disjoint axis** (D6 = read-time attestation 신뢰성 layer / ADR-082 = write-time semantic truth layer). scope 침범 0건 verify.

본 §결정 D6 ↔ ADR-045 §D-9 = **forcing function origin** (ADR-045 §D-9 = cross-Story pattern_count threshold trigger / 본 D6 = trigger 산물 normative anchor).

본 §결정 D6 ↔ ADR-055 = **catching layer SSOT** (E-2 sub-clause 의 IntegrationTest gate 영역 cross-ref).

본 §결정 D6 ↔ ADR-067 = **per-iteration verify content vs post-failure boundary reassessment** axis disjoint (cycle conflict 0건).

ADR-070 §D5 declaration-only retain precedent chain 4번째 instance — `mechanical_enforcement_actions: []` retain (Amendment 1 ADR-082 cross-ref + Amendment 2 ADR-081 §D6 severity calibration cross-ref + Amendment 3 D1 expansion 3-enum codify 패턴 정합). 본 Amendment 4 = D1-D5 + Amendment 1/2/3 본문 의미 변경 없음 — 신규 §결정 D6 추가 only.

### Amendment 5 (2026-05-19 KST, CFP-1003)

#### Context (Amendment 5)

본 ADR-070 D1 적용 scope L107-L111 본문 (3-row 표) 는 두 채널의 verify-before-trust 적용 영역을 codify:

- L109 `ADR-052 6 touchpoint 자동 dispatch 영역 — full 적용 (본 ADR 결정 SSOT)` — proactive 6 touchpoint scope **full 적용**
- L110 `codex:rescue 사용자 ad-hoc 채널 (ADR-022 Deprecated default 영역) — 사용자 책임 영역 (적용 외)` — reactive 채널 **적용 외** (사용자 책임)
- L111 `CodexReviewAgent (review-verdict-v4 producer, ADR-044 §결정 2 dispatch_mode: user_request_only) — 별도 lane scope (적용 외)` — review lane 영역 분리

CFP-963 Codex TP#4 가 reactive codex:rescue 채널 영역에서 다음 risk surface 식별:

- TH-1 (sandbox bypass misdeclaration) — 사용자 ad-hoc invocation 시점에도 동일한 codex CLI process boundary 안에서 Codex worker spawn → sandbox-restricted network operation (gh api / git fetch cross-repo / 외부 HTTP) 발화 가능성 동일 (codex@openai-codex plugin runtime 영역). proactive 채널 ADR-081 §결정 D1.D 4-tier enum (offline / repo-fetch-only / web-fetch / offline_substitution_declared) declare 의무 가 reactive 영역에 부재 → 사용자 ad-hoc invocation 시 spawn prompt 본문에 network_scope 명시 부재로 substitution path activate trigger 영역 모호.
- TH-2 (PAT exposure) — Codex worker 가 cross-repo state verify task 수행 시 CODEFORGE_CROSS_REPO_PAT (또는 user gh CLI auth context) 가 worker 환경에 노출. proactive 채널 = ADR-066 PAT rotation policy + Story §10 marker grep tally (substitution path enum 2/3 한정) 로 audit trail 확보. reactive 채널 = 사용자 책임 영역 (적용 외) invariant 정합 → audit trail 부재 risk.

본 Amendment 5 = **reactive 채널 영역의 사용자 책임 영역 invariant 보존** + **best-effort 가이드 anchor codify** (codeforge 측 강제 미발효, 사용자 ad-hoc 책임 영역에 대한 normative anchor RETAIN). proactive 채널 영역 (D1 L109 full 적용 invariant) 의미 변경 0건.

CFP-963 Story §6.3 OOS row L374 verbatim `Codex CLI reactive channel (codex:rescue) network_scope lint = OUT (derived default) proactive 6 touchpoint spawn 한정 (ADR-052 proactive/reactive 분리) — reactive 확장 = 별 CFP` deferred scope 의 closure carrier (CFP-1003 carrier Story).

#### 결정 (Amendment 5)

**A1. D1 적용 scope L107-L111 표 본문 강화 (3-row + reactive 영역 anchor)**

기존 D1 적용 scope L107-L111 본문 (3-row 표) 의미 변경 0건. 본 Amendment 5 = L110 reactive `codex:rescue` 채널 row 안 `사용자 책임 영역 (적용 외)` 의 anchor 강화 + best-effort 가이드 codify (codeforge 강제 미발효 + 사용자 ad-hoc 책임 영역 retain):

| Scope | codeforge 적용 (강제) | best-effort 가이드 (사용자 ad-hoc 책임 영역) |
|---|---|---|
| **proactive 6 touchpoint (D1 L109)** | D1 verify-before-trust + D2 verbatim 첨부 + D3 verdict reject + Amendment 3 substitution 3-enum + D6 mandatory-real-execution-evidence + D6.2 verify-don't-dismiss = **full 적용 (codeforge 강제 invariant)** | N/A (codeforge 강제 영역) |
| **reactive `codex:rescue` (D1 L110, ADR-022 Deprecated default + 사용자 ad-hoc invocation)** | **적용 외** (사용자 책임 영역 invariant 보존, codeforge 측 강제 미발효) | **best-effort 가이드 anchor** — 사용자 ad-hoc invocation 시 D1 verify-before-trust pattern + D2 verbatim 첨부 + D3 verdict reject 흐름 + Amendment 3 substitution 3-enum + ADR-081 Amendment 5 boilerplate 4 mandatory field (D1.A-D codify, network_scope: 4-tier enum 포함) 채택 권장. 사용자 자율 선택 영역 (codeforge 강제 0 invariant 보존). |
| **CodexReviewAgent review lane (D1 L111)** | 적용 외 (review lane scope, ADR-044 §결정 2 dispatch_mode: user_request_only) | N/A (review lane 별도 scope) |

본 표 = D1 적용 scope L107-L111 본문 강화 (3-row 표 + reactive 영역 row best-effort 가이드 column 추가). proactive 영역 강제 invariant + reactive 영역 사용자 책임 영역 invariant + review lane 분리 invariant 모두 보존.

**A2. reactive 영역 best-effort 가이드 anchor 본문 (사용자 ad-hoc 영역 normative anchor RETAIN)**

reactive `codex:rescue` 채널 사용자 ad-hoc invocation 시 다음 anchor 권장 (codeforge 강제 미발효, 사용자 자율 선택 영역):

1. **spawn prompt 본문 안 ADR-081 §결정 D1.A-D 4 mandatory field 채택 권장** — D1.A (dogfood-out Story path verbatim 첨부) / D1.B (current lane / phase 표기) / D1.C (sandbox_outside_paths enumerate) / D1.D (`network_scope: <4-tier enum>` 4-tier enum declare). 사용자 자율 선택 — codeforge 강제 0 (proactive 영역 ADR-081 §결정 D1.A-D codeforge 강제 invariant 정합 분리).
2. **D1 verify-before-trust pattern + D2 verbatim 첨부 + D3 verdict reject 흐름 채택 권장** — 사용자 ad-hoc invocation 시점에 Codex finding evidence 의 ground truth 를 own working directory file Read 로 verify 권장. 사용자 자율 선택 — codeforge 강제 0 (proactive 영역 D1/D2/D3 full 적용 invariant 정합 분리).
3. **Amendment 3 substitution path 3-enum 채택 권장** — `inline_orchestrator_verify` default / `manual_substitution_declare` (sandbox 영역 외 file verify task 필요 시) / `fallback_skip_with_marker` (Codex CLI 미가용 / sandbox network-block 확정). 사용자 자율 선택 — codeforge 강제 0 (proactive 영역 Amendment 3 3-enum invariant 정합 분리).
4. **Story §10 marker `[codex-rescue-fallback: <fail-mode>]` (또는 disjoint marker) 채택 권장** — reactive 채널 fail-mode tally audit trail (proactive 채널 `[codex-sandbox-fallback]` 의 disjoint variant, 또는 동일 marker 의 reactive scope value codify — Wave 2 mechanical lint 도입 시 별 CFP carrier 결정 영역). 사용자 자율 선택 — codeforge 강제 0.

본 4-anchor = reactive 영역 best-effort 가이드. 사용자 ad-hoc invocation 시점에 anchor 채택 / 비채택 = 사용자 책임 영역. codeforge 측 강제 미발효 invariant retain (D1 L110 `사용자 책임 영역 (적용 외)` 본문 정합).

**A3. reactive 영역 mechanical lint scope = Wave 2 carrier 분리 (ADR-064 §결정 1 unitary)**

`codex-network-scope-presence` lint (evidence-checks-registry entry, ADR-060 Amendment 14 §결정 28 carrier) 의 mechanical detection scope = proactive 6 touchpoint spawn prompt 한정 (CFP-963 Story §6.3 OOS row L374 derived default 정합) — reactive 영역 mechanical lint 확장 = 별 CFP carrier 분리 (Wave 2). ADR-064 §결정 1 (CFP scope unitary, "경량 → full" 단계 채택 금지) 정합. CFP-963 Phase 2 mechanical lint 패턴 답습 (Phase 1 declarative + Phase 2 mechanical = 별 CFP).

Wave 2 follow-up CFP scope (별 carrier 분리):

- `scripts/lib/check_codex_network_scope.py` 확장 — reactive spawn prompt detection logic
- `tests/scripts/cfp-1003/test_codex_network_scope_reactive.bats` 또는 동등 bats fixture pair (reactive variant)
- evidence-checks-registry entry description scope 확장 — proactive 6 touchpoint + reactive 채널 양면
- Story §10 marker 신규 enum value 또는 disjoint marker (`[codex-rescue-fallback: <fail-mode>]` reactive variant)
- bats fixture pair (reactive spawn prompt with/without network_scope) — discriminating

본 Wave 2 carrier = CFP-1003 retro 발의 시점 (또는 사용자 directive 시점) 별 CFP 분리. 본 Amendment 5 Wave 1 declarative-only scope retain.

**A4. D1-D6 + Amendment 1-4 본문 의미 변경 0건 (cross-ref-only Amendment 패턴 정합)**

본 Amendment 5 = D1 적용 scope L107-L111 표 본문 강화 only (3-row 표 + reactive 영역 row best-effort 가이드 column 추가). D1 본문 의미 변경 0건 (proactive full 적용 invariant + reactive 적용 외 invariant + review lane 분리 invariant 모두 보존). D2/D3/D4/D5/D6 + Amendment 1/2/3/4 본문 의미 변경 0건 — cross-ref-only Amendment 패턴 (Amendment 1/2 ADR-082 + ADR-081 §D6 cross-ref / Amendment 3 D1 expansion / Amendment 4 신규 §D6 패턴 정합).

**A5. ADR-070 §D5 declaration-only retain precedent chain 5번째 instance**

`mechanical_enforcement_actions: []` retain (Amendment 1/2/3/4 패턴 정합). reactive 영역 mechanical lint = Wave 2 carrier 분리 (A3 SSOT) — 본 Amendment 5 = declaration-only normative anchor only. ADR-082 §결정 6 known-limitation rationale (declaration-only retain) precedent chain 5번째 instance.

**A6. ADR-058 §결정 5 ratchet 정합 (강화 방향 명시)**

- `is_transitional: false` 본 ADR 유지 (permanent governance, reactive 영역 사용자 책임 영역 invariant 보존 + best-effort 가이드 anchor 강화 = permanent strengthening)
- `sunset_justification: "N/A — permanent strengthening (D1 적용 scope L107-L111 표 본문 강화, proactive full 적용 invariant + reactive 적용 외 invariant + review lane 분리 invariant 모두 보존, 약화 영역 0. ADR-070 §D5 declaration-only retain precedent chain 5번째 instance — mechanical_enforcement_actions: [] retain. reactive 영역 mechanical lint = Wave 2 carrier 분리 ADR-064 §결정 1 unitary 정합)"`
- 약화 방향 영역 0건 (D1-D6 + Amendment 1-4 본문 의미 변경 0, scope 축소 0)

**A7. ADR-064 §결정 (Trace 1) active amendment + full-scope 정합**

- Amendment 발의 시점 = CFP-963 Codex TP#4 deferred scope closure (active amendment ratchet 강화 방향)
- 적용 영역 = proactive 채널 강제 invariant + reactive 채널 사용자 책임 영역 invariant + review lane 분리 invariant 모두 (full-scope, 단일 채널 한정 아님)
- forbid-list 13 어휘 (ADR-064 §결정 1 + Amendment 2/4/5) 사용 0 건 self-attest

**A8. doc-only fast-path 적용 (ADR-054 §결정 1)**

본 Amendment 5 자체 = ADR-070 본문 patch (Amendment row append + sub-section append) — doc-only fast-path 적격. carrier Story (CFP-1003) = ADR-052 Amendment 9 + ADR-070 Amendment 5 + ADR-081 Amendment 5 + registry entry description patch + playbook §3.10 reactive variant codify = ADR-054 §결정 1 (신규 ADR 도입 아님, 기존 ADR Amendment + src/tests 무변경) doc-only fast-path 단일 PR 적격.

#### 결과 (Amendment 5)

- D1 적용 scope L107-L111 본문 강화 (3-row 표 + reactive 영역 row best-effort 가이드 column) — A1 SSOT
- reactive 영역 4-anchor best-effort 가이드 본문 명시 (사용자 ad-hoc 영역 normative anchor RETAIN, codeforge 강제 0 invariant 보존) — A2 SSOT
- reactive 영역 mechanical lint scope = Wave 2 carrier 분리 (ADR-064 §결정 1 unitary, CFP-963 Phase 2 mechanical 패턴 답습) — A3 SSOT
- D1-D6 + Amendment 1-4 본문 의미 변경 0건 (cross-ref-only Amendment 패턴) — A4 SSOT
- ADR-070 §D5 declaration-only retain precedent chain 5번째 instance — A5 SSOT
- ADR-058 §결정 5 ratchet 정합 (강화 방향, sunset_justification N/A — permanent strengthening) — A6 SSOT
- ADR-064 §결정 active amendment + full-scope 정합 (forbid-list 13 어휘 사용 0 건) — A7 SSOT
- doc-only fast-path 영역 정합 (본 Amendment 5 자체) — A8 SSOT

#### 거절된 대안 (Amendment 5)

- (Amendment 5-A) **reactive 영역 codeforge 강제 적용** (D1 L110 본문 `사용자 책임 영역 (적용 외)` 폐기 + reactive 영역 D1/D2/D3 + Amendment 3 + ADR-081 §결정 D1.A-D codeforge 강제 적용) — ADR-022 Deprecated default (codex:rescue 사용자 ad-hoc invocation = 사용자 책임 영역) invariant 위배. codex:rescue subagent 자체 = codex@openai-codex plugin runtime 영역, codeforge 강제 권한 외. 사용자 책임 영역 retain + best-effort 가이드 anchor 강화 채택 (ADR-064 §결정 7 top-down ratchet 정합 — 약화 방향 = 사용자 책임 영역 폐기, 차단).
- (Amendment 5-B) **reactive 영역 mechanical lint inline 본 Amendment 5** (Wave 1 + Wave 2 단일 CFP 통합) — ADR-064 §결정 1 (CFP scope unitary) 위배. Wave 1 declarative + Wave 2 mechanical 별 CFP 분리 채택 (CFP-963 Phase 1+2 패턴 답습).
- (Amendment 5-C) **reactive 영역 normative anchor 자체 부재 invariant 보존** (D1 L110 `적용 외` 의미 유지, best-effort 가이드 anchor 도입 0) — Codex TP#4 CX-963 deferred scope (CFP-963 Story §6.3 OOS row deferral 명시) closure 책무 부재 → CFP-963 retro deferred scope 영구 미해소 risk. best-effort 가이드 anchor (사용자 자율 선택, codeforge 강제 0) 채택 = ADR-064 ratchet 강화 방향 + 사용자 책임 영역 invariant 보존 양립.
- (Amendment 5-D) **review-verdict-v4 신규 `reactive_codex_invocation_count` contract field 신설** — contract MINOR bump + sibling sync (ADR-008/010) + Phase 2 PR = doc-only fast-path 이탈. ADR-070 §D5 + ADR-081 §D5 + ADR-082 §결정 6 declaration-only retain precedent 위배 → declaration-only retain + Wave 2 mechanical lint (별 CFP carrier) 채택.
- (Amendment 5-E) **ADR-052 본문 inline reactive 영역 normative anchor** (ADR-070 Amendment 5 회피) — ADR-052 본문 정책 SSOT (proactive 채널 한정) 보존 invariant 위배. reactive 영역 substitution scope + sandbox boundary = ADR-070 (verify-before-trust pattern SSOT) 영역, ADR-052 = touchpoint behavior SSOT (dispatch prompt template) 영역 분리. ADR-070 Amendment 5 본문 SSOT 채택 (ADR-052 Amendment 9 = cross-ref-only).

## 해소 기준

N/A — permanent policy (verify-before-trust = Codex worker 사용 영구 invariant, sandbox 영역 변경 없으면 permanent retain). ADR-058 §결정 1-3 정합:

- `is_transitional: false` (permanent governance)
- `## 해소 기준` 본 섹션 = `N/A — permanent policy` (sunset_justification 면제, ADR-058 §결정 5 정합)
- 영역 변경 시 (codex@openai-codex plugin sandbox 모델 변경 또는 codex CLI runtime working directory inject 추가) 본 ADR amendment 검토 영역 (ratchet 강화 방향만 amendment 허용, ADR-064 §결정 7 top-down ratchet 정합)

## 관련 파일

- [`docs/adr/ADR-052-codex-proactive-check-touchpoints.md`](ADR-052-codex-proactive-check-touchpoints.md) — Amendment 5 cross-ref 본문 SSOT
- [`docs/adr/ADR-081-codex-worker-prompt-boilerplate.md`](ADR-081-codex-worker-prompt-boilerplate.md) — §결정 D6 (severity calibration) Amendment 2 disjoint 보완 cross-ref source (사실 근거 layer ↔ severity 경중 layer)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §3.10 dispatch prompt template SSOT
- [`CLAUDE.md`](../../CLAUDE.md) — 오케스트레이션 규칙 § "Codex Proactive Check" blockquote SSOT
- [`docs/evidence-checks-registry.yaml`](../evidence-checks-registry.yaml) — declaration-only retain 정합 (entry append 면제)
- [`docs/adr/ADR-RESERVATION.md`](ADR-RESERVATION.md) — ADR-070 reserved 등록 SSOT
- [`docs/inter-plugin-contracts/fix-event-v1.md`](../inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger schema (D3 영역 false positive count tally 적용 대상)
- [`docs/adr/ADR-082-write-time-self-write-verification-mandate.md`](ADR-082-write-time-self-write-verification-mandate.md) — disjoint super-class (Amendment 1 cross-ref, CFP-776; D5 declaration-only retain = §결정 6 선례)
- [`docs/adr/ADR-045-story-retro-mandatory-trigger.md`](ADR-045-story-retro-mandatory-trigger.md) — §D-9 cross-Story pattern forcing function origin (Amendment 4 forcing function)
- [`docs/adr/ADR-055-integration-test-lane-policy.md`](ADR-055-integration-test-lane-policy.md) — Epic IntegrationTest gate (Amendment 4 D6.2 catching layer SSOT)
- [`docs/adr/ADR-067-fix-ledger-implementability-escalation.md`](ADR-067-fix-ledger-implementability-escalation.md) — Max FIX 3/3 + RESET (Amendment 4 D6 per-iteration verify content 와 axis disjoint)
