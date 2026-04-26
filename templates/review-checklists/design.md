# Design Review 체크리스트 (lane=design)

DesignReviewPLAgent가 ClaudeReviewAgent / CodexReviewAgent에 packet으로 주입하는 설계 리뷰 체크리스트. 두 워커가 **공통 입력**으로 사용. SSOT 분리는 [ADR-001](../../docs/adr/ADR-001-review-agent-unification.md) 결정.

## 리뷰 대상 (scope_globs)

- `docs/change-plans/<slug>.md` (Change Plan 본문)
- `docs/stories/<KEY>.md` §1-7 (컨텍스트·Change Plan 요약·RefactorAgent 분석)
- `docs/stories/<KEY>.md` §3 관련 ADR (정합성 교차 입력)
- `docs/adr/ADR-*.md` (위 §3에서 언급된 ADR 본문)
- Change Plan §8 Test Contract

## Category enum (출력 분류)

`adr-mismatch | design-completeness | mapper-refactor-balance | implementability | test-contract | section-missing`

## Severity 자동 룰

- **ADR violation** → P0 강제 (`adr-mismatch`)
- **§8 Test Contract 누락** → P0 강제 (`section-missing` 또는 `test-contract`)
- **§3 도입할 설계 / §4 API 계약 / §5 변경 계획 / §6 리팩터링 선행 누락** → P0 강제 (`section-missing`)

## 체크리스트 (5축)

### 1. Change Plan 완결성 (`design-completeness`, `section-missing`)

- 필수 섹션 존재: 목적 · 현재 구조 분석 · 도입할 설계 · API 계약 · 변경 계획(파일 단위) · 리팩토링 선행 · 테스트 계획(§8 Test Contract 포함) · 분기 · ADR 여부
- "0 컨텍스트 개발자 전제" 구체성 — 파일·인터페이스·시그니처·이름·타입 확정 여부
- 모호한 표현(고려·검토·필요시) 식별 — Dev가 재량 없이 실행할 수 있는 수준인가

### 2. ADR 정합성 (`adr-mismatch`, P0 고정)

- Story file §3에 나열된 관련 ADR을 **명시적으로 fetch**하여 Change Plan 결정과 대조
- ADR 결정 위반 발견 시 **P0 severity 강제**
- 설계 의도가 ADR 변경이라면 "신규 ADR 필요" P0 지적 (신규 ADR 없이 기존 ADR 변경 금지 — [`templates/adr.md`](../adr.md) §파일 메타)

### 3. CodebaseMapper ↔ RefactorAgent 균형 (`mapper-refactor-balance`)

- Mapper의 변호 근거가 합리적 반박 없이 일축됐는지 점검
- Refactor 제안이 요건 범위를 초과해 과잉 리팩터링으로 흐르는지 점검
- 두 관점 충돌이 Change Plan §2(현재 구조) / §3(도입할 설계)에 명시적으로 기록됐는지

### 4. 구현 가능성 (`implementability`)

- Dev가 재량 없이 실행 가능한 구체성
- 모호한 네이밍·시그니처·타입 식별 → P1
- API 계약 불완전성 (요청/응답 스키마·에러 코드·비동기 약속) → P0 또는 P1

### 5. Test Contract 타당성 (`test-contract`)

- 커버리지 계획·경계 조건·invariant·성능 baseline 기준 명시
- Change Plan 범위 대비 커버리지 공백 식별
- 성능 baseline §8.3 프로토콜 (mean 10% 악화 기준 측정 절차) 명시 여부

## 다음 게이트 (PASS 시)

- DocsAgent가 `gate:design-review-pass` 라벨 부착
- Phase 1 PR mergeable → merge → 구현 lane 진입
- Story file §9.1 "설계 리뷰 Iteration N" 누적

## Consumer overlay 확장

Consumer는 `.claude/_overlay/templates/review-checklists/design.md`에 도메인 특화 체크 항목을 추가할 수 있다. SessionStart hook이 base + overlay merge.
