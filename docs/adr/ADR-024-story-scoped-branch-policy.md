---
adr_number: 24
title: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred
status: Accepted
category: governance
date: 2026-05-03
is_transitional: false
amended_by: CFP-845
amended_date: 2026-05-17
amendments:
  - by: "CFP-134"
    date: "2026-05-08"
    scope: "hierarchical branch convention 추가 — flat cfp-NNN 에서 cfp-NNN[/<lane>[/<sub>]] 계층까지 분기 가능"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hierarchical branch convention 은 영구 SSOT 확장."
  - by: "CFP-280"
    date: "2026-05-11"
    scope: "required_status_checks.contexts drift invariant + branch-protection-manifest.yaml SSOT + branch-protection-drift-check.yml 자동화"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). drift invariant 는 영구 enforcement."
  - by: "CFP-389"
    date: "2026-05-11"
    scope: "audit-trailed exception channel = hotfix-bypass:* label family (carrier ADR-060) — §결정 6 의 evidence-enforceable mechanical check 호환"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hotfix-bypass label family 자체는 ADR-060 framework 와 연동된 영구 channel — 개별 evidence check entry 의 enforce 승격 시점에만 활성."
  - by: "CFP-426"
    date: "2026-05-12"
    scope: "§결정 6.A per-entry namespace 의 4 신규 `hotfix-bypass:worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}` label entry 추가 (ADR-040 Amendment 3 동반 / CFP-425 Epic Story 1) — `hotfix-bypass:adr-sunset` 패턴 직접 mirror, 단일 audit lint `scripts/check-bypass-audit-comment.sh` reuse."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 4 worktree-first label = §결정 6.A per-entry namespace 의무의 영구 확장."
  - by: "CFP-481"
    date: "2026-05-12"
    scope: "Amendment 4 — §결정 6.A per-entry namespace 의 7번째 신규 `hotfix-bypass:auto-phase-label` label entry 추가 (ADR-060 Amendment 4 동반 — 3rd warning-tier entry `auto-phase-label`) + §결정 6.A.1 (신설) branch → phase mapping 표 SSOT (cfp-NNN[/<lane>[/<sub>]] hierarchical → phase:* 8 label mapping verbatim, ADR-024 Amendment 1 hierarchical convention 의 직접 확장)."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hotfix-bypass:auto-phase-label = §결정 6.A per-entry namespace 의무의 영구 확장. branch → phase mapping 표 = ADR-024 Amendment 1 hierarchical convention 의 영구 SSOT 명세화."
  - by: "CFP-582"
    date: "2026-05-13"
    scope: "Amendment 5 — §결정 6.A per-entry namespace 의 12번째 신규 `hotfix-bypass:debate-convergence-quality` label entry 추가 (ADR-059 Amendment 2 §결정 8 동반 — convergence_quality_invariant 첫 debate 영역 warning-tier entry `debate-convergence-quality-marker-presence`, ADR-060 framework 정합). prior art `hotfix-bypass:adr-sunset` (CFP-389) + 4 `hotfix-bypass:worktree-*` (CFP-426) + `hotfix-bypass:auto-phase-label` (CFP-481) + `hotfix-bypass:claude-md-line-cap` (CFP-506) + `hotfix-bypass:sibling-pr-author-check` (CFP-521) + `hotfix-bypass:workflow-permissions` (CFP-530) + `hotfix-bypass:workflow-yaml-parse` (CFP-583) 직접 mirror, 단일 audit lint `scripts/check-bypass-audit-comment.sh` reuse."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hotfix-bypass:debate-convergence-quality = §결정 6.A per-entry namespace 의무의 영구 확장 (debate 영역 첫 family member)."
  - by: "CFP-825"
    date: "2026-05-17"
    scope: "Amendment 6 — §결정 6.A per-entry namespace 누적 사용 카운터 lint (bypass-label-counter, 63번째 evidence-checks-registry entry, warning tier first iteration) + 31번째 family member `hotfix-bypass:bypass-label-counter` (self-meta loop 회피) + 32번째 family member `hotfix-bypass:exempt:<entry>` template (rare 정당 declare 채널, narrative audit trail mechanical enforce = 후속 carrier). ratchet 룰: per-(plugin, label) signature ≥3 reach-merged PR 누적 시 carrier Issue 자동 발의 + dedup (window=all-time / dedup_unit=PR number / exempt 2종). CFP-771 retro §8 제안 1 carrier — exception → norm mutation 위험 누적 monitoring 부재 차단."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). bypass-label-counter = forbid scope 확장 (ratchet-up 강화 방향, ADR-058 §결정 5 정합). 2 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장 (self-meta + rare 정당 declare 2종 channel)."
  - by: "CFP-841"
    date: "2026-05-17"
    scope: "Amendment 7 — §결정 6.A per-entry namespace 의 34번째 신규 `hotfix-bypass:corpus-claim-verify` + 35번째 신규 `hotfix-bypass:cross-plugin-ownership-verify` family member 추가 (ADR-082 Amendment 1 carrier — §결정 6 behavioral→mechanical 전환, ADR-060 framework 2 신규 warning-tier evidence-checks-registry entry `corpus-claim-verify` + `cross-plugin-ownership-verify`). write-time semantic truth verify 영역 첫 family member."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 2 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장 (write-time semantic truth verify 영역 첫 진입)."
  - by: "CFP-845"
    date: "2026-05-17"
    scope: "Amendment 8 — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 (CFP-825 Amendment 6 §scope_boundary 의 4 out-of-scope 후속 carrier 영역 중 3 즉시 통합, 4번째 `blocking-on-merge tier 격상` = Story-2 #861 RESERVED 별 carrier evidence-gated 분리). §결정 6.A.3 (신설) per-plugin 전체 누적 카운터 ratchet — 단일 plugin 의 모든 hotfix-bypass:* family entry 누적 ≥5 reach-merged PR (signature = plugin-only, dedup_unit = PR number, window = all-time) 시 carrier Issue 자동 발의. §결정 6.A.4 (신설) `[bypass-justification]` PR comment marker mechanical enforce — hotfix-bypass:* label 부착 PR 의 marker presence grep-only lint (semantic adequacy 불가 = false-positive risk 명시, reviewer responsibility). §결정 6.A.5 (신설) cross-repo bypass counter extension — wrapper (plugin-codeforge) 단일 → internal-docs / marketplace sibling repo 3-repo 동시 cover, signature = (repo, plugin, label) 3-tuple, 단일 PAT (CODEFORGE_CROSS_REPO_PAT) reuse. §결정 6.A (확장) `hotfix-bypass:per-plugin-cumulative-counter` 37번째 + `hotfix-bypass:bypass-justification-marker` 38번째 + `hotfix-bypass:cross-repo-bypass-counter` 39번째 family member."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 3 신규 sub-decision = bypass-as-norm mutation 누적 monitoring 의 ratchet-up 강화 방향 (per-entry → per-plugin / narrative audit / cross-repo 확장). ADR-058 §결정 5 정합. 3 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장."
related_files:
  - CLAUDE.md
  - docs/consumer-guide.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-040-worktree-convention.md
  - docs/adr/ADR-059-debate-protocol-v1.md
  - docs/adr/ADR-060-evidence-enforceable-promotion-framework.md
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - docs/inter-plugin-contracts/label-registry-v2.md
  - templates/branch-protection-manifest.yaml
  - templates/github-workflows/branch-protection-drift-check.yml
  - templates/github-workflows/debate-convergence-quality.yml
  - templates/github-workflows/bypass-label-counter.yml
  - templates/github-workflows/per-plugin-cumulative-counter.yml
  - templates/github-workflows/bypass-justification-marker.yml
  - templates/github-workflows/cross-repo-bypass-counter.yml
  - scripts/check-bypass-label-counter.py
  - scripts/check-bypass-label-counter.sh
  - scripts/check-per-plugin-cumulative-counter.py
  - scripts/check-per-plugin-cumulative-counter.sh
  - scripts/check-bypass-justification-marker.py
  - scripts/check-bypass-justification-marker.sh
  - scripts/check-cross-repo-bypass-counter.py
  - scripts/check-cross-repo-bypass-counter.sh
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A 의무 — 본 ADR-024 Amendment 4 (CFP-481, 2026-05-12)
  # 가 ADR-040 Amendment 3 발효 (CFP-426 Phase 1 PR merge) 이후 작성된 normative
  # ADR amendment 이므로 §결정 7.C retroactive 면제 외 — Amendment 4 부터 mandate 적용.
  # 기존 ADR-024 Amendment 1·2·3 = retroactive 면제 (§결정 7.C 정합).
  - action: auto-phase-label
    status: deferred-followup     # registry yaml row append = CFP-481 Phase 2 PR scope
    target_section: §결정 6.A.1   # branch → phase mapping 표 SSOT (1순위 inference 로직)
  # Amendment 6 (CFP-825, 2026-05-17) — 본 Amendment 의 mechanical enforcement self-application
  - action: bypass-label-counter
    status: deferred-followup     # registry yaml row append = CFP-825 Phase 2 PR scope
    target_section: §결정 6.A.2   # per-entry namespace 누적 사용 카운터 lint ratchet 룰 (3-tuple: threshold / dedup / window)
  # Amendment 8 (CFP-845, 2026-05-17) — bypass-as-norm-mutation 후속 escalation 3 sub-decision self-application
  - action: per-plugin-cumulative-counter
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint+workflow wire = Phase 2 PR scope
    target_section: §결정 6.A.3   # per-plugin 전체 누적 카운터 ratchet (단일 plugin scope 분산 bypass 탐지)
  - action: bypass-justification-marker
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint+workflow wire = Phase 2 PR scope
    target_section: §결정 6.A.4   # PR comment marker grep-presence lint (false-positive risk 명시, reviewer responsibility)
  - action: cross-repo-bypass-counter
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint+workflow wire = Phase 2 PR scope
    target_section: §결정 6.A.5   # cross-repo extension (wrapper + internal-docs + marketplace 3-repo signature)
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

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (permanent governance carrier — Story-scoped branch policy 자체 가 codeforge 의 영구 결제 룰). ADR-058 §결정 7 보안 ADR default presumption = `false` 정합 (security & governance carrier).

## 관련 파일

- `CLAUDE.md` — Story 작성 의무 섹션에 ADR-024 cross-ref 추가
- `docs/consumer-guide.md` — §2e 와 cross-ref 분리 명시
- GitHub branch protection (api operation, file 외부) — `restrictions:{users:[],teams:[],apps:[]}` (Phase 1) + **`enforce_admins: true` (Phase 2 / CFP-70)** 적용
- ADR-013 (dogfood-out policy) — Story 작성 의무 root principle
- ADR-022 (Sonnet Decider) — 본 ADR 의 결정 protocol
- ADR-058 (sunset criteria mandate) — `is_transitional: false` classification 적용
- ADR-060 (evidence-enforceable framework) — Amendment 3 의 `hotfix-bypass:*` label family carrier

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

## Amendment 2 — required_status_checks.contexts drift invariant (CFP-280, 2026-05-11)

### 컨텍스트

CFP-136 (worktree infrastructure) 도입 후 `gh api` 로 branch protection 을 직접 조회했을 때, `required_status_checks.contexts` 에 3개 stale context 가 잔존함을 확인:

| stale context | 원인 |
|---|---|
| `doc frontmatter schema (CFP–28 — strict)` | 하이픈 문자 em-dash(`–`, U+2013) vs workflow job name의 hyphen(`-`, U+002D) 불일치 |
| `doc section schema (CFP–28 — strict)` | 동일 em-dash 문자 불일치 |
| `doc-locations-check / validate` | CFP-276 이후 해당 workflow job 삭제됨 — orphan |

실제 workflow job name (2개) 은 `doc frontmatter schema (CFP-28 — strict)` / `doc section schema (CFP-28 — strict)` (ASCII hyphen) 이므로, branch protection 에 등록된 em-dash 변형은 영구 mismatch → 해당 check 가 GitHub 에서 "expected" 상태로 표시되지 않아 PR merge 가 잠재적으로 차단될 수 있음.

CFP-136 align fix 시 3개 stale 제거 + 올바른 2개 추가 완료. 그러나 이 drift 재발 방지를 위한 **자동화 invariant 부재** — 본 Amendment 2 가 gap 해소.

현재 확정 4 required context:

```
phase-gate-mergeable        # phase-gate-mergeable.yml checks.create (동적 생성)
invariant-check             # invariant-check.yml job id (explicit name: 없음)
doc frontmatter schema (CFP-28 — strict)  # check-doc-frontmatter.yml job name
doc section schema (CFP-28 — strict)      # check-doc-section-schema.yml job name
```

### Amendment

#### §결정 A: `templates/branch-protection-manifest.yaml` SSOT 신설

branch protection 에 등록 필요한 `required_status_checks.contexts` 를 SSOT 파일로 관리. consumer 가 overlay 로 자기 context 추가 가능 (확장 only — 기본 4개 삭제 불허).

```yaml
# templates/branch-protection-manifest.yaml
# consumer overlay: .claude/_overlay/branch-protection-manifest.yaml 로 확장 가능
required_status_checks:
  contexts:
    - name: "phase-gate-mergeable"
      type: dynamic          # checks.create API (phase-gate-mergeable.yml)
      source_workflow: templates/github-workflows/phase-gate-mergeable.yml
    - name: "invariant-check"
      type: workflow-job-id  # job id (explicit name: 없음)
      source_workflow: templates/github-workflows/invariant-check.yml
    - name: "doc frontmatter schema (CFP-28 — strict)"
      type: workflow-job-name
      source_workflow: templates/github-workflows/check-doc-frontmatter.yml
    - name: "doc section schema (CFP-28 — strict)"
      type: workflow-job-name
      source_workflow: templates/github-workflows/check-doc-section-schema.yml
```

#### §결정 B: `templates/github-workflows/branch-protection-drift-check.yml` 신설

자동화 drift 감지. 트리거: `.github/workflows/**` 또는 `templates/branch-protection-manifest.yaml` 변경 push to main + 주 1회 schedule (`cron: '0 9 * * 1'`) + `workflow_dispatch`.

동작:
1. `gh api` 로 `repos/{owner}/{repo}/branches/main/protection/required_status_checks` 조회 → 실제 contexts 목록 추출 + sort
2. manifest yaml 에서 기대 contexts 추출 + sort
3. `comm -23` (stale: 실제에 있으나 manifest에 없는 것) + `comm -13` (missing: manifest에 있으나 실제에 없는 것) 비교
4. stale 또는 missing 존재 시 → `exit 1` (CI fail)

#### §결정 C: drift 발견 시 수정 절차 (운영 규칙)

1. manifest yaml 에 기대 contexts 반영 (정책 반영)
2. `gh api -X PUT repos/.../branches/main/protection` 로 실제 branch protection 동기
3. drift-check workflow 재실행 PASS 확인
4. 두 변경이 동일 PR 에 포함 의무 (SSOT 와 실제 동기 원자적 보장)

### Compatibility

- 기존 4 required check 변경 없음 — 단 SSOT 위치가 implicit → `templates/branch-protection-manifest.yaml` explicit 으로 전환
- 기존 `required-workflow-drift-check.yml` (enterprise required workflow drift) · `rulesets-drift-check.yml` (GitHub Rulesets drift) 와 별도 목적 — 중복 없음
- consumer overlay 확장 방식 → consumer 는 자기 context 추가만 가능 (core 4개 삭제 불허)

### Related

- CFP-280 carrier story
- `templates/branch-protection-manifest.yaml` — §결정 A SSOT
- `templates/github-workflows/branch-protection-drift-check.yml` — §결정 B 자동화
- CFP-136 (worktree infrastructure) — 3 stale context 최초 발견 trigger

## Amendment 3 — Audit-trailed exception channel via `hotfix-bypass:*` label family (CFP-389, 2026-05-11)

### 컨텍스트

ADR-024 §결정 6 ("emergency hotfix 도 PR 경유 의무, no exception") + `enforce_admins: true` (CFP-70, Phase 2 partial) + `restrictions: {users:[], teams:[], apps:[]}` (CFP-66) 조합 결과: enforce mode 진입한 required check 가 운영 장애 hotfix PR 을 차단 시 admin override 우회 채널 부재 → deadlock 위험.

CFP-389 (ADR-060 carrier — evidence-enforceable promotion framework) 가 첫 evidence check (`scripts/check-adr-sunset-criteria.sh`) 도입 시 동일 deadlock pattern 재발 차단을 위해 audit-trailed exception channel 정식 도입 결정 (사용자 ESCALATE Option A).

### Amendment

본 Amendment 3 은 §결정 6 보완 — emergency hotfix PR 경유 의무 유지하면서 evidence-enforceable check 한정 audit-trailed bypass channel 도입:

#### §결정 6.A: `hotfix-bypass:*` label family = audit-trailed exception channel

evidence-enforceable framework (ADR-060) 의 개별 evidence check 가 enforce mode 진입한 후, 운영 장애 hotfix 가 정책 위반을 강제하는 경우 → `hotfix-bypass:<entry-name>` label 부착으로 해당 check skip + audit trail 자동 발의:

- **label naming**: `hotfix-bypass:<entry-name>` family. 첫 entry = `hotfix-bypass:adr-sunset` (ADR-060 §결정 7).
- **권한자**: repo admin only. solo-dev 환경 = 사용자 본인 (mccho8865). contributor 추가 시 재논의 (별도 carrier).
- **scope 통제**: per-entry namespace 분리 (registry entry `bypass_label` 필드 per-entry). 단일 global bypass label 도입 금지 (ADR-060 §대안 E 거부 사유 정합).
- **enforce mode 진입 전 (warning mode)**: bypass label 부착 시 lint workflow conditional skip — required check 부착 아님 (continue-on-error). 본 Amendment 의 protection 강화 효과는 enforce mode 진입 후 발현.
- **확장 사례 (CFP-426 / Epic CFP-425)**: 4 신규 label entry 동시 도입 — `hotfix-bypass:worktree-session-start-wire` / `hotfix-bypass:worktree-pre-checkout` / `hotfix-bypass:worktree-pre-commit-main-block` / `hotfix-bypass:worktree-spawn-evidence-cwd`. 모두 §결정 6.A per-entry namespace 정합 + ADR-040 Amendment 3 §결정 7.D self-application 의 4 evidence check entry 와 1:1 mapping. audit lint = `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art 단일 reuse — `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect).

#### §결정 6.B: PR 경유 의무 유지 (no push/merge path override)

bypass label = lint skip only. 다음 항목 미변경 (§결정 6 + CFP-66 + CFP-70 정합):

- main 직접 push 금지 (restrictions:{users:[],teams:[],apps:[]} 유지)
- 모든 변경 = feature branch + PR 경유 의무
- enforce_admins:true (admin 도 4 required check 통과 의무 — bypass label 외 check 들에는 영향 X)

bypass label 은 evidence-enforceable check 한 가지의 skip 만 제공 — branch protection의 4 core required check (phase-gate-mergeable / doc frontmatter / doc section / invariant-check) 는 우회 불가.

#### §결정 6.C: Audit trail 3중 안전망

bypass label 적용 시 다음 3중 안전망 자동 활성:

1. **Audit comment 자동 발의** (workflow level): GitHub Actions bot 이 PR comment 1개 append (schema: ADR-060 §결정 8).
   ```
   [hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox> ADR_files=<paths> timestamp=<ISO8601>
   ```
2. **Audit assertion lint**: `scripts/check-bypass-audit-comment.sh` 가 audit comment 1개 이상 존재 검증 → 부재 시 PR block.
3. **Audit log 집계**: bypass label 적용 PR list quarterly merge 시 `docs/audit/hotfix-bypass-log.md` 자동 append (별도 carrier scope — CFP-390 인벤토리 backfill 또는 신규 carrier).

#### §결정 6.D: Re-entry 안전망 (bypass PR 자체 정책 위반)

bypass label PR 안 변경 자체가 정책 위반 (예: bypass PR 의 변경 ADR 가 sunset criteria 누락) 인 재귀 시나리오 — audit comment 에 `[sunset-criteria-deferred]` 태그 자동 추가 + 후속 보완 의무 자동 Issue 발의 (CFP-390 인벤토리 backfill scope 또는 별도 carrier).

본 재귀 시나리오 미해소 상태로 다음 bypass label 적용 시 escalation 경고 (별도 lint 또는 manual review — 별도 carrier).

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) 전부 유지 — 본 Amendment 3 은 §결정 6 의 호환 channel 확장만.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check 외 lint) 에는 영향 X.
- contributor 추가 시 권한자 재논의 의무 (별도 carrier).

### Related

- ADR-060 (carrier — evidence-enforceable promotion framework SSOT) §결정 7
- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — `bypass_label` per-entry 필드 정의
- `docs/evidence-checks-registry.yaml` — `hotfix-bypass:adr-sunset` 첫 사용 entry
- `scripts/check-bypass-audit-comment.sh` — audit assertion lint
- `templates/github-workflows/adr-sunset-criteria.yml` — bypass label conditional skip workflow
- label-registry-v2 entry 추가 의무 — `hotfix-bypass:adr-sunset` label = label-registry-v2 의 신규 `bypass` tier entry (MINOR bump v2.0 → v2.1 — 별도 follow-up PR 또는 Phase 1 PR 동반, ArchitectAgent 판단)

## Amendment 4 — `hotfix-bypass:auto-phase-label` 7번째 family member + branch → phase mapping 표 SSOT (CFP-481, 2026-05-12)

### 컨텍스트

CFP-455 + CFP-449 retro 식별 sentinel 2 (Codex review verdict EVIDENCE_FRAMEWORK_ENTRY P2) — PR open 후 phase label 누락이 2회 재현되어 mechanical enforcement 도입 timing 도달. CFP-481 (carrier) 가 ADR-060 Amendment 4 (3rd warning-tier entry `auto-phase-label` 등록) 동반으로 본 Amendment 4 도입.

본 Amendment 4 의 두 결정:

1. **`hotfix-bypass:auto-phase-label` 7번째 family member 추가** — Amendment 3 §결정 6.A per-entry namespace 정합 (CFP-389 prior art `hotfix-bypass:adr-sunset` + CFP-426 prior art 4 `hotfix-bypass:worktree-*` 직접 mirror).
2. **branch → phase mapping 표 SSOT 신설** — ADR-024 Amendment 1 hierarchical convention (`cfp-NNN[/<lane>[/<sub>]]`) 의 phase:* label 매핑이 codeforge 안에서 SSOT 부재. CFP-481 의 `auto-phase-label.yml` workflow 가 1순위 inference 로직으로 본 mapping 직접 사용 — 본 Amendment 4 가 mapping SSOT 명세화.

### Amendment

#### §결정 6.A.1 (신설) — branch → phase mapping 표 SSOT

ADR-024 Amendment 1 hierarchical convention `cfp-NNN[/<lane>[/<sub>]]` 의 lane 별도 phase:* label 매핑:

| branch pattern | phase:* label | 비고 |
|---|---|---|
| `cfp-NNN/requirements` | `phase:요구사항` | 요구사항 lane sub-branch (codeforge-requirements) |
| `cfp-NNN/design` | `phase:설계` | 설계 lane sub-branch (codeforge-design) |
| `cfp-NNN/design-review` | `phase:설계-리뷰` | 설계리뷰 lane sub-branch (codeforge-review) |
| `cfp-NNN/develop` | `phase:구현` | 구현 lane sub-branch (codeforge-develop) |
| `cfp-NNN/code-review` | `phase:구현-리뷰` | 구현리뷰 lane sub-branch (codeforge-review) |
| `cfp-NNN/security-test` | `phase:보안-테스트` | 보안테스트 lane sub-branch (codeforge-review) |
| `cfp-NNN[-<slug>]` (lane 표기 없음) | (mapping 없음 — 2순위 fallback) | story root branch — Issue Form 부착 phase:* label inheritance 또는 PR body `Related: #N` linked Issue label 복사 |
| `cfp-NNN-docs-*` 또는 body marker `<!-- doc-only -->` | `phase:설계-리뷰` (terminal default) | doc-only fast-path Story (ADR-054 §결정 4) |
| `cfp-NNN-close` 또는 Epic Phase N+1 close 시그널 | `phase:reservation` (terminal default) | Epic close PR (ADR-020 Amendment 1 §결정 9) |

**SSOT 발효**: 본 §결정 6.A.1 = mapping 표의 wrapper-owned SSOT. CFP-481 의 `auto-phase-label.yml` workflow 가 1순위 inference 로직으로 본 표 verbatim 사용. 신규 lane / sub-branch 추가 시 본 표 row 동시 갱신 의무.

**Sub-task branch (`cfp-NNN/<lane>/<sub-name>`)**: lane prefix 만 매칭 — 예: `cfp-481/design/security-arch` → `phase:설계` (lane prefix `cfp-481/design` 매칭).

**Fix iter / retro branch**: `cfp-NNN/fix-iter-<N>` / `cfp-NNN/retro` → mapping 없음 (2순위 fallback 의존).

**Mechanical enforcement** (ADR-040 Amendment 3 §결정 7.B Pattern I): `auto-phase-label` (status: deferred-followup — CFP-481 Phase 2 PR scope `docs/evidence-checks-registry.yaml` row append + `templates/github-workflows/auto-phase-label.yml` self-app workflow 도입) — 본 §결정 6.A.1 mapping 표를 1순위 inference 로직 SSOT 로 verbatim 사용. registry yaml entry name = `auto-phase-label`. tier 도입 시점 = warning (ADR-060 §결정 5 — 모든 신규 entry 는 warning 시작 강제). bypass label = `hotfix-bypass:auto-phase-label` (§결정 6.A 7번째 family member 정합).

#### §결정 6.A (확장) — `hotfix-bypass:auto-phase-label` 7번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합):

1. `hotfix-bypass:adr-sunset` (CFP-389)
2. `hotfix-bypass:worktree-session-start-wire` (CFP-426)
3. `hotfix-bypass:worktree-pre-checkout` (CFP-426)
4. `hotfix-bypass:worktree-pre-commit-main-block` (CFP-426)
5. `hotfix-bypass:worktree-spawn-evidence-cwd` (CFP-426)
6. (decision-principle-vocab — CFP-449 Amendment 3, ADR-060 entry — bypass_label optional warning tier)
7. **`hotfix-bypass:auto-phase-label` (CFP-481, 본 Amendment 4)** — 신규

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 별도 lint 신설 0건).

**bypass scope**: `auto-phase-label.yml` workflow 의 phase label 부착 step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) 전부 유지 — 본 Amendment 4 는 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 7번째 family member) + branch → phase mapping 표 SSOT 신설 only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~3 entry) 에는 영향 X.
- `auto-phase-label.yml` workflow 가 1순위 inference 로직으로 본 mapping 표 verbatim 사용 — workflow 변경 시 mapping 표와 동기 의무 (ADR-029 self-app byte-identity invariant 정합).

### Related

- ADR-060 Amendment 4 (carrier — 3rd warning-tier entry `auto-phase-label` 등록)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.3 MINOR (phase:* 8 label entry attach_owner_plugin field 갱신 — `auto-phase-label.yml` 명시)
- `templates/github-workflows/auto-phase-label.yml` (Phase 2 PR scope) — 본 mapping 표 verbatim 사용
- `.github/workflows/auto-phase-label.yml` (Phase 2 PR scope) — self-app mirror byte-identical (ADR-029)
- `docs/evidence-checks-registry.yaml` (Phase 2 PR scope) — `auto-phase-label` row append (warning tier, bypass_label `hotfix-bypass:auto-phase-label`)
- `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art) — audit lint reuse

## Amendment 5 — `hotfix-bypass:debate-convergence-quality` 12번째 family member (CFP-582, 2026-05-13)

### 컨텍스트

CFP-582 Wave 4 (ADR-059 Amendment 2 carrier — debate-protocol-v1 v1.2 convergence_quality_invariant) 가 ADR-060 framework 의 첫 debate 영역 warning-tier evidence check entry `debate-convergence-quality-marker-presence` 신설. 본 entry 는 Story §9 debate transcript 안 3 marker (`[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]`) section header 존재 여부를 mechanical lint 로 검증 — `scripts/check_debate_convergence_quality.py` + `templates/github-workflows/debate-convergence-quality.yml`.

ADR-060 framework 정합 의무: 모든 warning-tier evidence check entry 는 ADR-024 Amendment 3 §결정 6.A per-entry namespace `hotfix-bypass:*` family member 와 1:1 mapping 의무 (audit-trailed exception channel SSOT). 12번째 family member 등록이 본 Amendment 5 의 의무.

### Amendment

#### §결정 6.A (확장) — `hotfix-bypass:debate-convergence-quality` 12번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4 확장 정합):

1. `hotfix-bypass:adr-sunset` (CFP-389)
2. `hotfix-bypass:worktree-session-start-wire` (CFP-426)
3. `hotfix-bypass:worktree-pre-checkout` (CFP-426)
4. `hotfix-bypass:worktree-pre-commit-main-block` (CFP-426)
5. `hotfix-bypass:worktree-spawn-evidence-cwd` (CFP-426)
6. `hotfix-bypass:decision-principle-vocab` (CFP-449 — ADR-060 entry, bypass_label optional warning tier)
7. `hotfix-bypass:auto-phase-label` (CFP-481, Amendment 4)
8. `hotfix-bypass:marketplace-atomic` (ADR-063 carrier)
9. `hotfix-bypass:claude-md-line-cap` (CFP-506)
10. `hotfix-bypass:sibling-pr-author-check` (CFP-521)
11. `hotfix-bypass:workflow-permissions` (CFP-530)
12. `hotfix-bypass:workflow-yaml-parse` (CFP-583)
13. **`hotfix-bypass:debate-convergence-quality` (CFP-582, 본 Amendment 5)** — 신규

(family member 카운트 = 12 — 위 prior list 의 entry 중 ADR-060 entry 와 wrapper-internal entry 혼합 sequence. 본 Amendment 5 시점 family 총원 = 12 active entry. label-registry-v2 v2.6 sub-entry append 동반.)

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 별도 lint 신설 0건).

**bypass scope**: `debate-convergence-quality.yml` workflow 의 3 marker presence lint step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**debate 영역 첫 family member**: 기존 11 family member 는 모두 syntactic / structural mechanical lint 대응. 본 Amendment 5 의 12번째 family member 는 debate transcript 의 convergence_quality_invariant (semantic anti-sycophancy 검증) 영역 첫 진입 — debate-protocol-v1 v1.2 schema 와 inter-plugin-contracts 의 cross-validation channel 활성.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) 전부 유지 — 본 Amendment 5 는 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 12번째 family member) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~4 entry) 에는 영향 X.
- ADR-059 Amendment 2 §결정 8 convergence_quality_invariant carrier 동반 — debate-protocol-v1 v1.2 schema 의 `convergence_quality_invariant` block 과 cross-validate 의무.

### Related

- ADR-059 Amendment 2 (carrier — convergence_quality_invariant 3 marker mechanical enforcement + first debate-domain warning-tier entry)
- ADR-060 (framework — 7th warning-tier entry `debate-convergence-quality-marker-presence` 등록)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.6 sub-entry (CFP-582 — 12번째 hotfix-bypass:* family member entry)
- `docs/inter-plugin-contracts/debate-protocol-v1.md` v1.2 (convergence_quality_invariant schema block)
- `docs/evidence-checks-registry.yaml` (CFP-582 Phase 2 — `debate-convergence-quality-marker-presence` row append, warning tier, bypass_label `hotfix-bypass:debate-convergence-quality`)
- `templates/github-workflows/debate-convergence-quality.yml` — 3 marker mechanical lint workflow
- `scripts/check_debate_convergence_quality.py` — 3 marker regex lint (CFP-582 Phase 2 산출물)
- `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art) — audit lint reuse

## Amendment 6 — `hotfix-bypass:*` per-entry namespace 누적 사용 카운터 lint + 31/32번째 family member (CFP-825, 2026-05-17)

### 컨텍스트

ADR-024 Amendment 3 §결정 6.A `hotfix-bypass:<entry>` per-entry namespace 가 audit-trailed exception channel 의도로 도입된 후 30 entry 누적 (label-registry-v2 v2.22 / CFP-785 `adr-077-design-reading` 30번째 family member 시점, post-CFP-825 carrier base; CFP-771 retro §8 발의 시점 = 17 entry era). CFP-771 (2026-05-16) retro §8 제안 1 이 evidence cluster 5+ 사용 발견 carrier:

- CFP-770/771 PR #788 admin merge — `hotfix-bypass:claude-md-line-cap` + `hotfix-bypass:wording-dictionary` 2 label 동시 부착
- CFP-819 PR #823 — `hotfix-bypass:wording-dictionary` cosmetic 7 occurrences
- CFP-786/801/795 carrier — `hotfix-bypass:unit-tests` pre-existing pytest 부재 사유 누적

정당 예외 채널이 누적되며 정상 경로화하는 거버넌스 erosion (bypass-as-norm mutation) — 사용 빈도 monitoring 부재 시 잠재. ADR-024 Amendment 3 §결정 6.C audit trail 3중 안전망 (PR comment 자동 발의 + audit assertion lint + audit log 집계) 가 개별 PR scope cover 하나, **per-(plugin, label) signature 단위의 시계열 누적 패턴 감지 channel 부재** — 본 Amendment 6 이 그 gap 해소.

### Amendment

#### §결정 6.A.2 (신설) — per-entry namespace 누적 사용 카운터 lint ratchet 룰

`hotfix-bypass:*` family member 의 per-(plugin, label) signature 단위 누적 사용 횟수가 threshold reach 시 carrier Issue 자동 발의 의무. ratchet 3-tuple:

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **threshold** | per-(plugin, label) signature 누적 ≥3 reach-merged PR | CFP-770/771/819 corpus 5+ 사용 evidence cluster (verified-via: gh pr view #788 #823 --json labels, Phase 2 PR open 시 재 verify-before-trust 의무). dimension category = `count` (PR 누적 횟수). units = `merged PR count per (plugin, label) signature`. |
| **dedup unit** | PR number (merged PR 고유 idempotent) | docs/domain-knowledge/domain/github-actions/workflow-idempotency-patterns.md §schedule trigger 정합 (cron 반복 → concurrency group 부족 → file-marker 부적합 → signature dedup 의무, L174 verbatim) |
| **measurement window** | all-time | rolling window (30d/90d) 도입 시 dedup signature 가 stale signature pollution 영구 carry-forward 차단 못함 — 전체 history 누적 행위 패턴 감지 의무. |
| **exempt channels (2종)** | (1) `hotfix-bypass:bypass-label-counter` (self-meta loop 회피) / (2) `hotfix-bypass:exempt:<entry>` template (rare 정당 declare, narrative audit trail mechanical enforce = 후속 carrier 영역) | self-meta loop 차단 절대 invariant + rare 정당 declare 채널 보존 |

**자동 발의 carrier Issue 본문 의무 (Phase 2 PR scope)**: signature `<plugin>::<label>` + PR 누적 list + ADR-024 Amendment 6 cross-ref + 후속 평가 영역 (threshold 재calibration vs blocking-on-merge 격상 vs 정당 사용 영역 declare).

**self-meta loop 회피 invariant**: 본 lint workflow 자체의 PR (예: `bypass-label-counter.yml` 수정 PR) 에 `hotfix-bypass:bypass-label-counter` 부착 시 해당 PR signature 누적 count 제외. lint 가 자기 자신을 trigger 하는 재귀 차단.

**multi-signature 동시 reach 처리**: 단일 cron 실행에서 다중 (plugin, label) signature 가 동시에 threshold reach 시 각 signature 별 독립 carrier Issue 발의 (signature aggregation 금지 — 후속 evaluation 의 dedup 영역 별도).

#### §결정 6.A (확장) — `hotfix-bypass:bypass-label-counter` 31번째 + `hotfix-bypass:exempt:<entry>` 32번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4/5 확장 정합 + CFP-426~CFP-722 추가 entry 누적):

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:bypass-label-counter` | **31번째** | 본 lint workflow self-meta loop 회피 — 본 entry 부착 PR 은 누적 count 제외 |
| `hotfix-bypass:exempt:<entry>` | **32번째** (template) | rare 정당 declare 채널 — `<entry>` 부분 가 specific entry name (예: `hotfix-bypass:exempt:wording-dictionary`). narrative audit trail mechanical enforce 는 후속 carrier 영역 (본 Amendment 6 = label 등록만) |

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 별도 lint 신설 0건).

**bypass scope**: `bypass-label-counter.yml` workflow 의 per-signature tally + Issue auto-create step 만 skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**bypass-as-norm mutation 영역 첫 family member**: 기존 30 family member 는 개별 evidence check 의 1회 hotfix bypass 영역. 본 Amendment 6 의 31번째/32번째 family member 는 family 자체의 누적 사용 패턴 monitoring 영역 — 첫 진입.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) + Amendment 5 (CFP-582) 전부 유지 — 본 Amendment 6 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 31/32번째 family member + §결정 6.A.2 ratchet 룰 신설) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~5 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 6 = forbid scope 확장 (per-entry → 누적 카운터 monitoring 추가) = ratchet-up 강화 방향, sunset_justification_required: false.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-merge 격상 = empirical evidence 누적 후 별 CFP carrier 영역 (ADR-060 승격 gate AND condition 통과 의무).

### scope_boundary (CFP scope unitary, ADR-064 §결정 1 정합)

본 Amendment 6 **포함** 영역:

- per-(plugin, label) signature 단위 카운터 lint (warning tier only)
- bypass-as-norm mutation 누적 monitoring (Issue auto-create + dedup)
- 2 신규 family member (self-meta exempt + rare 정당 declare template)

본 Amendment 6 **out-of-scope** (후속 carrier 영역):

- **per-plugin scope 누적 카운터** (단일 plugin 5 entry 각 1회 = 5회 분산이지만 근본은 동일 plugin 의 체계적 회피) — 별 CFP carrier
- **blocking-on-merge tier escalation** — 별 CFP, ADR-060 승격 gate AND condition 통과 후
- **bypass narrative audit trail mechanical enforce** (`[bypass-justification]` PR 코멘트 marker) — 별 CFP
- **cross-repo bypass counter extension** (codeforge-internal-docs / marketplace) — 별 CFP, EC-1 정합
- **carrier Issue 코멘트 append** (이미 발의된 Issue 에 추가 PR 정보 append) — 별 CFP

### Related

- ADR-024 Amendment 3 §결정 6.A (prior art — per-entry namespace audit-trail SSOT)
- ADR-024 Amendment 3 §결정 6.C (prior art — audit trail 3중 안전망: PR comment + audit assertion lint + audit log 집계)
- ADR-060 (framework — 63번째 evidence-checks-registry entry `bypass-label-counter` warning tier 등록)
- ADR-058 §결정 5 (ratchet-up 강화 방향 정합 — sunset_justification_required: false)
- ADR-061 (Python script convention — 본 신설 script = `.py` file + thin bash wrapper)
- ADR-040 Amendment 3 §결정 7.D (mechanical_enforcement_actions[] self-application — `bypass-label-counter` entry 추가)
- ADR-068 Amendment 1 I-5 (dimensional empirical grounding — threshold ≥3 의 `count` dimension + empirical-source annotation 의무)
- ADR-005 (workflow self-app byte-identical mirror)
- ADR-010 §결정 2 (label-registry-v2 v2.22 → v2.23 MINOR bump = wrapper-local, sibling sync 면제)
- ADR-063 (marketplace ↔ plugin.json atomic invariant — 본 carrier 적용 제외, plugin.json MINOR bump 미동반)
- ADR-066 (CODEFORGE_CROSS_REPO_PAT rotation policy — 본 workflow `permissions: issues: write` 단일 PAT consolidation)
- ADR-008 (contract versioning — v2.22 → v2.23 MINOR bump 룰)
- ADR-027 Amendment 2 §결정 6.C (manual fallback path 정합 — workflow trigger 시 PAT 환경 검증 의무)
- CFP-627 (precedent — marketplace-drift-detection 24h cron + workflow_dispatch + Issue auto-create + per-(plugin, field) signature dedup 동일 구조 reuse)
- CFP-771 retro §8 제안 1 (carrier — bypass-label-namespace 카운터 lint 제안)
- CFP-389 prior art (`scripts/check-bypass-audit-comment.sh` audit lint reuse)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.22 → v2.23 MINOR (CFP-825 — 31번째 `hotfix-bypass:bypass-label-counter` + 32번째 `hotfix-bypass:exempt:<entry>` template)
- `docs/evidence-checks-registry.yaml` (CFP-825 Phase 2 — `bypass-label-counter` 63번째 entry append, warning tier, bypass_label `hotfix-bypass:bypass-label-counter`)
- `templates/github-workflows/bypass-label-counter.yml` (CFP-825 Phase 2 — 24h cron + workflow_dispatch + Issue auto-create)
- `scripts/check-bypass-label-counter.py` (CFP-825 Phase 2 — gh api query + signature tally + threshold check + Issue auto-create)
- `scripts/check-bypass-label-counter.sh` (CFP-825 Phase 2 — thin bash wrapper, ADR-061 정합)
- `tests/scripts/test-check-bypass-label-counter.bats` (CFP-825 Phase 2 — TC 5+ baseline)

## Amendment 7 — `hotfix-bypass:corpus-claim-verify` 34번째 + `hotfix-bypass:cross-plugin-ownership-verify` 35번째 family member (CFP-841, 2026-05-17)

### 컨텍스트

CFP-841 (ADR-082 Amendment 1 carrier — §결정 6 behavioral→mechanical 전환) 가 ADR-060 framework 의 2 신규 warning-tier evidence check entry 를 신설한다:

- `corpus-claim-verify` (ADR-082 §결정 2(a)) — Story/Change-Plan/ADR 본문 corpus/fixture enumeration ("예시 N건 / 전무 / 부재 / 다수" + file-path 인용 co-occurrence) 의 `[verified: git show <ref>:<path>]` annotation 부재 검출 (ADR-068 I-5 directly-analogous pattern 재사용). `scripts/check-corpus-claim-verify.{py,sh}` + `templates/github-workflows/corpus-claim-verify.yml` (CFP-841 Phase 2 carrier).
- `cross-plugin-ownership-verify` (ADR-082 §결정 2(d)) — ChangeImpactAgent Phase 0 mapping `templates/*` wrapper-local 단정 전 `lane-self-write-ownership-matrix.yaml` cross_plugin_doc_ownership sub-tree query 1-step annotation 부재 검출 + §13.B 4-way drift-sync invariant. `scripts/check-cross-plugin-ownership-verify.{py,sh}` + workflow (CFP-841 Phase 2 carrier).

ADR-060 framework 정합 의무: 모든 warning-tier evidence check entry 는 ADR-024 Amendment 3 §결정 6.A per-entry namespace `hotfix-bypass:*` family member 와 1:1 mapping 의무 (audit-trailed exception channel SSOT). 34번째 + 35번째 family member 등록이 본 Amendment 7 의 의무 (verified-via: `git show origin/main:docs/inter-plugin-contracts/label-registry-v2.md` — v2.24 CFP-820 `hotfix-bypass:version-3way-atomic` 33번째 family member 가 현 최신, 본 Amendment 7 = 34/35번째).

### Amendment

#### §결정 6.A (확장) — `hotfix-bypass:corpus-claim-verify` 34번째 + `hotfix-bypass:cross-plugin-ownership-verify` 35번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4/5/6 확장 정합 + CFP-426~CFP-820 추가 entry 누적, 33 active member):

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:corpus-claim-verify` | **34번째** | ADR-082 §결정 2(a) corpus annotation lint conditional skip — Story/Change-Plan/ADR corpus enumeration `[verified]` annotation lint (warning tier, CFP-841 Phase 2 carrier) |
| `hotfix-bypass:cross-plugin-ownership-verify` | **35번째** | ADR-082 §결정 2(d) cross-plugin ownership queryable lint conditional skip — `lane-self-write-ownership-matrix.yaml` cross_plugin_doc_ownership sub-tree query + §13.B 4-way drift-sync invariant lint (warning tier, CFP-841 Phase 2 carrier) |

(family member 카운트 = 33 active member (v2.24 CFP-820 33번째 `version-3way-atomic` 시점) + 본 Amendment 7 = 34/35번째 → 35 total. label-registry-v2 v2.24 → v2.25 MINOR bump 동반 — 2 신규 family member 동시 추가.)

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 독립 lint 신설 0건).

**bypass scope**: `corpus-claim-verify.yml` / `cross-plugin-ownership-verify.yml` workflow 의 annotation presence lint step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**write-time semantic truth verify 영역 첫 family member**: 기존 33 family member 는 syntactic / structural / debate / governance mechanical lint 대응. 본 Amendment 7 의 34/35번째 family member 는 ADR-082 write-time self-write semantic truth verify (corpus 단정 / cross-plugin ownership) 영역 첫 진입 — ADR-082 §결정 1 layer disjoint 표의 internal lane agent self-write layer 의 mechanical enforcement 활성.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) + Amendment 5 (CFP-582) + Amendment 6 (CFP-825) 전부 유지 — 본 Amendment 7 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 34/35번째 family member) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~6 entry) 에는 영향 X.
- ADR-082 Amendment 1 carrier 동반 — ADR-082 §결정 2(a)/2(d) mechanical_enforcement_actions[] deferred-followup 2 entry 와 1:1 mapping.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 7 = forbid scope 확장 (per-entry namespace 2 추가) = ratchet-up 강화 방향, `sunset_justification_required: false`.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-pr 격상 = empirical evidence 누적 후 별 CFP carrier 영역.

### Related

- ADR-082 Amendment 1 (carrier — §결정 6 behavioral→mechanical 전환, scope 2(a) corpus-claim-verify + scope 2(d) cross-plugin-ownership-verify)
- ADR-068 I-5 (scope 2(a) lint = I-5 `[empirical-source]` annotation directly-analogous pattern 재사용, cross-ref only)
- ADR-060 (framework — 2 신규 warning-tier evidence-checks-registry entry `corpus-claim-verify` + `cross-plugin-ownership-verify` 등록)
- ADR-024 Amendment 3 §결정 6.A (prior art — per-entry namespace audit-trail SSOT) + §결정 6.C (audit trail 3중 안전망)
- ADR-058 §결정 5 (ratchet-up 강화 방향 정합 — sunset_justification_required: false)
- ADR-010 §결정 2 (label-registry-v2 v2.24 → v2.25 MINOR = wrapper-canonical kind:registry, sibling sync 면제)
- ADR-008 (contract versioning — v2.24 → v2.25 MINOR bump 룰, 신규 label entry append = minor)
- ADR-063 (marketplace ↔ plugin.json atomic invariant — 본 carrier plugin.json MINOR bump 미동반 → atomic invariant 비발효)
- CFP-841 retro/Change Plan §3 (Phase 2 carrier — lint script + workflow + bats + yaml cross-plugin sub-tree 확장 + §13.B 4-way sync)
- CFP-389 prior art (`scripts/check-bypass-audit-comment.sh` audit lint reuse)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` Amendment 1 (carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.24 → v2.25 MINOR (CFP-841 — 34번째 `hotfix-bypass:corpus-claim-verify` + 35번째 `hotfix-bypass:cross-plugin-ownership-verify`)
- `docs/evidence-checks-registry.yaml` (CFP-841 — `corpus-claim-verify` + `cross-plugin-ownership-verify` 2 entry append, warning tier, deferred-followup status, Phase 2 actual wire)
- `templates/github-workflows/corpus-claim-verify.yml` / `cross-plugin-ownership-verify.yml` (CFP-841 Phase 2 — annotation presence lint workflow)
- `scripts/check-corpus-claim-verify.{py,sh}` / `scripts/check-cross-plugin-ownership-verify.{py,sh}` (CFP-841 Phase 2 — ADR-061 정합 외부 .py + thin bash wrapper)
- `tests/scripts/test-check-corpus-claim-verify.bats` / `test-check-cross-plugin-ownership-verify.bats` (CFP-841 Phase 2 — TC 5+ baseline 각)

## Amendment 8 — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 + 37/38/39번째 family member (CFP-845, 2026-05-17)

### 컨텍스트

CFP-825 Amendment 6 §결정 6.A.2 가 `bypass-label-counter` warning-tier lint 로 per-(plugin, label) signature 누적 모니터링 channel 을 도입했으나 **§scope_boundary 가 명시한 4 out-of-scope 후속 carrier 영역** (per-plugin scope 누적 / blocking-on-merge tier 격상 / `[bypass-justification]` narrative audit / cross-repo extension) 의 후속 carrier 영역 미해소. CFP-845 (carrier) brainstorm Phase 0 4-agent 수렴 결과 = "옵션 B 2-Story 분할 권장" — 본 Amendment 8 (Story-1) = 4 영역 중 3 즉시 통합 (per-plugin / `[bypass-justification]` marker / cross-repo), 4번째 (blocking-on-merge tier 격상) = Story-2 (#861 RESERVED) evidence-gated 분리. ADR-064 §결정 1 (CFP scope unitary) 정합 — Story-2 분리 사유 = ADR-060 promotion gate AND-condition (PR≥20 + bypass외 failure=0 + sibling merged) 가 외부 시간 의존 gate, "경량→full" 단계 한 CFP 묶임 차단.

본 Amendment 8 적용 영역 = 3 신규 sub-decision (§결정 6.A.3 / §결정 6.A.4 / §결정 6.A.5) + §결정 6.A 확장 (3 신규 family member: 37/38/39번째). bypass-as-norm mutation governance erosion 영역의 **multi-axis monitoring 확장** (entry-axis → plugin-axis → cross-repo-axis + narrative audit axis).

### Amendment

#### §결정 6.A.3 (신설) — per-plugin 전체 누적 카운터 ratchet 룰

`hotfix-bypass:*` family member 의 per-(plugin) signature 단위 (label entry 무관 cross-entry 집계) 누적 사용 횟수가 threshold reach 시 carrier Issue 자동 발의 의무. §결정 6.A.2 (per-entry namespace) 의 **상위 layer 집계 channel** — 단일 plugin 이 5 entry 각 1회 = 5회 분산 사용 시 §결정 6.A.2 미발의 (각 entry 1회 < threshold 3) but **근본은 동일 plugin 의 체계적 회피** (per-plugin scope norm mutation). 본 §결정 6.A.3 이 그 gap 해소.

ratchet 3-tuple:

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **threshold** | per-(plugin) signature 누적 ≥5 reach-merged PR | per-entry threshold 3 (§결정 6.A.2) 보다 보수적 (5) — entry 다양성 cover 의 noise floor. dimension category = `count` (PR 누적 횟수). units = `merged PR count per plugin signature (cross-entry aggregate)`. empirical-source = CFP-825 evidence cluster (single plugin 5+ entry 사용 corpus) + CFP-845 Research §unknown unknown 1 (per-plugin threshold calibration evidence 부족 → 보수적 시작, Phase 2 actual wire 후 별 calibration carrier) |
| **dedup unit** | PR number (merged PR 고유 idempotent) | §결정 6.A.2 와 동일 — docs/domain-knowledge/domain/github-actions/workflow-idempotency-patterns.md §schedule trigger 정합 |
| **measurement window** | all-time | §결정 6.A.2 와 동일 — rolling window 의 stale signature pollution 차단 |
| **exempt channels (3종)** | (1) `hotfix-bypass:per-plugin-cumulative-counter` (self-meta loop 회피) / (2) `hotfix-bypass:exempt:<entry>` template (rare 정당 declare, CFP-825 prior art) / (3) `hotfix-bypass:exempt:per-plugin` template (per-plugin scope 정당 declare, 본 §결정 6.A.3 신규) | self-meta loop 차단 + per-entry/per-plugin scope 양 declare 채널 보존 |

**자동 발의 carrier Issue 본문 의무 (Phase 2 PR scope)**: signature `<plugin>` + entry breakdown (entry 별 PR list) + PR 누적 list + ADR-024 Amendment 8 cross-ref + 후속 평가 영역 (threshold 재calibration vs blocking-on-merge 격상 vs 정당 사용 영역 declare).

**self-meta loop 회피 invariant**: 본 lint workflow 자체의 PR (예: `per-plugin-cumulative-counter.yml` 수정 PR) 에 `hotfix-bypass:per-plugin-cumulative-counter` 부착 시 해당 PR signature 누적 count 제외.

**§결정 6.A.2 와 disjoint invariant**: 동일 PR 가 §결정 6.A.2 (per-entry) + §결정 6.A.3 (per-plugin) 양 trigger 시 양 carrier Issue 각 발의 (signature aggregation 금지, 각 carrier 가 별 evaluation 영역).

#### §결정 6.A.4 (신설) — `[bypass-justification]` PR comment marker mechanical enforce

`hotfix-bypass:*` label 부착 PR 의 `[bypass-justification]` prefix PR comment 존재 의무 — narrative audit trail mechanical enforce. `scripts/check-bypass-justification-marker.sh` lint = grep-presence only (semantic adequacy 검증 불가):

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **lint scope** | hotfix-bypass:* label 부착 PR 의 PR comment (review comment 제외 — top-level only) | comment-prefix-registry-v1 v1.3 신규 `[bypass-justification]` prefix (CFP-845 carrier) — 14번째 phase prefix. dimension category = `count` (PR per-presence boolean) |
| **grep pattern** | `^\[bypass-justification\]` (line start anchor, case-sensitive) | comment-prefix-registry-v1 §3 entry 표준 형식 정합 (Bracket prefix + 빈칸 + 본문) |
| **semantic adequacy** | grep-only — **semantic 진위 검증 불가** | false-positive risk 명시 (CFP-845 Research §unknown unknown 2) — reviewer responsibility, lint 가 narrative 정당성 평가 X |
| **false-positive policy** | grep PASS but body 부적합 (예: 빈 marker, 단순 "ok") = lint PASS but reviewer reject 영역 | Phase 2 workflow PR comment 안 reminder 자동 발의 (사용자 가이드 + warning marker) — 별 carrier |

**bypass scope**: `bypass-justification-marker.yml` workflow 의 grep-presence lint step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**self-meta loop 회피 invariant**: 본 lint workflow 자체의 PR 에 `hotfix-bypass:bypass-justification-marker` 부착 시 marker presence check skip.

**marker 의무 scope**: hotfix-bypass:* label 부착 PR only — label 부착 없는 PR 은 marker 의무 X.

**audit trail 영구화**: PR comment 는 GitHub-side state (영구 보존, PR close 후도 유지) — file marker 와 disjoint, dedup 불요 (PR 별 1회 발화).

#### §결정 6.A.5 (신설) — cross-repo bypass counter extension

현 wrapper (`mclayer/plugin-codeforge`) 단일 cover → **3-repo 동시 cover** 확장: `mclayer/plugin-codeforge` + `mclayer/codeforge-internal-docs` + `mclayer/marketplace`. signature = (repo, plugin, label) 3-tuple, threshold 별 calibration:

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **scope repos (3종)** | wrapper plugin-codeforge / internal-docs / marketplace | ADR-013 §결정 family scope 7 plugin (wrapper + 6 lane plugin, 단 lane plugin 의 hotfix-bypass 사용은 wrapper-only governance — sibling sync 면제 정합, ADR-010 §결정 2). 본 §결정 6.A.5 cover = 3 cross-repo 중 hotfix-bypass label 사용 영역 (wrapper governance / internal-docs dogfood artifact / marketplace publication) |
| **threshold** | per-(repo, plugin, label) signature 누적 ≥3 reach-merged PR | §결정 6.A.2 와 동일 (3) — repo namespace 분리 시 per-repo 독립 trigger. dimension category = `count`. units = `merged PR count per (repo, plugin, label) signature` |
| **aggregate trigger** | 3 repo 동일 (plugin, label) signature 동시 reach 시 단일 aggregate carrier Issue 발의 (multi-repo signature) | per-repo 단독 trigger + aggregate trigger 양 channel disjoint — aggregate = 3-repo systemic mutation 신호, per-repo = 단일 repo local mutation 신호 |
| **dedup unit** | (repo, PR number) 2-tuple (cross-repo PR number 충돌 회피) | 3 repo 동일 PR number 가능 — repo namespace 의무 |
| **PAT scope** | 단일 PAT (CODEFORGE_CROSS_REPO_PAT, ADR-066) reuse — 3 repo `issues:read` + `repo:read` 권한 | 신규 secret 0건, ADR-066 rotation policy 적용 (90 day rotation / 180 day max lifetime) |
| **exempt channels** | `hotfix-bypass:cross-repo-bypass-counter` (self-meta loop 회피) + §결정 6.A.2/6.A.3 의 exempt 채널 carry-over | 3 axis lint self-meta loop 차단 |

**자동 발의 carrier Issue 본문 의무 (Phase 2 PR scope)**: signature `(repo)::<plugin>::<label>` 또는 aggregate `<plugin>::<label>` (3-repo) + repo breakdown (repo 별 PR list) + ADR-024 Amendment 8 cross-ref + 후속 평가 영역 + ADR-066 PAT audit trail.

**carrier Issue repository**: aggregate carrier = `mclayer/plugin-codeforge` (wrapper governance owner SSOT, ADR-013 정합). per-repo carrier = 해당 repo (각 repo 의 local governance).

**ADR-066 PAT 의존 invariant**: 본 §결정 6.A.5 작동 의무 = CODEFORGE_CROSS_REPO_PAT secret 활성 + 3 repo `issues:read` + `repo:read` 권한 보유 — PAT 만료 시 workflow 실패 (warning tier 정합, blocking 미발효).

#### §결정 6.A (확장) — 3 신규 family member (37/38/39번째)

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4/5/6/7 확장 정합 + CFP-426~CFP-841 추가 entry 누적, 36 active member — v2.26 CFP-821 `branch-protection-sync` 36번째):

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:per-plugin-cumulative-counter` | **37번째** | §결정 6.A.3 per-plugin scope 누적 카운터 self-meta loop 회피 — 본 entry 부착 PR 은 per-plugin 누적 count 제외 |
| `hotfix-bypass:bypass-justification-marker` | **38번째** | §결정 6.A.4 PR comment marker presence lint conditional skip — narrative audit 영역 첫 family member |
| `hotfix-bypass:cross-repo-bypass-counter` | **39번째** | §결정 6.A.5 cross-repo 3-tuple signature 누적 카운터 self-meta loop 회피 — cross-repo 영역 첫 family member |

(family member 카운트 = 36 active member (v2.26 CFP-821 36번째 `branch-protection-sync` 시점) + 본 Amendment 8 = 37/38/39번째 → 39 total. label-registry-v2 v2.26 → v2.27 MINOR bump 동반 — 3 신규 family member 동시 추가.)

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 신규 audit lint 0건).

**bypass scope**: `per-plugin-cumulative-counter.yml` / `bypass-justification-marker.yml` / `cross-repo-bypass-counter.yml` workflow 의 각 lint step 만 skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**bypass-as-norm mutation 다차 axis monitoring 영역 진입**: 기존 36 family member 는 단일 axis (per-entry signature) cover. 본 Amendment 8 의 37/38/39번째 family member 는 **3 신규 axis** (per-plugin scope / narrative audit / cross-repo extension) 동시 진입 — bypass-as-norm mutation governance erosion 의 multi-axis monitoring 완비.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) + Amendment 5 (CFP-582) + Amendment 6 (CFP-825) + Amendment 7 (CFP-841) 전부 유지 — 본 Amendment 8 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 37/38/39번째 family member + §결정 6.A.3/6.A.4/6.A.5 ratchet 룰 신설) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~7 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 8 = forbid scope 확장 (per-entry → per-plugin scope 추가 + narrative audit 추가 + cross-repo 추가) = ratchet-up 강화 방향, sunset_justification_required: false.
- ADR-024 Amendment 6 §scope_boundary 4 out-of-scope 영역 중 3 영역 흡수 (per-plugin / `[bypass-justification]` marker / cross-repo) — 4번째 (blocking-on-merge tier 격상) = Story-2 #861 RESERVED 별 carrier evidence-gated 분리, ADR-064 §결정 1 CFP scope unitary 정합.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-merge 격상 = empirical evidence 누적 후 별 CFP carrier 영역 (ADR-060 승격 gate AND condition 통과 의무, Story-2 #861).
- comment-prefix-registry-v1 v1.2 → v1.3 MINOR bump 동반 (§결정 6.A.4 `[bypass-justification]` 14번째 prefix 신설) — ADR-008 MINOR (entry 추가 = append-only for v1.x rule 정합), kind:registry sibling sync 면제 (ADR-010 §결정 2).
- ADR-066 단일 PAT (CODEFORGE_CROSS_REPO_PAT) reuse — 신규 secret 0건, rotation policy 영향 0.

### scope_boundary (CFP scope unitary, ADR-064 §결정 1 정합)

본 Amendment 8 **포함** 영역 (Story-1 = 본 #845 ACTIVE):

- §결정 6.A.3 per-plugin scope 누적 카운터 ratchet (warning tier only)
- §결정 6.A.4 `[bypass-justification]` PR comment marker presence lint (grep-only, false-positive risk 명시)
- §결정 6.A.5 cross-repo bypass counter extension (wrapper + internal-docs + marketplace 3-repo)
- 3 신규 family member (37/38/39번째)
- comment-prefix-registry-v1 v1.3 MINOR bump (`[bypass-justification]` 14번째 prefix)

본 Amendment 8 **out-of-scope** (Story-2 #861 RESERVED 별 carrier 영역):

- **blocking-on-merge tier escalation** — ADR-060 승격 gate AND condition (PR 누적 ≥20 + bypass 외 failure=0 + sibling Story merged) 통과 후 별 carrier (#861 evidence-gated). 본 Amendment 8 = 3 신규 entry warning tier first iteration only.

본 Amendment 8 **후속 carrier 영역** (Phase 2 actual wire 후 별 carrier):

- per-plugin threshold 재calibration (현 5 = 보수적 시작, Phase 2 evidence 누적 후 재평가)
- cross-repo aggregate threshold 재calibration (현 3 = per-entry 동일, multi-repo systemic 신호 noise floor 평가)
- `[bypass-justification]` marker semantic adequacy 자동 평가 (현 grep-only, NLP 평가는 별 carrier — Research §unknown unknown 2 deferred)
- per-plugin 외 추가 axis (예: per-author cumulative — Phase 2 actual wire 후 evidence 누적 시 별 carrier)

### Related

- ADR-024 Amendment 3 §결정 6.A (prior art — per-entry namespace audit-trail SSOT)
- ADR-024 Amendment 3 §결정 6.C (prior art — audit trail 3중 안전망: PR comment + audit assertion lint + audit log 집계)
- ADR-024 Amendment 6 §결정 6.A.2 (prior art — per-entry namespace 누적 사용 카운터 ratchet 룰)
- ADR-024 Amendment 6 §scope_boundary (본 Amendment 8 의 4 out-of-scope 영역 중 3 영역 흡수, 4번째 = Story-2 #861 RESERVED)
- ADR-060 (framework — 3 신규 warning-tier evidence-checks-registry entry `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` 등록, Phase 1 entry append + Phase 2 actual wire)
- ADR-058 §결정 5 (ratchet-up 강화 방향 정합 — sunset_justification_required: false)
- ADR-061 (Python script convention — 본 신설 3 lint script = `.py` file + thin bash wrapper 각)
- ADR-040 Amendment 3 §결정 7.D (mechanical_enforcement_actions[] self-application — `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` 3 entry 추가)
- ADR-068 Amendment 1 I-5 (dimensional empirical grounding — threshold ≥5 `count` dimension + threshold ≥3 `count` dimension 각 empirical-source annotation 의무)
- ADR-005 (workflow self-app byte-identical mirror — 3 신규 workflow yml templates/ ↔ .github/workflows/ 동기)
- ADR-010 §결정 2 (label-registry-v2 v2.26 → v2.27 MINOR + comment-prefix-registry-v1 v1.2 → v1.3 MINOR = wrapper-canonical kind:registry, sibling sync 면제)
- ADR-008 (contract versioning — 2 kind:registry MINOR bump 룰, 신규 entry append = minor)
- ADR-063 (marketplace ↔ plugin.json atomic invariant — 본 carrier plugin.json MINOR bump 미동반 → atomic invariant 비발효)
- ADR-066 (CODEFORGE_CROSS_REPO_PAT rotation policy — 본 §결정 6.A.5 cross-repo workflow `permissions: issues: write` + `repo: read` 단일 PAT reuse, rotation 90 day 정합)
- ADR-027 Amendment 2 §결정 6.C (manual fallback path 정합 — workflow trigger 시 PAT 환경 검증 의무)
- ADR-013 (family scope SSOT — 3 cross-repo = wrapper + internal-docs + marketplace)
- ADR-064 §결정 1 (CFP scope unitary — Story-1 (본 #845) 3 즉시 통합 + Story-2 (#861 RESERVED) 1 deferred 분리 정합)
- CFP-825 retro §6 후보 3 (carrier — bypass-as-norm mutation 후속 escalation 4 영역 발의)
- CFP-825 Amendment 6 §scope_boundary (out-of-scope 4 영역 verbatim 인용 → 본 Amendment 8 = 3 영역 흡수)
- CFP-845 Issue body + scope-split comment (2026-05-17 KST) — 옵션 B 2-Story 분할 권장 (Researcher / PMO / Analyst 3-agent 합치)
- CFP-861 RESERVED (Story-2 — blocking-on-merge tier 격상 carrier, evidence-gated)
- CFP-771 retro §8 제안 1 (prior art lineage — bypass-label-namespace 카운터 lint 제안, CFP-825 Amendment 6 첫 carrier)
- CFP-627 (precedent — marketplace-drift-detection 24h cron + workflow_dispatch + Issue auto-create + per-(plugin, field) signature dedup 동일 구조 cross-repo reuse)
- CFP-389 prior art (`scripts/check-bypass-audit-comment.sh` audit lint reuse)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.26 → v2.27 MINOR (CFP-845 — 37번째 `hotfix-bypass:per-plugin-cumulative-counter` + 38번째 `hotfix-bypass:bypass-justification-marker` + 39번째 `hotfix-bypass:cross-repo-bypass-counter`)
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` v1.2 → v1.3 MINOR (CFP-845 — 14번째 `[bypass-justification]` prefix 신설)
- `docs/evidence-checks-registry.yaml` (CFP-845 Phase 1 — `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` 3 entry append, warning tier, deferred-followup status, Phase 2 actual wire)
- `templates/github-workflows/per-plugin-cumulative-counter.yml` / `bypass-justification-marker.yml` / `cross-repo-bypass-counter.yml` (CFP-845 Phase 2 — 24h cron + PR-time lint 각)
- `scripts/check-per-plugin-cumulative-counter.{py,sh}` / `check-bypass-justification-marker.{py,sh}` / `check-cross-repo-bypass-counter.{py,sh}` (CFP-845 Phase 2 — ADR-061 정합 외부 .py + thin bash wrapper 각)
- `tests/scripts/test-check-per-plugin-cumulative-counter.bats` / `test-check-bypass-justification-marker.bats` / `test-check-cross-repo-bypass-counter.bats` (CFP-845 Phase 2 — TC 5+ baseline 각)
