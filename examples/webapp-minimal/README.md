# webapp-minimal — 웹 애플리케이션 consumer 예시

풀스택 웹 애플리케이션 프로젝트를 `codeforge` 플러그인으로 개발할 때의 overlay 구성 예시. 가상 도메인은 **Task Manager** (할 일·담당자·팀 관리), 기술 스택은 consumer가 채움.

## Dev roster

webapp preset 활용:
- `BackendDeveloperAgent` (preset) — 라우트·도메인·인증·서비스 레이어
- `FrontendDeveloperAgent` (preset) — 템플릿·정적 자산·UI
- `DataEngineerAgent` (core) — DB 어댑터·마이그레이션·스키마
- `InfraEngineerAgent` (core) — 배포·CI·설정
- `QADeveloperAgent` (core) — tests/**
- `DeveloperAgent` (core) — **비활성화** (Backend/Frontend로 커버 → CLAUDE.md overlay에 명시)

## 구조

```
webapp-minimal/
├── README.md
├── .claude/
│   ├── settings.json                           # SessionStart hook 등록
│   └── _overlay/
│       ├── CLAUDE.md                           # 프로젝트 SSOT 상수
│       └── agents/
│           ├── BackendDeveloperAgent.md        # preset 복사 + 웹앱 특화
│           ├── FrontendDeveloperAgent.md       # preset 복사 + 웹앱 특화
│           ├── DomainAgent.md                  # 도메인 용어·제약
│           └── DataEngineerAgent.md            # 저장소·스키마 특화
└── .gitignore
```

## 적용 단계

### 1. 복사 · 플레이스홀더 치환

```bash
cp -r examples/webapp-minimal/ ~/my-webapp/
cd ~/my-webapp
```

`.claude/_overlay/project.yaml`과 `CLAUDE.md`의 `<REPLACE: ...>` 전부 치환:
- 프로젝트명
- GitHub org/repo
- story_key_prefix (예: TM)
- CODEOWNERS team (architect/domain-expert)
- 컴포넌트 라벨 (component:*)

### 2. Preset agent 커스터마이즈

이미 `.claude/_overlay/agents/BackendDeveloperAgent.md`·`FrontendDeveloperAgent.md`가 preset에서 복사돼 있음. 본인 stack에 맞게 수정:
- 프레임워크 명시 (FastAPI/Flask/Rails/Express 등)
- 경로 관습 (`src/api/routes/**`, `src/web/templates/**` 등)
- 허용·거부 경로 scoping

### 3. Hook 확인

```bash
cat .claude/settings.json
# SessionStart 훅이 플러그인의 regen-agents.sh를 가리키는지 확인
```

### 4. 세션 시작

```bash
claude
# SessionStart hook이 .claude/agents/*.md와 CLAUDE.md 자동 생성
ls .claude/agents/
```

## Consumer 실수요 검증 포인트

이 예시가 실제 웹앱에 맞는지 보려면:
- `.claude/agents/BackendDeveloperAgent.md` 출력에 본인 stack이 반영됐는지
- `Write(src/api/**)` 등 overlay 경로가 `permissions.allow`에 들어갔는지
- `DomainAgent`가 프로젝트 도메인 용어·제약을 가지고 있는지

안 맞으면 overlay를 수정하고 다시 세션 시작 → 재생성.
