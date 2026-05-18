---
title: Production cutover — 7-step rollback protocol (incident response)
area: production-cutover
introduced_by: CFP-954
parent_epic: CFP-882
status: active
date: 2026-05-18
related_adrs:
  - ADR-72   # §결정 5 EPIC CLOSED gate evidence quad
  - ADR-014  # boundary axis (DR / disconnect / clock / rate / env)
  - ADR-045  # retro mandatory trigger (PMOAgent auto-trigger)
related_files:
  - docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md
  - docs/domain-knowledge/domain/production-cutover/README.md
  - docs/domain-knowledge/domain/production-cutover/cutover-evidence-collection.md
---

# Production cutover — 7-step rollback protocol

OperationalRiskArch §A.3 + Researcher §E.1 정합 — Helm rollback + AWS CodeDeploy Blue/Green 답습. Live touching consumer Story 영역의 production cutover incident response 7-step.

## Step 1 — Detect

ProductionEvidenceDeputy 4-evidence-quad 중 1+ failing 감지:
- bucket prefix listing 0 (production storage write 0)
- WAL sample schema mismatch (production schema ↔ 실 row schema diff > 0)
- drainage rate > ingest rate (L1 backlog 누적, drainage_rate / ingest_rate > 1.0)
- cadence trigger window mismatch (cadence_actual_window vs designed_window deviation > tolerance budget)

Detection source: production-cutover-evidence.yml workflow (PR-time) + manual workflow_dispatch (operations team pre-verify) + Prometheus alert (continuous monitoring).

## Step 2 — Isolate

production-touching label 부착 PR / Story open 시 즉시:
- `phase:완료` label 보류 (phase-gate-mergeable 차단)
- `retro-pending` label 부착 (PMOAgent retro auto-trigger forcing function)
- Live touching consumer 영역에서 추가 Story commit pause (operations team manual decision)

## Step 3 — Assess

ProductionEvidenceDeputy + LiveOps + LiveOrdering 3 SubAgent 동시 spawn (consumer Story 영역 시 ADR-72 §결정 3 trigger axis 정합):
- ProductionEvidenceDeputy = 실측 evidence verify
- LiveOps = production env containment + runbook 검증
- LiveOrdering = order placement state + reconciliation invariant verify

## Step 4 — Rollback decision

rollback (canary 이전 state 복귀) vs forward-fix (canary 유지 + hotfix Story 신설) 결정 게이트:
- **rollback path**: production state 영향 reversible + 사용자 explicit decision 의무
- **forward-fix path**: rollback 영향 destructive 시 (예: WAL data 보존 의무) + hotfix Story 신설 + `hotfix-bypass:prod-cutover-deputy-evidence` label

**사용자 explicit go-ahead 의무 영역** (reconcile-protocol-v1 user_decision_branches: 0 invariant 영역 외, ADR-064 §self-application — production cutover rollback = 사용자 결정 분기 허용 영역).

## Step 5 — Execute

### 5a. rollback path
- marketplace.json `plugins[codeforge].channels[*].versions[]` revert (Story-5 downgrade asymmetry invariant 정합)
- consumer environment 의 plugin install version 강제 downgrade (`/plugins install codeforge@<previous-version>`)
- production WAL sample re-verify (rollback 후 4-evidence-quad 재measurement)

### 5b. forward-fix path
- hotfix Story 신설 (별 Story KEY)
- `hotfix-bypass:prod-cutover-deputy-evidence` label 부착 (warning tier 영역, ADR-024 Amendment 8 family member 정합)
- `[bypass-justification]` PR comment marker 의무 (CFP-845 framework + comment-prefix-registry-v1 v1.3 정합)
- production deploy 단계 hotfix → 4-evidence-quad re-verify

## Step 6 — Verify

ProductionEvidenceDeputy 4-evidence-quad re-run + cross-Story consistency check 4 entry:
- CSC-1: label-registry-v2 sequential MINOR bump (current 정합)
- CSC-2: ADR-72 amendment_log monotonic (current 정합)
- CSC-3: reconcile-protocol-v1 schema version (current 정합)
- **CSC-4 (신규, rollback path 만)**: rollback 정합 verify (downgrade asymmetry invariant + marketplace.json channels[] revert 정합)

## Step 7 — Postmortem

PMOAgent retro auto-trigger (ADR-045 mandate):
- retro_summary 안 RC#? entry append (root cause classification)
- learnings_count 갱신
- feedback_back_to_codeforge enumeration (codeforge-improvement label + carrier Story 발의 결정)

Structured postmortem (Google SRE workbook "Postmortem culture" chapter 답습):
- impact: production state 영향 시간 + 영향 사용자 수
- root cause: 5-WHY chain
- contributing factors: ProductionEvidenceDeputy spawn 시점 + 4-evidence-quad measurement gap
- action items: forcing function (workflow / ADR / agent mandate 보강)

## Cross-ref

- ADR-72 §결정 5 SSOT (EPIC CLOSED gate evidence quad)
- ADR-045 retro mandatory trigger
- README.md (도메인 anchor)
- cutover-evidence-collection.md (4-evidence-quad sample method)
- Helm rollback semantic guide (atomic rollback transaction)
- AWS CodeDeploy Blue/Green deployment whitepaper (pre/post cutover health check)
