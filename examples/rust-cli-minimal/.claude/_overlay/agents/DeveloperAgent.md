---
permissions:
  allow:
    - Edit(src/**)
    - Write(src/**)
    - Edit(Cargo.toml)
    - Write(Cargo.toml)
---

### 기술 스택 (Log Parser Rust CLI)

- 언어: Rust stable (edition 2021)
- CLI 프레임워크: `<REPLACE: clap 4.x / argh / 수동 std::env::args>`
- 로그 파싱: `<REPLACE: regex + serde / nom / 수동 split>`

### 주 소유 경로

- `src/main.rs`, `src/cli/**` — 명령 정의·플래그 파싱·입출력 스트림 wiring
- `src/parsers/**` — Parser Profile 구현 (포맷별 규칙)
- `src/events/**` — Event 모델·직렬화 (serde JSON·CSV 출력)
- `src/filters/**` — Filter DSL 파서·evaluator
- `Cargo.toml` — 의존성·bin target 정의

### CLI 관습

- 단일 명령 구조: `rust-cli-minimal parse <input> [--format <profile>] [--filter <expr>] [--output json|csv]`
- 표준 입력 지원: `<input>` 생략 시 stdin 처리
- 에러 메시지는 stderr, 결과는 stdout
- 종료 코드: 0 성공 / 1 파싱 실패(부분 성공 포함) / 2 사용자 에러(플래그·파일 누락) / 3 시스템 에러

### Rust 빌드 관습 (CFP-2506)

- 로컬 검증 1차 = **`cargo check`**(링커 불요). 완전빌드는 `templates/scripts/build-local.{sh,ps1}` 경유(Docker 마운트 또는 native). 상세 = consumer-guide §1q.
- 비-Copy 값(String/Vec 등)의 move-after-use 는 `cargo check` 가 E0382 로 즉시 검출 — 링커 없이 로컬에서 잡는다.
- 출력 직렬화는 단일 지점(`src/events/serializer.rs` 또는 동등) — 출력 포맷 변경 시 여기만 수정.

### 도메인 제약 (DomainAgent와 정합)

- 스트리밍 처리 강제: 전체 입력 메모리 로드 금지. `BufRead::lines()` iterator 기반.
- Filter DSL은 **순수 predicate** — I/O 호출 금지 (보안·재현성).
