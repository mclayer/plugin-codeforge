---
adr_number: 132
title: "consumer branch-protection 자동 wire 메커니즘 — operator-token GET-merge-PUT + 형상 파라미터 + context↔job 정합 게이트 + dead-gate 출고 차단 (Epic CFP-2468 Track W/W1)"
status: Proposed
category: governance/security
date: 2026-06-30
carrier_story: CFP-2469
parent_epic: CFP-2468
supersedes: null
amends: null
related_adrs:
  - ADR-024  # branch policy SSOT (§결정 A core-contexts-삭제-불허 + Amendment 2 §결정 C step 2 수동→자동 — 본 ADR 이 carrier, ADR-024 Amendment 20 동반)
  - ADR-027  # consumer adoption protocol (§결정 2 warning-inject-only graceful — 403→WARN 근거, mechanical/advisory layer 구분 ADR-027 Amendment 13 동반)
  - ADR-066  # CODEFORGE_CROSS_REPO_PAT scope invariant (§결정 2 6-scope, Administration:write 부재 — 본 ADR 의 1급 제약, operator gh auth 옵션 A 로 무손상)
  - ADR-005  # templates/scripts byte-identical mirror (신규 wire-* 배치 결정 cross-ref — scripts/ vs templates/scripts/)
  - ADR-113  # admin merge pre-flight gate / contexts strict match (context↔job-name 정합 게이트 cross-ref)
related_files:
  - scripts/wire-branch-protection.sh
  - scripts/wire-branch-protection.ps1
  - scripts/reapply-branch-protection.sh
  - scripts/reapply-branch-protection.ps1
  - scripts/bootstrap-consumer.sh
  - scripts/bootstrap-consumer.ps1
  - overlay/hooks/check_bootstrap.py
  - templates/scripts/setup-branch-protection.sh
  - templates/branch-protection-manifest.yaml
  - docs/consumer-guide.md
mechanical_enforcement_actions: []
is_transitional: false
sunset_justification: "N/A — permanent governance/security policy. ADR-058 §결정 7 security ADR default presumption 정합 (is_transitional: false). 본 ADR = 강화 방향 전용 (강제력 추가 — dead-gate 출고 차단, branch protection write 자동화). 1급 제약 ADR-066 §결정 2 PAT scope 무손상 (operator gh auth 옵션 A). 약화 방향 (codeforge PAT Administration:write 확장 / core contexts 삭제 / enforce_admins 우회 정상화) 발의 차단."
---

# ADR-132: consumer branch-protection 자동 wire 메커니즘

## 상태

`Proposed` (2026-06-30). Epic CFP-2468 (codeforge 강제력·검증 균질성 복구) Track W/W1 carrier. Story CFP-2469. Phase 2 (CFP-2469 구현 PR) 산출물(wire-* 스크립트 + bootstrap stage + readiness check + reapply) merge 시 Accepted.

## 컨텍스트

mctrader (첫 비-dogfood consumer, 16 repo) 회고 전수 점검에서 codeforge **강제력 부재** 의 체계적 갭이 드러났다. consumer 16 repo 중 15개 branch protection 0 → codeforge 게이트 workflow 가 파일로만 깔려 PR 마다 돌지만 merge 차단력 0 (**dead gate**). 보호된 1개도 `enforce_admins=false` · required review 0 · 게이트 1/6.

근원은 **"게이트 workflow 존재" vs "merge 차단력" 의 분리** 다:

| 영역 | 자동화 상태 (firsthand, 2026-06-29 KST) | 근거 |
|---|---|---|
| 게이트 workflow consumer 배포 | bootstrap-consumer 가 whitelist 기반 copy (CFP-2439, 30종) | `scripts/bootstrap-consumer.sh` Stage 5 workflow copy |
| branch protection PUT (required_status_checks 등록) | **0 — 전 영역 수동 operator** | `bootstrap-consumer.sh` grep "branch.protection|setup-branch-protection|required_status_checks|enforce_admins" = 0 match |
| readiness check 의 protection 점검 | **0** | `overlay/hooks/check_bootstrap.py` 10 check 중 protection 점검 부재 |
| drift preview helper | `templates/scripts/setup-branch-protection.sh` = **FORM (b) ZERO write** (GET-only dry-run) | setup-branch-protection.sh L4-6 "ZERO GitHub API write calls" |
| 실 PUT 경로 | consumer org admin 수동 1회 step | `docs/consumer-guide.md` L1848-1859 operator manual |

이는 codeforge 버그가 아니라 **설계상 의도적으로 수동 step 으로 남겨둔 영역** (ADR-024 Amendment 2 §결정 C step 2 + ADR-066 §결정 2 권한 invariant). 그러나 그 수동 step 이 강제력 부재(dead gate 출고)를 낳았다. 본 ADR = **권한 invariant 를 깨지 않으면서 그 step 을 자동 배선으로 전환** 하는 메커니즘 SSOT.

## 결정

### 결정 1 — write 로직 SSOT 추출 (`wire-branch-protection.{sh,ps1}` 신설)

branch protection write 로직을 신규 `scripts/wire-branch-protection.sh` + `scripts/wire-branch-protection.ps1` 단일 SSOT 로 추출한다. 3 호출부가 재사용:

1. **bootstrap stage** — consumer 초기화 시 1-repo 배선 (`bootstrap-consumer.{sh,ps1}` 신규 stage).
2. **readiness check** — `check_bootstrap.py` 가 배선 여부 점검 (read-only GET — wire-* 의 dry-run/inspect mode 재사용).
3. **reapply** — `reapply-branch-protection.{sh,ps1}` 가 N-repo 일괄 배선 시 repo-list loop 로 반복 호출.

**Separation of Duties (SoD)**: 기존 `templates/scripts/setup-branch-protection.sh` (FORM b, drift preview, ZERO-write) 는 **무손상 보존**. write 로직 = 신규 wire-*, drift-preview = 기존 setup-branch-protection.sh — preview ↔ write 분리. write 와 preview 가 한 스크립트에 섞이면 FORM(b) 의 "Administration:write credential 불요" 보장이 깨진다.

**배치 결정 (ModuleArch)**: 신규 wire-* / reapply-* = `scripts/` (NOT `templates/scripts/`). 이유 = operator 가 wrapper repo 셸에서 직접 실행하는 운영 도구 — consumer 가 byte-identical 복사할 대상이 아니다 (ADR-005 mirror 비대상). bootstrap stage 가 호출할 때는 plugin root 의 `scripts/` 경로를 참조. 향후 consumer 자기-wire (operator 부재 self-service) 필요 시 templates 미러 = follow-up 영역.

### 결정 2 — 권한 모델 = operator gh auth 토큰 (옵션 A, ADR-066 무손상)

자동 배선은 `branch protection PUT` = GitHub `Administration:write` scope 를 요구한다. codeforge 의 cross-repo PAT (`CODEFORGE_CROSS_REPO_PAT`) 에는 이 scope 가 **의도적으로 부재** — ADR-066 §결정 2 scope **6종** (`repo:read` / `repo:write` / `metadata:read` / `marketplace contents:read` / `reconcile-target-repos contents:write+pull_requests:write` / `cross-repo-target-repos issues:write`) 어디에도 `Administration:write` 없음. `admin:*` / `delete_repo` / org-wide write 는 명시 금지.

| 옵션 | credential 출처 | ADR-066 영향 | 판정 |
|---|---|---|---|
| **A (채택)** | operator 의 `gh auth` 토큰 (bootstrap/reapply 가 operator 셸에서 실행되는 그 권한) | **무손상** — codeforge PAT 미사용, operator 가 자기 org-admin 권한으로 PUT | 채택 |
| B | codeforge PAT 에 `Administration:write` grant | **정면 위반** — ADR-066 §결정 2 6-scope 확장 | 비채택 (영구 OOS) |

→ 자동 배선은 operator 가 bootstrap/reapply 를 실행하는 그 셸의 `gh auth` 토큰을 사용한다. operator 가 org-admin 이면 성공, 아니면 GitHub 403. **codeforge PAT scope 무변경** (ADR-066 §결정 2 6종 그대로).

### 결정 3 — 403 graceful degrade (WARN, not hard-fail)

operator 권한 부족(403) 시 배선은 **실패하지 않는다** — WARN 출력 + drift preview fallback (`setup-branch-protection.sh --dry-run`). bootstrap 전체 실패 사유가 아니다.

근거 = ADR-027 §결정 2 "Block 아님 — warning inject only" + enforcement = LLM/operator 측 책임. 권한 부족은 operator 환경 사실이지 codeforge 결함이 아니므로, 자동화는 가능한 만큼만 충전하고 나머지는 graceful degrade 한다.

**mechanical vs advisory layer 구분 (ADR-027 Amendment 13 paired)**: ADR-027 §결정 2 의 "Block 아님" 은 **hook 層 (UserPromptSubmit advisory) 한정** 이다. 본 ADR 이 충전하는 branch protection 層은 GitHub native `required_status_checks` = **mechanical merge-block** (Primary trigger 의 실효화). 즉 본 ADR = advisory hook 이 아니라 **mechanical protection layer 를 충전** → dead-gate 해소. 단 그 충전 *시도* 자체의 실패(403)는 advisory 영역으로 graceful 처리. 이 layer 구분이 dead-gate 해소의 핵심 — "게이트 workflow 존재 ≠ merge 차단력" 을 mechanical layer 충전으로 메운다.

### 결정 4 — context↔job-name 정합 게이트 (영구 pending 차단)

`required_status_checks.contexts[]` 에 등록하는 context 문자열은 **실제 배포된 workflow 의 job 표시명과 byte-identical** 이어야 한다. 불일치 시 등록 context 가 영원히 status 를 못 받아 **영구 pending** (PR 이 절대 merge 가능 상태로 못 감) — dead-gate(차단력 0)보다 악화된 상태(차단력 100%지만 통과 불가).

**배선 전 검증**: 각 context 가 실제 consumer repo 에 배포된 workflow 의 job 표시명과 1:1 정합하는지 검증한다. 미정합 context 는 **배선 제외 + WARN** (배선 자체를 abort 하지 않음).

**등록 context set 결정 (consumer-applicable, firsthand)**: wrapper 의 manifest core-4 contexts (`phase-gate-mergeable` / `invariant-check` / `doc frontmatter schema (CFP-28 — strict)` / `doc section schema (CFP-28 — strict)`) 는 **전부 consumer-distributable 이 아니다**:

- `phase-gate-mergeable.yml` = consumer whitelist 포함 (`templates/scripts/consumer_applicable_workflows.txt`). context 명 `phase-gate-mergeable` = dynamic `checks.create` status name (manifest type:dynamic — workflow job-id `check-gate` 가 아니라 동적 생성 check 명).
- `invariant-check.yml` = wrapper `.github/workflows/` 에만 존재 (templates 부재 + whitelist 부재) → **wrapper-self only**.
- `doc frontmatter/section schema (CFP-28 — strict)` 2 context = source workflow `lint.yml` 이 **실재** (wrapper `.github/workflows/lint.yml` L106·L119 가 그 2 job 표시명을 물리 emit, firsthand 2026-06-30 KST) 하나 **templates 부재 + consumer whitelist 부재** (`templates/scripts/consumer_applicable_workflows.txt` 에 `lint.yml` 미등재) → consumer 에 미전파·미실행 → **wrapper-self only**. 정적 등록 시 consumer 에서 영원히 status 미수신 = 영구 pending. (invariant-check 와 동형 — source 존재 여부와 무관하게 *whitelist 부재* 가 wrapper-self only 의 결정 원인.)

→ consumer 가 wrapper manifest 를 정적 복사해 배선하면 안 도는 context 3개를 등록 = 정확히 영구 pending 실패모드. **따라서 등록 context set = consumer 가 실제 배포·실행하는 workflow 의 job 표시명 ∩ codeforge 게이트** (정합 게이트가 동적 산출). 이것이 정합 게이트가 load-bearing 인 empirical 근거.

**input anchor SSOT**: context 명 strict-match 규칙 = `branch-protection-context-registry-v1.md` §3 (Archived 이나 schema invariant 보존 — "contexts[] array element string verbatim, byte-identical match: whitespace / em-dash / 괄호 포함").

### 결정 5 — 형상 파라미터 (solo deadlock 회피 + dead-gate 강화)

branch protection 강제력 dial 을 무작정 올리면 **solo-dev 영구 deadlock** 이 발생한다:

- `required_approving_review_count ≥ 1` + `enforce_admins: true` + **solo-dev (PR author 1인)** = 영구 deadlock. GitHub 은 PR author 자기승인을 금지 — admin/write 권한자도 자기 PR 승인 불가 (`source: docs.github.com about-protected-branches — "people with admin or write access ... cannot approve their own pull request"`). author 1인이면 승인할 사람이 없는데 `enforce_admins=true` 가 admin override 도 막아 merge 불가.

배선 default 형상:

| 필드 | default | 형상별 분기 | 근거 |
|---|---|---|---|
| `required_approving_review_count` | **shape param** | `solo=0` / `team(≥2 maintainer)=≥1` | solo deadlock 회피 + team review 강제 |
| `enforce_admins` | `true` | (불변) | dead-gate 차단 핵심 — admin 우회로 게이트 무력화 방지 (`source: docs.github.com about-protected-branches — "include administrators" 가 admin-override 차단`) |
| `restrictions` | `null` | (불변) | 빈 배열 `[]` = "아무도 push 못함" 또 다른 deadlock. GitHub API "restriction 없음" 의 올바른 표현 = `null` |
| `strict` | `true` | 형상별 override 여지 | merge 전 base 최신화 강제 (consumer-guide L1853 예시 정합 — **단 그 예시에서 정합 인용하는 것은 형상 4필드(`strict`/`review_count`/`enforce_admins`/`restrictions`) baseline 한정**. 같은 예시의 `contexts[]` 정적 리스트는 §결정 4 동적 정합 게이트 산출 대상이지 정적 복사 금지 — 그 리스트는 wrapper-self only context 3개를 포함) |

`enforce_admins=true` 는 dead-gate 차단 목적상 **유지가 옳다** (review_count=0 일 때 admin/non-admin 모두 required check 통과 의무 → admin 우회 무력화 차단). review_count 와의 조합이 deadlock 을 만들지 않게 **형상 인지가 필수** — review_count 형상 파라미터화가 그 조합 안전을 보장. 현 consumer-guide L1853-1856 예시 (`review_count:0 + enforce_admins:true + restrictions:null + strict:true`) 가 이미 solo-safe baseline.

### 결정 6 — idempotency = GET-merge-PUT (반복 실행 안전 + 무파괴)

bootstrap·reapply 는 여러 번 실행될 수 있다 (재초기화 / drift 복구 / 신규 repo). 배선은 **idempotent** + 기존 보호 설정 비파괴여야 한다.

- GitHub branch protection PUT = **full-replacement semantics** — PUT body 가 전체 보호 설정을 통째로 교체 (partial merge 아님) (`source: GitHub REST API "Update branch protection" — PUT replaces the entire protection object`). desired-state 전체를 매번 PUT 하면 자동 idempotent.
- 단, consumer 고유 보호 설정(추가 context 등)을 naive full-PUT 이 덮어쓴다. → **GET-merge-PUT**: 현 state GET → codeforge desired contexts 를 union merge → PUT. core contexts 삭제 불허 (append-only invariant, setup-branch-protection.sh `_validate_core4` 동형 — ADR-024 §결정 A 정합).
- 외부 corroboration: terraform github provider (`github_branch_protection`) + GitHub safe-settings 가 모두 declarative full-replacement reconcile 로 idempotency 를 달성하는 **산업 표준 모델** (`source: terraform-provider-github docs / github/safe-settings README`). 본 메커니즘은 그 "managed fields only" 패턴과 동형 — codeforge 관리 context 만 union, consumer 고유 설정 보존. (멱등 자체는 precedent 자동보장 가정 없이 CFP-2469 AC-5 `apply(apply(state))==apply(state)` 로 실측 검증.)

### 결정 7 — 16-repo 일괄 운영 (reapply-branch-protection)

`reapply-branch-protection.{sh,ps1}` = N-repo 일괄 재배선 경로 (mctrader 16 repo 등). 형태 결정:

- **채택**: 독립 스크립트가 `wire-branch-protection.{sh,ps1}` 를 repo-list loop 로 반복 호출. repo-list source = 명시 파라미터 또는 file. 이유 = 단일-repo wire 의 SRP 보존 (wire-* = 1-repo 원자 단위), reapply = orchestration layer 분리.
- 대안 (비채택): wire-* 에 `--all-repos` flag — 단일-repo 원자성과 일괄 orchestration 을 한 스크립트에 섞어 SRP 약화.

일괄 운영 리스크 3종:

1. **existence_check** — branch 부재 repo 는 skip (graceful, abort 금지).
2. **exponential backoff** — 16-repo 일괄 = GitHub API rate-limit (secondary rate limit 포함) 영역 → backoff 재시도.
3. **partial-failure 누적보고** — 한 repo 실패가 전체를 abort 시키지 않음. 끝까지 진행 후 실패 repo 목록 집계 보고.

### 결정 8 — readiness check 추가 (dead-gate 검출)

`overlay/hooks/check_bootstrap.py` 에 branch protection readiness check 를 추가한다 (**WARN tier** — 기존 10 check 의 advisory 관습 답습, ADR-027 §결정 2 default non-blocking 정합):

- consumer repo main branch 의 `required_status_checks.contexts[]` 미등록(dead gate) 검출 → WARN.
- `enforce_admins` 미설정 점검.

readiness 점검 경로는 2개다 (defense-in-depth, F-CR-2469-1): (1) `check_bootstrap.py` check 12 (`check_branch_protection_readiness` — SessionStart 진단 hook 경로) + (2) `scripts/check-debut-readiness.{sh,ps1}` Check 5 (명시 readiness 스크립트 경로 — 원 요구사항이 check-debut-readiness 를 dead-gate 출고 차단 surface 로 명시). 양자 동일 read-only GET 검증 (`required_status_checks.contexts[]` + `enforce_admins`), 호출 시점만 상이.

이 check 가 **drift 재감지 safety-net** 역할 — never-built weekly-cron `branch-protection-drift-check.yml` 을 *대체* 한다 (결정 9 참조).

### 결정 9 — dead-ref cluster 정리 (cleanup, not 실체화)

ADR-024 Amendment 2 §결정 B 가 선언한 drift-detection 자산은 **never-built** 이며 3-way dead-ref 를 형성한다 (firsthand, 2026-06-29 KST):

1. `templates/github-workflows/branch-protection-drift-check.yml` — ADR-024 §결정 B + related_files + manifest L6 + setup-branch-protection.sh L301 + consumer-guide L1859 가 SSOT 로 인용하나 **물리 부재** (templates + .github/workflows 양쪽 0건).
2. `scripts/check-branch-protection-drift.sh` — 문서 인용 존재하나 **물리 부재**.
3. `scripts/lib/workflow_branch_protection_drift_check.py` — **orphan** (부재 workflow 의 run-block helper, 어떤 `.yml`/`.sh` 도 참조 안 함 — `grep -rl ... --include=*.yml --include=*.sh` = 0건). **provenance (firsthand, file header)**: CFP-478 Phase 2 sub-PR b 가 ADR-061 Amendment 1 §결정 1.B "Block #26" (`branch-protection-drift-check.yml` lines 38-48 의 run-block 추출) 으로 생성 — 그 host workflow 가 끝내 never-built 이라 helper 만 orphan 잔존. cleanup 안전 = 외부 참조 0 (위 grep).

**결정 = 정리 (cleanup)**. 근거: 본 ADR 결정 8 readiness check 가 drift 재감지 safety-net 의 *대체* 이므로 never-built weekly-cron 실체화는 불요 (기능 중복, 6개월 미빌드). 대안 (실체화) = 비채택.

cleanup scope:

- (Phase 2) `scripts/lib/workflow_branch_protection_drift_check.py` orphan 삭제.
- (ADR-024 Amendment 20) related_files + §결정 B 의 drift-check.yml 인용을 "ADR-132 §결정 8 readiness check 로 대체" 로 명시.
- (Phase 2) `templates/branch-protection-manifest.yaml` L6 + `setup-branch-protection.sh` L301 + `docs/consumer-guide.md` L1859 의 drift-check.yml 참조를 readiness check 로 갱신.

## 대안

- **codeforge PAT 에 Administration:write grant (옵션 B)** — ADR-066 §결정 2 정면 위반. 영구 OSS. 기각.
- **GitHub Rulesets 마이그레이션** — legacy branch protection 1차 채택 (단일 main + basic 요구 = legacy 적합 구간, Rulesets 공식 deprecation 일정 없음 `source: docs.github.com — legacy 미deprecated`). Rulesets = follow-up Issue. 기각 (현 Story scope).
- **정적 manifest 복사 배선** — consumer 가 안 도는 wrapper-self context 등록 → 영구 pending. 기각 (결정 4 정합 게이트로 대체).
- **drift-check.yml 실체화** — readiness check 와 기능 중복. 기각 (결정 9).
- **mctrader 16 repo 실 배선 실행** — 본 Story = wrapper-self 도구 산출만. 실 배선 = Track M Story 또는 reapply 호출 (Epic 본문 "범위 밖").

## 결과

### 도입 효과

- consumer 게이트 workflow 의 **merge 차단력 충전** (dead-gate 출고 차단) — mechanical protection layer 자동 배선.
- ADR-066 §결정 2 PAT scope 무손상 (operator gh auth 옵션 A) — 자동화하되 codeforge 권한 미확장.
- solo-dev deadlock 0 (형상 파라미터) + 영구 pending 0 (context↔job 정합 게이트) + 무파괴 idempotent (GET-merge-PUT).
- readiness check 가 dead-gate 상태 검출·경고 + never-built drift-check 자산 정리.

### 영향 범위

- wrapper-self 도구 (신규 wire-*/reapply-* + bootstrap stage + readiness check). consumer-distributable 아님 (operator-run).
- consumer repo (배선 *대상* — 본 Story 는 도구만, 실 배선 = 별 Track).
- ADR-024 (Amendment 20 — step 2 수동→자동) + ADR-027 (Amendment 13 — mechanical/advisory layer) paired.

### 후속 carrier

- **GitHub Rulesets 마이그레이션** (legacy → Rulesets) — 별 Issue (legacy 1차).
- **consumer 자기-wire templates 미러** — operator 부재 self-service 필요 시 (현재 OOS).
- **mctrader 16 repo 실 배선** — Track M / reapply 호출 (Epic 본문 범위 밖).

## ADR-119 firsthand 인용

본 ADR 의 외부 지식 단정은 모두 source 인용:
- author 자기승인 금지 / enforce_admins admin-override 차단 = `docs.github.com about-protected-branches` 공식.
- branch protection PUT full-replacement semantics = GitHub REST API "Update branch protection".
- terraform/safe-settings full-replacement reconcile 표준 = terraform-provider-github docs / github/safe-settings README.
- legacy branch protection 미deprecated = docs.github.com (rulesets 공존).
repo 사실 단정은 firsthand 실측 (file:line 인용, 2026-06-29~30 KST).
