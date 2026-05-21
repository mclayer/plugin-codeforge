---
kind: registry
registry: imperative-walker-protocol
version: "1.0"
status: Active
sibling_sync: exempt (ADR-010 §결정 2 kind:registry)
supersedes_carrier: reconcile-protocol-v1 (v1.13 Deprecated, CFP-1125)
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md
date: 2026-05-21
authors:
  - ArchitectAgent (CFP-1145 / CFP-1111 Wave 1 Story-3 — imperative-walker-protocol-v1 신설 codify, 7 ADR (ADR-092~098) 결정 SSOT carrier. reconcile-protocol-v1 v1.13 Deprecated 후속 carrier)
carrier_story: CFP-1145 (CFP-1111-W1-S3)
parent_epic: CFP-1111
related_adrs:
  - ADR-092  # changelog SSOT location (per-plugin self-owned CHANGELOG.md) — §3 codify source
  - ADR-093  # completion report 4-field schema (walk_result 4-value closed_enum + 2-layer 4-field) — §2 codify source
  - ADR-094  # consumer legacy version fallback policy (hybrid grace GA 12mo / Beta 9mo) — §4 codify source
  - ADR-095  # sunset metric standardization (metric source changelog mining + cron) — §5 codify source
  - ADR-096  # min_prerequisite_version manifest schema (dual carrier + topological resolve) — §6 codify source
  - ADR-097  # paradigm replacement governance anchor (paradigm scope boundary) — §7 codify source
  - ADR-098  # UpgradeAgent runtime ownership (PMO 흡수 ownership) — §7 codify source
  - ADR-076  # declarative reconciliation upgrade — paradigm replacement 대상 paradigm, walk_result semantic 원천 + UpgradeAgent runtime SSOT
  - ADR-008  # versioning (kind:registry MINOR/PATCH sibling sync 면제)
  - ADR-010  # sibling sync (kind:registry exempt — §결정 2)
  - ADR-058  # ADR sunset criteria mandate (ratchet 강화 방향 invariant)
  - ADR-064  # decision principle mandate (CFP scope unitary + self-application ratchet)
related_files:
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md  # v1.13 Deprecated, paradigm replacement source (semantic 답습 source)
  - docs/adr/ADR-092-changelog-ssot-location.md
  - docs/adr/ADR-093-completion-report-4field-schema.md
  - docs/adr/ADR-094-consumer-legacy-version-fallback-policy.md
  - docs/adr/ADR-095-sunset-metric-standardization.md
  - docs/adr/ADR-096-min-prerequisite-version-manifest-schema.md
  - docs/adr/ADR-097-paradigm-replacement-governance-anchor.md
  - docs/adr/ADR-098-upgrade-agent-runtime-ownership.md
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md
related_plugins:
  - codeforge (wrapper, owner of walker runtime semantic)
  - codeforge-requirements
  - codeforge-design
  - codeforge-review
  - codeforge-develop
  - codeforge-test
  - codeforge-pmo
version_history:
  - { version: "1.0", date: 2026-05-21, carrier: CFP-1145, change: "initial — imperative changelog walk paradigm 의 walker protocol schema SSOT 신설. reconcile-protocol-v1 (v1.13 Deprecated, CFP-1125) 후속 carrier. 7 ADR (ADR-092~098) 결정 codify: §2 walk_result 4-value closed_enum + 2-layer 4-field 보고 schema (ADR-093) / §3 per-plugin self-owned CHANGELOG.md SSOT + aggregate view derived + drift detection warning tier (ADR-092) / §4 hybrid grace period fallback GA 12mo · Beta 9mo (ADR-094) / §5 sunset metric source changelog mining + cron (ADR-095) / §6 min_prerequisite_version dual carrier + topological resolve (ADR-096) / §7 paradigm replacement scope boundary 3 조건 AND (ADR-097) + UpgradeAgent runtime ownership PMO 흡수 (ADR-098). kind:registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합). closed_enum open_extension:false invariant 보존 (ADR-064 §self-application ratchet 강화 방향만)." }
---

# imperative-walker-protocol-v1 — Inter-plugin Contract Registry

codeforge family upgrade 의 imperative changelog walk paradigm 의 walker protocol schema SSOT. per-plugin self-owned `CHANGELOG.md` 7 source 의 walk → walk_result + 4-field 완료 보고 → consumer fallback / sunset metric / min_prerequisite_version manifest 영역의 walker 행동 schema 를 정의한다.

**kind**: registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합)

> verified-via: Read docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md (L55 + L168 — "kind: registry 파일 ... 본 MANIFEST 범위 밖" + "Scope limitation: kind:contract 만 적용 (kind:registry — fix-event / label-registry / debate-protocol 등 — 본 script 적용 외)" verbatim — kind:registry sibling sync 면제)

## §1 개요

본 contract = imperative changelog walk paradigm 의 **walker protocol SSOT** 다. reconcile-protocol-v1 (declarative reconciliation, v1.13 Deprecated — CFP-1125) 의 **후속 carrier** 로서, declarative desired-state 선언 paradigm 을 imperative changelog walk 절차 paradigm 으로 전환하는 paradigm replacement (ADR-097) 진행 중의 walker 행동 schema 를 codify 한다.

**paradigm replacement context (ADR-097 정합)**: declarative reconciliation (ADR-076) 을 imperative changelog walk paradigm 으로 wholesale 대체하는 governance event 는 ADR-097 §결정 1 paradigm replacement scope boundary (closed-set 3 조건 AND) 자격 영역이다. 본 contract 는 그 전환의 walker runtime 행동 surface 를 정의하며, 9+ ADR/contract bulk sunset 의 carrier-preserved sunset (ADR-097 §결정 3 — 효용 lossless carry) 를 reproduce 하는 schema carrier 다. reconcile-protocol-v1 §4.13 walk_result enum semantic 은 본 contract §2 로 lossless carry 된다 (paradigm shift 후 효용 보존).

**본 contract codify source (7 ADR)**:

| § | 영역 | codify source ADR | 핵심 결정 |
|---|---|---|---|
| §2 | walk_result + 4-field 완료 보고 schema | ADR-093 | walk_result 4-value closed_enum + 2-layer 4-field (외부 보고 / 내부 schema) |
| §3 | changelog SSOT location | ADR-092 | per-plugin self-owned `CHANGELOG.md` + aggregate view derived + drift detection |
| §4 | consumer fallback 정책 | ADR-094 | hybrid grace period (GA 12mo / Beta 9mo) |
| §5 | sunset metric | ADR-095 | metric source = changelog mining + cron |
| §6 | min_prerequisite_version manifest | ADR-096 | dual carrier + topological resolve |
| §7 | paradigm + ownership cross-ref | ADR-097 / ADR-098 | paradigm scope boundary + UpgradeAgent runtime ownership (PMO 흡수) |

**범위 (in scope)**: walker walk_result + 4-field 보고 schema / changelog SSOT location + aggregate view / consumer fallback grace period 정책 / sunset metric source 표준 / min_prerequisite_version manifest schema + topological resolve / paradigm scope boundary + UpgradeAgent ownership cross-ref.

**범위 외 (out of scope)**: UpgradeAgent runtime mandate body 실 구현 (changelog walk 알고리즘 / plan 생성 / apply transaction — Wave 2 Story-4 CFP-703 영역 + ADR-098 §결정 1 ownership boundary codify only) / consumer fallback degraded mode per-behavior enumeration (ADR-094 §결과 후속 carrier) / sunset metric 실 cron dashboard json + 집계 script (ADR-095 §결정 2 후속 carrier) / min_prerequisite_version mismatch lint mechanical wire (ADR-096 §결정 3 후속 sub-CFP Phase 2 carrier).

## §2 walk_result schema (ADR-093 codify)

walker 완료 보고 = **walk_result enum + 4-field**. closed_enum `open_extension: false` 강제 — consumer overlay 가 보고 field 또는 walk_result enum 값을 임의 확장할 수 없다 (ADR-093 §결정 1 K-5 결정 verbatim).

> verified-via: Read docs/adr/ADR-093-completion-report-4field-schema.md (§결정 1 — "walk_result enum (closed-set, 4-value): SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED" + 2-layer 4-field 표 + §결정 2 closed_enum invariant "open_extension: false (closed-set)" verbatim)

### §2.1 walk_result enum (4-value closed_enum)

```yaml
walk_result:
  enum: [SUCCESS, SUCCESS_WITH_DEGRADATION, PARTIAL_FAILURE, FAILED]
  open_extension: false   # closed-set — 5번째 enum 값 신설 = ADR-093 amendment (강화 방향) 로만
  semantic_source: "reconcile-protocol-v1 §4.13 result_fidelity_binding (Deprecated, semantic lossless 답습 — paradigm shift carrier-preserved, ADR-097 §결정 3)"
  exit_code_mapping: deterministic   # exit code → walk_result enum deterministic mapping 의무 (silent false SUCCESS 차단 — ADR-093 §결정 1 verbatim: "result field 미기록 / SUCCESS hardcode = forbidden")
```

- **SUCCESS** — walk 정상 완료, degradation 0.
- **SUCCESS_WITH_DEGRADATION** — walk 완료하나 일부 degraded (예: consumer min_prerequisite_version 미달 grace window 안 degraded mode — §4).
- **PARTIAL_FAILURE** — 일부 영역 실패 (부분 산출물 forbidden — exit code 비-0 일부).
- **FAILED** — walk 실패.

exit code → walk_result enum deterministic mapping 의무. result field 미기록 / `SUCCESS` hardcode 는 forbidden (silent false SUCCESS 차단).

### §2.2 4-field 2-layer 분리 schema

두 4-field schema 는 같은 "4-field 완료 보고" 이름을 공유하나 layer 가 disjoint 하다 (ADR-093 §결정 1 2-layer 분리):

| layer | 4-field | facing | 역할 |
|---|---|---|---|
| **외부 보고 layer (사용자 4-field) = walk completion report** | `from_version` / `to_version` / `target_version_release_date` / `key_changes_summary` | human-facing | 사용자 발화 verbatim — walk 종료 시 사용자가 받는 완료 보고 본문 (어느 버전 → 어느 버전, target 버전 release 일자, 핵심 변경 요약) |
| **내부 schema layer (PMO 4-field) = walk_result detail** | `touched_files` / `atomic_invariants` / `verify_via` / `lane_outcomes` | machine / audit-facing | PMO 2nd pass — walk 과정 내부 audit detail (touched 파일 / atomic invariant 검증 / verify-via 경로 / lane 별 outcome) |

양 layer 는 동일 walk 의 다른 surface 다. 외부 보고 (사용자 4-field) 는 walk_result enum 과 함께 사용자에게 발화되고, 내부 schema (PMO 4-field) 는 walk_result 의 detail 로서 audit / 집계 surface 에 기록된다.

### §2.3 closed_enum invariant (unconditional)

walk_result enum + 양 4-field (사용자 4-field + PMO 4-field) 모두 `open_extension: false`. consumer overlay field 추가 불가 invariant 는 **무조건 (unconditional)** — ADR-068 I-3 unconditional vs conditional guard placement intent 정합 ("충돌 시 unconditional 우선, broad coverage"). field 확장 차단은 특정 path 한정 conditional guard 가 아니라 양 layer 전 보고 경로에 무조건 적용. schema 확장 (enum 값 / field 추가) 은 ADR-093 amendment (ADR-058 §결정 5 sunset_justification 의무, ratchet 강화 방향만) 로만 codify — runtime ad-hoc 확장 금지.

## §3 changelog SSOT (ADR-092 codify)

walker 의 입력 source = **per-plugin self-owned `CHANGELOG.md`** (ADR-092 §결정 1 K-4 결정). aggregate view 는 walker 7-plugin 합집합 derived (런타임, SSOT 아님).

> verified-via: Read docs/adr/ADR-092-changelog-ssot-location.md (§결정 1 K-4 결정 표 — "wrapper plugin: CHANGELOG.md self-owned / SSOT" + "consumer overlay: 미보유 / N/A (walker 입력으로만 참여)" + "aggregate view (7 합집합): 런타임 walker 산출 / derived view (SSOT 아님)" verbatim)

| 대상 | changelog 보유 | SSOT 여부 | walker 역할 |
|---|---|---|---|
| wrapper plugin | `CHANGELOG.md` self-owned | **SSOT** | walk source (7 source 중 1) |
| 6 lane plugin 각각 | `CHANGELOG.md` self-owned | **SSOT** | walk source (해당 lane self-write) |
| consumer overlay | 미보유 | N/A | walker 입력 (설치 plugin version 집합) |
| aggregate view (7 합집합) | 런타임 walker 산출 | derived view (SSOT 아님) | walker 합집합 (union) 매 호출 재생성, drift 발생 불가 |

- **per-plugin self-owned**: wrapper + 6 lane plugin 각자 own `CHANGELOG.md`. 각 plugin self-write boundary 안에서만 갱신 (cross-plugin write 0건). plugin version bump (ADR-016 mirrored field `version`) 와 같은 PR 안에서 해당 plugin `CHANGELOG.md` entry append.
- **consumer overlay = changelog 미보유**: consumer 는 walker 입력 (설치 plugin version 집합) 으로만 참여, 별 changelog SSOT 신설 0.
- **aggregate view = walker derived**: "통합 변경 내역" 단일 진입점은 walker 가 7 plugin `CHANGELOG.md` 를 합집합 (union) 으로 조립해 제공 — derived view 이지 SSOT 아님. 매 호출 재생성 (영속 file 부재), drift 발생 불가.

**drift detection = warning tier** (ADR-092 §결정 2, ADR-060 evidence-enforceable framework `warning` tier). 각 plugin `CHANGELOG.md` 마지막 entry version ↔ 해당 plugin `.claude-plugin/plugin.json` `.version` field 정합 (equality). mismatch = drift 신호. PR gate block 미발동 (PR-gate layer disjoint — ADR-026 보존). mechanical wire = 별 sub-CFP carrier (pattern_count >= 2 재발 시 follow-up CFP MUST promote). ADR-016 mirrored field versioning + ADR-063 marketplace ↔ plugin.json atomic invariant 와 disjoint axis (atomic coordination 의무 + 사후 drift detection 보완).

## §4 Fallback 정책 (ADR-094 codify)

consumer 가 `min_prerequisite_version` (§6 / ADR-096) 미만 버전을 유지할 때 walker fallback 정책 = **hybrid grace period** (ADR-094 §결정 1 mode (c) 채택). closed-set 3 mode enum:

> verified-via: Read docs/adr/ADR-094-consumer-legacy-version-fallback-policy.md (§결정 1 mode 표 — "(c) hybrid grace period ... 채택 — K8s deprecation policy matrix 정합" + §결정 2 grace window 표 "GA-equivalent (stable feature) 12개월 / Beta-equivalent 9개월 — K8s deprecation policy verbatim" verbatim)

```yaml
fallback_mode:
  enum: [silent_degraded, hard_fail, hybrid_grace_period]   # (a)/(b)/(c)
  open_extension: false   # closed-set — 4번째 mode 신설 = ADR-094 amendment (강화 방향) 로만
  adopted: hybrid_grace_period   # (c) 채택
grace_window:
  ga_equivalent_months: 12   # K8s deprecation policy — GA(stable) API grace 최소 12개월 verbatim
  beta_equivalent_months: 9  # K8s deprecation policy — Beta API grace 최소 9개월 verbatim
  canary_tier: not_applicable   # canary = grace window 적용 외 (HIGH risk class, ADR-076 §결정 9 production-impact)
  window_start: first_detected_at   # floor 미만 최초 감지 시점 (degraded warning 첫 발화 timestamp, ADR-079 KST +09:00 zoned)
```

- **(c) hybrid grace period 채택** — floor 미만 감지 시 grace window (GA 12mo / Beta 9mo) 안 degraded mode 작동 + **warning 보고 의무** (silent 금지), window 종료 후 hard fail.
  - **(a) silent degraded 거부** — silent harm (consumer 가 degraded 인지 못함, mctrader-data#81 silent partial 결함 class 동형).
  - **(b) hard fail 거부** — grace 없는 productivity cliff.
- **grace window 안**: degraded mode 작동 (floor 미만 보장 불가 신규 behavior 만 비활성, 나머지 정상 유지) + 매 작동 시 warning 보고 의무 (degraded 상태 + 잔여 grace 기간 + 권장 upgrade target 명시). 보고 schema = §2 walk_result `SUCCESS_WITH_DEGRADATION` + 외부 보고 4-field cross-ref.
- **grace window 종료 후**: hard fail — floor 미만 consumer 에서 walker 작동 거부. grace window 가 hard fail 의 사전 통지 + 유예 layer (cliff 완화).
- **feature class 판정**: walker behavior 가 의존하는 channel tier (ADR-076 §결정 9 stable / beta / canary) 정합. stable = GA-equivalent (12mo), beta = Beta-equivalent (9mo), canary = grace window 적용 외 (즉시 degraded warning).
- **fallback trigger source**: floor 미만 판정 비교 기준 = consumer 측 설치 버전 (plugin install `.version` / `codeforge.version_pin`) ↔ wrapper manifest `min_prerequisite_version` (§6 / ADR-096 SSOT). trigger source field 정의 = §6 SSOT (본 §4 = trigger 발동 후 walker behavior 정책만, field 정의 미중복).

**ADR-095 baseline align**: grace window 정량 (12mo / 9mo) 은 §5 sunset metric baseline 과 동일 K8s deprecation policy 기준점 공유 (cross-cutting baseline 일관성).

## §5 sunset metric (ADR-095 codify)

sunset metric source = **changelog mining (§3 / ADR-092 cross-ref) + cron 자동 측정** (ADR-095 §결정 1 K-7 결정). closed-set 2-source (AND / OR composable):

> verified-via: Read docs/adr/ADR-095-sunset-metric-standardization.md (§결정 1 metric source 표 — "changelog mining ... ADR-092 (changelog SSOT location) — metric mining source SSOT" + "cron 자동 측정 ... ADR-057 rate-limit-fallback.json precedent 답습" + baseline "GA (stable) 12개월 / Beta 9개월" verbatim)

```yaml
sunset_metric:
  source:
    enum: [changelog_mining, cron_auto_measure]   # closed-set 2-source (AND/OR composable)
    open_extension: false   # 자유 산문 metric source (예: "충분히 안정화되면") 배제 — ADR-058 §결정 3 모달 어휘 금지 정합
  baseline:
    ga_months: 12   # K8s deprecation policy GA threshold
    beta_months: 9  # K8s deprecation policy Beta threshold
  combination: "시간 threshold (baseline) AND metric threshold (rate/count/flag)"
  carrier_preserved: true   # bulk sunset 시 효용 carry lossless reproduce 측정 신호 포함 (ADR-097 §결정 3)
```

- **metric source = changelog mining + cron** — sunset 진척을 codeforge family changelog (§3 SSOT) 에서 mechanical 추출 (도입 사유 해소 신호를 changelog entry pattern 으로 mining) + monthly cron 측정해 dashboard json 갱신 (ADR-057 `rate-limit-fallback.json` precedent 답습). 자유 산문 metric source 배제 (ADR-058 §결정 3 모달 어휘 금지 정합).
- **baseline (K8s deprecation policy 차용)** — sunset 시간 threshold = GA 12mo / Beta 9mo. `is_transitional: true` ADR 의 도입 사유 해소 후, GA-tier anchor 12mo / Beta-tier anchor 9mo grace 후 sunset 발동. baseline = 시간 차원 정량 anchor, 각 ADR 의 구체 metric (rate / count / flag) 과 AND 결합.
- **carrier-preserved sunset (ADR-095 §결정 3 / ADR-097 §결정 3)** — bulk sunset (9 ADR 동시 sunset) = carrier-preserved sunset. metric 이 "도입 사유 해소"뿐 아니라 "효용 carry lossless reproduce" 를 측정 신호로 포함 (β audit LOSSLESS evidence). lossless 미달 (효용 carry 누락) ADR 은 bulk sunset 비대상 (naive sunset 차단, ADR-058 §결정 5 무조건 적용).
- **dashboard schema (declaration-only Wave 1)** — 9 ADR sunset metric 단일 집계 dashboard (`docs/kpi/sunset-metric.json` 등) row = (a) adr_number / (b) sunset_carrier_cfp / (c) metric source / (d) baseline threshold / (e) measured value / (f) gate_status (pending / met / sunset_ready). 실 cron 자동 측정 인프라 = 후속 carrier (ADR-095 §결정 2).

## §6 min_prerequisite_version manifest (ADR-096 codify)

cross-tier (lane plugin → wrapper) 의존 표현 manifest schema = **dual carrier** (consumer `.claude/_overlay/project.yaml` version_pin + plugin `plugin.json` min_prerequisite_version). semver range + topological resolve (7 plugin DAG). mismatch = §4 Fallback trigger (ADR-096 §결정 1 K-8 dual carrier + §결정 2 topological resolve + §결정 3 mismatch lint).

> verified-via: Read docs/adr/ADR-096-min-prerequisite-version-manifest-schema.md (§결정 1 K-8 dual carrier 표 — "plugin 측 (publisher 선언) ... min_prerequisite_version: { codeforge: ">=6.0.0" }" + "consumer 측 (current-state pin) ... codeforge.version_pin.version" + §결정 2 "topological order = [wrapper, ...6 lane]" + §결정 3 "warning tier ... ADR-094 Fallback 안내" verbatim)

```yaml
min_prerequisite_version:
  carrier:
    enum: [plugin_publisher_plugin_json, consumer_project_yaml_version_pin]   # closed-set 2-carrier (dual)
    open_extension: false   # carrier 확장 = ADR-096 amendment (강화 방향) 로만
  range_semantics: npm_engines   # >=6.0.0, >=6.0.0 <7.0.0 등 standard semver range
  resolve: topological   # 7 plugin DAG — topological order [wrapper, ...6 lane] (Cargo MSRV + npm engines 정합)
  dag_invariant: "lane → wrapper 단방향 cross-tier 의존, cycle 부재 (DAG)"
  wrapper_self: empty_or_omit   # wrapper = top of dependency tree, min_prerequisite_version 빈 map 또는 생략
  mismatch_action: fallback_trigger   # §4 Fallback (ADR-094 hybrid grace) trigger
  mismatch_lint_tier: warning   # ADR-060 4-tier `warning` (Wave 1 declaration-only, blocking 승격 = ADR-060 승격 gate 후)
```

- **dual carrier (K-8)** — publisher 선언 (`plugin.json` `min_prerequisite_version: { codeforge: <range> }`, "이 lane plugin 이 동작하려면 wrapper 최소 버전") + consumer 고정값 (`project.yaml` `codeforge.version_pin.version`, 실 install 버전). 두 carrier 교집합 비교 (publisher 요구 range ↔ consumer 고정 실값) 가 mismatch detection 입력. 단일 carrier 는 cross-tier 의존 양 끝 표현 불가.
- **semver range + topological resolve** — range 표현 = npm `engines` semantics. 7 plugin (wrapper + 6 lane) 의존 그래프 = topological sort. lane → wrapper 단방향 (6 lane 각각이 wrapper prerequisite, wrapper = root 의존 없음). topological order = `[wrapper, ...6 lane]` — wrapper 먼저 resolve → 각 lane `min_prerequisite_version` 이 확정 wrapper 버전 검증. cross-tier 단방향 = cycle 부재 (DAG invariant). Cargo MSRV resolver + npm engines walk ordering 정합.
- **mismatch = §4 Fallback trigger** — topological walk 중 어느 lane plugin 의 range 를 consumer wrapper version_pin 실값이 미만으로 충족 못하면 (`consumer_pin < plugin_min_prerequisite`) → §4 ADR-094 Fallback (hybrid grace) trigger. resolve 는 detection 만, 처리 (degraded mode / grace / 호환 범위) 는 §4 / ADR-094 SSOT 위임 (detection 본 §6 ↔ 처리 §4 disjoint binding).
- **mismatch lint = warning tier** — ADR-060 `warning` tier. Wave 1 declaration-only (mechanical wire = 후속 sub-CFP Phase 2 carrier). false-block risk (구형 consumer 정상 운영 차단) 회피 — warning 으로 가시화 + §4 Fallback 경로 안내가 1차 적정 강도. pattern_count >= 2 mismatch 재발 시 follow-up CFP MUST promote.

## §7 paradigm + ownership cross-ref (ADR-097 / ADR-098 codify)

### §7.1 paradigm replacement scope boundary (ADR-097 codify)

본 contract 가 carry 하는 imperative changelog walk paradigm 으로의 전환은 ADR-097 §결정 1 **paradigm replacement scope boundary** (closed-set 3 조건 AND) 자격 영역이다.

> verified-via: Read docs/adr/ADR-097-paradigm-replacement-governance-anchor.md (§결정 1 scope boundary 표 — "(a) 9+ ADR/contract 동시 sunset 동반 / (b) 단일 atomic Epic / (c) ratchet 강화 방향 (carve-out, 약화 아님)" 3 조건 AND + §결정 3 carrier-preserved sunset 표 verbatim)

```yaml
paradigm_replacement_scope_boundary:
  conditions:   # closed-set 3 조건 AND (1+ 부재 = 일반 amendment 영역, ADR-064 §결정 5 unitary 적용)
    - { id: a, name: "9+ ADR/contract 동시 sunset 동반", verify: "sunset 대상 enumeration + 각 효용 carry 경로 명시" }
    - { id: b, name: "단일 atomic Epic", verify: "Epic Issue + N sub-Story sibling carrier + atomic merge order" }
    - { id: c, name: "ratchet 강화 방향 (carve-out, 약화 아님)", verify: "β audit lossless 9/9 + ratchet direction declare" }
  open_extension: false   # 면제 trigger 확장 = ADR-097 amendment (강화 방향) 로만
  cfp_scope_unitary_exemption: "ADR-064 §결정 5 면제 channel (Amendment 7) — 단일 atomic Epic 안 9+ ADR/contract 동시 sunset + 신규 anchor 묶음 atomic 도입 허용"
  carrier_preserved_sunset: "bulk sunset = 효용 lossless carry (carrier shift) = 강화 방향, naive sunset (효용 소멸) = 차단 (ADR-058 §결정 5)"
```

- **scope boundary 3 조건 AND** — (a) 9+ ADR/contract 동시 sunset + (b) 단일 atomic Epic + (c) ratchet 강화 방향 (carve-out). 3 조건 모두 충족 시에만 paradigm replacement = ADR-064 §결정 5 CFP scope unitary 면제 자격. 1+ 조건 부재 = 일반 amendment 영역 (별개 CFP 분리 의무).
- **carrier-preserved sunset (ADR-097 §결정 3)** — 9 ADR/contract bulk sunset 이 ratchet 약화가 아닌 조건 = 효용이 대체 paradigm (imperative walker) 안으로 lossless carry. 효용 carrier 가 paradigm replace 후 reproduce 되면 sunset = "효용 소멸"이 아니라 "효용 이전 (carrier shift)" = 강화 방향. reconcile-protocol-v1 §4.13 walk_result enum semantic 의 본 contract §2 lossless carry 가 그 instantiation (β audit LOSSLESS evidence).

### §7.2 UpgradeAgent runtime ownership (ADR-098 codify)

walker runtime 의 ownership = **codeforge-pmo lane 흡수** (ADR-098 §결정 1 K-3 결정). cross-cutting agent semantic 확장 — UpgradeAgent = PMOAgent sibling.

> verified-via: Read docs/adr/ADR-098-upgrade-agent-runtime-ownership.md (§결정 1 ownership enum 표 — "(a) codeforge-pmo 흡수 ... 채택 [권장]" + "(b) 신규 codeforge-upgrade lane plugin ... 거부 / defer — 8-plugin family blast radius" + §결정 3 "runtime SSOT = ADR-076 ... reconcile-protocol-v1 = Deprecated ... 1st-class SSOT citation 금지" verbatim)

```yaml
upgrade_agent_ownership:
  enum: [codeforge_pmo_absorb, new_codeforge_upgrade_lane_plugin]   # closed-set 2-value
  open_extension: false   # ownership 후보 확장 = ADR-098 amendment (강화 방향) 로만
  adopted: codeforge_pmo_absorb   # (a) 채택 — cross-cutting agent (PMOAgent sibling), single-repo scope 유지 (신규 plugin 도입 0)
  rejected: new_codeforge_upgrade_lane_plugin   # (b) 거부 — 8-plugin family blast radius (ADR-023 lifecycle)
  model_tier_reassessment: required   # ADR-042 §결정 2/§결정 3 — 실 tier 확정 = Wave 2 Story-3 CFP-703 (declare only)
  runtime_ssot: ADR-076   # declarative reconciliation upgrade flow (paradigm replace 진행 중)
  reconcile_protocol_v1_citation: forbidden_1st_class   # v1.13 Deprecated — 1st-class SSOT citation 금지
```

- **ownership = codeforge-pmo 흡수 (a 채택)** — upgrade transaction = lane-agnostic family-wide 작업 → cross-cutting lane (codeforge-pmo) 자연스러운 귀속 (PMOAgent + GitOpsAgent + DialogFidelityAgent sibling). single-repo scope 유지 (신규 plugin 도입 0, 8-plugin family blast radius 0). (b) 신규 codeforge-upgrade lane plugin = 거부 (ADR-023 lifecycle blast radius 과잉).
- **ownership boundary codify only** — UpgradeAgent 실 runtime mandate body (changelog walk 절차 / plan / apply transaction / 3 mode) = Wave 2 Story-3 (CFP-703) 영역 (ADR-098 scope 외). model tier 재평가 의무 = declare only (실 tier 확정 = CFP-703, ADR-042 amendment carry).
- **runtime SSOT = ADR-076** (paradigm replace 진행 중) — reconcile-protocol-v1 (v1.13 Deprecated) 1st-class SSOT citation 금지. walker 가 어느 paradigm (declarative 잔존 vs imperative 전환) 이든 UpgradeAgent = codeforge-pmo 귀속 (paradigm-agnostic ownership anchor).

## §8 version_history

| version | date | cfp | change |
|---|---|---|---|
| 1.0 | 2026-05-21 | CFP-1145 | initial — imperative changelog walk paradigm 의 walker protocol schema SSOT 신설. reconcile-protocol-v1 (v1.13 Deprecated, CFP-1125) 후속 carrier. 7 ADR (ADR-092~098) 결정 codify (§2 walk_result + 4-field 보고 schema / §3 changelog SSOT + aggregate view + drift detection / §4 hybrid grace fallback / §5 sunset metric source / §6 min_prerequisite_version manifest + topological resolve / §7 paradigm scope boundary + UpgradeAgent ownership). kind:registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합). closed_enum open_extension:false invariant 보존 (ADR-064 §self-application ratchet 강화 방향만). |
