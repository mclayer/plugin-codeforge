# Consumer Guide — 플러그인 적용 가이드

이 플러그인(`dev-orchestrator`)을 consumer 프로젝트에서 사용하는 방법.

## 1. 설치

### 1a. 플러그인 설치 (marketplace 경유)

```bash
/plugins install dev-orchestrator@<marketplace>
```

또는 로컬 경로 설치(개발 중인 플러그인 테스트 시):

```bash
/plugins install /path/to/dev-orchestrator-repo
```

설치 확인:

```bash
ls ~/.claude/plugins/cache/<marketplace>/dev-orchestrator/<version>/agents/
# ArchitectAgent.md  DeveloperAgent.md  ...
```

### 1b. 필수 의존성 3종

`CLAUDE.md` §"세션 개시 의무"에 명시된 3종 미설치 시 플러그인 동작 불가:

- MCP: `atlassian` 인증 완료
- 플러그인: `codex@openai-codex`, `superpowers@claude-plugins-official`, `claude-md-management@claude-plugins-official`
- CLI: `codex`

## 2. Consumer 프로젝트 구조 초기화

```
<consumer-project>/
├── .claude/
│   ├── _overlay/                       # 프로젝트 특화 overlay (편집 대상)
│   │   ├── CLAUDE.md                   # 프로젝트 식별·SSOT 상수
│   │   └── agents/
│   │       ├── DomainAgent.md          # 도메인 전문가 특화
│   │       ├── DataEngineerAgent.md    # 데이터 계층 특화
│   │       └── ...                     # 필요한 에이전트만
│   ├── agents/                         # GENERATED (hook 산출물, gitignore)
│   ├── settings.json                   # SessionStart hook 등록
│   └── settings.local.json             # (선택) 로컬 오버라이드
├── CLAUDE.md                           # GENERATED (hook 산출물, gitignore 또는 commit)
├── .claude-work/                       # DocsAgent write queue (gitignore)
└── ...
```

### 2a. 초기 복사

```bash
# consumer project root에서
mkdir -p .claude/_overlay/agents
cp ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/_overlay/README.md .claude/_overlay/
```

### 2b. `.claude/settings.json` 설정 (SessionStart hook 등록)

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh" }
    ]
  },
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

### 2c. `.gitignore`에 추가

```gitignore
# dev-orchestrator plugin — generated files
.claude/agents/
.claude-work/
CLAUDE.md    # core+overlay merge 결과면 gitignore. 수동 커밋 원하면 제외.
```

## 3. Overlay 작성

### 3a. `.claude/_overlay/project.yaml` — objective SSOT 상수

Atlassian·GitHub 좌표, label taxonomy 등 structured 상수는 `project.yaml`에 작성. 스켈레톤 복사 후 치환:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

Schema 전체 명세: [`project-config-schema.md`](project-config-schema.md). 주 소비자는 DocsAgent·RequirementsPLAgent·DomainAgent·PMOAgent. 에이전트는 이 파일을 `Read`로 직접 참조.

SessionStart hook이 자동으로 `validate_config.py`를 실행해 schema 준수를 검증. 위반 시 hook abort → 세션 개시 실패. 수동 검증:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/validate_config.py \
    .claude/_overlay/project.yaml
```

### 3b. `.claude/_overlay/CLAUDE.md` 예시 (narrative 컨텍스트)

CLAUDE.md overlay에는 **서술 컨텍스트만** (도메인 소개·기술 스택 선택 근거·경로 관습 설명). Objective 상수는 project.yaml에 있음.

```markdown
## Project

`<your-project>` — <한 줄 프로젝트 설명>. <기술 스택> 기반.

SSOT 상수는 `.claude/_overlay/project.yaml` 참조.

## Domain

<프로젝트 도메인 한 줄 서술 — 예: "e-commerce 결제 플랫폼 · PG 연동·환불·정산 전반">

## 기술 스택 (선택 근거)

- 언어: <선택 이유 포함>
- 저장소: <선택 이유>
- 배포: <선택 이유>

## 경로 관습

- `src/<your-domain>/...` — 도메인 로직
- `src/adapters/...` — 외부 시스템 어댑터
- 기타 프로젝트 관습
```

### 3c. Preset 임포트 (선택)

프로젝트 shape이 플러그인 preset과 맞으면 preset agents를 overlay로 복사.

```bash
# 예: 웹 애플리케이션 프로젝트
cp -r ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

복사된 agent는 이제 consumer 소유 — 자유롭게 프레임워크·경로 구체화. Core `DeveloperAgent`와 경로 overlap이 있으면 preset README의 "충돌 방지" 섹션 참조. Preset 미사용 프로젝트(CLI 툴, 라이브러리, 임베디드 등)는 core의 generic `DeveloperAgent`만 써도 되고, overlay에서 직접 `role: dev` 에이전트를 추가 정의해도 된다.

상세는 [`../presets/README.md`](../presets/README.md) 참조.

### 3d. `.claude/_overlay/agents/<Name>.md` 예시

프로젝트 특화 정보가 필요한 에이전트만 overlay 작성. 대부분 에이전트는 core만으로 충분. 예시 (프로젝트에 따라 자유롭게):

#### `.claude/_overlay/agents/DataEngineerAgent.md`

```markdown
---
permissions:
  allow:
    - Edit(src/<your-project>/adapters/sources/**)
    - Write(src/<your-project>/adapters/sources/**)
    - Edit(src/<your-project>/pipelines/**)
    - Write(src/<your-project>/pipelines/**)
---

### 프로젝트 데이터 파이프라인

기술 스택:
- 수집: <HTTP/Kafka/WebSocket/...>
- 저장: <DB/Parquet/ClickHouse/...>
- 조회: <SQL/ORM/특화 쿼리 레이어>

주요 경로:
- `src/<your-project>/adapters/sources/**` — 외부 데이터 소스 어댑터
- `src/<your-project>/adapters/storage/**` — 저장 계층
- `schemas/<프로젝트 스키마 파일들>`

ADR 제약:
- ADR-<NNN>: <프로젝트 고유 데이터 결정>
```

#### `.claude/_overlay/agents/DomainAgent.md`

```markdown
### 도메인 소스

- Confluence Domain Knowledge 트리: pageId=<domain-kb-root>
- ADR 카테고리 label: `<project-domain-category>`
- 도메인 코드 경로: `src/<your-project>/domain/**`
- 도메인 용어: <프로젝트 특화 용어 1>, <용어 2>, <용어 3>

### 우선순위 원칙
- <예: 지연 민감 / 데이터 일관성 / 보안 / 장애 복구 등 프로젝트별 최우선 항목>
- <예: 안전 제약 — 사용자 명시 해제 전까지 유지>
```

## 4. 첫 실행 검증

### 4a. Claude Code 세션 시작

프로젝트 디렉토리에서 `claude` 실행. SessionStart hook이 자동으로 `.claude/agents/*.md`와 `CLAUDE.md` 생성.

### 4b. 생성 결과 확인

```bash
ls -la .claude/agents/
# 22개 파일 (core + overlay 병합 결과)

head -20 .claude/agents/DataEngineerAgent.md
# frontmatter (merged) + "GENERATED FROM ..." 헤더 + core body + "## Project Overlay" + overlay body
```

### 4c. 권한 재확인

에이전트가 overlay에서 추가한 경로(예: `Edit(src/<your-project>/adapters/sources/**)`)로 실제 편집 가능한지 세션 내에서 확인.

## 5. Workflow

Consumer 프로젝트에서 요구사항을 입력하면 플러그인이 24 core 에이전트 + `role: dev` 동적 roster · 7 레인 구조로 자율 실행:

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트
```

상세 오케스트레이션 규칙은 [`orchestrator-playbook.md`](orchestrator-playbook.md).

## 6. FAQ

### Q1. Overlay에 스칼라 필드(name, description, model)가 들어가면?

**merge.py가 abort**한다. 스칼라는 core-only. 예외적으로 허용은 향후 탐색 예정.

### Q2. `.claude/agents/*.md`를 직접 편집하면?

SessionStart hook이 다음 실행 시 덮어쓴다. 편집하려면 `.claude/_overlay/agents/` 또는 플러그인 core agents/를 수정.

### Q3. Core 에이전트 자체를 바꾸고 싶다 (버그 수정·새 규칙 추가)

**플러그인 repo에 PR**. Core는 모든 consumer의 SSOT. overlay는 프로젝트 고유 내용만 담는 곳.

### Q4. 플러그인 업그레이드 시 overlay 호환성

core의 에이전트 섹션 구조·frontmatter 키가 바뀌면 overlay가 깨질 수 있다. 플러그인 버전 변경 시 `plugin.json`의 `version` 필드와 [`plugin-design.md`](plugin-design.md)의 compat note 확인.

### Q5. `codex` 플러그인 / CLI 미설치 상태에서 시작하면?

세션 시작 시 의존성 체크가 blocking wait 상태로 전환되며 설치 요청. 설치 전까지 어떤 작업도 진행 안 함.

## 7. 트러블슈팅

| 증상 | 원인 | 대응 |
|------|------|------|
| `regen-agents.sh: merge.py not found` | PLUGIN_ROOT 해석 실패 | `CLAUDE_PLUGIN_ROOT` 환경변수 확인, 또는 `PLUGIN_ROOT=...` 명시 |
| `ERROR: overlay scalar mismatch at '.name'` | overlay frontmatter에 core와 다른 name 지정 | overlay의 name 필드 제거 (name은 core-only) |
| `ERROR: PyYAML required` | python3 환경에 PyYAML 없음 | `pip install pyyaml` 또는 venv 설정 |
| Agent가 overlay 내용을 따르지 않음 | 생성된 `.claude/agents/<Name>.md` 확인 | `cat .claude/agents/<Name>.md` → overlay body 실제 존재하는지 점검 |
