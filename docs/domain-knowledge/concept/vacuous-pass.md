---
kind: concept_definition
slug: vacuous-pass
title: Vacuous PASS (공허한 통과) — 검사 대상 0건으로 인한 게이트 무력화
first_defined_by: CFP-2661
related: [ADR-119, ADR-136, ADR-145]
---

# Vacuous PASS (공허한 통과)

## 한 줄 정의

**게이트가 "위반 0건" 으로 PASS 했지만, 그 PASS 가 "위반이 없어서" 가 아니라 "검사 대상 자체가 0건이어서" 발생한 상태.**
논리학의 **vacuous truth** (공허한 참) 가 품질 게이트에서 실패 모드로 발현한 것.

## 논리적 뿌리 — vacuous truth

> "A vacuous truth is a conditional or universal statement that is true because the antecedent cannot be satisfied."
> — [Wikipedia, Vacuous truth](https://en.wikipedia.org/wiki/Vacuous_truth)

전칭명제 `∀x ∈ A: Q(x)` 는 `A = ∅` 일 때 **자동으로 참**이다.
게이트의 명제는 거의 항상 전칭형이다 — "스캔 대상 파일 **모두**가 규칙 R 을 만족한다."
따라서 스캔 대상 집합이 비면 게이트는 **아무것도 검사하지 않고 참을 반환**한다.

같은 문서가 지적하는 실무 위험이 정확히 게이트의 위험이다:

> "Outside of mathematics, statements in the form of a vacuous truth, while logically valid, can nevertheless be misleading. Such statements make reasonable assertions about qualified objects which do not actually exist."
> (예: 접시에 채소가 없었는데 아이가 "접시의 채소를 전부 먹었어" 라고 말하는 경우 — 참이지만 부모를 오도한다.)

**게이트의 초록불은 "검사했고 깨끗하다" 로 읽힌다. vacuous PASS 는 이 읽기를 배신한다.**

## codeforge 에서의 발현 형태 (3종)

| 형태 | 메커니즘 | 증상 |
|---|---|---|
| **dead-path silent skip** | 스크립트가 존재하지 않는 경로를 스캔 대상으로 지목 → `[ ! -e "$p" ] && continue` 로 조용히 건너뜀 | 종료코드 0, 로그 무음, 실제 검사 0건 |
| **empty allowlist / scope 손실** | allowlist·권한 경로가 구경로를 가리켜 실제 대상이 매칭 0 | 규칙은 살아 있으나 적용 표면이 0 |
| **skipped-but-required** | GHA workflow 가 `paths:` 미매칭으로 skip → required check 가 `Pending` 고착 | PASS 아님(merge 차단)이지만 **동일 뿌리**(대상 0건)의 쌍둥이 실패 모드 |

세 번째는 vacuous PASS 가 아니라 **vacuous PENDING** 이다. 뿌리는 같고 결과 방향만 반대다 (fail-open vs fail-stuck).

## 업계 관행 — "대상 0건 = 기본 실패" 는 실재한다

vacuous PASS 를 거부하는 것은 codeforge 고유 발명이 아니다. 주요 도구가 이미 채택:

| 도구 | 대상 0건 시 동작 | 출처 |
|---|---|---|
| **pytest** | **exit 5** = "No tests were collected" (0 아님) | [pytest exit codes](https://docs.pytest.org/en/stable/reference/exit-codes.html) |
| **golangci-lint** | **exit 5** = `NoGoFiles` ("no go files to analyze") | [exitcodes pkg](https://pkg.go.dev/github.com/golangci/golangci-lint/pkg/exitcodes) |
| **Jest** | 기본 **exit 1** ("No tests found, exiting with code 1"). 통과시키려면 `--passWithNoTests` **명시적 opt-in** | [jest#8594](https://github.com/jestjs/jest/issues/8594) |
| **ESLint** | 패턴 미매칭 시 **fatal error** (v5 breaking change). 무시하려면 `--no-error-on-unmatched-pattern` **명시적 opt-in** | [eslint#10587](https://github.com/eslint/eslint/issues/10587) |
| **ruff** | `warning: No Python files found under the given path(s)` — 최소 **경고**는 낸다 | [ruff#6335](https://github.com/astral-sh/ruff/issues/6335) |

**추출되는 설계 규범 2개:**
1. **empty target = 기본 실패 또는 최소 경고.** 침묵 통과는 어느 주요 도구도 채택하지 않는다.
2. **관용은 opt-in 이어야 한다.** `--passWithNoTests` / `--no-error-on-unmatched-pattern` 처럼 *명시적으로 선언*해야 허용되며, 선언이 기록으로 남는다. 기본값이 관용이면 안 된다.

pytest 와 golangci-lint 가 **독립적으로 같은 exit code 5** 를 "대상 없음" 에 배정한 것은 이 규범의 수렴적 진화 증거다.

## 인접 개념 — mutation testing 의 positive control

mutation testing 은 "테스트가 실제로 무언가를 검출하는가" 를 묻는다 — 코드에 결함을 주입하고 테스트가 죽는지 본다.

> "You can have 100% coverage with tests that assert nothing."
> — [Symflower, mutation testing](https://symflower.com/en/company/blog/2023/using-mutation-testing/)

vacuous PASS 는 이것의 **한 단계 앞** 문제다. mutation testing 은 "테스트가 있으나 무력한" 경우를 잡고, vacuous PASS 는 "테스트가 애초에 실행되지 않은" 경우다.
따라서 **positive control (일부러 위반을 심고 게이트가 붉어지는지 확인)** 이 vacuous PASS 의 유일한 신뢰 가능한 반증 수단이다 — 게이트의 초록불만으로는 두 상태를 구별할 수 없다.

이는 codeforge 의 기존 원칙과 정확히 일치한다:
- **ADR-119 (research-before-claims)** — "게이트 verdict PASS = internal proxy 아닌 outcome ground-truth 로만 단정"
- **CFP-2545** — `presence-grep = false oracle` → execution-backed 검증으로 전환
- **CFP-2635** — masking 방지 게이트 자신이 over-claim → 실행 반증으로 포착

## 반증 가능성 기준 (discriminating test)

게이트가 vacuous 하지 않음을 증명하려면 **음성 대조군만으로는 불충분**하다:

- ❌ "깨끗한 repo 에서 게이트가 PASS 한다" → vacuous PASS 와 구별 불가
- ✅ "위반을 심으면 게이트가 FAIL 한다" (positive control) → 게이트가 실제로 대상을 보고 있음을 증명
- ✅ "대상 집합 크기를 로그로 방출한다" (`scanned N files`) → 0 이면 즉시 가시화

**최소 요건: 게이트는 자신이 검사한 대상 수를 보고해야 한다.** 보고하지 않는 게이트는 vacuous 여부를 외부에서 판정할 수 없다.

## 정적 분석 도구의 사각지대 (왜 커스텀 lint 가 필요한가)

죽은 경로 참조를 잡는 기성 도구는 **거의 없다**:

- **shellcheck** — 순수 정적 분석. 하드코딩된 경로가 실재하는지 파일시스템 확인 **안 함** (런타임 값 추적 불가가 설계상 한계). [SC1091](https://www.shellcheck.net/wiki/SC1091)
- **actionlint** — `paths:` / `paths-ignore:` 글롭의 **문법만** 검사. 파일시스템 매칭 검사 **안 함**. 파일 존재 확인은 로컬 재사용 워크플로(`uses: ./...`) 한정. [actionlint checks](https://github.com/rhysd/actionlint/blob/main/docs/checks.md)
- **action-validator** (예외) — "it makes sure that any globs used in `paths` / `paths-ignore` match at least one file in the repo". 유일하게 이 검사를 하는 도구. [mpalmer/action-validator](https://github.com/mpalmer/action-validator)

**결론: 셸 스크립트 안의 죽은 경로 참조를 잡는 기성 도구는 부재.** 커스텀 lint 신설이 정당하다. 단 action-validator 의 선례는 "글롭이 최소 1건 매칭하는지 확인" 이라는 **검사 형태 자체가 업계에 실재**함을 보여준다 — codeforge 의 발명이 아니라 채택.

## 기본 규범 (본 개념이 요구하는 것)

1. 게이트는 스캔 대상 수를 **방출**한다.
2. 대상 0건은 **FAIL 또는 최소 경고** — 침묵 PASS 금지.
3. 0건 관용은 **명시적 opt-in 선언**으로만 (기록 가능한 형태).
4. 게이트의 자기 테스트는 **positive control 을 포함**한다 (음성 대조군 단독 불가).
5. required status check 로 등록되는 workflow 는 `paths:` 필터에 **의존하지 않는다** (skipped→Pending 고착).
