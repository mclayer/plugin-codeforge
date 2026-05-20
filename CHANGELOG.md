# Changelog

`codeforge-design` plugin 릴리스 이력.

## [0.13.0] - 2026-05-20

### Added (CFP-684 / Epic CFP-1026 S3 — design lane agent 구조 재편 atomic activation)

본 release = wrapper SSOT (CFP-676 S1 `abcd92bf` + CFP-681 S2 `6f54c646` merged) 의 codeforge-design plugin repo cross-repo sibling 반영. doc-only fast-path (ADR-054 §결정 1/3 — 4 조건 satisfy, src/tests 부재).

#### agent file 5종 (rename 2 + 신설 3)

- **`agents/DataArchitectAgent.md`** (신설) — DataMigrationArchitectAgent rename + mandate 확장 (§3 data + §11 전체 데이터 구조: entity / aggregate / value object / DB schema / event schema / DTO / API contract data / persistence model / 데이터 흐름 + schema 진화 + migration + rollback + integrity invariant). Opus 유지 (ADR-042 Amd7 §결정 1 (d) + 결정 4 inheritance).
- **`agents/InfraOperationalArchitectAgent.md`** (신설) — OperationalRiskArchitectAgent rename. mandate scope **무변경** invariant (§7.4 DR / Cancel-on-disconnect / Clock sync / Rate limit / Env isolation / Container considerations — ADR-014 Amd4 verbatim). ADR-72 ProductionEvidence ↔ InfraOperational disjoint axis (policy SSOT axis vs evidence SSOT axis) 명시. Opus inherit.
- **`agents/CodeArchitectAgent.md`** (신설) — 5번째 permanent deputy. §3 code single-mandate advocacy (layered / hexagonal / clean / DDD bounded context / module boundary / dependency direction). Sonnet (`claude-sonnet-4-6` explicit, ADR-042 Amd7 §결정 1 (a) single-mandate advocacy).
- **`agents/ArchitectAnalystAgent.md`** (신설) — 4-tuple sub-tuple component (chief author 포함, deputy 아님). 변경 전 기존 설계 (ADR / Change Plan / Story §3/§7/§11) 분석 단일 축. Sonnet. PriorArtAgent **conceptual rename only** (실제 file move 0, `PriorArtAgent.md` 부재 verified — gh api direct list).
- **`agents/ProductionEvidenceDeputyAgent.md`** (신설) — 5번째 deputy 영역 file (CONDITIONAL production cutover Story 만, ADR-72). production evidence quad (functional / security / monitoring / testing 4 source) + EPIC CLOSED gate + post-cutover wiring + Family 7 atomic canary pin. wrapper-self-app N/A (ADR-72 §결정 6). Opus inherit.

#### agent file deletion (rename source)

- `agents/DataMigrationArchitectAgent.md` (→ DataArchitectAgent.md rename)
- `agents/OperationalRiskArchitectAgent.md` (→ InfraOperationalArchitectAgent.md rename)

#### Changed

- **`CLAUDE.md`**: "6 permanent + 2 CONDITIONAL" → **"5 permanent + 3 CONDITIONAL + 4-tuple sub-tuple"** wrapper SSOT 와 byte-consistent 재작성 (deputy 매트릭스 + Sub-agent fan-out + ArchitectPL prompt + 4-tuple sub-tuple 단락 신설 + InfraArchitect 신설 철회 명문화).
- **`docs/architecture/codeforge-design.md`**: CFP-969 living arch doc — deputy 5+3 + 4-tuple sub-tuple 반영 (ADR-078 §결정 1 4 영역 갱신: 모듈 / 경계 / 인터페이스 계약 / 데이터 흐름). InfraOperationalArch ↔ ProductionEvidence disjoint axis 명시.
- **`.claude-plugin/plugin.json`**: 0.12.1 → **0.13.0** MINOR (ADR-037 agent 신설/rename = MINOR). description 갱신 (5 permanent + 3 CONDITIONAL + 4-tuple sub-tuple roster 반영).

#### Related ADRs

- **ADR-042 Amendment 7** (CFP-676 / S1 — design lane agent model tier SSOT) — DataMigrationArch → DataArch rename + Opus 유지 / OperationalRiskArch → InfraOperationalArch rename + Opus 유지 / CodeArchitect + ArchitectAnalyst Sonnet 신설 / InfraArchitect 신설 철회.
- **ADR-014 Amendment 4** (CFP-676 / S1 — OperationalRiskArch → InfraOperationalArch rename + §7.4 primary/shell 분류 + ProductionEvidence dual-spawn disjoint axis).
- **ADR-72** (ProductionEvidenceDeputy + Epic cutover gate) — CONDITIONAL deputy 3번째 (production cutover Story 만, wrapper-self-app N/A).
- **ADR-044** (Phase-scoped sequential team SSOT) — 4-tuple sub-tuple flat spawn / nested team 금지 / 재귀 spawn 금지 / sub-lead 격상 0건 (CFP-676 reaffirm 단락).
- **ADR-054** (doc-only Story fast-path 분류 표) — 본 Story 4 조건 명확 satisfy carrier.
- **ADR-037** (plugin version bump rule) — agent 신설/rename = MINOR bump.
- **ADR-063** (Marketplace ↔ plugin.json atomic invariant) — marketplace.json mirrored field 4종 sibling sync 동반 (별도 cross-repo PR).
- **ADR-016** (Marketplace registration policy) — codeforge family 7 plugin 모두 등록.

#### Marketplace sibling sync (별도 cross-repo PR)

- `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge-design]` mirrored field 4종 (name / version / description / author) sync. ADR-063 atomic invariant. Orchestrator monopoly.

## [0.12.1] - 2026-05-16

### Changed (CFP-751 Phase 2 sibling — deputy 일반 명사 → SubAgent sweep, ADR-010 paired sync)

- **13 file / 142 mechanical replacements** — `docs/**` + `CLAUDE.md` + `agents/**` + `templates/**` 영역의 lowercase 일반 명사 `deputy` → `SubAgent`. wrapper carrier `mclayer/plugin-codeforge` Phase 2 PR ADR-080 §결정 1-2 sibling sync (ADR-010 §결정 2 paired ordering).
- **Class-B 보존 verified** — 6 `*DeputyAgent` cross-refs (LiveOpsDeputyAgent / LiveOrderingDeputyAgent CamelCase identifiers + filename preservation) / 17 `Deputy` capitalized concept. agent files (`agents/*DeputyAgent.md`) 본문 lowercase 일반 명사만 swept, identifier 0 변경.
- **`.claude-plugin/plugin.json`** — 0.12.0 → 0.12.1 PATCH (doc-only mirror sync — ADR-037 PATCH 결정). marketplace atomic sync 동반 (ADR-063).

## [0.12.0] - 2026-05-14

### Added

- `design-output-v2` contract v2.2 → v2.3 MINOR — `chief_author_artifact.spec_invariant_measurement_required: bool` field 신설 (CFP-662 / Issue mclayer/plugin-codeforge#669, Epic CFP-620 sibling, codeforge-develop PR #25 canonical 정합, doc-only fast-path ADR-054).

## [0.11.0] - 2026-05-13

### CFP-582 — ADR-059 Amendment 2 / debate-protocol-v1 v1.2 sibling sync — Blanket Adversarial Debate Trigger (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge CFP-582 — Wave 4 ADR-059 Amendment 2) 의 canonical sibling sync. DesignLane cross-module Story 진입 시 adversarial debate 자동 발동.

### CFP-597 — ArchitectAgent §5.7 marketplace sync proactive self-check trigger (ADR-063 Amendment 1)

ArchitectAgent Phase 1 산출물 commit 직전 plugin.json mirrored field diff 감지 + Change Plan §13 declarative declare 의무화. review-verdict-v4 v4.5 `marketplace_sync_declared` optional bool field 정합.

#### Changed (CFP-582)
