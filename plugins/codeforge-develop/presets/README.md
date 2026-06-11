# Presets — 프로젝트 shape별 overlay 번들

Core `agents/`는 프로젝트 shape에 중립적인 agent 구성만 유지한다. 특정 프로젝트 유형(웹앱·CLI·임베디드 등)에 반복되는 Dev 구성 패턴은 여기 **preset**으로 제공.

Preset은 **참조 레시피**. Consumer가 필요 시 수동으로 `.claude/_overlay/agents/`에 복사해 사용한다. Hook이 자동으로 preset을 로드하지 않는다 (overlay는 consumer 소유 원칙 유지).

## 구조

```
presets/
├── README.md                    # 이 파일
├── docker-compose.test.yml      # 통합테스트 격리 환경 템플릿 (CFP-367 / ADR-055)
└── webapp/                      # 웹 애플리케이션 preset
    ├── README.md
    └── agents/
        ├── BackendDeveloperAgent.md    (role: dev)
        └── FrontendDeveloperAgent.md   (role: dev)
```

추가 preset은 실수요 기반으로 Stage 2 이후 확장 예정 (cli-tool, library, embedded, game, desktop-app 등).

## 사용법

Consumer 프로젝트에서:

```bash
# 예: webapp preset 전체 복사
cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
      .claude/_overlay/agents/

# 또는 일부만 골라 복사 (frontend만)
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/FrontendDeveloperAgent.md \
   .claude/_overlay/agents/
```

SessionStart hook(regen-agents.sh)이 이후 세션에서 overlay-only agent로 감지해 `.claude/agents/<Name>.md`로 렌더한다 (core 없음).

## Preset agent 커스터마이즈

복사된 preset agent는 이제 consumer 소유. 자유롭게 수정:
- 프레임워크 구체화 (예: BackendDev 본문에 "FastAPI + SQLAlchemy 2.0" 명시)
- 경로 scoping 재정의 (`src/api/**` vs `src/web/**` 등 프로젝트 관습 반영)
- 금지 사항 추가·완화

Plugin 업데이트로 preset 원본이 바뀌었을 때는 consumer가 직접 diff 반영:

```bash
diff ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/BackendDeveloperAgent.md \
     .claude/_overlay/agents/BackendDeveloperAgent.md
```

## docker-compose.test.yml 사용법

IntegrationTestAgent가 사용하는 통합테스트 격리 환경 템플릿. InfraEngineerAgent가 §8.6 environment_dependencies를 참고해 레포 루트에 복사 후 커스터마이즈:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/docker-compose.test.yml .
```

3 서비스 구성:
- `app`: 테스트 대상 실제 애플리케이션 컨테이너 (static mock 금지)
- `test-db`: 격리 PostgreSQL (운영 DB와 완전 분리, ephemeral)
- `wiremock`: 외부 API WireMock stub (계약 기반, 실제 API 스펙 일치 필수)

## 신규 preset 기여

특정 프로젝트 shape에 반복되는 Dev 구성이 있으면 `presets/<shape>/agents/<Name>.md` + `presets/<shape>/README.md`로 PR.

- 모든 preset agent는 `role: dev` frontmatter 필수 (DevPL이 roster discovery에서 인식)
- preset은 **overlay shape 파일**로 작성 (core counterpart 없이 단독 렌더)
- 경로 scoping은 해당 shape의 관습 반영 (webapp = `src/**/templates/**` 등)
