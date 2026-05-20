# [CFP-1117-S6] Golden-path worked example — mctrader ADR-031 + INV-5 FINAL VERDICT (Phase 2 PR5)

**parent_epic**: CFP-1117  
**LAND order**: Phase 2 PR5 (depends on S1, S2, S3, S4, S5 — 마지막 Story)

## WHY

mctrader **ADR-031 data-domain-decoupling** (4-Layer 모델 + Open Host Service + Anti-Corruption Layer 동시 보유) 를 golden-path worked example 대상. `examples/ddd-golden-path-mct031.md` 신규 — before/after worked example 5 영역 박제로 **INV-5 (vocabulary theater 차단 forcing function) FINAL VERDICT evidence enumeration**.

**Vocabulary theater 차단 evidence (INV-5 binding, FINAL VERDICT)**: 본 Story = Codex BIG CONCERN 차단 의무의 **최종 binding**. 본 Story LAND = vocabulary theater 차단 forcing function 의 EVIDENCE 완성. 본 Story LAND 전 = forcing function declaration only / 본 Story LAND 후 = forcing function evidence enumerated.

### mctrader ADR-031 4-Layer 모델 (verbatim cite, line 499-524)

```
Layer 0 ─ mctrader-market (FOUNDATION, 의존 0, 순수 pydantic/sqlalchemy, data 비의존)
   • 도메인 어휘: Symbol·Timeframe·Decimal38_18·UTCDateTime·OrderStatus·lifecycle
   • wire contract: TickRowV1_1·InformationBarModel·CandleModel/CandleLike·OrderBookLike
   • exchange-neutral Protocol: CandleProvider·OrderBookProvider(기존) + (신규)RealtimeStream
   • ◀ RELOCATE (MCT-182, D1): aggregation algo + TickRecord/OrderbookEventRecord dataclass + PaperLineage
Layer 1 ─ 거래소 어댑터 (각각 → market 만, market Protocol 구현)  [ACL pattern]
   mctrader-market-bithumb · mctrader-market-upbit · -<해외> · -<한국거래소> ...
Layer 2 ─ mctrader-data (DATA-STORAGE 영역 단독 소유, → market + → 어댑터들)  [OHS pattern]
   • adapters.py 팩토리: 모든 거래소 ingestion 단일 경계
   • NEW api/(FastAPI): /v1 historical(Arrow IPC) + 역방향 POST + 정규화 stream(Redis Stream)
Layer 2'─ mctrader-engine (PURE CONSUMER, mctrader_data=0, mctrader_market_*=0)
   • 의존 = Layer 0(market 어휘/contract/algo) + data /v1(REST + 정규화 실시간 stream)

핵심 확장성 불변식 (D5): 새 거래소 = ① 신규 Layer1 어댑터 repo ② data adapters.py 등록
    ③ data 수집/정규화 설정 → engine 변경 0, market-core 변경 0, ADR 0
순환: 영원히 없음 (market→누구도 의존 안 함, data→market+어댑터, engine→market+REST)
```

(mctrader-hub `docs/adr/ADR-031-data-domain-decoupling.md` line 499-524, verbatim verified 2026-05-20 KST)

본 4-Layer 모델 = **OHS (Layer 2 /v1 REST API endpoint, line 514)** + **ACL (Layer 1 거래소 어댑터 → market Protocol 구현, line 508-509)** 동시 보유 사례.

## Acceptance criteria

| AC | 설명 | 검증 |
|---|---|---|
| AC-6.1 | `examples/ddd-golden-path-mct031.md` 신규 + mctrader ADR-031 line 499-524 4-Layer 모델 verbatim 박제 | grep "Layer 0 ─ mctrader-market" examples/ddd-golden-path-mct031.md |
| AC-6.2 | OHS / ACL identification — Layer 2 /v1 REST API = OHS / Layer 1 거래소 어댑터 = ACL 명시 | grep "Open Host Service" + "Anti-Corruption Layer" examples/ddd-golden-path-mct031.md ≥ 2 |
| AC-6.3 | Before/after Story field 박제 (영역 1) — mctrader Story (예: MCT-182) `§ubiquitous_language` 안 BC 명시 (mctrader application BC: data / engine / market) | examples/ddd-golden-path-mct031.md 안 §"영역 1: Story field" 섹션 |
| AC-6.4 | Before/after deputy spawn rationale 박제 (영역 2) — ArchitectPL spawn rationale "perspective-contributor" → "which subdomain under threat = data persistence" 어휘 transition | examples/ddd-golden-path-mct031.md 안 §"영역 2: deputy spawn rationale" |
| AC-6.5 | Before/after Change Plan DDD field 박제 (영역 3) — Change Plan §bounded_context_boundary + §affected_aggregates 안 explicit BC + Aggregate 박제 | examples/ddd-golden-path-mct031.md 안 §"영역 3: Change Plan DDD field" |
| AC-6.6 | Before/after review-verdict finding 박제 (영역 4) — DesignReviewPL 가 `bc_violation` (4-Layer 경계 위반) + `ubiquitous_language_drift` (Storage 어휘 mctrader 측 SSOT 와 drift) finding type 실 emit 사례 1건 이상 | examples/ddd-golden-path-mct031.md 안 §"영역 4: review-verdict finding" + finding type 3 enum 등장 |
| AC-6.7 | Before/after ADR acceptance criteria 박제 (영역 5) — ADR-087 §결정 N + ADR-031 의 4-Layer 모델 위 OHS / ACL identification 이 DDD acceptance criteria 추가 | examples/ddd-golden-path-mct031.md 안 §"영역 5: ADR acceptance criteria" |
| **AC-INV-5-S6 (FINAL VERDICT)** | **본 worked example 안 §"FINAL VERDICT: vocabulary theater 차단 evidence enumeration" 섹션 — 5 영역 박제 evidence 가 (a) spawn decision 변경 (b) review findings type 변경 (c) ADR acceptance criteria 변경 3 enumeration 의무. 본 §LAND = INV-5 완성** | grep "FINAL VERDICT" + grep "vocabulary theater" + 3-enum evidence cross-validation |

## Test contract

본 Story = INV-5 의 FINAL VERDICT — vocabulary theater 차단 forcing function 의 evidence enumeration. test contract 자체 = 5 영역 박제 evidence 의 explicit declaration.

### evidence enumeration (FINAL VERDICT 섹션 content 예고)

```markdown
## FINAL VERDICT: vocabulary theater 차단 evidence enumeration

본 worked example 의 5 영역 박제가 다음 3 enumeration 으로 vocabulary theater 차단 forcing function 의 evidence 를 완성한다:

### Enumeration 1: spawn decision 변경 evidence
Before — ArchitectPLAgent 가 MCT-182 Story 진입 시 deputy spawn rationale: "data persistence perspective contributor 필요"
After — ArchitectPLAgent 가 MCT-182 Story 진입 시 deputy spawn rationale: "which subdomain under threat = data persistence subdomain (mctrader-data BC) — Subdomain Specialist (AggregateArchitectAgent + DataArchitectAgent) spawn"
Δ — 어휘 transition 만이 아닌, deputy spawn enum 가 4-way RACI matrix (CFP-1086) 안 specific row 활성화 + Subdomain Specialist mapping layer 안 명시 enum 적용. spawn decision 의 mechanical 변경.

### Enumeration 2: review findings type 변경 evidence
Before — DesignReviewPL 가 MCT-182 review 시 generic finding: "P1 data domain coupling 위반"
After — DesignReviewPL 가 MCT-182 review 시 specific finding type emit:
  - `bc_violation`: Layer 0 (market BC) → Layer 2 (data BC) 역방향 의존 감지
  - `aggregate_violation`: TickRecord dataclass 가 Layer 0 (market) 의 aggregate consistency boundary 안 위치해야 함 (Layer 2 pyarrow schema 와 별)
  - `ubiquitous_language_drift`: "Storage" 어휘가 mctrader Storage subdomain SSOT 와 drift
Δ — review-verdict-v4 v4.8 finding type enum 가 specific severity routing + dedup mechanism 변경. semantic accountability 의 mechanical evidence.

### Enumeration 3: ADR acceptance criteria 변경 evidence
Before — ADR-031 acceptance criteria: "INV-3 = TickRecord dataclass 가 pyarrow 비결합"
After — ADR-031 acceptance criteria + ADR-087 cross-ref:
  - INV-3 (기존) + DDD Acceptance criterion: Layer 0 market BC = Foundation Subdomain (Core) + Layer 2 data BC = Storage Subdomain (Supporting) + Layer 2 = OHS endpoint (/v1 REST API) + Layer 1 거래소 어댑터 = ACL pattern
Δ — ADR acceptance criteria 가 strategic design (BC + Subdomain) + tactical pattern (OHS + ACL) 명시 의무. ADR 검증 항목 자체 변경.
```

## Dependencies

- S1 LAND (ADR-087 §결정 7 forcing function 정의)
- S2 LAND (15 agent frontmatter `ddd_pattern` + role description "which subdomain under threat" 어휘)
- S3 LAND (template field + lint script Wave 1 wire)
- S4 LAND (review-verdict-v4 v4.8 finding type 3 enum)
- S5 LAND (skills/deputy-mandate Subdomain Specialist layer)
- precedent (external read-only): mctrader-hub `docs/adr/ADR-031-data-domain-decoupling.md` (변경 0)

## Scope

### In
- `examples/ddd-golden-path-mct031.md` 신규
- 5 영역 박제 (Story field / deputy spawn rationale / Change Plan DDD field / review-verdict finding / ADR acceptance criteria) before/after
- FINAL VERDICT INV-5 evidence enumeration 3 enumeration 섹션

### Out
- mctrader ADR-031 실 변경 (N/A — external read-only reference)
- mctrader 6 repo BC charter 박제 (downstream Epic)
- mctrader Top 10 ADR retroactive annotation (downstream Epic)

## 5-checklist self-application

| Axis | 결과 |
|---|---|
| 1. 결정 영역 | worked example documentation — axis 1 영역 외 |
| 2. cost | N/A |
| 3. consumer impact | wrapper 단독 SSOT (read-only reference of mctrader 측 ADR) |
| 4. sibling cross-ref | ADR-087 §결정 7 + ADR-031 (mctrader, read-only) |
| 5. deferred carrier | **mctrader downstream Epic (별 CFP) — upstream 본 Story LAND + worked example 시연 PASS 후 진입** (Q3 confirm 정합) |

**통과** + **본 Story = upstream Epic 의 마지막 Story, downstream Epic gate**.

## 후속 (별 CFP, downstream Epic)

본 Story LAND 후 downstream Epic 진입 가능:

- mctrader-hub `docs/glossary.md` SSOT 신규 (Published Language 분리, 별 SSOT)
- mctrader 6 repo BC charter 박제 (hub=Governance / data=Storage / engine=Trading / market=SharedKernel / signal-collector=Acquisition / web=Presentation 6 entry)
- Top 10 ADR retroactive annotation (ADR-029~033 + 영향도 기준 5 추가)
- mctrader 어휘 검증 cron (`scripts/glossary-drift-check.py` + GH Action)
