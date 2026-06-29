---
kind: concept_definition
type: domain-knowledge
slug: fix-ground-truth-replay
title: FIX ground-truth replay ("수정됨" = 원 repro 재실행 GREEN(외부 Retest)으로만 닫는 패턴 + false-close 차단)
status: Active
updated: 2026-06-30
carrier_story: CFP-2480
related_adrs:
  - ADR-119  # research-before-claims — "수정됨=반증 후 단언" + §결정 10② runtime 실패 진단 acted-on 전 falsification (FIX replay 직접 근거, close-time wire)
  - ADR-067  # fix-ledger implementability escalation — max-FIX 3/3 카운터. replay FAIL ↔ 카운터 disjoint (Amendment 3)
  - ADR-070  # Codex verify-before-trust — replay 결과도 신호원 → PL 재실행 falsify 후 close. FIX-close 시점 적용 (Amendment 12)
  - ADR-077  # clarification 강제 재조사 — fact-check marker 무검증 승격 금지 (replay 주장 = hypothesis default)
related_concepts:
  - execution-based-review-verification        # E1 (CFP-2477) — ground-truth falsification(Popper)·flaky quarantine·신호원 SSOT. FIX replay = 그 FIX-close 시점 적용
  - mutation-based-hollow-gate-detection       # Story B (CFP-2464) — undetermined 3-상태 disposition + flaky 결정론 전제 재사용
  - merge-time-adversarial-verification-gate   # Story A (CFP-2458) — provenance 동반(INV-G4) 동형
tags:
  - fix-ground-truth-replay
  - retest
  - reproduce-before-fix
  - non-deterministic-false-close
  - flaky-quarantine
  - signal-source-separation
  - reproducer-record
  - replay-before-close
sources:
  - https://www.guru99.com/re-testing-vs-regression-testing.html                  # Retest(재검증) — 실패했던 바로 그 테스트/명령을 수정 코드에 재실행해 fix 확인. "Re-testing is carried out to confirm the test cases that failed in the final execution are passing after the defects are fixed"
  - https://www.browserstack.com/guide/retesting-vs-regression-testing            # Retest ≠ Regression — "Retesting answers 'is the bug fixed?' while regression testing answers 'did anything else break?'"
  - https://git-scm.com/docs/git-bisect                                           # reproduce-before-fix — bisect/repro 신뢰도는 결정론적 reproduction 존재에 비례
  - https://hauntsaninja.github.io/git_bayesect.html                              # Git Bayesect — Beta-Bernoulli conjugacy posterior + expected-entropy-minimisation commit selection (비결정 실패 재현 = 다회 관측 + Bayesian entropy minimization, mixed→불확정 보류)
---

## 정의

**FIX ground-truth replay** = FIX 루프에서 "수정됨" 으로 닫을 때, 원래 그 finding 을 정당화한 실패 명령/쿼리(reproducer)를 Codex 가 재실행해 *이제 통과*(반증)함을 확인해야만 §10 FIX Ledger 가 닫히는 close 조건. "주장(claim)" 이 아닌 "실측(measurement)" — DeveloperPL 의 "고쳤다" self-claim 은 verdict 입력이 아니고, 원 reproducer 의 GREEN 재현이 verdict source 다.

이는 산업 **Retest(재검증)** — 실패했던 *바로 그 테스트/명령* 을 수정 코드에 재실행해 fix 를 확인하는 행위 ("Re-testing is carried out to confirm the test cases that failed in the final execution are passing after the defects are fixed", 출처: guru99.com/re-testing-vs-regression-testing.html) — 의 codeforge FIX-loop instantiation 이다. Retest 는 Regression(회귀: fix 가 다른 곳을 깼는가)과 구분된다 — "Retesting answers 'is the bug fixed?' while regression testing answers 'did anything else break?'" (출처: browserstack.com/guide/retesting-vs-regression-testing).

## 컨텍스트

CFP-2480 (Epic CFP-2476 의 E3) 동인 = ADR-119 "수정됨=반증 후 단언" 의 mechanical wire 부재. ADR-119 §결정 10② 는 "runtime 실패 진단은 acted-on(수정 착수) 전 falsification 통과 의무 + 비대칭 규칙(file:line 1개 > '확인함 OK' N개)" 를 선언했으나 Phase 1 declarative(child wire 위임)였다 — FIX-close 시점의 mechanical wire 가 공백. 본 개념이 그 close-time carrier 다.

### E1 specialization 으로서의 위치 (핵심 구분)

본 개념은 **E1 `execution-based-review-verification`(ground-truth falsification 일반)의 FIX-close 시점 적용** 이다 (E3 의 다른 specialization = `policy-pack-executable-governance`). E1 이 finding *발화* 시 verify-before-trust 라면, E3 replay 는 finding *닫기* 시 replay-before-close 다 — 같은 Popper 비대칭의 다른 시점:

| 개념 | 시점 | 비대칭 적용 |
|---|---|---|
| E1 execution-based-review-verification | finding **발화** 시 | 실행이 단정을 falsify (verify-before-trust) |
| **E3 fix-ground-truth-replay (본 개념)** | finding **닫기** 시 | 원 reproducer 재실행이 fix 를 반증 (replay-before-close) |

**중복 정립 금지** — Popper 비대칭(falsify only), discriminating check, flaky quarantine+deterministic seeding, read-only sandbox, Codex=신호원은 모두 E1 concept(`execution-based-review-verification.md` X-1~X-6) SSOT 이고 본 개념은 참조만 한다.

## 핵심 규칙 (외부 개념 → invariant 매핑)

### F-1: close 조건 = Retest (원 reproducer 가 이제 GREEN)

FIX "수정됨" close 의 충족 조건 = 외부 **Retest** — finding 을 정당화한 *원 reproducer* 가 수정 코드(fix 포함 worktree HEAD)에서 GREEN (출처: guru99.com/re-testing-vs-regression-testing.html). 주장만으로 닫기 불가. 원 reproducer 가 여전히 RED 면 close 거부 — 수정이 실제로 안 된 것이므로 닫기 거부가 정답(degrade 없음, 본 개념의 fail-mode (A)축).

**함의**: replay verdict 는 {원래 실패 명령, base SHA, 현재 재실행 verdict, 반증 여부} 대조 구조 + provenance 동반(artifact 없이 close 경로 0 — Story A INV-G4 동형). replay 기준 = "원 finding SHA 의 자식(fix 포함) worktree HEAD 에서 원 reproducer 재실행" = retest (과거 시간여행 아님 — base SHA pin 은 명령·입력 결정론 고정용).

### F-2: reproduce-before-fix (reproducer 를 finding 생성 시점에 기록)

replay 의 전제 = finding 마다 **결정론적 reproducer 가 처음부터 존재·기록** 되어야 한다 — bisect/repro 신뢰도는 결정론적 reproduction 존재에 비례한다 (출처: git-scm.com/docs/git-bisect). codeforge §10 FIX Ledger 의 `트리거` column 은 "실패 원문 요약(free string)" 이지 재실행 가능 명령이 아니다 → 구조적 공백. 해소 = fix-event-v1 v1.4 `reproducer_command` optional column (finding 생성 시점 저장, base SHA 동반).

**함의 — 재현 가능성 비대칭**: 게이트/테스트 출처 finding 은 reproducer 환원 가능(replay 자연), 코드 P1 품질·의미 판정 finding 은 실행 가능 명령으로 환원 불가. 환원 불가 finding 은 별도 disposition `replay-impossible`(사유 명시, silent 면제 금지).

### F-3: non-deterministic false-close 차단 (다회 결정론 확인, flaky=quarantine)

replay 는 **다회 결정론 확인 후** close — 1회 GREEN close 금지. 비결정 실패 재현은 다회 관측 + Bayesian entropy minimization(Beta-Bernoulli conjugacy posterior + expected-entropy-minimisation)으로 추론하며 mixed 결과는 불확정 보류한다 (출처: hauntsaninja.github.io/git_bayesect.html). false-close 위험은 양방향:

- **false-GREEN**(최위험): 수정 안 했는데 우연히 통과 → 부당 close. §1 "주장 아닌 실측" 목적을 **정면 훼손** — 게이트 자체가 hollow 가 된다.
- **false-RED**: 진짜 고쳤는데 flaky 실패 → 닫지 못해 ADR-067 max-FIX 3/3 부당 소진.

→ flaky repro 는 close 신호가 아니라 quarantine(E1 X-3 / ADR-070 §결정 D9(b) undetermined 상속). mixed → `undetermined` disposition 보류.

### F-4: 신호원 분리 — replay 결과조차 PL 재현 falsify 후 채택 (실행자 ≠ 판정자)

Codex 가 replay 를 *실행·보고* 하나, close 판정은 PL/Orchestrator 직접 재현 falsify 후(`[hypothesis]` → `[verified]`). 또한 §10 FIX Ledger 갱신 권한 = Orchestrator 단독(fix-event-v1 §1 monopoly) — replay *실행* = Codex worker, replay verdict *기록·close* = Orchestrator (separation of duties, E1 X-5 상속). reproducer 자체도 신뢰 외측 입력 — schema 제약(repo-relative 게이트/테스트 명령만, raw shell free-string 금지) + 발화자 ≠ 기록자.

### F-5: regression 동반 여부 = 설계 결정 (replay 는 원 finding 한정 falsify)

외부상 FIX 검증은 ① Retest(원 실패 재확인) ② Regression(다른 곳 깼는가) 둘이다 (출처: browserstack.com/guide/retesting-vs-regression-testing). 본 개념의 replay 는 **원 finding 한정 Retest** 다 — replay GREEN 은 원 finding 반증이지 전체 회귀 보증이 아니다(Popper — falsify 도구지 verify 아님, E1 X-1). regression 동반(인접 게이트 재실행)을 E3 scope 에 넣을지는 새 touchpoint 금지(Epic 비대상)와의 정합 하에 **설계 결정 항목** 으로 분리(§1 scope 보존).

## 경계

- **In scope**: FIX "수정됨" close 의 ground-truth 조건 정립 — close=Retest(F-1) + reproduce-before-fix(F-2) + non-deterministic false-close 양방향 차단(F-3) + 신호원 분리(F-4) + regression 동반=설계 결정(F-5).
- **Out of scope**:
  - E1 execution-based-review-verification(ground-truth falsification 일반 — finding 발화 시) — 본 개념의 base. Popper/flaky/sandbox/신호원 = E1 SSOT(재정의 금지).
  - `policy-pack-executable-governance`(E3 의 다른 specialization — 리뷰/머지 시 정책 실행) — 별 concept.
  - replay 강제 범위(좁게 vs 넓게), max-FIX 상호작용 최종형, flaky 임계 N 최종값 = 설계 후속(§1, AC-11 — E3 완료 게이트 아님).
  - regression 동반 replay = 설계 결정(F-5, Epic 새 touchpoint 금지 정합 하).
- **Anti-pattern**: 1회 GREEN 으로 close(F-3 false-GREEN = 목적 정면 훼손, 최위험). reproducer 미기록 finding 을 주장만으로 close(F-2 위반). 환원 불가 finding 을 silent 면제(F-2 — replay-impossible 사유 의무). replay 결과 무재현 자동 close(F-4 separation 위반). raw shell free-string reproducer 저장(injection vector — schema 제약 위반). replay GREEN 을 전체 회귀 보증으로 단정(F-5 — replay 는 원 finding 한정 falsify).

## 관련 ADR

- **ADR-119** Amd 2 §결정 10② — "수정됨=반증 후 단언" + runtime 실패 진단 acted-on 전 falsification + 비대칭 규칙(file:line 1개 > 확인 N개). 본 개념 = §결정 10② 의 FIX-close 시점 mechanical wire(close-time carrier).
- **ADR-067** Amendment 3 (CFP-2480) — max-FIX 3/3 카운터. replay FAIL ↔ 카운터 disjoint(replay = 닫기 게이트지 새 FIX iter 아님 — F-3 false-RED / 무한거부 backstop = fix-attempt 카운터).
- **ADR-070** Amendment 12 (CFP-2480) — verify-before-trust 의 FIX-close 시점 적용(E1 Amendment 11 §결정 D9 disposition 일반화). reproducer = `[hypothesis]` → PL falsify → `[verified]` close.
- **ADR-077** I-4 — fact-check marker 무검증 승격 금지. replay 주장 = hypothesis default, 재현 falsify 후 verified close(F-4)의 재사용 anchor.

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2480 E3 ResearcherAgent Mandate 1·2 산출물 + ArchitectAgent chief author). Retest≠Regression(guru99·browserstack) / reproduce-before-fix(git-bisect) / non-deterministic 재현(Git Bayesect Bayesian entropy minimization) cited. E1 `execution-based-review-verification`(ground-truth falsification 일반)의 FIX-close 시점 적용으로 명시 — E1 SSOT 개념 재정의 금지, 참조만. 요구사항리뷰 FIX 반영: retest≠regression 출처 = guru99 + browserstack(dedicated), Bayesect = Bayesian entropy minimization(majority voting 아님).
