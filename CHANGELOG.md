# Changelog

`codeforge-develop` plugin 릴리스 이력.

## [0.1.0] - 2026-04-29

### CFP-39 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 다섯 번째 lane plugin (parent §5.9).

### Added

- 5 agents 이전: DeveloperPLAgent, QADeveloperAgent, DeveloperAgent, DataEngineerAgent, InfraEngineerAgent
- presets/{webapp,README.md} 이전 (BackendDeveloperAgent, FrontendDeveloperAgent)
- docs/inter-plugin-contracts/develop-output-v1.md (canonical)
- overlay/hooks/{regen-agents,session-start-deps-check}.sh
- README + CLAUDE.md

### Why

ζ arc §5.9: DeveloperPL이 role:dev roster 동적 discover. 5 agent + presets 가 함께 이전. CFP-31 §3.5 거부 (overlay 충분 권고)는 wrapper-only end-state 와 충돌이라 폐기.

### Compatibility

- **Wire**: codeforge >= 4.0.0
