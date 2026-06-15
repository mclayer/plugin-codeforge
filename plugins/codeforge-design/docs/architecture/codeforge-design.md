---
title: codeforge-design lane 구조 (설계 레인 — Change Plan + ADR 확정)
last_captured: 2026-05-20
last_update_cfp: CFP-1086-S4  # chief 통합 mechanism + tie-break ladder body + mctrader 5 repo cross-layer evidence (P4)
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-969 / Sub-Epic CFP-949 Wave 1, parent Epic CFP-756 / ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타는 Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다.
     CFP-1026 S3 update: deputy 5+3 + 4-tuple sub-tuple 반영 (ADR-042 Amendment 7 / ADR-014 Amendment 4 / ADR-72).
     CFP-1086 S1 update: 5+3 → 7+3+1 roster 재편 반영 (ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086 신설 atomic). AggregateArch + APIContractArch 신설 / CodeArch → ModuleArch rename / DataArch mandate 축소. -->

## 모듈

codeforge-design = 설계 레인 plugin. **Change Plan + ADR 확정** 책임. `[verified: CLAUDE.md @ cfp-1086-s1 Sub-agent fan-out table + agents/ tree direct enumeration]` — agent 구성:

**Permanent agent (9 file)** — 모든 설계 lane 진입 시 spawn (PL + chief + 7 deputy, CFP-1086 / ADR-042-agent-model-selection-policy Amendment 8):

| 모듈 (agent) | 역할 | 입장 / 책임 | model |
|---|---|---|---|
| **ArchitectPLAgent** | 설계 lane PL (supervisor + FIX 판정자) | ArchitectAgent chief + SubAgent 산출물 검수 + final pl_recommendation. **chief tie-break ladder 3 단계** (ADR-068 Amd 2) + **Deputy 신설 결정 framework** (ADR-086 §결정 1/2) 적용 | Opus |
| **ArchitectAgent** (chief author) | 통합 author / synthesizer | SubAgent 산출물 통합 + Change Plan §1-§13 author + ADR draft + Story §3/§7/§11 mirror write | Opus |
| **SecurityArchitectAgent** (deputy) | 위협 — 공격자 관점 | 외부 입력 / 신뢰 경계 / 권한 위임 (Change Plan §7.1-§7.3, §7.5-§7.6 input) | Opus |
| **InfraOperationalArchitectAgent** (deputy, CFP-1026 S1 rename — OperationalRiskArch → Infra...) | 운영 리스크 + infra — production-readiness 변호자 | 끊김 / 실패 / 과부하 / 스테이징-프로덕션 누설 / Docker (Change Plan §7.4 + §11.6 idempotency consult input — AggregateArch primary) | Opus inherit |
| **TestContractArchitectAgent** (deputy) | QA perspective contributor | §8 Test Contract 커버리지 / 경계 / invariant (Epic 소속 Story 시 §8.6 `story_key` + `suite: "story"` 필수) | Opus |
| **DataArchitectAgent** (deputy, CFP-1086 Amendment 8 mandate 축소 — 빅데이터 OLAP only) | 빅데이터 OLAP 영역 변호자 | Parquet / 객체저장소 / DuckDB / streaming / 백필 / 시계열 집계 (Change Plan §3 OLAP + §11 OLAP input). RDB OLTP 영역은 AggregateArch primary 로 분리 | Opus |
| **AggregateArchitectAgent** (deputy, CFP-1086 Amendment 8 신설) | RDB OLTP aggregate invariant 변호자 — single-mandate | aggregate boundary + 트랜잭션 경계 + persistence-bound + Alembic 정책 7 원칙 (Change Plan §3 aggregate + §11.1-§11.6 RDB OLTP input). **CONDITIONAL applicability** (`project.yaml aggregate_arch.applicable: bool`) | Sonnet |
| **APIContractArchitectAgent** (deputy, CFP-1086 Amendment 8 신설 — skeleton at S1 / body 심화 = S2) | API transport contract 변호자 — single-mandate | REST/GraphQL/gRPC/WebSocket + API versioning + DTO + OpenAPI/GraphQL schema + contract testing (Change Plan §3 API + §8 contract testing input) | Sonnet |
| **ModuleArchitectAgent** (deputy, CFP-1086 Amendment 8 — CodeArch rename + mandate 정정) | §3 code module-level 구조 advocate — single-mandate | module boundary + dependency direction + layered/hexagonal/clean module-level + DDD bounded context module placement (Change Plan §3 code input). 도메인 모델 invariant 영역 = AggregateArch 분리 | Sonnet |

**4-tuple sub-tuple component (3 file, deputy 아님 — ADR-044 CFP-676 reaffirm)** — Orchestrator 가 flat spawn (chief author 포함 4 component 평행):

| 모듈 (agent) | 역할 | 입장 / 책임 | model |
|---|---|---|---|
| **CodebaseMapperAgent** | 보수 — as-is 변호자 | 기존 패턴 유지, 변경 영향 최소화 (Change Plan §2 현재 구조 input) | Sonnet |
| **RefactorAgent** | 혁신 — to-be 옹호자 | 결합도 감소, 인터페이스 분리, 패턴화 (Change Plan §3 + §6 input) | Sonnet |
| **ArchitectAnalystAgent** (CFP-1026 S1 신설 — PriorArtAgent conceptual rename) | 변경 전 기존 설계 분석 단일 축 — fact 변호자 | 변경 전 ADR / Change Plan / Story §3/§7/§11 분석 (Change Plan §2 컨텍스트 input) | Sonnet |

**CONDITIONAL deputy (3+1 file)** — Story trigger 충족 시 ArchitectPLAgent 가 추가 spawn (CFP-1086 Amendment 8 정합 — 3 → 3+1):

| 모듈 (agent) | trigger 조건 | 책임 | model |
|---|---|---|---|
| **LiveOpsDeputy** | Live touching Story (real funds / live exchange API / production credential / live order placement 1+ touching, CFP-77) | operator approval / kill switch / incident response / OperationEvent audit (Change Plan §13 + §7.5 consult input) | Opus |
| **LiveOrderingDeputy** | Live touching Story (위 동일 CFP-77 trigger) | order submit / partial fill / cancel race / rejection mapping / ledger reconcile invariant (Change Plan §11 ledger + §8.5 order replay + §11.6 idempotency consult input) | Opus |
| **ProductionEvidenceDeputy** (CFP-1026 S1 신설 — ADR-72) | production cutover Story (Change Plan §13 `production_cutover_touching: true` 선언 OR §13 Live Operational Discipline 본문 보유). wrapper-self-app N/A | 실측 production 통과 evidence quad (functional / security / monitoring / testing) + EPIC CLOSED gate + post-cutover wiring + Family 7 atomic canary pin | Opus inherit |
| **AggregateArch CONDITIONAL applicability** (CFP-1086 Amendment 8 P2 신설 — 3+1) | `project.yaml aggregate_arch.applicable: bool` (default `true`). non-applicable consumer = frontend-only / API-only / external-managed RDB | AggregateArchitect deputy 활성 여부 결정. `false` 시 7 → 6 permanent deputy + 3 sub-tuple = 9 SubAgent parallel spawn | (CONDITIONAL flag, agent file 없음) |

> **4-way 이념 대립 축** (CFP-1086 정합): RDB OLTP 영역 = CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ AggregateArch / 빅데이터 OLAP 영역 = CodebaseMapper ↔ Refactor ↔ SecurityArch ↔ DataArch / Cross-layer (ELT/ETL/CDC) = AggregateArch + DataArch co-author deferred. chief author 가 충돌 해소 + Change Plan 명시. TestContractArch / InfraOperationalArch / ModuleArch / APIContractArch / ArchitectAnalyst / LiveOps / LiveOrdering / ProductionEvidence = contributor / single-mandate advocacy 단일 축 (대립 비참여).

**InfraArchitect 신설 철회** (CFP-1026 S1 — ADR-042-agent-model-selection-policy Amendment 7 SSOT): Docker-first + AWS 없음 환경 — InfraArchitect 미도입 결정. InfraOperationalArchitect 가 §7.4.6 Container considerations 영역 cover.

**DDDArchitect 신설 reject** (CFP-1086 / ADR-042-agent-model-selection-policy Amendment 8 §DDDArchitectAgent reject 명문화): Phase 1 Q4-prime 사용자 발의 — axis 미정합 (method / 학파 layer + ModuleArch wording overlap + consumer applicability 축소). 미도입 결정, ratchet 위반 아님 (ADR-058 §결정 5 sunset_justification 불필요).

## 경계

**Lane self-write boundary** `[verified: CLAUDE.md @ cfp-1026-s3 Self-write 책임 표]`:

| 경계 영역 | owner agent |
|---|---|
| `docs/change-plans/<slug>.md` (§7.4 + §11.6 + §3 code + §3 data 통합 포함) | ArchitectAgent (direct write, CFP-26 Phase 0a) |
| `docs/adr/ADR-NNN-<slug>.md` | ArchitectAgent (direct write, CFP-26 Phase 0a) |
| Story §3 (ADR list mirror) | ArchitectAgent |
| Story §7 (보안 + §7.4 운영 리스크 mirror) | ArchitectAgent |
| Story §11 (데이터 마이그레이션 mirror) | ArchitectAgent |
| `docs/architecture/<path>.md` (본 doc 영역) | ArchitectAgent (lane gate — ADR-078 §결정 1 4 영역 갱신 의무, 매 Change Plan merge 시) |
| GitHub comment `[설계]` prefix | ArchitectPLAgent |
| `phase:설계` → `phase:설계-리뷰` transition | ArchitectPLAgent |

**Deputy mandate matrix** (§3 / §7 / §11 / §13 sub-section ownership) — `codeforge:deputy-mandate` skill SSOT 요약 (CFP-1026 S1):

| Change Plan sub-section | owner deputy |
|---|---|
| §2 현재 구조 (변경 전 기존 설계 컨텍스트) | CodebaseMapperAgent + ArchitectAnalystAgent (4-tuple sub-tuple) |
| §3 code (layered / hexagonal / clean / DDD bounded context / module boundary / dependency direction) | CodeArchitectAgent (CFP-1026 S1 신설) |
| §3 data (entity / aggregate / VO / persistence model / 데이터 흐름) | DataArchitectAgent (CFP-1026 S1 rename + mandate 확장) |
| §3 도입할 설계 (refactor 시각) + §6 리팩토링 선행 | RefactorAgent (4-tuple sub-tuple) |
| §7.1-§7.3 / §7.5-§7.6 보안 | SecurityArchitectAgent |
| §7.4 운영 리스크 (DR / disconnect / clock / rate / env / container) + §11.6 idempotency consult | InfraOperationalArchitectAgent (CFP-1026 S1 rename) |
| §8 Test Contract | TestContractArchitectAgent |
| §11.1-§11.5 schema / migration / rollback / integrity / backfill + §11.6 idempotency (primary) + event schema / DTO / API contract data | DataArchitectAgent |
| §13 Live Operational Discipline (CONDITIONAL Live touching) | LiveOpsDeputy |
| §11 ledger reconcile + §8.5 order replay + §11.6 idempotency (order side, CONDITIONAL Live touching) | LiveOrderingDeputy |
| Production evidence quad + EPIC CLOSED gate + post-cutover wiring + Family 7 canary pin (CONDITIONAL production cutover) | ProductionEvidenceDeputy |

**InfraOperationalArch ↔ ProductionEvidence disjoint axis** (ADR-014 Amendment 4 §결정 3 / ADR-72 §결정 4):
- policy SSOT axis (InfraOperationalArch) = §7.4 invariant 정의 — design-time decision
- evidence SSOT axis (ProductionEvidence) = production grounding 실측 명시 — runtime evidence
- consumer production cutover Story 에서 dual-spawn 가능 (영역 disjoint)
- wrapper-self-app 시 ProductionEvidence N/A (ADR-72 §결정 6)

**Cross-cutting gate boundary**:
- **Codex Proactive Check Touchpoint #2** = ArchitectAgent §3 완료 직후 mandatory dispatch (CFP-532 / ADR-052 Amendment 4) — P0 + P1 finding 모두 inline FIX 의무 (skip 영역 차단)
- **ADR-065 mechanical self-check** = Phase 1 산출물 commit 직전 7-item mechanical sync (label-registry / doc-locations / workflow self-app / link target / MANIFEST.yaml / section-ownership / doc-locations row) self-verify 의무
- **ADR-068 boundary completeness** = ArchitectAgent §3 / §7 작성 시 4+1 semantic invariants (I-1 API contract semantic / I-2 cross-module propagation / I-3 guard placement intent / I-4 wording SSOT / I-5 dimensional empirical grounding) self-verify 의무. **Amendment 2 (CFP-1086) chief tie-break ladder 3 단계**: (1) RACI matrix lookup → (2) ADR-068 invariant 적용 → (3) chief judgement + ADR Amendment carrier 발의
- **ADR-082 write-time self-write verification** = §9 evidence / corpus enumeration / cross-plugin ownership write-time source direct verify 의무 (assertion 금지)
- **ADR-086 Deputy 신설 결정 framework (CFP-1086 신설)** = deputy roster 변경 carrier Story 시 axis 분석 의무 (§결정 1) + 5-checklist self-application (§결정 2: axis disjoint / cost-token budget / consumer carrier / sibling Epic align / deferred trigger) + deferred carrier path (§결정 3). review-verdict-v4 v4.6 `deputy_axis_restructure_self_check_passed` field carrier

**Disjoint scope** (ADR-078 §결정 3):
- 본 doc (architecture_doc) = lane internal 누적 현재 상태, Story key 독립
- Change Plan = Story별 변경 델타, Story key 종속, 1회 작성
- ADR = 단일 결정 단위, 불변
- 본 doc ↔ Change Plan = 상보 disjoint (구조 vs 델타)

## 인터페이스 계약

lane 간 + lane 내부 계약 surface = `docs/inter-plugin-contracts/` (canonical = 본 plugin repo, wrapper = sibling sync mirror — ADR-010):

**Producer 계약 (kind:contract)** — 본 lane 이 생성:

| contract | 용도 | SSOT pointer |
|---|---|---|
| `design_output` | 설계 lane 산출물 핸드오프 (Change Plan + ADR + Story §3/§7/§11 mirror) | `docs/inter-plugin-contracts/design-output-v2.md` (canonical) + wrapper sibling mirror (ADR-010) |

**Host 계약 (kind:registry — sibling sync 면제, ADR-010 §결정 2)** — 본 lane 이 발동 / 참여:

| contract | 본 lane 역할 |
|---|---|
| `debate-protocol-v1` | DesignReview lane divergence 시 multi-round adversarial debate carrier. **Wave 4 blanket trigger** (`blanket_cross_module_designlane`) = touched_top_level_paths ≥ 2 OR touched_lanes ≥ 2 Story 시 자동 활성 (ADR-059 Amendment 2). 4-value dispatch_mode 우선순위 `auto_on_divergence > blanket_cross_module_designlane > mechanical_fast_path_inline > user_request_only`. transcript → Story §9 append → §10 FIX Ledger `debate_artifact_ref` carrier |
| `parallel-dispatch-protocol-v1` | ArchitectPLAgent 의 5 (또는 8/9) SubAgent + 4-tuple sub-tuple **parallel spawn** 계약 host. sequential 강제 사유 3종 (state dependency / shared resource / ordering invariant) 부재 시 default parallel (ADR-064 Trace 4) |
| `review-verdict-v4` | ArchitectPL → DesignReviewPL 핸드오프 carrier field 보유: `mechanical_self_check_passed` (ADR-065) + `boundary_completeness_self_check_passed` (ADR-068 I-1~I-4) + `dimensional_empirical_self_check_passed` (ADR-068 I-5) + `marketplace_sync_declared` (ADR-063 §결정 9) |

**Chief author monopoly**:
- **ADR-RESERVATION row append** — `docs/adr/ADR-RESERVATION.md` sequential append (ArchitectAgent chief 가 신규 ADR 번호 예약, parallel epic conflict 회피 — ADR-050)
- **신규 ADR draft write** — `docs/adr/ADR-NNN-<slug>.md` (CFP-26 Phase 0a, 본 lane plugin repo 가 아닌 wrapper / lane plugin 의 owner repo 에 따라 분기)

> 계약 schema field-level 상세 + version 값 = 각 contract file SSOT + MANIFEST.yaml. 본 섹션 = surface enumeration (계약 이름 + SSOT pointer, version literal 미박제 — version drift 회피).

## 데이터 흐름

**설계 lane 진입 → 산출물 flow** (Orchestrator 가 lane 진입 시 ArchitectPLAgent 1개 spawn — non-skippable):

```
[upstream] requirements_output 수신 (Story §1-§6 완료)
  ↓
ArchitectPLAgent (lane PL) spawn
  ↓ Story §13 CONDITIONAL trigger 검토 (Live touching / production cutover)
  ↓
Orchestrator parallel spawn (ADR-039 flat spawn, ArchitectPL re귀 spawn 0):
  ├─ ArchitectAgent (chief author) — multi-source synthesizer (4-tuple sub-tuple component)
  ├─ CodebaseMapperAgent       → §2 input (4-tuple sub-tuple)
  ├─ RefactorAgent             → §3 + §6 input (4-tuple sub-tuple)
  ├─ ArchitectAnalystAgent     → §2 컨텍스트 input (4-tuple sub-tuple, CFP-1026 S1 신설)
  ├─ SecurityArchitectAgent    → §7.1-§7.3 / §7.5-§7.6 input (7 permanent deputy)
  ├─ InfraOperationalArchAgent → §7.4 + §11.6 idempotency consult input (7 permanent, CFP-1026 S1 rename — §11.6 AggregateArch primary 영역 협업)
  ├─ TestContractArchAgent     → §8 Test Contract input (7 permanent deputy)
  ├─ DataArchitectAgent        → §3 OLAP + §11 OLAP input (7 permanent, CFP-1086 mandate 축소 — RDB OLTP 영역 제거, 빅데이터 OLAP only)
  ├─ ModuleArchitectAgent      → §3 code module-level input (7 permanent, CFP-1086 CodeArch rename + mandate 정정)
  ├─ AggregateArchitectAgent   → §3 aggregate + §11.1-§11.6 RDB OLTP input (7 permanent, CFP-1086 신설 — CONDITIONAL applicability `project.yaml aggregate_arch.applicable` 확인 후 spawn)
  ├─ APIContractArchitectAgent → §3 API + §8 contract testing input (7 permanent, CFP-1086 신설 — skeleton at S1 / body 심화 = S2)
  ├─ [CONDITIONAL] LiveOpsDeputy           → §13 + §7.5 consult
  ├─ [CONDITIONAL] LiveOrderingDeputy      → §11 ledger + §8.5 + §11.6 consult
  └─ [CONDITIONAL] ProductionEvidenceDeputy → §13 production evidence quad + EPIC CLOSED gate (CFP-1026 S1 신설)
  ↓ (10-13 산출물 병렬 수신 — CFP-1086 7 permanent + 3 sub-tuple = 10 default, AggregateArch non-applicable 시 9 / CONDITIONAL 모두 활성 시 최대 13)
ArchitectAgent (chief author) — 산출물 통합 (Opus multi-source synthesis)
  ├─ Change Plan §1-§13 author (docs/change-plans/<slug>.md direct write)
  ├─ 신규 ADR draft (docs/adr/ADR-NNN-<slug>.md direct write + ADR-RESERVATION row append)
  ├─ Story §3 ADR list mirror
  ├─ Story §7 보안 + §7.4 운영 리스크 mirror
  ├─ Story §11 데이터 마이그레이션 mirror
  └─ §3.5 self-lint (deputy 산출물 input 표면 mechanical check)
     §5.5 ADR-065 mechanical 7-item self-check (commit 직전)
     §5.6 ADR-068 boundary completeness 4 invariants self-check
     §5.6.1 ADR-068 I-5 dimensional empirical grounding self-check
     §5.7 ADR-063 marketplace sync diff 감지 (Change Plan §13 declarative)
  ↓
[Codex Proactive Check Touchpoint #2 — mandatory dispatch]
  · ArchitectAgent §3 완료 직후 자동 발동 (CFP-532 / ADR-052 Amendment 4)
  · P0 + P1 finding 모두 inline FIX 의무 (skip 차단)
  ↓
ArchitectPLAgent 검수 → review-verdict packet 작성
  · 4 boolean field (mechanical / boundary / dimensional / marketplace_sync_declared)
  · PASS or FIX → ArchitectAgent 재스폰 (RETURN)
  ↓
[downstream] design_output → DesignReviewLane 핸드오프
```

**FIX 루프 데이터 흐름**:
- DesignReviewLane FIX verdict → ArchitectPLAgent 재spawn → ArchitectAgent 재스폰 (Change Plan 갱신만 담당)
- 구현 lane FIX root cause = 설계 판정 시 ArchitectPLAgent (DeveloperPL 1차 진단 후 최종 결정) → Change Plan 갱신 + Phase 1 follow-up PR
- debate-protocol-v1 발동 시 transcript = Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry → ArchitectAgent 재스폰 시 verbatim 입력

**artifact propagation**:
- Story file (`internal-docs/codeforge-design/stories/<KEY>.md`) = lane 컨텍스트 SSOT (ArchitectAgent self-fetch §1-§7)
- Change Plan (`docs/change-plans/<slug>.md`) = Story별 변경 델타 (1회 작성, Story key 종속)
- ADR (`docs/adr/`) = 단일 결정 단위 (불변)
- 본 doc (architecture_doc) = 누적 현재 상태 (영속, Story key 독립) — 매 Change Plan merge 시 4 H2 영역 갱신 의무 (CLAUDE.md `Self-write 책임` 표 last row)

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### ADR-076 declarative reconciliation 3-layer cross-ref

본 lane 의 architecture_doc 운용은 [ADR-076](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-076-declarative-reconciliation-upgrade.md) declarative reconciliation 3-layer 패턴을 도메인 disjoint 로 답습 (ADR-078 §결정 4 명시):

- **desired state** = 본 doc 의 4 H2 closed-enum (모듈 + 경계 + 인터페이스 계약 + 데이터 흐름) 누적 현재 상태 SSOT
- **current state** = lane plugin agent file (`agents/*.md`) + `CLAUDE.md` 의 실제 정의 상태
- **converge** = ArchitectAgent self-write (매 Change Plan merge 시 4 H2 갱신, CLAUDE.md `Self-write 책임` 표 last row) + design lane verdict gate (DesignReviewPL 가 본 doc drift 검증 — CFP-923 detection class d, architecture-drift lint 후속 carrier)

---

### mctrader 5 repo cross-layer evidence (CFP-1086 P4 carrier)

본 section = CFP-1086 Story-4 의 P4 evidence — 7+3+1 deputy roster + chief tie-break ladder + ADR-086 Deputy 신설 결정 framework 의 **first real-world application case** (mctrader 5 repo consumer project). consumer 측 cross-layer mandate matrix 의 explicit declare. anti-scope guard 준수 (모듈 / 경계 / 인터페이스 / 흐름 수준 only — 코드 line 수준 0건).

#### mctrader 5 repo 의존 그래프 (consumer project)

```
mclayer/mctrader-market          (외부 API client — 일반 거래소)
mclayer/mctrader-market-bithumb  (Bithumb KRW 거래소 client)
                  ↓ DTO + API contract
mclayer/mctrader-engine          (RDB OLTP — backtest engine, 트랜잭션 경계)
mclayer/mctrader-web             (RDB OLTP — FastAPI web UI, 사용자 dialog)
                  ↓ ELT/ETL/CDC pipeline (cross-layer boundary)
mclayer/mctrader-data            (빅데이터 OLAP — Parquet + DuckDB + 시계열 집계)
```

5 repo cross-module dependency direction = market[-bithumb] → engine + web (DTO + API contract) → data (ELT/ETL/CDC). 역방향 의존성 0건 (clean architecture invariant).

#### Axis mapping — deputy primary 영역 (7+3+1 roster 적용)

| mctrader repo | 1차 layer | Primary deputy | Consult deputy | 비고 |
|---|---|---|---|---|
| `mclayer/mctrader-market` | API transport | **APIContractArch** (REST/WebSocket transport + DTO shape + rate limit contract) | SecurityArch (auth) + InfraOperationalArch (재연결 / clock drift) | 외부 거래소 API contract — APIContractArch single-mandate advocacy 첫 적용 영역 |
| `mclayer/mctrader-market-bithumb` | API transport | **APIContractArch** (Bithumb REST/WebSocket + KRW 통화 quirks + Korean exchange specific) | SecurityArch (API key) + InfraOperationalArch (Bithumb specific rate limit) | KRW 통화 domain — DataArch consult (가격 schema OLAP 영역) |
| `mclayer/mctrader-engine` | RDB OLTP | **AggregateArch** (backtest run aggregate invariant + 트랜잭션 경계 + Alembic 정책 7 원칙) | SecurityArch (PII) + InfraOperationalArch (connection pool / DR) + DataArch (engine 산출물 → OLAP backfill pipeline) | RDB OLTP aggregate invariant — AggregateArch single-mandate first applied |
| `mclayer/mctrader-web` | RDB OLTP | **AggregateArch** (user aggregate + 트랜잭션 경계 + FastAPI session 정책) | SecurityArch (CSRF / OWASP) + APIContractArch (FastAPI REST contract surface — DTO shape co-author) + InfraOperationalArch (gunicorn worker / DR) | UI 영역 ↔ DTO boundary = AggregateArch + APIContractArch co-author |
| `mclayer/mctrader-data` | 빅데이터 OLAP | **DataArch** (Parquet schema + 객체저장소 layout + DuckDB query plan + streaming + 백필 + 시계열 집계) | InfraOperationalArch (OLAP scan compute budget) + AggregateArch (engine OLTP → OLAP 변환 schema mapping consult) | 빅데이터 OLAP only — DataArch mandate 축소 후 first applied case |
| 5 repo cross-module | dependency direction | **ModuleArch** (boundary + dependency direction + DDD bounded context module placement) | ArchitectAgent chief tie-break (cross-layer 충돌 시 — Amendment 2 ladder 3 단계 적용) | 5 repo 간 boundary + 역방향 의존성 차단 invariant |
| 모든 repo cross-cutting | — | **SecurityArch** + **InfraOperationalArch** (consult) | TestContractArch §8.6 (5 repo integration test contract) | cross-cutting = single advocate 가 5 repo 모두 cover |

#### Cross-layer ELT/ETL/CDC boundary (AggregateArch ↔ DataArch co-author)

RDB OLTP (engine / web) → 빅데이터 OLAP (data) 의 **ELT / ETL / CDC pipeline** = AggregateArch + DataArch **co-author 영역**:

- **scope boundary** — RDB schema (AggregateArch primary, Alembic SSOT) ↔ Parquet schema (DataArch primary, schema evolution rule) 의 변환 mapping
- **CFP-1086 Story-1 declare** "deferred carrier (별 sibling 배포 lane Epic 산출 후 결정)" — 본 S4 mctrader evidence 가 first applied case
- **chief tie-break trigger** — 변환 mapping wording 충돌 시 (예: enum name AggregateArch UPPER_SNAKE_CASE vs DataArch lowercase snake_case) Amendment 2 ladder 2 단계 (I-4 wording SSOT) 적용
- **consumer carrier path** — mctrader 측 ELT/ETL pipeline 구현 시 codeforge sibling Epic 발의 → ADR-086 §결정 3 deferred carrier path 호출

#### 4-way RACI matrix 실 적용 evidence (Story-3 carrier cross-ref)

본 mctrader case 가 Story-3 의 4-way overlap zone RACI 표준 row 의무 첫 적용 (Story-3 = parallel sibling, 본 S4 작성 시점 codify 진행 중). 4 영역 RACI mapping enumerate:

| RACI scenario | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| `mctrader-web` RDB schema 결정 | AggregateArch | ArchitectAgent (chief) | SecurityArch (PII) + InfraOperationalArch (connection pool) | DataArch (OLAP backfill 영향) + APIContractArch (DTO shape 영향) |
| `mctrader-market[-bithumb]` API contract 결정 | APIContractArch | ArchitectAgent (chief) | SecurityArch (auth) + InfraOperationalArch (rate limit) | AggregateArch (DTO ↔ entity mapper 영향) |
| `mctrader-data` Parquet schema 결정 | DataArch | ArchitectAgent (chief) | InfraOperationalArch (OLAP scan budget) + AggregateArch (RDB ↔ OLAP 변환 영향) | ModuleArch (boundary invariant 영향) |
| `mctrader-engine` ↔ `mctrader-data` ELT/ETL pipeline | AggregateArch + DataArch co-author | ArchitectAgent (chief tie-break — Amendment 2 ladder) | SecurityArch (data 마스킹) + InfraOperationalArch (pipeline 실패 시 DR) | ModuleArch (5 repo boundary) + APIContractArch (만약 API exposure 동반 시) |
| 5 repo cross-module dependency direction | ModuleArch | ArchitectAgent (chief tie-break — cross-layer 충돌 시) | 모든 deputy (cross-cutting) | — |

> **Important** — 본 RACI matrix = Story-3 RACI 표준 row 형식 의 4-column 답습 (R/A/C/I). Story-3 codify 후 본 mctrader case 가 cross-ref 입력 (mandate matrix lookup 시 1단계 RACI lookup 첫 적용 사례).

#### chief tie-break ladder application (mctrader scenario sample)

mctrader-engine OLTP enum name (예: `BacktestStatus.RUNNING`) ↔ mctrader-data OLAP column name (예: `backtest_status_running`) wording 충돌 발생 가정. chief tie-break ladder 3 단계 적용:

1. **단계 1 RACI lookup** — `mctrader-engine` enum = AggregateArch primary (RACI 명시). `mctrader-data` column = DataArch primary (RACI 명시). 양 deputy 동등 R → tie-break 불가 → 단계 2 진입.
2. **단계 2 ADR-068 invariant** — I-4 wording SSOT 적용. ADR §결정 wording 우선 SSOT — codeforge mctrader-hub repo ADR (consumer ADR) 안 `BacktestStatus.RUNNING` UPPER_SNAKE_CASE 으로 codify 되어 있으면 RDB 측 우선. OLAP column = `backtest_status_running` 은 변환 mapping 영역 (`enum→snake_case` deterministic transform).
3. **단계 3 chief judgement (만약 ADR 영역도 wording 부재 시)** — chief 가 `BacktestStatus.RUNNING` UPPER_SNAKE_CASE base SSOT 채택 + ADR Amendment 발의 (mctrader-hub ADR codify carrier) + 사용자 escalation (consumer 영역).

→ 본 sample = ADR-068 Amendment 2 ladder 의 mctrader 실 적용 시 expected flow declaration (cross-ref evidence only — 실 적용 carrier 는 mctrader Epic 발의 시점).

#### Anti-scope guard 준수 declare

본 section = mctrader 5 repo 의 **layer / module / boundary / interface / RACI mapping 수준만**. 다음 4종 금지 (ADR-078 §결정 1 anti-scope guard):

1. mctrader 5 repo 의 클래스 / 함수 / 변수 라인 단위 enumeration **0건**
2. import graph 라인-level **0건**
3. 함수 signature / parameter list / return type **0건**
4. mctrader 5 repo 의 `src/` 디렉터리 1:1 mirror **0건**

→ "deputy roster + chief tie-break + RACI matrix 가 consumer 영역에서 어떻게 매핑되는지" 수준만. 그 외 (mctrader 실 schema / 실 API contract / 실 코드 line) 영역 = consumer Story / Change Plan / ADR 영역.

#### Cross-reference (CFP-1086 carrier 박제)

- wrapper `docs/adr/ADR-068-boundary-completeness-invariants.md` Amendment 2 §"Tie-break ladder 3 단계" SSOT
- wrapper `docs/adr/ADR-086-deputy-creation-decision-framework.md` §결정 1/2/3 (axis 분석 + 5-checklist + deferred carrier path)
- wrapper `docs/adr/ADR-042-agent-model-selection-policy.md` Amendment 8 (7+3+1 roster + AggregateArch CONDITIONAL applicability)
- `agents/ArchitectAgent.md` §"Chief 통합 mechanism" + §"Chief tie-break ladder" body (본 S4 carrier)
- `skills/deputy-mandate/SKILL.md` 4-way overlap zone RACI section (Story-3 carrier — parallel sibling)
- consumer mctrader 5 repo (Story analyst 영역 외 — 본 evidence section = declaration only)

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` 또는 `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
