---
adr_number: 007
title: DataMigrationArchitectAgent 신설 — §11 데이터 마이그레이션 author input contributor
status: Accepted
category: Team & Process
date: 2026-04-28
related_files:
  - agents/DataMigrationArchitectAgent.md
  - agents/ArchitectAgent.md
  - agents/ArchitectPLAgent.md
  - agents/CodebaseMapperAgent.md
  - agents/RefactorAgent.md
  - agents/SecurityArchitectAgent.md
  - agents/TestContractArchitectAgent.md
  - templates/change-plan.md
  - templates/review-checklists/design.md
  - agents/DesignReviewPLAgent.md
  - agents/CodexReviewAgent.md
  - CLAUDE.md
  - docs/orchestrator-playbook.md
related_stories:
  - CFP-21
is_transitional: false
---

# ADR-007: DataMigrationArchitectAgent 신설

## 상태

Accepted (2026-04-28)

## 컨텍스트

ADR-004 §"후속 조치"는 Codex 감사 후속 항목 #1·#2·#4-#6을 본 plugin이 적용해야 할 항목으로 명문화했다. CFP-21은 그 중 #2 (High severity)의 직접 적용 — **데이터 layer 결정 누락 위험: 설계 시점에 schema 진화·migration 전략·rollback 경로·integrity invariant·backfill 정책이 누락되어 구현 테스트 / 보안 테스트 lane에서 발견되는 비싼 회귀 발생**.

ADR-006 (TestContractArch precedent) 패턴 그대로 isomorphic — author 비대칭 해소 mechanism 동일. ADR-004 §"긍정적" 결과의 "shift-left … FIX 회귀 비용 감소" 논거가 §11 데이터 마이그레이션에도 동등하게 적용.

## 결정

### 결정 1 — DataMigrationArchitectAgent 신설 (6번째 deputy)

ArchitectPLAgent 직속 6번째 deputy로 추가. CodebaseMapperAgent / RefactorAgent / SecurityArchitectAgent / TestContractArchitectAgent와 동급. SecurityArchitectAgent.md verbatim 도형으로 작성하되 도메인 substitution (§7→§11, 공격자→데이터 무결성 advocate).

본 deputy는 SecurityArch / TestContractArch와 마찬가지로 4-way 도형 대립에 참여하지 않는 별개 advocate가 아니라, **4-way 대립의 4번째 axis** (Mapper 보수 / Refactor 혁신 / SecurityArch 공격자 / DataMigrationArch 데이터 무결성). TestContractArch는 §8 author input contributor로서 도형 대립 비참여 영역 그대로 유지.

### 결정 2 — chief author 본문 author 권한 유지

§11 본문 author = ArchitectAgent (chief author) 유지. DataMigrationArch는 author input contributor (deputy 산출물 → chief author 통합). SecurityArchitectAgent:§7 / TestContractArchitectAgent:§8 패턴과 정확 동형.

### 결정 3 — 모든 Story 필수 스폰 + §11.6 N/A 권한

작은 버그·문서 전용 Story 포함 모든 Story에서 DataMigrationArch 스폰 의무. 단 §11.6 N/A 권한 보유 (ADR-005 `plugin-meta-na` / `runtime-inert` 분류 정합). N/A 사유 누락 시 DesignReview P0 차단 (SecurityArch §7.6 / TestContractArch §8.6 N/A 패턴 동형).

Consumer overlay에 `has_data_layer: false` (pure plugin meta / docs-only repo) 시 항상 N/A로 결과 가능 — 단 사유 1줄 의무.

### 결정 4 — 책임 경계 시점 분리

DataMigrationArch (Design lane) ≠ 구현 lane / 구현 테스트 lane:
- **DataMigrationArch (Design)**: "어떻게 schema가 진화해야 하는가" — 설계 결정 (예방)
- **DeveloperPL + role:dev:data (구현)**: "migration script가 §11.2 전략대로 작성되었는가" — 구현
- **TestAgent (구현 테스트)**: "migration이 staging에서 §11.4 invariant를 지키는가" — 구현 검증 (검출)

§11.4 Data integrity invariant 정의가 구현 테스트 lane "마이그레이션 검증"의 SSOT.

### 결정 5 — SecurityArch와의 책임 경계

겹치는 영역 (예: PII 데이터 schema 변경) 시 author 결정 규칙:
- **SecurityArch §7.4**: 민감 데이터 분류 + 흐름 + log 노출 금지 — "누가 무엇을 신뢰할 수 있는가"
- **DataMigrationArch §11.1·§11.5**: schema 영향 + backfill 전략 — "데이터가 어떻게 변하는가"

둘 다 산출물 제공 → ArchitectAgent chief author가 통합. 내용 중복 시 §7 우선, §11에서 cross-ref만.

### 부수 결정

1. **§11 데이터 마이그레이션 신규 섹션** (templates/change-plan.md §1-§10 → §1-§11) — §11.1 Schema 영향 + §11.2 Migration 전략 + §11.3 Rollback 경로 + §11.4 Data integrity invariant + §11.5 Backfill / 기존 데이터 처리 + §11.6 N/A
2. **DesignReview checklist §11 audit 신설** (3 P0 차단 룰: §11 누락 / §11.6 N/A 사유 부재 / DataMigrationArch 매핑 미반영)
3. **lane=design category enum 확장** (`data-migration` 카테고리 추가, 7 → 8)
4. **ArchitectPL Phase 1.5 sanity check 1 항목 추가** — §11 input 표면 형식 검사
5. **ArchitectPL 메타-규칙 1번에 §11 → DataMigrationArch 매핑 1행 추가** — §섹션별 deputy author input 통합 정합성
6. **min-privilege permissions** (SecurityArch §7.7 패턴) — WebSearch/WebFetch 허용 (migration tool docs / anti-pattern lookup 필요)

## 결과

### 긍정적

- shift-left 데이터 무결성: §11 데이터 마이그레이션이 설계 단계에서 별도 author input으로 가시화 → 구현 테스트 / 보안 테스트 lane FIX 회귀 비용 감소
- self-validation 분리: chief author가 §11 직접 author 아님 — DataMigrationArch input 통합 후 확정
- ADR-004 / ADR-006 패턴 세 번째 적용 — 구조적 정합성 검증 (dogfooding success metric)
- 4-way 이념 대립 강화 (Mapper / Refactor / SecurityArch / DataMigrationArch) — schema 안전성 단독 advocate 부재로 인한 implicit 책임 회피 차단
- Codex audit #2 (High severity) 직접 closure

### 부정적

- 설계 lane 토큰 비용 추가 증가: 5-agent (ArchitectPL + Architect + Mapper + Refactor + SecurityArch + TestContractArch) → 6-agent (+DataMigrationArch). 1 Story당 5-10k 토큰 추가 추정
- ArchitectPL 메타-규칙 통합 부담 증가 (deputy 산출물 5 → 6)
- Self-paradox: 본 CFP 자체는 DataMigrationArch 부재 상태에서 §11 N/A 처리 (CFP-17 / CFP-18 / CFP-19 / CFP-20 동일 패턴 — plugin meta paradox, ADR-005 정합)

### Trade-off

부정 영향(토큰 비용)은 ADR-004 / ADR-006 결정과 동일 trade-off — shift-left 데이터 무결성 가치가 비용 상회. full closure KPI(FIX 회귀 비용 감소) 1-2 Story 누적 후 PMOAgent 회고에서 측정.

## 해소 기준

N/A — permanent policy



```
[설계 lane — After v0.14.0]
ArchitectPLAgent (PL: supervisor + FIX judge)
 ├── ArchitectAgent (Chief Author)
 ├── CodebaseMapperAgent (보수 — as-is)
 ├── RefactorAgent (혁신 — to-be)
 ├── SecurityArchitectAgent (위협 — §7 author input)
 ├── TestContractArchitectAgent (QA perspective — §8 author input)
 └── DataMigrationArchitectAgent (데이터 무결성 — §11 author input) [NEW]
```

## 관련 파일

- `agents/DataMigrationArchitectAgent.md` (신설)
- `agents/ArchitectAgent.md` (§11 author 라인 + deputy 5인)
- `agents/ArchitectPLAgent.md` (Phase 1·1.5·2·3 deputy 5인 갱신, 메타-규칙 §11 1행 추가)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md`, `agents/SecurityArchitectAgent.md`, `agents/TestContractArchitectAgent.md` (cross-ref 1줄)
- `templates/change-plan.md` (§11 신설)
- `templates/review-checklists/design.md` (§11 audit + 3 P0 차단 룰)
- `agents/DesignReviewPLAgent.md` (category_enum + severity_overrides §11 P0 3건)
- `agents/CodexReviewAgent.md` (lane=design prompt category enum + auto-P0 §11)
- `CLAUDE.md`, `docs/orchestrator-playbook.md` (deputy 수 일괄, 24 core, 4-way 대립 재명명, 책임 매트릭스 §11 6행, FIX decision table 1행)
- `.claude-plugin/plugin.json`, `CHANGELOG.md`, `docs/migration-guide.md` (v0.14.0)
- `docs/adr/ADR-004-architectpl-securityarch-restructure.md` (#2 closure cross-ref)
