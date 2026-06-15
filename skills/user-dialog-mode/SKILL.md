---
name: user-dialog-mode
description: Orchestrator 가 사용자에게 메시지 발화 turn (ADR-039 inline whitelist 1번 entry) 시 호출. frame mode 진입 4 step + 4 layer 검증 + sub-mechanism 2 종을 lookup. ADR-071 carrier.
tools: Read
---

# Orchestrator-user dialog mode (frame + 4 layer + sub-mechanism)

> 참조 lookup-table skill — 매 user-facing turn 직전 호출. 정책 SSOT: [ADR-071](../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) + [playbook §3.14](../../docs/orchestrator-playbook.md). 본질 = mechanical rule 추종이 아닌 진짜 수렴 대화 — mechanism 은 본질 보조 scaffolding (가설 E trap 주의).

## 호출 시점

매 user-facing turn 직전 (= ADR-039 inline whitelist 1번 entry). lane spawn 직전 / subagent 결과 수령 후 / `AskUserQuestion` 직전 / 일반 dialog turn 모두 적용.

## frame mode 진입 4 step (ADR-071 §결정 1)

| step | 행위 |
|---|---|
| 1 | **codeforge 내부 어휘 "내부 메모" 분류 격리** — ADR-NNN / CFP-NNN / lane plugin name / hook name / inter-plugin contract name 을 내부 메모 영역으로 분류. 사용자 발화 본문 직접 등장 금지 (식별자 인용 시 사전 요약 의무) |
| 2 | **사용자 지금까지 무엇 알고 있는지 정리** — 사용자 mental model 추정. 이전 turn 발화 기준 + 미공개 컨텍스트 분리 |
| 3 | **사용자 이 turn 무엇 답·결정해야 하는지 한 문장** — turn 의 사용자 action item 1 문장. 한 문장으로 명확하지 않으면 step 미완 |
| 4 | **위 셋 바탕으로 메시지 작성** — step 1+2+3 통합 위에 본문. **mid-turn glossary lookup 의무** (ADR-071 §결정 19, Amendment 8 — CFP-1764): agent burst output paste 합성 시 codename 발견 시 [`docs/wording-dictionary.md`](../../docs/wording-dictionary.md) 카테고리 (c) lookup → 평이 어휘 1:1 치환 또는 평문 풀이 동반. closed 15 codename 첫 batch + ratchet extensibility (신규 어휘 = 별 후속 CFP) |

## frame mode 안 세부 룰 3 종 (ADR-071 §결정 2)

### (a) 메시지 직전 self-check 3 문항

1. 사용자가 답해야 할 것이 한 문장으로 명확한가
2. 비-codeforge 맥락 사람이 이해 가능한가
3. 답하는 데 필요한 배경 (왜 / trade-off / 걸려있는 것) 충분한가

3 문항 모두 PASS 후 발화. 길이 제약 없음.

### (b) 사실/가치 분리 + 분류 결정 트리 (ADR-071 §결정 5)

| 판단 | 처리 |
|---|---|
| 사실 판단 | derived default 적용 (컨텍스트로 추론 가능 시) — declare default + 결과 보고 + 사용자 정정 의무 |
| 가치 판단 | `AskUserQuestion` 발화 의무 |
| 모호 | 가치 측 분류 (safe direction) → `AskUserQuestion` |

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

### (c) sub-agent 결과 평이 번역

- raw packet 그대로 노출 금지
- codeforge 내부 용어 평이한 한글 번역
- **3 줄 제약 명시적 거부** — 길이 자유
- "왜 / trade-off / 걸려있는 것" 배경 포함
- 원본 packet 은 사용자 요청 시 별도

## 4 layer 검증 (ADR-071 §결정 3)

| Layer | 동작 | 발화 위치 |
|---|---|---|
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 | 매 turn 맨 윗줄 (trivial turn 면제) |
| **Layer 2 — 자기 declare** | turn 끝 "주의한 가설" 1 줄 (보조 신호) | 매 turn 맨 아랫줄 (trivial turn 면제) |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 "추상" 한글 token (stem match) 등장 시 immediate halt + 재작성 | 사용자 token detection 시점 |
| **Layer 4 — 누적 detection** | N=1 (같은 양상 다음 turn 재발 시) immediate halt + M=5 max threshold `AskUserQuestion` escalation | `docs/orchestrator-communication-incidents.md` cross-Story 영속 |

**Hanja form ("抽象") 면제** (CLAUDE.md 한자 금지 정책 정합). **영문 alias ("abstract") = trigger 아님** (한글 token 만 anchor).

### Turn-shape edge 분기 (E9 / E10 / E11 / E12, playbook §3.14 "Turn-shape derived defaults" SSOT)

| Edge | Layer 1 (preamble) | Layer 2 (declare) | Layer 3 / Layer 4 |
|---|---|---|---|
| **E9 streaming token** | final flush 시 적용 | final flush 시 적용 | active |
| **E10 tool-call-only** (prose 0 줄 + cosmetic 1-줄 미만) | 면제 | 면제 | Layer 3 active / Layer 4 incident 분류 외 |
| **E11 AskUserQuestion popup** | "AskUserQuestion 으로 답해주실 것:" 1 문장 | 면제 (popup 본문이 declare 충당) | active |
| **E12 trivial answer** (응답 ≤ 1 줄 + 의문 부재 + 결정 부재 AND) | 면제 | 면제 | active |

## Sub-mechanism 2 종 (ADR-071 §결정 4)

### 1 — "이전과 다르게 한 점" 1 줄 의무

매 halt 후 (Layer 3 / Layer 4 N=1) 재작성 메시지 맨 아랫줄 (Layer 2 declare 와 별 줄) 에 `이전과 다르게 한 점:` prefix + 1 줄. 단순 표현 다듬기가 아닌 **차원 전환** 의무.

### 2 — 다른 차원 전환 (4 차원 enum)

같은 양상 재발 시 (Layer 4 file row count ≥ 2) 단순 표현 다듬기 금지 — 다른 차원 강제 전환:

| 차원 | 의미 | 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 / derived default / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 |
| **보고 형식** | sub-agent 결과 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 |
| **질문 자체** | 어떤 결정을 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

## Layer 4 영속 file (ADR-071 §결정 6)

- path: `docs/orchestrator-communication-incidents.md` (wrapper repo)
- owner: Orchestrator 단독 monopoly
- append-only / cross-Story 영속 / M=5 lifetime counter
- pattern_dimension column = 4 차원 enum 만
- 사용자 escalation 후 차원 강제 전환

## 압축 pointer (상세 = normative SSOT)

- 3 memory entry normative 승격 mapping = ADR-071 §결정 8 (feedback_explain_before_ask / feedback_question_quality / feedback_subagent_driven_auto_select — 위치 표는 ADR SSOT).
- CFP-582 cross-ref (ADR-071 §결정 9): agent↔agent debate domain (ADR-059 Amendment 2) — conceptual cross-ref only, 3 marker **schema 재사용 절대 금지**.
- scope 외 (ADR-071 §결정 10): Layer 1 mechanical lint (별도 CFP) / agent↔agent debate / 코드 품질·보안·성능 / 사용자 memory entry 삭제 / consumer overlay customization (**overlay 는 정책 축소 불허**) / debate marker import (schema 직접 채택 절대 금지).

## DialogFidelityAgent spawn anchor — sunset (ADR-071 Amendment 9 / CFP-2236, 2026-06-14)

> **[SUNSETTED]** 구 DialogFidelityAgent 3-anchor spawn anchor (`post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause`) 는 전면 폐지 (ADR-071 Amendment 9, carrier-preserved). dialog turn 검증 ground 보존 = 동일 anchor 의 **Codex TP#2 / TP#3** (mandatory P0/P1 inline FIX) + **ADR-064 §결정 9 Q-3check** (Orchestrator self-check). 폐지 근거 = 죽은 spawn 의무 + 검증 ground 중복 + Opus verifier 비용 대비 효과 0. **보존 invariant 무손상**: 위 frame mode 4 step / 4 layer 검증 / sub-mechanism 2 종 / 아래 3 touchpoint / mid-turn glossary / 5번째 cognitive layer 신설 금지 invariant 모두 무변경 (ADR-071 본체 폐지 아님 — verifier auxiliary 만 절제).

## Conversational reporting frequency suppression (ADR-071 §결정 15 / CFP-851)

> normative SSOT = [playbook §3.14 frequency suppression](../../docs/orchestrator-playbook.md) + [ADR-071 §결정 15](../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md). 본 sub-section = **lookup mirror only**.

**frequency vs richness 분리 invariant**: 좁히는 것은 말 거는 횟수·시점 (frequency / timing) 만 — **말할 때의 풍부함은 §결정 2(c) (3 줄 제약 거부 · 길이 자유 · 배경 포함) 그대로 보존** (ADR-058 §결정 5 약화 차단 근거).

### 3 touchpoint closed enumeration

| touchpoint | 발화 사유 | scope |
|---|---|---|
| **(a) 결과-명세 확인** | 사용자 선언 결과 자체 모호 + 잘못 추측 시 rollback 비싼 경우 (verifiable outcome surface 안전판) | `AskUserQuestion` 발화 (§결정 5 결정 트리 — 모호 → 가치 측 분류) |
| **(b) 사용자만 풀 수 있는 차단** | 인증·권한 등 codeforge 자체 해소 불가 | ADR-039 inline whitelist 1번 entry (사용자 dialog) scope 안 |
| **(c) 최종 완료 보고 1회** | 요청한 작업 단위 전체 완료 | ADR-039 inline whitelist 4번 entry (Status report) scope 안 |

그 외 진행·중간 결정·근거·중간 결과 = 산출물 channel (대화 turn 아님): Story file / change-plan / ADR / PR description / Issue comment / TodoWrite panel.

**무약화 invariant** — 3 touchpoint 발화 turn 에도 모두 그대로 적용: Layer 1 preamble + Layer 2 declare (turn-shape edge 무변경) / §결정 2(c) richness. (DialogFidelityAgent 3-anchor spawn + §결정 14 incident append-rate measurement = CFP-2236 sunset — ADR-071 Amendment 9.)

4번째 touchpoint 신설 = **별도 CFP 의무** (ADR-064 §결정 7 ratchet + ADR-058 §결정 5 sunset_justification + Story §1 사용자 explicit 승인). mechanical lint = 별도 follow-up CFP (§결정 15 = behavioral directive only).

> **완료보고 정직성 + 제안 필요성 게이트 (ADR-119 §결정 9 cross-ref)**: touchpoint (c) 최종 완료 보고 = 작업 상태("완료"/"잔여") 실측(Read/Grep) 후에만 단언, 추측성 backlog 패딩 금지. 보고 중 follow-up 제안 발의 = 필요성 3문 게이트 선통과 의무 (발견 ≠ 필요).

## Mid-turn glossary lookup (ADR-071 §결정 19 / CFP-1764)

> normative SSOT = [ADR-071 §결정 19](../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) + [`docs/wording-dictionary.md`](../../docs/wording-dictionary.md) 카테고리 (c). 본 sub-section = **lookup mirror only**.

frame mode step 3 과 step 4 사이 forcing function — agent burst output paste 합성 시 codename 발견 시 평이 어휘 1:1 치환 또는 평문 풀이 동반 의무. lookup SSOT = `docs/wording-dictionary.md` 카테고리 (c) 단일 (ADR 본문 / 본 SKILL.md / domain-knowledge 별 SSOT 금지). 적용 = 사용자 dialog turn only — governance artifact (ADR / spec / change-plan / Story file) 는 codename 자연 사용 허용.

### codename → 평이 어휘 mapping (cap 15, 시점 1 baseline 2026-05-27)

| codename | 평이 어휘 (1:1) | 비고 |
|---|---|---|
| Story | 작업 단위 | codeforge SDLC 1 단위 |
| carry / carry-over | 이어 옮기다 / 다음으로 옮겨감 | 결정 / 정보 전달 |
| drift | 원본과 어긋남 / 이탈 | repo / file 일관성 깨짐 |
| spec | 명세서 | brainstorm 산출물 |
| scope manifest | 변경 범위 목록 | PR scope 명시 |
| ADR | 결정 기록 | Architecture Decision Record |
| Amendment | 수정안 / 후속 수정 | 기존 ADR 후속 결정 |
| sub-agent / agent | 부속 작업자 / 작업자 | spawn 단위 |
| lane | 작업 영역 | 8 lane plugin family |
| Phase 1 / Phase 2 | 1차 단계 / 2차 단계 | PR split |
| Layer N | N층 / N단계 | ADR-071 cognitive enum |
| sub-mechanism | 부속 매커니즘 | ADR-071 §결정 4 |
| mid-turn | 발화 도중 | Amendment 8 핵심 |
| forcing function | 강제 매커니즘 | governance ratchet |
| ratchet | 강화 방향 고정 | sunset asymmetry |

신규 어휘 도입 (16번째+) = **별 후속 CFP 의무** (ratchet extensibility). 정확 lookup = `docs/wording-dictionary.md` 카테고리 (c) verbatim.

- 본 §결정 19 = mechanism 추가 — **5번째 cognitive layer 신설 금지 invariant 보존** (§결정 3 4-layer enum count 불변, §결정 12.3 정합).
- Mechanical layer (lint-time post-write detection — `check-codename-glossary-lookup.sh` 등) / Consumer false positive (overlay `jargon_filter_exempt_vocabulary` — 별 follow-up CFP): 상세 = ADR-071 §결정 19 SSOT.
