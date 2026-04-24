# dev-orchestrator

**Claude Code 범용 SW 개발 오케스트레이션 플러그인**. 사용자 요구사항 한 건을 받아 **24 core 에이전트 + `role: dev` 동적 roster · 7 레인** 구조로 요구사항 해석 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트 게이트까지 자율 실행한다.

## 주요 특징

- **24 core 에이전트 + `role: dev` 동적 roster · 7 레인 · 2 Cross-cutting** 구조로 SW 개발 프로세스 전반 커버
- **프로젝트 shape별 preset** (`presets/webapp` 등) — 웹앱·CLI·라이브러리·임베디드 등 Dev 구성 번들을 골라 overlay에 임포트
- **CodebaseMapper ↔ Refactor 이념 대립** 으로 설계 균형 확보
- **Claude + Codex(GPT-5) peer 리뷰** 로 설계 리뷰·코드 리뷰·보안 테스트 3중 peer 이중화
- **보안 테스트 전용 레인** (OWASP·CWE·CVE·trust boundary·credential) — Story 완료 전 필수 게이트
- **FIX 루프 상태 머신** — 설계 리뷰·구현 리뷰 최대 3회, 구현 테스트·보안 테스트 FIX 무제한
- **Overlay 메커니즘 (β)** — consumer 프로젝트가 도메인·SSOT 상수·기술 스택을 파일 분리 방식으로 확장
- **Templates SSOT** (`templates/`) — Change Plan · ADR · Story Page · Impl Manifest 양식 일원화
- **단독 문서 writer (DocsAgent)** 를 통한 Jira·Confluence·docs 일관성 보장

## 에이전트 구조

```
(Human) 사용자
   ↓
Orchestrator (최상위 Claude 세션)
 ├── [Cross-cutting] PMOAgent, DocsAgent
 ├── [요구사항] RequirementsPL (DomainAgent → Analyst → Researcher)
 ├── [설계] Architect (CodebaseMapper vs Refactor)
 ├── [설계 리뷰] DesignReviewPL (Claude ‖ Codex)
 ├── [구현] DeveloperPL (role:dev roster 병렬) + QADev
 ├── [구현 리뷰] CodeReviewPL (Claude ‖ Codex)
 ├── [구현 테스트] TestAgent
 └── [보안 테스트] SecurityTestPL (Claude ‖ Codex)
```

상세는 [`CLAUDE.md`](CLAUDE.md) 참조.

## 설치 · 사용

### 1. 플러그인 설치

```bash
/plugins install dev-orchestrator@<marketplace>
```

### 2. 필수 의존성

- MCP: `atlassian` (Jira + Confluence)
- 플러그인: `codex@openai-codex`, `superpowers@claude-plugins-official`, `claude-md-management@claude-plugins-official`
- CLI: `codex`

세션 개시 시 자동 점검 · 미설치 시 blocking wait.

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
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

`.claude/_overlay/CLAUDE.md`와 `.claude/_overlay/agents/<Name>.md`(필요한 에이전트만)에 프로젝트 특화 내용 작성.

## 문서

| 파일 | 내용 |
|------|------|
| [`CLAUDE.md`](CLAUDE.md) | 오케스트레이션 규칙 SSOT — 에이전트·레인·권한·FIX 루프·Jira/ADR 규약 |
| [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) | Orchestrator 행동 SSOT — 생명주기·스폰·상태 머신·토큰 예산·트러블슈팅 |
| [`docs/consumer-guide.md`](docs/consumer-guide.md) | Consumer 프로젝트 설치·overlay 작성 가이드 |
| [`docs/plugin-design.md`](docs/plugin-design.md) | 플러그인 설계 spec — core/overlay 분리 원칙·merge 계약·β 메커니즘 |
| [`docs/project-config-schema.md`](docs/project-config-schema.md) | `project.yaml` Schema SSOT — Atlassian·GitHub·labels 구조화 상수 |
| [`templates/`](templates/) | 공통 문서 양식 SSOT — Change Plan · ADR · Story Page · Impl Manifest |
| [`presets/`](presets/) | 프로젝트 shape별 Dev 에이전트 번들 — webapp 등 |
| `agents/*.md` | 24 core 에이전트 SSOT |

## 구조

```
dev-orchestrator/
├── .claude-plugin/
│   └── plugin.json
├── agents/                       # 24 core agent md (process + generic Dev)
├── presets/                      # 프로젝트 shape별 Dev 번들
│   ├── README.md
│   └── webapp/
│       ├── README.md
│       └── agents/
│           ├── BackendDeveloperAgent.md
│           └── FrontendDeveloperAgent.md
├── templates/                    # 공통 문서 양식 SSOT
│   ├── change-plan.md
│   ├── adr.md
│   ├── story-page-structure.md
│   └── impl-manifest.md
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

`0.4.0` — Stage 2 `project.yaml` 구조화 SSOT 상수 도입. Consumer의 Atlassian·GitHub·labels 상수를 `.claude/_overlay/project.yaml`로 structured 분리 (CLAUDE.md overlay는 narrative 전담). Schema SSOT는 `docs/project-config-schema.md`. 예시 2종 overlay 재구성, DocsAgent·DomainAgent 등 주 소비자 업데이트.

## 라이선스

TBD.

## 연혁

- **2026-04-24 (v0.1.0)**: 플러그인 pivot — 기존 crypto FW repo(`mctrader`)에서 범용 SW 개발 플러그인으로 재편. Archive tag `archive/pre-plugin-pivot-20260424`에 pivot 직전 상태 보존.
- **2026-04-24 (v0.2.0)**: 보안 테스트 레인 추가 — `SecurityTestPLAgent` + `ClaudeSecurityTestAgent` + `CodexSecurityTestAgent` 신설. 기존 "테스트" 레인 → "구현 테스트" + "보안 테스트" 2단계. `templates/` 디렉토리 SSOT 도입 (Change Plan · ADR · Story Page · Impl Manifest 양식 독립 파일화).
- **2026-04-24 (v0.3.0)**: Generic Dev roster + preset 시스템 — 웹 편향 제거. `BackendDeveloperAgent` · `FrontendDeveloperAgent`를 `presets/webapp/`으로 이동, core에 generic `DeveloperAgent` 신설, `ServerEngineerAgent` → `InfraEngineerAgent` 리네임(범위 확장). `DeveloperPLAgent`가 `role: dev` frontmatter 태그로 동적 roster discovery. `merge.py`에 `--overlay-only` 모드 추가 (core 없는 consumer-defined agent 지원). Core 24 에이전트 + `role: dev` 동적 roster.
- **2026-04-24 (v0.4.0)**: Stage 2 `project.yaml` 구조화 SSOT 상수 도입. Atlassian·GitHub·labels를 `.claude/_overlay/project.yaml`에 structured 분리, CLAUDE.md overlay는 narrative 컨텍스트(도메인·기술 스택 근거)만 담당. Schema SSOT 신설 (`docs/project-config-schema.md`). DocsAgent·DomainAgent 등이 Atlassian 호출 전 project.yaml을 직접 read. 예시 2종 overlay 재구성.
