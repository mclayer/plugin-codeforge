---
key: TEST-FIXTURE-002
title: invalid debate transcript fixture — rounds empty
status: phase:구현-리뷰
type: story
date: 2026-05-11
github_issue: mclayer/plugin-codeforge#0
---

# TEST-FIXTURE-002: invalid debate transcript (rounds empty)

## §1. 사용자 요구사항

placeholder.

## §9. 품질 게이트 이력

### §9.1 설계 리뷰 Iteration

#### Iteration 1

placeholder verdict.

### Debate transcript: docs/foo.md:42

#### trigger

```yaml
lane: design-review
detected_by: DesignReviewPLAgent
divergence_type: severity
anchor_id: docs/foo.md:42
```

#### rounds

(empty — `check-doc-section-schema.sh` FAIL 의무)

#### termination

```yaml
method: pl_llm_judgment
final_verdict: PASS
dialog_rounds_count: 0
```
