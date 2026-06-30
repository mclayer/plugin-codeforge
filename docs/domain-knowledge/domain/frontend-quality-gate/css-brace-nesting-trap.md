---
kind: domain_fact
title: CSS 미닫힌 brace 오중첩 함정 — lenient 빌더 에러0 빌드 성공 → 빌드 신호 미발현 + createPortal static 추락(조건부 발현)
area: frontend-quality-gate
topic_slug: css-brace-nesting-trap
status: active
sources:
  - "ADR-136 컨텍스트 WEB-033 + 'static 추락 = 조건부 발현' 보정 (archive/adr/ADR-136-frontend-quality-gate-standard.md) — 요구사항리뷰 F2"
  - "CFP-2505 §2 도메인 해석 CSS nesting 함정 (internal-docs wrapper/stories/CFP-2505.md)"
  - "CFP-2505 §6 외부사실 검증 — 미닫힌 brace = stylelint CssSyntaxError(rule 평가 이전 단계) [source: stylelint.io/user-guide/errors/]"
related_adrs:
  - ADR-136   # frontend 품질게이트 표준 — D1 이 차단하는 '원인' fact. 본 trap 의 carrier
  - ADR-127   # overlay 확장-only/축소불가 invariant — D1 floor 가 brace invariant 를 축소불가로 강제
related_stories:
  - CFP-2505   # ADR-136 carrier
  - CFP-2512   # 본 domain-knowledge 문서 착륙
updated: 2026-06-30
---

# Frontend-quality-gate · CSS 미닫힌 brace 오중첩 함정

## 정의

**CSS brace nesting 함정** = CSS 소스에 미닫힌 `{` 가 하나 들어가면, 그 뒤 전체 CSS 가 앞 셀렉터의 **자손으로 오중첩**되어 의도와 다른 스코프에 묶이는 구조적 결함이다. 더 위험한 점은 — **lenient 빌더(lightningcss 등)가 brace 를 보정해 에러 0 으로 빌드를 성공**시켜, 이 결함이 빌드 신호로 전혀 드러나지 않는다는 것이다.

발현 사슬(WEB-033, [consumer 측 실측 — 본 lane 미독립검증]):

1. `styles.css` 의 미닫힌 `{` 2개(`.terminal-controls .tt-live` + `@media`)로 그 뒤 전체 CSS(거래내역 모달 포함)가 해당 셀렉터의 자손으로 오중첩.
2. lightningcss lenient 빌더가 brace 를 보정 → **에러 0 으로 빌드 성공**(빌드 신호 미발현).
3. 거래내역 모달은 `createPortal(document.body)` 로 그 오중첩 스코프 *밖*에 렌더 → `position:fixed` 미적용 → `position:static` 으로 페이지 하단 인라인 추락("모달이 아니라 아래로 나열").

## 컨텍스트

이 trap 은 D1(구조적 CSS lint)이 차단하는 **"원인" 층위**의 fact 다([ground-truth-layer-model](./ground-truth-layer-model.md) R-2). 핵심은 빌드 통과가 정상을 보증하지 않는다는 것 — lenient 보정은 빌더의 **기능(편의)**이라 끌 수 없고, 따라서 구조 보증은 빌드와 독립된 별도 lint 채널(D1)로만 가능하다.

> **"static 추락" = 조건부 발현** (consumer 측 실측, ADR-136 요구사항리뷰 F2 보정): `createPortal → position:fixed 미적용 → static` 은 무조건 발현이 아니다 — `position:fixed` 규칙이 React-부모 전용 scope / CSS-module selector 에 의존해, portal 로 DOM 부모가 바뀐 조건에서만 풀리는 **조건부 발현**이었다(규칙이 전역 selector 였다면 portal 후에도 fixed 유지). 결론(D1+D2 양층 차단 필요)은 불변 — render-truth 게이트가 필요한 이유는 이 발현이 *조건부*라 정적 검출로는 예측 불가하기 때문이다.

## 핵심 규칙 / 불변식 (invariant)

### R-1: 미닫힌 `{` → 후속 전체 자손 오중첩 (구조 결함 전파)

- CSS 파서는 미닫힌 `{` 를 만나면 후속 규칙을 그 블록 내부로 해석한다 → 미닫힌 지점 이후 전체가 앞 셀렉터의 자손으로 오중첩된다. 결함이 한 줄에 국소화되지 않고 **후속 전체로 전파**된다.
- **함의**: 단일 오타(`}` 누락)가 파일 뒷부분 전체의 스코프를 바꾼다 — 거리상 멀리 떨어진 규칙(거래내역 모달 CSS)이 영향받는다. 육안 적발이 비현실적인 이유.

### R-2: lenient 빌더가 brace 보정 → 에러 0 빌드 성공 = 빌드 신호 미발현 (핵심 함정)

- lightningcss 등 lenient 빌더는 미닫힌 brace 를 보정해 빌드를 **에러 0 으로 성공**시킨다. 이는 빌더의 의도된 편의 기능이라 끌 수 없다.
- **함의**: "빌드 통과 ≠ 정상". 빌드 성공이 구조 정합을 보증하지 않으므로, 구조 보증은 빌드 파이프라인 안이 아니라 **빌드 독립 별도 lint 채널**(D1)로만 얻는다. lenient 보정은 리뷰어 도달 위험신호도 0 으로 만든다(정적 2-peer 리뷰 ③도 신호 없음).

### R-3: D1 의 1급 방어 = parser-level invariant (rule 무관) [ADR-136 결정4-A 정합]

- 미닫힌 brace 는 stylelint 의 **CSS parser syntax error(CssSyntaxError)** 다 — rule 평가 *이전* 단계라 어떤 rule 을 켜고 끄는지와 무관하다(CFP-2505 §6 검증완 [source: stylelint.io/user-guide/errors/]).
- stylelint CLI 가 syntax error 시 **non-zero exit** → CI 차단. 이것이 brace 결함의 1급 방어이며, rule 목록으로 정의할 수 없는 invariant 다.
- **함의**: D1 의 floor 는 rule 집합만이 아니라 "stylelint non-zero exit = CI fail"이라는 parser-level invariant 를 포함한다. consumer overlay 가 rule 을 disable 해도 이 invariant 는 영향받지 않는다(ADR-127 축소불가 동형 — config 차원 약화와 무관한 파서 단계).

### R-4: createPortal static 추락은 조건부 발현 — 정적 검출로 예측 불가

- portal 로 DOM 부모가 바뀌면, `position:fixed` 규칙이 (React-부모 전용 scope / CSS-module selector 같은) **부모 의존 selector** 일 때만 규칙이 풀려 static 으로 추락한다. 전역 selector 였다면 portal 후에도 fixed 유지된다 — 즉 **조건부 발현**.
- **함의**: 같은 brace 결함이라도 발현 여부가 selector scope·portal 사용 조건에 의존한다 → 정적 분석으로 "이 brace 가 static 추락을 일으킨다"를 예측 불가. 따라서 D1(원인 차단)만으로 불충분하고, 실 렌더 결과를 보는 D2(증상 포착)가 상보로 필요하다.

## 경계 / 예외

- **In scope**: 미닫힌 brace 의 후속 오중첩 전파(R-1), lenient 빌드 통과로 인한 신호 미발현(R-2), D1 의 parser-level invariant 1급 방어(R-3), createPortal static 추락의 조건부 발현성(R-4).
- **Out of scope**:
  - D1 게이트의 *구현*(css-lint.yml job-level `if:` / effective-config self-check / warning-tier 승격) — ADR-136 결정3/5/6 + Phase 2 구현 lane.
  - brace 외 CSS 결함(z-index/specificity/미디어쿼리 등 구조 정상인데 깨지는 케이스) — D1 단독으로 못 잡는 영역, D2 보완 대상([ground-truth-layer-model](./ground-truth-layer-model.md) R-2).
  - styled-components/CSS-in-JS 의 customSyntax 처리(`postcss-styled-syntax`) — ADR-136 결정4 커버리지 계층화, overlay 확장 슬롯.
- **Anti-pattern**:
  - 빌드 성공을 "CSS 구조 정상"으로 단정(R-2 — lenient 보정이 결함을 가린다).
  - brace 검출을 특정 rule on/off 에 의존(R-3 — syntax error 는 rule 이전 단계, parser-level invariant).
  - "static 추락은 createPortal 쓰면 항상 발생"으로 일반화(R-4 — selector scope 의존 조건부 발현, 무조건 아님).
  - 미닫힌 brace 를 D1(원인)만으로 충분히 막았다고 간주(R-4 — 조건부 발현은 정적 예측 불가, D2 상보 필요).

## 관련 ADR / Story / 코드

- [ADR-136](../../../../archive/adr/ADR-136-frontend-quality-gate-standard.md) — frontend 품질게이트 표준. 컨텍스트 WEB-033 + "static 추락 = 조건부 발현"(요구사항리뷰 F2 보정) + 결정4(D1 floor = parser-level invariant ∪ rule-level floor)가 본 trap 의 carrier.
- [ADR-127](../../../../archive/adr/ADR-127-mandatory-full-flow-no-exemption.md) — overlay 확장-only/축소불가 invariant. D1 floor 가 brace parser-level invariant 를 config 차원 약화와 무관하게 강제(동형 적용).
- Story CFP-2505 (internal-docs `wrapper/stories/CFP-2505.md`) — ADR-136 carrier. §2 CSS nesting 함정 + §6 외부사실 검증.
- 외부사실 (CFP-2505 §6 검증완 — 본 lane 신뢰도 상향 0): 미닫힌 brace = stylelint CssSyntaxError(rule 평가 이전 단계, rule 무관) → CLI non-zero exit → CI 차단 [source: stylelint.io/user-guide/errors/ , /usage/cli/].
- WEB-033 발현 사슬 수치(static rectTop=2676 → fixed rectTop=0)는 `[verification-out-of-scope: consumer 측 실측]` — 상세 = [render-truth-headless-browser](./render-truth-headless-browser.md).

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2512 DeveloperAgent, ADR-136 §7.9 capture 후보 회수). CSS 미닫힌 brace 오중첩 + lenient 빌드 통과 + createPortal 조건부 static 추락 fact 신설. ADR-136 컨텍스트 WEB-033 + F2 조건부 발현 보정 + 결정4 + CFP-2505 §2 도메인 해석 전사·정제(재발명 0). 외부사실(stylelint CssSyntaxError = rule 이전 단계)은 CFP-2505 §6 검증완 인용 — 새 단정·신뢰도 상향 0. WEB-033 수치는 consumer 실측 한정 표기 보존. R-1(후속 전체 오중첩 전파) / R-2(lenient 에러0 빌드 = 신호 미발현) / R-3(parser-level invariant 1급 방어, rule 무관) / R-4(createPortal static 추락 = 조건부 발현, 정적 예측 불가).
