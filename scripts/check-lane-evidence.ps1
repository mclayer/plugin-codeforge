# check-lane-evidence.ps1 — Lane evidence cross-validate (CFP-126 / ADR-031 Phase 2, Windows variant).
#
# check-lane-evidence.sh 의 PowerShell 5.1+ thin wrapper.
#
# Usage:
#   pwsh -File scripts/check-lane-evidence.ps1 [-Story <path>] [-Pr <number>] [-Strict] [-Quiet]

[CmdletBinding()]
param(
    [string]$Story = "",
    [int]$Pr = 0,
    [switch]$Strict,
    [switch]$Quiet
)

$ErrorActionPreference = "Continue"

function Log([string]$msg) { if (-not $Quiet) { Write-Output $msg } }
function LogErr([string]$msg) { [Console]::Error.WriteLine($msg) }

# Auto-detect story path from branch
if (-not $Story) {
    $branch = git branch --show-current 2>$null
    if ($branch -and $branch -match '^([a-zA-Z]+)-(\d+)') {
        $key = "$($matches[1].ToUpper())-$($matches[2])"
        $candidate = "docs/stories/$key.md"
        if (Test-Path $candidate) {
            $Story = $candidate
        }
    }
}

# Auto-detect PR
if ($Pr -eq 0) {
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        try {
            $prNum = gh pr view --json number --jq '.number' 2>$null
            if ($prNum) { $Pr = [int]$prNum }
        } catch { }
    }
}

function Parse-StorySection14([string]$path) {
    if (-not (Test-Path $path)) { return "" }
    $content = Get-Content $path -Raw
    $in14 = $false; $inYaml = $false
    $result = @()
    foreach ($line in $content -split "`n") {
        if ($line -match '^#{2,4} §14') { $in14 = $true; continue }
        if ($in14 -and $line -match '^#{2,3} §[0-9]') { $in14 = $false }
        if ($in14 -and $line -match '^```yaml') { $inYaml = $true; continue }
        if ($in14 -and $inYaml -and $line -match '^```') { $inYaml = $false; continue }
        if ($in14 -and $inYaml) { $result += $line }
    }
    return ($result -join "`n")
}

function Fetch-PrLaneEvidence([int]$prNum) {
    if ($prNum -eq 0) { return "" }
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        LogErr "gh CLI 미설치 — PR description fetch 불가"
        return ""
    }
    try {
        $body = gh pr view $prNum --json body --jq '.body' 2>$null
        if (-not $body) { return "" }
        $inBlock = $false
        $result = @()
        foreach ($line in $body -split "`n") {
            if ($line -match '^## Lane evidence') { $inBlock = $true; continue }
            if ($inBlock -and $line -match '^## ') { $inBlock = $false }
            if ($inBlock) { $result += $line }
        }
        return ($result -join "`n")
    } catch { return "" }
}

# Run checks
$fail = 0

# Check 1: Story §14 presence
if (-not $Story -or -not (Test-Path $Story)) {
    LogErr "[FAIL] Story file path detect 실패 또는 file 부재 — -Story <path> 명시"
    $fail++
} else {
    Log "[OK] Story file: $Story"
}

# Check 2: §14 YAML block
$storyYaml = ""
if ($Story -and (Test-Path $Story)) {
    $storyYaml = Parse-StorySection14 $Story
    if (-not $storyYaml) {
        LogErr "[FAIL] Story §14 Lane Evidence YAML block 부재"
        $fail++
    } else {
        Log "[OK] Story §14 YAML block detected"
    }
}

# Check 3: PR description block
$prBlock = ""
if ($Pr -gt 0) {
    $prBlock = Fetch-PrLaneEvidence $Pr
    if (-not $prBlock) {
        LogErr "[FAIL] PR #$Pr 의 ## Lane evidence 블록 부재"
        $fail++
    } else {
        Log "[OK] PR #$Pr ## Lane evidence block detected"
    }
} else {
    Log "[SKIP] PR number unknown (-Pr 명시 또는 git branch 의 open PR 부재)"
}

# Check 4: Lane name set 일치
if ($storyYaml -and $prBlock) {
    $storyLanes = ($storyYaml -split "`n" | Where-Object { $_ -match '^\s*-\s*lane:' } | ForEach-Object { ($_ -replace '.*lane:\s*([^\s#]+).*', '$1') }) | Sort-Object -Unique
    $prLanes = ($prBlock -split "`n" | Where-Object { $_ -match '^- ' } | ForEach-Object { ($_ -replace '^-\s*([^:]+):.*', '$1').Trim() }) | Sort-Object -Unique
    $diff = Compare-Object -ReferenceObject $storyLanes -DifferenceObject $prLanes -PassThru
    if ($diff) {
        LogErr "[FAIL] Lane name set mismatch (Story §14 vs PR description):"
        $diff | ForEach-Object { LogErr "  $_" }
        $fail++
    } else {
        Log "[OK] Lane name set 일치"
    }
}

# Check 5: BYPASS reason
if ($storyYaml -match 'output_status:\s*bypass') {
    if ($prBlock -notmatch '(?i)BYPASS:') {
        LogErr "[FAIL] §14 에 bypass row 존재 — PR description 에 'BYPASS: <reason>' 명시 의무"
        $fail++
    } else {
        Log "[OK] BYPASS reason PR description 명시 확인"
    }
}

Log ""
Log "=== Summary: $fail FAIL ==="

if ($Strict -and $fail -gt 0) {
    exit 1
}
exit 0
