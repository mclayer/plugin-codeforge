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
| 4 | **위 셋 바탕으로 메시지 작성** — step 1+2+3 통합 위에 본문. **mid-turn glossary lookup 의무** (ADR-071 §결정 19, Amendment 8 — CFP-1764): agent burst output paste 합성 시 codename 발견 시 [`docs/wording-dictionary.md`](../../docs/wording-dictionary.md) 카테고리 (c) lookup → 평이 어휘 1:1 치환 또는 평문 풀이 동반. closed 15 codename 첫 batch + ratchet extensibility (신규 어휘 = 별 후속 CFP) |

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

- Layer 1 preamble mechanical lint — 별도 follow-up CFP
- agent ↔ agent debate (CFP-582 cover)
- 코드 품질 / 보안 / 성능
- 사용자 personal memory entry 자체 삭제 (사용자 영역)
- consumer overlay 영역 customization (overlay 가 정책 축소 불허)
- debate-protocol-v1 3 marker import (schema 직접 채택 절대 금지)

## DialogFidelityAgent spawn anchor (ADR-071 §결정 13 / CFP-818)

> normative SSOT = [playbook §3.14 verifier auxiliary](../../docs/orchestrator-playbook.md) + [ADR-071 §결정 12·13](../../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md). 본 sub-section = **lookup mirror only** (skill body precedence 정합 — [ADR-064 §결정 10](../../docs/adr/ADR-064-decision-principle-mandate.md) normative > skill body 우선).

### 3-anchor 발화 형태 매핑

| anchor | 발동 시점 | 발화 형태 (UC) |
|---|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / AskUserQuestion 직전) | UC-1 (AskUserQuestion) / UC-2 (numbered list / dialog format) / Layer 3 stem detect |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (사용자 보고 발화 직전) | UC-3 (ArchitectPL 결과 보고) — Codex TP#2 mandatory dedup |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 | UC-4 (root cause 판정) — Codex TP#3 dedup |

### turn-shape edge × 3-anchor 12 cell 활성 표

| anchor \ edge | E9 streaming | E10 tool-call-only | E11 popup | E12 trivial |
|---|---|---|---|---|
| `post_user_turn` | final flush 시 활성 | 면제 | active | 면제 |
| `pre_architectpl_synthesis` | active | active | active | active |
| `pre_fix_rootcause` | active | active | active | active |

cell 값: `active` (spawn 의무) / `면제` (spawn 금지) / `final flush 시 활성` (E9 streaming 의 final flush 1회만).

### Output Port closed enum (Story-1 결정 SSOT, 변경 0)

- `verify_result: fidelity_ok | drift_detected | ledger_gap`
- `correction_action_hint: rescan_ledger | escalate_user | self_correct | no_action | null`

free-form output 차단 (generator 역할 침범 금지).

### Inline whitelist 1번 entry 정합

DialogFidelityAgent spawn (subagent 형태) = [ADR-039 §결정 2](../../docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry 1번 entry (사용자 dialog) scope **안** cognitive 보강. 5번째 entry 신설 아님 (closed enumeration 보존).

### Q-3check disjoint scope

[ADR-064 §결정 9](../../docs/adr/ADR-064-decision-principle-mandate.md) Q-3check = Orchestrator self-check. DialogFidelityAgent = 외부 verifier. disjoint — 양자 cross-cutting 보강.

### closed enum 확장 시 별도 CFP 의무

3-anchor closed. 확장 후보 (`pre_lane_spawn` / `pre_phase_transition` / `pre_pause_decision`) 발생 시 별도 CFP 신설 의무.

## Conversational reporting frequency suppression (ADR-071 §결정 15 / CFP-851 / Amendment 4)

> normative SSOT = [playbook §3.14 frequency suppression](../../docs/orchestrator-playbook.md) + [ADR-071 §결정 15](../../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md). 본 sub-section = **lookup mirror only** (skill body precedence 정합 — [ADR-064 §결정 10](../../docs/adr/ADR-064-decision-principle-mandate.md) normative > skill body 우선).

### 본질 anchor — frequency vs richness 분리 invariant

본 정책이 좁히는 것은 **말 거는 횟수·시점** (frequency / timing) 만. **말할 때의 풍부함은 §결정 2(c) "3 줄 제약 거부 · 길이 자유 · 배경 포함" 그대로 보존**. 두 축 분리 = ADR-058 §결정 5 약화 차단 (`sunset_justification: null`) 근거.

### 3 touchpoint closed enumeration

| touchpoint | 발화 사유 | scope |
|---|---|---|
| **(a) 결과-명세 확인** | 사용자 선언 결과 자체 모호 + 잘못 추측 시 rollback 비싼 경우 (verifiable outcome surface 안전판) | `AskUserQuestion` 발화 (§결정 5 결정 트리 — 모호 → 가치 측 분류) |
| **(b) 사용자만 풀 수 있는 차단** | 인증·권한 등 codeforge 자체 해소 불가 | ADR-039 inline whitelist 1번 entry (사용자 dialog) scope 안 |
| **(c) 최종 완료 보고 1회** | 요청한 작업 단위 전체 완료 | ADR-039 inline whitelist 4번 entry (Status report) scope 안 |

그 외 진행·중간 결정·근거·중간 결과 = 산출물 channel (대화 turn 아님): Story file / change-plan / ADR / PR description / Issue comment / TodoWrite panel.

### 무약화 invariant — turn 발생 시 적용

3 touchpoint 발화 시 다음 모두 그대로 적용:
- Layer 1 가시적 preamble + Layer 2 자기 declare (turn-shape edge derived default 무변경)
- §결정 2(c) richness (raw packet 노출 금지, 평이한 한글, 3 줄 제약 거부, "왜 / trade-off / 걸려있는 것" 배경 포함)
- DialogFidelityAgent 3-anchor spawn (§결정 12/13)
- §결정 14 incident append-rate measurement

### closed enum 확장 시 별도 CFP 의무

4번째 touchpoint 신설 시 별도 CFP 의무 (ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification + Story §1 사용자 explicit 승인 의무). 본 ADR-071 안 3번째 closed enumeration 인스턴스 (3-anchor enum / 4 차원 enum / 3 touchpoint enum 동형).

### mechanical lint = 별도 follow-up CFP

§결정 15 = behavioral directive only. 3 touchpoint 외 발화 자동 감지 + 억제-induced rework 측정 = 별도 follow-up CFP scope (§결정 10 패턴 정합, dialog-fidelity-effect precedent runtime cron measurement 동형).

## Mid-turn glossary lookup (ADR-071 §결정 19 / CFP-1764 / Amendment 8)

> normative SSOT = [ADR-071 §결정 19](../../docs/adr/ADR-071-orchestrator-user-dialog-convergence.md) + [`docs/wording-dictionary.md`](../../docs/wording-dictionary.md) 카테고리 (c). 본 sub-section = **lookup mirror only** (skill body precedence 정합 — [ADR-064 §결정 10](../../docs/adr/ADR-064-decision-principle-mandate.md) normative > skill body 우선).

### 본질 anchor — agent burst paste 합성 시점의 mid-turn forcing function

§결정 2(c) "sub-agent 결과 평이 번역" 의무는 명시되나 *번역 mechanism 부재* — agent output prose 가 codeforge vocabulary 로 작성된 채 Orchestrator 가 합성 발화에 그대로 옮긴다. 본 §결정 19 = mid-turn paste-and-translate 시점 glossary lookup 강제. mctrader-hub#517 4-turn 누적 jargon leak evidence.

### lookup table SSOT location

**`docs/wording-dictionary.md` 카테고리 (c)** — closed 15 codename 첫 batch + ratchet extensibility. ADR 본문 / 본 skill SKILL.md / domain-knowledge 별 SSOT 금지 (single source of truth).

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

신규 어휘 도입 = 별 후속 CFP 의무 (ratchet extensibility). 정확 lookup = `docs/wording-dictionary.md` 카테고리 (c) verbatim.

### Scope (사용자 dialog turn only)

- **적용**: 사용자 dialog turn (Orchestrator 직접 발화) 영역
- **scope 외**: governance artifact (ADR / spec / change-plan / Story file) — codename 자연 사용 허용

### Forcing function 위치 — frame mode step 4 직전

frame mode step 3 (turn 결정 1 문장 정리) 와 step 4 (메시지 작성) 사이 cognitive 단계 — codename 발견 시 평이 어휘 치환 또는 평문 풀이 동반 의무 실행.

### 5번째 cognitive layer 신설 금지 invariant 보존

본 §결정 19 = mechanism 추가 (glossary lookup forcing function), §결정 3 4-layer cognitive enum count 변경 아님 (§결정 12.3 invariant 정합).

### Mechanical layer (Story-2 carrier)

- `scripts/check-codename-glossary-lookup.sh` PR diff scan + wording-dictionary 카테고리 (c) grep target
- `templates/github-workflows/codename-glossary-lookup.yml` warning-tier workflow
- `docs/evidence-checks-registry.yaml` 23번째 warning entry (`codename-glossary-lookup`)
- `hotfix-bypass:codename-glossary-lookup` 75번째 hotfix-bypass family member (label-registry-v2 v2.37 → v2.38 MINOR)

turn-final hook 부재 platform 한계 — lint-time post-write detection only, runtime mid-turn block 불가.

### Consumer false positive

consumer project (mctrader-hub 등) 가 동일 codename 을 비즈니스 용어로 사용하는 경우 (예: "drift" = 포트폴리오 변동), consumer overlay `jargon_filter_exempt_vocabulary: [...]` field 신설 — 별 follow-up CFP carrier (본 Amendment 8 scope 외).

### closed enum 확장 시 별 CFP 의무

15 codename closed enumeration. 16번째 entry 이상 도입 시 별 후속 CFP 의무 (ADR-064 §결정 5 CFP scope unitary + ADR-058 §결정 5 sunset_justification + Story §1 사용자 explicit 승인). 본 ADR-071 안 5번째 closed enumeration 인스턴스 (3-anchor enum §13.6 / 4 차원 enum §4 / 3 touchpoint enum §15.5 / trigger table §16 / **codename 15-batch §19**).
