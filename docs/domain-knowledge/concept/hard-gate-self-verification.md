---
kind: concept_definition
type: domain-knowledge
slug: hard-gate-self-verification
title: Hard-gate self-verification — green ≠ detection guarantee (super-class 명명 + silent-green≠silent-fallback≠honest-degrade 3-way taxonomy + internal-control identity-probe + presence/shape 메타-게이트 + honest-ceiling)
status: Active
updated: 2026-07-15
carrier_story: CFP-2684
related_adrs:
  - ADR-154  # carrier — super-class 명명 + 3-way taxonomy + 2-control 계약 + presence/shape 메타-게이트 + honest-ceiling(§결정1~10). 본 concept = ADR-154 결정의 domain-knowledge mirror
  - ADR-151  # execution-liveness(L1) 인벤토리 8-field REUSE + honest-ceiling(§결정7) 상속. subject disjoint(self-test 코퍼스 ↔ 임의 hard-gate core)
  - ADR-152  # discriminating-A/B 어휘 + honest-ceiling 구조 + born-hollow positive-leak 상속 (재codify 금지, cross-ref)
  - ADR-082  # §11.A red-green-stash-proof(RED proof) REUSE — write-time verify super-class kin (amend 아님)
  - ADR-119  # research-before-claims — 게이트 verdict = outcome ground-truth. honest-ceiling = "universal detection 기계강제" hard-claim 금지 근거(§결정6 검사연극 차단)
  - ADR-060  # evidence-gate — 신규 메타-게이트 = warning-tier 등록(day-1 required 승격 없음). 등급/승격 축 ⊥ 검출보장 축
  - ADR-006  # §8.7 discriminating-fixture 선례 (CFP-1334)
related_concepts:
  - vacuous-pass                            # silent-green 의 상위 class (검출력 0 green) — 재정의 없이 cross-ref
  - mutation-based-hollow-gate-detection    # meta-hollow-gate 차단 — 게이트 자기 무결성 축 (positive-control 상속)
  - lane-verification-floor                 # honest-degrade ≠ silent-skip 원리 SSOT (R-5 형제 축)
  - execution-based-review-verification     # green=ground-truth 검증 축 (verdict outcome-truth)
  - merge-time-adversarial-verification-gate  # tautology-smell grep loop-closure cross-ref (AC-2 residual)
tags:
  - hard-gate-self-verification
  - silent-fallback-taxonomy
  - internal-control-identity-probe
  - honest-ceiling
  - presence-shape-meta-gate
  - green-not-detection-guarantee
  - forcing-function
sources:
  - https://en.wikipedia.org/wiki/Scientific_control                     # positive/negative control — 2-control 계약(positive-control ⊕ internal-control) 외부 anchor
  - https://en.wikipedia.org/wiki/Mutation_testing                       # mutation testing — positive-control sanity mutant / hollow-gate 검출 이론 anchor
  - https://en.wikipedia.org/wiki/Halting_problem                        # equivalent-mutant = halting 동치 → 검출 sufficiency undecidable (honest-ceiling 근거)
  - https://en.wikipedia.org/wiki/Oracle_problem_(software_testing)      # oracle problem — "올바른 출력" 일반 결정 oracle 부재 (L3 미강제 근거)
  - https://en.wikipedia.org/wiki/Fail-safe                              # fail-closed vs fail-open — silent-fallback → 명시 실패 재분류 원리
---

## 정의

**Hard-gate self-verification** = hard gate / required job 이 **green 을 냈다는 사실만으로는 그 게이트가 검증 대상을 실제로 실행/검출했음이 보증되지 않는다**는 super-class 불변식이다. 한 줄 명명: **"게이트 green ≠ 검출 보증"(green ≠ detection guarantee)**. green verdict 은 (L1 채널 alive) + (L2 대상 존재·실행 흔적·미지 입력 fail-closed) 까지만 기계로 ground-truth 보증되며, (L3 검출력 = 게이트가 실제 결함을 죽이는가)은 원리상 기계 증명 불가(undecidable) — 따라서 review-tier + **honest-ceiling** 로 정직 공개한다.

본 개념의 신규 정의 표면은 **정확히 3영역**으로 한정한다(그 외는 기존 named 조각의 cross-ref, 재정의 0):

1. **super-class 명명** — "게이트 green ≠ 검출 보증"을 도메인 불변식으로 명명.
2. **silent-fallback taxonomy** — silent-green ≠ silent-fallback ≠ honest-degrade 3-way 를 antonym 으로 codify(아래 R-2).
3. **internal-control identity-probe** — 채널 자체가 살아있음(선언 대상 = 실행 대상)을 known-answer 로 증명하는 2번째 대조군(아래 R-3).

## 컨텍스트

3-Story 위양성 계보(threshold N=2 초과, origin/main 실측 — ADR-154 컨텍스트):

| Story | 증상 | taxonomy 위치 |
|---|---|---|
| S3 (CFP-2159) | review invariant-check 이식이 항상 green — 검출력 0 | **silent-green** anchor |
| S5 (CFP-2174) | hard gate 가 6-lane 취득 경로 미실행 + CLI 가 없는 에이전트명도 default 실행(우회) | **silent-fallback** anchor |
| S6 (CFP-2178) | AC-4 검증 regex 가 green 이나 실제 검출 0 (거짓 green) | **silent-green** anchor |

이 셋은 "게이트가 green 이나 미검증/우회"라는 동일 class 의 결함이며, super-class 미명명이 매 신규 게이트마다 위양성 재발명을 유발했다(매번 다른 관찰자가 개별 포착). 본 개념 = 그 class 를 명명하고, 신규 hard gate 가 self-verification 번들(positive-control self-test + empty-target/unknown-input fail-closed + execution-trace + internal-control probe + honest-ceiling 선언)을 갖췄는지 presence/shape 로 fail-closed 검사하는 메타-게이트의 도메인 근거다.

## 핵심 규칙

### R-1: super-class = "게이트 green ≠ 검출 보증" (기존 6+ 조각 compose, 재정의 0)

본 super-class 는 기존 named 조각을 **재정의 없이 cross-ref 로 compose** 한다. 조각과 그 SSOT(재codify 금지 — 각 소유 ADR 이 authoritative):

- `red-green-stash-proof` — RED proof (ADR-082 §11.A). REUSE.
- `vacuous-pass` — 검출력 0 green 의 상위 class. cross-ref.
- `execution-liveness` — self-test 채널 alive, L1 (ADR-151). REUSE.
- `discriminating-fixture` — clean↔mutant 구별 fixture (ADR-006 §8.7). cross-ref.
- `discriminating-A/B` — self-test(A) / product activation(B) 어휘 (ADR-152 §결정1). 상속.
- `mutation-hollow-gate` — 게이트를 검증하는 게이트도 hollow 일 수 있음 (meta-hollow). cross-ref.
- `honest-degrade` — 의도적 fail-open + 정직 공개 (아래 R-2). cross-ref.

신규 가치 = super-class **명명** + silent-fallback taxonomy(R-2) + identity-probe(R-3) codify ONLY.

### R-2: silent-green ≠ silent-fallback ≠ honest-degrade (3-way taxonomy, antonym)

세 상태를 명확히 가른다:

- **silent-green**: 게이트 green 이나 **검출력 0**(regex 매치 0 / self-test 상시 통과). = **결함(위양성)**. 예: S6.
- **silent-fallback**: 게이트의 **검증 경로가 우회·흡수**(unknown-input→default, missing-file→skip, `2>/dev/null`·`|| true`, 미실행 경로). = **결함(위양성)**. 예: S5.
- **honest-degrade**: **의도적 fail-open + honest-ceiling 명시 선언**(대상 부재/도구 한계를 정직 공개하고 통과). = **정상(결함 아님)**. 예: ADR-151 §결정7 정직 천장, "부재 대상 정직 no-op" 관례(26 script / 127 occurrence).

**honest-degrade 예외 명시(필수)**: silent-fallback 방어는 honest-degrade 를 **오탐하면 안 된다**. honest-degrade 는 **결함 아님** — 무차별 silent-fallback 검출은 massive false-positive(정당 no-op 26/127)이므로, taxonomy 는 "honest-degrade 는 결함 아님"을 명문화한다. 이것이 광역 archetype-B silent-fallback scan 을 **채택하지 않는** 근거다(ADR-154 §결정3).

### R-3: 2-control 계약 — positive-control ⊕ internal-control identity-probe

게이트 무결성 = **2개 대조군(control)** 의 대칭 계약:

- **positive-control (sanity mutant)**: "게이트가 결함 앞에서 반드시 RED 를 낸다"를 curated 1-mutant 로 상시 증명(silent-green 방어). 전수 mutation-score 아님.
- **internal-control (identity-probe)**: "게이트가 검증하는 채널 자체가 살아있다(선언 대상 = 실행 대상)"를 known-answer 내장 기준(원문대조 / resolved-target echo / unknown-input negative 中 1+)으로 증명. **execution-trace(대상 실행 count)와 별개 축** — count 는 "대상 몇 개를 스캔했나", identity-probe 는 "선언된 대상이 실제 실행 대상인가".

**identity-bearing 판정 = 결정론적 self-declared selector**: "어떤 실 게이트가 identity-probe 강제 대상인가"는 메타-게이트의 semantic 추론(자연어 매칭 = 비결정·gameable)에 맡기지 않는다. 인벤토리/게이트 레코드의 **self-declared opt-in 토큰 `identity_bearing: true`**로 확정한다 — 선언 게이트는 probe presence 를 fail-closed 강제, 미선언(`false`/부재)은 미대상(정직 no-op). **열거 완결성**("모든 진짜 identity-bearing 게이트가 실제로 self-declare 했는가")은 self-declared 의존이라 기계 강제 불가 = declared 완결성(honest-ceiling — R-4, review-tier).

### R-4: honest-ceiling (P0 불가침) — 기계강제 천장의 정직 공개

메타-게이트는 **presence/shape/format/fail-closed 까지만** 강제한다. **검출 sufficiency 는 증명할 수 없다**: L3(equivalent-mutant 판정)는 halting 문제와 동치(**undecidable**) + oracle problem. 따라서:

- 검출 sufficiency 는 **review-tier**(declared)만 — L3 를 normative(기계강제)로 격상하는 어떤 규칙도 금지(불변식).
- **presence ≠ truth**: 메타-게이트의 green 은 "번들이 형식상 존재한다"이지 "게이트가 결함을 실제로 죽인다"가 아니다.
- **"universal detection 완전 봉인" framing 을 하지 않는다** — 그런 hard-claim 은 검사연극(ADR-119 §결정6)이자 위양성. 본 개념은 "구조 fail-closed + 형식누락 저감 + 잔여 정직 공개"로만 재약속하며 **"완전 봉인"을 주장하지 않는다**(불가). bounded degradation.
- **game-able residual 정직 공개**: (a) AC-2 shape-scan 은 tautological same-path(inline hand-copy 가 2-exit shape 로 위장)에 속을 수 있고, (b) AC-13 identity-bearing 열거 완결성은 self-declared 의존이라 미선언 게이트를 semantic 재분류 못 한다 — 두 잔여 모두 기계로 **완전 봉인 불가**임을 정직 공개하고 review-tier(설계리뷰) + tautology-smell grep loop-closure(ADR-082 §11.A)에 cross-ref 한다.

### R-5: presence/shape 메타-게이트 계약 (mechanizable floor)

신규 hard gate 의 self-verification 번들을 **정적 presence/shape** 로 fail-closed 검사:

- positive-control self-test 가 **2-exit-differ SHAPE**(clean→exit0 ≠ mutant→exit1 를 2 exit-capture 로 관측·비교) 보유 — 순수 string-scan 아님(string-scan 으로 degrade 하면 self-test 가 RED).
- empty-target → **honest-degrade 선언 + exit0**(침묵 GREEN 금지), unknown-input → **fail-closed exit1**(silent-fallback 금지 — `2>/dev/null` masking 금지, explicit catch).
- execution-trace(대상 count/스캔 흔적) emit.
- identity-bearing 선언 게이트 → internal-control probe presence.
- honest-degrade ≠ silent-skip 는 [[lane-verification-floor]] R-2 와 동형 — 정직 면제 marker 가 silent skip 보다 우선.

## 경계

disjoint 축(재유입 봉인):

- **⊥ L3 detection-power(검출 sufficiency)**: 게이트가 실제 결함을 죽이는가 = review-tier/undecidable. 본 개념 = L1(ADR-151 소유) + L2 presence/shape 까지. 완전 봉인 아님.
- **⊥ execution-liveness(ADR-151)**: self-test 채널 alive = ADR-151 소관. 본 개념 = 임의 hard-gate core 의 self-verification 계약(subject disjoint).
- **⊥ evidence-gate 등급/승격(ADR-060)**: 등급/승격 축 ⊥ 검출보장 축. 신규 메타-게이트 = warning-tier 등록.
- **⊥ ADR-082 §11.A(regression test↔production binding)**: bug-fix regression 스코프 ⊥ 임의 hard-gate self-verification super-class. red-green-stash-proof 재codify 금지(cross-ref).
- **⊥ runtime soak/DAST/real-render**: 정적 lint — soak(G2)/DAST(G5)/real-render(§8.7) runtime 축 무관(wrapper-self plugin-meta-na).

## 관련 ADR

- **ADR-154** (carrier) — super-class 명명 + 3-way taxonomy + 2-control + presence/shape 메타-게이트 + honest-ceiling. 본 concept = 그 결정의 domain-knowledge mirror.
- **ADR-151** — execution-liveness(L1) + 인벤토리 8-field REUSE + honest-ceiling(§결정7) 상속. subject disjoint.
- **ADR-152** — discriminating-A/B 어휘 + honest-ceiling 구조 + born-hollow positive-leak 상속(재codify 금지).
- **ADR-082** — §11.A red-green-stash-proof REUSE (write-time verify super-class kin, amend 아님).
- **ADR-119** — 게이트 verdict = outcome ground-truth + 검사연극 차단(honest-ceiling 근거).
- **ADR-060** — 신규 메타-게이트 warning-tier 등록 host.
- **ADR-006** — §8.7 discriminating-fixture 선례.

## 변경 이력

| 일자(KST) | Story | 변경 |
|---|---|---|
| 2026-07-15 | CFP-2684 | 신규 — super-class 명명 + silent-green≠silent-fallback≠honest-degrade 3-way taxonomy + internal-control identity-probe codify. 기존 6+ named 조각 cross-ref(재정의 0), 신규 정의 3영역 한정. honest-ceiling(검출 sufficiency=undecidable, presence ≠ truth, 완전 봉인 미주장) 불가침. ADR-154 carrier. |
