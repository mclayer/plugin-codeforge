---
kind: contract
contract_version: "1.0"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-pmo (Cross-cutting plugin, producer — GitOpsAgent)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
  - ADR-035 (Worktree convention — CFP-139)
  - ADR-036 (Phase-scoped agent teams — CFP-139)
related_files:
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - templates/story-page-structure.md (Story §10.5 row schema)
  - codeforge-pmo:agents/GitOpsAgent.md (canonical producer agent)
authors:
  - Claude (CFP-139 — GitOpsAgent introduction)
parent_epic: CFP-134
carrier_story: CFP-139
---

# git_ops_event v1 — Inter-plugin Contract

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/git-ops-event-v1.md`: **canonical** (codeforge-pmo repo, GitOpsAgent producer plugin)
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — ADR-010 + CFP-24 marketplace sync 정책 동질)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- ADR-010 (본 contract 의 sibling sync 정책): codeforge wrapper repo `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`

`codeforge-pmo` plugin (GitOpsAgent) → `codeforge` core (Orchestrator) + lane PL agents 단방향 schema. GitOpsAgent 가 worktree create / delete / merge / conflict + branch tree 변경을 typed event 로 보고. wrapper Orchestrator + lane PL 가 event 수령 후 다음 액션 (teammate spawn / lane 전환 / chief author re-spawn / PMOAgent escalation) 결정.

## 1. 목적

GitOpsAgent (codeforge-pmo plugin) 가 wrapper Orchestrator / lane PL agent 에게 git operation event 를 typed 으로 보고. Worktree create / delete / merge / conflict + branch tree 변경 추적. Story §10.5 ledger 와 cross-ref (Orchestrator self-write 영역 — fix-event-v1 와 별개 ledger).

## 2. Schema

```yaml
git_ops_event:
  event_id: string                    # UUID v4
  event_type: enum
    - WORKTREE_CREATE                 # TeamCreate 직전 worktree 생성 + branch checkout
    - WORKTREE_PRUNE                  # TeamDelete 후 worktree 제거 + gc
    - BRANCH_MERGE_OK                 # Sub-branch → parent 무충돌 merge
    - BRANCH_MERGE_CONFLICT           # Merge 시 line conflict 감지
    - BRANCH_TREE_DECOMPOSE           # PMOAgent 분해 결과 받아 GitOpsAgent 가 branch tree 생성
    - STALE_GC                        # SessionStart hook (7일+ + origin absent worktree gc)
  story_key: string                   # 예: "CFP-139"
  parent_branch: string               # 예: "cfp-135", "cfp-135/design"
  child_branch: string | null         # 예: "cfp-135/design/mapper" (없을 시 null)
  worktree_path: string | null        # 예: "$HOME/.claude/worktrees/plugin-codeforge/cfp-135-design-mapper"
  timestamp: ISO8601                  # UTC, "2026-05-08T12:34:56Z"
  triggered_by: string                # Orchestrator | <PL agent name> | PMOAgent | scheduler (SessionStart hook)
  outcome: enum
    - SUCCESS
    - CONFLICT                        # merge 시 line conflict
    - ERROR                           # 그 외 git operation 실패
  conflict_detail: string | null      # CONFLICT 시 file path + line range (예: "src/foo.ts:42-58")
  related_team_name: string | null    # TEAM-<LANE> if applicable (예: "TEAM-DESIGN")
  ledger_entry: string | null         # Story §10.5 row reference (예: "§10.5 Iter 3")
```

### Markdown row 형식 예시 (Story §10.5)

```markdown
| Iter | 시각 | event_type | parent → child | outcome | triggered_by | ledger_entry |
|------|------|------------|----------------|---------|--------------|--------------|
| 1 | 2026-05-08T10:15:00Z | WORKTREE_CREATE | cfp-139 → cfp-139-gitops-agent | SUCCESS | Orchestrator | — |
| 2 | 2026-05-08T11:42:00Z | BRANCH_MERGE_OK | cfp-139/design → cfp-139 | SUCCESS | DesignReviewPL | — |
| 3 | 2026-05-08T14:20:00Z | BRANCH_MERGE_CONFLICT | cfp-139/impl/api → cfp-139/impl | CONFLICT | DeveloperPL | "src/api.ts:120-145" |
```

## 3. 항목 (이벤트별 사용 매트릭스)

| event_type | 발생 시점 | producer | consumer | 다음 액션 |
|---|---|---|---|---|
| `WORKTREE_CREATE` | TeamCreate 직전 (lane 진입 시 worktree 부재 → 생성) | GitOpsAgent | Orchestrator | teammate spawn (cwd 주입) |
| `WORKTREE_PRUNE` | TeamDelete 후 (lane 종료 시 worktree gc) | GitOpsAgent | Orchestrator | (none — gc only, 후속 action 없음) |
| `BRANCH_MERGE_OK` | Sub-branch → parent merge 성공 | GitOpsAgent | lane PL | 다음 lane 진입 |
| `BRANCH_MERGE_CONFLICT` | Merge conflict 감지 | GitOpsAgent | lane PL + PMOAgent | chief author teammate re-spawn 또는 PMOAgent escalation |
| `BRANCH_TREE_DECOMPOSE` | Epic / Story 분해 후 (PMOAgent decompose 결과 수령) | GitOpsAgent | PMOAgent (sibling) | branch hierarchy spec 확정 |
| `STALE_GC` | SessionStart hook (7일+ + origin absent) | GitOpsAgent | Orchestrator | (cleanup log only) |

### 필드 사용 가이드

- `parent_branch` 는 항상 필수. WORKTREE_CREATE / BRANCH_TREE_DECOMPOSE 는 root branch (예: `cfp-139`) 일 수 있음.
- `child_branch` 는 sub-branch 작업 시 (예: `cfp-139/design`, `cfp-139/design/mapper`). STALE_GC / WORKTREE_PRUNE 시 null 가능.
- `conflict_detail` 은 outcome=CONFLICT 일 때만 populate. 그 외 null.
- `related_team_name` 은 lane PL 가 trigger 인 경우 채움 (TEAM-DESIGN / TEAM-DEVELOP 등). Orchestrator / scheduler trigger 시 null.
- `ledger_entry` 는 Story §10.5 row 가 작성된 후 cross-ref. event 발생 후 비동기 채워짐 (initial emit 시 null OK).

## 4. 변경 규칙

ADR-008 SemVer 적용:

- **Add new event_type**: MINOR bump (v1.0 → v1.1) — backward compatible (consumer 가 unknown enum value 무시 정책 유지 시)
- **Modify required field type or remove field**: BREAKING (v1 → v2) — sibling sync 동시 의무 (ADR-010)
- **Add optional field**: PATCH (v1.0 → v1.0.1) — sibling 자동 sync 가능
- **Outcome enum 값 추가**: MINOR — consumer 가 default fallback 처리 의무 명시 시
- **Markdown row 형식 변경 (Story §10.5)**: BREAKING — Story §10.5 lint workflow regex 의존성 (CFP-139 후속 workflow CFP 도입 시)

### Sibling sync (ADR-010)

- canonical = `mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/git-ops-event-v1.md` (GitOpsAgent producer plugin)
- wrapper sibling = 본 file (verbatim mirror + "**상위 SSOT 위치**" 섹션)
- canonical 변경 시 wrapper sibling sync PR 후속 의무 — `check-inter-plugin-contracts.sh` lint 강제
- codeforge-pmo plugin 의 GitOpsAgent.md agent file 의 contract reference 도 본 file 의 schema 와 align

### Writer / Consumer boundary

- **Producer (writer)**: GitOpsAgent (codeforge-pmo plugin) 단독. 다른 agent / Orchestrator 가 git_ops_event emit 금지 — GitOpsAgent 경유 의무.
- **Consumer (reader)**:
  - Orchestrator: WORKTREE_CREATE / WORKTREE_PRUNE / STALE_GC 처리
  - lane PL agent: BRANCH_MERGE_OK / BRANCH_MERGE_CONFLICT 처리 (lane 별)
  - PMOAgent: BRANCH_TREE_DECOMPOSE / BRANCH_MERGE_CONFLICT escalation
- **Story §10.5 ledger writer**: Orchestrator 단독 (fix-event-v1 §10 monopoly 와 동일 패턴, CFP-32 ζ arc principle 적용)

### v1.x 의 invariant

- `event_id` UUID v4 형식 유지 — collision 방지 + cross-event correlation 가능
- `timestamp` UTC ISO8601 유지 — Story §10.5 markdown 표 sort 가능성 보존
- enum 값 한국어 prefix 사용 안 함 (영문 SCREAMING_SNAKE_CASE 유지) — i18n 회피
