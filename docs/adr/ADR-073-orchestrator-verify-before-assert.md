---
adr_number: 73
title: Orchestrator verify-before-assert — cross-repo ground truth + assumption verify mandate
status: Accepted
category: governance
date: 2026-05-14
carrier_story: CFP-622
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    cfp: CFP-776
    date: 2026-05-17
    scope: "ADR-082 cross-ref 보완 관계 명시 (disjoint 보완) — ADR-073 = Orchestrator 행위(cross-repo state + assumption) 한정 ↔ ADR-082 = internal lane agent self-write(§9 evidence / Phase 0 mapping / corpus enumeration) write-time semantic truth verify. 두 layer disjoint, scope 침범 0. ADR-082 §결정 1 layer disjoint 4-layer 표가 공통 anchor (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D). 본문 §결정 / mechanism 의미 변경 없음 — cross-ref-only Amendment."
    status: applied
    ref: "## Amendments / Amendment 1 + ADR-082 §결정 1"
    sunset_justification: null
  - amendment_id: 2
    cfp: CFP-966
    date: 2026-05-18
    scope: "§결정 1 expansion — transition trigger enum 3종 (lane_spawn / pr_open / merge_transition) + cold start session_start 보강 + sustained in-session polling 의무 (turn-0-only SessionStart hook 한계 해소). 본 Amendment 는 §결정 1-8 본문 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 0건. evidence-checks-registry warning-tier entry parallel-work-sentinel-pickup (recurrence count 2 / threshold 3 / promotion_trigger auto_blocking, schema v1.2 정합) 가 measurement carrier. memory rule 6 (title-based search) + rule 7 (Epic state poll) = declarative cross-ref normative anchor (mechanical enforcement = sibling Story-2 CFP-967 carrier). Sentinel: 2026-05-18 KST same-day 2/2 parallel race incidents (CFP-953 first label-based search miss + CFP-946 second 11분 gap Epic close miss)."
    status: applied
    ref: "## Amendments / Amendment 2 + CFP-966 carrier"
    sunset_justification: null
  - amendment_id: 3
    cfp: CFP-689
    date: 2026-05-20
    scope: "§결정 1 expansion — transition trigger enum 4번째 entry `worktree_lane_spawn` 추가 (closed-set ratchet 강화, Amendment 2 §결정 1-A precedent 답습) + worktree-first 환경 self-ownership verify 3-tuple path-based normative (a) cwd ↔ worktree path 일치 (`git rev-parse --show-toplevel` vs `git worktree list --porcelain`, path normalize forward-slash + lowercase drive-letter) (b) HEAD lineage ↔ session reflog membership (long-Phase-gap reflog 90d GC 시 (a)+(c) 2-source AND fallback) (c) `git worktree list --porcelain | grep <branch>` + reflog 2-source AND ownership verify + subagent verdict `parallel_session_conflict` 발화 시 Orchestrator re-verify mandate (ADR-082 verify-before-trust 자기 산출물 영역 확장 cross-ref — agent 도 multi-worktree self-confusion 보임). 본 Amendment 는 §결정 1-8 본문 + Amendment 1+2 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 0건. evidence-checks-registry warning-tier entry `worktree-self-ownership-verify` (recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, declaration-only-Wave-1) 가 measurement carrier. memory `feedback_worktree_first_not_parallel_session` = normative 승격 carrier. Sentinel: 2026-05-19~20 KST single session 3 occurrences (CFP-1026 STAND-DOWN false-positive + CFP-681 cfp-1014 dup worktree RequirementsPL `f39b221` self-misflag + CFP-681 ArchitectPL Phase 3 자기 ArchitectAgent commit `00b7d8a` parallel_session_conflict mis-flag)."
    status: applied
    ref: "## Amendments / Amendment 3 + CFP-689 carrier"
    sunset_justification: null
  - amendment_id: 4
    cfp: CFP-1041
    date: 2026-05-20
    scope: "ADR-085 cross-ref 보완 관계 명시 (disjoint complement — verify axis ↔ coordination axis). ADR-073 = Orchestrator 행위(cross-repo state + assumption) verify 한정 (verify axis) ↔ ADR-085 = 복수 Claude Code session ownership / 분담 / handoff coordination (coordination axis, pre-hoc cross-session). 두 layer axis disjoint — verify 가 충족되어도 ownership 미결정 시 parallel race 발생, ownership 결정 후에도 verify 미수행 시 false claim. ADR-085 §결정 1 5-layer disjoint 표가 공통 anchor (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설). 본 Amendment 는 §결정 1 lane-entry sentinel 4-step polling 의 4번째 source (active_sessions_check) cross-ref-only append — 본문 §결정 1-8 + Amendment 1-3 mechanism 의미 변경 0 (ADR-085 §결정 3 cross-ref-only Amendment, ADR-082 Amendment 1 ADR-073 cross-ref pattern verbatim 답습). post-rebase sequence [1, 2, 3 (CFP-689 worktree-first self-ownership), 4 (본 CFP-1041 ADR-085 coordination)] consecutive — sibling escalation #1038 의 actual carrier = CFP-689 (PR #1043 merged 18236621 2026-05-20, 본 CFP-1041 Phase 1 PR open 도중 origin/main 으로 advance), dogfooding ADR-085 본 carrier 가 codify 하는 `parallel_session_shared_workdir_collision` pattern (9th+ parallel race lineage single session evidence)."
    status: applied
    ref: "## Amendments / Amendment 4 + ADR-085 §결정 3"
    sunset_justification: null
related_stories:
  - CFP-622  # carrier
  - CFP-776  # Amendment 1 — ADR-082 cross-ref (disjoint 보완)
  - CFP-966  # Amendment 2 — transition trigger enum + sustained polling (declarative anchor)
  - CFP-967  # Amendment 2 sibling — mechanical wire (script + hook + workflow + bats)
  - CFP-953  # Amendment 2 sentinel evidence (first parallel race — label-based search miss)
  - CFP-946  # Amendment 2 sentinel evidence (second parallel race — 11분 gap Epic close miss)
  - CFP-689  # Amendment 3 — worktree-first self-ownership verify 3-tuple (declarative anchor, plugin-codeforge#1038 carrier)
  - CFP-1038 # Amendment 3 carrier ESC — PMO P1 escalation (worktree_first_self_confusion_within_single_session pattern_count 3 reach, plugin-codeforge#1038)
  - CFP-983  # Amendment 3 candidate (c) 정식 carrier — #983 P1 ESC body shared workdir collision worktree-first invariant 강화 영역
  - CFP-1041 # Amendment 4 — ADR-085 disjoint complement (verify axis ↔ coordination axis), §결정 1 lane-entry sentinel 4-step polling 의 4번째 source `active_sessions_check` cross-ref-only append
  - CFP-597  # sentinel #4 strike #1 origin (CLAUDE.md cap + playbook §3.6 false alarm)
  - CFP-578  # ADR-070 verify-before-trust 자매 (external worker output)
  - CFP-612  # ADR-071 dialog convergence 자매 governance
  - CFP-635  # sister Epic over-questioning (super-class shared, scope disjoint)
related_adrs:
  - ADR-070  # 자매 ADR (external worker output verify ↔ self-assertion verify)
  - ADR-071  # sister governance (dialog convergence layer)
  - ADR-082  # disjoint super-class (internal lane agent self-write verify — Orchestrator 행위 ↔ lane agent self-write)
  - ADR-039  # Inline whitelist boundary (verify 액션 분류 추가 row)
  - ADR-058  # sunset_justification (false 정합)
  - ADR-064  # decision principle mandate (self-application top-down ratchet)
  - ADR-012  # CLAUDE.md cap (cross-ref 추가 시 압축 plan 동반)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무 (governance category)
  - ADR-085  # Amendment 4 — disjoint complement (verify axis ↔ coordination axis, ADR-085 §결정 1 5-layer 표 anchor)
related_files:
  - CLAUDE.md  # 결정 원칙 section + ADR list 영역 cross-ref
  - skills/codeforge-brainstorm/SKILL.md  # verify 의무 amend
  - <internal-docs>/wrapper/templates/spec.md  # pre_lookup_evidence[] field 신설
  - <internal-docs>/wrapper/templates/plan.md  # pre_lookup_evidence[] field 신설
is_transitional: false
mechanical_enforcement_actions:
  - parallel-work-sentinel-pickup     # CFP-966 Amendment 2 — declarative anchor (warning tier, sibling Story-2 CFP-967 mechanical wire merged 2026-05-19, status: warning per ADR-040 Amendment 3 §결정 7.D self-application 정합)
  - worktree-self-ownership-verify    # CFP-689 Amendment 3 — declarative anchor (warning tier, declaration-only-Wave-1, recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, actual lint script + workflow + hook = sibling Story-2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup precedent 답습)
# Wave 1 = behavioral directive only (Orchestrator self-discipline forcing function) — Amendment 2 (CFP-966)
# 가 첫 mechanical_enforcement_actions[] row entry append (declarative anchor only — script + workflow
# 실 binding 은 sibling Story-2 CFP-967 carrier).
# Layer 2 mechanical lint (pre-tool-use hook 또는 evidence-checks-registry warning-tier) = 별도 follow-up CFP 분리.
# 본 ADR effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 추가될 때
# mechanical_enforcement_actions[] 갱신 + Amendment 발의 (강화 방향만 — ADR-058 §결정 5 / ADR-064 §결정 7
# top-down ratchet 정합).
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책)."
pre_lookup_evidence:
  verified_files:
    - { path: "docs/adr/ADR-070-codex-verify-before-trust.md", verified-via: "git show origin/main", note: "자매 ADR — 본질 선언 패턴 + 결정 구조 reference" }
    - { path: "docs/adr/ADR-071-orchestrator-user-dialog-convergence.md", verified-via: "git show origin/main", note: "anchor-first 패턴 차용 (mechanism 우선 reading risk 회피)" }
    - { path: "docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md", verified-via: "git show origin/main", note: "Inline whitelist 4-entry boundary" }
    - { path: "docs/adr/ADR-058-adr-sunset-criteria-mandate.md", verified-via: "git show origin/main", note: "is_transitional: false 정합 + sunset_justification ratchet 차단" }
    - { path: "docs/adr/ADR-064-decision-principle-mandate.md", verified-via: "git show origin/main", note: "self-application top-down ratchet (강화 방향 only)" }
    - { path: "docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md", verified-via: "git show origin/main", note: "Amendment 1 §결정 6 cap 320 (현 CLAUDE.md = 321줄, +1 over)" }
    - { path: "docs/adr/ADR-040-worktree-convention.md", verified-via: "git show origin/main", note: "Amendment 3 governance category mechanical_enforcement_actions[] 의무 (Wave 1 = []  empty + retroactive 면제 표시)" }
  origin_main_sha: "e5c5c64e64b28a83f312210a2a9c71e177738fb3"  # git rev-parse origin/main 결과 (PL self-application 첫 적용)
  last_git_fetch_timestamp: "2026-05-14T18:30+09:00"  # KST per memory feedback_time_display
---

# ADR-073: Orchestrator verify-before-assert — cross-repo ground truth + assumption verify mandate

## 상태

Accepted (2026-05-14 KST, CFP-622 carrier). `is_transitional: false` — 영구 정책 (governance carrier, ADR-064 / ADR-058 self carrier 패턴 정합).

## 본질 선언

> **Orchestrator 가 cross-repo state 또는 assumption 을 단정할 때, ground truth 를 verify-before-assert 의무.**

위 본질 선언이 본 ADR 의 **anchor**. 본 ADR 의 모든 §결정 (mandate / mechanism enumeration / 3-layer coherence / subagent context packet / spec template field / skill body amend / scope 외 분리) 은 본질을 보조하는 **scaffolding** — mechanism 만 codify 하고 본질 (verify discipline) 을 놓치면 ADR-071 가설 E (mechanical 규칙 자체 한계) 의 self-defeating trap 으로 떨어진다. 본 anchor 가 §결정 1 보다 먼저 배치된 이유 = mechanism 우선 reading risk 회피 forcing function (ADR-071 anchor-first 패턴 차용).

본 ADR 은 ADR-070 / ADR-071 와 함께 super-class "Orchestrator self-discipline ratchet" 의 3 children 중 1 children:

| Layer | ADR | Producer | Verify 영역 |
|---|---|---|---|
| External worker output | ADR-070 | Codex (외부 worker) | review-verdict-v4 finding evidence |
| Orchestrator self-assertion | **ADR-073 (본 ADR)** | Orchestrator (자기) | cross-repo state + file path 단정 |
| User dialog convergence | ADR-071 | Orchestrator (사용자 대화) | 4 vulnerability 차단 + 4 layer 검증 |

mechanism 만 codify 하고 본질을 놓치면 self-defeating trap. 3 layer cross-ref 의무 (§결정 3 표 verbatim).

## 컨텍스트

본 ADR 의 동인은 sentinel #4 strike 누적 evidence — Orchestrator 가 cross-repo file / state 인용 시 working tree 또는 stale local state 를 ground truth 로 신뢰하는 anti-pattern.

### Strike 누적 evidence 표

| Strike | Story | 일자 | 발견 영역 | 결과 |
|---|---|---|---|---|
| #1 | CFP-597 retro §6 sentinel #4 | 2026-05-13 | playbook §3.6 false alarm + CLAUDE.md 320 cap 위협 | 1 sample sentinel — 다음 carrier 동일 anti-pattern 재현 시 ADR 발의 임계 도달 declare |
| #2 | CFP-622 본 carrier (2026-05-14 KST) | 2026-05-14 | `grep -c §3.6\|§5.7 c:/workspace/mclayer/plugin-codeforge-{design,pmo}/agents/...` → 0 hits (false-negative). 실제 origin/main = CFP-597 PR #41 (f608838 design) + #17 (f77766d pmo) 으로 sibling backfill 완료 상태 | Root cause: `git fetch origin` 누락. Cascade: spec/plan/4 worktree 가짜 작업 ~30분 + 사용자 cognitive load 3회 confirm + 4 worktree setup→prune |

→ Issue #607 sentinel "2번째 sample 발견 시 ADR 발의 임계 도달" 충족. 본 ADR-073 발의 carrier.

### Systemic 4-layer staleness hierarchy (Bazel hermeticity 동형)

ground truth 의 staleness 계층:

```
working tree mutable        ← 가장 stale (uncommitted edits)
< local main push-lag       ← local commit 후 push 전
< origin/main canonical     ← canonical (GitHub remote)
< GitHub API eventual       ← API cache (eventual consistency)
```

Orchestrator 가 단정 발화 시 사용해야 하는 ground truth = **origin/main canonical** (working tree 와 local main 은 staleness 영역). GitHub API staleness 는 별도 영역 (§결정 7 scope 외 분리).

### 현 SSOT 결격 영역

- ADR-070 (Codex external worker verify) = external worker output scope. Orchestrator self-assertion 영역 normative anchor 부재.
- ADR-071 (사용자 dialog convergence) = dialog 표현 / 사실 vs 가치 분리 영역. cross-repo state factual verify 영역 부재.
- ADR-039 §결정 2 (Inline whitelist 4-entry) = inline 액션 분류 영역. file path / cross-repo state 인용 시 verify 의무 boundary 모호.
- ADR-064 §결정 7 (self-application top-down ratchet) = 결정 원칙 ratchet 영역. file Read 액션 verify 의무 영역 부재.

기존 SSOT 들이 super-class "Orchestrator self-discipline ratchet" 의 일부만 커버 — Orchestrator self-assertion verify 영역은 normative anchor 신설 영역 (본 ADR-073).

## 결정

### §결정 1 — Verify-before-assert mandate

Orchestrator (또는 subagent) 가 sibling plugin / cross-repo file path / state 에 대해 **단정 발화** 시 (예: "X file 안 §N section 부재", "Y issue closed 상태", "Z PR merged"), 다음 4 의무:

1. `cd <repo> && git fetch origin` 선행 (working tree stale 우려)
2. `git show origin/main:<path>` 또는 `gh issue/pr view --json state` direct verify
3. 인용 옆 `verified-via: <method>` annotation
4. spec/plan frontmatter 안 `pre_lookup_evidence[]` PL 수동 declaration (mechanical layer 부재 시)

**적용 영역**: cross-repo state + assumption 기술 한정. Inline whitelist (ADR-039 §결정 2 4-entry) 영역 안 단순 file stat (line count / section exist) 는 inline 허용 — **단정 발화 시만 verify 의무**.

**Inline whitelist boundary 표** (ADR-039 §결정 2 4-entry 영역 cross-ref):

| 액션 | 분류 | Verify 의무 | 근거 |
|---|---|---|---|
| 사용자 dialog 중 file Read | inline (ADR-039 1번 entry) | 인용 시만 (단순 stat 면제) | ADR-071 §결정 11 cognitive 보강 영역 |
| TodoWrite scratchpad | inline (ADR-039 2번 entry) | 면제 | non-assertion |
| Read-only Q&A 답변 | inline (ADR-039 3번 entry) | 인용 시만 (단순 stat 면제) | answer-only scope |
| Status report | inline (ADR-039 4번 entry) | 인용 시 의무 | factual claim 영역 |
| 사용자/subagent 단정 발화 | non-inline (subagent spawn 영역) | **의무** | 본 §결정 1 |

**거절된 대안 D1**:
- (D1-A) 모든 file Read 시 verify 의무 강제 — Inline whitelist 영역 침범 + ADR-039 default subagent context 정합 위반
- (D1-B) Codex worker 영역만 verify (ADR-070 흡수) — Orchestrator self-assertion 영역 systemic 원인 미해소 (strike #2 evidence 자체가 Orchestrator 자기 단정 영역)
- (D1-C) verify 의무를 사용자 dialog turn 한정 — ADR-071 dialog convergence 영역 침범 + subagent spawn prompt staleness 영역 미해소 (§결정 4 영역)

### §결정 2 — Mechanism enumeration (super-class anchor + extensible)

super-class = "stale source 인용 anti-pattern". 현재 mechanism 2 종, future strike #3+ append 가능 (ADR-058 §결정 5 ratchet 강화 방향 only).

| ID | Mechanism | Strike origin | 차단 mechanism |
|---|---|---|---|
| M1 | same-repo working tree mutation lag | CFP-597 retro §6 strike #1 (CLAUDE.md 320 cap stale read — working tree 미반영) | `wc -l <file>` 사전 측정 + 압축 plan 동반 (ADR-012 Amendment 1 정합) |
| M2 | cross-repo origin lag | 본 carrier strike #2 (git fetch 누락 → sibling backfill 인지 실패 → CFP-597 PR #41/#17 누락 인지 가짜 작업 ~30분) | `git fetch origin` 선행 + `git show origin/main:<path>` direct verify |
| M3+ | future strike (TBD) | TBD (다음 carrier sentinel) | TBD |

future strike #3+ 발견 시 row append 의무 — Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). M1 + M2 row 삭제 / 약화 변경 = sunset_justification 의무 (ratchet 차단 logic 통과 의무).

**Future append schema**:
```
| ID | Mechanism | Strike origin | 차단 mechanism |
|----|-----------|---------------|----------------|
| M3 | <신규 staleness 영역> | <Story ref + sentinel> | <차단 cmd / annotation> |
```

### §결정 3 — 3-layer coherence

verify-before-trust 원칙 3 layer cross-ref 의무. layer 침범 금지 (각 layer scope 분리 — 흡수 / 통합 시 dispatch_mode scope 침범 risk):

| Layer | ADR | Producer | 적용 영역 | scope 분리 사유 |
|---|---|---|---|---|
| External worker output | ADR-070 | Codex (외부 worker) | review-verdict-v4 finding evidence + verbatim attach | sandbox boundary cross-cutting (file Read 실패 silent fallback) |
| Orchestrator self-assertion | **ADR-073 (본 ADR)** | Orchestrator (자기) | cross-repo state + file path 단정 | working tree mutable < origin/main canonical staleness 영역 (ADR-070 sandbox 영역 외) |
| User dialog convergence | ADR-071 | Orchestrator (사용자 대화) | 4 vulnerability 차단 + 4 layer 검증 + cognitive convergence | dialog 표현 layer (ADR-073 factual verify 와 disjoint) |

**3 ADR 동시 진행 가능** (file-level conflict 0): super-class "Orchestrator self-discipline ratchet" children 이지만 producer / scope / verify 영역 모두 disjoint.

**거절된 대안 D3**:
- (D3-A) ADR-073 을 ADR-070 Amendment 로 통합 — Codex external worker scope ↔ Orchestrator self scope type mismatch (producer 영역 침범 risk + dispatch_mode confusion)
- (D3-B) ADR-073 을 ADR-071 Amendment 로 통합 — dialog convergence cognitive layer ↔ factual verify layer scope mismatch (가설 E mechanical 규칙 자체 한계 영역 vs 사실 verify 영역 disjoint)
- (D3-C) 3 ADR 통합 super ADR 신설 — super-class anchor 가 codified 되면 children 의 mechanism enumeration 자유도 손실 + future strike append 시 Amendment 영역 침범

### §결정 4 — Subagent context packet staleness annotation

Orchestrator 가 subagent spawn 시 prompt 안 file path / cross-repo state 인용 영역에 metadata 첨부 의무. subagent 가 Orchestrator 의 "지금" 가정 회피 — subagent context packet 자체가 staleness 영역.

**Context packet schema**:

```yaml
context_packet:
  cited_files:
    - path: "<absolute path or repo:relative>"
      verified_at: "<ISO-8601 KST>"
      git_fetch_sha: "<origin/main SHA at verify>"
      verified_via: "<method — git show origin/main | gh api | wc -l 등>"
  cited_state:
    - resource: "<issue#NNN | PR#NNN | branch:<name>>"
      verified_at: "<ISO-8601 KST>"
      api_response_sha: "<gh api ETag or query timestamp>"
      verified_via: "<gh issue view | gh pr view | git ls-tree>"
```

**적용 영역**: subagent spawn prompt 안 file path / cross-repo state 인용 시 의무. 단순 dialog turn (사용자 ↔ Orchestrator) 영역은 ADR-071 영역 (본 §결정 4 scope 외).

**거절된 대안 D4**:
- (D4-A) annotation 면제 (Orchestrator 신뢰) — strike #2 evidence (Orchestrator 자기 단정 영역) 가 mitigation 부재 영역
- (D4-B) verbatim file content 첨부 의무 (ADR-070 D2 패턴 차용) — Orchestrator subagent 영역은 own working directory 일치 영역 (sandbox boundary cross-cutting 부재) — verbatim 첨부 token 비용 과다 + ADR-070 영역 침범

### §결정 5 — spec/plan template `pre_lookup_evidence[]` field 신설

spec template + plan template (codeforge-internal-docs SSOT — ADR-013 dogfood-out 정합) 에 frontmatter field 신설.

**Schema**:

```yaml
pre_lookup_evidence:
  verified_files:
    - { path, repo, verified-via, sha }  # 또는 commit SHA
  cross_section_conflict_check:
    - { issue, scope, merge_order, conflict }
  last_git_fetch_timestamp: "<ISO-8601 KST>"  # ADR-073 §결정 1 의무
  origin_main_sha: "<git rev-parse origin/main 결과>"  # PL self-application 적용 시 권장
```

**적용 영역**:
- 모든 spec/plan 신설 시 frontmatter `pre_lookup_evidence` block 의무
- 본 ADR-073 spec (`<internal-docs>/wrapper/specs/2026-05-14-cfp-622-orchestrator-verify-before-assert.md`) frontmatter 가 첫 적용 사례 (recursive bootstrap mitigation — PL 수동 declare)
- 본 ADR-073 frontmatter `pre_lookup_evidence:` block 자체가 self-application 두 번째 사례

**target file** (codeforge-internal-docs PR3 carrier):
- `<internal-docs>/wrapper/templates/spec.md`
- `<internal-docs>/wrapper/templates/plan.md`

**거절된 대안 D5**:
- (D5-A) field 명 = `evidence[]` (단순) — 의미 모호 + 기존 evidence-checks-registry 와 충돌 risk
- (D5-B) field 명 = `verified_sources[]` — verified 라는 표현 redundancy (frontmatter 자체가 PL declare 영역)
- (D5-C) field optional — spec/plan 신설 forcing function 부재 (recursive bootstrap mitigation 효력 약화)

### §결정 6 — Skill body amend (codeforge:brainstorm only)

`skills/codeforge-brainstorm/SKILL.md` 본문 안 다음 section 추가 의무:

> **자기 적용 의무 (ADR-073 §결정 1)**: Phase 0 4 agent prompt 안 file path / cross-repo state 인용 시 `git fetch origin` 선행 + `git show origin/main:<path>` direct verify + `verified-via` annotation 의무. agent prompt template 의 default behavior — 4 agent 산출물 모두 `verified-via` annotation 준수.

**적용 영역 한정** (cross-plugin amend 분리):
- `skills/codeforge-brainstorm/SKILL.md` (codeforge wrapper plugin own skill) — **본 ADR scope**
- `superpowers:writing-plans` (claude-plugins-official upstream plugin) — **본 ADR scope 외** (별도 carrier 분리, CFP-622 §10 후속 carrier 영역 declare)

**거절된 대안 D6**:
- (D6-A) `superpowers:writing-plans` skill body 도 동시 amend — cross-plugin 영역 (claude-plugins-official upstream 협의 의무 발화) — Story scope 침범 + ADR-013 dogfood-out 영역 외
- (D6-B) `codeforge:brainstorm` Phase 0 mandatory 면제 (optional 명시) — 첫 적용 사례 effort 부족 + Phase 0 4 agent prompt staleness 영역 미커버

### §결정 7 — GitHub API staleness 분리 (scope 외)

`gh issue / pr list / view` 결과도 GitHub API eventual consistency 영역 — local git state staleness 와 별도 영역 (4-layer staleness hierarchy 의 4번째 layer).

**본 ADR scope = local git state 한정** (working tree / local main / origin/main 3-layer 영역).

GitHub API staleness 영역 = 별도 CFP carrier 분리:
- cross-repo state SSOT 영역 (issue / PR / branch 단정 verify 영역)
- API ETag / cache invalidation pattern 영역
- gh CLI vs MCP github tool selection 영역

**Cross-ref**: ADR-073 본문에 GitHub API staleness 영역은 "scope 외 declare" 만 하고 mechanism / mitigation 영역은 별도 CFP carrier 위임 (super-class 동일 children 으로 분리 가능).

**거절된 대안 D7**:
- (D7-A) GitHub API staleness 도 본 ADR 흡수 — scope 비대화 + 4-layer hierarchy mechanism 영역 침범 (gh CLI / MCP github tool 영역 = wrapper repo wrapper-only ζ arc 영역)
- (D7-B) GitHub API staleness 면제 declare 부재 — scope 모호성 향후 strike #3+ 인용 시 잘못된 영역 분류 risk

### §결정 8 — hook automation 분리 (scope 외)

`pre-tool-use` hook 으로 file Read 직전 git fetch trigger = mechanical enforcement layer.

**본 ADR scope = behavioral directive layer only** (Wave 1 = []  empty mechanical_enforcement_actions[]).

**별도 follow-up CFP 분리 영역**:
- pre-tool-use hook 도입 (file Read 액션 hook)
- evidence-checks-registry warning-tier entry (`orchestrator-verify-before-assert-declared`) 등록
- ADR-040 Amendment 3 §결정 7.A schema 정합 mechanical_enforcement_actions[] 갱신
- ADR-073 Amendment 1 carrier 발의 (강화 방향 only — ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합)

**Wave 1 → Wave 2 progression chain** (ADR-040 Amendment 3 self-application 패턴 차용):
```
Wave 1 (declaration mandate)         ← 본 ADR-073 (CFP-622, 2026-05-14)
  ↓
Wave 2 (mechanical lint actual wire) ← follow-up CFP (TBD)
  ↓
Wave 3 (warning → blocking-on-pr)    ← ADR-073 Amendment 2 (TBD, ratchet 강화)
```

**거절된 대안 D8**:
- (D8-A) Wave 1 동시 mechanical_enforcement_actions[] 신설 — hook automation 영역 (pre-tool-use hook) 가 ADR-073 declaration 동시 영역에 codify 시 Wave 1 → Wave 2 progression chain 손실 (ADR-040 Amendment 3 self-application 패턴 위반)
- (D8-B) hook automation 영구 면제 — verify-before-assert 의무가 behavioral directive layer 만 codified 시 strike #3+ 재발 risk + ratchet 강화 방향 차단 (ADR-058 §결정 5 정합 손실)

## 결과

본 ADR codify 결과:
- Sentinel #4 strike #2 trigger 충족 (Issue #607 — 2번째 sample 발견 시 ADR 발의 임계 도달)
- ADR-070 자매 layer 신설 (Codex external worker output verify ↔ Orchestrator self-assertion verify)
- 3-layer coherence (ADR-070 + ADR-071 + ADR-073) cross-ref 확립
- super-class anchor + 2 mechanism enumeration (M1 working tree mutation lag + M2 cross-repo origin lag) + future strike #N append schema
- skill body amend (codeforge:brainstorm Phase 0 verify 의무)
- spec/plan template `pre_lookup_evidence[]` field 신설
- 본 carrier 자체 self-application paradox 시연 (Strike #3 + Strike #4) → mechanism 확장 후보 evidence (M3 Windows shell ref-mangling, M4 continuous race condition during rebase)
- CFP-635 sister Epic (over-questioning) 와 super-class shared, scope disjoint

## Amendments

### Amendment 1 — ADR-082 cross-ref (disjoint 보완 관계, CFP-776)

**문제**: ADR-073 = Orchestrator 가 cross-repo state / assumption 단정 시 verify 의무 (Orchestrator 행위 한정). 그러나 lane agent 가 §9 evidence 작성 / Phase 0 mapping / corpus enumeration 시 write-time semantic truth 를 verify 없이 단언하는 영역 (pattern_count 3 누적, CFP-746/CFP-770) 은 ADR-073 scope 외 — internal lane self-write 미포함.

**결정**: ADR-082 (Write-time self-write verification mandate) 신설로 해당 gap 을 disjoint super-class layer 로 codify. ADR-073 ↔ ADR-082 = **disjoint 보완 관계**:

- **ADR-073** = Orchestrator 행위 한정 (cross-repo state + assumption 기술 시 `git fetch` + `git show origin/main:<path>` direct verify + `verified-via` annotation)
- **ADR-082** = internal lane agent self-write 한정 (§9 evidence / Phase 0 mapping / corpus enumeration write-time 에 작성 값 자체의 사실성 source direct verify)

두 layer 는 verify 대상 / 행위 주체가 disjoint — scope 침범 0. ADR-082 §결정 1 layer disjoint 4-layer 표 (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) 가 공통 anchor. 본 Amendment 는 cross-ref-only — ADR-073 §결정 1-8 / mechanism enumeration 의 의미 변경 없음.

### Amendment 2 — Transition trigger enum + sustained polling expansion (CFP-966)

**문제**: ADR-073 base §결정 1 (CFP-622) + Amendment 1 (CFP-776 ADR-082 cross-ref) 은 Orchestrator 가 cross-repo state / assumption 을 **단정 발화** 하는 순간 (한 turn 내 1회 event) 의 verify 의무를 codify. 그러나 long-running Orchestrator session 안에서 발생하는 **mid-flight parallel race incidence** 영역은 base + Amendment 1 scope 외 — session 시작 시점 (turn 0) state snapshot 이 stale 화 하면서 동일 session 안 후속 turn 의 단정 발화 도 동시 정합 invariant 가 깨진다.

Sentinel evidence (2026-05-18 KST same-day 2/2 occurrence):
- **CFP-953** (first incident): Epic CFP-882 Wave 4 Story-2 진행 시 label-based search (`gh issue list --label parent:CFP-882`) 만 수행 → CFP-932 (실제 Wave 4 Story-2 carrier, label `parent:CFP-699` 만 부착) miss → #953 brainstorm Phase 0/2 + spec PR #624 진행 후 발견 → #953 closed not_planned + spec deprecation PR #625. memory rule 6 신설 carrier (title-based search 의무).
- **CFP-946** (second incident, same day, 11분 gap): Epic CFP-946 brainstorm + Story-A (#957) PR #961 merged `06:42:12Z` → 11분 후 parallel session PR #962 `[CFP-946 option 1]` merged `06:53:30Z` "Closes #946" → Epic #946 CLOSED. Story-B (#958) ArchitectPL spawn 직전 HEAD re-pin 시 #962 검출. Story-B scope 분할 (declaration absorbed by #962 + mechanical layer carry-forward = #963 P2). memory rule 7 신설 carrier (Epic 진행 중 polling 의무).

**결정**: §결정 1 의 verify-before-assert mandate 를 **mid-flight transition state** 영역까지 expansion. 다음 3 요소 신설:

#### Amendment 2 §결정 1-A — Transition trigger enum 3종 (closed set)

Orchestrator (또는 subagent) 가 다음 transition 직전 시점에 추가 verify 의무 발화:

| ID | Transition trigger | 발화 시점 | Verify 의무 |
|----|---|---|---|
| `lane_spawn` | lane 진입 직전 (Requirements / Design / DesignReview / Develop / CodeReview / SecurityTest / IntegrationTest / PMO retro lane spawn) | Agent tool spawn 직전 | Issue body / current CFP context title-based search + Epic state poll + HEAD re-pin (`git ls-remote origin <branch>`) + HEAD compare (`gh api repos/.../compare/<prior>...<current>`) |
| `pr_open` | PR open 직전 (Phase 1 / Phase 2 / retro PR) | `gh pr create` 직전 | 동일 3-step (title-based search + Epic poll + HEAD compare) + sibling Story PR list cross-ref |
| `merge_transition` | PR merge 직전 (`gh pr merge` 직전) + merge 직후 (gate label / phase label transition 직전) | merge command 직전 + 직후 transition action 직전 | 동일 3-step + Epic state final poll (close eligibility check, ADR-077 §결정 4 정합) |

closed enum — 4번째 trigger 추가 시 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합).

#### Amendment 2 §결정 1-B — Cold start session_start 보강

기존 SessionStart hook tier (`templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` + ADR-038 Amendment 2 §결정 9 TodoWrite preload pattern) 는 **turn 0 prompt-injection 단독 layer** — additionalContext 가 first user turn 직전 1회 발화. mid-flight parallel race (CFP-953 / CFP-946 evidence) 차단 영역은 cover 부족.

본 Amendment 2 는 cold start session_start 도 transition trigger 4번째 가상 entry 로 amplify:
- session 첫 turn additionalContext 안 **active CFP context list** + **open Epic state list** + **current branch HEAD vs origin/main delta** 3-item preload 의무 (SessionStart hook tier 위임 — Story-2 carrier `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` mechanical wire)
- additionalContext 안 layer 1 fallback 만 — actual sustained polling = §결정 1-C 영역

#### Amendment 2 §결정 1-C — Sustained in-session polling 의무 mandate (turn-0-only 한계 해소)

base §결정 1 (Orchestrator 단정 발화 시점 verify) + 본 Amendment §결정 1-A (transition trigger 3종) 의 **sustained polling** discipline normative anchor:

- Long-running session 안 **매 transition trigger 직전 HEAD SHA re-pin** 의무 — TodoWrite scratchpad / Story §0 Live Progress / `.claude-work/progress/<KEY>.md` 등 session state cache 가 stale (이미 polling 후 5+ min 경과) 일 가능성 무조건 가정
- mechanical polling source (parallel branch HEAD list + open Epic list + recent merged PR list) = sibling Story-2 CFP-967 mechanical wire (`scripts/check-parallel-work-sentinel.{sh,py}` + workflow event dispatch) 영역
- 본 ADR scope = behavioral directive + declarative anchor (§결정 1-A enum + §결정 1-B cold start ratchet + §결정 1-C polling mandate). actual lint script + workflow yaml + hook json sample = Story-2 carrier 위임 (declaration-only-Wave-1 patterns, ADR-082 §결정 6 + ADR-060 Amendment 10 §결정 24 precedent 답습)

#### Amendment 2 — mechanical_enforcement_actions[] 첫 entry append

본 Amendment 2 가 ADR-073 frontmatter `mechanical_enforcement_actions[]` 의 첫 row entry (`parallel-work-sentinel-pickup`) append 발의 — base + Amendment 1 의 `[]` empty Wave 1 → Amendment 2 의 1-entry warning-tier Wave 1 ratchet (ADR-040 Amendment 3 §결정 7.D self-application 정합).

| Wave | Status | Carrier |
|---|---|---|
| Wave 1 base (declaration mandate) | `mechanical_enforcement_actions: []` | CFP-622 (ADR-073 base, 2026-05-14) |
| Wave 1 + Amendment 1 (ADR-082 cross-ref) | `mechanical_enforcement_actions: []` (unchanged) | CFP-776 (Amendment 1, 2026-05-17) |
| **Wave 1.5 + Amendment 2 (declarative anchor entry)** | `mechanical_enforcement_actions: [parallel-work-sentinel-pickup]` (warning tier) | **CFP-966 (본 Amendment 2, 2026-05-18) — declarative anchor only** |
| Wave 1.6 + Story-2 mechanical wire | (entry unchanged, status warning → blocking-on-pr 자동 승격 trigger 활성) | CFP-967 (Story-2 mechanical wire, sequential — Story-1 merge 후) |
| Wave 2 (recurrence count ≥ 3 자동 승격) | (entry current_tier: blocking-on-pr 전환) | post-CFP-967 follow-up CFP (recurrence.threshold=3 auto-firing) |

#### Amendment 2 — Disjoint scope cross-ref (Edge 3 정합)

본 Amendment 2 는 ADR-082 Amendment 1 (CFP-841 Phase 1 declare — write-time self-write verification scope 2(a) corpus-claim-verify + scope 2(d) cross-plugin-ownership-verify deferred-followup) 과 **disjoint scope**:

- **ADR-082 Amendment 1** = internal lane agent self-write **write-time** semantic truth verify (corpus annotation + cross-plugin ownership) — 작성 값 자체의 사실성 source verify
- **ADR-073 Amendment 2** (본) = Orchestrator **transition state** verify (lane spawn / PR open / merge transition 직전 mid-flight parallel race state poll) — write-time 영역 외, session state cache staleness 영역

ADR-082 §결정 1 layer disjoint 4-layer 표 anchor 정합 — 두 Amendment 가 별 layer 안 ratchet 강화 진행, scope 침범 0건. 본 Amendment 2 본문 자체 안 ADR-082 cross-ref 영역 변조 0 (Amendment 1 disjoint 보완 관계 그대로 보존).

#### Amendment 2 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 2 scope = §결정 1-A/1-B/1-C 강화 방향 only (transition trigger enum 추가 + cold start 보강 + sustained polling mandate). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1 동형 precedent).

### Amendment 3 — worktree-first self-ownership verify 3-tuple (CFP-689)

**문제**: ADR-040 worktree-first normative (Amendment 3·5·6 §결정 7.D 4 evidence-check entry blocking-on-pr) 가 만든 토폴로지 = **multi-worktree distributed local state** (동일 lane branch 가 N 개 isolated worktree `${HOME}/.claude/worktrees/<repo>/cfp-NNN[-suffix]` 에 분산). 산업 표준 4-layer staleness hierarchy (Bazel hermeticity: source tree / network / clock / process) 와 동형이되 **5th layer "spatial dimension (multi-worktree distributed local state)"** 로 확장된 codeforge-specific 도메인. 단일-worktree 멘탈모델 (`C:/workspace/mclayer/<repo>/`) 로는 자기 세션이 dedicated worktree 에서 만든 commit 도 외부 commit 처럼 보인다 — **자기 세션 자체 산출물을 외부 parallel session 으로 오인하는 self-confusion**.

memory rule 6 (title-based search) + rule 7 (Epic state poll) + Amendment 2 transition trigger enum 3종 + cold start session_start 은 **detection layer** only — worktree-first 환경 안 detection 양성 직전 self-ownership verify 선행 layer 가 governance 안 부재. 이 verification layer 부재가 false-positive 의 force-push war / 잘못된 stand-down / 중복 spawn 을 만드는 systemic root.

**Sentinel evidence** (2026-05-19~20 KST single session 3 occurrences, pattern_count 3 reach):

- **Occurrence #1 — CFP-1026 brainstorm STAND-DOWN false-positive** (2026-05-19): Phase 0 4-agent parallel context fetch 직후 본 session 자기 산출물을 외부 work 으로 오인 → STAND-DOWN 발화 → 검증 후 false-positive 확인 → resume.
- **Occurrence #2 — CFP-681 cfp-1014 dup worktree** (2026-05-19~20): RequirementsPL 중복 spawn — authoritative `cfp-681-s2` worktree 의 자기 work commit `f39b221` 을 parallel session 산출물로 mis-flag → dup worktree setup → 검증 후 self-confusion 확인 → dup prune.
- **Occurrence #3 — CFP-681 ArchitectPL Phase 3 자기 commit mis-flag** (2026-05-20): ArchitectPL verdict packet 안 자기 ArchitectAgent commit `00b7d8a` 를 `parallel_session_conflict` 로 mis-flag — **subagent 도 multi-worktree self-confusion 영역에서 보이는 패턴 입증**. Orchestrator 가 subagent verdict 를 final source of truth 로 취급 시 self-confusion contagion (Orchestrator → subagent → Orchestrator 재반영 cycle).

#### Amendment 3 §결정 1-A 추가 — Transition trigger enum 4번째 entry (closed-set ratchet)

Amendment 2 §결정 1-A 의 transition trigger enum 3종 (`lane_spawn` / `pr_open` / `merge_transition`) + cold start `session_start` (Amendment 2 §결정 1-B) 에 **4번째 entry `worktree_lane_spawn`** 추가 (closed-set ratchet 강화, Amendment 2 §결정 1-A precedent 답습):

| ID | Transition trigger | 발화 시점 | Verify 의무 |
|----|---|---|---|
| `lane_spawn` (Amendment 2) | lane 진입 직전 (Requirements / Design / DesignReview / Develop / CodeReview / SecurityTest / IntegrationTest / PMO retro lane spawn) | Agent tool spawn 직전 | Amendment 2 §결정 1-A 3-step (title-based search + Epic poll + HEAD compare) |
| `pr_open` (Amendment 2) | PR open 직전 (Phase 1 / Phase 2 / retro PR) | `gh pr create` 직전 | 동일 3-step + sibling Story PR list cross-ref |
| `merge_transition` (Amendment 2) | PR merge 직전 + merge 직후 gate label / phase label transition | merge command 직전 + 직후 transition action 직전 | 동일 3-step + Epic state final poll |
| **`worktree_lane_spawn` (Amendment 3, 신규)** | **worktree-first lane spawn 직전 (`Agent` tool 호출 prompt 안 worktree path 주입 직전)** | **lane spawn 직전 + subagent verdict `parallel_session_conflict` 발화 직후** | **§결정 1-D self-ownership verify 3-tuple (path-based, 아래)** |

closed enum — 5번째 trigger 추가 시 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). open_extension: false.

#### Amendment 3 §결정 1-D — Self-ownership verify 3-tuple (path-based, 사용자 prompt identity-based 대안 채택)

`worktree_lane_spawn` transition 직전 + subagent verdict `parallel_session_conflict` 발화 시점에 다음 3-tuple verify 의무 (path-based, ResearcherAgent + FeasibilityAgent 통합 권장 채택 — Solo-dev 환경 identity-based 식별력 0 회피):

**3-tuple verify primitive** (atomic group — 3-step 동시 수행, 부분 PASS 허용 fallback rule 동반):

| ID | Verify check | 실행 cmd | PASS 조건 | Fallback rule |
|----|---|---|---|---|
| **(a) cwd ↔ worktree path 일치** | 현재 작업 worktree path 가 git worktree list 안 등록 entry 와 정확 일치 | `git rev-parse --show-toplevel` vs `git worktree list --porcelain` | string equality (path normalize: forward-slash `/` + lowercase drive-letter `c:` `c:/users/...`) | normalize 후 mismatch 시 (a) FAIL → (c) backstop |
| **(b) HEAD lineage ↔ session reflog membership** | HEAD commit lineage 가 본 session reflog 안 단일 선형 (자기 산출물 입증) | `git reflog show <branch> --all` + `git log <commit> --oneline` cross-check | reflog membership = true (본 session 안 commit chain 추적 가능) | long-Phase-gap reflog 90d GC (git default `gc.reflogExpire=90 days`) 시 (b) FAIL → **(a)+(c) 2-source AND fallback** |
| **(c) worktree list + reflog 2-source AND** | `git worktree list --porcelain | grep <branch>` 출력 + reflog 양 source AND 정합 | `git worktree list --porcelain` parse `branch` field + reflog entry exists | 양 source PASS = self-ownership verify TRUE | (a) FAIL OR (b) FAIL OR (c) FAIL 시 → parallel session verdict (memory rule 6/7 detection layer 인계) |

**Edge case handling**:
- **detached HEAD** (branch reflog 없음): `branch` field 부재 → (b) 자동 skip → **(a)+(c) 2-source AND fallback** (PASS 조건 = (a) PASS AND (c) PASS — branch field 없을 시 detached HEAD log line `(detached HEAD ...)` 검증).
- **anonymous worktree** (`branch` field 부재 — `git worktree add --detach` path): self-ownership verify 불가능 영역 → **forcing function**: "anonymous worktree 안 lane spawn 금지" (codeforge worktree convention violation — ADR-040 §결정 1 named worktree mandate 정합). detection 시 즉시 ABORT + named branch worktree 재생성 의무.
- **path normalization**: Windows drive-letter case 변동 (`C:/` vs `c:/`) + slash direction (`/` vs `\`) → canonical form = **lowercase drive + forward-slash** (`c:/users/...`). MSYS2 / Git Bash / WSL / native cmd.exe 전 환경 동형 보장.
- **signed commit GPG** + **CODEFORGE_SESSION_ID env 부재**: 사용자 prompt identity-based 3-tuple (cwd ↔ git config user.email / HEAD author ↔ session identity / `gh pr list head:<branch>`) 영역의 edge — 본 Amendment 3 path-based 채택으로 회피 (identity-based scope OUT, ResearcherAgent + FeasibilityAgent 통합 권장).

#### Amendment 3 §결정 1-E — Subagent verdict re-verify mandate (ADR-082 cross-ref)

Orchestrator 가 subagent verdict 안 `parallel_session_conflict` (또는 동형 발화 — `external_work_detected` / `cross_session_collision` / `stand_down_recommended` 등) 수신 시:

1. **즉시 ground-truth re-verify 의무** — `git worktree list --porcelain` + `git reflog show <branch>` direct execution (subagent 가 이미 수행했더라도 Orchestrator 자기 검증).
2. **subagent verdict ≠ final source of truth** — multi-worktree self-confusion 영역에서는 agent 도 mis-flag 패턴 입증 (Occurrence #3 sentinel evidence — ArchitectPL Phase 3 ArchitectAgent commit `00b7d8a` mis-flag). Subagent verdict 는 advisory annotation 만 — Orchestrator 가 self-ownership verify 3-tuple 결과를 ground truth 채택.
3. **3-tuple PASS (self-ownership TRUE) 시**: subagent verdict 의 `parallel_session_conflict` REJECT + continue (자기 산출물 정상 진행). FIX Ledger row append (`subagent_misflag_self_confusion` reason code) — Orchestrator 단독 §10 append 독점 (fix-event-v1 contract).
4. **3-tuple FAIL (self-ownership FALSE) 시**: subagent verdict 의 `parallel_session_conflict` 채택 + memory rule 6/7 detection layer 절차 진행 (title-based search + Epic state poll + HEAD compare).

**ADR-082 §결정 1 layer disjoint 4-layer 표 cross-ref 의무**:

- **ADR-082** = internal lane agent self-write **write-time** semantic truth verify (corpus annotation + cross-plugin ownership) — 작성 값 자체의 사실성 source verify
- **ADR-073 Amendment 3** (본) = Orchestrator **worktree-first self-confusion** verify (worktree_lane_spawn transition 직전 + subagent verdict re-verify) — 자기 산출물 영역의 verify 확장 (lane agent self-write 가 만든 commit 의 self-ownership verify 영역)

두 layer 는 verify 대상이 disjoint — ADR-082 = 작성 값의 source verify / 본 Amendment 3 = commit ownership 의 worktree topology verify. scope 침범 0. agent verdict packet `parallel_session_conflict` mis-flag 영역은 본 Amendment 3 의 §결정 1-E re-verify mandate 가 직접 cover (ADR-082 §결정 1 layer disjoint anchor 와 양립).

#### Amendment 3 §결정 1-F — Disjoint axis with #983 (reflog membership 1 bit)

본 Amendment 3 의 self-confusion sub-domain 은 #983 후보 (a)/(b) 의 real parallel cross-session collision sub-domain 과 **disjoint axis** (reflog membership 1 bit signal):

| 차원 | 진짜 parallel (cross-session conflict, #983 후보 (a)/(b) 영역) | self-confusion (within single session, **본 Amendment 3 영역**) |
|---|---|---|
| reflog membership | **본 세션 reflog 에 없는 commit** + 다른 worktree lineage 가 origin 에 독립 존재 | **본 세션 skeleton → lane commit 단일 선형** 이 multi-worktree 로 흩어진 산출물 |
| 1-bit signal | reflog membership = **false** | reflog membership = **true** |
| 적용 governance | memory rule 6/7 + ADR-073 Amendment 2 (detection layer) | **본 Amendment 3 (verification layer — detection 직전 self-ownership verify 선행)** |
| 처리 액션 | stand-down / re-spawn / merge-order 의뢰 | continue (자기 산출물 정상 진행) + subagent verdict reject |
| Carrier ESC | #983 (별 Story carrier, real parallel cross-session collision 영역) | CFP-689 (본 Story, plugin-codeforge#1038 carrier) |

본 Amendment 3 = #983 P1 ESC body 안 후보 (c) "ADR-073 Amendment 3 — shared workdir collision worktree-first invariant 강화" 의 정식 carrier. #983 후보 (a)/(b) (real parallel cross-session collision sub-domain) 는 별 Story carrier 영역 — 본 Amendment 3 scope 외, disjoint axis 명시 invariant.

#### Amendment 3 — Wave 1 declaration / Wave 2 mechanical wire 분리 (CFP-966/967 precedent 답습)

본 Amendment 3 = **declarative anchor only** (Wave 1, declaration-only, ADR-064 §결정 1 CFP scope unitary 정합). CFP-966 (declarative anchor) → CFP-967 (mechanical wire merged 2026-05-19) chain 완결 precedent 답습:

| Wave | Status | Carrier |
|---|---|---|
| Wave 1 Amendment 3 (declarative anchor) | `mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify]` (2 entry, warning tier, status: deferred-followup) | **CFP-689 (본 Amendment 3, 2026-05-20) — declarative anchor only** |
| Wave 2 sibling Story-2 mechanical wire | (entry status: deferred-followup → warning 전환) | **TBD 별 sub-CFP carrier** (`scripts/check-worktree-self-ownership.sh` + `scripts/lib/check_worktree_self_ownership.py` Python SSOT + `templates/github-workflows/worktree-self-ownership-verify.yml` + `.github/workflows/` byte-identical self-app + `templates/.claude/hooks/PreToolUse-worktree-self-ownership.json.sample` + `tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats` + label-registry-v2 신규 entry `hotfix-bypass:worktree-self-ownership-verify`) |
| Wave 3 (recurrence count ≥ 3 자동 승격) | (entry current_tier: warning → blocking-on-pr 전환) | post-Wave-2 follow-up CFP (recurrence.threshold=3 auto-firing — pattern_count 3 already reached 2026-05-19~20 sentinel evidence) |

#### Amendment 3 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 3 scope = §결정 1 본문 + Amendment 1+2 강화 방향 only (transition trigger enum 4번째 entry append + self-ownership verify 3-tuple 신설 + subagent verdict re-verify mandate). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2 동형 precedent). ADR-064 §self-application top-down ratchet 정합 (강화 방향 only — verify scope 확장).

### Amendment 4 — ADR-085 cross-ref disjoint complement (verify axis ↔ coordination axis, CFP-1041)

**문제**: ADR-073 (base + Amendment 1+2+3) 은 Orchestrator 행위 영역에서 cross-repo state / assumption verify (verify axis) 의무를 codify. 그러나 복수 Claude Code session 이 동일 repository / Story / branch 에서 동시 작업할 때 ownership 결정 / 분담 / handoff coordination (coordination axis) 영역은 ADR-073 scope 외 — verify 가 모두 충족되어도 ownership 미결정 시 parallel race 발생, ownership 결정 후에도 verify 미수행 시 false claim 가능 (둘 다 필요한 orthogonal layer).

**결정**: ADR-085 (Multi-session collaboration protocol — `active_sessions[]` + lane-entry sentinel + rebase merge 우선 + handoff baton transfer) 신설로 coordination axis layer 추가. ADR-073 ↔ ADR-085 = **disjoint complement** 관계:

- **ADR-073** = Orchestrator cross-repo state / assumption verify 한정 (verify axis, post-hoc verify)
- **ADR-085** = 복수 session ownership / 분담 / handoff coordination 한정 (coordination axis, pre-hoc cross-session)

ADR-085 §결정 1 5-layer disjoint 표가 공통 anchor (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설). 본 Amendment 4 는 §결정 1 lane-entry sentinel 4-step polling 의 **4번째 source** (`active_sessions_check`) cross-ref-only append — 본문 §결정 1-8 + Amendment 1-3 mechanism 의미 변경 0 (ADR-085 §결정 3 cross-ref-only Amendment, ADR-082 Amendment 1 ADR-073 cross-ref pattern verbatim 답습).

post-rebase amendments[] sequence = [1, 2, 3 (CFP-689 worktree-first self-ownership), 4 (본 CFP-1041 ADR-085 coordination)] consecutive. 본 carrier 진행 중 origin/main 으로 CFP-689 (PR #1043, sibling escalation #1038 actual carrier) advance — dogfooding ADR-085 본 carrier 가 codify 하는 `parallel_session_shared_workdir_collision` pattern (9th+ parallel race lineage single session evidence: CFP-953/946/949/932/954/991/967/1014 + 본 CFP-1041 진행 중 CFP-689 race) verbatim 시연.

#### Amendment 4 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 4 scope = cross-ref-only append (mechanism 의미 변경 0, scope 확장 / 강화 0). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3 동형 precedent). ADR-064 §self-application top-down ratchet 정합.

## 관련 파일

- `docs/adr/ADR-RESERVATION.md` — row 73 (CFP-622)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — disjoint super-class (Amendment 1 cross-ref, CFP-776)
- `CLAUDE.md` — "결정 원칙" section + "Verify-before-trust 4-layer governance" 단락 ADR-073 cross-ref
- `skills/codeforge-brainstorm/SKILL.md` — Phase 0 자기 적용 의무 sub-section
- `.claude-plugin/plugin.json` — version bump (CFP-622 carrier MINOR)
- `CHANGELOG.md` — 5.53.0 entry + Strike #3 + Strike #4 sub-sections
- `mclayer/marketplace/.claude-plugin/marketplace.json` — codeforge entry mirrored field sync (PR1 #109 merged)
- `mclayer/codeforge-internal-docs/wrapper/{specs,plans,stories,change-plans}/CFP-622-*.md` — Story carrier (PR3 TBD)
- `mclayer/codeforge-internal-docs/wrapper/templates/{spec,plan}.md` — pre_lookup_evidence[] field 신설
- **Amendment 2 (CFP-966, 2026-05-18) 관련**:
  - `docs/evidence-checks-registry.yaml` — `parallel-work-sentinel-pickup` 신규 entry (warning tier, declaration-only-Wave-1, recurrence count 2 / threshold 3 / promotion_trigger auto_blocking)
  - `docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md` — narrative SSOT (sentinel batch + escalation matrix)
  - `docs/orchestrator-playbook.md` §3.5 — lane spawn 직전 polling 의무 enum + HEAD compare pattern
  - `docs/parallel-work/section-ownership.yaml` — ADR-073 file lock row append (Amendment 2 신설 carrier)
  - `mclayer/codeforge-internal-docs/wrapper/stories/CFP-966.md` — Story-1 declarative anchor (본 Amendment 2 carrier)
  - `mclayer/codeforge-internal-docs/wrapper/change-plans/CFP-966.md` — Change Plan (declarative)
  - **sibling Story-2**: CFP-967 mechanical wire (`scripts/check-parallel-work-sentinel.{sh,py}` + `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` + `templates/github-workflows/parallel-work-sentinel-check.yml` + `tests/bats/test_parallel_work_sentinel.bats`)
- **Amendment 3 (CFP-689, 2026-05-20) 관련**:
  - `docs/evidence-checks-registry.yaml` — `worktree-self-ownership-verify` 신규 entry (warning tier, declaration-only-Wave-1, recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, sibling_dependencies: [CFP-689, TBD-Wave-2-sub-CFP])
  - `docs/domain-knowledge/domain/orchestrator-discipline/worktree-self-ownership-verify.md` — narrative SSOT 신설 (DomainAgent 지식 공백 해소 — Multi-worktree distributed local state 5th layer staleness + disjoint axis + 3 occurrences sentinel evidence + path-based 3-tuple verify primitive + edge case + subagent verdict re-verify mandate)
  - `docs/parallel-work/section-ownership.yaml` — ADR-073 file lock row append (Amendment 3 신설 carrier, Amendment 2 row CFP-966 와 section disjoint)
  - `CLAUDE.md` "Verify-before-trust 4-layer governance" 단락 — Amendment 3 (CFP-689) 1문장 inline append + `mechanical_enforcement_actions[]` 2 entry mention (ADR-012 cap 320 line budget verified — 315 → ~318 lines 예상)
  - `mclayer/codeforge-internal-docs/wrapper/stories/CFP-689.md` — Story-1 declarative anchor (본 Amendment 3 carrier — RequirementsPL 7-agent synthesis §2-6 + ArchitectAgent §3/§7/§11 final write)
  - `mclayer/codeforge-internal-docs/wrapper/change-plans/CFP-689.md` — Change Plan (declarative)
  - **sibling Story-2 (TBD 별 sub-CFP)**: mechanical wire (`scripts/check-worktree-self-ownership.{sh,py}` + `templates/.claude/hooks/PreToolUse-worktree-self-ownership.json.sample` + `templates/github-workflows/worktree-self-ownership-verify.yml` + `tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats` + label-registry-v2 신규 entry `hotfix-bypass:worktree-self-ownership-verify`)
  - **#729 future Amendment 4 disjoint 영역**: plugin-codeforge#729 (ADR-073 "Amendment 1" title 표기 — 슬롯 충돌, Amendment 4 로 재배정 의무, ContinuityAgent CRITICAL 발견). Glob false negative P1 영역 — 본 Amendment 3 self-ownership verify 3-tuple 영역과 section disjoint 보장 (Amendment 4 = `Glob false negative` 별 §결정 영역).

## 해소 기준

N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책).
