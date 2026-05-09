---
name: codeforge-brainstorm
description: codeforge 프로젝트 전용 brainstorming — Requirements 에이전트 4종 병렬 컨텍스트 수집 후 강화된 설계 대화 진행. ADR-034 Amendment 1에 의해 Stage 0 공식 스킬로 지정.
---

# codeforge:brainstorm Skill

codeforge 프로젝트에서 `superpowers:brainstorming`을 대체하는 강화 brainstorming 스킬.

## 적용 조건

- `.claude/_overlay/project.yaml` 존재 (codeforge consumer 프로젝트)
- 또는 `docs/adr/` 디렉터리 존재 (wrapper dogfood 프로젝트)

조건 불충족 시 `superpowers:brainstorming`으로 fallback.

## Phase 0 opt-in 확인

스킬 실행 직후 사용자에게 확인 (별도 메시지):

> "4개 에이전트를 병렬로 실행해 brainstorming 컨텍스트를 수집합니다.
> ResearcherAgent(Opus tier) 포함으로 추가 비용이 발생합니다.
> Phase 0을 실행할까요?"

사용자 거부 → `superpowers:brainstorming` 스킬로 즉시 fallback.

## Phase 0: 병렬 에이전트 burst

4개 에이전트를 **동시에** spawn. Agent tool 4 calls in parallel.

> **템플릿 변수 주의**: `{USER_IDEA}`, `{OPEN_EPICS}`, `{DESIGN_SUMMARY}`는 Orchestrator가 에이전트 spawn 직전 실제 값으로 대체한다. 스킬 파일 내 이 변수들은 "여기에 해당 내용을 삽입하라"는 지시이며 실제 코드가 아니다.

### DomainAgent 프롬프트 템플릿

```
당신은 codeforge DomainAgent입니다.
사용자의 아이디어: {USER_IDEA}

docs/domain-knowledge/ 디렉터리를 읽고 이 아이디어와 관련된
핵심 도메인 사실 5개 이내를 300자 이내로 요약하세요.
추론 없이 사실만. 존재하지 않으면 "관련 domain-knowledge 없음"으로 응답.
```

### ResearcherAgent 프롬프트 템플릿

```
당신은 codeforge ResearcherAgent입니다.
사용자의 아이디어: {USER_IDEA}

이 아이디어의 unknown unknowns와 핵심 개념을 탐구하세요.
출력 형식 (500자 이내):
- 핵심 개념 3개: [개념명: 1줄 설명]
- Unknown unknowns 2개: [발견한 암묵적 가정 또는 위험]
추론 근거 생략. 결론만.
```

### RequirementsAnalystAgent 프롬프트 템플릿

```
당신은 codeforge RequirementsAnalystAgent입니다.
사용자의 아이디어: {USER_IDEA}

이 아이디어를 예비 요구사항으로 확장하세요.
출력 형식:
- AC 3~5개: [Given/When/Then 형식]
- Edge Case 2개: [예외 시나리오]
추론 과정 생략. 목록만.
```

### PMOAgent 프롬프트 템플릿 (Phase 0 — 예비 분해)

```
당신은 codeforge PMOAgent입니다.
사용자의 아이디어: {USER_IDEA}
현재 open 에픽 목록: {OPEN_EPICS}  ← gh issue list --label phase:설계 등으로 수집

이 아이디어의 예비 분해를 제안하세요.
출력 형식:
- 예상 Story 수: N개 (근거 1줄)
- 의존 가능 epic: [CFP-NNN] 또는 "없음"
- 주요 위험 요소: 1개
추론 과정 생략.
```

### 컨텍스트 패킷 합성

4개 에이전트 결과를 다음 형식으로 합성:

```
=== brainstorming 컨텍스트 패킷 ===
[DomainAgent] {도메인 사실 요약}
[Researcher] 핵심 개념: {목록} / Unknowns: {목록}
[Analyst] 예비 AC: {목록} / Edge Cases: {목록}
[PMO] 예상 Story: {N}개 / 의존: {에픽} / 위험: {1개}
================================
```

## Phase 1: 강화된 brainstorming 대화

`superpowers:brainstorming` 스킬을 호출하되, 첫 메시지에 컨텍스트 패킷을 포함.

`superpowers:brainstorming`의 checklist 1(project context explore)은 이미 수행됨 —
Phase 0 결과로 대체. checklist 2부터 진행.

## Phase 2: 분해 및 scope_manifest 생성

brainstorming 설계 확정 후 (spec 작성 직전):

PMOAgent를 다시 spawn (2nd pass — Phase 0의 예비 분해와 달리 설계 확정 후 정확한 분해):

```
당신은 codeforge PMOAgent입니다.
확정된 설계: {DESIGN_SUMMARY}

다음을 생성하세요:
1. Epic/Story 분해 초안 (Story 제목 + 1줄 설명)
2. scope_manifest 초안 (YAML):
   planned_adrs: [예약 필요 ADR 수]
   planned_files:
     - 예상 변경 파일 경로들
   planned_claude_md_sections:
     - 예상 수정 섹션명들
```

PMOAgent 출력의 scope_manifest 초안을 spec 파일 끝에 추가.

## 종료

spec 파일 저장 완료 후 `superpowers:writing-plans` 스킬 호출.
(scope_manifest 초안은 spec 파일에 포함됨 — Phase 1 PR 시 Issue body에 붙여넣기)
