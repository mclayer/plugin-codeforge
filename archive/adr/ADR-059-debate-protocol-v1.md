---
adr_number: 59
title: Multi-round Adversarial Debate Protocol (Codex ↔ Opus) — debate-protocol-v1
status: Proposed
category: orchestration
date: 2026-05-11
carrier_story: CFP-391
is_transitional: false
related_adrs:
  - ADR-044  # dispatch_mode enum 확장 대상 (Amendment carrier 동반)
  - ADR-052  # Codex proactive check touchpoints — touchpoint #4 격상은 Story 2 (CFP-392) scope
  - ADR-022  # Sonnet decider Deprecated context (CFP-134 / ADR-035 정합)
  - ADR-008  # inter-plugin contract versioning rule
  - ADR-010  # canonical/sibling sync 책임
  - ADR-039  # subagent default for codeforge modification work
  - ADR-031  # Lane-spawn evidence trail (§14 row schema 정합)
  - ADR-050  # parallel epic coordination (ADR-RESERVATION 절차 정합)
  - ADR-137  # blanket_refactor 소비 governance (Epic-close 구현-리팩터링 triage 3분기 + producer/consumer 분리, CFP-2541 Story C 실배선) — §결정11 엔진 계약 표면의 소비처
related_files:
  - docs/inter-plugin-contracts/debate-protocol-v1.md
  - docs/inter-plugin-contracts/fix-event-v1.md
  - docs/adr/ADR-044-phase-scoped-sequential-team.md
  - templates/team-spec-design-review.yaml
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - CLAUDE.md
amendment_log:
  - id: 1
    date: 2026-05-13
    carrier_story: CFP-533
    summary: "dispatch_mode enum 3-value 명시화 + mechanical_fast_path_inline 채널 신설. governance 강화 ratchet (ADR-064 active amendment 정합)."
  - id: 2
    date: 2026-05-13
    carrier_story: CFP-582
    summary: "DesignLane blanket trigger 신설 (모든 cross-module Story 자동 발동) + convergence_quality_invariant 신설 (3 marker pattern: [COUNTERARGUMENT] / [ALTERNATIVE_PROPOSED] / [DEBATE_PURPOSE_STATEMENT]) + Touchpoint #2 carry-over 의무. Epic-FIX-ESCALATION-prevention #525 close trigger."
  - id: 3
    date: 2026-07-01
    carrier_story: CFP-2534
    summary: "refactor lane (구현-리팩터링) consumer 추가 — trigger.lane enum + blanket_refactor dispatch_mode (divergence 감지 없이 자동 발동, cadence 미인코딩=Story C) + role_assignment optional 필드 (default null=대칭; refactor=codex proponent/claude opponent) + divergence_type structural 재사용. 기존 가드(anti-sycophancy 4 + convergence_quality_invariant 3-tuple + anchor-recurrence ≥2 + min3/max5) 전부 상속, 신규 정의 0. debate-protocol-v1 v1.2→v1.3 MINOR bump 동반. Epic CFP-2533 Story A (계약 표면만; producer/consumer 실배선 = Story C)."
amendments:
  - id: 1
    date: 2026-05-13
    carrier_story: CFP-533
    section_ref: "§결정 6 — dispatch_mode enum 명시화"
  - id: 2
    date: 2026-05-13
    carrier_story: CFP-582
    section_ref: "§결정 7~10 — DesignLane blanket + convergence_quality_invariant + Touchpoint #2 carry-over"
  - id: 3
    date: 2026-07-01
    carrier_story: CFP-2534
    section_ref: "§결정 11 — refactor lane consumer + blanket_refactor + role_assignment"
related_stories:
  - CFP-391  # carrier (5 결정 원본)
  - CFP-533  # Amendment 1 carrier (dispatch_mode enum 명시화)
  - CFP-582  # Amendment 2 carrier (Epic-FIX-ESCALATION-prevention #525 close)
  - CFP-2534  # Amendment 3 carrier (refactor lane consumer, Epic CFP-2533 Story A)
sunset_justification: "N/A — permanent policy + Amendment 1+2 = governance 강화 ratchet 누적 (ADR-058 §결정 5 + ADR-064 active amendment 정합). Amendment 2 가 Epic-FIX-ESCALATION-prevention #525 close trigger."
mechanical_enforcement_actions:
  - action_name: "debate-convergence-quality-lint"
    owner_adr: "ADR-060 Amendment 2"
    owner_section: "docs/evidence-checks-registry.yaml (warning tier entry, scripts/check_debate_convergence_quality.py)"
    status: "deferred — Phase 2 carrier (별도 CFP Story, mechanical script + workflow + registry row 신설 시점)"
    decision_binding: "§결정 8 (3 marker pattern + 3-tuple AND 검증)"
---

# ADR-059: Multi-round Adversarial Debate Protocol (debate-protocol-v1)

## 상태

Proposed (2026-05-11) — CFP-391 carrier.

## 컨텍스트

DesignReview lane 에서 Claude (Opus) 와 Codex (GPT-5) 두 워커는 lane-agnostic Adversarial 패턴(ADR-044 §결정 2)으로 정의되어 있으나, 현재 `dispatch_mode: user_request_only` 제약으로 사용자 explicit request 시에만 활성된다. review-verdict-v4 의 `worker_dialog_rounds` 필드는 라운드 카운트 측정만 제공할 뿐이며, 다음 두 요건은 미정의:

1. 두 워커가 동일 anchor 에 대해 finding 불일치 (severity OR recommendation) 를 산출했을 때 **자동으로 다중 라운드 토론으로 전환**하는 정책
2. 토론 누적 transcript 자체를 다음 라운드 입력 + ArchitectAgent re-run 입력에 캐리오버하여 **topic drift 차단 + reasoning carryover** 를 보장하는 forcing function

사용자가 다른 세션에서 Codex↔Opus 다중 라운드 토론을 실증해 단일 모델 단독 판정보다 결론 견고성이 높음을 확인했다 (평균 3~4 라운드 합의 도달). 본 ADR 은 그 사용자 실증을 codeforge 정책으로 구조화한다.

본 ADR 의 5 결정 외에 ADR-044 §결정 2 의 `dispatch_mode` enum 에 `auto_on_divergence` 값을 추가하는 Amendment 가 동반된다 (별도 ADR-044 Amendment commit).

## 결정

### 결정 1 — debate-protocol-v1 registry 신설 (lane-agnostic)

새 inter-plugin-contract `debate-protocol-v1` (kind:registry, wrapper-owned, lane-agnostic) 도입. 본 protocol 이 정의하는 사항:

- **트리거 surface**: lane 정보 + divergence_type + anchor_id + anchor_text
- **Context carryover 방식**: full transcript + topic anchor (Round 0 쟁점 원문 매 라운드 입력 최상단 prepend 강제)
- **라운드 정책**: min 3, soft default 4, max 5
- **종료 조건**: PL LLM 합의 판정 OR `AskUserQuestion` 사용자 escalation OR anchor 재발 즉시 escalation
- **Anti-sycophancy 메커니즘**: `remaining_disagreements` 필드 강제 + role_lock + 반대 입장 강제 유지 prompt + `POSITION_CHANGE` 라벨 의무
- **Transcript 영속화**: Story §9 inline append (`### Debate transcript: <anchor_id>` sub-section)

Schema 상세는 `docs/inter-plugin-contracts/debate-protocol-v1.md` SSOT. lane 정보를 인자로 받는 일반 schema 로 정의 — Story 2 (Requirements lane 확장, CFP-392) 에서 동일 registry 재사용 의무.

### 결정 2 — DesignReview lane 자동 발동 (Story 1 scope)

DesignReview lane 에서 다음 조건 만족 시 debate-protocol-v1 자동 발동:

- ClaudeReviewAgent 와 CodexReviewAgent 의 review-verdict-v4 `findings[]` 에서 동일 `anchor_id` 에 대해
- (a) 서로 다른 severity (P0/P1/P2) **OR**
- (b) 서로 다른 recommendation (FIX / FIX_DISCRETIONARY / PASS)
- (c) 한쪽만 발화 (silent side 처리는 (b) 의 특수 case — 한쪽 FIX, 다른쪽 silent = PASS 로 간주)

발동 책임: DesignReviewPLAgent (sibling sync to codeforge-review plugin `templates/review-pl-base.md`). divergence detection 은 review-verdict-v4 packet 합성 직전 surface 검사로 수행.

**dispatch_mode 우선순위 룰** (ADR-044 Amendment 본문 정합): `default > auto_on_divergence > user_request_only` — 두 mode 가 동시 활성 시 더 강한 쪽이 effective. `user_request_only` 단독 활성 (사용자가 explicit Codex request 안 함) 상태에서는 Codex worker 자체가 spawn 되지 않아 divergence 감지 불가 → debate 발동 안 함 (정합).

### 결정 3 — ArchitectAgent re-run reasoning carryover

debate FIX verdict 산출 시 다음 흐름 강제:

1. **transcript Story §9 inline append** — `### Debate transcript: <anchor_id>` sub-section (debate-protocol-v1 schema 준수)
2. **§10 FIX Ledger row append** — Orchestrator self-write (fix-event-v1 1.1 contract — `debate_artifact_ref` optional 필드 채움, Story §9 anchor link)
3. **ArchitectPLAgent re-spawn** — prompt 에 debate transcript 명시적 주입 (단순 verdict 전달 금지)
4. **ArchitectAgent re-run instruction** — "양측 입장의 reasoning trail 을 반영해 redesign" 명시. 양보 / 반박 / 핵심 disagreement 가 prompt 안에 verbatim 보존

이로써 단일 verdict 전달 시 발생하는 양측 reasoning trail 손실을 차단하고 redesign 품질을 향상시킨다.

### 결정 4 — 같은 anchor 재발 즉시 사용자 escalation

ArchitectAgent 수정 후 DesignReview 재진입 시 **동일 `anchor_id` 가 두 번째 debate 발동을 유발**하면 debate Round 진입 없이 즉시 `AskUserQuestion` 사용자 escalation.

- 검출 방식: DesignReviewPL 이 lane 진입 시 Story §9 scan → 동일 `anchor_id` 의 transcript section 수 카운트 → `anchor_recurrence_count >= 2` 검출 시
- 의미: AI 합의로 해결 불가능 시그널 (이전 debate 결론을 ArchitectAgent 가 적용했음에도 같은 쟁점이 재발) → 사용자 중재 진입
- 무한 루프 차단 forcing function

**anchor_id stable identifier 정의** (R7 결정): debate-protocol-v1 registry §"Anchor 정의" 에서 명시. 본 ADR 채택 정의 = **finding 의 `anchor_id` field (review-verdict-v4 schema 정의)** — 일반적으로 `<file>:<line>` 또는 `§<section-ref>` 형식. 동일 finding 객체가 두 워커에 의해 발화될 때 같은 `anchor_id` 사용 = review-verdict-v4 producer 책임. SHA256 hash 강제 안 함 (정합 단순화).

### 결정 5 — Lane-agnostic 설계 (Story 2 hard dependency 보장)

protocol contract 는 lane 정보를 인자로 받는 일반 schema 로 정의. Story 2 (Requirements lane 확장 — CFP-392) 에서 동일 protocol 재사용. lane-specific 트리거 조건만 추가 정의 (예: Requirements lane = semantic divergence — RequirementsPL LLM 판정).

- **registry 의 `trigger.lane` enum**: `design-review | requirements | code-review | security-test`
- **registry 의 `trigger.divergence_type` enum**: `severity | recommendation | semantic`
- Story 1 은 `design-review` + `severity|recommendation` 만 active. Story 2 가 `requirements` + `semantic` 추가. 미래 CFP 가 `code-review` / `security-test` 추가 가능.

duplicate registry 도입 금지 (anti-pattern). 본 결정으로 Story 2 가 본 Story merge 후 contract 신설 없이 trigger 조건만 추가 정의 가능.

### 결정 6 — dispatch_mode enum 명시화 (Amendment 1, CFP-533)

debate-protocol-v1 자체의 dispatch_mode 가 §결정 2 (DesignReview 자동 발동) 와 §결정 4 (anchor 재발 escalation) 사이 inline FIX 분기 영역이 명시되지 않아 inline judgment 가 가능한 single-file 영역에서도 표준 multi-round debate (min 3 라운드 × 2 worker × ~5K token) 의 token cost 가 발생하던 영역 정리.

본 Amendment 1 은 debate-protocol-v1 registry 의 `dispatch_mode` field 를 optional → required 로 전환 + 3-value enum 명시화. ADR-044 §결정 2 의 team-spec dispatch_mode (default / user_request_only / auto_on_divergence) 와 분리된 protocol-level dispatch_mode (auto_on_divergence / mechanical_fast_path_inline / user_request_only). 두 enum 은 다른 layer 영역 (ADR-044 = team roster level / ADR-059 = protocol activation level) — 동일 어휘 사용은 의미적 호환 보장 forcing function.

**3-value 표**:

| dispatch_mode | 진입 조건 | scope |
|---|---|---|
| `auto_on_divergence` | review-verdict-v4 `findings[]` 동일 `anchor_id` 에서 (a) 다른 severity 또는 (b) 다른 recommendation (FIX vs PASS) = `divergence_detected: true` | 표준 multi-round debate (min 3 / max 5 라운드). §결정 1-5 의 표준 흐름 발효 |
| `mechanical_fast_path_inline` | `divergence_detected: true` + single-file scope + severity ≤ critical | inline FIX 분기 (debate skip, PL inline 판정). transcript Story §9 append 면제, §10 FIX Ledger row append 의무 보존 (debate_artifact_ref = null) |
| `user_request_only` | consumer / user ad-hoc 명시 trigger | manual dispatch, 자동 발동 X. ADR-044 user_request_only Codex worker 가 활성된 상태에서도 protocol-level dispatch 는 사용자 explicit request 시에만 발동 |

**우선순위 룰** (두 mode 동시 활성 시 effective mode 결정):

```
auto_on_divergence  >  mechanical_fast_path_inline  >  user_request_only
```

- `mechanical_fast_path_inline` 진입 조건 (single-file + severity ≤ critical) 충족 못하면 `auto_on_divergence` 로 fallback (표준 debate 발동)
- `user_request_only` 단독 활성 (사용자 explicit request 안 함) 상태에서는 Codex worker 자체가 spawn 되지 않아 divergence 감지 불가 — protocol-level dispatch 미발동 (§결정 2 정합)

**`mechanical_fast_path_inline` 발동 결정 로직** (DesignReviewPL):

1. divergence detection 알고리즘 수행 (review-pl-base.md §3.0)
2. divergence_detected: true 시 추가 검증:
   - (a) single-file scope: divergence anchor 가 단일 file path 만 포함
   - (b) severity ≤ critical: 모든 divergence anchor 의 severity ≤ P1 (P0 critical 영역은 표준 debate 의무)
3. (a) + (b) 모두 충족 → `mechanical_fast_path_inline` 진입 → PL inline 판정 + Story §10 row append (debate_artifact_ref = null)
4. 미충족 → `auto_on_divergence` fallback (표준 multi-round debate)

본 결정의 의도 = inline judgment 가 가능한 single-file 영역에서 표준 debate token cost 회피. ADR-064 active amendment 정합 (governance 강화 ratchet, scope 확장 — 약화 방향 아님). debate-protocol-v1 registry v1.0 → v1.1 MINOR bump 동반 (additive strengthening, ADR-008 §결정 2 정합).

### 결정 7 — DesignLane blanket trigger (Amendment 2, CFP-582)

DesignReview lane 의 `auto_on_divergence` (Amendment 1, CFP-391) 외에 **DesignLane internal (ArchitectPL + ArchitectAgent + 6 SubAgent)** 으로 debate-protocol-v1 적용 영역 확장. trigger condition = **모든 cross-module Story 자동 발동** (signal-driven `divergence_detected` 와 분리된 structural-driven trigger).

**cross-module Story 정의 (mechanical heuristic)**:
- `touched_top_level_paths >= 2` (file-path 기반) OR
- `touched_lanes >= 2` (의미 기반, lane evidence §14 row 기반)

OR-merge 로 false negative 차단. 단일 lane 또는 단일 top-level path Story = blanket 미발동 (기존 `auto_on_divergence` 만 적용).

**dispatch_mode 신규 enum value**: `blanket_cross_module_designlane` — debate-protocol-v1 v1.2 MINOR bump 으로 추가. 우선순위:
`blanket_cross_module_designlane > auto_on_divergence > mechanical_fast_path_inline > user_request_only`

ArchitectPLAgent spawn 시 Orchestrator 가 cross-module 판정 후 prompt 에 `invoke_blanket_debate: true` 명시 + Story §14 Lane Evidence `[debate-blanket-invoked:<reason>]` row append 의무.

**참여자 (participants[])**: ArchitectPLAgent (PL) + ArchitectAgent (chief author) + 활성 SubAgent 들 (mandate matrix 기반) + Codex worker (proactive check touchpoint #2 carry-over — §결정 9). binary fanout round-robin (Codex × SubAgent pair) 으로 schema breaking 회피.

**Exemption**: 없음. 사용자 directive 2026-05-13 "모든 cross-module Story" 충실. 후속 Amendment 시 escape hatch 도입 검토 (ADR-058 §결정 5 governance 강화 ratchet 정합 — 약화 방향 차단).

### 결정 8 — convergence_quality_invariant 신설 (Amendment 2, CFP-582)

debate transcript 의 **3 marker pattern** 의무 — `participants[]` 가 라운드 N 출력 시 section header 강제 포함:

| Marker | Round 영역 | Required | 의미 |
|---|---|---|---|
| `[COUNTERARGUMENT]` | Round 1+ 매 라운드 per worker | yes | 상대 입장에 대한 명시적 반응 = 반론 수용 |
| `[ALTERNATIVE_PROPOSED]` | debate cumulative ≥ 1 | yes | 대안 발의 — 합의 도달이 아닌 새 해법 제시 |
| `[DEBATE_PURPOSE_STATEMENT]` | Round 0 only | yes | 토론 목적 명문화 — Round 0 첫 발화 의무 |

**PL 검증 책무** (기존 §3.1 anti-sycophancy 4 메커니즘 확장):

5. 매 라운드 출력에서 3 marker section header 검증. 부재 시 invalid 처리 + 재발화 요청 (1회 한정) + 두 번째 부재 시 force_continue + adversarial prompt 재주입 ("debate 의 본질은 반론·대안 — 합의 도달 자체가 목적이 아니다").
6. `consensus_reached` verdict 발화 전 3-tuple AND 충족 검증: `counterargument_present == true` AND `alternative_proposed_count >= 1` AND `debate_purpose_statement_present == true`. 미충족 시 `consensus_reached` 차단 + `force_continue` 강제. (PL 검증 시 per-round scope = `counterargument_present_both_workers` / per-termination scope = `counterargument_present_all_rounds_both_workers` 변형 사용 — 동일 base name 의 scope suffix. registry §2.2 + §2.3 schema 정합.)

**Measurable signal**: debate-protocol-v1 v1.2 schema 의 `round.convergence_quality_invariant` block (Task 3 schema 정의).

**Story §9 transcript marker**: 위 검증 violation 시 transcript 에 `[convergence_invariant_violation]` marker 영속 기록 — 후속 ratchet (강화 방향 Amendment) 의 evidence 소스.

**Domain knowledge SSOT**: `docs/domain-knowledge/domain/agent-teams/convergence-quality-invariant.md` (Wave 4 Task 7 신규 page).

### 결정 9 — Touchpoint #2 (ADR-052 Amendment 4) carry-over 의무 (Amendment 2, CFP-582)

ArchitectAgent §3 mandatory Codex proactive check (ADR-052 Amendment 4 / CFP-532) 결과 P0/P1 finding 발견 시, DesignLane blanket debate Round 0 input 구성 시 Codex finding 을 `codex_initial_position` 에 verbatim forward 의무. 이중 spawn 회피 + reasoning carryover 정신 정합.

**Forward mapping**:
- Codex finding `statement` → `codex_initial_position.statement`
- Codex finding `rationale` → `codex_initial_position.rationale`
- Codex finding `severity` → `codex_initial_position.severity`
- Codex finding `recommendation` (`FIX` / `FIX_DISCRETIONARY`) → `codex_initial_position.recommendation`

**P2 finding 영역**: Story §10 deferred 기록만 (debate Round 0 forward 미적용). P0 + P1 만 carry-over.

**Touchpoint #2 미발동 케이스** (예: ArchitectAgent §3 작성 전 blanket trigger 발동): Codex worker 를 debate Round 0 시점에 ad-hoc spawn (codex:codex-rescue subagent) — 이중 spawn 회피 목적은 carry-over 우선이나 Touchpoint #2 자체가 없는 경우 fallback.

### 결정 10 — lane-agnostic registry 정합 (Amendment 2, CFP-582)

debate-protocol-v1 v1.2 schema 갱신은 lane-agnostic 정신 유지 (CFP-391 §결정 5 정합) — convergence_quality_invariant block + dispatch_mode 4번째 enum value (`blanket_cross_module_designlane`) 는 DesignLane blanket 외 미래 lane (CodeReview / SecurityTest 의 blanket 적용) 에도 재사용 가능한 일반 schema. lane-specific trigger 조건 (cross-module 판정 등) 만 lane plugin 측에 분리.

CodeReview / SecurityTest blanket invocation 도입 시 신규 ADR (Amendment X) — 본 §결정 10 의 schema reuse 의무로 별도 v-bump 면제 (additive lane enum 추가는 MINOR, schema 구조 변경 시에만 추가 MINOR — ADR-008 §결정 2 정합).

### 결정 11 — refactor lane (구현-리팩터링) consumer 추가 (Amendment 3, CFP-2534)

debate-protocol-v1 의 lane-agnostic 재사용성(§결정 5·10)을 실제로 소비해 **구현-리팩터링 전용 consumer(refactor lane)** 를 추가한다. 실제 머지된 코드를 대상으로 Codex(찬성·중복/재사용 발굴)와 Claude(반대·필요성 게이트)가 min 3 / max 5 라운드 적대 토론으로 리팩터링 지점을 도출하는 계약 표면을 연다.

**본 결정 = 계약 표면(contract surface)만.** producer/consumer 실 dispatch 배선 · Epic-close triage(now/defer/drop) · RefactorAgent 재편 · anti-recursion 실차단 · deferred-lifecycle 연동은 **Story B/C 소유** — 본 §결정 11 은 그 경계를 명시한다.

**ADR-137 cross-ref (Story C 실배선 종착)**: ADR-137 = 본 §결정 11 blanket_refactor 계약 표면의 **소비 governance** — Epic-close triage 3분기(now/defer/drop) + producer/consumer 실 dispatch 분리(PMOAgent = verdict judge / Orchestrator inline = debate dispatch, ADR-039 §결정18 재귀 가드) + drop-ledger anchor-recurrence(≥2 escalation) + deferred-lifecycle 연동을 CFP-2541 Story C 에서 실배선했다. §결정 11 = 엔진 계약 표면 / ADR-137 = 그 위 소비 governance (decision domain 분리).

**(1) refactor lane enum 추가**: registry `trigger.lane` enum 에 `refactor` 를 additive 추가. v1.2→v1.3 MINOR (ADR-008 §결정 2 additive lane enum = MINOR, §결정 10 정합).

**(2) blanket_refactor dispatch_mode — invocation semantics 만**: `dispatch_mode` enum 에 `blanket_refactor` 를 additive 추가. 이 값은 **발동 방식(activation-manner)만** 인코딩한다 — `divergence_detected` 신호를 계산하지 않고 무조건 debate 를 켠다 (CFP-582 `blanket_cross_module_designlane` 동형: 리팩터는 "찬성↔반대" 대립이 도메인 본질). 

  - **cadence(발동 주기)는 인코딩하지 않는다**: "Epic-close 1회 배치" vs "매 Story" 같은 주기는 producer 가 언제 trigger schema 를 작성하는지의 문제 = **Story C 배선**. dispatch_mode 정의에 cadence 어휘를 넣지 않는다. (경계 forcing function: "매 Story blanket" 이 schema 로 새어들면 안 된다.)
  - **signal block 불요**: `blanket_cross_module_designlane` 는 `cross_module_signal`(touched_paths/lanes 수치)을 required 로 갖지만, `blanket_refactor` 는 무조건 발동이라 수치 신호가 없다 → 유사 signal block 을 두지 않는다(dead surface 회피).
  - **우선순위 위치 (SSOT = §결정 7)**: 정본 우선순위 사슬은 §결정 7 이 SSOT. `blanket_refactor` 는 blanket 군에 total-order 로 삽입 = `blanket_cross_module_designlane > blanket_refactor > auto_on_divergence > mechanical_fast_path_inline > user_request_only`. 두 blanket 은 lane-disjoint(설계 lane vs refactor lane)라 실질 충돌 없으나 total-order 결정론 보장.

**(3) role_assignment — 신규 optional 필드 (대칭 슬롯 재해석 금지)**: Codex=proponent(찬성)/Claude=opponent(반대) 방향배정을 **신규 optional 필드** `role_assignment: {claude, codex} | null` (값 enum proponent|opponent, default null=대칭=기존 동작)로 인코딩. 기존 `claude_initial_position`/`codex_initial_position` **대칭 슬롯을 "고정 방향" 으로 재해석하면 기존 필드 의미 변경 = MAJOR (ADR-008 §결정 3)** → 재해석 금지. 신규 optional 필드 = MINOR (ADR-008 §결정 2). 

  - **role_lock 과 orthogonal**: role_lock = "Round 0 입장(position) fixed" = 입장 안정성 / role_assignment = "어느 워커가 찬성·반대 편(direction)" = 초기 편 배정. role_assignment 는 role_lock 을 복제하지 않는다("direction, not position").
  - refactor lane = `role_assignment: {codex: proponent, claude: opponent}`.

**(4) divergence_type = `structural` 재사용**: refactor lane 은 신규 divergence_type 값을 추가하지 않고 기존 `structural` 을 재사용한다. registry §2.1 "lane-specific divergence_type 정의" list 의 per-lane keying 이 의미를 확정: *"structural (refactor) = 실제 머지 코드의 중복·재사용 divergence, `<file>:<line>` anchor"* (DesignLane structural = 설계 산출물 / Refactor structural = 실코드 중복·재사용, per-lane 구분). 신규 값(`duplication`/`reusability`)도 additive MINOR 이나, schema 최소화 + CFP-582 선례 일치 + per-lane keying 이 이미 disambiguation 제공 → 재사용 채택.

**(5) 가드 상속 — 신규 정의 0**: trigger schema 표면만 확장하고 round(§2.2)/termination(§2.3) schema 를 무변경으로 두어 다음을 **전부 상속**한다 — anti-sycophancy 4종 + convergence_quality_invariant 3-tuple(`counterargument_present` AND `alternative_proposed_count>=1` AND `debate_purpose_statement_present`) + anchor-recurrence ≥2 즉시 escalation + min 3 / max 5 라운드. 이들 중 **어느 것도 refactor 전용으로 재정의하지 않는다**. domain page `convergence-quality-invariant.md` 의 lateral expansion 의무가 refactor lane 을 자동 포섭(신규 domain page write 불요).

**(6) Touchpoint #2 carry-over 상호작용**: Codex=proponent role 은 §결정 9 Touchpoint #2 carry-over(Codex proactive check finding → `codex_initial_position` verbatim forward)와 `codex_initial_position` 슬롯을 공유한다. 두 메커니즘은 **orthogonal** — carry-over 는 finding 원문을 방향과 무관하게 forward 하고, proponent 방향은 별개 role_assignment 필드로 표현된다. 충돌 없음.

**(7) ADR-044 team-spec layer 무변경**: ADR-044 team-spec layer dispatch_mode(default/user_request_only/auto_on_divergence)는 protocol layer 와 의도적으로 분리된 다른 layer(§결정 6). `blanket_refactor` 는 protocol layer 에만 추가 → team-spec layer 무변경. 두 layer 어휘 의미 호환 유지.

**(8) producer/consumer 예약**: registry producers/consumers frontmatter 에 refactor lane entry 를 "Story C 배선 예정" placeholder reservation 으로 추가 — dangling 방지(계약↔결정 양방향 링크)하되 실 dispatch 는 열지 않는다(Story C 소유).

**SemVer**: debate-protocol-v1 v1.2 → v1.3 MINOR bump. 기존 lane 5값·dispatch_mode 4값·divergence_type 4값·position 슬롯 의미 변경 0 (순수 additive strengthening, ADR-008 §결정 2/§결정 10). Story A scope = 계약 표면; Story B(RefactorAgent 재편) / Story C(triage·producer/consumer 실배선·anti-recursion·deferred-lifecycle) 는 별 Story.

## 해소 기준

N/A — permanent policy

## 결과

- **편향 축소**: Codex↔Opus 다중 라운드 합의로 단일 모델 편향 축소. 근거 선행연구(Du et al. 2023 = arXiv 2305.14325 / Liang et al. 2023 = arXiv 2305.19118)는 **일반 추론·번역·산술** debate 에서의 편향 축소를 실증한 것으로, **구현 리팩터링(코드 중복·재사용 판단)으로의 전이는 약한 확장 가정**이다 (refactoring 특정 유효성은 별도 실증 미확보). 코드 도메인 debate 는 일관성이 낮다는 보고도 있으며(MAD, arXiv 2503.12029), 코드 도메인 최근접 prior-art anchor = PD³ (arXiv 2505.17492, project/code duplication 에 adapted multi-agent debate 적용 — 단 협력형). — Story §6.1 / requirements-review lane 검증(CFP-2534 §9)
- **drift 차단**: topic anchor 매 라운드 prepend 로 U-shaped attention bias 완화 (Liu et al. 2023 "Lost in the Middle" 정합 — Story §6.2)
- **reasoning carryover**: ArchitectAgent re-run 시 양측 reasoning 보존 → FIX 품질 향상
- **사용자 escalation 경로 명시**: AI 합의 불가능 시그널 (max 5 미합의 + anchor 재발) 처리 형식화
- **lane-agnostic 재사용성**: Story 2 (Requirements) + 미래 CFP 가 contract 신설 없이 trigger 조건만 추가
- **operational risk**: token budget cap (max 5 라운드 × 2 worker × ~5K token = ~50K) + AskUserQuestion escalation 으로 비용 폭증 차단 (Story §4.2 R11)

## 거절된 대안

- **(A) Rolling summary 모드 채택**: token 절약은 크나 미묘한 reasoning trail 손실 위험 — full transcript v1 채택. rolling summary 는 deferred CFP-D (5+ 라운드 비용 cap 시도 시점)
- **(B) Semantic similarity 기반 divergence 정의 (DesignReview scope)**: review-verdict-v4 schema 가 `anchor_id` + `severity` + `recommendation` 으로 충분히 명확 — fuzzy logic 도입 불필요. semantic 은 Requirements scope 만 (Story 2)
- **(C) PL 외 별도 judge agent 신설**: ChatEval (Chan et al. 2023) 정합 — 기존 PL 책무 강화로 충분. 신규 agent 도입 시 codeforge 의 6 lane plugin 구조 복잡도 증가
- **(D) min 5 / max 7 라운드 정책**: min 3 / max 5 채택 (값 유지). 근거 정정(CFP-2534 §9 다출처 검증) — Du et al.(arXiv 2305.14325)은 약 **4 라운드 plateau**를 보고하며, "5 라운드 saturation" 은 Du/Liang 이 아니라 **Ye et al. 2024(MCTS)** 귀속이다. max 5 cap 근거 = over-debating noise(4-5 라운드 diminishing/negative returns, kappa 하락) + 세션 실증 3~4 라운드 합의(2025 literature review = arXiv 2506.00066). min 3 / max 5 수치 자체는 변경하지 않음(pin).
- **(E) `auto_on_divergence` 를 user opt-in flag 로 노출**: consumer overlay 정책 축소 불허 invariant 정합 — debate 자동 발동은 강제. opt-out 은 별도 CFP carrier 도입 시점에 검토 (Story §5.3 Non-goal)

## 관련 파일

- [ADR-044](ADR-044-phase-scoped-sequential-team.md) — Amendment (dispatch_mode enum 확장)
- [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) — Story 2 (CFP-392) 진입 시 touchpoint #4 격상 Amendment 대상
- [debate-protocol-v1 registry](../inter-plugin-contracts/debate-protocol-v1.md) — schema SSOT
- [fix-event-v1 1.1](../inter-plugin-contracts/fix-event-v1.md) — `debate_artifact_ref` optional 필드 MINOR bump
- [Story CFP-391](https://github.com/mclayer/plugin-codeforge/issues/391) — carrier
