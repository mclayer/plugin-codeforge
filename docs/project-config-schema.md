---
title: project.yaml schema — consumer SSOT 상수 구조화
status: active
created: 2026-04-24
updated: 2026-05-30  # CFP-1809 — branch_protection.* block 신설 (consumer overlay 4-enum applicability — wrapper_only/always/optional/external_managed, ADR-083 consumer-applicability filter framework instance). MINOR — 기존 schema 확장 (선택 field, backward-compat: 부재 = 기존 wrapper-only 동작 유지)
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

  # CFP-127 / ADR-032 amendment 1 + CFP-660 / ADR-032 amendment 2 — strict mode opt-in.
  # default = false (warning-only, ADR-027 §결정 2 Tertiary trigger LLM-trust 정합).
  # true 시 strict-eligible drift 5종 발견 → exit 1 (CFP-660 4 → 5 종 확장):
  #   (a) project.yaml 부재
  #   (b) plugin 11종 중 wrapper(1) + 6 lane(6) + superpowers(1) = 8 critical 미설치
  #   (c) settings.json 의 SessionStart × 2 + UserPromptSubmit × 1 hook 미등록
  #   (d) 18 label 중 phase:* (7) + gate:* (3) = 10 critical 부재
  #   (e) consumer .github/workflows/<name>.yml SHA / 핵심 line drift vs wrapper templates
  #       (CFP-660 / ADR-032 amendment 2 §결정 6 — STRICT_ELIGIBLE_WORKFLOWS 7 file:
  #        phase-gate-mergeable / phase-label-invariant / story-init / story-section-1-immutable /
  #        subissue-from-impl-manifest / fix-ledger-sync / story-section-schema).
  #       Tier 1 SHA-256 compare → Tier 2 core marker (concurrency / on / permissions) fallback.
  #       Superficial whitespace-only diff = drift 분류 영역 외 (semantic-only invariant 영역).
  # Priority (CLI > env > yaml — most explicit wins):
  #   1. CLI flag: --strict
  #   2. Env: CODEFORGE_STRICT_BOOTSTRAP=1
  #   3. YAML (lowest): bootstrap.strict_mode: true (본 field)
  # Bypass precedence: HOTFIX_BYPASS_CODEFORGE=1 + REASON 양 env set → strict 무관 hook self skip (ADR-027 §결정 3).
  # Per-drift bypass: hotfix-bypass:workflow-version-drift label 부착 (audit-trailed channel,
  #   ADR-024 Amendment 3 §결정 6.A per-entry namespace, 20번째 hotfix-bypass:* family member).
  # Revert: false 또는 field 삭제 + commit.
  strict_mode: true | false             # 기본값: false (opt-in)

  # CFP-658 / ADR-027 Amendment 2 — Action 차단 환경 fallback path (normative SSOT).
  # enum: auto (default) / action_blocked
  #   - auto: 기존 동작 — story-init.yml 등 6 핵심 workflow 자동 실행 가정
  #   - action_blocked: enterprise org `default_workflow_permissions: read` 차단 환경 — manual fallback path 자동 활성
  # Trigger 우선순위 (C) > (A):
  #   (A) Declarative — 본 field (environment default)
  #   (C) Explicit ad-hoc — Issue `fallback:manual` label (per-Issue override)
  # Priority (CLI > env > yaml — ADR-032 정합 일관성):
  #   1. CLI flag: --fallback-mode=action_blocked
  #   2. Env: CODEFORGE_FALLBACK_MODE=action_blocked
  #   3. YAML (lowest): bootstrap.fallback_mode: action_blocked (본 field)
  # 활성 시 Orchestrator 가 RequirementsPL / ArchitectPL 의 manual `bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출 의무
  # (Phase 2 carrier — 본 script 신설 후 활성).
  # 4 required check (phase-gate-mergeable + doc frontmatter + doc section + invariant-check) 통과 의무 동일.
  # `enforce_admins: true` ratchet 유지 (CFP-70) — admin override 차단.
  # 상세 SSOT: ADR-027 Amendment 2 §결정 6 + domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md.
  fallback_mode: auto | action_blocked  # 기본값: auto

# [선택] Infra 산출물 전략 (CFP-128 / ADR-033)
# default = "docker_first" — InfraEngineerAgent 가 Dockerfile + compose.yml + .dockerignore 1st-class 산출
# "legacy_systemd" — systemd unit / launchd plist (deprecated, opt-in only — ADR-033 §결정 3)
# "none" — library / config-only repo (Docker artifact 미적용, examples/library-minimal 시범)
infra_strategy: docker_first | legacy_systemd | none  # 기본값: docker_first

# [선택] Infra 산출물 보조 옵션 (CFP-128 / ADR-033)
infra_strategy_extras:
  k8s_preset_enabled: true | false  # presets/k8s/ (codeforge-develop) 활성 여부, 기본값: false

# [선택] Multi-repo story key system (CFP-342 / ADR-069)
# Opt-in only — 부재 시 single-repo flat 모드 유지 (기존 동작 보존).
# 활성화 트리거 = `codeforge.stories.repos[]` 에 1+ entry 선언.
# Backward compat: 기존 single-repo consumer + 기존 multi-repo hub-flat 운영 (mctrader MCT-1~111) 모두 영향 0.
codeforge:
  stories:
    hub:
      key_pattern: <string>           # 예: "{prefix}-{seq:03d}" (또는 자유 format string), optional
      story_dir: <string>             # default: "docs/stories", optional
      template: <string>              # default: "hub-story.md", optional
    repo_key_pattern: <string>        # 예: "{prefix}-{seq:03d}", optional
    counters:
      path: <string>                  # default: ".codeforge/counters.json", optional
      lock: file                      # enum: "file" (Phase 1 = file 만 지원), optional
    repos:
      - name: <string>                  # required, repo 식별자 (예: "mctrader-hub")
        role: governance | implementation  # required, enum
        path: <string>                  # role=implementation 시 required, sibling checkout 위치
        github: <string>                # role=implementation 시 required (예: "mclayer/mctrader-data")
        story_dir: <string>             # default: "docs/stories", optional
        components:                     # role=implementation 시 권장 (target repo fallback)
          - <string>                    # 예: "data", "pipeline"
        creates_repo_stories: <bool>    # default: true (governance role 은 false), optional

  # [선택] Wrapper plugin version 고정 — 3-way version atomic invariant consumer layer
  #   (CFP-820 Wave 3 Story-6 / ADR-063 Amendment 5 §결정 15 / reconcile-protocol-v1 v1.5 §4.8)
  # 3-way invariant: publisher (wrapper .claude-plugin/plugin.json .version)
  #   ↔ registry (mclayer/marketplace .claude-plugin/marketplace.json .plugins[name=codeforge].version)
  #   ↔ consumer (본 codeforge.version_pin.version) — 3 layer byte-identical exact-string match
  #   (semver normalize 안 함: 5.81.0 ≠ 5.81 ≠ v5.81.0 모두 mismatch — publisher SSOT canonical, consumer verbatim mirror)
  # Fallback semantic (orthogonality invariant — `version_pin` 가용성 ≠ version 정합성, conflate 금지):
  #   - version_pin block 미등록 (본 block 부재) = warning-first (3-way lint skip + warn message
  #       "consumer 고정 SSOT 미등록 — codeforge.version_pin 등록 후 3-way enforce 활성", exit 0).
  #       onboarding 마찰 0 (ADR-027 Amendment 4 §결정 8 / bootstrap.fallback_mode 패턴 답습)
  #   - version_pin.version 등록 후 publisher/registry mismatch = blocking-on-pr (exit 1, PR 차단 — drift 0 strict enforce)
  # consumer-authored (project-config-schema §4b write 금지 invariant 절대 보존 — codeforge agent write 0)
  # 3-way lint = read-only (scripts/check-3way-version-parity.sh — Phase 2 carrier).
  #   ADR-066 §결정 2 marketplace contents:read reuse, 추가 PAT grant 0 (write scope 미사용)
  version_pin:
    version: <string>                  # 예: "5.81.0" — 고정 할 wrapper plugin version (publisher↔registry↔consumer 3-way SSOT)

  # [선택] Multi-version channel 고정 — codeforge family 7 plugin release tier selector
  #   (CFP-906 Wave 4 sub-Epic #1 Story-1 / ADR-076 §결정 9 / ADR-016 Amendment 3 / ADR-063 Amendment 6 §결정 17 / reconcile-protocol-v1 v1.7 §4.10)
  # 3-tier closed-enum (stable | beta | canary) — release tier selector (version specifier 와 독립 차원).
  # codeforge.version_pin (version specifier) 과 disjoint peer block — 동일 block 내 embedding 금지
  #   (ADR-076 §결정 9.3 disjoint invariant — channel ≠ version specifier, 두 변경 축 axis of change 분리).
  # family_7_plugin_atomic × channel 고정 invariant (ADR-016 §결정 1 + Amendment 3):
  #   consumer codeforge.channel: <C> 선언 시 family 7 plugin (wrapper + codeforge-{requirements,design,develop,test,review,pmo}) 모두 동일 channel <C> 으로 resolve.
  #   per-plugin channel override 거부 (mixed channel 운영 = ADR-016 §결정 1 family scope invariant 위배).
  # 3-way channel invariant (ADR-063 Amendment 6 §결정 17):
  #   publisher (wrapper <C>-branch version) ↔ registry (marketplace.json plugins[name=codeforge].channels[tier=<C>].version) ↔ consumer (본 codeforge.channel.tier resolved version) 3-way byte-identical.
  # Per-tier semantic (ADR-076 §결정 9.1):
  #   - stable (default): current active stable release. LOW risk class. developer self-service OK.
  #   - beta: opt-in incremental track. MEDIUM risk class. developer + reviewer awareness 충분.
  #   - canary: preview + production-impact tier. HIGH risk class (production cutover semantic).
  #       admin tier 권장 (consumer-side 책임, ADR-076 §결정 9.4 channel selection authority asymmetry).
  #       canary tier 선언 시 Wave 4 sub-Epic #1 Story-3 ProductionEvidenceDeputy spawn trigger 영역
  #         (ADR-72 §결정 1 정합 — Live touching = TRUE 영역, declare layer 본 Story-1 영역 외).
  # Fallback semantic (orthogonality invariant — channel 가용성 ≠ channel 정합성, conflate 금지):
  #   - channel block 미등록 (본 block 부재) = default stable 자연 fallback (warning 0, lint skip 0).
  #       기존 consumer overlay 영향 0 (additive only — schema rule §1.1 선택 필드 추가, backward-compat invariant).
  #   - channel.tier 등록 후 invalid enum value (stable/beta/canary 외) = validator FAIL (warning-first → Wave 4 sub-Epic #1 Story-2 runtime carrier blocking-on-pr).
  #   - channel.tier 등록 후 family 7 plugin 중 1+ mixed channel 검출 = Wave 4 sub-Epic #1 Story-2 runtime UpgradeAgent abort (declare layer = mandate semantic, runtime detection = Story-2 carrier).
  # consumer-authored (project-config-schema §4b write 금지 invariant 절대 보존 — codeforge agent write 0)
  # Channel drift detection (Wave 4 sub-Epic #1 Story-2 carrier):
  #   3-tuple drift — (a) consumer codeforge.channel.tier ↔ (b) 실 install plugin .version ↔ (c) marketplace channels[*].versions[] membership.
  #   24h cron + workflow_dispatch + Issue auto-create (ADR-063 Amendment 3 §결정 13 marketplace-drift-detection 패턴 답습, warning-first).
  channel:
    tier: stable | beta | canary       # 3-tier closed-enum strict (default: stable). undeclared 값 = validator FAIL (Story-2 runtime carrier active).

# [선택] Lane 활성화 설정 (CFP-317 / ADR-048)
# default = security_ai: false (5-lane + CI gate 모드)
# security_ai: true 시 SecurityTestPL (Claude+Codex 2차 AI 보안 분석) spawn 활성
# 내부 전용 / solo-dev 시스템은 false 권장.
# 외부 노출 서비스 / 금융 데이터 처리 시스템은 true 권장.
lanes:
  security_ai: false               # 기본값: false (opt-in only)

# [선택] ModuleArchitect deputy applicability + migration tool override — aggregate-level (CFP-1086 / CFP-1126 / ADR-042 Amendment 8 + 10 / ADR-086)
# default = applicable: true, migration_tool: alembic
# applicable: false 시 ModuleArch deputy (aggregate-level) 미spawn (frontend-only / API-only / external-managed RDB consumer)
# migration_tool: 9-enum override (consumer overlay 가 자유 override 가능)
aggregate_arch:
  # CONDITIONAL applicability (CFP-1086 P2)
  # default: true (대부분 consumer 가 RDB OLTP schema 제어권 보유)
  # false = ModuleArch deputy (aggregate-level) 미spawn (예: frontend-only project / API-only project / external-managed RDB)
  applicable: true                 # bool, default true

  # Migration tool 9-enum override (consumer overlay 가 stack 에 맞게 override)
  # 정책 layer (7 원칙: 양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) 는 stack-agnostic
  # Tool layer = consumer 자유 override (default alembic Python stack)
  migration_tool: alembic          # enum: [alembic, prisma-migrate, typeorm, goose, golang-migrate, flyway, liquibase, sqlx-migrate, custom]

# [선택] Telemetry / measurement channel (CFP-283 / ADR-042 / ADR-043)
# default = 모든 channel disabled (opt-in default false invariant — ADR-043 §결정 1)
# Phase 1 = wrapper / consumer 동일 trust model — default false + 사용자 explicit opt-in 의무
# wrapper dogfood always-on enforcement (env flag / hook / runtime validation) = Phase 2 follow-up CFP
# silent always-on 금지 — default false 위반 시 policy_violation
telemetry:
  enabled: false                              # global gate (default false)
  channels:
    stop_event: false                         # stop-event-v1 ledger (default false)
    # spawn_event: false                      # spawn-event-v1 (Phase 2 deferred — ADR-042 §결정 3)
  storage_path: ".claude-work/measurement/"   # default sqlite location (ADR-042 §결정 4)
  retention_hot_days: 14                      # default 14d (range: 7-30, Researcher §6.6 InfluxData 중간값)

# [선택] 통합테스트 Baseline Suite 정의 (ADR-055 Amendment 2)
integration_test:
  # Baseline Suite 경로 (default: tests/integration/baseline/)
  baseline_suite_path: <string>         # e.g. "tests/integration/baseline"

  # 서비스 기동 전 필수 .env 키 목록 (env_missing 감지용)
  required_env_keys:
    - <string>                          # e.g. "DATABASE_URL"
    - <string>                          # e.g. "BITHUMB_API_KEY"

  # 초기 Baseline 정의 항목 (최초 Epic 실행 전 consumer가 직접 정의 — seed 역할)
  # 이후 Epic PASS 시 Story Suite 자동승격으로 누적 확장됨
  initial_baseline:
    - id: <string>                      # e.g. "deployability_check"
      description: <string>             # e.g. "서비스 전체 스택 기동 + DB 연결 + health check"
      test_path: <string>               # e.g. "tests/integration/baseline/test_deployability.py"

  # docker-compose.test.yml 경로 (default: docker-compose.test.yml)
  docker_compose_test_path: <string>    # e.g. "infra/docker-compose.test.yml"

  # Deployability 4-step (d) — health check endpoint 목록
  # 미정의 시 기본값: [{name: "app", url: "http://localhost:8000/health", expected_status: 200, timeout_seconds: 30}]
  health_checks:
    - name: <string>               # e.g. "app", "worker"
      url: <string>                # e.g. "http://localhost:8000/health"
      expected_status: <int>       # default: 200
      timeout_seconds: <int>       # default: 30

  # Deployability 4-step (c) — DB 연결 확인 대상
  # 미정의 시 DB probe 비활성 (deployability_verified 판정 시 DB step 생략)
  db_probes:
    - name: <string>               # e.g. "primary_db", "redis_cache"
      dialect: postgres | mysql | sqlite | redis | mongo
      connection_env: <string>     # .env 내 연결 문자열 키, e.g. "DATABASE_URL"
      ping_command: <string|null>  # null 시 dialect 기본 ping 사용 (e.g. "SELECT 1" for postgres)
      timeout_seconds: <int>       # default: 10
```

### `integration_test` 섹션 설명

Consumer 프로젝트의 통합테스트 Baseline Suite와 실행 환경을 구성한다. 모두 선택 사항.

- **`baseline_suite_path`**: Baseline Suite 테스트 디렉터리. 미정의 시 `tests/integration/baseline/` 사용.
- **`required_env_keys`**: 서비스 기동 전 확인할 `.env` 필수 키 목록. 미정의 시 env_missing 감지 비활성.
- **`initial_baseline`**: 프로젝트 최초 Epic 실행 전 seed 항목. 첫 Epic PASS 후 Story Suite 자동승격으로 확장됨. ADR-055 Amendment 2 §결정 3 참조.
- **`docker_compose_test_path`**: 통합테스트용 docker-compose 파일 경로. 미정의 시 루트의 `docker-compose.test.yml` 사용.
- **`health_checks`**: Deployability 4-step (d) health check endpoint 목록. 미정의 시 `http://localhost:8000/health` HTTP 200 확인. 복수 서비스(API + worker 등) consumer는 명시 필수.
- **`db_probes`**: Deployability 4-step (c) DB 연결 확인 대상. 미정의 시 DB probe 생략 (deployability_verified 판정에서 (c) step 항상 PASS 처리). 실제 DB 연결 검증을 원하는 consumer는 명시 필수.

**미정의 시 동작**: `integration_test` 섹션 자체가 없으면 IntegrationTestAgent가 default 경로와 빈 env_keys 목록, default health check URL로 동작한다.

### `codeforge.version_pin` 섹션 설명 (CFP-820 Wave 3 Story-6 / ADR-063 Amendment 5 §결정 15)

3-way version atomic invariant 의 **consumer-side layer**. ADR-063 base atomic invariant 는 wrapper-side publishing-time 3-file (`.claude-plugin/plugin.json` + `CHANGELOG.md` + `mclayer/marketplace/.claude-plugin/marketplace.json`) 만 cover. 본 `codeforge.version_pin` block 이 consumer-side runtime 고정 layer 를 추가해 **publisher ↔ registry ↔ consumer 3-way byte-identical version invariant** 를 완성한다.

- **`version_pin.version`** (선택, string): consumer 가 사용 중인 wrapper plugin version 을 자기 repo SSOT 로 declare (예: `"5.81.0"`). publisher (`plugin.json .version`) ↔ registry (`marketplace.json .plugins[name=codeforge].version`) ↔ consumer (본 field) 3 layer exact-string match (semver normalize 안 함 — `5.81.0` ≠ `5.81` ≠ `v5.81.0` 모두 mismatch. publisher SSOT 가 canonical, consumer 는 verbatim mirror 의무).
- **Fallback semantic (orthogonality invariant)**: `version_pin 가용성` (본 block 등록 여부 = enforce 가능 여부) 과 `version 정합성` (값 일치 여부 = drift 존재 여부) 은 **ORTHOGONAL 2 조건** — conflate 금지.
  - **version_pin block 미등록** (본 block 부재) = **warning-first** (3-way lint skip + warn message "consumer 고정 SSOT 미등록 — codeforge.version_pin 등록 후 3-way enforce 활성", exit 0). version_pin 부재 = mismatch 판정 불성립 (비교 대상 없음 — false-positive 차단). onboarding 마찰 0 (ADR-027 Amendment 4 §결정 8 / `bootstrap.fallback_mode` 패턴 답습).
  - **version_pin.version 등록 후 mismatch** = **blocking-on-pr** (exit 1, PR 차단). drift 0 strict enforce (등록 영역).
- **미정의 시 동작**: `codeforge.version_pin` block 자체가 없으면 3-way lint (`scripts/check-3way-version-parity.sh`, Phase 2 carrier) 가 warning-first 분기 (lint skip + warn, exit 0) — 신규 consumer onboarding 마찰 0. consumer 가 `version_pin` 등록은 자율 (codeforge 강제 안 함).
- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 field write 금지 (§4b write 금지 invariant 절대 보존). 3-way lint = read-only compare-only (write surface 0, ADR-066 §결정 2 `marketplace contents:read` reuse — 추가 PAT grant 0).

### `aggregate_arch` 섹션 설명 (CFP-1086 / ADR-042 Amendment 8 / ADR-086)

**ModuleArchitectAgent** (aggregate-level — 구 AggregateArchitectAgent, CFP-1126 / ADR-042 Amd 10 통합) deputy 의 consumer overlay 영역. RDB OLTP aggregate invariant 변호자. 2 field — `applicable` (CONDITIONAL spawn 활성) + `migration_tool` (9-enum override).

- **`aggregate_arch.applicable`** (선택, bool, default `true`): ModuleArch deputy (aggregate-level) 활성 여부.
  - `true` (default) — 대부분 consumer 가 RDB OLTP schema 제어권 보유. 설계 lane 진입 시 ModuleArch deputy (aggregate-level) parallel spawn 활성. 6 permanent deputy 모두 활성 (CFP-1086 / CFP-1126 정합).
  - `false` — ModuleArch deputy (aggregate-level) 미spawn. non-applicable consumer 영역:
    - **frontend-only project** (RDB schema 부재)
    - **API-only project** (외부 RDB consume only, schema 제어권 없음)
    - **external-managed RDB** (consumer 가 schema 제어권 없음, 예: SaaS DB)
  - `false` 시 6 permanent deputy + 3 sub-tuple = 9 SubAgent (vs default 10) parallel spawn. ArchitectAgent chief 가 RDB OLTP 영역 결정 안내 skip + 사유 명시.
  - LiveOps / LiveOrdering / ProductionEvidence CONDITIONAL 패턴 재사용 (CFP-1086 P2).

- **`aggregate_arch.migration_tool`** (선택, string, default `alembic`): RDB 마이그레이션 도구 선택.
  - **정책 layer (stack-agnostic)** — Alembic 정책 7 원칙 (양방향 호환 / 확장-정리 분리 / reverse / smoke / cross-repo / 백업 / hard limit) 은 모든 tool 에 적용 (stack-agnostic, wrapper 강제).
  - **Tool layer (consumer override)** — 9-enum:
    - `alembic` (default, Python + SQLAlchemy reference implementation, mctrader)
    - `prisma-migrate` / `typeorm` (Node stack)
    - `goose` / `golang-migrate` (Go stack)
    - `flyway` / `liquibase` (Java stack)
    - `sqlx-migrate` (Rust stack)
    - `custom` (consumer-defined — 9 enum 외 도구)
  - 본 field 는 ModuleArchitectAgent (aggregate-level) 의 §11 RDB OLTP author 시 input (tool 선택만, 정책 7 원칙 mandate 는 무변경).

- **미정의 시 동작**: `aggregate_arch` 섹션 자체가 없으면 default 값 적용 (`applicable: true`, `migration_tool: alembic`). codeforge wrapper 강제 안 함 (consumer 자율).

- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 field write 금지 (§4b write 금지 invariant 절대 보존). ModuleArchitectAgent (aggregate-level) = read-only (consumer overlay value 를 spawn-time Context Packet 으로 수신 후 mandate 결정에 반영).

### `deploy` 섹션 설명 (CFP-1059 / [ADR-087](../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md))

Deploy lane + Deploy Review lane (CFP-1059 / 6 → 8 lane 확장) 의 consumer overlay 영역. Phase 1 declarative — 실 DeployPLAgent / DeployReviewPLAgent spawn = lane plugin seed (codeforge-deploy / codeforge-deploy-review) 신설 후 활성 (별 sub-Story carrier).

```yaml
# .claude/_overlay/project.yaml

# [선택] Deploy lane settings (CFP-1059 / ADR-087)
deploy:
  # 배포 매커니즘 = blue-green + atomic swap + 3-시간 보존 + 자동 rollback (ADR-087 §결정 5 — 단일 매커니즘 고정).
  # 본 block 부재 시 deploy lane 가 트리거 안 됨 (Epic close 후 wrapper trigger skip — opt-in).

  # [필수, deploy block 활성 시] 5 sub-field 모두 declare 의무.

  # host_mapping — 배포 대상 호스트 ↔ container 매핑 (multi-host topology declare)
  host_mapping:
    - host: <string>                   # SSH target hostname (e.g. "deploy-01.acme.io")
      containers:                      # 해당 host 에 배포될 container image list
        - <string>                     # e.g. "acme/api:latest"
        - <string>                     # e.g. "acme/worker:latest"

  # docker_hub — Docker Hub registry 좌표 (image push/pull SSOT)
  docker_hub:
    org: <string>                      # Docker Hub org / username, e.g. "acme"
    image_prefix: <string>             # image name prefix, e.g. "acme-app-"
    auth_secret_env: <string>          # GitHub Secrets key for Docker Hub auth (e.g. "DOCKER_HUB_TOKEN")

  # traefik — Traffic 분배 reverse proxy 설정 (atomic swap label flip target)
  traefik:
    enabled: <bool>                    # true = Traefik label-based swap / false = manual (custom orchestration)
    network: <string>                  # Traefik docker network name (e.g. "acme-public")
    domain_pattern: <string>           # public-facing domain template, e.g. "{service}.acme.io"

  # 1password — Secret provider (1Password Connect SDK lookup, primary)
  1password:
    enabled: <bool>                    # true = 1Password Connect primary / false = .env fallback
    connect_host_env: <string>         # 1Password Connect server URL env key (e.g. "OP_CONNECT_HOST")
    connect_token_env: <string>        # 1Password Connect token env key (e.g. "OP_CONNECT_TOKEN")
    vault: <string>                    # vault name, e.g. "Production"
    # Fallback semantic: 1password.enabled=false 시 deploy lane = .env file SSH 전송 fallback (less secure)

  # ssh_targets — SSH pull deployment 대상 host list (host_mapping host 와 중복 가능)
  ssh_targets:
    - host: <string>                   # SSH hostname (host_mapping 의 host 와 일치 권장)
      user: <string>                   # SSH login user (e.g. "deploy")
      key_secret_env: <string>         # GitHub Secrets key for SSH private key (e.g. "SSH_DEPLOY_KEY")
      port: <int>                      # default: 22

  # [선택] auto_rollback — 자동 rollback 신호 monitor 설정 (CFP-1193 / ADR-105 §결정 3 / ADR-106 Amendment 1 §결정 1 단계 2-a)
  # 부재 시 rollback-signal-monitor cron = wrapper fast-pass exit 0 (ADR-104 §결정 4 정합, 신호 감지 비활성)
  auto_rollback:
    enabled: <bool>                    # false = kill-switch config flag (§3.4 secondary disable — filesystem flag primary)
                                       # true = 신호 감지 활성 (안전장치 4 AND 충족 시만 trigger, ADR-105 §결정 3)
    error_rate_threshold: <float>      # 에러율 임계 — 에러/전체 요청 비율 (예: 0.02 = 2%)
                                       # 미정의(빈 문자열/부재) = 안전장치 1 false → trigger 0 (보수적 EC-1)
    latency_burn_rate_threshold: <float>  # latency error budget 소진율 임계 (예: 1.0 = burn_rate ≥ 1.0)
                                          # 미정의 = 안전장치 1 false (error_rate_threshold OR burn_rate_threshold 중 1개 이상 정의 의무)
    window: <int>                      # 측정 window (초, default: 3600 = 1시간, ADR-087 §결정 5 3시간 보존 window 내 의무)
                                       # 보존 window(3시간=10800초) 초과 설정 금지 — 안전장치 2 false 처리 (EC-3)

  # [선택] operational_monitor — regression/smoke·health monitor 설정 (CFP-1194 / ADR-106 Amendment 2 §결정 1 단계 2-a)
  # 부재 시 regression-smoke-health-monitor cron = wrapper fast-pass exit 0 (ADR-104 §결정 4 정합, 감지 비활성)
  # S4 auto_rollback block 과 disjoint — S5 는 ops-signal Issue 발의만 (auto-rollback trigger 없음)
  operational_monitor:
    enabled: <bool>                    # false = 신호 감지 비활성 (flap state 누적 중단)
                                       # true = regression + health 감지 활성
    signal_type: <str>                 # 측정 대상 식별자 (예: "latency_p99", "success_rate", "throughput")
                                       # health 감지는 signal_type 무관 (.codeforge/health-status.json 파싱)
    metric_name: <str>                 # health-status.json / current-metric.json 안 key name (예: "latency_p99_ms")
    regression_threshold: <float>      # regression 판정 임계 (%, 예: 10.0 = 10% 악화)
                                       # 미정의(빈 문자열/부재) = 신호 미감지 (보수적 unconditional guard EC-4)
    recovery_margin: <float>           # hysteresis recovery margin (%, default: 0.5)
                                       # regression 해소 판정 = pct_change < (threshold - margin)
                                       # 외부 HTTP health endpoint 금지 (D3 0 API call — filesystem .codeforge/health-status.json primary)
    flap_n: <int>                      # N-tick for-clause tick 수 (default: 2)
                                       # 연속 N tick 유지 후 Issue 발의 (단발 FAIL 억제)
    window: <int>                      # 측정 window (초, default: 86400 = 24시간 — daily cron 주기 정합)

  # [선택] self_improving_loop — loop closure gate 설정 (CFP-1195 / ADR-106 §결정 4)
  # 부재 시 self-improving-loop-closure cron = wrapper fast-pass exit 0 (ADR-104 §결정 4 정합)
  # loop closure 3-principle OR-fire: (a) dedup + (b) max-depth + (c) escalate_user — OR 발동 시 자동 Issue 생성 억제
  self_improving_loop:
    enabled: <bool>                    # false = loop closure gate 비활성 (cron 실행되나 gate 통과 0)
                                       # true = ops-signal pattern 누적 + Epic-level dedup + PMO escalation 활성
    loop_max_depth: <int>              # 동일 signature 반복 loop 최대 허용 깊이 (default: 3)
                                       # loop_depth >= loop_max_depth → max-depth gate trip → escalate_user
                                       # Google SRE/ITIL/NASA 보수적 lower bound 3 (ADR-068 I-5 §7.4 empirical-source)
    dedup_window_hours: <int>          # 동일 signature dedup window (시간, default: 24)
                                       # window 내 open Issue/Epic 존재 → dedup gate trip → 신규 발의 억제
                                       # S4/S5 Issue-level 24h 정합 (ADR-068 I-5 §7.4 dimension: lifecycle)
    pattern_count_threshold: <int>     # PMO escalation 발화 임계 (default: 2)
                                       # signal_type 별 ops-signal Issue 누적 count >= threshold → stage 3 발화
                                       # Google SRE/ITIL/NASA industry lower bound 2 (ADR-068 I-5 §7.4 dimension: count)

  # [선택] canary — canary auto-promote 설정 (CFP-1196 / ADR-105 §결정 3)
  # 부재 시 canary-auto-promote = wrapper fast-pass exit 0 (ADR-104 §결정 4 정합, canary 비활성)
  # 안전장치 4 AND: (1) criteria 4-tuple (2) 3h retention window (3) notification 가용성 (4) kill-switch off
  # kill-switch OR disable (보수적): filesystem flag .codeforge/auto-promote.disabled OR config auto_promote_enabled=false
  canary:
    subset: <string>                   # 배포 대상 canary host list (공백 구분, 예: "host1 host2")
                                       # 미정의(빈 문자열/부재) = deploy.host_mapping 첫 번째 host (D2 default — 보수적)
                                       # 전체 host = promote 단계와 canary 단계 경계 소멸 → subset 지정 권장
    auto_promote_enabled: <bool>       # false = kill-switch config flag (안전장치 4 secondary disable)
                                       # true = 안전장치 4 AND 충족 시 자동 promote 활성 (default: true 이나 생략 = enabled 로 간주)
                                       # filesystem kill-switch (.codeforge/auto-promote.disabled) 가 OR 보수적 disable
                                       # → config true 여도 filesystem flag 부재 시만 promote 실행
```

- **본 block 부재 시 동작**: deploy lane (CFP-1059) 가 Epic close 후 자동 trigger 되지 않음 (opt-in). 8 lane workflow 완결 시 wrapper Orchestrator = `phase:보안-테스트` 후 terminal (CFP-1059 이전 default 동작 유지). consumer 가 deploy block 등록 후 codeforge-deploy plugin install 시 deploy lane 활성.
- **operational_monitor 동작 원칙** (CFP-1194 / ADR-106 Amendment 2 §결정 1 단계 2-a): S4 `auto_rollback` 과 완전 disjoint — S5 는 ops-signal Issue 발의만 (auto-rollback trigger 없음, ADR-104 §결정 4 wrapper fast-pass). `regression_threshold` 미정의 = 보수적 EC-4 (신호 미감지). `flap_n` 연속 N tick 도달(default 2) 후 Issue 발의 (flap 3-layer 내 layer-a). hysteresis recovery margin = pct_change < (threshold - margin, default 0.5%) 조건 충족 시 신호 해소. window default 86400초(24h, daily cron 주기 정합). 0 API call invariant (filesystem primary: `.codeforge/{operational-baseline,health-status,operational-flap-state}.json` — 외부 HTTP health endpoint 금지).
- **self_improving_loop 동작 원칙** (CFP-1195 / ADR-106 §결정 4): loop closure 3-principle OR-fire — (a) dedup gate (open Issue/Epic 존재), (b) max-depth gate (loop_depth >= loop_max_depth), (c) escalate_user gate (pattern_count >= threshold) — 3 원칙 중 1개라도 trip 시 자동 Issue 생성 억제 + stage 4 user gate 발화 (자동 Epic 개시 금지 invariant). `enabled: false` = cron 실행되나 gate 통과 불가 (0 Issue 발의). `loop_max_depth` 미정의 = default 3 (보수적 runaway 차단 lower bound). `pattern_count_threshold` 미정의 = default 2 (industry lower bound, Google SRE/ITIL/NASA 정합). S4/S5 monitor 와 disjoint source — S4/S5-originated Issue 는 Epic-level dedup gate (b)만 적용 (re-creation 없음). 0 API call invariant (filesystem primary: `docs/kpi/operational-signal-history.jsonl` append-only — ADR-104 §결정 3).
- **canary 동작 원칙** (CFP-1196 / ADR-105 §결정 3): `canary.auto_promote_enabled: false` = safety_4 config kill-switch → promote 전체 무력화 (filesystem kill-switch `.codeforge/auto-promote.disabled` OR config false = 보수적 OR disable). `subset` 미정의 = host_mapping 첫 번째 host (D2 default, 보수적 최소 배포). 안전장치 3 (notification_available) = promote 전 GH_TOKEN + gh CLI presence pre-check (0 API call) — unavailable 시 무음 promote 차단. 안전장치 1 aggregation (CFP-991 verbatim 재사용): ALL(gate_state IN {pass, n_a}) AND ANY(gate_state == pass) → criteria_met. 1+ fail = abort (EC-1 보수적). all n_a = abort (pass 최소 1 필수). wrapper self-app Tier-1 fast-pass (GITHUB_REPOSITORY=mclayer/plugin-codeforge → exit 0, ADR-104 §결정 4). consumer 환경: Actions vars `CANARY_*_GATE_STATE` + `CANARY_WITHIN_RETENTION` + `DEPLOY_CANARY_SUBSET` 로 gate 상태 주입 의무.
- **auto_rollback 안전장치 4 AND** (CFP-1193 / ADR-105 §결정 3): `auto_rollback.enabled: false` = safety_4 false → trigger 전체 무력화 (신호 감지·기록 계속 — 무음 차단 금지 EC-2). `error_rate_threshold` / `latency_burn_rate_threshold` 미정의 = safety_1 false → trigger 0 (보수적 fallback EC-1). `window` 가 3시간 보존 window(10800초) 초과 = safety_2 false (ADR-087 §결정 5). filesystem kill-switch (`.codeforge/auto-rollback.disabled`) = safety_4 override (config enabled 여부 무관 — OR disable §3.4 정합). kill-switch 활성 시에도 신호 감지·ops-signal Issue 발의 계속 (EC-2).
- **fallback semantic**:
  - `deploy.host_mapping` 부재 = deploy lane 활성화 prerequisite 불충족 → warning + skip (Epic close 진행, manual deploy operator 영역).
  - `deploy.1password.enabled=false` = `.env` fallback (CI Secrets → SSH 전송, less secure). production 환경 = `true` 권장.
  - `deploy.traefik.enabled=false` = manual orchestration override (consumer 자체 reverse proxy). codeforge wrapper = blue-green atomic swap automation skip.
- **schema 7 원칙 binding** (CFP-1059 / [ADR-089](../archive/adr/ADR-089-schema-change-7-principles.md)): consumer 의 schema 변경 (DB / inter-plugin contract / API contract / event schema / project.yaml 본 block 자체) 시 ChangePlan §11 self-check 표 의무 (S2 carrier wire). deploy block field 추가 시 본 schema 자체도 7 원칙 적용.
- **cross-layer 영향** (CFP-1059 / [ADR-090](../archive/adr/ADR-090-cross-layer-reference-policy.md)): consumer 가 multi-layer architecture (RDB / 빅데이터 / API / service repo) 운영 시 deploy block 등록 = cross-layer 의존 매핑 source (자동 감지 + 사용자 declare hybrid).
- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 block write 금지 (§4b write 금지 invariant 절대 보존). DeployPLAgent / DeployReviewPLAgent = read-only (consumer overlay value 를 spawn-time Context Packet 으로 수신 후 배포 sequence 결정에 반영).

### `atlassian` 섹션 설명 (CFP-1215 / [ADR-100](../archive/adr/ADR-100-confluence-doc-ssot-recognition.md))

Atlassian suite 재결합 (Epic-A CFP-1146) 의 consumer overlay 영역. ADR-100 §결정 3 — project.yaml `atlassian.*` schema (token = `*_env` reference only, SecurityArch 권고, deploy 1password env-key precedent 정합).

```yaml
# .claude/_overlay/project.yaml

# [선택] Atlassian suite 재결합 (CFP-1215 / ADR-100)
# 부재 시 동작: Confluence 비활성, 기존 git-only governance 유지 (opt-in)
atlassian:
  enabled: <bool>                    # true = Confluence doc SSOT 활성 (ADR-100, ADR-013/041 partial extend)
                                     # false 또는 section 부재 = git-native only governance (default)
  confluence:
    base_url: <string>               # Confluence instance URL — NOT secret (Internal 분류)
                                     # 예: "https://myorg.atlassian.net/wiki"
    space_key: <string>              # target space key — NOT secret (Internal 분류)
                                     # 예: "CGOV" (codeforge governance space)
    api_token_env: <string>          # .env / secret store key name — 평문 token 금지, env-key reference only
                                     # 예: "ATLASSIAN_API_TOKEN" (Atlassian REST basic-auth token env key)
    user_email_env: <string>         # Atlassian REST basic-auth email key name — token 과 동일 Secret 취급
                                     # 예: "ATLASSIAN_USER_EMAIL"
    # 신규 field (CFP-1668 / ADR-100 Amendment 2 + ADR-111 Amendment 2)
    instance: <string>               # [optional] Atlassian instance hostname — NOT secret (Internal 분류)
                                     # 예: "mclayer.atlassian.net" / "myorg.atlassian.net"
                                     # consumer multi-instance 영역 (sandbox/production 분리 가능)
                                     # 부재 시: base_url 에서 hostname 추출 (fallback)
    homepage_id: <string>            # [required if mirror enabled] Confluence space 의 root homepage page ID
                                     # per-consumer IA tree base anchor — confluence-ia-tree.yaml space.root_homepage_id 정합
                                     # 예: "1867943"
                                     # 부재 시 mirror 비활성 (consumer Confluence migration 선행 조건)
    mirror_targets: <array>          # [required if mirror enabled] closed-enum 5 의 subset (확장 0 invariant)
                                     # ADR-111 Amendment 2 §결정 1 SYMMETRIC subset (consumer 선택 자유)
                                     # 허용 값: adr / architecture_doc / change_plan / domain_knowledge / orchestrator_playbook
                                     # 예: [adr, architecture_doc]
                                     # 부재 시 mirror 비활성
    per_doc_type_override: <map>     # [optional] per-doc-type 별 binding 오버라이드
                                     # wrapper-managed marker block 안 ownership
                                     # conflict resolution: consumer-authored 영역 우선 (OOS edge case 4번 carrier)
                                     # 예: {adr: {parent_page_id: "12345"}}
  jira:                              # W4+ (ADR-103 sync mechanism) — S2 declare-only, schema placeholder
    project_key: <string>            # NOT secret (Internal 분류)
                                     # 예: "PROJ"

# [선택] Branch protection consumer overlay (CFP-1809 / [ADR-083](adr/ADR-083-consumer-applicability-filter.md) instance)
# default = applicable: wrapper_only (codeforge family plugin repo SSOT 만 유지 — wrapper CLAUDE.md "6 lane plugin branch protection contexts SSOT" 표 자체 governance)
# 부재 시 동작: consumer 측 `phase-gate-mergeable` 참조 silent drift 차단 안 됨 (wrapper-only governance, consumer 자체 branch protection 자율).
# applicable: always 선언 시 consumer 가 자체 main branch protection contexts 의무 declare (mctrader case — 자체 build/test/lint 등 자체 governance).
branch_protection:
  applicable: wrapper_only | always | optional | external_managed
                                     # ADR-083 consumer-applicability filter 4-enum instance (본 schema-specific 정의 — walker per-step applicable_to 와 disjoint scope):
                                     #   wrapper_only (default) — codeforge family plugin repo 만 governance. consumer 측 branch protection 자율 (wrapper 비검사). 기존 동작 보존.
                                     #   always — consumer 가 자체 main branch protection 의무 (예: mctrader-* 5 repo). required_contexts[] declare 의무.
                                     #   optional — consumer 자율 declare (선언 시 검사 활성, 부재 시 skip). enforcement 없음.
                                     #   external_managed — external CI tool (Jenkins / CircleCI / GitLab CI 등) 가 governance. codeforge lint 영역 외 (false-positive 차단).

  required_contexts:                 # consumer 측 main branch required_status_checks.contexts[] strict-match list
                                     # applicable=always 시 의무. applicable=wrapper_only/external_managed 시 무시. applicable=optional 시 선언 가능.
                                     # 예: ["build", "test", "lint"] — context-name strict match (workflow job ID 또는 GitHub Action status check name)
    - <string>                       # e.g. "build" / "test" / "lint" / "phase-gate-mergeable"

  enforce_admins: <bool>             # default true (admin 도 required check 통과 의무 — wrapper CFP-70 정합)
                                     # consumer 가 admin override 허용 정책 시 false (less safe — drift 0 invariant 위배 가능)

  consumer_repo_lint:                # [선택] branch-protection-context-parity lint (CFP-1807 cross-repo parity carrier) 가 consumer repo 도 검사할지 결정
                                     # 부재 시: consumer repo 검사 비활성 (codeforge family 9 plugin 만 iteration)
    enabled: <bool>                  # default false — consumer 자체 lint 미설정 fallback
                                     # true = lint 가 family[] 안 consumer repo 도 iteration (consumer 측 contexts drift 자동 감지)
    family:                          # enabled=true 시 의무 — 검사 대상 consumer repo list
      - <string>                     # e.g. "mclayer/mctrader-hub" / "mclayer/mctrader-data"
```

- **secret 분류** (SecurityArch §7.1 정합):
  - **Secret = `api_token` + `user_email`** (Atlassian REST basic-auth pair) — schema field 는 `*_env` reference (env key name) 만 허용, 평문 token / email 직접 기재 금지. 값은 env / secret store 경유 주입.
  - **Internal (NOT secret) = `base_url` / `space_key` / `project_key`** — 평문 기재 허용.
  - precedent: project-config-schema.md `deploy.docker_hub.auth_secret_env` / `deploy.1password.connect_token_env` / `deploy.ssh_targets[].key_secret_env` = 모두 `_env` suffix reference 패턴 (ADR-100 §결정 3 §secret boundary 정합).

- **부재 시 동작**: `atlassian` section 자체가 없으면 Confluence 비활성 — 기존 git-only governance 동작 유지. codeforge agent = git SSOT 우선 (ADR-013 §결정 1 KEEP 영역 보존). `homepage_id` 또는 `mirror_targets` 부재 시도 mirror 비활성 (opt-in, backward-compat 보장).

- **신규 field 분류** (CFP-1668 / ADR-100 Amendment 2 + ADR-111 Amendment 2):
  - **Internal (NOT secret) = `instance` / `homepage_id` / `mirror_targets` / `per_doc_type_override`** — 평문 기재 허용. `instance` = `base_url` hostname 중복 허용 (명시적 override 가능).
  - **`mirror_targets` closed-enum 5** (ADR-111 Amendment 2 §결정 1 SYMMETRIC subset): `adr` / `architecture_doc` / `change_plan` / `domain_knowledge` / `orchestrator_playbook`. 확장 0 invariant — 신규 타입 추가 시 ADR-111 Amendment 필요.
  - **`per_doc_type_override` scope**: wrapper-managed marker block 안 ownership. consumer-authored 영역에서 conflict 시 consumer 우선 (ADR-027 consumer-authored 원칙 정합).

- **ADR-027 natural extend**: atlassian.* schema 신설은 ADR-027 amendment 불요 — project-config-schema.md 갱신으로 bootstrap validation 이 자동 cover (ADR-027 §결정 1 정합). consumer 측 schema validator 추가는 Phase 2 carrier.

- **narrow allow defer**: `atlassian.enabled: true` 설정 시에도 Layer 1 (`mcp__atlassian__*` deny baseline) 은 W4/ADR-103 narrow allow wire 전까지 유지 (ADR-100 §결정 4 — deny precedence 경고, narrow allow 사용처 미존재 시 선제 부여 = 최소권한 위반).

- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 block write 금지 (§4b write 금지 invariant 절대 보존). sync agent (ADR-103 carrier) = read-only (consumer overlay value 수신 후 sync 대상 결정).

### `branch_protection` 섹션 설명 (CFP-1809 / [ADR-083](../archive/adr/ADR-083-consumer-applicability-filter.md) instance)

Consumer 측 main branch protection contexts governance 의 consumer overlay 영역. CFP-1785 retro follow-up FU-C P3 carrier — consumer 가 `phase-gate-mergeable` 등 wrapper context 를 stale reference 로 보유 시 silent drift 차단. ADR-083 consumer-applicability filter framework 의 schema-specific instance (walker per-step `applicable_to: {consumer/wrapper/both}` filter 와 disjoint scope — 본 4-enum 은 branch protection 영역 특화).

- **`branch_protection.applicable`** (선택, enum, default `wrapper_only`): consumer-applicability 4-enum 분류.
  - **`wrapper_only`** (default) — codeforge family plugin repo (wrapper + 6 lane plugin + codeforge-deploy + codeforge-deploy-review = 9 plugin) 만 governance. wrapper `CLAUDE.md` "6 lane plugin branch protection contexts SSOT" 표 가 SSOT. consumer 측 branch protection = 자율 (wrapper 검사 0건). 기존 동작 보존 — backward-compat invariant.
  - **`always`** — consumer 가 자체 main branch protection 의무 declare. `required_contexts[]` field 의무 (예: mctrader 5 repo 가 자체 build/test/lint 등 자체 governance). lint 가 declare 된 contexts 와 actual gh api response strict-match parity 검사.
  - **`optional`** — consumer 자율 declare. `required_contexts[]` 선언 시 검사 활성, 부재 시 skip. enforcement 없음 (advisory only — onboarding 마찰 0).
  - **`external_managed`** — external CI tool (Jenkins / CircleCI / GitLab CI / BuildKite 등) 가 governance. codeforge lint 영역 외 (false-positive 차단 — 외부 도구 contexts 검사 안 함). consumer 가 external CI 운영 시 declare.

- **`branch_protection.required_contexts`** (조건부 의무, array): consumer 측 main branch `required_status_checks.contexts[]` strict-match list.
  - `applicable=always` 시 의무 — declare 0건 = validator FAIL.
  - `applicable=optional` 시 선택 — declare 시 검사 활성, 부재 시 skip.
  - `applicable=wrapper_only / external_managed` 시 무시 (declare 해도 검사 안 함).
  - context-name = workflow job ID 또는 GitHub Action status check name strict match (semver normalize 안 함 — "build" ≠ "Build" ≠ "build (ci)" 모두 mismatch, consumer 가 verbatim mirror 의무).

- **`branch_protection.enforce_admins`** (선택, bool, default `true`): admin 도 required check 통과 의무 (wrapper CFP-70 정합 — drift 0 invariant 강화).
  - `true` (default) — admin merge pre-flight gate (ADR-113 §결정 1 정합) 활성. admin override 차단.
  - `false` — admin override 허용 (less safe — drift 0 invariant 약화 가능). 명시적 consumer 선택 시에만 false (advisory warning).

- **`branch_protection.consumer_repo_lint`** (선택, object): `branch-protection-context-parity` lint (CFP-1807 cross-repo parity carrier) 의 consumer repo 확장 영역.
  - **`enabled`** (선택, bool, default `false`) — consumer 자체 lint 미설정 fallback. `true` 시 lint 가 `family[]` 안 consumer repo 도 iteration (consumer 측 contexts drift 자동 감지).
  - **`family`** (조건부 의무, array) — `enabled=true` 시 의무. 검사 대상 consumer repo list (예: `["mclayer/mctrader-hub", "mclayer/mctrader-data"]`). 부재 시 = enabled 무효 (lint skip).
  - Phase 2 carrier 영역 — 본 Story (CFP-1809) Phase 1 declarative-only. mechanical wire (consumer repo iteration logic) = 별 sub-CFP carrier.

- **미정의 시 동작**: `branch_protection` 섹션 자체가 없으면 default 값 적용 (`applicable: wrapper_only`, `enforce_admins: true`, `consumer_repo_lint.enabled: false`). codeforge wrapper 강제 안 함 (consumer 자율 — backward-compat invariant). 기존 consumer overlay 영향 0 (additive only — schema rule §1.1 선택 필드 추가).

- **mctrader case (applicable=always)** — mctrader-hub + mctrader-data + mctrader-market + mctrader-engine + mctrader-web 5 repo 가 자체 build/test/lint 등 자체 governance 운영. consumer overlay `branch_protection.applicable: always` + `required_contexts: ["build", "test", "lint"]` declare. CFP-1785 retro 가 발견한 silent drift 영역 (consumer 가 wrapper `phase-gate-mergeable` context 를 stale reference 로 보유 시) = `applicable=always` declare 후 actual gh api response strict-match parity 검사로 차단.

- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 block write 금지 (§4b write 금지 invariant 절대 보존). `branch-protection-context-parity` lint (CFP-1807 carrier) = read-only compare-only (write surface 0). consumer 가 본 field 등록은 자율 (codeforge 강제 안 함, default `wrapper_only` 보존).

- **ADR-083 framework cross-ref**: ADR-083 = consumer-applicability filter general framework (walker per-step `applicable_to: {consumer/wrapper/both}` filter). 본 `branch_protection.applicable` 4-enum 은 framework 의 schema-specific instance — branch protection 영역 특화 enum (4-way) vs walker filter 영역 일반 enum (3-way). disjoint scope — 두 4-enum 이 같은 axis 가 아님 (walker filter = workflow yml copy 영역, branch protection = consumer repo gh api response 검사 영역).

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

**Multi-repo 예시 — mctrader 6-repo (CFP-342 / ADR-069)**:

```yaml
project:
  name: mctrader

github:
  org: mclayer
  repo: mctrader-hub
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: MCT
  codeowners:
    architect_team: "@mclayer/architects"
    domain_expert_team: "@mclayer/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"

# CFP-342 / ADR-069 — Multi-repo story key system (mctrader 6-repo Mode B)
codeforge:
  stories:
    hub:
      key_pattern: "{prefix}-{seq:03d}"
      story_dir: docs/stories
      template: hub-story.md
    repo_key_pattern: "{prefix}-{seq:03d}"
    counters:
      path: .codeforge/counters.json
      lock: file
    repos:
      - name: mctrader-hub
        role: governance
        story_dir: docs/stories
        creates_repo_stories: false
      - name: mctrader-data
        role: implementation
        path: C:/workspace/mclayer/mctrader-data
        github: mclayer/mctrader-data
        story_dir: docs/stories
        components: [data, pipeline, storage]
      - name: mctrader-market
        role: implementation
        path: C:/workspace/mclayer/mctrader-market
        github: mclayer/mctrader-market
        story_dir: docs/stories
        components: [market, contracts]
      - name: mctrader-engine
        role: implementation
        path: C:/workspace/mclayer/mctrader-engine
        github: mclayer/mctrader-engine
        story_dir: docs/stories
        components: [engine, strategy, risk]
      - name: mctrader-web
        role: implementation
        path: C:/workspace/mclayer/mctrader-web
        github: mclayer/mctrader-web
        story_dir: docs/stories
        components: [web, ui]
  # CFP-820 Wave 3 Story-6 — 3-way version atomic invariant consumer 고정 (선택, ADR-063 Amendment 5 §결정 15)
  version_pin:
    version: "5.81.0"   # wrapper plugin version 고정 — 미등록 시 warning-first, 등록 시 blocking-on-pr 3-way enforce
  # CFP-906 Wave 4 sub-Epic #1 Story-1 — Multi-version channel 고정 (선택, ADR-076 §결정 9 declare layer)
  channel:
    tier: stable        # 3-tier closed-enum (stable | beta | canary, default: stable) — release tier selector, version_pin disjoint peer

# CFP-1809 — branch_protection consumer overlay (mctrader case, applicable=always)
branch_protection:
  applicable: always    # mctrader 5 repo 자체 governance — wrapper SSOT 와 disjoint
  required_contexts:
    - "build"
    - "test"
    - "lint"
  enforce_admins: true  # admin override 차단 (drift 0 invariant 강화, wrapper CFP-70 정합)
  consumer_repo_lint:
    enabled: false      # consumer 자체 lint 미설정 default (Phase 2 carrier — 별 sub-CFP wire)
```

**통합테스트 설정 예시 — mctrader-engine (FastAPI + PostgreSQL + Redis)**:

```yaml
integration_test:
  baseline_suite_path: tests/integration/baseline
  docker_compose_test_path: infra/docker-compose.test.yml

  required_env_keys:
    - DATABASE_URL
    - REDIS_URL
    - BITHUMB_API_KEY
    - BITHUMB_SECRET_KEY

  health_checks:
    - name: api
      url: http://localhost:8000/health
      expected_status: 200
      timeout_seconds: 30
    - name: worker
      url: http://localhost:8001/health
      expected_status: 200
      timeout_seconds: 30

  db_probes:
    - name: primary_db
      dialect: postgres
      connection_env: DATABASE_URL
      ping_command: null           # null → dialect 기본 "SELECT 1" 사용
      timeout_seconds: 10
    - name: redis_cache
      dialect: redis
      connection_env: REDIS_URL
      ping_command: "PING"
      timeout_seconds: 5

  initial_baseline:
    - id: deployability_check
      description: "전체 스택 기동 + DB 연결 + API/Worker health check"
      test_path: tests/integration/baseline/test_deployability.py
```

## 4. 에이전트 접근 규칙

### 4a. Read 전담
- **DocsAgent**: GitHub Issue/PR/comment·repo file write 시 `org`·`repo`·`story_key_prefix`·`codeowners`·`milestone.epic_naming_pattern` 활용
- **RequirementsPLAgent**: Story SSOT 파일(`docs/stories/<KEY>.md`) 위치 결정 시 `story_key_prefix` 사용. **Multi-repo system 활성 시** (CFP-342 / ADR-069) `codeforge.stories.repos[]` 검사 → hub vs repo story 결정 + target repo 결정 (frontmatter `story_scope` priority 1, `component` label fallback)
- **DomainAgent**: Domain Knowledge 트리(`docs/domain-knowledge/`) read + Discussions 질의 시 `discussions.domain_kb_category` 사용
- **PMOAgent**: 회고·Cross-Story 패턴 분석 시 GitHub Issue search query에 `org`·`repo` 활용
- **All lane plugin agents**: **Multi-repo system 활성 시** (CFP-342 / ADR-069) `codeforge.stories.repos[].path` + `components` 활용해 작업 target repo 결정 (priority: frontmatter `story_scope: repo` + `repo` → `story_scope: hub` → `component` label mapping → ESCALATE)
- **Orchestrator**: 세션 개시 시 1회 read → 필요 값 Context Packet으로 하위 에이전트에 전달 (반복 fetch 회피). 매 변경 시작 시 `story_cutoff.additional_exempt_categories`(있으면)를 cutoff 분류 입력으로 사용. **Multi-repo system 활성 시** Project Config Packet 에 `codeforge.stories.repos[]` slice 포함 의무

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
- [`adr/ADR-069-multi-repo-story-key-system.md`](../archive/adr/ADR-069-multi-repo-story-key-system.md) — Multi-repo story key system (`codeforge.stories.*` 블록 SSOT)
- [`adr/ADR-020-cross-repo-epic-pattern.md`](../archive/adr/ADR-020-cross-repo-epic-pattern.md) — Mode A/B/C cross-repo Epic 패턴 (ADR-050 의 조직적 결정 root)
