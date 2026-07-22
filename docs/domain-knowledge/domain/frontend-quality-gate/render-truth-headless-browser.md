---
kind: domain_fact
title: render-truth = headless browser — CDP/Playwright 실 Chromium computed-style·좌표·스크린샷이 레이아웃 ground-truth
area: frontend-quality-gate
topic_slug: render-truth-headless-browser
status: active
sources:
  - "ADR-136 컨텍스트 WEB-033 CDP 실측 + 결정10 §8.7.1~§8.7.3 (archive/adr/ADR-136-frontend-quality-gate-standard.md) — render-truth 도구·min bar·baseline"
  - "CFP-2505 §2 도메인 해석 실 브라우저 렌더 검증 (internal-docs wrapper/stories/CFP-2505.md)"
  - "CFP-2505 §6 외부사실 검증 — Playwright toHaveScreenshot/toHaveCSS/boundingBox + GHA chromium headless [source: playwright.dev/docs/test-snapshots , /ci]"
related_adrs:
  - ADR-136   # frontend 품질게이트 표준 — D2 render-truth 게이트. 본 fact 의 carrier
  - ADR-006   # §8 Test Contract author = ArchitectAgent(chief), deputy = input contributor — §8.7 author 경계
related_stories:
  - CFP-2505   # ADR-136 carrier
  - CFP-2512   # 본 domain-knowledge 문서 착륙
updated: 2026-06-30
---

# Frontend-quality-gate · render-truth = headless browser

## 정의

**render-truth(렌더 진리)** = 실 브라우저 레이아웃 엔진이 산출하는 computed-style·실 좌표·스크린샷이 frontend 레이아웃 결함의 **ground-truth** 라는 도메인 사실이다. CDP(Chrome DevTools Protocol)/Playwright 로 실 Chromium 을 headless 구동하면, 텍스트(lint)·DOM(jsdom) 층위가 구조적으로 못 보는 "렌더 위치/가시성"을 직접 측정할 수 있다.

- 실 브라우저는 레이아웃 엔진을 가지므로 `position` 적용 결과, 요소의 실 좌표(`boundingBox`), computed-style, 가시성을 **실제로 계산**한다 — jsdom 의 0 반환([jsdom-layout-blindness](./jsdom-layout-blindness.md))과 달리 ground-truth 다.
- 이것이 [ground-truth-layer-model](./ground-truth-layer-model.md)의 최상위 층위(실 레이아웃 좌표)이며, D2(UI 실렌더 검증)가 딛고 서는 토대다.

WEB-033 근본원인 확정은 **CDP 헤드리스 Chrome 실측으로만 가능**했다 — 수정 전 `static rectTop=2676` → 수정 후 `fixed rectTop=0`. `[verification-out-of-scope: consumer 측 실측 — 본 lane 미독립검증]`.

## 컨텍스트

WEB-033(escalation #2502)에서 lint(텍스트)·jsdom(DOM)·정적 리뷰(신호) 3중 게이트가 전부 통과했고, 모달이 화면 어디에 어떻게 렌더되는지를 본 유일한 채널이 실 브라우저 레이아웃 측정이었다. static 추락(rectTop=2676 → 0)은 실 Chromium 좌표로만 관측·확정됐다 — 이것이 D2 가 "실 layout 엔진으로 outcome 검증"을 요구하는 도메인 근거다.

도구 선택은 CFP-2505 요구사항리뷰 lane 에서 검증된 외부사실에 의존한다(아래 인용). raw CDP 는 Playwright 와 동등한 저수준 능력이나 세션/대기/diff 를 직접 구현해야 해 고비용 → Playwright 권장.

## 핵심 규칙 / 불변식 (invariant)

### R-1: 실 브라우저 computed-style·좌표·스크린샷 = 레이아웃 ground-truth (도메인 핵심)

- CDP/Playwright 로 실 Chromium 을 구동하면 레이아웃 엔진이 `position`·좌표·가시성·computed-style 을 실제 계산한다 → 렌더 결과의 ground-truth.
- WEB-033 근본원인도 CDP 실측(static rectTop=2676 → fixed rectTop=0)으로만 확정 — 다른 어떤 층위(텍스트/DOM)로도 이 좌표를 얻을 수 없었다. `[verification-out-of-scope: consumer 측 실측]`.
- **함의**: 레이아웃 회귀(position 추락 등)를 잡으려면 검증의 ground-truth 를 실 브라우저 좌표로 올려야 한다(게이트 추가가 아니라 ground-truth 수준 상승).

### R-2: D2 도구 독립성 — jsdom 계열 부적격, 실 layout 엔진(Playwright 권장) [ADR-136 결정10 §8.7.1]

- UI/CSS 변경의 outcome 검증은 **실 layout 엔진**으로 한다. jsdom 계열(testing-library + jsdom)은 layout 미계산이라 **D2 부적격**([jsdom-layout-blindness](./jsdom-layout-blindness.md) R-3).
- D2 는 lint·jsdom 과 도구가 독립인 **직교 게이트** — 같은 도구를 정교화한 게 아니라 ground-truth 층위가 다른 별도 채널.

### R-3: min bar = ≥1 computed-style 단언(결정적) primary + screenshot(optional), layout-result 속성 포함 권장 [ADR-136 결정10 §8.7.2]

- 변경 UI 에 **≥1 computed-style 단언**(`toHaveCSS` / `boundingBox()` — 결정적) primary + screenshot 회귀(`toHaveScreenshot`) optional.
- jsdom 통과 ≠ 승인 — jsdom 통과·실렌더 실패면 D2 실패.
- **layout-result 속성 포함 권장**: WEB-033 류 회귀(`position:static→fixed` 추락)를 구조적으로 보장하려면 computed-style 단언이 **layout 결과 속성**(`position` / 좌표 `boundingBox` / `visibility`)을 포함해야 한다 — 색상·폰트만 단언하면 layout 회귀를 못 잡는다.

### R-4: baseline 결정성 — Linux(CI) 생성 + threshold 명시, render job idempotent [ADR-136 결정10 §8.7.3 + 결정11]

- screenshot baseline 은 **Linux(CI) 생성**으로 OS 폰트·렌더 drift 회피 + threshold(pixelmatch) 명시. baseline 은 repo commit 으로 deterministic → CI render job 재실행 idempotency 보장(non-deterministic baseline 금지).
- 도구는 Playwright 권장 — raw CDP 는 동등 저수준이나 세션/대기/diff 직접 구현 고비용. GHA ubuntu `npx playwright install --with-deps chromium` headless 동작(CFP-2505 §6 검증완).

### R-5: CI-only 격리 + 외부 navigate 금지 (운영·보안 표면 최소) [ADR-136 결정11]

- Playwright(Node+Chromium)은 `actions/setup-node` + npx self-contained → consumer host production runtime 에 Node/Chromium 강요 0(CI-only 의존 격리).
- Chromium headless 가 **외부 URL navigate 없이 로컬 빌드만 렌더** → 추가 신뢰경계 최소(CI 격리 sandbox 안). 외부 navigate 금지. supply-chain = 버전 `pin` + lockfile + `npm ci`(`@latest` 금지).

## 경계 / 예외

- **In scope**: 실 브라우저 layout 측정의 ground-truth 지위(R-1), D2 도구 독립성·jsdom 부적격(R-2), min bar = computed-style 단언 + layout-result 속성 권장(R-3), baseline 결정성·idempotency(R-4), CI-only 격리·외부 navigate 금지(R-5).
- **Out of scope**:
  - §8.7 sub-section 의 *템플릿 본문 작성*(§8.7.0 applicability 표 / §8.7.x N/A 표기) — ADR-136 결정10 + Phase 2 change-plan.md 구현. 본 fact 는 도메인 layer.
  - D2 강제 granularity(risk-gate — UI/CSS 변경 PR 만 §8.7 required) 의 *판정 트리거 정의* — ADR-136 결정9.
  - 비-레이아웃 시각 검증(접근성 a11y / 애니메이션 타이밍) — 본 fact 는 layout/computed-style ground-truth 축 한정.
  - raw CDP 직접 사용의 세부 절차 — Playwright 권장이라 일반 권고 밖.
- **Anti-pattern**:
  - jsdom 계열로 D2(render-truth)를 대체(R-2 — layout 미계산, 부적격).
  - 색상·폰트만 단언하고 layout-result 속성(position/좌표/가시성)을 빠뜨림(R-3 — WEB-033 류 회귀 미검출).
  - OS-의존 baseline 생성(R-4 — 폰트·렌더 drift 로 flaky → non-deterministic, idempotency 위반).
  - Chromium 으로 외부 URL navigate(R-5 — 신뢰경계 확장, CI sandbox 격리 위반).

## 관련 ADR / Story / 코드

- [ADR-136](../../../../archive/adr/ADR-136-frontend-quality-gate-standard.md) — frontend 품질게이트 표준. 컨텍스트 WEB-033 CDP 실측 + 결정10 §8.7.1~§8.7.3(도구 독립성·min bar·baseline) + 결정11(CI-only 격리·보안)이 본 fact 의 carrier.
- [ADR-006](../../../../archive/adr/ADR-006-testcontract-architect.md) — §8 Test Contract author = ArchitectAgent(chief), TestContractArchitectAgent = input contributor. §8.7(D2) author 경계.
- Story CFP-2505 (internal-docs `wrapper/stories/CFP-2505.md`) — ADR-136 carrier. §2 실 브라우저 렌더 검증 + §6 외부사실 검증.
- 외부사실 (CFP-2505 §6 검증완 — 본 lane 신뢰도 상향 0): Playwright `toHaveScreenshot()`(pixelmatch baseline) + `toHaveCSS`/`boundingBox()`(computed-style 결정적) + GHA ubuntu `npx playwright install --with-deps chromium` headless 동작 [source: playwright.dev/docs/test-snapshots , /ci].
- WEB-033 수치(static rectTop=2676 → fixed rectTop=0): `[verification-out-of-scope: consumer 측 실측 — 본 lane 미독립검증, CFP-2505 escalation #2502 입력 packet]`.

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2512 DeveloperAgent, ADR-136 §7.9 capture 후보 회수). CDP/Playwright 실 Chromium computed-style·좌표·스크린샷 = 레이아웃 ground-truth fact 신설. ADR-136 컨텍스트 WEB-033 CDP 실측 + 결정10 §8.7.1~§8.7.3 + 결정11 + CFP-2505 §2 도메인 해석 전사·정제(재발명 0). 외부사실(Playwright 단언·screenshot baseline·GHA headless)은 CFP-2505 §6 검증완 인용 — 새 단정·신뢰도 상향 0. WEB-033 수치(rectTop 2676→0)는 `[verification-out-of-scope: consumer 측 실측]` 한정 표기 보존. R-1(실 브라우저 = ground-truth) / R-2(도구 독립·jsdom 부적격) / R-3(computed-style 단언 + layout-result 속성 권장) / R-4(Linux baseline 결정성·idempotency) / R-5(CI-only 격리·외부 navigate 금지).
