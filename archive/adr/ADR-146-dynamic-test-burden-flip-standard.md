---
adr_number: 146
title: 동적 테스트 최대화 표준(burden-flip) + fuzz/property/load/concurrency §8.8 1급 편입 — do-it-unless-proven-infeasible + presence/구조 fail-closed(검출력 천장 정직 공개)
status: Accepted
category: governance
date: 2026-07-11
carrier_story: CFP-2605
supersedes: []
related_adrs:
  - ADR-006  # §8 Test Contract authoring mechanism owner — TestContractArch input contributor / ArchitectAgent(chief) 통합. Amd2 A2-5 "신규 ADR vs Amendment" 판정 구조를 §결정 11 에 verbatim 적용. Amd2 tier B property "후보 식별"(edge-DERIVATION 축) = G4 §8.8 property(EXECUTION 로스터 축)와 axis-disjoint — G4 는 ADR-006 Amd2 wording 무수정(상류·직교 확장, 충돌 아님)
  - ADR-136  # 결정9 L168 "정적 applicability(repo 단위) ⊥ 동적 this-PR-needs-execution 2-layer" = burden-flip default-true(Layer2) ↔ ADR-136 default-false(Layer1) 정합의 codified 선례(§결정 1). 결정14 execution-liveness 3요건(L1 blocking/L2 full-scope/L3 self-test) = §8.8 게이트 준수 상위 원리(§결정 5)
  - ADR-015  # §8.5 soak/restart/replay stateful category(+Amd1) — G4 concurrency(interleaving 축)는 §8.5 temporal 축과 disjoint, soak/restart/replay 신설 금지·G2 참조만(§결정 3)
  - ADR-119  # research-before-claims / 게이트=ground-truth — 게이트는 presence/구조까지만 fail-closed. "동적 테스트가 요건을 의미상 검증한다/결함을 실제로 잡는다"를 강제하는 척 = 검사연극(§결정 8 천장)
  - ADR-127  # no-exemption 정식 풀 플로우 — §결정 5 자연 N/A 3축 AND(산출물부재 ∧ downstream 무변경 ∧ 미래의무 무선결). burden-flip = 이 원칙의 강화(계승, 충돌 아님, §결정 7). Phase 2 runner-wiring 별 CFP defer = 축3 위반이므로 동일 Story 유지
  - ADR-048  # CI-native 테스트 실행 — 4기법 실 실행 러너 = consumer test.yml(QADeveloperAgent). StatefulTest deprecated 유지 → 신규 codeforge 러너 부활 금지(§결정 6)
  - ADR-139  # adequacy ⊥ liveness 두 직교 축 — G4 = adequacy(동적 검증 충분성) 거주. "test liveness" 표현 금지(orchestration/runtime liveness 어휘 충돌 차단, §결정 4)
  - ADR-060  # adequacy SSOT + 승격 evidence-gate — adequacy 어휘 고정 근거(§결정 4)
  - ADR-008  # Inter-plugin Contract Versioning — 권고 = ZERO contract change(4기법 필드 계약 밖 = RTM 이중소유 회피). fallback = design-output-v2 optional bool 1건 additive MINOR(미채택, §결정 10)
  - ADR-145  # G1 요건 traceability zero-drop — G4 AC 는 ADR-145 3-tier(normative/declared/advisory) + AC-ID sub-letter 문법(ac_id.py SSOT 공유)에 정합만. ADR-145 amend/재사용 금지(§결정 9)
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(146) claim→write→row-append 3-step 발급(claimant ArchitectPLAgent:CFP-2605)
  - ADR-005  # N/A 명시 패턴 — 자연 N/A substantive reason(≥30자) + §11 데이터 마이그레이션 N/A(wrapper-self governance, schema/data 무변경) 근거(§결정 7)
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary(chief tie-break ladder) + I-4 wording SSOT
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs). ADR-127 정합
  - ADR-138  # blanket_designrefactor debate — verdict judge = ArchitectAgent chief(§결정 12 §8.8 좌표 = debate 2-축 분해 verdict)
related_concepts:
  - dynamic-test-burden-flip
  - adequacy-presence-ceiling-honesty
is_transitional: false
---

# ADR-146 — 동적 테스트 최대화 표준(burden-flip) + fuzz/property/load/concurrency §8.8 1급 편입

## 상태

Accepted (2026-07-11 KST) — CFP-2605 (Epic CFP-2602 G4) carrier. "구현이 바뀌었는데도 그 변경을 *실제로 실행해* 검증하는 동적 테스트가 조용히 빠지는" 병(green-but-buggy, adequacy 갭)을 도메인 불변식 위반으로 재정의하고, §8 Test Contract 의 default 를 opt-in → do-it-unless-proven-infeasible(burden-flip)로 뒤집으며 fuzz/property/load/concurrency 4 동적 기법을 §8.8 1급 로스터로 편입하는 governance SSOT. 강화(ratchet↑) 방향 — 기존 §8.5/§8.7 게이트 무변경 위에 §8 preamble 표준 + §8.8 로스터 + `check_section_8_8` lint 함수 1개 추가. **약화 surface 0**(신규 required context 0, branch-protection 6-tuple 무변경, 계약 무변경).

## 컨텍스트

사용자 원문(Story §1 verbatim): "codeforge 테스트 레인이 테스트 가능한 최대한의 동적 테스트를 수행하도록 강화한다"(2026-07-11 세션, 최광범위 승인). Epic CFP-2602(요건충족·산출물생존 강제) 확장 child, 게이트 G4 슬라이스.

실측된 갭(CodebaseMapper, origin/main 2de1512c):

- **§8 applicability 가 opt-in**: §8.5.0/§8.7.0 = "적용 조건 있을 때만 본문" — feasible 한 동적 검증이 침묵 누락돼도 전 게이트 green(adequacy 갭). [verified: `plugins/codeforge-design/templates/change-plan.md` §8.5.0/§8.7.0]
- **4기법 편입 불균등**: property-based+metamorphic 은 ADR-006 Amd2 tier-B "후보 식별"로만 명명(1급 execution 로스터 부재) [verified: ADR-006 A2-2 L242 / TestContractArchitectAgent.md L160-161]. **fuzz 는 진성 부재**(오직 "API fuzz" cross-ref). load="sustained load"(§8.5.1)·concurrency="동시성"(§8.2) = incidental 키워드. [verified: Mapper grep]
- **실행 러너 gap = StatefulTest 재발 위험(실증)**: §8.5 계약은 있으나 유일 러너 StatefulTestAgent 가 deprecated [verified: ADR-048:110] — "계약만 있고 미실행"(hollow-contract). G4 4기법이 같은 함정에 빠지지 않으려면 실 실행을 consumer test.yml(QADev)로 배선 + 게이트 self-test 의무.

도메인 불변식 **INV-D1(adequacy default)**: "구현 변경에 feasible 한 동적 검증은 default 로 수행돼야 하며, 미수행은 침묵이 아니라 정당화(fail-closed 사유)를 요구한다." 현 opt-in 이 이를 깬다.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음): "테스트 default + 배제 정당화"는 확립된 관행이다 — OSS-Fuzz continuous fuzzing(등록 프로젝트 상시 적용, `source: github.com/google/oss-fuzz`) / Google Beyoncé rule(`source: abseil.io/resources/swe-book`) / mutation ratchet(Stryker). 동시에 **강제해도 결함검출은 보장 못 한다** — fuzz coverage plateau / 약한 property false confidence / load 환경 의존 / race 재현 불가("발생한 실행만"). load≠stress≠soak≠spike≠breakpoint 6-way taxonomy(`source: grafana.com/load-testing/types-of-load-testing`, soak=average-load 변형) / linearizability 검증 = NP-complete(`source: Gibbons & Korach, SIAM J. Comput. 26(4), 1997`). ∴ 자동화로 rot·형식누락은 저감하나 검출력(discriminating) 봉인은 불가(§결정 8 근거).

## 결정

§8 Test Contract 의 동적 테스트 default 를 do-it-unless-proven-infeasible(burden-flip)로 뒤집고, fuzz/property/load/concurrency 4기법을 §8.8 1급 로스터(applicability 판정 + 산출물 계약 + 실행)로 편입하되, 기계가 강제 가능한 것(applicability 표·산출물 계약 필드의 presence/구조)의 천장을 정직히 공개한다. 착지 = §8 preamble 표준 + §8.8 로스터 sub-section + `check_doc_section_schema.py` 확장(신규 required job 0).

### 결정 1 — burden-flip 표준(§8 전반) + 2-layer 정합(default-true ↔ ADR-136 default-false)

- **§8 preamble 표준(altitude)**: "feasible 한 동적 검증은 default 로 수행(DO)한다; 미수행은 침묵이 아니라 정당화(infeasibility_reason)를 요구한다"(do-it-unless-proven-infeasible). 적용 범위 = **§8 전 동적 테스트 로스터 전반**(사용자 최광범위 승인 R1 — 신규 4기법 한정 아님). §8.8 은 이 표준의 4기법 구체 instantiation.
- **presence-ceiling + no-hollow**: 기계 fail-closed 는 §8.8 4기법 좌표의 applicability 레코드 presence/구조까지만(AC-1a normative). §8-wide 표준의 *완결성*(전 동적 항목이 do-unless-infeasible 를 지키는가)은 대조 인벤토리 부재로 review-tier(AC-1b declared). preamble 표준(altitude) ⊇ §8.8 로스터(기계 slice) — 표준은 넓고 게이트는 좁다.
- **2-layer 정합(CONFLICT default-true↔false 해소, ADR-136:168 결정9 codified 선례 인용)**:
  - **Layer1 (존재/도메인 opt-in) = default-FALSE**: 그 기법의 툴체인·대상 표면이 도메인에 존재하는가(예: Go `-race`/`cargo-fuzz` 부재 = 툴체인 없음). 부재 → 정당화된 자연 N/A. ADR-136 `frontend.applicable` default-false 동형(안전 방향).
  - **Layer2 (per-change 적용) = do-unless-infeasible = burden-flip**: Layer1 이 존재하면 그 변경에 default 로 적용(DO), 미적용은 infeasibility_reason 요구.
  - **∴ 모순 아님**: burden-flip 은 Layer2(적용 default 반전), ADR-136 default-false 는 Layer1(존재 안전 default) — disjoint. burden-flip 이 "툴체인 없는 consumer 에 fuzz 강제"하지 않는다(Layer1 이 자연 N/A). ADR-136:168 "정적 applicability ⊥ 동적 this-PR-needs-execution"의 동형 적용.

### 결정 2 — fuzz/property/load/concurrency §8.8 1급 편입 (tier A/B 재도출 금지)

- 4기법 = §8.8 로스터 1급 항목(applicability DO|N/A + DO 시 산출물 계약 필드 + 실행). 산출물 계약 필드(Story §5.2): fuzz 6(target/input_surface/oracle/seed_or_corpus/execution_budget/pass_condition) · property 4(property_definition/input_generator/sample_budget/pass_condition) · load 4(load_profile/metrics/threshold_or_baseline_ref/duration) · concurrency 5(shared_state/execution_model/worker_count/oracle/duration).
- **재도출 금지(상류·직교)**: ADR-006 Amd2 tier A(EP/BVA/enum/collection) + tier B(Decision Table/State Transition/Pairwise/Property/Metamorphic)의 **엣지 도출(edge-DERIVATION) 축은 무변경**. G4 는 그 위에 별개 disjoint **EXECUTION 로스터 축**을 얹는다. property-based 는 tier-B "후보 식별"(design-time 불변식 후보)에서 §8.8 property "실행 로스터 항목"(execution)으로 **승격**(PROMOTED, absent 아님) — DERIVATION 축의 "후보 식별" wording 은 그대로 둔다(결정 11 axis-disjoint). fuzz 만 진성 신규.

### 결정 3 — 3축 disjoint 경계 + g2_boundary_check (Epic 경계 위반 fail-closed)

- **3 결함 축 disjoint**(Story §2.C): load(saturation/용량 포화 축) ⊥ soak(endurance/수명 축 = **G2 단일소유**, 참조만) ⊥ concurrency(interleaving/병렬 순서 축). §8.3 Perf Baseline(regression/단발 축)과도 구분.
- **load ≠ soak**: load 는 부하 올려 포화점(용량 축), soak 는 장시간 생존(수명 축) — Grafana 6-way taxonomy 정합. G4 load 는 saturation 만.
- **concurrency ≠ §8.5 stateful**: concurrency = 실행 순서(interleaving) 축, §8.5 = 시간(temporal)·재시작 축. G4 는 §8.5 soak/restart/replay 신설 안 함(ADR-015 disjoint).
- **`g2_boundary_check` 레코드 필드**: 각 §8.8 기법 레코드가 "soak/restart/replay 로 넘어가지 않았음(G2 참조)"을 확인. 게이트가 이 token presence 를 fail-closed 검사(AC-7) — Epic 경계 침범 차단. (단 presence ≠ 실준수 = 결정 8 천장.)

### 결정 4 — adequacy 어휘 가드 ("test liveness" 표현 금지)

- G4 축 명칭 = **"adequacy(동적 검증 충분성)"**로 고정(ADR-060 SSOT). ADR-139 의 3-sense 동음이의 가드: adequacy(green-but-dead) ⊥ liveness-orchestration(stall) ⊥ 지속-liveness-runtime(soak=G2). **G4 문서 "test liveness" 표현 금지**(orchestration/runtime liveness 와 충돌). soak/생존 어휘는 G2 참조 맥락에서만.

### 결정 5 — 게이트 = check_doc_section_schema.py EXTEND + execution-liveness 3요건 + L3 self-test + RTM location-resolution

- **`check_section_8_8` 신규 함수 추가**(`check_section_8_5`/`check_section_8_7` verbatim 동형), `main()` docs/change-plans loop wire, `NA_85_SUBSTANTIVE_RE` 재사용. **신규 workflow `.yml` 0 → branch-protection 6-tuple 무변경**(G1 의 6→7 과 대조 — G4 는 신규 required context 신설 안 함).
- **execution-liveness 3요건(ADR-136 결정14, conjunctive AND)**: (L1 blocking) 신규 함수가 **기존 strict context `doc section schema (CFP-28 — strict)` 에 편승**(동일 `sys.exit(1)`) → born-broken required 위험 0, day-1 blocking 안전. (L2 full-scope) 단일 canonical `.py` — 신규 `.yml` 부재 → dual-copy(`templates/github-workflows/`) 불요. docs/change-plans 전수 스캔이 full-scope. (L3 self-tested) 신규 `tests/scripts/test-check-doc-section-8-8.sh`(§8.7 self-test 선례 CWD-격리 답습) — mutation-kill discriminating + sibling-dependency guard.
- **mixed-case per-technique N/A substantive check(hollow-gap 마감)**: §8.5/§8.7 은 aggregate-N/A 사유만 기계검사한다. §8.8 게이트는 DO 3 + N/A 1(mixed) 시 그 N/A 항목의 per-technique substantive reason 도 검사 — AC-2 hollow-gap 을 §8.5/§8.7 대비 새로 마감.
- **RTM location-resolution(G1 P1 재사용, amend 금지)**: 게이트는 authoritative 위치에서 §8 Test Contract 를 resolve — wrapper-self dogfood = Change Plan §8 / consumer Story = Story §8. G4 게이트는 이 규칙을 신설하지 않고 ADR-145 §결정 6 을 인용(중복 SSOT 회피).

### 결정 6 — 실행 러너 = consumer test.yml(QADev) + wrapper-self declarative

- **4기법 실 실행 = consumer `test.yml`(QADeveloperAgent, ADR-048 CI-native 정합)**. 신규 codeforge 러너 부활 = ADR-048 재충돌 금지(StatefulTest deprecated 유지). execution routing 을 **명시**하지 않으면 §8.5 StatefulTest hollow-contract 재발(TestContractArch dissent-3 채택).
- **wrapper-self declarative**: wrapper-self 거버넌스 Story(실행코드 0줄류)는 4기법 대개 자연 N/A — §8.8 레코드 schema 존재 + 정당화만 의무, 실 동적 구동 면제(실측 정량 파라미터 `[empirical-source: consumer test.yml, Phase 2]` defer — 추정값 lock-in 아님).

### 결정 7 — 자연 N/A 3축 AND (skip 아님) + ADR-005 표기

- 정당화된 infeasibility(예: 실행코드 0줄 문서 변경 / 툴체인 부재 consumer)는 ADR-127 이 금지하는 "skip/opt-out/default-green"이 **아니다** — 근거(infeasibility_reason ≥30자, ADR-005 substantive 패턴)를 남기는 것 자체가 규율(INV-D4).
- **3축 AND**(ADR-127 §결정 5): 산출물 target 부재 ∧ downstream 무변경 ∧ 미래의무 무선결. 세 축 동시 충족만 자연 N/A. **Phase 2 runner-wiring 을 별 CFP 로 defer 하면 축3 위반**(declarative-seed 미래의무 선결) → template §8.8 + lint + self-test + agent-md mandate 는 **동일 Story Phase 2**(§8-§11 PR)가 carry.

### 결정 8 — 정직 천장 (AC-8, 4 잔여 공개, no-hollow)

- **게이트는 구조(applicability 표·산출물 계약 필드 presence)까지만 fail-closed**. "동적 테스트가 요건을 의미상 검증한다 / 결함을 실제로 잡는다"를 강제하는 척 = 검사연극(ADR-119 정합).
- **4 잔여 정직 공개**: (i) 검출력(discriminating — 테스트가 결함을 켠 채 잡는가) = **G3 미강제** (ii) 열거 완결성(feasible 최대 열거) = AC-1b review 미강제 (iii) infeasibility 사유 타당성 = AC-5 review 미강제 (iv) **`g2_boundary_check` presence ≠ boundary 실준수**(TestContractArch dissent-2 — token 존재가 경계 실준수를 보장하지 않음). **"완전 봉인" hard-claim 금지** — "구조 fail-closed + 형식누락 저감 + 잔여 정직 공개"로 재약속. rubber-stamping 방지 = review + advisory defense-in-depth.

### 결정 9 — AC = G1 3-tier + AC-ID sub-letter 재사용 (ADR-145 amend 금지)

- G4 AC 는 ADR-145 3-tier(`normative` fail-closed 기계 / `declared` review-verified / `advisory` 경보)와 AC-ID sub-letter 문법(`AC-1a`/`AC-1b`, `ac_id.py` SSOT 공유)에 **정합만**. normative = AC-1a·2·3·4a-d·6·7·8·9(doc-section lint) / declared = AC-1b·5(DesignReview, forged machine test 금지) / advisory = AC-10.
- **ADR-145(G1 carrier) amend/재사용 금지** — G4 carrier = 본 ADR-146 신규. G1 게이트(AC↔§8↔실파일 zero-drop)와 G4 게이트(4기법 applicability presence)는 disjoint.

### 결정 10 — 계약 additive MINOR surface 최소화 (권고 = ZERO change)

- **권고 = inter-plugin 계약 변경 0**: 4기법 산출물 필드(target/oracle/parameters 등)를 어떤 계약에도 넣지 않는다 — template §8.8 + `check_section_8_8` 이 RTM 을 carry(§8.5/§8.7 이 design-output 필드 추가 0 으로 착륙한 선례 동형). 계약에 4기법 필드 = RTM 이중 소유(design-output ∧ §8.8) → drift. `test-verdict-v2`(v2.2) 무변경. `design-output-v2`(v2.4) 무변경 권고 — **race 근거**: G1(CFP-2603)이 이미 design-output v2.4→v2.5 additive bump in-flight [verified: MANIFEST L31 = v2.4 Active], 동시 bump = MANIFEST 3-point parity race → G1 우선, ZERO change 가 race 회피.
- **fallback(미채택, 기록 보존)**: verdict-packet anchor 필요 시 `chief_author_artifact.dynamic_roster_self_check_passed: bool`(design-output-v2 additive MINOR, ADR-008 §결정 2, default false) 1건만 — 단 4기법 필드는 여전히 계약 밖. G1 v2.5 머지 후 별 follow-up 으로만.

### 결정 11 — ADR-006 관계 판정 (Amendment vs 신규 ADR — A2-5 verbatim 구조 + axis-disjoint carve-out)

**(A2-5 판정 구조 적용 — design.md:53 "신규 ADR 없이 기존 ADR 변경 금지" 설계리뷰 P0 방지를 위해 ADR-006 A2-5 를 verbatim 구조로 포함한다.)**

- **ADR-146 = primary carrier (신규 ADR 정당)**: G4 의 burden-flip 표준(default 반전) + §8.8 fail-closed 구조 게이트 = **새 mechanism**이다. ADR-006 Amd2 는 *기존* "§8 author input contributor — shift-left QA" mechanism 에 엣지-도출(edge-DERIVATION) mandate 항목을 추가(범위 확장)했으므로 Amendment 였다. G4 는 (i) applicability default 를 뒤집고 (ii) 신규 `check_section_8_8` fail-closed 게이트 + execution-liveness 3요건을 도입하므로 별도 컨텍스트/결정/결과 블록이 중복이 아니다 → **신규 ADR**.
- **agent-md 4기법 mandate = ADR-146 흡수 (ADR-006 Amendment 3 아님)**: TestContractArch/QADev 가 §8.8 을 author/이행하는 mandate(Phase 2)는 ADR-146 *자신의* 표준의 downstream binding 이지 ADR-006 derivation-walk 의 새 항목이 아니다 → ADR-006 §결정 1/2 authoring mechanism 을 **cross-ref**할 뿐 ADR-006 Amendment 3 은 발의하지 않는다.
- **property tier-B = axis-disjoint carve-out (ADR-006 Amd2 wording 무수정)**: ADR-006 Amd2 tier-B property "후보 식별"(design-time 불변식 후보, edge-DERIVATION 축)은 그대로 authoritative·**무수정** 유지된다. G4 §8.8 property(dynamic-EXECUTION 로스터 축)는 **disjoint 신규 축**으로 ADR-006 Amd2 를 cross-ref(참조)하되 supersede/rewrite 하지 않는다. A2-4 disjoint 선례(설계-time property 후보 식별 ⊥ APIContractArch Schemathesis 구현-time API fuzz, "cross-ref 만") 동형. ∴ ADR-006 modification 0 → "ADR-006 무단 확장" P0 발생 없음.

### 결정 12 — §8.8+ 좌표 + Ports&Adapters (blanket_designrefactor debate verdict, Phase 2 ModuleArch)

- **§8.8 신규 좌표**(§8.5=G2 nesting 기각/§8.6=의도적 gap renumber 금지/§8.7=UI 점유 → 다음 자유 번호 §8.8). blanket_designrefactor debate verdict(ArchitectAgent chief, ADR-138) = **2-축 분해**: SECTION 좌표 = NEW §8.8(ALT-2, extend-§8.5 는 G2 coupling debt) / GATE MODULE = EXTEND `check_doc_section_schema.py`(신규 함수, opponent "extend-existing" 이 gate module 에서 WINS). SECTION 의 extend 와 GATE 의 extend 는 다른 extends — collapse 금지. convergence 3-tuple(counterargument ✓ + ≥1 alternative ✓ + debate-purpose ✓) satisfiable. Codex adversarial leg = Orchestrator-inline dispatch(recursion guard — chief spawn 불가).
- **Ports&Adapters relevance (Phase 2 ModuleArch 재검토)**: `check_section_8_8` = pure-lint 층(network-0, offline-testable) — 신규 boundary/module 신설 아님. Phase 2 Ports&Adapters lint 구조 정합은 ModuleArch 재검토 note(Phase 1 N/A).

## 대안 (기각 근거)

- **opt-in applicability 유지**: adequacy 갭(feasible 동적 검증 침묵 누락) 방치 → 기각(§결정 1 burden-flip).
- **§8.5 하위 nesting(ALT-1)**: G2 축(soak/restart)과 coupling debt = Story §2.C disjoint 위반 → 기각, 신규 §8.8(§결정 12).
- **신규 required workflow job(6→7-tuple)**: presence/구조 doc-lint 는 기존 strict context 로 충분 — 신규 job = over-surface + branch-protection 변경 → 기각, `check_section_8_8` EXTEND(§결정 5).
- **신규 lint 모듈(ALT-3 new-module)**: §8 은 template sub-section 축, 별 모듈 = MORE surface + 신규 context → 기각, 기존 파일 함수 추가.
- **4기법 필드 계약 반영**: RTM 이중 소유(design-output ∧ §8.8) drift + G1 v2.5 race → 기각, ZERO contract change(§결정 10).
- **신규 codeforge 동적 러너 부활**: ADR-048 재충돌(StatefulTest deprecated) → 기각, consumer test.yml(§결정 6).
- **ADR-006 Amendment 3 로 착륙**: burden-flip+게이트 = 새 mechanism 이라 별 컨텍스트/결정/결과 블록 필요 → 기각, 신규 ADR-146 + agent-md mandate 흡수(§결정 11).

## 결과

- feasible 한 동적 검증이 침묵 누락되면 §8.8 게이트가 구조적으로 차단(applicability 표·산출물 계약 presence fail-closed). 미민팅(완결성 Hop) = AC-1b review + advisory 로 defense-in-depth.
- 형식누락·rot 저감 + 검출력·완결성·사유타당성·g2-준수 4 잔여 정직 공개 = ADR-119/ADR-006 Amd2 정합(검사연극 회피).
- Epic CFP-2602 게이트 disjoint: **G1**(AC↔명명 §8↔실파일 zero-drop) ⊥ **G2**(soak/restart/replay 런타임 지속-liveness) ⊥ **G3**(discriminating 검출력) ⊥ **G4**(4기법 applicability·산출물 계약 presence/구조 + burden-flip 표준). 공유 = 원리("선언→실행, adequacy 강화", Epic #2346 계보)뿐.
- 약화 surface 0: 신규 required context 0, branch-protection 6-tuple 무변경, 계약 무변경. sunset_justification = N/A(permanent governance ratchet, ADR-058 §결정 5 강화 방향).

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2605.md` (§7 설계 서사)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2605-g4-burden-flip-dynamic-roster.md`
- 수정(Phase 2): `plugins/codeforge-design/templates/change-plan.md`(§8 preamble + §8.8) · `templates/story-page-structure.md`(§8.8 미러) · `scripts/lib/check_doc_section_schema.py`(`check_section_8_8`) · `plugins/codeforge-design/agents/TestContractArchitectAgent.md` · `plugins/codeforge-develop/agents/QADeveloperAgent.md`
- 신규(Phase 2): `tests/scripts/test-check-doc-section-8-8.sh`(L3 discriminating self-test)
- Phase 1: `docs/architecture/codeforge-family.md`(data_flow 1-line + Open Decisions)
- 선례: `scripts/lib/check_doc_section_schema.py` `check_section_8_5`/`check_section_8_7`(동형 확장 대상) · `tests/scripts/test-check-doc-section-8-7.sh`(self-test 선례) · ADR-145(G1 sibling — Phase 1/2 분리 + 3-tier AC + RTM location-resolution)
