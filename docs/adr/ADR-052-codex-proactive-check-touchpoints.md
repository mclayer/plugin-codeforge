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
related_stories:
  - CFP-354
  - CFP-411
related_adrs:
  - ADR-039
  - ADR-034
  - ADR-044
  - ADR-059
related_files:
  - docs/orchestrator-playbook.md
  - docs/superpowers-integration.md
  - CLAUDE.md
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

