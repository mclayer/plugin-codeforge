---
title: codeforge-deploy-review lane 구조 (배포 리뷰 레인 — smoke / 성능 비교 / cutover 사후 검증)
last_captured: 2026-06-01
last_update_cfp: CFP-1677  # Living Architecture git source 신설 (defer carrier from CFP-1586 Sub-C)
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-1677, parent defer carrier from CFP-1586 Sub-C / ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타는 Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다.
     [verified: agents/ tree direct ls + CLAUDE.md / README.md / CHANGELOG.md / deploy-review-output-v1.md / templates/deploy-review-mechanism.md @ cfp-1677 origin/main] -->

## 모듈

codeforge-deploy-review = 배포 리뷰 레인 plugin (codeforge 6 → 8 lane 확장의 #7). **production 환경 성능 측정을 1st-class 검증 phase 로 격상** (CFP-1059 / [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md)). 본 lane scope = **"한 번 끝나는 검증" 만** (smoke / 성능 비교 / cutover 사후 검증) — 운영 phase (continuous monitoring) 와 disjoint.

`[verified: agents/ direct ls @ cfp-1677 — DeployReviewPLAgent.md / DeployReviewWorkerAgent.md / ProductionEvidenceDeputyAgent.md 3 file 실재]`. agent 구성:

**Permanent agent (2 file)** — 모든 배포 리뷰 lane 진입 시 spawn:

| 모듈 (agent) | 역할 | 입장 / 책임 | model |
|---|---|---|---|
| **DeployReviewPLAgent** | 배포 리뷰 lane PL (supervisor + verdict 종합 + FIX dispatch) | production-grade 성능 측정 1st-class lead — smoke / 성능 비교 / cutover 사후 검증 verdict 종합. 성능 미충족 시 root cause 1차 진단 + debate-protocol-v1 cross-module trigger (성능 모델 결정 분열 시) + 구현/설계/요구사항 lane FIX dispatch. DeployReviewWorker + ProductionEvidenceDeputy spawn | Opus (adversarial debate 자동 발동 영역 mandatory — ADR-042-agent-model-selection-policy §결정 1) |
| **DeployReviewWorkerAgent** | 검증 3종 실 측정 worker | smoke test 실행 (HTTP shadow / WebSocket·daemon 대기 mode) + 성능 baseline 수집 (latency p50/p95/p99 / throughput / error rate / CPU·memory) + cutover 사후 검증 측정. raw metric 측정만 (verdict 판정 금지) → DeployReviewPL 반환 | sonnet (ADR-141 Amendment 2 carve-out — fallback 대상 없음) |

**CONDITIONAL deputy (1 file)** — production cutover-touching Story 시 DeployReviewPL 이 추가 spawn:

| 모듈 (agent) | trigger 조건 | 책임 | model |
|---|---|---|---|
| **ProductionEvidenceDeputyAgent** | production cutover Story (Story §13 `production_cutover_touching: true` 선언 OR §13 Live Operational Discipline 본문 보유). wrapper-self-app N/A | production evidence quad (functional / security / monitoring / testing 4 measurement source) + EPIC CLOSED gate + post-cutover wiring + Family atomic canary pin (publisher_versions[] length_invariant) | (frontmatter `model:` field 부재 — CONDITIONAL deputy, parent_pl spawn) |

> **ProductionEvidenceDeputy ownership 이관** (ADR-088 §결정 4 + ADR-72 Amendment 4): codeforge-design lane CONDITIONAL deputy → **codeforge-deploy-review lane 정식 deputy**. parent_pl: ArchitectPLAgent → DeployReviewPLAgent / ssot_position: codeforge-design → codeforge-deploy-review. mandate body = ADR-72 §결정 1-7 verbatim 유지 (책임 영역 불변, ownership / parent_pl / ssot_position 만 변경). InfraOperationalArch (codeforge-design) 와 disjoint axis — policy SSOT (design-time) vs evidence SSOT (runtime).

## 경계

**호출 시점 + lane 진입 경계**: 배포 lane (DeployPLAgent) 이 green 컨테이너 healthcheck PASS 후, atomic swap 직전 단계에서 Orchestrator 가 DeployReviewPLAgent 1개 spawn (ADR-088 §결정 3 검증 3종 시점). **PASS** → DeployPLAgent 에 atomic swap 허용 신호 → blue 3-시간 보존. **FAIL** → root cause 1차 진단 + lane back 을 Orchestrator 에 반환.

**"한 번 끝나는 검증" 경계** (ADR-088): 본 lane = smoke / 성능 비교 / cutover 사후 검증 3종만. 운영 phase (canary promote / rollback 신호 회수 / regression 감지 / channel drift / cutover monitoring 30일 / smoke ongoing 등 continuous monitoring) 와 **disjoint** — 운영 phase = 별 Epic carrier (본 Epic close 후 발의).

**기존 review lane 과의 disjoint axis** (ADR-088 — production 성능 측정 축이 4 review lane 모두와 분리):

| lane | 축 | 본 lane 과의 disjoint |
|---|---|---|
| DesignReview | ADR 정합 / 설계 보장성 | code/production-level 미접근 |
| CodeReview | 구현 품질 | production runtime 측정 미접근 |
| SecurityTest | code-level 보안 정합 | production 성능 측정 미접근 |
| IntegrationTest (codeforge-test) | 시나리오 단위 정합 | production cutover 사후 검증 미접근 |
| **Deploy Review (본 lane)** | production 환경 성능 측정 + cutover 사후 검증 | 위 4 lane 모두와 disjoint axis |

**Self-write boundary**: 본 plugin agent 는 read-only 분석 + 성능 측정 (curl / docker / ssh) 만. `src/**` / `tests/**` / `docs/**` 직접 write 권한 없음 (3 agent 모두 frontmatter `deny` 명시). 예외 = ProductionEvidenceDeputy 의 `.claude-work/doc-queue/**` write (evidence quad 산출 queue). Story / Epic §14 Lane Evidence `deploy-review` row 갱신은 **Orchestrator** 가 처리 (ADR-088 §결정 8). 성능 미충족 FIX root cause 최종 판정 = ArchitectPL (DeveloperPL 1차 진단 후, ADR-035) — 본 PL 은 1차 진단 + dispatch.

**debate-protocol-v1 trigger 경계** (Opus tier mandatory — ADR-088 §결정 2): 성능 미충족 root cause 가 cross-module (성능 모델 결정 분열, 양 architect 의견 분열) 시 DeployReviewPL 이 debate-protocol-v1 자동 발동. 본 lane 이 adversarial debate 자동 발동 영역이므로 PL = Opus tier mandatory.

**production-touch 경계**: ProductionEvidenceDeputy 는 production cutover-touching Story 시만 CONDITIONAL spawn. wrapper / lane plugin self-application = N/A (ADR-088 §결정 7 / ADR-087 §결정 6 precedent / CFP-954 보존) — codeforge family plugin 자체 변경 Story 는 배포 리뷰 lane spawn N/A.

**§14 Lane Evidence 의무**: 매 배포 리뷰 lane spawn 시 Story / Epic §14 Lane Evidence 표에 `deploy-review` row append (ADR-031 lane-evidence-check.yml extension). `mechanical_enforcement_actions: [deploy-review-lane-spawn-evidence]` declaration-only Wave 1. Bypass = `hotfix-bypass:deploy-review-lane-spawn` label.

**Disjoint scope** (ADR-078 §결정 3): 본 doc (architecture_doc) = lane internal 누적 현재 상태, Story key 독립 / Change Plan = Story별 변경 델타, Story key 종속 / ADR = 단일 결정 단위, 불변 / 본 doc ↔ Change Plan = 상보 disjoint (구조 vs 델타).

## 인터페이스 계약

lane 간 + lane 내부 계약 surface = `docs/inter-plugin-contracts/` (canonical = 본 plugin repo, wrapper = sibling sync mirror — ADR-010):

**Producer 계약 (kind:contract)** — 본 lane 이 생성:

| contract | 용도 | SSOT pointer / 상태 |
|---|---|---|
| `deploy_review_output` | 배포 리뷰 lane 산출물 핸드오프 (DeployReviewPL / Worker output → Orchestrator) | `docs/inter-plugin-contracts/deploy-review-output-v1.md` (canonical = 본 plugin repo). 현재 `contract_version: 0.1` **Phase 1 placeholder declare** — actual schema body wire = S3 sub-Story carrier (Draft → Active 시 MAJOR bump, ADR-008 §결정 1) |

> 예상 schema field group (S3 actual wire 영역, deploy-review-output-v1.md 명시): `smoke_verdict` / `performance_comparison` (latency·throughput·error_rate 3-tuple + `[empirical-source: ...]` annotation 의무) / `cutover_post_evidence_quad` (4 measurement source) / `debate_artifact_ref` (Story §9 link) / `fix_dispatch_target` (DeveloperPL / ArchitectPL / RequirementsPL) / `production_evidence_deputy_ownership_transfer_log`.

**Host 계약 (kind:registry — sibling sync 면제, ADR-010 §결정 2)** — 본 lane 이 발동 / 참여:

| contract | 본 lane 역할 |
|---|---|
| `debate-protocol-v1` | 성능 미충족 root cause 가 cross-module (성능 모델 결정 분열) 시 DeployReviewPL 이 자동 발동 (ADR-059 multi-round adversarial debate). min 3 / soft default 4 / max 5 라운드. anti-sycophancy (`remaining_disagreements` + role_lock + `POSITION_CHANGE`). transcript → Story §9 append → FIX Ledger `debate_artifact_ref` |

**검증 evidence 3종 schema** (DeployReviewWorker → DeployReviewPL 반환 — `worker_measurement` packet, agent file 명시):

| evidence | 측정 field |
|---|---|
| **smoke** | `smoke_result` (pass/fail) + `smoke_detail` (HTTP shadow status code / payload diff / error 여부 · WebSocket·daemon 연결 안정성) |
| **성능 비교** | `performance_metrics`: latency p50/p95/p99 (ms) / throughput / error_rate / cpu_pct / memory_mb / `baseline_delta` (기존 production baseline 대비, null = 첫 측정 → 절대값 + `[empirical-source: TBD]` ADR-068 I-5) |
| **cutover 사후 검증** | `cutover_post_metrics` (atomic swap 직후 ~ 3-시간 실 production 트래픽 error rate / latency 회귀) + `regression_detected` (bool) |

> DeployReviewPL 의 종합 verdict (`deploy_review_verdict`) packet = `smoke_status` / `performance_status` / `performance_metrics` / `cutover_post_status` (pass / regression_detected / pending) / `pl_recommendation` (PASS / FAIL / FIX_DISCRETIONARY) / `root_cause` (code / design / requirements / cross-module) / `fix_lane` (develop / design / requirements / debate) / `debate_artifact_ref` / `production_evidence_quad`.

**검증 mode selection** (ADR-088 §결정 6): `http` (REST/GraphQL/gRPC — production 트래픽 shadow mirror) / `websocket`·`daemon` (WebSocket / 시세 수집 daemon / 백그라운드 worker — active connection 안정성 + 메시지 throughput). consumer 가 service 별 `project.yaml deploy.services[].verification_mode` 명시 (ADR-027 Amendment N).

**ProductionEvidence quad schema** (CONDITIONAL — ADR-72 Amendment 2 4 measurement source): MS-1 live_touching (functional) / MS-2 production_cutover_touching (dual-source AND) / MS-3 marketplace_publish_touching / MS-4 consumer_impact_blast_radius + EPIC CLOSED gate verify + Family atomic canary pin (publisher_versions[] length_invariant + 3-way match publisher ↔ registry ↔ consumer).

> 계약 schema field-level 상세 + version 값 = 각 contract file SSOT + MANIFEST.yaml. 본 섹션 = surface enumeration (계약 이름 + SSOT pointer, version literal 미박제 — version drift 회피).

## 데이터 흐름

**배포 리뷰 lane 진입 → 산출물 flow** (Orchestrator 가 lane 진입 시 DeployReviewPLAgent 1개 spawn — non-skippable):

```
[upstream] DeployPLAgent (배포 lane) green 컨테이너 healthcheck PASS, atomic swap 직전
  ↓ deploy_verdict (deployed_repos / blue_green_status) + green_containers + deploy_config + performance_baseline + production_cutover_touching
DeployReviewPLAgent (lane PL) spawn
  ↓ Story §13 production_cutover_touching 검토 (ProductionEvidenceDeputy CONDITIONAL spawn 결정 — 모호 시 default spawn)
  ↓
DeployReviewPL → spawn:
  ├─ DeployReviewWorkerAgent — 검증 3종 실 측정:
  │    ├─ smoke (verification_mode 분기: HTTP shadow request/response 비교 · WebSocket·daemon 대기 안정성)
  │    ├─ 성능 비교 baseline 수집 (latency p50/p95/p99 / throughput / error rate / CPU·memory, baseline 대비 delta)
  │    └─ cutover 사후 검증 (atomic swap 직후 ~ 3-시간 실 production 트래픽 회귀 감지)
  │       → worker_measurement packet 반환 (raw metric only, verdict 판정 금지)
  └─ [CONDITIONAL] ProductionEvidenceDeputyAgent — production evidence quad (MS-1~4) + EPIC CLOSED gate + Family canary pin
       → .claude-work/doc-queue/** 산출 + DeployReviewPL 반환
  ↓
DeployReviewPL — verdict 종합:
  ├─ smoke PASS + 성능 비교 PASS → pl_recommendation PASS → atomic swap 허용 신호 → blue 3-시간 보존
  └─ 성능 비교 FAIL (성능 회귀 감지) → root cause 1차 진단:
       ├─ code-level (구현 비효율)         → DeveloperPL FIX (구현 lane 재진입)
       ├─ design-level (architecture / 성능 모델) → ArchitectPL FIX (설계 lane 재진입)
       ├─ requirements-level (성능 기준 재조정) → RequirementsPL FIX (요구사항 lane 재진입)
       └─ cross-module (양 architect 분열)   → debate-protocol-v1 자동 발동 (ADR-059, Opus tier mandatory)
       ↓ ArchitectPL 최종 판정 (DeveloperPL 1차 진단 후 — ADR-035)
  ↓
[downstream] deploy_review_verdict → Orchestrator handoff (deploy-review-output 영역, Phase 1 placeholder)
```

**FIX 루프 데이터 흐름**:
- 성능 비교 FAIL → DeployReviewPL root cause 1차 진단 → lane back dispatch (develop / design / requirements / debate)
- cross-module 분열 시 debate-protocol-v1 발동 → transcript = Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry → re-spawn 시 verbatim 입력
- root cause 최종 판정 = ArchitectPL (DeveloperPL 1차 진단 후, ADR-035)

**cascade trigger chain** (ADR-088 결과 — templates/deploy-review-mechanism.md 명시):

```
Epic close → auto-deploy.yml (ADR-026 Amendment N + ADR-087)
  → DeployPLAgent spawn (배포 lane — 변경 repo blue-green sequence)
  → green healthcheck PASS → DeployReviewPLAgent spawn (본 lane — smoke + 성능 비교)
  → verdict PASS → atomic swap → blue 3-시간 보존 → cutover 사후 검증 (3-시간 한 번 끝나는 측정)
  → verdict FAIL → 자동 rollback + FIX dispatch (debate-protocol-v1 가능)
```

**artifact propagation**:
- Story file = lane 컨텍스트 SSOT (DeployReviewPL self-fetch — §13 production_cutover_touching / 성능 기준)
- worker_measurement packet = raw metric (DeployReviewWorker → DeployReviewPL, 1회 측정)
- deploy_review_verdict = 종합 verdict (DeployReviewPL → Orchestrator)
- 본 doc (architecture_doc) = 누적 현재 상태 (영속, Story key 독립)

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` 또는 `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
