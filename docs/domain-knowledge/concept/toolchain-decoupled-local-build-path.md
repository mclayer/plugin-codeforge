---
kind: concept_definition
type: domain-knowledge
slug: toolchain-decoupled-local-build-path
title: Toolchain-decoupled local build path — host toolchain 부재를 우회하는 컨테이너/대체-ABI 빠른 피드백 경로 (CI 권위 보존)
status: Active
updated: 2026-06-30
carrier_story: CFP-2506
related_adrs:
  - ADR-033  # Docker-first 인프라 표준 (presets/ Docker primary) — 컨테이너 마운트 빌드의 상위 표준
related_files: []
---

# Toolchain-decoupled local build path

## 정의

host OS 에 native 컴파일러/링커 toolchain 이 부재하거나 깨졌을 때, **CI 를 단일 검증 권위로 유지한 채** 개발자에게 별도의 (느린 CI 왕복이 아닌) 로컬 사전검증 경로를 제공하는 패턴. 검증의 **권위(authority)** 와 **빠른 피드백(feedback loop)** 을 분리해, 후자만 host-toolchain 의존에서 떼어낸다.

## 컨텍스트

이 개념의 출발점 = host 에 빌드 toolchain 이 완비되지 않아 검증이 CI 로 단일화되고 피드백 루프가 분 단위 CI 왕복으로 늘어나는 문제(CFP-2506 동인). 외부 사실 anchor:

### 문제의 외부 사실 anchor
- Windows 에서 `rustup` 기본 host triple = **MSVC ABI** (`x86_64-pc-windows-msvc`) — MSVC 링커(`link.exe`)·Visual Studio Build Tools 에 hard dependency. 출처: https://rust-lang.github.io/rustup/installation/windows.html
- 대체 ABI `x86_64-pc-windows-gnu` (Tier 1) 은 MinGW-w64 의 `gcc`/`as.exe`/`dlltool.exe`/`ld` 를 요구. 이 도구들은 rustup 이 자동 설치하지 않으며 별도 MSYS2/MinGW 설치 필요. 출처: https://doc.rust-lang.org/beta/rustc/platform-support/windows-gnu.html
- 즉 "로컬 빌드 불가" = 두 ABI 중 어느 toolchain 도 host 에 완비되지 않은 상태. CI 만이 toolchain 을 완비 → 검증이 CI 로 단일화되어 피드백 루프가 CI 왕복(분 단위)으로 늘어남.

### 우회 경로의 외부 사실 anchor (선택지 — 단정적 채택은 설계 영역)
세 경로 모두 host toolchain 을 **재현(컨테이너) / 대체(GNU ABI 보강) / 격리(별도 OS)** 중 하나로 충당한다.

1. **컨테이너 재현** — Docker 공식 `rust` 이미지(linux/glibc) 에 repo 를 bind-mount 하고 컨테이너 안 linux toolchain 으로 빌드. multi-arch(amd64/arm64) 지원. 출처: https://hub.docker.com/_/rust
2. **대체-ABI 보강** — MSYS2 `pacman -S mingw-w64-x86_64-toolchain` 로 `as`/`dlltool`/`gcc` 설치 후 windows-gnu target 빌드. 출처: https://www.msys2.org/ , https://github.com/rust-lang/rust-wiki-backup/blob/master/Using-Rust-on-Windows.md
3. **OS 격리** — WSL2 안 native linux toolchain. 단 프로젝트 파일을 `/mnt/c`(NTFS) 가 아닌 WSL2 native fs 에 두지 않으면 cross-fs I/O 로 3~10x 느림. 출처: https://markentier.tech/posts/2022/01/speedy-rust-builds-under-wsl2/

### 검증 깊이 계층 (cargo)
로컬 사전검증은 "어디까지 검증하느냐"를 선택할 수 있다 — `cargo check` 는 codegen·링크 단계를 생략(`--emit=metadata`)하고 type check·borrow check 만 수행 → **링커 없이도 동작 가능**. `cargo build`/`test` 는 codegen+링크 필요 → 링커(toolchain) 필수. 출처: https://doc.rust-lang.org/cargo/commands/cargo-check.html , https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
이 계층 덕에 "링커 없는 host 에서도 `cargo check` 수준 사전검증은 가능"한 부분 우회가 존재.

## 핵심 규칙

### R-개념-1: CI = 단일 검증 권위 (불변식)
- 로컬 경로는 *사전검증(pre-flight)* 일 뿐 머지 게이트가 아니다. 로컬 PASS 가 CI PASS 를 대체하지 못한다 (로컬은 host/컨테이너 환경 drift 가능).
- 로컬 경로 추가는 **순수 가산(additive)** — 기존 CI 권위·branch protection 을 축소하지 않는다.

### R-개념-2: 적용 시 함정 (외부에서 관찰됨)
- 컨테이너 빌드 시 host 의 `target/`(Windows PE 산출물·캐시) 와 컨테이너 linux `target/`(ELF) 가 같은 dir 을 공유하면 **캐시 오염** → 별도 target dir 권고(`CARGO_TARGET_DIR` 분리). 출처: https://docs.docker.com/build/cache/optimize/
- bind mount I/O 는 native fs 보다 느림 — Docker Desktop 의 consistency 옵션(`cached`/`delegated`) 또는 named volume 으로 cargo registry/target 캐시 분리. 출처: https://docs.docker.com/engine/storage/volumes/
- CRLF↔LF·파일 권한/소유(host uid ↔ container uid) 차이 — `--user "$(id -u):$(id -g)"` 패턴으로 소유 문제 완화. 출처: https://hub.docker.com/_/rust

## 경계

- **In scope**: native 빌드 toolchain 부재/손상 host 에서, CI 단일 검증 권위를 보존한 채 로컬 빠른-피드백 경로를 제공하는 패턴 자체 (컨테이너 재현 / 대체-ABI 보강 / OS 격리 3 우회 + cargo 검증 깊이 계층).
- **Out of scope**: 특정 언어·toolchain 의 구체 구현 디테일(설계·구현 lane), CI 게이트 권위 자체의 변경(로컬은 보강만), 비-Rust 적용의 구체화(개념은 언어-비의존이나 본 carrier 는 Rust).
- **Anti-pattern**: 로컬 GREEN 을 CI 권위 대체로 advertise(불변식 위반) / 컨테이너 linux 빌드 GREEN 을 host 플랫폼 산출물 동등으로 단정(build-verification ↔ artifact-equivalence 혼동 — 동행 도메인 fact [[rust-local-build-equivalence]] R-3 참조).

## 관련 ADR

- [ADR-033](../../../archive/adr/ADR-033-docker-first-infra-engineering.md) Amendment 1 — Docker-first 인프라 표준. 본 개념의 "컨테이너 재현" 우회 경로가 Docker-first 정책과 정합 (Rust 로컬 dev-feedback codify).
- 동행 도메인 fact: `docs/domain-knowledge/domain/build-toolchain/rust-local-build-equivalence.md` (R-1~R-5 — 본 개념의 Rust-구체 invariant 집합).
- carrier Story: CFP-2506 = 이 개념을 codeforge 스캐폴딩(consumer Rust 프로젝트)에 표준 경로로 추가. D1(컨테이너 마운트 빌드)·D2(build-local 스크립트)·D3(MSYS2 gcc/binutils 또는 WSL2) = 위 3 우회 경로의 구현체.

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2506 ResearcherAgent). 검증 권위 ↔ 빠른 피드백 분리 개념 정립. 기존 concept/ 자산에 Rust toolchain/컨테이너 빌드 주제 선행 부재 → 신규. 외부 사실 anchor(rustup MSVC default / windows-gnu MinGW 요구 / cargo check 링커-less / target dir 오염 / WSL2 fs 성능) 인용.
