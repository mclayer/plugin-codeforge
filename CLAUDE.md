# CLAUDE.md

## 언어 정책

모든 응답·코드 주석·문서 작성에서 **한글을 주 언어로 사용**. 영어는 기술 용어·코드·고유명사 등 필요한 경우에만 사용. 한자(일본어·중국어 포함) 사용 절대 금지.

Claude Code 범용 SW 개발 오케스트레이션 플러그인. **0 core 에이전트 (wrapper-only)** · 7 레인 + `role: dev` 동적 roster 로 요구사항 접수부터 보안 테스트 통과까지 자율 실행. 에이전트 상세는 각 lane plugin (codeforge-{review,pmo,requirements,test,develop,design}) SSOT — 본 wrapper repo 에는 agent file 없음. Dev preset 은 [codeforge-develop presets/](https://github.com/mclayer/plugin-codeforge-develop/tree/main/presets) 참조.

## Plugin

이 리포는 **consumer 프로젝트가 설치해 사용하는 Claude Code 플러그인**. 프로젝트별 도메인·기술 스택·SSOT 상수는 **overlay 메커니즘**(consumer 측 `.claude/_overlay/` + SessionStart merge hook)으로 주입. 상세는 [`docs/consumer-guide.md`](docs/consumer-guide.md) 참조.

**Objective SSOT 상수** (GitHub org/repo·story_key_prefix·CODEOWNERS team·Discussions 카테고리·Milestone naming·label taxonomy)는 **`.claude/_overlay/project.yaml`** 에 structured로 기재. 에이전트는 해당 파일을 `Read`로 직접 참조. Schema: [`docs/project-config-schema.md`](docs/project-config-schema.md). Narrative 컨텍스트(도메인 해설·기술 스택 근거)는 `.claude/_overlay/CLAUDE.md`에 기재.

### Marketplace cross-repo 동기화 의무

본 플러그인은 [`mclayer/marketplace`](https://github.com/mclayer/marketplace) 를 통해 노출. codeforge family 7 plugin (wrapper + 6 lane) **모두 등록**. **mirrored 필드** = `name`·`version`·`description`·`author` — 변경 시 `marketplace.json` `plugins[name=codeforge]` 동일 필드를 **같은 Story 내 sync PR** (codeforge PR merge 직후 즉시 open·merge). 비-mirrored 필드(`keywords` 등) 면제. 정식 cross-repo parity CI 는 후속 CFP-50 잠정 — 도입 전까지 author·Orchestrator 의무. drift 시 stale version install 로 단일 진입점 의미가 무너진다. 정책 SSOT: [ADR-016](docs/adr/ADR-016-marketplace-registration-policy.md) (CFP-49).

## SSOT Boundary

Wrapper CLAUDE.md content scope = (1) Plugin identity (2) Cross-cutting policy (3) 4 SSOT 예외 (책임 매트릭스 / 원인 판정 decision table / FIX Ledger §10 schema / 6 deputy mandate matrix) — 정확한 정의는 [ADR-012](docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md). Dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) monorepo SSOT, plugin repo 작업 시 brainstorming/writing-plans skill 의 spec/plan 저장 위치도 internal-docs override — 정책 SSOT: [ADR-013](docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (CFP-45).

Lane internal · per-lane spawn detail · severity rule · GitHub workflow subsection 상세는 lane plugin CLAUDE.md 또는 [playbook](docs/orchestrator-playbook.md) 위임.

## 세션 개시 의무 (필수 의존성 SSOT)

세션 시작 직후, 모든 작업보다 먼저 의존성 노출·설치·인증 상태 확인. 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 요구. 복구 완료 전까지 **모든 작업 중단**.

**MCP 서버 (1종)**: `github` — Issue/PR/sub-issue/comment·label·milestone 각 lane plugin self-write; `docs/{change-plans,adr,domain-knowledge,retros}/**` 직접 write 는 owner agent (CFP-26 Phase 0a)

**GitHub 도구 우선순위**: 모든 GitHub 작업(Issue·PR·comment·sub-issue·repo file write)은 `mcp__github__*` 도구 우선 사용. `gh` CLI는 MCP 미커버 영역(`milestone CRUD` / `Discussions` / `GraphQL` / `label 부트스트랩 스크립트`)에서만 fallback. MCP 미노출 시 gh 로 즉시 우회 금지 — 사용자에게 `/mcp` 재인증 요청 후 대기.

**필수 플러그인 (8종)**:
- `codeforge-{review,pmo,requirements,develop,design}@mclayer` — 5 lane plugin (codeforge-test deprecated — CFP-317 / ADR-048)
- `codex@openai-codex` — CodexReviewAgent + codex CLI dependency
- `superpowers@claude-plugins-official` — 17 lane agent × 8 skill 호출 (SSOT: [`docs/superpowers-integration.md`](docs/superpowers-integration.md))
- `github@claude-plugins-official` — GitHub MCP 도구 노출

**필수 CLI (2종)**: `codex`, `gh`. (CFP-59 / ADR-019 → ADR-022 (Deprecated by CFP-134 / ADR-035) — Gemini CLI 의존 제거. ad-hoc Sonnet / Codex 호출 = Claude Code Agent tool runtime / codex CLI, 외부 auth 무관. `gemini` CLI 가 다른 용도로 설치되어 있으면 unset / removable optional.)

**권장 플러그인 (4종, 미설치 시 권유만)**: `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

확인·자동복구·blocking-wait 절차 SSOT: [playbook §1.1](docs/orchestrator-playbook.md) checklist 0번 (MCP `ToolSearch` 노출 / settings.json 토글 / `/mcp` 재인증·`/plugins install` 요구 / consumer `.github/` 6 workflow + 3 forms + CODEOWNERS 부재 알림 / **codeforge plugin family version drift 검사 — CFP-262 / [ADR-037](docs/adr/ADR-037-plugin-version-bump-rule.md)**: MAJOR drift = hard-stop blocking, `bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-version-drift.sh`).

## Development Agent Team

Wrapper agent **0개** (ζ arc 완료, [ADR-009](docs/adr/ADR-009-wrapper-only-decomposition.md)). Orchestrator (top-level Claude 세션) 가 6 lane plugin 의 agent 를 spawn.

| Lane | Plugin | Agent count | SSOT |
|---|---|---|---|
| 요구사항 | codeforge-requirements | 4 (PL + DomainAgent + RequirementsAnalyst + Researcher) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/CLAUDE.md) |
| 설계 | codeforge-design | 8 (PL + ArchitectAgent chief + 6 deputy) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
| 설계리뷰 / 구현리뷰 / 보안테스트 | codeforge-review | 5 (3 PL + 2 worker) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) |
| 구현 | codeforge-develop | 5 (PL + QADev + 3 role:dev core) + preset/overlay 동적 | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-develop/blob/main/CLAUDE.md) |
| Cross-cutting | codeforge-pmo | 2 (PMOAgent + GitOpsAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) |

각 lane plugin 의 agent 역할·동작은 해당 plugin CLAUDE.md SSOT. 본 표는 composition map 만.

**Lane plugin lifecycle**: 신규 추가 / deprecate / rename 절차는 [ADR-023](docs/adr/ADR-023-lane-plugin-lifecycle.md). Marketplace sibling sync ([ADR-016](docs/adr/ADR-016-marketplace-registration-policy.md)) 와 align — CFP-50 (parity CI, follow-up) 가 자동 검증.

**Agent model tier 정책**: agent file `model:` field 의 Opus / Sonnet / Haiku 분류 기준 + 신규 agent 도입 / 기존 model 변경 시 ADR 의무 SSOT = [ADR-042](docs/adr/ADR-042-agent-model-selection-policy.md). 핵심 원칙: "Sonnet 으로 fully cover 가능 = role 재정의 시그널". ResearcherAgent 의 mandate (Concept formulation + Deep exploration + Requirement reshape) 와 Opus tier rationale 은 [ADR-046](docs/adr/ADR-046-researcher-role-redefinition.md) SSOT.

**주체 명칭**: **Orchestrator** = 최상위 Claude 세션 (모든 Agent 툴 스폰, 토큰 예산 소유) · **(Human) 사용자** = 인간 행위자 · **Cross-cutting** = 모든 레인에 걸쳐 작동하는 에이전트 (PMOAgent).

리뷰 워커 통합 근거: [ADR-001](docs/adr/ADR-001-review-agent-unification.md) (3 lane × 2 vendor → 2 lane-agnostic worker). [Inter-plugin Contract `review_verdict`](docs/inter-plugin-contracts/review-verdict-v2.md) versioning: [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md).

> **(선택) Stage 0 — pre-Issue brainstorming**: 비-trivial Story 는 `codeforge:brainstorm` (codeforge 프로젝트) 또는 `superpowers:brainstorming` (generic) 으로 사전 scope 정리 후 Issue Form 제출 권장 ([ADR-034 + Amendment 1](docs/adr/ADR-034-pre-issue-brainstorming-stage.md) · [playbook §1.2.0](docs/orchestrator-playbook.md)). `codeforge:brainstorm` = Requirements 에이전트 4종 병렬 컨텍스트 + scope_manifest 초안 자동 생성 (opt-in Phase 0). CI 강제 없음.

## 레인 5개 · 단계 정의

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → [CI gate]
```

모든 Story는 **full 5 레인 + CI gate** 통과. Fast-path 없음 (단 **Hotfix 경로** 2종은 예외 — 운영 장애 대응, 사후 감사 의무. 상세는 [`docs/hotfix-playbook.md`](docs/hotfix-playbook.md) — CFP-93 분리, mctrader debut audit 까지 사용 사례 0). **CI gate** = 구현 리뷰 PASS 후 Orchestrator가 `gh pr checks <PR_NUMBER> --watch`로 GitHub CI 결과 polling (최대 30분 timeout). PASS 시 merge gate 진입 (`lanes.security_ai: true` consumer는 SecurityTestPL spawn 추가). FAIL 시 DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → FIX loop (CFP-317 / ADR-048).

**Story flow (default — single-repo Story 또는 Epic 외 1 child Story)**: **1 Story = 2 PRs**
- **Phase 1 PR** (요구사항 + 설계 + 설계리뷰 lane): `docs/stories/<KEY>.md` §1-7 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md`. **(internal-docs SSOT 적용 시, ADR-013 dogfood-out + amendment)**: change-plan 위치는 `<internal-docs-clone>/<plugin-folder>/change-plans/<slug>.md`. Codeforge family / dogfood Story 의 경우 본 path override. 또한 doc-only Story (예: ADR carrier 가 architecture decision SSOT 인 경우) 는 **별도 change-plan 면제** — ADR 가 §3 도입할 설계 SSOT 역할 충족 (ADR-013 정합).
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane): `src/**` + `tests/**` + `docs/stories/<KEY>.md` §8-11 append

**Epic flow (cross-repo 또는 multi-Story Epic)** — **1 Epic = Phase 1 doc PR + N implementation PRs + Phase N+1 close PR** (N=3~5 일반적, mctrader 데뷔 audit Issue #181 P1-3, CFP-82):
- **Phase 1 PR** (hub / owner repo): Epic doc + N child Story stub + Codex 7-area review aggregate
- **Phase 2 ~ Phase N PR**: 각 child Story 의 implementation. **Joint-phase narrow form 허용** (단일 child Story 가 1 phase 안에서 multi-repo joint PR 보유 가능, ADR-020 Amendment 1 §결정 9 — 예: MCT-26 = data#1 + engine#1)
- **Phase N+1 close PR** (hub / owner repo): `EPIC-RESULTS-<KEY>.md` artifact + Epic Issue close
- Mid-Phase **spec amendment PR** 가능 (Codex push-back 발견 시 — 예: mctrader-hub PR #72)

**Cross-repo Epic** (mctrader 등 multi-repo consumer) — **Centralization mode 의무 결정** (ADR-020 Amendment 1 / CFP-81):
- **Mode A (repo-local, ADR-020 v1 default)**: 각 작업 repo 가 자체 Story
- **Mode B (hub-centralized)**: 1 hub repo 가 모든 child Story (mctrader 패턴)
- parent Epic Issue + child Story (per mode) + `epic_dependencies` graph + Change Plan §3 contract pin + Mixed-mode 금지. 상세 [ADR-020](docs/adr/ADR-020-cross-repo-epic-pattern.md), playbook §3.4.

**레인 진입 전 Preflight 체크 의무** — 각 레인 진입 직전 Orchestrator가 3개 체크 수행 (phase 라벨 정합 / docs file 선행 섹션 / 외부 의존성 가용). FAIL 시 block+report. 상세는 playbook §3B.

| 레인 | 진입 트리거 | 1차 self-write target | FIX max |
|---|---|---|---|
| 요구사항 | story-init.yml Action (Issue Forms 제출) | §1·§2·§5·§6 (RequirementsPL + 3 sub) | — |
| 설계 | RequirementsPL verdict | §3·§7·§11 + change-plan + ADR-NNN (ArchitectAgent + 6 deputy) | — |
| 설계 리뷰 | ArchitectAgent verdict | §9 (DesignReviewPL Claude+Codex 종합) + `gate:design-review-pass` | 3 |
| 구현 | 설계 리뷰 PASS | §8·§8.5 + Phase 2 PR 첫 commit (DeveloperPL + QADev + N role:dev) | — |
| 구현 리뷰 | DeveloperPL ready | §9 (CodeReviewPL Claude+Codex 종합) | 3 |
| CI gate | 구현 리뷰 PASS | (Orchestrator inline `gh pr checks` polling — 30분 timeout) | ∞ |
| 보안 테스트 **(opt-in: lanes.security_ai: true)** | CI gate PASS | §9 (SecurityTestPL 2-layer: GitHub native + Claude+Codex) + `gate:security-test-pass` (+ `gate:live-entry-pass` if Live touching, ADR-030) | ∞ |

세부 spawn sequence · branch logic · FIX 진단 흐름 SSOT: [playbook §3](docs/orchestrator-playbook.md) + 각 lane plugin CLAUDE.md.

## 오케스트레이션 규칙

> **Orchestrator 정책 적용 범위 (normative)**: 본 CLAUDE.md 및 playbook 의 모든 Orchestrator 행동 규칙 (lane spawn 방식·stop discipline·진행 시각화·GitHub 도구 선택·통신 표준·fact verification 등) 은 **wrapper plugin 자체 작업과 모든 consumer project 에 동일 적용**. Consumer overlay (`.claude/_overlay/`) 는 정책을 축소할 수 없고 확장만 가능.

> **behavioral directive → memory 금지 (normative)**: 사용자가 Orchestrator 행동 directive 를 내릴 때, 해당 규칙을 personal memory file 에 저장하는 것으로 갈음하지 않는다. 대신 **즉시 CFP 제안** 후 playbook / CLAUDE.md / consumer-guide 에 반영해야 한다. Memory = ephemeral + consumer 비전파 + single-session scope = structural enforcement 불가. 예외 없음.

> **Orchestrator 행동 SSOT**: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) — 세션 생명주기, 스폰 프롬프트 템플릿, 병렬 스폰 판단, FIX 상태 머신, 세션 재개 복원, 토큰 예산.

**Default subagent context (수정 작업) — codeforge 정책 (ADR-039)**: codeforge 를 이용한 **수정 작업** 진행 중, Orchestrator 는 모든 work 을 `Agent` tool spawn (subagent) 으로 수행한다. inline 수행 (Orchestrator turn 안에서 Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 직접 호출) 은 **Inline whitelist 4-entry** (사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report — 상세 [playbook §3.0](docs/orchestrator-playbook.md)) 외 영역에서 금지. "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 자체 금지 — branch logic 제거 = ADR-025 §결정 7 `policy_violation_subdecision` 발화 채널 차단. 정책 SSOT [ADR-039](docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) (amends ADR-009). Skill 호출 = Inline (file write 아님, meta wrapper) — Skill 내부 individual tool call (Read/Edit/Write/mcp__github__\*/Agent/Bash) level 에서 spawn 분류 발동. Dialog turn separation 의무 (Story §2 AC-5): 사용자 dialog 와 dialog 직후 state change 는 별도 turn / message — 한 메시지 안 inline write + dialog 동시 수행 금지.

**Default subagent context 의 codeforge 정책 결정** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 미설정 시) — 하위 에이전트는 Agent 툴 사용 불가 (재귀 스폰 금지 — platform inherent), 서브에이전트 간 직접 통신 불가 (codeforge 정책 — agent teams enabled context 별도), 서브에이전트 one-shot (codeforge 정책). 모든 스폰은 최상위 Claude.

**Agent teams enabled context 별도** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, CFP-137 / [ADR-044](docs/adr/ADR-044-phase-scoped-sequential-team.md) 적용 후) — sibling teammate 간 SendMessage 사용 가능 + Phase-scoped sequential team + Adversarial debate (review lane) + Cross-layer (TEAM-DEVELOP) 패턴 활성. 단 (a) 재귀 spawn 금지 (platform inherent — Lead 와 teammate 모두), (b) nested team 금지 (no team-of-teams), (c) one-team-per-lead 강제 — 다음 lane TeamCreate 전 현 team `TeamDelete()` 의무. team-spec yaml 7종 (`templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml`) + hook 3종 sample (`templates/agent-teams-hook-samples/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample`) SSOT. review lane Codex worker `dispatch_mode: user_request_only` (사용자 ad-hoc 요청 시에만 활성, ADR-022 Deprecated 정합). env=0 fallback = ADR-039 default subagent context (one-shot Agent tool, 본 단락 무효화). 상세 SSOT [ADR-044](docs/adr/ADR-044-phase-scoped-sequential-team.md) + [domain-knowledge entry](docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md) + [playbook §3.6-§3.9](docs/orchestrator-playbook.md).

**Wrapper 위임 패턴** (모든 행위 = ADR-039 default subagent spawn — 위 "Default subagent context (수정 작업)" 단락 정합):
- 컨텍스트 전달: `docs/stories/<KEY>.md` SSOT, agent 프롬프트는 path 주입, 본문은 agent self-fetch — Context Packet / §0 Live Progress / Project Config Packet 상세는 [playbook §12·§14](docs/orchestrator-playbook.md)
- Never-skippable: 각 lane 진입 시 Orchestrator 가 해당 lane plugin PL agent 1개만 spawn — sub-agent fan-out (수·역할·non-skippable 매트릭스) 상세는 각 lane plugin CLAUDE.md SSOT
- **Lane-spawn evidence (ADR-031, CFP-126)**: 매 lane spawn 시 Story §14 Lane Evidence row append (start: spawn 직전, end: return 직후 outcome 채움) + Phase 2 PR description `## Lane evidence` 블록 의무. `lane-evidence-check.yml` workflow + `scripts/check-lane-evidence.sh` lint 가 cross-validate. Bypass = `BYPASS_LANE_EVIDENCE=1` + `BYPASS_LANE_EVIDENCE_REASON` env. Effective date = ADR-031 Accepted 후 신규 Phase 2 PR 부터 (retroactive 미처리). `.claude-work/progress/<KEY>.md` (CFP-20 NG6 cache) 와 분리 — §14 가 SSOT.
- Track 병렬 (R7 설계리뷰 PASS 시): Track A (DesignReviewPL merge gate) ∥ Track B (DeveloperPL Phase 2 PR 준비) — 상세 [playbook §3.1]
- **Worktree dispatch (CFP-136 / [ADR-040](docs/adr/ADR-040-worktree-convention.md))**: 매 lane spawn 시 isolated working directory 보장. base = `${HOME}/.claude/worktrees/<repo-name>/<branch-flat>`, hierarchical branch (ADR-024 Amendment 1) `cfp-NNN[/<lane>[/<sub>]]`, lifecycle (`on_team_create_pre|post` / `on_team_delete_pre|post` / `on_session_start` / `on_story_close`). 5 script (`templates/scripts/worktree-{create,merge,prune,path-util}.sh` + `check-worktree-stale.sh`) + SessionStart hook (`templates/.claude/hooks/SessionStart-codeforge-worktree-gc.json.sample`) — 7 days + origin absent stale 자동 prune. CFP-137 (agent teams) prerequisite + CFP-139 (GitOpsAgent) hook contract SSOT. Default subagent context (agent teams `=0`) 에서도 사용자 ad-hoc 호출 가능. 상세 [playbook §3.5](docs/orchestrator-playbook.md).
- **Worktree-first (normative — wrapper + all consumers, CFP-341)**: lane spawn·ad-hoc 구분 없이 모든 coding work 는 worktree 안에서 수행. `git checkout <branch>` 로 원본 working directory 직접 편집 금지. Story 시작 시 `bash templates/scripts/worktree-create.sh` 선행 의무. 상세 [playbook §3.0.10](docs/orchestrator-playbook.md).

**Parallel epic coordination (ADR-050)**: 복수 Orchestrator 세션 병렬 진행 시 충돌 조율 의무.

- **Epic Scope Manifest 작성 의무**: Phase 1 시작 시 Orchestrator가 Epic Issue body에 `<!-- scope_manifest -->` 블록 작성 (예상 변경 파일·ADR·CLAUDE.md 섹션 목록). GitOpsAgent가 이 블록을 파싱해 다른 open 에픽과 교집합 검사.
- **ADR 번호 예약**: ADR 필요 시 GitOpsAgent가 `docs/adr/ADR-RESERVATION.md` sequential append로 번호 클레임 (직접 번호 추측 금지).
- **Section 편집 정책**: `docs/parallel-work/section-ownership.yaml` 정의 섹션은 `parallel_edit` 정책 준수 (append-only / locked). locked 섹션 동시 수정 시 `merge-order` 조율 의무.
- **Merge 순서**: 낮은 CFP 번호 PR이 merge 우선. GitOpsAgent가 `merge-order:1/2` 레이블 자동 부여.

Scope Manifest 형식:
```yaml
<!-- scope_manifest -->
planned_adrs: [NNN]
planned_files:
  - path/to/file.md
planned_claude_md_sections:
  - "섹션명"
<!-- /scope_manifest -->
```

**Progress visualization via TodoWrite (ADR-038, CFP-274)**: TodoWrite 를 CFP-20 §14.7 render flow 의 3번째 channel 로 추가. 4 marker (⏳ 🔄 ✅ ❌) hierarchical (lane row + 2-space indent agent sub-row) 렌더 표준. ❌ 는 검출 lane 이 아닌 원인 lane 에 표시 (검출 lane 은 ✅ + content `FIX-N detected`). Single-Story 모드 (multi-Story 별도 CFP). Lane plugin 변경 0건 (Writer 단독 invariant 유지). multi-row in_progress 의도적 허용 (codeforge 병렬 agent 모델 — wrapper-specific deviation). 상세: [ADR-038](docs/adr/ADR-038-progress-visualization-todowrite.md), [playbook §14](docs/orchestrator-playbook.md).

### Sonnet Decider (Deprecated — CFP-134 / ADR-035, 2026-05-08)

**DEPRECATED**: Codex review / Sonnet decider 는 codeforge 1st-class component 가 아니라 **사용자 ad-hoc 도구**. codeforge 가 자동 invoke 하지 않음. 사용자 explicit request (e.g., "codex 와 opus 로 심층 리뷰 후 sonnet 으로 정리") 시에만 ad-hoc spawn. 이전 ADR-022 의 5 trigger 자동 발동 + 5-step protocol + decision-packet-v2.1 schema 무효. Architecture decision SSOT = [ADR-035](docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md) (Epic CFP-134). 상세 deprecation context = [CFP-134 Epic spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md).

#### review-verdict v3 → v4 cutover 완료 (CFP-137 / ADR-044)

ADR-022 deprecate 후 `review-verdict-v3` contract (canonical: codeforge-review plugin / sibling: 본 wrapper repo) 의 Sonnet decider 영역 — `decision_state` enum 의 8 state, `sonnet_final_status`, `decider_decision_ref`, `write_errors` step Sonnet semantics, 5-step Orchestrator algorithm — **review-verdict v4 (CFP-137 / ADR-044 §결정 4) 으로 정식 제거**. v4 = `pl_recommendation` 자체가 final verdict (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE), 4-step linear path. 신규 field `worker_dialog_rounds: int >= 0` 추가 (Adversarial debate measurable verification, ADR-044 §결정 5).

**Cutover (CFP-137 wrapper Phase 1 PR merge 시점)**:
- v3 sibling (wrapper repo) `status: Active → Archived` 동기 갱신.
- v4 sibling (wrapper repo) `status: Active` 신설.
- canonical sync (codeforge-review plugin) = sibling sync follow-up PR (ADR-010 §단계 절차 정합 — wrapper-first).
- 즉시 cutover (consumer scope 0건, mctrader debut audit 까지 backward compat 면제).
- v3 본문은 archive reference 로 보존 — 6 CFP 무사고 후 별도 cleanup CFP 에서 file 삭제 (v2 deprecate 패턴).

상세: [`docs/inter-plugin-contracts/review-verdict-v4.md`](docs/inter-plugin-contracts/review-verdict-v4.md) (wrapper sibling).

### FIX 루프

**판정 SSOT** = codeforge-review [`templates/review-pl-base.md`](https://github.com/mclayer/plugin-codeforge-review/blob/main/templates/review-pl-base.md) §3 (severity 종합·dedup·판정). Contract surface = [`review-verdict-v4`](docs/inter-plugin-contracts/review-verdict-v4.md) `pl_recommendation` (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE) — CFP-137 / ADR-044 cutover 후. v3 archived 참조: [`review-verdict-v3`](docs/inter-plugin-contracts/review-verdict-v3.md).

**트리거**: 설계 리뷰 FIX → ArchitectPLAgent 회귀. 구현 리뷰·구현 테스트·보안 테스트 FAIL → DeveloperPL 1차 진단 + ArchitectPLAgent 최종 판정 (parallel diagnosis).

**원인 판정 최종 결정자** (CFP-134 / ADR-035 정정 후): PL 이 자기 lane review-verdict 의 final pl_recommendation 작성. Sonnet decider 자동 발동 무효 (ADR-022 Deprecated — CFP-134). FIX root cause 원인 판정 (설계 vs 구현) 은 ArchitectPLAgent 가 DeveloperPL 1차 진단 받은 후 최종 결정. 사용자 explicit request 시에만 ad-hoc Sonnet 호출 가능.

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 ([fix-event-v1](docs/inter-plugin-contracts/fix-event-v1.md) contract, CFP-32 monopoly). GitHub Issue 라벨은 보조 (fix-ledger-sync.yml Action mirror).

**§10 FIX Ledger 스키마**:
```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | ISO8601 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
```

상세 룰 (max FIX 횟수 / RESET marker / parallel diagnosis / mechanical fast-path) 은 [playbook §6](docs/orchestrator-playbook.md) SSOT.

### 원인 판정 decision table (설계 리뷰·구현 리뷰·구현 테스트·보안 테스트 FAIL 시)

**프로세스**: 설계 리뷰 FIX는 DeveloperPL 개입 없이 ArchitectPLAgent 직접 회귀. 구현 리뷰·구현 테스트·보안 테스트 FIX는 DeveloperPL 1차 원인 진단 → Orchestrator 경유 → ArchitectPLAgent 최종 판정. 모든 경우 evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무. Story file §10 FIX Ledger에 누적.

| Failure 유형 | 1차 가정 | 설계 원인 escalate 조건 |
|---|---|---|
| **설계 리뷰 P0 §7 누락** | **설계** | 항상 설계 (ArchitectAgent chief author 미흡) |
| Unit test FAIL | 구현 | 테스트 사양이 Change Plan 계약과 불일치 |
| Integration test FAIL | 구현 | 모듈 경계·계약 위반 |
| Infra test FAIL | 구현 | 배포/환경 요구 Change Plan 누락 |
| 성능 test FAIL | **설계** | 단순 최적화로 해결되면 구현 |
| Code review P0 보안 | 구현 | trust boundary 설계 오류 |
| Code review P0 아키텍처 | **설계** | 레이어·의존성 방향 위반 |
| **Code review P1 품질 (local)** | 구현 | 단일 파일·함수 내 품질 (naming, 작은 중복, 가독성) |
| **Code review P1 품질 (boundary)** | **설계** | 모듈 경계·인터페이스·패턴 일관성 (여러 파일 공통 이슈, 설계 지침 부재) |
| **보안 테스트 (opt-in — security_ai:true) P0 injection·credential hardcode** | 구현 | 코드 단위 결함 |
| **보안 테스트 (opt-in — security_ai:true) P1 암호학 오용·CVE** | 구현 | 코드 수정·버전 업그레이드로 해결 |
| **보안 테스트 (opt-in — security_ai:true) P1 boundary 권한 일관성** | **설계** | 여러 파일·레이어 공통 지침 부재 |
| **보안 테스트 (opt-in — security_ai:true) P0 trust boundary 위반** | 구현 | §7.1에 boundary 부재·모순 또는 §7.1과 코드 boundary 불일치 → 설계 |
| **보안 테스트 (opt-in — security_ai:true) P0 auth/authz 결함** | 구현 | §7.3 인증·권한 모델 자체 결함 → 설계. 모델은 맞으나 구현 결함 → 구현 유지 |
| **구현 테스트 Migration FAIL · data integrity 위반 · rollback 실패** | 구현 | §11.1-§11.5 부재·모순 (schema 영향 누락 / Migration 전략 부재 / Rollback 경로 부재 / invariant 정의 부재) → 설계. 모델은 맞으나 script 결함 → 구현 유지 |
| **§7.4 DR/disconnect cascade FAIL** | 구현 | §7.4 boundary 부재·모순 → 설계 |
| **§7.4 Rate limit / IP ban** | 구현 | §7.4 quota·throttling 정책 부재 → 설계 |
| **§7.4 Env isolation 위반 (live ↔ staging 누설)** | 구현 | §7.4 isolation 모델 부재 → 설계 |
| **§7.4 Clock skew FAIL (CONDITIONAL active)** | 구현 | §7.4 skew tolerance 부재·N/A 모순 → 설계 |
| **§11 Idempotency 위반 (CONDITIONAL active)** | 구현 | §11 invariant 부재·N/A 모순 → 설계 |
| **§8.5 Cache / state drift (long-running)** | 구현 | §8.5.1 long-running invariant 정의 부재 또는 §7.4.1 DR boundary 부재 → 설계 |
| **§8.5 Unbounded background accumulation** | 구현 | §7.4.4 rate limit / quota 정책 부재 또는 §8.5.1 worker queue bound 정의 부재 → 설계 |
| **§8.5 Restart recovery loss** | 구현 | §7.4.5 env isolation 모델 부재 또는 §11.6 idempotency CONDITIONAL active 인데 spec 부재 → 설계 |
| **§8.5 Idempotency replay failure (§11.6 active 시)** | 구현 | §11.6 idempotency invariant 정의 부재 (§11.6 active 인데 §8.5.3 cross-ref 깨짐) → 설계 |
| **Real-funds 손실 (Live trade) — CONDITIONAL Live touching Story** | 구현 | §7.4 live exposure limit / §11 ledger invariant / first-trade cap 부재 시 → 설계 |
| **Kill switch 자동 발동 실패 (CONDITIONAL Live touching Story)** | 구현 | §7.4 trigger condition (drawdown / max_exposure / rate_limit / KRW_drift) 부재 시 → 설계 |
| **Kill switch manual override 실패 (CONDITIONAL Live touching Story)** | 구현 | operator-action-v1 schema / protocol 부재 시 → 설계 |
| **Partial fill reconciliation 실패 (CONDITIONAL Live touching Story)** | 구현 | §11 partial fill invariant (8-state lifecycle drift / fee 정합 / cancel race) 부재 시 → 설계 |
| **Fee handling drift (CONDITIONAL Live touching Story)** | 구현 | §11 fee accounting invariant (fee_actual ≠ fee_expected drift threshold) 부재 시 → 설계 |
| **Dockerfile build FAIL (CI) (CFP-128 / ADR-033)** | 구현 | Change Plan §3 image strategy / multi-stage 부재 → 설계 |
| **Container image CVE P0 (trivy) (CFP-128 / ADR-033)** | 구현 | base image 자체 stale (4y old, EOL) → 설계 (image base 결정 재검토) |
| **hadolint P1 violation (CFP-128 / ADR-033)** | 구현 | (단일 파일) — 항상 구현 |
| **Compose service health check FAIL (CFP-128 / ADR-033)** | 구현 | §7.4 health check policy 부재 → 설계 |
| **Container secret 누설 (env / log / image layer) (CFP-128 / ADR-033)** | 구현 | §7.5 secret mount 전략 부재 → 설계 |
| **Network mode 위반 (internal service host network 노출) (CFP-128 / ADR-033)** | 구현 | §7.1 network boundary 부재·모순 → 설계 |
| **§7.4 Container restart loop / volume mount race (CFP-128 / ADR-033)** | 구현 | §7.4 restart policy / volume invariant 부재 → 설계 |

**P1 품질 local vs boundary 판정 기준**:
- **local**: finding이 1개 파일 또는 1개 함수 범위에 한정, 설계 결정과 무관한 개별 구현 결함
- **boundary**: finding이 여러 파일·계층에 걸침, 또는 Change Plan에 "이 경계·패턴 어떻게 가야 하는지" 지침이 부족해서 발생한 이슈
- DeveloperPL이 1차 진단 시 이 분류를 포함 → ArchitectPLAgent 최종 판정

- **설계 원인 판정 시**: Change Plan 갱신 (특히 §3 도입할 설계 / §6 리팩터링 선행 / §7 보안 설계 / §8 Test Contract 중 해당 항목) → Phase 1 follow-up PR → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, Phase 2 PR commit append → 구현 리뷰 재실행

### Design / Code / Security 리뷰 책임 매트릭스 (중복 방지)

네 레인의 체크 항목이 겹치지 않도록 분담. 한쪽에서 커버된 항목은 다른 쪽에서 재검토하지 않음.

**review verdict write 책임 (CFP-134 / ADR-035 정정 후, Stage 0 spec §3.5 verbatim)**: review-verdict v3 schema 의 final gate write (Story §9 / GitHub comment / gate label / phase transition) = **Orchestrator self-write** (PL 은 lane synthesis 후 `pl_recommendation` 만 작성, Orchestrator 가 받아 final write 수행). Sonnet decider 자동 발동 무효 (ADR-022 Deprecated — CFP-134). 사용자 explicit request 시에만 ad-hoc Sonnet 호출 가능.

| 체크 항목 | DesignLane | DesignReview | CodeReview | SecurityTest (opt-in) |
|-----------|:----------:|:------------:|:----------:|:------------:|
| Change Plan 완결성(§1-10 섹션 존재) | — | ✅ | — | — |
| ADR 정합성(§3·§7 위반 여부) | — | ✅ | — | — |
| CodebaseMapper ↔ Refactor 균형 | — | ✅ | — | — |
| API 계약 일관성 (라우트·스키마·타입) | — | ✅ | — | — |
| §8 Test Contract 타당성 | — | ✅ | — | — |
| **§8.5 Stateful / restart invariant 정의** | ✅ TestContractArch | ✅ DesignReview (감사 — applicability 표 valid) | — | StatefulTestAgent (검증) |
| **§8.5 누락 / vague N/A 사유** | — | ✅ **P0 차단** | — | — |
| 성능 baseline §8.3 프로토콜 타당성 | — | ✅ | — | — |
| **§7 Trust boundary 정의** | ✅ | (감사) | — | (검증) |
| **§7 Threat model (STRIDE-LITE)** | ✅ | (감사) | — | — |
| **§7 Auth/Authz 모델 결정** | ✅ | (감사) | — | (검증) |
| **§7 민감 데이터 분류·흐름** | ✅ | (감사) | — | (검증) |
| **§7 위협↔완화 매핑** | ✅ | (감사) | — | (검증) |
| **§7 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§11 Schema 변경 영향** | ✅ | (감사) | — | (검증) |
| **§11 Migration 전략** | ✅ | (감사) | — | (검증) |
| **§11 Rollback 경로** | ✅ | (감사) | — | (검증) |
| **§11 Data integrity invariant** | ✅ | (감사) | — | (검증) |
| **§11 Backfill / 기존 데이터 처리** | ✅ | (감사) | — | (검증) |
| **§11 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§7.4 DR / failover 경로** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 Cancel-on-disconnect** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 Clock sync (CONDITIONAL)** | ✅ OpRiskArch | (감사·N/A 사유) | — | (검증) |
| **§7.4 Rate limit / quota** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 Env isolation** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§11 Idempotency (CONDITIONAL)** | ✅ DataMigrationArch | (감사·N/A 사유) | — | — |
| **§11 Idempotency 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| 코드 ↔ Change Plan 변경 계획 준수 | — | — | ✅ | — |
| 코드 스타일·네이밍·가독성 | — | — | ✅ | — |
| 테스트 코드 품질 (커버리지·경계·mock 경계) | — | — | ✅ | — |
| 런타임 오류 가능성 (null·타입·race 일반) | — | — | ✅ | — |
| 레이어 경계·의존성 방향 준수 | — | 부분(패턴 수준) | 주(실구현) | — |
| Impl Manifest §8.5 ↔ 실제 파일 일치 | — | — | ✅ | — |
| Injection 공격 표면 (SQL·Command·Template·NoSQL) | — | — | — | ✅ |
| **Trust boundary 위반 (외부 입력 검증 누락)** | (설계) | — | — | ✅ (코드 준수 검증) |
| Credential / secret 노출 (hardcoded·log·error) | — | — | — | ✅ (1차: Secret Scanning) |
| **Auth / 세션 결함 (CSRF·session fixation·JWT 무결성)** | (설계) | — | — | ✅ (코드 준수 검증) |
| 암호학 오용 (weak algo·nonce reuse·ECB·hardcoded key) | — | — | — | ✅ |
| **민감 데이터 유출 (PII·금융·헬스 데이터 로그·응답)** | (설계 분류) | — | — | ✅ (런타임 노출 검증) |
| 의존성 CVE 스캔 | — | — | — | ✅ (1차: Dependabot) |
| 정적 분석 결함 | — | — | — | ✅ (1차: CodeQL) |
| 설정·배포 보안 (default credential·open port·TLS) | — | — | — | ✅ |
| Race / TOCTOU 보안 취약 | — | — | — | ✅ |
| **Container image base / multi-stage build 전략 (CFP-128 / ADR-033)** | ✅ (Refactor + OpRiskArch) | ✅ (감사) | (구현 준수) | — |
| **Dockerfile syntax + best practice (CFP-128 / ADR-033)** | — | — | — | ✅ (1차: hadolint) |
| **Container image CVE / misconfig (CFP-128 / ADR-033)** | — | — | — | ✅ (1차: trivy) |
| **Compose service definition / health check / dep order (CFP-128 / ADR-033)** | — | (감사) | ✅ | — |
| **Container network mode / port exposure (CFP-128 / ADR-033)** | ✅ SecurityArch | (감사) | — | ✅ (코드 준수 검증) |
| **Container secret / env mount 전략 (CFP-128 / ADR-033)** | ✅ SecurityArch | (감사) | — | ✅ (런타임 노출 검증) |
| **§7.4 Container restart policy / volume DR / health check tuning (CFP-128 / ADR-033)** | ✅ OpRiskArch | (감사) | — | (검증) |

> **DesignLane vs SecurityTest**:
> - DesignLane(SecurityArch) = "**어디에 boundary가 있어야 하는가**" — 설계 결정 (예방)
> - SecurityTest = "**코드가 그 boundary를 지키는가**" — 구현 검증 (검출)
> - 두 lane이 같은 카테고리(예: trust boundary)를 다루지만 **시점이 다름**: 설계 결정 vs 코드 준수
> - DesignReview는 "§7 보안 설계 자체의 완결성"을 감사 (추가 보안 검토 X — SecurityArch 산출물이 충분한가만)

- **DesignLane**: 대상은 설계 단계의 보안 결정 (SecurityArchitectAgent 산출물 → ArchitectAgent §7 반영). trust boundary·threat model·auth model·민감 데이터 흐름 정의
- **DesignReview**: 대상은 문서(Change Plan + ADR). 실구현 코드 미검토. §7 보안 설계 완결성 감사
- **CodeReview**: 대상은 코드(src·config·deploy·tests). 일반 품질·런타임 결함·테스트 품질 중심. 보안은 SecurityTest가 깊게 검증
- **SecurityTest**: 대상은 코드 + 인프라 + 의존성. 보안 카테고리 전담. 1차 layer는 GitHub native 도구(Dependabot/CodeQL/Secret Scanning), 2차 layer는 Claude/Codex 통합 워커(lane=security packet)
- 중복 지적 발생 시 해당 레인의 ReviewPL이 dedup → severity 높은 쪽 채택

> **Debut-audit measurable signal**: 본 매트릭스의 ✅ 0 개 또는 ≥2 개 row 가 [ADR-021](docs/adr/ADR-021-phase-gap-measurable-signal.md) R4 (Responsibility leak) detection source.

### Deputy mandate 매트릭스 (codeforge-design lane) — 6 permanent + 2 CONDITIONAL

ADR-014 + ADR-012 §3 4번째 SSOT 예외. design lane 의 deputy (CFP-46 OperationalRiskArchitect 신설 + CFP-77 LiveOps + LiveOrdering CONDITIONAL 추가) 가 §7 / §11 / §13 sub 별로 owning 하는 범위 명시 — H17 책임 분쟁 차단.

| §7 / §11 / §13 sub | CodebaseMapper | Refactor | SecurityArch | **OpRiskArch** | TestContractArch | DataMigrationArch | **LiveOps** (CONDITIONAL) | **LiveOrdering** (CONDITIONAL) |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| §7.1 Trust boundary | — | — | ✅ **(+container network mode / secret mount — CFP-128)** | (consult) | — | — | (consult Live API) | — |
| §7.2 Threat model | — | — | ✅ | — | — | — | — | — |
| §7.3 Auth/authz | — | — | ✅ | — | — | — | (consult operator approval) | — |
| **§7.4 DR / disconnect / rate limit / env isolation** | — | — | (consult) | **✅ (+container restart policy / volume DR / health check / network mode — CFP-128)** | — | — | (consult Live failure) | (consult exchange rate-limit) |
| **§7.4 Clock sync (CONDITIONAL)** | — | — | (consult) | **✅** | — | — | — | — |
| §7.5 민감 데이터 분류 | — | — | ✅ **(+container secret mount / image layer 누설 — CFP-128)** | — | — | — | (consult API key) | — |
| §7.6 위협↔완화 매핑 | — | — | ✅ | (DR↔failover consult) | — | — | (consult kill switch) | — |
| **§11 Idempotency (CONDITIONAL)** | — | — | — | (consult) | — | **✅** | — | (consult order idempotency) |
| §11 Schema/Migration/Rollback | — | — | — | — | — | ✅ **(+DB container volume / data persistence — CFP-128)** | — | — |
| **§11 Ledger reconcile / partial fill / fee invariant (CONDITIONAL Live)** | — | — | — | (consult) | — | (consult §11) | — | **✅** |
| **§8.5 Stateful / restart invariant** | — | — | — | (consult §7.4 짝) | **✅** | (consult §11.6 짝) | — | (consult order replay) |
| **§13 Live Operational Discipline (CONDITIONAL Live touching)** | — | — | (consult §7.5) | (consult kill switch) | — | (consult §11) | **✅** | (consult §11 ledger) |

✅ = primary owner / (consult) = secondary input.

**§3 chief author 수준 cell annotation (CFP-128 / ADR-033)**: 본 매트릭스 row 외에, ArchitectAgent (chief author) 의 §3 도입할 설계 책임에 **image base / multi-stage 전략** 결정 추가 (Refactor consult). 새 row 추가 안 함 — chief author 의 cross-cutting 책임 cell annotation 만.

**CONDITIONAL deputy 활성 정책 (CFP-77)**:
- **LiveOpsDeputy + LiveOrderingDeputy** = Live touching Story 만 active (real funds / live exchange API / production credential / live order placement 중 하나 이상 touching). Backtest/Paper-only Story = 미spawn (token / token cost 절약).
- ArchitectPLAgent 가 Story 의 §13 CONDITIONAL trigger 검토 후 6 → 8 deputy parallel spawn 결정.
- 활성 시: ArchitectAgent chief 가 8 deputy 산출물 통합 (4-way 이념 대립 + production-readiness 단일 축 + Live operational 단일 축 + Live ordering 단일 축).

§7.4 schema 자체는 codeforge-design plugin SSOT (OperationalRiskArchitectAgent agent file). §13 / Live ordering schema 는 codeforge-design plugin agent file (LiveOpsDeputy / LiveOrderingDeputy — CFP-77 follow-up agent file CFP). wrapper 는 본 매트릭스만 SSOT 보유 ([ADR-014](docs/adr/ADR-014-operational-risk-ssot-distribution.md), CFP-77 amendment).

**PMOAgent (Cross-cutting)** — Epic 창설 / Story 완료 회고 (**자동 의무 trigger** — Phase 2 PR merge 후 5분 grace, CFP-138 / [ADR-045](docs/adr/ADR-045-story-retro-mandatory-trigger.md)) / 사용자 요청 시 spawn. 단일 Story lane 게이트 비개입. 상세: [codeforge-pmo CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md).

### Lane plugin self-write boundary

`docs/**` + GitHub Issue/PR/comment + label 영역의 write 책임은 lane plugin 별로 분산. wrapper repo 자체에는 agent 0개 — Orchestrator 가 lane plugin 을 spawn 하면 lane plugin 이 자기 owner section 을 직접 write.

**Lane plugin owner path**:

| Lane plugin | docs/ self-write 영역 | GitHub self-write |
|---|---|---|
| codeforge-requirements | `docs/stories/<KEY>.md §2·§5·§6`, `docs/domain-knowledge/<area>/<topic>.md` | `[요구사항]` prefix comment, phase:요구사항→phase:설계 transition, Discussions Q&A routing |
| codeforge-design | `docs/stories/<KEY>.md §3·§7·§11`, `docs/change-plans/<slug>.md`, `docs/adr/ADR-NNN-<slug>.md` | `[설계]` prefix comment, phase:설계→phase:설계-리뷰 transition |
| codeforge-review (CFP-35 v2 — pre-CFP-61 history) | `docs/stories/<KEY>.md §9` (각 Review PL) | `[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]` prefix comment, gate:design-review-pass / gate:security-test-pass label, phase transition (review-verdict-v2). **(History only — CFP-61 부터 final §9 verdict + GitHub gate write 책임 Orchestrator 로 transfer)** |
| **codeforge-review (CFP-137 v4 — current SSOT, CFP-134 / ADR-035 정정 후)** | review-verdict-v4 packet 작성 (findings + `pl_recommendation`) — synthesis 만, Orchestrator 에 return. **final §9 verdict append + GitHub comment + gate label + phase transition 은 Orchestrator self-write** (Stage 0 spec §3.5 verbatim, ADR-022 Deprecated 후 Sonnet decider 자동 발동 무효) | (review-verdict 영역 GitHub write 는 Orchestrator) |
| codeforge-develop | `docs/stories/<KEY>.md §8·§8.5`, Phase 2 PR creation | `[구현]` prefix comment, phase:구현→phase:구현-리뷰 transition |
| codeforge-pmo | `docs/retros/<sprint>.md`, `docs/stories/<KEY>.md §11`, Epic Issue body, Milestone description | `[PMO]` prefix comment, Epic Milestone via gh api |

**Wrapper Orchestrator 단독 영역**:
- `docs/stories/<KEY>.md §10` FIX Ledger append (CFP-32 monopoly · `fix-event-v1` contract)
- **review-verdict 최종 write** (Story §9 append / GitHub comment / gate label / phase transition) — **CFP-134 / ADR-035 정정 후 (Stage 0 spec §3.5 verbatim)**: PL synthesis (findings + `pl_recommendation`) 만 lane plugin self-write 영역, **final §9 verdict append + GitHub comment + gate label + phase transition 은 Orchestrator self-write** (ADR-022 Deprecated 후 Sonnet decider 자동 발동 무효 — review-verdict v3 의 Sonnet 5-step 영역 NO-OP, v4 MAJOR bump 가 정식 제거 — CFP-137 / ADR-044 cutover 완료).
- general `docs/**` write (lane plugin owner 외)
- branch protection · CI workflow · cross-plugin schema templates

**4 single-owner doc** (CFP-26 Phase 0a 이후): `docs/{change-plans,adr,domain-knowledge,retros}/**` 는 owner agent direct write — lane plugin 의 ArchitectAgent / DomainAgent / PMOAgent 자기 owner path write.

문서화 표준 4 single-owner doc 템플릿은 [`templates/`](templates/) — change-plan / adr 현재 존재, domain-knowledge schema / retro schema CFP-27 신설. owner agent는 본인 owner path write 시 해당 템플릿 schema 준수 필수 — `scripts/check-write-permission-redistribution.sh` (CFP-26) + 향후 frontmatter/section schema lint (CFP-27)에서 강제.

자세한 owner path / mechanism / trigger 는 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 (codeforge-{review,pmo,requirements,test,develop,design}) 참조.

## Doc Location Registry (CFP-276 / ADR-041)

codeforge plugin 의 doc taxonomy (epic_results / story_file / adr / change_plan / retro / domain_knowledge / spec / plan / decision_packet / inter_plugin_contract) 위치 SSOT = [`docs/doc-locations.yaml`](docs/doc-locations.yaml). Human-readable mirror = [`docs/doc-location-registry.md`](docs/doc-location-registry.md) (auto-generated from yaml). Lint = [`scripts/check-doc-locations.sh --full`](scripts/check-doc-locations.sh) (CI required check, branch protection 5번째). 정책 SSOT: [ADR-041](docs/adr/ADR-041-doc-location-registry.md). 새 doc type 도입 / 기존 location 변경 시 yaml row 갱신만 → codeforge upgrade 자연스러운 reflection. EPIC-RESULTS 의 issue #276 SSOT 모순 (3 문서 disagree) 해소가 본 registry 도입 동인.

## Inter-plugin Contract (CFP-29 Phase 1 후 + CFP-42 sibling backfill)

codeforge core 가 외부 plugin과 통신할 때의 typed schema. wrapper repo 의 [docs/inter-plugin-contracts/](docs/inter-plugin-contracts/) 디렉터리는 두 종류 보유:

### kind:contract (typed inter-plugin schema, 6 entry / 8 file)

[docs/inter-plugin-contracts/MANIFEST.yaml](docs/inter-plugin-contracts/MANIFEST.yaml) 가 SSOT. lint 는 [scripts/check-inter-plugin-contracts.sh](scripts/check-inter-plugin-contracts.sh).

| Contract | Producer plugin | Files (wrapper sibling) |
|---|---|---|
| `review_verdict` | codeforge-review | review-verdict-v1.md (Archived) · review-verdict-v2.md (Archived) · [review-verdict-v3.md](docs/inter-plugin-contracts/review-verdict-v3.md) (Archived — CFP-137) · [review-verdict-v4.md](docs/inter-plugin-contracts/review-verdict-v4.md) (Active — CFP-137 / ADR-044) |
| `requirements_output` | codeforge-requirements | requirements-output-v1.md (Active) |
| `design_output` | codeforge-design | design-output-v1.md (Archived) · design-output-v2.md (Active — §7.4 + §11 idempotency, CFP-46) |
| `develop_output` | codeforge-develop | develop-output-v1.md (Active) |
| `test_verdict` | codeforge-test | test-verdict-v1.md (Active) |
| `pmo_output` | codeforge-pmo | pmo-output-v1.md (Active) |

각 wrapper sibling 은 lane plugin canonical 의 verbatim mirror + "**상위 SSOT 위치**" 섹션. canonical 변경 시 wrapper sibling sync PR 후속 의무 ([ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)).

### kind:registry (cross-cutting protocol, 3 file)

wrapper-owned. 본 lint scope 밖 — `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

- [comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) — 11 phase prefix taxonomy
- [fix-event-v1.md](docs/inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger writer monopoly
- [label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) — phase/gate/fix label taxonomy

### Versioning + Write boundary

Versioning + sibling sync SSOT: [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md) (SemVer 룰) + [ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md) (canonical/sibling 책임 + 신규 contract 추가 4단계). Write boundary: 각 lane plugin = 자기 contract producer + self-writer. wrapper Orchestrator = verdict 응답 + lane 라우팅 + Story §10 FIX Ledger 만 처리 (상세 [playbook](docs/orchestrator-playbook.md)).

---

## ADR (`docs/adr/` SSOT)

위치 = `docs/adr/ADR-NNN-<slug>.md` (flat, frontmatter `category:` 분류). Lookup = `Glob(docs/adr/ADR-*.md)` + `Grep` frontmatter filter → `Read`. CODEOWNERS 가 `docs/adr/**` 을 architect team review 강제 (Phase 1 PR 결재 필수). 페이지 템플릿: [codeforge-design `templates/adr.md`](https://github.com/mclayer/plugin-codeforge-design/blob/main/templates/adr.md). DesignReview 의 ADR 정합성 체크는 [codeforge-review CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) SSOT.

## GitHub Workflow

`templates/github-workflows/` 13종 fixture: 9 core (`story-init.yml` · `phase-label-invariant.yml` · `story-section-1-immutable.yml` · `subissue-from-impl-manifest.yml` · `phase-gate-mergeable.yml` · `fix-ledger-sync.yml` · `post-merge-followup.yml` (ADR-026 / CFP-74) · `retro-mandatory.yml` ([ADR-045](docs/adr/ADR-045-story-retro-mandatory-trigger.md) / CFP-138 — Story 완료 회고 forcing function, `gate:retro-complete` close-blocking) · `parallel-epic-conflict-check.yml` (ADR-050 — 병렬 에픽 파일 충돌 감지, non-blocking)) + 4 Live touching reusable workflow (`live-test-guard.yml` · `live-deploy-approval.yml` · `live-secret-policy.yml` · `kill-switch-integration-test.yml`, CFP-C). Issue Forms / branch protection / 버그 기록 등 상세 hierarchy + label 분류 + 코멘트 규칙 SSOT: [`docs/consumer-guide.md`](docs/consumer-guide.md) §1.3 + [`label-registry-v1`](docs/inter-plugin-contracts/label-registry-v1.md) + [`comment-prefix-registry-v1`](docs/inter-plugin-contracts/comment-prefix-registry-v1.md).

**Branch protection**: main 브랜치 = 4 required status check (phase-gate-mergeable + doc frontmatter + doc section + invariant-check) + `restrictions:{users:[],teams:[],apps:[]}` (direct push 차단) + **`enforce_admins: true` (admin 도 required check 통과 의무, CFP-70)**. CODEOWNERS 자동 review request 는 **도덕적 governance** — solo-dev 환경 강제 off (`require_code_owner_reviews:false` + `required_approving_review_count:0`, CFP-72). contributor 추가 시 `require_code_owner_reviews:true` + `count:1` 복원 의무 (별도 CFP). CODEOWNERS template: [`templates/CODEOWNERS.template`](templates/CODEOWNERS.template). 정책 SSOT: [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md). Rulesets / branch naming auto enforcement 는 solo-dev 가정 하 defer — contributor 추가 시 별도 CFP.

## Story 작성 의무 (CFP-45)

매 변경 시작 시 Orchestrator 가 cutoff 분류 → 강제/면제 결정. **모호 시 강제 측 분류**. Plugin 자체 + consumer 프로젝트 모두 적용. 정책 SSOT: [ADR-013](docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md). Story file 위치 = `mclayer/codeforge-internal-docs/<plugin-folder>/stories/<KEY>.md` (Plugin repo Issue body 와 bidirectional `story_uri`/`story_issues` binding). 새 Story = internal-docs `story.yml` Issue Form → `story-init.yml` Action 자동 생성 + Phase 1 PR open.

**Branch governance** (CFP-66 / ADR-024): 모든 wrapper 변경 = Story-scoped feature branch (`cfp-NNN[-<slug>]`) + PR 경유 의무. main 직접 push 금지 — branch protection `restrictions:{users:[],teams:[],apps:[]}` 물리 차단. emergency hotfix 도 PR 경유 (no exception). 병렬 modification 지원 = Story 단위 독립 branch + 독립 PR. 정책 SSOT: [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md). Consumer-side branch protection 권장은 별도 ([consumer-guide.md §2e](docs/consumer-guide.md)).

### 강제 대상 (Story file 작성 의무)
- 신규 ADR 결정 / 기존 ADR 변경
- 아키텍처·도메인 모델 추가·삭제·재정의
- 에이전트 추가·삭제·역할 재정의
- Workflow 정의(`templates/github-workflows/**`) 변경
- SSOT 문서(`templates/`·`presets/`·`CLAUDE.md`·`docs/orchestrator-playbook.md`) 의미 변경
- Breaking change · consumer migration 영향

### 면제 대상 (chore commit OK)
- Typo · 문법 · 줄바꿈 · 마크다운 형식 정리
- 링크 깨짐 수정 / 죽은 링크 제거
- Lint 자동 fix · dependency lock · version bump (security 영향 없는 경우)
- README 단순 문구 수정

면제 시 commit body 에 `Story 면제 사유: <이유>` 1줄 명시. 판단 시점: cutoff 분류 선언 (변경 시작 시) + commit 직전 재확인.

### Brainstorming/writing-plans skill default override

Plugin repo (codeforge family) 작업 시:
- `superpowers:brainstorming` skill spec 저장 위치 = `<internal-docs-clone>/<plugin-folder>/specs/` (default `docs/superpowers/specs/` 아님)
- `superpowers:writing-plans` skill plan 저장 위치 = `<internal-docs-clone>/<plugin-folder>/plans/` (default 아님)
- Controller (Orchestrator) 가 path 명시 의무, Skill prompt 에 explicit override
- Plugin repo CI (`dogfood-artifact-paths`) 가 PR 단계에서 fail-closed (ADR-017). Skill prompt 정책 인지는 1차 안전망, CI 가 authoritative
- `codeforge:brainstorm` skill = codeforge 프로젝트 전용 강화 brainstorming (ADR-034 Amendment 1). `superpowers:brainstorming` 상위호환.

Consumer overlay: `.claude/_overlay/project.yaml` `story_cutoff.additional_exempt_categories[]` 로 도메인 특화 면제 추가 가능 (**강제 항목 축소 불허** — 안전 방향만). Schema [`docs/project-config-schema.md`](docs/project-config-schema.md) §2.

본 plugin repo dogfooding: KEY prefix `CFP`. Plugin meta 변경 시 무의미한 lane 은 `N/A — <사유>` 명시 (ADR-005 standardization).

## docs/stories + docs/retros 규약

Story file = `docs/stories/<KEY>.md` ([`templates/story-page-structure.md`](templates/story-page-structure.md), KEY = `<story_key_prefix>-N`). 각 lane plugin 이 owned section 직접 갱신 (§ "Lane plugin self-write boundary" 표). §1 변조 금지 invariant = `story-section-1-immutable.yml` Action 강제. Retro file = `docs/retros/<sprint>.md` (PMOAgent self-write, [`templates/retro.md`](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/templates/retro.md), `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` warning 검증).
