---
adr_number: 77
title: Clarification 강제 재조사 전파 정책 SSOT
status: Active
category: governance
date: 2026-05-16
is_transitional: false
carrier_story: CFP-759
parent_epic: CFP-755
supersedes: []
amends: []
amendment_log: []
related_stories:
  - CFP-759  # 본 Story carrier — Story-1 (ADR-077 신설 + RESERVATION row 77 reserved→active)
  - CFP-755  # Epic A anchor (요구사항 clarification 강제 재조사 전파)
related_adrs:
  - ADR-039  # Orchestrator subagent default — env=0 재조사 fan-out 은 Orchestrator round-trip (재귀 spawn 금지). §결정 9 deferred spawn cost risk 부분 충당 (inherit-not-resolve)
  - ADR-044  # Phase-scoped sequential team — env=1 시 SendMessage fan-out, §결정 8 env-equality protocol invariant 무손상 (envelope env-invariant 단일값)
  - ADR-045  # PMO retro mandatory trigger — 조건부 PMO 합류 trigger 와 retro trigger origin disjoint
  - ADR-052  # Codex proactive Touchpoint — Amendment 1/3 (Touchpoint #4 RequirementsPL multi-round debate + fact-check marker 4종). trigger origin disjoint (Codex divergence vs 사용자 답변)
  - ADR-056  # 합성 순서 (§5 Analyst → §2 Domain → §6 Researcher → PL) — 재조사 후 PL 재종합 정합
  - ADR-058  # ADR sunset criteria mandate — is_transitional:false 정합 (§해소 기준 N/A permanent), §결정 5 sunset_justification ratchet 차단
  - ADR-059  # debate-protocol-v1 — 재조사 카운터 ↔ debate round counter disjoint, max-round 5 선례 (재조사 카운터 cap 정합)
  - ADR-064  # Decision principle mandate — §결정 4 parallel default + sequential 3 사유, §결정 1 forbid-list (모달 어휘 금지)
  - ADR-067  # FIX ledger RESET + cross-lane 합산 금지 — 재조사 카운터 ↔ §10 FIX Ledger disjoint hard constraint 선례
  - ADR-076  # 선언적 reconciliation upgrade — §결정 4 RESET disjoint layer invariant N-layer 확장 패턴 재사용 (stale 게이트 declarative reconciliation 정식화)
  - ADR-031  # Lane-spawn evidence — 재조사 fan-out 도 §14 Lane Evidence row 대상 (§결정 10 cross-ref)
  - ADR-013  # dogfood-out — Story file = internal-docs wrapper/stories/CFP-759.md
  - ADR-054  # doc-only fast-path — Story-1 = 신규 ADR 도입 → full-lane 강제 (fast-path 제외)
related_files:
  - docs/adr/ADR-RESERVATION.md  # row 77 reserved→active 전환 (본 Story-1 Phase 1 PR)
  - docs/orchestrator-playbook.md  # §2.2/§4.4 amend 방향 선언만 (본문 amend = Story-2)
  - CLAUDE.md  # 요구사항 레인·FIX 루프·PMO 비개입 단락 cross-ref (본문 갱신 = Story-2)
  - docs/inter-plugin-contracts/requirements-output-v1.md  # 재조사 카운터 schema (contract bump = Story-4)
  - templates/team-spec-requirements.yaml  # 조건부 PMO conditional teammate entry (변경 = Story-3)
  - docs/domain-knowledge/domain/requirements-discipline/clarification-mandatory-recheck-propagation.md  # domain narrative (DomainAgent self-write, CFP-759)
  - docs/domain-knowledge/concept/clarification-driven-reinvestigation.md  # concept narrative (ResearcherAgent self-write, CFP-759)
  - docs/evidence-checks-registry.yaml  # adr-077-ratchet-declared / adr-077-design-reading-mandate-declared (registry row append = Story-3, ADR frontmatter 는 declare)
mechanical_enforcement_actions:
  - action: adr-077-ratchet-declared
    status: Active
    progress_note: "CFP-848 Story-5 Phase 2 carrier (2026-05-17 KST) — deferred-followup → Active 전환. lint script (check-adr-077-ratchet.sh / check_adr_077_ratchet.py) + workflow (adr-077-ratchet-declared.yml) 이미 CFP-785 Phase 2 에서 land 완료. evidence-checks-registry detect_command + status 전이 동반. hotfix-bypass:adr-077-ratchet label-registry-v2 v2.22 기 append."
    target_section: §결정 9
  - action: adr-077-design-reading-mandate-declared
    status: Active
    progress_note: "CFP-848 Story-5 Phase 2 carrier (2026-05-17 KST) — deferred-followup → Active 전환. lint script (check-adr-077-design-reading-mandate.sh / check_adr_077_design_reading_mandate.py) + workflow (adr-077-design-reading-mandate-declared.yml) 이미 CFP-785 Phase 2 에서 land 완료. evidence-checks-registry detect_command + status 전이 동반. hotfix-bypass:adr-077-design-reading label-registry-v2 v2.22 기 append."
    target_section: §결정 3
# Story-1 scope = ADR 본문 신설 + RESERVATION row 77 전이만. mechanical lint wire = Story-3
# (evidence-checks-registry row append + workflow). ADR-040 Amendment 3 §결정 7.D self-application
# invariant 정합 — declarative governance ADR 의 mechanical action 은 deferred-followup status 로
# declare (registry entry 부재 시점 valid declaration, ADR-068 mechanical_enforcement_actions
# deferred-followup 선례 동형).
---

# ADR-077: Clarification 강제 재조사 전파 정책 SSOT

## 상태

**Active (2026-05-16)** — CFP-759 (Epic A #755 Story-1) carrier. RESERVATION row 77 `reserved → active` 전환 동반 (본 Story-1 Phase 1 PR).

`is_transitional: false` — permanent governance invariant. 요구사항 레인 clarification 강제 재조사 전파 도메인의 normative SSOT. codeforge 가 deprecate 되지 않는 한 영구 유효. 안전망 ADR 아님 (ADR-058 §결정 7 default presumption `false` 가 아닌 governance carrier 영구 정책 — §해소 기준 N/A 1줄 면제 영역).

## 컨텍스트

### 직접 동인 (CFP-755 Epic A §1 brainstorm 수렴 verbatim)

사용자 directive (Epic A brainstorm 수렴 원문, Story-1 §1 verbatim):

> "강제적으로 수행하라" — 사용자 답변 시 조건·판단 게이트 폐기. 정상적 scope 정교화 과정에서 누락·재발명·stale 설계 진입을 차단하는 것이 목표.

clarification("사용자 확인 필요") 질문에 대한 답변은 **요구사항 입력의 정의상 변경**이다. clarification 답변 = scope 정교화이며 정상 forward 진행이지 결함이 아니다. 따라서 "변화가 있었는지 판단 후 재조사" 형태의 게이트는 도메인 오류 (false dichotomy) — 답변이 들어왔다는 사실 자체가 입력 변경이므로 변화 유무를 다시 판정하는 분기는 자기 모순. 게이트 없는 무조건 전파가 도메인 정합 (Story-1 §2.1 DomainAgent 판정 `[verified — §1 verbatim "강제적으로 수행하라" + brainstorm 수렴 6항 §1번]`).

### 근본 WHY (Story-1 §5.1)

**설계가 요구 변경에 미추적 (under-tracking) 되는 손실 차단.** clarification 답변 (= 요구 입력 변경) 이 들어왔는데 설계 baseline 이 갱신 안 된 채 phase:설계 진입하면 (a) 누락 (설계가 변경 미반영) (b) 재발명 (이미 결정된 것 재논의) (c) stale 설계 진입 (ArchitectAgent 가 outdated 조사로 설계) 3 손실 발생. 무조건 재조사 + stale 게이트 = 이 3 손실의 forcing function.

### 도메인 갭 (Story-1 §2.5 / §4.2 / §6.3 — 본 ADR 영역으로 위임된 결정)

요구사항 레인이 "이 결정이 필요하다"는 요구만 명세하고 본 ADR 정책 본문으로 위임한 결정 영역:

- "범위를 바꾸는 답변"의 mechanical 판정 기준 (단순 확인 / scope 정교화 / Epic 구조 변경 disambiguation — Story-1 E-1 거짓양성 차단)
- 안전 envelope 정량값 (burst window debounce / max-wait ceiling / 재조사 카운터 상한)
- stale recovery 기준 (stale 마킹 해제 = 재조사 완료 판정)
- PMO 합류 closed enumeration + ADR-045 disjoint
- design-reading mandate 세부 깊이·산출 형식
- Touchpoint #4 재트리거 boundary + 3 카운터 disjoint 보장

### 본 ADR 영역 (Story-1 scope 경계)

본 ADR = ADR-077 본문 신설 + RESERVATION row 77 `reserved → active` 전환 **만**. playbook §2.2/§4.4 본문 amend / CLAUDE.md 본문 갱신 / lane plugin 행동 / inter-plugin contract bump = Story-2~5 carrier. 본 ADR 은 후속 Story 에 "방향 선언 + cross-ref" 만 제공 (Story-1 §3 / §4.1 Story-2~5 경계표 정합).

## 결정

> 6 SubAgent (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch) 산출 dedup·상충 조정 후 §결정 1-10 으로 본문화. 정량값·invariant·disjoint·cross-ref 전부 본문 고정. envelope threshold 등 모든 한계 표현은 ADR-064 §결정 1 forbid-list (모달/주관 어휘) 회피 — rate/count 정량값 의무.

### 결정 1 — 무조건 트리거 (조건 게이트 폐기 + value-equality skip 비차용 invariant)

요구사항 단계에서 사용자가 clarification 질문에 답할 **때마다**, 판단 게이트 없이 강제로 재조사 발동한다. 기존 "PL 1개만 재스폰 + 서브에이전트 재조사는 PL 재량 / 변화없음 → 통합만" 분기를 폐기한다.

- **trigger semantics**: clarification 답변 수령 = dirty 이벤트. **value-equality skip 비차용 invariant** — 답변 내용이 이전과 의미상 동치여도 dirty 전파를 skip 하지 않는다 (Researcher §6.1 개념-1 event-driven invalidation 외부 anchor + §2.1 도메인 정합, multi-source 병합). dirty 전파의 값 무관성 (value-independent) 은 normative invariant — "값이 같으면 skip" 분기를 ADR-077 정책에서 도입 금지.
- **gate 폐기 범위**: PL 재량 판단 분기 + "변화없음 → 통합만" 분기 양쪽 모두 폐기. trigger 조건을 PL재량 → clarification-answer-driven 으로 치환 (playbook §4.4 trigger semantics amend 방향 — 본문 amend = Story-2).
- **disjoint 경계**: 본 trigger 는 사용자 clarification 답변 origin 전용. Codex divergence-driven RequirementsPL redo (ADR-052 Amendment 1 A4) 와 trigger origin disjoint (§결정 7 참조).

### 결정 2 — fan-out 멤버 6 permanent + 조건부 PMO (§272 흡수, 대체 아님)

clarification 답변 수령 시 항상 다음 6 sub-agent fan-out:

- DomainAgent (§2) + RequirementsAnalyst (§5) + Researcher (§6) — 요건 종합 3
- FeasibilityAgent (§4.2) + ContinuityAgent (§4.3) + ChangeImpactAgent (§4.1) — design-reading 3

**조건부 가산**: 답변 영향이 Epic/Story 구조까지 도달하면 PMOAgent 도 합류 (재분해).

- **§272 흡수 (Refactor decoupling 채택)**: 기존 playbook §2.2 표 L272 "요구사항 범위·우선순위 변경 → Orchestrator 자체 → Story 재분해" 단일 행은 **흡수 (absorb) 되며 대체 (replace) 아님**. playbook §2.2 표 행은 **유지** (삭제 아님) — "Story 재분해" invariant 의미 보존. 본 ADR §결정 2 가 trigger SSOT cross-ref 가 되고, playbook §2.2 표 본문 amend (cross-ref 하위화 형태) = Story-2 carrier. SSOT 의미 손상 최소화가 cross-ref 하위화 형태 선택의 근거.
- **contrapositive invariant**: "PMO 합류 미발동 = Epic 구조 무변경" — 이 역명제가 closed enumeration 의 mechanical 판정 anchor. 어떤 clarification 유형이 PMO trigger 인가의 closed enumeration = P-5 (결정 4 정량 표 참조).
- **interface (Refactor 채택)**: team-spec-requirements.yaml 의 PMOAgent 표현 = `spawn_mode: conditional` + `activation_condition` (closed enum key) + `contrapositive_invariant` 필드. team-spec yaml 변경 자체 = Story-3 carrier. 본 §결정 2 = P-5 closed enum SSOT.
- **ADR-045 disjoint**: 조건부 PMO 합류 trigger (Epic 구조 변경) ↔ ADR-045 PMO retro mandatory trigger (Phase 2 PR merge 후 5분 grace) = trigger origin disjoint. 동일 PMOAgent 의 서로 다른 spawn 진입 — 합류 fan-out 은 retro 가 아님.

### 결정 3 — design-reading mandate 심화 (skim 금지 + 설계 의도/근거 파악, AC-7 수용 조건)

design-reading 에이전트 (FeasibilityAgent / ContinuityAgent / ChangeImpactAgent) 의 mandate 를 "문서 skim" 에서 **"설계 의도/근거 파악"** 으로 심화한다 (normative §결정).

- **normative 선언 (AC-7 수용 조건 충족)**: design-reading 3 agent 는 이전 Story 설계 산출물 (§7 등) 및 관련 ADR 을 **skim 금지** — 설계 결정의 의도 (왜 그 선택을 했는가) 와 근거 (어떤 제약/trade-off 가 작동했는가) 수준으로 읽는다. 단순 존재/제목 확인 (skim) 으로 갈음 금지.
- **적용 3 agent 명시 (TestContractArch grep-testable 채택)**: FeasibilityAgent (§4.2 아키텍처 장벽 파악) / ContinuityAgent (§4.3 이전 결정 연속성) / ChangeImpactAgent (§4.1 변경 델타) — 3 agent verbatim 명시. mechanical lint = `adr-077-design-reading-mandate-declared` (grep-testable: 본 §결정 3 "skim 금지 + 의도/근거 파악" 선언 + 적용 3 agent 명시 존재, frontmatter declare, registry row append = Story-3).
- **위임 경계**: skim → 의도 파악의 mechanical 판정 기준·깊이 수치·산출 형식 = P-6 (설계 lane 후속 위임 유지). Epic B (#756 architecture doc) 는 design-reading 충분성 enabler (soft 의존, blocking 아님) — Epic B 부재 시 degrade path = P-6 영역. 본 §결정 3 = "normative 선언 포함" 자체를 AC-7 수용 조건으로 고정 (Story-1 §5.4 AC-7 정합).

### 결정 4 — 안전 envelope (3 sub-mechanism + 정량값, OpRiskArch 채택)

답변 burst → PL 재종합 1사이클 coalesce → 단일 fan-out 으로 backpressure 를 가한다. envelope = 3 sub-mechanism + 정량값:

| 파라미터 | 정량값 (단위) | empirical_source | 근거 |
|---|---|---|---|
| P-1 debounce | `90` (s, latency) | `[empirical-source: TBD]` (wiretap required — Story-3 §8.3 Perf Baseline 실측 carry. ADR-077 신설 시점 라이브 telemetry 부재 — governance default, 실측 후 ratchet) | OpRiskArch — 답변 burst coalesce window. debounce 후 단일 fan-out |
| P-1 max_wait_ceiling | `600` (s = 10min, latency) | `[empirical-source: TBD]` (wiretap required — Story-3 §8.3 carry) | OpRiskArch — debounce 무한 연장 차단 상한. ceiling 도달 시 강제 fan-out |
| P-1 coalesce 단위 | `1` (fan-out per window, count) | `[empirical-source: derived]` (mechanism invariant — §1 6항 §4번 verbatim "coalesce → 단일 fan-out", 측정 무관 구조 결정) | OpRiskArch — window 내 N 답변 → 단일 fan-out (매 답변 재스폰 아님) |
| P-2 recheck_counter_cap | `5` (count) | `[empirical-source: docs/adr/ADR-059-debate-protocol-v1.md §결정 4 max-round 5]` (selection precedent — ADR-059 adversarial debate max-round 5 + Du/Liang saturation literature anchor, OpRiskArch 채택) | OpRiskArch — cap 초과 = ESCALATE |
| P-2 max_total_recheck_spawns | `35` (count = 5 × 7) | `[empirical-source: derived]` (= recheck_counter_cap × fan-out 멤버 수, §결정 2 6 permanent + 조건부 PMO = 7. 산술 derived, 별도 실측 무관) | OpRiskArch 보강-1 — per-Story 절대 ceiling 논리 fan-out 상한 |

> **empirical-source-annotation (ADR-068 Amendment 1 I-5)**: P-1 latency 2종 (`debounce` / `max_wait_ceiling`) = `TBD` 명시 — ADR-077 = governance policy 신설 시점, 라이브 재조사 fan-out wall-clock telemetry 부재 (anti-pattern 1 empirical-absent default 회피 = explicit TBD marker mitigation 2 채택). 실측 carrier = Story-3 §8.3 Perf Baseline (재조사 fan-out wall-clock / spawn count / ESCALATE 도달 metric). P-2 `recheck_counter_cap` = ADR-059 §결정 4 max-round 5 selection precedent (standardized internal precedent, synthetic guess 아님). `coalesce 단위` / `max_total_recheck_spawns` = derived (mechanism invariant + 산술) — 측정 무관. ratchet 방향 (§결정 9): TBD → 실측값 전환 = 강화 (Story-3 후속), 약화 = ADR-058 §결정 5 sunset_justification 의무.

- **circuit-breaker (Researcher §6.1 개념-3 외부 anchor)**: recheck_counter_cap 초과 = circuit open → 사용자 직결 ESCALATE (결정 6 참조). debounce + max-wait ceiling + circuit-breaker = bounded backpressure envelope 3 sub-mechanism (R2 외부 anchor 부착).
- **envelope = ADR-039 §결정 9 deferred risk 부분 충당 (inherit-not-resolve, over-claim 금지)**: 본 envelope 는 ADR-039 §결정 9 spawn cost telemetry deferred risk 의 **재조사 범위 부분** 만 mechanical bound 한다. spawn cost telemetry 자체는 ADR-039 §결정 9 Phase 2 잔존 (본 ADR 이 resolve 하지 않음 — inherit only). over-claim 금지 normative.
- **env-invariant 단일값 (OpRiskArch + ADR-044 §결정 8 정합)**: P-1 / P-2 정량값은 env=0 (Orchestrator round-trip cold-start) / env=1 (SendMessage continuous) **동일 단일값**. env=0 / env=1 각각에 분리된 threshold 도입 = ADR-044 §결정 8 env-equality protocol invariant 손상 → 금지. P-2 = 5 는 env=0 cold-start 보수값으로 선택 (env=1 에서도 동일 cap).
- **rate-limit fallback disjoint (OpRiskArch 보강-2)**: 재조사 카운터 = 논리 fan-out 단위. ADR-057 rate-limit Sonnet→Opus fallback 재spawn 은 카운터 무증분 (disjoint) — 동일 논리 fan-out 의 재시도이지 신규 재조사 아님.
- **멱등 invariant (DataMigrationArch INV-IDEM-1/2)**: 동일 답변 set 재발 → 재조사 결과 내용 동치 (INV-IDEM-1 멱등). coalesce 병합 결정성 — timing jitter 무관하게 동일 window 내 답변 set 은 동일 fan-out 으로 병합 (INV-IDEM-2 결정성). U-1 (coalesce window 내 답변 race A→B) 정책 = supersede-into-set (window 내 답변 누적 후 단일 set 으로 fan-out, last-writer 아님 — 답변 손실 차단). E-2 (재조사 중 또 clarification) = 대기-then-coalesce (진행 중 재조사 abort 아님, 다음 window 로 누적). partial-failure deadlock = ESCALATE escape (결정 6, P-2 disjoint).

### 결정 5 — 재조사 카운터 disjoint (제3 carrier, ADR-076 §결정 4 N-layer 확장 패턴 재사용)

재조사 카운터는 §10 FIX Ledger 카운터 / playbook §4.4 "2회 재스폰 한도" / debate round counter 와 **물리적으로 disjoint 한 제3 측정 채널**이다.

- **disjoint hard constraint (DomainAgent §2.2 최우선 채택)**: 재조사 = 정상 scope 정교화 (forward), FIX = 게이트 회귀 (regression) → 서로 다른 측정 채널. 재조사 카운터를 FIX cap 에 합산하면 정상 정교화가 품질 결함으로 오분류 (의미 붕괴). cross-lane 합산 금지 (ADR-067 §결정 정합).
- **N-layer 확장 패턴 (Refactor 채택)**: ADR-076 §결정 4 "RESET disjoint layer invariant" (같은 단어가 다른 layer 에서 다른 의미 — Story progression vs upgrade transaction) 를 4-layer 로 확장 재사용:
  1. 재조사 카운터 (scope 정교화 layer) — recheck_counter_cap = 5 (결정 4)
  2. §10 FIX Ledger (품질 게이트 layer) — lane별 max 3 (ADR-067)
  3. playbook §4.4 2회 재스폰 한도 (PL재량 재스폰 layer)
  4. debate round counter (adversarial 합의 layer) — min 3 / max 5 (ADR-059)
  4 layer 간 cross-pollinate 금지. 3곳 cross-declare: 본 §결정 5 + §결과 절 + requirements-output contract schema (Story-4 carrier).
- **§9.0 ↔ §10 ↔ debate round 물리 disjoint (TestContractArch 채택, normative)**: 재조사 카운터는 Story §9.0 Clarification 재스폰 이력 표 (별도 표 / owner = RequirementsPL / `fix:*` 라벨 미추가) 에 기록. §10 FIX Ledger (Orchestrator monopoly / `Iter` 합산) 에 합산 금지. **"재조사 카운터 = fix-event-v1 row 아님, §10 합산 금지"** = normative invariant. playbook §4.4 L1859 선례 (2회 한도가 이미 §10 FIX Ledger 와 별도 채널로 운영 중, CodebaseMapper as-is 사실) 가 disjoint SSOT 확증.

### 결정 6 — ESCALATE escape valve (재조사 실패 아님, scope 재정의 trigger)

recheck_counter_cap (= 5) 초과 시 ESCALATE 한다. ESCALATE 의미 = "재조사 실패/abort" 아님 — **"clarification 으로 요건이 계속 흔들림 → scope 자체를 재정의해야 함"** 의 의미 전환 (escape valve).

- **escalation_class (OpRiskArch 채택)**: `escalation_class: scope_redefinition_required` — NOT `failure` / NOT `abort`. ESCALATE 후 recheck_counter RESET to 0 (scope 재정의 후 새 baseline).
- **§10 FIX Ledger 무기록 (OpRiskArch 채택)**: ESCALATE 는 §10 FIX Ledger 에 기록하지 않음 (§9.0 또는 별도 channel — 재조사 카운터 disjoint 정합, 결정 5). 정상 scope 정교화의 한계 도달 시그널이지 품질 결함 아님.
- **escape valve 의미 보존 (DomainAgent §2.4 채택)**: 이 의미 보존이 안 되면 ESCALATE 가 정상 scope 정교화를 차단하는 역효과 → 사용자 directive ("정상적 scope 정교화 차단 아님") 위반. 단순 abort 금지 normative.
- **선례 (ContinuityAgent §4.3 확증)**: ADR-059 §결정 4 (debate max round 후 사용자 escalation) escape valve 의미 보존 패턴 동형.
- **partial-failure deadlock escape (DataMigrationArch INV-IDEM-4)**: 재조사 fan-out 중 일부 agent FAIL 로 deadlock 시도 ESCALATE escape (P-2 disjoint — deadlock ESCALATE 는 counter cap 별도 진입).

### 결정 7 — trigger origin disjoint (ADR-052 boundary + 정보 무결성 invariant)

clarification 강제 재조사 trigger 와 다른 재실행 trigger 는 **trigger origin 단위로 disjoint** 이다.

- **origin 단위 disjoint (ContinuityAgent §4.3 RD-3 채택)**:
  - clarification 강제 재조사 = **user-answer-driven** (사용자 clarification 답변 origin, 본 ADR)
  - ADR-052 Amendment 1 A4 RequirementsPL redo = **Codex-divergence-driven** (Touchpoint #4 divergence origin)
  두 trigger 는 서로 다른 진입 — disjoint declare. 재조사 synthesis 재작성이 Touchpoint #4 를 재트리거하는가 (P-7) = 설계 lane 후속 위임. 본 §결정 7 = trigger origin disjoint boundary 자체를 normative 고정.
- **정보 무결성 invariant (SecurityArch 채택, codify)**: 강제 재조사 시 `prior_output_ref` (이전 §2/§5/§6 산출) 의 fact-check marker 4종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]`) 을 **verbatim 보존**한다. 재조사 sub-agent 는 `[hypothesis]` / `[fact-check-pending]` 을 `[verified]` 로 **무검증 승격 금지**. marker 부재 = 암묵 `[hypothesis]` default 유지 (ADR-052 Amendment 3 무손상). reverse-explicit `[verification-out-of-scope: <사유>]` marker 도 verbatim 보존. 이 무결성 영역은 §결정 7 trigger origin disjoint 및 P-7 와 동일 영역 — chief author codify.
- **3 카운터 disjoint 정합**: 재조사 카운터 ↔ debate round counter ↔ FIX cap disjoint (결정 5) 가 trigger origin disjoint 의 measurement 표현. ADR-052 Amendment 1 Touchpoint #4 debate 메커니즘 자체는 미변경 — 본 ADR 은 재조사와의 boundary 만 declare.

### 결정 8 — stale 게이트 (ADR-076 declarative reconciliation 재사용 + monotonic generation guard)

범위를 바꾸는 답변 수령 시 해당 조사 섹션 (§2 / §4.1 / §4.2 / §4.3 / §5 / §6) 을 stale 마킹하고, 재조사 완료 전 phase:설계 진입을 차단한다.

- **declarative reconciliation 정식화 (ArchitectAgent 결정 — Researcher R3 / 개념-2 채택)**: stale 게이트 = 목표 상태 (요구 변경 반영된 설계) ↔ 현재 상태 (stale 설계) 차이 reconcile. ADR-076 이 이미 채택한 declarative reconciliation 패턴을 **재사용** (신규 패턴 도입 불요). 요구사항 레인이 "ADR-076 재사용 가부 = 설계 lane 결정" 으로 위임 (§6.2 / §6.4 R3) → 본 ADR 이 **재사용 채택** 으로 판정. stale 마킹 = dirty state, 재조사 완료 = reconcile 완료.
- **INV-IDEM-3 monotonic generation guard (DataMigrationArch E-2 핵심 채택, normative 고정)**: stale 전이는 멱등 + **monotonic generation guard** — 하위 generation 의 재조사 완료가 상위 generation 의 stale 을 clear 하지 못한다. 재조사 진행 중 새 clarification 답변 수령 시 generation 증가 (monotonic). 하위 generation 재조사가 늦게 완료되어도 상위 generation stale 잔존. 이 invariant 미선언 시 §5.1 WHY (stale 설계 진입 차단) 무력화 → normative 고정 의무. generation schema (정수 monotonic counter / per-section) = P-N 설계 lane 후속 위임.
- **INV-IDEM-4 partial-failure fail-closed (DataMigrationArch 채택, normative)**: 재조사 fan-out 중 일부 agent FAIL 시 해당 섹션 stale **잔존** (fail-closed). FAIL agent 섹션을 false-clear 금지 — 부분 성공으로 stale 해제 시 stale 설계 진입 차단 무력화. partial-failure deadlock = ESCALATE escape (결정 6).
- **stale recovery 기준 (P-3 위임)**: stale 마킹 해제 = "재조사 완료 판정" 의 mechanical 기준 (어느 답변이 어느 섹션 stale, last-updated >= 최종 clarification timestamp 등) = P-3 / P-4 설계 lane 후속 위임. 본 §결정 8 = stale 게이트 = declarative reconciliation + monotonic generation + fail-closed 3 invariant "normative 선언 존재" 고정.
- **"범위 바꾸는 답변" mechanical 판정 (P-4 위임, E-1 거짓양성 차단)**: 단순 확인 (scope 무변경) vs scope 정교화 vs Epic 구조 변경 disambiguation 룰 = P-4 (§2.5 도메인 지식 공백). 본 ADR 은 "이 판정이 필요하다 + stale 게이트가 declarative reconciliation 으로 정식화된다" 까지 normative 고정.
- **stale 게이트 mechanical wire**: phase-gate-mergeable.yml phase:설계 precondition 추가 (조사 섹션 last-updated >= 최종 clarification timestamp) 또는 evidence-check-registry entry 신설 = Story-3 이후 carrier (workflow 변경 = full-lane 별개 Story). stale 게이트 restart-aware / §8.5 후보 = Story-3 carry-forward (TestContractArch 채택).

### 결정 9 — ratchet (AC-6 수용 조건, ADR-058 §결정 5 정합)

본 ADR 의 다음 정책 속성은 **단조 강화·비회귀 (ratchet) 방향**으로만 amend 한다 (normative 선언):

- envelope 강도 (debounce / max-wait / counter cap — 강화 = 더 엄격한 backpressure)
- fan-out 멤버 (6 permanent + 조건부 PMO — 강화 = 멤버 추가, 축소 불가)
- 트리거 무조건성 (조건 게이트 폐기 — 강화 = 게이트 재도입 금지, value-equality skip 비차용 invariant 보존)
- 재조사 카운터 disjoint (4-layer — 강화 = layer 추가, 합치 불가)
- design-reading mandate 심화 (skim 금지 — 강화 = 깊이 강화, skim 회귀 금지)

- **약화 방향 차단 (ADR-058 §결정 5 sunset_justification 의무)**: 약화 방향 변경 (envelope threshold 완화 / fan-out 멤버 축소 / 게이트 재도입 / disjoint layer 합치 / skim 회귀) = ADR-058 §결정 5 `sunset_justification` 3-tuple (metric / who / how) 정량 명시 없이 차단. `is_transitional: false` (frontmatter) 정합 — permanent governance, ADR-064 top-down self-application ratchet 동형.
- **normative 선언 자체가 AC-6 수용 조건 (TestContractArch grep-testable 채택)**: 구체 ratchet 속성 enumeration·임계는 위 5 항목으로 고정. mechanical lint = `adr-077-ratchet-declared` (grep-testable: 본 §결정 9 ratchet 방향 선언 + ADR-058 §결정 5 sunset_justification 문구 + frontmatter `is_transitional: false` 존재). registry row append = Story-3, ADR frontmatter `mechanical_enforcement_actions[]` 는 declare (deferred-followup). Story-1 §5.4 AC-6 ("normative 선언 존재" 를 수용 기준으로 고정) 정합.

### 결정 10 — parallel always-executable mandate (ContinuityAgent RD-4 carrier, ADR-064 §결정 4 정합)

재조사 fan-out (6 permanent + 조건부 PMO) 은 **parallel always-executable** 이다 (normative mandate).

- **parallel default 명문화 (ContinuityAgent §4.3 RD-4 carrier 채택)**: 재조사 fan-out = ADR-064 §결정 4 parallel default 영역. 단일 메시지 다중 Agent tool call (Orchestrator) 또는 env=1 SendMessage 동시 dispatch. sequential 선택은 ADR-064 §결정 4 의 3 사유 (state dependency / shared resource / ordering invariant) 중 1 종 명시 의무 — 재조사 fan-out 6 agent 는 상호 독립 (state dependency 부재) → default parallel.
- **sequential-bias 교훈 carrier**: 과거 sequential 오염 incident (parallel 가능 작업의 무근거 sequential 실행) 차단을 위해 "parallel always-executable" 을 normative 로 명문화 (ContinuityAgent RD-4 — 명문화만, 메커니즘은 ADR-064 §결정 4 미변경).
- **env=0/env=1 동등 (ADR-044 §결정 8 정합)**: env=0 = Orchestrator round-trip 다중 spawn (1 메시지 N Agent tool call) / env=1 = SendMessage 동시 dispatch. 양쪽 parallel 동등 — env-invariant 단일 protocol (결정 4 envelope env-invariant 정합).
- **§14 Lane Evidence (ADR-031 cross-ref)**: 재조사 fan-out 도 lane evidence row 대상인지 = 설계 lane 후속 판정 (Story-1 §3 ADR-031 약한 관련). 본 §결정 10 = parallel always-executable mandate 자체를 normative 고정.

## 결과

### 즉각적 결과

- ADR-077 = 요구사항 레인 clarification 강제 재조사 전파 정책의 normative SSOT 확립. RESERVATION row 77 `reserved → active` 전환 (본 Story-1 Phase 1 PR).
- 6 SubAgent 산출 dedup·상충 조정 결과: (a) Analyst "3 카운터 통합 envelope" 제안 → DomainAgent disjoint hard constraint 종속 (disjoint 우선, 결정 5) (b) Researcher 외부패턴 3종 → §2 도메인 제약 종속 (개념-1/3 dedup, 개념-2 ADR-076 재사용 채택 결정 8) (c) OpRiskArch envelope 정량 + DataMigrationArch 4 idempotency invariant 통합 (결정 4/8) (d) SecurityArch 정보 무결성 invariant codify (결정 7).
- **4-layer counter disjoint cross-declare**: 본 §결정 5 + 본 §결과 절 (재조사 카운터 = scope 정교화 layer / §10 FIX Ledger = 품질 게이트 layer / playbook §4.4 = PL재량 재스폰 layer / debate round = adversarial 합의 layer, cross-pollinate 금지) + requirements-output contract schema (Story-4 carrier 3번째 cross-declare 위치).

### 후속 carrier dependency 명시 (Story-1 scope 누수 방지)

| 항목 | 귀속 Story | 본 ADR 의 역할 |
|---|---|---|
| playbook §2.2 표 행 amend (cross-ref 하위화) | Story-2 | §결정 2 가 trigger SSOT cross-ref (본문 amend 아님) |
| playbook §4.4 본문 재작성 (강제 fan-out 절차) + §9.0 schema | Story-2 | §결정 1/5 가 amend 방향 선언만 |
| CLAUDE.md 요구사항 레인·FIX 루프·PMO 비개입 단락 갱신 | Story-2 | §결정 2/5 가 cross-ref (본문 미변경) |
| requirements-output contract bump (재조사 카운터 schema + 4-layer disjoint 3번째 cross-declare) | Story-4 | §결정 5 가 schema 요구만 명세 |
| team-spec-requirements.yaml conditional PMO entry (`spawn_mode: conditional`) | Story-3 | §결정 2 가 closed enum SSOT |
| stale 게이트 workflow 신설 (phase:설계 precondition) + evidence-check entry | Story-3 이후 | §결정 8 이 declarative reconciliation 재사용 + 3 invariant declare |
| evidence-checks-registry row append (`adr-077-ratchet-declared` / `adr-077-design-reading-mandate-declared` warning tier) | Story-3 | frontmatter `mechanical_enforcement_actions[]` deferred-followup declare |
| §8.5 stale 게이트 restart-aware / §8.3 재조사 fan-out wall-clock·spawn count·ESCALATE Perf Baseline | Story-3 | TestContractArch carry-forward (Story-1 N/A) |

### 검증 영역 (비-영향 입증)

- **ADR-044 §결정 8 env-equality protocol invariant 무손상**: P-1 / P-2 정량값 env-invariant 단일값 (결정 4) — env=0 cold-start / env=1 SendMessage 동일 threshold. §결정 8 invariant 손상 0.
- **ADR-039 §결정 1 binary always-spawn invariant 정합**: 무조건 재조사 = always-spawn (binary, §결정 9 deferred spawn cost 는 inherit-not-resolve, over-claim 0 — 결정 4).
- **ADR-052 Amendment 1/3 Touchpoint #4 debate 메커니즘 무변경**: 본 ADR 은 재조사 ↔ Touchpoint #4 boundary 만 declare (결정 7), 메커니즘 미변경. fact-check marker 4종 verbatim 보존 invariant (결정 7) 가 ADR-052 Amendment 3 무손상 보장.
- **ADR-067 cross-lane 합산 금지 정합**: 재조사 카운터 = §10 FIX Ledger disjoint (결정 5) — cross-lane 합산 0.

## 해소 기준

**N/A — permanent policy** (`is_transitional: false` — permanent governance invariant).

본 ADR 은 요구사항 레인 clarification 강제 재조사 전파 도메인의 1st-class normative anchor — codeforge 가 deprecate 되지 않는 한 영구 유효. Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application 정합):

- 새 fan-out 멤버 추가 (결정 2 — 멤버 축소 불가)
- envelope threshold 강화 (결정 4 — 더 엄격한 backpressure)
- counter disjoint layer 추가 (결정 5 — layer 합치 불가)
- design-reading 깊이 강화 (결정 3 — skim 회귀 금지)
- ratchet 속성 enumeration 확장 (결정 9)

약화 방향 (envelope 완화 / fan-out 멤버 축소 / 조건 게이트 재도입 / disjoint layer 합치 / skim 회귀) = ADR-058 §결정 5 `sunset_justification` 3-tuple (metric / who / how) 정량 명시 없이 차단. 사용자 directive verbatim (CFP-755 Epic A §1 "강제적으로 수행하라") 정합.

## 관련 파일

- `docs/adr/ADR-RESERVATION.md` — row 77 `reserved → active` 전환 (본 Story-1 Phase 1 PR)
- `docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` — §결정 9 deferred spawn cost risk 부분 충당 (inherit-not-resolve, 결정 4)
- `docs/adr/ADR-044-phase-scoped-sequential-team.md` — §결정 8 env-equality protocol invariant 무손상 (결정 4/10)
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — 조건부 PMO 합류 trigger ↔ retro trigger origin disjoint (결정 2)
- `docs/adr/ADR-052-codex-proactive-check-touchpoints.md` — Amendment 1/3 Touchpoint #4 boundary (결정 7)
- `docs/adr/ADR-056-requirements-synthesis-order.md` — 합성 순서 (재조사 후 PL 재종합 정합)
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — is_transitional:false 정합 (§해소 기준 N/A), §결정 5 ratchet 차단 (결정 9)
- `docs/adr/ADR-059-debate-protocol-v1.md` — 재조사 카운터 ↔ debate round counter disjoint + max-round 5 선례 (결정 4/5)
- `docs/adr/ADR-064-decision-principle-mandate.md` — §결정 4 parallel default (결정 10) + §결정 1 forbid-list 모달 어휘 금지 (결정 4)
- `docs/adr/ADR-067-fix-ledger-implementability-escalation.md` — cross-lane 합산 금지 (재조사 카운터 disjoint 선례, 결정 5)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — §결정 4 RESET disjoint layer invariant N-layer 확장 재사용 (결정 5/8)
- `docs/adr/ADR-031-lane-spawn-evidence.md` — 재조사 fan-out §14 Lane Evidence row 대상 (결정 10, 설계 lane 후속 판정)
- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md` — Story file = internal-docs wrapper/stories/CFP-759.md
- `docs/adr/ADR-054-doc-only-fast-path.md` — Story-1 = 신규 ADR → full-lane 강제
- `docs/orchestrator-playbook.md` — §2.2 (재스폰 대상 표) / §4.4 (Clarification 재스폰 절차) amend 방향 선언만 (본문 amend = Story-2)
- `CLAUDE.md` — 요구사항 레인·FIX 루프·PMO 비개입 단락 cross-ref (본문 갱신 = Story-2)
- `docs/inter-plugin-contracts/requirements-output-v1.md` — 재조사 카운터 schema + 4-layer disjoint 3번째 cross-declare (contract bump = Story-4)
- `templates/team-spec-requirements.yaml` — 조건부 PMO conditional teammate entry (`spawn_mode: conditional`, 변경 = Story-3)
- `docs/evidence-checks-registry.yaml` — `adr-077-ratchet-declared` / `adr-077-design-reading-mandate-declared` warning tier (registry row append = Story-3)
- `docs/domain-knowledge/domain/requirements-discipline/clarification-mandatory-recheck-propagation.md` — domain narrative (DomainAgent self-write, CFP-759)
- `docs/domain-knowledge/concept/clarification-driven-reinvestigation.md` — concept narrative (ResearcherAgent self-write, CFP-759)
- `<internal-docs>/wrapper/stories/CFP-759.md` — 본 ADR carrier Story (Epic A Story-1)
