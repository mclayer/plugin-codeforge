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
