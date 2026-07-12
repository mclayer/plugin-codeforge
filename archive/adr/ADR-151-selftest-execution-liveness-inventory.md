---
adr_number: 151
title: wrapper-self self-test execution-liveness 인벤토리/메타-게이트 신설 — 선언(L3 fixture)→실행(CI 채널 alive) 승격 forcing-function (presence/alive/형식 천장, 검출력=G3 미강제)
status: Accepted
category: governance
date: 2026-07-12
carrier_story: CFP-2622
supersedes: []
related_adrs:
  - ADR-136  # 강 의존(핵심 렌즈, amend 아님) — 결정14 execution-liveness 3요건(L1 blocking/L2 full-scope/L3 self-tested, cross-cutting standing 원리) = 본 ADR 의 자기적용 대상 원리. G6 = 그 원리를 wrapper-self self-test corpus 전체에 강제하는 corpus-wide 메타-게이트 신설. A2-5 판정(결정 1): 원리 재정의 0(재사용만) + 신규 fail-closed 메타-게이트 mechanism 도입 → 신규 ADR(ADR-136 결정14 actionlint N-class 은 단일 게이트 self-test, 본 ADR 은 corpus-wide 인벤토리 강제 = 별 mechanism). ADR-136 무수정
  - ADR-146  # 강 의존(G4 형제, landed) — burden-flip(do-unless-proven-infeasible)·정직 천장(결정8)·자연 N/A 3축 AND(결정7)·A2-5 "신규 ADR vs Amendment" verbatim 판정 구조(결정11)·"test liveness" 어휘 금지(결정4) 상속. G6 = G4 가 wrapper 에 declarative 로 남긴 실행 축을 wrapper 고유(self-test 실행-liveness) 형태로 실체화
  - ADR-148  # 강 의존(G2 형제) — INV-D2(선언 ⊥ 실행 2-표면) 상속. G6 차별점: 형제 arc 가 wrapper 에 declarative 면제로 둔 "실행 표면"이 wrapper 에서는 런타임 앱 아닌 CI self-test corpus 로 실재 → declarative 면제 아닌 실제 실행 대상
  - ADR-150  # 강 의존(G5 형제) — 독립 축 single-axis 신규 ADR 선례(§8.9 = "next free number" 논리) + presence 천장(재현/실행 presence 까지, 검출 강제 아님) 동형. Epic CFP-2602 "게이트 G당 1 신규 ADR" 패턴 정합
  - ADR-145  # 정합만(amend/재사용 금지) — G1 3-tier AC(normative/declared/advisory) + AC-ID sub-letter 문법(`ac_id.py` SSOT). G6 AC-1a..AC-10 은 이 문법에 정합. G1 게이트(AC↔§8↔실파일 zero-drop) ⊥ G6 게이트(self-test 실행-liveness) disjoint
  - ADR-139  # 3-sense 동음이의 가드 — adequacy(hollow-gate, green-but-dead) ⊥ liveness-orchestration(stall) ⊥ 지속-liveness-runtime(soak=G2). G6 축 명칭 = execution-liveness(게이트 실행-무결성)/adequacy. "test liveness"/soak 어휘 금지(G2 참조 맥락 외)
  - ADR-060  # evidence-gate — L1 blocking 승격(non_required/warning → required)은 PR누적≥20 + failure=0 + sibling 3-tuple 충족 별 carrier Story. 본 ADR 은 승격 안 함(정직 기록만, day-1 blocking 강제 아님)
  - ADR-127  # no-exemption 자연 N/A 3축 AND(§결정5) SSOT — soak/real-render/DAST runtime 자연 N/A = skip 아님(산출물 target 부재 ∧ downstream 무변경 ∧ 미래의무 무선결 AND). skip-offer 금지 정합(신규 self-test 무레코드 침묵 un-run 차단 = ADR-127 정신)
  - ADR-130  # path-filter 금지(required check permanent-pending 함정) + job-level `if:` graceful no-op — 메타-게이트 workflow 배선 시 준수(wrapper-self-only `if: github.repository ==` 는 정당, hashFiles job-level 재발 금지)
  - ADR-119  # research-before-claims / 게이트=ground-truth — 정직 천장(presence/alive/형식 까지, 검출력 강제=검사연극) + 제안 필요성 게이트(진성 hollow-gate 실측 근거). GAP hard-claim 금지(wrapper-self 선언-only 아님, 26/35 discriminating corpus 보유)
  - ADR-048  # 경계 — 메타-게이트 = 정적 lint(배선 presence 검사)이지 신규 codeforge 동적 러너 부활 아님(StatefulTest deprecated 무충돌). CI-native 정합
  - ADR-005  # N/A 명시 패턴 + inheritance 차단 — wrapper-self runtime 축 N/A(plugin-meta-na) 표기 선례 + §11 데이터 마이그레이션 N/A
  - ADR-147  # 경계(disjoint 축) — 러너 인프라(배선된 job 이 실 러너를 배정받는가)는 ADR-147 소관, G6 OOS. G6 = "workflow 가 self-test 를 배선했는가(선언→실행)" 축, "배선된 job 이 실 러너를 받는가" 축 아님(2 축 disjoint)
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(151) OCC claim(claimant ArchitectPLAgent:CFP-2622:run-20260712T012444Z, claim-state max 150→151). dual-key 3-leg 정합(filename ∧ frontmatter ∧ registry row)
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs `wrapper/change-plans/cfp-2622-g6-selftest-execution-liveness-inventory.md`)
  - ADR-006  # §8 Test Contract authoring mechanism owner — 메타-게이트 자신의 L3 self-test = TestContractArchitectAgent input + ArchitectAgent(chief) 통합
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary(chief tie-break ladder)
related_concepts:
  - mutation-based-hollow-gate-detection
  - execution-based-review-verification
  - lane-verification-floor
  - github-actions-expression-context-availability
is_transitional: false
---

# ADR-151 — wrapper-self self-test execution-liveness 인벤토리/메타-게이트 신설

## 상태

Accepted (2026-07-12 KST) — CFP-2622 (Epic CFP-2602 G6) carrier. "wrapper-self 산출물은 이미 대규모 discriminating self-test corpus 를 보유하나(정직 인정 — 35 self-test 중 26 이 mutation-kill 키워드 보유), 그중 12 는 **어느 workflow 에도 배선 안 돼(DEAD) L3 fixture 는 작성됐으나 실행 안 되는(선언→실행 미승격)** 상태로 남는다"는 병(게이트-실행 adequacy 갭)을 도메인 불변식 위반으로 재정의하고, `tests/scripts/*.sh` self-test corpus 전수에 대해 **실행 채널의 존재·alive·discriminating fixture 형식 presence 를 구조 fail-closed 로 강제하는 execution-liveness 인벤토리/메타-게이트**를 신설하는 governance SSOT. ADR-136 결정14 execution-liveness 3요건(L1/L2/L3)의 wrapper-self self-test corpus-wide 자기적용 — 강화(ratchet↑) 방향, 약화 surface 0(신규 required context 0, branch-protection 6-tuple 무변경, inter-plugin 계약 무변경). ADR-136 을 **cross-ref**하되 amend 하지 않는다(G6 = 신규 corpus-wide 강제 mechanism = 신규 ADR, §결정 1).

## 컨텍스트

사용자 원문(Story §1 verbatim): "codeforge 테스트 레인이 테스트 가능한 최대한의 동적 테스트를 수행하도록 강화한다 — 세 번째 축: wrapper-self 의 동적 테스트를 '선언(declared)'에서 '실제 런타임 실행'으로 승격한다"(2026-07-11 세션, 최광범위 승인). Epic CFP-2602(요건충족·산출물생존 강제) 확장 child, 게이트 G6 슬라이스 — G1(ADR-145 AC traceability)·G2(ADR-148 soak)·G4(ADR-146 dynamic burden-flip)·G5(ADR-150 DAST) 형제.

### 도메인 사실 (origin/main ground-truth 실측 — 로컬 워킹트리 stale, verify-before-trust 상 origin/main 우선)

1. **wrapper-self = 0-core 거버넌스 모노레포 — 런타임 앱 부재.** 자기 산출물(agent-md / skill / template / workflow / lint 스크립트 / ADR)은 문서·거버넌스 아티팩트. 따라서 wrapper-self 에서 "동적 테스트"의 도메인 의미 = **CI self-test corpus 가 결함을 실제로 죽이는지 실행하는 것**(= wrapper 의 "런타임"). consumer 형 soak/real-render/DAST 를 억지 이식 = over-forcing 검사연극(ADR-119 §결정9 위반).

2. **self-test corpus census (execution-backed)**: `tests/scripts/*.sh` = **35** 파일 `[verified: git ls-tree origin/main tests/scripts + basename count]`. 이 중 **13 이 어느 workflow 에서도 basename-미참조**, 그중 1(`test_check-adr-cross-ref-consistency.sh`)은 `adr-cross-ref-consistency.yml:51` 의 inline `--self-test` 로 대체 실행 → **12 truly-DEAD** `[verified: workflow blob(173 파일) full-scan basename cross-ref]`.

3. **진성 hollow-gate 실증**: required 6-tuple context `doc section schema (CFP-28 — strict)`(lint.yml `doc-section-schema` job → `bash scripts/check-doc-section-schema.sh`)의 mutation-kill self-test `test-check-doc-section-8-7.sh` / `-8-8.sh` / `-8-9.sh` 는 **완전히 build 된 discriminating fixture**(`assert_discriminating` exit-code 대조 + Mutation A/B/C 실 RED)이나 **어느 workflow 에도 배선 안 됨** `[verified: check-doc-section-schema.sh self-test token = 0 / 세 test 파일 workflow 미참조]`. 즉 required 게이트가 hollow 화(§8.7/8.8/8.9 검사 무력화)돼도 잡을 채널 부재 = 현존 hollow-gate 위험.

4. **auto-discovery 부재**: self-test 배선 = 1-script-당-1-explicit-`run:`-line. bulk-runner/auto-discovery 부재 → 신규 `.sh` 가 침묵 un-run 되는 root cause(silent-un-run).

### 왜 지금 (제안 필요성 게이트 — ADR-119 §결정9 통과)

① **깨졌나·강제 요인**: required 게이트(doc-section)의 self-test 가 실행 안 됨 = 현존 hollow-gate 위험(관찰자 없어도 결함). ② **이득>비용**: 저비용 정적 메타-게이트로 silent-un-run class 봉인 + 진성 hollow-gate 3건 승격. ③ **관찰자 없어도 할 일**: Epic CFP-2602 charter(요건충족·산출물생존) 직접 슬라이스. GAP hard-claim 금지 정합 — wrapper-self 는 선언-only 가 아니며(26/35 discriminating), 갭은 wholesale 부재 아닌 "L3 fixture 작성됐으나 실행 채널 죽음".

## 결정

### 결정 1 — ADR-136 관계 판정 (Amendment vs 신규 ADR — A2-5 verbatim 구조)

**(ADR-146 결정11 의 A2-5 판정 구조를 verbatim 적용 — "신규 ADR 없이 기존 ADR 변경 금지"(설계리뷰 P0) ∧ 그 역("기존 ADR 로 착륙 가능한데 왜 신규") 양 prong 을 모두 반증한다.)**

- **Amendment prong (ADR-136 결정14 로 착륙) = 기각**: ADR-136 결정14 는 execution-liveness *원리*(3요건)를 codify 하고 **단일 게이트 self-test 1건**(actionlint N-class, §14.3)을 wire 했다. 그 Amendment(CFP-2535)가 Amendment 였던 이유 = "원리의 발생 계보가 본 ADR + 신규 메커니즘 0(전부 기존 concept 합성)". G6 은 그 조건을 충족하지 않는다 — G6 은 원리를 하나 더 적용하는 게 아니라 **corpus 전수(35 self-test)에 대한 인벤토리-강제 메타-게이트**라는 신규 mechanism(신규 fail-closed 게이트 + 인벤토리 스키마 + silent-un-run root 차단 forcing-function + AC-9 재귀 자기적용)을 도입한다. ADR-136 결정14 자신이 "다른 게이트가 이 원리 위반이면 **별 Story 로 정정**"이라 명시 — 별 Story 의 carrier 는 그 Story 고유 mechanism 이 신규면 신규 ADR.
- **신규 ADR prong = 채택**: G6 은 (i) `tests/scripts/*.sh` 전수 execution-liveness 레코드 presence 를 강제하는 **신규 fail-closed 메타-게이트**를 도입하고 (ii) **신규 인벤토리 스키마**(§결정 2)를 정의하며 (iii) **메타-게이트 자신의 재귀 L3 자기적용**(§결정 9)을 요구한다. 별도 컨텍스트/결정/결과 블록이 중복이 아니다 → **신규 ADR-151**. 형제 arc 정합(G1=ADR-145 / G2=ADR-148 / G4=ADR-146 / G5=ADR-150 = 각각 상속 원리를 적용하되 신규 게이트 mechanism 이므로 신규 ADR — Epic CFP-2602 "게이트 G당 1 신규 ADR" 패턴).
- **ADR-136 무수정**: execution-liveness 3요건(L1/L2/L3)·2-표면·N-class 는 그대로 authoritative. 본 ADR 은 cross-ref 만 하고 supersede/rewrite 하지 않는다 → "ADR-136 무단 확장" P0 발생 없음.

### 결정 2 — execution-liveness self-test 인벤토리 레코드 스키마 (per `tests/scripts/*.sh` 1행)

인벤토리 SSOT = **`docs/selftest-execution-liveness-inventory.yaml`**(machine-parseable registry, `docs/evidence-checks-registry.yaml` 선례 위치 정합 — 문서 표/check-내장 대안 기각: 표=기계-strict 불가, check-내장=불투명). per-self-test 레코드 필드:

| 필드 | 뜻 | fail-closed? |
|---|---|---|
| `self_test` | 스크립트 경로(`tests/scripts/*.sh`) | AC-1a(부재=FAIL) |
| `execution_channel` | `workflow:job` \| `inline_self_test_flag` \| `agent_runtime` \| `manual_registered` | AC-2 |
| `channel_status` | `alive` \| `dead`(채널 부재) \| `permanently_skipped`(`if: false`/born-invalid) | AC-3 |
| `blocking_tier` | `required` \| `non_required` \| `warning_tier` \| `manual` (정직 기록 — L1 승격은 별건) | 기록만 |
| `discriminating_fixture` | `present`(mutation-kill GREEN≠RED 패턴) \| `smoke_only` \| `N/A` | AC-4 형식 presence 까지만 |
| `l2_full_scope` | `both_copies`(templates/+.github/) \| `single` \| `N/A`(non-parity) | AC-5 |
| `manual_reason` | ≥30자 substantive (channel=`manual_registered`/`agent_runtime` 시) | AC-2(부재=FAIL) |
| `g_boundary_check` | runtime 축(soak=G2 / DAST=G5 / real-render=§8.7)으로 넘어가지 않음 확인 + 형제 축 참조 | AC-8 |

`manual_reason` substantive 기준 = §8.5.0 동형 재사용(≥30자 + 반복·공백-only 반려). 인벤토리 자체가 **선언 표면**(정적·wrapper dogfood normative) — 실행 표면(CI 채널 alive)과 disjoint(ADR-148 INV-D2 상속).

### 결정 3 — 메타-게이트 fail-closed 검사 규칙 (normative linter) + review/advisory 분리

메타-게이트 = **정적 lint**(`scripts/lib/check_selftest_execution_liveness.py` + wrapper `scripts/check-selftest-execution-liveness.sh`) — 신규 동적 러너 부활 아님(ADR-048 무충돌, §결정 1 A1). 검사 규칙:

- **AC-1a (normative)**: `tests/scripts/*.sh` 각 파일 = 인벤토리에 레코드 존재(부재 = fail-closed). 신규 self-test 가 무레코드 침묵 un-run 되는 root 차단.
- **AC-2 (normative)**: `execution_channel` 값이 실재 배선(workflow `run:` line / inline `--self-test` / registry)을 가리키거나, `manual_registered`/`agent_runtime` 이면 `manual_reason`(≥30자 substantive) 존재(없으면 FAIL).
- **AC-3 (normative)**: `execution_channel: workflow:job` 레코드는 참조 workflow/job 이 실재 ∧ `permanently_skipped` 아님(presence 검사 — css-lint-test 영구 skip / job-level hashFiles born-invalid 재발 차단).
- **AC-5 (normative)**: parity-bearing self-test(byte-identical `templates/`+`.github/` 대상)는 `l2_full_scope: both_copies`. non-parity = `N/A`.
- **AC-8 (normative)**: wrapper-self runtime 축(soak/real-render/DAST) N/A 표기는 자연 N/A **3축 AND**(산출물 target 부재 ∧ downstream 무변경 ∧ 미래의무 무선결) + `g_boundary_check` 존재. 억지 runtime 이식 = over-forcing 차단.
- **AC-9 (normative, 재귀)**: 메타-게이트 자신이 인벤토리에 레코드 보유 + 자기 discriminating self-test + `channel_status: alive`(§결정 9).

**비-fail-closed (검사연극 회피 — 강제 안 함)**:
- **AC-1b (declared/review)**: feasible self-test 최대 CI-배선(do-unless-proven-manual). 대조 완결성은 기계 완전판정 불가 → DesignReview obligation.
- **AC-4 (G3-ceiling)**: `discriminating_fixture: present` 가 **실제로 mutation 을 죽이는가**(검출력) = review-tier / G3 소관 — 기계 강제 불가. 메타-게이트는 fixture 형식 presence(GREEN≠RED 패턴)까지만.
- **AC-6 (declared/review)**: L1 blocking 승격 = ADR-060 evidence-gate 별 carrier — G6 은 승격 안 함(정직 기록만).
- **AC-7 (doc-presence)**: 게이트 천장·잔여 정직 명시 강제(§결정 7).
- **AC-10 (advisory)**: near-namesake/중복 self-test 저감 권고 경보(blocking FAIL 권한 없음).

### 결정 4 — 12 truly-DEAD self-test 분류 (execution-model 4-bucket + backfill 우선순위)

설계 lane 이 §4.3/§5.5 위임받은 execution-model 분류(실측 근거). "dead gate" hard-claim 금지 — agent-runtime tool 은 hypothesis-withheld:

| bucket | self-test | execution-model 판정(실측) | 처리 |
|---|---|---|---|
| **A 진성 hollow-gate (우선 backfill)** | `test-check-doc-section-8-7/-8-8/-8-9.sh` | required 게이트 `check-doc-section-schema.sh`(§8.7 UI-render / §8.8 G4 dynamic / §8.9 G5 DAST case)의 mutation-kill fixture, fully-built, 채널 DEAD `[verified]` | **Phase 2: 신규 wrapper-self-only workflow 배선 → channel alive 승격**(선언→실행). 최우선 |
| **B agent-runtime tool** | `test-check-fix-replay-disposition.sh` / `test-check-merge-gate-disposition.sh` / `test-check-mutation-disposition.sh` | 대응 check(`fix_replay_disposition.py` / `check_merge_gate_disposition.py` / `check_mutation_disposition.py`)가 FIX loop·merge·리뷰 시점 **agent/Orchestrator-runtime 호출**(fix-event-v1 contract / orchestrator-playbook / root-cause-decision·fix-ledger SKILL 참조 `[verified]`) — CI gate 아님 | `execution_channel: agent_runtime` + `manual_reason`(runtime 호출 지점 명시). "dead gate" hard-claim 금지 |
| **C dead-path 존치(live-machinery)** | `test-check-stakes-tier-gating.sh` | `check-stakes-tier-gating.sh` = ADR-141(전 에이전트 opus 단일 tier) 이 명시한 "dead-path 존치(live-machinery)" — stakes-tier 머신이 보존되나 all-opus 하 dormant `[verified: ADR-141 row]` | `manual_registered` + `manual_reason`(ADR-141 dead-path 존치 근거) |
| **D orphan / 이미-해소 dead-path (dedup·정리)** | `test-check-lint-css.sh`(subject `check-lint-css` 부재; 실 게이트=css-lint 37-ref + `test-css-lint.sh` WIRED — AC-10 near-namesake) / `test-check-story-stakes-overlay.sh`(subject 부재) / `test_adr-path-dead-path-sweep.sh`(CFP-2519 one-shot subject 부재) / `test_adr-sunset-criteria-pathagnostic.sh`(check-adr-sunset-criteria.sh EXISTS+8-ref 이나 본 test unref → inline-cover 확인 or backfill) / `test_schema-lib-archive-adr-activation.sh`(CFP-2523 one-shot subject 부재) | subject 부재 orphan / 1-shot 잔재 `[verified: 광역 tree search subject 부재]` | Phase 2: `manual_registered`+reason 또는 remove/dedup(AC-10 권고). `adr-sunset-criteria-pathagnostic` 만 inline-cover 여부 실측 후 A/inline 분기 |

인벤토리 스코프 = **전 35 `tests/scripts/*.sh`**(CI-gate 한정 아님) — agent-runtime/dead-path/orphan 도 `manual_reason` 로 강제 enroll(제외 = silent-un-run 구멍). backfill 우선순위 = **bucket A(진성 hollow-gate) 우선**, B/C/D 는 인벤토리 정직 disposition(전수 CI-wire 아님).

### 결정 5 — 신규 required context 0 (배선 정책) + L1 blocking 승격 defer

- **배선 = 신규 non-required wrapper-self-only workflow** — exemplar 답습: `actionlint-workflows-test.yml`(wrapper-self-only `if: github.repository == 'mclayer/plugin-codeforge'`, template-copy 없음 → 단방향 parity walk 상 자동 parity-safe, day-1 hard-fail "meta gate that verifies detection is alive") + `ac-traceability-self-test.yml`(day-1 hard-fail, dedicated self-test workflow). 메타-게이트 + bucket A 3 self-test 를 이 패턴으로 wire. **branch-protection 6-tuple 무변경**(G4 결정5 / G5 동형).
- **L1 blocking 승격 = defer**(ADR-060 evidence-gate 별 carrier Story) — PR누적≥20 + failure=0 + sibling 3-tuple 충족 시. G6 은 non_required/warning-tier 유지(day-1 blocking 강제 아님, ADR-060 warning-first 정합). 만약 미래 required 승격 시 born-broken 안전전제 = **self-test suite green ∧ own-PR green THEN required 등록**(ac-traceability-self-test.yml ordering-invariant 상속) + 사용자 결정 필요.

### 결정 6 — wrapper-self runtime 축 자연 N/A 3축 AND

soak(G2)·real-render(§8.7)·DAST(G5) runtime 축 = wrapper-self **자연 N/A**(런타임 데몬/frontend/공격 표면 산출물 부재). skip 아님 — **3축 AND**(① 산출물 target 부재 ② downstream 무변경 ③ 미래의무 무선결) + 각 인벤토리 레코드 `g_boundary_check`(형제 축 참조). 억지 이식 = over-forcing 검사연극 → AC-8 로 구조 차단. 어떤 자연 N/A 도 미래 CFP defer 로 미루면 축③ 위반 → 동일 Story 유지(ADR-127 정합).

### 결정 7 — 정직 천장 (presence/alive/형식 까지, hard-claim 금지)

게이트가 기계 강제 가능한 것 = **self-test CI 배선 presence / 채널 alive / discriminating fixture 형식 presence / L2 양-copy presence** 까지. **강제 불가(정직 공개)**: (i) discriminating **검출력**(fixture 가 진짜 모든 mutation 을 죽이는가) = G3 소관 미강제 (ii) 열거 완결성(feasible self-test 최대 배선) = review-tier (iii) L1 blocking 승격 타당성 = ADR-060 evidence-gate. **"wrapper 동적검증 완전 봉인" hard-claim 금지** — "실행-채널 fail-closed + 선언→실행 갭 저감 + 잔여 정직 공개"로 재약속(AC-7 = 게이트/표준 문서에 이 천장·잔여 명시 강제). ADR-119 게이트=ground-truth / absence of evidence ≠ evidence of absence 정합.

### 결정 8 — 어휘 = execution-liveness / adequacy ("test liveness"·soak 금지)

G6 축 명칭 = **execution-liveness(게이트 실행-무결성)** 또는 **adequacy**. 3-sense 동음이의 가드(ADR-139): adequacy(green-but-dead) ⊥ liveness-orchestration(background wait stall) ⊥ 지속-liveness-runtime(soak=G2). wrapper-self 문서에서 "test liveness"/"soak"/"생존" 어휘는 G2 참조 맥락 외 금지(ADR-146 결정4 / ADR-139 상속).

### 결정 9 — 메타-게이트 재귀 L3 자기적용 (AC-9)

메타-게이트 자신이 execution-liveness 준수 — `check_selftest_execution_liveness.py` 는 자기 discriminating self-test(`tests/scripts/test_check-selftest-execution-liveness.sh`)를 보유하고, 그 self-test 는 신규 wrapper-self-only workflow 에 배선돼 `channel_status: alive`. 메타-게이트가 hollow 로 새지 않음(게이트를 검증하는 게이트도 hollow 일 수 있다 — [[lane-verification-floor]] R-5 meta-hollow-gate). self-test 의 discriminating 3-분기(GREEN/RED mutation-kill/anti-theater green≠red) = §8 Test Contract(§결정 §8.10).

### 결정 10 — ADR 번호 claim (ADR-133 OCC atomic)

번호 151 = OCC atomic claim primitive 점유(`adr-reservation-atomic-claim.py --claimant ArchitectPLAgent:CFP-2622:run-20260712T012444Z`, claim-state max_adr_number 150→151 — concurrent CFP-2613 이 148·149, CFP-2612 가 150 선점 후 `Glob max+1` 재계산 금지, claim 반환 151 사용). dual-key 3-leg 정합: filename `ADR-151-selftest-execution-liveness-inventory.md` ∧ frontmatter `adr_number: 151` ∧ ADR-RESERVATION.md registry row. claim(점유 직렬화) ↔ registry append(기록 책무) disjoint(ADR-133 §결정3 / ADR-070 chief author inline append).

## 결과

### 강화 방향 (ratchet↑, 약화 surface 0)

- 신규 required context **0**(branch-protection 6-tuple 무변경) / inter-plugin 계약 **무변경** / 신규 category **0**. ADR-058 §결정5 강화 방향 — `sunset_justification` N/A.
- 신규 산출물(Phase 2): `docs/selftest-execution-liveness-inventory.yaml`(인벤토리 SSOT, 35 레코드) + `scripts/lib/check_selftest_execution_liveness.py` + `scripts/check-selftest-execution-liveness.sh` + `tests/scripts/test_check-selftest-execution-liveness.sh`(재귀 L3) + `.github/workflows/selftest-execution-liveness-test.yml`(메타-게이트 + bucket A 3 self-test 배선, wrapper-self-only non-required).
- Phase 1(본 ADR + Change Plan) = narrative only. 실 `.sh`/`.py`/`.yaml`/`.yml` write = **Phase 2 구현 lane deliverable**(ADR-136 결정14 부록 Phase-1 no-`.sh`-write 상속 — 설계리뷰가 "메타-게이트 미구현"을 P0 로 올리면 Phase 2 deliverable 로 기각).

### 경계 (disjoint 축 — 재유입 봉인)

- **⊥ G3(검출력 실증)**: self-test fixture 가 실제로 mutation 을 죽이는가(켠 채 잡는가) = G3 소관. G6 = 형식 presence 까지.
- **⊥ ADR-147(러너 인프라)**: 배선된 job 이 실 러너를 배정받아 실행되는가 = ADR-147. G6 = "workflow 가 self-test 를 배선했는가" 축.
- **⊥ consumer 동적(G2 soak / G5 DAST / G4 burden-flip)**: 형제 arc 소관. G6 = wrapper-self self-test 실행-liveness.
- **⊥ mctrader remediation / deploy-review 부활**: §1 불변.

### Living Architecture 영향

`architecture_doc_impact` = **governance CI 층 추가**(self-test execution-liveness 강제 채널). 상세 = Change Plan §10.A.
