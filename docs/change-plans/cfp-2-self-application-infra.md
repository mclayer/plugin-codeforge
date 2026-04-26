---
title: Plugin Self-Application 인프라 2단계 — Issue Forms · Workflows · PR template · CODEOWNERS · overlay 정정
slug: cfp-2-self-application-infra
status: draft
author: ClaudeOrchestrator (CFP-1 §11 회고 기반)
reviewers: [user]
related_adrs: []
created: 2026-04-26
story: CFP-2
---

## §1. 목적

CFP-1에서 도입한 Plugin Self-Application 정책의 **인프라 2단계** 적용. 1단계(정책 명시 + `docs/stories/` 디렉토리)에 이어, GitHub Actions 자동화로 dogfooding 완성.

### 수용 기준

- `.claude/_overlay/project.yaml`이 CFP-1 결정(prefix `CFP`, 1인 maintainer codeowners)과 일치
- `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` 3종 존재 — Issue Forms 제출 가능
- `.github/workflows/`에 plugin이 정의한 6종 워크플로우 (`story-init.yml`, `phase-label-invariant.yml`, `story-section-1-immutable.yml`, `subissue-from-impl-manifest.yml`, `phase-gate-mergeable.yml`, `fix-ledger-sync.yml`) 존재
- `.github/PULL_REQUEST_TEMPLATE.md` 존재 — PR 생성 시 표준 템플릿
- `.github/CODEOWNERS` 존재 — `@mccho8865` 1인 매핑
- 다음 Story부터 `story-init.yml` Action이 자동으로 docs file 생성 + Phase 1 PR open
- Branch protection 가이드는 PR body로 제공 (코드로 표현 불가)

## §2. 현재 구조 분석

### 2.1 Plugin repo의 self-application 인프라 부재

CFP-1 §2.1에서 식별:
- `docs/stories/` 디렉토리 부재 → CFP-1에서 신설 완료
- `.github/workflows/`에 plugin templates 6종 부재 → 본 변경에서 적용
- `.github/ISSUE_TEMPLATE/` 부재 → 본 변경에서 적용
- `.github/CODEOWNERS` 부재 → 본 변경에서 적용
- `.github/PULL_REQUEST_TEMPLATE.md` 부재 → 본 변경에서 적용

### 2.2 기존 `.claude/_overlay/project.yaml` 모순

이미 존재하나 CFP-1 결정과 불일치:

| 키 | 기존 (불일치) | CFP-1 결정 |
|---|---|---|
| `github.story_key_prefix` | `PLG` | `CFP` |
| `codeowners.architect_team` | `@mctrader/architects` (team 부재) | `@mccho8865` (1인) |
| `codeowners.domain_expert_team` | `@mctrader/domain-experts` (team 부재) | `@mccho8865` (1인) |
| `labels.components` | `[codeforge]` (단일) | `[agents, docs, templates, workflows, presets, core, infra]` (Plugin 자체 영역) |

이 overlay는 plugin이 자기 workflow를 적용 안 하던 시기의 dead artifact. 본 변경에서 정정해 workflow가 정상 동작하도록.

### 2.3 1인 maintainer 환경 제약

`mctrader` GitHub org에 architect/domain-expert team 부재. CODEOWNERS는 `@mccho8865` 1인에 매핑. Branch protection의 "Require review from Code Owners"를 켜면 PR author 자신은 자동 reviewer로 request되지 않아 PR이 영원히 unreviewed 상태로 막힘 → 1인 환경에서 OFF 권장.

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

- **Mapper(보수)**: "워크플로우 자동화 도입은 추가 운영 부담. workflow 디버깅 복잡. 1인 환경에서 Issue Forms·CODEOWNERS는 의례적이고 실효성 낮음."
- **Refactor(혁신)**: "Plugin이 자기 거버넌스를 dogfooding하지 않으면 consumer 신뢰 약화. CFP-1 정책의 인프라 측면을 미루면 정책 자체가 약해짐."
- **채택: Refactor**. 근거: CFP-1에서 정책 도입 시 이미 인프라 2단계는 별도 Story로 분리한 약속. 자동화 안 적용하면 `story-init.yml` 같은 templates의 동작이 plugin repo에서 검증 안 됨 → consumer가 받았을 때 처음으로 버그 발견할 위험.

Mapper 우려는 §3.5 Branch protection 가이드 PR body 제공 (코드 도입 아닌 안내) + 1인 환경 한계 명시로 흡수.

### 3.2 변경 영역

**A. `.claude/_overlay/project.yaml` 정정** (기존 파일 수정):
- `story_key_prefix: PLG` → `CFP`
- `codeowners.architect_team` → `@mccho8865`
- `codeowners.domain_expert_team` → `@mccho8865`
- `labels.components` → `[agents, docs, templates, workflows, presets, core, infra]`

**B. `.github/ISSUE_TEMPLATE/`** (신규):
- `templates/github-issue-forms/story.yml` → `.github/ISSUE_TEMPLATE/story.yml`
- `templates/github-issue-forms/bug.yml` → `.github/ISSUE_TEMPLATE/bug.yml`
- `templates/github-issue-forms/audit.yml` → `.github/ISSUE_TEMPLATE/audit.yml`

**C. `.github/workflows/`** (신규 6종 추가, 기존 `lint.yml` · `test.yml` 보존):
- `templates/github-workflows/story-init.yml` → `.github/workflows/story-init.yml`
- `templates/github-workflows/phase-label-invariant.yml` → `.github/workflows/phase-label-invariant.yml`
- `templates/github-workflows/story-section-1-immutable.yml` → `.github/workflows/story-section-1-immutable.yml`
- `templates/github-workflows/subissue-from-impl-manifest.yml` → `.github/workflows/subissue-from-impl-manifest.yml`
- `templates/github-workflows/phase-gate-mergeable.yml` → `.github/workflows/phase-gate-mergeable.yml`
- `templates/github-workflows/fix-ledger-sync.yml` → `.github/workflows/fix-ledger-sync.yml`

**D. `.github/PULL_REQUEST_TEMPLATE.md`** (신규):
- `templates/github-pr-template.md` 그대로 복사

**E. `.github/CODEOWNERS`** (신규):
- `templates/CODEOWNERS.template` 기반, `@ORG/ARCHITECT_TEAM` · `@ORG/DOMAIN_EXPERT_TEAM` placeholder를 `@mccho8865`로 치환
- Plugin SSOT 영역(`CLAUDE.md`, `templates/**`) 추가 매핑

### 3.3 Workflow 동작 검증 가능성

각 워크플로우의 첫 트리거 시점:
- `story-init.yml`: 다음 Story Issue Form 제출 시 (사용자가 `[STORY]` Issue 만들면 자동 동작)
- `phase-label-invariant.yml`: 다음 phase 라벨 추가 시
- `story-section-1-immutable.yml`: 다음 Story PR에 §1 변경 포함 시 자동 reject
- `subissue-from-impl-manifest.yml`: 다음 Phase 2 PR이 §8.5 매핑표 commit 시
- `phase-gate-mergeable.yml`: PR이 `Closes #N` 키워드로 Story Issue를 link하면 자동 동작
- `fix-ledger-sync.yml`: Story file §10에 새 행 추가되어 main에 push될 때

본 PR 자체로는 workflow 동작이 발생하지 않음 (Issue/PR 생성·label 변경 등이 없으므로). 동작 검증은 다음 Story(CFP-3 등)에서 실증.

### 3.4 Branch protection 가이드 (PR body로 제공)

GitHub Settings > Branches > Branch protection rule for `main`:
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging:
  - `phase-gate-mergeable` (필수)
  - `lint` (기존)
  - `test` (기존, 있다면)
- ❌ Require review from Code Owners (1인 maintainer 환경에서 OFF 권장 — self-merge 막힘 방지)
- ✅ Require linear history (선택)
- ✅ Do not allow bypassing the above settings (선택, 단 이를 켜면 admin도 우회 못함)

### 3.5 ADR 정합성

- 신규 ADR 필요: **없음**. Process Decision의 인프라 적용이며 Architecture Decision 아님
- ADR-001 영향 없음
- 향후 Process Decision도 ADR 격상하면 ADR-002로 발의 검토

## §4. API 계약

### 4.1 Issue Forms 입력 schema

기존 `templates/github-issue-forms/*.yml` 그대로. 변경 없음 (단순 복사).

### 4.2 Workflow trigger 매트릭스

| Workflow | Trigger | 동작 |
|---|---|---|
| `story-init.yml` | `issues.opened` + label `type:story` + `phase:요구사항` | docs file 생성 + Phase 1 PR open |
| `phase-label-invariant.yml` | `issues.labeled` `phase:*` 추가 | 기존 phase 라벨 자동 detach |
| `story-section-1-immutable.yml` | `pull_request.opened/synchronize` | docs/stories/<KEY>.md §1 변경 PR auto-reject |
| `subissue-from-impl-manifest.yml` | `push` to PR branch (Phase 2) + Story file §8.5 변경 | 파일 단위 sub-issue 자동 생성 |
| `phase-gate-mergeable.yml` | `pull_request.opened/synchronize/labeled/unlabeled` + `issues.labeled/unlabeled` | linked Issue의 phase·gate 라벨 검사, mergeable status 결정 |
| `fix-ledger-sync.yml` | `push` to main (또는 PR) + Story file §10 새 행 | Issue `[FIX #N]` 코멘트 + `fix:<레인>-retry` 라벨 자동 |

### 4.3 CODEOWNERS 매핑

§3.2 E 참조. 1인 maintainer는 GitHub Settings에서 Branch protection의 "Require review from Code Owners" OFF 권장 (자가 review 차단 방지).

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.claude/_overlay/project.yaml` | 수정 | DocsAgent (= 본 작업자) | 적용 완료 |
| `.github/ISSUE_TEMPLATE/story.yml` | 신규 | DocsAgent | 적용 완료 (cp from templates/) |
| `.github/ISSUE_TEMPLATE/bug.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/ISSUE_TEMPLATE/audit.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/workflows/story-init.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/workflows/phase-label-invariant.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/workflows/story-section-1-immutable.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/workflows/subissue-from-impl-manifest.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/workflows/phase-gate-mergeable.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/workflows/fix-ledger-sync.yml` | 신규 | DocsAgent | 적용 완료 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 신규 | DocsAgent | 적용 완료 |
| `.github/CODEOWNERS` | 신규 | DocsAgent | 적용 완료 |
| `docs/stories/CFP-2.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-2-self-application-infra.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 기존 파일 보존 + 단순 복사 + overlay 정정.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — 인프라 파일 복사·yaml 정정만, 코드 변경 없음
- 통합 테스트: **N/A**
- 인프라 테스트: **워크플로우 syntax 검증** (GitHub Actions가 push 시 자동 lint). actionlint 별도 실행은 본 PR scope 밖
- **검증 방법**: 다음 Story(예: CFP-3 또는 임의 Issue Form 제출)에서 workflow 자동 동작 관찰. 본 PR 자체는 trigger 없음

### §8.2 경계 조건·invariant

- `.claude/_overlay/project.yaml`의 `story_key_prefix=CFP`와 기존 `docs/stories/CFP-1.md` 일치 — invariant 유지
- CODEOWNERS 1인 매핑이 GitHub에서 valid한지 — `gh api users/mccho8865`로 사전 검증 완료 (login 확인됨)
- `.github/workflows/`의 기존 `lint.yml` · `test.yml` 보존 — 신규 6종은 추가만, 기존 덮어쓰기 없음
- `mctrader/architects` team이 placeholder로 남으면 GitHub이 "team 없음" 경고 → 본 변경에서 `@mccho8865`로 정정해 경고 제거

### §8.3 Perf Baseline

**N/A** — 인프라 추가, 성능 영향 없음.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (Plugin meta 변경, 구현/테스트/보안 lane N/A).

Commit 시리즈 3개로 본질 분리:
- **Commit 1**: `.claude/_overlay/project.yaml` 정정 (CFP-1 결정 sync)
- **Commit 2**: `.github/ISSUE_TEMPLATE/` + `.github/workflows/` + `.github/PULL_REQUEST_TEMPLATE.md` + `.github/CODEOWNERS` (인프라 일괄 도입)
- **Commit 3**: `docs/stories/CFP-2.md` + `docs/change-plans/cfp-2-...md` (Story 영속화)

본 PR base는 `feat/cfp-1-self-application` (PR #23). PR #23 머지되면 자동 rebase to main.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-001** (review-agent-unification): **무관**. 본 변경은 거버넌스 인프라
- **신규 ADR 필요**: **없음**. Process Decision 인프라 적용. 향후 Process Decision도 ADR 격상되면 ADR-002 발의
