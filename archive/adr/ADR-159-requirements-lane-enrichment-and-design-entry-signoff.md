---
adr_number: 159
title: 요구사항 lane 능동 요건 발굴(enrichment 일급) + intent-confirmation-loop + design-entry 사용자 확정 gate
status: Proposed
category: governance
date: 2026-07-17
carrier_story: CFP-2725
parent_epic: null
is_transitional: false
supersedes: []
amends: []
related_stories:
  - CFP-2725  # 본 ADR 신설 carrier — 요구사항 lane 사용자 대화 프로세스 정식화 (dogfood)
related_adrs:
  - ADR-071  # Amendment 15 sibling — intake 항상 declare 4번째 touchpoint(§15.5 확장) + §결정 20 lane-scoped carve-out + design-entry gate = §결정 22 정당 멈춤 carve-out. 발화 monopoly·relay 구조 무변경
  - ADR-077  # Amendment 1 sibling — 순수 확정 = terminal event(신규 trigger origin `user-final-confirmation-driven`, §결정 7 taxonomy 확장) + why-왕복 counter = §결정 5 5번째 disjoint measurement channel + 리뷰-후 확정 rewind
  - ADR-125  # Amendment 3 sibling — 결정 A(사용자 확정 = 리뷰 PASS 후·설계 진입 전 위치) + 결정 B(내부 시스템 적합성 4번째 disjoint 검증 축). Amd2 internal-invariant 축 선례 답습
  - ADR-124  # 외부지식 충당 3-단계 disjoint 짝 (cross-ref only — enrichment = 단계① 능동 정립의 대화-lane 짝, 내부적합 = 외부지식 3-단계 internal 아날로그). 의미 변경 0
  - ADR-046  # Researcher 역할 재정의 선례 (synthesizer→elicitor 동형 pattern) + Mandate 2 demand-anchored (enrichment why-anchored boundary anchor). cross-ref only — Researcher 본문 무접촉
  - ADR-127  # 정식 풀 플로우 비협상 + §결정 4 skip-offer 금지 (intake "항상"의 우회 차단 기반, user-explicit skip 채널과 disjoint)
  - ADR-144  # stop taxonomy — "사용자 최종 확정 대기" = payload>0 정당 멈춤(A1) 매핑, 자동확정 절대 금지
  - ADR-099  # Jira decision channel — async 원격 확정 재사용 (dual-input + timeout=재알림 + 자동결정 금지)
  - ADR-100  # Jira decision channel binding — 확정 payload 운반 + 양채널 mirror
  - ADR-119  # research-before-claims — §결정 9 제안 필요성 3문 게이트(enrichment guardrail) + §결정 10 ④ advisory ceiling ground-truth(author≠user 구분 불가)
  - ADR-039  # spawn/발화 monopoly — 사용자 dialog = Orchestrator inline 전용. relay 구조로만 실현 (무변경, cross-ref)
  - ADR-052  # Codex proactive touchpoint #4 — 작성측 self-check(단계②) ↔ 본 확정/enrichment(대화 축) disjoint (무변경)
  - ADR-145  # §5 AC 표 = 확인 대화로 정련된 요구의 기계 착지 표면
  - ADR-058  # sunset criteria mandate — is_transitional:false permanent 정합
  - ADR-064  # decision principle mandate — ratchet 강화 방향 self-application
related_files:
  - archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md
  - archive/adr/ADR-071-orchestrator-user-dialog-convergence.md
  - archive/adr/ADR-077-clarification-forced-reinvestigation-propagation.md
  - archive/adr/ADR-125-requirements-review-lane.md
  - docs/orchestrator-playbook.md
  - plugins/codeforge-requirements/CLAUDE.md
  - plugins/codeforge-requirements/agents/RequirementsPLAgent.md
---

# ADR-159: 요구사항 lane 능동 요건 발굴(enrichment 일급) + intent-confirmation-loop + design-entry 사용자 확정 gate

## 상태

Proposed (2026-07-17 KST, CFP-2725 carrier). `is_transitional: false` — 영구 governance 결정 기록. 본 ADR 은 요구사항 lane 사용자 대화 프로세스를 정식화하는 SSOT 이며, [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) Amendment 15 · [ADR-077](ADR-077-clarification-forced-reinvestigation-propagation.md) Amendment 1 · [ADR-125](ADR-125-requirements-review-lane.md) Amendment 3 과 짝을 이룬다 (3축 복합 — dialog frequency 축 = ADR-071 소유 / terminal event·counter 축 = ADR-077 소유 / lane 시퀀스·검증축 = ADR-125 소유 / lane 일급 목적·확정 액트 = 본 ADR 본체 수용). ADR-127 패턴(신규 ADR 본체 + 영향 ADR Amendment 동반) 답습.

## 본질 선언

> **요구사항 lane 의 일급 목적은 transcription(전사)이 아니라 elicitation(도출·발굴)이다.** 사용자와의 대화로 why(의도)를 확정하는 것은 전제(1단계)이고, 그 확정된 why 를 발판으로 사용자가 명시하지 않은/못한 **본질(underlying) 요건까지 능동 발굴·확장(enrichment)** 해 문자 그대로가 아닌 본질 요구를 충족시키는 것이 목적이다. why 교정은 확장의 전제이지 종착점이 아니다.

본 anchor(CFP-2725 §1 사용자 directive verbatim: "요구사항의 풍부화와 정확화" + "본질적인 사용자의 요구사항을 충족")가 아래 모든 §결정보다 먼저 배치된 이유 = mechanism 우선 reading risk 회피 (게이트 통과 최적화로 lane 목적을 좁히는 self-defeating trap 차단). 아래 §결정(왕복 declare / 확정 gate / terminal event / counter / advisory ceiling)은 본질을 보조하는 scaffolding 이다.

## 컨텍스트

요구사항 lane 은 사용자 발화를 downstream 9 lane 이 소비 가능한 명세로 변환하는 유일한 정규 변환 지점이다. 현행 시스템의 사용자 접점은 **전부 조건부** — "항상" 발동 접점 0, "사용자 최종 확정" 이 lane 진행 조건인 지점 0 (Story §4.1 AS-IS 실측: §5.5 항목 부재 시 사용자 발화 0 으로 lane 통과 가능).

이 구조가 방치하는 도메인 실패 모드는 2층이다:

1. **(상위) literal-compliance gap** — 문자적 요청만 충족하고 본질 요구를 미발굴 (전사에 그침). 요구공학의 근본 전제상 사용자는 자기 요구를 완전히 명시하지 못한다 (unstated/tacit 요건 — `source: SEI Elicitation of Unstated Needs / SEI Blog "Eliciting and Analyzing Unstated Requirements"`). "의도는 전달 대상이 아니라 발견 대상" (`source: arXiv 2602.03429 DiscoverLLM`).
2. **(하위, 상위의 한 사례) why 오추정 → downstream 오염** — 발굴은커녕 출발 의도조차 틀리게 짚어 정밀화가 오류를 증폭 ("정밀하게 엉뚱한 목표"). SOTA LLM 은 모호 요청에 의도를 가정하고 직행 답변하는 것이 **모델 계통 편향**이다 (`source: arXiv 2410.13788` — ICLR 2025 clarification-reluctance; SE 에이전트 실험 최대 74% 성능 향상 `source: arXiv 2502.13069`). confidence-gated asking 은 confidently-wrong 을 통과시킨다.

현행 게이트(에이전트 자기평가-조건부 질문)는 하위 실패(과신-미질문)도 못 막고 상위 실패(발굴 부재)는 겨냥하지 않는다. 본 ADR 의 forcing function 은 3중이다: (i) 게이트 발동 조건에서 **자기평가 제거**(intake 항상 왕복) — 하위 봉인 / (ii) 확정 why 를 발판으로 **미명시 요건 능동 발굴을 왕복의 명시 산출로 요구** — 상위 실현 / (iii) 확정 권한을 사용자에게 반환(design-entry gate) — informed sign-off.

## 결정

> 본 ADR = 요구사항 lane 일급 목적(enrichment) + intake 왕복 declare + design-entry 확정 gate(결정 A) + terminal confirm act + enrichment why-anchored boundary + advisory ceiling 정직 라벨의 SSOT. 발화 frequency 축은 ADR-071 Amd15, terminal event·counter 축은 ADR-077 Amd1, lane 시퀀스·내부적합 검증축은 ADR-125 Amd3 에서 짝 wiring (cross-ref).

### 결정 1 — 요구사항 lane 일급 목적 = enrichment/elicitation (RequirementsPL 역할 재정의)

요구사항 lane 의 일급 목적을 **본질 요구 충족을 위한 능동 요건 확장(enrichment)** 으로 정식화한다. why 확정은 이 확장의 **전제(1단계)** 이지 종착점이 아니다.

- **RequirementsPL 역할 재정의**: 현 PL = "synthesizer" (세 관점 dedup·통합). 본 ADR 이 이를 **elicitor/enricher** (사용자와 능동 발굴 주체) 로 확장한다. ADR-046 이 Researcher 를 "얕은 검색 → 3-mandate(Concept formulation / Deep exploration / Requirement reshape)" 로 재정의한 선례와 **동형 pattern** ("역할이 제대로 안 잡힘 → 재정의" 사용자 directive 반복). ADR-046 본문 무접촉 — cross-ref 만.
- **enrichment machinery 기존재 (신규 발명 아님)**: Researcher Mandate 3(concept-driven reshape) + Mandate 2(unknown-unknown proactive 발굴, demand-anchored) + Analyst ambiguity 확장 + Domain underlying 제약이 이미 확장 축 (`verified — ADR-046 §Amendment 2 Mandate 2 demand-anchored 재초점`). 본 ADR = 이 기존 축을 **agent-실행 → 사용자 대화 주도로 무게중심 재배치** (기존 축 대체 아님). 신규 sub-agent 0.
- **왕복 성공 기준 2축**: ① why 를 맞게 짚었나 ② 본질 요구를 충족하도록 요건이 확장됐나. 왕복이 오해 정정(결함 교정)에 그치면 lane 목적 미달성.

### 결정 2 — intake 항상 왕복 = mandatory DECLARE (STRENGTHEN frame, mandatory ASK 아님)

매 요구사항 접수마다 이해한 배경·의도를 먼저 제시하고 확인받는 왕복을 **무조건 절차화**한다 (자명해 보여도 생략 없음). 단, 이는 **mandatory DECLARE 이지 mandatory ASK 가 아니다** (핵심 강화 frame).

- **DECLARE ≠ ASK (원천 회피)**: trivial 요구는 최소형 = **이해 재진술 1~3줄 + "이의 없으면 진행" 고지 + 열린 질문 0~1개** — 명시 답변 대기 없이 진행 가능하다 (Story AC-15). 모호(ask-trigger ① 해당)일 때만 실제 ASK 로 escalate. 이 DECLARE≠ASK 구분이 ADR-071 §결정 20 (ask-trigger 3종 한정 — "요구 애매할 때만" 묻기) 과의 충돌을 **원천에서 해소**한다: intake 왕복은 derived-default 를 제시·재진술하는 declare 패턴(ADR-071 §결정 16 natural-language trigger 의 no-dialog-reflex derived-default 동형)이지, 매 접수마다 사용자를 멈춰 세우는 ASK 가 아니다. 발화 frequency 축의 배선 = ADR-071 Amendment 15 (§결정 20 lane-scoped carve-out — 요구사항 lane "항상 declare"; 타 lane 일반화 금지, §결정 20 본체 보존).
- **"컨텍스트 충분 → 확인 생략" 추론 금지** (Story U4): 컨텍스트를 모았다는 이유로 확인 왕복을 대체한다고 가정하지 않는다 (clarification-reluctance 방어).
- **enrichment 명시 output (Story R7)**: 확인 왕복은 확장 산출을 명시 output 으로 생성한다 — (a) 발굴된 미명시/본질 요건 후보 목록 (b) 각 후보의 원문 대비 delta 표시 (문자 그대로 vs 확장분 구분) (c) 확장 후보도 확정 packet(결정 3)의 확인·잔량 대상에 포함. 열린 보충 질문 = 미명시 요건 발굴 채널로 명시적 지위 부여 (정정용 질문과 병행).
- **단일 예외 = 사용자 본인의 명시 skip 지시**: 사용자가 특정 Story 에서 "이번엔 확인 왕복 생략" 을 직접 지시하면 해당 1회에 한해 우선하되 지시 verbatim 을 확정 기록에 남긴다. 생략 판정 주체가 사용자이므로 핵심 명제("에이전트 자기평가 제거")는 무손상 — 에이전트 측 skip-offer 는 여전히 금지 (ADR-127 §결정 4 / ADR-071 §결정 21). 좁은 해석 default (왕복만 skip, 최종 확정 유지 — lane/Story 생략은 불가, ADR-127 §결정 3.2 정합).

### 결정 3 — design-entry 사용자 확정 gate (결정 A: 요구사항리뷰 PASS 후·설계 진입 직전)

사용자 최종 확정 gate 의 위치를 **요구사항리뷰 PASS 후 · 설계 진입 직전**으로 확정한다 (요구사항 lane exit gate 아님 — "exit gate" 용어 폐기, design-entry gate 로 대체).

- **위치 근거 (비가역성 경계)**: 요구사항 + 요구사항리뷰 = 가역 문서 단계, 설계 = 첫 비가역 지점. why 대화 + enrichment 발굴은 요구사항 lane 에서 계속되고, 옮기는 것은 최종 sign-off 뿐. 흐름 = `요구사항(why대화+enrichment+§1-7) → 요구사항리뷰(외부사실+내부적합) → 사용자 최종 확정 → 설계`. BABOK approve 의 입력-의존성 정합 — approve 는 verified+validated 요건 위에서만 작동한다 (`source: iiba.org BABOK 7.2 Verify / 7.3 Validate / 5.5 Approve`; BABOK task 는 명시적 비순차이나 approve 는 입력-의존).
- **protective intent 무손상 + 강화**: 원문 "사용자 최종 확정 전까지 종료 불가" 의 본질 = *미확정 요건으로 비가역 하류(설계) 진입 방지*. 확정을 리뷰 뒤로 옮겨도 (i) 첫 비가역 지점(설계) 앞에 그대로 위치 = protective intent **무손상** (ii) 외부사실+내부적합(결정 B) 검증 끝난 한 벌 *informed* 상태 확정 = **강화**. 재배치가 UQ-1 순서 역설("확정 후 리뷰 변경 → 확정 무효")을 원천 해소.
- **predicate/enforcer 분리 (안정 interface)**: 안정 predicate = `user-final-sign-off-resolved` (ground-truth = 확정 발화 presence — advisory ceiling, author≠user 구분 불가라 "확정 기록의 실재" presence 까지만 정직 주장) / 교체가능 enforcer = tier. **Phase 1 = playbook 설계 진입 preflight advisory ONLY** — anchor = 기존 phase:요구사항-리뷰 → phase:설계 전이 경계 (기존 preflight "§1-6 채움" 조건과 sibling). 신규 phase 라벨·gate AND·required context = **Phase 1 채택 금지** (기계 fail-closed = advisory ceiling 위반).
- **informed sign-off packet (Story AC-12)**: 확정 요청은 (a) 확정 대상 요약(why + scope + 능동 발굴·확장 요건 포함 재편 요구 요약) + (b) 외부사실·내부적합 검증 반영본 + (c) 미해결 질문 잔량(0건 또는 명시 defer 목록 — trivial 최소형에서도 잔량 명시(0 포함) 생략 불가)을 포함해야 유효하다. 잔량 은폐 상태의 확정은 무효 (vacuous confirm 회피 — `source: Example Mapping (Cucumber) red-card` 정합).
- **단일 sign-off (Story AC-24)**: 요구사항 → 요구사항리뷰 전이는 별도 사용자 확정 gate 를 요구하지 않으며, 설계 진입 직전 확정이 **유일한 sign-off** 다 (이중확정 아님). 확정 이후 실질 변경 시에만 delta 재확정.
- **delta 재확정 (Story AC-9)**: 확정 이후 설계·구현 중 §1-7 실질 변경이 why·scope·AC 에 영향을 주면 전체 재확정이 아니라 변경 delta 한정 경량 재확인 왕복 후 진행. 실질 변경 판정 기준 상세 = 설계 lane 위임. 리뷰-FIX 유발 변경은 확정 전 흡수되어 본 재확정 발동 빈도는 설계 진입 후 변경으로 좁아진다.

### 결정 4 — terminal confirm act (명시 발화 필수 + 기록·복원 + async·Epic 규율)

사용자 최종 확정 = **명시 확정 발화**를 요구한다 (무이의·침묵 진행 = 확정 아님).

- **기록**: 확정 발화 verbatim 을 Story file 에 기록하고 세션·Jira 양채널에 mirror 한다. SSOT 서열 = Story §5.5 verbatim primary / Jira mirror best-effort (fail-open — Jira 결손 ≠ 확정 무효, `verified — jira-decision-channel SKILL.md fail-open`).
- **복원 (Story AC-7)**: 세션 재개 시 복원 범위 = (a) 확정 여부 + (b) 미해소 질문 목록. 복원 원천 = Story file 의 확정 발화 verbatim 기록.
- **terminal event 분류**: 순수 확정(내용 무변경) = terminal event — 재조사 fan-out 미발동. 내용 수정 동반 확정만 재조사 후 재확정 경로. why-왕복 counter 는 기존 recheck cap 과 별도 disjoint. 이 event taxonomy·counter disjoint 의 배선 = ADR-077 Amendment 1 (신규 trigger origin `user-final-confirmation-driven` + 5번째 measurement channel).
- **user-explicit skip 채널 (Story AC-18)**: 결정 2 의 사용자 명시 skip 지시 = 확정 기록에 verbatim 남김. 에이전트 skip-offer 금지 무손상.
- **Epic 규율 (Story AC-16)**: Epic 접수 시 why 왕복 1회 + child Story 는 Epic 확정 why 상속, child 가 Epic why 를 벗어나는 delta 를 가질 때만 그 delta 한정 재왕복.
- **async 원격 확정 (Story AC-17)**: 사용자 세션 부재 + decision_channel 활성 시 Jira 원격 확정도 세션 확정과 동등 유효. 무응답 시 단계형 재알림만 (자동확정 **절대 금지** — timeout = 재알림, `verified — ADR-099/100`). 열린 질문은 세션 전용(closed-option 확정만 Jira 겸용). cadence 정량값 = 설계 lane.

### 결정 5 — enrichment why-anchored boundary (over-clarification 배제, null 결과 valid)

능동 요건 확장이 unbounded gold-plating 으로 drift 하지 않도록 경계를 명문화한다.

- **anchor (Story AC-20)**: 확장은 확정된 why + informed sign-off packet(결정 3)이 정의한 본질 요구에 **정박(anchored)** 되어야 하며, 본질 의도와 무관한 scope 팽창·gold-plating·edge-case 폭주는 확장으로 인정되지 않는다. anchor concept = 사용자 "본질적인" 어구. 근거 = ADR-119 §결정 9 (발견 ≠ 필요, 제안 필요성 3문 게이트) + ADR-046 Mandate 2 demand-anchored ("필요한 만큼만")의 대화-lane 재적용 (신규 발명 아님). Kano 분류가 확장 anchor — must-be(암묵 기대 누락)·underlying need 우선, indifferent 축 발산 제외 (`source: Kano model / Qualtrics Kano Analysis`).
- **3중 기성 방어**: recheck cap 5 → ESCALATE scope_redefinition_required (ADR-077 §결정 4/6) + Non-goal 명시 의무 + 사용자 확정 제동(informed sign-off). 신규 게이트 신설 불요.
- **null 결과 valid (검사연극 방어)**: 발굴할 미명시 요건이 없으면 null 명시 반환이 정상이다 (declarative-only — ADR-119 §결정 8 동형). enrichment "충족" 을 매 Story mandate 화하거나 "발굴 소진" 을 terminal 조건에 넣으면 무한 확장이라 종료 불가 — terminal 성립 = "발굴 소진" 아닌 **"사용자가 확장 충분 판단 + 순수 확정 발화"** (인간 판단 종료).
- **enrichment 판정 축의 ground-truth = 사용자 확정**: enrichment "충족" 판정 주체 = 인간이므로 기계 검증 표면을 신설하지 않는다 (hollow-gate 회피). advisory-ceiling 정직 라벨(결정 6)은 design-entry gate 축 한정 — enrichment 판정 축 비적용.

### 결정 6 — advisory ceiling 정직 라벨 (over-claim 금지) + 확정 결정론

design-entry 확정 gate 의 기계 검증 범위를 정직하게 라벨링한다.

- **advisory ceiling (Story AC-14)**: Phase 1 = advisory 절차 규율. 기계 검증 커버 범위 = **확정 기록·규칙의 presence 까지**. "기계 강제 100%" over-claim 금지 (기계 승격 = 증거 축적 후 별도 결정). 근거 = 단일 사용자 환경에서 author 로 "사용자 행위 vs Orchestrator 행위" 구분 불가 (`verified — jira-decision-channel SKILL.md A1-3` + ADR-119 §결정 10 ④) → 어떤 기계 게이트도 ground-truth 증명 불가. 기계화해도 "in-coverage best-effort" 정직 라벨 의무. 표현: "rule/record presence 는 testable, user actually confirmed 는 NOT testable".
- **cross-channel 승자 + 병렬세션 결정론 (Story AC-25)**: 사용자 확정이 세션·Jira 양채널 mirror 또는 병렬 세션 환경에서 기록될 때, 두 채널·세션의 확정 상태가 상충하거나 동시 기록되면 설계는 cross-channel 상충 승자 규칙과 병렬 세션 확정 이중기록 방지의 결정론적 해소 규칙을 정의한다 (구체 메커니즘 = 설계 위임; 본 repo 병렬세션 race 이력 CFP-777/CFP-2719 계보 고려). first-valid-immutable 은 Jira 채널 내부 ordering 만 규정하므로 cross-channel 승자·stale-answer 무효화는 별도 규칙.

## 결과

- **긍정**: 요구사항 lane 의 도메인 목적(elicitation)이 SSOT 로 박제되어 literal-compliance gap(상위 실패)과 why 오추정(하위 실패)을 함께 forcing function 으로 방어. 사용자 확정 권한이 informed sign-off 로 반환. 재배치(결정 A)가 순서 역설 원천 해소.
- **부정/trade-off**: intake 항상 declare 는 발화 frequency 를 증가시킨다 (강화 방향 ratchet — DECLARE≠ASK 로 사용자 burden 최소화, trivial 최소형 경량화). Phase 1 advisory 는 기계 강제 부재 (정직한 상한 — Phase 2 승격 경로만 예약).
- **영향 경계**: 발화·spawn monopoly(ADR-039) 무변경 — 실장은 Orchestrator turn + relay 강화만. relay 구조 무손상. 신규 mechanical 게이트 0 (Phase 1). consumer 전파 = wrapper 규칙 = 전 consumer 하한선 (overlay 축소 불가, 강화만 가능).
- **무손상 invariant 명제 (dogfood 검증 대상)**: ADR-071 §결정 1/3/4/15/20/21 + 5번째 cognitive layer 신설 금지 / ADR-077 §결정 1 value-equality skip 비차용 / ADR-125 lane count 10·required contexts 무변경 / ADR-039 monopoly / ADR-124 외부사실 축 무약화 / ADR-046 3-mandate 골격 — 전부 보존.

## sunset_justification (ADR-058 §결정 5 — 약화 차단)

본 ADR = 약화 0건. **강화 방향** — 요구사항 lane 에 능동 발굴 forcing function 추가 + 사용자 확정 gate 추가 + terminal/counter/advisory 정직 라벨 추가. 기존 어떤 §결정/게이트도 대체·약화하지 않는다 (짝 Amendment 3건 모두 direction: strengthen, sunset_justification: null). is_transitional: false (permanent governance anchor). 원복은 별도 Story 의 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 (약화 시 sunset_justification 3-tuple metric/who/how) 를 따른다. ADR-064 §결정 7 top-down self-application ratchet 정합.

## 해소 기준

N/A — permanent policy.

본 ADR 은 요구사항 lane 사용자 대화 프로세스 도메인의 1st-class normative anchor — codeforge 가 deprecate 되지 않는 한 영구 유효. Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application 정합).

## 관련 파일

- 본 ADR — 요구사항 lane enrichment 일급 목적 + design-entry 확정 gate + terminal confirm act SSOT
- [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) — Amendment 15 (intake declare touchpoint + §결정 20 lane-scoped carve-out + §결정 22 정당 멈춤 carve-out)
- [ADR-077](ADR-077-clarification-forced-reinvestigation-propagation.md) — Amendment 1 (terminal event + 5번째 counter channel + 리뷰-후 rewind)
- [ADR-125](ADR-125-requirements-review-lane.md) — Amendment 3 (결정 A 확정 위치 + 결정 B 내부적합 검증 축)
- [ADR-124](ADR-124-external-knowledge-provisioning-model.md) — 외부지식 충당 3-단계 (enrichment·내부적합 disjoint 짝, cross-ref)
- [ADR-046](ADR-046-researcher-role-redefinition.md) — Researcher 재정의 선례 + demand-anchored boundary (cross-ref)
- [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) — 정식 풀 플로우 + skip-offer 금지
- [ADR-144](ADR-144-orchestrator-autonomy-stop-taxonomy.md) — stop taxonomy (확정 대기 = 정당 멈춤 A1)
- [ADR-099](ADR-099-atlassian-allow-redefinition.md) / [ADR-100](ADR-100-confluence-doc-ssot-recognition.md) — Jira decision channel (async 원격 확정 — dual-input + timeout=재알림)
- [ADR-119](ADR-119-research-before-claims.md) — 제안 필요성 게이트 + advisory ceiling ground-truth
- `docs/orchestrator-playbook.md` — 설계 진입 preflight (user-final-sign-off-resolved sibling predicate) + §9.7.1 전이 표
- `plugins/codeforge-requirements/CLAUDE.md` + `agents/RequirementsPLAgent.md` — RequirementsPL elicitor/enricher 재정의 (Phase 2 배선)
- [CFP-2725](https://github.com/mclayer/plugin-codeforge/issues/2725) — carrier Issue
