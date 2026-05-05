# userprompt-reminder.ps1 — UserPromptSubmit hook (Windows wrapper).
#
# CFP-104 (Phase 2b of CFP-96 Epic) — Python core thin wrapper.
# Implementation SSOT: userprompt_reminder.py (cross-platform).
#
# Stdin pass-through 의무: Claude Code 가 prompt JSON 을 stdin 으로 전달 →
# Python 이 sys.stdin.read() 로 읽음. PowerShell 의 자동 변수 $input 사용.

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
$pythonCore = Join-Path $scriptDir "userprompt_reminder.py"

if (-not (Test-Path $pythonCore)) {
    exit 0
}

# stdin pass-through (변경 prompt JSON / raw text).
$input | & $pythonCmd $pythonCore
exit 0
