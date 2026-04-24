---
title: Migration Guide — 플러그인 버전업 시 consumer overlay 변경 절차
status: active
created: 2026-04-24
updated: 2026-04-24
---

# Migration Guide

`codeforge` 플러그인 버전업 시 consumer 프로젝트의 overlay를 마이그레이션하는 절차.

각 섹션은 **한 major/minor 버전 bump 당 1건**. breaking change가 있는 버전만 다룬다. Core는 플러그인 업데이트 시 자동 반영되지만, `.claude/_overlay/` 내용은 consumer가 직접 업데이트.

## 목차

- [v0.5 → v0.6](#v05--v06-plugin-name-rename-dev-orchestrator--codeforge) — Plugin name rename + Atlassian 이관
- [v0.3 → v0.4](#v03--v04-stage-2-projectyaml-구조화) — `project.yaml` 도입
- [v0.2 → v0.3](#v02--v03-generic-dev-roster--preset) — Generic Dev roster + preset
- [v0.1 → v0.2](#v01--v02-보안-테스트-레인--templates) — 보안 테스트 레인 + templates (non-breaking)

---

## v0.5 → v0.6 (Plugin name rename `dev-orchestrator` → `codeforge`)

### Breaking changes

- **Plugin name 변경**: `dev-orchestrator` → `codeforge`
- **Marketplace install URL 변경** (해당 시): `/plugins install dev-orchestrator@<marketplace>` → `/plugins install codeforge@<marketplace>`
- **`CLAUDE_PLUGIN_ROOT` 하위 경로 변경**: `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/` → `${CLAUDE_PLUGIN_ROOT}/codeforge/`
- **GitHub repo 이동**: `mctrader/mctrader` → `mctrader/plugin-codeforge` (GitHub 자동 URL redirect 30일 유지)

### 영향받는 consumer 파일

- `.claude/settings.json` — SessionStart hook 커맨드의 경로

### 마이그레이션 절차

#### 1. Plugin 재설치 (marketplace 사용 시)

```bash
/plugins uninstall dev-orchestrator
/plugins install codeforge@<marketplace>
```

로컬 개발용 plugin (directory-based install) 은 재설치 불필요 — 플러그인 디렉토리가 `codeforge`로 바뀌었는지만 확인.

#### 2. `.claude/settings.json` hook 경로 수정

**Before**:
```json
{
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

**After**:
```json
{
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

#### 3. Preset 임포트 경로 (사용 중이면)

**Before**:
```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

**After**:
```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

#### 4. project.yaml skeleton 복사 경로 (신규 설치 시)

**Before**:
```bash
cp ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

**After**:
```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

#### 5. 검증

```bash
claude
# SessionStart hook이 새 경로로 정상 작동, .claude/agents/*.md 생성 확인
ls .claude/agents/ | wc -l
```

### 체크리스트

- [ ] `.claude/settings.json` hook 커맨드에 `dev-orchestrator` 잔존 없음 (grep 확인)
- [ ] Plugin 재설치 완료 (해당 시)
- [ ] 세션 개시 후 `.claude/agents/` 정상 생성
- [ ] consumer repo README·doc에 plugin 이름 참조 있다면 일괄 교체

### 참고

- `CHANGELOG.md` v0.6.0 엔트리
- Repo 새 주소: https://github.com/mctrader/plugin-codeforge (30일간 `mctrader/mctrader` 자동 redirect)

---

## v0.3 → v0.4 (Stage 2 `project.yaml` 구조화)

### Breaking changes

- **Atlassian·GitHub·labels 상수 위치 변경**: `.claude/_overlay/CLAUDE.md` 에 free text로 작성하던 SSOT 상수가 `.claude/_overlay/project.yaml`로 이동.
- **에이전트 동작 변경**: DocsAgent·DomainAgent·RequirementsPLAgent·PMOAgent가 Atlassian 호출 전 `project.yaml`을 `Read`하는 것이 의무. 파일이 없거나 필수 필드 누락 시 Orchestrator 경유 사용자 에스컬레이션.

### 영향받는 consumer 파일

- `.claude/_overlay/CLAUDE.md` — SSOT 상수 섹션 제거 필요
- `.claude/_overlay/project.yaml` — **신규 작성 필수**

### 마이그레이션 절차

#### 1. `project.yaml` 신설

```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

#### 2. 기존 CLAUDE.md overlay에서 상수 값 이동

**Before** (`.claude/_overlay/CLAUDE.md` 일부):
```markdown
## SSOT 상수

- Confluence space: `TM` (spaceId=12345)
- Story parent pageId: 23456
- Story template pageId: 34567
- Jira project key: `TM`
- Atlassian host: `https://acme.atlassian.net`

## Domain Knowledge

- Domain Knowledge 루트 pageId: 45678
- ADR 루트 pageId: 56789
```

**After** (`.claude/_overlay/project.yaml`):
```yaml
project:
  name: task-manager
  repo: github.com/acme/task-manager

atlassian:
  site: acme.atlassian.net
  confluence:
    space_key: TM
    stories_parent_page_id: 23456
    domain_knowledge_parent_page_id: 45678
    adr_root_page_id: 56789
  jira:
    project_key: TM

github:
  pr_title_prefix_template: "[{project_key}-{story_number}] {title}"

labels:
  components:
    - api
    - ui
    - data
    - infra
```

**After** (`.claude/_overlay/CLAUDE.md` — narrative만 유지):
```markdown
## Project

`task-manager` — 팀 단위 할 일 관리 웹 애플리케이션. Python + FastAPI 기반.

SSOT 상수는 `.claude/_overlay/project.yaml` 참조.

## Domain

할 일(Task) 관리와 팀 협업. Task status lifecycle·팀 권한 모델이 핵심.

## 기술 스택 (선택 근거)

- 언어 Python 3.12: 기존 팀 역량·생태계
- 프레임워크 FastAPI: async 지원·OpenAPI 자동 생성
- DB PostgreSQL: ACID·RLS 지원

## 경로 관습

- `src/api/**` — REST 라우트
- `src/domain/**` — 도메인 로직
- `src/adapters/**` — 외부 시스템 어댑터
```

#### 3. 검증

```bash
# project.yaml 파싱 확인
python3 -c "import yaml; yaml.safe_load(open('.claude/_overlay/project.yaml'))"

# 세션 개시 → SessionStart hook이 .claude/agents/ 재생성
claude

# DocsAgent overlay 본문 확인 — project.yaml 참조 문구 포함
cat .claude/agents/DocsAgent.md | grep -A1 "project.yaml"
```

#### 4. 체크리스트

- [ ] `.claude/_overlay/project.yaml` 존재 + 필수 필드 채움 (project·atlassian·github)
- [ ] `.claude/_overlay/CLAUDE.md`에서 SSOT 상수 섹션 제거 (혹은 "project.yaml 참조" 명시)
- [ ] 기존 `component:*` 라벨 값이 `project.yaml`의 `labels.components`와 일치
- [ ] `cat .claude/_overlay/project.yaml` 결과를 팀과 공유·검증 (pageId·key 오타 방지)

### 참고

- Schema SSOT: [`project-config-schema.md`](project-config-schema.md)
- Consumer 가이드: [`consumer-guide.md`](consumer-guide.md) §3a

---

## v0.2 → v0.3 (Generic Dev roster + preset)

### Breaking changes

- **Core 에이전트 이름·위치 변경**:
  - `BackendDeveloperAgent`·`FrontendDeveloperAgent` → `presets/webapp/agents/`로 이동 (core에서 제거)
  - `ServerEngineerAgent` → `InfraEngineerAgent`로 **리네임**
  - 신규 core agent: `DeveloperAgent` (generic)
- **DevPL roster 동작 변경**: 하드코딩된 "4 Dev" → `role: dev` frontmatter 태그로 **동적 discovery**. consumer가 추가 Dev 에이전트를 overlay로 정의 가능.
- **`merge.py` 동작 변경**: "core 없음 + overlay 있음" 케이스가 이전엔 abort였으나 이제 **overlay-only 렌더** (`--overlay-only` 모드). preset 임포트·consumer-defined agent 지원.

### 영향받는 consumer 파일

- `.claude/_overlay/agents/ServerEngineerAgent.md` → `InfraEngineerAgent.md`로 rename (있다면)
- `.claude/_overlay/agents/BackendDeveloperAgent.md`, `FrontendDeveloperAgent.md` → core 제거로 인해 preset에서 복사해야 정상 작동 (웹앱 프로젝트 한정)
- `.claude/_overlay/CLAUDE.md` — Dev roster 구성 설명이 있으면 업데이트

### 마이그레이션 절차

#### A. 웹앱 프로젝트 (preset/webapp 사용)

1. **preset 복사**
   ```bash
   cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
         .claude/_overlay/agents/
   ```
   (기존 overlay 본문이 있으면 수동 병합)

2. **ServerEngineer → InfraEngineer 리네임** (overlay가 있었다면)
   ```bash
   git mv .claude/_overlay/agents/ServerEngineerAgent.md \
          .claude/_overlay/agents/InfraEngineerAgent.md
   # 파일 내부 frontmatter name: 필드도 "InfraEngineerAgent"로 수정 (선택 — overlay에 name 없으면 불필요)
   ```

3. **Generic `DeveloperAgent` 충돌 방지**
   Backend+Frontend가 `src/**`를 충분히 커버하므로 generic DeveloperAgent는 중복. CLAUDE.md overlay에 다음 명시:
   ```markdown
   > 이 프로젝트는 webapp preset(Backend+Frontend)을 쓰므로 core의 generic `DeveloperAgent`는 비활성화.
   ```
   또는 `.claude/_overlay/agents/DeveloperAgent.md` overlay로 permissions를 제한 (`deny` 경로로 preset 영역 제외).

4. **세션 개시 → 결과 확인**
   ```bash
   claude
   ls .claude/agents/ | grep -E "Backend|Frontend|Infra"
   # BackendDeveloperAgent.md, FrontendDeveloperAgent.md, InfraEngineerAgent.md 존재
   ```

#### B. 비웹앱 프로젝트 (CLI 툴·라이브러리·임베디드 등)

1. **Backend/Frontend overlay 제거** (있었다면)
   ```bash
   rm -f .claude/_overlay/agents/BackendDeveloperAgent.md
   rm -f .claude/_overlay/agents/FrontendDeveloperAgent.md
   ```

2. **ServerEng → Infra 리네임** (A와 동일)

3. **Generic DeveloperAgent 활용**
   core의 `DeveloperAgent`가 자동으로 roster에 포함됨. 경로 scoping이 필요하면 overlay 작성:
   ```markdown
   ---
   permissions:
     allow:
       - Edit(src/cli/**)
       - Write(src/cli/**)
       - Edit(src/core/**)
       - Write(src/core/**)
   ---

   ### 기술 스택
   - 언어: Go 1.22
   - CLI 프레임워크: cobra
   ```

4. **추가 Dev 에이전트 정의 (선택)**
   프로젝트에 `ParserDev`·`FirmwareDev` 같은 특화 역할이 필요하면 `role: dev` 태그로 overlay-only agent 작성:
   ```markdown
   ---
   name: FirmwareDeveloperAgent
   role: dev
   description: 임베디드 펌웨어 구현 — MCU·드라이버·실시간 제약
   permissions:
     allow:
       - Edit(firmware/**)
       - Write(firmware/**)
   ---

   ### 담당
   STM32 HAL·FreeRTOS 태스크·인터럽트 핸들러
   ```

#### 체크리스트

- [ ] `ls .claude/_overlay/agents/`에 `ServerEngineerAgent.md` 없음
- [ ] 웹앱: Backend/Frontend preset 복사됨 + role: dev 태그 존재
- [ ] 비웹앱: generic `DeveloperAgent` overlay로 경로 scoping (필요 시)
- [ ] 세션 개시 후 `.claude/agents/`에 예상 roster만 존재 (불필요한 preset agent 없음)

---

## v0.1 → v0.2 (보안 테스트 레인 + templates)

### Non-breaking

v0.2는 consumer overlay에 영향 없음. Core만 확장:
- 신규 core agent 3종: `SecurityTestPLAgent`, `ClaudeSecurityTestAgent`, `CodexSecurityTestAgent`
- 신규 `templates/` 디렉토리: `change-plan.md`, `adr.md`, `story-page-structure.md`, `impl-manifest.md`
- 기존 "테스트" 레인 → "구현 테스트" + "보안 테스트" 2단계로 분리

### 선택적 작업

보안 테스트 레인이 consumer 프로젝트 특화 기준을 요구하면:
- `.claude/_overlay/agents/ClaudeSecurityTestAgent.md`, `CodexSecurityTestAgent.md` 신설 — 프로젝트 특화 보안 체크포인트 추가
- 예: "이 프로젝트는 결제 PG 연동 있음 → PCI DSS 범위 체크 추가"

### 체크리스트

- [ ] Jira 대시보드 JQL이 `phase:보안-테스트` 라벨을 조회하도록 갱신 (기존 `phase:테스트`만 쓰던 경우)
- [ ] 보안 테스트 P0/P1 FIX 무제한임을 팀에 공유 (기존 "테스트 FIX 무제한" 정책 동일)

---

## 일반 원칙

### 버전업 전 확인

1. `CHANGELOG` 또는 [`README.md`](../README.md) 연혁 섹션에서 target version의 breaking change 확인
2. `archive/` 태그 존재 여부 (주요 pivot 시 보존) — rollback 경로
3. 본 가이드의 해당 섹션 수행

### 버전업 후 검증

1. 세션 개시 → SessionStart hook 성공 (`regenerated N core + M overlay-only agents` 메시지)
2. `.claude/agents/`의 에이전트 수·이름이 기대대로
3. Dry-run 1건: 간단한 Story 요건 → 설계 → 구현 1~2 단계 실행해서 Orchestrator가 정상 roster를 discover하는지 관찰

### 문제 발생 시

- 플러그인 repo의 해당 버전 PR·이슈 확인
- consumer CLAUDE.md overlay에 `project.yaml` 참조가 누락됐거나 이름 오타가 있는지 grep
- `git log --oneline <archive-tag>..HEAD` 로 변경 범위 파악 후 부분 rollback

## 관련 문서

- [`consumer-guide.md`](consumer-guide.md) — 신규 consumer 설치 가이드
- [`project-config-schema.md`](project-config-schema.md) — `project.yaml` schema SSOT
- [`plugin-design.md`](plugin-design.md) — core/overlay 경계 원칙
- [`../README.md`](../README.md) — 버전 연혁
