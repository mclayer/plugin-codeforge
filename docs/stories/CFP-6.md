# CFP-6: validate_config.py 확장 — story_cutoff 검증 + unknown key reject (CFP-1 invariant 영구 보존)

## §1. 사용자 요구사항 (verbatim)

CFP-5 PR #32 직후 사용자:

> "이어서 진행합시다."

CFP-5 §11 회고에서 명시한 후속 Story:

> CFP-6 (Phase B): validate_config.py에 story_cutoff.additional_exempt_categories 검증 + unknown key reject (Codex 종합 리뷰 P1 #2)

본 Story는 종합 리뷰 P1 4건 중 마지막 미처리 항목.

## §2. 도메인 해석

본 변경의 도메인은 **plugin core 정책 invariant의 schema-level enforcement**. CFP-1이 정책 도입(문서 문구), CFP-6이 validator로 실효 메커니즘 도입.

- 도메인 제약: SessionStart hook이 호출하는 Python validator. consumer overlay 검증의 단일 entry point
- 암묵 가정: SCHEMA_RULES가 single source — `docs/project-config-schema.md` SSOT 와 코드가 정합되어야
- 범위 경계: validate_config.py 확장 + 4 test case. Phase C/D 후속 invariant는 별도 Story
- 우선순위: CFP-1 invariant("강제 항목 축소 불허") enforcement gap 해소

지식 공백: 없음 (Python + PyYAML 표준).

## §3. 관련 ADR

- **ADR-001/ADR-002**: 무관
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `overlay/hooks/validate_config.py` | 수정 | `project.*` · `github.*` · `labels.components` schema 17 rule, unknown key reject 없음 | + `story_cutoff` 2 rule, + `ALLOWED_KEYS_BY_PARENT` auto-derived, + `_check_unknown_keys()` recursive, + `validate()` 끝에서 호출 |
| `docs/stories/CFP-6.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-6-validate-config-story-cutoff.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **Consumer가 `.claude/_overlay/project.yaml`에 도메인 특화 면제 항목 추가**: `story_cutoff.additional_exempt_categories: ["auto-generated migration files"]` → SessionStart에서 validator OK 통과
2. **Consumer가 강제 항목 축소 시도** (악의 또는 실수): `story_cutoff.required_categories: ["P0"]` → unknown key reject로 자동 차단 + error message에 schema 위치 안내
3. **Consumer가 typo로 `github_typo`, `lables.components` 같은 잘못된 키 작성**: unknown key reject로 즉시 발견
4. **Plugin maintainer가 새 필드 추가** (예: `github.bot_account`): SCHEMA_RULES에 추가하면 자동으로 ALLOWED_KEYS_BY_PARENT에 반영 — single source maintenance

### Acceptance Criteria

- 4 test case 모두 PASS:
  - Test 1 (현 plugin overlay): EXIT 0 ✓
  - Test 2 (story_cutoff 확장): EXIT 0 ✓
  - Test 3 (unknown top-level): EXIT 4 + schema 안내 ✓
  - Test 4 (force-shrink 시도): EXIT 4 + allowed list ✓
- error message에 parent path + allowed children list 명시
- `docs/project-config-schema.md` §2 SSOT와 SCHEMA_RULES 정합
- 기존 17 rule 변경 없음 (regression 없음)

### 엣지 케이스

- **Empty `story_cutoff: {}` 또는 `null`**: dict type check 통과 후 자식 검증 — 자식 없으므로 OK (additional_exempt_categories는 선택)
- **Empty list `additional_exempt_categories: []`**: `_is_list_of_str([])` 정의 — 빈 list도 통과 (vacuously true). consumer 명시적 비워두는 의도 가능
- **Recursive nested unknown key**: `github.codeowners.unknown_member` → `_check_unknown_keys`가 모든 nesting level에서 차단

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] CFP-6 작업 진행 결정 ("이어서 진행합시다")
- [✓] CFP-5 §11 회고에 명시된 Phase B scope 그대로 적용
- [✓] Phase C/D는 별도 Story로 분리

## §6. 외부 지식 배경

본 변경은 plugin 내부 schema validator + Python 표준 라이브러리. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: PyYAML + dict traversal 표준 도구. unknown key reject 패턴은 일반적 schema validation idiom (JSON Schema의 additionalProperties: false에 해당). 외부 라이브러리·표준·선행사례 별도 조사 없음.

ADR 정합성: 무관. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-6-validate-config-story-cutoff.md`](../change-plans/cfp-6-validate-config-story-cutoff.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: CFP-1 invariant("강제 항목 축소 불허")의 enforcement gap을 schema validator로 영구 해결.

**§3 도입할 설계**:
- `SCHEMA_RULES`에 `story_cutoff` 2 entry 추가
- `ALLOWED_KEYS_BY_PARENT` SCHEMA_RULES에서 auto-derived (single source)
- `_check_unknown_keys()` recursive function 추가
- `validate()` 끝에 unknown key check 호출
- 4 test case로 동작 검증

**§4 API 계약**: schema validator의 입출력 의미는 그대로. error message 형식 1종 추가 (`unknown key: <path> ...`). exit code 4 (schema violation)에 통합.

**§9 분기 선택**: 단일 PR + 2 commit (validator / Story+Change Plan).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "기존 minimal validator 보존. unknown key reject는 false positive 위험."
- **Refactor(혁신)**: "CFP-1 invariant는 문서 문구만으론 violation 차단 불가. unknown key reject가 anti-shrink 자동화의 유일한 실효 메커니즘."
- **채택: Refactor 우세**. Mapper 우려는 명확한 error message + schema reference 안내로 흡수. 새 field 추가 시 SCHEMA_RULES 갱신이 자연스러운 patten — false positive 위험 minimal.

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta script 확장, 코드 산출물 없음**.

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `overlay/hooks/validate_config.py` | 수정 | DocsAgent | +30 / -1 (SCHEMA_RULES 2 entries + ALLOWED_KEYS_BY_PARENT helper + `_check_unknown_keys` + `validate()` 호출) | Change Plan §3.2-3.4 |
| `docs/stories/CFP-6.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-6-validate-config-story-cutoff.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음.

### §9.1 설계 리뷰

**N/A** — Codex 종합 리뷰 P1 #2가 본 변경의 발견 source. PR review에서 정합성 추가 확인.

### §9.2 구현 리뷰

**N/A** — 30줄 Python 확장. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**Local 4 test case 결과 (실제 validator 호출):**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin overlay (story_cutoff 부재) | EXIT 0 | EXIT 0 ✓ |
| 2 | story_cutoff.additional_exempt_categories: [...] | EXIT 0 | EXIT 0 ✓ |
| 3 | extra_top_level + github_typo (unknown top-level) | EXIT 4 + 2 errors | EXIT 4 + 2 errors with schema reference ✓ |
| 4 | story_cutoff.required_categories + remove_force_categories | EXIT 4 + 2 errors | EXIT 4 + 2 errors with allowed list ✓ |

기존 17 rule 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local validator script, attack surface 변경 없음. PyYAML safe_load 사용 (이미 적용됨).

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## §11. 참조

- **GitHub Issue URL**: 부재 (Issue Form 미사용 — CFP-7 잠정 end-to-end 실증 예정)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base**: main
- **Change Plan**: [`docs/change-plans/cfp-6-validate-config-story-cutoff.md`](../change-plans/cfp-6-validate-config-story-cutoff.md)
- **CFP-1 Story**: [`docs/stories/CFP-1.md`](CFP-1.md) — Self-application 정책 (강제 6항목 + 면제 4항목 + 강제 축소 불허 invariant)
- **CFP-5 Story**: [`docs/stories/CFP-5.md`](CFP-5.md) — Phase A invariant 자동화 첫 도입
- **관련 ADR**: 없음

### 회고

**발견 1 — Schema가 invariant의 진짜 SSOT**: CFP-1 정책 문구로는 "강제 축소 불허"가 enforce 안 됨. 실제 SSOT는 `SCHEMA_RULES` 코드. 문서가 invariant의 *서술*이라면 schema는 invariant의 *실체*. CFP-6이 둘을 정합하는 첫 사례.

**발견 2 — Unknown key reject = anti-shrink의 유일한 실효 메커니즘**: 강제 축소 시도(예: `required_categories` 키)를 schema에 정의하지 않으면 unknown key reject가 자동으로 차단. **금지 항목을 enumerate할 필요 없이, 허용 항목만 enumerate하면 충분**한 안전 모델. JSON Schema `additionalProperties: false` idiom과 동일.

**발견 3 — Codex 종합 리뷰 P1 4건 모두 처리 완료**: P1 #1 (CFP-4 story-init.yml sync) ✓, P1 #2 (CFP-6 본 Story) ✓, P1 #3 (CFP-4 CLAUDE.md stage 정정) ✓, P1 #4 (CFP-4 plugin.json 메타) ✓. 종합 리뷰가 발견한 critical drift는 모두 main 또는 PR queue에 처리. 자동화 layer (CFP-5/6) + 정합 chore (CFP-4) + 처리 close (CFP-3) 패턴 완성.

**향후 작업 (별도 Story)**:
- **CFP-7 (Phase C-1)**: frontmatter `permissions.allow` ↔ CLAUDE.md "Write queue 의뢰 권한" 표 정합 — Python regex parser 필요, 복잡도 높음
- **CFP-8 (Phase C-2)**: ADR-002 footer SSOT 참조 1줄 패턴 검증 (모든 agent md "## 문서화 표준" 섹션) — Python regex로 footer 본문 정합 검증
- **CFP-9 (Phase C-3)**: `code.md` `dup-local: P1` SSOT enum 정합 (PR #26 audit P0 #4 invariant)
- **CFP-10 (Phase D)**: `docs/migration-guide.md` v0.X→v0.Y 섹션 ↔ `CHANGELOG.md` 최상단 BREAKING 정합
- **CFP-11 (잠정 end-to-end)**: 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → 모든 workflow 자동 동작 첫 실증
- **ADR-003 (조건부)**: invariant 자동화 Phase B/C/D 격상 patten 정량 trigger
