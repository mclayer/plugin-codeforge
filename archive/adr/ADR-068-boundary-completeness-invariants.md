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
  - CFP-528
  - CFP-1086
  - CFP-1087
  - CFP-1565  # Amendment 5 carrier — 신규 I-7 chief-author cross-ADR scope/fact claim consistency invariant (CFP-1522 retro F-003 P1 evidence: ADR-113 §결정 6 `admin:repo` scope claim ↔ ADR-066 §결정 2 6-scope SSOT mismatch). I-4 wording SSOT 와 disjoint axis (I-4 = Story↔ADR↔impl identifier wording sync / I-7 = cross-ADR factual/scope claim consistency). 6 → 7 invariants ratchet 강화.
  - CFP-1059  # cross-ref only — ADR-087 §결정 5 `[empirical-source: TBD]` annotation 3개소 (healthcheck window / graceful drain / retention period) + ADR-042 Amendment 9 4 신설 agent tier spawn count empirical grounding 가 I-5 dimensional empirical grounding 정합 (본 ADR-068 본문 정책 0건 변경)
  - CFP-1580  # Amendment 4 carrier — Wave 2 mechanical wire 영역 design review skip 정합 invariant codify (pattern_count 5 evidence: CFP-1489/1497/1500/1502/1539 5 precedent linear chain, escalation_resolved_carrier paired sibling ADR-045 §D-9 Amendment 7)
absorbed_issues:
  - 438
related_adrs:
  - ADR-008
  - ADR-042  # Amendment 8 cross-ref (CFP-1086 / Story-1 sibling carrier — 7+3+1 roster 재편, axis 분석 + 5-checklist self-application 첫 사례) + Amendment 9 cross-ref (CFP-1059 / Story-1 — 4 신설 agent tier spawn count empirical grounding [empirical-source: TBD] I-5 정합)
  - ADR-058
  - ADR-059
  - ADR-060
  - ADR-063
  - ADR-064
  - ADR-065
  - ADR-067
  - ADR-082  # I-5 directly-analogous pattern 재사용 backref (ADR-082 Amendment 1 scope (a) corpus-claim-verify lint, cross-ref only — I-5 본문 0건 변경, CFP-841)
  - ADR-086  # 신설 cross-ref (CFP-1086 / Story-1 — Deputy 신설 결정 framework P7, 본 Amendment 2 = tie-break ladder 3단계 §3 (chief judgement + ADR Amendment 발의) trigger 가 ADR-086 §결정 1 axis 분석 + §결정 2 5-checklist 의무 발동)
  - ADR-073  # I-6 verification primitive ↔ §결정 1 verify-before-assert primitive directly-analogous (CFP-1087 Amendment 3 cross-ref backref — ADR-073 본문 0건 변경)
  - ADR-087  # 신설 cross-ref (CFP-1059 / Story-1 — Deploy lane 신설, §결정 5 `[empirical-source: TBD]` annotation 3개소 = I-5 dimensional empirical grounding 정합 — healthcheck window / graceful drain / retention period)
  - ADR-088  # 신설 cross-ref (CFP-1059 / Story-1 — Deploy Review lane + ProductionEvidence transfer, 본 ADR-068 본문 정책 0건 변경)
  - ADR-066  # 신설 cross-ref (CFP-1565 Amendment 5 — I-7 evidence source: ADR-066 §결정 2 PAT 6-scope SSOT 가 ADR-113 §결정 6 `admin:repo` scope claim 의 ground truth — cross-ADR scope claim consistency 위반 sentinel. 본 ADR-068 = I-7 invariant 신설, ADR-066 본문 0건 변경)
  - ADR-113  # 신설 cross-ref (CFP-1565 Amendment 5 — I-7 evidence source: ADR-113 §결정 6 admin merge preflight gate 의 PAT scope claim 이 ADR-066 SSOT 와 mismatch (chief 미 cross-check, CFP-1522 retro F-003 P1). 본 ADR-068 = I-7 invariant 신설, ADR-113 본문 0건 변경)
amendments:
  - amendment_id: 1
    cfp: CFP-528
    date: 2026-05-13
    scope: "신규 I-5 dimensional empirical grounding invariant 추가 — 10 dimension enum (latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count) 의 quantitative parameter 마다 `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 의무. empirical evidence 없는 default lock-in 차단 (anti-pattern 4종: empirical-absent default / synthetic guess / industry-assumption transplant / legacy inertia). Mitigation 4종 (empirical-first / explicit TBD / range-bound default / dimensional checklist) + Justification 면제 조건 (well-defined SLA / standardized protocol RFC / vendor doc explicit guarantee) + Exemption (SLA/quantitative metric 무관 trivial decision). Verification format = empirical-source-annotation 3-key (value / unit / empirical_source). review-verdict-v4 v4.3 → v4.4 MINOR — `dimensional_empirical_self_check_passed: bool` field + `findings[].type: \"dimensional-empirical-gap\"` literal. boundary completeness 4 invariants (I-1/I-2/I-3/I-4) → 5 invariants ratchet 강화. #319 (RETRO-MCT-104) absorb close (distinct failure-class but systemic super-class)."
    status: applied
    ref: "본문 I-5 declaration L88-L98"
    sunset_justification: "ratchet 강화 방향 (4 → 5 invariants, scope 축소 0건). I-1/I-2/I-3/I-4 본문 의미 변경 0건 — I-5 disjoint append only. is_transitional false 유지 (permanent governance). ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment)."
  - amendment_id: 2
    cfp: CFP-1086
    date: 2026-05-20
    scope: "wording SSOT 충돌 시 chief tie-break ladder 신설 (3 단계 순차: (1) RACI 매트릭스 lookup — deputy-mandate skill row → 명시된 R/A 가 있으면 그대로 / (2) ADR-068 invariant 적용 — I-1 API contract / I-2 cross-module / I-3 conditional guard / I-4 wording SSOT / I-5 dimensional empirical / (3) chief judgement + ADR Amendment carrier 발의 — RACI 미codify 영역만, ADR-086 §결정 1 axis 분석 + §결정 2 5-checklist self-app + 사용자 escalation 의무). I-4 wording SSOT invariant 강화 — 기존 I-4 = wording-impl identifier desync 검출 / 본 Amendment 2 = chief tie-break ladder mechanism codify (충돌 해소 절차). boundary_completeness_self_check_passed scope expansion — 본 ladder 3단계 모두 통과 시 true. BackendArchEpic CFP-1086 Story-1 sibling carrier (ADR-042 Amendment 8 + ADR-086 신설 atomic). ratchet 강화 방향 (4 → 5 invariants 후 5번째 I-4 mechanism codify 추가, scope 축소 0건). I-1/I-2/I-3/I-5 본문 의미 변경 0건 — Amendment 2 = I-4 mechanism 보강만."
    status: applied
    ref: "본문 Amendment 2 section + Implementation note (CFP-1086 Story-4 carrier — chief author body cross-ref binding)"
    sunset_justification: "ratchet 강화 방향 (I-4 mechanism codify 추가, 약화 0건). I-1/I-2/I-3/I-5 본문 의미 변경 0건. is_transitional false 유지 (permanent governance). ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment). Amendment 1 (CFP-528 / I-5) 의 ratchet 패턴 (5 → 5 invariants + mechanism boost) 답습."
  - amendment_id: 3
    cfp: CFP-1087
    date: 2026-05-20
    scope: "신규 I-6 audit-gate-pointer-existence invariant 추가 — codeforge-review canonical templates/review-pl-base.md §8.6 audit gate finding 영역 pointer 부재 detection 영역 mechanical existence verify 의무. Verification format = existence-verify-annotation 4-key (link target 실재 / section anchor resolvable / file path reference 실재 / ADR §결정 N reference 정확) — semantic content verify 영역 제외 (boundary-completeness I-1/I-2 영역과 disjoint axis). Trigger = §8.6 audit gate finding 발화 시 pointer 부재 detect → audit_gate_pointer_self_check_passed false + findings[].type 'audit-gate-pointer-missing' literal emit. Mitigation = pointer 명시적 declare (4-form 중 1+). review-verdict-v4 v4.6 → v4.7 MINOR — `audit_gate_pointer_self_check_passed: bool` field + `findings[].type: 'audit-gate-pointer-missing'` literal. boundary completeness 5 invariants (I-1~I-5) → 6 invariants ratchet 강화 (Amendment 2 mechanism codify 영역 invariants count 5 retain 후 본 Amendment 3 I-6 신설). CFP-528 Amendment 1 (I-5 declaration) precedent verbatim 답습 — pattern cost 최소. CFP-698 retro Wave 2-1 HIGH carrier (sibling: CFP-1088 IntegrationTest §7.4 disjoint, CFP-1089 mechanical workflow Wave-2 enforcement). collision resolution — main #1095 merged CFP-1086 Amendment 2 sequential precedence acquire 후 본 carrier renumber Amendment 3 + v4.7 + 5.99.0."
    status: applied
    ref: "본문 §결정 1 I-6 declaration + §결정 3 표 4번째 row + §결정 6 표 4번째 row + Amendment 3 section"
    sunset_justification: "ratchet 강화 방향 (5 → 6 invariants, scope 축소 0건). I-1/I-2/I-3/I-4/I-5 본문 의미 변경 0건 — I-6 disjoint append only (audit gate pointer existence axis 분리). is_transitional false 유지 (permanent governance). ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment). Amendment 1 (CFP-528 / I-5) pattern verbatim 답습. retroactive 면제 (Amendment 3 발효 후 신규 finding 한정)."
  - amendment_id: 4
    cfp: CFP-1580
    date: 2026-05-25
    scope: "신규 §결정 7 추가 — Wave 2 mechanical wire 영역 design review skip 정합 invariant codify (declarative anchor only). Wave 2 mechanical wire 정의 = Wave 1 declarative anchor active state + scripts/workflow/bats implementation only (Wave 1 declarative or 신규 ADR/governance 영역과 disjoint). spawn 결정 invariant: Wave 2 mechanical wire 영역에서 DesignReviewPL spawn = optional (skip default), Wave 1 declarative or 신규 ADR/governance 영역 = mandatory. 근거 = ArchitectAgent §13 4-tuple self-check (ADR-068 I-1~I-6 6 invariants semantic + ADR-065 10-item mechanical sync syntactic + ADR-082 §결정 11.A bats RED→GREEN stash proof + chief tie-break ladder 3-단계 Amendment 2 chief author commit-time forcing function) + bats RED→GREEN stash proof + CodeReviewPL mechanical correctness review (스크립트 동작 / lint exit code / TDD coverage retain) = DesignReviewPL semantic review 대체 sufficient (Wave 2 mechanical wire 영역 한정). 5 precedent CFP linear chain evidence base (CFP-1489 1-E spawn-time SHA pin Wave 2-A / CFP-1497 1-G amendment-slot reservation Wave 2-C / CFP-1500 1-F mid-spawn drift Wave 2-B / CFP-1502 1-D chief author span Wave 2-D / CFP-1539 1-I pre-spawn-prompt-finalize Wave 2-E — all Wave 1 declarative anchor active 후 Wave 2 mechanical wire 영역에서 DesignReviewPL spawn 0 + 0 design FIX + 0 design review divergence detection + wrapper-self CodeReviewPL PASS + admin squash merge) reach pattern_count 5 ≫ ADR-045 §D-9 threshold 2 = Mandatory escalation 산물 (PMOAgent CFP-1539+1540 batch retro §6 escalate_user → 사용자 Option A confirmed compress normative codify 2026-05-25 KST). DeveloperPL spawn prompt 안 declarative anchor field `wave2_mechanical_wire_dr_skip_applicable: bool` declare (declarative anchor only, 실 wire DeveloperPLAgent agent file 변경 / spawn prompt template 변경 / workflow lint = 별 sub-CFP carrier Wave 2 mechanical enforcement). boundary completeness 6 invariants (I-1~I-6) 본문 의미 변경 0건 — §결정 7 = spawn 결정 invariant codify (orthogonal axis: spawn-time orchestration governance, invariants axis: write-time verification semantic). Amendment 1 (CFP-528 I-5) + Amendment 2 (CFP-1086 chief tie-break ladder) + Amendment 3 (CFP-1087 I-6 audit-gate-pointer) precedent verbatim 답습 (ratchet 강화 방향, invariants count 6 retain — mechanism codify + spawn 결정 invariant 추가, scope 축소 0). review-verdict-v4 schema 변경 0건 (declarative anchor only) — sibling sync 면제. paired sibling ADR-045 §D-9 Amendment 7 (CFP-1580, evidence-only Amendment, pattern_count 5 escalation_resolved_carrier 본 CFP declare — Amendment 6 CFP-776 ADR-082 forcing function 산물 evidence-only Amendment pattern 답습). doc-only fast-path ADR-054 (src/tests 무변경)."
    status: applied
    ref: "본문 §결정 7 declaration + Amendment 4 section + 변경이력 entry"
    sunset_justification: "ratchet 강화 방향 (Wave 2 mechanical wire 영역 skip default codify + Wave 1 영역 mandatory retain invariant 강화 boundary 명확화, scope 축소 아님). I-1/I-2/I-3/I-4/I-5/I-6 본문 의미 변경 0건 — §결정 7 = orthogonal axis (spawn-time orchestration governance) append only, invariants axis (write-time verification semantic) 영역 외. is_transitional false 유지 (permanent governance). ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment). Amendment 1/2/3 precedent verbatim 답습. retroactive 면제 (Amendment 4 발효 후 신규 Wave 2 mechanical wire PR 한정 — 5 precedent CFP-1489/1497/1500/1502/1539 = process retroactive ratification declarative only, 새 mechanical enforcement 0건)."
  - amendment_id: 5
    cfp: CFP-1565
    date: 2026-06-01
    scope: "신규 I-7 chief-author cross-ADR scope/fact claim consistency invariant 추가 — chief author 가 ADR/doc 본문에서 다른 ADR 의 SSOT 값 (scope list / count / enum / 권한 범위 등) 을 인용·단언할 때, 인용 시점에 대상 ADR 의 실제 SSOT 를 직접 Read-verify 후 대조할 의무. 미검증 cross-ADR scope claim = ADR 간 경계 사실 불일치 = boundary completeness gap. Trigger = chief author §3/§7/§10/§11 작성 시 cross-ADR scope/fact claim (다른 ADR §결정 N 의 list/count/enum/scope) 인용 발화 → 대상 ADR direct Read-verify 누락 detect. Mitigation = claim 별 cited_adr + §결정 N + cited_value + verify_status annotation 명시 + commit 직전 target ADR direct Read 대조. Justification 조건 (annotation 면제): self-ref (동일 ADR 안 §결정 cross-ref) / well-known stable constant (변경 빈도 0 영역). Exemption: cross-ADR scope/fact claim 0건 Story = scope 외 (Story §1 명시 선언). Verification format = cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status). review-verdict-v4 v4.11 → v4.12 MINOR — `chief_author_crossref_consistency_self_check_passed: bool` 7번째 verdict-level optional field + `findings[].type: \"chief-author-crossref-inconsistency\"` 11번째 enum literal. DesignReviewPL + CodeReviewPL dual cross-validate (I-1~I-6 패턴 답습). I-4 wording SSOT 와 disjoint axis (I-4 = Story↔ADR↔impl identifier wording sync / I-7 = cross-ADR factual/scope claim consistency). boundary completeness 6 invariants (I-1~I-6) → 7 invariants ratchet 강화. CFP-1522 retro F-003 P1 evidence (ADR-113 §결정 6 `admin:repo` scope claim ↔ ADR-066 §결정 2 6-scope SSOT mismatch, chief 미 cross-check)."
    status: applied
    ref: "본문 §결정 1 I-7 declaration + §결정 2 Tier A/B/C I-7 row + §결정 6 표 4번째 row + Amendment 5 section + 변경이력 entry"
    sunset_justification: "N/A — ratchet 강화 방향 (6 → 7 invariants, scope 축소 0건). I-1/I-2/I-3/I-4/I-5/I-6 본문 의미 변경 0건 — I-7 disjoint append only (cross-ADR factual/scope claim consistency axis 분리, I-4 wording SSOT 와 별 axis). is_transitional false 유지 (permanent governance). ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합 (강화 방향만 amendment). Amendment 1 (CFP-528 I-5) + Amendment 3 (CFP-1087 I-6) invariant 신설 precedent verbatim 답습. retroactive 면제 (Amendment 5 발효 후 신규 cross-ADR scope claim 발화 한정)."
mechanical_enforcement_actions:
  - action: boundary-completeness-self-check
    status: deferred-followup
    progress_note: "ADR-068 신설 시점 registry entry 부재 (verdict field-only enforcement). blocking-on-pr 승격 후보 — 별도 CFP 가 evidence-checks-registry append + verdict field-time lint 신설 후 status 갱신 (deferred-followup → warning → blocking-on-pr)."
    target_section: §결정 2
  - action: wording-ssot-grep-lint
    status: warning
    progress_note: "ADR-060 framework 4번째 warning entry — schema v1.2 (CFP-509 / ADR-060 Amendment 6). hotfix-bypass:boundary-wording label. 첫 20 PR sample 측정 후 blocking-on-pr 승격 별도 CFP."
    target_section: §결정 5
  - action: dimensional-empirical-grounding
    status: deferred-followup
    progress_note: "ADR-068 Amendment 1 (CFP-528) 신설 시점 — verdict field-only enforcement (`dimensional_empirical_self_check_passed: bool`). registry entry 부재. blocking-on-pr 승격 후보 — 별도 CFP 가 evidence-checks-registry append + verdict field-time lint 신설 후 status 갱신 (deferred-followup → warning → blocking-on-pr)."
    target_section: §결정 1
  - action: audit-gate-pointer-existence-check
    status: deferred-followup
    progress_note: "ADR-068 Amendment 3 (CFP-1087) 신설 시점 — verdict field-only enforcement (`audit_gate_pointer_self_check_passed: bool` + `findings[].type: 'audit-gate-pointer-missing'`). registry entry 부재. blocking-on-pr 승격 후보 — 별도 CFP CFP-1089 (Wave-2 mechanical wire enforcement) carrier 가 evidence-checks-registry append + scripts/check-audit-gate-pointer.sh + workflow yml 신설 후 status 갱신."
    target_section: §결정 1
  - action: chief-author-crossref-consistency-check
    status: deferred-followup
    progress_note: "ADR-068 Amendment 5 (CFP-1565) 신설 시점 — Wave 1 declaration-only (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습). verdict field-only enforcement (`chief_author_crossref_consistency_self_check_passed: bool` + `findings[].type: 'chief-author-crossref-inconsistency'`). evidence-checks-registry entry `chief-author-crossref-consistency` (status deferred-followup, bypass_label hotfix-bypass:boundary-wording 재사용 — ADR-068 owner family). 실 mechanical wire (scripts/check-chief-author-crossref-consistency.sh + scripts/lib + workflow yml + bats fixture) = 별 sub-CFP Wave 2 carrier. blocking-on-pr 승격 후보 — pattern_count >= 2 재발 시 follow-up CFP MUST promote (ADR-082 §결정 6 정합)."
    target_section: §결정 1
---

# ADR-068: Boundary completeness invariants (semantic dual-binding)

## 상태

`Accepted` (2026-05-13). ADR-065 (mechanical syntactic 7-item self-check) 의 semantic 상위 개념. 분리 운영 — verdict packet 양 별도 boolean field emit.

## 컨텍스트

mctrader-hub MCT-150 Phase 2 case study (Epic CFP-525 brainstorm spec L17) — design-review PASS 후 code-review 에서 **반복 발견된 boundary completeness gap 4회** (양 reviewer independent identification). 4 gap 의 type 별도 분류:

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
- 정의: module A method 가 status enum 을 반환할 때, 호출 site (module B/C) 가 enum 별도 분기 처리 의무. 미처리 enum 값 = silent pass-through = caller gap.
- Verification format: **propagation-matrix** — Story §7 본문 또는 ADR §결정 표에 enum 별도 caller-side 분기 매핑 (row: enum value × column: caller module × cell: handling logic 요약). 미처리 enum × caller pair 부재 의무.

**I-3: Unconditional vs conditional guard placement intent**
- 정의: invariant guard (assertion / pre-condition / post-condition) 의 위치가 "함수 진입 시점 무조건" 인지 "특정 path 한정" 인지 ADR 본문에 명시 의무. caller 가 guard 위치 가정 오류 = re-fix.
- Verification format: **guard-placement-diagram** — Story §7 또는 ADR §결정 본문에 guard 별도 (a) placement (function entry / branch entry / loop body / cleanup path 등) + (b) condition (unconditional / conditional with predicate) + (c) failure mode (assertion error / state transition / log + continue) 3-key 명시.

**I-4: Wording SSOT**
- 정의: Story 본문 (§3 결정 / §7 아키텍처) ↔ ADR ↔ impl (enum identifier / method name / docstring noun phrase) 양 방향 wording 동기화 의무. 13곳 desync (MCT-150 evidence) baseline.
- Verification format: **wording-sync-table** — Story §3/§7 의 enum identifier (UPPER_SNAKE_CASE) + method name (camelCase / snake_case) + 핵심 noun phrase (Korean 또는 English) 목록과 ADR 본문 + impl source identifier 의 매칭 표. mechanical 영역 (enum/method identifier) = `scripts/check-wording-ssot.sh` lint (§결정 5). semantic phrase 영역 = DesignReview manual flag.

**I-5: Dimensional empirical grounding (Amendment 1 — CFP-528, 2026-05-13)**
- 정의: §3 / §7 의 quantitative parameter (10 dimension enum: latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count) 마다 `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 의무. empirical evidence 없는 default lock-in 차단.
- Trigger 4종 (anti-pattern entry condition):
  1. **empirical-absent default** — wiretap/probe 없이 가정값 채택 (#319 RETRO-MCT-104 carrier: WS push interval 30s 가정 → 실측 200ms, 150x 오류)
  2. **synthetic guess** — "통상 1MB" / "보통 100rps" round-number heuristic
  3. **industry-assumption transplant** — "AWS p99 latency" / "PG max_connections 100" 컨텍스트 무관 import
  4. **legacy inertia** — 이전 시스템 값 무비판 복제
- Mitigation 4종: empirical-first (wiretap/probe step 의무화) / explicit TBD 기재 (`[empirical-source: TBD]` marker) / range-bound default (단일 numeric 대신 `[min, max] with fallback strategy`) / dimensional checklist (per-dimension `empirical_source` field)
- Justification 조건 (annotation 면제): well-defined SLA / standardized protocol RFC / vendor doc explicit guarantee — 3종 부재 시 annotation 의무
- Exemption (trivial decision): SLA/quantitative metric 무관 (logging / naming / refactoring) — Story §1 명시 선언 의무
- Verification format: **empirical-source-annotation** — quantitative parameter 별도 (a) value (b) unit (c) empirical_source (file path / wiretap script / ADR ref / TBD) 3-key 정합

**I-6: Audit-gate-pointer-existence (Amendment 3 — CFP-1087, 2026-05-20)**
- 정의: codeforge-review canonical `templates/review-pl-base.md` §8.6 audit gate finding 영역의 pointer 부재 detection 영역. ArchitectAgent §3 / §7 / §11 작성 시 audit gate finding 발화 시점에 pointer scope 4-form 중 1+ existence verify 의무. pointer 부재 = mechanical detect 가능 영역 (semantic content verify 영역과 disjoint axis).
- 4-form pointer scope: (a) **link target** — markdown `[text](url)` 형식의 url 부분 file path / cross-repo URL 실재 verify / (b) **section anchor** — `#section-id` 영역 target file 안 heading 존재 verify / (c) **file path reference** — bare file path string (예: `docs/adr/ADR-068.md`) 실재 verify / (d) **ADR §결정 N reference** — `ADR-NNN §결정 M` 영역 target ADR 본문 §결정 M 실재 verify
- Trigger: §8.6 audit gate finding 발화 시 pointer scope 4-form 중 1+ existence verify FAIL detect → audit_gate_pointer_self_check_passed false emit + findings[].type "audit-gate-pointer-missing" literal 동반 emit
- Mitigation: pointer 명시적 declare (4-form 중 1+ scope choose) + existence pre-verify (commit 직전 `Read` / `Glob` / `gh api` direct verify, ADR-073 §결정 1 verify-before-assert primitive directly-analogous)
- Justification 조건: §8.6 audit gate finding 외 영역 = scope 외 (본 invariant 적용 0)
- Exemption: pointer placeholder 의도적 미decode 영역 (예: `<TBD>` / `<future-carrier>`) — Story §1 명시 선언 + `[verification-out-of-scope: <사유>]` annotation
- Verification format: **existence-verify-annotation** — pointer 별 (a) form (link target / section anchor / file path reference / ADR §결정 N reference 4-enum 중 1) (b) target (resolved value 또는 placeholder) (c) verify_status (verified / pending / out-of-scope) 3-key 정합. boundary-completeness I-1/I-2 semantic content verify 영역과 disjoint axis — dedup 비교차 (same anchor_id 양 literal 후보 충돌 회피, debate-protocol-v1 auto_on_divergence 오발동 차단)

**I-7: Chief-author cross-ADR scope/fact claim consistency (Amendment 5 — CFP-1565, 2026-06-01)**
- 정의: chief author 가 ADR / doc 본문에서 다른 ADR 의 SSOT 값 (scope list / count / enum / 권한 범위 등) 을 인용·단언할 때, 인용 시점에 대상 ADR 의 실제 SSOT 를 직접 Read-verify 후 대조할 의무. 미검증 cross-ADR scope claim = ADR 간 경계 사실 불일치 = boundary completeness gap. I-6 (audit-gate-pointer existence) 가 pointer 의 **실재** verify 라면, I-7 = cross-ADR 인용 **값** 의 SSOT 정합 verify.
- Trigger: chief author §3 / §7 / §10 / §11 작성 시 cross-ADR scope/fact claim (다른 ADR §결정 N 의 list / count / enum / scope 값) 인용 발화 시점에 대상 ADR direct Read-verify 누락 detect → chief_author_crossref_consistency_self_check_passed false emit + findings[].type "chief-author-crossref-inconsistency" literal 동반 emit
- Mitigation: claim 별 명시적 annotation (cited_adr + §결정 N / cited_value / verify_status) + commit 직전 target ADR direct `Read` 대조 (ADR-073 §결정 1 verify-before-assert primitive directly-analogous, source-of-truth direct fetch)
- Justification 조건 (annotation 면제): self-ref (동일 ADR 안 §결정 cross-ref) / well-known stable constant (변경 빈도 0 영역, 예: SemVer MAJOR/MINOR/PATCH 정의)
- Exemption: cross-ADR scope/fact claim 0건 Story = scope 외 (Story §1 명시 선언) — 본 invariant 적용 0
- Verification format: **cross-adr-claim-verify-annotation** — cross-ADR claim 별 (a) cited_adr (`ADR-NNN §결정 N` 형식) (b) cited_value (인용한 list / count / enum / scope 값 verbatim) (c) verify_status (verified — target ADR direct Read 대조 완료 / pending — 미대조 / out-of-scope — Justification 면제) 3-key 정합. I-4 wording SSOT (Story↔ADR↔impl identifier wording sync) 와 **disjoint axis** — I-4 = identifier 표기 동기화 / I-7 = cross-ADR factual/scope **값** 의 SSOT 정합. dedup 비교차 (same anchor_id 양 literal 후보 충돌 회피, debate-protocol-v1 auto_on_divergence 오발동 차단)

### 결정 2 — Dual-binding (design lane authoring + code-review cross-validate)

3-tier enforcement:

**Tier A (authoring-time)**: ArchitectAgent prompt 의무
- §3 / §7 작성 시 4 invariants 별도 verification format self-check 수행
- verdict packet `boundary_completeness_self_check_passed: bool` emit (review-verdict-v4 v4.3 optional field)
- 4 invariants 모두 PASS 일 때만 true emit. 1+ FAIL 시 false emit + `findings[]` 에 미통과 invariant 별도 evidence 동반 (`findings[].type: "boundary-completeness"`)
- I-5 (Amendment 1, CFP-528) self-check 수행 시 `dimensional_empirical_self_check_passed: bool` 별도 field emit (review-verdict-v4 v4.4 optional field). 10 dimension enum 의 모든 quantitative parameter 가 `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 보유 시 true. 1+ 누락 시 false + `findings[].type: "dimensional-empirical-gap"` 동반.
- I-7 (Amendment 5, CFP-1565) self-check 수행 시 `chief_author_crossref_consistency_self_check_passed: bool` 별도 field emit (review-verdict-v4 v4.12 optional field). §3/§7/§10/§11 의 모든 cross-ADR scope/fact claim 이 cross-adr-claim-verify-annotation 3-key 보유 + verify_status=verified (또는 Justification 면제 out-of-scope) 시 true. 1+ pending/미검증 시 false + `findings[].type: "chief-author-crossref-inconsistency"` 동반.

**Tier B (design-review-time)**: DesignReviewPL 의무
- review-pl-base.md §3 의 4 invariants flag 항목 검증 의무
- design lane perspective — ArchitectAgent §3/§7 의 verification format 누락 발견 시 finding emit
- `findings[].type: "boundary-completeness"` literal + severity P0~P3
- I-5 (Amendment 1) cross-validate: DesignReviewPL `findings[].type: "dimensional-empirical-gap"` literal 로 I-5 위반 flag.
- I-7 (Amendment 5) cross-validate: DesignReviewPL `findings[].type: "chief-author-crossref-inconsistency"` literal 로 I-7 위반 flag — 설계 문서 감사 관점 (ADR/doc 본문의 cross-ADR scope claim ↔ 대상 ADR SSOT 대조 누락 발견 시 emit).

**Tier C (code-review-time)**: CodeReviewPL 의무 (cross-validate)
- review-pl-base.md §3 동일 4 invariants flag 항목 검증 의무
- code lane perspective — impl ↔ ADR ↔ Story 매핑 검증. impl docstring 누락 / caller enum 분기 미처리 / impl guard 위치 mismatch / impl identifier wording desync 시 finding emit
- 동일 `findings[].type: "boundary-completeness"` literal + severity P0~P3
- dedup: 같은 `anchor_id` 양 lane finding 시 severity 높은 쪽 채택 (skills/review-responsibility/SKILL.md)
- I-5 (Amendment 1) cross-validate: CodeReviewPL `findings[].type: "dimensional-empirical-gap"` literal 로 I-5 위반 flag (impl 의 quantitative parameter empirical-source annotation 누락 검출).
- I-7 (Amendment 5) cross-validate: CodeReviewPL `findings[].type: "chief-author-crossref-inconsistency"` literal 로 I-7 위반 flag — 구현 cross-validate 관점 (impl / doc 안 다른 ADR 의 scope/enum/count 인용 값이 대상 ADR SSOT 와 mismatch 검출 시 emit).

Cross-validate divergence (DesignReview = PASS, CodeReview = FIX 또는 vice versa) 시 = debate-protocol-v1 `auto_on_divergence` 발동 surface (ADR-059). CFP-530 (Wave 4) Amendment 1 positive sibling.

### 결정 3 — ADR-065 와의 분리 운영 근거 + #438 absorption

ADR-065 (mechanical syntactic 7-item) 와 본 ADR-068 (semantic 4-invariant) 분리 운영. 동일 ArchitectAgent verdict packet 의 **두 별도 boolean field** emit:

| Field | Owner ADR | Scope | Verification method |
|---|---|---|---|
| `mechanical_self_check_passed` | ADR-065 | Syntactic 7-item (file path / link target / version / cross-ref / label registry / doc location / workflow self-app) | mechanical grep / regex / file Read |
| `boundary_completeness_self_check_passed` | ADR-068 (본) | Semantic 4-invariant (I-1~I-4: API contract / propagation / guard placement / wording SSOT) | LLM judgment + cross-lane validation |
| `dimensional_empirical_self_check_passed` | ADR-068 Amendment 1 (CFP-528) | Semantic dimensional grounding (I-5: 10 dimension enum 의 quantitative parameter empirical-source annotation) | LLM judgment + cross-lane validation (annotation 부재 검출) |

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

- **Registry entry**: `wording-ssot-grep-lint` (`docs/evidence-checks-registry.yaml`, schema v1.2)
  - `owner_adr`: ADR-068
  - `carrier_adr`: ADR-060
  - `current_tier`: warning
  - `status`: Active
  - `hotfix_bypass_label`: `hotfix-bypass:boundary-wording` (ADR-024 Amendment 3 per-entry namespace 정합)
  - `promotion_gate`: PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged → blocking-on-pr 승격 (별도 CFP, Wave 2A 직접 scope 외)
  - `introduced_in`: CFP-527
  - schema v1.2 정합 (CFP-509 / ADR-060 Amendment 6) — `recurrence` field 신설 정합
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

### 결정 7 — Wave 2 mechanical wire 영역 design review skip 정합 invariant (Amendment 4 — CFP-1580, 2026-05-25)

ArchitectAgent §13 4-tuple self-check 의 Wave 2 mechanical wire 영역 적용 보장 = DesignReviewPL 대체 sufficient 근거 codify. spawn 결정 invariant 영역 (orthogonal axis with §결정 1 invariants — write-time verification semantic 영역 외).

#### 7.1 Wave 1 vs Wave 2 boundary 정의

| Phase | 정의 | DesignReviewPL spawn |
|---|---|---|
| **Wave 1 declarative anchor** | ADR / inter-plugin contract / CLAUDE.md / playbook / skill SSOT codify Phase (governance permanent layer 변경) | **mandatory retain** (skip 0건 invariant) |
| **Wave 2 mechanical wire** | Wave 1 declarative anchor active state + `scripts/*.{sh,py}` + `templates/github-workflows/*.yml` + `.github/workflows/` self-app + `tests/scripts/*.bats` + `docs/evidence-checks-registry.yaml` entry append + `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump (mechanical enforcement implementation only) | **optional (skip default)** — 본 §결정 7 codify 영역 |

신규 ADR/governance 영역 (예: 새 §결정 신설 / forbid-list 확장 / scope 확장 / 정책 본문 변경) = Wave 1 declarative anchor 영역 (mandatory retain).

#### 7.2 spawn 결정 invariant

**Wave 2 mechanical wire PR 영역** (boundary 7.1 표 Wave 2 column 정합):

- DesignReviewPL spawn = **optional (skip default)**
- ArchitectAgent §13 4-tuple self-check (ADR-068 I-1~I-6 + ADR-065 10-item mechanical sync, Amendment 5 11th post-write actual-run verify) + bats RED→GREEN stash proof (ADR-082 §결정 11.A) = chief author commit-time forcing function 충분
- CodeReviewPL mechanical correctness review **retain** (스크립트 동작 / lint exit code / TDD coverage / file path resolvability) — DesignReviewPL skip 과 별개 axis (orthogonal)
- DeveloperPL spawn prompt 안 declarative anchor field `wave2_mechanical_wire_dr_skip_applicable: bool` self-declare 의무 (declarative anchor only — 실 wire = 별 sub-CFP carrier Wave 2 mechanical enforcement)

**Wave 1 declarative anchor or 신규 ADR/governance 영역 PR**:

- DesignReviewPL spawn = **mandatory retain** (invariant 보존)
- skip 0건 invariant 강화 (Wave 1 영역 mandatory retain 명확화 = scope 축소 아님, mechanism codify = boundary 명확화 강화 방향)

#### 7.3 5 precedent CFP linear chain evidence base

| # | CFP | sub-scope | Wave 1 anchor | Wave 2 wire | DesignReviewPL spawn |
|---|---|---|---|---|---|
| 1 | CFP-1489 | 1-E pre-spawn HEAD-pin | CFP-1437 (Amd 15) | merged | 0 |
| 2 | CFP-1497 | 1-G amendment-slot pre-reservation | CFP-1435 (Amd 17) | merged | 0 |
| 3 | CFP-1500 | 1-F mid-spawn drift | CFP-1436 (Amd 16) | merged | 0 |
| 4 | CFP-1502 | 1-D chief author span | CFP-1438 (Amd 18) | merged | 0 |
| 5 | CFP-1539 | 1-I pre-spawn-prompt-finalize | CFP-FU-A (Amd 19) | merged | 0 |

5 Story 모두 wrapper-self CodeReviewPL PASS + admin squash merge — 0 design FIX, 0 design review divergence detection. pattern_count 5 ≫ ADR-045 §D-9 threshold 2 = Mandatory escalation → PMOAgent CFP-1539+1540 batch retro §6 escalate_user → 사용자 Option A confirmed (compress normative codify) 2026-05-25 KST → 본 §결정 7 codify 산물.

#### 7.4 retroactive 면제 + process compression 정상화

- 5 precedent CFP-1489/1497/1500/1502/1539 = process retroactive ratification declarative only (새 mechanical enforcement 0건)
- bypass-as-norm-mutation 위험 (ADR-024 Amendment 8 cross-ref) — 명시적 invariant 없이 5x 반복 → implicit norm 형성 → governance drift 위험. 본 §결정 7 = explicit invariant 확립 → audit trail 보장
- ADR-064 §결정 7 self-application top-down ratchet 정합 (강화 방향만, scope 축소 아님 — Wave 2 mechanical wire 영역만 skip default, Wave 1 mandatory retain)

#### 7.5 review-verdict-v4 schema 변경 0건 (declarative anchor only)

본 §결정 7 = declarative anchor only — review-verdict-v4 schema bump 0건 (sibling sync 면제, ADR-008 §결정 정합). `boundary_completeness_self_check_passed` / `mechanical_self_check_passed` / `dimensional_empirical_self_check_passed` / `audit_gate_pointer_self_check_passed` 4 field 보존 (Amendment 4 = scope expansion 아니라 spawn 결정 invariant codify orthogonal axis).

DeveloperPL spawn prompt schema 확장 (`wave2_mechanical_wire_dr_skip_applicable: bool` field 실 wire) = 별 sub-CFP carrier (declarative anchor only).

### 결정 6 — Mechanical enforcement actions binding

frontmatter `mechanical_enforcement_actions[]` 2 entry — ADR-040 Amendment 3 §결정 7.A (CFP-531 FIX iter 1 정정 후 schema) list[object] verbatim 정합:

| Action | Status | Target section | Evidence check / registry binding |
|---|---|---|---|
| `boundary-completeness-self-check` | `deferred-followup` | §결정 2 (3-tier dual-binding) | verdict field `boundary_completeness_self_check_passed: bool` (review-verdict-v4 v4.3) + DesignReview/CodeReview `findings[].type: "boundary-completeness"`. ADR-068 신설 시점 registry entry 부재 — verdict field-only enforcement. blocking-on-pr 승격 별도 CFP 가 (a) `docs/evidence-checks-registry.yaml` row append + (b) verdict field-time lint 신설 후 status 갱신 (deferred-followup → warning → blocking-on-pr). |
| `wording-ssot-grep-lint` | `warning` | §결정 5 (warning-tier evidence-enforceable) | `docs/evidence-checks-registry.yaml` entry (schema v1.2, current_tier: warning) + `scripts/check-wording-ssot.sh` + `.github/workflows/wording-ssot-check.yml`. 첫 20 PR sample 측정 후 blocking-on-pr 승격 별도 CFP. |
| `dimensional-empirical-grounding` | `deferred-followup` | §결정 1 (I-5 신설) | verdict field `dimensional_empirical_self_check_passed: bool` (review-verdict-v4 v4.4) + DesignReview/CodeReview `findings[].type: "dimensional-empirical-gap"`. ADR-068 Amendment 1 신설 시점 registry entry 부재 — verdict field-only enforcement. blocking-on-pr 승격 별도 CFP 가 (a) `docs/evidence-checks-registry.yaml` row append + (b) verdict field-time lint 신설 후 status 갱신. |
| `chief-author-crossref-consistency-check` | `deferred-followup` | §결정 1 (I-7 신설, Amendment 5) | verdict field `chief_author_crossref_consistency_self_check_passed: bool` (review-verdict-v4 v4.12) + DesignReview/CodeReview `findings[].type: "chief-author-crossref-inconsistency"`. ADR-068 Amendment 5 신설 시점 Wave 1 declaration-only — evidence-checks-registry entry `chief-author-crossref-consistency` (status deferred-followup, bypass_label `hotfix-bypass:boundary-wording` 재사용 — ADR-068 owner family). 실 mechanical wire (scripts/check-chief-author-crossref-consistency.sh + scripts/lib + workflow yml + bats) = 별 sub-CFP Wave 2 carrier. pattern_count >= 2 재발 시 follow-up CFP MUST promote (ADR-082 §결정 6 정합). |

Schema verbatim (ADR-040 §결정 7.A CFP-531 정정 후 + CFP-427 progress_note optional 신설):
- `action` (required) = evidence-check-registry entry name (또는 deferred-followup carrier action name)
- `status` (required) = warning / enforcing / deferred-followup enum 중 1
- `progress_note` (optional) = entry-level 진척 / carrier history free-form string
- `target_section` (required) = 본 ADR 본문 §결정 N reference

본 ADR-068 frontmatter `mechanical_enforcement_actions[]` 5 entry 모두 4 field 보유 (Amendment 1 `dimensional-empirical-grounding` + Amendment 3 `audit-gate-pointer-existence-check` + Amendment 5 `chief-author-crossref-consistency-check` 포함).

## 관련 ADR

| ADR | 관계 |
|---|---|
| ADR-065 (ArchitectAgent Phase 1 mechanical sync self-check) | **분리 운영 base** — syntactic 7-item carrier. 본 ADR-068 = semantic 4-invariant. 동일 ArchitectAgent verdict packet 양 별도 boolean field. ADR-065 계속 active (sunset 불필요), #438 ADR-065 구현 일부로 포섭. |
| ADR-067 (Fix-ledger implementability escalation, Wave 1) | **EC-2 동시 발동 순서 sibling** — invariant fail → implementability assessment → §10 row reasoning_carryover 활용 (§결정 4). |
| ADR-058 (ADR sunset criteria mandate) | **`is_transitional: false` (governance permanent) 정합** — §결정 7 보안 ADR default presumption + governance default 동일 적용. sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 정합). |
| ADR-060 (Evidence-enforceable promotion framework) | **§결정 5 wording-ssot-grep-lint warning-tier 첫 적용** — 4번째 warning entry (auto-phase-label / forbid-list / adr-sunset-criteria 다음). schema v1.2 정합 (Amendment 6 / CFP-509, recurrence field 정식 도입 — v1.1 Amendment 2 / CFP-455 의 current_tier required 확장). 승격 gate 3 AND condition. |
| ADR-063 (Marketplace atomic invariant) | **plugin.json + CHANGELOG + marketplace.json atomic coordination** — review-verdict-v4 v4.3 MINOR bump → plugin.json 5.34.0 MINOR bump → marketplace.json sync atomic. PR ordering: marketplace 선행 merge → wrapper Phase 1 PR. |
| ADR-064 (Decision principle mandate) | **normative anchor 정합** — 4 어휘 (best-effort / broad coverage / full-scope / active amendment) + forbid-list 8 어휘 lint. dual-binding (cross-lane enforce) = `broad coverage` / `full-scope` 직접 적용. |
| ADR-008 (Inter-plugin contract versioning) | **review-verdict-v4 v4.2 → v4.3 MINOR bump** — `boundary_completeness_self_check_passed: bool` optional field + `findings[].type: "boundary-completeness"` literal 추가. backward-compat 의무 (기존 v4.2 packet 모두 valid). Amendment 1 (CFP-528, 2026-05-13) 가 v4.3 → v4.4 MINOR bump (`dimensional_empirical_self_check_passed: bool` + `findings[].type: "dimensional-empirical-gap"`). |
| ADR-059 (Debate protocol v1) | **positive sibling** — dual-binding cross-validate divergence (DesignReview ↔ CodeReview) 시 `auto_on_divergence` 발동 surface 확장. CFP-530 (Wave 4) Amendment 1 정합. |
| ADR-082 (Write-time self-write verification mandate) Amendment 1 | **I-5 directly-analogous pattern 재사용 backref (cross-ref only)** — ADR-082 §결정 2(a) corpus-claim-verify lint (CFP-841 Phase 2 carrier) 가 I-5 `[empirical-source: <ref>]` annotation 패턴을 verbatim 재사용 (`[verified: git show <ref>:<path>]` annotation 동형 mechanical 패턴). 본 ADR-068 I-5 본문 정책 (10 dimension enum / verdict field `dimensional_empirical_self_check_passed` / mitigation 4종) **0건 변경 invariant** — ADR-082 Amendment 1 = pattern 재사용 명시만 (양방향 backref). 충돌 0. |
| ADR-042 Amendment 7 + ADR-014 Amendment 4 (CFP-676 atomic carrier) | **I-5 적용 사례 declare (cross-ref only — I-5 본문 0건 변경)** — CFP-1026 S1 design lane agent 구조 재편이 spawn token cost 2.6배 (현재 13 Hub-spoke spawn → full activation 34) 의 `count` dimension quantitative parameter 를 도입. 본 parameter = I-5 `count` dimension 의 적용 대상 — CFP-676 Change Plan §13 C 항목 + Story §7 이 `[empirical-source: TBD]` annotation 보유 (I-5 Mitigation 2 explicit TBD 기재, trigger 1 empirical-absent default 차단). local probe/wiretap source 부재로 `[verified]` 금지 + `[fact-check-pending]` retain (Codex F-CFP676-TOKEN-EMPIRICAL-SOURCE P1). 본 ADR-068 I-5 invariant 본문 / 10 dimension enum / verdict field / mitigation 4종 **0건 변경** — CFP-676 = I-5 적용 declare 만 (양방향 backref). |

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (governance permanent — ADR-058 §결정 7 보안/governance default presumption 정합).

Amendment 시 ratchet 강화 방향만 허용 (ADR-058 §결정 5 sunset_justification 차단):
- scope 확장 (4 → 5+ invariants 추가)
- 강도 강화 (warning-tier → blocking-on-pr 승격 별도 CFP)
- enforcement surface 확장 (design + code → security + test lane 확장 별도 CFP)

약화 방향 (4 invariants 축소 / dual-binding → single-binding 다운그레이드 / warning tier 자체 deprecate) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

## 결과

- ArchitectAgent Phase 1 commit 직전 self-check **3** boolean field (mechanical_self_check_passed + boundary_completeness_self_check_passed + dimensional_empirical_self_check_passed) **셋** true 일 때만 진행
- DesignReviewPL + CodeReviewPL 4 invariants flag 검증 의무 (review-pl-base.md §3 갱신, Phase 2 sibling sync)
- review-verdict-v4 v4.3 schema MINOR bump (sibling sync 6 lane plugin mirror, ADR-010)
- wording-ssot-grep-lint warning-tier registry entry + lint script + workflow self-app (ADR-060 framework 4번째 entry)
- #438 자동 closure (CFP-527 Phase 2 PR `Closes #438` reference)
- MCT-150 baseline (boundary gap 4건 design-review PASS 후 code-review 발견) 대비 신규 Story 의 design-lane detection ratio ≥ 50% KPI (sunset gate 별도 CFP carrier)

## 변경이력

- **2026-05-13 v1 (Accepted, CFP-527)**: 초기 결정 — 4 invariants (I-1~I-4) + dual-binding + ADR-065 분리 운영.
- **2026-05-13 Amendment 1 (CFP-528)**: I-5 dimensional empirical grounding invariant 신설 (10 dimension enum 의 quantitative parameter `[empirical-source]` annotation 의무). review-verdict-v4 v4.3 → v4.4 MINOR bump (`dimensional_empirical_self_check_passed: bool` optional field + `findings[].type: "dimensional-empirical-gap"` literal). ratchet 강화 방향 (4 → 5 invariants, ADR-058 §결정 5 정합). #319 (RETRO-MCT-104 stream latency 150x oversight) keep-linked + close as absorbed (distinct failure-class but systemic super-class — empirical-grounded design discipline).
- **2026-05-17 cross-ref backref (CFP-841 — ADR-068 본문 정책 0건 변경)**: ADR-082 Amendment 1 (§결정 6 behavioral→mechanical 전환) 의 scope (a) `corpus-claim-verify` lint 가 I-5 `[empirical-source: <ref>]` annotation 패턴을 directly-analogous 하게 재사용 (`[verified: git show <ref>:<path>]` annotation 동형 mechanical 패턴). **본 변경이력 entry = backref 등록만 — I-5 invariant 본문 / verdict field / 10 dimension enum / mitigation 4종 0건 변경 invariant** (Amendment 아님, `## 관련 ADR` 표 ADR-082 row + `related_adrs` frontmatter backref 동반). 양방향 backref 정합 (ADR-082 frontmatter `related_adrs: ADR-068` + 본 entry).
- **2026-05-19 cross-ref backref (CFP-676 — ADR-068 본문 정책 0건 변경)**: CFP-1026 S1 (ADR-042 Amendment 7 + ADR-014 Amendment 4 atomic carrier) 의 design lane agent 구조 재편이 spawn token cost 2.6배 (현재 13 Hub-spoke spawn → full activation 34) 의 `count` dimension quantitative parameter 를 I-5 적용 대상으로 declare. **본 변경이력 entry = I-5 적용 declare backref 등록만 — I-5 invariant 본문 / verdict field / 10 dimension enum / mitigation 4종 0건 변경 invariant** (Amendment 아님). CFP-676 Change Plan §13 C 항목 + Story §7 이 `[empirical-source: TBD]` annotation 보유 (Mitigation 2 explicit TBD — local source 부재 `[verified]` 금지, `[fact-check-pending]` retain, Codex F-CFP676-TOKEN-EMPIRICAL-SOURCE P1). `## 관련 ADR` 표 ADR-042 Amendment 7 + ADR-014 Amendment 4 row 동반 (양방향 backref).
- **2026-05-20 Amendment 2 (CFP-1086 / Story-1 — I-4 wording SSOT invariant 강화)**: chief tie-break ladder 3 단계 신설 (RACI lookup → ADR-068 invariant → chief judgement + ADR Amendment 발의). 본문 `## Amendment 2` section 추가. `boundary_completeness_self_check_passed` scope expansion — 본 ladder 3단계 모두 통과 시 true. BackendArchEpic CFP-1086 Story-1 sibling carrier (ADR-042 Amendment 8 7+3+1 roster 재편 + ADR-086 신설 Deputy 신설 결정 framework P7 atomic). ratchet 강화 방향 (I-4 mechanism codify 추가, 약화 0건). I-1/I-2/I-3/I-5 본문 의미 변경 0건. 자세한 결정 matrix 는 본 ADR `## Amendment 2` body section 참조.
- **2026-05-20 Implementation note (CFP-1086 / Story-4 — ADR-068 본문 정책 0건 변경)**: Amendment 2 의 chief author body implementation cross-ref 명시 — `plugin-codeforge-design:agents/ArchitectAgent.md` (구 lane repo 좌표 — 현 `plugins/codeforge-design/`, repo 삭제됨 2026-06-12) §"Chief 통합 mechanism" + §"Chief tie-break ladder" + §"Wording SSOT advocate" sections 가 Amendment 2 §"Tie-break ladder 3 단계" 의 chief author 행동 implement. `plugin-codeforge-design:docs/architecture/codeforge-design.md` §"mctrader 5 repo cross-layer evidence" 가 P4 first-applied evidence case. **본 변경이력 entry = implementation surface 분포 declaration only — Amendment 2 본문 정책 / I-1~I-5 invariant body / verdict field / 10 dimension enum / mitigation 0건 변경 invariant** (Amendment 아님). frontmatter amendment_id:2 row `ref` field 갱신 (implementation note 동반 명시) + 본 ADR body §"Amendment 2 — CFP-1086 Story-1 chief tie-break ladder" 끝 § "Implementation note" subsection 추가. declaration layer (governance permanent) vs implementation layer (chief author prompt) vs architecture doc layer (lane internal SSOT) vs skill layer (RACI matrix host) 4-layer 분리 명시.
- **2026-05-20 Amendment 3 (CFP-1087 — I-6 audit-gate-pointer-existence invariant 신설)**: codeforge-review canonical `templates/review-pl-base.md` §8.6 audit gate finding 영역 pointer 부재 detection 영역 mechanical existence verify invariant (4-form pointer scope: link target / section anchor / file path reference / ADR §결정 N reference) 신설. review-verdict-v4 v4.6 → v4.7 MINOR bump (`audit_gate_pointer_self_check_passed: bool` 5번째 verdict-level optional field + `findings[].type: "audit-gate-pointer-missing"` 5번째 enum literal). ratchet 강화 방향 (5 → 6 invariants, ADR-058 §결정 5 정합). I-1/I-2/I-3/I-4/I-5 본문 의미 변경 0건 — I-6 disjoint append only (audit gate pointer existence axis 분리). CFP-528 Amendment 1 (I-5 declaration) precedent verbatim 답습. CFP-698 retro Wave 2-1 HIGH carrier (sibling: CFP-1088 IntegrationTest §7.4 disjoint, CFP-1089 mechanical workflow Wave-2 enforcement). collision resolution — main #1095 merged CFP-1086 Amendment 2 sequential precedence acquire 후 본 carrier renumber Amendment 3 (memory rule 6 title-search 영역 ADR-068 동일 slot detect 결함 evidence — `project_cfp_1087_phase1_pause_p0_collision.md` Lesson 2). ADR-073 cross-ref backref 동반 (I-6 verification primitive ↔ §결정 1 verify-before-assert primitive directly-analogous, ADR-073 본문 0건 변경).
- **2026-06-01 Amendment 5 (CFP-1565 — I-7 chief-author cross-ADR scope/fact claim consistency invariant 신설)**: chief author 가 ADR/doc 본문에서 다른 ADR 의 SSOT 값 (scope list / count / enum / 권한 범위 등) 인용·단언 시 대상 ADR direct Read-verify 후 대조 의무. Verification format = cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status). review-verdict-v4 v4.11 → v4.12 MINOR bump (`chief_author_crossref_consistency_self_check_passed: bool` 7번째 verdict-level optional field + `findings[].type: "chief-author-crossref-inconsistency"` 11번째 enum literal). ratchet 강화 방향 (6 → 7 invariants, ADR-058 §결정 5 정합). I-1/I-2/I-3/I-4/I-5/I-6 본문 의미 변경 0건 — I-7 disjoint append only (cross-ADR factual/scope claim consistency axis 분리). I-4 wording SSOT (identifier 표기 동기화) 와 disjoint axis — I-7 = cross-ADR 인용 **값** 의 SSOT 정합 (I-6 audit-gate-pointer = pointer **실재** verify, I-7 = 인용 **값** SSOT 정합). CFP-1522 retro F-003 P1 evidence (ADR-113 §결정 6 `admin:repo` scope claim ↔ ADR-066 §결정 2 PAT 6-scope SSOT mismatch, chief 미 cross-check). CFP-528 Amendment 1 (I-5 declaration) + CFP-1087 Amendment 3 (I-6 declaration) precedent verbatim 답습. ADR-073 §결정 1 verify-before-assert primitive directly-analogous (cross-ref backref). DesignReviewPL + CodeReviewPL dual cross-validate. Wave 1 declaration-only (mechanical wire = 별 sub-CFP carrier, ADR-082 §결정 6 retain pattern). doc-only fast-path ADR-054.
- **2026-05-25 Amendment 4 (CFP-1580 — §결정 7 Wave 2 mechanical wire 영역 design review skip 정합 invariant codify)**: 신규 §결정 7 추가 — Wave 2 mechanical wire 영역 (Wave 1 declarative anchor active 후 scripts/workflow/bats implementation only) 에서 DesignReviewPL spawn = optional (skip default) + Wave 1 declarative or 신규 ADR/governance 영역 = mandatory retain. ArchitectAgent §13 4-tuple self-check (ADR-068 I-1~I-6 + ADR-065 10-item + ADR-082 §결정 11.A bats RED→GREEN stash proof + chief tie-break ladder 3-단계) + CodeReviewPL mechanical correctness review retain = DesignReviewPL 대체 sufficient. 5 precedent CFP linear chain evidence base (CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539 — all Wave 2 mechanical wire + DesignReviewPL spawn 0 + 0 design FIX + 0 divergence + wrapper-self CodeReviewPL PASS + admin squash merge) pattern_count 5 ≫ ADR-045 §D-9 threshold 2 = Mandatory escalation 산물 (PMOAgent CFP-1539+1540 batch retro §6 escalate_user → 사용자 Option A confirmed compress normative codify 2026-05-25 KST). DeveloperPL spawn prompt `wave2_mechanical_wire_dr_skip_applicable: bool` declarative anchor field codify (declarative anchor only — 실 wire = 별 sub-CFP carrier Wave 2 mechanical enforcement). boundary completeness 6 invariants (I-1~I-6) 본문 의미 변경 0건 — §결정 7 = orthogonal axis (spawn-time orchestration governance) append only, invariants axis (write-time verification semantic) 영역 외. review-verdict-v4 schema 변경 0건 (declarative anchor only, sibling sync 면제). ratchet 강화 방향 (Wave 2 영역 skip default codify + Wave 1 영역 mandatory retain invariant 강화 boundary 명확화, scope 축소 0). is_transitional false 유지 (permanent governance). paired sibling ADR-045 §D-9 Amendment 7 (evidence-only, Amendment 6 CFP-776 ADR-082 forcing function 산물 evidence-only Amendment pattern 답습). doc-only fast-path ADR-054 (src/tests 무변경).

---

## Amendment 2 — CFP-1086 Story-1 chief tie-break ladder (P1, BackendArchEpic carrier)

**날짜**: 2026-05-20

### 동기

CFP-1086 BackendArchEpic Phase 2 의 Phase 1 dialog 에서 사용자 ACK 받은 (b)+(c) WHY — 깊은 동기 (c) "deputy 간 RACI 충돌" (§3/§7/§11 작성 시 DataArch + SecurityArch + InfraOpArch 가 RDB 영역에서 ownership 부딪힘). 본 Amendment 2 = (c) WHY 의 mechanism gap 해소 carrier — wording SSOT 충돌 시 chief tie-break 절차 codify.

기존 I-4 (wording SSOT invariant) = Story §3 결정 wording ↔ ADR §결정 wording ↔ impl enum identifier 양방향 wording desync 검출만 cover. **충돌 해소 절차 부재** — chief author 가 wording 충돌 발견 시 어느 SSOT 가 우선인지 / 누가 정정 권한 보유인지 / 정정 후 어떤 ADR carrier 가 발의되는지 mechanism 명시 부재 → 양 SSOT 모두 stale 유지 또는 chief 임의 결정 (RACI 충돌 재발).

본 Amendment 2 = chief tie-break ladder 3 단계 mechanism codify — RACI 매트릭스 lookup (deputy-mandate skill R/A row) → ADR-068 invariant 적용 (I-1~I-5) → chief judgement + ADR Amendment carrier 발의 (사용자 escalation 의무).

### Tie-break ladder 3 단계 (순차 적용 의무)

#### 1단계 — RACI 매트릭스 lookup (deputy-mandate skill row)

`codeforge:deputy-mandate` skill 의 7+3+1 mandate 매트릭스 (CFP-1086 Story-1 Amendment 8 정합) + **Story-3 carrier** RACI 표준 row 형식 (4-column R/A/C/I) 에서 충돌 영역 row 검색:

- **명시된 R/A 가 존재** → 그 deputy / chief author 의 결정 채택. 다른 deputy 는 C/I 역할만 (consult / informed).
- **명시된 R/A 부재 OR 영역 row 자체 부재** → 2단계 진입.

근거: RACI 매트릭스는 ADR-042 Amendment 8 + Story-3 carrier 로 codify 된 explicit ownership SSOT — explicit > implicit invariant.

#### 2단계 — ADR-068 invariant 적용 (I-1 ~ I-5)

5 invariants 의 **boundary completeness verification format** 적용:

- **I-1 API contract semantic completeness** — public method 의 return enum / state 의미 docstring 명시 의무. 충돌 시 API contract 우선 SSOT.
- **I-2 cross-module status enum propagation** — module 간 enum propagation 의 caller 분기 처리 의무. 충돌 시 producer 측 SSOT 우선.
- **I-3 unconditional vs conditional guard placement intent** — invariant guard 가 "함수 진입 시점 무조건" 인지 "특정 path 한정" 인지 ADR 본문 명시 의무. 충돌 시 unconditional 우선 (broad coverage, ADR-064 정합).
- **I-4 wording SSOT** — Story §3 결정 wording ↔ ADR §결정 wording ↔ impl enum identifier 양방향 일치 의무. 충돌 시 **ADR §결정 wording 우선 SSOT** (governance permanent layer 가 Story / impl 보다 우선 — Story key 종속 vs Story key 독립 invariant 정합).
- **I-5 dimensional empirical grounding** — 10 dimension enum 의 quantitative parameter empirical-source annotation 의무. 충돌 시 `[verified: <ref>]` annotation 보유 측 우선, 양 측 모두 `[TBD]` 시 `[fact-check-pending]` retain (3단계 진입).

5 invariants 모두 통과 안 됨 → 3단계 진입.

#### 3단계 — chief judgement + ADR Amendment carrier 발의

RACI 미codify + ADR-068 invariant 적용 후도 wording 충돌 미해소 영역 (mechanism gap):

- **chief author (ArchitectAgent Opus)** judgement — multi-source synthesis 책임자 단독 결정.
- **ADR Amendment carrier 발의 의무** — RACI 미codify 영역을 codify 하는 별 follow-up CFP (또는 본 Story 내 ADR Amendment) 발의. ADR-086 §결정 1 axis 분석 + §결정 2 5-checklist self-app 의무 (Deputy 신설 결정 framework cross-ref).
- **사용자 escalation 의무** — chief judgement 단독 결정 = `AskUserQuestion` 발화 의무 (ADR-064 §결정 3 룰 5 가치 판단 영역 한정 정합). 사용자 ACK 후 ADR Amendment carrier 발의.

근거: 3단계 = RACI 미codify 영역 = mechanism gap → ADR Amendment carrier 가 다음 Story 의 1단계 (RACI lookup) 입력으로 채워짐. Iterative ratchet 강화 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합).

### Verdict packet boundary expansion (review-verdict-v4)

본 Amendment 2 carrier = `boundary_completeness_self_check_passed` field scope expansion:

- **기존 (v4.3, CFP-527)**: 4 invariants (I-1 ~ I-4) 검증 통과 시 true
- **Amendment 1 (v4.4, CFP-528)**: I-5 별 boolean field `dimensional_empirical_self_check_passed` 신설 (별 disjoint check)
- **본 Amendment 2 (CFP-1086)**: `boundary_completeness_self_check_passed` scope expansion — 5 invariants (I-1 ~ I-4 + Amendment 2 chief tie-break ladder 3 단계 mechanism) 모두 통과 시 true. I-5 별 field 무변경 (Amendment 1 disjoint invariant 보존).

contract version bump = `review-verdict-v4 v4.5 → v4.6 MINOR` — sibling ADR-042 Amendment 8 의 `deputy_axis_restructure_self_check_passed` field 신설 + 본 Amendment 2 의 boundary scope expansion (changelog row 안 명시 — schema field 자체는 변경 0). ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합 (ADR-042 Amendment 8 의 신규 field 신설로 v4.6 carrier 가 본 boundary expansion 도 동반 codify).

### 4-way 이념 대립 axis 보존

본 Amendment 2 = **chief tie-break mechanism** codify — 4-way 이념 대립 axis (CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ DataArch — single-mandate advocacy 패턴 정합) 본문 변경 0건. tie-break = 4-way 대립 후 chief 가 종합 판정 시점 절차 — 대립 자체 (advocate phase) 영역 외.

ArchitectPLAgent 가 `review_verdict_v4` packet 작성 시 본 ladder 3단계 모두 적용 evidence 보유 (synth log 안 명시 의무) — false 시 ArchitectAgent re-spawn (FIX 의무, ADR-067 max FIX 3/3 cap 정합).

### 기존 정책 변경 0건 (ADR-068 본문 I-1 ~ I-5)

본 Amendment 2 = ADR-068 의 결정 1~6 본문 변경 0건. I-1 ~ I-5 invariants 본문 의미 변경 0건. 변경 = (a) 본 `## Amendment 2` body section (b) frontmatter amendments[] row 2 + related_stories CFP-1086 append + related_adrs ADR-042 / ADR-086 append + amendment_log row 2. `boundary_completeness_self_check_passed` scope expansion = I-4 mechanism boost (verification format 강화 — chief tie-break ladder 3단계 mechanism 통과 의무 명시) — scope 축소 0건. ratchet 강화 방향 (4 → 5 invariants 후 5번째 I-4 mechanism codify 추가, ADR-058 §결정 5 정합) → sunset_justification 불필요 (frontmatter amendment_id:2 `sunset_justification: ratchet 강화 방향 명시`).

### Cross-ref

- ADR-042 Amendment 8 (CFP-1086 Story-1 sibling carrier — 7+3+1 roster 재편 atomic, axis 분석 + 5-checklist self-app 첫 사례). 본 Amendment 2 의 1단계 (RACI lookup) 가 ADR-042 Amendment 8 의 mandate 매트릭스를 입력으로 받음.
- ADR-086 (CFP-1086 Story-1 신설 carrier — Deputy 신설 결정 framework P7). 본 Amendment 2 의 3단계 (chief judgement + ADR Amendment 발의) 가 ADR-086 §결정 1 axis 분석 + §결정 2 5-checklist self-app 의무 발동.
- ADR-064 §결정 3 룰 5 (가치 판단 영역 한정 `AskUserQuestion`) — 본 Amendment 2 의 3단계 사용자 escalation 의무 정합.
- ADR-067 max FIX 3/3 cap — `boundary_completeness_self_check_passed: false` 시 ArchitectAgent re-spawn 의무, 3회 후 implementability reassessment trigger 정합.
- review-verdict-v4 v4.6 MINOR (CFP-1086 carrier) — 본 Amendment 2 scope expansion + ADR-042 Amendment 8 의 `deputy_axis_restructure_self_check_passed` field 동반 atomic.
- ADR-068 Amendment 1 (CFP-528) — I-5 disjoint field invariant 보존 (본 Amendment 2 = I-1~I-4 영역만 scope expansion).

### Implementation note (CFP-1086 Story-4 — chief author body cross-ref)

본 Amendment 2 declare = governance permanent layer ADR 본문. **Implementation body** = codeforge-design plugin 의 ArchitectAgent (chief author) prompt body — `agents/ArchitectAgent.md` §"Chief 통합 mechanism" + §"Chief tie-break ladder" sections (CFP-1086 Story-4 carrier).

#### Implementation surface 분포 (declarative SSOT only — body 변경 0건)

| Layer | SSOT location | scope |
|---|---|---|
| **Declaration layer** (governance permanent) | 본 ADR-068 Amendment 2 §"Tie-break ladder 3 단계" | mechanism 절차 정의 (3 단계 sequential) + 사용자 escalation 의무 + ratchet 강화 방향만 |
| **Implementation layer** (chief author prompt) | `plugin-codeforge-design:agents/ArchitectAgent.md` §"Chief 통합 mechanism" + §"Chief tie-break ladder" | multi-source synthesis pattern 4 단계 + ladder 3 단계 chief author 행동 implement + verdict packet binding |
| **Architecture doc layer** (lane internal 누적 SSOT) | `plugin-codeforge-design:docs/architecture/codeforge-design.md` §"경계" + §"mctrader 5 repo cross-layer evidence" | 4-way RACI matrix + mctrader first-applied evidence + cross-layer ELT/ETL/CDC boundary |
| **Skill layer** (RACI matrix host) | `plugin-codeforge:skills/deputy-mandate/SKILL.md` RACI section (CFP-1086 Story-3 carrier — parallel sibling) | 4-way overlap zone RACI 표준 row 형식 (R/A/C/I 4-column) |

#### Carrier 분리 (Story 4 vs Story 3 vs Story 1)

| Carrier Story | 영역 | 본 ADR-068 Amendment 2 의 관계 |
|---|---|---|
| CFP-1086 Story-1 | Amendment 2 본문 (3 단계 declare) + ADR-042 Amendment 8 (roster) + ADR-086 (framework) atomic | declaration carrier (본 Amendment 2 body 자체) |
| CFP-1086 Story-3 | `skills/deputy-mandate/SKILL.md` RACI matrix codify | ladder 단계 1 (RACI lookup) 의 input SSOT codify carrier |
| **CFP-1086 Story-4 (본)** | `agents/ArchitectAgent.md` chief body + `docs/architecture/codeforge-design.md` mctrader evidence + 본 implementation note | implementation carrier (Amendment 2 mechanism 의 chief author 행동 body + 실 적용 evidence) |

#### Body 정합성 invariant

- 본 Amendment 2 declaration body (§"Tie-break ladder 3 단계") 와 implementation body (`agents/ArchitectAgent.md` §"Chief tie-break ladder") wording 동기화 의무 (I-4 wording SSOT 자기 적용)
- declaration 변경 시 implementation cascade 의무 (ADR-065 mechanical 7-item self-check §결정 1 row 6 cross-ref drift catch)
- mctrader evidence (architecture doc 영역) = first-applied case declaration only — 실 적용 carrier 는 mctrader Epic 발의 시점 (consumer 영역, codeforge sibling Epic 자매 carrier 가능)

#### Mechanical enforcement actions binding (이미 §결정 6 정의 — Amendment 2 추가 없음)

본 Amendment 2 = `boundary_completeness_self_check_passed` scope expansion (5 invariants I-1~I-4 + Amendment 2 ladder 3 단계 mechanism). frontmatter `mechanical_enforcement_actions[]` 영역 unchanged — 기존 entry `boundary-completeness-self-check` (status: deferred-followup, target_section: §결정 2) 가 scope expansion 후도 동일 entry 로 cover (verdict field-only enforcement 유지).

신규 lint script / workflow yml / registry entry **0건** (declaration-only + chief author body cross-ref binding only). Implementation cascade 검증 = `agents/ArchitectAgent.md` body 자체 직접 read 만 (lint script 영역 외).

### Cross-ref (Implementation note 영역 추가)

- `plugin-codeforge-design:agents/ArchitectAgent.md` §"Chief 통합 mechanism" + §"Chief tie-break ladder" + §"Wording SSOT advocate" body (CFP-1086 Story-4)
- `plugin-codeforge-design:docs/architecture/codeforge-design.md` §"mctrader 5 repo cross-layer evidence" (CFP-1086 Story-4 P4 carrier)
- `plugin-codeforge:skills/deputy-mandate/SKILL.md` 4-way overlap zone RACI section (CFP-1086 Story-3 carrier — parallel sibling)

---

---

## Amendment 4 — CFP-1580 Wave 2 mechanical wire 영역 design review skip 정합 invariant codify

**날짜**: 2026-05-25 KST

### 동기

PMOAgent CFP-1539+1540 batch retro §6 §D-9 escalation pattern detect — pattern `wave2-mechanical-wire-design-review-skip` pattern_count 5 reach (CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539 5 precedent linear chain, all Wave 1 declarative anchor active state + scripts/workflow/bats implementation only + DesignReviewPL spawn 0 + 0 design FIX + 0 design review divergence detection + wrapper-self CodeReviewPL PASS + admin squash merge). 5 ≫ threshold 2 = Mandatory escalation → escalation_action escalate_user → 사용자 결정 (2026-05-25 KST): **Option A — Compress normative codify**.

기존 ADR-068 §결정 1~6 = write-time verification semantic invariants (I-1~I-6) 영역. **spawn-time orchestration governance (DesignReviewPL spawn 여부 결정) 영역 codify 부재** — Wave 2 mechanical wire 영역에서 5 Story 모두 DesignReviewPL skip 했으나 explicit invariant 없음 → implicit norm 형성 → bypass-as-norm-mutation 위험 (ADR-024 Amendment 8 cross-ref).

본 Amendment 4 = §결정 7 신설 — Wave 2 mechanical wire 영역 DesignReviewPL spawn = optional (skip default) + Wave 1 declarative or 신규 ADR/governance 영역 = mandatory retain. explicit invariant 확립 → audit trail 보장 + Wave 1 영역 mandatory retain invariant 강화 (boundary 명확화).

### orthogonal axis 보존 (§결정 1 invariants 영역 외)

본 Amendment 4 = **spawn-time orchestration governance axis** codify. §결정 1 invariants (I-1~I-6) = **write-time verification semantic axis**. 두 axis disjoint:

| Axis | Scope | Phase | Amendment carrier |
|---|---|---|---|
| **write-time verification semantic** (§결정 1) | ArchitectAgent §3/§7 작성 시 4-6 invariants self-check | commit-time | Amendment 1 (I-5) / Amendment 3 (I-6) |
| **spawn-time orchestration governance** (§결정 7, 본 Amendment) | DesignReviewPL spawn 여부 결정 (Wave 1 vs Wave 2) | spawn-time | **Amendment 4 (본)** |

I-1/I-2/I-3/I-4/I-5/I-6 invariants 본문 의미 변경 0건 — §결정 7 = orthogonal axis append only, invariants axis 영역 외.

### Wave 1 vs Wave 2 boundary 정합 (§결정 7.1 cross-ref)

§결정 7.1 표 boundary 정의 verbatim 적용. Wave 2 mechanical wire 정의 = Wave 1 declarative anchor active state + scripts/workflow/bats implementation only (file scope: `scripts/*.{sh,py}` + `templates/github-workflows/*.yml` + `.github/workflows/` self-app + `tests/scripts/*.bats` + `docs/evidence-checks-registry.yaml` entry append + `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump).

신규 ADR/governance 영역 = Wave 1 declarative anchor (mandatory retain). 모호 시 Wave 1 측 분류 (Wave 1 mandatory retain 강화 방향, scope 축소 차단).

### 5 precedent CFP linear chain evidence base (§결정 7.3 cross-ref)

§결정 7.3 표 verbatim. 5 Story 모두 wrapper-self CodeReviewPL PASS + admin squash merge — 0 design FIX, 0 design review divergence detection. pattern_count 5 ≫ ADR-045 §D-9 threshold 2 = Mandatory escalation → 사용자 Option A confirmed.

| # | CFP | Wave 1 anchor | Wave 2 wire | Outcome |
|---|---|---|---|---|
| 1 | CFP-1489 | CFP-1437 (ADR-082 Amd 15 pre-spawn HEAD-pin 1-E) | merged | DesignReviewPL spawn 0 + 0 design FIX |
| 2 | CFP-1497 | CFP-1435 (ADR-082 Amd 17 amendment-slot reservation 1-G) | merged | DesignReviewPL spawn 0 + 0 design FIX |
| 3 | CFP-1500 | CFP-1436 (ADR-082 Amd 16 mid-spawn drift 1-F) | merged | DesignReviewPL spawn 0 + 0 design FIX |
| 4 | CFP-1502 | CFP-1438 (ADR-039 Amd 5 / ADR-044 Amd 3 chief author span 1-D) | merged | DesignReviewPL spawn 0 + 0 design FIX |
| 5 | CFP-1539 | CFP-FU-A (ADR-082 Amd 19 pre-spawn-prompt-finalize 1-I) | merged | DesignReviewPL spawn 0 + 0 design FIX |

### DeveloperPL spawn prompt declarative anchor field codify

본 Amendment 4 = declarative anchor only — DeveloperPL spawn prompt 안 다음 field declare:

```yaml
wave2_mechanical_wire_dr_skip_applicable: bool  # Wave 2 mechanical wire 영역 PR 시 self-declare 의무
                                                  # true = §결정 7.1 표 Wave 2 column 정합 + DesignReviewPL skip default
                                                  # false = Wave 1 declarative or 신규 ADR/governance 영역 = DesignReviewPL mandatory retain
                                                  # 실 wire (DeveloperPLAgent agent file 변경 / spawn prompt template 변경 / workflow lint) = 별 sub-CFP carrier
```

declarative anchor only — 실 wire = 별 sub-CFP carrier (Wave 2 mechanical enforcement). 본 §결정 7 = declarative SSOT (governance permanent layer), 실 implementation = DeveloperPLAgent agent file 변경 / spawn prompt template 변경 / workflow lint 신설 = 별 carrier.

### review-verdict-v4 schema 변경 0건 (§결정 7.5 cross-ref)

본 Amendment 4 = declarative anchor only — review-verdict-v4 schema bump 0건 (sibling sync 면제, ADR-008 §결정 정합). 기존 4 boolean field (mechanical_self_check_passed / boundary_completeness_self_check_passed / dimensional_empirical_self_check_passed / audit_gate_pointer_self_check_passed) 보존.

### ratchet 강화 방향 (ADR-058 §결정 5 / ADR-064 §결정 7 정합)

- 강화 방향: Wave 2 mechanical wire 영역 skip default codify + Wave 1 영역 mandatory retain invariant 강화 boundary 명확화
- 축소 차단: DesignReviewPL spawn mandatory retain 영역 축소 (Wave 1 governance / 신규 ADR 영역 skip 불가) / ArchitectAgent §13 4-tuple self-check 영역 축소 / process compression 후 본 codify 자체 revoke 발의 차단
- invariants count 6 retain (I-1~I-6 본문 의미 변경 0건)
- `is_transitional: false` 유지 (permanent governance — ADR-058 §결정 7 보안/governance default presumption 정합)

### Mechanical enforcement actions binding (§결정 6 영역)

본 Amendment 4 = declarative anchor only — `mechanical_enforcement_actions[]` entry 신규 0건. 실 mechanical wire (DeveloperPL spawn prompt field 실 wire / workflow lint `wave2-mechanical-wire` label PR 영역 DesignReviewPL spawn 0 warning tier 검출) = 별 sub-CFP carrier.

ADR-082 §결정 6 + ADR-070 §D5 + CFP-898/899/900 + ADR-085/097 precedent declaration-only Wave 1 retain pattern 답습.

### paired sibling ADR-045 §D-9 Amendment 7

본 Amendment 4 carrier = ADR-045 §D-9 Amendment 7 paired sibling (CFP-1580, evidence-only Amendment). pattern_count 5 escalation_resolved_carrier 본 CFP declare — Amendment 6 CFP-776 ADR-082 forcing function 산물 evidence-only Amendment pattern verbatim 답습.

### Cross-ref

- ADR-045 §D-9 Amendment 7 (CFP-1580 paired sibling — evidence-only forcing function 산물 기록)
- ADR-068 Amendment 1 (CFP-528 — I-5 declaration precedent)
- ADR-068 Amendment 2 (CFP-1086 — chief tie-break ladder 3-단계, ArchitectAgent commit-time forcing function 기반)
- ADR-068 Amendment 3 (CFP-1087 — I-6 audit-gate-pointer precedent)
- ADR-065 (10-item mechanical sync syntactic, Amendment 5 11th post-write actual-run verify — ArchitectAgent §13 4-tuple self-check 1/4 layer)
- ADR-082 §결정 11.A (bats RED→GREEN stash proof — ArchitectAgent §13 4-tuple self-check 1/4 layer)
- ADR-058 §결정 5 (ratchet 강화 방향만 amendment 정합)
- ADR-064 §결정 7 (top-down ratchet 정합)
- ADR-024 Amendment 8 (bypass-as-norm-mutation 위험 cross-ref)
- 5 precedent CFP linear chain: CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539

---

## Amendment 5 — CFP-1565 I-7 chief-author cross-ADR scope/fact claim consistency invariant 신설

**날짜**: 2026-06-01 KST

### 동기

CFP-1522 retro F-003 P1 — ADR-113 §결정 6 (admin merge preflight gate) 가 PAT scope 를 `admin:repo` 로 단언했으나, ADR-066 §결정 2 의 PAT 6-scope SSOT 와 mismatch. chief author 가 ADR-113 본문 작성 시 ADR-066 의 실제 scope SSOT 를 direct Read-verify 하지 않고 인용 → cross-ADR scope claim 불일치 = ADR 간 경계 사실 drift.

기존 I-1~I-6 invariants = (I-1) API contract docstring / (I-2) cross-module propagation / (I-3) guard placement / (I-4) wording SSOT (identifier 표기) / (I-5) dimensional empirical / (I-6) audit-gate-pointer existence. **chief author 가 다른 ADR 의 SSOT 값 (scope / count / enum / 권한) 을 인용·단언할 때 그 값의 SSOT 정합 verify 영역 codify 부재** — I-4 는 identifier wording 표기 동기화만 cover, cross-ADR factual/scope **값** 의 SSOT 정합은 무방비.

본 Amendment 5 = I-7 신설 — chief author cross-ADR scope/fact claim 인용 시 대상 ADR direct Read-verify 후 대조 의무.

### I-7 정의 (§결정 1 cross-ref)

§결정 1 I-7 declaration verbatim 적용. cross-ADR scope/fact claim 별 cross-adr-claim-verify-annotation 3-key (cited_adr+§결정 / cited_value / verify_status) 명시 + commit 직전 target ADR direct Read 대조. ADR-073 §결정 1 verify-before-assert primitive directly-analogous (source-of-truth direct fetch).

### I-4 disjoint axis 보존

| Invariant | axis | verify 대상 |
|---|---|---|
| **I-4 wording SSOT** | identifier 표기 동기화 | Story §3 결정 ↔ ADR ↔ impl 의 enum identifier / method name / noun phrase 표기 일치 |
| **I-6 audit-gate-pointer existence** | pointer 실재 | §8.6 audit gate finding 의 link / anchor / file path / ADR §결정 N pointer 실재 |
| **I-7 cross-ADR claim consistency (본)** | cross-ADR 인용 **값** SSOT 정합 | 다른 ADR 의 scope list / count / enum / 권한 범위 인용 값 ↔ 대상 ADR 실제 SSOT 대조 |

I-4 = 표기 sync (wording), I-7 = factual/scope **값** SSOT 정합. 세 invariant 모두 disjoint axis — dedup 비교차 (same anchor_id 양 literal 후보 충돌 회피).

### verdict packet field 신설 (review-verdict-v4 v4.12)

- 신규 7번째 verdict-level optional bool field `chief_author_crossref_consistency_self_check_passed` — §3/§7/§10/§11 의 모든 cross-ADR scope/fact claim 이 cross-adr-claim-verify-annotation 보유 + verify_status=verified (또는 Justification 면제) 시 true. 1+ pending/미검증 시 false + `findings[].type: "chief-author-crossref-inconsistency"` (11번째 enum literal) 동반 emit.
- ADR-008 §결정 2 "새 선택 필드 추가" + "enum literal 추가" MINOR bump 정합 (closed-enum 10 → 11 ratchet, additive only). backward-compat invariant (기존 v4.11 consumer 가 본 7번째 field + 11번째 literal 무시 가능).
- DesignReviewPL + CodeReviewPL dual cross-validate (I-1~I-6 패턴 답습).

### ratchet 강화 방향 (ADR-058 §결정 5 / ADR-064 §결정 7 정합)

- 강화 방향: 6 → 7 invariants 추가 (scope 축소 0건)
- I-1/I-2/I-3/I-4/I-5/I-6 본문 의미 변경 0건 — I-7 disjoint append only
- `is_transitional: false` 유지 (permanent governance — ADR-058 §결정 7 governance default presumption 정합)
- sunset_justification = N/A (ratchet 강화 방향, Amendment 1/3 invariant 신설 precedent 답습)

### Mechanical enforcement actions binding (§결정 6 영역)

본 Amendment 5 = Wave 1 declaration-only — `mechanical_enforcement_actions[]` entry `chief-author-crossref-consistency-check` (status deferred-followup) append. 실 mechanical wire (`scripts/check-chief-author-crossref-consistency.sh` + scripts/lib + workflow yml + bats fixture) = 별 sub-CFP Wave 2 carrier. bypass_label = `hotfix-bypass:boundary-wording` 재사용 (ADR-068 owner family — 신규 label 신설 0건, dimensional-empirical-grounding deferred entry 가 기존 label 재사용한 precedent 답습). pattern_count >= 2 재발 시 follow-up CFP MUST promote (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습).

### Cross-ref

- ADR-066 §결정 2 (PAT 6-scope SSOT — I-7 evidence ground truth source, 본문 0건 변경)
- ADR-113 §결정 6 (admin merge preflight gate PAT scope claim — CFP-1522 retro F-003 P1 sentinel, 본문 0건 변경)
- ADR-073 §결정 1 (verify-before-assert primitive — I-7 Mitigation directly-analogous)
- ADR-068 Amendment 1 (CFP-528 — I-5 invariant 신설 precedent) + Amendment 3 (CFP-1087 — I-6 invariant 신설 precedent)
- ADR-058 §결정 5 / ADR-064 §결정 7 (top-down ratchet 정합)
- ADR-082 §결정 6 + ADR-070 §D5 (declaration-only Wave 1 retain pattern 답습)
- ADR-065 §결정 1 row 10 (Amendment 6 CFP-1565 — commit-time 선제-lint 에 claude-md-line-cap 추가, sibling carrier same Story)

---

## 관련 파일

- `CLAUDE.md` (ADR (`docs/adr/` SSOT) 단락 + Inter-plugin Contract 단락 ADR-068 cross-ref 추가)
- `docs/adr/ADR-068-boundary-completeness-invariants.md` (Amendment 5 — frontmatter `amendments[]` amendment_id 5 + `mechanical_enforcement_actions[]` `chief-author-crossref-consistency-check` entry + `related_stories` CFP-1565 + `related_adrs` ADR-066 / ADR-113 + 본문 §결정 1 I-7 declaration + §결정 2 Tier A/B/C I-7 row + §결정 6 표 row + 본 `## Amendment 5` section + 변경이력 entry, CFP-1565)
- `docs/inter-plugin-contracts/review-verdict-v4.md` (v4.11 → v4.12 MINOR bump — `chief_author_crossref_consistency_self_check_passed` field + `chief-author-crossref-inconsistency` literal, CFP-1565)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (review_verdict row v4.11 → v4.12, CFP-1565)
- `docs/evidence-checks-registry.yaml` (`chief-author-crossref-consistency` deferred-followup entry append, CFP-1565)
- `plugin-codeforge-review/agents/DesignReviewPLAgent.md` + `plugin-codeforge-review/agents/CodeReviewPLAgent.md` + `plugin-codeforge-review/templates/review-pl-base.md` (I-7 check item + finding type — Phase 2 cross-repo sibling sync PR)
- `docs/inter-plugin-contracts/review-verdict-v4.md` (v4.2 → v4.3 MINOR bump)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (review-verdict-v4 version row 갱신)
- `skills/review-responsibility/SKILL.md` (CodeReview lane row "4 invariants cross-validate" 추가)
- `docs/evidence-checks-registry.yaml` (`wording-ssot-grep-lint` warning-tier entry append)
- `scripts/check-wording-ssot.sh` (mechanical lint 신규)
- `templates/github-workflows/wording-ssot-check.yml` (workflow template 신규)
- `.github/workflows/wording-ssot-check.yml` (self-app byte-identical)
- `plugin-codeforge-review/templates/review-pl-base.md` (§3 4-invariant flag — Phase 2 sibling sync)
- `plugin-codeforge-design/templates/architect-agent-prompt.md` (self-check step — 4 invariants + ADR-065 7-item 분리 명시, Phase 2 sibling sync)

---

## 2026-05-20 cross-ref note (CFP-1059 — ADR-068 본문 정책 0건 변경)

**Carrier**: CFP-1059 Story-1 (ADR-023 Amendment 1 + ADR-087 + ADR-088 + ADR-042 Amendment 9 sibling carrier).

본 cross-ref note = ADR-068 §결정 1~6 본문 / I-1~I-5 invariants body / verdict field / 10 dimension enum / mitigation **0건 변경 invariant** (Amendment 아님, declaration-only Wave 1 cross-ref note).

### I-5 dimensional empirical grounding 정합 cross-ref (3개소)

CFP-1059 Story-1 신설 ADR + Amendment 들이 I-5 dimensional empirical grounding 패턴 정합 — `[empirical-source: TBD]` annotation 의무 verification format 답습:

| Source ADR | quantitative parameter | I-5 dimension | annotation 위치 |
|---|---|---|---|
| ADR-087 §결정 5 step 4 | healthcheck window (default 60s timeout) | latency / lifecycle | `[empirical-source: TBD]` — consumer 별 healthcheck window 측정 의무 |
| ADR-087 §결정 5 step 7 | blue graceful drain (HTTP default 30s / WebSocket default 5min) | latency / lifecycle | `[empirical-source: TBD]` — mctrader websocket 시세 수집 사례 사후 측정 lock-in |
| ADR-087 §결정 5 step 8 | blue 3-시간 보존 (retention window) | lifecycle / count | `[empirical-source: TBD]` — 3-시간 = brainstorm Phase 1 합의 default, consumer override 가능 (`project.yaml deploy.retention_hours`) |
| ADR-042 Amendment 9 spawn count | 2 lane × 2 agent = 4 spawn point per Story (production cutover-touching Story 한정) | count / scale | `[empirical-source: TBD]` — consumer mctrader production cutover Story 첫 적용 시 측정 lock-in |

I-5 §결정 1 Amendment 1 의 4 anti-pattern 차단 (`empirical-absent default` / `synthetic guess` / `industry-assumption transplant` / `legacy inertia`) — 모든 quantitative parameter `[empirical-source: TBD]` 박제 = explicit TBD 박제 mitigation 정합 (well-defined SLA / standardized protocol RFC / vendor doc explicit guarantee 부재 영역).

### declaration-only Wave 1 retain (mechanical_enforcement_actions[] 0건 추가)

본 cross-ref note = mechanical_enforcement_actions[] entry 0건 추가 — ADR-082 §결정 6 + ADR-070 §D5 + CFP-898 / CFP-899 / CFP-900 precedent declaration-only Wave 1 retain pattern 답습. 본 CFP-1059 Story-1 = declaration carrier (declarative scope), mechanical wire = Phase 2 PR (별 CFP — Wave 2 후속 carrier).

### Cross-references

- ADR-023 Amendment 1 (CFP-1059 / Story-1 — lane plugin 6 → 8 확장)
- ADR-087 (CFP-1059 / Story-1 — Deploy lane as 7th lane plugin, §결정 5 `[empirical-source: TBD]` 3 annotation)
- ADR-088 (CFP-1059 / Story-1 — Deploy Review lane + ProductionEvidence transfer)
- ADR-042 Amendment 9 (CFP-1059 / Story-1 — 4 신설 agent tier spawn count empirical grounding)
- ADR-082 §결정 6 + ADR-070 §D5 (declaration-only Wave 1 retain pattern 답습)
- ADR-058 §결정 5 (본 cross-ref note = ADR-068 본문 정책 0건 변경, sunset_justification 영역 외)
