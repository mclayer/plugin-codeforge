---
name: mctrader 개발 에이전트 팀 구성
description: mctrader 프레임워크 개발을 위한 Claude Code 에이전트 팀 확정 구조
type: project
---

개발 에이전트 팀 구성 확정 (2026-04-20, 구조 업데이트).

```
User
 └── LeaderAgent
      ├── DomainExpertAgent
      └── ArchitectAgent
           ├── CodeHeadAgent
           │    ├── DeveloperAgent
           │    ├── RefactorAgent
           │    └── ReviewAgent
           └── InfraHeadAgent
```

**Why:** ArchitectAgent가 기술 최종 의사결정권을 가지며, CodeHeadAgent와 InfraHeadAgent가 각 도메인의 헤드로 그 아래 위치. LeaderAgent는 사용자-기술팀 간 조율 전담.

**How to apply:** 새 기능 요청 시 LeaderAgent가 범위 판단 → ArchitectAgent 설계 주도 → CodeHead/InfraHead 검토 → CodeHead가 하위 팀 위임. 인프라 솔루션 가능성은 InfraHeadAgent가 항상 먼저 검토.
