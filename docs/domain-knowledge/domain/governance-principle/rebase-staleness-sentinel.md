---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: rebase-staleness-sentinel
title: Rebase staleness sentinel — parallel-session-merge-stream-main-advance-during-lane-flow pattern + mitigation matrix (CFP-1588 F-DR-011)
status: Active
date: 2026-05-25
updated: 2026-05-25
carrier_story: CFP-1588
parent_carrier: CFP-1523 (F-DR-011 advisory post-carrier — strict mode rebase staleness sentinel codify)
tags:
  - rebase-staleness
  - parallel-session-merge-stream
  - main-advance-during-lane-flow
  - sentinel-pattern
  - mitigation-matrix
  - super-class-codification
related_adrs:
  - ADR-040       # Worktree convention — multi-worktree isolated workspace (sentinel 발생 환경)
  - ADR-050       # Parallel epic coordination — Epic-level scope manifest + conflict label coordination
  - ADR-054       # Story 작성 의무 + doc-only fast-path — 본 codify 형식
  - ADR-073       # Orchestrator verify-before-assert — lane-entry sentinel 4-step polling (Amendment 2~4)
  - ADR-082       # Write-time self-write verification mandate — author claim verify (write-time anchor)
  - ADR-085       # Multi-session collaboration protocol — active_sessions[] + lane-entry sentinel + rebase merge 우선
related_stories:
  - CFP-1588      # 본 codify carrier (FU-1523-3 묶음 F-DR-011)
  - CFP-1523      # parent carrier (advisory deferred)
  - CFP-953       # 1st occurrence — duplicate incident + memory rule 6 신설 (title-based search)
  - CFP-946       # 2nd occurrence — parallel race + rule 7 신설 (Epic state poll)
  - CFP-949       # 4th occurrence — sub-issue scope polling gap (Rule 7 refinement)
  - CFP-1014      # 10th parallel race — Story-5 별 session canonical
  - CFP-1334      # CFP-1334 parallel race 2회 19+ commits sentinel
  - CFP-1403      # mid-flight sibling conflict — force-rebase clean pattern
deferred_followup_cfps:
  - FU-1588-R     # REALIZED by CFP-2784 (2026-07-22) — script+workflow+registry-row+label 동시 배선 (§규칙4 scope 실현)
is_transitional: false
sunset_criteria: |
  N/A — permanent governance sentinel (ADR-058 §결정 5 정합).
  본 sentinel = parallel session merge stream 환경 inherent race window 영역 SSOT.
  pattern_count 6+ super-class evidence (CFP-953/946/949/1014/1334/1403) 가
  안정적 `normative` ("강제 규칙") anchor 정합. 환경 자체 (multi-session distributed work) 가
  사라지지 않는 한 sunset 영역 외.
---

# Rebase staleness sentinel — parallel-session-merge-stream-main-advance-during-lane-flow pattern

## 정의

본 file = codeforge governance corpus 의 **`parallel-session-merge-stream-main-advance-during-lane-flow`** sentinel pattern SSOT. multi-session distributed work 환경 (복수 Orchestrator 세션 + worktree-first isolated workspace + Story-scoped feature branch) 에서 lane flow 진행 중 main branch advance (sibling session merge) 가 발생할 때 rebase staleness 가 race window 영역에서 누적되는 정형 pattern.

핵심 정의 3종:

- **Pattern name**: `parallel-session-merge-stream-main-advance-during-lane-flow` — super-class identifier (sentinel pattern grep handle)
- **Window**: lane spawn → PR open → CI gate wait → admin merge 사이 시점 (사용자 explicit handoff 부재 환경)
- **Mitigation**: 4-tier closed-enum (auto-merge / pre-emptive rebase / wait + retry / handoff baton transfer)

**Sentinel 위치**: `governance-principle/` 영역 (ADR-085 Multi-session collaboration protocol 의 narrative SSOT companion). ADR sentinel 영역 아닌 domain-knowledge sentinel 채택 — 이미 ADR-073 Amendment 2~4 가 mechanical layer carrier 영역 codify 완료 (declarative_layer 본 file 만, ADR-060 framework Wave 1 → Wave 2 wire pattern 답습).

## 컨텍스트

### Origin (pattern_count 6+ super-class evidence)

본 sentinel = pattern_count 6+ 누적 super-class — 다음 6 known Story 단발 (single-session lineage) :

| # | CFP | KST date | Sub-class | Resolution |
|---|---|---|---|---|
| 1 | CFP-953 | 2026-05-18 | duplicate incident (label-only check 불충분) | memory rule 6 신설 (title-based search) |
| 2 | CFP-946 | 2026-05-18 | parallel race (Story-A merged) | memory rule 7 신설 (Epic state poll) |
| 3 | CFP-949 | 2026-05-18 | sub-issue scope polling gap | rule 7 refinement (sub-issue layer polling 의무) |
| 4 | CFP-1014 | 2026-05-20 | Story-5 별 session canonical (10th parallel race) | rule 7 stale-source 정확 사례 |
| 5 | CFP-1334 | 2026-05-23 | parallel race 2회 19+ commits | reset+re-apply strategy / strict head-up-to-date loop |
| 6 | CFP-1403 | 2026-05-24 | mid-flight sibling conflict | force-rebase clean pattern (phase-gate 3 gate label 정합) |

각 occurrence 의 ROOT cause = **lane flow 진행 중 main branch advance** (sibling session merge stream). worktree-first invariant 정합 환경 inherent — single-session sequential 환경에서는 재현 불가 영역.

### Cross-reference (ADR-085 / ADR-073 / ADR-082 multi-layer governance)

- **ADR-085** (Multi-session collaboration protocol) §1 — `active_sessions[]` field + lane-entry sentinel + rebase merge 우선 `normative` ("강제 규칙") 3-pillar anchor. 본 sentinel = ADR-085 coordination axis 의 sentinel pattern instance.
- **ADR-073 Amendment 2~4** (Orchestrator verify-before-assert) §결정 1 — transition trigger enum 4-set (`lane_spawn` / `pr_open` / `merge_transition` / `worktree_lane_spawn`) + lane-entry sentinel 4-step polling (title-search / epic-state-poll / head-compare-sibling-commits / active_sessions_check). 본 sentinel 의 verify axis layer.
- **ADR-082 §결정 1** (Write-time self-write verification mandate) — author claim verify (write-time anchor). 본 sentinel 발생 시 stale local main checkout state 회피 forcing function 영역.

## 핵심 규칙

### 규칙 1 — sentinel detection 4-source (ADR-073 Amendment 4 폴링 enum 정합)

매 lane flow transition 직전 (lane spawn / PR open / admin merge) Orchestrator 의무 4-source polling:

| Source | Mechanism | Detection signal |
|---|---|---|
| `title-search` | `gh pr list --search "head:<branch>"` + Story title text grep | 동일 Story scope 의 별 session PR 발견 시 = race window 진입 |
| `epic-state-poll` | `gh issue view <epic-id> --json state,body` (siblings = Epic body scope_manifest CFP ref 파싱) | Epic state transition (open → closed) 또는 body 내 sibling CFP ref 감지 시 = scope drift |
| `head-compare-sibling-commits` | `git -C <worktree> fetch origin main && git log HEAD..origin/main --oneline` | sibling commit 누적 N >= 1 시 = rebase staleness 진입 |
| `active_sessions_check` (ADR-085) | Story Issue body `active_sessions[]` field traverse | 같은 branch 안 다른 git_identity entry 발견 시 = collaboration channel 활성 |

4-source AND 검증 (1+ source signal 발생 = race window 진입, defensive 측 분류).

### 규칙 2 — Mitigation 4-tier closed-enum

race window detection 후 다음 4 mitigation 중 1 선택 (선택 기준 = lane flow phase + race window 깊이):

| # | Mitigation | When applicable | Procedure |
|---|---|---|---|
| 1 | **auto-merge** | Phase 1 PR + CI gate 미진입 + sibling commit ≤ 2 | `gh pr merge --auto --rebase` — main advance 시 rebase 자동 + CI 재실행. 본 CFP-1403 force-rebase clean pattern |
| 2 | **pre-emptive rebase** | Phase 2 PR + CI gate 진입 후 + sibling commit ≥ 3 | `git -C <worktree> fetch origin main && git -C <worktree> rebase origin/main` + force-push + CI 재대기. CFP-1334 reset+re-apply strategy |
| 3 | **wait + retry** | admin merge 직전 + sibling PR pre-merge window 진행 중 | `gh pr checks --watch` + sibling PR merge 완료 후 본 PR pre-merge polling (strict head-up-to-date loop, CFP-1334 답습) |
| 4 | **handoff baton transfer** (ADR-085 §결정 5) | 별 session 가 같은 branch 활성 발견 + 작업 분담 가능 | Story Issue body comment `[handoff]` prefix + 작업 boundary 명시 + 별 session 가 후속 phase 이어받음 (CFP-1014 / CFP-777 별 session canonical pattern) |

**우선순위** (default 결정 분기): 1 → 2 → 3 → 4. 환경 contraint 시 상위 mitigation 채택 우선 (rebase < wait < handoff cost).

### 규칙 3 — Window 영역 안 차단 actions (negative guard)

race window 진입 직후 다음 actions 차단:

- ❌ **force-push without pre-emptive rebase**: ancestry corruption 영역 (CFP-991 / CFP-1014 evidence)
- ❌ **direct main push**: ADR-024 §결정 1 main 직접 push 금지 invariant
- ❌ **silent skip of CI gate**: phase-gate-mergeable required check + ADR-113 admin merge pre-flight gate 5-step procedure 정합 (CFP-1522)
- ❌ **wholesale-mirror without ImpactReport diff sanity check**: ADR-076 Amendment 3 §결정 3 result_fidelity_binding 정합 (CFP-900)

### 규칙 4 — Mechanism layer cross-ref (declarative_layer 본 file / mechanical wire = Wave 2 별 sub-CFP)

본 file = declarative_layer SSOT only (ADR-060 framework Wave 1 → Wave 2 wire pattern 답습). mechanical wire (rebase staleness lint script + workflow + bats fixture + label-registry-v2 hotfix-bypass family member) = FU-1588-R 별 sub-CFP carrier 영역.

mechanical wire 후보 SSOT:

- `scripts/check-rebase-staleness-sentinel.sh` (warning tier — lane spawn 직전 4-source polling 실행 + sibling commit count)
- `templates/github-workflows/rebase-staleness-detection.yml` (PR-open + workflow_dispatch trigger)
- `docs/evidence-checks-registry.yaml` row append (`rebase-staleness-sentinel` entry status: deferred-followup → warning)
- `hotfix-bypass:rebase-staleness-sentinel` label family member append (label-registry-v2 MINOR bump)

## 경계

### Scope in (본 sentinel 적용 영역)

- multi-session distributed work 환경 (복수 Orchestrator 세션 + worktree-first isolated workspace + Story-scoped feature branch)
- lane flow 진행 중 main branch advance (sibling session merge stream)
- pattern_count 6+ super-class evidence (CFP-953/946/949/1014/1334/1403)
- 4-source polling detection (title-search / epic-state-poll / head-compare-sibling-commits / active_sessions_check)
- 4-tier mitigation closed-enum (auto-merge / pre-emptive rebase / wait + retry / handoff baton transfer)

### Scope out (본 sentinel 영역 외)

- **ADR 신설 0** — 본 carrier (CFP-1588) = doc-only fast-path (ADR-054), 별 ADR Amendment 0건 (declarative_layer 본 file 만)
- **single-session sequential 환경 N/A** — 재현 불가 영역 (multi-session distributed work 환경 inherent)
- **mechanical wire (lint script + workflow + bats fixture)** = FU-1588-R 별 sub-CFP carrier (declarative_layer 본 file 만)
- **ADR-085 본문 변경 0건** — 본 sentinel = ADR-085 coordination axis 의 narrative SSOT companion (ADR 본문 무변경 invariant)
- **ADR-073 본문 변경 0건** — 본 sentinel = ADR-073 verify axis 의 narrative SSOT companion (4 Amendment cumulative cover)
- **force-push procedure 본 sentinel 외** — ADR-040 §결정 1 worktree-first invariant + ADR-024 §결정 1 main push 차단 별 mechanism layer
- **codeforge-deploy / deploy-review lane 영역 외** — production cutover sentinel = ADR-072 + ProductionEvidenceDeputy 별 mechanism

## 관련 ADR

- **ADR-040** (Worktree convention) — multi-worktree isolated workspace (sentinel 발생 환경 baseline)
- **ADR-050** (Parallel epic coordination) — Epic-level scope manifest + conflict label coordination (sentinel detection 보조 layer)
- **ADR-054** (doc-only fast-path) — 본 carrier (CFP-1588) classification 근거 (SSOT 문서 변경 + src/tests 무변경)
- **ADR-058** (ADR sunset criteria mandate) §결정 5 — `is_transitional: false` permanent governance sentinel rationale
- **ADR-073** (Orchestrator verify-before-assert) Amendment 2~4 — transition trigger enum 4-set + lane-entry sentinel 4-step polling (verify axis carrier)
- **ADR-082** (Write-time self-write verification mandate) §결정 1 — stale local main checkout state 회피 forcing function (write-time anchor)
- **ADR-085** (Multi-session collaboration protocol) — `active_sessions[]` + lane-entry sentinel + rebase merge 우선 `normative` 3-pillar anchor (coordination axis carrier, 본 sentinel = narrative SSOT companion)

## 변경 이력

| 일자 (KST) | 변경 | Carrier | 비고 |
|---|---|---|---|
| 2026-07-22 | mechanical wire 배선 (script+py+workflow쌍+registry entry+label member+inventory bijection+consumer 전파) + 4-source polling detection 정정 (표 4행) | CFP-2784 | FU-1588-R 실현체(Wave 2). declarative_layer(CFP-1588) 위 mechanical wire. warning-tier 비차단. |
| 2026-05-25 | 신설 (rebase staleness sentinel SSOT — pattern_count 6+ super-class evidence + 4-source polling detection + 4-tier mitigation closed-enum + mechanism layer cross-ref) | CFP-1588 | parent_carrier CFP-1523 F-DR-011 advisory post-carrier (deferred → 본 codify 활성). 6 occurrence super-class (CFP-953/946/949/1014/1334/1403) 정합. declarative_layer 본 file 만 (mechanical wire = FU-1588-R 별 sub-CFP carrier). ADR-085 + ADR-073 + ADR-082 narrative SSOT companion (3 ADR 본문 변경 0건). |
