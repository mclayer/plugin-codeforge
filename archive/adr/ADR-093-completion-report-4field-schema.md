---
adr_number: 93
title: Completion report 4-field schema — walker walk_result + 4-field 완료 보고 schema (외부 보고 / 내부 schema 2-layer 분리) closed_enum SSOT
status: Accepted
category: tooling-infrastructure
date: 2026-05-21
carrier_story: CFP-1136 (CFP-1111-W1-S2)
parent_epic: CFP-1111
related_stories:
  - CFP-1136     # 본 carrier (CFP-1111 Wave 1 Story-2, ADR-093 sub-Story)
  - CFP-1111     # umbrella Epic
related_adrs:
  - ADR-097      # paradigm replacement governance anchor — declarative → imperative walk paradigm shift 의 governance anchor (본 schema = 그 paradigm 의 완료 보고 surface)
  - ADR-076      # declarative reconciliation upgrade — walk_result 4-value enum 의 semantic 원천 (reconcile-protocol-v1 §4.13 Deprecated, semantic 답습)
  - ADR-094      # consumer legacy version fallback policy — 구형 consumer 보고 schema 호환 sister (W1-S2 sibling)
  - ADR-068      # boundary completeness invariants — I-3 unconditional guard placement intent 정합 (closed_enum open_extension:false unconditional)
related_files:
  - docs/adr/ADR-094-consumer-legacy-version-fallback-policy.md  # sister — 구형 consumer 보고 schema 호환 (cross-ref)
  - docs/adr/ADR-097-paradigm-replacement-governance-anchor.md   # paradigm replacement governance anchor (cross-ref)
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md       # walk_result 4-value enum semantic 원천 (cross-ref)
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md         # §4.13 result_fidelity_binding (Deprecated, semantic 답습 source)
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-097 §결정 0 / ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (behavioral directive only, walker 완료 보고 schema mechanical lint = Wave 1 declaration 후 pattern_count >= 2 재발 시 follow-up CFP MUST promote)
is_transitional: false  # permanent policy — 4-field 완료 보고 schema 는 walker paradigm 의 영구 완료 보고 surface. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-093 — Completion report 4-field schema

## 상태

`Accepted` (2026-05-21 KST) — CFP-1136 carrier (CFP-1111 Wave 1 Story-2, ADR-093 sub-Story). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 CFP-899 precedent 정합 — chief author scope). ADR-097 (paradigm replacement governance anchor) 의 7-bundle (CFP-1111 Wave 1 Story-2, ADR-092~098) 중 2/7 sibling carrier.

## 컨텍스트

### 동인

ADR-097 (paradigm replacement governance anchor) 이 codify 하는 declarative → imperative changelog walk paradigm 전환 영역에서, upgrade walker 의 **완료 보고 (completion report)** 가 표준 schema 없이 ad-hoc 자유 형식으로 산출되면 (a) 사용자가 매 walk 마다 다른 형식의 보고를 받고, (b) consumer overlay 가 임의 field 를 덧붙여 보고 surface 가 drift 하며, (c) 자동 집계/검증 layer (drift detection / cron metric) 가 보고를 parse 할 수 없다.

기존 declarative reconciliation paradigm 에서는 `reconcile-protocol-v1` §4.13 `result_fidelity_binding` 이 walk_result 4-value enum (`SUCCESS` / `SUCCESS_WITH_DEGRADATION` / `PARTIAL_FAILURE` / `FAILED`) 을 carry 했다. 그러나 reconcile-protocol-v1 은 CFP-1111 (imperative changelog walk paradigm 도입) carrier 로 status `Active → Deprecated` 전환 (§4.13/§4.14/§4.8 binding sunset 동반) — paradigm shift 후 walk_result enum 의 semantic 은 lossless carry 되어야 하나, 그 carrier 가 부재했다.

본 ADR 은 walker 완료 보고 = **walk_result enum + 4-field schema** 를 normative SSOT 로 codify 한다. 핵심 결정 (K-5) = 보고 schema 의 closed_enum `open_extension: false` 강제 — consumer overlay 가 보고 field 를 임의 확장할 수 없게 박는다.

> verified-via: Read docs/inter-plugin-contracts/reconcile-protocol-v1.md (L955-990 §4.13 result_fidelity_binding — walk_result 4-value enum `SUCCESS`/`SUCCESS_WITH_DEGRADATION`/`PARTIAL_FAILURE`/`FAILED` + `closed_set_invariant` "result field 미기록 / SUCCESS hardcode = forbidden — exit code → result enum deterministic mapping 의무" verbatim; L46 frontmatter amendment_log "status Active → Deprecated. CFP-1111 carrier")
> verified-via: Read docs/adr/ADR-097-paradigm-replacement-governance-anchor.md (§결정 0 3 carry-over — closed_enum open_extension:false / ADR-026 Amendment 5 PR-gate layer / ADR-067 disjoint invariant 보존 패턴 답습 source)
> verified-via: Read docs/adr/ADR-068-boundary-completeness-invariants.md (L114-116 + L322 I-3 unconditional vs conditional guard placement intent — "충돌 시 unconditional 우선 (broad coverage, ADR-064 정합)" verbatim)

### 2-layer 보고 schema 의 표면 충돌

본 ADR 작성 시점에 두 4-field schema 가 표면적으로 경합한다:

1. **사용자 발화 verbatim 4-field** (외부 보고): `from_version` / `to_version` / `target_version_release_date` / `key_changes_summary` — 사용자가 walk 종료 시 받기 원하는 완료 보고 본문. "어느 버전에서 어느 버전으로, 그 버전 release 일자, 핵심 변경 요약" — human-facing.
2. **PMO 2nd pass 4-field** (내부 schema): `touched_files` / `atomic_invariants` / `verify_via` / `lane_outcomes` — walk 과정의 내부 audit detail. machine/audit-facing.

두 4-field 는 같은 "4-field 완료 보고 schema" 이름을 공유하나 layer 가 disjoint 하다. 본 ADR §결정 1 이 이 경합을 **2-layer 분리** 로 해소한다 — 사용자 4-field = walk completion report (외부 보고), PMO 4-field = walk_result detail (내부 schema). 양 layer 는 동일 walk 의 다른 surface 이며 충돌 아님.

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (ADR-097 §결정 0 패턴 답습 — 본 schema 가 인접 governance layer 를 약화하지 않음을 박아두는 anchor):

1. **closed_enum open_extension:false 보존 (본 ADR 핵심)** — walk_result enum + 양 4-field 모두 closed-set. consumer overlay 가 보고 field 또는 walk_result enum 값을 임의 확장할 수 없다 (§결정 2). schema 확장은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — walker 완료 보고 schema 는 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 와 disjoint. 완료 보고는 walk runtime 의 출력 surface 이지 PR gate 의 일부가 아니다 — 보고 schema 도입이 PR-gate layer 를 변경하지 않는다.
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ walk completion report layer 는 disjoint. walker 의 walk_result `FAILED` 보고가 ADR-067 RESET 룰 카운터를 변경하지 않는다 (ADR-076 §ADR-067 disjoint layer cross-ref 답습 — upgrade transaction layer ≠ Story progression layer).

### §결정 1 — 4-field 완료 보고 schema (2-layer 분리)

walker 완료 보고 = **walk_result + 4-field**. K-5 결정 = closed_enum `open_extension: false` 강제 (§결정 0 carry-over #1 — 본 ADR 핵심).

**walk_result enum** (closed-set, 4-value): `SUCCESS` / `SUCCESS_WITH_DEGRADATION` / `PARTIAL_FAILURE` / `FAILED`. reconcile-protocol-v1 §4.13 result_fidelity_binding 정합 (Deprecated 이나 semantic 답습 — paradigm shift lossless carry, ADR-097 §결정 3 carrier-preserved sunset 정합). exit code → walk_result enum deterministic mapping 의무 (silent false `SUCCESS` 차단 — reconcile-protocol-v1 §4.13 `closed_set_invariant` verbatim 답습: "result field 미기록 / SUCCESS hardcode = forbidden").

**4-field 2-layer 분리** — 두 4-field schema 가 같은 이름을 공유하나 layer disjoint:

| layer | 4-field | facing | 역할 |
|---|---|---|---|
| **사용자 4-field = walk completion report (외부 보고)** | `from_version` / `to_version` / `target_version_release_date` / `key_changes_summary` | human-facing | 사용자 발화 verbatim — walk 종료 시 사용자가 받는 완료 보고 본문 (어느 버전 → 어느 버전, target 버전 release 일자, 핵심 변경 요약) |
| **PMO 4-field = walk_result detail (내부 schema)** | `touched_files` / `atomic_invariants` / `verify_via` / `lane_outcomes` | machine / audit-facing | PMO 2nd pass — walk 과정 내부 audit detail (touched 파일 / atomic invariant 검증 / verify-via 경로 / lane 개별 outcome) |

양 layer 는 동일 walk 의 다른 surface 다. 외부 보고 (사용자 4-field) 는 walk_result enum 과 함께 사용자에게 발화되고, 내부 schema (PMO 4-field) 는 walk_result 의 detail 로서 audit/집계 surface 에 기록된다. 두 layer 모두 §결정 2 closed_enum invariant 적용.

### §결정 2 — closed_enum invariant

walk_result enum + 양 4-field (사용자 4-field + PMO 4-field) 모두 `open_extension: false` (closed-set).

- **walk_result enum**: 4-value closed-set (`SUCCESS` / `SUCCESS_WITH_DEGRADATION` / `PARTIAL_FAILURE` / `FAILED`). 5번째 enum 값 신설 = 본 ADR amendment (강화 방향) 로만 가능 — runtime/consumer 임의 추가 금지.
- **사용자 4-field**: 4-field closed-set. consumer overlay 가 외부 보고 field 추가 불가.
- **PMO 4-field**: 4-field closed-set. consumer overlay 가 내부 schema field 추가 불가.

consumer overlay field 추가 불가 invariant 는 **무조건 (unconditional)** — ADR-068 I-3 unconditional vs conditional guard placement intent 정합 ("충돌 시 unconditional 우선, broad coverage" verbatim). field 확장 차단은 특정 path 한정 conditional guard 가 아니라 양 layer 전 보고 경로에 무조건 적용된다. consumer overlay 는 정책을 확장만 할 수 있고 축소할 수 없다는 wrapper 원칙 (CLAUDE.md "Orchestrator 정책 적용 범위") 의 schema 영역 instantiation — 단, 보고 schema 는 확장 자체도 불가 (closed_enum) 하여 보고 surface drift 를 원천 차단.

schema 확장 (enum 값 / field 추가) 은 본 ADR amendment (ADR-058 §결정 5 sunset_justification 의무, ratchet 강화 방향만) 로만 codify — runtime ad-hoc 확장 금지.

## 결과

### 긍정

- walker 완료 보고의 표준 surface 획득 — 매 walk 마다 일관된 보고 형식 (walk_result enum + 4-field) 으로 사용자 / audit layer 양쪽 정합.
- 2-layer 분리로 human-facing 보고 (사용자 4-field) ↔ machine/audit detail (PMO 4-field) 의 역할 disjoint 명시 — 같은 이름 4-field 의 layer 혼동 차단.
- closed_enum open_extension:false 로 보고 surface drift 원천 차단 — consumer overlay field/enum 임의 확장 불가.
- reconcile-protocol-v1 §4.13 walk_result enum semantic 의 lossless carrier — paradigm shift (declarative → imperative) 후에도 보고 enum 효용 보존 (ADR-097 §결정 3 carrier-preserved sunset 정합).

### 부정 / trade-off

- closed_enum 으로 인해 consumer 가 보고에 자기 field 를 덧붙이고 싶어도 불가 — schema 경직성. 완화 = 확장 필요 시 본 ADR amendment (ratchet 강화) 경로로 정식 codify (보고 surface 일관성 우선 trade-off 정당).
- walk_result enum + 양 4-field schema 의 mechanical lint Wave 1 부재 (`mechanical_enforcement_actions: []`) — schema 준수가 manual (behavioral directive). pattern_count >= 2 재발 (보고 field drift / enum hardcode) 시 follow-up CFP MUST promote to mechanical lint (ADR-082 §결정 6 retain rationale 답습).
- 2-layer 의 양 4-field 가 같은 "4-field" 이름을 공유 — reader 가 혼동할 risk. 완화 = §결정 1 표가 layer / facing / 역할 disjoint 명시 (외부 보고 vs 내부 schema label 박제).

## 해소 기준

N/A — permanent policy (4-field schema). walker 완료 보고 schema (walk_result enum + 2-layer 4-field) 는 영구 정책 (is_transitional: false). 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: walk_result enum 값 추가 / 4-field field 추가 / closed_enum invariant mechanical 승격 / lint 도입). 약화 방향 (예: closed_enum open_extension true 다운그레이드 / 4-field 축소 / consumer overlay field 확장 허용) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = tooling-infrastructure, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `docs/adr/ADR-094-consumer-legacy-version-fallback-policy.md` — sister within W1-S2 (구형 consumer 보고 schema 호환, cross-ref)
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — paradigm replacement governance anchor (본 schema = 그 paradigm 의 완료 보고 surface, cross-ref)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — walk_result 4-value enum semantic 원천 (cross-ref)
- `docs/adr/ADR-068-boundary-completeness-invariants.md` — I-3 unconditional guard placement intent 정합 (cross-ref)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` — §4.13 result_fidelity_binding (Deprecated, walk_result enum semantic 답습 source)
