# Changelog

`codeforge-design` plugin 릴리스 이력.

## [0.16.0] - 2026-05-20

### Changed (CFP-1086 Story-3 (Wave 2) — CLAUDE.md RACI 4-way overlap zone section mirror codify)

본 release = wrapper SSOT (CFP-1086 Story-3 — deputy-mandate skill RACI body 4-way overlap zone codify carrier) 의 codeforge-design plugin repo cross-repo sibling 반영. doc-only fast-path (ADR-054 Category 2 — CLAUDE.md section mirror, agent file / ADR / src / tests 변경 0). Story-1 = 7+3+1 roster 신설 + 4-way 이념 대립 영역 분리. Story-2 = APIContractArch mandate body 심화. Story-3 (본 release) = RACI 4-way 12-cell matrix mirror.

#### Changed

- **`CLAUDE.md`** — `## RACI 4-way overlap zone (CFP-1086 Story-3 — wrapper SSOT mirror)` 신규 단락:
  - wrapper canonical SSOT cross-ref ([`skills/deputy-mandate/SKILL.md`](https://github.com/mclayer/plugin-codeforge/blob/main/skills/deputy-mandate/SKILL.md) `## RACI 표준 row 형식 (Story-3 — 4-way overlap zone body)`)
  - 12-cell summary table (3 sub-axis Security / InfraOp / TestContract × 4 cross-axis Aggregate / Data OLAP / Module / APIContract) 의 R/C/I 1-row summary (각 Cell detail = wrapper skill 참조)
  - Cell 3.4 예외 명시 (R=APIContractArch primary §8.6 contract testing primary axis 정합, C=TestContractArch CI placement + orchestration disjoint axis — CFP-1086 §7+3+1 primary axis matrix row 정합)
  - 4-column 열 정의 (R primary 결정권자 / A=ArchitectAgent chief tie-break ladder 3단계 / C co-author 양방향 dialog / I 일방향 통지)
  - Cell selection heuristic 4-step (single-axis primary lookup / 2-axis overlap RACI 활성 / R+C 합의 부재 → ladder 2단계 / 미해소 → ladder 3단계)
  - Related ADRs (ADR-068 Amendment 2 + ADR-086 + review-verdict-v4 v4.6)
- **`.claude-plugin/plugin.json`**: 0.15.0 → **0.16.0** MINOR (ADR-037 — CLAUDE.md section 신규 추가 + cross-repo sibling carrier governance behavior change). description 갱신 (Story-3 RACI 4-way overlap zone mirror entry 추가).

#### Related ADRs

- ADR-042 Amendment 8 (CFP-1086 Story-1 carrier — 7+3+1 roster, RACI matrix axis 입력)
- ADR-068 Amendment 2 (CFP-1086 Story-1 sibling carrier — chief tie-break ladder 3 단계 1단계 RACI lookup SSOT, 본 mirror = ladder 1단계 entry point)
- ADR-086 (CFP-1086 Story-1 sibling 신설 carrier — Deputy 신설 결정 framework P7)
- ADR-058 §결정 5 (top-down ratchet 정합, additive only)
- ADR-064 §결정 7 (decision principle mandate top-down ratchet)
- ADR-054 (doc-only fast-path Category 2 — CLAUDE.md section mirror)

#### Marketplace sibling sync (Orchestrator 영역, 별도 cross-repo PR)

- `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge-design]` mirrored field 4종 (name / version / description / author) sync. ADR-063 atomic invariant.

## [0.15.0] - 2026-05-20

### Changed (CFP-1086 Story-2 — APIContractArchitectAgent mandate body 심화 codify, S1 skeleton 위 body 작성)

본 release = wrapper SSOT (CFP-1086 Story-2 — APIContractArch mandate body 심화 carrier) 의 codeforge-design plugin repo cross-repo sibling 반영. doc-only fast-path (ADR-054 Category 2 — agent file body 확장, ADR / src / tests 변경 0). Story-1 (carrier) = 신설 declaration + frontmatter + skeleton. Story-2 (본 release) = 5 mandate 영역 full body + Out of scope 강화 + 적극적 이의 제기 12 사유 + cross-ref 강화.

#### Changed

- **`agents/APIContractArchitectAgent.md`** (body 심화 — frontmatter 무변경 invariant) — 5 mandate 영역 full body codify:
  - **§1 Transport semantics** — REST (9 사항: HTTP verb idempotency / status code / Richardson Maturity Model 4-level / HATEOAS / content negotiation / cache / pagination / HTTP/2+3) / GraphQL (7 사항: Query/Mutation/Subscription axis / N+1 mitigation DataLoader / persisted queries / federation vs schema stitching / error handling / schema evolution / introspection control) / gRPC (6 사항: ProtoBuf schema / 4 RPC types / deadline propagation / interceptors / status codes / service mesh) / WebSocket (6 사항: connection lifecycle / heartbeat / reconnect strategy / subprotocol negotiation / message framing / authentication) + 5 axis × 4 transport decision matrix (latency / payload / streaming / client diversity / caching) + polyglot avoidance rationale.
  - **§2 API versioning** — 3-axis (URI / Header negotiation / Query parameter) pros·cons table + semver alignment (MAJOR / MINOR / PATCH) ADR-008 정합 + deprecation policy (N-1 parallel support window + Sunset header RFC 8594 + Link header RFC 8288 + migration guide) + GraphQL versioning special (additive only + `@deprecated` directive + persisted query 의 version 관리) + breaking change communication (changelog + migration script + soft launch 4-phase).
  - **§3 DTO contract** — Shape definition 4 format (JSON Schema / OpenAPI Schema Object / Protobuf / GraphQL type) + nullable vs optional vs required 4 상태 distinction (required+non-null / required+nullable / optional+non-null / optional+nullable) + validation rule 9 primitive (type / format / min·max / pattern / enum / const / multipleOf / required[] / dependentRequired) + validation library matrix (Zod / Joi / Pydantic v2 / jakarta-validation / go-playground/validator / FluentValidation) + RFC 7807 error contract (`application/problem+json` 5 표준 field type/title/status/detail/instance + extension members) + DTO mapping policy (domain entity ↔ DTO assembler = AggregateArch ↔ APIContractArch co-author boundary `R(AggregateArch primary persistence schema) + R(APIContractArch primary DTO shape)`).
  - **§4 OpenAPI / GraphQL schema** — OpenAPI (3.0 vs 3.1 nullable 표현 차이 / code-first vs spec-first decision table + recommended default / spec-first workflow 4-step / tooling: openapi-generator / swagger-codegen / Speakeasy / Fern / orval / validation: Spectral / dredd / Schemathesis) + GraphQL (SDL 표준 sample / schema-first vs code-first decision table + recommended default = code-first / introspection control / tooling: graphql-codegen / Apollo Server / Yoga / Pothos / Nexus / TypeGraphQL / strawberry-graphql) + schema versioning + evolution (oasdiff / openapi-diff / graphql-inspector CI gate) + schema repository 정책 (spec file 위치 / codegen output / versioned artifact publish).
  - **§5 Contract testing** — 3 paradigm × tool ecosystem × CI integration: consumer-driven contract (Pact 구조 5-step + strengths + limitations + `can-i-deploy` gate) + provider-driven contract (Spring Cloud Contract 구조 4-step + Spring ecosystem use case) + schema-based contract (dredd / Schemathesis / chakram / k6 / Prism + graphql-inspector / graphql-codegen+zod) + contract testing vs integration testing axis disjoint (APIContractArch primary contract format / TestContractArch primary §8.6 통합 테스트 CI placement + orchestration / InfraOperationalArch consult broker 운영) + CI integration (pre-merge gate + post-merge canary + sunset coordination).
  - **Out of scope 강화** — 6 boundary explicit codify (aggregate / TestContract / Module / Security / InfraOperational / Data) + co-author 영역 명시 (DTO ↔ entity mapper / hexagonal port / OLAP query API exposure).
  - **적극적 이의 제기 의무 12 사유** — transport 선택 근거 / polyglot transport / versioning 정책 / anti-pattern versioning / DTO validation / error contract / OpenAPI/GraphQL schema / code-first·spec-first / contract testing / backward compatibility / deprecation graceful migration / GraphQL N+1 problem.
  - **Cross-ref 강화** — Story-1 carrier (ADR-042 Amd 8) + Story-3 carrier (4-way RACI overlap zone) + ADR-068 Amendment 2 chief tie-break ladder wording SSOT 명시 + ADR-008 (semver alignment 답습) + ADR-072 (production-cutover dual-spawn) + ADR-054 (doc-only fast-path Category 2).
- **`.claude-plugin/plugin.json`**: 0.14.0 → **0.15.0** MINOR (ADR-037 — agent mandate body 심화 = MINOR). description 갱신 (Story-2 body 심화 5 영역 enumeration 반영).

#### Related ADRs

- ADR-042 Amendment 8 (CFP-1086 Story-1 carrier — APIContractArch 신설 + Sonnet (a) single-mandate advocacy 정합)
- ADR-068 Amendment 2 (Story-1 sibling carrier — chief tie-break ladder 3 단계, 본 mandate body 가 chief author tie-break wording SSOT 역할)
- ADR-086 (Story-1 sibling 신설 carrier — Deputy 신설 결정 framework P7)
- ADR-008 (Inter-plugin Contract Versioning — semver alignment 답습)
- ADR-014 Amendment 4 (design lane SubAgent mandate SSOT)
- ADR-076 (declarative reconciliation upgrade — API schema declarative pattern 동형 답습)
- ADR-072 (ProductionEvidenceDeputy + Epic cutover gate — production-cutover 영역 cross-ref)
- ADR-054 (doc-only fast-path Category 2 — agent file body 확장)

#### Marketplace sibling sync (Orchestrator 영역, 별도 cross-repo PR)

- `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge-design]` mirrored field 4종 (name / version / description / author) sync. ADR-063 atomic invariant.

## [0.14.0] - 2026-05-20

### Added (CFP-1086 Story-1 — BackendArchEpic Phase 2 design lane 7+3+1 roster 재편)

본 release = wrapper SSOT (CFP-1086 Story-1 — ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086 신설 atomic carrier) 의 codeforge-design plugin repo cross-repo sibling 반영. doc-only fast-path (ADR-054 5-repo atomic).

#### agent file 4종 (rename 1 + 신설 2 + mandate 축소 1)

- **`agents/AggregateArchitectAgent.md`** (신설) — 6번째 permanent deputy. RDB OLTP aggregate invariant + 트랜잭션 경계 + persistence-bound aggregate boundary + Alembic 정책 (tool-agnostic policy 7 원칙: 양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit). Sonnet (single-mandate advocacy — ADR-042 Amd8 §결정 1 (a)). CONDITIONAL applicability — `project.yaml aggregate_arch.applicable: bool` (frontend-only / API-only / external-managed consumer non-applicable, P2). consumer overlay `project.yaml aggregate_arch.migration_tool` 9-enum override (default alembic).
- **`agents/APIContractArchitectAgent.md`** (신설, skeleton at S1 / body 심화 = S2) — 7번째 permanent deputy. API transport contract advocate — REST/GraphQL/gRPC/WebSocket + API versioning + DTO contract + OpenAPI/GraphQL schema + contract testing. Sonnet (single-mandate advocacy). 본 release = skeleton + Out of scope + Story-2 cross-ref. body 심화 = CFP-1086 Wave 1 sequential Story-2 별 PR.
- **`agents/ModuleArchitectAgent.md`** (CodeArchitectAgent rename + mandate 정정) — 4번째 permanent deputy. axis 명확화 — module / package boundary + dependency direction + layered/hexagonal/clean module-level + DDD bounded context **module placement** 만 (aggregate invariant 영역 = AggregateArch 분리). Sonnet 유지. mandate 축소 (이전 mandate 7 항목 중 5번째 "DDD aggregate boundary" 영역 = AggregateArch primary 로 이동).
- **`agents/DataArchitectAgent.md`** (mandate 축소) — 빅데이터 OLAP 영역 변호자 only. Parquet / 객체저장소 / DuckDB / streaming pipeline / 백필 / 시계열 집계. RDB OLTP 영역 (PostgreSQL / SQLAlchemy / Alembic / 트랜잭션 경계 / 도메인 모델) 모두 AggregateArch 분리. Opus 유지 (§결정 1 (d) — analytical schema rollback / data integrity invariant 영역). Cross-layer ELT/ETL/CDC boundary (DataArch + AggregateArch co-author) deferred carrier.

#### agent file deletion (rename source)

- `agents/CodeArchitectAgent.md` (→ ModuleArchitectAgent.md rename, axis 명확화)

#### Changed

- **`CLAUDE.md`**: "5 permanent + 3 CONDITIONAL" → **"7 permanent + 3+1 CONDITIONAL + 4-tuple sub-tuple"** wrapper SSOT 와 byte-consistent 재작성 (deputy 매트릭스 7 row + 4-way 영역 분리 + Sub-agent fan-out 갱신 + ArchitectPLAgent prompt 4-mode + DDDArchitect 신설 reject 명문화 + chief tie-break ladder 3 단계 cross-ref).
- **`docs/architecture/codeforge-design.md`**: CFP-1086 living arch doc 갱신 — 7+3+1 roster 반영 (ADR-078 §결정 1 4 영역 갱신: 모듈 / 경계 / 인터페이스 계약 / 데이터 흐름). 4-way 이념 대립 axis 영역 분리 (RDB OLTP / 빅데이터 OLAP / Cross-layer). Cross-cutting gate boundary 에 ADR-068 Amd 2 + ADR-086 추가.
- **`.claude-plugin/plugin.json`**: 0.13.0 → **0.14.0** MINOR (ADR-037 — agent 신설 + rename + mandate 축소 = MINOR). description 갱신 (7+3+1 roster + CONDITIONAL applicability P2 + chief tie-break ladder + Deputy 신설 결정 framework P7 반영).

#### Related ADRs

- ADR-042 Amendment 8 (CFP-1086 Story-1 carrier — design lane 7+3+1 roster 재편)
- ADR-068 Amendment 2 (sibling carrier — chief tie-break ladder 3 단계)
- ADR-086 (sibling 신설 carrier — Deputy 신설 결정 framework P7, axis 분석 + 5-checklist + deferred carrier path)
- ADR-014 Amendment 4 (cross-ref — InfraOperationalArch §7.4 primary 4-sub)
- ADR-076 (declarative reconciliation upgrade — 3-layer 패턴 동형 답습)
- ADR-072 (ProductionEvidenceDeputy + Epic cutover gate)
- ADR-078 (living architecture doc SSOT)
- ADR-054 (doc-only fast-path — 5-repo atomic 단일 PR family)

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
