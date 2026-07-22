---
adr_number: 135
title: "force-push pre-flight HEAD-pin 가드 (own-branch push-time race-guard — local pre-push hook 차단 + CI 사후 detect warning 2-layer)"
status: Proposed
category: orchestration-discipline
date: 2026-06-30
carrier_story: CFP-2490
parent_epic: CFP-2481
supersedes: null
amends: null
related_adrs:
  - ADR-039  # Pre-spawn-pin mandate (§결정 14) — branch 생성 시점 HEAD pin. 본 ADR = push 시점 layer sibling (axis disjoint: branch-create-time vs push-time)
  - ADR-073  # Orchestrator verify-before-assert — Amendment 5 가 CFP-1103 (force-push pre-flight) 을 sibling 으로 명시. 본 ADR 이 그 carrier (axis disjoint: cross-repo state assertion vs own-branch push pre-flight)
  - ADR-060  # Evidence-enforceable promotion framework — CI 사후 detect = warning tier 도입 (blocking 승격 = recurrence-driven)
  - ADR-115  # Runtime hook enforcement — local pre-push hook 채널 근거 (opt-in installer)
  - ADR-040  # Worktree convention — pre-push hook 은 per-worktree opt-in install
  - ADR-005  # Self-app byte-identical — CI 사후 detect workflow templates/ ↔ .github/ parity
  - ADR-061  # Python thin-wrapper convention — CI detect script (sh thin wrapper + py SSOT)
  - ADR-024  # Story-scoped branch policy — hotfix-bypass:* family namespace (신규 bypass label)
  - ADR-127  # No-exemption full-flow — 정식 Phase 1/2 PR 분리
related_files:
  - archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md
  - archive/adr/ADR-073-orchestrator-verify-before-assert.md
  - templates/.claude/hooks/pre-push.sh.sample
  - templates/.claude/hooks/pre-push-auto-rebase.sh.sample
  - scripts/install-git-hooks.sh
  - docs/evidence-checks-registry.yaml
  - docs/inter-plugin-contracts/label-registry-v2.md
mechanical_enforcement_actions:
  - force-push-base-advance-detect   # CI 사후 detect (warning tier) — evidence-checks-registry entry Phase 2 wire
is_transitional: false
sunset_justification: "N/A — permanent orchestration-discipline policy. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 방향 — own-branch force-push pre-flight HEAD-pin 가드 codify, 약화 0). ADR-039/ADR-073 supersede 아님 (sibling — axis disjoint: branch-create-time pin / cross-repo state assertion / 본 push-time own-branch pre-flight 3축 분리). 약화 방향 (pre-flight 검사 생략 / advisory→silent / opt-in 강제 한계 은폐 / blocking 승격 evidence-gate 우회) 발의 차단."
---

# ADR-135: force-push pre-flight HEAD-pin 가드 (own-branch push-time race-guard)

## 상태

`Proposed` (2026-06-30). Epic CFP-2481 (Epic 병렬 실행 정형화) Phase B 의 E2 (race-guard hardening) carrier. #1027 (`[ESCALATION] force-push pre-flight HEAD-pin gate — ancestry_corruption pattern_count 2 reach`, OPEN P1) 의 ADR + mechanical wire carrier 다. CFP-1103 (force-push pre-flight gate, CLOSED NOT_PLANNED 2026-05-20) body 의 `pre-push-base-advance-check` 제안이 직접 입력.

본 ADR = **정책 정의** SSOT (own-branch push-time pre-flight 의 검사 명제 + 2-layer 분담 + opt-in 강제 한계 정직 기술). enforcement 코드 (hook sample 확장 + CI detect workflow + discriminating test + registry/label entry) = CFP-2490 Phase 2 PR 가 소유.

## 컨텍스트

### 문제 — ancestry corruption (force-push 가 sibling commit 을 덮어씀)

branch-creating / force-push 행위자가 **stale base 위에서 작업·force-push** 해 origin 의 sibling commit 을 ancestry corruption (덮어쓰기) 하는 사고가 2회 발생 (#1027, pattern_count 2 reach — ADR-045 §D-9 Mandatory escalation threshold):

| # | 사례 | 증상 | recovery cost |
|---|---|---|---|
| 1 | CFP-967 Phase 2 | Orchestrator force-push 전 시작 branch 미인지 → empty commit + checkout + force-push → DeveloperPL clean commit overwrite | reflog reset → re-rebase (별 session carry-over) |
| 2 | CFP-991 Phase 2 | force-push 가 Phase 2 production code (orphan commit) 를 design FIX iter chain 으로 overwrite → CodeReviewPL stale state | `git reset --hard origin/main` + cherry-pick orphan + chain 재구성 |

### `--force-with-lease` 의 footgun — base advance 미검사 [verified]

`git push --force-with-lease` 는 **자기 branch 의 remote tip** 이 예상과 같을 때만 force-push (blind `--force` 보다 안전) 하지만, **base branch (main) 의 advance 는 검사하지 않는다**. CFP-1087 cascade race 의 정확한 근본 원인 — force-push 직전 main 이 advance 했어도 `--force-with-lease` 는 통과시킨다.

> 보강 후보: git ≥2.30 의 `--force-if-includes` 는 local tracking ref reachability 를 추가 검사해 "remote 가 fetch 후 advance 했는데 local 이 반영 안 한 채 force-push" 를 차단한다 (`--force-with-lease` 가 못 잡는 race window 의 부분 보완). 단 이는 *자기 branch 의 upstream* reachability 이지 *base(main) advance* 는 여전히 미검사 — 본 ADR 의 pre-flight hook 이 그 base-advance 축을 직접 cover. [verified — git push man page `--force-if-includes` semantics + CFP-1103 body 실측]

### 본질적 마찰 — CI 로 막을 수 없다 [verified]

force-push pre-flight 는 **CI 로 차단 불가** — force-push 가 발생한 시점엔 이미 origin 이 변경된 후라 CI 는 **사후 detect** 만 가능. 진짜 pre-flight 차단은 force-push 실행 *직전* 에 도는 **local pre-push hook** (opt-in) 채널만 가능. opt-in 이므로 강제력이 약하다 — 이것이 #1027 이 2회 재발한 구조적 이유이며, 본 ADR 은 이 한계를 은폐하지 않고 정직히 기술한다 (검사연극 금지, ADR-119).

### disjoint axis 3종 (혼동 차단) [verified]

| 축 | anchor | 시점 | 상태 |
|---|---|---|---|
| spawn-time SHA-anchor | `scripts/lib/check_spawn_prompt_format.py` (ADR-115 / ADR-082 Amd 15 1-E) | subagent spawn prompt emit 직전 | 이미 carry (PreToolUse(Agent) blocking) |
| cross-repo state assertion | ADR-073 §결정 1 본체 | Orchestrator 단정 발화 시점 | 본 ADR 와 disjoint |
| **own-branch push-time pre-flight** | **본 ADR-135** | `git push --force[-with-lease]` 직전 | **한 번도 landed 안 됨** (CFP-1103 NOT_PLANNED) |

> §1 이 인용한 `check_spawn_prompt_head_pin.py` 는 **부재** [verified] — spawn-time 영역은 `check_spawn_prompt_format.py` 가 이미 carry. 과거 `check_spawn_prompt_head_pin.py` (CFP-1489 생성) 는 de-bloat (#2112, label-registry v2.93) 로 제거됨. force-push HEAD-pin 은 이 spawn-time 축과 **별 축** (push-time, own-branch) 이므로 신규 자산을 별 파일로 생성한다.

## 결정

### 결정 1 — own-branch force-push pre-flight 3-check 명제 정의

`git push` (특히 `--force` / `--force-with-lease`) 직전, branch-creating / force-push 행위자는 다음 3-check 를 수행한다 (#1027 root cause 직접 대응):

1. **branch 인지** — `git rev-parse --abbrev-ref HEAD` (현재 branch / detached HEAD / main 직접 push 구분).
2. **base-advance / divergence detect** — `git fetch origin <base>` (best-effort) + `git rev-parse origin/<base>` + `git rev-list --count <branch>..origin/<base>` (BEHIND count) + `git merge-base --is-ancestor` (divergence). `--force-with-lease` 가 못 잡는 base(main) advance 를 여기서 잡는다.
3. **claimed-HEAD reachability** (force-push 시) — `git for-each-ref --contains <local-HEAD>` / upstream tracking ref 비교. self-claim / packet SHA / memory SHA 무조건 신뢰 금지 ([[feedback_verify_pin_head_sha]] 정합).

self-claim / Orchestrator packet-provided SHA / local working dir HEAD / 이전 memory SHA 무조건 신뢰 금지 — ADR-039 §결정 14 (Pre-spawn-pin) 의 push-time analog.

### 결정 2 — 2-layer 채널 분담 (pre-flight 차단 + 사후 detect warning)

| layer | 채널 | 강도 | 자산 |
|---|---|---|---|
| **L1 pre-flight (진짜 차단)** | local `pre-push` git hook (opt-in) | advisory default + `PRE_PUSH_BASE_CHECK` env opt-in blocking abort | 기존 `templates/.claude/hooks/pre-push.sh.sample` (CFP-447) 의 **Step 1 BEHIND-rebase awareness 를 force-push 인지 + base-advance abort 로 확장** |
| **L2 post-hoc (가시화)** | CI workflow (`pull_request`) | warning tier (continue-on-error, required 6-tuple 무등록) | 신규 CI detect workflow (templates/ ↔ .github/ byte-identical) + Python SSOT script + discriminating test |

L1 이 진짜 pre-flight 차단을 담당하나 **opt-in 이라 미설치 환경에서 무력** — 이 한계를 L2 가 사후 가시화로 보완하되, L2 는 force-push 가 *이미 발생한 후* 의 detect 이므로 **차단 불가능** (warning 만). 두 layer 모두 강제력이 구조적으로 제한됨을 정직히 기술한다.

### 결정 3 — 기존 `pre-push.sh.sample` 확장 (신규 경쟁 hook 생성 금지)

git 은 worktree 당 **단일** `.git/hooks/pre-push` 만 실행한다. 기존 자산 = `pre-push.sh.sample` (CFP-447, BEHIND-rebase awareness + atomic invariant advisory) + `pre-push-auto-rebase.sh.sample` (CFP-477, BEHIND abort) 둘 다 동일 `.git/hooks/pre-push` 타겟으로 manual copy 된다 (서로 배타). [verified]

따라서 **신규 별도 pre-push hook sample 을 추가하지 않는다** (단일 hook slot 경쟁 회피). 대신 **기존 `pre-push.sh.sample` (CFP-447) 의 Step 1 (BEHIND-rebase awareness) 을 force-push 인지 + base-advance abort 로 확장**한다 (touchpoint #4 + Codex 지적 정합 — "신규 생성 아닌 기존 BEHIND-rebase awareness 의 force-push 확장"). 확장은 advisory default 보존 + `PRE_PUSH_BASE_CHECK=1` opt-in blocking. 파일명 변경 0.

> #1027 body 의 `pre-push-head-pin.sample` 및 CFP-1103 body 의 `pre-push-base-advance-check.sh.sample` 신규 파일 제안은 **단일 hook slot 경쟁** 문제로 채택하지 않는다 — 기존 `pre-push.sh.sample` 확장이 동일 검사 명제를 충돌 없이 실현한다 (chief author 판단, 두 제안의 *검사 명제* 는 채택 / *신규 파일* 형식만 거부).

### 결정 4 — installer 채널 분리 invariant 보존

`scripts/install-git-hooks.sh` (CFP-428) 는 `templates/.git-hooks/*.sample` 만 symlink 설치한다 — `templates/.claude/hooks/` 는 미접촉 [verified]. `pre-push.sh.sample` 은 `templates/.claude/hooks/` 에 있어 **installer 자동 설치 대상이 아니다** (사용자 manual copy). 본 ADR 은 이 채널 분리를 유지 — pre-push hook 은 manual opt-in copy, installer 자동 등록은 `.git-hooks/` family 만. (자동 force-push 가드 install 격상은 별도 follow-up 후보 — pre-push hook 의 default-on 은 worktree-first 정상 push 마찰 risk 가 있어 본 Story scope 밖.)

### 결정 5 — CI 사후 detect = warning tier 고정 (blocking 승격은 evidence-gated)

L2 CI detect 는 ADR-060 §결정 5 (첫 도입 = warning) 정합 — `continue-on-error: true`, required_status_checks 6-tuple 무등록. blocking 승격은 recurrence-driven (ADR-060 §결정 19) — 별 carrier 가 evidence (실 force-push 사고 재발 + mutation-RED) 후 평가. 본 Story 는 승격하지 않는다.

### 결정 6 — de-bloat 재발 방지 (live workflow + discriminating test 동반 의무)

spawn-prompt-head-pin family 가 theater 로 분류돼 de-bloat (#2112) 제거된 전례 [verified] 를 답습하지 않기 위해, 신규 force-push detect 자산은 **live workflow + detect_command path 실존 + discriminating self-test** 3-종을 동반한다 (CFP-2381 deferred-followup-reconcile gate 통과 조건). declaration-only registry entry 금지.

## 결과

### 긍정

- #1027 (OPEN P1 escalation) 이 ADR + wire carrier 를 획득 — close 경로 확보 (CFP-2490 Phase 2 merge 시).
- own-branch push-time 축이 spawn-time / cross-repo 축과 명시 분리 — 3축 혼동 차단.
- 기존 `pre-push.sh.sample` 확장으로 신규 hook slot 경쟁 0.

### 부정 / 한계 (정직 기술)

- **opt-in 강제 한계**: L1 hook 은 사용자 manual copy 필요 — 미설치 환경에서 무력. server-side (GitHub.com) pre-receive hook 은 미지원 (GitHub Enterprise 만 지원) [hypothesis — 일반 통념, 본 Story 비-load-bearing] 이라 "강제력 있는 force-push 차단" 은 구조적 불가능. 이를 OOS / trade-off 로 명시.
- **L2 는 사후 detect** — 차단 불가, warning 만.
- `--force-if-includes` 보강은 base-advance 를 직접 cover 안 함 (upstream reachability 만) — 본 hook 의 base-advance check 가 주 메커니즘.

### Out-of-scope

- pre-push hook 의 installer 자동 등록 / default-on (별도 follow-up — worktree-first push 마찰 평가 필요).
- blocking tier 승격 (evidence-gated 별 carrier).
- spawn-time SHA-anchor (이미 `check_spawn_prompt_format.py` carry) / cross-repo state assertion (ADR-073 §결정 1).
- parallel-work-sentinel AND-aggregate (ADR-073 Amendment 14) — sentinel single-mode 약점 보완은 본 force-push 축과 disjoint, OOS.

## 관련 파일

- `archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` — §결정 14 Pre-spawn-pin (branch-create-time sibling)
- `archive/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 5 가 CFP-1103 force-push pre-flight 을 sibling 명시
- `templates/.claude/hooks/pre-push.sh.sample` — 확장 대상 (CFP-447, Step 1 BEHIND-rebase awareness → force-push base-advance abort)
- `scripts/install-git-hooks.sh` — installer 채널 분리 (CFP-428, `.git-hooks/` family 만)
- `docs/evidence-checks-registry.yaml` — CI 사후 detect entry (warning tier, Phase 2 wire)
- `docs/inter-plugin-contracts/label-registry-v2.md` — hotfix-bypass:* 신규 family member (v2.100 → v2.101 MINOR)
