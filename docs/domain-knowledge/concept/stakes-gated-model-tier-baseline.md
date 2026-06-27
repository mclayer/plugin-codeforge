---
kind: concept_definition
type: domain-knowledge
slug: stakes-gated-model-tier-baseline
title: Stakes-gated model tier — sonnet≥opus baseline 측정 protocol + opus 복원 trigger (F1 evidence-gate)
status: Active
updated: 2026-06-27
carrier_story: CFP-2432
related_adrs:
  - ADR-042  # Amendment 16 — Story-shape 조건부 model tier 정책 SSOT (본 protocol = AC-9 evidence-gate 의 실체) / Amendment 17 — DomainAgent financial-invariant-0 baseline 확장
  - ADR-058  # §결정5 — 약화 방향 sunset_justification evidence requirement (tier-flip 하향 evidence-gate)
  - ADR-057  # §결정3 — Codex 독립 review baseline 선례 (measurement) / §결정4 — opts.model fresh-spawn override
related_files:
  - archive/adr/ADR-042-agent-model-selection-policy.md  # Amendment 16/17 (정책 SSOT)
  - scripts/check-stakes-tier-gating.sh  # 4-AND + clamp 판정 SSOT (+ DomainAgent financial-invariant-0 predicate, Amd17)
  - docs/orchestrator-playbook.md  # §3.0.12a gating 배선
  - docs/domain-knowledge/domain/backtesting-discipline/financial-correctness-invariant-catalog.md  # DomainAgent baseline: catalog cross-ref 측정 입력 (Amd17)
---

# Stakes-gated model tier — baseline 측정 protocol + opus 복원 trigger

## 정의

**Stakes-gated model tier baseline protocol** = CFP-2432 / ADR-042 Amendment 16 의 F1 evidence-gate(AC-9) 실체. low-stakes shape 에서 InfraOperationalArchitectAgent 를 opus→sonnet 으로 tier-flip 하는 것은 **provisional** 이다 — sonnet 산출물 품질이 opus baseline 이상임을 측정하고, 미달 시 opus 로 복원한다. 약화 방향(reasoning depth 하향)의 ADR-058 §결정5 evidence requirement 를 충족하는 측정 loop 를 정의한다.

**CFP-2445 / ADR-042 Amendment 17 확장**: 동일 protocol 을 **DomainAgent** 의 financial-invariant-0 shape tier-flip 에도 적용한다 — 단 **측정 대상이 다르다**(InfraOpArch = §7.4 운영 리스크 표 완결성 / DomainAgent = 도메인 invariant 식별 완결성). 4-step protocol 골격(측정 대상 → opus baseline → 미달 임계 OR → 복원 trigger + marker)은 공유, agent별 측정 정의만 분기.

## 컨텍스트

왜 measurement 인가 (약화 방향 evidence-gate):

- tier-flip opus→sonnet = ratchet 약화 방향(reasoning depth 하향). ADR-058 §결정5 / ADR-064 §결정7 (is_transitional:false governance ADR 의 약화 방향 symmetric evidence-gate) 에 따라 **evidence requirement 발화**.
- ADR-057 §결정3 선례: 6 agent 의 Sonnet 적부를 **Codex 독립 review verdict** 로 판정 → CodebaseMapper/Refactor 등은 Sonnet 적정, 일부는 품질 미달 시 opus 복원(ADR-057 Amendment 3 selective rollback = degradation→restoration LOOP 의 실 사례).
- 본 protocol = 그 measurement baseline 선례(§결정3 / ADR-042 Amd4 본문)를 stakes-gated tier-flip 에 재사용.
  - **인용 정정**: F1 의 "ADR-057 Amd4" 는 mislabel — Amd4 = 버전핀→별칭(model 표기) 이고 measurement 선례가 아니다. 실제 measurement 선례 = **ADR-057 §결정3 / ADR-042 Amd4 본문**. degradation→restoration LOOP 선례 = **ADR-057 Amendment 3**(measurement 과 구분).

## 핵심 규칙

### 측정 protocol (4-step)

| step | 항목 | 정의 (정량 — 주관 어휘 금지) |
|---|---|---|
| (a) 측정 대상 | InfraOpArch §7.4 운영 리스크 표 완결성 | §7.4.1~.6 각 항목의 (판정 + 근거 + marker) 충족 행 수 (정수). low-stakes shape 에선 §7.4.1~.4 = "N/A 발화 + 사유" 충족 행, §7.4.5/.6 = "표준 hygiene 잔존" 충족 행 |
| (b) opus baseline 캡처 | 동일 Story 양 tier 대조 + Codex 독립 review | 1차 = Codex 독립 review verdict(ADR-057 §결정3 선례 재사용). 2차 = 동일 Story 를 opus / sonnet 양 tier 로 대조 spawn(packet 고정) 후 (a) 정량값 비교. baseline = opus 산출물의 (a) 값 |
| (c) "미달" 임계 (OR — binary, falsifiable) | sonnet 산출물이 baseline 미달인지 | ① §7.4 sub 누락 ≥ 1 (opus 가 작성했는데 sonnet 이 누락) **OR** ② Codex review P0/P1 finding ≥ 1 **OR** ③ sonnet 식별 항목 수 < opus × tolerance |
| (d) 복원 trigger | 미달 시 opus 복원 | (c) 1개라도 해당 시 해당 agent 를 opus 로 복원(spawn-time opts.model 제거) + sonnet 채택 시 commit/PR body `stakes-tier-evidence:` marker 의무(부재 시 FAIL — `check-tier-downgrade-guard.sh` justification marker gate 동형) |

### DomainAgent baseline 측정 정의 (CFP-2445 / ADR-042 Amendment 17)

InfraOpArch 의 §7.4 운영 리스크 표 완결성과 달리, DomainAgent 의 baseline 측정 대상 = **도메인 invariant 식별 완결성**. 4-step protocol 골격은 동일, 측정 정의만 분기:

| step | DomainAgent 측정 정의 (정량 — 주관 어휘 금지) |
|---|---|
| (a) 측정 대상 | financial-invariant-0 shape Story 에서 DomainAgent 산출의 **(catalog cross-ref 항목 수 + 도메인 제약·암묵 가정·지식 공백 식별 행 수)** 정수. catalog = `docs/domain-knowledge/domain/backtesting-discipline/financial-correctness-invariant-catalog.md`(INV-1~11) |
| (b) opus baseline 캡처 | 1차 = Codex 독립 review verdict(ADR-057 §결정3 선례). 2차 = 동일 Story 양 tier(opus/sonnet) 대조 spawn(packet 고정) 후 (a) 정량 비교. baseline = opus 산출물의 (a) 값 |
| (c) "미달" 임계 (OR — falsifiable) | ① catalog cross-ref 누락 ≥ 1(opus 가 인용했는데 sonnet 이 누락) **OR** ② Codex review P0/P1 finding ≥ 1 **OR** ③ sonnet 식별 항목 수 < opus × tolerance(초기 1.0) |
| (d) 복원 trigger | (c) 1개라도 해당 시 DomainAgent opus 복원(opts.model 제거) + sonnet 채택 시 commit/PR body **`financial-invariant-zero-evidence:`** marker 의무(부재 시 FAIL — `check-tier-downgrade-guard.sh` 동형) |

> **indirect real-funds risk 가드**: DomainAgent 누설 = 백테스트 결과 거짓 → 실자금 결정 오염이므로 fail-safe(불확실=opus) + financial-invariant-0 5-AND 전부 충족 요구 + evidence-gate 3중. InfraOpArch 의 `stakes-tier-evidence:` marker 와 별도 namespace(`financial-invariant-zero-evidence:`) — 두 tier-flip 의 KPI 분모 오염 차단.

### opus 복원 trigger (요약)

다음 중 **1개라도** 해당 시 InfraOperationalArchitectAgent(low-stakes shape) 또는 DomainAgent(financial-invariant-0 shape)를 opus 로 복원한다:

1. low-stakes sonnet 산출물의 §7.4 sub 누락 ≥ 1 (opus baseline 대비)
2. Codex 독립 review 가 sonnet 산출물에 P0 또는 P1 finding ≥ 1
3. sonnet 식별 항목 수 < opus baseline × tolerance (정량 미달)

복원 = 정책 자체 철회가 아니라 해당 shape/agent 의 tier-flip 만 되돌림. ADR-058 §결정5 의 "약화는 evidence 있으면 1급 허용, 없으면 차단" 의 evidence loop.

### tolerance / 측정 주기

- **tolerance** = 측정 첫 적용 시 lock-in(empirical-source TBD — consumer 실 적용 시 측정). 초기 보수값 = 1.0(opus 항목 수와 동일 이상 요구).
- **측정 주기** = tier-flip 채택 Story 단위(per-Story). 누적 미달 패턴(pattern_count ≥ 2) 시 PMOAgent 가 정책 재검토 발의(ADR-045 §D-9).

## 경계

- **perf baseline = N/A** — tier 선택은 산출물 품질 trade-off 이지 런타임 latency/throughput 경로가 아니다(ADR-042 Amd16 §8.4 정합). 본 protocol 은 품질 measurement 만 다룬다.
- **정책 철회 ≠ tier-flip 복원**: 복원 trigger 발화는 해당 shape/agent 의 tier-flip 만 되돌릴 뿐 stakes-gated tier 정책 자체를 무효화하지 않는다.
- **판정 SSOT 경계**: 4-AND shape 판정 + `max(floor,overlay)` clamp 는 `scripts/check-stakes-tier-gating.sh` 의 책임(본 protocol 의 입력 게이트). 본 문서는 그 입력으로 sonnet 이 결정된 후의 품질 evidence-gate 만 정의 — 두 영역 disjoint.

## 관련 ADR

- **ADR-042 Amendment 16** — Story-shape 조건부 model tier 정책 SSOT(InfraOpArch). 본 protocol = §F1 / AC-9 evidence-gate 의 실체. sunset_justification 약화 방향 evidence 3-axis(stakes-gated 정제 / falsifiable evidence-gate / 지배 low-stakes shape 비용효율).
- **ADR-042 Amendment 17** (CFP-2445) — DomainAgent financial-invariant-0 조건부 sonnet. 본 protocol DomainAgent baseline 확장(측정 대상 = 도메인 invariant 식별 완결성). catalog cross-ref 누락 = 미달 임계 ①. `financial-invariant-zero-evidence:` marker(별 namespace).
- **ADR-058 §결정5** — 약화 방향 sunset_justification evidence requirement (tier-flip 하향 evidence-gate 발화 근거).
- **ADR-064 §결정7** — is_transitional:false governance ADR 의 약화 방향 symmetric evidence-gate.
- **ADR-057 §결정3 / §결정4** — Codex 독립 review baseline measurement 선례(§결정3) + opts.model fresh-spawn override 메커니즘(§결정4). ADR-057 Amendment 3 = degradation→restoration LOOP 선례.
- 관련 파일: `scripts/check-stakes-tier-gating.sh`(4-AND + clamp 판정 SSOT) · `docs/orchestrator-playbook.md` §3.0.12a(gating 배선).

## 변경 이력

| 일자 (KST) | 변경 | carrier |
|---|---|---|
| 2026-06-27 | 신설 — sonnet≥opus baseline 측정 protocol(4-step) + opus 복원 trigger(3-임계 OR) + tolerance/주기 codify | CFP-2432 (ADR-042 Amendment 16 Phase 2) |
| 2026-06-28 | DomainAgent baseline 측정 정의 확장(측정 대상 = 도메인 invariant 식별 완결성, catalog cross-ref + 도메인 제약·암묵 가정·지식 공백 행 수) + `financial-invariant-zero-evidence:` marker(별 namespace) | CFP-2445 (ADR-042 Amendment 17 Phase 2) |
