# codeforge-upgrade.ps1 — CFP-743 Phase 2 — PowerShell thin dispatcher
# Change Plan §3.1 3 책임 분리 아키텍처 / §4.1 CLI 인자 schema / §4.4 drift-check ownership
#
# 역할: CLI layer (thin dispatcher ONLY) — sh 와 동일 reconcile semantic
#   - argument enum whitelist parse (--dry-run / --apply / --rollback <version>)
#   - unknown arg = reject (no free-text injection surface, §7.1 trust boundary)
#   - Orchestrator / UpgradeAgent 위임만 (reconcile semantic 로직 0건)
#   - check-codeforge-version-drift.sh 호출 금지 (UpgradeAgent Plan stage 귀속, §4.4)
#   - user_decision_branches: 0 (no prompt invariant, reconcile-protocol-v1)
#
# sh ↔ ps1 parity: 동일 reconcile semantic, 동일 canonical 함수 (path_normalize.py 공유)
# §4.5 path normalization: 6 입력 형태 → canonical (scripts/lib/path_normalize.py 위임)
# abort-before-touch: path 정규화 실패 시 filesystem touch 0 보장 상태 abort

param(
    # CFP-744 AC-11 §3.7.2-parser ps1 parity — sh 의 while/case loop 동형:
    # ValueFromRemainingArguments 로 전 인자 capture 후 loop parse
    # (sh↔ps1 byte-level behavior parity — reconcile-protocol-v1 §4.5 parity_invariant).
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ArgList = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$NormalizePy = Join-Path $ScriptDir "lib\path_normalize.py"

# --------------------------------------------------------------------------
# 내부 헬퍼: path 정규화 (§4.5 abort-before-touch)
# --------------------------------------------------------------------------
function Invoke-ToCanonical {
    param([string]$RawPath, [string]$RepoRootArg)
    $result = & python $NormalizePy $RawPath --repo-root $RepoRootArg 2>&1
    if ($LASTEXITCODE -ne 0) {
        [Console]::Error.WriteLine("[path_normalization_failure] $result")
        [Console]::Error.WriteLine("[path_normalization_failure] 원본 입력: $RawPath")
        [Console]::Error.WriteLine("abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(e))")
        exit 2
    }
    return $result
}

# --------------------------------------------------------------------------
# 사용법 출력
# --------------------------------------------------------------------------
function Show-Usage {
    @"
codeforge-upgrade.ps1 — codeforge plugin 업그레이드 CLI (CFP-743 / CFP-744 AC-11)

사용법:
  pwsh scripts/codeforge-upgrade.ps1 --dry-run
  pwsh scripts/codeforge-upgrade.ps1 --apply
  pwsh scripts/codeforge-upgrade.ps1 --rollback <version>
  pwsh scripts/codeforge-upgrade.ps1 --apply --repo <consumer-repo-root>

옵션:
  --dry-run               desired state diff preview (filesystem touch 0, network call 가능)
  --apply                 snapshot → 9 영역 reconcile → 사후 sanity check (단일 atomic unit)
  --rollback <version>    해당 version snapshot restore (예: --rollback 5.74.0)
  --repo <path>           reconcile 대상 consumer repo root 명시 지정 (CFP-744 AC-11,
                          mode 와 순서 무관 — orthogonal). 미지정 시
                          CODEFORGE_REPO_ROOT env → 없으면 SCRIPT_DIR 부모 (현 동작 보존)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - 실 reconcile semantic = UpgradeAgent 담당 (thin dispatcher)
  - check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 호출 (CLI 금지, §4.4)
"@
}

# --------------------------------------------------------------------------
# argument parser — §3.7.2-parser ps1 parity (sh 의 while/case loop 동형)
# 7-invariant byte-level 보존 (sh 와 동일 (a)~(g)):
#   (a) 기존 mode invocation 동작·exit code·error 문구 byte-identical
#   (b) --repo orthogonal (mode 순서 무관)  (c) --rollback value-taking
#   (d) mode 정확히 1개 강제  (e) unknown arg enum whitelist reject
#   (f) downstream pipeline 무변경  (g) --repo/env/fallback resolve byte-identical
# --------------------------------------------------------------------------
if ($ArgList.Count -eq 0) {
    Show-Usage | Write-Host
    [Console]::Error.WriteLine("오류: 인자가 필요합니다. --dry-run / --apply / --rollback 중 하나를 지정하세요.")
    exit 1
}

$Mode = ""
$RollbackVersion = ""
$InputRepo = ""
$ModeSetCount = 0

$i = 0
while ($i -lt $ArgList.Count) {
    $tok = $ArgList[$i]
    switch ($tok) {
        "--dry-run" {
            $Mode = "dry_run"; $ModeSetCount++; $i++
        }
        "--apply" {
            $Mode = "transaction"; $ModeSetCount++; $i++
        }
        "--rollback" {
            $Mode = "snapshot_restore"; $ModeSetCount++
            if ($i + 1 -ge $ArgList.Count) {
                [Console]::Error.WriteLine("오류: --rollback 에는 version 인자가 필요합니다. 예: --rollback 5.74.0")
                exit 1
            }
            $RollbackVersion = $ArgList[$i + 1]; $i += 2
        }
        "--repo" {
            if ($i + 1 -ge $ArgList.Count) {
                [Console]::Error.WriteLine("오류: --repo 에는 path 인자가 필요합니다. 예: --repo /path/to/consumer-repo")
                exit 1
            }
            $InputRepo = $ArgList[$i + 1]; $i += 2
        }
        { $_ -eq "--help" -or $_ -eq "-h" } {
            Show-Usage | Write-Host
            exit 0
        }
        default {
            # unknown arg = enum whitelist reject (§7.1 free-text injection surface 0)
            [Console]::Error.WriteLine("오류: 알 수 없는 인자: '$tok'")
            [Console]::Error.WriteLine("허용 인자: --dry-run / --apply / --rollback <version> / --repo <path>")
            [Console]::Error.WriteLine("unknown arg = enum whitelist reject (Change Plan §7.1 trust boundary)")
            exit 1
        }
    }
}

# (d) mode 정확히 1개 강제 (0개 = 인자 필요 / 2개+ = mode 충돌)
if ($ModeSetCount -eq 0) {
    Show-Usage | Write-Host
    [Console]::Error.WriteLine("오류: 인자가 필요합니다. --dry-run / --apply / --rollback 중 하나를 지정하세요.")
    exit 1
}
if ($ModeSetCount -gt 1) {
    [Console]::Error.WriteLine("오류: mode 인자는 정확히 1개여야 합니다 (--dry-run / --apply / --rollback 중복/충돌).")
    exit 1
}

# --------------------------------------------------------------------------
# (g) consumer_repo_root resolve (CFP-744 AC-11 §4.5)
#   우선순위: --repo > CODEFORGE_REPO_ROOT env > SCRIPT_DIR 부모 (현 동작 byte-identical)
# --------------------------------------------------------------------------
if ($InputRepo) {
    $RepoRoot = $InputRepo
} elseif ($env:CODEFORGE_REPO_ROOT) {
    $RepoRoot = $env:CODEFORGE_REPO_ROOT
} else {
    # fallback = 현 동작 그대로 (SCRIPT_DIR 부모, byte-identical)
    $RepoRoot = Split-Path -Parent $ScriptDir
}

# --------------------------------------------------------------------------
# §4.5 / §7.4.1 (i) — --repo wrong-target 검증 (실재 디렉터리 AND .git 보유)
#   미지정 fallback (SCRIPT_DIR 부모) = plugin repo → 검증 skip (현 동작 보존)
# --------------------------------------------------------------------------
if ($InputRepo -or $env:CODEFORGE_REPO_ROOT) {
    if (-not (Test-Path -PathType Container $RepoRoot)) {
        [Console]::Error.WriteLine("[repo_target_failure] 지정 repo 가 실재 디렉터리 아님: $RepoRoot")
        [Console]::Error.WriteLine("abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(i))")
        exit 2
    }
    if (-not (Test-Path -PathType Container (Join-Path $RepoRoot ".git"))) {
        [Console]::Error.WriteLine("[repo_target_failure] 지정 repo 가 git repo 아님 (.git 부재): $RepoRoot")
        [Console]::Error.WriteLine("reconcile target 재확인 요망 (오타 / 다른 repo / non-git 디렉터리)")
        [Console]::Error.WriteLine("abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(i))")
        exit 2
    }
}

# --------------------------------------------------------------------------
# repo root path 정규화 (§4.5 — abort-before-touch on failure)
# (f) downstream pipeline 무변경 — resolve source 만 확장
# --------------------------------------------------------------------------
$CanonicalRepoRoot = Invoke-ToCanonical -RawPath $RepoRoot -RepoRootArg $RepoRoot

# --------------------------------------------------------------------------
# UpgradeAgent spawn 위임 출력 (sh ↔ ps1 동일 semantic)
# reconcile semantic 로직 0건 — thin dispatcher
# --------------------------------------------------------------------------
Write-Host "=== codeforge-upgrade.ps1: UpgradeAgent spawn 위임 ==="
Write-Host "mode: $Mode"
if ($Mode -eq "snapshot_restore") {
    Write-Host "rollback_version: $RollbackVersion"
}
Write-Host "canonical_repo_root: $CanonicalRepoRoot"
Write-Host "reconcile_protocol_version: 1.2"
Write-Host "user_decision_branches: 0"
Write-Host ""
Write-Host "--- Orchestrator: 아래 UpgradeAgent 를 spawn 하여 처리하십시오 ---"
Write-Host "agent_file: templates/agents/UpgradeAgent.md"
Write-Host "input_mode: $Mode"
if ($Mode -eq "snapshot_restore") {
    Write-Host "input_rollback_version: $RollbackVersion"
}
Write-Host "input_repo_root: $CanonicalRepoRoot"
Write-Host ""
Write-Host "주의: check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 에서 호출 (CLI 금지 — §4.4)"
Write-Host "주의: 사용자 결정 분기 0 유지 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)"
