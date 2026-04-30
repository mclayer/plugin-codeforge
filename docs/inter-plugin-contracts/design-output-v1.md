---
kind: contract
contract_version: "1.0"
status: Archived
archived_at: 2026-04-30
superseded_by: design-output-v2.md
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-design (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008
  - ADR-009
  - ADR-014
authors:
  - CFP-40 ζ arc — Design lane extraction (LAST, 2026-04-29)
  - CFP-46 — Archived in favor of design-output-v2.md (2026-04-30)
---

# design_output v1 — Inter-plugin Contract

`codeforge-design` plugin → `codeforge` core (Orchestrator) 단방향 schema. ArchitectPLAgent 가 5 deputies 병렬 spawn 후 ArchitectAgent (chief author) 가 Change Plan + ADR + Story §3/§7/§11 mirror self-write.

**상위 SSOT**: `mclayer/plugin-codeforge-design/docs/inter-plugin-contracts/design-output-v1.md`

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① design_packet (Story §1-7 + 관련 ADR list + 코드 경로)
        ▼
codeforge-design plugin
  └─ ArchitectPLAgent
        │
        │ ② 5 deputies 병렬 spawn (한 메시지)
        ▼
  ├─ CodebaseMapperAgent      (보수 — as-is 변호자)
  ├─ RefactorAgent            (혁신 — 결합도/구조 옹호자)
  ├─ SecurityArchitectAgent   (위협 — trust boundary/auth/data 변호자)
  ├─ TestContractArchitectAgent (§8 Test Contract author input)
  └─ DataMigrationArchitectAgent (§11 데이터 마이그레이션 author input)
        │
        │ ③ 5 결과 PL 에 return
        ▼
  └─ ArchitectAgent (chief author) spawn
        │
        │ ④ 통합 + Change Plan §1-11 + 신규 ADR draft author
        │
        │ ⑤ Self-write:
        │    - Edit(docs/change-plans/<slug>.md) — 본 plugin owner
        │    - Edit(docs/adr/ADR-NNN-<slug>.md) — 본 plugin owner
        │    - Edit(docs/stories/<KEY>.md §3 ADR list mirror)
        │    - Edit(docs/stories/<KEY>.md §7 보안 설계 mirror)
        │    - Edit(docs/stories/<KEY>.md §11 데이터 마이그레이션 mirror)
        │    - mcp__github__add_issue_comment ([설계] prefix)
        │    - mcp__github__issue_write (phase:설계 → phase:설계-리뷰)
        ▼
        │ ⑥ design_output v1 typed return
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
  contract_version: "1.0"
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
  contract_version: "1.0"
  story_key: <STORY_KEY>

  status: PASS | FIX_CHIEF_AUTHOR_REVISION | ESCALATE_PACKET_INCOMPLETE

  deputies_results:                     # 필수 — 5 deputy 결과 audit
    codebase_mapper:
      coverage_observations: <int>
      preservation_concerns: [<list>]
    refactor:
      proposals: <int>
      proposal_paths: [<list>]
    security_arch:
      trust_boundaries_identified: <int>
      threat_model_completeness: <enum: stride-lite | partial | minimal>
    test_contract_arch:
      coverage_targets: <int>
      contract_invariants: <int>
    data_migration_arch:
      schema_changes: <int>
      rollback_strategies: <int>

  chief_author_artifact:
    change_plan_path: docs/change-plans/<slug>.md
    new_adr_paths:                      # 신규 ADR 경로 array
      - docs/adr/ADR-NNN-<slug>.md
    sections_authored:                  # §1-11 중 본 iteration 에서 작성·갱신된 섹션
      - "§3 도입할 설계"
      - "§7 보안 설계"
      - "§8 Test Contract"
      - "§11 데이터 마이그레이션"

  # PL self-write 결과 audit
  writes_completed:
    change_plan: <bool>                 # docs/change-plans/<slug>.md
    new_adrs: <int>                     # 신규 ADR 파일 수
    story_section_3: <bool>             # ADR list mirror
    story_section_7: <bool>             # 보안 설계 mirror
    story_section_11: <bool>            # 데이터 마이그레이션 mirror
    phase_comment: <bool>               # [설계] prefix
    phase_label_transitioned: <bool>    # phase:설계 → phase:설계-리뷰
```

## 4. ESCALATE 처리

- `FIX_CHIEF_AUTHOR_REVISION`: PL 검수 RETURN — chief author 재스폰 필요. PL 이 clarification context 첨부
- `ESCALATE_PACKET_INCOMPLETE`: Story §1-7 또는 ADR list 부재

## 5. v1 → v2 변경 가능성

- 새 deputy 추가 (overlay/preset 진화) — minor (deputies_results schema 확장)
- 새 mirror section 추가 (§12 등) — minor

## 6. 동결 ATTRIBUTION

- 동결 일시: 2026-04-29 (CFP-40, ζ arc LAST extraction)
- Source: CFP-31 §5.10
