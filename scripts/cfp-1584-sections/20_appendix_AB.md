## 부록 A. 관련 문서

- `CLAUDE.md` — 에이전트 목록·레인·권한·GitHub Workflow·ADR 규약 ("무엇")
- 각 `agents/<Name>.md` — 에이전트별 역할·포지션·제약 (SSOT)
- 각 lane plugin `CLAUDE.md` self-write 표 — 문서화 표준 SSOT (Issue 코멘트 phase prefix, Story file 섹션 책임 분담) — codeforge-{review,pmo,requirements,test,develop,design}
- `.claude/_overlay/project.yaml` — 프로젝트 SSOT 상수 (GitHub·labels). Schema: `docs/project-config-schema.md`
- `docs/stories/<KEY>.md` — Story 11섹션 single-file SSOT
- `docs/adr/ADR-NNN-<slug>.md` — 설계 결정 아카이브 (flat, frontmatter category)
- `docs/change-plans/<slug>.md` — Change Plan 실행 명세 (Git-versioned)
- `templates/github-workflows/` — 6 GitHub Actions SSOT (consumer가 .github/workflows/로 복사)
- `templates/github-issue-forms/` — story.yml / bug.yml / audit.yml
- `templates/CODEOWNERS.template`, `templates/github-pr-template.md`

## 부록 B. 개정 이력

- 2026-04-23: 초기 작성 (18 에이전트 · 4 레인)
- 2026-04-24: v2 개편 (21 에이전트 · 6 레인) — EngineerPL 제거, CodebaseMapper·DesignReviewPL·ClaudeDesignReview·CodexDesignReview 신설, Review/Test 리네임, DocsAgent 단독 writer 원칙, FIX 카운터 Jira 라벨 단일, Fast-path/Codex 효용 평가 미도입
- 2026-04-24: v3 플러그인 pivot (범용 SW 개발 플러그인 `codeforge`로 재편, 22 에이전트 · 6 레인) — crypto 정체성 제거, overlay 메커니즘 β 도입
- 2026-04-24: v4 보안 테스트 레인 추가 (25 에이전트 · 7 레인) — SecurityTestPLAgent + ClaudeSecurityTestAgent + CodexSecurityTestAgent 신설, "테스트" 레인을 "구현 테스트"로 개편 후 "보안 테스트" 레인 추가, templates/ 디렉토리 도입
- 2026-04-24: v5 generic Dev roster + preset 시스템 (23 core 에이전트 + `role: dev` 동적 roster · 7 레인) — BackendDev·FrontendDev를 `presets/webapp/`으로 이동, core에 generic `DeveloperAgent` 신설, ServerEng를 `InfraEngineerAgent`로 리네임(범위 확장), DevPL이 `role: dev` frontmatter 태그로 런타임 roster discovery
- 2026-04-24: v6 Stage 2 `project.yaml` 구조화 SSOT 상수 도입
- 2026-04-26: **v8 Atlassian 제거 + GitHub 전환 (BREAKING)** — Confluence/Jira backend 완전 제거, GitHub primitive (Issues / PR / Milestones / Sub-issues / Projects v2 / Discussions / Actions / repo files / CODEOWNERS) 단일 backend화. Story 페이지 → `docs/stories/<KEY>.md` single-file SSOT. ADR → `docs/adr/ADR-NNN-<slug>.md` flat. Domain KB → `docs/domain-knowledge/<area>/<topic>.md` 계층. 1 Story = 2 PRs (Phase 1 docs / Phase 2 code+docs append). 6 GitHub Actions 자동화 (story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync). 보안 테스트 1차 layer = Dependabot/CodeQL/Secret Scanning/Push Protection. project.yaml schema `atlassian.*` → `github.*`. `gh` CLI 필수 추가, `github@claude-plugins-official` 플러그인 필수 격상.
- 2026-04-26: **v9 Review/Test 워커 통합 (BREAKING)** — [ADR-001](../docs/adr/ADR-001-review-agent-unification.md). 3 lane × 2 vendor = 6 워커(Claude/Codex × Design/Code/Security)를 lane-agnostic 2 워커(`ClaudeReviewAgent` / `CodexReviewAgent`)로 통합. 도메인은 호출 PL이 review packet으로 주입(checklist_path · scope_globs · category_enum · severity_overrides). 공통 base SSOT = `templates/review-pl-base.md`, 체크리스트 SSOT = `templates/review-checklists/{design,code,security}.md`. 25 → **20 core agents**. SecurityTestPL에 `Bash(gh api repos/*)` 권한 부여(1차 layer alerts fetch). 워커 packet 누락 시 `ESCALATE_PACKET_INCOMPLETE` 강제 — generic fallback 금지.

- 2026-05-09: **v10 CFP-293** — §8.4 성능 베이스라인 정책 (Issue #306 / NF-T5) 신설 + §14.11 Spawn ID 대장 mini-table (Issue #312) 신설 + §14.12 Spawn-level token telemetry mini-table (Issue #300) 신설.

본 playbook은 에이전트 구조·규약 변경 시 PR과 함께 갱신. git log로 변경 추적.
