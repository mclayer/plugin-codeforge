---
kind: concept_definition
type: domain-knowledge
slug: clarification-driven-reinvestigation
title: Clarification-driven reinvestigation — scope 정교화 (forward) ↔ 품질 게이트 회귀 (backward) 의미 분리 + value-equality skip 비차용 + 4-layer disjoint
status: Active
updated: 2026-05-17
carrier_story: CFP-893
related_adrs:
  - ADR-077  # Clarification 강제 재조사 전파 정책 SSOT — 본 개념의 normative SSOT
  - ADR-076  # 선언적 reconciliation upgrade — stale 게이트 declarative reconciliation 재사용 anchor
  - ADR-067  # FIX ledger RESET — §10 FIX Ledger 와의 cross-pollinate 금지 disjoint hard constraint 선례
  - ADR-059  # debate-protocol-v1 — debate round counter (3 카운터 disjoint 일원), max-round 5 precedent
  - ADR-058  # ADR sunset criteria mandate — value-equality skip 비차용 invariant ratchet 차단 정합
  - ADR-052  # Codex proactive Touchpoint — trigger origin disjoint boundary (Touchpoint #4 divergence vs clarification answer)
related_stories:
  - CFP-759  # Epic A Story-1 — ADR-077 신설 carrier (concept declared-but-absent 의 forward-pointer)
  - CFP-893  # 본 concept doc 물리 작성 carrier (Epic A close follow-up CFP)
tags:
  - clarification
  - reinvestigation
  - scope-refinement
  - value-equality-skip-non-adoption
  - 4-layer-disjoint
  - escalate-escape-valve
  - information-integrity
  - dirty-event
---

# Clarification-driven reinvestigation

## 정의

`clarification-driven reinvestigation` = **요구사항 단계에서 사용자가 clarification 질문에 답할 때마다, 판단 게이트 없이 강제로 재조사를 fan-out 하는 메커니즘**. 답변 = 입력 변경 = dirty 이벤트 = 무조건 전파.

본 개념은 ADR-077 §결정 1-10 의 narrative anchor — "왜 게이트를 두면 안 되는가" 와 "왜 4-layer disjoint 인가" 와 "왜 ESCALATE 가 failure 가 아닌가" 를 분리 가능한 단위로 정리한다.

## 컨텍스트

### 직접 동인

사용자 directive (Epic A #755 brainstorm 수렴 verbatim) — **"강제적으로 수행하라"**.

기존 메커니즘 ("PL 재량 + 변화없음 → 통합만") 의 손실:

- (a) **누락** — 설계가 변경 미반영 채 phase:설계 진입
- (b) **재발명** — 이미 결정된 것 재논의
- (c) **stale 설계 진입** — ArchitectAgent 가 outdated 조사로 설계

본 개념의 forcing function 정체 = 위 3 손실의 구조적 차단.

### 도메인 위치

본 개념은 **요구사항 레인의 dirty 이벤트 전파 메커니즘**. 요구사항 입력 (사용자 발화 / clarification 답변 / Epic 구조 변경) 의 변경이 후속 lane (설계 / 구현 / 리뷰) 에 전파되는 경로 SSOT.

비교 — 본 개념 vs 인접 패턴:

| 패턴 | trigger origin | 카운터 | 의미 |
|---|---|---|---|
| **clarification-driven reinvestigation** (본 개념) | user-answer-driven (사용자 clarification 답변) | 재조사 카운터 (scope 정교화 layer) | scope 정교화 (forward) |
| FIX iteration (ADR-067) | review lane FAIL (품질 게이트) | §10 FIX Ledger (품질 게이트 layer) | 게이트 회귀 (backward) |
| Touchpoint #4 RequirementsPL redo (ADR-052 Amendment 1) | Codex-divergence-driven (Touchpoint #4 divergence) | divergence iteration counter | divergence 합의 (lateral) |
| debate round (ADR-059) | DesignReview lane divergence | debate round counter (adversarial 합의 layer) | adversarial 합의 (lateral) |

4 패턴은 **trigger origin + 의미 + 카운터** 가 모두 disjoint. 동일 lane 에서 동시 발화 가능 — cross-pollinate 금지 (§4-layer disjoint normative invariant 참조).

## 핵심 규칙

### I-1: 무조건 트리거 (value-equality skip 비차용)

`clarification 답변 수령 = dirty 이벤트`. 판단 게이트 없이 강제 fan-out — 답변 내용이 이전과 의미상 동치 (value-equal) 여도 dirty 전파를 skip 하지 않는다.

**Why** — "값이 같으면 skip" 분기 도입 시:

1. 자기 모순 — clarification 답변이 들어왔다는 사실 자체가 입력 변경. "값이 같다" 판정이 이미 후행 조사 결과 (= 재조사 발동 후에야 알 수 있는 정보).
2. event-driven invalidation 위반 — multi-source 병합 환경 (DomainAgent / Analyst / Researcher 3 source) 에서 동일 입력이 source 별로 다른 의미 도달 가능. value-equality 가 source 1개에서 성립해도 다른 source 에선 의미 변동 가능.
3. **forward 의미 손상** — clarification answer 는 scope 정교화 (forward) 이지 게이트 회귀 (backward) 아님. forward 진행을 "변화없음" 으로 막는 것 자체가 도메인 정합 위반.

ADR-077 §결정 1 verbatim — "dirty 전파의 값 무관성 (value-independent) 은 normative invariant — `값이 같으면 skip` 분기를 ADR-077 정책에서 도입 금지".

### I-2: 4-layer disjoint normative

재조사 카운터는 4 측정 채널 중 하나의 **물리적으로 분리된 layer**:

| Layer | 카운터 | 상한 | 의미 |
|---|---|---|---|
| 1. scope 정교화 (forward) | 재조사 카운터 (§9.0 Clarification 재스폰 이력) | recheck_counter_cap = 5 | 정상 scope 정교화 |
| 2. 품질 게이트 (backward) | §10 FIX Ledger (Iter 합산) | lane별 max 3 | 게이트 회귀 |
| 3. PL재량 재스폰 (lateral) | playbook §4.4 2회 재스폰 한도 | 2 | PL재량 재실행 |
| 4. adversarial 합의 (lateral) | debate round counter | min 3 / max 5 | adversarial 합의 |

**cross-pollinate 금지** — 본 4 layer 간 카운터 합산·치환·skip-cascade 금지. **약화 방향 차단** (layer 합치 / cap 완화) = ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 정량 명시 의무.

**Why** — scope 정교화 (forward) ↔ 게이트 회귀 (backward) 의미 분리가 본 개념의 핵심. layer 합산 시 정상 scope 정교화가 품질 결함으로 오분류 → 사용자 directive ("정상적 scope 정교화 차단 아님") 위반.

ADR-076 §결정 4 "RESET disjoint layer invariant" (같은 단어가 다른 layer 에서 다른 의미 — Story progression vs upgrade transaction) 패턴의 N-layer 확장 재사용.

### I-3: ESCALATE escape valve (scope_redefinition_required, NOT failure / NOT abort)

`recheck_counter_cap = 5` 초과 시 ESCALATE 한다. ESCALATE 의미 = **"clarification 으로 요건이 계속 흔들림 → scope 자체를 재정의해야 함"** 의 의미 전환 (escape valve).

- `escalation_class: scope_redefinition_required`
- NOT `failure` / NOT `abort`
- §10 FIX Ledger 무기록 (4-layer disjoint 정합 — layer 1 의 한계 도달이 layer 2 기록으로 cross-pollinate 금지)
- ESCALATE 후 `recheck_counter` RESET to 0 (scope 재정의 후 새 baseline)

**Why** — escape valve 의미 보존이 안 되면 ESCALATE 가 정상 scope 정교화를 차단하는 역효과. 단순 abort 금지 normative.

**선례 (외부 anchor)** — ADR-059 §결정 4 (debate max round 후 사용자 escalation) escape valve 의미 보존 패턴 동형.

### I-4: 정보 무결성 invariant (fact-check marker 4종 verbatim 보존)

강제 재조사 시 `prior_output_ref` (이전 §2/§5/§6 산출) 의 fact-check marker 4종을 **verbatim 보존**한다.

- `[verified]` — direct fact check (Read / Grep / gh api / git show 등 ground-truth 확인 완료)
- `[hypothesis]` — 추론·해석 (검증 미완)
- `[fact-check-pending]` — 검증 필요 declare (TODO)
- `[user-input]` — 사용자 발화 verbatim

**보존 규칙**:

- 재조사 sub-agent 는 `[hypothesis]` / `[fact-check-pending]` 을 `[verified]` 로 **무검증 승격 금지**
- marker 부재 = 암묵 `[hypothesis]` default 유지 (ADR-052 Amendment 3 무손상)
- reverse-explicit `[verification-out-of-scope: <사유>]` marker 도 verbatim 보존

**Why** — 무결성 보존 위반 시 재조사 round 마다 fact-check 수준 inflation (`[hypothesis]` → `[verified]` 위조 승격) 발생 → 의사결정 품질 붕괴. 본 invariant 는 §결정 7 trigger origin disjoint 와 동일 영역 (SecurityArch codify).

### I-5: trigger origin disjoint

clarification 강제 재조사 trigger 와 다른 재실행 trigger 는 **trigger origin 단위로 disjoint**.

- clarification 강제 재조사 = **user-answer-driven** (사용자 clarification 답변 origin, 본 개념)
- ADR-052 Amendment 1 A4 RequirementsPL redo = **Codex-divergence-driven** (Touchpoint #4 divergence origin)
- 두 trigger 는 서로 다른 진입 — disjoint declare

**Why** — origin disjoint 가 4-layer counter disjoint (I-2) 의 measurement 표현. 동일 RequirementsPL 의 두 진입이 origin 단위로 분리되어야 카운터 cross-pollinate 차단.

## 메커니즘 요약 (ADR-077 §결정 cross-ref)

| 메커니즘 | normative anchor | invariant cross-ref |
|---|---|---|
| 무조건 트리거 + value-equality skip 비차용 | ADR-077 §결정 1 | I-1 |
| fan-out 6 permanent + 조건부 PMO | ADR-077 §결정 2 | (membership) |
| design-reading mandate 심화 (skim 금지) | ADR-077 §결정 3 | (depth) |
| 안전 envelope (debounce 90s + max-wait 600s + cap 5) | ADR-077 §결정 4 | (rate-limit) |
| 4-layer counter disjoint | ADR-077 §결정 5 | I-2 |
| ESCALATE escape valve (scope_redefinition_required) | ADR-077 §결정 6 | I-3 |
| trigger origin disjoint + 정보 무결성 invariant | ADR-077 §결정 7 | I-4 / I-5 |
| stale 게이트 (declarative reconciliation 재사용) | ADR-077 §결정 8 | (state) |
| ratchet (강화·비회귀 방향만) | ADR-077 §결정 9 | (governance) |
| parallel always-executable mandate | ADR-077 §결정 10 | (execution) |

## 경계

### vs `kst-display-invariant` (개념 layer-bounded 패턴)

본 개념과 `kst-display-invariant` 는 둘 다 **disjoint layer** 패턴이지만 적용 도메인 분리:

- `kst-display-invariant` = 시각 표기 (display layer) ↔ contract field (UTC strict) layer disjoint
- 본 개념 = 요구사항 재조사 카운터 (scope 정교화 layer) ↔ FIX Ledger (품질 게이트 layer) ↔ PL 재량 (lateral) ↔ debate (lateral) 4-layer disjoint

**공통 패턴** — layer-bounded 원칙 + cross-pollinate 금지 + 약화 방향 ADR-058 §결정 5 차단.

### vs FIX iteration (ADR-067)

| 차원 | clarification-driven reinvestigation | FIX iteration |
|---|---|---|
| trigger origin | user-answer-driven | review lane FAIL |
| 의미 방향 | forward (scope 정교화) | backward (게이트 회귀) |
| 카운터 layer | layer 1 (재조사 카운터) | layer 2 (§10 FIX Ledger) |
| 상한 | recheck_counter_cap = 5 | lane별 max 3 |
| 초과 시 | ESCALATE (scope_redefinition_required) | 사용자 RESET trigger |
| §10 기록 | 무기록 (disjoint) | 의무 기록 |

## 운영 시그널

본 개념이 정상 작동하는지의 mechanical 시그널:

- `adr-077-ratchet-declared` lint (Active, registry blocking-on-pr) — ratchet 방향 선언 존재 검증
- `adr-077-design-reading-mandate-declared` lint (Active) — skim 금지 + 의도/근거 파악 선언 검증
- `adr-077-integration` lint (warning, CFP-848 carrier + CFP-897 precision) — G-1..G-5 invariant
- 4-layer cross-declare 위치 3곳 — 본 §결정 5 + §결과 절 + `requirements-output-v1` contract schema (Story-4 = CFP-834)

위반 시 — Orchestrator strict-verify-gate (ADR-070) 가 적발하거나, IntegrationTestAgent Epic-level 검증이 ratchet 약화·layer 합산을 감지.

## 후속 영역 (본 doc scope 외)

- "범위를 바꾸는 답변" mechanical 판정 (단순 확인 / scope 정교화 / Epic 구조 변경 disambiguation) — ADR-077 P-4 위임 (설계 lane 후속 carrier)
- stale recovery 기준 mechanical 룰 — ADR-077 P-3 위임
- 재조사 fan-out wall-clock telemetry empirical baseline — ADR-077 P-1 deferred (Story-3 §8.3 Perf Baseline)
- generation schema (monotonic counter / per-section) — ADR-077 P-N 설계 lane 위임

## 관련 ADR

- [ADR-077](../../adr/ADR-077-clarification-forced-reinvestigation-propagation.md) — **본 개념의 normative SSOT** (§결정 1-10)
- [ADR-076](../../adr/ADR-076-declarative-reconciliation-upgrade.md) — declarative reconciliation 패턴 재사용 anchor (stale 게이트, §결정 8)
- [ADR-067](../../adr/ADR-067-fix-ledger-reset-rule.md) — §10 FIX Ledger cross-pollinate 금지 disjoint hard constraint 선례 (§결정 5)
- [ADR-059](../../adr/ADR-059-debate-protocol-v1.md) — debate round counter (3 카운터 disjoint 일원, max-round 5 precedent)
- [ADR-058](../../adr/ADR-058-adr-sunset-criteria-mandate.md) — value-equality skip 비차용 invariant ratchet 차단 정합 (§결정 5 sunset_justification)
- [ADR-052](../../adr/ADR-052-codex-proactive-check-touchpoints.md) — trigger origin disjoint boundary (Touchpoint #4 divergence vs clarification answer)

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-05-17 | 신규 작성 — ADR-077 §결정 1-10 narrative anchor 5 invariant codify | CFP-893 |

## verified-via (ADR-073)

- ADR-077 본문 §결정 1-10 verbatim (origin/main: `baaac665f94ef995652e6f55f44ae23c9e568ea5` — pinned 2026-05-17 KST)
- ADR-077 frontmatter `related_files` L37 — `docs/domain-knowledge/concept/clarification-driven-reinvestigation.md` (본 file path SSOT)
- Issue #893 verbatim scope statement
- Epic A 5 Story (CFP-759 / 778 / 785 / 834 / 848) carrier history — 4-layer disjoint 실 적용 사례
