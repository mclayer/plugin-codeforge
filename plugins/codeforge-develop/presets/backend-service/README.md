# backend-service preset

비-webapp **backend service** 프로젝트용 Dev 에이전트 번들. 서버 라우트·템플릿·정적 자산 이원화가 **없는** frontend-less shape — 인터넷 비도달·long-running service / CLI 도구 / daemon / worker 에 적합. Rust / Go / Python service 공통 (language-agnostic).

> "Backend Service" = 산업 표준 배포 유형명 (인터넷 비노출·long-running·service-discovery 로 내부 도달). web service 와 disjoint — webapp preset 이 아닌 본 preset 을 쓴다.

## 포함 agent

| 에이전트 | 역할 | 기본 경로 |
|----------|------|-----------|
| `ServiceDeveloperAgent` | 도메인·포트·어댑터·CLI·daemon·worker 진입점 | `src/**` (adapters/storage·sources 제외) |

`role: dev` frontmatter → DevPL이 자동 roster에 포함. `model: sonnet` (구현 tier — ADR-042 §결정 1(b) Implementation work).

웹앱처럼 Backend/Frontend로 이원화하지 않는다 — backend service 레이어는 단일 Change Plan 단위로 공동 수정되므로 단일 generic agent 가 자연 경계 (frontend 분할 부재).

## 사용법

```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/backend-service/agents/*.md \
      .claude/_overlay/agents/
```

SessionStart hook(regen-agents.sh)이 이후 세션에서 overlay-only agent로 감지해 `.claude/agents/<Name>.md`로 렌더한다 (core counterpart 없이 단독 렌더).

## Core `DeveloperAgent`와의 충돌 방지

Core의 generic `DeveloperAgent`는 `Write(src/**)`를 광범위하게 소유. backend-service preset을 쓰면 `ServiceDeveloperAgent`와 경로 겹침(`src/**`)이 발생한다.

### 해결책 A — `DeveloperAgent` 비활성화 (권장)

단일 service dev 엔 잔여 경로가 없으므로 generic `DeveloperAgent`를 비활성화하는 것이 자연스럽다. `ServiceDeveloperAgent`(sonnet)가 `src/**` 구현을 단독 소유한다.

```bash
# consumer overlay에서 DeveloperAgent 비활성화:
# .claude/_overlay/agents/DeveloperAgent.md 를 "빈 permissions" overlay로 작성하거나
# .claude/agents/DeveloperAgent.md 를 .gitignore + 생성 후 삭제 운용
```

가장 깔끔한 방법: `.claude/_overlay/CLAUDE.md`에 "이 프로젝트는 generic `DeveloperAgent` 대신 `ServiceDeveloperAgent`를 사용"을 명시해 Orchestrator가 DeveloperAgent 스폰 후보에서 제외하게 한다.

> 본 preset 은 generic `DeveloperAgent` 파일을 건드리지 않는다 — 충돌 회피는 전적으로 consumer overlay 측 비활성화 지시로 수행한다.

## 데이터 어댑터 경계 (DataEngineerAgent 보존)

`ServiceDeveloperAgent`의 deny 경계는 `src/**/adapters/storage/**` + `src/**/adapters/sources/**`를 포함한다 — 이 2종은 core `DataEngineerAgent`(`role: dev`)의 allow 경로다. backend service 구현 lane 에 routine 등장하므로 기본값으로 보존해 path 소유 충돌을 막는다.

`DataEngineerAgent`를 쓰지 않는 consumer가 이 adapter 영역을 `ServiceDeveloperAgent`로 넘기려면 overlay에서 해당 deny를 해제한다 (preset default = 안전쪽 보존).

## Preset agent 커스터마이즈

복사된 preset agent는 이제 consumer 소유. 자유롭게 수정:
- 프레임워크 구체화 (예: 본문에 "Rust + tokio + axum" 또는 "Go + grpc-go" 명시)
- 경로 scoping 재정의 (`src/service/**` vs `src/cli/**` 등 프로젝트 관습 반영)
- 금지 사항 추가·완화 (DataEng 미사용 시 adapter deny 해제 등)

Plugin 업데이트로 preset 원본이 바뀌었을 때는 consumer가 직접 diff 반영:

```bash
diff ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/backend-service/agents/ServiceDeveloperAgent.md \
     .claude/_overlay/agents/ServiceDeveloperAgent.md
```

## 확장 예시

`ServiceDeveloperAgent` 단독으로 부족하면 consumer overlay에서 추가 `role: dev` 에이전트 정의 가능:
- `WorkerDeveloperAgent` (백그라운드 작업/큐 컨슈머 전담)
- `CLIDeveloperAgent` (CLI 명령 트리 전담)
- `ProtocolDeveloperAgent` (gRPC/프로토콜 핸들러 전담)

`role: dev` 태그만 있으면 DevPL roster에 자동 포함.
