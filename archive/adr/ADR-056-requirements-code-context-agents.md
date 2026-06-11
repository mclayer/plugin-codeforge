---
adr_number: 56
title: 요구사항 레인 코드 컨텍스트 3 에이전트 추가
status: Accepted
category: agent-design
date: 2026-05-11
carrier_story: CFP-374
related_adrs:
  - ADR-042
  - ADR-046
  - ADR-054
supersedes: null
superseded_by: null
amends: null
is_transitional: false
---

# ADR-056: 요구사항 레인 코드 컨텍스트 3 에이전트 추가

## 상태

Accepted (2026-05-11) — CFP-374

## 컨텍스트

기능 추가·변경 Story에서 요구사항 레인의 3개 병렬 에이전트(DomainAgent·RequirementsAnalystAgent·ResearcherAgent)는 사용자 원문과 도메인 지식·외부 자료를 중심으로 분석하지만, 다음 세 가지 정보가 누락된다:

1. **변경 델타**: 현재 코드에서 무엇이 달라지는가 — 설계 레인(CodebaseMapperAgent)에서야 파악되어 FIX 루프 유발
2. **구현 가능성**: 현재 아키텍처로 자연스럽게 구현 가능한가 — 설계 레인 진입 후 아키텍처 장벽 뒤늦게 발견
3. **이전 작업 연속성**: 과거 Story·ADR과 충돌·중복 여부 — 이미 결정된 사항 재논의 또는 ADR 위반

## 결정

요구사항 레인에 3개 신규 에이전트를 추가하고, Story file §4를 §4.0/§4.1/§4.2/§4.3으로 확장한다.

### §결정 1: ChangeImpactAgent (Sonnet) 신규

- `src/**` 전체를 읽어 요구사항 구현 시 변경 예상 파일·컴포넌트·인터페이스를 AS-IS → DELTA 형태로 매핑
- Story §4.1 owner. write queue drain 방식.
- Sonnet 선택 근거: 코드 패턴 매핑·파일 목록 분류 — 창의적 판단 최소 (ADR-042 정합)

### §결정 2: FeasibilityAgent (Opus) 신규

- `src/**` + `docs/adr/ADR-*.md`를 읽어 구현 가능성 등급 판정 + 설계 레인 경고 힌트 생성
- Story §4.2 owner.
- Opus 선택 근거: 아키텍처 제약 추론·ADR 해석은 설계 레인 수준의 판단력 필요 (ADR-042 정합)

### §결정 3: ContinuityAgent (Sonnet) 신규

- `docs/stories/**`, `docs/change-plans/**`, `docs/adr/ADR-*.md`를 읽어 과거 작업과의 충돌·중복·의존 분류
- Story §4.3 owner.
- Sonnet 선택 근거: 문서 교차 참조·목록 추출 (ADR-042 정합)

### §결정 4: §4 → §4.0/§4.1/§4.2/§4.3 확장

- 기존 §4 "관련 코드 경로 + 책임" → §4.0으로 번호 변경 (RequirementsPLAgent 계속 소유)
- §4.1 (ChangeImpactAgent), §4.2 (FeasibilityAgent), §4.3 (ContinuityAgent) 신설
- story-page-structure.md + 단계별 갱신 책임 표 업데이트

### §결정 5: 6-way 병렬 패턴

6개 에이전트 모두 공통 입력 패키지를 동시에 수신. 독립 관점 보장 원칙(타 산출물 교차 전달 금지) 유지.
RequirementsPLAgent가 6개 관점 dedup·통합 수행.

## 결과

### 긍정적 결과

- 설계 레인 진입 시 코드 컨텍스트 사전 제공 → ArchitectAgent FIX 루프 감소 기대
- 아키텍처 장벽이 요구사항 단계에서 조기 발견 가능
- 과거 ADR·Story 충돌을 요구사항 단계에서 필터링

### 부정적 결과 / 트레이드오프

- 요구사항 레인 스폰 비용 증가 (3→6 병렬 추가)
- src/**가 없는 신규 프로젝트 초기 Story에서 ChangeImpactAgent·FeasibilityAgent는 "코드 없음" 결과를 반환 (null 결과이나 명시 의무 유지)

### 미결 / Follow-up

- Consumer overlay로 ChangeImpactAgent·FeasibilityAgent의 src/** 탐색 범위 제한 가능 여부 — CFP 후속 검토
- codeforge-requirements version 0.2.1 → 0.3.0 bump + marketplace sync (ADR-016 의무)

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-042](ADR-042-agent-model-selection-policy.md) — 모델 티어 정책
- [ADR-046](ADR-046-researcher-role-redefinition.md) — Researcher Opus tier 근거
- [CFP-374 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/requirements/specs/2026-05-11-requirements-code-context-agents-design.md)
- ChangeImpactAgent / FeasibilityAgent / ContinuityAgent — 현 `plugins/codeforge-requirements/agents/`, 구 plugin-codeforge-requirements repo 삭제됨 2026-06-12
- [story-page-structure.md](../../templates/story-page-structure.md)
