---
name: codeforge-writing-plans
description: 0-context 개발자도 그대로 실행 가능한 구현 계획서(plan) 작성 native skill. codeforge:brainstorm Phase 2 종료 + ArchitectAgent §3 작성에서 cross-agent 재사용. 외부 writing-plans plugin 없이 자립(ADR-122 §결정 2/3).
---

# codeforge:writing-plans Skill

codeforge 프로젝트 전용 구현 계획서(plan) 작성 스킬 — 외부 writing-plans plugin 없이 자립(native)한다. plan 작성 discipline 을 본 skill 본문이 직접 내재한다 (ADR-122 §결정 2/3).

## 호출 시점 (cross-agent 재사용)

본 skill 은 두 호출 지점이 공유한다:

- **(a) codeforge:brainstorm Phase 2 종료 시** — spec 파일 저장 완료 후 호출되어 구현 계획서를 작성한다.
- **(b) ArchitectAgent 가 Change Plan §3 도입할 설계를 작성할 때** — 설계 산출물의 step 분해/검증을 본 skill 의 discipline 으로 작성한다.

두 지점이 동일한 plan 작성 규범을 공유하므로 별도 skill 로 추출했다 (ADR-122 §결정 2/3).

## P1 discipline invariant — 0-context reader 전제 (ADR-122 §결정 3 핵심)

**계획서는 그 프로젝트·맥락을 처음 보는 개발자(0-context reader)도 그대로 실행 가능해야 한다.**

- 암묵 지식(implicit knowledge) 가정 금지 — "당연히 아는" 맥락을 생략하지 않는다.
- 생략된 맥락 가정 금지 — 직전 대화·이전 Story·구두 합의에만 존재하는 정보를 plan 이 전제하지 않는다.
- 모든 step 은 **자족적(self-contained)** 이어야 한다 — 한 step 만 읽고도 무엇을·어떻게·어떻게 검증할지 알 수 있어야 한다.

> **검증 방식 명시**: 본 invariant 는 **behavioral** 이다. mechanical lint 로는 완전 검증 불가 — 0-context 실행 가능성은 DesignReview 의 judgment(설계 리뷰 레인 판단)로 검증된다. grep gate 는 호출 토큰 재유입만 차단하며, 본 invariant 의 준수 여부는 측정하지 못한다.

## plan 작성 step 분해

작업을 순차/병렬 step 으로 분해한다. 각 step 은 다음 3 요소를 모두 담는다:

1. **무엇을 (what)** — 변경 대상 파일 경로 + 함수/심볼명을 구체적으로 명시한다.
2. **어떻게 (how)** — 구체적 변경 내용. "X 를 수정" 이 아니라 "X 의 Y 를 Z 로 바꾼다" 수준의 자족적 서술.
3. **검증 (verify)** — 이 step 의 완료를 어떻게 확인하는가 (아래 "검증 단계 의무").

**step 간 의존 순서 명시**: 어떤 step 이 어떤 step 의 선행인지(순차) 또는 독립인지(병렬 가능)를 명시한다. 0-context reader 가 실행 순서를 추론하지 않아도 되도록 한다.

## 검증 단계 의무

각 step 또는 plan 종료에 **검증 방법을 반드시 명시**한다 — "완료를 어떻게 아는가(definition of done)".

- 검증 수단 예: 테스트 실행 / grep 결과(예: "토큰 0줄") / 명령 실행 결과 / 산출물 존재 확인.
- 검증 없는 step 은 0-context reader 가 자기 작업의 성공을 판정할 수 없으므로 금지한다.

## plan 저장 위치 (dogfood-out — ADR-013 / ADR-017)

codeforge family plugin 작업의 plan 기본 저장 위치는 **plugin repo 가 아니다** — internal-docs repo 다.

- **저장 위치**: `mclayer/codeforge-internal-docs` repo 의 `<plugin-folder>/plans/YYYY-MM-DD-<KEY>-<feature>-plan.md`
  - `<plugin-folder>` = wrapper / requirements / design / review / develop / test / pmo (작업 대상 plugin 이름)
  - `<KEY>` = 현재 Story 의 CFP-NNN
- **plugin repo 안 금지 경로**: plugin repo 내 `docs/superpowers/plans/**` literal 경로는 ADR-017 lint 가 PR 단계에서 거부한다.

> consumer 프로젝트는 ADR-017 미적용 — consumer 는 자기 repo 안 plan 경로를 자유롭게 쓸 수 있다 (본 dogfood-out 규칙은 codeforge family plugin self 한정).

**근거**: [ADR-013](../../archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (dogfood-out: spec/plan SSOT = internal-docs repo, plugin repo 금지) · [ADR-017](../../archive/adr/ADR-017-skill-override-path-enforcement.md) (skill override path enforcement — literal 경로 lint).
