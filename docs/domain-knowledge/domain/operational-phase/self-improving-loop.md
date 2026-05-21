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
  - ADR-104  # normative SSOT — §결정 5 (self-improving loop narrative + loop closure gate 위험 식별)
  - ADR-045  # §D-9 cross-Story pattern_count ≥ 2 → ADR escalation forcing function — loop 답습 source
  - ADR-104  # §결정 5 "loop closure gate = S6 carrier" forward-ref
related_stories:
  - CFP-1190  # 본 carrier (loop 개념 정의 + 위험 식별 — closure mechanism 은 S6)
  - CFP-1187  # umbrella Epic
created: 2026-05-22
updated: 2026-05-22
---

# 운영 phase self-improving loop

> **normative SSOT**: [`docs/adr/ADR-104-operational-phase-definition.md`](../../../adr/ADR-104-operational-phase-definition.md). 본 파일은 ADR-104 §결정 5 의 서술적 elaboration 이다.

> **범위 boundary (본 파일)**: loop 개념 정의 + 무한 발산 위험 식별 만. 실 loop closure mechanism (dedup / max-depth / 사용자 gate) = **S6 carrier** (ADR-104 §결정 5 anti-scope 명시). 본 파일은 위험을 식별하고 S6 를 forward-ref 한다.

## §1. self-improving loop 회로

### 기본 회로

운영 phase 의 신호는 codeforge 의 다음 작업거리로 환류된다 (ADR-104 §결정 5):

```
[운영 신호 회수]
    에러율 급증 / latency burn rate 임계 초과
    / regression 감지 / smoke FAIL
       ↓
[자동 Issue 생성]
    GitHub Issue — "운영 신호: <신호명> 임계 초과 (자동 생성)"
    label: ops-signal, needs-triage
       ↓
[PMOAgent escalation]
    PMOAgent 가 ops-signal Issue 감지
    → retro pattern 으로 분류 (ADR-045 §D-9 pattern_count 집계)
    → pattern_count ≥ 2 → ADR escalation forcing function 발동
       ↓
[다음 Epic 후보]
    PMOAgent 가 Epic 후보 발의
    → Orchestrator 가 사용자에게 보고
    → 사용자 확인 후 Epic 개시 (story-epic-flow-preflight)
```

### ADR-045 §D-9 패턴 답습

ADR-045 §D-9 은 retro pattern 에 대해 다음을 정의한다:

> "PMOAgent retro corpus enumeration cross-Story pattern_count ≥ threshold 2 검출 시 ADR escalation forcing function"

self-improving loop 는 이 패턴을 운영 도메인으로 확장한다:
- **retro pattern** (ADR-045) = Story 완료 후 PMOAgent 가 cross-Story 패턴 발견 시 ADR 발의
- **self-improving loop** (ADR-104) = 운영 신호 pattern_count ≥ 2 시 PMOAgent 가 next Epic 후보 발의

두 패턴의 핵심 공통점: **자동 감지 → escalation → 인간 확인 게이트**. 운영 phase 도 retro 도, 완전 자동화로 Epic 을 개시하지 않고 사용자 확인을 거친다.

## §2. 회로 각 단계 상세

### 단계 1 — 운영 신호 회수

`measurement-channel.md §2` 의 4종 신호 (에러율 / latency burn rate / regression / smoke·health) 중 임계 초과 또는 FAIL 발생.

측정 주체: consumer 측 cron workflow (S4 이후 신설, filesystem/cron 기반 — 0 API call constraint 정합).

### 단계 2 — 자동 Issue 생성

신호 임계 초과 시 GitHub Issue 자동 생성. Issue 형식 (선언, 실 template = S4~S7 carrier):

```
제목: [ops-signal] <신호명> 임계 초과 — <KST 타임스탬프>
본문:
  - 신호 유형: <에러율 / latency burn rate / regression / smoke-fail>
  - 측정값: <정량값> (임계: <정량값>)
  - 발생 시각: <YYYY-MM-DDTHH:MM:SS+09:00>
  - 측정 환경: <consumer repo>
label: ops-signal, needs-triage
```

정량 우선 (ADR-064 모달 어휘 금지 정합) — Issue 본문에 "성능이 나쁨" 등 정성 표현 금지. 측정값과 임계값을 수치로 기록.

### 단계 3 — PMOAgent escalation

PMOAgent 는 `ops-signal` label Issue 를 감지하고:

1. **pattern_count 집계** — 동일 신호 유형의 Issue 누적 횟수 (cross-Story 패턴 감지)
2. **pattern_count ≥ 2** → ADR-045 §D-9 forcing function 발동 → ADR 후보 발의 (운영 pattern 의 정책화)
3. **retro 병합** — 운영 신호 Issue 를 Story 완료 retro 에 병합 기록 (PMOAgent retro corpus)

### 단계 4 — 다음 Epic 후보

PMOAgent 가 Epic 후보 발의 → Orchestrator 가 사용자에게 보고. 사용자가 확인하면:
- `codeforge:story-epic-flow-preflight` 로 Story / Epic flow 결정
- 해당 Epic 이 기존 8 lane 을 거쳐 다음 배포로 이어짐
- 배포 후 다시 운영 phase mechanism 이 감시 → loop 재진입

## §3. 답습 비교: retro pattern vs self-improving loop

| 항목 | ADR-045 retro pattern | 운영 phase self-improving loop |
|---|---|---|
| 트리거 | Story 완료 후 PMOAgent retro | 운영 신호 임계 초과 |
| 감지 주체 | PMOAgent (retro mandatory trigger) | cron workflow → 자동 Issue → PMOAgent |
| 집계 기준 | cross-Story pattern_count ≥ 2 | 동일 신호 유형 pattern_count ≥ 2 |
| 반응 | ADR escalation forcing function | Epic 후보 발의 + 사용자 확인 |
| 사람 게이트 | 있음 (사용자 확인) | 있음 (사용자 확인 — §4 참조) |
| 무한 loop 위험 | 낮음 (retro = Story 완료 trigger — Story 없으면 retro 없음) | **있음 — §4 식별** |

## §4. 무한 발산 위험 식별

### 위험 패턴

```
운영 신호 → Issue → Epic → 구현 Story → 배포 → 새 운영 신호 → 새 Issue → 새 Epic → ...
```

자동 Issue 생성이 활성화되면, 이 loop 가 자기 증식할 수 있다:

1. 운영 신호 A 발생 → Issue-A 자동 생성
2. Issue-A 가 Epic-A 로 발전 → Story-A 구현 → 배포
3. 배포 후 운영 phase 가 다시 신호를 회수 → 신호 B 발생 → Issue-B 자동 생성
4. Issue-B 가 Epic-B 로 발전 → Story-B 구현 → 배포
5. ... (무한 반복)

이 자체는 정상 작동처럼 보이지만, 아래 퇴화 케이스가 위험하다:

- **동일 신호 반복** — 동일 근원(root cause)에서 나오는 신호가 계속 임계를 초과하면서 매번 새 Epic 이 개시됨 (root cause 해소 없이 Issue 만 누적)
- **Issue 폭발** — 신호 임계가 너무 낮게 설정되면 짧은 시간에 다수 Issue 생성 (noise 과잉)
- **Epic 무한 중첩** — loop 가 다음 Epic 을 낳고, 그 Epic 의 배포가 다시 신호를 낳는 pattern_count 누적 없는 자기 증식

### 위험 수준

**중간 (MEDIUM)** — 완전 자동화가 아닌(사용자 확인 게이트 있음), 하지만:
- 사용자가 "진행해" 를 반복하면 실질적으로 무한 loop 에 동조하게 됨
- noise 과잉 Issue 가 GitHub repo 를 오염시킬 수 있음
- 동일 root cause 에 대한 Epic 중복 발의로 토큰·작업 낭비

### loop closure gate = S6 carrier (forward-ref)

**본 파일 (S1) 은 위험을 식별만 한다**. 실 loop closure mechanism 의 구현은 **S6 carrier** 로 명시 위임한다 (ADR-104 §결정 5 anti-scope):

S6 가 구현할 loop closure gate 예상 요소:
- **dedup gate** — 동일 신호 유형에 대해 open Issue 가 이미 존재하면 새 Issue 생성 억제 (중복 방지)
- **max-depth gate** — loop 깊이 카운터 (Issue → Epic → 배포 → 재신호 cycle 횟수 상한)
- **escalate_user gate** — max-depth 초과 시 자동 Issue 중단 + 사용자에게 ESCALATE (ADR-045 §D-9 `escalation_action: escalate_user` 패턴 답습)

S6 까지 loop closure gate 가 없는 동안, 운영 신호 Issue 는 cron workflow 가 **수동 throttle** (예: 동일 신호 유형 주당 1건 상한) 로 과잉 생성을 방지한다 (S4~S5 임시 안전망 — S6 에서 dedup 으로 교체).

## §5. loop 의 의도

self-improving loop 는 "codeforge 가 운영 신호로부터 스스로를 개선하는 회로" 다. 목적:

- 배포 후 발견된 실 문제가 다음 작업 우선순위에 반영된다
- PMOAgent 가 자동 감지 → retro pattern 집계 → ADR 의무 발의 까지 이어지는 체계가 운영 도메인에도 적용된다
- 사람(사용자) 이 무엇을 다음에 할지 운영 신호를 보고 결정할 수 있다

무한 발산 위험은 이 loop 의 **의도한 부작용**이며, S6 에서 closure gate 로 안전하게 닫힌다. S1 에서 이 위험을 명시적으로 식별하는 이유는 S6 를 필수(non-skippable) carrier 로 만들기 위함이다 — loop 개념을 도입하면서 closure gate 없이는 안전하지 않다는 것을 governance 문서에 기록한다.
