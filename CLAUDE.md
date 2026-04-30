# CLAUDE.md

Claude Code 범용 SW 개발 오케스트레이션 플러그인. **0 core 에이전트 (wrapper-only)** · 7 레인 구조 + `role: dev` 동적 roster로 요구사항 접수부터 보안 테스트 통과까지 자율 실행. 에이전트 상세는 각 lane plugin 의 `agents/<Name>.md` (codeforge-{review,pmo,requirements,test,develop,design} 각 repo SSOT — 본 wrapper repo 에는 agent file 없음). 공통 문서 양식은 [`templates/`](templates/) SSOT 참조. **Review subsystem (3 PL + 2 worker + base + 3 checklist)은 별도 plugin [`codeforge-review`](https://github.com/mclayer/plugin-codeforge-review)** 로 추출 (CFP-29 Phase 1). Inter-plugin contract `review_verdict v1` 은 [`docs/inter-plugin-contracts/review-verdict-v1.md`](docs/inter-plugin-contracts/review-verdict-v1.md) SSOT ([ADR-001](docs/adr/ADR-001-review-agent-unification.md) lane-agnostic 통합 + [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md) versioning). 프로젝트 shape별 Dev 구성 preset은 [`presets/`](https://github.com/mclayer/plugin-codeforge-develop/tree/main/presets) 참조.

## Plugin

이 리포는 **consumer 프로젝트가 설치해 사용하는 Claude Code 플러그인**. 프로젝트별 도메인·기술 스택·SSOT 상수는 **overlay 메커니즘**(consumer 측 `.claude/_overlay/` + SessionStart merge hook)으로 주입. 상세는 [`docs/consumer-guide.md`](docs/consumer-guide.md) 참조.

**Objective SSOT 상수** (GitHub org/repo·story_key_prefix·CODEOWNERS team·Discussions 카테고리·Milestone naming·label taxonomy)는 **`.claude/_overlay/project.yaml`** 에 structured로 기재. 에이전트는 해당 파일을 `Read`로 직접 참조. Schema: [`docs/project-config-schema.md`](docs/project-config-schema.md). Narrative 컨텍스트(도메인 해설·기술 스택 근거)는 `.claude/_overlay/CLAUDE.md`에 기재.

### Marketplace cross-repo 동기화 의무

본 플러그인은 [`mclayer/marketplace`](https://github.com/mclayer/marketplace)를 통해 사용자에게 노출된다 (`/plugins install codeforge@mclayer`). codeforge `.claude-plugin/plugin.json`의 **mirrored 필드 — `name` · `version` · `description` · `author`** — 변경 시 `mclayer/marketplace`의 [`/.claude-plugin/marketplace.json`](https://github.com/mclayer/marketplace/blob/main/.claude-plugin/marketplace.json) `plugins[name=codeforge]`의 동일 필드를 같은 Story 범위 내에서 **반드시 동기화 PR로 반영**한다 (codeforge PR 머지 직후 즉시 marketplace sync PR open·merge).

**규칙**:
- mirrored 필드 변경이 포함된 codeforge PR은 본문 / Story file §11에 "marketplace sync PR 후속 의무" 명시
- codeforge PR merge → 즉시 marketplace 측 동기화 PR open (gh API로 cross-check 후 merge)
- 비-mirrored 필드(`keywords` 등 marketplace.json schema 비대상)만 변경 시 sync 면제 (예외 사유는 Story §4·§7에 명시)
- 정식 인프라화는 cross-repo parity CI 후속 CFP에서 처리 — 자동 차단 도입 전까지 author·Orchestrator 의무

**근거**: 사용자 명시 (CFP-24, 2026-04-28). drift 시 사용자가 stale version·어긋난 description을 install하게 되어 marketplace의 단일 진입점 의미가 무너진다.

## SSOT Boundary (ADR-012)

본 wrapper CLAUDE.md content scope 는 [ADR-012](docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md) 에 따라 strictly limited:
1. **Plugin identity** (composition · marketplace sync · dependency check)
2. **Cross-cutting policy** (dogfood Story 작성 의무 · write boundary table · inter-plugin contract index · ADR list)
3. **3 SSOT 예외** (cross-lane scope, no single-plugin home): 책임 매트릭스 · 원인 판정 decision table · FIX Ledger §10 schema

Lane internal · per-lane spawn detail · severity rule detail · GitHub workflow subsection 상세는 각 lane plugin CLAUDE.md SSOT 또는 [playbook](docs/orchestrator-playbook.md) 위임.

## 세션 개시 의무 (필수 의존성 자동 확인 + 복구 or 요구)

**세션 시작 직후, 모든 작업보다 먼저** 아래 의존성의 노출·설치·인증 상태를 확인한다. 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 설치·재인증을 요구한다. 복구 완료 전까지 **모든 작업 중단** (요구사항 해석·에이전트 스폰·파일 수정·커밋 전부 금지).

### 필수 의존성 SSOT

**MCP 서버 (1종)**:
- `github` — Issue/PR/sub-issue/comment·label·milestone는 각 lane plugin self-write (codeforge-{review,pmo,requirements,test,develop,design} 별 self-write 표 참조); `docs/{change-plans,adr,domain-knowledge,retros}/**` 직접 write는 owner agent (CFP-26 Phase 0a)

**필수 플러그인 (9종)**:
- `codeforge-review@mclayer` (>= 1.0.0) — review subsystem (3 PL + 2 worker). CFP-35 v2 self-write
- `codeforge-pmo@mclayer` (>= 0.1.0) — PMO lane (PMOAgent). CFP-36
- `codeforge-requirements@mclayer` (>= 0.1.0) — Requirements lane (4 agent + 도메인 KB owner). CFP-37
- `codeforge-test@mclayer` (>= 0.1.0) — Test lane (TestAgent). CFP-38
- `codeforge-develop@mclayer` (>= 0.1.0) — Develop lane (DeveloperPL + QADev + 3 role:dev + presets). CFP-39 ζ arc 추출. 미설치 시 구현 lane 진행 불가
- `codex@openai-codex` — **codeforge-review의 CodexReviewAgent** (3 리뷰 lane 공통) 전용. RequirementsAnalyst는 별도 `codex` CLI만 의존하며 본 플러그인이 없어도 CLI만 설치돼 있으면 동작 (아래 필수 CLI 항목 참조)
- `superpowers@claude-plugins-official` — agent md 다수 스킬 의존 (brainstorming, writing-plans, systematic-debugging, test-driven-development, verification-before-completion, dispatching-parallel-agents)
- `github@claude-plugins-official` — GitHub MCP 도구 (issue_write, sub_issue_write, create_or_update_file, create_pull_request 등) 노출

**필수 CLI (2종)**:
- `codex` — RequirementsAnalyst가 `codex exec -m gpt-5.4` 호출
- `gh` — PMOAgent (Milestone), DomainAgent (Discussions Q&A), 각 lane plugin (필요 시 graphql fallback) self-call

**권장 플러그인 (4종, 미설치 시 권유만, 중단 없음)**:
- `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

### 확인·복구 절차

1. **노출 확인**:
   - MCP: `ToolSearch select:mcp__github__issue_write` 결과 확인
   - 플러그인: `~/.claude/settings.json` `enabledPlugins[<id>] == true` + `~/.claude/plugins/cache/<marketplace>/<plugin>/` 디렉토리 존재
   - CLI: `which codex`, `which gh`, `gh auth status` 가용

2. **추가 검증** (consumer 리포 기준):
   - `.github/workflows/`에 plugin 권장 6개 워크플로우 부재·SHA drift 검사 (story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync). 부재·drift 시 **알림만** (자동 복사·자동 commit 안 함)
   - `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` 부재 알림
   - `.github/PULL_REQUEST_TEMPLATE.md` 부재 알림
   - `CODEOWNERS` 파일 architect/domain-expert team 매핑 부재 알림

3. **자동 복구 시도** (사용자 개입 없이 가능한 경우):
   - 플러그인 cache 있으나 `enabledPlugins == false` → `~/.claude/settings.json` 직접 편집해 `true` 토글 후 세션 재시작 안내

4. **사용자 요구** (자동 불가 · blocking wait):
   - GitHub MCP 미인증 → `/mcp` 재인증 요청
   - 플러그인 cache 부재 → `/plugins install <name>@<marketplace>` 실행 요청
   - `codex` / `gh` CLI 부재 → 설치 가이드 제시 후 응답 대기
   - `gh auth status` 실패 → `gh auth login` 요청

상세 절차는 [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) §1.1 체크리스트 0번 참조.

## Development Agent Team

Wrapper agent **0개** (ζ arc 완료, [ADR-009](docs/adr/ADR-009-wrapper-only-decomposition.md)). Orchestrator (top-level Claude 세션) 가 6 lane plugin 의 agent 를 spawn.

| Lane | Plugin | Agent count | SSOT |
|---|---|---|---|
| 요구사항 | codeforge-requirements | 4 (PL + DomainAgent + RequirementsAnalyst + Researcher) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/CLAUDE.md) |
| 설계 | codeforge-design | 7 (PL + ArchitectAgent chief + 5 deputy) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
| 설계리뷰 / 구현리뷰 / 보안테스트 | codeforge-review | 5 (3 PL + 2 worker) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) |
| 구현 | codeforge-develop | 5 (PL + QADev + 3 role:dev core) + preset/overlay 동적 | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-develop/blob/main/CLAUDE.md) |
| 구현테스트 | codeforge-test | 1 (TestAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-test/blob/main/CLAUDE.md) |
| Cross-cutting | codeforge-pmo | 1 (PMOAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) |

각 lane plugin 의 agent 역할·동작은 해당 plugin CLAUDE.md SSOT. 본 표는 composition map 만.

**주체 명칭**: **Orchestrator** = 최상위 Claude 세션 (모든 Agent 툴 스폰, 토큰 예산 소유) · **(Human) 사용자** = 인간 행위자 · **Cross-cutting** = 모든 레인에 걸쳐 작동하는 에이전트 (PMOAgent).

리뷰 워커 통합 근거: [ADR-001](docs/adr/ADR-001-review-agent-unification.md) (3 lane × 2 vendor → 2 lane-agnostic worker). [Inter-plugin Contract `review_verdict`](docs/inter-plugin-contracts/review-verdict-v2.md) versioning: [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md).

## 레인 7개 · 단계 정의

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트
```

모든 Story는 **full 7 레인** 통과. Fast-path 없음 (단 **Hotfix 경로** 2종은 예외 — 운영 장애 대응, 사후 감사 의무. 상세는 [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) §10 참조).

**1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항 + 설계 + 설계리뷰 lane): `docs/stories/<KEY>.md` §1-7 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md`
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane): `src/**` + `tests/**` + `docs/stories/<KEY>.md` §8-11 append

**레인 진입 전 Preflight 체크 의무** — 각 레인 진입 직전 Orchestrator가 3개 체크 수행 (phase 라벨 정합 / docs file 선행 섹션 / 외부 의존성 가용). FAIL 시 block+report. 상세는 playbook §3B.

- **요구사항**: 사용자가 GitHub Issue Forms (story.yml) 제출 → `story-init.yml` Action이 자동 `<KEY>` 번호 계산 + `docs/stories/<KEY>.md` 생성 (§1 verbatim, §2-11 placeholder) + Phase 1 PR 자동 open + Issue body link 변환 → RequirementsPLAgent 아래 **병렬** (DomainAgent · Analyst · Researcher 동시 스폰, 각자 독립 관점) → RequirementsPL이 세 결과 dedup·상충 조정 → §2/§5/§6 직접 self-write + §3-4 갱신 (codeforge-requirements self-write 표)
- **설계**: ArchitectPLAgent가 CodebaseMapper(변호자) · Refactor(혁신자) · SecurityArchitectAgent(위협 변호자) · TestContractArchitectAgent(QA perspective contributor) · DataMigrationArchitectAgent(데이터 무결성 변호자) **5 deputy 병렬 스폰** → ArchitectAgent(chief author)가 통합 → Change Plan 확정 (§7 보안 설계 + §8 Test Contract + §11 데이터 마이그레이션 포함) → ArchitectAgent가 `docs/change-plans/<slug>.md` + 신규 `docs/adr/ADR-NNN-<slug>.md` direct write (CFP-26 Phase 0a 후) + ArchitectAgent 가 Story file §7/§3/§11 직접 self-write (CFP-40 codeforge-design 추출 후 — codeforge-design self-write 표)
- **설계 리뷰**: DesignReviewPL이 Claude/Codex 설계 리뷰 종합 → PASS 시 `gate:design-review-pass` 라벨 부착 → Phase 1 PR mergeable → merge → 구현 진입 / FIX 시 ArchitectPLAgent 회귀 → ArchitectAgent (chief author) 재스폰 (최대 3회)
- **구현**: Phase 2 PR open (DeveloperPL 이 첫 commit 준비 후 직접 `mcp__github__create_pull_request` — codeforge-develop self-write 표). Orchestrator가 QADev + DeveloperPL 병렬 스폰. DevPL이 프로젝트 `role: dev` roster를 동적 discover해 의존성 없는 한 **모두 병렬** 스폰. ArchitectPLAgent가 stateless 재스폰되어 매핑표 감사
- **구현 리뷰**: CodeReviewPL이 Claude/Codex 코드 리뷰 종합 → PASS 시 구현 테스트 진입 / FIX 시 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (최대 3회)
- **구현 테스트**: TestAgent (기능 → 성능 순차). ALL PASS 시 보안 테스트 진입 / FAIL 시 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (무제한)
- **보안 테스트**: 1차 layer = Dependabot/CodeQL/Secret Scanning/Push Protection (GitHub native). 2차 layer = SecurityTestPL이 Claude/Codex 보안 테스트 종합 (OWASP·CWE·CVE·trust boundary·credential). PASS 시 `gate:security-test-pass` 라벨 → Phase 2 PR mergeable → merge → Story 완료 / FAIL 시 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (무제한)

## 오케스트레이션 규칙

> **Orchestrator 행동 SSOT**: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) — 세션 생명주기, 사용자 상호작용, 스폰 프롬프트 템플릿, 병렬 스폰 판단, docs file 동기화 체크리스트, FIX 상태 머신, 세션 재개 복원, 토큰 예산, 트러블슈팅.

### 플랫폼 제약
하위 에이전트는 Agent 툴 사용 불가 — 재귀 스폰 금지. 모든 스폰은 최상위 Claude가 직접. 서브에이전트 간 직접 통신 불가 (Orchestrator 경유).

### 컨텍스트 전달 (docs file SSOT + Context Packet)

각 Story마다 **`docs/stories/<KEY>.md`** 파일이 컨텍스트 단일 출처(SSOT). 에이전트 프롬프트에는 기본적으로 **docs file 경로만 주입**하고, 필요한 내용은 에이전트가 직접 `Read(docs/stories/<KEY>.md)`로 fetch.

**Context Packet 주입** (설계·구현·리뷰 레인): Orchestrator가 섹션 캐시를 유지해 에이전트 프롬프트에 packet 형태로 필요 섹션을 직접 삽입 → 반복 fetch 회피. 상세는 playbook §12.

**§0 Live Progress** (ephemeral derivative cache): `.claude-work/progress/<KEY>.md` (Orchestrator owner, gitignored). M3 hierarchical + S3 completion snippet 형식. 정상 흐름은 Orchestrator가 cache patch, 재개·손상 시 state source(Story §10 + phase label + §-fill)에서 재 derive. 상세는 playbook §14.

**Project Config Packet** (RequirementsPL·DomainAgent·PMO·ArchitectPLAgent — 각 lane plugin): `.claude/_overlay/project.yaml` slice도 packet으로 주입 → GitHub 호출 에이전트의 반복 `Read` 회피. 상세는 playbook §12.5.

**Story file 위치**: `docs/stories/<KEY>.md` (KEY = `<github.story_key_prefix>-N`, 예: `PLG-7`). story-init.yml Action이 자동 생성 (요구사항 lane 진입 시).

**생성·갱신 책임**: 각 lane plugin self-write — owner section 별로 분산. 자세한 분담은 § "Lane plugin self-write boundary" 절 참조.

**섹션 갱신 path**: 각 lane plugin 이 자기 owned section 을 직접 `Edit(docs/stories/**)`. multi-writer 영역 (§9 review verdict — Phase 별 다른 Review PL self-write) 은 lane 별 phase 진행 순서에 따라 자연 직렬화.

섹션 규격·단계별 책임 상세는 각 lane plugin 의 self-write 표 SSOT (codeforge-{review,pmo,requirements,test,develop,design} CLAUDE.md) 참조.

### Never-skippable 에이전트

- **요구사항**: **RequirementsPLAgent**, **DomainAgent**, **RequirementsAnalystAgent**, **ResearcherAgent** (세 서브 에이전트는 PL 산하 병렬 관점 제공자로 전원 필수)
- **설계**: **ArchitectPLAgent**, **ArchitectAgent**, **CodebaseMapperAgent**, **RefactorAgent**, **SecurityArchitectAgent**, **TestContractArchitectAgent**, **DataMigrationArchitectAgent**
- **설계 리뷰** (codeforge-review plugin): **DesignReviewPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent** (워커는 lane=design packet 수령)
- **구현**: **DeveloperPLAgent**, **QADeveloperAgent**
- **구현 리뷰** (codeforge-review plugin): **CodeReviewPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent** (워커는 lane=code packet 수령)
- **구현 테스트**: **TestAgent**
- **보안 테스트** (codeforge-review plugin): **SecurityTestPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent** (워커는 lane=security packet 수령)
조건부 생략: `role: dev` 에이전트만 해당 (Change Plan이 해당 에이전트 소유 경로 미변경 시). 요구사항·설계 레인의 서브 에이전트는 전원 non-skippable — "조사할 것 없음" 판단도 독립 관점의 하나이므로 각자 스폰되어 명시적으로 결과를 반환해야 한다 ("null 결과"도 유효한 관점).

**PMOAgent**는 Never-skippable이 아니며 Cross-cutting 트리거 기반 스폰: Epic 창설 1회 / Story 완료 회고 1회 / 사용자 요청 시. 단일 Story 레인 게이트에 개입 없음.

### 스폰 시퀀스

각 lane 별 상세 스폰 흐름·branch logic 은 [playbook §3 스폰 시퀀스](docs/orchestrator-playbook.md) SSOT. 요약:

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 구현테스트 → 보안테스트
```

각 lane 진입 시 Orchestrator 가 해당 lane plugin 의 PL agent 를 spawn → PL 이 sub-agent 병렬 spawn (요구사항 3개 / 설계 5 deputy / 리뷰 2 worker / 구현 N role:dev). PL 산출물 종합 후 Orchestrator 에 verdict return → 다음 lane 라우팅.

**Clarification 재스폰**: 서브에이전트 one-shot 이라 PL ↔ 서브 continuous dialog 불가 → PL 이 Orchestrator 에 재 spawn 의뢰 (각 lane plugin CLAUDE.md SSOT).

**Track 병렬** (R7 — 설계리뷰 PASS 시): Track A (DesignReviewPL self-write merge gate) ∥ Track B (DeveloperPL Phase 2 PR 준비). 상세 [playbook §3.1](docs/orchestrator-playbook.md).

### FIX 루프

**판정 SSOT**: codeforge-review 의 [`templates/review-pl-base.md`](https://github.com/mclayer/plugin-codeforge-review/blob/main/templates/review-pl-base.md) §3 — severity 종합·dedup·종합 판정. codeforge core 입장에서는 [`docs/inter-plugin-contracts/review-verdict-v2.md`](docs/inter-plugin-contracts/review-verdict-v2.md) §3.2 review_verdict.status 필드 (PASS / FIX / FIX_DISCRETIONARY) 가 contract surface.

**트리거** (review-pl-base.md §3 결과 FIX 또는 FIX 재량):
- 설계 리뷰 → ArchitectPLAgent 회귀
- 구현 리뷰 / 구현 테스트 / 보안 테스트 FAIL → DeveloperPL 1차 진단 + ArchitectPLAgent 최종 판정 (parallel diagnosis, R4)

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 (CFP-32 monopoly · `fix-event-v1` contract). GitHub Issue 라벨은 보조 지표 (fix-ledger-sync.yml Action 자동 mirror).

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
| **보안 테스트 P0 injection·credential hardcode** | 구현 | 코드 단위 결함 |
| **보안 테스트 P1 암호학 오용·CVE** | 구현 | 코드 수정·버전 업그레이드로 해결 |
| **보안 테스트 P1 boundary 권한 일관성** | **설계** | 여러 파일·레이어 공통 지침 부재 |
| **보안 테스트 P0 trust boundary 위반** | 구현 | §7.1에 boundary 부재·모순 또는 §7.1과 코드 boundary 불일치 → 설계 |
| **보안 테스트 P0 auth/authz 결함** | 구현 | §7.3 인증·권한 모델 자체 결함 → 설계. 모델은 맞으나 구현 결함 → 구현 유지 |
| **구현 테스트 Migration FAIL · data integrity 위반 · rollback 실패** | 구현 | §11.1-§11.5 부재·모순 (schema 영향 누락 / Migration 전략 부재 / Rollback 경로 부재 / invariant 정의 부재) → 설계. 모델은 맞으나 script 결함 → 구현 유지 |

**P1 품질 local vs boundary 판정 기준**:
- **local**: finding이 1개 파일 또는 1개 함수 범위에 한정, 설계 결정과 무관한 개별 구현 결함
- **boundary**: finding이 여러 파일·계층에 걸침, 또는 Change Plan에 "이 경계·패턴 어떻게 가야 하는지" 지침이 부족해서 발생한 이슈
- DeveloperPL이 1차 진단 시 이 분류를 포함 → ArchitectPLAgent 최종 판정

- **설계 원인 판정 시**: Change Plan 갱신 (특히 §3 도입할 설계 / §6 리팩터링 선행 / §7 보안 설계 / §8 Test Contract 중 해당 항목) → Phase 1 follow-up PR → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, Phase 2 PR commit append → 구현 리뷰 재실행

### Review severity 종합 규칙

3 review/test PL(DesignReviewPL · CodeReviewPL · SecurityTestPL) 공통 — **codeforge-review plugin 소속**. SSOT는 codeforge-review repo의 `templates/review-pl-base.md` §3 (dedup · 종합 판정 표 · noise 분류). 본 CLAUDE.md에서는 SSOT 참조만 두고 표를 재인용하지 않는다.

### Design / Code / Security 리뷰 책임 매트릭스 (중복 방지)

네 레인의 체크 항목이 겹치지 않도록 분담. 한쪽에서 커버된 항목은 다른 쪽에서 재검토하지 않음.

| 체크 항목 | DesignLane | DesignReview | CodeReview | SecurityTest |
|-----------|:----------:|:------------:|:----------:|:------------:|
| Change Plan 완결성(§1-10 섹션 존재) | — | ✅ | — | — |
| ADR 정합성(§3·§7 위반 여부) | — | ✅ | — | — |
| CodebaseMapper ↔ Refactor 균형 | — | ✅ | — | — |
| API 계약 일관성 (라우트·스키마·타입) | — | ✅ | — | — |
| §8 Test Contract 타당성 | — | ✅ | — | — |
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

### PMOAgent 프로젝트 관리 (Cross-cutting)

단일 Story 레인 게이트 밖 **Cross-cutting 감사·회고·패턴 분석 전담**. 요구사항 해석은 RequirementsPLAgent 영역.

**스폰 시점**:
- **Epic 창설 시** (1회): Scope 분해 자문 — Story 분해·의존성 식별·**병렬/순차 판정** (파일 경로 disjoint / 인터페이스↔구체 분리 / 공유 자원 충돌 기준, 상세 [PMOAgent.md §1](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/agents/PMOAgent.md))
- **Story 완료 시**: 회고 감사 (Preflight/Gate 준수·§8/§8.5 매핑·FIX evidence pack 완성도·토큰 예산)
- **사용자 요청 시** (주기적): Cross-Story 패턴 보고서 (FIX 반복 유형·ESCALATE 트렌드·성능 회귀·코드 핫스팟)

**산출물**:
- `[PMOAgent 회고]` / `[PMOAgent Cross-Story 감사]` 보고서 (PMOAgent 직접 Story §11 self-write + docs/retros/<sprint>.md owner direct write — codeforge-pmo)
- **ADR 후보 발의** (반복 패턴이 "설계 지침 부재"로 해석 시 `status=Proposed` ADR draft를 write queue에 제출)
- 세션 회고 synthesize (playbook §8.3 테이블 채움)

상세는 [`agents/PMOAgent.md`](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/agents/PMOAgent.md).

### Lane plugin self-write boundary

`docs/**` + GitHub Issue/PR/comment + label 영역의 write 책임은 lane plugin 별로 분산. wrapper repo 자체에는 agent 0개 — Orchestrator 가 lane plugin 을 spawn 하면 lane plugin 이 자기 owner section 을 직접 write.

**Lane plugin owner path**:

| Lane plugin | docs/ self-write 영역 | GitHub self-write |
|---|---|---|
| codeforge-requirements | `docs/stories/<KEY>.md §2·§5·§6`, `docs/domain-knowledge/<area>/<topic>.md` | `[요구사항]` prefix comment, phase:요구사항→phase:설계 transition, Discussions Q&A routing |
| codeforge-design | `docs/stories/<KEY>.md §3·§7·§11`, `docs/change-plans/<slug>.md`, `docs/adr/ADR-NNN-<slug>.md` | `[설계]` prefix comment, phase:설계→phase:설계-리뷰 transition |
| codeforge-review | `docs/stories/<KEY>.md §9` (각 Review PL) | `[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]` prefix comment, gate:design-review-pass / gate:security-test-pass label, phase transition (review-verdict-v2) |
| codeforge-develop | `docs/stories/<KEY>.md §8·§8.5`, Phase 2 PR creation | `[구현]` prefix comment, phase:구현→phase:구현-리뷰 transition |
| codeforge-test | (§9.3 은 Orchestrator 가 verdict receipt 후 처리 — lane plugin 직접 write 안 함) | `[구현-테스트]` prefix comment |
| codeforge-pmo | `docs/retros/<sprint>.md`, `docs/stories/<KEY>.md §11`, Epic Issue body, Milestone description | `[PMO]` prefix comment, Epic Milestone via gh api |

**Wrapper Orchestrator 단독 영역**:
- `docs/stories/<KEY>.md §10` FIX Ledger append (CFP-32 monopoly · `fix-event-v1` contract)
- general `docs/**` write (lane plugin owner 외)
- branch protection · CI workflow · cross-plugin schema templates

**4 single-owner doc** (CFP-26 Phase 0a 이후): `docs/{change-plans,adr,domain-knowledge,retros}/**` 는 owner agent direct write — lane plugin 의 ArchitectAgent / DomainAgent / PMOAgent 자기 owner path write.

문서화 표준 4 single-owner doc 템플릿은 [`templates/`](templates/) — change-plan / adr 현재 존재, domain-knowledge schema / retro schema CFP-27 신설. owner agent는 본인 owner path write 시 해당 템플릿 schema 준수 필수 — `scripts/check-write-permission-redistribution.sh` (CFP-26) + 향후 frontmatter/section schema lint (CFP-27)에서 강제.

자세한 owner path / mechanism / trigger 는 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 (codeforge-{review,pmo,requirements,test,develop,design}) 참조.

### Codex CLI / 플러그인 필수
- CodexReviewAgent (codeforge-review plugin 소속): Codex 플러그인 (3 리뷰 lane 공통 — 미설치 시 설계 리뷰·구현 리뷰·보안 테스트 모두 진행 불가). codeforge-review plugin 자체도 설치 의무 (CFP-29 BREAKING)
- RequirementsAnalyst: `codex` CLI
- 미설치 시 해당 레인 진행 불가, Orchestrator가 설치 안내 후 중단

### 병렬 스폰 권장
- **요구사항**: **DomainAgent · RequirementsAnalyst · Researcher 병렬** — 셋 모두 공통 입력에서 각자 키워드·관점 자체 도출. PL이 synthesizer
- **설계**: **5 deputy 병렬** (CodebaseMapper · Refactor · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent) — 5 deputy 모두 원 소스 직접 읽기, 한쪽이 다른 쪽의 요약에 의존하지 않음. ArchitectAgent (chief author)가 통합, ArchitectPLAgent가 검수
- **구현**: QADev + DevPL의 `role: dev` roster (의존성 없는 한 모두 병렬)
- **리뷰·보안**: Claude + Codex 병렬 (Design Review / Code Review / Security Test 각 레인)

**Clarification 재스폰 공통 절차** (요구사항·설계 레인): 서브에이전트는 one-shot이라 PL↔서브 continuous dialog 불가. PL이 통합 중 추가 질의가 필요하면 → Orchestrator에 "<에이전트> 재스폰 요청 + clarification context + 이전 출력 pointer" 전달 → Orchestrator가 해당 에이전트를 신규 스폰. 이것이 "각 책임 종료 전까지 보조" 메커니즘의 실제 구현.

## Inter-plugin Contract (CFP-29 Phase 1 후 + CFP-42 sibling backfill)

codeforge core 가 외부 plugin과 통신할 때의 typed schema. wrapper repo 의 [docs/inter-plugin-contracts/](docs/inter-plugin-contracts/) 디렉터리는 두 종류 보유:

### kind:contract (typed inter-plugin schema, 6 entry / 7 file)

[docs/inter-plugin-contracts/MANIFEST.yaml](docs/inter-plugin-contracts/MANIFEST.yaml) 가 SSOT. lint 는 [scripts/check-inter-plugin-contracts.sh](scripts/check-inter-plugin-contracts.sh).

| Contract | Producer plugin | Files (wrapper sibling) |
|---|---|---|
| `review_verdict` | codeforge-review | review-verdict-v1.md (Archived) · review-verdict-v2.md (Active) |
| `requirements_output` | codeforge-requirements | requirements-output-v1.md (Active) |
| `design_output` | codeforge-design | design-output-v1.md (Active) |
| `develop_output` | codeforge-develop | develop-output-v1.md (Active) |
| `test_verdict` | codeforge-test | test-verdict-v1.md (Active) |
| `pmo_output` | codeforge-pmo | pmo-output-v1.md (Active) |

각 wrapper sibling 은 lane plugin canonical 의 verbatim mirror + "**상위 SSOT 위치**" 섹션. canonical 변경 시 wrapper sibling sync PR 후속 의무 ([ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)).

### kind:registry (cross-cutting protocol, 3 file)

wrapper-owned. 본 lint scope 밖 — `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

- [comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) — 11 phase prefix taxonomy
- [fix-event-v1.md](docs/inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger writer monopoly
- [label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) — phase/gate/fix label taxonomy

### Versioning + sync 정책

- [ADR-008 Inter-plugin Contract Versioning](docs/adr/ADR-008-inter-plugin-contract-versioning.md): SemVer 룰 (v1.x backward-compat, v2.0 BREAKING + 양쪽 plugin 동시 bump + 새 ADR)
- [ADR-010 Inter-plugin Contract Sibling Sync](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md): canonical/sibling 책임 + sync 트리거 + 신규 contract 추가 4단계 절차

### Write boundary

각 lane plugin 이 자기 contract 의 producer + self-writer. wrapper Orchestrator 는 contract verdict 에 응답해 다음 lane 라우팅·Story §10 FIX Ledger 만 처리. 상세 흐름은 [docs/orchestrator-playbook.md](docs/orchestrator-playbook.md) 참조.

---

## ADR (`docs/adr/` SSOT)

- 위치: `docs/adr/ADR-NNN-<slug>.md` (flat). frontmatter `category:` 필드로 분류 (Team & Process / Architecture / Data & Storage / Infrastructure / UX 등 — consumer overlay가 도메인별 추가 카테고리 정의)
- 목록: `Glob(docs/adr/ADR-*.md)` + `Grep`으로 frontmatter category·status 필터
- 상세: `Read(docs/adr/ADR-NNN-<slug>.md)`
- 세션 시작 시 ADR 목록 조회, 결정 사항 번복 금지
- 설계 결정마다 신규 ADR 생성 (번호 = 기존 최대 + 1)
- CODEOWNERS가 `docs/adr/**`을 architect team에 자동 review 강제 → ADR 변경은 Phase 1 PR로 architect 결재 필수

### 생성 기준
라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 도메인 핵심 개념 (consumer overlay가 도메인 특화 기준 추가)

### DesignReview ADR 정합성 체크 (필수)

DesignReviewPL 프롬프트에 명시:
- Story file §3에서 관련 ADR 목록 fetch (`Glob` + `Read`)
- Change Plan 결정이 ADR 결정을 **위반**하는가 explicit 검토
- Change Plan §7 보안 설계 결정이 ADR 결정을 **위반**하는가 explicit 검토
- 위반 발견 시 **P0 severity 고정**
- 설계 의도가 ADR 변경이면 "신규 ADR 필요" 발견사항으로 기록 (신규 ADR 없이 ADR 변경 금지)

### 페이지 템플릿
[`templates/adr.md`](https://github.com/mclayer/plugin-codeforge-design/blob/main/templates/adr.md) 참조. frontmatter (adr_number / title / status / category / date / related_files) + 본문 섹션 (`## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램 / ## 관련 파일`).

**CFP-27부터** `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` 가 본 schema를 검증 (warning 모드 — CFP-28 strict 전환).

## 버그 기록 (GitHub Issues)
- Issue Forms: `.github/ISSUE_TEMPLATE/bug.yml`. Severity dropdown (P0/P1/P2)
- 신규 버그: Orchestrator 또는 해당 lane agent 가 `mcp__github__issue_write(action='create', title=..., body=..., labels=['type:bug', 'component:<name>'])`
- 해결 시: PR body에 `Closes #<bug-issue>` keyword → merge 시 자동 close (GitHub native)

## GitHub Workflow

사용자 요구사항 접수부터 PR merge까지의 모든 의사결정·협업을 GitHub에 영속 기록. GitHub Issue/PR/comment·label·milestone 쓰기는 각 lane plugin self-write (§ "Lane plugin self-write boundary" 표 참조).

### 계층
- **Epic** = 사용자 요구사항 1건. **Milestone (due date·% 진행률 자동) + Issue (`type:epic` 라벨, body=narrative)**. Orchestrator가 PMOAgent 스폰 → PMOAgent 가 Milestone + Epic Issue 직접 생성 (codeforge-pmo self-write)
- **Story** = PR 1쌍 (Phase 1 + Phase 2 = Change Plan 1건). **Issue (`type:story` 라벨)**. Milestone에 속함. Orchestrator(필요 시 PMO 조언) scope 분해 시 확정된 독립 작업 단위만 생성
- **하위 작업(sub-issue)** = Impl Manifest 파일 단위. **Sub-issue (`impl-manifest` 라벨)**. Phase 2 PR이 §8.5 매핑표 commit 시 `subissue-from-impl-manifest.yml` Action이 자동 생성. PR merge 시 parent close에 따라 자동 close
- **Audit Story** = hotfix 사후 감사 1건. `audit:post-hotfix` 라벨. hotfix merge 다음 세션 개시 시 Orchestrator가 Issue Forms (audit.yml)로 자동 생성

### 상태 + Phase Label 방식

GitHub Issue 기본 2-state (`open`/`closed`). 단계는 **phase label**로 표현. PR merge 시 GitHub native `Closes #N` keyword가 Issue 자동 close.

```
[Issue Form 제출] story-init.yml Action 자동 실행
   ↓ docs file 생성 + Phase 1 PR 자동 open + 라벨 phase:요구사항 부착
[phase:요구사항 → phase:설계]   (RequirementsPL 이 phase 라벨 부착 — codeforge-requirements self-write, phase-label-invariant.yml 가 기존 detach)
   ↓ ArchitectAgent (chief author) Change Plan 확정
[phase:설계 → phase:설계-리뷰]
   ↓ 설계 리뷰 PASS → DesignReviewPL 이 gate:design-review-pass 라벨 부착 (review-verdict-v2 self-write)
[Phase 1 PR mergeable → merge → Issue label phase:구현]
   ↓ Phase 2 PR open
[phase:구현 → phase:구현-리뷰]
   ↓ 구현 리뷰 PASS
[phase:구현-리뷰 → phase:구현-테스트]
   ↓ 구현 테스트 PASS
[phase:구현-테스트 → phase:보안-테스트]
   ↓ 보안 테스트 PASS → SecurityTestPL 이 gate:security-test-pass 라벨 부착 (review-verdict-v2 self-write)
[Phase 2 PR mergeable → merge → "Closes #<Story Issue>" → Issue 자동 close]
status=closed
```

### FIX 루프 라벨 규칙

(`fix-ledger-sync.yml` Action이 §10 commit 감지 시 자동 부착)

- **설계 리뷰 P0/P1**: `phase:설계-리뷰 → phase:설계` + `fix:설계-리뷰-retry` 라벨 추가 + `[FIX #N]` 코멘트 (Action이 자동 mirror)
- **구현 리뷰 P0/P1**: `phase:구현-리뷰 → phase:구현` + `fix:구현-리뷰-retry` 라벨 추가 + `[FIX #N]` 코멘트
- **구현 테스트 FAIL**: `phase:구현-테스트 → phase:구현` + `fix:구현-테스트-retry` 라벨 추가 + `[FIX #N]` 코멘트
- **보안 테스트 P0/P1**: `phase:보안-테스트 → phase:구현` (구현 원인) 또는 `phase:보안-테스트 → phase:설계` (설계 원인) + `fix:보안-테스트-retry` 라벨 추가 + `[FIX #N]` 코멘트

카운터는 Story file §10 FIX Ledger SSOT, GitHub 라벨은 보조 지표.

### 코멘트 규칙 (lane plugin self-write)

형식·phase prefix(10 lane prefix + Orchestrator Preflight 1 = 총 11종). 각 lane plugin 이 자기 phase prefix 로 `mcp__github__add_issue_comment` 직접 호출 — 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 (codeforge-{review,pmo,requirements,test,develop,design}) 참조.

### GitHub 워크플로우 자동화

`templates/github-workflows/` SSOT, consumer가 `.github/workflows/`로 복사. SessionStart hook이 부재·drift 검사. 6종:

- `story-init.yml`: Issue Forms (story.yml) 제출 → docs file 생성 + Phase 1 PR + Issue body 변환
- `phase-label-invariant.yml`: `phase:*` single-active 강제
- `story-section-1-immutable.yml`: §1 line range 변경 PR 자동 reject
- `subissue-from-impl-manifest.yml`: §8.5 매핑표 → file 단위 sub-issue 자동 생성
- `phase-gate-mergeable.yml`: PR body의 `Related|Closes|Fixes|Resolves: #N` 패턴으로 linked Story Issue 추출 → 해당 **Issue의 phase + gate 라벨** 검사 (Issue가 SSOT, PR 라벨 sync 불필요). Issue 라벨 변경 시 linked PR 재평가 (issues `labeled/unlabeled` 트리거). required status check
- `fix-ledger-sync.yml`: PR 또는 main push 시 docs §10 전체 파싱 → 새 Iter 행마다 Issue `[FIX #N]` 코멘트 + `fix:<레인>-retry` 라벨 자동 (idempotent — 이미 mirror된 Iter는 skip)

상세는 [docs/consumer-guide.md](docs/consumer-guide.md) §1.3 참조.

### Branch protection + Required status checks
- Main 브랜치: `phase-gate-mergeable` required status check + CODEOWNERS review 필수
- CODEOWNERS: `docs/adr/**`·`docs/change-plans/**`·`docs/stories/**`·`.github/workflows/**` → `@org/architects` / `docs/domain-knowledge/**` → `@org/domain-experts`. 템플릿: [`templates/CODEOWNERS.template`](templates/CODEOWNERS.template)

### Labels 체계

- `type:*`: `type:epic`, `type:story`, `type:bug`, `impl-manifest` (sub-issue)
- `phase:*` (single-active 1개): `phase:요구사항`, `phase:설계`, `phase:설계-리뷰`, `phase:구현`, `phase:구현-리뷰`, `phase:구현-테스트`, `phase:보안-테스트`
- `gate:*` (review 통과 표시): `gate:design-review-pass`, `gate:security-test-pass`
- `fix:*` (누적): `fix:설계-리뷰-retry`, `fix:구현-리뷰-retry`, `fix:구현-테스트-retry`, `fix:보안-테스트-retry`
- `component:*` (`project.yaml` `labels.components`에 정의)
- `adr:NNN`
- `hotfix:minimal`, `hotfix:critical`, `audit:post-hotfix`

### 대시보드 (GitHub Issues search syntax)
- 현재 구현 리뷰 중: `repo:<org>/<repo> is:issue is:open label:"phase:구현-리뷰"`
- 현재 설계 리뷰 중: `repo:<org>/<repo> is:issue is:open label:"phase:설계-리뷰"`
- 현재 보안 테스트 중: `repo:<org>/<repo> is:issue is:open label:"phase:보안-테스트"`
- FIX 대상: `repo:<org>/<repo> is:issue is:open label:"fix:설계-리뷰-retry","fix:구현-리뷰-retry","fix:구현-테스트-retry","fix:보안-테스트-retry"`
- Story 전체: `repo:<org>/<repo> is:issue is:open label:type:story`
- Projects v2 board view에서도 phase·milestone·custom field별 가시성 제공

### 원문 위치
GitHub Issue/PR은 **워크플로우 상태·이벤트 로그**만. 구조화된 원문은 각 도구 유지:
- **요구사항·컨텍스트·서사**: `docs/stories/<KEY>.md` (Git-versioned). 섹션 1-11
- **설계 실행 명세**: `docs/change-plans/<slug>.md` (Git-versioned). Story file §7 요약 미러링
- **설계 결정(ADR)**: `docs/adr/ADR-NNN-<slug>.md` (Git-versioned). Story file §3에서 인용
- **코드 리뷰 원문**: GitHub PR 설명·코멘트·review. Story file §9에 요약 집계

## Story 작성 의무 (모든 변경 적용)

매 변경 시작 시 Orchestrator가 cutoff 분류 → 강제/면제 결정. **모호 시 강제 측 분류** (false positive < false negative). 이 정책은 plugin 자체와 consumer 프로젝트 모두에 적용.

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

면제 시 commit body에 `Story 면제 사유: <이유>` 1줄 명시 의무. 사유 없는 면제 commit은 PR review에서 reject 대상.

### Consumer overlay 확장

Consumer는 `.claude/_overlay/project.yaml`의 `story_cutoff.additional_exempt_categories[]`로 도메인 특화 면제 항목을 추가할 수 있다 (예: "auto-generated migration files", "vendored library updates"). **강제 항목 축소는 불허** — 안전 방향(면제 추가) 확장만 허용. Schema는 [`docs/project-config-schema.md`](docs/project-config-schema.md) §2 참조.

### Plugin 자체 적용 (dogfooding)

이 plugin repo도 동일 정책 적용. KEY prefix는 `CFP` (CodeForge Plugin). Plugin meta 변경은 §8 Test Contract / §9 리뷰·테스트 결과 등 무의미한 lane을 `N/A — <사유>`로 명시 (lane 게이트 면제 audit trail). 인프라 자동화는 단계적 도입:

- **1단계 완료** (CFP-1): Story 작성 의무 정책 + `docs/stories/` 디렉토리 + 수동 Story 작성
- **2단계 완료** (CFP-2): `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` + `.github/workflows/`에 6종 워크플로우(story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync) + `.github/PULL_REQUEST_TEMPLATE.md` + `.github/CODEOWNERS` 도입
- **3단계 향후** (CFP-5 잠정): `templates/**` ↔ `.github/**` parity + frontmatter ↔ CLAUDE.md 표 ↔ `.claude-plugin/plugin.json` 정합 자동 점검 CI. SSOT drift 자동 차단
- **End-to-end 실증 향후** (CFP-7 잠정): 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → workflow 자동 동작 첫 검증

**Branch protection** (수동 적용, GitHub Settings > Branches): main 브랜치에 `phase-gate-mergeable` required status check 권장. 1인 maintainer 환경에서는 `Require review from Code Owners`는 OFF 권장 (PR self-merge 차단 방지).

판단 시점: Orchestrator가 변경 시작 시 cutoff 분류 선언, commit 직전 재확인.

## docs/stories markdown 규약 요약

- 위치: `docs/stories/<KEY>.md` (single-file SSOT, KEY = `<github.story_key_prefix>-N`)
- Template: [`templates/story-page-structure.md`](templates/story-page-structure.md). story-init.yml Action이 신규 생성
- 각 lane plugin 이 자기 owned section 직접 갱신 (§ "Lane plugin self-write boundary" 표 참조)
- 세부 규약·섹션 책임: 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 SSOT (codeforge-{review,pmo,requirements,test,develop,design})
- §1 변조 금지 invariant: `story-section-1-immutable.yml` Action이 강제
- **Retro page schema** (참고): `docs/retros/<sprint>.md` 페이지는 PMOAgent 직접 write — 형식은 [`templates/retro.md`](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/templates/retro.md) (CFP-27 신설) 따름. `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 검증 (warning 모드)

## Domain Knowledge

- 위치: `docs/domain-knowledge/<area>/<topic>.md` (계층 구조). Consumer overlay가 area 자유 정의
- CODEOWNERS가 `docs/domain-knowledge/**` → `@org/domain-experts` 자동 review
- DomainAgent 입력 4소스: `docs/domain-knowledge/**` + `docs/adr/**` + 도메인 코드 + 사용자 원문 §1
- Q&A는 GitHub Discussions의 "Domain Q&A" 카테고리 (consumer overlay `github.discussions.domain_kb_category` 지정)
- **페이지 schema**: [`templates/domain-knowledge.md`](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/templates/domain-knowledge.md) (CFP-27 신설). frontmatter (title / area / topic_slug / status / sources / related_adrs / related_stories / updated) + 본문 섹션 (`## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력`). `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` 검증 (warning 모드)
