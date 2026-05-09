---
kind: contract
contract_version: "1.1"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-develop (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
  - ADR-044 (Phase-scoped Sequential Team — Cross-layer pattern measurable verification)
authors:
  - CFP-42 sibling backfill (2026-04-29) — wrapper sibling 첫 작성, canonical 본문 verbatim mirror
  - CFP-297 (2026-05-09) — v1.1 MINOR bump: cross_layer_dialog_rounds field 추가 (ADR-044 §결정 5)
---

# develop_output v1 — Inter-plugin Contract

`codeforge-develop` plugin → `codeforge` core (Orchestrator) 단방향 schema. DeveloperPLAgent 가 role:dev roster 동적 discover + 병렬 spawn 후 Story §8 / §8.5 self-write + Phase 2 PR open + verdict 반환.

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-develop/docs/inter-plugin-contracts/develop-output-v1.md`: **canonical** (codeforge-develop repo)
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — ADR-010 + CFP-24 marketplace sync 정책 동질)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- ADR-010 (본 contract 의 sibling sync 정책): codeforge wrapper repo `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① develop_packet (Story §3 design + §8 Test Contract + Change Plan §3 paths)
        ▼
codeforge-develop plugin
  └─ DeveloperPLAgent
        │
        │ ② role:dev roster discover (frontmatter `role: dev` 검색)
        │ ③ 의존성 없는 한 모두 병렬 spawn (한 메시지)
        ▼
  ├─ DeveloperAgent          (core role:dev)
  ├─ DataEngineerAgent       (core role:dev)
  ├─ InfraEngineerAgent      (core role:dev)
  ├─ QADeveloperAgent        (병렬 — Test Contract 이행, ArchitectPL 산하 §8 owner)
  └─ <preset/overlay role:dev 추가분>
        │
        │ ④ DeveloperPL Self-write:
        │    - Edit(docs/stories/<KEY>.md §8 implementation summary)
        │    - Edit(docs/stories/<KEY>.md §8.5 Impl Manifest 매핑표)
        │    - mcp__github__create_pull_request (Phase 2 PR)
        │    - mcp__github__add_issue_comment ([구현] prefix)
        │    - mcp__github__issue_write (phase:구현 → phase:구현-리뷰)
        ▼
        │ ⑤ develop_output v1 typed return
        ▼
codeforge core (Orchestrator)
        │
        │ ⑥ 처리:
        │    - PASS → ArchitectPLAgent stateless 재스폰 (§8.5 매핑 감사) → 구현 리뷰 lane 진입
        │    - PARTIAL → Orchestrator 인지 (특정 role:dev 실패) + 사용자 ESCALATE
```

## 2. develop_packet (Orchestrator → DeveloperPLAgent)

```yaml
develop_packet:
  contract_version: "1.1"
  story_key: <STORY_KEY>
  change_plan_paths:                # 필수 — Change Plan §3 코드 변경 경로
    - <path glob>
  test_contract:                    # 필수 — Story §8 Test Contract slice
    section: <markdown>
  consumer_overlay:                 # 필수
    role_dev_roster: [<list>]        # frontmatter role:dev 매칭된 agent 이름
    presets: [<list>]                # 활성 preset
```

## 3. develop_output (DeveloperPL → Orchestrator)

```yaml
develop_output:
  contract_version: "1.1"
  story_key: <STORY_KEY>

  status: PASS | PARTIAL | ESCALATE_PACKET_INCOMPLETE

  spawned_dev_agents:               # 필수 — 어떤 role:dev 가 실제 활성됐는지 audit
    - name: <string>
      file: <path>                  # frontmatter source
      executed: <bool>
      files_modified: [<path>]
      tests_modified: [<path>]

  qa_developer_result:
    executed: <bool>
    test_files_created: [<path>]

  # Cross-layer pattern (TEAM-DEVELOP) measurable verification — ADR-044 §결정 5
  cross_layer_dialog_rounds: <int>  # DeveloperAgent ↔ QADeveloperAgent 간 dialog round 수 (>= 0)
                                    # Cross-layer pattern 미사용 시 0

  # PL self-write 결과 audit
  writes_completed:
    story_section_8: <bool>          # 구현 요약 + 변경 파일 목록
    story_section_8_5: <bool>        # Impl Manifest 매핑표 (subissue-from-impl-manifest.yml input)
    phase_2_pr_opened: <bool>
    phase_comment: <bool>            # [구현] prefix
    phase_label_transitioned: <bool> # phase:구현 → phase:구현-리뷰

  pr_metadata:                      # PR 정보 (PASS only)
    pr_number: <int>
    pr_url: <string>
```

### 3.1 cross_layer_dialog_rounds 필드 상세

| 항목 | 내용 |
|---|---|
| 필드명 | `cross_layer_dialog_rounds` |
| 타입 | `int >= 0` |
| 필수 여부 | 필수 (v1.1 이후) |
| 기본값 | `0` |
| 설명 | TEAM-DEVELOP Cross-layer pattern 에서 DeveloperAgent 와 QADeveloperAgent 간 실제 dialog round 수. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경에서 SendMessage 를 통한 직접 대화 횟수. Cross-layer pattern 을 사용하지 않았거나 `AGENT_TEAMS=0` 환경에서는 `0` 기록. |
| 용도 | ADR-044 §결정 5 measurable verification — dev ↔ QA 협업 depth 검증. Orchestrator 가 Story §14 Lane Evidence row 에 포함하여 audit trail 유지. |
| 연관 ADR | ADR-044 (Phase-scoped Sequential Team + Cross-layer pattern) |

## 4. ESCALATE 처리

- `PARTIAL`: role:dev 일부 spawn 실패 → Orchestrator 가 사용자 인지
- `ESCALATE_PACKET_INCOMPLETE`: Change Plan paths 부재, role:dev roster 비어있음 등

## 5. v1 → v2 변경 가능성

- 새 role:dev 카테고리 추가 (overlay/preset 진화) — minor
- Phase 2 PR open 메커니즘 변경 — major

## 6. 동결 ATTRIBUTION

- 동결 일시: 2026-04-29 (CFP-39)
- Source: CFP-31 §5.9

## 7. Changelog

| Version | Date | CFP | 변경 내용 |
|---|---|---|---|
| 1.0 | 2026-04-29 | CFP-42 | 최초 작성 (wrapper sibling backfill) |
| 1.1 | 2026-05-09 | CFP-297 | MINOR bump: `cross_layer_dialog_rounds: int >= 0` 추가 — TEAM-DEVELOP Cross-layer pattern (DeveloperAgent ↔ QADeveloperAgent) measurable verification (ADR-044 §결정 5). `develop_packet` + `develop_output` 양쪽 `contract_version` "1.1" 갱신. |
