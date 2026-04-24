# <REPLACE: 프로젝트명> — Consumer Overlay

이 프로젝트는 **Log Parser** CLI 툴 (로그 파일 → 구조화 이벤트 추출 → JSON/CSV 출력). `dev-orchestrator` 플러그인을 사용.

> 위 core CLAUDE.md §(org chart)에서 "구현 레인의 `role: dev` roster"는 이 프로젝트에서 core의 `DeveloperAgent` + `InfraEngineerAgent`만으로 구성한다. `DataEngineerAgent`·webapp preset은 **미사용**. Frontend 계층 없음.

## 프로젝트 상수 (SSOT)

### Atlassian
- Confluence space: `<REPLACE: SPACE_KEY>` (예: `LP`)
- Stories parent pageId: `<REPLACE: Stories 루트 pageId>`
- Domain Knowledge parent pageId: `<REPLACE: DK 루트 pageId>`
- ADR 루트 pageId: `<REPLACE: ADR 루트 pageId>`
- Jira project key: `<REPLACE: PROJECT_KEY>` (예: `LP`)

### GitHub
- Repo: `<REPLACE: github.com/owner/repo>`
- PR 제목 prefix: `[LP-N] ...`

## 기술 스택

- 언어: `<REPLACE: Python / Go / Rust / Node.js / ...>`
- CLI 프레임워크: `<REPLACE: click / typer / clap / cobra / commander / ...>`
- 로그 파싱: `<REPLACE: regex / structlog / 정규식 + 수동 파서 / ...>`
- 출력: `<REPLACE: JSON / CSV / Parquet / stdout 스트림>`
- 테스트: `<REPLACE: pytest / go test / cargo test / ...>`
- 패키징: `<REPLACE: pyproject.toml + twine / cargo publish / goreleaser / ...>`

## 도메인 용어 사전 (요약)

- **Log Line**: 원시 로그 텍스트 한 줄
- **Event**: Log Line에서 추출된 구조화 레코드 `{timestamp, level, message, fields...}`
- **Parser Profile**: 특정 로그 포맷(nginx / syslog / JSON lines 등)을 파싱하는 규칙 셋
- **Filter**: Event 스트림에서 조건에 맞는 것만 통과시키는 predicate

자세한 용어·제약은 `.claude/_overlay/agents/DomainAgent.md`.

## 경로 관습

- `src/cli/**` — CLI 명령·플래그·입출력 (DeveloperAgent)
- `src/parsers/**` — Parser Profile 구현 (DeveloperAgent)
- `src/events/**` — Event 모델·직렬화 (DeveloperAgent)
- `src/filters/**` — Filter DSL·evaluator (DeveloperAgent)
- `deploy/**`, `config/**`, `scripts/**` — 릴리스·배포 스크립트 (InfraEngineerAgent)
- `tests/**` — 테스트 (QADev)

## TestAgent 러너

- 기능: `<REPLACE: pytest -q tests/unit tests/integration>`
- 성능: `<REPLACE: pytest-benchmark tests/perf>` (대용량 로그 파싱 처리율 측정)
- baseline: `<REPLACE: tests/perf/baselines/>`

## Labels 추가 (component:*)

- `component:cli` — 명령·인자 처리
- `component:parser` — 로그 파싱 엔진
- `component:filter` — Event 필터링
- `component:infra` — 패키징·릴리스
