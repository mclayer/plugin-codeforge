# wire-branch-protection.ps1 — CFP-2469 (Epic CFP-2468 Track W/W1) branch protection write SSOT (Windows variant).
#
# wire-branch-protection.sh 의 PowerShell 5.1+ wrapper. 동작 parity (AC-8).
# ADR-132 §결정 1 — branch protection write 로직 단일 SSOT.
#
# 메커니즘 (ADR-132 §결정 2/3/4/5/6) — .sh 동형:
#   - GET-merge-PUT idempotent (desired-state union merge, AC-5)
#   - operator gh auth 토큰 (옵션 A — codeforge PAT 미사용, ADR-066 무손상, AC-7)
#   - review_count 형상 파라미터 (solo=0 / team≥1, AC-2)
#   - enforce_admins=true / restrictions=null / strict=true default (ADR-132 §결정 5)
#   - context↔job-name 정합 게이트 (AC-4 — 미정합 제외 + WARN)
#   - 403 → WARN graceful degrade (AC-3)
#
# Usage:
#   pwsh -File scripts/wire-branch-protection.ps1 -Repo <owner/name> [-Shape solo|team]
#        [-ReviewCount N] [-Branch main] [-DryRun] [-Inspect] [-Contexts "a,b,c"]
#
# Exit code:
#   0 = 배선 성공 (또는 -Inspect 배선 확인 / -DryRun payload 산출)
#   2 = error (gh 부재 / repo 미탐지)
#   3 = graceful degrade (403 → WARN / -Inspect dead-gate 검출)
#
# SSOT: ADR-132 + Change Plan cfp-2469-consumer-branch-protection-wire.md §3

[CmdletBinding()]
param(
    [string]$Repo = "",
    [ValidateSet("solo", "team")]
    [string]$Shape = "solo",
    [string]$ReviewCount = "",
    [string]$Branch = "main",
    [string]$Contexts = "",
    [switch]$DryRun,
    [switch]$Inspect
)

$ErrorActionPreference = "Continue"

# Core contexts (ADR-024 §결정 A 삭제 불허 invariant — .sh DEFAULT_CONTEXTS 동형)
$DefaultContexts = @(
    "phase-gate-mergeable",
    "invariant-check",
    "doc frontmatter schema (CFP-28 — strict)",
    "doc section schema (CFP-28 — strict)"
)

function Log([string]$msg) {
    [Console]::Error.WriteLine("[wire-branch-protection] $msg")
}

# ── repo 탐지 ──
if (-not $Repo) {
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $Repo = (gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>$null)
    }
}
if (-not $Repo) {
    Log "ERROR: -Repo <owner/name> 미지정 + 자동 탐지 실패"
    exit 2
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Log "ERROR: gh CLI 미설치 (operator gh auth 토큰 필요, ADR-132 §결정 2)"
    exit 2
}

# ── shape → review_count 분기 (ADR-132 §결정 5, AC-2) ──
function Resolve-ReviewCount {
    if ($ReviewCount) { return $ReviewCount }
    switch ($Shape) {
        "solo" { return "0" }
        "team" { return "1" }
        # default 분기 불필요 — [ValidateSet("solo","team")] 가 param binding 단계에서
        # 그 외 값을 차단 (N-CR-2469-2: dead code 제거). fail-safe 는 ValidateSet 이 담당.
    }
}

# ── 후보 context 목록 ──
function Get-CandidateContexts {
    if ($Contexts) {
        return @($Contexts -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }
    return $DefaultContexts
}

# ── actual check names (정합 게이트 input, ADR-132 §결정 4) ──
function Get-ActualCheckNames([string]$repo, [string]$branch) {
    $sha = (gh api "repos/$repo/commits/$branch" --jq '.sha' 2>$null)
    if (-not $sha) { return @() }
    $names = gh api "repos/$repo/commits/$sha/check-runs" --paginate --jq '.check_runs[].name' 2>$null
    if (-not $names) { return @() }
    return @($names)
}

# ── 현 protection state GET (GET-merge + -Inspect 재사용) ──
function Get-CurrentContexts([string]$repo, [string]$branch) {
    $ctx = gh api "repos/$repo/branches/$branch/protection/required_status_checks" --jq '.contexts[]?' 2>$null
    if (-not $ctx) { return @() }
    return @($ctx)
}

function Test-ProtectionExists([string]$repo, [string]$branch) {
    gh api "repos/$repo/branches/$branch/protection" --jq '.url' *>$null
    return ($LASTEXITCODE -eq 0)
}

# ────────────────────────────────────────────────────────── -Inspect ──
if ($Inspect) {
    if (-not (Test-ProtectionExists $Repo $Branch)) {
        Log "INSPECT: $Repo@$Branch — branch protection 부재 (dead gate)"
        exit 3
    }
    $cur = Get-CurrentContexts $Repo $Branch
    $curCount = @($cur).Count
    $ea = (gh api "repos/$Repo/branches/$Branch/protection/enforce_admins" --jq '.enabled' 2>$null)
    if (-not $ea) { $ea = "unknown" }
    Log "INSPECT: $Repo@$Branch — protection 활성, contexts=$curCount, enforce_admins=$ea"
    if ($curCount -eq 0) {
        Log "INSPECT: required_status_checks.contexts 0개 (dead gate — workflow 돌지만 merge 차단력 0)"
        exit 3
    }
    exit 0
}

# ────────────────────────────────────────────────── 정합 게이트 + payload ──
$rcValue = Resolve-ReviewCount
$candidates = Get-CandidateContexts
$actual = Get-ActualCheckNames $Repo $Branch

$appliedContexts = @()
$excludedContexts = @()
if (@($actual).Count -eq 0) {
    Log "WARN: actual check run 0개 ($Repo@$Branch) — 정합 검증 불가 → 후보 전체 배선 (실 배포 후 재배선 권장, AC-4)"
    $appliedContexts = $candidates
} else {
    foreach ($ctx in $candidates) {
        if ($actual -contains $ctx) {
            $appliedContexts += $ctx
        } else {
            $excludedContexts += $ctx
        }
    }
    if (@($excludedContexts).Count -gt 0) {
        Log "WARN: context↔job-name 미정합 $(@($excludedContexts).Count)개 배선 제외 (영구 pending 차단, AC-4):"
        foreach ($e in $excludedContexts) { Log "  - $e" }
    }
}

# ── GET-merge: 현 contexts union (consumer 고유 보존, AC-5 / ADR-132 §결정 6) ──
$existing = Get-CurrentContexts $Repo $Branch
$seen = @{}
$mergedContexts = @()
foreach ($ec in $existing) {
    if ($ec -and -not $seen.ContainsKey($ec)) { $seen[$ec] = $true; $mergedContexts += $ec }
}
foreach ($ac in $appliedContexts) {
    if (-not $seen.ContainsKey($ac)) { $seen[$ac] = $true; $mergedContexts += $ac }
}

if (@($mergedContexts).Count -eq 0) {
    Log "WARN: 배선할 context 0개 (후보 ∩ actual = ∅ + 현 contexts 0) — 배선 skip (dead-gate 잔존)"
    Log "      → workflow 배포 후 재실행 권장 (정합 게이트 산출 0)"
    exit 3
}

# ── desired PUT payload (ADR-132 §결정 5 형상 4필드, full-replacement) ──
$payloadObj = [ordered]@{
    required_status_checks        = [ordered]@{ strict = $true; contexts = @($mergedContexts) }
    enforce_admins                = $true
    required_pull_request_reviews = [ordered]@{
        required_approving_review_count = [int]$rcValue
        require_code_owner_reviews      = $false
    }
    restrictions                  = $null
}
$payload = $payloadObj | ConvertTo-Json -Depth 10

# ────────────────────────────────────────────────────────── -DryRun ──
if ($DryRun) {
    Log "DRY-RUN: $Repo@$Branch — PUT 0 (side-effect 0). desired payload:"
    Write-Output $payload
    Log "DRY-RUN: shape=$Shape review_count=$rcValue contexts=$(@($mergedContexts).Count) (정합 제외 $(@($excludedContexts).Count)개)"
    exit 0
}

# ────────────────────────────────────────────────────────── PUT ──
# operator gh auth 토큰 (ADR-132 §결정 2, AC-7). 403 → WARN graceful (§결정 3, AC-3).
Log "PUT: $Repo@$Branch — shape=$Shape review_count=$rcValue contexts=$(@($mergedContexts).Count)"
$putOut = ($payload | gh api -X PUT "repos/$Repo/branches/$Branch/protection" --input - 2>&1) | Out-String
$putRc = $LASTEXITCODE

if ($putRc -eq 0) {
    Log "PUT 성공: $Repo@$Branch branch protection 배선 완료 (merge 차단력 충전)"
    exit 0
}

if ($putOut -match "403|Resource not accessible|Must have admin|Administration") {
    Log "WARN: $Repo@$Branch — 403 권한 부족 (operator 가 org-admin 아님). graceful degrade (AC-3):"
    Log "      → drift preview fallback: bash templates/scripts/setup-branch-protection.sh --dry-run"
    Log "      → operator org-admin 권한으로 수동 적용 또는 권한 확보 후 재실행"
    exit 3
}

Log "ERROR: $Repo@$Branch — PUT 실패 (403 외): $putOut"
exit 2
