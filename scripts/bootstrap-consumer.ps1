# bootstrap-consumer.ps1 — single-entry consumer setup (CFP-125 Phase 2, Windows variant).
#
# bootstrap-consumer.sh 의 PowerShell 5.1+ wrapper. 동일 8 단계 idempotent setup.
# CFP-103 cross-platform 의무 정합.
#
# Usage:
#   pwsh -File scripts/bootstrap-consumer.ps1
#   pwsh -File scripts/bootstrap-consumer.ps1 -Org <org> -Repo <repo>
#   pwsh -File scripts/bootstrap-consumer.ps1 -DryRun
#   pwsh -File scripts/bootstrap-consumer.ps1 -Force
#   pwsh -File scripts/bootstrap-consumer.ps1 -Reset
#   pwsh -File scripts/bootstrap-consumer.ps1 -FamilySkip
#
# Exit code: 0 (모두 처리 또는 already-done) / 1 (fatal — gh 미인증, git repo 부재)

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Reset,
    [switch]$FamilySkip,
    [string]$Org = "",
    [string]$Repo = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
# F-CR-005: env override seam (test fixture 격리 지원 — PLUGIN_ROOT 주면 override, 없으면 기본값)
$PluginRoot = if ($env:PLUGIN_ROOT) { $env:PLUGIN_ROOT } else { Split-Path -Parent $ScriptDir }
$StateDir = ".claude/_overlay"
$StateFile = "$StateDir/.bootstrap-state.json"

function Log([string]$msg) {
    [Console]::Error.WriteLine("[bootstrap-consumer] $msg")
}

function Run-OrDry([scriptblock]$action, [string]$desc) {
    if ($DryRun) {
        [Console]::Error.WriteLine("[dry-run] $desc")
    } else {
        & $action
    }
}

function Mark-Step([string]$step) {
    if ($DryRun) { return }
    if (-not (Test-Path $StateDir)) {
        New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
    }
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    if (Test-Path $StateFile) {
        $state = Get-Content $StateFile -Raw | ConvertFrom-Json
        if (-not $state.steps) { $state | Add-Member -NotePropertyName steps -NotePropertyValue ([PSCustomObject]@{}) }
        $state.steps | Add-Member -NotePropertyName $step -NotePropertyValue $ts -Force
    } else {
        $state = [PSCustomObject]@{ version = "1"; steps = [PSCustomObject]@{ $step = $ts } }
    }
    $state | ConvertTo-Json -Depth 10 | Set-Content -Path $StateFile -Encoding utf8
}

function Is-StepDone([string]$step) {
    if ($Force) { return $false }
    if (-not (Test-Path $StateFile)) { return $false }
    $state = Get-Content $StateFile -Raw | ConvertFrom-Json
    if (-not $state.steps) { return $false }
    return ($null -ne $state.steps.$step)
}

# Reset
if ($Reset) {
    if (Test-Path $StateFile) {
        if (-not $DryRun) {
            $confirm = Read-Host "경고: -Reset 가 .bootstrap-state.json 삭제 + 모든 단계 재시도. 계속 (y/N)?"
            if ($confirm -ne "y" -and $confirm -ne "Y") {
                Log "사용자 취소"
                exit 0
            }
            Remove-Item -Path $StateFile -Force
            Log "state file 삭제됨"
        } else {
            Log "(dry-run) state file 삭제 skip"
        }
    }
}

# org/repo 자동 감지
function Detect-OrgRepo {
    if ($Org -and $Repo) { return }
    if (Test-Path ".claude/_overlay/project.yaml") {
        $yaml = Get-Content ".claude/_overlay/project.yaml" -Raw
        if ($yaml -match '(?m)^\s*org:\s*([^\s#"'']+)') { if (-not $script:Org) { $script:Org = $matches[1] } }
        if ($yaml -match '(?m)^\s*repo:\s*([^\s#"'']+)') { if (-not $script:Repo) { $script:Repo = $matches[1] } }
    }
    if (-not $script:Org -or -not $script:Repo) {
        try {
            $remote = git remote get-url origin 2>$null
            if ($remote -and $remote -match 'github\.com[:/]([^/]+)/([^./]+?)(\.git)?$') {
                if (-not $script:Org) { $script:Org = $matches[1] }
                if (-not $script:Repo) { $script:Repo = $matches[2] }
            }
        } catch { }
    }
}

# Stage 1
function Stage-1-Precheck {
    Log "Stage 1: pre-check (gh + git)"
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Log "ERROR: gh CLI 미설치 — https://cli.github.com 에서 설치 후 'gh auth login' 실행"
        return $false
    }
    if (-not $DryRun) {
        gh auth status *>$null
        if ($LASTEXITCODE -ne 0) {
            Log "ERROR: gh auth status 실패 — 'gh auth login' 실행"
            return $false
        }
    }
    git rev-parse --is-inside-work-tree *>$null
    if ($LASTEXITCODE -ne 0) {
        Log "ERROR: 현재 디렉터리가 git repo 아님"
        return $false
    }
    Detect-OrgRepo
    if (-not $script:Org -or -not $script:Repo) {
        Log "ERROR: org/repo 감지 실패 — -Org <org> -Repo <repo> 명시"
        return $false
    }
    Log "  org=$script:Org repo=$script:Repo"
    # CFP-2250 결함3 preflight: manifest / project.yaml 결손 사전 안내 (story-init 발동 전 진단).
    # project.yaml 부재 = Stage 3 에서 자동 scaffold. manifest 부재 = Stage 7 skip. story-init 은 별 lane(S4).
    if (-not (Test-Path ".claude/_overlay/project.yaml")) {
        Log "  preflight: project.yaml 부재 — Stage 3 에서 example 로 자동 scaffold (이후 org/repo 직접 치환 의무)"
    }
    if (-not (Test-Path (Join-Path $PluginRoot "templates/consumer-scripts.manifest"))) {
        Log "  preflight: consumer-scripts.manifest 부재 — Stage 7 skip (wrapper plugin 설치 확인 권장)"
    }
    Mark-Step "stage_1_precheck"
    return $true
}

# Stage 2
function Stage-2-PluginReminder {
    Log "Stage 2: plugin install reminder"
    $userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }
    $pluginsJson = Join-Path $userProfile ".claude/plugins/installed_plugins.json"
    # CFP-2250 / ADR-122 — superpowers 더 이상 codeforge 의존 아님 (check_bootstrap.py REQUIRED_PLUGINS 정합, 11→10).
    $required = @(
        "codeforge@mclayer", "codeforge-requirements@mclayer", "codeforge-design@mclayer",
        "codeforge-develop@mclayer", "codeforge-test@mclayer", "codeforge-review@mclayer",
        "codeforge-pmo@mclayer", "github@claude-plugins-official", "codex@openai-codex",
        "claude-md-management@claude-plugins-official"
    )
    $missing = @()
    if (Test-Path $pluginsJson) {
        try {
            $data = Get-Content $pluginsJson -Raw | ConvertFrom-Json
            $installed = @()
            if ($data.plugins) {
                $installed = $data.plugins.PSObject.Properties.Name
            }
            foreach ($p in $required) {
                if ($installed -notcontains $p) { $missing += $p }
            }
        } catch {
            $missing = $required
        }
    } else {
        Log "  (plugins JSON 부재 — Claude Code 미설치 또는 plugin 0개)"
        $missing = $required
    }
    if ($missing.Count -gt 0) {
        Log "  $($missing.Count)/$($required.Count) plugin 미설치:"
        foreach ($p in $missing) { Log "    /plugins install $p" }
        Log "  → Claude Code 에서 위 명령 직접 실행 의무 (platform-level)"
    } else {
        Log "  ✓ $($required.Count)/$($required.Count) plugin 설치 확인"
    }
    Mark-Step "stage_2_plugin_reminder"
    return $true
}

# Stage 3
function Stage-3-OverlayScaffold {
    Log "Stage 3: overlay scaffold"
    Run-OrDry { New-Item -ItemType Directory -Path ".claude/_overlay/agents" -Force | Out-Null } "mkdir .claude/_overlay/agents"
    $files = @(
        @{src = "overlay/_overlay/README.md"; dst = ".claude/_overlay/README.md"},
        @{src = "overlay/_overlay/project.yaml.example"; dst = ".claude/_overlay/project.yaml"},
        @{src = "overlay/_overlay/run-tests.sh.example"; dst = ".claude/_overlay/run-tests.sh"},
        @{src = "overlay/_overlay/run-perf.sh.example"; dst = ".claude/_overlay/run-perf.sh"}
    )
    foreach ($e in $files) {
        if (-not (Test-Path $e.dst)) {
            Run-OrDry { Copy-Item -Path (Join-Path $PluginRoot $e.src) -Destination $e.dst } "cp $($e.dst)"
            Log "  cp $($e.dst)"
        } else {
            Log "  skip $($e.dst) (already exists)"
        }
    }
    Mark-Step "stage_3_overlay_scaffold"
    return $true
}

# Stage 4
function Stage-4-SettingsJson {
    Log "Stage 4: settings.json bootstrap"
    $target = ".claude/settings.json"
    $source = Join-Path $PluginRoot "templates/settings.json.example"
    if (Test-Path $target) {
        $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        $backup = "$target.bak.$ts"
        Log "  WARN: $target 이미 존재 — 백업 후 skip ($backup)"
        if (-not $DryRun) {
            Copy-Item -Path $target -Destination $backup
        }
    } else {
        Run-OrDry { Copy-Item -Path $source -Destination $target } "cp $target"
        Log "  cp $target"
    }
    Mark-Step "stage_4_settings_json"
    return $true
}

# Stage 5
function Stage-5-GithubSetup {
    Log "Stage 5: GitHub workflows / forms / CODEOWNERS / PR template"
    Run-OrDry { New-Item -ItemType Directory -Path ".github/workflows", ".github/ISSUE_TEMPLATE" -Force | Out-Null } "mkdir .github/{workflows,ISSUE_TEMPLATE}"
    $whitelist = Join-Path $PluginRoot "templates/scripts/consumer_applicable_workflows.txt"
    $fallbackWorkflows = @(
        "phase-gate-mergeable.yml", "phase-label-invariant.yml", "story-init.yml",
        "story-section-1-immutable.yml", "subissue-from-impl-manifest.yml",
        "fix-ledger-sync.yml", "story-section-schema.yml"
    )
    $workflows = @()
    if (Test-Path $whitelist) {
        try {
            # FIX-CR-004/006: try/catch 로 unreadable whitelist 를 degrade 경로로 라우팅 + UTF-8 명시 (F-CR-004/006)
            $workflows = @(Get-Content $whitelist -Encoding utf8 -ErrorAction Stop |
                Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' } |
                ForEach-Object { $_.Trim() })    # CRLF/trailing-whitespace 정규화 (.sh .Trim() 동형)
        } catch {
            # AC-4 fail-safe degrade — read-fail (권한/인코딩 등) + WARN + non-abort (.sh 동형)
            Log "  [WARN] whitelist read-fail ($whitelist): $($_.Exception.Message) — 고정 7종 fallback 으로 degrade (CFP-2439 §3.3, .sh parity)"
            $workflows = @()   # 아래 empty-check 가 7종 fallback 라우팅
        }
    }
    # F-CR-001: whitelist 부재/read-fail/parse 0종 → degrade (0종 fail-closed 금지, §3.3, ADR-116)
    if ($null -eq $workflows -or @($workflows).Count -eq 0) {
        Log "  [WARN] whitelist 부재/read-fail/parse 0종 — 고정 7종 fallback 으로 degrade (CFP-2439 §3.3, ADR-116 never-reduce: 0종 미배포 차단)"
        $workflows = $fallbackWorkflows
    }
    foreach ($w in $workflows) {
        $src = Join-Path $PluginRoot "templates/github-workflows/$w"
        $dst = ".github/workflows/$w"
        if (-not (Test-Path $src)) { Log "  [WARN] whitelist source 부재 — skip: $w"; continue }
        if (-not (Test-Path $dst)) {            # idempotent guard 보존 (ADR-116)
            Run-OrDry { Copy-Item -Path $src -Destination $dst } "cp $dst"
            Log "  cp $dst"
        }
    }
    $forms = @("audit.yml", "bug.yml", "story.yml")
    foreach ($f in $forms) {
        $dst = ".github/ISSUE_TEMPLATE/$f"
        if (-not (Test-Path $dst)) {
            Run-OrDry { Copy-Item -Path (Join-Path $PluginRoot "templates/github-issue-forms/$f") -Destination $dst } "cp $dst"
            Log "  cp $dst"
        }
    }
    if (-not (Test-Path ".github/ISSUE_TEMPLATE/config.yml")) {
        if (-not $DryRun) {
            "blank_issues_enabled: false" | Set-Content -Path ".github/ISSUE_TEMPLATE/config.yml" -Encoding utf8
        }
        Log "  cp .github/ISSUE_TEMPLATE/config.yml"
    }
    if (-not (Test-Path ".github/CODEOWNERS")) {
        Run-OrDry { Copy-Item -Path (Join-Path $PluginRoot "templates/CODEOWNERS.template") -Destination ".github/CODEOWNERS" } "cp .github/CODEOWNERS"
        Log "  cp .github/CODEOWNERS (placeholder team — 직접 치환 의무)"
    }
    if (-not (Test-Path ".github/PULL_REQUEST_TEMPLATE.md")) {
        Run-OrDry { Copy-Item -Path (Join-Path $PluginRoot "templates/github-pr-template.md") -Destination ".github/PULL_REQUEST_TEMPLATE.md" } "cp .github/PULL_REQUEST_TEMPLATE.md"
        Log "  cp .github/PULL_REQUEST_TEMPLATE.md"
    }
    Mark-Step "stage_5_github_setup"
    return $true
}

# Stage 6 — CFP-2250 결함1: 3-tier fallback (bash → PowerShell-native → ERROR). silent skip 제거.
function Stage-6-Labels {
    Log "Stage 6: labels bootstrap"
    $bootstrapLabelsSh = Join-Path $PluginRoot "scripts/bootstrap-labels.sh"
    $bootstrapLabelsPs1 = Join-Path $PluginRoot "scripts/bootstrap-labels.ps1"
    $bashCmd = Get-Command bash -ErrorAction SilentlyContinue
    if ($DryRun) {
        $bashPresent = [bool]$bashCmd
        Log "  (dry-run) label seed (bash present=$bashPresent → $(if ($bashPresent) {'bootstrap-labels.sh'} else {'bootstrap-labels.ps1 native fallback'}))"
        Mark-Step "stage_6_labels"
        return $true
    }
    if ($bashCmd) {
        # tier 1: bash (POSIX 경로 — WSL/Git Bash 검증된 경로, 회귀 0)
        # CFP-2250 FIX (Codex P1): 파이프(| ForEach-Object) 제거 — $LASTEXITCODE 가 bash native exit 를
        # 확실히 보존하도록 출력 캡처 후 검사 (이전: exit 미검사 → 실패를 성공으로 삼킴).
        $labelsOut = & bash $bootstrapLabelsSh "$script:Org/$script:Repo" 2>&1
        $labelsRc = $LASTEXITCODE
        foreach ($l in $labelsOut) { Log "  $l" }
        if ($labelsRc -ne 0) {
            Log "  ERROR: bash label 시드 실패 (bootstrap-labels.sh exit $labelsRc)"
            return $false
        }
    } elseif (Test-Path $bootstrapLabelsPs1) {
        # tier 2: PowerShell-native fallback (결함1 해소 핵심 — bash 부재 네이티브 Windows)
        Log "  bash 미발견 — PowerShell-native label 시드 (bootstrap-labels.ps1)"
        $labelsOut = & $bootstrapLabelsPs1 -Repo "$script:Org/$script:Repo" 2>&1
        $labelsRc = $LASTEXITCODE
        foreach ($l in $labelsOut) { Log "  $l" }
        if ($labelsRc -ne 0) {
            Log "  ERROR: PowerShell label 시드 실패 (exit $labelsRc)"
            return $false
        }
    } else {
        # tier 3: bash + .ps1 모두 부재 (이론상) — silent skip 금지, 명시적 ERROR
        Log "  ERROR: bash + bootstrap-labels.ps1 모두 부재 — label 시드 불가 (plugin 설치 확인)"
        return $false
    }
    Mark-Step "stage_6_labels"
    return $true
}

# Stage 7
function Stage-7-ConsumerScripts {
    Log "Stage 7: consumer-scripts.manifest copy"
    $manifest = Join-Path $PluginRoot "templates/consumer-scripts.manifest"
    if (-not (Test-Path $manifest)) {
        Log "  WARN: manifest 부재 — skip"
        Mark-Step "stage_7_consumer_scripts"
        return $true
    }
    Get-Content $manifest | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $scriptPath = ($line -split ":")[0]
        if ($scriptPath -match '^/' -or $scriptPath -match '\.\.' -or $scriptPath -match '^-') {
            Log "  reject: $line"
            return
        }
        if (-not (Test-Path $scriptPath)) {
            $dir = Split-Path -Parent $scriptPath
            if ($dir) {
                Run-OrDry { New-Item -ItemType Directory -Path $dir -Force | Out-Null } "mkdir $dir"
            }
            Run-OrDry { Copy-Item -Path (Join-Path $PluginRoot $scriptPath) -Destination $scriptPath } "cp $scriptPath"
            Log "  cp $scriptPath"
        }
    }
    Mark-Step "stage_7_consumer_scripts"
    return $true
}

# Stage 8
function Stage-8-Summary {
    Log ""
    Log "=== bootstrap-consumer 완료 ==="
    Log "  org=$script:Org repo=$script:Repo"
    Log ""
    Log "Next step: pwsh -File scripts/check-debut-readiness.ps1"
    Log ""
    if (Test-Path $StateFile) {
        Log "State marker: $StateFile"
    }
}

# Main
$stages = @(
    @{name = "stage_1_precheck"; fn = { Stage-1-Precheck }},
    @{name = "stage_2_plugin_reminder"; fn = { Stage-2-PluginReminder }},
    @{name = "stage_3_overlay_scaffold"; fn = { Stage-3-OverlayScaffold }},
    @{name = "stage_4_settings_json"; fn = { Stage-4-SettingsJson }},
    @{name = "stage_5_github_setup"; fn = { Stage-5-GithubSetup }},
    @{name = "stage_6_labels"; fn = { Stage-6-Labels }},
    @{name = "stage_7_consumer_scripts"; fn = { Stage-7-ConsumerScripts }}
)
if ($FamilySkip) {
    Log "(--FamilySkip set — Stage 6 labels skip)"
}
$rc = 0
foreach ($s in $stages) {
    if (Is-StepDone $s.name) {
        Log "$($s.name): SKIP (marker exists, -Force 로 재시도 가능)"
        continue
    }
    if ($s.name -eq "stage_6_labels" -and $FamilySkip) {
        Log "$($s.name): SKIP (-FamilySkip)"
        continue
    }
    if (-not (& $s.fn)) {
        Log "ERROR: $($s.name) failed"
        $rc = 1
        break
    }
}
Stage-8-Summary
exit $rc
