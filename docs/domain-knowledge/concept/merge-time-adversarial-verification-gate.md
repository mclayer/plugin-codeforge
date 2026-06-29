---
kind: concept_definition
type: domain-knowledge
slug: merge-time-adversarial-verification-gate
title: Merge-time adversarial verification gate (independent cross-model critic as final pre-merge corroboration + separation of duties)
status: Active
updated: 2026-06-29
carrier_story: CFP-2458
related_adrs:
  - ADR-119  # research-before-claims — Amd 2 게이트 verdict ground-truth + 실패 진단 falsification (독립 검증자 충원 동인)
  - ADR-052  # Codex proactive Touchpoint — dual-peer Codex 의 trigger origin 선례
  - ADR-077  # clarification 강제 재조사 — fact-check marker 무검증 승격 금지 invariant 재사용
related_concepts:
  - clarification-driven-reinvestigation   # 4-layer counter disjoint + fact-check marker invariant (재사용 anchor)
  - orchestrator-runtime-hook-enforcement  # merge-time gate enforcement layer (PreToolUse/CI vs behavioral)
tags:
  - adversarial-verification
  - merge-gate
  - cross-model-diversity
  - separation-of-duties
  - llm-as-critic
  - false-positive-calibration
  - dual-peer
sources:
  - https://asdlc.io/patterns/adversarial-code-review/                         # Adversarial Code Review 패턴 (Builder↔Critic, echo-chamber, pre-merge Review Gate)
  - https://openreview.net/forum?id=U19s6I8Q0u                                  # Beyond Self-Checking — cross-model ρ=0.54 vs 0.77 정량 이득
  - https://arxiv.org/html/2603.00539v1                                         # Systematic Overcorrection — 적대적 프롬프트 FNR amplify (26%→73%)
  - https://www.infoq.com/news/2026/04/claude-code-review/                      # Anthropic Code Review — verify findings, <1% incorrect, human-approval 필수
  - https://slsa.dev/spec/v1.0/provenance                                       # SLSA provenance/attestation (separation of duties anchor)
  - https://www.sonarsource.com/resources/library/quality-gate/                 # quality gate 산업 정의
  - https://zylos.ai/research/2026-04-22-autonomous-code-review-multi-agent-pr-analysis/  # cry-wolf effect / confidence calibration 산업 현황
---

## 정의

**Merge-time adversarial verification gate** = 구현리뷰 PASS + CI PASS 이후, 머지 직전(shift-right 최우측) 시점에 **구현 주체와 다른 모델 분포**의 독립 critic 에게 PR diff + Story 컨텍스트(요구사항·설계 의도·수용기준)를 주고 "왜 틀렸거나 불완전한가"를 1패스 적대적으로 반증(falsify)시키는 품질 게이트. 외부 산업·학계 개념 4축의 교차점이다 — (1) adversarial code review (Builder↔Critic echo-chamber 차단), (2) N-version / cross-model diversity verification (서로 다른 분포 = 독립 corroboration), (3) pre-merge quality gate (CI/CD 산업 표준), (4) separation of duties (implementer ≠ certifier, SLSA provenance 계열).

## 컨텍스트

CFP-2458 동인 = ADR-119 Amd 2 의 "게이트 PASS 를 내부 proxy 아닌 결과 ground-truth 로만 단정" 정책에 **독립 검증자를 충원**하고, dual-peer(Codex)가 Claude-miss P0/P1 을 반복 포착해온 패턴을 머지 직전으로 확장하는 것. Codex API 한도 증가가 발동 계기. 기존 게이트 provenance 백로그(#2322, Orchestrator self-attests gates → preventive)를 흡수.

핵심 메모리 증거 (dogfood track record): CFP-2285/2440/2445/2432 등 다수 Story 에서 dual-peer Codex 가 Claude-miss P0/P1 을 firsthand 포착(MEMORY.md). 단 **역방향도 실재** — Codex false-pos 를 PL 의 runtime-test falsify 로 교정한 사례 다수(CFP-2440 Codex 2건 false-pos, CFP-2449 Codex 2건 false-pos, CFP-2432 dual-peer 실 P1 포착). 즉 critic 은 신호원이지 판정자가 아니다.

## 핵심 규칙 (외부 개념 → invariant 매핑)

### C-1: cross-model diversity = 독립성의 실체 (self-checking 아님)

독립 검증의 이득은 "두 번 본다"가 아니라 **서로 다른 모델 분포가 complementary failure mode 를 가진다**는 데서 온다. "Beyond Self-Checking" — family 간 verifier correlation ρ=0.54 vs family 내 ρ=0.77, cross-model 이 self-checking 대비 +7.41%p. self-verification 은 planning/logic/math 전반에서 documented 약점.

**함의**: Codex(GPT-5) ≠ Claude(구현 주체) 분포 분리가 게이트 가치의 원천. 같은 모델 self-review 면 echo-chamber("double down on errors").

### C-2: separation of duties — implementer ≠ certifier

SLSA Level 4 = two-person review + provenance attestation. 핵심 = 만든 주체가 인증하지 못하게 하는 통제. #2322(Orchestrator self-attests gates)의 결함 = self-attestation = separation of duties 위반. merge-time 독립 critic = 이 위반의 구조적 차단(외부 인증자 충원).

### C-3: 적대적 framing 은 양날 — overcorrection bias amplify (가장 중요한 unknown-unknown)

"find why this PR is wrong" 식 적대적/설명요구 프롬프트는 **overcorrection(false-rejection) bias 를 증폭**한다. "Systematic Overcorrection" — GPT-4o FNR 이 simple judgment 26.2% → explanation+repair 73.2%(HumanEval) / 35.9% → 87.9%(MBPP). 거부 사유 = Logic Error 주장 48.2%(falsifiable evidence 없이), Added Requirements 환각 14.1%, Boundary Error 과적용 13.2%. "more detailed prompts may inadvertently introduce biases toward excessive fault finding".

**함의**: 적대적 프롬프트는 진짜 결함도 잡지만 **valid 코드를 대거 over-reject** 한다. 따라서 critic 출력은 자동 차단이 아니라 **falsifiable evidence(file:line) 동반 + PL 재검증** 을 통과해야 머지 보류로 승격. 이는 ADR-077 I-4 "fact-check marker 무검증 승격 금지" 와 동형 — critic 의 P0/P1 주장 = `[hypothesis]` default, PL 직접 falsify 후만 `[verified]` 승격.

### C-4: false-positive calibration = 채택 생존 조건 (cry-wolf)

FP 10% 미만이면 개발자가 모든 finding 을 진짜로 취급, 10~30% 면 "noisy" 라벨, 그 이상이면 도구 폐기("cry-wolf effect, 가장 흔한 폐기 사유"). Anthropic Code Review 는 "verify findings to reduce false positives" + "<1% incorrect" + **"will not approve PRs — human approval 필수"** 로 대응.

**함의**: P2 는 자동 차단 금지(기록 후 진행). 차단 권한은 P0/P1 + evidence 동반에 한정. critic 은 승인 권한 없음(보류 신호만) — human/PL 최종 판정 보존.

### C-5: single-pass 의 구조적 한계

"one opinion from a probabilistic system isn't evidence" — 단일 LLM judge 는 position bias / stochasticity / gap-filling(불완전 추론 over-credit) / sycophancy 노출. 1패스는 비용·지연 균형상 합리적이나, 그 출력의 인식론적 지위는 "단정"이 아니라 "반증 후보 제기"로 한정해야 한다(C-3·C-4 와 합류).

## 경계

- **In scope**: merge-time(shift-right 최우측) 단일 cross-model 적대적 게이트의 개념 정립 + 실패모드 + calibration 룰.
- **Out of scope**:
  - review lane 의 정규 dual-peer(Claude+Codex) — 이건 review-time(더 왼쪽), 본 게이트는 그 이후 머지 직전 추가 layer(defense-in-depth, 중복 아님).
  - mutation-testing peer(Story B) — 적대적 검증 패턴 재사용처이나 변이-기반(다른 mechanism).
  - 게이트 enforcement 기구 결정(PreToolUse merge matcher / CI job / Orchestrator inline) — 설계 lane 위임(개념 layer 아님).
- **Anti-pattern**: critic 의 P0/P1 주장을 evidence 없이 자동 머지 차단(C-3 overcorrection 으로 false-block 양산 → cry-wolf 폐기). self-model(Claude)로 self-review(C-1 echo-chamber).

## 관련 ADR

- **ADR-119** Amd 2 — 게이트 verdict ground-truth + 실패 진단 falsification. 본 게이트 = 그 정책의 독립 검증자 충원 mechanism (carrier 동인).
- **ADR-052** — Codex proactive Touchpoint, dual-peer Codex trigger origin 선례(본 게이트는 trigger origin = merge-time 으로 disjoint 확장).
- **ADR-077** I-4 — fact-check marker 무검증 승격 금지. C-3 critic 주장 승격 룰의 재사용 anchor.

## 변경 이력

- 2026-06-29 KST — 초기 작성 (CFP-2458 ResearcherAgent Mandate 1·2 산출물). 학계(overcorrection / cross-model / LLM-judge failure) + 산업(Anthropic Code Review / SLSA / cry-wolf) cited.
