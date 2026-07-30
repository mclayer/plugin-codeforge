---
kind: concept_definition
type: domain-knowledge
slug: subagent-outcome-terminal-state-taxonomy
title: Subagent outcome terminal-state taxonomy — completion-quality ⊥ termination-mechanism 2 직교축 (self-termination ≠ world-completion)
status: Active
updated: 2026-07-28
carrier_story: CFP-2850
related_adrs:
  - ADR-043  # spawn-event-v1 ledger Allow-list — outcome/termination_cause enum field 착지 지점 (CFP-2850 Amendment: 4 field 확장)
  - ADR-163  # measurement — 자매채널 stop-event-v1 3-field 축분리 선례(§결정2) + §14↔spawn-event dedup(§결정13) harmonize 근거
  - ADR-093  # closed-enum walk_result — open_extension:false / SUCCESS-hardcode 금지 규율 상속 (outcome closed-set 근거)
  - ADR-039  # Orchestrator writer monopoly — outcome/termination_cause emit 주체 (machine-observable 우선)
  - ADR-119  # research-before-claims — INCONCLUSIVE 런타임 자동판별 = open problem → honest-degrade / honest-null
related_concepts:
  - context-offloading-to-ephemeral-workers   # spawn-event-v1 측정 substrate 공유 — C6 wasted-token=outcome-conditioned accounting 이 그 delegation-ratio/cost 축과 downstream 연결
  - vacuous-pass                               # C2 INCONCLUSIVE(false/hallucinated completion) = SUCCESS 위장 = vacuous truth 계열(outcome 축의 false-green)
tags:
  - codeforge
  - agent-outcome
  - terminal-state-taxonomy
  - orthogonal-axes
  - completion-quality
  - termination-mechanism
  - closed-enum
  - record-only
  - honest-null
---

## 정의

subagent(1회 spawn)가 종료했을 때 그 **종료 상태(terminal state)** 를, 서로 독립인 **최소 2 직교축** 으로 분류하는 taxonomy.

- 축 1 = **completion-quality** (`outcome`) — "산출물이 쓸 만한 결과였는가"(달성했나).
- 축 2 = **termination-mechanism** (`termination_cause`) — "어떻게 멈췄는가"(정상 / 시간초과 / 무출력 / 에러 / 취소).

이 taxonomy 의 근본 명제는 **"self-termination ≠ world-completion"** — agent 가 스스로 "done" 을 선언한 사실이 실제 세계-완료(작업이 실제로 유효하게 끝났음)를 의미하지 않는다. 두 축은 conflate 되면 안 된다 — 하나의 flat multi-값 enum 으로 뭉치면 **overlap**(TIMEOUT ∧ INCONCLUSIVE 동시 성립 가능)과 **gap**(ERROR / CANCELLED / PARTIAL / CREDIT 누락)이 동시에 발생하기 때문이다.

## 컨텍스트

codeforge 는 Orchestrator 가 매 작업을 ephemeral subagent 로 spawn 한다(ADR-039). 그 spawn 의 낭비(wasted-token)·역할·모델별 실패율을 집계하려면 먼저 "이 spawn 이 어떤 결과로 끝났는가" 를 구조화 분류해야 한다. 그러나 measurement channel `spawn-event-v1` 의 기존 19-field 에는 outcome 을 담는 field 가 전무했다(분류 substrate 부재).

CFP-2850(N9)이 이 taxonomy 의 **first codified case** 다 — spawn-event-v1 에 `outcome`·`termination_cause` 2 optional field 를 additive 도입(19→23-field)하고, 그 값을 record-only 로 append 한다. `docs/domain-knowledge/concept/` 개념 corpus 에 agent-outcome / terminal-state 정립 파일이 없어(close-loop read 부재) 본 concept 을 신설, 미래 Story 의 재사용 앵커로 삼는다.

**사내 선례 — stop-event-v1 3-field 축분리**: 자매 Tier-3 channel `stop-event-v1` 이 이미 동일 원리로 3축을 분리 소유한다 — `outcome{success, failure, partial}` + `reason_class{...4}` + `recovery_action{retry, escalate, abort}`(ADR-163 §결정2). N9 이 5-값 단일 enum 을 신설하면 사내 **3번째 divergent outcome vocabulary** 가 되므로, 이 선례와 harmonize(REUSE)하는 것이 설계 제약이다. 학계·산업의 termination taxonomy(정상 / budget / abnormal 단일 mechanism 축 MECE + hallucinated-completion·execution-timeout·partial-completion 산업 failure-mode 목록)가 개념 참조군이다.

## 핵심 규칙

taxonomy 를 구성하는 6 명제(C1-C6, Story §6.1 SSOT):

- **C1 — 2 직교축 분리 (completion-quality ⊥ termination-mechanism)**: outcome(달성 품질)과 termination_cause(종료 기전)는 독립 축이다. 단일 flat enum 으로 conflate 금지. 근본 명제 = "self-termination ≠ world-completion".
- **C2 — INCONCLUSIVE = false / hallucinated completion**: 성공을 선언했으나 산출이 무효인 상태. SUCCESS 와의 구분이 가장 미묘하며 산업 failure-mode 목록에도 독립 등재된다. `outcome=inconclusive` 로 표현. 런타임 자동 판별은 학계 미해결 open problem(self-termination ≠ completion) → Orchestrator verify-후 or coarse-defer, envelope.verdict 단독 SUCCESS 신뢰 금지(machine-observable 우선). 초기 저발화 기대(대부분 machine-observable 로 흡수) = 결함 아님(honest degrade, ADR-119).
- **C3 — TIMEOUT ⊂ budget-exhaustion (CREDIT = sub-case)**: 시간·context·turn·credit 을 budget exhaustion 단일 상위군으로 묶는다. `termination_cause=timeout` 이 이 상위군을 통합 표현하며, CREDIT-EXHAUSTED 는 독립 top-level 이 아니라 timeout 의 sub-case 다(별개 top-level enum 값 신설 안 함).
- **C4 — ZERO-OUTPUT = silent failure**: 유효 산출 없이 종료(`tool_uses=0`). `termination_cause=zero_output` 로 표현. competence-기반인지 resource-기반인지 판별 불가하므로 token=null / unattributed 로 정직 기록(silent-success 위장 금지).
- **C5 — RESPAWN = recovery-action 축 (outcome 아님, 미저장)**: respawn(형제 재시도)은 종결상태가 아니라 후속 recovery-action 이다. outcome / termination_cause 축에 저장하지 않는다 — stop-event-v1 이 이미 `recovery_action{retry, escalate, abort}` 를 소유하므로 **REUSE by reference**(3번째 divergent vocab 금지), respawn 관계는 `parent_event_id` chain(기존 field)이 표현한다.
- **C6 — wasted-token = outcome-conditioned accounting**: 낭비 토큰은 outcome 을 **먼저** 분류해야 집계 가능하다. ∴ N9 의 두 반절(분류 → 낭비집계)은 **인과 순서**(load-bearing 명제) — 분류가 선행하고 낭비 인과가 후행한다. 실패 run 의 비용 배수(예: 1.27x 비용 / 2.77x 사이클 / 1.76x retry, retry token bill 1.7~2.5x 증폭)는 *[hypothesis — 단일 출처, 본 taxonomy 미검증 정량치]* 로 남긴다(over-claim 금지).

**축분리 명세 (closed-enum — N9 실체)**:

- `outcome{success, inconclusive, failure, partial}` — completion-quality 축. stop-event-v1 outcome 3값 REUSE + `inconclusive`(C2) additive.
- `termination_cause{normal, timeout, zero_output, error, cancelled}` — termination-mechanism 축.
- 두 enum 모두 **closed-set**(open_extension:false, SUCCESS-hardcode 금지 — ADR-093 상속).
- **record-only (INV-5)**: outcome / termination_cause 는 gate / block / deny 를 세우지 않는다. 분류 기록만.
- **free-form 0 (T-INFO-8)**: 두 축 모두 enum-only. stop-event 의 free-form `reason_class_subclass` 류 복사 금지(enum-only harmonize).
- **honest-null**: 실측 미확보 field 는 null(추정 저장 금지 — ADR-119).

## 경계

- **In scope**: subagent 1회 spawn 의 terminal-state 를 2 직교축(completion-quality + termination-mechanism)으로 분류하는 taxonomy 와 그 축분리 규율. spawn-event-v1 `outcome` / `termination_cause` field 의 의미론.
- **Out of scope**:
  - **recovery-action 축(RESPAWN)** — outcome 아님. stop-event-v1 `recovery_action` 소유(disjoint 축, C5) → 본 taxonomy 미저장.
  - **Orchestrator-stop reason** — stop-event-v1 `reason_class`(Orchestrator 가 왜 멈췄나)는 subagent-termination 과 disjoint subject. termination_cause(subagent 가 어떻게 멈췄나)와 혼동 금지.
  - **token / cost 실측 값 자체** — 측정 substrate(spawn-event-v1 total_tokens / 4-way / cost)는 개별 축. 본 taxonomy 는 그 측정을 **조건짓는 분류축**(C6 outcome-conditioned)일 뿐, 측정 mechanism 이 아니다.
  - **enum emit 주체·판별 로직** — 누가 outcome 을 emit·판별하나(Orchestrator machine-observable)는 writer 배선(ADR-039) 영역으로, taxonomy 정의와 disjoint.
- **Anti-pattern**:
  - 단일 flat 5-값 enum 신설(2 직교축 conflate — overlap TIMEOUT ∧ INCONCLUSIVE, gap ERROR / CANCELLED / PARTIAL / CREDIT).
  - CREDIT-EXHAUSTED 를 독립 top-level enum 값으로 승격(timeout sub-case 를 과분류).
  - envelope.verdict 단독 SUCCESS 신뢰(INCONCLUSIVE 위장 미탐 — C2).
  - outcome 을 gate / block / deny 로 승격(record-only 위반 — INV-5).
  - free-form reason 텍스트 저장(enum-only 위반 — T-INFO-8).
  - 3번째 divergent outcome vocabulary 신설(stop-event-v1 REUSE 회피).

## 관련 ADR

- **ADR-043** spawn-event-v1 ledger Allow-list — `outcome` / `termination_cause`(+ total_tokens / model) 4 field 가 착지하는 Allow-list. CFP-2850 Amendment 으로 4 field 확장(전부 numeric / enum, Deny-list no-op inherit).
- **ADR-163** measurement — 자매채널 stop-event-v1 3-field 축분리 선례(§결정2) + §14↔spawn-event dedup 의무(§결정13). N9 outcome vocab harmonize 의 SSOT.
- **ADR-093** closed-enum walk_result — `open_extension:false` + SUCCESS-hardcode 금지 규율. outcome / termination_cause closed-set 근거.
- **ADR-039** Orchestrator writer monopoly — outcome / termination_cause 를 emit 하는 유일 주체(machine-observable 우선, envelope.verdict 단독 아님).
- **ADR-119** research-before-claims — INCONCLUSIVE 런타임 자동판별 = open problem → honest-degrade(저발화 기대) / 실측 미확보 = honest-null(추정 저장 금지).
- **CFP-2850**(carrier_story) — spawn-event 실측 append 활성화(P0-2) + agent outcome 분류(N9). 본 taxonomy 의 first codified case.

## 변경 이력

- 2026-07-28 KST — 초기 작성(CFP-2850 Phase 2 구현 lane). C1-C6 학계·산업 termination taxonomy + 사내 stop-event-v1 3-field 선례를 codify. N9 = first codified case(close-loop read 부재 해소). SSOT = Change Plan CFP-2850 §3.2 / §3.8 + Story §6.1.
