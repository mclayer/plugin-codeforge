---
title: CODEFORGE_CROSS_REPO_PAT rotation audit log
status: Active
date: 2026-05-14
related_adrs:
  - ADR-013
  - ADR-063
  - ADR-066
related_cfp:
  - CFP-450
  - CFP-521
  - CFP-627
---

# CODEFORGE_CROSS_REPO_PAT rotation audit log

CFP-450 (ADR-013 Amendment 4) PAT consolidation 후 단일 `CODEFORGE_CROSS_REPO_PAT` 의 rotation history.

정책 SSOT: [ADR-066](../adr/ADR-066-pat-rotation-policy.md).

## Rotation history

| rotated_at (KST) | by | reason | expiration | revoked_at |
|---|---|---|---|---|
| 2026-05-12T??:??:??+09:00 | mccho@mclayer.it | CFP-450 initial issuance (Option B consolidation) | TBD — 사용자 확인 의무 | - |
| 2026-05-14T??:??:??+09:00 (PENDING — Phase 2 PR description checklist 강제) | mccho@mclayer.it | **CFP-627 scope grant — marketplace contents:read** added for `marketplace-drift-detection.yml` workflow (ADR-066 Amendment 2 §결정 2 scope minimum 4종 정합 + ADR-063 Amendment 3 §결정 13 (post-rebase — CFP-631 occupied Amendment 2 §결정 11+12) reactive scheduled detection prerequisite). **Forcing function (DesignReview FIX iter 1 F-DR-004 option b)**: Phase 2 PR description checklist item "actual grant date update before merge (PENDING placeholder 해소 의무)" 의무 — Phase 2 PR merge 전 단일 placeholder 해소. audit trail integrity = manual update single-point-of-failure 차단. | TBD — Phase 2 진입 전 actual grant date + 90 days (ADR-066 §결정 1 권장 lifetime) | - |

## Schema

| 필드 | 형식 | 설명 |
|---|---|---|
| `rotated_at (KST)` | ISO 8601 (KST `+09:00` suffix) | 새 PAT 발급 + org secret 갱신 완료 시점 |
| `by` | email | rotation 수행 주체 (사용자 식별) |
| `reason` | free text | rotation 사유 (scheduled / leak response / scope change 등) |
| `expiration` | ISO 8601 date (KST) | 새 PAT 의 만료 일자 (≤ 90 days 권장 / ≤ 180 days 최대) |
| `revoked_at` | ISO 8601 (KST) 또는 `-` | 이전 PAT 의 revoke 시점 (당시 active row 면 `-`) |

## Audit notes

- 본 file 은 PAT rotation 시점 사후 audit 용 (compromise 분석 / lifetime tracking).
- 사용자 manual entry 의무 — workflow 자동 갱신 0건 (PAT 발급 절차 자체가 GitHub UI 의존, ADR-066 §결정 5 정합).
- Rotation 시 (a) 새 row append + (b) 이전 row 의 `revoked_at` 갱신 의무.
- 첫 row 의 `rotated_at` / `expiration` 시간 부분은 사용자가 실제 발급 시점 확인 후 PR 또는 별도 commit 으로 채울 의무 (CFP-521 본 Story PR merge 이후 follow-up commit 허용).

## Compromise response (leak / suspected leak 시)

[ADR-066 §결정 4](../adr/ADR-066-pat-rotation-policy.md#결정-4--compromise-response-leak--suspected-leak-시-4-step) 4-step 실행 + 본 file 신규 row append (`reason: leak response (compromise <date>)`).

## 자동화 carrier (Phase 2 후속)

- 자동 만료 reminder workflow: 별도 CFP.
- Audit log schema lint (`scripts/check-pat-rotation-log.sh`): 별도 CFP.
- 도입 시 ADR-066 `mechanical_enforcement_actions[]` row append + `docs/evidence-checks-registry.yaml` warning tier entry 등록 (ADR-040 Amendment 3 §결정 7 + ADR-060 정합).
