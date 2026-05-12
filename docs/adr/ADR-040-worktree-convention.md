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
  - id: 3
    carrier_story: CFP-426
    date: 2026-05-12
    title: Normative ↔ mechanical boundary mandate (frontmatter mechanical_enforcement_actions[] 의무)
    sunset_justification: "N/A — is_transitional: false (permanent governance mandate). normative ↔ mechanical boundary 자체가 codeforge 거버넌스 영구 룰."
  - id: 4
    carrier_story: CFP-429
    date: 2026-05-13
    title: Worktree-first enforcement closing the loop declaration (4/4 actual wire 완료 + gate FAIL = warning tier 유지 + actual 승격 follow-up CFP open)
    sunset_justification: "N/A — is_transitional: false (permanent governance mandate). enforcement 완료 declaration = §결정 7.A normative ↔ mechanical mandate 의 self-application closing the loop. ratchet 강화 방향 (mandate fulfillment evidence) — §결정 7.C retroactive 면제 mandate 변경 0."
mechanical_enforcement_actions:
  # FIX iter 1 F-1 (CFP-427) 정정: status enum 정합 (warning / enforcing / deferred-followup) 환원 +
  # progress_note optional string field 신설 (entry-level 진척 추적). schema 변경 = MINOR (backward compatible).
  # ADR-040 §결정 7.A schema 본문 추가는 별도 Amendment 4 (Story 4 CFP-429 carrier) 책임.
  - action: worktree-first-session-start-wire
    status: warning
    progress_note: "actual wire CFP-427 (Story 2 — scripts/check-session-start-hook-presence.sh). CFP-429 (Story 4) Amendment 4 declaration — 4/4 actual wire 완료 + ADR-060 §결정 6 promotion gate (b) bypass 외 failure > 0 FAIL → current_tier: warning 유지 + actual 승격 follow-up CFP (from-cfp-425-followup label)."
    target_section: §결정 5
  - action: worktree-first-pre-checkout
    status: warning
    progress_note: "actual wire CFP-428 (Story 3 — templates/.git-hooks/pre-checkout.sample + scripts/install-git-hooks.sh). verification-only lint. R3 self-block 회피 5-layer: (1) worktree-internal work + (2) opt-in install + (3) warning tier exit 0 + (4) BYPASS_WORKTREE_FIRST=1 env + (5) --git-dir vs --git-common-dir skip in worktree. CFP-429 (Story 4) Amendment 4 declaration — gate (b) FAIL → warning tier 유지 + actual 승격 follow-up CFP."
    target_section: §결정 7
  - action: worktree-first-pre-commit-main-block
    status: warning
    progress_note: "actual wire CFP-428 (Story 3 — templates/.git-hooks/pre-commit-main-block.sample + scripts/install-git-hooks.sh). verification-only lint, src/docs path matching only. R3 self-block 회피 5-layer: (1) worktree-internal work + (2) opt-in install + (3) warning tier exit 0 + (4) BYPASS_WORKTREE_FIRST=1 env + (5) --git-dir vs --git-common-dir skip in worktree. CFP-429 (Story 4) Amendment 4 declaration — gate (b) FAIL → warning tier 유지 + actual 승격 follow-up CFP."
    target_section: §결정 7
  - action: worktree-first-spawn-evidence-cwd
    status: warning
    progress_note: "actual wire CFP-427 (Story 2 — scripts/check-spawn-evidence-cwd.sh + enforce-from filter). CFP-429 (Story 4) Amendment 4 declaration — gate (b) FAIL → warning tier 유지 + actual 승격 follow-up CFP."
    target_section: §결정 5
related_stories:
  - CFP-134
  - CFP-136
  - CFP-137
  - CFP-139
  - CFP-348
  - CFP-425  # Epic — worktree-first mechanical enforcement 영구화
  - CFP-426  # Amendment 3 carrier
  - CFP-427  # Story 2 — SessionStart hook actual wire (worktree-first-session-start-wire + worktree-first-spawn-evidence-cwd)
  - CFP-428  # Story 3 — git layer 안전망 (worktree-first-pre-checkout + worktree-first-pre-commit-main-block actual wire)
  - CFP-429  # Story 4 — Amendment 4 carrier (closing the loop declaration)
related_adrs:
  - ADR-009
  - ADR-024  # Amendment 3 hotfix-bypass label family 동반
  - ADR-031
  - ADR-035
  - ADR-058  # is_transitional + 해소 기준 mandate (본 ADR `is_transitional: false` 정합)
  - ADR-060  # evidence-enforceable framework (본 Amendment 3 의 mechanical_enforcement_actions[] field 가 framework SSOT 연동)
related_files:
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md
  - docs/adr/ADR-058-adr-sunset-criteria-mandate.md
  - docs/adr/ADR-060-evidence-enforceable-promotion-framework.md
  - docs/evidence-checks-registry.yaml
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - templates/scripts/worktree-create.sh
  - templates/scripts/worktree-merge.sh
  - templates/scripts/worktree-prune.sh
  - templates/scripts/check-worktree-stale.sh
  - templates/scripts/worktree-path-util.sh
  - templates/github-workflows/worktree-first-session-start-wire.yml
  - templates/github-workflows/worktree-first-pre-checkout.yml
  - templates/github-workflows/worktree-first-pre-commit-main-block.yml
  - templates/github-workflows/worktree-first-spawn-evidence-cwd.yml
  - scripts/check-worktree-first-session-start-wire.sh
  - scripts/check-worktree-first-pre-checkout.sh
  - scripts/check-worktree-first-pre-commit-main-block.sh
  - scripts/check-worktree-first-spawn-evidence-cwd.sh
  - docs/orchestrator-playbook.md
is_transitional: false
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

**Mechanical enforcement** (Amendment 3 §결정 7.B Pattern I): `worktree-first-session-start-wire` (status: warning — CFP-426 Phase 2 도입) 와 `worktree-first-spawn-evidence-cwd` (status: warning) 두 evidence-check entry 가 본 §결정 5 의 hook wire 및 SessionStart 호출 정합을 verify. SSOT = `docs/evidence-checks-registry.yaml` 의 동명 entry. **bypass env**: `BYPASS_WORKTREE_FIRST=1` (4 entry 전체 lint short-circuit, `BYPASS_WORKTREE_GC` 와 disjoint scope — Amendment 3 §결정 7.E).

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


## Amendment 3 — Normative ↔ mechanical boundary mandate (CFP-426, 2026-05-12)

**제목**: normative ADR 의 frontmatter `mechanical_enforcement_actions[]` 의무 + §결정 N reference 의무 (carrier: CFP-426, parent Epic CFP-425)

**상태**: Proposed → CFP-426 Phase 1 PR merge 시점 Accepted.

### 컨텍스트

CFP-425 Epic brainstorming (2026-05-12 KST) 결과: 직전 review session 자체가 main working tree 에서 실행 중 (playbook §3.0.11 normative 미실현) + `.claude/settings.json` 에 SessionStart-worktree-gc hook 미wire (sample 만 존재) + stale worktree 17건 + base-directory 위반 2건 발견. 본 Story (CFP-426 = Epic Story 1/4) 가 Amendment 3 carrier.

근본 동인 (RequirementsAnalyst why-first 추출, Story §6.1 개념 1 verbatim):

- **moral governance** = policy declaration only (작성자 자발 준수 + review 의존)
- **mechanical enforcement** = CI lint / hook / required check 통과 의무
- 두 layer 가 **선언** 시점에 mapping 되지 않으면, 정책 작성 → enforcement 도입 시점 사이 무력화 패턴 재발

ADR-040 자체가 본 패턴의 사례: `templates/.claude/hooks/SessionStart-codeforge-worktree-gc.json.sample` 까지 만들었음에도 wrapper repo `.claude/settings.json` 에 wire 하는 "마지막 1마일" 이 빠진 채 Accepted. 동일 패턴이 ADR-053 (구조적 변경 재구동) · ADR-031 (lane-spawn evidence) 등에서 잠재.

본 Amendment 3 = "매 normative ADR 가 어떤 mechanical action 으로 enforce 되는가" 를 frontmatter 에 의무 기재하도록 함.

### Amendment

#### §결정 7 — Normative ↔ mechanical boundary mandate

##### §결정 7.A — frontmatter `mechanical_enforcement_actions[]` 의무 필드 schema

**적용 대상**: 본 ADR-040 Amendment 3 이후 **신설** 또는 **Amendment** 되는 normative ADR (즉, `is_transitional: false` 또는 frontmatter 미선언 default 안전망 추정 `true` 중 정책 SSOT 역할 카테고리 — `category: governance` / `category: security` / `category: tooling-infrastructure` / `category: dogfood-out` / `category: lifecycle`).

**Retroactive 면제 명시 (위험 R1 회피)**: 본 Amendment 3 발효 시점 (CFP-426 Phase 1 PR merge timestamp) 이전에 Accepted 된 ADR 는 본 mandate 면제. 기존 normative ADR retroactive backfill 은 CFP-D 잠정 패턴 별도 carrier (Story §3.1 cross-ref).

**면제 카테고리**:
- `is_transitional: true` ADR (해소 기준 SSOT = ADR-058 §결정 1-3) → `mechanical_enforcement_actions[]` 면제 (transitional 의 mechanical enforcement 는 본질적으로 sunset 자체 — ADR-058 lint 가 cover).
- frontmatter `status: Archived` / `status: Deprecated` / `supersedes` 항 있는 superseded ADR → 면제.
- normative declaration 이 아닌 ADR (decision-only / amendment-summary / retro-record) → 면제. 판단 기준 = `category` field 가 위 5 카테고리 외 또는 본 ADR-040 같은 정책 SSOT 역할 아님.

**Schema (A안 채택 — list[string] verbatim entry name)**:

```yaml
# frontmatter (신설 / Amendment 적용 normative ADR)
mechanical_enforcement_actions:
  - action: <evidence-check-registry entry name>   # 예: worktree-first-pre-checkout
    status: warning | enforcing | deferred-followup
    target_section: §결정 N                          # 본문 어느 결정과 binding 되는가
```

**필드 의미**:
- `action`: `docs/evidence-checks-registry.yaml` 의 `entries[].name` verbatim (kebab-case). registry 미등록 entry 직접 명시 금지 — 먼저 registry append 의무.
- `status`: 본 ADR amendment 시점 mechanical action 의 enforcement tier 와 정합.
  - `warning` = ADR-060 §결정 3 4-tier enum 의 `warning` tier (continue-on-error / non-required check). 첫 도입 default.
  - `enforcing` = `blocking-on-pr` / `blocking-on-merge` / `hotfix-bypass` tier 활성 후 (registry yaml `current_tier` 와 정합).
  - `deferred-followup` = mechanical action 도입 carrier 가 별도 follow-up CFP 일 때. action 이름 + 후속 carrier reference 의무.
- `target_section`: 본 ADR 본문 §결정 N 중 어느 결정이 본 mechanical action 으로 enforce 되는가 명시. inline 또는 별도 sub-section `## Mechanical Enforcement` 둘 다 허용 (작성자 선택).

**B안 (object — `action_type`/`target`/`current_tier` 풍부 schema) 거부 사유**: registry yaml 이 이미 entry-level 메타 (lint script path / workflow path / tier) 의 SSOT. ADR frontmatter 가 동일 정보 중복 보유 시 drift 위험. 본 Story §4.2 설계 lane 경고 힌트 (4번) 정합.

**C안 (hybrid — string + object union) 거부 사유**: schema parse 복잡도 증가, 신규 ADR 작성 시점의 의사결정 비용 (어느 form 사용?) 증가. A안 우위 단순 + 명확.

##### §결정 7.B — 본문 §결정 N reference 의무

신설 / Amendment 적용 normative ADR 의 본문에 다음 두 패턴 중 하나로 mechanical action ↔ §결정 N binding 명시:

- **Pattern I (inline, default 권고)**: 각 §결정 N 본문 끝에 1줄 추가 — `**Mechanical enforcement**: \`<action-name>\` (status: <tier>) — 본 결정의 mechanical lint 는 \`docs/evidence-checks-registry.yaml\` 의 동명 entry SSOT.`
- **Pattern II (separate sub-section)**: 본 ADR 본문 끝에 `## Mechanical Enforcement` sub-section 추가 — 표 형태 (`| action | status | §결정 N |`) 로 통합 명시. 다수 action 이 동일 §결정 N 에 묶일 때 유리.

Pattern 선택 = 작성자 자유. **단** `mechanical_enforcement_actions[]` frontmatter 에 declare 된 action 마다 본문 어딘가에 reference 존재 의무 (frontmatter ↔ 본문 정합).

##### §결정 7.C — Mandate scope = 본 ADR-040 이후 신설/Amendment ADR (retroactive 면제)

본 mandate 효력 시점 = CFP-426 Phase 1 PR merge timestamp. 이전 Accepted ADR (ADR-001 ~ ADR-059, ADR-060 포함 — CFP-389 merge 2026-05-11 가 본 Amendment 3 발효 이전) 는 **retroactive 면제**. 기존 normative ADR 의 backfill = 별도 carrier (CFP-D 잠정 패턴) 책임.

**근거 (위험 R1 회피)**: retroactive 적용 시 기존 60+ normative ADR 모두 frontmatter 갱신 + 본문 reference 추가 의무 → 폭증. 본 Story Phase 1 PR scope 외 + Epic CFP-425 scope 외. Story §2.2 암묵 가정 3 verbatim.

##### §결정 7.D — Self-application 첫 사례 (본 Amendment 3 자체)

본 Amendment 3 가 ADR-040 의 amendment 이므로 §결정 7.A 의 적용 대상 = **본 Amendment 3 자체부터**. 따라서 본 Story Phase 1 PR 의 ADR-040 frontmatter `mechanical_enforcement_actions[]` 에 4 entry verbatim:

```yaml
mechanical_enforcement_actions:
  - action: worktree-first-session-start-wire
    status: warning
    target_section: §결정 5
  - action: worktree-first-pre-checkout
    status: warning
    target_section: §결정 7   # Amendment 3 = §결정 7 자체가 worktree-first 정책
  - action: worktree-first-pre-commit-main-block
    status: warning
    target_section: §결정 7
  - action: worktree-first-spawn-evidence-cwd
    status: warning
    target_section: §결정 5
```

본 4 entry 의 actual schema = Story 1 Phase 2 PR 의 `docs/evidence-checks-registry.yaml` 추가 row + Story 2/3 의 actual wire (CFP-427/428) + Story 4 (CFP-429) 승격 평가.

##### §결정 7.E — `BYPASS_WORKTREE_FIRST` env vs `BYPASS_WORKTREE_GC` env scope 분리

본 Amendment 3 가 도입하는 4 lint script 의 short-circuit env = `BYPASS_WORKTREE_FIRST=1`. 기존 §결정 5 의 `BYPASS_WORKTREE_GC=1` 와 **disjoint scope**:

| env | scope | trigger |
|---|---|---|
| `BYPASS_WORKTREE_GC=1` | `templates/scripts/check-worktree-stale.sh` 단독 — 단일 session 의 stale check 전체 skip | 매 SessionStart hook 호출 시 |
| `BYPASS_WORKTREE_FIRST=1` | 본 Story 4 lint script 전체 skip (warning tier 신규 entry) | 매 PR `pull_request` event 시 |

두 env 동시 활성 가능 — 하나가 다른 하나의 superset 아님. 작성 시점 ArchitectAgent 검토 결과 = **분리 scope 유지** (Story §2.5 상충 후보 1 verbatim).

##### §결정 7.F — ADR-058 sunset criteria mandate 와의 공존

ADR-058 §결정 1-3 = `is_transitional` + `## 해소 기준` + 측정성 3-tuple 의무. 본 Amendment 3 §결정 7 = `mechanical_enforcement_actions[]` + §결정 N reference 의무. 두 mandate **frontmatter 다른 field** + 본문 다른 sub-section → 충돌 없이 공존.

Validation: 본 ADR-040 frontmatter = `is_transitional: false` + `mechanical_enforcement_actions[]` 4 entry 동시 보유. `## 해소 기준` 섹션 = `N/A — permanent policy` 1줄. 두 mandate 동시 충족 가능 사례 = 본 ADR 자체.

##### §결정 7.G — Normative ADR category 판단 룰 (ArchitectAgent 신설 시점)

신설 ADR 의 `category` field 가 다음 5종 중 하나면 normative ADR — `mechanical_enforcement_actions[]` 의무:

1. `governance` — 거버넌스 정책 (예: ADR-024 / ADR-039 / ADR-058 / ADR-060)
2. `security` — 보안 정책 (예: 향후 ADR — `is_transitional: false` default presumption per ADR-058 §결정 7)
3. `tooling-infrastructure` — tooling / infra (예: ADR-040 / ADR-050)
4. `dogfood-out` — codeforge family 내부 운영 정책 (예: ADR-013 / ADR-016 / ADR-017)
5. `lifecycle` — lane / agent lifecycle (예: ADR-023 / ADR-044)

이외 카테고리 (decision-only / retro-record / amendment-summary 등) 또는 `is_transitional: true` ADR = 면제. 신설 ADR 의 category 결정 모호 시 **안전 방향 = 의무 적용** (false negative 차단 우선).

### 이행 의무

- 본 Phase 1 PR (CFP-426) 에 ADR-040 frontmatter `mechanical_enforcement_actions[]` 4 entry 추가 + 본 §결정 7 본문 추가 (위 §7.A~§7.G).
- 본 Phase 2 PR (CFP-426) 에 `docs/evidence-checks-registry.yaml` 4 row append (warning tier) + 4 lint script + 4 workflow yml + 4 `hotfix-bypass:worktree-*` label 등록.
- CFP-427 (Story 2) 에서 `worktree-first-session-start-wire` 의 actual wire 첫 사례 (`worktree-first-spawn-evidence-cwd` 도 함께).
- CFP-428 (Story 3) 에서 `worktree-first-pre-checkout` + `worktree-first-pre-commit-main-block` 의 git layer install.
- CFP-429 (Story 4) 진입 시 ADR-060 §결정 6 promotion gate 충족 여부 재평가 — gate 충족 시 4 entry `status: warning → enforcing` 전환 + ADR-040 Amendment 4 (enforcement 완료 선언).
- 본 Amendment 3 이후 신설되는 모든 normative ADR (5 category) 의 frontmatter `mechanical_enforcement_actions[]` 누락 시 DesignReview lane P1 finding 의무.

### 정합성 검증

- **ADR-058 정합**: `## 해소 기준` 섹션 = `N/A — permanent policy` (본 ADR `is_transitional: false`). 본 Amendment 3 도 host ADR 의 sunset 분류 그대로 상속 (Amendment 단독 sunset 섹션 도입 불필요 — ADR-058 §결정 5 정합).
- **ADR-060 정합**: `mechanical_enforcement_actions[].action` 의 verbatim entry name 4종 = `docs/evidence-checks-registry.yaml` Phase 2 PR row append entry 와 1:1 mapping. registry 미등록 action 명시 시 §결정 7.A 위반.
- **ADR-024 Amendment 3 정합**: 4 entry 가 4 `hotfix-bypass:worktree-*` label 동반 (per-entry namespace per §결정 6.A) — Story 1 Phase 2 PR 에 4 label `gh label create` 의무.
- **ADR-009 invariant 무손상**: 본 Amendment 3 = 정책 mandate 추가만 — wrapper agent 신설 0.
- **ADR-039 정합**: 본 Story 의 모든 lane spawn 작업 = subagent default (Agent tool spawn) — `mechanical_enforcement_actions[]` 의 actual enforce 는 GitHub Actions runner 단독 (Agent spawn 무관).
- **ADR-040 본문 §결정 1~6 + Amendment 1 + Amendment 2 무손상**: 본 Amendment 3 = 새 §결정 7 추가만, 기존 결정 변경 없음.

### Compatibility

- 기존 normative ADR (ADR-001 ~ ADR-060) `mechanical_enforcement_actions[]` 미보유 — retroactive 면제 (§결정 7.C). frontmatter lint 의 schema 정합 위반 0.
- 향후 신설 normative ADR 의 frontmatter schema 변경 = MINOR (backward compatible — 기존 필드 변경 없음, 신규 optional → 의무 field 추가).
- `BYPASS_WORKTREE_FIRST=1` env = 본 Amendment 3 가 정의 + reserved. consumer hook / wrapper Orchestrator 가 동일 이름 의존 시 본 ADR SSOT 외 변경 금지 (§결정 7.E 정합).

### Related

- CFP-425 Epic (worktree-first mechanical enforcement 영구화)
- CFP-426 Story 1 (본 Amendment 3 carrier) — Issue mclayer/plugin-codeforge#426
- CFP-427 Story 2 (SessionStart hook actual wire)
- CFP-428 Story 3 (git layer pre-checkout + pre-commit-main-block)
- CFP-429 Story 4 (Amendment 4 carrier — closing the loop declaration + gate FAIL = warning tier 유지)
- ADR-024 Amendment 3 (hotfix-bypass label family — 4 신규 `hotfix-bypass:worktree-*` label 등록 동반)
- ADR-058 (sunset criteria mandate — `is_transitional` + `## 해소 기준` 공존)
- ADR-060 (evidence-enforceable framework — `mechanical_enforcement_actions[].action` 의 registry SSOT)


## Amendment 4 — Self-application closing the loop declaration (CFP-429, 2026-05-13)

**제목**: §결정 7.D self-application 4/4 actual wire 완료 사실 + ADR-060 §결정 6 promotion gate 평가 결과 반영 (gate FAIL = warning tier 유지 + actual 승격 follow-up CFP open)

**상태**: Proposed → CFP-429 Phase 1 PR merge 시점 Accepted.

### 컨텍스트

본 Amendment 4 = §결정 7.D self-application 첫 사례 (Amendment 3 carrier Story 1 = CFP-426) → Story 2 (CFP-427 = 진입 단계 2/4 actual wire) → Story 3 (CFP-428 = git layer 2/4 actual wire 추가 = 4/4 actual wire 완료) closing the loop 의 final declaration. 4 evidence-check entry 의 actual wire 진척 = 100% 완료 (skeleton → actual logic 전환 4/4).

ADR-040 §결정 7.A `mechanical_enforcement_actions[]` schema = "매 normative ADR 가 어떤 mechanical action 으로 enforce 되는가" 의 self-fulfillment evidence 누적 — Amendment 1/2 = mandate 도입 + scope 확장, Amendment 3 = self-application 첫 사례, **Amendment 4 = self-application closing the loop (= mandate 자체의 실효성 검증)**.

### Amendment

#### §결정 7.H — Self-application closing the loop declaration (Amendment 4, CFP-429, 2026-05-13)

##### §7.H.1 — ADR-060 §결정 6 promotion gate 평가 결과 (본 Story carrier 자체)

| 조건 | threshold | actual | result |
|---|---|---|---|
| (a) PR 누적 ≥ 20 (window: 2026-05-12T09:52:09 KST → 2026-05-13T15:30:00 KST) | 20 | 37 | PASS |
| (b) bypass label 외 failure count = 0 | 0 | >0 (4 workflow 매 PR final commit lint failure conclusion 다수 — 100+ run failure sample) | **FAIL** |
| (c) sibling Story merged ([CFP-427, CFP-428, CFP-429]) | 3/3 | 3/3 (CFP-429 self-reference at Phase 2 PR merge) | PASS |

**Verdict**: gate FAIL — 조건 (b) bypass 외 failure > 0. 

##### §7.H.2 — Amendment 4 결정 (declaration only scope)

1. **4 entry `current_tier: warning` 유지** — `docs/evidence-checks-registry.yaml` 4 entry tier 변경 0. `worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}` 모두 `warning` 유지.
2. **4 workflow `continue-on-error: true` 유지** — `templates/github-workflows/worktree-first-*.yml` + `.github/workflows/worktree-first-*.yml` 변경 0.
3. **Amendment 4 declaration only scope** — closing the loop 사실 + gate FAIL evidence + actual 승격 follow-up CFP cross-ref 의 mechanical declaration. mandate 새 도입 0.
4. **frontmatter `mechanical_enforcement_actions[]` 4 entry `progress_note` 갱신** — "CFP-429 (Story 4) Amendment 4 declaration — 4/4 actual wire 완료 + ADR-060 §결정 6 promotion gate (b) bypass 외 failure > 0 FAIL → current_tier: warning 유지 + actual 승격 follow-up CFP (from-cfp-425-followup label)." status field `warning` 유지.
5. **actual 승격 follow-up CFP open** — 본 Story Phase 2 PR 안 conditional step (gate FAIL = trigger). `gh issue create --label "type:story,phase:요구사항,from-cfp-425-followup" --title "[STORY] worktree-first 4 entry actual warning → blocking-on-pr 승격 (CFP-425 Epic post-closure)"`. 본 follow-up Story 가 evidence 6 산출물 (i~vi) 전체 충족 후 actual 승격 carrier 책임.
6. **§결정 7.D self-application 완료 history 기록** — Story 1 (skeleton declaration) → Story 2 (2/4 actual wire) → Story 3 (4/4 actual wire) → Story 4 (Amendment 4 declaration + gate 평가) 의 4-step sequence verbatim. 본 Amendment 4 = §결정 7 mandate fulfillment evidence.

##### §7.H.3 — §결정 7.A schema 무손상

`mechanical_enforcement_actions[]` schema (action / status / progress_note / target_section) 변경 0. data update only (progress_note string field 갱신). MINOR bump 0 (Story 2 가 신설한 optional field 의 data update).

##### §7.H.4 — §결정 7.C retroactive 면제 무손상

본 Amendment 4 도 host ADR-040 의 §결정 7.C scope 안 — CFP-426 merge timestamp 이전 ADR retroactive 면제 mandate 변경 0.

##### §7.H.5 — §결정 7.D self-application closing the loop 명시

본 Amendment 4 가 §결정 7.D "Self-application 첫 사례 (본 Amendment 3 자체)" 의 closing the loop = "4 entry actual wire 완료 + gate 평가 carrier 자체". 본 §7.D 본문 변경 0 — §7.H 가 §7.D 의 self-application progression 의 final step 임을 declare.

##### §7.H.6 — §결정 7.E `BYPASS_WORKTREE_FIRST` env contract 무손상

본 Amendment 4 env contract 변경 0.

##### §7.H.7 — actual 승격 follow-up CFP scope

- title: `"[STORY] worktree-first 4 entry actual warning → blocking-on-pr 승격 (CFP-425 Epic post-closure)"`
- label: `type:story` + `phase:요구사항` + `from-cfp-425-followup` (신규 label — label-registry-v2 v2.4 → v2.5 MINOR bump 동반 의무)
- scope:
  - 4 entry actual `current_tier: warning → blocking-on-pr` 갱신
  - 4 workflow `continue-on-error: true → false` 변경
  - ADR-060 §결정 6 evidence 6 산출물 (i~vi) 전체 충족 (특히 (iv) GitHub Actions outage runbook + (v) audit comment author verification lint + (vi) sticky comment pattern — 본 Story scope 외)
  - `required_status_checks.contexts` 4 entry 부착 (ADR-024 Amendment 4 가칭 carrier 동반 가능성)
  - plugin.json MINOR bump 가능성 (ADR-016 + ADR-063 atomic invariant 정합)
  - CLAUDE.md "GitHub Workflow" 섹션 4 entry warning/blocking 분류 갱신 (CFP-506 ratchet ≤320줄 cap 정합)

### 이행 의무

- 본 Phase 1 PR (CFP-429) 에 ADR-040 frontmatter `amendments[]` row 4 append + `mechanical_enforcement_actions[]` 4 entry `progress_note` 갱신 + 본 Amendment 4 sub-section append.
- 본 Phase 2 PR (CFP-429) 에 `docs/evidence-checks-registry.yaml` 4 entry description 갱신 + `templates/github-workflows/story-init.yml` reminder step 추가 + `tests/integration/stories/CFP-425/self-test-worktree-block.sh` 신설 + `.github/workflows/self-test-worktree-block.yml` 신설 + follow-up CFP open conditional step.
- 본 Phase 2 PR merge 후 GitOpsAgent (Orchestrator 위임) 가 follow-up CFP open conditional step 실행 — duplicate Issue check + label 신설 + Issue open.
- Task 4.7 EPIC-RESULTS-CFP-425.md artifact 작성 + Epic close PR (PMOAgent 책임, 본 Amendment 4 scope 외).

### 정합성 검증

- **ADR-058 정합**: `## 해소 기준` 섹션 = `N/A — permanent policy` (host ADR `is_transitional: false`). 본 Amendment 4 도 host ADR 의 sunset 분류 그대로 상속 (Amendment 단독 sunset 섹션 도입 불필요 — ADR-058 §결정 5 정합). frontmatter `amendments[]` row 4 `sunset_justification` 의무 명시 (위 frontmatter row 4 verbatim).
- **ADR-060 정합**: §결정 6 promotion gate 평가 = 본 Amendment 4 carrier 자체. gate FAIL 결정 + evidence (i)~(iii) 산출물 명시 (Change Plan §1 frontmatter `gate_evaluation` block verbatim). evidence (iv)~(vi) = actual 승격 carrier 의무 (본 Amendment 4 scope 외).
- **ADR-024 Amendment 3 정합**: 4 `hotfix-bypass:worktree-*` label family 활성화 유지 (label 추가 0). 신규 label `from-cfp-425-followup` 추가 — label-registry-v2 v2.4 → v2.5 MINOR bump.
- **ADR-009 invariant 무손상**: 본 Amendment 4 = declaration only — wrapper agent 신설 0.
- **ADR-040 본문 §결정 1~7 + Amendment 1 + Amendment 2 + Amendment 3 §7.A~§7.G 무손상**: 본 Amendment 4 = §7.H sub-section 추가만, 기존 결정 변경 없음.

### Compatibility

- 기존 normative ADR (ADR-001 ~ ADR-064) `mechanical_enforcement_actions[]` 미보유 — retroactive 면제 (§결정 7.C). frontmatter lint 의 schema 정합 위반 0.
- 본 Amendment 4 = data update only / no schema change / no MINOR bump (Story 2 가 신설한 optional field `progress_note` data update).
- `BYPASS_WORKTREE_FIRST=1` env = Amendment 3 정의 + reserved. 본 Amendment 4 env contract 변경 0.

### Related

- CFP-425 Epic (worktree-first mechanical enforcement 영구화)
- CFP-426 Story 1 (Amendment 3 carrier — skeleton 4 entry 도입)
- CFP-427 Story 2 (진입 단계 2 entry actual wire)
- CFP-428 Story 3 (git layer 2 entry actual wire — 4/4 완료)
- CFP-429 Story 4 (본 Amendment 4 carrier — closing the loop declaration + gate FAIL = warning tier 유지)
- ADR-060 §결정 6 (promotion gate evaluation — 본 Amendment 4 carrier)
- ADR-024 Amendment 3 §결정 6.A (hotfix-bypass label family + `from-cfp-425-followup` 신규 label 동반)
- ADR-058 (sunset criteria mandate — `is_transitional: false` 상속 + frontmatter row 4 `sunset_justification` 의무)


## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-024 (story-scoped branch policy)](ADR-024-story-scoped-branch-policy.md) — 본 ADR 가 Amendment 1 로 hierarchical naming 추가. **Amendment 3 carrier 시점 = CFP-426 = `hotfix-bypass:worktree-*` label family 4 신규 entry 동반 (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합)**.
- [ADR-009 (wrapper-only decomposition)](ADR-009-wrapper-only-decomposition.md) — wrapper agent 0 개 invariant 정합 (worktree 는 인프라, agent 추가 아님).
- [ADR-031 (lane spawn evidence)](ADR-031-lane-spawn-evidence-trail.md) — 7 days grace period 패턴 차용. **Amendment 3 시점 = §14 Lane Evidence `Working dir:` field 가 `worktree-first-spawn-evidence-cwd` lint 의 검증 대상**.
- [ADR-035 (codeforge agent teams Epic architecture)](ADR-035-codeforge-agent-teams-epic-architecture.md) — Epic-level carrier ADR (D2 implementation level 의 worktree 상세를 본 ADR 가 별도 carrier 로 분리).
- [ADR-058 (ADR sunset criteria mandate)](ADR-058-adr-sunset-criteria-mandate.md) — **Amendment 3 frontmatter `mechanical_enforcement_actions[]` 가 ADR-058 의 `is_transitional` + `## 해소 기준` mandate 와 공존 (§결정 7.F)**.
- [ADR-060 (evidence-enforceable framework)](ADR-060-evidence-enforceable-promotion-framework.md) — **Amendment 3 의 `mechanical_enforcement_actions[].action` verbatim 이 `docs/evidence-checks-registry.yaml` SSOT 와 1:1 mapping**.
- **CFP-134** — Epic carrier (worktree infrastructure + agent teams + GitOpsAgent).
- **CFP-136** — 본 ADR carrier Story (worktree infra Wave 1).
- **CFP-137** — phase-scoped agent teams (worktree convention 의존).
- **CFP-139** — GitOpsAgent (lifecycle 자동화, 본 ADR §결정 3 hook contract 구현).
- **CFP-425** — Epic carrier (worktree-first mechanical enforcement 영구화).
- **CFP-426** — Amendment 3 carrier (본 §결정 7 — normative ↔ mechanical boundary mandate).
