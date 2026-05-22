---
adr_number: 106
title: 운영 metric → PMOAgent input 회로 — self-improving loop normative codify (회로 4단계 + ADR-045 §D-9 disjoint 답습 + KPI append-only + loop closure 3원칙 + operational-signal contract defer)
status: Accepted
category: governance
date: 2026-05-22
carrier_story: CFP-1192
parent_epic: CFP-1187
related_stories:
  - CFP-1192     # 본 carrier (Epic CFP-1187 Story-3, 운영 metric → PMOAgent input 회로 anchor)
  - CFP-1193     # Amendment 1 carrier (Epic CFP-1187 Story-4, 단계 2 two-part split)
  - CFP-1194     # Amendment 2 carrier (Epic CFP-1187 Story-5, 단계 2-a generalize — monitor-originated notification)
  - CFP-1187     # umbrella Epic — 운영 phase 신설
related_adrs:
  - ADR-104      # 직접 제약 (S1) — 운영 phase 1st-class 정의. §결정 5 (self-improving loop narrative + loop closure gate 위험 식별 + S6 carrier forward-ref) 가 본 ADR 이 normative codify 할 source / §결정 3 (0 API call) / §결정 4 (wrapper-N/A) 직접 계승
  - ADR-105      # 직접 제약 (S2) — 자동 rollback 도메인 재정의. §결정 3 안전장치 3 (사후 알림 → Issue 자동 발의 + PMOAgent escalation 의무) 의 escalation 회로 실 정의가 본 ADR (L96/L147 가 S3 를 carrier 지정)
  - ADR-045      # 직접 제약 — §D-9 (L402-427) cross-Story pattern_count ≥ 2 → ADR escalation forcing function + escalation_action 2-value enum (adr_draft_emitted | escalate_user). 본 ADR 답습 source + disjoint 명시 대상 (retro 도메인 vs 운영 phase 도메인 — ADR-045 본문 무변경)
  - ADR-064      # 직접 제약 — 모달 어휘 forbid-list (운영 신호 정량 우선 정합) + Trace 4 default parallel (S2 ∥ S3)
  - ADR-058      # 직접 제약 — §해소 기준 정량 명시 의무 + ratchet 강화 방향 (loop closure 원칙 약화 차단)
  - ADR-057      # 배경 — consumer overlay 정책 축소 불가 (loop closure threshold consumer 확장 가능 / 축소 불가) + "자동 재시도 금지" 패턴 (PMOAgent 실패 시 escalate)
  - ADR-083      # 배경 — filesystem-only signal invariant (0 API call constraint 동형 source, ADR-104 §결정 3 경유 계승)
  - ADR-084      # 배경 — pattern_count ≥ 2 재발 시 mechanical promote precedent (declaration-only Wave 1 retain pattern chain — file명 = ADR-084-numeric-space-sharing-channel-disjointness.md, sentinel clause L40-41)
  - ADR-086      # 배경 — deputy creation decision framework (본 S3 deputy 결정 CONDITIONAL 미spawn 정합)
  - ADR-054      # 배경 — doc-only fast-path (본 Story 는 비대상 — 신규 ADR 포함 → full-lane)
related_files:
  - docs/adr/ADR-RESERVATION.md                                                       # row 106 reserved → active 전환
  - docs/adr/ADR-104-operational-phase-definition.md                                  # §결정 5 forward-ref referent 충족 (의미 변경 0)
  - docs/adr/ADR-105-auto-rollback-redefinition.md                                    # §결정 3 안전장치 3 escalation 회로 실 정의 (의미 변경 0)
  - docs/adr/ADR-045-story-retro-mandatory-trigger.md                                 # §D-9 답습 source (의미 변경 0)
  - docs/domain-knowledge/domain/operational-phase/self-improving-loop.md             # narrative SSOT — 본 ADR 이 normative codify (file 무변경, forward-ref 충족만)
  - docs/domain-knowledge/domain/operational-phase/measurement-channel.md             # 단계 1 input 4종 신호 (에러율 / latency burn rate / regression / smoke·health) cross-ref
  - docs/kpi/operational-signal-history.jsonl                                         # KPI append-only state 구조 declare (실 write = S6 carrier)
  - docs/inter-plugin-contracts/pmo-output-v1.md                                      # disjoint 검증 대상 (PMOAgent 출력 vs operational-signal input)
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-082 §결정 6 / ADR-070 §D5 / ADR-076 / ADR-086 / ADR-097 / ADR-104 / ADR-105 retain pattern 답습 (behavioral directive only, self-improving loop = 회로 정책 정의 layer / 실 mechanism (PMOAgent 회로 wire + KPI append-only write + loop closure gate dedup·max-depth·escalate_user) = S6 carrier 가 신설 시 evidence-checks-registry row append; pattern_count >= 2 recurrence 시 follow-up CFP MUST promote to mechanical lint — ADR-084 precedent)
is_transitional: false  # permanent governance anchor — ADR-104/105 (운영 phase / 자동 rollback, is_transitional: false) 정합. self-improving loop 회로 정의 (회로 4단계 / ADR-045 §D-9 disjoint 답습 / KPI append-only 구조 / loop closure 3원칙 / contract 관계) 는 future 재사용 permanent. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합 — loop closure 원칙 축소 / OR→AND 완화 / 사용자 게이트 제거 시 약화 evidence-gate 의무)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (closure 원칙 추가 / 게이트 강도 강화 / disjoint 강도 강화). loop closure 원칙 축소 / 사용자 게이트 완화 = 약화 방향 → ADR-058 §결정 5 약화 evidence requirement 의무
amendment_log:
  - amendment: 1
    date: 2026-05-22
    carrier_story: CFP-1193   # Epic CFP-1187 Story-4 (rollback signal monitor mechanism)
    summary: "§결정 1 단계 2 two-part split — 단계 2-a (자동 rollback 직후 사후 알림 Issue 발의, 안전장치 3 동반분) = S4 早期 wire / 단계 2-b (일반 ops-signal Issue 자동 발의 + loop signature dedup gate 실 mechanism) = S6. cross-ADR reconcile: ADR-105 §결정 3 안전장치 3 (auto-rollback trigger 시 notification mechanism 必 동반 — 미충족 시 auto 진입 자격 없음) 이 단계 2 의 notification 부분을 S4 에 강제하는데, 원 §결정 1 표 + §경계 가 단계 2 전체를 S6 에 배정해 상호 모순 → split 으로 해소. §경계 line 162 S4/S5 row refine (S4 = 단계 1 + 단계 2-a notification only)."
    direction: strengthening   # ratchet 강화 (단계 2 boundary 정밀화 — S4 가 안전장치 3 의무 동반분을 早期 wire, S6 영역 축소 0 — 일반 ops-signal + dedup mechanism 은 S6 유지). cross-ADR 정합 강화.
    sunset_justification: null  # strengthening — 약화 0 (S6 일반 ops-signal Issue + dedup gate mechanism 무변경, S4 가 안전장치 3 notification 동반 의무분만 早期 wire). ADR-058 §결정 5 약화 evidence-gate 불요.
  - amendment: 2
    date: 2026-05-22
    carrier_story: CFP-1194   # Epic CFP-1187 Story-5 (regression/smoke·health monitor mechanism — S4 자매)
    summary: "§결정 1 단계 2-a generalize — 'auto-rollback 직후 사후 알림 Issue (S4)' → 'monitor-originated 사후/감지 알림 Issue (auto-rollback notification [S4] + regression/health detection notification [S5])'. trigger origin generalize = monitor 가 신호 감지 (auto-rollback trigger [S4] OR regression/health threshold·FAIL [S5]). 책임주체 = monitor 자신 (S4/S5 실 wire). Issue-level dedup 유지. §경계 S5 row refine (S5 = 단계 1 + 단계 2-a monitor-originated notification — auto-rollback 비동반 regression/health 신호도 자기 notification 동반분 早期 wire). 동인: 원 단계 2-a 가 'auto-rollback trigger event 동반분' 으로 한정 → S5 의 regression/health 신호 (auto-rollback 비동반) 가 단계 2-a 에도 (S6 미구현 상태) 단계 2-b 에도 안 맞는 boundary 공백 → generalize 로 해소. S4 Amendment 1 precedent 완전 동형 (S4 가 단계 2 전체 S6 배정에서 안전장치 3 의무 동반분만 단계 2-a split·早期 wire 한 패턴을 S5 가 monitor-originated notification generalize 로 답습)."
    direction: strengthening   # ratchet 강화 (단계 2-a scope generalize — S5 가 자기 신호 notification 동반분을 早期 wire, S6 단계 2-b 일반 ops-signal 회로 + Epic-level signature dedup gate 영역 축소 0). cross-Story 정합 강화 (S4/S5 자매 monitor notification path 동형화).
    sunset_justification: null  # strengthening — 약화 0 (단계 2-b 일반 ops-signal + Epic-level dedup gate mechanism 무변경, 단계 3·4 무변경. S5 가 monitor-originated notification 동반분만 早期 wire). ADR-058 §결정 5 약화 evidence-gate 불요.
  - amendment: 3
    date: 2026-05-22
    carrier_story: CFP-1243   # S4 producer enum literal conformance (operational-signal-v1 closed enum drift 해소)
    summary: "S4 producer (`scripts/check_rollback_signal.py`) emit literal conformance — burn-rate 임계 초과 시 emit 하던 비정규 literal `burn_rate` 를 §결정 3 closed enum 정규 value `latency_burn_rate` 로 conform. operational-signal-v1.md `signal_type` row note 가 deferred follow-up CFP 로 기록해 둔 producer↔contract alias drift (ADR-106 §결정 3 `latency_burn_rate` ↔ S4 producer `burn_rate`) 를 해소 — contract = SSOT, producer 가 conform (Option B). §결정 3 enum 내용 자체는 무변경 (이미 정규 `latency_burn_rate`). operational-signal-v1.md note 를 RESOLUTION 으로 갱신 (alias 없음 명시). 변경 = producer 1 string literal (L142) + producer docstring 1 line (L30) + contract editorial note + bats contract-binding guard TC 추가 (emit signal_type ∈ closed enum membership 보증)."
    direction: strengthening   # ratchet 강화 (corrective conformance — producer 가 contract closed enum 에 정렬, drift 해소. enum 축소 0 / 게이트 완화 0 / closure 원칙 변경 0). contract-binding guard TC 신설로 future drift 차단.
    sunset_justification: null  # strengthening — 약화 0 (§결정 3 closed enum 4-value 무변경, 단계 1~4 회로 무변경, loop closure 3원칙 무변경. producer 가 비정규 alias → 정규 enum value 로 conform 하는 corrective trail, additive). ADR-058 §결정 5 약화 evidence-gate 불요.
---

# ADR-106 — 운영 metric → PMOAgent input 회로 (self-improving loop)

## 상태

`Accepted` (2026-05-22 KST) — CFP-1192 carrier (Epic CFP-1187 Story-3, 운영 metric → PMOAgent input 회로 anchor). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-097 row 97 / ADR-104 row 104 / ADR-105 row 105 chief author precedent 정합).

## 컨텍스트

### 동인

S1 (ADR-104 §결정 5) 이 self-improving loop narrative 를 그렸다: "운영 신호 (에러율 급증 / 회귀 / rollback 발생) → 자동 Issue 생성 → PMOAgent escalation → 다음 Epic 후보". 그리고 self-improving-loop.md (S1 Phase 2 narrative, `docs/domain-knowledge/domain/operational-phase/self-improving-loop.md`) 의 "이 파일이 정의하지 않는 것" 표가 **`PMOAgent ↔ 운영 신호 회로 실 wire | S3`** 로 본 Story 를 carrier 로 명시한다. 즉 S1 은 narrative 만 그렸고, 그 narrative 를 **normative 정책으로 codify** 하는 것이 본 S3 의 책임이다.

운영 phase 는 배포검토 lane (일회성 검증, ADR-088) 이후 **계속 도는** 감시 영역이다 (S1 ADR-104 §결정 1). 그런데 운영 중 발견한 신호(에러율 급증 / 회귀 / 자동 rollback 발생)를 **그냥 흘려보내면** 운영의 효용이 절반에 그친다 — "감시했지만 다음 작업으로 이어지지 않는다". 따라서 신호를 codeforge 의 다음 작업거리로 **환류(feedback)** 시키는 회로가 필요하다: **운영 신호 → 자동 Issue → PMOAgent escalation → 다음 Epic 후보**.

또 S2 (ADR-105 §결정 3 안전장치 3, 동 file L96/L147) 가 자동 rollback 후 "사후 알림 → Issue 자동 발의 + PMOAgent escalation 의무" 만 declare 하면서 그 **escalation 회로 실 정의 = S3 영역** 으로 명시했다. 본 ADR 이 그 escalation 회로를 정의한다.

### 근본 mismatch + 외부 정당성

운영 phase 의 시간축 ongoing 성격 ↔ codeforge 의 Story-scoped delta + 종료 게이트 구조 사이의 mismatch (S1 ADR-104 §결정 2 — 운영 phase = lane 아니라 mechanism layer). self-improving loop 는 이 ongoing 신호를 **다음 작업거리로 환류**시키는 control loop 이나, 산업 autonomic computing (MAPE-K: Monitor → Analyze → Plan → Execute) 의 self-management 와 달리 **Execute (다음 Epic 개시) 가 자동이 아니다** — 단계 4 사용자 확인 게이트 의무 (§결정 1). 또 control theory 의 runaway feedback loop (positive feedback 무한 증폭) 위험을 closure 3원칙 (damping / hysteresis / rate limiting 답습) 으로 차단한다 (§결정 4).

이 회로는 codeforge 가 이미 검증한 패턴 ADR-045 §D-9 (cross-Story pattern_count ≥ 2 → ADR escalation forcing function) 를 답습한다. **단 도메인이 disjoint** 하다: ADR-045 = 개발 후 회고(retro) 도메인, 본 ADR = 배포 후 운영(operational) 도메인. 답습하되 중복이 아님을 §경계 에 disjoint 표로 명시한다 (governance 자기참조 정합 — §결정 2).

## 결정

운영 metric → PMOAgent input 회로 (self-improving loop) 를 codeforge 의 normative 정책으로 codify 한다. 정의는 아래 5 결정으로 구성된다. 본 ADR 이 normative SSOT 이고, `docs/domain-knowledge/domain/operational-phase/self-improving-loop.md` (S1 Phase 2 narrative) 는 서술적 elaboration 이다 — ADR 이 결정, domain-knowledge 가 해설. **두 source (ADR-104 §결정 5 / self-improving-loop.md) 본문은 무변경** — 본 ADR 이 forward-ref referent 를 채울 뿐이다.

### §결정 1 — 회로 4단계 normative codify (단계별 trigger / 책임 주체 / 산출)

self-improving loop = 운영 phase 에서 회수한 신호를 codeforge 의 다음 작업거리(Epic 후보)로 환류시키는 control loop. 회로 4단계:

```
[단계 1: 운영 신호 회수] → [단계 2: 자동 Issue 생성] → [단계 3: PMOAgent escalation] → [단계 4: 다음 Epic 후보]
```

ADR-104 §결정 5 narrative 의 normative codify (trigger / 책임 주체 / 산출 표):

| 단계 | trigger | 책임 주체 | 산출 | 정량 / 정합 기준 |
|---|---|---|---|---|
| **단계 1 — 운영 신호 회수** | measurement-channel.md 4종 신호 (에러율 / latency burn rate / regression / smoke·health) 중 임계 초과 또는 FAIL | consumer 측 cron workflow (S4~S5 실 구현) | 신호 event (signature + 측정값 + 임계값) | 정량 우선 (ADR-064 모달 어휘 금지) — signature = 신호유형 + 측정값 + window 수치 |
| **단계 2-a — monitor-originated 사후/감지 알림 Issue** (Amendment 1 split + **Amendment 2 generalize**, **S4 + S5** 早期 wire) | monitor 가 신호 감지 (auto-rollback **trigger 발동** [S4, 안전장치 4 AND 충족 후 hook trigger] OR regression/health **임계 초과·FAIL** [S5, rollback 비동반]) | mechanism (monitor 자신 → Issue 자동 발의 — **S4 auto-rollback notification** [CFP-1193] + **S5 regression/health detection notification** [CFP-1194] 실 wire) | GitHub Issue (`ops-signal` label, 본문에 측정값 / baseline / 임계값 수치 + signature 기록) | **monitor-originated notification 동반분** — (S4) ADR-105 §결정 3 안전장치 3 auto-rollback trigger 시 notification mechanism 必 동반 (무음 rollback 금지) / (S5) regression/health 신호 감지 시 자기 notification 동반분 (무음 감지 금지). Issue-level dedup (단일 신호 24h 1 Issue) 적용 |
| **단계 2-b — 일반 ops-signal Issue 자동 발의** (Amendment 1 split, **S6**) | 단계 1 신호 임계 초과 (auto-rollback trigger 와 disjoint — 일반 운영 신호 회로) | mechanism (cron workflow → Issue 자동 발의, **S6 실 wire**) | GitHub Issue (`ops-signal` label) | loop signature dedup gate 실 mechanism (Epic-level closure — 동일 signature open Issue / 진행 Epic 존재 시 억제, §결정 4 원칙 (a), **실 mechanism = S6**) |
| **단계 3 — PMOAgent escalation** | `ops-signal` label Issue 감지 | PMOAgent (cross-cutting) | pattern_count 집계 → ≥ 2 시 ADR escalation forcing function (§결정 2 ADR-045 §D-9 답습) + retro 병합 기록 | pattern_count ≥ 2 (ADR-045 §D-9 threshold 답습) + escalation_action 2-value enum (adr_draft_emitted \| escalate_user) |
| **단계 4 — 다음 Epic 후보** | PMOAgent escalation 발의 | Orchestrator → 사용자 | `codeforge:story-epic-flow-preflight` 로 Story / Epic flow 결정 (사용자 확인 게이트) | **사용자 확인 게이트 의무** (완전 자동 Epic 개시 금지 — §결정 2 ADR-045 §D-9 인간 게이트 답습) |

**회로 닫힘 normative — self-improving ≠ self-executing**: 4 단계 모두 인간 게이트(단계 4 사용자 확인)로 닫힌다. **완전 자동화로 Epic 을 개시하지 않는다.** 산업 MAPE-K 의 self-healing (Execute 자동) 과의 핵심 차이 — codeforge 의 self-improving 은 Execute(다음 Epic 개시)가 자동이 아니다. 이는 governance 자동 변조 차단 (자동 신호 → 자동 Epic → 자동 governance 변경 chain 차단) 의 보안 핵심이기도 하다.

### §결정 2 — ADR-045 §D-9 disjoint 답습 (도메인 disjoint 명시 의무)

단계 3 PMOAgent escalation 은 ADR-045 §D-9 (`docs/adr/ADR-045-story-retro-mandatory-trigger.md` L402-427) 패턴을 답습한다 — "PMOAgent cross-Story pattern_count ≥ threshold 2 검출 시 ADR escalation forcing function + escalation_action 2-value enum (adr_draft_emitted | escalate_user)". 그러나 **패턴은 동형이되 입력 도메인은 disjoint** 하다. §경계 의 disjoint 표가 이를 명시한다. **"ADR-045 와 동일" 단일 진술은 금지** — 두 forcing function 이 같은 PMOAgent escalation 메커니즘을 공유하나, 입력 corpus (retro corpus vs operational signal) 가 disjoint 함을 표로 분리 명시해야 한다.

**ADR-045 본문 무변경** — ADR-045 §D-9 는 retro 도메인 정의를 유지한다. 본 ADR 이 운영 도메인 disjoint 를 §경계 에 추가할 뿐이다.

### §결정 3 — KPI append-only state 구조 declare (실 write = S6 carrier)

운영 신호 이력은 기존 `docs/kpi/` 의 `.json` (state summary) + `.jsonl` (append-only history) 쌍 패턴 (`rate-limit-fallback.json` + `rate-limit-fallback-history.jsonl`) 을 답습하여 `docs/kpi/operational-signal-history.jsonl` 로 누적한다. 구조 (10 field) 를 declare 한다:

```jsonl
# docs/kpi/operational-signal-history.jsonl (append-only — 본 ADR = 구조 declare, 실 write = S6)
{"signal_signature": "<신호유형>:<측정값>:<window>", "signal_type": "error_rate|latency_burn_rate|regression|smoke_health", "measured_value": <number>, "threshold": <number>, "window": "<숫자+단위>", "detected_at_kst": "YYYY-MM-DDTHH:MM:SS+09:00", "issue_ref": "<owner>/<repo>#<N>", "escalation_action": "adr_draft_emitted|escalate_user|none", "pattern_count": <int>, "loop_depth": <int>}
```

state summary `.json` (operational-signal-rate.json 등 — S6 결정) 은 history 의 rolling window 집계만 보유 (rate-limit-fallback.json 패턴 — `schema_version` / `history_file` pointer / `measured_at` / `window_months` / 집계 metric / `gate_status`).

**append-only invariant**: 측정값은 덮어쓰지 않고 누적만 한다 (사용자 §1 verbatim "측정값은 덮어쓰지 않고 누적만 하는 방식(append-only)"). 이는 신호 이력 무결성 (변조 차단 / 손실 0 audit trail) 의 보안 기능이기도 하다 (§경계 보안 trust boundary 참조). **본 ADR = 구조만 declare** — 실 write mechanism (cron 이 jsonl append + .json 갱신, ADR-045 §D-4 Pattern A SHA-based optimistic concurrency 정합) = **S6 (#1195) carrier**.

### §결정 4 — loop closure 3원칙 (무한 발산 방지 — 원칙 정의 only, mechanism = S6)

self-improving-loop.md (S1) 가 무한 발산 위험(동일 신호 반복 / Issue 폭발 / Epic 무한 중첩, 위험 수준 MEDIUM)을 식별하고 closure gate 를 S6 forward-ref 했다. 본 ADR 은 closure 3원칙을 normative 정의한다 (실 mechanism = S6):

| 원칙 | 정의 | 무한 발산 방지 대상 | 실 mechanism (S6) |
|---|---|---|---|
| **(a) dedup** | 동일 signature 신호에 대해 이미 open Issue / 진행 중 Epic 이 존재하면 새 Issue / Epic 발의 차단 | 동일 root cause 신호 반복 발의 (root cause 미해소 상태 누적) | dedup gate — signature 기준 open Issue 존재 check (S6) |
| **(b) max-depth** | loop 깊이 카운터 (신호 → Issue → Epic → 배포 → 재신호 cycle 횟수 상한). 상한 초과 시 자동 발의 중단 | Epic 무한 중첩 (loop 가 다음 Epic 을 낳고 그 배포가 재신호) | max-depth counter (KPI `loop_depth` field 추적) (S6) |
| **(c) escalate_user** | max-depth 초과 또는 dedup 충돌 누적 시 자동 Issue 중단 + 사용자 ESCALATE (ADR-045 §D-9 escalation_action: escalate_user 답습) | Issue 폭발 (noise 과잉) | escalate_user gate (자동 발의 중단 + 사용자 통지) (S6) |

**원칙 강도**: 3원칙 모두 **OR 조건으로 발동** (하나라도 trip 되면 자동 발의 억제 — 보수적). consumer overlay 가 threshold (dedup window / max-depth 상한) 를 **확장 가능하나 축소 불가** (ADR-057 정합 — 안전망 약화 차단). 외부 정당성 — control theory damping (dedup = hysteresis 동일 입력 억제 / max-depth = rate limiting 횟수 상한 / escalate_user = human circuit breaker 인간 차단기). **본 ADR = 원칙만 정의** — 실 closure gate mechanism (dedup gate / max-depth counter / escalate_user wire) = **S6 (#1195) carrier**.

### §결정 5 — operational-signal contract 결정 (defer — 회로/관계 declare, 실 wiring = S6)

`docs/inter-plugin-contracts/` (git ls-tree origin/main 검증) 에 `operational-signal-v1` 은 **부재**다. 운영 신호 input schema (cron / monitor → PMOAgent) 와 기존 `pmo-output-v1` (v1.2, PMOAgent → Orchestrator 출력) 는 **방향 + 도메인 disjoint** 다 (input vs output / 운영 신호 event vs retro·Epic 산출).

**결정 = defer (신설하지 않고 관계만 declare)**. 두 선택지 ((A) operational-signal-v1 신설 / (B) pmo-output-v1 v1.3 확장) 중 본 Phase 1 에서는 **둘 다 채택하지 않고**, 본 ADR 에 회로/관계만 declare 하고 실 contract wiring 을 **S6 (#1195) carrier** 로 defer 한다. 근거:

1. **Phase 1 churn 최소화** — operational-signal-v1 신설 시 MANIFEST.yaml row append + canonical_repo 결정 + sibling sync (pmo_output canonical = `mclayer/plugin-codeforge-pmo`, sibling sync 대상) 비용 발생. 본 S3 = 정책 정의 Story (코드 0) — contract body 가 실제 소비될 시점 = S6 mechanism wire 시점이므로 그때 신설이 자연스럽다.
2. **CFP-1059 placeholder precedent** — `deploy_output` / `deploy_review_output` 가 MANIFEST.yaml 에 `canonical_repo: ... # TBD — lane plugin seed 신설 후 confirm` placeholder 로 declare 만 하고 body wire 를 sub-Story carrier 로 defer 한 precedent 답습.
3. **disjoint 검증 완료** — 신설 vs 확장 결정에 필요한 disjoint (input vs output 방향 / 운영 vs retro 도메인) 는 §경계 에 검증 표로 명시. S6 가 wiring 시 신설(SSOT 명료) 권고 — 단계 3 escalation 출력은 기존 `pmo-output-v1` `cross_story_pattern_adr_trigger` field 재사용 가능, 단계 1→3 input 은 신규 operational-signal-v1 가 자연스럽다.

**wrapper-N/A / 0 API call 계승** — 본 회로의 실 측정 (단계 1) 은 ADR-104 §결정 3 (0 API call, filesystem / cron) + §결정 4 (wrapper-self-app N/A) 를 계승한다. self-improving loop 실 wire / KPI write = consumer 한정, 신호 측정 = filesystem / cron (실시간 telemetry API 미사용, ADR-083 동형). wrapper repo 는 운영 phase mechanism dogfood 불가 (production 환경 부재) — declarative SSOT 만 검증.

## 결과

### 긍정

- 운영 신호가 다음 작업거리로 환류되는 self-improving loop 가 normative 로 정의되어 "감시는 하나 다음으로 이어지지 않는" 효용 누락이 해소된다.
- ADR-045 §D-9 검증된 패턴 (PMOAgent escalation / threshold 2 / escalation_action enum) 을 재사용해 신규 메커니즘 발명을 회피한다 (도메인 disjoint 만 추가).
- 단계 4 사용자 확인 게이트 + closure 3원칙으로 self-improving 이 self-executing (완전 자동 governance 변조) 으로 폭주하지 않는다.
- KPI append-only invariant 로 신호 이력 무결성 (변조 차단 / 손실 0 audit trail) 보존.
- contract defer 로 Phase 1 churn (MANIFEST + sibling sync) 회피.

### 부정 / trade-off

- **무한 발산 위험 (EC-1)** — self-improving loop 는 "신호 → Epic → 배포 → 재신호 → 또 Epic …" 의 무한 자기증식 위험을 안고 있다 (위험 수준 MEDIUM — 사용자 확인 게이트가 있으나 "진행해" 반복 시 실질적 무한 동조). 본 ADR 은 closure 3원칙 정의로 위험을 식별·억제하나, 실 closure gate mechanism 은 S6 까지 부재 (S4~S5 cron 의 수동 throttle 임시 안전망). S6 전 운영 phase 활성화 시 발산 위험이 잔존한다.
- **declaration-only** — 본 ADR 은 회로 정책 정의 layer. 실 mechanism (PMOAgent 회로 wire / KPI append-only write / closure gate) = S6 carrier (`mechanical_enforcement_actions: []`). pattern_count ≥ 2 recurrence 시 follow-up CFP MUST promote to mechanical lint (ADR-084 precedent).
- contract defer 로 인해 operational-signal typed schema 가 S6 까지 부재 — 그 사이 단계 1→3 input 은 untyped (Issue body 평문) 로 흐른다.

### Edge Case 처리 요약 (요구사항 §5.2)

| EC | 시나리오 | 기대 동작 |
|---|---|---|
| EC-1 | 무한 발산 | closure 3원칙 발동 (max-depth 초과 시 escalate_user). 실 gate = S6 |
| EC-2 | 동일 signature 중복 신호 | dedup gate 발동 (open Issue / 진행 Epic 존재 시 억제). 실 = S6 |
| EC-3 | escalation overload (noise 과잉) | max-depth / dedup OR 발동 → escalate_user |
| EC-4 | signal vs noise (false positive) | 정량 신호 (measured_value + window — burn rate = 소진 속도 순간값 아님) 가 spike·sustained 구분 + dedup 흡수 |
| EC-5 | PMOAgent 부재 / 실패 | escalate (즉시 사용자 통지) + **자동 재시도 금지** (ADR-057 정합). 신호 event 는 KPI jsonl append-only 누적 → 손실 0 |
| EC-6 | 사용자 무응답 (단계 4 게이트 무한 대기) | 신호 event KPI jsonl 누적 보존 (손실 0). 다음 Epic 미개시 = 정상 (인간 게이트 = 의도적 보수) |
| EC-7 | KPI jsonl write 경합 (복수 cron tick) | ADR-045 §D-4 Pattern A (SHA-based optimistic concurrency) 답습. 실 write 경합 처리 = S6 |

## 경계 (boundary)

### 본 ADR scope

- **본 ADR scope** = self-improving loop **회로 정책 정의** (회로 4단계 trigger / 책임주체 / 산출 + ADR-045 §D-9 disjoint 답습 + KPI append-only 구조 declare + loop closure 3원칙 + operational-signal contract 관계 defer). declarative SSOT.
- **S1 (ADR-104 §결정 5 / self-improving-loop.md)** = self-improving loop **narrative** (회로 4단계 서술 + closure gate 위험 식별 + S6 forward-ref). 본 ADR 이 narrative 를 normative codify (두 source 본문 **무변경** — forward-ref referent 충족만).
- **S2 (ADR-105 §결정 3 안전장치 3)** = 자동 rollback 후 "사후 알림 → Issue 자동 발의 + PMOAgent escalation 의무" **declare**. 본 ADR 이 그 escalation 회로 실 정의.
- **S6 (#1195)** = self-improving loop **실 mechanism** (PMOAgent 회로 실 wire / KPI append-only state 실 write / loop closure gate 실 구현 dedup·max-depth·escalate_user / **단계 2-b 일반 ops-signal Issue 자동 발의 + Epic-level signature dedup gate** (Amendment 1) / operational-signal contract 실 신설·wiring). 본 ADR 은 회로 4단계·closure 3원칙·KPI 구조·contract 관계의 **정의만** — 실 mechanism / workflow yml / script / contract body 신설 0.
- **S4 / S5** = ongoing monitor mechanism (단계 1 신호 회수 실 구현 — S4 자동 rollback signal monitor [신호 1·2 에러율/burn rate] / S5 regression·smoke·health monitor [신호 3·4 regression/smoke·health]). 본 ADR 은 단계 1 input 4종 신호 (measurement-channel.md) cross-ref only.
  - **Amendment 1 (CFP-1193) 후 S4 = 단계 1 + 단계 2-a (자동 rollback 직후 사후 알림 Issue, ADR-105 §결정 3 안전장치 3 의무 동반분) 까지 실 wire** — auto-rollback trigger 시 notification mechanism 必 동반 강제 (cross-ADR reconcile).
  - **Amendment 2 (CFP-1194) 후 S5 = 단계 1 + 단계 2-a (regression/health 감지 직후 monitor-originated 알림 Issue) 까지 실 wire** — S5 의 regression/health 신호 (auto-rollback 비동반) 도 자기 monitor-originated notification 동반분을 早期 wire (무음 감지 금지). S5 dedup 성격 = Issue-level (단발 신호 24h 1 Issue, S4 단계 2-a 동형).
  - 단계 2-b (일반 ops-signal Issue 회로 + Epic-level signature dedup gate mechanism) + 단계 3 + 단계 4 = **S6 유지** (Amendment 1·2 모두 S6 영역 무변경).
- **단계 2-a ↔ 단계 2-b disjoint (Amendment 1·2)** — 단계 2-a = **monitor-originated notification** (monitor 가 자기 신호 감지 직후 발의 — S4 auto-rollback trigger event 동반 [ADR-105 안전장치 3 강제] OR S5 regression/health 임계 초과·FAIL 동반, 양자 모두 Issue-level dedup) / 단계 2-b = **일반 ops-signal Issue 자동 발의 회로 + Epic-level signature dedup gate** (S6 — loop closure machinery, 특정 monitor 의 self-notification 이 아니라 회로 전체의 Epic-level closure 기제). 두 path 는 **origin disjoint** (특정 monitor 의 즉시 self-notification [2-a] vs 회로 차원 Epic-level closure gate [2-b]) — S4·S5 는 각자 monitor-originated notification 동반분만 早期 wire (단계 2-a), S6 가 회로 차원 closure gate (단계 2-b) 신설. S6 일반 회로 + Epic-level dedup gate 는 Amendment 1·2 모두 무변경.

### ADR-045 §D-9 ↔ 본 ADR disjoint 표 (§결정 2 — "동일" 단일 진술 금지)

| 항목 | ADR-045 §D-9 (retro / 회고 도메인) | ADR-106 self-improving loop (운영 phase 도메인) | disjoint 여부 |
|---|---|---|---|
| **입력 도메인** | 개발 후 회고 (retro) — Story 완료 후 PMOAgent 회고 corpus | 배포 후 운영 (operational) — 배포검토 이후 ongoing 신호 | **disjoint** (시간축 위치 다름 — 회고 시점 vs 배포 후 ongoing) |
| **트리거** | Story 완료 retro write 시점 | 운영 신호 임계 초과 (cron tick) | **disjoint** |
| **집계 단위** | cross-Story pattern_count (review-verdict anchor_id) | 동일 신호 signature pattern_count (signal type) | **disjoint** (식별자 종류 다름) |
| **감지 주체** | PMOAgent (retro mandatory trigger) | cron workflow → 자동 Issue → PMOAgent | 답습 (PMOAgent escalation 공통) |
| **threshold** | N = 2 (Google SRE / ITIL / NASA ASRS) | N = 2 (동일 industry lower bound 답습) | 답습 (값 동일) |
| **escalation_action** | adr_draft_emitted \| escalate_user | adr_draft_emitted \| escalate_user (답습) | 답습 (enum 동일) |
| **인간 게이트** | 있음 | 있음 (단계 4 사용자 확인) | 답습 (구조 동일) |

**disjoint normative**: ADR-045 = "회고에서 발견한 cross-Story pattern → ADR" / 본 ADR = "운영에서 회수한 cross-signal pattern → 다음 Epic". **답습하되 중복이 아니다** — 같은 PMOAgent escalation 메커니즘 (threshold 2 / escalation_action enum / 인간 게이트) 을 공유하나 **입력 도메인 (retro corpus vs operational signal) 이 disjoint**. ADR-045 §D-9 본문은 무변경 (retro 도메인 유지).

### pmo-output-v1 ↔ operational-signal contract disjoint 검증 표 (§결정 5)

| contract | 방향 | 도메인 | 본 ADR 관계 |
|---|---|---|---|
| **pmo-output-v1** (v1.2, 실재) | PMOAgent → Orchestrator (출력) | retro / Epic 산출 audit + ADR proposal | 기존 — `cross_story_pattern_adr_trigger` field 가 단계 3 escalation 출력 carrier 로 재사용 후보 |
| **operational-signal-v1** (부재 — defer) | cron workflow / monitor → PMOAgent (input) | 운영 신호 event (signature / 측정값 / 임계 / signal type) | 신설 defer — pmo-output 과 방향 + 도메인 disjoint (input vs output). 실 신설 = S6 |

### 보안 trust boundary (§7.1 / §7.5 light scope — declarative)

- **자동 Issue 발의 권한 (단계 2, §7.1)** — cron workflow → GitHub Issue 자동 발의는 consumer repo 내부 권한 (GitHub Actions token issues:write) 으로 제한된다. 권한 남용 위협 (Issue 폭발 / 신호 위조 → 거짓 Epic / governance 자동 변경 chain) 은 closure 3원칙 (dedup spam 차단 / max-depth 권한 상승 chain 차단 / escalate_user human circuit breaker) + 단계 4 사용자 확인 게이트로 완화. 자동 Issue 발의 권한 = consumer repo scope 한정 (external 발의 불가).
- **신호 출처 무결성 (단계 1, §7.1)** — 0 API call constraint (ADR-104 §결정 3, filesystem / cron) 가 신호 출처를 filesystem 으로 제한 → external network 위조 표면 축소 (보안 이점). KPI jsonl append-only invariant (§결정 3) 가 신호 이력 무결성 (변조 차단 / 손실 0 audit trail) 보장.
- **wrapper-N/A invariant (§7.5)** — ADR-104 §결정 4 계승. wrapper repo 에 자동 Issue 발의 workflow 가 trigger 되지 않도록 declare-time exemption → wrapper governance 오염 차단.
- **fail-safe (EC-5, §7.5)** — PMOAgent escalation 실패 시 자동 재시도 금지 (ADR-057) + 즉시 사용자 통지 + 신호 손실 0 (append-only). 실패 시 자동 진행 금지 = fail-safe.

## 해소 기준

N/A — permanent policy

`is_transitional: false` permanent governance anchor. self-improving loop 회로 정의 (회로 4단계 / ADR-045 §D-9 disjoint 답습 / KPI append-only 구조 / loop closure 3원칙 / operational-signal contract 관계) 는 future 재사용 permanent. amendment 시 ratchet 강화 방향만 허용 (closure 원칙 추가 / 게이트 강도 강화 / disjoint 강도 강화). loop closure 원칙 축소 / OR→AND 완화 / 사용자 게이트 제거 = 약화 방향 → ADR-058 §결정 5 약화 evidence requirement 의무.

## 관련 ADR

- **ADR-104 (S1)** — 운영 phase 1st-class 정의. §결정 5 self-improving loop narrative (본 ADR 이 normative codify) + §결정 3 (0 API call) / §결정 4 (wrapper-N/A) 계승
- **ADR-105 (S2)** — 자동 rollback 도메인 재정의. §결정 3 안전장치 3 (사후 알림 → escalation 의무) 의 escalation 회로 실 정의가 본 ADR
- **ADR-045** — §D-9 cross-Story pattern → ADR escalation forcing function + escalation_action 2-value enum (답습 source + disjoint 명시 대상, 본문 무변경)
- **ADR-064** — 모달 어휘 forbid-list (운영 신호 정량 우선) + Trace 4 default parallel (S2 ∥ S3)
- **ADR-058 §결정 5** — §해소 기준 정량 명시 + ratchet 강화 방향 (loop closure 원칙 약화 차단)
- **ADR-057** — consumer overlay 축소 불가 (closure threshold 확장 가능 / 축소 불가) + "자동 재시도 금지" (PMOAgent 실패 시 escalate)
- **ADR-083** — filesystem-only signal invariant (0 API call 동형 — ADR-104 §결정 3 경유 계승)
- **ADR-084** — pattern_count ≥ 2 재발 시 mechanical promote precedent (declaration-only Wave 1 retain pattern chain)
- **ADR-054** — doc-only fast-path (본 Story 비대상 — 신규 ADR 포함 → full-lane)

## 관련 파일

- `docs/adr/ADR-RESERVATION.md` — row 106 reserved → active 전환 (본 commit)
- `docs/adr/ADR-104-operational-phase-definition.md` — §결정 5 forward-ref referent 충족 (의미 변경 0)
- `docs/adr/ADR-105-auto-rollback-redefinition.md` — §결정 3 안전장치 3 escalation 회로 실 정의 (의미 변경 0)
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — §D-9 답습 source (의미 변경 0)
- `docs/domain-knowledge/domain/operational-phase/self-improving-loop.md` — narrative SSOT, 본 ADR 이 normative codify (file 무변경, forward-ref 충족만)
- `docs/domain-knowledge/domain/operational-phase/measurement-channel.md` — 단계 1 input 4종 신호 cross-ref
- `docs/kpi/operational-signal-history.jsonl` — KPI append-only state 구조 declare (실 write = S6 carrier)
- `docs/inter-plugin-contracts/pmo-output-v1.md` — disjoint 검증 대상 (PMOAgent 출력 vs operational-signal input)

## 변경 이력

| 날짜 (KST) | CFP | 변경 |
|---|---|---|
| 2026-05-22 | CFP-1192 | 최초 작성 — 운영 metric → PMOAgent input 회로 (self-improving loop normative codify: 회로 4단계 trigger/책임주체/산출 표 + ADR-045 §D-9 disjoint 답습 표 + KPI append-only state 구조 declare + loop closure 3원칙 OR 발동 + operational-signal contract defer (CFP-1059 placeholder precedent) + self-improving ≠ self-executing 단계 4 사용자 게이트 + 보안 trust boundary §7.1/§7.5). ArchitectAgent chief author direct write. Epic CFP-1187 Story-3. ADR-104 / ADR-105 / ADR-045 / self-improving-loop.md 본문 무변경 invariant. |
| 2026-05-22 | CFP-1193 | **Amendment 1** — §결정 1 표 단계 2 two-part split (단계 2-a 자동 rollback 직후 사후 알림 Issue = **S4** 早期 wire / 단계 2-b 일반 ops-signal Issue + signature dedup gate = S6) + §경계 S4/S5 row refine + 단계 2-a↔2-b disjoint 진술 추가. **cross-ADR reconcile** — ADR-105 §결정 3 안전장치 3 (auto-rollback trigger 시 notification mechanism 必 동반, 미충족 시 auto 진입 자격 없음) 이 단계 2 의 notification 부분을 S4 에 강제하나 원 §결정 1 표 + §경계 가 단계 2 전체를 S6 배정 → 모순 해소. strengthening (S6 일반 회로 + dedup mechanism 무변경, S4 가 안전장치 3 의무 동반분만 早期 wire). ADR-104/105 본문 무변경. ArchitectAgent chief author (CFP-1193 설계리뷰 FIX iter1). |
| 2026-05-22 | CFP-1194 | **Amendment 2** — §결정 1 표 단계 2-a generalize ("자동 rollback 직후 사후 알림 Issue (S4)" → "monitor-originated 사후/감지 알림 Issue (auto-rollback notification [S4] + regression/health detection notification [S5])") + trigger origin generalize (monitor 신호 감지: auto-rollback trigger [S4] OR regression/health 임계·FAIL [S5]) + 책임주체 = monitor 자신 (S4/S5 실 wire) + §경계 S5 row refine (S5 = 단계 1 + 단계 2-a monitor-originated notification 早期 wire) + 단계 2-a↔2-b disjoint 재정식화 (2-a = monitor-originated self-notification / 2-b = 회로 차원 Epic-level closure gate, S6). **boundary 공백 해소** — 원 단계 2-a 가 "auto-rollback trigger event 동반분" 한정 → S5 regression/health 신호 (auto-rollback 비동반) 가 단계 2-a 에도 (S6 미구현) 단계 2-b 에도 안 맞는 공백 → generalize 로 해소. **S4 Amendment 1 precedent 완전 동형** (단계 2 전체 S6 배정 → 안전장치 3 의무 동반분만 단계 2-a split·早期 wire 패턴을 S5 가 monitor-originated notification generalize 로 답습). strengthening (단계 2-b 일반 ops-signal + Epic-level dedup gate + 단계 3·4 무변경, S5 가 자기 notification 동반분만 早期 wire). ADR-104/105 본문 무변경. ArchitectAgent chief author (CFP-1194 설계 lane). |
| 2026-05-22 | CFP-1243 | **Amendment 3** — S4 producer (`scripts/check_rollback_signal.py`) emit literal conformance. burn-rate 임계 초과 시 emit 하던 비정규 literal `burn_rate` 를 §결정 3 closed enum 정규 value `latency_burn_rate` 로 conform (Option B — contract = SSOT, producer 가 conform). operational-signal-v1.md `signal_type` row note 가 deferred follow-up CFP 로 기록해 둔 producer↔contract alias drift 해소 + note 를 RESOLUTION 으로 갱신. §결정 3 closed enum 4-value 자체는 무변경 (이미 정규). 변경 = producer 1 string literal (L142) + producer docstring 1 line (L30) + contract editorial note + bats contract-binding guard TC (emit signal_type ∈ closed enum membership 보증, future drift 차단). strengthening (corrective conformance — 약화 0, additive trail). ADR-104/105 / §결정 3 enum 무변경. |
