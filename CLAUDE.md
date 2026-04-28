# CLAUDE.md (codeforge-develop)

codeforge ζ arc Develop lane plugin. 5 agent + presets/webapp.

## Plugin position

codeforge core (>= 4.0.0) 의존.

## Inter-plugin contracts

- `develop_output v1` — [`docs/inter-plugin-contracts/develop-output-v1.md`](docs/inter-plugin-contracts/develop-output-v1.md)

## Self-write 책임

| Path | 책임 agent | Mechanism |
|---|---|---|
| `docs/stories/<KEY>.md §8` | DeveloperPLAgent | Edit |
| `docs/stories/<KEY>.md §8.5` | DeveloperPLAgent | Edit |
| Phase 2 PR | DeveloperPLAgent | mcp__github__create_pull_request |
| GitHub comment `[구현]` prefix | DeveloperPLAgent | mcp__github__add_issue_comment |
| `phase:구현` → `phase:구현-리뷰` | DeveloperPLAgent | mcp__github__issue_write |

## Role:dev roster 동적 discovery

DeveloperPLAgent 가 다음 source 에서 frontmatter `role: dev` 매칭:
- 본 plugin agents/* (3 core + QADev)
- presets/<active>/agents/*
- consumer overlay `.claude/_overlay/agents/*`

매칭된 agent 들을 의존성 없는 한 모두 병렬 spawn (한 메시지). 상세는 codeforge wrapper CLAUDE.md "스폰 시퀀스" 참조.
