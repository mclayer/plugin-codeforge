# Changelog

`codeforge-develop` plugin 릴리스 이력.

## 0.5.2 — 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113 Story frontmatter trust + CFP-123 Live touching gate + CFP-133 PR comment evidence + CFP-342 Phase 2 PR gate 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## 0.5.1 — 2026-05-12

- [CFP-448 sibling] DeveloperPLAgent model `claude-opus-4-7` → `claude-sonnet-4-6` PATCH
- ADR-042 Amendment 5 §결정 1 (b) + ADR-057 Amendment 3 정합
- Sibling PRs: design#34 (merged), wrapper#502 (merged)

## [0.4.0] - 2026-05-10

### Added
- presets/docker-compose.test.yml: 통합테스트 격리 환경 템플릿 신규 (CFP-367 / ADR-055) — 3-service(app/test-db/wiremock) ephemeral 구성, InfraEngineerAgent §8.6 사용

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
