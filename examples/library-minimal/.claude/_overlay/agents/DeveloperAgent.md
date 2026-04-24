---
permissions:
  allow:
    - Edit(src/**)
    - Write(src/**)
  deny:
    - Edit(pyproject.toml)
    - Write(pyproject.toml)
    - Edit(Cargo.toml)
    - Write(Cargo.toml)
    - Edit(package.json)
    - Write(package.json)
    - Edit(CHANGELOG.md)
    - Write(CHANGELOG.md)
---

### 기술 스택 (Schema Guard)

- 언어: `<REPLACE: Python 3.10+ / Rust stable / TypeScript / ...>`
- 타입 체크: `<REPLACE: pyright / mypy / tsc / rustc — ...>`
- 직렬화: `<REPLACE: pydantic / serde / zod / — ...>`

### 주 소유 경로

- `src/<lib>/public/**` 또는 `src/<lib>/__init__.py` — **공개 API surface** (semver 계약 대상)
- `src/<lib>/internal/**` — 내부 구현 (자유 리팩터링)
- `src/<lib>/types/**` — Schema·Result·Error 타입 정의
- `src/<lib>/validators/**` — Validator 구현체 (primitive·container·constraint)

### 금지 경로 (InfraEngineer 영역)

- `pyproject.toml` / `Cargo.toml` / `package.json` → InfraEngineerAgent (릴리스·의존성)
- `CHANGELOG.md` → InfraEngineerAgent + DocsAgent
- `tests/**` → QADeveloperAgent

### 공개 API 작업 원칙 (라이브러리 특화)

- **Breaking change → Change Plan §3에 API 영향 기재 필수** (어떤 이름·시그니처 변경인지, 영향받는 호출 패턴 예시)
- **Deprecation 경로**: 기존 API 제거 시 `deprecated` 데코레이터·attribute 먼저 추가 → 1 minor 뒤 제거
- **Surface 최소화**: 내부 타입·함수를 공개 네임스페이스에 노출 금지 — `__all__` / `pub(crate)` 등 활용
- **Result 반환 일관성**: 모든 공개 validator는 Result 타입 반환 (exception 대신) — 사용자가 실패 path를 structured로 처리 가능

### 도메인 제약 (DomainAgent와 정합)

- Validator는 **순수 함수** — 상태 공유·전역 변수 금지
- Error Path는 완전 수집 (첫 실패에서 중단 금지)
- Custom Rule은 사용자 제공 함수지만 I/O 금지는 문서 + 런타임 타입 힌트로 권고 (강제는 불가 — 라이브러리 경계)
