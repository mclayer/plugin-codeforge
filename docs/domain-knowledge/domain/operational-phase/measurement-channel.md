---
kind: domain_fact
type: domain-knowledge
area: operational-phase
topic_slug: measurement-channel
title: 운영 phase 측정 채널 — 0 API call constraint + wrapper-N/A invariant
status: Active
tags:
  - operational-phase
  - measurement-channel
  - zero-api-call-constraint
  - wrapper-na-invariant
  - filesystem-signal
  - cfp-1190
related_adrs:
  - ADR-104  # normative SSOT — §결정 3 (0 API call constraint) + §결정 4 (wrapper-N/A invariant)
  - ADR-083  # filesystem-only signal invariant — 0 API call 의 동형 source (§결정, L133)
  - ADR-066  # PAT scope 최소화 정합 (offline-first invariant)
  - ADR-072   # wrapper-self-app N/A invariant + Tier-1 declare-time exemption 패턴 source
  - ADR-064  # §결정 7 evidence-gated symmetric ratchet — consumer overlay 정책 축소 불가 (0 API call / wrapper-N/A 축소 차단)
related_stories:
  - CFP-1190  # 본 carrier
  - CFP-1187  # umbrella Epic
created: 2026-05-22
updated: 2026-05-22
---

# 운영 phase 측정 채널

> **normative SSOT**: [`docs/adr/ADR-104-operational-phase-definition.md`](../../../../archive/adr/ADR-104-operational-phase-definition.md). 본 파일은 ADR-104 §결정 3·4 의 서술적 elaboration 이다.

## 정의

**측정 채널** = 운영 phase 에서 신호를 회수하는 수단. codeforge 의 측정 채널은 **filesystem / cron 기반**이며 network call 을 최소화한다 (ADR-104 §결정 3 — 0 API call constraint).

측정 대상 신호 4종: 에러율 / latency burn rate / regression / smoke·health.

## 컨텍스트

### 동형 source — ADR-083

0 API call constraint 의 동형 source 는 ADR-083 (consumer-applicability-filter) §결정 (L133):

> "두 signal 모두 consumer-side filesystem 안 — network call 0, gh api 0, marketplace.json membership check 0"

ADR-083 는 upgrade flow applicability 필터 영역에서 이 원칙을 선언했다. ADR-104 §결정 3 은 이를 **운영 도메인**으로 확장한다.

### wrapper-N/A invariant 배경

wrapper (codeforge 자체) 는 production 배포 환경이 없다 (plugin = code 0 + runtime behavior 0 + production deploy state 부재, ADR-072 L172). 따라서 wrapper 는 운영 phase 실측 대상이 아니다 — 선언(declarative SSOT)만 보유한다.

이 비대칭성은 ADR-072 §결정 6 wrapper-self-app N/A invariant 의 도메인 일반화다.

## 핵심 규칙

### 0 API call constraint (ADR-104 §결정 3)

운영 phase 측정 채널은 가능한 한 filesystem / cron 기반이며 network call 을 최소화한다. 근거 3종:

**(a) offline-first invariant** (ADR-066 PAT scope 최소화 정합) — 측정 채널이 외부 credential / network 의존을 만들지 않는다.

**(b) trust boundary 명확** — filesystem-only signal = consumer 권한 area 안 only. 측정 채널이 production secret / credential / cross-repo trust 영역에 접근하지 않는다.

**(c) 측정 비용 최소** — 측정 자체가 부작용·비용을 만들지 않아야 한다 (single read / cron tick).

**허용 패턴**:

| 패턴 | 근거 |
|---|---|
| cron workflow 가 consumer repo 의 로컬 log 파일 파싱 | network call 0 |
| GitHub Actions 자체 환경 내 metric 집계 (Actions-internal) | 외부 network API 미사용 |
| health check endpoint 응답을 로컬 filesystem 에 기록 후 파싱 | 분석은 filesystem |

**위반 패턴 (anti-pattern)**:

| anti-pattern | 위반 이유 |
|---|---|
| GitHub API 직접 호출로 production 상태 측정 (`gh api` / REST) | network call (gh api 0 invariant 위반) |
| 외부 SRE metric API (Prometheus remote_read / Datadog metrics query) | network call 의존 |
| marketplace.json HTTP fetch 로 버전 비교 | network call 위반 |
| 실시간 webhook 수신으로 에러율 계산 | push-based network dependency |

### 측정 대상 신호 4종 (ADR-104 §결정 5 정량 우선)

**신호 1 — 에러율**

| 항목 | 내용 |
|---|---|
| 정의 | 단위 시간당 5xx / 실패 응답 / exception 발생 비율 |
| 출처 | consumer production 환경 (application log / Actions summary) |
| 측정 주체 | consumer 측 cron workflow (S4 이후) |
| 임계 정의 | S2 carrier 영역 (본 파일 = 신호 존재 선언만) |
| 자동 반응 | 임계 초과 시 자동 Issue 생성 |

**신호 2 — latency burn rate**

| 항목 | 내용 |
|---|---|
| 정의 | 단위 시간당 latency SLO 소진 속도 (배포 전 baseline 대비 비율) |
| 출처 | consumer production 환경 (response time log / Actions metric step) |
| 측정 주체 | consumer 측 cron workflow |
| 임계 정의 | S2 carrier 영역 |
| 자동 반응 | burn rate 임계 초과 시 자동 rollback 신호 → Issue 생성 |

latency burn rate = 순간 latency 가 아닌 **소진 속도** — SRE error budget burn rate 개념 답습.

**신호 3 — regression**

| 항목 | 내용 |
|---|---|
| 정의 | 직전 배포 baseline 대비 주요 지표 악화 (에러율 증가 / latency 증가 / throughput 감소 등) |
| 출처 | consumer production 환경 (배포 전후 비교, 로컬 baseline snapshot) |
| 측정 주체 | consumer 측 cron workflow (baseline snapshot 파일 vs 현재 측정값 비교) |
| 임계 정의 | S2 carrier 영역 |
| 자동 반응 | regression 감지 시 자동 Issue → 다음 Epic 후보 |

**신호 4 — smoke·health (지속 health check)**

| 항목 | 내용 |
|---|---|
| 정의 | 핵심 endpoint / 서비스 정상 동작 여부 (smoke test, health endpoint 응답 확인) |
| 출처 | consumer production 환경 |
| 측정 주체 | consumer 측 cron workflow (주기 실행) |
| 임계 정의 | FAIL = 즉시 자동 Issue (이진 — 임계 개념 없음) |
| 자동 반응 | health check FAIL 시 즉시 Issue 생성 |

배포검토 lane 의 "일회성 smoke" 와 구별: 배포검토 = 배포 직후 1회, 운영 phase = **지속 주기 실행**.

**정량 우선 원칙**: 4종 신호 모두 정량(숫자 임계) 우선, 모달·정성 어휘 ("성능이 나쁘면", "에러가 많으면") 금지 (ADR-064 forbid-list / ADR-104 §결정 5).

### wrapper-N/A invariant (ADR-104 §결정 4)

- **wrapper = declarative SSOT only** — 실측 0
- **consumer = 실측 Tier-2** — 실 신호 회수

```
ADR-072 §결정 6 (원형):
  production-cutover-evidence.yml Tier-1 declare-time exemption
  = production_cutover_touching=true AND repo=wrapper AND code_change=0 → fast-pass

운영 phase 확장 (ADR-104 §결정 4):
  운영 phase mechanism workflow 가 wrapper repo 에 trigger 되면
  → Tier-1 declare-time exemption 으로 fast-pass / skip
```

**consumer overlay 축소 불가** (ADR-064 §결정 7 정합) — 0 API call constraint + wrapper-N/A invariant 는 wrapper-canonical invariant. consumer 가 `operational_phase.enabled: false` 선언해도 override 되지 않는다.

## 경계

### Tier 분리 (검증 비대칭성)

| 검증 주체 | 검증 내용 | Tier |
|---|---|---|
| wrapper (codeforge) | 운영 phase 정의·정책 ADR 정합성 (본 파일 포함) | Tier-1 (declare-time) |
| consumer (mctrader 등) | 실 측정 신호 값·임계 동작 (S4 이후) | Tier-2 (runtime) |

### 이 파일이 결정하지 않는 것

- 신호 임계 구체값 (정량 수치) = S2 carrier 영역
- 실 cron workflow yml / script = S4~S7 carrier 영역
- consumer 별 적용 overlay schema = S4 이후 ADR-027 consumer adoption 패턴

## 관련 ADR

- [ADR-104](../../../../archive/adr/ADR-104-operational-phase-definition.md) — **normative SSOT** (§결정 3 0 API call + §결정 4 wrapper-N/A)
- [ADR-083](../../../../archive/adr/ADR-083-consumer-applicability-filter.md) — filesystem-only signal invariant (0 API call 동형 source)
- [ADR-072](../../../../archive/adr/ADR-072-production-evidence-deputy-and-epic-cutover-gate.md) — wrapper-self-app N/A invariant + Tier-1 declare-time exemption 패턴 source
- [ADR-066](../../../../archive/adr/ADR-066-pat-rotation-policy.md) — PAT scope 최소화 정합 (offline-first)
- [ADR-064](../../../../archive/adr/ADR-064-decision-principle-mandate.md) — §결정 7 evidence-gated symmetric ratchet (consumer overlay 축소 불가)

## 변경 이력

| 버전 | 날짜 | 변경 내용 | carrier |
|---|---|---|---|
| v1.0 | 2026-05-22 | 신설 — 측정 채널 narrative (CFP-1190 Phase 2) | CFP-1190 |
