---
adr_number: 83
title: "Mechanical fast-path — Orchestrator direct-commit 권한 + FIX iteration 비소비 경계 + same-iteration internal verify 절차"
status: Proposed
category: Process
date: 2026-05-18
carrier_story: CFP-665
parent_epic: null
supersedes: null
amends: null
amendments: []
proposer: PMOAgent
author: ArchitectAgent
related_stories:
  - CFP-665   # ADR-045 Amendment 5 §D-9 cross-Story pattern threshold (N=2) carrier
  - CFP-19    # R11 Mechanical fast-path inline mention (formalize 대상 SSOT gap)
related_adrs:
  - ADR-045   # §D-9 cross_story_pattern_adr_trigger — 본 carrier = pattern_count 2 ≥ threshold 2 산물
  - ADR-067   # fix-ledger implementability escalation + max FIX overflow (§10 카운터 / RESET 경계 cross-ref)
  - ADR-065   # ArchitectAgent Phase 1 mechanical self-check (mechanical sync self-check 인접 영역, disjoint)
  - ADR-054   # doc-only Story fast-path (별 mechanism — doc-only Story 분류 vs review-iteration fast-path disjoint)
  - ADR-022   # Sonnet review-verdict decider (Deprecated — PL = adjudicator, fast-path 판정 주체 명확화)
  - ADR-008   # inter-plugin contract versioning (review-verdict-v4 schema bump 정합 cross-ref)
  - ADR-058   # is_transitional + 해소 기준 의무 (false 정합)
related_files:
  - docs/orchestrator-playbook.md   # §6.10 Mechanical fast-path (R11) — 현 inline SSOT, 본 ADR 이 ADR-level 절차 anchor 로 승격
  - docs/adr/ADR-RESERVATION.md     # row 83 (CFP-665) — Proposed 단계, GitOpsAgent reserve 후 active 전환
  - docs/adr/ADR-067-fix-ledger-implementability-escalation.md   # §10 카운터 / RESET 경계 cross-ref
is_transitional: false
mechanical_enforcement_actions: []
# Proposed 단계 — mechanical enforcement action 미선언 (behavioral procedure SSOT anchor only).
# Accepted 전환 + actual lint/workflow wire 는 후속 carrier (Change Plan §3 SSOT). ADR-070 §D5
# declaration-only retain / ADR-082 Wave 1 `mechanical_enforcement_actions: []` known-limitation 선례 정합.
sunset_justification: "N/A — permanent process policy (Proposed). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과 예정. ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — fast-path 자격 subset 축소 / Orchestrator direct-commit 권한 확대 약화 금지). is_transitional: false."
---

# ADR-083: Mechanical fast-path — Orchestrator direct-commit 권한 + FIX iteration 비소비 경계 + same-iteration internal verify 절차

## 상태

`Proposed` (2026-05-18). proposer = PMOAgent (ADR-045 Amendment 5 §D-9 cross-Story pattern threshold N=2 REACHED — mandatory ADR trigger, forcing function). author = ArchitectAgent (codeforge-design chief author). carrier_story = CFP-665.

본 ADR 은 검토용 draft 다 (Accepted/enacted 아님). codeforge orchestrator framework 자체를 규율하므로 draft-for-review posture 가 적절하다. 본 author 는 verdict 권한을 보유하나 (Accepted | Rejected 결론 가능), 증거가 결정적이지 않은 한 **Proposed 를 default 로 유지**한다 — §verdict 참조.

## 본질 선언

Mechanical fast-path (CFP-19 R11) 은 review iteration 의 mechanical-category finding 을 정상 FIX cycle (parallel diagnosis + FIX iteration counter 소비 + §10 FIX Ledger row append) 없이 Orchestrator direct-commit + same-iteration internal verify 로 처리하는 경로다. 본 경로의 **적용 조건 / Orchestrator 권한 경계 / FIX-counter 소비 경계 / §10 append 정책**이 정합하게 codify 되지 않으면, 아래 §결정 mechanism 을 몇 개 쌓든 의미 없다 — fast-path 가 logic/data-safety 변경을 silent 하게 흡수하거나 (FIX budget 회계 왜곡), 반대로 mechanical 변경을 과도하게 FIX iteration 으로 escalate (budget 낭비) 하는 양방향 결함의 원인이 된다.

## 컨텍스트

### Cross-Story pattern corpus (N=2 — ADR-045 Amendment 5 §D-9 정량 임계값)

| # | Story | fast-path 사례 | mechanical_category | FIX iteration 소비 | §10 row append | Resolution | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | U2-HELPER (mctrader-data#88) | CodeReview iter 2 — DeveloperPL `__all__` extension 새 P1 → `test_public_surface` CI fail | minor (symbol-export) | 비소비 | 0 | Orchestrator direct commit + code-review iter 2 내부 verify (Option A) | U2-HELPER retro §1 line 37 / §3.2 Candidate 2 (emit_condition pre-registered) |
| 2 | U3-MIGRATE (mctrader-data#89) | pyright type errors (moto 5.x `mock_aws` + `importlib.util` + spec None guard) | minor (type-only) | 비소비 | 0 | mechanical fix + CI re-verify (CFP-19 R11) | U3-MIGRATE retro §1 line 40 / §2.2 (Pattern H N=2) / Orchestrator LAND comment #89 (`fast_path: pyright FIX 비소비`) |

두 sample 공통: `mechanical_category` fast-path 로서 적용 조건 / Orchestrator 권한 / FIX-counter 소비 경계가 **CFP-19 R11 inline 언급에만 머물고 정식 ADR-level 절차 SSOT 부재**.

PMOAgent ADR-045 Amendment 5 §D-9 정량 임계값: cumulative_n **2** ≥ threshold 2 → `cross_story_pattern_adr_trigger.triggered: true` + `escalation_action: adr_draft_emitted` (forcing function — PMOAgent self-decide 영역 제거). carrier_source = U2-HELPER retro §3.2 Candidate 2 (`emit_condition: "동일 mechanical_category fast-path 패턴 재발 시 즉시 발의"` pre-registered, N=1 carrier → U3-MIGRATE pyright 으로 N=2 reach).

> **defect/process-mechanism semantics 판정 (PMO §2.2 verbatim)**: 본 패턴은 단순 git hygiene 가 아니라 "FIX iteration counter 소비 경계 + Orchestrator direct-commit 권한 + same-iteration internal verify 절차" 의 **process-mechanism SSOT 부재** 신호다. U3-MIGRATE retro §2.7 의 N=2 도달 비-trigger 패턴 (C/D/F/I/L — positive signal / structural carrier / 확립 절차 successful application) 과 disjoint — Pattern H 만 §D-9 "design-guidance absence" semantics 충족 → mandatory ADR trigger.

### 현 SSOT 결격 영역

- **CFP-19 R11 inline 언급** = `docs/orchestrator-playbook.md §6.10 Mechanical fast-path (R11)` 가 자격 조건 / 절차 4-step / 보안 lane 제약을 기술하나, 이는 **playbook 절(section) 수준 운영 지침**이지 ADR-level decision SSOT 아님 (verified-via: `Read docs/orchestrator-playbook.md:2239-2253` working tree 2026-05-18). §6.10 step 4 (`§10 ledger 신규 row 안 매김`) 가 FIX-counter 비소비 경계의 유일한 1줄 — logic/data-safety 변경 ineligibility 명문 부재.
- **`mechanical_category` enum SSOT** = `codeforge-review:templates/review-pl-base.md §3 R11` (`typo / broken-link / minor-naming / comment-only / none`, verified-via: `docs/orchestrator-playbook.md:2241` cross-ref 2026-05-18). 어느 subset 이 fast-path 적격인지 / type-only·symbol-export 신규 mechanical_category 가 enum 에 포함되는지 ADR-level 경계 부재.
- **Orchestrator direct-commit 권한** = §6.10 step 1-2 가 "Orchestrator 가 §6.6 parallel diagnosis 건너뛰고 DeveloperPL 직접 spawn" 으로 기술하나, U2-HELPER sample 1 = DeveloperPL **재spawn 없이** Orchestrator direct commit (retro §1 line 37). §6.10 절차와 실 사례 사이 micro-gap — DeveloperPL re-spawn 회피가 허용되는 정확한 조건 ADR-level 부재.
- **ADR-067** = fix-ledger implementability escalation + max FIX overflow (§결정 1 max FIX 3/3 reassessment / §결정 3 RESET vs escalation) — FIX iteration **소비** 후의 escalation 처리 한정. fast-path 의 FIX iteration **비소비** 경계는 ADR-067 scope 외 (보완 관계, disjoint).
- **ADR-054** = doc-only Story fast-path 분류 표 — Story 진입 단계의 lane 단축 분류. review iteration 내부의 mechanical finding fast-path 와 disjoint mechanism (별 axis).

## 결정

> 본 §결정 은 Proposed draft 다. Accepted 전환 시 codeforge orchestrator framework 의 review-iteration FIX cycle SSOT 가 된다.

### §결정 1 — `mechanical_category` enum + fast-path 적격 subset SSOT

`mechanical_category` enum 의 canonical SSOT 는 `codeforge-review:templates/review-pl-base.md §3 R11` 절이다 (본 ADR 은 해당 enum 을 재정의하지 않고 ADR-level 적격 경계만 anchor — over-codification 회피).

| mechanical_category | 정의 | fast-path 적격 |
|---|---|---|
| `typo` | 철자 / 오탈자 정정 (behavioral change 0) | YES |
| `broken-link` | dead link / path 정정 (behavioral change 0) | YES |
| `minor-naming` | symbol / identifier / wording 정정 (behavioral change 0) | YES |
| `comment-only` | 주석 / docstring only (behavioral change 0) | YES |
| `symbol-export` | `__all__` / public surface enumeration 정정 (behavioral change 0 — U2-HELPER sample 1) | YES |
| `type-only` | type annotation / type-checker (pyright/mypy) 정정 (runtime behavioral change 0 — U3-MIGRATE sample 2) | YES |
| `none` | 위 어디에도 미해당 (logic / data-safety / security / contract 변경) | **NO** |

> **enum 확장 경계**: `symbol-export` / `type-only` 는 corpus N=2 가 실증한 신규 mechanical_category. 본 표는 U2/U3 sample 의 실제 분류를 ADR-level 로 박제한다. enum subset 확장 (신규 mechanical_category 추가) 시 별 CFP carrier 의무 — `codeforge-review:templates/review-pl-base.md §3 R11` SSOT 와 본 표 동시 갱신 cascade (drift 차단). subset 축소 (적격 → 비적격 강등) = 강화 방향 (top-down ratchet 정합), 자유롭게 가능.

### §결정 2 — fast-path FIX-iteration counter 비소비 조건

fast-path 자격 = `mechanical_category != none` AND **no-behavioral-change** AND `(severity = P2 OR (severity = P1 AND 영향 파일 수 = 1))` (CFP-19 R11 자격 조건 verbatim 보존 + no-behavioral-change 명문 추가).

| 조건 | 적격 (FIX iteration 비소비) | 비적격 (정상 FIX cycle, counter 소비) |
|---|---|---|
| no-behavioral-change | YES — runtime behavior / data semantic / contract 불변 (symbol-export / type-only / typo / comment-only / broken-link / minor-naming) | — |
| logic change | — | NO — runtime behavior 변경 (조건 분기 / 알고리즘 / 상태 전이) |
| data-safety change | — | NO — data 무결성 / 손실 / idempotency / migration 영향 (U3-MIGRATE P0-1 `both_head_404` 류는 fast-path 절대 비적격 — 정상 FIX cycle) |
| security / contract change | — | NO — injection / credential / CVE / trust-boundary / inter-plugin contract 변경 (보안 lane = §결정 4 항상 `none`) |

**핵심 invariant**: logic 또는 data-safety 변경이 fast-path 로 흡수되면 FIX budget 회계가 왜곡되고 (ADR-067 max FIX 3/3 reassessment trigger 우회), data-safety 결함이 §10 audit trail 없이 silent merge 될 수 있다. no-behavioral-change 가 비소비의 **필요조건**이다 — 의심 시 fast-path 비적격 (정상 FIX cycle, fail-safe 방향).

### §결정 3 — Orchestrator direct-commit 권한 경계 + same-iteration internal verify 절차

#### 3.1 권한 경계 (DeveloperPL re-spawn 회피 조건)

| 상황 | Orchestrator 절차 |
|---|---|
| review iteration 이 mechanical finding 자체 검출 (§결정 1 적격 + §결정 2 비적격 조건 미해당) | §6.10 step 1-2 — Orchestrator 가 §6.6 parallel diagnosis 건너뛰고 DeveloperPL fix-only 모드 직접 spawn → DeveloperPL fix commit |
| fix 적용 후 **새 mechanical-only side-effect** (예: U2-HELPER `__all__` extension → `test_public_surface` CI fail) — single-file, no-behavioral-change, P1 영향 파일 1 | Orchestrator **direct commit** (DeveloperPL 재spawn 회피) — side-effect 가 §결정 1 적격 + §결정 2 비적격 조건 미해당 + 기계적 일관성 정정 (CI gate 가 deterministic verify channel) 일 때 한정 |
| side-effect 가 logic/data-safety/contract 변경 또는 multi-file 또는 분류 불확실 | direct commit 금지 — 정상 §6.6 parallel diagnosis cycle (FIX iteration counter 소비) |

> Orchestrator direct-commit 권한은 **deterministic verify channel (CI/pytest gate) 가 side-effect 의 mechanical 정합성을 객관 검증 가능할 때**로 한정한다. PL adjudication 우선 원칙 (ADR-022 Deprecated — Sonnet decider 무효, PL = adjudicator) 정합 — fast-path 적격/비적격 최종 판정 주체는 ReviewPL (verdict packet `mechanical_category` 필드). Orchestrator 는 ReviewPL verdict 를 집행할 뿐 자체 분류 권한 보유 아님.

#### 3.2 same-iteration internal verify 절차 (CFP-19 R11 step 3 확장)

1. fix commit 후 **CI/pytest re-run** — 동일 finding 검출 안 됨 + CI green 확인 (deterministic channel)
2. **line-level grep audit** — fix 가 의도한 line 범위만 touch, no-behavioral-change invariant 위반 0 확인 (U2-HELPER retro §1 "empirical line-level grep audit" 박제 패턴 verbatim)
3. 다음 review iteration 이 동일 finding 재검출 시 → fast-path 자격 미충족/분류 잘못 판정 → **정상 §6.6 cycle 회복** (Iter row append, FIX iteration counter 소비 — CFP-19 R11 `자격 미충족` 분기 verbatim 보존)
4. 다음 review iteration 이 P0/P1 신규 검출 (mechanical 외) 시 → 정상 §6.6 cycle (fast-path 무관)

same-iteration internal verify = fast-path 의 **회계 safety net**. verify 통과 = FIX iteration 비소비 확정. verify 실패 = 정상 cycle 강등 (counter 소비 회복) — fast-path 가 결함을 silent skip 하지 않도록 보장하는 forcing function.

### §결정 4 — §10 FIX Ledger append 정책 (fast-path = row append 0, audit trail 별도 표기)

| 경로 | §10 FIX Ledger | audit trail |
|---|---|---|
| fast-path 자격 충족 + same-iteration internal verify PASS | **row append 0** (FIX iteration counter 증가 0) | Story §10 외 별도 표기 — Orchestrator LAND comment 또는 retro §1 quality gate 표에 `fast-path (mechanical) — FIX iteration 비소비, §10 row append 0` 명시 (U3-MIGRATE retro §1 line 40 / Orchestrator LAND comment #89 `fast_path: pyright FIX 비소비` 박제 형식) |
| fast-path 자격 미충족 / internal verify FAIL → 정상 §6.6 cycle 강등 | row append (정상 FIX iteration — Orchestrator monopoly, fix-event-v1 contract) | Story §10 FIX Ledger row (정상 회계) |

**§10 monopoly 보존**: Story §10 FIX Ledger append 는 Orchestrator monopoly (fix-event-v1 contract, ADR-067 cross-ref). fast-path 의 row append 0 는 §10 monopoly 우회가 아니라 — fast-path 가 정의상 FIX iteration 이 아니므로 ledger event 자체가 비발생. audit trail 은 §10 외 채널 (LAND comment / retro) 에 명시적 박제 의무 (silent skip 차단 — observability 보존).

**ADR-067 경계 disjoint**: ADR-067 §결정 1 (max FIX 3/3 reassessment) + §결정 3 (RESET vs escalation) 은 FIX iteration **소비** 후 overflow 처리. fast-path 비소비는 ADR-067 trigger 에 영향 0 (counter 증가 0 → reassessment trigger 무관). 보완 관계, 충돌 0.

### §결정 5 — review-verdict-v4 schema 영향 (Proposed 단계 — 미확정)

본 ADR Proposed 단계에서는 review-verdict-v4 schema 변경을 **선언만** 하고 actual bump 는 Accepted 전환 + 후속 carrier (Change Plan §3 SSOT) 로 defer 한다. 후보 (Accepted 시 결정):

- ReviewPL verdict packet `mechanical_category` 필드는 이미 존재 (CFP-19 R11) — 신규 필드 불요 가능성.
- fast-path 비소비 explicit marker (`fast_path_applied: bool` 또는 동등) 신규 필드 도입 시 = ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump + sibling sync (canonical = `plugin-codeforge-review`).
- ADR-070 §D5 declaration-only retain / ADR-082 Wave 1 `mechanical_enforcement_actions: []` known-limitation 선례 정합 — Proposed 단계 = behavioral procedure SSOT anchor only, mechanical enforcement action 미선언.

### §결정 6 — scope 경계 (out-of-scope 명시)

- **ADR-054 doc-only Story fast-path** = Story 진입 단계 lane 단축 분류 — review iteration 내부 mechanical finding fast-path 와 disjoint mechanism. 본 ADR scope 외 (별 axis, ADR-054 SSOT 유지).
- **보안 lane mechanical_category** = injection / credential / CVE / trust-boundary 는 항상 `mechanical_category = none` (CFP-19 R11 제약 verbatim 보존) — fast-path 자격 영구 부재. U3-MIGRATE SEC-P1-1 (trust-boundary) / P0-1 (data-loss) 는 정상 FIX cycle (retro §1 박제). 본 ADR §결정 1 표 `none` row 가 명문.
- **mechanical_category enum 재정의** = `codeforge-review:templates/review-pl-base.md §3 R11` SSOT 유지. 본 ADR 은 적격 subset 경계만 anchor (enum 자체 재정의 아님 — over-codification / SSOT 분절 회피).

## 결과

본 ADR (Accepted 시) codify 결과:

- CFP-19 R11 inline 언급 (orchestrator-playbook §6.10) → ADR-level 절차/권한/회계 SSOT 승격. §6.10 = 본 ADR 의 운영 절차 mirror (cross-ref).
- §결정 1 mechanical_category 적격 subset 표 (corpus N=2 가 실증한 `symbol-export` / `type-only` 박제) — `codeforge-review §3 R11` SSOT 와 cascade 동기.
- §결정 2 no-behavioral-change = FIX-counter 비소비 필요조건 — logic/data-safety silent 흡수 차단 (FIX budget 회계 무결성 보존).
- §결정 3 Orchestrator direct-commit 권한 = deterministic verify channel 한정 + PL adjudication 우선 (ADR-022 Deprecated 정합) + same-iteration internal verify 절차 (CI re-run + line-level grep audit).
- §결정 4 §10 row append 0 + audit trail 별도 표기 의무 (silent skip 차단, §10 monopoly 보존, ADR-067 disjoint).
- ADR-067 (FIX 소비 후 overflow) + ADR-054 (Story 진입 분류) disjoint 보완 layer 신설 — review-iteration mechanical fast-path 회계 경계.
- 본 carrier 자체 = PMOAgent ADR-045 Amendment 5 §D-9 cross_story_pattern_adr_trigger pattern_count 2 ≥ threshold 2 forcing function 산물 (escalation_action `adr_draft_emitted`).

### 부정적 결과 / Trade-off

- Orchestrator / ReviewPL 의 fast-path 적격 판정 단계 추가 (no-behavioral-change 평가 overhead) vs logic/data-safety silent 흡수로 인한 production data-loss 위험 차단 (U3-MIGRATE P0-1 류).
- §결정 1 enum subset 표 ↔ `codeforge-review §3 R11` SSOT cascade 동기 의무 (drift 시 fast-path 자격 판정 silent drift) — manual cascade review 의존 (자동 cascade lint 신설 = 별 후속 CFP, ADR-065 row 8 cascade obligation 패턴 정합).
- review-verdict-v4 schema 변경 (Accepted 시 §결정 5) → sibling sync PR 의무 (canonical = `plugin-codeforge-review`).

## 거절된 대안

- **(D-A) CFP-19 R11 playbook §6.10 inline 유지 (ADR 미신설)** — cross-Story N=2 reach 가 process-mechanism SSOT 부재를 실증 (ADR-045 §D-9 forcing function). inline 운영 지침은 적용 조건/권한/회계 경계의 normative SSOT 가 아니어서 양방향 결함 (logic silent 흡수 / mechanical 과escalate) 반복 → §결정 1-4 ADR-level anchor.
- **(D-B) `mechanical_category` enum 을 본 ADR 에서 재정의** — `codeforge-review:templates/review-pl-base.md §3 R11` SSOT 분절 → §결정 1 = 적격 subset 경계만 anchor (enum 재정의 회피, SSOT 단일성 보존).
- **(D-C) FIX-counter 비소비를 mechanical_category 만으로 판정 (no-behavioral-change 조건 생략)** — logic/data-safety 변경이 mechanical_category 오분류로 fast-path 흡수 시 §10 audit trail 없이 silent merge (U3-MIGRATE P0-1 data-loss 류 위험) → §결정 2 no-behavioral-change = 필요조건 명문.
- **(D-D) ADR-067 에 fast-path 비소비 경계 흡수 (Amendment)** — ADR-067 = FIX iteration 소비 후 overflow/RESET 한정 (disjoint scope). fast-path 비소비 흡수 시 ADR-067 anchor 가 소비/비소비 양 axis 로 분절 → 본 ADR 독립 anchor (ADR-067 보완 cross-ref only).
- **(D-E) Proposed 단계에서 review-verdict-v4 schema 즉시 bump** — schema 변경은 사용자 가치 판단 + sibling sync 동반 (ADR-008 / ADR-010). Proposed draft 단계 = behavioral procedure SSOT anchor only, schema bump = Accepted 전환 + 후속 carrier (Change Plan §3 SSOT) → §결정 5 defer.

## 관련 ADR

- **ADR-045** §D-9 cross_story_pattern_adr_trigger: 본 carrier = §D Mandatory escalation 산물 (pattern_count 2 ≥ threshold 2, escalation_action `adr_draft_emitted`). 보완 관계, 충돌 0.
- **ADR-067** fix-ledger implementability escalation + max FIX overflow: §결정 1 (max FIX 3/3 reassessment) + §결정 3 (RESET vs escalation) = FIX iteration 소비 후 한정. 본 ADR = 비소비 경계. disjoint 보완, 충돌 0.
- **ADR-065** ArchitectAgent Phase 1 mechanical self-check: design lane Phase 1 산출물 commit-time mechanical sync — 본 ADR = review-iteration mechanical finding fast-path. 인접 영역, disjoint, 충돌 0.
- **ADR-054** doc-only Story fast-path: Story 진입 lane 단축 분류 — 본 ADR = review iteration 내부 fast-path. 별 axis disjoint, 충돌 0.
- **ADR-022** Sonnet review-verdict decider (Deprecated, CFP-134/ADR-035): fast-path 적격 최종 판정 주체 = ReviewPL (PL = adjudicator, Sonnet decider 무효). §결정 3 정합.
- **ADR-008** inter-plugin contract versioning: §결정 5 review-verdict-v4 schema 변경 시 MINOR bump 정합 cross-ref. 충돌 0.
- **ADR-058** is_transitional + 해소 기준 의무: `is_transitional: false` 정합 (permanent process policy). 충돌 0.

## 관련 파일

- `docs/orchestrator-playbook.md` — §6.10 Mechanical fast-path (R11) — 현 inline SSOT, 본 ADR Accepted 시 ADR-level 절차 anchor 로 승격 (§6.10 = mirror cross-ref)
- `docs/adr/ADR-RESERVATION.md` — row 83 (CFP-665) — Proposed 단계 (GitOpsAgent reserve → Accepted 전환 시 active)
- `docs/adr/ADR-067-fix-ledger-implementability-escalation.md` — §10 카운터 / RESET 경계 disjoint cross-ref
- `codeforge-review:templates/review-pl-base.md` — §3 R11 `mechanical_category` enum SSOT (본 ADR §결정 1 적격 subset cascade 동기 대상)
- 출처 retro: `mctrader-data:docs/retros/U2-HELPER-retro-2026-05-18.md` §3.2 Candidate 2 (N=1 carrier) / `mctrader-data:docs/retros/U3-MIGRATE-retro-2026-05-18.md` §2.2 / §3.1 (N=2 reach, adr_candidate 페이로드)

## 해소 기준

N/A — permanent process policy (Proposed 단계). Accepted 전환 시 ADR-064 §self-application top-down ratchet 정합 (강화 방향만 — fast-path 적격 subset 축소 / no-behavioral-change 조건 강화 / Orchestrator direct-commit 권한 축소 = 허용. 적격 subset 확대 / no-behavioral-change 조건 완화 / direct-commit 권한 확대 약화 = ADR-058 §결정 5 약화 방향 발의 차단). `is_transitional: false` (영구 정책).
