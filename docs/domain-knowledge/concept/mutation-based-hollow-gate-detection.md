---
kind: concept_definition
type: domain-knowledge
slug: mutation-based-hollow-gate-detection
title: Mutation-based hollow-gate detection (LLM-as-mutator adversarial probe — surviving mutant ↔ 검사연극 매핑)
status: Active
updated: 2026-06-29
carrier_story: CFP-2464
related_adrs:
  - ADR-119  # research-before-claims Amd 2 — 게이트 verdict ground-truth, falsifiable evidence 의무 (surviving-mutant 주장 승격 룰 anchor)
  - ADR-052  # Codex proactive Touchpoint — Codex=신호원 dual-peer trigger origin 선례 (mutator dispatch 재사용)
  - ADR-077  # clarification 강제 재조사 — fact-check marker 무검증 승격 금지 invariant (surviving-mutant 주장 = hypothesis default)
related_concepts:
  - merge-time-adversarial-verification-gate  # Story A — 같은 적대적 검증 family, 다른 mechanism (review-of-output vs probe-the-detector)
  - clarification-driven-reinvestigation       # fact-check marker invariant 재사용 anchor
  - orchestrator-runtime-hook-enforcement      # mutator dispatch enforcement layer (Orchestrator inline 전용)
tags:
  - mutation-testing
  - adversarial-verification
  - llm-as-mutator
  - hollow-gate
  - surviving-mutant
  - equivalent-mutant
  - test-adequacy
  - flaky-test-contamination
  - false-positive-calibration
sources:
  - https://engineering.fb.com/2025/09/30/security/llms-are-the-key-to-mutation-testing-and-better-compliance/   # Meta ACH — LLM mutant+test 생성, equivalence detector precision 0.79→0.95
  - https://arxiv.org/abs/2501.12862                                                                              # Mutation-Guided LLM Test Generation at Meta (FSE 2025) — 9,095 mutants / 571 tests / 73% accept
  - https://arxiv.org/abs/2602.08146                                                                              # Test vs Mutant: Adversarial LLM Agents (AdverTest) — surviving mutant feedback loop, FDR 66.63%
  - https://arxiv.org/html/2408.01760v1                                                                           # LLMs for Equivalent Mutant Detection — prevalence 4~39%, best F1 86.58%
  - https://www.sciencedirect.com/science/article/pii/S2667305326000153                                          # GEM-LLM — 25~30% surviving 을 equivalent 로 분류, precision 98%
  - https://arxiv.org/abs/2010.13464                                                                              # What It Would Take to Use Mutation Testing in Industry — Facebook (diff-based, code-review surface, actionability)
  - https://mir.cs.illinois.edu/marinov/publications/ShiETAL19FlakyMutation.pdf                                  # Mitigating Effects of Flaky Tests on Mutation Testing (Shi et al. ISSTA 2019) — mutant-test pair 9% unknown / unknown mutant 79.4% 감축 / mutation score 5%p·mutant-test pair 10%p 변동
  - https://en.wikipedia.org/wiki/Mutation_testing                                                               # mutation testing / mutation score / mutation operator 표준 정의
---

## 정의

**Mutation-based hollow-gate detection** = 테스트가 PASS 상태인 코드에 **의도적·국소 결함(mutant)** 을 주입한 뒤 기존 테스트 스위트를 재실행해, 그 변이가 테스트를 PASS→FAIL(RED)로 뒤집는지를 관찰함으로써 **테스트 스위트가 실제로 무엇을 검증하는지(adequacy)** 를 역으로 falsify 하는 기법. 변이가 살아남으면(주입 후에도 테스트 PASS = surviving mutant) 그 게이트는 코드 실행만 하고 동작은 검증하지 않는 **hollow-gate(검사연극)** 이라는 강한 신호다.

코드 커버리지는 "테스트가 어떤 라인을 *실행* 했는가" 만 말하고 "그 동작을 *검증* 하는가" 는 말하지 못한다 — 100% 커버리지여도 assertion 이 없거나 `assertTrue(true)` 면 아무것도 보장하지 않는다. mutation testing 은 코드를 변형한 뒤 테스트가 실패하는지를 봄으로써 이 갭을 드러낸다 (출처: Wikipedia mutation testing; oneuptime / testRigor 산업 가이드).

codeforge 변형 = **LLM-as-mutator**: Codex 가 mutant 주입자(공격자), 기존 테스트 스위트가 detector(방어자). 이는 Meta ACH 와 AdverTest(Test vs Mutant) 가 산업·학계에서 실증한 패턴이다 (출처: engineering.fb.com 2025-09-30; arxiv 2602.08146).

## 컨텍스트

CFP-2464(Epic CFP-2457 Story B) 동인 = MEMORY.md 에 반복 기록된 **빈 게이트·검사연극(hollow-gate) 결함의 구조적 차단**. dogfood track record 에서 hollow-gate 가 실제로 출현했다 — CFP-2451 에서 "prefix 하드코딩 hollow-gate" 를 dual-peer 가 포착하고 mutation-RED(mutation 주입 후 테스트가 RED 로 바뀌는지 확인)로 검증한 사례, CFP-2440 에서 idempotency early-exit 미명시 → silent no-op 회귀를 설계리뷰가 차단한 사례가 그 부류다 (MEMORY.md). Story A(CFP-2458) 가 머지 직전 *산출물* 을 적대적 critic 으로 반증한다면, Story B 는 *detector(테스트 스위트) 자체* 를 변이로 반증한다 — **같은 적대적 검증 철학, 다른 mechanism**.

Codex API 한도 증가가 LLM-as-mutator 의 발동 계기. Meta 연구는 LLM 이 mutation testing 의 scale 장벽(전통적 mutation 은 변이가 너무 많고 노이즈가 심함)을 무너뜨렸음을 실증했다 (출처: InfoQ 2026-01, Meta ACH).

## 핵심 규칙 (외부 개념 → invariant 매핑)

### M-1: surviving mutant = hollow-gate 신호이되 **단정 아님** (equivalent mutant 양면성)

surviving mutant 의 의미는 이항(binary)이 아니라 양면적이다 — (a) **진짜 테스트 갭** (hollow-gate, 우리가 노리는 것) 또는 (b) **equivalent mutant** (구문은 다르나 의미가 동일해 어떤 테스트로도 죽일 수 없는 변이). equivalent mutant 비율은 실세계에서 **4~39%** (Madeyski et al. 2013, 출처: arxiv 2408.01760), 자바 실프로그램에서 최대 30% (출처: GEM-LLM, ScienceDirect S2667305326000153). 프로그램 동치성 판정은 **undecidable** — 모든 equivalent mutant 를 자동 식별하는 것은 수학적으로 불가능 (출처: arxiv 2408.01760).

**함의 (가장 중요한 unknown-unknown)**: "변이가 살아남았다 → 테스트가 hollow 다" 라는 적대적 주장은 **equivalent mutant 일 때 false-positive(억울한 검사연극 누명)** 가 된다. equivalent mutant 는 본질적으로 정의상 죽일 수 없으므로 "이 테스트를 보강하라" 는 요구는 **충족 불가능한 요구(impossible-to-satisfy demand)** — cry-wolf 의 가장 악성 형태. 따라서 surviving-mutant 주장은 **falsifiable evidence(어떤 동작 차이가 어떤 입력에서 관측 가능한가) 동반 + 재현 falsify 후만** "hollow-gate 결함" 으로 승격해야 한다. ADR-077 I-4 fact-check marker 무검증 승격 금지와 동형 — surviving-mutant 주장 = `[hypothesis]` default, PL/QADev 직접 재현 후만 `[verified]` 승격.

LLM equivalence detector 가 보조 가능하나 한계 명확 — best F1 86.58%(fine-tuned UniXCoder), prompting-only 는 미달, Meta ACH detector precision 0.79(기본)→0.95(static 전처리), GEM-LLM 은 surviving 의 25~30% 를 equivalent 로 precision 98% 로 분류 (출처: arxiv 2408.01760; engineering.fb.com; ScienceDirect S2667305326000153). 즉 detector 도 신호원이지 판정자가 아니다.

### M-2: Codex=신호원, PL/QADev 재현 falsify 후 승격 (Story A C-2 separation of duties 상속)

Story A C-2(implementer ≠ certifier)를 mutation 축으로 상속 — mutant 주입자(Codex) ≠ 결함 인증자(PL/QADev). AdverTest 의 two-agent 구조(Test agent T ↔ Mutant agent M)가 이를 학술적으로 뒷받침하나, 그 framework 도 surviving mutant 를 **자동 차단이 아니라 T 에게 피드백해 테스트를 정련** 하는 신호로 쓴다 (출처: arxiv 2602.08146). Facebook 산업 연구: 26명 개발자 중 거의 전원이 "원칙적으로 테스트 부족을 노출했다" 인정했으나 절반만 실제 행동 — actionability 가 핵심 장벽이며 mutant 는 advisory 신호 (출처: arxiv 2010.13464).

### M-3: flaky test 오염 — mutation 결과 신뢰성의 숨은 적 (unknown-unknown)

mutation testing 은 **테스트가 결정론적** 이라고 암묵 가정하나 flaky test 가 이를 깬다. 자바 22개 프로젝트에서 flaky 미처리 시 **mutant-test pair 의 9% 가 unknown status**(죽었는지 살았는지 판정 불가)였고, 저자 기법으로 unknown mutant 를 **79.4% 감축**했다. 반복 실행 간 변동 = mutation score **5%p**(평균) / mutant-test pair 차이 **10%p**(평균) (출처: Shi et al. ISSTA 2019, mir.cs.illinois.edu; IEEE 10675738 flaky 중복제거). **정정 이력**: 종전 "죽은 mutant 의 19% flaky-induced + mutation score ±4%p 변동" = 원논문 부재(환각, B 요구사항리뷰 Story §6.2 falsify) → 실측 수치로 교체.

**함의**: flaky test 는 두 방향으로 오염한다 — (a) **false kill**: flaky 가 우연히 실패해 hollow-gate 를 정상으로 위장(억울하게 hollow 를 놓침), (b) **false survive**: 결정론으로 보였던 kill 이 flaky 라서 surviving 으로 보고됨(없는 검사연극 날조). 따라서 surviving-mutant 판정 전 **동일 mutant 다회 실행으로 결정론 확인** 또는 flaky baseline 격리가 전제. 이것이 빠지면 적대 검증이 noise generator 로 전락 (cry-wolf → 도구 폐기).

### M-4: 전수 금지, diff-based + 소수 고가치 mutant (비용 모델 + actionability)

mutation testing 의 근본 비용 = 변이 1개당 테스트 스위트 1회 실행 = N배. 전통적 전수 mutation 은 변이가 폭증해 산업 적용을 막아왔다 (출처: 미시간 EECS survey; arxiv 2010.13464). 산업 정착 패턴은 두 축으로 수렴 —
1. **diff-based / commit-time**: Google·Meta 는 *변경된 코드에만* mutation 적용 + 미검출 mutant 를 code review 에 표시 (출처: Towards Incremental Mutation Testing, staff.um.edu.mt; arxiv 2010.13464; engineering.fb.com).
2. **소수 고가치 mutant**: Meta ACH 는 전통 mutation 대비 *fewer, more realistic, highly specific* mutant 를 특정 fault class 에 집중 생성 — 10,795 Kotlin class 에서 9,095 mutant + 571 test, 테스트 73% 수용 (출처: arxiv 2501.12862; engineering.fb.com). Facebook 의 핵심 원칙 = "테스트가 실패할 가능성이 높거나 actionable signal 이 없는 mutant 는 만들지 말 것" (출처: arxiv 2010.13464).

**함의**: codeforge 는 전수 mutation 금지 — Story §1 verbatim "전수 vs 샘플링은 설계 확정" 을 외부 근거로 **diff-기반 + 소수 고가치 변이(LLM-targeted)** 쪽으로 기울임. 적용 시점은 detector(테스트 스위트)가 이미 존재하고 GREEN 인 시점 (구현 lane 산출물 검증 직후 또는 구현리뷰 lane) — detector 가 없으면 변이를 죽일 대상 자체가 없다.

### M-5: false-positive calibration = 채택 생존 조건 (Story A C-4 cry-wolf 상속)

mutation 의 FP 원천은 critic 의 환각이 아니라 (M-1) equivalent mutant + (M-3) flaky 오염이라는 **mechanism-특유 원천** 이다. Story A C-4(cry-wolf: FP 10% 미만이어야 채택 생존)가 이 축에서도 성립하되, FP 억제 책임이 calibration 표현이 아니라 equivalence 식별 + flaky 격리라는 구조적 전처리에 있다. P2 급 surviving mutant(저영향)는 자동 차단 금지(기록 후 진행). 차단·FIX 승격 권한은 evidence 동반 + 재현된 hollow-gate 에 한정 — Codex 는 승인·차단 권한 없는 신호원.

## 경계

- **In scope**: LLM-as-mutator 로 테스트 스위트의 adequacy 를 적대적으로 falsify 하는 hollow-gate 탐지 개념 + 실패모드(equivalent / flaky) + 비용·시점 모델 + surviving-mutant 주장 승격 룰.
- **Out of scope**:
  - Story A merge-time adversarial verification gate — *산출물(PR diff)* 을 critic 이 review 하는 것 (review-of-output). 본 개념은 *detector(테스트)* 를 변이로 probe 하는 것 (probe-the-detector). 같은 적대적 검증 family, **다른 mechanism** — 중복 아님, defense-in-depth.
  - mutation 적용 lane·시점·전수/샘플링 구체 wiring + mutator dispatch enforcement 기구(Orchestrator inline matcher / CI job) — 설계 lane 위임(개념 layer 아님).
  - 테스트 *생성*(AdverTest·ACH 의 test-generation 측) — 본 개념은 *기존* 테스트 검증(probe)이 1차. 생성은 reshape 의 선택적 follow-on.
- **Anti-pattern**: surviving mutant 를 equivalent / flaky 구분 없이 즉시 "검사연극" 으로 자동 FIX 승격(M-1·M-3 false-positive 양산 → cry-wolf 폐기). 전수 mutation(M-4 비용 폭증). Codex 가 mutant 주입자이면서 동시에 hollow-gate 판정자(M-2 separation 위반).

## 관련 ADR

- **ADR-119** Amd 2 — 게이트 verdict ground-truth + falsifiable evidence 의무. surviving-mutant 주장 승격 룰(M-1)의 정책 anchor.
- **ADR-052** — Codex proactive Touchpoint, dual-peer Codex 신호원 선례. mutator dispatch 가 이 origin 을 mutation 축으로 재사용.
- **ADR-077** I-4 — fact-check marker 무검증 승격 금지. surviving-mutant = hypothesis default, 재현 후 verified 승격(M-1)의 재사용 anchor.

## 변경 이력

- 2026-06-29 KST — 초기 작성 (CFP-2464 ResearcherAgent Mandate 1·2 산출물). Meta ACH / AdverTest / equivalent-mutant LLM detection / flaky 오염 / Facebook 산업 연구 cited. Story A(merge-time-adversarial-verification-gate) 와 family 관계·mechanism 차이 명시.
