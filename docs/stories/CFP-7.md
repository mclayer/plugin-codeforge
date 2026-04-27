# CFP-7: invariant-check.yml Step 4 — frontmatter ↔ CLAUDE.md "Write queue 의뢰 권한" 표 정합 (Phase C-1)

## §1. 사용자 요구사항 (verbatim)

CFP-6 PR #33 직후 사용자:

> "이어서 진행합시다."

CFP-6 §11 회고에 명시된 후속 Story:

> CFP-7 (Phase C-1): frontmatter `permissions.allow` ↔ CLAUDE.md "Write queue 의뢰 권한" 표 정합 — Python regex parser 필요

본 Story는 Phase C(복합 검증) 첫 항목.

## §2. 도메인 해석

본 변경의 도메인은 **plugin agent permission SSOT의 양방향 정합 자동 검증**. CLAUDE.md narrative와 frontmatter machine-readable spec 사이의 drift는 이전엔 audit으로만 잡히던 영역.

- 도메인 제약: 15개 에이전트가 write queue 의뢰 권한을 가짐 (DocsAgent는 single writer로 별도)
- 암묵 가정: CLAUDE.md "Write queue 의뢰 권한" 표 + agents/*.md frontmatter `permissions.allow`가 양방향 SSOT mirror여야 함
- 범위 경계: invariant-check.yml에 Step 4 추가 + Python regex parser. 다른 frontmatter 필드(`Bash` wrappers 등) 정합은 별도 Story
- 우선순위: Phase B(CFP-6 schema validator) 다음 단계 — narrative ↔ machine-readable parity

지식 공백: 없음 (Python regex + frontmatter parsing 표준).

## §3. 관련 ADR

- **ADR-001/ADR-002**: 무관
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 수정 | 3 step (workflow parity / version / agent count) | + Step 4 (write queue permission parity, Python parser) |
| `docs/stories/CFP-7.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-7-write-queue-permission-parity.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **새 에이전트가 write queue를 사용**: PR에서 frontmatter에 `Edit/Write(.claude-work/doc-queue/**)` 추가 시 CLAUDE.md 표에 동기 추가 안 하면 invariant-check FAIL → 수정 강제
2. **CLAUDE.md 표에서 누락**: 표에 listed인데 frontmatter에 권한 누락 → drift detect
3. **비대칭 권한**: Edit만 또는 Write만 frontmatter에 있음 → 의도 불명, 양쪽 모두 또는 양쪽 모두 부재여야
4. **Shorthand 표기**: 표는 PL suffix (`DesignReviewPL`) / Agent suffix 생략 (`Refactor`) 등 7종 shorthand 사용 — 매핑 테이블로 흡수

### Acceptance Criteria

- 4 test case 모두 PASS:
  - Test 1: 현 plugin (15 listed + DocsAgent) → OK
  - Test 2: agent에서 권한 완전 누락 → drift detect ("listed but 부재")
  - Test 3: 표에 없는 agent가 권한 보유 → drift detect ("frontmatter 있음 but 표 부재")
  - Test 4: 비대칭 (Edit만) → drift detect ("Edit/Write 비대칭")
- DocsAgent는 single writer로 표 면제 (EXEMPT_FROM_TABLE에 명시)
- 7 shorthand 매핑 (CodebaseMapper, Refactor, RequirementsAnalyst, Researcher, DesignReviewPL, CodeReviewPL, SecurityTestPL)
- error message에 drift 종류 + agent 이름 명시

### 엣지 케이스

- **Frontmatter 부재 agent**: `re.match(r"^---\n(.*?)\n---", ...)` 실패 시 skip (continue) — 정합 검사 대상 아님
- **표 라인 부재**: `'Write queue 의뢰 권한' 표 라인 부재` 에러 + exit 1 (CLAUDE.md 자체 변조 방어)
- **Partial + missing 동시 분류 회피**: partial로 보고된 agent는 "listed but missing" 재보고 안 함

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] CFP-7 작업 진행 결정 ("이어서 진행합시다")
- [✓] CFP-6 §11 회고에 명시된 Phase C-1 scope 그대로 적용
- [✓] DocsAgent 표 면제 정책 (single writer 역할 → EXEMPT_FROM_TABLE 명시)

## §6. 외부 지식 배경

본 변경은 plugin 내부 invariant-check workflow + Python 표준 라이브러리. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: regex + dict 매핑 표준 도구. YAML frontmatter 파싱은 첫 두 `---` 사이 raw text 추출로 충분 (PyYAML 의존 회피). 외부 라이브러리·표준·선행사례 별도 조사 없음.

ADR 정합성: 무관. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-7-write-queue-permission-parity.md`](../change-plans/cfp-7-write-queue-permission-parity.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: CFP-6 schema-level enforcement에 이어 narrative ↔ machine-readable mirror 정합 검증.

**§3 도입할 설계**:
- Python parser (50줄)로 CLAUDE.md 표 1줄 추출 (`re.search` "Write queue 의뢰 권한" → "기타")
- 7 SHORTHAND 매핑으로 표 표기 → 실제 파일명 정규화
- agents/*.md frontmatter (`^---\n(.*?)\n---`) 추출 후 `Edit/Write(.claude-work/doc-queue/**)` 정규식 검출
- 3종 drift 분류: partial / listed-but-missing / unlisted-but-present
- DocsAgent EXEMPT_FROM_TABLE (single writer 별도 역할)

**§4 API 계약**: invariant-check workflow Step 추가 1종. exit 0 / exit 1 (drift 발견). error annotation은 GitHub Actions native (`::error file=...::msg`).

**§9 분기 선택**: 단일 PR + 2 commit (workflow / Story+Change Plan).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "현 invariant-check.yml은 shell 기반. Python 도입은 의존성 증가."
- **Refactor(혁신)**: "frontmatter parsing은 shell로 충분히 어려움. Python 표준 라이브러리만 사용 (PyYAML 회피) → ubuntu-latest runner default 의존만."
- **채택: Refactor 우세**. shell 기반 frontmatter parsing은 awk/sed 복잡도 폭증. Python 표준 도구 의존만으로 50줄에 의도 명료. Mapper 우려는 PyYAML 미사용으로 흡수 (frontmatter raw text regex만).

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta workflow 확장, 코드 산출물 없음**.

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `.github/workflows/invariant-check.yml` | 수정 | DocsAgent | +90 / -3 (Step 4 Python parser) | Change Plan §3 |
| `docs/stories/CFP-7.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-7-write-queue-permission-parity.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음.

### §9.1 설계 리뷰

**N/A** — Phase C-1 scope는 CFP-6 §11에 명시. Self-application meta script.

### §9.2 구현 리뷰

**N/A** — 90줄 Python parser. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**Local 4 test case 결과 (실제 parser 호출):**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin (15 listed + DocsAgent) | OK | OK ✓ |
| 2 | PMOAgent에서 doc-queue Edit/Write 둘 다 제거 | "PMOAgent: listed but 부재" | matched ✓ |
| 3 | DeveloperAgent frontmatter에 doc-queue 추가 | "DeveloperAgent: frontmatter 있음 but 표 부재" | matched ✓ |
| 4 | PMOAgent에서 Write만 제거 (Edit 보존) | "PMOAgent: 비대칭 Edit=True Write=False" (1건만, listed-missing 중복 보고 X) | matched ✓ |

기존 3 step (workflow parity / version / agent count) 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local Python parser, attack surface 변경 없음. CLAUDE.md/agents/*.md read-only.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

단, 구현 중 SHORTHAND 매핑 부족(3개) 발견 → local test로 즉시 보완 (Test 1에서 `DesignReviewPL/CodeReviewPL/SecurityTestPL` shorthand 발견). 전형적 self-discovery 패턴.

## §11. 참조

- **GitHub Issue URL**: 부재 (Issue Forms 미사용 — CFP-11 잠정 end-to-end 실증 예정)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base**: main
- **Change Plan**: [`docs/change-plans/cfp-7-write-queue-permission-parity.md`](../change-plans/cfp-7-write-queue-permission-parity.md)
- **CFP-5 Story**: [`docs/stories/CFP-5.md`](CFP-5.md) — Phase A 자동화 첫 도입 (mechanical invariant)
- **CFP-6 Story**: [`docs/stories/CFP-6.md`](CFP-6.md) — Phase B schema-level enforcement
- **관련 ADR**: 없음

### 회고

**발견 1 — Shorthand 매핑은 첫 실행에서야 드러난다**: CLAUDE.md 작성 당시 4 shorthand만 인지 (CodebaseMapper, Refactor, RequirementsAnalyst, Researcher). PL suffix 3종(DesignReviewPL/CodeReviewPL/SecurityTestPL)은 parser 첫 실행에서야 발견. invariant 자동화의 부수 효과 — narrative 작성 시 무의식 shorthand가 machine-readable parity 시점에 드러남.

**발견 2 — DocsAgent EXEMPT는 본질적 정책 결정**: DocsAgent도 doc-queue 권한을 가지지만 "의뢰 권한"이 아닌 "drain 주체". CLAUDE.md 표에 listed 안 함 — 역할 차이의 narrative SSOT 표명. EXEMPT_FROM_TABLE 한 줄 코드가 이 역할 차이를 machine-readable로 박제.

**발견 3 — Phase C도 단일 step Python으로 충분**: Phase C는 "Python regex parser 필요, 복잡도 높음"으로 분류됐으나 실제 90줄 한 step에 들어감. Phase C-2/C-3/D도 비슷한 규모 가능성 — 단계 격상보다 invariant-check.yml 한 step 추가 패턴이 자연스러움.

**향후 작업 (별도 Story)**:
- **CFP-8 (Phase C-2)**: ADR-002 footer SSOT 참조 1줄 패턴 검증 (모든 agent md "## 문서화 표준" 섹션) — Python regex로 footer 본문 정합 검증
- **CFP-9 (Phase C-3)**: `code.md` `dup-local: P1` SSOT enum 정합 (PR #26 audit P0 #4 invariant)
- **CFP-10 (Phase D)**: `docs/migration-guide.md` v0.X→v0.Y 섹션 ↔ `CHANGELOG.md` 최상단 BREAKING 정합
- **CFP-11 (잠정 end-to-end)**: 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → 모든 workflow 자동 동작 첫 실증
- **ADR-003 (조건부)**: invariant 자동화 Phase B/C/D 격상 patten 정량 trigger
