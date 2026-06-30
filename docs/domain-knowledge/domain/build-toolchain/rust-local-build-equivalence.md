---
kind: domain_fact
title: Rust 로컬빌드 동등성 — check/build/test 의 링커 의존 분기 + MSVC↔GNU toolchain + Docker target-triple 한계
area: build-toolchain
topic_slug: rust-local-build-equivalence
status: active
sources:
  - "사용자 요구사항 §1 (CFP-2506) verbatim — Windows Rust consumer 링커/도구(as.exe·dlltool·gcc) 부재로 로컬 cargo build/test 불가"
  - "The Cargo Book — cargo check vs build (https://doc.rust-lang.org/cargo/commands/cargo-check.html)"
  - "rustc Platform Support — Tier 1: x86_64-pc-windows-msvc, x86_64-pc-windows-gnu (https://doc.rust-lang.org/rustc/platform-support.html)"
  - "The rustup book — Windows MSVC vs GNU toolchain ABI (https://rust-lang.github.io/rustup/installation/windows.html)"
  - "Rust target triple 명명 규약 — <arch>-<vendor>-<os>-<abi> (https://doc.rust-lang.org/nightly/rustc/platform-support.html)"
  - "docs/consumer-guide.md §3c (backend-service preset = Rust·Go·Python 공통 비-webapp service)"
  - "docs/consumer-guide.md consumer-scripts.manifest (배포 스크립트 등재 메커니즘, CFP-744 Phase 2)"
related_adrs:
  - ADR-033   # Docker-first Infra — Docker primary, 본 도메인의 "Docker 마운트 빌드" 표준 경로 정합
  - ADR-042   # backend-service preset (ServiceDeveloperAgent) — Rust consumer 커버 model tier
related_stories:
  - CFP-2506
updated: 2026-06-30
---

# Build-toolchain · Rust 로컬빌드 동등성

## 정의

**Rust 로컬빌드 동등성** = consumer 개발자가 로컬에서 수행하는 빌드 검증(`cargo check`/`build`/`test`)이 CI 게이트가 보장하는 검증을 *어디까지* 대체·보강하는가의 도메인 경계. 핵심 분기 2축:

1. **codegen·링킹 필요 여부 축** — `cargo check` 는 링커 불요, `cargo build`/`test` 는 링커 필요. 로컬에 링커(MSVC `link.exe` 또는 GNU `gcc`/`ld`)가 없어도 *타입·차용 검사*는 로컬에서 가능하다.
2. **target triple 동등성 축** — Docker linux 컨테이너 빌드는 target 이 `x86_64-unknown-linux-gnu` 로 바뀐다 → **컴파일·타입 검증의 대리물(proxy)** 은 되지만 **Windows 산출물 바이너리 동등물**은 아니다.

이 두 축이 "로컬은 보강이지 대체 아님 / CI 권위는 게이트로 유지"(사용자 §1 목표)의 도메인 근거다.

## 컨텍스트

CFP-2506 동인 = Windows 개발 환경의 Rust consumer 가 링커/도구(as.exe·dlltool·gcc) 부재로 로컬 `cargo build`/`test` 가 불가 → 매 변경이 "CI 권위"로만 검증되어 피드백 루프가 분 단위 CI 왕복으로 늘어남. 비-Copy 값 E0382 (partial-move) 같은 컴파일·타입 버그가 CI 에서야 표면화한다.

이 도메인 지식은 codeforge 스캐폴딩에 "로컬빌드 경로 표준"(D1 문서 표준 / D2 build-local 스크립트 / D3 toolchain 가이드)을 Rust consumer onboarding 에 제공할 때, **무엇을 보장하고 무엇을 못 보장하는지** 설계 lane 이 정확히 wiring 하도록 하는 invariant 집합을 제공한다. 기존 codeforge 도메인 지식에 Rust 빌드 toolchain 항목이 부재(knowledge gap)했으므로 신설한다.

OOS(사용자 §1): mctrader 전용 구현 디테일 / 비-Rust consumer / CI 게이트 권위 자체 변경.

## 핵심 규칙 / 불변식 (invariant)

### R-1: cargo check 는 링커 불요 — codegen 단계를 건너뛴다 (도메인 핵심)

- `cargo check` 는 프런트엔드 컴파일(파싱 → 매크로 확장 → 이름 해석 → 타입 검사 → 차용 검사 → MIR 생성·borrow check)까지 수행하고 **코드 생성(codegen) 직전에 멈춘다**. 즉 `.rmeta`(메타데이터)만 만들고 object code(`.o`)·실행 바이너리를 만들지 않는다. (출처: The Cargo Book — `cargo check`)
- **링커(`link.exe`/`gcc`/`ld`)·어셈블러(`as`)·`dlltool` 은 codegen 산출물(object code)을 묶는 단계에서만 필요**하다. check 는 이 단계에 도달하지 않으므로 링커·binutils 부재 환경에서도 동작한다.
- **함의**: 사용자가 보고한 E0382(partial move, 비-Copy 값 부분 이동) 류 컴파일·타입·차용 버그는 **전부 check 단계에서 검출**된다 — 링커 없이 로컬에서 즉시 잡힌다. 로컬빌드 표준의 1차 권장 명령은 `cargo check`(+`cargo clippy`)여야 한다. 이것이 "로컬로 피드백 루프를 당긴다"의 최소·고-ROI 경로.

### R-2: build/test 는 링커 필요 — 비결정 분기는 target ABI 다 (MSVC vs GNU)

- `cargo build`(바이너리 생성)와 `cargo test`(테스트 바이너리 컴파일+실행)는 codegen + **링킹** 을 수행하므로 링커가 필수다.
- Windows 에는 두 Tier-1 target ABI 가 있다 (출처: rustc Platform Support):
  - **`x86_64-pc-windows-msvc`** (rustup Windows **기본 host**): MSVC ABI. 링커 = `link.exe`(MSVC). C 런타임 = MSVC CRT. **MSYS2 의 `as.exe`/`dlltool`/`gcc`(MinGW binutils)를 쓰지 않는다.** 필요 의존 = "Visual Studio Build Tools(MSVC)" 또는 "Windows SDK".
  - **`x86_64-pc-windows-gnu`**: GNU ABI(MinGW-w64). 링커·어셈블러·import-lib 도구 = `gcc`/`ld`/`as`/`dlltool`(MinGW binutils). 이 target 에서만 `as.exe`·`dlltool`·`gcc` 가 요구된다.
- **함의 — 이것이 도메인의 결정적 분기**: 사용자가 보고한 "`as.exe`·`dlltool`·`gcc` 부재"는 **GNU toolchain 을 쓰고 있다는 신호**다. 동일 머신에서 **MSVC toolchain(기본)으로 전환**하면 MinGW binutils 자체가 불요해져 그 결함이 사라질 수 있다 — D3 toolchain 가이드는 "MSYS2 로 MinGW binutils 채우기"와 **"MSVC Build Tools 설치(GNU→MSVC 전환)"를 동격 또는 선행 선택지로** 제시해야 한다. ABI 전환은 비공짜다 (R-5 참조).

### R-3: Docker linux 빌드 = 컴파일·타입 검증 proxy 이지 Windows 산출물 동등 아님

- Docker `rust:<tag>` 컨테이너 안에서 빌드하면 target triple 이 `x86_64-unknown-linux-gnu`(컨테이너 host)로 바뀐다. 산출물은 **ELF linux 바이너리**이지 Windows PE 바이너리가 아니다.
- **Docker 빌드가 보장하는 것 (build-verification)**: cross-platform 으로 안정적인 검증 — 타입 검사, 차용 검사, 대부분의 컴파일 에러, 그리고 **플랫폼 비의존 로직의 `cargo test` 통과**. 이는 CI 권위의 *보강*으로서 충분히 가치 있다.
- **Docker 빌드가 보장 못 하는 것 (artifact-equivalence)**:
  - Windows 전용 `#[cfg(windows)]` / `#[cfg(target_os = "windows")]` 코드 경로는 linux target 에서 컴파일조차 안 되거나 다른 분기를 탄다 → 이 코드의 검증 누락.
  - 플랫폼 의존 동작(경로 구분자, 파일 권한, FFI/winapi, 시간대, 줄바꿈)에 의존하는 테스트는 linux 에서 다른 결과 → **false-GREEN(Windows 에서 깨질 것을 통과로 보고) 또는 false-RED** 위험.
  - 실행 바이너리 ABI·링킹 결과(Windows PE) 자체는 검증 안 됨.
- **함의 — build-verification ↔ artifact-equivalence 를 반드시 구분**: 로컬빌드 표준 문서는 Docker 경로를 "**컴파일·타입·플랫폼-비의존 테스트 검증**" 으로만 advertise 하고, "Windows 산출물·플랫폼-의존 동작의 ground-truth 는 CI(Windows runner)" 임을 명문화해야 한다. 이것이 "로컬은 보강이지 대체 아님"의 정확한 도메인 표현. (Docker-first 정합 = ADR-033)

### R-4: cross-repo path-dep(sibling crate)는 컨테이너 안에서 `../` 로 안 풀린다

- Cargo `path = "../other-crate"` 의존은 호스트 파일시스템의 상대 경로를 그대로 해석한다. `docker run -v <repo>:/src -w /src` 로 repo 하나만 마운트하면, 컨테이너 안 `/src` 에서 `../other-crate` 는 `/other-crate`(또는 컨테이너 루트 밖)를 가리켜 **부재 → 빌드 실패**.
- **도메인 이슈**: sibling crate 의존이 있는 workspace 는 단일-repo 마운트 모델로 Docker 빌드가 성립하지 않는다. 해소 패턴 후보(설계 lane 결정):
  - (a) **공통 부모 마운트**: sibling 들의 공통 부모 디렉터리를 `-v <parent>:/src` 로 마운트하고 `-w /src/<this-crate>` 로 작업 → 컨테이너 안 상대 경로 토폴로지가 호스트와 동형 보존.
  - (b) **각 sibling 개별 마운트 + 컨테이너 내 동형 경로 배치**: `-v <repo>:/src -v <sibling>:/sibling` 후 컨테이너 안에서 호스트와 같은 상대 관계가 되도록 경로 정렬(또는 junction/symlink).
  - Windows 측 junction(`mklink /J`)/symlink 으로 호스트 경로 토폴로지를 정규화하는 패턴도 사용자 §1(D1)이 언급. 어느 패턴이든 **불변식 = 컨테이너 내부 `path=` 의 상대 토폴로지가 호스트와 동형이어야 한다**.
- **함의**: build-local 스크립트(D2)는 단일 crate 와 sibling-path workspace 를 **다르게 처리**해야 한다 — workspace 루트 또는 공통 부모를 마운트 지점으로 자동 감지하지 않으면 sibling-path consumer 에서 silent fail.

### R-5: MSVC↔GNU ABI 전환은 비공짜 — 무조건 MSVC 권고는 금물

- MSVC 와 GNU 는 **ABI 가 다르다**(C 런타임·예외 처리·이름 맹글링·import lib 형식). 따라서:
  - 두 toolchain 의 산출물은 호환되지 않는다 (한 ABI 로 빌드한 크레이트를 다른 ABI 로 링크 불가).
  - 특정 crate 가 GNU 전용(예: 일부 MinGW 전제 sys-crate)이거나 MSVC 전용 의존이면 ABI 전환이 빌드 자체를 깬다.
  - **CI runner 가 어느 ABI 를 권위로 삼는지**가 로컬 권장 ABI 를 결정한다 — 로컬과 CI 의 ABI 가 다르면 로컬 GREEN ↔ CI RED 괴리가 재발(루프 단축 목적 자체가 무력화).
- **함의**: D3 가 "MSVC 전환"을 제시할 때 **CI 의 권위 ABI 와 일치**하는지를 선결 조건으로 명문화해야 한다. consumer 의 CI 가 GNU 권위면 로컬도 GNU 를 채워야(MSYS2) 괴리가 없다. "MSVC 가 항상 정답"은 도메인상 거짓 — CI 권위 ABI 가 기준.

## 경계 / 예외

- **In scope**: Rust consumer 의 로컬빌드 검증이 CI 권위를 *보강*하는 도메인 경계 — check/build/test 의 링커 의존 분기(R-1/R-2), MSVC↔GNU ABI 분기(R-2/R-5), Docker target-triple 의 build-verification↔artifact-equivalence 구분(R-3), sibling path-dep 마운트 토폴로지 불변식(R-4).
- **Out of scope (사용자 §1 OOS + 설계 위임)**:
  - mctrader 전용 구현 디테일 / 비-Rust consumer / CI 게이트 권위 자체 변경 (사용자 OOS).
  - build-local 스크립트의 환경별 toolchain 분기 *구체 구현*, manifest 등재 wiring, MSYS2/WSL2 설치 절차 *구체 단계* — 설계·구현 lane 위임(도메인 layer 아님).
  - consumer-scripts.manifest 등재 여부 결정: build-local 은 CI runtime invoke 가 아니라 ad-hoc 개발자 CLI 이므로, manifest 등재 시 dependent-workflow 미부착 패턴(codeforge-upgrade.sh 선례)에 해당 — 등재 형식은 설계 lane 판단.
- **Anti-pattern**:
  - Docker linux 빌드 GREEN 을 "Windows 에서도 옳다"로 단정(R-3 — artifact-equivalence 아님, false-GREEN).
  - 무조건 "MSVC 로 바꿔라" 권고(R-5 — CI 권위 ABI 무시 시 괴리 재발).
  - sibling-path workspace 를 단일-repo 마운트로 처리(R-4 — `../` silent fail).
  - 로컬 GREEN 을 CI 권위 대체로 advertise(사용자 §1 — 보강이지 대체 아님).

## 관련 ADR / Story / 코드

- [ADR-033](../../../../archive/adr/ADR-033-docker-first-infra.md) — Docker-first Infra. R-3 의 "Docker rust-image 마운트 빌드" 표준 경로가 이 정책과 정합 (Docker primary).
- [ADR-042](../../../../archive/adr/ADR-042-agent-model-selection-policy.md) — backend-service preset(ServiceDeveloperAgent, sonnet)이 Rust·Go·Python 공통 비-webapp service 를 커버. Rust consumer onboarding 의 model tier 근거.
- [Story CFP-2506](../../../stories/CFP-2506.md) — 본 KB 도출 Story.
- 코드 참조 (repo 사실): `examples/` 에 Rust 예제 부재 (cli-tool-minimal=Go golang:1.22-alpine, webapp-minimal, library-minimal). Rust 예제·Dockerfile 신설이 D1/D2 의 산출물 후보.
- `docs/consumer-guide.md` line 589 — migration_tool enum `sqlx-migrate`(Rust + sqlx) 존재 (Rust consumer 가 이미 부분 cover 됨을 시사).

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2506 DomainAgent, 독립 관점). Rust 빌드 toolchain 도메인 신설 (기존 도메인 지식 부재 = knowledge gap). R-1(check=링커 불요/codegen 전 정지) / R-2(build·test=링커 필요, MSVC↔GNU ABI 분기) / R-3(Docker linux = build-verification proxy ≠ Windows artifact-equivalence) / R-4(sibling path-dep `../` 컨테이너 미해소 + 공통-부모 마운트 불변식) / R-5(MSVC↔GNU ABI 전환 비공짜, CI 권위 ABI 가 기준). 사용자 §1(CFP-2506) verbatim + Cargo Book / rustc Platform Support / rustup Windows ABI 인용.
