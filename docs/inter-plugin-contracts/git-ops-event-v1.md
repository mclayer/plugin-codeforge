---
id: git-ops-event-v1
schema_version: "1.0"
plugin: codeforge-pmo
kind: contract
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-pmo (Cross-cutting plugin, producer — GitOpsAgent)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
  - ADR-040 (Worktree convention — CFP-136)
  - ADR-044 (Phase-scoped sequential team — CFP-137)
related_files:
  - docs/inter-plugin-contracts/MANIFEST.yaml (wrapper)
  - templates/story-page-structure.md (Story §10.5 row schema, wrapper)
  - agents/GitOpsAgent.md (canonical producer agent, 본 plugin)
authors:
  - Claude (CFP-139 — GitOpsAgent introduction)
parent_epic: CFP-134
carrier_story: CFP-139
---

# git_ops_event v1 — Inter-plugin Contract

**상위 SSOT 위치**:
- 본 file (`mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/git-ops-event-v1.md`): **canonical SSOT** (codeforge-pmo repo, GitOpsAgent producer plugin)
- `mclayer/plugin-codeforge/docs/inter-plugin-contracts/git-ops-event-v1.md`: wrapper sibling reference (canonical 변경 시 sync 의무 — ADR-010 + sibling sync 정책)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- ADR-010 (본 contract 의 sibling sync 정책): codeforge wrapper repo `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`

`codeforge-pmo` plugin (GitOpsAgent) → `codeforge` core (Orchestrator) + lane PL agents 단방향 schema. GitOpsAgent 가 worktree create / delete / merge / conflict + branch tree 변경을 typed event 로 보고. wrapper Orchestrator + lane PL 가 event 수령 후 다음 액션 (teammate spawn / lane 전환 / chief author re-spawn / PMOAgent escalation) 결정.

## §1 Producer

- **Plugin**: `codeforge-pmo`
- **Agent**: `GitOpsAgent` (`agents/GitOpsAgent.md`)
- **역할**: Cross-cutting git operations orchestrator (long-running teammate)
- **Emit 시점**: worktree lifecycle event (create / delete / merge / conflict) + branch tree 변경 + stale GC

## §2 Consumer

| Consumer | 처리 event types |
|---|---|
| **Orchestrator** (codeforge core) | `WORKTREE_CREATE` / `WORKTREE_PRUNE` / `STALE_GC` |
| **PMOAgent** (sibling) | `BRANCH_TREE_DECOMPOSE` / `BRANCH_MERGE_CONFLICT` (cross-lane escalation) |
| **lane PL agents** (sibling teammate) | `BRANCH_MERGE_OK` / `BRANCH_MERGE_CONFLICT` (single-lane) |

**비-consumer**: lane plugin 내부 deputy / worker 는 직접 수신 금지 — lane PL 경유 의무 (ADR-044 §결정 1 SendMessage scope 제약 정합).

## §3 Envelope

모든 event 공통 필드:

```yaml
git_ops_event:
  event_id: string                    # UUID v4
  event_type: enum                    # §4 참조
  story_key: string                   # 예: "CFP-139"
  parent_branch: string               # 예: "cfp-135", "cfp-135/design"
  child_branch: string | null         # 예: "cfp-135/design/mapper" (없을 시 null)
  worktree_path: string | null        # 예: "$HOME/.claude/worktrees/plugin-codeforge/cfp-135-design-mapper"
  timestamp: ISO8601                  # UTC, "2026-05-08T12:34:56Z"
  triggered_by: string                # Orchestrator | <PL agent name> | PMOAgent | scheduler (SessionStart hook)
  source: GitOpsAgent                 # 항상 고정 (producer 단독 emit)
  outcome: enum
    - SUCCESS
    - CONFLICT                        # merge 시 line conflict
    - ERROR                           # 그 외 git operation 실패
  conflict_detail: string | null      # CONFLICT 시 file path + line range (예: "src/foo.ts:42-58")
  related_team_name: string | null    # TEAM-<LANE> if applicable (예: "TEAM-DESIGN")
  ledger_entry: string | null         # Story §10.5 row reference (예: "§10.5 Iter 3")
```

## §4 Event payload (6 event types)

### 4.1 WORKTREE_CREATE

TeamCreate 직전 worktree 생성 + branch checkout.

```yaml
event_type: WORKTREE_CREATE
payload:
  team_id: string                     # 예: "TEAM-DESIGN"
  branch: string                      # 생성된 branch 이름
  worktree_path: string               # 절대 경로 (ADR-040 §결정 1 SSOT)
  teammate_id: string                 # 해당 worktree 의 teammate ID
```

**다음 액션**: Orchestrator → teammate spawn (cwd = `worktree_path` 주입)

### 4.2 WORKTREE_PRUNE

TeamDelete 후 worktree 제거 + gc.

```yaml
event_type: WORKTREE_PRUNE
payload:
  team_id: string
  branch: string
  worktree_path: string
  prune_ok: bool                      # git worktree prune 성공 여부
```

**다음 액션**: Orchestrator — gc only, 후속 action 없음

### 4.3 BRANCH_MERGE_OK

Sub-branch → parent 무충돌 merge 성공.

```yaml
event_type: BRANCH_MERGE_OK
payload:
  source_branch: string               # 예: "cfp-139/design/mapper"
  target_branch: string               # 예: "cfp-139/design"
  ff_only: bool                       # fast-forward only 여부
  merge_commit: string | null         # merge commit SHA (ff-only 시 null)
```

**다음 액션**: lane PL → 다음 lane 진입

### 4.4 BRANCH_MERGE_CONFLICT

Merge 시 line conflict 감지.

```yaml
event_type: BRANCH_MERGE_CONFLICT
payload:
  source_branch: string
  target_branch: string
  conflict_files: [string]            # 충돌 파일 경로 목록
  peer_recipient: enum
    - lane_pl                         # single-lane conflict → 해당 lane PL SendMessage
    - pmo                             # cross-lane conflict → PMOAgent escalation
  escalation_reason: string           # 충돌 원인 요약
```

**다음 액션**:
- `peer_recipient: lane_pl` → 해당 lane PL teammate SendMessage → deputy 재작업 dialog → 해소 후 retry
- `peer_recipient: pmo` → PMOAgent escalation → Orchestrator 협의 → 사용자 판단 트리거 가능

**분기 기준** (§5.5 Q3 답변):
- **single-lane conflict**: 동일 lane 내 sub-worktree 충돌 → `peer_recipient: lane_pl`
- **cross-lane conflict**: 여러 lane 이 공유하는 경계 (예: shared schema / interface) 충돌 → `peer_recipient: pmo`

### 4.5 STALE_GC

SessionStart hook 트리거 (7일+ + origin absent worktree GC).

```yaml
event_type: STALE_GC
payload:
  pruned_worktrees: [string]          # 제거된 worktree path 목록
  reason: enum
    - age_7days                       # 7일 초과
    - origin_absent                   # remote branch 삭제됨
    - story_closed                    # Story Issue closed (gh API check)
  bypass_env: bool                    # BYPASS_WORKTREE_GC=1 감지 시 no-op + true
```

**다음 액션**: Orchestrator — cleanup log only

### 4.6 BRANCH_TREE_DECOMPOSE

PMOAgent 분해 결과 받아 GitOpsAgent 가 branch tree 생성 완료.

```yaml
event_type: BRANCH_TREE_DECOMPOSE
payload:
  epic_key: string                    # 예: "CFP-134"
  stories: [string]                   # 예: ["CFP-136", "CFP-137", "CFP-139"]
  branch_tree:
    root: string                      # 예: "cfp-134"
    children:
      - branch: string                # 예: "cfp-136"
        sub_branches: [string]        # 예: ["cfp-136/design", "cfp-136/impl"]
  worktree_plan:
    - branch: string
      path: string                    # 절대 경로 (ADR-040 §결정 1 SSOT)
      teammate_id: string | null
```

**다음 액션**: PMOAgent (sibling) → branch hierarchy spec 확정 → Orchestrator 보고

## §5 Versioning (ADR-008)

ADR-008 SemVer 적용:

| 변경 유형 | Bump | 비고 |
|---|---|---|
| 새 event_type 추가 | MINOR (v1.0 → v1.1) | consumer 가 unknown enum 무시 정책 유지 시 backward compatible |
| 필수 field 타입 변경 / 제거 | MAJOR (v1 → v2) | sibling sync 동시 의무 (ADR-010) |
| optional field 추가 | PATCH (v1.0 → v1.0.1) | sibling 자동 sync 가능 |
| outcome enum 추가 | MINOR | consumer 가 default fallback 처리 의무 명시 시 |
| Markdown row 형식 변경 (Story §10.5) | MAJOR | Story §10.5 lint workflow regex 의존성 |

### Sibling sync (ADR-010)

- **canonical** = 본 file (`mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/git-ops-event-v1.md`)
- **wrapper sibling** = `mclayer/plugin-codeforge/docs/inter-plugin-contracts/git-ops-event-v1.md`
- canonical 변경 시 wrapper sibling sync PR 후속 의무 — `check-inter-plugin-contracts.sh` lint 강제
- 본 plugin 의 `agents/GitOpsAgent.md` agent file 의 contract reference 도 본 file schema 와 align 의무

### Writer / Consumer boundary

- **Producer (writer)**: GitOpsAgent 단독. 다른 agent / Orchestrator 가 git_ops_event emit 금지 — GitOpsAgent 경유 의무.
- **Story §10.5 ledger writer**: Orchestrator 단독 (fix-event-v1 §10 monopoly 와 동일 패턴, CFP-32 ζ arc principle 적용)

### v1.x 불변 invariant

- `event_id` UUID v4 형식 유지 — collision 방지 + cross-event correlation 가능
- `timestamp` UTC ISO8601 유지 — Story §10.5 markdown 표 sort 가능성 보존
- `source: GitOpsAgent` 고정 (producer 단독 emit invariant)
- enum 값 한국어 prefix 사용 안 함 (영문 SCREAMING_SNAKE_CASE 유지) — i18n 회피

### Markdown row 형식 예시 (Story §10.5)

```markdown
| Iter | 시각 | event_type | parent → child | outcome | triggered_by | ledger_entry |
|------|------|------------|----------------|---------|--------------|--------------|
| 1 | 2026-05-08T10:15:00Z | WORKTREE_CREATE | cfp-139 → cfp-139-gitops-agent | SUCCESS | Orchestrator | — |
| 2 | 2026-05-08T11:42:00Z | BRANCH_MERGE_OK | cfp-139/design → cfp-139 | SUCCESS | DesignReviewPL | — |
| 3 | 2026-05-08T14:20:00Z | BRANCH_MERGE_CONFLICT | cfp-139/impl/api → cfp-139/impl | CONFLICT | DeveloperPL | "src/api.ts:120-145" |
```

## §6 Changelog

- **v1.0** (2026-05-09, CFP-139): 초기 동결. 6 event types (WORKTREE_CREATE / WORKTREE_PRUNE / BRANCH_MERGE_OK / BRANCH_MERGE_CONFLICT / STALE_GC / BRANCH_TREE_DECOMPOSE). §5.5 Q1 답변 기반 — 6 event 유지 (worktree_gc_bypassed 등 3 event 추가 검토 후 기각, audit trail 은 STALE_GC `bypass_env` field 로 충족).
