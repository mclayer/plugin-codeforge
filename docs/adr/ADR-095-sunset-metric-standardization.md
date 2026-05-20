---
adr_number: 95
title: 9 ADR sunset metric 표준화 — sunset_justification 3-tuple metric 영역 형식 통일 + 집계 dashboard + cron 자동 측정
status: Accepted
category: governance
date: 2026-05-21
carrier_story: CFP-1138
parent_epic: CFP-1111
related_stories:
  - CFP-1138     # 본 carrier (CFP-1111 Wave 1 Story-2, ADR-095 7-bundle 4/7)
  - CFP-1111     # umbrella Epic
  - CFP-1125     # Story-1 sunset declarative 9 anchor (9 현존 is_transitional=true ADR 의 sunset_carrier_cfp + sunset_justification_metric_source 선언)
related_adrs:
  - ADR-097      # paradigm replacement governance anchor — §결정 3 carrier-preserved sunset 개념 (bulk sunset metric = 효용 reproduce 증명) 정합
  - ADR-058      # ADR sunset criteria mandate — §결정 5 sunset_justification 3-tuple (metric/who/how) 의 metric 영역 표준화 대상
  - ADR-092      # changelog SSOT location — metric source = changelog mining SSOT (K-7 결정 cross-ref)
  - ADR-076      # declarative reconciliation upgrade — 9 anchor 중 1 (sunset_justification_metric_source: walker integration test) 표준화 적용 대상
related_files:
  - docs/adr/ADR-058-adr-sunset-criteria-mandate.md  # §결정 5 sunset_justification 3-tuple metric 영역
  - docs/adr/ADR-092-changelog-ssot-location.md       # metric source = changelog mining SSOT (sister within W1-S2)
  - docs/kpi/rate-limit-fallback.json                 # ADR-057 KPI dashboard precedent (집계 dashboard 형식 답습)
  - docs/adr/ADR-RESERVATION.md                       # row 95 reserved → active 전환
mechanical_enforcement_actions: []  # declaration-only Wave 1 — 9 ADR metric 형식 통일 declare + 집계 dashboard schema declare. 실 cron 자동 측정 = 후속 carrier (ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 — behavioral declaration, pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical lint)
is_transitional: false  # permanent governance — sunset metric 표준 자체는 영구 정책 (sunset 기준 부재). 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-095 — 9 ADR sunset metric 표준화

## 상태

`Accepted` (2026-05-21 KST) — CFP-1138 carrier (CFP-1111 Wave 1 Story-2, ADR-095 7-bundle 4/7). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 CFP-899 precedent 정합 — chief author scope).

## 컨텍스트

### 동인

ADR-058 §결정 3 은 `## 해소 기준` 섹션의 모든 entry 에 측정성 3-tuple (metric / who / how) 정량 명시를 의무화한다. 그러나 **metric 영역의 형식 자체는 표준화되지 않았다** — 각 ADR 작성자가 metric 을 자유 산문으로 기술하므로, 9 현존 `is_transitional: true` ADR (CFP-1125 Story-1 sunset declarative 9 anchor) 의 metric 표현이 일관되지 않다.

구체 evidence (현존 sunset_justification_metric_source 표현 산포):
- ADR-076 `sunset_justification_metric_source: walker integration test (tests/walker/test-desired-state-coverage.bats)` — bats test path 형식.
- ADR-053 / ADR-083 — `sunset_carrier_cfp: CFP-1111-Wave-4-Story-11` 만 보유, metric_source 형식 미통일.

> verified-via: Grep "sunset_carrier_cfp|sunset_justification_metric_source" docs/adr — 3 file 매치 (ADR-053 L28 sunset_carrier_cfp only / ADR-076 L8-9 carrier + metric_source bats path / ADR-083 L17 carrier only). metric_source 형식 표준 부재 입증.
> verified-via: Read docs/adr/ADR-058-adr-sunset-criteria-mandate.md (L60-68 §결정 3 — metric/who/how 3-tuple 정량 의무, "안정화되면/임시/한시적" 모달 어휘 금지. metric *형식* 표준은 미정의 — metric *존재* 의무만 codify).

이 metric 형식 비일관은 두 governance 비용을 낳는다:

1. **집계 불가** — metric 표현이 ADR 마다 다르면 9 ADR sunset 진척을 한 dashboard 로 집계할 수 없다 (각 ADR 을 manual 독해해야 함). ADR-057 의 `docs/kpi/rate-limit-fallback.json` 같은 cron-측정 dashboard 패턴을 9 ADR 전체로 확장하려면 metric 형식 표준이 prerequisite.
2. **cron 자동 측정 불가** — metric source 가 자유 산문이면 mechanical 측정 stub 작성 불가. metric source 를 closed-set (changelog mining + cron)으로 표준화해야 자동 측정 인프라가 성립.

본 ADR 은 ADR-058 §결정 3 의 metric *영역* 형식을 표준화한다 — metric *존재* 의무 (ADR-058) 위에 metric *형식* 통일 layer 를 부착 (ratchet 강화 방향, scope 확장).

### CFP-1111 Wave 1 Story-2 7-bundle 위치

본 ADR 은 7-slot bundle (CFP-1111 Wave 1 Story-2 — ADR-092~098 7 ADR sibling carrier) 의 4/7 이다. 7-bundle 구성: ADR-092 (changelog SSOT) / ADR-093 (4-field 완료 보고 schema) / ADR-094 (Fallback 정책) / **ADR-095 (본 — 9 ADR sunset metric 표준화)** / ADR-096 (min_prerequisite_version manifest schema) / ADR-097 (paradigm replacement governance anchor, merged 8d1888b) / ADR-098 (UpgradeAgent runtime ownership). 본 ADR 의 metric source 표준 (K-7) 은 ADR-092 (changelog SSOT) 의 changelog mining 을 cross-ref 한다.

> verified-via: Read docs/adr/ADR-RESERVATION.md (L131 row 95 — "9 ADR sunset metric 표준화 SSOT ... ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 의 metric 영역 표준화 — 9 ADR (현존 is_transitional=true) sunset metric 형식 통일 / 집계 dashboard / cron 자동 측정 normative SSOT codify. ADR-092 (changelog SSOT) cross-ref (metric mining source)" verbatim).

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (sunset metric 표준화 layer 가 인접 governance layer 를 약화하지 않음을 박아두는 anchor):

1. **closed_enum open_extension:false 보존** — metric source 표준 (§결정 1, K-7) 의 source enum (changelog mining + cron 자동 측정) 은 closed-set. metric source 확장은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — sunset metric dashboard + cron (§결정 2) 은 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 와 disjoint. metric 측정 layer 가 PR gate 를 우회하지 않는다.
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ sunset metric 측정 layer 는 disjoint. metric dashboard 의 cron 주기가 ADR-067 RESET 룰을 변경하지 않는다 (ADR-076 §ADR-067 disjoint layer cross-ref 답습).

### §결정 1 — sunset metric 표준화 (ADR-058 §결정 5 metric 영역)

ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 의 **metric 영역 형식**을 표준화한다. 9 현존 `is_transitional: true` ADR (CFP-1125 Story-1 sunset declarative 9 anchor) 의 metric 형식을 통일한다.

**metric source 표준 (K-7 결정)**: sunset metric 의 source 는 closed-set 2-source (AND/OR composable):

| source | 정의 | SSOT cross-ref |
|---|---|---|
| **changelog mining** | sunset 진척을 codeforge family changelog (ADR-092 SSOT) 에서 mechanical 추출 — 도입 사유 (예: rate-limit cascade, declarative paradigm) 의 해소 신호를 changelog entry pattern 으로 mining | ADR-092 (changelog SSOT location) — metric mining source SSOT |
| **cron 자동 측정** | monthly cron 이 metric 을 측정해 dashboard json 갱신 (§결정 2) — ADR-057 `rate-limit-fallback.json` precedent 답습 | docs/kpi/*.json (집계 dashboard) |

자유 산문 metric source (예: "충분히 안정화되면", manual review) 는 표준 비대상 — ADR-058 §결정 3 모달 어휘 금지 정합. metric source 는 위 2-source 중 1+ 로 표현 의무.

**baseline (K8s deprecation policy 차용)**: sunset metric 의 시간 threshold baseline 은 K8s deprecation policy 를 차용한다 — **GA (stable) 12개월 / Beta 9개월**. 즉 `is_transitional: true` ADR 의 도입 사유가 해소된 후, GA-tier anchor 는 12개월 / Beta-tier anchor 는 9개월 grace 후 sunset 정식 발동. baseline 은 metric 의 시간 차원 정량 anchor 이며, 각 ADR 의 구체 metric (rate / count / flag) 과 AND 결합 (시간 threshold 충족 AND metric threshold 충족 시 sunset).

> verified-via: Read docs/kpi/rate-limit-fallback.json (schema_version 1.1 — measured_at / window_months 3 / sonnet_spawn_total / fallback_count / fallback_rate_percent / sample_size_sufficient / gate_status. ADR-057 KPI dashboard 형식 = 집계 dashboard 답습 대상).

### §결정 2 — metric 집계 dashboard + cron (declaration-only Wave 1)

9 ADR sunset metric 을 단일 집계 dashboard (`docs/kpi/sunset-metric.json` 등) 로 집계 + monthly cron 자동 측정한다. ADR-057 rate-limit-fallback KPI dashboard precedent (`docs/kpi/rate-limit-fallback.json` + monthly cron + `rate-limit-fallback-rate` evidence-check registry entry) 를 답습한다.

**dashboard schema (declaration)**: 집계 dashboard 는 9 ADR 각각의 (a) adr_number / (b) sunset_carrier_cfp / (c) metric source (changelog mining / cron — §결정 1) / (d) baseline threshold (GA 12개월 / Beta 9개월) / (e) measured value / (f) gate_status (pending / met / sunset_ready) 를 row 로 보유. ADR-057 dashboard 의 `gate_status` field semantics 답습.

**Wave 1 = declaration-only**: 본 ADR 은 metric 형식 표준 + dashboard schema 를 declare 만 한다. 실 cron 자동 측정 인프라 (`docs/kpi/sunset-metric.json` 실 생성 + cron workflow + 집계 script) 는 **후속 carrier** 다 — ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (`mechanical_enforcement_actions: []`). cron 측정이 도입되기 전까지는 9 ADR 의 metric 형식 통일 (sunset_justification_metric_source field) 이 manual 1차 안전망 + DesignReview lane MUST flag (behavioral directive).

### §결정 3 — carrier-preserved sunset 정합 (ADR-097 §결정 3)

bulk sunset (9 ADR 동시 sunset) = carrier-preserved sunset (효용 lossless carry — ADR-097 §결정 3). 본 ADR 의 metric 표준은 ADR-097 carrier-preserved sunset 개념과 정합한다:

bulk sunset 발동 시 9 ADR 각각의 효용 carry 경로 (대체 paradigm carrier 로 lossless 이전) 를 metric 이 **reproduce 증명**한다. 즉 metric 은 "도입 사유 해소"뿐 아니라 "효용 carry lossless" 를 측정 신호로 포함한다 — β2 audit LOSSLESS evidence (CFP-1113 carrier evidence, 9/9 lossless) 기반.

| | metric 측정 대상 | ADR-097 §결정 3 |
|---|---|---|
| **naive sunset** | 도입 사유 해소 only (효용 carrier 부재) | 면제 비대상 — ADR-058 §결정 5 naive sunset 차단 |
| **carrier-preserved sunset** (본 §결정 정합) | 도입 사유 해소 AND 효용 carry lossless reproduce (β audit) | ADR-097 §결정 3 carrier-preserved — sunset_justification 본문 = 효용 carry 경로 명시 |

본 §결정 은 ADR-097 §결정 3 carrier-preserved sunset 개념을 metric 측정 차원으로 specialize 한다 — metric 이 "효용 reproduce 증명" 신호를 포함하므로, bulk sunset 시 walker (대체 paradigm carrier) 가 효용을 reproduce 함을 metric 으로 입증. lossless 미달 (효용 carry 누락) ADR 은 bulk sunset 비대상 (ADR-097 §결정 3 naive sunset 차단 정합).

## 결과

### 긍정

- ADR-058 §결정 3 metric 영역 형식 표준 획득 — metric *존재* 의무 (ADR-058) 위 metric *형식* 통일 layer 부착 (ratchet 강화).
- 9 ADR sunset 진척을 단일 dashboard 로 집계 가능 — metric source closed-set (changelog mining + cron) 표준이 mechanical 측정 prerequisite 충족.
- ADR-097 carrier-preserved sunset 개념의 metric 측정 차원 specialize — metric 이 효용 carry lossless 를 reproduce 증명 (β audit evidence 기반).
- K8s deprecation policy baseline (GA 12개월 / Beta 9개월) 차용 — sunset 시간 threshold 의 industry-grounded 정량 anchor.

### 부정 / trade-off

- metric source closed-set (changelog mining + cron) 가 자유 산문 metric 을 배제 — 일부 ADR 의 metric 이 source 표준에 안 맞을 risk. 완화 = §결정 1 source 2-tuple AND/OR composable + baseline 시간 threshold AND 결합 (유연성 보존). source 확장 = 본 ADR amendment (강화 방향).
- 실 cron 측정 Wave 1 부재 (`mechanical_enforcement_actions: []`) — metric 형식 통일은 declare 만, 실 dashboard json + cron workflow 는 후속 carrier. pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical (ADR-082 §결정 6 retain rationale 답습).
- 9 ADR metric 형식 retroactive 통일 부담 — 9 현존 ADR (CFP-1125 Story-1 anchor) 의 sunset_justification_metric_source field 형식 일괄 정합 필요. 단 CFP-1125 Story-1 이 declarative 9 anchor 선언을 carry 하므로 본 ADR 은 metric *형식* 표준만 codify (실 field 통일 = CFP-1125 + 후속).

## 해소 기준

N/A — permanent policy (`is_transitional: false`). sunset metric 표준 자체는 영구 거버넌스 정책 (sunset 기준 부재). 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: metric source closed-set 확장 / dashboard schema field 강화 / cron 측정 mechanical 승격 / baseline threshold 정밀화). 약화 방향 (예: metric source closed-set 축소 / metric 형식 표준 무자격 영역 확장 / open_extension true 다운그레이드) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = governance, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — §결정 5 sunset_justification 3-tuple (metric/who/how) 의 metric 영역 표준화 대상 (cross-ref)
- `docs/adr/ADR-092-changelog-ssot-location.md` — metric source = changelog mining SSOT (K-7 결정 cross-ref, sister within W1-S2)
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — §결정 3 carrier-preserved sunset 개념 (bulk sunset metric = 효용 reproduce 증명) 정합 (cross-ref)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — 9 anchor 중 1 (sunset_justification_metric_source: walker integration test), 표준화 적용 대상 (cross-ref)
- `docs/kpi/rate-limit-fallback.json` — ADR-057 KPI dashboard precedent (집계 dashboard 형식 답습 대상)
- `docs/adr/ADR-RESERVATION.md` — row 95 reserved → active 전환
