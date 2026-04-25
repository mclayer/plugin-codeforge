# Atlassian → GitHub Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** codeforge plugin에서 atlassian MCP 의존을 hard remove하고, Confluence/Jira의 모든 책임을 GitHub primitive(Issues, PR, Milestones, Sub-issues, Projects v2, Discussions, Actions, repo files, CODEOWNERS)로 이전한다.

**Architecture:** Story 페이지 §1–11은 `docs/stories/<KEY>.md` single-file SSOT. ADR은 `docs/adr/ADR-NNN-<slug>.md` flat. Domain KB는 `docs/domain-knowledge/<area>/<topic>.md` 계층. Workflow는 1 Story = 2 PRs (Phase 1: docs only / Phase 2: code+docs append). 6개 GitHub Actions가 invariant·자동화 강제. DocsAgent는 단독 doc writer로 Edit/Write(docs/**) + GitHub MCP write 도구 보유.

**Tech Stack:** Markdown(plugin core 문서), YAML(GitHub Actions·Issue Forms), JSON(`.claude/settings.json`), Bash(validation scripts·gh CLI fallback), GitHub MCP plugin tools.

**Spec reference:** [docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md](../specs/2026-04-25-atlassian-to-github-migration-design.md)

---

## File Structure

### Created (신규)

| Path | 책임 |
|------|------|
| `scripts/check-no-atlassian.sh` | 코드베이스 atlassian 잔재 0회 검증 (Test 1) |
| `scripts/check-agent-frontmatter.sh` | 24 agent md `permissions` 블록의 atlassian 도구 0건 검증 (Test 2) |
| `scripts/check-doc-links.sh` | docs/* 마크다운 cross-reference 깨짐 검사 (Test 3) |
| `templates/CODEOWNERS.template` | architect_team / domain_expert_team placeholder 포함 |
| `templates/github-pr-template.md` | Phase 1 / Phase 2 양식 분리 |
| `templates/github-issue-forms/story.yml` | Story 신규 입력 form (§1 verbatim 강제) |
| `templates/github-issue-forms/bug.yml` | Bug 입력 form |
| `templates/github-issue-forms/audit.yml` | Audit Story (post-hotfix) form |
| `templates/github-workflows/story-init.yml` | Issue 생성 → docs file 생성 PR + Issue body 변환 |
| `templates/github-workflows/phase-label-invariant.yml` | `phase:*` single-active 강제 |
| `templates/github-workflows/story-section-1-immutable.yml` | §1 line range 변경 PR reject |
| `templates/github-workflows/subissue-from-impl-manifest.yml` | §8.5 매핑표 → file 단위 sub-issue 자동 생성 |
| `templates/github-workflows/phase-gate-mergeable.yml` | phase + gate 라벨 둘 다 있어야 mergeable |
| `templates/github-workflows/fix-ledger-sync.yml` | docs §10 commit → Issue comment + fix:* 라벨 |

### Modified (기존 수정)

| Path | 변경 유형 |
|------|----------|
| `CLAUDE.md` | major rewrite (atlassian 의존 제거 + GitHub-native + 세션 개시 의무 갱신) |
| `docs/orchestrator-playbook.md` | major rewrite (§1.1 / §3B / §11 / §12 / §12.5 갱신) |
| `docs/project-config-schema.md` | atlassian.* 제거, github.* 신설 |
| `docs/consumer-guide.md` | GitHub repo 셋업 절차로 rewrite |
| `docs/migration-guide.md` | v0.7→v0.8 섹션 append (기존 섹션 유지) |
| `agents/DocsAgent.md` | major rewrite (권한 재정의 + Confluence/Jira 호출 → GitHub) |
| `agents/PMOAgent.md`, `RequirementsPLAgent.md`, `DomainAgent.md`, `RequirementsAnalystAgent.md`, `ResearcherAgent.md` | rewrite (atlassian read → docs Read + github MCP read) |
| `agents/ArchitectAgent.md`, `CodebaseMapperAgent.md`, `RefactorAgent.md` | rewrite (동일 변환 + ADR fetch 경로) |
| `agents/DesignReviewPLAgent.md`, `ClaudeDesignReviewAgent.md`, `CodexDesignReviewAgent.md` | rewrite (atlassian read 잔여 제거) |
| `agents/CodeReviewPLAgent.md`, `ClaudeCodeReviewAgent.md`, `CodexCodeReviewAgent.md` | rewrite |
| `agents/SecurityTestPLAgent.md`, `ClaudeSecurityTestAgent.md`, `CodexSecurityTestAgent.md` | rewrite + Dependabot/CodeQL/Secret Scanning 1차 layer 명시 |
| `agents/TestAgent.md`, `DeveloperPLAgent.md`, `QADeveloperAgent.md` | rewrite |
| `agents/DeveloperAgent.md`, `DataEngineerAgent.md`, `InfraEngineerAgent.md` | minor (잔여 제거) |
| `templates/story-page-structure.md` | header rewrite + §1 변조 금지 invariant 명시 |
| `templates/adr.md` | frontmatter `category:` 필드 추가 |
| `templates/impl-manifest.md` | sub-issue 형식 |
| `presets/webapp/agents/*` | atlassian 잔재 검사·제거 |
| `.claude/settings.json` | atlassian MCP allow 제거, github MCP + gh CLI Bash 추가 |
| `.claude/settings.local.json` | 동일 |
| `README.md` | breaking change·신규 backend 명시 |
| `CHANGELOG.md` | v0.8 (Atlassian 제거) 섹션 추가 |

---

## Execution Order

1. **Phase A (Tasks 1–4): Validation infra + Schema foundation**
2. **Phase B (Tasks 5–13): New GitHub artifacts (workflows · forms · templates)**
3. **Phase C (Tasks 14–16): Core docs rewrite (CLAUDE.md · playbook · DocsAgent)**
4. **Phase D (Tasks 17–22): Other 23 agents**
5. **Phase E (Tasks 23–27): Templates · consumer-guide · migration-guide · README · CHANGELOG**
6. **Phase F (Task 28): Final validation**

각 Task는 독립 commit. Phase 경계마다 전체 validation 재실행.

---

## Phase A: Validation Infra + Schema Foundation

### Task 1: validation 스크립트 작성 (TDD foundation)

**Goal**: atlassian 잔재 검출 + agent frontmatter 일관성 + 마크다운 링크 깨짐 검사 스크립트 3개 작성. 현재 상태에서는 모두 FAIL해야 함 (atlassian 도처 등장).

**Files:**
- Create: `scripts/check-no-atlassian.sh`
- Create: `scripts/check-agent-frontmatter.sh`
- Create: `scripts/check-doc-links.sh`

- [ ] **Step 1: scripts/check-no-atlassian.sh 작성**

```bash
#!/usr/bin/env bash
# 검사: atlassian 잔재가 코드베이스에 남아 있는가
# 허용 위치 (allowlist): CHANGELOG.md(역사 기록), docs/migration-guide.md(version-bump 가이드)
set -euo pipefail

cd "$(dirname "$0")/.."

ALLOWLIST=(
  "CHANGELOG.md"
  "docs/migration-guide.md"
  "docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md"
  "docs/superpowers/plans/2026-04-25-atlassian-to-github-migration.md"
  "scripts/check-no-atlassian.sh"
)

# atlassian|Confluence|Jira|mcp__atlassian 패턴 grep
HITS=$(grep -rEn 'atlassian|Confluence|Jira|mcp__atlassian' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.json' \
  --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
  . 2>/dev/null || true)

if [[ -z "$HITS" ]]; then
  echo "✓ atlassian 잔재 없음"
  exit 0
fi

# allowlist 필터
FILTERED=$(echo "$HITS" | while IFS= read -r line; do
  file="${line%%:*}"
  file="${file#./}"
  ALLOWED=false
  for allow in "${ALLOWLIST[@]}"; do
    if [[ "$file" == "$allow" ]]; then ALLOWED=true; break; fi
  done
  if ! $ALLOWED; then echo "$line"; fi
done)

if [[ -z "$FILTERED" ]]; then
  echo "✓ atlassian 잔재는 allowlist 파일에만 존재"
  exit 0
fi

echo "✗ atlassian 잔재 발견 (allowlist 외):"
echo "$FILTERED"
exit 1
```

- [ ] **Step 2: scripts/check-agent-frontmatter.sh 작성**

```bash
#!/usr/bin/env bash
# 검사: 24 agent md의 frontmatter `permissions:` 블록에 atlassian MCP 도구가 0건인가
set -euo pipefail

cd "$(dirname "$0")/.."

FAIL=0
for f in agents/*.md; do
  # frontmatter 추출 (첫 ---와 두 번째 --- 사이)
  fm=$(awk '/^---$/{c++; next} c==1' "$f" 2>/dev/null || true)
  if echo "$fm" | grep -qE 'mcp__atlassian__'; then
    echo "✗ $f frontmatter에 atlassian MCP 도구 있음:"
    echo "$fm" | grep -E 'mcp__atlassian__' | sed 's/^/    /'
    FAIL=1
  fi
done

if [[ $FAIL -eq 0 ]]; then
  echo "✓ 모든 agent frontmatter에서 atlassian MCP 도구 0건"
fi
exit $FAIL
```

- [ ] **Step 3: scripts/check-doc-links.sh 작성**

```bash
#!/usr/bin/env bash
# 검사: docs/* 안의 마크다운 상대 링크가 깨지지 않았는가
set -euo pipefail

cd "$(dirname "$0")/.."

FAIL=0
# (link_text)(relative_path) 추출, 외부 URL/anchor 전용 링크 제외
while IFS= read -r line; do
  file="${line%%:*}"
  rest="${line#*:}"
  # [text](path) 추출
  while [[ "$rest" =~ \]\(([^\)]+)\) ]]; do
    target="${BASH_REMATCH[1]}"
    rest="${rest#*]\(${target}\)}"
    # 외부 URL skip
    [[ "$target" =~ ^https?:// ]] && continue
    [[ "$target" =~ ^mailto: ]] && continue
    # anchor 분리
    target_path="${target%%#*}"
    [[ -z "$target_path" ]] && continue  # anchor 전용
    # 절대 경로화
    dir="$(dirname "$file")"
    abs_path="$dir/$target_path"
    if [[ ! -e "$abs_path" ]]; then
      echo "✗ $file: 깨진 링크 → $target"
      FAIL=1
    fi
  done
done < <(grep -rn '](.*)' docs/ CLAUDE.md README.md agents/ 2>/dev/null || true)

if [[ $FAIL -eq 0 ]]; then echo "✓ 마크다운 링크 무결"; fi
exit $FAIL
```

- [ ] **Step 4: 권한 부여 + 현재 상태에서 실행 (모두 FAIL이어야 함 — 아직 atlassian 도처)**

```bash
chmod +x scripts/check-no-atlassian.sh scripts/check-agent-frontmatter.sh scripts/check-doc-links.sh
./scripts/check-no-atlassian.sh && echo "ERR: 통과하면 안됨" || echo "OK: 예상대로 FAIL"
./scripts/check-agent-frontmatter.sh && echo "ERR: 통과하면 안됨" || echo "OK: 예상대로 FAIL"
./scripts/check-doc-links.sh
```

Expected: 처음 두 스크립트 FAIL (exit 1), 세 번째는 PASS (현재 링크는 무결할 것)

- [ ] **Step 5: Commit**

```bash
git add scripts/
git commit -m "test: atlassian → github 마이그레이션용 validation 스크립트 3종 추가"
```

---

### Task 2: docs/project-config-schema.md 갱신 (atlassian.* → github.*)

**Goal**: spec §7 그대로 반영. atlassian.* 키 정의 전부 삭제, github.* 키 정의 신설.

**Files:**
- Modify: `docs/project-config-schema.md`

- [ ] **Step 1: 현 atlassian.* 섹션 위치 확인**

```bash
grep -n 'atlassian\|jira\|confluence\|github\|labels' docs/project-config-schema.md
```

- [ ] **Step 2: atlassian 섹션 삭제 + github 섹션 신설** (Edit 도구로 섹션 단위 교체)

신규 github 섹션 본문:

````markdown
## github

| key | type | required | 설명 |
|-----|------|----------|------|
| `org` | string | ✓ | GitHub org 또는 user (예: "mctrader") |
| `repo` | string | ✓ | repo 이름 (예: "myproject") |
| `default_branch` | string | ✓ | merge target (보통 `main`) |
| `pr_title_prefix_template` | string | ✓ | PR 제목 prefix 템플릿. placeholder: `{key}`, `{title}`. 예: `"[{key}] {title}"` → `[PLG-3] Add idempotency key` |
| `story_key_prefix` | string | ✓ | Issue 번호 prefix (Jira project_key 대체). 예: `PLG` → `PLG-7` |
| `codeowners.architect_team` | string | ✓ | `docs/adr/**`·`docs/change-plans/**` review 강제 team. 예: `"@org/architects"` |
| `codeowners.domain_expert_team` | string | ✓ | `docs/domain-knowledge/**` review 강제 team. 예: `"@org/domain-experts"` |
| `discussions.domain_kb_category` | string | ✓ | DomainAgent Q&A 카테고리. 예: `"Domain Q&A"` |
| `milestone.epic_naming_pattern` | string | ✓ | Milestone 명명 패턴. placeholder: `{key}`, `{slug}`. 예: `"Epic-{key}-{slug}"` |

### 예시

```yaml
github:
  org: mctrader
  repo: myproject
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: PLG
  codeowners:
    architect_team: "@mctrader/architects"
    domain_expert_team: "@mctrader/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
```
````

기존 atlassian.* 섹션은 통째로 제거.

- [ ] **Step 3: 검증**

```bash
grep -E 'atlassian|jira|confluence' docs/project-config-schema.md && echo "ERR: 잔재" || echo "OK"
grep -E 'github\.org|story_key_prefix|codeowners' docs/project-config-schema.md && echo "OK: github 섹션 존재" || echo "ERR"
```

- [ ] **Step 4: Commit**

```bash
git add docs/project-config-schema.md
git commit -m "schema: project.yaml의 atlassian.* 제거, github.* 신설"
```

---

### Task 3: .claude/settings.json + settings.local.json (MCP allow 갱신)

**Goal**: atlassian MCP allow 제거, github MCP + gh CLI Bash 추가.

**Files:**
- Modify: `.claude/settings.json`
- Modify: `.claude/settings.local.json`

- [ ] **Step 1: settings.json 갱신**

기존 atlassian 4건 (`mcp__atlassian__searchConfluenceUsingCql`, `getConfluencePage`, `searchJiraIssuesUsingJql`, `getJiraIssue`)을 다음으로 교체:

```json
"mcp__github__issue_read",
"mcp__github__list_issues",
"mcp__github__search_issues",
"mcp__github__pull_request_read",
"mcp__github__list_pull_requests",
"mcp__github__get_file_contents",
"mcp__github__search_code",
"mcp__github__get_label",
"Bash(gh auth status)",
"Bash(gh api repos/*)",
```

- [ ] **Step 2: settings.local.json 갱신**

기존 `mcp__atlassian__*` 도구 전부 (인증·리소스·Confluence·Jira) 제거. 대체로 다음 추가:

```json
"mcp__github__issue_write",
"mcp__github__add_issue_comment",
"mcp__github__sub_issue_write",
"mcp__github__create_or_update_file",
"mcp__github__create_pull_request",
"mcp__github__update_pull_request",
"mcp__github__merge_pull_request",
"mcp__github__create_branch",
"Bash(gh api repos/*/milestones*)",
"Bash(gh api repos/*/discussions*)",
"Bash(gh api graphql*)",
"Bash(gh pr *)",
"Bash(gh issue *)",
"Bash(gh label *)"
```

- [ ] **Step 3: 검증**

```bash
grep -c 'mcp__atlassian__' .claude/settings.json .claude/settings.local.json
# 결과: 0:0
grep -c 'mcp__github__' .claude/settings.json .claude/settings.local.json
# 결과: >= 4 in settings.json, >= 6 in settings.local.json
```

- [ ] **Step 4: Commit**

```bash
git add .claude/settings.json .claude/settings.local.json
git commit -m "settings: atlassian MCP allow 제거, github MCP + gh CLI 추가"
```

---

### Task 4: presets/webapp atlassian 잔재 검사·정리

**Goal**: presets/webapp/agents/* 안의 atlassian 잔재 확인. presets는 overlay 양식이므로 보통 비어 있을 가능성 큼.

**Files:**
- Modify (필요 시): `presets/webapp/agents/BackendDeveloperAgent.md`
- Modify (필요 시): `presets/webapp/agents/FrontendDeveloperAgent.md`
- Modify (필요 시): `presets/webapp/README.md` (있으면)

- [ ] **Step 1: 잔재 검사**

```bash
grep -rEn 'atlassian|Confluence|Jira|mcp__atlassian' presets/ || echo "✓ 잔재 없음"
```

- [ ] **Step 2: 잔재 발견 시 제거**

각 발견 위치를 GitHub-equivalent 표현으로 교체. 예: `Confluence Story 페이지` → `docs/stories/<KEY>.md`. 발견 0건이면 이 step skip.

- [ ] **Step 3: scripts/check-no-atlassian.sh 부분 통과 확인**

```bash
./scripts/check-no-atlassian.sh; echo "exit=$?"
# atlassian 도처 남아 있으므로 여전히 FAIL — presets만 클린
```

- [ ] **Step 4: Commit (변경 있을 시)**

```bash
git add presets/
git commit -m "presets(webapp): atlassian 잔재 제거"
# 변경 없으면 skip
```

---

## Phase B: New GitHub Artifacts (Workflows · Forms · Templates)

### Task 5: templates/CODEOWNERS.template 작성

**Files:**
- Create: `templates/CODEOWNERS.template`

- [ ] **Step 1: 파일 작성**

```
# CodeForge plugin이 권장하는 CODEOWNERS template
# consumer가 자기 organization team으로 placeholder 치환 후 .github/CODEOWNERS로 복사

# 설계 결정 (ADR) — architect team 의무 review
docs/adr/**                                   @ORG/ARCHITECT_TEAM

# 변경 계획 (Change Plan) — architect team 의무 review
docs/change-plans/**                          @ORG/ARCHITECT_TEAM

# Story 페이지 — architect team review (Phase 1 PR 자동 결재)
docs/stories/**                               @ORG/ARCHITECT_TEAM

# Domain Knowledge — domain expert team review
docs/domain-knowledge/**                      @ORG/DOMAIN_EXPERT_TEAM

# GitHub Workflow 변경 — architect team review (security-sensitive)
.github/workflows/**                          @ORG/ARCHITECT_TEAM

# Plugin overlay 설정 — architect team review
.claude/_overlay/**                           @ORG/ARCHITECT_TEAM
```

- [ ] **Step 2: Commit**

```bash
git add templates/CODEOWNERS.template
git commit -m "feat(templates): CODEOWNERS template 추가 — architect/domain-expert team 분리"
```

---

### Task 6: templates/github-issue-forms/story.yml 작성

**Files:**
- Create: `templates/github-issue-forms/story.yml`

- [ ] **Step 1: 파일 작성**

```yaml
name: Story
description: 신규 사용자 요구사항 (Story 1건 = PR 1쌍)
title: "[STORY] "
labels: ["type:story", "phase:요구사항"]
body:
  - type: markdown
    attributes:
      value: |
        ## Story 요청
        이 form은 codeforge plugin이 사용하는 Story 신규 입력 form입니다.
        제출 후 `story-init.yml` Action이 자동으로 다음을 수행합니다:
        1. `<story_key_prefix>-N` 다음 번호 계산
        2. `docs/stories/<KEY>.md` 생성 (§1=아래 입력, §2-11=placeholder)
        3. Phase 1 PR 자동 생성 (architect team CODEOWNERS auto-review)
        4. Issue body를 docs file 링크로 갱신
  - type: textarea
    id: user-requirement-verbatim
    attributes:
      label: 사용자 요구사항 (변조 금지 verbatim)
      description: |
        이 텍스트는 docs/stories/<KEY>.md §1에 그대로 복사됩니다.
        story-section-1-immutable.yml Action이 이후 §1 변경을 자동 reject합니다.
        가능한 한 정확하고 완결된 형태로 입력하세요.
      placeholder: 예) 결제 시스템에 idempotency key 도입 — 같은 결제 요청이 네트워크 재시도로 중복 처리되지 않도록 한다.
    validations:
      required: true
  - type: input
    id: epic-milestone
    attributes:
      label: Epic Milestone (선택)
      description: 이 Story가 속한 Epic Milestone 번호. 없으면 비워두세요.
      placeholder: 예) 3
  - type: dropdown
    id: component
    attributes:
      label: Component (선택)
      description: 주 영향 component. consumer overlay project.yaml `labels.components`에 정의된 값.
      options:
        - (선택 안 함)
        - backend
        - frontend
        - infra
        - data
        - other
    validations:
      required: false
```

- [ ] **Step 2: yamllint 검증**

```bash
which yamllint || pip install yamllint
yamllint templates/github-issue-forms/story.yml
```

Expected: PASS (warning 허용, error 0)

- [ ] **Step 3: Commit**

```bash
git add templates/github-issue-forms/story.yml
git commit -m "feat(templates): Story Issue Form 추가 — §1 verbatim 입력 강제"
```

---

### Task 7: templates/github-issue-forms/bug.yml 작성

**Files:**
- Create: `templates/github-issue-forms/bug.yml`

- [ ] **Step 1: 파일 작성**

```yaml
name: Bug
description: 버그 리포트
title: "[BUG] "
labels: ["type:bug"]
body:
  - type: textarea
    id: summary
    attributes:
      label: 증상
      description: 어떤 기대 동작 vs 실제 동작
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: 재현 절차
      placeholder: |
        1. ...
        2. ...
        3. 발생: ...
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: 기대 동작
    validations:
      required: true
  - type: textarea
    id: env
    attributes:
      label: 환경
      placeholder: OS / 버전 / 설정 / 재현 빈도
  - type: dropdown
    id: severity
    attributes:
      label: Severity
      options:
        - P0 — 차단·데이터 손실
        - P1 — 주요 기능 장애
        - P2 — 경미·우회 가능
    validations:
      required: true
```

- [ ] **Step 2: yamllint + Commit**

```bash
yamllint templates/github-issue-forms/bug.yml
git add templates/github-issue-forms/bug.yml
git commit -m "feat(templates): Bug Issue Form 추가"
```

---

### Task 8: templates/github-issue-forms/audit.yml 작성

**Files:**
- Create: `templates/github-issue-forms/audit.yml`

- [ ] **Step 1: 파일 작성**

```yaml
name: Audit (post-hotfix)
description: Hotfix 사후 감사 Story
title: "[AUDIT] "
labels: ["type:story", "audit:post-hotfix", "phase:요구사항"]
body:
  - type: markdown
    attributes:
      value: |
        ## Hotfix 사후 감사
        이 form은 hotfix 머지 후 다음 세션에서 자동 생성되는 Audit Story 형식입니다.
        Hotfix가 우회한 정상 7-lane 통과를 사후 보강하기 위한 것입니다.
  - type: input
    id: hotfix-pr
    attributes:
      label: Hotfix PR 번호
      placeholder: 예) #142
    validations:
      required: true
  - type: textarea
    id: hotfix-summary
    attributes:
      label: Hotfix 변경 요약
      description: 어떤 변경이 어떻게 우회 적용되었는가
    validations:
      required: true
  - type: textarea
    id: skipped-lanes
    attributes:
      label: 우회된 lane 목록
      placeholder: |
        - 설계 리뷰: 생략 (긴급 운영 장애)
        - 보안 테스트: 생략
    validations:
      required: true
  - type: textarea
    id: audit-scope
    attributes:
      label: 사후 감사 범위
      description: Audit Story가 대상으로 할 게이트
      placeholder: |
        - 설계 리뷰 retroactive 수행
        - 보안 테스트 retroactive 수행
        - Change Plan §3 보강
    validations:
      required: true
```

- [ ] **Step 2: yamllint + Commit**

```bash
yamllint templates/github-issue-forms/audit.yml
git add templates/github-issue-forms/audit.yml
git commit -m "feat(templates): Audit Issue Form 추가 — post-hotfix retroactive lane"
```

---

### Task 9: templates/github-pr-template.md 작성

**Goal**: Phase 1 (docs only) / Phase 2 (code+docs append) 양식을 한 파일에 조건부 섹션으로 분리. PR body 생성 시 해당 phase 섹션만 채움.

**Files:**
- Create: `templates/github-pr-template.md`

- [ ] **Step 1: 파일 작성**

```markdown
<!--
  CodeForge PR Template — 다음 두 형식 중 하나를 사용하세요.

  Phase 1 PR (요구사항·설계·설계리뷰 lane): docs/stories/**/§1-7 + docs/change-plans/**/+ docs/adr/**
  Phase 2 PR (구현·구현리뷰·구현테스트·보안테스트 lane): src/** + tests/** + docs/stories/**/§8-11 append

  사용하지 않는 phase 섹션은 통째로 삭제하세요.
-->

## Story

- Story Issue: # (자동 매핑)
- Story SSOT: `docs/stories/<KEY>.md`
- Change Plan: `docs/change-plans/<slug>.md`

---

## (Phase 1 only) 요구사항·설계·설계리뷰 PR

### 변경 요약
<!-- 무엇을 했는가, 왜 (1-3 bullet) -->

### 핵심 설계 결정
<!-- ADR 신규/갱신 여부, 핵심 결정 근거 -->
- ADR: `docs/adr/ADR-NNN-<slug>.md`
- 결정 근거: ...

### 설계 리뷰 PASS 증거
- 설계 리뷰 iteration: <N>회
- DesignReviewPL 종합 판정: PASS
- ADR 정합성: 위반 0건
- (또는) Change Plan §3 vs ADR 정합성 확인 결과

### Test plan (Phase 1)
<!-- 본 PR 머지 전에 수행할 검토 -->
- [ ] Story §1 verbatim 그대로 (story-init.yml 결과 검증)
- [ ] §3-§7 모두 채워짐 (placeholder 0건)
- [ ] ADR 정합성 위반 0건
- [ ] CodebaseMapper 분석 §2 ↔ Refactor 제안 §3 대립 조정 명시

---

## (Phase 2 only) 구현·구현리뷰·구현테스트·보안테스트 PR

Closes #<Story Issue 번호>

### 변경 요약
<!-- 무엇을 했는가, 왜 (1-3 bullet) -->

### Impl Manifest §8.5
<!-- subissue-from-impl-manifest.yml이 자동 생성하는 sub-issue 목록 (자동 채움) -->

### Test plan (Phase 2)
- [ ] 단위 테스트 PASS
- [ ] 통합 테스트 PASS
- [ ] 인프라 테스트 PASS (해당 시)
- [ ] 성능 테스트: baseline 대비 mean ≤ +10%
- [ ] 보안 테스트 PASS (Dependabot/CodeQL/Secret Scanning + Claude/Codex Security)

### FIX 이력
<!-- docs/stories/<KEY>.md §10 FIX Ledger 참조 -->
- 구현 리뷰 FIX iteration: <N>회 (최대 3)
- 구현 테스트 FIX iteration: <N>회 (무제한)
- 보안 테스트 FIX iteration: <N>회 (무제한)

---

🤖 Generated with [CodeForge plugin](https://github.com/mctrader/codeforge)
```

- [ ] **Step 2: Commit**

```bash
git add templates/github-pr-template.md
git commit -m "feat(templates): PR template 추가 — Phase 1 / Phase 2 양식 분리"
```

---

### Task 10: templates/github-workflows/story-init.yml 작성

**Goal**: Story Issue Form 제출 → 다음 PLG-N 번호 계산 → docs file 생성 PR + Issue body 변환 + 라벨 부착 + Milestone 할당.

**Files:**
- Create: `templates/github-workflows/story-init.yml`

- [ ] **Step 1: 파일 작성**

```yaml
name: Story Init

on:
  issues:
    types: [opened]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  story-init:
    if: contains(github.event.issue.labels.*.name, 'type:story') && contains(github.event.issue.labels.*.name, 'phase:요구사항')
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Compute next story key
        id: key
        run: |
          # consumer overlay에서 story_key_prefix 읽기
          PREFIX=$(yq '.github.story_key_prefix' .claude/_overlay/project.yaml)
          # 기존 docs/stories/<PREFIX>-*.md 중 최대 번호 + 1
          LAST=$(ls docs/stories/${PREFIX}-*.md 2>/dev/null \
                 | sed -E "s|.*/${PREFIX}-([0-9]+)\.md|\1|" \
                 | sort -n | tail -1)
          NEXT=$(( ${LAST:-0} + 1 ))
          echo "key=${PREFIX}-${NEXT}" >> $GITHUB_OUTPUT
          echo "slug=$(echo '${{ github.event.issue.title }}' | sed -E 's/^\[STORY\] //; s/[^A-Za-z0-9가-힣]+/-/g; s/^-+|-+$//g; s/(.{40}).*/\1/')" >> $GITHUB_OUTPUT

      - name: Parse user requirement from Issue body
        id: parse
        run: |
          # Issue Form은 markdown header로 field name이 들어감 ("### 사용자 요구사항 (변조 금지 verbatim)")
          REQ=$(echo "${{ github.event.issue.body }}" \
                | awk '/### 사용자 요구사항/,/### Epic Milestone/' \
                | sed '1d;$d' | sed '/^$/d')
          echo "requirement<<EOF" >> $GITHUB_OUTPUT
          echo "$REQ" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

          MILESTONE=$(echo "${{ github.event.issue.body }}" \
                     | awk '/### Epic Milestone/,/### Component/' \
                     | sed '1d;$d' | sed '/^$/d' | head -1)
          echo "milestone=$MILESTONE" >> $GITHUB_OUTPUT

      - name: Create branch + docs/stories/<KEY>.md
        run: |
          KEY="${{ steps.key.outputs.key }}"
          SLUG="${{ steps.key.outputs.slug }}"
          BRANCH="feat/${KEY}-${SLUG}"

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git checkout -b "$BRANCH"

          # docs/stories/<KEY>.md 생성 (templates/story-page-structure.md 기반)
          mkdir -p docs/stories
          cat > "docs/stories/${KEY}.md" <<EOF
          # ${KEY}: ${{ github.event.issue.title }}

          - **Issue**: #${{ github.event.issue.number }}
          - **Status**: phase:요구사항

          ## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

          ${{ steps.parse.outputs.requirement }}

          ## 2. 도메인 해석

          *(DomainAgent 작성 예정 — placeholder)*

          ## 3. 관련 ADR

          *(RequirementsPL 작성 예정 — placeholder)*

          ## 4. 관련 코드 경로

          *(RequirementsPL 작성 예정 — placeholder)*

          ## 5. 요구사항 확장 해석

          *(RequirementsAnalyst 작성 예정 — placeholder)*

          ## 6. 외부 지식 배경

          *(Researcher 작성 예정 — placeholder)*

          ## 7. 설계 서사

          *(Architect 작성 예정 — placeholder)*

          ## 8. 개발 서사

          *(DeveloperPL 작성 예정 — Phase 2 PR에서)*

          ## 9. 품질 게이트 이력

          *(Review/Test PL 작성 예정 — Phase 2 PR에서)*

          ## 10. FIX Ledger

          | Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
          |------|------|------|--------|-----------|-------------|--------|

          *(FIX 발생 시 append)*

          ## 11. 회고

          *(PMOAgent 작성 예정 — Story 완료 시)*
          EOF

          git add "docs/stories/${KEY}.md"
          git commit -m "[${KEY}] feat: Story init — §1 verbatim, §2-11 placeholder"
          git push origin "$BRANCH"

      - name: Create Phase 1 PR
        run: |
          KEY="${{ steps.key.outputs.key }}"
          SLUG="${{ steps.key.outputs.slug }}"
          BRANCH="feat/${KEY}-${SLUG}"

          gh pr create \
            --base "$(yq '.github.default_branch' .claude/_overlay/project.yaml)" \
            --head "$BRANCH" \
            --title "[${KEY}] ${{ github.event.issue.title }}" \
            --body "Story SSOT: \`docs/stories/${KEY}.md\`%0A%0AThis is the Phase 1 PR (요구사항+설계+설계리뷰 lane). architect team CODEOWNERS auto-review attached.%0A%0ARelated: #${{ github.event.issue.number }}" \
            --label "type:story,phase:요구사항"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Update Issue body to docs link
        run: |
          KEY="${{ steps.key.outputs.key }}"
          gh issue edit ${{ github.event.issue.number }} \
            --body "Story SSOT: [\`docs/stories/${KEY}.md\`](../blob/main/docs/stories/${KEY}.md)"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Assign Milestone (if specified)
        if: steps.parse.outputs.milestone != ''
        run: |
          gh issue edit ${{ github.event.issue.number }} --milestone "${{ steps.parse.outputs.milestone }}"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: yamllint + actionlint**

```bash
yamllint templates/github-workflows/story-init.yml
which actionlint || brew install actionlint
actionlint templates/github-workflows/story-init.yml
```

- [ ] **Step 3: Commit**

```bash
git add templates/github-workflows/story-init.yml
git commit -m "feat(workflows): story-init.yml — Issue Forms → docs file + Phase 1 PR 자동화"
```

---

### Task 11: templates/github-workflows/phase-label-invariant.yml 작성

**Goal**: `phase:*` 라벨이 정확히 1개 active. 다른 phase:* 부착 시 기존 자동 detach.

**Files:**
- Create: `templates/github-workflows/phase-label-invariant.yml`

- [ ] **Step 1: 파일 작성**

```yaml
name: Phase Label Invariant

on:
  issues:
    types: [labeled]
  pull_request:
    types: [labeled]

permissions:
  issues: write
  pull-requests: write

jobs:
  enforce-single-active:
    runs-on: ubuntu-latest
    steps:
      - name: Strip other phase:* labels
        uses: actions/github-script@v7
        with:
          script: |
            const target = context.payload.label.name;
            if (!target.startsWith('phase:')) return;
            const issueNumber = context.payload.issue?.number || context.payload.pull_request?.number;
            if (!issueNumber) return;
            const { data: labels } = await github.rest.issues.listLabelsOnIssue({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issueNumber
            });
            const phaseLabels = labels.filter(l => l.name.startsWith('phase:') && l.name !== target);
            for (const l of phaseLabels) {
              await github.rest.issues.removeLabel({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issueNumber,
                name: l.name
              });
              core.notice(`detached ${l.name} (single-active phase invariant)`);
            }
```

- [ ] **Step 2: yamllint + actionlint + Commit**

```bash
yamllint templates/github-workflows/phase-label-invariant.yml
actionlint templates/github-workflows/phase-label-invariant.yml
git add templates/github-workflows/phase-label-invariant.yml
git commit -m "feat(workflows): phase-label-invariant.yml — phase:* single-active 강제"
```

---

### Task 12: templates/github-workflows/story-section-1-immutable.yml 작성

**Goal**: docs/stories/**/§1 line range가 PR에서 변경되면 자동 reject. story-init.yml의 첫 commit이 §1을 확정한 시점부터 line range protect.

**Files:**
- Create: `templates/github-workflows/story-section-1-immutable.yml`

- [ ] **Step 1: 파일 작성**

```yaml
name: Story §1 Immutable

on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'docs/stories/**'

permissions:
  contents: read
  pull-requests: write

jobs:
  check-section1:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Detect §1 modifications
        id: detect
        run: |
          # PR base ref와 head ref 사이 docs/stories/* 변경 추출
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"
          VIOLATIONS=""
          for f in $(git diff --name-only "$BASE_SHA" "$HEAD_SHA" -- 'docs/stories/*.md'); do
            # §1 = "## 1. 사용자 요구사항" ~ "## 2. 도메인 해석" 사이
            # base에 §1 존재했는가 (즉 story-init 후의 PR인가)
            if ! git show "$BASE_SHA:$f" 2>/dev/null | grep -q '^## 1\. 사용자 요구사항'; then
              # 새 파일 또는 §1 미생성 — story-init.yml 단계라 skip
              continue
            fi
            BASE_S1=$(git show "$BASE_SHA:$f" | awk '/^## 1\./,/^## 2\./')
            HEAD_S1=$(git show "$HEAD_SHA:$f" | awk '/^## 1\./,/^## 2\./')
            if [[ "$BASE_S1" != "$HEAD_S1" ]]; then
              VIOLATIONS="${VIOLATIONS}${f}: §1 변경 감지\n"
            fi
          done
          if [[ -n "$VIOLATIONS" ]]; then
            echo "violations<<EOF" >> $GITHUB_OUTPUT
            echo -e "$VIOLATIONS" >> $GITHUB_OUTPUT
            echo "EOF" >> $GITHUB_OUTPUT
            exit 1
          fi

      - name: Comment on PR (failure)
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.payload.pull_request.number,
              body: `❌ **Story §1 Immutable Violation**\n\nThe following files have §1 (사용자 요구사항 verbatim) modifications, which is not allowed:\n\n\`\`\`\n${{ steps.detect.outputs.violations }}\n\`\`\`\n\nIf §1 needs legitimate correction (typo etc.), open a separate PR with explicit bypass approval from architect team.`
            });
```

- [ ] **Step 2: yamllint + actionlint + Commit**

```bash
yamllint templates/github-workflows/story-section-1-immutable.yml
actionlint templates/github-workflows/story-section-1-immutable.yml
git add templates/github-workflows/story-section-1-immutable.yml
git commit -m "feat(workflows): story-section-1-immutable.yml — §1 line range 변경 차단"
```

---

### Task 13: 나머지 3 워크플로우 작성 (subissue / phase-gate / fix-ledger-sync)

**Goal**: B 그룹 자동화 3건. spec §5.2 책임 표 그대로.

**Files:**
- Create: `templates/github-workflows/subissue-from-impl-manifest.yml`
- Create: `templates/github-workflows/phase-gate-mergeable.yml`
- Create: `templates/github-workflows/fix-ledger-sync.yml`

- [ ] **Step 1: subissue-from-impl-manifest.yml**

```yaml
name: Sub-issue from Impl Manifest

on:
  pull_request:
    types: [synchronize, opened]
    paths:
      - 'docs/stories/**'

permissions:
  contents: read
  issues: write

jobs:
  generate-subissues:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Parse §8.5 Impl Manifest table
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const path = require('path');
            const { execSync } = require('child_process');

            const baseSha = context.payload.pull_request.base.sha;
            const headSha = context.payload.pull_request.head.sha;

            // PR이 변경한 docs/stories/*.md 중 §8.5 매핑표 행 추출
            const files = execSync(`git diff --name-only ${baseSha} ${headSha} -- 'docs/stories/*.md'`)
                          .toString().trim().split('\n').filter(Boolean);

            for (const f of files) {
              const content = fs.readFileSync(f, 'utf8');
              // §8.5 ~ §9 사이의 마크다운 테이블 행 추출
              const m = content.match(/##\s*8\.5[\s\S]*?(?=##\s*9\.|\Z)/);
              if (!m) continue;
              const table = m[0];
              // 테이블 행: `| <path> | <description> | ... |`
              const rows = table.split('\n').filter(line =>
                line.match(/^\|\s*[a-zA-Z0-9_/.\-]+\s*\|/) && !line.match(/-{3,}/)
              );

              const storyKey = path.basename(f, '.md');

              for (const row of rows) {
                const cells = row.split('|').map(c => c.trim()).filter(Boolean);
                const filePath = cells[0];
                const description = cells[1] || '';

                // 이미 sub-issue 존재 확인 (제목 매칭)
                const expectedTitle = `[${storyKey}] impl: ${filePath}`;
                const { data: existing } = await github.rest.search.issuesAndPullRequests({
                  q: `repo:${context.repo.owner}/${context.repo.repo} is:issue label:impl-manifest in:title "${filePath}"`
                });
                if (existing.total_count > 0) continue;

                // sub-issue 생성
                const { data: subIssue } = await github.rest.issues.create({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  title: expectedTitle,
                  body: `Parent Story: ${storyKey}\nFile: \`${filePath}\`\nResponsibility: ${description}\n\n_Auto-generated by subissue-from-impl-manifest.yml_`,
                  labels: ['impl-manifest']
                });

                // parent Issue (Story) 찾아 sub-issue 관계 연결 (gh sub-issue API)
                const parentIssueQuery = await github.rest.search.issuesAndPullRequests({
                  q: `repo:${context.repo.owner}/${context.repo.repo} is:issue label:type:story in:title "${storyKey}"`
                });
                if (parentIssueQuery.data.total_count > 0) {
                  const parentNumber = parentIssueQuery.data.items[0].number;
                  // sub-issue 연결: GraphQL mutation
                  await github.graphql(`
                    mutation AddSubIssue($parentId: ID!, $childId: ID!) {
                      addSubIssue(input: {issueId: $parentId, subIssueId: $childId}) {
                        subIssue { id }
                      }
                    }
                  `, {
                    parentId: parentIssueQuery.data.items[0].node_id,
                    childId: subIssue.node_id
                  }).catch(e => core.warning(`addSubIssue failed: ${e.message}`));
                }

                core.notice(`Created sub-issue #${subIssue.number} for ${filePath}`);
              }
            }
```

- [ ] **Step 2: phase-gate-mergeable.yml**

```yaml
name: Phase Gate Mergeable

on:
  pull_request:
    types: [opened, synchronize, labeled, unlabeled]

permissions:
  pull-requests: write
  checks: write

jobs:
  check-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Determine PR phase + gate
        id: gate
        uses: actions/github-script@v7
        with:
          script: |
            const labels = context.payload.pull_request.labels.map(l => l.name);
            const phaseLabel = labels.find(l => l.startsWith('phase:'));
            const gateLabel = labels.find(l => l.startsWith('gate:'));

            // Phase 1 PR: docs only changes
            // Phase 2 PR: src/** changes 포함
            const { data: files } = await github.rest.pulls.listFiles({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number
            });
            const hasCode = files.some(f => f.filename.startsWith('src/') || f.filename.startsWith('tests/'));

            let required;
            if (hasCode) {
              required = { phase: 'phase:보안-테스트', gate: 'gate:security-test-pass' };
            } else {
              required = { phase: 'phase:설계-리뷰', gate: 'gate:design-review-pass' };
            }

            const phaseOk = phaseLabel === required.phase;
            const gateOk = gateLabel === required.gate;
            const status = (phaseOk && gateOk) ? 'success' : 'pending';
            const summary = (phaseOk && gateOk)
              ? `✓ phase + gate satisfied: ${required.phase} + ${required.gate}`
              : `⏳ Awaiting: phase=${required.phase} (current=${phaseLabel || 'none'}), gate=${required.gate} (current=${gateLabel || 'none'})`;

            // Status check 등록
            await github.rest.checks.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              name: 'phase-gate-mergeable',
              head_sha: context.payload.pull_request.head.sha,
              status: 'completed',
              conclusion: (status === 'success') ? 'success' : 'action_required',
              output: { title: 'Phase Gate', summary: summary }
            });
```

- [ ] **Step 3: fix-ledger-sync.yml**

```yaml
name: Fix Ledger Sync

on:
  push:
    branches: [main]
    paths:
      - 'docs/stories/**'

permissions:
  contents: read
  issues: write

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Detect new §10 rows
        id: detect
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const path = require('path');
            const { execSync } = require('child_process');

            // 직전 commit과 현재 commit의 diff에서 docs/stories/*.md §10 추가 행 추출
            const changed = execSync(`git diff --name-only HEAD^ HEAD -- 'docs/stories/*.md'`)
                            .toString().trim().split('\n').filter(Boolean);

            const events = [];
            for (const f of changed) {
              const diff = execSync(`git diff HEAD^ HEAD -- ${f}`).toString();
              // §10 ~ §11 사이의 추가 행 (+로 시작)
              const inSection = /^@@.*##\s*10\./;
              const lines = diff.split('\n');
              let inS10 = false;
              for (const line of lines) {
                if (line.match(/^\+##\s*10\./)) inS10 = true;
                else if (line.match(/^\+##\s*11\./)) inS10 = false;
                else if (inS10 && line.startsWith('+|') && !line.match(/^\+\|\s*Iter/) && !line.match(/^\+\|-{3,}/)) {
                  // FIX Ledger 새 행
                  const cells = line.substring(1).split('|').map(c => c.trim()).filter(Boolean);
                  if (cells.length >= 6) {
                    events.push({
                      file: f,
                      key: path.basename(f, '.md'),
                      iter: cells[0],
                      lane: cells[2],
                      cause: cells[4],
                      reset: cells[6] || ''
                    });
                  }
                }
              }
            }
            core.setOutput('events', JSON.stringify(events));

      - name: Mirror to Issue + attach fix label
        if: steps.detect.outputs.events != '[]' && steps.detect.outputs.events != ''
        uses: actions/github-script@v7
        with:
          script: |
            const events = JSON.parse('${{ steps.detect.outputs.events }}');
            for (const e of events) {
              // Story Issue 찾기
              const { data: issues } = await github.rest.search.issuesAndPullRequests({
                q: `repo:${context.repo.owner}/${context.repo.repo} is:issue label:type:story in:title "${e.key}"`
              });
              if (issues.total_count === 0) continue;
              const issueNumber = issues.items[0].number;

              // Issue comment mirror
              const resetNote = e.reset ? `\n**RESET marker**: ${e.reset}` : '';
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issueNumber,
                body: `[FIX #${e.iter}] **${e.lane}** — 원인: ${e.cause}${resetNote}\n\nSource: \`${e.file}\` §10`
              });

              // fix:* 라벨 부착 (lane → label 매핑)
              const laneToLabel = {
                '설계-리뷰': 'fix:설계-리뷰-retry',
                '구현-리뷰': 'fix:구현-리뷰-retry',
                '구현-테스트': 'fix:구현-테스트-retry',
                '보안-테스트': 'fix:보안-테스트-retry'
              };
              const label = laneToLabel[e.lane];
              if (label) {
                await github.rest.issues.addLabels({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: issueNumber,
                  labels: [label]
                });
              }
            }
```

- [ ] **Step 4: 모두 lint + Commit**

```bash
yamllint templates/github-workflows/subissue-from-impl-manifest.yml \
         templates/github-workflows/phase-gate-mergeable.yml \
         templates/github-workflows/fix-ledger-sync.yml
actionlint templates/github-workflows/*.yml
git add templates/github-workflows/subissue-from-impl-manifest.yml \
        templates/github-workflows/phase-gate-mergeable.yml \
        templates/github-workflows/fix-ledger-sync.yml
git commit -m "feat(workflows): B 그룹 자동화 3종 — subissue 자동 생성 / phase-gate / fix-ledger sync"
```

---

## Phase C: Core Docs Rewrite

### Task 14: CLAUDE.md major rewrite

**Goal**: spec §6, §7, §2 내용을 CLAUDE.md에 반영. 다음 섹션 모두 atlassian 의존 제거 + GitHub-native 표현으로 교체.

**Files:**
- Modify: `CLAUDE.md`

**대상 섹션** (현재 CLAUDE.md 구조 기준):
1. 프로젝트 소개 부분의 "atlassian MCP 사용" 제거
2. "Plugin" 섹션의 overlay 메커니즘 — atlassian.* 언급 → github.*로
3. "세션 개시 의무" 섹션 — MCP atlassian → github, 권장 플러그인 atlassian 제거 + github 격상, gh CLI 추가
4. "Confluence Story 페이지 SSOT" 표현 → "docs/stories/<KEY>.md SSOT"
5. "Jira 워크플로우" 섹션 → "GitHub Workflow" 섹션으로 전면 재작성
6. "ADR (Confluence Pages SSOT)" → "ADR (`docs/adr/` SSOT)"
7. "Domain Knowledge" 섹션 → "`docs/domain-knowledge/` 트리"

- [ ] **Step 1: 현재 CLAUDE.md 섹션 인벤토리**

```bash
grep -n '^## \|^### ' CLAUDE.md
```

- [ ] **Step 2: 섹션별로 Edit 도구 사용해 atlassian → github 교체**

권장 작업 순서 (한 commit per section group):
1. **세션 개시 의무 섹션 갱신**: spec §6.1 그대로. MCP 1종 변경, 필수 플러그인 4종, 필수 CLI 2종
2. **컨텍스트 전달 섹션**: "Confluence Story 페이지 SSOT" → "docs/stories/<KEY>.md SSOT". `mcp__atlassian__getConfluencePage(pageId=N)` → `Read(docs/stories/<KEY>.md)`
3. **Jira 워크플로우 섹션 전면 재작성**: spec §3 lifecycle 반영. Phase label·fix label 표현 유지, transition 메커니즘은 GitHub native (PR merge, label invariant Action)
4. **ADR 섹션 재작성**: Confluence search → `Glob(docs/adr/ADR-*.md)`. 카테고리는 frontmatter
5. **Domain Knowledge 섹션 갱신**: Confluence 트리 → `docs/domain-knowledge/<area>/<topic>.md`. DomainAgent fetch 경로 변경
6. **Bug 기록 섹션**: `mcp__atlassian__createJiraIssue` → `mcp__github__issue_write`
7. **Confluence Story 페이지 규약 요약** 섹션 → "docs/stories markdown 규약"으로 재작성

- [ ] **Step 3: 잔재 검증**

```bash
grep -E 'atlassian|Confluence|Jira|mcp__atlassian' CLAUDE.md && echo "ERR" || echo "OK"
grep -cE 'github|GitHub|mcp__github__|docs/stories' CLAUDE.md
# 결과: >= 20개 (충분히 GitHub-native로 전환됨)
```

- [ ] **Step 4: link checker**

```bash
./scripts/check-doc-links.sh
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE.md): atlassian 의존 제거, GitHub-native 워크플로우로 전면 재작성"
```

---

### Task 15: docs/orchestrator-playbook.md major rewrite

**Goal**: spec §3, §4, §6 내용 반영. 현재 928줄 playbook의 다음 섹션 갱신.

**Files:**
- Modify: `docs/orchestrator-playbook.md`

**대상 섹션**:
- §1.1 dependency check: atlassian → github
- §3B preflight 체크: Story 페이지 → docs/stories file
- §11 write queue drain: DocsAgent의 atlassian 호출 → GitHub MCP 호출
- §12 Context Packet: Confluence section fetch → docs file Read
- §12.5 Project Config Packet: atlassian.* slice → github.* slice

- [ ] **Step 1: 섹션 인벤토리 + atlassian 위치**

```bash
grep -n '^## \|^### ' docs/orchestrator-playbook.md
grep -nE 'atlassian|Confluence|Jira|mcp__atlassian' docs/orchestrator-playbook.md | head -50
```

- [ ] **Step 2: 섹션별 Edit (각 1 commit 또는 묶음 1 commit)**

핵심 invariant (변경 시 유지해야 함):
- 7 lane 흐름은 그대로 (요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 구현테스트 → 보안테스트)
- DocsAgent 단독 doc writer 원칙 유지
- write queue 메커니즘 유지 (`.claude-work/doc-queue/<story>/`)
- FIX 카운터 SSOT는 §10 FIX Ledger 유지 (단 위치는 docs file로)
- preflight 3개 체크 유지 (phase 라벨 정합 / docs file 선행 섹션 / 외부 의존성 가용)

변경:
- "Story 페이지" → "docs/stories/<KEY>.md"
- `getConfluencePage(pageId=Story)` → `Read(docs/stories/<KEY>.md)`
- `searchConfluenceUsingCql(cql="label='adr'")` → `Glob(docs/adr/ADR-*.md)`
- `searchJiraIssuesUsingJql(...)` → `gh issue list --label ...` 또는 `mcp__github__list_issues`
- Story 페이지 동기화 체크리스트 → docs file 갱신 체크리스트
- Jira 라벨 부착·전이 절차 → GitHub label 부착 + Action 자동화 의존

- [ ] **Step 3: 잔재 검증**

```bash
grep -E 'atlassian|Confluence|Jira|mcp__atlassian' docs/orchestrator-playbook.md && echo "ERR" || echo "OK"
```

- [ ] **Step 4: link checker + Commit**

```bash
./scripts/check-doc-links.sh
git add docs/orchestrator-playbook.md
git commit -m "docs(playbook): atlassian 의존 제거, docs/stories + GitHub MCP로 전환"
```

---

### Task 16: agents/DocsAgent.md major rewrite

**Goal**: spec §4.2 그대로. 권한 재정의 + Confluence/Jira 호출 매핑 표 + FIX Ledger 갱신 절차 + Issue comment phase prefix 10종.

**Files:**
- Modify: `agents/DocsAgent.md`

- [ ] **Step 1: frontmatter `permissions` 블록 교체**

spec §4.2 allow/deny 그대로 적용:

```yaml
---
name: DocsAgent
description: ...
permissions:
  allow:
    - Edit(docs/**)
    - Write(docs/**)
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
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
    - mcp__github__create_pull_request
    - mcp__github__update_pull_request
    - mcp__github__get_label
    - mcp__github__create_branch
    - Bash(gh api repos/*/milestones*)
    - Bash(gh api repos/*/discussions*)
    - Bash(gh api graphql*)
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
---
```

- [ ] **Step 2: 본문 섹션 재작성**

대상 섹션 (현재 DocsAgent.md 구조):
1. **책무**: "Confluence·Jira 단독 writer" → "docs/** 단독 writer + GitHub Issue/PR/comment write"
2. **Story 페이지 섹션 규격**: 위치 표현 변경 (Confluence → docs file). §1-11 본문 규격은 spec §3.3 형식 유지
3. **FIX Ledger 갱신 절차**: §10 테이블 형식은 그대로, 갱신 메커니즘은 docs file commit + Action(fix-ledger-sync.yml)이 mirror·label
4. **Jira 코멘트 prefix 10종**: 그대로 유지하되 위치는 GitHub Issue comment
5. **Bug 생성 절차**: `createJiraIssue(...)` → `mcp__github__issue_write(action='create', labels=['type:bug'])`
6. **ADR 생성 절차**: `createConfluencePage(...)` → `Write(docs/adr/ADR-NNN-<slug>.md)` + `mcp__github__create_or_update_file` (PR 통한 commit)
7. **Domain Knowledge 갱신**: Confluence 페이지 → `docs/domain-knowledge/<area>/<topic>.md` + Discussions Q&A 카테고리 update
8. **Phase 라벨 부착 메커니즘**: `editJiraIssue(labels=...)` → `mcp__github__issue_write` (label 추가 — phase-label-invariant.yml가 detach)
9. **Sub-task 생성**: `createJiraIssue(issueTypeName='하위작업')` → 자동 (subissue-from-impl-manifest.yml가 single source)
10. **Phase 2 PR 생성**: `mcp__github__create_pull_request` (DeveloperPL 의뢰 시)

- [ ] **Step 3: 검증**

```bash
grep -E 'atlassian|Confluence|Jira|mcp__atlassian' agents/DocsAgent.md && echo "ERR" || echo "OK"
./scripts/check-agent-frontmatter.sh
```

- [ ] **Step 4: Commit**

```bash
git add agents/DocsAgent.md
git commit -m "agent(DocsAgent): 권한 재정의 + GitHub primitive 매핑으로 전면 재작성"
```

---

## Phase D: Other 23 Agents

23개 agent를 5개 그룹으로 묶어 commit. 각 agent의 변경은 거의 mechanical:
1. frontmatter `permissions` 블록의 `mcp__atlassian__*` 제거 + 필요 시 `mcp__github__*` read 도구 추가 (read-only)
2. 본문에서 "Confluence Story 페이지" → "docs/stories/<KEY>.md", "Jira" → "GitHub Issue", "ADR Confluence 페이지" → "docs/adr/ADR-NNN-<slug>.md" 등
3. 호출 패턴: `getConfluencePage(pageId=N)` → `Read(docs/stories/<KEY>.md)`, `searchConfluenceUsingCql` → `Glob(docs/adr/ADR-*.md)` 등

### Task 17: Cross-cutting (PMOAgent) + 요구사항 lane (4 agents)

**Files:**
- Modify: `agents/PMOAgent.md`
- Modify: `agents/RequirementsPLAgent.md`
- Modify: `agents/DomainAgent.md`
- Modify: `agents/RequirementsAnalystAgent.md`
- Modify: `agents/ResearcherAgent.md`

- [ ] **Step 1: 각 agent의 atlassian 잔재 위치 인벤토리**

```bash
for f in agents/PMOAgent.md agents/RequirementsPLAgent.md agents/DomainAgent.md agents/RequirementsAnalystAgent.md agents/ResearcherAgent.md; do
  echo "=== $f ==="
  grep -nE 'atlassian|Confluence|Jira|mcp__atlassian' "$f" | head -10
done
```

- [ ] **Step 2: 각 파일 변환** (Edit 도구로 mechanical 치환)

공통 치환 매핑:
- `mcp__atlassian__getConfluencePage` → `mcp__github__get_file_contents` (frontmatter) / `Read(docs/...)` (본문)
- `mcp__atlassian__searchConfluenceUsingCql` → `Glob` + `Grep`
- `mcp__atlassian__getPagesInConfluenceSpace` → `Glob(docs/...)`
- `mcp__atlassian__getJiraIssue` → `mcp__github__issue_read`
- `mcp__atlassian__searchJiraIssuesUsingJql` → `mcp__github__list_issues` + `mcp__github__search_issues`
- "Confluence Story 페이지" → "docs/stories/<KEY>.md"
- "Jira" → "GitHub Issue" (대부분의 문맥)
- "ADR Confluence 페이지" → "`docs/adr/ADR-NNN-<slug>.md`"
- "Domain Knowledge Confluence 트리" → "`docs/domain-knowledge/`"

agent별 특이점:
- **DomainAgent**: Domain Knowledge 4소스 표현 — "Confluence Domain Knowledge + ADR + 도메인 코드 + 사용자 원문" → "`docs/domain-knowledge/` + `docs/adr/` + 도메인 코드 + 사용자 원문 §1"
- **RequirementsPL**: 통합 명세서 §3-6 갱신 → DocsAgent 의뢰 (write queue)
- **Researcher**: 외부 지식 fetch는 그대로 WebFetch/WebSearch
- **PMOAgent**: Cross-Story 패턴 분석 시 Issue 검색 — JQL → GraphQL search syntax. 예시 query 갱신

- [ ] **Step 3: 검증**

```bash
for f in agents/PMOAgent.md agents/RequirementsPLAgent.md agents/DomainAgent.md agents/RequirementsAnalystAgent.md agents/ResearcherAgent.md; do
  if grep -qE 'atlassian|Confluence|Jira|mcp__atlassian' "$f"; then
    echo "ERR: $f 잔재"
  else
    echo "OK: $f"
  fi
done
./scripts/check-agent-frontmatter.sh
```

- [ ] **Step 4: Commit**

```bash
git add agents/PMOAgent.md agents/RequirementsPLAgent.md agents/DomainAgent.md agents/RequirementsAnalystAgent.md agents/ResearcherAgent.md
git commit -m "agents: PMO + 요구사항 lane (5개) atlassian 의존 제거, GitHub-native로 전환"
```

---

### Task 18: 설계 lane (3 agents)

**Files:**
- Modify: `agents/ArchitectAgent.md`
- Modify: `agents/CodebaseMapperAgent.md`
- Modify: `agents/RefactorAgent.md`

- [ ] **Step 1: 위치 인벤토리 + 변환**

Task 17과 동일 패턴. 특이점:
- **ArchitectAgent**: Change Plan 저장 → DocsAgent 의뢰 (`docs/change-plans/<slug>.md`). ADR 생성·갱신도 DocsAgent 의뢰 (`docs/adr/ADR-NNN-<slug>.md`)
- **CodebaseMapper**: 원 소스 read는 `Read`, `Glob`, `Grep`. ADR 정합성 fetch: `Glob(docs/adr/ADR-*.md)` + frontmatter category로 필터
- **Refactor**: 동일

- [ ] **Step 2: 검증 + Commit**

```bash
./scripts/check-agent-frontmatter.sh
git add agents/ArchitectAgent.md agents/CodebaseMapperAgent.md agents/RefactorAgent.md
git commit -m "agents: 설계 lane (3개) atlassian 의존 제거"
```

---

### Task 19: 설계 리뷰 lane (3 agents)

**Files:**
- Modify: `agents/DesignReviewPLAgent.md`
- Modify: `agents/ClaudeDesignReviewAgent.md`
- Modify: `agents/CodexDesignReviewAgent.md`

- [ ] **Step 1: 변환** (대부분 read-only — atlassian read 잔여 제거)

특이점:
- **DesignReviewPL**: ADR 정합성 체크 메커니즘 — Confluence ADR fetch → `Glob(docs/adr/ADR-*.md)` + `Read`. Severity 종합·dedup 절차는 그대로
- **ClaudeDesignReview**: 동일
- **CodexDesignReview**: Codex 호출은 `Bash(node ...)` 그대로. atlassian 호출 0건이지만 본문 표현 정정

- [ ] **Step 2: 검증 + Commit**

```bash
./scripts/check-agent-frontmatter.sh
git add agents/DesignReviewPLAgent.md agents/ClaudeDesignReviewAgent.md agents/CodexDesignReviewAgent.md
git commit -m "agents: 설계 리뷰 lane (3개) atlassian 잔여 제거"
```

---

### Task 20: 코드 리뷰 + 보안 테스트 + 구현 테스트 lane (7 agents)

**Files:**
- Modify: `agents/CodeReviewPLAgent.md`
- Modify: `agents/ClaudeCodeReviewAgent.md`
- Modify: `agents/CodexCodeReviewAgent.md`
- Modify: `agents/SecurityTestPLAgent.md`
- Modify: `agents/ClaudeSecurityTestAgent.md`
- Modify: `agents/CodexSecurityTestAgent.md`
- Modify: `agents/TestAgent.md`

- [ ] **Step 1: 변환**

특이점:
- **SecurityTestPL**: spec §5.2 Dependabot/CodeQL/Secret Scanning이 1차 layer임을 명시. Claude/Codex 보안 에이전트는 high-level (trust boundary, auth model) 검증
- **ClaudeSecurityTest, CodexSecurityTest**: 1차 layer 결과 활용 절차 추가
- **TestAgent**: Story §9.3 갱신 의뢰 — DocsAgent 경유. atlassian 호출 0건 (이미 거의 없음)

- [ ] **Step 2: 검증 + Commit**

```bash
./scripts/check-agent-frontmatter.sh
git add agents/CodeReviewPLAgent.md agents/ClaudeCodeReviewAgent.md agents/CodexCodeReviewAgent.md \
        agents/SecurityTestPLAgent.md agents/ClaudeSecurityTestAgent.md agents/CodexSecurityTestAgent.md \
        agents/TestAgent.md
git commit -m "agents: 코드 리뷰 + 보안 + 테스트 lane (7개) atlassian 잔여 제거 + Dependabot/CodeQL 1차 layer 명시"
```

---

### Task 21: 구현 lane (5 agents)

**Files:**
- Modify: `agents/DeveloperPLAgent.md`
- Modify: `agents/QADeveloperAgent.md`
- Modify: `agents/DeveloperAgent.md`
- Modify: `agents/DataEngineerAgent.md`
- Modify: `agents/InfraEngineerAgent.md`

- [ ] **Step 1: 변환**

특이점:
- **DeveloperPL**: Phase 2 PR 생성 의뢰 — DocsAgent 경유 `mcp__github__create_pull_request`. Impl Manifest 작성 → `docs/stories/<KEY>.md` §8.5 매핑표 → subissue-from-impl-manifest.yml가 자동 sub-issue
- **QADev**: §8 Test Contract 이행. 테스트 파일 매핑 → §8.5에 추가
- **DeveloperAgent, DataEngineerAgent, InfraEngineerAgent**: read-only로 atlassian 호출 거의 없음. 본문 표현 정정만

- [ ] **Step 2: 검증 + Commit**

```bash
./scripts/check-agent-frontmatter.sh
./scripts/check-no-atlassian.sh
# 이 시점에서 모든 agent에서 atlassian 잔재 0이어야 함
git add agents/DeveloperPLAgent.md agents/QADeveloperAgent.md agents/DeveloperAgent.md agents/DataEngineerAgent.md agents/InfraEngineerAgent.md
git commit -m "agents: 구현 lane (5개) atlassian 잔여 제거 + Phase 2 PR 생성 흐름 명시"
```

---

### Task 22: 전체 agent 재검증

**Goal**: 24 agent 모두 atlassian 잔재 0건 확인.

- [ ] **Step 1: 전체 grep**

```bash
./scripts/check-agent-frontmatter.sh && echo "✓ frontmatter 통과"
grep -rEn 'atlassian|Confluence|Jira|mcp__atlassian' agents/ && echo "ERR: 본문에 잔재" || echo "✓ 본문 통과"
```

Expected: 둘 다 PASS.

- [ ] **Step 2: 잔재 발견 시 inline 수정**

만약 PASS 하지 않으면 발견 위치 수정 후 재검증.

- [ ] **Step 3: Commit (필요 시)**

```bash
# 변경 있을 시만
git add agents/
git commit -m "agents: 잔재 정리"
```

---

## Phase E: Templates · Consumer Guide · Migration Guide · README

### Task 23: templates/story-page-structure.md 갱신

**Files:**
- Modify: `templates/story-page-structure.md`

- [ ] **Step 1: 헤더 + 도입부 재작성**

현재 "Confluence Story 페이지 섹션 규격"을 "`docs/stories/<KEY>.md` 섹션 규격"으로:

```markdown
# Story Page Structure

`docs/stories/<KEY>.md` 단일 파일 SSOT의 섹션 규격. 11개 섹션이 모두 한 파일에 존재한다.

## 위치 + 갱신 권한

- 위치: `docs/stories/<KEY>.md` (KEY = `<github.story_key_prefix>-N`, 예: `PLG-7`)
- 갱신 권한: **DocsAgent 단독** (`Edit(docs/**)`, `Write(docs/**)`)
- 다른 에이전트는 write queue (`.claude-work/doc-queue/<KEY>/`)에 의뢰 파일 append → DocsAgent drain
- §1 변조 금지 invariant: `story-section-1-immutable.yml` Action이 강제

## 섹션 규격
...
```

§1-§11 각 섹션의 본문 규격은 기존과 동일 유지 (작성 책임자, 입력 소스, 형식 등).

- [ ] **Step 2: 검증 + Commit**

```bash
grep -E 'atlassian|Confluence|Jira' templates/story-page-structure.md && echo "ERR" || echo "OK"
git add templates/story-page-structure.md
git commit -m "templates(story-page-structure): docs/stories markdown SSOT로 헤더 재작성"
```

---

### Task 24: templates/adr.md + templates/impl-manifest.md 갱신

**Files:**
- Modify: `templates/adr.md`
- Modify: `templates/impl-manifest.md`

- [ ] **Step 1: templates/adr.md frontmatter `category:` 추가**

현재 ADR template 상단에 frontmatter 추가:

```markdown
---
adr_number: NNN
title: <결정 제목>
status: Proposed | Accepted | Deprecated | Superseded
category: Team & Process | Architecture | Data & Storage | Infrastructure | UX
date: YYYY-MM-DD
related_files: []
---

# ADR-NNN: <결정>

## 상태
...

## 컨텍스트
...

## 결정
...

## 결과
...

## 다이어그램 (Mermaid)
...

## 관련 파일
...
```

`category:` 값 enum 명시. status enum 명시.

- [ ] **Step 2: templates/impl-manifest.md sub-issue 형식**

현재 Impl Manifest는 Jira sub-task 양식. 이를 GitHub sub-issue 양식으로:

```markdown
# Impl Manifest

`docs/stories/<KEY>.md` §8.5 매핑표 형식. `subissue-from-impl-manifest.yml` Action이 매핑표 행마다 sub-issue 자동 생성.

## §8.5 매핑표 형식

| 파일 경로 | 책임 | 의존 | 테스트 위치 |
|----------|------|------|-----------|
| `src/payment/idempotency.py` | idempotency key 검증·저장 | Redis client | `tests/payment/test_idempotency.py` |
| `tests/payment/test_idempotency.py` | idempotency 단위 테스트 | — | (self) |

각 행은 sub-issue 1건에 대응. Action이 자동 생성하므로 DocsAgent는 매핑표만 작성, sub-issue write 직접 호출 불필요.

## Sub-issue 형식 (자동 생성)

- 제목: `[<KEY>] impl: <파일경로>`
- 라벨: `impl-manifest`
- 본문:
  ```
  Parent Story: <KEY>
  File: `<파일경로>`
  Responsibility: <책임 설명>

  _Auto-generated by subissue-from-impl-manifest.yml_
  ```
- Parent Story Issue 사이의 sub-issue 관계: GraphQL `addSubIssue` mutation으로 자동 연결
```

- [ ] **Step 3: 검증 + Commit**

```bash
grep -E 'atlassian|Confluence|Jira' templates/adr.md templates/impl-manifest.md && echo "ERR" || echo "OK"
git add templates/adr.md templates/impl-manifest.md
git commit -m "templates: ADR frontmatter category 추가, Impl Manifest sub-issue 형식 변경"
```

---

### Task 25: docs/consumer-guide.md major rewrite

**Goal**: GitHub repo 셋업 절차 + 워크플로우 cp + CODEOWNERS·Issue Forms·Branch protection 안내.

**Files:**
- Modify: `docs/consumer-guide.md`

- [ ] **Step 1: 새 구조 설계**

```markdown
# CodeForge Consumer Guide

## 0. 사전 요구사항

- GitHub Team plan (Sub-issues, Projects v2, CODEOWNERS, Branch protection 사용)
- gh CLI 설치 + 인증 (`gh auth login`)
- `github@claude-plugins-official` plugin 설치

## 1. 신규 프로젝트 셋업

### 1.1 plugin 설치

```bash
/plugins install codeforge@<marketplace>
/plugins install github@claude-plugins-official
/plugins install codex@openai-codex
/plugins install superpowers@claude-plugins-official
/plugins install claude-md-management@claude-plugins-official
```

### 1.2 overlay 작성

`.claude/_overlay/project.yaml` 작성:

```yaml
github:
  org: myorg
  repo: myproject
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: PLG
  codeowners:
    architect_team: "@myorg/architects"
    domain_expert_team: "@myorg/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"

labels:
  components:
    - backend
    - frontend
    - infra
```

### 1.3 GitHub repo 셋업

```bash
# CODEOWNERS 복사 + team placeholder 치환
cp <plugin-templates>/CODEOWNERS.template .github/CODEOWNERS
sed -i 's|@ORG/ARCHITECT_TEAM|@myorg/architects|g; s|@ORG/DOMAIN_EXPERT_TEAM|@myorg/domain-experts|g' .github/CODEOWNERS

# Issue Forms 복사
mkdir -p .github/ISSUE_TEMPLATE
cp <plugin-templates>/github-issue-forms/*.yml .github/ISSUE_TEMPLATE/

# blank issue 비활성화
cat > .github/ISSUE_TEMPLATE/config.yml <<EOF
blank_issues_enabled: false
EOF

# PR template 복사
cp <plugin-templates>/github-pr-template.md .github/PULL_REQUEST_TEMPLATE.md

# Workflow 6개 복사
mkdir -p .github/workflows
cp <plugin-templates>/github-workflows/*.yml .github/workflows/

# 라벨 생성 (gh CLI)
gh label create "type:story" --color "0E8A16"
gh label create "type:epic" --color "3E4B9E"
gh label create "type:bug" --color "D73A4A"
gh label create "audit:post-hotfix" --color "FBCA04"
gh label create "impl-manifest" --color "C2E0C6"
gh label create "phase:요구사항" --color "FEF2C0"
gh label create "phase:설계" --color "FEF2C0"
gh label create "phase:설계-리뷰" --color "FEF2C0"
gh label create "phase:구현" --color "FEF2C0"
gh label create "phase:구현-리뷰" --color "FEF2C0"
gh label create "phase:구현-테스트" --color "FEF2C0"
gh label create "phase:보안-테스트" --color "FEF2C0"
gh label create "fix:설계-리뷰-retry" --color "F9D0C4"
gh label create "fix:구현-리뷰-retry" --color "F9D0C4"
gh label create "fix:구현-테스트-retry" --color "F9D0C4"
gh label create "fix:보안-테스트-retry" --color "F9D0C4"
gh label create "gate:design-review-pass" --color "C2E0C6"
gh label create "gate:security-test-pass" --color "C2E0C6"

# Branch protection (main)
gh api -X PUT repos/myorg/myproject/branches/main/protection \
  -F required_status_checks='{"strict":true,"contexts":["phase-gate-mergeable"]}' \
  -F required_pull_request_reviews='{"required_approving_review_count":1,"require_code_owner_reviews":true}' \
  -F enforce_admins=false \
  -F required_linear_history=false

# Dependabot, CodeQL, Secret Scanning 활성화 (UI 또는 gh api)
```

### 1.4 commit + 첫 Story

```bash
git add .github/
git commit -m "chore: CodeForge plugin 워크플로우 + Issue Forms + CODEOWNERS 셋업"
git push

# 첫 Story 생성
gh issue create --template story.yml
```

## 2. 일상 운용

### 2.1 Story 흐름 (Phase 1 + Phase 2)

(spec §3.1 그대로 요약)

### 2.2 FIX 루프 발생 시

(spec §3 / FIX Ledger 설명)

### 2.3 PMOAgent 회고 + Cross-Story 패턴

(PMOAgent 설명)

## 3. 트러블슈팅

- Workflow drift: SessionStart hook이 알림. plugin templates 갱신 시 `cp` 다시
- gh CLI 인증 만료: `gh auth login`
- GitHub MCP 인증 만료: `/mcp`
- ...
```

- [ ] **Step 2: 검증 + Commit**

```bash
grep -E 'atlassian|Confluence|Jira' docs/consumer-guide.md && echo "ERR" || echo "OK"
./scripts/check-doc-links.sh
git add docs/consumer-guide.md
git commit -m "docs(consumer-guide): GitHub-native 셋업 절차로 전면 재작성"
```

---

### Task 26: docs/migration-guide.md append + README + CHANGELOG

**Files:**
- Modify: `docs/migration-guide.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: docs/migration-guide.md에 v0.7 → v0.8 섹션 추가 (기존 섹션 유지)**

목차 상단에 추가:
```markdown
- [v0.7 → v0.8](#v07--v08-atlassian-제거--github-전환) — Atlassian 제거 + GitHub 전환 (BREAKING)
```

새 섹션 추가:
```markdown
## v0.7 → v0.8 (Atlassian 제거 + GitHub 전환)

### Breaking changes

이 release는 Atlassian backend를 완전 제거한다. 기존 v0.7 이하 consumer는 in-place 업그레이드 불가 — fresh GitHub-based setup 필요.

- **MCP 의존**: `atlassian` (HTTP) → **`github`**
- **필수 플러그인**: `github@claude-plugins-official` 필수로 격상, `atlassian@claude-plugins-official` 제거
- **필수 CLI**: `gh` 추가
- **워크플로우 모델**: Confluence Story 페이지 → `docs/stories/<KEY>.md`. Jira workflow → GitHub Issue + phase:* labels + Actions
- **PR 모델**: 1 Story = 2 PRs (Phase 1 docs / Phase 2 code+docs append)

### project.yaml 스키마

`atlassian.*` 키 모두 삭제 → `github.*` 키 신설. 자세한 형식은 [project-config-schema.md](project-config-schema.md) 참조.

### 영향 범위

기존 v0.7 consumer가 0건이므로 마이그레이션 도구·자동 변환은 제공하지 않는다. v0.8 이후 신규 시작 consumer는 [consumer-guide.md](consumer-guide.md) 셋업 절차를 따른다.

### 참고

- 설계 spec: `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md`
- 구현 plan: `docs/superpowers/plans/2026-04-25-atlassian-to-github-migration.md`
```

- [ ] **Step 2: README.md 갱신**

backend 명시 부분: "atlassian (Confluence/Jira)" → "GitHub (Issues/PR/Milestones/Sub-issues/Projects v2/Discussions/Actions/repo files)". breaking change 안내 한 줄.

- [ ] **Step 3: CHANGELOG.md에 v0.8 섹션 추가**

```markdown
## v0.8 — 2026-04-XX (Breaking)

### Breaking
- Atlassian backend 완전 제거. consumer는 GitHub-only로만 사용 가능
- `atlassian.*` project.yaml 스키마 → `github.*`로 교체
- 24 agents의 atlassian MCP 권한 제거, github MCP read 권한 추가 (DocsAgent는 추가로 write)
- 필수 플러그인 4종 (codex, superpowers, claude-md-management, **github**), 필수 CLI 2종 (codex, **gh**)

### Added
- `templates/github-workflows/*.yml` 6개 (story-init, phase-label-invariant, story-section-1-immutable, subissue-from-impl-manifest, phase-gate-mergeable, fix-ledger-sync)
- `templates/github-issue-forms/*.yml` 3개 (story, bug, audit)
- `templates/github-pr-template.md` (Phase 1 / Phase 2 양식 분리)
- `templates/CODEOWNERS.template`
- `scripts/check-no-atlassian.sh`, `check-agent-frontmatter.sh`, `check-doc-links.sh`

### Changed
- `docs/stories/<KEY>.md`로 Story §1-11 single-file SSOT
- `docs/adr/ADR-NNN-<slug>.md` flat + frontmatter `category:`
- `docs/domain-knowledge/<area>/<topic>.md` 계층

### Migration
v0.7 이하에서 v0.8로 in-place 업그레이드 불가. [migration-guide.md](docs/migration-guide.md#v07--v08-atlassian-제거--github-전환) 참조.
```

- [ ] **Step 4: link checker + Commit**

```bash
./scripts/check-doc-links.sh
git add docs/migration-guide.md README.md CHANGELOG.md
git commit -m "docs: v0.7→v0.8 마이그레이션 가이드 + README/CHANGELOG 갱신"
```

---

### Task 27: Phase 검증 — Phase E 종료 시 점검

- [ ] **Step 1: 전체 atlassian 잔재 검사**

```bash
./scripts/check-no-atlassian.sh
```

Expected: PASS (allowlist 제외 0건)

- [ ] **Step 2: agent frontmatter 검증**

```bash
./scripts/check-agent-frontmatter.sh
```

Expected: PASS (24 agents 모두 atlassian MCP 도구 0건)

- [ ] **Step 3: link checker**

```bash
./scripts/check-doc-links.sh
```

Expected: PASS

- [ ] **Step 4: yamllint + actionlint 전수 검사**

```bash
yamllint templates/github-workflows/*.yml templates/github-issue-forms/*.yml
actionlint templates/github-workflows/*.yml
```

Expected: PASS

- [ ] **Step 5: 모두 PASS면 다음 phase**

---

## Phase F: Final Validation + Release Prep

### Task 28: 최종 통합 검증 + 다음 단계 안내

- [ ] **Step 1: 전체 검증 스크립트 일괄 실행**

```bash
echo "=== atlassian 잔재 검사 ==="
./scripts/check-no-atlassian.sh

echo "=== agent frontmatter 검사 ==="
./scripts/check-agent-frontmatter.sh

echo "=== 마크다운 링크 검사 ==="
./scripts/check-doc-links.sh

echo "=== YAML lint ==="
yamllint templates/github-workflows/ templates/github-issue-forms/

echo "=== Action lint ==="
actionlint templates/github-workflows/*.yml

echo "=== git status (clean이어야 함) ==="
git status

echo "=== 변경된 파일 수 ==="
git log --oneline main.. | wc -l
```

Expected: 모든 검사 PASS, git status clean.

- [ ] **Step 2: 변경 요약 print**

```bash
echo "=== Created files ==="
git diff --diff-filter=A --name-only main..

echo "=== Modified files ==="
git diff --diff-filter=M --name-only main..

echo "=== Deleted files (없어야 함) ==="
git diff --diff-filter=D --name-only main..
```

- [ ] **Step 3: 릴리스 태그 준비** (실제 push·tag는 사용자 결정)

```bash
echo "v0.8 릴리스 준비 완료. 다음 단계:"
echo "1. PR 생성 (codeforge plugin 자체 변경)"
echo "2. Architect review"
echo "3. Merge → tag v0.8"
```

- [ ] **Step 4: 작업 완료 commit (있다면)**

만약 Task 27까지 모두 완료했고 git status가 clean이면 추가 commit 불필요. dirty 상태이면:

```bash
git add -u
git status   # 확인 후
git commit -m "chore: v0.8 atlassian → github 마이그레이션 최종 정리"
```

---

## Self-Review Checklist (작성 후 점검)

이 plan 작성 후 spec과 대조해 다음을 확인:

- [ ] spec §2 8개 영역 모두 구현 task에 매핑 — 1:Workflow 메타(Tasks 6, 10, 13), 2:Story §1-11(Tasks 10, 23), 3:FIX Ledger(Task 13 fix-ledger-sync), 4:ADR(Tasks 5, 24), 5:Domain KB(Task 25), 6:Phase 코멘트(Task 16 DocsAgent), 7:Bug/Audit(Tasks 7, 8), 8:Workflow 전이(Tasks 11, 13)
- [ ] spec §3 Story Lifecycle 6단계 — story-init.yml(Task 10), Phase 1 PR 흐름(CLAUDE.md, playbook, DocsAgent), Phase 2 PR 흐름(동일), FIX 루프(fix-ledger-sync, DocsAgent)
- [ ] spec §4 Agent 권한 재매핑 24개 — Tasks 16, 17, 18, 19, 20, 21
- [ ] spec §5 GitHub Actions 6종 — Tasks 10, 11, 12, 13
- [ ] spec §6 세션 개시 의무 — Task 14 CLAUDE.md
- [ ] spec §7 project.yaml 스키마 — Task 2
- [ ] spec §8 변경 항목 32건 — 표 cross-check
- [ ] spec §9 Error handling — Task 14 CLAUDE.md + Task 15 playbook
- [ ] spec §10 Testing — Task 1 + Task 27 검증

Placeholder scan: TBD/TODO/"implement later" 등 0건 — Task 마다 concrete 코드/명령 제공 ✓

Type consistency: `<KEY>`, `<slug>`, `phase:*`, `fix:*`, `gate:*`, `type:*` 라벨 명명 일관 — 모든 task에서 동일 ✓

---

## Risks · Open Considerations

- **Action 동작 검증**: GitHub-hosted runner에서 실제 동작은 PR 머지·테스트 셋업 후 확인. 본 plan은 yamllint·actionlint까지만 보장
- **§1 immutable line range 검증의 false positive**: §1 본문에 마크다운 코드 블록 등이 들어가면 awk pattern이 어색할 수 있음. 첫 실 사용 시 케이스별 보강
- **subissue API beta**: `addSubIssue` mutation은 GitHub GraphQL 베타. 실 사용 시 API 변경 가능성 모니터링
- **gh CLI 버전 의존**: `gh label create`, `gh issue create --template`, `gh api repos/*/milestones*` 등은 gh ≥ 2.40 필요. consumer-guide에서 명시
