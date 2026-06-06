---
kind: concept_definition
type: domain-knowledge
slug: si-framework-applicability-subject
title: SI 엔터프라이즈 프레임워크 5요소 ↔ codeforge 적용 주체 경계 (process-layer self-application vs artifact-layer projection)
status: Active
updated: 2026-05-19
carrier_story: (pending — RequirementsPL 통합 후 부여)
related_adrs:
  - ADR-078  # living architecture doc — SI ② 참조아키텍처의 process-layer 부분 대응 (consumer 산출물 X)
  - ADR-076  # declarative reconciliation upgrade — SI ⑤ 재사용 자산 저장소의 desired-state SSOT 대응 (wrapper-canonical)
  - ADR-064  # decision principle mandate — SI ⑤ 준수 게이트/거버넌스의 normative anchor 대응
  - ADR-009  # wrapper-only decomposition — codeforge 자체에 코드 자산 ③ 부재 (process plugin 본질)
related_stories: []
---

# 개념: SI 5요소의 codeforge 적용 주체 경계

## 핵심 정의

SI(System Integration) 엔터프라이즈 프레임워크 / "software factory" 표준은 5요소를
두 개의 disjoint layer 로 분리한다:

- **process/governance layer** (factory 자체에 적용): ① 아키텍트/PMO 선행 조직, ②의
  워터폴 프로세스 부분, ④ 강제 산출물 표준의 *프로세스 규칙*, ⑤의 *준수 게이트·거버넌스*
- **artifact/asset layer** (factory 가 생성하는 product line 에 적용): ② 참조아키텍처의
  *코드 골격*, ③ 6레이어+4환경 공통컴포넌트 *코드 자산*, ⑤ 전사 *재사용 코드 저장소*

외부 표준(Software Factory product-line model, TOGAF/FEA reference architecture)에서
②③⑤의 코드·자산 측면은 **factory 가 만드는 산출물(product)** 에 귀속되며 factory
runtime 자체에 귀속되지 않는다. 이것이 본 아이디어가 제기한 "적용 주체 모호성"의
표준적 해소 방향이다.

## codeforge 매핑 (subject disambiguation)

| SI 5요소 | codeforge 적용 주체 | 근거 |
|---|---|---|
| ① 아키텍트/PMO 선행 | **codeforge 자체** (process) | ArchitectPLAgent · PMOAgent · 6 lane |
| ② 참조아키텍처 | **양분** — process 부분 = codeforge (ADR-078 living arch doc) / 코드 골격 = consumer 산출물 | ADR-078 는 codeforge·consumer 양쪽 self-owned 변형 지원하나 *프로세스 문서*이지 코드 스캐폴드 아님 |
| ③ 공통컴포넌트 코드 자산 | **consumer 산출물 전용** — codeforge 자체에는 비적용 | ADR-009 wrapper-only: codeforge 는 0 core agent · agent file 부재 = 코드 자산을 보유하지 않는 process plugin |
| ④ 강제 산출물 25종 | **codeforge 자체** (process) | Story/ADR/Change Plan/retro/§14 evidence = 강제 산출물 표준의 codeforge instantiation |
| ⑤ 재사용 자산 저장소·게이트 | **양분** — 거버넌스/게이트 = codeforge (ADR-064·gate label) / 코드 자산 저장소 = consumer 또는 미구현 | ADR-076 declarative reconciliation = *플러그인 정책* 의 desired-state SSOT 이지 consumer *코드* 자산 카탈로그 아님 |

## 핵심 결론 (decision-relevant)

codeforge 는 SI 5요소 중 **process/governance layer(①④⑤-거버넌스)는 이미 SW화**
했으나, **artifact/asset layer(②-코드골격/③/⑤-코드저장소)는 본질적으로 codeforge
자체에 적용 불가** — ADR-009 wrapper-only 결정에 의해 codeforge 는 코드 자산을
보유하지 않는 process orchestration plugin 이기 때문이다. 해당 3요소는 codeforge 가
*생성·거버닝하는 consumer 프로젝트의 산출물*에만 투영(projection)된다.

"codeforge 가 SI 구조를 전체적으로 따라야 한다"는 요구는 따라서 **subject split
요구**로 재편되어야 한다: (a) process 요소 = codeforge self-application 강화 /
(b) artifact 요소 = codeforge 가 consumer 에 강제하는 *산출 표준*으로 외재화 —
codeforge 코어에 공통컴포넌트 코드 자산을 신설하는 것은 ADR-009 정면 위배.
