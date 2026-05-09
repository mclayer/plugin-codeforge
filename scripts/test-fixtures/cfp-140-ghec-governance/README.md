# CFP-140 GHEC Governance e2e Fixtures

AC-23 (Change Plan §8.2) — 4 e2e fixture scenarios.

## Fixture 1: Issue Type auto-attach (UC-5)

`fixture-1-issue-type-auto-attach/`

PASS criteria: mclayer org 신규 Story Issue 생성 시 Issue Type "Story" 자동 부착 1건 verify.

Mechanism:
- story-init.yml Action의 "Attach native Issue Type" step
- org Issue Types API: `GET /orgs/{org}/issue-types` → find "Story" → PATCH issue

Test method: Shell script mock (no real API call in fixture — uses API response mocks).

## Fixture 2: Ruleset drift detect (UC-1)

`fixture-2-ruleset-drift/`

PASS criteria: sync-rulesets.sh --dry-run detects diff + --apply syncs correctly.

Two sub-cases:
- `no-drift/`: live state matches spec → exit 0
- `has-drift/`: live state differs → exit 2 (would-change)

Test method: Mock gh API responses via environment override.

## Fixture 3: Audit log fetch (UC-3)

`fixture-3-audit-log-fetch/`

PASS criteria: audit-trail-fetch.sh fetches paginated events + PII redaction applied.

Test method: Mock GraphQL response JSON files + cursor file resume test.

## Fixture 4: Required workflow drift (UC-2)

`fixture-4-required-workflow-drift/`

PASS criteria: sync-required-workflows.sh --dry-run detects missing required workflows.

Test method: Mock gh API responses.
