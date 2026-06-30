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
is_transitional: false
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
- DevSecOps SubAgent 패턴 — Security ≠ QA, QA를 design phase 별도 author로 의무화

## 결정

### 결정 1 — TestContractArchitectAgent 신설 (5번째 SubAgent, Option A)

ArchitectPLAgent 직속 5번째 SubAgent로 추가. CodebaseMapperAgent / RefactorAgent / SecurityArchitectAgent와 동급. SecurityArchitectAgent.md verbatim 도형으로 작성하되 도메인 substitution (§7→§8, 공격자→QA perspective contributor).

**사용자 BLOCKING-1 결정 verbatim**: "Option A: 5번째 SubAgent (ArchitectPL 직속, Mapper/Refactor/SecurityArch와 동급)"

### 결정 2 — chief author 본문 author 권한 유지

§8 본문 author = ArchitectAgent (chief author) 유지. TestContractArch는 author input contributor (SubAgent 산출물 → chief author 통합). SecurityArchitectAgent:§7 패턴과 정확 동형.

**사용자 BLOCKING-2 결정 verbatim**: "QA perspective contributor: SubAgent는 §8 author input 제공, §8 본문 author는 chief author 유지 (SecurityArch:§7 패턴 정확 동형)"

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

1. **ArchitectPL 검수 4 항목 → 메타-규칙 2 항목 압축** (Refactor STRONG ROI #1) — SubAgent N+1 추가 시 enumerate 폭증 회피
2. **TestContractArch ↔ QADev mutual reference** (Refactor STRONG ROI #3) — 시점/산출물 분리 invariant 명문 cross-ref
3. **min-privilege permissions** (SecurityArch §7.7) — WebSearch/WebFetch 제거 (TestContractArch 외부 lookup 불필요)
4. **ADR-005 status 전이** — `Proposed` → `Accepted` (CFP-17/18 두 번 dogfooding 검증 완료, **결정 1·2·3에 한정**: N/A 표기 형식 / 면제 분류 / N/A inheritance 차단). **결정 4 (invariant-check workflow Step 신설)는 본 Story 범위 외 — 별도 follow-up Story (CFP-19+) 발의 의무**. 본 status 전이가 결정 4 self-condition 충족을 함의하지 않으며, 결정 4 implementation은 별도 lane으로 추적.
5. **`templates/change-plan.md` §8.4 N/A 권한 신설** — `plugin-meta-na` / `runtime-inert` 분류 (ADR-005 정합)

## 결과

### 긍정적

- shift-left QA: §8 Test Contract가 설계 단계에서 별도 author input으로 가시화 → 구현/보안 테스트 lane FIX 회귀 비용 감소 (full closure KPI)
- self-validation 분리: chief author가 §8 직접 author 아님 — TestContractArch input 통합 후 확정
- ADR-004 패턴 두 번째 적용 — 구조적 정합성 검증 (dogfooding success metric)
- ArchitectPL 검수 메타-규칙화 → SubAgent N+1 추가 시 SSOT 갱신 부담 일정 (drift 방지 ROI)
- BDD/Shift-left/DevSecOps 외부 정당성 3중 (Researcher Insight 1·2·3)

### 부정적

- 설계 lane 토큰 비용 추가 증가: 5-agent (ArchitectPL + Architect + Mapper + Refactor + SecurityArch) → 6-agent (+TestContractArch). 1 Story당 5-10k 토큰 추가 추정
- ArchitectPL 메타-규칙 항목으로 압축됐지만 SubAgent 5인 산출물 통합 부담 증가
- self-paradox: 본 Story 자체는 TestContractArch 부재 상태에서 §8 N/A 처리 (Story §1 verbatim 인지)

### Trade-off

부정 영향(토큰 비용)은 ADR-004 결정과 동일 trade-off — shift-left QA 가치가 비용 상회. full closure KPI(FIX 회귀 비용 감소) 1-2 Story 누적 후 PMOAgent 회고에서 측정.

## 해소 기준

N/A — permanent policy



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
- `agents/ArchitectPLAgent.md` (검수 메타-규칙 2 항목 + SubAgent 5 갱신)
- `agents/QADeveloperAgent.md` (:25 1줄 보강)
- `agents/SecurityArchitectAgent.md` (§7-§8 cross-reference 규칙 섹션)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` (1줄 cross-ref)
- `templates/change-plan.md` (§8 header + §8.4 N/A 신설)
- `CLAUDE.md`, `docs/orchestrator-playbook.md`, `docs/plugin-design.md` (SubAgent 수 일괄)
- `.claude-plugin/plugin.json`, `CHANGELOG.md`, `README.md`, `docs/migration-guide.md` (v0.12.0)
- `docs/adr/ADR-005-plugin-self-application-na-standardization.md` (status `Accepted` 전이)
- `docs/adr/ADR-004-architectpl-securityarch-restructure.md` (#1 closure cross-ref)

## Amendment 1 (CFP-2504) — 외부 venue/시계열 데이터 형상 재현 fidelity 의무

> **carrier 근거 (1줄)**: mctrader MCT-58 — 합성 테스트(+1 seq 균일)로만 검증해 829 green·전 lane PASS인데, 실 Bithumb 의 μs-timestamp-as-seq snapshot-only 스트림(스냅샷마다 ~78ms 점프)을 재현 안 해 라이브 배포 직후 GAP-flood 발생. **합성 형상으로 replay 해도 통과**한 채널이 production 형상에서 깨졌다.

### A1-0 — 결정 요약

§8 Test Contract 에 **외부 venue/시계열 데이터 형상 재현 fidelity 의무**를 신설한다. TestContractArchitectAgent 가 §8 author input 작성 시 이 의무를 인지·요구하고, 미충족 시 설계리뷰가 P0/이의로 차단한다. **CONDITIONAL** — 외부 venue/exchange/stream/time-window 시계열 데이터에 의존하는 Story 한정 발동. 의존 없는 Story(메모리-only / 내부 결정론)는 N/A.

이는 ADR-006 §결정 1-3 의 "shift-left QA — §8 author input contributor" mechanism 의 **CONDITIONAL 확장**이다. 신규 ADR 이 아닌 Amendment 인 근거 = 아래 A1-5.

### A1-1 — Trigger (CONDITIONAL 발동 조건)

다음 중 하나라도 해당하면 본 의무 active:

- Story 가 외부 venue / exchange / stream 의 실제 데이터 형상에 의존 (예: 거래소 L2/tick orderbook, WebSocket stream, snapshot 프로토콜)
- Story 가 외부 time-window 시계열 데이터에 의존 (예: candle/bar 시계열, sequence-number 기반 ordering, timestamp 기반 dedup/replay)
- 코드가 **shape-sensitive** — seq 의 의미론(증가 규칙·재사용·μs-as-seq 등), timestamp granularity/다중성, GAP/rate-spike/disorder 패턴에 따라 동작이 갈림

모호 시 default = active (TestContractArch 의 명시적 N/A 판정 의무 — A1-3).

### A1-2 — 의무 (active 시)

§8 Test Contract 에 해당 venue 의 **실제 데이터 형상을 재현하는** 테스트 1+ 를 포함한다. 다음 두 경로 중 하나로 충족한다:

- **(a) captured-golden** — 실 venue tap/녹화(wiretap 또는 실 stream capture) 산출물을 fixture 로 사용. 형상이 자동으로 production-faithful.
- **(b) 실형상-justified fixture** — 합성 fixture 이되, 재현하는 실형상 특성을 **명시·정당화**한다: seq 의미론(증가 규칙·μs-as-seq 등 venue 별 실제 규약) + timestamp granularity·다중성(동일 timestamp 다중 메시지 등) + GAP/rate-spike/disorder 패턴(스냅샷 점프·burst·out-of-order). 각 특성은 실 venue 사실 근거와 함께 justify 하되, **seq 의미론·timestamp 규약·GAP 패턴 단정은 1차 출처(거래소 공식 spec/문서 또는 실 capture·wiretap) 인용 필수 — "정상 거래소 관행"·"일반적으로 +1 단조증가" 류 2차 추정은 근거로 불인정**. (근거: MCT-58 은 unknown-unknown — 팀이 Bithumb 의 μs-as-seq 규약을 *몰랐고* +1 로 오인. 추정 justify 를 허용하면 그 오인이 그대로 통과한다. 1차 출처 강제가 오인 통과 경로를 닫는다.)

**합성-only(균일 +1 seq · 고정 interval)는 shape-sensitive 코드에 불충분**임을 명시한다. discriminating fixture(CFP-1334)·mutation-RED 는 "테스트가 변화를 감지하는가"를 강제하지만 "**올바른 형상인가**"는 보장하지 못한다 — 본 의무는 그 공백(형상 정확성)을 메운다.

### A1-3 — N/A path

외부 venue/시계열 데이터 의존 없음(메모리-only 결정론 / 내부 자료구조만 / 외부 stream 미접촉) → §8 에 N/A + 사유 1줄 명시(ADR-005 정합). TestContractArch 가 §8 author input 작성 시 N/A 판정 + 사유 제공. N/A 사유 누락 시 설계리뷰 P0 차단(§8.4 N/A 패턴 동형).

본 A1-3 의 N/A(외부 데이터 **미접촉**)와 A1-6 의 N/A(외부 데이터를 **접촉하나 형상에 동작이 갈리지 않음** = shape-insensitive)는 서로 다른 분류다 — A1-3 은 venue 자체에 닿지 않는 Story, A1-6 은 닿되 비민감 변환만 하는 Story.

### A1-4 — 소유 + 기존 mandate 와의 disjoint

- **소유**: TestContractArchitectAgent 가 §8 author input 작성 시 본 의무를 인지·요구. ArchitectAgent(chief author)가 §8 본문 통합. 미충족 시 DesignReviewPLAgent(설계리뷰)가 P0/이의.
- **loop closure (설계→구현 gap 차단)**: 설계리뷰가 §8 선언을 강제하고, **구현리뷰(code-review)가 구현 fixture 의 형상 실재현을 검증**한다 — §8 에 형상 재현을 선언해도 구현 fixture 가 균일 +1 seq·고정 interval 합성이면 code-review 가 §8 contract 미이행으로 잡는다.
- **기존 "WS stream latency 가정 검토"(TestContractArch §8.5 라인 — `push_interval` empirical source 확인)와 disjoint**: 그건 *수치 근거*(push_interval 값이 실증됐는가) 축이고, 본 의무는 *형상 재현*(seq/timestamp/GAP 패턴이 실 venue 모양인가) 축이다. 한쪽이 다른 쪽을 함의하지 않는다 — push_interval 수치가 실증돼도 합성 +1 seq 형상이면 본 의무 미충족.
- **§8.5.3 idempotency replay 와 disjoint**: §8.5.3 의 replay 는 재실행 결과 동일성(idempotency) 검증이고, 본 의무는 replay 입력의 *형상 정확성*이다. 합성 형상으로 replay 해도 §8.5.3 은 통과 — 본 의무가 그 입력 형상을 production-faithful 로 강제.

### A1-5 — Amendment vs 신규 ADR 판단

**Amendment 채택**. 근거: 본 의무는 ADR-006 이 신설한 "§8 Test Contract author input contributor — shift-left QA" mechanism 의 *범위 확장*이지 새 mechanism 이 아니다 — TestContractArch 가 §8 author input 작성 시 인지하는 mandate 항목 하나를 추가하고, 설계리뷰 P0 차단 channel(§8.4 N/A 동형)을 재사용한다. 소유 agent·통합 경로·차단 channel 이 모두 ADR-006 의 기존 구조이므로, 새 ADR 의 별도 컨텍스트/결정/결과 블록은 중복이다. ADR-014 가 §7.4/§11.6 를 deputy mandate 에 Amendment 로 끼운 선례, ADR-124 Amendment 1 이 "외부 기술선택 좁은 예외"를 기존 리뷰 mechanism 에 확장으로 끼운 선례와 동형이다.

### A1-6 — "real-venue-shape" 정의의 균형 (과잉규정 회피)

actionable 하면서도 burden 과잉이 아니도록 다음으로 균형을 잡는다:

- **너무 빡빡(captured-golden 강제) 회피**: 실 tap 녹화를 모든 Story 에 강제하면 외부 venue 접근 비용·secret·flakiness 부담이 과도하다. 경로 (b) 실형상-justified fixture 를 동등 1급으로 허용 — 핵심은 "형상 특성의 명시·정당화"이지 "실 데이터 물리 보유"가 아니다.
- **너무 느슨(서술만) 회피**: 단순 "형상 고려함" 1줄은 무력하다. (b) 는 seq 의미론 + timestamp granularity/다중성 + GAP/rate-spike/disorder 3 축의 *명시 + 실 venue 근거 justify* 를 요구한다 — TestContractArch 가 빈칸을 채우게 강제하는 forcing function.
- **scope 한정**: shape-sensitive(seq/timestamp/GAP 의존) 코드에만. 외부 데이터를 단순 통과·집계만 하고 형상에 동작이 갈리지 않으면 N/A(외부 데이터를 접촉하나 비민감 — A1-3 의 미접촉 N/A 와 구별되는 별도 분류). 외연 무한확장(모든 외부 호출에 형상 fixture 강제) 차단 — A1-1 trigger 의 shape-sensitivity 조건이 negative-list 역할.
  - **N/A 적격 (shape-insensitive)** = `sum`/`count`/`mean`/`map` 류 **형상-무관 변환** — 입력 순서·seq 의미론·timestamp 다중성이 결과에 영향 없음.
  - **shape-sensitive (N/A 불가)** = `first`/`last`/ordering 의존, `sorted`/순서 가정, seq 를 dedup/ordering 키로 사용, time-window 경계 조건. "통과·집계"와 "형상 의존"은 orthogonal 이다 — `first`/`last` 는 외부 데이터를 *통과*시키지만 ordering 에 의존하므로 shape-sensitive(N/A 불가).

### A1-7 — consumer-applicability

- **wrapper self = N/A**: codeforge wrapper 자신은 외부 venue/거래소 stream 을 touch 하지 않는다(plugin-meta / 내부 거버넌스 문서·agent md) → 본 의무 항상 N/A(ADR-005 `plugin-meta-na`).
- **venue-touching consumer(mctrader 류) = active**: 거래소 L2/tick·WS stream·snapshot 프로토콜·시계열 candle 에 의존하는 consumer Story 에서 발동. consumer overlay 는 보수 방향(추가 venue 별 형상 체크리스트 확장)만 — 의무 축소 불가(overlay 확장-only 정합).

### A1-8 — Phase 2 deferred (기계적 lint)

synthetic-only 자동탐지(예: fixture 가 균일 +1 seq · 고정 interval 인지 정적 판별)는 **본질적으로 fuzzy** — "shape-sensitive 코드인가" 판정과 "fixture 가 실형상인가" 판정 모두 의미 추론을 요구해 단순 정적 grep 으로 안정 검출이 어렵다. 따라서 본 Amendment 는 **Phase 1 선언적 의무**(TestContractArch mandate + 설계리뷰 체크리스트 항목)만 정착하고, 기계적 lint 는 **별도 follow-up(deferred-followup)**으로 미룬다.

- evidence-checks-registry 에 placeholder entry `venue-shape-fidelity-presence`(status: deferred-followup, detect_command/workflow omit — `deputy-spawn-count-empirical-grounding`(CFP-1086) omit 패턴 답습) 추가.
- Phase 2 carrier 가 실 lint 알고리즘(예: §8 에 "형상 재현/captured-golden/실형상-justified" 또는 "N/A — venue 미접촉" anchor presence 검출) 설계 후 warning 전환.

### A1-9 — 해소 기준

N/A — permanent policy (외부 venue/시계열 의존 Story 가 존재하는 한 영구 적용). Phase 2 lint wire 는 별 carrier 추적.

### A1-10 — 관련 파일 (Amendment 1)

- `plugins/codeforge-design/agents/TestContractArchitectAgent.md` (§8.5 인접 신항 — production-venue shape fidelity)
- `plugins/codeforge-review/templates/review-checklists/design.md` (Test Contract 타당성 섹션 1항 추가 — §8 선언 강제)
- `plugins/codeforge-review/templates/review-checklists/code.md` (테스트 코드 품질 1항 추가 — 구현 fixture 형상 실재현 검증, loop closure)
- `docs/evidence-checks-registry.yaml` (`venue-shape-fidelity-presence` deferred-followup placeholder entry)
- `skills/deputy-mandate/SKILL.md` (§8 row cross-ref 1줄 — 선택)
