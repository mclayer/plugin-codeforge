---
name: rate-limit-429-mitigation
description: in-process Anthropic infra 429 surgical mitigation procedure SSOT. Use when Orchestrator detects Anthropic API rate limit response (HTTP 429 / "Server is temporarily limiting" / "rate limit" / "quota exceeded") during codeforge lane spawn or consumer project work, before parallel-burst contexts (Phase 0 brainstorm 7-agent spawn / debate round N+1 / deputy 6+3+1 fan-out). Provides 3-step procedure (detection 4-tuple, exp-backoff curve, retry sequential composition) + decision tree (low/medium/high intensity bucket → cap lookup). ADR-109 §결정 1-§결정 7 binding. Orchestrator inline whitelist closed 4-entry (ADR-039 §결정 2) 무손상 — retry primitive 위치 = 본 skill body.
---

# codeforge:rate-limit-429-mitigation

ADR-109 SSOT 정합 in-process Anthropic infra 429 mitigation procedure. Claude Code session alive context (Orchestrator 직접 제어 영역). Sibling Story B (#1355) OS-level external session auto-resume disjoint axis.

## When to invoke

본 skill 호출 trigger 3 종 (Orchestrator + chief author + RequirementsPL 모두 적용):

1. **Detection trigger** — Anthropic API response 안 다음 4 pattern any-match (closed-set, ADR-109 §결정 1):
   - `"rate limit"`
   - `"quota exceeded"`
   - `"429"`
   - `"Server is temporarily limiting"`
2. **Pre-burst preventive trigger** — parallel-burst context 진입 직전:
   - `codeforge:codeforge-brainstorm` skill 호출 직후 (7-agent Phase 0 spawn 직전)
   - DesignReview lane blanket debate round N+1 진입 직전 (debate-protocol-v1 v1.2)
   - ArchitectPLAgent 6+3+1 deputy + 4-tuple sub-tuple 단일-메시지 multi-tool spawn 직전
3. **Cascade detection trigger** — `docs/kpi/429-incident-history.jsonl` 직전 30분 누적 incident count ≥ 1건 시 (medium/high intensity bucket 진입)

## 3-step procedure

### Step 1 — 탐지 (Detection)

ADR-109 §결정 1 4-tuple any-match. detection enum closed-set (no regex wildcard).

```
detected = "rate limit" in response_body
        OR "quota exceeded" in response_body
        OR "429" in response_status
        OR "Server is temporarily limiting" in response_body
```

- **False-positive 차단**: regex wildcard 0 (closed-set 4-tuple only). user prompt body verbatim match 차단 (response source verify, TLS layer).
- **529 disjoint** (ADR-109 §결정 6): HTTP 529 status code = retry 무의미 영역 — 본 skill 영역 외 (longer cooldown 60s base max 300s separate axis).

### Step 2 — 대기 (Backoff)

ADR-109 §결정 2 exp-backoff curve full jitter (Marc Brooker AWS Architecture Blog 2015 verbatim).

#### Step 2.1 — Retry-After header 우선

`Retry-After` 또는 `anthropic-ratelimit-*-reset` header presence 시 header 값 적용 (exp-backoff override):

```
wait_seconds = parse_retry_after_header(response.headers)
```

#### Step 2.2 — Exp-backoff curve (header 부재 시)

```
wait_seconds = random_uniform(0, min(60, base * 2^attempt))
# base = 1s, attempt = 0..5 (max 6 attempts)
# 1s → 2s → 4s → 8s → 16s → 32s nominal, jittered (full jitter algorithm)
```

- **single attempt cap = 60s** (max wait per individual retry)
- **total max attempts = 6** (cumulative wall-clock ≤ 75s budget, EC-1 정합)
- **jitter rationale**: no-overlap retry distribution (contention avoidance proven, AWS verbatim)

### Step 3 — 재시도 (Retry sequential composition)

ADR-109 §결정 3 sequential composition (within-model timing axis → cross-model substitution axis disjoint cross-ref).

```
attempt 1: same-model retry (within-model timing axis, 본 ADR 신설)
  ├── success → §14 Lane Evidence marker write [429-auto-retry: count=1, final_status=success] → return
  └── failure → attempt 2

attempt 2: ADR-057 §결정 2 model fallback (Sonnet → Opus, max 1회, cross-model substitution axis cross-ref)
  ├── success → §14 marker [429-auto-retry: count=2, final_status=success] → return
  └── failure (Opus 도 429) → attempt 3..6 (soak 6 attempts)

attempts 3-6: 6 attempts soak (§결정 2 max 6 attempts cap)
  ├── any success → §14 marker → return
  └── all fail → §결정 4 circuit breaker open → §결정 5 user manual resume only
```

#### Step 3.1 — Circuit breaker open (ADR-109 §결정 4 3-window AND)

3 window 모두 충족 시 circuit breaker open:

| Window | Threshold | Source |
|---|---|---|
| Fast | 5건 / 1min | `docs/kpi/429-incident-history.jsonl` rolling window |
| Medium | 10건 / 5min | 동상 |
| Slow | 3건 / 1 week | `docs/kpi/429-incident.json` weekly aggregate |

#### Step 3.2 — Cascade depth ≥ 2 → user manual resume only (ADR-109 §결정 5)

`cascade_depth` = 단일 user request 안 retry sequence nested cascade level. depth ≥ 2 (예: same-model 429 → Opus fallback → Opus 429 → 2차 retry burst) 시:

- **자동 재시도 금지** (ADR-057 §결정 2 invariant verbatim 답습)
- **`AskUserQuestion` escalation** 또는 **사용자 turn 대기**
- §14 marker `[429-auto-retry: count=N, final_status=failed]` write + KPI JSONL append-only event log row write (cascade_depth field)

## Decision tree — Intensity bucket → Cap lookup

Phase 0 brainstorm 7-agent burst + debate round + deputy fan-out 진입 직전 cap lookup. `docs/kpi/429-incident-history.jsonl` 직전 30분 window incident count 기준:

```
intensity = count_429_incidents_last_30min()

if intensity == 0:  # Low intensity
    parallel_spawn_cap = 7  # default (parallel-dispatch-protocol-v1 §6.2 worker_count_max)
    spawn_stagger_ms = 0    # no stagger
    fallback_mode = "parallel"

elif intensity == 1:  # Medium intensity
    parallel_spawn_cap = 4  # sequential 2-batch (4-agent → 3-agent)
    spawn_stagger_ms = 5000  # 5s inter-batch wait
    fallback_mode = "sequential_2batch"

else:  # High intensity (>= 2)
    parallel_spawn_cap = 1  # fully sequential
    spawn_stagger_ms = 10000  # 10s inter-agent wait
    fallback_mode = "fully_sequential"
```

- **Phase 0 brainstorm 7-agent spawn** (`codeforge:codeforge-brainstorm`): low/medium/high intensity bucket 적용
- **Debate round N+1**: round-level cascade detection (직전 2 round 누적 429 ≥ 2건 → `pause_reason: 429_cascade_throttle` + `AskUserQuestion`)
- **Deputy 6+3+1 + 4-tuple fan-out**: ArchitectPLAgent 단일-메시지 multi-tool spawn 직전 동일 lookup 적용

## Anti-pattern guard (RefactorAgent 권고 정합)

본 skill body = **3-step procedure 수준만** codify. 다음 영역 = **skill body 영역 외**:

- Jitter algorithm 세부 구현 (full jitter vs decorrelated jitter vs equal jitter) — Dev 실행 시점 결정 영역
- HTTP header parsing 세부 (`Retry-After` delta-seconds vs HTTP-date format edge case) — Dev 실행 시점 결정 영역
- Anthropic SDK 또는 HTTP client 의존성 (concrete library 선택) — runtime cover, skill body 영역 외
- Per-tier rate limit threshold tuning (per-org / per-API-key adaptive threshold) — Phase 2 telemetry post-deploy refine 영역 (ADR-068 I-5 dimensional empirical grounding 정합)

**rationale**: skill body 과세분화 시 (1) 변경 surface ↑ (2) ADR-064 §결정 5 CFP scope unitary 위반 risk (3) RefactorAgent decoupling 권고 위반 (skill body = procedure SSOT only, implementation detail = Dev 영역).

## Telemetry write (§14 Lane Evidence marker)

Retry sequence 종료 (success / failed / abort) 시점 의무 marker write:

```yaml
# Story §14 lane_evidence[] entry 안 transcript 필드
transcript: "<lane evidence narrative> [429-auto-retry: count=<N>, final_status=<success|failed>]"
```

- regex (mechanical lint `429-retry-evidence-presence` warning tier, ADR-109 §결정 8.1):

```
\[429-auto-retry: count=\d+, final_status=(success|failed)\]
```

- **§10 FIX Ledger row append 금지** (ADR-109 §결정 9 boundary): 429 retry = 운영 phase telemetry axis (ADR-104 정합), governance FIX 영역 외. fix:* label 미부착, ADR-067 RESET counter 영향 0.

## KPI JSONL append-only event log

`docs/kpi/429-incident-history.jsonl` 동시 append (ADR-109 §결정 8.2 + §결정 10 redaction matrix 정합):

```jsonl
{"timestamp": "<KST +09:00 ISO 8601>", "lane": "<요구사항|설계|...>", "agent_role": "<PL|deputy|worker>", "retry_count": <int>, "final_status": "<success|failed>", "cascade_depth": <int>, "error_pattern": "<4-tuple enum>"}
```

- **Secret redaction matrix** (ADR-109 §결정 10 unconditional invariant ADR-068 I-3):
  - `org_id` / `account_id` = **strip (collection-time)** (수집 자체 금지)
  - `session_uuid` = hash (SHA-256 truncated 8-byte)
  - `api_endpoint` = mask (domain only, path strip)
  - user prompt body / lane agent prompt body = 수집 금지

## Cross-references

- [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) — 본 skill body SSOT (§결정 1-§결정 10)
- [ADR-039](../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 2 inline whitelist closed 4-entry 보호 + §결정 9 carryover (Amendment N)
- [ADR-044](../../archive/adr/ADR-044-phase-scoped-sequential-team.md) — Amendment N team-spec yaml `parallel_spawn_cap` + `spawn_stagger_ms` + `cascade_circuit_breaker` 3 field 신설
- [ADR-057](../../archive/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — §결정 2 cross-model substitution axis (sequential composition cross-ref)
- [ADR-064](../../archive/adr/ADR-064-decision-principle-mandate.md) — §결정 4 Trace 4 Amendment N (surgical exception channel)
- [ADR-067](../../archive/adr/ADR-067-fix-ledger-implementability-escalation.md) — RESET contamination 차단 cross-ref
- [ADR-104](../../archive/adr/ADR-104-operational-phase-definition.md) — 운영 phase 1st-class 정의
- [ADR-106](../../archive/adr/ADR-106-operational-signal-pmo-input-circuit.md) — 운영 metric → PMOAgent input 회로
- `mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1354-in-process-429-mitigation.md` — Phase 1 Change Plan carrier (dogfood-out per ADR-013)
