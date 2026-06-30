# rust-cli-minimal — Rust CLI consumer 예시 (로컬빌드 경로 실증)

단일 crate Rust CLI 툴을 `codeforge` 플러그인으로 개발할 때의 overlay 구성 예시. cli-tool-minimal shape 를 **Rust** 로 구체화했다. 가상 도메인은 **Log Parser** (로그 파일 → 구조화 이벤트 추출).

**이 example 의 핵심 목적 (CFP-2506 / ADR-033 Amendment 1)**: Windows 등 host 에 링커·binutils(`as.exe`·`dlltool`·`gcc` 또는 `link.exe`)가 없어 로컬 `cargo build`/`test` 가 불가할 때의 **로컬빌드 경로 표준**(D1 Docker 마운트 빌드 / D2 build-local 스크립트 / D3 toolchain 가이드)을 실제로 보여준다.

## Dev roster

**preset 미사용**. Core의 generic agent만으로 구성:
- `DeveloperAgent` (core) — CLI 명령·파서·도메인 로직 (`src/**`, `Cargo.toml`)
- `InfraEngineerAgent` (core) — 패키징·릴리스·로컬빌드 스크립트
- `QADeveloperAgent` (core) — `tests/**`

service shape 가 더 무거우면 `backend-service` preset 의 `ServiceDeveloperAgent` 채택 (consumer-guide §3c).

## 구조

```
rust-cli-minimal/
├── README.md
├── Cargo.toml                              # 단일 bin crate (의존성 0)
├── src/
│   └── main.rs                             # hello-world + 비-Copy 값 use (cargo check 실효 실증)
├── Dockerfile                              # FROM rust:1-slim — 마운트 빌드 실증 (production image 아님)
├── .dockerignore                           # target/ 등 context 축소
├── .gitignore                              # /target
├── .gitattributes                          # *.sh eol=lf (CRLF shebang 파싱 완화)
└── .claude/
    ├── settings.json                       # SessionStart hook 등록
    └── _overlay/
        ├── CLAUDE.md                       # 프로젝트 SSOT 상수 + 로컬빌드 경로
        ├── project.yaml                    # GitHub·labels·infra_strategy
        └── agents/
            ├── DomainAgent.md              # Log Parser 도메인 용어·제약
            └── DeveloperAgent.md           # Rust 경로 관습·빌드 관습
```

## 로컬빌드 경로 사용법 (핵심)

링커 없는 host 에서도 로컬 사전검증을 당기려면 wrapper 의 `templates/scripts/build-local.{sh,ps1}` 를 이 repo 루트에서 실행:

```bash
# bash (Linux / macOS / Git Bash / WSL2)
./build-local.sh            # cargo check(링커 불요) → Docker 마운트 빌드 또는 native cargo build → graceful degrade
./build-local.sh test       # 1번째 인자 = cargo 서브커맨드 passthrough (예: test)
```

```powershell
# PowerShell (Windows)
./build-local.ps1
./build-local.ps1 test
```

동작 단계 (도메인 지식 R-1~R-5):

1. **1차 `cargo check`** — codegen 직전 정지 → 링커 불요(R-1). 타입·차용·E0382(partial move) 등 컴파일 버그 전부 검출. `src/main.rs` 의 `Event` struct 가 비-Copy String 필드를 move 해 이를 실증한다.
2. **2차 완전빌드** — check 성공 시: Docker 가용 → `rust:1-slim` 컨테이너 마운트 빌드(R-3, target=linux-gnu) / Docker 부재 → native `cargo build` / 둘 다 불가 → graceful degrade(안내 후 종료, exit 0).

Docker 마운트 빌드를 직접 복붙하려면 (consumer-guide §1q 와 동일):

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -e CARGO_TARGET_DIR=/tmp/target \
  -v "$(pwd)":/src -w /src \
  -v cargo-cache:/usr/local/cargo/registry \
  rust:1-slim cargo build
```

## 적용 단계

### 1. 복사 · 플레이스홀더 치환

```bash
cp -r examples/rust-cli-minimal/ ~/my-rust-cli/
cd ~/my-rust-cli
git init
```

`.claude/_overlay/CLAUDE.md`·`project.yaml`의 `<REPLACE: ...>` 치환 (프로젝트명·GitHub org/repo·story_key_prefix·CODEOWNERS team 등). `Cargo.toml` 의 `name` 도 본인 프로젝트로.

### 2. Overlay 커스터마이즈

`DeveloperAgent` overlay 에 본인 CLI 프레임워크(clap/argh 등)·경로 관습 반영.

### 3. 세션 시작

```bash
claude
ls .claude/agents/
# DeveloperAgent.md, InfraEngineerAgent.md, QADeveloperAgent.md + process agents
```

## 권위 경계 (반드시 이해)

- **로컬 = 보강(pre-flight), CI = 단일 검증 권위.** 로컬 PASS 가 머지 게이트를 대체하지 않는다.
- **Docker linux 빌드 ≠ Windows 산출물 동등** — 컨테이너 빌드는 target 이 `x86_64-unknown-linux-gnu` 로 바뀌어 build-verification(타입·차용·플랫폼-비의존 로직) proxy 일 뿐, Windows PE 산출물·플랫폼 의존 동작(`#[cfg(windows)]`)의 ground-truth 는 CI(Windows runner)다 (R-3).
- toolchain 충당(MSYS2 GNU / MSVC Build Tools / WSL2) + CI 권위 ABI 선결 조건 = `docs/consumer-guide.md` §1q.
