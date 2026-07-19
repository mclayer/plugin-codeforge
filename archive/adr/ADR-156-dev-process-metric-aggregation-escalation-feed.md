---
adr_number: 156
title: dev-process metric aggregation + §D-9 dev-domain escalation feed circuit — A substrate(ADR-155) 위 downstream 집계 정책 (6 지표 산식·경계 + producer↔decider 분리 + honest-degrade 천장 + 3-domain disjoint feed EXTEND, closure machinery 미복제)
status: Active
category: governance
date: 2026-07-15
carrier_story: CFP-2688
parent_epic: CFP-2686
related_stories:
  - CFP-2688     # 본 carrier (Epic #2686 Story B — dev-process 지표 aggregation)
  - CFP-2687     # 선행 substrate (Story A — ADR-155 dev-process-event-v1)
  - CFP-2686     # umbrella Epic
related_adrs:
  - ADR-155      # 직접 제약 (substrate SSOT) — dev-process observability substrate + dev-process-event-v1. B = downstream consumer, mining port read-only. §15.2 5th boundary invariant(semantic-evidence-aggregation) 상속
  - ADR-106      # 직접 제약 (circuit template) — operational-signal → PMOAgent circuit. NEW ADR precedent(§D-9 amendment 아닌 신규 ADR 로 disjoint feed 추가, ADR-045 본문 무변경). B = 동형이되 dev-process 축 disjoint. ★closure machinery(dedup/max-depth/escalate_user) 미복제 — B = passive read-time feeder
  - ADR-045      # 직접 제약 — §D-9 cross-Story pattern_count ≥ 2 → ADR escalation forcing function + escalation_action 2-value enum. B = EXTEND(신규 disjoint feed), 산문 corpus supersede 금지, 본문 무변경 invariant
  - ADR-163      # 직접 제약 — measurement channel. dev-process-event = 9th channel. 0-API-call 상속 / measure≠classify tier / token-cost upstream = spawn-event-v1
  - ADR-104      # 직접 제약 (경계) — operational-phase 정의. dev-process ⊥ operational-phase disjoint axis, wrapper-N/A false-block 방지
  - ADR-119      # 직접 제약 — research-before-claims / honest-degrade 천장(인과 주장 금지, 재발률=측정치, exact-count 금지). self-referential dogfood 7연속 이력 대응
  - ADR-140      # 배경 — write-time hygiene(Path B reject 근거, port-isolation break + DRY 위반)
  - ADR-061      # 배경 — python portability(UTC-Z parser Z-strip 3.11+)
related_files:
  - archive/adr/ADR-RESERVATION.md                                              # row 156 append
  - docs/inter-plugin-contracts/dev-process-event-v1.md                         # A substrate 계약 (read-only 소비, 의미 변경 0)
  - scripts/lib/query_dev_process_event.py                                      # A mining port (B 유일 read 진입점, 의미 변경 0)
  - scripts/lib/aggregate_stop_event.py                                         # 집계기 archetype (의미 변경 0)
  - scripts/lib/spawn_event_pricing.py                                          # token-cost 원천 helper (재사용, 의미 변경 0)
  - archive/adr/ADR-045-story-retro-mandatory-trigger.md                        # §D-9 EXTEND source (본문 무변경 invariant)
  - archive/adr/ADR-106-operational-signal-pmo-input-circuit.md                 # circuit template (본문 무변경)
  - docs/inter-plugin-contracts/pmo-output-v1.md                                # cross_story_pattern_adr_trigger additive 재사용(계약 무변경)
  - docs/architecture/codeforge-family.md                                       # living-arch data_flow + interfaces node
mechanical_enforcement_actions: []  # declaration-only Phase 1 — ADR-082 §결정 6 / ADR-070 §D5 / ADR-106 retain pattern 답습. B 집계 정책 정의 layer / 실 mechanism(aggregate_dev_process_event.py + 6 compute fn + KPI dual-file write + lint/self-test) = 동일 Story Phase 2 carrier(CFP-2688 §8-§11). pattern_count >= 2 recurrence 시 follow-up CFP MUST promote to mechanical lint (ADR-084 precedent)
is_transitional: false  # permanent governance anchor — ADR-155/106/045(substrate/circuit/escalation, is_transitional: false) 정합. dev-process metric 집계 정책(6 지표 산식·경계 + producer↔decider + honest-degrade 천장 + 3-domain disjoint feed) = future 재사용 permanent. 약화 방향 차단 ratchet(ADR-058 §결정 5 — honest-degrade 천장 완화 / producer↔decider 경계 제거 / disjoint 강도 축소 = 약화 evidence-gate 의무)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만(천장 강화 / 경계 강화 / disjoint 강화). honest-degrade 완화 / over-claim 허용 = 약화 방향 → ADR-058 §결정 5 약화 evidence requirement 의무
---

# ADR-156 — dev-process metric aggregation + §D-9 dev-domain escalation feed circuit

## 상태

`Active` (2026-07-15 KST) — CFP-2688 carrier (Epic #2686 Story B — dev-process 지표 aggregation). ArchitectAgent chief author direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved` 미경유 직접 `active` (chief author scope, ADR-155 row 155 precedent 정합).

## 컨텍스트

### 동인

A(#2687, ADR-155)가 `dev-process-event-v1` substrate(9번째 Tier-3 persistent channel + 2계층 index/blob + 4-ID freeze + 결점 taxonomy 4-tuple + mining port)를 freeze 했으나, 그 위 **downstream 집계 = dev-process 지표**는 별 wave 로 명시 defer 됐다(A OOS 표: "B(#2688): 지표 계산식·사이클타임 산식·FIX 반복수 집계 알고리즘" `[verified: dev-process-event-v1.md:361-362]`). B(#2688)가 그 집계 정책을 정의한다.

**landing ≠ activation**: A 실 ledger `.claude/ledger/dev-process-event.jsonl` = 파일 부재(capture DORMANT) `[verified: Story §2.2]`. B 는 buildable now(query port empty→`[]`+zero graceful `[verified: query_dev_process_event.py:386-389]`)이나 실 가치 = substrate activation 이후. 따라서 B 는 (a) 산식·집계 로직 정의 + (b) 실측은 activation 이후 + (c) empty-ledger honest-degrade 자세를 상속한다.

**self-referential dogfood 7연속 이력 대응**: codeforge 는 최근 lint/게이트 Story 가 자기 산출물에서 그 결함을 재범하는 패턴(MEMORY 7연속)을 겪었다. dev-process 지표는 이 패턴 자체를 측정하려는 것이라 over-claim 유혹이 특히 크다 — "정확한 사이클타임 / exact FIX count / 정밀 should-have-caught 귀속 / 비-null token 비용" 은 substrate gap 상 전부 honest-degrade 강제 대상이다.

### 근본 mismatch + 외부 정당성

B 가 원하는 상관 차원(예: 결점을 발견한 리뷰어의 origin-lane, cycle-time 6-point subtype, §D-9 pattern 키 anchor_id/root_cause_class)의 상당수가 A 의 18-field index 에 **부재**하다 `[verified: append_dev_process_event.py:130-149]`. B 는 이 gap 을 재정의(A 침범)하지 않고 honest-degrade(근사·uncomputable-flag)로 흡수하며, 원할 시 A 계약 amendment 로 올린다(B 결정 아님).

이 회로는 codeforge 가 이미 검증한 패턴 ADR-045 §D-9(cross-Story pattern_count ≥ 2 → ADR escalation)를 답습한다. 단 도메인이 disjoint 하다: ADR-045 = 개발 후 회고(retro), ADR-106 = 배포 후 운영(operational), **본 ADR = 개발 과정(dev-process)**. ADR-106 이 이미 §D-9 를 amendment 하지 않고 **NEW ADR 로 disjoint feed 를 추가**한 선례를 남겼다(§경계 disjoint 표로 명시, ADR-045 본문 무변경) `[verified: ADR-106:2,109,192-202]`. 본 ADR 이 3번째 disjoint 도메인을 동형으로 추가한다.

## 결정

dev-process metric aggregation(Story B) 정책을 codeforge 의 normative SSOT 로 codify 한다. 정의는 아래 5 결정으로 구성된다. 본 ADR 이 normative SSOT 이고, Change Plan(`docs/change-plans/2026-07-15-cfp-2688-dev-process-metrics.md`)이 산식·집계·§8 Test Contract·§11 migration 의 상세 SSOT 이다.

### §결정 1 — B = 집계 ONLY, A ⊥ C 경계 (INV-B1/B3)

B 는 A `dev-process-event-v1` substrate 를 **read-only 소비**만 한다.

- **read 진입점 = mining port 단독** — `query_dev_process_event.query()/query_with_stats()` `[verified: query_dev_process_event.py:234-258]`. 원장 직접 파싱(Path B) 금지 — reader-port 격리 파괴 + dedup/honest-degrade 재구현(DRY 위반 ADR-140) + §9 port 하류 무의존(AC-17) 위반. (INV-B1)
- **B ⊥ C disjoint** — B = 측정·집계(aggregator). C(#2689) = 예방·판정(self-gate producer, PASS/FAIL·임계·차단). B 는 PASS/FAIL 을 세우지도 파이프라인을 게이팅하지도 않는다 `[verified: dev-process-event-v1.md:361-362]`. (INV-B3)
- **5th boundary invariant 상속(INV-B2)** — 상관 ID JOIN 허용, accounting payload re-record 금지(SoT 이중화 차단) `[verified: dev-process-event-v1.md:331]`. A 이벤트 재-emit 0.

### §결정 2 — 6 지표 산식 정의 + honest-degrade 천장 (INV-B5)

6 지표 계열의 산식·단위·입력필드를 Change Plan §4.1-§4.6 에 정의하고, 각 지표에 honest-degrade 경로를 강제한다:

| 지표 | 산식 요지 | honest-degrade 천장 |
|---|---|---|
| ① cycletime | lane 경계 residency(종료 앵커 우선순위 next-different-lane > final_artifact > verdict) | "lane residency"(NOT time-to-PASS, 6-point subtype 부재) / open_interval / negative-duration EXCLUDE + count |
| ② fixloop | fix_attempt_count(distinct fix_id) + fix_iteration_count(§10 재진입) 분리 | distinct fix_id 를 "iteration"으로 단일 표기 금지(과대집계) |
| ③ defect-attribution + should-have-caught | detecting_lane×family×type + review-responsibility heuristic | origin/expected-lane substrate 부재 → advisory / unattributed → uncomputable / 기계 게이트 detection 불가 시 honest-degrade |
| ④ selfref-recurrence | 동일 defect_id 재출현 + 4-tuple{family,type,ttd,detecting_lane} | defect_id=sha256(...) best-effort(normalized-location 무보장) / self-ref candidate(heuristic) ⊥ 일반 recurrence(기계) |
| ⑤ trend + §D-9 feed | bucketed time-series(forecast 금지) + pattern_count | anchor_id/root_cause_class substrate 부재 → uncomputable-by-substrate PRIMARY(§결정 4) |
| ⑥ token-cost | spawn-event-v1 weighted 4-class cost + top-N concentration | 3-gap 미해소 → null + upstream_gap_flags / cache 1h-2× helper 미유도 → honest-null |

**정직 천장 (ADR-119)**: exact-count/guaranteed-unique 주장 금지 — `query_with_stats()` 관측치(`rows_total`/`rows_deduped`/`duplicates_collapsed`) 상속 `[verified: query_dev_process_event.py:194-207]`. **"측정된 0(measured-0)" ≠ "미측정(dormant/empty)"** — stats 로 구분 표기(fabricated 0 금지). 인과 주장 금지("telemetry 가 결점 줄인다" 금지), 재발**률** = 측정치. (INV-B5)

### §결정 3 — §D-9 dev-domain escalation feed EXTEND (producer↔decider 분리)

단계 = `dev-process ledger → aggregate(B) → KPI → §D-9 pattern_count feed → PMOAgent §D-9 action`. B 의 역할 경계:

- **B = pattern_count PRODUCER** + frozen N=2 대비 "escalation-eligible 신호" 방출까지. `pattern_count = count(distinct story_key) for same {anchor_id, root_cause_class} within window`(within consumer_scope only). 결과 row = count 만 — escalation action(adr_draft_emitted/escalate_user) 판정 미포함.
- **escalation ACTION 디스패치 = PMOAgent §D-9 mandate(decider)** — B 가 pattern_count≥2 를 판정해 action 을 실행하면 PMO retro-time 소관 침범(SoT 이중화). B 는 새 임계 발명·게이팅 금지.
- **§D-9 = EXTEND(신규 disjoint feed)** — ADR-045 §D-9 를 EXTEND 하고 MEMORY.md 산문 corpus enumeration 을 supersede 하지 않는다. N=2 threshold 재정의 없이 frozen 상수로 재사용(citation 품질 = ADR-045 소관, B scope 아님). pmo-output-v1 `cross_story_pattern_adr_trigger` **additive 재사용**(계약 amendment 불요) `[verified: pmo-output-v1.md:119-126,166,172 v1.2 optional/additive]`.

**★closure machinery 미복제 (ADR-106 divergence)**: ADR-106 §결정 4 는 무한 발산 방지 closure 3원칙(dedup / max-depth / escalate_user)을 정의한다. **B 는 이를 복제하지 않는다** — B 는 PASSIVE read-time feeder(pattern_count 산출 + N=2 eligibility 신호만), auto-executing loop(cron → 자동 Issue → 자동 Epic chain)가 아니다. dedup/max-depth 는 self-executing loop 의 발산 억제 기제이므로 producer-only feeder 에 불필요하다. escalation loop 의 발산 억제·인간 게이트 = PMOAgent §D-9(decider) 소관.

### §결정 4 — AC-19 uncomputable = §D-9 feed 의 PRIMARY 경로 (정직 프레이밍)

§D-9 pattern 키 `anchor_id`/`root_cause_class` 는 A `_ROW_KEYS` 18-field 에 **부재** `[verified: append_dev_process_event.py:130-149]`. 따라서 `pattern_count=null` + `pattern_status='uncomputable_missing_key'` 가 **DEFAULT 경로**(edge 가 아님)이고 escalation feed 는 생성되지 않는다. 설계는 §D-9 feed 를 "producer-defined, currently uncomputable-by-substrate" 로 정직하게 프레이밍한다 — feed schema 는 landed(schema-pin, Change Plan §4.7) 이나 실 pattern_count 는 substrate 가 키를 제공할 때(A amendment)까지 null.

### §결정 5 — 신규 formal 계약 미신설 + de-facto KPI schema-pin + 0-API/measurement-tier 상속

- **신규 inter-plugin 계약(dev-process-metric-v1) 미신설** — kpi = LOCAL FILE 표면(transport 아님) → APIContractArch N/A, YAGNI(Story R2/G3 defer). 대신 **KPI snapshot/history schema 를 de-facto stable schema 로 Change Plan §4.7 에 pin**(§D-9 feed 필드 pattern_count/pattern_status/anchor_id/root_cause_class 포함). **신규 kind:registry doc 미생성 → doc-section §4-change-rules obligation 미발동 + MANIFEST registries 갱신 불요.**
- **KPI dual-file** — `docs/kpi/dev-process-<metric>-{history.jsonl,snapshot.json}` 6 지표. history = append-only(기존 row byte 불변) + snapshot = overwrite-idempotent. dual-file PATTERN = operational-signal-history.jsonl + operational-signal-rate.json 선례 `[verified: ls docs/kpi/]`(단 `-snapshot.json` literal 선례 부재 — new-but-consistent variant 채택, AC-6 wording 준수).
- **0-API-call / measurement-tier 상속(ADR-163)** — Path A local I/O only, record-only non-blocking(exit 0), measure≠classify(aggregate_stop_event tier 상속 `[verified: aggregate_stop_event.py:17-21]`). token-cost 원천 = spawn-event-v1(dev-process-event 아님, re-record 금지).
- **scope-guard ⊥ ADR-104** — dev-process 축 ⊥ operational-phase, wrapper-N/A 무저촉(설계리뷰 "wrapper runtime 0 → 측정 불가" false-block 방지) `[verified: dev-process-event-v1.md:345-347]`.

## 결과

### 긍정

- dev-process 지표(사이클타임·FIX·결점귀속·self-ref 재발·추세·token-cost)가 A substrate 위 downstream 집계로 정의되어 codeforge 자기-개선 관측 loop 의 wrapper-self 공백이 충당된다.
- ADR-045 §D-9 검증된 패턴(threshold 2 / escalation_action enum) + ADR-106 circuit 골격을 재사용해 신규 메커니즘 발명을 회피한다(도메인 disjoint 만 추가, closure machinery 미복제).
- honest-degrade 천장(§결정 2/4)으로 self-referential over-claim(7연속 이력) 재범을 구조적으로 차단한다.
- producer↔decider 분리(§결정 3)로 B 가 escalation action 을 흡수해 PMO 소관을 이중화하는 것을 차단한다.
- 신규 formal 계약 미신설(§결정 5)로 Phase 1 churn(MANIFEST/registry)을 회피한다.

### 부정 / trade-off

- **substrate gap 상 정밀도 한계** — cycle-time coarse residency(6-point 부재) / should-have-caught advisory(origin-lane 부재) / §D-9 uncomputable-by-substrate(anchor_id/root_cause_class 부재) / token-cost 3-gap(spawn-event-v1). 정밀화는 A 계약 amendment(B 귀속 아님) 또는 upstream(spawn-event-v1 3-gap) 해소 필요.
- **dormant 실측 부재** — capture 미배선(landing ≠ activation) 상태에선 B 산출 = honest-zero snapshot. 실 가치 = activation 이후. 이는 A 의 "정의는 landed, 실측은 defer" 자세 상속.
- **declaration-only Phase 1** — 본 ADR = 집계 정책 정의 layer. 실 mechanism(aggregate_dev_process_event.py + 6 compute fn + KPI dual-file write + lint/self-test) = Phase 2 carrier(`mechanical_enforcement_actions: []`). pattern_count ≥ 2 recurrence 시 follow-up CFP MUST promote to mechanical lint(ADR-084 precedent).

### Edge Case 처리 요약 (Change Plan §8.2)

| EC | 시나리오 | 기대 동작 |
|---|---|---|
| EC-1 | empty/dormant ledger | crash 0(exit 0), count=0, 계산 불가=null, "미측정" stats 표기(measured-0 위장 금지) |
| EC-2 | malformed-only ledger | malformed_skipped + honesty_note 보존, 정상 row 로만 집계(empty 와 상태 구분) |
| EC-3 | 6-point subtype 부재 | residency 로 정직 표기, time-to-PASS over-label 금지 |
| EC-4 | negative/reverse-duration | duration 집계 EXCLUDE + negative_duration_count/clock_anomaly_count(§7.4.3 clock) |
| EC-5 | anchor_id/root_cause_class 부재 | pattern_count=null + uncomputable_missing_key(PRIMARY 경로, §결정 4) |
| EC-6 | token-cost 3-gap 미해소 | 파생 null + upstream_gap_flags / cache 1h-2× helper 미유도 → honest-null |
| EC-7 | consumer_scope missing | scope_unknown bucket / §D-9 pattern_count = within-scope only |
| EC-8 | self-test tautology | 독립 fixture 기대값 oracle(자기 계산값 self-match 금지, CFP-2673 drift-0 선례 답습 금지) |

## 경계 (boundary)

### 본 ADR scope

- **본 ADR scope** = dev-process metric 집계 **정책 정의**(6 지표 산식·경계 + producer↔decider 분리 + honest-degrade 천장 + 3-domain disjoint feed EXTEND + de-facto KPI schema-pin). declarative SSOT.
- **A (#2687, ADR-155)** = substrate·계약(dev-process-event-v1 + mining port + capture). 본 ADR 은 이를 read-only 소비만 — substrate 재구축·event schema 수정·capture 활성화 = A 귀속(**본 ADR 무접촉**).
- **C (#2689)** = gate/verdict 판정(self-gate producer, PASS/FAIL·임계·차단). B ⊥ C disjoint — 본 ADR 은 verdict 미산출.
- **PMOAgent §D-9** = escalation ACTION 디스패치(decider). B = pattern_count producer + eligibility 신호까지(§결정 3).
- **Phase 2 (CFP-2688 §8-§11)** = 실 mechanism(aggregate_dev_process_event.py + 6 compute fn + KPI dual-file write + lint/self-test + inventory enroll). 본 ADR 은 정책 정의만 — 실 script/lint 신설 0.

### ADR-045 §D-9 / ADR-106 ↔ 본 ADR 3-domain disjoint 표 (§결정 3 — "동일" 단일 진술 금지)

| 항목 | ADR-045 §D-9 (retro 도메인) | ADR-106 (operational 도메인) | ADR-156 (dev-process 도메인) | disjoint 여부 |
|---|---|---|---|---|
| **입력 도메인** | 개발 후 회고(retro corpus) | 배포 후 운영(operational signal) | 개발 과정(dev-process event) | **3-way disjoint** (시간축 위치 다름 — 회고 vs 배포후 vs 개발중) |
| **트리거** | Story 완료 retro write | 운영 신호 임계 초과(cron tick) | dev-process ledger 집계(batch) | **disjoint** |
| **집계 단위** | cross-Story pattern_count (review-verdict anchor_id) | 동일 signal signature pattern_count | 동일 {anchor_id, root_cause_class} pattern_count within scope | **disjoint** (substrate·식별자 종류 다름) |
| **감지 주체** | PMOAgent (retro mandatory trigger) | cron → 자동 Issue → PMOAgent | B aggregate → §D-9 feed → PMOAgent | 답습 (PMOAgent escalation 공통) |
| **threshold** | N = 2 (frozen) | N = 2 (답습) | N = 2 (frozen 재사용, 재litigate 금지) | 답습 (값 동일) |
| **escalation_action** | adr_draft_emitted \| escalate_user | adr_draft_emitted \| escalate_user | (판정 미포함 — producer only) | 답습 (enum 동일, B 는 미판정) |
| **loop 성격** | forcing function(비차단 governance) | self-executing loop(closure 3원칙) | **PASSIVE read-time feeder(closure machinery 미복제)** | **disjoint** (B ≠ auto-executing loop) |

**disjoint normative**: ADR-045 = "회고에서 발견한 cross-Story pattern → ADR" / ADR-106 = "운영에서 회수한 cross-signal pattern → 다음 Epic" / 본 ADR = "개발 과정에서 집계한 cross-story pattern → §D-9 feed". **답습하되 중복이 아니다** — 같은 PMOAgent escalation 메커니즘(threshold 2 / escalation_action enum)을 공유하나 **입력 도메인(retro corpus vs operational signal vs dev-process event)이 3-way disjoint**. **ADR-045 §D-9 본문은 무변경**(retro 도메인 유지) — 본 ADR 이 dev-process 도메인 disjoint 를 §경계 에 추가할 뿐이다(ADR-106 §결정 2 precedent 동형 `[verified: ADR-106:109,192-202]`). ADR-106 본문도 무변경(operational 도메인 유지).

### 보안 trust boundary (§7.1 / §7.5 light scope — declarative)

- **read-only 소비 (§7.1)** — B 는 dev-process ledger(index-tier allow-list-clean) + spawn-event ledger 를 port/reader 경유 read-only. 0-API-call(local I/O only) → external network 위조 표면 0. include_blob=False default → verbatim content deref 0.
- **index-tier-derived only emit (§7.5)** — KPI 출력 = enum/hash/count/numeric 파생만(verbatim content/path/credential 0). 신규 secret 표면 = NO(3 조건: include_blob=False / index-tier-derived only / cross-channel JOIN correlation-only).
- **5th boundary re-record ban (§7.1)** — token accounting 을 dev-process ledger 로 re-record 금지(SoT 이중화 차단, INV-B2/B4).
- **honest-ceiling (ADR-119)** — "leak-proof"/"DoS-proof" 주장 금지. O(n) linear born-safe bound.

## 해소 기준

N/A — permanent policy

`is_transitional: false` permanent governance anchor. dev-process metric 집계 정책(6 지표 산식·경계 + producer↔decider + honest-degrade 천장 + 3-domain disjoint feed)은 future 재사용 permanent. amendment 시 ratchet 강화 방향만 허용(honest-degrade 천장 강화 / producer↔decider 경계 강화 / disjoint 강도 강화). honest-degrade 완화 / over-claim 허용 / producer↔decider 경계 제거 = 약화 방향 → ADR-058 §결정 5 약화 evidence requirement 의무.

## 관련 ADR

- **ADR-155 (A substrate)** — dev-process observability substrate + dev-process-event-v1. B = downstream consumer, mining port read-only, 5th boundary invariant 상속
- **ADR-106 (circuit template)** — operational-signal → PMO circuit. NEW ADR precedent(disjoint feed 추가, ADR-045 본문 무변경) + closure machinery 미복제 divergence
- **ADR-045 §D-9** — cross-Story pattern → ADR escalation forcing function + escalation_action enum (EXTEND source, 본문 무변경 invariant)
- **ADR-163** — measurement channel. 9th channel 소비, 0-API-call / measure≠classify 상속
- **ADR-104** — operational-phase 경계. dev-process ⊥ operational-phase disjoint axis(false-block 방지)
- **ADR-119** — research-before-claims / honest-degrade 천장
- **ADR-140** — write-time hygiene(Path B reject 근거)
- **ADR-061** — python portability(UTC-Z parser Z-strip)

## 관련 파일

- `archive/adr/ADR-RESERVATION.md` — row 156 append (본 commit)
- `docs/inter-plugin-contracts/dev-process-event-v1.md` — A substrate 계약 (read-only 소비, 의미 변경 0)
- `scripts/lib/query_dev_process_event.py` — A mining port (B 유일 read 진입점, 의미 변경 0)
- `scripts/lib/aggregate_stop_event.py` — 집계기 archetype (의미 변경 0)
- `scripts/lib/spawn_event_pricing.py` — token-cost 원천 helper (재사용, 의미 변경 0)
- `archive/adr/ADR-045-story-retro-mandatory-trigger.md` — §D-9 EXTEND source (본문 무변경 invariant)
- `archive/adr/ADR-106-operational-signal-pmo-input-circuit.md` — circuit template (본문 무변경)
- `docs/inter-plugin-contracts/pmo-output-v1.md` — cross_story_pattern_adr_trigger additive 재사용 (계약 무변경)
- `docs/architecture/codeforge-family.md` — living-arch data_flow + interfaces node
- `docs/change-plans/2026-07-15-cfp-2688-dev-process-metrics.md` — 집계 산식·§8 Test Contract·§11 migration 상세 SSOT (internal-docs)

## 변경 이력

| 날짜 (KST) | CFP | 변경 |
|---|---|---|
| 2026-07-15 | CFP-2688 | 최초 작성 — dev-process metric aggregation 정책 (5 결정: §1 B=집계 ONLY A⊥C 경계 INV-B1/B2/B3 + §2 6 지표 산식 + honest-degrade 천장 INV-B5 + §3 §D-9 dev-domain feed EXTEND producer↔decider 분리 closure machinery 미복제 + §4 AC-19 uncomputable PRIMARY 경로 + §5 신규 formal 계약 미신설 de-facto KPI schema-pin 0-API/measurement-tier 상속). 3-domain disjoint 표(retro[ADR-045]/operational[ADR-106]/dev-process[ADR-156]) — ADR-045/ADR-106 본문 무변경 invariant. ADR-106 NEW ADR precedent 동형(closure machinery 미복제 divergence). ArchitectAgent chief author direct write. Epic #2686 Story B. 번호 156 = GH_TOKEN 부재로 OCC atomic claim primitive 미실행 → ADR-133 §결정4 fallback(fresh git ls-tree 실측): `git fetch origin main` + `git ls-tree --name-only origin/main archive/adr/` numeric max = ADR-155(140~148·150~155 존재, 149 orphan gap 존치, 156 collision-free) 2026-07-15 KST origin/main f5cd56a6. CFP-2680 row 153 / CFP-2684 row 154 / CFP-2687 row 155 동일 fallback 선례. dual-key 3-leg 정합: filename ADR-156-dev-process-metric-aggregation-escalation-feed.md ∧ frontmatter adr_number: 156 ∧ RESERVATION row 156. 신규 required context 0(Phase 1 doc/ADR only, branch-protection 7-tuple 무변경) / inter-plugin 계약 무변경(신규 formal 계약 미신설, de-facto KPI schema-pin) / 신규 category 0(governance 재사용). ADR-058 §결정 5 강화(ratchet) 방향, sunset_justification N/A. |
