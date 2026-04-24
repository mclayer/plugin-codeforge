# webapp preset

웹 애플리케이션 프로젝트용 Dev 에이전트 번들. **서버 라우트·템플릿·정적 자산 이원화**가 있는 풀스택/반-스택 웹 프로젝트에 적합.

## 포함 agent

| 에이전트 | 역할 | 기본 경로 |
|----------|------|-----------|
| `BackendDeveloperAgent` | 서버 라우트·도메인·포트·어댑터 | `src/**` (templates/static/adapters/storage·sources 제외) |
| `FrontendDeveloperAgent` | 템플릿·정적 자산·클라이언트 JS/CSS | `src/**/templates/**`, `src/**/static/**`, `templates/**`, `static/**` |

두 에이전트 모두 `role: dev` frontmatter → DevPL이 자동 roster에 포함.

## 사용법

```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

## Core `DeveloperAgent`와의 충돌 방지

Core의 generic `DeveloperAgent`는 `Write(src/**)`를 광범위하게 소유. webapp preset을 쓰면 경로 겹침 발생.

### 해결책 2가지

**(A) `DeveloperAgent` 비활성화 (권장)** — 웹앱에선 Backend+Frontend로 충분
```bash
# consumer overlay에서 DeveloperAgent 비활성화:
# .claude/_overlay/agents/DeveloperAgent.md 를 "빈 permissions" overlay로 작성하거나
# .claude/agents/DeveloperAgent.md 를 .gitignore + 생성 후 삭제 운용
```

가장 깔끔한 방법: `.claude/_overlay/CLAUDE.md`에 "이 프로젝트는 `DeveloperAgent` 대신 Backend/Frontend를 사용"을 명시해 Orchestrator가 DeveloperAgent 스폰 후보에서 제외하게 한다.

**(B) 경로 재정의** — Backend/Frontend가 각자 scope을 조이고, 그 외 잔여 영역을 `DeveloperAgent`가 담당
```yaml
# .claude/_overlay/agents/DeveloperAgent.md 에서
permissions:
  deny:
    - "Write(src/**/routes/**)"      # Backend 영역
    - "Write(src/**/templates/**)"   # Frontend 영역
    - "Write(src/**/static/**)"      # Frontend 영역
    - "Write(src/**/adapters/**)"    # DataEng 영역
```

## 확장 예시

Backend/Frontend로 부족하면 consumer overlay에서 추가 `role: dev` 에이전트 정의 가능:
- `APIGatewayDeveloperAgent` (라우트 전담)
- `AuthDeveloperAgent` (인증/권한 전담)
- `UIComponentDeveloperAgent` (디자인 시스템 컴포넌트 전담)

`role: dev` 태그만 있으면 DevPL roster에 자동 포함.
