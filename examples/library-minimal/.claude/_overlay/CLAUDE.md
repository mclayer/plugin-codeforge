# <REPLACE: 프로젝트명> — Consumer Overlay

이 프로젝트는 **Schema Guard** 라이브러리 — 데이터(dict/struct/JSON)를 스키마에 대해 검증하고 구조화된 에러를 반환. `dev-orchestrator` 플러그인 사용.

> 위 core CLAUDE.md §(org chart)에서 "구현 레인의 `role: dev` roster"는 이 프로젝트에서 core의 `DeveloperAgent` + `InfraEngineerAgent`만으로 구성. `DataEngineerAgent`·preset은 미사용. Frontend 없음.

## SSOT 상수

Atlassian·GitHub·labels는 [`project.yaml`](project.yaml). 아래는 narrative 컨텍스트만.

## 기술 스택

- 언어: `<REPLACE: Python 3.10+ / Rust stable / TypeScript / Go / Java 17+ / ...>`
- 패키지 매니저: `<REPLACE: pyproject.toml (uv / poetry / setuptools) / Cargo / npm / Maven / Gradle / ...>`
- 테스트: `<REPLACE: pytest + hypothesis / cargo test / jest + fast-check / JUnit 5 / ...>`
- 타입 체크 (선택): `<REPLACE: pyright / mypy / tsc / — (compiled lang)>`

## 도메인 용어 사전 (요약)

- **Schema**: 데이터 구조·제약을 선언적으로 기술한 정의 `{type, required, fields, constraints}`
- **Validator**: Schema + Data → `Result` (OK 또는 구조화 Error)
- **Error Path**: 실패 지점의 JSON Pointer 유사 경로 (예: `.users[3].email`)
- **Custom Rule**: 사용자 정의 제약 함수 — 순수 predicate만 허용 (부작용 금지)

자세한 도메인·API 안정성 원칙은 `.claude/_overlay/agents/DomainAgent.md`.

## 경로 관습 (라이브러리 특화)

- `src/<lib>/__init__.py` 또는 `src/<lib>/public/**` — **공개 API surface** (semver 계약)
- `src/<lib>/internal/**` — 내부 구현 (자유 리팩터링)
- `src/<lib>/types/**` — 타입 정의·Result·Error 모델
- `pyproject.toml` / `Cargo.toml` / `package.json` — 패키지 매니페스트 (InfraEngineerAgent)
- `CHANGELOG.md` — 릴리스 이력 (InfraEngineerAgent + DocsAgent)
- `docs/**` — API reference·예시·tutorial (DocsAgent)
- `tests/**` — property-based + unit (QADev)

## 공개 API 안정성 원칙

- **semver 엄수**: breaking change는 major bump 필수. Change Plan §3에 "API 영향"을 먼저 평가.
- **Deprecation 경로**: 제거 전 최소 1 minor 버전에서 deprecated 경고 → 다음 major에서 제거.
- **Surface 최소화**: 내부 구현 노출 금지 — `__all__` 또는 `pub` 엄격 관리.

## TestAgent 러너

- 기능: `<REPLACE: pytest -q tests/unit tests/property>`
- 성능: `<REPLACE: pytest-benchmark tests/perf>` (큰 schema/data 벤치마크)
- baseline: `<REPLACE: tests/perf/baselines/>`
