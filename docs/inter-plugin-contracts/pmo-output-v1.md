---
kind: contract
contract_version: "1.1"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-pmo (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, codeforge wrapper CFP-31)
authors:
  - CFP-36 ζ arc — second lane self-write pattern validation (2026-04-29)
  - CFP-139 — GitOpsAgent worktree_manifest MINOR bump (2026-05-08)
---

# pmo_output v1 — Inter-plugin Contract

`codeforge-pmo` plugin → `codeforge` core (Orchestrator) 단방향 schema. PMOAgent 가 self-write 후 typed output 으로 결과 audit 보고.

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/pmo-output-v1.md`: **canonical** (codeforge-pmo repo)
- `mclayer/plugin-codeforge/docs/inter-plugin-contracts/pmo-output-v1.md`: sibling reference (sync 의무)

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① pmo_packet 작성 (trigger-specific)
        ▼
codeforge-pmo plugin
  └─ PMOAgent
        │
        │ ② Self-write 단계:
        │    - Edit(docs/retros/<sprint>.md) [회고 감사 / Cross-Story 패턴 보고서]
        │    - Edit(docs/stories/<KEY>.md §11) [Story 완료 회고 mirror]
        │    - mcp__github__add_issue_comment ([PMO] prefix)
        │    - gh api repos/*/milestones (Epic milestone 갱신)
        │    - ADR 후보 발의 시: codeforge-design 에 hand-off (verdict.adr_proposal)
        ▼
        │ ③ pmo_output v1 typed output (writes_completed audit + ADR proposal)
        ▼
codeforge core (Orchestrator)
        │
        │ ④ output 처리:
        │    - adr_proposal 존재 → codeforge-design 에 발의 hand-off
        │    - patterns_for_cross_story_audit → 향후 PMO trigger 데이터로 보존
```

## 2. pmo_packet (Orchestrator → PMOAgent)

```yaml
pmo_packet:
  contract_version: "1.0"        # 필수
  trigger:                       # 필수 — enum
    - epic_creation              # Epic 창설 시 1회 (scope 분해 자문)
    - story_completion           # Story 완료 시 (회고 감사)
    - cross_story_audit_request  # 사용자 주기적 요청 (Cross-Story 패턴)
  story_key: <STORY_KEY>         # 선택 — story_completion 시 필수
  epic_milestone: <int>          # 선택 — epic_creation / cross_story_audit 시 필수
  scope_for_audit:               # 선택 — cross_story_audit_request 시
    sprint_period: <str>
    story_keys: [<list>]
```

## 3. pmo_output (PMOAgent → Orchestrator)

```yaml
pmo_output:
  contract_version: "1.1"
  trigger: <packet 동일 enum>
  story_key: <STORY_KEY>          # 필수 (해당 시) — packet과 일치
  epic_milestone: <int>           # 필수 (해당 시) — packet과 일치

  status: COMPLETED | PARTIAL | ESCALATED   # 필수

  # PMOAgent self-write 결과 audit
  writes_completed:
    retro_doc: <bool>             # 필수 — docs/retros/<sprint>.md write 완료
    story_section_11: <bool>      # 필수 — Story §11 retro pointer (story_completion only)
    epic_milestone_progress: <bool>  # 필수 — milestone progress 갱신 (epic 관련 trigger)
    pmo_comment: <bool>           # 필수 — [PMO] prefix GitHub comment 게시

  # ADR 후보 발의 (선택 — 패턴 발견 시)
  adr_proposal:                   # 선택 — null 허용
    title: <string>               # ADR 제목 안
    context: <markdown>           # 발의 근거 (관찰된 cross-Story 패턴)
    status: Proposed              # 항상 Proposed (codeforge-design 에서 Accepted/Rejected 결정)
    target_plugin: codeforge-design (CFP-40 후) | wrapper

  # Cross-Story 감사 결과 (선택)
  patterns_observed:              # 선택 — null 또는 array
    - category: <enum>            # fix-loop-pattern / escalate-trend / performance-regression / hotspot
      summary: <markdown>
      affected_stories: [<list>]
      severity: P0 | P1 | P2

  # GitOpsAgent worktree manifest reference (CFP-139, v1.1 신설 — optional)
  # PMOAgent 가 retro 작성 시 GitOpsAgent 산출물 (.claude-work/worktree-manifest.yaml) 의
  # worktree create / delete / merge / conflict event 를 reference. v1.0 consumer 호환 — 필드 부재 = 미사용.
  worktree_manifest:              # 선택 — null 허용 (v1.1 NEW, additive)
    schema: git-ops-event-v1      # 향후 inter-plugin contract 신설 예정 (CFP-139 follow-up)
    manifest_path: <path>         # 보통 .claude-work/worktree-manifest.yaml
    events:                       # array of git ops events
      - event_type: <enum>        # team-create / team-delete / sequential-merge / conflict-detected / fix-iteration-rebuild / stale-cleanup
        timestamp: ISO8601
        lane: <string>            # 7 lane slug (requirements / design / develop / ...) 또는 cross-cutting
        actor: GitOpsAgent
        worktree_count: <int>     # team-create 시 N
        outcome: success | conflict | aborted
        detail: <markdown>        # short narrative
```

## 4. ESCALATE 처리

PMOAgent self-write 단계 실패 (예: GitHub milestone API rate limit, retro file write 실패) 시:
- `status: ESCALATED`
- `writes_completed` 모든 필드 false
- Orchestrator 가 사용자 ESCALATE 후 수동 복구 의뢰

## 5. v1 → v2 변경 가능성

다음 조건에서 v2 BREAKING 가능:
- `adr_proposal` schema 확장 (예: 결정 우선순위 추가)
- 새 trigger enum 추가 (backward-compat 시 minor)
- `patterns_observed` category enum 변경 (drop 시 v2)
- `worktree_manifest` 필드 required 화 (v1.1 = optional, BREAKING 시 v2)

## 6. Changelog

- **v1.1** (2026-05-08, CFP-139): `worktree_manifest` optional 필드 추가 (GitOpsAgent 산출물 reference, additive — v1.0 consumer 호환). MINOR per [ADR-008](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-008-inter-plugin-contract-versioning.md) (additive optional field).
- **v1.0** (2026-04-29, CFP-36): 초기 동결.

## 7. 본 contract 시점 동결 ATTRIBUTION

- 동결 일시: 2026-04-29 (CFP-36) → v1.1 amendment 2026-05-08 (CFP-139)
- 협업: Claude (codification) · CFP-31 parent spec §5.6 · CFP-139 GitOpsAgent agent file
- Source: `mclayer/plugin-codeforge-pmo/agents/PMOAgent.md` + `agents/GitOpsAgent.md` 책임 정의
