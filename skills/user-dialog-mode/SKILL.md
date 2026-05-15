---
name: user-dialog-mode
description: Orchestrator 가 사용자에게 메시지 발화 turn (ADR-039 inline whitelist 1번 entry) 시 호출. frame mode 진입 4 step + 4 layer 검증 + sub-mechanism 2 종을 lookup. ADR-071 carrier.
tools: Read
---

# Orchestrator-user dialog mode (frame + 4 layer + sub-mechanism)

> 참조 lookup-table skill — 매 user-facing turn 직전 호출. mechanism 만 적용하고 본질 anchor 를 놓치면 가설 E (mechanical 규칙 자체 한계) trap. 정책 SSOT: [ADR-071](../../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md) + [playbook §3.14](../../docs/orchestrator-playbook.md).

## 본질 anchor

**Orchestrator 가 사용자와 대화할 때, mechanical rule 추종이 아니라 진짜 수렴 대화에 참여하도록 codeforge SSOT 를 영구적으로 바꾸는 변화.**

본 본질이 충족되지 않으면 아래 mechanism 을 몇 개 쌓든 의미 없다. 모든 mechanism 은 본질을 보조하는 scaffolding.

## 호출 시점

매 user-facing turn 직전 (= [ADR-039](../../docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 1번 entry = 사용자 dialog turn). lane spawn 직전 / subagent 결과 수령 후 / `AskUserQuestion` 발화 직전 / 일반 dialog turn 모두 적용.

## frame mode 진입 4 step (ADR-071 §결정 1)

| step | 행위 |
|---|---|
| 1 | **codeforge 내부 어휘 "내부 메모" 분류 격리** — ADR-NNN / CFP-NNN / lane plugin name / hook name / inter-plugin contract name 을 내부 메모 영역으로 분류. 사용자 발화 본문 직접 등장 금지 (식별자 인용 시 사전 요약 의무) |
| 2 | **사용자 지금까지 무엇 알고 있는지 정리** — 사용자 mental model 추정. 이전 turn 발화 기준 + 미공개 컨텍스트 분리 |
| 3 | **사용자 이 turn 무엇 답·결정해야 하는지 한 문장** — turn 의 사용자 action item 1 문장. 한 문장으로 명확하지 않으면 step 미완 |
| 4 | **위 셋 바탕으로 메시지 작성** — step 1+2+3 통합 위에 본문 |

## frame mode 안 세부 룰 3 종 (ADR-071 §결정 2)

### (a) 후보 1 — 메시지 보내기 직전 self-check 3 문항

1. 사용자가 답해야 할 것이 한 문장으로 명확한가
2. 비-codeforge 맥락 사람이 이해 가능한가
3. 답하는 데 필요한 배경 (왜 / trade-off / 걸려있는 것) 충분한가

3 문항 모두 PASS 후 메시지 발화. 길이 제약 없음.

### (b) 후보 2 — 사실/가치 분리

| 판단 | 처리 |
|---|---|
| 사실 판단 | derived default 적용 (컨텍스트로 추론 가능 시) — declare default + 결과 보고 + 사용자 정정 의무 |
| 가치 판단 | `AskUserQuestion` 발화 의무 |
| 모호 | 가치 측 분류 (safe direction) → `AskUserQuestion` |

`feedback_question_quality` memory entry normative 승격 carrier.

### (c) 후보 3 — sub-agent 결과 평이 번역

- raw packet 그대로 노출 금지
- codeforge 내부 용어 평이한 한글 번역
- **3 줄 제약 명시적 거부** — 길이 자유
- "왜 / trade-off / 걸려있는 것" 배경 포함
- 원본 packet 은 사용자 요청 시 별도

## 4 layer 검증 (ADR-071 §결정 3)

| Layer | 동작 | 발화 위치 |
|---|---|---|
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 | 매 turn 맨 윗줄 (trivial turn 면제) |
| **Layer 2 — 자기 declare** (Amendment 1, §결정 12 — 표 형식 3 항목 strict subschema fix) | 메시지 맨 윗줄 (Layer 1 preamble 와 동일 위치 또는 직후) "표 형식 3 항목" declare | 매 turn 맨 윗줄 (trivial turn 면제 보존) |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 "추상" 한글 token (stem match) 등장 시 immediate halt + 재작성 | 사용자 token detection 시점 |
| **Layer 4 — 누적 detection** | N=1 (같은 양상 다음 turn 재발 시) immediate halt + M=5 max threshold `AskUserQuestion` escalation | `docs/orchestrator-communication-incidents.md` cross-Story 영속 |

**Hanja form ("抽象") 면제** (CLAUDE.md 한자 금지 정책 정합). **영문 alias ("abstract") = trigger 아님** (한글 token 만 anchor).

### Layer 2 strict subschema (Amendment 1, ADR-071 §결정 12 — CFP-695)

Layer 2 self declare 본문 형식 = **표 형식 3 항목 closed enum** (자유 산문 금지). self-attestation paradox 회피 + boilerplate decay 완화 + mechanical lint 가능 + 본 carrier 자기적용 evidence forcing function.

| 항목 | 의미 | 값 enum |
|---|---|---|
| 사용자가 답해야 할 것 | 한 문장 | free-text 1 sentence (없으면 "없음 — 진행 보고") |
| 묻기 직전 derived default 시도 여부 | 했음 / 안 했음 / 가치 판단 영역이라 묻기 의무 | `done` / `skipped` / `value-judgment` |
| 가치 판단 vs 사실 판단 | value / fact / mixed | enum |

**Sub-mechanism 1 ("이전과 다르게 한 점") 와 별 줄 정합**: 표 schema = Layer 2 self declare 본문 자체, sub-mechanism 1 의 "이전과 다르게 한 점:" 줄 = 표 와 별 줄 (메시지 맨 아랫줄). Layer 4 N=1 halt 후 재작성 turn 시 표 + sub-mechanism 1 줄 모두 의무.

**Phase 2 mechanical lint** (§결정 13, advisory only — turn-final hook 부재 한계 인정): PR title/body 안 표 schema 정규식 lint. `hotfix-bypass:dialog-declare-schema` label.

### Turn-shape edge 분기 (E9 / E10 / E11 / E12, playbook §3.14 "Turn-shape derived defaults" SSOT)

| Edge | Layer 1 (preamble) | Layer 2 (declare) | Layer 3 / Layer 4 |
|---|---|---|---|
| **E9 streaming token** | final flush 시 적용 | final flush 시 적용 | active |
| **E10 tool-call-only** (prose 0 줄 + cosmetic 1-줄 미만) | 면제 | 면제 | Layer 3 active / Layer 4 incident 분류 외 |
| **E11 AskUserQuestion popup** | "AskUserQuestion 으로 답해주실 것:" 1 문장 | 면제 (popup 본문이 declare 충당) | active |
| **E12 trivial answer** (응답 ≤ 1 줄 + 의문 부재 + 결정 부재 AND) | 면제 | 면제 | active |

상세 derived default = [playbook §3.14](../../docs/orchestrator-playbook.md) "Turn-shape derived defaults" 표 SSOT.

## Sub-mechanism 2 종 (ADR-071 §결정 4)

### Sub-mechanism 1 — "이전과 다르게 한 점" 1 줄 의무

매 halt 후 (Layer 3 / Layer 4 N=1) 재작성 메시지 맨 아랫줄 (Layer 2 declare 와 별 줄) 에 `이전과 다르게 한 점:` prefix + 1 줄. 단순 표현 다듬기 (어휘 변경 / 문장 길이 압축) 가 아닌 **차원 전환** 의무.

### Sub-mechanism 2 — 다른 차원 전환 (4 차원 enum)

같은 양상 재발 시 (Layer 4 file row count ≥ 2) 단순 표현 다듬기 금지. 다음 차원 중 다른 차원 강제 전환:

| 차원 | 의미 | 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 / derived default / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 |
| **보고 형식** | sub-agent 결과 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 |
| **질문 자체** | 어떤 결정을 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

`feedback_explain_before_ask` memory entry normative 승격 carrier.

## Layer 4 영속 file (ADR-071 §결정 6)

- path: `docs/orchestrator-communication-incidents.md` (wrapper repo)
- owner: Orchestrator 단독 monopoly
- append-only / cross-Story 영속 / M=5 lifetime counter
- pattern_dimension column = 4 차원 enum 만
- 사용자 escalation 후 차원 강제 전환

## 사실/가치 분류 결정 트리 (ADR-071 §결정 5)

```
결정 후보 발화 직전:
  is_factual?
    YES → derived default 적용 → declare + 결과 보고 + 사용자 정정 의무
    NO (가치 판단) → AskUserQuestion 발화 의무
    AMBIGUOUS → 가치 측 분류 (safe direction) → AskUserQuestion
```

**사실 예시**: 파일 존재 / `wc -l` 결과 / `git log` 출력 / SHA / `grep` 결과
**가치 예시**: 사용자 선호 / 정책 강화 방향 / scope 결정 / brainstorm 채택안
**모호 예시**: derived default 추론 가능 + future 작업 영향 큼 → 가치 측

## 3 memory entry normative 승격 mapping (ADR-071 §결정 8)

| memory entry | 정책 위치 SSOT |
|---|---|
| `feedback_explain_before_ask` | playbook §3.14 frame 본문 + ADR-071 §결정 1 step 4 + §결정 4 sub-mechanism 1 |
| `feedback_question_quality` | playbook §3.14 frame 본문 + ADR-071 §결정 2 (b) + §결정 5 결정 트리 |
| `feedback_subagent_driven_auto_select` | **변경 없음** — playbook §3.0.5 기존 정책 유지 (codeforge wrapper side SSOT 변경 0) |

## CFP-582 conceptual cross-ref (ADR-071 §결정 9)

[ADR-059](../../docs/adr/ADR-059-debate-protocol-v1.md) Amendment 2 (CFP-582) = agent ↔ agent debate domain. 본 skill / ADR-071 = Orchestrator ↔ user dialog domain. CFP-582 의 3 marker pattern (`counterargument_present` / `alternative_proposed` / `debate_purpose_statement_present`) = debate transcript verification schema — **turn-by-turn user dialog 에 직접 mapping 부적합**. Conceptual cross-ref only — schema 재사용 절대 금지.

## scope 외 (ADR-071 §결정 10)

- Layer 1 preamble mechanical lint — 별 follow-up CFP
- agent ↔ agent debate (CFP-582 cover)
- 코드 품질 / 보안 / 성능
- 사용자 personal memory entry 자체 삭제 (사용자 영역)
- consumer overlay 영역 customization (overlay 가 정책 축소 불허)
- debate-protocol-v1 3 marker import (schema 직접 채택 절대 금지)
