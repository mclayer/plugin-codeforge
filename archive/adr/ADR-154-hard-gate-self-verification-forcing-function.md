---
adr_number: 154
title: 게이트 자기검증 forcing-function — hard gate/required job 의 silent-green·silent-fallback 위양성 차단(super-class 명명 + 3-way taxonomy + 2-control 계약 + presence/shape 메타-게이트 + honest-ceiling). 검출 sufficiency=undecidable 정직 천장, 신규 fail-closed 메타-게이트 + 재귀 자기적용
status: Accepted
category: governance
date: 2026-07-14
carrier_story: CFP-2684
supersedes: []
amendment_log:
  - amendment: 1
    carrier_story: CFP-2922
    date: 2026-08-10
    scope: >-
      적용 대상 확장(instrument-side) — §결정 5(2-control 계약) + §결정 6(fail-direction) +
      §결정 7(born-hollow 금지)의 적용 대상에 "리뷰·구현 레인이 게이트 판별력을 재기 위해 작성하는
      뮤테이션 측정 하네스"를 추가(§결정 3 은 확장 대상 아님).
      신규 normative = L-1(declared-unit 의미층 확증 = §결정 7 double-guard 3번째 leg, 측정 판정과
      독립 표면 요구) · L-2(주입 국소성 = 앵커·건수 한정 + 변경 **site** 수 assert; hunk 아님) 2 leg ONLY.
      대표 형상 ③(선택자 미포함 → "안 돌았다") ④(계기 사망 — cp949/WSL/MSYS) = 신규 0
      (③ = §결정 5 internal-control / ④ = §결정 5 internal-control ⊕ §결정 6 fail-direction 재사용).
      applicability = self-declared opt-in `mutation_harness`(§결정 5 identity_bearing 형판 재사용,
      normative 계수 비산입; instrument-side 는 2-control 양쪽 무조건 — identity_bearing 게이팅 미상속). 하네스는 §결정 8 5-piece chain ·
      ADR-151 인벤토리 enroll · 메타-게이트 스캔 대상으로 끌어들이지 않음(born-broken 방지).
      ADR-152/151/168 무접촉(구 082 = ADR-168 재제정본). retrofit defer 형판 = ADR-171(구 060 재제정본).
      근거 = CFP-2878 arc 침묵 주입/복원 실패(주체 ≥5 role-횡단, 전건 개정 전 스코프 밖).
      선행 판정 대응 = CFP-2878 CP L841(b)/L823 의 "ADR-154 확장 기각"은 subject 상이(N3 census
      runtime-emit ⊥ instrument-side) + A1-3 메타게이트 미신설로 mechanism 부담 미발생 → 미충돌.
    sunset_justification: >-
      N/A — ADR-154 = is_transitional:false permanent governance ratchet → ADR-058 §결정 5 sunset
      trigger 미해당. 본 Amendment = 강화 방향(약화 surface 0): 신규 required context 0 ·
      branch-protection 7-tuple 무변경 · inter-plugin 계약 무변경 · 신규 category 0 · 신규 workflow 0.
      INV-5(ceiling immutable) 무손상 — L-1 은 declared-unit assertion 이지 L3 detection sufficiency
      격상이 아니다.
    reinterpretation: false  # 본문 §결정 1-10 소급 재해석 아님 — 적용 대상 추가 + 전방 leg 추가이며 forward-only ratchet(landed 산출물 소급 무효화 0, retrofit = review-tier 별 carrier defer). 판정 근거 = 본문 §A1-4·A1-5 공통 절. 진위 = 리뷰 판정 축(honest-ceiling)
  - amendment: 2
    carrier_story: CFP-2963
    date: 2026-08-14
    scope: >-
      **적용 대상 확장 ONLY** — §결정 5(2-control)·§결정 6(fail-direction)·§결정 7(born-hollow
      금지)의 적용 대상에 "lane 산출물로 저작돼 repo 에 landed 된 게이트 스크립트"(**안정 좌표
      보유**, 이하 landed-gate)를 추가한다(A2-2). 그 실질은 **A1-3 조건부 유보의 해제 조건 명시**다:
      A1-3 이 하네스에 landed 계약을 걸지 않은 유일 사유("임시 산출물이라 스캔할 안정 좌표가 없다")가
      landed-gate 에는 성립하지 않는다. **이 조건절의 SSOT 는 ADR-154 이므로 본 Amendment 로 존치**한다.
      ★**신규 normative 0 — 본 Amendment 는 새 계약을 만들지 않는다.** 초판이 담았던 M-1(2-arm corpus
      동적 kill 분류) · M-2(분모 단조 하한) 및 경계·opt-in·sidecar manifest·정직 천장·carrier 결속은
      **ADR-175 로 이관**됐다(아래 형태 판정). 본 Amendment 는 그 ADR 로의 **포인터**만 보유한다.
      ★**형태 판정 전환 정직 기재(무언 폐기 금지)**: 초판 A2-1 은 §결정 1 3-prong 자기적용 **1/3** 로
      Amendment 를 채택했고 **반대 판정 가능성을 스스로 등재**했다. **설계리뷰(CFP-2963 Story §9.12
      DR-M5)가 그 판정을 뒤집었다** — 리트머스 재적용 = **2~3/3**((ii) 는 같은 문서 A2-6 이 "신규
      normative 는 M-1·M-2 둘뿐"이라 선언하므로 "1 점뿐" 이 자기 계수와 모순 / (iii) 는 초판이 이미
      자인), ADR-151 §결정 1 신규 ADR prong 3-conjunct = **3/3**. 채택 근거 3 중 2 가 반증됐고
      (근거 1 = 거짓 딜레마[§결정 1 자신이 "cross-ref/재사용만, supersede/rewrite 0" 으로 착지] /
      근거 3 = A1-1 선례 부적용[A1-1 은 0/3 · 신규 workflow 0, 본 건은 workflow 1 + 메타-게이트 1 +
      스키마 1 로 결정적 prong 이 반전]), **잔존 견고 근거는 근거 2(A1-3 조건절 SSOT 귀속) 1건뿐**이라
      그 1건만 본 Amendment 에 남긴다.
    sunset_justification: >-
      N/A — ADR-154 = is_transitional:false permanent governance ratchet → ADR-058 §결정 5 sunset
      trigger 미해당. 본 Amendment(축소 후) = 강화 방향(약화 surface 0): 신규 required context **0** ·
      branch-protection 8-tuple **무변경** · inter-plugin 계약 무변경 · 신규 category 0 ·
      **신규 workflow 0**(초판이 declare 했던 workflow 1 은 ADR-175 로 이관 — 은폐 아닌 귀속 이동).
      INV-5(ceiling immutable) 무손상 — 본 Amendment 는 적용 대상만 넓히고 detection sufficiency
      판정을 도입하지 않는다.
    reinterpretation: false  # 본문 §결정 1-10 및 Amendment 1 의 landed 대상 의미 불변 — 적용 대상 추가(A2-2)이며 forward-only ratchet(기존 76 self-test 소급 무효화 0, retrofit = 별 carrier defer). A1-3 은 무변경 유지(재해석 아닌 조건 해제 명시). 진위 = 리뷰 판정 축(honest-ceiling)
related_adrs:
  - ADR-175  # 파생 신규 ADR(CFP-2963) — Amendment 2 초판이 담았던 M-1(2-arm corpus 동적 kill 분류) · M-2(분모 단조 하한) normative 본체 + 경계·opt-in·sidecar manifest·정직 천장·carrier 결속의 착지점. 설계리뷰(Story §9.12 DR-M5)가 Amendment 착지 판정을 뒤집은 결과이며, 본 ADR 은 ADR-175 에 의해 **무수정 cross-ref** 된다(supersede/rewrite 0 — §결정 2/4/5/6/7/8/9 authoritative 유지). Amendment 2 는 A2-2 적용 대상(landed-gate) + A1-3 조건 해제 SSOT 귀속만 축소 존치
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

---

## Amendment 1 (CFP-2922, 2026-08-10) — 적용 대상 확장: 게이트 self-test → 리뷰·구현 레인 뮤테이션 측정 하네스(instrument-side). 신규 normative = L-1(declared-unit 의미층 확증) · L-2(주입 국소성) **2 leg ONLY**, 대표 형상 ③④ 는 **신규 0**(기존 조항 재사용). INV-5 무손상

### 배경 — 미승계는 "안 읽음" 이 아니었다 (CFP-2878 arc 실측)

CFP-2878(vacuous-PASS census + §10 시각 lint) arc 가 자기 Change Plan §13.1 에 규율 2종을 **"신설"** 했는데, 그 둘은 이미 본 ADR 정본에 있었다 — §13.1-32 ⓑ *"무해 대조군 필수"* = **§결정 5 2-control 계약** / §13.1-30 *"의미 층 확증"* = **§결정 7 mutation-validity double-guard**.

★**그리고 그 Change Plan 은 본 ADR 을 알고 있었다.** origin/main 판본 실측 `[ArchitectAgent firsthand 2026-08-10]`:

| 실측 | 값 |
|---|---|
| CP frontmatter `related_adrs` 에 ADR-154 | **존재**(`L15`) |
| CP §13.1-5(`L874`)의 ADR-154 인용 | **INV-5 단 하나** — *"L3 detection sufficiency 를 normative 로 격상 금지"* |
| CP 본문의 `identity-probe`(= §결정 5 AC-13 어휘) | **2회**(`L52`·`L69`) — ★**둘 다 "비대상" 선언** |

> ★**앵커 기질 고지 (설계리뷰 P2-5 수리 — 근인이 리뷰 진단과 다르다)**: 위 앵커는 **전부 `origin/main` 판본 기준**이다. 초판은 `L874` 자리를 `L588` 로 적었는데, 근인은 *저작 오류*가 아니라 ***판본 혼입***이었다 — `L588` 은 **3커밋 뒤진 로컬 체크아웃에서는 정확한 앵커**이고 `origin/main` 에서 같은 항이 `L874` 다. 즉 두 판본에서 읽은 앵커를 한 표에 섞었다. 설계리뷰의 판별 대조군(나머지 앵커 verbatim 일치)이 성립한 이유도 여기 있다 — 그 앵커들은 전부 `origin/main` 추출분이었다. ★**이것이 본 Amendment 가 A1-6 형상 ④ 로 codify 한 *"읽은 대상이 내가 읽으려던 대상인가"* 의 자기 실패**이며, 수리 시 인용 앵커 **8개 전항**을 `origin/main` 으로 재대조했다(`L15`·`L52`·`L69`·`L874`·`L916`·`L920`·`L921`·`L950` — 1건 정정, 7건 일치) `[ArchitectAgent firsthand 2026-08-10]`.

⇒ 저자는 §결정 5 의 어휘까지 읽었고, **건설 중이던 산출물(N3 census 게이트)에 대해 올바로 스코프 아웃했다.** 빠진 것은 그 조항이 **측정하는 계기(instrument)** 에도 걸린다는 문면이다. ★**근인 = 문면 갭이지 주의력 결손이 아니다. 문면 갭의 처방은 감사 강화가 아니라 문면 갱신이다** — 그래서 본 Amendment 가 곧 미승계 처분이다.

**문면 침묵 실측 (null 주장 + 판별 대조군 — 동일 파일·동일 도구 ripgrep, shell 미경유)** `[ArchitectAgent firsthand 2026-08-10]`:

| 패턴 | hit | 역할 |
|---|---|---|
| `리뷰 레인 \| review lane \| review-lane \| 측정 하네스 \| harness` | **0** | null 주장 |
| `review-tier \| honest-ceiling \| 정직 천장` | **29** | 대조군(혼합) |
| `게이트 자기검증` | **3** | ★한글 전용 대조군 |

술어는 살아 있고 **대상이 없다.** 그리고 §경계 블록이 5개 disjoint 축을 열거하는데 **리뷰-레인 측정 하네스는 포함도 배제도 되어 있지 않다 — 침묵이다.** CP §13.1-31 조건 ⓘ 가 세운 명제(*"명세가 침묵하는 축에서의 `pin` 은 명시가 아니라 결정"*)를 ADR 측에 대칭 적용하면, **침묵 축의 승계 기대는 기대가 아니라 요행**이다.

**발생 규모 (★기질 병기 — 절대값은 술어-의존)**: CP §13.1-30(`L920`)은 *"같은 형 6건 / 주체 6"* → 갱신 *"주체 7 · 사례 9+"*; PMO 회고 패킷은 *"11건 · 주체 5(회고 후 6)"*. **계수 술어에 따라 값이 갈린다.** 따라서 본 Amendment 는 근거를 값이 아니라 **주체 다수성(≥5 · role-횡단 — 설계 PL · 구현 PL · 구현 리뷰 PL · peer · Orchestrator · PMO)** 에 건다. 결론은 술어-불변이다: **개인 부주의가 아니라 절차의 구조적 공백**이며, 그래서 규율이지 반성문이 아니다. ★그리고 **그 전부가 리뷰·측정 레인의 뮤테이션 하네스에서 났지 gate self-test 에서 나지 않았다** — 즉 전부 개정 전 스코프 밖이었다.

**계기 사망은 이 arc 밖에서도 살아 있다 (본 Amendment 판정 세션 자기 실증, 2026-08-10)** `[ArchitectAgent firsthand]`:

- bash `sed -n '/결정 8/,/결정 9/p'` 가 한글 범위지정 오작동으로 **§결정 1 구간을 반환**했다. Grep 도구(shell 미경유)로 전환 후 정상. **측정 명령이 성공 종료했고 출력도 있었으나 대상이 아니었다.**
- 로컬 `codeforge-internal-docs` 체크아웃이 **3커밋 뒤**였고 그 판본 §13.1 은 **23항까지뿐**이었다 — 그대로 읽었으면 *"§13.1-29~32 부재"* 라는 **거짓 null** 을 냈다. `git show origin/main:` 재측정으로 회피. ★이것도 같은 형이다: **읽은 대상이 내가 읽으려던 대상인가** = §결정 5 internal-control 의 문서 축 instance.

### A1-1 — 형태 판정: Amendment 채택 · 신규 ADR 기각 (§결정 1 A2-5 3-prong **자기적용 = 0/3**)

§결정 1 의 신규-ADR 3-prong 을 본 후보에 그대로 적용한다:

| prong | 판정 | 근거 |
|---|---|---|
| (i) distinct context | **기각** | 본 ADR 이 이미 명명한 class 의 **네 번째 발생지**. §컨텍스트 super-class 정의(*"게이트가 green 이어도 … 위양성"*)가 그대로 덮는다. 새 인스턴스가 distinct context 라면 본 ADR 은 재발마다 재발행돼야 한다 |
| (ii) distinct decisions | **기각** | 후보의 normative 내용이 §결정 5·§결정 7·§결정 6 에 **1:1 사상**된다. 신규 *결정 블록* 이 아니라 기존 조항의 **leg** 다 |
| (iii) distinct result | **기각(결정적)** | 본 ADR 이 인용하는 ADR-151 §결정1 test = *"신규 fail-closed 메타-게이트 = 신규 ADR"*. 후보는 신규 게이트를 낳지 않는다 — 기계화는 이미 `plugin-codeforge#2922` ⓑ 소유. **결과가 남의 carrier 인 ADR 은 distinct result 가 없다** |

**0/3 → 신규 ADR 기각.** 독립 근거 2: 여기서 새 ADR 을 쓰면 본 ADR 이 두 번 금지한 것을 어긴다 — §결정 9 *"재codify 0"*, §결정 2 *"신규 가치 = super-class 명명 + silent-fallback taxonomy + identity-probe codify **ONLY**"*. **informational 강등도 기각** — 위 §배경이 문면 갭을 실측했고, 문면 갭은 문면으로만 닫힌다. 경쟁 home 4종 배제(무언 폐기 금지): **ADR-158** = 자기 title 이 `#2684 게이트 자기검증 disjoint` 명시 선언 / **ADR-163** = telemetry event ledger 아키텍처(계기 무결성 축 아님) / **ADR-073** = 주어가 Orchestrator role(본 건은 주체 ≥5 role-횡단) / **ADR-082(현 ADR-168 재제정)** = §결정 1 이 든 **primary 경쟁 home** — 기각 근거는 그대로 유효(subject = bug-fix regression 의 test↔production 결속 ⊥ 계기 무결성)이나 ★**판별자는 역전됐다**: §결정 1 은 ADR-082 를 *"Amendment 가 전부 declaration-only"* 라서 기각했는데 **본 Amendment 자신이 declaration-only 다**(A1-8 이 자인). 따라서 *"declaration-only 라서 그 home 이 아니다"* 는 본 건에 쓸 수 없고, **기각은 subject-disjoint 만으로 선다** — 근거를 갈아끼운다.

★**P1-2 — 선행 판정 대응 (CFP-2878 CP 가 ADR-154 확장을 이미 심의하고 기각했다. 무언 폐기 금지의 자기 적용)**: 본 Amendment 의 증거 기반 전체를 제공한 그 CP 가, **같은 ADR 로의 확장을 정면으로 검토하고 기각**했다 — `L841(b)` verbatim: *"ADR-154 를 home 으로 확장 — 새 modality(self-test shape 검사 → runtime emit)를 번들에 추가하거나 **`별 selector 메타게이트`를 신설**해야 하는 **신규 mechanism 부담** + §15.b 아래 이미 작동 중인 landed 선례 존재로 **parsimony 열위 → 기각**"*, `L823`: *"…ADR-136 §15.b 가 이미 별도 mechanism 으로 충족하므로 **ADR-154 확장 없이 해소**"*. **그 기각은 유효하고 본 Amendment 와 충돌하지 않는다 — subject 가 다르다**:

| 축 | CP 가 기각한 확장(`L823`·`L841(b)`) | 본 Amendment |
|---|---|---|
| subject | **N3 census 게이트**(file-set-scan 산출물의 runtime emit modality) | **instrument-side 뮤테이션 하네스**(측정 계기) |
| 요구 mechanism | 번들에 새 modality 추가 **또는 별도 selector 메타게이트 신설** | ★**메타게이트 신설 0**(A1-3) — selector 는 도입하되 **스캔 표면을 만들지 않는다** |
| 대안 존재 | ADR-136 §15.b 가 이미 충족(landed 선례) → parsimony 열위 | 대체 mechanism **부재**(문면 침묵 실측, §배경) |

★**그 기각 사유가 본 건에 재발하지 않는 이유가 정확히 A1-3 이다** — CP 가 부담으로 든 *"`별 selector 메타게이트`"* 중 **selector(`mutation_harness`)만 취하고 메타게이트는 취하지 않으므로 `L841(b)` 의 mechanism 부담이 발생하지 않는다.** 이 배치가 본 Amendment 의 parsimony 근거다.

### A1-2 — 적용 대상 확장 (스코프 — **신규 normative 0**)

§결정 5(2-control 계약) · §결정 6(fail-direction — unparseable/미판독 subject = fail-closed, 침묵 skip 금지) · §결정 7(born-hollow 금지)의 적용 대상에 다음을 **추가**한다:

> **리뷰·구현 레인이 게이트의 판별력을 재기 위해 작성하는 뮤테이션 측정 하네스**(ad-hoc·임시 포함) — 이하 **instrument-side**.

근거 = §결정 2 super-class(*"green ≠ detection guarantee"*)의 **계기 측 instance**. 게이트가 자기 검증 대상을 실제로 검출하는지 보장되지 않으면 위양성이듯, **계기가 자기 측정 대상을 실제로 재는지 보장되지 않으면 그 측정값도 위양성**이다. 새 개념이 아니라 같은 명제의 한 층 위 적용이다.

**§경계 갱신(침묵 제거)** — 기존 §경계 5행에 다음을 더한다: **instrument-side 뮤테이션 하네스 = ⊥ 아님(본 ADR 대상)**. 다만 L3 detection-power 는 여전히 ⊥ 다(§결정 4 무손상).

### A1-3 — ★경계: 하네스에 landed 계약을 걸지 않는다 (born-broken 방지)

instrument-side 확장은 **계약(§결정 5 · 6 · 7)에 한정**한다 — 세 결정은 A1-2 가 열거한 확장 대상이며, **그 밖의 결정(§결정 3 mechanical floor 포함)은 확장 대상이 아니다**(A1-6 이 커버 조항을 고를 때 이 목록에 구속된다 — 설계리뷰 P2-3 의 근인). 다음으로는 **끌어들이지 않는다**:

- **⊥ §결정 8 5-piece chain**(`.py` SSOT core / `.sh` wrapper / template yml / mirror yml / self-test) — 하네스는 landed 산출물이 아니다
- **⊥ ADR-151 인벤토리 enroll**(bijection cross-seal) — 임시 산출물을 인벤토리에 넣으면 항상-stale
- **⊥ 메타-게이트 정적 스캔 대상** — 스캔할 안정 좌표가 없다

★**임시 산출물에 landed 계약을 걸면 born-broken 이다.** 본 Amendment 는 하네스에 *지켜야 할 것* 을 주되 *스캔당할 자리* 를 주지 않는다. 그 대가는 A1-8 정직 천장에 공개한다.

### A1-4 — 신규 normative ① **L-1 의미층 확증 = declared-unit assertion** (§결정 7 double-guard 의 **3번째 leg**)

**현 조항**: `mutation-validity double-guard(diff-q sed-actually-changed + py_compile mutated-is-valid-python)` = ⓐ 바이트 층 + ⓑ 문법 층.

**ⓐ 를 firsthand 반증한 실측** (CP §13.1-30 `L921`, 7번째 실증): 구판 *"주입 직후 `patched != original`"* assert 가 **통과했음에도 의미상 no-op** 이었다 — 신판 parity step 앞에 **공백행**이 있어 지운 개행이 주석이 아니라 그 공백행에 붙었고, **바이트는 변했으나 YAML 은 그대로 5 step**. ★**그 상태의 초록을 읽었으면 *"미봉합"* 이라는 정반대 결론이 났다.**

⇒ **신규 leg ⓒ**: **주입 직후, 그 주입이 *의도한 의미 단위* 를 실제로 바꿨는지 피검 대상의 의미 표현(파싱 결과 · census · exit code)으로 assert 한다.** 바이트 차이는 주입의 **필요조건이지 충분조건이 아니다** — ⓐ 는 최소 조건으로 존치한다.

★**ⓒ 의 독립성 요건 (설계리뷰 P2-4 — 순환 차단. ★INV-5 의 *반대* 방향 리스크: 과대가 아니라 공허)**: ⓒ 의 assert 는 **측정 판정과 독립한 입력·표면**에서 수행한다 — ***측정 판정에 쓰인 exit code 를 ⓒ 의 근거로 재사용하는 것을 금지한다.*** 이유: §결정 7 의 KILL 판정 자체가 exit code 기반(`KILLED ⟺ original(kill-fixture)=exit1 AND mutated=exit0`, `:153`)이므로, ⓒ 를 **같은 입력·같은 표면**의 exit code 로 세우면 **ⓒ ≡ 측정 결과** 가 되어 tautology = **born-hollow** 다(§결정 7 이 `sed-mutation on REAL gate copy` 로 금지한 그 형의 재현). 허용 표면 예: 피검 대상의 **파싱 결과**(`len(steps)==4`) · **census 값**(`violations=148`) · 측정과 **다른 입력**에 대한 exit code. **같은 실행의 exit code 단독 = 불가.**

**★왜 더 강하게 쓰지 않았는가 (rationale — 약하게 쓴 이유가 계약의 일부다)**

L-1 은 **저자가 선언한 단위**에 대한 델타 assert 만 강제한다(declared-unit assertion). ***"의미상 no-op 을 검출한다" 로 쓰지 않는다 — 금지다.***

- 후자는 임의 뮤테이션의 semantic non-equivalence **일반 판정** = equivalent-mutant = halting 동치이며, **§결정 4 INV-5(ceiling immutable) 정면 위반** + over-claim P0 다.
- 따라서 L-1 은 **선언되지 않은 축의 no-op 은 잡지 못한다.** 이 약함은 결함이 아니라 **천장**이다.
- ★**그리고 이 절제 자체가 본 Amendment 가 codify 하는 명제와 동형이다** — CFP-2878 이 세운 *"단언 ≠ 판별"*(CP §13.1-32 `L950`)은 **단언을 판별로 과대주장하지 말라**는 것이다. L-1 을 *"no-op 검출"* 로 쓰면 **이 Amendment 가 자기가 codify 하는 규율을 첫 문장에서 어긴다.**
- **형판** = ADR-152 §결정 4 *"declared-consistency 를 강제할 뿐 detection 을 강제하지 않는다"*(cross-ref, 재codify 0).
- ★**다음 저자에게**: 이 문면을 *"약하게 쓴 실수"* 로 읽고 강화하지 말 것. **강화 시도가 곧 INV-5 위반이다.**

### A1-5 — 신규 normative ② **L-2 주입 국소성** (§결정 7 신규 leg)

**형상**: 전건 `str.replace` 치환이 **실행행과 주석을 동시에** 바꿔 단언 실패가 났고, 그것을 **KILL 로 오독**했다(거짓 KILL). ★이 arc 에서 Orchestrator 와 Codex peer 가 **같은 술어로 같은 오답**을 냈다.

**현 2-leg 어느 것도 "의도한 자리만 바꿨는가" 를 보지 않는다** — ⓐ 는 "바뀌었는가", ⓑ 는 "여전히 유효한가" 만 본다.

⇒ **신규 leg**: **치환은 앵커·건수 한정(anchored / count-bounded)으로 수행하고, 변경된 site 수가 의도한 수와 일치함을 assert 한다.** 전건 치환(`replace()` 무제한 · 전역 `s///g`)은 하네스에서 금지하며, 불가피하면 변경 site 를 열거해 선언한다.

★**계수 단위 = `site`(치환 술어의 **매치 발생 건수**), `diff hunk` 아님 (설계리뷰 P2-1 — 단위 분기 봉합)**: 두 단위는 같지 않고, **틀린 단위를 고르면 이 leg 이 존재하는 이유가 된 바로 그 결함을 통과시킨다.** 본 leg 을 낳은 형상(실행행 + 인접 주석행 동시 치환)은 ***site = 2 · hunk = 1*** 이다 — `hunk == 1` 로 구현한 하네스는 **그 결함에 GREEN 을 준다.** ★*"단언 ≠ 판별" 이 자기 leg 에 걸린 자리*이므로 단위를 문면에 고정한다: **assert 대상 = 술어가 실제로 매치·치환한 site 수** (예: `re.subn()` 의 반환 건수 · `sed` 의 치환 카운트). 인접 행 병합으로 site 수를 은폐하는 hunk/line 단위 계수는 **본 leg 의 충족으로 계상하지 않는다.** (`#2922` ⓑ 공유 유틸의 API 계약이 이 단위로 갈린다 — 구현 전 확정 필요.)

**INV-5 무관**: **site 계수**(술어 매치 건수)는 concrete 케이스에서 decidable 하다 — detection sufficiency 판정이 아니다.

**★A1-4 · A1-5 공통 — 적용 범위 + forward-only ratchet (`reinterpretation: false` 의 근거)**

- **적용 = §결정 7 전체**(instrument-side ∪ 게이트 self-test). **같은 결함류에 임의 경계를 긋지 않는다** — 바이트 층 assert 의 불충분성은 하네스든 landed self-test 든 동일하다.
- ★**forward-only ratchet — landed 산출물 소급 무효화 0**: L-1·L-2 는 **신규·개정** 하네스/self-test 에 적용한다. 이미 착지한 §결정 7 산출물(메타-게이트 self-test M1-M6 등)을 **소급 위반으로 재분류하지 않는다.** 그 retrofit 은 **review-tier + 별 carrier defer**(**ADR-171** evidence-gate 형판 — 구 ADR-060 의 재제정본. §결정 8 의 required 승격 defer 와 동형).
- ⇒ **`reinterpretation: false`**: 기존 §결정 1-10 문면의 **landed 대상에 대한 의미가 불변**이다. 본 Amendment 는 *적용 대상 추가 + 전방 leg 추가* 이지 기존 결정의 **소급 재해석이 아니다**. (이 marker 는 presence/type 만 기계 검사되고 **진위 = 리뷰 판정 축**이므로 — 템플릿 honest-ceiling — 판정 근거를 문면에 남긴다.)
- ★**인용 사슬 = 변경 표면 전건 (설계리뷰 P3-1 — 구판 사슬이 표면보다 좁았다)**: `false` 판정은 L-1·L-2 만으로 서지 않는다. **가장 넓은 변경 표면은 A1-2(적용 대상 확장)** 이며, 그것이 소급 재해석이 되지 않도록 **막는 것은 A1-7 과 A1-3 이다** — **A1-7** 의 opt-in selector 는 *미선언 = 미대상* 이므로 **기존 산출물을 자동으로 쓸어 담지 않고**(선언 없이 대상이 되는 artifact = 0), **A1-3** 은 스캔 표면을 만들지 않으므로 **기존 산출물이 새 판정을 받는 경로 자체가 없다**. 이 셋(A1-2 ⊕ A1-3 ⊕ A1-7) + forward-only(위) 가 **4중 봉인**이고, 그중 하나라도 풀리면 `reinterpretation` 재판정 대상이다.
- ★**미측정 정직 고지**: landed self-test 가 **실제로 L-1 결함을 보유하는지는 재지 않았다.** 그래서 소급 강제도 하지 않고, *"landed 는 안전하다"* 는 단정도 하지 않는다 — 둘 다 근거가 없다.

### A1-6 — ★신규 0 명시: 대표 형상 ③④ 는 **기존 조항 재사용** (과대주장 절제)

본 arc 대표 형상 4종 중 **2종은 A1-2 스코프 확장만으로 덮인다. 신규 leg 을 만들지 않는다.**

| 형상 | 처분 | 커버하는 **기존** 조항 |
|---|---|---|
| ③ 선택자에 수호 테스트가 안 들어감 → 초록이 *"안 죽었다"* 가 아니라 ***"안 돌았다"*** (CP §13.1-29 `L916`) | **신규 0** | **§결정 5 internal-control(identity probe)** — *"선언 대상 = 실행 대상"*. 하네스가 재려던 테스트가 실제로 실행됐는가 = 계기 축의 identity 문제 |
| ④ 계기 사망 — 한글 리터럴 cp949 파손(arc 3회 + PMO 2회) · `bash` 의 WSL 릴레이 해석 · MSYS 경로 맹글링 | **신규 0** | **검출 = §결정 5 internal-control**(판별 대조군으로 술어 생존 먼저 입증) ⊕ **처분 = §결정 6 fail-direction**(계기가 대상을 읽지 못하면 **fail-closed**, 침묵 통과 금지) |

★**형상 ③ 귀속 정정 (설계리뷰 P2-3 — 구판은 A1-3 과 모순이었다)**: 구판은 형상 ③ 커버를 **§결정 3 AC-5 execution-trace** 로 들었는데, A1-3 이 *"확장은 계약(§결정 5·7)에 한정"* 이라 선언한 것과 **충돌**했다(§결정 3 은 확장 대상이 아니다). 게다가 AC-5 는 두 겹의 미공개 조건부성을 갖는다 — **(i) §결정 3 mechanical floor 는 *"신규 hard gate"* 에만 걸린다**(`:109`) → legacy 게이트를 재는 하네스에는 보장 0, **(ii) AC-5 는 *emit* 의무이지 *fail* 의무가 아니다**(fail 의무 = AC-3, 구판 미인용) → `count=0` 이어도 초록이 가능하다. ⇒ **커버 조항을 §결정 5 internal-control 로 정정**한다(확장 대상 안, 무조건). **AC-5 는 게이트 축의 동형 kin 으로 cross-ref 만** 하며 **커버 근거로 쓰지 않는다** — 구판은 이 강도 차이를 공개하지 않았다.

★**과대주장 절제가 본 Amendment 의 신뢰성이다.** 이 둘을 "신규 leg" 로 계상하면 §결정 9(재codify 0)를 어기고, 본 Amendment 가 겨냥하는 *"같은 규칙 두 벌"* 을 스스로 생산한다. **본 Amendment 의 신규 normative 는 L-1 · L-2 둘뿐이며, 그 외 어떤 것도 추가하지 않았다.**

### A1-7 — applicability = **self-declared opt-in** (§결정 5 `identity_bearing` 형판 재사용 — 재codify 0)

"어떤 산출물이 instrument-side 계약의 대상인가" 를 **semantic 추론에 맡기지 않는다**(비결정·gameable — §결정 5 가 AC-13 에서 이미 기각한 방식):

- 뮤테이션 측정을 수행하는 산출물이 **`mutation_harness: true`** 를 선언하면 A1-2 계약(2-control) + A1-4/A1-5 2-leg presence 가 대상이 된다. **미선언(`false`/필드 부재) = 미대상(정직 no-op).**
- **형판 = §결정 5 `identity_bearing: true/false`** verbatim 구조. 신규 메커니즘 0.
- ★**selector 합성 확정 — instrument-side 에서 2-control 은 *양쪽 다 무조건* (설계리뷰 P2-2 — 구판 문면 0)**: §결정 5 는 게이트 축에서 **positive-control 은 무조건 / internal-control(probe) 은 별도 flag `identity_bearing` 이 가름** 으로 배선돼 있다. **instrument-side 는 그 조건부를 상속하지 않는다** — `mutation_harness: true` 선언만으로 **positive-control ⊕ internal-control 양쪽이 대상**이다. 근거: 게이트는 identity 를 다룰 수도 안 다룰 수도 있지만, **계기는 "선언한 대상을 실제로 쟀다" 는 주장 자체가 존재 이유**이므로 identity 는 선택 속성이 아니라 **구성적(constitutive)** 이다. ⇒ **instrument-side 에 `identity_bearing` 게이팅을 적용하지 않는다.** (이 확정이 없으면 A1-6 의 형상 ③④ 커버가 미정의 위에 서게 된다 — 구판의 실제 결함.) **게이트 축의 `identity_bearing` 조건부는 무변경**(§결정 5 무손상).
- ★**선언 표면(record home) — 인벤토리 아님 (설계리뷰 P3-3)**: §결정 5 형판 원본은 record home 을 *"게이트/self-test 인벤토리 레코드"* 로 명시하지만, **하네스는 A1-3 에 의해 ADR-151 인벤토리 enroll 대상이 아니다** — 따라서 **같은 home 을 쓸 수 없다**. instrument-side 의 선언 표면 = **하네스 자신의 기계 판독 가능한 표면**(공유 유틸 진입점 호출 인자 또는 하네스 모듈 상수). **구체 표면 확정 = `#2922` ⓑ Phase 2 소관**이며, 본 Amendment 는 제약 2개만 건다: **(a) 기계 판독 가능** **(b) ADR-151 인벤토리를 record home 으로 쓰지 않는다**(A1-3 정합).
- ★**이 절은 normative 계수에 들어가지 않는다 — 축이 다르다.** §결정 5 자신의 어휘가 이미 가른다: ***"applicability = self-declared(opt-in), probe presence = normative"***. `mutation_harness` 는 **applicability selector** 이지 하네스가 만족해야 할 요건이 아니다. 따라서 A1-6 의 *"신규 normative = L-1 · L-2 둘뿐"* 은 본 절에도 불구하고 유지된다. (같은 이유로 §결정 5 가 AC-13 을 *"probe presence 강제이지 detection sufficiency 강제가 아니므로 INV-5 무손상"* 이라 판정한 논리가 그대로 상속된다.)
- **실효 강제점 = `plugin-codeforge#2922` ⓑ 공유 라이브러리** — 라이브러리 import 가 곧 선언이 되게 배선한다(구현면, Phase 2).

**잔여 상속(신규 저작 0)**: *"모든 진짜 하네스가 실제로 self-declare 했는가"*(열거 완결성)는 **기계 강제 불가 — self-declared 의존이라 declared 완결성**이다. 이 잔여는 §결과의 **AC-13 열거-완결성 residual 문단과 동일 형식**이므로 그 처분을 그대로 상속한다(AC-8 honest-ceiling 공개 + AC-9 review-tier 판정). 새 잔여 문법을 만들지 않는다.

### A1-8 — 정직 천장 (본 Amendment 자신의 잔여 — 미기재 시 §13.1-28 형 재생산)

- ★**하네스 규율은 기계 강제가 아니다.** 하네스는 임시 산출물이라 §결정 8 5-piece chain 산출물이 아니고 **메타-게이트 정적 스캔 대상이 아니다**(A1-3). 따라서 A1-4/A1-5 는 **review-tier + 공유 라이브러리 채택**으로만 실효를 갖는다.
- ★**`#2922` ⓑ 라이브러리의 채택률은 강제되지 않는다.** 하네스는 매번 새로 쓰일 수 있고, 라이브러리를 쓰지 않은 하네스를 fail-closed 로 막는 표면이 **없다**.
- **A1-4 미선언 축 잔여**: 저자가 선언하지 않은 의미 축의 no-op 은 잡히지 않는다(위 rationale — 강화 금지).
- **A1-7 열거 완결성 잔여**: 상속(위).
- ★**본 수리가 새로 낳은 미확정 2건(설계리뷰 회귀 — 등재하지 않으면 §13.1-28 형)**: **(a)** L-2 계수 단위를 `site` 로 고정했으나 **`#2922` ⓑ 공유 유틸의 API 가 그 단위로 구현될지는 미착지** — 계약면만 확정, 구현면 미검증. **(b)** `mutation_harness` 의 **선언 표면(record home) 구체형이 Phase 2 미정** — 본 Amendment 는 제약 2개(기계 판독 가능 · 인벤토리 비사용)만 걸었고 표면 자체는 정하지 않았다. 둘 다 **계약면 확정 / 구현면 미착지** 상태로 정직 공개한다.
- ★**어휘 금지 재확인**: 본 Amendment 에 대해 *"universal / 완전 봉인 / 하네스 위양성 근절"* 류 framing 금지 — §결정 4 + INV-5 **무손상**이며, 위반 시 설계리뷰 P0.

### A1-9 — 접촉 경계 + carrier 결속

- **ADR-154 단독 amend.** **ADR-152 무접촉** — §관련 파일이 `cross-ref(재사용, **amend 금지**)` 로 못 박았고, `KILLED ⟺ …` 는 ADR-152 §결정8 원문(단방향)이 아니라 **본 ADR §결정 7 자신의 합성**이다. **ADR-151 인벤토리 8-field 스키마 무접촉 · ADR-168 무접촉**(구 ADR-082 의 재제정본 — 현재시제 접촉 경계는 live SSOT 에 건다).
- ★**퇴역 포인터 정정 기록 (설계리뷰 P1-1)**: 초판이 신규 저작 줄에서 **ADR-060**(→ Superseded by **ADR-171**) · **ADR-082**(→ Superseded by **ADR-168**) 를 인용했다 — 퇴역 SSOT 에서 형판을 상속하고 현재시제 경계를 퇴역 번호에 건 것. **정본 본문의 기존 인용(§관련 ADR 등)은 저작 당시 live 였으므로 스코프 밖·무접촉**이며, **본 Amendment 가 새로 쓴 줄만** 후행 번호로 정정했다. 상속한 형판·경계의 **실질은 무변경** — 두 후행 ADR 모두 의미 무변경 재제정이다.
- **강화 방향 유지(약화 surface 0)**: 신규 required context **0** · branch-protection 7-tuple **무변경** · inter-plugin 계약 **무변경** · 신규 category **0** · 신규 workflow **0**.
- **carrier 결속(계약면 ⊥ 구현면)**: **계약면 = 본 Amendment**(Phase 1) ⊥ **구현면 = `plugin-codeforge#2922` ⓑ** — *"뮤테이션 하네스 공통 유틸(주입 assert + canary)을 라이브러리화하고 리뷰/구현 레인이 공유. 우선순위 1"*(Phase 2). 계약면 없이 라이브러리만 만들면 채택이 자율이라 *"선언만 하고 강제 안 함"* 이 재생산되고, 라이브러리 없이 계약만 쓰면 *"규율이 문서로만 산다"* 가 된다 — **양방향으로 필요하다.**
- ★**본 Amendment 는 `#2922` Phase 2 의 blocking 전제조건이 아니다** — §결정 8 의 Phase 1 narrative / Phase 2 실코드 분리 **무손상**.

---

## Amendment 2 (CFP-2963, 2026-08-14 · **2026-08-15 축소 개정**) — 적용 대상 확장: landed 셸 게이트 **ONLY**. **신규 normative 0** — M-1·M-2 본체는 **[ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md) 로 이관**(설계리뷰가 Amendment 착지 판정을 뒤집음). INV-5 무손상

> ★**본 Amendment 의 현재 범위 = 2 절뿐**: **배경**(A1-3 조건부 유보의 해제 조건) + **A2-2**(적용 대상 = landed-gate). 초판의 A2-1 은 **판정 전환 기록**으로 재작성됐고, **A2-3~A2-9 는 ADR-175 로 이관**됐다(A2-3 자리 = 포인터). 이관 경위·근거는 A2-1 참조.

### 배경 — A1-3 의 유보는 **무조건이 아니라 조건부**였다 (그 조건이 본 건에서 성립하지 않는다)

A1-3 은 instrument-side 하네스에 landed 계약(§결정 8 5-piece chain · ADR-151 인벤토리 enroll · 메타-게이트 정적 스캔)을 **걸지 않는다**고 선언했고, 그 사유를 세 줄로 명시했다 — 그중 스캔 축의 사유는 **`⊥ 메타-게이트 정적 스캔 대상 — 스캔할 안정 좌표가 없다`** 였다. 즉 유보의 근거는 *"이런 계약이 과하다"* 가 아니라 ***"대상에 안정 좌표가 없다"*** 는 **사실 명제**다.

**본 Amendment 의 대상은 그 사실 명제가 성립하지 않는 모집단**이다 — **lane 산출물로 저작돼 repo 에 landed 된 게이트 스크립트**는 경로·커밋·해시라는 **안정 좌표를 보유**한다. 따라서 본 Amendment 는 **새 원리를 도입하는 것이 아니라 A1-3 의 조건부 유보가 해제되는 정확한 조건을 문면에 명시**한다. ★그리고 이 문장은 **ADR-154 문면 안에서만 의미를 갖는다** — A1-3 의 조건절을 남의 문서가 해제하면 SSOT 가 갈린다.

**발생 근거(CFP-2963 arc 실측)**: 같은 batch 의 산출물 검토에서 *"검사처럼 보이나 아무것도 막지 않는 것"* 이 **20 인스턴스**로 발현했고(계수 기준 = **인스턴스** — 전건 열거·재계수 SSOT = [ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md) §결정 9. 초판이 적었던 *"11 인스턴스"* 는 기준 혼재 상태의 미도출 수치였다), 그중 대표 형상이 **fail-open 셸 술어**(게이트 판정이 `if` 조건절 안에 있어 `set -e` 면제 → rc≠0 을 삼키는 fallback → 정수 비교 실패 rc=2 → else 로 흐름 = **어떤 입력으로도 FAIL 하지 않는 게이트**)다. **기존 3층 어느 것도 이 모집단을 정의역에 담지 않는다** — 층 B 의 subject 발견 계약이 `<DIR>/tests/scripts/*.sh` **∧** inline enrollment marker(`hard-gate-self-verification: enrolled` | `hgsv-enroll`)로 **구조적으로 한정**돼 있기 때문이다(`scripts/lib/check_hard_gate_self_verification.py:57`·`:106`) `[ArchitectAgent firsthand 2026-08-14]`.

★**침묵이 아니라 명시적 유보였다** — 그래서 처방이 *"감사 강화"* 가 아니라 **조건 명시**다(A1-1 의 *"문면 갭의 처방은 문면 갱신"* 과 같은 형).

### A2-1 — 형태 판정: **초판 판정(Amendment 채택)은 설계리뷰가 뒤집었다 — 신규 ADR([ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md)) 채택**

★**판정 이력을 무언 폐기하지 않는다.** 초판 A2-1 은 §결정 1 3-prong 자기적용 **1/3** 로 Amendment 를 채택했고, 그 자리에서 **반대 판정 가능성을 스스로 등재**하며 *"설계리뷰가 이 판정을 뒤집을 수 있다"*, *"뒤집힐 경우 normative 내용은 그대로 신규 ADR 로 이관 가능하도록 저작했다(내용 ⊥ 그릇)"* 라고 적었다. **CFP-2963 설계리뷰(Story §9.12 DR-M5)가 그 조건을 발동시켰다.** 아래는 초판 판정과 재판정을 **나란히** 남긴 것이다 — 초판 근거를 지우지 않고 결론만 전환한다.

| prong | **초판 A2-1 판정** | **재판정(설계리뷰)** | 전환 사유 |
|---|---|---|---|
| (i) distinct context | 부분 성립 → **기각** | **부분 성립** | 기각은 *"A1-1 이 다른 모집단을 Amendment 로 흡수한 선례"* 에 의존했는데, **A1-1 은 0/3 이고 (iii) 를 결정적으로 기각**하며 그 사유가 *"결과가 남의 carrier"* 였다. 초판 자신이 *"그 사유는 본 건에 **없다**"* 라고 자인했다 ⇒ **결정적 prong 이 반전된 사안에 선례를 확장**한 것. 또 A1-1 은 declaration-only · **신규 workflow 0**, 본 건은 **workflow 1** |
| (ii) distinct decisions | **기각** (*"신규 결정 1 점뿐"*) | **부분 성립 — 자기 계수와 모순이었다** | 같은 Amendment 의 **초판 A2-6**(→ 현 [ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md) §결정 6)이 ***"신규 normative 는 M-1 · M-2 둘뿐"*** 을 선언했다. (ii) 기각은 자기 문서가 **2** 라 한 수를 **1** 로 세워야 성립하므로 불가. 게다가 M-2(분모 단조 하한)는 modality 가 아니라 **census 불변식** |
| (iii) distinct result | ★**성립(자인)** | **성립** | 초판이 이미 자인. 재판정에서 **신규 workflow 1**(A2-9 자인) + **신규 sidecar manifest 스키마 1**(A2-8 (b) 가 *"필드 정의 + versioning 미확정"* 으로 실재를 자인) 이 추가 확정 |

**⇒ 리트머스 = 1/3 → 2~3/3.** 나아가 §결정 1 이 인용한 **ADR-151 §결정 1 신규 ADR prong 3-conjunct**(*(i) 신규 fail-closed 메타-게이트 (ii) 신규 인벤토리 스키마 (iii) 메타-게이트 자신의 재귀 L3 자기적용*)가 본 건에 **3/3** 성립한다.

**초판이 든 채택 근거 3 중 2 가 반증됐다**:

1. ~~**§결정 9 + §결정 2 가 신규 ADR 을 구조적으로 막는다**~~ → **거짓 딜레마(반증됨)**. 신규 ADR 이 super-class·taxonomy·2-control 을 *다시 정의해야 한다* 는 명제가 성립하지 않는다 — **§결정 1 자신이** *"본 ADR 은 cross-ref/재사용만 하고 supersede/rewrite 하지 않는다"* 로 착지했고 ADR-151 §결정 1 도 동문을 보유하며, Epic CFP-2602 G-family(ADR-145/146/148/150/151/152/153)가 전부 그 형태다. 결정적으로 **초판이 스스로 등재한 반대 처분**(*"신규 ADR + ADR-154 전면 cross-ref(재codify 0 유지)"*)이 이 근거를 자기 무력화한다.
2. ★**A1-3 조건절의 SSOT 귀속** → **견고 · 유지**. *"A1-3 의 유보 조건이 언제 풀리는가"* 의 소유자는 ADR-154 이며, 남의 ADR 이 그 조건을 해제하면 **A1-3 의 의미가 두 문서에 갈린다**. **이것이 본 Amendment 를 축소 존치하는 유일 근거다.**
3. ~~**(iii) test 의 방향성**~~ → **본 건에 부적용(반증됨)**. 위 표 (i) 열 참조 — A1-1 선례의 결정적 prong 이 반전된 사안이라 선례 확장 불가. (다만 *"(iii) 를 필요조건으로도 충분조건으로도 쓴"* §결정 1 문면 내부의 비대칭 자체는 **실재하는 미해소 긴장**이며, 본 Amendment 가 그것을 새로 만든 것이 아니라는 초판 진술은 **유효**하다.)

**⇒ 처분 = 분할(설계리뷰 권고 채택)**:

- **본 Amendment = 축소 존치** — **배경**(A1-3 조건 해제) + **A2-2**(적용 대상 = landed-gate) + 본 절(판정 전환 기록) + A2-3(포인터). SSOT 귀속 보존.
- **ADR-175 = 이관 착지점** — M-1·M-2 normative 본체 + 경계·opt-in·sidecar manifest·정직 천장·carrier 결속. 초판이 *"내용 ⊥ 그릇"* 으로 저작한 덕에 **이관 비용 ≈ 0** 이었다.
- 이 분할은 설계리뷰 **DR-M8**(동일 normative 표 2벌 저작 + divergence 1건 실발생)도 **동시 해소**한다 — 결정면 정본이 ADR-175 단독이 되어 중복 표가 0 이 된다.

**경쟁 home 배제(무언 폐기 금지 — 재판정 후에도 유효)**: **ADR-151** = self-test 코퍼스 execution-liveness(채널 alive) — subject disjoint이며 인벤토리 **8-field 스키마는 확장하지 않는다**(확장분은 ADR-175 §결정 8 sidecar 분리). **ADR-171** = 승격 evidence-gate 축 — 등급/승격 축 ⊥ 검출보장 축. **ADR-130** = 7일 green / path-filter 금지 — 배선 제약이지 계약 소유자 아님.

### A2-2 — 적용 대상 확장 (스코프 — 안정 좌표 보유 모집단)

§결정 3(mechanical floor 의 **검사 modality**) · §결정 5(2-control) · §결정 6(fail-direction) · §결정 7(born-hollow 금지)의 적용 대상에 다음을 **추가**한다:

> **lane 산출물로 저작돼 repo 에 landed 된 게이트 스크립트**(셸 포함) — 경로·커밋·해시라는 **안정 좌표를 보유**하는 모집단. 이하 **landed-gate**.

**A1-3 과의 관계 = 모순 아님 · 조건 해제다.** A1-3 은 *임시* 산출물(하네스)에 대한 유보였고, 그 사유가 안정 좌표 부재였다. landed-gate 는 그 사유가 성립하지 않으므로 **A1-3 은 무변경으로 유지되고 본 Amendment 는 그 밖의 모집단을 다룬다** — A1-3 을 재해석하지 않는다.

**§경계 갱신(침묵 제거)** — 기존 §경계 + A1-2 갱신분에 다음을 더한다: **landed-gate(셸 포함) = ⊥ 아님(본 ADR 대상)**. **L3 detection-power 는 여전히 ⊥**(§결정 4 무손상).

★**광역 정적 스캔은 여전히 기각 상태다(§결정 3 무변경).** §결정 3 이 기각한 **archetype-B 광역 silent-fallback scan**(honest-degrade FP 26 script / 127 occurrence)을 되살리지 **않는다**. 어휘 열거로 관용구를 잡는 설계는 본 Amendment 하에서도 채택 불가다.

★**이 정의를 소비하는 normative 계약은 [ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md) 가 보유한다.** 본 절은 **모집단 정의와 그 정의가 성립하는 조건(A1-3 해제)** 까지만 소유하며, 그 모집단에 무엇을 강제하는가(M-1 동적 kill 분류 · M-2 분모 단조 하한)는 ADR-175 §결정 4·5 소관이다. ADR-175 는 본 절을 **재정의하지 않고 참조만** 한다(§결정 9 재codify 0 동형) — 따라서 landed-gate 정의의 SSOT 는 **본 절 단독**이다.

### A2-3 — 이관 포인터: A2-3~A2-9 는 [ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md) 로 이관됐다

**본 Amendment 는 여기서 끝난다.** 초판이 보유했던 아래 7 절은 A2-1 의 판정 전환에 따라 **ADR-175 로 이관**됐다. 여기에 요약본을 남기지 않는다 — 요약을 남기면 그 자체가 §결정 9(재codify 0)가 금지하는 *"같은 규칙 두 벌"* 이고, 설계리뷰 **DR-M8** 이 지적한 divergence 채널을 다시 여는 것이다.

> ★★**3열 축소(설계리뷰 DR2-M8 처분 — 무언 정정 금지)**: 구 표의 3열은 *"이관 시 변경"* 이라는 이름으로 **ADR-175 내용을 요약**하고 있었고, 그것이 바로 이 절 머리말이 금지한 *"같은 규칙 두 벌"* 이었다. **실제로 drift 2건이 발생**했다 — ⓐ **row A2-7** 이 적격 전제를 *"입력 의존 **종단 emit**"* 으로 적었는데 이는 ADR-175 §결정 4 ②-b 가 **폐기한 기준**이고(정본 = `observed_line_set` = **관측 라인 집합**), 나아가 **3-conjunct 를 2-conjunct 로** 기술해 **(c) drivability 를 누락**했다 ⓑ **row A2-8** 이 *"잔여 3 … 미확정 3 → 1"* 이라 적었으나 ADR-175 실문면은 **잔여 HC-1·HC-2 2 · 미결 U-2~U-5 4 · 경로는 확정**이다. ⇒ **3열을 「절 제목 + 이관 사실」만으로 축소**하고 내용 요약을 삭제한다. **이관분의 내용을 알려면 이관처 §결정을 읽는다** — 그것이 본 절 머리말의 원래 취지다.

| 초판 절 | 이관처 |
|---|---|
| A2-3 경계(cross-repo / 3번째 메타 층 / 인벤토리 스키마 확장 배제) | **[ADR-175](ADR-175-landed-gate-corpus-dynamic-hollow-classification.md) §결정 3** |
| A2-4 신규 normative M-1(2-arm corpus 동적 kill 분류) | **ADR-175 §결정 4** |
| A2-5 신규 normative M-2(분모 단조 하한) | **ADR-175 §결정 5** |
| A2-6 신규 0 명시 | **ADR-175 §결정 6** |
| A2-7 opt-in selector | **ADR-175 §결정 7** |
| A2-8 정직 천장 | **ADR-175 §결정 9** |
| A2-9 접촉 경계 + carrier 결속 | **ADR-175 §결정 10** |

★**본 표는 이관 *사실* 만 기록한다** — 이관 시 무엇이 어떻게 바뀌었는가(정정·신설·재계수)는 **각 이관처 §결정이 자기 안에 정직 기재**하고 있으며, 본 절이 그것을 복사하면 divergence 채널이 다시 열린다(위 drift 2건이 그 실증이다).

★**천장 동시-변경 불변식의 양단이 이동했다** — 이제 **ADR-175 §결정 9 ↔ Change Plan §8.QC-MECH MECH-9** 이며, 본 Amendment 는 그 불변식의 당사자가 아니다.

★**본 Amendment 축소 후 재확인**: 신규 normative **0** · 신규 workflow **0** · 신규 required context **0** · branch-protection **8-tuple 무변경** · ADR-152/151/168 **무접촉** · **INV-5 무손상**. 초판이 declare 했던 *"신규 workflow 1"* 은 은폐된 것이 아니라 **ADR-175 §결정 10 으로 귀속 이동**했다.
