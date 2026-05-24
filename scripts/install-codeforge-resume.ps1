#Requires -Version 5.1 -RunAsAdministrator
<#
.SYNOPSIS
    Install codeforge external session auto-resume wrapper (Windows Task Scheduler).

.DESCRIPTION
    Copies wrapper script and registers Windows Task Scheduler job.
    Idempotent: updates existing task if present.

.PARAMETER ScriptSourceDir
    Source directory containing codeforge-session-resume.ps1 and templates
    (default: script parent directory).

.NOTES
    - Requires Administrator privileges
    - Platform: Windows only
    - Idempotent: safe to run multiple times
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ScriptSourceDir = (Split-Path -Parent $MyInvocation.MyCommand.Path)
)

# ADR-110 §결정 5: Polyglot platform adapter
if ($PSVersionTable.Platform -eq "Unix") {
    Write-Error "Linux/macOS 미지원. bash equivalent = Phase 2 sub-CFP carrier" -ErrorAction Stop
    exit 1
}

# Verify running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script requires Administrator privileges. Please run as Administrator."
    exit 1
}

Write-Host "=== Codeforge Session Resume Installer ===" -ForegroundColor Cyan

# Source files
$wrapperScript = Join-Path $ScriptSourceDir "codeforge-session-resume.ps1"
$xmlTemplate = Join-Path $ScriptSourceDir "..\templates\scheduler\codeforge-auto-resume.xml"

if (-not (Test-Path $wrapperScript)) {
    Write-Error "Wrapper script not found: $wrapperScript"
    exit 1
}

if (-not (Test-Path $xmlTemplate)) {
    Write-Error "XML template not found: $xmlTemplate"
    exit 1
}

# Install destination
$installDir = "$env:ProgramFiles\codeforge"
$installScript = Join-Path $installDir "codeforge-session-resume.ps1"

# Create install directory if needed
if (-not (Test-Path $installDir)) {
    Write-Host "Creating directory: $installDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# Copy wrapper script
Write-Host "Copying wrapper script..." -ForegroundColor Yellow
Copy-Item $wrapperScript $installScript -Force
Write-Host "  Installed to: $installScript" -ForegroundColor Green

# Set ACL on install directory (ADR-110 §결정 2)
Write-Host "Setting ACL on $installDir..." -ForegroundColor Yellow
icacls $installDir /inheritance:r /grant:r "$env:USERNAME`:F" /grant:r "Administrators:F" | Out-Null
Write-Host "  ACL set for user and Administrators" -ForegroundColor Green

# Read and update XML template path
# SecurityTest P1 #1 FIX (CWE-611 XXE prevention) — XmlReaderSettings explicit DTD/Entity prohibit
Write-Host "Preparing Task Scheduler definition..." -ForegroundColor Yellow
$xmlReaderSettings = New-Object System.Xml.XmlReaderSettings
$xmlReaderSettings.DtdProcessing = [System.Xml.DtdProcessing]::Prohibit
$xmlReaderSettings.XmlResolver = $null
$xmlReader = [System.Xml.XmlReader]::Create($xmlTemplate, $xmlReaderSettings)
try {
    $xmlDoc = New-Object System.Xml.XmlDocument
    $xmlDoc.Load($xmlReader)
} finally {
    $xmlReader.Dispose()
}

# ADR-110 §결정 2: Set Principal/UserId to current user SID (dynamic, no hardcoded placeholder)
$nsmgr = New-Object System.Xml.XmlNamespaceManager($xmlDoc.NameTable)
$nsmgr.AddNamespace("ns", "http://schemas.microsoft.com/windows/2004/02/mit/task")
$principalNode = $xmlDoc.SelectSingleNode("//ns:Principal/ns:UserId", $nsmgr)
if ($principalNode -ne $null) {
    $currentUserSID = ([System.Security.Principal.WindowsIdentity]::GetCurrent()).User.Value
    $principalNode.InnerText = $currentUserSID
    Write-Host "  Principal SID updated: $currentUserSID" -ForegroundColor Gray
}

$execNode = $xmlDoc.SelectSingleNode("//ns:Exec", $nsmgr)
if ($execNode -ne $null) {
    $execNode.Command = "powershell.exe"
    $execNode.Arguments = "-ExecutionPolicy RemoteSigned -NonInteractive -File `"$installScript`""
    $execNode.WorkingDirectory = $env:USERPROFILE
}

# Register Task Scheduler job
$taskName = "codeforge-auto-resume"
$taskPath = "\codeforge\"

Write-Host "Registering Task Scheduler job: $taskName" -ForegroundColor Yellow

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "  Task already exists. Updating..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
}

# Import the task
$tempXmlPath = "$env:TEMP\codeforge-auto-resume-$([DateTime]::Now.Ticks).xml"
$xmlDoc.Save($tempXmlPath)

try {
    Register-ScheduledTask -Xml (Get-Content $tempXmlPath -Raw) -TaskName $taskName -TaskPath $taskPath -Force | Out-Null
    Write-Host "  Task registered successfully" -ForegroundColor Green
}
catch {
    Write-Error "Failed to register task: $($_.Exception.Message)"
    exit 1
}
finally {
    Remove-Item $tempXmlPath -Force -ErrorAction SilentlyContinue
}

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
$verifyTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($verifyTask) {
    Write-Host "  Task verification: OK" -ForegroundColor Green
}
else {
    Write-Error "Task verification failed"
    exit 1
}

# Show user configuration
Write-Host "`n=== Installation Complete ===" -ForegroundColor Cyan
Write-Host "Wrapper installed to: $installScript" -ForegroundColor Green
Write-Host "Task name: $taskName" -ForegroundColor Green
Write-Host "`nTo enable auto-resume in your project:" -ForegroundColor Cyan
Write-Host "  1. Edit .claude/_overlay/project.yaml"
Write-Host "  2. Add: runtime:"
Write-Host "           auto_resume:"
Write-Host "             enabled: true" -ForegroundColor Yellow
Write-Host "`nTo disable auto-resume:" -ForegroundColor Cyan
Write-Host "  schtasks /Delete /TN `"$taskName`" /F" -ForegroundColor Yellow
Write-Host "`nFor details, see docs/consumer-guide.md §1j" -ForegroundColor Gray
