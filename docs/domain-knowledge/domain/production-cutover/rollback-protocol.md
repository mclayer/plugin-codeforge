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
  - ADR-045  # retro mandatory trigger (PMOAgent auto-trigger) + §D-9 escalation (안전장치 3 사후 알림)
  - ADR-105  # 자동 rollback 도메인 재정의 — Step 4 2-layer disjoint amend (user-decision layer 보존 + auto-rollback layer 신설) + 안전장치 4 AND
  - ADR-104  # 운영 phase 1st-class 정의 (S1) — wrapper-N/A / 0 API call 계승 source
  - ADR-087  # blue-green + 3-시간 보존 (안전장치 2 default anchor)
  - ADR-064  # 모달 어휘 forbid-list (안전장치 1) + §self-application 2-layer (Step 4 표)
related_stories:
  - CFP-882  # parent Epic (Wave 4 sub-Epic)
  - CFP-954  # 본 carrier Story (Story-3)
  - CFP-1191 # Step 4 amend carrier — 자동 rollback 도메인 재정의 (Epic CFP-1187 Story-2)
created: 2026-05-18
updated: 2026-05-22
---

# Production cutover — 7-step rollback protocol

## 정의

**7-step rollback protocol** = Live touching consumer Story 영역의 production cutover incident response 절차 (Detect → Isolate → Assess → Rollback decision → Execute → Verify → Postmortem). Helm rollback + AWS CodeDeploy Blue/Green 답습 (OperationalRiskArch §A.3 + Researcher §E.1 정합).

본 entry = production cutover incident response narrative SSOT — ProductionEvidenceDeputy / LiveOps / LiveOrdering 3 SubAgent 가 incident 시 참조하는 단일 절차 정의.

## 컨텍스트

ProductionEvidenceDeputy 4-evidence-quad 중 1+ failing 시 production cutover incident 진입. rollback (canary 이전 state 복귀) vs forward-fix (canary 유지 + hotfix Story) 결정 게이트는 **2 layer 로 분리**된다 (ADR-105 — CFP-1191 carrier):

- **user-decision layer** (기존, 보존) = 사용자 explicit decision 의무 영역 (reconcile-protocol-v1 user_decision_branches 0 invariant 영역 외 — production cutover rollback = 사용자 결정 분기 허용 영역, ADR-064 §self-application 정합). rollback vs forward-fix 가치 판단 분기 허용.
- **auto-rollback layer** (신규, ADR-105) = 안전장치 4 모두 충족(AND) 시 사람 승인 없이 자동 발동. 숫자 임계 deterministic 이므로 user_decision_branches 0 (invariant 영역 *내* — ADR-064 §self-application 2-layer 정밀화). 보존 기간(green→blue default 3h) 안에서만.

두 layer 는 disjoint — auto layer 자격을 잃는 모든 영역(안전장치 미충족 / 보존 기간 초과 / kill-switch 활성 / 임계 모호)은 전부 user-decision layer 로 복귀한다 (Step 4 표 참조).

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

rollback (canary 이전 state 복귀) vs forward-fix (canary 유지 + hotfix Story 신설) 결정 게이트는 **2 layer 로 분리**된다 (ADR-105 — CFP-1191). 기존 user-decision layer 는 **보존** 되고, auto-rollback layer 가 **신설** 된다 (단순 치환 아님 — 두 layer disjoint).

| layer | 발동 조건 | 결정 주체 | 결정 분기 (ADR-064 §self-application) | 보존 기간 | path |
|---|---|---|---|---|---|
| **user-decision layer** (기존, 보존) | 안전장치 4 중 1+ 미충족 / 보존 기간 초과 / kill-switch 활성 / 임계 모호 / forward-fix 판단 필요 | 사용자 (explicit go-ahead) | **있음** — rollback vs forward-fix 분기 허용 (`user_decision_branches: 0` invariant 영역 *외* 유지) | 무관 (사람이 판단) | Step 5a rollback path / Step 5b forward-fix path |
| **auto-rollback layer** (신규, ADR-105) | 안전장치 4 **모두 충족** (AND) | mechanism (deterministic) | **없음** — 숫자 임계 deterministic (`user_decision_branches: 0` invariant 영역 *내*) | green→blue default 3h **안에서만** (ADR-087 §결정 5) | Step 5a rollback path (사람 승인 없이 자동) |

**안전장치 4 (AND — 모두 충족 시에만 auto layer 진입, ADR-105 §결정 3)**:
1. **명확한 숫자 임계** — 에러율 / latency burn rate 등 숫자 + window 형식으로만 trigger. 모달·정성 어휘 금지 (ADR-064 forbid-list / ADR-058 §해소 기준 정합). 임계 모호 시 auto 진입 불가 → user-decision layer.
2. **보존 기간 안에서만** — green→blue 복귀가 데이터 손실 0 으로 가능한 보존 기간(default 3h, CFP-1059 / ADR-087 §결정 5 정합, consumer 확장 가능 / 축소 불가 ADR-064 §결정 7) 안에서만. 초과 시 자동 금지 → user-decision layer → Step 5b forward-fix.
3. **자동 rollback 후 사후 알림** — 자동 실행 ≠ 침묵 실행. 되돌린 직후 Issue 자동 발의 + PMOAgent escalation 의무 (ADR-045 §D-9 답습, 무음 rollback = 위반).
4. **kill-switch** — 자동 rollback mechanism 비활성화 토글 (예: `.codeforge/auto-rollback.disabled` filesystem flag 또는 config). 활성 시 auto layer 전체 무력화 → user-decision layer 만 동작. **kill-switch 가 다른 안전장치보다 우선** (ADR-014 boundary axis 정합).

> ⚠️ **kill-switch disambiguation** (ADR-105 §결정 5) — 산업 "kill switch"(rollback 실행 수단, traffic instant reroute) ↔ codeforge "kill-switch"(자동 rollback mechanism *비활성화* 토글) 는 **반대 방향**. 산업 = 되돌림 발동 / codeforge = 되돌림 자동화 차단.

- **user-decision rollback path**: production state 영향 reversible + 사용자 explicit decision 의무 (사용자 explicit go-ahead 의무 영역 — `user_decision_branches: 0` invariant 영역 외, ADR-064 §self-application — production cutover rollback = 사용자 결정 분기 허용 영역).
- **auto-rollback path**: 안전장치 4 AND 충족 시 mechanism 이 사람 승인 없이 자동 발동 (실 mechanism = S4 carrier).
- **forward-fix path**: rollback 영향 destructive 시 (예: WAL data 보존 의무) + hotfix Story 신설 + `hotfix-bypass:prod-cutover-deputy-evidence` label.

### Step 5 — Execute

**5a. rollback path**
- marketplace.json `plugins[codeforge].channels[*].versions[]` revert (reconcile-protocol-v1 v1.12 §4.14 `downgrade_asymmetry_marker.status: wired` declarative invariant 정합 — Story-5 CFP-1014 carrier 완료. rollback ≠ demotion boundary annotation: rollback = operational version revert layer (사용자 explicit go-ahead 의무) / demotion = channel tier 하향 declare 차단 layer (forward-only ratchet wired). 두 layer disjoint — rollback path 는 invariant 준수 검증 영역, demotion path 는 invariant 자체로 차단)
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
- **CSC-4 (신규, rollback path 만)**: rollback 정합 verify (reconcile-protocol-v1 v1.12 §4.14 `downgrade_asymmetry_marker.status: wired` declarative invariant — Story-5 CFP-1014 carrier 완료 + marketplace.json channels[] revert 정합 + rollback ≠ demotion boundary disjoint annotation 정합)

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

본 7-step protocol = Live touching consumer Story 영역 한정. wrapper governance Story (CFP-954 본 Story 자체 포함) = production cutover 영역 외 (code 0 + production deploy state 부재, ADR-72 §결정 6 wrapper-self-app N/A — 자동 rollback mechanism 실측도 wrapper N/A, ADR-105 §결정 4 / ADR-104 §결정 4 계승).

rollback decision 의 ADR-064 §self-application 정합은 **2 layer 로 disjoint** (ADR-105 §결정 2):
- **auto-rollback layer** = `user_decision_branches: 0` (숫자 임계 deterministic — invariant 영역 *내*, 안전장치 4 AND 충족 시).
- **user-decision layer** = 사용자 결정 분기 허용 (production cutover rollback 한정 — invariant 영역 *외* 유지).

"rollback decision = 분기 허용" 단일 진술은 본 amend 후 사용 금지 — 반드시 2-layer 로 분리 인용 (auto layer 분기 0 / user layer 분기 허용). 두 layer 는 disjoint 하며 한 layer 가 다른 layer 를 약화하지 않는다.

## 관련 ADR

- **ADR-72 §결정 5** — EPIC CLOSED gate evidence quad SSOT (Detect step trigger source)
- **ADR-72 §결정 6** — wrapper-self-app N/A invariant (경계)
- **ADR-014** — boundary axis (DR / disconnect / clock / rate / env, incident classification)
- **ADR-045** — retro mandatory trigger (Step 7 Postmortem PMOAgent auto-trigger)

## 변경 이력

| 날짜 (KST) | Story | 변경 |
|---|---|---|
| 2026-05-18 | CFP-954 | 최초 작성 — production cutover incident response 7-step rollback protocol narrative SSOT (Detect→Isolate→Assess→Rollback decision→Execute→Verify→Postmortem, Helm rollback + AWS CodeDeploy 답습) |
| 2026-05-22 | CFP-1191 | Step 4 amend — 자동 rollback 도메인 재정의 (ADR-105). user-decision layer 단일 게이트 → user-decision layer (보존) + auto-rollback layer (신규) **2-layer disjoint** 표 추가 (단순 치환 아님). 안전장치 4 AND codify (숫자 임계 / 보존 기간 안 / 사후 알림 / kill-switch) + kill-switch disambiguation (산업 ↔ codeforge 반대 방향) + ADR-064 §self-application 2-layer 정밀화 (auto layer 분기 0 / user layer 분기 허용). amend 위치 = 컨텍스트(L36) + Step 4(L64-70) + 경계(L108). Step 5 L75 rollback ≠ demotion disjoint 무변경 (보존). |
