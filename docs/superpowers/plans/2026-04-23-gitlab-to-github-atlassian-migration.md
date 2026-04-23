# GitLab → GitHub + Atlassian 이관 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GitLab(`mctrader1/mctrader`)에 있는 코드·이슈·ADR·문서를 GitHub(`mctrader/mctrader` private) + Jira(`MCTR`) + Confluence(`MCTRADER`)로 이관하고 GitLab은 read-only archive로 전환한다.

**Architecture:** MCP 직접 호출로 대화형 이관 (스크립트 없음). Atlassian MCP(`mcp__atlassian__*`)로 Confluence/Jira에 콘텐츠 생성, GitLab MCP(`mcp__GitLab__get_issue`)로 ADR fetch, Git mirror로 GitHub에 푸시. 각 단계마다 MCP fetch로 검증.

**Tech Stack:** Atlassian MCP, GitLab MCP, GitHub CLI (`gh`), Git mirror, Claude Code Edit/Write.

**Spec:** [docs/superpowers/specs/2026-04-23-gitlab-to-github-atlassian-migration-design.md](../specs/2026-04-23-gitlab-to-github-atlassian-migration-design.md)

---

## Task 1: 사전 준비 — Atlassian 인증 + GitHub 조직 확인 + MCP tool 이름 discover

**Files:**
- Read-only: 없음 (외부 시스템 상태 확인)

- [ ] **Step 1.1: Atlassian MCP 인증 상태 확인**

Tool 호출: `mcp__atlassian__authenticate`
Expected: 이미 인증된 경우 "Already authenticated" 등 성공 응답. 미인증 시 인증 URL 제공 → 사용자에게 브라우저 로그인 후 `mcp__atlassian__complete_authentication` 호출 요청.

**미인증 시 게이트**: 인증 완료 전까지 다음 Task 진행 금지.

- [ ] **Step 1.2: Atlassian MCP tool 이름 discover**

현재 세션에 `mcp__atlassian__authenticate` / `mcp__atlassian__complete_authentication`만 노출됨. 실제 createPage/createIssue 등 도구의 정확한 이름은 인증 후 로딩된다.

Run: `ToolSearch(query="mcp__atlassian", max_results=30)`
Expected: Confluence 페이지 CRUD, Jira 이슈 CRUD 관련 tool 10~20개 노출.

**기록**: Step 1.2 결과의 정확한 tool 이름을 실행 세션 메모에 기록. 이후 Task는 추상 이름(`createPage`, `createJiraIssue`)으로 참조 — 실행 시 실제 이름으로 매핑.

- [ ] **Step 1.3: GitHub 조직 `mctrader` 존재 확인**

Run: `gh api orgs/mctrader`
Expected: JSON 응답(조직 정보) — 존재 시. 404 시 사용자에게 조직 수동 생성 요청(GitHub UI, Free tier OK).

**미존재 시 게이트**: 조직 생성 전까지 Task 6 진입 금지.

- [ ] **Step 1.4: Confluence space `MCTRADER` 접근 확인**

Tool 호출: `mcp__atlassian__<getSpace or searchSpaces>(key="MCTRADER")` (Step 1.2에서 확인한 이름 사용)
Expected: space 정보 응답. 없으면 사용자에게 space 생성 요청.

- [ ] **Step 1.5: Jira project `MCTR` 접근 확인**

Tool 호출: `mcp__atlassian__<getJiraProject>(key="MCTR")`
Expected: project 정보 응답 (issue types 포함 — `Bug` issue type 존재 여부 확인).

- [ ] **Step 1.6: 현재 GitLab 리모트 상태 스냅샷**

Run:
```bash
cd /Users/1111971/workspace/mctrader
git remote -v > /tmp/migration-pre-remote.txt
git ls-remote origin | wc -l > /tmp/migration-pre-refcount.txt
cat /tmp/migration-pre-remote.txt /tmp/migration-pre-refcount.txt
```
Expected: `origin\thttps://gitlab.com/mctrader1/mctrader.git` 두 줄 + ref 개수(브랜치+태그 합계).

**게이트**: 모든 확인 통과 후 Task 2 진행.

---

## Task 2: Confluence 스켈레톤 — ADR 루트 + 6개 카테고리 parent 생성

**Files:**
- 외부: Confluence space `MCTRADER`

- [ ] **Step 2.1: "ADR" 루트 페이지 생성**

Tool 호출: `mcp__atlassian__createPage` with:
- space: `MCTRADER`
- parent: (space root)
- title: `ADR`
- body (Confluence storage format):
```xml
<p>Architecture Decision Records — mctrader 프로젝트의 설계 결정 기록</p>
<h2>카테고리</h2>
<ul>
  <li>Team &amp; Process</li>
  <li>Architecture</li>
  <li>Data &amp; Storage</li>
  <li>Infrastructure</li>
  <li>Dashboard &amp; UX</li>
  <li>Trading Strategy</li>
</ul>
<h2>전체 ADR 목록</h2>
<ac:structured-macro ac:name="detailssummary">
  <ac:parameter ac:name="cql">label = "adr" AND space = "MCTRADER"</ac:parameter>
  <ac:parameter ac:name="headings">번호,상태,카테고리,결정일</ac:parameter>
</ac:structured-macro>
```

Expected: 응답에서 `pageId` 획득. **기록**: `<ADR_ROOT_PAGE_ID>`.

- [ ] **Step 2.2: 6개 카테고리 parent 페이지 생성**

Step 2.1의 `<ADR_ROOT_PAGE_ID>`를 parent로 하여 6개 페이지 생성. 각 호출:

| 순서 | title | 간단 설명 body |
|---|---|---|
| 1 | Team & Process | 에이전트 팀 구성, 개발 프로세스 관련 결정 |
| 2 | Architecture | 아키텍처 패턴, 포트/어댑터 설계 결정 |
| 3 | Data & Storage | 데이터 저장 포맷·쿼리 엔진 결정 |
| 4 | Infrastructure | 배포·인프라·프로세스 수명주기 결정 |
| 5 | Dashboard & UX | 대시보드·시각화·UI 결정 |
| 6 | Trading Strategy | 전략·거래소 연동·백테스트 결정 |

각 페이지 body (예시 Team & Process):
```xml
<p>에이전트 팀 구성, 개발 프로세스 관련 ADR</p>
<ac:structured-macro ac:name="detailssummary">
  <ac:parameter ac:name="cql">label = "adr" AND parent = <CATEGORY_PAGE_ID></ac:parameter>
</ac:structured-macro>
```

각 응답에서 `pageId` 획득 후 표로 기록:

```
CATEGORY_ID_TEAM_PROCESS=...
CATEGORY_ID_ARCHITECTURE=...
CATEGORY_ID_DATA_STORAGE=...
CATEGORY_ID_INFRASTRUCTURE=...
CATEGORY_ID_DASHBOARD_UX=...
CATEGORY_ID_TRADING_STRATEGY=...
```

- [ ] **Step 2.3: 루트 + 카테고리 7개 페이지 존재 검증**

Tool 호출: `mcp__atlassian__<searchPages>(space="MCTRADER", cql="type=page AND (title='ADR' OR parent='<ADR_ROOT_PAGE_ID>')")`
Expected: 7개 결과 (루트 1 + 카테고리 6).

---

## Task 3: ADR 21건 이관 — GitLab → Confluence

**Files:**
- 외부: GitLab `mctrader1/mctrader` (read), Confluence `MCTRADER` (write)

### ADR → 카테고리 매핑 테이블

| GitLab iid | ADR 번호 | 제목 (간략) | 카테고리 변수 |
|---|---|---|---|
| 1 | ADR-001 | Hexagonal Architecture | `CATEGORY_ID_ARCHITECTURE` |
| 2 | ADR-002 | OrderBook Diff-only 저장 | `CATEGORY_ID_DATA_STORAGE` |
| 3 | ADR-003 | Parquet + DuckDB 채택 | `CATEGORY_ID_DATA_STORAGE` |
| 4 | ADR-004 | 백테스트 우선 개발 전략 | `CATEGORY_ID_TRADING_STRATEGY` |
| 5 | ADR-005 | Queue Position Model | `CATEGORY_ID_TRADING_STRATEGY` |
| 6 | ADR-006 | Bithumb 우선 연동, 멀티 거래소 | `CATEGORY_ID_TRADING_STRATEGY` |
| 7 | ADR-007 | 틱띠기 — OrderBook Imbalance | `CATEGORY_ID_TRADING_STRATEGY` |
| 8 | ADR-008 | Linux 단일 서버, systemd | `CATEGORY_ID_INFRASTRUCTURE` |
| 9 | ADR-009 | QueuePositionModel lifecycle 포트 | `CATEGORY_ID_ARCHITECTURE` |
| 10 | ADR-010 | Dashboard Web Interface | `CATEGORY_ID_DASHBOARD_UX` |
| 11 | ADR-011 | 서버사이드 타임존 변환 | `CATEGORY_ID_DASHBOARD_UX` |
| 12 | ADR-012 | Collector 수명주기 | `CATEGORY_ID_INFRASTRUCTURE` |
| 13 | ADR-013 | 백테스트 진행률 추적 | `CATEGORY_ID_TRADING_STRATEGY` |
| 15 | ADR-014a | 시각화 뷰 레이어 | `CATEGORY_ID_DASHBOARD_UX` |
| 16 | ADR-014b | 에이전트 팀 구조 재편 | `CATEGORY_ID_TEAM_PROCESS` |
| 17 | ADR-016 | TesterAgent 신설 | `CATEGORY_ID_TEAM_PROCESS` |
| 18 | ADR-017 | Dashboard DuckDB Connection | `CATEGORY_ID_DASHBOARD_UX` |
| 19 | ADR-018 | Dashboard Cache Strategy | `CATEGORY_ID_DASHBOARD_UX` |
| 20 | ADR-019 | Orderbook Snapshot Lookback | `CATEGORY_ID_DASHBOARD_UX` |
| 24 | ADR-020 | TDD 병렬 구현 | `CATEGORY_ID_TEAM_PROCESS` |
| 25 | ADR-021 | 요건 단계 도입 | `CATEGORY_ID_TEAM_PROCESS` |

(ADR-015는 GitLab 이력상 공백 — 건너뜀)

### 3.A 골든 패턴 (ADR-001 Hexagonal Architecture — 최초 1건)

- [ ] **Step 3.A.1: GitLab ADR-001 fetch**

Tool: `mcp__GitLab__get_issue(project_id=81469985, issue_iid=1)`
Expected: iid=1, title `ADR-001: Hexagonal Architecture (Ports & Adapters) 채택`, body(마크다운).

- [ ] **Step 3.A.2: 본문 변환 — Markdown → Confluence storage format**

변환 규칙:
- `# 헤딩` → `<h1>`, `## 헤딩` → `<h2>`, `### 헤딩` → `<h3>`
- ` ```mermaid\n ... \n``` ` → `<ac:structured-macro ac:name="mermaid-cloud"><ac:plain-text-body><![CDATA[ ... ]]></ac:plain-text-body></ac:structured-macro>`
  (정확한 매크로 이름은 Confluence 인스턴스 설치된 앱 기준. 기본 "Mermaid Diagrams for Confluence" 앱이 `mermaid-cloud`. 미설치 시 code block `<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">mermaid</ac:parameter>...`로 fallback)
- ` ```python\n ... \n``` ` → `<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">python</ac:parameter>...</ac:structured-macro>`
- 인라인 링크 `[text](url)` → `<a href="url">text</a>`
- 리스트 `- item` → `<ul><li>`

페이지 상단 삽입 (Page Properties):
```xml
<ac:structured-macro ac:name="details">
  <ac:rich-text-body>
    <table>
      <tr><th>번호</th><td>ADR-001</td></tr>
      <tr><th>상태</th><td>Accepted</td></tr>
      <tr><th>카테고리</th><td>Architecture</td></tr>
      <tr><th>결정일</th><td><GitLab issue created_at 날짜부분></td></tr>
      <tr><th>GitLab 원본</th><td><a href="<GitLab issue web_url>">iid=1</a></td></tr>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>
```

- [ ] **Step 3.A.3: Confluence 페이지 생성**

Tool: `mcp__atlassian__createPage` with:
- space: `MCTRADER`
- parent: `<CATEGORY_ID_ARCHITECTURE>`
- title: `ADR-001: Hexagonal Architecture (Ports & Adapters) 채택`
- body: Step 3.A.2에서 변환된 XML
- labels: `["adr"]`

Expected: `pageId` 응답.

- [ ] **Step 3.A.4: 검증 — 페이지 fetch 후 렌더 확인**

Tool: `mcp__atlassian__<getPage>(id=<new pageId>)`
Expected:
- title 일치
- body 내 `<ac:structured-macro>` 존재 (변환 성공)
- labels에 `adr` 포함

렌더링 오류(Mermaid 미설치 등) 발견 시 Step 3.A.2의 변환 규칙 조정 후 재시도.

### 3.B 반복 — 나머지 20건

- [ ] **Step 3.B.1: ADR-002 ~ ADR-021 이관 (각 건당 Step 3.A.1 ~ 3.A.3 반복)**

매핑 테이블의 iid 순서(1→25)로 순회:
- iid=1 ✅ (Step 3.A 완료)
- iid=2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,19,20,24,25 (총 20건)

각 건에서 `<CATEGORY_ID_*>` 변수는 테이블의 매핑 사용.
ADR-014 중복 처리: iid=15 → title 접두 `ADR-014a:`, iid=16 → title 접두 `ADR-014b:`로 GitLab 원제목에서 `ADR-014:`를 치환.

- [ ] **Step 3.B.2: 전체 검증**

Tool: `mcp__atlassian__<searchPages>(space="MCTRADER", cql="label='adr' AND parent IN (<all 6 category IDs>)")`
Expected: 21개 결과. 카테고리 분포:
- Team & Process: 4건 (014b, 016, 020, 021)
- Architecture: 2건 (001, 009)
- Data & Storage: 2건 (002, 003)
- Infrastructure: 2건 (008, 012)
- Dashboard & UX: 6건 (010, 011, 014a, 017, 018, 019)
- Trading Strategy: 5건 (004, 005, 006, 007, 013)

불일치 시 누락 ADR 재이관.

- [ ] **Step 3.B.3: 루트 ADR 페이지의 detailssummary 매크로 렌더 확인**

브라우저에서 `https://<tenant>.atlassian.net/wiki/spaces/MCTRADER/pages/<ADR_ROOT_PAGE_ID>` 방문 → 21개 ADR이 자동 테이블로 표시되는지 육안 확인.

**사용자 확인 게이트**: 렌더링 문제 없으면 Task 4 진행.

---

## Task 4: guides + api 문서 이관 → Confluence

**Files:**
- Read: `docs/guides/*.md` (5건), `docs/api/*.md` (1건)
- 외부: Confluence `MCTRADER` (write)

- [ ] **Step 4.1: "Guides" parent 페이지 생성**

Tool: `mcp__atlassian__createPage`, title=`Guides`, parent=(space root).
Body: `<p>운영 및 개발 가이드</p>`.
기록: `<GUIDES_PAGE_ID>`.

- [ ] **Step 4.2: guides 5건 이관**

각 파일:
- `docs/guides/config-reference.md` → title=`Config Reference`
- `docs/guides/dashboard-collector-data.md` → title=`Dashboard Collector Data`
- `docs/guides/known-issues.md` → title=`Known Issues`
- `docs/guides/orderbook-trade-visualization-spec.md` → title=`Orderbook/Trade Visualization Spec`
- `docs/guides/running-services.md` → title=`Running Services`

각 건:
1. Read 툴로 파일 내용 로드
2. Task 3.A.2 변환 규칙으로 Confluence storage format 변환
3. `mcp__atlassian__createPage(space="MCTRADER", parent=<GUIDES_PAGE_ID>, title=..., body=...)`
4. 응답 pageId 기록

- [ ] **Step 4.3: "API Reference" parent 페이지 생성**

Tool: `mcp__atlassian__createPage`, title=`API Reference`, parent=(space root).
기록: `<API_REF_PAGE_ID>`.

- [ ] **Step 4.4: api 1건 이관**

- `docs/api/bithumb-websocket-api.md` → title=`Bithumb WebSocket API`, parent=`<API_REF_PAGE_ID>`.

- [ ] **Step 4.5: 전체 Confluence 페이지 카운트 검증**

Tool: `mcp__atlassian__<searchPages>(space="MCTRADER", cql="type=page")`
Expected: 최소 30개 (ADR 루트 1 + 카테고리 6 + ADR 21 + Guides 루트 1 + guides 5 + API Ref 1 + api 1 = **36**).

---

## Task 5: bugs → Jira MCTR 이관

**Files:**
- Read: `docs/bugs/*.md` (3건)
- 외부: Jira `MCTR` (write)

- [ ] **Step 5.1: `docs/bugs/bug-collector-sighup-nohup.md` → Jira 이슈**

1. Read 파일
2. Summary: `[Migrated] collector sighup/nohup 버그` (파일명 기반)
3. Description: 파일 본문 그대로 (Markdown → Jira wiki/ADF 포맷 변환 — MCP 도구가 Markdown 입력을 지원하면 그대로)
4. Tool: `mcp__atlassian__createJiraIssue` with:
   - project: `MCTR`
   - issueType: `Bug`
   - summary, description 위 값
   - labels: `["migrated-from-repo"]`
   - (선택) assignee: 사용자 계정
5. 응답에서 issue key (예: `MCTR-1`) 기록

- [ ] **Step 5.2: `bug-parquet-sink-dict-mutation.md` → Jira 이슈** (Step 5.1과 동일 패턴)

Summary: `[Migrated] parquet sink dict mutation 버그`

- [ ] **Step 5.3: `bug-test-tsfmt-wrong-timestamp.md` → Jira 이슈** (Step 5.1과 동일 패턴)

Summary: `[Migrated] test tsfmt wrong timestamp 버그`

- [ ] **Step 5.4: 모두 Resolved/Closed 상태로 전이**

각 이슈에 대해 Tool: `mcp__atlassian__<transitionJiraIssue>(issueKey=..., transition="Done" or "Resolve")`.
(transition 이름은 프로젝트 workflow에 따라 — Step 1.5에서 확인된 issue type의 transition 목록 사용)

- [ ] **Step 5.5: 검증**

Tool: `mcp__atlassian__<searchJiraIssues>(jql="project=MCTR AND labels='migrated-from-repo'")`
Expected: 3건, 모두 status=Done/Resolved.

---

## Task 6: GitHub 레포 생성 + 코드 미러 푸시

**Files:**
- 외부: GitLab(read), GitHub(write)
- Temp: `/tmp/mctrader-mirror.git` (bare clone)

- [ ] **Step 6.1: GitHub 레포 `mctrader/mctrader` 존재 확인, 없으면 생성**

Run: `gh api repos/mctrader/mctrader 2>&1 | head -1`
Expected (존재): JSON 응답
Expected (미존재): `gh: Not Found (HTTP 404)` → 다음 명령 실행:

```bash
gh repo create mctrader/mctrader --private --description "mctrader — scalping auto-trading framework (migrated from GitLab 2026-04-23)"
```
Expected: 레포 생성 메시지 + URL.

- [ ] **Step 6.2: GitLab에서 bare mirror clone**

```bash
cd /tmp
rm -rf mctrader-mirror.git
git clone --mirror https://gitlab.com/mctrader1/mctrader.git mctrader-mirror.git
cd mctrader-mirror.git
git ls-remote . | wc -l
```
Expected: ref 개수가 Step 1.6에서 기록한 값과 일치.

- [ ] **Step 6.3: GitHub으로 mirror push**

```bash
cd /tmp/mctrader-mirror.git
git remote set-url --push origin https://github.com/mctrader/mctrader.git
git push --mirror
```
Expected: "Writing objects ... done.", 모든 브랜치·태그 push 성공.

오류 시: 큰 파일(100MB+) 있으면 git-lfs 필요 — 해당 파일 식별 후 사용자 확인.

- [ ] **Step 6.4: 검증 — GitHub ref 개수**

```bash
git ls-remote https://github.com/mctrader/mctrader.git | wc -l
```
Expected: Step 1.6과 동일한 ref 개수.

---

## Task 7: 로컬 레포 origin 교체

**Files:**
- Modify: `/Users/1111971/workspace/mctrader/.git/config` (via `git remote`)

- [ ] **Step 7.1: 현재 브랜치 백업 확인**

```bash
cd /Users/1111971/workspace/mctrader
git status
git branch --show-current
git log --oneline -5
```
Expected: 작업 중인 브랜치명(`feat/dashboard-perf`) + 최근 커밋.

- [ ] **Step 7.2: origin URL 변경**

```bash
git remote set-url origin https://github.com/mctrader/mctrader.git
git remote -v
```
Expected:
```
origin	https://github.com/mctrader/mctrader.git (fetch)
origin	https://github.com/mctrader/mctrader.git (push)
```

- [ ] **Step 7.3: fetch 검증**

```bash
git fetch origin
git branch -r | head
```
Expected: `origin/main`, `origin/feat/dashboard-perf` 등 원격 브랜치 출력.

- [ ] **Step 7.4: 현재 브랜치 원격 tracking 재설정**

```bash
git branch --set-upstream-to=origin/feat/dashboard-perf feat/dashboard-perf
git status
```
Expected: "Your branch is up to date with 'origin/feat/dashboard-perf'" 또는 ahead/behind 정보.

---

## Task 8: `.claude/settings(.local).json` 갱신 — GitLab 제거 + Atlassian 추가

**Files:**
- Modify: `.claude/settings.json:12`
- Modify: `.claude/settings.local.json:65-78`

- [ ] **Step 8.1: `.claude/settings.json` L12 GitLab 권한 제거**

Current L12:
```json
      "mcp__GitLab__list_issues",
```

Edit: Step 1.2에서 discover한 Atlassian tool 이름 중 READ용 3~5개로 교체. 예:
```json
      "mcp__atlassian__searchPages",
      "mcp__atlassian__getPage",
      "mcp__atlassian__searchJiraIssues",
      "mcp__atlassian__getJiraIssue",
```

(정확한 이름은 Step 1.2 기록 사용)

- [ ] **Step 8.2: `.claude/settings.local.json` L65-78 GitLab 권한 제거**

Current L65-71, L78: `mcp__GitLab__*` 9개 권한.

Edit: 해당 줄 전체 삭제 후 같은 위치에 Atlassian write 권한 추가:
```json
      "mcp__atlassian__createPage",
      "mcp__atlassian__updatePage",
      "mcp__atlassian__searchPages",
      "mcp__atlassian__getPage",
      "mcp__atlassian__createJiraIssue",
      "mcp__atlassian__updateJiraIssue",
      "mcp__atlassian__searchJiraIssues",
      "mcp__atlassian__getJiraIssue",
      "mcp__atlassian__transitionJiraIssue",
      "mcp__atlassian__authenticate",
      "mcp__atlassian__complete_authentication",
```

- [ ] **Step 8.3: GitHub CLI 권한 추가 (신규)**

`.claude/settings.local.json`에 Bash 권한 추가:
```json
      "Bash(gh repo *)",
      "Bash(gh api *)",
      "Bash(gh pr *)",
      "Bash(gh issue *)",
      "Bash(gh auth *)",
```

- [ ] **Step 8.4: JSON 유효성 검증**

```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo "settings.json OK"
python3 -m json.tool .claude/settings.local.json > /dev/null && echo "settings.local.json OK"
```
Expected: 둘 다 "OK".

---

## Task 9: `CLAUDE.md` 갱신

**Files:**
- Modify: `CLAUDE.md:47, :101, :113-119`

- [ ] **Step 9.1: L47 교체**

Old:
```
- **ID + 1줄 요약**: ADR이 배경 참조 수준일 때. 필요 시 sub-agent가 `mcp__GitLab__get_issue`로 fetch
```
New:
```
- **ID + 1줄 요약**: ADR이 배경 참조 수준일 때. 필요 시 sub-agent가 Confluence `mcp__atlassian__getPage`로 fetch
```

- [ ] **Step 9.2: L101 교체**

Old:
```
- 문서 쓰기: DocsAgent(.md + GitLab MCP)
```
New:
```
- 문서 쓰기: DocsAgent(.md + Atlassian MCP — Confluence 페이지, Jira 이슈)
```

- [ ] **Step 9.3: L113-119 ADR 섹션 재작성**

Old (L113-119):
```
## ADR (GitLab Issues SSOT)
- 프로젝트 `mctrader1/mctrader` (ID 81469985)
- 목록: `mcp__GitLab__list_issues(labels=["ADR"])` / 상세: `mcp__GitLab__get_issue(issue_iid=N)`
- 세션 시작 시 ADR 목록 조회, 결정 사항 번복 금지
- 설계 결정마다 신규 ADR 생성 (번호 = 기존 최대 + 1)

### 생성 기준
라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 전략 도메인 핵심 개념
```

New:
```
## ADR (Confluence Pages SSOT)
- Space: `MCTRADER` / 루트 페이지 `ADR` / 6개 카테고리 parent 하위
- 목록: `mcp__atlassian__searchPages(cql="label='adr' AND space='MCTRADER'")` / 상세: `mcp__atlassian__getPage(id=N)`
- 세션 시작 시 ADR 목록 조회, 결정 사항 번복 금지
- 설계 결정마다 신규 ADR 생성 (번호 = 기존 최대 + 1)

### 카테고리
Team & Process / Architecture / Data & Storage / Infrastructure / Dashboard & UX / Trading Strategy
신규 ADR은 결정 성격에 맞는 카테고리 page의 child로 생성.

### 생성 기준
라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 전략 도메인 핵심 개념
```

- [ ] **Step 9.4: L120+ "이슈 포맷" 섹션 재작성**

Old (이슈 포맷 부분):
```
### 이슈 포맷
제목 `ADR-NNN: <결정>` + label `ADR`. 본문: `## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램 / ## 관련 파일`
```

New:
```
### 페이지 템플릿
제목 `ADR-NNN: <결정>` + label `adr` + Page Properties(번호/상태/카테고리/결정일/관련파일).
본문 섹션: `## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램(Mermaid) / ## 관련 파일`
```

- [ ] **Step 9.5: 잔여 GitLab 참조 0건 확인**

```bash
grep -n "GitLab\|gitlab\|mcp__GitLab\|mctrader1" CLAUDE.md
```
Expected: 빈 결과.

---

## Task 10: `.claude/agents/DocsAgent.md` 갱신

**Files:**
- Modify: `.claude/agents/DocsAgent.md:11-22, :33-37, :67-71`

- [ ] **Step 10.1: L11-22 tool 권한 교체**

Old (L11-22):
```yaml
    - mcp__GitLab__create_issue
    - mcp__GitLab__update_issue
    - mcp__GitLab__create_issue_note
    - mcp__GitLab__update_issue_note
    - mcp__GitLab__list_issues
    - mcp__GitLab__get_issue
    - mcp__GitLab__discover_tools
    - mcp__GitLab__create_wiki_page
    - mcp__GitLab__update_wiki_page
    - mcp__GitLab__list_wiki_pages
    - mcp__GitLab__get_wiki_page
    - mcp__GitLab__delete_wiki_page
```

New:
```yaml
    - mcp__atlassian__createPage
    - mcp__atlassian__updatePage
    - mcp__atlassian__getPage
    - mcp__atlassian__searchPages
    - mcp__atlassian__createJiraIssue
    - mcp__atlassian__updateJiraIssue
    - mcp__atlassian__getJiraIssue
    - mcp__atlassian__searchJiraIssues
    - mcp__atlassian__transitionJiraIssue
```

(정확한 tool 이름은 Step 1.2 기록 사용)

- [ ] **Step 10.2: L33-37 ADR 정책 섹션 교체**

Old (L33-37):
```
### ADR은 GitLab Issues 전용 (SSOT)
- **모든 ADR은 GitLab Issues(label=ADR)에만 작성·업데이트한다.** 레포 내 `docs/adr/` 디렉토리는 폐기되었으며 이중 관리 금지
- ADR 작성·수정 시 반드시 `mcp__GitLab__create_issue` / `mcp__GitLab__update_issue` 도구 사용
- Mermaid 다이어그램·상세 근거 등 ADR 모든 내용은 GitLab Issue 본문에 포함 (별도 Markdown 파일 생성 금지)
- 기존 `docs/adr/` 내용을 복원하거나 GitLab 이슈를 Markdown으로 mirror 하지 않는다
```

New:
```
### ADR은 Confluence 페이지 전용 (SSOT)
- **모든 ADR은 Confluence space `MCTRADER` 내 "ADR" 계층(카테고리 parent 하위)에만 작성·업데이트한다.** 레포 내 Markdown 중복 관리 금지
- ADR 작성·수정 시 반드시 `mcp__atlassian__createPage` / `mcp__atlassian__updatePage` 사용
- 페이지 상단에 Page Properties(번호/상태/카테고리/결정일/관련파일) 삽입, label=`adr` 부여
- Mermaid 다이어그램은 Confluence Mermaid 매크로(또는 code block fallback)로 포함
- 6개 카테고리 중 성격에 맞는 parent page 하위에 생성 (Team & Process / Architecture / Data & Storage / Infrastructure / Dashboard & UX / Trading Strategy)
```

- [ ] **Step 10.3: L67-71 "GitLab Wiki 마이그레이션" 섹션 제거**

Old (L67-71):
```
- 추후 GitLab Wiki 마이그레이션 대상에 포함

### 추후: GitLab Wiki 마이그레이션
- MCP GitLab wiki 도구가 지원되면 `docs/` 비-ADR 내용을 GitLab Wiki로 이전한다.
- 이전 시 파일 구조와 슬러그를 동일하게 유지한다.
```

New (두 섹션 모두 삭제, 이유: guides/api는 이미 Confluence로 이동됨).

- [ ] **Step 10.4: L40-50 디렉토리 구조 설명에서 guides/api/bugs 제거**

Old (L42-48):
```
  docs/
  ├── api/            # 외부 API 연동 문서 (거래소 WebSocket 등)
  ├── guides/         # 운영/개발 가이드
  ├── bugs/           # 버그 히스토리 (재발 방지)
  ├── requirements/   # PMOAgent가 작성한 통합 요건 명세서 (요건 단계 산출물)
  └── change-plans/   # ArchitectAgent가 작성한 변경 계획서 (모든 과제 1:1 저장)
```

New:
```
  docs/
  ├── requirements/   # PMOAgent가 작성한 통합 요건 명세서 (요건 단계 산출물)
  └── change-plans/   # ArchitectAgent가 작성한 변경 계획서 (모든 과제 1:1 저장)
  # api/, guides/, bugs/는 Confluence(MCTRADER) 및 Jira(MCTR)로 이전됨 (2026-04-23)
```

- [ ] **Step 10.5: bugs 기록 정책 추가**

같은 섹션에 다음 추가:
```
### 버그 기록: Jira
- 버그는 Jira 프로젝트 `MCTR`에 Bug issue로 기록
- `mcp__atlassian__createJiraIssue(project="MCTR", issueType="Bug", ...)` 사용
- label=`migrated-from-repo`는 2026-04-23 이전 리포지토리 기록 이관분만 해당 — 신규 버그엔 부여하지 않음
```

---

## Task 11: `.claude/agents/PMOAgent.md` 갱신

**Files:**
- Modify: `.claude/agents/PMOAgent.md:61`

- [ ] **Step 11.1: L61 교체**

Old:
```
   - **강한 관련**(결정이 본 작업의 직접 제약): `mcp__GitLab__get_issue`로 fetch 후 "## 상태/컨텍스트/결정/결과" verbatim 포함
```

New:
```
   - **강한 관련**(결정이 본 작업의 직접 제약): `mcp__atlassian__getPage`로 fetch 후 "## 상태/컨텍스트/결정/결과" verbatim 포함
```

- [ ] **Step 11.2: PMOAgent.md 잔여 GitLab 참조 확인**

```bash
grep -n "GitLab\|gitlab\|mcp__GitLab" .claude/agents/PMOAgent.md
```
Expected: 빈 결과.

---

## Task 12: 전수 점검 — 에이전트 정의 + README 파일 잔여 GitLab 참조 제거

**Files:**
- Scan: `.claude/agents/*.md`, `docs/README.md`, `README.md`
- Modify (확인 결과): `docs/README.md`, `README.md`

- [ ] **Step 12.1: 에이전트 파일 전수 grep**

```bash
grep -rn "GitLab\|gitlab\|mcp__GitLab\|mctrader1" .claude/agents/
```
Expected: Task 10 (DocsAgent), Task 11 (PMOAgent) 수정 후 결과는 **빈 결과**.
(다른 에이전트엔 GitLab 참조 없음 — 2026-04-23 기준 확인됨. 발견 시 동일 원칙: 이슈 권한 → Atlassian 권한, GitLab 프로젝트 ID → Confluence space/Jira project key.)

- [ ] **Step 12.2: `docs/README.md` 재작성**

Old (전체):
```markdown
# mctrader 문서

작업 중 습득한 외부 API 스펙, 설계 결정, 운영 가이드를 관리한다.

> 추후 GitLab Wiki로 이전 예정.

## 구조

| 디렉토리 | 내용 |
|----------|------|
| `api/` | 외부 API 연동 문서 (거래소 WebSocket 등) |
| `adr/` | ADR 보완 문서 |
| `guides/` | 운영/개발 가이드 |
```

New (전체):
```markdown
# mctrader 문서

작업 산출물(요건 명세서, 변경 계획서) 및 설계 문서(superpowers specs/plans)를 관리한다.

도메인 문서(ADR, 운영 가이드, 외부 API 스펙, 버그 이력)는 외부 시스템으로 이관:
- **ADR**: Confluence space `MCTRADER` / 페이지 트리 `ADR/<카테고리>/ADR-NNN: ...`
- **운영 가이드 · API 스펙**: Confluence space `MCTRADER` / `Guides`, `API Reference` 트리
- **버그 기록**: Jira project `MCTR` / Bug issue

## 구조

| 디렉토리 | 내용 |
|----------|------|
| `requirements/` | PMOAgent 통합 요건 명세서 |
| `change-plans/` | ArchitectAgent 변경 계획서 (PR과 1:1 매핑) |
| `superpowers/specs/` | 설계 문서 (brainstorming 결과) |
| `superpowers/plans/` | 구현 계획서 |
```

Edit 툴로 전체 내용 교체.

- [ ] **Step 12.3: `README.md` 재작성 (GitLab 스캐폴드 제거)**

현재 `README.md`는 GitLab이 프로젝트 생성 시 자동 삽입한 boilerplate(L5-43에 GitLab 가이드 링크 및 "Editing this README" 템플릿). 전체 교체:

Old: 전체 (94줄 GitLab boilerplate)

New (전체):
```markdown
# mctrader

암호화폐 스캘핑 자동매매 프레임워크 (Python).

## 문서 안내

| 종류 | 위치 |
|------|------|
| ADR (Architecture Decision Records) | [Confluence — space MCTRADER, 트리 `ADR`](https://mctrader.atlassian.net/wiki/spaces/MCTRADER) |
| 운영 가이드 · 외부 API 스펙 | Confluence — space MCTRADER, 트리 `Guides` / `API Reference` |
| 버그 이력 | [Jira — project MCTR](https://mctrader.atlassian.net/jira/software/projects/MCTR) |
| 요건·계획서 | [`docs/requirements/`](docs/requirements/), [`docs/change-plans/`](docs/change-plans/) |
| 에이전트 오케스트레이션 규칙 | [`CLAUDE.md`](CLAUDE.md) |

## 개발

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pytest
```

## 리포지토리

- 코드: https://github.com/mctrader/mctrader (이 리포)
- 이력 아카이브: https://gitlab.com/mctrader1/mctrader (read-only, 2026-04-23 이관 완료)
```

Write 툴로 전체 파일 덮어쓰기 (Read 선행 필수).

- [ ] **Step 12.4: 전수 재검증**

```bash
grep -rn "GitLab\|gitlab\|mcp__GitLab\|mctrader1" .claude/ CLAUDE.md README.md docs/README.md
```
Expected: 빈 결과 (또는 마이그레이션 완료 아카이브 언급 1-2건 — `README.md`의 "이력 아카이브" 링크는 의도된 참조로 유효).

---

## Task 13: 로컬 docs 정리 + 커밋

**Files:**
- Delete: `docs/guides/`, `docs/api/`, `docs/bugs/`

- [ ] **Step 13.1: 디렉토리 삭제 (Confluence/Jira 이관 성공 확인 후)**

```bash
cd /Users/1111971/workspace/mctrader
git rm -r docs/guides docs/api docs/bugs
git status
```
Expected: 3개 디렉토리 내 파일 전부 `deleted:` 상태.

- [ ] **Step 13.2: 커밋**

```bash
git add -A
git commit -m "$(cat <<'EOF'
chore(migration): GitLab → GitHub+Atlassian 이관 완료

- docs/guides, docs/api, docs/bugs → Confluence(MCTRADER)/Jira(MCTR) 이관 후 제거
- .claude/settings(.local).json: GitLab MCP 권한 제거, Atlassian/GitHub 권한 추가
- CLAUDE.md: ADR SSOT → Confluence space MCTRADER
- .claude/agents/DocsAgent.md: ADR 정책 + 디렉토리 구조 + bugs 기록 정책 업데이트
- .claude/agents/PMOAgent.md: ADR fetch → atlassian__getPage

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 13.3: 첫 GitHub push**

```bash
git push origin feat/dashboard-perf
```
Expected: push 성공. GitHub 웹에서 커밋 확인.

---

## Task 14: GitLab 프로젝트 read-only archive (최종 게이트)

**사용자 확인 게이트**: Task 1-13 모두 완료 후, 사용자에게 최종 아카이브 실행 확인 요청.

- [ ] **Step 14.1: 사용자에게 다음 메시지 제시**

```
이관 완료 확인:
✅ Confluence MCTRADER: ADR 21건 + guides 5 + api 1 페이지 생성
✅ Jira MCTR: bugs 3건 이슈 생성
✅ GitHub mctrader/mctrader: 코드 미러 완료, 로컬 origin 전환
✅ CLAUDE.md / 에이전트 정의 / settings 업데이트 완료
✅ docs/ 비-ADR 디렉토리 삭제 및 GitHub에 커밋 푸시

마지막 단계: GitLab mctrader1/mctrader 프로젝트를 read-only archived로 전환합니다.
archive 후에는 쓰기 불가(이력은 보존). 실행할까요? (Yes/No)
```

- [ ] **Step 14.2: 사용자 Yes 시 GitLab archive**

Option A — 웹 UI: `Settings → Advanced → Archive project` (사용자 수동).
Option B — API:
```bash
curl --request POST \
  --header "PRIVATE-TOKEN: <GitLab token>" \
  "https://gitlab.com/api/v4/projects/81469985/archive"
```
(토큰은 사용자가 제공)

- [ ] **Step 14.3: 아카이브 검증**

```bash
curl -s "https://gitlab.com/api/v4/projects/81469985" | python3 -c "import json,sys;d=json.load(sys.stdin);print('archived=',d.get('archived'))"
```
Expected: `archived= True`.

---

## Post-Migration 검증 체크리스트

- [ ] Confluence: `https://<tenant>.atlassian.net/wiki/spaces/MCTRADER` 방문 → ADR/Guides/API Reference 계층 표시
- [ ] Confluence ADR 루트 페이지 → detailssummary 매크로가 21개 ADR 테이블로 렌더
- [ ] Jira: `https://<tenant>.atlassian.net/jira/software/projects/MCTR` 방문 → 3 Bug 이슈 표시 (Status=Done)
- [ ] GitHub: `https://github.com/mctrader/mctrader` 방문 → 레포 존재, 커밋 이력 연속, 최신 커밋은 Task 13.2
- [ ] 로컬 `git push/pull origin` 동작 정상
- [ ] `grep -rn "GitLab\|mcp__GitLab" CLAUDE.md .claude/` 결과 빈 결과
- [ ] `ls docs/` 결과 `change-plans/ requirements/ superpowers/ README.md` 등만 존재
- [ ] GitLab 프로젝트 archived=true

---

## 롤백 가이드

| Step 실패 시점 | 롤백 방법 |
|---|---|
| Task 2-5 (Confluence/Jira 쓰기 실패) | 생성된 페이지/이슈 수동 삭제 후 재시도. GitLab은 여전히 SSOT |
| Task 6 (GitHub push 실패) | GitHub 레포 삭제 후 재시도 (GitLab 이력 무손실) |
| Task 7 (로컬 origin 교체 후 문제) | `git remote set-url origin https://gitlab.com/mctrader1/mctrader.git`로 복구 |
| Task 8-12 (설정/CLAUDE.md 오염) | `git reset HEAD~ && git checkout -- .claude/ CLAUDE.md`로 복구 |
| Task 13 (디렉토리 삭제 후 되돌림) | `git checkout HEAD~ -- docs/guides docs/api docs/bugs` |
| Task 14 (아카이브 후) | GitLab UI `Settings → Advanced → Unarchive project`로 해제 가능 |
