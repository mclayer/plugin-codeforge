---
title: project.yaml schema — consumer SSOT 상수 구조화
status: active
created: 2026-04-24
updated: 2026-04-26
---

# `project.yaml` Schema

Consumer 프로젝트의 **objective SSOT 상수**를 구조화 주입하는 파일. 위치: `.claude/_overlay/project.yaml`.

에이전트(특히 DocsAgent·RequirementsPLAgent·DomainAgent·PMOAgent)는 이 파일을 `Read` 툴로 직접 읽어 GitHub 상수를 확보한다. CLAUDE.md overlay는 **narrative 컨텍스트**(도메인 해설·기술 스택 근거)에 집중.

## 1. 경계

### project.yaml에 들어가는 것 (structured)
- GitHub 좌표 (org·repo·default branch·story key prefix·CODEOWNERS team·Discussions 카테고리·Milestone naming)
- PR 제목 포맷
- Label taxonomy 프로젝트별 확장 (`component:*` 구체값)
- 프로젝트 식별자 (name)

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

# [필수] GitHub 좌표
github:
  org: <string>                     # GitHub org 또는 user, e.g. "acme"
  repo: <string>                    # repo 이름, e.g. "task-manager"
  default_branch: <string>          # merge target, 보통 "main"

  # PR 제목 prefix 템플릿. {key}·{title} placeholder 지원.
  # e.g. "[{key}] {title}" → "[TM-7] Add idempotency key"
  pr_title_prefix_template: <string>

  # Issue 번호 prefix. e.g. "TM" → "TM-7"
  story_key_prefix: <string>

  codeowners:
    architect_team: <string>        # e.g. "@acme/architects" — docs/adr·docs/change-plans·.github/workflows·docs/stories review 강제
    domain_expert_team: <string>    # e.g. "@acme/domain-experts" — docs/domain-knowledge review 강제

  discussions:
    domain_kb_category: <string>    # e.g. "Domain Q&A" — DomainAgent Q&A 카테고리

  milestone:
    epic_naming_pattern: <string>   # e.g. "Epic-{key}-{slug}" — Epic Milestone 명명

# [선택] 프로젝트별 label 확장
# phase:*·fix:*·gate:*·type:*·adr:*·impl-manifest·hotfix:*·audit:* 는 core에서 정의 (overlay 대상 아님).
# consumer는 component:* 만 정의.
labels:
  components:                       # 각 항목이 "component:<name>" 라벨로 생성
    - <string>                      # e.g. "api", "ui", "data"

# [선택] Story 작성 의무 cutoff 확장 (CLAUDE.md "Story 작성 의무" 섹션 참조)
# Plugin core가 정의한 강제 항목 6종은 축소 불허. Consumer는 도메인 특화 면제 항목만 추가 가능.
story_cutoff:
  additional_exempt_categories:     # 각 항목 1줄 자유 텍스트 면제 사유 카테고리
    - <string>                      # e.g. "auto-generated migration files"
    - <string>                      # e.g. "vendored library updates (security 영향 없음)"

# [선택] Workflow distribution mode (CFP-86 / consumer-guide §2c, CFP-89)
# default = "full" (Path A — 7 workflow 모두 보유 — CFP-94 후 story-section-schema.yml 추가)
# "degraded" (Path B) = 일부 workflow 부재, manual compensating check 의무
# 부재한 workflow 명시 의무 (degraded 시).
workflow_distribution:
  mode: full | degraded             # 기본값: full
  missing_workflows:                # mode=degraded 시 의무, mode=full 시 비어있음
    - <string>                      # e.g. "story-init.yml"
    - <string>                      # e.g. "fix-ledger-sync.yml"

# [선택] Progress narration verbosity (CFP-114 / ADR-029)
# default = "full" (모든 sub-step event 가 stderr 로 narrate — Deputy spawn/return / 병렬 dispatch / R9 subset 등)
# "lane_only" = lane-level event 만 narrate (CFP-20 기존 동작, sub-step 은 file-only)
# 다른 값 = validate_config.py FAIL.
progress_narration_verbosity: full | lane_only  # 기본값: full

# [선택] Bootstrap protocol settings (CFP-103 / ADR-027 / CFP-127 / ADR-032)
bootstrap:
  # CFP-103 — workflow distribution override (existing).
  expected_workflows:                   # 부재 시 check_bootstrap.EXPECTED_WORKFLOWS_FULL 사용
    - <string>                          # e.g. "phase-gate-mergeable.yml"

  # CFP-127 / ADR-032 amendment 1 — strict mode opt-in.
  # default = false (warning-only, ADR-027 §결정 2 Tertiary trigger LLM-trust 정합).
  # true 시 strict-eligible drift 4종 발견 → exit 1 (CFP-127 / ADR-032 §결정 2):
  #   (a) project.yaml 부재
  #   (b) plugin 11종 중 wrapper(1) + 6 lane(6) + superpowers(1) = 8 critical 미설치
  #   (c) settings.json 의 SessionStart × 2 + UserPromptSubmit × 1 hook 미등록
  #   (d) 18 label 중 phase:* (7) + gate:* (3) = 10 critical 부재
  # Priority (CLI > env > yaml — most explicit wins):
  #   1. CLI flag: --strict
  #   2. Env: CODEFORGE_STRICT_BOOTSTRAP=1
  #   3. YAML (lowest): bootstrap.strict_mode: true (본 field)
  # Bypass precedence: HOTFIX_BYPASS_CODEFORGE=1 + REASON 양 env set → strict 무관 hook self skip (ADR-027 §결정 3).
  # Revert: false 또는 field 삭제 + commit.
  strict_mode: true | false             # 기본값: false (opt-in)

# [선택] Infra 산출물 전략 (CFP-128 / ADR-033)
# default = "docker_first" — InfraEngineerAgent 가 Dockerfile + compose.yml + .dockerignore 1st-class 산출
# "legacy_systemd" — systemd unit / launchd plist (deprecated, opt-in only — ADR-033 §결정 3)
# "none" — library / config-only repo (Docker artifact 미적용, examples/library-minimal 시범)
infra_strategy: docker_first | legacy_systemd | none  # 기본값: docker_first

# [선택] Infra 산출물 보조 옵션 (CFP-128 / ADR-033)
infra_strategy_extras:
  k8s_preset_enabled: true | false  # presets/k8s/ (codeforge-develop) 활성 여부, 기본값: false

# [선택] Telemetry / measurement channel (CFP-283 / ADR-042 / ADR-043)
# default = 모든 channel disabled (opt-in default false invariant — ADR-043 §결정 1)
# wrapper dogfood = CODEFORGE_DOGFOOD_TELEMETRY=1 explicit env flag 시만 always-on
# consumer 측 silent always-on 금지 — default false 위반 시 policy_violation
telemetry:
  enabled: false                              # global gate (default false)
  channels:
    stop_event: false                         # stop-event-v1 ledger (default false)
    # spawn_event: false                      # spawn-event-v1 (Phase 2 deferred — ADR-042 §결정 3)
  storage_path: ".claude-work/measurement/"   # default sqlite location (ADR-042 §결정 4)
  retention_hot_days: 14                      # default 14d (range: 7-30, Researcher §6.6 InfluxData 중간값)
```

## 3. 예시 (webapp)

```yaml
project:
  name: task-manager

github:
  org: acme
  repo: task-manager
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: TM
  codeowners:
    architect_team: "@acme/architects"
    domain_expert_team: "@acme/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"

labels:
  components:
    - api
    - ui
    - data
    - infra

workflow_distribution:
  mode: full
  missing_workflows: []
```

**Path B (degraded) 예시 — mctrader-hub 시점**:

```yaml
workflow_distribution:
  mode: degraded
  missing_workflows:
    - story-init.yml
    - story-section-1-immutable.yml
    - fix-ledger-sync.yml
    - subissue-from-impl-manifest.yml
```

## 4. 에이전트 접근 규칙

### 4a. Read 전담
- **DocsAgent**: GitHub Issue/PR/comment·repo file write 시 `org`·`repo`·`story_key_prefix`·`codeowners`·`milestone.epic_naming_pattern` 활용
- **RequirementsPLAgent**: Story SSOT 파일(`docs/stories/<KEY>.md`) 위치 결정 시 `story_key_prefix` 사용
- **DomainAgent**: Domain Knowledge 트리(`docs/domain-knowledge/`) read + Discussions 질의 시 `discussions.domain_kb_category` 사용
- **PMOAgent**: 회고·Cross-Story 패턴 분석 시 GitHub Issue search query에 `org`·`repo` 활용
- **Orchestrator**: 세션 개시 시 1회 read → 필요 값 Context Packet으로 하위 에이전트에 전달 (반복 fetch 회피). 매 변경 시작 시 `story_cutoff.additional_exempt_categories`(있으면)를 cutoff 분류 입력으로 사용

### 4b. Write 금지
모든 에이전트는 `.claude/_overlay/project.yaml` **write 금지**. 이 파일은 consumer가 직접 관리. DocsAgent도 쓰지 않음.

### 4c. 값 부재 시 동작
- **필수 필드 missing** → 에이전트는 블록 후 Orchestrator에 "project.yaml에 `<field>` 누락" 보고. Orchestrator가 사용자에게 질의.
- **선택 필드 missing** → 기본 동작

## 5. 파일 부재 케이스

`.claude/_overlay/project.yaml`이 아예 없으면:
- 세션 개시 시 Orchestrator가 경고 출력: "project.yaml 없음 — GitHub 워크플로우 기능 제한됨"
- DocsAgent·RequirementsPLAgent 등이 GitHub MCP 호출 시 ERROR (필수 상수 unknown)
- 작업 지속은 가능하나 Story·PR 자동화 기능 대부분 차단됨

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
- **기술 스택 일부 구조화**: test runner·perf baseline 경로 등 objective 성격 항목 이전 (현재는 `.claude/_overlay/run-tests.sh`·`run-perf.sh` wrapper로 캡슐화)
- **placeholder 탐지**: `<REPLACE ...>` 값이 남아있으면 warn (unconfigured consumer 감지)
- **GitHub Projects v2 연동**: Project number·view ID 구조화

> Project Config Packet 자동 주입은 **이미 구현됨** — Orchestrator가 세션 개시 시 project.yaml을 1회 로드해 sub-agent 프롬프트에 packet으로 삽입한다. 캐시·무효화·Fallback 의미는 [`orchestrator-playbook.md`](orchestrator-playbook.md) §12.5 단일 SSOT 참조.

## 8. 관련 문서

- [`consumer-guide.md`](consumer-guide.md) §3 — 실제 설정·복사 절차
- [`plugin-design.md`](plugin-design.md) §5 — Stage 1/2 범위
- [`../overlay/_overlay/project.yaml.example`](../overlay/_overlay/project.yaml.example) — 스켈레톤
- [`../overlay/hooks/validate_config.py`](../overlay/hooks/validate_config.py) — Schema 검증 구현
- [`../agents/DocsAgent.md`](https://github.com/mclayer/plugin-codeforge/blob/v3.0.0/agents/DocsAgent.md) — 주 소비자
