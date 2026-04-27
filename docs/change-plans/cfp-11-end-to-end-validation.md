---
title: CFP-11 end-to-end 실증 — Issue Form workflow 자동 동작 첫 검증 + 발견 drift 정합
slug: cfp-11-end-to-end-validation
status: draft
author: ClaudeOrchestrator (CFP-10 §11 후속)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-11
---

## §1. 목적

self-application 자동화 5층(CFP-1/2/4/5~10)의 finishing layer로 **사용자 → workflow 트리거 경로 첫 실측**. workflow 설계대로 동작하는지 + 환경 정합이 갖춰졌는지 reality check.

### 수용 기준

- Issue Form (story.yml) 제출 → story-init.yml workflow 7 step 모두 PASS
- auto-generated docs/stories/CFP-11.md가 §1 verbatim + §2-11 placeholder 양식
- 자동 open Phase 1 PR (label/base/head 정상)
- Issue body가 docs link로 자동 갱신
- 발견된 drift 모두 fix or 문서화

## §2. 현재 구조 분석

### 2.1 자동 chain 설계 (작성 시점 의도)

```
Issue 제출 (form) → story-init.yml fires
  → step 1: Checkout
  → step 2: Install yq
  → step 3: Compute next story key (`<PREFIX>-<N+1>`)
  → step 4: Parse user requirement (form 필드 awk 추출)
  → step 5: Create branch + docs/stories/<KEY>.md (template)
  → step 6: Create Phase 1 PR
  → step 7: Update Issue body to docs link
```

### 2.2 실측 결과 (Issue #39 → #41)

**1차 시도 (Issue #39)**: step 3에서 fail
- `sed: -e expression #1, char 44: Invalid collation character`
- Korean range `가-힣` ubuntu-latest C 로케일에서 reject

**2차 시도 (Issue #41, PR #40 fix 후)**: step 5까지 ✓, step 6에서 fail
- `GitHub Actions is not permitted to create or approve pull requests`
- org-level "Workflow permissions" → "Allow GitHub Actions to create and approve pull requests" OFF

**Pre-flight (Issue 제출 자체)**: label 부재로 fail
- `gh issue create --label "type:story" → not found`
- 18 plugin label 자동 부트스트랩 부재

### 2.3 자동 검증 부재

CFP-5~10이 모두 SSOT drift를 invariant CI로 검증하지만, **환경 정합 (org permission, label 존재)**은 별도 layer 필요. 사용자가 첫 시도할 때만 드러남.

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세** (단순화).

근거:
- workflow의 PR auto-create degrade는 영구적 복잡도 증가 — 1인 maintainer org 정책은 "한 번 enable하면 끝"
- 환경 정합은 부트스트랩 단계 명시가 더 lean
- code drift는 PR #40으로 fix, 환경 drift는 문서화로 충분

Mapper 의견(degrade graceful)은 미래 다른 org 정책 issue 발생 시 재검토 후보.

### 3.2 Drift 1 — sed Korean (PR #40 머지 완료)

```yaml
# Before
SLUG=$(printf '%s' "$ISSUE_TITLE" | sed -E 's/[^A-Za-z0-9가-힣]+/-/g; ...')
# After
SLUG=$(python3 - <<'PYEOF'
import os, re
title = os.environ.get("ISSUE_TITLE", "")
title = re.sub(r"^\[STORY\]\s*", "", title)
slug = re.sub(r"[^A-Za-z0-9가-힣]+", "-", title, flags=re.UNICODE)
slug = slug.strip("-")[:40].rstrip("-")
print(slug)
PYEOF
)
```

CFP-5 invariant 준수: `templates/github-workflows/story-init.yml` 동시 byte-identical.

### 3.3 Drift 2 — org permission (consumer-guide 보강)

`docs/consumer-guide.md`에 다음 부트스트랩 단계 추가:

```markdown
### Bootstrap (1회) — repo 또는 org admin 권한 필요

**1. org-level workflow permission**:
- https://github.com/organizations/<org>/settings/actions
- Workflow permissions → "Read and write permissions" 선택
- "Allow GitHub Actions to create and approve pull requests" 체크
- 미설정 시: story-init.yml의 PR auto-create step이 "GitHub Actions is not permitted to create or approve pull requests" 에러로 fail

**2. label 부트스트랩**:
- 신규 repo 생성 직후 plugin이 사용하는 18 label 부재
- 다음 명령 1회 실행 (또는 manual gh label create x18):

```
# (script 또는 명령 enumerate)
```
```

### 3.4 Drift 3 — label bootstrap (consumer-guide 보강)

위 §3.3에 통합. 향후 CFP-13에서 자동 부트스트랩 script 도입 후보.

### 3.5 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요 (CFP-12/13의 책임 분리는 ADR-003 후보 — 조건부)

## §4. API 계약

본 Story는 메타 validation — API 계약 변경 없음. workflow logic은 PR #40의 sed → Python 1건만 변경.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/story-init.yml` | 수정 (Drift 1 fix) | DocsAgent | PR #40 merged |
| `templates/github-workflows/story-init.yml` | 수정 (parity) | DocsAgent | PR #40 merged |
| `docs/consumer-guide.md` | 수정 (bootstrap 단계) | DocsAgent | 본 PR 진행 중 |
| `docs/stories/CFP-11.md` | 보강 (§2-11 채움) | DocsAgent | 본 PR 진행 중 |
| `docs/change-plans/cfp-11-end-to-end-validation.md` | 신규 | DocsAgent | 본 PR 진행 중 |

## §6. 리팩토링 선행 작업

**없음**.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** (메타 Story)
- **End-to-end 실측**: Issue #41 제출 → workflow 실행 → 산출물 검증. 본 Story가 곧 test 자체

### §8.2 경계 조건·invariant

§9.3 표 참조 (Pre-fix vs Post-fix). 5/7 step 정상 동작 + 2 step 환경 의존 입증.

### §8.3 Perf Baseline

**N/A**.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (메타 Story).

본 PR base는 `main`. 머지 전제: PR #40 merged ✓.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요
- ADR-003 (조건부) 후보: invariant 자동화 vs 환경 부트스트랩 vs 사용자 가이드의 책임 분리
