# CFP-10: invariant-check.yml Step 7 — Migration-guide ↔ CHANGELOG BREAKING 정합 (Phase D)

## §1. 사용자 요구사항 (verbatim)

CFP-9 PR #37 머지 직후 사용자 (autonomy mode):

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해" (CFP-8/9 진행 중 부여, 본 Story도 그 연장)

CFP-9 §11 회고에 명시된 Phase D:

> CFP-10 (Phase D): `docs/migration-guide.md` v0.X→v0.Y 섹션 ↔ `CHANGELOG.md` 최상단 BREAKING 정합

## §2. 도메인 해석

본 변경의 도메인은 **release artifact의 cross-document 정합**. CHANGELOG와 migration-guide는 buyer-facing artifact로 별도 audience를 가지지만, BREAKING change에 대한 instruction은 양 문서가 일관해야 함.

- 도메인 제약: CHANGELOG의 모든 BREAKING release는 migration-guide에 대응 섹션 보유
- 암묵 가정: migration-guide는 superset 가능 (non-BREAKING 섹션도 문서화 가치). 역방향(migration → CHANGELOG)은 강제 안 함
- 범위 경계: Step 7 추가 + major.minor 단위 매칭. patch 버전(X.Y.Z의 Z>0) BREAKING도 to-version major.minor 단위로 매칭
- 우선순위: consumer가 plugin upgrade 시 migration 절차를 못 찾는 사고 방지 (CHANGELOG에는 BREAKING 표시지만 migration-guide에 절차 누락 case)

지식 공백: 없음 (CHANGELOG/migration-guide 패턴 사실적 분석 + Korean emdash 처리).

## §3. 관련 ADR

- **ADR-001**: 0.9 BREAKING의 motivation이지만 본 변경 design과 무관
- **ADR-002**: 무관
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 수정 | 6 step (CFP-5/7/8/9) | + Step 7 (migration-guide BREAKING parity) |
| `docs/stories/CFP-10.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-10-migration-changelog-parity.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **새 BREAKING 릴리즈 작성 시 migration-guide 빠뜨림**: CHANGELOG에 `## [X.Y.Z] (BREAKING ...)` 추가했는데 migration-guide에 `## v? → vX.Y` 섹션 없으면 invariant-check FAIL → release block
2. **patch BREAKING (X.Y.Z, Z>0)**: major.minor 단위로 to-version 매칭 — patch 단위 별도 섹션은 일반적으로 필요 없으나 X.Y에 1개 섹션이라도 있으면 통과
3. **non-BREAKING 섹션도 migration-guide에 문서화** (예: v0.6→v0.7 요구사항·설계 레인 병렬화): superset 허용, 강제 차단 안 함
4. **BREAKING 부재**: BREAKING 버전이 1건도 없으면 step skip + ✓ 출력 (vacuous truth)

### Acceptance Criteria

- 4 test case 모두 PASS:
  - Test 1: 현 plugin (BREAKING 2건 = 0.8.0/0.9.0, 둘 다 migration-guide 섹션 보유) → exit 0
  - Test 2: 가상 v1.0.0 BREAKING 추가 (migration-guide 미작성) → "v1.0.0 BREAKING but migration-guide v?→v1.0 섹션 부재"
  - Test 3: migration-guide에서 v0.7→v0.8 섹션 제거 → "v0.8.0 BREAKING but ... 부재"
  - Test 4: CHANGELOG에서 모든 BREAKING 단어 제거 → "BREAKING 버전 없음 (skip)" + exit 0

### 엣지 케이스

- **Korean emdash `→` 사용**: migration-guide는 emdash → 사용. regex `[→\-]+>?` 으로 dash와 emdash 모두 허용
- **CHANGELOG에 `## [X.Y.Z]` 헤더는 있는데 BREAKING 단어 없음**: non-BREAKING으로 분류 — 강제 안 함
- **major.minor 매칭 strategy**: patch BREAKING도 major.minor 단위로 매칭. 이론상 v0.9.1 BREAKING이 있으면 v0.8→v0.9 섹션이 cover (major.minor 같으므로)

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] CFP-9 §11 회고에 명시된 Phase D scope 그대로 적용
- [✓] 사용자 자율 실행 모드 인가 (CFP-8 시점)
- [✓] superset 허용 정책 (migration-guide의 non-BREAKING 섹션은 강제 안 함)

## §6. 외부 지식 배경

본 변경은 plugin 내부 release artifact 정합 자동화. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: regex 표준 도구. SemVer 패턴은 plugin 내부 SSOT 위치 한정.

ADR 정합성: ADR-001 BREAKING의 motivation이지만 design과 무관. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-10-migration-changelog-parity.md`](../change-plans/cfp-10-migration-changelog-parity.md)

### 핵심 설계

**§3 도입할 설계**:
- CHANGELOG.md의 `## [X.Y.Z] ... (BREAKING` 패턴 추출 (multiline regex)
- migration-guide.md의 `## vA.B → vC.D` 패턴 추출 (Korean emdash + dash 모두 허용)
- BREAKING의 to-version major.minor가 migration-guide section to-version과 매칭 검증
- 역방향(migration → CHANGELOG) 강제 안 함 — superset 허용

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "CHANGELOG와 migration-guide는 release process 일부. CI invariant보다 release checklist에 두는 게 적합."
- **Refactor(혁신)**: "release checklist는 사람의 주의 의존. CHANGELOG에 BREAKING 적었는데 migration-guide 작성을 잊는 게 가장 빈번한 release 사고 패턴 (consumer 입장에서 'BREAKING이라는데 어떻게 마이그레이션?' 막힘)."
- **채택: Refactor 우세**. Phase A~C 동일 패턴 — narrative SSOT (CHANGELOG·migration-guide 병행) ↔ machine-readable parity. PR-level invariant로 release 사고 사전 차단이 가장 실용적.

## §8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta workflow 확장**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `.github/workflows/invariant-check.yml` | 수정 | DocsAgent | +70 / -3 (Step 7 + header) | Change Plan §3 |
| `docs/stories/CFP-10.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-10-migration-changelog-parity.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Phase D scope는 CFP-9 §11에 명시. Plugin meta workflow 확장.

### §9.3 구현 테스트

**Local 4 test case 결과 (실제 parser 호출):**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin (BREAKING 2건, 둘 다 migration-guide section 보유) | OK (2 matched) | OK ✓ |
| 2 | CHANGELOG에 v1.0.0 BREAKING 추가 (migration-guide 미작성) | "v1.0.0 BREAKING but ... 부재" 1건 | matched ✓ |
| 3 | migration-guide에서 v0.7→v0.8 제거 | "v0.8.0 BREAKING but ... 부재" 1건 | matched ✓ |
| 4 | CHANGELOG의 BREAKING 단어 모두 제거 | "BREAKING 버전 없음 (skip)" + exit 0 | matched ✓ |

기존 Step 1-6 (CFP-5/7/8/9) 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local Python parser, attack surface 변경 없음.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**. CFP-7~9 self-discovery 패턴(SHORTHAND / path 오타 / Codex anchor)이 발견되지 않음 — Phase D는 단순 cross-doc 매칭이라 자체 발견 사항 없음.

## §11. 참조

- **GitHub Issue URL**: 부재 (Issue Forms 미사용 — CFP-11 잠정 end-to-end 실증 예정)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base**: main
- **Change Plan**: [`docs/change-plans/cfp-10-migration-changelog-parity.md`](../change-plans/cfp-10-migration-changelog-parity.md)
- **CFP-9 Story**: [`docs/stories/CFP-9.md`](CFP-9.md) — Phase C-3 code category enum
- **관련 ADR**: 없음

### 회고

**발견 1 — Phase D는 단순 cross-doc 매칭이라 self-discovery 패턴 부재**: CFP-7 (SHORTHAND), CFP-8 (path 오타), CFP-9 (Codex anchor)는 모두 첫 구현 시 self-discovery 발견. Phase D는 CHANGELOG 패턴이 명료하고 migration-guide section heading도 일관해서 첫 구현으로 통과. invariant 자동화 작업의 self-discovery rate는 SSOT의 narrative 표현 다양성에 비례.

**발견 2 — superset 허용은 release process 자율성 보존**: 강제 양방향 매칭이면 non-BREAKING migration 섹션도 강제 — release-note 작성자의 자유도 침해. 실제 release 사고 패턴은 항상 "BREAKING적었는데 migration 누락" 방향이라 단방향 강제로 충분.

**발견 3 — Phase A~D 7 invariant 모두 단일 Workflow 한 step씩 수렴**: CFP-5 (3 step), CFP-6 (validate_config), CFP-7~10 (각 1 step). 모든 Phase가 invariant-check.yml에 step 추가 패턴으로 통일. 향후 Phase E/F가 도입되더라도 동일 ratchet 가능.

**향후 작업 (별도 Story)**:
- **CFP-11 (잠정 end-to-end)**: 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → 모든 workflow 자동 동작 첫 실증
- **ADR-003 (조건부)**: invariant 자동화 Phase 격상 patten 정량 trigger
- **확장 후보**: lane=design/security category enum (CFP-9의 lane=code 외 확장), severity_overrides parity 등
