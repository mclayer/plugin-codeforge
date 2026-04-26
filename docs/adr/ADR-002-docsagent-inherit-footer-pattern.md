---
adr_number: 002
title: 모든 에이전트 md의 "문서화 표준" 섹션은 DocsAgent.md SSOT 참조 1줄만 유지
status: Accepted
category: Team & Process
date: 2026-04-27
related_files:
  - agents/DocsAgent.md
  - agents/ArchitectAgent.md
  - agents/CodebaseMapperAgent.md
  - agents/RefactorAgent.md
  - agents/RequirementsPLAgent.md
  - agents/DomainAgent.md
  - agents/RequirementsAnalystAgent.md
  - agents/ResearcherAgent.md
  - agents/DesignReviewPLAgent.md
  - agents/CodeReviewPLAgent.md
  - agents/SecurityTestPLAgent.md
  - agents/ClaudeReviewAgent.md
  - agents/CodexReviewAgent.md
  - agents/DeveloperPLAgent.md
  - agents/DeveloperAgent.md
  - agents/DataEngineerAgent.md
  - agents/InfraEngineerAgent.md
  - agents/QADeveloperAgent.md
  - agents/TestAgent.md
  - agents/PMOAgent.md
  - presets/webapp/agents/BackendDeveloperAgent.md
  - presets/webapp/agents/FrontendDeveloperAgent.md
related_stories: []
---

# ADR-002: 모든 에이전트 md의 "문서화 표준" 섹션은 DocsAgent.md SSOT 참조 1줄만 유지

## 상태

`Accepted` (2026-04-27)

## 컨텍스트

`codeforge` 플러그인은 **DocsAgent 단독 writer 원칙**(CLAUDE.md "문서 write 단독 writer 원칙")을 채택해 GitHub Issue/PR/comment·`docs/**` 파일 write를 DocsAgent로 단일화했다. 다른 에이전트는 `.claude-work/doc-queue/<story>/` 큐에 의뢰만 한다.

이 정책은 모든 에이전트 md에 영향을 주는 cross-cutting 규약이지만, 처음에는 각 에이전트 md 본문에 GitHub Issue 코멘트 형식·phase prefix·Story file 섹션 규격 등을 산발적으로 기재했다 → 9개 이상의 사본이 drift를 유발 (Round 1 audit).

ADR-001 (워커 통합) 후속으로 **DocsAgent.md를 단일 SSOT로 통합**하고, 다른 모든 에이전트 md 끝에 "문서화 표준" 섹션을 1줄 참조로 유지하기로 정착시켰다 (현재 22개 파일 일관 적용 — 22개 = `agents/` 19종 + `presets/webapp/agents/` 2종 + DocsAgent 자기 포함 1종, 단 DocsAgent는 SSOT 본체이므로 footer 미적용).

본 ADR은 이 inherit 패턴의 의도·범위·유지 규약을 형식화해, 향후 신규 에이전트 추가·preset 확장 시 일관성을 보장한다.

## 결정

### 1. SSOT 위치

**DocsAgent.md "문서화 표준 SSOT" 섹션**(`agents/DocsAgent.md` §"문서화 표준 SSOT" 이하)이 모든 문서 기록 표준의 **단일 출처(Single Source of Truth)**:

- GitHub Issue 코멘트 형식 + phase prefix 11종
- Story file 섹션 규격 (참조: `templates/story-page-structure.md`)
- Change Plan 템플릿 (참조: `templates/change-plan.md`)
- ADR 템플릿 (참조: `templates/adr.md`)
- FIX Ledger 스키마 (참조: CLAUDE.md "FIX 루프" + `docs/orchestrator-playbook.md` §6)
- Impl Manifest 스키마 (참조: `templates/impl-manifest.md`)

### 2. 다른 에이전트 md의 footer 양식 (exact-copy invariant)

DocsAgent **외**의 모든 에이전트 md(현재 21개 + 향후 신규)는 마지막 섹션에 다음 2줄을 **exact-copy로 유지**한다:

```markdown
## 문서화 표준
[`agents/DocsAgent.md`](DocsAgent.md) 참조.
```

또는 권한 deny 명시가 함께 필요한 경우(권장 — Write/Edit 권한 없는 에이전트):

```markdown
## 문서화 표준
GitHub Issue/PR/docs write 권한 없음. 모든 문서화는 Orchestrator 경유 DocsAgent가 기록 (write queue 경유). 문서화 표준은 [DocsAgent.md](DocsAgent.md) 참조.
```

(워커 의뢰 권한이 있는 에이전트는 "(write queue 경유)" 절 포함, 단순 read-only 에이전트는 생략 가능)

### 3. 변경 금지 범위

- **footer 본문 확장 금지** — 표준 변경은 전부 DocsAgent.md SSOT를 갱신해야 한다. 다른 에이전트 md에 표준 일부를 인라인 복제하면 drift 발생
- **참조 경로 일관 유지** — `agents/<X>.md` 위치에서는 `[DocsAgent.md](DocsAgent.md)` (상대), `presets/<flavor>/agents/<X>.md` 위치에서는 `[../../agents/DocsAgent.md](../../agents/DocsAgent.md)` 또는 SSOT 텍스트 참조

### 4. CodeReview 강제 항목

신규 또는 수정된 에이전트 md PR에서 다음을 검증:

1. footer 섹션 누락 시 → P1 (DesignReview에서 패턴 누락 지적)
2. footer 본문이 SSOT 외 표준을 인라인 복제 시 → P0 (drift 위험)
3. SSOT 갱신 PR에서 다른 에이전트 md footer를 부수적으로 수정하는 경우 → P1 (단일 책임 위반 — SSOT 갱신은 본 ADR 결정 변경 PR과 분리)

## 결과

### 긍정

- **drift 방지**: 표준 변경 시 1군데(`DocsAgent.md`)만 갱신 — Round 1 audit에서 발견된 9개 사본 drift 같은 문제 재발 방지
- **신규 에이전트 추가 비용 ↓**: 작성자가 표준 본문을 다시 쓸 필요 없이 footer 2줄만 추가
- **권한 정책 가시성**: footer가 짧지만 매 에이전트 md에 명시되어 "이 에이전트는 직접 write 못 한다"가 즉시 인지됨 (예: 새 에이전트 작성자가 무심코 `Write(docs/**)` 권한 추가하는 일 차단)

### 부정 / 트레이드오프

- 22개 footer 사본을 유지해야 함 — 형식적으로는 중복. 단 본문이 1줄(또는 2줄)에 불과하므로 drift 비용보다 visibility 가치가 크다
- footer 본문 변경(예: SSOT 위치 이동)은 22개 동시 갱신 필요 — 한 번에 처리하는 정책 변경 PR 형태로 진행

### 대안 (기각)

| 대안 | 기각 사유 |
|------|----------|
| **A. footer 완전 제거 + CLAUDE.md 선언만 유지** | 신규 에이전트 작성자가 권한·기록 정책을 즉시 인지하기 어려움. 검토 시 매번 CLAUDE.md를 펼쳐야 함 (인지 부하 ↑) |
| **B. 구조적 재구성 — 권한·표준 metadata를 frontmatter로 통일** | YAML frontmatter에 표준 본문을 인라인 작성 시 가독성 저하. agent md 작성자는 markdown 본문 위주로 작업하므로 footer 형식이 더 자연스러움 |
| **C. Symlink로 단일 본문 공유** | Git tree symlink는 일부 호스팅 환경에서 일관 렌더링 안 됨. CI 의존성 추가 |

## 다이어그램

```
[CLAUDE.md] "문서 write 단독 writer 원칙" 선언 (정책 개요만)
    │
    │ "문서화 표준은 DocsAgent.md SSOT 참조"
    ▼
[agents/DocsAgent.md] §"문서화 표준 SSOT" — 본체 표준 (코멘트 형식·phase prefix·Story 섹션 규격·...)
    │
    │ exact-copy footer 2줄
    ▼
[다른 21 에이전트 md]
    "## 문서화 표준
     [DocsAgent.md](DocsAgent.md) 참조."
```

## 관련 파일

- 본 ADR이 강제하는 footer가 적용된 에이전트 md: 위 `related_files` 참조 (현재 22개)
- 본 ADR 미적용 (예외): `agents/DocsAgent.md` (자체가 SSOT 본체이므로 footer 미적용)
- CodeReview 강제 항목: [CLAUDE.md](../../CLAUDE.md) "문서 write 단독 writer 원칙" + [`templates/review-checklists/code.md`](../../templates/review-checklists/code.md)
