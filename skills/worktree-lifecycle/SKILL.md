---
name: worktree-lifecycle
description: Worktree-first 개발 규약 lookup 시 (① 코딩/수정 작업 개시 직전 worktree 생성, ② Story/PR 완결 직후 eager 정리). 개시(생성위치 표준·3단계 deadline) → 작업 중 git -C 주입 → 완결 시 정리(1급 단계) → backstop GC → 잔재 발견·scratch TTL·orphan 판정(§4a) → residue-clean 완료-게이트 → bypass env 의 전 lifecycle 을 정의한다. lookup mirror — 정책 SSOT = ADR-040(+Amd 1~9) + ADR-169(세션 잔재 수명 규약), 절차 SSOT = orchestrator-playbook §3.5 + §0a-prime + §9.7.1/§9.7.2.
tools: Read
---

# Worktree Lifecycle (CFP-2191 / ADR-040 Amendment 8·9 / ADR-169)

> 참조 테이블 skill — 코딩/수정 작업 **개시 직전** 과 Story/PR **완결 직후** 두 시점에 본 skill 을 확인하세요.

본 skill 은 **lookup mirror** — 내용의 원본은 아래 2곳이며 본 skill 로의 SSOT 이동/변경 금지:

- **정책 SSOT**: [ADR-040 worktree convention (+Amendment 1~9)](../../archive/adr/ADR-040-worktree-convention.md) + ADR-169(세션 잔재 수명 규약 — 잔재 발견/scratch TTL/생성위치 가드/residue-clean 완료-게이트)
- **절차 SSOT**: [orchestrator-playbook](../../docs/orchestrator-playbook.md) §3.5 (Worktree dispatch + 잔재 발견/scratch TTL) + §9.7.1/§9.7.2 (residue-clean 완료-게이트) + Step 0a-prime (eager 정리 + backstop GC)

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
- **생성위치 표준 (CFP-2822 / ADR-169)**: worktree 는 base dir(`~/.claude/worktrees/<repo>/`) **안에서만** 생성. 표준 위치 밖 `git worktree add <path>` = 위반 — PreToolUse 위치 가드(`WORKTREE_LOCATION_GUARD_TIER=warn|block`)가 도입기 warn(auto-relocate 안내 = base dir 경유 재생성 권고) → 승격기 block. **1차 예방(fail-open — matcher 회피·명령 난독화로 완전차단 불가) ⊕ discovery 스캐너 2차 검출**(§4a AC-11 미등록 orphan count). bypass `BYPASS_WORKTREE_LOCATION_GUARD`. "기계적 차단" ≠ 완전봉인(over-claim 금지).
- **생성 시점 3단계 수명 deadline (AC-4)**: worktree/scratch 생성 시 creation timestamp 기준 3-deadline 이 규약으로 내재 — (1) **TTL** = scratch loose 파일 age>TTL 자동 purge(§4a) / (2) **eager-deadline** = Story/PR 완결 즉시 정리(§3) / (3) **backstop-deadline** = age 7d + merged + clean + not-locked orphan GC(§4). 별도 timestamp 파일 불요 — 파일시스템 mtime(생성/최근 접근) + git 등록부가 age SSOT.

## 2. 작업 중 — worktree-pinned operation

- **subagent spawn 시**: prompt 에 `Working dir: <worktree-path>` 주입 (playbook §3.5 step 2).
- **모든 file operation** = worktree 절대경로 기준 — git command 는 `git -C <worktree_abs_path> <subcommand>`, Write/Edit 는 worktree 하위 absolute path (forward-slash 정규형). 상대경로 호출은 harness cwd reset 후 main repo 로 resolve 되는 사고 경로 (ADR-040 Amendment 6 §결정 7.J.1).
- **Read/Grep 도 worktree 경로 고정** — main repo path 는 stale snapshot 위험 (ADR-040 Amendment 7 §결정 7.J.4).
- **cross-repo 작업** = repo 별 worktree 분리. wrapper worktree 안에서 internal-docs write 금지 — 별도 worktree explicit create + switch (playbook §3.5.2 / ADR-168 §결정 1 sub-scope 1-J (구 ADR-082 Amendment 21, 재제정 CFP-2840)).

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

**자동 트리거 = `SessionEnd` async dispatch (primary wire)** (ADR-040 Amendment 9 §결정 5 / ADR-128 §결정 3): `hooks/hooks.json` SessionEnd entry (`async: true`) → `hooks/session-end` 가 background GC (`check-worktree-stale.sh`) 호출. 세션당 1회 종료 발화 → 7일 GC cadence 빈도 정합. **동시 GC race 방지 invariant (비협상)**: SessionEnd + Stop 동시 wire 금지. **단 ADR-169 §결정 4 재해석(SessionEnd primary + SessionStart detached carve-out)**: 진짜 invariant = 동시 GC race 방지이지 "단일 wire"가 아님 — 단일 wire **OR 멱등/lock 실증 다중 wire**. crash-blind-spot 보완 = SessionStart detached lazy GC 다중화(§4a, mkdir 원자 lock + cooldown + 멱등 remove 선행 조건). 수동/스케줄 호출도 병행 가능:

```bash
GC_DRY_RUN=1 bash templates/scripts/check-worktree-stale.sh   # preview (prune 대상만 보고)
bash templates/scripts/check-worktree-stale.sh                # 실제 prune — 수동/스케줄 호출
```

prune 조건 = 4 조건 **ALL** (스크립트 헤더 SSOT):

1. age > 7일 (`STALE_DAYS` 기본 7)
2. branch MERGED (squash-aware: `gh pr list --state merged --head <branch>` + merged PR `headRefOid` 이후 추가 local commit 0). gh 부재/실패 시 fail-safe 보존
3. worktree CLEAN (tracked 변경 0 + 알려진 임시파일 외 untracked 0 — 잔여 변경 있으면 절대 prune 금지)
4. 현재/main worktree 아님 + `locked` 아님

> **중단 이후 회수(salvage) 절차는 여기 없다** — mid-run 사망·stall·한도 도달·429 4-class 의 회수 라우팅·미완결 산출 고정·번들 인계 = [`codeforge:session-recovery`](../session-recovery/SKILL.md) 3부 (본 skill 은 lookup mirror 라 신규 절차 SSOT 를 두지 않는다).

> 과거 SessionStart hook 동기/주기 호출은 제거됨 (worktree 90+ 동기 스캔으로 세션 시작 지연). **SessionStart 배제 = 무거운 동기 full-scan 한정** — SessionStart async:true 무시 → 동기 실행 = 지연 회귀라 배제(요구사항리뷰 PASS 확정 외부사실). **단 detached fire-and-forget(즉시 return + 실 스캔 분리 프로세스)는 carve-out**(전제 불성립 → §4a 크래시 보완 트리거, ADR-169 §결정 4). backstop 자동 트리거 = SessionEnd async primary wire + SessionStart detached lazy GC(§4a) + 수동/스케줄 병행.

## 4a. 잔재 발견(residue discovery) + scratch TTL + orphan 3축 판정 (CFP-2822 / ADR-169)

backstop(§4)이 커버 못하는 **사각지대**(codeforge-scratch·workspace root `_wt-*`·홈 직하 미등록 git dir·harness Temp·stash) 전용 **상위집합** 스캔. backstop 과 **disjoint** — 등록 worktree 는 backstop 전담(discovery 는 cross-check-only 로 인식-후-제외, 재판정 X).

```bash
bash templates/scripts/check-workspace-residue-discovery.sh                     # 전체 스캔 (aging report)
bash templates/scripts/check-workspace-residue-discovery.sh --story-key cfp-NNN # Story-scoped (완료-게이트 §4b)
bash templates/scripts/check-codeforge-scratch-ttl.sh                           # scratch TTL purge (loose-file only)
```

- **orphan 3축 판정 (AC-12)**: (1) 등록여부 (2) git존재 (3) 상태검사 필요여부 — **분류 신호로만**(삭제 여부 미결정). 3-케이스: (a) 등록 worktree → backstop 4-AND 위임 (b) 독립 clone·미등록 git dir → 상태검사(dirty/unpushed/stash/locked, **gh-merged 판정 안 함** — PR lifecycle 부재) (c) git 부재 빈 껍데기 → age+canonical 후 안전 삭제. **미등록 위치 git dir = "unregistered-location" 사유 기록 + 별도 count (AC-11)**.
- **보존 트리거 = 상태 신호 한정 (INV-1)**: dirty / unpushed-N / locked / pin / INCONCLUSIVE 1+ 양성 또는 판정 불능 → fail-safe 보존 + 메타파일 사유 기록. **등록·존재 여부 자체 ≠ 보존 사유**. mtime 단독 삭제 금지(상태 신호 AND). gh/network 실패 → 항상 KEEP + "network-inconclusive"(INV-2, "판정 못하니 삭제" 절대 금지).
- **scratch TTL purge (AC-5)**: codeforge-scratch 내부 age>TTL **순수 loose 파일**만 자동 삭제. `.git` 보유 항목(clone/worktree/export)은 삭제 제외 → orphan 회부. 상태·메타파일은 scratch **밖** `~/.claude/worktree-gc-state/`(자기소멸 회피).
- **harness Temp = observe-only (AC-6 1단계, INV-9)**: Temp 하위 총량·나이·git-여부 관측 + git-aware 판정(unpushed/stash/locked → 보존 "temp-git-worktree"). **삭제 실행 0** — 2단계(삭제)는 `TEMP_GC_DELETE_ENABLED` default-off + self-scratchpad 배제·활성세션 proxy·harness GC 중복 해소 3전제 충족 후에만. 제3자 소유 Temp 삭제 금지 = 보안 불변식.
- **fail-safe (AC-7)**: dirty/unpushed/locked/pin 감지 시 보존 + 사유 명시("dirty" / "unpushed-N-commits" / "locked" / "pin") + 메타파일 저장 + 상태 보고 포함. 자동 unlock/force 금지(INV-1, 수동 해소만).
- **reporting (AC-8/8a/14/15)**: `[residue-scan] DONE: scanned=N flagged=M`(**always exit 0 advisory**, 기존 `[stale-check]`/`[completion-clean]` output contract 무접촉). 보존-예외 항목별 **사유 + 나이(aging)** 집계 + 임계 초과 **재알림**(지수 backoff base 7d→max 90d + item+reason dedup). **stash census**(건수·나이, **삭제 0** — 가시화-only, git 무만료 = 의도적 사용자 데이터) + **용량 임계 경고** + 순수 관측 집계(삭제수/보존수/회수GB 히스토리). 재알림 상태 = `~/.claude/worktree-gc-state/` JSONL append(크래시 무손상).
- **크래시 보완 트리거 (AC-3/13)**: SessionEnd best-effort eager + **SessionStart detached lazy GC** 다중화(ADR-169 §결정 4 — "멱등/lock 실증 다중 wire" 완화). 2차 트리거 활성화 전 **mkdir 원자 lock + cooldown + 멱등 remove 선행**(E10 double-delete 0). detach = Windows `Start-Process -WindowStyle Hidden` / POSIX `setsid`·`nohup+disown`(bash nohup 은 harness 트리 wait 시 미분리 가능 주의). OS 스케줄러(ADR-110) = consumer opt-in 보조(주 트리거 아님).
- **정책 SSOT** = ADR-169(세션 잔재 수명 규약), 절차 SSOT = playbook §3.5. 대상=worktree 클래스 한정(Temp 2단계·stash 는 GC 삭제 경로에 미포함, AC-3).
- **비대화형(사람 없는) 호출 계약** = [orchestrator-playbook](../../docs/orchestrator-playbook.md) §0a-prime-2 참조 (작업 디렉터리 고정 · 관측-only 3중 게이트 · exit code 비-오라클 · 출력 verdict 어휘 미인용 · 발화 주체). 본 skill 의 절차는 호출 맥락에 따라 분기하지 않는다 — 위 계약은 절차 위에 얹히는 호출측 규약이다.

## 4b. 완료-게이트 — phase:완료 worktree-clean self-check

backstop(§4, age 7d+ orphan)과 **disjoint** — 정상 완료 경로의 eager 누락(0일령 worktree 잔존)을 검출하는 advisory 게이트 (ADR-040 Amendment 9 §결정 7.K / ADR-045 Amendment 13 §D-12). 정리 *실행* owner = GitOpsAgent eager 불변 — 본 게이트는 *검증*만.

```bash
STORY_KEY=cfp-NNN bash scripts/check-worktree-completion-clean.sh   # detected=0 = eager 정리 완료
```

검출 대상 (F2 구분 계약, ADR-040 §결정 7.K): (a) 본 STORY_KEY scope ∧ ((b) sub-worktree `cfp-NNN/lane/*`·`cfp-NNN/fix-iter-*` 잔존 = 즉시 검출 OR (c) Story root `cfp-NNN` flat = Phase 2 PR `mergedAt` non-null 일 때만 검출, open(보존 중)이면 제외). fail-safe 4종 상속 (gh 미인증→보존 / dirty→data-loss 가드 / hard-block 금지 / always exit 0). `phase:완료` transition precondition (playbook §9.7.1 (c)) 에서 Orchestrator self-check 가 호출. warning-tier 로컬 self-check (required CI 불가 — worktree 클라우드 러너 미접근).

**residue-clean self-check (CFP-2822 / ADR-169 §결정 9)**: worktree-clean 과 **disjoint 형제** — 완료 Story 잔재(worktree+scratch+stash+orphan) 가시화 확인(worktree-clean = 등록 worktree eager 미실행 검출 / residue-clean = 잔재 전반 가시화).

```bash
bash templates/scripts/check-workspace-residue-discovery.sh --story-key cfp-NNN   # flagged 보존항목 aging 리포트 확인
```

`phase:완료` transition precondition (playbook §9.7.1 (e)) 에서 Orchestrator self-check 가 호출. **자동 삭제 강제 아님**(가시화 = INV-3, stash 자동삭제 = Non-goal). fail-safe 4종 상속. warning-tier 로컬 self-check (required CI 불가 — 잔재 스캔 대상[~/.claude/worktrees·codeforge-scratch·workspace root·Temp] 클라우드 러너 미접근, branch protection 8-tuple 무변경). evidence-checks-registry `residue-clean-completion-gate` (warning-tier, workflow:null, **`gate:residue-clean` label 미신설** — §D-12 worktree-clean 패턴 답습).

## 5. bypass env — disjoint scope (ADR-040 §결정 5 기존 2종 + ADR-169 신규 3종)

하나가 다른 하나의 superset 아님 (ADR-040 §결정 5 + Amendment 3 §결정 7.E). env 이름 = reserved contract (ADR-040/ADR-169 SSOT 외 변경 금지). 신규 3종 전부 기존 31개와 **disjoint**(INV-6) + 각 사용 시 **audit 한 줄 의무** + 전역 export 경고.

| env | scope | trigger |
|---|---|---|
| `BYPASS_WORKTREE_GC=1` | `check-worktree-stale.sh` 단독 — stale check 전체 skip (origin 접촉 0 + prune 0, non-blocking exit 0) | stale check 호출 시 |
| `BYPASS_WORKTREE_FIRST=1` | worktree-first lint 4종 (`session-start-wire` / `pre-checkout` / `pre-commit-main-block` / `spawn-evidence-cwd`) 전체 short-circuit | PR `pull_request` event 시 |
| `BYPASS_WORKTREE_LOCATION_GUARD=1` | ① 생성위치 PreToolUse 가드 skip (§1 생성위치 표준) | `git worktree add` 발화 시 (ADR-169) |
| `BYPASS_WORKSPACE_RESIDUE_SCAN=1` | ③④ discovery(orphan+Temp+stash) skip (§4a). `BYPASS_WORKTREE_GC` 재사용 금지(범위가 worktree 초과) | residue 스캔 호출 시 (ADR-169) |
| `BYPASS_CODEFORGE_SCRATCH_TTL=1` | ② scratch TTL purge skip (§4a) | scratch TTL 호출 시 (ADR-169) |

- **별도 축(bypass 아님)**: `TEMP_GC_DELETE_ENABLED`(default-off — Temp 삭제 2단계 gate, INV-9) / `WORKTREE_LOCATION_GUARD_TIER=warn|block`(위치 가드 tier). `GC_DRY_RUN=1`(파괴적 동작 preview) = **재사용**(신규 이름 X). 가드-무력화 계열(`GC_TEMP_IGNORE_RE`/`GC_*_BIN`)은 production 미노출(test-only 격리).
