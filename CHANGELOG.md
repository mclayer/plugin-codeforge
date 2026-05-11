# Changelog

`codeforge-design` plugin 릴리스 이력.

## [0.7.0] - 2026-05-11

### CFP-387 / ADR-058 — ADR template sunset criteria + transitional 분류 frontmatter (MINOR)

Wrapper canonical ADR-058 (안전망 ADR 영구 부채화 차단) 의 cross-plugin Phase 2. ADR template canonical SSOT 갱신 — consumer-facing 의미 변경 → MINOR bump (ADR-037 룰).

### Added

- `templates/adr.md` frontmatter `is_transitional: true | false` 필드 (ADR-058 §결정 1 의무화) — 미선언 default `true` (안전망 추정, safe direction, §결정 4)
- `templates/adr.md` body `## 해소 기준` 섹션 (`## 결과` 직후 / `## 다이어그램 (선택)` 직전) — `is_transitional: true` 시 의무 / `false` 시 "N/A — permanent policy" 1줄
- 측정성 3-tuple (metric / who / how) 정량 명시 의무 — 모달 어휘 ("충분히 안정화되면", "임시로", "한시적", "until further notice") 금지
- frontmatter `amendments[]` schema — `sunset_justification` 필수 (ADR-058 §결정 5 ratchet 차단)
- 보안 ADR default presumption = `is_transitional: false` (ADR-058 §결정 7)
- 예시 3종 inline: (1) rate-limit 안전망 패턴 — ADR-057 fallback rate mirror / (2) platform SLA 발표 패턴 — 외부 신호 기반 / (3) full-rollout 완료 패턴 — 내부 milestone 기반

### Why

ADR-058 (wrapper canonical carrier, CFP-387) — 측정 기준 없는 영구 안전망 ADR 차단 forcing function. ADR-057 (Orchestrator Opus 필수화 + Sonnet→Opus fallback) 이 측정 기준 없는 영구 안전망으로 굳어지는 위험이 brainstorming (Opus×Codex 3라운드, 2026-05-11) 에서 식별 → 합의 원칙 5 "안전망 측정가능 종료" forcing function.

본 plugin = ADR template canonical SSOT — frontmatter + body schema 갱신 carrier.

### Compatibility

- **Wire**: codeforge >= 5.11.0 (sibling 동기 권장 — wrapper CLAUDE.md ADR 섹션 ADR-058 cross-ref 추가)
- **Template surface**: backward compatible — 기존 ADR 의 frontmatter 미선언 = default `true` 안전망 추정 (declaration only, mechanical enforcement 부재 = CFP-B 잠정 carrier)
- **Sibling sync**: wrapper repo `templates/adr.md` sibling 사본 0건 → canonical-only single source (ADR-010 sync 무발화)
- **Marketplace sync**: mirrored field 4종 (`name`/`version`/`description`/`author`) 중 `version` + `description` 변경 → marketplace sync PR 의무 (Phase 2 PR merge 직후, ADR-016)

### Cross-plugin coordination

- wrapper PR (Phase 2): `CLAUDE.md` ADR 섹션 + `plugin.json` 5.10.0 → 5.11.0 + `CHANGELOG.md`
- wrapper canonical ADR: `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` (Phase 1 PR #399 merged)
- Mode B hub-centralized (ADR-020 Amendment 1) — wrapper hub, codeforge-design worker plugin

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
