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
related_stories:
  - CFP-354
  - CFP-411
  - CFP-446
  - CFP-510
  - CFP-532
  - CFP-578
related_adrs:
  - ADR-039
  - ADR-034
  - ADR-044
  - ADR-059
  - ADR-064
  - ADR-070
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
touchpoint: <1|2|3|4|5|6>
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
