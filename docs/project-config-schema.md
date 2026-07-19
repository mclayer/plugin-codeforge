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

  # [선택] Story SSOT repo (codeforge family dogfood-out only — CFP-2252 / ADR-013 Amendment 7)
  # 부재 시 template default = "mclayer/codeforge-internal-docs" (확장-only — 축소/제거 금지,
  # 선례 ADR-024 Amd2 §결정 A + ADR-026 Amd4 §결정 6, mechanism ADR-116 cross-ref).
  # 비-mclayer codeforge family fork 가 자체 internal-docs repo 사용 시 override.
  # 비-codeforge consumer 무관 (is_codeforge_family 가드 — consumer 분기 = ${GITHUB_REPOSITORY} local write).
  story_ssot_repo: <owner/repo>     # e.g. "mclayer/codeforge-internal-docs" (default)

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

# [DEPRECATED — ADR-127 §결정 6] story_cutoff.additional_exempt_categories 면제 확장채널 폐지.
# 모든 변경 = Story 작성 의무 (chore 면제 폐지 — ADR-127 §결정 1). consumer overlay 는 면제 추가 불가
# (overlay 는 정책 확장(더 엄격하게 — 강제 추가)만 가능, 면제 추가=강제 축소는 invariant 위반).
# 본 field 는 schema 에서 deprecated — 신규 overlay 에 사용 금지. (validate_config.py 는 backward-compat
# 으로 기존 overlay 의 본 key 를 reject 하지 않으나, 면제 효과는 ADR-127 발효로 무력화됨.)
# story_cutoff:
#   additional_exempt_categories: []   # [DEPRECATED] 면제 효과 없음 (ADR-127 §결정 6)

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
  #   (b) plugin 10종 중 wrapper(1) + 6 lane(6) = 7 critical 미설치
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

# [선택] Phase gate hub repo 화이트리스트 확장 (CFP-1716 / ADR-116)
# phase-gate-mergeable.yml + phase-gate-auto-cleanup.yml 의 ALLOWED_HUB_REPOS env 를 consumer 특화 hub repo 로 확장.
# Mechanism:
#   - Template default = "github.com/mclayer/codeforge-internal-docs" (항상 포함, 축소 불가)
#   - Consumer overlay 안 phase_gate.allowed_hub_repos[] 로 추가 hub repo 선언
#   - Post-reconcile: bash scripts/inject-allowed-hub-repos.sh 실행 (idempotent, dedup, never-reduce 보장)
# Idempotent: 매 reconcile 후 호출 = 항상 올바른 상태 복원 (매번 덮어써짐 현상 해소)
# 정책 SSOT: ADR-116 확장-only constraint (축소 / 기본값 제거 금지) — 선례 ADR-026 Amd4 §결정 6 / ADR-024 §결정 6
phase_gate:
  allowed_hub_repos:                  # Consumer 화이트리스트 추가 (string list, optional)
    - <string>                        # 예: "github.com/mclayer/mctrader-hub"
    - <string>                        # 예: "github.com/internal-org/internal-hub"

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
        components:                     # role=implementation 시 권장 (story-init.yml S3 component→owner_repo 라우팅 실 source)
          - <string>                    # 예: "data", "pipeline"
          # CFP-2423 / ADR-069 Amendment 1 (Phase 2) — Component-based repo routing
          #
          # 동작:
          #   - story-init.yml 의 "Route component to owner repo" step 이 ### Component 값을 파싱
          #   - 정규화(lowercase+trim, 매칭 시점만) 후 repos[].components[] 로 매핑
          #   - 1:1 매핑 → owner_repo=target (Story file 생성 repo)
          #   - 0 매핑 / 미매핑 → hub fallback (story_ssot_repo 또는 GITHUB_REPOSITORY)
          #   - N≥2 매핑 (component 중복 소유) → ESCALATE (fail-closed, Issue comment + workflow exit 1)
          #
          # 저장값 보존 원칙:
          #   - project-config-schema.md + 라벨(component:<원문>) + overlay 값: 원문 보존
          #   - 매칭 비교 시점만: 정규화(lowercase+trim)
          #
          # Topology validation:
          #   - repo_topology.responsibilities[].owner_repo 와 라우팅 결과(owner_repo) 대조 (ADR-131 소유레포 SSOT)
          #   - 불일치 시: surface(warning/notice), hard-block 아님 (AC-5)
          #   - topology applicable!=true / 미주입 → 대조 skip, PASS (AC-6)
          #   - multi-mapping + 중복소유 검출 → ADR-131 메타불변식 ③ 정합
          #
          # Backward compat:
          #   - repos[] 미선언 시: single-repo hub-flat 모드 유지 (기존 동작 100% 보존)
          #   - 라벨 부착(component:<원문>), Story frontmatter 생성 무변경
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

# [DEAD — ADR-141] story_stakes 조건부 tier config 는 폐지됨 (전 에이전트 opus 단일 tier — stakes 조건부 tier 소멸). 아래 스키마 는 역사 참고용, 신규 프로젝트 미사용.
# [선택] Story-shape 조건부 model tier — stakes 분류 + tier override (CFP-2432 / ADR-042 Amendment 16)
#   + DomainAgent financial-invariant-0 (CFP-2445 / ADR-042 Amendment 17)
# 같은 agent role 의 model tier 를 Story 의 stakes(결과 위험)로 분기. tier = f(mandate depth, stakes).
# low-stakes 4-AND shape(실자금 없음 ∧ production cutover 없음 ∧ 신규 신뢰경계 없음 ∧ live 외부 API 호출 없음)
#   에서 wrapper Orchestrator 가 InfraOperationalArchitectAgent 를 opus→sonnet spawn-time override, high-stakes 는 opus.
# DomainAgent (Amd17): (4-AND low-stakes) AND (financial-invariant-0 shape) 동시 충족 시만 sonnet.
#   financial-invariant-0 = stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축의 *별* predicate
#   (wrapper Orchestrator 가 spawn-전 외부 shape 판정 — §1 원문 + directive 경로 키워드 기준, consumer 자기보고 아님).
# default 부재 = 모든 agent 현행 tier (wrapper floor) — fail-safe (확장-only invariant, ADR-127 §결정6).
#
# ── 4 stakes 신호 소스 ownership (F-2) ──
#   - Story 메타 = shape 사실(실자금/cutover/신규경계/live API 여부) — wrapper Orchestrator 가 Story 에서 판정 (4-AND).
#   - project.yaml story_stakes = consumer 의 보수 override 채널만 (shape 사실 자기보고 아님).
# ── precedence / merge (F-2) ──
#   - 최종 tier = max(wrapper_floor, overlay)  (rank: haiku < sonnet < opus — 보수 방향 우선).
#   - 미상/파싱불가 = 보수 opus (fail-loud, get_consumer_tier.py fail-loud 선례 동형).
# ── enforcement 2중 (F-3) ──
#   (1) schema-gate: bootstrap strict-check (overlay/hooks/check_bootstrap.py check 11) 가 down-tier 거부.
#   (2) spawn-time clamp: scripts/check-stakes-tier-gating.sh 의 max(floor, overlay).
story_stakes:
  # [선택] conservative_override — 특정 agent 를 항상 opus 로 강제 (보수 방향, 확장-only — 항상 허용).
  #   consumer 가 "이 agent 는 우리 프로젝트에선 low-stakes 라도 opus 유지" 선언 시 사용.
  conservative_override:
    - InfraOperationalArchitectAgent   # 예: 항상 opus 강제 (Amd16)
    - DomainAgent                      # 예: financial-invariant-0 shape 라도 항상 opus 유지 (Amd17, 확장-only 보수 방향)

  # [거부 — schema-gate] tier_override 로 floor 미만 tier(opus→sonnet) 직접 지정 = down-tier 공격적 override.
  #   bootstrap strict-check (f) 가 거부 (확장-only enforcement, ADR-127 §결정6 / AC-3).
  #   tier_override 로 floor 이상(opus 강제)은 합법 (conservative_override 와 동등 효과).
  # tier_override:
  #   InfraOperationalArchitectAgent: sonnet   # ← 거부됨 (floor=opus 미만 down-tier)

# [선택] Telemetry / measurement channel (CFP-283 / ADR-163 / ADR-043; CFP-2393 spawn-event)
# default = 모든 channel disabled (opt-in default false invariant — ADR-043 §결정 1)
# Phase 1 = wrapper / consumer 동일 trust model — default false + 사용자 explicit opt-in 의무
# wrapper dogfood always-on enforcement (env flag / hook / runtime validation) = Phase 2 follow-up CFP
# silent always-on 금지 — default false 위반 시 policy_violation
telemetry:
  enabled: false                              # global gate (default false)
  channels:
    stop_event: false                         # stop-event-v1 ledger (default false)
    spawn_event: false                        # spawn-event-v1 per-agent token/cost attribution ledger (default false — ADR-163 Amendment 1 / ADR-043 Amendment 2, CFP-2393. oh-my-claudecode MIT 차용)
  storage_path: ".claude-work/measurement/"   # storage_path override = parent dir 대체 (basename 고정). per-channel 별 default: stop-event sqlite default parent = .claude-work/measurement/ (basename stop-event.sqlite, ADR-163 §결정 4); spawn-event JSONL default parent = .claude/ledger/ (basename spawn-event.jsonl 고정 — spawn-event-v1.md §3 storage_path_override_rule SSOT). override 지정 시 양 channel parent dir 함께 대체(각자 basename 유지), wrapper dir escape 금지 — ADR-163 §결정 9
  retention_hot_days: 14                      # default 14d (range: 7-30, Researcher §6.6 InfluxData 중간값)

# [선택] 통합테스트 Baseline Suite 정의 (ADR-055 Amendment 2)
integration_test:
  # Baseline Suite 경로 (default: tests/integration/baseline/)
  baseline_suite_path: <string>         # e.g. "tests/integration/baseline"

  # 서비스 기동 전 필수 프로세스 env 키 목록 (env_missing 감지용 — legacy 경로, D2 4계약은 아래 설명 참조)
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

  # daemon_type — 서비스 실행 형태 discriminator (CFP-2613 / ADR-148 §결정6)
  #   operational:true Story 필수 선언 (누락 = 지속-liveness soak 게이트 FAIL, silent default 금지)
  #   long_running_daemon        = 상주 데몬(백그라운드 loop) — 지속-liveness soak 게이트 scope
  #   request_response_service   = HTTP 요청/응답 서비스 — 기존 health_checks HTTP-200 default 유지
  #   batch_job | cli | none     = soak 미대상
  daemon_type: long_running_daemon | request_response_service | batch_job | cli | none

  # sink_probes — long_running_daemon ∧ operational:true 시 필수 (presence = fail-closed)
  #   IntegrationTest Deployability soak step 이 관측하는 terminal-sink monotone 전진 probe 목록
  #   non-HTTP 데몬의 sink-advance(적재 종점 단조 전진) = G2 신설 개념 (K8s native probe handler 아님)
  #   ★ 본 필드명 목록이 canonical field-name SSOT (F-4) — 타 문서는 참조만, 재인코딩 금지
  sink_probes:
    - name: <string>                     # e.g. "committed_rows", "written_parts"
      probe_type: sink-advance | exec | log-progress
      metric_command: <string>           # monotone 값 1개 반환 (credential = CI secret name 참조만, 평문 금지)
      boot_grace_seconds: <int>          # exit/restart 카운트 시작 유예 (ceiling ≤ soak/2)
      threshold: <int> | null            # manifestation-derived 조기 PASS (선택) — floor 창 내 임계 도달 시 조기 종료. null = floor 만료까지 net 순증(freeze) 판정
      duration_floor_seconds: <int>      # soak 창 max horizon / deadline ceiling (항상 필수, > 0 — timeout·hang 방지). threshold 와 배타 아님(그 위 상한)
      manifestation_trigger_type: time | volume
      poll_interval_seconds: <int>

# [선택] 인프라 자원 선언 manifest (CFP-2700 / ADR-157 §결정1)
# 인프라 자원(secret·env·외부 저장소 credential 등)을 prose 가 아닌 기계판독 manifest 로 선언.
# 2-plane: plane A resources[] (자원 카탈로그, id 단위) + plane B execution_units{} (실행단위→required 자원).
# infra_strategy (ADR-033 적용 여부 스위치) 와 직교 — 겹치지 않음 (applicability ⊥ 자원 내용).
# 미정의 시 동작: 본 block 부재 = manifest 미선언 (D3 drift scan census-only, startup 대조 대상 0).
# write boundary: SCHEMA(본 문서) = wrapper 소유 / VALUES(실 자원 맵) = consumer-authored only (§4b).
infra_resources:
  # ── plane A: 자원 카탈로그 (id 단위 — env 키 아님) ──
  resources:
    - id: <string>                    # 자원 논리 ID (env 키 아님) — plane B 는 이 ID 로만 참조
      namespace: <string>             # (선택) cross-repo 참조 시 필수 (§결정4). repo-local 자원은 생략. owner/repo 형식 — _NS_RE spoof/traversal 차단 + 순회 대상=선언 자원만(임의 repo 확산 불가). 별도 operator allowlist 없음(same-domain tautology, §결정8 (vii)).
      cross_repo_ref: <string>        # (namespace 선언 자원 필수, §결정4 ref-pin) moving-HEAD(main 등 7종) hard-fail + non-SHA ref WARN(idempotent 미보장) — 엄밀 idempotency 는 SHA-pin 만 보장 (§결정8 (viii)).
      cross_repo_path: <string>       # (namespace 선언 자원 필수, §결정4) foreign repo 내 대조 파일 경로 (static-parse 대상)
      canonical_env: <string>         # 자원당 정확히 1개 (INV-4) — 이 자원의 정본 env 키
      aliases:                        # (필수 표현 — 빈 집합 허용: 별칭 없으면 `accepted: []` 명시, AC-2)
        accepted:                     # 수용된 별칭 (canonical 과 동일 자원, drift 아님)
          - <string>                  # e.g. CONFLUENCE_API_TOKEN (canonical ATLASSIAN_API_TOKEN 의 accepted alias)
        deprecated:                   # deprecated 별칭 — 기한 필드 필수 (R6, 무기한 deprecated 금지)
          - name: <string>            # e.g. MINIO_URL
            status: deprecated
            deprecated_since: <date>  # ISO 8601 (YYYY-MM-DD)
            remove_after: <date>      # ISO 8601 — 이 기한 후 제거 대상
  # ── plane B: 실행단위 → required 자원 (ID-only 참조) ──
  execution_units:
    <unit-name>:                      # 실행단위 논리명 (CI job / 프로세스 / 서비스)
      required:                       # 이 실행단위가 요구하는 자원 (resource-id 만 — env 키 재기재 금지 = drift 원천 차단)
        - <resource-id>               # plane A resources[].id 참조 (env 키 = 자원의 투영이지 자원 아님)
      resource_modes:                 # EDGE 속성 — 실행단위×자원 마다 mode (같은 토큰이 unit A optional, unit B required 가능)
        <resource-id>: required | optional_degradable   # required=미설정 시 부팅거부 / optional_degradable=degrade+WARN (미설정 fail 아님)
        # optional_degradable 자원은 <resource-id>_degraded_behavior 로 degrade 동작 선언 필수 (no-silent-degrade)
        <resource-id>_degraded_behavior: <string>       # e.g. "파생 write skip + WARN, raw ingest 지속"
  # ── D2 startup fail-closed 채택 선언 (AC-15 / ADR-157 §결정2 — I-5 채택-bounded) ──
  startup_validation:
    adopted: true | false             # true = 실행단위 부팅 시 reference impl 로 required 자원 대조
    reason: <string>                  # adopted: false 시 필수 — 미채택 + 사유부재 = FAIL (silent 미채택 금지)
```

### `integration_test` 섹션 설명

Consumer 프로젝트의 통합테스트 Baseline Suite와 실행 환경을 구성한다. 모두 선택 사항.

- **`baseline_suite_path`**: Baseline Suite 테스트 디렉터리. 미정의 시 `tests/integration/baseline/` 사용.
- **`required_env_keys`**: 서비스 기동 전 확인할 **프로세스 env** 필수 키 목록 (legacy 경로 — `.env` 파일 grep 아님). 대조는 D2 startup fail-closed **4계약**([ADR-157](../archive/adr/ADR-157-infra-resource-manifest-drift-gate.md) §결정2: ① 프로세스 env 검사 ② exit-masking 금지 ③ 빈 값 reject ④ fail-closed default)을 따르며, reference impl = `scripts/lib/infra_startup_validator.py`. **미정의 = "감지 비활성" 아님**(구 서술은 proto-D2 결함 ⓓ fail-open 으로 폐기): `infra_resources.execution_units` manifest 채택 시 그 선언이 대조 원천이고, 채택 여부 자체를 `infra_resources.startup_validation` 으로 명시한다(미채택 + 사유부재 = FAIL — AC-15). 둘 다 부재한 프로젝트는 env 대조 원천 부재를 정직 공개할 뿐 silent fail-open 을 정상 동작으로 규정하지 않는다.
- **`initial_baseline`**: 프로젝트 최초 Epic 실행 전 seed 항목. 첫 Epic PASS 후 Story Suite 자동승격으로 확장됨. ADR-055 Amendment 2 §결정 3 참조.
- **`docker_compose_test_path`**: 통합테스트용 docker-compose 파일 경로. 미정의 시 루트의 `docker-compose.test.yml` 사용.
- **`health_checks`**: Deployability 4-step (d) health check endpoint 목록. 미정의 시 `http://localhost:8000/health` HTTP 200 확인. 복수 서비스(API + worker 등) consumer는 명시 필수.
- **`db_probes`**: Deployability 4-step (c) DB 연결 확인 대상. 미정의 시 DB probe 생략 (deployability_verified 판정에서 (c) step 항상 PASS 처리). 실제 DB 연결 검증을 원하는 consumer는 명시 필수.
- **`daemon_type`** (CFP-2613 / [ADR-148](../archive/adr/ADR-148-persistent-liveness-soak-gate.md) §결정6): 서비스 실행 형태 discriminator. `operational:true` Story 는 **선언 필수** (누락 = 지속-liveness soak 게이트 FAIL, silent default 금지 — `operational:true` 는 has-outcome-signal ⊥ is-a-daemon 직교 속성이므로 daemon 여부를 별도 discriminator 로 명시). `long_running_daemon` 만 soak 게이트 scope — `request_response_service` 는 기존 health_checks HTTP-200 default 유지(mass-breakage 회피). enum 5종: `long_running_daemon | request_response_service | batch_job | cli | none`.
- **`sink_probes`**: `long_running_daemon ∧ operational:true` 시 **presence fail-closed** (선언 부재 = FAIL). IntegrationTest Deployability soak step 이 관측하는 terminal-sink monotone 전진 probe 목록. non-HTTP 데몬의 `sink-advance`(적재 종점 단조 전진) 판정 = **G2 신설 개념** — K8s native probe handler(exec/httpGet/tcpSocket/grpc)가 아니라 monotone 값 반환 custom probe 등가(`source: kubernetes.io/docs/concepts/workloads/pods/probes` 는 개념 등가만, sink-advance 자체는 non-native). soak duration 은 `duration_floor_seconds`(soak 창 max horizon / deadline ceiling — **항상 필수**, > 0, timeout·무한 CONTINUE hang 방지) 위에 `threshold`(manifestation-derived **선택적 조기 PASS** — 임계 도달 시 floor 만료 전 종료)가 얹히는 구조 = **상호배타 아님**. threshold=null 이면 floor 만료 시점 net 순증(freeze) 판정. soak duration 도출 규칙 = [consumer-guide §1o Operational Story](consumer-guide.md) / ADR-148 §결정7 참조.

> **SCHEMA(문서) = wrapper 소유 / VALUES(실 값 맵) = consumer-authored only** (`health_checks`/`db_probes` 동형 — §4b write 금지 invariant). 본 `integration_test.sink_probes[]` 필드명 정의(`name`/`probe_type`/`metric_command`/`boot_grace_seconds`/`threshold`/`duration_floor_seconds`/`manifestation_trigger_type`/`poll_interval_seconds`)가 **canonical field-name SSOT (F-4)** — change-plan §7.4.7 · IntegrationTestAgent · consumer-guide 등 타 문서는 이곳을 **참조(pointer)만** 하고 필드 목록을 재인코딩하지 않는다 (dual-location = SSOT-참조지 값-복제 아님, ADR-068 I-4 wording-SSOT).

**미정의 시 동작**: `integration_test` 섹션 자체가 없으면 IntegrationTestAgent가 default 경로와 default health check URL로 동작한다. env 대조는 위 `required_env_keys` 항목의 D2 규칙을 따른다 — legacy 목록 부재 시 `infra_resources` manifest 채택 여부(`startup_validation`)가 대조 원천을 결정하며, "빈 목록 = 감지 비활성" 을 정상 default 로 규정하지 않는다(ADR-157 §결정2 계약 (4)). `daemon_type` 미선언 non-operational Story 는 soak 미대상(기존 4-step deployability 만).

### `infra_resources` 섹션 설명 (CFP-2700 / [ADR-157](../archive/adr/ADR-157-infra-resource-manifest-drift-gate.md) §결정1)

인프라 자원 변경의 미전파(자원 추가/이동/제거 시 참조 하드코드·설정·타 저장소 코드가 따라오지 못해 지연 크래시)를 각 참조면에서 loud 하게 검출하기 위한 **기계판독 자원 선언 manifest**. carrier = consumer(및 wrapper-self dogfood) `.claude/_overlay/project.yaml` 의 신규 `infra_resources:` block. 스키마 SSOT = 본 섹션, 실 값 맵 = consumer-authored. **2-plane** 구조 — plane A 는 자원을 논리 ID 로 카탈로그화하고, plane B 는 실행단위가 그 ID 만 참조해 required 자원을 선언한다(env 키 = 자원의 *투영*이지 자원 아님).

- **plane A `resources[]`** (자원 카탈로그, id 단위):
  - **`id`** (필수, string): 자원 논리 ID(env 키 아님). plane B 는 이 ID 로만 자원을 참조한다.
  - **`namespace`** (선택, string): cross-repo 참조 시 **필수**(ADR-157 §결정4) — cross-repo 참조는 `<namespace>/<id>` fully-qualified. repo-local 자원은 생략(AC-14 cross-repo In-scope 네임스페이스 명세). 값 = foreign `owner/repo` 형식. **fetch 도메인 = 선언된 namespace 집합**(순회 대상 = manifest cross-repo 자원 자체) + `_NS_RE`(owner/repo shape anchored — malformed·traversal 차단). **별도 operator-approval allowlist 는 없다**(ADR-157 §결정8 (vii)): manifest = semi-trusted 신뢰 declaration source(namespace = 작성자 선언, 공격자 주입 아님)이고 fetch = read-only 라 same-domain "allowlist" 는 tautology + 보안 분리 무제공이다. 미승인/오타 namespace 는 fetch 404 → hard-fail, 오타-실재 repo 는 content-mismatch → fail-closed 로 이미 걸린다.
  - **`cross_repo_ref`** / **`cross_repo_path`** (`namespace` 선언 자원 = cross-repo 자원 필수, ADR-157 §결정4 — G5 소비): D3 `--cross-repo` 대조(`scripts/lib/check_infra_resource_drift.py`)가 `gh api repos/<namespace>/contents/<cross_repo_path>?ref=<cross_repo_ref>` 로 foreign repo 참조면을 **static-parse-only**(fetch 콘텐츠 실행/eval 0) fetch 해 `canonical_env`(또는 alias) 전파를 대조한다 — 미참조 = 타저장소 미전파 검출. **`cross_repo_ref`**: moving-HEAD(`main`/`master`/`head`/`trunk`/`develop`/`default`/`latest` 7종) = **hard-fail**. 그 외 non-SHA ref(tag/mutable-branch)는 **수용하되 WARN**(비-SHA 는 idempotent 미보장 — name-based 로 tag/branch 구분 불가, mutable branch·재지정 tag 는 재실행 간 content 변동 가능). **엄밀 idempotency 는 SHA-pin(`^[0-9a-f]{7,64}$`)만 보장**(ADR-157 §결정8 (viii) — "pin 된 tag/SHA 만 대조" 는 name-based 로 집행 불가한 과대였으므로 정정). failure-mode 분리: content-mismatch=fail-closed(non-zero) / token(`CODEFORGE_CROSS_REPO_PAT`) 부재=degraded-FAIL(fail-open degrade 금지) / foreign transient(503·network·timeout)=fail-open+WARN+Issue(flaky 타repo 가 본 repo CI 상시 red 회피, ADR-011 death 재현 방지) / 403·404=`resp.ok` 확인 후 fail-closed(transient 와 구분). honest-ceiling(§결정8): 동적 키 구성 / 프록시 위장(socat) / 스캔 밖 표면 미검출 — presence ≠ truth, "완전 봉인" 금지. 실 cross-repo 활성 = **consumer 채택-bound**(I-5); wrapper-self 는 namespace 선언 자원 0 = vacuous PASS.
  - **`canonical_env`** (필수, string): 이 자원의 정본 env 키. **자원당 정확히 1개**(INV-4) — env 키 다종 난립은 canonical 부재의 *증상*이지 원인이 아니다.
  - **`aliases`** (필수 표현 — 빈 집합 허용, ADR-157 §결정1 "4 필수 필드" / AC-2): 동일 자원의 별칭 집합. 별칭이 없으면 `aliases:` + `accepted: []` 로 **빈 집합을 명시**한다 — 누락(키 자체 부재)은 schema FAIL(`scripts/lib/check_infra_manifest_schema.py`): "별칭 없음"의 명시 선언과 미선언(alias drift 판정 불능)을 구분하기 위함. `accepted[]` = canonical 과 동일 자원으로 수용된 별칭(drift 아님). `deprecated[]` = 폐기 예정 별칭이며 각 항목은 `name`·`status`·`deprecated_since`·`remove_after` **기한 필드 필수**(R6, 무기한 deprecated 금지 — R6 기한 필드의 기계 검증은 schema validator 미포함, 정직 공개).
- **plane B `execution_units{}`** (실행단위 → required 자원): 각 실행단위(CI job/프로세스/서비스)가 부팅 시 요구하는 자원을 **resource-id 만**으로 선언한다(env 키 재기재 = 2군데 진실 = drift 원천이므로 금지).
  - **`required[]`** (필수): 이 실행단위가 요구하는 자원 ID 목록(plane A `resources[].id` 참조).
  - **`resource_modes{}`** (선택): 실행단위×자원 **EDGE 속성**. mode 는 자원 자체가 아니라 (실행단위, 자원) 간선에 둔다 — 같은 토큰이 unit A 에서 `optional_degradable`, unit B 에서 `required` 일 수 있다(예: ADR-103 dry-run 자원). `∈ {required, optional_degradable}`:
    - **`required`** — 미설정 시 부팅 거부(fail-closed).
    - **`optional_degradable`** — 미설정 시 degrade + WARN(부팅 거부 아님). 이 경우 `<resource-id>_degraded_behavior` 로 **무엇으로 degrade 하는지 선언 필수**(no-silent-degrade). **미설정을 fail 시키지 않는다** — 이것이 required 와 optional_degradable 의 스키마 구분 semantics 다(AC-18: required=미설정 시 부팅 거부 / optional_degradable=미설정 시 fail 대상 아님, degrade+WARN. 런타임 대조 강제는 D2 startup 계약=G3 carrier).
    - **파서 계약 (F-CLA-004)**: `resource_modes` 맵 안에 병기되는 `<resource-id>_degraded_behavior` suffix 키는 **mode 엔트리가 아니라 metadata** 다 — mode 를 iterate 하는 파서는 `_degraded_behavior` suffix 키를 **strip 후 제외**해야 한다(suffix 키를 mode enum 값으로 오해 금지). 별도 sub-map 분리 등 구조 재설계는 ADR-157 amendment 소관 — 본 note 는 파서 계약 명시만.
- **`startup_validation`** (AC-15 / ADR-157 §결정2 — D2 채택 선언, G3): D2 startup fail-closed 계약의 **채택 여부 명시** 블록. `adopted: true` = 실행단위가 부팅 시 reference impl(`scripts/lib/infra_startup_validator.py`, 4계약: ① 프로세스 env 검사 ② exit-masking 금지 ③ 빈 값 reject ④ fail-closed default)로 required 자원을 대조 — 미설정 required = 첫 business 동작 이전 부팅 거부(exit 78 EX_CONFIG, 미설정 자원 ID loud 로그). `adopted: false` 는 `reason` **필수** — 미채택 + 사유 = 비적용 PASS / 미채택 + 사유부재 = FAIL(silent 미채택 금지, none-disguise 동형). wrapper-self 는 declarative-only(부팅하는 제품 바이너리 0)라 `adopted: false` + 사유 경로이며, reference impl 은 discriminating fixture(`tests/fixtures/infra-refimpl/` — refimpl-enforced/unenforced pair, `BUSINESS_OP_REACHED` 센티넬 판별)로만 falsify 한다(AC-4 honest-ceiling).

**applicability vs 내용 분리**: `infra_strategy`(ADR-033 — 적용 여부 스위치, `docker_first`/`legacy_systemd`/`none`) ≠ `infra_resources`(자원 내용). 둘은 직교하며 겹치지 않는다.

**패턴 재사용(신규 발명 아님, AC-16)**: `_env` reference 규약이 이미 project.yaml 다수 위치(`deploy.docker_hub.auth_secret_env` / `atlassian.confluence.api_token_env` / `integration_test.db_probes[].connection_env` 등)에 정착 — `infra_resources` = 산재한 기존 규약의 중앙화 + (자원 ID · alias · mode) 필드 추가. baseline/승격 기제도 ADR-060 재사용(신규 발명 금지).

**강제 범위 / honest-ceiling (ADR-157 §결정8 / AC-4·AC-12·AC-13)**: 본 manifest 대조 모델은 **정적 리터럴 env-key 참조 = 결정가능·in-scope**(AST/grep), **동적 구성 키(런타임 문자열 조립) = out-of-scope**(AC-13). D3 CI drift scan(Phase 2, G2 carrier)은 ADR-060 **warning-tier** 로 편입되며 required 승격 없이 surfacing 한다(AC-12). D2 startup fail-closed 계약의 강제 범위 = "wrapper 계약 + 참조 구현을 consumer 가 채택한 경우" 한정 — 미채택 consumer 미강제를 정직 공개한다(AC-4). "완전 보장/완전 봉인" hard-claim 금지 — "구조 fail-closed + 형식 누락 저감 + 잔여 정직 공개".

**미정의 시 동작**: `infra_resources` 섹션 자체가 없으면 manifest 미선언 — D3 drift scan(G2)은 census-only(inert 관측만)로 남는다. D2 startup 대조(G3)는 `startup_validation` 채택 선언 부재 = **미채택 상태**(I-5 채택-bounded — D2 는 consumer 가 채택해 쓰는 opt-in property)이므로, 이 미채택 상태에 한해 대조 원천 0 · 신규 consumer onboarding 마찰 0(additive-only)이다 — 단 "섹션/목록 부재 = 감지 비활성" 을 정상 default 로 규정하지 않는다(ADR-157 §결정2 계약 (4) fail-closed default: proto-D2 결함 (d) fail-open "미정의 시 감지 비활성" 봉인). D2 채택(`startup_validation.adopted: true`) 시 reference impl(`scripts/lib/infra_startup_validator.py`)은 미설정 required 를 첫 business 동작 이전 부팅 거부한다(fail-closed, exit 78 EX_CONFIG). 즉 "마찰 0"은 D2 미채택 상태의 성질이지 startup 대조가 fail-open 이라는 뜻이 아니다.

**write boundary**: SCHEMA(본 문서) = wrapper 소유 / VALUES(실 자원 맵) = **consumer-authored only**(§4b write 금지 invariant — `health_checks`/`db_probes`/`version_pin` 동형). wrapper-self dogfood 선언(`.claude/_overlay/project.yaml infra_resources:`)은 wrapper 가 자기 자원의 consumer 로서 author 한다(CFP-1 self-application).

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

### `frontend` 섹션 설명 (CFP-2505 / [ADR-136](../archive/adr/ADR-136-frontend-quality-gate-standard.md))

frontend 품질게이트(D1 구조적 CSS lint + D2 UI 실렌더 검증)의 authoritative 활성 source. `aggregate_arch` 섹션과 동형(선택필드 + 안전 default + additive-only + 미주입 비차단)이나 **default 방향이 반대**다. 1 field — `applicable` (CONDITIONAL 게이트 활성).

- **`frontend.applicable`** (선택, bool, **default `false`** — 안전 방향): frontend 품질게이트 활성 여부. `aggregate_arch.applicable`(default `true`) 와 default 방향이 반대인 이유 = 대다수 consumer(backend/lib/CLI-only)가 frontend 부재 → false 가 안전·보편 default (aggregate 는 "RDB 가 있다" 가 보편이라 true — ADR-136 결정2 명시).
  - `true` — frontend-bearing consumer. D1 CI 게이트(`css-lint.yml`) + D2 §8.7 UI 실렌더 검증 활성. 설계 lane 진입 시 UI/CSS 변경 PR 의 change-plan §8.7 본문 required.
  - `false` 또는 미주입 — frontend 무관 → 게이트 PASS(비차단), §8.7 N/A. 비-frontend consumer 무손상(additive).
- **2-layer 분리** (RefactorAgent interface separation, ADR-136 결정2): `frontend.applicable` = **authoritative gate**(D1/D2 공용 런타임 활성 여부) ⊥ whitelist(`consumer_applicable_workflows.txt`) membership = **eligibility**(css-lint.yml 이 consumer 에 배포될 자격). 두 layer 충돌 시 우선순위 = **flag authoritative** (ADR-130 §결정1 positive whitelist 와 정합 — whitelist 등재가 배포 자격, flag 가 런타임 활성).
- **미정의 시 동작**: `frontend` 섹션 자체가 없으면 default `false` 적용 → 게이트 비활성 + §8.7 N/A. codeforge wrapper 강제 안 함 (consumer 자율). 미주입 비차단 → 신규/기존 비-frontend consumer onboarding 마찰 0.
- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 field write 금지 (§4b write 금지 invariant 절대 보존). D1/D2 게이트 = read-only (consumer overlay value 를 spawn-time 활성 판정 입력으로 수신).

### `venue` 섹션 설명 (CFP-2504 / [ADR-006 Amendment 1](../archive/adr/ADR-006-testcontract-architect.md))

외부 venue/시계열 데이터 형상 재현 fidelity 게이트(§8 Test Contract 에 형상 재현 선언 또는 N/A anchor presence CI lint)의 authoritative 활성 source. `frontend` 섹션과 **완전 동형**(선택필드 + 안전 default false + additive-only + 미주입 비차단 + 2-layer 분리). 1 field — `applicable` (CONDITIONAL 게이트 활성).

- **`venue.applicable`** (선택, bool, **default `false`** — 안전 방향): 외부 venue/시계열 형상 재현 fidelity 게이트 활성 여부. `frontend.applicable`(default `false`) 와 default 방향이 같은 이유 = 대다수 consumer(내부 결정론 / 메모리-only / venue 무관 backend·lib·CLI)가 외부 거래소 venue·tick·WS stream·snapshot·candle 시계열을 touch 하지 않음 → false 가 안전·보편 default (venue-touching 은 mctrader 류 거래 consumer 한정 — ADR-006 Amendment 1 §A1-7 명시).
  - `true` — venue-touching consumer. `venue-shape-fidelity-presence-check.yml` CI lint 활성 → docs/stories/*.md §8 Test Contract 에 형상 재현 선언(captured-golden / 실형상-justified fixture) 또는 명시적 N/A(venue 미접촉 사유) anchor 부재 시 warning emit (continue-on-error 비차단, ADR-060 첫 도입 warning-tier).
  - `false` 또는 미주입 — venue 무관 → 게이트 no-op PASS(data-absence fail-open, 비차단). 비-venue consumer 무손상(additive).
- **2-layer 분리** (RefactorAgent interface separation, ADR-136 동형): `venue.applicable` = **authoritative gate**(lint 런타임 활성 여부) ⊥ whitelist(`consumer_applicable_workflows.txt`) membership = **eligibility**(`venue-shape-fidelity-presence-check.yml` 이 consumer 에 배포될 자격). 두 layer 충돌 시 우선순위 = **flag authoritative** (ADR-130 §결정1 positive whitelist 와 정합 — whitelist 등재가 배포 자격, flag 가 런타임 활성). flag false/미주입 consumer 는 workflow 가 배포돼도 lint 가 내부 no-op PASS.
- **anchor-presence 한정 (synthetic-detection scope-out)**: 본 lint 는 §8 에 형상 재현 anchor(선언 또는 N/A) 의 **존재** 만 검출한다. "fixture 가 합성인지(균일 +1 seq·고정 interval) 자동판정"은 본질적 fuzzy(의미 추론 요구) → scope 외 (ADR-006 §A1-8 / ADR-119 검사연극 금지). "올바른 형상인가" 실 검증은 Phase 1 review channel(설계리뷰 P0 + code-review fixture 형상 실재현)이 담당 — 본 lint 는 §8 선언 누락만 잡는 review-독립 보강 layer.
- **미정의 시 동작**: `venue` 섹션 자체가 없으면 default `false` 적용 → 게이트 no-op + §8 anchor 검사 비대상. codeforge wrapper 강제 안 함 (consumer 자율). 미주입 비차단 → 신규/기존 비-venue consumer onboarding 마찰 0. wrapper self = venue 무관(plugin-meta) → 본 섹션 미주입 = 항상 N/A(ADR-005 `plugin-meta-na`, A1-7).
- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 field write 금지 (§4b write 금지 invariant 절대 보존). lint 게이트 = read-only (consumer overlay value 를 CI-time 활성 판정 입력으로 수신).

### `story_stakes` 섹션 설명 (CFP-2432 / [ADR-042 Amendment 16](../archive/adr/ADR-042-agent-model-selection-policy.md))

> [DEAD — ADR-141] story_stakes 조건부 tier 는 폐지됨 (전 에이전트 opus 단일 tier). 본 섹션 은 역사 참고용.

Story-shape 조건부 model tier 의 consumer overlay 영역. 같은 agent role(Amd16 = InfraOperationalArchitectAgent / Amd17 = DomainAgent)의 model tier 를 Story 의 **stakes(결과 위험)** 로 분기한다 — `tier = f(mandate depth, stakes)`. stakes 는 mandate depth 와 orthogonal 축이므로 ADR-042 §결정2 invariant("Sonnet 으로 fully cover 가능 = role 결손 신호")와 양립한다 (low-stakes shape 에서 safety 핵심축이 물리적 dormant → 같은 depth 가 sonnet 으로 cover).

- **DomainAgent financial-invariant-0 (CFP-2445 / [ADR-042 Amendment 17](../archive/adr/ADR-042-agent-model-selection-policy.md))**: DomainAgent sonnet flip 조건 = **(4-AND low-stakes) AND (financial-invariant-0 shape)** 2-predicate AND. financial-invariant-0 = stakes 4-AND 와 **orthogonal 한 financial-correctness 결과접촉 축**(별 predicate `STAKES_FINANCIAL_INVARIANT_ZERO`) — 그 Story 에서 DomainAgent 가 백테스트 결과 숫자(equity/PnL/position/체결가/universe/파라미터)를 생성·변형·해석하지 않을 때만 표면이 0. 판정은 wrapper Orchestrator 의 **spawn-전 외부 shape 판정**(§1 사용자 원문 + directive 경로 키워드 — consumer 자기보고 아님). 4-AND false(live API/실자금 등) 또는 financial-invariant-0 false(결과 접촉) 또는 미상 → opus(fail-safe). `conservative_override` 에 `DomainAgent` 추가로 financial-invariant-0 shape 라도 항상 opus 유지 선언 가능(확장-only).

- **`story_stakes.conservative_override`** (선택, list of agent name): 나열된 agent 를 항상 opus 로 강제 (보수 방향). 확장-only 정합 — **항상 허용**. consumer 가 "이 agent 는 우리 프로젝트에선 low-stakes Story 라도 opus 유지" 를 선언하는 채널.
- **down-tier 금지 (확장-only enforcement, ADR-127 §결정6 / AC-3)**: consumer 는 tier 를 **보수 방향(opus 강제)으로만** override 가능. down-tier(opus→sonnet) 공격적 override 는 **불가** — `tier_override` 맵에 wrapper floor 미만 tier(예: InfraOperationalArchitectAgent: sonnet, floor=opus) 를 지정하면 **2중 enforcement** 가 거부:
  1. **schema-gate** — bootstrap strict-check (`overlay/hooks/check_bootstrap.py` check 11 / strict (f)) 가 down-tier 검출 → strict mode exit 1 (default mode WARN).
  2. **spawn-time clamp** — `scripts/check-stakes-tier-gating.sh` 의 `max(wrapper_floor, overlay)` 가 약한 요청 무시 + stderr 거부 로그.
- **4 stakes 신호 소스 ownership (F-2)**: Story 메타 = shape 사실(실자금/cutover/신규경계/live API 여부, wrapper Orchestrator 가 4-AND 판정). project.yaml `story_stakes` = consumer 의 보수 override 채널만(shape 사실 자기보고 아님 — Spoofing 차단). 최종 tier precedence = `max(wrapper_floor, overlay)`(보수 우선), 미상/파싱불가 = 보수 opus(fail-loud).
- **low-stakes 판정 (wrapper 정책 — consumer overlay 무관)**: low_stakes := 실자금 없음 ∧ production cutover 없음 ∧ 신규 신뢰경계 없음(5-enum 0건) ∧ live 외부 API 호출 없음(read-only 시세 포함). 4-AND 모두 충족 시 sonnet, 하나라도 high → opus(high-absorbing). 누락 → opus(fail-safe).
- **미정의 시 동작**: `story_stakes` 섹션 자체가 없으면 모든 agent 현행 tier(wrapper floor) 유지 — 파괴적 변경 0(optional, 부재=현행). codeforge wrapper 강제 안 함.
- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 field write 금지 (§4b write 금지 invariant 절대 보존). wrapper Orchestrator = read-only (overlay value 를 spawn-time clamp 입력으로 수신).

### `deploy` 섹션 설명 (CFP-1059 / [ADR-087](../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md))

> **DEPRECATED — 배포 완전 위임 ([ADR-121](../archive/adr/ADR-121-deprecate-deploy-lanes.md) §결정 5, CFP-2228)**
>
> - 본 `deploy.*` block 전체는 deploy / deploy-review 2 lane 폐지에 따라 **Deprecated** 상태다. **sunset = 2026-07-13 (KST)** (ADR-121 §결정 A — D-day + 1 calendar month). **필드 물리 제거 = Epic [#2217](https://github.com/mclayer/plugin-codeforge/issues/2217) S5** (sunset gate 경과 실측 후) — 본 시점 삭제 0, 아래 5 mandatory + 4 optional nested 필드 서술·yaml 예시는 이력 보존.
> - **대체 모델 — `deploy.github_environments` 위임 stub**: 배포 설정은 더 이상 project.yaml `deploy.*` 가 아니라 **consumer repo GitHub Actions workflow + GitHub Environments (dev/stg/prd)** 로 위임한다 (ADR-121 §결정 2·3). stg→prd promote = Environments **required reviewers** 승인 게이트. smoke 검증 = consumer workflow post-deploy job 환원 (ADR-121 결정 8).
> - **seed 템플릿**: `templates/github-workflows/consumer-deploy-seed.yml` + `templates/github-workflows/post-deploy-smoke.yml` — **Epic #2217 S3 merge 후 활성** (본 배너 작성 시점 origin/main 미존재, forward reference — S3 와 병렬 진행 중).

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
  jira:                              # CFP-2285 원격 채널 (opt-in). 미설정/enabled:false = no-op.
                                     # 채널 runtime 은 addCommentToJiraIssue 1종만 사용 (ADR-099 §A1-1).
                                     #   이슈 생성(createJiraIssue)·status 전이(transitionJiraIssue) 는 deny
                                     #   → control/mirror 이슈는 운영자가 사전 생성한다.
    decision_channel:                # Arc A 비동기 결정 채널(입력/HITL). 결정 fork 를 Jira 로 라우팅
      enabled: <bool>                # true = 판단-기반 라우팅 활성
      cloud_id: <string>             # Atlassian cloudId (getAccessibleAtlassianResources)
      control_project_key: <string>  # 결정 채널 Jira 프로젝트 key (비공개·단일 운영자 권장 — ADR-099 §A1-3 신뢰가정)
      control_issue_key: <string>    # 운영자 사전 생성한 control 결정 이슈(assignee=운영자=native notify). 결정을 이 이슈 코멘트로 post
      issue_type: <string>           # 결정 이슈 타입(있으면). 예: "작업"
      notify: assignee | watcher     # Jira native 알림 (assignee 또는 watcher)
      timeout_minutes: <int>         # 미응답 재알림(escalation) 임계. 예: 1440 = 24h
      escalation: { intervals_minutes: [<int>, ...] }   # 재알림 점증 스케줄(분). 예: [60, 240, 1440]
      auto_decide_on_timeout: false  # 박제 — timeout 도달해도 자동결정 절대 금지(결정은 끝까지 운영자 몫)
    progress_mirror:                 # Arc B 세션·작업 모니터링(출력, write-only, comment-only)
      enabled: <bool>                # true = 진행 미러 활성 (opt-in, 기본 off)
      project_key: <string>          # 진행 미러 대상 control project (decision_channel 과 같은 project 공유 가능)
      cloud_id: <string>             # Atlassian cloudId (decision_channel 과 공유 가능)
      mirror_issue_key: <string>     # 운영자 사전 생성 모니터링 이슈(빈값=no-op). 진행을 코멘트로 미러
      current_activity: pinned-comment-update   # "현재 무엇 하는중" 1줄 = 단일 코멘트 update 방식

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

# [선택] Cross-repo 책임 배치 토폴로지 SSOT (CFP-2419 / [ADR-131](archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md), Epic CFP-2418)
# default = applicable: false (미주입 → 메타불변식 게이트 PASS — frontend-only/단일레포 consumer 비차단)
# wrapper 는 메타불변식(구조적 사실)만 강제, 구체 "어느 레포가 무엇" 맵은 consumer overlay 가 주입 (Nx @nx/owners 컴파일 모델 — 선언=프로젝트단위/강제=파일단위, source: Nx Enterprise @nx/owners. 개념 인용·채택 도구 아님)
repo_topology:
  applicable: <bool>                 # default false. false (또는 미주입) → 메타불변식 게이트 PASS (비차단).
                                     # true = 멀티레포 consumer 가 책임 배치 맵 주입 → wrapper 메타불변식 검사 대상.
                                     # "정책값 공백 = PASS" 는 ADR-130 fail-closed(unknown=exit 1)와 다른 LAYER — wrapper 구조검증 vs consumer 정책 opt-in (ADR-131 §결정2).

  responsibilities:                  # applicable=true 시 per-consumer 책임 배치 맵 (배열). 각 항목 = 1 책임.
                                     # wrapper 는 스키마 유효성(아래 3 필수 필드 존재)만 mechanical check. 맵 내용(어느 레포가 옳은가)은 검사 안 함 (의미 판정 = 리뷰어 attestation, ADR-131 §결정4).
    - responsibility: <string>       # required, 책임 식별자 (예: "risk-metrics-sharpe-mdd", "order-execution")
      owner_repo: <string>           # required, 소유레포 (예: "mclayer/mctrader-engine"). 메타불변식: 정확히 1개 (0/N≥2 = 위반).
      rationale: <string>            # required, 배치 근거 (왜 이 레포가 소유하나 — 도메인 귀속 서술)
      linked_artifact:               # required, ≥1 — 연결 작업단위/ADR/change-plan 링크 (배치 결정 추적성)
        - <string>                   # e.g. "CFP-2418" / "ADR-131" / "wrapper/change-plans/cfp-2419-...md" — 최소 1개 필수

  # ── 신설 (L1 코드→책임) — CFP-2428 / ADR-131 Amendment 1 (Epic CFP-2418 deferred FU) ──
  responsibility_markers:            # [선택] applicable=true 시 per-repo 코드→책임 마커 manifest (배열).
                                     # 미주입/빈 = PASS (fail-open, L2 responsibilities[] 동형). consumer-authored, wrapper write 0.
                                     # join-key = responsibility (아래) ↔ repo_topology.responsibilities[].responsibility byte-identical 동일 namespace.
    - path: <string|glob>            # required, 경로 또는 모듈 glob (예: "engine/src/risk/**", "packages/order/*").
                                     #   파일별 *언어 주석* 아님 — per-repo 구조화 매핑 (polyglot-safe, AC-5).
      responsibility: <string>       # required, join-key — repo_topology.responsibilities[].responsibility 와
                                     #   byte-identical 동일 namespace 의무 (AC-1). 의미 내용 검사 안 함 (구조 대조만).
      repo: <string>                 # [선택] 이 마커가 속한 레포 (예: "mclayer/mctrader-engine"). 미지정 시
                                     #   불일치(b) 검사 비대상(역방향 추론 안 함). 지정 시 topology.owner_repo[R] 와 문자열 대조.
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

### `repo_topology` 섹션 설명 (CFP-2419 / [ADR-131](../archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md), Epic CFP-2418)

Cross-repo **책임 배치(responsibility placement)** 토폴로지 SSOT 의 consumer overlay 영역. 멀티레포 consumer(예: mctrader 14 repo)에서 "어느 레포가 무슨 책임을 소유하는가"를 1급 산출물로 격상한다(ADR-131 §결정1). wrapper 는 **메타불변식(구조적 사실)만 강제**하고, 구체 "어느 레포가 무엇" 맵은 consumer overlay 가 주입한다 — `branch_protection.applicable` / `aggregate_arch.applicable` 와 동형 overlay 주입 패턴 (ADR-083 consumer-applicability filter framework instance). 본 섹션은 **Phase 1 declarative-only** — 실 메타불변식 hard-block 검사 스크립트는 Story 2, story-init.yml 라우팅 자동화는 Story 3 carrier (검사 스크립트·required check 0 신설 — 회귀 0 차단).

- **`repo_topology.applicable`** (선택, bool, default `false`): 책임 배치 토폴로지 거버넌스 활성화 여부.
  - **`false`** (default, 또는 섹션 미주입) — 메타불변식 게이트 **PASS** (비차단). frontend-only / 단일레포 consumer 무손상 (EC-1).
  - **`true`** — 멀티레포 consumer 가 `responsibilities[]` 맵을 주입 → wrapper 메타불변식 검사 대상.

- **`repo_topology.responsibilities`** (조건부 의무, array): `applicable=true` 시 per-consumer 책임 배치 맵. 각 항목 = 1 책임. 각 항목 필수 3 필드:
  - **`responsibility`** (required, string) — 책임 식별자.
  - **`owner_repo`** (required, string) — 소유레포. 메타불변식 ① **정확히 1개**(0개 = 주인없는 책임 위반 / N≥2 = 중복소유 위반).
  - **`rationale`** (required, string) — 배치 근거(왜 이 레포가 소유하나 — 도메인 귀속 서술). 의미 판정 attestation 의 근거 텍스트.
  - **`linked_artifact`** (required, array, **≥1**) — 연결된 작업단위/ADR/change-plan 링크 1개 이상 필수(배치 결정 추적성). 0개 = 스키마 무효(메타불변식 ④ 위반).

- **4 메타불변식** (wrapper 강제 대상 — ADR-131 §결정2): ① 모든 책임 정확히 1 소유레포 ② 주인없는 책임 0 ③ 중복소유 0 ④ SSOT 파일 존재 + 스키마 유효. wrapper 는 **구조의 유효성**(위 3 필수 필드 존재 + 4 메타불변식)만 검사하고 **맵 내용**("이 레포가 *의미상* 옳은가")은 검사 안 한다 — 의미 판정 = 리뷰어 근거인용 attestation 요구만(승인 자체는 대신 판단 안 함, 검사연극 금지 ADR-119 정합, ADR-131 §결정4).

- **layer 분리** (ADR-131 §결정2 verbatim): **"정책값 공백 = PASS"** 는 [ADR-130](../archive/adr/ADR-130-applicability-closure-integrity.md) 의 **fail-closed(`unknown` = exit 1)** 와 **다른 LAYER** 이다. ADR-130 fail-closed = *wrapper 구조 검증* layer(미분류 자산 안전 차단), `repo_topology` 의 "공백 PASS" = *consumer 정책값 미주입* layer(opt-in 무손상). `applicable=true` 후 `responsibilities[]` 를 비워도 스키마 유효성만 검사하되 정책 내용 공백은 PASS (EC-2). 모순 아님.

- **미정의 시 동작**: `repo_topology` 섹션 자체가 없으면 default 적용(`applicable: false`). codeforge wrapper 강제 안 함(consumer 자율 — backward-compat invariant). 기존 consumer overlay 영향 0 (additive only — schema rule §1.1 선택 필드 추가, 기존 mctrader/webapp overlay 무손상).

- **유지보수 루프 (변경시점 고아검사)**: 책임을 추가/이동하는 변경은 `repo_topology.responsibilities[]` 갱신을 필수로 한다(새 책임 = SSOT 등재 강제) → SSOT 가 stale prose 로 썩는 것 방지(거짓 GREEN 차단, UC-3). 실 고아검사 hard-block = Story 2 carrier.

- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 block write 금지 (§4b write 금지 invariant 절대 보존). 토폴로지 SSOT *스키마 문서*(본 섹션) author = ArchitectAgent(chief, ADR-131 §결정1 — repo-level 배치 1급 author), 그러나 consumer 의 *실 값*(`responsibilities[]` 맵)은 consumer overlay 가 작성 — wrapper agent 는 값 write 0 (메타불변식 게이트 = read-only compare-only).

- **ADR-131 framework cross-ref**: ADR-131 = cross-repo 책임 배치 거버넌스 모델 SSOT (토폴로지 SSOT 1급화 + 메타불변식 게이트 계약 + 기계/사람 판정 분리). 본 `repo_topology` 스키마는 그 모델의 schema-specific instance — overlay 주입형 책임 배치 맵 영역 특화 (vs `branch_protection.applicable` = branch protection 영역 / `aggregate_arch.applicable` = aggregate boundary 영역). disjoint scope — 같은 axis 아님.

### `responsibility_markers` 섹션 설명 (CFP-2428 / [ADR-131](../archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md) Amendment 1, Epic CFP-2418)

`repo_topology` 하위 **declared-marker layer(L1 코드→책임)** 의 consumer overlay 영역. CFP-2422 가 신설한 메타불변식 게이트(L2 책임→레포)의 **sibling layer** — 멀티레포 consumer 가 "이 경로/모듈은 무슨 책임을 구현하는가"를 per-repo 구조화 산출물(marker manifest)로 선언하면, 그 선언이 상위 토폴로지(L2 `responsibilities[]`) 및 실제 파일시스템(L3)과 **transitive 일관성**을 유지하는지 wrapper 가 *구조적으로만* 대조하고 위반 3종을 **warning-tier(continue-on-error 비차단)** 로 surface 한다. **의미 추론 0 / hard-block 0 / 파일별 어노테이션 0** (Story §1 verbatim MVP invariant). 외부 6도구(ArchUnit·Nx tags·Bazel·CODEOWNERS·dependency-cruiser·CodeQL) 전부 책임 *자율 귀속* 0 — 따라서 "의미단위 깊은 검증" = (불가능한)의미 추론이 아니라 **선언마커(L1)↔토폴로지(L2)↔실제 위치(L3) transitive 일관성 + drift 검출**.

- **`repo_topology.responsibility_markers`** (선택, array): `applicable=true` 시 per-repo 코드→책임 마커 manifest. 각 항목 = 1 마커 entry. 필수 2 필드 + 선택 1 필드:
  - **`path`** (required, string|glob) — 경로 또는 모듈 glob (예: `"engine/src/risk/**"`, `"packages/order/*"`). 파일별 *언어 주석* 아님 — per-repo 구조화 매핑(polyglot-safe, Rust+Python+TS 단일 주석문법 부재 + 유지보수 폭발 회피, AC-5).
  - **`responsibility`** (required, string) — **join-key**. `repo_topology.responsibilities[].responsibility` 와 **byte-identical 동일 namespace** 의무(AC-1). 의미 내용("이 경로가 정말 그 책임이냐")은 검사 안 함 — 구조적 set 대조만.
  - **`repo`** (선택, string) — 이 마커가 속한 레포 (예: `"mclayer/mctrader-engine"`). 미지정 시 불일치(b) 검사 비대상(역방향 추론 안 함 — 의미추론 회피). 지정 시 `topology.owner_repo[R]` 와 문자열 동등 대조.

- **drift 3종 (warning-tier — continue-on-error 비차단)**:
  - **(a) unmarked** — L2 책임 R 이 L1 manifest 에 entry 0 (set-diff `{topology.responsibilities} − {markers.responsibility} ≠ ∅`) → exit 1.
  - **(b) marker↔topology 불일치** — `repo` 지정된 entry 의 `marker.repo ≠ topology.owner_repo[marker.responsibility]` (문자열 동등) → exit 1.
  - **(c) stale marker** — manifest entry `path`/glob 이 fs 에 부재 (`os.path.exists` / `glob.glob` 매칭 0건) → exit 1. offline-first(fs only, gh 0).
  - manifest→topology **역방향 고아**(manifest 에만 있고 topology 에 없는 R) = informational `::notice::` 만(warning 아님, drift 카운트 0 — micro-decision ③).

- **exit 매트릭스 (falsifiable, L2 게이트 동형 5상태)**: `responsibility_markers` 미주입 = **exit 0**(fail-open PASS + honest `::notice::`) / `applicable != true` = **exit 0** / `applicable:true` + 빈 맵 = **exit 0**(스키마 유효성만) / manifest **malformed**(`path`/`responsibility` 키 부재·yaml 파싱 실패) = **exit 2**(setup-error fail-closed) / drift 위반(a/b/c 1+) = **exit 1**(warning, continue-on-error 라 merge 비차단).

- **layer 분리** (ADR-131 §결정2 동형): 공백/미주입/`applicable:false` = **PASS**(consumer 정책 미주입 layer, ADR-130 fail-closed 와 다른 LAYER). frontend-only/단일레포/marker 미도입 consumer 비차단.

- **미정의 시 동작**: `responsibility_markers` 부재 = default 미주입 = PASS. additive only (schema rule §1.1 선택 필드 추가, 기존 mctrader/webapp overlay 무손상 — backward-compat invariant).

- **write boundary**: consumer-authored. 모든 codeforge agent 는 본 block write 금지 (§4b write 금지 invariant 절대 보존). marker manifest *스키마 문서*(본 섹션) author = ArchitectAgent(chief), 그러나 consumer 의 *실 값*(`responsibility_markers[]` 맵)은 consumer overlay 가 작성 — wrapper agent 는 값 write 0 (drift 게이트 = read-only compare-only).

- **L1↔L2 disjoint**: 본 marker layer(L1 코드→책임)는 CFP-2422 메타불변식 게이트(L2 책임→레포)와 **검사 명제 비중첩** — L2 는 책임의 *소유레포 유일성*(고아/중복/거친파생)을 강제하고, L1 은 *코드 위치 정합*(unmarked/불일치/stale)을 surface. 같은 `repo_topology` 부모 + 같은 `responsibility` join-key 를 공유하나 검사 layer disjoint.

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
  daemon_type: request_response_service   # FastAPI HTTP 서비스 — soak 미대상 (health_checks HTTP-200 default 유지)
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

**통합테스트 설정 예시 — mctrader-collector (long_running_daemon + sink-advance soak)**:

지속-liveness soak 게이트(G2, [ADR-148](../archive/adr/ADR-148-persistent-liveness-soak-gate.md)) 대상 상주 데몬. `daemon_type: long_running_daemon` 선언 시 `sink_probes[]` presence 필수 (부재 = fail-closed). soak 판정 = 프로세스 생존(exit==0 ∧ RestartCount==0) ∧ terminal-sink monotone 전진 — HTTP-200 아님.

```yaml
integration_test:
  daemon_type: long_running_daemon          # 상주 collector 데몬 — 지속-liveness soak 게이트 scope
  docker_compose_test_path: infra/docker-compose.collector-test.yml

  required_env_keys:
    - DATABASE_URL
    - BITHUMB_WS_URL

  sink_probes:
    - name: committed_ticks                 # terminal sink = DB 적재 종점 (outcome ground-truth)
      probe_type: sink-advance
      metric_command: "psql $DATABASE_URL -tAc 'SELECT count(*) FROM ticks'"  # monotone 값 1개 반환
      boot_grace_seconds: 30                 # 느린 부팅 유예 (ceiling ≤ soak/2)
      threshold: 1000                        # manifestation-derived 조기 PASS (선택): ≥1000 ticks 적재 시 floor 만료 전 종료
      duration_floor_seconds: 1800           # soak 창 max horizon / deadline ceiling (항상 필수) — threshold 미도달 시 1800s timeout
      manifestation_trigger_type: volume
      poll_interval_seconds: 5
```

## 4. 에이전트 접근 규칙

### 4a. Read 전담
- **DocsAgent**: GitHub Issue/PR/comment·repo file write 시 `org`·`repo`·`story_key_prefix`·`codeowners`·`milestone.epic_naming_pattern` 활용
- **RequirementsPLAgent**: Story SSOT 파일(`docs/stories/<KEY>.md`) 위치 결정 시 `story_key_prefix` 사용. **Multi-repo system 활성 시** (CFP-342 / ADR-069) `codeforge.stories.repos[]` 검사 → hub vs repo story 결정 + target repo 결정 (frontmatter `story_scope` priority 1, `component` label fallback)
- **DomainAgent**: Domain Knowledge 트리(`docs/domain-knowledge/`) read + Discussions 질의 시 `discussions.domain_kb_category` 사용
- **PMOAgent**: 회고·Cross-Story 패턴 분석 시 GitHub Issue search query에 `org`·`repo` 활용
- **All lane plugin agents**: **Multi-repo system 활성 시** (CFP-342 / ADR-069) `codeforge.stories.repos[].path` + `components` 활용해 작업 target repo 결정 (priority: frontmatter `story_scope: repo` + `repo` → `story_scope: hub` → `component` label mapping → ESCALATE)
- **Orchestrator**: 세션 개시 시 1회 read → 필요 값 Context Packet으로 하위 에이전트에 전달 (반복 fetch 회피). 매 변경 시작 시 **모든 변경 = Story 작성 의무**(chore 면제 폐지 — ADR-127 §결정 1). `story_cutoff.additional_exempt_categories` 면제 입력 사용 폐지(deprecated — ADR-127 §결정 6). **Multi-repo system 활성 시** Project Config Packet 에 `codeforge.stories.repos[]` slice 포함 의무

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
