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
  - ADR-72   # wrapper-self-app N/A invariant + Tier-1 declare-time exemption 패턴 source
  - ADR-057  # consumer overlay 정책 축소 불가 (0 API call / wrapper-N/A 축소 차단)
related_stories:
  - CFP-1190  # 본 carrier
  - CFP-1187  # umbrella Epic
created: 2026-05-22
updated: 2026-05-22
---

# 운영 phase 측정 채널

> **normative SSOT**: [`docs/adr/ADR-104-operational-phase-definition.md`](../../../adr/ADR-104-operational-phase-definition.md). 본 파일은 ADR-104 §결정 3·4 의 서술적 elaboration 이다.

## §1. 0 API call constraint — "측정 자체가 부작용을 만들면 안 된다"

### 원칙

운영 phase 측정 채널은 **filesystem / cron 기반**이며 network call 을 최소화한다 (ADR-104 §결정 3).

이 원칙의 동형 source 는 ADR-083 (consumer-applicability-filter) §결정 (L133):

> "두 signal 모두 consumer-side filesystem 안 — network call 0, gh api 0, marketplace.json membership check 0"

ADR-083 는 upgrade flow applicability 필터 영역에서 이 원칙을 선언했다. ADR-104 §결정 3 은 이를 **운영 도메인**으로 확장한다.

### 왜 측정이 부작용·비용을 만들면 안 되는가

근거 3종 (ADR-104 §결정 3 / ADR-083 L133 답습):

**(a) offline-first invariant** (ADR-066 PAT scope 최소화 정합)

측정 채널이 외부 credential / network 의존을 만들면, 측정 시스템 자체가 추가적인 인증·권한 관리 overhead 를 요구하게 된다. 이는 ADR-066 의 PAT scope 최소화 철학에 반한다. filesystem/cron 기반이면 이 overhead 가 없다.

**(b) trust boundary 명확**

filesystem-only signal = consumer 권한 area 안 only. 측정 채널이 production secret / credential / cross-repo trust 영역에 접근하지 않아야 한다 (§7 보안 경계 정합). 외부 metric API (Prometheus 원격 query, Datadog API call 등) 를 측정 채널로 쓰면 해당 API 의 credential 이 codeforge mechanism 에 들어오게 된다 — trust boundary 위반.

**(c) 측정 비용 최소 (single read / cron tick)**

실시간 metric API 기반 canary analysis (progressive delivery 외부 SRE 패턴) 는 API 호출 횟수가 많고, API failure 가 측정 시스템 failure 로 전파된다. codeforge 의 운영 phase 는 filesystem 읽기 + cron tick = 최소 비용으로 신호를 회수한다.

### 0 API call constraint 위반 패턴 (anti-pattern)

아래 패턴은 0 API call constraint 위반이다:

| anti-pattern | 위반 이유 |
|---|---|
| GitHub API 직접 호출로 production 상태 측정 (`gh api` / REST) | network call (gh api 0 invariant 위반) |
| 외부 SRE metric API (Prometheus remote_read / Datadog metrics query) | network call 의존 |
| marketplace.json HTTP fetch 로 버전 비교 | network call (marketplace.json membership check 0 invariant 위반) |
| 실시간 webhook 수신으로 에러율 계산 | push-based network dependency |

**허용 패턴** (0 API call constraint 충족):

| 패턴 | 근거 |
|---|---|
| cron workflow 가 consumer repo 의 로컬 log 파일 파싱 (filesystem read) | network call 0 |
| cron workflow 가 GitHub Actions 자체 환경 내 metric 집계 (Actions-internal) | 외부 network API 미사용 |
| health check endpoint 응답을 로컬 filesystem 에 기록 후 파싱 | network call = health check 1회 (허용 범위), 분석은 filesystem |

## §2. 측정 대상 신호 enum

운영 phase 가 측정하는 신호는 4종 (ADR-104 §결정 5 "정량 신호 우선" + ADR-064 모달 어휘 금지 정합):

### 신호 1 — 에러율 (error rate)

| 항목 | 내용 |
|---|---|
| 정의 | 단위 시간당 5xx / 실패 응답 / exception 발생 비율 |
| 출처 | consumer production 환경 (application log / Actions summary) |
| 측정 주체 | consumer 측 cron workflow (S4 이후) |
| 임계 정의 | S2 carrier 영역 (본 파일 = 신호 존재 선언만 — ADR-104 §결정 5 정합) |
| 자동 반응 | 임계 초과 시 자동 Issue 생성 → self-improving-loop.md §1 진입 |

### 신호 2 — latency burn rate

| 항목 | 내용 |
|---|---|
| 정의 | 단위 시간당 latency SLO 소진 속도 (배포 전 baseline 대비 비율) |
| 출처 | consumer production 환경 (response time log / Actions metric step) |
| 측정 주체 | consumer 측 cron workflow |
| 임계 정의 | S2 carrier 영역 |
| 자동 반응 | burn rate 가 임계 초과 시 자동 rollback 신호 → Issue 생성 |

latency burn rate 는 순간 latency 가 아닌 **소진 속도** 다. SRE 의 error budget burn rate 개념 답습 — 단기 spike 와 지속적 열화를 구별한다.

### 신호 3 — regression

| 항목 | 내용 |
|---|---|
| 정의 | 직전 배포 baseline 대비 주요 지표 악화 (에러율 증가 / latency 증가 / throughput 감소 등) |
| 출처 | consumer production 환경 (배포 전후 비교, 로컬 baseline snapshot) |
| 측정 주체 | consumer 측 cron workflow (baseline snapshot 비교) |
| 임계 정의 | S2 carrier 영역 |
| 자동 반응 | regression 감지 시 자동 Issue → 다음 Epic 후보 (self-improving-loop.md) |

regression 측정 = filesystem 안 baseline snapshot 파일 vs 현재 측정값 비교. 외부 diff API 없이 로컬 파일 파싱.

### 신호 4 — smoke·health (지속 health check)

| 항목 | 내용 |
|---|---|
| 정의 | 핵심 endpoint / 서비스 정상 동작 여부 (smoke test, health endpoint 응답 확인) |
| 출처 | consumer production 환경 |
| 측정 주체 | consumer 측 cron workflow (주기 실행) |
| 임계 정의 | FAIL = 즉시 자동 Issue (임계 개념 없음 — 통과/실패 이진) |
| 자동 반응 | health check FAIL 시 즉시 Issue 생성 |

배포검토 lane 의 "일회성 smoke" 와 구별: 배포검토 = 배포 직후 1회, 운영 phase = **지속(ongoing) 주기 실행** (시간 성격 차이가 두 영역 disjoint 의 근거).

### 정량 우선 원칙 (ADR-064 정합)

4종 신호 모두 **정량(숫자 임계) 우선**이고 모달·정성 어휘 ("성능이 나쁘면", "에러가 많으면") 는 금지된다 (ADR-064 forbid-list / ADR-104 §결정 5). 구체 임계값(숫자)는 S2 carrier 영역.

## §3. wrapper-self-app N/A invariant

### wrapper(codeforge 자체) 는 운영 phase 실측 대상이 아니다

wrapper (codeforge 자체) 는 production 배포 환경이 없다 (plugin = code 0 + runtime behavior 0 + production deploy state 부재, ADR-72 L172). 따라서:

- **wrapper = declarative SSOT only** — wrapper repo 는 운영 phase 정의 / 정책 (ADR-104 + 본 4 파일) 만 보유한다. 실측 0.
- **consumer = 실측 Tier-2** — 운영 phase mechanism 의 실제 신호 회수는 consumer (mctrader 등 실 배포 환경) 대상이다.

이는 ADR-72 §결정 6 wrapper-self-app N/A invariant 의 도메인 일반화다:

```
ADR-72 §결정 6 (원형):
  production-cutover-evidence.yml Tier-1 declare-time exemption
  = production_cutover_touching=true AND repo=wrapper AND code_change=0 → fast-pass

운영 phase 확장 (ADR-104 §결정 4):
  운영 phase mechanism workflow 가 wrapper repo 에 trigger 되면
  → Tier-1 declare-time exemption 으로 fast-pass / skip
  (실 mechanism 신설 = S4~S7 carrier 영역)
```

### consumer 적용 기대 패턴 (S4 이후)

S4~S7 에서 consumer 용 운영 phase mechanism 이 신설되면, consumer 는 아래 패턴으로 적용한다:

1. consumer `.claude/_overlay/project.yaml` 에 `operational_phase.enabled: true` 선언 (ADR-027 consumer adoption 패턴)
2. consumer 자신의 production log path / health endpoint 를 overlay 에 기재
3. codeforge 운영 phase workflow 가 consumer 의 filesystem (log, snapshot) 를 읽어 신호 측정

wrapper-N/A invariant = consumer overlay 로 축소 불가 (ADR-057 정합). consumer 가 `operational_phase.enabled: false` 를 선언해도 wrapper-canonical invariant 로 인해 override 되지 않는다.

### 검증 비대칭성

wrapper 는 선언(declarative SSOT)만 검증하고, consumer 는 실측을 검증한다. 이 비대칭성은 ADR-072 Tier-1 / Tier-2 split 패턴을 운영 phase 도메인에 그대로 답습한다:

| 검증 주체 | 검증 내용 | Tier |
|---|---|---|
| wrapper (codeforge) | 운영 phase 정의·정책 ADR 정합성 (본 파일 포함) | Tier-1 (declare-time) |
| consumer (mctrader 등) | 실 측정 신호 값·임계 동작 (S4 이후) | Tier-2 (runtime) |
