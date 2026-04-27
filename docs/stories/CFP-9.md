# CFP-9: invariant-check.yml Step 6 — Code review category enum 3 location 정합 (Phase C-3)

## §1. 사용자 요구사항 (verbatim)

CFP-8 PR #36 머지 직후 사용자:

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해"

CFP-8 §11 회고에 명시된 Phase C-3:

> CFP-9 (Phase C-3): `code.md` `dup-local: P1` SSOT enum 정합 (PR #26 audit P0 #4 invariant)

본 Story는 Phase C 마지막 항목.

## §2. 도메인 해석

본 변경의 도메인은 **review category enum의 3 location 정합**. SSOT는 `templates/review-checklists/code.md` line 14 (10 categories pipe-separated)이고, 이 enum은 `CodeReviewPLAgent.md` packet YAML과 `CodexReviewAgent.md` lane=code 프롬프트에 mirror되어야 함.

- 도메인 제약: 3 location의 enum이 동일 categories + 동일 순서 (단순 set 같음 X — 순서까지)
- 암묵 가정: SSOT 변경 시 다른 2 위치도 sync 강제. drift 발견 시 즉시 차단
- 범위 경계: Step 6 추가. severity_overrides나 lane=design/security enum은 별도 invariant (향후 확장 후보)
- 우선순위: PR #26 audit P0 #4 — `dup-local: P1` 분류는 1차 가정 "구현"이라는 origin 판정의 핵심. enum drift 시 review FIX 카운터 정책이 무력화 위험

지식 공백: 없음 (3 location의 패턴 사실적 분석으로 regex 도출).

## §3. 관련 ADR

- **ADR-001**: 무관 (review 워커 통합 ADR — 본 변경은 carrier가 아닌 enum data 정합)
- **ADR-002**: 무관
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 수정 | 5 step (CFP-5/7/8) | + Step 6 (code category enum parity, Python parser) |
| `docs/stories/CFP-9.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-9-code-category-enum-parity.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **새 category 추가** (예: `flaky-test`): `templates/review-checklists/code.md` line 14에만 추가하면 invariant-check FAIL → PL/Codex 동시 갱신 강제
2. **PL packet에서 category 누락** (refactor 중 실수): drift detect로 PR review에서 즉시 발견
3. **Codex 프롬프트 순서 변경**: 동일 set이어도 순서 다르면 drift detect (LLM 출력 일관성 유지)
4. **CodexReviewAgent.md lane=design/security 영향 격리**: lane=code anchor regex로 다른 lane enum 무시

### Acceptance Criteria

- 4 test case 모두 PASS:
  - Test 1: 현 plugin (10 categories x 3 location) → exit 0
  - Test 2: SSOT에 `new-cat` 추가 → PL/Codex 둘 다 drift detect
  - Test 3: PL list에서 `dead-code` 제거 → drift detect
  - Test 4: Codex 순서 변경 (`runtime-bug` ↔ `layer-violation`) → drift detect (set 같음에도 순서 차이로 fail)
- 3 location 추출 패턴:
  - SSOT: `` `runtime-bug | layer-violation | ... | dup-boundary` `` pipe-separated inline code
  - PL: `category_enum:` YAML list
  - Codex: `#### lane=code` heading 이후 `category from {...}` (lane=design/security와 격리)
- diff 보고: SSOT - location 차집합 + location - SSOT 차집합 (drift 위치 명확화)

### 엣지 케이스

- **3 location 모두 동일하지만 다른 순서**: drift로 분류 (LLM 일관성 + reviewer cognitive load)
- **빈 SSOT enum** (`code.md` line 14 누락): "pipe-separated category enum 부재" 에러 + exit 1
- **CodexReviewAgent.md 구조 변경 시** (예: lane heading 이름 변경): regex 매칭 실패 → 즉시 차단 (false positive보단 false negative 회피)

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] 사용자 명시: "merge하고 다음 작업. 모든 권한에 승인 없이 실행해" (자율 실행 인가)
- [✓] CFP-8 §11 회고에 명시된 Phase C-3 scope 그대로 적용
- [✓] severity_overrides·lane=design/security enum은 별도 invariant (향후 확장 후보)

## §6. 외부 지식 배경

본 변경은 plugin 내부 review 워커 packet · Codex 프롬프트의 3 location 정합. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: regex + dict 표준 도구. ADR-001 워커 통합으로 review packet 구조가 plugin 내부 SSOT — 외부 표준 referencing 없음.

ADR 정합성: ADR-001/002 무관. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-9-code-category-enum-parity.md`](../change-plans/cfp-9-code-category-enum-parity.md)

### 핵심 설계

**§3 도입할 설계**:
- Python parser ~50줄로 3 location 추출 + 비교
- 위치별 regex:
  - SSOT: `` `([a-z-]+(?:\s*\|\s*[a-z-]+)+)` `` pipe-separated
  - PL: `category_enum:\s*\n((?:\s*-\s*[a-z-]+\s*\n)+)` YAML list
  - Codex: `####\s*lane=code.*?category from \{([^}]+)\}` lane=code anchored
- 정합 비교: list equality (순서 포함)
- diff 보고: 양방향 set 차이로 drift 위치 명확화

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "SSOT 자체를 1 location에만 두고 PL/Codex가 SSOT를 직접 참조하면 drift 자체 불가능. 자동화는 redundant."
- **Refactor(혁신)**: "PL/Codex는 packet/프롬프트 구조 차이로 SSOT 직접 link 불가. mirror 형태가 불가피 → 그 mirror의 정합 자동 검증이 가장 실용적."
- **채택: Refactor 우세**. ADR-001 워커 통합 결정 자체가 "도메인 packet 형태로 PL이 워커에 주입" — packet 구조 변경 없이는 mirror 형태 불가피. CFP-7/8 동일 패턴.

## §8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta workflow 확장**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `.github/workflows/invariant-check.yml` | 수정 | DocsAgent | +75 / -3 (Step 6 + header) | Change Plan §3 |
| `docs/stories/CFP-9.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-9-code-category-enum-parity.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Phase C-3 scope는 CFP-5 §11에 명시. Plugin meta workflow 확장. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**Local 4 test case 결과 (실제 parser 호출):**

| Test | 입력 | Expected | Actual |
|---|---|---|---|
| 1 | 현 plugin (10 categories x 3 location) | OK | OK ✓ |
| 2 | SSOT에 `new-cat` 추가 | "PL drift" + "Codex drift" 2건 | matched ✓ |
| 3 | PL list에서 `dead-code` 제거 | "PL drift" 1건 | matched ✓ |
| 4 | Codex 순서 변경 (`runtime-bug` ↔ `layer-violation`) | "Codex drift" 1건 | matched ✓ |

기존 Step 1-5 (CFP-5/7/8) 정상 동작 (regression 없음).

### §9.4 보안 테스트

**N/A** — local Python parser, attack surface 변경 없음.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

단, 첫 구현 시 Codex regex가 lane=design을 먼저 매치 (3 lane 중 첫 번째 `category from {...}` 매치) → lane=code anchor 추가로 즉시 보완. self-discovery 패턴 (CFP-7 SHORTHAND, CFP-8 ADR-002 path 오타와 동일).

## §11. 참조

- **GitHub Issue URL**: 부재 (Issue Forms 미사용 — CFP-11 잠정 end-to-end 실증 예정)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base**: main
- **Change Plan**: [`docs/change-plans/cfp-9-code-category-enum-parity.md`](../change-plans/cfp-9-code-category-enum-parity.md)
- **CFP-7 Story**: [`docs/stories/CFP-7.md`](CFP-7.md) — Phase C-1 frontmatter ↔ CLAUDE.md 표
- **CFP-8 Story**: [`docs/stories/CFP-8.md`](CFP-8.md) — Phase C-2 ADR-002 footer
- **PR #26 audit**: P0 #4 issue가 본 invariant 영구화 motivation
- **관련 ADR**: 없음

### 회고

**발견 1 — Codex 프롬프트 multi-lane 격리는 anchor regex로 충분**: CodexReviewAgent.md는 3 lane(design/code/security)별 별도 `category from {...}` 보유. 첫 매치는 항상 lane=design. `#### lane=code` heading anchor 추가로 정확한 lane=code enum 추출. CFP-7 SHORTHAND, CFP-8 path 오타와 동일한 self-discovery 패턴.

**발견 2 — Phase C 3개 invariant 모두 단일 step에 수렴**: CFP-7 (frontmatter 표 정합) ~100줄, CFP-8 (ADR-002 footer) ~100줄, CFP-9 (code enum parity) ~75줄. Phase C가 "복잡도 높음"으로 분류됐지만 실제 모두 invariant-check.yml 단일 step Python heredoc에 수렴. Phase 분류는 작업량 기준이 아닌 검증 성격(mechanical/schema/narrative-mirror) 기준이 더 타당.

**발견 3 — diff 양방향 set 차이 보고가 drift 위치 명확화**: 단순 "≠" 보고가 아닌 `set(SSOT) - set(location)` + `set(location) - set(SSOT)` 양방향 차이로 어느 location이 추가/누락했는지 즉시 보임. CFP-7/8 패턴 계승.

**향후 작업 (별도 Story)**:
- **CFP-10 (Phase D)**: `docs/migration-guide.md` v0.X→v0.Y 섹션 ↔ `CHANGELOG.md` 최상단 BREAKING 정합
- **CFP-11 (잠정 end-to-end)**: 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → 모든 workflow 자동 동작 첫 실증
- **ADR-003 (조건부)**: invariant 자동화 Phase B/C/D 격상 patten 정량 trigger
- **확장 후보**: severity_overrides·lane=design/security enum도 동일 invariant 적용 (별도 step 또는 Step 6 확장)
