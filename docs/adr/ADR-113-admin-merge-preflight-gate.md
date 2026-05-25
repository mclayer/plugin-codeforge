---
adr_number: 113
title: Admin merge pre-flight gate + ACTION_REQUIRED state governance reform
status: Accepted
category: governance
date: 2026-05-25
carrier_story: CFP-1522
parent_epic: CFP-1543
supersedes: null
amends: null
amendments: []
amendment_log: []
is_transitional: false
mechanical_enforcement_actions:
  - admin-merge-preflight-gate
related_adrs:
  - ADR-024  # enforce_admins source + hotfix-bypass channel SSOT + Amendment 6/8 §결정 6.A bypass-as-norm-mutation chain
  - ADR-040  # Amendment 3 §결정 7.D mechanical_enforcement_actions[] frontmatter 의무 (self-application 정합)
  - ADR-045  # §D-9 cross-Story pattern_count ≥ 2 mandatory ADR escalation (본 ADR = pattern_count 3 reach 산물)
  - ADR-058  # §결정 5/7 sunset criteria + 보안 ADR default presumption false
  - ADR-060  # evidence-checks-registry 4-tier framework + warning 첫 entry
  - ADR-066  # PAT 90d rotation invariant — admin-merge 및 branch protection PATCH 는 session admin auth disjoint axis (ADR-066 §결정 2 6-scope set 안 admin:* literal 부재, cross-ref only)
  - ADR-073  # §결정 1 verify-before-assert transition trigger directly-analogous primitive (lane_spawn / pr_open / merge_transition / worktree_lane_spawn / fix_iter_start / sibling_story_handoff / stale_local_main_checkout / mcp_token_expired_mid_flight / label_change 9 trigger 답습)
  - ADR-082  # write-time self-write verification mandate + §결정 6 declaration-only-Wave-1 retain pattern
  - ADR-087  # deploy-lane-presence Phase 2 carrier (CLAUDE.md L304/L306 drift origin — declaration-only Wave 1)
related_files:
  - CLAUDE.md                                                # 본 ADR cross-ref + L304/L306 drift 정정 (4 required check 현 main state)
  - docs/orchestrator-playbook.md                            # §3.19 신설 (Admin merge pre-flight gate procedure)
  - docs/evidence-checks-registry.yaml                       # admin-merge-preflight-gate entry append (warning-tier deferred-followup)
  - docs/inter-plugin-contracts/label-registry-v2.md         # hotfix-bypass:admin-merge-preflight-gate 95번째 family member + v2.69 → v2.70 MINOR bump
  - docs/inter-plugin-contracts/MANIFEST.yaml                # label-registry-v2 row v2.69 → v2.70 ratchet
  - docs/parallel-work/section-ownership.yaml                # admin-merge-preflight-gate section ownership row append
---

# ADR-113 — Admin merge pre-flight gate + ACTION_REQUIRED state governance reform

## 상태

Accepted (2026-05-25 KST) — CFP-1522 carrier_story, parent Epic CFP-1543. ADR-045 §D-9 cross-Story pattern_count 3 super-class (`admin_merge_action_required_force_attempt`) reach Mandatory ADR escalation 산물. ADR-073 §결정 1 verify-before-assert transition trigger directly-analogous primitive 의 admin-merge attempt 시점 sub-domain instantiation. declaration-only Wave 1 (ADR-082 §결정 6 retain pattern, ADR-070 §D5 retain, ADR-086 self-application 정합).

## 컨텍스트

### 3-incident pattern_count 3 reach super-class

본 ADR 은 `admin_merge_action_required_force_attempt` super-class 의 cross-Story 3 incident 누적 → ADR-045 §D-9 Mandatory escalation 자동 발동 산물.

| # | CFP | 시점 (KST) | 증상 |
|---|---|---|---|
| 1 | CFP-1334 retro | 2026-05-22 | `gh pr merge --admin` 시도 시 `pending checks` ACTION_REQUIRED 상태에서 force-merge attempt → required check 0 status 가 silent admin override 됨, post-merge phase-gate-mergeable workflow re-trigger 부재 |
| 2 | CFP-1318 retro | 2026-05-23 | phase-gate-mergeable workflow_dispatch entry 부재로 admin merge 후 stale state 잔존 (no re-trigger mechanism), Issue #1326 audit trail 안 "missing required check phantom" 명시 |
| 3 | CFP-1495 PR #1505 close | 2026-05-25 | 8 file Phase 1 산출물 (Confluence drift detection cron, codeforge-pmo) carrier 영역 admin-merge 시도 중 ACTION_REQUIRED 잔존 detect 후 PR 자체 close (산출물 evacuate, headRefOid `13b958eb` 보존) — `CFP-1495 carrier` 영역 본 ADR merge 후 recovery procedure (§7.4.1 DR) 활성 |

3-factor compound (Researcher hypothesis): (a) `enforce_admins: true` 가 ratchet 강화 방향 정합이지만 (b) `gh pr merge --admin` CLI 가 required check 0 status 의 silent override path 를 노출 (admin 권한 inherent) + (c) `phase-gate-mergeable.yml` workflow `workflow_dispatch` entry 부재 → manual re-trigger 불가. 본 3-factor compound = admin merge attempt 시점 procedural governance gap (gate 자체는 enforce_admins 로 강화되었으나 attempt-time verify procedure 부재).

### Researcher hypothesis enum (3 incident root cause)

- (a) Orchestrator inline whitelist 4-entry (ADR-039 §결정 2) 중 4번째 entry "Status report" path 안 `gh pr merge --admin` 호출이 verify-before-trust 의무 (ADR-073 §결정 1) 영역 외 → admin merge attempt 시점 mechanical pre-flight gate 부재
- (b) `phase-gate-mergeable.yml` `on:` block = `pull_request: [opened, synchronize, labeled, unlabeled, edited]` only, `workflow_dispatch` entry 0 → required check ACTION_REQUIRED 잔존 시 manual re-trigger 경로 부재 (verified ground truth, 535 lines workflow file `on:` block grep direct)
- (c) `hotfix-bypass:*` channel family 가 lint skip 영역 cover 하나, `gh pr merge --admin` CLI silent override path 영역 = label family 미cover (별 sub-domain)
- (d) `enforce_admins: true` invariant 가 branch protection rule layer 강제하나, `gh api -X PATCH /repos/.../branches/main/protection` 호출 자체에 explicit forbid 영역 0 (Threat B: branch protection toggle abuse 우회 attack surface)
- (e) Wave 4 brainstorm carrier 영역 (별 CFP 후속) — `phase-gate-mergeable.yml` `workflow_dispatch` entry 보완 검토 (현 ADR-113 scope 외, follow-on carrier)

### Decision principle anchor (ADR-064 §결정 1-7 정합)

본 ADR = **broad coverage** (3 incident side effect / failure mode enum / Authn/Authz boundary 포함) + **best-effort** (current evidence-grounded 도달 가능한 최선의 안) + **active amendment** (ratchet 강화 방향, ADR-058 §결정 7 보안 ADR default presumption false 정합 — `is_transitional: false` permanent governance ratchet).

## 결정

### 결정 1 — Pre-flight gate 5-step procedure mandate

Orchestrator 가 `gh pr merge --admin <PR-N>` attempt 시점 직전 5-step pre-flight gate 의무.

**Step 1 — required check state enum fetch (verify-before-trust ADR-073 §결정 1 primitive)**

```
gh pr checks <PR-N> --json name,state,conclusion --jq '.[] | select(.state != "completed" or .conclusion != "success") | "\(.name): \(.state)/\(.conclusion)"'
```

출력 list 가 비어있으면 (모든 required check `state=completed AND conclusion=success`) → admin merge 진행. 비어있지 않으면 → Step 2.

**Step 2 — ACTION_REQUIRED detection + abort**

Step 1 출력에서 1+ check 의 `state` 가 다음 enum 영역에 속하면 abort:

```yaml
abort_states_enum:  # closed-set, open_extension: false
  - action_required        # primary block — manual approval needed
  - failure                # explicit fail (Step 1 select 영역)
  - cancelled              # workflow cancelled, indeterminate state
  - timed_out              # CI timeout, retry candidate
  - stale                  # stale check, fresh commit re-trigger needed
  - pending                # in-progress, retry-wait
  - in_progress            # in-progress alias
  - skipped                # workflow conditional skip, fresh trigger candidate
  - neutral                # neutral state (e.g., codecov soft pass), Orchestrator manual judgment
  - unknown                # fail-closed semantic — admin merge 차단
```

unknown value (closed-set enum 외) = **fail-closed** (admin merge 차단, 사용자 escalation).

abort 시 `gh pr merge --admin` 호출 금지 + Step 3 진입.

**Step 3 — fresh commit trigger recovery**

ACTION_REQUIRED 잔존 시 fresh commit (empty commit 또는 trailing whitespace amendment commit) 으로 workflow re-trigger:

```bash
git -C "<worktree_abs_path>" commit --allow-empty -m "[CFP-NNN] re-trigger required checks (admin-merge preflight Step 3)"
git -C "<worktree_abs_path>" push origin <branch>
```

`workflow_dispatch` entry 부재 영역 fallback (`phase-gate-mergeable.yml` 영역 verified). Wave 4 brainstorm carrier (별 follow-on CFP) = `workflow_dispatch` entry 보완 검토 영역 (§결정 8 sibling).

**Step 4 — re-verify (≤ 60s wait + re-fetch)**

```bash
sleep 60   # workflow propagation grace (CI dispatch latency typical 30-60s, Anthropic infra-independent)
gh pr checks <PR-N> --json name,state,conclusion --jq '.[] | select(.state != "completed" or .conclusion != "success")'
```

empty output → admin merge 진행. non-empty → Step 5 (attempt cap check).

**Step 5 — attempt cap = 3 STOP + escalate**

Step 1-4 cycle 의 attempt count 가 **3 회** reach 시 STOP + 사용자 escalation 의무. Workflow log direct verify:

```bash
gh run list --workflow="phase-gate-mergeable.yml" --branch=<branch> --limit 10 --json databaseId,conclusion,createdAt
gh run view <latest-id> --log
```

워크플로 self-error (workflow code bug / dependency outage) 추정 시 사용자 escalation. `auto-retry` 무한 loop 차단 (Threat A: counter reset abuse mitigation, §결정 2 cross-ref).

### 결정 2 — Attempt cap = 3 dual scope (per-PR AND per-Story)

Threat A (counter reset abuse — close+reopen / PR 재생성 / attempt 분산) 차단:

- **per-PR scope**: 동일 PR-N 안 `gh pr merge --admin` 시도 누적 ≥ 3 → STOP
- **per-Story scope**: 동일 carrier_story (CFP-NNN) 안 모든 PR 의 admin-merge 시도 누적 ≥ 3 → STOP (close+reopen / PR 재생성 우회 차단)

**dual carrier 조건**: 둘 중 1+ trigger 시 STOP + 사용자 escalation 의무. counter reset abuse mitigation.

**counter telemetry**: Story §14 Lane Evidence 안 `admin_merge_attempts` optional field (per-Story aggregate) + PR description 안 `admin-merge attempts: N/3` declaration optional. PMOAgent retro corpus enumeration (ADR-045 §D-9) 가 cross-Story pattern_count tally — 본 ADR pattern_count 3 reach 자체가 sentinel.

### 결정 3 — Branch protection rule change explicit forbid

Threat B (enforce_admins toggle abuse — `gh api -X PATCH /repos/<org>/<repo>/branches/main/protection` 으로 `enforce_admins.enabled: false` toggle 우회 attack) mitigation:

- `gh api -X PATCH /repos/<org>/<repo>/branches/main/protection*` 또는 동등 호출 = **explicit forbid** (Orchestrator inline whitelist 영역 외, subagent 영역 모두 영역 외)
- branch protection rule change 의무 시점 = `hotfix-bypass:*` label family 의 audit-trailed exception channel **외** 영역 (별 ADR — 향후 branch protection rule mutation 의무 carrier CFP 발의 시 별 ADR codify 의무)
- ADR-024 §결정 6.A bypass-as-norm-mutation 차단 chain (Amendment 6 §결정 6.A.2 + Amendment 8 §결정 6.A.3/6.A.4/6.A.5) 의 5 lint chain 자동 covered (별 lint 신설 0)

**ADR-066 cross-ref**: branch protection rule PATCH 권한 = session-level admin authentication (`gh auth login` interactive 또는 admin session token, repo admin role) — ADR-066 §결정 2 CODEFORGE_CROSS_REPO_PAT 6-scope set (CI/automation rotation policy) 와 disjoint axis. 본 §결정 3 = 권한 보유 형태와 무관한 procedure-level forbid (session admin auth revoke 영역 외, behavioral directive only).

### 결정 4 — 5 lint chain 자동 covered (bypass-as-norm-mutation 차단)

`hotfix-bypass:admin-merge-preflight-gate` label family member 의 bypass-as-norm-mutation 차단 mechanism = ADR-024 Amendment 6/8 §결정 6.A 5 lint chain 자동 covered:

| Lint | ADR ref | 영역 |
|---|---|---|
| `bypass-label-counter` | ADR-024 Amendment 6 §결정 6.A.2 | per-entry namespace 누적 사용 카운터 |
| `per-plugin-cumulative-counter` | ADR-024 Amendment 8 §결정 6.A.3 | per-plugin scope 누적 (codeforge wrapper-self) |
| `bypass-justification-marker` | ADR-024 Amendment 8 §결정 6.A.4 | `[bypass-justification]` PR comment marker grep-presence |
| `cross-repo-bypass-counter` | ADR-024 Amendment 8 §결정 6.A.5 | cross-repo 3-repo signature 누적 |
| `check-bypass-audit-comment.sh` | ADR-060 framework | bypass audit comment 자동 발의 |

**별 lint 신설 0건** — 본 ADR family member 추가 만으로 5 lint chain inherit. ADR-040 Amendment 3 §결정 7.D self-application precedent 답습.

### 결정 5 — Failure mode enum 4-fail + fail-closed semantic

admin-merge pre-flight gate 의 failure mode closed-enum:

- **fail-1 API call failure** — network failure / token expiry / Anthropic infra 429 → retry exp-backoff 3회 + `codeforge:rate-limit-429-mitigation` skill cross-ref + ADR-066 PAT 만료 check (90d rotation invariant)
- **fail-2 state enum unknown** — `gh pr checks` 반환 state value 가 §결정 1 abort_states_enum closed-set 외 → **fail-closed semantic** (admin merge 차단 + 사용자 escalation, 10-value enum invariant 보존)
- **fail-3 re-trigger 후 ACTION_REQUIRED 잔존** — Step 3 fresh commit trigger 후 Step 4 re-verify 에서 동일 ACTION_REQUIRED 잔존 → workflow self-error 추정 → attempt cap 카운트 + Step 5 STOP escalation
- **fail-4 silent bypass attempt** — Orchestrator 또는 subagent 가 §결정 1 5-step procedure skip + `gh pr merge --admin` 직접 호출 → §결정 4 5 lint chain 자동 covered (별 mechanism 0)

10-value `abort_states_enum` closed-set + `unknown` fail-closed 영역 정합. 본 enum extension 시 ADR Amendment 의무 (ADR-082 closed-set ratchet 정합, open_extension: false).

### 결정 6 — Authn/Authz cross-ref (ADR-066 90d rotation invariant)

본 ADR 영역 권한 mapping:

| Action | Required scope | ADR ref |
|---|---|---|
| `gh pr merge --admin` | `repo` (write 권한) — admin override = `enforce_admins: true` bypass 용 session-level admin authentication (interactive `gh auth login` 또는 admin session token, ADR-066 CODEFORGE_CROSS_REPO_PAT SSOT 외 영역) | ADR-066 §결정 2 6-scope set 와 disjoint axis (session admin auth vs CI token rotation policy) |
| `gh pr checks` (read) | `repo` + `checks:read` | ADR-066 single PAT reuse 가능 (low risk read-only) |
| `hotfix-bypass:*` label attach | label.write (codeforge-pmo owner + Orchestrator self-attach) | ADR-024 §결정 6.A |
| `gh api -X PATCH .../branches/main/protection` | admin session authentication (repo admin role) — ADR-066 CI PAT SSOT 외 영역 (session admin auth axis) | **§결정 3 explicit forbid** (procedural, 권한 보유 시에도 호출 금지) |

ADR-066 §결정 2 PAT scope minimum 6-scope set (`repo:read` / `repo:write` / `metadata:read` / `marketplace contents:read` / `reconcile-target-repos contents:write+pull_requests:write` / `cross-repo-target-repos issues:write`) = CI/automation token rotation policy 영역 SSOT — admin-merge 및 branch protection PATCH 는 session-level admin authentication 영역으로 **disjoint axis** (CI PAT scope 안 `admin:*` literal 부재 verified). 본 ADR 영역의 admin override 권한은 PAT scope 확장이 아닌 session admin auth 경유 — ADR-066 rotation invariant (90d / max 180d) 와 boundary 분리. cross-ref only.

### 결정 7 — §7.4.1 DR (CFP-1495 carrier 재진입 path)

CFP-1495 PR #1505 close evacuation (산출 8 file headRefOid `13b958eb` 보존) recovery procedure:

```bash
git -C "<new-worktree>" fetch origin 13b958eb
git -C "<new-worktree>" checkout -b cfp-1495-redo origin/main
git -C "<new-worktree>" cherry-pick 13b958eb
git -C "<new-worktree>" push -u origin cfp-1495-redo
gh pr create --title "[CFP-1495] Confluence drift detection cron — REDO" --body "Recovery from closed PR #1505 (headRefOid 13b958eb). post-CFP-1522 ADR-113 admin-merge pre-flight gate active 후 재진입."
```

branch naming `cfp-1495-redo` 권장 (ADR-024 cfp-NNN 정합, 간결 — `cfp-1495` 동일 branch 재사용 시 origin ref dangle 위험). post-CFP-1522 merge 후 활성.

### 결정 8 — Wave 2+ deferred-followup carrier 분리 (ADR-064 §결정 5 unitary 정합)

본 ADR scope = Wave 1 declarative anchor (5-step procedure + attempt cap + branch protection forbid + DR recovery). 후속 carrier 영역 분리:

| Wave | carrier 영역 | 후속 CFP (TBD) |
|---|---|---|
| **Wave 2** | mechanical wire — `scripts/check-admin-merge-preflight.sh` (3-layer self-block: pre-commit hook + pre-push hook + Orchestrator self-instrumentation) | 별 sub-Story carrier (CFP-TBD-Wave2) |
| **Wave 3** | Codex worker fail mode enum 9번째 entry (`admin_merge_preflight_skip`) + ADR-070 §결정 D1 sub-class | 별 carrier (Codex collaboration governance scope) |
| **Wave 4** | `phase-gate-mergeable.yml` `workflow_dispatch` entry 보완 + manual re-trigger 경로 codify | 별 brainstorm carrier (Researcher hypothesis (e) follow-on) |
| **별** | ADR-RESERVATION row 107-112 backfill (registry row gap 영역) | 별 follow-up CFP carrier (chief author scope 외 — ADR-064 §결정 5 unitary 정합) |

ADR-082 §결정 6 retain pattern (declaration-only-Wave-1) + ADR-086 self-application 정합.

## 결과

본 ADR 의 expected outcome / governance impact / measurable effect:

- **`admin_merge_action_required_force_attempt` super-class mitigation**: 3-incident pattern_count 3 reach (CFP-1334 / CFP-1318 / CFP-1495) 의 procedural governance gap closure — admin-merge attempt 시점 5-step pre-flight gate 가 ACTION_REQUIRED silent override path 차단.
- **Threat A counter reset abuse mitigation**: attempt cap=3 dual scope (per-PR AND per-Story) 가 close+reopen / PR 재생성 / attempt 분산 우회 경로 차단 — counter telemetry `admin_merge_attempts` optional field (Story §14 Lane Evidence) 가 PMOAgent retro corpus enumeration (ADR-045 §D-9) cross-Story pattern_count tally evidence base.
- **Threat B branch protection toggle abuse mitigation**: `gh api -X PATCH .../branches/main/protection` explicit forbid 가 `enforce_admins.enabled: false` toggle 우회 attack surface 차단 (procedural directive, session admin auth 권한 보유 시에도 호출 금지).
- **5 lint chain auto-inherit (별 mechanism 0)**: ADR-024 Amendment 6/8 §결정 6.A 의 bypass-as-norm-mutation 차단 5 lint chain (`bypass-label-counter` / `per-plugin-cumulative-counter` / `bypass-justification-marker` / `cross-repo-bypass-counter` / `check-bypass-audit-comment.sh`) 자동 covered — 별 lint 신설 0건.
- **declaration-only Wave 1 mechanical wire deferred-followup**: `mechanical_enforcement_actions: [admin-merge-preflight-gate]` frontmatter (ADR-040 Amendment 3 §결정 7.D self-application 정합) → Wave 2 별 sub-CFP carrier 가 `scripts/check-admin-merge-preflight.sh` 3-layer wire (pre-commit hook + pre-push hook + Orchestrator self-instrumentation) 산출.

## 관련 파일

frontmatter `related_files` 의 narrative companion (markdown link 형식):

- [CLAUDE.md](../../CLAUDE.md) — 본 ADR cross-ref + L304/L306 drift 정정 (4 required check 현 main state, deploy-lane-presence Phase 2 carrier 미배포 명문화)
- [docs/orchestrator-playbook.md §3.19](../orchestrator-playbook.md) — Admin merge pre-flight gate procedure 신설 (5-step procedure + attempt cap + DR recovery)
- [docs/evidence-checks-registry.yaml](../evidence-checks-registry.yaml) — `admin-merge-preflight-gate` entry append (warning-tier deferred-followup, ADR-060 framework 정합)
- [docs/inter-plugin-contracts/label-registry-v2.md](../inter-plugin-contracts/label-registry-v2.md) — `hotfix-bypass:admin-merge-preflight-gate` 95번째 family member 신설 + v2.69 → v2.70 MINOR bump
- [docs/inter-plugin-contracts/MANIFEST.yaml](../inter-plugin-contracts/MANIFEST.yaml) — label-registry-v2 row v2.69 → v2.70 ratchet (kind:registry, sibling sync 면제 ADR-010 §결정 2)
- [docs/parallel-work/section-ownership.yaml](../parallel-work/section-ownership.yaml) — `admin-merge-preflight-gate` section ownership row append (parallel epic conflict 차단 ADR-050 정합)

## 해소 기준

N/A — permanent governance ratchet (ADR-058 §결정 7 보안 ADR default presumption false 정합, 약화 0건 invariant — `is_transitional: false`).

본 ADR = 강화 방향 only (admin-merge attempt 시점 procedural governance gap closure). ADR-058 §결정 5 sunset_justification 면제 (강화 방향 evidence-gate 통과, ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — pattern_count 3 reach Mandatory escalation 산물).

## 후속 작업

| 우선순위 | 작업 | 영역 |
|---|---|---|
| Wave 2 | `scripts/check-admin-merge-preflight.sh` 3-layer mechanical wire (pre-commit / pre-push / Orchestrator instrumentation) | 별 sub-Story carrier |
| Wave 3 | Codex worker fail mode enum 9번째 entry + ADR-070 §결정 D1 sub-class instantiation | 별 carrier (Codex governance) |
| Wave 4 | `phase-gate-mergeable.yml` `workflow_dispatch` entry 보완 검토 (Researcher hypothesis (e)) | 별 brainstorm carrier |
| 즉시 | CFP-1495 carrier 재진입 (§결정 7 DR procedure 활성) | post-CFP-1522 merge 직후 |
| 별 | ADR-RESERVATION row 107-112 backfill (registry row gap 영역, chief author scope 외) | 별 follow-up CFP |

## Amendments

(amendment 0 — 본 ADR 신설, 별 Amendment 없음.)

## Cross-reference

- **directly-analogous primitive**: [ADR-073 §결정 1](ADR-073-orchestrator-verify-before-assert.md) — transition trigger enum 9종 (lane_spawn / pr_open / merge_transition / worktree_lane_spawn / fix_iter_start / sibling_story_handoff / stale_local_main_checkout / mcp_token_expired_mid_flight / label_change) 답습 (admin_merge_attempt 시점 sub-domain instantiate)
- **declaration-only-Wave-1 retain pattern**: [ADR-082 §결정 6](ADR-082-write-time-self-write-verification-mandate.md) + [ADR-070 §D5](ADR-070-codex-verify-before-trust.md)
- **§D-9 forcing function**: [ADR-045 §D-9](ADR-045-story-retro-mandatory-trigger.md) — pattern_count 3 reach Mandatory escalation 산물
- **bypass channel 5 lint chain**: [ADR-024 Amendment 6 §결정 6.A.2 + Amendment 8 §결정 6.A.3/6.A.4/6.A.5](ADR-024-story-scoped-branch-policy.md)
- **evidence-checks-registry framework**: [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — 4-tier (warning / blocking-on-pr / blocking-on-merge / hotfix-bypass)
- **deploy-lane-presence Phase 2 drift origin**: [ADR-087](ADR-087-deploy-lane-and-lifecycle-extension.md) — CLAUDE.md L304/L306 drift 정정 cross-ref (현 main branch protection contexts = 4, 5번째 deploy-lane-presence Phase 2 wire 시점 ratchet)
- **mechanical_enforcement_actions[] frontmatter**: [ADR-040 Amendment 3 §결정 7.D](ADR-040-worktree-convention.md) — self-application 정합
- **sunset_justification**: [ADR-058 §결정 5/7](ADR-058-adr-sunset-criteria-mandate.md) — `is_transitional: false` permanent (보안 ADR default presumption false 정합)
