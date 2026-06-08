---
adr_number: 112
title: Living Architecture per-Epic mandatory update gate — ArchitectAgent Epic close 직전 5-anchor section update 의무 + no-op explicit declare
status: Accepted
category: governance
date: 2026-05-24
carrier_story: CFP-1426
parent_epic: CFP-1415
related_adrs:
  - ADR-078  # Living Architecture SSOT origin — `docs/architecture/<plugin>.md` per-plugin self-owned 누적 현재 상태 SSOT (4 영역 closed-enum: 모듈 / 경계 / 인터페이스 계약 / 데이터 흐름). 본 ADR = ADR-078 의 update gate forcing function (write timing + verify field). Sibling Story #1425 (S3.1) = ADR-078 Amendment 2 (5-anchor section closed-set codify, base for §결정 2)
  - ADR-111  # Confluence-mirror classification policy SSOT (CFP-1419) — §결정 1 closed-enum 4 mirror 대상 중 2번째 = Living Architecture. 본 ADR §결정 1 per-Epic update gate 가 발효될 때마다 ADR-111 §결정 5 cross-link discipline (Confluence anchor link presence) 가 동시 발효 — Living Architecture 변경 시 Confluence mirror 동기 SLA 정합
  - ADR-091  # ArchitectLane DDD vocabulary governance — 5-anchor section 중 "Open Decisions Pending" anchor 2번째 entry 가 DDD vocabulary drift 추적 영역 (glossary SSOT cross-ref). 본 ADR §결정 2 5-anchor closed-set 의 5번째 anchor 가 ADR-091 §결정 6 enforcement 3-tier 의 design-time tier 와 align
  - ADR-068  # Boundary completeness invariants (I-1~I-6) + verdict-level boolean field pattern. 본 ADR §결정 3 review-verdict-v4 6번째 verdict-level optional bool field 신설 = ADR-068 Amendment 1 (I-5 dimensional_empirical_self_check_passed) / Amendment 3 (I-6 audit_gate_pointer_self_check_passed) pattern verbatim 답습. disjoint axis (boundary completeness ↔ living architecture update timing, 별 packet field)
  - ADR-065  # ArchitectAgent Phase 1 mechanical sync self-check (7-item) + verdict-level boolean field pattern. 본 ADR §결정 3 mechanical_self_check_passed (ADR-065 syntactic 7-item) + boundary_completeness_self_check_passed (ADR-068 I-1~I-4) + dimensional_empirical_self_check_passed (Amendment 1 I-5) + audit_gate_pointer_self_check_passed (Amendment 3 I-6) + deputy_axis_restructure_self_check_passed (Amendment 2) 5 기존 verdict-level boolean field 와 disjoint — 동일 verdict packet 6번째 별도 boolean field
  - ADR-064  # 결정 원칙 mandate — §결정 7 evidence-gated symmetric ratchet (강화 방향 evidence requirement: pattern_count / incident evidence). 본 ADR is_transitional: false 결정 = ratchet 강화 방향 (per-Epic mandatory update gate 신설 = governance 강도 확장), sunset_justification 면제 정합
  - ADR-058  # ADR sunset criteria mandate — §결정 5 sunset_justification 의무 (ratchet 차단). 본 ADR is_transitional: false 영역 (permanent governance ratchet), sunset_justification: null 정합
  - ADR-008  # Inter-plugin Contract Versioning (MAJOR/MINOR bump) — 본 ADR §결정 3 review-verdict-v4 v4.10 → v4.11 MINOR bump 정합 ("새 선택 필드 추가" + "enum literal 추가" MINOR bump 정합, additive only backward-compat invariant)
is_transitional: false
sunset_justification: null
mechanical_enforcement_actions:
  - living-architecture-update
amendment_log: []
---

# ADR-112 — Living Architecture per-Epic mandatory update gate

## 상태

Accepted (2026-05-24 KST) — ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. CFP-1426 carrier (Mega-Epic CFP-1415 Sub-C S3.2). Sibling Story #1425 (S3.1) = ADR-078 Amendment 2 (5-anchor section closed-set codify, base for §결정 2). Mechanical wire (`living-architecture-update`) = deferred-followup Wave 1 (S3.5 / CFP-1429 carrier).

## 컨텍스트

codeforge governance layer 의 Living Architecture SSOT ([ADR-078](ADR-078-living-architecture-doc.md)) = consumer plugin self-owned `docs/architecture/<plugin>.md` 누적 현재 상태 doc — 6 lane plugin self-owned seed (CFP-949 sub-Epic 완료). 그러나 ADR-078 본문은 **write timing 의무 (언제 update 해야 하는가)** 와 **verify field (verdict packet 안 boolean marker)** 를 명시 안함 → Epic close 시 Living Architecture page 가 stale 될 수 있음 (Change Plan 델타 + 코드 변경 merged 이후에도 Living Architecture 본문 미수정).

### Pattern_count evidence

evidence-gated ratchet 강화 정합 (ADR-064 §결정 7 + ADR-058 §결정 5):

1. **Living Architecture stale-after-Epic-close pattern** (≥ 2 incidents recent — Mega-Epic CFP-1415 audit trail) — Change Plan §3 affected_aggregates + §5 affected_modules 변경 merged 이후에도 `docs/architecture/<plugin>.md` 본문 미반영 사례.
2. **No-op silent skip 모호함 sub-pattern** — ArchitectAgent self-check "Living Architecture 영향 없음" 결정 시 명시적 declare 없이 silent skip → DesignReviewPL cross-validate 불가, retro corpus enumeration 시 "왜 update 안 했는가" 사후 reconstruct 불가능.
3. **Confluence-mirror sync SLA pattern** — ADR-111 §결정 1 closed-enum 4 mirror 대상 중 Living Architecture 가 2번째 entry. Living Architecture 변경 시 Confluence mirror 동기 SLA 발효 — write timing 의무 없으면 Confluence mirror 도 stale.

본 ADR 은 위 3 pattern 의 systemic super-class 차단 forcing function — per-Epic mandatory update gate + closed-binary update OR no-op explicit declare.

### Disjoint axis with related ADRs

- **ADR-078** (Living Architecture SSOT origin): 4 영역 closed-enum (모듈 / 경계 / 인터페이스 계약 / 데이터 흐름) **what** + per-plugin location **where** 정의. 본 ADR = **when** (Epic close 직전 mandatory) + **how-to-mark** (verdict field) — disjoint axis (content scope ↔ update timing).
- **ADR-065** (mechanical self-check 7-item): syntactic mechanical sync (label-registry / doc-locations / MANIFEST 등). 본 ADR = **semantic governance update** (architecture 본문 자체 변경). 동일 verdict packet 안 disjoint boolean field.
- **ADR-068 Amendment 1 / Amendment 3** (I-5 dimensional empirical / I-6 audit-gate-pointer): boundary completeness sub-invariant. 본 ADR = **Living Architecture update completeness** — boundary completeness 와 별 layer.
- **ADR-091** (DDD vocabulary governance): glossary SSOT + INV-5 vocabulary theater 차단. 본 ADR 5-anchor 중 "Open Decisions Pending" anchor 가 DDD vocabulary drift 추적 영역과 align — cross-ref-only.
- **ADR-111** (Confluence-mirror classification policy): mirror 대상 4 doc enum + cross-link discipline. 본 ADR write timing 의무 → ADR-111 §결정 5 cross-link discipline 동시 발효 (cascade dependency).

## 결정

### §결정 1 — per-Epic mandatory update gate

**ArchitectAgent 가 Epic close 직전 (또는 Epic 마지막 Story Phase 2 PR merge 직전) re-spawn 의무** — consumer self-owned `docs/architecture/<plugin>.md` Living Architecture page 의 5-anchor section 영향 평가.

**Trigger**:
- Epic close 직전 (Epic 마지막 Story Phase 2 PR merge 직전 시점, ADR-026 post-merge automation hook chain 안 합류)
- 또는 ArchitectAgent self-detect (Change Plan §3 affected_aggregates / §5 affected_modules / §7 affected_interfaces / §8 affected_data_flows 4 영역 중 1+ 변경 감지 시 — Epic 중 sub-Story 단위 발효 옵션, evidence-gated)

**Granularity rationale**: per-Story mandate = over-frequent, ArchitectAgent fatigue 위험. per-Epic = 적정 granularity (Epic = "사용자에게 새 capability 노출 완결 단위" 의미, Living Architecture 변경 자연 align).

**Write authority**: ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent (codeforge-design lane self-write boundary 안). DesignReviewPL = cross-validate (read-only verifier, §결정 4).

### §결정 2 — 5-anchor section update OR no-op explicit declare (closed-binary)

ArchitectAgent 는 다음 5 anchor section 중 **최소 1개 update 의무 OR `[living-arch-no-impact: <rationale>]` explicit declare** 의무.

**5-anchor closed-set** (ADR-078 §결정 1 4 영역 closed-enum + arc42 / C4 subset, sibling Story #1425 S3.1 codify base):

1. **arc42 §3 — Context & Scope** (시스템 boundary + 외부 actor + cross-cutting concern enumeration)
2. **arc42 §5 — Building Block View** (모듈 hierarchy + 책임 분담 + module boundary 표 — ADR-078 4 영역 closed-enum 의 "모듈" + "경계")
3. **C4 Container** (deploy unit + tech stack + runtime container — ADR-078 4 영역 closed-enum 의 "데이터 흐름" 의 container-level slice)
4. **C4 Component** (container 내부 component decomposition + interface contract — ADR-078 4 영역 closed-enum 의 "인터페이스 계약" + "데이터 흐름" 의 component-level slice)
5. **Open Decisions Pending** (현재 open 상태 design decision enumeration + 후속 ADR carrier 예약 — ADR-091 vocabulary governance + glossary cross-ref drift 추적 영역)

**Closed-binary invariant** — silent skip 차단:

- (a) 5 anchor 중 **1+ section update 완료** → §결정 3 verdict field `true` (update 발효 evidence)
- (b) 5 anchor 모두 update 불필요 → **`[living-arch-no-impact: <rationale>]` explicit declare 필수** (PR description 또는 Change Plan §13 안 marker) → §결정 3 verdict field `true` (explicit declare 발효 evidence)
- (c) update 0건 AND no-op declare 부재 → §결정 3 verdict field `false` → FIX 의무 (ArchitectAgent re-spawn) + DesignReviewPL findings[].type `living-architecture-not-updated` emit (§결정 4)

**Rationale** — (rejected) update OR skip silent = no-op 모호함 (retro reconstruct 불가, DesignReviewPL cross-validate 불가) → (a)/(b)/(c) 3-way explicit closed-binary 채택.

### §결정 3 — review-verdict-v4 v4.10 → v4.11 MINOR bump

**6번째 verdict-level optional bool field 신설** — `living_architecture_updated_self_check_passed: bool`:

- `true` = ArchitectAgent self-check 통과 — 5-anchor 1+ section update OR `[living-arch-no-impact: <rationale>]` explicit declare 1+ 형식 충족 (§결정 2 (a) 또는 (b))
- `false` = 충족 부족 — FIX 의무 (ArchitectAgent re-spawn) + DesignReviewPL findings[].type `living-architecture-not-updated` 동반 emit (§결정 4)
- null/omit = v4.10 이전 consumer backward-compat (Orchestrator 무시)

**Disjoint axis** (동일 verdict packet 안 별 boolean field, 6th):
1. `mechanical_self_check_passed` (v4.2, ADR-065 syntactic 7-item)
2. `boundary_completeness_self_check_passed` (v4.3, ADR-068 I-1~I-4)
3. `dimensional_empirical_self_check_passed` (v4.4, ADR-068 Amendment 1 I-5)
4. `marketplace_sync_declared` (v4.5, ADR-063 Amendment 1)
5. `audit_gate_pointer_self_check_passed` (v4.7, ADR-068 Amendment 3 I-6)
6. **`living_architecture_updated_self_check_passed` (v4.11, 본 ADR)** ← 신설
7. `deputy_axis_restructure_self_check_passed` (v4.6, ADR-068 Amendment 2 conditional scope)

**ADR-008 §결정 2 정합** — "새 선택 필드 추가" + "enum literal 추가" = MINOR bump 정합 (closed-enum 9 → 10 ratchet, additive only).

**Backward-compat invariant** — 기존 v4.10 consumer 가 본 6번째 field + 10번째 enum literal 무시 가능 (Runtime impact 없음).

### §결정 4 — DesignReviewPL cross-validate

**review-verdict-v4 `findings[].type` enum 10번째 literal 추가** — `living-architecture-not-updated`:

- DesignReviewPL 이 ArchitectAgent self-check `living_architecture_updated_self_check_passed: false` + no-op explicit declare 부재 (PR description / Change Plan §13 안 `[living-arch-no-impact: <rationale>]` 부재) detect 시 emit
- severity: P1 (FIX 의무 — ArchitectAgent re-spawn 후 §결정 2 (a) section update 또는 (b) explicit declare 추가)
- evidence 영역: 5-anchor enumeration + 각 anchor 의 update 부재 ground truth + Change Plan affected_aggregates / affected_modules / affected_interfaces / affected_data_flows 4 영역 변경 sample (Living Architecture impact 있을 가능성 sentinel)
- suggestion 영역: (a) 어느 anchor update 또는 (b) `[living-arch-no-impact: <rationale>]` declare 위치 명시

**Scope** — design lane only (DesignReviewPL primary emit lane). CodeReviewPL 영역 외 (governance write-time anchor, not code-time invariant — design layer 의미만 검증 가능).

**ADR-091 §결정 6 enforcement 3-tier 와 align** — DDD finding type (bc_violation / aggregate_violation / ubiquitous_language_drift) 와 disjoint axis (DDD 어휘 ↔ Living Architecture 본문 update timing).

### §결정 5 — warning tier 시작 + evidence-gated promote

**mechanical_enforcement_actions: [living-architecture-update]** — ADR-060 evidence-enforceable framework 정합:

- **Initial tier**: warning (declaration-only Wave 1 — ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습)
- **Mechanical wire** = S3.5 carrier (CFP-1429) — script `scripts/check-living-architecture-update.sh` + workflow `templates/github-workflows/living-architecture-update.yml` + label `hotfix-bypass:living-architecture-update` (next family member count race-check 후 결정 — Phase 2 carrier 영역, 본 PR scope 외)
- **Promote gate** (warning → blocking-on-pr): ADR-060 §결정 5 evidence-gated AND condition — (1) PR 누적 ≥ 20 + (2) bypass 외 failure = 0 + (3) sibling Story merged
- **Bypass channel**: `hotfix-bypass:living-architecture-update` label (per-entry namespace, audit-trailed exception channel — ADR-024 Amendment 3 정합, label-registry-v2 family member append = S3.5 mechanical wire scope)

**Pattern_count ≥ 2 재발 시 follow-up CFP MUST promote** — ADR-082 §결정 6 retain pattern (declaration-only Wave 1 의 deferred-followup hand-off invariant).

## 대안

| 대안 | rationale | reject 사유 |
|---|---|---|
| (A) Per-Story mandate | 최대 frequency = minimum stale window | ArchitectAgent fatigue 위험 (Story 별 5-anchor 평가 over-frequent) + Story = sub-deliverable 단위 (cumulative 본문 변경 빈도 ↔ Story 빈도 mismatch). per-Epic = 적정 granularity (Epic = "사용자 capability 노출 완결 단위" align). |
| (B) Section update OR silent skip | 단순 (no-op rationale 작성 면제) | no-op 모호함 — retro corpus enumeration 시 "왜 update 안 했는가" 사후 reconstruct 불가능. DesignReviewPL cross-validate 불가 (silent skip ↔ 정당한 no-op disjoint signal 부재). closed-binary explicit declare (§결정 2) 채택 — 모호함 차단. |
| (C) ArchitectAgent self-write only (DesignReviewPL cross-validate 면제) | code-time invariant 영역 외 (governance write-time anchor) | DesignReviewPL = read-only verifier 활성 시 cross-anchor parity check (CFP-1303 parallel_anchors_checked[] pattern verbatim 답습) — self-check false positive / false negative 차단. §결정 4 finding type emit 의무 채택. |
| (D) `findings[].type` enum 신설 0건 (verdict field 만 추가) | 단순 MINOR bump (field 1개) | DesignReviewPL emit 시 finding type 표준화 필요 (anchor_id + type 조합 stable identifier — debate-protocol-v1 §결정 2/4 정합). 기존 enum literal pattern (boundary-completeness / mechanical_sync_required / dimensional-empirical-gap / audit-gate-pointer-missing / DDD 3종 / confluence-mirror-link-missing) 답습 — 10번째 literal `living-architecture-not-updated` 추가 채택. |

## 결과

### 변경 영역 — 본 PR scope (4 file)

1. **`docs/adr/ADR-112-living-architecture-update-gate.md`** (본 file 신설)
2. **`docs/adr/ADR-RESERVATION.md`** — row 112 append (CFP-1426 active)
3. **`docs/inter-plugin-contracts/review-verdict-v4.md`** — v4.10 → v4.11 MINOR bump (frontmatter contract_version + related_adrs + authors[] + amendment_log[] + schema findings[].type enum + verdict-level field + schema header comment)
4. **`CLAUDE.md`** — `## ADR (docs/adr/ SSOT)` section ADR-112 cross-ref 1-2 line append (line cap PASS verify)

### 변경 영역 — 본 PR scope 외 (sibling / follow-up)

- **Sibling Story #1425 (S3.1)** = ADR-078 Amendment 2 (5-anchor section closed-set codify, base for §결정 2). ADR-078 본문 update 영역 = S3.1 scope, 본 PR 영역 외.
- **Sibling cross-repo PR** = `codeforge-review/agents/DesignReviewPLAgent.md` (DesignReviewPL check item 추가 — §결정 4 `living-architecture-not-updated` finding emit 영역). Follow-up CFP carrier.
- **Mechanical wire (S3.5 / CFP-1429)** = `scripts/check-living-architecture-update.sh` + `templates/github-workflows/living-architecture-update.yml` + label-registry-v2 family member `hotfix-bypass:living-architecture-update`. 본 PR scope 외.
- **Wrapper sibling sync (5 lane plugin)** = requirements/design/develop/test/pmo `review-verdict-v4.md` sibling drift = 본 PR scope 외 (별 sweep CFP carrier, CFP-1167 precedent).

### Backward-compat invariant

- review-verdict-v4 v4.10 consumer = 본 6번째 verdict-level field + 10번째 enum literal 무시 가능 (Runtime impact 없음)
- ADR-008 §결정 4 v.x compat 룰 정합 (additive only MINOR)

### Mechanical_enforcement_actions Wave 1 declaration-only

ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습:
- Wave 1 = declaration-only (`mechanical_enforcement_actions: [living-architecture-update]` frontmatter declare + 본문 §결정 5 mechanical action ↔ §결정 binding)
- Wave 2 = mechanical wire (S3.5 / CFP-1429) — script + workflow + label
- pattern_count ≥ 2 재발 시 follow-up CFP MUST promote (deferred-followup hand-off invariant)

## 해소 기준

N/A — permanent policy

**Rationale**: 본 ADR `is_transitional: false` permanent governance ratchet. Living Architecture per-Epic mandatory update gate (governance forcing function) = per-Epic mandate + closed-binary update OR explicit declare = ratchet 강화 방향 (ADR-064 §결정 7 evidence-gated symmetric ratchet 정합). 약화 시 (e.g., per-Epic → per-Quarter / closed-binary → silent-skip-allowed) = ADR-058 §결정 5 sunset_justification 의무 (evidence-gated 약화 방향).

`sunset_justification: null` (frontmatter) — permanent governance, sunset 면제.

## 관련 파일

- [ADR-078](ADR-078-living-architecture-doc.md) — Living Architecture SSOT origin (sibling Story #1425 S3.1 = 5-anchor section closed-set codify base)
- [ADR-111](ADR-111-confluence-mirror-classification-policy.md) — Confluence-mirror classification policy (§결정 1 closed-enum 4 mirror 대상 중 Living Architecture 2번째 entry, cascade dependency)
- [ADR-091](ADR-091-architectlane-ddd-vocabulary-governance.md) — DDD vocabulary governance (5-anchor 중 "Open Decisions Pending" cross-ref)
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — Boundary completeness invariants + verdict-level boolean field pattern (Amendment 1 / Amendment 3 pattern 답습)
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) — Mechanical self-check 7-item + verdict-level boolean field pattern
- [ADR-064](ADR-064-decision-principle-mandate.md) — 결정 원칙 mandate (§결정 7 evidence-gated symmetric ratchet)
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — ADR sunset criteria mandate (§결정 5 sunset_justification)
- [ADR-008](../inter-plugin-contracts/MANIFEST.yaml) — Inter-plugin Contract Versioning (MAJOR/MINOR bump)
- [review-verdict-v4 sibling](../inter-plugin-contracts/review-verdict-v4.md) — wrapper sibling reference (canonical = codeforge-review plugin)
