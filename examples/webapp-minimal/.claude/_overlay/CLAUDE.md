# <REPLACE: 프로젝트명> — Consumer Overlay

이 프로젝트는 **Task Manager** 도메인 웹 애플리케이션 (할 일·담당자·팀 관리). `dev-orchestrator` 플러그인을 사용해 요구사항부터 보안 테스트까지 자율 실행.

> 위 core CLAUDE.md §(org chart)에서 "구현 레인의 `role: dev` roster"는 이 프로젝트에서 webapp preset (BackendDev + FrontendDev) + core DataEng + InfraEng으로 구성한다. Core의 generic `DeveloperAgent`는 비활성화 (Backend/Frontend로 충분).

## 프로젝트 상수 (SSOT)

### Atlassian
- Confluence space: `<REPLACE: SPACE_KEY>` (예: `TM`)
- Stories parent pageId: `<REPLACE: Stories 루트 pageId>`
- Domain Knowledge parent pageId: `<REPLACE: DK 루트 pageId>`
- ADR 루트 pageId: `<REPLACE: ADR 루트 pageId>`
- Jira project key: `<REPLACE: PROJECT_KEY>` (예: `TM`)
- Jira transition IDs: DocsAgent가 `getTransitionsForJiraIssue`로 동적 획득 (고정 매핑 필요 시 아래 추가)

### GitHub
- Repo: `<REPLACE: github.com/owner/repo>`
- PR 제목 prefix: `[TM-N] ...`

## 기술 스택

- 언어: `<REPLACE: Python / Node.js / Go / ...>`
- 백엔드 프레임워크: `<REPLACE: FastAPI / Flask / Express / Rails / ...>`
- 프론트엔드 템플릿: `<REPLACE: Jinja2 / React / Vue / Svelte / ...>`
- 저장소: `<REPLACE: PostgreSQL / MySQL / SQLite / ...>`
- ORM/쿼리: `<REPLACE: SQLAlchemy / Prisma / sqlx / ...>`
- 테스트: `<REPLACE: pytest / vitest / jest / ...>`
- 배포: `<REPLACE: Docker + K8s / systemd / Heroku / Fly.io / ...>`

## 도메인 용어 사전 (요약)

- **Task**: 사용자가 완료해야 할 작업 단위. `{id, title, description, status, assignee, due_date, team_id}`
- **Assignee**: Task를 할당받은 사용자
- **Team**: 공통 프로젝트를 공유하는 사용자 그룹
- **Status**: `backlog | in_progress | done | cancelled`

자세한 용어·제약은 `.claude/_overlay/agents/DomainAgent.md` 참조.

## 경로 관습

- `src/api/**` — REST 라우트·dependency injection (BackendDev)
- `src/domain/**` — 도메인 로직·엔티티 (BackendDev)
- `src/adapters/repositories/**` — DB 어댑터 (DataEng)
- `src/adapters/auth/**` — 외부 인증 어댑터 (BackendDev)
- `src/templates/**`, `src/static/**` — UI 자산 (FrontendDev)
- `migrations/**` — DB 마이그레이션 (DataEng)
- `deploy/**`, `config/**`, `scripts/**` — 인프라 자산 (InfraEng)
- `tests/**` — 전 분야 테스트 (QADev)

## TestAgent 러너

- 기능: `<REPLACE: pytest -q tests/unit tests/integration>`
- 성능: `<REPLACE: pytest-benchmark tests/perf --benchmark-json=out.json>`
- baseline: `<REPLACE: tests/perf/baselines/>`

## Labels 추가 (component:*)

- `component:api` — 백엔드 라우트·비즈니스 로직
- `component:ui` — 템플릿·정적 자산
- `component:data` — DB·마이그레이션·스키마
- `component:infra` — 배포·설정·CI
