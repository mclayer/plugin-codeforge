# 배포 리뷰 매커니즘 template (성능 측정 + cutover evidence 4-quad)

> consumer application repo 의 배포 리뷰 매커니즘 참조 template. 실 workflow yml seed = wrapper repo `templates/github-workflows/bidirectional-smoke.yml` (CFP-1059 Story-1). 본 file 은 검증 3종 + cutover evidence 4-quad 참조용.

## 검증 3종 (한 번 끝나는 — ADR-088 §결정 3)

| 검증 | 시점 | 매커니즘 | verdict 영향 |
|---|---|---|---|
| smoke | atomic swap 직전 (green healthcheck 후) | HTTP shadow / WebSocket·daemon 대기 | FAIL → atomic swap 차단 + rollback |
| 성능 비교 | atomic swap 직전 (smoke 후) | latency p50/p95/p99 / throughput / error rate / CPU·memory baseline 대비 | FAIL → root cause 진단 + lane back |
| cutover 사후 검증 | atomic swap 직후 ~ 3-시간 보존 종료 | 실 production 트래픽 회귀 감지 | regression → 자동 rollback (EC-4) |

## 검증 mode selection (ADR-088 §결정 6)

| Service 유형 | verification_mode | 매커니즘 |
|---|---|---|
| REST/GraphQL/gRPC API | `http` | production 트래픽 shadow mirror (request/response 비교) |
| WebSocket / 시세 수집 daemon / 백그라운드 worker | `websocket` 또는 `daemon` | active connection 안정성 + 메시지 throughput 측정 |

consumer `project.yaml deploy.services[].verification_mode` 명시 (ADR-027 Amendment N).

## 성능 미충족 시 회귀 (ADR-088 §결정 5)

```
성능 비교 FAIL
  ↓ DeployReviewPL root cause 1차 진단
  ├── code-level → DeveloperPL FIX (구현 lane)
  ├── design-level → ArchitectPL FIX (설계 lane — 성능 모델 결정)
  ├── requirements-level → RequirementsPL FIX (요구사항 lane — 성능 기준 자체 재조정)
  └── cross-module (양 architect 분열) → debate-protocol-v1 자동 발동 (ADR-059)
  ↓
ArchitectPL 최종 판정 (DeveloperPL 1차 진단 후 — ADR-035)
```

## cutover evidence 4-quad (ProductionEvidenceDeputy — ADR-072 이관, production cutover-touching 시)

| Quad | 내용 |
|---|---|
| MS-1 functional (live_touching) | Live Operational Discipline / real funds / live API / production credential |
| MS-2 production_cutover_touching (dual-source AND) | §13 선언 + (deployment artifact / marketplace 발행 / infra topology) 1+ |
| MS-3 marketplace_publish_touching | family plugin marketplace.json bump 동반 |
| MS-4 consumer_impact_blast_radius | consumer configuration / policy / runtime behavior 영향 |

## [empirical-source: TBD] annotation (ADR-068 I-5)

성능 baseline (latency p50/p95/p99 / throughput / error rate) = consumer mctrader 첫 적용 시 실측 후 lock-in. 첫 측정 시 절대값 기록 + TBD marker.

## cascade trigger chain (ADR-088 결과)

```
Epic close
  ↓ auto-deploy.yml (ADR-026 Amendment N + ADR-087)
DeployPLAgent spawn (배포 lane) — 변경 repo enumeration + blue-green sequence
  ↓ green 컨테이너 healthcheck PASS
DeployReviewPLAgent spawn (배포 리뷰 lane, 본 lane) — smoke + 성능 비교
  ↓
verdict: PASS → atomic swap trigger → blue 3-시간 보존
verdict: FAIL → 자동 rollback + FIX dispatch (debate-protocol-v1 가능)
  ↓
atomic swap 후 cutover 사후 검증 (3-시간 동안 한 번 끝나는 측정)
```
