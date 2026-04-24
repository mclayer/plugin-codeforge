---
permissions:
  allow:
    - Edit(src/adapters/repositories/**)
    - Write(src/adapters/repositories/**)
    - Edit(migrations/**)
    - Write(migrations/**)
    - Edit(schemas/**)
    - Write(schemas/**)
---

### 기술 스택 (Task Manager)

- DBMS: `<REPLACE: PostgreSQL 15+ / MySQL 8+ / SQLite 3 / ...>`
- 마이그레이션: `<REPLACE: Alembic / Prisma Migrate / goose / ...>`
- ORM/쿼리: `<REPLACE: SQLAlchemy 2.0 / Prisma / sqlx / raw SQL / ...>`

### 주 소유 경로

- `src/adapters/repositories/**` — Task·Team·User 리포지토리 (DB 어댑터)
- `migrations/**` — 스키마 마이그레이션 파일
- `schemas/**` — 공유 스키마 정의 (JSON schema 또는 Protobuf)

### Task Manager 핵심 스키마

- `tasks (id PK, title, description, status, assignee_id FK, team_id FK, due_date, created_at, updated_at)`
- `teams (id PK, name, owner_id FK)`
- `team_members (team_id FK, user_id FK, role) — PK(team_id, user_id)`
- `users (id PK, email UNIQUE, name, hashed_password)`

### 불변 규약

- `tasks.team_id`와 `tasks.assignee_id` 는 `team_members` 에 실재해야 함 (FK + 트리거 또는 app-level 검증)
- `tasks.status` enum 값 외 insert 차단 (CHECK 제약 또는 domain enum)
- 스키마 변경은 **하위호환 유지** — breaking change 시 Change Plan에 migration 단계 명시 필수

### 기존 ADR (프로젝트 도입 시 채울 것)

- `<REPLACE: ADR-NNN: 저장소 선택 근거>`
- `<REPLACE: ADR-NNN: 마이그레이션 전략>`
