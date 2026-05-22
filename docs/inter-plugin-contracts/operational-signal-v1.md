---
kind: registry
registry: operational-signal
version: "1.0"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/operational-signal-v1.md
date: 2026-05-22
authors:
  - ArchitectAgent (CFP-1195 carrier — ADR-106 §결정 5 defer resolve, self-improving loop input schema SSOT)
version_history:
  - { version: "1.0", date: 2026-05-22, carrier: CFP-1195, change: "initial — 운영 신호 input schema (monitor cron → PMOAgent escalation). 10-field signal event schema + signal_type 4-value enum (error_rate/latency_burn_rate/regression/smoke_health) + escalation_action 3-value enum (adr_draft_emitted/escalate_user/none) + 단계 1→2-b→3→4 회로 경계 + pmo-output-v1 cross-ref (input vs output disjoint). ADR-106 §결정 3 KPI 구조 + §결정 5 contract defer resolve (A-2 kind:registry 채택). kind:registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합)." }
owner_adr: ADR-106  # 운영 metric → PMOAgent input 회로 (§결정 3 KPI 구조 / §결정 5 contract defer resolve)
carrier_story: CFP-1195
sibling_sync_exempt: true
related_adrs:
  - ADR-106  # owner — 회로 4단계 / loop closure 3원칙 / KPI append-only 구조 / contract defer resolve
  - ADR-104  # 0 API call (§결정 3) + wrapper-N/A (§결정 4)
  - ADR-105  # 안전장치 3 escalation 회로
  - ADR-045  # §D-9 escalation 답습 (도메인 disjoint) + §D-4 SHA optimistic write 경합
  - ADR-008  # Inter-plugin contract versioning (registry MINOR/PATCH sibling sync 면제)
  - ADR-010  # Inter-plugin Contract Sibling Sync (kind:registry exempt §결정 2)
  - ADR-024  # hotfix-bypass label family (`hotfix-bypass:self-improving-loop`)
  - ADR-060  # Evidence-enforceable promotion framework (warning tier entry `self-improving-loop-closure`)
  - ADR-064  # 정량 우선 (loop closure threshold 숫자) + Trace 4 default parallel
  - ADR-079  # KST display layer (detected_at_kst field)
related_files:
  - scripts/operational-signal-to-issue.sh                          # 단계 2-b producer (Issue 발의 + Epic-level dedup gate)
  - scripts/loop_closure_gate.py                                     # KPI jsonl append-only write + max-depth counter (ADR-061)
  - scripts/check-ops-signal-alerts.sh                              # 단계 3 PMOAgent escalation pickup scan
  - docs/kpi/operational-signal-history.jsonl                       # KPI append-only history (10-field event)
  - docs/kpi/operational-signal-rate.json                           # state summary (rolling window 집계)
  - docs/inter-plugin-contracts/pmo-output-v1.md                    # 단계 3 escalation 출력 carrier (cross_story_pattern_adr_trigger 재사용)
  - templates/github-workflows/self-improving-loop-closure.yml      # 단계 2-b cron (독립 cron 0 0 * * *)
---

# operational-signal-v1 — 운영 신호 input schema (self-improving loop)

> **kind:registry** (sibling sync 면제, ADR-010 §결정 2). canonical = `mclayer/plugin-codeforge`.
> ADR-106 §결정 5 (operational-signal contract defer) 의 resolve — 설계 lane 확정 = A-2 (kind:registry).

## 1. 목적

운영 phase self-improving loop (ADR-106) 의 **단계 1 → 단계 3 input** schema SSOT. monitor cron (S4/S5, wrapper templates — consumer 실행) 이 발의하는 `ops-signal` label Issue 의 body schema + KPI append-only history (`operational-signal-history.jsonl`) event schema 를 정의한다.

**방향 + 도메인 disjoint** (pmo-output-v1 과 분리 근거): operational-signal-v1 = monitor → PMOAgent **input** (운영 신호 event) / pmo-output-v1 = PMOAgent → Orchestrator **output** (retro / Epic 산출 + escalation). 단계 3 escalation **출력**은 pmo-output-v1 `cross_story_pattern_adr_trigger` field 를 재사용한다 (input event 가 escalation 으로 소비된 후의 출력).

## 2. Schema

operational-signal-v1 은 2 layer schema 를 정의한다: (a) signal event schema (10-field — KPI jsonl 의 1 line / ops-signal Issue body) — §3 항목 / (b) 회로 단계 경계 + loop closure 3원칙 binding — §3 항목 하위. signal event 1 line = `operational-signal-history.jsonl` 의 1 append entry (append-only).

## 3. 항목

### 3.1 signal event schema (10-field)

ADR-106 §결정 3 KPI append-only state 구조 (10-field) 와 동일. `operational-signal-history.jsonl` 의 1 line = 1 signal event:

```jsonl
{"signal_signature": "<signal_type>:<measured_value>:<window>", "signal_type": "error_rate|latency_burn_rate|regression|smoke_health", "measured_value": <number>, "threshold": <number>, "window": "<숫자+단위>", "detected_at_kst": "YYYY-MM-DDTHH:MM:SS+09:00", "issue_ref": "<owner>/<repo>#<N>", "escalation_action": "adr_draft_emitted|escalate_user|none", "pattern_count": <int>, "loop_depth": <int>}
```

| field | type | required | 의미 | invariant |
|---|---|:-:|---|---|
| `signal_signature` | string | Y | `<signal_type>:<measured_value>:<window>` (S4/S5 sha256 signature 의 human-readable form) | dedup key canonical = S4/S5 16-char sha256 hex (`sha256(signal_type\|measured\|window) \| head -c 16`, `check_rollback_signal.py` L20). colon-form 은 KPI jsonl human-readable view (dedup 비사용). Issue-level [S4/S5] + Epic-level [S6] dedup 모두 hex signature 기준 |
| `signal_type` | enum | Y | `error_rate` \| `latency_burn_rate` \| `regression` \| `smoke_health` (measurement-channel.md 4종 신호) | closed enum (open_extension: false — 신규 신호 유형 추가 시 MINOR bump). **note**: S4 producer (`check_rollback_signal.py`) 가 burn-rate 임계 초과 시 정규 enum value `latency_burn_rate` 를 emit 한다 (CFP-1243 / ADR-106 Amendment 3 — producer 가 비정규 alias `burn_rate` → 정규명 `latency_burn_rate` 로 conform, 근원 drift 해소 완료). enum value ↔ producer literal 일치 — alias 없음 |
| `measured_value` | number | Y | 측정값 (정량 — ADR-064 모달 어휘 금지) | append-only (덮어쓰기 0) |
| `threshold` | number | Y | 임계값 (consumer SLO) | — |
| `window` | string | Y | 측정 window (숫자+단위, 예 `3600s`) | spike vs sustained 구분 (EC-4) |
| `detected_at_kst` | string | Y | KST `+09:00` ISO 8601 zoned (ADR-079 display layer) | display only — 집계/dedup 계산은 UTC epoch |
| `issue_ref` | string | Y | `<owner>/<repo>#<N>` ops-signal Issue 참조 | consumer repo scope |
| `escalation_action` | enum | Y | `adr_draft_emitted` \| `escalate_user` \| `none` | `none` (단계 2-b) → `adr_draft_emitted\|escalate_user` (단계 3/4) 전이 |
| `pattern_count` | int | Y | 동일 signal_type signature 누적 횟수 | ≥ 2 → ADR-045 §D-9 forcing function (도메인 disjoint 답습) |
| `loop_depth` | int | Y | loop cycle 깊이 카운터 (신호→Issue→Epic→배포→재신호 1회당 +1) | monotonic / max-depth gate (≥ 상한 → escalate_user) |

### 3.2 회로 단계 경계 (ADR-106 §결정 1)

| 단계 | producer | consumer | schema 사용 |
|---|---|---|---|
| 단계 1 — 신호 회수 | S4/S5 monitor cron (measurement-channel.md) | — | signal event 생성 (`escalation_action: none`) |
| 단계 2-a — monitor-originated notification | S4/S5 monitor (MERGED) | — | Issue-level signature dedup + ops-signal Issue 발의 |
| 단계 2-b — 일반 ops-signal + Epic-level dedup | operational-signal-to-issue.sh (S6) | — | (a) 비-monitor 신호 Issue 발의 + (b) Epic-level dedup gate (모든 ops-signal) + KPI jsonl append |
| 단계 3 — PMOAgent escalation | check-ops-signal-alerts.sh (S6) | PMOAgent | pattern_count 집계 → `escalation_action` 결정 → pmo-output-v1 `cross_story_pattern_adr_trigger` 출력 |
| 단계 4 — 다음 Epic 후보 | PMOAgent → Orchestrator | 사용자 | escalation_action enum → 사용자 확인 게이트 (self-improving ≠ self-executing) |

### 3.3 loop closure 3원칙 (ADR-106 §결정 4 — OR 발동)

| 원칙 | field 의존 | trip 조건 | consumer overlay threshold |
|---|---|---|---|
| (a) dedup | `signal_signature` | open Issue OR 진행 Epic 존재 | `dedup_window_hours` (default 24, 확장 가능/축소 불가) |
| (b) max-depth | `loop_depth` | loop_depth ≥ 상한 | `loop_max_depth` (default 3) |
| (c) escalate_user | `escalation_action` | max-depth/dedup OR trip | `pattern_count_threshold` (default 2) |

OR 발동 (하나라도 trip 시 자동 발의 억제 — 보수적 fail-safe). consumer overlay (`project.yaml deploy.self_improving_loop`) 확장 가능 / 축소 불가 (ADR-057 / ADR-058 ratchet).

### 3.4 pmo-output-v1 disjoint (escalation 출력 carrier)

| contract | 방향 | 도메인 | 본 contract 관계 |
|---|---|---|---|
| operational-signal-v1 (본) | monitor → PMOAgent (input) | 운영 신호 event | input schema SSOT |
| pmo-output-v1 (v1.2) | PMOAgent → Orchestrator (output) | retro / Epic 산출 + escalation | 단계 3 escalation 출력 carrier (`cross_story_pattern_adr_trigger` 5 sub-field 재사용) |

**ADR-045 §D-9 disjoint 답습** (도메인 disjoint — "ADR-045 와 동일" 단일 진술 금지): 같은 PMOAgent escalation 메커니즘 (threshold N=2 / escalation_action enum / 인간 게이트) 공유하나 입력 corpus disjoint (retro corpus [ADR-045] vs operational signal [본]). ADR-045 본문 무변경.

### 3.5 무결성 invariant (ADR-106 §결정 3 / ADR-045 §D-4)

- **append-only invariant** — `operational-signal-history.jsonl` 측정값 덮어쓰기 0 (event sourcing / audit log immutability). 신호 이력 무결성 (변조 차단 / 손실 0 audit trail).
- **write 경합 invariant** — ADR-045 §D-4 Pattern A (Contents API SHA-based optimistic concurrency): 409 Conflict → 최신 SHA re-fetch + CAS retry. last-writer-wins 0 / 신호 손실 0.
- **idempotency invariant** — 동일 signal event 중복 append 0 (`signal_signature` + `detected_at_kst` 기반). `loop_depth` monotonic counter (재계산 idempotent). counter scope = repo-local (consumer repo `operational-signal-history.jsonl` SSOT).
- **0 API call invariant** — 신호 측정 source = filesystem / cron (ADR-104 §결정 3). 실시간 telemetry API 직접 호출 0. Issue 발의/조회 = consumer repo scope gh CLI.

### 3.6 wrapper-self-app N/A (ADR-104 §결정 4 / ADR-072)

wrapper repo (`mclayer/plugin-codeforge`) trigger 시 Tier-1 declare-time exemption fast-pass (exit 0) — production 환경 부재, loop closure 무의미. 실 loop closure / KPI write = consumer (production) 한정. wrapper = declarative SSOT (schema 정의 + template 제공).

## 4. 변경 규칙

- **versioning** (ADR-008): MINOR bump = signal_type enum 추가 / field optional 추가 (backward-compat) / 회로 단계 경계 정밀화. PATCH = 오타·링크. MAJOR = field 제거 / enum 의미 변경 (backward-incompat).
- **kind:registry sibling sync 면제** (ADR-010 §결정 2): canonical = `mclayer/plugin-codeforge`. sibling plugin sync 불요. plugin.json bump 불요 (ADR-008 §결정 2 row append).
- **closed enum invariant** (ADR-064 §self-application ratchet): `signal_type` (4-value) / `escalation_action` (3-value) = closed enum (open_extension: false). 추가 시 MINOR bump + 약화 방향 (enum 축소 / loop closure 원칙 완화 / 사용자 게이트 제거) = ADR-058 §결정 5 약화 evidence-gate 의무.
- **append-only ratchet**: signal event schema field 제거 = breaking (MAJOR). field 추가 = MINOR (append-only history backward-compat — 구 row 의 신규 field 부재 = null).

## 관련 ADR

- **ADR-106** — owner (회로 4단계 / loop closure 3원칙 / KPI 구조 / §결정 5 contract defer resolve)
- **ADR-104** — 0 API call (§결정 3) + wrapper-N/A (§결정 4)
- **ADR-105** — 안전장치 3 escalation 회로
- **ADR-045** — §D-9 escalation 답습 (도메인 disjoint) + §D-4 SHA optimistic
- **ADR-008 / ADR-010** — kind:registry sibling sync 면제
- **ADR-079** — KST display layer (detected_at_kst)
