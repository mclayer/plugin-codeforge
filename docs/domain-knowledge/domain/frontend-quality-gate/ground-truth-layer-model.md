---
kind: domain_fact
title: frontend 게이트 ground-truth 층위 모델 — 텍스트(lint) < DOM(jsdom) < 실 레이아웃(headless browser) + D1/D2 상보성
area: frontend-quality-gate
topic_slug: ground-truth-layer-model
status: active
sources:
  - "ADR-136 본질 선언 + 결정1 (archive/adr/ADR-136-frontend-quality-gate-standard.md) — 게이트 보증 수준 = ground-truth 추상 수준 / D1·D2 직교·상보"
  - "CFP-2505 §2 도메인 해석 (internal-docs wrapper/stories/CFP-2505.md) — 도메인 1급 명제 + 3중 게이트 맹점 + D1/D2 상보성 표"
  - "CFP-2505 §6 외부사실 검증 (요구사항리뷰 lane PASS 13/14 confirmed) — 본 문서 외부사실 인용의 검증 출처"
related_adrs:
  - ADR-136   # frontend 품질게이트 표준 — D1 구조적 CSS lint + D2 UI 실렌더 검증. 본 도메인 모델의 1급 carrier
  - ADR-130   # applicability⊥closure + graceful-no-op invariant — D1 게이트가 딛고 선 토대
  - ADR-055   # §8.6 Integration CONDITIONAL — §8.7(D2)이 §8.6 과 disjoint axis 임을 명시
related_stories:
  - CFP-2505   # ADR-136 carrier (frontend 품질게이트 표준 발의)
  - CFP-2512   # 본 domain-knowledge 문서 착륙 (ADR-136 §7.9 회수)
updated: 2026-06-30
---

# Frontend-quality-gate · ground-truth 층위 모델

## 정의

**ground-truth 층위 모델** = frontend 변경이 머지 전 통과하는 자동 검증 게이트가 *무엇을, 어느 추상 수준에서, 무슨 ground-truth 로* 보증하는지를 층위(layer)로 정렬한 도메인 모델이다.

> **도메인 1급 명제** (ADR-136 본질 선언): 게이트가 보증하는 결함 수준은 그 게이트가 딛고 선 **ground-truth 추상 수준**이 결정한다 — 텍스트(lint) < DOM 트리(jsdom) < 실 레이아웃 좌표(headless browser). 낮은 층위 게이트는 높은 층위 버그를 **구조적으로** 못 잡는다. frontend 품질을 닫으려면 게이트를 *추가* 하는 게 아니라 ground-truth *수준* 을 올려야 한다.

3 층위는 순서가 있는 포함 관계가 아니라 **검출 가능 결함의 추상 수준**이 다른 직교 축이다:

| 층위 | ground-truth | 검출 가능 | 구조적 사각 |
|---|---|---|---|
| 텍스트(lint) | CSS/소스 구문 트리 | 구문·구조 정합(brace 균형, 빈 블록, 셀렉터 구조) | 렌더 결과 일체 미관측 |
| DOM 트리(jsdom) | DOM 노드 존재·구조 | "요소가 DOM 에 있는가" | 레이아웃 좌표·가시성·position 미계산 ([§외부사실 검증](#관련-adr--story--코드): jsdom README "Unimplemented parts: Layout") |
| 실 레이아웃(headless browser) | 실 Chromium 레이아웃 좌표/computed-style | 렌더 위치·가시성·layout-result 속성 | 작성된 케이스만 봄(커버리지 밖 미관측) |

## 컨텍스트

본 모델은 mctrader-web WEB-033 실증 결함(escalation #2502, [consumer 측 실측 — 본 lane 미독립검증]) 이 frontend 품질 3중 게이트(① lint ② jsdom 단위테스트 ③ 정적 2-peer 리뷰)를 **전부 통과**한 사건에서 도출됐다. 셋 다 layout 을 보지 않는 도구라 **상관된 맹점**을 공유한 것이다 — 텍스트도 안 보고(①) 레이아웃도 안 보고(②) 신호도 없는(③) 상태에서, 텍스트 구조결함이 빌드를 우회해 레이아웃 결과로만 발현하는 CSS-only 렌더버그가 빈 파이프라인을 관통했다.

| 게이트 | 층위 | 못 잡은 본질 |
|---|---|---|
| ① lint | 텍스트 (현 wrapper = node eslint+tsc / python ruff+pyright, **CSS 파서 0**) | CSS 파싱 도구 부재 → 미닫힌 `{` 볼 눈 없음. 검출실패 아닌 **검출기 부재**. |
| ② jsdom 단위테스트 | DOM 트리 | 모달 DOM 존재 확인(PASS) but position/실좌표/가시성 = 레이아웃 엔진 부재로 계산 자체 안 함. static 추락 관측 밖. |
| ③ 정적 2-peer 리뷰 | 사람의 빌드/코드 신호 | lenient 빌드가 에러 0 성공 → 리뷰어 도달 위험신호 0. 수백 줄 CSS 미닫힌 brace 육안 적발 비현실. |

공통 진단: 단일 게이트 강화로 닫히지 않는다. 두 층위(텍스트·실 레이아웃)를 **각각** 메워야 한다 — 이것이 D1/D2 상보성의 근거다.

## 핵심 규칙 / 불변식 (invariant)

### R-1: 게이트 보증 수준 = 딛고 선 ground-truth 층위 (도메인 핵심)

- 게이트가 검출할 수 있는 결함의 최대 추상 수준은 그 게이트의 ground-truth 가 결정한다. 텍스트 ground-truth 게이트는 텍스트 결함까지만, DOM ground-truth 게이트는 DOM 존재까지만, 실 레이아웃 ground-truth 게이트만 렌더 위치·가시성을 본다.
- **함의**: 낮은 층위 게이트를 아무리 정교화해도 높은 층위 버그는 구조적으로 못 잡는다. "jsdom 을 더 잘 쓰자"로 CSS 렌더버그를 잡으려는 시도는 층위 미스매치다 — 해법은 게이트 추가가 아니라 ground-truth 수준 상승(D2).

### R-2: D1/D2 상보성 = 원인 차단 / 증상 포착 이중방어

| | D1 구조적 CSS lint | D2 UI 실렌더 검증 |
|---|---|---|
| 닫는 층위 | 구조적(syntactic) 정적 검출 | 의미적(semantic) 동적 검증 |
| ground-truth | CSS 소스 구문 트리 | 실 Chromium 레이아웃 좌표/스타일 |
| 메우는 사각 | ① 원인(미닫힌 brace) **발생지점** 차단 | ②③ 증상(static 추락) **발현지점** 포착 |
| 검출시점 | 가장 이름(텍스트)·저비용·도메인무관 | 가장 늦음(렌더결과)·무겁지만 ground-truth |

- **D1 단독 불충분**: brace 가 멀쩡한데 깨지는 CSS(z-index/specificity/미디어쿼리)는 구조가 정상이라 못 잡는다.
- **D2 단독 불충분**: 무겁고 작성된 케이스만 본다(커버리지 밖 미관측).
- **함께**: D1 이 값싸게 구조결함 대다수를 이른 텍스트 층위에서 차단 + D2 가 구조정상·의미깨짐 잔여를 실 레이아웃 ground-truth 로 늦게 포착. WEB-033 = 구조결함이 의미결함으로 발현한 케이스라 둘 다 잡을 수 있다.

### R-3: 두 게이트는 직교 — 강제 채널·결합 분리

- D1 = CI lint 게이트(consumer required 승격 경로) / D2 = §8 Test Contract 정책(§8.7 신규 sub-section, 설계리뷰 P0 강제). 두 게이트의 **강제 채널이 다르다**(mandatory↔whitelist 동치 비대칭).
- D1 실패가 D2 를 단락(short-circuit)시키지 않도록 `needs:` 결합 금지 — 독립 job/workflow. 한 게이트의 실패가 다른 게이트의 실행을 막으면 이중방어가 깨진다.

### R-4: ground-truth 상승은 비용을 동반 — frontend-bearing 조건부 적용

- 높은 층위(실 브라우저)일수록 검출력은 크지만 비용(Chromium 설치·render 실행)도 크다. 따라서 ground-truth 수준 상승은 무조건이 아니라 frontend-bearing consumer 에만 조건부 적용한다(`frontend.applicable` flag — [jsdom-layout-blindness](./jsdom-layout-blindness.md) 와 공유하는 적용 경계).

## 경계 / 예외

- **In scope**: frontend 게이트의 ground-truth 층위 정렬(R-1), D1/D2 상보 이중방어 구조(R-2), 두 게이트 직교성(R-3), 층위 상승의 비용·조건부 적용(R-4).
- **Out of scope**:
  - 각 층위 게이트의 *구현 디테일*(stylelint config rule 목록 / Playwright 단언 작성법) — 설계·구현 lane 위임([css-brace-nesting-trap](./css-brace-nesting-trap.md) / [render-truth-headless-browser](./render-truth-headless-browser.md) 가 각 층위 fact 보유).
  - non-frontend 품질 축(접근성 a11y / 성능 perf budget / i18n) — 본 모델은 "레이아웃 ground-truth" 축에 한정.
  - `frontend.applicable` flag schema 자체(default false 등) — ADR-136 결정2 carrier.
- **Anti-pattern**:
  - 낮은 층위 게이트 정교화로 높은 층위 버그를 잡으려는 시도(R-1 — 층위 미스매치).
  - 게이트 *개수*를 늘려 frontend 품질을 닫으려는 접근(상관된 맹점을 공유하는 동일 층위 게이트는 추가해도 사각 불변).
  - D1·D2 를 `needs:` 로 결합해 한 게이트 실패가 다른 게이트를 단락(R-3).

## 관련 ADR / Story / 코드

- [ADR-136](../../../../archive/adr/ADR-136-frontend-quality-gate-standard.md) — frontend 품질게이트 표준. 본 모델의 1급 carrier (본질 선언 + 결정1 D1/D2 직교·상보).
- [ADR-130](../../../../archive/adr/ADR-130-applicability-closure-integrity.md) — applicability⊥closure + graceful-no-op invariant. D1 게이트가 딛고 선 토대.
- [ADR-055](../../../../archive/adr/ADR-055-integration-test-lane-policy.md) — §8.6 Integration CONDITIONAL. D2(§8.7)이 §8.6 과 disjoint axis(§8.6 = service 간 통합 / §8.7 = UI render-truth).
- Story CFP-2505 (internal-docs `wrapper/stories/CFP-2505.md`) — ADR-136 carrier. §2 도메인 해석 + §6 외부사실 검증(13/14 confirmed)이 본 문서 인용의 검증 출처.
- 외부사실 (CFP-2505 §6 검증완 — 본 lane 신뢰도 상향 0): jsdom 공식 README "Unimplemented parts: Layout" [source: github.com/jsdom/jsdom README]. 층위 미계산 상세 = [jsdom-layout-blindness](./jsdom-layout-blindness.md).

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2512 DeveloperAgent, ADR-136 §7.9 capture 후보 회수). frontend 게이트 ground-truth 층위 모델(텍스트<DOM<실레이아웃) + D1/D2 상보성 anchor 신설. ADR-136 본질 선언 + 결정1 + CFP-2505 §2 도메인 해석 전사·정제(재발명 0). 외부사실(jsdom layout 미구현)은 CFP-2505 §6 검증완 인용 — 새 단정·신뢰도 상향 0. R-1(보증 수준=ground-truth 층위) / R-2(D1·D2 원인차단·증상포착 상보) / R-3(직교·강제채널 분리·needs 결합 금지) / R-4(층위 상승 비용·frontend-bearing 조건부).
