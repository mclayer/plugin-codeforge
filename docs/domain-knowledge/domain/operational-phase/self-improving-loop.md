---
kind: domain_fact
type: domain-knowledge
area: operational-phase
topic_slug: self-improving-loop
title: 운영 phase self-improving loop — 신호 환류 회로 + 무한 발산 위험 식별
status: Active
tags:
  - operational-phase
  - self-improving-loop
  - loop-closure-gate
  - pmo-escalation
  - auto-issue
  - cfp-1190
related_adrs:
  - ADR-104  # normative SSOT — §결정 5 (self-improving loop narrative + loop closure gate 위험 식별 + S6 carrier forward-ref)
  - ADR-045  # §D-9 cross-Story pattern_count ≥ 2 → ADR escalation forcing function — loop 답습 source
related_stories:
  - CFP-1190  # 본 carrier (loop 개념 정의 + 위험 식별 — closure mechanism 은 S6)
  - CFP-1187  # umbrella Epic
created: 2026-05-22
updated: 2026-05-22
---

# 운영 phase self-improving loop

> **normative SSOT**: [`docs/adr/ADR-104-operational-phase-definition.md`](../../../adr/ADR-104-operational-phase-definition.md). 본 파일은 ADR-104 §결정 5 의 서술적 elaboration 이다.

> **범위 boundary**: loop 개념 정의 + 무한 발산 위험 식별 만. 실 loop closure mechanism (dedup / max-depth / 사용자 gate) = **S6 carrier** (ADR-104 §결정 5 anti-scope 명시).

## 정의

**self-improving loop** = 운영 신호가 codeforge 의 다음 작업거리로 환류되는 회로 (ADR-104 §결정 5):

```
[운영 신호 회수]
    에러율 급증 / latency burn rate 임계 초과
    / regression 감지 / smoke FAIL
       ↓
[자동 Issue 생성]
    GitHub Issue — "운영 신호: <신호명> 임계 초과 (자동 생성)"
       ↓
[PMOAgent escalation]
    ops-signal Issue 감지 → retro pattern 분류
    → pattern_count ≥ 2 → ADR escalation forcing function 발동
       ↓
[다음 Epic 후보]
    PMOAgent 발의 → 사용자 확인 후 Epic 개시
```

이 회로는 ADR-045 §D-9 (cross-Story pattern_count ≥ 2 → ADR escalation forcing function) 패턴의 **운영 도메인 확장**이다.

## 컨텍스트

### ADR-045 §D-9 패턴 답습

ADR-045 §D-9 정의:

> "PMOAgent retro corpus enumeration cross-Story pattern_count ≥ threshold 2 검출 시 ADR escalation forcing function + escalation_action 2-value `adr_draft_emitted | escalate_user`"

self-improving loop 는 이 패턴을 운영 도메인으로 확장한다:

| 항목 | ADR-045 retro pattern | self-improving loop |
|---|---|---|
| 트리거 | Story 완료 후 PMOAgent retro | 운영 신호 임계 초과 |
| 감지 주체 | PMOAgent (retro mandatory trigger) | cron workflow → 자동 Issue → PMOAgent |
| 집계 기준 | cross-Story pattern_count ≥ 2 | 동일 신호 유형 pattern_count ≥ 2 |
| 반응 | ADR escalation forcing function | Epic 후보 발의 + 사용자 확인 |
| 사람 게이트 | 있음 | **있음 (사용자 확인 필수)** |
| 무한 loop 위험 | 낮음 | **있음 — §핵심 규칙 참조** |

두 패턴의 핵심 공통점: **자동 감지 → escalation → 인간 확인 게이트**. 완전 자동화로 Epic 을 개시하지 않는다.

### loop 의 의도

운영 신호로부터 codeforge 가 스스로를 개선하는 회로 — 배포 후 발견된 실 문제가 다음 작업 우선순위에 반영된다. PMOAgent 가 자동 감지 → retro pattern 집계 → ADR 의무 발의 까지 이어지는 체계를 운영 도메인에도 적용한다.

## 핵심 규칙

### 회로 각 단계

**단계 1 — 운영 신호 회수**: `measurement-channel.md` 의 4종 신호 (에러율 / latency burn rate / regression / smoke·health) 중 임계 초과 또는 FAIL 발생. 측정 주체: consumer 측 cron workflow (S4 이후).

**단계 2 — 자동 Issue 생성**: 신호 임계 초과 시 GitHub Issue 자동 생성. 정량 우선 (ADR-064 모달 어휘 금지 정합) — Issue 본문에 측정값과 임계값을 수치로 기록.

**단계 3 — PMOAgent escalation**:
1. `ops-signal` label Issue 감지 + pattern_count 집계 (동일 신호 유형 누적 횟수)
2. pattern_count ≥ 2 → ADR-045 §D-9 forcing function 발동 → ADR 후보 발의
3. 운영 신호 Issue 를 Story 완료 retro 에 병합 기록

**단계 4 — 다음 Epic 후보**: PMOAgent 발의 → Orchestrator 가 사용자에게 보고 → 사용자 확인 → `codeforge:story-epic-flow-preflight` 로 Story/Epic flow 결정.

### 무한 발산 위험 (loop closure gate = S6 carrier)

**위험 패턴**:

```
운영 신호 → Issue → Epic → Story 구현 → 배포 → 새 운영 신호 → 새 Issue → 새 Epic → ...
```

퇴화 케이스:
- **동일 신호 반복** — 동일 root cause 에서 나오는 신호가 계속 임계를 초과하면서 매번 새 Epic 이 개시 (root cause 해소 없이 Issue 만 누적)
- **Issue 폭발** — 신호 임계가 너무 낮게 설정되면 짧은 시간에 다수 Issue 생성 (noise 과잉)
- **Epic 무한 중첩** — loop 가 다음 Epic 을 낳고, 그 Epic 의 배포가 다시 신호를 낳는 자기 증식

**위험 수준: 중간 (MEDIUM)** — 사용자 확인 게이트가 있지만, "진행해" 를 반복하면 실질적으로 무한 loop 에 동조하게 된다.

**본 파일 (S1) 은 위험을 식별만 한다**. 실 loop closure mechanism 구현 = **S6 carrier** (ADR-104 §결정 5 anti-scope):

S6 가 구현할 loop closure gate 예상 요소:
- **dedup gate** — 동일 신호 유형에 대해 open Issue 가 이미 존재하면 새 Issue 생성 억제
- **max-depth gate** — loop 깊이 카운터 (Issue → Epic → 배포 → 재신호 cycle 횟수 상한)
- **escalate_user gate** — max-depth 초과 시 자동 Issue 중단 + 사용자 ESCALATE (ADR-045 §D-9 `escalation_action: escalate_user` 패턴 답습)

S6 까지 loop closure gate 가 없는 동안, cron workflow 가 수동 throttle (예: 동일 신호 유형 주당 1건 상한) 로 과잉 생성을 방지한다 (S4~S5 임시 안전망).

## 경계

### 이 파일이 정의하는 것

- self-improving loop 회로 개념 정의 (ADR-104 §결정 5)
- ADR-045 §D-9 패턴과의 유사성 및 차이
- 무한 발산 위험 식별 (S6 필수화의 근거)

### 이 파일이 정의하지 않는 것 (후속 Story)

| 항목 | carrier |
|---|---|
| loop closure gate 실 구현 (dedup / max-depth / 사용자 gate) | **S6** |
| ops-signal Issue template 실 구현 | S4~S7 |
| PMOAgent ↔ 운영 신호 회로 실 wire | S3 |
| 자동 rollback 신호 임계 정량값 | S2 |

## 관련 ADR

- [ADR-104](../../../adr/ADR-104-operational-phase-definition.md) — **normative SSOT** (§결정 5 — self-improving loop + loop closure gate 위험 식별 + S6 carrier forward-ref)
- [ADR-045](../../../adr/ADR-045-story-retro-mandatory-trigger.md) — §D-9 cross-Story pattern_count ≥ 2 → ADR escalation forcing function (loop 답습 source)

## 변경 이력

| 버전 | 날짜 | 변경 내용 | carrier |
|---|---|---|---|
| v1.0 | 2026-05-22 | 신설 — self-improving loop narrative (CFP-1190 Phase 2) | CFP-1190 |
