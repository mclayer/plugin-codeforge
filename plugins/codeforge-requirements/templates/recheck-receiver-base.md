# 재조사 수신부 공통 base (recheck-receiver-base)

요구사항 lane 7 agent (RequirementsPLAgent dispatcher 1 + worker 6) 가 공유하는 **강제 재조사 fan-out 수신 절차 · 정보 무결성 invariant · counter boundary semantics** 의 SSOT. 각 agent md 는 본 base 를 참조하고 gate 1줄 + per-agent delta (담당 섹션 / write-queue 경로 / 고유 sub-section) 만 inline 으로 유지한다.

- **참조 방식 = 참조-time 공통 base SSOT** (ADR-120 §결정 4 (b) — review-pl-base.md 동형). 본 base 를 참조하는 빌드/합성 스크립트 = 0건 의무 (참조-time only — doc-only fast-path 보존, ADR-054).
- **gate 명제 보존**: 본 base 는 spawn 시 자동 로드되지 않으므로, gate 명제 (무검증 승격 금지 / circuit open fail-closed / §9.0 직접 기록 금지) 는 각 agent 본문에 1줄 inline 잔존 의무 (ADR-120 §결정 4 corollary 공통 단서).

ADR 근거: ADR-077 §결정 4 (재조사 envelope 정량) · ADR-120 §결정 4 (b) (참조-time base SSOT) · ADR-077 Amendment 1 (why-왕복 counter = 5번째 disjoint measurement channel + 순수 확정 = terminal event).

---

## 1. Worker 공통 수신 절차 (5-step)

본 agent 가 강제 재조사 fan-out dispatch 수신 시:

1. 공통 입력 packet 신규 수령 (RequirementsPLAgent 가 coalesce 완료 후 단일 dispatch).
2. 담당 섹션 (`<per-agent delta — §3 표 참조>`) fresh 재작성. stale 마킹 해제 = RequirementsPL 영역.
3. **정보 무결성 invariant** (§2 본문) 적용.
4. §9.0 owner = RequirementsPL (`recheck_N | <본 agent 이름> | <triggering_answer_ref>` 행 append). 본 agent 직접 기록 금지.
5. 결과 write queue 제출 (`.claude-work/doc-queue/<story>/<seq>-story-section-<N>.md` — `<N>` = per-agent delta).

## 2. 정보 무결성 invariant (canonical 본문)

강제 재조사 fan-out 재스폰 시 수신한 `prior_output_ref` (이전 §2/§4.1/§4.2/§4.3/§5/§6 산출) 의 fact-check marker **5종** (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]` / `[verification-out-of-scope: <사유>]`) 을 **verbatim 보존**한다. `[hypothesis]` / `[fact-check-pending]` 을 `[verified]` 로 **무검증 승격 금지** — 직접 재검증 + evidence file:line 인용 시에만 승격 허용. marker 부재 = 암묵 `[hypothesis]` default 유지. reverse-explicit `[verification-out-of-scope: <사유>]` 사유 필드 verbatim 보존. **승격 비대칭**: lower → higher 무검증 금지 / higher → lower (`[verified]` → `[hypothesis]`) 강등 허용 (보수 안전 방향).

## 3. Counter boundary semantics (canonical 본문)

`recheck_counter == 5` = 5번째 정상 재조사 사이클. `recheck_counter` 가 6으로 증가 진입 = `cap 초과` = circuit open → ESCALATE (`escalation_class: scope_redefinition_required`, `recheck_counter` RESET to 0). 즉 5번째 재조사 = 정상 완료, 6번째 trigger 시점 = circuit open.

- **Worker 측 ESCALATE 수신 (counter boundary D4)**: `recheck_counter` 6 진입 = cap 초과 = circuit open. RequirementsPL 이 ESCALATE 판정 → worker 진행 중단 + 현 상태 그대로 partial 반환 (fail-closed).
- 재조사 envelope (debounce / max-wait / coalesce / recheck_counter_cap / max_total_recheck_spawns) 정량값 = **ADR-077 §결정 4 정량 표 SSOT cross-ref**. env=0 / env=1 정량 분기 표현 0건.
- **why-왕복 counter = 5번째 disjoint measurement channel (ADR-077 Amendment 1 결정 2)**: 요구사항 lane intake 왕복(why-왕복) counter 는 기존 4개 channel (재조사 카운터 / §10 FIX Ledger / playbook §4.4 재스폰 한도 / debate round counter) 와 **disjoint 한 5번째 measurement channel** 이다. `recheck_counter` cap **비소모** — 기존 cross-pollinate 금지 invariant 를 그대로 상속 (§10 FIX Ledger 합산 금지 포함). counter cap 정량값 = **ADR-077 §결정 4 정량 표 SSOT cross-ref** (본 base 재선언 0).
- **cross-namespace disambiguation (필수 — 오독 차단)**: 본 counter 는 ADR-071 §결정 3 cognitive Layer 1-4 와 **무관**하다 — **measurement channel ≠ cognitive layer**. "5번째 measurement channel" 이지 **5번째 cognitive layer 신설이 아니다** (ADR-071 §결정 3 "5번째 cognitive layer 신설 금지" invariant 와 무충돌 — 다른 namespace). 본 counter 는 "counter/measurement channel" 로 명명하고 cognitive "layer" 명명을 피한다.
- **terminal event 비소모 (ADR-077 Amendment 1 결정 1)**: 사용자 최종 확정 발화 = trigger origin `user-final-confirmation-driven`. **순수 확정(내용 무변경) = terminal event** — 재조사 fan-out 미발동 + counter 비소모 (요구 입력 변경 0 이므로 clarification 답변 class 밖 — §결정 1 value-equality skip 비차용 무손상). 내용 수정 동반 확정만 `user-answer-driven` origin 으로 §결정 1 무조건 fan-out 경로 (모호 시 default = fan-out, 안전 방향).

## 4. Per-agent delta 표 (wiring map)

| agent | 담당 섹션 | write-queue 파일 | 고유 sub-section (inline 잔존) |
|---|---|---|---|
| RequirementsPLAgent | dispatcher (fan-out 6 / 병렬 의무 / burst coalesce / PMO 합류 / stale 마킹 / why-왕복 counter 운용 — §3 5번째 channel) | — (PL = §9.0 owner) | dispatcher 본문 전체 inline |
| DomainAgent | §2 Domain | `<seq>-story-section-2.md` | — |
| ChangeImpactAgent | §4.1 ChangeImpact | `<seq>-story-section-4.1.md` | — |
| FeasibilityAgent | §4.2 Feasibility | `<seq>-story-section-4.2.md` | — |
| ContinuityAgent | §4.3 Continuity | `<seq>-story-section-4.3.md` | — |
| RequirementsAnalystAgent | §5 Analyst | `<seq>-story-section-5.md` | — |
| ResearcherAgent | §6 Researcher | `<seq>-story-section-6.md` | 외부 anchor 재검증 (신규 작성 금지 — `prior_output_ref` cross-ref only) |
