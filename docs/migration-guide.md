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

- [v0.8 → v0.9](#v08--v09-reviewtest-워커-통합) — **3 lane × 2 vendor = 6 워커 → 2 워커 (BREAKING)**
- [v0.7 → v0.8](#v07--v08-atlassian-제거--github-전환) — **Atlassian 제거 + GitHub 전환 (BREAKING)**
- [v0.6 → v0.7](#v06--v07-요구사항설계-레인-병렬화) — 요구사항·설계 레인 병렬 모델
- [v0.5 → v0.6](#v05--v06-plugin-name-rename-dev-orchestrator--codeforge) — Plugin name rename + Atlassian 이관
- [v0.3 → v0.4](#v03--v04-stage-2-projectyaml-구조화) — `project.yaml` 도입
- [v0.2 → v0.3](#v02--v03-generic-dev-roster--preset) — Generic Dev roster + preset
- [v0.1 → v0.2](#v01--v02-보안-테스트-레인--templates) — 보안 테스트 레인 + templates (non-breaking)

---

## v0.8 → v0.9 (Review/Test 워커 통합)

### Breaking changes

[ADR-001](adr/ADR-001-review-agent-unification.md) 결정에 따라 **3 lane × 2 vendor = 6 워커**(Claude{Design,Code,SecurityTest}ReviewAgent + Codex 동등 6종)를 **2 lane-agnostic 워커**(`ClaudeReviewAgent`, `CodexReviewAgent`)로 통합. lane-specific 도메인(체크리스트·스코프·category enum·severity 자동 룰)은 호출 PL이 `review_packet`으로 주입.

- 24 core agents → **20 core agents** (워커 6 삭제 + 워커 2 신규)
- Codex 플러그인이 단일 의존성으로 격상 — 미설치 시 3 리뷰 lane 전부 진입 불가
- SecurityTestPL이 `Bash(gh api repos/*)` 권한 사용 — 1차 layer (Dependabot/CodeQL/Secret Scanning/Push Protection) 결과를 packet에 inline 첨부

### Affected files (consumer overlay 측)

| 파일 | 액션 |
|------|------|
| `.claude/_overlay/agents/ClaudeDesignReviewAgent.md` (있다면) | **제거** — `agents/ClaudeReviewAgent.md` (core)로 통합 |
| `.claude/_overlay/agents/Codex{Design,Code,SecurityTest}ReviewAgent.md` (있다면) | **제거** — `agents/CodexReviewAgent.md` (core)로 통합 |
| `.claude/_overlay/templates/review-checklists/<lane>.md` (선택) | **신규 가능** — 언어·프레임워크 특화 체크 항목 추가 (Python·Go·React 등) |
| `.claude/_overlay/CLAUDE.md` 내 워커 인용 | "Claude/Codex<Domain>ReviewAgent" 패턴이 있다면 "ClaudeReviewAgent / CodexReviewAgent" lane-agnostic 참조로 갱신 |

### Migration 절차 (consumer)

1. **Codex 플러그인 인증 확인**: 3 리뷰 lane 전부 진입 불가가 되므로 `codex@openai-codex` 플러그인 미설치 시 즉시 설치
2. **6 워커 오버라이드 제거**: `.claude/_overlay/agents/`에 `Claude{Design,Code,SecurityTest}ReviewAgent.md` 또는 Codex 동등 파일이 있다면 제거. 도메인 특화 체크는 lane checklist (`templates/review-checklists/<lane>.md`)로 이동
3. **GitHub 토큰 권한 확인**: SecurityTestPL이 `gh api repos/*/dependabot/alerts` 등을 호출하므로 Dependabot/CodeQL/Secret Scanning alerts read 권한 필요
4. **첫 리뷰 lane 실행 시 검증**: PL이 `review_packet` 필수 필드(lane / checklist_path / scope_globs / category_enum / story_key, security 추가 시 first_layer_findings) 누락 시 워커가 `ESCALATE_PACKET_INCOMPLETE` 반환 — generic fallback 없음
5. **CHANGELOG·코멘트의 historical 인용 유지**: 과거 `Codex<Domain>ReviewAgent` 명칭은 historical로 보존 (변경 금지)

### Backward compatibility

- 라벨·워크플로우·phase 전이 invariant **무변경**: `phase:설계-리뷰` / `phase:구현-리뷰` / `phase:보안-테스트` / `gate:design-review-pass` / `gate:security-test-pass` / `fix:<레인>-retry` 라벨, `phase-gate-mergeable.yml`·`fix-ledger-sync.yml` Action 동작 유지
- `docs/stories/<KEY>.md` 섹션 구조(§1-11) **무변경**

기존 v0.8 활성 Story가 있다면, 다음 리뷰 iteration부터 자연스럽게 새 워커가 packet 수령. Phase 2 PR 진행 중 Story는 즉시 영향 없음.

---

## v0.7 → v0.8 (Atlassian 제거 + GitHub 전환)

### Breaking changes

이 release는 Atlassian backend (Confluence/Jira)를 완전 제거한다. v0.7 이하 consumer는 in-place 업그레이드 불가 — fresh GitHub-based setup 필요.

- **MCP 의존**: `atlassian` (HTTP) → **`github`**
- **필수 플러그인**: `github@claude-plugins-official` 권장에서 격상, `atlassian@claude-plugins-official` 제거
- **필수 CLI**: `gh` 추가 (Milestone·Discussions·기타 GraphQL fallback)
- **워크플로우 모델**:
  - Story 페이지 (Confluence) → `docs/stories/<KEY>.md` (single-file SSOT, §1-11)
  - ADR (Confluence pages) → `docs/adr/ADR-NNN-<slug>.md` (flat, frontmatter `category:`)
  - Domain Knowledge (Confluence tree) → `docs/domain-knowledge/<area>/<topic>.md` (계층)
  - Jira workflow → GitHub Issue + `phase:*` labels + GitHub Actions
  - Jira sub-task → GitHub Sub-issue (subissue-from-impl-manifest.yml Action 자동 생성)
  - Jira Epic → GitHub Milestone + Epic Issue
- **PR 모델**: 1 Story = **2 PRs** (Phase 1 docs / Phase 2 code+docs append)
- **§1 변조 금지 invariant**: `story-section-1-immutable.yml` Action이 강제
- **Phase 라벨 single-active**: `phase-label-invariant.yml` Action이 강제
- **보안 테스트 1차 layer**: GitHub native (Dependabot / CodeQL / Secret Scanning / Push Protection)

### project.yaml 스키마

`atlassian.*` 키 모두 삭제 → `github.*` 키 신설.

```yaml
# OLD (v0.7)
atlassian:
  site: ...
  confluence:
    space_key: ...
    stories_parent_page_id: ...
    domain_knowledge_parent_page_id: ...
    adr_root_page_id: ...
  jira:
    project_key: ...

github:
  pr_title_prefix_template: "[{project_key}-{story_number}] {title}"

# NEW (v0.8)
github:
  org: ...
  repo: ...
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: ...                   # e.g. "TM"
  codeowners:
    architect_team: "@org/architects"
    domain_expert_team: "@org/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
```

자세한 형식은 [project-config-schema.md](project-config-schema.md) 참조.

### Consumer 절차 (fresh setup)

기존 v0.7 consumer가 0건이므로 자동 마이그레이션 도구·자동 변환은 제공하지 않는다. 신규 또는 v0.7에서 v0.8로 이전하는 consumer는 [consumer-guide.md](consumer-guide.md) 셋업 절차를 따른다:

1. `.github/workflows/` 6개 plugin 워크플로우 복사
2. `.github/ISSUE_TEMPLATE/` 3 Forms + `config.yml` (blank issue 비활성화) 복사
3. `.github/PULL_REQUEST_TEMPLATE.md` 복사
4. `.github/CODEOWNERS` 복사 + team placeholder 치환
5. `.claude/_overlay/project.yaml` 새 schema로 재작성
6. GitHub Labels 일괄 생성 (gh label create ...)
7. Branch protection 설정 (main 브랜치, required status check `phase-gate-mergeable`)
8. Dependabot / CodeQL / Secret Scanning / Push Protection 활성화

### 영향 범위

- consumer 리포의 `.github/`·`.claude/_overlay/project.yaml`·`docs/` 디렉토리 모두 영향
- 기존 Confluence 페이지·Jira issue는 별도 export 후 `docs/` 마크다운으로 수동 이전 권장 (자동 도구 미제공)
- 기존 활성 Story (Atlassian상)가 있다면 v0.8에서 새 Story로 다시 시작하는 게 가장 단순

### 참고

- 설계 spec: `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md`
- 구현 plan: `docs/superpowers/plans/2026-04-25-atlassian-to-github-migration.md`

---

## v0.6 → v0.7 (요구사항·설계 레인 병렬화)

### Breaking changes (오케스트레이션 semantics)

- **요구사항 레인**: `DomainAgent → Analyst → Researcher` 순차 (조건부 생략 포함) → **`DomainAgent ∥ Analyst ∥ Researcher` 병렬** (셋 다 non-skippable)
- **설계 레인**: `CodebaseMapper → Refactor` 순차 (Refactor가 Mapper 요약 입력 수신) → **`CodebaseMapper ∥ Refactor` 병렬** (둘 다 원 소스 직접 독해, 산출물 교차 참조 없음)
- **Clarification 재스폰 프로토콜**: PL↔서브 continuous dialog가 불가하므로, PL이 통합 중 추가 질의가 필요하면 Orchestrator 경유 재스폰 요청 (이전 출력 pointer + clarification context + 범위 제한). 동일 에이전트 2회 재스폰 이후 미해소면 사용자 ESCALATE
- **Researcher·DomainAgent non-skippable 승격**: 이전엔 조건부 생략 가능이었으나, 이제 "조사 불필요" 판정도 명시 반환 필수 (null skip 금지)

### 영향 범위

- **Consumer overlay가 RequirementsPLAgent 또는 ArchitectAgent 행동을 override하지 않는다면 영향 없음** — core agent 이름·경로·Story 페이지 섹션 규격 모두 동일
- Override 중인 consumer만 아래 절차 필요

### 마이그레이션 절차 (override 중인 consumer만)

#### 1. RequirementsPLAgent override 수정

overlay에 "DomainAgent → Analyst → Researcher 순서로 스폰" 류 지시가 있으면:

**Before**:
```markdown
1. DomainAgent 스폰 → 지식 공백 수령
2. Analyst 스폰 (DomainAgent 지식 공백 payload 포함)
3. Analyst 산출물의 Researcher 키워드 존재 시 Researcher 스폰
```

**After**:
```markdown
1. 공통 입력 패키지 준비 (사용자 원문 + Story §1-2 + 관련 ADR + Project Config Packet)
2. DomainAgent · Analyst · Researcher **병렬 스폰** (공통 입력만 전달, 타 에이전트 산출물 미포함)
3. 세 결과 병렬 수령 → dedup · 상충 조정
4. Clarification 필요 시 Orchestrator 경유 재스폰
```

#### 2. ArchitectAgent override 수정

"Mapper → Refactor 순 스폰" 류 지시가 있으면:

**Before**:
```markdown
1. CodebaseMapper 스폰 → as-is 산출물 수령
2. Refactor 스폰 (Mapper 산출물 입력)
```

**After**:
```markdown
1. 공통 입력 패키지 준비 (변경 대상 코드 경로 + 관련 ADR + Change Plan 초안 + Story §1-7)
2. CodebaseMapper · Refactor **병렬 스폰** (둘 다 원 소스 직접 독해, 상호 산출물 미전달)
3. 두 결과 병렬 수령 → 교차 검토 → Change Plan §2·§3에 각각 반영
4. Clarification 필요 시 Orchestrator 경유 재스폰
```

#### 3. Story 페이지 §6 null 결과 규정 확인

Consumer overlay가 `templates/story-page-structure.md` §6을 override하면 "Researcher 키워드 비어있으면 섹션 생략" 서술이 있는지 점검, "외부 지식 보강 불필요 사유 명시" 로 변경.

### 검증 체크리스트

- [ ] overlay의 RequirementsPLAgent/ArchitectAgent에서 "순차"·"→" 표기 제거
- [ ] Researcher·DomainAgent를 "조건부 생략 가능"으로 표기한 overlay 있으면 제거
- [ ] 세션 1회 수행 후 Story 페이지 §10 FIX Ledger에 clarification 재스폰 이력이 적절히 기록되는지 확인

---

## v0.5 → v0.6 (Plugin name rename `dev-orchestrator` → `codeforge`)

### Breaking changes

- **Plugin name 변경**: `dev-orchestrator` → `codeforge`
- **Marketplace install URL 변경** (해당 시): `/plugins install dev-orchestrator@<marketplace>` → `/plugins install codeforge@<marketplace>`
- **`CLAUDE_PLUGIN_ROOT` 하위 경로 변경**: `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/` → `${CLAUDE_PLUGIN_ROOT}/codeforge/`
- **GitHub repo 이동**: `mctrader/plugin-codeforge` → `mctrader/plugin-codeforge` (GitHub 자동 URL redirect 30일 유지)

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
- Repo 새 주소: https://github.com/mctrader/plugin-codeforge (30일간 `mctrader/plugin-codeforge` 자동 redirect)

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
