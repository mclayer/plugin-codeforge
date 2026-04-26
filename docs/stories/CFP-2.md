# CFP-2: Plugin Self-Application 인프라 2단계 — Issue Forms · Workflows · PR template · CODEOWNERS · overlay 정정

## §1. 사용자 요구사항 (verbatim)

CFP-1 §11 회고에서 발의된 후속 작업 + 본 세션에서 사용자 진행 지시:

> "이어서 쭉 수행하자" (CFP-1 PR #23 직후)

CFP-1 회고에 명시된 CFP-2 범위:

> **CFP-2 (예정)**: 인프라 2단계 — `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` + 6종 워크플로우 + branch protection. Plugin이 정의한 거버넌스 자동화의 자기 적용 완료.

> Plugin self-application 정책 도입(CFP-1)의 후속이며, dogfooding 인프라를 자동화 수준으로 끌어올림. CFP-1 §11에서 명시적으로 별도 Story로 분리하기로 결정한 작업.

## §2. 도메인 해석

본 변경의 도메인은 **plugin meta 거버넌스 인프라 적용**. CFP-1과 동일한 plugin meta 도메인이지만 출력물 성격이 다름:

- 도메인 제약: GitHub Actions 워크플로우는 `.github/workflows/` 디렉토리에서만 자동 실행, Issue Forms는 `.github/ISSUE_TEMPLATE/`에서만 인식, PR template은 `.github/PULL_REQUEST_TEMPLATE.md`로 단일. 경로가 GitHub native invariant
- 암묵 가정: workflow가 자동 동작하려면 GitHub Actions 활성화 + 적절한 토큰 권한 필요. plugin templates의 workflow는 이미 그 가정 위에 작성됨
- 범위 경계: `.github/` 인프라 + `.claude/_overlay/project.yaml` 정정. branch protection은 GitHub Settings UI/API에서만 설정 가능 → 코드 외 영역, PR body 가이드로 처리
- 우선순위: CFP-1 정책의 효과가 인프라 도입 시점부터 자동화로 안착

지식 공백: 없음 (plugin templates 활용, 추가 외부 지식 불요).

## §3. 관련 ADR

- **신규 ADR 필요 없음**: 인프라 적용은 Process Decision의 실행이며 Architecture Decision 아님
- ADR-001 (review-agent-unification): 무관

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.claude/_overlay/project.yaml` | 수정 | Plugin self-consumer overlay (PLG prefix dead state) | CFP prefix + 1인 maintainer codeowners + plugin components |
| `.github/ISSUE_TEMPLATE/` | 신규 | (디렉토리 비어있음) | Issue Forms 3종 (story/bug/audit) |
| `.github/workflows/` | 신규 (6종 추가) | `lint.yml`, `test.yml` (기존 유지) | + 6종 (story-init, phase-label-invariant, story-section-1-immutable, subissue-from-impl-manifest, phase-gate-mergeable, fix-ledger-sync) |
| `.github/PULL_REQUEST_TEMPLATE.md` | 신규 | (없음) | Plugin templates 표준 PR body |
| `.github/CODEOWNERS` | 신규 | (없음) | Plugin SSOT 영역 → @mccho8865 매핑 |
| `docs/stories/CFP-2.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-2-self-application-infra.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **Plugin maintainer가 신규 Story Issue 제출**: GitHub Issue Form (story.yml) → `story-init.yml` Action 자동 동작 → `docs/stories/CFP-N.md` 생성 + Phase 1 PR auto-open
2. **Plugin meta 변경 PR 생성**: `phase-gate-mergeable.yml`이 linked Story Issue의 phase·gate 라벨 검사, mergeable status 결정
3. **Plugin meta 변경에서 §10 FIX Ledger 행 추가**: `fix-ledger-sync.yml`이 자동 Issue 코멘트 + 라벨 부착
4. **다른 plugin/consumer가 codeforge 사용**: codeforge 자체가 dogfooding된 상태로 신뢰 검증

### Acceptance Criteria

- 다음 GitHub Issue Form 제출 시 `story-init.yml` Action이 정상 동작 (CFP-3.md 자동 생성·Phase 1 PR open)
- `.claude/_overlay/project.yaml`의 `story_key_prefix=CFP`가 기존 `docs/stories/CFP-1.md`와 일치
- CODEOWNERS가 PR review request에서 `@mccho8865`만 호출 (team 부재 경고 없음)
- Branch protection 가이드(PR body)에 1인 maintainer 한계 명시

### 엣지 케이스

- 1인 maintainer + Branch protection "Require Code Owner review" ON 시도: PR self-merge 막힘 → CODEOWNERS에는 `@mccho8865`이 있어도 PR author 자신 review request 못함. PR body에 OFF 권장 명시로 해결
- Workflow의 yaml syntax 오류: GitHub Actions UI에서 즉시 표시. Plugin templates는 consumer 운영 검증된 상태이므로 위험 낮음
- `.claude/_overlay/project.yaml` 정정 후 workflow trigger 시 prefix mismatch 가능성: CFP-1 commit과 본 변경 commit 사이에 새 Story가 들어오면 PLG prefix로 생성될 위험 → 본 PR 머지 전까지 plugin repo에 새 Story Issue 제출 자제 (사용자 자체 통제, 1인이라 안전)

### §5.5 사용자 확인 필요 (blocking wait — 모두 본 세션에서 확인 완료)

- [✓] CFP-2 작업 진행 결정 ("이어서 쭉")
- [✓] CODEOWNERS team vs 개인 — `@mccho8865` 1인 매핑 (1인 maintainer)
- [✓] PR #23 위 stack 진행 (자동 rebase to main 후 머지)

## §6. 외부 지식 배경

본 변경은 plugin templates 활용에 한정. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: GitHub Actions trigger semantics는 plugin templates의 작성 시점에 검증된 사실이고, 본 변경은 그 templates를 단순 복사. 외부 라이브러리·표준·선행사례 별도 조사 없음.

ADR 정합성: 신규 ADR 없음, ADR-001 무관. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-2-self-application-infra.md`](../change-plans/cfp-2-self-application-infra.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: CFP-1 1단계(정책+`docs/stories/`)에 이어 GitHub Actions 자동화로 dogfooding 완성. `story-init.yml` 등 6종 워크플로우 + Issue Forms + CODEOWNERS + PR template 인프라 도입.

**§3 도입할 설계**:
- `.claude/_overlay/project.yaml` 정정 (PLG → CFP, team → @mccho8865, components 확장)
- `.github/ISSUE_TEMPLATE/` 3종 (templates/github-issue-forms/ 복사)
- `.github/workflows/` 6종 추가 (templates/github-workflows/ 복사, 기존 lint/test 보존)
- `.github/PULL_REQUEST_TEMPLATE.md` (templates/github-pr-template.md 복사)
- `.github/CODEOWNERS` (1인 maintainer 매핑)

**§4 API 계약**: GitHub Actions trigger 매트릭스(Change Plan §4.2 표). CODEOWNERS 1인 매핑 + Branch protection "Require Code Owner review" OFF 권장.

**§9 분기 선택**: 단일 PR + 3 commit 분할 (overlay 정정 / 인프라 일괄 / Story 영속화).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "워크플로우 자동화 도입 = 운영 부담. 1인 환경에서 Issue Forms·CODEOWNERS는 의례적이고 실효성 낮음."
- **Refactor(혁신)**: "Plugin이 자기 거버넌스를 dogfooding하지 않으면 consumer 신뢰 약화. CFP-1 정책 후 인프라 적용 미루면 정책 자체가 약해짐."
- **채택: Refactor**. 근거: Plugin templates의 workflow가 plugin 자체에서 검증 안 되면 consumer가 처음 발견할 위험. dogfooding의 본질 = 자기 도구 자기 적용.

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta 변경, 코드 산출물 없음**.

본 변경은 GitHub 인프라 파일 복사 + yaml 정정에 한정. `role: dev` roster 활성화 없음. DocsAgent가 단독 작성 (본 세션에서 직접 진행).

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `.claude/_overlay/project.yaml` | 수정 | DocsAgent | +20 / -15 (재작성) | Change Plan §3.2 A |
| `.github/ISSUE_TEMPLATE/story.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 B |
| `.github/ISSUE_TEMPLATE/bug.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 B |
| `.github/ISSUE_TEMPLATE/audit.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 B |
| `.github/workflows/story-init.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 C |
| `.github/workflows/phase-label-invariant.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 C |
| `.github/workflows/story-section-1-immutable.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 C |
| `.github/workflows/subissue-from-impl-manifest.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 C |
| `.github/workflows/phase-gate-mergeable.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 C |
| `.github/workflows/fix-ledger-sync.yml` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 C |
| `.github/PULL_REQUEST_TEMPLATE.md` | 신규 | DocsAgent (cp) | 신규 | Change Plan §3.2 D |
| `.github/CODEOWNERS` | 신규 | DocsAgent | 신규 | Change Plan §3.2 E |
| `docs/stories/CFP-2.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-2-self-application-infra.md` | 신규 | DocsAgent | 신규 | Change Plan 본 파일 |

> Plugin self-application 1단계와 동일하게 `subissue-from-impl-manifest.yml` Action이 본 PR에서 처음 활성화되지만, 본 PR 자체가 인프라 도입이라 trigger 발생 안 함. 첫 sub-issue 자동 생성은 다음 Phase 2 PR 시점.

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음 — 본 Story는 CFP-1 회고 기반 + 사용자 1회 confirmation으로 진행.

### §9.1 설계 리뷰

**N/A — 별도 설계 리뷰 lane 면제 사유**: brainstorming skill의 사용자 approval (Change Plan §1-10) 자체가 설계 검증 역할. PR review에서 reviewer가 정합성 추가 확인.

### §9.2 구현 리뷰

**N/A — 인프라 파일 복사·yaml 정정, 코드 리뷰 lane 무관**. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**N/A — 자동 단위/통합 테스트 대상 아님**. 검증은 다음 Story Issue Form 제출 시 workflow 동작 관찰 (수동, 별도 시점).

### §9.4 보안 테스트

**N/A — 의존성·attack surface 변경 없음**. Workflow 권한(`permissions`)은 plugin templates에서 minimal scope으로 정의됨 (templates 자체 신뢰 가정).

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## §11. 참조

- **GitHub Issue URL**: 부재 (CFP-2 자체가 Issue Forms 도입 PR이므로 Issue 사전 생성 불가능 — chicken-and-egg)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base PR (stack)**: PR #23 (CFP-1, `feat/cfp-1-self-application`)
- **Change Plan**: [`docs/change-plans/cfp-2-self-application-infra.md`](../change-plans/cfp-2-self-application-infra.md)
- **CFP-1 Story**: [`docs/stories/CFP-1.md`](CFP-1.md)

### 회고

**발견 1 — Chicken-and-egg**: Issue Forms를 도입하는 PR 자체는 Issue Forms로 트리거 못함. CFP-2가 인프라 자체이므로 GitHub Issue 사전 생성 없이 진행. 향후 CFP-3부터는 Issue Forms로 정상 진행 가능.

**발견 2 — Existing overlay drift**: `.claude/_overlay/project.yaml`이 plugin templates의 PLG prefix placeholder로 작성된 채 dead state로 존재. CFP-1에서 prefix=CFP 결정 후 본 PR에서 정정. **Workflow 자동화를 안 적용하면 overlay drift가 발견되지 않는 패턴** — dogfooding이 필요한 근거 보강.

**발견 3 — 1인 maintainer + CODEOWNERS 한계**: GitHub은 PR author를 reviewer로 자동 request 안 함. CODEOWNERS는 audit/문서화 용도로만 사용, Branch protection의 "Require Code Owner review"는 OFF. 향후 collaborator 추가 시 ON 격상.

**향후 작업 (별도 Story)**:
- **CFP-3 (잠정)**: `story_cutoff` schema validation 자동화 (pre-commit hook 또는 CI gate). CFP-1 정책의 강제 항목 축소 시도 자동 차단.
- **CFP-4 (잠정)**: Plugin self-application 첫 정상 사용 사례 — Issue Forms로 시작하는 일반 변경 (예: README 보강, 새 에이전트 도입 등)으로 workflow 자동화 동작 검증.
- **ADR-002 (조건부)**: Process Decision도 ADR 대상으로 격상하는 거버넌스 결정.
