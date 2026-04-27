# CFP-5: Invariant Check Phase A — workflow parity + plugin.json↔CHANGELOG version + agent count

## §1. 사용자 요구사항 (verbatim)

CFP-3 PR #27 close + audit Round 2 정리 직후 사용자:

> "다음 작업 시작합시다."

이전 메시지에서 사용자가 ok한 CFP-5 Phase A scope:

> Phase A scope (이번 작업):
> 파일 추가: .github/workflows/invariant-check.yml (PR/push 트리거)
> 검증 3종:
> 1. Workflow parity — for f in $(ls templates/github-workflows/); do diff -q templates/github-workflows/$f .github/workflows/$f; done
> 2. Version match — yq '.version' .claude-plugin/plugin.json ↔ head -1 CHANGELOG.md
> 3. Agent count — ls agents/*.md | wc -l ↔ grep '^Claude Code 범용' CLAUDE.md | grep -oP '\d+ core'

종합 리뷰 (Claude+Codex)의 가장 큰 합의 결론에 대한 첫 자동화 구현. **"다음 단계 우선순위는 새 기능 추가가 아니라 SSOT를 SSOT답게 유지하는 자동 invariant"** (Codex executive summary verbatim).

## §2. 도메인 해석

본 변경의 도메인은 **plugin meta SSOT drift 자동 차단**. self-application 흐름의 자연 진화 — 정책(CFP-1) → 인프라(CFP-2) → 사후 정합(CFP-3) → 메타 정합(CFP-4) → **invariant 자동화(CFP-5)**.

- 도메인 제약: GitHub Actions workflow가 PR/push 트리거로 동작. Plugin은 이미 yq, jq 사용 중이라 추가 도구 의존성 없음
- 암묵 가정: SSOT drift는 audit-by-human로 발견 가능하지만 (a) maintainer time burnout (b) 발견 지연 (c) consumer noticed 위험 → 자동 차단이 본질적 해결
- 범위 경계: Phase A 3 mechanical invariant만. Phase B/C/D는 별도 Story (validate_config.py / frontmatter↔CLAUDE.md 표 / ADR-002 footer / dup-local enum / migration-guide BREAKING 정합 등)
- 우선순위: Mechanical 검증 우선 — false positive 위험 매우 낮고 implementation 복잡도 낮음

지식 공백: 없음 (GitHub Actions semantics + bash one-liner 표준).

## §3. 관련 ADR

- **[ADR-001-review-agent-unification](../adr/ADR-001-review-agent-unification.md)** (active): 무관
- **[ADR-002-docsagent-inherit-footer-pattern](../adr/ADR-002-docsagent-inherit-footer-pattern.md)** (Accepted): 본 Phase A 미포함. Phase C-2에서 ADR-002 footer 검증 자동화 가능
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.github/workflows/invariant-check.yml` | 신규 | (없음) | 3 mechanical invariant 자동 검증 (push/PR 트리거) |
| `docs/stories/CFP-5.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-5-invariant-check-phase-a.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **Plugin maintainer가 templates/github-workflows/ 변경 + .github/workflows/ 미동기 commit**: invariant-check.yml의 Workflow parity step이 fail → PR review에 inline error → 머지 차단
2. **Plugin maintainer가 plugin.json version bump 후 CHANGELOG.md 갱신 누락 (또는 vice versa)**: Version match step이 fail → 양쪽 동기 갱신 의무 강제
3. **Plugin maintainer가 agents/ 신규 추가 후 CLAUDE.md 갱신 누락**: Agent count step이 fail → 동기 갱신 의무
4. **회귀 테스트로서 작동**: PR #26 audit P0 #5 ("24/25 → 20" 정정) 같은 사후 audit 작업이 미래에 재발 안 함

### Acceptance Criteria

- `.github/workflows/invariant-check.yml`이 main 현재 상태에서 3 invariant 모두 PASS (회귀 0건, local simulation 검증)
- workflow가 push to main + pull_request to main 트리거
- 각 step 실패 시 `::error::` annotation으로 어느 invariant 어떤 값이 mismatch인지 명시
- `permissions: contents: read` minimal scope

### 엣지 케이스

- **Phase A 3 invariant 외 drift**: 본 Story scope 외. Phase B/C/D 후속 Story로 점진 도입
- **GitHub Actions yaml syntax**: GitHub이 push 시 자동 lint. 작성 후 첫 push에서 syntax 오류 시 즉시 수정
- **`templates/github-workflows/*.yml` 신규 추가 시점**: 새 파일 추가 → `.github/workflows/`에 동시 복사 + 본 PR도 미머지 상태면 invariant-check가 fail. 자연스럽게 동시 작업 의무 강제

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] CFP-5 작업 진행 결정 ("다음 작업 시작합시다")
- [✓] Phase A scope 확정 ("ok") — workflow parity + version match + agent count 3종
- [✓] Phase B/C/D는 별도 Story로 분리

## §6. 외부 지식 배경

본 변경은 GitHub Actions native 기능 + bash standard tools 활용. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: GitHub Actions semantics는 plugin이 이미 6 workflow + lint/test로 검증된 사실이고, bash diff/jq/yq/grep은 표준 도구. 외부 라이브러리·표준·선행사례 별도 조사 없음.

ADR 정합성: ADR-001/ADR-002 모두 active, 본 변경과 무관. 통과.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-5-invariant-check-phase-a.md`](../change-plans/cfp-5-invariant-check-phase-a.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: Codex+Claude 종합 리뷰의 합의 결론 — "SSOT를 SSOT답게 유지하는 자동 invariant" — 의 첫 구현. Phase A는 mechanical 3종 (low risk, fast win).

**§3 도입할 설계**:
- `.github/workflows/invariant-check.yml` 신규
- Step 1 Workflow parity: `for f in templates/github-workflows/*.yml; do diff ...`
- Step 2 Version match: `jq '.version' plugin.json` ↔ `grep '^## \[N.N.N\]' CHANGELOG.md | head -1`
- Step 3 Agent count: `ls agents/*.md | wc -l` ↔ `grep -oE '[0-9]+ core 에이전트' CLAUDE.md | head -1`
- Trigger: push to main + PR to main, `permissions: contents: read`
- Phase B/C/D는 별도 Story (CFP-6+)

**§4 API 계약**: GitHub Actions yaml schema 표준. `::error::` annotation으로 PR review inline 표시.

**§9 분기 선택**: 단일 PR + 2 commit 분할 (workflow / Story+Change Plan).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "audit-by-human (Round 1·2)이 1인 환경에서 충분. 자동화는 over-engineering."
- **Refactor(혁신)**: "audit-by-human은 burnout + 지연 + consumer-facing risk. mechanical drift는 자동 차단."
- **채택: Refactor 부분 채택 (Phase A만)**. Mapper 우려는 Phase 분할로 흡수 — 전체 invariant 자동화 한 번에 도입 회피, mechanical 3종만 우선.

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta 인프라 추가, 코드 산출물 없음**.

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 | 상위 요건 ref |
|-----------|-----------|---------------|-----------|---------------|
| `.github/workflows/invariant-check.yml` | 신규 | DocsAgent | 신규 (~80줄) | Change Plan §3.2 |
| `docs/stories/CFP-5.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-5-invariant-check-phase-a.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음.

### §9.1 설계 리뷰

**N/A** — brainstorming skill의 사용자 approval (Phase 분할 + Phase A scope confirm)이 설계 검증 역할. PR review에서 정합성 추가 확인.

### §9.2 구현 리뷰

**N/A** — bash one-liner 단순 workflow. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**Local simulation 결과** (실제 invariant 로직 동일):
- Step 1 Workflow parity: 6 templates ↔ 6 self-app copy, 0 drift ✓
- Step 2 Version match: plugin.json `0.9.0` ↔ CHANGELOG.md `[0.9.0]` ✓
- Step 3 Agent count: agents/ 20 파일 ↔ CLAUDE.md "20 core 에이전트" ✓

GitHub Actions 실 실행 검증은 push 후. yaml syntax는 GitHub이 자동 lint.

### §9.4 보안 테스트

**N/A** — `permissions: contents: read` minimal scope. attack surface 변경 없음.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## §11. 참조

- **GitHub Issue URL**: 부재 (CFP-3·CFP-4와 동일 — Issue Forms 인프라 도입은 CFP-2 머지로 가능하지만 본 작업은 Issue Forms 우회로 수동 진행. CFP-7 잠정 Story가 end-to-end 실증 예정)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base**: main (PR #31 머지된 직후 상태)
- **Change Plan**: [`docs/change-plans/cfp-5-invariant-check-phase-a.md`](../change-plans/cfp-5-invariant-check-phase-a.md)
- **CFP-1 Story**: [`docs/stories/CFP-1.md`](CFP-1.md) — Self-application 정책
- **CFP-2 Story**: [`docs/stories/CFP-2.md`](CFP-2.md) — 인프라 2단계
- **CFP-3 Story**: PR #27 close (audit Round 2에 흡수)
- **CFP-4 Story**: [`docs/stories/CFP-4.md`](CFP-4.md) — Self-app 메타 정합
- **관련 ADR**: [`docs/adr/ADR-001-review-agent-unification.md`](../adr/ADR-001-review-agent-unification.md), [`docs/adr/ADR-002-docsagent-inherit-footer-pattern.md`](../adr/ADR-002-docsagent-inherit-footer-pattern.md)

### 회고

**발견 1 — Phase 분할로 ROI 균형**: 전체 invariant 자동화를 한 번에 도입하면 implementation 복잡도 + false positive 위험 + 디버깅 부담이 누적. Phase A의 3 mechanical invariant는 (a) 구현 < 80줄 bash (b) main 현재 상태 PASS 검증 완료 (c) 즉시 회귀 테스트 효과. 단계적 도입이 본질.

**발견 2 — audit-by-human → audit-by-CI 진화**: 사용자 audit Round 1 (PR #26, 21건) + Round 2 (b64cb15, 11건+) 패턴이 1인 maintainer의 burnout + 지연을 반복적으로 노출. 종합 리뷰의 가장 큰 합의는 "audit을 자동화해야 한다"였고 본 Phase A가 그 첫 구현. 향후 Phase B/C/D 도입 시 audit-by-human은 점차 "발견자 없음 invariant"만 다루게 됨.

**발견 3 — Self-application 흐름의 5번째 layer**: CFP-1 정책 → CFP-2 인프라 → CFP-3 사후 (close) → CFP-4 메타 정합 → CFP-5 자동화. 매 Story가 한 layer의 SSOT 강화. CFP-5 Phase A 머지 후 invariant 3종은 영구 보존되며 미래 drift 자동 차단.

**향후 작업 (별도 Story)**:
- **CFP-6 (Phase B)**: `validate_config.py`에 `story_cutoff.additional_exempt_categories` 검증 + unknown key reject (Codex 종합 리뷰 P1 #2)
- **CFP-7 (Phase C-1)**: frontmatter `permissions.allow` ↔ CLAUDE.md "Write queue 의뢰 권한" 표 정합 — Python regex parser 필요
- **CFP-8 (Phase C-2)**: ADR-002 footer SSOT 참조 1줄 패턴 검증 (모든 agent md의 "## 문서화 표준" 섹션)
- **CFP-9 (Phase C-3)**: `code.md` `dup-local: P1` SSOT enum 정합 (PR #26 audit P0 #4 invariant 영구 보존)
- **CFP-10 (Phase D)**: `docs/migration-guide.md` v0.X→v0.Y 섹션 존재 ↔ `CHANGELOG.md` 최상단 BREAKING 정합 — CFP-3 사후 정정 패턴 영구 차단
- **CFP-11 (잠정, end-to-end)**: 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → 모든 workflow (story-init + invariant-check + phase-gate-mergeable + ...) 자동 동작 첫 실증
- **ADR-003 (조건부)**: invariant 자동 점검의 Phase B/C/D 격상 시점 정량 trigger
