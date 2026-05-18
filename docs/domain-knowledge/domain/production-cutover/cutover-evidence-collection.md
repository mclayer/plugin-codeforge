---
kind: domain_fact
type: domain-knowledge
area: production-cutover
topic_slug: cutover-evidence-collection
title: Production cutover — 4-evidence-quad 수집 절차
status: Active
tags:
  - production-cutover
  - evidence-quad
  - production-evidence-deputy
  - epic-closed-gate
  - cfp-954
related_adrs:
  - ADR-72   # §결정 5 EPIC CLOSED gate evidence quad 4중 정의
  - ADR-014  # CONDITIONAL SubAgent base + boundary axis (design-time SSOT vs runtime-evidence)
  - ADR-082  # write-time self-write verification mandate
related_stories:
  - CFP-882  # parent Epic (Wave 4 sub-Epic)
  - CFP-954  # 본 carrier Story (Story-3)
created: 2026-05-18
updated: 2026-05-18
---

# Production cutover — 4-evidence-quad 수집 절차

## 정의

**4-evidence-quad** = ADR-72 §결정 5 가 의무하는 EPIC CLOSED gate 의 production 실측 evidence 4중 (bucket prefix listing + WAL sample + L1 backlog drainage rate + L2/L3 cadence trigger). **Live touching Epic 한정 의무** (wrapper governance Epic / doc-only Epic 자연 N/A — ADR-005 plugin self-application N/A 표준 정합).

본 entry = ADR-72 §결정 5 narrative SSOT — ProductionEvidenceDeputy 가 EPIC CLOSED gate 검증 시 참조하는 evidence 수집 절차 단일 정의.

## 컨텍스트

ProductionEvidenceDeputy spawn trigger (ADR-72 §결정 3) 후, EPIC CLOSED gate (§결정 5) 에서 production state 실측 evidence 4중을 명시 verify 한다. 4-evidence-quad = spawn 후 evidence verify gate. 4 prerequisite measurement source mechanical anchor 4-tuple = spawn trigger gate (README.md §4 참조, disjoint).

## 핵심 규칙

### Evidence quad 4중 정의

**1.1 Production bucket prefix listing evidence** — production storage (S3 / GCS / etc) bucket prefix listing verbatim output:
- bucket name (예: `s3://mctrader-production-wal/`)
- prefix path (예: `2026-05-18/cycle-01/`)
- object count (>=1 sample object)
- sample object key (예: `2026-05-18T07:00:00.000Z__wal__BTC_KRW.json`)

Sample method (boto3):
```python
import boto3
s3 = boto3.client('s3')
resp = s3.list_objects_v2(Bucket='mctrader-production-wal', Prefix='2026-05-18/cycle-01/')
print(f"object count: {resp.get('KeyCount', 0)}")
for obj in resp.get('Contents', [])[:3]:
    print(f"  key: {obj['Key']} size: {obj['Size']}")
```

Sample method (gcloud):
```bash
gcloud storage ls gs://mctrader-production-wal/2026-05-18/cycle-01/ --recursive | head -3
```

**1.2 WAL sample 실측** — production storage WAL row sample:
- timestamp field present + parseable (ISO 8601)
- payload schema 정합 verify (production schema spec ↔ 실 row schema diff = 0)

Sample method (boto3 + json):
```python
import json, boto3
s3 = boto3.client('s3')
key = '2026-05-18/cycle-01/2026-05-18T07:00:00.000Z__wal__BTC_KRW.json'
obj = s3.get_object(Bucket='mctrader-production-wal', Key=key)
sample = json.loads(obj['Body'].read())
assert 'timestamp' in sample
assert 'payload' in sample
print(f"timestamp: {sample['timestamp']} payload keys: {list(sample['payload'].keys())}")
```

**1.3 L1 backlog drainage rate (1h sustained 측정)** — drainage rate 의무 invariant: `drainage_rate / ingest_rate <= 1.0` (1h sustained window).

Sample method (Prometheus query):
```promql
# 1h drainage rate
sum(rate(mctrader_l1_backlog_drained_total{env="production"}[1h])) /
sum(rate(mctrader_l1_ingest_total{env="production"}[1h]))

# Threshold: result <= 1.0 (drainage 가 ingest 를 따라잡는다)
```

**1.4 L2/L3 자연 cadence trigger 실측** — 5min OR 1h window trigger 실측 명시 (cadence_actual_window vs designed_window mismatch surface).

Sample method:
```promql
# L2 cadence (designed 5min)
histogram_quantile(0.5, rate(mctrader_l2_cadence_window_seconds_bucket{env="production"}[1h]))
# expect: ~300 (=5min)

# L3 cadence (designed 1h)
histogram_quantile(0.5, rate(mctrader_l3_cadence_window_seconds_bucket{env="production"}[24h]))
# expect: ~3600 (=1h)
```

### 사용자 ack quad 5중 (Story-1 anchor 정합)

ADR-72 §결정 5 추가 — 사용자 ack 5중:
1. bucket 콘솔 evidence 명시 (사용자 직접 bucket 콘솔 확인)
2. log evidence (production log sample)
3. Prometheus metric (drainage rate + cadence)
4. drainage 4중 결합 (위 4-evidence-quad)
5. **사용자 ack signature** (사용자 explicit confirm — production-touching label 부착 + Story §1 [user-input] verbatim)

### 4 prerequisite measurement source mechanical anchor 4-tuple cross-ref

(CFP-954 carrier — README.md §4 참조)

- MS-1 `live_touching`
- MS-2 `production_cutover_touching` (dual-source AND)
- MS-3 `marketplace_publish_touching`
- MS-4 `consumer_impact_blast_radius` (ADR-068 I-5 empirical anchor)

본 4-tuple = ProductionEvidenceDeputy spawn trigger gate (ADR-72 §결정 3). 4-evidence-quad = spawn 후 evidence verify gate (§결정 5).

## 경계

### Wrapper-self-app N/A invariant

ADR-72 §결정 6 정합 — wrapper plugin 자체 = production cutover 영역 외 (code 0 + runtime behavior 0 + production deploy state 부재). 본 cutover-evidence-collection 절차 = consumer Story (예: mctrader live touching production cutover Story) 영역 한정. wrapper governance Story (CFP-954 본 Story 자체 포함) = Tier-1 declare-time exemption (실 4-evidence-quad measurement skip).

trigger gate (4 measurement source 4-tuple) ↔ verify gate (4-evidence-quad) 는 disjoint axis — 본 entry 는 verify gate 한정. trigger gate 는 README.md §4 SSOT.

## 관련 ADR

- **ADR-72 §결정 5** — EPIC CLOSED gate production evidence quad 4중 정의 SSOT
- **ADR-72 §결정 6** — wrapper-self-app N/A invariant
- **ADR-014** — CONDITIONAL SubAgent base + boundary axis (design-time SSOT vs runtime-evidence)
- **ADR-082** — write-time self-write verification mandate (evidence value 사실성 source direct verify)

## 변경 이력

| 날짜 (KST) | Story | 변경 |
|---|---|---|
| 2026-05-18 | CFP-954 | 최초 작성 — ADR-72 §결정 5 4-evidence-quad 수집 절차 narrative SSOT (4중 evidence 정의 + sample method + 사용자 ack 5중 + measurement source 4-tuple cross-ref + wrapper-self-app N/A) |
