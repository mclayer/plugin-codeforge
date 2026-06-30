---
kind: domain_fact
title: jsdom layout-blindness — 레이아웃 엔진 부재로 렌더 위치·가시성·position 구조적 미계산, 우회 불가
area: frontend-quality-gate
topic_slug: jsdom-layout-blindness
status: active
sources:
  - "ADR-136 컨텍스트 3중 게이트 표 ② + 결정10 §8.7.1 (archive/adr/ADR-136-frontend-quality-gate-standard.md) — jsdom 계열 = D2 부적격, layout 미계산"
  - "CFP-2505 §2 도메인 해석 (internal-docs wrapper/stories/CFP-2505.md) — jsdom layout-blindness 정의 + 우회 불가 경계"
  - "CFP-2505 §6 외부사실 검증 (요구사항리뷰 lane PASS) — jsdom README 'Unimplemented parts: Layout' [source: github.com/jsdom/jsdom README + issue #653]"
related_adrs:
  - ADR-136   # frontend 품질게이트 표준 — §8.7.1 jsdom 부적격 명시. 본 fact 의 carrier
  - ADR-015   # §8.5 stateful CONDITIONAL — §8.7 이 동형 차용한 applicability 형식 (도구 독립성 맥락)
related_stories:
  - CFP-2505   # ADR-136 carrier
  - CFP-2512   # 본 domain-knowledge 문서 착륙
updated: 2026-06-30
---

# Frontend-quality-gate · jsdom layout-blindness

## 정의

**jsdom layout-blindness** = jsdom 이 DOM 트리만 구성하고 **레이아웃(layout) 엔진을 구현하지 않아**, 요소의 렌더 위치·가시성·`position` 적용 결과를 *구조적으로* 계산하지 못하는 본질적 한계다.

- jsdom 은 HTML 파싱 → DOM 노드 트리 구성 → CSSOM 일부까지 수행하지만, **레이아웃(박스 모델 계산, reflow, 좌표 산출)은 미구현**이다. 공식 README 가 "Unimplemented parts: Layout" 로 명시한다 ([§외부사실](#관련-adr--story--코드), CFP-2505 §6 검증완).
- 따라서 `getBoundingClientRect()` / `offsetTop` / `offsetWidth` 등 layout-derived 속성은 **0 (또는 기본값)을 반환**한다 — 실제 렌더 좌표가 아니다. `getComputedStyle()` 도 cascade 결과 문자열은 줄 수 있으나 layout 결과(실 좌표·가시성·`position:fixed` 의 실제 배치 효과)는 계산하지 않는다.

핵심: jsdom 으로는 **"요소가 DOM 에 존재하는가"는 검증 가능**하지만 **"요소가 화면 어디에 어떻게 렌더되는가"는 구조적으로 불가**하다. 이 둘은 서로 다른 ground-truth 층위다([ground-truth-layer-model](./ground-truth-layer-model.md) R-1).

## 컨텍스트

mctrader-web WEB-033(escalation #2502, [consumer 측 실측 — 본 lane 미독립검증])에서 거래내역 모달의 jsdom 단위테스트는 **모달 DOM 존재를 확인하고 PASS** 했다. 그러나 그 모달은 `createPortal` 오중첩 스코프 밖에서 `position:fixed` 를 못 받아 `position:static` 으로 페이지 하단에 추락했고 — jsdom 은 레이아웃 엔진이 없어 그 추락(좌표·position 적용 결과)을 **계산조차 하지 않았다**. "DOM 존재"는 PASS 인데 "렌더 위치 깨짐"은 관측 밖이라 게이트가 통과한 것이다.

이 fact 는 D2(UI 실렌더 검증)가 *왜 jsdom 강화가 아니라 별도 실 브라우저 검증의 추가*여야 하는지의 도메인 근거다. jsdom 한계는 사용법 미숙이 아니라 **도구 본질**이라 우회할 수 없다 — 레이아웃 엔진을 켜는 옵션이 없다.

## 핵심 규칙 / 불변식 (invariant)

### R-1: jsdom 은 레이아웃을 계산하지 않는다 — layout 속성 0 반환 (도메인 핵심)

- jsdom 공식 README "Unimplemented parts: Layout"(CFP-2505 §6 검증완). 박스 모델·reflow·좌표 산출 미구현.
- `getBoundingClientRect()` / `offsetTop` / `offsetHeight` / `clientWidth` 등 layout-derived 속성은 **0 또는 기본값** 반환 — 실 렌더 좌표 아님.
- **함의**: jsdom 단위테스트의 "위치 단언"은 ground-truth 가 아니다. layout 결과에 의존하는 검증은 jsdom 으로 작성하면 항상 통과(0 비교)하거나 의미 없는 비교가 된다.

### R-2: "DOM 존재" 검증 가능 ↔ "렌더 위치/가시성" 검증 구조적 불가

- 가능: `screen.getByRole(...)` / `toBeInTheDocument()` 류 DOM 노드 존재·구조·접근성 트리 검증.
- 불가: `position:fixed` 의 실제 배치 효과, 요소가 viewport 안에 보이는지(가시성), `createPortal` 로 DOM 부모가 바뀐 뒤의 레이아웃 결과 — 전부 레이아웃 엔진 산출물이라 jsdom 관측 밖.
- **함의**: WEB-033 류 회귀(`position:static` 추락)는 jsdom 으로 **구조적으로 검출 불가**. 단위테스트 PASS 가 "렌더 정상"을 보증하지 않는다(jsdom 통과 ≠ 승인).

### R-3: 한계는 도구 본질 — "jsdom 정교화"로 우회 불가, 실 브라우저만 ground-truth

- jsdom 의 레이아웃 미계산은 옵션·설정으로 끌 수 없는 **아키텍처 한계**다(레이아웃 엔진 자체가 없음).
- 따라서 CSS 렌더버그를 잡으려면 jsdom 을 더 정교하게 쓰는 게 아니라 **레이아웃 엔진을 가진 실 브라우저**(headless Chromium 등)로 검증을 *추가* 해야 한다 — 이것이 D2 가 jsdom 강화가 아니라 별도 게이트인 이유.
- **함의**: 설계 lane 은 §8.7(D2)에서 jsdom 계열(testing-library + jsdom)을 **render-truth 도구로 부적격** 처리해야 한다(ADR-136 결정10 §8.7.1). 실 layout 엔진(Playwright 권장)으로만 outcome 검증.

## 경계 / 예외

- **In scope**: jsdom 의 레이아웃 미계산 본질(R-1), "DOM 존재"와 "렌더 위치"의 검증 가능성 비대칭(R-2), 한계의 우회 불가성·실 브라우저 필요(R-3).
- **Out of scope**:
  - jsdom 의 *정당한* 용도(DOM 구조·이벤트·접근성 트리 단위테스트) — jsdom 은 그 층위에서 유효하다. 본 fact 는 "layout 층위 부적격"만 단언, jsdom 전면 부정 아님.
  - 실 브라우저 검증의 *구현*(Playwright 단언·screenshot baseline) — [render-truth-headless-browser](./render-truth-headless-browser.md) 보유.
  - 다른 DOM 시뮬레이터(happy-dom 등)의 layout 지원 여부 — 본 fact 는 jsdom 한정(CFP-2505 §6 검증 범위).
- **Anti-pattern**:
  - jsdom 단위테스트 PASS 를 "렌더 정상"으로 단정(R-2 — DOM 존재 ≠ 렌더 위치).
  - layout 결과(좌표·position·가시성)에 의존하는 단언을 jsdom 으로 작성(R-1 — 0 비교, 의미 없음).
  - "jsdom 을 더 잘 설정하면 layout 도 잡힌다"는 가정(R-3 — 도구 본질, 우회 불가).

## 관련 ADR / Story / 코드

- [ADR-136](../../../../archive/adr/ADR-136-frontend-quality-gate-standard.md) — frontend 품질게이트 표준. 컨텍스트 3중 게이트 표 ②(jsdom layout 미계산) + 결정10 §8.7.1(jsdom 계열 D2 부적격 명시)이 본 fact 의 carrier.
- [ADR-015](../../../../archive/adr/ADR-015-stateful-test-category.md) — §8.5 stateful CONDITIONAL applicability 형식. §8.7(D2)이 도구 독립성 맥락에서 동형 차용.
- Story CFP-2505 (internal-docs `wrapper/stories/CFP-2505.md`) — ADR-136 carrier. §2 도메인 해석 + §6 외부사실 검증.
- 외부사실 (CFP-2505 §6 검증완 — 본 lane 신뢰도 상향 0): jsdom 공식 README "Unimplemented parts: Layout" → `getBoundingClientRect`/`offsetTop` 등 layout 속성 0 반환 [source: github.com/jsdom/jsdom README + issue #653]. `[verification-out-of-scope: 본 lane 직접 재현 아님 — CFP-2505 요구사항리뷰 lane 검증 인계]`.

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2512 DeveloperAgent, ADR-136 §7.9 capture 후보 회수). jsdom 레이아웃 미계산·우회 불가 fact 신설. ADR-136 컨텍스트 3중 게이트 표 ② + 결정10 §8.7.1 + CFP-2505 §2 도메인 해석 전사·정제(재발명 0). 외부사실(jsdom README "Unimplemented parts: Layout")은 CFP-2505 §6 검증완 인용 — 새 단정·신뢰도 상향 0. R-1(layout 속성 0 반환) / R-2(DOM 존재 가능 ↔ 렌더 위치 구조적 불가) / R-3(도구 본질, 실 브라우저만 ground-truth).
