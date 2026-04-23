# CLAUDE.md

Claude Code용 오케스트레이션 규칙. 에이전트 상세는 각 `.claude/agents/<Name>.md` (SSOT).

## Project
`mctrader` — 암호화폐 스캘핑 자동매매 프레임워크. Python, 완전 자율 실행. `settings.json`에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

## Development Agent Team

```
User
 └── PMAgent                         # 요건 접수 + 3-PL 평행 조정 + 테스트 레인 최종 게이트 + FIX 카운터 소유
      ├── PMOAgent                     # 요건 PL
      │    ├── DocsAgent               # 문서화 (조직상 PMO, 기능상 전단계 스폰)
      │    ├── RequirementsAnalystAgent  # GPT-5.4 래퍼 (codex exec)
      │    └── ResearcherAgent         # 도메인 웹 리서치 (조건부)
      ├── ArchitectAgent              # 설계 + 구현 PL (QADev 감사 + FIX 원인 판정)
      │    ├── RefactorAgent            # 설계 공동작업자 (분석·제안, 읽기 전용)
      │    ├── QADeveloperAgent         # TDD tests/** (구현 단계)
      │    ├── DeveloperPLAgent → Frontend/Backend
      │    └── EngineerPLAgent → DataEng/ServerEng
      ├── ReviewPLAgent               # 리뷰 레인 PL (Step 1)
      │    ├── ClaudeReviewAgent
      │    └── CodexReviewAgent
      └── TestAgent                   # 테스트 레인 최종 게이트 (Step 2, PMAgent 직속 단독)
```

**용어**: "**리뷰 레인(Step 1)**" = ReviewPLAgent + Claude/Codex 병렬 리뷰. "**테스트 레인(Step 2)**" = TestAgent pytest 최종 실행. 리뷰 레인 수렴 후 테스트 레인 진입.

## 단계 용어
- **요건**: PMAgent 접수 → PMOAgent 통합 명세서 확정
- **설계**: Architect Change Plan 확정 + DocsAgent가 `docs/change-plans/<slug>.md` 저장
- **구현**: QADev + Dev/Engineer 병렬 → Architect의 QADev 매핑표 감사
- **품질**: 리뷰 레인(ReviewPL이 Claude/Codex 종합, Step 1) → 테스트 레인(TestAgent pytest, Step 2). 수렴 후 순차 — 최종 원인 판정·계획서 갱신은 Architect가 PMAgent 경유로 수령

**Change Plan**: Dev 스폰 전 `docs/change-plans/<slug>.md` 저장 필수 (생략 불허)
**통합 요건 명세서**: 복잡 요건만 `docs/requirements/<slug>.md` 저장 (PMO 판단)

## 오케스트레이션 규칙

### 플랫폼 제약
하위 에이전트는 Agent 툴 사용 불가 — 재귀 스폰 금지. 모든 스폰은 최상위 Claude가 직접. 서브에이전트 간 직접 통신 불가 (오케스트레이터 경유).

### 컨텍스트 전달
프롬프트에 관련 컨텍스트를 명시적으로 포함한다 (사용자 원문·PM 해석·관련 코드 경로·관련 문서 경로).

**ADR 참조는 선택적**:
- **verbatim 포함**: ADR 결정이 본 작업의 핵심 근거일 때 (설계 제약 직접 적용)
- **ID + 1줄 요약**: ADR이 배경 참조 수준일 때. 필요 시 sub-agent가 Confluence `mcp__atlassian__getConfluencePage`로 fetch

불필요한 verbatim 포함은 프롬프트 비대화·토큰 증가를 유발하므로 관련성 기준으로 판단한다.

### PMAgent 선행 의무
오케스트레이터는 PMOAgent/ArchitectAgent/구현 에이전트 스폰 전 **반드시 PMAgent 먼저 스폰**. 출력: 태스크 분류 + 필요 에이전트 목록 + 스폰 순서 + 조건부 생략 제안.

#### Never-skippable (단계별)
- 요건: **PMOAgent** (하위 중 하나라도 호출 시 필수), **RequirementsAnalystAgent** (PMAgent가 "요건 이미 명확" 명시 시만 생략)
- 구현: **QADeveloperAgent** (TDD)
- 품질: **ReviewPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent**, **TestAgent**

조건부 생략: ResearcherAgent(PMOAgent 판정 — Analyst 키워드 비어있을 때), EngineerPLAgent(인프라 변경 없음), DocsAgent(문서화 대상 없음, Change Plan·ADR 저장은 여전히 필수)

### 스폰 시퀀스

```
[요건] PMAgent → PMOAgent → Analyst → Researcher(조건부) → PMOAgent 통합
       · 상충 시 PMAgent 경유 사용자 에스컬레이션
       · "사용자 확인 필요" 항목은 blocking wait (사용자 답변 전 설계 진입 금지)
       · 복잡 요건 시 DocsAgent가 docs/requirements/<slug>.md 저장

[설계] PMOAgent 통합 → Architect ↔ Refactor → Change Plan 확정 → DocsAgent 저장

[구현] Architect가 병렬 스폰
       ├── QADev (tests/** 작성 — 분기 독립 1회)
       └── 분기 A(Engineer) / B(Dev) / A+B
       → Architect가 QADev 매핑표 감사 → 통과 시 품질 단계

[품질] PMAgent가 Architect 감사 PASS 수령 → ReviewPLAgent 스폰
       [리뷰 레인 Step 1] ReviewPL → Claude + Codex 병렬 리뷰 → severity 종합
             ├── P0/P1 → PMAgent 경유 Architect 회귀 (FIX 루프, 최대 3회)
             └── PASS → PMAgent가 테스트 레인 진입 지시

       [테스트 레인 Step 2] PMAgent → TestAgent pytest
             ├── FAIL → PMAgent 경유 Architect 회귀 (원인 판정 + 계획서 갱신, 재구현 후 리뷰 레인부터 재실행)
             └── ALL PASS → DocsAgent (최종 완료)
```

**분기 선택**: 1순위 A(Engineer, 인프라 해결 가능 시), 2순위 B(Dev), A+B(양측 필요). 선택 근거 Change Plan에 한 줄 기록.

### FIX 루프
**트리거**: 리뷰 레인(Step 1) P0/P1 또는 테스트 레인(Step 2) FAIL.
**시퀀스**: ReviewPL 또는 TestAgent → PMAgent 수령 → Architect ↔ Refactor 계획서 갱신 → 구현 재실행 → 리뷰 레인부터 품질 재실행.
**카운터 (PMAgent 세션 메모리 소유)**:
- 리뷰 레인(Step 1) FIX 최대 3회 → 초과 시 PMAgent 경유 사용자 ESCALATE
- 테스트 레인(Step 2) FIX 무제한 (모든 테스트 PASS 필수)
- 테스트 레인 FAIL 후 재진입한 리뷰 레인에서 P0/P1 발견 시 리뷰 레인 카운터 리셋 (재구현 결과는 새 리뷰 대상)
- 테스트 레인 반복 FAIL 시 Architect가 근본 원인 재분석해 계획서 대폭 수정 (숫자 규칙 없음)
- **ReviewPL/TestAgent/Architect 간 수평 호출 금지** — 모든 게이트 재실행과 회귀 요청은 PMAgent 경유

설계 금지 원칙 유지 — Dev·Engineer·QADev는 계획서 준수, 설계·분기 결정은 Architect+Refactor 계획서 갱신만.

### Write 권한 (path-scoped — 각 agent md frontmatter가 SSOT)
- Dev 쓰기: BackendDev(src/**), FrontendDev(templates·static), QADev(tests/**), DataEng·ServerEng(분기 A)
- 읽기 전용: Refactor, Claude/CodexReview, TestAgent, Researcher, 모든 PL
- 외부 도구 wrapper: RequirementsAnalyst(Bash(codex exec *))
- 문서 쓰기: DocsAgent(.md + Atlassian MCP — Confluence 페이지, Jira 이슈)

### Codex CLI / 플러그인 필수
- CodexReviewAgent(리뷰 레인): Codex 플러그인
- RequirementsAnalyst(요건): `codex` CLI
- 미설치 시 해당 단계 진행 불가, 오케스트레이터가 설치 안내 후 중단

### 병렬 스폰 권장
- 구현: QADev + 구현 분기
- 리뷰 레인(Step 1): Claude + Codex 리뷰 병렬
- 경로 분리된 쓰기 작업만 병렬 허용

## ADR (Confluence Pages SSOT)
- Space: `MCTRADER` / 루트 페이지 `ADR` / 6개 카테고리 parent 하위
- 카테고리: Team & Process / Architecture / Data & Storage / Infrastructure / Dashboard & UX / Trading Strategy
- 목록: `mcp__atlassian__searchConfluenceUsingCql(cql="label='adr' AND space='MCTRADER'")` / 상세: `mcp__atlassian__getConfluencePage(pageId=N)`
- 세션 시작 시 ADR 목록 조회, 결정 사항 번복 금지
- 설계 결정마다 신규 ADR 생성 (번호 = 기존 최대 + 1)
- 신규 ADR은 결정 성격에 맞는 카테고리 페이지의 child로 생성

### 생성 기준
라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 전략 도메인 핵심 개념

### 페이지 템플릿
제목 `ADR-NNN: <결정>` + label `adr` + 상단 메타데이터 테이블(번호/상태/카테고리/결정일/관련파일).
본문 섹션: `## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램(Mermaid) / ## 관련 파일`

## 버그 기록 (Jira)
- 프로젝트: `MCTRADER` (키 = 카테고리 구분 없음, label로 분류)
- 신규 버그: `mcp__atlassian__createJiraIssue(projectKey="MCTRADER", issueTypeName="작업", labels=["bug", <component>])`
- 해결 시: `mcp__atlassian__transitionJiraIssue`로 "완료" 전이

## Jira 워크플로우 (MCTRADER 프로젝트)

사용자 요건 접수부터 PR merge까지의 모든 의사결정·협업을 Jira에 영속 기록한다.

### 계층
- **Epic** = 사용자 요건 1건. 오케스트레이터가 PMAgent 스폰 직전 생성
- **Story** = PR 1건 (= Change Plan 1건). PMAgent scope 분해 시 확정된 독립 작업 단위만 생성

### 상태 + Phase Label 방식

Jira 기본 3-state 유지(`해야 할 일`/`진행 중`/`완료`). 단계는 **phase label**로 표현(Jira free tier custom status 제약).

```
[생성] status=해야 할 일 → phase:요건 label 부여 + 진행 중 전이
  ↓ Architect Change Plan 확정
[phase:요건 → phase:설계] (label 교체)
  ↓ 구현 병렬 스폰
[phase:설계 → phase:구현]
  ↓ Step1 진입
[phase:구현 → phase:리뷰-step1]
  ↓ Step1 PASS
[phase:리뷰-step1 → phase:테스트-step2]
  ↓ PR merged (GitHub for Jira 자동 전이)
status=완료, 마지막 label 유지(감사용)
```

### Transition ID
- `해야 할 일` → 11 / `진행 중` → 21 / `완료` → 31

### FIX 루프
- **리뷰 레인(Step1) P0/P1** 또는 **테스트 레인(Step2) FAIL** 시: phase label 되돌림 `phase:리뷰-step1|phase:테스트-step2 → phase:구현` + `fix:step1-retry`/`fix:step2-retry` label 추가 + 코멘트 `[FIX #N] <Agent>: <원인>`
- 카운터는 **PMAgent 세션 메모리** (리뷰 레인 최대 3회, 테스트 레인 무제한)
- 테스트 레인 FAIL 후 재진입한 리뷰 레인에서 P0/P1 발견 시 리뷰 레인 카운터 리셋

### 코멘트 규칙
형식: `[<phase>] <AgentName>: <한 줄 요약>\n\n<2-5줄 상세>\n\n원문: <경로 또는 URL>`

**Phase prefix 8종**: `[요건]`, `[설계]`, `[구현]`, `[리뷰-Step1]`, `[테스트-Step2]`, `[FIX #N]`, `[사용자]`, `[완료]`

### 코멘트 권한
- **직접 기록(9)**: PMAgent, PMOAgent, ArchitectAgent, DeveloperPLAgent, EngineerPLAgent, ReviewPLAgent, RefactorAgent, ClaudeReviewAgent, CodexReviewAgent (md frontmatter에 `mcp__atlassian__addCommentToJiraIssue` 권한)
- **오케스트레이터 경유(9)**: RequirementsAnalyst, Researcher, QADev, Frontend/Backend/DataEng/ServerEng Dev, TestAgent, DocsAgent — 보고서 맨 앞 TL;DR 1-3줄을 오케스트레이터가 그대로 복사

### GitHub 연계
- 모든 구현 커밋: `[MCTRADER-N] <type>: <summary>` prefix
- PR 제목: `[MCTRADER-N] <Story 요약>`
- PR 본문: `Jira: https://mctrader.atlassian.net/browse/MCTRADER-N` 상단 포함
- GitHub for Jira 앱이 PR merge 시 Story 자동 `완료` 전이 (설치 시)

### Labels 체계
- `phase:*` (현재 단계 1개): `phase:요건`, `phase:설계`, `phase:구현`, `phase:리뷰-step1`, `phase:테스트-step2`
- `component:*` (Story 단위): `component:collector`, `component:dashboard`, `component:strategy`, `component:backtest`
- `adr:NNN` (관련 ADR 참조, 복수)
- `branch:A` / `branch:B` / `branch:A+B` (구현 분기 결정)
- `fix:step1-retry` / `fix:step2-retry` (FIX 발생 시 누적)
- `bug` (버그 이슈), `migrated-from-repo` (2026-04-23 이관분)

### 대시보드 JQL 예시
- 현재 리뷰 중: `project = MCTRADER AND labels = "phase:리뷰-step1"`
- FIX 대상: `project = MCTRADER AND labels in ("fix:step1-retry", "fix:step2-retry")`
- Story 전체: `project = MCTRADER AND issuetype = 작업 AND statusCategory != Done`

### 원문 위치
Jira는 **워크플로우 로그**만. 원문은 각 도구 유지:
- 설계: `docs/change-plans/<slug>.md` (Git-versioned)
- 결정: Confluence ADR 페이지
- 코드 리뷰: GitHub PR 설명·코멘트

## Domain Knowledge
- [OrderBook/Trade 시각화 스펙 (Confluence)](https://mctrader.atlassian.net/wiki/spaces/MCTRADER/pages/589826)

## Trading Domain
암호화폐 · 스캘핑(단기·고빈도) · 완전 자율 실행 · 실시간 가격·호가창
