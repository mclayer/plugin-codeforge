---
adr_number: 46
title: Framework Migration Epic Pattern — PMOAgent Version Delta Review + Deputy Migration Notes
date: 2026-05-09
status: Proposed
category: Team & Process
carrier_story: CFP-316
related_files:
  - docs/orchestrator-playbook.md
  - templates/change-plan.md
  - docs/consumer-guide.md
related_stories:
  - CFP-316
amends: null
supersedes: null
---

# ADR-046: Framework Migration Epic Pattern

## 상태

Proposed (2026-05-09) — CFP-316 carrier.

## 컨텍스트

consumer 작업이 커지면서 codeforge framework 진화(새 deputy 추가, §section 변경, ADR 변경 등) 시 기존 Stories/Change Plans/ADRs의 구조 재편이 필요한 경우가 빈번하게 발생한다.

**기존 메커니즘의 한계**:
- DataMigrationArchitectAgent (ADR-007): scope = story-time DB schema migration (§11). Framework-level migration은 명시적 비-범위 (ADR-007 §결정 4)
- ADR-027/ADR-032 Consumer Adoption Protocol: bootstrap enforcement (plugin 설치, hook 등록, label 존재 검사). 신규 consumer 초기 setup만 다룸 — framework 진화에 따른 지속적 migration 비-범위
- PMOAgent: cross-story visibility, Epic 관리, 회고 담당 — 이미 Migration Epic 유형의 작업을 가장 잘 처리할 수 있는 위치에 있으나, Framework Delta Review trigger가 정의되지 않음

**Codex 2-round feasibility review (2026-05-09)**:
- Round 1 (blank-slate): Option 5 (Migration Epic 공식화) 선호, 전용 agent REJECT
- Round 2 (full transfer): Combined 1+4+5 수렴, 전용 agent REJECT (동일 결론)
- 양쪽 모두: "episodic problem, dedicated agent 정당화 임계 미달"

**핵심 통찰**: "빈번한 영향"이 전용 agent를 정당화하지 않는다. PMOAgent가 이미 cross-story visibility를 보유하고 있으며, 필요한 것은 전문화된 인지가 아니라 구조화된 워크플로우다.

## 결정

### 결정 1 — 전용 MigrationPlannerAgent 신설 REJECT (현재 아키텍처)

전용 MigrationPlannerAgent는 다음 조건 중 하나가 충족될 때까지 비-범위:
- codeforge가 월 1회 이상 breaking change 릴리즈
- 복수 consumer repo 병렬 migration 추적 필요
- Migration complexity가 PMOAgent 일반 인지를 초과 (자동 호환성 검사 필요)

현재 아키텍처에서 이 조건 중 하나도 충족되지 않음. 재검토는 별도 CFP.

### 결정 2 — PMOAgent Version Delta Review trigger 추가 (Option 1)

PMOAgent의 기존 trigger (Story 완료 회고, Epic 관리, Cross-Story 패턴 분석)에 **Version Delta Review** 추가:

**Trigger timing**: Framework Delta Event 발생 후 5분 이내 (또는 사용자 수동 trigger)

**Version Delta Review 프로세스**:
1. Framework Delta Event 종류 판별 (4 Types — §결정 4 참조)
2. 기존 진행 중인 Stories/Change Plans의 §section 구조 점검
3. Material drift 판별:
   - patch bump / advisory-only ADR: "no migration needed" 보고서
   - minor/major bump 또는 신규 deputy 또는 §section 신설: Migration Epic 후보 평가
4. Migration Epic 생성 또는 "no action" 결정 → Story §11에 기록

### 결정 3 — Deputy Migration Notes 의무화 (Option 4)

각 design deputy는 자신이 owning하는 §section이 변경될 때 Migration Notes 게시 의무:

| Deputy | Owned §section | Migration Notes 트리거 |
|---|---|---|
| CodebaseMapperAgent | §4 관련 코드 경로 | as-is 표현 방식 변경 |
| RefactorAgent | §6 리팩터링 선행 | 새 리팩터링 패턴 추가 |
| SecurityArchitectAgent | §7 보안 설계 | §7 sub-section 추가/변경 |
| TestContractArchitectAgent | §8 Test Contract | §8.5 Stateful invariant 추가 등 |
| DataMigrationArchitectAgent | §11 데이터 마이그레이션 | §11 sub-section 추가/변경 |
| OperationalRiskArchitectAgent | §7.4 DR/failover | §7.4 sub-section 추가/변경 |

**Migration Notes 포맷**:
```
## Migration Note: <deputy name> — <version-or-adr-ref>

**변경 사항**: <1줄 요약>
**기존 §X 보유 Story 적용**: <retrofit 가이드 2-5줄>
**N/A 조건**: <해당 없는 경우>
```

### 결정 4 — Framework Delta Event 4 Trigger Types 공식 정의

| Type | 설명 | PMOAgent 반응 |
|---|---|---|
| Type A — Version bump | codeforge version bump in consumer project | patch: advisory review / minor·major: Migration Epic 후보 |
| Type B — ADR 변경 | Story 구조/lane 동작에 영향을 주는 신규·실질적 ADR 변경 | 영향 범위 평가 후 Migration Epic 여부 결정 |
| Type C — Deputy 변경 | 신규 deputy 추가 또는 deputy mandate 변경 (새 필수 §section 발생) | 진행 중 Story에 새 §section 추가 Migration Story 생성 |
| Type D — Bootstrap 변경 | ADR-027/ADR-032 enforcement 변경 | consumer-guide 업데이트 + bootstrap 재검증 Migration Story |

### 결정 5 — Migration Epic Pattern + Tiered §5 Template (Option 5)

Migration Epic = ADR-020 Cross-Repo Epic Pattern의 codeforge framework-specific 적용.

**Delta 크기에 따른 tiered template**:

| Delta 크기 | 필수 §section | 면제 (N/A 허용) |
|---|---|---|
| Small (1-2 ADR 변경, 새 deputy 없음) | §1 + §4 | §2, §3, §5 (N/A 사유 1줄) |
| Medium (새 deputy mandate, 새 §section 추가) | §1 + §2 + §3 + §4 | §5 (N/A 허용) |
| Large (breaking change, §structure 재편) | §1 + §2 + §3 + §4 + §5 | — |

**Migration Epic §5 필수 섹션**:

- **§1 Framework Delta Summary**: codeforge 버전 범위, 변경된 ADR 목록, 신규/변경 deputy, 변경된 §section
- **§2 Affected Artifact Inventory**: 진행 중 Stories + Change Plans + ADRs + hooks + labels 영향 목록
- **§3 Deputy Migration Notes**: deputy별 domain-specific retrofit 가이드 (§결정 3 포맷)
- **§4 Migration Story Backlog**: PMO-owned 순서화된 remediation Story 목록 + AC (각 Story = 1 consumer repo 또는 1 §section 단위)
- **§5 Completion Gate**: bootstrap PASS + 열린 Stories §sections 갱신 완료 + ADR alignment 확인

## 결과

### 긍정적

- PMOAgent 기존 cross-story visibility 재활용 — 전용 agent 토큰 비용 0
- Deputy Migration Notes가 §section 변경 시 retrofit 부담을 domain expert에게 shift-left
- Tiered template으로 작은 delta에서의 overhead 최소화
- 전용 agent 신설 없음 → 아키텍처 복잡도 유지

### 부정적

- PMOAgent 책임 확장 → 회고 + epic management + Version Delta Review = 3 trigger 처리
- Deputy Migration Notes 작성 의무가 모든 deputy에게 추가 부담 (단, N/A 조건 명시로 완화)

### Trade-off

빈번한 framework 진화 (거의 모든 작업에서 영향 발생) → Option 5 (Migration Epic)를 예외가 아닌 **루틴 메커니즘**으로 설계. Tiered template이 소규모 delta에서의 overhead를 조절.

## Risk

| Risk | Mitigation |
|---|---|
| PMOAgent Version Delta Review 누락 | Framework Delta Event = well-defined 4-type. SessionStart hook에 version bump 감지 추가 후보 |
| Deputy Migration Notes 게시 지연 | deputy mandate에 명시 (§결정 3). DesignReview P1로 감사 |
| Migration Epic tiered 분류 오류 (small vs medium) | PMOAgent가 delta 크기 판별 → 사용자 확인 optional |
| 전용 agent 재검토 기준 불명확 | §결정 1 재검토 3개 조건 명시 — 별도 CFP 트리거로 사용 |

## Out-of-scope

- 전용 MigrationPlannerAgent 신설 (재검토 조건 미충족 — §결정 1)
- 자동 migration script 생성 (consumer 수동 또는 별도 Tool)
- codeforge version bump 자동 감지 CI/CD (별도 CFP — SessionStart hook 확장 후보)
- ADR-007 DataMigrationArch scope 변경 (story-time DB migration 유지)
- ADR-027/032 기존 bootstrap enforcement 변경 (Delta Event Type D는 감지만)

## 관련 파일

- `docs/orchestrator-playbook.md` (PMOAgent trigger 섹션 갱신 — Phase 2)
- `docs/consumer-guide.md` (Migration Epic Pattern 신규 §X — Phase 2)
- `docs/adr/ADR-007-datamigration-architect.md` (비-범위 cross-ref)
- `docs/adr/ADR-020-cross-repo-epic-pattern.md` (Migration Epic = ADR-020 적용)
- `docs/adr/ADR-027-consumer-adoption-protocol.md` (Delta Event Type D cross-ref)
- carrier story: `codeforge-internal-docs/wrapper/stories/CFP-316.md`
