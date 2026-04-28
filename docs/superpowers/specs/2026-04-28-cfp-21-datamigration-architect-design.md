---
spec_id: cfp-21
title: DataMigrationArchitectAgent — 6번째 deputy (Codex audit #2 대응, BREAKING)
status: Approved
date: 2026-04-28
authors:
  - Orchestrator (synthesis)
  - CodexReviewAgent (#2 audit, GPT-5)
related_adrs:
  - ADR-004 (ArchitectPL + SecurityArch — same pattern)
  - ADR-006 (TestContractArch — 5th deputy precedent)
related_files:
  - agents/DataMigrationArchitectAgent.md (NEW)
  - agents/ArchitectPLAgent.md
  - agents/ArchitectAgent.md
  - agents/CodebaseMapperAgent.md
  - agents/RefactorAgent.md
  - agents/SecurityArchitectAgent.md
  - agents/TestContractArchitectAgent.md
  - templates/change-plan.md (§3.X data migration)
  - templates/review-checklists/design.md
  - agents/ClaudeReviewAgent.md
  - agents/CodexReviewAgent.md
  - docs/orchestrator-playbook.md
  - CLAUDE.md
  - docs/adr/ADR-007-datamigration-architect.md (NEW)
  - CHANGELOG.md
  - docs/migration-guide.md
---

## 0. 사용자 원문 (verbatim)

> 다음 실행 (CFP series autonomous progression — Codex audit #2 deferred queue)

## 1. 컨텍스트 — Codex audit #2

ADR-004 §"후속 조치" + v0.11.0 sprint 회고 §2.1에서 명시:

> #2 (High) — 데이터 layer 결정 누락 위험. 새 agent OR Change Plan §섹션.

CFP-19/CFP-20 머지로 N=5 deputy (Mapper · Refactor · SecurityArch · TestContractArch + chief author) 안정화 완료. 데이터 마이그레이션·schema 진화·rollback 결정은 현재 ArchitectAgent chief author의 implicit 책임이지만 **독립 advocate 부재** — schema 변경 영향 범위·downtime risk·rollback path가 설계 시점에 누락되면 구현 테스트 / 보안 테스트 lane에서 발견되어 비싼 회귀 발생.

본 CFP는 Codex audit #2를 ADR-004 deputy advocate 패턴으로 적용 — DataMigrationArchitectAgent 6번째 deputy 신설.

## 2. 결정

ADR-004 / ADR-006 패턴 그대로 차용 — 신규 6번째 deputy 추가. SecurityArch가 trust boundary advocate인 것처럼, DataMigrationArch는 **데이터 무결성·마이그레이션 안전성 advocate**.

### 2.1 deputy 책임 분담

| Deputy | 관점 | 주요 산출물 |
|--------|------|------------|
| CodebaseMapper | as-is 변호 | §2 현재 구조 |
| Refactor | to-be 혁신 | §3·§6 도입 설계 + 리팩터링 |
| SecurityArch | 공격자 (Trust) | §7 보안 설계 |
| TestContractArch | QA perspective | §8 Test Contract |
| **DataMigrationArch (NEW)** | **데이터 무결성 (Migration)** | **§3.X 또는 §11 데이터 마이그레이션** |

### 2.2 Change Plan 신규 §11 데이터 마이그레이션

새 §섹션 **§11. 데이터 마이그레이션** (DataMigrationArchitectAgent 입력 — 누락 시 DesignReview P0 차단). §11 구조:

```
## §11.1 Schema 변경 영향
- 변경 대상 테이블/컬렉션/인덱스 + 변경 유형 (ADD/MODIFY/DROP)
- 기존 데이터 행/문서 수 추정 + impact 분석

## §11.2 Migration 전략
- 마이그레이션 방식 (online/offline/blue-green/dual-write)
- Lock 시간 추정 + downtime 허용 여부
- Backward/forward compatibility (구버전 코드가 새 schema 읽을 수 있는가, 그 반대)

## §11.3 Rollback 경로
- 실패 시 rollback 스크립트/절차
- Rollback이 데이터 손실 동반하는 지점 명시
- Point of no return 지점

## §11.4 Data integrity invariant
- Migration 전후 불변식 (예: row count 보존, FK 정합성, NULL 비율)
- 검증 쿼리·체크포인트

## §11.5 Backfill / 기존 데이터 처리
- Default value 정책
- Backfill 배치 전략 (chunk size, throttle)

## §11.6 N/A 명시 (DB·migration 무관 시)
- "본 Story는 데이터 layer 변경 없음 — migration 분석 N/A"
- 근거 1줄
```

§7 (보안 설계) 패턴 동일 — N/A 사유 부재 시 DesignReview P0 차단.

### 2.3 Trust boundary와 책임 분리

DataMigrationArch ≠ SecurityArch overlap:
- **SecurityArch**: trust boundary·외부 입력·credential·auth → 누가 신뢰할 수 있는가
- **DataMigrationArch**: schema 진화·rollback·integrity invariant → 데이터가 어떻게 변하는가

겹치는 영역 (예: PII 데이터 schema 변경): SecurityArch가 §7.4 민감 데이터 분류, DataMigrationArch가 §11.1 schema 영향. 둘 다 산출물 제공 → ArchitectAgent chief author가 통합.

### 2.4 conditional 적용 vs always-spawn

다른 deputy처럼 **always-spawn + null 결과 권한**. plugin meta / docs-only / pure UI Story는 §11.6 N/A 사유 명시 (1줄). consumer overlay에 `has_data_layer: false`이면 항상 N/A로 결과 — 그래도 spawn 비용은 minor (~3-5k tokens/Story).

## 3. BREAKING 영향 + Migration

### 3.1 BREAKING

- **agent count**: 23 → 24 core
- **deputy count**: 5 → 6 (ArchitectPL view), 4 → 5 (ArchitectAgent peer view)
- **Change Plan template**: §1-§10 → §1-§11 (신규 §11)
- **DesignReview checklist**: §11 누락 차단 룰 추가
- **lane=design category enum**: 신규 `data-migration` 추가 (Claude/Codex review packet)

### 3.2 Migration

Consumer overlay 영향 — `has_data_layer` 도입 (default `true`). 기존 consumer는 N/A 사유 명시 의무. 자세한 절차는 [docs/migration-guide.md](../../migration-guide.md) v0.13.0 → v0.14.0 절.

## 4. ADR 영향

신규 **ADR-007** (Status: Accepted, 2026-04-28) — DataMigrationArchitectAgent 도입 결정. ADR-004 (§"후속 조치" #2)에서 명시한 후속 항목 #2의 직접 적용. ADR-006 (TestContractArch precedent) 패턴 따름.

ADR-001/004/005/006 본문 변경 없음 (각각의 결정은 그대로 유효, ADR-007이 추가 deputy 결정 별도 기록).

## 5. 비결정 (deferred)

- **§section ownership model** (deputy를 §섹션 single-author로 재정의) — 본 CFP 후 N=6 deputy 안정화 완료 시 별도 ADR-008 발의
- **DataMigrationArch deep audit (Codex follow-up)** — 본 CFP 후 dogfooding으로 첫 Story 적용 시 발견사항 수집

## 6. Test Contract 후보 (§8)

본 CFP는 plugin meta paradox이라 자기 적용 안 함. §8 N/A.

invariant-check.yml로 자동 검증:
- Step 3: agent count 23→24 ↔ CLAUDE.md "24 core" parity
- Step 6: lane=design category enum (Claude/CodexReview) ↔ design.md SSOT (`data-migration` category 신규)
- Step 8: severity overrides count (design checklist §11 P0 룰 추가)

## 7. 보안 영향 (§7)

Trust boundary 변화 없음. 신규 deputy의 권한은 SecurityArch 동일 패턴 (Read/Grep/Glob/read-only Bash + write queue + WebSearch/WebFetch). 외부 호출 추가 없음.

§11 데이터 마이그레이션 결정은 SecurityArch §7.4 민감 데이터와 cross-ref — chief author가 통합.

## 8. 후속

본 CFP 머지 후 v0.14.0 release. 다음 deferred:
- ADR-008 §section ownership model (BREAKING — deputy를 single-section author로 재정의)
- CFP-22+ Codex audit #4-#6 묶음 (관측성·API 호환·SLO checklist) — 이미 CFP-20 부분 적용됨, 잔여 항목만

## 9. 참고

- ADR-004 후속 #2: [docs/adr/ADR-004-architectpl-securityarch-restructure.md](../../adr/ADR-004-architectpl-securityarch-restructure.md) §"후속 조치"
- v0.11.0 sprint 회고 §2.1: [docs/retros/2026-04-27-v0.11.0-sprint-close.md](../../retros/2026-04-27-v0.11.0-sprint-close.md)
- ADR-006 (precedent): [docs/adr/ADR-006-testcontract-architect.md](../../adr/ADR-006-testcontract-architect.md)
