# Jira 기반 에이전트 워크플로우 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 에이전트 팀의 의사결정·협업 과정을 Jira Epic/Story/코멘트로 영속화하고, 오케스트레이터와 9개 PL/결정자 에이전트의 행동 규칙을 CLAUDE.md·에이전트 정의·settings에 반영한다.

**Architecture:** 설정 변경 중심(코드 추가 없음). Jira 관리자 UI 1회 설정(custom status + GitHub for Jira 앱) + CLAUDE.md 워크플로우 섹션 추가 + 9개 에이전트에 `mcp__atlassian__addCommentToJiraIssue` 권한 부여 + 18개 에이전트 전원에 TL;DR 출력 규칙 명시. 검증은 실제 MCP 호출로 Epic/Story 샘플 생성.

**Tech Stack:** Claude Code agent md (YAML frontmatter + markdown), `.claude/settings.local.json`, Atlassian MCP tools, GitHub for Jira 앱.

**Spec:** [docs/superpowers/specs/2026-04-23-jira-agent-workflow-design.md](../specs/2026-04-23-jira-agent-workflow-design.md)

---

## Task 1: 사전 준비 — Jira Custom Status + GitHub for Jira 앱 (사용자 수동)

**Files:** 외부 시스템만 변경

- [ ] **Step 1.1: Jira 워크플로우에 Custom Status 5종 추가**

사용자 수동 작업 (Admin 권한). 웹 UI 경로:
1. https://mctrader.atlassian.net/jira/software/projects/MCTRADER/settings/workflows
2. 현재 워크플로우(기본 3-state) `Edit`
3. 다음 5개 status 생성, 모두 category = `In Progress`:
   - `요건`
   - `설계`
   - `구현`
   - `리뷰-Step1`
   - `테스트-Step2`
4. 전이 규칙 추가:
   - `해야 할 일` → `요건`, `설계`, `구현`, `리뷰-Step1`, `테스트-Step2` (모두 허용)
   - 진행 중 status 간 양방향 전이 (FIX 루프 되돌림용)
   - 진행 중 status → `완료` (어느 단계에서든 클로징 가능)
5. `Publish workflow` 저장

검증: `mcp__atlassian__getTransitionsForJiraIssue(issueIdOrKey="MCTRADER-1")` 호출 시 응답에 5개 신규 상태가 포함되어야 함. 미포함이면 워크플로우 편집 재시도.

- [ ] **Step 1.2: GitHub for Jira 앱 설치**

사용자 수동 작업 (Admin 권한).
1. https://marketplace.atlassian.com/apps/1219592/github-for-jira/cloud/overview
2. `Get it now` → `mctrader.atlassian.net`에 설치 승인
3. GitHub 측: `mctrader` 조직 선택 → 앱 설치 승인
4. 레포 범위 설정: `mctrader/mctrader` 포함
5. Jira 쪽 앱 설정에서 연결 확인 (GitHub 연결 상태 "Connected")

검증: `gh api repos/mctrader/mctrader/installations 2>&1` 로 Jira 앱 설치 확인 가능. 또는 Jira `MCTRADER-1` 이슈 패널에 "Development" 섹션이 노출되는지 웹 UI에서 확인.

- [ ] **Step 1.3: 상태 전이 ID 수집**

Step 1.1 완료 후 새 상태들의 transition ID를 수집해 기록 (오케스트레이터가 후속 전이 시 참조).

Run:
```python
# 세션 내에서
mcp__atlassian__getTransitionsForJiraIssue(
  cloudId="9dfd8e80-9cc3-4f30-adca-905478a2d628",
  issueIdOrKey="MCTRADER-1"
)
```
Expected: 기존 3개 transition(`해야 할 일`, `진행 중`, `완료` = 각각 id 11, 21, 31) + 신규 5개. 결과에서 다음 매핑 기록:
- `요건` → transition id = ?
- `설계` → transition id = ?
- `구현` → transition id = ?
- `리뷰-Step1` → transition id = ?
- `테스트-Step2` → transition id = ?

이 매핑을 Task 2에서 CLAUDE.md에 기록하고, 오케스트레이터가 스폰 시점마다 참조.

**게이트**: Step 1.1~1.3 모두 완료 전까지 Task 2 이후 진행 금지.

---

## Task 2: CLAUDE.md에 Jira 워크플로우 섹션 추가

**Files:**
- Modify: `CLAUDE.md` (섹션 삽입 위치: `## ADR (Confluence Pages SSOT)` 섹션 앞 또는 `## 버그 기록 (Jira)` 섹션 바로 아래)

- [ ] **Step 2.1: CLAUDE.md 현재 상태 확인**

Read CLAUDE.md 전체 → "## 버그 기록 (Jira)" 섹션 라인 번호 확인. (migration 이후 L120 근처 예상)

- [ ] **Step 2.2: "## Jira 워크플로우" 섹션을 "## 버그 기록 (Jira)" 바로 아래에 삽입**

Edit CLAUDE.md, 추가할 내용:

```markdown
## Jira 워크플로우 (MCTRADER 프로젝트)

사용자 요건 접수부터 PR merge까지의 모든 의사결정·협업은 Jira에 영속 기록한다.

### 계층
- **Epic** = 사용자 요건 1건. 오케스트레이터가 PMAgent 스폰 직전 생성
- **Story** = PR 1건 (= Change Plan 1건). PMAgent scope 분해 시 확정된 독립 작업 단위만 생성

### 상태 흐름
```
해야 할 일 → 요건 → 설계 → 구현 → 리뷰-Step1 → 테스트-Step2 → 완료
```
Story 각각이 자체 full cycle을 가진다. Epic 상태는 `해야 할 일` → `요건`(scope 분해) → `진행 중`(첫 Story 생성) → `완료`(사용자 확인)로만 이동.

### 상태 전이 ID (Task 1.3에서 수집)
- `요건` → transition id `<TID_REQ>` (Task 1.3 결과로 교체)
- `설계` → `<TID_DESIGN>`
- `구현` → `<TID_IMPL>`
- `리뷰-Step1` → `<TID_REVIEW>`
- `테스트-Step2` → `<TID_TEST>`
- `완료` → `31`
- `해야 할 일` → `11`, `진행 중` → `21` (기본)

### FIX 루프
- **Step1 P0/P1** 또는 **Step2 FAIL** 시: 상태 되돌림 `리뷰-Step1|테스트-Step2 → 구현` + 코멘트 `[FIX #N] <Agent>: <원인>`
- 카운터는 오케스트레이터 세션 메모리 (Step1 최대 3회, Step2 무제한)
- Step2 FAIL 후 재진입한 Step1에서 P0/P1 발견 시 Step1 카운터 리셋

### 코멘트 규칙
모든 코멘트는 `[<phase>] <AgentName>: <한 줄 요약>` prefix + 2-5줄 TL;DR + 원문 링크(Change Plan md / ADR URL / PR URL) 형식.

**Phase prefix 8종**: `[요건]`, `[설계]`, `[구현]`, `[리뷰-Step1]`, `[테스트-Step2]`, `[FIX #N]`, `[사용자]`, `[완료]`

### 코멘트 권한
- **직접 기록(9)**: PMAgent, PMOAgent, ArchitectAgent, DeveloperPLAgent, EngineerPLAgent, QualityPLAgent, RefactorAgent, ClaudeReviewerAgent, CodexReviewerAgent
- **오케스트레이터 경유(9)**: RequirementsAnalyst, Researcher, QADev, Frontend/Backend/DataEng/ServerEng Dev, Tester, DocsAgent — 보고서 맨 앞 TL;DR 1-3줄을 오케스트레이터가 그대로 복사

### GitHub 연계
- 모든 구현 커밋: `[MCTRADER-N] <type>: <summary>` prefix
- PR 제목: `[MCTRADER-N] <Story 요약>`
- PR 본문: `Jira: https://mctrader.atlassian.net/browse/MCTRADER-N` 상단 포함
- GitHub for Jira 앱이 PR merge 시 Story 자동 `완료` 전이

### Labels 체계
- `phase:*` (현재 단계 1개: `phase:요건` / `phase:설계` / `phase:구현` / `phase:리뷰-step1` / `phase:테스트-step2`)
- `component:*` (Story 단위: `component:collector`, `component:dashboard`, `component:strategy`, `component:backtest`)
- `adr:NNN` (관련 ADR 참조, 복수 허용)
- `branch:A` / `branch:B` / `branch:A+B` (구현 분기 결정)
- `fix:step1-retry` / `fix:step2-retry` (FIX 발생 시 추가)

### 원문 위치
Jira는 **워크플로우 로그**만. 원문은 각 도구 유지:
- 설계: `docs/change-plans/<slug>.md`
- 결정: Confluence ADR 페이지
- 코드 리뷰: GitHub PR 설명/코멘트
```

- [ ] **Step 2.3: Task 1.3 결과로 transition ID placeholder 치환**

Task 1.3에서 수집한 실제 transition ID로 `<TID_REQ>`, `<TID_DESIGN>`, `<TID_IMPL>`, `<TID_REVIEW>`, `<TID_TEST>` 5곳을 Edit으로 실제 숫자로 교체.

- [ ] **Step 2.4: 검증**

Run:
```bash
grep -n "Jira 워크플로우\|TID_" /Users/1111971/workspace/mctrader/CLAUDE.md
```
Expected:
- "## Jira 워크플로우 (MCTRADER 프로젝트)" 섹션 헤더 발견
- "<TID_*>" placeholder는 **0건** (모두 실제 숫자로 교체됨)

---

## Task 3: `.claude/settings.local.json`에 `addCommentToJiraIssue` 권한 추가

**Files:**
- Modify: `.claude/settings.local.json`

- [ ] **Step 3.1: 현재 settings.local.json 읽기**

Read `.claude/settings.local.json` 전체 → Atlassian 권한 블록 위치 확인.

- [ ] **Step 3.2: `mcp__atlassian__addCommentToJiraIssue` 추가**

Edit `.claude/settings.local.json`, `"mcp__atlassian__transitionJiraIssue"` 바로 아래에 추가:

Old:
```
      "mcp__atlassian__transitionJiraIssue",
      "mcp__atlassian__getTransitionsForJiraIssue",
```

New:
```
      "mcp__atlassian__transitionJiraIssue",
      "mcp__atlassian__getTransitionsForJiraIssue",
      "mcp__atlassian__addCommentToJiraIssue",
```

- [ ] **Step 3.3: JSON 유효성 검증**

Run:
```bash
python3 -m json.tool /Users/1111971/workspace/mctrader/.claude/settings.local.json > /dev/null && echo "OK"
```
Expected: `OK`

---

## Task 4: 결정/PL 에이전트 9개에 코멘트 권한 + Story 키 인지 규칙 추가

**Files:**
- Modify: `.claude/agents/PMAgent.md`
- Modify: `.claude/agents/PMOAgent.md`
- Modify: `.claude/agents/ArchitectAgent.md`
- Modify: `.claude/agents/DeveloperPLAgent.md`
- Modify: `.claude/agents/EngineerPLAgent.md`
- Modify: `.claude/agents/QualityPLAgent.md`
- Modify: `.claude/agents/RefactorAgent.md`
- Modify: `.claude/agents/ClaudeReviewerAgent.md`
- Modify: `.claude/agents/CodexReviewerAgent.md`

각 에이전트마다 다음 2가지 변경:
**A. permissions.allow에 `mcp__atlassian__addCommentToJiraIssue` 추가**
**B. 에이전트 본문 하단에 "Jira 코멘트 규약" 섹션 추가**

### Template for 변경 B (모든 9개 에이전트 공통)

에이전트 md 본문 맨 끝(파일 마지막 `---` 구분선 없이, 마지막 섹션 뒤)에 추가:

```markdown

## Jira 코멘트 규약

오케스트레이터가 프롬프트로 전달하는 Jira Story 키(`MCTRADER-N`)로 결정·협업 메시지를 직접 기록한다. 보고서 맨 앞 1-3줄 TL;DR은 필수이며, 이 TL;DR을 그대로 `mcp__atlassian__addCommentToJiraIssue`의 `commentBody`에 전달한다.

형식: `[<phase>] <에이전트명>: <한 줄 요약>\n\n<2-5줄 상세>\n\n원문: <경로 또는 URL>`

- phase prefix 8종 중 현재 작업에 해당하는 것을 선택 (CLAUDE.md `## Jira 워크플로우` 참조)
- 원문 링크: 설계 변경은 `docs/change-plans/<slug>.md:L<line>`, 결정은 Confluence ADR URL, 코드 리뷰는 PR URL
- Story 키 미전달 시: 기록하지 않고 오케스트레이터에게 보고서만 반환
```

### 4.1 PMAgent

- [ ] **Step 4.1.1: PMAgent.md permissions에 추가**

Current block:
```yaml
permissions:
  deny:
    - Write
    - Edit
```

Edit to:
```yaml
permissions:
  allow:
    - mcp__atlassian__addCommentToJiraIssue
  deny:
    - Write
    - Edit
```

- [ ] **Step 4.1.2: 본문 하단에 Jira 코멘트 규약 섹션 추가**

위 Template 그대로 Edit으로 파일 끝에 Append.

- [ ] **Step 4.1.3: 검증**
```bash
grep -q "mcp__atlassian__addCommentToJiraIssue" .claude/agents/PMAgent.md && \
  grep -q "Jira 코멘트 규약" .claude/agents/PMAgent.md && echo OK
```
Expected: `OK`

### 4.2 PMOAgent

- [ ] **Step 4.2.1**: PMOAgent.md permissions 확인 후 `mcp__atlassian__addCommentToJiraIssue` 추가. 이미 `allow` 블록이 있을 수 있으므로 기존 배열 끝에 append.

- [ ] **Step 4.2.2**: 본문 하단에 Template 섹션 Append.

- [ ] **Step 4.2.3**: grep 검증 (위와 동일 패턴).

### 4.3 ArchitectAgent

- [ ] **Step 4.3.1**: ArchitectAgent.md current block (permissions):
```yaml
permissions:
  deny:
    - Write
    - Edit
```
Edit to:
```yaml
permissions:
  allow:
    - mcp__atlassian__addCommentToJiraIssue
  deny:
    - Write
    - Edit
```

- [ ] **Step 4.3.2**: 본문 하단 Template 섹션 Append.

- [ ] **Step 4.3.3**: grep 검증.

### 4.4 DeveloperPLAgent

- [ ] **Step 4.4.1**: 기존 allow 블록에 `mcp__atlassian__addCommentToJiraIssue` 한 줄 추가.

현재:
```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
```
수정 후:
```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - mcp__atlassian__addCommentToJiraIssue
```

- [ ] **Step 4.4.2**: 본문 하단 Template 섹션 Append.

- [ ] **Step 4.4.3**: grep 검증.

### 4.5 EngineerPLAgent

- [ ] **Step 4.5.1**: PMAgent와 동일 패턴 (deny만 있는 블록에 allow 추가).

Current:
```yaml
permissions:
  deny:
    - Write
    - Edit
```
Edit to:
```yaml
permissions:
  allow:
    - mcp__atlassian__addCommentToJiraIssue
  deny:
    - Write
    - Edit
```

- [ ] **Step 4.5.2**: Template 섹션 Append.

- [ ] **Step 4.5.3**: grep 검증.

### 4.6 QualityPLAgent

- [ ] **Step 4.6.1**: 기존 allow 블록에 append.

Current:
```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
  deny:
    - Write
    - Edit
```
Edit to:
```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - mcp__atlassian__addCommentToJiraIssue
  deny:
    - Write
    - Edit
```

- [ ] **Step 4.6.2**: Template 섹션 Append.

- [ ] **Step 4.6.3**: grep 검증.

### 4.7 RefactorAgent

- [ ] **Step 4.7.1**: allow 블록 끝에 append.

기존 allow: `Read, Grep, Glob, Bash(find *), Bash(ls *), Bash(.venv/bin/python *)`에 `mcp__atlassian__addCommentToJiraIssue` 한 줄 추가.

- [ ] **Step 4.7.2**: Template 섹션 Append.

- [ ] **Step 4.7.3**: grep 검증.

### 4.8 ClaudeReviewerAgent

- [ ] **Step 4.8.1**: allow 블록 끝에 append (기존 `WebFetch` 뒤).

- [ ] **Step 4.8.2**: Template 섹션 Append.

- [ ] **Step 4.8.3**: grep 검증.

### 4.9 CodexReviewerAgent

- [ ] **Step 4.9.1**: allow 블록 끝에 append.

- [ ] **Step 4.9.2**: Template 섹션 Append.

- [ ] **Step 4.9.3**: grep 검증.

### 4.10 전체 검증

- [ ] **Step 4.10.1: 9개 에이전트 모두 권한·섹션 보유 확인**

Run:
```bash
for a in PMAgent PMOAgent ArchitectAgent DeveloperPLAgent EngineerPLAgent QualityPLAgent RefactorAgent ClaudeReviewerAgent CodexReviewerAgent; do
  has_perm=$(grep -c "mcp__atlassian__addCommentToJiraIssue" /Users/1111971/workspace/mctrader/.claude/agents/$a.md)
  has_section=$(grep -c "Jira 코멘트 규약" /Users/1111971/workspace/mctrader/.claude/agents/$a.md)
  printf "%-25s perm=%s section=%s\n" "$a" "$has_perm" "$has_section"
done
```
Expected: 9개 모두 `perm=1 section=1`.

---

## Task 5: 오케스트레이터 경유 에이전트 9개에 TL;DR 출력 규칙 추가

**Files:**
- Modify: `.claude/agents/RequirementsAnalystAgent.md`
- Modify: `.claude/agents/ResearcherAgent.md`
- Modify: `.claude/agents/QADeveloperAgent.md`
- Modify: `.claude/agents/FrontendDeveloperAgent.md`
- Modify: `.claude/agents/BackendDeveloperAgent.md`
- Modify: `.claude/agents/DataEngineerAgent.md`
- Modify: `.claude/agents/ServerEngineerAgent.md`
- Modify: `.claude/agents/TesterAgent.md`
- Modify: `.claude/agents/DocsAgent.md`

각 에이전트 본문 하단에 다음 섹션 Append:

```markdown

## TL;DR 출력 규약 (Jira 오케스트레이터 경유)

모든 보고서는 맨 앞 1-3줄 TL;DR로 시작한다. 오케스트레이터가 이 TL;DR을 Jira Story 코멘트에 복사해 워크플로우 로그로 기록한다.

형식:
```
TL;DR: <한 줄 결과 요약>
- <추가 포인트 1>
- <추가 포인트 2>

<상세 보고서 본문…>
```

TL;DR 누락 시 오케스트레이터가 보고서를 반려하고 재요청할 수 있다.
```

### 5.1~5.9 각 에이전트별 반복

- [ ] **Step 5.1.1** ~ **Step 5.9.1**: 각 에이전트 파일 끝에 위 TL;DR 섹션 Append
- [ ] **Step 5.10: 검증**

Run:
```bash
for a in RequirementsAnalystAgent ResearcherAgent QADeveloperAgent FrontendDeveloperAgent BackendDeveloperAgent DataEngineerAgent ServerEngineerAgent TesterAgent DocsAgent; do
  has=$(grep -c "TL;DR 출력 규약" /Users/1111971/workspace/mctrader/.claude/agents/$a.md)
  printf "%-30s tldr=%s\n" "$a" "$has"
done
```
Expected: 9개 모두 `tldr=1`.

---

## Task 6: 통합 스모크 테스트 — 샘플 Epic + Story + 코멘트 생성

**Files:** 외부 시스템 (Jira MCTRADER)

목적: Jira 설정·권한·워크플로우가 설계대로 동작하는지 실제 MCP 호출로 확인.

- [ ] **Step 6.1: 샘플 Epic 생성**

Tool:
```python
mcp__atlassian__createJiraIssue(
  cloudId="9dfd8e80-9cc3-4f30-adca-905478a2d628",
  projectKey="MCTRADER",
  issueTypeName="에픽",
  summary="[Smoke Test] Jira 워크플로우 도입 검증",
  description="설계서 docs/superpowers/specs/2026-04-23-jira-agent-workflow-design.md 검증용 샘플 Epic.\n\n본 Epic은 테스트 후 삭제 또는 '완료' 처리.",
  additional_fields={"labels": ["smoke-test", "migration-verification"]}
)
```
Expected: `MCTRADER-<N>` 반환 (N>=4). 반환된 키 기록.

- [ ] **Step 6.2: Epic 상태 `요건` 전이**

Tool:
```python
mcp__atlassian__transitionJiraIssue(
  cloudId="9dfd8e80-9cc3-4f30-adca-905478a2d628",
  issueIdOrKey="<Epic 키>",
  transition={"id": "<TID_REQ>"}   # Task 1.3 수집값
)
```
Expected: 성공. 이후 `getJiraIssue` 응답 `status.name == "요건"` 확인.

- [ ] **Step 6.3: Story 생성 + Epic link + 초기 상태 `요건`**

Tool:
```python
mcp__atlassian__createJiraIssue(
  cloudId="9dfd8e80-9cc3-4f30-adca-905478a2d628",
  projectKey="MCTRADER",
  issueTypeName="작업",
  summary="[Smoke Test] 샘플 Story 1 — Jira 연동 검증",
  description="Epic: <Epic 키>\n\n샘플 Story — Change Plan 없이 Jira 워크플로우만 테스트.",
  additional_fields={
    "labels": ["smoke-test", "phase:요건"],
    "customfield_10014": "<Epic 키>"  # Epic link 필드 (프로젝트별 다를 수 있음, 확인 필요)
  },
  transition={"id": "<TID_REQ>"}
)
```
Expected: `MCTRADER-<M>` 반환. `getJiraIssue`로 `status.name == "요건"` + labels 확인.

참고: `customfield_10014`는 team-managed project의 "상위 항목" 필드. 실제 ID는 `getJiraIssueTypeMetaWithFields`로 조회해 확정. 확인 안 되면 Epic link는 수동 UI 연결로 대체해도 테스트 목적 달성.

- [ ] **Step 6.4: Story에 샘플 코멘트 3개 추가 (단계 이정표 시뮬레이션)**

각 코멘트는 `addCommentToJiraIssue`로:

코멘트 1:
```
[요건] PMOAgent: scope 확정 — 단일 기능 개선

SMOKE TEST — 실제 PMO 보고 아님. Jira 연동 검증용.

원문: (스모크 테스트, 원문 없음)
```

코멘트 2:
```
[설계] ArchitectAgent: 분기 B 선택, 단일 파일 수정

SMOKE TEST.

원문: docs/change-plans/smoke-test.md (없음)
```

코멘트 3:
```
[완료] 오케스트레이터: 스모크 테스트 성공

Jira 워크플로우·권한·GitHub 연동 모두 정상. 본 이슈는 Close 처리.
```

- [ ] **Step 6.5: Story·Epic 상태를 `완료`로 전이 (정리)**

```python
mcp__atlassian__transitionJiraIssue(
  cloudId="...",
  issueIdOrKey="<Story 키>",
  transition={"id": "31"}  # 완료
)
mcp__atlassian__transitionJiraIssue(
  cloudId="...",
  issueIdOrKey="<Epic 키>",
  transition={"id": "31"}
)
```

검증: `getJiraIssue`로 둘 다 `status.name == "완료"`.

- [ ] **Step 6.6: GitHub for Jira 연계 확인 (선택)**

선택적 — 샘플 Epic/Story는 코드 변경이 없어 GitHub 연계는 실제 작업에서 검증됨. 스모크 단계에서는 건너뜀.

---

## Task 7: 변경 커밋 + GitHub push

**Files:**
- Stage: `CLAUDE.md`, `.claude/settings.local.json`, `.claude/agents/*.md`

- [ ] **Step 7.1: 변경 파일 확인**

Run:
```bash
git status
```
Expected: CLAUDE.md + settings.local.json + 18개 agent md 파일이 modified.

- [ ] **Step 7.2: 커밋**

Run:
```bash
git add CLAUDE.md .claude/settings.local.json .claude/agents/
git commit -m "$(cat <<'EOF'
feat(agents): Jira 기반 워크플로우 통합 — Epic/Story + 코멘트 영속화

- CLAUDE.md: Jira 워크플로우 섹션 추가 (계층·상태·FIX 루프·코멘트 규칙·GitHub 연계)
- settings.local.json: mcp__atlassian__addCommentToJiraIssue 권한 추가
- 9개 결정/PL 에이전트: 직접 코멘트 권한 + Jira 코멘트 규약 섹션
  (PM/PMO/Architect/DevPL/EngPL/QualityPL/Refactor/Claude+CodexReviewer)
- 9개 오케스트레이터 경유 에이전트: TL;DR 출력 규약 섹션
  (Analyst/Researcher/QADev/Frontend+Backend/DataEng+ServerEng/Tester/Docs)

관리자 1회 설정(별도): Jira custom status 5종 + GitHub for Jira 앱 설치 완료

Spec: docs/superpowers/specs/2026-04-23-jira-agent-workflow-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 7.3: GitHub push**

Run:
```bash
git push origin feat/dashboard-perf
```
Expected: push 성공, GitHub 웹에서 커밋 반영 확인.

---

## 최종 검증 체크리스트

- [ ] Jira MCTRADER 프로젝트 워크플로우에 5개 custom status 존재 (`getTransitionsForJiraIssue`로 확인)
- [ ] GitHub for Jira 앱 설치 완료 (웹 UI에서 Development 섹션 표시)
- [ ] CLAUDE.md에 "## Jira 워크플로우 (MCTRADER 프로젝트)" 섹션 존재
- [ ] CLAUDE.md의 `<TID_*>` placeholder 0건 (실제 숫자로 교체됨)
- [ ] `.claude/settings.local.json`에 `addCommentToJiraIssue` 권한 존재
- [ ] 9개 결정/PL 에이전트 md에 권한 + "Jira 코멘트 규약" 섹션 존재 (Task 4.10 검증 통과)
- [ ] 9개 오케스트레이터 경유 에이전트 md에 "TL;DR 출력 규약" 섹션 존재 (Task 5.10 검증 통과)
- [ ] 스모크 테스트 Epic/Story/코멘트 생성 성공 (Task 6 전체 통과)
- [ ] 모든 변경사항 GitHub에 push됨

---

## 롤백 가이드

| Step 실패 | 롤백 |
|---|---|
| Task 1 (Jira admin 설정) | Jira workflow 원복 또는 status 수동 삭제 |
| Task 2-5 (md 변경) | `git reset HEAD~ && git checkout -- <파일>` |
| Task 6 (스모크 이슈) | 생성된 Epic·Story 수동 삭제 (Jira UI) |
| Task 7 (커밋·push) | `git revert <hash>` + force push는 피하고 revert 커밋으로 |
