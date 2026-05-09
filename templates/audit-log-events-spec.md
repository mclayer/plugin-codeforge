---
title: "Audit Log Events Spec"
version: "1.0"
category: Governance
status: Active
related_adrs:
  - ADR-048
  - ADR-031
related_stories:
  - CFP-140
---

# Audit Log Events Spec (CFP-140 / ADR-048)

codeforge governance trace 에 사용되는 GitHub Enterprise Audit Log event 분류 SSOT.
`scripts/audit-trail-fetch.sh` 가 이 spec 에 따라 event 를 필터링한다.

## PII Handling (§7.5 의무)

Audit log 항목은 `actor` email + `actor_ip` 를 **hash** 한 후에만 retro file 첨부 가능.
`audit-trail-fetch.sh` 가 자동 redact (SHA-256 truncated to 12 chars).

## Event Categories

### review_verdict

review-verdict v4 packet (ADR-035 / ADR-044) 과 cross-validate 하는 audit events.

| GitHub event | trigger | codeforge context |
|---|---|---|
| `pull_request.review_submitted` | Review 제출 | review packet submission 시점 |
| `pull_request.merged` | PR merge | final verdict PASS + phase transition |
| `issues.labeled` | label 부착 | `gate:design-review-pass` / `gate:security-test-pass` |

Cross-validate query: `story_key` + timerange 를 기준으로 Story §14 lane evidence 와 1:1 매핑.
event 유실 시 retro note `"audit window exceeded"` 또는 `"event_lost"`.

### lane_evidence

Story §14 Lane Evidence rows (ADR-031) 와 cross-validate.

| GitHub event | trigger | codeforge context |
|---|---|---|
| `push` | commit push | Phase 2 PR commit (lane implementation boundary) |
| `pull_request.opened` | PR open | Phase PR open (lane start) |
| `issues.labeled` | phase:* transition | lane boundary marker |

### fix_ledger

Story §10 FIX Ledger (fix-event-v1 contract) 와 cross-validate.

| GitHub event | trigger | codeforge context |
|---|---|---|
| `issues.labeled` | fix:* 부착 | FIX Ledger row 생성 trigger |
| `issue_comment.created` | [FIX] prefix comment | fix-event-v1 comment schema |

### governance_change

governance 상태 변경 감사 (drift detection).

| GitHub event | trigger | alert threshold |
|---|---|---|
| `org.update_member` | org 멤버 변경 | 항상 alert |
| `org.update_default_repository_permission` | permission 변경 | 항상 alert |
| `protected_branch.create` / `.update` | branch protection 변경 | drift-check 일치 여부 확인 |
| `repository_ruleset.create` / `.update` / `.destroy` | ruleset 변경 | spec 과 diff → `governance-drift` Issue |

## Rate Limit

| API | Limit | 대응 |
|---|---|---|
| GraphQL `enterprise.auditLog` | 5000 pt/hr | cursor pagination + exponential backoff |
| REST `/orgs/{org}/audit-log` | 100/page (max 200) | page iteration |

## Retention

GHEC default audit log retention: **180 days**.
`audit-trail-fetch.sh --since` 가 180 일 이전이면 warning `"audit window may be exceeded"`.
