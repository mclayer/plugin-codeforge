---
kind: domain_fact
type: domain-knowledge
area: production-cutover
topic_slug: production-cutover-readme
title: Production Cutover — narrative SSOT hub
status: Active
tags:
  - production-cutover
  - production-evidence-deputy
  - narrative-ssot-hub
  - release-lifecycle
  - cfp-954
related_adrs:
  - ADR-072   # ProductionEvidenceDeputy mandate SSOT (§결정 1-7)
  - ADR-076  # §결정 9.4 canary tier production-impact authority advisory
  - ADR-055  # Integration Test lane Amendment 3 Epic-level reactivation
  - ADR-014  # CONDITIONAL SubAgent base pattern (LiveOps + LiveOrdering + ProductionEvidence 3 CONDITIONAL)
  - ADR-016  # Amendment 3 family scope production publish (cross-ref)
  - ADR-063  # Amendment 6 §결정 17 marketplace channels[] matrix (cross-ref)
  - ADR-040  # worktree-first convention
  - ADR-073  # verify-before-assert (`frozen-SHA pin`)
  - ADR-082  # write-time self-write verification mandate
related_stories:
  - CFP-699  # grandparent Epic
  - CFP-882  # parent Epic (Wave 4 sub-Epic)
  - CFP-954  # 본 carrier Story (Story-3)
created: 2026-05-18
updated: 2026-05-18
---

# Production Cutover — narrative SSOT hub

본 페이지 = codeforge wrapper 의 **production cutover surface 운영 narrative SSOT** (CFP-954 carrier, Wave 4 sub-Epic #882 Story-3 — ProductionEvidenceDeputy mandate first activation 영역). ADR-072 / ADR-076 / ADR-055 3 ADR 의 cross-ref hub.

## 1. 도메인 개념

**Production cutover** = software 가 backtest/paper-only 환경에서 **real funds + live exchange API + production credential + live order placement** 영역으로 전환되는 시점. real-world failure mode 의 first emergence point — 사용자 explicit go-ahead 의무 + production-grounding 단일 owner 축 (ProductionEvidenceDeputy, ADR-072 §결정 1) 의무.

5-stage release lifecycle taxonomy (codeforge family plugin distribution):

| Stage | Carrier Story | scope |
|---|---|---|
| 1. schema declare | CFP-906 (MERGED) | 3-tier channel taxonomy SSOT declare layer |
| 2. runtime activation | CFP-932 (MERGED) | CLI/script/migration tool/drift detection workflow active |
| **3. production cutover** | **CFP-954 (본 Story)** | ProductionEvidenceDeputy mandate first activation + IntegrationTestAgent Epic-level reactivation + production-touching label registry append |
| 4. promotion criteria | Story-4 (TBD) | promotion criteria 4-tuple + marketplace.json channels[] populate |
| **5. downgrade asymmetry** | **CFP-1014 (MERGED)** | canary→beta→stable downgrade semantic invariant (reconcile-protocol-v1 v1.12 §4.14 `downgrade_asymmetry_marker.status: wired` declarative SSOT, §4.8 단독 promotion 선례 verbatim 답습, partial-active state 도입 0 / field shape 변경 0 / closed_enum length=2 invariant + open_extension:false) + **Wave 4 sub-Epic #882 close 최종 고정 (5/5 Story complete)** |

## 2. 4 industry exemplars (empirical anchor)

Researcher §A.1 정합 — codeforge family production cutover discipline 의 external anchor:

| Exemplar | Production cutover discipline | codeforge 적용 매핑 |
|---|---|---|
| **Kubernetes `kubectl rollout`** | 4-stage progressive rollout (canary → 25% → 50% → 100%) + auto-rollback on failure (rollout health probe — readiness / liveness / startup / metrics) | ADR-076 §결정 9 3-tier channel taxonomy = subset. canary tier = K8s canary equivalent. 4-tuple measurement source = K8s rollout health probe precedent 답습 |
| **Chrome 4-channel release** | Stable / Beta / Dev / Canary — 4 weeks cadence + automated promotion criteria | codeforge 3-tier (stable / beta / canary) = Chrome subset. promotion criteria 4-tuple = Chrome canary→dev→beta→stable promotion gate precedent 답습 (Story-4 carrier) |
| **Helm `helm rollback` + `helm test`** | Pre-rollback test gate + atomic rollback transaction (revision history + helm test smoke check) | Story-3 production-cutover-evidence.yml = Helm test gate precedent. rollback-protocol.md = Helm rollback discipline 답습 |
| **AWS CodeDeploy Blue/Green deployment** | Pre-cutover health check + post-cutover smoke test + auto-rollback (CloudWatch alarm based) | ProductionEvidenceDeputy 4-evidence-quad (bucket prefix listing / WAL sample / drainage rate / cadence trigger) = AWS CodeDeploy CloudWatch alarm precedent 답습 |

Additional 5th anchor: **Google SRE workbook "Postmortem culture"** chapter — incident response evidence + structured postmortem.

## 3. ProductionEvidenceDeputy mandate cross-ref

ADR-072 §결정 1-7 SSOT mandate scope 3 책임:
1. **Production evidence quad owner** — production state 실측 evidence 4중 (bucket prefix listing / WAL sample / L1 backlog drainage rate / L2/L3 cadence trigger)
2. **EPIC CLOSED gate 검증** — Epic close PR merge 직전 production evidence quad 충족 검증 (§결정 5)
3. **Post-cutover wiring inspection** — production cutover 후 compose.yml env / production deploy state / collector emit schema 실측 ↔ 가설 mismatch surface

Trigger axis (ADR-072 §결정 3, Live touching ↔ production cutover disjoint):
- Backtest/Paper-only: 6 permanent SubAgent
- Live touching pre-cutover: 8 SubAgent (6 + LiveOps + LiveOrdering)
- **Production cutover**: 9 SubAgent (6 + LiveOps + LiveOrdering + ProductionEvidence) — both spawn 의무
- wrapper governance: 6 SubAgent (ProductionEvidence wrapper-self-app N/A, ADR-072 §결정 6)

## 4. 4 prerequisite measurement source mechanical anchor 4-tuple (CFP-954 carrier)

| Anchor | Measurement source | 측정 방식 |
|---|---|---|
| MS-1 `live_touching` | Story file frontmatter (`live_touching: bool`) | `yaml.safe_load` (ADR-061 §결정 5 + CFP-699 CR-821-6 strict-verify) |
| MS-2 `production_cutover_touching` | dual-source AND: Story frontmatter + GitHub label `production-touching` | mismatch fail-loud Issue auto-create dedup signature |
| MS-3 `marketplace_publish_touching` | `git diff plugin.json .version` + `marketplace.json channels[]` field touch | Story-4 carrier (Phase 1 best-effort declare) |
| MS-4 `consumer_impact_blast_radius` | marketplace.json `plugins[codeforge].channels[]` consumer count proxy | ADR-068 I-5 dimensional empirical anchor (proxy approximation) |

## 5. Cross-ref

- `cutover-evidence-collection.md` — 4-evidence-quad 수집 절차 + sample method
- `rollback-protocol.md` — 7-step incident response (Helm rollback + AWS CodeDeploy 답습)
- ADR-072 §결정 1-7 SSOT
- consumer-guide.md §2j (production cutover 사용법)
- `tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml` (Epic-level baseline first)
- `templates/github-workflows/production-cutover-evidence.yml` + `scripts/check-production-cutover-evidence.sh`
