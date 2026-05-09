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
amendments:
  - id: 1
    carrier_story: CFP-139
    date: 2026-05-09
    title: GitOpsAgent hook 실행 주체 명시
  - id: 2
    carrier_story: CFP-348
    date: 2026-05-09
    title: Branch-protection-aware worktree cleanup lifecycle
related_stories:
  - CFP-134
  - CFP-136
  - CFP-137
  - CFP-139
  - CFP-348
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
on_session_start     → GitOpsAgent (또는 templates/scripts/check-worktree-stale.sh, hook 호출) GC stale worktrees
on_story_close       → GitOpsAgent prunes all sub-worktrees (Story root 제외 — Phase 2 PR merge 까지 보존)
```

- **Sequential merge** (parallel 금지): 동일 lane 내 multiple sub-worktree merge 시 race condition 회피. GitOpsAgent 가 lock 보유.
- **Conflict 발생 시**: user escalate (decider whitelist — destructive action 직전 stop).

**근거**: CFP-139 GitOpsAgent 의 mandate 명확화 — 본 ADR 가 lifecycle hook contract SSOT.

### 결정 4 — Cross-platform path handling

- **Bash POSIX path** = primary (Linux / macOS / Windows Git Bash).
- **Windows native path** = utility 변환 (`templates/scripts/worktree-path-util.sh` 의 `to_posix_path()` 헬퍼 + `is_windows()` detection).
- worktree 생성 / 제거 / merge 스크립트는 모두 POSIX path 입력 → 내부에서 OS 감지 후 변환.
- Claude Code Agent tool `cwd` 파라미터 = OS-native path 형태로 전달 (Windows = backslash, *nix = forward slash).

**근거**: 본 plugin 은 cross-platform consumer (mctrader = Windows dev, hypothetical Linux CI). path 처리 inconsistency 가 lifecycle hook 실패 1차 원인 — utility 일원화로 차단.

### 결정 5 — Stale GC policy

**Stale 조건** (AND):
1. Worktree last access (mtime of `.git/worktrees/<name>/HEAD`) ≥ **7 days** 전.
2. Local branch 가 origin 에 부재 (`git ls-remote --exit-code --heads origin "$BRANCH"` non-zero).

**GC trigger**:
- `on_session_start` hook — Claude Code SessionStart hook 이 `bash ${CLAUDE_PROJECT_DIR}/templates/scripts/check-worktree-stale.sh` 호출. hook sample = `templates/.claude/hooks/SessionStart-codeforge-worktree-gc.json.sample` (consumer 측 `.claude/settings.json` `hooks.SessionStart[]` merge). Install path 는 `bash scripts/bootstrap-consumer.sh` Stage 7 (CFP-97 / ADR-031) 가 `templates/consumer-scripts.manifest` 의 plugin-root-relative entry 를 consumer 작업 디렉터리에 동일 layout 으로 mirror — 따라서 consumer 의 `${CLAUDE_PROJECT_DIR}/templates/scripts/check-worktree-stale.sh` 가 정상 호출 경로.
- ad-hoc 사용자 호출 (`bash templates/scripts/check-worktree-stale.sh`).

**Note**: 본 base SSOT 는 단순 origin check 만 정의. gh API (PR merged / Issue closed) check + `cfp-NNN` Story root branch open 시 sub-worktree 보존 예외 로직 = **CFP-139 GitOpsAgent 진입 시 ADR amendment** 로 추가. 본 CFP-136 = infrastructure base (script 실제 동작 align), 강화 logic 은 GitOpsAgent 에 위임.

**근거**: 7 days = ADR-031 lane evidence freeze 와 동일 grace period. orphan worktree 누적 방지 + 활성 작업 보호. Origin branch 부재 = remote lifecycle 종료 신호 (PR merge 후 origin 에서 branch 제거되는 일반 패턴).

**보안 면제 cross-ref** (CFP-136 보안 lane iter 1 SEC-iter1-P1-1 정정): `git ls-remote --exit-code --heads origin "$BRANCH"` = anonymous git protocol read-only ref query. 외부 API · 인증 시스템 · 자격증명 비접촉 — Story §7 SSOT (filesystem-only + origin git ref query 1회 narrowing) 정합. trust boundary 영향 없음.

**Bypass mechanism** (CFP-136 보안 lane iter 1 SEC-iter1-P1-1 SSOT 보강): `BYPASS_WORKTREE_GC=1` env var 가 단일 session 의 stale check 전체를 skip — origin git ref query 미발생 + prune 미수행 + non-blocking `exit 0`. Script entry-point 첫 단계 short-circuit. 사용 케이스: (1) origin 접촉 차단 환경 (offline / restricted network), (2) debugging (false-positive stale 의심), (3) opt-out (consumer 측 정책 거부). **Env var 이름은 reserved contract** — 본 ADR SSOT 외 변경 금지 (consumer hook / wrapper Orchestrator 가 동일 이름 의존).

### 결정 6 — Scripts location + consumer distribution

**Wrapper repo**:
- `templates/scripts/worktree-create.sh`
- `templates/scripts/worktree-merge.sh`
- `templates/scripts/worktree-prune.sh`
- `templates/scripts/check-worktree-stale.sh`
- `templates/scripts/worktree-path-util.sh` (helper, 결정 4)

**Consumer distribution**: `templates/consumer-scripts.manifest` (ADR-031 / CFP-97) 에 본 5 script 추가 → consumer install 시 `${CLAUDE_PROJECT_DIR}/templates/scripts/` 로 복사 (plugin-root-relative verbatim mirror per `scripts/bootstrap-consumer.sh:335` `local target="$script_path"` SSOT — Stage 7 가 manifest entry 를 그대로 consumer working tree 에 mirror, `.claude/scripts/` 변환 로직 없음). §결정 5 GC trigger path + hook sample command path 와 1:1 정합. consumer 측 Orchestrator + GitOpsAgent (CFP-139) 가 동일 SSOT 사용.

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

## Amendment 1 — CFP-139 (2026-05-09)

**제목**: GitOpsAgent hook 실행 주체 명시 (carrier: CFP-139, codeforge-pmo plugin)

**상태**: Proposed (Phase 1 PR open) → CFP-139 Phase 2 PR merge 시점 Accepted.

### 컨텍스트

본 ADR §결정 3 (Lifecycle hooks) 는 6 hook (`on_team_create_pre/post`, `on_team_delete_pre/post`, `on_session_start`, `on_story_close`) 의 실행 주체로 "GitOpsAgent (CFP-139)" 를 anticipate 하지만, CFP-136 carrier 시점에는 GitOpsAgent 미존재 → Orchestrator inline fallback. CFP-139 가 codeforge-pmo plugin 에 GitOpsAgent 신설 → 본 ADR §결정 3 의 hook 실행 주체를 정식 위임 명시.

또한 §결정 5 의 "**Note**: gh API check + sub-worktree 보존 예외 = CFP-139 GitOpsAgent 진입 시 ADR amendment 로 추가" 약속을 본 amendment 가 이행.

### 변경

**§결정 3 hook 실행 주체** (이전 = "GitOpsAgent (CFP-139)" anticipate, 이후 = 정식 위임):

| Hook | 이전 (CFP-136) | CFP-139 이후 (Amendment 1) |
|---|---|---|
| `on_team_create_pre` | Orchestrator inline (fallback) | **GitOpsAgent** 가 `templates/scripts/worktree-create.sh <branch> <path>` × N 실행 |
| `on_team_create_post` | Orchestrator (cwd 주입) | Orchestrator (변경 없음 — teammate spawn 시점 cwd 주입은 platform inherent) |
| `on_team_delete_pre` | Orchestrator inline (fallback) | **GitOpsAgent** 가 `templates/scripts/worktree-merge.sh` sequential merge 수행 (lock 보유) |
| `on_team_delete_post` | Orchestrator inline | **GitOpsAgent** 가 `templates/scripts/worktree-prune.sh` 호출 |
| `on_session_start` | SessionStart hook (`check-worktree-stale.sh`) | **GitOpsAgent** 가 SessionStart hook 호출 보조 + 능동 GC (gh API PR merged + Story closed cross-ref) |
| `on_story_close` | (미정의) | **GitOpsAgent** 가 sub-worktree prune (Story root 제외, Phase 2 PR merge 까지 보존) |

**§결정 5 stale GC 강화** (CFP-136 의 약속 이행):

CFP-136 SSOT = 단순 origin check 만 (`git ls-remote --exit-code --heads origin`). 본 amendment 가 GitOpsAgent 진입 후 강화:

1. **gh API PR merged check**: `gh pr list --state merged --head <branch>` 검증 → merged 면 stale.
2. **Story closed cross-ref**: branch name 에서 `cfp-NNN` 추출 → Story Issue state = closed 면 stale (단 Phase 2 PR 이 open 상태면 보존).
3. **`cfp-NNN` Story root branch 보존 예외**: sub-worktree (`cfp-NNN/lane/<lane>` 등) 만 prune, Story root 는 Phase 2 PR merge 까지 보존.
4. **`BYPASS_WORKTREE_GC=1` env**: §결정 5 SSOT 무손상 — short-circuit 동작 유지.

### 이행 의무

- codeforge-pmo plugin `agents/GitOpsAgent.md` 의 responsibility table 에 본 6 hook 실행 의무 명시 (CFP-139 Phase 1 AC-1).
- CFP-139 Phase 2 e2e fixture (trace log) 에 `worktree_create / merge_attempt / worktree_delete` 3-event sequence trace 포함 (CFP-139 Phase 1 AC-10).

### 정합성 검증

- ADR-009 invariant 무손상: GitOpsAgent = codeforge-pmo plugin agent (lane plugin 영역). wrapper agent 0개 유지.
- ADR-044 정합: GitOpsAgent 는 long-running teammate (Story 전 기간 active) — phase-scoped sequential team lifecycle step 2 (`worktree 준비`) 의 실행 주체.
- ADR-024 Amendment 1 정합: hierarchical branch naming (`cfp-NNN[/<lane>[/<sub>]]`) 의 actual 생성자 = GitOpsAgent.

### 만료 / supersede

본 amendment 는 ADR-040 본문 §결정 3 / §결정 5 와 **함께 활성**. 별도 superseding amendment 없는 한 영구.


## Amendment 2 — CFP-348 (2026-05-09)

**제목**: Branch-protection-aware worktree cleanup lifecycle (carrier: CFP-348)

**상태**: Proposed → CFP-348 Phase 2 PR merge 시점 Accepted.

### 컨텍스트

ADR-040 §결정 3 `on_team_delete_pre` = "sequential merge, conflict 시 user escalate" 는 main 브랜치가 branch protection 으로 직접 push 가 차단된 경우의 동작을 미정의. 또한 §위험 "Branch protection conflict" 항에서 "sub-branch → Story root 만 merge 허용 (no main 직접 merge)" 를 언급하나 Story root → main 의 cleanup 타이밍 invariant 가 명시되지 않음.

CFP-340 `finishing-a-development-branch` 실행 시 branch protection 이 있는 repo 에서 "Merge Locally" 를 제시하여 사용자 교정 발생 → 명시적 결정 필요.

### 변경

**§결정 3 보완 — Story root worktree cleanup invariant**:

| 조건 | `on_team_delete_pre` 동작 | Cleanup trigger |
|---|---|---|
| main branch protection **없음** | sequential merge → main 직접 push | `on_team_delete_post` → worktree prune |
| main branch protection **있음** | 직접 merge 금지. PR 생성 후 대기 | `gh pr view <N> --json mergedAt` non-null 확인 후 worktree prune |

**cleanup 순서 invariant** (branch-protected repo):

```
push → PR 생성 → gh pr view <N> --json mergedAt 확인 (non-null) → git worktree remove
```

- pre-merge cleanup 절대 금지: PR merge 확인 전 `git worktree remove` = policy violation.
- Story root worktree 는 `mergedAt` 확인 시점까지 보존 의무 (Amendment 1 `on_story_close` "Phase 2 PR merge 까지 보존" 의 명시적 enforcement).

**Branch protection 감지 명령**:

```bash
gh api "repos/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/branches/main" --jq '.protected'
# "true" → cleanup invariant 적용, "false" → 직접 merge 가능
```

**GitOpsAgent 영향**: `on_team_delete_pre` hook 실행 시 위 감지 로직 수행 의무. branch-protected 감지 시 PR 생성 후 `mergedAt` polling 으로 merge 확인 → cleanup 트리거. 직접 merge 시도 금지.

### 이행 의무

- `docs/orchestrator-playbook.md` §3.5 Step 5 "Story 완료 후" 에 branch-protected lifecycle 분기 명시 (CFP-348 AC).
- `docs/consumer-guide.md` §2e 에 branch protection ↔ worktree lifecycle 연결 명시 (CFP-348 AC).
- GitOpsAgent (codeforge-pmo) `on_team_delete_pre` 구현 시 본 amendment §결정 3 보완 준수 의무 (CFP-139 follow-up).

### 정합성 검증

- Amendment 1 "Story root 제외, Phase 2 PR merge 까지 보존" 과 정합: 본 amendment 는 "Phase 2 PR merge 까지 보존" 의 enforcement 방법을 명시 (protection check + mergedAt polling).
- ADR-024 branch governance 정합: PR-only merge = ADR-024 "main 직접 push 금지" 강제 정합.
- ADR-009 invariant 무손상: 본 amendment 는 GitOpsAgent 행동 명세 추가이며 wrapper agent 신설 없음.


## 관련 파일

- [ADR-024 (story-scoped branch policy)](ADR-024-story-scoped-branch-policy.md) — 본 ADR 가 Amendment 1 로 hierarchical naming 추가.
- [ADR-009 (wrapper-only decomposition)](ADR-009-wrapper-only-decomposition.md) — wrapper agent 0 개 invariant 정합 (worktree 는 인프라, agent 추가 아님).
- [ADR-031 (lane spawn evidence)](ADR-031-lane-spawn-evidence-trail.md) — 7 days grace period 패턴 차용.
- [ADR-035 (codeforge agent teams Epic architecture)](ADR-035-codeforge-agent-teams-epic-architecture.md) — Epic-level carrier ADR (D2 implementation level 의 worktree 상세를 본 ADR 가 별도 carrier 로 분리).
- **CFP-134** — Epic carrier (worktree infrastructure + agent teams + GitOpsAgent).
- **CFP-136** — 본 ADR carrier Story (worktree infra Wave 1).
- **CFP-137** — phase-scoped agent teams (worktree convention 의존).
- **CFP-139** — GitOpsAgent (lifecycle 자동화, 본 ADR §결정 3 hook contract 구현).
