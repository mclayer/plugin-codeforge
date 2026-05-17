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
related_stories:
  - CFP-622  # carrier
  - CFP-776  # Amendment 1 — ADR-082 cross-ref (disjoint 보완)
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
related_files:
  - CLAUDE.md  # 결정 원칙 section + ADR list 영역 cross-ref
  - skills/codeforge-brainstorm/SKILL.md  # verify 의무 amend
  - <internal-docs>/wrapper/templates/spec.md  # pre_lookup_evidence[] field 신설
  - <internal-docs>/wrapper/templates/plan.md  # pre_lookup_evidence[] field 신설
is_transitional: false
mechanical_enforcement_actions: []
# Wave 1 = behavioral directive only (Orchestrator self-discipline forcing function).
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

## 관련 파일

- `docs/adr/ADR-RESERVATION.md` — row 73 (CFP-622)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — disjoint super-class (Amendment 1 cross-ref, CFP-776)
- `CLAUDE.md` — "결정 원칙" section ADR-073 cross-ref
- `skills/codeforge-brainstorm/SKILL.md` — Phase 0 자기 적용 의무 sub-section
- `.claude-plugin/plugin.json` — version bump (CFP-622 carrier MINOR)
- `CHANGELOG.md` — 5.53.0 entry + Strike #3 + Strike #4 sub-sections
- `mclayer/marketplace/.claude-plugin/marketplace.json` — codeforge entry mirrored field sync (PR1 #109 merged)
- `mclayer/codeforge-internal-docs/wrapper/{specs,plans,stories,change-plans}/CFP-622-*.md` — Story carrier (PR3 TBD)
- `mclayer/codeforge-internal-docs/wrapper/templates/{spec,plan}.md` — pre_lookup_evidence[] field 신설

## 해소 기준

N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책).
