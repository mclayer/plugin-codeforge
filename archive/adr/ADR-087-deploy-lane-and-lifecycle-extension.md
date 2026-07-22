---
adr_number: 87
title: Deploy lane 신설 — codeforge-deploy plugin 정식 도입 + lane lifecycle 6→8 단계 확장
status: Superseded by ADR-121
category: lifecycle
date: 2026-05-20
carrier_story: CFP-1059
parent_epic: CFP-1059
related_stories:
  - CFP-1059  # carrier Epic
  - CFP-1808  # Amendment 2 — Phase 2 wire activation (deploy-lane-presence 6번째 required check + 2 plugin phase-gate-mergeable.yml 신설 + deploy-lane-presence.yml 신설). Wave 1 declarative + immediate wire atomic (HIGH risk 영구 차단 회피 mandate, declaration-only Wave 1 패턴 적합 영역 외).
related_adrs:
  - ADR-023  # lane plugin lifecycle (Amendment N 동반 — 8 lane 확장 절차)
  - ADR-042  # agent model selection (Amendment 9 동반 — DeployPL/Worker tier)
  - ADR-026  # post-merge automation (Amendment N 동반 — Epic close → Deploy trigger)
  - ADR-063  # marketplace atomic invariant (Amendment N 동반 — 7→9 plugin family)
  - ADR-027  # consumer adoption (Amendment N 동반 — project.yaml deploy.* schema)
  - ADR-014  # operational risk SSOT (Amendment N 동반 — InfraOperationalArch ↔ DeployPL boundary)
  - ADR-088  # Deploy Review lane (sibling carrier within CFP-1059)
  - ADR-089  # Schema 변경 7 원칙 (sibling carrier within CFP-1059)
  - ADR-090  # Cross-layer 참조 정책 (sibling carrier within CFP-1059)
  - ADR-068  # I-5 dimensional empirical grounding (3-시간 보존 / blue-green swap window 측정 의무)
  - ADR-054  # doc-only fast-path (본 carrier Story-1 적격 — code/test/security review skip)
  - ADR-076  # declarative reconciliation (expand-contract pattern 동형 ratchet)
  - ADR-082  # write-time self-write verification (본 ADR self-write evidence enumeration 정합)
  - ADR-070  # Codex verify-before-trust (chief author direct write precedent)
  - ADR-040  # worktree convention + Amendment 3 mechanical_enforcement_actions[] frontmatter 의무
related_files:
  - docs/adr/ADR-023-lane-plugin-lifecycle.md
  - docs/adr/ADR-042-agent-model-selection-policy.md
  - docs/adr/ADR-026-post-merge-automation.md
  - docs/adr/ADR-063-marketplace-atomic-invariant.md
  - docs/adr/ADR-027-consumer-adoption-protocol.md
  - docs/adr/ADR-014-operational-risk-ssot-distribution.md
  - docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md
  - docs/adr/ADR-089-schema-change-7-principles.md
  - docs/adr/ADR-090-cross-layer-reference-policy.md
  - CLAUDE.md  # Development Agent Team / 필수 플러그인 / 레인 단계 정의 / Lane 진입 skill 표 갱신
  - docs/orchestrator-playbook.md  # 8 lane spawn order
  - templates/github-workflows/auto-deploy.yml  # Epic close → Deploy trigger workflow (Phase 1 skeleton)
amendment_log:
  - amendment_number: 1
    date: "2026-05-23"
    carrier_story: CFP-1317-S1
    description: "stateful daemon BG-1~4 비적격 기준 형식화 (§결정 5 §5.2 표 4 row append, OR semantic) + 보조 배포 매커니즘 rolling/writer-lease sub-domain 정식화 (신규 §결정 9 신설, chief tie-break ladder result 타협안 채택 — single enum primary `deploy_strategy: blue-green|rolling|writer-lease` + secondary annotation `eligibility_reason: BG-N enum`) + §결정 5 wording 정정 (\"blue-green 단일 매커니즘 고정\" → \"primary blue-green + BG-1~4 비적격 시 보조 매커니즘 (§결정 9)\") + EC-G concurrent deploy + rollback race serialization (§9.5) + EC-H 기존 consumer migration path default blue-green (§9.6). mctrader#1272 escalation (a)+(b) 흡수."
    sunset_justification: null  # strengthening direction (scope 확장 — 보조 매커니즘 sub-domain 추가, 약화 0건). ADR-058 §결정 5 정합.
    related_files:
      - docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
      - docs/domain-knowledge/domain/deployment-mechanism/stateful-daemon-bg-eligibility.md
      - docs/domain-knowledge/domain/deployment-mechanism/single-writer-fencing-pattern.md
amendments:
  - number: 1
    date: "2026-05-23"
    carrier_story: CFP-1317-S1
    description: "§결정 5 stateful daemon BG-1~4 비적격 기준 형식화 + 신규 §결정 9 (rolling/writer-lease 보조 매커니즘) + §결정 5 wording 정정 + EC-G/H 흡수"
    sunset_justification: null
  - number: 2
    date: "2026-05-29"
    carrier_story: CFP-1808
    description: "Phase 2 wire activation — deploy-lane-presence 6번째 required check 활성 (본 repo main 보호 contexts 5→6 ratchet) + 2 plugin repo (codeforge-deploy / codeforge-deploy-review) phase-gate-mergeable.yml workflow 신설 (HIGH risk 영구 차단 회피 — 부재 시 plugin PR merge 영구 pending). deploy-lane-presence.yml workflow 신설 (templates/ + .github/workflows/ self-app per ADR-005 byte-identical). auto-deploy.yml + deploy-lane-spawn-evidence.yml workflows 이미 활성 — 본 Amendment 안 cross-ref declarative declare only. ADR-088 (배포 리뷰 lane) cross-ref backref 의무. ADR-058 §결정 5 ratchet 강화 only (5→6 contexts, 영구 차단 회피) — 약화 / scope 축소 / 면제 영역 0건. parent CFP-1785 retro F-D HIGH carrier (parallel session CFP-1785 종결 후 audit 결과 발견)."
    sunset_justification: null  # strengthening direction (Phase 2 wire activation, contexts 5→6 ratchet, 2 plugin sibling sync 의무 — HIGH risk 영구 차단 회피 mandate). ADR-058 §결정 5 정합 (약화 0건).
is_transitional: false  # permanent lane structure — 약화 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null
mechanical_enforcement_actions:
  - deploy-lane-spawn-evidence  # declaration-only Wave 1 (ADR-070 / ADR-082 / ADR-086 precedent 답습)
  - deploy-lane-presence  # CFP-1808 Amendment 2 — Phase 2 wire activation. workflow self-app templates/ + .github/workflows/ byte-identical + 본 repo main 보호 contexts 5→6 ratchet + 2 plugin sibling phase-gate-mergeable.yml workflow 신설 (HIGH risk 영구 차단 회피 mandate).
---

# ADR-087 — Deploy lane 신설 (codeforge-deploy plugin 정식 도입 + lane lifecycle 6→8 단계 확장)

## 상태

`Accepted (2026-05-20 KST)` — CFP-1059 Epic Story-1 carrier (배포 lane + 배포 리뷰 lane 신설 sibling ADR 4종 중 하나). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. doc-only fast-path (ADR-054 Category 2) — code/integration test/security review skip.

## 컨텍스트

### 동인

사용자 발화 verbatim (CFP-1059 Epic body §1):

> "코드 개정 작업은 수행하고 있지만 배포 과정이 정립되어 있지 않다. 통합 테스트 이후 배포 과정을 추가하는게 어떤가"

> "배포 행위 자체 정립이다." (dominant motivation)

codeforge family 현재 = 6 lane plugin (`codeforge-{requirements,design,develop,test,review,pmo}`) + wrapper. 배포 행위 = 사용자의 application repo 가 통합 테스트 / 보안 테스트 통과 후 production 환경에 코드를 띄우는 단계. 이 단계가 codeforge 의 1st-class lane 으로 정립되지 않은 채 ad-hoc 으로 수행됨.

### Consumer 사례 (mctrader)

본 ADR 의 evidence anchor consumer = mctrader (5 repo: `mctrader-{market,market-bithumb,data,engine,web}`). 사용자 Epic 묶음 종료 후:

- 변경된 repo 만 (예: 5 repo 중 2 repo) 배포 의무
- blue-green + atomic swap + 3-시간 보존 + 자동 rollback 매커니즘
- consumer 자체의 schema migration (RDB Alembic / 빅데이터 expand script) 와 cross-layer 의존 순서 영역

### 기존 lane 과의 disjoint axis

- **codeforge-test (통합테스트 lane)** = code 정합 + 시나리오 단위 검증 (코드 행위 검증). 배포 lane 의 매커니즘 실행 (blue-green / atomic swap) 과 disjoint.
- **codeforge-review (보안테스트 lane)** = code-level 보안 정합 (취약점 / 인증 / 권한). production 환경 매커니즘 검증과 disjoint.
- **codeforge-pmo (Cross-cutting)** = Epic 창설 / 회고. 매 Epic 단위 자동 발동 영역 — 배포 trigger 의 channel 과 disjoint (ADR-026 post-merge automation 가 Story / PR 단위 vs ADR-087 가 Epic 단위).
- **codeforge-design (설계 lane) InfraOperationalArch deputy** = 운영 risk 상시 결정 (DR / Clock / Env / Container). 배포 매커니즘 실행 (blue-green / atomic swap / healthcheck) 과 disjoint axis (ADR-014 Amendment N 정합).

### 사용자 결정 (2026-05-20 KST)

CFP-1059 brainstorm Phase 1 dialog 결과:

- WHY 우선순위 (3-tier): WHY-1 (dominant) = 배포 행위 자체 정립 / WHY-2 = 성능 1st-class 검증 phase 격상 (ADR-088 carrier) / WHY-3 = 회귀 깊이 확장
- 배포 매커니즘 = blue-green + atomic swap + 3-시간 보존 + 자동 rollback (단일 매커니즘)
- 인프라 stack = Docker (다중 호스트) + GitHub Actions (빌드) + Docker Hub (저장) + SSH pull (배포) + 1Password Connect (비밀) + Traefik (traffic 분배)
- 배포 단위 = repo (consumer 묶음 Epic 안 변경된 repo 만)

## 결정

### §결정 1 — codeforge-deploy lane plugin 정식 신설

새 lane plugin `codeforge-deploy@mclayer` 신설. 8 lane composition:

| # | Lane | Plugin | Agent 수 | 기존/신설 |
|---|---|---|---|---|
| 1 | 요구사항 | `codeforge-requirements` | 7 | 기존 |
| 2 | 설계 | `codeforge-design` | PL + chief author + 5+3 SubAgent | 기존 |
| 3 | 설계리뷰 / 구현리뷰 / 보안테스트 | `codeforge-review` | 5 | 기존 |
| 4 | 구현 | `codeforge-develop` | 5 + preset | 기존 |
| 5 | 통합테스트 | `codeforge-test` | 1 | 기존 |
| 6 | **배포** | **`codeforge-deploy`** | **2 (DeployPL + DeployWorker)** | **신설 (본 ADR)** |
| 7 | **배포 리뷰** | **`codeforge-deploy-review`** | **2 (DeployReviewPL + DeployReviewWorker)** | **신설 (ADR-088)** |
| 8 | Cross-cutting | `codeforge-pmo` | 3 | 기존 |

본 ADR scope = #6 `codeforge-deploy` 신설만. #7 = ADR-088 sibling carrier.

**deploy lane scope = consumer 의 application repo 배포 영역** (codeforge plugin marketplace publish 와 disjoint — ADR-063 marketplace atomic invariant 가 그쪽 cover). wrapper / lane plugin 자체의 marketplace release 와 의미 혼동 차단.

### §결정 2 — DeployPLAgent + DeployWorkerAgent 2종 신설 (Sonnet tier)

| Agent | Model tier | Mandate |
|---|---|---|
| **DeployPLAgent** | Sonnet | 배포 매커니즘 실행 lead — Epic 묶음 단위 발동, 변경 repo 결정, blue-green sequence orchestration, healthcheck 검증, atomic swap trigger, 3-시간 보존 timer 설정, 자동 rollback 결정 |
| **DeployWorkerAgent** | Sonnet | 각 repo 배포 worker — idempotent script 실행, graceful shutdown 신호, healthcheck endpoint poll, secret provider lookup (1Password Connect 또는 fallback), reverse proxy label 갱신 (Traefik primary) |

ADR-042 Amendment 9 sibling carrier (DeployPL + DeployWorker + DeployReviewPL + DeployReviewWorker 4 agent tier 결정).

### §결정 3 — 배포 단위 = repo (consumer 묶음 Epic 안 변경된 repo 만)

- 1 Epic 묶음 = 1 ~ N repo 변경 가능 (consumer 영역). 변경 안 된 repo = 배포 skip.
- 변경 감지 = Phase 2 PR merge log + Epic close 시점 sync (post-merge-followup.yml workflow chain 확장 — ADR-026 Amendment N).
- mctrader 사례: 5 repo 중 손댄 것만 배포 (예: `mctrader-data` + `mctrader-engine` 만 변경 시 `mctrader-{market,market-bithumb,web}` skip).

### §결정 4 — 환경 단계 = consumer declare

- default 1 (`production`). consumer 가 `project.yaml deploy.environments: [<list>]` 으로 staging / canary 등 추가 가능 (ADR-027 Amendment N schema).
- 본 ADR scope = production 단일 default 정의. multi-env promotion 흐름 = Wave 5+ (별 carrier — 운영 phase 8 후보 중 canary promote).

### §결정 5 — 배포 매커니즘 = primary blue-green + BG-1~4 비적격 시 보조 매커니즘 (§결정 9)

**Amendment 1 (2026-05-23 KST, CFP-1317-S1)**: 본래 "blue-green 단일 매커니즘 고정" wording → "primary blue-green + BG-1~4 비적격 시 보조 매커니즘 (§결정 9)" 으로 정정. stateful daemon 영역에서 blue-green 가정이 깨지는 4 sub-pattern (BG-1~4) codify + 보조 매커니즘 sub-domain mapping = §결정 9 carrier.

#### §5.1 — primary blue-green 9-step (default mechanism)

| 단계 | 내용 | Empirical reference |
|---|---|---|
| 1 | 빌드 → Docker Hub push | GitHub Actions build + push (consumer 자체 workflow, codeforge 가 abstraction 만 제공) |
| 2 | 확장 (expand) 마이그레이션 apply | RDB layer: Alembic upgrade — AggregateArch 책임 / 빅데이터: custom expand script — DataArch 책임 (ADR-089 §결정 2 expand-contract 분리) |
| 3 | green 컨테이너 시작 | docker-compose 새 컨테이너 (new version tag), blue 유지 |
| 4 | 건강 확인 | healthcheck endpoint `/healthz` + log signature poll. **[empirical-source: TBD]** — consumer 별 healthcheck window 측정 의무 (default 60s timeout, mctrader 사례 측정 후 lock-in) |
| 5 | 검증 단계 (배포 리뷰 lane) | smoke + 성능 비교 + cutover 사후 검증 — ADR-088 carrier scope |
| 6 | atomic swap | Traefik label 갱신 (blue → green priority swap), 단일 routing rule 변경 시점이 cutover 순간 |
| 7 | blue graceful drain | active connection 종료 대기. **[empirical-source: TBD]** — HTTP default 30s timeout / WebSocket default 5min timeout (mctrader websocket 시세 수집 사례 사후 측정 lock-in) |
| 8 | blue 3-시간 보존 | `retention-window-timer.yml` workflow 가 3h 후 cleanup trigger. **[empirical-source: TBD]** — 3-시간 = brainstorm Phase 1 합의 default, consumer override 가능 (`project.yaml deploy.retention_hours`) |
| 9 | 3-시간 후 정리 | docker container stop + image 보존 (image registry retention 별 정책). 정리 (contract) 마이그레이션 = 다음 Epic step 2 통합 (별도 흐름 — ADR-089 §결정 2 정합) |

ADR-068 I-5 dimensional empirical grounding cross-ref — 본 §5.1 안 `[empirical-source: TBD]` annotation 3개소 (healthcheck window / graceful drain / retention period). Wave 2+ (consumer mctrader 실측 후 carrier 별도 CFP 가 lock-in).

#### §5.2 — BG-1~4 stateful daemon 비적격 기준 (Amendment 1 신설, CFP-1317-S1)

**OR semantic**: 다음 4 row 중 **1+ 만족 시** blue-green 차단 + §결정 9 보조 매커니즘 진입. 2+ row 동시 만족 시 최강한 invariant 우선 (예: BG-1 + BG-4 동시 → writer-lease 가 양 invariant 모두 cover, 우선 채택 — §결정 9.3 mapping).

| 기준 (BG-N) | 정의 | mctrader 사례 | 비적격 trigger (OR semantic) |
|---|---|---|---|
| **BG-1 단일-writer 영속 상태** | ACID-D (durability) + WAL (Write-Ahead Log) pattern. 동시 writer 2 instance = consistency invariant violation (data corruption / split-brain) | `mctrader-data` WAL = single-writer DB 패턴 (시세 수집 raw write) | (BG-1) 만족 시 blue-green green container 가 동일 WAL 영역 동시 write = consistency violation → §결정 9.3 writer-lease 의무 |
| **BG-2 외부 단일연결 자원** | 외부 시스템이 client-side 단일 연결 강제 (예: 거래소 WebSocket = 동일 ApiKey 로 2 socket 시 server reject 또는 race condition) | `mctrader-market-bithumb` collector = Bithumb WebSocket (동일 ApiKey 2 socket 시 server-side race) | (BG-2) 만족 시 blue+green 양쪽 active = 외부 시스템 reject → §결정 9.2 또는 §결정 9.3 (consumer 의 외부 자원 protocol semantic 에 따라 양 매커니즘 모두 적격 — §결정 9.4 self-judge) |
| **BG-3 single-active 세션 enforcement** | 시스템 자체가 토큰 / lease 로 단일 active session 강제 (예: trading engine paper_runner — 동시 2 instance = 주문 중복 위험 / position 누적 inconsistency) | `mctrader-engine` paper_runner (동시 2 instance = position 누적 risk) | (BG-3) 만족 시 blue+green 양쪽 active = session token 충돌 → §결정 9.2 rolling per-host 의무 (한 시점 active host = 1) |
| **BG-4 non-idempotent 작업 경쟁** | 같은 입력에서 같은 결과 보장 안 됨 (예: compactor = 같은 raw 파일 2 process compact 시 중복 compact 결과물 / 부작용 누적 / 출력물 corruption) | `mctrader-data` compactor (동시 2 process = 중복 compact 결과물 누적) | (BG-4) 만족 시 blue+green 양쪽 active = 같은 작업 중복 실행 → §결정 9.3 writer-lease 의무 (lease holder = 단일 실행자) |

**비적격 평가 의무**: consumer 가 `project.yaml deploy.eligibility_reason: <BG-N enum 또는 null>` 명시 의무. null = blue-green primary (BG-1~4 미해당 자가 진단). BG-N enum = §결정 9 보조 매커니즘 진입.

**Forward extensibility (EC-B)**: BG-1~4 = consumer 가 식별 가능한 stateful pattern 의 초기 닫힌-set. 향후 BG-N+1 추가 = 별도 ADR-087 Amendment carrier (본 Amendment 1 = BG-4 까지).

### §결정 6 — wrapper / lane plugin 자체 self-application = N/A (doc-only fast-path)

- wrapper repo (`mclayer/plugin-codeforge`) + lane plugin repo (`mclayer/plugin-codeforge-*`) 자체의 release 흐름 = marketplace publish (ADR-063 cover) — deploy lane spawn 미적용.
- 본 ADR-087 자체 carrier Story (CFP-1059-S1) = doc-only fast-path (ADR-054 Category 2) — code review / integration test / security test skip + deploy lane spawn N/A.
- consumer application repo (예: mctrader) 만 deploy lane 활성화.

### §결정 7 — Epic close → auto-deploy trigger (별 channel, ADR-026 disjoint)

- Story / PR 단위 post-merge fix path (ADR-026 §결정 1) 와 disjoint — Epic 묶음 단위 발동 channel.
- `templates/github-workflows/auto-deploy.yml` (Phase 1 = skeleton, Phase 2 = wire) workflow 가 Epic close event 감지 + 변경 repo enumeration + DeployPLAgent spawn.
- consumer 가 `project.yaml deploy.enabled: true` 선언 시에만 활성 (default false — backward-compat).

### §결정 8 — Lane spawn evidence 의무 (declaration-only Wave 1)

- Story §14 Lane Evidence 표에 `deploy` row append 의무 (ADR-031 lane-evidence-check.yml extension).
- `mechanical_enforcement_actions: [deploy-lane-spawn-evidence]` declaration-only Wave 1 (ADR-076 / ADR-070 / ADR-082 / ADR-086 precedent 답습 — `evidence-checks-registry.yaml` 신규 entry 발의 시 row append 후 mechanical lint 활성).
- Bypass = `hotfix-bypass:deploy-lane-spawn` label (ADR-024 Amendment N family member 확장 — CFP-1059 sibling carrier).

### §결정 9 — 보조 배포 매커니즘 (rolling / writer-lease) 적격 사유 형식화 (Amendment 1 신설, CFP-1317-S1)

§결정 5 §5.2 BG-1~4 비적격 trigger 만족 시 진입하는 2 보조 매커니즘 sub-domain 정식화. mctrader#1272 escalation (b) carrier — "현 EC-5 = 자원 사유만 정의, stateful 사유 미정의" 해소.

#### §9.1 — chief tie-break ladder 결과 (ADR-068 Amendment 2 §결정 1 정합)

| 단계 | 결과 |
|---|---|
| (1) RACI matrix lookup (skill body 3-way 9-cell) | Cross-axis 9-cell 안 직접 match cell 0 (deploy strategy axis = primary axis matrix 안 row 부재). Step 2 진입. |
| (2) ADR-068 invariant 적용 | I-1 (semantic completeness): BG-1~4 + rolling/writer-lease 정의 완전 / I-3 (unconditional guard): BG-1~4 OR semantic / I-4 (wording SSOT): K8s single enum 산업 표준 ↔ 도메인 진실 2-axis matrix trade-off |
| (3) chief judgement | **타협안 채택** — `deploy_strategy: blue-green \| rolling \| writer-lease` (single enum primary, K8s `strategy.type: Recreate \| RollingUpdate` 답습) + secondary annotation `eligibility_reason: BG-N enum` (consumer 명시, 2-axis matrix info 보존). Rationale: (a) 산업 prior art alignment (K8s + Argo Rollouts hybrid) (b) consumer 학습 비용 minimize (1 primary key) (c) 도메인 진실 보존 (BG-N annotation = many-to-many mapping evidence) (d) Forward extensibility (BG-N+1 추가 시 annotation enum 만 확장) (e) backward-compat (default `blue-green` + annotation 부재 시 자동 blue-green) |
| (4) ADR-091 Amendment 발의 | 0건 — vocabulary governance scope (Authority Pair / Domain Service / Subdomain Specialist) 외 application BC 영역, vocabulary theater 차단 (INV-5 정합) |

#### §9.2 — rolling per-host 매커니즘 (BG-3 적격)

- **정의**: host 마다 차례로 swap (한 시점 active host = 1). K8s `Deployment` `RollingUpdate` `maxSurge=1 maxUnavailable=0` 답습. 1-host-at-a-time 변종 (Argo Rollouts canary `setWeight: 100/n_hosts` step 정합).
- **적격 BG**: BG-3 (single-active session enforcement) primary / BG-2 (외부 단일연결 자원) consumer-side self-judge 양가성 영역
- **layer 분리 (EC-D)**: rolling = **host-level 단일성** (한 시점 active host = 1). **session-level 단일성** (한 시점 active session = 1) 은 별 layer = application code 책무 (lease + heartbeat). rolling 도 swap window 안 2 host 일시 active 가능 영역 — session-level enforcement 가 별도 application layer 책무.
- **rationale (BG-3)**: paper_runner 동시 2 instance = position 누적 risk → rolling 으로 host-level 1 active 보장 + session token check 가 application layer 안 redundant safety net.

#### §9.3 — writer-lease 매커니즘 (BG-1 + BG-4 적격)

- **정의**: fencing token + TTL + 자동 만료 매커니즘. distributed systems literature 핵심 개념 — Kleppmann "Designing Data-Intensive Applications" Ch.8 "fencing tokens" 절 [verified]. 산업 prior art 3종: etcd lease (HashiCorp Raft-based KV, Kubernetes leader election primary) / Kafka leader epoch (partition leader epoch increment + follower stale detect) / ZooKeeper ephemeral node + Curator LeaderLatch (session TTL 기반).
- **적격 BG**: BG-1 (단일-writer 영속 상태) + BG-4 (non-idempotent 작업 경쟁) primary / BG-2 (외부 단일연결 자원) consumer-side self-judge 양가성 영역
- **EC-E 영역 declare**: writer-lease 의 fencing token 발급 / TTL / revoke 매커니즘 실 구현 = consumer-side implementation 책무 영역. 본 §결정 9 = "writer-lease = fencing token + TTL + 자동 만료 매커니즘 의무" semantic codify 만. 실 구현 선택 (etcd lease / Kafka leader epoch / ZK ephemeral / 자체 구현) = consumer choice.
- **rationale (BG-1)**: WAL single-writer = 동시 writer 2 instance 시 data corruption / split-brain → lease holder = 단일 writer 보장 + lease 만료 시 안전 handoff.
- **rationale (BG-4)**: compactor non-idempotent = 동일 입력 동시 2 process 시 중복 결과물 누적 → lease holder = 단일 실행자 보장 + lease 만료 시 다음 holder pickup.

#### §9.4 — BG-2 (외부 단일연결 자원) consumer-side self-judge

BG-2 = §9.2 rolling 과 §9.3 writer-lease 양 매커니즘 모두 적격 영역. consumer 의 외부 자원 protocol semantic 에 따라 self-judge 의무:

- **rolling 적격 case**: 외부 시스템이 host-level disconnect → reconnect 안전 (예: WebSocket reconnect-on-disconnect 정합 거래소 + 서버 race 없음)
- **writer-lease 적격 case**: 외부 시스템이 lease-based identifier 요구 (예: ApiKey + session ID 짝 = 외부 server 단일 active session 강제)
- mctrader-market-bithumb 사례: WebSocket reconnect 안전 → `eligibility_reason: BG-2` + `deploy_strategy: rolling` 권장 (consumer self-decide)

#### §9.5 — Concurrent deploy + rollback race serialization 의무 (EC-G — CFP-1317-S1 [codex-TP4-P1])

§9.2 rolling / §9.3 writer-lease 매커니즘 영역 안에서도 **deploy event-level race** = 별 layer. green container health check 직후 + atomic swap 직전 window 에 다른 deploy event 발생 시 race condition (예: hot-patch + 동시 main branch merge).

- **의무**: deploy event-level serialization (FIFO queue) — 1 active deploy event = 1 lease holder. concurrent deploy reject + rollback 진행 중 신규 deploy block.
- **실 enforcement 매커니즘**: consumer-side deploy orchestrator (별 carrier 영역). 본 §결정 9.5 = semantic invariant codify 만.
- **rationale**: §9.3 writer-lease 가 data-plane single-writer 영역 cover, §9.5 = control-plane (deploy event itself) single-writer 영역. 두 layer disjoint (data layer ↔ control layer) — §9.3 만으로 control plane race 미cover.
- **ArchitectAgent self-judge**: §결정 9.5 = §결정 9 body sub-clause 통합 (별도 §결정 10 분리 X). Rationale = data-plane single-writer (§9.3) + control-plane single-writer (§9.5) 둘 다 "단일성 invariant" 의 disjoint layer 표현, single coherent ADR §결정 영역 통합. 별도 §결정 10 분리 시 §결정 9 ↔ §결정 10 coupling 인공 증가.

#### §9.6 — 기존 consumer migration path (EC-H — CFP-1317-S1 [codex-TP4-P1])

본 Amendment 1 발효 시 기존 consumer (ADR-087 §결정 5 "blue-green 단일 매커니즘 고정" 전제로 `project.yaml` 작성된 consumer) backward-compat 보장.

- **default behavior = `deploy_strategy: blue-green`** (기존 consumer 영향 0, opt-in 으로 §결정 9 보조 매커니즘 활성).
- **migration path 2단계**:
  1. **신규 consumer**: `deploy_strategy: blue-green | rolling | writer-lease` 선택 자유 + `eligibility_reason: BG-N enum` 또는 null 명시
  2. **기존 consumer**: blue-green default 유지 (project.yaml 변경 0) + 사용자 가 BG-1~4 자가 진단 후 opt-in 시 §결정 9 보조 매커니즘 활성
- **consumer overlay `project.yaml deploy.strategy_override` 신설 가능성**: 본 Amendment scope 외 (consumer adoption side, mctrader#1265 영역). 본 §결정 9.6 = declare-only.
- **ADR-089 Schema 변경 7 원칙 cross-ref**: 양방향 호환 강제 (default blue-green = 기존 schema 영향 0) + reverse 가능성 (consumer 가 보조 매커니즘 → blue-green 복귀 시 `deploy_strategy: blue-green` + `eligibility_reason: null` 명시).


## 해소 기준

N/A — permanent policy

## 결과

### Lane composition 정합

- CLAUDE.md "Development Agent Team" 표 row count = 8 (이전 6 + 배포 + 배포 리뷰).
- `codeforge:story-epic-flow-preflight` skill body 8 lane mention.
- `docs/orchestrator-playbook.md` §3 Story flow = 8 lane spawn order (요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → 배포 리뷰).

### Cascade workflow (codeforge family atomic)

CFP-1059 Story-1 = 4 ADR carrier 묶음 + 8 Amendment + skill 갱신 + plugin.json MAJOR 6.0.0 atomic bump.

- marketplace sync PR (선행 merge — ADR-063 §결정 2)
- 7 plugin sibling sync PR family (wrapper + 6 기존 lane plugin 모두 6.0.0 mirrored field 4종 verbatim)
- internal-docs PR (spec + plan + Story stub)

### Self-application bootstrap mitigation (ADR-082 §결정 2 정합)

본 ADR-087 작성 = ArchitectAgent self-write 영역. verify evidence:

- ADR-RESERVATION row 87 = CFP-1059 active (GitOpsAgent commit `2104183`, T1) — verified-via Read tool 직접 확인
- 4 sibling ADR (087/088/089/090) file 부재 verify-via Bash `ls docs/adr/ADR-08[7-9]*.md ADR-090*.md` → empty
- Plan plan.md anchor ADR 번호 stale (085/086 명시) → 본 commit batch 가 087-090 으로 정정 (별도 commit, internal-docs worktree)
- spec §4 ADR-085 draft 영역 verbatim 가져옴 (ADR 번호만 087 로 정정)

## 관련 파일

- [ADR-023](ADR-023-lane-plugin-lifecycle.md) — Amendment N (8 lane 확장 절차)
- [ADR-042](ADR-042-agent-model-selection-policy.md) — Amendment 9 (DeployPL/Worker tier)
- [ADR-026](ADR-026-post-merge-automation.md) — Amendment N (Epic close → Deploy trigger)
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — Amendment N (7→9 plugin family)
- [ADR-027](ADR-027-consumer-adoption-protocol.md) — Amendment N (project.yaml deploy.* schema)
- [ADR-014](ADR-014-operational-risk-ssot-distribution.md) — Amendment N (InfraOperationalArch ↔ DeployPL boundary)
- [ADR-088](ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — sibling carrier (Deploy Review lane)
- [ADR-089](ADR-089-schema-change-7-principles.md) — sibling carrier (Schema 변경 7 원칙)
- [ADR-090](ADR-090-cross-layer-reference-policy.md) — sibling carrier (Cross-layer 정책)
- `templates/github-workflows/auto-deploy.yml` (Phase 1 skeleton, S6 wire)
- `templates/github-workflows/blue-green-swap.yml` (Phase 1 skeleton, S6 wire)
- `templates/github-workflows/retention-window-timer.yml` (Phase 1 skeleton, S6 wire)
- `templates/github-workflows/auto-rollback.yml` (Phase 1 skeleton, S6 wire)

## Amendment 2 (2026-05-29 KST, CFP-1808) — Phase 2 wire activation: deploy-lane-presence 6번째 required check + 2 plugin sibling sync + auto-deploy / deploy-lane-spawn-evidence declarative declare

본 Amendment 는 §결정 1-N (기존) 본문의 Phase 2 wire activation — HIGH risk 영구 차단 회피 mandate (declaration-only Wave 1 패턴 적용 영역 외, 즉시 wire 의무). ADR-058 §결정 5 ratchet 강화 only.

### §A. Wave 1 declarative + immediate wire atomic (rationale: HIGH risk 회피)

본 Amendment scope = declarative-only Wave 1 패턴 적용 영역 **외** — pattern_count 1 first applied case + HIGH risk 영구 차단 가능성 (2 plugin repo PR merge 영구 pending). 즉시 wire 의무 — Wave 2 별 sub-CFP 분리 = ratchet 약화 위험 (영구 차단 risk 미해소 기간 연장). precedent: ADR-088 §결정 2 (배포 리뷰 lane mandatory smoke / 성능 비교 / cutover 검증 — 즉시 wire mandate 동형).

### §B. deploy-lane-presence 6번째 required check 활성

본 repo `main` 보호 contexts 현재 5 (phase-gate-mergeable / invariant-check / doc frontmatter schema (CFP-28 — strict) / doc section schema (CFP-28 — strict) / check-gate) → 6 (+ deploy-lane-presence). admin gh CLI 작업 (`gh api repos/.../branches/main/protection`) Story 마지막 단계 mandate.

### §C. 2 plugin sibling sync (`phase-gate-mergeable.yml` 신설)

`codeforge-deploy` + `codeforge-deploy-review` plugin repo `.github/workflows/phase-gate-mergeable.yml` = 부재 → 신설 의무 (HIGH risk 차단 회피). source = 본 repo `templates/github-workflows/phase-gate-mergeable.yml` (32899 bytes, 2026-05-26 timestamp). byte-identical copy (ADR-010 sibling sync precedent + ADR-005 self-app 동형).

### §D. auto-deploy / deploy-lane-spawn-evidence declarative declare (이미 활성)

본 repo `auto-deploy.yml` + `deploy-lane-spawn-evidence.yml` + `deploy-review-lane-spawn-evidence.yml` workflows = 이미 활성 (.github/workflows/ + templates/ byte-identical). 본 Amendment 안 cross-ref declarative declare only — 신규 file 신설 0.

### §E. ADR-088 cross-ref backref

배포 리뷰 lane (ADR-088) 영역 영향 cross-ref:
- `auto-deploy.yml` trigger → 배포 lane (ADR-087) → 자동 trigger → 배포 리뷰 lane (ADR-088)
- `deploy-lane-presence` required check = 배포 lane + 배포 리뷰 lane 양 evidence 의무

본 Amendment 본문 안 ADR-088 §결정 1/2/3 cross-ref 명시 의무 (배포 리뷰 lane mandatory smoke / 성능 비교 / cutover 사후 검증 — Phase 2 PR evidence chain 동반).

### §F. Amendment 2 — sunset_justification N/A 정당

`is_transitional: false` 보존 — Amendment 2 scope = 결정 1-N 강화 방향 only (Phase 2 wire activation, contexts 5→6 ratchet, 2 plugin sibling sync 의무). 약화 / scope 축소 / 면제 0건. ADR-058 §결정 5 sunset_justification ratchet 통과. ADR-064 §self-application top-down ratchet 정합 (영구 차단 회피 mandate carve-out 외).

### §G. Related

- `<internal-docs>/plugin-codeforge/stories/CFP-1808.md` — Story file
- `<internal-docs>/plugin-codeforge/specs/CFP-1808-deploy-phase-gate-workflows.md` — Spec file
- `.github/workflows/deploy-lane-presence.yml` + `templates/github-workflows/deploy-lane-presence.yml` — workflow file 신설 (본 Amendment carrier)
- `<codeforge-deploy>/.github/workflows/phase-gate-mergeable.yml` + `<codeforge-deploy-review>/.github/workflows/phase-gate-mergeable.yml` — 2 plugin sibling sync (본 Amendment carrier)
- parent retro: `<internal-docs>/plugin-codeforge/retros/2026-05-28-cfp-1785.md` (parallel session FU-D HIGH origin)
- cross-ref: ADR-088 §결정 1-3 (배포 리뷰 lane)
