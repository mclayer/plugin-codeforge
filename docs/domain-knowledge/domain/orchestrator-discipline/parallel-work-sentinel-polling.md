---
kind: domain_fact
type: domain-knowledge
area: orchestrator-discipline
topic_slug: parallel-work-sentinel-polling
title: "Parallel work sentinel polling — title-based search + Epic state poll + HEAD compare"
status: Active
tags:
  - parallel-work
  - sentinel
  - polling
  - transition-trigger
  - session-start
  - verify-before-trust
  - cfp-953
  - cfp-946
domain: orchestrator-discipline
owner_adr: ADR-073-Amendment-2
sibling_cfp:
  - CFP-953  # first incident — label-based search miss (2026-05-18 KST)
  - CFP-946  # second incident — 11분 gap Epic close miss (2026-05-18 KST same day)
  - CFP-967  # sibling Story-2 mechanical wire (script + hook + workflow + bats)
related_adrs:
  - ADR-073  # carrier — Amendment 2 §결정 1-A/1-B/1-C declarative anchor
  - ADR-070  # 자매 layer 2 — Codex verify-before-trust (외부 worker output)
  - ADR-082  # disjoint super-class (internal lane agent self-write verify)
  - ADR-045  # 자매 layer 4 — PMOAgent retro corpus enumeration (§D-9)
  - ADR-060  # evidence-enforceable warning-tier framework
  - ADR-058  # ADR sunset criteria — Amendment 2 ratchet 강화 방향 정합
  - ADR-064  # decision principle — top-down ratchet self-application
  - ADR-040  # mechanical_enforcement_actions[] 첫 entry 부착 (Amendment 3 §결정 7.D)
related_stories:
  - CFP-966  # Story-1 declarative anchor (본 narrative SSOT carrier)
  - CFP-967  # Story-2 mechanical wire (sibling, sequential)
created: 2026-05-18
updated: 2026-05-18
---

# Parallel work sentinel polling

## What

Orchestrator 가 long-running session 안에서 **mid-flight parallel race incidence** 를 차단하는 sustained polling discipline. 3 trigger source 의 closed-set enum + cold start session_start 보강 + HEAD compare pattern 으로 구성:

### Transition trigger 3종 (closed enum)

| ID | Transition trigger | 발화 시점 | Polling 의무 3-step |
|----|---|---|---|
| `lane_spawn` | lane 진입 직전 (Requirements / Design / DesignReview / Develop / CodeReview / SecurityTest / IntegrationTest / PMO retro lane spawn) | Agent tool spawn 직전 | (1) Issue body / current CFP context title-based search → (2) open Epic state poll → (3) HEAD compare sibling commits |
| `pr_open` | PR open 직전 (Phase 1 / Phase 2 / retro PR) | `gh pr create` 직전 | 동일 3-step + sibling Story PR list cross-ref |
| `merge_transition` | PR merge 직전 + 직후 (gate label / phase label transition) | `gh pr merge` 직전 + 직후 transition action 직전 | 동일 3-step + Epic state final poll (close eligibility check) |

### Cold start session_start 보강

기존 SessionStart hook tier (TodoWrite preload pattern, ADR-038 Amendment 2 §결정 9) 가 turn 0 prompt-injection 단독 layer — mid-flight parallel race incidence 차단 영역은 cover 부족. 본 polling discipline 의 cold start anchor 는 SessionStart hook tier 의 4번째 가상 trigger entry (session 첫 turn additionalContext 안 active CFP context list + open Epic state list + current branch HEAD vs origin/main delta 3-item preload 의무).

### HEAD compare pattern (3-step verify-before-trust)

```bash
# Step 1 — title-based search (memory rule 6 의무, CFP-953 incident carrier)
gh issue list --search "<keyword>" --state all --json number,title,labels,closedAt
# Note: label-based search 만 (rule 6 위반) → CFP-953 incident reproduction risk

# Step 2 — Epic state poll (memory rule 7 의무, CFP-946 incident carrier)
gh issue view <epic_number> --json state,closedAt,closedBy,labels
# Note: polling 직전 5+ min 경과 session state cache 무조건 stale 가정

# Step 3 — HEAD compare sibling commits (verify-before-trust 4-layer governance Layer 1)
PRIOR_HEAD=$(cat .claude-work/progress/<KEY>.md | grep pinned_head)  # session state cache (stale 가능)
CURRENT_HEAD=$(git ls-remote origin <branch> | cut -f1)              # direct verify
gh api repos/{owner}/{repo}/compare/${PRIOR_HEAD}...${CURRENT_HEAD} \
  --jq '.commits[].sha'  # parallel commits enumeration (mid-flight race 차단)
```

## Why

memory rule 6 (title-based search 의무) + rule 7 (Epic 진행 중 polling 의무) 가 normative-only directive layer 만 cover — wrapper-local + consumer 비전파 + single-session scope = structural enforcement 부재. mechanical enforcement carrier 가 부재한 동안 same-day 2/2 parallel race incidents 발생 (2026-05-18 KST sentinel):

- **CFP-953** (first incident): label-based search (`gh issue list --label parent:CFP-882`) 만 수행 → CFP-932 (실제 Wave 4 Story-2 carrier, label `parent:CFP-699` 만 부착) miss → #953 brainstorm Phase 0/2 + spec PR #624 진행 후 발견 → #953 closed not_planned + spec deprecation PR #625. memory rule 6 신설 carrier (title-based search 의무).
- **CFP-946** (second incident, same day, 11분 gap): Epic CFP-946 brainstorm + Story-A (#957) PR #961 merged `06:42:12Z` → 11분 후 parallel session PR #962 `[CFP-946 option 1]` merged `06:53:30Z` "Closes #946" → Epic #946 CLOSED. Story-B (#958) ArchitectPL spawn 직전 HEAD re-pin 시 #962 검출. Story-B scope 분할 (declaration absorbed by #962 + mechanical layer carry-forward = #963 P2). memory rule 7 신설 carrier (Epic 진행 중 polling 의무).

본 polling discipline 의 ADR-073 Amendment 2 declarative anchor + sibling Story-2 (CFP-967) mechanical wire 가 normative-only → mechanical 전환의 carrier.

## How

본 polling discipline 의 5 SSOT file 영역 mapping:

| Layer | File | Status | Carrier |
|---|---|---|---|
| **ADR Amendment** | `docs/adr/ADR-073-orchestrator-verify-before-assert.md` Amendment 2 | declarative anchor (본 Story-1) | CFP-966 (Story-1) |
| **Evidence registry row** | `docs/evidence-checks-registry.yaml` `parallel-work-sentinel-pickup` entry | declaration-only-Wave-1 status (warning tier) | CFP-966 (Story-1) |
| **Narrative SSOT** | `docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md` (본 file) | declarative anchor (본 Story-1) | CFP-966 (Story-1) |
| **Cross-ref anchor** | `CLAUDE.md` + `docs/orchestrator-playbook.md` §3.5 | declarative anchor (본 Story-1) | CFP-966 (Story-1) |
| **Mechanical wire** | `scripts/check-parallel-work-sentinel.{sh,py}` + `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` + `templates/github-workflows/parallel-work-sentinel-check.yml` + `tests/bats/test_parallel_work_sentinel.bats` | (deferred) | CFP-967 (Story-2 sibling, sequential) |

### Memory rule 6 + 7 mechanical binding cross-ref

| Memory rule | Mechanical enforcement binding | Sibling Story |
|---|---|---|
| **Rule 6** (title-based search 의무, CFP-953 carrier) | ADR-073 Amendment 2 §결정 1-A `lane_spawn` trigger Step 1 + `parallel-work-sentinel-pickup` evidence-checks-registry entry (warning tier first, recurrence-aware promotion) | CFP-967 (Story-2 mechanical wire — script + workflow) |
| **Rule 7** (Epic 진행 중 polling 의무, CFP-946 carrier) | 동일 (ADR-073 Amendment 2 + `parallel-work-sentinel-pickup` registry entry). Transition trigger 3종 = `lane_spawn` / `pr_open` / `merge_transition` | CFP-967 (Story-2 동일) |

## Sentinel evidence accumulation pattern

2026-05-18 KST same-day 2-occurrence sentinel batch:

### CFP-953 — First parallel race (2026-05-18 KST)

- **Trigger**: Epic CFP-882 Wave 4 sub-Epic Story-2 진행 의도 + label-based search (`gh issue list --label parent:CFP-882`) 만 수행
- **Miss source**: CFP-932 (실제 Wave 4 Story-2 carrier) 가 label `parent:CFP-699` 만 부착 (label drift — Wave 4 sub-Epic relabel 동반 없이 CFP-932 가 Story-2 carrier 로 reassign 되었음)
- **Discovery moment**: #953 brainstorm Phase 0/2 완료 + spec PR #624 진행 후 발견
- **Mitigation**: #953 CLOSED not_planned / #954 cross-ref 정정 / orphan spec deprecation PR #625 / **memory rule 6 신설** (title-based search 의무)
- **Lesson**: label drift 영역 = title-based search 가 catch 가능 (`gh issue list --search "channel runtime"` → CFP-932 hit 가능)

### CFP-946 — Second parallel race (2026-05-18 KST, 11분 gap)

- **Trigger**: Epic CFP-946 brainstorm Phase 0/2 + Story-A (#957) ArchitectAgent normative author 진행
- **Story-A merge**: PR #961 MERGED `2026-05-18T06:42:12Z`
- **Gap**: 11분
- **Parallel session collision**: PR #962 `[CFP-946 option 1] ADR-081 Amd 3 sandbox_network_required toggle` MERGED `2026-05-18T06:53:30Z` "Closes #946." → Epic #946 CLOSED
- **Discovery moment**: Story-B (#958) ArchitectPL spawn 직전 HEAD re-pin 시 #962 검출
- **Mitigation**: Story-B scope 분할 (declaration absorbed by #962 + mechanical layer carry-forward = #963 P2 follow-up CFP) / **memory rule 7 신설** (Epic 진행 중 polling 의무)
- **Lesson**: Epic 진행 중 lane transition (lane spawn + PR open + merge transition) 매 직전 HEAD re-pin + Epic state poll 의무

### Sentinel pattern summary

| Incident | Date | Gap | Detection layer (post-event) | Mitigation carrier |
|---|---|---|---|---|
| CFP-953 (first) | 2026-05-18 KST | n/a | title-based search retroactive | memory rule 6 + ADR-073 Amendment 2 §결정 1-A Step 1 |
| CFP-946 (second) | 2026-05-18 KST | 11분 from previous | HEAD re-pin at lane transition | memory rule 7 + ADR-073 Amendment 2 §결정 1-A Step 3 |

**Recurrence count = 2** (same-day batch). evidence-checks-registry entry `parallel-work-sentinel-pickup` 의 `recurrence.count: 2` + `recurrence.threshold: 3` declare — 3번째 incident 발생 시 `promotion_trigger: auto_blocking` 자동 발화 (ADR-060 §결정 19 Amendment 6 / schema v1.2 정합).

## Escalation matrix

| Tier | Trigger condition | Action |
|---|---|---|
| **warning** (current) | recurrence.count < 3 (현재 = 2) | `current_tier: warning` 유지 — declaration-only-Wave-1 status (CFP-966 Story-1 declarative anchor merged + CFP-967 Story-2 mechanical wire pending) |
| **warning → blocking-on-pr 자동 승격** | recurrence.count ≥ 3 (3rd incident 발생 시) | `promotion_trigger: auto_blocking` 자동 발화 — 별 carrier CFP 가 `current_tier: warning → blocking-on-pr` MINOR amendment 발의 (ADR-060 §결정 6 AND condition + recurrence-driven promotion) |
| **blocking-on-pr → blocking-on-merge** | post-`blocking-on-pr` PR 누적 ≥ 20 + bypass 외 failure = 0 + 후속 incident 0 | post-CFP-967 follow-up CFP (Wave 2 ratchet) |

### Carrier Story sequence

```
CFP-966 (본 Story-1 — declarative anchor)
  ↓ sequential dependency
CFP-967 (Story-2 — mechanical wire: script + hook + workflow + bats)
  ↓ recurrence.count ≥ 3 도달 시 auto-firing
post-CFP-967 follow-up CFP (Wave 2 — warning → blocking-on-pr 승격)
  ↓ blocking-on-pr 후 PR 누적 ≥ 20 + 0 failure 도달 시
Wave 3 follow-up CFP (blocking-on-pr → blocking-on-merge 승격)
```

## See also

- **ADR-073 Amendment 2** ([`docs/adr/ADR-073-orchestrator-verify-before-assert.md`](../../../adr/ADR-073-orchestrator-verify-before-assert.md)) — declarative anchor carrier (§결정 1-A/1-B/1-C)
- **evidence-checks-registry entry** ([`docs/evidence-checks-registry.yaml`](../../../evidence-checks-registry.yaml)) — `parallel-work-sentinel-pickup` row
- **Sibling Story-2** — [CFP-967](https://github.com/mclayer/plugin-codeforge/issues/967) (mechanical wire carrier — script + hook + workflow + bats)
- **Memory rule 6** — feedback_session_start_parallel_work_check.md `Rule 6 — title-based search 의무` (CFP-953 incident carrier)
- **Memory rule 7** — feedback_session_start_parallel_work_check.md `Rule 7 — Epic 진행 중 polling 의무` (CFP-946 incident carrier)
- **Verify-before-trust 4-layer governance** ([CLAUDE.md](../../../../CLAUDE.md) "## ADR" section) — ADR-073 Layer 1 / ADR-070 Layer 2 / ADR-082 Layer 3 / ADR-045 §D Layer 4 disjoint scope
- **Orchestrator playbook §3.5** ([`docs/orchestrator-playbook.md`](../../../orchestrator-playbook.md)) — Worktree dispatch lane spawn lifecycle + polling 의무 enum

## 정의

**Parallel work sentinel polling** 은 codeforge orchestration 의 **transition state verify** layer — Orchestrator 가 long-running session 안에서 발생하는 mid-flight parallel race incidence 를 cover 하는 sustained polling discipline. ADR-073 Amendment 2 declarative anchor + sibling Story-2 (CFP-967) mechanical wire 가 normative-only → mechanical 전환 carrier.

기존 codeforge orchestration discipline 3-tier 중 transition state verify layer 가 부재 영역 — base ADR-073 §결정 1 (Orchestrator 단정 발화 시점 verify, CFP-622 carrier) + Amendment 1 (ADR-082 cross-ref disjoint 보완, CFP-776 carrier) 이 cover 못 한 mid-flight transition state staleness 영역을 본 Amendment 2 가 채움 (2026-05-18 KST same-day 2/2 parallel race incidents sentinel evidence).

## 컨텍스트

본 page 는 ADR-073 (Orchestrator verify-before-assert) Amendment 2 의 narrative SSOT cross-cutting reference. CFP-966 (Story-1) declarative anchor carrier + CFP-967 (Story-2) mechanical wire sibling. memory rule 6 + rule 7 normative-only directive 의 mechanical enforcement carrier 의 anchor — same-day 2-occurrence sentinel evidence (CFP-953 + CFP-946) accumulation pattern + recurrence-driven promotion gate (count 2 / threshold 3 / promotion_trigger auto_blocking) 의 SSOT.
