#Requires -Version 5.1
<#
.SYNOPSIS
    Codeforge external session auto-resume wrapper for Windows Task Scheduler.

.DESCRIPTION
    Monitors rate-limit reset time and automatically resumes the last Claude Code session
    once the rate limit window expires. Implements ADR-110 §결정 1-10.

.PARAMETER SessionUuidFile
    Path to file containing the last session UUID (default: $env:LOCALAPPDATA\codeforge\last-session.txt).

.PARAMETER MaxRetryCount
    Maximum retry attempts before showing user notification (default: 3).

.PARAMETER LogFile
    Path to log file for operation history (default: $env:LOCALAPPDATA\codeforge\resume.log).

.NOTES
    - Platform: Windows only (ADR-110 §결정 5)
    - Session UUID abstraction: reads from local file, not ~/.claude/projects directly (ADR-110 §결정 4)
    - Ghost session prevention via mutex Local\CodeforgeResumeWrapper (ADR-110 §결정 6)
    - Rate-limit detection: claude --print "noop" + anthropic-ratelimit-unified-5h-reset header (ADR-110 §결정 8)
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionUuidFile = "$env:LOCALAPPDATA\codeforge\last-session.txt",

    [Parameter(Mandatory=$false)]
    [int]$MaxRetryCount = 3,

    [Parameter(Mandatory=$false)]
    [string]$LogFile = "$env:LOCALAPPDATA\codeforge\resume.log"
)

# ADR-110 §결정 5: Polyglot platform adapter - explicit abort on non-Windows
if ($PSVersionTable.Platform -eq "Unix") {
    Write-Error "Linux/macOS 미지원. bash equivalent = Phase 2 sub-CFP carrier" -ErrorAction Stop
    exit 1
}

# Initialize codeforge directory with proper ACL (ADR-110 §결정 4, ADR-068 I-3)
$CodeforgeDir = "$env:LOCALAPPDATA\codeforge"
if (-not (Test-Path $CodeforgeDir)) {
    New-Item -ItemType Directory -Path $CodeforgeDir -Force | Out-Null
}

# Set ACL: user-only (ADR-110 §결정 4)
icacls "$CodeforgeDir" /inheritance:r /grant:r "$env:USERNAME`:F" | Out-Null 2>&1

# Ensure log file exists and can be written
if (-not (Test-Path $LogFile)) {
    New-Item -ItemType File -Path $LogFile -Force | Out-Null
}

# Log function with secret redaction (ADR-110 §결정 4)
function Write-Log {
    param([string]$Message)

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss+09:00"
    # Redact sk-ant-* tokens (ADR-110 §결정 4)
    $redacted = $Message -replace 'sk-ant-[a-zA-Z0-9_-]+', 'sk-ant-***'
    "$timestamp | $redacted" | Add-Content -Path $LogFile -Encoding UTF8

    # Rotate log: keep 90 days + 5MB size limit (ADR-110 §결정 9)
    if ((Get-Item $LogFile).Length -gt 5MB) {
        $archivePath = "$LogFile.$(Get-Date -Format 'yyyy-MM-dd')"
        Copy-Item $LogFile $archivePath -Force
        Clear-Content $LogFile
    }

    # Purge archived logs older than 90 days (ADR-110 §결정 9)
    Get-ChildItem "$LogFile.*" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } | Remove-Item -Force -ErrorAction SilentlyContinue
}

# Ghost session prevention mutex (ADR-110 §결정 6)
$mutexName = "Local\CodeforgeResumeWrapper"
$mutex = $null
$mutexAcquired = $false

try {
    $mutex = New-Object System.Threading.Mutex($false, $mutexName)
    $mutexAcquired = $mutex.WaitOne(5000)

    if (-not $mutexAcquired) {
        Write-Log "Mutex acquire timeout - another instance running. Exiting gracefully."
        exit 0
    }

    Write-Log "=== Codeforge session resume wrapper started ==="

    # ADR-110 §결정 4: Read session UUID from abstraction layer file
    if (-not (Test-Path $SessionUuidFile)) {
        Write-Log "Session UUID file not found: $SessionUuidFile"
        exit 0
    }

    $sessionUuid = (Get-Content $SessionUuidFile -Raw).Trim()
    if ([string]::IsNullOrEmpty($sessionUuid)) {
        Write-Log "Session UUID file is empty"
        exit 0
    }

    Write-Log "Read session UUID: $(($sessionUuid -replace '.$', '***'))"

    # ADR-110 §결정 8: Detect rate-limit reset time
    Write-Log "Checking rate-limit status via 'claude --print noop'..."

    $output = & claude --print "noop" 2>&1
    $resetEpochStr = $null

    # Parse anthropic-ratelimit-unified-5h-reset header from stderr/stdout
    if ($output -match 'anthropic-ratelimit-unified-5h-reset[:\s]+(\d+)') {
        $resetEpochStr = $matches[1]
    }

    if ([string]::IsNullOrEmpty($resetEpochStr)) {
        Write-Log "No rate-limit header detected - session may be available now"
        Write-Log "Attempting immediate resume..."

        & claude --resume $sessionUuid
        $resumeExitCode = $LASTEXITCODE
        Write-Log "Resume exit code: $resumeExitCode"
        exit $resumeExitCode
    }

    # Parse reset epoch
    [uint64]$resetEpoch = $resetEpochStr
    $resetTime = [DateTime]::UnixEpoch.AddSeconds($resetEpoch).ToLocalTime()
    $nowTime = Get-Date

    Write-Log "Rate-limit reset time: $($resetTime.ToString('yyyy-MM-ddTHH:mm:ss+09:00'))"
    Write-Log "Current time: $($nowTime.ToString('yyyy-MM-ddTHH:mm:ss+09:00'))"

    if ($resetTime -le $nowTime) {
        Write-Log "Reset time is in past - resuming session now"
        & claude --resume $sessionUuid
        $resumeExitCode = $LASTEXITCODE
        Write-Log "Resume exit code: $resumeExitCode"
        exit $resumeExitCode
    }

    # ADR-110 §결정 8: Update Task Scheduler trigger time
    $taskName = "codeforge-auto-resume"
    $newTriggerTime = $resetTime.ToString("HH:mm")

    Write-Log "Updating Task Scheduler trigger time to $newTriggerTime"
    $schtasksOutput = & schtasks /Change /TN $taskName /ST $newTriggerTime 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Log "Task Scheduler trigger updated successfully"
    } else {
        Write-Log "WARNING: Failed to update Task Scheduler trigger. Output: $schtasksOutput"
    }

    Write-Log "Rate-limit window active. Next trigger: $newTriggerTime KST"
    Write-Log "=== Session resume wrapper completed ==="
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log "Stack: $($_.ScriptStackTrace)"

    # Handle retry counter and fallback (ADR-110 §결정 9)
    $retryCountFile = "$CodeforgeDir\retry-count.txt"
    $retryCount = 0

    if (Test-Path $retryCountFile) {
        [int]::TryParse((Get-Content $retryCountFile -Raw).Trim(), [ref]$retryCount) | Out-Null
    }

    $retryCount++
    $retryCount | Set-Content -Path $retryCountFile -NoNewline

    Write-Log "Retry count: $retryCount / $MaxRetryCount"

    if ($retryCount -ge $MaxRetryCount) {
        Write-Log "Max retries exceeded. Sending Windows Toast notification..."

        # Show Windows Toast notification (ADR-110 §결정 9)
        try {
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = @"
<toast>
  <visual>
    <binding template="ToastText02">
      <text id="1">Codeforge Session Resume</text>
      <text id="2">Auto-resume failed after $MaxRetryCount attempts. Please manually resume your session.</text>
    </binding>
  </visual>
</toast>
"@
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("codeforge").Show($toast)
        }
        catch {
            Write-Log "Toast notification failed: $($_.Exception.Message)"
        }

        # Reset retry counter
        0 | Set-Content -Path $retryCountFile -NoNewline
    }

    exit 1
}
finally {
    # Release mutex
    if ($mutexAcquired -and $null -ne $mutex) {
        $mutex.ReleaseMutex()
        $mutex.Dispose()
    }
}
