---
key: CFP-FIXTURE-FIX-VALID-1
title: FIX evidence fixture — 1 FIX iteration, 1 fix-iter lane row (PASS)
status: phase:보안-테스트
date: 2026-05-09
type: story
---

# CFP-FIXTURE-FIX-VALID-1: Valid fixture with 1 FIX iteration

(fixture stub — CFP-298 check-fix-evidence.sh valid PASS test)

## §1 메타

placeholder

## §10 FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | 2026-05-09T11:00:00Z | 설계-리뷰 | DesignReviewPL P0 §7 누락 | 설계 | Change Plan §3 재작성 | — |

## §14 Lane Evidence

```yaml
lane_evidence:
  - lane: 요구사항
    iteration: 1
    agent: RequirementsPLAgent
    spawned_at: 2026-05-09T10:00:00Z
    returned_at: 2026-05-09T10:15:00Z
    output_status: completed
    outcome: PASS
    spawn_id: req-001
    fix_iteration: null
  - lane: 설계
    iteration: 1
    agent: ArchitectPLAgent
    spawned_at: 2026-05-09T10:20:00Z
    returned_at: 2026-05-09T10:50:00Z
    output_status: completed
    outcome: PASS
    spawn_id: design-001
    fix_iteration: null
  - lane: 설계-리뷰
    iteration: 1
    agent: DesignReviewPL
    spawned_at: 2026-05-09T11:00:00Z
    returned_at: 2026-05-09T11:30:00Z
    output_status: completed
    outcome: FIX
    spawn_id: design-review-001
    fix_iteration: null
  - lane: 설계
    iteration: 2
    agent: ArchitectPLAgent
    spawned_at: 2026-05-09T12:00:00Z
    returned_at: 2026-05-09T12:45:00Z
    output_status: completed
    outcome: PASS
    spawn_id: design-002-fix
    fix_iteration: 1
  - lane: 설계-리뷰
    iteration: 2
    agent: DesignReviewPL
    spawned_at: 2026-05-09T13:00:00Z
    returned_at: 2026-05-09T13:20:00Z
    output_status: completed
    outcome: PASS
    spawn_id: design-review-002
    fix_iteration: null
```
