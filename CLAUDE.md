# CLAUDE.md (codeforge-pmo)

codeforge ζ arc PMO lane plugin. PMOAgent 가 codeforge core 의 Orchestrator 에 의해 스폰되어 Cross-cutting 책임 수행 — 단일 lane gate 에 무관.

## Plugin position

본 plugin 은 codeforge wrapper 의 dependency. 단독 동작 불가 — codeforge core (>= 1.0.0) 가 Orchestrator + Story file lifecycle + GitHub workflow CI 보유.

설치 + 의존성 + architecture 는 [`README.md`](README.md) 참조.

## Inter-plugin contracts

- `pmo_output v1` — [`docs/inter-plugin-contracts/pmo-output-v1.md`](docs/inter-plugin-contracts/pmo-output-v1.md) (canonical SSOT)
- codeforge wrapper 측 sibling reference: `mclayer/plugin-codeforge/docs/inter-plugin-contracts/pmo-output-v1.md`

## Self-write 책임 (CFP-36 ζ arc 패턴)

PMOAgent 가 다음을 직접 write:

| Path | 트리거 | Mechanism |
|---|---|---|
| `docs/retros/<sprint>.md` | story_completion / cross_story_audit_request | `Edit(docs/retros/**)` |
| `docs/stories/<KEY>.md §11` | story_completion | `Edit(docs/stories/**)` |
| Epic GitHub milestone | epic_creation / story_completion | `gh api repos/*/milestones*` |
| GitHub comment `[PMO]` prefix | 모든 trigger | `mcp__github__add_issue_comment` |

DocsAgent 경유 안 함 — codeforge wrapper 측 DocsAgent 는 ζ arc 진행 중 단계적 해체. 자세한 사항은 codeforge wrapper [CFP-31 parent spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) 참조.

## Cross-Story patterns 입력 → ADR 발의 hand-off

PMOAgent 가 cross_story_audit_request 트리거에서 cross-Story 패턴 (FIX 반복·ESCALATE 트렌드·성능 회귀·코드 핫스팟) 발견 시:
- `pmo_output v1.adr_proposal` 필드에 ADR 후보 (status: Proposed) 발의
- Orchestrator 가 codeforge-design plugin (CFP-40 후) 또는 codeforge wrapper 의 ArchitectAgent 에 hand-off
- 본 plugin 은 ADR file 직접 write 안 함 — 발의만
