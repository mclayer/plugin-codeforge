---
adr_number: 25
title: Stop discipline — non-whitelist stops as policy violation (Decider-decides ≠ user-confirms)
status: Accepted
category: Team & Process
date: 2026-05-03
carrier_story: CFP-73
related_files:
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md
  - docs/inter-plugin-contracts/stop-event-v1.md
  - CLAUDE.md
related_stories:
  - CFP-73
  - CFP-80
  - CFP-135
  - CFP-2573  # Amendment 3 carrier (ADR-144 L1 realization — vague-pause 행 + policy_violation_vague_pause subclass)
supersedes: null
superseded_by: null
amendment_log:
  - amendment_id: 1
    date: 2026-05-04
    scope: "Epic / 작업 단위 continuity directive (CFP-80) — 사용자 의도 단위 안의 모든 sub-decision / sub-CFP 자동 통과 + 1번 final report 의무 명시"
    status: applied
  - amendment_id: 2
    date: 2026-05-08
    scope: "ADR-022 deprecate (CFP-134 / ADR-035) 정합 — invariant trigger 의 Sonnet 표기 제거. 'Sonnet decides ⇒ Orchestrator proceeds' → 'PL pl_recommendation 결정 (review-verdict 단) / 직전 사용자 directive (작업 단위 단) ⇒ Orchestrator proceeds without user confirmation' 으로 generalize. ADR-025 정책 자체 (whitelist 외 stop = defect) 무손상 — Sonnet 라는 specific actor reference 만 정리."
    status: applied
  - amendment_id: 3
    date: 2026-07-05
    scope: "CFP-2573 carrier — vague-pause(decision-null verbalized form) 신설, ADR-144 §결정 2 L1 realization. §결정 7 illegal-stop 표에 vague-pause 행 추가(6번째): 판별조건 '잔여작업 有 + 결정 payload=0 + volitional 발화(ask-trigger 3종 미해당)', 예 '한 숨 쉬어가자', tier [advisory](plain-text turn-end·tool-mediation 부재로 runtime hard-deny 불가). §결정 10 reason_class subclass enum 에 policy_violation_vague_pause 추가. 강화(ratchet↑) 방향 — 기존 5행·3 subclass 무변경, 신규 class 1개 추가만. ADR-144 = anchor SSOT(3축 taxonomy: 축 A2 payload=0). is_transitional:false permanent 정합, sunset_justification N/A(ADR-058 §결정 5 강화 방향 면제)."
    status: applied
  - amendment_id: 4
    date: 2026-08-12
    reinterpretation: false
    scope: "CFP-2944 carrier — §결정 7 illegal-stop 표에 named form 2행 추가(7번째 status-report-then-halt = 정보성 보고 편승 정지[priming 인벤토리 4번째 form] / 8번째 limit-signal-halt = 한도류 신호 발 의지적 정지[5번째 form]) + **form-set fence 신설**(illegal-stop named form inventory v1 = over-halt · over-ask · vague-pause · status-report-then-halt · limit-signal-halt 5 id, 기계 SSOT). 각 신규 행은 discriminant 3항을 primary 로 명기하고 예시는 보조(비망라), negative control 동반. §결정 10 = **기존 분류 재사용, 신규 enum 0** — status-report-then-halt → 기존 subclass policy_violation_vague_pause / limit-signal-halt → stop-event-v1 기존 reason_class policy_violation_rate_limit_induced. §결정 6 whitelist 5종 **무변경**(세션 한도 미등재 유지 = 합법화 방지). consumer mirror(docs/consumer-guide.md §7.1) 선행 drift(vague-pause 행 부재 실측) 동반 해소 — §결정 9 가 선언한 mirror 의무의 이행. 강화(ratchet↑) 방향: 기존 6행·4 subclass·whitelist 5종 무변경, illegal 표 행 추가만."
    status: proposed
is_transitional: false
---

# ADR-025: Stop discipline — Decider-decides ≠ user-confirms

## 상태

Accepted (2026-05-03). ADR-022 amendment carrier — ADR-022 §결정 11 Phase 1 trust model boundary 명확화. Amendment 2 (2026-05-08, CFP-135) — ADR-022 deprecate (CFP-134 / ADR-035) 후속 invariant 정정.

## 컨텍스트

ADR-022 (CFP-61, 2026-05-02) 가 Sonnet decider 자동 진행 + 5 종 user escalation whitelist 정의. Phase 1 trust model 이 hook / refusal logic 없음 명시. **Amendment 2 (2026-05-08, CFP-135 / CFP-134 / ADR-035) 후**: ADR-022 Deprecated → invariant 의 actor 표기를 generalize ("Sonnet" → "PL pl_recommendation / 직전 사용자 directive"). ADR-025 정책 자체 (whitelist 외 stop = defect) 무손상.

데뷔 운영 (mctrader 15 Story / codeforge dogfood ~67 Story, 2026-05-02 ~ 05-03) 에서 사용자 호소: "phase 상 사용자 stop 너무 많아 생산성 저하". Codex audit (gpt-5.5 high, 2026-05-03) 진단: "ADR-022 can be misread as requiring user confirmation after Sonnet decisions" — trust model 의 trust 가 "Sonnet pick → 자동 진행" 이지 "Sonnet pick → user confirm" 아님이 ADR-022 본문에 명시 부재.

Story §12 Sonnet Decision Log row 0건, mctrader 데뷔-audit feedback Issues 0건 — 측정 채널 부재가 Phase 2 transition (30+ packet) 자체를 unreachable 로 만드는 secondary problem 확인.

## 결정

### 결정 1 — Trust model invariant 명시

**(Amendment 2, 2026-05-08, CFP-135 정정 후)**: invariant 의 actor 표기 generalize — **"Decider decides" implies "Orchestrator proceeds without user confirmation"**. Decider 의 actor 분류 (post-ADR-022 Deprecated 정정):
- **review-verdict (DesignReview / CodeReview / SecurityTest)**: PL `pl_recommendation` (PASS / FIX / FIX_DISCRETIONARY) = decider. PL 직접 write (Story §9 / GitHub comment / gate label / phase transition).
- **작업 단위 (Epic / Story / backlog)**: 사용자 직전 directive = decider (작업 단위 식별). Orchestrator 가 작업 단위 안 모든 sub-decision / sub-step 까지 자동 통과 + 1번 final report.
- **사용자 explicit ad-hoc Sonnet request**: 사용자 directive ⇒ Sonnet decider 임시 invoke (codeforge 자동 발동 무효).

**(이전 ADR-022 active 시 표기, history record)**: ~~ADR-022 적용 시 invariant: "Sonnet decides" implies "Orchestrator proceeds without user confirmation". Sonnet decider 가 PASS / FIX / pick 응답 후 Orchestrator 가 사용자에게 "진행할까요?" / "이대로 가도 됩니까?" 묻는 것은 5 종 whitelist 미발화 시 policy violation (defect).~~

위 invariant 의 정신 (whitelist 외 stop = defect) 은 무변. actor reference 만 정리 (ADR-022 Deprecated → PL / 사용자 directive 로 actor remap).

### 결정 2 — Whitelist 외 stop 발화 = defect 분류

ADR-022 §결정 2 의 5 종 whitelist 외 stop 모두 `reason_class: policy_violation` 으로 stop-event-v1 ledger 에 기록. defect 추적 의무. PMOAgent retro 시 분석 대상.

### 결정 3 — Brainstorming option 자동 진행 vs design approval gate

brainstorming skill 의 substantive choice 발화 시:
- 사용자가 **"결정 의뢰" / "선택해줘" / "최적화해줘" 명시** 한 경우 — trigger (a) option-formulation 자동 발화 + Sonnet pick 후 진행. design approval gate 우회.
- 사용자가 **"선택지 보여달라" / "초안 보여달라" 명시** 한 경우 — design approval gate (skill 정책 우선).

### 결정 4 — Phase boundary

- **Phase 1** = doc-only (본 ADR + stop-event-v1 schema). Enforcement hook 없음.
- **Phase 2** = ROI-driven (30+ stop event 누적 후 별도 CFP). Hook / refusal logic / runtime validation 도입 여부 결정.

## 거부된 대안

### 대안 A — ADR-022 본문 amendment

거부 사유: ADR-022 가 이미 ADR-019 supersede + long body. 신규 carrier ADR 가 history clean. ADR-019 amendment 1 precedent 와 다른 방향 (ADR-019 → ADR-022 supersede 한 case 와 본 case 의 magnitude 차이 — 본 ADR 은 trust 의미 명확화만, ADR-022 §결정 11 의 Phase 1 trust model 자체 변경 아님).

### 대안 B — Hook / refusal logic 즉시 도입

거부 사유: ADR-022 §결정 8 Phase 2 ROI 평가 SSOT 위반. measurement 없이 enforcement 도입 시 over-correction 위험 (hook 이 잘못 분류하면 사용자 통제 상실).

## 결과

긍정:
- 정책↔실행 gap 명확화. defect 분류 가능.
- stop-event ledger (Phase 2 PR sibling) 와 짝 — amendment 효과 검증 채널 확보.
- ADR-022 본문 변경 없음 (cross-ref only) — history clean.

부정:
- ADR-019 → ADR-022 → ADR-025 supersession chain noise 가능성 — 단 본 ADR 은 amendment 관계 (no supersede), 정합.
- enforcement 부재 (Phase 1 trust model 정합) — 측정 데이터 누적 후 Phase 2 enforcement 결정 의무.

## ADR 정합성

- **ADR-022**: amendment relation (no supersede). 본 ADR 의 §결정 1 invariant 가 ADR-022 §결정 11 Phase 1 trust model 의 trust 의미를 명확화.
- **ADR-021**: stop-event-v1 ledger 가 R1-R4 detection source 보강 (R1 Missing agent finding repeat / R3 Phase gap propagate).
- **ADR-024**: story-scoped branch policy 정합 (1 PR 통합 옵션 거부 정합 — 본 ADR carrier Story 도 cfp-73-stop-discipline branch + Phase 1/Phase 2 PR 분리).

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/adr/ADR-022-sonnet-review-verdict-decider.md`
- `docs/inter-plugin-contracts/stop-event-v1.md` (Phase 2 sibling)
- `CLAUDE.md`

## Amendment 1 (CFP-80 — 2026-05-04): Epic / 작업 단위 continuity directive

### 동기

ADR-025 §결정 1 trust model invariant 명시 후에도 Orchestrator session 의 actual behavior = 작업 단위 안 sub-phase / sub-CFP 마다 stop 패턴 반복. 사용자 명시 (2026-05-04): "하나의 Epic 이 전체 phase 를 모두 따르고 그 과정과 결과를 한번에 밝혀야 하는데 phase 단위로 자꾸 끊어댄다."

본 amendment = §결정 1 trust model 의 stricter application — Orchestrator 가 **단일 PL pl_recommendation pick** (Amendment 2 정정 후 — 이전 ~~"단일 Sonnet pick"~~) 자동 진행에서 그치지 않고, **사용자 의도 단위 (Epic / backlog / Story)** 안의 모든 sub-decision / sub-CFP 까지 자동 통과 + 1번 final report 의무 명시.

### 결정 5 — Orchestrator 작업 단위 continuity 의무

사용자 메시지 받은 시점 = 작업 단위 식별:

| 사용자 메시지 패턴 | 작업 단위 | Continuity 의무 |
|---|---|---|
| "다음 작업 있나" + 1+ 후보 존재 | 모든 후보 / backlog 처리 단위 | backlog 모든 issue / CFP 자동 통과 + 1번 final report |
| "X 진행" (X = Epic 명시) | Epic 의 7 phase + 모든 child Story | child Story 모두 Phase 1 + Phase 2 PR cycle 자동 통과 + 1번 final report |
| "X 진행" (X = Story 명시) | Story 의 Phase 1 + Phase 2 PR cycle | 양 PR cycle 자동 통과 + 1번 final report |
| 명시 선택 ("a" / "C" / "ok" / "진행하자") | 직전 메시지의 후보 또는 진행 path | path 끝까지 자동 진행 |
| 정보 요청 ("X 보여달라" / "X 가 뭐냐") | 정보 답변 단위 | 답변 + stop 없음 (작업 진행 없음) |

작업 단위 안에서 발생하는 모든 sub-decision = **PL pl_recommendation 적용 (review-verdict 단)** + 직전 사용자 directive 으로 자동 통과 (Amendment 2 정정 후 — 이전 ~~"ADR-022 trigger 5종 자동 처리 + Sonnet pick 적용"~~, ADR-022 Deprecated 후 무효). 본 sub-decision 마다 사용자 confirm 받음 = **policy violation (defect)** — §결정 2 와 동일 분류.

### 결정 6 — 합법 stop whitelist (5종 strict)

§결정 1 trust model invariant 와 정합. ADR-022 §결정 2 escalation whitelist 의 strict 적용:

1. **User environment 변경 의무** (PAT 발급 / API key / 외부 서비스 가입 / KRW 입금 / 1Password setup 등) — 사용자 직접 작업 의무
2. **Destructive action 직전** (force push / DB drop / 설정 영구 변경 / live-real first trade) — 단 sub-decision 까지 stop 안 함
3. **진정 unprecedented / unscoped 영역** (새 organizational decision, brainstorming skill default)
4. **Decider escalation 결정** — Amendment 2 정정 후: PL pl_recommendation = `ESCALATE_PACKET_INCOMPLETE` 또는 사용자 ad-hoc Sonnet 호출 시 escalation_required=true. 이전 ~~"Codex+Sonnet decider 의 escalation 결정 (decision-packet `decider_decision.escalation_required=true`)"~~ 표기는 ADR-022 Deprecated 후 actor remap.
5. **작업 단위 완료 후 final report** (1번)

위 5종 외 모든 stop = defect 분류. stop-event-v1 ledger `reason_class: policy_violation` 기록.

### 결정 7 — 불법 stop 패턴 명시 (반드시 회피)

| Pattern | Defect 사유 |
|---|---|
| "후보 A/B/C/D 중 어떤거?" | sub-decision 자동 처리 의무 — PL pl_recommendation / 직전 사용자 directive 로 자동 진행 (Amendment 2 정정 후, 이전 ~~"Codex+Sonnet 자동 처리 의무"~~) |
| "큰 작업이라 확인 받겠습니다" | token cost 추정 = 사용자 의도 아님 |
| "Phase 1 완료, Phase 2 시작할까요?" | 1 Story / Epic 안의 sub-step (decision unit 분리 violation). 확인 질문 form = `over-ask` (fence 등재 id — 본 표의 다른 확인-질문 행들도 동 form 의 변형이며, 전파면 anchor 요건은 **id 당 최소 1곳**이다: §A4-2) |
| "5 sub-CFP 중 첫 번째 완료, 다음 진행할까요?" | backlog 단위면 5 모두 처리 |
| "final report 후 다음 작업 후보 결정 받음" | backlog 안 끝났으면 자동 발굴 + 진행 |
| "한 숨 쉬어가자" 류 (vague-pause — Amendment 3, CFP-2573) | **decision-null pause (verbalized form)** — 잔여작업 有 + 결정 payload = 0 + volitional 발화, ask-trigger 3종(① 요구 애매 / ② 진짜 가치 trade-off / ③ 비가역·고비용) 어디에도 미해당 → 정당 사유 부재. `[advisory]` — plain-text turn-end·tool-mediation 부재로 runtime hard-deny 불가(ADR-144 §결정 1/2 축 A2 payload=0), 명명·예방까지만. `over-halt`(무발화 silent form)의 발화판 (GAP-3) |
| "다음은 X 단계입니다" 류 정보성 보고 후 정지 (status-report-then-halt — Amendment 4, CFP-2944) | **decision-null pause (보고-편승 form)** — vague-pause 와 동일 축(A2)의 미명명 표층형. **판별은 discriminant 3항이 primary**(잔여작업 有 ∧ 결정 payload = 0 ∧ volitional 발화)이고 위 예시는 **보조·비망라**다 — 열거를 primary 로 쓰면 6번째 form 이 또 빠져나간다. 진행 보고 자체는 의무(§결정 8 · ADR-038)이므로 **보고의 정당성이 뒤따르는 정지의 정당성으로 전이되지 않는다**(halo 차단). negative control(정당 구분선): 보고 후 즉시 다음 작업 계속 / 작업 단위 완료보고(terminal — whitelist 5번) / ask-trigger 3종 해당 발화(payload > 0). `[advisory]` — turn-end plain-text 라 runtime hard-deny 불가, 명명·예방까지만 |
| "세션 한도라 여기서 멈추겠습니다" 류 한도류 신호 발 정지 (limit-signal-halt — Amendment 4, CFP-2944) | **한도류 신호를 근거로 한 의지적 정지** — vague-pause 와 동일 축(A2, payload = 0). 대상 = 선제적 정지 제안("리셋 후 재개하시죠") · 자식 리밋을 Story 종료로 오처리 · 제어 회복 후 재확인 질문·무발화 정지. 신호 판정 = ADR-109 Amendment 2 판별식 D(`D-out-1`·`D-out-2`), 6-literal 열거는 비망라 fast-path. 세션 한도는 §결정 6 whitelist 5종에 **미등재이며 등재하지 않는다**(합법화 방지). negative control(정당 구분선): `D-out-2` 의 **1회 통지**(whitelist #1 User environment 변경 의무 — 통지는 정당, "통지 후 무기한 대기"만 부당) / 통지 후 이어갈 가용 잔여작업이 실제로 0(whitelist #1 정지 성립) / 세션이 **실제로 사망**한 비의지적 종료(축 C — ADR-110 · ADR-071 §결정 24 복구 경로). `[advisory]` — runtime hard-deny 불가(한도 순간 토큰 발화 불가 구간은 정의역 밖) |

**form-set SSOT (Amendment 4 신설 — 기계 원본)**: 아래 fence 가 illegal-stop **named form id 집합**의 유일 원본이다. 위 표는 사람이 읽는 렌더면, hook priming TEXT 2채널(`hooks/story-transition-autonomy-reminder.py` · `scripts/lib/agent_spawn_transition_reminder.py`)과 `docs/consumer-guide.md` §7.1 은 전파면이다. **fence ↔ 표 ↔ priming TEXT ↔ consumer mirror 중 어느 한 쌍이라도 form id 집합이 불일치하면 검사 위반**(정적 검사 — 관측 tier, merge 무차단. 강제력 상한은 Amendment 4 §A4-6).

```
# illegal-stop named form inventory v1 (ADR-025 Amendment 4 / CFP-2944)
# 형식: <form-id> | <축> | <표 anchor 예시>
over-halt | A2 | 무발화 정지
over-ask | A1 | "다음 진행할까요?" 확인 질문
vague-pause | A2 | "한 숨 쉬어가자" 류
status-report-then-halt | A2 | "다음은 X 단계입니다" 류 보고 후 정지
limit-signal-halt | A2 | "세션 한도라 여기서 멈추겠습니다" 류
```

### 결정 8 — Result 보고 형식 (1번)

- 작업 단위 전체 완료 후 1번 final report
- Sub-step 별도 완료 시각 / 소요 시간 / decider pick (PL pl_recommendation 또는 사용자 ad-hoc Sonnet pick) / override marker 포함 (Amendment 2 정정 후, 이전 ~~"Sonnet pick"~~)
- 사용자 redirect 가능성 명시 (단 본인이 stop 안 함)

본 보고 형식 = `feedback_progress_time_reporting.md` (작업 완료 시간 + 소요 시간 reporting 의무) 의 자연 확장.

### 결정 9 — Consumer scope (mctrader / 향후 다른 consumer)

ADR-022 §결정 11 Phase 1 trust model — codeforge-family + consumer 모두 적용. 본 amendment 도 동일 scope:

- Consumer Orchestrator 도 Epic-level continuity directive 적용 의무
- Consumer 측 사용자 명시 directive 발화 의무 (Phase 1 trust model — enforcement hook 없음)
- Phase 2 (ROI-driven instrumentation, 30+ stop event 후) 의 hook / refusal logic 도입 시 consumer 측도 동일 적용

Consumer 측 적용 가이드 = `docs/consumer-guide.md` § "Stop discipline + Epic-level continuity" 섹션.

### 결정 10 — Phase 2 stop-event-v1 ledger 의 본 amendment 영향

`stop-event-v1` schema 의 `reason_class` enum 에 본 amendment 의 위반 패턴 명시:

- `policy_violation` (기존, §결정 2 — whitelist 외 stop)
- `policy_violation_subdecision` (본 amendment, §결정 7 — 작업 단위 안 sub-decision stop)
- `policy_violation_phase_split` (본 amendment, §결정 7 — Phase 1/2 사이 stop)
- `policy_violation_vague_pause` (Amendment 3, CFP-2573 / §결정 7 — decision-null verbalized form "한 숨 쉬어가자", payload=0 volitional 정지. ADR-144 §결정 2. free-form `reason_class_subclass` 로 표현 = non-breaking, 4-enum `reason_class` member 추가 0)

- **Amendment 4 (CFP-2944) — 신규 enum 0**: `status-report-then-halt` = 위 `policy_violation_vague_pause` subclass **재사용**(같은 축 A2 의 표층형이라 신규 subclass 불요). `limit-signal-halt` = `stop-event-v1` **기존** `reason_class` 인 `policy_violation_rate_limit_induced` 재사용(집계 `_ILLEGIT` 버킷에 이미 포함 — `scripts/lib/aggregate_stop_event.py`). 따라서 4-enum `reason_class` member 추가 0 · 신규 subclass 0 · 계약 v1.x 무변경(stop-event-v1 §3.4 "5번째 enum 추가 = BREAKING" 미저촉).

stop-event-v1 ledger Phase 2 도입 시 본 sub-classification 으로 측정 → consumer + wrapper 양쪽 행동 데이터 누적.

### 결정 11 — Memory feedback 동등 SSOT

본 ADR-025 = wrapper SSOT. memory feedback (`feedback_epic_level_continuity.md`) = session-level enforcement (Claude Code memory directive). 양자 정합 의무 — 한쪽 변경 시 다른 쪽 동기 update.

### Cross-references

- ADR-022 §결정 11 (consumer-side Phase 1 trust model) — 본 amendment 의 consumer scope 근거
- ADR-021 R1-R4 (stop event detection source)
- mctrader-hub 측 Live Mode Epic (mctrader-hub#56) — Phase 2~N implementation 시 본 amendment 적용 (Story-level Phase 1+2 PR cycle 자동 통과)
- `feedback_epic_level_continuity.md` (session memory directive)
- `feedback_no_clarification_default.md` (substantive choice 자동 처리 default)
- `feedback_codex_review_auto_proceed.md` (Codex audit 게이트 = user approval 게이트 대체)

## Amendment 4 (CFP-2944 — illegal-stop named form 2종 추가 + form-set SSOT fence 신설)

**날짜**: 2026-08-12 KST · **carrier**: CFP-2944 · **status**: Proposed (Phase 1 draft — 설계리뷰 PASS 전) · **방향**: **강화**(illegal 표 행 추가만, whitelist·enum 확대 0).

### A4-1. 왜 예시 인벤토리가 표류했나 (근본원인 — 재발 계보)

Amendment 3(2026-07-05)이 vague-pause class 를 명명한 **당일부터 5주 이상** 경과했음에도 사용자가 같은 불만을 다시 제기했다. 원인은 정의의 불완전이 아니라 **정의를 운반하는 물리적 표층의 불완전**이다:

```
ADR-144 §결정 2 discriminant (정의)   ← "다음은 X 단계입니다" 를 이미 포섭
   │  (독립 아티팩트 — 자동 갱신 없음)
   ▼
ADR-025 §결정 7 named 예시 열거        ← "한 숨 쉬어가자" 1개만, 갱신 안 됨   ← 여기
   ▼
hook priming TEXT (정의가 아니라 예시를 인용)
   ▼
turn-end 자기검열 — salient 한 예시가 없으면 self-recognize 실패
```

discriminant tier 는 `[advisory]`(turn-end plain-text)라 매 turn 재적용을 기대할 수 없고, 실제 자기검열은 **예시 인벤토리**로 일어난다. 인벤토리가 별도 아티팩트라 동기화 강제가 없었다 — 이것은 ADR-144 가 정직하게 선언한 platform 상한(GAP-1/GAP-2)이 **아니라** 단순 유지보수 누락이다. 두 가지를 혼동하면 "이미 GAP 선언했으니 재발 아니다"로 오분류된다.

### A4-2. form-set fence = 기계 원본 (두-주인 방지 규약)

§결정 7 에 신설한 fence 가 form id 집합의 유일 원본이다. **표는 렌더면**이고 hook priming TEXT 2채널·`docs/consumer-guide.md` §7.1 은 **전파면**이다.

- **검사 방향 2**: ① fence 의 모든 id 가 §결정 7 표 region · priming TEXT 2채널 · consumer mirror 에 존재 ② 그 4면 중 어디에도 fence 밖 신규 form id 가 단독 등장하지 않음. 어느 방향이 깨져도 검사 위반이다(fence↔표 drift 포함 — 두-주인 SSOT 재생산 차단, CFP-2879 선례).
- **검사 스크립트는 form id 리터럴을 하드코딩하지 않는다** — fence 를 파싱해 집합을 얻고 다른 3면과 대조한다. 하드코딩 사본 = 경쟁 SSOT ∧ hollow 재생산(ADR-109 Amendment 1 (c) 동형 규율).
- fence 는 id 와 축만 담고 **tier 라벨을 담지 않는다** — tier 선언면은 §결정 7 표 1곳으로 유지한다.

**form id anchor 표기 규약 (신설 — 검사 방향 2 의 성립 전제)**: 방향 ②(면→fence 초과 검출)는 "면에서 form id 후보를 추출"할 수 있어야 성립하는데, 한글 산문 안 bare kebab 토큰은 일반 어휘와 구별되지 않아 추출 자체가 불가능하다. 따라서 **전파면**(§결정 7 표 · priming TEXT 2채널 · consumer mirror)에서 form id 는 다음 둘 중 하나로 표기한다 — ① backtick 감싼 형태 ② `(<form-id> — …)` 형태(dash 구분 동반). 요건은 **id 당 전파면마다 최소 1 anchor** 이며, 같은 form 의 모든 인스턴스 문장에 anchor 를 붙일 의무는 없다(렌더 가독성 보존).

- **fence 자신은 규약 대상 밖**이다 — fence 는 `<form-id> | <축> | <anchor 예시>` 파서 원본이라 backtick 을 넣으면 파싱 값이 오염된다.
- **규약은 본 amendment 가 신설**하며 착지 상태는 면마다 다르다: §결정 7 표 = 본 Phase 1 에서 전 id anchor 충족. priming TEXT 2채널 · consumer mirror = **현행 미준수**(전자는 bare 괄호 표기, 후자는 form id 자체가 0) → Phase 2 §A4-7-1/2 착지 대상. **착지 전까지 그 2면에 대한 방향 ② 실검출은 0** 이다(추정 아닌 실측 — §A4-6-5).
- **검사 어휘 분별 의무**: 추출기는 fence 등재 form id 와 **taxonomy class 명**(`decision-null` · `ask-trigger` 등 — ADR-144 §결정 2 소유)을 구분해야 한다. 후자는 form id 가 아니므로 anchor 표기로 등장해도 방향 ② 위반이 아니다.

### A4-3. 신규 2 form 의 축 배정 (ADR-144 taxonomy 무손상)

| form id | 축 | 근거 |
|---|---|---|
| `status-report-then-halt` | **A2** | 잔여작업 有 ∧ payload = 0 ∧ volitional 발화 — discriminant 3항 전건 충족. 보고문은 payload 가 아니다(결정 요구 0) |
| `limit-signal-halt` | **A2** | 동상. 단 "새 세션에서 이어가시죠"처럼 **사용자 액션을 요구하는 변형은 A1** — payload > 0 이나 ask-trigger 3종 미해당이라 여전히 illegal |

**축 B/C 와의 경계(오분류 1순위 — ADR-144 §결정 1 핵심 경고 승계)**: 자식 완료 통지 미도달로 갇힌 delivery-gap(P10)은 **축 B(비의지적 stall)** 이고, 세션이 실제로 죽은 경우는 **축 C** 다. 둘 다 본 amendment 대상이 **아니다** — 대화 규칙으로 고치면 무효이며 force-resume(ADR-039 §결정 19) 또는 복구 경로(ADR-110 · ADR-071 §결정 24)로만 해소된다. **판별자**: "그 시점에 다음 tool call 을 할 수 있었는가" — 할 수 있었는데 안 함 = 축 A. 본 Story 진행 중 축 B stall 3회가 관측됐고 그 발화 표면이 A2 와 구별하기 어려웠다 — 오분류 시 remedy 가 정반대(축 B = force-resume vs 축 A = 자기검열)이므로 판별자 적용이 선행 의무다.

### A4-4. whitelist 5종 무변경 (§결정 6 — 합법화 방지)

"세션 한도 도달"을 whitelist 6번째로 **추가하지 않는다**. 추가는 "멈춰도 된다"는 신규 승인이므로 약화 방향이고 ADR-058 §결정 5 evidence-gate 를 발동시킨다. 반면 illegal 표 행 추가는 강화 방향이라 정합이다. 세션 한도 정지는 **현행 체계에서도 이미 whitelist 밖 defect** 였다 — 본 amendment 는 그 사실을 named form 으로 가시화할 뿐 새 금지를 창설하지 않는다.

**whitelist #1 carve-out 보존**: `D-out-2`(remedy 주체가 사람)에서 필요한 액션을 **1회 통지**하는 것은 whitelist #1(User environment 변경 의무) 정당 발동이다. 본 amendment 가 금지하는 것은 **통지 후 무기한 대기**뿐이며, 통지 후 이어갈 가용 잔여작업이 실제로 0 이면 whitelist #1 정지가 그대로 성립한다(over-suppression 방어).

### A4-5. consumer mirror 동기 (§결정 9 이행)

§결정 9 는 consumer 적용 가이드를 `docs/consumer-guide.md` § "Stop discipline + Epic-level continuity" 로 지정한다. 실측 결과 그 mirror 는 **Amendment 3 이후 미동기화** 상태다 — `docs/consumer-guide.md` §7.1 불법 stop 표에는 §결정 7 이 Amendment 3 에서 등재한 `vague-pause` 행이 **부재**하고, `vague-pause` · `over-halt` · `over-ask` · `decision-null` · `ask-trigger` **전 패턴이 0-hit** 이다(패턴 grep 기준 — 행수 대조가 아니다). 즉 §결정 7 form-set fence 가 등재한 named form id 중 consumer mirror 에 존재하는 것은 **본 Phase 1 착지 시점 실측 기준 0 건**이다(Phase 2 §A4-7-2 동기화로 해소 예정). 본 amendment 는 §결정 7 을 확장하므로 동기화 없이 진행하면 drift 가 `vague-pause` **1 form 에서 신규 2 form 을 더한 form 집합 전체**로 확대된다. 따라서 consumer mirror 동기화를 본 amendment 범위에 포함한다(신규 의무 창설이 아니라 §결정 9 가 이미 선언한 mirror 의무의 이행).

**행수 표기를 쓰지 않는 이유 (자기참조 절대수치 금지)**: 본 amendment **자신이** §결정 7 표에 행을 추가하므로 "wrapper §결정 7 은 N행" 류 현재시제 수치는 **착지 즉시 stale** 이 된다. 판정 기준은 **form 집합 술어**(fence ↔ §결정 7 표 ↔ priming TEXT 2채널 ↔ consumer mirror 의 id 집합 동일성)이며 행수·site 수 assert 가 아니다 — §A4-2 검사 방향 2 및 [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 8 A8-5 전수 술어와 동형이고, CFP-2944 Story INV-T6("자기참조 절대수치 assert 금지")의 정의역에 **본 amendment 문면 자체**가 포함됨을 여기서 명시한다.

### A4-6. 정직 천장 (강제력 상한 — over-claim 금지)

1. **행동 준수는 강제되지 않는다** — 어떤 정적 검사도 "실제로 안 멈췄는가"를 판정할 수 없다. 본 amendment 가 얻는 것은 **문서·기계 표면 간 정합**뿐이다.
2. **검출 sufficiency 는 원리적으로 미결정** — form-set 검사는 *등재된* form 의 4면 동기화만 본다. "6번째 form 을 미리 등재하게" 만들 수는 없다. 그래서 각 행이 **discriminant primary + 예시 보조**로 쓰여야 하며, 이 구조 요구는 review-tier 책임이다.
3. **검사 verdict 의 실 tier** — 현행 실행 채널(`orchestrator-autonomy-stop-taxonomy-check.yml`)은 job-level 및 step-level `continue-on-error: true` 이고 branch protection required contexts 에 미등재다. 즉 위반이 관측되어도 **merge 를 차단하지 않는다**. "이 검사로 차단한다" 류 표현을 쓰지 않는다. 승격 경로 = ADR-060 evidence-gate.
4. 현행 `check_vague_pause_taxonomy_presence.py` 는 taxonomy **라벨** 3 리터럴 presence 만 보고 **예시(named form)는 보지 않는다** — 유일 named 예시를 전삭제해도 `exit 0` 으로 생존함이 firsthand mutation 으로 확인됐다. 그 GREEN 을 본 amendment 의 acceptance 근거로 재사용하면 동어반복이다.
5. **방향 ② 는 anchor 규약 준수면에 한해서만 검출한다** — §A4-2 규약 밖 표기(한글 산문 안 bare kebab 토큰)로 신규 form id 를 심으면 **미탐**이다. 이는 장래 가능성이 아니라 **현행 실측**이다: priming TEXT 2채널의 현행 form id 3종은 전건 규약 밖 표기라 그 2면의 방향 ② 실검출은 **0** 이다(Phase 2 착지로 해소 예정). "방향 ② 완전 검출" 주장을 금지하며, 규약 준수 후에도 규약 밖 신설 표기는 미탐으로 남는다 — 그 잔여를 산문 고백으로 두지 않고 **생존 기대 mutant 로 박제**한다(CFP-2944 Story §7.12.3 `M-A5'`). 방향 ①(fence→면)만 표기 규약과 무관하게 완전하다.

### A4-7. Phase 2 실행 범위 (구현 PR — 본 Phase 1 PR 밖, 열거만)

**완료 bar 는 열거가 아니라 술어다** — 아래 1·2 의 판정 기준은 "몇 행을 추가했는가"가 아니라 **"판정 시점 fence 가 등재한 전 id 가 해당 면에 §A4-2 anchor 표기로 존재하는가"** 다. 열거를 bar 로 쓰면 fence 가 자라거나 선행 drift 가 있을 때 계획이 조용히 미달한다 — 본 amendment 자신이 그 미달을 실증했다(초안의 "vague-pause 행 + 신규 2행" 3행 열거는 fence 5 id 중 2 id 를 누락시켜, 계획을 완수해도 §A4-2 방향 ① 이 RED 로 착지하는 상태였다. 설계리뷰 iter2 F-A 지적 + §A4-8 dry-run 으로 검출).

1. hook priming TEXT 2채널 동형 확장 — **fence 전 id 가 §A4-2 anchor 표기로 존재**하도록. 현행 3 id 는 규약 밖 bare 표기이므로 **신규 2 id 추가 + 기존 3 id anchor 화**가 함께 요구된다(신규 hook 신설 0 · cross-hook 공유 helper 모듈 0 — ADR-144 §결정 3 + ADR-071 §22.7 CODE abstraction 금지).
2. `docs/consumer-guide.md` §7.1 mirror 동기 — 동일 술어. 현행 form id 존재 0 이므로 **fence 전 id 착지**가 요구된다(§A4-5 실측: 전 패턴 0-hit).
3. form-set parity 검사 신설(fence 파싱 기반) + `check_vague_pause_taxonomy_presence.py` self-test fixture 확장. 검사 스크립트의 자기 tier 선언 문구를 실 실행 채널 tier 와 일치하도록 정정(현행 자기 선언과 §A4-6-3 실측이 불일치).
4. workflow `paths:` 에 `skills/**` 추가(현재 부재 — mirror sweep 대상 누락) + `templates/github-workflows/` twin **byte-parity 동시 반영**(`invariant-check` required `diff -q`).
5. `CLAUDE.md` 결정·대화 원칙 절 bullet 추가.

### A4-8. 저작 자기적용 결박 (self-application binding — 정의역 총칙 + dry-run 의무)

**왜 조항별 확장이 아니라 총칙인가 (재발 계보 — firsthand)**: CFP-2944 는 "저작한 규범을 자기 산출물에 적용하지 않음"이라는 **단일 axis** 로 요구사항 lane 2회 · 설계리뷰 lane 2회, 총 4회전 연속 결함을 냈다. 1회전 처방은 문제가 표면화한 **조항 2개**(T5 인용 규율 · INV-T6 자기참조 수치 금지)에 각각 "정의역에 본 문면 포함" 한 줄을 붙이는 것이었다. 그 처방은 **같은 axis 의 다른 조항들에서 즉시 재발**했다 — 검사 계약(§A4-2 방향 ①)이 자기 Phase 2 계획으로 충족 불가한 상태로 착지했고, 방향 ② 는 전제가 거짓이라 실검출이 0 이었으며, 열거 drift 는 그 정정을 담은 FIX 안에서 다시 나왔다. 조항별 확장은 **∀ 를 사람이 손으로 전개**하므로 신설 조항이 자동 누락되고, 조항 수가 회전마다 늘어 O(n) 편집을 매번 요구한다. 따라서 quantifier 를 **한 곳에 두는 총칙**으로 대체한다.

**적용 주체 = CFP-2944 carrier 가 저작하는 전 문면**: 본 amendment · [ADR-109](ADR-109-in-process-429-mitigation-framework.md) Amendment 2 · [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 8 · Story `CFP-2944` §7. 본 규약의 **판정문 verbatim SSOT 는 본 절 1곳**이며 나머지 3 문면은 pointer 만 둔다 — 이는 ADR-141 §A8-5 가 규정한 mirror 정책의 적용이다(결박의 배치 자체를 본 carrier 자신의 규범으로 결정함으로써 자기적용을 실증한다).

**B-1. 정의역 총칙 (∀ — 조항별 예외 0)**: 위 주체가 저작하는 **모든 규범 술어·검사 계약**의 정의역에는 **그 술어를 저작한 문면 자체**가 포함된다. 조항마다 정의역 확장을 재선언할 의무는 없으며, **재선언이 없다는 사실을 정의역 밖 근거로 쓰는 것을 금지한다**. 장래 신설되는 조항도 별도 문구 없이 자동 포섭된다.

**B-2. dry-run 의무 (선언 ≠ 적용)**: 술어를 저작·개정할 때 그 술어를 **자기 산출물 전체에 1회 평가**하고 결과를 남긴다. RED 면 착지 전에 **(a) 산출물 수정** 또는 **(b) 술어 정의역의 명시 축소 + 축소 근거** 중 하나를 이행한다 — 둘 다 없이 착지 금지. **"정의역에 포함된다고 선언했으므로 적용됐다"는 추론을 금지한다**: 설계리뷰 iter2 F-A 는 정의역 *안*이면서 RED 였고 B-1 만으로는 잡히지 않았다. dry-run 결과는 Story `CFP-2944` §7.16 표에 **술어 단위**로 기록하며, **표에 행이 없는 술어는 미평가로 간주**한다 — 누락이 침묵하지 않고 표면화하는 것이 본 항의 실효 기전이다.

**B-3. 전제 검증 의무**: 술어가 다른 표기·구조 규약을 **전제**하면(예: §A4-2 anchor 표기), 그 전제가 **현행 대상면에서 성립하는지 실측**하고, 불성립이면 "규약은 신설 대상 · 현행 미준수 · 그 면의 실검출 0" 으로 declare 한다. 전제를 성립 가정한 채 검출력을 주장하지 않는다(iter2 F-B — 전제가 거짓이라 mutant 가 생존했고 천장 서술은 실상을 과소진술했다). **대응 mutant 는 전제를 만족하는 형태로 구성하되, 전제를 벗어난 형태를 별도 생존-기대 mutant 로 함께 박제**한다 — 검출 가능한 mutant 만 두면 검사연극이고, 산문 고백만 두면 잔여가 falsifiable 하지 않다.

**B-4. 정직 상한 (over-claim 0)**: B-1~B-3 은 **저작 규율**이다. 저작 시점에 문면을 대상으로 도는 lint 는 부재하고(Story Z-11), 정적 검사는 착지 후 CI 에서만 돌며 그마저 merge 무차단(§A4-6-3)이다. 따라서 본 절은 자기적용 실패를 **차단하지 않는다** — 누락을 **가시화**할 뿐이며 표를 부실하게 채우면 그대로 빠져나간다. 실 backstop 은 리뷰 lane 의 대조이고, 위 4회전 결함을 잡아낸 것도 정확히 그 경로다. "자기적용 봉인" · "기계 강제" 주장을 금지한다.

### Cross-references

- [ADR-144](ADR-144-orchestrator-autonomy-stop-taxonomy.md) §결정 1(3축 배정규칙) · §결정 2(discriminant — anchor SSOT, 무손상) · §결정 3(priming scope, 신규 hook 금지) · §결정 7(정직 상한).
- [ADR-109](ADR-109-in-process-429-mitigation-framework.md) Amendment 2 — `limit-signal-halt` 의 신호 판정(판별식 D · 4치 출력). 본 amendment = 정지 적법성 축, ADR-109 = 판정 축(disjoint).
- [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 8 — A6-3(a) 후단 재개봉(규범 공백을 만든 표면 제거).
- §결정 6 whitelist 5종 / [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) §결정 20 ask-trigger 3종 — **무변경**(over-suppression 방어 carve-out).
- `docs/inter-plugin-contracts/stop-event-v1.md` §3.4/§5.1 — reason_class 4-enum · `policy_violation_rate_limit_induced` 재사용(계약 무변경).
