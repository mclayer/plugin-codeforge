# Example Consumer Projects

`codeforge` 플러그인을 consumer 프로젝트로 사용하는 최소 예시들. 각 예시는 **overlay shape만 포함** (실제 src/ 코드는 없음) — consumer가 본인 stack을 채워 넣는 전제.

## 목록

| 예시 | 프로젝트 shape | Dev roster 구성 |
|------|----------------|------------------|
| [`webapp-minimal/`](webapp-minimal/) | 웹 애플리케이션 | webapp preset (Backend·Frontend) + DataEng + InfraEng + QADev |
| [`cli-tool-minimal/`](cli-tool-minimal/) | CLI 툴 | Generic DeveloperAgent + InfraEng + QADev (preset 미사용) |
| [`library-minimal/`](library-minimal/) | 배포 라이브러리 | Generic DeveloperAgent + InfraEng + QADev (preset 미사용, 공개 API 경로 scoping 강조) |

세 예시는 플러그인이 **웹앱·CLI·라이브러리 shape에서 동일한 오케스트레이션으로 동작**함을 실증한다. Core `agents/`는 프로젝트 shape 중립, Dev roster는 `role: dev` frontmatter 태그로 런타임 discovery.

## 사용법 (공통)

1. 예시 디렉토리를 새 프로젝트 repo로 복사:
   ```bash
   cp -r examples/webapp-minimal/ ~/my-new-project/
   cd ~/my-new-project
   git init
   ```

2. `.claude/_overlay/project.yaml`과 `CLAUDE.md`의 `<REPLACE: ...>` 플레이스홀더를 본인 프로젝트 값으로 치환 (프로젝트명·GitHub org/repo·story_key_prefix·CODEOWNERS team 등).

3. 필요 시 `.claude/_overlay/agents/*.md`의 경로 관습·도메인 용어·기술 스택을 본인 stack에 맞게 수정.

4. `claude` 실행 — SessionStart hook이 `.claude/agents/*.md`와 `CLAUDE.md` 자동 생성.

자세한 consumer 가이드는 [`../docs/consumer-guide.md`](../docs/consumer-guide.md).

## 추가 shape 예시 기여

library, embedded, game, desktop-app 등 shape 예시가 필요하면 `examples/<shape>-minimal/`으로 PR. 포맷은 기존 예시와 동일 구조 권장.
