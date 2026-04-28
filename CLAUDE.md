# CLAUDE.md

Claude Code 범용 SW 개발 오케스트레이션 플러그인. 24 core 에이전트 · 7 레인 구조 + `role: dev` 동적 roster로 요구사항 접수부터 보안 테스트 통과까지 자율 실행. 에이전트 상세는 각 [`agents/<Name>.md`](agents/) (SSOT). 공통 문서 양식은 [`templates/`](templates/) SSOT 참조. 리뷰 PL 공통 base + 체크리스트는 [`templates/review-pl-base.md`](templates/review-pl-base.md) · [`templates/review-checklists/`](templates/review-checklists/) SSOT ([ADR-001](docs/adr/ADR-001-review-agent-unification.md)). 프로젝트 shape별 Dev 구성 preset은 [`presets/`](presets/) 참조.

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

## 세션 개시 의무 (필수 의존성 자동 확인 + 복구 or 요구)

**세션 시작 직후, 모든 작업보다 먼저** 아래 의존성의 노출·설치·인증 상태를 확인한다. 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 설치·재인증을 요구한다. 복구 완료 전까지 **모든 작업 중단** (요구사항 해석·에이전트 스폰·파일 수정·커밋 전부 금지).

### 필수 의존성 SSOT

**MCP 서버 (1종)**:
- `github` — Issue/PR/sub-issue/comment·repo file write 전반. DocsAgent 단독 writer가 사용

**필수 플러그인 (4종)**:
- `codex@openai-codex` — **CodexReviewAgent** (3 리뷰 lane 공통) 전용. RequirementsAnalyst는 별도 `codex` CLI만 의존하며 본 플러그인이 없어도 CLI만 설치돼 있으면 동작 (아래 필수 CLI 항목 참조)
- `superpowers@claude-plugins-official` — agent md 다수 스킬 의존 (brainstorming, writing-plans, systematic-debugging, test-driven-development, verification-before-completion, dispatching-parallel-agents)
- `claude-md-management@claude-plugins-official` — DocsAgent의 claude-md-improver / revise-claude-md 스킬 의존
- `github@claude-plugins-official` — GitHub MCP 도구 (issue_write, sub_issue_write, create_or_update_file, create_pull_request 등) 노출

**필수 CLI (2종)**:
- `codex` — RequirementsAnalyst가 `codex exec -m gpt-5.4` 호출
- `gh` — DocsAgent가 Milestone·Discussions·기타 GraphQL fallback 호출 (`gh api repos/*/milestones*`, `gh api graphql*` 등)

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

## Development Agent Team (24 core 에이전트 + `role: dev` 동적 roster · 7 레인 + 2 Cross-cutting)

※ 본 구조는 v0.12.0(CFP-18 머지) 직후부터 발효. 머지 시점 이전에 진행 중이던 Story는 [`docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md`](docs/superpowers/specs/2026-04-27-cfp-17-architectpl-securityarch-design.md) §8.1 paradox 처리에 따라 옛 구조로 완료.

```
(Human) 사용자                       # 외부 행위자 — 요구사항 제공·blocking 질문 응답·ESCALATE 수신
   ↓ 요구사항 전달
Orchestrator                        # 최상위 Claude 세션 — 모든 스폰·토큰 예산 소유
 │
 ├── [Cross-cutting] PMOAgent        # 프로젝트 관리 — Epic 분해 자문·Story 회고·Cross-Story 패턴·ADR 후보 발의
 ├── [Cross-cutting] DocsAgent       # 문서화 writer (Story file + GitHub lifecycle) + 표준 SSOT (write queue drain)
 │
 ├── [요구사항] RequirementsPLAgent
 │    ├── DomainAgent                  # 프로젝트 도메인 전문가 (docs/domain-knowledge + ADR + 도메인 코드 + 사용자 원문 4소스)
 │    ├── RequirementsAnalystAgent     # GPT-5.4 래퍼 (codex exec)
 │    └── ResearcherAgent              # 외부 지식 리서치 (웹·논문·공급사 문서)   ※ 셋 모두 병렬 스폰, 독립 관점 유지
 │
 ├── [설계] ArchitectPLAgent
 │    ├── ArchitectAgent (chief author)         # Change Plan §1-§11 + ADR draft + §8 Test Contract + §11 데이터 마이그레이션 author
 │    ├── CodebaseMapperAgent                   # 보수 — as-is 변호자
 │    ├── RefactorAgent                         # 혁신 — 결합도/구조 옹호자
 │    ├── SecurityArchitectAgent                # 위협 — trust boundary/auth/data 변호자
 │    ├── TestContractArchitectAgent            # QA perspective contributor — §8 Test Contract author input
 │    └── DataMigrationArchitectAgent           # 데이터 무결성 — schema 진화·rollback·integrity invariant 변호자 (§11 author input)
 │    ※ QADev는 조직상 여기 계약(§8 소유자) but 실행은 구현 레인에서 DevPL 산하
 │
 ├── [설계 리뷰] DesignReviewPLAgent              # lane=design packet 주입
 │    ├── ClaudeReviewAgent            # 공통 워커 (lane-agnostic, Claude 네이티브)
 │    └── CodexReviewAgent             # 공통 워커 (lane-agnostic, Codex GPT-5 wrapper)
 │
 ├── [구현] DeveloperPLAgent
 │    ├── <role: dev 에이전트 N개>     # 프로젝트 roster — core 3종(DeveloperAgent·DataEngineerAgent·InfraEngineerAgent) + overlay/preset 추가분
 │    └── QADeveloperAgent            # 테스트 코드 (Change Plan §8 Test Contract 이행)
 │
 ├── [구현 리뷰] CodeReviewPLAgent                # lane=code packet 주입
 │    ├── ClaudeReviewAgent            # ↑ 공통 워커 재사용
 │    └── CodexReviewAgent             # ↑ 공통 워커 재사용
 │
 ├── [구현 테스트] TestAgent          # Orchestrator 직속 구현 테스트 게이트 (기능 + 성능, 언어·프레임워크 중립)
 │
 └── [보안 테스트] SecurityTestPLAgent             # lane=security packet 주입 + 1차 layer fetch 의무
      ├── ClaudeReviewAgent            # ↑ 공통 워커 재사용 (high-level: trust boundary·auth model)
      └── CodexReviewAgent             # ↑ 공통 워커 재사용
      ※ 1차 layer는 GitHub native — Dependabot/CodeQL/Secret Scanning/Push Protection
```

리뷰 워커 통합 ([ADR-001](docs/adr/ADR-001-review-agent-unification.md)): 3 lane × 2 vendor = 6 워커였던 구조를 **2 워커(ClaudeReviewAgent · CodexReviewAgent)** 로 통합. 도메인(체크리스트·스코프·category enum·severity 자동 룰)은 호출 PL이 review packet으로 주입. 공통 로직(severity 종합·dedup·보고 형식)은 [`templates/review-pl-base.md`](templates/review-pl-base.md) SSOT.

**주체 명칭**:
- **Orchestrator** = 최상위 Claude 세션 (모든 Agent 툴 스폰, 토큰 예산 소유)
- **(Human) 사용자** = 인간 행위자
- **Cross-cutting** = 특정 레인에 속하지 않고 모든 레인에 걸쳐 작동하는 에이전트 (PMOAgent 프로젝트 관리 / DocsAgent 문서 writer)

## 레인 7개 · 단계 정의

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트
```

모든 Story는 **full 7 레인** 통과. Fast-path 없음 (단 **Hotfix 경로** 2종은 예외 — 운영 장애 대응, 사후 감사 의무. 상세는 [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) §10 참조).

**1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항 + 설계 + 설계리뷰 lane): `docs/stories/<KEY>.md` §1-7 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md`
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane): `src/**` + `tests/**` + `docs/stories/<KEY>.md` §8-11 append

**레인 진입 전 Preflight 체크 의무** — 각 레인 진입 직전 Orchestrator가 3개 체크 수행 (phase 라벨 정합 / docs file 선행 섹션 / 외부 의존성 가용). FAIL 시 block+report. 상세는 playbook §3B.

- **요구사항**: 사용자가 GitHub Issue Forms (story.yml) 제출 → `story-init.yml` Action이 자동 `<KEY>` 번호 계산 + `docs/stories/<KEY>.md` 생성 (§1 verbatim, §2-11 placeholder) + Phase 1 PR 자동 open + Issue body link 변환 → RequirementsPLAgent 아래 **병렬** (DomainAgent · Analyst · Researcher 동시 스폰, 각자 독립 관점) → RequirementsPL이 세 결과 dedup·상충 조정 → DocsAgent 경유 §2·§5·§6 동시 채움 + §3-4 갱신
- **설계**: ArchitectPLAgent가 CodebaseMapper(변호자) · Refactor(혁신자) · SecurityArchitectAgent(위협 변호자) · TestContractArchitectAgent(QA perspective contributor) · DataMigrationArchitectAgent(데이터 무결성 변호자) **5 deputy 병렬 스폰** → ArchitectAgent(chief author)가 통합 → Change Plan 확정 (§7 보안 설계 + §8 Test Contract + §11 데이터 마이그레이션 포함) → DocsAgent가 `docs/change-plans/<slug>.md` 저장 + Story file §7 미러링
- **설계 리뷰**: DesignReviewPL이 Claude/Codex 설계 리뷰 종합 → PASS 시 `gate:design-review-pass` 라벨 부착 → Phase 1 PR mergeable → merge → 구현 진입 / FIX 시 ArchitectPLAgent 회귀 → ArchitectAgent (chief author) 재스폰 (최대 3회)
- **구현**: Phase 2 PR open (DeveloperPL이 첫 commit 준비 후 DocsAgent 경유 `mcp__github__create_pull_request`). Orchestrator가 QADev + DeveloperPL 병렬 스폰. DevPL이 프로젝트 `role: dev` roster를 동적 discover해 의존성 없는 한 **모두 병렬** 스폰. ArchitectPLAgent가 stateless 재스폰되어 매핑표 감사
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

**Project Config Packet** (DocsAgent·RequirementsPL·DomainAgent·PMO·ArchitectPLAgent): `.claude/_overlay/project.yaml` slice도 packet으로 주입 → GitHub 호출 에이전트의 반복 `Read` 회피. 상세는 playbook §12.5.

**Story file 위치**: `docs/stories/<KEY>.md` (KEY = `<github.story_key_prefix>-N`, 예: `PLG-7`). story-init.yml Action이 자동 생성 (요구사항 lane 진입 시).

**생성·갱신 전담**: **DocsAgent**.

**섹션 갱신 의뢰 경로**: 각 에이전트는 Orchestrator 경유 DocsAgent에 "Story file <key> 섹션 {X}에 다음 내용 추가" 의뢰. Story file 섹션 갱신 등 multi-writer 영역 file 변경은 **DocsAgent 단독**. 단 single-owner docs (`docs/{change-plans,adr,domain-knowledge,retros}/**`)는 owner agent direct write — 상세는 §"문서 write 책임 분담"

섹션 규격·단계별 책임 상세는 [`agents/DocsAgent.md`](agents/DocsAgent.md) 참조.

### Never-skippable 에이전트

- **요구사항**: **RequirementsPLAgent**, **DomainAgent**, **RequirementsAnalystAgent**, **ResearcherAgent** (세 서브 에이전트는 PL 산하 병렬 관점 제공자로 전원 필수)
- **설계**: **ArchitectPLAgent**, **ArchitectAgent**, **CodebaseMapperAgent**, **RefactorAgent**, **SecurityArchitectAgent**, **TestContractArchitectAgent**, **DataMigrationArchitectAgent**
- **설계 리뷰**: **DesignReviewPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent** (워커는 lane=design packet 수령)
- **구현**: **DeveloperPLAgent**, **QADeveloperAgent**
- **구현 리뷰**: **CodeReviewPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent** (워커는 lane=code packet 수령)
- **구현 테스트**: **TestAgent**
- **보안 테스트**: **SecurityTestPLAgent**, **ClaudeReviewAgent**, **CodexReviewAgent** (워커는 lane=security packet 수령)
- **Cross-cutting**: **DocsAgent** (모든 레인에서 write 창구로 필수)

조건부 생략: `role: dev` 에이전트만 해당 (Change Plan이 해당 에이전트 소유 경로 미변경 시). 요구사항·설계 레인의 서브 에이전트는 전원 non-skippable — "조사할 것 없음" 판단도 독립 관점의 하나이므로 각자 스폰되어 명시적으로 결과를 반환해야 한다 ("null 결과"도 유효한 관점).

**PMOAgent**는 Never-skippable이 아니며 Cross-cutting 트리거 기반 스폰: Epic 창설 1회 / Story 완료 회고 1회 / 사용자 요청 시. 단일 Story 레인 게이트에 개입 없음.

### 스폰 시퀀스

```
[요구사항] Orchestrator → RequirementsPLAgent → **병렬** (DomainAgent · RequirementsAnalyst · Researcher 동시 스폰) → RequirementsPLAgent 통합
        · 셋 모두 공통 입력(사용자 원문 Story §1 + ADR 목록 §3 선제 fetch + 코드 경로 §4 + Project Config Packet)에서 각자 키워드·관점 자체 도출 (§2·§5·§6은 각자의 출력 destination이므로 input 아님)
          - DomainAgent: 도메인 지식 공백 (용어·개념·비즈니스 규칙·ADR)
          - Analyst: 요구사항 ambiguity (암묵 가정·누락·충돌·AC)
          - Researcher: 외부 기술·선행사례 (라이브러리·표준·유사 구현)
        · 세 결과 독립적으로 반환 → RequirementsPL이 dedup·상충 조정해 통합 명세서 확정
        · "null 결과" (조사 불필요 판단)도 유효한 관점 — 에이전트 skip 금지
        · DomainAgent 지식 공백 해소 시 본 에이전트가 docs/domain-knowledge/<area>/<topic>.md 직접 write (CFP-26 Phase 0a)
        · 상충 시 Orchestrator 경유 사용자 에스컬레이션
        · "사용자 확인 필요" 항목은 blocking wait
        · 통합 명세서는 Story file §3-6에 DocsAgent 경유 반영
        · **Clarification 재스폰**: PL이 세 결과 통합 중 특정 관점의 추가 조사·재해석이 필요하면 Orchestrator에 "<에이전트> 재스폰 요청 + clarification context" 전달 → Orchestrator가 해당 에이전트 신규 스폰 (이전 출력 + 재질의 context 포함). 서브에이전트는 one-shot이므로 재스폰이 유일한 "clarification" 메커니즘

[설계] Orchestrator → ArchitectPLAgent → **병렬 스폰** (deputy 5인)
        ├── CodebaseMapperAgent (as-is 변호자 — 원 소스 직접 읽기)
        ├── RefactorAgent (to-be 혁신자 — 원 소스 직접 읽기)
        ├── SecurityArchitectAgent (위협/공격자 — 원 소스 직접 읽기, OWASP·CWE 참조)
        ├── TestContractArchitectAgent (QA perspective contributor — §8 커버리지 후보·경계·invariant)
        └── DataMigrationArchitectAgent (데이터 무결성 advocate — §11 schema 영향·migration 전략·rollback·integrity invariant)
        · 다섯 다 PL이 공통 입력(코드 경로 + 관련 ADR + Change Plan 초안 + Story §1-7) 직접 제공
        · 다섯 결과 PL에 독립적으로 반환 → PL이 forward
        ↓
        Orchestrator → ArchitectAgent (chief author) 스폰
        with input: 5 deputy 산출물 + Story §1-7 + 관련 ADR
        → Change Plan §1-§11 author + 신규 ADR draft + §8 Test Contract + §11 데이터 마이그레이션
        → DocsAgent 저장 의뢰
        ↓
        ArchitectPLAgent draft 검수 (메타-규칙 2 항목: §섹션별 deputy author input 통합 정합성 + §섹션 누락 차단)
        · PASS → Orchestrator에 DesignReview lane 진입 요청
        · RETURN → ArchitectAgent 재스폰 의뢰 (clarification context)
        · **Clarification 재스폰**: PL이 deputy 산출물 검수 중 추가 분석 필요 시 Orchestrator에 "<Mapper|Refactor|SecurityArch|TestContractArch|DataMigrationArch> 재스폰 요청 + clarification context" 전달

[설계 리뷰] Orchestrator → DesignReviewPLAgent (lane=design packet 작성) → packet return
        Orchestrator가 한 메시지에 dispatch:
        ├── ClaudeReviewAgent (lane=design packet 수령)
        └── CodexReviewAgent  (lane=design packet 수령, 병렬)
        → DesignReviewPL 결과 종합 → PASS or FIX (최대 3회) (R3·R2)
        · PASS (R7 2 트랙 병렬):
          - Track A: DocsAgent가 `gate:design-review-pass` 라벨 부착 → Phase 1 PR mergeable·merge
          - Track B: DeveloperPL spawn → Change Plan §5·§8 fetch + 첫 commit draft 준비 (PR open 보류)
          - Track A merge 완료 시 Track B가 즉시 `mcp__github__create_pull_request` 호출
          - 동시에 Orchestrator가 background DocsAgent (type=security-prefetch, R10) → `.claude-work/cache/<KEY>-sec1.json` 생성
        · FIX: Orchestrator 경유 ArchitectPLAgent 회귀 → ArchitectAgent 재스폰 → Change Plan 갱신 → 설계 리뷰 재실행

[구현] Phase 2 PR open (DeveloperPL → DocsAgent → mcp__github__create_pull_request)
        Orchestrator가 병렬 스폰
        ├── DeveloperPLAgent
        │    └── <role: dev 에이전트 N개>   # 프로젝트 roster — Change Plan 경로 교집합 있는 것만 실제 스폰
        └── QADeveloperAgent (조직상 ArchitectPLAgent 산하 §8 Test Contract 이행자, 실행상 구현 레인 병렬)
        → roster 전체는 의존성 없는 한 병렬
        → DeveloperPL 완료 보고 → §8.5 Impl Manifest 매핑표 commit → subissue-from-impl-manifest.yml Action이 자동 sub-issue 생성
        → Orchestrator가 ArchitectPLAgent를 stateless 재스폰해 매핑표 감사
        → 감사 PASS 시 Orchestrator가 구현 리뷰 레인 진입

[구현 리뷰] Orchestrator → CodeReviewPLAgent (lane=code packet 작성) → packet return
        Orchestrator가 한 메시지에 dispatch:
        ├── ClaudeReviewAgent (lane=code packet 수령)
        └── CodexReviewAgent  (lane=code packet 수령, 병렬)
        → CodeReviewPL 결과 종합 → PASS or FIX (최대 3회) (R3·R2)
        · FIX 시 mechanical_category 자격 확인 → fast-path 또는 정상 cycle (R11)
        · 정상 cycle FIX: Orchestrator 경유 DeveloperPL ∥ ArchitectPLAgent 병렬 진단/판정 (R4)
          · 설계 원인 판정 시: Change Plan 갱신 → Phase 1 follow-up PR로 회귀 → 설계 리뷰부터 재실행
          · 구현 원인 판정 시: Phase 2 PR commit append → 구현 리뷰 재실행

[구현 테스트] Orchestrator → TestAgent **subset 병렬** (R9):
        · TestAgent(subset: functional) ∥ TestAgent(subset: performance) — 한 메시지에 dispatch
        · 모드 1 (기능): 단위/통합/인프라 테스트 (consumer overlay가 러너·경로 지정)
        · 모드 2 (성능): baseline 대비 mean 10% 이상 악화 시 FAIL (consumer overlay가 baseline 위치 지정)
        · 둘 다 PASS → 보안 테스트 레인 진입
        · consumer overlay `tests.performance.depends_on_functional: true` 시 sequential fallback
        · FAIL → Orchestrator 경유 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (구현 원인 / 설계 원인)
          · 설계 원인: Change Plan 갱신 → 설계 리뷰부터 재실행
          · 구현 원인: 구현만 재실행 → 구현 리뷰 재실행
          · 재진입한 구현 리뷰에서 P0/P1 발견 시 구현 리뷰 카운터 리셋 (구현 테스트 FIX는 무제한)

[보안 테스트] Orchestrator → SecurityTestPLAgent (lane=security packet 작성, 1차 layer cache hit/miss 확인)
        1차 layer: `.claude-work/cache/<KEY>-sec1.json` hit 시 inline 첨부 (R10) / miss 시 PL이 `gh api repos/*` 직접 fetch
        cache는 Phase 2 PR open 직후 Orchestrator가 background DocsAgent (type=security-prefetch)로 사전 생성
        2차 layer (Orchestrator가 한 메시지에 dispatch, R3):
        ├── ClaudeReviewAgent (lane=security packet 수령, high-level: trust boundary, auth model)
        └── CodexReviewAgent  (lane=security packet 수령, 병렬)
        → SecurityTestPL severity 종합 (OWASP·CWE·CVE·trust boundary·credential 범위)
        · PASS → DocsAgent가 `gate:security-test-pass` 라벨 부착 → Phase 2 PR mergeable → merge (PR body의 `Closes #N`이 Issue 자동 close) → PMOAgent (회고)
        · FAIL → Orchestrator 경유 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정
          · 설계 원인 (trust boundary / auth 모델 오설계): Change Plan 갱신 → 설계 리뷰부터 재실행
          · 구현 원인 (injection / credential hardcode / CVE 업그레이드): 구현만 재실행 → 구현 리뷰·구현 테스트 재실행
          · 보안 테스트 FIX 카운터 무제한 (테스트 레인 family 정책)
```

### FIX 루프

**판정 SSOT**: [`templates/review-pl-base.md`](templates/review-pl-base.md) §3 — severity 종합·dedup·종합 판정(P0/P1=2 → FIX, P1=1 → FIX 재량, P2만 → PASS). 본 섹션은 **트리거·카운터·원인 판정**만 본문에 명시.

**트리거** (review-pl-base.md §3 결과 FIX 또는 FIX 재량):
- 설계 리뷰 → ArchitectPLAgent 회귀 → ArchitectAgent 재스폰
- 구현 리뷰 → DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정
- 구현 테스트 FAIL → DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정
- 보안 테스트 → DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정

**카운터 SSOT = `docs/stories/<KEY>.md` §10 "FIX Ledger"** (GitHub Issue 라벨은 대시보드용 보조 지표):
- §10은 테이블 형식으로 모든 FIX iteration 누적 (레인별 컬럼 + RESET 마커 지원)
- Orchestrator가 FIX 판정 시마다 `Read(docs/stories/<KEY>.md)` → §10 파싱 → "현재 사이클" count 산출
- §10에 새 행이 commit되면 `fix-ledger-sync.yml` Action이 자동:
  1. Issue comment에 `[FIX #N]` mirror
  2. `fix:<레인>-retry` 라벨 자동 부착

**§10 FIX Ledger 스키마** (DocsAgent가 관리, 상세는 [DocsAgent.md](agents/DocsAgent.md) §9 참조):
```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | ISO8601 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
| 3    | ISO8601 | 보안-테스트 | SecurityTestPL P0 × 1 (SQL injection) | 구현 | DeveloperAgent 재스폰 | — |
```

**최대 FIX 횟수** (§10 current-cycle count 기준):
- **설계 리뷰 FIX 최대 3회** → 초과 시 Orchestrator 경유 사용자 ESCALATE
- **구현 리뷰 FIX 최대 3회**
- **구현 테스트 FIX 무제한**
- **보안 테스트 FIX 무제한**

**카운터 리셋**: 구현 테스트 또는 보안 테스트 FAIL → 구현 재실행 → 구현 리뷰 재진입 시 §10에 `RESET 구현-리뷰` 마커 행 추가. 이후 구현 리뷰 카운터는 RESET 이후 iteration만 합산.

**수평 호출 금지** — ReviewPL/TestAgent/ArchitectPLAgent/DeveloperPL 간 직접 호출 금지, 모든 게이트 재실행·회귀 요청은 Orchestrator 경유.

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

3 review/test PL(DesignReviewPL · CodeReviewPL · SecurityTestPL) 공통. SSOT는 [`templates/review-pl-base.md`](templates/review-pl-base.md) §3 (dedup · 종합 판정 표 · noise 분류). 본 CLAUDE.md에서는 SSOT 참조만 두고 표를 재인용하지 않는다.

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
- **Epic 창설 시** (1회): Scope 분해 자문 — Story 분해·의존성 식별·**병렬/순차 판정** (파일 경로 disjoint / 인터페이스↔구체 분리 / 공유 자원 충돌 기준, 상세 [PMOAgent.md §1](agents/PMOAgent.md))
- **Story 완료 시**: 회고 감사 (Preflight/Gate 준수·§8/§8.5 매핑·FIX evidence pack 완성도·토큰 예산)
- **사용자 요청 시** (주기적): Cross-Story 패턴 보고서 (FIX 반복 유형·ESCALATE 트렌드·성능 회귀·코드 핫스팟)

**산출물**:
- `[PMOAgent 회고]` / `[PMOAgent Cross-Story 감사]` 보고서 (DocsAgent 경유 Story file §11 또는 별도 회고 페이지에 기록)
- **ADR 후보 발의** (반복 패턴이 "설계 지침 부재"로 해석 시 `status=Proposed` ADR draft를 write queue에 제출)
- 세션 회고 synthesize (playbook §8.3 테이블 채움)

상세는 [`agents/PMOAgent.md`](agents/PMOAgent.md).

### CodebaseMapper ↔ Refactor ↔ SecurityArchitect ↔ DataMigrationArchitect 4-way 이념 대립

- **CodebaseMapperAgent** = **기존 코드 변호자** (보수). "기존 패턴 유지, 변경 영향 최소화"가 기본 입장
- **RefactorAgent** = **리팩터링 옹호자** (혁신). "결합도 감소, 인터페이스 분리, 패턴화"가 기본 입장
- **SecurityArchitectAgent** = **위협 변호자** (공격자 관점). "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가"가 기본 입장
- **DataMigrationArchitectAgent** = **데이터 무결성 변호자** (CFP-21). "schema가 어떻게 변하는가, 기존 데이터는 어떻게 처리되는가, 실패 시 어떻게 복구하는가"가 기본 입장
- ArchitectPLAgent가 Mapper·Refactor·SecurityArch·DataMigrationArch **병렬 스폰** — 넷 다 원 소스(코드 + ADR + Change Plan 초안 + Story §1-7)를 직접 읽고 각자 관점에서 분석 (서로 산출물에 오염되지 않도록 독립 유지)
- 네 관점 충돌 시 ArchitectAgent (chief author)가 결정 근거와 함께 Change Plan §2(현재 구조)·§3(도입할 설계)·§7(보안 설계)·§11(데이터 마이그레이션)에 명시. 수용·반박은 chief author가 조정 후 기록 (deputy 간 상호 대응 방식 아님). ArchitectPLAgent는 통합 결과를 검수
- DesignReviewPL이 "**ArchitectAgent (chief author) 통합 판정 + ArchitectPLAgent 검수**가 Mapper 변호 근거를 근거 있게 일축·수용했는가 / Refactor 제안이 요건 범위를 넘지 않았는가 / SecurityArch 위협·완화 매핑이 §7에 충실히 반영되었는가 / DataMigrationArch 마이그레이션 안전성 매핑이 §11에 충실히 반영되었는가" 교차 체크 (병렬 모델에서는 deputy 간 상호 대응하지 않으므로, 대립 해소 품질 평가는 chief author + PL 통합 결과 대상)

TestContractArchitectAgent는 §8 author input contributor (도형 대립 비참여 — Mapper/Refactor/SecurityArch/DataMigrationArch 4-way와 별개 영역). ArchitectPLAgent 메타-규칙 1번이 §8 TestContractArch input + §11 DataMigrationArch input 통합 정합성을 감사.

### 설계 lane deputy Freshness

모든 deputy (CodebaseMapperAgent · RefactorAgent · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent) 공통:
- **매 설계 레인 진입 시 재스폰** (이전 Story 산출물 재사용 금지)
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 전제)

### ArchitectPLAgent 라이프사이클 (stateless 재스폰)

- 매 트리거마다 Orchestrator가 신규 스폰 — 세션 유지 없음
- Story file §1-8 재로딩으로 컨텍스트 복원
- 토큰 비용: 재스폰 당 ~5-10k tokens. FIX 3회 가정 시 15-30k overhead (playbook §8 참조)
- **ArchitectAgent (chief author)** 도 각 설계 레인 진입마다 stateless 재스폰 — 5 deputy 산출물을 입력으로 수령 후 Change Plan §1-§11 author 수행. ArchitectPLAgent RETURN 시에도 재스폰

### Write 권한 (path-scoped — 각 agent md frontmatter가 SSOT)

**Core 기본 경로** (consumer overlay가 확장):
- **Write 권한 있음**:
  - `role: dev` 에이전트별 개별 scoping (core: DeveloperAgent `src/**` 기본 + `tests/**`·`docs/**` deny, DataEng 프로젝트별 데이터 계층 경로, InfraEngineer `deploy/**`·`config/**`·`scripts/**`; preset·overlay가 경로 재정의 — preset 예: `presets/webapp/agents/{Backend,Frontend}DeveloperAgent`)
  - QADev `role: qa` (`tests/**` allow + `src/**` deny — production 코드 직접 수정 금지)
  - **DocsAgent**: `docs/**` (단, `docs/{change-plans,adr,domain-knowledge,retros}/**` 4종은 deny — CFP-26 Phase 0a부터 owner agent로 이관) + `.claude-work/doc-queue/**` + GitHub MCP write 도구 전용 + `src`·`tests`·`.claude`·`config`·`deploy`·`scripts` 명시 deny
  - **ArchitectAgent**: `docs/change-plans/**` + `docs/adr/**` (CFP-26 Phase 0a — chief author direct write)
  - **DomainAgent**: `docs/domain-knowledge/**` (CFP-26 Phase 0a — 도메인 KB direct write)
  - **PMOAgent**: `docs/retros/**` (CFP-26 Phase 0a — retro direct write)
- **Write queue 의뢰 권한만** (`.claude-work/doc-queue/**`): RequirementsPLAgent, ArchitectPLAgent, SecurityArchitectAgent, TestContractArchitectAgent, DataMigrationArchitectAgent, CodebaseMapper, Refactor, DesignReviewPL, CodeReviewPL, SecurityTestPL, ClaudeReviewAgent, CodexReviewAgent, DeveloperPLAgent, RequirementsAnalyst, Researcher, TestAgent — Story file·GitHub comment 등 multi-writer / lifecycle 책임은 여전히 DocsAgent 경유
- **외부 도구 wrapper**: RequirementsAnalyst(`Bash(codex exec *)`), CodexReviewAgent(`Bash(node *)` codex-companion 실행 + `WebSearch`·`WebFetch` CVE/OWASP 조회), ClaudeReviewAgent(`WebSearch`·`WebFetch` 보안 lane CVE 조회), SecurityTestPL(`Bash(gh api repos/*)` 1차 layer alerts fetch), DocsAgent(`Bash(gh api repos/*/milestones*)`, `Bash(gh api repos/*/discussions*)`, `Bash(gh api graphql*)`, `Bash(mkdir/ls/rm .claude-work/doc-queue*)`)

### 문서 write 책임 분담 (CFP-26 Phase 0a 후)

**DocsAgent + 3 owner agent 분담 모델**. `docs/**` 영역은 둘로 나뉜다:

1. **Single-owner 직접 write** (CFP-26 Phase 0a부터):
   - **ArchitectAgent**: `docs/change-plans/**` + `docs/adr/**` (chief author 산출물)
   - **DomainAgent**: `docs/domain-knowledge/**` (도메인 KB)
   - **PMOAgent**: `docs/retros/**` (회고)
   - 이 4 path (`docs/{change-plans,adr,domain-knowledge,retros}/**`)는 DocsAgent deny — owner agent가 직접 write
2. **DocsAgent 단독 owner** (multi-writer 직렬화 + GitHub lifecycle):
   - `docs/stories/<KEY>.md` (multi-writer 직렬화 — RequirementsPL §2-6, ArchitectAgent §7 미러링, DeveloperPL §8/§8.5, ReviewPLs §9, TestAgent §10 결과, FIX Ledger §10 schema, PMO §11 회고 pointer)
   - `docs/**` 그 외 일반 문서 (orchestrator-playbook, plugin-design, migration-guide, consumer-guide 등)
   - GitHub Issue/PR/comment (phase prefix 11종) · PR/Issue body create/update (`Closes #N` keyword) · label 부착(gate/phase/fix) · sub-issue 수동 fallback · milestone · gh api fallback
3. **나머지 에이전트** (Write queue 의뢰만): Story file 섹션 갱신·GitHub comment 게시 등 multi-writer/lifecycle 영역은 `.claude-work/doc-queue/<story>/`에 의뢰 → Orchestrator가 DocsAgent 스폰 시 drain. 상세는 playbook §11

문서화 표준(GitHub Issue 코멘트 phase prefix, Story file 섹션 규격, Change Plan 템플릿, ADR 템플릿, FIX Ledger 스키마, Impl Manifest 스키마)은 [`agents/DocsAgent.md`](agents/DocsAgent.md) SSOT. 4 single-owner doc 템플릿은 [`templates/`](templates/) — change-plan / adr는 현재 존재, domain-knowledge schema / retro schema는 CFP-27에서 신설 예정. owner agent는 본인 owner path write 시 해당 템플릿 schema 준수 필수 — `scripts/check-write-permission-redistribution.sh` (CFP-26) + 향후 frontmatter/section schema lint (CFP-27)에서 강제.

### Codex CLI / 플러그인 필수
- CodexReviewAgent: Codex 플러그인 (3 리뷰 lane 공통 — 미설치 시 설계 리뷰·구현 리뷰·보안 테스트 모두 진행 불가)
- RequirementsAnalyst: `codex` CLI
- 미설치 시 해당 레인 진행 불가, Orchestrator가 설치 안내 후 중단

### 병렬 스폰 권장
- **요구사항**: **DomainAgent · RequirementsAnalyst · Researcher 병렬** — 셋 모두 공통 입력에서 각자 키워드·관점 자체 도출. PL이 synthesizer
- **설계**: **5 deputy 병렬** (CodebaseMapper · Refactor · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent) — 5 deputy 모두 원 소스 직접 읽기, 한쪽이 다른 쪽의 요약에 의존하지 않음. ArchitectAgent (chief author)가 통합, ArchitectPLAgent가 검수
- **구현**: QADev + DevPL의 `role: dev` roster (의존성 없는 한 모두 병렬)
- **리뷰·보안**: Claude + Codex 병렬 (Design Review / Code Review / Security Test 각 레인)

**Clarification 재스폰 공통 절차** (요구사항·설계 레인): 서브에이전트는 one-shot이라 PL↔서브 continuous dialog 불가. PL이 통합 중 추가 질의가 필요하면 → Orchestrator에 "<에이전트> 재스폰 요청 + clarification context + 이전 출력 pointer" 전달 → Orchestrator가 해당 에이전트를 신규 스폰. 이것이 "각 책임 종료 전까지 보조" 메커니즘의 실제 구현.

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
[`templates/adr.md`](templates/adr.md) 참조. frontmatter (adr_number / title / status / category / date / related_files) + 본문 섹션 (`## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램 / ## 관련 파일`).

## 버그 기록 (GitHub Issues)
- Issue Forms: `.github/ISSUE_TEMPLATE/bug.yml`. Severity dropdown (P0/P1/P2)
- 신규 버그: DocsAgent가 `mcp__github__issue_write(action='create', title=..., body=..., labels=['type:bug', 'component:<name>'])`
- 해결 시: PR body에 `Closes #<bug-issue>` keyword → merge 시 자동 close (GitHub native)

## GitHub Workflow

사용자 요구사항 접수부터 PR merge까지의 모든 의사결정·협업을 GitHub에 영속 기록. 쓰기는 DocsAgent 단독.

### 계층
- **Epic** = 사용자 요구사항 1건. **Milestone (due date·% 진행률 자동) + Issue (`type:epic` 라벨, body=narrative)**. Orchestrator가 PMOAgent 스폰 직전 DocsAgent 경유 생성
- **Story** = PR 1쌍 (Phase 1 + Phase 2 = Change Plan 1건). **Issue (`type:story` 라벨)**. Milestone에 속함. Orchestrator(필요 시 PMO 조언) scope 분해 시 확정된 독립 작업 단위만 생성
- **하위 작업(sub-issue)** = Impl Manifest 파일 단위. **Sub-issue (`impl-manifest` 라벨)**. Phase 2 PR이 §8.5 매핑표 commit 시 `subissue-from-impl-manifest.yml` Action이 자동 생성. PR merge 시 parent close에 따라 자동 close
- **Audit Story** = hotfix 사후 감사 1건. `audit:post-hotfix` 라벨. hotfix merge 다음 세션 개시 시 Orchestrator가 Issue Forms (audit.yml)로 자동 생성

### 상태 + Phase Label 방식

GitHub Issue 기본 2-state (`open`/`closed`). 단계는 **phase label**로 표현. PR merge 시 GitHub native `Closes #N` keyword가 Issue 자동 close.

```
[Issue Form 제출] story-init.yml Action 자동 실행
   ↓ docs file 생성 + Phase 1 PR 자동 open + 라벨 phase:요구사항 부착
[phase:요구사항 → phase:설계]   (DocsAgent가 phase 라벨 부착, phase-label-invariant.yml가 기존 detach)
   ↓ ArchitectAgent (chief author) Change Plan 확정
[phase:설계 → phase:설계-리뷰]
   ↓ 설계 리뷰 PASS → DocsAgent가 gate:design-review-pass 라벨 부착
[Phase 1 PR mergeable → merge → Issue label phase:구현]
   ↓ Phase 2 PR open
[phase:구현 → phase:구현-리뷰]
   ↓ 구현 리뷰 PASS
[phase:구현-리뷰 → phase:구현-테스트]
   ↓ 구현 테스트 PASS
[phase:구현-테스트 → phase:보안-테스트]
   ↓ 보안 테스트 PASS → DocsAgent가 gate:security-test-pass 라벨 부착
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

### 코멘트 규칙 (DocsAgent 단독 기록)

형식·phase prefix(10 lane prefix + Orchestrator Preflight 1 = 총 11종)은 [`agents/DocsAgent.md`](agents/DocsAgent.md) SSOT 참조. 다른 에이전트는 Orchestrator에 기록 요청만 수행, DocsAgent가 실행 (`mcp__github__add_issue_comment`).

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
- DocsAgent가 생성·섹션 갱신 전담
- 세부 규약·섹션 책임: [`agents/DocsAgent.md`](agents/DocsAgent.md) SSOT
- §1 변조 금지 invariant: `story-section-1-immutable.yml` Action이 강제

## Domain Knowledge

- 위치: `docs/domain-knowledge/<area>/<topic>.md` (계층 구조). Consumer overlay가 area 자유 정의
- CODEOWNERS가 `docs/domain-knowledge/**` → `@org/domain-experts` 자동 review
- DomainAgent 입력 4소스: `docs/domain-knowledge/**` + `docs/adr/**` + 도메인 코드 + 사용자 원문 §1
- Q&A는 GitHub Discussions의 "Domain Q&A" 카테고리 (consumer overlay `github.discussions.domain_kb_category` 지정)
