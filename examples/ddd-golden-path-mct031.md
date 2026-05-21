# DDD Golden-Path Worked Example — mctrader ADR-031 4-Layer 모델

> **carrier**: CFP-1117 Story-6 (#1123, Epic 마지막) — ArchitectLane DDD vocabulary governance Epic 의 **golden-path worked example**.
> **SSOT**: ADR-091 §결정 7 INV-5 forcing function 의 **최종 입증** 산출물 (Phase 2 PR5 LAND gate).
> **status**: Active (2026-05-21 KST) — ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합.

## 본 worked example 의 목적 (Codex BIG CONCERN 최종 입증)

ADR-091 의 핵심 risk = **vocabulary theater** (어휘 emit 만 하고 decision flow 변경 0 → restructure = document 만 향상 / runtime lesson 해소 = 0, glossary [`#vocabulary-theater-codeforge-자체-anti-pattern`](../docs/glossary.md#vocabulary-theater-codeforge-자체-anti-pattern)).

본 file 은 mctrader `docs/adr/ADR-031-data-domain-decoupling.md` 의 4-Layer 의존 모델을 **before (DDD 어휘 부재) / after (DDD 어휘 적용)** worked example 로 5 영역 전수 박제하여, 어휘 emit 이 **spawn decision · review findings · ADR acceptance criteria 를 실제로 변경**함을 enumeration evidence 로 입증한다. 단순 문서 향상이 아니라 runtime 6× lesson (MCT-170 / MCT-177 / MCT-179 / MCT-180 / MCT-184 / MCT-185 Phase 0 verify pattern) 해소가 본 입증의 acceptance criterion.

---

## Published Language 분리 명시 (ADR-091 §결정 4)

본 worked example 의 **대상**(mctrader ADR-031)은 **mctrader application BC** 의 사례다. 본 plugin(codeforge)은 **codeforge governance BC**다. 두 BC 는 동음이의 term (`Aggregate` / `Module` / `Repository` 등)을 가지므로 Published Language 를 분리한다.

| BC | 본 worked example 안 역할 | Published Language SSOT |
|---|---|---|
| **codeforge governance BC** (본 plugin) | DDD 어휘 governance mechanism 보유 주체 (Story field / deputy spawn / Change Plan field / review-verdict finding / ADR acceptance) | [`../docs/glossary.md`](../docs/glossary.md) |
| **mctrader application BC** (worked example 대상) | DDD 어휘 적용 **사례** (4-Layer 모델 = Shared Kernel / ACL / OHS / Conformist) — 외부 application 사례 cite only | `mctrader-hub/docs/glossary.md` (downstream Epic, 별 CFP) |

**동음이의 차단 의무**:
- codeforge governance BC 의 `Aggregate` = supervised authority cluster (ArchitectPL metaphor) / ArchitectAgent 산출물 = real consistency boundary (glossary [`#aggregate-governance-bc`](../docs/glossary.md#aggregate-governance-bc)).
- mctrader application BC 의 `Aggregate` = DDD Aggregate root in domain model (glossary [`#aggregate-mctrader-application-bc`](../docs/glossary.md#aggregate-mctrader-application-bc)).
- 본 worked example 에서 mctrader 측 어휘는 모두 `(mctrader application BC)` qualifier 병기. **mctrader-hub repo 변경 0** (cite only — downstream Epic 영역, 별 CFP).

---

## mctrader ADR-031 4-Layer 모델 (verbatim cite, L499-524)

> **cite source**: `mctrader-hub/docs/adr/ADR-031-data-domain-decoupling.md` line 499-524 (canonical main). **mctrader application BC** 의 사례 — 본 codeforge governance BC 변경 0건.

```
## 4-Layer 의존 모델 (TO-BE, spec §4 박제)

 Layer 0 ─ mctrader-market (FOUNDATION, 의존 0, 순수 pydantic/sqlalchemy, data 비의존)
   • 도메인 어휘: Symbol·Timeframe·Decimal38_18·UTCDateTime·OrderStatus·lifecycle
   • wire contract: TickRowV1_1·InformationBarModel·CandleModel/CandleLike·OrderBookLike
   • exchange-neutral Protocol: CandleProvider·OrderBookProvider(기존) + (신규)RealtimeStream
   • ◀ RELOCATE (MCT-182, D1): aggregation algo + TickRecord/OrderbookEventRecord dataclass + PaperLineage
        ▲                        ▲                         ▲                    ▲
 Layer 1 ─ 거래소 어댑터 (각각 → market 만, market Protocol 구현)
   mctrader-market-bithumb · mctrader-market-upbit · -<해외> · -<한국거래소> ... (무한 확장)
        ▲ (등록은 data adapters.py 한 곳)
 Layer 2 ─ mctrader-data (DATA-STORAGE 영역 단독 소유, → market + → 어댑터들)
   • adapters.py 팩토리: 모든 거래소 ingestion 단일 경계 (신규 거래소 = 여기만 등록)
   • storage: scan_candles·orderbook_replay·NAS·parquet + io reader(engine서 이전, MCT-183)
   • NEW api/(FastAPI): /v1 historical(Arrow IPC) + 역방향 POST + 정규화 stream(Redis Stream) (MCT-184/185)
        ▲ 런타임 REST/stream (python import 아님)
 Layer 2'─ mctrader-engine (PURE CONSUMER)
   • mctrader_data = 0 (pyproject 제거, MCT-188)
   • mctrader_market_bithumb/upbit/* = 0 (어댑터 직접 의존 제거, MCT-186)
   • 의존 = Layer 0(market 어휘/contract/algo) + data /v1(REST + 정규화 실시간 stream)

 핵심 확장성 불변식 (D5): 새 거래소 = ① 신규 Layer1 어댑터 repo ② data adapters.py 등록
   ③ data 수집/정규화 설정 → engine 변경 0, market-core 변경 0, ADR 0
 순환: 영원히 없음 (market→누구도 의존 안 함, data→market+어댑터, engine→market+REST)
```

### DDD 패턴 매핑 (mctrader application BC, glossary anchor 정합)

| Layer | mctrader repo | DDD 패턴 (mctrader application BC) | glossary anchor |
|---|---|---|---|
| **Layer 0** | mctrader-market (FOUNDATION, 의존 0) | **Shared Kernel** — 도메인 어휘 (Symbol/Timeframe/Decimal38_18/OrderStatus) + wire contract (TickRowV1_1/CandleModel) + exchange-neutral Protocol (CandleProvider/RealtimeStream). Layer 1/2/2' 가 동시 동의 후 공유 | [`#shared-kernel`](../docs/glossary.md#shared-kernel) |
| **Layer 1** | mctrader-market-bithumb / upbit (→ market Protocol 구현) | **Anti-Corruption Layer (ACL)** — 거래소별 model 을 market Protocol 구현으로 normalize. 외부 거래소 model 이 market 도메인 model 을 오염 차단 (translator + adapter) | [`#anti-corruption-layer-acl`](../docs/glossary.md#anti-corruption-layer-acl) |
| **Layer 2** | mctrader-data (adapters.py 팩토리 + storage + /v1 api) | **Open Host Service (OHS)** — /v1 REST (Arrow IPC) + 정규화 stream (Redis Stream) 으로 multiple consumer 동시 지원. **+ Application Service** (use case orchestration: ingestion 단일 경계) | [`#open-host-service-ohs`](../docs/glossary.md#open-host-service-ohs) |
| **Layer 2'** | mctrader-engine (PURE CONSUMER, mctrader_data=0) | **Conformist** — data /v1 Published Language 를 변경 권한 없이 그대로 따름. translation layer 부재 (REST + stream consume only) | [`#conformist`](../docs/glossary.md#conformist) |

**핵심 확장성 불변식 (D5)**: 새 거래소 = Layer 1 어댑터 + adapters.py 등록 + 수집 설정 → engine/market 변경 0. 이 불변식이 **Layer 0 Shared Kernel ↔ Layer 1 ACL ↔ Layer 2 OHS ↔ Layer 2' Conformist** 의 BC boundary 가 강제하는 결과다.

---

## 5 영역 전수 박제 (before / after)

ADR-091 §결정 7 INV-5 가 명시한 5 영역 각각 — **DDD 어휘 부재 (before)** → **DDD 어휘 적용 (after)** worked example.

### 영역 1 — Story field (§ubiquitous_language)

S3 Story template `§ubiquitous_language` block (`../templates/story-page-structure.md` L137-160) 의 mctrader ADR-031 적용.

#### Before (DDD 어휘 부재)

```yaml
# §ubiquitous_language block 부재 — Story 가 "data layer 를 engine 에서 분리" 라고만 서술
# 어느 BC 안에서 작동하는지, Layer 사이 통신 패턴이 무엇인지 explicit declare 0
# → 신규 member 합류 시: "engine 이 data 를 직접 import 하면 안 되나?" interpretation drift surface
```

#### After (DDD 어휘 적용)

```yaml
bounded_context: application BC (downstream)   # mctrader application BC — codeforge governance BC 와 Published Language 분리
ddd_terms:                                     # docs/glossary.md anchor 정합 (codeforge governance BC SSOT)
  - Shared Kernel                              # Layer 0 mctrader-market (도메인 어휘 + wire contract + Protocol)
  - Anti-Corruption Layer (ACL)                # Layer 1 거래소 어댑터 (market Protocol 구현)
  - Open Host Service (OHS)                    # Layer 2 mctrader-data /v1 REST (Arrow IPC + Redis Stream)
  - Conformist                                 # Layer 2' mctrader-engine (data /v1 Published Language 따름)
  - 4-Layer Architecture (mctrader 적용)        # 종합 구조
glossary_ref: docs/glossary.md                 # Published Language SSOT (content duplication 금지 — link only)
```

**작성 규칙 적용** (S3 §ubiquitous_language 작성 규칙 1-4):
1. `bounded_context = application BC (downstream)` — mctrader 가 codeforge governance BC 가 아님을 explicit declare.
2. `ddd_terms` 전수 = glossary anchor 존재 (Shared Kernel / ACL / OHS / Conformist / 4-Layer 모두 [`../docs/glossary.md`](../docs/glossary.md) entry 보유) — drift 차단.
3. **동음이의 분리** — mctrader 측 `Aggregate` 사용 시 `Aggregate (mctrader application BC)` qualifier 의무 (본 ADR-031 은 storage decoupling 이라 RDB OLTP Aggregate 영역 직접 해당 안 함 — 영역 5 참조).
4. **anti-pattern 어휘 forbid** — "Big Ball of Mud" 를 design intent 로 사용 금지 (본 ADR-031 = 정반대 = BC 분리 명시).

> **`field` 변경 evidence** (INV-5 #1): before = `§ubiquitous_language` block 부재 → after = 5 ddd_terms + bounded_context explicit. lint `scripts/check-ubiquitous-language.sh` (warning tier) 가 ddd_terms ↔ glossary drift 감지 + `scripts/check-bounded-context-presence.sh` 가 bounded_context field presence 검증. **어휘 emit 이 Story field 의 실 검증 대상으로 작동.**

### 영역 2 — deputy spawn rationale (Subdomain Specialist + "which subdomain under threat")

ADR-091 §결정 2 의 deputy spawn rationale 어휘 transition (glossary [`#which-subdomain-under-threat-deputy-spawn-rationale`](../docs/glossary.md#which-subdomain-under-threat-deputy-spawn-rationale) + [`#subdomain-specialist`](../docs/glossary.md#subdomain-specialist)) 의 mctrader ADR-031 적용. deputy-mandate matrix (`../skills/deputy-mandate/SKILL.md`) lookup 정합.

#### Before (DDD 어휘 부재)

```
ArchitectPLAgent deputy spawn rationale:
  "data decoupling Story 이므로 perspective-contributor 일부 활성 — OperationalRisk(운영 리스크)
   관점 + 코드 구조 관점 추가 검토"
  → 어느 deputy 가 왜 활성인지 perspective(보수/혁신/위협) 어휘로만 서술
  → "OperationalRisk 가 데이터 layer 도 보는가?" 결정 분기 모호
```

#### After (DDD 어휘 적용)

```
ArchitectPLAgent deputy spawn rationale (which subdomain under threat):
  primary = ModuleArchitectAgent (Domain Service)
    → "boundary subdomain decision is at risk" : mctrader ADR-031 = data layer decoupling
       (RDB OLTP 아님 — storage/streaming boundary). Layer 0/1/2/2' module boundary +
       dependency direction (역방향 금지) = ModuleArch unified mandate (boundary axis,
       ADR-042 Amendment 10 — module-level + aggregate-level 통합) 영역.
  consult = DataArchitectAgent (Domain Service)
    → OLAP storage (scan_candles / orderbook_replay / parquet / Arrow IPC) 영역 advocacy.
  CONDITIONAL = (해당 시) Subdomain Specialist
    → "which subdomain under threat = production evidence" : mctrader-data /v1 OHS 가
       live trading 또는 production cutover 영역 touching 시에만 ProductionEvidenceDeputy /
       LiveOpsDeputy spawn. ADR-031 (순수 storage decoupling) 자체 = Subdomain inactive →
       Subdomain Specialist spawn 0 (PMO orchestration 절약).
```

**어휘 transition 의 실 효과**:
- before: "perspective-contributor / OperationalRisk 활성" — 어느 deputy 가 왜 활성인지 모호.
- after: "which subdomain under threat" — boundary subdomain at risk → ModuleArch primary (명시 enum). live ops / production evidence subdomain inactive → Subdomain Specialist spawn 0 (명시 면제).

> **deputy spawn rationale 변경 evidence** (INV-5 #2): before = perspective 어휘 → after = "which subdomain under threat" enum 어휘. **이 어휘가 실제 spawn count 를 변경** — ADR-031 같은 순수 storage decoupling Story 에서 LiveOps/ProductionEvidence Subdomain Specialist spawn 0 (subdomain inactive 명시) → orchestration 비용 절약. 어휘가 spawn decision 의 forcing function 으로 작동.

### 영역 3 — Change Plan DDD field (§3.D bounded_context_boundary + §3.A affected_aggregates)

codeforge-design plugin `templates/change-plan.md` 의 DDD block (S3 sibling carrier — 별 repo, ADR-091 Amendment 2 §design Change Plan sibling cross-ref 정합) 의 mctrader ADR-031 적용. review-verdict-v4 v4.8 `bc_violation` 은 §3.D, `aggregate_violation` 은 §3.A 와 forcing function 연결.

#### Before (DDD 어휘 부재)

```
§3 도입할 설계:
  "mctrader-data 가 storage 와 /v1 API 를 단독 소유. engine 은 data 를 import 하지 않고
   REST 로만 접근."
  → BC 경계 / cross-BC 통신 패턴이 산문으로만 서술 — bc_violation 검증 anchor 부재
```

#### After (DDD 어휘 적용)

```yaml
§3.D bounded_context_boundary:
  bounded_contexts:
    - name: Layer 0 (mctrader-market)
      pattern: Shared Kernel
      role: 도메인 어휘 + wire contract + exchange-neutral Protocol SSOT (Layer 1/2/2' 동시 동의 공유)
    - name: Layer 1 (거래소 어댑터)
      pattern: Anti-Corruption Layer (ACL)
      role: 거래소 model → market Protocol 구현 normalize
    - name: Layer 2 (mctrader-data)
      pattern: Open Host Service (OHS)
      role: /v1 REST (Arrow IPC) + 정규화 stream (Redis Stream) multiple consumer 지원
    - name: Layer 2' (mctrader-engine)
      pattern: Conformist
      role: data /v1 Published Language 따름 (변경 권한 0)
  cross_bc_communication:
    - from: Layer 1 → Layer 0    via: market Protocol 구현 (ACL — python import)
    - from: Layer 2 → Layer 0/1  via: market 어휘 + adapters.py 팩토리 (python import)
    - from: Layer 2' → Layer 2   via: /v1 REST + Redis Stream (런타임, python import 아님 — OHS 경유)
    # invariant: 순환 0 (market → 누구도 의존 안 함). engine → data 직접 python import = bc_violation

§3.A affected_aggregates:
  # ADR-031 = storage decoupling (RDB OLTP aggregate 영역 직접 해당 안 함)
  # mctrader application BC 의 DDD Aggregate root (consistency boundary) 영향 시에만 작성
  application_bc_aggregates:
    - N/A — 본 ADR-031 은 데이터 layer decoupling (storage/streaming boundary).
            RDB OLTP transactional consistency boundary 미touching.
            (만약 order/position aggregate 가 transaction boundary 안에 있었다면
             AggregateArch mandate carry-over 받은 ModuleArch unified 영역 + aggregate_violation 검증)
```

> **Change Plan DDD field 변경 evidence** (INV-5 #3): before = BC 경계 산문 서술 → after = §3.D bounded_context_boundary (4 BC pattern + cross-BC 통신 매트릭스 + 순환 0 invariant) + §3.A affected_aggregates (N/A 명시 — RDB OLTP 미touching). **이 field 가 review-verdict-v4 `bc_violation` (§3.D 연결) / `aggregate_violation` (§3.A 연결) 의 cross-validate anchor 로 작동** — 어휘 emit 이 review finding 의 검증 대상으로 변환.

### 영역 4 — review-verdict finding (bc_violation / aggregate_violation / ubiquitous_language_drift)

S4 review-verdict-v4 v4.8 (`../docs/inter-plugin-contracts/review-verdict-v4.md` L471-473) 의 3 finding type enum 의 mctrader ADR-031 적용 예시. DesignReviewPL + CodeReviewPL emit.

#### `bc_violation` 실 emit 사례

```yaml
finding:
  type: bc_violation
  severity: P0
  anchor_id: layer-2prime-direct-import
  description: >
    mctrader-engine (Layer 2', Conformist) src/ 안 `from mctrader_data.storage import scan_candles`
    직접 import 발견. Layer 2' → Layer 2 직접 python import = ACL/OHS 우회 = BC boundary 침범.
    Conformist 는 data /v1 Published Language (REST + Redis Stream) 만 consume 의무 (런타임,
    python import 아님). ADR-031 §D7 data-free done-criterion (engine src/ `from/import
    mctrader_data` == 0) 위반.
  emit_lane: [DesignReviewPL, CodeReviewPL]   # v4.8 dual-binding
  forcing_link: Change Plan §3.D bounded_context_boundary cross_bc_communication invariant
```

#### `aggregate_violation` 실 emit 사례 (해당 시)

```yaml
finding:
  type: aggregate_violation
  severity: P1
  anchor_id: order-aggregate-external-mutation   # ADR-031 본문 미touching — 가정 사례
  description: >
    (ADR-031 자체는 storage decoupling 이라 RDB OLTP aggregate 미touching. 단, 만약 engine 이
    data /v1 의 order/position consistency boundary 를 외부에서 직접 mutate 했다면:)
    aggregate root 외부 직접 access = consistency boundary 침범. transaction boundary 부정합.
    ModuleArchitectAgent (boundary axis unified, ADR-042 Amendment 10) 영역.
  emit_lane: [DesignReviewPL, CodeReviewPL]
  forcing_link: Change Plan §3.A affected_aggregates + ADR-091 §결정 3 Layer B real Aggregate
```

#### `ubiquitous_language_drift` 실 emit 사례

```yaml
finding:
  type: ubiquitous_language_drift
  severity: P2
  anchor_id: adapter-undefined-term
  description: >
    Change Plan §3 안 "어댑터" 를 glossary Anti-Corruption Layer (ACL) 정의 없이 ad-hoc 사용.
    glossary SSOT 외 미정의 DDD term — Layer 1 거래소 어댑터 = ACL pattern 임을 glossary anchor
    (#anti-corruption-layer-acl) 정합 명시 의무. check-ubiquitous-language lint (ADR-091
    Amendment 2 §결정 6 2번째 tier) 감지.
  emit_lane: [DesignReviewPL, CodeReviewPL]
  forcing_link: check-ubiquitous-language lint + docs/glossary.md SSOT
```

> **review-verdict finding 변경 evidence** (INV-5 #4): before = review-verdict-v4 v4.7 에 BC/Aggregate/Language drift finding type 부재 → 이런 위반을 `general` finding 으로만 emit (semantic accountability 0) → after = v4.8 3 finding type 신설 + 위 3 실 emit 사례. **어휘 emit 이 reviewer 의 semantic accountability mechanism 으로 작동** — `bc_violation` 가 Layer 2' 직접 import (data-free done-criterion 위반) 를 P0 로 차단.

### 영역 5 — ADR acceptance criteria (ADR-091 §결정 mapping)

ADR-091 §결정 1/2/3/4/5/6/7 이 mctrader ADR-031 의 어느 영역에 적용되는지 mapping.

| ADR-091 §결정 | 내용 | mctrader ADR-031 적용 영역 |
|---|---|---|
| **§결정 1** Hybrid mapping | 15 agent → 3 DDD role (Authority Pair / Domain Service / Subdomain Specialist) | mctrader ADR-031 검토 시 ArchitectPL+Architect (Authority Pair) 가 ModuleArch+DataArch (Domain Service) 산출물 통합. live/production touching 시 Subdomain Specialist 활성 (영역 2) |
| **§결정 2** deputy spawn rationale | "perspective-contributor" → "which subdomain under threat" 어휘 transition | 영역 2 — boundary subdomain at risk → ModuleArch primary / live·production subdomain inactive → Subdomain Specialist spawn 0 |
| **§결정 3** Aggregate 2-layer | Layer A (governance metaphor) / Layer B (산출물 = real Aggregate) | Change Plan §3.D + §3.A + ADR draft + §8 Test Contract + §11 데이터 마이그레이션 = real consistency boundary (handoff 전 cohere 의무). mctrader application BC 의 Aggregate (DDD root) 와 동음이의 분리 (영역 3 N/A 명시) |
| **§결정 4** Published Language 분리 | codeforge governance BC ↔ mctrader application BC 2 SSOT | 본 worked example 의 Published Language 분리 명시 section + 동음이의 qualifier 병기 (`(mctrader application BC)`) |
| **§결정 5** BC governance + frontmatter field | 14/15 agent frontmatter bounded_context + ddd_pattern 의무 | mctrader ADR-031 검토에 spawn 되는 ModuleArch / DataArch / ProductionEvidence agent 의 frontmatter field (S2 LAND) 가 어느 BC + DDD role 인지 declare → vocabulary theater 차단 |
| **§결정 6** enforcement 3-tier | Agent prompt (S2) / Template lint (S3) / review-verdict enum (S4) | 영역 1 (template lint) + 영역 4 (review-verdict enum) + S2 agent frontmatter (영역 2 deputy 정합) |
| **§결정 7** INV-5 forcing function | 5 영역 evidence enumeration 의무 (본 worked example = LAND gate) | 본 worked example 전체 = §결정 7 의 acceptance criterion 충족 산출물 |

> **ADR acceptance criteria 변경 evidence** (INV-5 #5): before = ADR-031 같은 외부 application 사례를 codeforge ArchitectLane 이 검토할 때 "data 분리 Story" 라는 ad-hoc 분류 → after = ADR-091 §결정 1-7 가 명시적 acceptance criteria 로 작동 (4-Layer = Shared Kernel/ACL/OHS/Conformist mapping + §결정 6 3-tier enforcement). **본 before/after diff 자체가 mctrader ADR-031 의 4-Layer 모델 (line 499-524) 위에 OHS (Layer 2 data /v1 REST API endpoint) + ACL (Layer 1 거래소 어댑터 → market Protocol 구현) 를 시연** (ADR-091 §결정 7 #5 요구).

---

## FINAL VERDICT — Vocabulary Theater 차단 입증

> **INV-5 최종 입증** (ADR-091 §결정 7 / Codex BIG CONCERN). 본 section = CFP-1117 Epic 의 마지막 acceptance criterion.

### Vocabulary theater 가 차단되었음을 입증하는 5 영역 evidence enumeration

vocabulary theater = "어휘 emit 만, decision flow 변경 0". 본 worked example 의 5 영역 박제는 각 영역에서 **어휘 emit 이 실제 behavioral 변화를 일으킴**을 enumeration evidence 로 입증한다 (단순 문서 향상 아님):

| # | 영역 | before (DDD 어휘 부재) | after (DDD 어휘 적용) | **실 behavioral 차이** (decision flow 변경) |
|---|---|---|---|---|
| 1 | **Story field** | §ubiquitous_language block 부재 — "data 분리" 산문만 | bounded_context + 5 ddd_terms (Shared Kernel/ACL/OHS/Conformist/4-Layer) + glossary_ref | **lint 가 실 검증** — `check-ubiquitous-language.sh` 가 ddd_terms↔glossary drift 감지 (exit 1), `check-bounded-context-presence.sh` 가 field presence 검증. 어휘가 mechanical fail signal 의 대상 |
| 2 | **deputy spawn** | "perspective-contributor / OperationalRisk 활성" 모호 | "which subdomain under threat" → ModuleArch primary / live·production subdomain inactive | **spawn count 변경** — ADR-031 순수 storage decoupling Story 에서 LiveOps/ProductionEvidence Subdomain Specialist spawn 0 (subdomain inactive 명시) → orchestration 비용 절약. 어휘가 spawn decision forcing function |
| 3 | **Change Plan DDD field** | BC 경계 산문 서술 | §3.D bounded_context_boundary (4 BC pattern + cross-BC 통신 매트릭스 + 순환 0 invariant) + §3.A affected_aggregates (N/A 명시) | **review anchor 변환** — §3.D 가 `bc_violation` cross-validate anchor, §3.A 가 `aggregate_violation` anchor 로 작동. 어휘가 review finding 검증 대상으로 변환 |
| 4 | **review-verdict finding** | v4.7 — BC/Aggregate/Language drift finding type 부재 (`general` 로만 emit, semantic accountability 0) | v4.8 — `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` 3 finding type + 실 emit 사례 (P0 Layer 2' 직접 import 차단) | **review verdict 변경** — `bc_violation` 가 engine→data 직접 import (data-free done-criterion 위반) 를 P0 로 차단 → DesignReviewPL + CodeReviewPL dual-binding emit. 어휘가 semantic accountability mechanism |
| 5 | **ADR acceptance criteria** | "data 분리 Story" ad-hoc 분류 | ADR-091 §결정 1-7 명시적 acceptance criteria (4-Layer = Shared Kernel/ACL/OHS/Conformist + 3-tier enforcement) | **acceptance 기준 변경** — §결정 1-7 이 mctrader ADR-031 검토의 명시 기준. before/after diff 가 4-Layer 위 OHS + ACL 시연. 어휘가 ADR acceptance criteria |

### Forcing function 연결 (S2 ↔ S3 ↔ S4 ↔ S5 cross-Story)

본 worked example 이 입증하는 핵심 = 5 영역이 **독립적 문서 향상이 아니라 cross-Story forcing function 으로 연결**되어 있다는 점:

```
S2 (agent frontmatter bounded_context + ddd_pattern)
  ↓ 어느 BC + DDD role 인지 declare
S5 (deputy spawn rationale "which subdomain under threat")
  ↓ subdomain at risk 판단 → Subdomain Specialist spawn 결정 (영역 2)
S3 (Story §ubiquitous_language + Change Plan §3.D/§3.A + Template lint)
  ↓ ddd_terms↔glossary drift 검증 + BC boundary anchor 작성 (영역 1, 3)
S4 (review-verdict-v4 v4.8 finding type)
  ↓ bc_violation/aggregate_violation/ubiquitous_language_drift emit (영역 3 anchor ↔ 영역 4 finding)
S6 (본 worked example)
  → 5 영역 evidence enumeration = INV-5 최종 입증 (영역 5 ADR acceptance criteria)
```

이 연결고리 안에서 어휘 emit (S2 frontmatter) 이 spawn decision (S5) → review anchor 작성 (S3) → review finding emit (S4) → ADR acceptance (S6) 로 **실제 decision flow 를 변경**한다. 어느 한 단계라도 "어휘만 emit, 다음 단계 변경 0" 이면 vocabulary theater 실패 — 본 worked example 은 5 단계 전수 연결을 입증한다.

### INV-5 결론

- **vocabulary theater anti-pattern 차단** = 6 Story 전수 acceptance criteria (S1 charter glossary/concept / S2 frontmatter / S3 template+lint / S4 finding enum / S5 deputy layer / S6 본 FINAL VERDICT).
- **runtime 6× lesson 해소** — mctrader cross-repo Story 의 interpretation drift (MCT-170/177/179/180/184/185 Phase 0 verify pattern) 가 BC/ACL/OHS/Conformist 명시 어휘 + bc_violation P0 차단으로 해소.
- **단순 문서 향상 아님** — 5 영역 각각이 lint fail signal (#1) / spawn count (#2) / review anchor (#3) / review verdict (#4) / ADR acceptance (#5) 의 실 behavioral 변화 evidence 보유.
- **Codex BIG CONCERN 최종 입증 PASS** — 어휘 emit 이 spawn decision · review findings · ADR acceptance criteria 를 실제로 변경함이 5 영역 enumeration evidence 로 확정.

---

## Downstream Epic gate note

본 S6 LAND + worked example PASS = **mctrader DDD downstream Epic 진입 gate**:

- mctrader application BC charter ADR + Top 10 ADR (ADR-029~033 + 영향도 5) retroactive DDD annotation + `mctrader-hub/docs/glossary.md` SSOT 신설 = **별 CFP** (downstream Epic, 본 codeforge governance BC 영역 외).
- 본 worked example 은 mctrader ADR-031 을 **cite only** (mctrader-hub repo 변경 0). Published Language 분리 (ADR-091 §결정 4) 정합 — codeforge governance BC ↔ mctrader application BC 동음이의 차단.
- CFP-1117 Epic 6 Story (S1-S6) 완결 → ArchitectLane DDD vocabulary governance = codeforge governance BC 영구 정책 (ADR-091 `is_transitional: false`, ratchet 강화 방향만 허용).
