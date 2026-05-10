# Changelog

`codeforge-develop` plugin 릴리스 이력.

## [0.3.0] - 2026-05-10

### Changed
- InfraEngineerAgent: model claude-sonnet-4-6 → claude-haiku-4-5 (ADR-042 Amendment 2, mechanical pattern execution)
- QADeveloperAgent: model claude-sonnet-4-6 → claude-haiku-4-5 (ADR-042 Amendment 2)
- DataEngineerAgent: model claude-sonnet-4-6 → claude-haiku-4-5 (ADR-042 Amendment 2)

## [0.2.0] - 2026-05-07

### CFP-128 / ADR-033 — InfraEngineer Docker-first mandate + presets/k8s/ (MINOR)

#### Added

- InfraEngineer mandate Docker-first 재작성 (D1 sibling sync PR #8, commit b6bda7c)
- `presets/k8s/` NEW directory (Kubernetes preset)

#### Why

ADR-033 (wrapper canonical) — InfraEngineer 의 backing mandate 를 Docker-first 로 확정 + Kubernetes preset 도입. CFP-128 marketplace mirror prep 의 일환으로 minor bump.

#### Compatibility

- **Wire**: codeforge >= 4.0.0

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
