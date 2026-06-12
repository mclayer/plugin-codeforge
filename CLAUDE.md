# CLAUDE.md

## 언어 정책
모든 응답·주석·문서는 **한글 주 언어**. 영어는 기술 용어·코드·고유명사만. 한자(일·중 포함) 금지.

## 정체
codeforge = Claude Code 범용 SW 개발 오케스트레이션 플러그인 모노레포. **0 core 에이전트 (wrapper-only)** — wrapper 루트 자체 에이전트 0, 최상위 Claude 세션(Orchestrator)이 8개 lane plugin 의 에이전트를 spawn 해 요구사항 접수부터 배포 리뷰까지 진행한다. 8 lane plugin 은 본 repo `plugins/<plugin name>/` 하위 동봉 (ADR-118 D3) — 에이전트 상세 SSOT = `plugins/<lane>/CLAUDE.md`. 구 lane repo 8개 = 2026-06-12 GitHub archive (이력 보존, ADR-118 D1).

consumer 프로젝트가 **설치해 쓰는 플러그인**이다. 프로젝트별 도메인·기술스택·상수는 consumer 측 `.claude/_overlay/` 로 주입(overlay 는 정책을 확장만 가능, 축소 불가). 상세: [docs/consumer-guide.md](docs/consumer-guide.md).

8 lane plugin: `codeforge-{requirements, design, review, develop, test, deploy, deploy-review, pmo}@mclayer`. 추가 필수: `superpowers` · `github` · `codex`.

## 핵심 흐름
8 레인: 요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → 배포리뷰.

- **1 Story = Phase 1 PR(§1–7) + Phase 2 PR(§8–11).** 문서만 바뀌는 변경 = 1 PR. Epic = Phase 1 문서 PR + N개 구현 PR + close PR.
- Orchestrator 는 각 레인 진입 시 해당 lane plugin 의 **PL 에이전트 1개**만 spawn 한다 (PL 이 내부 sub-agent fan-out).
- Story file = `docs/stories/<KEY>.md` (KEY 접두사 = `CFP`). 각 레인이 자기 owned 섹션을 직접 write.

## 작업 규칙 (필수)
- **브랜치**: 모든 변경은 feature 브랜치(`cfp-NNN[-slug]`) + PR 경유. **main 직접 push 금지.**
- **worktree**: 모든 코딩 작업은 격리된 worktree(`~/.claude/worktrees/<repo>/<branch>`) 안에서 — `git checkout` 직접 편집 금지 — **Story/PR 완결(merge 확인) 직후 해당 worktree 즉시 정리**. 절차 = `codeforge:worktree-lifecycle` skill.
- **스크래치 위치**: repo 밖 임시 산출물은 `~/.claude/codeforge-scratch/` 만 허용 (홈 루트 직접 쓰기 금지 — repo-confinement 가드가 차단).
- **subagent default**: 수정 작업은 `Agent` tool spawn 으로 수행. inline 직접 편집(Read/Write/Edit/Bash 직접)은 4종만 허용 — 사용자 대화 / TodoWrite / 읽기전용 Q&A 답변 / 상태 보고.
- **병렬 default**: 서로 독립인 작업은 한 메시지에 다중 spawn. 순차는 (상태 의존 / 공유 자원 / 순서 자체가 의미) 중 하나일 때만.
- **검증 후 단언 (research-before-claims, ADR-119)**: substantive 단정 = 대상별 검증 선행 — ① 외부 지식: 자료 조사(WebSearch/WebFetch/공식 문서) + 출처 인용. ② repo·cross-repo 사실: 실측 — repo 내부는 Read/Grep, cross-repo 는 `git fetch` 후 origin/main 실제 확인(`git show origin/main:<path>`). 외부 워커(Codex 등) 출력은 직접 Read 검증 후 신뢰. ③ 확인 불가: "확인 불가/추정" 명시 후 진행. wrapper+consumer 모두 적용.

## 레인 진입 시 스킬 호출
Orchestrator 는 해당 레인 진입 직전 아래 스킬을 호출한다. 상세 절차·표는 각 스킬 본문 SSOT.

| 진입 시점 | 스킬 |
|---|---|
| 설계 | `codeforge:deputy-mandate` |
| 설계리뷰 / 구현리뷰 / 보안테스트 / 배포리뷰 | `codeforge:review-responsibility` |
| 배포 / lane owner path 확인 | `codeforge:lane-self-write-boundary` |
| FIX 루프 | `codeforge:root-cause-decision` + `codeforge:fix-ledger-schema` |
| 요구사항 접수 직후 | `codeforge:story-cutoff-classification` (Story 작성 의무 여부) |
| Story/Epic flow 결정 | `codeforge:story-epic-flow-preflight` |
| 코딩 작업 개시 직전 / Story·PR 완결 직후 | `codeforge:worktree-lifecycle` |
| 매 사용자 대화 turn | `codeforge:user-dialog-mode` |

## 결정 · 대화 원칙
- 합리적 default 가 자명하면 **묻지 말고** 무엇을 할지 통보 후 진행 (사용자가 정정).
- 권장 1안 + 대안 1안만 제시 (옵션 나열 금지). 3+ 후보는 brainstorm 영역.
- 내부 식별자(ADR/CFP 번호·계약명)는 사용자에게 평문 한 줄 풀이 먼저.
- 표·개조식으로 핵심을 앞에. 긴 평서문 덩어리 금지.

## 문서 위치
- 결정 기록(ADR) = `archive/adr/ADR-NNN-<slug>.md`.
- Change Plan / 도메인 지식 / 회고 = `docs/{change-plans,domain-knowledge,retros}/` (owner 에이전트 직접 write).
- 문서 종류별 위치 SSOT = [docs/doc-locations.yaml](docs/doc-locations.yaml).
- dogfood 산출물(spec/plan/story 등) = `mclayer/codeforge-internal-docs` repo.

## 필수 의존성 (세션 개시 확인)
- Orchestrator 모델 = 별칭 `opus` (최신 Opus tier). Sonnet/Haiku 세션이면 중단 후 재시작.
- MCP 서버 `github` 필수 (`mcp__github__*` 우선, 미커버 영역만 `gh` CLI fallback).
- 필수 CLI: `gh`, `codex`.
- 미노출 시 `/mcp` 재인증 / `/plugins install` 요구 후 대기. 복구 전 작업 중단.

## 마켓플레이스 동기화
plugin.json 의 `name`·`version`·`description`·`author` 변경 시 `mclayer/marketplace` 의 동일 필드를 같은 Story 안 sync PR 로 맞춘다 (marketplace sync PR 선행 merge → plugin PR merge). 상세: [archive/adr/ADR-063-marketplace-atomic-invariant.md](archive/adr/ADR-063-marketplace-atomic-invariant.md).

## 브랜치 보호
**branch protection contexts SSOT (wrapper 단일)**: `phase-gate-mergeable.yml` workflow job ID = `check-gate` — contexts 에 `check-gate` 포함 의무. CFP-1850-S2 wrapper 6-tuple 정합 확정 (상세 이력 = audit doc 보존).

| repo | required_status_checks contexts | 비고 |
|------|--------------------------------|------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)","check-gate","Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)"]` | 6-tuple (CFP-1808 Amendment 2). lane 8 repo = archived (CFP-2178 S6) — 보호 규칙 잔존+동결 (실측: deploy 1-repo smoke), 활성 관리 = wrapper 단일. audit: [docs/security/branch-protection-audit.md](docs/security/branch-protection-audit.md) |

## 시각 표기
사용자 대면·문서 표기 = KST `+09:00` ISO 8601. 외부 timestamp(GitHub/git)는 원본 보존.

## Sonnet → Opus fallback
`model: sonnet` 서브에이전트가 rate-limit 에러 반환 시: 동일 작업을 `model: opus` 로 1회 재spawn, 실패 시 사용자 통지 후 대기 (자동 재시도 금지).

---
> 본 파일은 Orchestrator 가 매 턴 자기검열해야 하는 정책만 담는다. 레인 내부 절차·근거·이력은 각 lane plugin CLAUDE.md / 스킬 / `docs/` 가 SSOT.
