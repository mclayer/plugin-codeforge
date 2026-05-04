---
adr_number: 25
title: Stop discipline — non-whitelist stops as policy violation (Sonnet-decides ≠ user-confirms)
status: Accepted
category: Team & Process
date: 2026-05-03
carrier_story: CFP-73
related_files:
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/inter-plugin-contracts/stop-event-v1.md
  - CLAUDE.md
related_stories:
  - CFP-73
supersedes: null
superseded_by: null
---

# ADR-025: Stop discipline — Sonnet-decides ≠ user-confirms

## 상태

Accepted (2026-05-03). ADR-022 amendment carrier — ADR-022 §결정 11 Phase 1 trust model boundary 명확화.

## 컨텍스트

ADR-022 (CFP-61, 2026-05-02) 가 Sonnet decider 자동 진행 + 5 종 user escalation whitelist 정의. Phase 1 trust model 이 hook / refusal logic 없음 명시.

데뷔 운영 (mctrader 15 Story / codeforge dogfood ~67 Story, 2026-05-02 ~ 05-03) 에서 사용자 호소: "phase 상 사용자 stop 너무 많아 생산성 저하". Codex audit (gpt-5.5 high, 2026-05-03) 진단: "ADR-022 can be misread as requiring user confirmation after Sonnet decisions" — trust model 의 trust 가 "Sonnet pick → 자동 진행" 이지 "Sonnet pick → user confirm" 아님이 ADR-022 본문에 명시 부재.

Story §12 Sonnet Decision Log row 0건, mctrader 데뷔-audit feedback Issues 0건 — 측정 채널 부재가 Phase 2 transition (30+ packet) 자체를 unreachable 로 만드는 secondary problem 확인.

## 결정

### 결정 1 — Trust model invariant 명시

ADR-022 적용 시 invariant: **"Sonnet decides" implies "Orchestrator proceeds without user confirmation".** Sonnet decider 가 PASS / FIX / pick 응답 후 Orchestrator 가 사용자에게 "진행할까요?" / "이대로 가도 됩니까?" 묻는 것은 5 종 whitelist 미발화 시 **policy violation (defect)**.

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

## 관련 파일

- `docs/adr/ADR-022-sonnet-review-verdict-decider.md`
- `docs/inter-plugin-contracts/stop-event-v1.md` (Phase 2 sibling)
- `CLAUDE.md`

## Amendment 1 (CFP-80 — 2026-05-04): Epic / 작업 단위 continuity directive

### 동기

ADR-025 §결정 1 trust model invariant 명시 후에도 Orchestrator session 의 actual behavior = 작업 단위 안 sub-phase / sub-CFP 마다 stop 패턴 반복. 사용자 명시 (2026-05-04): "하나의 Epic 이 전체 phase 를 모두 따르고 그 과정과 결과를 한번에 밝혀야 하는데 phase 단위로 자꾸 끊어댄다."

본 amendment = §결정 1 trust model 의 stricter application — Orchestrator 가 **단일 Sonnet pick** 자동 진행에서 그치지 않고, **사용자 의도 단위 (Epic / backlog / Story)** 안의 모든 sub-decision / sub-CFP 까지 자동 통과 + 1번 final report 의무 명시.

### 결정 5 — Orchestrator 작업 단위 continuity 의무

사용자 메시지 받은 시점 = 작업 단위 식별:

| 사용자 메시지 패턴 | 작업 단위 | Continuity 의무 |
|---|---|---|
| "다음 작업 있나" + 1+ 후보 존재 | 모든 후보 / backlog 처리 단위 | backlog 모든 issue / CFP 자동 통과 + 1번 final report |
| "X 진행" (X = Epic 명시) | Epic 의 7 phase + 모든 child Story | child Story 모두 Phase 1 + Phase 2 PR cycle 자동 통과 + 1번 final report |
| "X 진행" (X = Story 명시) | Story 의 Phase 1 + Phase 2 PR cycle | 양 PR cycle 자동 통과 + 1번 final report |
| 명시 선택 ("a" / "C" / "ok" / "진행하자") | 직전 메시지의 후보 또는 진행 path | path 끝까지 자동 진행 |
| 정보 요청 ("X 보여달라" / "X 가 뭐냐") | 정보 답변 단위 | 답변 + stop 없음 (작업 진행 없음) |

작업 단위 안에서 발생하는 모든 sub-decision = ADR-022 trigger 5종 자동 처리 + Sonnet pick 적용. 본 sub-decision 마다 사용자 confirm 받음 = **policy violation (defect)** — §결정 2 와 동일 분류.

### 결정 6 — 합법 stop whitelist (5종 strict)

§결정 1 trust model invariant 와 정합. ADR-022 §결정 2 escalation whitelist 의 strict 적용:

1. **User environment 변경 의무** (PAT 발급 / API key / 외부 서비스 가입 / KRW 입금 / 1Password setup 등) — 사용자 직접 작업 의무
2. **Destructive action 직전** (force push / DB drop / 설정 영구 변경 / live-real first trade) — 단 sub-decision 까지 stop 안 함
3. **진정 unprecedented / unscoped 영역** (새 organizational decision, brainstorming skill default)
4. **Codex+Sonnet decider 의 escalation 결정** (decision-packet `decider_decision.escalation_required=true`)
5. **작업 단위 완료 후 final report** (1번)

위 5종 외 모든 stop = defect 분류. stop-event-v1 ledger `reason_class: policy_violation` 기록.

### 결정 7 — 불법 stop 패턴 명시 (반드시 회피)

| Pattern | Defect 사유 |
|---|---|
| "후보 A/B/C/D 중 어떤거?" | Codex+Sonnet 자동 처리 의무 (sub-decision) |
| "큰 작업이라 확인 받겠습니다" | token cost 추정 = 사용자 의도 아님 |
| "Phase 1 완료, Phase 2 시작할까요?" | 1 Story / Epic 안의 sub-step (decision unit 분리 violation) |
| "5 sub-CFP 중 첫 번째 완료, 다음 진행할까요?" | backlog 단위면 5 모두 처리 |
| "final report 후 다음 작업 후보 결정 받음" | backlog 안 끝났으면 자동 발굴 + 진행 |

### 결정 8 — Result 보고 형식 (1번)

- 작업 단위 전체 완료 후 1번 final report
- Sub-step 별 완료 시각 / 소요 시간 / Sonnet pick / override marker 포함
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
