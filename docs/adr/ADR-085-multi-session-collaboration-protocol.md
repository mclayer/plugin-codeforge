---
adr_number: 85
title: Multi-session collaboration protocol — 복수 Claude Code session ownership / 분담 / handoff normative SSOT
status: Accepted
category: governance
date: 2026-05-20
carrier_story: CFP-1041
parent_epic: null
supersedes: null
amends: null
amendments: []
amendment_log: []
related_stories:
  - CFP-1041  # carrier (3-pillar anchor — active_sessions[] + lane-entry sentinel + rebase merge 우선)
  - CFP-681   # retroactive evidence: rebase merge first success variant (force-push 회피)
  - CFP-953   # parallel race incident corpus #1 (title-based search 부재 → memory rule 6 신설 source)
  - CFP-946   # parallel race incident corpus #2 (Epic state poll 부재 → memory rule 7 신설 source)
  - CFP-949   # parallel race incident corpus #3 (sub-issue scope polling gap)
  - CFP-932   # parallel race incident corpus #4 (parallel session absorb)
  - CFP-954   # parallel race incident corpus #5 (collision rebase ratchet)
  - CFP-991   # parallel race incident corpus #6 (5+ parallel race single thread + 2 ancestry corruption)
  - CFP-967   # parallel race incident corpus #7 (parallel-work-sentinel-check.yml carrier)
  - CFP-1014  # parallel race incident corpus #8 (7th ratchet collision)
related_adrs:
  - ADR-073  # Orchestrator verify-before-assert (verify axis disjoint complement — Orchestrator 행위 한정, 본 ADR-085 = coordination axis pre-hoc)
  - ADR-082  # Write-time self-write verification mandate (verify axis disjoint complement — internal lane agent self-write 한정, §결정 1 4-layer 표 anchor verbatim 답습 + 5번째 row 신설)
  - ADR-070  # Codex verify-before-trust (verify axis disjoint complement — 외부 worker output 한정)
  - ADR-040  # Worktree convention (single-session worktree namespace surface — 본 ADR-085 = multi-session coordination layer 동형 보완 disjoint)
  - ADR-050  # Parallel epic conflict coordination (PR-level post-hoc detection — 본 ADR-085 = session-level pre-hoc ownership coordination disjoint)
  - ADR-058  # is_transitional + 해소 기준 (false 정합 — permanent governance ratchet 강화 방향)
  - ADR-064  # CFP scope unitary (단일 carrier 영역 분할 거부 anchor) + §self-application top-down ratchet (약화 방향 차단)
  - ADR-045  # §D-9 cross_story_pattern_adr_trigger (본 carrier = pattern_count ≥ 8 reach escalation_action adr_draft_emitted 산물)
  - ADR-024  # hotfix-bypass family member (label-registry-v2 v2.40 — active-sessions-presence / lane-entry-ownership-verify 2 신규 family member)
  - ADR-060  # evidence-checks-registry 2 entry warning tier (active-sessions-presence / lane-entry-ownership-verify, deferred-followup)
  - ADR-008  # inter-plugin contract MINOR versioning (label-registry-v2 v2.39→v2.40 신규 entry append)
related_files:
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # Amendment 4 cross-ref-only append (본문 0건 변경)
  - docs/adr/ADR-082-write-time-self-write-verification-mandate.md  # Amendment 3 cross-ref-only append (본문 0건 변경)
  - docs/adr/ADR-RESERVATION.md  # row 85 active (CFP-1041)
  - docs/inter-plugin-contracts/label-registry-v2.md  # v2.40 MINOR (2 hotfix-bypass family member)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # label-registry-v2 version "2.39" → "2.40"
  - docs/evidence-checks-registry.yaml  # active-sessions-presence + lane-entry-ownership-verify 2 entry warning tier deferred-followup
  - templates/story-page-structure.md  # frontmatter active_sessions[] field row append (5-tuple schema)
  - CLAUDE.md  # 신규 "Multi-session collaboration protocol" 단락 + verify-before-trust 단락 cross-ref 1줄
  - docs/orchestrator-playbook.md  # §3.N sub-section (lane-entry sentinel ownership verify) + ADR-073 Amd 2 polling enum 4번째 source append cross-ref
  - .claude-plugin/plugin.json  # MINOR bump (governance behavior 변경, ADR-037 정합) + marketplace.json sibling sync (ADR-063)
is_transitional: false
# Wave 1 = declarative-only (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습).
# Wave 2 mechanical wire (active_sessions[] schema enforce / lane-entry sentinel
# subprocess invoke / Issue body sync hook) = 별 sub-CFP carrier 분리.
# §결정 N+ 의 mechanical_enforcement_actions[] 2-entry deferred-followup 은 본 ADR
# effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 promotion 시
# Amendment 발의 (강화 방향만 — ADR-058 §결정 5 / ADR-064 §self-application top-down ratchet 정합).
mechanical_enforcement_actions:
  - action: active-sessions-presence
    status: deferred-followup     # Phase 1 declare / Phase 2 actual wire (별 sub-CFP carrier)
    target_section: §결정 2       # active_sessions[] field presence-grep (Story Issue body OR Story file frontmatter) lint
  - action: lane-entry-ownership-verify
    status: deferred-followup     # Phase 1 declare / Phase 2 actual wire (별 sub-CFP carrier)
    target_section: §결정 3       # lane-entry sentinel `gh pr list --search "head:<branch>"` 4번째 polling source ADR-073 Amd 2 cross-ref
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — coordination scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책). 8+ parallel race incidents single session evidence (CFP-953/946/949/932/954/991/967/1014 lineage) 가 8 occurrences sentinel ≥ ADR-045 §D-9 threshold 2 escalation_action adr_draft_emitted forcing function 산물."
pre_lookup_evidence:
  verified_files:
    - { path: "docs/adr/ADR-082-write-time-self-write-verification-mandate.md", verified-via: "Read working tree", note: "§결정 1 disjoint 4-layer 표 verbatim 답습 anchor source (5번째 row Multi-session collaboration 신설 base)" }
    - { path: "docs/adr/ADR-073-orchestrator-verify-before-assert.md", verified-via: "git show origin/main", note: "Amendment 4 cross-ref-only append target (본문 0건 변경 — disjoint 보완)" }
    - { path: "docs/adr/ADR-070-codex-verify-before-trust.md", verified-via: "git show origin/main", note: "D5 declaration-only retain 패턴 선례 + mechanical_enforcement_actions deferred-followup precedent" }
    - { path: "docs/adr/ADR-RESERVATION.md", verified-via: "Read working tree", note: "row 84 = CFP-989 active (마지막) / row 85 부재 → ADR-085 번호 가용 확정. row 79/80/81/82/84 precedent = reserved 미경유 직접 active" }
    - { path: "CLAUDE.md", verified-via: "wc -l (Bash)", note: "315줄 (cap ≤320 CFP-506, 여유 5줄) — Codex TP#4 finding 1 fresh re-measure 정합 (NOT 321/+1 over from ADR-073 retro snapshot)" }
  origin_main_sha: "eabe2b8128a855ee1e8dd62dec0fedd624257d02"  # wrapper origin/main HEAD verified 2026-05-20 10:00 KST
  last_git_fetch_timestamp: "2026-05-20T10:00+09:00"  # KST per ADR-079
---

# ADR-085: Multi-session collaboration protocol — 복수 Claude Code session ownership / 분담 / handoff normative SSOT

## 상태

Accepted (2026-05-20 KST) — CFP-1041 carrier. PMOAgent ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach (8+ parallel race incidents single session evidence: CFP-953/946/949/932/954/991/967/1014 lineage) escalation_action `adr_draft_emitted` 산물. ADR-064 §결정 5 CFP scope unitary 정합 (independent Story, parent_epic null).

## 본질 선언

복수 Claude Code session 이 동일 repository / Story / branch / Epic 에서 동시에 작업할 때, **ownership 결정 / 분담 / handoff 의 normative 절차를 declarative SSOT 로 codify** 한다. 본 ADR 이 충족되지 않으면 아래 §결정 mechanism 을 몇 개 쌓든 의미 없다 — 모든 §결정 은 본질을 보조하는 scaffolding.

기존 codeforge governance 의 multi-session 처리 layer 는 (1) **PR-level post-hoc detection** (ADR-050 parallel-epic-conflict-check.yml — PR open 시 scope_manifest 교집합 검출) + (2) **single-session worktree namespace surface** (ADR-040 — `${HOME}/.claude/worktrees/<repo>/<branch-flat>` per-session isolation) 만 정의한다. **(3) session-level pre-hoc ownership coordination (lane entry / write 전 ownership 결정) layer = 명백한 도메인 공백** (verified-via: `git show origin/main:docs/adr/ADR-050-parallel-epic-conflict-coordination.md` + `git show origin/main:docs/adr/ADR-040-worktree-convention.md`, DomainAgent Phase 0 Read — "session ownership" / "active sessions" / "handoff baton" 키워드 0건 매칭). ADR-085 가 이 (3) layer 신설 anchor.

기존 verify-before-trust 4-layer (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) 는 모두 **verify axis** (작성 / 단언 / 외부 worker output 의 사실성 검증). ADR-085 = **coordination axis** (작성 자체의 ownership / 분담 / handoff). axis disjoint — verify 가 충족되어도 ownership 미결정 시 parallel race 발생, ownership 결정 후에도 verify 미수행 시 false claim. 두 layer 모두 필요.

## 컨텍스트

### pattern corpus (8 누적 — Issue #1041 body verbatim)

1. **CFP-953** (2026-05-18 KST) — Epic B close 후 "진행해" → Story-2 #953 + Story-3 #954 신규 생성. label-based check (`gh issue list --label parent:CFP-882`) 만 수행 → CFP-932 (실제 Wave 4 #882 Story-2 carrier, label `parent:CFP-699` 만 부착) miss → #953 brainstorm Phase 0/2 + spec PR #624 진행 후 발견. Memory rule 6 신설 source (title-based search 의무).
2. **CFP-946** (2026-05-18 KST same day SECOND) — Epic CFP-946 brainstorm Phase 0/2 + 2 Story 분해 → Story-A PR #961 MERGED 06:42:12Z, 11분 후 parallel session PR #962 MERGED 06:53:30Z → Epic #946 CLOSED. Story-B scope 분할 + memory rule 7 신설 source (Epic state poll 의무).
3. **CFP-949** (2026-05-18 KST FOURTH same-day) — Epic CFP-949 (6 lane self-owned arch doc seed). 별 session sub-issue #968-#973 발의 4초 전 본 session spec commit `c5cee2f2`. 별 session decomposition 더 정교 → 본 session stale. PR #631 close + Wave 1 stand-down. Rule 7 refinement (sub-issue layer polling 추가).
4. **CFP-932** (2026-05-18 KST) — Wave 4 sub-Epic #882 Story-2 본 session noise lesson — stale memory 진입 + parallel session 흡수 (Phase 1+2 ALL MERGED 별 session).
5. **CFP-954** (2026-05-18 KST) — Story-3 production cutover Phase 1 collision rebase v2.33→v2.34 (CFP-949 #975 dual-carrier).
6. **CFP-991** (2026-05-19 KST) — Wave 4 sub-Epic #882 Story-4 — 13+ FIX iter / 6 parallel race / **2 ancestry corruption recovery (orphan 15bc90f cherry-pick)** / re-spawn lane on fresh HEAD post-recovery (stale ESCALATE → fresh PASS) / blanket cross-module debate 3rd 실 적용.
7. **CFP-967** (2026-05-19 KST) — parallel-work-sentinel-check.yml carrier — collision rebase v2.36 45번째 (CFP-963 v2.35 44번째 병렬 merge 선점).
8. **CFP-1014** (2026-05-19 KST) — Story-5 7th parallel race v2.37→v2.38 ratchet (final state Wave 4 sub-Epic #882 close).

### 누적 신호 (super-class anchor evidence)

- **8 occurrences single session lineage** ≥ ADR-045 §D-9 threshold 2 (forcing function escalation_action `adr_draft_emitted` immediate trigger).
- **subagent self-confusion pattern** (memory `feedback_worktree_first_not_parallel_session`) — 본 session subagent 가 다른 worktree commit 을 "parallel session conflict" 로 false-positive flag (3회 단일 session: CFP-1026 STAND-DOWN / cfp-1014 dup / ArchitectPL 자기 `00b7d8a` mis-flag). subagent verdict "parallel conflict" 도 무신뢰.
- **CFP-681 rebase merge first success variant** retroactive evidence (force-push 회피 → ancestry corruption 0 evidence anchor — 본 ADR §결정 4 rebase merge 우선 normative 의 evidence 근거).

## 결정

### §결정 1 — Layer disjoint 5-layer 표 (super-class anchor)

ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row "Multi-session collaboration" 신설. anchor-first 패턴 (본 ADR 의 backbone).

| Layer | ADR | verify 대상 / scope |
|---|---|---|
| Orchestrator cross-repo state / assumption verify | ADR-073 | Orchestrator 행위 한정 — cross-repo state + assumption 기술 시 `git fetch` + `git show origin/main:<path>` direct verify + `verified-via` annotation |
| external worker (Codex) output verify | ADR-070 | 외부 worker output 한정 — Codex finding evidence ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject |
| **internal lane agent self-write verify (본 ADR)** | **ADR-082** | **lane agent §9 evidence / Phase 0 mapping / corpus enumeration write-time** — 작성 값 자체가 사실과 일치하는가 source direct verify 후 write |
| retro corpus enumeration (PMOAgent §5 pattern_count) | ADR-045 §D | retro pattern aggregation — cross-Story pattern_count ≥ threshold 검출 시 ADR escalation forcing function |
| **Multi-session coordination (본 ADR)** | **ADR-085** | **복수 Claude Code session ownership / 분담 / handoff coordination — cross-session pre-hoc coordination axis** |

5번째 row = **axis 자체가 다름** (verify axis ≠ coordination axis). layer 1-4 가 모두 충족되어도 coordination axis 부재 시 parallel race 발생. 둘 다 필요한 orthogonal layer (조합).

### §결정 2 — active_sessions[] schema mandate (Story Issue body + Story file frontmatter dual carrier)

복수 session 이 동일 Story / Epic / branch 에 entry 할 때 **active_sessions[] field 를 dual carrier 에 명시 의무**.

#### Schema (5-tuple)

```yaml
active_sessions:
  - git_identity: "MinCheol Cho <mccho@mclayer.it>"
    worktree_path: "C:/workspace/mclayer/plugin-codeforge/.claude/worktrees/cfp-1041-multi-session"
    entry_phase: "Phase 1 design lane"     # enum: "Phase 1 requirements" | "Phase 1 design" | "Phase 1 design-review" | "Phase 2 develop" | "Phase 2 code-review" | "Phase 2 security-test" | "Phase 2 integration-test" | "Phase 2 retro"
    entered_at_kst: "2026-05-20T10:00:00+09:00"   # ADR-079 KST +09:00 ISO 8601 zoned strict
    last_heartbeat_kst: "2026-05-20T10:30:00+09:00"  # update on lane phase transition (entry_phase 변경 시) + 매 PR open / commit push 직후
```

#### Dual carrier

- **Story Issue body** — `<!-- active_sessions -->` HTML comment block (parallel-epic-conflict-check.yml scope_manifest pattern 답습). Orchestrator (Inline whitelist 1번 entry 사용자 dialog 영역) 또는 GitOpsAgent 가 write.
- **Story file frontmatter** — `active_sessions: []` array field (templates/story-page-structure.md frontmatter 표 codify, **D8 deliverable**).

#### Backward-compat

기존 Story default `[]` (optional field). 기존 미명시 Story = legacy single-session (Wave 1 declarative — Wave 2 mechanical lint promotion 시 점진 ratchet).

### §결정 3 — lane-entry sentinel ownership verify (ADR-073 Amd 2 polling enum 4번째 source append cross-ref)

**lane entry 직전 의무**: ownership 검증 4-step polling.

1. **memory rule 6** (title-based search) — `gh issue list --search "<EPIC>-* in:title parent:CFP-<N>"` (label-based 부재 시 title fallback).
2. **memory rule 7** (Epic state poll) — `gh issue view <EPIC> --json state,labels`.
3. **active_sessions[] field check** — Story Issue body + frontmatter active_sessions[] 모두 verify (§결정 2 dual carrier).
4. **🆕 lane-entry sentinel** — `gh pr list --search "head:<branch>"` PR existence check (다른 session 이 이미 PR open 했는가).

위 4-step 모두 통과 시에만 lane entry. 1+ failure → Orchestrator 가 사용자 dialog 발화 (Inline whitelist 1번 entry, codeforge:user-dialog-mode skill 경유) — "parallel session detected, defer / takeover / abandon" 결정.

**ADR-073 Amendment 2 cross-ref**: §결정 1 expansion polling enum 3종 (`lane_spawn` / `pr_open` / `merge_transition`) → 4번째 source `active_sessions_check` append (cross-ref-only — ADR-073 본문 0건 변경 disjoint 보완, **D3 deliverable**).

### §결정 4 — Rebase merge 우선 normative (force-push 회피)

**lane re-spawn / FIX iter / handoff 시**: `git pull --rebase origin main` 우선. `git push --force` / `git push --force-with-lease` 회피.

#### Evidence

- **CFP-681 retroactive evidence** — rebase merge first success variant. force-push 0 사용 → ancestry corruption 0 evidence anchor.
- **CFP-991 counter-evidence** — 2 ancestry corruption recovery (orphan `15bc90f` cherry-pick) — force-push 사용 시 ancestry 손상 발생. ADR §6 candidate force-push pre-flight HEAD-pin gate carrier (pattern_count 2 CFP-967+991, 별 CFP 권고).

#### Exception (sub-§결정 4.1)

force-push 필수 영역 (sequential merge conflict resolution / stale base rebase) = `--force-with-lease=branch:sha` 사용 의무 + **HEAD-pin pre-flight gate** (`gh api repos/<owner>/<repo>/commits/<branch> --jq .sha` fresh re-pin 후 push). memory `feedback_verify_pin_head_sha` carrier.

### §결정 5 — Handoff baton transfer protocol (#870 inline absorb)

In-flight FIX baton transfer (Session A → Session B handoff) 시 의무.

#### Schema (active_sessions[].fix_iter_ownership field 신설)

```yaml
active_sessions:
  - git_identity: "..."
    fix_iter_ownership:
      handoff_from: "MinCheol Cho <mccho@mclayer.it>"   # 직전 session git_identity
      handoff_to: "MinCheol Cho <mccho@mclayer.it>"     # 본 session git_identity (자기 session)
      fix_iter_number: 2                                 # §10 FIX Ledger row number
      handoff_at_kst: "2026-05-20T11:00:00+09:00"
      handoff_reason: "context-budget-exhausted"        # enum: context-budget-exhausted | user-redirect | structural-restart-ADR-053 | other
```

#### Procedure

1. **Session A** (handoff_from) — §10 FIX Ledger row append (Orchestrator monopoly, fix-event-v1 contract) + active_sessions[] entry update `last_heartbeat_kst` + Story §9 evidence write + `git push origin <branch>`.
2. **Session A** — handoff comment to Story Issue `[handoff:CFP-1041]` (comment-prefix-registry-v1 14번째 entry — 별 sub-CFP carrier).
3. **Session B** (handoff_to) — lane entry 4-step polling (§결정 3) 통과 후 `git pull --rebase origin <branch>` + active_sessions[] entry append + fix_iter_ownership populate.

#### Cross-ref

fix-event-v1 schema 변경 0 (별 sub-CFP carrier 분리). Wave 1 = declarative-only. Wave 2 mechanical (comment-prefix `[handoff:...]` lint + active_sessions[] field validate hook) = 별 sub-CFP.

### §결정 6 — Race-window resolution + heartbeat grace

#### Race window definition

두 session 이 동시 entry / 동시 push / 동시 PR open 발생 시 — `active_sessions[]` array 가 partial state (둘 다 자기 entry append 시도 → git merge conflict).

#### Resolution

1. **First-write-wins by `entered_at_kst`** — earlier timestamp 가 ownership 보유. later session 은 conflict resolve 시 `entered_at_kst` 비교 후 자기 entry 제거 또는 lane defer 결정.
2. **Heartbeat grace 24h** — `last_heartbeat_kst` 가 24h 초과 stale 시 다른 session 이 takeover 가능 (Wave 2 orphan reaper carrier).
3. **Tie-breaker** — `entered_at_kst` 동일 (1-second precision) 시 `git_identity` alphabetical 우선 (deterministic).

### §결정 7 — Subagent self-confusion mitigation (EC-10, Codex TP#4 finding 6)

**Issue**: 본 session subagent 가 다른 worktree commit (자기 session 의 dedicated worktree) 을 "parallel session conflict" 로 false-positive flag (3회 단일 session: CFP-1026 STAND-DOWN / cfp-1014 dup / ArchitectPL 자기 `00b7d8a` mis-flag — memory `feedback_worktree_first_not_parallel_session` carrier).

#### Mitigation

subagent verify-before-trust 시 active_sessions[] field 가 **first-class source** (memory `feedback_worktree_first_not_parallel_session` carrier 정합).

##### Procedure (subagent self-discipline)

1. Subagent 가 non-FF push 거부 / 예상 외 commit / "parallel session" 단정 signal 검출 시 — **즉시 단정 금지**.
2. **active_sessions[] field check 의무** (Story Issue body + frontmatter dual) — 본 session entry 확인.
3. `git worktree list` + `git reflog` ownership verify — 본 session 의 dedicated worktree 인가 확인.
4. 1-3 모두 통과 시 = **본 session subagent 자기 commit** (parallel session 아님). subagent verdict "parallel conflict" 도 무신뢰.

### §결정 8 — known-limitation (mechanical_enforcement_actions 2-entry deferred-followup rationale binding)

frontmatter `mechanical_enforcement_actions: [active-sessions-presence, lane-entry-ownership-verify]` 2-entry **deferred-followup** retain.

#### Rationale

- **ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습** — Wave 1 declarative-only + Wave 2 mechanical wire 별 sub-CFP carrier 분리. precedent chain 5번째 instance (ADR-070 §D5 → ADR-082 §결정 6 → ADR-081 §결정 D6.e → ADR-070 Amendment 4 D6.4 → 본 §결정 8).
- **ADR-040 Amendment 3 frontmatter 의무 정합** — governance category ADR 의 mechanical_enforcement_actions[] 필수 (missing flag 회피).
- **ADR-058 §결정 5 ratchet 강화 방향만** — Wave 2 mechanical wire 시 `status: deferred-followup → warning` promotion (약화 방향 차단).

#### Wave 2 promotion criteria

본 ADR effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 promotion 시 Amendment 1 발의:

- `active-sessions-presence` — Story Issue body OR frontmatter `active_sessions[]` presence-grep lint (PR open 시).
- `lane-entry-ownership-verify` — lane entry 4-step polling subprocess invoke (ADR-073 Amendment 2 polling enum 4번째 source wire).

별 sub-CFP carrier 의 hotfix-bypass label 4-tier scope = `hotfix-bypass:active-sessions-presence` / `hotfix-bypass:lane-entry-ownership-verify` (label-registry-v2 v2.40 신규 family member).

### §결정 N+ — Out-of-scope declarations (본 carrier scope 외 영역)

본 ADR-085 scope 외 영역 (별 carrier 분리 의무):

- **ADR-050 본문 0건 변경** — parallel-epic-conflict-check.yml (PR-level post-hoc) 와 ADR-085 (session-level pre-hoc) 는 axis disjoint complement. ADR-050 본문 amend 불요.
- **fix-event-v1 schema 변경 0** — §결정 5 handoff baton transfer 의 fix-event-v1 schema 변경 (handoff_baton optional field 신설) = 별 sub-CFP carrier (inter-plugin contract MINOR bump 의무, ADR-008 정합).
- **superpowers:writing-plans amend 불요** — plan-time multi-session brainstorming guidance 는 별 carrier (cross-plugin sibling sync 후순위 ratchet).
- **Wave 2 mechanical wire 별 sub-CFP carrier** — `active-sessions-presence.yml` workflow + `lane-entry-ownership-verify.yml` workflow + `templates/scripts/active-sessions-validate.sh` 등 mechanical layer = 별 carrier 분리 (Wave 1 declarative-only invariant 보존).
- **comment-prefix-registry-v1 v1.3 14번째 entry `[handoff:CFP-NNNN]`** — §결정 5 handoff comment prefix 신설 = 별 sub-CFP carrier (inter-plugin contract MINOR bump, ADR-008 정합).

## 결과

### 정량 결과

- **8 occurrences pattern_count corpus** → super-class anchor ADR codify (forcing function 산물).
- **5-layer disjoint 표** anchor — 4-layer verify axis + 1-layer coordination axis 완전성 codify (ADR-082 §결정 1 verbatim 답습 + 1 row 신설).
- **2 hotfix-bypass family member** (label-registry-v2 v2.39 → v2.40 MINOR).
- **2 evidence-checks-registry entry** (active-sessions-presence + lane-entry-ownership-verify, warning tier deferred-followup).
- **CLAUDE.md 4 line net add** (cap 320 여유 5줄 정합, Codex TP#4 finding 1 fresh re-measure).

### 정성 결과

- **codeforge governance 의 3rd axis 완성** — verify axis (ADR-073/070/082/045 §D) + worktree namespace axis (ADR-040) + **coordination axis (ADR-085 신설)** orthogonal triplet.
- **subagent self-confusion mitigation** (EC-10) — memory `feedback_worktree_first_not_parallel_session` 의 normative 승격 (rule 6+7 + ADR-085 §결정 7 = declarative anchor).
- **handoff baton transfer protocol** — context-budget-exhausted / user-redirect / structural-restart 3 enum scenario 대응 (Wave 1 declarative + Wave 2 mechanical wire).

### 후속 carrier (별 CFP 의무)

- **active-sessions-presence.yml workflow** 신설 (Wave 2 mechanical wire) — Story Issue body OR frontmatter active_sessions[] presence-grep lint (PR open 시).
- **lane-entry-ownership-verify.yml workflow** 신설 (Wave 2 mechanical wire) — lane entry 4-step polling subprocess invoke.
- **fix-event-v1 schema MINOR bump** — §결정 5 handoff_baton optional field 신설 (ADR-008 정합 sibling sync 의무).
- **comment-prefix-registry-v1 v1.3 14번째 entry `[handoff:CFP-NNNN]`** — §결정 5 handoff comment prefix.
- **force-push pre-flight HEAD-pin gate ADR draft** (pattern_count 2 CFP-967+991 reach) — §결정 4 sub-§결정 4.1 mechanical wire.
- **orphan reaper 24h grace** (Wave 2) — §결정 6 heartbeat grace.

## 해소 기준

N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — coordination scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책).

self-referential 주의: 본 ADR 의 해소 기준 부재 선언 자체가 §결정 3 lane-entry sentinel 대상 아님 (verify axis 아닌 coordination axis self-protection).

## 관련 파일

- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) — §결정 1 4-layer 표 verbatim 답습 anchor source (Amendment 3 cross-ref-only append, 본문 0건 변경)
- [ADR-073](ADR-073-orchestrator-verify-before-assert.md) — verify axis disjoint complement (Amendment 4 cross-ref-only append, 본문 0건 변경)
- [ADR-070](ADR-070-codex-verify-before-trust.md) — verify axis disjoint complement (D5 declaration-only retain precedent)
- [ADR-040](ADR-040-worktree-convention.md) — worktree namespace axis disjoint complement (single-session)
- [ADR-050](ADR-050-parallel-epic-conflict-coordination.md) — PR-level post-hoc detection disjoint complement (본 ADR = session-level pre-hoc)
- [ADR-045](ADR-045-story-retro-mandatory-trigger.md) — §D-9 cross_story_pattern_adr_trigger forcing function source (pattern_count ≥ 8 reach escalation_action adr_draft_emitted)
- [ADR-064](ADR-064-decision-principle-mandate.md) — §결정 5 CFP scope unitary + §self-application top-down ratchet
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — is_transitional + 해소 기준 의무 (false 정합 + 약화 차단)
- [ADR-024](ADR-024-story-scoped-branch-policy.md) — Amendment N (label-registry-v2 v2.40 — 2 hotfix-bypass family member)
- [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — evidence-checks-registry 2 entry warning tier (deferred-followup)
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — label-registry-v2 v2.39 → v2.40 MINOR bump 정합
- [ADR-RESERVATION.md](ADR-RESERVATION.md) — row 85 active (CFP-1041)
- `docs/inter-plugin-contracts/label-registry-v2.md` — v2.40 MINOR (2 family member append)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — label-registry-v2 version "2.39" → "2.40"
- `docs/evidence-checks-registry.yaml` — active-sessions-presence + lane-entry-ownership-verify 2 entry
- `templates/story-page-structure.md` — frontmatter active_sessions[] field row append (5-tuple schema)
- `CLAUDE.md` — 신규 "Multi-session collaboration protocol" 단락 + verify-before-trust 단락 cross-ref 1줄
- `docs/orchestrator-playbook.md` — §3.N sub-section + ADR-073 Amd 2 polling enum 4번째 source cross-ref
- `.claude-plugin/plugin.json` — MINOR bump + marketplace.json sibling sync (ADR-063 atomic invariant)

## 외부 fact

- **CFP-681 success variant** (2026-05-19 KST, parallel session #1027 force-push pre-flight gate 첫 성공) — retroactive evidence anchor: rebase merge first / force-push 회피 → ancestry corruption 0. 본 ADR §결정 4 evidence 근거.
- **8 parallel race incidents single session lineage** (2026-05-18 ~ 2026-05-19 KST, CFP-953/946/949/932/954/991/967/1014) — pattern_count ≥ 8 reach evidence (memory entries 누적).
- **subagent self-confusion 3 occurrences single session** (CFP-1026 STAND-DOWN / cfp-1014 dup / ArchitectPL 자기 `00b7d8a` mis-flag — memory `feedback_worktree_first_not_parallel_session`) — EC-10 evidence.
