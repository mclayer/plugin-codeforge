---
kind: registry
registry: 429-incident
version: "1"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/429-incident-v1.md
date: 2026-08-19
authors:
  - Claude (CFP-2967 carrier — ADR-109 Amendment 6 fail-safe fail-over telemetry observability)
amendment_log: []
related_adrs:
  - ADR-109  # rate-limit failure cascade telemetry; Amendment 6 fable-respan trigger wiring
  - ADR-043  # telemetry privacy policy (Allow-list ONLY + Deny-list regex)
  - ADR-163  # measurement channel architecture
related_files:
  - docs/inter-plugin-contracts/MANIFEST.yaml  # comment line — kind:registry 분류 명시
  - skills/rate-limit-429-mitigation/SKILL.md  # ADR-109 Amendment 6 행동 specification
  - docs/orchestrator-playbook.md  # 관찰 채널 context
---

# 429-incident v1

## 1. 목적

Orchestrator fable 모델 rate-limit (HTTP 429) 발생 시 fail-safe fail-over 신호 전달을 위한 event row schema machine-readable SSOT. ADR-109 Amendment 6 fable re-spawn trigger 데이터 기반 확보.

**kind:registry 분류**. MANIFEST.yaml comment 줄 관리만 (별도 entry 행 미추가 — stop-event-v1 / spawn-event-v1 선례).

## 2. Schema (7 field — Allow-list ONLY)

각 ledger row entry (producer 착지 형태):

| 필드 | 타입 | 필수 | producer 채움 | 설명 |
|---|---|---|---|---|
| `timestamp` | ISO8601 offset-aware (`Z`) | REQUIRED | YES | UTC 절대 순간 |
| `final_status` | enum | REQUIRED | YES | 구조적 상수 `failed` (성공 사건은 이 채널 미도달) |
| `lane` | string\|null | OPTIONAL | NO | 항구적 null |
| `agent_role` | enum\|null | OPTIONAL | NO | 항구적 null. 역할 어휘 closed-set ∪ null. **정본 = ADR-043 Amendment 7 (B) 행 단독**. 값공간 `{PL, deputy, worker} ∪ null` (agent 명이 아니다). **미상 필드는 `null` 명시, 생략 금지** |
| `retry_count` | int\|null | OPTIONAL | NO | 항구적 null |
| `cascade_depth` | int\|null | OPTIONAL | NO | 항구적 null |
| `error_pattern` | 폐쇄 enum | OPTIONAL | YES | `rate_limit` (단일 값공간) |

**producer 착지 행의 형태가 고정된다**:

```json
{"timestamp": "<UTC Z>", "lane": null, "agent_role": null, "retry_count": null,
 "final_status": "failed", "cascade_depth": null, "error_pattern": "rate_limit"}
```

**정직 ceiling (ADR-119)**: 턴 사망 주체가 Orchestrator 인지 서브에이전트인지 구별 불가. 30분 window 소비자는 계수만 읽으므로 손실 0 — 미래 판별자 추가 시 ADR-109 §결정 10 redaction matrix 행 1개 = **또 하나의 Amendment 의무** (schema_version 미도입 논거와 동형).

**bound (2') 정의역**: 착지 행의 전 필드가 컴파일 시점에 열거 가능한 상수여야 하며, producer 는 hook payload 를 **파싱하지 않고** payload 유래 값이 착지 행에 진입하는 경로가 **구조적으로 부재**해야 한다 (ADR-043 Amendment 7, §7.3 bound (2') 정의역 승계).

## 3. 항목

### 3.1 Allow-list ONLY enforcement

**7 field 외 capture 금지**. 추가 field capture = BREAKING change → ADR-163 §결정 2 + ADR-043 §결정 2 amendment 의무.

근거:
- Allow-list = future expansion 시 explicit ADR review 강제
- Deny-list 단독 = unknown unknown 위험
- 2-layer defense in depth (Allow-list + Deny-list)

### 3.2 tier: [advisory / priming]

본 계약 파일의 핵심 역할(axis ②) = **관측만, enforcement 비차용** (ADR-163 §결정 10 / 범위 한정 서술 — 기계 tier-honesty lint 정의역).

### 3.3 기록 어휘 ≠ 감지 어휘 (명시 분리 의무)

`StopFailure` matcher 가 주는 토큰 `rate_limit`(언더스코어)는 ADR-109 §결정 1 감지집합 literal 중 **어느 것도 아니다**. `error_pattern` 의 값공간은 감지집합 ∪ `{"rate_limit"}` 이며 이는 **§결정 1 감지집합에 원소를 추가하지 않는다**(NG-2 무저촉).

**producer 의 `error_pattern` 값공간 = CLOSED `{"rate_limit"}` 단일 원소**.

### 3.3 hook payload 계약 (벤더 소유 — 방어적 소비)

`StopFailure` 이벤트는 실재하며 matcher 값공간은 폐쇄 10종 (`rate_limit` 포함) `[source: code.claude.com/docs/en/hooks — verified 2026-08-19]`. 공통 payload 필드 = `session_id`·`prompt_id`·`transcript_path`·`cwd`·`permission_mode`·`hook_event_name` (+조건부 `agent_id`·`agent_type`). **`StopFailure` 전용 필드 스키마는 문서 미명시** — 확인 불가.

⇒ 방어 계약: **미지 필드 무시** / 필수 필드 부재 시 **fail-open**(기록 생략, 훅은 exit 0) / payload 의존 지점은 각각 `vendor-unverified` 라벨. `[verified]` 표기 금지.

### 3.4 Append rules

**writer**: producer 는 harness 훅 프로세스만 (§3.1 stdin 미파싱 · 상수 1행 write)

**storage**: 
- 유형: JSONL append-only (host-local, `.claude/ledger/429-incident-history.jsonl` — consumer overlay 무관)
- retention: 적용 안 함 (rolling archive — 별 job)
- 권한: file mode 0600 (T-INFO-2 mitigation)

**ordering**: 
- append-only invariant — truncate/pop/seek(0) 경로 0
- timestamp ISO8601 UTC offset-aware (naive ± tz 혼용 금지)
- 정렬 가정 금지 (`history_lines[-1]` 단축 금지)

**idempotency**: N/A (각 사건 = 단일 append, 재시도 0 구조)

**trigger_sources**:
- Orchestrator fable 모델 rate-limit HTTP 429 응답 수신 시 (ADR-109 Amendment 6 fail-safe trigger)

**opt_in_default_false**:
- telemetry.enabled: false default (ADR-043 §결정 1 invariant)
- wrapper always-on (Phase 2 배선, 현 Phase 1 = 기계 계약만 doc-only)
- silent always-on 금지

## 4. 변경 규칙

- **Append-only for v1.x**: 7 field 외 새 필드 추가 = ADR-163 §결정 2 + ADR-043 §결정 2 amendment 의무 (BREAKING → v2.0)
- **`error_pattern` enum 확장**: 2번째 value 추가 = ADR-109 §결정 1 감지집합 widen + ADR-043 §결정 2 amendment 의무 (BREAKING)
- **timestamp offset 변경 (UTC `Z` → 다른 tz)**: ADR-043 §결정 1 amendment 의무 (BREAKING — privacy/telemetry invariant)
- **storage backend 변경 (JSONL → 다른 포맷)**: ADR-163 §결정 4 amendment 의무 (BREAKING — format-specific guarantees)
- **opt-in default 변경 (false → true)**: ADR-043 §결정 1 amendment 의무 (BREAKING — privacy invariant)

## 5. Phase 1 / Phase 2 scope

### Phase 1 (본 PR CFP-2967)

- 본 schema file 신설 (kind:registry)
- MANIFEST.yaml comment 줄 갱신 (429-incident-v1 v1 명시)
- ADR-109 Amendment 6 신설 (fail-safe fail-over wiring 정책 codify)

### Phase 2 (deferred follow-up CFP)

- Telemetry hook 구현 (Python script `scripts/lib/append_429_incident.py` + 단순 상수 행 구성)
- Aggregation script (event log → 30분 window intensity bucket 산출, §3.3 scope 판별 gate 동반)
- ~Cryptographic audit trail~ N/A (git 이력 자체가 append-only substrate)
- Cross-host telemetry 통합 (ADR-043 §결정 5 deferred)

ROI gating prerequisite: 실측 429 사건 기반 phase 2 Priority 평가.

## 6. Cross-references

- **ADR-109** (rate-limit failure cascade telemetry) — 본 schema SSOT. Amendment 6 fail-safe fail-over 신호 codify
- **ADR-043** (codeforge telemetry privacy policy) — Allow-list ONLY (§결정 2) + Deny-list regex (§결정 3) + opt-in default false (§결정 1)
- **ADR-163** (measurement channel architecture) — measurement channel SSOT (§결정 2 schema principles)
- **docs/inter-plugin-contracts/MANIFEST.yaml** — kind:registry 분류 명시 (comment 줄)
- **skills/rate-limit-429-mitigation/SKILL.md** — ADR-109 Amendment 6 행동 specification
- **docs/kpi/429-incident-history.jsonl** — actual ledger (initial seed rows — Phase 1)

