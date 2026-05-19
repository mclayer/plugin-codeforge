---
adr_number: 72
title: ProductionEvidence Deputy 신설 + EPIC cutover gate evidence quad — production-grounding 단일 owner 축
status: Accepted
category: governance
date: 2026-05-14
is_transitional: false
carrier_story: CFP-632
epic: CFP-620
related_stories:
  - CFP-632
related_adrs:
  - ADR-005
  - ADR-014
  - ADR-040
  - ADR-042
  - ADR-045
  - ADR-058
  - ADR-063
  - ADR-068
  - ADR-070
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/parallel-work/section-ownership.yaml
mechanical_enforcement_actions:
  - action: production-cutover-deputy-spawn-evidence
    status: warning
    bypass_label: hotfix-bypass:prod-cutover-deputy-evidence
    script_path: scripts/check-production-cutover-evidence.sh
    workflow_path: templates/github-workflows/production-cutover-evidence.yml
    progress_note: "CFP-954 (Story-3) 가 status 승격: deferred-followup → warning. detect_command (scripts/check-production-cutover-evidence.sh) + workflow (templates/github-workflows/production-cutover-evidence.yml) 신설 + .github/workflows/ byte-identical mirror 동반. 4 prerequisite measurement source mechanical anchor 4-tuple (MS-1 live_touching / MS-2 production_cutover_touching dual-source AND / MS-3 marketplace_publish_touching / MS-4 consumer_impact_blast_radius) Change Plan §3.5 정의. ratchet 강화 방향 (deferred-followup → warning) — ADR-058 §결정 5 sunset_justification 영역 외. follow-up CFP-Z 신설 영역 — review-verdict-v4 v4.5 → v4.6 MINOR bump (owner_deputy_kind enum production_evidence 추가) + verdict packet field-time check (warning → blocking-on-pr 승격 carrier). bypass_label CFP-651 정정 (54자 → 41자 GitHub 50자 제한 정합) 유지."
    target_section: §결정 3
  - action: epic-cutover-gate-evidence-quad-check
    status: warning
    bypass_label: hotfix-bypass:epic-cutover-quad-check
    script_path: scripts/check-production-cutover-evidence.sh
    workflow_path: templates/github-workflows/production-cutover-evidence.yml
    progress_note: "CFP-954 (Story-3) 가 status 승격: deferred-followup → warning. detect_command + workflow 신설 (production-cutover-evidence.yml 가 EPIC CLOSED gate evidence quad lint 통합 영역 — PR-open trigger 안 epic close gate sub-section verify). Sibling Story-4 (plugin-codeforge-pmo#18) PMOAgent retro epic_close_gate template 본문 작성 = warning → blocking-on-pr 승격 prerequisite (별 carrier). 4중 evidence (bucket prefix listing / WAL sample / Prometheus rate metric / drainage rate) verify scope = consumer Live touching Epic 한정 (wrapper-self-app N/A, §결정 6 정합). ratchet 강화 방향 — ADR-058 §결정 5 sunset_justification 영역 외. bypass_label CFP-651 정정 (51자 → 36자) 유지."
    target_section: §결정 5
amendment_log:
  - amendment_number: 1
    date: 2026-05-14
    carrier_story: CFP-651
    summary: "frontmatter mechanical_enforcement_actions[] 2 entry에 bypass_label 필드 신설 + GitHub 50자 제한 정합 단축값 적용. action name 자체 unchanged. evidence-checks-registry.yaml 2 entry bypass_label 동 단축 (CFP-651 정정 동반)."
  - amendment_number: 3
    date: 2026-05-19
    carrier_story: CFP-991
    summary: "Wave 4 sub-Epic #1 Story-4 carrier — canary promotion criteria 4-tuple wiring + canary cross-repo coordination + reconcile-protocol-v1 v1.10 → v1.11 §4.14 canary_compatibility_check_binding sibling carrier. (a) §결정 1 표 wrapper governance row append — `CFP-991 — promotion criteria 4-tuple wiring + canary cross-repo coordination + reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding` entry 추가 (Story-3 CFP-954 row 뒤). (b) §결정 5 표 row append — promotion criteria 4-tuple SSOT cross-ref (functional + security + monitoring + testing measurement source, ADR-076 §결정 9.6 Chrome 3-channel verbatim cite). (c) §결정 6 wrapper-self-app N/A invariant 보존 — Story-4 = declare-time Tier-1 exemption (production_cutover_touching=true AND repo=wrapper AND code_change=0 triple-AND fast-PASS), consumer canary→beta promotion = Tier-2 admin-tier 권장 (advisory only). (d) mechanical_enforcement_actions retain status `warning` (Story-4 declare-only 영역, blocking-on-pr 승격 carrier = follow-up CFP). (e) sibling label-registry-v2 v2.34 → v2.35 MINOR (4 신규 entry: 1 hotfix-bypass:canary-promotion-criteria 46번째 family member + 3 gate:channel-{canary,beta,stable}-promotion). (f) 5 threat × mitigation matrix cross-ref — T-1.1 wrapper Tier-1 declare-time bypass (canary_consumer_evidence_origin enum closed-set) + T-2.1 silent canary uptake CFP-906 답습 + T-3.1 gate label mis-attach (attach_owner_plugin: consumer_repo_only + workflow mechanical guard) + T-4.1 4-tuple measurement spoofing (ADR-070 §결정 D6 CFP-988 mandatory-real-execution-evidence STANDING cross-ref) + T-5.1 downgrade asymmetry Story-5 prerequisite (placeholder_reserve). (g) ratchet 강화 방향 — ADR-058 §결정 5 sunset_justification 영역 외 (declare → enforcement transition + 4 신규 label entry + §결정 1/§결정 5 표 row append, scope 확장 only). (h) 8-mirror checklist self-application — ADR-72 (2-digit form) / ADR-076 (3-digit form) 정식 form 정확 사용 invariant. variant form 도입 0건 의무 (CFP-906 + CFP-932 + CFP-954 lineage pattern_count 3 reach 차단). (i) ADR-070 §결정 D6 (CFP-988 Amendment 4) cross-ref — mandatory-real-execution-evidence STANDING 4-tuple ((a) CR-own discriminating revert / (b) reconcile-integration path / (c) DevPL pasted stdout 미신뢰 / (d) single-aggregator/single-unit bypass forbidden) 가 §4.14 promotion gate evaluation 시점 single-aggregator bypass 금지 mitigation 영역 (T-4.1 4-tuple measurement spoofing direct verify 의무)."
  - amendment_number: 2
    date: 2026-05-18
    carrier_story: CFP-954
    summary: "Wave 4 sub-Epic #882 Story-3 carrier. (a) frontmatter mechanical_enforcement_actions[0/1].status `deferred-followup → warning` 2 entry 동시 승격 (production-cutover-deputy-spawn-evidence + epic-cutover-gate-evidence-quad-check) — Story-3 progress_note `follow-up CFP-Z` 의 정확한 carrier. (b) `script_path: scripts/check-production-cutover-evidence.sh` + `workflow_path: templates/github-workflows/production-cutover-evidence.yml` 2 신설 field-time 추가 — null → populated. (c) **4 prerequisite measurement source SSOT 신설** — MS-1 live_touching (Story frontmatter yaml.safe_load) / MS-2 production_cutover_touching (dual-source AND: frontmatter + GitHub label `production-touching` — false-positive 0 보장 + dual-source mismatch fail-loud Issue auto-create) / MS-3 marketplace_publish_touching (git diff plugin.json `.version` + marketplace.json channels[] field touch — Story-4 carrier 영역 best-effort declare) / MS-4 consumer_impact_blast_radius (marketplace.json channels[] consumer count proxy, ADR-068 I-5 empirical anchor). (d) Story-3 = 4 prerequisite mechanical anchor declare scope only — 실 first ProductionEvidenceDeputy spawn = consumer Story 영역 (예: mctrader live touching production cutover Story). wrapper-self-app N/A invariant (§결정 6) 정합 — Story-3 자체는 declare-time Tier-1 exemption 영역. (e) production-cutover-evidence.yml = PR-open + workflow_dispatch 2-trigger split (D2 consensus, cron 24h 미권고 — production cutover = event-driven not continuous monitoring). (f) wrapper-self-app exemption 2-tier (D3 consensus): Tier-1 (repo=wrapper, declare-time scope check) + Tier-2 (repo=consumer, runtime 4-evidence-quad measurement). (g) ratchet 강화 방향 — ADR-058 §결정 5 sunset_justification 영역 외. follow-up CFP-Z = review-verdict-v4 v4.5 → v4.6 MINOR bump (owner_deputy_kind enum production_evidence 추가) carrier (warning → blocking-on-pr 승격 prerequisite). always-pass 패턴 3rd occurrence 차단 = 3-layer defense (`|| true` 금지 lint + 2-assertion 의무 + discriminating fixture TDD RED phase) D5 consensus 적용. 8-mirror checklist self-application — ADR-72 / ADR-076 정식 form 사용, non-canonical 3-digit / 2-digit ADR ref 변종 도입 0건 invariant (CFP-906 pattern_count 18 + CFP-932 pattern_count 9 → CFP-954 = 3-Story pattern_count 차단 적기)."
---

# ADR-72: ProductionEvidence Deputy 신설 + EPIC cutover gate evidence quad — production-grounding 단일 owner 축

## 상태

Accepted (2026-05-14) — CFP-632 Story-1 anchor 의 §결정 산출물. Phase 1 PR merge 시 `ADR-RESERVATION.md` row 72 = `reserved → active` 전환 (GitOpsAgent self-write).

## 컨텍스트

mctrader 3-cycle 누적 패턴 분석 (CFP-620 post-mortem) 결과 동일 root cause 패턴이 3 회 반복:

- **Cycle N**: review lane 4 lane (DesignReview / CodeReview / IntegrationTest / SecurityTest) PASS → EPIC CLOSED → production cutover 시점 wiring / data flow 결함 검출 → mctrader hotfix Story 신설 → 추가 cycle 진입
- 모든 4 lane PASS evidence = **mock-only 검증 자체** (ArchitectAgent §7 design spec → QADev §8 Test Contract → integration test = mock service / fixture / synthetic data 기반). production env compose.yml / production deploy state / collector emit schema 실측 grounding 부재.
- ArchitectPL Phase 1 SubAgent 6 permanent + 2 CONDITIONAL (LiveOps + LiveOrdering) 중 **production state 실측 grounding owner 부재** — OpRiskArch 는 §7.4 (DR / disconnect / clock / rate / env) **design-time policy SSOT** 정의 owner (ADR-014 §결정 1 정합). 실 production env 의 invariant 충족 evidence 명시 owner 책임 공백.
- EPIC CLOSED gate (PMOAgent retro epic_close_gate) 가 **mock test PASS + CI PASS + PR merge** 만 의무 — production 실측 evidence (bucket prefix listing / WAL sample / Prometheus rate metric / drainage rate 4중) gate 항목 부재.

본 누적 결함 패턴을 차단하기 위해 **production-grounding 단일 owner 축** 필요. ADR-014 Amendment 1 (CFP-77 LiveOps + LiveOrdering CONDITIONAL SubAgent 신설) 패턴 reuse — 3번째 CONDITIONAL SubAgent 로 ProductionEvidenceDeputy 신설.

### Scope 분리 (boundary axis)

ProductionEvidenceDeputy 의 책임은 **runtime-evidence** (production state 실측 명시) — OpRiskArch §7.4 의 **design-time SSOT** (invariant 정의) 와 별도 축. 두 SubAgent 의 mandate overlap 영역 (DR backup verify / env secret state / clock drift 실측 / rate metric / bucket prefix env isolation) 70%+ 발생 추정 — boundary axis 명시 의무 (§결정 4 명시). Story-2 (#633) 가 ADR-014 Amendment 3 본문 작성 시 양 ADR 의 cross-ref 양 방향 의무.

## 결정

### §결정 1 — ProductionEvidenceDeputyAgent 신설 (3번째 CONDITIONAL SubAgent)

ADR-014 §결정 1 (6 permanent SubAgent) + Amendment 1 §결정 6 (2 CONDITIONAL = LiveOps + LiveOrdering) 가 **6 permanent + 3 CONDITIONAL** 로 확장:

- **ProductionEvidenceDeputyAgent** (CONDITIONAL — Live touching Story OR production cutover 영향 Story 한정, §결정 3 spawn condition 정합)
- canonical agent file = sibling PR (codeforge-design plugin) `agents/production-evidence-deputy.md` NEW
- wrapper 책임 = CLAUDE.md "Deputy mandate 매트릭스" 9번째 row 추가 (ADR-012 §3 4번째 예외 — wrapper SSOT 보유 영역 = matrix row only)
- agent file 본문 작성 = 본 ADR-72 정책 ground 후 sibling PR (codeforge-design plugin) carrier

본 SubAgent 는 ArchitectPL 의 SubAgent spawn 결정 분기 (§결정 3 spawn condition 충족 시) 에 추가됨. 6+2 → 6+3 CONDITIONAL 확장 (ADR-014 Amendment 1 패턴 reuse).

### §결정 2 — Mandate scope (3 책임 + 7-cell mandate matrix overlap 명시)

ProductionEvidenceDeputy 의 mandate scope 3 책임:

1. **Production evidence quad owner** — production state 실측 evidence 4중 명시 책임:
   - bucket prefix listing (boto3 / gcloud 결과 verbatim)
   - WAL sample 실측 (production storage WAL row sample)
   - L1 backlog drainage rate (1h sustained 측정, ≤ ingest rate 의무)
   - L2/L3 자연 cadence trigger 실측 (5min or 1h window)
2. **EPIC CLOSED gate 검증** — Epic close PR merge 직전 production evidence quad 충족 검증 (§결정 5 정합)
3. **Post-cutover wiring inspection** — production cutover 후 wiring reflect 검증 (compose.yml env / production deploy state / collector emit schema 실측 ↔ 가설 mismatch surface)

**Mandate matrix 7 cell** (OpRiskArch §7.4 sub × ProductionEvidence 책임 overlap):

| ProductionEvidence 책임 | OpRiskArch §7.4 sub | overlap 영역 | 1차 owner | 2차 owner consult |
|---|---|---|---|---|
| production evidence quad owner | §7.4.1 DR | DR backup 실측 evidence (snapshot 명시 vs DR policy 정의) | 양 측 consult | OpRiskArch (policy 정의) + ProductionEvidence (실측) |
| production evidence quad owner | §7.4.2 Cancel-on-disconnect | drainage rate ↔ disconnect timing | OpRiskArch primary | ProductionEvidence cross-ref (drainage 실측 명시) |
| production evidence quad owner | §7.4.3 Clock sync | clock drift 실측 vs tolerance budget | 양 측 consult | OpRiskArch (budget 정의) + ProductionEvidence (drift 실측) |
| production evidence quad owner | §7.4.4 Rate limit | Prometheus rate metric ↔ token bucket 정책 | OpRiskArch primary | ProductionEvidence cross-ref (metric 실측 명시) |
| production evidence quad owner | §7.4.5 Env isolation | bucket prefix listing / env secret state | **양 측 consult (분쟁 가장 강한 cell)** | OpRiskArch (containment 정책 — ADR-014 Amendment 2 §결정 3) + ProductionEvidence (env state 실측) |
| EPIC CLOSED gate 검증 | (5 sub cross-cut) | gate quad evidence | ProductionEvidence primary | OpRiskArch consult (policy 정합 검증) |
| Post-cutover wiring inspection | (5 sub cross-cut) | cutover 후 wiring reflect 검증 | ProductionEvidence primary | OpRiskArch consult (policy 충족 verify) |

overlap density 5/7 = 71% — boundary axis 명시 의무 (§결정 4) 정합. ADR-014 Amendment 2 §결정 3 (env secret ownership 경계: SecurityArch threat owner / OpRiskArch containment owner) 가 5번째 cell (env isolation) 의 직접 영향 — Story-2 (#633) ADR-014 Amendment 3 가 SecurityArch / OpRiskArch / ProductionEvidence 3-way 충돌 처리 단락 작성 의무 (Story-2 carrier).

### §결정 3 — Spawn condition (Live touching ↔ production cutover disjoint trigger axis + SubAgent spawn both 의무)

ProductionEvidenceDeputy spawn 조건 = **Live touching Story OR production cutover 영향 Story** 한정 (Change Plan §13 안 `production_cutover_touching: true` 선언 또는 §13 Live Operational Discipline 본문 보유 Story).

**Trigger axis 분리 표** (Live touching ↔ production cutover disjoint):

| Story 유형 | LiveOps | LiveOrdering | OpRiskArch | ProductionEvidence | 비고 |
|---|---|---|---|---|---|
| Backtest/Paper-only | X | X | ✓ | X | 6 permanent SubAgent 만 |
| Live touching pre-cutover | ✓ | ✓ | ✓ | X | 8 SubAgent (6 + LiveOps + LiveOrdering) — production cutover 영역 외 |
| Production cutover (consumer Story) | ✓ | ✓ | ✓ | ✓ | 9 SubAgent (6 + LiveOps + LiveOrdering + ProductionEvidence) — both spawn 의무 |
| wrapper governance (예: 본 ADR-72 Phase 1 = CFP-632 + mandate activation = CFP-954) | X | X | ✓ | X (wrapper-self-app N/A) | §결정 6 정합 — Amendment 2 (CFP-954) 가 mandate 의 **first activation declare** 영역 (production-cutover-evidence.yml workflow + check-production-cutover-evidence.sh + evidence-checks-registry 2 entry status 승격), 실 first spawn = consumer Story 영역 |
| wrapper governance (CFP-991 Story-4 — canary promotion criteria enforcement layer wiring + canary cross-repo coordination + reconcile-protocol-v1 v1.10 → v1.11 §4.14 `canary_compatibility_check_binding` sibling carrier) | X | X | ✓ | X (wrapper-self-app N/A) | §결정 6 정합 — Amendment 3 (CFP-991) 가 promotion criteria 4-tuple SSOT 의 **enforcement layer carrier** (canary-promotion-criteria.yml workflow + check-canary-compatibility.sh + scripts/lib/canary-compatibility-helpers.sh + evidence-checks-registry `canary-compatibility-check` entry warning tier + label-registry v2.34→v2.35 4 신규 entry), 실 consumer canary→beta promotion gate runtime evaluation = Tier-2 consumer Story 영역. wrapper PR 자체 = Tier-1 declare-time exemption (`production_cutover_touching=true AND repo=wrapper AND code_change=0` triple-AND fast-PASS, ADR-72 §결정 6 invariant 정합) |

**SubAgent spawn both 의무**: Live touching + production cutover both = OpRiskArch + LiveOps + LiveOrdering + ProductionEvidence both spawn (총 9 SubAgent). 한쪽만 spawn 금지 — boundary axis (design-time vs runtime-evidence) 의 정합 검증 의무. ProductionEvidence trigger ⊂ Live touching trigger (reverse 는 false — Live touching but pre-cutover Story 는 OpRiskArch + LiveOps + LiveOrdering 만 spawn, ProductionEvidence inactive).

ArchitectPL 의 spawn 결정 분기 (`docs/orchestrator-playbook.md` §3.2 표):

- Backtest/Paper-only: 6 SubAgent
- Live touching pre-cutover: 8 SubAgent (6 + 2 CONDITIONAL Live)
- Production cutover: **9 SubAgent (6 + 3 CONDITIONAL — Live + ProductionEvidence)**

Token cost 영향: production cutover Story 가 Live Mode Epic 의 ~30% 추정 (cutover 시점 child Story 한정) — 평균 Live touching Story 의 token overhead 추가 ~10-15%.

### §결정 4 — Boundary axis 명시 (design-time SSOT vs runtime-evidence)

> **policy SSOT (OperationalRiskArch §7.4 — DR / disconnect / clock / rate / env 의 invariant 정의) vs evidence SSOT (ProductionEvidenceDeputy production grounding subsection — invariant 충족 실측 명시)**

본 boundary axis 1줄 명시 = ADR-014 Amendment 3 (Story-2 carrier #633) 가 양 방향 cross-ref 의무. Story-2 가 ADR-014 본문에 본 boundary axis verbatim 통합 + ADR-014 Amendment 2 §결정 3 (SecurityArch / OpRiskArch env secret ownership 경계) 와 본 ADR-72 §결정 2 5번째 cell (env isolation 양 측 consult) 의 3-way 충돌 처리 단락 작성 의무 (Story-2 직접 작성 영역 — 본 ADR-72 는 의무만 명시).

본 boundary axis 의 enforcement = ArchitectPL SubAgent spawn 결정 분기 (§결정 3) + DesignReviewPL §7.4 / production grounding subsection 정합성 검증 (sibling Story-3 영역, plugin-codeforge-review#34). 본 ADR-72 author 시점 = boundary axis 1줄 명시만, mechanical enforcement = follow-up CFP scope (frontmatter `mechanical_enforcement_actions[].status: deferred-followup` 정합).

### §결정 5 — EPIC CLOSED gate evidence quad 신설

PMOAgent retro epic_close_gate 가 다음 4중 evidence 명시 의무 (Live touching Epic 한정 — wrapper governance Epic / doc-only Epic 자연 N/A):

1. **Production bucket prefix listing evidence** — boto3 / gcloud 결과 verbatim (bucket name + prefix path + object count + sample object key)
2. **WAL sample 실측** — production storage WAL row sample (timestamp + payload schema 정합 verify)
3. **L1 backlog drainage rate (1h 측정)** — drainage rate ≤ ingest rate 의무 (drainage_rate / ingest_rate ≤ 1.0)
4. **L2/L3 자연 cadence trigger 실측** — 5min or 1h window trigger 실측 명시 (cadence_actual_window vs designed_window mismatch surface)
5. **(CFP-991 Amendment 3 carrier) Canary promotion criteria 4-tuple SSOT cross-ref** — reconcile-protocol-v1 v1.11 §4.14 `canary_compatibility_check_binding.promotion_criteria_4tuple` (functional + security + monitoring + testing measurement source SSOT, ADR-076 §결정 9.6 Chrome 3-channel Stable/Beta/Canary verbatim 4 industry exemplar cite). 본 4-tuple = canary → beta promotion gate evaluation 영역 (consumer canary tier 활성 Story carrier 영역, wrapper Story-4 = declare-time exemption Tier-1 영역). gate evaluation 시점 4-tuple all 'pass' OR 'n_a' 충족 = promotion gate proceed / 1+ 'fail' = promotion abort. ADR-070 §결정 D6 (CFP-988 Amendment 4) mandatory-real-execution-evidence STANDING 4-tuple cross-ref (T-4.1 4-tuple measurement spoofing mitigation — single-aggregator bypass forbidden + real execution evidence direct verify 의무). label-registry v2.35 `gate:channel-{canary,beta,stable}-promotion` 3 entry mechanical marker.

**사용자 ack quad 5중** (Story-1 anchor 사용자 ack):
- bucket 콘솔 evidence 명시 + log evidence + Prometheus metric + drainage 4중 + 사용자 ack signature

PMOAgent retro epic_close_gate 본문 = sibling PR (codeforge-pmo plugin) `templates/retro.md` carrier 영역 — 본 ADR-72 = mandate ground 만 (gate 항목 본문 = sibling PR 작성). epic_close_gate evidence quad 미충족 시 Epic close 차단 (gate verify FAIL → PR merge block).

본 EPIC CLOSED gate evidence quad mandate = **Live touching Epic 한정 의무**. wrapper 자체 Epic (예: CFP-612 / CFP-628 governance / doc-only Epic) = N/A 자연 분류 (ADR-005 plugin self-application N/A 표준 정합).

### §결정 6 — Wrapper-self-app N/A 명문화 (ADR-005 cross-ref)

wrapper plugin 자체 = production cutover 영역 외 (plugin = code 0 + runtime behavior 0 + production deploy state 부재). 따라서 ProductionEvidenceDeputy 의 wrapper-self-app trigger = **영구적으로 N/A**.

본 ADR-72 가 도입하는 ProductionEvidenceDeputy 자체는 Live touching consumer Story (mctrader 등) 에서 spawn 되나, wrapper plugin 자체 변경 Story (governance / docs / SubAgent mandate matrix 추가 등) 는 본 SubAgent spawn 영역 외. ADR-005 (Plugin Self-Application N/A 표준화) §결정 1 N/A 표기 형식 (`plugin-meta-na` 면제 분류) 정합.

본 ADR-72 자체 = wrapper governance ADR (code 0 + runtime behavior 0) — `production_cutover_touching: false` 명시 의무 (Change Plan §13 정합).

### §결정 7 — Agent model = Opus tier (ADR-042 mandate-depth SubAgent)

ProductionEvidenceDeputyAgent = **Opus tier** (claude-opus-4-7).

근거 (ADR-042 §결정 1 (d) Security / safety boundary owner 정합):
- production state 실측 grounding = high-stakes domain interpretation (mctrader Live trading + KRW exchange + real funds 컨텍스트)
- mandate-depth SubAgent = 6 permanent SubAgent (SecurityArch / OpRiskArch / DataMigrationArch / TestContractArch) 와 동일 tier. 2 CONDITIONAL Live (LiveOps / LiveOrdering — ADR-042 §결정 1 (e) inheritance Opus) 와 동일 tier
- mctrader 3-cycle 누적 결함 패턴의 catch-rate 우선 결정 — Sonnet swap 시 production state 실측 evidence 누락 / mismatch surface 약화 위험 (cycle 0 목표 미달성 risk)

ADR-042 §결정 3 (신규 agent 도입 시 ADR 의무) 정합 — 본 ADR-72 §결정 7 이 model selection ADR 의무 충족.

### §결정 8 — Follow-up CFP-Z reservation 명시 (review-verdict-v4 `owner_deputy_kind` MINOR bump carrier)

본 ADR-72 신설 시점 review-verdict-v4 schema 의 `findings[].owner_deputy_kind` enum 영역 영향 검증 결과:

- 현행 enum: `codebase_mapper` / `refactor` / `security_architect` / `operational_risk_architect` / `data_migration_architect` / `test_contract_architect` / `live_ops` / `live_ordering` (6 permanent + 2 CONDITIONAL)
- ProductionEvidenceDeputy 신설 시 enum 추가 필요: `production_evidence` (3rd CONDITIONAL)
- 본 enum 추가 = review-verdict-v4 MINOR bump (additive enum, backward-compat 유지) — ADR-008 §결정 2 정합

본 enum 추가 = **별도 CFP-Z carrier 영역** (본 ADR-72 = mandate ground 만, contract schema 변경은 follow-up CFP). carrier 의무 명시:

- **CFP-Z (잠정)**: review-verdict-v4 v4.5 → v4.6 MINOR bump (`owner_deputy_kind` enum `production_evidence` 추가) + sibling sync (6 lane plugin mirror, ADR-010) + ProductionEvidenceDeputy spawn evidence verdict packet field-time check. CFP-954 Story-3 가 status `deferred-followup → warning` 1차 승격 carrier (amendment_log Amendment 2). CFP-Z = warning → blocking-on-pr 2차 승격 prerequisite carrier (별 carrier scope).
- **CFP-Z' (잠정)**: PMOAgent retro epic_close_gate evidence quad workflow 통합 (retro-mandatory.yml 확장) + evidence-checks-registry append (`epic-cutover-gate-evidence-quad-check` warning tier 등록)

본 §결정 8 = ADR-72 author 시점 schema gap 명시 + 후속 carrier 의무 명시. ratchet 강화 방향 (mandate scope 확장 — 8 → 9 SubAgent enum) — ADR-058 §결정 5 정합 (sunset_justification 불필요, 강화 방향).

## 관련 ADR

| ADR | 관계 |
|---|---|
| ADR-014 (Operational Risk SSOT Distribution) + Amendment 1 (CFP-77 CONDITIONAL SubAgent) + Amendment 2 (CFP-378 reconciliation 경계) | **직접 패턴 source** — 6 permanent + 2 CONDITIONAL SubAgent 패턴 reuse. boundary axis (design-time SSOT vs runtime-evidence) 정합 검증 의무 = Amendment 3 (Story-2 #633 carrier). 본 ADR-72 §결정 4 가 boundary axis 1줄 명시 + Amendment 3 cross-ref. Amendment 2 §결정 3 (env secret ownership 경계) ↔ 본 §결정 2 5번째 cell (env isolation 양 측 consult) 3-way 충돌 처리 = Story-2 carrier 본문 작성 의무. |
| ADR-005 (Plugin Self-Application N/A 표준화) | **wrapper-self-app N/A 표준** — §결정 6 정합. wrapper governance Story / Epic = ProductionEvidenceDeputy spawn 영역 외 (`plugin-meta-na` 면제 분류). |
| ADR-042 (Agent Model Selection Policy) + Amendment 5 | **신규 agent ADR 의무** — §결정 3 정합. ProductionEvidenceDeputy = Opus tier (§결정 7). mandate-depth SubAgent = 6 permanent SubAgent + 2 CONDITIONAL Live 와 동일 tier. |
| ADR-058 (ADR Sunset Criteria Mandate) | **`is_transitional: false` (governance permanent) 정합** — §결정 7 보안 ADR default presumption + governance default 동일 적용. sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (§결정 5 정합). |
| ADR-068 (Boundary Completeness Invariants) + Amendment 1 (CFP-528 I-5 dimensional empirical grounding) | **production grounding = empirical grounding 의 specialization** — Story-3 (sibling carrier #34 plugin-codeforge-review) 가 I-5 verdict field-time enforcement 추가 시 production_grounding_present sub-field 추가 가능. ADR-72 §결정 5 evidence quad = I-5 의 production-specific 적용 사례. |
| ADR-070 (Codex Verify-Before-Trust) | **design-stage verify-before-trust specialization** — ProductionEvidence = design-stage production grounding evidence verification (verify-before-trust 의 production env 적용). chief author 가 production state 실측 evidence 직접 verify 의무 (file path reference 만 사용 금지 정합). |
| ADR-040 (Worktree Convention) + Amendment 3 (mechanical_enforcement_actions[]) | **frontmatter `mechanical_enforcement_actions[]` 의무** — 본 ADR-72 frontmatter 2 entry (production-cutover-deputy-spawn-evidence + epic-cutover-gate-evidence-quad-check) 보유. `status: deferred-followup` — evidence-checks-registry append 완료 (CFP-632 FIX iter 1, deferred-followup status). detect script + workflow integration 만 follow-up CFP-Z / CFP-Z' carrier 영역. schema verbatim (ADR-040 §결정 7.A) 정합. |
| ADR-063 (Marketplace Atomic Invariant) | **plugin.json bump 검증** — 본 ADR-72 = wrapper governance change. plugin.json bump 영역 = §결정 1 + §결정 2 가 wrapper CLAUDE.md "Deputy mandate 매트릭스" row 추가 만 변경 (SubAgent mandate scope 정의는 wrapper SSOT 보유 영역 = ADR-014 §결정 2 정합). plugin.json MINOR bump 후보 = false (wrapper SSOT 본문 변경 없음 — matrix row 추가만, ADR-005 plugin-meta-na 정합). marketplace_sync_declared = false (Phase 1 PR 영역). 단 follow-up CFP-Z 가 review-verdict-v4 MINOR bump 시 sibling sync + plugin.json MINOR bump 동반 가능 (별도 carrier scope). |
| ADR-045 (Story Retro Mandatory Trigger) | **EPIC CLOSED gate evidence quad sibling** — Story-4 (#18 plugin-codeforge-pmo) 가 PMOAgent retro Cross-Story pattern ≥2 ADR trigger 추가. 본 ADR-72 §결정 5 evidence quad 가 PMOAgent retro template 확장 영역 (Story-4 sibling carrier). |
| ADR-042 Amendment 7 + ADR-014 Amendment 4 (CFP-676 atomic carrier) | **InfraOperationalArchitect rename mirror cross-ref** — OperationalRiskArchitectAgent → InfraOperationalArchitectAgent rename 후에도 본 ADR-72 §결정 2/§결정 4 boundary axis (policy SSOT vs evidence SSOT) 무변경 계승. ProductionEvidenceDeputy ↔ InfraOperationalArchitect disjoint axis 정합. 하단 "CFP-676 mirror cross-ref" 단락 참조. |

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (governance permanent — ADR-058 §결정 7 보안/governance default presumption 정합).

Amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 sunset_justification 차단):
- scope 확장 (3 책임 → 4+ 책임 추가, 또는 mandate matrix 7 cell → 8+ cell 확장)
- 강도 강화 (deferred-followup → warning → blocking-on-pr 승격 별도 CFP)
- enforcement surface 확장 (production cutover Story → 추가 Story 유형 확장 별도 CFP)

약화 방향 (3 책임 축소 / spawn condition 완화 / ProductionEvidenceDeputy 자체 deprecate) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

## 결과

### 긍정

- mctrader 3-cycle 누적 결함 패턴 차단 — production-grounding 단일 owner 축 (ProductionEvidenceDeputy) 신설로 cycle 0 목표
- ArchitectPL Phase 1 SubAgent 6+2 → 6+3 CONDITIONAL 확장 (ADR-014 Amendment 1 패턴 reuse 검증된 mechanism)
- EPIC CLOSED gate evidence quad 의무로 production 실측 evidence 명시 강제 (mock-only 검증의 silent pass-through 차단)
- boundary axis (design-time SSOT vs runtime-evidence) 명시 명시로 OpRiskArch ↔ ProductionEvidenceDeputy mandate 분쟁 차단 (Fix-3 H17 SubAgent mandate boundary 분쟁 재발 risk 차단)
- ADR-068 I-5 dimensional empirical grounding 의 production-specific 적용 사례 추가 — empirical grounding invariant ratchet 강화 방향

### 부정 / 트레이드오프

- production cutover Story = 9 SubAgent spawn (6+3 CONDITIONAL) — token overhead 평균 ~10-15% 추가 (Live touching Story 의 30% 추정 적용 시)
- sibling PR 2종 (codeforge-design + codeforge-pmo) coordination overhead — wrapper PR merge 후 즉시 진행 의무 (ADR-010 sibling sync)
- ProductionEvidenceDeputy agent 본문 작성 = sibling PR scope (codeforge-design plugin) — 본 ADR-72 author 시점 = mandate ground 만, agent file 본문 부재 시 ArchitectPL fallback (현재 OperationalRiskArchitectAgent + 추가 chief authoring 패턴, ADR-014 Amendment 1 §결정 8 정합)
- mandate matrix 7 cell overlap 71% 영역 — boundary axis enforcement 부재 시 두 SubAgent 동시 spawn 시 verdict packet `findings[].owner_deputy` field 충돌 (verdict_v4 field-level 분쟁) → ArchitectPL dedup 책임. follow-up CFP-Z = review-verdict-v4 v4.5 → v4.6 MINOR bump (`owner_deputy_kind` enum `production_evidence` 추가) carrier 의무
- mechanical enforcement 부재 (Phase 1 = `deferred-followup` tier) — follow-up CFP-Z + CFP-Z' merge 까지 author 자발적 준수 + DesignReview lane review 가 1차 안전망

### Trade-off

- mandate scope (3 책임 — production evidence quad owner + EPIC CLOSED gate 검증 + post-cutover wiring inspection) 의 명시성 우선 / mandate 비대 위험 trade-off 에서 명시성 우선 (Phase 0 brainstorm 사용자 default 3번 명시 정합)
- spawn condition (Live touching Story OR production cutover 영향 Story) 의 disjoint trigger 명시성 우선 / token cost 증가 trade-off 에서 명시성 우선 (Phase 0 brainstorm 사용자 default 4번 명시 정합)

## 거부된 대안

본 ADR 은 결정 = ProductionEvidenceDeputy 신설 (CONDITIONAL 3번째 SubAgent) — 아래 대안 거부:

- **(b) OpRiskArch mandate 확장 옵션** — OpRiskArch §7.4 에 production grounding subsection 추가만 (신규 SubAgent 신설 X). 거부 사유: OpRiskArch mandate 비대 (5 sub + production grounding subsection 추가 시 6 sub 영역) + design-time policy 와 runtime-evidence 두 axis 혼재 + ADR-014 Amendment 2 §결정 3 (env secret ownership 경계) 정합 깨짐. Phase 0 brainstorm Researcher boundary axis 분리 의무 (사용자 default 6번) + Continuity 70%+ overlap 분석 + ADR-014 H17 (SubAgent 경계 분쟁) 재발 risk evidence 종합 결과 reject.
- **(c) ProductionEvidence 책임을 LiveOps + LiveOrdering 양 SubAgent 에 분산** — production evidence quad owner = LiveOps / EPIC CLOSED gate 검증 = LiveOrdering 분산. 거부 사유: 책임 split 시 dedup 책임 ArchitectPL 에 떠넘겨짐 + production state 실측 evidence 의 단일 owner 축 약화 + mandate matrix 7 cell overlap 영역의 정합 검증 owner 부재.
- **(d) PMOAgent retro template 만 확장 (SubAgent 신설 X)** — EPIC CLOSED gate evidence quad 만 PMOAgent retro 본문에 추가, design-stage production grounding owner 부재. 거부 사유: design 시점 production grounding 의무 부재 → review lane 4 lane PASS 후 EPIC close 직전 evidence quad 검증 시점에 결함 검출 → 차기 cycle 진입 (mctrader 3-cycle 패턴 재발). design-stage owner 신설이 cycle 0 목표 정합.
- **(e) 자연 확장 (ADR-014 변경 없음, ProductionEvidence 책임 chief author 가 직접 흡수)** — ArchitectAgent chief author 가 production grounding 책임 직접 보유. 거부 사유: chief author 의 multi-source synthesis 책임 (8 SubAgent 산출물 통합) 과 production state 실측 grounding 책임 (single-mandate advocate) 혼재. mandate-depth SubAgent 패턴 (ADR-042 §결정 1 (d) 정합) 위반.

## 다이어그램

```
[Story §1 사용자 요구사항]
        ↓
[ArchitectPL deputy spawn 결정 분기]
        ↓
   ┌────┴──────────────────────────────────┐
   │                                        │
[Backtest/Paper-only]              [Live touching Story]
6 permanent deputy                  ┌─────┴──────────────┐
                                     │                    │
                              [pre-cutover]      [production cutover]
                              8 deputy            9 deputy (both 의무)
                              (6 + LiveOps        (6 + LiveOps
                               + LiveOrdering)     + LiveOrdering
                                                   + ProductionEvidence)
                                                          ↓
                                                  ┌───────┴────────────┐
                                                  │                    │
                                          [design-time SSOT]   [runtime-evidence]
                                          OpRiskArch §7.4      ProductionEvidence
                                          DR/disconnect/       production grounding
                                          clock/rate/env       subsection
                                                  │                    │
                                                  └────────┬───────────┘
                                                           ↓
                                                  [boundary axis]
                                                  policy SSOT vs evidence SSOT
                                                  (Amendment 3 cross-ref 의무)
```

## 관련 파일

- `CLAUDE.md` (wrapper) — "Deputy mandate 매트릭스" 섹션 6+2 → 6+3 CONDITIONAL 갱신 + 9번째 row (ProductionEvidence) 추가
- `docs/orchestrator-playbook.md` — §3.2 ArchitectPL SubAgent spawn 결정 분기 표 갱신 (Backtest/Paper / Live pre-cutover / production cutover 3 분기)
- `docs/parallel-work/section-ownership.yaml` — ADR-50 cross-section conflict detection (Story-2 ADR-014 Amendment 3 충돌 방지 row 추가 검토)
- `docs/adr/ADR-RESERVATION.md` — row 72 = `reserved → active` 전환 (Phase 1 merge 시 GitOpsAgent self-write)
- **Sibling PR 2종 (declaration only)**:
  - `mclayer/plugin-codeforge-design/agents/ArchitectPLAgent.md` — SubAgent roster 9번째 entry (CONDITIONAL) 추가
  - `mclayer/plugin-codeforge-design/agents/production-evidence-deputy.md` (NEW) — agent 본문 작성 (본 ADR-72 가 spec mandate ground)
  - `mclayer/plugin-codeforge-design/CLAUDE.md` — SubAgent roster 매트릭스 갱신 (8 → 9 = PL + chief + 7 SubAgent)
  - `mclayer/plugin-codeforge-pmo/templates/retro.md` — epic_close_gate 섹션 안 production evidence quad 4중 항목 추가
- **Follow-up carrier**:
  - CFP-Z (잠정) — review-verdict-v4 v4.5 → v4.6 MINOR bump (`owner_deputy_kind` enum `production_evidence` 추가) + ProductionEvidenceDeputy spawn evidence verdict packet field-time check
  - CFP-Z' (잠정) — PMOAgent retro epic_close_gate evidence quad workflow 통합 (retro-mandatory.yml 확장) + evidence-checks-registry append

## 외부 reference

- mctrader 3-cycle 누적 패턴 (Epic CFP-620 post-mortem)
- mctrader-hub Live Mode Epic (ADR-014 Amendment 1 carrier)
- Sibling Story-2 (ADR-014 Amendment 3): https://github.com/mclayer/plugin-codeforge/issues/633
- Sibling Story-3 (ADR-068 Amendment 2 — verdict field-time enforcement): https://github.com/mclayer/plugin-codeforge-review/issues/34
- Sibling Story-4 (PMOAgent retro Cross-Story pattern): https://github.com/mclayer/plugin-codeforge-pmo/issues/18
- Sibling Story-5 (DevPL/QADev spec invariant verify gate): https://github.com/mclayer/plugin-codeforge-develop/issues/24

---

## CFP-676 mirror cross-ref — InfraOperationalArchitect rename boundary axis 무변경 (신규 §결정 아님)

> **번호 미부여 cross-ref 단락** (collision 0 — 본 ADR-72 §결정 1~8 본문 변경 0건). CFP-1026 S1 ([ADR-042](ADR-042-agent-model-selection-policy.md) Amendment 7 + [ADR-014](ADR-014-operational-risk-ssot-distribution.md) Amendment 4 atomic carrier) 의 design lane agent 구조 재편이 OperationalRiskArchitectAgent → **InfraOperationalArchitectAgent** rename 을 수행함에 따른 mirror cross-ref. 본 단락 = ADR-72 ↔ ADR-014 양 방향 cross-ref 정합 유지만, 신규 §결정 / mandate scope 변경 / spawn condition 변경 0건.

**식별자 정합 (Codex S-CFP676-ADR72-FORM P2 / Story §5.3 EC-1 / memory CFP-932 sentinel)**: 본 ADR file 의 정식 식별자 = **`ADR-72`** (2-digit form, frontmatter `adr_number: 72`, file `docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md`). `ADR-072` (3-digit zero-pad) 는 본 ADR 의 식별자 아님 — CFP-676 carrier 전 anchor (ADR-042 Amendment 7 / ADR-014 Amendment 4 / CLAUDE.md / skills/deputy-mandate/SKILL.md / Change Plan / Story §3·§7) 에서 2-digit form 통일 의무 (ADR-068 I-4 wording SSOT 정합). CFP-906 + CFP-932 + CFP-954 3-form 혼동 lineage pattern_count 차단.

**ProductionEvidenceDeputy ↔ InfraOperationalArchitect disjoint axis (rename 후 무변경)**:

- 본 ADR-72 §결정 1 (ProductionEvidenceDeputy 신설 3번째 CONDITIONAL) + §결정 2 (7-cell mandate matrix) + §결정 4 (boundary axis: policy SSOT vs evidence SSOT) 의 OperationalRiskArch 측 owner = rename 후 **InfraOperationalArchitect** 로 verbatim substitute (mandate scope / overlap cell / boundary axis 정의 0건 변경 — rename 만).
- **InfraOperationalArchitect** = §7.4 design-time policy SSOT owner (DR / disconnect / clock / rate / env / container invariant 정의 — 상시 6 permanent SubAgent). **ProductionEvidenceDeputy** = production state runtime-evidence owner (실측 명시 — CONDITIONAL, Live touching OR production cutover Story 한정).
- §결정 3 spawn condition 표 (Backtest/Paper = 6 / Live pre-cutover = 8 / production cutover = 9 = 6 + LiveOps + LiveOrdering + ProductionEvidence) 의 "6 permanent SubAgent" = SecurityArchitect / TestContractArchitect / DataArchitect (DataMigrationArchitect rename) / InfraOperationalArchitect (OperationalRiskArch rename) / CodeArchitect (CFP-676 신설) + (4-tuple sub-agent CodebaseMapper/Refactor/ArchitectAnalyst 는 deputy column 아님 — flat-spawn sub-tuple, ADR-044 CFP-676 reaffirm 단락 정합). **deputy 명단 = 5 permanent + 3 CONDITIONAL** (CLAUDE.md "Deputy mandate 매트릭스" + skills/deputy-mandate/SKILL.md CFP-676 S1 동시 갱신).
- **wrapper-self-app N/A invariant 무변경** (§결정 6 — ADR-005 `plugin-meta-na`): CFP-676 자체 = wrapper governance Story (code 0 + runtime behavior 0) → ProductionEvidence spawn 영역 외. InfraOperationalArchitect rename 은 deputy 명칭 SSOT 변경 (정책 문서) — production cutover trigger 무관.

**Scope 경계**: 본 cross-ref 단락 = ADR-72 정책 SSOT 무변경 declare 만. ProductionEvidenceDeputyAgent agent file 본문 (`agents/production-evidence-deputy.md`) + InfraOperationalArchitect agent file rename = W2 S3 (codeforge-design sibling Story) 영역. 본 CFP-676 S1 = wrapper 정책 SSOT (ADR / CLAUDE.md / skill) 만 (doc-only fast-path — [ADR-054](ADR-054-doc-only-fast-path.md)).

---

## 변경이력

- **2026-05-14 v1 (Accepted, CFP-632)**: 초기 결정 — ProductionEvidenceDeputyAgent 신설 (CONDITIONAL 3번째 SubAgent) + EPIC CLOSED gate evidence quad + boundary axis (design-time SSOT vs runtime-evidence) 명시 + 7-cell mandate overlap matrix + Live touching ↔ production cutover disjoint trigger axis + Opus tier + wrapper-self-app N/A + follow-up CFP-Z reservation.
- **2026-05-19 mirror cross-ref (CFP-676 — ADR-72 본문 정책 0건 변경)**: CFP-1026 S1 (ADR-042 Amendment 7 + ADR-014 Amendment 4 atomic carrier) 의 OperationalRiskArchitectAgent → InfraOperationalArchitectAgent rename 에 따른 mirror cross-ref 단락 추가 (번호 미부여, 신규 §결정 아님). §결정 1~8 본문 / mandate scope / spawn condition / boundary axis 정의 **0건 변경 invariant** — rename 반영 + 2-digit form (ADR-72) 식별자 정합 명문화 (Codex S-CFP676-ADR72-FORM P2 / wording SSOT ADR-068 I-4). `## 관련 ADR` 표 ADR-042 Amendment 7 + ADR-014 Amendment 4 row 동반 (양방향 backref).
