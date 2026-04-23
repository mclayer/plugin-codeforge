---
title: Orchestrator Playbook
status: active
owner: Orchestrator (= 최상위 Claude 세션)
created: 2026-04-23
related:
  - CLAUDE.md
  - .claude/agents/PMOAgent.md
  - .claude/agents/ArchitectAgent.md
  - .claude/agents/ReviewPLAgent.md
  - .claude/agents/TestAgent.md
---

# Orchestrator Playbook

최상위 Claude 세션(이하 **Orchestrator**)의 행동 SSOT. 사용자(Human)가 제공한 요건을 받아 18개 에이전트를 조정하는 모든 규약을 담는다.

`CLAUDE.md`는 "무엇이 있는가(에이전트 목록·단계 용어·권한 경계)"를 정의하고, 본 playbook은 "어떻게 움직이는가(생명주기·스폰·복원·에스컬레이션)"를 정의한다.

---

## 1. 세션 생명주기

### 1.1 세션 개시 체크리스트

사용자 요건 접수 직후 아래를 순서대로 수행한다. 하나라도 생략하면 이후 단계에서 컨텍스트 drift·중복 작업 발생.

1. **메모리 로드**: `/Users/1111971/.claude/projects/-Users-1111971-workspace-mctrader/memory/MEMORY.md` — 이전 세션 feedback·project·reference 기록 확인
2. **Jira 활성 Story 조회**: `searchJiraIssuesUsingJql("project = MCTRADER AND statusCategory != Done")` — 진행 중인 Story가 있는지 확인 (resume 후보)
3. **ADR 목록 확인**: 세션 내 첫 설계 결정 직전에만 `searchConfluenceUsingCql("label='adr' AND space='MCTRADER'")` — 기존 결정 번복 금지
4. **태스크 분류**: 아래 중 판정
   - 신규 요건 → §1.2 신규 세션 플로우
   - resume (활성 Story 존재) → §7 세션 재개 복원 절차
   - 프로덕션 버그·긴급 hotfix → §8 별도 경로 (후속 작업)

### 1.2 신규 세션 플로우

```
사용자 요건 접수
  ↓
Orchestrator 태스크 분류 (Epic/Story 단위 분해)
  ↓
Jira Epic 생성 (요건 1건 단위, 복잡하면 여러 Story로 분해)
  ↓
Story별 반복:
  ├─ Jira Story 생성 (phase:요건 라벨 + 진행 중 전이)
  ├─ DocsAgent 스폰: Confluence Story 페이지 생성 (템플릿 753705 복제, §1-2 초기화)
  └─ PMOAgent 스폰 (요건 단계 시작)
```

### 1.3 세션 종료 조건

- **정상 완료**: 테스트 레인 PASS → DocsAgent로 Story 페이지 §11 완료 처리 + PR merge → 세션 회고 (§8.3) → 종료
- **blocking wait**: PMOAgent "사용자 확인 필요" 체크박스 미해소 → 사용자에게 질문 제시 후 세션 대기 상태 전이 (§2)
- **ESCALATE**: 리뷰 레인 FIX 3회 초과 또는 Architect 판단 근본 한계 → 사용자에게 구조화된 에스컬레이션 보고 후 판단 대기

---

## 2. 사용자(Human) 상호작용 규약

### 2.1 blocking wait 진입 기준

다음 중 하나 이상 충족 시 Orchestrator는 **즉시 진행 중단**하고 사용자 응답 대기 상태로 전이:

- PMOAgent 통합 명세서에 "사용자 확인 필요" 체크박스 미해소 항목 존재
- PMOAgent 상충 조정 실패 (Analyst 해석 ↔ ADR 충돌)
- ArchitectAgent가 "기존 API의 breaking change 불가피" 보고
- ReviewPL ESCALATE 판정 (Step 1 FIX 3회 초과)
- Architect가 "Step 2 반복 FAIL — 근본 원인 재분석 후에도 해소 불가" 보고
- 사용자 요건 범위·우선순위·예산이 프롬프트에서 해석 불가

### 2.2 사용자 응답 수령 시 재스폰 대상 판정

사용자 응답이 들어오면 아래 표에 따라 재스폰 대상을 결정한다.

| 응답 종류 | 재스폰 대상 | 전달할 컨텍스트 |
|-----------|------------|----------------|
| "사용자 확인 필요" 답변 | PMOAgent | 답변 내용 + 기존 Story 페이지 URL. PMOAgent가 §5.5 체크박스 갱신 후 통합 명세서 재확정 |
| ADR 갱신 승인 | DocsAgent → PMOAgent | DocsAgent가 ADR 업데이트 후 PMOAgent 재호출 |
| breaking change 승인 | ArchitectAgent | ADR 후보 추가 지시 + Change Plan 재수립 |
| ReviewPL ESCALATE 후 judgment | ArchitectAgent (재진입) | 사용자 지시를 계획서 갱신 입력으로 전달. 리뷰 레인 카운터 **리셋** |
| Step 2 반복 FAIL 판단 | ArchitectAgent | 사용자가 지시한 근본 원인 가설 + 계획서 대폭 수정 허가 |
| 요건 범위·우선순위 변경 | Orchestrator 자체 판단 | Jira Story 재분해 또는 기존 Story scope 수정 → PMOAgent 재스폰 |

### 2.3 사용자 ESCALATE 프롬프트 표준 형식

```
⚠️ 사용자 판단 요청 (ESCALATE)

[상황]
- Story: MCTRADER-N — {한 줄 요약}
- 현재 단계: {phase:리뷰-step1 / phase:테스트-step2 / phase:구현}
- 트리거: {ReviewPL 3회 FIX / Step 2 반복 FAIL / ADR 충돌 / breaking change}

[시도 이력]
1. Iteration 1: {수정 방향} → {결과}
2. Iteration 2: {수정 방향} → {결과}
3. ...

[남은 이슈]
- {객관적 blocking 결함 목록}

[가능한 선택지]
- (A) {선택 A — 트레이드오프 서술}
- (B) {선택 B}
- (C) 요건 자체 재해석 — 범위 축소 / ADR 갱신 / 포기

[Orchestrator 의견]
{선택 A 권장 등, 근거 1-2줄}

다음 행동을 지시해주세요.
```

응답 전까지 Orchestrator는 **스폰 중단**. 사용자 응답 수령 시 §2.2 표로 재진입.

### 2.4 사용자 지시 vs 내부 판단 충돌

- **사용자 지시가 항상 우선**. CLAUDE.md 규칙·ADR·본 playbook은 사용자 명시 지시에 의해 override 가능
- 단, 사용자 지시가 ADR과 충돌하면 **ADR 갱신 의사 확인** 후 진행 (암묵적 위반 금지)
- 트레이딩 자동매매 도메인 특성상 **안전 제약**(주문 검증·리스크 한도 등)은 사용자가 명시적으로 해제하지 않는 한 유지

---

## 3. 스폰 시퀀스 + 프롬프트 템플릿

### 3.1 단계별 스폰 순서 (요약)

```
요건: Orchestrator → PMOAgent(하위에 PMAgent → Analyst → Researcher 조건부) → Story §3-6 갱신
설계: Orchestrator → ArchitectAgent ↔ RefactorAgent → Change Plan 확정 → DocsAgent(git + Story §7)
구현: Orchestrator → ArchitectAgent → (QADev ∥ DeveloperPL/EngineerPL) → 매핑표 감사
리뷰 레인: Orchestrator → ReviewPLAgent → (ClaudeReview ∥ CodexReview 병렬) → PASS/FIX 판정
테스트 레인: Orchestrator → TestAgent (기능 모드 → 성능 모드 순차) → ALL PASS/FAIL
완료: Orchestrator → DocsAgent (Story §11 + PR 링크 + status:completed 라벨)
```

상세 분기 규칙은 CLAUDE.md "스폰 시퀀스" 섹션과 각 에이전트 md 참조.

### 3.2 에이전트 프롬프트 표준 템플릿

**공통 블록** (모든 에이전트 스폰에 포함):

```
[컨텍스트]
- Jira Story: MCTRADER-N (phase:<현재 라벨>)
- Confluence Story 페이지: https://mctrader.atlassian.net/wiki/spaces/MCTRADER/pages/<id> (pageId=<id>)
- 참조 섹션: §{X}, §{Y}   ← 필요한 것만 지정
- 관련 ADR (직접 제약 있을 때만 verbatim, 그 외 Story 페이지 §3 링크로 충분):
  {ADR 번호 + 1줄 요약}

[작업 지시]
{에이전트별 구체 지시 — 산출물·경계·완료 기준}

[복귀 보고 형식]
- TL;DR 1-3줄 + 상세 본문
- Jira 직접 기록: `[<phase>] <AgentName>: <요약>` (본 에이전트 md "Jira 코멘트 규약" 참조)
- 산출물 경로: {파일 경로 또는 Story 페이지 섹션 N 갱신 의뢰}

[제약]
- {에이전트 권한·책임 경계, 필요 시 강조}
```

**에이전트별 특이 블록** (공통 블록 위에 추가):

| 에이전트 | 추가 블록 |
|----------|----------|
| **PMOAgent** | PMAgent 생략 여부 명시, Analyst/Researcher 스폰 재량 |
| **PMAgent** | 사용자 원문 verbatim (Story 페이지 §1 복사), 도메인 질문 힌트 |
| **RequirementsAnalystAgent** | Researcher 키워드 필드 생성 의무, codex CLI 필수 |
| **ArchitectAgent** | Change Plan 저장 경로 (`docs/change-plans/<slug>.md`) + DocsAgent 이중 저장 의무 |
| **RefactorAgent** | 쓰기 권한 없음 — 분석·제안만, Dev가 실행 |
| **QADeveloperAgent** | 매핑표 반환 의무, `tests/perf/**` 포함 시 baseline 정책 |
| **Frontend/BackendDev** | 계획서 변경 금지 — 결함 발견 시 즉시 Architect 에스컬레이션 |
| **DataEng/ServerEng** | 분기 A 경로 지시 + 설계 금지 원칙 |
| **ReviewPLAgent** | Claude/Codex 병렬 스폰 후 종합 담당 — 정규화 스키마 준수 |
| **Claude/CodexReviewAgent** | 정규화 스키마(P0/P1/P2/P3) 반환 필수, 독립 수행 |
| **TestAgent** | 기능 모드 → 성능 모드 순차 실행, baseline 비교 임계 mean:10% |
| **DocsAgent** | Confluence/git 중 어느 쪽 작업인지, 섹션 번호 명시 |

### 3.3 컨텍스트 주입 정책

- **Story 페이지 URL + 참조 섹션 번호**가 기본 — Orchestrator는 verbatim 복사 지양
- ADR **직접 제약** (설계 강제 수준)인 경우에만 프롬프트에 verbatim 포함
- 배경 참조 ADR은 Story 페이지 §3 링크로 충분 — 에이전트가 필요 시 `getConfluencePage`로 fetch
- 코드 경로는 Story 페이지 §4에 요약, 구체 내용은 에이전트가 `Read` 도구로 직접 접근

---

## 4. 병렬 스폰 판단

### 4.1 병렬 가능 조건 (AND)

1. **경로 분리**: 쓰기 대상 파일 경로가 겹치지 않음 (path-scoped 권한으로 보장)
2. **입력 독립**: 한쪽 산출물이 다른 쪽 입력이 아님
3. **완료 대기 가능**: 모든 병렬 에이전트 완료 후 종합 판단 가능

세 조건 중 하나라도 부족하면 순차 스폰.

### 4.2 표준 병렬 패턴 3종

| 패턴 | 구성 | 조건 충족 |
|------|------|----------|
| **리뷰 레인** | ClaudeReviewAgent ∥ CodexReviewAgent | 읽기 전용 + 정규화 스키마 동일 반환 → ReviewPL이 합집합 평가 |
| **구현 단계** | QADeveloperAgent(tests/**) ∥ {DeveloperPL(src/**) / EngineerPL(deploy·config·scripts)} | 쓰기 경로 분리 |
| **PMO 요건** | **순차 진행 원칙** (PMAgent → Analyst → Researcher) — 병렬 아님 | Analyst 입력에 PMAgent 해석 필요, Researcher 입력에 Analyst 키워드 필요 |

### 4.3 병렬 일부 실패 시 처리

- **모두 완료 대기**가 원칙 — 한쪽 빨리 실패해도 나머지 완료까지 기다려 종합 판단
- 이유: FIX 지시를 한 번에 포괄적으로 전달해 iteration 낭비 방지
- 예외: ClaudeReview가 [P0]를 즉시 내면 CodexReview 대기 없이 FIX 진입 가능 — 단, 이 경우에도 Codex 완료 후 결과 병합해 Story 페이지 §9에 기록

---

## 5. Confluence Story 페이지 동기화

### 5.1 단계 종료 시 DocsAgent 스폰 체크리스트

Orchestrator는 각 단계 종료 직후 DocsAgent를 스폰해 Story 페이지(MCTRADER-N)의 해당 섹션을 갱신시킨다.

| 트리거 | 갱신 섹션 | Orchestrator가 DocsAgent에 전달할 내용 |
|--------|----------|---------------------------------------|
| Jira Story 생성 직후 | 페이지 신규 생성 + §1-2 | 사용자 원문 verbatim + PMAgent 도메인 해석 결과 |
| PMOAgent 통합 명세서 확정 | §3-6 | 관련 ADR 링크 / 코드 경로 / Analyst 해석 / Researcher 배경지식 / 상충 분석 |
| Architect Change Plan 확정 | §7 | Change Plan GitHub 링크 + "목적 / 도입할 설계 / API 계약 / 분기 선택" verbatim or 요약 + Refactor 분석 요약 |
| Dev/Engineer 구현 완료 | §8 | QADev 매핑표 요약 + 담당 에이전트 + 변경 파일 주요 경로 |
| 리뷰 레인 iteration 종료 | §9 "리뷰 레인 Iteration N" | Claude/Codex severity counts + 주요 findings 3-5건 + ReviewPL 판정 |
| 테스트 레인 종료 | §9 "테스트 레인" | 기능 통과/실패 개수 + 성능 baseline 대비 변동 요약 |
| FIX 발생 (iteration 단위) | §10 "Iteration N" | 트리거 · 원인 분석 · 수정 방향 · 결과 |
| PR merged (최종) | §11 + 라벨 | PR 링크 + `status:completed` 라벨로 교체 |

### 5.2 Story 페이지 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `getConfluencePage(pageId=N)` 후 해당 섹션만 참조
- 전체 페이지 읽기는 Architect 설계 진입 1회만 허용 (§1-6 전체가 필요)
- 페이지 변경은 **DocsAgent 독점** — 다른 에이전트는 `updateConfluencePage` 금지

### 5.3 Jira Story description vs Story 페이지

| 위치 | 내용 |
|------|------|
| Jira Story description | 한 줄 요약 + 수용 기준 + Confluence Story 페이지 URL (live 링크) |
| Confluence Story 페이지 | 전체 컨텍스트·서사 (§1-11 규격) |
| Jira Story 코멘트 | 단계별 이벤트 로그 (각 에이전트 `[<phase>] <AgentName>: <한 줄>` 직접 기록) |

Jira는 이벤트·상태, Confluence는 구조화 영속 — 역할 분리 준수.

---

## 6. FIX 루프 상태 머신

### 6.1 카운터 상태

Orchestrator는 세션 메모리에 아래 두 카운터를 유지한다.

```
state = {
  "step1_fix_count": int,   # 0..3, 3 초과 시 ESCALATE
  "step2_fix_count": int,   # 0..∞, 제한 없음
  "current_story": "MCTRADER-N",
  "current_phase": "phase:구현|phase:리뷰-step1|phase:테스트-step2"
}
```

### 6.2 트리거 → 상태 전이

| 현재 phase | 트리거 | 전이 후 phase | 카운터 동작 |
|-----------|--------|---------------|-------------|
| 리뷰-step1 | ReviewPL FIX 판정 | 구현 | `step1_fix_count += 1`. 3 초과 시 ESCALATE |
| 리뷰-step1 | ReviewPL PASS | 테스트-step2 | (변화 없음) — 리뷰 레인 진입 직전이라면 `step1_fix_count` 유지 |
| 테스트-step2 | TestAgent FAIL | 구현 | `step2_fix_count += 1`, **`step1_fix_count = 0`으로 리셋** |
| 테스트-step2 | TestAgent ALL PASS | 완료 | (종료) |

### 6.3 카운터 리셋 조건

- **Step 2 FAIL → 구현 복귀 시 `step1_fix_count = 0`**: 재구현 결과는 새 리뷰 대상. 이전 리뷰 FIX 카운트는 옛 코드 기준이라 의미 없음
- 리뷰 레인 내부 FIX 루프는 리셋 없음 (3회 누적 → ESCALATE)

### 6.4 세션 인터럽트 시 카운터 복원

Orchestrator 세션 메모리는 휘발성. 세션 재개 시 Jira 라벨로 복원:

```
step1_fix_count = Jira Story의 "fix:step1-retry" 라벨 부여 횟수 (라벨 변경 이력에서 카운트)
step2_fix_count = Jira Story의 "fix:step2-retry" 라벨 부여 횟수
```

Jira 라벨은 누적 제거되지 않으므로 카운트 = 현재 라벨 개수가 아닌 **부여 이력 개수**. 필요 시 `getJiraIssue(expand="changelog")`로 라벨 변경 이력 조회해 재계산.

---

## 7. 세션 재개(resume) 복원 절차

세션 인터럽트 후 재시작 시 Orchestrator가 자동으로 재진입 지점을 판정한다.

### 7.1 활성 Story 조회

```
searchJiraIssuesUsingJql("project = MCTRADER AND statusCategory != Done")
```

결과가:
- **0건**: 신규 세션 — §1.2로 진입
- **1건**: 자동 resume — §7.3 매핑 표 적용
- **2건 이상**: 사용자에게 어느 Story를 resume할지 확인 (fallback §7.6)

### 7.2 Story 페이지 최신 섹션 판독

`getConfluencePage(pageId=<Story 페이지 id>)` → 어느 섹션까지 채워졌는지 확인해 재진입 지점을 보정.

### 7.3 phase label ↔ 재진입 에이전트 매핑

| phase 라벨 | 마지막 채운 Story 페이지 섹션 | 재진입 에이전트 |
|-----------|-------------------------------|-----------------|
| phase:요건 | §1-2까지 | PMOAgent (Analyst/Researcher 단계 확인 후 이어서) |
| phase:요건 | §5-6까지 | PMOAgent — 통합 명세서 재확정, "사용자 확인 필요" 해소 여부 체크 |
| phase:설계 | §7 초안까지 | ArchitectAgent — Change Plan 저장 여부 확인 후 이어서 |
| phase:구현 | §7 완료, §8 비어있음 | ArchitectAgent가 QADev + Dev/Engineer 스폰 필요 (상태 불명 시 Orchestrator가 계획서 재확인) |
| phase:구현 | §8 일부 채움 | 마지막 구현 에이전트 (Story 페이지 §8에서 확인) 재스폰 |
| phase:리뷰-step1 | §9 일부 | ReviewPLAgent (Claude/Codex 병렬 재스폰) |
| phase:테스트-step2 | §9 테스트 블록 비어있음 | TestAgent 재스폰 |
| phase:테스트-step2 | §9 테스트 블록 FAIL 상태 | `step1_fix_count = 0`으로 리셋 후 ArchitectAgent 회귀 |

### 7.4 FIX 카운터 복원

§6.4 절차로 Jira 라벨 이력에서 복원.

### 7.5 사용자 통보

복원 판정 완료 후 사용자에게 **구조화된 통보** 제시:

```
🔄 세션 재개

[복원된 상태]
- Story: MCTRADER-N — {제목}
- phase: {현재 라벨}
- 재진입 지점: {에이전트 이름} 스폰
- FIX 카운터: Step 1 = {n}/3, Step 2 = {m}
- Story 페이지 마지막 갱신 섹션: §{X}

[이어서 진행합니다. 문제 있으면 알려주세요.]
```

### 7.6 Fallback (자동 판정 실패)

- 활성 Story 2건 이상 → 사용자에게 "어느 Story를 resume하시겠습니까?" 질문
- Story 페이지 접근 불가 → Atlassian MCP 장애 의심, §9.2로 이동
- phase 라벨과 Story 페이지 섹션이 불일치 → 사용자에게 모호성 보고, 판단 요청

---

## 8. 토큰 예산 모니터링 + 세션 회고

### 8.1 추적 지표

Orchestrator는 세션 내 아래 누적치를 유지:

- 단계별 input/output 토큰 (요건 / 설계 / 구현 / 품질 / 완료)
- 에이전트별 누적 토큰 (PMAgent 회고 보고 표에서 이관된 18 에이전트 분)
- FIX iteration별 추가 토큰

### 8.2 단계별 사전 예산·중단 임계

| 경로 | 사전 예산 (input+output) | 중단 임계 |
|------|-------------------------|----------|
| 요건 | 50k | 100k |
| 설계 | 100k | 200k |
| 구현 | 200k | 400k |
| 품질 | 100k | 250k |
| FIX 루프 (per iteration) | 50k | 150k |

**중단 임계 초과 시**: 진행 중단 → 사용자에게 구조화 에스컬레이션 (§2.3 형식 준용) — "토큰 한계 도달, 계속 진행할지 결정해주세요".

### 8.3 세션 회고 보고 (완료 시 필수)

정상 완료 또는 ESCALATE 시점에 아래 형식으로 사용자에게 보고.

#### 에이전트별 작업 요약 (18 에이전트 모두 포함, 미참여는 "-")

| Agent | 수행 내용 |
|-------|-----------|
| Orchestrator | |
| PMOAgent | |
| PMAgent | |
| DocsAgent | |
| ResearcherAgent | |
| RequirementsAnalystAgent | |
| ArchitectAgent | |
| RefactorAgent | |
| DeveloperPLAgent | |
| FrontendDeveloperAgent | |
| BackendDeveloperAgent | |
| EngineerPLAgent | |
| DataEngineerAgent | |
| ServerEngineerAgent | |
| QADeveloperAgent | |
| ReviewPLAgent | |
| ClaudeReviewAgent | |
| CodexReviewAgent | |
| TestAgent | |

#### 토큰 사용량 (18 에이전트 모두 포함, 0 허용)

| Agent | Input Tokens | Output Tokens | 합계 |
|-------|-------------|---------------|------|
| Orchestrator | | | |
| PMOAgent | | | |
| ... (18개 에이전트 전체) | | | |
| **합계** | | | |

토큰 수는 각 Agent 호출 결과에 포함된 usage 정보를 기반으로 기록한다. Orchestrator 자체 토큰은 세션 전체 - 서브에이전트 합계로 계산.

---

## 9. 트러블슈팅 플레이북

### 9.1 에이전트 스폰 실패

| 증상 | 원인 | 대응 |
|------|------|------|
| Agent 툴 호출 실패 | subagent_type 철자 오류 | `.claude/agents/` 목록과 대조 후 재시도 |
| 권한 거부 (Edit/Write) | path-scoped 권한 불일치 | 대상 에이전트 md frontmatter 권한 확인, 담당 에이전트 재선택 |
| 무한 스폰 | 서브에이전트가 Agent 툴 호출 시도 | 플랫폼 제약 위반 — 해당 에이전트 md에 "직접 스폰 불가" 명시 확인 |

### 9.2 Atlassian MCP 연결 장애

Story 페이지 갱신·Jira 코멘트 기록이 불가할 때:

1. 세션 내 임시 로그로 전환 — Orchestrator 메모리에 섹션 갱신 내용 누적
2. 사용자에게 "Atlassian MCP 장애 — 세션 종료 전 일괄 동기화하거나 수동 입력 필요" 통보
3. 복구 후 DocsAgent 일괄 스폰으로 backlog 동기화

Jira 라벨 복원이 불가하면 FIX 카운터는 사용자 확인 필요.

### 9.3 Codex CLI / 플러그인 미설치

- **CodexReviewAgent (리뷰 레인 Step 1)**: 미설치 시 리뷰 레인 **진입 불가** — Orchestrator가 사용자에게 설치 안내 후 세션 중단
- **RequirementsAnalystAgent (요건)**: `codex` CLI 미설치 시 요건 단계 **진입 불가** — 동일 처리
- 두 경우 모두 `SKIPPED` 경로 허용 안 됨 — Codex 독립 시각 없이는 구조가 성립하지 않음

### 9.4 Story 페이지 stale 감지

에이전트 보고에서 "Story 페이지에 없는 컨텍스트가 프롬프트로 주입됨" 또는 "섹션 내용이 현재 코드와 불일치" 감지 시:

1. Orchestrator가 즉시 DocsAgent 스폰 → 최신 상태로 Story 페이지 갱신
2. 갱신 완료 후 해당 에이전트 재스폰 (fresh 컨텍스트로)
3. 반복 발생 시 Story 페이지 템플릿 규격 위반 의심 — 사용자 보고

### 9.5 FIX 카운터 복원 실패

Jira 라벨 이력 조회가 불가하거나 부정확할 때:

1. 현재 라벨 `fix:step1-retry` / `fix:step2-retry` 존재 여부만 확인
2. 존재 시 카운터 = 1로 보수적 초기화 → Story 페이지 §10 FIX 서사에서 실제 iteration 수 확인 후 보정
3. 여전히 모호하면 사용자에게 판단 요청

---

## 부록 A. 관련 문서

- `CLAUDE.md` — 에이전트 목록·단계 용어·권한·Jira/ADR 규약 ("무엇")
- 각 `.claude/agents/<Name>.md` — 에이전트별 역할·포지션·제약 (SSOT)
- Confluence `Stories` parent (pageId=589846) — Story 페이지 규격
- Confluence `ADR` 트리 — 설계 결정 아카이브
- `docs/change-plans/<slug>.md` — Change Plan 실행 명세 (git)

## 부록 B. 개정 이력

본 playbook은 에이전트 구조·규약 변경 시 PR과 함께 갱신한다. git log로 변경 추적.
