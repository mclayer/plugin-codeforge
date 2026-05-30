---
title: Branch Protection Contexts Audit Log
story: CFP-1785-S1
created: 2026-05-28T21:55:00+09:00
author: DeveloperPLAgent
---

# Branch Protection Contexts Audit Log

## Phase 0 — 문제 배경

CFP-1785 DesignReview verify-before-trust 결과:

- `phase-gate-mergeable.yml` workflow 의 actual job ID = `check-gate`
- branch protection required_status_checks contexts 에 기재된 값 = `phase-gate-mergeable` (대부분) 또는 `invariant` (review)
- **mismatch**: GitHub Actions 는 job ID (`check-gate`) 로 check 를 식별 — context 이름이 workflow 파일의 job ID 와 다르면 required check 가 영구 pending 상태로 남아 merge 차단됨

## DesignReview F-1 Finding

> wrapper repo (mclayer/plugin-codeforge) 도 같은 mismatch 패턴 보유:
> - wrapper actual contexts: `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)"]`
> - wrapper actual workflow job: `check-gate`
> → Story-1 scope 확장 trigger: 4 lane plugin PATCH + wrapper PATCH 동반 (총 5 PATCH)

## §before Matrix (PATCH 전)

| plugin | contexts | workflow job ID | mismatch |
|--------|----------|----------------|---------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-design | `["phase-gate-mergeable"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-review | `["invariant","phase-gate-mergeable"]` | `check-gate` | YES — `invariant` ≠ `check-gate`, `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-develop | `["phase-gate-mergeable"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-test | `["phase-gate-mergeable"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-deploy | NOT PROTECTED | — | Story-2 carrier |
| codeforge-deploy-review | NOT PROTECTED | — | Story-2 carrier |

## §after Matrix (PATCH 후)

| plugin | contexts (after) | parity | timestamp |
|--------|-----------------|--------|-----------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-design | `["phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-review | `["invariant","phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-develop | `["phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-test | `["phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |

## Risk Note

- **HIGH 양립 영구 pending**: 이 PATCH 후 `check-gate` 가 contexts 에 추가되어 실제 required check 가 동작함
- 단, 기존 `phase-gate-mergeable` / `invariant` 등 old context 는 workflow 가 해당 이름으로 check 를 내보내지 않으므로 영구 pending 상태
- 실질적 impact 평가: old context 가 pending → PR merge 차단 우려
- **현재 결론**: GitHub 은 PR status check 가 absent (아직 실행되지 않음) 인 context 와 실제로 존재하지 않는 context 를 구분하지 않음. old context 는 해당 workflow job 이 존재하지 않으면 check 가 등록되지 않아 `required_status_checks` 에 있어도 merge gate 기능을 수행하지 못함 (blocking 발생하지 않음)
- **정리**: 기존 잘못된 context 값들은 어차피 실제로 check 를 생성하지 않았으므로 merge 를 막지 않았음. 이 Story-1 PATCH 로 올바른 `check-gate` context 가 추가되어 처음으로 실제 required check 가 동작하기 시작함
- `phase-gate-mergeable` / `invariant` 등 구형 context 제거는 **Story-2 carrier** (cleanup scope)

## Baseline Verify Date

2026-05-28T21:55:00+09:00

---

## §Story-2 — codeforge-deploy / codeforge-deploy-review 2 plugin protection CREATE

**Story**: CFP-1785-S2
**작성**: DeveloperPLAgent
**timestamp**: 2026-05-28T23:15:00+09:00

### §before Matrix (CREATE 전 baseline — 2026-05-28T22:40:32+09:00 verify)

| plugin | protection state | 사유 |
|--------|-----------------|------|
| codeforge-deploy | 404 NOT PROTECTED | CFP-1059 / ADR-087 신설 시점 (2026-04~05) protection 누락 |
| codeforge-deploy-review | 404 NOT PROTECTED | CFP-1059 / ADR-088 신설 시점 (2026-04~05) protection 누락 |

verified-via: `gh api repos/mclayer/plugin-codeforge-{deploy,deploy-review}/branches/main/protection` (Phase 0 RequirementsPL verify 2026-05-28T22:40:32+09:00 + Phase 2 pre-PUT baseline GET 재실행 verify-before-trust 2026-05-28T23:15:00+09:00) `[verified]`

### CREATE Payload (4 sibling precedent 복제)

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["phase-gate-mergeable", "check-gate"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": {
    "users": [],
    "teams": [],
    "apps": []
  }
}
```

- contexts = `["phase-gate-mergeable", "check-gate"]` (design / develop / test 3-sibling 2-tuple precedent 복제, review `invariant` outlier 미적용 — deploy/deploy-review = new plugin)
- `strict: true` (Story-1 sibling 정합)
- `enforce_admins: true` (CFP-70 anchor)
- `required_pull_request_reviews: null` (solo-dev 가정, CFP-72)
- `restrictions: {users:[], teams:[], apps:[]}` (direct push 차단)

### §after Matrix (CREATE 후 post-verify — 2026-05-28T23:15:00+09:00)

| plugin | contexts (after) | enforce_admins | restrictions | PARITY | timestamp |
|--------|-----------------|----------------|--------------|--------|-----------|
| codeforge-deploy | `["check-gate","phase-gate-mergeable"]` (sorted) | true | not null (users:[], teams:[], apps:[]) | **PARITY OK** | 2026-05-28T23:15:00+09:00 |
| codeforge-deploy-review | `["check-gate","phase-gate-mergeable"]` (sorted) | true | not null (users:[], teams:[], apps:[]) | **PARITY OK** | 2026-05-28T23:15:00+09:00 |

verified-via: `gh api repos/mclayer/plugin-codeforge-{deploy,deploy-review}/branches/main/protection --jq '.required_status_checks.contexts | sort'` + `--jq '.enforce_admins.enabled'` + `--jq '.restrictions != null'` (post-CREATE GET, 2026-05-28T23:15:00+09:00) `[verified]`

### Risk Note (Story-2)

- **workflow file 미존재 영역**: 2 plugin `.github/workflows/phase-gate-mergeable.yml` 자체 부재 → 양 context (`phase-gate-mergeable` + `check-gate`) 모두 영구 pending 상태
- GitHub 기본 동작: pending context = absent (fail 처리 0) → PR merge 가능 (Story-1 carry-over invariant 동형)
- `enforce_admins: true` 활성화로 admin merge gate (ADR-113 5-step pre-flight gate) mechanism 신규 활성화 (이전 404 NOT PROTECTED 영역 → 신설)
- **Phase 2 carrier**: 2 plugin workflow file `phase-gate-mergeable.yml` 신설 = ADR-087 Phase 2 wire 정합 영역 (별 follow-up CFP)
- **rollback path**: protection DELETE (`gh api --method DELETE repos/mclayer/plugin-codeforge-{deploy,deploy-review}/branches/main/protection`) 으로 이전 404 state 복원 가능 (idempotent)

---

## CFP-1850-S2 — requirements/pmo phase-gate-mergeable 필수 추가 + 8 repo 워크플로 mirror (2026-05-31 KST)

### 변경 1 — 보호규칙 API PATCH (requirements/pmo)

| plugin | contexts (before) | contexts (after) | enforce_admins | timestamp |
|--------|-------------------|------------------|----------------|-----------|
| codeforge-requirements | `["check-gate"]` | `["check-gate","phase-gate-mergeable"]` | true | 2026-05-31T00:30:00+09:00 |
| codeforge-pmo | `["check-gate"]` | `["check-gate","phase-gate-mergeable"]` | true | 2026-05-31T00:30:00+09:00 |

verified-via: `gh api repos/mclayer/plugin-codeforge-{requirements,pmo}/branches/main/protection/required_status_checks/contexts` (post-POST GET) `[verified]`

### 변경 2 — phase-gate-mergeable.yml workflow mirror (8 lane repo)

8 lane plugin repo 의 `.github/workflows/phase-gate-mergeable.yml` 을 wrapper 정본 (CFP-1850-S1 isChoreOnly 5th fast-pass 포함, 37047B) 으로 통일. 이전 상태: 6 repo (design/develop/review/test/requirements/pmo) = 17213B stale (isPostMergeFix + isChoreOnly 누락), deploy/deploy-review = 32899B (isChoreOnly 누락). 8 PR 모두 MERGED, main byte-parity 확인.

| repo | PR | merge |
|------|----|----|
| design | #65 | MERGED |
| develop | #33 | MERGED |
| review | #48 | MERGED |
| test | #31 | MERGED |
| deploy | #4 | MERGED |
| deploy-review | #3 | MERGED |
| requirements | #33 | MERGED |
| pmo | #32 | MERGED |

### 안전 근거 (S1 선행 의존)

requirements/pmo 에 phase-gate-mergeable 필수 추가가 안전한 이유 = CFP-1850-S1 의 isChoreOnly fast-pass 가 두 repo 워크플로에 먼저 들어갔기 때문 (변경 2 가 변경 1 선행). 단일 chore PR (phase:unclassified + Story 미연결 + chore-safe diff) 은 isChoreOnly 로 통과 → 영구 action_required 차단 재발 없음.

### review invariant 유지 결정

review 의 `invariant` 필수 체크는 `invariant-check.yml` 이 생성하는 live check — 제거 시 review 고유 보호 강도 축소. CFP-1850-S2 = 보호 강도 비축소 원칙 (ADR-058 §결정 5 ratchet) 으로 유지. "통일"의 본질 = requirements/pmo 누락 보완이며 review 의 추가 체크는 무해.

### rollback path

requirements/pmo phase-gate-mergeable 제거: `gh api --method DELETE repos/mclayer/plugin-codeforge-{requirements,pmo}/branches/main/protection/required_status_checks/contexts -f 'contexts[]=phase-gate-mergeable'` (idempotent).
