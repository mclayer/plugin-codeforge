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
related_stories:
  - CFP-354
  - CFP-411
  - CFP-446
related_adrs:
  - ADR-039
  - ADR-034
  - ADR-044
  - ADR-059
  - ADR-064
related_files:
  - docs/orchestrator-playbook.md
  - docs/superpowers-integration.md
  - CLAUDE.md
is_transitional: false
---

# ADR-052: Codex Proactive Check — 6 Touchpoints

## 상태

**Proposed (2026-05-09)** — CFP-354 carrier story.

## 컨텍스트

Orchestrator(Claude)가 설계 레인 등에서 "꼬임" 현상이 발생한다:
- 6 deputy 산출물 통합 시 모순·순환 논리·누락이 생겨도 스스로 포착 불가
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
touchpoint: <1|2|3|4|5|6>
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

기존 D3 ProactiveCheckPacket v1 스키마 유지. iterative dispatch 의 round 별 input/output 은 동일 schema 의 다중 dispatch 로 표현 — schema 신규 field 불필요. round 추적은 Orchestrator turn 내 inline counter (transient, persistence 불필요 — A5 의 transcript 영속화 부재 정합).

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
- (Amendment-F) Round 별 transcript Story §9 inline append (debate-protocol-v1 align) — proactive check 영역은 verdict 산출 channel 아님 (사용자 dialog 의 pre-formatting 만). FIX 흐름 reasoning carryover 도 부재 (FIX ledger row append 없음). 영속화 채널 부재 정당. A5 비교 표 참조.
- (Amendment-G) Touchpoint #1 외 5 touchpoint 동시 iterative 격상 — 다른 5 touchpoint 는 verdict producer 또는 root cause 판정 영역, 단순 question refinement 와 영역 분리. 별도 carrier 검토 필요 (현재 CFP 미할당).

