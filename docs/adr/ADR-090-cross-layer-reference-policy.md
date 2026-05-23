---
adr_number: 90
title: Cross-layer 참조 정책 + 양 layer 동시 변경 순서 (source-first expand / leaf-first contract)
status: Accepted
category: governance
date: 2026-05-20
carrier_story: CFP-1059
parent_epic: CFP-1059
related_stories:
  - CFP-1059  # carrier Epic
related_adrs:
  - ADR-089  # Schema 변경 7 원칙 (sibling carrier — 본 ADR 이 §결정 1 원칙 5 cross-repo 영향 layer 구체화)
  - ADR-087  # Deploy lane (sibling carrier — 본 정책이 deploy lane mandatory invariant)
  - ADR-088  # Deploy Review lane (sibling carrier)
  - ADR-72  # ProductionEvidenceDeputy mandate
  - ADR-068  # boundary completeness invariants (I-2 cross-module propagation completeness cross-ref)
  - ADR-076  # declarative reconciliation (expand-contract pattern 동형)
  - ADR-083  # consumer-applicability filter (layer 별 적용 여부)
  - ADR-054  # doc-only fast-path
  - ADR-082  # write-time self-write verification
  - ADR-070  # Codex verify-before-trust (chief author direct write precedent)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무
  - ADR-058  # sunset criteria mandate (is_transitional: false ratchet 정합)
related_files:
  - docs/adr/ADR-089-schema-change-7-principles.md
  - docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
  - docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md
  - docs/adr/ADR-068-boundary-completeness-invariants.md
  - templates/github-workflows/cross-layer-impact-check.yml  # Phase 1 skeleton
  - templates/github-workflows/dependency-order-check.yml  # Phase 1 skeleton
  - templates/change-plan.md  # §11 데이터 마이그레이션 layer dependency 영역
amendment_log: []
amendments: []
is_transitional: false  # permanent governance — 약화 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null
mechanical_enforcement_actions:
  - cross-layer-impact-detection  # declaration-only Wave 1
  - dependency-order-enforce  # declaration-only Wave 1
---

# ADR-090 — Cross-layer 참조 정책 + 양 layer 동시 변경 순서

## 상태

`Accepted (2026-05-20 KST)` — CFP-1059 Epic Story-1 carrier. ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. doc-only fast-path (ADR-054 Category 2).

## 컨텍스트

### 동인

ADR-089 §결정 1 원칙 5 (Schema 변경 = cross-repo 영향 검증) 의 구체화 layer. consumer 가 multi-layer architecture (RDB layer / 빅데이터 layer / API layer / service repo) 운영 시 양 layer 동시 변경 시점이 발생 — 변경 순서가 부재하면 무중단 배포 불가.

### Consumer 사례 (mctrader)

CFP-1059 Epic spec §11 mctrader 5 layer 그래프 evidence:

```
mctrader-market / mctrader-market-bithumb / mctrader-market-upbit  (시세 수집 layer)
                          ↓
              mctrader-data  (빅데이터 — Parquet/MinIO/DuckDB/Redis)
                ┃ DataArchitect 책임 (OLAP only)
                          ↓
              mctrader-engine  (백테스트 — RDB + 빅데이터)
                ┃ AggregateArchitect (RDB) + DataArchitect (빅데이터) 협업
                          ↓
              mctrader-web  (UI/API)
                ┃ AggregateArchitect (RDB) + APIContractArchitect (transport+DTO) 협업
                          ↑
              PostgreSQL  (engine + web 공유)
                ┃ AggregateArchitect 책임 (RDB schema 결정자)

           (모든 layer 모듈 경계) ← ModuleArchitect 책임 (CFP-1086 rename)
```

### 변경 순서 문제 사례

- **expand (확장)**: 신규 column 을 `mctrader-data` 추가. 의존 chain = data → engine → web. **source-first**: `data` 먼저 신규 column 추가 (read 가능 시점 보장) → `engine` 추가 column 사용 → `web` 의 column 노출.
- **contract (정리)**: 구 column 을 `mctrader-data` 제거. **leaf-first**: `web` 먼저 column 미참조 (사용자 영향 0) → `engine` 미참조 → `data` 가 column drop.
- 순서 reverse 시 (source-first contract / leaf-first expand) = 의존 chain 위쪽에서 신규 column 참조 시도 → 아래쪽에 없음 → exception.

### 기존 ADR 영역 부족

- **ADR-089** = Schema 변경 7 원칙 (일반 invariant). 변경 순서 구체화 부재.
- **ADR-076** = expand-contract 패턴 (upgrade flow). cross-layer 의존 그래프 traverse 영역 부재.
- **ADR-068 I-2** = cross-module propagation completeness. 단일 module 내 enum propagation 영역 한정.

→ 본 ADR 이 cross-layer 영역 (RDB / 빅데이터 / API / service repo 의 cross-layer 의존) 구체화 layer.

### 사용자 결정 (2026-05-20 KST)

CFP-1059 brainstorm Phase 1 dialog 결과:

- 의존 매핑 = 자동 감지 + 사용자 declare hybrid
- 강제 강도 = 경고 (warning tier) + 사용자 declare 의무
- layer 별 분리 정책 = RDB strict / 빅데이터 lenient
- 변경 순서 = expand → source-first / contract → leaf-first
- 한쪽 실패 = 묶음 전체 rollback (atomic invariant)

## 결정

### §결정 1 — 의존 매핑 = 자동 감지 + 사용자 declare hybrid

자동 감지 source:

- `pyproject.toml` deps / `package.json` dependencies — service repo 간 직접 의존
- `docker-compose.yml` volume mounts — 공유 volume / 공유 DB connection
- ORM model declaration (Alembic env / SQLAlchemy model imports) — RDB schema 공유 감지
- inter-plugin contract MANIFEST — codeforge 영역 (consumer 에 적용 안 됨)

자동 감지 한계 → 사용자 declare 보충 (`project.yaml deploy.layer_dependencies[]`):

```yaml
deploy:
  layer_dependencies:
    - source: mctrader-data
      dependents: [mctrader-engine, mctrader-web]
      shared_layer: postgresql  # RDB layer 공유
    - source: mctrader-engine
      dependents: [mctrader-web]
      shared_layer: postgresql
    - source: mctrader-market
      dependents: [mctrader-data]
      shared_layer: redis-pubsub  # event layer 공유
```

자동 감지 + declare 가 둘 다 있으면 union (declare 가 cover 하지 못한 영역 자동 보완).

### §결정 2 — 강제 강도 = 경고 (warning tier) + 사용자 declare 의무

- 자동 감지 결과 + declare 결과 가 다를 때 (drift) → warning tier (Phase 2 PR open 시점 lint).
- 사용자가 declare 0 + 자동 감지 1+ 발견 → declare 의무 (PR comment 안내).
- declare 0 + 자동 감지 0 → 단일 repo 변경 영역 (cross-layer 영역 외) → pass-through.

→ blocking tier 승격 = Wave 5+ (consumer mctrader 실측 evidence accumulate 후 별 carrier).

### §결정 3 — layer 별 분리 정책 (RDB strict / 빅데이터 lenient)

| Layer | 정책 | 근거 |
|---|---|---|
| **RDB** (PostgreSQL / MySQL / SQLite) | **strict** — 양방향 호환 의무 + reverse 함수 의무 + backup 의무 (ADR-089 §결정 1 7 원칙 모두 PASS) | RDB = source of truth, 비가역 data 손실 위험, ACID 트랜잭션 lock 영향 |
| **빅데이터** (Parquet / MinIO / DuckDB / S3 / object store) | **lenient** — 양방향 호환 의무 + reverse 함수 권장 + backup 권장 (원칙 1+2+4 strict, 3+6 권장, 7 strict) | 빅데이터 = append-only / 재계산 가능, recovery 영역 (re-ingest / replay) |
| **API contract** (REST / GraphQL / gRPC / WebSocket) | **strict** — version bump (ADR-008) + 양방향 호환 + 양방향 smoke 의무 | API = consumer 다수, breaking 시 영향 광범위 |
| **event schema** (Kafka / queue / pub-sub) | **strict** — schema registry compat mode (`BACKWARD_TRANSITIVE` 또는 `FULL_TRANSITIVE`) + consumer-side 점진 migration | event = async, version mix 영역 길게 유지 |
| **config schema** (`project.yaml` / `compose.yml`) | **lenient** — additive only + deprecation 단계 (`deprecated: true` flag 6개월 후 remove) | config = restart 시점 적용, 점진 migration 가능 |

각 layer 정책은 consumer 영역에 따라 변경 가능 — `project.yaml deploy.layer_separation` (ADR-027 Amendment N).

### §결정 4 — 변경 순서 invariant

#### 4.1 expand = source-first ordering

신규 column / field / endpoint 추가 시 의존 chain 위쪽 (source / dependency target) 먼저 배포.

mctrader 사례 (data → engine → web):
1. `mctrader-data` 신규 column 추가 + 양방향 호환 보장 (nullable / default)
2. `mctrader-engine` 신규 column read/write 코드 추가
3. `mctrader-web` 신규 column UI 노출

→ 각 step 사이 atomic swap + 3-시간 보존 (ADR-087 §결정 5). 1개 Epic 안 3 step 묶음 가능 (consumer 영역) — 단 cascade trigger chain 의무 (auto-deploy.yml step ordering).

#### 4.2 contract = leaf-first ordering

구 column / field / endpoint 정리 시 의존 chain 아래쪽 (leaf / dependent) 먼저 배포.

mctrader 사례 (web → engine → data, expand 와 reverse):
1. `mctrader-web` 구 column UI 제거 (사용자 영향 0)
2. `mctrader-engine` 구 column 미참조 (read/write 코드 제거)
3. `mctrader-data` column drop (backup 의무 — ADR-089 §결정 1 원칙 6)

→ contract = 별 Epic 묶음 (ADR-089 §결정 1 원칙 2 expand-contract 분리). expand Epic 의 다음 N 번째 Epic 의 step 2 통합.

### §결정 5 — 한쪽 실패 = 묶음 전체 rollback (atomic invariant)

cross-layer 변경 묶음 안 1+ layer 가 healthcheck FAIL / smoke FAIL / 성능 미충족 → 묶음 전체 rollback.

- `auto-rollback.yml` workflow 가 cascade rollback trigger (Traefik label revert + 이전 image tag 재시작 + reverse migration 호출).
- rollback 후 묶음 전체 = 이전 state (3-시간 보존된 blue) 복원.
- partial rollback (일부 layer만 rollback) = 금지 — version mix 영역 불일치 위험.

### §결정 6 — 4 architect 책임 분담 (CFP-1086 cross-ref)

본 cross-layer 정책의 영역별 책임 분담 = CFP-1086 sibling Epic 결과 4 architect:

| 영역 | 책임 architect | 본 ADR 적용 |
|---|---|---|
| RDB schema (PostgreSQL aggregate / Alembic 정책) | **AggregateArchitect** (CFP-1086 신설) | §결정 3 RDB strict + §결정 4 ordering source/leaf-first |
| API contract (REST/GraphQL/gRPC/WebSocket + DTO + OpenAPI) | **APIContractArchitect** (CFP-1086 신설) | §결정 3 API strict + §결정 4 양방향 smoke anchor |
| 모듈 경계 + dependency direction | **ModuleArchitect** (CFP-1086 rename — CodeArch였음) | §결정 1 자동 감지 source enumeration + §결정 4 의존 chain traverse |
| 빅데이터 (Parquet/MinIO/DuckDB/streaming OLAP only) | **DataArchitect** (CFP-1086 축소) | §결정 3 빅데이터 lenient + §결정 4 ordering (data layer 위치) |

CFP-1086 Story-1 (ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086) 결과 적용. 본 ADR 이 4 architect mandate의 deploy-domain 적용 layer.

### §결정 7 — wrapper / lane plugin self-application = N/A

- 본 ADR-090 자체 carrier Story = doc-only fast-path. cross-layer 영역 0 — 본 정책 self-check 영역 외.
- codeforge 7 plugin family (wrapper + 6 lane) = inter-plugin contract layer 영역 — ADR-008 + ADR-089 §결정 1 7 원칙 cross-ref 적용 (본 ADR 외 영역).

### §결정 8 — Mechanical enforcement (declaration-only Wave 1)

- `mechanical_enforcement_actions: [cross-layer-impact-detection, dependency-order-enforce]` declaration-only Wave 1.
- 후속 evidence-check-registry entry 발의 시 (Story-7 mechanical wire 영역):
  - `cross-layer-impact-detection` → `cross-layer-impact-check.yml` workflow + `scripts/check-cross-layer-impact.sh` lint
  - `dependency-order-enforce` → `dependency-order-check.yml` workflow + `scripts/check-dependency-order.sh` lint
- bypass = `hotfix-bypass:cross-layer-impact` + `hotfix-bypass:dependency-order` label.


## 해소 기준

N/A — permanent policy

## 결과

### ChangePlan §11 cross-layer 영역 codify (Wave 2+)

`templates/change-plan.md` §11 데이터 마이그레이션 영역에 cross-layer dependency self-check 표 추가 (별 carrier CFP — Story-7 mechanical wire 영역):

```yaml
cross_layer_check:
  layer_dependencies_declared: <count>
  layer_dependencies_auto_detected: <count>
  drift_count: <count>  # declared vs auto-detected mismatch
  ordering_check:
    expand_source_first: PASS | FAIL | N/A
    contract_leaf_first: PASS | FAIL | N/A
  atomic_rollback_validated: PASS | FAIL | N/A
```

### Cascade workflow (ADR-087 §결정 7 + 본 §결정 4)

```
Epic close
  ↓
auto-deploy.yml (Epic close trigger)
  ↓
cross-layer-impact-check.yml — 의존 그래프 traverse + drift detect
  ↓
dependency-order-check.yml — expand=source-first / contract=leaf-first 검증
  ↓
expand chain 진행 (source-first ordering) — 각 layer 단계 별 blue-green + atomic swap + smoke
  ↓
한쪽 실패 시 auto-rollback.yml cascade rollback (atomic invariant 보존)
```

### 4 architect 책임 분담 적용 evidence

CFP-1086 Story-1 결과 4 architect (AggregateArch / APIContractArch / ModuleArch / DataArch) 책임 분담이 본 ADR 의 cross-layer 정책 domain 의 첫 적용 사례. CFP-1086 spec §3 "4 architect axis 명확화" 정합.

### Self-application bootstrap mitigation (ADR-082 §결정 2 정합)

본 ADR-090 작성 evidence:
- ADR-RESERVATION row 90 = CFP-1059 active (commit `2104183`)
- 3 sibling ADR (087/088/089) 모두 생성 verified (본 batch 이전 step)
- 본 ADR §결정 6 4 architect 책임 = CFP-1086 ADR-086 + ADR-042 Amendment 8 + ADR-068 Amendment 2 cross-ref verify

## 관련 파일

- [ADR-089](ADR-089-schema-change-7-principles.md) — sibling carrier (본 ADR 이 원칙 5 cross-repo 영향 구체화)
- [ADR-087](ADR-087-deploy-lane-and-lifecycle-extension.md) — sibling carrier (배포 lane mandatory invariant)
- [ADR-088](ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — sibling carrier
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — I-2 cross-module propagation completeness cross-ref
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — expand-contract pattern 동형
- [ADR-083](ADR-083-consumer-applicability-filter.md) — layer 별 적용 여부
- `templates/github-workflows/cross-layer-impact-check.yml` (Phase 1 skeleton)
- `templates/github-workflows/dependency-order-check.yml` (Phase 1 skeleton)
- `templates/change-plan.md` §11 cross-layer dependency 영역
