---
name: worktree-lifecycle
description: Worktree-first 개발 규약 lookup 시 (① 코딩/수정 작업 개시 직전 worktree 생성, ② Story/PR 완결 직후 eager 정리). 개시 → 작업 중 git -C 주입 → 완결 시 정리(1급 단계) → backstop GC → bypass env 2종의 전 lifecycle 을 정의한다. lookup mirror — 정책 SSOT = ADR-040(+Amd 1~8), 절차 SSOT = orchestrator-playbook §3.5 + §0a-prime.
tools: Read
---

# Worktree Lifecycle (CFP-2191 / ADR-040 Amendment 8)

> 참조 테이블 skill — 코딩/수정 작업 **개시 직전** 과 Story/PR **완결 직후** 두 시점에 본 skill 을 확인하세요.

본 skill 은 **lookup mirror** — 내용의 원본은 아래 2곳이며 본 skill 로의 SSOT 이동/변경 금지:

- **정책 SSOT**: [ADR-040 worktree convention (+Amendment 1~8)](../../archive/adr/ADR-040-worktree-convention.md)
- **절차 SSOT**: [orchestrator-playbook](../../docs/orchestrator-playbook.md) §3.5 (Worktree dispatch) + Step 0a-prime (eager 정리 + backstop GC)

**호출 시점 2개**:

| 시점 | 할 일 |
|---|---|
| ① 코딩/수정 작업 개시 직전 | worktree 생성 (§1) — main working tree 직접 편집 금지 |
| ② Story/PR 완결 직후 | eager 정리 (§3) — merge 확인 후 즉시 worktree 제거 |

## 1. 개시 — worktree 생성

```bash
bash templates/scripts/worktree-create.sh <branch-name> [<base-branch>]   # base 생략 시 origin/main
# stdout = worktree 절대경로 (single line, scriptable)
```

- **base dir** = `${HOME}/.claude/worktrees/<repo-name>/<branch-flat>` (ADR-040 §결정 1). branch 의 `/` 는 `-` 로 flatten (예: `cfp-136/lane/design` → `cfp-136-lane-design`).
- **branch naming** (ADR-040 §결정 2): Story root = `cfp-NNN[-slug]` flat + hierarchical sub = `cfp-NNN/lane/<lane>[/<sub>]` / `cfp-NNN/fix-iter-<N>`.
- `git checkout` 으로 main working tree 를 직접 편집하는 것 = 금지 (CLAUDE.md 작업 규칙 anchor).

## 2. 작업 중 — worktree-pinned operation

- **subagent spawn 시**: prompt 에 `Working dir: <worktree-path>` 주입 (playbook §3.5 step 2).
- **모든 file operation** = worktree 절대경로 기준 — git command 는 `git -C <worktree_abs_path> <subcommand>`, Write/Edit 는 worktree 하위 absolute path (forward-slash 정규형). 상대경로 호출은 harness cwd reset 후 main repo 로 resolve 되는 사고 경로 (ADR-040 Amendment 6 §결정 7.J.1).
- **Read/Grep 도 worktree 경로 고정** — main repo path 는 stale snapshot 위험 (ADR-040 Amendment 7 §결정 7.J.4).
- **cross-repo 작업** = repo 별 worktree 분리. wrapper worktree 안에서 internal-docs write 금지 — 별도 worktree explicit create + switch (playbook §3.5.2 / ADR-082 Amendment 21 sub-scope 1-J).

## 3. 완결 시 정리 — eager primary (1급 단계)

Story/PR 완결의 일부다. 부속 작업이 아니다 — **merge 확인 즉시 해당 worktree 를 제거**한다.

**branch-protected repo cleanup invariant** (ADR-040 Amendment 2 — 순서 강제):

```
push → PR 생성 → gh pr view <N> --json mergedAt 확인 (non-null) → git worktree remove <path> → git worktree prune
```

- **pre-merge `git worktree remove` = policy violation.** `mergedAt` non-null 확인 전 제거 금지.
- **순서 불변 — 비가역 정리는 merge 확인 후에만.** branch/worktree 삭제(비가역)는 `mergedAt` 비-null 확인 **후에만** 실행한다. branch delete 를 merge 호출과 **같은 무조건 스크립트에 묶지 말 것** — `A; B` / `A && B` 파이프는 선행(merge) 실패 시에도 exit code 를 가려 삭제(B)가 실행될 수 있다. 반드시 조건 가드(`merge 성공 확인 → then 삭제`)로 분리한다. 기계적 보강 = `git-branch-delete-merge-gate` PreToolUse hook — 열린(미머지) PR branch 의 remote 삭제(`git push <remote> --delete|-d|:<b>`)를 하드차단(bypass: `BYPASS_BRANCH_DELETE_MERGE_GATE=1`). **사고 박제: INCIDENT 2026-06-15 #2280** — 미머지 PR branch 선삭제로 PR auto-close + phase-gate-mergeable status 가 head SHA 에 stuck("expected") → reopen·fresh PR·admin merge 까지 BLOCKED.
- **squash merge 환경의 merged 판정** = PR 상태 기반: `gh pr list --state merged --head <branch>`. squash merge 는 branch commit 을 origin/main ancestry 에 올리지 않으므로 `origin/main..HEAD` 비교는 항상 거짓 양성 (`templates/scripts/check-worktree-stale.sh` 헤더 명세).
- **수행 주체** = Story/Epic 완료 회고 시점의 GitOpsAgent (playbook Step 0a-prime primary 경로 — mergedAt 확인 후 경로 기반 제거). GitOpsAgent 미spawn 컨텍스트(ad-hoc 작업)에서는 작업 수행 주체가 동일 invariant 로 직접 정리.
- sub-worktree (`cfp-NNN/lane/<lane>[/<sub>]`) = `bash templates/scripts/worktree-prune.sh <branch>` (playbook §3.5 step 5). Story root worktree 는 Phase 2 PR merge 확인까지 보존.

## 4. backstop GC — orphan 안전망

eager 정리(§3)를 못 거친 크래시·중단 orphan 전용. eager 와 disjoint 2-경로 (playbook Step 0a-prime).

```bash
GC_DRY_RUN=1 bash templates/scripts/check-worktree-stale.sh   # preview (prune 대상만 보고)
bash templates/scripts/check-worktree-stale.sh                # 실제 prune — 수동/스케줄 호출
```

prune 조건 = 4 조건 **ALL** (스크립트 헤더 SSOT):

1. age > 7일 (`STALE_DAYS` 기본 7)
2. branch MERGED (squash-aware: `gh pr list --state merged --head <branch>` + merged PR `headRefOid` 이후 추가 local commit 0). gh 부재/실패 시 fail-safe 보존
3. worktree CLEAN (tracked 변경 0 + 알려진 임시파일 외 untracked 0 — 잔여 변경 있으면 절대 prune 금지)
4. 현재/main worktree 아님 + `locked` 아님

> 과거 SessionStart hook 동기 호출은 제거됨 (worktree 90+ 동기 스캔으로 세션 시작 지연) — 수동/스케줄 호출만.

## 5. bypass env 2종 — disjoint scope

하나가 다른 하나의 superset 아님 (ADR-040 §결정 5 + Amendment 3 §결정 7.E). env 이름 = reserved contract (ADR-040 SSOT 외 변경 금지).

| env | scope | trigger |
|---|---|---|
| `BYPASS_WORKTREE_GC=1` | `check-worktree-stale.sh` 단독 — stale check 전체 skip (origin 접촉 0 + prune 0, non-blocking exit 0) | stale check 호출 시 |
| `BYPASS_WORKTREE_FIRST=1` | worktree-first lint 4종 (`session-start-wire` / `pre-checkout` / `pre-commit-main-block` / `spawn-evidence-cwd`) 전체 short-circuit | PR `pull_request` event 시 |
