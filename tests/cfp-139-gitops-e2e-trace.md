# CFP-139 Phase 2 e2e Fixture — TEAM-DECOMPOSE Happy Path Trace

## 시나리오

PMOAgent → GitOpsAgent SendMessage → branch_tree return 1 trace (trace log only, AC #10)

## Trace

### Event 1 (BRANCH_TREE_DECOMPOSE)

```yaml
git_ops_event:
  event_id: "e1f2a3b4-c5d6-7890-abcd-ef1234567890"
  event_type: BRANCH_TREE_DECOMPOSE
  story_key: CFP-NNN
  parent_branch: "cfp-NNN"
  child_branch: null
  worktree_path: null
  timestamp: "2026-05-09T10:00:00Z"
  triggered_by: "PMOAgent (TEAM-DECOMPOSE)"
  outcome: SUCCESS
  conflict_detail: null
  related_team_name: "TEAM-DECOMPOSE"
  ledger_entry: null
```

PMOAgent → GitOpsAgent: {epic: CFP-NNN, stories: [CFP-NNN-1, CFP-NNN-2], sub_tasks: [...]}
GitOpsAgent: branch tree 생성 계획 수립
GitOpsAgent → PMOAgent: {branch_tree: {"cfp-NNN": ["cfp-NNN/design", "cfp-NNN/impl"]}}

### Event 2 (WORKTREE_CREATE — design lane)

```yaml
git_ops_event:
  event_id: "a2b3c4d5-e6f7-8901-bcde-f23456789012"
  event_type: WORKTREE_CREATE
  story_key: CFP-NNN
  parent_branch: "cfp-NNN"
  child_branch: "cfp-NNN/design"
  worktree_path: "~/.claude/worktrees/plugin-codeforge/cfp-NNN-design"
  timestamp: "2026-05-09T10:05:00Z"
  triggered_by: "Orchestrator (TeamCreate TEAM-DESIGN)"
  outcome: SUCCESS
  conflict_detail: null
  related_team_name: "TEAM-DESIGN"
  ledger_entry: "§10.5 row 1"
```

### Event 3 (BRANCH_MERGE_OK — design lane 완료)

```yaml
git_ops_event:
  event_id: "b3c4d5e6-f7a8-9012-cdef-3456789abcde"
  event_type: BRANCH_MERGE_OK
  story_key: CFP-NNN
  parent_branch: "cfp-NNN"
  child_branch: "cfp-NNN/design"
  worktree_path: "~/.claude/worktrees/plugin-codeforge/cfp-NNN-design"
  timestamp: "2026-05-09T11:30:00Z"
  triggered_by: "DesignReviewPL (TeamDelete TEAM-DESIGN)"
  outcome: SUCCESS
  conflict_detail: null
  related_team_name: "TEAM-DESIGN"
  ledger_entry: "§10.5 row 2"
```

### Event 4 (WORKTREE_PRUNE — design lane 정리)

```yaml
git_ops_event:
  event_id: "c4d5e6f7-a8b9-0123-defa-456789abcdef"
  event_type: WORKTREE_PRUNE
  story_key: CFP-NNN
  parent_branch: "cfp-NNN"
  child_branch: "cfp-NNN/design"
  worktree_path: "~/.claude/worktrees/plugin-codeforge/cfp-NNN-design"
  timestamp: "2026-05-09T11:35:00Z"
  triggered_by: "GitOpsAgent (TeamDelete post-hook)"
  outcome: SUCCESS
  conflict_detail: null
  related_team_name: null
  ledger_entry: null
```

## 검증 기준

- [ ] 4 event type 모두 발화: BRANCH_TREE_DECOMPOSE / WORKTREE_CREATE / BRANCH_MERGE_OK / WORKTREE_PRUNE
- [ ] git-ops-event-v1 schema 준수 (모든 필드 존재)
- [ ] §10.5 ledger_entry 교차 참조 정합 (Story §10.5 row 1,2 와 매핑)
- [ ] STALE_GC / BRANCH_MERGE_CONFLICT event type 미발화 (happy path)
