# CFP-8: invariant-check.yml Step 5 — ADR-002 footer SSOT 참조 1줄 패턴 검증 (Phase C-2)

## §1. 사용자 요구사항 (verbatim)

CFP-7 PR #35 머지 직후 사용자:

> "이어서 진행합시다."

CFP-7 §11 회고에 명시된 Phase C-2:

> CFP-8 (Phase C-2): ADR-002 footer SSOT 참조 1줄 패턴 검증 (모든 agent md "## 문서화 표준" 섹션) — Python regex로 footer 본문 정합 검증

본 Story는 Phase C 두 번째 항목.

## §2. 도메인 해석

본 변경의 도메인은 **ADR-002 결정의 자동 enforcement**. ADR-002는 "DocsAgent.md SSOT 참조 1줄만 유지" + "footer 본문 확장 금지"를 명시했으나 정합 검증은 사람의 PR review 의존이었음.

- 도메인 제약: 21개 agent md(DocsAgent 제외 19개 + presets/webapp/agents 2개)가 "## 문서화 표준" 섹션 보유
- 암묵 가정: footer body는 1줄, DocsAgent.md 참조 link 정확한 상대 경로, SSOT 본문 inline 복제 금지
- 범위 경계: invariant-check.yml에 Step 5 추가. 발견된 ADR-002 §3 path example 오타도 동시 수정
- 우선순위: ADR-002 결정의 enforcement gap — Phase C-1과 동일한 narrative ↔ machine-readable mirror 패턴

지식 공백: 없음 (ADR-002 §3 + agent md footer 사실적 패턴 분석으로 form 3종 식별).

## §3. 관련 ADR

- **ADR-001**: 무관
- **ADR-002**: 본 Story가 enforce 대상. 단 ADR-002 자체 결정 변경은 없고 §3.2 path example 오타만 정정 (3 levels up 경로). 이는 ADR 결정 변경이 아닌 documentation fix
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 수정 | 4 step (CFP-5/7) | + Step 5 (ADR-002 footer pattern, Python parser) |
| `docs/adr/ADR-002-docsagent-inherit-footer-pattern.md` | 수정 | §3.2에 `../../agents/...` (잘못된 경로 — 실제는 `presets/agents/`로 향함) | `../../../agents/...` 정정 |
| `docs/stories/CFP-8.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-8-adr-002-footer-parity.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **새 에이전트 추가 시 footer 누락**: PR이 invariant-check Step 5 FAIL → "## 문서화 표준 섹션 부재" 안내
2. **footer body에 SSOT 본문 inline 복제 시도**: "phase prefix 11종 + ..." 같은 SSOT 본문 키워드 → drift 위험으로 차단
3. **presets/<flavor>/agents/X.md에 잘못된 상대 경로 사용** (ADR-002 §3.2 오타 따라 `../../agents/...`): link target mismatch로 차단
4. **footer body 다줄 확장 시도** ("권한 deny + queue 안내" 두 줄로 분리 등): "1줄 아님" drift detect

### Acceptance Criteria

- 4 test case 모두 PASS:
  - Test 1: 현 plugin (21 agent md) → exit 0
  - Test 2: DeveloperAgent에서 "## 문서화 표준" 섹션 완전 제거 → "섹션 부재" detect
  - Test 3: ArchitectAgent body에 `phase prefix` keyword 삽입 → "금지 keyword" detect
  - Test 4: presets/webapp/agents/Backend...에 `../../agents/...` 잘못된 경로 → "link target 불일치" detect
- ADR-002 §3.2 path example 오타 (`../../` → `../../../`) 정정
- 4 SSOT 본문 inline 복제 금지 keyword: "phase prefix", "Story file 섹션", "FIX Ledger 스키마", "Impl Manifest 스키마"
- 위치별 expected link target 매핑:
  - `agents/<X>.md` → `DocsAgent.md`
  - `presets/<flavor>/agents/<X>.md` → `../../../agents/DocsAgent.md`

### 엣지 케이스

- **DocsAgent.md**: scope 외 (SSOT 본체 — footer 부재가 정상)
- **빈 body or whitespace only**: `body_lines == []` → "1줄 아님 (0 줄)" detect
- **다른 location의 agent md** (예: 미래 `presets/cli/agents/`): expected_link_target에 분기 추가 필요. 현재 webapp만 있으므로 미래 확장 시 처리

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] CFP-8 작업 진행 결정 ("이어서 진행합시다")
- [✓] CFP-7 §11 회고에 명시된 Phase C-2 scope 그대로 적용
- [✓] ADR-002 §3.2 path example 오타 동시 수정 (별도 PR 분리 안 함 — invariant 자동화의 enforce target 자체가 잘못된 example 포함했으므로 함께 수정이 자연스러움)

## §6. 외부 지식 배경

본 변경은 plugin 내부 invariant-check workflow + Python 표준 라이브러리. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: regex + pathlib 표준 도구. ADR-002 §3은 form 종류와 path 규칙 명시 — 외부 표준 referencing 없음. footer pattern은 ADR-002 자체 SSOT.

ADR 정합성: ADR-002 본 결정 변경 없음 (path example 오타 정정만). 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-8-adr-002-footer-parity.md`](../change-plans/cfp-8-adr-002-footer-parity.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: ADR-002 §3 결정 ("footer 본문 확장 금지" + "exact-copy invariant") 자동 enforcement.

**§3 도입할 설계**:
- Python parser ~100줄로 21 agent md 순회
- 위치별 `expected_link_target()` 함수로 상대 경로 매핑
- 4 SSOT 본문 inline 복제 금지 keyword list
- 3종 drift 분류: section 부재 / body 다줄 / link target 불일치 / 금지 keyword 포함

**§4 API 계약**: invariant-check workflow Step 추가 1종. exit 0 / exit 1.

**§9 분기 선택**: 단일 PR + 2 commit (workflow + ADR-002 fix / Story+Change Plan).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "ADR-002 §3 'CodeReview 강제 항목'은 PR review에 위임. 자동화는 over-engineering."
- **Refactor(혁신)**: "PR review는 사람의 주의 의존. ADR-002 enforcement gap = 21 사본 footer가 한 번에 drift할 위험. 자동 검증이 ADR 결정의 진짜 SSOT."
- **채택: Refactor 우세**. CFP-1~CFP-7 패턴과 동일 — narrative SSOT (ADR-002 결정) ↔ machine-readable enforcement (invariant-check Step 5) mirror 정합. Mapper 우려는 Python 100줄 + 4 keyword list로 흡수.

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta workflow 확장**.

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `.github/workflows/invariant-check.yml` | 수정 | DocsAgent | +106 / -3 (Step 5 + header) | Change Plan §3 |
| `docs/adr/ADR-002-docsagent-inherit-footer-pattern.md` | 수정 | DocsAgent | +1 / -1 (path example 오타) | Change Plan §2.4 |
| `docs/stories/CFP-8.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-8-adr-002-footer-parity.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음.

### §9.1 설계 리뷰

**N/A** — Phase C-2 scope는 CFP-7 §11에 명시.

### §9.2 구현 리뷰

**N/A** — 100줄 Python parser. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**Local 4 test case 결과 (실제 parser 호출):**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin (21 agent md, DocsAgent 제외) | OK | OK ✓ |
| 2 | DeveloperAgent의 "## 문서화 표준" 섹션 제거 | "섹션 부재" 1건 | matched ✓ |
| 3 | ArchitectAgent body에 "phase prefix" keyword 삽입 | "금지 keyword 'phase prefix'" 1건 | matched ✓ |
| 4 | presets/webapp/agents/Backend...에 `../../agents/...` (3 → 2 levels) | "link target 불일치" 1건 | matched ✓ |

기존 Step 1-4 (CFP-5/7) 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local Python parser, attack surface 변경 없음.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

단, 구현 중 ADR-002 §3.2 path example 오타 발견 (3 levels up이 정합인데 2 levels up으로 적혀있음) → 같은 PR에 fix 포함. self-discovery 패턴.

## §11. 참조

- **GitHub Issue URL**: 부재 (Issue Forms 미사용 — CFP-11 잠정 end-to-end 실증 예정)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base**: main
- **Change Plan**: [`docs/change-plans/cfp-8-adr-002-footer-parity.md`](../change-plans/cfp-8-adr-002-footer-parity.md)
- **CFP-7 Story**: [`docs/stories/CFP-7.md`](CFP-7.md) — Phase C-1 frontmatter ↔ CLAUDE.md 표
- **관련 ADR**: [ADR-002](../adr/ADR-002-docsagent-inherit-footer-pattern.md) — 본 invariant의 narrative SSOT

### 회고

**발견 1 — invariant 자동화는 narrative SSOT 자체의 오타도 폭로**: ADR-002 §3.2 example의 `../../agents/...` 경로는 작성 당시 정확한지 검증 안 됨. CFP-8 parser 구현 중 expected target 계산하다가 즉시 발견. invariant 자동화의 부수 효과 — 표 기반 narrative 안에 숨은 fact-error도 Python으로 박제될 때 드러남.

**발견 2 — ADR-002 §3 form 3종 + presets 변형 = 4종 footer**: 사람이 작성한 narrative SSOT는 form 3종(minimal / extended / queue-enabled)을 enumerate했지만 실제로는 위치별 path 변형까지 포함해 4종. parser는 link target 검증으로 모두 흡수.

**발견 3 — CFP-7과 본 Story는 narrative ↔ machine-readable parity 동일 패턴**: CFP-7 = CLAUDE.md 표 ↔ frontmatter, CFP-8 = ADR-002 §3 ↔ 21 agent footer. 둘 다 Python ~100줄로 단일 step 내 처리. Phase C가 "복잡도 높음"으로 분류됐지만 실제로는 Phase A/B와 비슷한 ratio. CFP-9/CFP-10도 비슷할 가능성.

**향후 작업 (별도 Story)**:
- **CFP-9 (Phase C-3)**: `code.md` `dup-local: P1` SSOT enum 정합 (PR #26 audit P0 #4 invariant)
- **CFP-10 (Phase D)**: `docs/migration-guide.md` v0.X→v0.Y 섹션 ↔ `CHANGELOG.md` 최상단 BREAKING 정합
- **CFP-11 (잠정 end-to-end)**: 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → 모든 workflow 자동 동작 첫 실증
- **ADR-003 (조건부)**: invariant 자동화 Phase B/C/D 격상 patten 정량 trigger
