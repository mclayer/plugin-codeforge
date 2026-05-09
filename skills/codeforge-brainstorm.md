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

**먼저 WHY를 추출하세요.** 사용자가 이것을 요구하는 근본 동기·필요·배경을 파악합니다.
지식 부족이나 선입견으로 인해 실제 필요와 다른 방향을 요청했을 가능성을 항상 고려하세요.

**WHY를 렌즈로 요구사항을 확장하세요.** 사용자가 명시한 것(what)이 아니라 파악한 동기(why)를 기준으로 AC를 도출합니다. why가 충족되려면 사용자가 미처 언급하지 않은 요구사항까지 포함해야 합니다.

출력 형식:
- 추정 동기 (why): [이 요청의 근본 필요 1~2줄]
- 명시된 요구 ↔ 실제 필요 일치 여부: 일치 / 불일치 가능성 있음 (사유 1줄)
- why 기반 확장 요구사항: [명시되지 않았지만 동기 충족에 필요한 항목 1~3개]
- AC 3~5개: [Given/When/Then 형식 — why 충족 기준으로 작성]
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
[Analyst] 추정 동기(why): {근본 필요} / 일치 여부: {일치|불일치 가능성+사유} / 예비 AC: {목록} / Edge Cases: {목록}
[PMO] 예상 Story: {N}개 / 의존: {에픽} / 위험: {1개}
================================
```

## Phase 1: 강화된 brainstorming 대화

`superpowers:brainstorming` 스킬을 호출하되, 첫 메시지에 컨텍스트 패킷을 포함.

`superpowers:brainstorming`의 checklist 1(project context explore)은 이미 수행됨 —
Phase 0 결과로 대체. checklist 2부터 진행.

**Why-first 원칙**: brainstorming의 첫 질문은 반드시 "왜"를 향한다. 사용자가 요청한 내용(what)이 아니라 그 배경·동기·실제 필요(why)를 먼저 확립한다.

- RequirementsAnalystAgent가 "불일치 가능성 있음"을 보고한 경우, brainstorming 초반에 이 점을 명시적으로 탐색한다 — "요청하신 것이 X인데, 실제로 해결하고 싶은 문제는 무엇인가요?"
- why 파악 결과 사용자의 실제 필요가 명시된 요구와 다를 경우, 더 나은 대안을 Orchestrator가 직접 제안한다 — "요청하신 X보다 Y가 실제 필요에 더 적합한 이유는 …" 형식.
- **why는 요구사항 확장의 렌즈다.** 사용자가 말한 것에 머물지 않고, 파악한 동기가 충족되려면 무엇이 더 필요한지를 brainstorming 전반에 걸쳐 지속적으로 물어본다. RequirementsAnalystAgent의 "why 기반 확장 요구사항"을 출발점으로 삼아 대화 중에 추가로 발굴한다.
- 대안 제안 후 사용자가 원래 방향을 유지하면 그 선택을 존중하고 진행한다.

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
