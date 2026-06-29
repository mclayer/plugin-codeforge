# reapply-branch-protection.ps1 — CFP-2469 (Epic CFP-2468 Track W/W1) N-repo 일괄 배선 (Windows variant).
#
# reapply-branch-protection.sh 의 PowerShell 5.1+ wrapper. 동작 parity (AC-8).
# ADR-132 §결정 7 — wire-branch-protection.ps1 을 repo-list loop 로 반복 호출.
#
# 일괄 운영 리스크 3종 (.sh 동형):
#   1. existence_check — branch 부재 repo skip (graceful, abort 금지)
#   2. exponential backoff — rate-limit (secondary 포함) 재시도
#   3. partial-failure 누적보고 — 한 repo 실패가 전체 abort 안 함. 끝까지 진행 후 집계
#
# Usage:
#   pwsh -File scripts/reapply-branch-protection.ps1 -Repos "owner/a,owner/b" [-Shape solo|team]
#   pwsh -File scripts/reapply-branch-protection.ps1 -ReposFile <path> [-ReviewCount N] [-DryRun]
#
# Exit code:
#   0 = 전 repo 성공 (또는 graceful skip/degrade)
#   1 = 1+ repo 실패 (partial-failure)
#   2 = setup error (gh 부재 / repo 목록 0 / wire-* 부재)
#
# SSOT: ADR-132 §결정 7 + Change Plan cfp-2469-consumer-branch-protection-wire.md §3/§7.4

[CmdletBinding()]
param(
    [string]$Repos = "",
    [string]$ReposFile = "",
    [ValidateSet("solo", "team")]
    [string]$Shape = "solo",
    [string]$ReviewCount = "",
    [string]$Branch = "main",
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WireScript = Join-Path $ScriptDir "wire-branch-protection.ps1"

function Log([string]$msg) {
    [Console]::Error.WriteLine("[reapply-branch-protection] $msg")
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Log "ERROR: gh CLI 미설치 (operator gh auth 토큰 필요)"
    exit 2
}
if (-not (Test-Path $WireScript)) {
    Log "ERROR: wire-branch-protection.ps1 부재: $WireScript"
    exit 2
}

# ── repo 목록 수집 ──
$RepoList = @()
if ($Repos) {
    $RepoList += @($Repos -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}
if ($ReposFile) {
    if (-not (Test-Path $ReposFile)) {
        Log "ERROR: -ReposFile 부재: $ReposFile"
        exit 2
    }
    $RepoList += @(Get-Content $ReposFile -Encoding utf8 |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith("#") })
}

if (@($RepoList).Count -eq 0) {
    Log "ERROR: repo 목록 0 — -Repos 또는 -ReposFile 명시"
    exit 2
}

# ── existence_check (ADR-132 §결정 7.1) ──
function Test-BranchExists([string]$repo, [string]$branch) {
    gh api "repos/$repo/branches/$branch" --jq '.name' *>$null
    return ($LASTEXITCODE -eq 0)
}

# ── exp-backoff wrapper (ADR-132 §결정 7.2) ──
function Invoke-WireWithBackoff([string]$repo) {
    $delays = @(2, 4, 8)
    $attempt = 0
    while ($true) {
        $wireArgs = @("-Repo", $repo, "-Shape", $Shape, "-Branch", $Branch)
        if ($ReviewCount) { $wireArgs += @("-ReviewCount", $ReviewCount) }
        if ($DryRun) { $wireArgs += "-DryRun" }
        $out = (& pwsh -File $WireScript @wireArgs 2>&1) | Out-String
        $rc = $LASTEXITCODE
        if ($out -match "rate limit|429|secondary rate|abuse detection") {
            if ($attempt -lt 3) {
                $d = $delays[$attempt]
                Log "  [$repo] rate-limit 신호 — ${d}s backoff 후 재시도 (attempt $($attempt+1)/3)"
                Start-Sleep -Seconds $d
                $attempt++
                continue
            }
            Log "  [$repo] rate-limit 3회 재시도 소진 — 실패 누적"
        }
        [Console]::Error.Write($out)
        return $rc
    }
}

# ────────────────────────────────────────────────── main loop ──
Log "일괄 배선 시작: $(@($RepoList).Count) repo (shape=$Shape branch=$Branch dry-run=$DryRun)"

$Succeeded = @()
$Skipped = @()
$Degraded = @()
$Failed = @()

foreach ($repo in $RepoList) {
    Log "── $repo ──"
    if (-not (Test-BranchExists $repo $Branch)) {
        Log "  SKIP: $repo@$Branch branch 부재 (existence_check — abort 금지, §결정 7.1)"
        $Skipped += $repo
        continue
    }
    $wrc = Invoke-WireWithBackoff $repo
    switch ($wrc) {
        0 { $Succeeded += $repo }
        3 { $Degraded += $repo; Log "  DEGRADED: $repo — 403 권한 부족/dead-gate (graceful, 비-abort)" }
        default { $Failed += $repo; Log "  FAIL: $repo — wire-* exit $wrc (누적, 끝까지 진행)" }
    }
}

# ── 누적보고 (ADR-132 §결정 7.3) ──
Log ""
Log "=== 일괄 배선 집계 ($(@($RepoList).Count) repo) ==="
Log "  성공: $(@($Succeeded).Count)  / skip(branch 부재): $(@($Skipped).Count)  / degrade(403): $(@($Degraded).Count)  / 실패: $(@($Failed).Count)"
if (@($Succeeded).Count -gt 0) { Log "  성공: $($Succeeded -join ' ')" }
if (@($Skipped).Count -gt 0)   { Log "  skip: $($Skipped -join ' ')" }
if (@($Degraded).Count -gt 0)  { Log "  degrade(403 WARN — operator 권한 확보 후 재실행): $($Degraded -join ' ')" }
if (@($Failed).Count -gt 0)    { Log "  실패: $($Failed -join ' ')" }

if (@($Failed).Count -gt 0) {
    exit 1
}
exit 0
