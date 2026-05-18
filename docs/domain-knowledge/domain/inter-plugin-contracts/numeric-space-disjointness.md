---
title: Numeric-space-sharing channel disjointness — narrative SSOT for ADR-084 D2-3 declaration obligation
area: inter-plugin-contracts
topic: numeric-space-disjointness
type: domain-knowledge
date: 2026-05-19
carrier_story: CFP-989
related_adrs:
  - ADR-084  # 본 narrative SSOT 의 carrier ADR (3-곳 declare 의무 3rd location)
  - ADR-076  # reconcile-protocol-v1 declarative reconciliation (first applied case host)
  - ADR-082  # disjoint 4-layer 표 governance pattern source
  - ADR-068  # boundary completeness invariants (scope disjoint — Q1 분기)
owner_agent: codeforge-design:ArchitectAgent
introduced_by: CFP-989
---

# Numeric-space-sharing channel disjointness

ADR-084 의 D2-3 declaration obligation 의 3rd location narrative SSOT. inter-plugin contract 안 두 (이상) channel 이 동일 numeric domain (integer / enum / ordinal) 을 encoding 으로 share 할 때, **encoding overlap 은 사실, semantic overlap 은 금지** 의 원리 + sample fixture + 위반 시 failure mode + audit checklist 를 narrative 로 풀어 쓴 entry.

## 핵심 원리 (3-tier 통찰)

### Tier 1 — encoding overlap fact ≠ semantic overlap forbidden

두 channel 이 동일 numeric range 를 encoding 으로 share 하는 것은 사실 진술. encoding share 자체는 contract 위반 아님 — compatibility constraint 영역 (예: 둘 다 0-255 byte 범위 사용, JSON serialize 시 동일 type). 그러나 두 channel 의 **semantic 이 disjoint** 면 cross-channel propagation 시 boundary 변환 함수 explicit 명시 의무 — implicit identity propagation 은 자동 결함 (under-specification).

선례 동형: type theory 의 nominal vs structural typing — 같은 underlying representation (예: `type UserId = i64; type OrderId = i64;`) 이라도 nominal type disjoint 면 cross-substitute 금지 (`fn lookup_user(id: UserId)` 에 `OrderId` 값 직접 전달 = compile error). encoding 동형 + semantic disjoint = 두 layer 분리 invariant.

### Tier 2 — variable boundary 변환 함수 explicit 명시 의무

channel A → channel B propagate 시 boundary 자체가 contract surface. boundary 변환 함수 부재 = source channel max 가 target channel 로 그대로 흘러들어가는 over-propagation 자동 결함 (CFP-986 exact failure mode).

**identity propagation 도 explicit 명시 의무** (ADR-084 EC-4): 두 channel 의 semantic 이 동등인 경우 (드문 case — 사실상 같은 channel 의 두 alias) 라도 "channel A.range ≤ channel B.range AND semantic 동등 의도" clause 명시 의무. identity 단순 코드 동등 비교 = under-specification (의도 unrecorded → 후속 maintainer 가 의미 disjoint 화 시 missed update path).

### Tier 3 — implicit clause = under-specified-contract → defensible-misread → post-merge defect

P-3 패턴 (Epic CFP-858 retro emission): spec 자체는 sound 했으나 disjointness invariant 가 implicit 으로 남겨진 영역 → defensible-misread (reviewer / implementer 가 합리적 추론으로 implicit identity 가정) → post-merge defect (CFP-986 reconcile-overlay.sh:490-491 silent false `result: FAILED` 발생).

implicit clause = **무한 defensible-misread surface**. 1 reviewer 가 catch 해도 다음 reviewer / maintainer / implementer / Codex worker 가 동일 misread 재현 가능. explicit codify 만이 defensible-misread surface 차단.

## Sample fixture (CFP-986 first applied case)

### Setup

`docs/inter-plugin-contracts/reconcile-protocol-v1.md` 의 두 channel:

| Channel | Encoding | Semantic | Range |
|---|---|---|---|
| `detect-repo-kind exit` (classification) | small non-negative integer | repo kind classification (which path consumer takes through reconcile-overlay.sh) | `0=plugin / 1=consumer / 2=mixed / 3=unknown` (0-3) |
| `_S2_MAX_EXIT` (severity) | small non-negative integer | reconcile result severity (whether the reconcile result is acceptable for consumer-facing reporting) | `0=proceed / 1=abort / 2=degraded` (0-2) |

**encoding overlap fact**: 둘 다 small non-negative integer encoding (overlap range = 0-2). **semantic disjoint**: classification 은 repo kind, severity 는 reconcile result outcome — 동일한 0-2 integer value 가 두 channel 에서 완전히 다른 의미.

### Defect (pre-b6d7eb5)

`reconcile-overlay.sh` line 490-491:
```bash
_ec=$(detect-repo-kind ...)
_S2_MAX_EXIT=$_ec  # implicit identity propagation (over-propagation defect)
```

- `_ec=1` (consumer kind, classification semantic) → `_S2_MAX_EXIT=1` (filter abort, severity semantic) → `result: FAILED` 기록
- 정상 consumer reconcile flow 가 false `result: FAILED` silent 기록 — post-merge defect

### Fix (b6d7eb5, CFP-986 §4.12/§4.13 spec clarification)

`reconcile-protocol-v1.md` §4.12 `exit_code_contract.classification_severity_disjoint_invariant` (D2-1 location):
```yaml
classification_severity_disjoint_invariant:
  channel_a: detect-repo-kind exit (classification, 0-3)
  channel_b: _S2_MAX_EXIT (severity, 0-2)
  encoding_overlap_range: 0-2 (fact)
  semantic_disjoint: true (forbidden: identity propagation)
  boundary_transform_function: |
    severity = (1 if (classification ∈ {1, 2}) AND filter_abort) else (2 if degraded) else 0
  rationale: classification ≠ severity — both small non-negative integer encoding but disjoint semantic
```

`reconcile-protocol-v1.md` §4.13 `degradation_propagation.s2_filter_abort.classification_not_severity_clause` (D2-1 boundary 변환 함수 명시 location):
```yaml
classification_not_severity_clause:
  forbidden_propagation: _S2_MAX_EXIT = _ec  # identity (over-propagation defect, CFP-986 reproduce)
  required_propagation: |
    if filter_abort AND classification ∈ {1=consumer, 2=mixed}: _S2_MAX_EXIT = 1 (abort)
    elif degraded_signals_present: _S2_MAX_EXIT = 2 (degraded)
    else: _S2_MAX_EXIT = 0 (proceed)
```

### ADR-084 §D3 retroactive validation (D2-2 location — ADR 본문 declare)

ADR-084 §D3 = CFP-986 b6d7eb5 first applied case retroactive validation. `[DISJOINT]` marker explicit annotation (ADR-084 D2-2 형식).

### 본 narrative entry (D2-3 location — domain-knowledge narrative SSOT)

= 현재 file. ADR-084 D2 3-곳 declare 의무의 3rd location 충족.

## Audit checklist (DesignReview lane MUST flag — ADR-084 D4)

inter-plugin contract 신설 / 갱신 (kind:contract / kind:registry 모두) touch 시 DesignReviewPL / DesignReviewAgent 가 수행 의무 audit:

- [ ] **Audit-A (encoding overlap detect)**: contract 본문 안 두 (이상) numeric field / enum field 가 동일 numeric range 를 encoding 으로 share 하는지 grep-presence 확인 (`range:` / `enum:` / `values:` numeric value 동등 비교)
- [ ] **Audit-B (cross-channel propagation detect)**: cross-channel propagation path 존재 시 boundary 변환 함수 explicit clause 가 contract 본문 안에 있는지 확인 (ADR-084 D2-1 충족 여부)
- [ ] **Audit-C (3-곳 declare 의무 충족 확인)**:
  - D2-1: inter-plugin contract 본문 `## Numeric Space Disjointness` section (또는 `<A>_<B>_disjoint_invariant` clause) 존재
  - D2-2: ADR 본문 `[DISJOINT]` 또는 `[SHARED-semantic]` marker explicit annotation 존재
  - D2-3: `docs/domain-knowledge/domain/inter-plugin-contracts/<topic>.md` narrative SSOT entry 존재
- [ ] **미충족 시 P1 finding emit**: `finding.type: "numeric-space-disjointness-implicit"` + `finding.evidence: <field-A>+<field-B>+<numeric-range>+<propagation-path>` + suggested FIX = D2-1/2/3 3-곳 declare 추가

## False positive 영역 (EC-1)

단일 contract 내 numeric-space 분리 + cross-propagation path 부재 시 ADR-084 의무 미발효 (EC-1):

- 예: `label-registry-v2.md` 안 `severity: {0,1,2}` enum + `tier: {0,1,2}` enum — 둘 다 0-2 range 이나 cross-channel propagation path 부재 (label registry 자체가 source-of-truth, propagation target 채널 없음).
- 예: 동일 yaml schema 안 두 enum field 가 의미 자명 disjoint + cross-propagation path 부재 (e.g., `priority: {0,1,2,3}` + `phase: {0,1,2}` 동일 doc 안).

이 영역은 lint false positive 영역 — DesignReviewPL 인지 의존 (D4 behavioral directive 만 적용, lint 자동 grep 불가).

## Sentinel pattern_count counter

현재 pattern_count = **1** (CFP-986 b6d7eb5 single sample).

**Sentinel reach 조건** (ADR-084 D6.3): pattern_count ≥ 2 recurrence (CFP-986 외 추가 instance 1+ 발생) → follow-up CFP MUST promote to mechanical lint.

**후속 candidate site (Researcher §6 enumerate)** [hypothesis — sentinel reach 시 carrier 검증 영역]:
1. ADR-052 touchpoint(1-6) ↔ severity(0-2) ↔ ADR-067 max-FIX(0-3) 3-way cohabitation
2. review-verdict-v4 severity ↔ label-registry-v2 severity:* ↔ evidence-checks-registry current_tier 3-way bidirectional binding (severity-propagation-v1 §결정 — 이미 RC#8 binding 정의되어 있으나 numeric-space-sharing 영역 explicit codify 영역 audit 필요)
3. fix-event-v1 affected_scope enum + comment-prefix-registry-v1 prefix enum 등

본 candidate site enumerate 는 RequirementsPL §6.5 [hypothesis] 영역 — Architect lane 본문 작성 시 fixture enumerate 영역 아님 (Q2-A retroactive validation only default 정합).

## 위반 시 failure mode (CFP-986 exact reproduction)

implicit identity propagation 시 다음 failure mode 발현:

1. **Silent false reporting**: 정상 flow 가 false `result: FAILED` 또는 false `severity: 1` 기록 (CFP-986 reconcile-overlay.sh exact behavior)
2. **Inverse defect (post-merge)**: spec self-test 가 PRIMARY consumer use case 에 대해 false FAILED 발생 — IntegrationTest gate (Epic-level reactivation) 가 catch (Epic CFP-858 §6.3 evidence)
3. **Cumulative misread cascade**: 1 maintainer catch 해도 다음 maintainer 가 동일 misread 재현 — implicit clause = defensible-misread surface 무한 재발
4. **Post-merge unit test silently green**: unit-level test 가 single-aggregator bypass 영역 (TC-RF-3 evidence, CFP-986 root cause) → reconcile-integration path actual exec 만 catch

## 관련 파일

- [ADR-084](../../adr/ADR-084-numeric-space-sharing-channel-disjointness.md) — 본 narrative SSOT 의 carrier ADR (3-곳 declare 의무 3rd location)
- [ADR-076](../../adr/ADR-076-declarative-reconciliation-upgrade.md) — reconcile-protocol-v1 declarative reconciliation host
- [ADR-082](../../adr/ADR-082-write-time-self-write-verification-mandate.md) — disjoint 4-layer 표 governance pattern source
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` — CFP-986 §4.12/§4.13 first applied case (b6d7eb5)
- [EPIC-RESULTS-CFP-858](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/retros/EPIC-RESULTS-CFP-858.md) — §6.3 P-3 systemic cluster (본 ADR-084 E-3 emission origin)
