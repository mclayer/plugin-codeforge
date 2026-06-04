# codeforge

**Claude Code 범용 SW 개발 오케스트레이션 플러그인**. 사용자 요구사항 한 건을 받아 **0 core 에이전트 (wrapper-only) + 8 lane plugin (codeforge-{requirements,design,review,develop,test,deploy,deploy-review,pmo}) + `role: dev` 동적 roster · 8 레인** 구조로 요구사항 해석 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 통합 테스트 → 보안 테스트 → 배포 → 배포 리뷰까지 자율 실행한다.

## 주요 특징

- **0 core (wrapper-only) + 8 lane plugin + `role: dev` 동적 roster · 8 레인 · 1 Cross-cutting (PMOAgent)** 구조로 SW 개발 프로세스 전반 커버
- **프로젝트 shape별 preset** (`presets/webapp` 등) — 웹앱·CLI·라이브러리·임베디드 등 Dev 구성 번들을 골라 overlay에 임포트
- **CodebaseMapper ↔ Refactor 이념 대립** 으로 설계 균형 확보
- **Claude + Codex(GPT-5) peer 리뷰** 로 설계 리뷰·코드 리뷰·보안 테스트 3중 peer 이중화
- **보안 테스트 전용 레인** (OWASP·CWE·CVE·trust boundary·credential) — Story 완료 전 필수 게이트
- **FIX 루프 상태 머신** — 설계 리뷰·구현 리뷰 최대 3회, 구현 테스트·보안 테스트 FIX 무제한
- **Overlay 메커니즘 (β)** — consumer 프로젝트가 도메인·SSOT 상수·기술 스택을 파일 분리 방식으로 확장
- **Templates SSOT** (`templates/`) — Change Plan · ADR · Story Page · Impl Manifest 양식 일원화
- **Lane plugin self-write boundary** — 각 lane plugin 이 자기 owner section/comment/label 을 직접 write 해 자율적 일관성 유지 (codeforge-* CLAUDE.md self-write 표 SSOT)

## 에이전트 구조

```
(Human) 사용자
   ↓
Orchestrator (최상위 Claude 세션)
 ├── [Cross-cutting] PMOAgent
 ├── [요구사항] RequirementsPL (DomainAgent ‖ Analyst ‖ Researcher 병렬)
 ├── [설계] ArchitectPLAgent (CodebaseMapper ‖ Refactor ‖ SecurityArchitect ‖ TestContractArch 병렬, ArchitectAgent chief author)
 ├── [설계 리뷰] DesignReviewPL (Claude ‖ Codex)
 ├── [구현] DeveloperPL (role:dev roster 병렬) + QADev
 ├── [구현 리뷰] CodeReviewPL (Claude ‖ Codex)
 ├── [구현 테스트] TestAgent
 ├── [보안 테스트] SecurityTestPL (Claude ‖ Codex)
 ├── [배포] DeployPL
 └── [배포 리뷰] DeployReviewPL
```

상세는 [`CLAUDE.md`](CLAUDE.md) 참조.

## 설치 · 사용

### 1. 플러그인 설치

```bash
/plugins marketplace add mclayer/marketplace
/plugins install codeforge@mclayer
```

또는 `~/.claude/settings.json`에 영구 등록:

```jsonc
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": { "codeforge@mclayer": true }
}
```

### 2. 필수 의존성

- MCP: `github` (Issue/PR/sub-issue/comment write)
- 플러그인: `codex@openai-codex`, `superpowers@claude-plugins-official`, `claude-md-management@claude-plugins-official`, `github@claude-plugins-official`
- CLI: `codex`, `gh`

세션 개시 시 자동 점검 · 미설치 시 blocking wait.

### 2a. Enterprise environment prerequisite (CFP-661 / [ADR-027 Amendment 2](archive/adr/ADR-027-consumer-adoption-protocol.md))

codeforge 의 6 핵심 workflow (`story-init.yml` 외 5종) 는 PR / branch create / Issue comment write 권한을 사용. GitHub Enterprise org 의 admin policy 가 `default_workflow_permissions: read` cap 으로 차단 시 workflow silent skip → Story init 실패. **enterprise admin 권한 보유 환경에서 다음 prerequisite 활성 의무**:

#### 권한 있음 — repo Settings 활성

repo Settings → Actions → General → "Workflow permissions" 영역:

1. **"Read and write permissions"** 선택 (default `Read repository contents and packages permissions` 에서 전환)
2. **"Allow GitHub Actions to create and approve pull requests"** 체크박스 활성

CLI 등가 명령:

```bash
gh api --method PUT repos/<owner>/<repo>/actions/permissions/workflow \
  -f default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

#### 권한 없음 — graceful degradation 자동 활성

`default_workflow_permissions: read` 차단 환경에서는 `story-init.yml` 의 `Create Phase 1 PR` step 이 `continue-on-error: true` 로 graceful 실패 → 후속 step 이 Issue comment 로 manual fallback 안내 자동 게시. CFP-658 Wave 1 fallback path 가 대체 진입점으로 활성:

- `.claude/_overlay/project.yaml` 에 `bootstrap.fallback_mode: action_blocked` 설정 (declarative trigger A)
- 또는 Issue 발의자가 `fallback:manual` label 부착 (per-Issue override trigger C)
- RequirementsPL / ArchitectPL 가 `bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출

상세 SSOT: [`docs/consumer-guide.md §1h` Action 차단 환경 fallback](docs/consumer-guide.md) + [ADR-027 §결정 6](archive/adr/ADR-027-consumer-adoption-protocol.md).

### 3. Consumer 프로젝트 overlay 구성

[`docs/consumer-guide.md`](docs/consumer-guide.md) 참조.

핵심 단계:

```bash
# consumer project root에서
mkdir -p .claude/_overlay/agents
```

`.claude/settings.json`에 SessionStart hook 등록:

```json
{
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

`.claude/_overlay/CLAUDE.md`와 `.claude/_overlay/agents/<Name>.md`(필요한 에이전트만)에 프로젝트 특화 내용 작성.

## 문서

| 파일 | 내용 |
|------|------|
| [`CLAUDE.md`](CLAUDE.md) | 오케스트레이션 규칙 SSOT — 에이전트·레인·권한·FIX 루프·GitHub Workflow·ADR 규약 |
| [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) | Orchestrator 행동 SSOT — 생명주기·스폰·상태 머신·토큰 예산·트러블슈팅 |
| [`docs/consumer-guide.md`](docs/consumer-guide.md) | Consumer 프로젝트 설치·overlay 작성 가이드 |
| [`docs/plugin-design.md`](docs/plugin-design.md) | 플러그인 설계 spec — core/overlay 분리 원칙·merge 계약·β 메커니즘 |
| [`docs/project-config-schema.md`](docs/project-config-schema.md) | `project.yaml` Schema SSOT — GitHub·labels 구조화 상수 |
| [`docs/migration-guide.md`](docs/migration-guide.md) | 플러그인 버전업 시 consumer overlay 마이그레이션 절차 |
| [`CHANGELOG.md`](CHANGELOG.md) | 릴리스 이력 (SemVer) |
| [`templates/`](templates/) | 공통 문서 양식 SSOT — Change Plan · ADR · Story Page · Impl Manifest |
| [`presets/`](https://github.com/mclayer/plugin-codeforge-develop/tree/main/presets) | 프로젝트 shape별 Dev 에이전트 번들 — webapp 등 |
| `agents/*.md` | 없음 (wrapper-only — agent md 는 8 lane plugin 에 분산) |

## 구조

```
codeforge/
├── .claude-plugin/
│   └── plugin.json
├── agents/                       # (없음 — wrapper-only, ζ arc 완료 후 0개)
├── presets/                      # 프로젝트 shape별 Dev 번들
│   ├── README.md
│   └── webapp/
│       ├── README.md
│       └── agents/
│           ├── BackendDeveloperAgent.md
│           └── FrontendDeveloperAgent.md
├── templates/                    # 공통 문서 양식 SSOT (wrapper-local)
│   ├── story-page-structure.md   # wrapper-local SSOT
│   ├── epic-results.md           # wrapper-local SSOT
│   ├── impl-manifest.md          # wrapper-local SSOT
│   # change-plan.md / adr.md = codeforge-design plugin SSOT (ADR-079 §결정 8 / CLAUDE.md L290)
├── overlay/                      # consumer 측 overlay tooling
│   ├── hooks/
│   │   ├── regen-agents.sh       # SessionStart hook entry
│   │   └── merge.py              # frontmatter deep merge + body append
│   └── _overlay/
│       └── README.md             # consumer 복사용 skeleton 가이드
├── docs/
│   ├── orchestrator-playbook.md
│   ├── consumer-guide.md
│   ├── plugin-design.md
│   └── README.md
├── CLAUDE.md
└── README.md
```

## 버전

`0.7.0` — 요구사항·설계 레인 **병렬화**. Domain/Analyst/Researcher 셋 모두 non-skippable로 승격 + 병렬 스폰 (각자 공통 입력에서 관점 자체 도출), CodebaseMapper·Refactor 병렬 스폰 (둘 다 원 소스 직접 독해). PL/Architect가 진정한 synthesizer 역할. Clarification 재스폰 프로토콜 신설.

## 라이선스

TBD.

## 연혁

전체 릴리스 이력은 [`CHANGELOG.md`](CHANGELOG.md) 참조.
