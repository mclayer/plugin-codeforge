---
kind: registry
registry: severity-propagation
version: "1.0"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/severity-propagation-v1.md
date: 2026-05-13
authors:
  - ArchitectAgent (CFP-529 carrier — RC#8 bidirectional binding SSOT)
version_history:
  - { version: "1.0", date: 2026-05-13, carrier: CFP-529, change: "initial — review-verdict-v4 findings[].severity ↔ label-registry-v2 severity:* ↔ evidence-checks-registry current_tier 3-way bidirectional binding SSOT. RC#8 (Codex 적대적 검토 발견, Epic #525) carrier." }
owner_adr: ADR-068
carrier_story: CFP-529
sibling_sync_exempt: true
related_adrs:
  - ADR-008  # Inter-plugin contract versioning (registry MINOR/PATCH sibling sync 면제)
  - ADR-010  # Inter-plugin Contract Sibling Sync (kind:registry exempt)
  - ADR-024  # hotfix-bypass label family
  - ADR-058  # ADR sunset criteria mandate (top-down ratchet)
  - ADR-060  # Evidence-enforceable promotion framework (current_tier enum)
  - ADR-063  # Marketplace atomic invariant (severity ↔ guard binding example)
  - ADR-064  # Decision principle mandate (top-down ratchet self-application)
  - ADR-068  # Boundary completeness invariants (RC#8 carrier)
related_files:
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - docs/inter-plugin-contracts/label-registry-v2.md
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - docs/evidence-checks-registry.yaml
  - docs/adr/ADR-068-boundary-completeness-invariants.md
  - docs/adr/ADR-060-evidence-enforceable-promotion-framework.md
related_plugins:
  - codeforge (wrapper, consumer of severity ↔ guard binding)
  - codeforge-review (canonical owner of review-verdict-v4 severity field)
---

# severity-propagation-v1 — Inter-plugin Contract Registry

`severity` 어휘의 cross-channel propagation SSOT. review-verdict findings 의 `severity` field 가 label-registry-v2 `severity:*` family + evidence-checks-registry `current_tier` enum 과 bidirectional binding 의무를 정의한다.

**kind**: registry (sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2 정합)

## 1. 목적

### RC#8 (Codex 적대적 검토 발견, Epic #525) carrier

severity 정의 변경 시 implementation guard / test threshold / hotfix-bypass label 도 동기 갱신 의무. 역방향 동일 — guard 강도 변경 시 severity 정의 재평가 의무. 본 contract = RC#8 의 mechanical SSOT carrier.

### Cross-channel boundary

`severity` 어휘는 3 channel 에 동시 등장:

1. **review-verdict-v4 `findings[].severity`**: P0 / P1 / P2 / critical / blocker enum
2. **label-registry-v2 `severity:*` family**: `severity:P0` / `severity:P1` / `severity:P2` / `severity:critical` / `severity:blocker` label set
3. **evidence-checks-registry `current_tier`**: warning / blocking-on-pr / blocking-on-merge / hotfix-bypass enum (ADR-060 framework)

3 channel 의 severity 어휘 의미가 drift 시 review packet ↔ GitHub label ↔ CI gate 의 enforce 강도가 mismatch → boundary gap.

### 본 contract 의 범위 (in scope)

- 3 channel 간 severity ↔ label ↔ tier mapping 정합성 정의
- bidirectional ratchet 규칙 (severity bump / tier 약화 방향) 명시
- mechanical enforcement hook 위치 명시 (CFP-529 Phase 2 carrier)

### 본 contract 의 범위 외 (out of scope)

- severity enum 자체 값 정의 (review-verdict-v4 SSOT)
- label naming convention (label-registry-v2 SSOT)
- tier promotion threshold (ADR-060 framework SSOT)

## 2. Schema

본 contract 는 mapping 규칙 SSOT 이며 자체 wire format 미보유 (registry kind). 3 channel 간 정합성 관계는 다음 schema 로 표현:

```yaml
# 3-way binding schema (conceptual)
severity_propagation:
  review_verdict_severity: <P0|P1|P2|critical|blocker>     # review-verdict-v4 findings[].severity
  label_registry_severity: <severity:P0|...|severity:blocker>  # label-registry-v2 severity:* family
  evidence_checks_tier: <warning|blocking-on-pr|blocking-on-merge|hotfix-bypass>  # ADR-060 current_tier
  guard_continue_on_error: <true|false>                    # workflow yml continue-on-error
  binding_direction: <forward|backward|lateral>            # CFP-529 Phase 2 3-direction enum
```

### 3-way Binding Matrix (정합성 schema)

| Source channel | Target channel 1 | Target channel 2 | Direction | Binding 규칙 |
|---|---|---|---|---|
| review-verdict-v4 `findings[].severity` bump | label-registry-v2 `severity:*` bump | evidence-checks-registry `current_tier` 승격 후보 등재 | severity → label → tier | ratchet 강화 — severity P2 → P1 시 label `severity:P1` add + tier 승격 평가 의무 |
| label-registry-v2 `severity:*` 변경 (label 추가 / category 변경) | review-verdict-v4 severity enum 확장 | evidence-checks-registry tier mapping 확장 | label → severity → tier | label 변경 = review-verdict schema bump 의무 (ADR-008 §결정 2 MINOR) |
| evidence-checks-registry `current_tier` 승격 (warning → blocking-on-pr) | review-verdict severity baseline 평가 | label-registry-v2 severity:* 강도 평가 | tier → severity → label | tier 승격 = severity 정의 재평가 의무 (downgrade 차단) |

## 3. 항목

### 3.1 Bidirectional Ratchet 규칙

#### Rule 3.1.1 — severity bump ⇒ guard 강도 ratchet 의무

severity (P2 → P1 → critical → blocker) bump 시 다음 mechanical 갱신 의무:

- label-registry-v2 `severity:*` label add (해당 severity level 없으면 신설)
- evidence-checks-registry 해당 entry `current_tier` 승격 후보 자동 등재 (ADR-060 framework gate 평가 trigger)
- workflow `continue-on-error: true` → `continue-on-error: false` 평가 (blocking 승격 시점)

#### Rule 3.1.2 — severity downgrade 금지 (ratchet, ADR-058 self-application)

label-registry-v2 `severity:*` family 의 severity level downgrade (예: `severity:P1` 삭제) = ADR-058 §결정 5 sunset_justification 의무 — 3-tuple metric / who / how 정량 명시 없이 차단.

#### Rule 3.1.3 — tier 약화 시 ADR Amendment 의무

evidence-checks-registry `current_tier` 약화 (blocking-on-pr → warning downgrade / blocking-on-merge → blocking-on-pr) 시:
- ADR-058 §결정 5 sunset_justification 의무 (해당 entry 의 owner_adr Amendment carrier)
- 본 contract `severity-propagation-v1` Amendment trigger 의무 (severity baseline 재평가)

#### Rule 3.1.4 — guard 강도 (workflow `continue-on-error`) 와 severity 의 bidirectional binding

- guard `continue-on-error: false` (blocking) ⇔ severity P1 / critical / blocker
- guard `continue-on-error: true` (warning) ⇔ severity P2 (advisory)
- 두 영역 mismatch 시 mechanical detection (CFP-529 Phase 2 handoff wording linter 영역)

### 3.2 Enforcement Hooks

#### 3.2.1 Mechanical (CFP-529 Phase 2 carrier)

`scripts/check_handoff_wording.py` 안의 severity-propagation check sub-routine — 3 channel severity 어휘 일관성 검증.

검증 항목:
- review-verdict-v4 `findings[].severity` enum value ↔ label-registry-v2 `severity:*` label name 매핑 정합
- label-registry-v2 `severity:*` ↔ evidence-checks-registry `current_tier` 매핑 정합
- workflow `continue-on-error` ↔ severity 의 bidirectional binding 검증

#### 3.2.2 Manual (DesignReview + CodeReview cross-validate)

- DesignReviewPL: severity 어휘 변경 detect 시 본 contract reference 의무 (ADR-068 §결정 2 Tier B 영역)
- CodeReviewPL: impl level severity 어휘 (예: `raise SomeError(severity="P0")` 코드 패턴) cross-validate (Tier C 영역)

### 3.3 Cross-references

- **ADR-068 (Boundary completeness invariants)**: RC#8 carrier. §결정 2 dual-binding 으로 severity ↔ guard mismatch detection.
- **ADR-060 (Evidence-enforceable promotion framework)**: `current_tier` 4-tier enum (warning / blocking-on-pr / blocking-on-merge / hotfix-bypass) SSOT. 본 contract 가 severity ↔ tier 매핑 의무 정의.
- **ADR-064 (Decision principle mandate)**: top-down ratchet self-application — severity / tier downgrade 차단 (Rule 3.1.2 / 3.1.3).
- **ADR-024 Amendment 3 (hotfix-bypass label family)**: per-entry namespace `hotfix-bypass:<entry-name>` exempt channel.
- **review-verdict-v4** (`docs/inter-plugin-contracts/review-verdict-v4.md`): `findings[].severity` field SSOT.
- **label-registry-v2** (`docs/inter-plugin-contracts/label-registry-v2.md`): `severity:*` label family SSOT.
- **evidence-checks-registry-v1** (`docs/inter-plugin-contracts/evidence-check-registry-v1.md`): `current_tier` enum SSOT.

## 4. 변경 규칙

### 4.1 Versioning Policy

- **kind:registry**: MINOR / PATCH bump = sibling sync 면제 (ADR-010 §결정 2)
- **MAJOR bump**: 본 contract 자체 breaking change 시 별도 ADR 의무 (ADR-058 §결정 5 sunset_justification 적용)
- **Amendment**: ratchet evidence-gated symmetric (강화·약화 양방향 + 양방향 evidence 의무, ADR-058 §결정 5 + ADR-064 §결정 7 self-application)

### 4.2 SemVer rule (ADR-008 §결정 2 정합)

- **MAJOR**: severity 어휘 enum 자체 breaking change (P0~blocker 5단 → 다른 set) / 본 schema 의 channel set (3개) 변경
- **MINOR**: ratchet 규칙 추가 / cross-reference 신규 ADR / new channel 추가 (예: 4번째 channel)
- **PATCH**: 오타 / 설명 보강 / 예시 추가

### 4.3 Amendment trigger 조건

- (a) review-verdict-v4 `findings[].severity` enum value 추가 / 삭제 시 (MINOR / MAJOR 평가)
- (b) label-registry-v2 `severity:*` family 변경 시 (MINOR / MAJOR 평가)
- (c) evidence-checks-registry `current_tier` enum 변경 시 (MINOR / MAJOR 평가)
- (d) workflow `continue-on-error` ↔ severity 매핑 규칙 변경 시 (MINOR 평가)

### 4.4 Ratchet 보존 의무 (downgrade 차단)

본 contract 의 모든 Amendment 는 evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무, ADR-064 §결정 7 self-application). 약화 방향 (severity downgrade / tier 약화 / channel 제거) 은 ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 정량 명시 없이 차단.

### 4.5 CFP-529 Phase 2 mechanical implementation 참조

본 contract 의 mechanical enforcement = `scripts/check_handoff_wording.py` (Wave 3 Phase 2, CFP-529 carrier).

검증 mechanism:
- mechanical pre-screen (5 패턴): synonym substitution / unit drift / modal downgrade / boundary inversion / scope widening
- AI escalate stub (3 패턴): precision loss / conditional erasure / actor drift
- direction enum 3-way: forward (설계 → 구현 verbatim 매칭) / backward (구현 → 설계 reverse lookup → ADR Amendment trigger warning) / lateral (sibling section §3 ↔ §7 ↔ §8.5 cross-section diff)

CFP-529 Phase 2 PR (별 PR) merge 시 mechanical lint 활성.
