---
adr_number: 24
title: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred
status: Accepted
category: governance
date: 2026-05-03
amended_by: CFP-134
amended_date: 2026-05-08
amendments:
  - by: "CFP-134"
    date: "2026-05-08"
    scope: "hierarchical branch convention 추가 — flat cfp-NNN 에서 cfp-NNN[/<lane>[/<sub>]] 계층까지 분기 가능"
related_files:
  - CLAUDE.md
  - docs/consumer-guide.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
---

# ADR-024: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred

## 상태

Accepted (2026-05-03 — CFP-66 carrier)

## 컨텍스트

User directive 2026-05-03 (CFP-65 작업 중간):

> "codeforge로 작업하는 모든 변경사항은 story 단위 이하에서 브랜치를 분리하여 작업 수행해 main 브랜치에 머지할 수 있도록 한다 main브랜치에 직접 수정하는 것을 금지한다. 이유는 스토리 단위 별로 병렬 수정이 가능하도록 하기 위함이다."

현재 practice (2026-05-02 ~ 03 dogfood 운영):
- CFP-63 / CFP-64 / CFP-65 모두 feature branch + PR 경유 — 행동상 직접 push 사례 없음
- main branch protection 설정: `enforce_admins: false`, `restrictions: null` — admin (mccho8865) 가 main 직접 push 가능, 단 운영 중 직접 push 미사용

Gap: 행동상 충족 / policy enforcement 미완. solo-dev 가 우연히 main commit 하거나 emergency hotfix 명목으로 직접 push 시 governance 부재.

추가 제약 (Sonnet decider CFP-66-001 검토):
- 6+ pre-existing CI fail 존재 (inter-plugin-drift / workflow yaml regex 등) — `enforce_admins:true` 즉시 적용 시 ANY PR merge 차단 (deadlock).
- consumer 측 branch policy 권장 (consumer-guide.md §2e) 와 wrapper repo 자체 policy 분리 필요 — 두 scope 가 혼재 시 governance 모호.

## 결정

### 결정 1: Story-scoped feature branch + PR 경유 의무

모든 wrapper 변경 (codeforge family 자체 dogfood 작업 포함) = Story-scoped feature branch + PR 경유. main 직접 push 금지 — 정책 + 물리 강제.

권장 branch naming (강제는 Phase 2):
- `cfp-NNN[-<slug>]` (가장 일반적)
- `cfp-NNN-<phase>` (multi-phase Story 의 Phase 분리 시 — 예: `cfp-65-story-flow-phase1`)
- 동등 naming 도 허용 — Phase 2 에서 enforcement (Option G) 결정.

### 결정 2: main branch protection `restrictions:{users:[],teams:[],apps:[]}` 강제 (Phase 1)

`gh api -X PUT repos/mclayer/plugin-codeforge/branches/main/protection` 의 `restrictions` field 를 `null` → `{users:[],teams:[],apps:[]}` 로 변경. 결과: main 에 직접 push 권한이 누구에게도 없음 — PR 경유 merge 만 허용.

### 결정 3: `enforce_admins: false` Phase 1 유지 (deadlock 회피)

`enforce_admins: true` 적용 시 admin 도 required status check fail bypass 불가. 현재 6+ pre-existing CI fail 환경에서 ANY PR merge 차단 = 즉시 deadlock. Phase 2 (CI green 100% 달성 후 별도 CFP) 까지 `enforce_admins: false` 유지 — admin (mccho8865) 가 PR-based admin merge 로 deferred CI fail bypass 가능.

### 결정 4: Phase 2 enforcement 후속 CFP — CI green 전제

Phase 2 transition 조건 = 6+ pre-existing CI fail 전부 해소. 별도 CFP 로 다음 항목 평가:
- `enforce_admins: true` 전환
- GitHub Rulesets (legacy branch protection 대체)
- Story branch naming enforcement (e.g. `^cfp-\d+(-.*)?$` regex)
- PR source-branch non-main enforcement (자동화 추가)

Phase 2 도입 순서: Rulesets 검증 → naming rule 정착 → enforcement 자동화 → enforce_admins:true 최종 전환.

### 결정 5: Consumer policy 분리 + cross-reference

Wrapper repo (mclayer/plugin-codeforge) governance vs consumer-guide.md §2e (다운스트림 consumer 권장 settings) 분리. consumer 는 자기 repo 의 branch protection 을 자기 환경 (solo-dev / 1-2인 팀 / 다인 contributor) 에 맞게 설정 — wrapper governance 와 별도.

CLAUDE.md 에 본 ADR-024 cross-ref 1줄 + consumer-guide.md §2e cross-ref. 두 SSOT 의 분리 명시.

### 결정 6: Emergency hotfix 도 PR 경유 의무 (no exception)

운영 장애 hotfix 도 본 정책 예외 없음. hotfix branch (e.g. `hotfix-<id>`) + PR 경유 — admin merge via PR API 로 신속 merge 가능. 직접 push 우회 금지.

## 결과

- 직접 push 물리 차단 → governance 강화, solo-dev 우연 commit 차단
- PR-based admin merge 패턴 무영향 (`enforce_admins:false` 유지로 deferred CI fail bypass 가능)
- 병렬 modification 지원: 여러 Story-scoped branch 동시 작업 + 독립 PR 가능 (개별 PR 의 CI 검증 / merge 순서 자유)
- ADR governance trail — Phase 2 transition 의 명확한 trigger / 조건 추적 가능
- consumer 측은 자기 환경에 맞는 별도 protection — wrapper 정책 강요 X

## 관련 파일

- `CLAUDE.md` — Story 작성 의무 섹션에 ADR-024 cross-ref 추가
- `docs/consumer-guide.md` — §2e 와 cross-ref 분리 명시
- GitHub branch protection (api operation, file 외부) — `restrictions:{users:[],teams:[],apps:[]}` (Phase 1) + **`enforce_admins: true` (Phase 2 / CFP-70)** 적용
- ADR-013 (dogfood-out policy) — Story 작성 의무 root principle
- ADR-022 (Sonnet Decider) — 본 ADR 의 결정 protocol

## Phase 2 partial impl (CFP-70 — 2026-05-03)

CFP-70 (Sonnet decider CFP-70-001 pick=A + CFP-70-002 sub-pick=B minimal) 가 Phase 2 의 부분 적용:

- ✅ **`enforce_admins: true`** — 적용. admin (mccho8865) 도 4 required check (phase-gate-mergeable / doc frontmatter / doc section / invariant-check) 모두 통과 의무.
- ⏸️ **GitHub Rulesets** — solo-dev 가정 하 ROI 낮음. defer.
- ⏸️ **Branch naming auto enforcement** — 정책 도덕적 의무 (본 ADR §결정 1) 충분. defer.
- ⏸️ **PR source-branch non-main enforcement** — `restrictions:{users:[],teams:[],apps:[]}` 가 이미 covered. 추가 enforcement 불필요.

Phase 2 sequence 해석 ("Rulesets 검증 → naming → enforcement 자동화 → enforce_admins:true"): 결정 4 의 "검증" = "evaluate + skip-if-not-needed". Solo-dev evaluation 결과 = skip — sequence 위반 아님.

**가정 변경 시 재검토 의무**: contributor 추가 (외부 PR 가능성 발생) 시점에 Rulesets shadow + branch naming auto enforcement 별도 CFP 추진 의무. 본 ADR Phase 2 partial 명시 = 재검토 trigger.

Rollback runbook (emergency only):

```bash
# enforce_admins:false 재전환 (admin bypass 복원)
gh api -X PUT repos/mclayer/plugin-codeforge/branches/main/protection \
  --input <(현재 protection JSON 단 enforce_admins:false)
```

bypass 가능 admin = mccho8865 (mclayer org owner).

## solo-dev governance gap 영구 해결 (CFP-72 — 2026-05-04)

CFP-71 (PR #149) merge 시 발견 — solo-dev 환경 + `enforce_admins:true` + `require_code_owner_reviews:true` + `required_approving_review_count:1` = **본인 PR 본인 approve 불가** (GitHub policy: `Can not approve your own pull request`). CFP-66/70 검토 시 누락된 edge case. 매 PR 마다 `enforce_admins:false` + review requirement off 임시 bypass + 즉시 복원 = 1-2분 governance gap 누적.

CFP-72 (CFP-72-001 옵션 A 사용자 결단) 가 영구 해결:

- ✅ `required_approving_review_count: 0` — review 강제 해제
- ✅ `require_code_owner_reviews: false` — CODEOWNERS 강제 해제
- ✅ `enforce_admins: true` — 유지 (admin 도 4 required check 통과 의무)
- ✅ `restrictions: {users:[], teams:[], apps:[]}` — 유지 (direct push 차단)
- ✅ 4 required status check — 유지 (phase-gate-mergeable / doc frontmatter / doc section / invariant-check)

CODEOWNERS file 자체는 **유지** — auto review request 발생 = 도덕적 governance (PR open 시 architects team 자동 통보, merge 강제 요건 없음).

**가정 변경 시 재검토 의무**: contributor 추가 (외부 PR 가능성 발생) 시점에 `require_code_owner_reviews:true` + `required_approving_review_count:1` 복원 의무. 본 § = 재검토 trigger.

CFP-72 본 PR 자체가 governance gap **마지막** 임시 bypass 사용 사례 — merge 후 영구 해결 적용 → 재발 0.

## Amendment 1 — Hierarchical branch convention (CFP-134, 2026-05-08)

### 컨텍스트

Agent teams 적극 도입 (CFP-137) + worktree infrastructure (CFP-136) 도입 시 1 Story = N teammate 가 자기 sub-branch 위에서 병렬 작업. flat naming (`cfp-NNN[-slug]`) 으로는 lane / sub-task 분기 표현 불가. 사용자 directive (CFP-134 Epic, 2026-05-08): "Epic > Story > sub... 이렇게 있는 경우 branch 를 하위 생성하여 agent 내에서 적극적으로 병렬 작업".

### Amendment

기존 §결정 1 의 branch naming 확장:

```yaml
naming_convention:
  story_root: cfp-NNN[-slug]              # 기존 — 변경 없음
  lane: cfp-NNN/<lane-name>               # 신규 — lane 단위 sub-branch
  sub_task: cfp-NNN/<lane-name>/<sub-name>  # 신규 — deputy / role:dev 등 sub-task
  fix_iter: cfp-NNN/fix-iter-<N>          # 신규 — FIX iteration 임시 branch
  retro: cfp-NNN/retro                    # 신규 — retro 작업 임시 branch

example_paths:
  - cfp-135                               # Story root
  - cfp-135-foundation                    # Story root with slug
  - cfp-NNN/design                        # design lane sub-branch
  - cfp-NNN/design/chief                  # design lane chief author sub-branch
  - cfp-NNN/design/mapper                 # design lane CodebaseMapper deputy sub-branch
  - cfp-NNN/code-review/codex-worker      # code review lane Codex worker sub-branch
```

### 적용 규칙

- 모든 sub-branch 는 자기 worktree (CFP-136 infrastructure) 에서 작업 — file 충돌 0
- Lane 완료 시 sub-branch → lane branch sequential merge → Story root branch merge → main PR
- GitOpsAgent (CFP-139) 가 worktree lifecycle + sequential merge 담당
- Phase 2 enforcement (branch naming auto enforcement) 는 별도 CFP — solo-dev 환경 deferred (현재 ADR-024 결정 4)

### Compatibility

기존 flat naming `cfp-NNN[-slug]` 그대로 유효 — story root branch 로 사용. 신규 hierarchical 은 sub-branch 영역 추가만.

### Related

- CFP-134 Epic spec: `<internal-docs>/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md` §3.4
- CFP-136 (worktree infrastructure) — 본 amendment 의 prerequisite
- CFP-137 (agent teams 적극 도입) — 본 amendment 의 use case
- CFP-139 (GitOpsAgent) — 본 amendment 의 enforcement
