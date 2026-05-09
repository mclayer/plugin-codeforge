---
story_key: <KEY>
story_scope: hub
status: draft
component: cross-repo
type: story
parent_epic: null
related_adrs: []
story_issues: []
delegates: []
depends_on: []
blocks: []
---

# <KEY>: <coordination title>

## Background

<문제, 사용자 의도, 비즈니스/도메인 이유. 구현 상세 없음.>

## Direction

<결정 경계, 원하는 결과, cross-repo 제약.>

## Delegation

| Repo | Story | Responsibility |
|---|---|---|
| <repo-1> | <repo-1>#<KEY> | <구현 책임> |
| <repo-2> | <repo-2>#<KEY> | <구현 책임> |

## Acceptance Gates

- [ ] 위임된 repo story 파일 존재 + 역링크 확인
- [ ] 필요한 ADR/change-plan 업데이트 식별
- [ ] Cross-repo contract 영향 검토

## Links

- Delegated: <repo-1>#<KEY>, <repo-2>#<KEY>
