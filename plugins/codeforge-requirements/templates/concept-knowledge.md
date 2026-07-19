# Concept Knowledge 페이지 템플릿

ResearcherAgent가 `docs/domain-knowledge/concept/<slug>.md` 직접 write 시 따르는 schema SSOT (ADR-161).

**사용 대상**: ResearcherAgent (생성·갱신 단독)

---

## 파일 위치

- **위치**: `docs/domain-knowledge/concept/<slug>.md`. `<slug>`는 kebab-case 개념명 (예: `real-time-processing`, `order-book-depth`)
- **CODEOWNERS**: `docs/domain-knowledge/concept/**` → `@org/researchers` 자동 review (consumer overlay가 매핑)

---

## Frontmatter (필수)

````yaml
---
kind: concept_definition
title: <한 줄 제목>
slug: <kebab-case slug>
status: draft | active | deprecated
external_sources:
  - "<URL 또는 publication — Mandate 2 출처>"
related_concepts:
  - "<연관 concept slug>"
related_adrs: []
related_stories:
  - <KEY-N>
updated: YYYY-MM-DD
---
````

---

## 본문 섹션 (고정 순서)

````markdown
# <Concept Title>

## 정의 (외부 표준 기준)
업계·학계에서 통용되는 한 줄 정의. 출처 명시.

## 관련 외부 표준 / 선행사례
- 표준 / 논문 / 공급사 문서 + 핵심 내용 요약
- (URL 필수)

## 도메인 가정 (implicit)
이 개념이 프로젝트 요구사항에서 암묵적으로 전제하는 도메인 가정 목록.

## 선택지 (해석 옵션)
PLAgent가 이 개념을 요구사항에 적용할 때 선택 가능한 해석 옵션.
- 옵션 A: ...
- 옵션 B: ...
(결정은 PLAgent — Researcher는 선택지만 제공)

## 경계 / 주의
이 개념이 적용되지 않는 케이스 또는 DomainAgent 사내 지식과 충돌 가능성.

## 변경 이력
- YYYY-MM-DD: 초기 작성 (Story <KEY>)
````

---

## ResearcherAgent 작성 절차

```
0. (실행 초입 — close-loop read, ADR-046 Amd 2) 기존 docs/domain-knowledge/concept/ 자산을
   개념 정립·unknown-unknown 발굴의 *출발점*으로 재사용 read.
   · "이미 정립된 개념" 을 확인해야 새 unknown-unknown 을 발굴할 수 있다 = Mandate 2 재초점의 mandate-aligned 동기.
   · 토큰 회피: 직전 Story §6 Section 6 compact summary 역방향 재사용 우선, 필요 시에만 raw 파일 Read.
     Mode policy skip/light 판단 시 이 read 면제.
   · 독자 = 미래 Story 의 Researcher 자신 (silo close-loop, ADR-161 §결정 4/5 by-design 무손상).
1. Mandate 1 (Concept Formulation) 에서 식별된 implicit 개념별 slug 결정 (kebab-case)
2. 기존 docs/domain-knowledge/concept/ 디렉터리 Glob으로 중복 확인 (위 0 의 자산 재사용 read 의 write-time 연속선)
   · 기존 파일이 있으면 갱신 (frontmatter updated 필드 + 변경 이력 append)
   · 없으면 신규 생성
3. `Write(docs/domain-knowledge/concept/<slug>.md)` 호출
4. §6 Section 6 (Concept Summary)에 파일 경로 + compact 1-3줄 요약 포함
5. 기존 page 갱신 시 frontmatter `updated` 필드 + "변경 이력" 섹션 append
```
