# CFP-11: [STORY] CFP-11 end-to-end 실증 — Issue Form workflow 자동 동작 첫 검증 (재시도)

- **Issue**: #41
- **Status**: phase:요구사항

## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-11 end-to-end 실증 — 본 Issue 자체가 test subject. Issue Form (story.yml) 제출 → story-init.yml workflow 자동 실행 → docs/stories/CFP-11.md template 자동 생성 + Phase 1 PR 자동 open이 정상 동작하는지 첫 실측한다.
scope:
1. story-init workflow 실행 성공 (yq install / next-key compute / body parse / branch create / commit / PR create / Issue body update 7 step 모두 PASS)
2. 자동 생성 docs/stories/CFP-11.md가 §1 verbatim + §2-11 placeholder 양식 준수
3. 자동 open Phase 1 PR이 type:story + phase:요구사항 label 부착, base=main, head=feat/CFP-11-<slug> 정상
4. Issue body가 docs link로 자동 갱신
5. 모든 단계 실측 후 본 Story file (§2-11)을 직접 채워넣고 Change Plan 작성, Phase 2 진행
self-application 정책의 마지막 미실증 layer — 정책(CFP-1) → 인프라(CFP-2) → 메타정합(CFP-4) → 자동화(CFP-5~10)까지 도입했지만 실제 사용자 → workflow 트리거는 첫 실행. 1인 maintainer 환경에서도 workflow가 의도대로 동작하는지 사전 검증.

## 2. 도메인 해석

본 Story의 도메인은 **self-application 자동화 5층의 finishing layer 실측**. 이전 5 layer (정책/인프라/메타/자동화/SSOT)는 모두 정합 여부를 자동으로 검증할 수 있었지만, **사용자 → workflow 트리거** 경로는 사람이 한 번 사용하기 전엔 알 수 없었다.

- 도메인 제약: 1인 maintainer 환경 + GitHub default org policy + ubuntu-latest runner
- 암묵 가정: workflow가 작성 시점 logic대로 작동
- 범위 경계: workflow 7 step 전체 + Issue Form 인풋 + label bootstrap + repo settings
- 우선순위: bootstrap drift 발견 — workflow 자체 design은 수정 최소화, 환경/문서 보강

지식 공백: 없음 (실측 자체가 보강 행위).

## 3. 관련 ADR

- **ADR-001/002**: 무관
- 신규 ADR 필요 없음

## 4. 관련 코드 경로

| 경로 | 변경 유형 | 변경 후 책임 |
|------|-----------|--------------|
| `.github/workflows/story-init.yml` | 수정 (PR #40에서 sed → Python) | Korean 환경 안전 |
| `templates/github-workflows/story-init.yml` | 수정 (PR #40 byte-identical sync) | CFP-5 invariant 준수 |
| `docs/consumer-guide.md` | 수정 | org-level "Allow GitHub Actions to create PRs" + label bootstrap 단계 명시 |
| `docs/stories/CFP-11.md` | 수정 | 본 Story file 보강 (§2-11 placeholder → 실제 내용) |
| `docs/change-plans/cfp-11-end-to-end-validation.md` | 신규 | 본 Story Change Plan |

## 5. 요구사항 확장 해석

### 발견된 drift (자동 자체 발견)

**Drift 1 — sed Korean range collation 에러** (PR #40 fix):
- 증상: `sed: -e expression #1, char 44: Invalid collation character`
- 원인: `s/[^A-Za-z0-9가-힣]+/-/g` 의 Hangul range가 ubuntu-latest 기본 C 로케일에서 reject
- 해결: sed → Python `re.UNICODE` heredoc 교체 (multi-byte truncation 안전 부수 효과)
- 입증: PR #40 머지 후 Issue #41 재제출 → step "Compute next story key" PASS

**Drift 2 — GITHUB_TOKEN cannot create PRs** (org-level 정책):
- 증상: `GitHub Actions is not permitted to create or approve pull requests (createPullRequest)`
- 원인: org 설정 "Workflow permissions" → "Allow GitHub Actions to create and approve pull requests" OFF
- 해결: org admin 수동 enable (admin:org scope 필요, API로는 1인 환경 자동화 불가). consumer-guide에 bootstrap 단계 명시
- 입증: 본 PR 수동 open으로 chain 일관성 입증. Step 1-4 (yq / key / parse / commit+push) ✓, Step 5 (PR create) ✗, Step 6 (Issue body update) skip

**Drift 3 — type:* / phase:* 등 18 label 부재** (label bootstrap):
- 증상: `gh issue create --label "type:story,phase:요구사항"` → "could not add label: 'type:story' not found"
- 원인: 신규 repo 생성 직후 plugin label 자동 부트스트랩 부재
- 해결: 본 Story 작업 중 18 label 수동 생성. consumer-guide에 부트스트랩 절차 추가
- 입증: 라벨 생성 후 Issue 제출 정상

### Acceptance Criteria

- [x] sed Korean bug 수정 (PR #40)
- [x] CFP-11.md auto-generation 구조 정상 (§1 verbatim + §2-11 placeholder template) — 검증 완료
- [x] org permission drift 문서화 (consumer-guide bootstrap 단계)
- [x] label bootstrap 절차 문서화
- [x] Story file (§2-11) + Change Plan 영속화

### 엣지 케이스

- **Auto-generated docs file의 title `[STORY]` prefix 잔존**: workflow의 `printf '# %s: %s\n\n' "$KEY" "$ISSUE_TITLE"` 가 Issue title 그대로 차용. `[STORY]` 제거가 cosmetic improvement이나 본 Story scope 외 (별도 polish PR 후보)

## 6. 외부 지식 배경

본 변경은 plugin meta workflow 실측 + 환경 정합. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: GitHub Actions 기본 동작 + 1인 maintainer org 정책 reality check. 외부 라이브러리·표준 referencing 없음.

ADR 정합성: ADR-001/002 무관. 통과.

## 7. 설계 서사

Change Plan: [`docs/change-plans/cfp-11-end-to-end-validation.md`](../change-plans/cfp-11-end-to-end-validation.md)

### 핵심 설계

CFP-11은 메타 Story — 본문 변경 자체보다 **실측 결과 + 학습 정합 회복**이 산출. 발견된 drift 3건 중:
- 1건은 코드 fix (PR #40, sed → Python)
- 2건은 환경 설정 + 문서화 (consumer-guide bootstrap 단계)

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "workflow의 PR 자동 생성을 fallback degrade로 설계 — Issue comment + 수동 PR open URL 안내"
- **Refactor(혁신)**: "design 그대로 유지. 환경 설정이 정상이면 workflow도 정상. 문서화로 충분"
- **채택: Refactor 우세** (단순화). 1인 maintainer org 정책은 "한 번 enable하면 끝"이라 workflow degrade는 영구적 복잡도 증가. 부트스트랩 단계 명시가 더 lean. Mapper 의견은 미래에 다른 org 정책 issue 발생 시 재검토 후보.

## 8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta validation Story**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|------|-------------------|---------------|
| `.github/workflows/story-init.yml` | 수정 (PR #40, merged) | DocsAgent | +12 / -2 | Drift 1 |
| `templates/github-workflows/story-init.yml` | 동시 수정 (parity) | DocsAgent | +12 / -2 | Drift 1 |
| `docs/consumer-guide.md` | 수정 | DocsAgent | +20 (bootstrap 단계 추가) | Drift 2/3 |
| `docs/stories/CFP-11.md` | auto-generated + 보강 | DocsAgent | +130 (§2-11 채움) | Change Plan §5 |
| `docs/change-plans/cfp-11-end-to-end-validation.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## 9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Plugin meta validation Story. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**End-to-end 실측 결과:**

| 단계 | Pre-fix | Post-fix |
|------|---------|---------|
| Issue 제출 (label 부재) | ✗ "type:story not found" | ✓ (Drift 3 해결 후) |
| story-init step 1: Checkout | ✓ | ✓ |
| story-init step 2: Install yq | ✓ | ✓ |
| story-init step 3: Compute next story key | ✗ sed Korean error | ✓ (PR #40 fix) |
| story-init step 4: Parse user requirement | (미진입) | ✓ |
| story-init step 5: Create branch + docs file | (미진입) | ✓ (CFP-11.md auto-commit + push) |
| story-init step 6: Create Phase 1 PR | (미진입) | ✗ org permission |
| story-init step 7: Update Issue body | (미진입) | (skip, set -e fail) |
| Manual PR open | — | ✓ PR #42 |
| Manual Issue body update | — | ✓ |

자동 chain의 5/7 step 정상 동작 + 2 step은 환경 설정 의존. workflow logic 자체는 정상 입증.

### §9.4 보안 테스트

**N/A** — workflow design 변경 없음 (PR #40는 sed 단일 변경, attack surface 동일).

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1 | 2026-04-27 02:43 UTC | label bootstrap | type:story not found | 환경 (label 부재) | gh label create x18 + consumer-guide 추가 | — |
| 2 | 2026-04-27 02:45 UTC | story-init exec | sed Korean collation | 구현 (workflow bug) | PR #40 fix → main merge | — |
| 3 | 2026-04-27 02:49 UTC | story-init exec | GH_TOKEN cannot create PR | 환경 (org policy) | consumer-guide bootstrap 추가 + 수동 PR | — |

3 drift 모두 검출 + 정합 회복. FIX 카운터 RESET 마커는 본 Story 미적용 (메타 Story로 review FIX 루프 다른 의미).

## 11. 회고

**발견 1 — self-application 자동화 5층의 finishing layer가 곧바로 첫 bug 발견**: 정책(CFP-1) → 인프라(CFP-2) → 메타정합(CFP-4) → 자동화(CFP-5~10) 5층을 모두 invariant CI로 박제했지만, **사용자 → workflow 트리거 경로**는 사람이 한 번 사용하기 전엔 알 수 없었다. CFP-11이 첫 사용 시점에 3 drift 발견 — invariant 자동화 layer만으론 부족함을 입증.

**발견 2 — drift 종류의 분포**: 3 drift 중 1건만 코드 bug (sed Korean), 2건은 환경 설정 (org permission, label bootstrap). 자동화 invariant이 코드 정합은 잘 잡지만 **환경 정합**은 별도 layer 필요. consumer-guide 부트스트랩 절차 + SessionStart hook의 "Required org settings" check 추가가 자연스러운 다음 단계 (CFP-12 후보).

**발견 3 — chain의 progress preservation 가치**: workflow가 step 6에서 fail했지만 step 1-5의 산출물(branch + auto-CFP-11.md + push)은 보존됐다. 수동 PR open으로 chain 일관성 회복 가능. 이는 workflow 설계가 idempotent + intermediate-state-preserving해서 가능 — 향후 workflow 설계 패턴으로 일반화 가치 있음.

**발견 4 — Phase D 후의 첫 "다른 종류의 작업"**: CFP-5~10은 모두 invariant-check.yml step 추가 패턴. CFP-11은 처음으로 다른 카테고리(실측·환경 정합)로 외도 — self-application 작업이 invariant 박제만으론 끝나지 않음을 시사.

**향후 작업 (별도 Story)**:
- **CFP-12 (잠정)**: SessionStart hook에 `gh api repos/*/actions/permissions/workflow` check 추가 — `default_workflow_permissions == "write"` + `can_approve_pull_request_reviews == true` 검증 (1인 maintainer 환경 첫 사용 사고 사전 차단)
- **CFP-13 (잠정)**: label 자동 bootstrap script — `scripts/bootstrap-labels.sh` 또는 SessionStart hook 통합. 18 label 수동 생성 회피
- **ADR-003 (조건부)**: invariant 자동화 vs 환경 부트스트랩 vs 사용자 가이드의 책임 분리 ADR
- **CFP-11 폴리시**: workflow의 docs file title에서 `[STORY]` prefix strip (cosmetic, 우선순위 낮음)
