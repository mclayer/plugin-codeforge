# dev-orchestrator

**Claude Code 범용 SW 개발 오케스트레이션 플러그인**. 사용자 요구사항 한 건을 받아 **22 에이전트 · 6 레인** 구조로 요구사항 해석 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 테스트 게이트까지 자율 실행한다.

## 주요 특징

- **22 에이전트 · 6 레인 · 2 Cross-cutting** 구조로 SW 개발 프로세스 전반 커버
- **CodebaseMapper ↔ Refactor 이념 대립** 으로 설계 균형 확보
- **Claude + Codex(GPT-5) peer 리뷰** 로 설계 리뷰·코드 리뷰 이중화
- **FIX 루프 상태 머신** — 설계 리뷰·구현 리뷰 최대 3회, 테스트 FIX 무제한
- **Overlay 메커니즘 (β)** — consumer 프로젝트가 도메인·SSOT 상수·기술 스택을 파일 분리 방식으로 확장
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
 ├── [구현] DeveloperPL (4 Dev 병렬) + QADev
 ├── [구현 리뷰] CodeReviewPL (Claude ‖ Codex)
 └── [테스트] TestAgent
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
| `agents/*.md` | 22 에이전트 SSOT (core) |

## 구조

```
dev-orchestrator/
├── .claude-plugin/
│   └── plugin.json
├── agents/                       # 22 core agent md
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

`0.1.0` — 초기 플러그인 형태. Stage 2 (structured config + playbook overlay) 예정.

## 라이선스

TBD.

## 연혁

- **2026-04-24**: 플러그인 pivot — 기존 crypto FW repo(`mctrader`)에서 범용 SW 개발 플러그인으로 재편. Archive tag `archive/pre-plugin-pivot-20260424`에 pivot 직전 상태 보존.
