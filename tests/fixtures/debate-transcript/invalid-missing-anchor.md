---
key: TEST-FIXTURE-001
title: invalid debate transcript fixture — anchor_id empty
status: phase:구현-리뷰
type: story
date: 2026-05-11
github_issue: mclayer/plugin-codeforge#0
---

# TEST-FIXTURE-001: invalid debate transcript (anchor_id empty)

## §1. 사용자 요구사항

placeholder.

## §9. 품질 게이트 이력

### §9.1 설계 리뷰 Iteration

#### Iteration 1

placeholder verdict.

### Debate transcript:

본 sub-section 의 헤더에 anchor_id 가 비어있음. `check-doc-section-schema.sh` 가 FAIL 처리 의무.

#### trigger

```yaml
lane: design-review
detected_by: DesignReviewPLAgent
divergence_type: severity
anchor_id: ""
```

#### rounds

```yaml
- index: 0
  emitted_at: 2026-05-11T12:00:00Z
```

#### termination

```yaml
method: pl_llm_judgment
final_verdict: PASS
dialog_rounds_count: 3
```
