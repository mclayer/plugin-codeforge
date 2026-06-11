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
  - CFP-743
  - CFP-1336
  - CFP-2101
---

# CODEFORGE_CROSS_REPO_PAT rotation audit log

CFP-450 (ADR-013 Amendment 4) PAT consolidation 후 단일 `CODEFORGE_CROSS_REPO_PAT` 의 rotation history.

정책 SSOT: [ADR-066](../../archive/adr/ADR-066-pat-rotation-policy.md).

## Rotation history

| rotated_at (KST) | by | reason | expiration | revoked_at |
|---|---|---|---|---|
| 2026-05-12T00:00:00+09:00 [^t1] | mccho@mclayer.it | CFP-450 initial issuance (Option B consolidation) | 2026-08-10 [^e1] | - |
| 2026-05-14T00:00:00+09:00 [^t1] | mccho@mclayer.it | **CFP-627 scope grant — marketplace contents:read** added for `marketplace-drift-detection.yml` workflow (ADR-066 Amendment 2 §결정 2 scope minimum 4종 정합 + ADR-063 Amendment 3 §결정 13 reactive scheduled detection prerequisite). Scope added: `mclayer/marketplace contents:read`. **Verified live** 2026-05-15 KST via CFP-673 sub-PR (c) marketplace-parity workflow PR-time check + reactive scheduled detection PR #135 + PR #137 marketplace sync flow (PAT scope active confirmed). | 2026-08-10 [^e1] (scope add — original PAT lifetime 유지) | 2026-06-09T00:00:00+09:00 [^t4] (CFP-2101 — #2053 복구 시 classic No-expiration PAT 로 교체, 본 fine-grained PAT revoke) |
| PLACEHOLDER (Phase 2 진입 전 actual grant date 갱신 의무) [^t2] | mccho@mclayer.it | **CFP-743 scope grant — reconcile-target-repos contents:write + pull_requests:write** added for `scripts/codeforge-upgrade.{sh,ps1}` + UpgradeAgent reconcile PR open (ADR-066 Amendment 3 §결정 2 scope minimum 5종 정합 + reconcile-protocol-v1 v1.2 §2 desired_state_domains `github_workflow` / `issue_templates` / `codeowners` consumer `.github/` PR open prerequisite). Scope added: `reconcile-target-repos contents:write` + `reconcile-target-repos pull_requests:write` (consumer reconcile 대상 repo 한정 — org-wide write 금지, least-privilege invariant). **Phase 1 placeholder** — actual grant + live verify = Phase 2 PR 진입 전 사용자 manual blocker (ADR-066 §결정 2 Grant 절차 정합). | TBD (Phase 2 actual grant 시 90 days 기준 갱신) | - |
| PLACEHOLDER (CFP-1336 Wave 2 진입 전 actual grant date 갱신 의무) [^t3] | mccho@mclayer.it | **CFP-1336 scope grant — cross-repo-target-repos issues:write (label endpoint)** added for `templates/github-workflows/cross-repo-label-sync.yml` (Wave 2 carrier) cross-repo bidirectional label sync workflow (ADR-066 Amendment 4 §결정 2 scope minimum 6종 정합 + ADR-073 Amendment 9 §결정 1-A 9번째 entry `label_change` paired sibling + ADR-082 Amendment 13 §결정 1 layer 1 sub-scope 1-D cross-repo label-write authority paired sibling — 3 ADR Amendment 동시 발의, axis disjoint complement 3-set: verify subject ↔ write authority ↔ PAT scope grant). Scope added: `cross-repo-target-repos issues:write` (label endpoint 1종만 — `contents:write` / `workflows:write` / `admin:*` / `delete_repo` 등 escalation scope 미부여, fine-grained PAT repository access list 강제: `mclayer/plugin-codeforge` (wrapper) ↔ impl repo (consumer Phase 2 PR repo) 2-repo 한정, org-wide write 절대 금지). **Phase 1 placeholder** — actual grant + live verify = CFP-1336 Wave 2 별 sub-CFP carrier (workflow hydrate + impl repo listener seed) 진입 전 사용자 manual blocker (ADR-066 §결정 2 Grant 절차 정합, Amendment 2/3 placeholder pattern 답습). CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier — sentinel-driven 아닌 ratchet 확장 carrier. | TBD (Wave 2 actual grant 시 90 days 기준 갱신) | - |
| 2026-06-09T00:00:00+09:00 [^t4] | mccho@mclayer.it | **CFP-2101 token replacement — classic No-expiration (repo + workflow)** for #2053 PAT 404 outage 복구 (ADR-066 Amendment 5 §결정 1/2 evidence-gated exception clause 정합 — 첫 약화 방향 amendment). 이전 fine-grained PAT (2026-05-14 active row) revoke + classic PAT 신규 발급. Scope: classic `repo` + `workflow` (fine-grained 6 scope least-privilege 의 evidence-gated exception — single-owner dogfood 한정). Repository access: family 11 repo set (`mclayer/plugin-codeforge` + `codeforge-{requirements,design,review,develop,test,deploy,deploy-review,pmo}` + `marketplace` + `codeforge-internal-docs`). reason: #2053 outage — fine-grained ≤90일 회전 + repository-access-list friction 이 cross-repo write 전면 HTTP 404 (모든 신규 Story scaffold 차단) 유발 → classic No-expiration 으로 friction 회피. **Verified** 2026-06-09 KST — 사용자 11 repo set 교체 + cross-repo write 복구 확인 (#2053 close). 보상통제 3종 (ADR-066 §결정 1/2 Amendment 5 exception clause): (1) §결정 4 leak 즉시 revoke 절차 유지 (무만료라도 T+0 revoke + T+1h rotation 불변) (2) 단일 consolidated PAT (ADR-013 Amendment 4) (3) single-owner dogfood (multi-tenant production 아님). | No-expiration [^e2] (classic No-expiration — ADR-066 Amendment 5 evidence-gated exception, §결정 4 compromise response 가 lifetime 만료 대체) | - |

[^t1]: 시간 부분 `00:00:00+09:00` = ADR-066 §결정 5 사용자 manual entry 의무 영역 — 실제 발급 시점 정확 시간 불명 시 발급 일자 기준 자정 placeholder (CFP-521 §결정 5 + ADR-066 schema 정합). 사용자 GitHub Settings → Developer settings → Personal access tokens → 발급 시점 정확 timestamp 확인 후 별 commit / PR 으로 정정 허용.

[^e1]: 만료 일자 = 2026-05-12 발급 + 90 days (ADR-066 §결정 1 권장값) = **2026-08-10** (KST). 사용자가 GitHub Settings 에서 실제 expiration 설정 시 90 days 외 값 (예: 180 days = 2026-11-08 / 30 days = 2026-06-11) 적용 가능 — 실 설정값 확인 후 정정 허용.

[^t2]: CFP-743 Amendment 3 = **Phase 1 placeholder row** (ADR-066 §결정 2 Grant 절차 + §결정 5 audit log SSOT 정합). 실제 scope grant + live verify 는 Phase 2 PR (UpgradeAgent + CLI 실 구현) 진입 전 사용자 manual blocker. Phase 2 진입 시 본 row 의 `rotated_at` 을 actual grant timestamp 로 갱신 + scope active 를 reconcile PR open 1건으로 live verify (ADR-073 verify-before-assert 정합) 후 placeholder 표기 제거 의무.

[^t3]: CFP-1336 Amendment 4 = **Phase 1 placeholder row** (ADR-066 §결정 2 Grant 절차 + §결정 5 audit log SSOT 정합, Amendment 2/3 placeholder pattern 답습). 실제 scope grant + live verify 는 CFP-1336 Wave 2 별 sub-CFP carrier (`templates/github-workflows/cross-repo-label-sync.yml` workflow hydrate + impl repo listener seed + bats fixture pair + script lint binding) 진입 전 사용자 manual blocker. Wave 2 진입 시 본 row 의 `rotated_at` 을 actual grant timestamp 로 갱신 + scope active 를 cross-repo label sync workflow 1건 (wrapper → impl bidirectional label write success)으로 live verify (ADR-073 Amendment 9 §결정 1-A 9번째 entry `label_change` verify-before-assert 4-step 정합) 후 placeholder 표기 제거 의무.

[^t4]: CFP-2101 Amendment 5 = **actual rotation row** (placeholder 아님 — 토큰 교체 이미 완료, 2026-06-09 검증). #2053 PAT 404 outage 복구 시 사용자가 fine-grained PAT → classic No-expiration (repo+workflow) 11 repo set 으로 실 교체. 시간 부분 `00:00:00+09:00` = 정확 발급 시각 불명 시 발급 일자 기준 자정 placeholder ([^t1] 정합) — 사용자가 GitHub Settings 에서 정확 timestamp 확인 후 별도 commit 정정 허용.

[^e2]: classic No-expiration (무만료) = ADR-066 §결정 1 Amendment 5 evidence-gated exception clause 정합 (단일 family dogfood PAT 한정, 보상통제 3종 충족 시). 본래 §결정 1 default (90일 권장 / 180일 최대) 의 약화 방향 exception — lifetime 만료 부재를 §결정 4 compromise response (leak 즉시 T+0 revoke + T+1h rotation) 절차가 대체. 무만료라도 compromise 감지 시 revoke 의무 불변.

## Schema

| 필드 | 형식 | 설명 |
|---|---|---|
| `rotated_at (KST)` | ISO 8601 (KST `+09:00` suffix) | 새 PAT 발급 + org secret 갱신 완료 시점 |
| `by` | email | rotation 수행 주체 (사용자 식별) |
| `reason` | free text | rotation 사유 (scheduled / leak response / scope change 등) |
| `expiration` | ISO 8601 date (KST) 또는 sentinel `No-expiration` | 새 PAT 의 만료 일자 (≤ 90 days 권장 / ≤ 180 days 최대). 단 §결정 1 exception 적용 (단일 family dogfood PAT classic No-expiration) 시 sentinel `No-expiration` 허용 (ADR-066 Amendment 5, CFP-2101 — 보상통제 3종 충족 조건). sentinel row 는 §결정 6 자동 만료 reminder parse 에서 skip 대상 (만료 없음 → reminder 비대상). |
| `revoked_at` | ISO 8601 (KST) 또는 `-` | 이전 PAT 의 revoke 시점 (당시 active row 면 `-`) |

## Audit notes

- 본 file 은 PAT rotation 시점 사후 audit 용 (compromise 분석 / lifetime tracking).
- 사용자 manual entry 의무 — workflow 자동 갱신 0건 (PAT 발급 절차 자체가 GitHub UI 의존, ADR-066 §결정 5 정합).
- Rotation 시 (a) 새 row append + (b) 이전 row 의 `revoked_at` 갱신 의무.
- 첫 row 의 `rotated_at` / `expiration` 시간 부분은 사용자가 실제 발급 시점 확인 후 PR 또는 별도 commit 으로 채울 의무 (CFP-521 본 Story PR merge 이후 follow-up commit 허용).

## Compromise response (leak / suspected leak 시)

[ADR-066 §결정 4](../../archive/adr/ADR-066-pat-rotation-policy.md#결정-4--compromise-response-leak--suspected-leak-시-4-step) 4-step 실행 + 본 file 신규 row append (`reason: leak response (compromise <date>)`).

## 자동화 carrier (Phase 2 후속)

- 자동 만료 reminder workflow: 별도 CFP.
- Audit log schema lint (`scripts/check-pat-rotation-log.sh`): 별도 CFP.
- 도입 시 ADR-066 `mechanical_enforcement_actions[]` row append + `docs/evidence-checks-registry.yaml` warning tier entry 등록 (ADR-040 Amendment 3 §결정 7 + ADR-060 정합).

## 권고 (CFP-2178 S6 — 2026-06-12)

**권고 (CFP-2178 S6)**: CODEFORGE_CROSS_REPO_PAT 11-repo set 중 lane 8 repo 는 archive 됨 — **fine-grained PAT 전환 시 lane 8 repo 를 access list 에서 제외**할 것. 단 **현행 classic PAT 에서는 repository 단위 scope 축소가 기술적으로 실행 불가** (classic = 계정 전체 repo 일괄 접근, repo 단위 access list 개념 부재) — 본 기록은 권고이며 실행 자동화 없음. 실제 fine-grained 전환 실행 시 ADR-066 Amendment 의무.
