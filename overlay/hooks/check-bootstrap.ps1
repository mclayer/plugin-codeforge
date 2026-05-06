# check-bootstrap.ps1 — Consumer 환경 부트스트랩 정합 진단 (default non-blocking, Windows).
#
# CFP-103 (Phase 2a of CFP-96 Epic) — Python core thin wrapper.
# CFP-127 (Phase 2 of CFP-124 Epic) — strict mode opt-in flag passthrough.
# Implementation SSOT: check_bootstrap.py (cross-platform).
#
# Usage:
#   pwsh -File check-bootstrap.ps1                # default (non-blocking exit 0)
#   pwsh -File check-bootstrap.ps1 -Strict        # CFP-127 ADR-032 strict mode opt-in
#   pwsh -File check-bootstrap.ps1 -Quiet         # suppress warnings
#
# Exit code passthrough from Python core:
#   Default mode: 0
#   Strict mode + strict-eligible drift: 1 (CFP-127 / ADR-032)

[CmdletBinding()]
param(
    [switch]$Strict,
    [switch]$Quiet
)

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

# CFP-127 — pass through flags to Python core.
$pythonArgs = @($pythonCore)
if ($Strict) { $pythonArgs += "--strict" }
if ($Quiet) { $pythonArgs += "--quiet" }

& $pythonCmd @pythonArgs
exit $LASTEXITCODE
