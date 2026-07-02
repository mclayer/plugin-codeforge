---
title: codeforge-deploy lane 구조 (배포 레인 — blue-green + atomic swap + 3시간 보존 + 자동 rollback)
last_captured: 2026-06-01
last_update_cfp: CFP-1677  # Living Architecture git source 신설 (defer carrier from CFP-1586 Sub-C)
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-1677, defer carrier from CFP-1586 Sub-C / parent Epic ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타는 Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다.
     사실 출처: CLAUDE.md / README.md / agents/DeployPLAgent.md / agents/DeployWorkerAgent.md /
     docs/inter-plugin-contracts/deploy-output-v1.md / templates/deploy-mechanism.md / CHANGELOG.md @ cfp-1677 (origin/main b0e54fb). -->

## 모듈

codeforge-deploy = codeforge family **배포 (Deploy) lane plugin** (CFP-1059 / ADR-087). 6 → 8 lane 확장의 #6 배포 lane. 책임 = **consumer application repo 의 Epic 묶음 종료 후, 변경된 repo 만 production 환경에 배포** (blue-green + atomic swap + 3시간 보존 + 자동 rollback). `[verified: CLAUDE.md @ cfp-1677 "Agent 2종" 표 + agents/ tree direct enumeration]`

**Agent 2종 (모두 opus tier — ADR-141 로 opus 단일 tier 통일, ADR-042-agent-model-selection-policy Amendment 9)**:

| 모듈 (agent) | 역할 | 책임 | model |
|---|---|---|---|
| **DeployPLAgent** | 배포 lane PL (lead + 종합자) | Epic 묶음 단위 발동 — 변경 repo enumeration + blue-green sequence orchestration + healthcheck 검증 (단계 4 직접) + atomic swap trigger (단계 6 직접) + 3시간 보존 timer (단계 8) + 자동 rollback 결정. DeployWorkerAgent repo 별 spawn + verdict 종합 후 Orchestrator 반환 | opus |
| **DeployWorkerAgent** | 배포 worker | 각 변경 repo 배포 실 실행 — 9-step 마이그레이션 sequence 의 실행 단계 (build push / expand migration apply / green start / healthcheck poll / atomic swap label / blue drain / 정리). idempotent script + graceful shutdown 신호 + healthcheck endpoint poll + secret provider lookup (1Password Connect 또는 fallback) + reverse proxy label 갱신 (Traefik primary). 결과를 DeployPLAgent 반환 | opus |

> 전 에이전트 opus 단일 tier (ADR-141 — fallback 대상 없음). agent file frontmatter `model: opus`.

**stateless 재스폰**: 양 agent 모두 세션 유지 없음. 매 배포 trigger 마다 신규 스폰 (DeployPL = Epic close state + 변경 repo log 재로딩 / DeployWorker = repo deploy config + 현재 컨테이너 상태 재로딩).

## 경계

**배포 단위 = repo** (ADR-087 §결정 3) `[verified: agents/DeployPLAgent.md Mandate §1]`:
- consumer 묶음 Epic 안 **변경된 repo 만** 배포. 변경 안 된 repo = skip.
- 변경 감지 = Phase 2 PR merge log + Epic close 시점 sync (post-merge-followup.yml workflow chain — ADR-026 Amendment N).
- mctrader 사례: `mctrader-data` + `mctrader-engine` 만 변경 시 `mctrader-{market,market-bithumb,web}` skip.

**Lane self-write boundary** `[verified: CLAUDE.md @ cfp-1677 "Self-write 책임" 단락 + agents/*.md deny permissions]`:

| 경계 영역 | owner |
|---|---|
| 배포 매커니즘 실행 (docker / ssh / migration script) | DeployWorkerAgent (read-only 분석 + 실행만, `src/**`·`tests/**`·`docs/**` write 권한 없음) |
| Story / Epic §14 Lane Evidence `deploy` row | Orchestrator (ADR-087 §결정 8 — 본 plugin agent 가 아닌 wrapper Orchestrator) |
| GitHub Issue 코멘트 | wrapper Orchestrator 경유 |
| `project.yaml deploy.*` schema 정의 | **wrapper SSOT 영역** (CFP-1317-S2 / ADR-068 I-4) — `docs/project-config-schema.md` deploy 섹션 단일 SSOT. 본 plugin `templates/deploy-mechanism.md` = 9-step sequence + Edge Cases reference layer 만 (schema mirror 0건, drift 0 invariant) |

**disjoint axis 경계**:
- **InfraOperationalArch (설계 lane deputy) ↔ DeployPL** (ADR-014 Amendment N): 운영 risk policy SSOT = design-time decision (InfraOperationalArch §7.4 invariant 정의) ↔ 배포 매커니즘 실행 = runtime 실행 (DeployPL). 영역 disjoint.
- **Epic close → auto-deploy trigger** (ADR-026 disjoint channel): consumer `project.yaml deploy.enabled: true` 선언 시에만 활성 (default false, backward-compat). 통합테스트 / 보안테스트 통과 후 Epic close 시점 발동.
- **production-touch 경계**: deploy lane scope = **consumer application repo 배포 영역** — codeforge plugin marketplace publish (ADR-063 atomic invariant) 와 disjoint. wrapper repo + lane plugin repo 자체의 release = marketplace publish (deploy lane spawn 미적용, ADR-087 §결정 6). consumer application repo (예: mctrader) 만 deploy lane 활성화.

**평행 PL / 수평 호출 금지** `[verified: agents/DeployPLAgent.md §평행 PL]`: 평행 PL = RequirementsPL / ArchitectPL / DeveloperPL / DesignReviewPL / CodeReviewPL / SecurityTestPL / IntegrationTestAgent / DeployReviewPL. 모두 Orchestrator 경유, lane 간 수평 호출 금지. (lane 내부 DeployPL → DeployWorker spawn 은 허용 — Orchestrator 경유 없이 repo 별 spawn.)

## 인터페이스 계약

lane 간 계약 surface = `docs/inter-plugin-contracts/` (canonical = 본 plugin repo, wrapper = sibling sync mirror — ADR-010):

**Producer 계약 (kind:contract)** — 본 lane 이 생성 `[verified: docs/inter-plugin-contracts/deploy-output-v1.md]`:

| contract | 용도 | SSOT pointer | 상태 |
|---|---|---|---|
| `deploy_output` | 배포 lane 산출물 핸드오프 (DeployPL/Worker output → Orchestrator → 배포 리뷰 lane) | `docs/inter-plugin-contracts/deploy-output-v1.md` (canonical, contract_version 0.1) | Phase 1 placeholder declare only (CFP-1059) — actual schema body wire = S2 sub-Story carrier |

> `deploy_output` Phase 1 = declarative anchor (body 본문 0). 예상 schema field group (S2 wire 영역): `repo_deploys[]` / `deploy_sequence_timeline[]` / `secret_provider_invocation[]` / `traefik_label_flip` / `retention_window_timer` / `auto_rollback_decision`. Versioning = `0.1 Draft` → `1.0 Active` MAJOR bump (Draft→Active, ADR-008 §결정 1). agent file 내부 verdict 형식 (DeployPL `deploy_verdict` / DeployWorker `worker_result`) = lane internal handoff (계약 surface 와 분리).

**consumer overlay schema (wrapper SSOT redirect)** `[verified: templates/deploy-mechanism.md]`:
- consumer `project.yaml deploy.*` 작성 = wrapper `docs/project-config-schema.md` deploy 섹션 **단일 SSOT 직접 참조** (본 plugin 안 schema mirror 0건 — ADR-068 I-4 wording SSOT).
- **5 mandatory nested**: `host_mapping` / `docker_hub` / `traefik` / `1password` / `ssh_targets`.
- **4 optional nested**: `auto_rollback` (CFP-1193 / ADR-105) / `operational_monitor` (CFP-1194 / ADR-106 Amd 2) / `self_improving_loop` (CFP-1195 / ADR-106 §결정 4) / `canary` (CFP-1196 / ADR-105 §결정 3).

**배포 매커니즘 — blue-green 9-step** (ADR-087 §결정 5) `[verified: templates/deploy-mechanism.md + agents/DeployPLAgent.md Mandate §2 표]`:

| 단계 | 내용 | 책임 |
|---|---|---|
| 1 | 빌드 → Docker Hub push | DeployWorker (GitHub Actions build) |
| 2 | 확장 (expand) 마이그레이션 apply | DeployWorker (Alembic / 빅데이터 expand — ADR-089 §결정 2 expand-contract 분리) |
| 3 | green 컨테이너 시작 | DeployWorker (blue 유지) |
| 4 | 건강 확인 | **DeployPL 검증** (healthcheck `/healthz` + log signature, default 60s `[empirical-source: TBD]`) |
| 5 | 검증 단계 | 배포 리뷰 lane 위임 (smoke + 성능 비교 — ADR-088) |
| 6 | atomic swap | **DeployPL trigger** (Traefik label swap, cutover 순간) |
| 7 | blue graceful drain | DeployWorker (HTTP default 30s / WebSocket default 300s `[empirical-source: TBD]`) |
| 8 | blue 3시간 보존 | **DeployPL timer** (retention_hours default 3) |
| 9 | 3시간 후 정리 | DeployWorker (container stop, image 보존). contract 마이그레이션 = 다음 Epic step 2 (별 흐름, ADR-089 §결정 2) |

> 시간 차원 (4단계 healthcheck window / 7단계 graceful drain / 8단계 retention 3시간) = wrapper ADR-087 §결정 5 본문 `[empirical-source: TBD]` 3개소 (ADR-068 I-5 dimensional empirical grounding, consumer mctrader 첫 적용 시 실측 후 lock-in).

**보조 매커니즘 (BG-1~4 비적격 시 — ADR-087 §결정 9)** `[verified: templates/deploy-mechanism.md Edge Cases + agents Mandate §4]`: blue-green 표준 sequence 비적격 환경 시 보조 매커니즘 자동 선택.
- **EC-5** 호스트 자원 2배 한계 초과 → **rolling** (한 대씩) fallback 자동 선택.
- **EC-6** 이중화 호스트 부재 → downtime 0 보장 불가, consumer declare `acceptable_downtime_ms` 준수.
- **EC-1** 1Password Connect 부재 → `.env` + GitHub Actions secret fallback.
- **EC-2** Traefik 부재 → 다른 reverse proxy (nginx / Caddy / haproxy) abstraction (Phase 1 = Traefik primary, abstract interface Wave 5+).
- **EC-3** 큰 변경 hard limit (column 100+ / row 1억+ / lock 5분+) → 자동 흐름 외 + 사용자 수동 trigger (ADR-089 §결정 7).
- **EC-4** 3시간 보존 중 결함 발견 → 자동 rollback (blue 복원). 3시간 이후 = hotfix path (rollback 불가, 새 배포 cycle).
- **EC-7** consumer self-hosted Docker Hub fork → `deploy.docker_hub.org` override.

> writer-lease / fencing (ADR-087 Amendment 1 CFP-1317-S1 §결정 9) = BG-1~4 비적격 표 + writer-lease 보조 매커니즘 영역 — 상세 SSOT = wrapper ADR-087 §결정 9 본문.

## 데이터 흐름

**배포 lane 진입 → 산출물 flow** (Orchestrator 가 lane 진입 시 DeployPLAgent 1개 spawn — non-skippable) `[verified: agents/DeployPLAgent.md Mandate §0-§6 + agents/DeployWorkerAgent.md Mandate §0-§8]`:

```
[upstream] 통합테스트 → 보안테스트 통과 → consumer application repo Epic 묶음 close
  ↓ (consumer project.yaml deploy.enabled: true 선언 시에만)
auto-deploy trigger (post-merge-followup.yml chain — ADR-026 Amendment N + ADR-087 §결정 7)
  ↓
DeployPLAgent (lane PL) spawn
  · 스폰 패킷 수신 (epic_key / closed_at / candidate_repos / deploy_config)
  ↓ §1 변경 repo enumeration (ADR-087 §결정 3) — 변경된 repo 만, 나머지 skip
  ↓
변경 repo 별 DeployWorkerAgent spawn (1 repo = 1 worker):
  ├─ 단계 1 빌드 → Docker Hub push (GitHub Actions build)
  ├─ 단계 2 expand 마이그레이션 apply (Alembic / 빅데이터 expand, ADR-089 §결정 2 — expand only)
  ├─ 단계 3 green 컨테이너 시작 (blue 유지) + secret provider lookup (1Password Connect / .env fallback)
  └─ 단계 4 healthcheck poll (endpoint + log signature) → DeployPL 반환
  ↓
DeployPLAgent — 단계 4 건강 확인 직접 검증
  · PASS → 단계 5 (배포 리뷰 lane 검증) 진입 허용
  · timeout (default 60s) → 자동 rollback (atomic swap 미진입, green 폐기, blue 유지)
  ↓
[배포 리뷰 lane 위임 — 단계 5]
  · smoke + 성능 비교 (DeployReviewPLAgent, ADR-088 carrier scope)
  ↓ 배포 리뷰 verdict PASS 수신 후에만
DeployPLAgent — 단계 6 atomic swap trigger 직접
  · Traefik label 갱신 (blue → green priority swap), 단일 routing rule 변경 = cutover 순간 (downtime 0 목표)
  · EC-5 시 rolling fallback / EC-6 시 acceptable_downtime_ms 준수
  ↓
DeployWorkerAgent — 단계 7 blue graceful drain
  · HTTP SIGTERM + active request 완료 대기 (default 30s) / WebSocket·daemon 안정 종료 (default 300s)
  ↓
DeployPLAgent — 단계 8 blue 3시간 보존 timer 설정 (retention-window-timer.yml, retention_hours default 3)
  · 보존 중 결함 발견 (배포 리뷰 cutover 사후 검증 FAIL, EC-4) → 자동 rollback (blue 복원)
  ↓
DeployWorkerAgent — 단계 9 3시간 후 정리 (container stop, image 보존)
  · contract 마이그레이션 = 다음 Epic step 2 (별 흐름)
  ↓
DeployPLAgent — verdict 종합 (deploy_verdict) → Orchestrator 반환
  · deployed_repos / skipped_repos / blue_green_status / atomic_swap_at / retention_until / rollback_triggered
  ↓
[downstream] 배포 리뷰 lane (DeployReviewPLAgent — cutover 사후 검증, ADR-088) 인계
```

**FAIL 시 회귀 경로** `[verified: agents/DeployPLAgent.md §포지션 FAIL 시]`:
- healthcheck FAIL / 배포 매커니즘 실패 → 자동 rollback (blue 보존본 복원) + Orchestrator 통지.
- 성능 미충족 (배포 리뷰 lane verdict FAIL) → DeployReviewPL root cause 진단 dispatch (구현 / 설계 / 요구사항 lane back, ADR-088 §결정 5).

**§14 Lane Evidence 의무** (ADR-087 §결정 8 / ADR-031 extension): 매 배포 lane spawn 시 Story / Epic §14 Lane Evidence 표에 `deploy` row append (start: spawn 직전, end: return 직후 outcome). `mechanical_enforcement_actions: [deploy-lane-spawn-evidence]` declaration-only Wave 1. Bypass = `hotfix-bypass:deploy-lane-spawn` label.

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only** (누적 현재 상태 SSOT — 델타는 Change Plan disjoint). closed-enum 4 영역 (모듈 + 경계 + 인터페이스 계약 + 데이터 흐름) 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` 또는 `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
