# CLAUDE.md

## 언어 정책

모든 응답·코드 주석·문서 작성에서 **한글을 주 언어로 사용**. 영어는 기술 용어·코드·고유명사 등 필요한 경우에만 사용. 한자(일본어·중국어 포함) 사용 절대 금지.

Claude Code 범용 SW 개발 오케스트레이션 플러그인. **0 core 에이전트 (wrapper-only)** · 6 레인 + CI gate + `role: dev` 동적 roster 로 요구사항 접수부터 보안 테스트 통과까지 자율 실행. 에이전트 상세는 각 lane plugin (codeforge-{review,pmo,requirements,test,develop,design}) SSOT — 본 wrapper repo 에는 agent file 없음. Dev preset 은 [codeforge-develop presets/](https://github.com/mclayer/plugin-codeforge-develop/tree/main/presets) 참조.

## Plugin

이 리포는 **consumer 프로젝트가 설치해 사용하는 Claude Code 플러그인**. 프로젝트별 도메인·기술 스택·SSOT 상수는 **overlay 메커니즘**(consumer 측 `.claude/_overlay/` + SessionStart merge hook)으로 주입. 상세는 [`docs/consumer-guide.md`](docs/consumer-guide.md) 참조.

**Objective SSOT 상수** (GitHub org/repo·story_key_prefix·CODEOWNERS team·Discussions 카테고리·Milestone naming·label taxonomy)는 **`.claude/_overlay/project.yaml`** 에 structured로 기재. 에이전트는 해당 파일을 `Read`로 직접 참조. Schema: [`docs/project-config-schema.md`](docs/project-config-schema.md). Narrative 컨텍스트(도메인 해설·기술 스택 근거)는 `.claude/_overlay/CLAUDE.md`에 기재.

### Marketplace cross-repo 동기화 의무

본 플러그인은 [`mclayer/marketplace`](https://github.com/mclayer/marketplace) 를 통해 노출. codeforge family 7 plugin (wrapper + 6 lane) **모두 등록**. **mirrored 필드** = `name`·`version`·`description`·`author` — 변경 시 `marketplace.json` `plugins[name=codeforge]` 동일 필드를 **같은 Story 내 sync PR** (codeforge PR merge 직후 즉시 open·merge). 비-mirrored 필드(`keywords` 등) 면제. 정식 cross-repo parity CI 는 후속 CFP-50 잠정 — 도입 전까지 author·Orchestrator 의무. drift 시 stale version install 로 단일 진입점 의미가 무너진다. 정책 SSOT: [ADR-016](docs/adr/ADR-016-marketplace-registration-policy.md) (CFP-49).

## SSOT Boundary

Wrapper CLAUDE.md content scope = (1) Plugin identity (2) Cross-cutting policy (3) skill pointer (anchor vs reference 판정자: "Orchestrator 가 매 turn 자기검열해야 하는가" — ADR-051 Amendment 1) — **CFP-343 / ADR-051 이후 skill로 분리** (`codeforge:review-responsibility` / `codeforge:root-cause-decision` / `codeforge:fix-ledger-schema` / `codeforge:deputy-mandate` / `codeforge:lane-self-write-boundary` / `codeforge:story-cutoff-classification` / `codeforge:inter-plugin-contract-registry` / `codeforge:story-epic-flow-preflight`). 정확한 정의는 [ADR-012](docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md). Dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) monorepo SSOT — 정책 SSOT: [ADR-013](docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (CFP-45).

Lane internal · per-lane spawn detail · severity rule · GitHub workflow subsection 상세는 lane plugin CLAUDE.md 또는 [playbook](docs/orchestrator-playbook.md) 위임.

## 세션 개시 의무 (필수 의존성 SSOT)

세션 시작 직후, 모든 작업보다 먼저 의존성 노출·설치·인증 상태 확인. 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 요구. 복구 완료 전까지 **모든 작업 중단**.

**Orchestrator 모델 필수 확인**: Claude Code 세션 모델이 `claude-opus-4-7` (Opus)인지 확인. Sonnet 또는 Haiku 세션에서 codeforge 실행 시 즉시 중단 → 사용자에게 Opus 세션으로 재시작 요청. `/fast` 토글 또는 직접 Opus 모델 선택. Consumer overlay로 축소 불가 ([ADR-057](docs/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md)).

**MCP 서버 (1종)**: `github` — Issue/PR/sub-issue/comment·label·milestone 각 lane plugin self-write; `docs/{change-plans,adr,domain-knowledge,retros}/**` 직접 write 는 owner agent (CFP-26 Phase 0a)

**GitHub 도구 우선순위**: 모든 GitHub 작업(Issue·PR·comment·sub-issue·repo file write)은 `mcp__github__*` 도구 우선 사용. `gh` CLI는 MCP 미커버 영역(`milestone CRUD` / `Discussions` / `GraphQL` / `label 부트스트랩 스크립트`)에서만 fallback. MCP 미노출 시 gh 로 즉시 우회 금지 — 사용자에게 `/mcp` 재인증 요청 후 대기.

**필수 플러그인 (8종)**:
- `codeforge-{review,pmo,requirements,develop,design,test}@mclayer` — 6 lane plugin (codeforge-test 통합테스트 전용 부활 — CFP-367 / ADR-055 / ADR-048 Amendment 1)
- `codex@openai-codex` — CodexReviewAgent + codex CLI dependency
- `superpowers@claude-plugins-official` — 17 lane agent × 8 skill 호출 (SSOT: [`docs/superpowers-integration.md`](docs/superpowers-integration.md))
- `github@claude-plugins-official` — GitHub MCP 도구 노출

**필수 CLI (2종)**: `codex`, `gh`. (CFP-59 / ADR-019 → ADR-022 (Deprecated by CFP-134 / ADR-035) — Gemini CLI 의존 제거. ad-hoc Sonnet / Codex 호출 = Claude Code Agent tool runtime / codex CLI, 외부 auth 무관. `gemini` CLI 가 다른 용도로 설치되어 있으면 unset / removable optional.)

**권장 플러그인 (4종, 미설치 시 권유만)**: `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

확인·자동복구·blocking-wait 절차 SSOT: [playbook §1.1](docs/orchestrator-playbook.md) checklist 0번 (MCP `ToolSearch` 노출 / settings.json 토글 / `/mcp` 재인증·`/plugins install` 요구 / consumer `.github/` 6 workflow + 3 forms + CODEOWNERS 부재 알림 / **codeforge plugin family version drift 검사 — CFP-262 / [ADR-037](docs/adr/ADR-037-plugin-version-bump-rule.md)**: MAJOR drift = hard-stop blocking, `bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-version-drift.sh`).

**Deferred tool 선제 로드 (0i)**: SessionStart hook tier 위임 — [playbook §1.1 0i](docs/orchestrator-playbook.md) SSOT (ADR-038 Amendment 2 §결정 9, CFP-500).

**SessionStart hook — worktree-gc (0a-prime)**: wrapper repo `.claude/settings.json` 두 번째 hook entry = `check-worktree-stale.sh` — [playbook §1.1 0a-prime](docs/orchestrator-playbook.md) SSOT (CFP-427 / ADR-040 §결정 5).

**Git layer 안전망 (CFP-428)**: `templates/.git-hooks/{pre-checkout,pre-commit-main-block}.sample` + `scripts/install-git-hooks.sh` opt-in installer — [ADR-040 Amendment 3 §결정 7.D](docs/adr/ADR-040-worktree-convention.md) SSOT.

**구조적 변경 재구동 (ADR-053)**: 직전 세션 구조 변경 시 재구동 완료 후 작업 — 상세 [playbook §1.1 0g](docs/orchestrator-playbook.md).

## Development Agent Team

Wrapper agent **0개** (ζ arc 완료, [ADR-009](docs/adr/ADR-009-wrapper-only-decomposition.md)). Orchestrator (top-level Claude 세션) 가 6 lane plugin 의 agent 를 spawn.

| Lane | Plugin | Agent count | SSOT |
|---|---|---|---|
| 요구사항 | codeforge-requirements | 7 (PL + DomainAgent + RequirementsAnalyst + Researcher + ChangeImpactAgent + FeasibilityAgent + ContinuityAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/CLAUDE.md) |
| 설계 | codeforge-design | 8 (PL + ArchitectAgent chief + 6 deputy) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
| 설계리뷰 / 구현리뷰 / 보안테스트 | codeforge-review | 5 (3 PL + 2 worker) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) |
| 구현 | codeforge-develop | 5 (PL + QADev + 3 role:dev core) + preset/overlay 동적 | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-develop/blob/main/CLAUDE.md) |
| 통합테스트 | codeforge-test | 1 (IntegrationTestAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-test/blob/main/CLAUDE.md) |
| Cross-cutting | codeforge-pmo | 2 (PMOAgent + GitOpsAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) |

각 lane plugin 의 agent 역할·동작은 해당 plugin CLAUDE.md SSOT. 본 표는 composition map 만.

**Lane plugin lifecycle**: 신규 추가 / deprecate / rename 절차는 [ADR-023](docs/adr/ADR-023-lane-plugin-lifecycle.md). Marketplace sibling sync ([ADR-016](docs/adr/ADR-016-marketplace-registration-policy.md)) 와 align — CFP-50 (parity CI, follow-up) 가 자동 검증.

**Agent model tier 정책**: agent file `model:` field 의 Opus / Sonnet / Haiku 분류 기준 + 신규 agent 도입 / 기존 model 변경 시 ADR 의무 SSOT = [ADR-042](docs/adr/ADR-042-agent-model-selection-policy.md) (Amendment 2: InfraEngineer·QADeveloper·DataEngineer Haiku pilot 포함). 핵심 원칙: "Sonnet 으로 fully cover 가능 = role 재정의 시그널". ResearcherAgent 의 mandate (Concept formulation + Deep exploration + Requirement reshape) 와 Opus tier rationale 은 [ADR-046](docs/adr/ADR-046-researcher-role-redefinition.md) SSOT.

**주체 명칭**: **Orchestrator** = 최상위 Claude 세션 (모든 Agent 툴 스폰, 토큰 예산 소유) · **(Human) 사용자** = 인간 행위자 · **Cross-cutting** = 모든 레인에 걸쳐 작동하는 에이전트 (PMOAgent).

리뷰 워커 통합 근거: [ADR-001](docs/adr/ADR-001-review-agent-unification.md) (3 lane × 2 vendor → 2 lane-agnostic worker). [Inter-plugin Contract `review_verdict`](docs/inter-plugin-contracts/review-verdict-v2.md) versioning: [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md).

> **(선택) Stage 0 — pre-Issue brainstorming**: 비-trivial Story 는 `codeforge:brainstorm` (codeforge 프로젝트) 또는 `superpowers:brainstorming` (generic) 으로 사전 scope 정리 후 Issue Form 제출 권장 ([ADR-034 + Amendment 1·2](docs/adr/ADR-034-pre-issue-brainstorming-stage.md) · [playbook §1.2.0](docs/orchestrator-playbook.md)). `codeforge:brainstorm` = Requirements 에이전트 7종 병렬 컨텍스트 (기존 4 + 코드 컨텍스트 3: ChangeImpactAgent·FeasibilityAgent·ContinuityAgent) + scope_manifest 초안 자동 생성 (Phase 0 자동 실행 — ADR-034 Amendment 2 / CFP-386, opt-in 폐지. 비용 회피 시 `superpowers:brainstorming` 직접 호출). CI 강제 없음.

## 레인 6개 · 단계 정의

**Story / Epic flow + Preflight 체크**: `codeforge:story-epic-flow-preflight` skill 호출 — Story flow (1 Story = 2 PRs) / Epic flow / Cross-repo Epic centralization mode / 레인별 Preflight 체크 의무 SSOT. lane 진입 전 Orchestrator 의무 호출.

요약: full 6 레인 + CI gate 통과 (Hotfix 경로 2종 예외 — [hotfix-playbook.md](docs/hotfix-playbook.md)). 1 Story = Phase 1 PR (§1-7) + Phase 2 PR (§8-11). doc-only fast-path (ADR-054) = 1 PR. Epic = Phase 1 doc + N impl PRs + close PR. Preflight 3체크 = phase라벨 정합 / 선행섹션 / 외부의존성. 세부 SSOT: [playbook §3](docs/orchestrator-playbook.md) + 각 lane plugin CLAUDE.md.

## 결정 원칙 (ADR-064 normative SSOT)

codeforge 의 모든 결정 제안 시점 (proposing-time) 에 적용. 외연 영역 (`hotfix-bypass:*` operational-time, deprecation 사후 운영, source code fallback / safe-default 런타임 로직) 은 본 단락 scope 외. 정책 SSOT: [ADR-064](docs/adr/ADR-064-decision-principle-mandate.md) — 행동 패턴 + 적용 사례 SSOT = [`docs/domain-knowledge/domain/governance-principle/decision-style.md`](docs/domain-knowledge/domain/governance-principle/decision-style.md).

### 결정 내용 (Trace 1)

- **4 어휘 normative anchor**: best-effort (도달 가능한 최선의 안) / broad coverage (side effect / edge case / 외연 후보 포함) / full-scope (도메인 전체 즉시 적용) / active amendment (강화 방향 적극 발의)
- **Forbid-list dictionary 8 어휘** (mechanical lint = [CFP-449](https://github.com/mclayer/plugin-codeforge/issues/449) warning tier, ADR-060 §결정 5 정합 — scope = 5 영역: `docs/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**`. exempt channel = `hotfix-bypass:decision-principle-vocab` label. dictionary SSOT = [ADR-064](docs/adr/ADR-064-decision-principle-mandate.md) §결정 2):

```text
임시 / 단계적 / 일단 / 우선[시간 우선순위 의미 한정] / 잠정 / 가벼운 / minimal viable / quick win
```

  결정 menu 자체에서 제거 의무.

- **CFP scope unitary**: 한 CFP 안 "경량 → full" 단계 채택 금지. 별개 CFP 분리는 허용 (`CFP-N v0.1` + `CFP-N+1 v1.0` 가 독립 brainstorm + 독립 Story + 독립 PR).

### 결정 제시 (Trace 2)

Orchestrator 가 사용자에게 결정 제안 / 질문 시 5 룰 적용:

1. **Derived default 기본값 적용** — 컨텍스트로 합리적 default 도출 가능 시 `AskUserQuestion` 발화 생략. derived default 직접 declare + 결과 보고 (사용자 정정 의무).
2. **옵션 dump 금지** — 권장 1 안 + 대안 1 안 (최대 2). 3+ 후보는 brainstorm Phase 0 영역.
3. **식별자 사전 요약** — ADR / CFP / 코드 식별자 인용 시 핵심 결정 1 문장 요약 사전 제시 후 질문 / 제안 본문 진입.
4. **질문 brevity** — 1 문장 단위, 다중 질문 시 numbered list (최대 3 항목).
5. **`AskUserQuestion` 범위 제한** — 가치 판단 / 미공개 컨텍스트 2 종 한정.

### 적용 속도 (Trace 4)

Orchestrator multi-task spawn 결정 default = **parallel** (단일 메시지 다중 Agent tool call). sequential 선택은 다음 3 사유 중 1 종 명시 의무 — **state dependency** (task N+1 이 task N 출력 의존) / **shared resource** (동일 file / label / branch lock) / **ordering invariant** (출력 순서 자체가 의미 — ADR-RESERVATION row append, FIX Ledger row append). 3 사유 모두 부재 = default parallel. [ADR-039](docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) §결정 7 `policy_violation_subdecision` 결정 영역 확장. Epic open→close 시간 단축 measurable signal = `EPIC-RESULTS-<KEY>.md` artifact frontmatter `opened_at` / `closed_at` delta (현재 `templates/epic-results.md` frontmatter 에 두 field 부재 — CFP-β 가 PMOAgent owner path 에 field 신설 의무).

### Self-application top-down ratchet

ADR-064 amendment 는 강화 방향만 허용 (scope 확장 / 강도 강화). 약화 방향 (`is_transitional: false → true` 다운그레이드 / forbid-list dictionary 축소 / sequential 강제 사유 확장) 은 [ADR-058](docs/adr/ADR-058-adr-sunset-criteria-mandate.md) §결정 5 sunset_justification 의무로 차단. memory `feedback_explain_before_ask` + `feedback_question_quality` + `feedback_subagent_driven_auto_select` 3 memory entry 의 normative 승격 첫 carrier.

## 오케스트레이션 규칙

### Sonnet subagent rate-limit → Opus fallback (ADR-057)

Orchestrator가 `model: sonnet` subagent spawn 결과로 rate-limit 에러를 수신하면:
1. 동일 입력 패킷으로 `model: opus` 재spawn (1회 한정)
2. 재spawn 성공 시 정상 진행 (§14 Lane Evidence에 `[rate-limit-fallback:sonnet→opus]` 태그 추가)
3. Opus도 rate-limit 실패 시 사용자에게 상황 통지 후 대기 (자동 재시도 금지)

적용 대상 Sonnet agent: DeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent · CodebaseMapperAgent · RefactorAgent · DeveloperPLAgent (현재 Sonnet 유지 agent 전체).

> **SSOT 명시 (CFP-448 / ADR-057 Amendment 3, CL-6 사용자 확정)**: 본 명단은 [ADR-057 §결정 3 표](docs/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) 의 mirror reference 임. **SSOT = ADR-057 §결정 3 표**. drift 시 ADR 본문 우선 — 본 CLAUDE.md L127 갱신은 ADR Amendment definition of done 의 part.

> **KPI dashboard (CFP-393, ADR-057 Amendment 2)**: 본 fallback 정책의 sunset gate 2 측정 = [`docs/kpi/rate-limit-fallback.json`](docs/kpi/rate-limit-fallback.json) (monthly cron) + [`rate-limit-fallback-rate` registry entry](docs/evidence-checks-registry.yaml) — ADR-060 evidence-enforceable framework 첫 non-sunset application. 분모 / 분자 / sample sentinel / window 정량 정의는 [ADR-057 § "Sunset gate 2"](docs/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) 표 참조.

### Lane 진입 시 skill 호출 의무

Orchestrator는 해당 lane 진입 직전 아래 skill을 호출한다. 상세 테이블은 각 skill 참조.

| 진입 레인 | 호출 skill | 비고 |
|---|---|---|
| 설계 | `codeforge:deputy-mandate` | ArchitectPLAgent deputy spawn 결정 전 |
| 설계리뷰 | `codeforge:review-responsibility` | DesignReviewPL spawn 전 |
| 구현리뷰 | `codeforge:review-responsibility` | CodeReviewPL spawn 전 |
| 보안테스트 | `codeforge:review-responsibility` | SecurityTestPL spawn 전 |
| FIX 루프 | `codeforge:root-cause-decision` + `codeforge:fix-ledger-schema` | DeveloperPL 진단 전 |
| lane spawn 직전 (owner path 확인) | `codeforge:lane-self-write-boundary` | Lane plugin self-write 책임 영역 lookup |
| Story 분류 시 (요구사항 접수 직후) | `codeforge:story-cutoff-classification` | Story 작성 의무 vs chore commit 면제 결정 |
| Inter-plugin contract sync 시 (version bump 결정) | `codeforge:inter-plugin-contract-registry` | MANIFEST / Versioning / Write boundary lookup |
| Story flow 진입 시 (lane preflight 결정) | `codeforge:story-epic-flow-preflight` | Story / Epic / Cross-repo Epic / Preflight 결정 |

> **구현 실행 방식 자동 선택 (CFP-358 / CFP-374)**: `superpowers:executing-plans` / `superpowers:subagent-driven-development` 스킬이 "구현 실행 방식 선택" 프롬프트를 띄울 때, Orchestrator는 묻지 않고 자동으로 **Subagent-Driven**을 선택해 진행. **스킬 파일의 `AskUserQuestion` 지시보다 이 정책이 우선** — 스킬 로드 후 해당 선택지 발견 시 즉시 건너뛰고 Subagent-Driven 직접 진입. behavioral directive → memory 금지 (normative) 적용 — playbook §3.0.5 SSOT.

> **Orchestrator 정책 적용 범위 (normative)**: 본 CLAUDE.md 및 playbook 의 모든 Orchestrator 행동 규칙 (lane spawn 방식·stop discipline·진행 시각화·GitHub 도구 선택·통신 표준·fact verification 등) 은 **wrapper plugin 자체 작업과 모든 consumer project 에 동일 적용**. Consumer overlay (`.claude/_overlay/`) 는 정책을 축소할 수 없고 확장만 가능.

> **behavioral directive → memory 금지 (normative)**: 사용자가 Orchestrator 행동 directive 를 내릴 때, 해당 규칙을 personal memory file 에 저장하는 것으로 갈음하지 않는다. 대신 **즉시 CFP 제안** 후 playbook / CLAUDE.md / consumer-guide 에 반영해야 한다. Memory = ephemeral + consumer 비전파 + single-session scope = structural enforcement 불가. 예외 없음.

> **Codex Proactive Check (CFP-354 / [ADR-052](docs/adr/ADR-052-codex-proactive-check-touchpoints.md))**: Orchestrator는 6개 touchpoint(`AskUserQuestion` 직전 / **ArchitectAgent §3 완료 직후 (mandatory — CFP-532 / ADR-052 Amendment 4)** / DeveloperPLAgent FIX 2+ 감지 시 / **RequirementsPLAgent §1-§6 완료 직후 (multi-round debate 격상 — CFP-411 / ADR-052 Amendment 1)** / ArchitectPLAgent root cause 판정 직후 / ArchitectAgent ADR 초안 완료 직후)에서 `codex:codex-rescue` subagent를 proactive check 용도로 자동 dispatch. 패킷 스키마 + 트리거 + 결과 처리 SSOT = [playbook §3.10](docs/orchestrator-playbook.md). 기존 `codex:rescue`(reactive) 채널과 분리. **verify-before-trust 채널 의무 (CFP-578 / [ADR-070](docs/adr/ADR-070-codex-verify-before-trust.md) + ADR-052 Amendment 5)** — Codex worker spawn prompt `artifacts` 필드 안 file content verbatim 첨부 의무 (sandbox 영역 외 file 전체, file path reference 만 사용 금지). Codex 결과 수신 후 Orchestrator 가 finding evidence 의 ground truth 를 direct file Read / Glob / Grep 으로 verify 의무 — mismatch 시 verdict reject + Story §10 false positive count tally + override rationale 명시. **Touchpoint #2 단독 mandatory (CFP-532 / ADR-052 Amendment 4)** — Orchestrator 가 dispatch 결과 P0 + P1 finding 모두 inline FIX 의무 (skip 영역 차단). P2 finding 만 Story §10 deferred 기록 가능. 6 sample success rate 100% sentinel (CFP-426 + CFP-427 + CFP-428 + CFP-429 + 2 carry-over) — 모든 review lane FIX 회피 evidence. **Touchpoint #4 만 multi-round adversarial debate (debate-protocol-v1, §3.13) 자동 발동 — RequirementsPL 이 Codex proactive check 결과와 자기 synthesis (§2/§5/§6) 간 divergence 감지 시. divergence 영역 = 3 semantic criteria (AC 의미 / Edge Case 누락 / Why 해석 mismatch) + 1 factual criterion (fact-check: registry-execution drift / pre-existing leak / file path verification / cross-repo state verification — ADR-052 Amendment 3 / CFP-510). PL synthesis fact claim 영역 marker 4종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]`) + reverse-explicit `[verification-out-of-scope: <사유>]` 의무. FIX verdict 시 RequirementsPL 자체 redo (ArchitectAgent 미관여)**. 나머지 4 touchpoint (#1/#3/#5/#6) = single-shot 검토 + optional 유지 (Orchestrator skip 가능 영역 보존).

> **Orchestrator 행동 SSOT**: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) — 세션 생명주기, 스폰 프롬프트 템플릿, 병렬 스폰 판단, FIX 상태 머신, 세션 재개 복원, 토큰 예산.

**Default subagent context (수정 작업) — codeforge 정책 (ADR-039)**: codeforge 를 이용한 **수정 작업** 진행 중, Orchestrator 는 모든 work 을 `Agent` tool spawn (subagent) 으로 수행한다. inline 수행 (Orchestrator turn 안에서 Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 직접 호출) 은 **Inline whitelist 4-entry** (사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report — 상세 [playbook §3.0](docs/orchestrator-playbook.md)) 외 영역에서 금지. "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 자체 금지 — branch logic 제거 = ADR-025 §결정 7 `policy_violation_subdecision` 발화 채널 차단. 정책 SSOT [ADR-039](docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) (amends ADR-009). Skill 호출 = Inline (file write 아님, meta wrapper) — Skill 내부 individual tool call (Read/Edit/Write/mcp__github__\*/Agent/Bash) level 에서 spawn 분류 발동. Dialog turn separation 의무 (Story §2 AC-5): 사용자 dialog 와 dialog 직후 state change 는 별도 turn / message — 한 메시지 안 inline write + dialog 동시 수행 금지.

**Default subagent context 의 codeforge 정책 결정** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 미설정 시) — 하위 에이전트는 Agent 툴 사용 불가 (재귀 스폰 금지 — platform inherent), 서브에이전트 간 직접 통신 불가 (codeforge 정책 — agent teams enabled context 별도), 서브에이전트 one-shot (codeforge 정책). 모든 스폰은 최상위 Claude.

**Agent teams enabled context 별도** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, CFP-137 / [ADR-044](docs/adr/ADR-044-phase-scoped-sequential-team.md) 적용 후) — sibling teammate 간 SendMessage 사용 가능 + Phase-scoped sequential team + Adversarial debate (review lane) + Cross-layer (TEAM-DEVELOP) 패턴 활성. 단 (a) 재귀 spawn 금지 (platform inherent — Lead 와 teammate 모두), (b) nested team 금지 (no team-of-teams), (c) one-team-per-lead 강제 — 다음 lane TeamCreate 전 현 team `TeamDelete()` 의무. team-spec yaml 7종 (`templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml`) + hook 3종 sample (`templates/agent-teams-hook-samples/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample`) SSOT. review lane Codex worker `dispatch_mode: user_request_only` (사용자 ad-hoc 요청 시에만 활성, ADR-022 Deprecated 정합). env=0 fallback = ADR-039 default subagent context (one-shot Agent tool, 본 단락 무효화). 상세 SSOT [ADR-044](docs/adr/ADR-044-phase-scoped-sequential-team.md) + [domain-knowledge entry](docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md) + [playbook §3.6-§3.9](docs/orchestrator-playbook.md).

**Wrapper 위임 패턴** (모든 행위 = ADR-039 default subagent spawn — 위 "Default subagent context (수정 작업)" 단락 정합):
- 컨텍스트 전달: `docs/stories/<KEY>.md` SSOT, agent 프롬프트는 path 주입, 본문은 agent self-fetch — Context Packet / §0 Live Progress / Project Config Packet 상세는 [playbook §12·§14](docs/orchestrator-playbook.md)
- Never-skippable: 각 lane 진입 시 Orchestrator 가 해당 lane plugin PL agent 1개만 spawn — sub-agent fan-out (수·역할·non-skippable 매트릭스) 상세는 각 lane plugin CLAUDE.md SSOT
- **Lane-spawn evidence (ADR-031, CFP-126)**: 매 lane spawn 시 Story §14 Lane Evidence row append (start: spawn 직전, end: return 직후 outcome 채움) + Phase 2 PR description `## Lane evidence` 블록 의무. `lane-evidence-check.yml` workflow + `scripts/check-lane-evidence.sh` lint 가 cross-validate. Bypass = `BYPASS_LANE_EVIDENCE=1` + `BYPASS_LANE_EVIDENCE_REASON` env. Effective date = ADR-031 Accepted 후 신규 Phase 2 PR 부터 (retroactive 미처리). `.claude-work/progress/<KEY>.md` (CFP-20 NG6 cache) 와 분리 — §14 가 SSOT.
- Track 병렬 (R7 설계리뷰 PASS 시): Track A (DesignReviewPL merge gate) ∥ Track B (DeveloperPL Phase 2 PR 준비) — 상세 [playbook §3.1]
- **Worktree dispatch (CFP-136 / [ADR-040](docs/adr/ADR-040-worktree-convention.md))**: 매 lane spawn 시 isolated working directory 보장. base = `${HOME}/.claude/worktrees/<repo-name>/<branch-flat>`, hierarchical branch (ADR-024 Amendment 1) `cfp-NNN[/<lane>[/<sub>]]`, lifecycle (`on_team_create_pre|post` / `on_team_delete_pre|post` / `on_session_start` / `on_story_close`). 5 script (`templates/scripts/worktree-{create,merge,prune,path-util}.sh` + `check-worktree-stale.sh`) + SessionStart hook (`templates/.claude/hooks/SessionStart-codeforge-worktree-gc.json.sample`) — 7 days + origin absent stale 자동 prune. CFP-137 (agent teams) prerequisite + CFP-139 (GitOpsAgent) hook contract SSOT. Default subagent context (agent teams `=0`) 에서도 사용자 ad-hoc 호출 가능. 상세 [playbook §3.5](docs/orchestrator-playbook.md).
- **Worktree-first (normative — wrapper + all consumers, CFP-341)**: lane spawn·ad-hoc 구분 없이 모든 coding work 는 worktree 안에서 수행. `git checkout <branch>` 로 원본 working directory 직접 편집 금지. Story 시작 시 `bash templates/scripts/worktree-create.sh` 선행 의무. 상세 [playbook §3.0.10](docs/orchestrator-playbook.md).
- **Worktree-first mechanical enforcement (CFP-426 / ADR-040 Amendment 3 §결정 7 + Amendment 5 CFP-531)**: normative 선언 + mechanical action mapping 의무. 4 evidence-check entry **blocking-on-pr tier 활성** (CFP-531 / ADR-040 Amendment 5, 2026-05-13) — `worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}` (actual wire CFP-427/428 완료, enforce 활성). frontmatter `mechanical_enforcement_actions[]` schema = ADR-040 Amendment 3 §결정 7.A (list[object] verbatim). retroactive 면제 명시 (§결정 7.C — 본 Amendment 3 이후 신설/Amendment ADR 만). 4 hotfix-bypass label = `hotfix-bypass:worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}` (per-entry namespace, ADR-024 Amendment 3 §결정 6.A 정합). `BYPASS_WORKTREE_FIRST=1` env = `BYPASS_WORKTREE_GC=1` 와 disjoint scope (§결정 7.E).

**Parallel epic coordination (ADR-050 + Amendment 1 CFP-534)**: 복수 Orchestrator 세션 병렬 진행 시 충돌 조율 의무.

- **Epic Scope Manifest**: Phase 1 시작 시 Orchestrator가 Epic Issue body `<!-- scope_manifest -->` 블록 작성 (예상 변경 파일·ADR·CLAUDE.md 섹션 + **Amendment 1 3 신규 field**: `planned_inter_plugin_contracts[]` / `planned_label_registry_bumps[]` / `cross_section_conflict_detection: true`). GitOpsAgent가 다른 open 에픽과 교집합 + cross-section 검사 (inter-plugin-contracts / label-registry / MANIFEST 영역). 발견 시 `conflict:{contract-overlap,registry-bump-overlap}` 라벨 자동 + WARN comment + merge-order (lower CFP 우선) 자동 부여.
- **ADR 번호 예약**: GitOpsAgent가 `docs/adr/ADR-RESERVATION.md` sequential append.
- **Section 편집 정책**: `docs/parallel-work/section-ownership.yaml` 정의 (append-only / locked). locked 섹션 동시 수정 시 `merge-order` 의무.

Scope Manifest 형식 (Amendment 1):
```yaml
<!-- scope_manifest -->
planned_adrs: [NNN]
planned_files: [path/to/file.md]
planned_claude_md_sections: ["섹션명"]
planned_inter_plugin_contracts: [docs/inter-plugin-contracts/label-registry-v2.md]
planned_label_registry_bumps: [{kind: MINOR, scope: "<설명>"}]
cross_section_conflict_detection: true
<!-- /scope_manifest -->
```

**Progress visualization via TodoWrite (ADR-038, CFP-274)**: TodoWrite 를 CFP-20 §14.7 render flow 의 3번째 channel 로 추가. 4 marker (⏳ 🔄 ✅ ❌) hierarchical (lane row + 2-space indent agent sub-row) 렌더 표준. ❌ 는 검출 lane 이 아닌 원인 lane 에 표시 (검출 lane 은 ✅ + content `FIX-N detected`). Single-Story 모드 (multi-Story 별도 CFP). Lane plugin 변경 0건 (Writer 단독 invariant 유지). multi-row in_progress 의도적 허용 (codeforge 병렬 agent 모델 — wrapper-specific deviation). 상세: [ADR-038](docs/adr/ADR-038-progress-visualization-todowrite.md), [playbook §14](docs/orchestrator-playbook.md). 호출 시도 non-skippable + 실패 non-blocking 분리: [ADR-038 Amendment 1 §결정 8](docs/adr/ADR-038-progress-visualization-todowrite.md).

### Adversarial Debate Protocol (debate-protocol-v1, CFP-391 / ADR-059)

DesignReview lane 에서 Claude worker 와 Codex worker 가 review-verdict-v4 `findings[]` 의 동일 `anchor_id` 에 대해 **(a) 서로 다른 severity 또는 (b) 서로 다른 recommendation (FIX vs PASS)** 을 발화 = `divergence_detected` 시 multi-round adversarial debate 자동 발동. ADR-044 §결정 2 `dispatch_mode` enum 의 `auto_on_divergence` (Amendment 1, CFP-391) 가 활성 조건.

**dispatch_mode 3-value 표 (debate-protocol-v1 v1.1, ADR-059 Amendment 1 / CFP-533)**: `auto_on_divergence` (divergence_detected 시 표준 multi-round debate, min 3 / max 5) / `mechanical_fast_path_inline` (divergence_detected + single-file scope + severity ≤ critical 시 inline FIX, debate skip + PL inline 판정, transcript §9 면제 + §10 row 의무 보존) / `user_request_only` (consumer/user ad-hoc 명시 trigger, manual dispatch). 우선순위 `auto_on_divergence > mechanical_fast_path_inline > user_request_only`. ADR-044 team-spec layer dispatch_mode 와 분리 (별 layer 의미 호환 forcing function).

**라운드 정책**: min 3 / soft default 4 / max 5. min 3 미달 합의 시 PL 이 adversarial prompt 재주입 후 force_continue. max 5 미합의 시 `AskUserQuestion` 사용자 escalation.

**Anti-sycophancy 메커니즘**:
- `remaining_disagreements` 필드 매 라운드 출력 의무 (비어 있고 round < 3 = 가짜 합의 의심)
- role_lock + 반대 입장 강제 유지 prompt + `POSITION_CHANGE` 라벨 입장 변경 시 의무

**Topic anchor 강제 prepend**: Round 0 쟁점 statement 원문이 라운드 N 입력 **최상단** 에 매 라운드 verbatim 포함 (U-shaped attention bias 완화 forcing function). full transcript carryover 정합.

**Transcript 영속화**: Story §9 inline append (`### Debate transcript: <anchor_id>` sub-section, debate-protocol-v1 schema 준수). codeforge family Story (ADR-013 dogfood-out) = `<internal-docs-clone>/<plugin-folder>/stories/<KEY>.md §9`. Consumer Story = `docs/stories/<KEY>.md §9`.

**FIX 통합 (reasoning carryover)**: debate verdict = FIX 시 (1) transcript Story §9 append → (2) §10 FIX Ledger row append + `debate_artifact_ref` 필드 채움 (Story §9 section anchor link, fix-event-v1 1.1 MINOR bump) → (3) ArchitectPLAgent re-spawn — prompt 에 transcript verbatim 주입 → (4) ArchitectAgent re-run instruction "양측 입장의 reasoning trail 을 반영해 redesign 하라".

**Anchor 재발 escalation**: ArchitectAgent 수정 후 DesignReview 재진입 시 동일 `anchor_id` 가 두 번째 debate 유발 = `anchor_recurrence_count >= 2` → debate 진입 없이 즉시 `AskUserQuestion` 사용자 escalation. AI 합의 불가능 시그널 처리.

**env=0 / env=1 동등성**: agent teams enabled context (env=1) 에서는 SendMessage 기반 continuous dialog. default subagent context (env=0) 에서는 Orchestrator round-trip polyfill (매 라운드 worker subagent one-shot spawn + transcript 누적 입력 첨부). 양쪽 동일 protocol schema 준수 — env=0 시 토큰 비용 증가 의식 필요.

**lane-agnostic 설계**: protocol contract 는 lane 정보 인자로 받는 일반 schema. Story 2 (Requirements lane 확장 — CFP-392) 가 본 Story merge 후 contract 신설 없이 trigger 조건만 추가 정의. 미래 CFP-C (CodeReview / SecurityTest) 도 동일 패턴.

정책 SSOT: [ADR-059](docs/adr/ADR-059-debate-protocol-v1.md) + [debate-protocol-v1 registry](docs/inter-plugin-contracts/debate-protocol-v1.md). Sonnet decider 자동 발동 무효 (ADR-022 Deprecated / CFP-134) 정합 — debate 발동은 PL 책무, Sonnet 책무 아님.

### FIX 루프

**판정 SSOT** = codeforge-review [`templates/review-pl-base.md`](https://github.com/mclayer/plugin-codeforge-review/blob/main/templates/review-pl-base.md) §3 (severity 종합·dedup·판정). Contract surface = [`review-verdict-v4`](docs/inter-plugin-contracts/review-verdict-v4.md) `pl_recommendation` (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE) — CFP-137 / ADR-044 cutover 후. v3 archived 참조: [`review-verdict-v3`](docs/inter-plugin-contracts/review-verdict-v3.md).

**트리거**: 설계 리뷰 FIX → ArchitectPLAgent 회귀. 구현 리뷰·구현 테스트·보안 테스트 FAIL → DeveloperPL 1차 진단 + ArchitectPLAgent 최종 판정 (parallel diagnosis).

**원인 판정 최종 결정자** (CFP-134 / ADR-035 정정 후): PL 이 자기 lane review-verdict 의 final pl_recommendation 작성. Sonnet decider 자동 발동 무효 (ADR-022 Deprecated — CFP-134). FIX root cause 원인 판정 (설계 vs 구현) 은 ArchitectPLAgent 가 DeveloperPL 1차 진단 받은 후 최종 결정. 사용자 explicit request 시에만 ad-hoc Sonnet 호출 가능.

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 ([fix-event-v1](docs/inter-plugin-contracts/fix-event-v1.md) contract, CFP-32 monopoly). GitHub Issue 라벨은 보조 (fix-ledger-sync.yml Action mirror).

**debate-protocol-v1 발동 FIX**: §10 row 의 `debate_artifact_ref` optional 필드 (fix-event-v1 1.1, CFP-391 / ADR-059) 가 Story §9 transcript section anchor link 보유 (예: `#debate-transcript-F-001`). ArchitectPLAgent re-spawn 시 transcript 가 verbatim 입력으로 흘러들어 reasoning carryover 보장. 미debate FIX 행은 `null` 또는 column 자체 생략 (backward-compat).

**§10 FIX Ledger 스키마**: `codeforge:fix-ledger-schema` 호출 (FIX 루프 진입 시). Orchestrator 단독 §10 append 독점 (fix-event-v1 contract, CFP-32). RESET 룰·max FIX 횟수 상세는 [playbook §6](docs/orchestrator-playbook.md).

> **Max FIX 3/3 + implementability reassessment + cross-lane RESET (CFP-526 / ADR-067)**: 본 단락 SSOT = `codeforge:fix-ledger-schema` skill + playbook §6.4/§6.5/§6.6. 사용자 directive 2026-05-13 — ArchitectPL 재량 implementability 평가 + escalation trigger 3종.

### 원인 판정 decision table

FIX 루프 시작 시 `codeforge:root-cause-decision` 호출 (DeveloperPL 진단 전). Failure 유형별 1차 가정 (구현/설계)·escalate 조건 전체 테이블 포함.

요약: local P1 → 구현, boundary P1 → 설계. 설계 원인 시 Change Plan 갱신 + Phase 1 follow-up PR. 구현 원인 시 Phase 2 PR commit append.

### Design / Code / Security 리뷰 책임 매트릭스

설계리뷰·구현리뷰·보안테스트 lane 진입 시 `codeforge:review-responsibility` 호출. 4 lane 체크 항목 분담 전체 테이블 포함.

요약: DesignLane=설계 결정, DesignReview=문서 감사, CodeReview=구현 품질, SecurityTest=보안 검증. 중복 지적 시 해당 ReviewPL dedup → severity 높은 쪽 채택.

### Deputy mandate 매트릭스 (codeforge-design lane) — 6 permanent + 2 CONDITIONAL

설계 lane 진입 시 `codeforge:deputy-mandate` 호출 (ArchitectPLAgent deputy spawn 결정 전). 6+2 deputy §7/§11/§13 sub별 ownership 전체 테이블 포함.

요약: SecurityArch=§7.1/§7.2/§7.3/§7.5/§7.6, OpRiskArch=§7.4(DR/rate/env/clock), DataMigrationArch=§11 schema/migration/idempotency, TestContractArch=§8.5. CONDITIONAL LiveOps·LiveOrdering = Live touching Story만 spawn ([ADR-014](docs/adr/ADR-014-operational-risk-ssot-distribution.md)).

**PMOAgent (Cross-cutting)** — Epic 창설 / Story 완료 회고 (**자동 의무 trigger** — Phase 2 PR merge 후 5분 grace, CFP-138 / [ADR-045](docs/adr/ADR-045-story-retro-mandatory-trigger.md)) / 사용자 요청 시 spawn. 단일 Story lane 게이트 비개입. 상세: [codeforge-pmo CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md).

### Lane plugin self-write boundary

**Lane plugin self-write boundary**: `codeforge:lane-self-write-boundary` skill 호출 — 각 lane plugin owner path 상세 SSOT. lane spawn 직전 Orchestrator 의무 호출.

요약: codeforge-requirements=§2·§5·§6, codeforge-design=§3·§7·§11+change-plan+ADR, codeforge-develop=§8·§8.5+Phase2PR, codeforge-pmo=§11+retro. final §9 verdict + GitHub gate label + phase transition = Orchestrator self-write (ADR-022 Deprecated 후). §10 FIX Ledger = Orchestrator 단독 (fix-event-v1 contract, CFP-32). `docs/{change-plans,adr,domain-knowledge,retros}/**` = owner agent direct write (CFP-26 Phase 0a).

## Doc Location Registry (CFP-276 / ADR-041)

codeforge plugin 의 doc taxonomy (epic_results / story_file / adr / change_plan / retro / domain_knowledge / spec / plan / decision_packet / inter_plugin_contract) 위치 SSOT = [`docs/doc-locations.yaml`](docs/doc-locations.yaml). Human-readable mirror = [`docs/doc-location-registry.md`](docs/doc-location-registry.md) (auto-generated from yaml). Lint = [`scripts/check-doc-locations.sh --full`](scripts/check-doc-locations.sh) (CI required check, branch protection 5번째). 정책 SSOT: [ADR-041](docs/adr/ADR-041-doc-location-registry.md). 새 doc type 도입 / 기존 location 변경 시 yaml row 갱신만 → codeforge upgrade 자연스러운 reflection. EPIC-RESULTS 의 issue #276 SSOT 모순 (3 문서 disagree) 해소가 본 registry 도입 동인.

## Inter-plugin Contract (CFP-29 Phase 1 후 + CFP-42 sibling backfill)

**Inter-plugin contract MANIFEST / Versioning / Write boundary**: `codeforge:inter-plugin-contract-registry` skill 호출 — contract version bump / sibling sync 결정 직전 SSOT. MANIFEST = [docs/inter-plugin-contracts/MANIFEST.yaml](docs/inter-plugin-contracts/MANIFEST.yaml). lint = [scripts/check-inter-plugin-contracts.sh](scripts/check-inter-plugin-contracts.sh).

요약: kind:contract 6 entry (review_verdict·requirements_output·design_output·develop_output·test_verdict·pmo_output). kind:registry 5 file (comment-prefix / fix-event / label-registry-v2 / debate-protocol / evidence-check-registry-v1.1). Versioning SSOT = [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md). sibling sync SSOT = [ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md). kind:registry = sibling sync 면제. review-verdict-v4 현재 버전 = **v4.3** (CFP-527 / ADR-068 carrier — `boundary_completeness_self_check_passed` + `findings[].type: "boundary-completeness"` 신설. sibling sync 의무: ADR-010 §sibling sync PR, wrapper Phase 1 merge 후).

---

## ADR (`docs/adr/` SSOT)

위치 = `docs/adr/ADR-NNN-<slug>.md` (flat, frontmatter `category:` 분류). Lookup = `Glob(docs/adr/ADR-*.md)` + `Grep` frontmatter filter → `Read`. CODEOWNERS 가 `docs/adr/**` 을 architect team review 강제 (Phase 1 PR 결재 필수). 페이지 템플릿: [codeforge-design `templates/adr.md`](https://github.com/mclayer/plugin-codeforge-design/blob/main/templates/adr.md). DesignReview 의 ADR 정합성 체크는 [codeforge-review CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) SSOT.

**안전망 ADR 분류 + 해소 기준 의무** = [ADR-058](docs/adr/ADR-058-adr-sunset-criteria-mandate.md) — frontmatter `is_transitional: true | false` (미선언 default `true` 안전망 추정, safe direction) + `## 해소 기준` 섹션 (`is_transitional: true` 시 의무, metric / who / how 3-tuple 정량 명시 / 모달 어휘 금지). amendment 시 `sunset_justification` 의무 (ratchet 차단, §결정 5). 보안 ADR default presumption = `false` (§결정 7).

**Python script-writing convention** = [ADR-061](docs/adr/ADR-061-python-script-writing-convention.md) — multi-line Python (> 5줄 또는 backslash escape 포함) 작성 시 bash heredoc 금지 + 외부 `.py` 파일 (`Write` tool → `python file.py`) 의무. `<<'EOF'` single-quoted heredoc 가 정상 verbatim transmission 보장 못함 (Windows Git Bash / MSYS2 / WSL 환경 backslash escape inconsistency — CFP-418 FIX iter 1 evidence). Script 작성 직후 sanity check 3종 의무 (diff inspection / lint re-run / sample file Read). ADR-039 subagent default 정합.

**Marketplace ↔ plugin.json atomic invariant** = [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md) — mirrored field (`name`/`version`/`description`/`author`) bump 시 3 file (plugin.json + CHANGELOG.md + marketplace.json) atomic coordination 의무. PR ordering: marketplace sync PR 선행 merge → plugin PR merge (또는 concurrent merge gate). Anti-pattern (plugin PR 선행 merge 금지). bypass = `hotfix-bypass:marketplace-atomic` label (ADR-024 Amendment 3 정합). 3-Wave drift evidence (CFP-387 / CFP-393 / CFP-423 retro) — `check-marketplace-parity.sh` (CFP-50 / ADR-023) 사후 감지 SSOT (CFP-457 cleanup — `check-marketplace-sync.sh` 중복 deprecated). **작성 시점 enforce** (CFP-441) = [`scripts/check-version-bump-atomic.sh`](scripts/check-version-bump-atomic.sh) + [`templates/github-workflows/version-bump-atomic-check.yml`](templates/github-workflows/version-bump-atomic-check.yml) PR-time 통합 channel. **Local pre-push 보완** (CFP-447, opt-in) = [`templates/.claude/hooks/pre-push.sh.sample`](templates/.claude/hooks/pre-push.sh.sample) — BEHIND-rebase awareness + atomic invariant local check (advisory; `PRE_PUSH_BLOCKING=1` 시 차단). ADR-016 (sibling sync policy) vs ADR-063 (atomic invariant) 분리 — sync 무엇 vs sync 어떻게.

**ArchitectAgent Phase 1 mechanical sync self-check 의무 (non-marketplace 영역)** = [ADR-065](docs/adr/ADR-065-architect-phase1-mechanical-self-check.md) — codeforge-design lane 의 ArchitectAgent (chief author) Phase 1 산출물 commit 직전 7-item mechanical sync checklist (label-registry sync / doc-locations regen / workflow self-app / link target Phase 분배 / MANIFEST.yaml 갱신 / section-ownership row / doc-locations row) self-check 의무. ArchitectPLAgent verdict packet `mechanical_self_check_passed: bool` 필드 (review-verdict-v4 v4.2 carrier, 현재 v4.3, ADR-008 §결정 2 정합) 로 explicit marker. false 시 FIX 의무 — ArchitectAgent re-spawn. marketplace 영역 self-check 는 ADR-063 SSOT (cross-ref only — 중복 codification 회피). 3 Story 누적 결함 evidence (CFP-393 iter 1 3건 + iter 3 1건 + CFP-411 phase-gate path). ADR-068 (semantic 4-invariant) 와 분리 운영 — verdict packet 양 별도 boolean field (ADR-065 = `mechanical_self_check_passed`, ADR-068 = `boundary_completeness_self_check_passed`).

**Boundary completeness invariants (semantic)** = [ADR-068](docs/adr/ADR-068-boundary-completeness-invariants.md) — ArchitectAgent §3 / §7 작성 시 4 semantic invariants (I-1 API contract semantic completeness / I-2 cross-module propagation completeness / I-3 unconditional vs conditional guard placement intent / I-4 wording SSOT) self-check 의무. DesignReviewPL + CodeReviewPL dual-binding cross-validate. review-verdict-v4 v4.3 (`boundary_completeness_self_check_passed: bool` + `findings[].type: "boundary-completeness"`) 의 carrier. ADR-065 (mechanical syntactic 7-item) 와 분리 운영 (verdict packet 양 별도 boolean field). wording-ssot-grep-lint = ADR-060 evidence-enforceable warning-tier 8번째 entry (`hotfix-bypass:boundary-wording`). **Amendment 1 (CFP-528, 2026-05-13)** 가 5번째 invariant I-5 dimensional empirical grounding 신설 — 10 dimension enum (latency/scale/cardinality/throughput/cost/accuracy/lifecycle/volume/rate/count) 의 quantitative parameter empirical-source annotation 의무. review-verdict-v4 v4.3 → v4.4 MINOR (`dimensional_empirical_self_check_passed` + `findings[].type: "dimensional-empirical-gap"`). ratchet 강화 (4 → 5 invariants, ADR-058 §결정 5 정합). #319 (RETRO-MCT-104) absorb close (distinct failure-class but systemic super-class).

**Evidence-enforceable promotion framework** = [ADR-060](docs/adr/ADR-060-evidence-enforceable-promotion-framework.md) — ADR-058 declaration 의 mechanical enforcement 점진 적용 SSOT (CFP-B carrier). 4-tier enum (`warning` / `blocking-on-pr` / `blocking-on-merge` / `hotfix-bypass`) + 승격 gate AND condition (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) + velocity-normalized metric (throughput 독립). Registry data SSOT = [`docs/evidence-checks-registry.yaml`](docs/evidence-checks-registry.yaml). Schema doc = [`docs/inter-plugin-contracts/evidence-check-registry-v1.md`](docs/inter-plugin-contracts/evidence-check-registry-v1.md) (kind:registry, **v1.1 — CFP-455 Amendment 2**). 첫 entry = ADR sunset criteria lint ([`scripts/check-adr-sunset-criteria.sh`](scripts/check-adr-sunset-criteria.sh) + [`templates/github-workflows/adr-sunset-criteria.yml`](templates/github-workflows/adr-sunset-criteria.yml), warning mode). Hotfix bypass channel = `hotfix-bypass:*` label family (per-entry namespace, audit-trailed exception channel — [ADR-024 Amendment 3](docs/adr/ADR-024-story-scoped-branch-policy.md) 정합). DesignReview lane MUST flag missing/ambiguous sunset criteria on touched ADRs — CFP-B carrier merge 후에도 warning mode 동안 manual gate 병행 (lint 가 advisory only). **Amendment 1 (CFP-390, 2026-05-11)**: 인벤토리 backfill SSOT — **18 entry 그룹 A** (owner_adr 정합 ADR/contract 명확 entry 만, FIX iter 1 정정 후 8 entry 그룹 B 강등) + Phase 1 (SSOT 만) / Phase 2 (registry yaml row append) scope split + tier 재계산 (branch-protection-manifest 부착 2 entry 만 blocking, 나머지 warning) + `sibling_dependencies` CFP-391 → CFP-412 정정 (Issue #396 closed without delivery, CFP-412 = 4-tier amendment 재예약 carrier) + 후속 carrier `CFP-TBD (메타 anomaly lint — `scripts/check-evidence-registry.sh` 또는 동등, 인벤토리 누락 자동 감지)` 의무 명시. **Amendment 2 (CFP-455, 2026-05-12)**: 4-tier 정식 amendment + schema v1.0 → v1.1 MINOR bump — `current_tier` 필드 optional → required 전환 + retroactive 분류 검증 (22/22 entry 보유 verified) + `sibling_dependencies` append `CFP-455` (CFP-412 폐기 history 보존) + §결정 14 메타 anomaly vs schema validation lint 분리 + 신설 §결정 15 (exit-code 3-tier 0/1/2) + §결정 16 (warning-tier bypass_label optional) + §결정 17 (retroactive reclassification immediate fail) + §결정 18 (marketplace.json sync 의무 명시 — kind:registry 자체는 sibling sync 불필요 but plugin.json MINOR bump 동반으로 ADR-063 atomic invariant 발효). 메타 schema validation lint (`scripts/check-evidence-registry.sh` + workflow) = Phase 2 PR scope, warning mode 첫 도입. **Amendment 4 (CFP-481, 2026-05-12)**: 3rd warning-tier entry `auto-phase-label` 등록 — PR open 시 4-tier inference fallback chain (branch parse / Related Issue inherit / terminal default / unclassified) 으로 phase:* label 자동 부착 (`templates/github-workflows/auto-phase-label.yml` + `.github/workflows/auto-phase-label.yml` self-app byte-identical). ADR-024 Amendment 4 동반 — `hotfix-bypass:auto-phase-label` 7번째 family member + §결정 6.A.1 branch → phase mapping SSOT 신설. label-registry-v2 v2.3 MINOR 동반 (phase:* 8 label entry `attach_owner_plugin` field 갱신).

**Normative ↔ mechanical boundary mandate (ADR-040 Amendment 3, CFP-426)** = 매 normative ADR (category = `governance` / `security` / `tooling-infrastructure` / `dogfood-out` / `lifecycle`) frontmatter 에 `mechanical_enforcement_actions[]` 필수 + 본문 §결정 N 에 mechanical action ↔ §결정 binding 의무. action name = `docs/evidence-checks-registry.yaml` entry name verbatim. retroactive 면제 (본 Amendment 3 이후 신설/Amendment ADR 만, §결정 7.C). self-application 첫 사례 = 본 ADR-040 frontmatter 자체 (§결정 7.D, 4 entry: `worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}`). DesignReview lane MUST flag missing `mechanical_enforcement_actions[]` on touched normative ADRs 부터 Amendment 3 발효 후 신설.

**Severity propagation contract (RC#8 bidirectional binding, CFP-529 Wave 3)** = [`severity-propagation-v1`](docs/inter-plugin-contracts/severity-propagation-v1.md) — review-verdict-v4 `findings[].severity` ↔ label-registry-v2 `severity:*` ↔ evidence-checks-registry `current_tier` 3-way bidirectional binding SSOT. kind:registry (sibling sync 면제, ADR-010 §결정 2). ratchet 규칙: severity bump ⇒ guard 강도 ratchet 의무 / tier 약화 = ADR-058 §결정 5 sunset_justification 의무. mechanical enforcement = CFP-529 Phase 2 `scripts/check_handoff_wording.py` (handoff wording linter — 3-direction enum forward/backward/lateral + 5 mechanical pre-screen patterns + 3 AI escalate stub patterns, 별 PR carrier).

## GitHub Workflow

`templates/github-workflows/` 22종 fixture: 9 core (`story-init.yml` · `phase-label-invariant.yml` · `story-section-1-immutable.yml` · `subissue-from-impl-manifest.yml` · `phase-gate-mergeable.yml` · `fix-ledger-sync.yml` · `post-merge-followup.yml` (ADR-026 + Amendment 1 CFP-476 — dual-source AND + terminal-phase gate / CFP-74) · `retro-mandatory.yml` ([ADR-045](docs/adr/ADR-045-story-retro-mandatory-trigger.md) / CFP-138) · `parallel-epic-conflict-check.yml` (ADR-050)) + 4 evidence-enforceable warning (`adr-sunset-criteria.yml` — CFP-389; `decision-principle-vocabulary.yml` — CFP-449; `auto-phase-label.yml` — CFP-481; **`claude-md-line-cap.yml` — CFP-506 / ADR-012 Amendment 1 §결정 6, CLAUDE.md ≤320줄 cap lint, `continue-on-error: true`, `hotfix-bypass:claude-md-line-cap` label conditional skip + audit comment 자동 발의**) + 1 atomic invariant blocking (`version-bump-atomic-check.yml` — CFP-441 / ADR-063 §결정 5) + 4 worktree-first **blocking-on-pr** (`worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}.yml` — CFP-531 / ADR-040 Amendment 5, warning → blocking-on-pr 승격) + 4 Live touching reusable workflow (`live-test-guard.yml` · `live-deploy-approval.yml` · `live-secret-policy.yml` · `kill-switch-integration-test.yml`, CFP-C). Issue Forms / branch protection / 버그 기록 등 상세 hierarchy + label 분류 + 코멘트 규칙 SSOT: [`docs/consumer-guide.md`](docs/consumer-guide.md) §1.3 + [`label-registry-v2`](docs/inter-plugin-contracts/label-registry-v2.md) + [`comment-prefix-registry-v1`](docs/inter-plugin-contracts/comment-prefix-registry-v1.md).

**Branch protection**: main 브랜치 = 4 required status check (phase-gate-mergeable + doc frontmatter + doc section + invariant-check) + `restrictions:{users:[],teams:[],apps:[]}` (direct push 차단) + **`enforce_admins: true` (admin 도 required check 통과 의무, CFP-70)**. CODEOWNERS 자동 review request 는 **도덕적 governance** — solo-dev 환경 강제 off (`require_code_owner_reviews:false` + `required_approving_review_count:0`, CFP-72). contributor 추가 시 `require_code_owner_reviews:true` + `count:1` 복원 의무 (별도 CFP). CODEOWNERS template: [`templates/CODEOWNERS.template`](templates/CODEOWNERS.template). 정책 SSOT: [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md). Rulesets / branch naming auto enforcement 는 solo-dev 가정 하 defer — contributor 추가 시 별도 CFP.

> **phase-gate-mergeable label mapping** (CFP-479): `phase:*` ↔ `gate:*` 정식 매핑 표 SSOT = [`docs/orchestrator-playbook.md` §9.7](docs/orchestrator-playbook.md#97-phase-gate-mergeable-label-mapping-cfp-479). CFP-342 anomaly = `phase:구현` / `phase:구현-리뷰` 도 **`gate:design-review-pass`** 요구 (직관적 `gate:code-review-pass` 아님 — codeforge 는 별도 code-review gate label 미도입). 라벨 변경 시 workflow yml line 195-208 + playbook §9.7 + 본 단락 + consumer-guide §2e 동시 갱신 의무.

> **CODEFORGE_CROSS_REPO_PAT rotation policy** (CFP-521 / [ADR-066](docs/adr/ADR-066-pat-rotation-policy.md)): `phase-gate-mergeable.yml` + `rate-limit-fallback-kpi.yml` 가 사용하는 단일 PAT (CFP-450 / ADR-013 Amendment 4 consolidation) 의 lifetime / scope / compromise response / audit log SSOT. 권장 rotation 90 days / 최대 lifetime 180 days. Audit log = [`docs/security/pat-rotation-log.md`](docs/security/pat-rotation-log.md) (사용자 manual entry). Consumer-facing 정책 mirror = [`consumer-guide.md §1g`](docs/consumer-guide.md). 자동 만료 reminder workflow = Phase 2 carrier.

## Story 작성 의무 (CFP-45)

**Story 작성 의무 분류**: `codeforge:story-cutoff-classification` skill 호출 — 강제 대상 / doc-only fast-path / 면제 대상 3종 분류 기준 SSOT. 요구사항 접수 직후 Orchestrator 의무 호출.

요약: 강제 = ADR 변경·에이전트 변경·workflow 변경·SSOT 의미 변경·Breaking change. doc-only fast-path = SSOT 문서 변경 + 기존 ADR Amendment + src/tests 무변경 (ADR-054). 면제 = Typo·링크수정·lint fix·README 단순 수정. **모호 시 강제 측 분류**. Story file = `mclayer/codeforge-internal-docs/<plugin-folder>/stories/<KEY>.md`. 정책 SSOT: [ADR-013](docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md).

**Branch governance** (CFP-66 / ADR-024): 모든 wrapper 변경 = Story-scoped feature branch (`cfp-NNN[-<slug>]`) + PR 경유 의무. main 직접 push 금지. 정책 SSOT: [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md).

Brainstorming/writing-plans skill: Plugin repo 작업 시 spec = `<internal-docs-clone>/<plugin-folder>/specs/`, plan = `<internal-docs-clone>/<plugin-folder>/plans/`. `codeforge:brainstorm` = Phase 0 자동 실행 (CFP-386). Consumer overlay: `story_cutoff.additional_exempt_categories[]` 확장 가능 (강제 항목 축소 불허). 본 plugin repo KEY prefix `CFP`.

## docs/stories + docs/retros 규약

Story file = `docs/stories/<KEY>.md` ([`templates/story-page-structure.md`](templates/story-page-structure.md), KEY = `<story_key_prefix>-N`). 각 lane plugin 이 owned section 직접 갱신 (§ "Lane plugin self-write boundary" 표). §1 변조 금지 invariant = `story-section-1-immutable.yml` Action 강제. Retro file = `docs/retros/<sprint>.md` (PMOAgent self-write, [`templates/retro.md`](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/templates/retro.md), `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` warning 검증).
