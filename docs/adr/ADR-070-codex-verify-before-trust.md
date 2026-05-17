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
related_stories:
  - CFP-578  # carrier
  - CFP-506  # sentinel 1 reproduce
  - CFP-520  # sentinel 2 reproduce (skip option B)
  - CFP-530  # sentinel 3 reproduce (ADR 발의 timing 도달)
  - CFP-776  # Amendment 1 — ADR-082 cross-ref (disjoint 보완)
  - CFP-844  # Amendment 2 — ADR-081 §결정 D6 severity calibration cross-ref (disjoint 보완)
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
