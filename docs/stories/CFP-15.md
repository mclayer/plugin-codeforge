# CFP-15: story-init workflow의 docs h1·PR title `[STORY]` prefix strip (CFP-11 폴리시)

## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-14 PR #46 머지 직후 사용자 (autonomy mode 인가 연장):

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해"

CFP-11 §11에 명시된 폴리시 후보 + CFP-14 §11 회고에서 재명시:

> CFP-11 폴리시: workflow의 docs file title에서 `[STORY]` prefix strip (cosmetic, 우선순위 낮음)

본 Story는 그 폴리시 1건 적용.

## 2. 도메인 해석

본 Story는 **workflow auto-output cosmetic polish**. CFP-11 end-to-end 실증에서 발견된 작은 UX 결함 — story.yml form은 title을 자동으로 `[STORY] <input>` 형태로 prefix 부착하지만 workflow가 이를 strip하지 않아 docs h1·PR title에 `[STORY]` 노출.

- 도메인 제약: workflow 정의 변경이라 CLAUDE.md cutoff상 강제 Story (typo 면제 X)
- 암묵 가정: SLUG 계산은 이미 `[STORY]` strip — title_clean도 동일 처리 자연 확장
- 범위 경계: docs h1 + Phase 1 PR title 2 location. 다른 곳(`gh pr create --label`, body 등) 영향 없음
- 우선순위: 낮음 (CFP-11 §11 명시) — sprint 마무리 정합화

지식 공백: 없음.

## 3. 관련 ADR

- **ADR-001/002/003**: 무관
- 신규 ADR 필요 없음

## 4. 관련 코드 경로

| 경로 | 변경 유형 | 변경 후 책임 |
|------|-----------|--------------|
| `.github/workflows/story-init.yml` | 수정 (title_clean output 추가 + 2 location 사용) | docs h1·PR title에서 `[STORY]` strip |
| `templates/github-workflows/story-init.yml` | 동시 수정 (CFP-5 parity) | byte-identical |
| `docs/stories/CFP-15.md` | 신규 | 본 Story file |
| `docs/change-plans/cfp-15-workflow-title-polish.md` | 신규 | 본 Story Change Plan |

## 5. 요구사항 확장 해석

### 유스케이스

1. **Issue Form 제출 시 form이 자동 `[STORY]` prefix 부착**: workflow가 docs h1 / PR title에 prefix 그대로 사용 시 cosmetic 중복
2. **CFP-15 본 Story 자체가 첫 검증 사례**: 본 PR이 merge되고 다음 Story가 Issue Form으로 들어오면 정합 확인 가능

### Acceptance Criteria

- [x] `Compute next story key` step에서 `title_clean` GITHUB_OUTPUT 추가 (slug Python heredoc과 동일 추출 로직 재사용)
- [x] `Create branch + docs/stories/<KEY>.md` step의 h1: `printf '# %s: %s' "$KEY" "$ISSUE_TITLE"` → `"$TITLE_CLEAN"`
- [x] `Create Phase 1 PR` step의 title: `--title "[${KEY}] ${ISSUE_TITLE}"` → `"[${KEY}] ${TITLE_CLEAN}"`
- [x] CFP-5 invariant 준수 — `templates/github-workflows/story-init.yml` 동시 byte-identical
- [x] Local Python heredoc + shell sed extraction 검증 PASS

### 엣지 케이스

- **사용자가 직접 `CFP-N` prefix를 title에 포함** (CFP-11 사례 — 재시도 시 "CFP-11 end-to-end ..."): workflow는 이를 strip 안 함 (user-side issue, workflow가 무엇이 user-typed prefix인지 모름). `[STORY]`만 strip
- **빈 title** (form `validations.required: true`로 차단): edge case 발생 안 함
- **`[STORY]` 외 다른 prefix** (사용자가 임의로 `[BUG] ` 등 추가): 본 변경 scope 외, 향후 form 패턴 확장 시 같이 처리

### §5.5 사용자 확인 필요

- [✓] 사용자 자율 실행 모드 인가 연장
- [✓] CFP-11/14 §11에 명시된 폴리시 후보 채택

## 6. 외부 지식 배경

본 변경은 plugin 내부 workflow polish. 외부 지식 보강 불필요.

## 7. 설계 서사

Change Plan: [`docs/change-plans/cfp-15-workflow-title-polish.md`](../change-plans/cfp-15-workflow-title-polish.md)

### 핵심 설계

**§3 도입할 설계**:
- `Compute next story key` step의 Python heredoc을 2 줄 출력으로 확장 (slug + title_clean)
- shell sed `-n '1p'` / `-n '2p'`으로 두 값 추출 + GITHUB_OUTPUT
- 두 사용 지점 (docs h1, PR title) 모두 `$TITLE_CLEAN` 사용

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "기존 SLUG만 출력하는 단순 구조 유지. title_clean은 별도 Python heredoc으로 분리"
- **Refactor(혁신)**: "title_clean과 slug는 동일 Python re.sub 로직 — 재계산은 중복. 한 heredoc에 두 줄 출력이 자연"
- **채택: Refactor 우세**. 동일 logic 두 번 호출은 코드 중복. shell sed로 두 줄 추출은 표준 idiom.

## 8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta workflow polish**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|------|-------------------|---------------|
| `.github/workflows/story-init.yml` | 수정 | DocsAgent | +12 / -3 | Change Plan §3 |
| `templates/github-workflows/story-init.yml` | 동시 수정 (parity) | DocsAgent | +12 / -3 (byte-identical) | Change Plan §3 |
| `docs/stories/CFP-15.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-15-workflow-title-polish.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## 9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Plugin meta workflow polish.

### §9.3 구현 테스트

**Local 검증 PASS**:
- Python heredoc 2 줄 출력: `slug=CFP-15-폴리시-워크플로우-title-정제` + `title_clean=CFP-15 폴리시 — 워크플로우 title 정제`
- Shell sed extraction: PYOUT 변수 캡처 후 sed `-n '1p'` / `-n '2p'` 정상 추출
- byte-identical parity (CFP-5 invariant): templates ↔ .github/ identical

CI 통합 검증: 본 PR merge 후 다음 Issue Form 제출 시점에 첫 실측 가능.

### §9.4 보안 테스트

**N/A** — workflow polish, attack surface 변경 없음.

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음**.

## 11. 회고

**발견 1 — sprint 마무리 폴리시는 가치 작아도 정합화 ratchet 끝점**: CFP-1~14가 functionality 추가였다면 CFP-15는 cosmetic. 하지만 CFP-11 §11에서 enumerate된 항목을 close하면 "남은 후속 list"가 줄어들어 sprint 종결 인지 명확화.

**발견 2 — workflow GITHUB_OUTPUT multi-value 처리 패턴**: shell sed로 Python heredoc 출력의 N번째 줄 추출 + GITHUB_OUTPUT heredoc 등록. 향후 workflow에서 multi-value output 필요 시 재사용 idiom.

**발견 3 — user-typed prefix는 workflow 책임 외**: CFP-11 사례의 "CFP-11 end-to-end ..." 같은 user-typed key prefix는 workflow가 strip 안 함 (어떤 패턴이 user-typed인지 workflow 모름). `[STORY]`는 form auto-prefix라 strip 명확. 책임 boundary 명시화.

**향후 작업 (별도 Story)**:
- **CFP-16 (잠정)**: severity_overrides parity (string equality 불가, 별도 design 필요)
- **확장 후보**: 사용자가 추가하는 다른 prefix 패턴 (`[BUG]`, `[AUDIT]`) 일관 처리 — bug.yml/audit.yml form도 동일 패턴 적용 시 통합 polish
