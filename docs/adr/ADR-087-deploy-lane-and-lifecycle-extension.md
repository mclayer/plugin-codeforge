---
adr_number: 87
title: Deploy lane 신설 — codeforge-deploy plugin 정식 도입 + lane lifecycle 6→8 단계 확장
status: Accepted
category: lifecycle
date: 2026-05-20
carrier_story: CFP-1059
parent_epic: CFP-1059
related_stories:
  - CFP-1059  # carrier Epic
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
amendment_log: []
amendments: []
is_transitional: false  # permanent lane structure — 약화 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null
mechanical_enforcement_actions:
  - deploy-lane-spawn-evidence  # declaration-only Wave 1 (ADR-070 / ADR-082 / ADR-086 precedent 답습)
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

### §결정 5 — 배포 매커니즘 = blue-green + atomic swap + 3-시간 보존 (단일 매커니즘)

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
| 9 | 3-시간 후 정리 | docker container stop + image 보존 (image registry retention 별 정책). 정리 (contract) 마이그레이션 = 다음 Epic step 2 통합 (별 흐름 — ADR-089 §결정 2 정합) |

ADR-068 I-5 dimensional empirical grounding cross-ref — 본 §결정 5 안 `[empirical-source: TBD]` annotation 3개소 (healthcheck window / graceful drain / retention period). Wave 2+ (consumer mctrader 실측 후 carrier 별 CFP 가 lock-in).

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
- Plan plan.md anchor ADR 번호 stale (085/086 명시) → 본 commit batch 가 087-090 으로 정정 (별 commit, internal-docs worktree)
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
