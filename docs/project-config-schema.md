---
title: project.yaml schema — consumer SSOT 상수 구조화
status: active
created: 2026-04-24
updated: 2026-04-24
---

# `project.yaml` Schema

Consumer 프로젝트의 **objective SSOT 상수**를 구조화 주입하는 파일. 위치: `.claude/_overlay/project.yaml`.

에이전트(특히 DocsAgent·RequirementsPLAgent·DomainAgent)는 이 파일을 `Read` 툴로 직접 읽어 Atlassian/GitHub 상수를 확보한다. CLAUDE.md overlay는 **narrative 컨텍스트**(도메인 해설·기술 스택 근거)에 집중.

## 1. 경계

### project.yaml에 들어가는 것 (structured)
- Atlassian 좌표 (Confluence space·pageIds, Jira project key·transition IDs)
- GitHub 좌표 (repo URL, PR 제목 포맷)
- Label taxonomy 프로젝트별 확장 (`component:*` 구체값)
- 프로젝트 식별자 (name, repo)

### CLAUDE.md overlay에 들어가는 것 (narrative)
- 도메인 소개·용어 사전
- 기술 스택 선택 근거
- 경로 관습의 설계 근거
- DomainAgent 등이 소비할 서술 컨텍스트

### 에이전트별 overlay에 들어가는 것 (agent-specific)
- 경로 scoping (`permissions.allow/deny` 구체 경로)
- 에이전트 고유 지침 (프레임워크·라이브러리 명시 등)

## 2. Schema

```yaml
# .claude/_overlay/project.yaml

# [필수] 프로젝트 식별
project:
  name: <string>                    # e.g. "task-manager"
  repo: <string>                    # e.g. "github.com/acme/task-manager"

# [필수] Atlassian 좌표
atlassian:
  site: <string>                    # e.g. "acme.atlassian.net"

  confluence:
    space_key: <string>             # e.g. "TM"
    stories_parent_page_id: <integer|string>   # Story 페이지 parent
    domain_knowledge_parent_page_id: <integer|string>  # Domain Knowledge 루트
    adr_root_page_id: <integer|string>         # ADR 루트
    # Optional: 추가 parent 지정 (회고·패턴 등)
    # retrospective_parent_page_id: <integer|string>

  jira:
    project_key: <string>           # e.g. "TM"
    # Optional: transition ID 정적 매핑. 없으면 DocsAgent가
    # getTransitionsForJiraIssue로 동적 획득.
    transitions:
      to_in_progress: <integer>
      to_done: <integer>

# [필수] GitHub 좌표
github:
  # PR 제목 템플릿. {project_key}·{story_number}·{title} placeholder 지원
  pr_title_prefix_template: <string>   # e.g. "[{project_key}-{story_number}] {title}"

# [선택] 프로젝트별 label 확장
# phase:*·fix:*·adr:*·impl-manifest·hotfix:*·audit:* 는 core에서 정의 (overlay 대상 아님).
# consumer는 component:* 만 정의.
labels:
  components:                       # 각 항목이 "component:<name>" 라벨로 생성
    - <string>                      # e.g. "api", "ui", "data"
```

## 3. 예시 (webapp)

```yaml
project:
  name: task-manager
  repo: github.com/acme/task-manager

atlassian:
  site: acme.atlassian.net
  confluence:
    space_key: TM
    stories_parent_page_id: 12345
    domain_knowledge_parent_page_id: 12346
    adr_root_page_id: 12347
  jira:
    project_key: TM
    # transitions 생략 → DocsAgent가 동적 조회

github:
  pr_title_prefix_template: "[{project_key}-{story_number}] {title}"

labels:
  components:
    - api
    - ui
    - data
    - infra
```

## 4. 에이전트 접근 규칙

### 4a. Read 전담
- **DocsAgent**: Jira/Confluence 호출 시 `project_key` / `space_key` / `stories_parent_page_id` 활용
- **RequirementsPLAgent**: Story 페이지 생성·갱신 시 parent pageId 결정
- **DomainAgent**: Domain Knowledge 트리 fetch 시 root pageId 사용
- **PMOAgent**: 회고·패턴 페이지 생성 시 parent 결정
- **Orchestrator**: 세션 개시 시 1회 read → 필요 값 Context Packet으로 하위 에이전트에 전달 가능 (반복 fetch 회피)

### 4b. Write 금지
모든 에이전트는 `.claude/_overlay/project.yaml` **write 금지**. 이 파일은 consumer가 직접 관리. DocsAgent도 쓰지 않음.

### 4c. 값 부재 시 동작
- **필수 필드 missing** → 에이전트는 블록 후 Orchestrator에 "project.yaml에 `<field>` 누락" 보고. Orchestrator가 사용자에게 질의.
- **선택 필드 missing** → 기본 동작 (예: transitions 없으면 동적 조회)

## 5. 파일 부재 케이스

`.claude/_overlay/project.yaml`이 아예 없으면:
- 세션 개시 시 Orchestrator가 경고 출력: "project.yaml 없음 — Atlassian/Jira 기능 제한됨"
- DocsAgent·RequirementsPLAgent 등이 Atlassian MCP 호출 시 ERROR (필수 상수 unknown)
- 작업 지속은 가능하나 문서 동기화·Story 관리 기능 대부분 차단됨

신규 consumer는 `overlay/_overlay/project.yaml.example`을 복사해 시작.

## 6. Hook 통합 Schema 검증 (v0.5.0+)

SessionStart hook (`regen-agents.sh`)이 `overlay/hooks/validate_config.py`를 자동 실행:

- **missing file** → WARN (exit 0) · 계속 진행. 초기 설정 중인 consumer용
- **malformed YAML** → ERROR (exit 3) · hook abort
- **required field 누락 / 타입 위반** → ERROR (exit 4) · hook abort

수동 실행:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/validate_config.py \
    .claude/_overlay/project.yaml
```

구현은 hand-rolled 타입 체크 (`jsonschema` 의존성 회피 — PyYAML만 필요). 규칙은 `validate_config.py` `SCHEMA_RULES` 리스트.

## 7. 장래 확장 (미구현)

- **환경 변수 참조**: `${ENV_VAR}` placeholder 지원 (secrets 분리)
- **Context Packet 자동 주입**: Orchestrator가 project.yaml 요약을 sub-agent 프롬프트에 자동 삽입
- **기술 스택 일부 구조화**: test runner·perf baseline 경로 등 objective 성격 항목 이전
- **placeholder 탐지**: `<REPLACE ...>` 값이 남아있으면 warn (unconfigured consumer 감지)

## 8. 관련 문서

- [`consumer-guide.md`](consumer-guide.md) §3 — 실제 설정·복사 절차
- [`plugin-design.md`](plugin-design.md) §5 — Stage 1/2 범위
- [`../overlay/_overlay/project.yaml.example`](../overlay/_overlay/project.yaml.example) — 스켈레톤
- [`../overlay/hooks/validate_config.py`](../overlay/hooks/validate_config.py) — Schema 검증 구현
- [`../agents/DocsAgent.md`](../agents/DocsAgent.md) — 주 소비자
