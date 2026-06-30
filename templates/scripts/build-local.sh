#!/usr/bin/env bash
# build-local.sh — Rust consumer 로컬빌드 경로 (CFP-2506 / ADR-033 Amendment 1)
#
# 목적: host 에 링커·binutils(link.exe / gcc / as / dlltool) 가 없어도 로컬에서
#       빠른 사전검증(피드백 루프 단축)을 제공한다. CI 가 단일 검증 권위 —
#       본 스크립트는 보강(pre-flight)이지 머지 게이트 대체가 아니다.
#
# 2-stage degrade 모델 (도메인 지식 rust-local-build-equivalence.md R-1~R-5):
#   1차 — 항상 `cargo check`(+가용 시 `cargo clippy`). codegen 직전 정지 →
#         링커 불요(R-1). 타입·차용·E0382(partial move) 등 컴파일 버그 전부 검출.
#   2차 — check 성공 시에만 완전빌드(codegen+링킹) 분기:
#         ① Docker 가용 → rust:1-slim 컨테이너 마운트 빌드(§7.1, R-3 build-verification)
#         ② Docker 부재 + native cargo 완전빌드 가능 → `cargo build`
#         ③ 둘 다 불가 → graceful degrade(안내 후 exit 0 — 1차 check 는 이미 통과)
#
# 사용법:
#   ./build-local.sh            # cargo check + (가능 시) 완전빌드
#   ./build-local.sh test       # 1번째 인자 = cargo 서브커맨드 passthrough (예: test)
#
# 주의: 로컬 GREEN ≠ CI GREEN. Docker linux 빌드는 target 이 linux-gnu 로 바뀌므로
#       Windows 산출물·플랫폼 의존 동작의 ground-truth 는 CI(권위)다(R-3).

set -u

#─── 설정 ───
# 완전빌드용 Rust 이미지 (multi-arch amd64/arm64). 핀 고정은 consumer 가 조정.
RUST_IMAGE="${BUILD_LOCAL_RUST_IMAGE:-rust:1-slim}"
# cargo 서브커맨드 (기본 = build). 1번째 인자로 override (예: test).
CARGO_SUBCMD="${1:-build}"

#─── 사전 점검: cargo 존재 ───
if ! command -v cargo >/dev/null 2>&1; then
    echo "[build-local] ERROR: cargo 가 PATH 에 없습니다. rustup 설치 후 재시도하세요." >&2
    echo "[build-local]        https://rustup.rs" >&2
    exit 127
fi

#─── workspace 루트 자동 감지 (R-4: 단일 crate ↔ sibling-path workspace 분별) ───
# cargo locate-project --workspace 는 workspace 루트(또는 단일 crate)의 Cargo.toml
# 절대 경로를 반환한다. 그 디렉터리가 Docker 마운트 지점 = 컨테이너 안 path-dep 의
# 상대 토폴로지를 호스트와 동형 보존(R-4 silent-fail 방지).
WORKSPACE_MANIFEST="$(cargo locate-project --workspace --message-format plain 2>/dev/null || true)"
if [ -z "$WORKSPACE_MANIFEST" ]; then
    echo "[build-local] ERROR: Cargo workspace 를 찾지 못했습니다 (Cargo.toml 부재?)." >&2
    echo "[build-local]        Rust crate 루트 또는 그 하위에서 실행하세요." >&2
    exit 1
fi
WORKSPACE_ROOT="$(dirname -- "$WORKSPACE_MANIFEST")"

echo "[build-local] workspace 루트: $WORKSPACE_ROOT"
echo "[build-local] cargo 서브커맨드: $CARGO_SUBCMD"

#─── 1차: cargo check (항상 먼저 — 링커 불요, R-1) ───
echo "[build-local] [1/2] cargo check 실행 (링커 불요 — 타입·차용 검사)..."
# 주의: `if ! cargo check; then rc=$?` 는 rc 에 부정(!) 결과(0)가 담겨 실 exit code 를
#   삼킨다(check 실패인데 exit 0). 직접 실행 후 $? 캡처(.ps1 의 $LASTEXITCODE parity).
cargo check --workspace
rc=$?
if [ "$rc" -ne 0 ]; then
    echo "[build-local] cargo check 실패 (exit $rc) — 실 컴파일 에러. 완전빌드 진입 안 함." >&2
    exit "$rc"
fi
echo "[build-local] cargo check PASS."

# clippy 는 가용 시 보조 lint (없어도 비차단).
if cargo clippy --version >/dev/null 2>&1; then
    echo "[build-local] cargo clippy 실행 (보조 lint, 비차단)..."
    cargo clippy --workspace || echo "[build-local] clippy 경고 있음 (비차단)."
fi

#─── 2차: 완전빌드 분기 (check 통과 후에만) ───

# 분기 ① Docker 가용 → 컨테이너 마운트 빌드 (§7.1, R-3)
if command -v docker >/dev/null 2>&1; then
    echo "[build-local] [2/2] Docker 마운트 빌드 ($RUST_IMAGE, target=linux-gnu)..."
    echo "[build-local]       (R-3: build-verification proxy — Windows 산출물 동등 아님, CI 권위)"

    # --user: host uid/gid 로 컨테이너 빌드 → target/ 산출물 소유권 오염 방지.
    #   비-Windows(POSIX, id 명령 가용) 에서만. PowerShell 판은 생략(parity 주석).
    USER_FLAG=()
    if command -v id >/dev/null 2>&1; then
        USER_FLAG=(--user "$(id -u):$(id -g)")
    fi

    # CARGO_TARGET_DIR=/tmp/target: host target/(Windows PE·ELF 혼재) 캐시 오염 분리.
    # named volume cargo-cache: registry 캐시 재사용(반복 빌드 가속).
    # 경로 변수 전부 quote — injection 표면 최소(고정 cargo 명령, 사용자 입력 eval 0).
    docker run --rm \
        "${USER_FLAG[@]}" \
        -e CARGO_TARGET_DIR=/tmp/target \
        -v "$WORKSPACE_ROOT":/src \
        -w /src \
        -v cargo-cache:/usr/local/cargo/registry \
        "$RUST_IMAGE" \
        cargo "$CARGO_SUBCMD"
    rc=$?
    if [ "$rc" -ne 0 ]; then
        echo "[build-local] Docker 마운트 빌드 실패 (exit $rc)." >&2
        echo "[build-local]   sibling path-dep('../') 가 있으면 공통-부모 마운트 필요(R-4)." >&2
        echo "[build-local]   docs/consumer-guide.md §1q '공통-부모 마운트' 참조." >&2
        exit "$rc"
    fi
    echo "[build-local] Docker 마운트 빌드 PASS (linux target — CI 가 Windows 권위)."
    exit 0
fi

# 분기 ② Docker 부재 + native cargo 완전빌드 가능 시도
echo "[build-local] [2/2] Docker 부재 — native cargo $CARGO_SUBCMD 시도..."
# 주의: `if cargo CMD; then exit0; fi; rc=$?` 는 rc 에 if-구문 상태(else 없으면 조건
#   false 시 0)가 담겨 cargo 실 실패코드를 삼킨다(degrade 진단이 항상 exit 0 표기).
#   직접 실행 후 $? 캡처 — L55 check 분기 + .ps1 $LASTEXITCODE 와 parity (F-CR-001).
cargo "$CARGO_SUBCMD"
rc=$?
if [ "$rc" -eq 0 ]; then
    echo "[build-local] native cargo $CARGO_SUBCMD PASS."
    exit 0
fi

# 분기 ③ graceful degrade — 완전빌드 경로 미가용 (링커/toolchain 부재).
#   1차 cargo check 는 이미 PASS 했으므로 non-zero 종료 금지(exit 0).
echo "[build-local] [degrade] 완전빌드 경로 미가용 (native cargo $CARGO_SUBCMD exit $rc)." >&2
echo "[build-local]   원인 후보: 로컬 링커/binutils 부재(as/dlltool/gcc 또는 link.exe)." >&2
echo "[build-local]   - cargo check 는 이미 PASS — 타입·차용 검증 완료(피드백 루프 단축됨)." >&2
echo "[build-local]   - 완전빌드 검증은 Docker 설치 또는 toolchain 충당 후 가능." >&2
echo "[build-local]   - toolchain 가이드: docs/consumer-guide.md §1q (MSYS2/MSVC/WSL2)." >&2
echo "[build-local]   - 최종 권위 = CI 게이트(완전빌드·플랫폼 의존 검증)." >&2
exit 0
