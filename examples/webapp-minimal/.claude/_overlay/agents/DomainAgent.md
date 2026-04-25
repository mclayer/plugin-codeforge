### 도메인 소스 (Task Manager)

- Domain Knowledge: `docs/domain-knowledge/task/**`
- ADR 카테고리 (frontmatter `category:`): `domain-task`
- 도메인 코드: `src/domain/**`
- 도메인 용어: Task, Assignee, Team, Status, Priority, DueDate

### 핵심 개념

| 용어 | 정의 | 주요 invariant |
|------|------|----------------|
| **Task** | 완료해야 할 작업 단위 | id 불변, status transition은 valid transition table 준수 |
| **Assignee** | Task 소유 사용자 | Task 생성 시 팀 멤버만 assignee 가능 |
| **Team** | 프로젝트 공유 사용자 그룹 | 최소 1명의 admin 필수 |
| **Status** | Task 진행 상태 | `backlog → in_progress → done` / `any → cancelled` |
| **Priority** | Task 중요도 | `low | medium | high | urgent` |
| **DueDate** | Task 마감일 | 과거 날짜 설정 불가 (경고만) |

### 우선순위 원칙

- **데이터 무결성 최우선**: Task·Team 삭제 시 관련 레코드 cascade 검증
- **사용자 프라이버시**: Assignee 외 다른 팀의 task 조회 불가 (RLS 또는 ORM scope)
- **성능 목표**: Task 목록 조회 p95 < 300ms (100 task 기준)

### 금지 사항

- Task status 역방향 전이 (`done → in_progress`) 허용 금지 — 별도 `reopen` flow 통해서만
- Team admin 0명 상태 방지 (admin 해제 시 대체 admin 지정 강제)
