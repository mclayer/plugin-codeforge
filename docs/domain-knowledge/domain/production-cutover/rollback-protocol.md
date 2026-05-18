---
kind: domain_fact
type: domain-knowledge
area: production-cutover
topic_slug: rollback-protocol
title: Production cutover — 7-step rollback protocol (incident response)
status: Active
tags:
  - production-cutover
  - rollback-protocol
  - incident-response
  - production-evidence-deputy
  - postmortem
  - cfp-954
related_adrs:
  - ADR-72   # §결정 5 EPIC CLOSED gate evidence quad
  - ADR-014  # boundary axis (DR / disconnect / clock / rate / env)
  - ADR-045  # retro mandatory trigger (PMOAgent auto-trigger)
related_stories:
  - CFP-882  # parent Epic (Wave 4 sub-Epic)
  - CFP-954  # 본 carrier Story (Story-3)
created: 2026-05-18
updated: 2026-05-18
---

# Production cutover — 7-step rollback protocol

## 정의

**7-step rollback protocol** = Live touching consumer Story 영역의 production cutover incident response 절차 (Detect → Isolate → Assess → Rollback decision → Execute → Verify → Postmortem). Helm rollback + AWS CodeDeploy Blue/Green 답습 (OperationalRiskArch §A.3 + Researcher §E.1 정합).

본 entry = production cutover incident response narrative SSOT — ProductionEvidenceDeputy / LiveOps / LiveOrdering 3 SubAgent 가 incident 시 참조하는 단일 절차 정의.

## 컨텍스트

ProductionEvidenceDeputy 4-evidence-quad 중 1+ failing 시 production cutover incident 진입. rollback (canary 이전 state 복귀) vs forward-fix (canary 유지 + hotfix Story) 결정 게이트 = 사용자 explicit decision 의무 영역 (reconcile-protocol-v1 user_decision_branches 0 invariant 영역 외 — production cutover rollback = 사용자 결정 분기 허용 영역, ADR-064 §self-application 정합).

## 핵심 규칙

### Step 1 — Detect

ProductionEvidenceDeputy 4-evidence-quad 중 1+ failing 감지:
- bucket prefix listing 0 (production storage write 0)
- WAL sample schema mismatch (production schema ↔ 실 row schema diff > 0)
- drainage rate > ingest rate (L1 backlog 누적, drainage_rate / ingest_rate > 1.0)
- cadence trigger window mismatch (cadence_actual_window vs designed_window deviation > tolerance budget)

Detection source: production-cutover-evidence.yml workflow (PR-time) + manual workflow_dispatch (operations team pre-verify) + Prometheus alert (continuous monitoring).

### Step 2 — Isolate

production-touching label 부착 PR / Story open 시 즉시:
- `phase:완료` label 보류 (phase-gate-mergeable 차단)
- `retro-pending` label 부착 (PMOAgent retro auto-trigger forcing function)
- Live touching consumer 영역에서 추가 Story commit pause (operations team manual decision)

### Step 3 — Assess

ProductionEvidenceDeputy + LiveOps + LiveOrdering 3 SubAgent 동시 spawn (consumer Story 영역 시 ADR-72 §결정 3 trigger axis 정합):
- ProductionEvidenceDeputy = 실측 evidence verify
- LiveOps = production env containment + runbook 검증
- LiveOrdering = order placement state + reconciliation invariant verify

### Step 4 — Rollback decision

rollback (canary 이전 state 복귀) vs forward-fix (canary 유지 + hotfix Story 신설) 결정 게이트:
- **rollback path**: production state 영향 reversible + 사용자 explicit decision 의무
- **forward-fix path**: rollback 영향 destructive 시 (예: WAL data 보존 의무) + hotfix Story 신설 + `hotfix-bypass:prod-cutover-deputy-evidence` label

**사용자 explicit go-ahead 의무 영역** (reconcile-protocol-v1 user_decision_branches: 0 invariant 영역 외, ADR-064 §self-application — production cutover rollback = 사용자 결정 분기 허용 영역).

### Step 5 — Execute

**5a. rollback path**
- marketplace.json `plugins[codeforge].channels[*].versions[]` revert (Story-5 downgrade asymmetry invariant 정합)
- consumer environment 의 plugin install version 강제 downgrade (`/plugins install codeforge@<previous-version>`)
- production WAL sample re-verify (rollback 후 4-evidence-quad 재measurement)

**5b. forward-fix path**
- hotfix Story 신설 (별 Story KEY)
- `hotfix-bypass:prod-cutover-deputy-evidence` label 부착 (warning tier 영역, ADR-024 Amendment 8 family member 정합)
- `[bypass-justification]` PR comment marker 의무 (CFP-845 framework + comment-prefix-registry-v1 v1.3 정합)
- production deploy 단계 hotfix → 4-evidence-quad re-verify

### Step 6 — Verify

ProductionEvidenceDeputy 4-evidence-quad re-run + cross-Story consistency check 4 entry:
- CSC-1: label-registry-v2 sequential MINOR bump (current 정합)
- CSC-2: ADR-72 amendment_log monotonic (current 정합)
- CSC-3: reconcile-protocol-v1 schema version (current 정합)
- **CSC-4 (신규, rollback path 만)**: rollback 정합 verify (downgrade asymmetry invariant + marketplace.json channels[] revert 정합)

### Step 7 — Postmortem

PMOAgent retro auto-trigger (ADR-045 mandate):
- retro_summary 안 RC#? entry append (root cause classification)
- learnings_count 갱신
- feedback_back_to_codeforge enumeration (codeforge-improvement label + carrier Story 발의 결정)

Structured postmortem (Google SRE workbook "Postmortem culture" chapter 답습):
- impact: production state 영향 시간 + 영향 사용자 수
- root cause: 5-WHY chain
- contributing factors: ProductionEvidenceDeputy spawn 시점 + 4-evidence-quad measurement gap
- action items: forcing function (workflow / ADR / agent mandate 보강)

## 경계

본 7-step protocol = Live touching consumer Story 영역 한정. wrapper governance Story (CFP-954 본 Story 자체 포함) = production cutover 영역 외 (code 0 + production deploy state 부재, ADR-72 §결정 6 wrapper-self-app N/A). rollback decision 의 사용자 결정 분기 = reconcile-protocol-v1 user_decision_branches 0 invariant 영역 외 (production cutover rollback 한정 허용, ADR-064 §self-application).

## 관련 ADR

- **ADR-72 §결정 5** — EPIC CLOSED gate evidence quad SSOT (Detect step trigger source)
- **ADR-72 §결정 6** — wrapper-self-app N/A invariant (경계)
- **ADR-014** — boundary axis (DR / disconnect / clock / rate / env, incident classification)
- **ADR-045** — retro mandatory trigger (Step 7 Postmortem PMOAgent auto-trigger)

## 변경 이력

| 날짜 (KST) | Story | 변경 |
|---|---|---|
| 2026-05-18 | CFP-954 | 최초 작성 — production cutover incident response 7-step rollback protocol narrative SSOT (Detect→Isolate→Assess→Rollback decision→Execute→Verify→Postmortem, Helm rollback + AWS CodeDeploy 답습) |
