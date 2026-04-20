---
name: mctrader 개발 에이전트 팀 구성
description: mctrader 프레임워크 개발을 위한 Claude Code 에이전트 팀 확정 구조
type: project
---

개발 에이전트 팀 구성이 확정됨 (2026-04-20).

```
User
 └── LeaderAgent
      ├── ArchitectAgent
      ├── CodeSeniorAgent
      │    ├── ImplementerAgent
      │    ├── RefactorAgent
      │    └── ReviewAgent
      └── InfraAgent
```

**Why:** 사용자가 초기 구조 잡기 단계에서 직접 조율이 필요하여 LeaderAgent 추가. Architect/CodeSenior/Infra 세 시니어가 합의하는 구조로 설계 결정의 품질 확보. CodeSenior 하위에 구현팀을 두어 extreme refactoring 강제화.

**How to apply:** 새 기능 요청 시 LeaderAgent가 범위 판단 → 필요시 세 시니어 합의 → CodeSenior가 하위 팀 위임. 인프라 솔루션 가능성은 InfraAgent가 항상 먼저 검토.
