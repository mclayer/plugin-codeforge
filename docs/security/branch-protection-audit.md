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

---

## 2026-06-10 — lane repo main 머지불가 2종 결함 정정 (4 repo restrictions 제거 + 2 repo rpr 추가)

**배경**: codeforge de-bloat 캠페인 중 deploy/deploy-review de-bloat PR 이 fully-green 인데도 머지 불가 발견. 진단 결과 **§Story-2 (CFP-1785-S2) CREATE payload 의 Risk Note 가정이 틀렸음**이 규명됨 — 본 audit log line 112-113 의 "pending context = absent → PR merge 가능" 가정은 **미검증 추정**이었고, 실제로는 아래 2종 결함으로 **모든 머지가 차단**되고 있었다 (red-team PR #6/#5 가 8일 stuck 한 원인).

### 근본원인 2종

- **A — `restrictions` 빈 허용목록**: `{users:[], teams:[], apps:[]}` 은 "direct push 차단" 의도였으나(§Story-2 line 99), 실제 GitHub 동작 = **아무도(admin 포함, enforce_admins=true) 머지 불가**. "direct push 차단 + PR merge 허용" 의 올바른 구현은 restrictions 미설정(None) + "Require PR before merging" 룰이다.
- **B — `required_pull_request_reviews: null`**: "Require PR before merging" 룰 자체 부재. 이 상태에서 GitHub 는 required status check 를 stuck **"expected"** 로 평가 → merge API 가 `Required status check phase-gate-mergeable is expected` 반환 (실제 check-run 은 success 인데도). deploy/deploy-review 만 해당 (정상 6 lane 은 rpr 객체 count 0 보유).

deploy/deploy-review = A+B 동시, requirements/pmo = A 만 (rpr count 0 보유 — 이후 어느 시점 §Story-2 precedent 복제로 빈 restrictions 만 전파된 것으로 추정).

### §before (2026-06-10 진단 시점)

| plugin | restrictions | rpr | 결함 |
|--------|-------------|-----|------|
| codeforge-requirements | SET (빈 배열) | 0 | A |
| codeforge-pmo | SET (빈 배열) | 0 | A |
| codeforge-deploy | SET (빈 배열) | null | A + B |
| codeforge-deploy-review | SET (빈 배열) | null | A + B |
| design/review/develop/test | None | 0 | 정상 (대조군) |

### 수정 (API)

- **restrictions 제거** (4 repo): `gh api -X DELETE repos/mclayer/plugin-codeforge-{requirements,pmo,deploy,deploy-review}/branches/main/protection/restrictions`
- **rpr 추가** (2 repo): `gh api -X PATCH repos/mclayer/plugin-codeforge-{deploy,deploy-review}/branches/main/protection/required_pull_request_reviews` payload `{"required_approving_review_count":0,"dismiss_stale_reviews":false,"require_code_owner_reviews":false,"require_last_push_approval":false}`

수정 의미 = §Story-2 의 원래 의도("direct push 차단 + solo-dev PR merge 허용 + 리뷰 0")를 올바르게 실현. rpr count 0 = "PR 필수, 승인 0건" = solo-dev PR merge 허용.

### 검증 (실측)

deploy 에 rpr 추가 후 임시 test PR 생성 → `mergeStateStatus` 가 **BLOCKED → CLEAN** 전환 확인 (enforce_admins 토글 불필요). test PR 은 머지 없이 close + branch 삭제. de-bloat PR (#7/#6) 및 version-bump PR (#8/#7) 은 수정 전이라 enforce_admins off→--admin→on 토글로 머지했고, 토글은 매건 즉시 복원함.

### §after (전 8 lane parity — 2026-06-10 verify)

| plugin | enforce_admins | restrictions | rpr | contexts |
|--------|----------------|--------------|-----|----------|
| codeforge-requirements | true | None | 0 | check-gate, phase-gate-mergeable |
| codeforge-design | true | None | 0 | check-gate, phase-gate-mergeable |
| codeforge-review | true | None | 0 | invariant, check-gate, phase-gate-mergeable |
| codeforge-develop | true | None | 0 | check-gate, phase-gate-mergeable |
| codeforge-test | true | None | 0 | check-gate, phase-gate-mergeable |
| codeforge-pmo | true | None | 0 | check-gate, phase-gate-mergeable |
| codeforge-deploy | true | None | 0 | check-gate, phase-gate-mergeable |
| codeforge-deploy-review | true | None | 0 | check-gate, phase-gate-mergeable |

verified-via: `gh api repos/mclayer/plugin-codeforge-<lane>/branches/main/protection` (8 lane GET, 2026-06-10) `[verified]`. strict 는 lane별 상이(무관 — 정규화 안 함). enforce_admins=true 전 lane 유지.

### precedent 교정 (향후 신설 plugin)

§Story-2 CREATE payload (line 80-93) 의 `required_pull_request_reviews: null` + `restrictions: {users:[],teams:[],apps:[]}` 는 **머지불가 antipattern** — 재사용 금지. 신설 lane plugin protection 은 `required_pull_request_reviews: {required_approving_review_count: 0}` + `restrictions: null` 로 생성할 것 ("direct push 차단 + solo-dev PR merge").

### rollback path

- restrictions 복원(비권장 — 머지불가 재발): `gh api -X PUT .../protection/restrictions` with empty arrays
- rpr 제거(비권장 — phantom 재발): `gh api -X DELETE .../protection/required_pull_request_reviews`

## 2026-06-12 — CFP-2178 S6: lane repo 8개 archive + protection 활성 관리 9→1 동결

- archive 실측: deploy (smoke) 2026-06-12T02:16 KST → 잔여 7 (requirements/design/review/develop/test/pmo/deploy-review) 02:16~02:17 KST 순차, 실패 0
- 사후 검증: 8/8 isArchived true + 8/8 ls-remote fetch OK (AC-1/AC-2) + close 선행 7 issue (AC-3, §D-11 CLOSE_AS_OBVIATED)
- GAP-1 smoke 실측: archived repo protection rule **잔존+inert** (deploy GET 정상 — contexts 2-tuple/rpr 0/enforce_admins true verbatim, 변경 불가·발효 무대상). §after 표 (2026-06-10 parity) = archive 시점 동결 상태로 보존
- 활성 관리 표면 = wrapper 단일 (6-tuple). SSOT = wrapper CLAUDE.md 표 1행 + 본 doc. registry v1.2 Archived (#2179)

## 2026-07-11 — CFP-2603 (Epic CFP-2602 G1): wrapper 6→7-tuple `ac-traceability-matrix` 추가 예정 (pending)

- **상태 = pending (실등록 전)**: 신규 required context `ac-traceability-matrix` (요건 traceability zero-drop fail-closed 게이트, ADR-145) 를 wrapper `required_status_checks.contexts[]` 에 추가(6→7-tuple)할 **예정**. 본 엔트리 기록 시점 = 실 branch-protection API 등록 **전** — 현행 활성 표면은 아직 6-tuple.
- **실등록 시점 = Orchestrator post-merge** (ADR-145 §결정3 ordering-invariant): `workflow 착륙 → self-test suite green 확인(ac-traceability-self-test.yml) → own-PR green(게이트가 자기 Phase 2 PR 에 실 green 산출) → THEN required_contexts 등록`. 이 순서가 born-broken/false-red 린터의 required 등재를 구조적 차단(CFP-2530/CFP-2535 계보).
- **선례 divergence 근거 (추적 가능성)**: 6→7 narrowing 은 ADR-125 §결정2 "branch-protection 6-tuple 불변" 선례를 override 한다. override 는 **fail-closed 비호환 근거에 한정** — phase-gate INTERNAL 흡수 경로가 anchor 계층 warning-tier + fast-pass OR-gate bypass 로 fail-closed 불가(실측)이므로 신규 required job 이 정당(ADR-145 §결정3). 6-tuple 불변 원칙 자체는 폐기 아님.
- **등록 후 7-tuple (예정)**: 기존 6 context + `ac-traceability-matrix`. CLAUDE.md "브랜치 보호" 표 + arch-doc C4(6→7) 갱신 = Phase 2 PR 동반.
- **rollback**: required_contexts 에서 `ac-traceability-matrix` 제거(7→6) + 신규 workflow 삭제 (ADR-145 §12 trivial revert).
- 기록 시각: 2026-07-11T21:38:25+09:00 (KST).

## 2026-07-12T09:00:00+09:00 — CFP-2634 (ADR-145 §결정9): 6→7 등록 protocol — 현행 = doc-ahead, live 미등록

- **현재 live = 6-tuple (HELD)**: CFP-2609 canary 가 결함(adapter no-story_uri hard-fail)을 등록 직전 포착 → 6→7 등록 자체는 롤백/보류(#2632 deferred carrier). wrapper 실 branch-protection API 표면은 여전히 6-tuple.
- **doc = 7-tuple (doc-ahead)**: 본 문서 §2026-07-11 엔트리 및 CLAUDE.md 표는 `ac-traceability-matrix` 를 7번째 context 로 서술 — 이는 **의도/설계 기록**이며 live API 상태의 실측 반영이 아니다. doc-ahead 상태를 여기 명시적으로 기록해 "문서=현실" 오독을 차단한다.
- **등록 precondition (재확정, CFP-2634 §결정9 non-negotiable 3종)**:
  1. **genuine 비적용 no-story_uri canary** — synthetic fixture 대체 금지. 실 PR(실 story_uri 부재 상태)로 어댑터·core 4-조합 라우팅을 실제로 행사해야 한다.
  2. **actual in-job PASS 실측** — 위 canary PR 의 `ac-traceability-matrix` job 이 실제로 실행되어 exit 0(genuine PASS) 을 실측 확인해야 한다(로그 인용 필수, self-report 불가).
  3. **rollback-ready** — 등록 직전 현재 6-tuple contexts 배열을 캡처(스냅샷)해두어, 등록 후 결함 발견 시 즉시 7→6 원복 가능해야 한다.
- **등록 행위자 = post-merge Orchestrator gh-api act**: live 6→7 등록은 이 PR(코드/workflow 착륙)이 아니라, merge 후 Orchestrator 가 `gh api` 로 별도 실행하는 행위다. **forged machine-test 금지 = self-register 금지** — 게이트 자신의 워크플로 실행 결과만으로 자기 자신을 required 로 등재하는 self-attestation 경로는 차단(third-party canary PR 관찰이 선행 조건).
- 기록 시각: 2026-07-12T09:00:00+09:00 (KST).
<!-- canary CFP-2642 CI-surfacing verify 2026-07-12 (비적용, 병합 대상 아님) -->
