#Requires -Version 5.1
<#
.SYNOPSIS
    Action 차단 환경 수동 Story init fallback (CFP-658 Phase 2, Windows PowerShell parity)

.DESCRIPTION
    ADR-027 Amendment 2 §결정 6.H + 6.E + 6.G + 6.I 정합 — Bash 동일 logic, PowerShell semantics.
    Trigger (A): enterprise GitHub Actions default_workflow_permissions:read 차단 환경
    Trigger (C): Issue 발의자 ad-hoc override (`fallback:manual` label 부착, 우선순위 (C) > (A))

.PARAMETER IssueNumber
    GitHub Issue 번호 (숫자 전용, 필수)

.EXAMPLE
    .\templates\scripts\manual-story-init-fallback.ps1 -IssueNumber 42

.EXAMPLE
    $env:STORY_KEY_PREFIX = "TM"
    $env:CODEFORGE_STORY_WRITER_PAT = "ghp_..."
    .\templates\scripts\manual-story-init-fallback.ps1 -IssueNumber 42

.NOTES
    보안 (ADR-027 §결정 6.E):
      - IssueNumber: 숫자 전용 검증 (shell injection 차단)
      - Issue body: Out-File 임시 파일 경유 (eval 차단)
    PAT scope (ADR-027 §결정 6.F):
      CODEFORGE_STORY_WRITER_PAT 우선 (contents:write + pull-requests:write)
      fallback: GH_TOKEN
    Burst control (ADR-027 §결정 6.G):
      exponential backoff 1s/2s/4s, max 3 retry
      소진 시 fallback:rate-limited label 부착

    Exit codes:
      0 — 성공 또는 idempotent skip
      1 — 사용법 오류 또는 필수 의존성 부재
      2 — GitHub API 오류 (backoff 소진 후)
      3 — shell injection 위험 감지 (Issue 번호 형식 불일치)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$IssueNumber
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

$SCRIPT_NAME = "manual-story-init-fallback"
$MAX_RETRIES = 3
$DEFAULT_PREFIX = "CFP"

# ---------------------------------------------------------------------------
# SecurityArch 조건 3 — shell injection 차단: Issue 번호 숫자 전용 검증
# ---------------------------------------------------------------------------

if ($IssueNumber -notmatch '^\d+$') {
    Write-Error "[$SCRIPT_NAME] ERROR: IssueNumber must be numeric. Got: $IssueNumber"
    exit 3
}

# ---------------------------------------------------------------------------
# 의존성 확인
# ---------------------------------------------------------------------------

foreach ($cmd in @('gh', 'git')) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "[$SCRIPT_NAME] ERROR: $cmd 필요. 설치 후 재실행"
        exit 1
    }
}

# ---------------------------------------------------------------------------
# PAT 설정 (ADR-027 §결정 6.F — 2-PAT namespace)
# CODEFORGE_STORY_WRITER_PAT 우선 (story write 전용)
# ---------------------------------------------------------------------------

if ($env:CODEFORGE_STORY_WRITER_PAT) {
    $env:GH_TOKEN = $env:CODEFORGE_STORY_WRITER_PAT
    Write-Host "[$SCRIPT_NAME] INFO: CODEFORGE_STORY_WRITER_PAT 사용 (story write 전용 PAT)" -ForegroundColor Cyan
} elseif (-not $env:GH_TOKEN) {
    Write-Error (
        "[$SCRIPT_NAME] ERROR: GH_TOKEN 또는 CODEFORGE_STORY_WRITER_PAT 환경 변수 필요`n" +
        "  ADR-027 §결정 6.F: CODEFORGE_STORY_WRITER_PAT (contents:write + pull-requests:write)`n" +
        "  ADR-066: 90일 권장 rotation (최대 180일)"
    )
    exit 1
}

# ---------------------------------------------------------------------------
# GITHUB_REPOSITORY 자동 감지
# ---------------------------------------------------------------------------

if (-not $env:GITHUB_REPOSITORY) {
    try {
        $remoteUrl = git remote get-url origin 2>$null
        if ($remoteUrl -match 'github\.com[:/]([^/]+/[^/.]+)(\.git)?$') {
            $env:GITHUB_REPOSITORY = $Matches[1]
            Write-Host "[$SCRIPT_NAME] INFO: GITHUB_REPOSITORY=$($env:GITHUB_REPOSITORY) (git remote 추론)" -ForegroundColor Cyan
        } else {
            Write-Error "[$SCRIPT_NAME] ERROR: git remote URL 에서 org/repo 추출 실패: $remoteUrl`n  GITHUB_REPOSITORY 환경 변수를 직접 설정하세요"
            exit 1
        }
    } catch {
        Write-Error "[$SCRIPT_NAME] ERROR: GITHUB_REPOSITORY 환경 변수 또는 git remote origin 필요"
        exit 1
    }
}

$REPO = $env:GITHUB_REPOSITORY

# ---------------------------------------------------------------------------
# Story KEY prefix 결정
# ---------------------------------------------------------------------------

if (-not $env:STORY_KEY_PREFIX) {
    $yamlPath = ".claude/_overlay/project.yaml"
    if (Test-Path $yamlPath) {
        $prefixLine = Select-String -Path $yamlPath -Pattern '^\s*story_key_prefix\s*:' | Select-Object -First 1
        if ($prefixLine) {
            $prefixVal = $prefixLine.Line -replace '.*:\s*"?([^"#\s]+)"?.*', '$1'
            if ($prefixVal -and -not $prefixVal.StartsWith('<REPLACE')) {
                $env:STORY_KEY_PREFIX = $prefixVal
                Write-Host "[$SCRIPT_NAME] INFO: STORY_KEY_PREFIX=$env:STORY_KEY_PREFIX (project.yaml)" -ForegroundColor Cyan
            }
        }
    }
    if (-not $env:STORY_KEY_PREFIX) {
        $env:STORY_KEY_PREFIX = $DEFAULT_PREFIX
        Write-Warning "[$SCRIPT_NAME] WARN: STORY_KEY_PREFIX 미설정 — default '$DEFAULT_PREFIX' 사용. 실제 prefix 를 STORY_KEY_PREFIX 환경 변수로 지정 권장"
    }
}

$KEY = "$($env:STORY_KEY_PREFIX)-$IssueNumber"
Write-Host "[$SCRIPT_NAME] INFO: Story KEY=$KEY, Issue=#$IssueNumber, Repo=$REPO" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# exponential backoff helper (ADR-027 §결정 6.G)
# ---------------------------------------------------------------------------

function Invoke-GhWithBackoff {
    param([scriptblock]$ScriptBlock)
    $attempt = 0
    $delay = 1
    while ($attempt -lt $MAX_RETRIES) {
        try {
            & $ScriptBlock
            if ($LASTEXITCODE -eq 0) { return }
            throw "exit code $LASTEXITCODE"
        } catch {
            $attempt++
            if ($attempt -lt $MAX_RETRIES) {
                Write-Warning "[$SCRIPT_NAME] WARN: gh 호출 실패 (attempt $attempt/$MAX_RETRIES) — ${delay}s 후 재시도"
                Start-Sleep -Seconds $delay
                $delay = $delay * 2
            }
        }
    }
    Write-Error "[$SCRIPT_NAME] ERROR: gh 호출 max retry($MAX_RETRIES) 소진"
    exit 2
}

# ---------------------------------------------------------------------------
# existence_check verbatim port (story-init.yml L107-124 — ADR-027 §결정 6.H)
# ---------------------------------------------------------------------------

Write-Host "[$SCRIPT_NAME] INFO: existence_check — remote branch 확인 중..." -ForegroundColor Cyan

$issueJson = gh api "repos/$REPO/issues/$IssueNumber" 2>$null
if ($LASTEXITCODE -ne 0 -or -not $issueJson) {
    Write-Error "[$SCRIPT_NAME] ERROR: Issue #$IssueNumber fetch 실패 (repo: $REPO)"
    exit 2
}

$issueData = $issueJson | ConvertFrom-Json
$ISSUE_TITLE = $issueData.title
$ISSUE_BODY_RAW = $issueData.body

if (-not $ISSUE_TITLE) {
    Write-Error "[$SCRIPT_NAME] ERROR: Issue #$IssueNumber title 추출 실패"
    exit 2
}

# slug 생성 (소문자, 공백→dash, 특수문자 제거, 30자 제한)
$slug = $ISSUE_TITLE.ToLower() `
    -replace '[^a-z0-9 \-]', '' `
    -replace '\s+', '-' `
    -replace '-+', '-' `
    -replace '^-|-$', ''
if ($slug.Length -gt 30) {
    $slug = $slug.Substring(0, 30).TrimEnd('-')
}

$BRANCH = "feat/$KEY-$slug"

# remote branch 존재 여부 검사
$branchCheck = gh api "repos/$REPO/branches/$BRANCH" --silent 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[$SCRIPT_NAME] INFO: Remote branch $BRANCH already exists — skip (idempotent re-entry, ADR-027 §결정 6.H)" -ForegroundColor Yellow
    gh issue edit $IssueNumber --repo $REPO --add-label "fallback:manual" 2>$null
    exit 0
}

Write-Host "[$SCRIPT_NAME] INFO: 신규 branch — Story init 진행" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# Issue body 임시 파일 저장 (ADR-027 §결정 6.E — eval 차단)
# ---------------------------------------------------------------------------

$tmpDir = New-TemporaryFile | Split-Path
$issueBodyFile = Join-Path $tmpDir "issue-body-$IssueNumber.txt"

try {
    # 빈 body 처리
    if ($null -eq $ISSUE_BODY_RAW) {
        "" | Out-File -FilePath $issueBodyFile -Encoding utf8
    } else {
        $ISSUE_BODY_RAW | Out-File -FilePath $issueBodyFile -Encoding utf8
    }

    # 사용자 요구사항 섹션 추출
    $lines = Get-Content $issueBodyFile -Encoding utf8
    $inSection = $false
    $reqLines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in $lines) {
        if ($line -match '^### 사용자 요구사항') {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match '^### ') {
            $inSection = $false
        }
        if ($inSection -and $line.Trim() -ne '') {
            $reqLines.Add($line)
        }
    }
    $REQUIREMENT = $reqLines -join "`n"

} finally {
    if (Test-Path $issueBodyFile) { Remove-Item $issueBodyFile -Force -ErrorAction SilentlyContinue }
}

$TITLE_CLEAN = $ISSUE_TITLE -replace '\[.*?\]', '' -replace '^\s+|\s+$', ''

# ---------------------------------------------------------------------------
# git 설정 + branch 생성
# ---------------------------------------------------------------------------

Write-Host "[$SCRIPT_NAME] INFO: git branch $BRANCH 생성 중..." -ForegroundColor Cyan

git config user.name "codeforge-fallback[bot]"
git config user.email "codeforge-fallback[bot]@users.noreply.github.com"

git fetch origin main --quiet
git checkout -b $BRANCH origin/main

# ---------------------------------------------------------------------------
# Story file 생성 (docs/stories/<KEY>.md)
# §1 verbatim + §2-11 placeholder
# ---------------------------------------------------------------------------

Write-Host "[$SCRIPT_NAME] INFO: docs/stories/$KEY.md 생성 중..." -ForegroundColor Cyan

$null = New-Item -ItemType Directory -Force -Path "docs/stories"
$STORY_FILE = "docs/stories/$KEY.md"

# frontmatter + §1 verbatim (ADR-027 §결정 6.E: PowerShell here-string @'...'@ 사용)
$storyContent = @"
---
story_key: $KEY
story_issues:
  - repo: $REPO
    number: $IssueNumber
status: phase:요구사항
---

# ${KEY}: ${TITLE_CLEAN}

- **Issue**: #${IssueNumber}
- **Status**: phase:요구사항

- **Fallback**: manual (ADR-027 Amendment 2 §결정 6.A — Action 차단 환경)

## 1. 사용자 요구사항 (verbatim — Phase 2 후속 CFP 까지 CODEOWNERS manual review 로 변경 차단)

$REQUIREMENT

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
"@

$storyContent | Out-File -FilePath $STORY_FILE -Encoding utf8

git add $STORY_FILE
git commit -m "[$KEY] feat: Story init (manual fallback) — §1 verbatim, §2-11 placeholder"

# ---------------------------------------------------------------------------
# push (backoff 적용)
# ---------------------------------------------------------------------------

Write-Host "[$SCRIPT_NAME] INFO: origin 에 push 중..." -ForegroundColor Cyan

Invoke-GhWithBackoff { git push origin $BRANCH }
if ($LASTEXITCODE -ne 0) {
    Write-Warning "[$SCRIPT_NAME] ERROR: push 실패 — fallback:rate-limited label 부착"
    gh issue edit $IssueNumber --repo $REPO --add-label "fallback:rate-limited" 2>$null
    exit 2
}

# ---------------------------------------------------------------------------
# fallback:manual label 부착 (ADR-027 §결정 6.A 의무)
# ---------------------------------------------------------------------------

Write-Host "[$SCRIPT_NAME] INFO: fallback:manual label 부착 중..." -ForegroundColor Cyan
$labelResult = gh issue edit $IssueNumber --repo $REPO --add-label "fallback:manual" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "[$SCRIPT_NAME] WARN: fallback:manual label 부착 실패 (label 미존재 가능) — bootstrap-labels.sh 실행 권장"
}

# ---------------------------------------------------------------------------
# Phase 1 PR 생성 (ADR-027 §결정 6.I — PR description checklist mirror)
# ---------------------------------------------------------------------------

Write-Host "[$SCRIPT_NAME] INFO: Phase 1 PR 생성 중..." -ForegroundColor Cyan

$PR_BODY = @"
Story SSOT: ``docs/stories/$KEY.md``

이 PR은 Phase 1 PR (요구사항+설계+설계리뷰 lane)입니다.
architect team CODEOWNERS auto-review attached.

Related: #$IssueNumber

---

**[Fallback] manual-story-init-fallback.ps1 로 생성됨 (ADR-027 Amendment 2 §결정 6.A)**

이 PR은 GitHub Actions story-init.yml 차단 환경에서 수동으로 생성되었습니다.
아래 체크리스트를 수동으로 확인하세요:

- [ ] §1 사용자 요구사항이 Issue body 와 verbatim 일치 확인
- [ ] phase:요구사항 label 부착 확인
- [ ] fallback:manual label 부착 확인
- [ ] CODEOWNERS architect team review request 수동 추가 (필요 시)
- [ ] phase-gate-mergeable.yml required check 통과 여부 확인

참조: consumer-guide §1h / docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md
"@

Invoke-GhWithBackoff {
    gh pr create `
        --repo $REPO `
        --base "main" `
        --head $BRANCH `
        --title "[$KEY] $TITLE_CLEAN" `
        --body $PR_BODY `
        --label "type:story,phase:요구사항,fallback:manual"
}

Write-Host "[$SCRIPT_NAME] SUCCESS: Story $KEY init 완료 (branch: $BRANCH)" -ForegroundColor Green
Write-Host "[$SCRIPT_NAME] INFO: 다음 단계: Orchestrator 가 RequirementsPLAgent spawn → §2-§6 작성" -ForegroundColor Cyan
