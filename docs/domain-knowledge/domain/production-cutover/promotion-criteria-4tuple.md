---
kind: domain_fact
area: production-cutover
title: "Promotion Criteria 4-tuple — Canary→Beta→Stable Promotion Gate Evidence Quad"
domain: production-cutover
topic_slug: promotion-criteria-4tuple
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/domain-knowledge/domain/production-cutover/promotion-criteria-4tuple.md
created: 2026-05-19
updated: 2026-05-19
created_by: CFP-991  # Wave 4 sub-Epic #1 Story-4 carrier
carrier_adrs:
  - ADR-72 Amendment 3  # ProductionEvidenceDeputy mandate + EPIC cutover gate evidence quad — §결정 3 trigger axis 표 wrapper governance row + §결정 5 evidence quad 표 row (Amendment 3)
  - ADR-076 §결정 9.6   # 3-tier channel taxonomy declaration — promotion criteria 4-tuple SSOT empirical anchor (4 industry exemplar)
  - ADR-016 Amendment 3 # codeforge family scope 7 plugin × channel pin invariant
  - ADR-063 Amendment 5 # marketplace atomic invariant — publisher↔registry↔consumer 3-way version atomic
  - ADR-063 Amendment 6 # mirrored field × channel matrix
  - ADR-070 §결정 D6    # Codex verify-before-trust — mandatory-real-execution-evidence STANDING (CFP-988 Amendment 4)
related_contracts:
  - reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding
  - label-registry-v2 v2.35 (4 신규 entry: hotfix-bypass:canary-promotion-criteria + gate:channel-{canary,beta,stable}-promotion)
---

# Promotion Criteria 4-tuple — codeforge canary → beta → stable transition gate SSOT

## 정의

**promotion criteria 4-tuple** = consumer canary tier 활성 후 beta tier (또는 beta → stable) promotion gate 평가 시점의 **4 measurement source SSOT**:

1. **functional** (기능 정합성) — consumer Story functional test pass-rate
2. **security** (보안 정합성) — consumer Story SecurityTestPLAgent verdict + ProductionEvidenceDeputy spawn evidence
3. **monitoring** (관측 정합성) — consumer production-side monitoring metric
4. **testing** (통합 정합성) — consumer Story IntegrationTestAgent verdict (Epic-level baseline)

각 measurement source 별 `gate_state` enum (`pass` / `fail` / `n_a`) 의무. **aggregation rule**: 4 sub all `pass` OR (`pass` + `n_a` 조합) = promotion gate proceed / 1+ `fail` = promotion abort (warning_first → blocking_on_pr fallback orthogonality, ADR-060 §결정 5 default).

각 measurement 의 `evidence_origin` annotation 의무 (closed-set enum `wrapper_self` / `consumer_self` / `mixed`, open_extension: false — RefactorAgent C-1) — T-1.1 wrapper Tier-1 declare-time bypass mitigation core field.

## 컨텍스트

본 4-tuple SSOT 는 Wave 4 sub-Epic #1 (Epic CFP-882, multi-version channel pin) 의 **2nd production cutover surface** 영역. Wave 4 sub-Epic #882 Story-3 (CFP-954 production cutover layer mandate first activation) 이후 Story-4 (CFP-991) 가 promotion criteria enforcement layer carrier.

**3 carrier layer 분리** (CFP-906 + CFP-932 + CFP-991 lineage):
- Story-1 (CFP-906) = declare layer SSOT only (channel taxonomy 3-tier stable/beta/canary 선언)
- Story-2 (CFP-932) = runtime active layer (channel drift detection + channel-aware version pin runtime)
- **Story-4 (CFP-991) = enforcement layer carrier (promotion criteria 4-tuple gate evaluation + canary cross-repo coordination)**
- Story-5 (별 CFP) = downgrade asymmetry invariant declarative carrier

**boundary 2-tier disjoint** (ADR-72 §결정 6 wrapper-self-app N/A invariant 정합):
- **Tier-1 declare-time exemption** (wrapper PR scope) — code 0 + runtime 0 + secret/credential 0 변경, fast-PASS triple-AND `production_cutover_touching=true AND repo=wrapper AND code_change=0`
- **Tier-2 runtime measurement** (consumer canary tier 활성 Story scope) — admin-tier 권장 advisory, HIGH risk class

## 핵심 규칙

### 4-tuple measurement source codeforge 도메인 mapping

| Sub | codeforge 도메인 measurement source | evidence_origin enum 활용 |
|---|---|---|
| functional | consumer Story bats GREEN ratio + integration test PASS evidence (codeforge-test lane IntegrationTestAgent verdict) | wrapper_self (wrapper Story scope) / consumer_self (consumer Story scope) / mixed (양 source 혼합) |
| security | consumer Story SecurityTestPLAgent verdict (codeforge-review SecurityTestPL) + ProductionEvidenceDeputy spawn evidence (consumer canary tier 활성 Story carrier 영역) | consumer_self (production-impact mandate) |
| monitoring | consumer production-side monitoring metric (Prometheus rate / WAL sample / drainage rate — ADR-72 §결정 5 evidence quad 정합) | consumer_self (consumer production env scope) |
| testing | consumer Story IntegrationTestAgent verdict (Epic-level baseline v2 — ADR-055 Amendment 3 §결정 1, baseline-v2-cfp-991.yaml 신설 carrier 영역) | consumer_self (Epic-level baseline scope) |

### family_7_atomic × channel × promotion gate 3-axis cross-product

- **family_7_atomic invariant** (ADR-016 §결정 1 + Amendment 3): consumer `.claude/_overlay/project.yaml codeforge.channel.tier: canary` 선언 시 family 7 plugin (wrapper + 6 lane plugin) 모두 동일 channel 으로 resolve 의무. per-plugin channel override forbidden.
- **publisher_versions length_invariant = 7** (RefactorAgent C-3 + DataMigrationArch INV-C):
  - member_enum = `["codeforge", "codeforge-requirements", "codeforge-design", "codeforge-develop", "codeforge-test", "codeforge-review", "codeforge-pmo"]`
  - 6/8 deviation = validator FAIL exit 2
- **three_way_match invariant** (ADR-063 Amendment 5 §결정 15): publisher 7 plugin × registry marketplace.json `channels[tier=canary].version[]` × consumer `codeforge.channel.tier=canary` declared 3-way byte-identical 의무

### promotion_gate_failure_mode 단방향 ratchet

- `warning_first → blocking_on_pr` 단방향 escalation (ADR-060 evidence-enforceable 4-tier promotion gate 정합)
- 역방향(blocking → warning) 약화 시도 = ADR-058 §결정 5 sunset_justification 의무 — 차단
- default = `warning_first` (Phase 1 = warning tier 활성)
- bypass_label = `hotfix-bypass:canary-promotion-criteria` (label-registry-v2 v2.35 45번째 family member)

## 경계

### wrapper Tier-1 declare-time / consumer Tier-2 runtime boundary

본 4-tuple SSOT 는 wrapper Story scope 외 (consumer canary tier 활성 Story carrier 영역). wrapper PR (Story-4 carrier) = schema declare + workflow + scripts/lib + label-registry entry append 영역만 (code 0 + runtime 0 + secret/credential 0 변경 invariant). 실 promotion gate evaluation = consumer canary→beta promotion PR open 시점 (Tier-2 runtime measurement, ProductionEvidenceDeputy spawn 영역).

### downgrade scope 외 (Story-5 carrier)

stable → beta demotion / beta → canary demotion 영역 = Story-5 carrier (placeholder_reserve). 본 4-tuple SSOT = forward path (canary → beta → stable promotion) 한정. downgrade asymmetry marker = §4.14 `downgrade_asymmetry_marker.status: placeholder_reserve` field 영역 (Story-5 Phase 1 = wired 단독 promotion 의무, §4.8 version_handshake placeholder_reserve→active 선례 verbatim 답습).

### marketplace.json channels[] real populate scope 외

본 Story-4 = §4.10 `registry_channel_matrix.story_4_scope_write_carrier` A3 정정 entry forward-effective realize point declare. 실 marketplace.json `plugins[name=codeforge].channels[]` field cross-repo write = sequential carrier (Story-4 declare-only / consumer marketplace governance gate).

### wrapper-self-app N/A invariant (영구)

ADR-72 §결정 6 verbatim — wrapper plugin 자체 = production cutover 영역 외 (plugin = code 0 + runtime behavior 0 + production deploy state 부재). 따라서 본 4-tuple SSOT 의 wrapper-self-app trigger = **영구적으로 N/A** (Tier-1 declare-time exemption fast-PASS).

## 관련 ADR

| ADR | 관계 |
|---|---|
| **ADR-72 Amendment 3** | 본 4-tuple SSOT 의 carrier ADR — §결정 1 표 wrapper governance row append + §결정 5 evidence quad 표 row append (5번째 row promotion criteria 4-tuple cross-ref). amendment_log Amendment 3 (CFP-991 carrier) |
| **ADR-076 §결정 9.6** | 4 industry exemplar SSOT (Chrome 3-channel Stable/Beta/Canary primary + npm dist-tag + Rust 3-channel + K8s 3-stage 보조 reference). 본 4-tuple 의 empirical anchor source |
| ADR-016 §결정 1 + Amendment 3 | codeforge family scope 7 plugin atomic + channel 차원 확장 — family_7_atomic_canary_pin invariant SSOT |
| ADR-063 Amendment 5 §결정 15 | publisher↔registry↔consumer 3-way version atomic invariant — three_way_match field cross-ref |
| ADR-063 Amendment 6 §결정 17 | mirrored field × channel matrix — marketplace.json `plugins[name=codeforge].channels[]` per-channel version snapshot SSOT |
| ADR-070 §결정 D6 (CFP-988 Amendment 4) | mandatory-real-execution-evidence STANDING 4-tuple ((a) CR-own discriminating revert / (b) reconcile-integration path / (c) DevPL pasted stdout 미신뢰 / (d) single-aggregator/single-unit bypass forbidden) — T-4.1 4-tuple measurement spoofing mitigation 영역 cross-ref. promotion gate evaluation 시점 single-aggregator bypass forbidden + real execution evidence direct verify 의무 |
| ADR-060 (evidence-enforceable promotion framework) | `canary-compatibility-check` evidence-checks-registry entry warning-tier carrier + bypass_label `hotfix-bypass:canary-promotion-criteria` channel |
| ADR-058 §결정 5 (sunset criteria mandate) | promotion_gate_failure_mode 약화 방향(blocking → warning) 차단 invariant |
| ADR-055 Amendment 3 §결정 1 | IntegrationTestAgent Epic-level baseline first activation — Story-4 = baseline-v2-cfp-991.yaml (promotion criteria 4-tuple executable, Story-3 baseline-v1 후속) |

## 변경 이력

- **2026-05-19 CFP-991 신설**: Wave 4 sub-Epic #1 Story-4 canary promotion criteria enforcement layer carrier. ADR-72 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding sibling carrier. 4 industry exemplar verbatim cite (Chrome 3-channel primary + 보조 3개). wrapper Tier-1 declare-time exemption + consumer Tier-2 runtime measurement boundary 2-tier disjoint invariant. family_7_atomic × channel × promotion gate 3-axis cross-product mapping. downgrade scope (Story-5 carrier) / marketplace.json channels[] real populate scope (sequential carrier) / wrapper-self-app N/A scope (영구) 3 boundary 명시.
