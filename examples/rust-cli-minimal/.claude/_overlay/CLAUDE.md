# <REPLACE: 프로젝트명> — Consumer Overlay (Rust CLI)

이 프로젝트는 **Log Parser** Rust CLI 툴 (로그 파일 → 구조화 이벤트 추출 → JSON/CSV 출력). `codeforge` 플러그인을 사용. cli-tool-minimal shape 를 **Rust** 로 구체화한 example.

> 위 core CLAUDE.md §(org chart)에서 "구현 레인의 `role: dev` roster"는 이 프로젝트에서 core의 `DeveloperAgent` + `InfraEngineerAgent`만으로 구성한다. webapp preset·`DataEngineerAgent`는 **미사용**. Frontend 계층 없음. (service shape 가 더 무거우면 `backend-service` preset 의 `ServiceDeveloperAgent` 채택 — §3c.)

## SSOT 상수

**GitHub·labels 등 objective 상수는 [`project.yaml`](project.yaml)에 있음**. 에이전트는 그 파일을 `Read`로 직접 참조. 아래는 narrative 컨텍스트만.

## 기술 스택

- 언어: **Rust** (stable, edition 2021)
- CLI 프레임워크: `<REPLACE: clap 4.x / argh / 수동 std::env::args>`
- 로그 파싱: `<REPLACE: regex crate + serde / nom / 수동 split>`
- 출력: `<REPLACE: serde_json / csv crate / stdout 스트림>`
- 테스트: `cargo test` (+ `<REPLACE: criterion 벤치마크>`)
- 패키징: `<REPLACE: cargo publish / cargo-dist / cross 컨테이너 빌드>`

## 로컬빌드 경로 (Rust 특화 — CFP-2506)

host 에 링커/binutils(`as.exe`·`dlltool`·`gcc` 또는 `link.exe`)가 없어 로컬 `cargo build`/`test` 가 불가할 수 있다. 로컬 피드백 루프를 당기는 표준 경로:

- **`templates/scripts/build-local.sh` / `build-local.ps1`** 를 repo 루트에서 실행 — `cargo check`(링커 불요) 1차 → Docker 마운트 빌드 또는 native `cargo build` → 둘 다 불가 시 graceful degrade(안내 후 종료).
- toolchain 충당(MSYS2/MSVC/WSL2) + Docker 마운트 빌드 복붙 명령 = **`docs/consumer-guide.md` §1q**.
- **로컬 = 보강(pre-flight). CI = 단일 검증 권위** — 로컬 GREEN 이 머지 게이트를 대체하지 않는다. Docker linux 빌드는 Windows 산출물 동등이 아니다(권위 = CI).

## 도메인 용어 사전 (요약)

- **Log Line**: 원시 로그 텍스트 한 줄
- **Event**: Log Line에서 추출된 구조화 레코드 `{level, message, fields...}` (`src/main.rs` 의 `Event` struct 참조 — 비-Copy String 필드)
- **Parser Profile**: 특정 로그 포맷(nginx / syslog / JSON lines 등)을 파싱하는 규칙 셋
- **Filter**: Event 스트림에서 조건에 맞는 것만 통과시키는 predicate

자세한 용어·제약은 `.claude/_overlay/agents/DomainAgent.md`.

## 경로 관습

- `src/main.rs`, `src/cli/**` — CLI 명령·플래그·입출력 (DeveloperAgent)
- `src/parsers/**` — Parser Profile 구현 (DeveloperAgent)
- `src/events/**` — Event 모델·직렬화 (DeveloperAgent)
- `src/filters/**` — Filter DSL·evaluator (DeveloperAgent)
- `Dockerfile`, `deploy/**`, `scripts/**` — 릴리스·배포·로컬빌드 스크립트 (InfraEngineerAgent)
- `tests/**` — 테스트 (QADev)

## TestAgent 러너

- 기능: `<REPLACE: cargo test --workspace>`
- 성능: `<REPLACE: cargo bench>` (대용량 로그 파싱 처리율 측정)
- baseline: `<REPLACE: tests/perf/baselines/>`
