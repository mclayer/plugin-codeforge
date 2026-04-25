# Atlassian → GitHub Migration Design

- **Status**: Draft (브레인스토밍 합의 종료, 구현 계획 대기)
- **Author**: codeforge core
- **Date**: 2026-04-25
- **Type**: Architectural redesign — atlassian MCP 의존 제거 + GitHub-native 재설계

---

## 1. Goal & Scope

### Goal

codeforge plugin에서 atlassian MCP 의존을 **완전 제거**(hard remove)하고, Confluence·Jira가 담당하던 모든 책임을 GitHub primitive (Issues / PR / Milestones / Sub-issues / Projects v2 / Discussions / Actions / repo files / CODEOWNERS / Branch protection)로 이전한다.

### In scope

- Plugin 코드 전체 (CLAUDE.md, 24 agent md, orchestrator-playbook, project-config-schema, templates/, presets/)
- 신규 GitHub Actions 워크플로우 템플릿 (`templates/github-workflows/`)
- 신규 Issue Forms (`templates/github-issue-forms/`)
- 신규 PR template (`templates/github-pr-template.md`)
- 신규 CODEOWNERS template
- consumer-guide 갱신 (GitHub 셋업 절차)
- `.claude/settings.json` / `.claude/settings.local.json` 권한 갱신

### Out of scope

- 기존 atlassian → github 데이터 마이그레이션 도구·가이드 (consumer 부재 확정)
- atlassian MCP plugin 자체 (외부 plugin이라 그대로 둠)
- 추가 자동화 C 그룹 (`project-v2-auto-add.yml`, `pmo-trigger-on-fix-burst.yml`, `milestone-progress-notify.yml` — v0.1 보류, v0.2+ 추가 검토)
- Wiki 관련 기능 (PR review·branch 격리·MCP 도구 부재로 부적합 결론)

### Non-goals

- Backward compatibility (consumer 없음)
- Atlassian과의 dual-write 또는 hybrid 모드
- Third-party MCP (lobehub 등) 의존

---

## 2. Storage 매핑 (8 책임 영역 → GitHub primitive)

| # | 책임 영역 | 1차 저장소 | 보강 GitHub 기능 |
|---|----------|-----------|-----------------|
| 1 | Workflow 메타 (Epic/Story/sub-task) | Milestone(Epic) + Issue(Story) + Sub-issues(Impl Manifest) | Projects v2 (Board/Table/Roadmap view) + Issue Forms |
| 2 | Story 페이지 §1–11 (긴 서사) | `docs/stories/<KEY>.md` (single SSOT) | Issue Forms (§1 입력 강제) + PR template |
| 3 | FIX Ledger §10 | `docs/stories/<KEY>.md` §10 (append commit) | Issue comment `[FIX #N]` mirror |
| 4 | ADR | `docs/adr/ADR-NNN-<slug>.md` (flat, frontmatter `category:`) | CODEOWNERS @org/architects + Branch protection |
| 5 | Domain KB | `docs/domain-knowledge/<area>/<topic>.md` (계층) | Discussions (Q&A 카테고리) + CODEOWNERS @org/domain-experts |
| 6 | Phase 코멘트 로그 (10종 prefix) | Story Issue comments | Saved Replies 템플릿 (DocsAgent용) |
| 7 | Bug / Audit Story | Issue + labels (`type:bug`, `audit:post-hotfix`) | Issue Forms |
| 8 | Workflow 상태 전이 | Labels (`phase:*` single-active) + GitHub Actions | Branch protection + Required status checks + CODEOWNERS + Projects v2 automation |
| + | 보안 보강 | — | Dependabot + CodeQL + Secret Scanning + Push Protection (consumer settings에서 활성화) |

### 디렉토리 구조

```
docs/
  stories/
    <KEY>.md                              # Story §1-11 single file SSOT
  adr/
    ADR-001-<slug>.md                     # flat, frontmatter category 필드
    ADR-002-<slug>.md
    README.md                             # 인덱스 (자동 생성)
  change-plans/
    <slug>.md                             # 현행 그대로 유지
  domain-knowledge/
    <area>/
      <topic>.md                          # 계층 — area별 grouping
    README.md
```

**ADR이 flat인 이유**: ADR은 immutable cross-reference가 빈번 → path stability 중요. category 변경은 frontmatter 메타 변경만으로.
**Domain KB가 계층인 이유**: 안정적 reference 문서 + browse·검색에 area 그루핑 도움. ADR 같은 path-stability 부담 적음.

---

## 3. Workflow Lifecycle

### 3.1 Story 1건 = 2 PRs (확정 모델)

```
[1] User opens GitHub Issue (Issue Forms)
       ↓ form field "사용자 요구사항" 입력 (변조 금지 텍스트)
       ↓ form field "Epic Milestone" 선택 (선택사항)

[2] story-init.yml Action 자동 trigger
       - <KEY_PREFIX>-N 다음 번호 계산 (예: PLG-7)
       - feature branch 생성: feat/<KEY>-<slug>
       - docs/stories/<KEY>.md 생성:
            §1 = form input verbatim
            §2-11 = placeholder
       - Phase 1 PR 자동 생성 (architect team CODEOWNERS auto-review)
       - Issue body를 "Story SSOT: docs/stories/<KEY>.md" 링크로 갱신
       - Label 부착: type:story, phase:요구사항
       - Milestone 할당 (form input 명시한 경우)

[3] Phase 1 PR (요구사항 + 설계 + 설계리뷰 lane)
       branch: feat/<KEY>-<slug>
       changes: docs/stories/<KEY>.md + docs/change-plans/<slug>.md + docs/adr/ADR-NNN-<slug>.md (필요 시)
       commit append:
          §2 도메인 해석 (DomainAgent → DocsAgent)
          §3 ADR 정합성 (RequirementsPL → DocsAgent)
          §4 코드경로 (RequirementsPL → DocsAgent)
          §5 요구사항 확장해석 (Analyst → DocsAgent)
          §6 외부지식배경 (Researcher → DocsAgent)
          §7 설계서사 (Architect → DocsAgent)
          docs/change-plans/<slug>.md 신규 또는 갱신
          docs/adr/ADR-NNN-<slug>.md 신규 (설계 결정 시)
       Phase label 진행:
          phase:요구사항 → phase:설계 → phase:설계-리뷰
       phase-label-invariant.yml: single-active 강제
       설계 리뷰 PASS → label gate:design-review-pass 부착
       phase-gate-mergeable.yml: phase:설계-리뷰 + gate:design-review-pass → mergeable
       FIX 발생 시:
          - fix:설계-리뷰-retry 라벨 부착
          - docs/stories/<KEY>.md §10 commit append
          - fix-ledger-mirror.yml가 Issue comment [FIX #N] 자동 생성
          - 최대 3회 (FIX Ledger current-cycle count 기준)

[4] Phase 1 PR merge → main
       Story SSOT (§1-7) main 확립
       Issue label 갱신: DocsAgent가 phase:구현 라벨 부착 (phase-label-invariant.yml가 기존 phase:설계-리뷰 자동 detach)
       Phase 2 PR 시작 가능 상태

[5] Phase 2 PR (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane)
       PR 생성 주체: DeveloperPLAgent가 첫 구현 commit 준비 후 DocsAgent에 PR open 의뢰 → DocsAgent가 mcp__github__create_pull_request 호출 (Phase 1 PR과 달리 Action 자동 생성 아님 — 구현 시작 시점이 가변적이므로 명시적 트리거 필요)
       branch: 신규 feature branch (impl/<KEY>-<slug>)
       PR body: PULL_REQUEST_TEMPLATE.md의 Phase 2 양식 + "Closes #<Story Issue 번호>" 키워드 (merge 시 Issue 자동 close)
       changes:
          src/** + tests/** + config/** + deploy/**
          docs/stories/<KEY>.md §8-11 commit append (Impl Manifest §8.5 포함)
          docs/change-plans/<slug>.md 보강
       Sub-issue 자동 생성 (subissue-from-impl-manifest.yml):
          §8.5 매핑표의 각 file 단위로 sub-issue 1개 생성
          label: impl-manifest
       Phase label 진행:
          phase:구현 → phase:구현-리뷰 → phase:구현-테스트 → phase:보안-테스트
       FIX 발생 시:
          - fix:* 라벨 자동 부착 (fix-label-auto.yml)
          - Architect 판정 (구현 vs 설계) commit으로 §10 append
          - 설계 원인 → Phase 1 follow-up PR로 회귀 (drainage)
          - 구현 원인 → Phase 2 PR 안에서 commit append
          - 카운터 RESET 시 §10에 RESET 마커 commit
          - 구현 리뷰 FIX 최대 3회 / 구현 테스트·보안 테스트 FIX 무제한
       보안 테스트 PASS → label gate:security-test-pass
       phase-gate-mergeable.yml: phase:보안-테스트 + gate:security-test-pass → mergeable

[6] Phase 2 PR merge → main
       PR body의 "Closes #<Story Issue>" → Issue 자동 close (GitHub native)
       Sub-issues 자동 close (parent close 시 GitHub 기본)
       Milestone % 진행률 자동 갱신
       PMOAgent 회고 트리거 (사용자 요청 시 또는 다음 세션)
```

### 3.2 Hotfix 경로

기존 CLAUDE.md의 hotfix 정책(2종)은 유지. 단:
- `audit:post-hotfix` label은 신규 Audit Issue에 부착 (Audit Story 생성)
- Audit Story도 동일한 2-PR 모델 (Phase 1 + Phase 2) 적용

### 3.3 FIX Ledger §10 형식 (변경 없음)

`docs/stories/<KEY>.md` §10:

```markdown
## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1 | 2026-04-25T14:32Z | 설계-리뷰 | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2 | 2026-04-26T09:15Z | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
| 3 | 2026-04-26T16:48Z | 보안-테스트 | SecurityTestPL P0 × 1 (SQL injection) | 구현 | DeveloperAgent 재스폰 | — |
```

Architect 판정마다 1행 append commit. RESET 마커는 별도 행 또는 RESET 컬럼 마킹.

---

## 4. Agent 권한 재매핑

### 4.1 Atlassian → GitHub 도구 매핑 표

| 현 atlassian 도구 | 신 GitHub 도구 | 비고 |
|------------------|----------------|------|
| `mcp__atlassian__getConfluencePage` | `Read(docs/**)` + `Grep` + `mcp__github__get_file_contents` | 로컬 우선, 원격 fallback |
| `mcp__atlassian__searchConfluenceUsingCql` (label='adr') | `Glob(docs/adr/ADR-*.md)` + `Grep` (frontmatter category) | 로컬 파일 검색 |
| `mcp__atlassian__getPagesInConfluenceSpace` | `Glob(docs/domain-knowledge/**)` | 로컬 파일 검색 |
| `mcp__atlassian__getConfluenceSpaces` | (불필요) | 단일 repo 모델 |
| `mcp__atlassian__createConfluencePage` (DocsAgent only) | `Write(docs/**)` + `mcp__github__create_or_update_file` (PR commit 시) | DocsAgent only |
| `mcp__atlassian__updateConfluencePage` (DocsAgent only) | `Edit(docs/**)` + `mcp__github__create_or_update_file` | DocsAgent only |
| `mcp__atlassian__createJiraIssue` (DocsAgent only) | `mcp__github__issue_write` (action='create') | DocsAgent only |
| `mcp__atlassian__editJiraIssue` (DocsAgent only) | `mcp__github__issue_write` (action='update', label 추가/제거) | DocsAgent only |
| `mcp__atlassian__getJiraIssue` | `mcp__github__issue_read` | read-only 누구나 |
| `mcp__atlassian__searchJiraIssuesUsingJql` | `mcp__github__list_issues` + `mcp__github__search_issues` | JQL → GraphQL search syntax |
| `mcp__atlassian__transitionJiraIssue` | (불필요 — label 변경 + Action으로 status 자동) | 상태 전이 model 단순화 |
| `mcp__atlassian__getTransitionsForJiraIssue` | (불필요) | — |
| `mcp__atlassian__addCommentToJiraIssue` (DocsAgent only) | `mcp__github__add_issue_comment` | DocsAgent only |
| Sub-task 관리 | `mcp__github__sub_issue_write` | DocsAgent only |
| Milestone 관리 | `Bash(gh api repos/.../milestones ...)` | DocsAgent only (github MCP에 milestone 도구 부재 시 fallback) |
| Discussions 관리 | `Bash(gh api graphql ...)` | DocsAgent only (Domain KB Q&A) |

### 4.2 DocsAgent 권한 재정의

```yaml
permissions:
  allow:
    # 로컬 파일 write (단독 doc writer)
    - Edit(docs/**)
    - Write(docs/**)
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    # GitHub MCP write
    - mcp__github__issue_write
    - mcp__github__issue_read
    - mcp__github__list_issues
    - mcp__github__search_issues
    - mcp__github__add_issue_comment
    - mcp__github__sub_issue_write
    - mcp__github__create_or_update_file
    - mcp__github__get_file_contents
    - mcp__github__pull_request_read
    - mcp__github__list_pull_requests
    - mcp__github__update_pull_request
    - mcp__github__get_label
    - mcp__github__create_branch
    # gh CLI fallback (Milestone, Discussions)
    - Bash(gh api repos/*/milestones*)
    - Bash(gh api repos/*/discussions*)
    - Bash(gh api graphql*)
    # 작업 파일
    - Bash(mkdir/ls/rm .claude-work/doc-queue/*)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(.claude/**)
    - Edit(config/**)
    - Edit(deploy/**)
    - Edit(scripts/**)
```

### 4.3 기타 23 agent 권한 변경

- Read 전용: `Read(docs/**)`, `Glob(docs/**)`, `Grep`, `mcp__github__issue_read`, `mcp__github__list_issues`, `mcp__github__search_issues`, `mcp__github__get_file_contents`, `mcp__github__pull_request_read`
- Write queue 의뢰 권한: `Edit(.claude-work/doc-queue/**)`, `Write(.claude-work/doc-queue/**)` — 변경 없음
- 외부 도구 wrapper:
  - RequirementsAnalyst: `Bash(codex exec *)` 유지
  - CodexDesignReview, CodexCodeReview: `Bash(node *)` 유지
- atlassian MCP 도구는 모두 0개로

---

## 5. GitHub Actions 자동화 (A+B 그룹)

### 5.1 워크플로우 파일 위치

Plugin SSOT: `<plugin>/templates/github-workflows/`
Consumer 배포: `<consumer-repo>/.github/workflows/` (consumer가 첫 셋업 시 cp)

### 5.2 워크플로우 카탈로그

| 파일 | 그룹 | Trigger | 책임 |
|------|------|---------|------|
| `story-init.yml` | A | `issues: opened` (issue type=story Form) | 다음 KEY 번호 계산 → docs file 생성 PR → Issue body 변환 → 라벨·Milestone 부착 |
| `phase-label-invariant.yml` | A | `issues: labeled` | `phase:*` 라벨 하나만 active 강제 (다른 phase:* 자동 detach) |
| `story-section-1-immutable.yml` | A | `pull_request: opened/synchronize` | docs/stories/**/§1 line range 변경 PR 자동 reject |
| `subissue-from-impl-manifest.yml` | B | `pull_request: synchronize` (path: docs/stories/**) | §8.5 Impl Manifest 매핑표 추가 → file 단위 sub-issue 자동 생성. **Action이 sub-issue 생성의 single source of truth** (DocsAgent는 docs file 작성만, sub-issue write는 호출 안 함) |
| `phase-gate-mergeable.yml` | B | `pull_request: labeled, opened, synchronize` | Phase 1 PR mergeable = `phase:설계-리뷰` + `gate:design-review-pass` / Phase 2 PR mergeable = `phase:보안-테스트` + `gate:security-test-pass` (Branch protection + required check 결합) |
| `fix-ledger-sync.yml` | B | `push: docs/stories/**` (§10 변경) | docs §10 신규 행 commit 감지 → (1) Story Issue에 `[FIX #N]` 코멘트 자동 mirror + (2) 새 행의 "레인" 컬럼 파싱해 `fix:<레인>-retry` 라벨 자동 부착 + (3) RESET 마커 행이면 추가 메시지 코멘트. **fix:* 라벨 부착의 single source of truth** (DocsAgent 직접 부착 안 함) |

### 5.3 워크플로우 파일 배포 메커니즘 (Hybrid iii)

**SessionStart hook**:
- consumer 리포의 `.github/workflows/`에 plugin 권장 7개 워크플로우 파일 부재·SHA drift 감지
- 부재 시: 알림만 ("필수 워크플로우 N개 부재. 다음 명령으로 복사하세요: `cp <plugin-templates-path>/github-workflows/*.yml .github/workflows/`")
- Drift 시: 알림 ("plugin 워크플로우가 갱신됨. consumer 사본과 SHA 다름. 검토·갱신 권장")
- 자동 복사·자동 commit 안 함 (consumer 통제)

**consumer-guide.md 셋업 절차에 명시**:
1. plugin 설치 후 워크플로우 7개 + Issue Forms 3개 + PR template 1개 + CODEOWNERS 1개를 `cp`
2. CODEOWNERS의 team 자리 placeholder를 consumer 조직 team으로 치환
3. `.github/ISSUE_TEMPLATE/config.yml`에서 blank issue 비활성화 (Issue Forms만 강제)
4. Branch protection rule 설정: main 브랜치에 required status checks (`phase-gate-mergeable`) + required reviewers (CODEOWNERS)

---

## 6. 세션 개시 의무 갱신

### 6.1 필수 의존성 SSOT (CLAUDE.md §"세션 개시 의무" 갱신)

**MCP 서버 (1종)**:
- ~~`atlassian` (HTTP)~~ **제거**
- **`github`** **신규 필수** — Issue/PR/sub-issue/comment write 모두 사용

**필수 플러그인 (3 → 4종)**:
- `codex@openai-codex` (유지) — Codex 리뷰 의존
- `superpowers@claude-plugins-official` (유지) — skill 의존
- `claude-md-management@claude-plugins-official` (유지) — DocsAgent skill 의존
- **`github@claude-plugins-official`** **신규 필수** — 권장에서 격상

**필수 CLI (1 → 2종)**:
- `codex` (유지) — RequirementsAnalyst
- **`gh`** **신규 필수** — Milestone·Discussions·gh api 호출 (DocsAgent fallback)

**권장 플러그인 (4종)**:
- `atlassian@claude-plugins-official` **삭제**
- `github@claude-plugins-official` **격상 (필수로)**
- 나머지 4종 유지: `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

### 6.2 세션 개시 추가 검증

- consumer 리포의 `.github/workflows/` 6개 plugin 워크플로우 부재 + SHA drift 검사
- `.github/ISSUE_TEMPLATE/story.yml`, `bug.yml`, `audit.yml` 부재 검사
- `.github/PULL_REQUEST_TEMPLATE.md` 부재 검사
- `CODEOWNERS` 파일 architect/domain-expert team 매핑 부재 검사
- consumer가 `gh auth status` 인증 상태 확인

부재·drift 시 알림만, 자동 복사·자동 인증 안 함. 사용자 액션 대기.

### 6.3 자동 복구 가능 케이스

- 플러그인 cache 있으나 `enabledPlugins == false` → `~/.claude/settings.json` 직접 토글 (atlassian 제거 + github 활성화)

### 6.4 사용자 요구 (blocking) 케이스

- `mcp__github__*` 미인증 → `/mcp` 재인증
- `github@claude-plugins-official` cache 부재 → `/plugins install github@claude-plugins-official`
- `gh` CLI 부재 → 설치 가이드 제시

---

## 7. `.claude/_overlay/project.yaml` 스키마

### 7.1 제거되는 키

```yaml
atlassian:
  site
  confluence:
    space_key
    stories_parent_page_id
    domain_knowledge_parent_page_id
    adr_root_page_id
  jira:
    project_key
    transitions:
      to_in_progress
      to_done
```

### 7.2 신설되는 키

```yaml
github:
  org: <string>                       # GitHub org/user (예: "mctrader")
  repo: <string>                      # repo name (예: "myproject")
  default_branch: main                # default merge target
  pr_title_prefix_template: "[{key}] {title}"   # 예: [PLG-3] Add idempotency key
  story_key_prefix: PLG               # Issue 번호 prefix (Jira project_key 대체, 예: "PLG-7")
  codeowners:
    architect_team: "@org/architects"
    domain_expert_team: "@org/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"  # DomainAgent Q&A 카테고리
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"

labels:
  components: [...]                   # consumer 정의 (기존 유지)
```

### 7.3 스키마 문서 (`docs/project-config-schema.md`)

- atlassian.* 섹션 전부 삭제
- github.* 섹션 신설 (위 7.2 형식 정확히 명시)
- labels.components 섹션 유지

---

## 8. Plugin 변경 항목 체크리스트

| # | 파일/디렉토리 | 변경 유형 | 변경 내용 |
|---|--------------|----------|----------|
| 1 | `CLAUDE.md` | major rewrite | atlassian 의존 제거 + GitHub-native 워크플로우 + 세션 개시 의무 갱신 + ADR/Bug/Confluence Story 페이지 규약 섹션 모두 GitHub primitive로 |
| 2 | `docs/orchestrator-playbook.md` | major rewrite | §1.1 dependency check, §3B preflight, §11 write queue, §12 Context Packet, §12.5 Project Config Packet 모두 갱신. Story 페이지 동기화 체크리스트는 docs file 동기화로 |
| 3 | `docs/project-config-schema.md` | replace | atlassian.* 제거, github.* 신설 |
| 4 | `docs/consumer-guide.md` | major rewrite | GitHub repo 셋업 절차, Workflow 파일 cp 안내, CODEOWNERS·Issue Forms·Branch protection 안내 |
| 5 | `agents/DocsAgent.md` | major rewrite | 권한 재정의, Confluence/Jira 호출 → GitHub primitive 매핑, FIX Ledger 갱신 절차 재작성, 코멘트 prefix 10종은 Issue comment로 |
| 6 | `agents/PMOAgent.md` | rewrite | Confluence read → docs Read, Jira search → GitHub list_issues |
| 7 | `agents/RequirementsPLAgent.md` | rewrite | atlassian read → Read/Glob/Grep + github MCP read |
| 8 | `agents/DomainAgent.md` | rewrite | 동일 변환, Domain KB 트리는 docs/domain-knowledge/ 로 |
| 9 | `agents/RequirementsAnalystAgent.md` | rewrite | 동일 변환 |
| 10 | `agents/ResearcherAgent.md` | rewrite | 동일 변환 |
| 11 | `agents/ArchitectAgent.md` | rewrite | atlassian read → Read + github MCP read. ADR fetch 경로 변경 |
| 12 | `agents/CodebaseMapperAgent.md` | rewrite | 동일 변환 |
| 13 | `agents/RefactorAgent.md` | rewrite | 동일 변환 |
| 14 | `agents/DesignReviewPLAgent.md`, `agents/ClaudeDesignReviewAgent.md`, `agents/CodexDesignReviewAgent.md` | rewrite | atlassian read 잔여 제거 |
| 15 | `agents/CodeReviewPLAgent.md`, `agents/ClaudeCodeReviewAgent.md`, `agents/CodexCodeReviewAgent.md` | rewrite | 동일 |
| 16 | `agents/SecurityTestPLAgent.md`, `agents/ClaudeSecurityTestAgent.md`, `agents/CodexSecurityTestAgent.md` | rewrite | 동일 + Dependabot/CodeQL/Secret Scanning 1차 layer 활용 명시 |
| 17 | `agents/TestAgent.md` | rewrite | 동일 |
| 18 | `agents/DeveloperPLAgent.md`, `agents/QADeveloperAgent.md` | rewrite | 동일 |
| 19 | `agents/DeveloperAgent.md`, `agents/DataEngineerAgent.md`, `agents/InfraEngineerAgent.md` | minor | atlassian read 잔여 제거 (대부분 직접 호출 없음) |
| 20 | `templates/story-page-structure.md` | rewrite | "Confluence 페이지" 헤더 → "docs/stories markdown" 헤더, §1-11 섹션 규격 유지, §1 변조 금지 invariant 명시 |
| 21 | `templates/change-plan.md` | unchanged | Git-versioned 그대로 |
| 22 | `templates/adr.md` | minor | frontmatter `category:` 필드 추가, 본문 그대로 |
| 23 | `templates/impl-manifest.md` | rewrite | sub-task → Sub-issue 형식 (GitHub Issue body 양식) |
| 24 | `templates/github-workflows/*.yml` | **신설** (6개) | story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync |
| 25 | `templates/github-issue-forms/story.yml`, `bug.yml`, `audit.yml` | **신설** (3개) | Issue Forms 양식 |
| 26 | `templates/github-pr-template.md` | **신설** | Phase 1 PR / Phase 2 PR 양식 분리 (조건부 섹션) |
| 27 | `templates/CODEOWNERS.template` | **신설** | architect_team / domain_expert_team placeholder 포함 |
| 28 | `presets/<all>` | rewrite | atlassian.* override 제거, github.* 추가 |
| 29 | `.claude/settings.json` | rewrite | atlassian MCP allow 제거, github MCP + gh CLI Bash 추가 |
| 30 | `.claude/settings.local.json` | rewrite | 동일 |
| 31 | `docs/migration-guide.md` | append | 기존 파일은 plugin version-bump 가이드(consumer overlay 마이그레이션). atlassian 제거 release를 위한 신규 섹션 1개 추가 (예: `## v0.7 → v0.8 (Atlassian 제거 + GitHub 전환)`). 기존 섹션 보존 |
| 32 | `README.md`, `CHANGELOG.md` | update | 변경 사항 반영, breaking change 명시 |

---

## 9. Error Handling

### 9.1 Action 실패

- 예: `story-init.yml`이 PR 생성 실패 (token 만료 등)
- 처리: Issue comment에 에러 기록, 라벨 `automation:failed` 부착, Orchestrator가 SessionStart 시 감지 → 사용자 알림
- 복구: 사용자 수동 PR 생성 또는 워크플로우 재실행

### 9.2 GitHub MCP 인증 만료

- 처리: 세션 개시에서 `ToolSearch select:mcp__github__issue_write` 결과로 감지
- 복구: 사용자 `/mcp` 재인증 요구 (blocking, 작업 중단)

### 9.3 gh CLI 부재 또는 인증 만료

- 처리: 세션 개시에서 `which gh` + `gh auth status` 검증
- 복구: 부재 시 설치 가이드, 인증 만료 시 `gh auth login` 안내, blocking

### 9.4 Workflow file drift

- 처리: SessionStart hook이 plugin templates SHA와 consumer `.github/workflows/` 사본 SHA 비교
- 복구: 알림만, 사용자가 검토·갱신 결정

### 9.5 CODEOWNERS 누락

- 처리: SessionStart에서 부재 검사
- 복구: 부재 시 알림 + Phase 1 PR이 architect review 자동 받지 못하면 Orchestrator가 절차적 강제 (DesignReview lane 진입 차단)

### 9.6 phase 라벨 invariant 위반

- 처리: `phase-label-invariant.yml`이 단일 active 강제
- 복구: 자동 — 다른 phase:* 라벨 attach 시 기존 자동 detach

### 9.7 §1 변조 시도

- 처리: `story-section-1-immutable.yml`이 §1 line range 변경 PR 자동 reject
- 복구: 정당한 정정 필요 시 — Action 우회 메커니즘 없음. 사용자가 별도 PR + bypass approval로 해결 (운영 빈도 0에 가까움)

---

## 10. Testing

Plugin 자체의 변경이라 unit test 대상은:

| 영역 | 테스트 방법 |
|------|------------|
| Workflow `.yml` 파일 | GitHub Actions runner에서 dry-run (consumer 리포 시뮬레이션). plugin repo 자체에 test fixture 두고 CI에서 실행 |
| `project.yaml` 스키마 | `jsonschema` 라이브러리로 validate (기존 패턴 활용) |
| Agent frontmatter 일관성 | 24 agent md의 `permissions` 블록이 atlassian MCP 도구를 0개 참조하는지 grep |
| Documentation 일관성 | CLAUDE.md / playbook / agent md 사이의 cross-reference 깨짐 검사 (markdown link checker) |
| Atlassian 잔재 | repo 전체에서 `atlassian`·`Confluence`·`Jira`·`mcp__atlassian__` 0회 등장 (예외: CHANGELOG 마이그레이션 기록) |
| Action 단위 테스트 | `act` (https://github.com/nektos/act) 또는 GitHub-hosted runner에서 happy path + edge case |

---

## 11. Rollout / Release

Plugin 자체의 변경이라 release 단위:

- **v0.x.0** (current latest 다음 minor): atlassian 제거 + github 도입. **Breaking change**
- CHANGELOG에 명시: "atlassian backend 제거. consumer는 GitHub-only로만 사용 가능. project.yaml 스키마 변경 필요"
- 기존 consumer 0이므로 마이그레이션 가이드 불필요

---

## 12. Open Questions

본 spec에서 결정 보류한 항목은 없음 (브레인스토밍에서 모두 합의). 구현 단계에서 발견되는 detail은 implementation plan에서 다룬다.

---

## 13. References

- Brainstorming 결정 누적 (Q1–Q8)
- Atlassian MCP 사용 인벤토리 (Explore agent 산출, 본 spec §2 입력)
- 현 CLAUDE.md (atlassian 의존 서술)
- 현 `agents/DocsAgent.md` (단독 doc writer 권한 모델)
- 현 `docs/orchestrator-playbook.md` (Story 페이지 동기화 체크리스트)
- 현 `docs/project-config-schema.md` (atlassian.* 키 정의)
