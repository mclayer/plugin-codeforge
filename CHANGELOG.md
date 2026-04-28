# Changelog

`codeforge-design` plugin 릴리스 이력.

## [0.1.0] - 2026-04-29

### CFP-40 (codeforge ζ arc LAST) — Initial extraction (NEW)

codeforge ζ arc 마지막 lane plugin 추출 (parent §5.10). 7 agent + 2 templates (change-plan, adr).

### Added

- 7 agents 이전: ArchitectPLAgent, ArchitectAgent (chief author), CodebaseMapperAgent, RefactorAgent, SecurityArchitectAgent, TestContractArchitectAgent, DataMigrationArchitectAgent
- templates 이전: change-plan.md, adr.md
- docs/inter-plugin-contracts/design-output-v1.md (canonical)
- overlay/hooks/{regen-agents,session-start-deps-check}.sh
- README + CLAUDE.md

### Why

ζ arc §5.10: 가장 큰 표면 (5 deputies + chief + PL + 2 templates + Story §3/§7/§11 mirror + design review packet + FIX 재진입). Codex round 2 sequencing 권고 — 다른 5 plugin (review v2 + pmo + req + test + develop) 검증 후 마지막 진입으로 split-brain 위험 회피.

### Compatibility

- **Wire**: codeforge >= 5.0.0
- **Final extraction**: codeforge wrapper 가 본 PR 머지 후 agent 0개 (DocsAgent 동시 삭제) — wrapper-only 모델 완성
