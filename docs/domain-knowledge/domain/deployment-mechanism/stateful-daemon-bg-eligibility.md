---
domain: deployment-mechanism
title: Stateful daemon blue-green 비적격 기준 (BG-1~4)
date: 2026-05-23
carrier_story: CFP-1317-S1
related_adrs:
  - ADR-087  # §결정 5 §5.2 + §결정 9 binding (본 entry = ADR-087 narrative SSOT)
  - ADR-089  # Schema 변경 7 원칙 cross-ref (양방향 호환 / reverse 영역)
related_files:
  - docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
  - docs/domain-knowledge/domain/deployment-mechanism/single-writer-fencing-pattern.md
  - docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md  # See also — single-writer 인접 도메인
---

# Stateful daemon blue-green 비적격 기준 (BG-1~4)

ADR-087 §결정 5 "primary blue-green + BG-1~4 비적격 시 보조 매커니즘 (§결정 9)" 의 narrative SSOT. blue-green 단일 매커니즘 가정이 stateful daemon 영역에서 깨지는 4 sub-pattern + mctrader 사례 + 보조 매커니즘 mapping codify.

## 동인

blue-green deployment 의 핵심 전제 = **양쪽 (blue + green) 일시 동시 active** 후 atomic swap. 이 전제가 다음 4 영역에서 깨진다 (mctrader#1272 escalation (a) 발견):

- 영속 상태 단일-writer 보장 요구 (data corruption / split-brain 위험)
- 외부 시스템이 client-side 단일 연결 강제
- 시스템 자체가 lease / token 으로 single-active session 강제
- non-idempotent 작업의 동시 실행 중복 결과

## BG-1~4 정의 (ADR-087 §결정 5 §5.2 binding)

OR semantic — 1+ 만족 시 blue-green 차단 + §결정 9 보조 매커니즘 진입.

### BG-1 단일-writer 영속 상태

- **정의**: ACID-D (durability) + WAL (Write-Ahead Log) pattern. 동시 writer 2 instance = consistency invariant violation (data corruption / split-brain)
- **mctrader 사례**: `mctrader-data` WAL = single-writer DB 패턴 (시세 수집 raw write)
- **보조 매커니즘**: §결정 9.3 writer-lease (fencing token + TTL + 자동 만료) — lease holder = 단일 writer 보장
- **prior art**: MySQL InnoDB single-writer per partition / CockroachDB multi-Raft (본질적 rolling, blue-green 미적합)

### BG-2 외부 단일연결 자원

- **정의**: 외부 시스템이 client-side 단일 연결 강제. 동일 ApiKey / session ID 로 2 socket 시 server-side reject 또는 race condition
- **mctrader 사례**: `mctrader-market-bithumb` collector = Bithumb WebSocket (동일 ApiKey 2 socket 시 server-side race)
- **보조 매커니즘**: §결정 9.2 rolling 또는 §결정 9.3 writer-lease 양가성 영역 — consumer 의 외부 자원 protocol semantic 에 따라 self-judge (§결정 9.4)
- **rolling 적격 case**: 외부 시스템이 host-level disconnect → reconnect 안전 (WebSocket reconnect-on-disconnect 정합 거래소)
- **writer-lease 적격 case**: 외부 시스템이 lease-based identifier 요구 (ApiKey + session ID 짝 = 외부 server 단일 active session 강제)

### BG-3 single-active 세션 enforcement

- **정의**: 시스템 자체가 토큰 / lease 로 단일 active session 강제. 동시 2 instance = 주문 중복 위험 / position 누적 inconsistency
- **mctrader 사례**: `mctrader-engine` paper_runner (동시 2 instance = position 누적 risk)
- **보조 매커니즘**: §결정 9.2 rolling per-host (한 시점 active host = 1) — host-level 단일성 보장
- **layer 분리 (EC-D)**: rolling = host-level 단일성. session-level 단일성 = application code 책무 (lease + heartbeat) — rolling swap window 안 2 host 일시 active 가능 영역에서 application layer 가 redundant safety net 제공
- **prior art**: Redis master/replica swap (manual failover, atomic instance 단일성) / Curator LeaderLatch (session TTL 기반)

### BG-4 non-idempotent 작업 경쟁

- **정의**: 같은 입력에서 같은 결과 보장 안 됨. 같은 작업 동시 2 process 실행 시 중복 결과물 누적 / 부작용 누적 / 출력물 corruption
- **mctrader 사례**: `mctrader-data` compactor (동시 2 process compact = 중복 compact 결과물 누적)
- **보조 매커니즘**: §결정 9.3 writer-lease — lease holder = 단일 실행자 보장 + lease 만료 시 다음 holder pickup
- **rationale**: idempotent 작업 (예: HTTP GET / pure function call) 은 blue+green 동시 실행 안전 — BG-4 = idempotent 가정 깨지는 영역만 codify

## 2+ row 동시 만족 시 (EC-C)

mechanism 선택 = **최강한 invariant 우선**. 예시:
- `mctrader-data` WAL = BG-1 (단일-writer) + BG-4 (non-idempotent) 동시 → writer-lease 가 양 invariant 모두 cover, 우선 채택
- `mctrader-market-bithumb` collector = BG-2 (외부 단일연결) 단독 → §결정 9.4 self-judge (rolling 권장)

## Forward extensibility (EC-B)

BG-1~4 = consumer 가 식별 가능한 stateful pattern 의 초기 닫힌-set. 향후 BG-N+1 추가 (예: eventual-consistency multi-writer with conflict-resolution 영역) = 별 ADR-087 Amendment carrier.

## consumer-side 자가 진단 (project.yaml schema)

```yaml
deploy:
  strategy: blue-green | rolling | writer-lease  # default: blue-green
  eligibility_reason: null | BG-1 | BG-2 | BG-3 | BG-4  # default: null (BG-1~4 미해당)
```

- `strategy: blue-green` + `eligibility_reason: null` = primary blue-green (기존 consumer default, backward-compat)
- `strategy: rolling` + `eligibility_reason: BG-3` = single-active session enforcement 영역
- `strategy: writer-lease` + `eligibility_reason: BG-1` = single-writer 영속 상태 영역
- 2+ BG 동시 만족 시 = `eligibility_reason` 첫 만족 BG 기재 + strategy = 최강 invariant cover 매커니즘 (예: BG-1+BG-4 → `eligibility_reason: BG-1` + `strategy: writer-lease`)

## See also

- [single-writer-fencing-pattern.md](single-writer-fencing-pattern.md) — writer-lease / fencing token narrative + prior art (Kleppmann DDIA Ch.8 + etcd lease + Kafka leader epoch + ZK ephemeral)
- [../jsonl-write/race-condition-handling-pattern.md](../jsonl-write/race-condition-handling-pattern.md) — single-writer 인접 도메인 (cross-repo jsonl write layer Pattern A SHA-based optimistic concurrency). 두 entry 가 동일 domain motivation (단일-writer 보장) 의 disjoint layer — process-level (본 entry) vs file-level (jsonl-write).
- [ADR-087](../../../adr/ADR-087-deploy-lane-and-lifecycle-extension.md) §결정 5 + §결정 9 (본 entry 의 binding ADR)
- [ADR-089](../../../adr/ADR-089-schema-change-7-principles.md) (Schema 변경 7 원칙 — 양방향 호환 / reverse / smoke 영역)
