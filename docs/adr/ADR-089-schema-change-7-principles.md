---
adr_number: 89
title: Schema 변경 7 원칙 (양방향 호환 / expand-contract / reverse / 양방향 smoke / cross-repo / backup / hard limit)
status: Accepted
category: governance
date: 2026-05-20
carrier_story: CFP-1059
parent_epic: CFP-1059
related_stories:
  - CFP-1059  # carrier Epic
related_adrs:
  - ADR-087  # Deploy lane (sibling carrier — 본 7 원칙이 deploy lane mandatory invariant)
  - ADR-088  # Deploy Review lane (sibling carrier — §결정 4 양방향 smoke 검증 anchor)
  - ADR-090  # Cross-layer 참조 정책 (sibling carrier — §결정 5 cross-repo 영향 layer)
  - ADR-068  # boundary completeness invariants (I-1 API contract semantic completeness cross-ref / I-5 dimensional empirical grounding — hard limit empirical)
  - ADR-076  # declarative reconciliation (expand-contract pattern 동형 ratchet)
  - ADR-008  # inter-plugin contract versioning (양방향 호환 backward-compat 정책 cross-ref)
  - ADR-054  # doc-only fast-path
  - ADR-082  # write-time self-write verification
  - ADR-070  # Codex verify-before-trust (chief author direct write precedent)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무
  - ADR-058  # sunset criteria mandate (is_transitional: false ratchet 정합)
related_files:
  - docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
  - docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md
  - docs/adr/ADR-090-cross-layer-reference-policy.md
  - docs/adr/ADR-068-boundary-completeness-invariants.md
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md
  - templates/github-workflows/bidirectional-smoke.yml  # Phase 1 skeleton — §결정 4 anchor
  - templates/change-plan.md  # §11 데이터 마이그레이션 + §13 Phase 1 self-check 정합
amendment_log: []
amendments: []
is_transitional: false  # permanent governance — 약화 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null
mechanical_enforcement_actions:
  - schema-change-7-principles-self-check  # declaration-only Wave 1 (ADR-076 / ADR-082 / ADR-086 precedent 답습)
---

# ADR-089 — Schema 변경 7 원칙 (배포 lane mandatory invariant)

## 상태

`Accepted (2026-05-20 KST)` — CFP-1059 Epic Story-1 carrier. ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. doc-only fast-path (ADR-054 Category 2).

## 컨텍스트

### 동인

배포 lane (ADR-087) 신설에 따라 schema 변경 (DB schema / inter-plugin contract / API contract / event schema / project.yaml schema) 의 invariant SSOT 가 필요. 무중단 배포 (blue-green + atomic swap + 3-시간 보존) 매커니즘이 양방향 호환 의존 — schema 가 backward / forward 양방향 호환 없으면 blue (구버전) ↔ green (신버전) 트래픽 mix 영역에서 결함 발생.

### 기존 ADR 영역 부족

- **ADR-008** (inter-plugin contract versioning) = MAJOR/MINOR/PATCH semver + backward-compat rule. inter-plugin contract 한정.
- **ADR-068** (boundary completeness invariants) = I-1 API contract semantic completeness. 단일 contract 의 wording / docstring 영역.
- **ADR-076** (declarative reconciliation upgrade) = expand-contract pattern 활용 SSOT. upgrade flow 영역 한정.

→ Schema 변경 시 일반 invariant (DB schema / event schema / config schema 포함) SSOT 부재. 본 ADR 이 cross-domain 일반 invariant 영역 codify.

### 사용자 결정 (2026-05-20 KST)

CFP-1059 brainstorm Phase 1 dialog 결과:

> Schema 변경 시 양방향 호환 + expand-contract 분리 + reverse 가능성 + 양방향 smoke + cross-repo 영향 + 정리 전 백업 + hard limit 영역 명시 = 7 원칙

배포 lane mandatory invariant — schema 변경 발생 Story 시 ChangePlan §11 self-check 의무.

## 결정

### §결정 1 — 7 원칙 enumeration (배포 lane mandatory invariant)

각 schema 변경 (DB / API contract / event / config) 시 다음 7 원칙 모두 self-check 의무. 1+ FAIL = ChangePlan §11 FIX 의무 + Phase 2 PR open 차단.

#### 원칙 1 — 양방향 호환 (backward + forward compat)

- **Backward compat**: 신버전이 구 schema 의 데이터 / 호출 그대로 처리 가능. 신규 column / field 는 nullable 또는 default 보유.
- **Forward compat**: 구버전이 신 schema 의 데이터 / 호출에서 신규 필드 무시 가능. 신규 column / field 추가는 read path 영향 0 (필드 무시).

→ blue-green 동시 운영 시점 (atomic swap 직전) 에 양 버전이 같은 DB / queue 상태 공유 — 양방향 호환 없으면 swap 순간 deadlock 또는 data corruption.

#### 원칙 2 — 확장 (expand) PR / 정리 (contract) PR 분리

- **expand PR** = 신규 column / table / field 추가. 기존 코드 무영향 (nullable / default 보유).
- **contract PR** = 구 column / field 정리 (drop / rename). 별 Epic 의 step 2 통합 (먼저 신코드가 구 필드 미참조 검증 후).
- 같은 PR 안 expand + contract 동시 = 금지 (ADR-076 expand-contract 패턴 답습).

→ 무중단 배포 매커니즘 보장 (1 schema 변경 = 최소 2 Epic 묶음 — expand Epic + contract Epic).

#### 원칙 3 — reverse 가능성 (rollback path 명시)

- 모든 expand migration 은 reverse 함수 명시 의무 (Alembic `downgrade()` / 빅데이터 expand script 의 `--rollback` flag / RDB column add → drop reverse).
- contract migration 도 reverse 가능성 명시 — 다만 contract 는 비가역 영역 (예: data 손실) 가능 — 비가역 시 §결정 6 backup 의무로 cover.

→ 자동 rollback (ADR-087 §결정 5 단계 6 / `auto-rollback.yml`) trigger 시 reverse 호출.

#### 원칙 4 — 양방향 smoke test (old → new + new → old)

- **old → new smoke**: 구버전 client 가 신버전 server 호출 → 신규 필드 무시 + 구 필드 처리 PASS verify.
- **new → old smoke**: 신버전 client 가 구버전 server 호출 → 신규 필드 client-side 미사용 fallback PASS verify.

→ Deploy Review lane (ADR-088) 의 smoke 단계 영역. `bidirectional-smoke.yml` workflow Phase 1 skeleton — Phase 2 wire.

#### 원칙 5 — Schema 변경 = cross-repo 영향 검증

- DB schema (RDB) = 같은 DB 공유하는 service repo 모두 영향 (예: mctrader `engine` + `web` PostgreSQL 공유 시 양 repo audit).
- API contract / event schema = 호출 / 구독 service repo 모두 영향 (의존 그래프 traverse — ADR-090 carrier).
- inter-plugin contract = sibling sync (ADR-010 정합) + version bump (ADR-008).

→ ADR-090 cross-layer 참조 정책 sibling carrier 가 의존 그래프 자동 감지 + 사용자 declare hybrid 영역 cover.

#### 원칙 6 — 정리 (contract) 전 backup evidence 의무

- contract migration 실행 직전 = backup 의무 (RDB `pg_dump` / 빅데이터 snapshot / event queue replay log).
- backup retention = consumer declare (`project.yaml deploy.backup_retention_days` default 30일).
- backup evidence 가 없으면 contract PR merge 차단 (Phase 2 PR gate).

→ 비가역 data 손실 영역 안전망. 자동 rollback 매커니즘이 cover 못 하는 영역.

#### 원칙 7 — hard limit 영역 명시

- schema 변경이 다음 hard limit 1+ 초과 시 자동 흐름 외 + 사용자 수동 trigger 의무:
  - table column count 100+ 추가
  - row count 1억+ 영향
  - lock duration 5분+ 예상
  - cross-repo dependency 3+ depth
- hard limit 영역 = `auto-deploy.yml` skip + Issue label `deploy:hard-limit-manual` 자동 부착 + 사용자 점검 시간 알림.

→ 큰 변경은 "자동 무중단 보장 불가" 영역 — 사용자 사전 결정 의무.

### §결정 2 — ChangePlan §11 self-check 의무

`templates/change-plan.md` §11 데이터 마이그레이션 영역에 본 7 원칙 self-check 표 추가 (별 carrier CFP — DataMigrationArch 책임, 본 Epic Story-7 영역).

```yaml
schema_change_7_principles_self_check:
  P1_bidirectional_compat: PASS | FAIL | N/A
  P2_expand_contract_split: PASS | FAIL | N/A
  P3_reverse_possible: PASS | FAIL | N/A
  P4_bidirectional_smoke: PASS | FAIL | N/A
  P5_cross_repo_impact: PASS | FAIL | N/A
  P6_backup_before_contract: PASS | FAIL | N/A
  P7_hard_limit_declared: PASS | FAIL | N/A
```

1+ FAIL = ArchitectAgent FIX 의무 (Change Plan §11 갱신).

### §결정 3 — Wave 1 = declaration-only / Wave 2+ = mechanical lint

- `mechanical_enforcement_actions: [schema-change-7-principles-self-check]` declaration-only Wave 1 (ADR-076 / ADR-082 / ADR-086 precedent 답습).
- 후속 evidence-check-registry entry 발의 시 (Story-7 Phase 2 mechanical wire 영역) row append + lint script (`scripts/check-schema-7-principles.sh`) 활성.
- Wave 2+ mechanical lint = `schema-change-7-principles-self-check` warning tier 첫 도입 → Wave 5 blocking 승격 gate.

### §결정 4 — hard limit empirical evidence (ADR-068 I-5 cross-ref)

본 §결정 1 원칙 7 의 hard limit 4 영역 (column / row / lock / depth) 의 정량 threshold:

- column count 100+ → **[empirical-source: TBD]** — consumer 별 RDB engine threshold 실측 의무 (PostgreSQL 의 tuple width limit 8KB vs MySQL 의 row limit 65KB 영역 — mctrader PostgreSQL 사례 사후 lock-in)
- row count 1억+ → **[empirical-source: TBD]** — 실측 trigger (ALTER TABLE lock window) 의존
- lock duration 5분+ → **[empirical-source: TBD]** — consumer 의 acceptable_downtime_ms 정합 (`project.yaml deploy.acceptable_downtime_ms`)
- dependency depth 3+ → **[empirical-source: TBD]** — ADR-090 cross-layer 참조 정책 의존 그래프 traverse 결과 측정

ADR-068 I-5 dimensional empirical grounding cross-ref — Wave 2+ consumer mctrader 실측 후 carrier 별 CFP 가 정량 lock-in.

### §결정 5 — wrapper / lane plugin self-application = N/A

- 본 ADR-089 자체 carrier Story = doc-only fast-path (ADR-054 Category 2). schema 변경 0 — 본 원칙 self-check 영역 외.
- inter-plugin contract version bump (ADR-008 정합) = 본 7 원칙 동형 적용 가능 — Wave 2+ 영역.

## 결과

### 적용 영역

- **DB schema** (RDB Alembic / 빅데이터 expand script) — AggregateArch (CFP-1086) + DataArch 책임
- **inter-plugin contract** (kind:contract 7 entry — review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output / git_ops_event) — ADR-008 versioning + 본 7 원칙 cross-ref
- **API contract** (REST / GraphQL / gRPC / WebSocket) — APIContractArch (CFP-1086) 책임
- **event schema** (Kafka / queue / pub-sub event payload) — consumer 영역 (codeforge wrapper SSOT 외)
- **config schema** (`project.yaml`) — ADR-027 Amendment N (CFP-1059) 영역

### Bidirectional compat 정합 → ADR-008 §결정 2 cross-ref

ADR-008 §결정 2 (semver MAJOR = breaking) 와 본 §결정 1 원칙 1 (양방향 호환 강제) 정합:
- MAJOR bump = 본 원칙 위반 (양방향 호환 break) — 별 Epic step (2 Epic 묶음 의무) 필요
- MINOR bump = additive only (양방향 호환 보존) — 본 원칙 PASS

### Self-application bootstrap mitigation (ADR-082 §결정 2 정합)

본 ADR-089 작성 evidence:
- ADR-RESERVATION row 89 = CFP-1059 active (commit `2104183`)
- 4 sibling ADR (087/088/089/090) 중 087/088 이미 생성 (본 batch 이전 step)
- 본 ADR §결정 1 원칙 4 (양방향 smoke) → ADR-088 §결정 3 smoke 단계 cross-ref verify
- 본 ADR §결정 1 원칙 5 (cross-repo 영향) → ADR-090 cross-ref verify

## 관련 파일

- [ADR-087](ADR-087-deploy-lane-and-lifecycle-extension.md) — sibling carrier (배포 lane mandatory invariant)
- [ADR-088](ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — sibling carrier (§결정 1 원칙 4 양방향 smoke anchor)
- [ADR-090](ADR-090-cross-layer-reference-policy.md) — sibling carrier (§결정 1 원칙 5 cross-repo 영향 layer)
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — I-1 / I-5 cross-ref
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — expand-contract pattern 동형 ratchet
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — 양방향 호환 backward-compat 정책
- `templates/github-workflows/bidirectional-smoke.yml` (Phase 1 skeleton)
- `templates/change-plan.md` §11 데이터 마이그레이션 + §13 Phase 1 self-check 정합
