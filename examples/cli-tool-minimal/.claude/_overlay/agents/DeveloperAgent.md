---
permissions:
  allow:
    - Edit(src/cli/**)
    - Write(src/cli/**)
    - Edit(src/parsers/**)
    - Write(src/parsers/**)
    - Edit(src/events/**)
    - Write(src/events/**)
    - Edit(src/filters/**)
    - Write(src/filters/**)
---

### 기술 스택 (Log Parser CLI)

- 언어: `<REPLACE: Python 3.11+ / Go 1.22+ / Rust stable / ...>`
- CLI 프레임워크: `<REPLACE: click 8.x / typer / clap 4.x / cobra / ...>`
- 로그 파싱: `<REPLACE: re 모듈 + pydantic / regex crate + serde / ...>`

### 주 소유 경로

- `src/cli/**` — 명령 정의·플래그 파싱·입출력 스트림 wiring
- `src/parsers/**` — Parser Profile 구현 (포맷별 규칙)
- `src/events/**` — Event 모델·직렬화 (JSON·CSV 출력)
- `src/filters/**` — Filter DSL 파서·evaluator

### CLI 관습

- 단일 명령 구조: `logparser parse <input> [--format <profile>] [--filter <expr>] [--output json|csv]`
- 표준 입력 지원: `<input>` 생략 시 stdin 처리
- 에러 메시지는 stderr, 결과는 stdout
- 종료 코드: 0 성공 / 1 파싱 실패 (부분 성공 포함) / 2 사용자 에러 (플래그·파일 누락) / 3 시스템 에러

### 도메인 제약 (DomainAgent와 정합)

- 스트리밍 처리 강제: 전체 입력 메모리 로드 금지. 라인 iterator 기반
- Event 직렬화는 `src/events/serializer.py` (또는 동등) 단일 지점 — 출력 포맷 변경 시 여기만 수정
- Filter DSL은 **순수 predicate** — I/O 호출 금지 (보안·재현성)
