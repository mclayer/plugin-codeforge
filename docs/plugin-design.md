---
title: Plugin Design — core/overlay 분리 원칙 및 merge 계약
status: active
created: 2026-04-24
updated: 2026-04-24
---

# Plugin Design Spec

이 문서는 `codeforge` 플러그인의 구조·경계·overlay 메커니즘 설계 SSOT.

## 1. 목표

- **Generic SW 개발 오케스트레이션 플러그인** — 0 core 에이전트 (wrapper-only) + 8 lane plugin (codeforge-{requirements,design,review,develop,test,deploy,deploy-review,pmo}) 의 agent 가 자기 owner path 분산 보유 + `role: dev` 동적 roster · 8 레인 · FIX 루프 구조를 consumer 프로젝트 전반에 재사용
- **Core/Overlay/Preset 경계 유지** — core는 프로젝트 shape 중립, 프로젝트 고유 내용(도메인·SSOT 상수·기술 스택)은 consumer overlay에 격리, 자주 쓰이는 Dev 구성 번들은 preset으로 제공
- **깔끔한 추출** — 신규 consumer 프로젝트 가동 시 plugin을 설치하고 `.claude/_overlay/`만 작성하면 즉시 사용 가능 (필요 시 preset 복사)
- **overlay 일급 시민** — overlay는 죽은 스테이징이 아닌, consumer 프로젝트가 적극적으로 편집·사용하는 활성 계층
- **프로젝트 shape 중립** — core는 웹앱 가정 없이 generic Dev 역할로 구성, shape별 편향은 preset으로 분리

## 2. 분리 경계 (Option B 완화)

설계 결정: [Option B](#옵션-탐색-이력) — **agent의 역할·권한·오케스트레이션은 core, 프로젝트별 바뀌는 지침 섹션은 overlay**.

### 2a. Core로 가는 것

- 어떤 프로젝트든 성립하는 SW 프로세스 규칙 (Orchestrator 생명주기, FIX 루프, Review severity 종합)
- 추상 구조·관계 (0 core + 8 lane plugin org chart — 각 plugin 의 agent listing 은 해당 plugin repo 참조, 8 레인, PL/sub 계층, `role: dev` 동적 roster 디스커버리)
- 권한·책임 분리의 원칙 (path scope, single writer, Architect stateless 재스폰 등)
- 에이전트별 기본 행동 방식 (DomainAgent의 4-source fetch 프로세스, DesignReviewPL의 dedup 규칙)

### 2b. Overlay로 가는 것

- 프로젝트 고유명사 (프로젝트명·도메인 용어·SSOT 상수)
- SSOT 상수 (GitHub org/repo, story_key_prefix, CODEOWNERS team, Discussions 카테고리, Milestone naming)
- 기술 스택 선택 (언어·프레임워크·라이브러리)
- 도메인 경로 (`src/<project>/**`, `storage/**`, `adapters/<domain-sources>/**` 등 프로젝트 구조)
- 도메인 용어 사전
- 프로젝트별 labels (`component:*` 구체값 등)

### 2c. 분류 원칙 (판단이 애매할 때)

**이 지침을 플러그인 repo에 남기면 다른 프로젝트에서도 말이 되는가?**

- YES → core
- NO → overlay

## 3. 메커니즘 (Option β — 파일 분리 + hook concat)

### 3a. 파일 구조

```
plugin repo:                          consumer project:
  agents/                               .claude/_overlay/
    ArchitectAgent.md  (core)             agents/
    ...                                     DataEngineerAgent.md  (overlay)
                                            ...
  hooks/  (consumer-side tooling)         CLAUDE.md  (overlay, 선택)
    regen-agents.sh
    merge.py                            .claude/agents/  (GENERATED)
  CLAUDE.md  (core)                       ArchitectAgent.md  (= core + overlay)
                                          DataEngineerAgent.md  (= core + overlay)
  .claude-plugin/plugin.json              ...

                                        CLAUDE.md  (GENERATED = core + overlay)
```

### 3b. SessionStart hook flow

```
Claude Code session start
  → .claude/settings.json의 SessionStart hook 실행
    → ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh
      → for each agent in plugin's agents/:
          python3 merge.py <core> <overlay?> > .claude/agents/<Name>.md
      → if consumer has .claude/_overlay/CLAUDE.md:
          python3 merge.py <plugin CLAUDE.md> <overlay> > CLAUDE.md
  → Claude Code가 .claude/agents/ 및 CLAUDE.md를 로드 (이미 최신 상태)
```

## 4. Merge 계약

### 4a. Body append

```
<core body>

---

## Project Overlay

<overlay body>
```

- overlay가 없거나 body가 비어있으면 구분선·헤더·overlay 블록 **전부 생략**
- 구분선과 헤더는 hook이 자동 주입 (overlay 파일에는 본문만 쓰면 됨)
- overlay가 core의 특정 섹션을 "덮어쓰려면" 명시적으로 "위 core §X는 이 프로젝트에서 Y로 대체"라고 서술 (파서는 단순 append)

### 4b. Frontmatter deep merge

| 필드 유형 | 예시 | 병합 규칙 |
|-----------|------|-----------|
| 스칼라 식별·정체성 | `name`, `description`, `model`, `color` | **core-wins**. overlay가 다른 값 → **abort** (agent identity drift 방지) |
| 배열 (권한·툴) | `tools: [Read, "Write(src/**)", Bash]` | **concat + dedup** (core 먼저, overlay 뒤, 문자열 매칭 dedup) |
| 맵 (permissions 등) | `permissions: {allow: [...], deny: [...]}` | 재귀 적용 (맵 내부 배열은 concat+dedup) |
| 기타 스칼라 | (사용 예 없음) | core-wins silently |

#### 스칼라 core-wins abort 정책

overlay가 `name: BackendDeveloperAgent`처럼 core와 동일 값을 명시하는 건 OK. 하지만 `name: MyBackendDev`처럼 다른 값 주면 **hook abort**.

이유: agent identity의 유일성 보장. overlay가 agent 정체성을 바꾸려 하면 그건 "신규 에이전트 추가"로 설계되어야지 overlay가 아님.

### 4c. Auto-injected header

모든 generated md 최상단 (frontmatter 다음):

```markdown
<!--
  GENERATED FROM <core path> + <overlay path or "(none)">
  DO NOT EDIT DIRECTLY. Edit source files and let SessionStart hook regenerate.
  Last regenerated: <ISO 8601 UTC>
-->
```

Claude Code agent 파서는 frontmatter 기준으로 인식 — 본문 상단 HTML 주석은 무시.

### 4d. 파일 없음 케이스

| core | overlay | 동작 |
|------|---------|------|
| 있음 | 없음 | core만 복사 + 헤더 주입 (overlay 블록 없음) |
| 있음 | 있음 | deep merge + append |
| 없음 | 있음 | **overlay-only 렌더** — `merge.py --overlay-only` 경로. frontmatter + auto-header + body만 출력 (separator·Project Overlay 헤더 없음). preset 임포트·consumer-defined agent 지원 |
| 없음 | 없음 | skip |

**v0.3.0 이전**은 "없음+있음" 케이스를 에러로 차단했으나, preset/generic Dev roster 도입과 함께 overlay-only 렌더로 변경됨.

### 4e. Idempotency

hook은 idempotent. 같은 입력 → 같은 출력. 매 세션 시작 시 전부 regen (staleness 차단).
`Last regenerated` 타임스탬프 때문에 git diff는 매번 생기므로 **generated files는 gitignore 권장** (consumer 측 `.gitignore`에 `.claude/agents/`, `CLAUDE.md` 추가).

## 5. 범위 (Stage 1 / Stage 2)

### Stage 1 — 현재 범위

- `agents/*.md` — ζ arc (CFP-31~CFP-40) 완료로 **0개** (wrapper-only). 역사: v0.9 review 워커 6 → 2 통합, v0.11-v0.14 설계 SubAgent 5인 구조 완성, v0.15 owner doc direct write 이관 (CFP-26), v0.17 review 추출 → codeforge-review (CFP-29), v2.0 requirements 추출 → codeforge-requirements (CFP-37), v3.0 test 추출 → codeforge-test (CFP-38), v4.0 develop 추출 → codeforge-develop (CFP-39), v5.0 design 추출 → codeforge-design + DocsAgent final delete (CFP-40). 현재 agent md 는 각 8 lane plugin repo 가 SSOT
- `presets/<shape>/agents/*.md` — 프로젝트 shape별 Dev 번들 (webapp 등)
- `templates/*.md` — 공통 문서 양식 SSOT (change-plan · adr · story-page-structure · impl-manifest · domain-knowledge · retro)
- `CLAUDE.md` — core 오케스트레이션 규칙 (8 레인 구조)
- `docs/orchestrator-playbook.md` — Orchestrator 행동 SSOT (현재는 core 단일본, overlay 대상 아님)
- `docs/project-config-schema.md` + `overlay/_overlay/project.yaml.example` — consumer `project.yaml` schema SSOT + 스켈레톤
- `overlay/hooks/merge.py` + `regen-agents.sh` — consumer tooling (core+overlay merge 및 overlay-only 렌더)
- `overlay/_overlay/README.md` — consumer 복사용 skeleton
- `.claude-plugin/plugin.json` — plugin manifest
- `docs/consumer-guide.md` + `docs/plugin-design.md`

### Stage 2 — 후속 (일부 완료)

- ✅ `.claude/_overlay/project.yaml` — SSOT 상수를 구조화 주입 (v0.4.0 도입)
- 기술 스택 objective 항목 일부 추가 이전 (test runner·perf baseline 경로 등)
- project.yaml JSON Schema 검증 + SessionStart hook 연동
- Context Packet 자동 주입 (Orchestrator가 project.yaml 요약을 sub-agent 프롬프트에 자동 삽입)
- Playbook 일부 섹션의 overlay 지원 (예: 토큰 예산 프로젝트별 조정)
- 추가 에이전트 (Observability 등 논의됨 — 미확정)

## 6. 분류 가이드 (0 core (wrapper-only) + 8 lane plugin agent + preset)

현재 버전에서 각 에이전트의 core 비중 · overlay 예상 내용:

### Group A (Overlay 거의 없음 · core 100%)

**ArchitectPLAgent** (설계 lane PL · 6-deputy 오케스트레이터) · **ArchitectAgent** (chief author · Change Plan 집필) · CodebaseMapperAgent · RefactorAgent · **SecurityArchitectAgent** (threat model · trust boundary 설계) · **TestContractArchitectAgent** (§8 Test Contract QA perspective contributor) · **ModuleArchitectAgent** (aggregate-level — RDB OLTP 무결성 advocate · §11 author input · 구 DataMigrationArchitectAgent + AggregateArchitectAgent, CFP-1086/CFP-1126 통합) · DeveloperPLAgent · RequirementsPLAgent · RequirementsAnalystAgent · ResearcherAgent

**[codeforge-review plugin] (별도 — CFP-29 Phase 1 추출)**: DesignReviewPLAgent · CodeReviewPLAgent · SecurityTestPLAgent · ClaudeReviewAgent · CodexReviewAgent (워커 통합 후 lane-agnostic 2종 — [ADR-001](../archive/adr/ADR-001-review-agent-unification.md))

### Group B (Overlay 가벼움 · 경로·상수·용어)

DeveloperAgent · InfraEngineerAgent · QADeveloperAgent · TestAgent (러너 커맨드)

### Group C (Overlay 무거움 · 도메인 지식·워크플로우 특화)

*(현재 wrapper 에 agent 0개. SSOT 상수 참조 책임은 각 lane plugin agent 가 보유 — codeforge-requirements: DomainAgent, codeforge-develop: DataEngineerAgent·InfraEngineerAgent, codeforge-pmo: PMOAgent)*

### Preset (프로젝트 shape별 Dev 번들)

- **webapp** (`presets/webapp/agents/`): BackendDeveloperAgent · FrontendDeveloperAgent — 웹앱 프로젝트용. Consumer가 수동 복사 후 `role: dev` 태그로 DevPL roster에 자동 편입
- 추가 preset(cli-tool, library, embedded 등)은 실수요 기반으로 확장

## 7. 옵션 탐색 이력

### 분리 경계

| 옵션 | 내용 | 판정 |
|------|------|------|
| A 엄격 | agent는 전부 core, 상수만 overlay | ❌ 부족 — agent 본문의 "Jinja2+Bootstrap5 사용" 같은 지침도 overlay 대상 |
| **B 완화** | **agent 역할·권한 core, 프로젝트별 지침 섹션 overlay** | ✅ 채택 |
| C 과감 | B + 일부 agent 통째 overlay (DomainAgent 등) | ❌ 분리선 과다, pilot 부담 |

### 표현 메커니즘

| 옵션 | 내용 | 판정 |
|------|------|------|
| α In-file 섹션 | agent md 안에 `## Core` / `## Project Overlay` 마커 | ❌ 텍스트 마커 drift 위험 |
| **β 파일 분리 + hook concat** | `_core/` + `_overlay/` + SessionStart hook 병합 | ✅ 채택 (파일시스템 수준 경계) |
| γ CLAUDE.md + 환경 주입 | agent md는 flat core, overlay는 별도 경로 주입 | ❌ Option B "지침 섹션 overlay" 만족 못함 |

### 결합 방식

- **Body**: 단순 append (overlay tail). 매직 없음
- **Frontmatter**: deep merge (배열 concat+dedup, 스칼라 core-wins with abort on mismatch)

## 8. 향후 작업

- Stage 2 범위 (structured config, playbook overlay)
- Plugin 배포 — marketplace 등록
- overlay 검증 도구 (overlay가 core를 override하려 할 때 경고 CLI)
- Multi-language TestAgent 어댑터 (pytest·vitest·go test 등 runner 자동 감지)

## 9. 참조

- [`../CLAUDE.md`](../CLAUDE.md) — 플러그인 오케스트레이션 규칙 SSOT
- [`orchestrator-playbook.md`](orchestrator-playbook.md) — Orchestrator 행동 SSOT
- [`consumer-guide.md`](consumer-guide.md) — consumer 프로젝트 사용 가이드
- [`../templates/`](../templates/) — 공통 문서 양식 SSOT (change-plan · adr · story-page-structure · impl-manifest)
- [`../overlay/hooks/merge.py`](../overlay/hooks/merge.py) — merge 계약 구현
- [`../overlay/_overlay/README.md`](../overlay/_overlay/README.md) — consumer overlay 스켈레톤 가이드
