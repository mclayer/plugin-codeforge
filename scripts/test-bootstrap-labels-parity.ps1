# test-bootstrap-labels-parity.ps1 — bootstrap-labels.sh ↔ bootstrap-labels.ps1 label parity 검증 (CFP-2250).
#
# 목적 (Change Plan §8 TC2 / 설계리뷰 P2-2):
#   .sh (IFS read) ↔ .ps1 (line split) 양 dry-run 출력의 (name,color,desc) 3-tuple 정합.
#   단순 name set-equality 가 아니라 **parser/인코딩 divergence** 변별 —
#   UTF-8 한글 desc / embedded special char (em-dash, →, 화살표) / 필드 경계 처리 차이를 잡는다.
#
# 전제: bash (Git Bash / WSL / ubuntu) + powershell|pwsh + python+pyyaml.
#   bash 부재 시 = SKIP (Windows-only 환경 — .ps1 단독 self-check 만, exit 0).
#
# Exit code: 0 (parity PASS 또는 bash 부재 SKIP) / 1 (divergence 검출)
#
# Usage:
#   pwsh -File scripts/test-bootstrap-labels-parity.ps1
#   pwsh -File scripts/test-bootstrap-labels-parity.ps1 -Verbose

[CmdletBinding()]
param()

# native 자식 프로세스(powershell/bash)가 stderr 에 쓰면 5.1 이 NativeCommandError 로 승격시켜
# $? 를 false 로 만든다 (env 주의사항). Stop 금지 — Continue 로 두고 exit code 를 직접 평가.
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch { }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Sh  = Join-Path $ScriptDir "bootstrap-labels.sh"
$Ps1 = Join-Path $ScriptDir "bootstrap-labels.ps1"

if (-not (Test-Path $Sh))  { [Console]::Error.WriteLine("FAIL: bootstrap-labels.sh 부재 — $Sh"); exit 1 }
if (-not (Test-Path $Ps1)) { [Console]::Error.WriteLine("FAIL: bootstrap-labels.ps1 부재 — $Ps1"); exit 1 }

# --- parse helper: "name`tcolor`tdesc" 3-field line → ordered hashtable[name]=@(color,desc) ---
function ConvertTo-LabelMap {
    param([string[]]$Lines)
    $map = [ordered]@{}
    foreach ($line in $Lines) {
        if (-not $line) { continue }
        $parts = $line -split "`t", 3
        if ($parts.Count -ne 3) { continue }
        $map[$parts[0]] = @($parts[1], $parts[2])
    }
    return $map
}

# stdout 만 안전 캡처 (stderr → temp file, 5.1 NativeCommandError 회피).
$tmpErr = [System.IO.Path]::GetTempFileName()

# --- 1. .ps1 dry-run (native) ---
# pwsh (PowerShell 7) 우선 — CI windows-latest 기본. 부재 시 powershell.exe (5.1 floor).
$pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
if ($pwshCmd) {
    $psRaw = & pwsh -NoProfile -File $Ps1 -DryRun 2>$tmpErr
} else {
    $psRaw = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Ps1 -DryRun 2>$tmpErr
}
$psMap = ConvertTo-LabelMap -Lines $psRaw

# --- 2. .sh dry-run (bash 필요) ---
$bashCmd = Get-Command bash -ErrorAction SilentlyContinue
if (-not $bashCmd) {
    Remove-Item $tmpErr -ErrorAction SilentlyContinue
    [Console]::Error.WriteLine("SKIP: bash 미발견 — .sh dry-run 불가 (Windows-only 환경). .ps1 self-check 만 수행.")
    [Console]::Out.WriteLine("PARITY SKIP — .ps1 emitted $($psMap.Count) label (bash 부재로 cross-compare 생략).")
    exit 0
}
$shRaw = & bash $Sh --dry-run 2>$tmpErr
$shMap = ConvertTo-LabelMap -Lines $shRaw
Remove-Item $tmpErr -ErrorAction SilentlyContinue

# --- 3. 비교: name set + per-field (color, desc) divergence ---
$errors = New-Object System.Collections.Generic.List[string]

$shNames = [System.Collections.Generic.HashSet[string]]::new()
$shMap.Keys | ForEach-Object { [void]$shNames.Add($_) }
$psNames = [System.Collections.Generic.HashSet[string]]::new()
$psMap.Keys | ForEach-Object { [void]$psNames.Add($_) }

foreach ($n in $shMap.Keys) {
    if (-not $psNames.Contains($n)) { $errors.Add("name only in .sh: $n"); continue }
    $shVal = $shMap[$n]; $psVal = $psMap[$n]
    if ($shVal[0] -cne $psVal[0]) { $errors.Add("color divergence [$n]: sh='$($shVal[0])' ps1='$($psVal[0])'") }
    # desc = UTF-8 한글 / special char divergence 변별 (-cne = case + byte sensitive ordinal)
    if ($shVal[1] -cne $psVal[1]) {
        $errors.Add("desc divergence [$n]: sh.len=$($shVal[1].Length) ps1.len=$($psVal[1].Length)")
    }
}
foreach ($n in $psMap.Keys) {
    if (-not $shNames.Contains($n)) { $errors.Add("name only in .ps1: $n") }
}

# --- 4. count parity (self-check 수치) ---
if ($shMap.Count -ne $psMap.Count) {
    $errors.Add("count divergence: sh=$($shMap.Count) ps1=$($psMap.Count)")
}

if ($errors.Count -gt 0) {
    [Console]::Error.WriteLine("PARITY FAIL — $($errors.Count) divergence:")
    foreach ($e in $errors) { [Console]::Error.WriteLine("  - $e") }
    exit 1
}

[Console]::Out.WriteLine("PARITY PASS — sh=$($shMap.Count) ps1=$($psMap.Count) label (name+color+desc 3-tuple 정합, UTF-8/special char 포함).")
exit 0
