# check-bootstrap.ps1 — Consumer 환경 부트스트랩 정합 진단 (non-blocking, Windows).
#
# CFP-103 (Phase 2a of CFP-96 Epic) — Python core thin wrapper.
# Implementation SSOT: check_bootstrap.py (cross-platform).

$ErrorActionPreference = "SilentlyContinue"

# Python 3 검출 — Windows 에서는 'python' / 'py' / 'python3'.
$pythonCmd = $null
foreach ($cmd in @("python3", "python", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    exit 0
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonCore = Join-Path $scriptDir "check_bootstrap.py"

if (-not (Test-Path $pythonCore)) {
    exit 0
}

& $pythonCmd $pythonCore
exit 0
