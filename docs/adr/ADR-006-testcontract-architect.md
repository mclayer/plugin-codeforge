---
adr_number: 006
title: TestContractArchitectAgent 신설 — §8 Test Contract author input contributor
status: Accepted
category: Team & Process
date: 2026-04-27
related_files:
  - agents/TestContractArchitectAgent.md
  - agents/ArchitectAgent.md
  - agents/ArchitectPLAgent.md
  - agents/QADeveloperAgent.md
  - agents/SecurityArchitectAgent.md
  - templates/change-plan.md
  - CLAUDE.md
  - docs/orchestrator-playbook.md
related_stories:
  - CFP-18
---

# ADR-006: TestContractArchitectAgent 신설

## 상태

Accepted (2026-04-27)

## 컨텍스트

ADR-004 라인 70-72는 Codex 감사 후속 항목 #1·#2·#4-#6을 본 plugin이 적용해야 할 항목으로 명문화했다. CFP-18은 그 중 #1 (Top-1, High severity)의 직접 적용 — **§8 Test Contract가 chief author(ArchitectAgent) 단독 author이라 설계 시점 QA 견제 부재, self-validation 위험**.

ADR-004 패턴(보안 설계가 §7으로 SecurityArchitectAgent에 분리됨)과 isomorphic — author 비대칭 해소 mechanism 동일.

추가 외부 정당성 (Researcher §6.1 Insight 1·2·3):
- Kubernetes KEP / NASA SWE-087 / IEC 61508 — "Reviewers/Approvers distinct from authors" 원칙
- BDD Three Amigos / Shift-left QA — "design author = test author" 단일 author 모델 거부
- DevSecOps deputy 패턴 — Security ≠ QA, QA를 design phase 별도 author로 의무화

## 결정

### 결정 1 — TestContractArchitectAgent 신설 (5번째 deputy, Option A)

ArchitectPLAgent 직속 5번째 deputy로 추가. CodebaseMapperAgent / RefactorAgent / SecurityArchitectAgent와 동급. SecurityArchitectAgent.md verbatim 도형으로 작성하되 도메인 substitution (§7→§8, 공격자→QA perspective contributor).

**사용자 BLOCKING-1 결정 verbatim**: "Option A: 5번째 deputy (ArchitectPL 직속, Mapper/Refactor/SecurityArch와 동급)"

### 결정 2 — chief author 본문 author 권한 유지

§8 본문 author = ArchitectAgent (chief author) 유지. TestContractArch는 author input contributor (deputy 산출물 → chief author 통합). SecurityArchitectAgent:§7 패턴과 정확 동형.

**사용자 BLOCKING-2 결정 verbatim**: "QA perspective contributor: deputy는 §8 author input 제공, §8 본문 author는 chief author 유지 (SecurityArch:§7 패턴 정확 동형)"

### 결정 3 — 모든 Story 필수 스폰 + §8.6 N/A 권한

작은 버그·문서 전용 Story 포함 모든 Story에서 TestContractArch 스폰 의무. 단 §8.6 N/A 권한 보유 (ADR-005 `plugin-meta-na` / `runtime-inert` 분류 정합). N/A 사유 누락 시 DesignReview P0 차단 (SecurityArch §7.6 N/A 패턴 동형).

**사용자 BLOCKING-3 결정 verbatim**: "모든 Story 필수 + §8.6 N/A 권한 (작은 버그·문서 전용 N/A 허용 — ADR-005 정합)"

### 결정 4 — §7 단독 + §8 cross-reference만

보안 테스트 항목은 SecurityArch가 §7.5에 단독 author. §8은 §7.5 항목을 cross-reference만 ("→ §7.5 T-N 참조"). §7-§8 경계 겹침 시 author 결정 규칙: §7 우선, §8 cross-ref. 양 agent md ("§7 ↔ §8 cross-reference 규칙" 섹션) mutual reference.

**사용자 BLOCKING-4 결정 verbatim**: "§7 단독 + §8 cross-reference만 (보안은 §7 영역, §8은 reference만)"

### 결정 5 — 부분 closure (CFP-18 머지) / full closure (후속 Story 동작)

Codex audit #1 closure 정의를 2단계로 분리:
- **부분 closure**: CFP-18 머지 시점 — ADR-006 채택 + 19 SSOT 갱신 + TestContractArch.md 신규 author. **문서 정합 완료** 상태
- **full closure**: 후속 Story 1건 이상이 새 lane으로 실제 동작 검증 완료 — TestContractArch가 실제 §8 author input contribute, ArchitectPL 메타-규칙 검수 PASS, FIX Ledger 회귀 비용 감소 KPI 측정

**사용자 BLOCKING-5 결정 verbatim**: "부분/full closure 분리 (CFP-18 머지로 부분, 후속 Story 동작으로 full)"

### 부수 결정

1. **ArchitectPL 검수 4 항목 → 메타-규칙 2 항목 압축** (Refactor STRONG ROI #1) — deputy N+1 추가 시 enumerate 폭증 회피
2. **TestContractArch ↔ QADev mutual reference** (Refactor STRONG ROI #3) — 시점/산출물 분리 invariant 명문 cross-ref
3. **min-privilege permissions** (SecurityArch §7.7) — WebSearch/WebFetch 제거 (TestContractArch 외부 lookup 불필요)
4. **ADR-005 status 전이** — `Proposed` → `Accepted` (CFP-17/18 두 번 dogfooding 검증 완료)
5. **`templates/change-plan.md` §8.4 N/A 권한 신설** — `plugin-meta-na` / `runtime-inert` 분류 (ADR-005 정합)

## 결과

### 긍정적

- shift-left QA: §8 Test Contract가 설계 단계에서 별도 author input으로 가시화 → 구현/보안 테스트 lane FIX 회귀 비용 감소 (full closure KPI)
- self-validation 분리: chief author가 §8 직접 author 아님 — TestContractArch input 통합 후 확정
- ADR-004 패턴 두 번째 적용 — 구조적 정합성 검증 (dogfooding success metric)
- ArchitectPL 검수 메타-규칙화 → deputy N+1 추가 시 SSOT 갱신 부담 일정 (drift 방지 ROI)
- BDD/Shift-left/DevSecOps 외부 정당성 3중 (Researcher Insight 1·2·3)

### 부정적

- 설계 lane 토큰 비용 추가 증가: 5-agent (ArchitectPL + Architect + Mapper + Refactor + SecurityArch) → 6-agent (+TestContractArch). 1 Story당 5-10k 토큰 추가 추정
- ArchitectPL 메타-규칙 항목으로 압축됐지만 deputy 5인 산출물 통합 부담 증가
- self-paradox: 본 Story 자체는 TestContractArch 부재 상태에서 §8 N/A 처리 (Story §1 verbatim 인지)

### Trade-off

부정 영향(토큰 비용)은 ADR-004 결정과 동일 trade-off — shift-left QA 가치가 비용 상회. full closure KPI(FIX 회귀 비용 감소) 1-2 Story 누적 후 PMOAgent 회고에서 측정.

## 다이어그램

```
[설계 lane — After v0.12.0]
ArchitectPLAgent (PL: supervisor + FIX judge)
 ├── ArchitectAgent (Chief Author)
 ├── CodebaseMapperAgent (보수 — as-is)
 ├── RefactorAgent (혁신 — to-be)
 ├── SecurityArchitectAgent (위협 — §7 author input)
 └── TestContractArchitectAgent (QA perspective — §8 author input) [NEW]
```

## 관련 파일

- `agents/TestContractArchitectAgent.md` (신설)
- `agents/ArchitectAgent.md` (§8 author 라인 보강)
- `agents/ArchitectPLAgent.md` (검수 메타-규칙 2 항목 + deputy 5 갱신)
- `agents/QADeveloperAgent.md` (:25 1줄 보강)
- `agents/SecurityArchitectAgent.md` (§7-§8 cross-reference 규칙 섹션)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` (1줄 cross-ref)
- `templates/change-plan.md` (§8 header + §8.4 N/A 신설)
- `CLAUDE.md`, `docs/orchestrator-playbook.md`, `docs/plugin-design.md` (deputy 수 일괄)
- `.claude-plugin/plugin.json`, `CHANGELOG.md`, `README.md`, `docs/migration-guide.md` (v0.12.0)
- `docs/adr/ADR-005-plugin-self-application-na-standardization.md` (status `Accepted` 전이)
- `docs/adr/ADR-004-architectpl-securityarch-restructure.md` (#1 closure cross-ref)
