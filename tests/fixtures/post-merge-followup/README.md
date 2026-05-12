# Post-merge-followup Fixture Schema

CFP-476 Phase 2 test harness 를 위한 13 fixture 수집.

## Fixture YAML Schema

```yaml
---
# Metadata
description: "<시나리오 설명 — ADR-026 Amendment 1 §결정 5 컨텍스트>"
fixture_key: "<fixture-id>" # e.g., cfp-455-phase2-success
story_mapping: "<Story §8.5 AC/UC/EC 항목>" # e.g., AC-2, UC-3

# PR context (GitHub pull_request event)
pr:
  number: <int>
  title: "<PR title with CFP-NNN>"
  body: |
    <PR body markdown — may contain close keyword references>
  labels:
    - "phase:설계-리뷰" # or other phase
    - "type:feature"

# Issue context (story Issue, carrier)
issue:
  number: <int>
  closed_by_pull_requests_references: [<int>, ...] # Result of `gh issue view N --json closedByPullRequestsReferences`

# Consumer config (from .codeforge/project.yaml or .claude/_overlay/project.yaml)
consumer_config:
  lanes:
    security_ai: <boolean> # Default: true → phase:보안-테스트; false → phase:구현-테스트

# Expected test outcome
expected_outcome: "<one of: success, skip_phase1, skip_not_terminal_phase, skip_no_close_keyword, skip_dual_source_mismatch, skip_multi_issue, skip_cross_repo_unsupported, skip_chore, skip_multi_cfp, skip_already_audited>"

# Audit comment (if applicable)
expected_audit_marker: "<[close-success] | [multi-match-skip] | [cross-repo-skip] | [dual-source-mismatch] | [lazy-source-b] | null>"

# Optional: expected_audit_comment_body for complex audits
expected_audit_comment_body: |
  (optional full audit comment text)
```

## Fixture naming convention

- Lowercase kebab-case: `cfp-455-phase2-success.yml`
- Pattern: `<story-or-scenario>-<outcome>.yml` (most) or `<scenario-specific>.yml` (edge cases)

## Fixture count

- Mandatory: 13 fixtures (Story §8.6 Change Plan §8)
- Bonus (AC/UC coverage): 2 fixtures (pr-title-with-singlequote, idempotency-probe-dedupe)
- **Total: 15 fixtures**

## Test harness runner

Test harness (`test_post-merge-followup-yml.sh`) 가 각 fixture yml 를 load 후:

1. PR context 추출 (title, body, labels)
2. Issue context 생성 (mock gh CLI stub function)
3. bash mock run: `tests/scripts/post-merge-followup/action3-logic.sh` 실행
4. expected_outcome 비교
5. expected_audit_marker 비교 (if applicable)

---

## Template structure (filled by QADev Phase 2)

```
tests/fixtures/post-merge-followup/
├── 001-cfp-391-false-positive.yml
├── 002-cfp-412-false-positive.yml
├── 003-cfp-455-phase1-skip.yml
├── 004-cfp-455-phase2-success.yml
├── 005-terminal-phase-success.yml
├── 006-dual-source-mismatch.yml
├── 007-multi-issue-warning-skip.yml
├── 008-qualified-syntax-same-repo.yml
├── 009-qualified-syntax-cross-repo-skip.yml
├── 010-mid-phase-blocked.yml
├── 011-chore-pr-skip.yml
├── 012-multi-cfp-aggregating-skip.yml
├── 013-source-b-lazy-sync.yml
├── B1-pr-title-with-singlequote.yml
├── B2-idempotency-probe-dedupe.yml
└── README.md (this file)
```

---

Reference: CFP-476 Phase 1 ADR-026 Amendment 1 §결정 5.A ~ 5.D
