# check-debut-readiness.ps1 — single-entry consumer setup verify (CFP-125 Phase 2, Windows variant).
#
# check-debut-readiness.sh 의 PowerShell 5.1+ wrapper. 동일 4 verification.
#
# Usage:
#   pwsh -File scripts/check-debut-readiness.ps1
#   pwsh -File scripts/check-debut-readiness.ps1 -Quiet
#   pwsh -File scripts/check-debut-readiness.ps1 -Strict
#
# Exit code:
#   Default mode: 0 (모두 PASS) / 0 (FAIL — stderr advisory 만)
#   Strict mode (CFP-127 후 활성): 0 / 1
#   현 release: -Strict 인식하나 default 동작 + stderr 경고

[CmdletBinding()]
param(
    [switch]$Quiet,
    [switch]$Strict
)

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PluginRoot = Split-Path -Parent $ScriptDir

if ($Strict) {
    [Console]::Error.WriteLine("[check-debut-readiness] WARN: -Strict mode 는 CFP-127 (ADR-032) 후 활성. 현재 release 는 default mode (exit 0 advisory) 만 작동.")
}

function Log([string]$msg) {
    if (-not $Quiet) { Write-Output $msg }
}

function LogErr([string]$msg) {
    [Console]::Error.WriteLine($msg)
}

$PassCount = 0
$FailCount = 0
$FailDetails = @()

# Check 1
function Check-1-Bootstrap {
    Log "Check 1/4: check_bootstrap.py (8 sub-check)"
    $checkScript = Join-Path $PluginRoot "overlay/hooks/check_bootstrap.py"
    if (-not (Test-Path $checkScript)) {
        $script:FailCount++
        $script:FailDetails += "Check 1: check_bootstrap.py 부재 (plugin 미설치 또는 PLUGIN_ROOT 잘못됨)"
        return
    }
    try {
        $out = python3 $checkScript 2>&1
        if ($LASTEXITCODE -ne 0) {
            $script:FailCount++
            $script:FailDetails += "Check 1: check_bootstrap.py exit non-zero"
            return
        }
        if ($out) {
            Log "  (advisory output:)"
            $out | ForEach-Object { LogErr "    $_" }
        }
        $script:PassCount++
    } catch {
        $script:FailCount++
        $script:FailDetails += "Check 1: python3 호출 실패 — $_"
    }
}

# Check 2
function Check-2-Plugins {
    Log "Check 2/4: plugin 10종 presence"
    $userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }
    $pluginsJson = Join-Path $userProfile ".claude/plugins/installed_plugins.json"
    # CFP-2250 / ADR-122 — superpowers 제거 (check_bootstrap.py REQUIRED_PLUGINS 정합, 11→10).
    $required = @(
        "codeforge@mclayer", "codeforge-requirements@mclayer", "codeforge-design@mclayer",
        "codeforge-develop@mclayer", "codeforge-test@mclayer", "codeforge-review@mclayer",
        "codeforge-pmo@mclayer", "github@claude-plugins-official", "codex@openai-codex",
        "claude-md-management@claude-plugins-official"
    )
    if (-not (Test-Path $pluginsJson)) {
        $script:FailCount++
        $script:FailDetails += "Check 2: $pluginsJson 부재 (Claude Code 미설치 또는 plugin 0개)"
        return
    }
    try {
        $data = Get-Content $pluginsJson -Raw | ConvertFrom-Json
        $installed = if ($data.plugins) { $data.plugins.PSObject.Properties.Name } else { @() }
        $missing = $required | Where-Object { $installed -notcontains $_ }
        if ($missing.Count -gt 0) {
            $script:FailCount++
            $script:FailDetails += "Check 2: $($missing.Count)/$($required.Count) plugin 미설치 — $($missing -join ' ')"
        } else {
            $script:PassCount++
            Log "  ✓ $($required.Count)/$($required.Count) plugin 설치 확인"
        }
    } catch {
        $script:FailCount++
        $script:FailDetails += "Check 2: plugins JSON parse 실패 — $_"
    }
}

# Check 3
function Check-3-ProjectYaml {
    Log "Check 3/4: project.yaml schema validation"
    $yaml = ".claude/_overlay/project.yaml"
    if (-not (Test-Path $yaml)) {
        $script:FailCount++
        $script:FailDetails += "Check 3: $yaml 부재 — 'pwsh -File scripts/bootstrap-consumer.ps1' 권장"
        return
    }
    $validator = Join-Path $PluginRoot "overlay/hooks/validate_config.py"
    if (-not (Test-Path $validator)) {
        $script:FailCount++
        $script:FailDetails += "Check 3: $validator 부재"
        return
    }
    python3 $validator $yaml *>$null
    if ($LASTEXITCODE -ne 0) {
        $script:FailCount++
        $script:FailDetails += "Check 3: project.yaml schema 위반 — 'python3 $validator $yaml' 직접 실행하여 상세 확인"
    } else {
        $script:PassCount++
        Log "  ✓ project.yaml schema PASS"
    }
}

# Check 4
function Check-4-SettingsHooks {
    Log "Check 4/4: settings.json 3 hook 등록 정합"
    $settings = ".claude/settings.json"
    if (-not (Test-Path $settings)) {
        $script:FailCount++
        $script:FailDetails += "Check 4: $settings 부재"
        return
    }
    $content = Get-Content $settings -Raw
    $missingHooks = @()
    if ($content -notmatch "regen-agents") { $missingHooks += "SessionStart:regen-agents" }
    if ($content -notmatch "check-bootstrap") { $missingHooks += "SessionStart:check-bootstrap" }
    if ($content -notmatch "userprompt-reminder") { $missingHooks += "UserPromptSubmit:userprompt-reminder" }
    if ($missingHooks.Count -gt 0) {
        $script:FailCount++
        $script:FailDetails += "Check 4: $($missingHooks.Count)/3 hook 미등록 — $($missingHooks -join ' ') (templates/settings.json.example 정합 갱신 의무)"
    } else {
        $script:PassCount++
        Log "  ✓ 3/3 hook 등록 확인 (regen-agents + check-bootstrap + userprompt-reminder)"
    }
}

# Main
Log "=== check-debut-readiness 시작 ==="
Check-1-Bootstrap
Check-2-Plugins
Check-3-ProjectYaml
Check-4-SettingsHooks

Log ""
Log "=== Summary: $PassCount/4 PASS, $FailCount/4 FAIL ==="
if ($FailCount -gt 0) {
    LogErr ""
    LogErr "FAIL 상세:"
    foreach ($d in $FailDetails) {
        LogErr "  - $d"
    }
    LogErr ""
    LogErr "Recovery: 'pwsh -File scripts/bootstrap-consumer.ps1' 또는 consumer-guide §2.1+ manual 절차 참조"
}

# Default exit 0 (advisory, ADR-027 §결정 2 LLM-trust 정합)
exit 0
