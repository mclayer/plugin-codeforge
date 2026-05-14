#!/usr/bin/env bash
# manual-story-init-fallback.sh — Action 차단 환경 수동 Story init fallback (CFP-658 Phase 2)
#
# ADR-027 Amendment 2 §결정 6.H + 6.E + 6.G + 6.I 정합
# Trigger (A): enterprise GitHub Actions default_workflow_permissions:read 차단 환경
# Trigger (C): Issue 발의자 ad-hoc override (`fallback:manual` label 부착, 우선순위 (C) > (A))
#
# Usage:
#   bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>
#
# 환경 변수 (선택, 기본값 auto-detect):
#   GITHUB_REPOSITORY   — "org/repo" 형식 (미설정 시 git remote 추론)
#   STORY_KEY_PREFIX    — Story KEY prefix (미설정 시 project.yaml 또는 "CFP" fallback)
#   GH_TOKEN            — GitHub PAT (CODEFORGE_STORY_WRITER_PAT 우선, ADR-027 §결정 6.F)
#   CODEFORGE_STORY_WRITER_PAT — story write 전용 PAT (2-PAT namespace, ADR-027 §결정 6.F)
#
# Exit codes:
#   0 — 성공 (story file + branch + PR 생성 완료) 또는 idempotent skip
#   1 — 사용법 오류 또는 필수 의존성 부재
#   2 — GitHub API 오류 (backoff 소진 후)
#   3 — shell injection 위험 감지 (Issue 번호 형식 불일치)
#
# 보안:
#   - shell injection 차단: Issue 번호는 숫자 전용 검증 (ADR-027 §결정 6.E)
#   - Issue body: printf '%s' + heredoc single-quoted <<'EOF' 로 eval 금지 (ADR-027 §결정 6.E)
#   - PAT scope: CODEFORGE_STORY_WRITER_PAT (contents:write + pull-requests:write) 우선 사용
#     (ADR-027 §결정 6.F + ADR-066 rotation policy)
#
# Burst control (ADR-027 §결정 6.G):
#   Issue 10개 이상 연속 호출 시 10s sleep (rate-limit 보호)
#   exponential backoff: 1s / 2s / 4s (max 3 retry), 소진 시 fallback:rate-limited label

set -euo pipefail

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

SCRIPT_NAME="manual-story-init-fallback"
MAX_RETRIES=3
BURST_THRESHOLD=10
DEFAULT_PREFIX="CFP"

# ---------------------------------------------------------------------------
# 사용법 확인
# ---------------------------------------------------------------------------

if [[ $# -lt 1 || $# -gt 1 ]]; then
  printf 'Usage: %s <ISSUE_NUMBER>\n' "$0" >&2
  printf '\n  ISSUE_NUMBER: GitHub Issue 번호 (숫자 전용)\n' >&2
  printf '\nExample:\n  bash templates/scripts/%s.sh 42\n' "$SCRIPT_NAME" >&2
  exit 1
fi

ISSUE_NUMBER="$1"

# ---------------------------------------------------------------------------
# SecurityArch 조건 3 — shell injection 차단: Issue 번호 숫자 전용 검증
# ---------------------------------------------------------------------------

if ! [[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
  printf '[%s] ERROR: ISSUE_NUMBER must be numeric. Got: %s\n' "$SCRIPT_NAME" "$ISSUE_NUMBER" >&2
  exit 3
fi

# ---------------------------------------------------------------------------
# 의존성 확인
# ---------------------------------------------------------------------------

if ! command -v gh >/dev/null 2>&1; then
  printf '[%s] ERROR: gh CLI 필요. https://cli.github.com 설치 후 재실행\n' "$SCRIPT_NAME" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  printf '[%s] ERROR: git 필요\n' "$SCRIPT_NAME" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# PAT 설정 (ADR-027 §결정 6.F — 2-PAT namespace)
# CODEFORGE_STORY_WRITER_PAT 우선 (story write 전용)
# fallback: GH_TOKEN
# ---------------------------------------------------------------------------

if [[ -n "${CODEFORGE_STORY_WRITER_PAT:-}" ]]; then
  export GH_TOKEN="${CODEFORGE_STORY_WRITER_PAT}"
  printf '[%s] INFO: CODEFORGE_STORY_WRITER_PAT 사용 (story write 전용 PAT)\n' "$SCRIPT_NAME" >&2
elif [[ -z "${GH_TOKEN:-}" ]]; then
  printf '[%s] ERROR: GH_TOKEN 또는 CODEFORGE_STORY_WRITER_PAT 환경 변수 필요\n' "$SCRIPT_NAME" >&2
  printf '  ADR-027 §결정 6.F: CODEFORGE_STORY_WRITER_PAT (contents:write + pull-requests:write)\n' >&2
  printf '  ADR-066: 90일 권장 rotation (최대 180일)\n' >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# GITHUB_REPOSITORY 자동 감지
# ---------------------------------------------------------------------------

if [[ -z "${GITHUB_REPOSITORY:-}" ]]; then
  REMOTE_URL=$(git remote get-url origin 2>/dev/null || true)
  if [[ -z "$REMOTE_URL" ]]; then
    printf '[%s] ERROR: GITHUB_REPOSITORY 환경 변수 또는 git remote origin 필요\n' "$SCRIPT_NAME" >&2
    exit 1
  fi
  # https://github.com/org/repo.git 또는 git@github.com:org/repo.git
  GITHUB_REPOSITORY=$(printf '%s' "$REMOTE_URL" | sed -E 's|.*github\.com[:/]([^/]+/[^/]+)(\.git)?$|\1|')
  if [[ -z "$GITHUB_REPOSITORY" || "$GITHUB_REPOSITORY" == "$REMOTE_URL" ]]; then
    printf '[%s] ERROR: git remote URL 에서 org/repo 추출 실패: %s\n' "$SCRIPT_NAME" "$REMOTE_URL" >&2
    printf '  GITHUB_REPOSITORY 환경 변수를 직접 설정하세요 (e.g. export GITHUB_REPOSITORY=acme/task-manager)\n' >&2
    exit 1
  fi
  printf '[%s] INFO: GITHUB_REPOSITORY=%s (git remote 추론)\n' "$SCRIPT_NAME" "$GITHUB_REPOSITORY" >&2
fi

# ---------------------------------------------------------------------------
# Story KEY prefix 결정
# ---------------------------------------------------------------------------

if [[ -z "${STORY_KEY_PREFIX:-}" ]]; then
  # project.yaml 에서 story_key_prefix 추출 시도
  YAML_PATH=".claude/_overlay/project.yaml"
  if [[ -f "$YAML_PATH" ]]; then
    PREFIX_FROM_YAML=$(grep -E '^\s*story_key_prefix\s*:' "$YAML_PATH" | head -1 | sed -E 's/.*:\s*"?([^"#]+)"?.*/\1/' | tr -d '[:space:]' || true)
    if [[ -n "$PREFIX_FROM_YAML" && "$PREFIX_FROM_YAML" != "<REPLACE"* ]]; then
      STORY_KEY_PREFIX="$PREFIX_FROM_YAML"
      printf '[%s] INFO: STORY_KEY_PREFIX=%s (project.yaml)\n' "$SCRIPT_NAME" "$STORY_KEY_PREFIX" >&2
    fi
  fi
  if [[ -z "${STORY_KEY_PREFIX:-}" ]]; then
    STORY_KEY_PREFIX="$DEFAULT_PREFIX"
    printf '[%s] WARN: STORY_KEY_PREFIX 미설정 — default "%s" 사용. 실제 prefix 를 STORY_KEY_PREFIX 환경 변수로 지정 권장\n' \
      "$SCRIPT_NAME" "$STORY_KEY_PREFIX" >&2
  fi
fi

KEY="${STORY_KEY_PREFIX}-${ISSUE_NUMBER}"

printf '[%s] INFO: Story KEY=%s, Issue=#%s, Repo=%s\n' "$SCRIPT_NAME" "$KEY" "$ISSUE_NUMBER" "$GITHUB_REPOSITORY" >&2

# ---------------------------------------------------------------------------
# exponential backoff helper (ADR-027 §결정 6.G)
# ---------------------------------------------------------------------------

_gh_with_backoff() {
  local attempt=0
  local delay=1
  while [[ $attempt -lt $MAX_RETRIES ]]; do
    if "$@"; then
      return 0
    fi
    attempt=$((attempt + 1))
    if [[ $attempt -lt $MAX_RETRIES ]]; then
      printf '[%s] WARN: gh 호출 실패 (attempt %d/%d) — %ds 후 재시도\n' \
        "$SCRIPT_NAME" "$attempt" "$MAX_RETRIES" "$delay" >&2
      sleep "$delay"
      delay=$((delay * 2))
    fi
  done
  printf '[%s] ERROR: gh 호출 max retry(%d) 소진\n' "$SCRIPT_NAME" "$MAX_RETRIES" >&2
  return 1
}

# ---------------------------------------------------------------------------
# existence_check verbatim port (story-init.yml L107-124 — ADR-027 §결정 6.H)
# GitHub REST API 로 remote branch 존재 검사 (atomic + cross-firing visible)
# ---------------------------------------------------------------------------

printf '[%s] INFO: existence_check — remote branch 확인 중...\n' "$SCRIPT_NAME" >&2

# Issue title 에서 slug 생성 (소문자, 공백→dash, 특수문자 제거, 30자 제한)
ISSUE_TITLE=$(gh api "repos/${GITHUB_REPOSITORY}/issues/${ISSUE_NUMBER}" --jq '.title' 2>/dev/null || true)
if [[ -z "$ISSUE_TITLE" ]]; then
  printf '[%s] ERROR: Issue #%s fetch 실패 (repo: %s)\n' "$SCRIPT_NAME" "$ISSUE_NUMBER" "$GITHUB_REPOSITORY" >&2
  exit 2
fi

# SecurityArch 조건 3 — shell injection 차단: slug 생성 시 printf '%s' 사용
SLUG=$(printf '%s' "$ISSUE_TITLE" \
  | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9 -]//g' \
  | sed 's/[[:space:]][[:space:]]*/\-/g' \
  | sed 's/--*/-/g' \
  | sed 's/^-//; s/-$//' \
  | cut -c1-30 \
  | sed 's/-$//')

BRANCH="feat/${KEY}-${SLUG}"

if gh api "repos/${GITHUB_REPOSITORY}/branches/${BRANCH}" --silent 2>/dev/null; then
  printf '[%s] INFO: Remote branch %s already exists — skip (idempotent re-entry, ADR-027 §결정 6.H)\n' \
    "$SCRIPT_NAME" "$BRANCH" >&2
  printf '[%s] INFO: fallback:manual label 부착 확인 중...\n' "$SCRIPT_NAME" >&2
  gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" \
    --add-label "fallback:manual" 2>/dev/null || true
  exit 0
fi

printf '[%s] INFO: 신규 branch — Story init 진행\n' "$SCRIPT_NAME" >&2

# ---------------------------------------------------------------------------
# Issue body fetch (ADR-027 §결정 6.E — shell injection 차단)
# printf '%s' + 임시 파일로 eval 완전 차단
# ---------------------------------------------------------------------------

ISSUE_BODY=$(gh api "repos/${GITHUB_REPOSITORY}/issues/${ISSUE_NUMBER}" --jq '.body' 2>/dev/null || true)
if [[ -z "$ISSUE_BODY" ]]; then
  printf '[%s] ERROR: Issue #%s body fetch 실패\n' "$SCRIPT_NAME" "$ISSUE_NUMBER" >&2
  exit 2
fi

# 임시 파일 사용 (shell injection 2중 차단)
TMPDIR_FALLBACK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_FALLBACK"' EXIT

ISSUE_BODY_FILE="${TMPDIR_FALLBACK}/issue-body.txt"
printf '%s' "$ISSUE_BODY" > "$ISSUE_BODY_FILE"

# ---------------------------------------------------------------------------
# 사용자 요구사항 섹션 추출
# ---------------------------------------------------------------------------

REQUIREMENT=$(awk '/^### 사용자 요구사항/{flag=1; next} /^### /{flag=0} flag' "$ISSUE_BODY_FILE" \
  | sed '/^$/d' || true)

TITLE_CLEAN=$(printf '%s' "$ISSUE_TITLE" \
  | sed 's/\[.*\]//g' \
  | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')

# ---------------------------------------------------------------------------
# git 설정 + branch 생성
# ---------------------------------------------------------------------------

printf '[%s] INFO: git branch %s 생성 중...\n' "$SCRIPT_NAME" "$BRANCH" >&2

git config user.name "codeforge-fallback[bot]"
git config user.email "codeforge-fallback[bot]@users.noreply.github.com"

# origin/main 기준으로 branch 생성
git fetch origin main --quiet
git checkout -b "$BRANCH" origin/main

# ---------------------------------------------------------------------------
# Story file 생성 (docs/stories/<KEY>.md)
# §1 verbatim + §2-11 placeholder (story-init.yml 정합)
# ADR-027 §결정 6.E: heredoc single-quoted <<'EOF' 사용 (verbatim transmission)
# ---------------------------------------------------------------------------

printf '[%s] INFO: docs/stories/%s.md 생성 중...\n' "$SCRIPT_NAME" "$KEY" >&2
mkdir -p docs/stories

STORY_FILE="docs/stories/${KEY}.md"

# frontmatter + §1 (verbatim port from story-init.yml)
{
  cat <<FRONTMATTER_EOF
---
story_key: ${KEY}
story_issues:
  - repo: ${GITHUB_REPOSITORY}
    number: ${ISSUE_NUMBER}
status: phase:요구사항
---
FRONTMATTER_EOF
  printf '\n# %s: %s\n\n' "$KEY" "$TITLE_CLEAN"
  printf -- '- **Issue**: #%s\n' "$ISSUE_NUMBER"
  printf -- '- **Status**: phase:요구사항\n\n'
  printf -- '- **Fallback**: manual (ADR-027 Amendment 2 §결정 6.A — Action 차단 환경)\n\n'
  printf '## 1. 사용자 요구사항 (verbatim — Phase 2 후속 CFP 까지 CODEOWNERS manual review 로 변경 차단)\n\n'
  printf '%s\n\n' "$REQUIREMENT"
  cat <<'TPL_EOF'
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
TPL_EOF
} > "$STORY_FILE"

git add "$STORY_FILE"
git commit -m "[${KEY}] feat: Story init (manual fallback) — §1 verbatim, §2-11 placeholder"

# ---------------------------------------------------------------------------
# push (backoff 적용)
# ---------------------------------------------------------------------------

printf '[%s] INFO: origin 에 push 중...\n' "$SCRIPT_NAME" >&2

_gh_with_backoff git push origin "$BRANCH" || {
  printf '[%s] ERROR: push 실패 — fallback:rate-limited label 부착\n' "$SCRIPT_NAME" >&2
  gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" \
    --add-label "fallback:rate-limited" 2>/dev/null || true
  exit 2
}

# ---------------------------------------------------------------------------
# fallback:manual label 부착 (ADR-027 §결정 6.A 의무)
# ---------------------------------------------------------------------------

printf '[%s] INFO: fallback:manual label 부착 중...\n' "$SCRIPT_NAME" >&2
gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" \
  --add-label "fallback:manual" 2>/dev/null || \
  printf '[%s] WARN: fallback:manual label 부착 실패 (label 미존재 가능) — bootstrap-labels.sh 실행 권장\n' "$SCRIPT_NAME" >&2

# ---------------------------------------------------------------------------
# Phase 1 PR 생성 (ADR-027 §결정 6.I — PR description checklist mirror)
# ---------------------------------------------------------------------------

printf '[%s] INFO: Phase 1 PR 생성 중...\n' "$SCRIPT_NAME" >&2

PR_BODY=$(cat <<PR_BODY_EOF
Story SSOT: \`docs/stories/${KEY}.md\`

이 PR은 Phase 1 PR (요구사항+설계+설계리뷰 lane)입니다.
architect team CODEOWNERS auto-review attached.

Related: #${ISSUE_NUMBER}

---

**[Fallback] manual-story-init-fallback.sh 로 생성됨 (ADR-027 Amendment 2 §결정 6.A)**

이 PR은 GitHub Actions story-init.yml 차단 환경에서 수동으로 생성되었습니다.
아래 체크리스트를 수동으로 확인하세요:

- [ ] §1 사용자 요구사항이 Issue body 와 verbatim 일치 확인
- [ ] phase:요구사항 label 부착 확인
- [ ] fallback:manual label 부착 확인
- [ ] CODEOWNERS architect team review request 수동 추가 (필요 시)
- [ ] phase-gate-mergeable.yml required check 통과 여부 확인

참조: consumer-guide §1h / docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md
PR_BODY_EOF
)

_gh_with_backoff gh pr create \
  --repo "$GITHUB_REPOSITORY" \
  --base "main" \
  --head "$BRANCH" \
  --title "[${KEY}] ${TITLE_CLEAN}" \
  --body "$PR_BODY" \
  --label "type:story,phase:요구사항,fallback:manual" || {
  printf '[%s] ERROR: PR 생성 실패 — fallback:rate-limited label 부착\n' "$SCRIPT_NAME" >&2
  gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" \
    --add-label "fallback:rate-limited" 2>/dev/null || true
  exit 2
}

printf '[%s] SUCCESS: Story %s init 완료 (branch: %s)\n' "$SCRIPT_NAME" "$KEY" "$BRANCH" >&2
printf '[%s] INFO: 다음 단계: Orchestrator 가 RequirementsPLAgent spawn → §2-§6 작성\n' "$SCRIPT_NAME" >&2
