# mctrader 문서

작업 산출물(요건 명세서, 변경 계획서) 및 설계 문서(superpowers specs/plans)를 관리한다.

도메인 문서(ADR, 운영 가이드, 외부 API 스펙, 버그 이력)는 외부 시스템으로 이관되어 있다:
- **ADR**: [Confluence space `MCTRADER`](https://mctrader.atlassian.net/wiki/spaces/MCTRADER) / 페이지 트리 `ADR/<카테고리>/ADR-NNN: ...`
- **운영 가이드 · API 스펙**: Confluence `MCTRADER` / `Guides`, `API Reference` 트리
- **버그 기록**: [Jira project `MCTRADER`](https://mctrader.atlassian.net/jira/software/projects/MCTRADER) / `bug` label Task

## 구조

| 디렉토리 | 내용 |
|----------|------|
| `requirements/` | PMOAgent가 작성한 통합 요건 명세서 |
| `change-plans/` | ArchitectAgent가 작성한 변경 계획서 (PR과 1:1 매핑) |
| `superpowers/specs/` | 설계 문서 (brainstorming 산출물) |
| `superpowers/plans/` | 구현 계획서 (writing-plans 산출물) |
