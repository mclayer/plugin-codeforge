# Changelog

`codeforge-design` plugin 릴리스 이력.

## [Unreleased]

### Removed (CFP-2170 — ProductionEvidenceDeputyAgent design 본 물리 삭제)

- `agents/ProductionEvidenceDeputyAgent.md` 삭제 — ADR-088 §결정 4 ownership 이관 (canonical = `plugins/codeforge-deploy-review/agents/ProductionEvidenceDeputyAgent.md`) 의 lifecycle 완결. deprecated 부착 (2026-05-21) 후 0.21.2 / 0.21.3 — 2 release 경과로 "1 release grace" 만료 실측 (Change Plan cfp-2170 §2.3). consumer blast radius 0 — S5 전 marketplace `codeforge-design` source = 구 lane repo (monorepo `plugins/codeforge-design/**` 와 물리 disjoint).
- `CLAUDE.md` PE roster 기재 4곳 → 이관 사실 1줄 축약 (Sub-agent fan-out 표 PE row + 12-산출물 서사 PE 분기 제거, ADR-72 관련-ADR 줄 이관 註).

버전 할당 = Epic #2151 S5 release 시점 (plugin.json version bump 없음 — marketplace sync 의무 비발동).

### Changed (CFP-1141 — AggregateArch deprecate sibling cross-ref cascade 정정)

CFP-1126 (ADR-042 Amendment 10 — AggregateArchitectAgent deprecate + ModuleArchitectAgent boundary axis 통합 흡수) 의 deferred follow-up. sibling agent file 3종 안 stale `AggregateArch` (current actor) 참조를 canonical `ModuleArch (aggregate-level)` 로 정정 + permanent deputy roster `7 → 6` 정정:
- `agents/APIContractArchitectAgent.md` — roster 7→6 + AggregateArch primary/co-author/제약 → ModuleArch (aggregate-level)
- `agents/DataArchitectAgent.md` — roster 7→6 + mandate 이동 기록(❌ entity/aggregate/DB schema/persistence/데이터 흐름) + cross-layer co-author → ModuleArch (aggregate-level)
- `agents/ArchitectAgent.md` — §3/§11 RACI row + 3+1 CONDITIONAL applicability + 4-way 이념 대립 axis actor → ModuleArch (aggregate-level)

RACI 4→3 column 재편은 CFP-1168 (0.21.1) 에서 이미 완료 — 본 PR 무관. plugin.json description(frozen append-log)·marketplace 는 별 mirrored-field 변경 없음(version PATCH only). PATCH bump (ADR-037 (a) agent file minor edit). doc-only fast-path ADR-054. marketplace atomic sync = version mirror sibling PR 의무 (ADR-063 §결정 5).

## [0.21.2] - 2026-05-30

### Changed (CFP-1845 follow-up — agent model 핀 → 별칭 전환)

[CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 10건. tier 분류 변경 0건. wrapper #1846 / #1847 연계. marketplace sibling sync 동반.

## [0.21.1] - 2026-05-21

### Changed (CFP-1168 — RACI 4-way → 3-way overlap zone mirror 전면 재편)

wrapper `skills/deputy-mandate/SKILL.md` canonical SSOT sibling sync (CFP-1126 follow-up deferred carrier realized — ADR-042 Amendment 10 + ADR-091 Amendment 1 §결정 7 INV-5 정합):
- `CLAUDE.md` RACI section header `4-way overlap zone` → `3-way overlap zone`
- 12-cell summary (3 sub-axis × 4 cross-axis) → 9-cell summary (3 sub-axis × 3 cross-axis)
- Aggregate cross-axis column 제거 (AggregateArch deprecated). ModuleArch (boundary axis unified) cross-axis 가 module-level + aggregate-level RDB OLTP 흡수
- Security/InfraOp/TestContract × Aggregate cell 의 C=AggregateArch → Module cross-axis cell 안 aggregate-level 정합 검토 통합
- Cell 3.4 예외 → Cell 3.3 재번호 (APIContractArch primary §8.6 contract testing 보존)
- CONDITIONAL applicability key `aggregate_arch.applicable` 보존 (ModuleArch carry-over)
- 4-way 이념 대립 / roster 6+3+1 / applicability row = CFP-1126 (0.19.0) 에서 이미 정합 (변경 0)

PATCH bump (ADR-037 (g) CLAUDE.md SSOT clarity — CFP-1126 transitional pointer → realized catch-up, 기존 artifact invalidate 0). doc-only fast-path ADR-054. wrapper skill = canonical / 본 CLAUDE.md = mirror. marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5).

## [0.21.0] - 2026-05-21

### Added (CFP-1117 Story-3 (#1120) — ADR-091 §결정 5/7: Change Plan DDD block)

`templates/change-plan.md` §3 인근에 DDD block 2종 추가 (CONDITIONAL):
- `§3.D bounded_context_boundary` (ADR-091 §결정 5) — BC 명시 + module placement + cross-BC 통신 ACL/OHS 패턴. ModuleArchitectAgent (boundary axis unified) 입력. forcing function INV-5 — `bc_violation` review-verdict finding 연결.
- `§3.A affected_aggregates` (ADR-091 §결정 3) — aggregate root + consistency/transaction boundary + invariant 보존. RDB OLTP touching 의무 (`project.yaml aggregate_arch.applicable`). forcing function INV-5 — `aggregate_violation` finding 연결.

wrapper sibling PR #1151 (Story template §ubiquitous_language + 3 lint + evidence-registry + label-registry v2.43 + ADR-091 Amendment 2 Wave 2 wire). doc-only fast-path ADR-054 Cat 2.

## [0.20.0] - 2026-05-21

### Added (CFP-1117 Story-2 (#1119) — ADR-091 §결정 5: 14 agent DDD frontmatter field)

본 release = ADR-091 (ArchitectLane DDD vocabulary governance) §결정 5 의 codeforge-design plugin repo implementation. 14 agent 전수 frontmatter 에 `bounded_context` + `ddd_pattern` 2 field 부착 + vocabulary theater 차단 (INV-5, ADR-091 §결정 7 forcing function) 1줄 명시. ADR-091 Amendment 1 + CFP-1126 정합 (14 agent, AggregateArch 0, ModuleArch boundary axis unified).

#### Added (14 agent frontmatter 2 field)
- 전수 `bounded_context: codeforge-governance` — governance BC declare (ADR-091 §결정 4 Published Language 분리, mctrader application BC 와 동음이의 충돌 차단)
- agent별 `ddd_pattern` (ADR-091 §결정 1 Hybrid mapping):
  - Authority Pair 2 — `authority-pair-aggregate-root` (ArchitectPL, Layer A metaphor) / `authority-pair-chief-author` (ArchitectAgent, Layer B real consistency boundary)
  - Domain Service 6 — `domain-service` (SecurityArch / InfraOperationalArch / TestContractArch / APIContractArch / DataArch 5) + `domain-service-boundary-axis-unified` (ModuleArch — module-level + aggregate-level 통합, CFP-1126 흡수)
  - Domain Service sub-tuple 3 — `domain-service-sub-tuple` (CodebaseMapper / Refactor / ArchitectAnalyst, 4-tuple flat spawn)
  - Subdomain Specialist 3 — `subdomain-specialist` (LiveOps / LiveOrdering / ProductionEvidence, CONDITIONAL)

#### Added (vocabulary theater 차단 — INV-5 forcing function)
- 14 agent 본문에 `> **DDD pattern (ADR-091 §결정 N)**: ...` blockquote 1줄 — 각 ddd_pattern 어휘가 spawn decision / review rationale 에 실제 영향함을 명시 (Authority Pair = Aggregate consistency boundary 책임 / Domain Service = BC Owner 아님 advisory expertise / Subdomain Specialist = "which subdomain under threat" spawn rationale 어휘 transition). ModuleArch = boundary axis unified 가 module-level + aggregate-level 양 영역 동시 advocate 명시 (CFP-1126 흡수 사실 spawn decision 반영)

#### Note
- `ProductionEvidenceDeputyAgent.md` = deprecated (CFP-1059 Story-3 / ADR-088 §결정 4, ownership codeforge-deploy-review 이관) 상태이나 ADR-091 §결정 5 "전수 frontmatter field 의무" 정합 — field 누락 = vocabulary theater anti-pattern surface 차단 위해 부착 (정식 spawn SSOT 는 이관처)
- agent frontmatter contract — design plugin / wrapper merge.py 는 allowed-keys whitelist 부재 (임의 scalar/array/map deep-merge), 신규 2 field 별도 contract 갱신 불요. CI `agent frontmatter contract` check design plugin 미존재
- `.claude-plugin/plugin.json` 0.19.0 → 0.20.0 MINOR + description CFP-1117-S2 entry prepend (marketplace mirrored field verbatim sync)

#### Deferred (별 Story carrier — ADR-091 Wave 후속)
- S3 lint 3 entry (`check-ddd-pattern-frontmatter.sh` 등 warning tier) + template §ubiquitous_language / §bounded_context_boundary
- S4 review-verdict-v4 v4.7 → v4.8 finding type 3 (`bc_violation` / `aggregate_violation` / `ubiquitous_language_drift`)

## [0.19.0] - 2026-05-21

### Changed (CFP-1126 — ADR-042 Amendment 10 cross-repo sibling: AggregateArch + ModuleArch 통합, ratchet 축소)

본 release = wrapper SSOT (CFP-1126 / ADR-042 Amendment 10 — AggregateArchitectAgent deprecate + ModuleArchitectAgent mandate 흡수, boundary axis 단일 advocate, 7→6 permanent, ratchet 축소 first applied carrier ADR-058 §결정 5 sunset_justification) 의 codeforge-design plugin repo implementation. 사용자 직권 minimal path (Story file 0 / lane spawn 0 / Phase 분리 0 / Retro 0). **0.18.0 = CFP-1092 sibling (CHANGELOG entry 누락 — 별 영역).**

#### Removed
- `agents/AggregateArchitectAgent.md` delete — mandate carry-over to ModuleArchitectAgent (boundary axis 통합)

#### Changed
- `agents/ModuleArchitectAgent.md` mandate 확장 — frontmatter 7 → 13 primary (module-level 1-7 + aggregate-level 8-13 RDB OLTP) + CONDITIONAL applicability (aggregate_arch.applicable carry-over) + body Mandate/산출물 (§3 aggregate + §11)/이의제기 14항/제약 정정
- `CLAUDE.md` roster 7→6 permanent + 4-way 대립 + RACI 4-column transitional pointer note (full 4→3 재편 별 carrier) + fan-out + CONDITIONAL trigger 정정
- `.claude-plugin/plugin.json` 0.18.0 → 0.19.0 MINOR + description CFP-1126 entry prepend (marketplace mirrored field verbatim sync)

#### Deferred (별 follow-up CFP carrier — CFP scope unitary)
- sibling agent cross-ref 13 occurrence (APIContractArch 5 / DataArch 6 / ArchitectAgent 2) 정정
- RACI matrix 4-column → 3-column 정식 재편 (design lane governance 변경)

### Changed (CFP-1059 Story-3 — ProductionEvidenceDeputy ownership 이관 deprecate marker)

본 release = ProductionEvidenceDeputy ownership 이관 (codeforge-design CONDITIONAL deputy → codeforge-deploy-review 정식 deputy) 의 codeforge-design 측 deprecate marker 부착 (ADR-088 §결정 4 / ADR-72 Amendment N). doc-only fast-path (ADR-054 Category 2 — agent file deprecate annotation, ADR / src / tests 변경 0).

#### Changed

- **`agents/ProductionEvidenceDeputyAgent.md`** — deprecate marker 부착:
  - frontmatter `status: deprecated` + `deprecated_by: CFP-1059 Story-3` + `superseded_by: mclayer/plugin-codeforge-deploy-review:agents/ProductionEvidenceDeputyAgent.md` + `ssot_position` 갱신
  - body 상단 ⚠️ DEPRECATED marker (ownership 이관 동인 + 정식 SSOT URL + 1 release grace 후 삭제 명시)
  - mandate body (ADR-72 §결정 1-7) 는 변경 없이 유지 — 이관은 ownership / parent_pl / ssot_position 만
- codeforge-design lane 은 본 deputy 를 더 이상 spawn 하지 않음 (production cutover evidence = DeployReviewPLAgent spawn). 1 release grace 후 file 삭제 (ADR-023 lane plugin lifecycle deprecate 절차)

#### Cross-ref

- Epic: #1059 / Story-3 (codeforge-deploy-review plugin seed + ProductionEvidenceDeputy 이관)
- 정식 SSOT: [`mclayer/plugin-codeforge-deploy-review`](https://github.com/mclayer/plugin-codeforge-deploy-review)

## [0.17.0] - 2026-05-20

### Changed (CFP-1086 Story-4 — chief 통합 mechanism + tie-break ladder body + mctrader 5 repo cross-layer evidence)

본 release = wrapper SSOT (CFP-1086 Story-4 — ADR-068 Amendment 2 implementation body carrier) 의 codeforge-design plugin repo implementation. doc-only fast-path (ADR-054 Category 2 — agent file body 확장 + architecture_doc lane internal SSOT section 신설, ADR / src / tests 변경 0). **0.16.0 skip** — S3 (parallel sibling Story-3 RACI matrix codify) 점유. S4 preemptive bump to 0.17.0.

#### Changed

- **`agents/ArchitectAgent.md`** (body 확장 — frontmatter 무변경 invariant) — 3 신규 sections 추가:
  - **§"Chief 통합 mechanism (CFP-1086 Story-4 carrier — ADR-068 Amendment 2 implementer)"** — Multi-source synthesizer 역할 정의 (7 permanent deputy + 3+1 CONDITIONAL + 4-tuple sub-tuple component). Multi-source synthesis pattern 4 단계 (Deputy advocacy 수렴 / Sub-tuple fact synthesis / Wording SSOT 결정 / Change Plan + ADR draft author). Multi-source synthesis 산출물 구조 표 (Change Plan section 별 input deputy + chief role). Wording SSOT advocate 역할 (deputy 간 wording 충돌 시 final author).
  - **§"Chief tie-break ladder (ADR-068 Amendment 2 implementation — CFP-1086 Story-4)"** — ADR-068 Amendment 2 §"Tie-break ladder 3 단계" body 의 chief author implementation. 단계 1 RACI 매트릭스 lookup (deputy-mandate skill row + 4-way overlap zone matrix) → 단계 2 ADR-068 invariant 적용 (I-1 ~ I-5 verbatim implement) → 단계 3 chief judgement + ADR Amendment carrier 발의 + 사용자 escalation 의무 + ADR-058/ADR-064 ratchet 강화 정합. Verdict packet binding (review-verdict-v4 v4.6 `boundary_completeness_self_check_passed: true` emit 의무). 4-way 이념 대립 axis 보존 (advocate phase 영역 외).
- **`docs/architecture/codeforge-design.md`** (lane internal 누적 SSOT 확장) — §"mctrader 5 repo cross-layer evidence (CFP-1086 P4 carrier)" section 신설:
  - mctrader 5 repo 의존 그래프 (mctrader-market[-bithumb] → mctrader-engine/web → mctrader-data) — dependency direction + 역방향 의존성 0건 declare
  - Axis mapping 표 — 5 repo 각각의 1차 layer + Primary deputy + Consult deputy (APIContractArch primary market/market-bithumb / AggregateArch primary engine/web RDB OLTP / DataArch primary data 빅데이터 OLAP / ModuleArch primary 5 repo cross-module / SecurityArch + InfraOperationalArch cross-cutting)
  - Cross-layer ELT/ETL/CDC boundary (AggregateArch ↔ DataArch co-author 영역) — CFP-1086 Story-1 "deferred carrier" first applied case + chief tie-break trigger 시점 명시
  - 4-way RACI matrix 실 적용 evidence 5 scenario × R/A/C/I 4-column (Story-3 carrier cross-ref)
  - chief tie-break ladder application — mctrader scenario sample (OLTP enum ↔ OLAP column wording 충돌) 3 단계 적용 declaration only
  - Anti-scope guard 준수 declare 4종 (모듈/경계/인터페이스/RACI mapping 수준만, 코드 line 0건)
  - last_update_cfp frontmatter 갱신 (CFP-1086-S1 → CFP-1086-S4)
- **`.claude-plugin/plugin.json`**: 0.15.0 → **0.17.0** MINOR (0.16.0 skip — S3 sibling 점유). description 갱신 (Story-4 chief 통합 mechanism + mctrader evidence section P4 carrier 명시).

#### Invariant declare

- frontmatter / permissions 무변경 (agent prompt body 확장만)
- 4-way 이념 대립 axis 본문 변경 0건 (tie-break = mechanism, axis 자체는 보존)
- anti-scope guard 준수 (mctrader evidence section = layer / module / boundary / RACI mapping 수준만, src/ 코드 line 0건)

#### Related ADRs

- ADR-068 Amendment 2 (CFP-1086 Story-1 carrier — declaration layer SSOT, 본 release = implementation layer)
- ADR-068 Amendment 2 §"Implementation note" subsection (wrapper repo Story-4 carrier — chief author body cross-ref binding)
- ADR-086 (CFP-1086 Story-1 신설 — Deputy 신설 결정 framework, ladder 단계 3 호출 영역)
- ADR-042 Amendment 8 (CFP-1086 Story-1 carrier — 7+3+1 roster, ladder 단계 1 RACI lookup 입력)
- ADR-064 §결정 3 룰 5 (ladder 단계 3 사용자 escalation 정합)
- ADR-067 (max FIX 3/3 — verdict packet false 시 ArchitectAgent re-spawn 정합)
- ADR-078 (living architecture doc — mctrader evidence section anti-scope guard 4종 준수 정합)
- ADR-054 (doc-only fast-path Category 2 — agent file body 확장 + architecture_doc section 신설)

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
