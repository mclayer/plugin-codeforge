# build-local.ps1 — Rust consumer 로컬빌드 경로 (CFP-2506 / ADR-033 Amendment 1)
# build-local.sh 의 PowerShell parity. 동일 의미·동일 2-stage degrade 모델.
#
# 목적: host 에 링커·binutils(link.exe / gcc / as / dlltool) 가 없어도 로컬에서
#       빠른 사전검증(피드백 루프 단축)을 제공한다. CI 가 단일 검증 권위 —
#       본 스크립트는 보강(pre-flight)이지 머지 게이트 대체가 아니다.
#
# 2-stage degrade 모델 (도메인 지식 rust-local-build-equivalence.md R-1~R-5):
#   1차 — 항상 `cargo check`(+가용 시 `cargo clippy`). codegen 직전 정지 →
#         링커 불요(R-1). 타입·차용·E0382(partial move) 등 컴파일 버그 전부 검출.
#   2차 — check 성공 시에만 완전빌드(codegen+링킹) 분기:
#         (1) Docker 가용 -> rust:1-slim 컨테이너 마운트 빌드(R-3 build-verification)
#         (2) Docker 부재 + native cargo 완전빌드 가능 -> `cargo build`
#         (3) 둘 다 불가 -> graceful degrade(안내 후 exit 0)
#
# 사용법:
#   ./build-local.ps1            # cargo check + (가능 시) 완전빌드
#   ./build-local.ps1 test       # 1번째 인자 = cargo 서브커맨드 passthrough (예: test)
#
# Windows 특이: PowerShell 판은 `--user "$(id -u):$(id -g)"` 를 생략한다
#   ($(id -u) 미지원 — sh.sh parity 주석). Windows Docker 볼륨 소유권 모델이 다름.
#
# 주의: 로컬 GREEN != CI GREEN. Docker linux 빌드는 target 이 linux-gnu 로 바뀌므로
#       Windows 산출물·플랫폼 의존 동작의 ground-truth 는 CI(권위)다(R-3).

param(
    # cargo 서브커맨드 (기본 = build). 1번째 인자로 override (예: test).
    [string]$CargoSubcmd = "build"
)

$ErrorActionPreference = "Continue"

# 완전빌드용 Rust 이미지 (multi-arch). 핀 고정은 consumer 가 조정.
$RustImage = if ($env:BUILD_LOCAL_RUST_IMAGE) { $env:BUILD_LOCAL_RUST_IMAGE } else { "rust:1-slim" }

#─── 사전 점검: cargo 존재 ───
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "[build-local] cargo 가 PATH 에 없습니다. rustup 설치 후 재시도하세요. (https://rustup.rs)"
    exit 127
}

#─── workspace 루트 자동 감지 (R-4: 단일 crate <-> sibling-path workspace 분별) ───
$WorkspaceManifest = (cargo locate-project --workspace --message-format plain 2>$null)
if ([string]::IsNullOrWhiteSpace($WorkspaceManifest)) {
    Write-Error "[build-local] Cargo workspace 를 찾지 못했습니다 (Cargo.toml 부재?). Rust crate 루트에서 실행하세요."
    exit 1
}
$WorkspaceRoot = Split-Path -Parent $WorkspaceManifest

Write-Host "[build-local] workspace 루트: $WorkspaceRoot"
Write-Host "[build-local] cargo 서브커맨드: $CargoSubcmd"

#─── 1차: cargo check (항상 먼저 — 링커 불요, R-1) ───
Write-Host "[build-local] [1/2] cargo check 실행 (링커 불요 — 타입·차용 검사)..."
cargo check --workspace
if ($LASTEXITCODE -ne 0) {
    $rc = $LASTEXITCODE
    Write-Error "[build-local] cargo check 실패 (exit $rc) — 실 컴파일 에러. 완전빌드 진입 안 함."
    exit $rc
}
Write-Host "[build-local] cargo check PASS."

# clippy 는 가용 시 보조 lint (없어도 비차단).
cargo clippy --version 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[build-local] cargo clippy 실행 (보조 lint, 비차단)..."
    cargo clippy --workspace
    if ($LASTEXITCODE -ne 0) { Write-Host "[build-local] clippy 경고 있음 (비차단)." }
}

#─── 2차: 완전빌드 분기 (check 통과 후에만) ───

# 분기 (1) Docker 가용 -> 컨테이너 마운트 빌드 (R-3)
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "[build-local] [2/2] Docker 마운트 빌드 ($RustImage, target=linux-gnu)..."
    Write-Host "[build-local]       (R-3: build-verification proxy — Windows 산출물 동등 아님, CI 권위)"

    # --user 생략 (Windows: `$(id -u)` 미지원 — build-local.sh 와의 의도적 parity 차이).
    # CARGO_TARGET_DIR=/tmp/target: host target/ 캐시 오염 분리.
    # named volume cargo-cache: registry 캐시 재사용.
    # 경로 변수 quote — injection 표면 최소(고정 cargo 명령, 사용자 입력 eval 0).
    docker run --rm `
        -e CARGO_TARGET_DIR=/tmp/target `
        -v "${WorkspaceRoot}:/src" `
        -w /src `
        -v cargo-cache:/usr/local/cargo/registry `
        "$RustImage" `
        cargo $CargoSubcmd
    if ($LASTEXITCODE -ne 0) {
        $rc = $LASTEXITCODE
        Write-Error "[build-local] Docker 마운트 빌드 실패 (exit $rc)."
        Write-Error "[build-local]   sibling path-dep('../') 가 있으면 공통-부모 마운트 필요(R-4)."
        Write-Error "[build-local]   docs/consumer-guide.md §1q '공통-부모 마운트' 참조."
        exit $rc
    }
    Write-Host "[build-local] Docker 마운트 빌드 PASS (linux target — CI 가 Windows 권위)."
    exit 0
}

# 분기 (2) Docker 부재 + native cargo 완전빌드 가능 시도
Write-Host "[build-local] [2/2] Docker 부재 — native cargo $CargoSubcmd 시도..."
cargo $CargoSubcmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "[build-local] native cargo $CargoSubcmd PASS."
    exit 0
}
$rc = $LASTEXITCODE

# 분기 (3) graceful degrade — 완전빌드 경로 미가용 (링커/toolchain 부재).
#   1차 cargo check 는 이미 PASS 했으므로 non-zero 종료 금지(exit 0).
Write-Warning "[build-local] [degrade] 완전빌드 경로 미가용 (native cargo $CargoSubcmd exit $rc)."
Write-Warning "[build-local]   원인 후보: 로컬 링커/binutils 부재(as/dlltool/gcc 또는 link.exe)."
Write-Warning "[build-local]   - cargo check 는 이미 PASS — 타입·차용 검증 완료(피드백 루프 단축됨)."
Write-Warning "[build-local]   - 완전빌드 검증은 Docker 설치 또는 toolchain 충당 후 가능."
Write-Warning "[build-local]   - toolchain 가이드: docs/consumer-guide.md §1q (MSYS2/MSVC/WSL2)."
Write-Warning "[build-local]   - 최종 권위 = CI 게이트(완전빌드·플랫폼 의존 검증)."
exit 0
