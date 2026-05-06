---
adr_number: 31
title: Lane-spawn evidence trail (committed Orchestrator self-write + Phase 2 PR description regex + phase-gate-mergeable invariant)
date: 2026-05-06
status: Proposed
category: orchestration
carrier_story: CFP-126
parent_epic: CFP-124
supersedes: null
related_files:
  - templates/story-page-structure.md
  - templates/github-workflows/phase-gate-mergeable.yml
  - templates/github-pr-template.md
  - docs/orchestrator-playbook.md
  - scripts/check-lane-evidence.sh
  - CLAUDE.md
---

# ADR-031: Lane-spawn evidence trail

## 상태

Proposed (2026-05-06). carrier_story = CFP-126 (CFP-124 Epic 의 Phase 3 child). CFP-126 Phase 1 PR merge 시 Accepted 전환. **Storage location 은 본 Phase 1 draft 에서는 deferred — CFP-126 Phase 1 PR 의 Sonnet decider trigger a 가 결정** (4 candidate 중 pick).

## 컨텍스트

CFP-124 진단 (2026-05-06) §1.3 architectural root cause A1:

> **"Lane plugin 실제 spawn 흔적" 을 강제하는 invariant 부재.** Phase 1 PR + Phase 2 PR rhythm, §10 FIX Ledger, sub-issue, gate label — 모두 CI invariant 가 있지만 lane plugin 가 실제로 spawn 됐는지 검증 mechanism 없음. Claude (consumer Orchestrator) 가 인-context 에서 lane 작업을 simulate 하고 PR/ledger 만 만들면 `phase-gate-mergeable.yml` 가 통과한다.

ADR-027 §컨텍스트:35 검증 quote:

> 7 Epic (MCT-12 ~ MCT-63) 모두 main merge — 그러나 6 lane plugin 0개 spawn, manual Codex 7-area + Sonnet decider 패턴으로 우회.

### CFP-20 NG6 명시 — `§0` 위치는 cache-only

[CFP-20 spec](../../../codeforge-internal-docs/wrapper/specs/2026-04-28-cfp-20-live-progress-design.md) NG6 명시:

> §0 file 이 commit 되거나 deliverable 이 되는 모델 (cache 로 유지)

CFP-20 Q5 = `초안 L1 (Story file §0) → 사용자 push back 후 revoked`. 즉 `.claude-work/progress/<KEY>.md` (`§0 Live Progress`) = gitignored, ephemeral cache. **CI invariant 가 보는 PR diff 에 노출 없음** — lane evidence storage 로 부적합.

본 ADR 의 evidence storage 는 **committed (PR diff 노출)** 영역에 위치 — CFP-20 §0 cache 와 명확히 분리.

## 결정 요약

5 결정 freeze. carrier story = CFP-126. Storage location 의 4 candidate 는 §결정 1 enumerate, Sonnet decider 가 CFP-126 Phase 1 에서 pick.

### 결정 1 — Wrapper Orchestrator self-write committed lane evidence (storage location candidate set)

매 lane spawn (요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트, FIX 시 multiple entry 가능) 시 wrapper Orchestrator 가 **committed evidence** 누적. Schema 필드:

```yaml
- story_key: CFP-NN
  phase: phase:설계
  lane: 설계
  iteration: 1            # 첫 spawn = 1, FIX 재시도 = 2, 3, ...
  agent: ArchitectPLAgent (codeforge-design@mclayer)
  spawned_at: 2026-05-NN T HH:MM Z
  return_at: 2026-05-NN T HH:MM Z
  outcome: PASS | FIX | SKIPPED | ESCALATED
  pr_ref: mclayer/plugin-codeforge#NNN  # Phase 2 PR ref (FIX/optimization 시 동일 PR 누적)
  decision_packet_ref: <internal-docs path or yaml id, optional>
  transcript: <inline summary 50자 이내 또는 internal-docs decision archive link>
  fix_iteration: null     # ADR-031 결정 4 bypass 시 BYPASS_LANE_EVIDENCE_REASON 인용
```

**Storage location candidate** (Sonnet decider 가 CFP-126 Phase 1 PR 에서 pick):

- (a) Story file 의 신규 dedicated section (예: §14 Lane Evidence — additive, §13 CONDITIONAL Live 와 충돌 회피)
- (b) Story file `§8.5 Impl Manifest` 안 sub-block (Phase 2 PR 시점 첫 commit, 기존 schema additive)
- (c) Story file frontmatter `lane_spawns:` YAML array (frontmatter parsing 의존, lint 단순)
- (d) Phase 2 PR description body `## Lane evidence` 블록 만 (Story file 미수정, PR-side single source)

**명시적 제외**: `.claude-work/progress/<KEY>.md` (CFP-20 NG6 — gitignored cache, CI invariant 부적합).

CFP-126 Phase 1 PR 에서 Sonnet decider 가 4 candidate 중 1 pick — trade-off (commit churn / lint 복잡도 / cross-validate 가능성 / Story 가독성) 평가.

### 결정 2 — Phase 2 PR description 의무 블록 `## Lane evidence` (regex 검증)

Phase 2 PR body 의무 marker:

```markdown
## Lane evidence

- 요구사항: PASS  (story=<KEY>, iteration=1, agent=RequirementsPLAgent)
- 설계: PASS
- 설계-리뷰: PASS  (gate:design-review-pass)
- 구현: PASS
- 구현-리뷰: PASS  (FIX iteration: 1 — Story §10 row 3)
- 구현-테스트: PASS
- 보안-테스트: PASS  (gate:security-test-pass)
```

CI workflow 가 `^## Lane evidence$` 헤더 + 7-row regex (`- <lane>: PASS|SKIPPED|FIX|ESCALATED`) 검증. 결정 1 의 storage 가 (a)/(b)/(c) pick 시 = Story-file ↔ PR-description cross-validate (lane name set + outcome 일치). (d) pick 시 = PR-description single source.

`templates/github-pr-template.md` placeholder 추가 — 작성 누락 방지.

### 결정 3 — `phase-gate-mergeable.yml` 가 evidence 부재 시 action_required block

`templates/github-workflows/phase-gate-mergeable.yml` 확장 (CFP-126 Phase 2):

- Phase 2 PR (label `phase:보안-테스트` 부착 / phase 진입 직후) → PR description regex 검증
- 7-row 모두 valid 형식 통과 시 = `success`
- 부재 또는 invalid format = `action_required`

`type:epic` / doc-only fast-pass (CFP-106) 변경 없음 — Epic doc PR 은 본 invariant 면제 (Phase 1 = lane spawn 개념 외).

### 결정 4 — Bypass = `BYPASS_LANE_EVIDENCE=1` env (REASON 의무 동반)

긴급 hotfix / planned skip 시:

```
BYPASS_LANE_EVIDENCE=1
BYPASS_LANE_EVIDENCE_REASON="<incident-id 또는 사유>"
```

두 env 동시 set 의무 (ADR-027 §결정 3 `HOTFIX_BYPASS_CODEFORGE` 패턴 정합).

Bypass 사용 시:
- workflow regex 검증 skip
- Phase 2 PR description 에 `BYPASS: <REASON>` 명시 의무 (CI grep)
- `docs/hotfix-playbook.md` 등재 의무
- Bypass 후 followup audit Issue 자동 생성 (ADR-026 post-merge automation 활용)

### 결정 5 — Effective date = ADR-031 Accepted 후 신규 Phase 2 PR 부터 (retroactive 미처리)

기존 Story (CFP-1 ~ CFP-123, mctrader MCT-12 ~ MCT-63) retroactive 처리 안 함:

- CFP-126 Phase 2 PR merge 직후의 새 Phase 2 PR 부터 본 invariant 적용
- 기존 Story 의 evidence 부재 = 정상 (effective date 이전)
- CI workflow 가 effective date 이후 Story 만 검사 (commit timestamp 또는 Story `date:` 비교)

ADR-027 §결과:108 retroactive 미처리 invariant 정합.

## 결과

- 본 ADR Accepted 후 모든 신규 Phase 2 PR 가 lane evidence carry 의무
- Wrapper Orchestrator 가 lane plugin 0개 spawn 시 PR merge 불가 (bypass 명시 시 audit-trail)
- Schema 데이터 누적 → 30+ Story 후 PMOAgent retro 가 actual lane spawn rate / iteration 분포 / outcome 분포 측정 (ADR-026 telemetry 패턴 정합)

## 6 lane plugin 영향 매트릭스

| Repo | 영향 | sibling PR 의무 |
|---|---|---|
| `mclayer/plugin-codeforge` (wrapper) | ADR-031 + workflow + lint script + template | 본 PR 자체 |
| `mclayer/plugin-codeforge-requirements` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-design` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-review` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-develop` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-test` | 변경 없음 | 불요 |
| `mclayer/plugin-codeforge-pmo` | 변경 없음 (단 retro 시 lane evidence 데이터 활용 — 30+ Story 후) | 불요 |

본 ADR 는 wrapper Orchestrator self-write 영역만 다룸. Lane plugin 자체의 spawn-side instrumentation (Lane plugin 측 transcript schema / agent metadata schema) 은 별도 cross-plugin CFP — 본 Epic 비-범위.

## Out-of-scope

- Lane plugin self-instrumentation (cross-plugin spawn-side schema)
- 기존 Story retroactive 적용
- Strict mode default-on (ADR-032 별도)
- `.claude-work/progress/<KEY>.md` 에 lane_spawns 추가 (CFP-20 NG6 cache invariant 보존)
- 자동 lane spawn (Orchestrator spawn 책임 — 본 ADR 는 evidence 만)

## 관련 파일

- `templates/story-page-structure.md` (Phase 2 PR — Sonnet pick 결과 schema)
- `templates/github-workflows/phase-gate-mergeable.yml` (Phase 2 — regex 검증)
- `templates/github-pr-template.md` (Phase 2 — placeholder)
- `docs/orchestrator-playbook.md` (Phase 2 — §3 lane spawn 절차 갱신)
- `scripts/check-lane-evidence.sh` + `scripts/test-check-lane-evidence.sh` (Phase 2 NEW)
- `CLAUDE.md` (Phase 2 — §"오케스트레이션 규칙" 갱신)
- spec: `codeforge-internal-docs/wrapper/specs/2026-05-NN-cfp-126-lane-spawn-evidence-trail-design.md` (CFP-126 Phase 1)
- plan: `codeforge-internal-docs/wrapper/plans/2026-05-NN-cfp-126-lane-spawn-evidence-trail-plan.md` (CFP-126 Phase 1)
- carrier story: `codeforge-internal-docs/wrapper/stories/CFP-126.md`
- parent Epic: `codeforge-internal-docs/wrapper/stories/CFP-124.md`
