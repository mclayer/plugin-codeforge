---
kind: contract
contract_version: "2.0"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-design (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008
  - ADR-009
  - ADR-010
  - ADR-014
breaking_changes:
  - "deputies_results 에 op_risk_arch 추가 (5 deputy → 6 deputy) — OperationalRiskArchitectAgent neutral peer"
  - "chief_author_artifact.sections_authored 에 §7.4 운영 리스크 5 sub-item 명시 (DR / Cancel-on-disconnect / Clock sync CONDITIONAL / Rate limit / Env isolation)"
  - "chief_author_artifact.sections_authored 에 §11.6 Idempotency invariant (CONDITIONAL) 명시"
  - "§7 sub-numbering shift: 기존 §7.4 민감 → §7.5 / 기존 §7.5 위협매핑 → §7.6 / 기존 §7.6 N/A → §7.7"
  - "§11 sub-numbering shift: 기존 §11.6 N/A → §11.7"
  - "writes_completed.story_section_7 / story_section_11 의 mirror 범위 확장 (§7.4 / §11.6 신규 sub-section 포함)"
authors:
  - CFP-40 ζ arc — Design lane extraction (LAST, 2026-04-29) [v1 base]
  - CFP-46 — Operational Risk Architect (BREAKING bump, 2026-04-30) [v2]
---

# design_output v2 — Inter-plugin Contract

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-design/docs/inter-plugin-contracts/design-output-v2.md`: **canonical** (codeforge-design repo)
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — ADR-010 + CFP-24 marketplace sync 정책 동질)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- ADR-010 (본 contract 의 sibling sync 정책): codeforge wrapper repo `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`
- ADR-014 (carrier — v1 → v2 BREAKING bump): codeforge wrapper repo `docs/adr/ADR-014-operational-risk-ssot-distribution.md`

`codeforge-design` plugin → `codeforge` core (Orchestrator) 단방향 schema. ArchitectPLAgent 가 **6 deputies** 병렬 spawn 후 ArchitectAgent (chief author) 가 Change Plan + ADR + Story §3/§7/§11 mirror self-write.

**Carrier ADR**: [ADR-014 — Operational Risk SSOT distribution](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-014-operational-risk-ssot-distribution.md) (CFP-46)

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① design_packet (Story §1-7 + 관련 ADR list + 코드 경로)
        ▼
codeforge-design plugin
  └─ ArchitectPLAgent
        │
        │ ② 6 deputies 병렬 spawn (한 메시지)
        ▼
  ├─ CodebaseMapperAgent           (보수 — as-is 변호자)
  ├─ RefactorAgent                 (혁신 — 결합도/구조 옹호자)
  ├─ SecurityArchitectAgent        (위협 — trust boundary/auth/data 변호자)
  ├─ OperationalRiskArchitectAgent (운영 — DR/disconnect/clock/rate/env 변호자, CFP-46)
  ├─ TestContractArchitectAgent    (§8 Test Contract author input)
  └─ DataMigrationArchitectAgent   (§11 데이터 마이그레이션 author input)
        │
        │ ③ 6 결과 PL 에 return
        ▼
  └─ ArchitectAgent (chief author) spawn
        │
        │ ④ 통합 + Change Plan §1-11 + 신규 ADR draft author
        │    (§7.4 운영 리스크 5 sub-item / §11.6 idempotency CONDITIONAL 포함)
        │
        │ ⑤ Self-write:
        │    - Edit(docs/change-plans/<slug>.md) — 본 plugin owner
        │    - Edit(docs/adr/ADR-NNN-<slug>.md) — 본 plugin owner
        │    - Edit(docs/stories/<KEY>.md §3 ADR list mirror)
        │    - Edit(docs/stories/<KEY>.md §7 보안 설계 mirror — §7.1-§7.7 전체 포함)
        │    - Edit(docs/stories/<KEY>.md §11 데이터 마이그레이션 mirror — §11.1-§11.7 전체 포함)
        │    - mcp__github__add_issue_comment ([설계] prefix)
        │    - mcp__github__issue_write (phase:설계 → phase:설계-리뷰)
        ▼
        │ ⑥ design_output v2 typed return
        ▼
codeforge core (Orchestrator)
        │
        │ ⑦ 처리:
        │    - PASS → 설계 리뷰 lane 진입 (codeforge-review)
        │    - FIX (chief author 미흡) → ArchitectAgent 재스폰
```

## 2. design_packet (Orchestrator → ArchitectPLAgent)

```yaml
design_packet:
  contract_version: "2.0"
  story_key: <STORY_KEY>
  story_sections_1_to_7: <markdown>     # 필수
  related_adr_paths:                    # 필수 — Story §3 fetch
    - docs/adr/ADR-NNN-<slug>.md
  related_code_paths:                   # 필수 — Story §4
    - <path glob>
  project_config:                       # 필수 — overlay
    domain: <string>
```

## 3. design_output (ArchitectPL → Orchestrator)

```yaml
design_output:
  contract_version: "2.0"
  story_key: <STORY_KEY>

  status: PASS | FIX_CHIEF_AUTHOR_REVISION | ESCALATE_PACKET_INCOMPLETE

  deputies_results:                     # 필수 — 6 deputy 결과 audit (BREAKING — was 5)
    codebase_mapper:
      coverage_observations: <int>
      preservation_concerns: [<list>]
    refactor:
      proposals: <int>
      proposal_paths: [<list>]
    security_arch:
      trust_boundaries_identified: <int>
      threat_model_completeness: <enum: stride-lite | partial | minimal>
    op_risk_arch:                       # NEW v2 — CFP-46 / ADR-014
      dr_strategies: <int>              # §7.4.1 외부 의존 장애 모드 enumeration count
      cancel_on_disconnect: <bool>      # §7.4.2 적용 여부
      clock_sync_applicable: <bool>     # §7.4.3 CONDITIONAL — time-window 프로토콜 의존 여부
      rate_limit_policies: <int>        # §7.4.4 throttle / circuit breaker policy count
      env_isolation_layers: <int>       # §7.4.5 staging/prod 분리 layer count
    test_contract_arch:
      coverage_targets: <int>
      contract_invariants: <int>
    data_migration_arch:
      schema_changes: <int>
      rollback_strategies: <int>
      idempotency_applicable: <bool>    # NEW v2 — §11.6 CONDITIONAL 적용 여부

  chief_author_artifact:
    change_plan_path: docs/change-plans/<slug>.md
    new_adr_paths:                      # 신규 ADR 경로 array
      - docs/adr/ADR-NNN-<slug>.md
    sections_authored:                  # §1-11 중 본 iteration 에서 작성·갱신된 섹션 (BREAKING — §7.4 / §11.6 추가)
      - "§3 도입할 설계"
      - "§7.1 Trust boundary"
      - "§7.2 Threat model (STRIDE-LITE)"
      - "§7.3 Auth/Authz 설계"
      - "§7.4 운영 리스크 (DR / Cancel-on-disconnect / Clock sync CONDITIONAL / Rate limit / Env isolation)"  # NEW v2
      - "§7.5 민감 데이터 분류 + 흐름"  # was §7.4 in v1
      - "§7.6 위협 ↔ 완화 매핑"        # was §7.5 in v1
      - "§7.7 N/A 명시"                # was §7.6 in v1
      - "§8 Test Contract"
      - "§11.1 Schema 변경 영향"
      - "§11.2 Migration 전략"
      - "§11.3 Rollback 경로"
      - "§11.4 Data integrity invariant"
      - "§11.5 Backfill / 기존 데이터 처리"
      - "§11.6 Idempotency invariant (CONDITIONAL)"  # NEW v2
      - "§11.7 N/A 명시"               # was §11.6 in v1

  # PL self-write 결과 audit
  writes_completed:
    change_plan: <bool>                 # docs/change-plans/<slug>.md
    new_adrs: <int>                     # 신규 ADR 파일 수
    story_section_3: <bool>             # ADR list mirror
    story_section_7: <bool>             # 보안 설계 mirror (§7.1-§7.7 전체 포함, §7.4 운영 리스크 포함)
    story_section_11: <bool>            # 데이터 마이그레이션 mirror (§11.1-§11.7 전체 포함, §11.6 idempotency CONDITIONAL 포함)
    phase_comment: <bool>               # [설계] prefix
    phase_label_transitioned: <bool>    # phase:설계 → phase:설계-리뷰
```

## 4. 6 deputy 산출물 통합 표 (chief ArchitectAgent 통합 가이드)

ArchitectAgent (chief author) 가 6 deputy 산출물을 받아 Change Plan §1-§11 본문에 통합. 각 deputy 의 primary 책임 sub-section 과 consult 책임은 다음 표 SSOT.

| Deputy | Primary 책임 (직접 author) | Consult 책임 (chief 가 cross-ref 시 confer) |
|---|---|---|
| **CodebaseMapperAgent** | §2 현재 구조 분석 (as-is fact) | §3 도입할 설계 (3-way 대립 input), §6 리팩토링 선행 |
| **RefactorAgent** | §6 리팩토링 선행 작업 | §3 도입할 설계 (3-way 대립 input) |
| **SecurityArchitectAgent** | §7.1 Trust boundary, §7.2 Threat model, §7.3 Auth/Authz, §7.5 민감 데이터, §7.6 위협↔완화, §7.7 N/A | §11 데이터 마이그레이션 (PII / Secret 흐름 짝) |
| **OperationalRiskArchitectAgent** | §7.4.1 DR, §7.4.2 Cancel-on-disconnect, §7.4.3 Clock sync CONDITIONAL, §7.4.4 Rate limit, §7.4.5 Env isolation | §11.6 Idempotency invariant (재시도/disconnect 후 재진입 짝), §7.6 위협↔완화 매핑 (DR↔failover) |
| **TestContractArchitectAgent** | §8 Test Contract (§8.1-§8.4) | §1 수용 기준 (테스트 가능성 검증) |
| **DataMigrationArchitectAgent** | §11.1 Schema 영향, §11.2 Migration 전략, §11.3 Rollback, §11.4 Invariant, §11.5 Backfill, §11.6 Idempotency CONDITIONAL, §11.7 N/A | §7.5 민감 데이터 (PII/Secret 흐름 짝), §11.6 OpRiskArch consult (재진입 짝) |

> **OperationalRiskArchitectAgent 와 SecurityArchitectAgent 의 분담** (ADR-014):
> - SecurityArch = "trust boundary 위반 / auth 결함 / data exfil" (공격자 perspective)
> - OpRiskArch = "외부 장애 / disconnect / clock drift / rate limit / env 누출" (production-readiness perspective)
> - Overlap (예: env isolation 의 secret 누출 측면) → SecurityArch (§7.5) + OpRiskArch (§7.4.5) 양쪽 cross-ref. chief author dedup 의무.

## 5. ESCALATE 처리

- `FIX_CHIEF_AUTHOR_REVISION`: PL 검수 RETURN — chief author 재스폰 필요. PL 이 clarification context 첨부
- `ESCALATE_PACKET_INCOMPLETE`: Story §1-7 또는 ADR list 부재

## 6. BREAKING from v1

본 v2 는 v1 대비 BREAKING — `deputies_results` schema 변경 + `chief_author_artifact.sections_authored` 의 §7 / §11 sub-numbering shift 로 producer / consumer 양측 코드 변경 의무.

### Schema 변경 enumeration

1. **`deputies_results.op_risk_arch` 추가** (신규 6번째 deputy) — 5 field (dr_strategies / cancel_on_disconnect / clock_sync_applicable / rate_limit_policies / env_isolation_layers)
2. **`deputies_results.data_migration_arch.idempotency_applicable` 추가** — §11.6 CONDITIONAL 적용 여부 audit
3. **`chief_author_artifact.sections_authored` 의 §7 sub-numbering shift**:
   - 신규 §7.4 운영 리스크 (5 sub-item) 추가
   - 기존 §7.4 민감 데이터 → §7.5
   - 기존 §7.5 위협 ↔ 완화 매핑 → §7.6
   - 기존 §7.6 N/A 명시 → §7.7
4. **`chief_author_artifact.sections_authored` 의 §11 sub-numbering shift**:
   - 신규 §11.6 Idempotency invariant (CONDITIONAL) 추가
   - 기존 §11.6 N/A 명시 → §11.7
5. **`writes_completed.story_section_7` / `story_section_11` 의 mirror 범위 확장** — §7.4 / §11.6 신규 sub-section 포함 의무 (consumer 측 검증 로직 갱신 필요)
6. **흐름 diagram 의 deputy count**: "5 deputies" → "6 deputies" (모든 spawn 시퀀스 코드 갱신 의무)

### Carrier ADR

- **[ADR-014 — Operational Risk SSOT distribution](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-014-operational-risk-ssot-distribution.md)** (CFP-46) — DR / Cancel-on-disconnect / Clock sync / Rate limit / Env isolation 5 항목을 OperationalRiskArchitectAgent SSOT 로 통합 결정 + §11.6 Idempotency invariant CONDITIONAL 신설 결정
- **[ADR-008 — Inter-plugin Contract Versioning](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-008-inter-plugin-contract-versioning.md)** — v1 → v2 BREAKING bump 룰 적용 (양쪽 plugin 동시 bump + 새 carrier ADR)
- **[ADR-010 — Inter-plugin Contract Sibling Sync](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)** — wrapper sibling PR-F 가 본 PR-E 직후 진행

### Migration 가이드 (consumer / wrapper)

- **wrapper sibling sync** (PR-F): `mclayer/plugin-codeforge/docs/inter-plugin-contracts/design-output-v2.md` 신규 + v1 sibling Archived + MANIFEST.yaml v2 entry 추가
- **wrapper Orchestrator 코드** (PR-C): 6 deputy spawn 시퀀스 / `op_risk_arch` deputies_results 처리 / §7.4 / §11.6 mirror 검증 갱신
- **codeforge-review 의 design-review-pl** (후속 — out-of-scope of CFP-46): §7.4 / §11.6 P0 차단 룰 audit (ALREADY in templates/change-plan.md, but contract surface formalization)

## 7. v2 → v3 변경 가능성 (forward-looking)

- 새 deputy 추가 (예: AccessibilityArchitectAgent · I18nArchitectAgent) — minor (deputies_results schema 확장)
- 새 mirror section 추가 (§12 등) — minor
- §7.4 sub-item 추가 (예: §7.4.6 chaos engineering) — minor (CONDITIONAL 우선)
- §11.6 의 CONDITIONAL → MANDATORY 승격 — major (BREAKING)

## 8. 동결 ATTRIBUTION

- v1 동결: 2026-04-29 (CFP-40, ζ arc LAST extraction) — Archived 2026-04-30 (CFP-46 PR-E)
- v2 동결: 2026-04-30 (CFP-46 — OperationalRiskArchitectAgent + idempotency CONDITIONAL)
- Source: CFP-31 §5.10 (v1) + CFP-46 spec/plan (v2)
