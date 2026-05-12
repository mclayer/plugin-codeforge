---
adr_number: 24
title: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred
status: Accepted
category: governance
date: 2026-05-03
is_transitional: false
amended_by: CFP-389
amended_date: 2026-05-11
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
related_files:
  - CLAUDE.md
  - docs/consumer-guide.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-040-worktree-convention.md
  - docs/adr/ADR-060-evidence-enforceable-promotion-framework.md
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - templates/branch-protection-manifest.yaml
  - templates/github-workflows/branch-protection-drift-check.yml
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A 의무 — 본 ADR-024 Amendment 4 (CFP-481, 2026-05-12)
  # 가 ADR-040 Amendment 3 발효 (CFP-426 Phase 1 PR merge) 이후 작성된 normative
  # ADR amendment 이므로 §결정 7.C retroactive 면제 외 — 본 Amendment 4 부터 mandate 적용.
  # 기존 ADR-024 Amendment 1·2·3 = retroactive 면제 (§결정 7.C 정합).
  - action: auto-phase-label
    status: deferred-followup     # registry yaml row append = CFP-481 Phase 2 PR scope
    target_section: §결정 6.A.1   # branch → phase mapping 표 SSOT (1순위 inference 로직)
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

ADR-024 Amendment 1 hierarchical convention `cfp-NNN[/<lane>[/<sub>]]` 의 lane 별 phase:* label 매핑:

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
