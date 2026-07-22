---
adr_number: 154
title: 게이트 자기검증 forcing-function — hard gate/required job 의 silent-green·silent-fallback 위양성 차단(super-class 명명 + 3-way taxonomy + 2-control 계약 + presence/shape 메타-게이트 + honest-ceiling). 검출 sufficiency=undecidable 정직 천장, 신규 fail-closed 메타-게이트 + 재귀 자기적용
status: Accepted
category: governance
date: 2026-07-14
carrier_story: CFP-2684
supersedes: []
related_adrs:
  - ADR-082  # 재사용/super-class kin(amend 아님) — §결정11.A red-green-stash-proof(RED proof, carrier CFP-1330/1025) 는 REUSE(재codify 금지, cross-ref). super-class(write-time semantic truth verify) 는 kin 이나 §결정11 = "Wave 1 = declaration-only, 2 sub-decisions 모두 behavioral directive"(L939 verbatim) → CFP-2684 의 normative+phase-2+fail-closed 메타-게이트+재귀 자기적용 = 신규 mechanism → ADR-082 = cross-ref home 아님(§결정1 A2-5 Amendment prong 기각)
  - ADR-151  # 형제/증분(amend 아님) — self-test 채널 execution-liveness(L1) 봉인 + 8-field 인벤토리 스키마(REUSE — 신규 스키마 0). subject disjoint(self-test 코퍼스 ↔ 임의 게이트 core). AC-4 는 검출력을 G3/review 로 명시 DEFER(§결정7). axis-(ii) shape-scan = ADR-151 AC-4 enum→shape 1단계 증분(cross-ref, ADR-151 Amendment 아님 — landed self-tested `check_selftest_execution_liveness.py` 무침습). 신규 메타-게이트 self-test 는 ADR-151 인벤토리 1행 enroll(bijection cross-seal)
  - ADR-152  # 동형(cross-ref, 재codify 금지) — §결정1 discriminating-A(self-test)/B(product activation) 어휘 SSOT + §결정3/INV-G3-4 presence/구조 fail-closed·검출력 미강제 honest-ceiling 구조 + §결정8 born-hollow 금지(positive-leak 단정). CFP-2684 는 honest-ceiling 구조·discriminating 어휘를 상속(super-class 명명만 신규)
  - ADR-153  # disjoint sibling(CFP-2680) — 형제 패턴: "기존 required context 위에 편승하는 신규 fail-closed 게이트 = 신규 ADR". subject disjoint(ADR-153 = category-membership frozen-baseline / CFP-2684 = hard-gate 검출-integrity + silent-fallback taxonomy + identity-probe). ADR-153 over-claim 회피 교훈(honest-ceiling) 계승
  - ADR-119  # ethos — §결정6("조사했으므로 옳다" 검사연극 차단) + Amd2 §결정10(PASS = internal proxy 아닌 outcome ground-truth). 본 ADR = 이 원칙의 게이트-측 mechanization. honest-ceiling = "universal detection 기계강제" hard-claim 금지 근거
  - ADR-060  # evidence-gate — 신규 메타-게이트 = warning-tier 등록(day-1 required 승격 없음). required 승격(PR누적≥20 + failure=0 + sibling 3-tuple)은 별 carrier defer. 검사 등급/승격 축 ⊥ 검출보장 축(disjoint)
  - ADR-006  # §8 Test Contract authoring mechanism owner + §8.7 discriminating-fixture 선례(CFP-1334). 메타-게이트 자신의 self-test = TestContractArchitectAgent input + ArchitectAgent(chief) 통합
  - ADR-133  # ADR-RESERVATION atomic claim — 번호 154 발급. GH_TOKEN 부재로 OCC claim primitive 가 stale-state(max 152→153, ADR-153 이미 점유) 반환 → §결정4 fallback(fresh git ls-tree origin/main max=153 → 154). CFP-2680 row 153 동일 fallback 선례. dual-key 3-leg 정합
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs `wrapper/change-plans/cfp-2684-hard-gate-self-verification.md`)
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary(chief tie-break ladder). I-4 wording SSOT(super-class·taxonomy·ceiling 어휘 = 본 ADR §결정 wording 우선)
  - ADR-145  # 형제 게이트 G1(정합만) — AC-ID sub-letter 문법(`^AC-(\d+)$`, `ac_id.py` SSOT) 정합. wrapper-self ac-traceability 는 Change Plan §8 을 RTM 으로 강제(§결정6 location-resolution) → 본 Story RTM = Change Plan §8(13 AC)
  - ADR-146  # 형제 게이트 G4(정합만, amend 금지) — §결정11 A2-5 verbatim 구조 replicate + §8.8.5 정직 천장 동형. burden-flip 표준 상속
  - ADR-148  # 형제 게이트 G2(정합만) — INV-D2(선언 ⊥ 실행 2-표면) 정합. 메타-게이트 = stateless 단발 CLI 정적 lint(long-running/캐시/worker/restart 부재) → §8.5 N/A
  - ADR-150  # 형제 게이트 G5(정합만) — §8.9 single-axis 형판 + §8.9.5 4-잔여 honest-ceiling 동형. oracle 축 disjoint(DAST attack ⊥ 본 ADR 게이트 self-verification-integrity)
  - ADR-136  # execution-liveness 3요건(결정14, AND) 렌즈 — 메타-게이트 self-test born-broken/born-hollow 방지 상위 원리(L1 blocking 편승 / L2 canonical / L3 self-tested). 무수정 cross-ref
  - ADR-127  # no-exemption 자연 N/A 3축 AND — §8.3 Perf/§8.5 stateful/§8.7 UI/§8.9 DAST/§8.10 dark-path 자연 N/A = skip 아님(산출물 target 부재 ∧ downstream 무변경 ∧ 미래의무 무선결)
  - ADR-005  # N/A 명시 패턴 — §11 데이터 마이그레이션 N/A(governance, schema/data 무변경) + §8 자연 N/A substantive reason 근거
  - ADR-130  # path-filter 금지(required check permanent-pending 함정) + job-level `if:` graceful no-op — 메타-게이트 workflow 배선 시 준수(wrapper-self-only `if: github.repository ==` 는 정당)
  - ADR-139  # 3-sense 동음이의 가드 — self-verification-integrity(green-but-hollow) ⊥ liveness-orchestration(stall) ⊥ 지속-liveness-runtime(soak=G2). "test liveness"/soak 어휘 금지(참조 맥락 외)
related_concepts:
  - hard-gate-self-verification
  - silent-fallback-taxonomy
  - internal-control-identity-probe
  - lane-verification-floor
  - mutation-based-hollow-gate-detection
is_transitional: false
---

# ADR-154 — 게이트 자기검증 forcing-function (hard-gate self-verification): silent-green·silent-fallback 위양성 차단

## 상태

Accepted (2026-07-14 KST) — CFP-2684 carrier. "hard gate / required job 가 **green 이어도, 검증 대상을 실제 실행/검출하는지 보장되지 않으면 위양성**"(super-class: 게이트 green ≠ 검출 보증)을 도메인 불변식 위반으로 재정의하고, (a) 이 super-class 를 **명명**하며 (b) **silent-green ≠ silent-fallback ≠ honest-degrade** 3-way taxonomy 를 codify 하고 (c) 신규 hard gate 가 self-verification 번들(positive-control self-test + empty-target/unknown-input fail-closed + execution-trace + internal-control probe + honest-ceiling 선언)을 갖췄는지 **presence/shape 로 fail-closed 검사하는 신규 메타-게이트**를 신설하는 governance SSOT. **기계강제 천장은 presence/shape/format/fail-closed 까지만** — 검출 sufficiency(대표 결함류 실제 kill)는 원리상 undecidable(equivalent-mutant = halting 동치, oracle problem)이므로 **review-tier + honest-ceiling** 로 정직 공개한다. 강화(ratchet↑) 방향, 약화 surface 0(신규 required context 0, branch-protection 7-tuple 무변경, inter-plugin 계약 무변경, 신규 category 0). ADR-082/151/152(§11.A red-green-proof / execution-liveness 인벤토리 / discriminating-A·B·honest-ceiling)를 **cross-ref·재사용**하되 amend 하지 않는다(§결정 1 A2-5 both-prong 기각).

## 컨텍스트

사용자 원문(Story §1 verbatim, 원천 backlog plugin-codeforge #2181, ADR-후보 Epic #2151 close batch cross-Story 감사 N=3): "hard gate / required job 설계 시 **'게이트가 자기 검증 대상을 실제 실행/검출하는지' + 'silent-green / silent-fallback 위양성을 차단하는지'** 자기검증을 구조화(codify)한다." 배경 super-class = "게이트가 green 이어도, 게이트가 검증 대상을 실제 실행/검출하는지 보장되지 않으면 위양성".

### 도메인 사실 (3 Story 누적 위양성 계보 — threshold N=2 초과, origin/main 실측)

1. **S3(CFP-2159)**: review invariant-check 이식이 항상 green 통과(silent-green) 위험 → RED→GREEN 고의 결함 주입 3 run 으로 차단 `[verified: Story §1 verbatim]`.
2. **S5(CFP-2174)**: hard gate 가 6 lane 취득 경로 미실행(green 이어도 미검증) + CLI silent fallback(없는 에이전트명도 default 실행) 위양성 = **silent-fallback** anchor `[verified]`.
3. **S6(CFP-2178)**: AC-4 검증 regex 가 green 이나 실제 검출 0(거짓 green) = **silent-green** anchor `[verified]`.

**게이트 검증 3-layer 분해(도메인 렌즈, Story §2.1)**: L1 channel-liveness(self-test/게이트 CI 채널 alive — 이미 ADR-151 봉인, 신규 가치 0) / L2 target-count·non-vacuous(대상 존재 + 실행 흔적 emit + unknown-input fail-closed — 기계강제 신규 표면) / L3 detection-power(게이트가 실제 결함을 죽이는가 — **undecidable, review-tier**). 핵심 명제: **green verdict 은 L1·L2 까지만 기계로 ground-truth 보증 가능**, L3 는 원리상 기계 증명 불가 → **honest-ceiling**. "L3 를 기계 강제한다"는 주장 자체가 위양성(검사연극, ADR-119 §결정6).

**기존 cover 실측(genuine gap 확인)**: ADR-060 = 검사 등급/승격 framework(대상 실제 실행 여부 비대상) / ADR-082 §결정11.A = test↔production 결속(hard gate target 커버리지·silent fallback 비대상, 그리고 §결정11 자체가 "Wave 1 = declaration-only, behavioral directive"[L939]) / ADR-151 = self-test 채널 alive(L1)만(gate core 미봄) / ADR-152 = discriminating-A/B 어휘·honest-ceiling 구조는 소유하나 "게이트 green ≠ 검출 보증 = hard-gate 자기검증 super-class" 자체는 **미명명** → genuine gap.

### 왜 지금 (제안 필요성 게이트 — ADR-119 §결정9 3-질문 통과)

① **깨졌나·강제 요인**: 위양성 3 Story 누적(S3/S5/S6, threshold N=2 초과) = 관찰자 없어도 재발하는 결함 class. hard gate 가 green 이나 미검증/silent-fallback 이면 governance 안전망이 hollow. ② **이득 > 비용·리스크**: 저비용 정적 presence/shape 메타-게이트로 신규 hard gate 의 self-verification 번들 누락을 fail-closed 차단(FP 지뢰밭인 광역 silent-fallback scan 은 **채택 안 함** — §결정3). ③ **관찰자 없어도 할 일**: super-class 미명명이 매 신규 게이트마다 위양성 재발명을 유발(S3/S5/S6 = 매번 다른 관찰자가 개별 포착). GAP hard-claim 회피 — wrapper-self 는 이미 대규모 discriminating self-test corpus 보유(ADR-151 26/35), 갭은 "임의 hard gate core 의 self-verification 계약 미codify + super-class 미명명".

## 결정

hard-gate 자기검증 super-class 를 명명하고, silent-green/silent-fallback/honest-degrade 3-way taxonomy 를 codify 하며, 신규 hard gate 의 self-verification 번들 presence/shape 를 fail-closed 검사하는 신규 메타-게이트(warning-tier)를 신설하되, **기계가 강제 가능한 것(presence/shape/format/fail-closed)의 천장을 정직히 공개(honest-ceiling, 검출 sufficiency=undecidable)**한다. 착지 = 신규 `scripts/lib/check_*.py`(SSOT core) + `.sh` wrapper + byte-identical `templates/github-workflows/*.yml` + `.github/workflows/*.yml` mirror + discriminating self-test `tests/scripts/test_*.sh` + `docs/evidence-checks-registry.yaml` warning-tier row + ADR-151 인벤토리 1행 enroll(모두 Phase 2, 동일 Story). 결정 SSOT = 본 ADR / 파일 단위 배선 = Change Plan.

### 결정 1 — ADR 형태 판정 (Amendment vs 신규 ADR — A2-5 both-prong 기각 verbatim 구조)

**(ADR-146 §결정11 / ADR-151 §결정1 / ADR-152 §결정1 의 A2-5 판정 구조를 verbatim 적용 — "신규 ADR 없이 기존 ADR 변경 금지"(설계리뷰 P0) ∧ 그 역("기존 ADR 로 착륙 가능한데 왜 신규") 양 prong 을 모두 반증한다.)**

- **Amendment prong (ADR-082 로 착륙) = 기각**: ADR-082 super-class(write-time semantic truth verify)는 kin 이고 §결정11.A red-green-stash-proof(RED proof)는 **재사용(REUSE, 재codify 금지)**한다. 그러나 ADR-082 의 Amendment 들은 전부 "**Wave 1 = declaration-only**"(§결정11 L939 verbatim: "2 sub-decisions 모두 behavioral directive")다 — 즉 behavioral directive + Wave 2 mechanical wire 별도 sub-carrier defer. CFP-2684 는 normative+phase-2+coverage_required AC(AC-1/2/3/4/5/7/13)로 **이 Story 안에서 fail-closed 기계 메타-게이트 + 재귀 자기적용(AC-7)을 강제**한다 — ADR-151 §결정1 자신의 test("신규 fail-closed 메타-게이트 = 신규 ADR")를 충족하는 **신규 mechanism**. → ADR-082 = cross-ref, home 아님.
- **Amendment prong (ADR-151 로 착륙) = 기각**: subject-disjoint 다 — ADR-151 = self-test 코퍼스 execution-liveness(채널 alive, L1), CFP-2684 = **임의 hard-gate core 의 검출-integrity(L2) + silent-fallback taxonomy + identity-probe**. ADR-151 AC-4 는 검출력을 G3/review 로 **명시 DEFER**(§결정7)했다. axis-(ii) shape-scan 은 ADR-151 AC-4 의 enum-태그 검사를 **shape 검사로 1단계 증분**한 것이므로 cross-ref/증분으로 선언하되 ADR-151 Amendment 로 발의하지 않는다 — landed·self-tested `check_selftest_execution_liveness.py` 를 **무침습**(침습 = born-broken 위험 + subject 오염).
- **신규 ADR prong = 채택**: (i) **distinct context** — S3/S5/S6 위양성 계보(threshold N=2 초과). (ii) **distinct decisions** — super-class 명명 + silent-green≠silent-fallback≠honest-degrade 3-way taxonomy + 2-control 계약(positive-control ⊕ internal-control) + identity-probe(AC-13) + honest-ceiling. (iii) **distinct result** — 신규 fail-closed presence/shape 메타-게이트 + 재귀 자기적용. 별도 컨텍스트/결정/결과 블록이 중복이 아니다 → **신규 ADR-154**. Epic-CFP-2602 G-family 정합(ADR-145/146/148/150/151/152 = 각 신규 게이트 = 신규 ADR) + sibling ADR-153(CFP-2680 = 기존 required context 위 신규 게이트 = 신규 ADR, subject disjoint=category-membership).
- **ADR-082/151/152 무수정**: §11.A red-green-proof · execution-liveness 인벤토리 8-field 스키마 · discriminating-A/B 어휘·honest-ceiling 구조는 그대로 authoritative. 본 ADR 은 cross-ref/재사용만 하고 supersede/rewrite 하지 않는다 → "무단 확장" P0 발생 없음.

### 결정 2 — super-class 명명 + 3-way taxonomy (AC-6, AC-12 — compose, 재codify 0)

- **super-class 명명**: **"hard-gate self-verification — green ≠ detection guarantee"**(게이트 자기검증 — green 은 검출 보증이 아니다). 이 super-class 는 **기존 6+ named 조각을 cross-ref 로 compose** 하며 재정의 0: `red-green-stash-proof`(ADR-082 §11.A) / `vacuous-pass` / `execution-liveness`(ADR-151) / `discriminating-fixture`(ADR-006 §8.7) / `discriminating-A/B`(ADR-152 §결정1) / `mutation-hollow-gate` + `honest-degrade`. 신규 가치 = **super-class 명명 + silent-fallback taxonomy + identity-probe codify ONLY**(Story §4.3 중복 0 근거).
- **3-way taxonomy(antonym, AC-6 normative)**: 세 상태를 명확히 가른다 —
  - **silent-green**: 게이트 green 이나 **검출력 0**(regex 매치 0 / self-test 상시 통과) = **결함(위양성)**. 예: S6(CFP-2178).
  - **silent-fallback**: 게이트의 **검증 경로가 우회/흡수**(unknown-input→default, missing-file→skip, `2>/dev/null`·`|| true`, 미실행 경로) = **결함(위양성)**. 예: S5(CFP-2174).
  - **honest-degrade**: **의도적 fail-open + honest-ceiling 명시 선언**(대상 부재/도구 한계를 정직 공개하고 통과) = **정상(결함 아님)**. 예: ADR-151 §결정7 정직 천장, codeforge "부재 대상 정직 no-op" 관례(26 script / 127 occurrence).
- **honest-degrade 예외 명시 필수**: silent-fallback 방어는 honest-degrade 를 **오탐하면 안 된다** — 무차별 silent-fallback 검출은 massive false-positive(26/127 정당 no-op). taxonomy 는 "honest-degrade 는 결함 아님"을 명문화한다(§결정3 이 광역 scan 을 채택하지 않는 근거).

### 결정 3 — archetype C (hybrid): mechanizable/review split (D3)

Story §4.2 mechanizability 4-axis 실측을 baked 수용 아닌 firsthand 확증한 뒤 **archetype C(혼합)** 채택:

- **mechanical hard-floor (normative, phase-2, fail-closed)** = 신규 presence/shape 메타-게이트가 신규 hard gate 의 self-verification 번들을 검사:
  - positive-control self-test 가 **2-exit-differ SHAPE(axis ii)** 보유(clean GREEN ≠ mutant RED 를 포착·비교) — AC-1/2
  - empty-target fixture → **non-GREEN 또는 explicit honest-degrade 선언**(침묵 GREEN=FAIL) — AC-3
  - unknown-input fixture → **non-zero(fail-closed)** — AC-4
  - execution-trace(대상 count/스캔수/처리항목) emit — AC-5
  - internal-control probe present + discriminating-shape — AC-13
  - honest-ceiling 선언(gate 출력/doc/ADR) — AC-8
  - 3-way taxonomy 정의 presence — AC-6
  - super-class cross-ref no-dup presence — AC-12
  - 재귀 자기적용(자기 subject mutant→RED + inventory enroll) — AC-7
- **review-tier (declared, phase-1)** = 검출 sufficiency(대표 결함류 커버, AC-9) → `codeforge:review-responsibility` checklist 의무.
- **advisory** = 전수 mutation-score 상시 required 아님(비용 — nightly optional, AC-11).
- **★ 광역 archetype-B silent-fallback scan 채택 안 함(AC-10 conditional/declared 만)**: honest-degrade FP 지뢰밭(26 script / 127 occ 정당 no-op) — 무차별 스캔은 massive false-positive. silent-fallback 은 (a) taxonomy codify(§결정2) + (b) **per-new-gate fail-closed fixture presence**(§결정3 mechanical floor)로 다룬다, 광역 scan 아님.

### 결정 4 — honest-ceiling (P0 불가침, D4 — 가장 정밀 검토 대상)

- **메타-게이트는 presence/shape/format/fail-closed 까지만** 강제한다. **검출 sufficiency 를 증명할 수 없다** — L3(equivalent-mutant 판정)는 halting 문제와 동치(undecidable) + oracle problem(임의 프로그램의 "올바른 출력" 일반 결정 oracle 부재). AC-8 이 이 천장을 gate 출력/doc/ADR 에 선언한다.
- **ANY "universal detection 기계강제 / 완전 봉인" framing 금지** = CFP-2680 over-claim 재범 = 설계리뷰 P0. ADR-151 §결정7 / ADR-152 §결정3·INV-G3-4 의 정직 천장을 정확히 답습한다: "구조 fail-closed + 형식누락 저감 + 잔여 정직 공개"로 재약속, "완전 봉인" hard-claim 금지.
- **INV-5(ceiling immutable)**: 본 천장은 불변식 — 어떤 Amendment 도 L3 detection sufficiency 를 normative(기계강제)로 격상 금지. review-tier(declared)만. ADR-119 게이트=ground-truth / "absence of evidence ≠ evidence of absence" 정합.

### 결정 5 — 2-control 계약 (positive-control ⊕ internal-control probe — 대칭 반쪽)

Researcher 외부 이론 확증(Story §6.2): 게이트 무결성 = **2개 대조군(control)** 계약 —

- **positive-control (sanity mutant)**: "게이트가 결함 앞에서 반드시 RED 를 낸다"를 상시 증명(AC-1/2). silent-green 방어. curated 1-mutant 로 상시 강제(전수 mutation-score 아님, AC-11).
- **internal-control (identity probe, AC-13)**: "게이트가 검증하는 채널 자체가 살아있다(선언 대상 = 실행 대상)"를 known-answer 내장 기준(원문 대조 / resolved target echo / unknown-input negative 中 1+)으로 증명. **execution-trace(AC-5, 대상 실행 흔적 count)와 별개 축** — AC-5 = target-execution-count(대상 수/스캔), AC-13 = channel-identity known-answer probe(선언 대상이 실행 대상인가). S5 identity probe(시스템 프롬프트 원문 대조)의 일반화.
- **강제 = presence + discriminating-shape ONLY**: identity-bearing 게이트가 probe 없이 착지 = RED. probe 위반 fixture 로 RED 실증(presence + shape). detection sufficiency = review-tier(강제 아님).
- **★ identity-bearing 판정 = 결정론적 self-declared selector (AC-13 silent-skip 봉인)**: "어떤 실 게이트가 AC-13 강제 대상인가"는 메타-게이트의 semantic 추론(category-level "dispatch/routing/식별" 자연어 매칭 — 비결정·gameable)에 맡기지 **않는다**. 게이트/self-test 인벤토리 레코드의 **self-declared opt-in 필드 `identity_bearing: true/false`**(ADR-151 8-field 인벤토리 확장 또는 신규 게이트 레코드 필드 — 기계 검증 가능·honest applicability)로 확정한다: `identity_bearing: true` 선언 게이트는 probe presence 를 fail-closed 강제(부재 → RED), 미선언(`false`/필드 부재) 게이트는 미대상(정직 no-op). 이로써 "메타-게이트가 identity-bearing 게이트를 semantic 으로 놓쳐 AC-13 을 **silent-skip**"(이 Story 가 겨냥한 silent-under-enforcement 의 게이트측 재범)을 봉인한다. **applicability = self-declared(opt-in), probe presence = normative** — AC-13 은 probe presence 강제이지 detection sufficiency 강제가 아니므로 **INV-5(L3 detection sufficiency 불격상) 무손상**.
- **fail-open → fail-closed 재분류**: 미지 입력·대상 부재를 "조용히 통과(fail-open)"에서 "명시 실패(fail-closed)"로 재분류하는 것이 silent-fallback 방어의 확립 원리(AC-4).

### 결정 6 — silent-fallback parser fail-direction + 보안 축(§7, SecurityArch verbatim)

stakes=LOW(wrapper-self CI lint) — 유일 신규 공격 축 = repo-local 파일 body(untrusted) parse.

- **§7.3-crit fail-direction(최우선)**: 메타-게이트가 subject 파일을 파싱하다 **unparseable subject = fail-closed non-GREEN**(silent skip 금지). parse failure 가 조용히 통과 = 신규 게이트가 자신이 겨냥하는 silent-fallback 을 스스로 재범(self-ref 최악). `2>/dev/null` masking 금지(ADR-082 §11.B); explicit catch → exit 1.
- **AC-3 parser 2-분기 명확화**: "target 0건 = 정당 honest no-op(exit0 명시선언)" vs "target 존재하나 unparseable = fail-closed(exit1)". **warning-tier(workflow) ≠ silent-pass(script) 직교** — warning-tier 는 PR merge 만 안 막을 뿐, script 자체는 unparseable 에 exit1.
- **§7.7 self-parse 비대칭(both, 혼동 금지)**: (1) content-scan 에서 **자기 self-test 파일 self-source EXEMPT**(`_SELF_SOURCE_TOKENS` 형판 — 의도적 mutant fixture FP 회피) ⊥ (2) inventory enrollment 에서 **자기 self-test 강제 enroll+alive**(meta-hollow 금지, AC-7). fixed-point guard 불요(finite 파일, 재귀 spawn 0).
- **T-TRAVERSE = 유일 신규 가드**: axis-(ii) shape-scan 이 subject 파일 open 시 `(repo_root/rel).resolve()` 후 `is_relative_to(repo_root.resolve())`, escape/symlink-out → fail-closed reject. 나머지(ReDoS bounded quantifier / EXHAUST 4-axis bound / DESERIAL safe_load) = CFP-2635/2646 born-safe **REUSE**.
- **§7.3-self**: 신규 lint docstring 의 born-safe bound 서술 = paired proof-ref(self-test PERF 가드) + honest-ceiling("bounded degradation, 무해 아님") 동반(CFP-2646 resource-safety lint 이 이 docstring 을 스캔 — 무증거 단정 금지).
- §7.3 auth / §7.5 민감데이터 / §7.4.1 DR = N/A(정적 lint, 외부 입력·인증·민감데이터·상태 부재). (DR = §7.4 운영 리스크로 정식 이관 — §7.6 은 위협↔완화 매핑.)

### 결정 7 — self-application (AC-7) + inventory bijection cross-seal (최고위험 — born-hollow 금지)

- **재귀 자기적용(AC-7)**: 본 Story 신설 메타-게이트 자신이 규약을 만족 — 자기 positive-control self-test(자기 subject 에 mutant 주입→RED 실증) 보유 + CI 배선(channel alive) + ADR-151 인벤토리 1행 enroll(bijection). meta-hollow-gate 금지("게이트를 검증하는 게이트도 hollow 일 수 있다" — [[lane-verification-floor]] R-5).
- **born-hollow 금지(TestContractArch §8.2 verbatim)**: self-test = TC-CLEAN-PASS(valid 번들 + shallow observation → exit0, L3 ceiling 미강제 실증) + mutation set M1-M6(M1 positive-control-presence-check 제거 / M2 empty-match fail-closed 제거 / M3 unknown-input 제거 / M4 trace-check 제거 / M5 internal-control-probe 제거 / **M6 shape-scan→string-scan degrade** = axis-ii FN seal) 각각 positive-leak 단정 `KILLED ⟺ original(kill-fixture)=exit1 AND mutated=exit0`(ADR-152 §결정8 정합/파생 — 원문 단방향 `→ KILLED`+별도 역가드를 ⟺ 로 충실 합성한 의역, verbatim 아님; `exit≠(false,1)` 을 "killed" 로 오수용 **금지**) + mutation-validity double-guard(diff-q sed-actually-changed + py_compile mutated-is-valid-python) + **sed-mutation on REAL gate copy**(inline hand-copy = ADR-082 §11.A tautology = born-hollow, 금지) + LIVE ceiling-honesty check(실 docstring+registry+ADR grep, fixture-fallback 금지).
- **inventory bijection cross-seal(meta-hollow 무한후퇴 차단)**: 신규 메타-게이트 self-test 가 ADR-151 인벤토리에 missing 이면 **기존 selftest-execution-liveness 메타-게이트가 자기 FAIL** → two-meta-gate mutual cross-seal 로 meta-hollow 무한후퇴를 닫는다.

### 결정 8 — 0 신규 required context + warning-tier + 5-piece chain (D5)

- **배선 = 신규 non-required wrapper-self-only workflow** — exemplar 답습: `doc-frontmatter-category-test.yml` / `ac-traceability-self-test.yml` / `selftest-execution-liveness-test.yml`(모두 day-1 hard-fail, `if: github.repository == 'mclayer/plugin-codeforge'`). **branch-protection 7-tuple 무변경 — 신규 required context 0**(G-family 정합).
- **5-piece chain**: ① `scripts/lib/check_*.py`(Python SSOT core) ② `scripts/check-*.sh`(thin wrapper) ③ byte-identical `templates/github-workflows/*.yml` ④ `.github/workflows/*.yml` mirror ⑤ discriminating self-test `tests/scripts/test_*.sh`. 추가 배선: `docs/evidence-checks-registry.yaml` warning-tier row + ADR-151 인벤토리 1행 enroll(기존 8-field 스키마 REUSE — 신규 스키마 0).
- **required 승격 = defer**(ADR-060 evidence-gate 별 carrier) — PR누적≥20 + failure=0 + sibling 3-tuple 충족 시. day-1 warning-tier 유지(governance-tier dark quasi-pattern honest-ceiling — 아래 결과). born-broken 안전전제 = self-test suite green ∧ own-PR green THEN required 등록.
- **Phase 1(본 PR) = ADR + Change Plan NARRATIVE only**. 실 `.py`/`.sh`/`.yml`/self-test = Phase 2 구현 lane deliverable(ADR-151 §결과 precedent — 설계리뷰가 "메타-게이트 미구현"을 P0 로 올리면 Phase 2 deliverable 로 기각).

### 결정 9 — reuse cross-ref, 재codify 0 (AC-12)

- 산출 concept/ADR/lint 은 6+ 기존 named 개념을 **cross-ref**로만 묶는다(중복 정의 0): red-green-stash-proof(ADR-082 §11.A) / vacuous-pass / execution-liveness(ADR-151) / discriminating-fixture(ADR-006 §8.7) / discriminating-A/B(ADR-152 §결정1) / mutation-hollow-gate / honest-degrade.
- **신규 정의는 3영역 한정**: super-class 명명 + silent-fallback taxonomy + identity-probe. "이미 결정된 것(건드리지 말 것)": ADR-151 §결정7 honest ceiling / RED→GREEN 패턴 정의(ADR-082 §11.A) / evidence-check 등급(ADR-060) / discriminating-A/B 어휘·honest-ceiling 구조(ADR-152) — 모두 재정의 아닌 상속·cross-ref.

### 결정 10 — ADR 번호 발급 (ADR-133 §결정4 fallback — GH_TOKEN 부재 stale-claim 우회)

번호 **154** = **ADR-133 §결정4 fallback 채택**: OCC atomic claim primitive(`adr-reservation-atomic-claim.py --claimant ArchitectAgent:CFP-2684:run-1`)가 **GH_TOKEN 부재로 remote claim-state 를 advance/read 불가 → stale max(152)+1 = 153 을 반환**했으나, 153 은 **이미 CFP-2680(ADR-153)이 점유**(RESERVATION row 153 ∧ `ADR-153-*.md` 파일 ∧ frontmatter 존재 — dual-key 3-leg 모두 collision). CFP-2680 자신이 동일 GH_TOKEN-부재 fallback 으로 153 을 git-ls-tree 로 발급했기에 claim-state 가 advance 되지 않은 결과. verify-before-trust(ADR-119): claim 의 153 을 firsthand 반증(파일+row 존재 실측) → **fresh `git fetch origin main` + `git ls-tree --name-only origin/main archive/adr/` numeric max = 153(140~148·150·151·152·153, 149 orphan gap) → 154(collision-free)** 사용. dual-key 3-leg 정합: filename `ADR-154-hard-gate-self-verification-forcing-function.md` ∧ frontmatter `adr_number: 154` ∧ 본 RESERVATION row 154. claim(점유 직렬화) ↔ RESERVATION append(기록 책무) disjoint(ADR-133 §결정3 / ADR-070 chief author inline append).
> 정직 note(self-referential dogfood): ADR-번호 claim 채널 자체가 GH_TOKEN 부재 하에 **stale-state 를 조용히 반환**(silent-stale) — 본 ADR 이 겨냥하는 "green≠ground-truth" class 의 mild instance. 다만 이는 ADR-133 §결정4 fallback(git-ls-tree)이 정확히 존재하는 **honest-degrade 경로**이고 verify-before-trust 로 반증했으므로 결함 아님(정상). Phase-1 blocker 아님 — 다만 claim-state advance 신뢰성은 별 관찰(§결과).

## 대안 (기각 근거)

- **ADR-082 Amendment 로 착륙**: super-class 는 kin 이나 ADR-082 Amendment 는 전부 declaration-only(§결정11 L939) — CFP-2684 의 fail-closed 메타-게이트+재귀 자기적용 = 신규 mechanism → 기각, 신규 ADR-154(§결정1).
- **ADR-151 Amendment 로 착륙**: subject disjoint(self-test 코퍼스 ↔ 임의 게이트 core) + landed self-tested `check_selftest_execution_liveness.py` 침습 위험 → 기각, cross-ref/증분(§결정1).
- **광역 archetype-B silent-fallback scan**: honest-degrade FP 지뢰밭(26 script/127 occ) → 기각, taxonomy codify + per-new-gate fail-closed fixture(§결정3).
- **detection sufficiency 기계강제(universal detection)**: equivalent-mutant halting-동치·oracle problem → detection-forcing = 검사연극(ADR-119) + false-positive 유인 → 기각, presence/shape + review-tier honest-ceiling(§결정4).
- **AC-2 tautological same-path 완전배제 기계강제**: inline hand-copy 가 2-exit shape 로 통과 가능한 잔여는 shape-check 로 완전 봉인 불가 → 기각, honest-ceiling(AC-8) + review-tier(AC-9) + CodeReviewPL tautology-smell grep loop-closure(ADR-082 §11.A) cross-ref(§결과 game-able residual 정직 공개).
- **신규 required workflow context(tuple 확장)**: presence/shape doc-lint 는 신규 non-required wrapper-self-only workflow 로 충분 → 기각, 7-tuple 무변경(§결정8).
- **string-scan 으로 positive-control 검출**: RED→GREEN idiom 편차(FN) + S6 재범(self-referential hollow) → 기각, 구조 shape(2 exit 대조) 검출(§결정3, M6 seal).

## 결과

### 강화 방향 (ratchet↑, 약화 surface 0)

- 신규 required context **0**(branch-protection 7-tuple 무변경 — 신규 non-required wrapper-self-only workflow) / inter-plugin 계약 **무변경** / 신규 category **0**(governance 재사용). ADR-058 §결정5 강화 방향 — `sunset_justification` N/A.
- 신규 산출물(Phase 2): `scripts/lib/check_*.py`(메타-게이트 본체 — presence/shape fail-closed) + `scripts/check-*.sh` + `templates/github-workflows/*.yml` + `.github/workflows/*.yml`(byte-identical mirror) + `tests/scripts/test_*.sh`(재귀 self-test, M1-M6 positive-leak) + `docs/evidence-checks-registry.yaml` warning-tier row + `docs/selftest-execution-liveness-inventory.yaml` 1행 enroll.
- Phase 1(본 ADR + Change Plan) = narrative only. 실 코드 = Phase 2 구현 lane deliverable(ADR-151 §결과 precedent).
- **★ game-able residual 정직 공개(design-review 검사 대상)**: AC-2 shape-scan 은 **tautological same-path**(inline hand-copy 가 2-exit shape 로 위장)에 속을 수 있다 — 이 잔여는 기계로 완전 봉인 **불가**. cross-ref = AC-8(honest-ceiling) + AC-9(review-tier sufficiency) + CodeReviewPL tautology-smell grep loop-closure(ADR-082 §11.A). Change Plan §8.2 에 명시.
- **★ AC-13 열거-완결성 residual 정직 공개(AC-2 residual 과 대칭 — honest-ceiling thesis self-consistency)**: AC-13 identity-bearing 대상 판정이 self-declared `identity_bearing` flag 에 의존하므로(§결정5), **"모든 진짜 identity-bearing 게이트가 실제로 self-declare 했는가"(열거 완결성)는 기계 강제 불가 — self-declared 의존이라 declared 완결성**이다. 메타-게이트는 선언된 게이트의 probe presence 만 fail-closed 강제하고, 미선언 게이트를 identity-bearing 으로 재분류하지 못한다(semantic 재분류 = 비결정·검사연극 ADR-119 §결정6). 이 잔여는 AC-2 tautological same-path 잔여와 **동일 형식**으로 AC-8(honest-ceiling: 기계강제 천장 정직 공개) + AC-9(review-tier: 설계리뷰가 self-declaration 열거 완결성 판정)에 공개한다. AC-2 residual 은 공개하나 AC-13 분류-완결성 residual 은 미공개였던 **비대칭을 해소** — honest-ceiling thesis Story 의 self-consistency 회복. Change Plan §8.2 에 명시.
- **★ governance-tier dark quasi-pattern honest-ceiling**: 메타-게이트가 day-1 warning-tier → 자기 RED 가 merge 를 막지 않음 = "governance-tier dark" quasi-pattern. required-tier 승격은 ADR-060 evidence-gate 별 carrier defer(ADR-151 §결정5 precedent). Phase-1 blocker 아님 — honest-ceiling 로 공개.

### 경계 (disjoint 축 — 재유입 봉인)

- **⊥ L3 detection-power(검출 sufficiency)**: 게이트가 실제 결함을 죽이는가 = review-tier/undecidable. 본 ADR = L1(ADR-151 소유)+L2(신규) presence/shape 까지.
- **⊥ ADR-151(self-test 코퍼스 execution-liveness)**: self-test 채널 alive = ADR-151. 본 ADR = 임의 hard-gate core 의 self-verification 계약.
- **⊥ ADR-060(검사 등급/승격)**: 등급/승격 축 ⊥ 검출보장 축. 신규 메타-게이트 = ADR-060 등급 위 warning-tier 등록.
- **⊥ ADR-082 §11.A(regression test↔production binding)**: bug-fix regression 스코프 ⊥ 임의 hard-gate self-verification super-class. RED→GREEN 패턴 재codify 금지(cross-ref).
- **⊥ ADR-153(category-membership frozen-baseline)**: sibling, subject disjoint.

### Living Architecture 영향

`architecture_doc_impact` = **governance CI 층 추가**(hard-gate self-verification 강제 채널 — ADR-151 "governance CI 층 추가" 동형). 상세 = Change Plan §10.A.

## 해소 기준

N/A — permanent policy (permanent governance ratchet, ADR-058 §결정5 강화 방향). is_transitional: false.

## 관련 파일

- **Story**: `<internal-docs>/wrapper/stories/CFP-2684.md`(§7 설계 서사 / §3 ADR-154 carrier 확정)
- **Change Plan**: `<internal-docs>/wrapper/change-plans/cfp-2684-hard-gate-self-verification.md`(파일 단위 배선 + §8 authoritative RTM 13 AC + §7 보안)
- **신규(Phase 2 구현 lane deliverable)**:
  - `scripts/lib/check_<gate-self-verification>.py` — 메타-게이트 본체(정적 lint, presence/shape fail-closed AC-1/2/3/4/5/6/8/12/13; AC-7 재귀 자기적용 = self-test + inventory enroll 소관, .py core self-scan 아님 — Change Plan §5 정합)
  - `scripts/check-<gate-self-verification>.sh` — wrapper 진입점
  - `templates/github-workflows/<gate-self-verification>-test.yml` + `.github/workflows/<gate-self-verification>-test.yml` — byte-identical mirror(wrapper-self-only, non-required, day-1 hard-fail)
  - `tests/scripts/test_check-<gate-self-verification>.sh` — 재귀 self-test(TC-CLEAN-PASS + M1-M6 positive-leak + LIVE ceiling-honesty)
  - `docs/evidence-checks-registry.yaml` — warning-tier row
  - `docs/selftest-execution-liveness-inventory.yaml` — 1행 enroll(bijection cross-seal, 기존 8-field 스키마 REUSE)
- **Phase 1(본 ADR 동반)**: `docs/architecture/codeforge-family.md`(governance CI 층 1-line + Open Decisions row) · `archive/adr/ADR-RESERVATION.md`(154 row)
- **선례(exemplar 답습)**: `.github/workflows/doc-frontmatter-category-test.yml` · `.github/workflows/ac-traceability-self-test.yml` · `.github/workflows/selftest-execution-liveness-test.yml`(day-1 hard-fail wrapper-self-only)
- **cross-ref(재사용, amend 금지)**: ADR-082 §11.A(red-green-stash-proof) · ADR-151(execution-liveness 인벤토리 8-field) · ADR-152(discriminating-A/B·honest-ceiling·born-hollow positive-leak) · ADR-006 §8.7(discriminating-fixture) · ADR-153(sibling)
