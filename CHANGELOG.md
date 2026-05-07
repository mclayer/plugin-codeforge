# Changelog

`codeforge-design` plugin 릴리스 이력.

## [0.4.0] - 2026-05-07

### CFP-128 / ADR-033 — Docker-first infra mandate sync (MINOR)

Wrapper canonical ADR-033 (amends ADR-014) 의 sibling sync. OpRiskArch agent + design-output-v2 contract 갱신.

### Added

- `agents/OperationalRiskArchitectAgent.md` §7.4.6 Container considerations (Docker-first infra orientation; deputy mandate 추가)
- `docs/inter-plugin-contracts/design-output-v2.md` `contract_version: 2.1 → 2.2` (additive minor — Container considerations field)

### Why

ADR-033 (CFP-128 carrier, wrapper canonical) — Docker-first infra orientation 을 OpRiskArch deputy mandate 에 명시 + design-output-v2 contract 에 surface. ADR-014 (OpRisk SSOT distribution) 의 amendment.

### Compatibility

- **Wire**: codeforge >= 5.0.0 (no break)
- **Contract version**: design-output-v2 2.1 → 2.2 (additive minor — backward compatible)
- **Sibling sync**: D2 PR #21 (commit fcf1666) merged

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
