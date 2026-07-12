---
adr_number: 152
title: dark/born-missing forcing function(G3) — §8.10 dark-path activation manifest + G3(b) Epic-close 요구-슬라이스 매핑 강제. landing≠done 구조적 차단 + presence/구조 fail-closed(discriminating-B 검출력 천장 정직 공개, discriminating-A self-test 재귀)
status: Accepted
category: governance
date: 2026-07-12
carrier_story: CFP-2624
supersedes: []
related_adrs:
  - ADR-146  # 강 의존(landed) — 본 ADR = G4 burden-flip 표준(§8 preamble do-it-unless-proven-infeasible)의 dark-path 활성화 축 확장. §결정8 "검출력(discriminating — 테스트가 결함을 켠 채 잡는가) = G3 미강제" 가 G3(a) mandate 의 명시 근거. §8.8 wiring 패턴(check_section_8_8 verbatim 동형) 재사용. ★ ADR-146 amend/재사용 금지 — G3 carrier = 본 ADR-152 신규(신규 oracle 축 = 신규 ADR, §결정1)
  - ADR-150  # 강 의존(landed) — 형제 게이트 G5. §8.10 = §8.9(DAST, 점유) 다음 자유 번호(§결정2 "next free number" 논리 상속). `check_section_8_9`(single-axis) = §8.10 clone source(verbatim 동형). §결정3/4 "검출력=G3 소관 / 2 cross-field=declared-consistency 만, detection 아님" = §8.10 천장 설계 형판. amend 금지 — 축 disjoint(DAST oracle=attack ⊥ dark-path oracle=activation)
  - ADR-151  # 강 의존(landed) — 형제 게이트 G6. discriminating-A(self-test mutation-kill 검출력 인벤토리) 단일소유 + AC-4/결과 "discriminating_fixture present 가 실제 mutation 죽이는가(검출력)=G3 소관 미강제" 로 discriminating-B 를 G3 에 명시 양도. AC-4 §8.10 self-test = G6 execution-liveness 인벤토리 `channel_status: alive` 등재
  - ADR-145  # 형제 게이트 G1(정합만, amend/재사용 금지) — AC-level zero-drop(AC↔§8↔실파일) ⊥ G3(a) 활성화 축(flag ON 행사) / G3(b) Epic-level 요구 슬라이스(granularity 상이). 3-tier AC(normative/declared/advisory) + AC-ID sub-letter 문법(`^AC-(\d+)([a-z])?$`, `ac_id.py` SSOT) 정합
  - ADR-045  # PMO Epic-close sibling(§D-11) — G3(b) 모집단(Epic 요구 슬라이스) ⊥ §D-11 모집단(누적 retro follow-up Issue ≥3). 같은 trigger(Epic-close §9.7.2)·owner(PMO) 지만 모집단 disjoint
  - ADR-137  # PMO Epic-close sibling — G3(b) 모집단(요구 슬라이스) ⊥ ADR-137 모집단(실머지 코드 duplication anchor). triage-defer verdict 의 §deferred 착지 선례(`source` 값 도메인) = G3(b) `req-slice-defer` 동형 확장 근거
  - ADR-128  # 강 의존(Amd1, landed) — G3(b) deferral 착지처. `check-deferred-item-recovery.sh` no-silent-drop 회수 게이트(warning-tier) + `EPIC-RESULTS §deferred` 5-column row 재사용(신규 deferral 메커니즘 신설 금지 = 단일-carrier). scanner 는 disposition enum 만 검증(source 미검증) → `source: req-slice-defer` 추가 = scanner 무변경
  - ADR-006  # §8 Test Contract authoring mechanism owner(+Amd2 CFP-2586 §8 edge-case forcing) — §8.10 = TestContractArchitectAgent(계약 필드 QA perspective) input, ArchitectAgent(chief) author(§8.8/8.9 동형 §결정2). 정직-천장 관례(Amd2 L266: discriminating/mutation-RED 는 '변화 감지' 강제하나 '완결성' 보장 못함, presence 가 완결성 강제하는 척 = 검사연극) 상속. §8.7 discriminating-fixture 선례 소유(CFP-1334) 참조
  - ADR-119  # research-before-claims / 게이트=ground-truth — 게이트 = proxy 아닌 ground-truth. §8.10 manifest·EPIC-RESULTS 매핑 섹션 presence/well-formedness 까지만 fail-closed, "flag 를 실제 켜서 행사·검출했음"(discriminating-B 검출력) 완전봉인 hard-claim 금지(강제하는 척 = 검사연극)
  - ADR-060  # adequacy SSOT — G3 축 = dark-path adequacy(활성화 증명 충분성). "test liveness" 표현 금지(ADR-139/146 §결정8 어휘 가드 상속 — adequacy ⊥ liveness-orchestration(stall) ⊥ 지속-liveness-runtime(soak=G2) 3-sense 동음이의 차단)
  - ADR-127  # no-exemption 자연 N/A 3축 AND — dark-path 자연 N/A(default-off flag 도입 0) = skip 아님. 산출물 target 부재 ∧ downstream 무변경 ∧ 미래의무 무선결(3축 AND). Phase 2 runner-wiring 별 CFP defer = 축3 위반 → 동일 Story 유지
  - ADR-136  # execution-liveness 3요건(결정14, AND) — (L1 blocking 편승) (L2 single canonical .py) (L3 self-test) = §8.10 게이트 born-broken 방지 상위 원리. §8.10 self-test born-hollow(가짜 killed 판정) 금지 = 결정14 재현
  - ADR-005  # N/A 명시 패턴 — §8.10.x dark_path 자연 N/A substantive reason(≥30자) + §11 데이터 마이그레이션 N/A(wrapper-self governance, schema/data 무변경) 근거
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(152) OCC claim(claimant ArchitectPLAgent:CFP-2624:run-1, claim-state max_adr_number 151→152) → dual-key 3-leg. `Glob max+1` 재계산 금지(claim 반환값 사용, §결정4). 149-orphan reconcile 은 G3 범위 밖(#2566 소관)
  - ADR-068  # boundary invariant(약 의존, 배경) — I-7 = cross-ADR claim consistency(discriminating-fixture mandate 아님 — discriminating-fixture 선례 실소유 = CFP-1334 + ADR-006 §8.7 정정). deputy mandate boundary(chief tie-break ladder)
  - ADR-022  # phantom 정정(약 의존) — Story §1(b) "명시적 공개유예(ADR-022 observe-first)" 는 phantom. ADR-022 = DEPRECATED "Sonnet Decider"(deprecated_by CFP-134) 로 "observe-first" 개념 무관(grep 0 hits). G3(b) 명시적 deferral 탈출구 = deferred-item-lifecycle(ADR-128 Amd1) 실 메커니즘으로 재정박(§1 verbatim 불변 보존)
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs `wrapper/change-plans/cfp-2624-g3-dark-path-activation-forcing-function.md`)
related_concepts:
  - dark-path-activation-forcing-function
  - requirement-slice-survival-mapping
is_transitional: false
---

# ADR-152 — dark/born-missing forcing function(G3): §8.10 dark-path activation manifest + Epic-close 요구-슬라이스 매핑

## 상태

Accepted (2026-07-12 KST) — CFP-2624 (Epic CFP-2602 G3) carrier. "기능이 default-off flag(예: mctrader `COMPACT_TIERED=0`) 뒤에 숨어 landing(코드가 repo 에 착지) 됐다는 사실만으로 done(요구 충족)으로 인정돼 부실 산출물이 조용히 통과하는" 병(dark-path adequacy 갭 + 요구-슬라이스 silent drop)을 도메인 불변식 위반으로 재정의하고, (a) default-off flag 뒤 코드가 그 flag 를 실제 ON 으로 켜서 행사하는 discriminating test 를 §8 Test Contract 의 **독립 §8.10 dark-path activation manifest** 로 선언하도록 강제하고 (b) Epic-close 시 PMO 가 각 요구 슬라이스를 {실행 Story 매핑 | 명시적 deferral} 로 매핑한 산출물을 EPIC-RESULTS 에 남기도록 강제하는 governance SSOT. G4(ADR-146) burden-flip 표준·G5(ADR-150) DAST 축의 dark-path 활성화 instantiation — 강화(ratchet↑) 방향, 약화 surface 0(신규 required context 0, branch-protection tuple 무변경, inter-plugin 계약 무변경). ADR-146/150/151(G4/G5/G6)을 **cross-ref**하되 amend 하지 않는다(G3 = 신규 activation oracle 축 = 신규 ADR, §결정 1).

## 컨텍스트

사용자 원문(Story §1 verbatim, 2026-07-11 세션): "기능이 default-off flag 뒤에 숨어 landing ≠ done 인 부실 산출물을 구조적으로 차단한다. 코드가 repo 에 착지했다는 사실만으로 요구 충족으로 인정하지 않는다" — (a) discriminating test 가 flag 를 실제 ON 으로 켜서 행사(dark-path 강제 실행)해야 done, (b) Epic-close 시 각 요구 슬라이스를 실행 Story 또는 명시적 deferral 로 매핑해 조용한 드롭(silent drop) 차단. Epic CFP-2602(요건충족·산출물생존 강제) 확장 child, 게이트 G3 슬라이스 — G1/G2/G4/G5/G6 형제.

실측된 갭(요구사항 lane §2/§4, origin/main 실측):

- **landing ≠ done**: 코드가 repo 에 착지했다는 사실만으로 done 으로 인정됐다. mctrader compactor 요구에서 S4 warm-tier 서빙 구현 Story 부재, S5 롤업이 `COMPACT_TIERED=0` dark 로만 남아 실행 Story 없이 증발한 사례가 anchor [user-input, 재검증 out-of-scope]. Epic #2346 계보("전 lane PASS 후 제품 사망")의 요구사항-측 재정의.
- **"discriminating" 두 지시대상 미분화 위험**: codeforge 에는 이미 "discriminating" 이 게이트 **self-test 축**(discriminating-A)으로 쓰인다(CFP-1334, ADR-006 §8.7 venue-shape self-test, G6 ADR-151 fixture) — 대상 = 검사 기계 자신. G3(a) 는 같은 단어를 **product 축**(discriminating-B)으로 쓴다 — 대상 = 테스트되는 제품 코드의 활성화 상태. 이 둘을 섞으면 중복 게이트가 된다(§결정 1) [verified: git show origin/main:archive/adr/ADR-006 §8.7 discriminating self-test / tests/scripts/test-check-doc-section-8-8.sh].
- **형제 게이트 5종이 검출력(discriminating-B)을 G3 에 명시 양도**: G1(ADR-145 §결정1 test-semantic completeness 미강제) / G2(ADR-148 INV-D3) / G4(**ADR-146 §결정8: "검출력(discriminating)=G3 미강제"**) / G5(**ADR-150 §결정3·4: "검출력=G3 소관"**) / G6(**ADR-151 AC-4: "discriminating_fixture present 가 실제 mutation 죽이는가=G3 소관 미강제"**) — G3 는 그 미강제 잔여의 지정 owner [verified: origin/main 5 ADR verbatim].
- **§8.9(DAST) 가 현 §8 최상위 좌표**: `check_section_8_9` 가 origin/main 에 landed(L435) [verified: git show origin/main:scripts/lib/check_doc_section_schema.py]. §8.10 = 다음 자유 좌표. §8.9 region-slice 종료 정규식 `^#{1,4}\s+\S`(L447) 이 이미 4-hash `#### §8.10` 형제에서 정확히 종료 → §8.10 신설이 §8.8/§8.9 코드에 zero-touch(G5 가 필요로 했던 §8.8 L355 예외 불요 — §결정 7).

도메인 불변식(Story §2.1, INV-G3):

- **INV-G3-1**(landing ≠ done): 코드 착지 사실만으로 done 인정 금지. done = "요구된 동작이 실제로 켜져 행사됨".
- **INV-G3-2**(dark-path activation obligation): default-off flag/게이트 뒤 도달 가능 기능은, 그 flag 를 실제 ON 으로 켜서 행사하는 discriminating test(discriminating-B) 가 있어야만 "구현됨"으로 인정. flag-OFF 로만 통과하는 테스트(=한 번도 안 켜는 테스트)는 dark-path 미행사.
- **INV-G3-3**(requirement-slice survival): Epic 의 각 요구 슬라이스는 (실행 Story 매핑) 또는 (명시적 deferral) 중 하나로만 착지, 어느 쪽으로도 기록되지 않은 채 조용히 증발 = 위반.
- **INV-G3-4**(정직 천장): 게이트는 manifest·매핑 산출물의 presence/구조를 강제할 수 있을 뿐, "flag 가 진짜 켜졌음"(discriminating-B 검출력)·"모든 dark-path/슬라이스 열거 완결성"은 강제할 수 없다(equivalent-mutant/Duhem underdetermination·인벤토리 SSOT 부재) — 강제하는 척 = 검사연극(ADR-119). G4 §8.8.5 / G5 §8.9.5 정직 천장 동형.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음, 요구사항리뷰 lane 단계③ CONFIRMED): feature-flag 테스트 관행 = flag ON/OFF 양 상태 모두 행사, flag-OFF-only = dark 미검증 [source: LaunchDarkly "Testing code that uses feature flags", Martin Fowler "Feature Toggles"] / mutation testing surviving-mutant = weak·missing assertion, equivalent-mutant = 사람 판단 필요(자동 완전강제 불가) [source: LMAX mutation testing, arXiv:2404.09241] / discriminating test ↔ experimentum crucis(Bacon 1620→Hooke/Newton/Boyle)의 "갈림 실험" 계보 + Duhem underdetermination(단일 실험은 원리상 가설군을 결정적으로 못 고름) [source: Wikipedia "Experimentum crucis", Stanford SEP "Experiment in Physics"] / requirement traceability 조용한 드롭 + program-level 미자기강제 [source: Trace.Space, Parasoft DO-178C, Jama].

## 결정

dark-path 활성화 축(discriminating-B)과 요구-슬라이스 생존 축을 §8 Test Contract 의 **독립 §8.10 dark-path activation manifest**(single `dark_path` axis) + **EPIC-RESULTS 요구-슬라이스 매핑 섹션** 으로 신설하되, 기계가 강제 가능한 것(manifest 필드 presence/구조 + status enum + 2 cross-field 선언-정합 / 매핑 섹션 presence/well-formedness)의 천장을 정직히 공개(no-hollow)한다. 착지 = template §8.10 + `check_section_8_10`(`check_section_8_9` verbatim 동형) + `check_epic_results_slice_mapping` + self-test + template `epic-results.md` §requirement-slice-mapping + agent-md mandate(모두 Phase 2, 동일 Story). 결정 SSOT = 본 ADR / 파일 단위 배선 = Change Plan.

### 결정 1 — discriminating-A(meta/self-test) ⟷ discriminating-B(product/activation) 어휘 분리 (본 ADR 핵심 + 신규 ADR 정당)

- **두 지시대상을 어휘로 가른다**: **discriminating-A(meta 축, 기존)** = "린터·게이트가 mutation 을 실제로 죽이는가"(검사 기계 자신 — CFP-1334, ADR-006 §8.7, G6 ADR-151 fixture). **discriminating-B(object 축, G3(a) 신설)** = "product 기능이 default-off flag 뒤에 숨었는데 test 가 그 flag 를 실제 ON 으로 켜서 행사·검출했는가"(테스트되는 제품 코드의 활성화 상태). 이 경계 명문화가 본 ADR 의 핵심. 두 축은 형제 게이트(G1/G2/G4/G5/G6)가 명시적으로 G3 에 양도한 "검출력(discriminating)" 의 두 얼굴 — G3(a) 는 discriminating-B 를 강제하고, discriminating-A 는 G3(a) *게이트 자신*의 self-test 로 재귀 적용된다(§결정 8, AC-4).
- **신규 ADR 정당(A2-5 판정 구조 — "신규 ADR 없이 기존 ADR 변경 금지" P0 방지)**: G3 의 activation oracle(discriminating-B — flag 를 켜서 행사)은 G4 §8.8 의 functional-crash oracle·G5 §8.9 의 attack oracle 과 **다른 mechanism**이다. ADR-146/150 Amendment 로 착륙하려면 landed·self-tested `check_section_8_8`/`check_section_8_9` 를 침습해야 하나, G3 는 (i) 독립 `check_section_8_10` fail-closed 게이트 + (ii) 독립 §8.10 doc-section 좌표 + (iii) 독립 activation-honesty cross-field 검사 + (iv) G3(b) Epic-close 매핑 축(§8 밖 산출물 게이트)을 도입하므로 별도 컨텍스트/결정/결과 블록이 중복이 아니다 → **신규 ADR-152** (ADR-146/150/151 = cross-ref, **amend 아님**).
- **agent-md dark-path mandate = ADR-152 흡수**: TestContractArch/QADev/구현리뷰 가 §8.10 을 author/이행/확인하는 mandate(Phase 2)는 본 ADR 표준의 downstream binding 이지 ADR-006/146/150 의 새 항목이 아니다 → cross-ref 만.

### 결정 2 — §8.10 독립 single-`dark_path` 로스터 (§8.9 편입 아님, next-free 좌표)

- **§8.10 독립 신규 좌표**: §8.9(DAST 점유) → 다음 자유 번호 §8.10(ADR-146 §결정12 / ADR-150 §결정2 "next free number" 논리 상속). §8.6 의도적 gap 은 무관 — doc-section lint 는 **헤딩 존재만으로 트리거**(§8.6 존재 전제 안 함, `check_section_8_5`/`_8_7`/`_8_8`/`_8_9` 동형).
- **single `dark_path` axis(4-기법 loop 아님)**: §8.8 은 4기법 multi-key(`TECHNIQUE_8_8_META`)이나 §8.10 은 **dark-path 단일 축 1행**(§8.10.0 applicability 표 = `dark_path` 1 row, §8.9 DAST single-axis 동형). multi-key loop 구조를 복제하지 않는다.
- **sub-section 좌표(§8.9 numbering rationale 동형)**: §8.10.0 applicability(1 dark_path row) · §8.10.1 dark_path DO 산출물 계약(manifest) 본문 · **§8.10.2-4 의도적 gap**(§8.8 4기법용 §8.8.1-4 / §8.9 single §8.9.2-4 gap 과 positional homolog — single-axis 라 2-4 비어 있음) · **§8.10.5 정직 천장**("N.5 = 천장" 좌표 정합) · §8.10.x aggregate-N/A(default-off flag 도입 0 Story).

### 결정 3 — 정직 천장 = presence/구조 fail-closed, activation-detection-forcing 아님 (INV-G3-4)

- **게이트는 manifest 필드 presence + status enum + 2 cross-field 선언-정합(§결정 4)까지만 fail-closed**. "flag 를 실제로 켜서 관측을 assert 했음"(discriminating-B 실검출) 을 강제하지 **않는다** — 단일 테스트가 "기능이 진짜 켜졌음"을 결정적으로 증명 못 한다(equivalent-mutant + Duhem underdetermination, §컨텍스트 외부근거) → detection-forcing = 검사연극(ADR-119) + false-positive 유인. grep 으로 test body 의 flag-ON set 을 확인 = false-oracle(ADR-145 §결정5 grep 금지) — ast 로도 "flag 를 ON 으로 set + ON assert" 일반 판정 불가.
- **실 활성화 evidence = declared/advisory tier**: 참조된 discriminating test 가 실제 flag ON 을 켜고 ON-state 를 assert 하는지(flag-OFF-only 아님) = **AC-2 declared**(구현리뷰 test body 확인). 모든 default-off flag 열거 완결성 = **AC-1b declared**(flag-naming SSOT 부재). 반복 dark landing 경보 = AC-5 advisory. 게이트는 이들을 강제하지 않는다.
- **잔여 정직 공개(§8.10.5)**: (i) 검출력(discriminating-B 실행사) = 강제 안 함 (ii) 모든 default-off flag 열거 완결성 = AC-1b review 미강제(flag-naming SSOT 부재) (iii) infeasibility 사유 타당성 = review 미강제 (iv) **`g_boundary_check` presence ≠ boundary 실준수**. "완전 봉인" hard-claim 금지 — G4 §8.8.5 / G5 §8.9.5 잔여 공개 동형.

### 결정 4 — §8.10 manifest 산출물 계약 + 2 cross-field 선언-정합 normative (declared-consistency, detection 아님)

- **§8.10.1 dark_path DO 산출물 계약 필드(6 unconditional + token)**: `flag_identifier`(default-off flag/게이트 식별자) · `default_state`(default-off/gated 근거 — dark 성립) · `activation_test_ref`(flag 를 ON 으로 켜는 discriminating test 참조) · `on_state_assertion`(ON-state 관측 assertion — flag-OFF-only 아님) · `discriminating_basis`(flag OFF 시 test 가 fail/skip 하는 근거 — crucial-experiment 성격) · `status`(∈ `{activated, infeasible, natural_na}`) · `g_boundary_check`(Epic-boundary token, region presence). 조건부: `infeasibility_reason`(≥30자 — `status = infeasible` 일 때만).
- **2 fail-closed cross-field 검사**(§8.9 §결정4 declared-consistency ratchet-forward analog):
  - **(a) activation-honesty**: `status = activated` ⟹ `activation_test_ref` non-empty ∧ `on_state_assertion` substantive(≥15자). 빈 stub 로 "켰다" 위장 차단(Story §5.3 edge "선언된 §8.10 manifest 를 빈 stub 로" = AC-1a fail-closed red).
  - **(b) infeasible-reason**: `status = infeasible` ⟹ `infeasibility_reason` ≥30자(§8.9 MUT-E 동형).
- **★ 천장 NON-violation(DesignReview P0 pre-empt)**: 두 검사는 **declared-consistency**("켰다 선언하면 켜는 test·ON assert 도 채워라 / 못 켠다면 정당화하라")를 강제할 뿐 **detection 을 강제하지 않는다** — INV-G3-4 / discriminating-A self-test 재귀(§결정8)를 넘지 않는다. "flag 가 진짜 켜졌고 관측이 진짜 걸렸는가"는 어느 검사도 강제하지 않는다. G5 §8.9 의 "declared-consistency 만, detection 아님" 천장 동형.

### 결정 5 — G3(b) Epic-close 요구-슬라이스 매핑 = EPIC-RESULTS 섹션 presence lint(AC-6b normative) + PMO 감사 obligation(AC-6a declared) + §D-11/ADR-137 disjoint

- **산출물 = EPIC-RESULTS `## §requirement-slice-mapping` 섹션**: `templates/epic-results.md`(SSOT template)에 신규 mandatory 섹션. 각 행 = `slice | disposition{story|defer} | tracking-ref`. Epic-close(playbook §9.7.2) 에 PMO 가 Epic 의 각 요구 슬라이스를 열거·판정.
- **AC-6b normative = 산출물 섹션 presence/well-formedness fail-closed**: `check_epic_results_slice_mapping()` 신규 함수 — **파일명 `EPIC-RESULTS-*.md` 로 gate**(기존 retro false-positive 0), 섹션 present ∧ (≥1 well-formed row ∨ `N/A — <reason ≥30>`) ∧ 천장 문구 present(AC-8 no-hollow). strict context `doc section schema (CFP-28 — strict)` 편승(신규 required workflow 0). **완결성이 아닌 산출물 존재만 강제** — G1 이 AC-list 존재를 강제하되 분해완결성은 review 인 것과 동형.
- **AC-6a declared = "모든 슬라이스 열거" 완결성**: Epic 요구-슬라이스 인벤토리 SSOT 부재(Story §2.4-2) → 기계 강제 불가 = PMO Epic-close 감사 obligation(정직 divergence).
- **PMO Epic-close 내부 3축 disjoint**: §D-11(ADR-045 — 누적 retro follow-up Issue ≥3) ⊥ ADR-137(실머지 코드 duplication anchor) ⊥ **G3(b) 신설(Epic 의 요구 슬라이스)**. 같은 trigger(Epic-close §9.7.2)·owner(PMO) 지만 모집단이 disjoint(AC-7 declared 유지).

### 결정 6 — deferral 착지 = deferred-item-lifecycle 재사용 (신규 deferral 메커니즘 신설 금지, 단일-carrier, AC-6c) + §1(b) phantom 재정박

- **defer disposition → deferred-item-lifecycle**: "deferral" 판정된 슬라이스는 기존 `EPIC-RESULTS §deferred` 5-column row(`source: req-slice-defer`)로 착지해 `check-deferred-item-recovery.sh` 회수 게이트(warning-tier, no-silent-drop)에 도달한다. scanner(`check_deferred_item_recovery.py`)는 `disposition` enum{tracked, observed}만 검증하고 `source` column 은 미검증 [verified: origin/main L144-146] → `req-slice-defer` 추가 = **scanner 무변경**(ADR-137 `triage-defer` 선례 동형, column 신설 아님). 하류 recovery 게이트 tier=warning(기존 유지 — 강도 상향은 별 결정).
- **§1(b) "ADR-022 observe-first" phantom 재정박**: Story §1(b) 가 인용한 "명시적 공개유예(ADR-022 observe-first)" 는 현 repo 부재 phantom [verified: git grep origin/main "observe-first|공개유예|dark launch" = 0 hits]. ADR-022 = DEPRECATED "Sonnet Decider"(deprecated_by CFP-134) 로 "observe-first" 무관. G3(b) 의 "명시적 deferral" 탈출구 = deferred-item-lifecycle(ADR-128 Amd1/CFP-2470) 실 메커니즘으로 착지(§1 verbatim immutable 보존, 요구 드롭 아님 — §3 disambiguation).

### 결정 7 — 게이트 배선 = check_section_8_10 EXTEND + §8.8/§8.9 zero-touch + execution-liveness 3요건

- **`check_section_8_10` 신규 함수 추가**(`check_section_8_9` verbatim 동형, single-axis) + `SECTION_8_10_*` 헤딩 regex + `DARK_PATH_8_10_FIELDS` list(6) + `DARK_PATH_STATUS_ENUM`{activated, infeasible, natural_na} + 2 cross-field 검사 + `main()` 신규 `section_8_10_warns` list/call/print. **신규 workflow `.yml` 0 → 신규 required context 0**(기존 strict context `doc section schema (CFP-28 — strict)` 편승).
- **★ §8.8/§8.9 zero-touch (G5 대비 clean)**: `check_section_8_9` 의 region-slice 종료 정규식이 이미 `^#{1,4}\s+\S`(L447) — 4-hash `#### §8.10` 형제에서 정확히 종료해 §8.9 region 이 §8.10 으로 bleed 하지 않는다. G5 가 필요로 했던 §8.8 L355 region-slice 예외(`^###`→`^#{1,4}`)를 §8.10 은 **불요** — landed 코드 zero-touch. Phase 2 는 `test-check-doc-section-8-8.sh`/`test-check-doc-section-8-9.sh` 재구동으로 무회귀 증명(방어적).
- **execution-liveness 3요건(ADR-136 결정14, AND)**: (L1 blocking) 신규 함수가 기존 strict context 에 편승(동일 `sys.exit(1)`) → born-broken required 위험 0. (L2 full-scope) 단일 canonical `.py` — 신규 `.yml` 부재 → dual-copy 불요. (L3 self-tested) 신규 `tests/scripts/test-check-doc-section-8-10.sh`(§결정 8).
- **RTM location-resolution(G1 P1 재사용, amend 금지)**: §8.10 게이트는 authoritative 위치에서 §8 을 resolve — wrapper-self dogfood = Change Plan §8 / consumer Story = Story §8. 신설하지 않고 ADR-145 §결정6 인용. `check_epic_results_slice_mapping` 는 각 repo CI 가 자기 `docs/retros/EPIC-RESULTS-*.md` 를 스캔(consumer active / wrapper dogfood EPIC-RESULTS = internal-docs 착지 → wrapper CI dormant, PMO obligation+review 가 carry = declared 정직 공개).

### 결정 8 — AC-4 self-test born-hollow 금지 + G6 execution-liveness 인벤토리 등재 (discriminating-A 재귀)

- **`tests/scripts/test-check-doc-section-8-10.sh`**(L3 discriminating-A self-test, `test-check-doc-section-8-9.sh` verbatim-homolog): TC-CLEAN-PASS(완전-valid activated manifest 인데 test 가 관측을 얕게만 걸어도 PASS — detection 미강제 천장 실증) + mutation A/B/C/D/E kill(MUT-A DO 필드 누락 / MUT-B g-token 누락 / MUT-C status enum 위반 / MUT-D activated 인데 on_state_assertion 공백=activation-honesty / MUT-E infeasible 인데 reason 누락) + N/A-substantive discriminating + sibling-dependency guard(check_section_8_10 부재/미배선=명시 FAIL) + LIVE ceiling_honesty_check(실 template §8.10.5 4 잔여 개시, fixture-fallback 금지).
- **born-hollow 금지(AC-4)**: self-test 는 mutant 가 실제로 leak(기대-PASS 로 새어나감)함을 **positive 단정으로 실증**(original=exit 1 AND mutated=exit 0 → KILLED). `exit≠(false,1)` 을 "killed" 로 오수용 금지. **born-hollow 재발 경계**: G2 F-CR-004 / G4 F-CR-001 처럼 "가짜로 killed 판정" 하는 self-test 는 이 Story 가 겨냥하는 dark 결함의 게이트-측 재현이므로 금지.
- **G6 execution-liveness 인벤토리 등재**: §8.10 self-test 를 G6(ADR-151) execution-liveness 인벤토리에 `channel_status: alive` 로 등재(discriminating-A 축 = G6 소유, G3 는 discriminating-B 소유 — 축 disjoint).

### 결정 9 — Epic 게이트 disjoint 확장 (G1⊥G2⊥G3⊥G4⊥G5⊥G6)

- Epic CFP-2602 게이트 disjoint: **G1**(AC↔§8↔실파일 zero-drop, ADR-145) ⊥ **G2**(soak/restart/replay 런타임 지속 생존, ADR-148) ⊥ **G3**(dark-path 활성화 discriminating-B + Epic-slice 생존, **본 ADR**) ⊥ **G4**(기능 동적 §8.8 로스터, robustness oracle, ADR-146) ⊥ **G5**(런타임 DAST §8.9, attack oracle, ADR-150) ⊥ **G6**(self-test execution-liveness 인벤토리, discriminating-A, ADR-151). 공유 = 원리("landing≠done / proxy≠ground-truth", Epic #2346 계보)뿐. ADR-146/150 §결과 disjoint 목록을 ⊥G3 로 **cross-ref 확장**(amend 아님).
- **한 변경이 G1 PASS(테스트 존재) 이면서 G3(a) FAIL(flag-OFF-only) 가능** — G1 은 "AC 에 테스트가 존재하나"를, G3(a) 는 "그 테스트가 dark-path 를 켜나"를 본다(granularity·축 disjoint).
- **G2/G4/G5 경계 무침범**: soak/restart/replay = G2 단일소유 / 기능 fuzz = G4 / attack = G5. §8.10 레코드 `g_boundary_check` = "soak(G2)·fuzz(G4)·DAST attack(G5)로 넘어가지 않음" 을 확인(§결정 3 (iv) 천장: presence ≠ 실준수).

### 결정 10 — adequacy 어휘 가드 + inter-plugin 계약 변경 0 (RTM 이중소유 회피)

- G3 축 명칭 = **"dark-path adequacy(활성화 증명 충분성)"**(ADR-060 SSOT). **G3 문서 "test liveness" 표현 금지**(ADR-139/146 §결정8 어휘 가드 상속 — adequacy ⊥ liveness-orchestration(stall) ⊥ 지속-liveness-runtime(soak=G2) 3-sense 동음이의 차단). soak/생존 어휘는 G2 참조 맥락에서만. 핵심 어휘 = "landing≠done" / "dark-path activation" / "discriminating-B".
- **manifest 필드(flag_identifier/activation_test_ref 등)를 어떤 inter-plugin 계약에도 넣지 않는다** — template §8.10 + `check_section_8_10` 이 carry(§8.5/§8.7/§8.8/§8.9 이 design-output 필드 추가 0 으로 착륙한 선례 동형). 계약에 넣으면 RTM 이중 소유(design-output ∧ §8.10) → drift. design-output-v2 / test-verdict-v2 / review-verdict 무변경.

## 대안 (기각 근거)

- **dark-path 를 §8.9 서브필드/§8.8 5번째 기법으로 편입**: activation oracle 을 attack/robustness oracle 로스터에 혼입(축 오염) + landed `check_section_8_9`/`_8_8` 침습 → 기각, §8.10 독립(§결정 2).
- **ADR-146/150 Amendment 로 착륙**: activation oracle = 새 mechanism + 신규 게이트/좌표/cross-field 검사 + G3(b) Epic-close 축 → 별 컨텍스트/결정/결과 블록 필요 → 기각, 신규 ADR-152(§결정 1, A2-5 구조).
- **discriminating-B 실검출 강제(flag 를 실제 켰음을 기계 판정)**: grep-oracle(ADR-145 §결정5 금지) / ast 일반 판정 불가 / equivalent-mutant·Duhem 천장 → detection-forcing = 검사연극 + false-positive 유인 → 기각, presence/구조 + declared-consistency fail-closed(§결정 3/4, INV-G3-4).
- **AC-6b declared(PMO obligation + review 만, 산출물 lint 미배선)**: EPIC-RESULTS 매핑 섹션 존재를 기계 강제 안 하면 born-missing 재발 → 기각, `check_epic_results_slice_mapping` presence lint(§결정 5, 완결성은 여전히 declared).
- **신규 deferral 메커니즘 신설(요구-슬라이스 전용 회수 채널)**: deferred-item-lifecycle 과 중복 = 이중-carrier → 기각, 기존 §deferred + `source: req-slice-defer` 재사용(§결정 6, 단일-carrier).
- **G3(b) 를 §D-11/ADR-137 과 동일시**: 모집단 겹침 → drift → 기각, 3축 disjoint(§결정 5, AC-7).
- **신규 required workflow context(tuple 확장)**: presence/구조 doc-lint 는 기존 strict context 로 충분 → 기각, `check_section_8_10`/`check_epic_results_slice_mapping` EXTEND(§결정 7).
- **§8.8 L355 형 region-slice 예외 추가**: §8.9 종료 정규식이 이미 `^#{1,4}` 로 §8.10 형제에서 종료 → 불요 → 기각, zero-touch(§결정 7).

## 결과

- default-off flag 뒤 도달 가능한 product 코드가 §8.10 dark-path activation manifest 없이(또는 빈 stub 로) 착지하면 §8.10 게이트가 구조적으로 차단(manifest 필드 presence + status enum + 2 cross-field 선언-정합 fail-closed). Epic 요구 슬라이스가 실행 Story·deferral 어느 쪽으로도 기록 없이 증발하려 하면 EPIC-RESULTS `§requirement-slice-mapping` 섹션 부재/빈칸으로 감지(presence fail-closed) + defer 는 deferred-item-lifecycle 회수 게이트 도달. 검출력(discriminating-B 실행사)·열거 완결성·사유 타당성은 AC review + advisory 로 defense-in-depth(강제 금지).
- 형식누락·rot 저감 + 검출력·완결성·사유타당성·g-boundary-준수 4 잔여 정직 공개 = ADR-119/ADR-146 §8.8.5/ADR-150 §8.9.5 정합(검사연극 회피). 2 cross-field 는 declared-consistency 만 강제(detection 미강제) — INV-G3-4 / discriminating-A self-test 재귀(§결정8) 무침범.
- Epic CFP-2602 게이트 disjoint 확장: **G1⊥G2⊥G3⊥G4⊥G5⊥G6**. G3 = dark-path 활성화(discriminating-B) + Epic-slice 생존 축 — 형제 5종이 명시 양도한 검출력 잔여의 지정 owner.
- 약화 surface 0: 신규 required context 0, **branch-protection tuple 무변경**(doc-SSOT 7-tuple ∧ live 6-tuple[ac-traceability-matrix 미등록 = CFP-2609 reconcile 대기] 양쪽에 추가 0 — 기존 strict context `doc section schema (CFP-28 — strict)` 편승) / inter-plugin 계약 무변경 / 신규 category 0. §8.8/§8.9 코드 zero-touch(G5 L355 예외 불요). sunset_justification = N/A(permanent governance ratchet, ADR-058 §결정 5 강화 방향).
- **wrapper-self dogfood**: codeforge 자체 = deployable product 0(runtime-inert) → 본 Story 의 §8.10 = 자연 N/A(default-off product flag 도입 0). 실 dark-path activation manifest = consumer(예: mctrader `COMPACT_TIERED`) §8. wrapper-self 는 게이트-self-test(discriminating-A) active. Phase 2 정량 파라미터는 `[empirical-source: consumer, Phase 2]` defer(추정값 lock-in 아님). 본 요구사항 lane 자체가 stale-read 로 §8.8/8.9 "미존재" 오판한 self-dogfood 사례(Story §2.5) — G3 의 "landing≠done / proxy≠ground-truth" 정신과 정합.

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2624.md` (§7 설계 서사 / §3 ADR-152 확정)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2624-g3-dark-path-activation-forcing-function.md`
- 수정(Phase 2): `plugins/codeforge-design/templates/change-plan.md`(§8.10 로스터) · `templates/story-page-structure.md`(§8.10 미러) · `scripts/lib/check_doc_section_schema.py`(`check_section_8_10` 신규 + `check_epic_results_slice_mapping` 신규 — §8.8/§8.9 zero-touch) · `templates/epic-results.md`(§requirement-slice-mapping 섹션 + §deferred `source: req-slice-defer` enum 확장) · `plugins/codeforge-pmo/agents/PMOAgent.md`(Epic-close 요구-슬라이스 매핑 감사 mandate) · `plugins/codeforge-design/agents/TestContractArchitectAgent.md`(§8.10 계약 mandate)
- 신규(Phase 2): `tests/scripts/test-check-doc-section-8-10.sh`(L3 discriminating-A self-test — 천장 실증 + 5 mutation + born-hollow positive-leak + LIVE ceiling_honesty)
- Phase 1: `docs/architecture/codeforge-family.md`(data_flow 1-line + Open Decisions row — 갱신 또는 §10.A none_rationale)
- 선례: `scripts/lib/check_doc_section_schema.py` `check_section_8_9`(clone source — CFP-2612/ADR-150) · `tests/scripts/test-check-doc-section-8-9.sh`(self-test 선례) · `scripts/check-deferred-item-recovery.sh` + `templates/epic-results.md` §deferred(G3(b) deferral 재사용 — CFP-2470/ADR-128 Amd1) · ADR-146(G4 sibling — burden-flip·정직 천장·Phase 1/2 분리) · ADR-150(G5 sibling — §8.9 single-axis 형판) · ADR-151(G6 sibling — discriminating-A self-test 인벤토리) · ADR-145(G1 sibling — 3-tier AC + RTM location-resolution)
