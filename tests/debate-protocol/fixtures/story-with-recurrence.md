---
key: TEST-RECURRENCE-001
title: Story file fixture — same anchor recurrence (>= 2)
status: phase:설계-리뷰
type: story
date: 2026-05-11
github_issue: mclayer/plugin-codeforge#0
---

# TEST-RECURRENCE-001

## §1. 사용자 요구사항

placeholder.

## §9. 품질 게이트 이력

### §9.1 설계 리뷰 Iteration

#### Iteration 1

verdict — FIX (anchor_id docs/foo.md:42 divergence).

### Debate transcript: docs/foo.md:42

#### trigger
```yaml
anchor_id: docs/foo.md:42
```
#### rounds
```yaml
- index: 0
```
#### termination
```yaml
final_verdict: FIX
```

#### Iteration 2 — FIX-1 re-review

verdict — FIX (same anchor_id docs/foo.md:42 재발).

### Debate transcript: docs/foo.md:42

#### trigger
```yaml
anchor_id: docs/foo.md:42
```
#### rounds
```yaml
- index: 0
```
#### termination
```yaml
method: anchor_recurrence
final_verdict: ESCALATE
```

이 fixture 는 동일 anchor_id 가 두 번째 debate 를 유발 = `count >= 2` → 즉시 사용자 escalation 시나리오 (ADR-059 §결정 4) 의 input.
