---
kind: domain_fact
type: domain-knowledge
area: orchestrator-discipline
topic_slug: measurement-channel
title: Codeforge measurement channel — 4-channel observability boundary + stop-event-v1 ledger
status: Active
tags:
  - measurement
  - observability
  - telemetry
  - stop-event
  - jsonl
related_adrs:
  - ADR-025  # stop discipline (§결정 10 deferred slot 채움)
  - ADR-026  # post-merge automation (post-merge-counters.jsonl 30+ run ROI gate)
  - ADR-029  # phase execution visibility (sanitize policy SSOT 통합)
  - ADR-031  # lane-spawn evidence (§14 lane coarse vs spawn-event sub-step boundary)
  - ADR-038  # progress visualization TodoWrite (boundary 차단 — 측정 대상 아님)
  - ADR-039  # subagent default (§결정 9 deferred Phase 2 measurement)
  - ADR-042  # measurement channel architecture
  - ADR-043  # telemetry privacy policy
related_stories:
  - CFP-283
created: 2026-05-09
updated: 2026-05-09
---

# Codeforge measurement channel

## Summary

codeforge orchestration 의 **4-channel observability boundary** SSOT. Tier 3 (persistent ledger) 의 stop-event-v1 + post-merge-counters.jsonl 구조와, 각 channel 의 책임 경계 (측정 대상 / 측정 제외 대상) 를 명시한다. ADR-042 measurement channel architecture + ADR-039 Phase 2 enforcement 의 데이터 prerequisite.

## Pattern

4-channel observability model:
- **Tier 1 — TodoWrite progress** (ADR-038): session-local, non-persistent, rendering-only. 측정 대상 외.
- **Tier 2 — §14 Lane Evidence** (ADR-031): Story-scoped, commit-persisted, coarse-grained (lane level). spawn-event per-agent fine = 별 channel (Tier 3 spawn-event-v1, CFP-2393).
- **Tier 3 — JSONL ledger** (ADR-026 / ADR-042): cross-repo, append-only, time-series queryable. `post-merge-counters.jsonl` + `stop-event-v1` ledger + **`spawn-event-v1` ledger (per-agent token/cost attribution + replay, CFP-2393 — oh-my-claudecode MIT 차용)**. Pattern A (SHA-based optimistic concurrency) 의무 — [jsonl-write/race-condition-handling-pattern](../jsonl-write/race-condition-handling-pattern.md) 참조.
- **Tier 4 — GitHub telemetry** (future): Discussions / API metrics. scope TBD.

## Usage

신규 persistent ledger 도입 시:
1. Tier 3 JSONL pattern 채택 — `docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md` Pattern A 의무
2. long-lived branch + 단일 rolling PR (ADR-026 §결정 4)
3. ADR-042 §channel boundary 준수 — Tier 1/2 와 중복 측정 금지 (spawn-event-v1 = §14.12 Tier-1 mini-table 와 role separation, double-count 아님 — playbook §15.2 4번째 invariant)
4. stop-event-v1 schema 의 SSOT = [stop-event-v1.md](../../../../inter-plugin-contracts/stop-event-v1.md) §2 (18 field). spawn-event-v1 schema SSOT = [spawn-event-v1.md](../../../../inter-plugin-contracts/spawn-event-v1.md) §2 (19 field, enum/numeric/hash only)
   > **drift note (CFP-2393, 미정정 — stop-event 영역 over-reach 회피)**: 본 page 위 line "stop-event-v1 schema: `stop_event` field + `story_key` + `ts` + `session_id`" 표현은 stop-event-v1.md §2 계약(18 field)·실 runtime(append_stop_event.py 5 field) 양쪽과 모두 불일치하는 3-way drift 의 한 갈래다. 정정은 stop-event 영역 별 follow-up (본 spawn-event Story scope 외). spawn-event-v1 은 이 drift 를 복사하지 않기 위해 fix-event-v1 동형으로 author 됐다.

## 정의

**Measurement channel** 는 codeforge orchestration 의 **Tier 3 persistent measurement** 영역 — committed · queryable · time-series ledger 가 핵심. ADR-039 effective enforcement 의 ROI 검증 + Phase 2 enforcement 의 발동 trigger 데이터 prerequisite.

기존 codeforge observability stack 3-tier 중 Tier 3 가 가장 sparse — `post-merge-counters.jsonl` (ADR-026 lite scope) 만 존재했으며, stop-event-v1 ledger (ADR-025 §결정 10 deferred slot) 는 CFP-283 / ADR-042 신설로 채움. **spawn-event-v1 (per-agent token/cost attribution + replay) = CFP-2393 / ADR-042 Amendment 1 land** (구 Refactor B1 보류 해제 — Epic CFP-2391 S3, oh-my-claudecode MIT 차용). Tier 3 = 3 channel (post-merge-counters / stop-event-v1 / spawn-event-v1).

## 컨텍스트

본 page 는 ADR-042 (codeforge measurement channel architecture) + ADR-043 (codeforge telemetry privacy policy) 의 도메인 정의 cross-cutting reference. CFP-275 ADR-039 §결정 9 deferred 의 4 items 중 measurement channel slot only 처리 (CFP-283 carrier).

## 핵심 규칙

### Tier 분리 (3-tier observability stack)

| Tier | 의미 | 포함 channel |
|---|---|---|
| **Tier 1 ephemeral** | session / turn-only 휘발성 | stderr narration (ADR-029) / TodoWrite (ADR-038) / `.claude-work/progress/<KEY>.md` cache (CFP-20) |
| **Tier 2 committed lane-coarse** | git commit 영속, lane-level granularity | Story §10 FIX Ledger (CFP-32 / fix-event-v1) / Story §14 Lane Evidence (ADR-031) |
| **Tier 3 persistent measurement** | git commit 또는 sqlite/JSONL 영속, discrete event granularity | post-merge-counters.jsonl (ADR-026) / **stop-event-v1 ledger (CFP-283)** / **spawn-event-v1 ledger (CFP-2393 — per-agent attribution + replay)** |

### 4-channel boundary (ADR-042 §결정 1 / playbook §15 SSOT)

8-channel boundary 표 완전 enumeration = wrapper [`docs/orchestrator-playbook.md`](../../../orchestrator-playbook.md) §15 normative SSOT. 본 page 는 도메인 정의 cross-ref.

**Boundary 차단 invariant 4**:

- **TodoWrite ↔ stop-event-v1 boundary**: TodoWrite 호출은 stop-event-v1 ledger record 대상 아님 (ADR-038 standalone 정당화 — meta-cognitive scratchpad, file system / GitHub state mutation 미발화).
- **§14 ↔ spawn-event-v1 boundary**: spawn-event-v1 land (ADR-042 Amendment 1, CFP-2393). §14 lane-coarse ↔ spawn-event per-agent fine = disjoint granularity. **§14↔spawn-event dedup script 신설 의무** (read-time/aggregate, Phase 2 precondition AC).
- **§10 ↔ stop-event-v1 boundary**: stop-event-v1 의 `reason_class: policy_violation` row 가 §10 FIX Ledger row append 의 proxy. dedup 책임 = aggregate script (Phase 2). cold tier 별도 file 신설 안 함.
- **§14.12 ↔ spawn-event-v1 boundary (CFP-2393)**: §14.12 mini-table (Tier-1 quota-only, gitignored) 와 spawn-event-v1 (Tier-3 accounting+replay) = role separation, double-count 아님. §14.12 는 spawn-event land 후에도 Tier-1 quota-only 잔존. cross-write 금지.

### Storage architecture (ADR-042 §결정 4 / DataMigrationArch substantive)

**Hot tier default = sqlite** (JSONL 채택 안 함):

- WAL mode = atomic transaction + concurrent read 안전
- append-only invariant = sqlite trigger (`BEFORE UPDATE`/`BEFORE DELETE` → ROLLBACK)
- idempotency = `UNIQUE INDEX (event_id)` hardware-level enforcement
- schema migration = sqlite ALTER TABLE expand-contract 패턴

Storage path: `.claude-work/measurement/stop-event.sqlite` (consumer overlay `telemetry.storage_path` 로 override).

**Cold tier** = `docs/stories/<KEY>.md §10` FIX Ledger row append (`reason_class: policy_violation` row 가 cold tier proxy). 별도 cold tier file 신설 안 함 (Phase 1 scope 축소).

### Idempotency invariant (DataMigrationArch §11.6)

```
event_id = sha256(packet_id || actor || event_type || timestamp_iso8601)
```

`UNIQUE INDEX (event_id)` sqlite hardware enforcement. application-level retry 안전 (network retry / hook retry / spawn retry).

nested spawn double-count anti-pattern (Researcher §6.3 — claude-code#5904) 대응 = `parent_event_id` reference + chain dedup (Phase 2 aggregate script).

### Privacy invariant (ADR-043 SSOT)

- **opt-in default false** (모든 telemetry channel 적용 — wrapper / consumer 동일 trust model. stop_event / spawn_event 모두 per-channel flag default false)
- **Allow-list ONLY (channel 별 whitelist)** (capture 시점 — stop-event-v1 18 field / spawn-event-v1 19 field 외 capture 금지. spawn-event = enum/numeric/hash only, free-form string 0건)
- **Deny-list regex 6 pattern** (capture 통과 후 2차 안전망 — API key / GitHub PAT / 한국 주민번호 / email / hex≥32 / GitHub fine-grained PAT. spawn-event = free-form 0건이라 적용 0건, inherit 선언)
- **transcript content/path HARD invariant (spawn-event-v1, T-INFO-5 / ADR-043 Amendment 2)** — spawn-event 는 numeric aggregate + enum + hash 만 저장, transcript content / transcript_path 절대 미저장 (path = session-id 포함)
- **sha256 identity (spawn-event-v1, T-INFO-7 / ADR-043 Amendment 2)** — actor / parent_event_id = sha256 hash, raw 금지
- **wrapper-vs-consumer ledger isolation** (T-INFO-4 P0 위협 대응)
- **wrapper dogfood always-on enforcement** = Phase 2 follow-up CFP (env flag / hook / runtime validation 모두 본 ADR scope 외 — Phase 1 doc-only strict invariant 보존)

### 운영 invariant (OperationalRiskArchitect substantive)

- **0 API call constraint** (CRITICAL — measurement = measure 대상 amplify 금지)
- **best-effort 50ms ceiling** (append latency p99 ≤50ms, overflow 시 graceful degradation)
- **measurement-vs-fix scope boundary** (CFP-283 = measurement only, throttling / backoff / circuit breaker = 별도 후속 CFP)

### ROI gating (ADR-042 §결정 11 / ADR-026 §결정 3 패턴)

Phase 2 enforcement (rule-based hook / inline write detect / stop-event auto-fire / ~~rate-limit cascade detection~~ → **RESOLVED by ADR-057 (CFP-379)**: Orchestrator Opus 필수화 + Sonnet→Opus fallback 정책) 발동 prerequisite:

- post-merge-counters.jsonl 30+ run 누적
- ROI metric: (1) inline_violation_count 변화 추세 (2) `policy_violation_subdecision` stop frequency (3) token cost burn 정량 baseline

ROI 충분 시 follow-up CFP 발의 (Sonnet decider Phase 2 ROI 패턴 정합 — ADR-022 §결정 11).

## 경계

### 비-적용 (ledger record 대상 외)

- **TodoWrite scratchpad** — meta-cognitive scratchpad, file system / GitHub state mutation 미발화. boundary 차단.
- **stderr narration** — ephemeral debug, ledger 와 별도 channel (Tier 1 vs Tier 3). narration 이 ledger 를 대체 안 함.
- **재귀 spawn** — Orchestrator (top-level) 만 ledger write 권한 (ADR-039 §결정 3 Orchestrator-owned delegate subagent). subagent 의 자체 임의 ledger write = `policy_violation`.

### 관련 용어 분류

- **Hot tier**: sqlite raw event (7-30d retention, 14d default)
- **Cold tier**: §10 FIX Ledger row proxy (persistent, append-only)
- **Aggregate**: raw → §10 / dashboard 형식 변환 (Phase 2 script)
- **opt-in**: consumer 측 명시 발화 의무 (default false)
- **wrapper dogfood**: codeforge family 자체 development scope (Phase 1 = consumer 와 동일 default false trust model. always-on enforcement = Phase 2 follow-up CFP)

### 다른 ADR 와의 interaction (비-충돌 영역)

**TodoWrite (ADR-038) 와의 boundary** — TodoWrite tool surface 자체가 file system / GitHub state mutation 미발화. ledger record 대상 아님 (boundary 차단). ADR-042 §결정 1 invariant.

**Stop discipline (ADR-025) 와의 amends 관계** — §결정 10 deferred slot (stop-event-v1) 가 ADR-042 §결정 2 로 채움. ADR-025 의 5 종 whitelist 무변 — stop-event-v1 = 측정 channel, whitelist 자체 변경 X.

**Phase execution visibility (ADR-029) 와의 amends 관계** — §결정 2 sanitize policy 적용 범위 = narration (stderr) + telemetry ledger 양쪽 unified SSOT (ADR-043 §결정 3 / §결정 4 정합). CFP-283 carrier Amendment 1 (2026-05-09) land 완료. narration vs ledger 두 channel 모두 동일 sanitize 정책 inherit. ADR-029 §결정 2 = format / scope SSOT, ADR-043 §결정 3 = Deny-list regex / Allow-list 16 field SSOT.

**Lane-spawn evidence (ADR-031) 와의 boundary** — §14 lane coarse vs spawn-event-v1 sub-step. spawn-event-v1 보류 (ADR-042 §결정 3) — §14 schema 무변경 invariant 보존.

**Subagent default (ADR-039) 와의 inheritance** — §결정 9 4 deferred items 중 measurement channel slot only 처리 (CFP-283 carrier). 2 items 잔존 (inline write detect hook / spawn cost telemetry). ~~rate-limited cascade detection~~ → **RESOLVED by ADR-057 (CFP-379)**: Orchestrator Opus 필수화 + Sonnet→Opus fallback 정책.

**Post-merge automation (ADR-026) 와의 ROI gating** — §결정 3 30+ run ROI 평가 패턴 inherit. Phase 2 enforcement 발동 prerequisite.

## 관련 ADR

- [ADR-042](../../../../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md) — measurement channel architecture (architectural decision SSOT)
- [ADR-043](../../../../archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md) — telemetry privacy policy (sibling Phase 1 PR)
- [ADR-025](../../../../archive/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) — stop discipline (§결정 10 deferred slot 채움)
- [ADR-026](../../../../archive/adr/ADR-026-post-merge-automation.md) — post-merge automation (30+ run ROI gate 패턴)
- [ADR-029](../../../../archive/adr/ADR-029-phase-execution-visibility-expansion.md) — phase execution visibility (sanitize SSOT 통합 amends)
- [ADR-031](../../../../archive/adr/ADR-031-lane-spawn-evidence-trail.md) — lane-spawn evidence (§14 boundary)
- [ADR-038](../../../../archive/adr/ADR-038-progress-visualization-todowrite.md) — TodoWrite (boundary 차단)
- [ADR-039](../../../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — subagent default (§결정 9 deferred carrier)

## 변경 이력

- **2026-05-09** — ArchitectAgent 신규 작성 (CFP-283 carrier Story Phase 1 PR scope, ADR-042 §결정 12 동일 PR commit batch).
