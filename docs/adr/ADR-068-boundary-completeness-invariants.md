---
adr_number: 68
title: Boundary completeness invariants (semantic dual-binding)
status: Accepted
category: governance
date: 2026-05-13
is_transitional: false
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - skills/review-responsibility/SKILL.md
  - docs/evidence-checks-registry.yaml
  - scripts/check-wording-ssot.sh
  - templates/github-workflows/wording-ssot-check.yml
related_stories:
  - CFP-525
  - CFP-526
  - CFP-527
absorbed_issues:
  - 438
related_adrs:
  - ADR-008
  - ADR-058
  - ADR-059
  - ADR-060
  - ADR-063
  - ADR-064
  - ADR-065
  - ADR-067
mechanical_enforcement_actions:
  - name: boundary-completeness-self-check
    binding: §결정 2
    evidence_check: boundary-completeness-self-check (verdict field, blocking-on-pr 승격 후보)
  - name: wording-ssot-grep-lint
    binding: §결정 5
    evidence_check: wording-ssot-grep-lint (warning tier, registry entry 신설)
---

# ADR-068: Boundary completeness invariants (semantic dual-binding)

## 상태

`Accepted` (2026-05-13). ADR-065 (mechanical syntactic 7-item self-check) 의 semantic 상위 개념. 분리 운영 — verdict packet 양 별도 boolean field emit.

## 맥락

mctrader-hub MCT-150 Phase 2 case study (Epic CFP-525 brainstorm spec L17) — design-review PASS 후 code-review 에서 **반복 발견된 boundary completeness gap 4회** (양 reviewer independent identification). 4 gap 의 type 별 분류:

1. **API contract semantics 누락** — public method 의 return enum 의미가 docstring 에 부재 → caller 임의 해석
2. **Cross-module status enum propagation 누락** — module A 가 SUCCESS/BLOCKED/ESCALATED 3-state enum 반환, module B caller 가 1-state 만 분기 처리 → silent pass-through
3. **Guard placement intent 모호** — invariant guard 가 "함수 진입 시점 무조건" 인지 "특정 path 한정" 인지 ADR 본문 부재 → caller assumption 오류 = re-fix
4. **Wording desync 13곳** — Story §3 결정 wording ↔ ADR §결정 wording ↔ impl enum identifier 양 방향 불일치

Wave 1 (CFP-526, ADR-067) 은 FIX cycle escalation 의 **사후 처리** (max FIX 3/3 도달 시 implementability reassessment + 사용자 escalation) — boundary gap 자체의 발생 빈도는 미감소. Wave 2A (CFP-527, 본 ADR) = **사전 차단** — ArchitectAgent prompt surface 에 4 semantic invariants 의무화 + DesignReview + CodeReview dual-binding cross-validate 로 H6 systemic root cause (design ↔ code review boundary completeness gap) 의 발생 자체를 design 시점에 차단.

ADR-065 (Accepted 2026-05-13) 는 **syntactic** 영역 (file path / link target / version / cross-ref 7-item) self-check. 본 ADR-068 = **semantic** 영역 (enum / state / wording / guard placement intent 4-invariant) self-check. 검증 방법 차원 (mechanical grep/regex vs LLM judgment + cross-lane validation) 자체가 disjoint — 분리 운영 정합. #438 (ArchitectAgent Phase 1 mechanical sync self-check 7-item carrier) 는 ADR-065 구현 일부로 포섭 (본 ADR-068 §결정 3 cross-ref).

## 결정

### 결정 1 — 4 semantic boundary completeness invariants 정의

ArchitectAgent §3 (관련 ADR / 결정) / §7 (Change Plan / 설계 서사) 작성 시 4 invariants 모두 verification format 통과 의무.

**I-1: API contract semantic completeness**
- 정의: public method/function docstring 에 입력/출력 의 enum / state semantics 명시 의무 (예: "returns SUCCESS / BLOCKED / ESCALATED with rationale"). 누락 시 caller 가 임의 해석 가능 = boundary gap.
- Verification format: **docstring-template** — public surface 각 method 의 docstring 이 (a) parameter 의 valid enum value 열거 + (b) return value 의 enum/state semantics 열거 + (c) error/escalation path 의 trigger condition 명시 3-key 정합.

**I-2: Cross-module propagation completeness**
- 정의: module A method 가 status enum 을 반환할 때, 호출 site (module B/C) 가 enum 별 분기 처리 의무. 미처리 enum 값 = silent pass-through = caller gap.
- Verification format: **propagation-matrix** — Story §7 본문 또는 ADR §결정 표에 enum 별 caller-side 분기 매핑 (row: enum value × column: caller module × cell: handling logic 요약). 미처리 enum × caller pair 부재 의무.

**I-3: Unconditional vs conditional guard placement intent**
- 정의: invariant guard (assertion / pre-condition / post-condition) 의 위치가 "함수 진입 시점 무조건" 인지 "특정 path 한정" 인지 ADR 본문에 명시 의무. caller 가 guard 위치 가정 오류 = re-fix.
- Verification format: **guard-placement-diagram** — Story §7 또는 ADR §결정 본문에 guard 별 (a) placement (function entry / branch entry / loop body / cleanup path 등) + (b) condition (unconditional / conditional with predicate) + (c) failure mode (assertion error / state transition / log + continue) 3-key 명시.

**I-4: Wording SSOT**
- 정의: Story 본문 (§3 결정 / §7 아키텍처) ↔ ADR ↔ impl (enum identifier / method name / docstring noun phrase) 양 방향 wording 동기화 의무. 13곳 desync (MCT-150 evidence) baseline.
- Verification format: **wording-sync-table** — Story §3/§7 의 enum identifier (UPPER_SNAKE_CASE) + method name (camelCase / snake_case) + 핵심 noun phrase (Korean 또는 English) 목록과 ADR 본문 + impl source identifier 의 매칭 표. mechanical 영역 (enum/method identifier) = `scripts/check-wording-ssot.sh` lint (§결정 5). semantic phrase 영역 = DesignReview manual flag.

### 결정 2 — Dual-binding (design lane authoring + code-review cross-validate)

3-tier enforcement:

**Tier A (authoring-time)**: ArchitectAgent prompt 의무
- §3 / §7 작성 시 4 invariants 별 verification format self-check 수행
- verdict packet `boundary_completeness_self_check_passed: bool` emit (review-verdict-v4 v4.3 optional field)
- 4 invariants 모두 PASS 일 때만 true emit. 1+ FAIL 시 false emit + `findings[]` 에 미통과 invariant 별 evidence 동반 (`findings[].type: "boundary-completeness"`)

**Tier B (design-review-time)**: DesignReviewPL 의무
- review-pl-base.md §3 의 4 invariants flag 항목 검증 의무
- design lane perspective — ArchitectAgent §3/§7 의 verification format 누락 발견 시 finding emit
- `findings[].type: "boundary-completeness"` literal + severity P0~P3

**Tier C (code-review-time)**: CodeReviewPL 의무 (cross-validate)
- review-pl-base.md §3 동일 4 invariants flag 항목 검증 의무
- code lane perspective — impl ↔ ADR ↔ Story 매핑 검증. impl docstring 누락 / caller enum 분기 미처리 / impl guard 위치 mismatch / impl identifier wording desync 시 finding emit
- 동일 `findings[].type: "boundary-completeness"` literal + severity P0~P3
- dedup: 같은 `anchor_id` 양 lane finding 시 severity 높은 쪽 채택 (skills/review-responsibility/SKILL.md)

Cross-validate divergence (DesignReview = PASS, CodeReview = FIX 또는 vice versa) 시 = debate-protocol-v1 `auto_on_divergence` 발동 surface (ADR-059). CFP-530 (Wave 4) Amendment 1 positive sibling.

### 결정 3 — ADR-065 와의 분리 운영 근거 + #438 absorption

ADR-065 (mechanical syntactic 7-item) 와 본 ADR-068 (semantic 4-invariant) 분리 운영. 동일 ArchitectAgent verdict packet 의 **두 별도 boolean field** emit:

| Field | Owner ADR | Scope | Verification method |
|---|---|---|---|
| `mechanical_self_check_passed` | ADR-065 | Syntactic 7-item (file path / link target / version / cross-ref / label registry / doc location / workflow self-app) | mechanical grep / regex / file Read |
| `boundary_completeness_self_check_passed` | ADR-068 (본) | Semantic 4-invariant (I-1~I-4: API contract / propagation / guard placement / wording SSOT) | LLM judgment + cross-lane validation |

분리 사유:
1. **검증 방법 차원 disjoint** — syntactic = mechanical (deterministic), semantic = judgment (LLM) + cross-lane validation
2. **Owner agent 동일 (ArchitectAgent) but emit field 독립** — 동시 PASS 의무 (양 boolean true 일 때만 Phase 1 commit 진행)
3. **ADR-058 sunset_justification 불필요** — ADR-065 계속 active, 본 ADR-068 = ratchet 강화 방향 (top-down 강화, ADR-058 §결정 5 정합)

**#438 absorption**: ArchitectAgent Phase 1 mechanical sync self-check 7-item carrier Issue 는 ADR-065 구현 일부로 포섭. 본 CFP-527 (ADR-068 carrier) Phase 2 PR `Closes #438` reference 가 absorption 명문화.

### 결정 4 — EC-2 동시 발동 순서 (Wave 1 ↔ Wave 2A)

ADR-068 invariant 검증 fail + ADR-067 max FIX 3/3 도달 동시 발생 시 처리 순서:

1. **Trigger 순서**: ADR-068 invariant 검증 fail (Tier A self-check 또는 Tier B/C cross-validate) → ArchitectPL implementability 평가 (ADR-067 §결정 1) trigger
2. **Escalation 결정**: invariant fail 사유가 "구현 불가" 영역 진입 시 = ADR-067 사용자 escalation trigger 의 부분집합 (즉, invariant fail = implementability assessment input 의 evidence)
3. **§10 FIX Ledger row 기록**: row 의 `reasoning_carryover` field (fix-event-v1 1.2, CFP-526) 의 3-part 구조 활용:
   - `invariant_summary`: 4 invariants 중 어떤 invariant fail (I-1~I-4) + verification format 미통과 사유
   - `disputed_claims`: design lane vs code lane 의 divergent claim (cross-validate divergence 시)
   - `transcript_ref`: debate-protocol-v1 발동 시 Story §9 transcript section anchor link

본 결정 4 = ADR-067 (Wave 1) 와 ADR-068 (Wave 2A) 의 시간적 정합. ArchitectPLAgent prompt 본문 명세 의무.

### 결정 5 — Wording SSOT enforcement (warning-tier evidence-enforceable)

ADR-060 evidence-enforceable framework 의 4번째 warning-tier entry (auto-phase-label / forbid-list / adr-sunset-criteria 다음):

- **Registry entry**: `wording-ssot-grep-lint` (`docs/evidence-checks-registry.yaml`)
  - `owner_adr`: ADR-068
  - `current_tier`: warning
  - `hotfix_bypass_label`: `hotfix-bypass:boundary-wording` (ADR-024 Amendment 3 per-entry namespace 정합)
  - `promotion_gate`: PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged → blocking-on-pr 승격 (별도 CFP, Wave 2A 직접 scope 외)
- **Lint script**: `scripts/check-wording-ssot.sh`
  - Mechanical scope — Story §3/§7 enum-like identifier (UPPER_SNAKE_CASE 4+ char) 추출 → impl source ripgrep 매칭
  - Story file 없을 시 skip exit 0 (advisory only)
  - Semantic phrase NLP 영역 = warning tier 직접 scope 외 (DesignReview manual flag)
- **Workflow template**: `templates/github-workflows/wording-ssot-check.yml`
  - `continue-on-error: true` advisory only (warning tier)
  - consumer overlay carrier (default off, opt-in)
- **Self-app**: `.github/workflows/wording-ssot-check.yml` byte-identical
- **False positive 의식**: enum identifier vs Korean noun phrase 매칭 시 false positive 발생 가능 — `[A-Z][A-Z0-9_]{3,}` 4+ char UPPER_SNAKE_CASE 한정 regex 로 좁힘. 첫 20 PR sample 측정 후 blocking 승격 별도 CFP carrier.

승격 gate AND condition (ADR-060 §결정 7 정합):
1. PR 누적 ≥ 20 (entry introduced_in CFP-527 merge 후)
2. bypass label 외 failure count = 0
3. sibling Story merged (Wave 2B / Wave 3 / Wave 4 sibling 영역 중 1+ merge)

3 AND condition 충족 시 별도 CFP carrier 가 blocking-on-pr tier 로 승격 신청.

### 결정 6 — Mechanical enforcement actions binding

frontmatter `mechanical_enforcement_actions[]` 2 entry (ADR-040 Amendment 3 §결정 7.A list[object] schema 정합):

| Action name | Binding §결정 | Evidence check entry |
|---|---|---|
| `boundary-completeness-self-check` | §결정 2 (3-tier dual-binding) | verdict field `boundary_completeness_self_check_passed: bool` (review-verdict-v4 v4.3) + DesignReview/CodeReview `findings[].type: "boundary-completeness"`. blocking-on-pr 승격 후보 (별도 CFP). |
| `wording-ssot-grep-lint` | §결정 5 (warning-tier evidence-enforceable) | `docs/evidence-checks-registry.yaml` entry (current_tier: warning) + `scripts/check-wording-ssot.sh` + `.github/workflows/wording-ssot-check.yml` |

ADR-040 Amendment 3 §결정 7.A `mechanical_enforcement_actions[]` list[object] schema 정합 — name / binding / evidence_check 3-key verbatim.

## 관련 ADR

| ADR | 관계 |
|---|---|
| ADR-065 (ArchitectAgent Phase 1 mechanical sync self-check) | **분리 운영 base** — syntactic 7-item carrier. 본 ADR-068 = semantic 4-invariant. 동일 ArchitectAgent verdict packet 양 별도 boolean field. ADR-065 계속 active (sunset 불필요), #438 ADR-065 구현 일부로 포섭. |
| ADR-067 (Fix-ledger implementability escalation, Wave 1) | **EC-2 동시 발동 순서 sibling** — invariant fail → implementability assessment → §10 row reasoning_carryover 활용 (§결정 4). |
| ADR-058 (ADR sunset criteria mandate) | **`is_transitional: false` (governance permanent) 정합** — §결정 7 보안 ADR default presumption + governance default 동일 적용. sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 정합). |
| ADR-060 (Evidence-enforceable promotion framework) | **§결정 5 wording-ssot-grep-lint warning-tier 첫 적용** — 4번째 warning entry (auto-phase-label / forbid-list / adr-sunset-criteria 다음). schema v1.1 정합 (Amendment 2 / CFP-455). 승격 gate 3 AND condition. |
| ADR-063 (Marketplace atomic invariant) | **plugin.json + CHANGELOG + marketplace.json atomic coordination** — review-verdict-v4 v4.3 MINOR bump → plugin.json 5.34.0 MINOR bump → marketplace.json sync atomic. PR ordering: marketplace 선행 merge → wrapper Phase 1 PR. |
| ADR-064 (Decision principle mandate) | **normative anchor 정합** — 4 어휘 (best-effort / broad coverage / full-scope / active amendment) + forbid-list 8 어휘 lint. dual-binding (cross-lane enforce) = `broad coverage` / `full-scope` 직접 적용. |
| ADR-008 (Inter-plugin contract versioning) | **review-verdict-v4 v4.2 → v4.3 MINOR bump** — `boundary_completeness_self_check_passed: bool` optional field + `findings[].type: "boundary-completeness"` literal 추가. backward-compat 의무 (기존 v4.2 packet 모두 valid). |
| ADR-059 (Debate protocol v1) | **positive sibling** — dual-binding cross-validate divergence (DesignReview ↔ CodeReview) 시 `auto_on_divergence` 발동 surface 확장. CFP-530 (Wave 4) Amendment 1 정합. |

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (governance permanent — ADR-058 §결정 7 보안/governance default presumption 정합).

Amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 sunset_justification 차단):
- scope 확장 (4 → 5+ invariants 추가)
- 강도 강화 (warning-tier → blocking-on-pr 승격 별도 CFP)
- enforcement surface 확장 (design + code → security + test lane 확장 별도 CFP)

약화 방향 (4 invariants 축소 / dual-binding → single-binding 다운그레이드 / warning tier 자체 deprecate) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

## 결과

- ArchitectAgent Phase 1 commit 직전 self-check 2 boolean field (mechanical_self_check_passed + boundary_completeness_self_check_passed) 양 true 일 때만 진행
- DesignReviewPL + CodeReviewPL 4 invariants flag 검증 의무 (review-pl-base.md §3 갱신, Phase 2 sibling sync)
- review-verdict-v4 v4.3 schema MINOR bump (sibling sync 6 lane plugin mirror, ADR-010)
- wording-ssot-grep-lint warning-tier registry entry + lint script + workflow self-app (ADR-060 framework 4번째 entry)
- #438 자동 closure (CFP-527 Phase 2 PR `Closes #438` reference)
- MCT-150 baseline (boundary gap 4건 design-review PASS 후 code-review 발견) 대비 신규 Story 의 design-lane detection ratio ≥ 50% KPI (sunset gate 별도 CFP carrier)

## 관련 파일

- `CLAUDE.md` (ADR (`docs/adr/` SSOT) 단락 + Inter-plugin Contract 단락 ADR-068 cross-ref 추가)
- `docs/inter-plugin-contracts/review-verdict-v4.md` (v4.2 → v4.3 MINOR bump)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (review-verdict-v4 version row 갱신)
- `skills/review-responsibility/SKILL.md` (CodeReview lane row "4 invariants cross-validate" 추가)
- `docs/evidence-checks-registry.yaml` (`wording-ssot-grep-lint` warning-tier entry append)
- `scripts/check-wording-ssot.sh` (mechanical lint 신규)
- `templates/github-workflows/wording-ssot-check.yml` (workflow template 신규)
- `.github/workflows/wording-ssot-check.yml` (self-app byte-identical)
- `plugin-codeforge-review/templates/review-pl-base.md` (§3 4-invariant flag — Phase 2 sibling sync)
- `plugin-codeforge-design/templates/architect-agent-prompt.md` (self-check step — 4 invariants + ADR-065 7-item 분리 명시, Phase 2 sibling sync)
