# Changelog

`codeforge-test` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.1.0] - 2026-04-29

### CFP-38 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 네 번째 lane plugin (parent spec mclayer/plugin-codeforge CFP-31 §5.8). 가장 단순한 lane (TestAgent 1개 + owner doc 부재).

### Added

- `agents/TestAgent.md` — codeforge wrapper 에서 이전. self-write 권한 추가 (mcp__github__add_issue_comment, mcp__github__issue_write — phase comment + phase 전환)
- `docs/inter-plugin-contracts/test-verdict-v1.md` — canonical contract
- `overlay/hooks/{regen-agents,session-start-deps-check}.sh`
- README + CLAUDE.md

### Why

CFP-31 §5.8: TestAgent 1개 + owner doc 부재로 가장 단순한 lane 추출. Codex round 2 권고 sequencing (Sequence #4) 따름. 이전 3 plugin (review v2 + pmo + requirements) 검증 후 진입.

### Compatibility

- **Wire**: codeforge >= 3.0.0
- **Migration**: Story §10 FIX Ledger append 는 그대로 Orchestrator 단독. lane plugin 은 fix_routing_hint 만 verdict 에 첨부 (FAIL 시)
