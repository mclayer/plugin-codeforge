# bootstrap-labels.ps1 — bootstrap-labels.sh 의 PowerShell-native parity wrapper (CFP-2250 / ADR-027 Amendment 11).
#
# Windows-native (Git Bash / WSL 부재) 환경에서 GitHub label 부트스트랩 — bash 의존 0.
# base label = templates/labels/base-labels.tsv (.sh 와 공유 SSOT — drift 구조적 차단).
# hotfix-bypass:* / component:* = python 공통 호출 (.sh 와 동일 경로).
#
# 멱등 — 기존 label 은 "already exists" 후 통과 (create 실패 → edit → 진짜 실패 시 stderr verbatim).
# 보안 — gh 호출은 배열 인자 (& gh label create $name --color $color ...) 로 자동 quoting (injection 차단).
#         Invoke-Expression / iex 사용 금지. label 데이터는 wrapper SSOT (TSV/registry) — 신뢰 경계 안.
#
# Usage:
#   pwsh -File scripts/bootstrap-labels.ps1                  # 현재 repo (gh 기본 컨텍스트)
#   pwsh -File scripts/bootstrap-labels.ps1 -Repo org/repo   # 명시 repo
#   pwsh -File scripts/bootstrap-labels.ps1 -DryRun          # 라벨 목록만 stdout (gh 미호출, count self-check)
#
# Exit code: 0 (모두 처리, already-exists 포함) / 1 (gh 미설치 / 인증 실패 / TSV 부재)
#
# PowerShell 5.1+ floor (Windows 기본). CI = windows-latest pwsh (PowerShell 7).

[CmdletBinding()]
param(
    [string]$Repo = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# UTF-8 출력 강제 (한글 description + tab-separated dry-run stdout 정합 — .sh dry-run 출력 parity).
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
} catch { }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PluginRoot = Split-Path -Parent $ScriptDir

# -Repo 인자 → gh 배열 인자 (문자열 보간 명령 조립 금지 — injection 차단)
$RepoArg = @()
if ($Repo) { $RepoArg = @("--repo", $Repo) }

# CFP-492 2-way self-check 카운터 (.sh LABEL_COUNT parity)
$script:LabelCount = 0

# gh preflight (실모드만 — DryRun 은 gh 미호출)
if (-not $DryRun) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        [Console]::Error.WriteLine("ERROR: gh CLI 미설치. https://cli.github.com 에서 설치 후 'gh auth login' 실행.")
        exit 1
    }
}

# Idempotent label create — 이미 존재하면 edit 으로 멱등 (.sh create_label 미러).
# DryRun: gh 미호출, "name`tcolor`tdesc" stdout (CFP-33 check-label-registry parse 포맷 동일).
function New-Label {
    param([string]$Name, [string]$Color, [string]$Desc)
    $script:LabelCount++
    if ($DryRun) {
        # tab-separated (3 field) — .sh --dry-run 출력과 byte-parity
        [Console]::Out.WriteLine("$Name`t$Color`t$Desc")
        return
    }
    # 배열 인자 전달 = 자동 quoting (injection 차단). 문자열 보간 명령 조립 금지.
    $createErr = & gh label create $Name --color $Color --description $Desc @RepoArg 2>&1
    if ($LASTEXITCODE -eq 0) { return }
    # create 실패 → edit 시도 (already-exists 멱등 경로)
    $editErr = & gh label edit $Name --color $Color --description $Desc @RepoArg 2>&1
    if ($LASTEXITCODE -eq 0) { return }
    # create AND edit 모두 실패 = 진짜 실패 (권한/네트워크/API) — stderr verbatim (masked false-success 차단)
    $ghErr = if ($editErr) { "$editErr" } else { "$createErr" }
    $ghErr = ($ghErr -replace '\r?\n', ' ' -replace '\s+', ' ').Trim()
    if (-not $ghErr) { $ghErr = "(gh stderr 비어있음 — 권한/네트워크 점검)" }
    [Console]::Error.WriteLine("  ! $Name`: create/edit 실패 — $ghErr")
}

if (-not $DryRun) {
    [Console]::Error.WriteLine("Plugin label 부트스트랩...")
}

# ---- base label (templates/labels/base-labels.tsv, .sh 공유 SSOT) ----
$BaseTsv = if ($env:BASE_LABELS_TSV) { $env:BASE_LABELS_TSV } else { Join-Path $PluginRoot "templates/labels/base-labels.tsv" }
if (-not (Test-Path $BaseTsv)) {
    [Console]::Error.WriteLine("ERROR: base label TSV 부재 — $BaseTsv")
    exit 1
}
# 줄 단위 read (Import-Csv 대신 — embedded tab/특수문자/한글 desc 안전, .sh IFS read parity).
# UTF-8 명시 read (PowerShell 5.1 기본 인코딩이 BOM/ANSI 일 수 있어 명시 의무).
$tsvLines = Get-Content -LiteralPath $BaseTsv -Encoding UTF8
foreach ($line in $tsvLines) {
    # 빈 줄 / # 주석 줄 skip (.sh case '#'*|'' continue)
    if (-not $line) { continue }
    if ($line.TrimStart().StartsWith("#")) { continue }
    $parts = $line -split "`t", 3
    if ($parts.Count -ne 3) { continue }
    New-Label -Name $parts[0] -Color $parts[1] -Desc $parts[2]
}

# ---- hotfix-bypass:* dynamic (label-registry-v2.md §3 yaml, python 공통 — .sh 미러) ----
# canonical-only category — DryRun + 실모드 양쪽 모두 처리 (.sh 와 동일).
$RegistryMd = if ($env:REGISTRY_MD) { $env:REGISTRY_MD } else { Join-Path $PluginRoot "docs/inter-plugin-contracts/label-registry-v2.md" }
$ParseScript = Join-Path $ScriptDir "parse-hotfix-bypass-labels.py"
if ((Test-Path $RegistryMd) -and (Test-Path $ParseScript)) {
    $pyOk = $true
    try { & python -c "import yaml" 2>$null; if ($LASTEXITCODE -ne 0) { $pyOk = $false } }
    catch { $pyOk = $false }
    if (-not $pyOk) {
        [Console]::Error.WriteLine("  ! hotfix-bypass:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장).")
    } else {
        $hotfixOut = & python $ParseScript $RegistryMd 2>$null
        $rc = $LASTEXITCODE
        if ($rc -eq 2) {
            [Console]::Error.WriteLine("  ! hotfix-bypass:* SKIPPED — registry 안 0 entry (drift sentinel).")
        } elseif ($rc -ne 0) {
            [Console]::Error.WriteLine("  ! hotfix-bypass:* SKIPPED — parse failure (exit $rc).")
        } else {
            foreach ($hl in $hotfixOut) {
                if (-not $hl) { continue }
                $hp = $hl -split "`t", 3
                if ($hp.Count -ne 3) { continue }
                if (-not $hp[0]) { continue }
                New-Label -Name $hp[0] -Color $hp[1] -Desc $hp[2]
            }
        }
    }
}

# ---- component:* dynamic (project.yaml labels.components[], 실모드만 — .sh 미러) ----
# --dry-run 모드 skip (component:* 는 consumer overlay 동적 — check-label-registry strict sync 충돌 회피).
$ProjectYaml = if ($env:PROJECT_YAML) { $env:PROJECT_YAML } else { ".claude/_overlay/project.yaml" }
if ((-not $DryRun) -and (Test-Path $ProjectYaml)) {
    $pyOk = $true
    try { & python -c "import yaml" 2>$null; if ($LASTEXITCODE -ne 0) { $pyOk = $false } }
    catch { $pyOk = $false }
    if (-not $pyOk) {
        [Console]::Error.WriteLine("  ! component:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장).")
    } else {
        # path 를 argv 로 안전 전달 (.sh 와 동일 inline python, shell quoting 회피)
        $pyComponent = @"
import sys, yaml
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        d = yaml.safe_load(f) or {}
    for c in (d.get('labels', {}) or {}).get('components', []) or []:
        if isinstance(c, str) and not c.startswith('<REPLACE'):
            print(c)
except Exception as e:
    print(f'PARSE_ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"@
        $components = & python -c $pyComponent $ProjectYaml 2>$null
        if ($LASTEXITCODE -eq 0 -and $components) {
            foreach ($c in $components) {
                if (-not $c) { continue }
                New-Label -Name "component:$c" -Color "ededed" -Desc "Component: $c"
            }
        }
    }
}

if (-not $DryRun) {
    [Console]::Error.WriteLine("")
    $baseCount = ($tsvLines | Where-Object { $_ -and (-not $_.TrimStart().StartsWith("#")) }).Count
    [Console]::Error.WriteLine("✓ $baseCount base label (templates/labels/base-labels.tsv) + hotfix-bypass:* (registry 동적) + component:* (project.yaml.labels.components[] 동적) 처리 완료. 'gh label list' 로 확인.")
}

# CFP-492 2-way self-check (DryRun 모드만) — .sh stderr 포맷 parity
if ($DryRun) {
    [Console]::Error.WriteLine("[bootstrap-labels self-check] create_label invocations: $($script:LabelCount)")
}

exit 0
