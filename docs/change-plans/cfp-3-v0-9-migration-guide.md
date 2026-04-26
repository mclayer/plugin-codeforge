---
title: v0.8 → v0.9 Migration Guide 추가 + v0.1 → v0.2 stale 안내 정정
slug: cfp-3-v0-9-migration-guide
status: draft
author: ClaudeOrchestrator (CFP-2 정합성 점검 발견)
reviewers: [user]
related_adrs: [ADR-001-review-agent-unification]
created: 2026-04-27
story: CFP-3
---

## §1. 목적

v0.9 BREAKING change(review/test 워커 통합)에 대한 consumer migration guide 부재 gap 해소. v0.7 → v0.8까지만 있던 [`docs/migration-guide.md`](../migration-guide.md)에 `v0.8 → v0.9` 섹션 추가하고, v0.1 → v0.2 섹션의 stale `ClaudeSecurityTestAgent` overlay 안내(line 504 부근)에 cross-reference로 stale 표시.

### 수용 기준

- `docs/migration-guide.md`에 `v0.8 → v0.9 (Review/Test 워커 통합 — BREAKING)` 섹션 존재
- 목차에 v0.8 → v0.9 항목 추가 (역순 정렬 — 최신이 위)
- frontmatter `updated: 2026-04-27` 갱신
- v0.1 → v0.2 §보안 테스트 레인 안내에 v0.9-superseded cross-reference 주석 (`> ⚠️ **v0.9 이후 무효**`) 명시
- v0.2 ~ v0.8 시점 historical accuracy는 보존 (해당 섹션의 procedural step은 그대로 유지, 추가 주석만)

## §2. 현재 구조 분석

### 2.1 Migration guide gap

```
v0.7 → v0.8 (Atlassian → GitHub) — 있음
v0.8 → v0.9 (review/test 워커 통합) — 없음 ← gap
```

v0.9 BREAKING은 `commit 3d2bfb2`로 main에 들어갔지만 consumer 가이드 부재. v0.8 사용자가 v0.9로 올라갈 때 무엇을 해야 하는지 모름:
- 6 stale 워커 overlay md 처리 방법?
- PL md overlay 영향?
- 도메인 특화 보안 체크포인트(이전에 ClaudeSecurityTestAgent overlay에 있던 것) 어디로 이전?
- SecurityTestPL 권한 변경?

### 2.2 v0.1 → v0.2 섹션의 stale 안내

v0.1 → v0.2 마이그레이션 가이드(line 503-505)에:

> 보안 테스트 레인이 consumer 프로젝트 특화 기준을 요구하면:
> - `.claude/_overlay/agents/ClaudeSecurityTestAgent.md`, `CodexSecurityTestAgent.md` 신설 — 프로젝트 특화 보안 체크포인트 추가

이 안내는 v0.2 시점에 정확했으나 v0.9에서 해당 agent 자체가 삭제됨. v0.1 → v0.2 → ... → v0.9로 progressive migration하는 사용자가 이 안내를 따르면 v0.9에서 stale overlay 파일이 만들어짐.

### 2.3 Plugin SSOT 정합성 점검 결과

CFP-2 후속 점검에서 발견:
- 모든 `agents/**.md`: stale 워커 이름 0건 ✓
- `templates/`: stale 0건 ✓
- `docs/orchestrator-playbook.md` 본문: 정상 갱신 ✓ (§변경이력은 historical accuracy로 잔존, OK)
- `docs/migration-guide.md`: v0.8 → v0.9 섹션 부재 → gap

`docs/migration-guide.md`만 정정 필요.

### 2.4 Mapper 변호 근거

기존 historical 섹션을 그대로 보존하자는 Mapper 입장: "v0.1 → v0.2 섹션의 procedural step은 그 시점에 정확했고, 변경하면 historical accuracy 훼손."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Hybrid (둘 다 수용)**.

- v0.1 → v0.2 섹션의 procedural step **본문은 그대로 보존** (Mapper 변호 — 그 시점 정확)
- 단 stale overlay 안내 직후에 **`> ⚠️ v0.9 이후 무효` cross-reference 블록 추가** (Refactor 보강 — 현재 사용자에게 stale 위험 경고)

이 방식은 두 관점 모두 만족:
- Historical record 유지 (v0.2 시점 사용자가 본 것 그대로)
- Forward-compat 표시 (현재 v0.9 사용자가 잘못 따라가지 않음)

### 3.2 v0.8 → v0.9 섹션 구조

`v0.7 → v0.8` 섹션과 동일 패턴:

1. `### Breaking changes` — 변경 본질 + 영향 받는 agent/SSOT 목록
2. `### Consumer 절차` — 단계별 작업 (5단계: stale 삭제 / PL md 점검 / 도메인 특화 이전 / 권한 추가 / project.yaml 영향)
3. `### 체크리스트` — 4 체크포인트
4. `### 영향 범위` — core 변경 / consumer 작업 / 무관 분류
5. `### 참고` — ADR / commit / SSOT 위치

### 3.3 위치

`v0.7 → v0.8` 섹션 **바로 위** (역순 정렬 유지 — 최신 BREAKING이 목차·본문 모두 첫 위치).

### 3.4 ADR 정합성

- ADR-001 (review-agent-unification): **인용 강화**. Migration guide §참고에서 결정 근거로 명시
- 신규 ADR 필요: **없음**. v0.9 통합 자체가 ADR-001로 결정된 상태이고 본 변경은 그 결정의 consumer-facing 문서화

## §4. API 계약

### 4.1 Migration guide 텍스트

§3.2 구조에 따라 작성. 본문 verbatim은 [docs/migration-guide.md](../migration-guide.md) v0.8 → v0.9 섹션 참조.

### 4.2 Cross-reference 주석 텍스트

```markdown
> ⚠️ **v0.9 이후 무효** — 위 안내는 v0.2 ~ v0.8 시점의 절차다. v0.9에서 review/test 워커가 lane-agnostic 통합되어 `Claude*SecurityTestAgent`·`Codex*SecurityTestAgent` 자체가 삭제됐다. v0.9 이후 consumer는 도메인 특화 보안 체크포인트를 [v0.8 → v0.9 §3 절차](#v08--v09-reviewtest-워커-통합--breaking)에 따라 `templates/review-checklists/security.md` overlay 또는 SecurityTestPL packet 자동 룰로 이전해야 한다.
```

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `docs/migration-guide.md` | 수정 (frontmatter `updated` + 목차 1줄 + v0.8→v0.9 섹션 신규 ~70줄 + v0.1→v0.2 stale 주석 1블록) | DocsAgent | 적용 완료 |
| `docs/stories/CFP-3.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-3-v0-9-migration-guide.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 기존 섹션 보존 + 신규 섹션 1개 + 주석 1블록 추가.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — 마크다운 추가
- 통합 테스트: **N/A**
- 인프라 테스트: **N/A**
- **검증 방법**: PR review에서 문서 정합성 + cross-reference 링크 정상 동작 확인 (markdown anchor `#v08--v09-reviewtest-워커-통합--breaking`이 v0.8 → v0.9 섹션 헤더로 jump하는지)

### §8.2 경계 조건·invariant

- v0.1 → v0.8까지의 historical procedural step **변경 금지** (CFP-3 검증) — frontmatter `updated`만 갱신, 기존 섹션 본문 보존
- 목차 역순 정렬 유지 (최신 BREAKING이 위)
- `markdown link checker` (.github/workflows/lint.yml의 일부일 가능성) 통과 여부 — anchor link `#v08--v09-...`가 GitHub markdown 자동 anchor 규칙에 부합해야 함 (한글 헤더는 영문 슬러그로 변환되지 않으므로 절단 가능)

### §8.3 Perf Baseline

**N/A** — 문서 변경.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (Plugin meta 변경, 단순 문서 추가).

Commit 시리즈 1개로 단순 처리:
- **Commit 1**: `docs/migration-guide.md` (frontmatter + 목차 + v0.8→v0.9 섹션 + v0.1→v0.2 stale 주석)
- **Commit 2**: `docs/stories/CFP-3.md` + `docs/change-plans/cfp-3-...md`

본 PR base는 `feat/cfp-2-self-application-infra` (PR #24). PR #23/#24 머지되면 자동 rebase to main.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-001** (review-agent-unification): **인용**. Migration guide §참고에서 결정 근거로 명시. 본 변경은 ADR-001 결정의 consumer-facing 문서화이므로 ADR-001과 일치
- **신규 ADR 필요**: **없음**. Migration guide 추가는 Process 산출물이며 Architecture Decision 아님
