---
kind: contract
contract_version: "2.5"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-design (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008
  - ADR-009
  - ADR-010
  - ADR-014
  - ADR-033
  - ADR-145  # v2.5 carrier — ac_coverage_self_check_passed marker (요건 traceability zero-drop 게이트 §결정 6)
breaking_changes:
  - "deputies_results 에 op_risk_arch 추가 (5 SubAgent → 6 SubAgent) — OperationalRiskArchitectAgent neutral peer"
  - "chief_author_artifact.sections_authored 에 §7.4 운영 리스크 5 sub-item 명시 (DR / Cancel-on-disconnect / Clock sync CONDITIONAL / Rate limit / Env isolation)"
  - "chief_author_artifact.sections_authored 에 §11.6 Idempotency invariant (CONDITIONAL) 명시"
  - "§7 sub-numbering shift: 기존 §7.4 민감 → §7.5 / 기존 §7.5 위협매핑 → §7.6 / 기존 §7.6 N/A → §7.7"
  - "§11 sub-numbering shift: 기존 §11.6 N/A → §11.7"
  - "writes_completed.story_section_7 / story_section_11 의 mirror 범위 확장 (§7.4 / §11.6 신규 sub-section 포함)"
authors:
  - CFP-40 ζ arc — Design lane extraction (LAST, 2026-04-29) [v1 base]
  - CFP-46 — Operational Risk Architect (BREAKING bump, 2026-04-30) [v2]
  - CFP-47 — TestContractArch §8.5 mandate (additive minor, 2026-04-30) [v2.1]
  - CFP-128 — Docker-first infra (§7.4.6 Container considerations, additive minor, 2026-05-07) [v2.2]
  - CFP-662 — spec_invariant_measurement_required field (additive minor, 2026-05-14) [v2.3]
---

# design_output v2 — Inter-plugin Contract

`codeforge-design` plugin → `codeforge` core (Orchestrator) 단방향 schema. ArchitectPLAgent 가 **6 deputies** 병렬 spawn 후 ArchitectAgent (chief author) 가 Change Plan + ADR + Story §3/§7/§11 mirror self-write.

**상위 SSOT 위치**: 본 파일이 단일 원본 (canonical) — CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5 가 lane canonical ↔ wrapper mirror 이중체계를 폐지 (monorepo 통합 S1 후속). frontmatter 의 ADR-010 인용은 historical (sibling sync 정책 Superseded — ADR-010 Amendment 5). versioning 룰 = ADR-008 불변.

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
  contract_version: "2.5"
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
  contract_version: "2.5"
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
    op_risk_arch:                       # NEW v2 — CFP-46 / ADR-014 (extended v2.2 — CFP-128 / ADR-033)
      dr_strategies: <int>              # §7.4.1 외부 의존 장애 모드 enumeration count
      cancel_on_disconnect: <bool>      # §7.4.2 적용 여부
      clock_sync_applicable: <bool>     # §7.4.3 CONDITIONAL — time-window 프로토콜 의존 여부
      rate_limit_policies: <int>        # §7.4.4 throttle / circuit breaker policy count
      env_isolation_layers: <int>       # §7.4.5 staging/prod 분리 layer count
      container_considerations:         # NEW v2.2 — CFP-128 / ADR-033, CONDITIONAL on infra_strategy: docker_first
        applicable: <bool>              # project.yaml infra_strategy == docker_first 시 true
        restart_policy: <always | on-failure[:N] | unless-stopped | no | N/A>
        volume_dr:
          type: <anonymous | named | bind | N/A>
          backup_strategy: <text | N/A>
          host_path_leak_mitigation: <text | N/A>
        health_check:
          interval: <duration | N/A>
          timeout: <duration | N/A>
          retries: <int | N/A>
          start_period: <duration | N/A>
        network_mode: <bridge | overlay | macvlan | N/A>  # host 금지 (internal service)
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
      - "§7.4.6 Container considerations (CONDITIONAL — Docker-first, restart policy / volume DR / health check / network mode)"  # NEW v2.2 — CFP-128 / ADR-033
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
      - "§8.5 Stateful / restart invariant tests (CONDITIONAL — CFP-47 / ADR-015)"  # NEW v2.1 — additive

    spec_invariant_measurement_required: <bool>  # NEW v2.3 — CFP-662. chief author artifact 가 spec invariant measurement 의무를 명시했는지 marker. default false. 후속 carrier 가 의무화 / 검증 로직 추가 예정.

    ac_coverage_self_check_passed: <bool>  # NEW v2.5 — CFP-2603 / ADR-145 §결정 6. chief author 가 authoritative Test Contract location 에서 AC↔§8 coverage self-check (모든 normative AC-N → ≥1 §8 명명 테스트 매핑) 통과 보고 marker. default false. self-check disjoint 축 group (architecture_doc_updated / mechanical_self_check_passed 등) 과 peer. location 은 문서유형별 resolve (wrapper-self dogfood = Change Plan §8 / consumer = Story §8 mirror — "Story §8" 하드코딩/단정 금지). packet 에 RTM 중복 금지 (marker bool 만).

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

## 4. 6 SubAgent 산출물 통합 표 (chief ArchitectAgent 통합 가이드)

ArchitectAgent (chief author) 가 6 SubAgent 산출물을 받아 Change Plan §1-§11 본문에 통합. 각 SubAgent 의 primary 책임 sub-section 과 consult 책임은 다음 표 SSOT.

| Deputy | Primary 책임 (직접 author) | Consult 책임 (chief 가 cross-ref 시 confer) |
|---|---|---|
| **CodebaseMapperAgent** | §2 현재 구조 분석 (as-is fact) | §3 도입할 설계 (3-way 대립 input), §6 리팩토링 선행 |
| **RefactorAgent** | §6 리팩토링 선행 작업 | §3 도입할 설계 (3-way 대립 input) |
| **SecurityArchitectAgent** | §7.1 Trust boundary, §7.2 Threat model, §7.3 Auth/Authz, §7.5 민감 데이터, §7.6 위협↔완화, §7.7 N/A | §11 데이터 마이그레이션 (PII / Secret 흐름 짝) |
| **OperationalRiskArchitectAgent** | §7.4.1 DR, §7.4.2 Cancel-on-disconnect, §7.4.3 Clock sync CONDITIONAL, §7.4.4 Rate limit, §7.4.5 Env isolation, **§7.4.6 Container considerations (CONDITIONAL Docker-first, CFP-128 / ADR-033)** | §11.6 Idempotency invariant (재시도/disconnect 후 재진입 짝), §7.6 위협↔완화 매핑 (DR↔failover) |
| **TestContractArchitectAgent** | §8 Test Contract (§8.1-§8.4) | §1 수용 기준 (테스트 가능성 검증) |
| **DataMigrationArchitectAgent** | §11.1 Schema 영향, §11.2 Migration 전략, §11.3 Rollback, §11.4 Invariant, §11.5 Backfill, §11.6 Idempotency CONDITIONAL, §11.7 N/A | §7.5 민감 데이터 (PII/Secret 흐름 짝) |

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

1. **`deputies_results.op_risk_arch` 추가** (신규 6번째 SubAgent) — 5 field (dr_strategies / cancel_on_disconnect / clock_sync_applicable / rate_limit_policies / env_isolation_layers)
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
6. **흐름 diagram 의 SubAgent count**: "5 deputies" → "6 deputies" (모든 spawn 시퀀스 코드 갱신 의무)

### Additive minor — v2.0 → v2.1 (CFP-47, 2026-04-30)

본 v2.1 은 v2.0 대비 **additive minor** — `sections_authored` 에 §8.5 entry 1 줄 추가만. deputies_results / writes_completed 변경 없음. v2.0 consumer 가 v2.1 verdict 받아도 §8.5 entry 무시 — backward-compat.

#### Schema 변경 enumeration (v2.0 → v2.1)

1. **`chief_author_artifact.sections_authored` 에 §8.5 entry 추가** — TestContractArch §8.5 mandate (CFP-47 / ADR-015)

#### Carrier ADR (v2.1)

- **[ADR-015 — Stateful test category](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-015-stateful-test-category.md)** (CFP-47) — TestContractArchitectAgent mandate 에 §8.5 추가. 신규 SubAgent 미도입. design-output additive minor in-place bump.

### Additive minor — v2.1 → v2.2 (CFP-128, 2026-05-07)

본 v2.2 는 v2.1 대비 **additive minor** — `deputies_results.op_risk_arch.container_considerations` block 추가 + `sections_authored` 에 §7.4.6 entry 1 줄 추가. ADR-014 가 ADR-033 에 의해 amend 됨. v2.1 consumer 가 v2.2 verdict 받아도 미지 field 무시 — backward-compat. CONDITIONAL on `project.yaml infra_strategy: docker_first` — legacy_systemd / none 환경 = N/A.

#### Schema 변경 enumeration (v2.1 → v2.2)

1. **`deputies_results.op_risk_arch.container_considerations` 추가** — 5 sub-field (applicable / restart_policy / volume_dr / health_check / network_mode). CONDITIONAL on Docker-first.
2. **`chief_author_artifact.sections_authored` 에 §7.4.6 entry 추가** — Container considerations sub.
3. **6 SubAgent 통합 표 (§4) 의 OpRiskArch row 의 Primary 책임 컬럼에 §7.4.6 추가** — restart policy / volume DR / health check / network mode 4 항목.

#### Carrier ADR (v2.2)

- **[ADR-033 — Docker-first infra engineering](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-033-docker-first-infra-engineering.md)** (CFP-128) — ADR-014 amend by. OpRiskArch §7.4 mandate 에 §7.4.6 Container considerations 추가. 신규 SubAgent 미도입 — additive minor in-place bump.

### Additive minor — v2.2 → v2.3 (CFP-662, 2026-05-14)

본 v2.3 은 v2.2 대비 **additive minor** — `chief_author_artifact.spec_invariant_measurement_required: bool` optional field 1개 추가만. deputies_results / writes_completed 변경 없음. v2.2 consumer 가 v2.3 verdict 받아도 신규 field 무시 — backward-compat.

**새 field**: `chief_author_artifact.spec_invariant_measurement_required: bool` (additive minor, ADR-008 §결정 2 정합 — optional field 추가 = MINOR).

**Trigger**: codeforge-develop CFP-662 PR #25 (SHA `13a4e773f25b1942f8bc85ef573d35c7d8b23880`) — DeveloperPLAgent + QADeveloperAgent spec invariant 명시 의무 sub-section 도입 (ADR-068 §결정 1 I-3 + I-5 Tier D 정합).

**Purpose**: chief author artifact (Change Plan §3 / §7 / §11 등) 이 spec invariant measurement 의무를 명시했는지 marker (boolean carrier). 후속 carrier 가 본 field 의 의무화 / 검증 로직 추가 예정.

#### Schema 변경 enumeration (v2.2 → v2.3)

1. **`chief_author_artifact.spec_invariant_measurement_required` 추가** — boolean optional field, default `false`. spec invariant measurement 명시 여부 audit marker.

### Carrier ADR

- **[ADR-014 — Operational Risk SSOT distribution](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-014-operational-risk-ssot-distribution.md)** (CFP-46) — DR / Cancel-on-disconnect / Clock sync / Rate limit / Env isolation 5 항목을 OperationalRiskArchitectAgent SSOT 로 통합 결정 + §11.6 Idempotency invariant CONDITIONAL 신설 결정
- **[ADR-008 — Inter-plugin Contract Versioning](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-008-inter-plugin-contract-versioning.md)** — v1 → v2 BREAKING bump 룰 적용 (양쪽 plugin 동시 bump + 새 carrier ADR)
- **[ADR-010 — Inter-plugin Contract Sibling Sync](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)** — wrapper sibling PR-F 가 본 PR-E 직후 진행

### Migration 가이드 (consumer / wrapper)

- **wrapper sibling sync** (PR-F): `mclayer/plugin-codeforge/docs/inter-plugin-contracts/design-output-v2.md` 신규 + v1 sibling Archived + MANIFEST.yaml v2 entry 추가
- **wrapper Orchestrator 코드** (PR-C): 6 SubAgent spawn 시퀀스 / `op_risk_arch` deputies_results 처리 / §7.4 / §11.6 mirror 검증 갱신
- **codeforge-review 의 design-review-pl** (후속 — out-of-scope of CFP-46): §7.4 / §11.6 P0 차단 룰 audit (ALREADY in templates/change-plan.md, but contract surface formalization)

## 7. v2 → v3 변경 가능성 (forward-looking)

- 새 SubAgent 추가 (예: AccessibilityArchitectAgent · I18nArchitectAgent) — minor (deputies_results schema 확장)
- 새 mirror section 추가 (§12 등) — minor
- §7.4 sub-item 추가 (예: §7.4.6 chaos engineering) — minor (CONDITIONAL 우선)
- §11.6 의 CONDITIONAL → MANDATORY 승격 — major (BREAKING)

## 8. 동결 ATTRIBUTION

- v1 동결: 2026-04-29 (CFP-40, ζ arc LAST extraction) — Archived 2026-04-30 (CFP-46 PR-E)
- v2 동결: 2026-04-30 (CFP-46 — OperationalRiskArchitectAgent + idempotency CONDITIONAL)
- Source: CFP-31 §5.10 (v1) + CFP-46 spec/plan (v2)
- v2.1 동결: 2026-04-30 (CFP-47 — TestContractArch §8.5 mandate, additive minor in-place)
- v2.2 동결: 2026-05-07 (CFP-128 — §7.4.6 Container considerations, additive minor in-place; ADR-014 amended by ADR-033)
- v2.3 동결: 2026-05-14 (CFP-662 — chief_author_artifact.spec_invariant_measurement_required field 신설, additive minor in-place)

---

## v2.4 MINOR — `architecture_doc_updated` field (CFP-921)

**Carrier**: CFP-921 (Epic B Story-3) — ADR-078 lane gate mechanism.

### 신설 field

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `architecture_doc_updated` | bool | optional | `false` | ADR-078 lane gate carrier. `true` = ArchitectAgent 가 `docs/architecture/<path>.md` 4 영역 (modules/boundaries/interfaces/data_flow) 중 1+ 갱신 완료 보고. `false` = Change Plan §10.A `architecture_doc_impact` all false + `none_rationale` declare (skip 정당화). 누락 / mismatch = ArchitectPL `pl_recommendation: FIX` |

### Migration (v2.3 → v2.4)

- **Backward-compat MINOR** (ADR-008 §결정 2 — optional field default false)
- 기존 v2.3 producer → field omit 시 default `false` 적용
- 신규 v2.4 producer (post-CFP-921 ArchitectPL) → field 의무 emit (true 시 `docs/architecture/<path>.md` direct write 동반)
- Validator → field 부재 = `false` 가정 (backward-compat)
- Effective date: 2026-05-18 KST 이후 신규 design lane verdict packet (forward-only, ADR-079 §결정 6 동형)

### Disjoint axis (review-verdict-v4 v4.5 + design-output-v2 v2.4 동시 emit)

ADR-082 §결정 1 layer disjoint 정합 — design lane verdict packet 의 4 self-check boolean field 동시 emit:

- `mechanical_self_check_passed` (ADR-065) — 7-item mechanical sync
- `boundary_completeness_self_check_passed` (ADR-068) — I-1~I-4 semantic
- `dimensional_empirical_self_check_passed` (ADR-068 Amendment 1) — I-5 dimensional empirical
- **`architecture_doc_updated` (ADR-078, v2.4 신설)** — design-lane self-write verification (scope (b))
- `marketplace_sync_declared` (ADR-063 Amendment 1) — atomic invariant declare
- **`ac_coverage_self_check_passed` (ADR-145, v2.5 신설)** — AC↔§8 coverage self-check (authoritative Test Contract location, 문서유형별 resolve)

### Cross-references

- [ADR-078 architecture doc lane gate](../../archive/adr/ADR-078-living-architecture-doc.md) §결정 1 (4 wording SSOT)
- [ADR-082 write-time self-write verification](../../archive/adr/ADR-082-write-time-self-write-verification-mandate.md) scope (b)
- [ADR-008 inter-plugin contract versioning](../../archive/adr/ADR-008-inter-plugin-contract-versioning.md) §결정 2 (MINOR additive)
- [ADR-010 sibling sync ordering](../../archive/adr/ADR-010-inter-plugin-contract-sibling-sync.md) §결정 1 (canonical first → sibling follow)

---

## v2.5 MINOR — `ac_coverage_self_check_passed` marker (CFP-2603)

**Carrier**: CFP-2603 (Epic CFP-2602 G1) — [ADR-145](../../archive/adr/ADR-145-ac-traceability-zero-drop-gate.md) 요건 traceability zero-drop 게이트.

### 신설 field

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `chief_author_artifact.ac_coverage_self_check_passed` | bool | optional | `false` | ADR-145 §결정 6 marker. `true` = ArchitectAgent (chief author) 가 **authoritative Test Contract location** 에서 AC↔§8 coverage self-check (모든 normative AC-N → ≥1 §8 명명 테스트 매핑, 미커버=0) 통과 보고. location 은 **문서유형별 resolve** — wrapper-self dogfood = Change Plan §8 / consumer Story = Story §8 mirror (게이트가 self 의 Story §8 placeholder 를 파싱해 false-FAIL 하는 함정 회피, "Story §8" 하드코딩/단정 금지). self-check disjoint 축 group (`architecture_doc_updated` / `mechanical_self_check_passed` / `boundary_completeness_self_check_passed` / `dimensional_empirical_self_check_passed` / `marketplace_sync_declared`) 과 peer. **packet 에 RTM 중복 금지** — verbose RTM 이중 소유 회피, marker bool 만 전달. |

### Migration (v2.4 → v2.5)

- **Backward-compat MINOR** (ADR-008 §결정 2 — optional field default false)
- 기존 v2.4 producer → field omit 시 default `false` 적용
- 신규 v2.5 producer (post-CFP-2603 ArchitectPL) → coverage self-check 수행 후 marker emit
- Validator → field 부재 = `false` 가정 (backward-compat)
- Effective date: 2026-07-11 KST 이후 신규 design lane verdict packet (forward-only, ADR-079 §결정 6 동형)

### Cross-references

- [ADR-145 요건 traceability zero-drop 게이트](../../archive/adr/ADR-145-ac-traceability-zero-drop-gate.md) §결정 6 (계약 2 additive MINOR — design-output v2.5 marker)
- [ADR-006 §8 Test Contract](../../archive/adr/ADR-006-testcontract-architect.md) — AC↔§8 coverage self-check 의 authoritative location (§8 Test Contract authoring mechanism owner)
- [ADR-008 inter-plugin contract versioning](../../archive/adr/ADR-008-inter-plugin-contract-versioning.md) §결정 2 (MINOR additive)

