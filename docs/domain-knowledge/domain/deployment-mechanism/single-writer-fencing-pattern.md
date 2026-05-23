---
kind: domain_fact
type: domain-knowledge
area: deployment-mechanism
topic_slug: single-writer-fencing-pattern
title: Single-writer fencing pattern (writer-lease 매커니즘)
status: Active
tags:
  - deployment
  - fencing-token
  - writer-lease
  - single-writer
  - distributed-systems
related_adrs:
  - ADR-087
related_stories:
  - CFP-1317
  - CFP-1059
related_files:
  - docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
  - docs/domain-knowledge/domain/deployment-mechanism/stateful-daemon-bg-eligibility.md
  - docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md
carrier_story: CFP-1317-S1
created: 2026-05-23
updated: 2026-05-23
amended: 2026-05-23
---

# Single-writer fencing pattern (writer-lease 매커니즘)

## Summary

ADR-087 §결정 9.3 writer-lease 매커니즘의 narrative SSOT. distributed systems literature 핵심 개념 — fencing token + TTL + 자동 만료. BG-1 (단일-writer 영속 상태) + BG-4 (non-idempotent 작업 경쟁) 영역 cover.

## 컨텍스트

분산 시스템에서 **단일 writer 보장** = data corruption / split-brain 차단의 1차 안전장치. lock-based mutual exclusion 의 위크니스 (GC pause / network partition / process suspend) 를 cover 하는 패턴 = fencing token.

Kleppmann "Designing Data-Intensive Applications" Ch.8 "Distributed System Trouble" 절 "Fencing tokens" subsection 인용:

> "The lock service ... should also issue monotonically increasing fencing tokens. When a client wants to access the resource, it must include the latest fencing token. The resource server checks that the token is greater than any previous token, and rejects writes with a smaller token." [verified, source: Kleppmann DDIA Ch.8 published reference]

writer-lease = fencing token 의 **시간 만료 변종** — lease holder 가 일정 TTL 동안만 writer 권한 보유, 만료 시 자동 release + 다음 holder pickup.

## 정의

writer-lease = fencing token + TTL + heartbeat + auto-revoke 4 구성 요소의 패턴. single-writer 영역에서 GC pause / network partition / process suspend 등 lock-based mutual exclusion 의 weakness 를 cover 하기 위한 distributed systems literature 핵심 매커니즘.

### 4 구성 요소

### 1. Fencing token

- **정의**: monotonically increasing number (보통 64-bit integer or UUID + epoch)
- **목적**: lease holder 가 write 시 모든 resource server 에 token 동봉 → resource server 가 stale token reject (smaller token reject)
- **invariant**: token 은 lock service 에서만 발급 + 단조 증가 보장 (split-brain 시 old leader 의 stale token 자동 reject)

### 2. TTL (Time-To-Live)

- **정의**: lease 의 유효 기간 (보통 5s ~ 30s, application 별)
- **목적**: lease holder failure 시 (process crash / network partition) lease 자동 만료 → 다음 holder pickup 가능 영역 보장
- **trade-off**: 짧은 TTL = failover 빠름 + heartbeat 부담 ↑ / 긴 TTL = failover 느림 + 부담 ↓. application 별 SLO 에 따라 결정.

### 3. Heartbeat (lease renewal)

- **정의**: lease holder 가 TTL 만료 전 lock service 에 renewal request 발송
- **목적**: 정상 작동 중 lease 유지 + failure 시 자연 만료 → split-brain 차단
- **invariant**: heartbeat 실패 (network partition / lock service unreachable) 시 lease holder = **자발적 write 중단 의무** (fencing token 발급 외부 의존, holder 가 token 못 받으면 write 권한 없음)

### 4. Auto-revoke

- **정의**: TTL 만료 시 lock service 가 lease 자동 release + 다음 candidate 에 새 token 발급
- **목적**: zero-downtime failover (다음 holder pickup 자동)
- **invariant**: revoke 와 새 token 발급 = atomic operation (race-free)

## 핵심 규칙

writer-lease semantic invariant 4 (codeforge 도메인 적용 의무):
- (R1) lease holder 외 writer 무조건 reject (fencing token validation)
- (R2) TTL 만료 시 자동 revoke (zero-downtime failover)
- (R3) heartbeat 실패 시 holder 자발적 write 중단 (split-brain 차단)
- (R4) revoke + 새 token 발급 = atomic operation (race-free)

### 산업 prior art 4종

### Kleppmann "Designing Data-Intensive Applications" Ch.8 [verified]

- **Type**: 학술 reference
- **Key concept**: "fencing tokens prevent split-brain in distributed locks" — monotonically increasing number + resource server validation
- **Verify status**: published reference, 널리 알려진 distributed systems literature

### etcd lease (HashiCorp Raft-based KV) [hypothesis]

- **Type**: 산업 implementation
- **Key concept**: lease 키 TTL + revoke + auto-renew. Kubernetes leader election primary 매커니즘 (kube-scheduler / kube-controller-manager HA)
- **API**: `lease grant <ttl>` → lease ID + `lease keep-alive <id>` → heartbeat + `lease revoke <id>` → manual release
- **Verify status**: Codex TP#4 verify 영역 (etcd 공식 doc lease API verify)

### Kafka leader epoch [hypothesis]

- **Type**: 산업 implementation
- **Key concept**: partition leader 가 epoch number 증가 (monotonic), follower 가 stale leader 검출 → log truncation safe
- **mechanism**: leader election 시 ZooKeeper 또는 KRaft (Kafka Raft) 가 새 epoch 발급, old leader 의 write = epoch mismatch → reject
- **Verify status**: Codex TP#4 verify 영역

### ZooKeeper ephemeral node + Curator LeaderLatch [hypothesis]

- **Type**: 산업 implementation
- **Key concept**: session TTL 기반 lease pattern. session 만료 시 ephemeral node 자동 삭제 → 다음 candidate pickup
- **mechanism**: Apache Curator `LeaderLatch` recipe 가 LeaderSelector + ZooKeeper ephemeral 조합 → leader election + auto-failover
- **Verify status**: Codex TP#4 verify 영역

## 관련 ADR

- [ADR-087](../../../adr/ADR-087-deploy-lane-and-lifecycle-extension.md) §결정 9.3 writer-lease primary binding + §결정 9.5 concurrent deploy serialization cross-ref

### ADR-087 §결정 9.3 binding

본 entry = ADR-087 §결정 9.3 writer-lease 매커니즘의 narrative SSOT. 적격 BG mapping:

- **BG-1 (단일-writer 영속 상태)**: WAL single-writer = lease holder 단일 writer 보장 + lease 만료 시 안전 handoff (다음 holder 가 WAL 이어 받음)
- **BG-4 (non-idempotent 작업 경쟁)**: compactor non-idempotent = lease holder 단일 실행자 보장 + lease 만료 시 다음 holder pickup
- **BG-2 (외부 단일연결 자원) consumer-side self-judge**: 외부 시스템이 lease-based identifier 요구 시 (ApiKey + session ID 짝) writer-lease 적격

## 경계

본 entry + ADR-087 §결정 9.3 = **semantic invariant codify** 만. 실 구현 선택 = consumer 영역 분리.

### 실 구현 선택 (consumer-side)

본 entry + ADR-087 §결정 9.3 = **semantic invariant codify** 만. 실 구현 선택 = consumer 영역:

- etcd lease (Kubernetes 기반 consumer 권장 — kube-scheduler precedent)
- Kafka leader epoch (Kafka 기반 consumer)
- ZooKeeper ephemeral + Curator LeaderLatch (JVM 기반 consumer)
- 자체 구현 (Redis SETNX + EXPIRE 또는 PostgreSQL advisory lock + TTL row)

## Concurrent deploy + rollback race serialization (ADR-087 §결정 9.5 cross-ref)

§9.3 writer-lease 가 **data-plane single-writer** 영역 cover. **control-plane single-writer** (deploy event itself) = 별 layer (§9.5):

- deploy event-level serialization (FIFO queue) = 1 active deploy event = 1 lease holder
- concurrent deploy reject + rollback 진행 중 신규 deploy block
- 실 enforcement = consumer-side deploy orchestrator 영역 (별 carrier)

두 layer disjoint (data plane ↔ control plane) — writer-lease pattern 이 양 layer 에 동형 적용 가능 (lock service 가 data lease 와 deploy event lease 분리 namespace 발급).

## See also

- [stateful-daemon-bg-eligibility.md](stateful-daemon-bg-eligibility.md) — BG-1~4 비적격 기준 (본 entry 의 binding domain context)
- [../jsonl-write/race-condition-handling-pattern.md](../jsonl-write/race-condition-handling-pattern.md) — single-writer 인접 도메인 (cross-repo jsonl write Pattern A SHA-based optimistic concurrency). 두 entry 가 동일 domain motivation (단일-writer 보장) 의 disjoint layer — process-level (본 entry = writer-lease 매커니즘) vs file-level (jsonl-write = SHA optimistic concurrency).
- [ADR-087](../../../adr/ADR-087-deploy-lane-and-lifecycle-extension.md) §결정 9.3 (본 entry 의 binding ADR)
- Kleppmann "Designing Data-Intensive Applications" Ch.8 "Distributed System Trouble" — Fencing tokens 절


## 변경 이력

- 2026-05-23 (CFP-1317-S1, Wave A): 신설 entry. ADR-087 §결정 9.3 writer-lease 매커니즘 narrative SSOT + 4 prior art (Kleppmann DDIA / etcd lease / Kafka leader epoch / ZK ephemeral). mctrader#1272 escalation (b) 흡수 wrapper-side carrier.
