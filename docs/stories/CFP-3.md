# CFP-3: v0.8 → v0.9 Migration Guide 추가 + v0.1 → v0.2 stale 안내 정정

## §1. 사용자 요구사항 (verbatim)

CFP-2 PR 생성 후 사용자 진행 지시:

> "계속"

CFP-2 회고에서 잠정 후보로 명시된 CFP-3 (`story_cutoff` schema validation)은 1인 maintainer 환경에서 over-engineering 성격이라 우선순위 낮음. 대신 v0.9 통합 후속 정합성 점검을 진행하던 중 **migration-guide.md의 v0.8 → v0.9 섹션 부재 gap**을 발견 — consumer 영향 큰 BREAKING change 가이드 누락. 이를 CFP-3으로 처리.

> CFP-1·CFP-2와 동일한 self-application 흐름 유지: cutoff 강제 대상 (SSOT 문서 의미 변경) → Story file 작성 의무 → 본 Story 영속화.

## §2. 도메인 해석

본 변경의 도메인은 **plugin meta 거버넌스 — consumer-facing migration 문서**. CFP-1·CFP-2와 동일한 plugin meta 도메인:

- 도메인 제약: Migration guide는 consumer가 plugin 버전업 시 직접 참조하는 문서 — gap이 있으면 consumer가 혼란 + stale overlay 잔존 위험
- 암묵 가정: BREAKING change 발생 시 그 시점에 migration 섹션 추가가 표준. v0.8 → v0.9는 누락된 상태로 main에 머지된 (`commit 3d2bfb2`) gap
- 범위 경계: `docs/migration-guide.md` 수정만. agent md / templates / workflow 무관
- 우선순위: Consumer 영향 직접적이라 빠른 정정 가치 큼

지식 공백: 없음 (ADR-001 + v0.9 commit 차이 분석으로 충분).

## §3. 관련 ADR

- **[ADR-001-review-agent-unification](../adr/ADR-001-review-agent-unification.md)** (active): v0.9 통합 결정 근거. Migration guide의 v0.8 → v0.9 섹션이 ADR-001을 인용
- **신규 ADR 필요 없음**: Migration guide 추가는 Process 산출물 (consumer-facing 문서화)이며 Architecture Decision 아님

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `docs/migration-guide.md` | 수정 | v0.1 ~ v0.8 BREAKING migration 가이드 | + v0.8 → v0.9 섹션 + v0.1 → v0.2 stale overlay 안내 cross-reference |
| `docs/stories/CFP-3.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-3-v0-9-migration-guide.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **v0.8 consumer가 v0.9로 업그레이드**: `docs/migration-guide.md`의 `v0.8 → v0.9` 섹션을 따라 ① stale overlay 6 파일 삭제 ② PL md overlay 점검 ③ 도메인 특화 보안 체크포인트 이전 ④ SecurityTestPL 권한 추가 (필요 시) ⑤ project.yaml 무관 확인
2. **v0.1 consumer가 v0.9로 progressive 업그레이드**: v0.1→v0.2→...→v0.8→v0.9 순서로 따라가다 v0.1→v0.2 §보안 테스트 레인의 `ClaudeSecurityTestAgent overlay` 안내를 만나도 cross-reference 주석으로 v0.9에서 무효임을 인지 → v0.8→v0.9 §3 절차로 이동
3. **신규 v0.9 consumer**: v0.7→v0.8 fresh setup 따른 후 v0.8→v0.9 §1 (stale overlay 삭제)는 skip (애초 overlay 없으므로) — 그대로 v0.9 사용 가능

### Acceptance Criteria

- `docs/migration-guide.md` 목차에 `v0.8 → v0.9` 항목 (역순 정렬, 최상단)
- `v0.8 → v0.9 (Review/Test 워커 통합 — BREAKING)` 섹션 본문 존재 — Breaking changes / Consumer 절차 5단계 / 체크리스트 4건 / 영향 범위 / 참고
- v0.1 → v0.2 §보안 테스트 레인의 stale overlay 안내 직후에 `> ⚠️ v0.9 이후 무효` cross-reference 블록
- frontmatter `updated: 2026-04-27`
- v0.1 → v0.8까지의 procedural step 본문 변경 없음 (historical accuracy 보존)

### 엣지 케이스

- **GitHub markdown anchor 변환**: 한글 헤더 `## v0.8 → v0.9 (Review/Test 워커 통합 — BREAKING)` → anchor `#v08--v09-reviewtest-워커-통합--breaking`. cross-reference 링크가 정상 동작해야 함. GitHub markdown은 한글 헤더의 한글 부분을 anchor에 그대로 보존하므로 정상 동작 예상. PR review에서 클릭 검증
- **Markdown link checker** (`.github/workflows/lint.yml`이 검증할 가능성): cross-reference의 `#v08--v09-...` 앵커가 link checker에서 reachable하다고 판단되어야 함. 첫 push 후 lint workflow 결과 확인 필요
- **v0.7 이하에서 6 워커 overlay를 만든 적 없는 consumer**: §1 stale 삭제 단계 skip — 절차 자체는 idempotent (`rm -f`이라 파일 부재 시 무동작). 안내문에 명시 ("있는 경우" 단서)

### §5.5 사용자 확인 필요 (blocking wait — 모두 본 세션에서 확인 완료)

- [✓] CFP-3 작업 진행 결정 ("계속")
- [✓] CFP-3 scope 변경: schema validation → migration guide gap (정합성 점검 발견 우선)
- [✓] CFP-2 PR 위에 stack 진행

## §6. 외부 지식 배경

본 변경은 plugin 자체 v0.9 commit 분석 + ADR-001 기반. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: BREAKING change 본질은 plugin 내부 결정이고, migration step은 그 결정의 직접 추론. 외부 라이브러리·표준·선행사례 별도 조사 없음.

ADR 정합성: ADR-001 active, 본 변경이 ADR-001 결정을 consumer-facing 문서로 표현. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-3-v0-9-migration-guide.md`](../change-plans/cfp-3-v0-9-migration-guide.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: v0.9 BREAKING (review/test 워커 통합) consumer migration guide 부재 gap 해소. v0.7 → v0.8까지만 있던 가이드에 v0.8 → v0.9 섹션 추가 + v0.1 → v0.2의 stale overlay 안내 cross-reference 보강.

**§3 도입할 설계**:
- `v0.8 → v0.9 (Review/Test 워커 통합 — BREAKING)` 섹션 신규 (~70줄)
  - Breaking changes (삭제·신설 agent / 호출 패턴 변경 / 신규 SSOT / packet 메커니즘 / 권한 변경)
  - Consumer 절차 5단계 (stale 삭제 / PL md 점검 / 도메인 이전 / 권한 추가 / project.yaml 영향 — 없음)
  - 체크리스트 4건
  - 영향 범위 (core/consumer/무관)
  - 참고 (ADR-001 / commit / SSOT)
- 목차 갱신 (역순 정렬, v0.8 → v0.9가 최상단)
- v0.1 → v0.2 §보안 테스트 레인 stale overlay 안내에 v0.9-superseded cross-reference 주석 1블록 추가
- frontmatter `updated: 2026-04-27`

**§4 API 계약**: Migration guide 텍스트 verbatim (Change Plan §4 참조). Cross-reference 주석 텍스트 (Change Plan §4.2).

**§9 분기 선택**: 단일 PR + 2 commit 분할 (migration guide 본체 / Story 영속화).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "v0.1 → v0.8 historical procedural step은 그 시점 정확. 변경 시 historical accuracy 훼손."
- **Refactor(혁신)**: "stale 안내가 현재 사용자에게 위험. 정정 또는 제거 필요."
- **채택: Hybrid**. v0.1 → v0.8 procedural step 본문은 보존(Mapper), stale overlay 안내 직후에 cross-reference 주석만 추가(Refactor 보강). 두 관점 모두 수용.

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta 변경, 코드 산출물 없음**.

본 변경은 markdown 문서 변경에 한정. `role: dev` roster 활성화 없음.

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `docs/migration-guide.md` | 수정 | DocsAgent | +75 / -1 (frontmatter `updated` + 목차 1줄 + v0.8→v0.9 섹션 ~70줄 + v0.1→v0.2 stale 주석 1블록) | Change Plan §3 |
| `docs/stories/CFP-3.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-3-v0-9-migration-guide.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음.

### §9.1 설계 리뷰

**N/A** — brainstorming skill 흐름 + 사용자 confirmation으로 대체 (CFP-1·CFP-2 동일 패턴).

### §9.2 구현 리뷰

**N/A** — 마크다운 정정·추가, 코드 변경 없음.

### §9.3 구현 테스트

**N/A** — 자동 테스트 대상 아님. PR review에서 cross-reference anchor link 동작 수동 검증.

### §9.4 보안 테스트

**N/A** — 의존성·attack surface 변경 없음.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## §11. 참조

- **GitHub Issue URL**: 부재 (Issue Forms 인프라가 PR #24에 있으나 미머지 상태 — chicken-and-egg 연속)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base PR (stack)**: PR #24 (CFP-2)
- **Change Plan**: [`docs/change-plans/cfp-3-v0-9-migration-guide.md`](../change-plans/cfp-3-v0-9-migration-guide.md)
- **CFP-1 Story**: [`docs/stories/CFP-1.md`](CFP-1.md)
- **CFP-2 Story**: [`docs/stories/CFP-2.md`](CFP-2.md)
- **관련 ADR**: [`docs/adr/ADR-001-review-agent-unification.md`](../adr/ADR-001-review-agent-unification.md)

### 회고

**발견 1 — Self-application 정책의 즉각 효과**: CFP-1 정책 수립 → CFP-2 인프라 → CFP-3 정합성 점검에서 **migration guide gap 발견**. Self-application 흐름 자체가 plugin SSOT의 stale state를 노출하는 메커니즘으로 작동. CFP-1 §11 회고의 "dogfooding gap이 가장 큰 가치"가 한 단계 더 입증.

**발견 2 — Historical accuracy vs forward-compat 균형**: v0.1 → v0.2 시점 procedural step을 보존하면서 v0.9 stale 위험을 표시하려면 cross-reference 주석이 적합. 본문 재작성은 Mapper 우려대로 historical 훼손 위험. Hybrid 접근 (보존 + 주석)이 두 관점 모두 만족.

**발견 3 — Stack PR 누적**: PR #23 → PR #24 → PR #25 (CFP-3 본 PR). 머지 안 된 상태에서 stack이 3개 누적. base 머지 시마다 다음 PR이 자동 rebase되지만, conflict 위험은 누적. PR #23 review/merge 우선 진행 권장 (사용자 결정).

**향후 작업 (별도 Story)**:
- **CFP-4 (잠정)**: 첫 정상 워크플로우 검증 — 임의 plugin meta 변경(예: README 보강·새 에이전트)을 Issue Forms로 시작해 자동화 동작 첫 실증. PR #24 머지 후 가능
- **CFP-5 (잠정)**: 정합성 점검 자동화 — `templates/` ↔ `agents/` ↔ `CLAUDE.md` ↔ `docs/migration-guide.md` 사이의 stale reference 자동 감지 워크플로우 (CodeQL custom query 또는 grep-based CI gate)
- **ADR-002 (조건부)**: Process Decision의 ADR 격상

CFP-3 자체가 "plugin이 자기 정합성을 점검 → gap 발견 → 정정"의 표준 사이클 첫 사례로 기록.
