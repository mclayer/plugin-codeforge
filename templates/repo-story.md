---
story_key: <KEY>
story_scope: repo
repo: <repo-name>
hub_story: <HUB-KEY> | null
hub_repo: <hub-repo-name> | null
status: draft
component: <component>
type: story
parent_epic: null
related_adrs: []
story_issues: []
---

# <KEY>: <implementation title>

## Background

<Repo-local 문제 설명 + hub direction 링크.>

## Implementation Scope

<변경 대상 파일/모듈/서비스.>

## Technical Design

<구현 상세.>

## Acceptance Criteria

- [ ] <Repo-local 동작>
- [ ] <테스트>
- [ ] <Docs/config 업데이트>

## Test Plan

<커맨드, fixture, integration coverage.>

## Links

- Hub: <hub-repo-name>#<HUB-KEY>
- ADRs: <ADR-NNN>, ...
