---
kind: domain_fact
type: domain-knowledge
area: orchestrator-discipline
topic_slug: mid-flight-marker-provenance
title: "Mid-flight artifact-level provenance marker — owner/kst/status 3-tuple + CI-visibility 3-class boundary"
status: Active
updated: 2026-07-19
tags:
  - mid-flight-marker
  - provenance
  - freshness
  - session-handoff
  - artifact-level
  - ci-visibility-boundary
  - honest-ceiling
  - advisory
  - cfp-2761
domain: orchestrator-discipline
owner_adr: ADR-085-Amendment-2
sibling_cfp:
  - CFP-2761  # carrier (mid-flight artifact-level marker convention + Phase 2 wire)
  - CFP-777   # root_cause_class N=3 lineage — 세션 handoff 재구동 금지 / handoff normative
  - CFP-991   # root_cause_class N=3 lineage — 병렬 session race
  - CFP-2190  # root_cause_class N=3 lineage — mid-flight 산출물 stale (면제선언 + placeholder verdict + untracked ADR draft)
---

# Mid-flight artifact-level provenance marker

ADR-085 §결정 10 (Amendment 2, CFP-2761, 2026-07-19 KST) 의 narrative SSOT. 세션이 순차 교대(중단→재개) 또는 병렬 인계될 때, 이전 세션의 **미완(mid-flight) 산출물**에 "어느 세션 / 언제 / 확정(final) vs 잠정(provisional)" 표식이 없어 후속 세션이 매번 재판정하는 도메인 공백을 **artifact-level provenance marker** 관례로 codify 한다. 세션-레벨(ADR-085 §결정 2/5/6/7)과 **disjoint 한 산출물-레벨 축**.

## 정의

### 마커 3-tuple (closed-set)

mid-flight 산출물에 부착하는 인라인 provenance 마커:

```
<!-- mid-flight: owner=<git_identity>[|worktree=<path>]; kst=<YYYY-MM-DDTHH:MM:SS+09:00>; status=<draft|provisional|final> -->
```

| 필드 | 의미 | source |
|---|---|---|
| `owner` | 산출물을 만든 세션의 git_identity (ADR-085 §결정 2 `active_sessions[].git_identity` 와 정합 — 별도 identity 체계 신설 금지). solo-dev 식별력 보강 위해 `worktree` 조합 권장 | ADR-085 §결정 2 / ADR-073 Amendment 3 path-based 선례 |
| `kst` | 마커 각인 시각, KST +09:00 ISO 8601 zoned strict | ADR-079 |
| `status` | **closed-set {draft, provisional, final}** — 산출물 확정도 | ADR-085 §결정 10 |

### E1 legacy default

마커 **부재** 산출물 = `provisional` 간주 (ADR-085 §결정 2 `active_sessions: []` default 패턴 답습). 즉 표식이 없으면 "잠정"으로 취급 — 후속 세션이 재판정 후보로 본다.

## 컨텍스트

### 동인 — root_cause_class N=3

세션-레벨 machinery(ADR-085 §결정 2 active_sessions[] / §결정 5 handoff baton / §결정 6 heartbeat / §결정 7 subagent self-confusion)는 **세션**은 표식하나 **산출물**은 공백이다. 이 공백이 3회 재현 (ADR-045 §D-9 threshold N=2 초과):

- **CFP-777** — 세션 handoff 재구동 금지 / handoff normative (이전 세션 산출물 재판정).
- **CFP-991** — 병렬 session race (누가 소유한 미완 산출물인가 불명).
- **CFP-2190** — mid-flight 산출물 stale (면제선언 stale + placeholder verdict 무기록 + untracked ADR draft). 본 관례의 직접 source.

### 대상 5유형 + CI-visibility 3-class boundary

마커 관례는 관측면별로 검출 경로가 다르다 (단일 "grep 산출물" 가정 폐기). mid-flight 산출물 5유형과 CI 관측면 3분류:

| # | 유형 | 예시 | 관측면 class | CI 검출 경로 |
|---|---|---|---|---|
| 1 | 작업 단위 초안 | 커밋된 md/스크립트 초안 | **tracked content** (PR-time workflow) | committed 파일 인라인 마커 직접 스캔 |
| 2 | lane 면제(N/A) 선언 | 커밋된 registry/Story N/A 선언 | **tracked content** | committed content N/A-token anchor 스캔 |
| 3 | dispatch placeholder | 커밋된 Story/verdict placeholder (미기록 verdict) | **tracked content** | committed content placeholder-token anchor 스캔 |
| 4 | 미머지 worktree·branch | 로컬 worktree/branch | **local-state probe** (`workflow: null` hook-only) | `git worktree list --porcelain` + reflog path-based 3-tuple (ADR-073 Amendment 3) — SessionStart/PreToolUse hook 표면 |
| 5 | untracked ADR draft | 버전관리 밖 `archive/adr/ADR-NNN-*.md` 초안 | **tracked anchor (staleness proxy — narrow)** | ADR-RESERVATION 예약 row `status` + `reserved_at`/`reservation_date` age proxy 만 |

## 핵심 규칙

1. **owner ↔ git_identity 정합** — 마커 owner 는 ADR-085 §결정 2 active_sessions[] 의 git_identity 와 동일 체계. 별도 identity 신설 금지.
2. **kst = ADR-079 KST +09:00 zoned strict** — 로컬 시각·UTC 혼용 금지.
3. **status = closed-set {draft, provisional, final}** — 이 3값 외 토큰 금지. 파싱 idempotency + enum invariant.
4. **advisory / no-auto-skip** — 마커 = advisory provenance (기계 gate 아님). `status ≠ final` = 후속 세션에 "재판정 후보" 신호일 뿐, 자동 skip/차단 **없음**. 전량 warning-tier, branch-protection 7-tuple 무변경.
5. **Wave 1 declarative / Wave 2 mechanical** — Wave 1 = convention codify (본 문서 + ADR-085 §결정 10 + `templates/story-page-structure.md` 마커 필드). Wave 2 (CFP-2761 Phase 2) = stale-marker lint 5유형 discriminating fixture (`mid-flight-marker-stale`) + ADR-085 §결정 8 mechanical_enforcement_actions[] 2-check(active-sessions-presence + lane-entry-ownership-verify) deferred-followup → warning promotion + ADR-073 Amendment 21 worktree-self-ownership-verify(유형#4) Wave 2 activation.

## 경계

honest-ceiling (ADR-151 / ADR-154 / ADR-157 상속) — 본 관례가 **주장하지 않는** 것:

- **presence ≠ truth** — 정적 마커 presence 검출 ≠ 산출물 실제 확정여부 truth. 거짓-final(내용은 미완인데 `status=final` 각인) 은 정적 lint 로 검출 불가.
- **유형#5 narrow** — untracked ADR draft 는 버전관리 밖이라 초안 파일 인라인 마커가 fresh clone / 다음 세션 / CI 에 **안 보인다**. 정직히 주장 가능한 것 = ADR-RESERVATION 예약 row 의 `status` + age proxy 만 (owner/kst provenance **미주장** — 예약 row 스키마에 owner/kst 필드 부재). "lint 가 untracked ADR 마커 전량 검출" hard-claim **부재**.
- **예약-전 window 미커버** — 예약 row 부재 초안(ADR-050 reserve-before-create convention 위반 / 예약 전 생성) = 미커버. "모든 untracked 초안 ↔ 예약 row" 는 invariant 가 아니라 **convention-dependent** (ledger race 선례 CFP-1041 vs CFP-689 가 위반 실증).
- **유형#4 hook-only** — 미머지 worktree 는 local-state probe(hook 표면, `workflow: null`). fresh-checkout PR runner 는 로컬 worktree 를 미관측 → PR-time CI near-vacuous(CFP-2692 상속). byte-identical PR workflow 를 생성하면 always-green hollow → **미생성**(anti-hollow, ADR-073 Amendment 20 reconciled end-state mirror). hook-delivered warning-tier 가 실 enforcement 표면.
- **silent-green ≠ silent-fallback ≠ honest-degrade 3-way** (ADR-154) — empty-target → honest-degrade exit(silent-green 금지), unknown-input → fail-closed exit 2/3.
- **disjoint from session-level** — 본 축(artifact-level)은 ADR-085 §결정 2/5/6/7(session-level)과 disjoint 보완. 두 축 모두 필요.

## 관련 ADR

- **ADR-085 §결정 10 (Amendment 2, CFP-2761)** — 본 관례 home (coordination axis artifact-level). marker 3-tuple + CI-visibility 3분류 + honest-ceiling SSOT.
- **ADR-073 Amendment 3 + Amendment 21** — 유형#4(미머지 worktree) worktree-self-ownership-verify path-based 3-tuple (verify axis, local-state). Amendment 21 = Wave 2 mechanical activation, `workflow: null` hook-only. paired sibling of ADR-085 Amendment 2 (axis disjoint — coordination artifact-level ↔ verify local-state).
- **ADR-079** — KST +09:00 ISO 8601 zoned strict (마커 kst 필드 source).
- **ADR-050** — reserve-before-create convention (유형#5 예약 row anchor, convention-dependent invariant).
- **ADR-151 / ADR-154 / ADR-157** — honest-ceiling (presence ≠ truth) + silent-green ≠ silent-fallback ≠ honest-degrade 3-way taxonomy + 정적 리터럴 결정가능·동적 out-of-scope 상속.
- **ADR-045 §D-9** — cross_story_pattern_adr_trigger (root_cause_class N=3 ≥ threshold N=2 forcing function).

## 변경 이력

| 날짜 (KST) | CFP | 변경 |
|---|---|---|
| 2026-07-19 | CFP-2761 | 신규 — ADR-085 §결정 10 (Amendment 2) mid-flight artifact-level provenance marker convention narrative SSOT. marker 3-tuple(owner/kst/status closed-set) + E1 legacy=provisional + CI-visibility 3-class boundary(tracked content 1-3 / local-state probe 4 hook-only / tracked anchor narrow 5) + honest-ceiling(presence≠truth, 유형5 예약 row age proxy + 예약-전 window 미커버, 유형4 hook-only PR-CI near-vacuous) + advisory/no-auto-skip + Wave1/Wave2. |
