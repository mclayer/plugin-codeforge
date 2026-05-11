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
related_files:
  - docs/inter-plugin-contracts/debate-protocol-v1.md
  - docs/inter-plugin-contracts/fix-event-v1.md
  - docs/adr/ADR-044-phase-scoped-sequential-team.md
  - templates/team-spec-design-review.yaml
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - CLAUDE.md
amendment_log: []
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

## 해소 기준

본 ADR 은 transitional 아님 — `is_transitional: false`. 영구 정책으로 작동.

## 결과

- **편향 축소**: Codex↔Opus 다중 라운드 합의로 단일 모델 편향 축소 (Du et al. 2023 / Liang et al. 2023 선행 연구 정합 — Story §6.1)
- **drift 차단**: topic anchor 매 라운드 prepend 로 U-shaped attention bias 완화 (Liu et al. 2023 "Lost in the Middle" 정합 — Story §6.2)
- **reasoning carryover**: ArchitectAgent re-run 시 양측 reasoning 보존 → FIX 품질 향상
- **사용자 escalation 경로 명시**: AI 합의 불가능 시그널 (max 5 미합의 + anchor 재발) 처리 형식화
- **lane-agnostic 재사용성**: Story 2 (Requirements) + 미래 CFP 가 contract 신설 없이 trigger 조건만 추가
- **operational risk**: token budget cap (max 5 라운드 × 2 worker × ~5K token = ~50K) + AskUserQuestion escalation 으로 비용 폭증 차단 (Story §4.2 R11)

## 거절된 대안

- **(A) Rolling summary 모드 채택**: token 절약은 크나 미묘한 reasoning trail 손실 위험 — full transcript v1 채택. rolling summary 는 deferred CFP-D (5+ 라운드 비용 cap 시도 시점)
- **(B) Semantic similarity 기반 divergence 정의 (DesignReview scope)**: review-verdict-v4 schema 가 `anchor_id` + `severity` + `recommendation` 으로 충분히 명확 — fuzzy logic 도입 불필요. semantic 은 Requirements scope 만 (Story 2)
- **(C) PL 외 별도 judge agent 신설**: ChatEval (Chan et al. 2023) 정합 — 기존 PL 책무 강화로 충분. 신규 agent 도입 시 codeforge 의 6 lane plugin 구조 복잡도 증가
- **(D) min 5 / max 7 라운드 정책**: 선행 연구 (Du / Liang) 모두 5 라운드 이후 saturated → 본 v1 min 3 / max 5 채택
- **(E) `auto_on_divergence` 를 user opt-in flag 로 노출**: consumer overlay 정책 축소 불허 invariant 정합 — debate 자동 발동은 강제. opt-out 은 별도 CFP carrier 도입 시점에 검토 (Story §5.3 Non-goal)

## 관련 파일

- [ADR-044](ADR-044-phase-scoped-sequential-team.md) — Amendment (dispatch_mode enum 확장)
- [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) — Story 2 (CFP-392) 진입 시 touchpoint #4 격상 Amendment 대상
- [debate-protocol-v1 registry](../inter-plugin-contracts/debate-protocol-v1.md) — schema SSOT
- [fix-event-v1 1.1](../inter-plugin-contracts/fix-event-v1.md) — `debate_artifact_ref` optional 필드 MINOR bump
- [Story CFP-391](https://github.com/mclayer/plugin-codeforge/issues/391) — carrier
