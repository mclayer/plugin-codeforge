# Jira 기반 에이전트 워크플로우 통합 설계

**Date**: 2026-04-23
**Status**: Draft (spec 리뷰 대기)
**Scope**: 에이전트 팀의 의사결정·협업 과정을 Jira Epic/Story/코멘트로 영속화

## 1. 배경

현재 mctrader 에이전트 팀은 SI 프로젝트 구조(PM → PL → 구현자·QA·리뷰어)로 구성되어 있으나, 의사결정 과정은 Claude Code 세션 내 대화 로그에만 남는다. 이로 인해:

- **감사 불가**: "이 ADR은 왜 생겼나"를 세션 종료 후 재구성하기 어렵다
- **PR 연계 부족**: 코드 변경과 에이전트 결정의 연결 고리가 문서·커밋 메시지에만 있음
- **FIX 루프 불투명**: Step 1/2 FAIL 원인·재설계 이유가 세션 내부에 매몰

Jira MCTRADER 프로젝트를 **워크플로우 로그** 역할로 도입해 영속화한다. ADR은 이미 Confluence, 설계서는 `docs/change-plans/`, 코드 리뷰는 PR로 분담되어 있으므로 **Jira는 "누가 언제 어떤 결정을 내렸고 단계를 이동시켰는가"만 기록**한다.

## 2. 결정 요약

| # | 항목 | 결정 | 근거 |
|---|---|---|---|
| D1 | 계층 | 2계층 (Epic → Story) | PR 1건 = Story 1건으로 GitHub 매핑 자연 |
| D2 | Epic 범위 | 사용자 요건 1건 (복수 Story 포함 가능) | 큰 기능이 여러 PR로 분해되는 케이스 수용 |
| D3 | Story 단위 | 독립 PR/머지 단위 (1 Story = 1 PR) | 코드 리뷰 단위와 정합 |
| D4 | Story 사이클 | 각 Story가 자체 full cycle(요건→설계→구현→품질) | PM scope 분해 이후 작업별 요건 세부화 필요 |
| D5 | 상태 전이 | 기본 3-state 유지 + **phase label로 단계 표현** (Jira free tier 제약 — custom status 추가 불가) | JQL `labels = "phase:*"`로 단계별 필터, 보드 컬럼 대신 필터 UI 사용 |
| D6 | 코멘트 권한 | 오케스트레이터 + 9개 결정/PL 에이전트 직접 기록 | 결정자 1차 출처 보존, 구현자는 오케스트레이터 경유 |
| D7 | GitHub 연계 | 커밋·PR `[MCTRADER-N]` prefix + GitHub for Jira 앱 | 양방향 추적 + PR merge 자동 전이 |
| D8 | 원문 위치 | Change Plan md(Git) / ADR(Confluence) / PR(GitHub) 원문 유지 | 각 도구의 강점 활용, Jira는 요약/링크만 |
| D9 | FIX 카운터 | 세션 내 메모리 + 코멘트 기록 | 같은 Architect 왕복 내에서만 의미, custom field 불필요 |
| D10 | 종결 | Story=PR merge 자동 / Epic=사용자 명시 | 실제 "반영 완료" 시점 기준 |
| D11 | 생성 시점 | Epic=요건 접수 즉시 / Story=scope 확정 순간 | 요건 단계 활동도 Jira에 기록, 예비 Story 남발 방지 |

## 3. 아키텍처

### 3.1 산출물 역할 분담
```
┌─ Jira (워크플로우 로그) ─────────────────┐
│ Epic: 사용자 요건 1건                      │
│  ├─ Story-1: Change Plan 1건 (≈ PR 1건)   │
│  │   └─ 코멘트: 단계별 이정표              │
│  ├─ Story-2: ...                          │
│  └─ Story-N: ...                          │
└──────────────────────────────────────────┘
           │ 링크 (코멘트에 경로 명시)
           ▼
┌─ Git Repo ──────┐  ┌─ Confluence ───┐  ┌─ GitHub PR ────┐
│ Change Plan md  │  │ ADR 페이지      │  │ 코드 리뷰 대화  │
│ (설계 원문)     │  │ (불변 결정)     │  │ (diff 리뷰)     │
└────────────────┘  └────────────────┘  └────────────────┘
```

### 3.2 전체 흐름
```
[사용자 요건 접수]
    ↓
[Epic 생성, 상태=요건] ← 오케스트레이터
    ↓
[PMAgent scope 분해]
    ↓
    ┌──────── Story-1 생성 (분해 시 확정 단위만) ────────┐
    │                                                    │
    │  요건 → 설계 → 구현 → 리뷰-Step1 → 테스트-Step2   │
    │                                                    │
    │  PR 오픈 [MCTRADER-N] → PR merge → 상태=완료     │
    │                                                    │
    └────────────────────────────────────────────────────┘
    ↓
    (Story-2, Story-N 동일 패턴으로 순차 or 병렬 진행)
    ↓
[사용자 "요건 끝" 확인] → Epic 완료
```

### 3.3 Epic 생명주기

| 시점 | 동작 | 상태 | 주요 label |
|---|---|---|---|
| 사용자 요건 접수 | 오케스트레이터가 Epic 생성 (제목=사용자 원문 요약) | `해야 할 일` | — |
| PMAgent scope 분해 직후 | Epic 본문 업데이트 + 상태 전이 | → `진행 중` | — |
| Story 진행 중 | Epic 상태·label 유지 (Story 단위 추적이므로 Epic은 scope 인지만) | `진행 중` | — |
| 모든 Story `완료` + 사용자 "요건 끝" | 오케스트레이터가 Epic `완료` 전이 | `완료` | — |

### 3.4 Story 생명주기

Jira 기본 3-state(`해야 할 일`/`진행 중`/`완료`)를 유지하고 **phase label**로 단계 표현. 한 Story는 현재 단계 label 1개만 보유(교체 방식).

| 시점 | 동작 | 상태 | phase label |
|---|---|---|---|
| PMAgent scope 확정 순간 | Story 생성 + Epic link + `phase:요건` label | `해야 할 일` → `진행 중` | `phase:요건` |
| PMO 통합 명세서 확정 | 코멘트 기록 | `진행 중` | `phase:요건` 유지 |
| Architect Change Plan 확정 | docs/change-plans/<slug>.md 저장, label 교체, 코멘트 기록 | `진행 중` | → `phase:설계` |
| 구현 병렬 스폰 (QADev + Dev/Engineer) | label 교체, 코멘트 기록 | `진행 중` | → `phase:구현` |
| Architect QADev 매핑표 감사 통과 | 코멘트 기록 | `진행 중` | `phase:구현` 유지 |
| Step1 시작 (Claude+Codex 리뷰) | label 교체, 코멘트 기록 | `진행 중` | → `phase:리뷰-step1` |
| Step1 PASS | label 교체, 코멘트 기록 | `진행 중` | → `phase:테스트-step2` |
| Step2 PASS + PR 오픈 | PR 제목·본문에 [MCTRADER-N] 주입 | `진행 중` | `phase:테스트-step2` 유지 |
| PR merged | GitHub for Jira가 감지해 전이 | → `완료` | 마지막 label 유지(감사용) |

보드 대신 **JQL 필터**로 단계별 모니터링: `project = MCTRADER AND labels = "phase:리뷰-step1"` 등.

### 3.5 FIX 루프 표현

- **Step1 P0/P1 발견**: label 되돌림 `phase:리뷰-step1 → phase:구현`, `fix:step1-retry` label 추가, 코멘트 `[FIX #N] <Reviewer>: <원인 요약>`
- **Step2 FAIL**: label 되돌림 `phase:테스트-step2 → phase:구현`, `fix:step2-retry` label 추가, 코멘트 `[FIX #N] Tester: <실패 테스트 요약>`
- **카운터**: 오케스트레이터 세션 메모리 (Step1 최대 3회, Step2 무제한). Jira에는 코멘트 prefix `[FIX #N]`와 `fix:*` label로 시각화
- **Step2 FAIL 후 재진입 Step1에서 P0/P1 발견 시**: 세션 카운터 리셋, 새 리뷰로 취급

## 4. 코멘트 표준

### 4.1 형식

모든 코멘트는 **1줄 prefix + 2-5줄 TL;DR + 원문 링크** 구조:

```
[<phase>] <AgentName>: <한 줄 요약>

<추가 설명 2-5줄>

원문: <경로 또는 URL>
```

### 4.2 Phase prefix 8종 (고정 사전)

| Prefix | 사용 시점 |
|---|---|
| `[요건]` | PMAgent / PMOAgent / RequirementsAnalyst / Researcher 보고 |
| `[설계]` | Architect / Refactor 결정·제안 |
| `[구현]` | QADev / Frontend·Backend Dev / DataEng·ServerEng 진행 |
| `[리뷰-Step1]` | ClaudeReviewer / CodexReviewer severity |
| `[테스트-Step2]` | TesterAgent PASS/FAIL |
| `[FIX #N]` | FIX 루프 원인·계획 갱신 (N은 세션 내 증분) |
| `[사용자]` | 사용자 에스컬레이션·확인 기록 |
| `[완료]` | DocsAgent 후속 작업 / Story 클로징 |

### 4.3 TL;DR 요구사항

모든 에이전트(코멘트 권한 유무 불문)는 보고서 맨 앞에 **1-3줄 TL;DR**을 필수로 포함한다. 오케스트레이터 경유 에이전트의 경우 오케스트레이터가 이 TL;DR을 그대로 코멘트로 복사한다.

## 5. Labels 체계

| 카테고리 | 예시 | 비고 |
|---|---|---|
| `phase:*` | `phase:요건`, `phase:설계`, `phase:구현`, `phase:리뷰-step1`, `phase:테스트-step2` | 현재 단계 1개만 부여 (상태와 중복되나 JQL 필터 편의) |
| `component:*` | `component:collector`, `component:dashboard`, `component:strategy`, `component:backtest` | Story 단위 1~N개 |
| `adr:*` | `adr:017`, `adr:020` | 관련 ADR 참조, 복수 허용 |
| `branch:*` | `branch:A`, `branch:B`, `branch:A+B` | 구현 분기 결정 |
| `fix:*` | `fix:step1-retry`, `fix:step2-retry` | FIX 발생 시 추가 |
| `migrated-from-repo` | (기존 값 그대로) | 2026-04-23 이관분만 |

## 6. 권한 체계

### 6.1 오케스트레이터 책임
- Epic/Story 생성: `mcp__atlassian__createJiraIssue`
- 상태 전이: `mcp__atlassian__transitionJiraIssue`
- Labels 관리: `mcp__atlassian__editJiraIssue`
- 구현·보고 에이전트 TL;DR 복사 코멘트: `mcp__atlassian__addCommentToJiraIssue`
- PR prefix 주입: `gh pr create --title "[MCTRADER-N] ..."`

### 6.2 직접 코멘트 권한 (9개 에이전트)

다음 에이전트 md frontmatter `permissions.allow`에 `mcp__atlassian__addCommentToJiraIssue` 추가:

1. PMAgent
2. PMOAgent
3. ArchitectAgent
4. DeveloperPLAgent
5. EngineerPLAgent
6. QualityPLAgent
7. RefactorAgent
8. ClaudeReviewerAgent
9. CodexReviewerAgent

각 에이전트는 오케스트레이터로부터 Story 키(`MCTRADER-N`)를 프롬프트로 전달받고, 결정·협업 메시지를 직접 코멘트로 기록한다.

### 6.3 오케스트레이터 경유 에이전트

Jira 권한 없음, 오케스트레이터가 TL;DR 복사:
- RequirementsAnalystAgent (GPT-5.4 래퍼)
- ResearcherAgent
- QADeveloperAgent
- FrontendDeveloperAgent, BackendDeveloperAgent
- DataEngineerAgent, ServerEngineerAgent
- TesterAgent
- DocsAgent

이들의 출력은 TL;DR 1-3줄을 맨 앞에 강제 포함해야 한다(에이전트 정의에 명시).

## 7. GitHub 연계

### 7.1 커밋·PR 규칙

- **모든 구현 커밋**: `[MCTRADER-N] <type>: <summary>` 형식
- **PR 제목**: `[MCTRADER-N] <Story 요약>`
- **PR 본문 상단**: `Jira: https://mctrader.atlassian.net/browse/MCTRADER-N` 자동 포함
- **Smart Commits** 활용 가능: `Fixes MCTRADER-N`을 마지막 커밋에 포함하면 merge 시 자동 `완료` 전이

### 7.2 오케스트레이터가 prefix 자동 주입

구현 에이전트(Dev/Engineer/QADev)는 `[MCTRADER-N]` 형식을 몰라도 됨. 오케스트레이터가:
- 구현 에이전트 스폰 시 프롬프트에 "커밋 메시지 본문만 작성 (prefix 제외)"
- 에이전트 완료 후 오케스트레이터가 `git commit -m "[MCTRADER-N] ${body}"` 형태로 주입

또는 각 에이전트가 직접 `[MCTRADER-N]` 포함해 커밋하도록 프롬프트에 Story 키 전달 — 어느 쪽이든 **Story 키는 프롬프트로 주입**.

### 7.3 GitHub for Jira 앱

- 설치: https://marketplace.atlassian.com/apps/1219592/github-for-jira (무료)
- 설정: `mctrader` 조직 연결, 모든 레포 범위
- 기대 동작:
  - 커밋·PR·브랜치에 `MCTRADER-N` 포함 시 Jira Story 우측 패널에 자동 표시
  - PR merged 이벤트가 Story 상태 `완료` 전이 트리거 (Smart Commits 설정 경우)

## 8. Admin 사전 설정 (1회성)

### 8.1 Jira 워크플로우

현재 기본 3-state 그대로 유지: `해야 할 일 → 진행 중 → 완료`.

**Custom Status 추가는 철회**. 2026-04-23 확인 결과, 현재 Jira 구독/프로젝트 템플릿에서 In Progress 카테고리에 복수 status 추가가 불가. Phase 추적은 **labels로 대체**:
- `phase:요건`, `phase:설계`, `phase:구현`, `phase:리뷰-step1`, `phase:테스트-step2`
- 한 Story는 현재 단계 label 1개만 보유(교체 방식)
- FIX 루프: `fix:step1-retry`, `fix:step2-retry` label 누적

대시보드는 JQL 필터로 대체:
- "현재 리뷰 중": `project = MCTRADER AND labels = "phase:리뷰-step1"`
- "FIX 대상": `project = MCTRADER AND labels in ("fix:step1-retry", "fix:step2-retry")`

별도 관리자 설정 불필요.

### 8.2 GitHub for Jira 앱 설치

1. 위 URL에서 `Get it now` → 관리자 계정 인증
2. GitHub 쪽: `mctrader` 조직에 앱 설치 승인
3. 레포 범위: `mctrader/mctrader` 포함
4. 설정 완료 후 샘플 커밋(`[MCTRADER-1] test: jira integration`)으로 연동 검증

### 8.3 Epic issue type 확인

기존 프로젝트에 `에픽`(Epic) 타입 존재 (ID 10009 확인됨 from migration session). 추가 작업 없음.

### 8.4 이관분(MCTRADER-1~3) 처리

현재 이관된 3건(label `migrated-from-repo`)은 Epic 없이 독립 Story로 유지. 신규 Story와 구분됨.

## 9. CLAUDE.md / 에이전트 정의 변경 범위

### 9.1 CLAUDE.md 추가 섹션

```markdown
## Jira 워크플로우 (MCTRADER 프로젝트)

- Epic: 사용자 요건 1건. 오케스트레이터가 PMAgent 스폰 직전 생성
- Story: PR 1건 = Change Plan 1건. PMAgent scope 분해 시 확정 단위만 생성
- 상태: 요건 → 설계 → 구현 → 리뷰-Step1 → 테스트-Step2 → 완료
- FIX 루프: 상태 되돌림 + `[FIX #N]` prefix 코멘트
- 커밋·PR: `[MCTRADER-N]` prefix 필수
- 직접 코멘트 권한: PM/PMO/Architect/DevPL/EngPL/QualityPL/Refactor/Claude·CodexReviewer (9)
- 오케스트레이터 경유: Analyst/Researcher/QADev/Dev/Engineer/Tester/Docs (TL;DR 요구)
- 원문 위치: 설계=docs/change-plans/, 결정=Confluence ADR, 코드 리뷰=PR (Jira는 요약/링크만)
```

### 9.2 에이전트 정의 수정

- **9개 직접 코멘트 권한 에이전트**: `permissions.allow`에 `mcp__atlassian__addCommentToJiraIssue` 추가
- **오케스트레이터 경유 에이전트**: 프롬프트 출력 형식 표준에 "맨 앞 1-3줄 TL;DR 필수" 명시

### 9.3 MCP settings 추가

`.claude/settings.local.json`에 추가:
- `mcp__atlassian__addCommentToJiraIssue` (코멘트 권한 에이전트용 + 오케스트레이터 공용)

## 10. 에러 처리 / 롤백

- **Jira API 실패(네트워크·rate limit)**: 해당 코멘트/전이는 skip, 오케스트레이터 세션 로그에 기록 → 재시도 or 수동 보정
- **Epic/Story 생성 실패**: 진행 차단 후 사용자 알림 (Jira 접근 불가 시 전체 워크플로우 중단)
- **GitHub for Jira 자동 전이 실패**: 오케스트레이터가 PR merge 이벤트 감지 후 명시적 `transitionJiraIssue` fallback
- **직접 코멘트 권한 에이전트 실패**: 에이전트가 코멘트 실패 시 오케스트레이터에게 보고서로 반환 → 오케스트레이터가 재시도

## 11. 검증

### 11.1 설계 검증 포인트
- [ ] Epic 1건 + Story 2건 이상 구성의 샘플 시나리오 리허설 (작은 PR 2개로 구성된 기능)
- [ ] FIX 루프 #1~#3 시나리오 — Jira 코멘트 스레드 가독성
- [ ] PR merge 시 자동 전이 정상 (GitHub for Jira 앱 설정 후)

### 11.2 운영 지표
- Epic당 평균 Story 수 (1~5 정상, >10 scope 재검토)
- Step1 FIX 카운트 분포 (0~1 정상, 3회 도달 = 설계 재검토 필요)
- Story 생성부터 완료까지 평균 소요 시간
- Jira 코멘트 누락률 (오케스트레이터 에러로 기록 실패한 경우)

## 12. 범위 외 (Out of Scope)

- **Jira Custom Field** (FIX counter 등): 세션 메모리로 충분 (Q8 D)
- **Subtasks**: 1 Story = 1 PR 원칙이라 구현 분기(Dev/Engineer)는 Story 내 병렬, Subtask 불필요
- **Jira Automation 규칙 (JQL 기반 자동 상태 전이)**: GitHub for Jira 기본 동작으로 충분, 필요 시 별도 설계
- **ADR 생성 시 Jira 연동**: ADR은 Confluence SSOT, Jira 코멘트에서 `adr:NNN` label로 참조만
- **Agile 도구(Sprint, Velocity, Burndown)**: 현재 단일 작업자 프로젝트라 불필요
