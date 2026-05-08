---
adr_number: 40
title: Worktree convention — base directory + naming + lifecycle (CFP-134 Epic Wave 1)
date: 2026-05-08
status: Proposed
category: tooling-infrastructure
carrier_story: CFP-136
parent_epic: CFP-134
supersedes: null
amends: null
related_stories:
  - CFP-134
  - CFP-136
  - CFP-137
  - CFP-139
related_adrs:
  - ADR-009
  - ADR-024
  - ADR-031
  - ADR-035
related_files:
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md
  - templates/scripts/worktree-create.sh
  - templates/scripts/worktree-merge.sh
  - templates/scripts/worktree-prune.sh
  - templates/scripts/check-worktree-stale.sh
  - templates/scripts/worktree-path-util.sh
  - docs/orchestrator-playbook.md
---

# ADR-040: Worktree convention — base directory + naming + lifecycle

## 상태

**Proposed (2026-05-08)** — CFP-136 carrier, CFP-134 Epic Wave 1 (worktree infrastructure). Effective date = Phase 2 wrapper PR merge timestamp (ADR-031 §14 freeze pattern 재사용 — 본 effective date 이전 Phase 1 PR open 된 Story = grandfather, retroactive 강제 없음).

CFP-134 Epic 의 Wave 1 prerequisite — Phase-scoped agent teams (CFP-137) + GitOpsAgent (CFP-139) 가 worktree convention SSOT 에 의존. 본 ADR 가 Accepted 되어야 CFP-137 / CFP-139 spec / plan 작업 진입.

## 컨텍스트

사용자 directive (2026-05-08 conversation, claude-opus-4-7 wrapper session):

> 동일 working directory 에서 multiple session 병렬 실행 시 file 충돌 / overwrite 가 발생한다. 표준 git worktree 해결책을 도입하자.

### 현재 상태

ADR-024 (Story-scoped branch policy) 는 1 Story = 1 feature branch 만 정의 — 동일 repo / 동일 working directory. 단일 session 가정.

**문제**:
1. **File 충돌**: 사용자 main session + Codex CLI sub-session + lane plugin agent (Agent tool spawn) 가 동일 working directory `C:/workspace/mclayer/plugin-codeforge` 공유. file write race condition 발생.
2. **Branch checkout 충돌**: 1 session 이 `cfp-A` checkout 중인데 다른 session 이 `cfp-B` checkout 시도 → `git checkout` reject 또는 dirty working tree 오염.
3. **CFP-137 prerequisite 부재**: phase-scoped agent teams (lane parallel spawn) 도입 시 각 agent 가 자기 isolated workspace 필요 — 현재는 unsupported.
4. **CFP-139 prerequisite 부재**: GitOpsAgent (worktree lifecycle 자동화) 가 base directory · naming · GC 정책 SSOT 에 의존 — SSOT 미존재.

### Native git worktree 해결책

`git worktree add <path> <branch>` 로 동일 repo 의 multiple branch 를 동시 checkout. 각 worktree = 독립 working directory + 공유 `.git/`. file 충돌 0.

기 사용 사례: 본 ADR 작성 자체가 `cfp-136-worktree-infra` worktree 에서 진행 중 (`C:/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-136-worktree-infra/`).

## 결정

### 결정 1 — Worktree base directory

```
${HOME}/.claude/worktrees/<repo-name>/<branch-name-flatten>
```

- `${HOME}` = cross-platform consistent (Windows: `C:\Users\<user>` / macOS: `/Users/<user>` / Linux: `/home/<user>`).
- `<repo-name>` = remote repo basename (예: `plugin-codeforge`, `mctrader-hub`).
- `<branch-name-flatten>` = branch name 의 `/` → `-` 치환 (예: `cfp-136/lane/design` → `cfp-136-lane-design`). filesystem 호환.

**근거**: 사용자 home 하 단일 namespace `.claude/worktrees/` — IDE / shell autocomplete 에 친화적, repo 기준 grouping 으로 다중 consumer project 동시 작업 시 conflict 0.

### 결정 2 — Branch hierarchy naming (ADR-024 amendment 1 정합)

ADR-024 v1 = `cfp-NNN[-<slug>]` flat. 본 ADR 는 hierarchical sub-branch 추가:

```
cfp-NNN                          # Story root branch (Phase 1 PR)
cfp-NNN/lane/<lane-name>         # Lane sub-branch (parallel agent team workspace)
cfp-NNN/lane/<lane>/<sub>        # Sub-task (deputy / parallel finding)
cfp-NNN/fix-iter-<N>             # FIX iteration branch
cfp-NNN/retro                    # Retro branch (rare)
```

- `<lane-name>` ∈ {`requirements`, `design`, `design-review`, `develop`, `code-review`, `test`, `security`}.
- Parent branch = `cfp-NNN` (Story root). Phase 2 PR merge 시 Story root → main, sub-branch 는 prune.
- ADR-024 v1 의 `cfp-NNN[-<slug>]` flat 패턴은 **Amendment 1** 로 superset 으로 흡수 — flat 도 hierarchical 의 special case (depth=0).

**근거**: CFP-137 (phase-scoped agent teams) 가 lane 별 parallel agent spawn 시 lane sub-branch 별도 worktree 필요. flat naming 으로는 hierarchy 표현 불가.

### 결정 3 — Lifecycle hooks

```
on_team_create_pre   → GitOpsAgent (CFP-139) creates worktrees per teammate
on_team_create_post  → each teammate spawned with cwd = worktree_path
on_team_delete_pre   → GitOpsAgent merges worktrees → lane branch (sequential merge, conflict 시 user escalate)
on_team_delete_post  → GitOpsAgent prunes worktrees (git worktree remove)
on_session_start     → GitOpsAgent (또는 scripts/check-worktree-stale.sh) GC stale worktrees
on_story_close       → GitOpsAgent prunes all sub-worktrees (Story root 제외 — Phase 2 PR merge 까지 보존)
```

- **Sequential merge** (parallel 금지): 동일 lane 내 multiple sub-worktree merge 시 race condition 회피. GitOpsAgent 가 lock 보유.
- **Conflict 발생 시**: user escalate (decider whitelist — destructive action 직전 stop).

**근거**: CFP-139 GitOpsAgent 의 mandate 명확화 — 본 ADR 가 lifecycle hook contract SSOT.

### 결정 4 — Cross-platform path handling

- **Bash POSIX path** = primary (Linux / macOS / Windows Git Bash).
- **Windows native path** = utility 변환 (`templates/scripts/path-utils.sh` 의 `to_windows_path()` / `to_posix_path()` 헬퍼).
- worktree 생성 / 제거 / merge 스크립트는 모두 POSIX path 입력 → 내부에서 OS 감지 후 변환.
- Claude Code Agent tool `cwd` 파라미터 = OS-native path 형태로 전달 (Windows = backslash, *nix = forward slash).

**근거**: 본 plugin 은 cross-platform consumer (mctrader = Windows dev, hypothetical Linux CI). path 처리 inconsistency 가 lifecycle hook 실패 1차 원인 — utility 일원화로 차단.

### 결정 5 — Stale GC policy

**Stale 조건** (AND):
1. Worktree last access (mtime of `.git/worktrees/<name>/HEAD`) ≥ **7 days** 전.
2. Story branch closed — PR merged OR Issue closed (gh API 확인).

**GC trigger**:
- `on_session_start` hook (Claude Code SessionStart hook → `scripts/check-worktree-stale.sh` 실행).
- ad-hoc 사용자 호출 (`bash templates/scripts/check-worktree-stale.sh --prune`).

**예외**: `cfp-NNN` Story root branch 가 open 상태 (Phase 2 PR 미merge) 면 sub-worktree 도 보존 — 사용자가 재작업 가능.

**근거**: 7 days = ADR-031 lane evidence freeze 와 동일 grace period. orphan worktree 누적 방지 + 활성 작업 보호.

### 결정 6 — Scripts location + consumer distribution

**Wrapper repo**:
- `templates/scripts/worktree-create.sh`
- `templates/scripts/worktree-merge.sh`
- `templates/scripts/worktree-prune.sh`
- `templates/scripts/check-worktree-stale.sh`
- `templates/scripts/path-utils.sh` (helper, 결정 4)

**Consumer distribution**: `templates/consumer-scripts.manifest` (ADR-031 / CFP-97) 에 본 5 script 추가 → consumer install 시 `.claude/scripts/` 로 복사. consumer 측 Orchestrator + GitOpsAgent (CFP-139) 가 동일 SSOT 사용.

**근거**: Plugin self-application + consumer adoption (ADR-027) 정합 — 본 plugin 작업 시 dogfood, mctrader 등 consumer 에 distributable.

## 결과

### 긍정

- **File 충돌 0**: worktree isolation 으로 multi-session 병렬 작업 안전.
- **CFP-137 prerequisite 충족**: phase-scoped agent teams 가 lane 별 worktree 보유 가능.
- **CFP-139 prerequisite 충족**: GitOpsAgent lifecycle hook contract SSOT 확보.
- **ADR-024 amendment 1**: hierarchical branch convention 도입 → Story 내 lane / sub-task 분기 표현력 향상.
- **Cross-platform 지원**: Windows / macOS / Linux 일관 경로 처리.

### 부정 / 비용

- **Disk space**: worktree 당 working tree copy → repo size × N (N = active worktree 수). plugin-codeforge 기준 1 worktree ≈ 50MB → 10 worktree ≈ 500MB. acceptable (현대 SSD 기준).
- **Branch hierarchy 학습 곡선**: 사용자 / agent 가 `cfp-NNN/lane/design` 식 nested naming 적응 필요. mitigation = docs/orchestrator-playbook.md §X (CFP-136 후속) 에 예시 도식.
- **Sequential merge bottleneck**: 1 lane 내 multiple sub-worktree merge 시 sequential → parallel 보다 느림. mitigation = lane 내 sub-worktree 수 ≤ 4 권장.

### 위험

- **Worktree corruption**: `.git/worktrees/<name>/` 메타데이터 손상 시 worktree unusable. mitigation = `git worktree repair` 호출 또는 force prune + 재생성.
- **Branch protection conflict**: hierarchical sub-branch (`cfp-NNN/lane/design`) 가 main branch protection rule 미적용 — sub-branch 는 protection 면제 (default). 명시 정책: sub-branch 직접 push OK, 단 lane sub-branch → Story root branch merge 만 허용 (no main 직접 merge).

## 대안 고려

| 대안 | 채택 안 한 이유 |
|---|---|
| **Multiple repo clone** (`plugin-codeforge-1`, `plugin-codeforge-2`) | disk × N, `.git/` duplicate, fetch / pull sync 부담. worktree 가 native 해결책. |
| **Docker container per session** | overkill — file isolation 만 필요, full OS isolation 불필요. ADR-033 docker-first 와 무관 (개발 환경 isolation ≠ deploy artifact). |
| **VSCode multi-root workspace** | IDE-specific, Claude Code Agent tool 무관. file isolation 미보장. |
| **flat branch (ADR-024 v1 유지)** | CFP-137 lane parallel spawn 표현력 부족 — sub-task 별 worktree 필요. |

## 관련 파일

- [ADR-024 (story-scoped branch policy)](ADR-024-story-scoped-branch-policy.md) — 본 ADR 가 Amendment 1 로 hierarchical naming 추가.
- [ADR-009 (wrapper-only decomposition)](ADR-009-wrapper-only-decomposition.md) — wrapper agent 0 개 invariant 정합 (worktree 는 인프라, agent 추가 아님).
- [ADR-031 (lane spawn evidence)](ADR-031-lane-spawn-evidence-trail.md) — 7 days grace period 패턴 차용.
- [ADR-035 (codeforge agent teams Epic architecture)](ADR-035-codeforge-agent-teams-epic-architecture.md) — Epic-level carrier ADR (D2 implementation level 의 worktree 상세를 본 ADR 가 별도 carrier 로 분리).
- **CFP-134** — Epic carrier (worktree infrastructure + agent teams + GitOpsAgent).
- **CFP-136** — 본 ADR carrier Story (worktree infra Wave 1).
- **CFP-137** — phase-scoped agent teams (worktree convention 의존).
- **CFP-139** — GitOpsAgent (lifecycle 자동화, 본 ADR §결정 3 hook contract 구현).
