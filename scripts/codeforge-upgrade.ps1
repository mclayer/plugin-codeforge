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
    [Parameter(Position=0, Mandatory=$false)]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$Version = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$NormalizePy = Join-Path $ScriptDir "lib\path_normalize.py"

# --------------------------------------------------------------------------
# 내부 헬퍼: path 정규화 (§4.5 abort-before-touch)
# --------------------------------------------------------------------------
function Invoke-ToCanonical {
    param([string]$RawPath)
    $result = & python $NormalizePy $RawPath --repo-root $RepoRoot 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[path_normalization_failure] $result"
        Write-Error "[path_normalization_failure] 원본 입력: $RawPath"
        Write-Error "abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(e))"
        exit 2
    }
    return $result
}

# --------------------------------------------------------------------------
# 사용법 출력
# --------------------------------------------------------------------------
function Show-Usage {
    @"
codeforge-upgrade.ps1 — codeforge plugin 업그레이드 CLI (CFP-743)

사용법:
  pwsh scripts/codeforge-upgrade.ps1 -Action --dry-run
  pwsh scripts/codeforge-upgrade.ps1 -Action --apply
  pwsh scripts/codeforge-upgrade.ps1 -Action --rollback -Version <version>

옵션:
  --dry-run               desired state diff preview (filesystem touch 0, network call 가능)
  --apply                 snapshot → 9 영역 reconcile → 사후 sanity check (단일 atomic unit)
  --rollback <version>    해당 version snapshot restore (예: --rollback 5.74.0)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - 실 reconcile semantic = UpgradeAgent 담당 (thin dispatcher)
  - check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 호출 (CLI 금지, §4.4)
"@
}

# --------------------------------------------------------------------------
# argument enum whitelist parse
# --------------------------------------------------------------------------
if (-not $Action) {
    Show-Usage | Write-Host
    Write-Error "오류: 인자가 필요합니다. --dry-run / --apply / --rollback 중 하나를 지정하세요."
    exit 1
}

$Mode = ""
$RollbackVersion = ""

switch ($Action) {
    "--dry-run" {
        $Mode = "dry_run"
    }
    "--apply" {
        $Mode = "transaction"
    }
    "--rollback" {
        $Mode = "snapshot_restore"
        if (-not $Version) {
            Write-Error "오류: --rollback 에는 -Version 인자가 필요합니다. 예: -Action --rollback -Version 5.74.0"
            exit 1
        }
        $RollbackVersion = $Version
    }
    "--help" {
        Show-Usage | Write-Host
        exit 0
    }
    default {
        # unknown arg = enum whitelist reject (§7.1 free-text injection surface 0)
        Write-Error "오류: 알 수 없는 인자: '$Action'"
        Write-Error "허용 인자: --dry-run / --apply / --rollback"
        Write-Error "unknown arg = enum whitelist reject (Change Plan §7.1 trust boundary)"
        exit 1
    }
}

# --------------------------------------------------------------------------
# repo root path 정규화 (§4.5 — abort-before-touch on failure)
# --------------------------------------------------------------------------
$CanonicalRepoRoot = Invoke-ToCanonical -RawPath $RepoRoot

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
