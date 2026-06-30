# Code Review 체크리스트 (lane=code)

CodeReviewPLAgent가 ClaudeReviewAgent / CodexReviewAgent에 packet으로 주입하는 구현 리뷰 체크리스트. SSOT 분리는 [ADR-001](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-001-review-agent-unification.md).

## 리뷰 대상 (scope_globs)

- 앱 코드: `src/**`
- 인프라 자산: `config/**`, `deploy/**`, `scripts/**`
- 테스트 코드: `tests/**`
- Story file §8.5 Impl Manifest (파일 단위 매핑 검증 입력 — 누락된 파일 있으면 P0)

## Category enum (출력 분류)

`runtime-bug | layer-violation | naming | test-quality | impl-manifest-mismatch | concurrency | error-handling | dead-code | dup-local | dup-boundary | integration-test-readiness | exec-result-mismatch`

> `exec-result-mismatch` = 실행 검증 axis (CFP-2477 / ADR-070 Amd11 §결정 D9) — PR touch 한 게이트·체크를 실제 실행한 ground-truth(exit/stdout)가 PR/Story 단정 또는 명백 정책(ADR-037 등)과 모순. 정적 추정 아님.

## Severity 자동 룰

- **Impl Manifest §8.5 매핑 누락 또는 실제 파일과 불일치** → P0 강제 (`impl-manifest-mismatch`)
- **레이어 경계·의존성 방향 위반** → P0 강제 (`layer-violation`) — Hexagonal/Clean Architecture ADR 준수
- **데이터 손실·panic·null deref 등 명백한 런타임 결함** → P0 강제 (`runtime-bug`)
- **실행 결과 ↔ 단정/명백 정책 모순 (PL 재실행 falsify 통과 + flaky/환경차 배제)** → severity = 모순이 드러낸 실 결함 기준 (`exec-result-mismatch`). 실행 GREEN 은 finding 미승격 (Popper falsify 전용). flaky/환경차 의심 = `undetermined` 보류 (자동 승격 금지)

## 체크리스트 (8축)

### 1. 코드 ↔ Change Plan 변경 계획 준수 (`impl-manifest-mismatch`)

- Change Plan §5 변경 계획 / §8.5 Impl Manifest 매핑표와 실제 변경 파일 일치 확인
- 매핑표 누락 파일 있으면 P0
- 매핑표에 있으나 실제로 변경 안 된 파일 있으면 P1

### 2. 레이어 계약·의존성 방향 (`layer-violation`)

- 관련 ADR(아키텍처 결정) 준수 — 예: Hexagonal Architecture에서 도메인 → 포트 → 어댑터 단방향
- 의존성 방향 역전 (예: 도메인이 어댑터 import) → P0
- 모듈 경계·인터페이스 일관성

### 3. 코드 품질 (`naming`, `dup-local`, `dup-boundary`)

- 네이밍·시그니처·에러 전파 일관성
- **P1 품질 local vs boundary 분류** (CLAUDE.md 원인 판정 decision table 기반):
  - `dup-local`: 1개 파일 또는 1개 함수 범위에 한정 (**P1**, 구현 원인 — 동일 파일 내 품질 결함)
  - `dup-boundary`: 여러 파일·계층에 걸친 패턴 부재 이슈 (**P1**, 설계 원인 escalation 후보)

### 4. 런타임 오류·동시성 (`runtime-bug`, `concurrency`, `error-handling`)

- null/None deref · 타입 불일치 · panic 가능성
- race condition · deadlock · TOCTOU
- 예외 경로 누락 · 빈 except · 에러 무음 처리

### 5. 테스트 코드 품질 (`test-quality`)

- 커버리지 누락 영역 식별 (QADev 매핑표와 교차)
- 경계 케이스·invariant 검증
- mock 경계 적절성 (외부 의존성만 mock, 내부 로직 mock 금지)
- assertion 강도 (단순 not None vs 도메인 의미 검증)
- (§8.7 active Story) 구현된 venue 형상 fixture가 §8에 선언된 형상(seq 의미론/timestamp granularity·다중성/GAP·rate-spike/disorder)을 **실제로 재현하는가** — §8 선언만으로 불충분, fixture 코드가 균일 +1 seq·고정 interval 합성이면 §8 contract 미이행 (ADR-006 Amendment 1 / §8.7)

### 6. Dead code · 미완성 (`dead-code`)

- 도달 불가 코드 · 사용되지 않는 import/변수
- TODO/FIXME 미해결 (Change Plan에 후속 ADR 명시 없으면 P1)

### 7. 통합테스트 사전 조건 (`integration-test-readiness`)

CFP-367 / ADR-055 — IntegrationTestAgent 진입 전 CodeReviewPL이 검증하는 통합테스트 준비 항목.

- **§8.6 Integration Test Contract 존재 여부**: Story §8.6이 `N/A`가 아닌 경우 → `docker-compose.test.yml` 존재 필수 (누락 시 P1)
  - 대상: 컴포넌트 경계 2개 이상 변경 Story
  - 체크: 레포 루트 또는 `deploy/` 하위에 `docker-compose.test.yml` 파일 존재 확인
  - 없으면: P1 `integration-test-readiness` — "§8.6에 environment_dependencies 명시됐으나 docker-compose.test.yml 없음"
- **§8.6 면제 Story**: §8.6에 `N/A — <근거>` 명시된 경우 본 섹션 체크 생략

> **참고**: `tests/integration/<story-key>/` 파일 존재는 IntegrationTestAgent가 lane 6에서 직접 작성하므로 CodeReviewPL이 blocking하지 않는다. InfraEngineerAgent가 작성해야 하는 `docker-compose.test.yml`만 체크 대상.

### 8. 실행 검증 (`exec-result-mismatch`)

CFP-2477 / ADR-070 Amendment 11 §결정 D9 — **execute-the-gate vs read-the-diff**. Codex worker가 정적 diff 읽기에 더해 PR touch 한 게이트·체크를 실제 실행해 단정과 대조 (개념 SSOT = `docs/domain-knowledge/concept/execution-based-review-verification.md`).

- **실행 대상** = PR touch 파일 ∩ discriminating check(self-test/eval 모드, 결함 시 RED) 우선. 70+ 전수 금지. 대표 후보 = `check-plugin-version-bump-self.sh`(ADR-037) 외 self-test 보유 게이트. Python 게이트(ADR-061 thin-wrapper, *.py)도 대상 — Codex sandbox python3 안 실행.
- **실행 주체** = Codex 자체 sandbox (read-only 기본 / network-off / `.git`·`.codex` 보호). lane worker own-Bash 실행 아님 (CodexReviewAgent allowlist 미확대). write 필요 게이트만 `task --write`(workspace-write) + `[exec-verify-write-mode: <check>]` marker.
- **승격 룰** = 실행결과 ↔ 단정 모순일 때만 finding (`exec-result-mismatch`). 실행 GREEN 은 승격 금지 (Popper falsify 전용). 동일 입력 다회 실행 결정론 확인 후 승격 — flaky/환경차 의심 = `undetermined` 보류. finding 구조 = {asserted/expected, executed target, exec verdict(exit+stdout), conflict summary}.
- **verify-before-trust** = Codex 실행 결과 = `[hypothesis]` → **CodeReviewPL 직접 재실행 falsify 통과 시만 채택** (ADR-070 Amd11 §결정 D9, §결정 D6.1 mandatory-real-execution-evidence 확장). 정적 추정만으로 채택 불가.
- **검증 제약 분리** = 실행 불가(권한/interpreter 부재/환경 미구성)는 "검증 제약" 으로 제품결함 finding 과 분리 (UC-3). Codex 미가용 = lane-time `fail_open_then_record_with_marker` (`[exec-verify-fallback: ...]`).

## 다음 게이트 (PASS 시)

- 구현 테스트 lane 진입 (Orchestrator → TestAgent 스폰)
- Story file §9.2 "구현 리뷰 Iteration N" 누적

## 1차 원인 가정 (FIX 시)

원인 판정 표는 [CLAUDE.md](../../CLAUDE.md) "원인 판정 decision table" SSOT. 본 체크리스트는 코드 lane 카테고리 enum과 severity override만 담당하며, 원인 분기 표는 inline 복제하지 않는다 (drift 방지). PL이 1차 진단 → DeveloperPL이 재진단 → Architect 최종 판정.

## Consumer overlay 확장

Consumer는 `.claude/_overlay/templates/review-checklists/code.md`에 언어·프레임워크 특화 체크 항목을 추가할 수 있다 (예: Python의 `__init__.py` 검사, Go의 goroutine leak 패턴).
