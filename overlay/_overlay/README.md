# Consumer Project `.claude/_overlay/` 스켈레톤

이 디렉토리는 **consumer 프로젝트가 자신의 repo에 복사해 두고 편집하는** overlay 소스의 참조 구조. 플러그인 자체는 이 디렉토리를 로드하지 않는다.

## 복사 방법

```bash
# consumer project root에서
mkdir -p .claude/_overlay/agents
cp -r ${PLUGIN_ROOT}/overlay/_overlay/* .claude/_overlay/
```

## 구조

```
<consumer-project>/
└── .claude/
    ├── _overlay/
    │   ├── CLAUDE.md                   # 프로젝트 특화 규칙·상수 (선택)
    │   └── agents/                     # 필요한 에이전트만 overlay (sparse)
    │       ├── DomainAgent.md          # 프로젝트 도메인 전문가 (도메인 용어·제약·소스)
    │       ├── DataEngineerAgent.md    # 프로젝트 데이터 파이프라인 (경로·기술 스택)
    │       └── ...
    ├── settings.json                   # SessionStart hook 등록
    └── agents/                         # GENERATED (hook 산출물, gitignore 권장)
```

## overlay 작성 규칙

### agents/<Name>.md

- **frontmatter**: 배열·맵만 확장 (tools·permissions). 스칼라(name/description/model/color)는 건들지 말 것 (merge 시 mismatch → abort)
- **body**: 순수 markdown. 자동으로 core 뒤에 `\n\n---\n\n## Project Overlay\n\n` 구분자와 함께 붙음
- core의 특정 섹션을 "덮어쓰려면" 명시적으로 "위 core §X의 X 지침은 이 프로젝트에서 Y로 대체한다"라고 서술 (파서는 단순 append)

### CLAUDE.md

- 플러그인의 CLAUDE.md core는 오케스트레이션 규칙·에이전트 구조. overlay에는 **프로젝트 식별·SSOT 상수·도메인 소개** 작성.
- 예: 프로젝트 이름·Confluence space key·Jira project key·ADR 트리 위치·도메인 특화 섹션.

## 예시: overlay/_overlay/agents/DataEngineerAgent.md (최소)

```markdown
---
permissions:
  allow:
    - Edit(src/<your-project>/adapters/sources/**)
    - Write(src/<your-project>/adapters/sources/**)
---

이 프로젝트의 데이터 계층 설명 — 수집 방식 · 저장 포맷 · 조회 도구.

기술 스택:
- 수집: <HTTP/Kafka/WebSocket/파일 등>
- 저장: <DB/파일 포맷/워크로드 스토리지>
- 조회: <SQL/OLAP/프로젝트 특화 쿼리 레이어>

주요 경로:
- `src/<your-project>/adapters/sources/**` — 외부 데이터 소스 어댑터
- `src/<your-project>/adapters/storage/**` — 저장 계층
- `schemas/**` — 데이터 스키마 정의

기존 ADR:
- ADR-<NNN>: <프로젝트 고유 데이터 결정>
```

## regenerate

Consumer `.claude/settings.json`에 SessionStart hook 등록:

```json
{
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

세션 시작 시 자동 실행 → `.claude/agents/*.md`, `CLAUDE.md` 재생성.
