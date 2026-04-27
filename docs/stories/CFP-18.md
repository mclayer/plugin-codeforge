---
key: CFP-18
title: TestContractArchitectAgent 신설 — §8 Test Contract Architect 단독 작성 견제
type: story
status: in-progress
phase: 요구사항
created: 2026-04-27
related_adrs: [ADR-004]
---

## §1 요구사항 원문 (사용자 input — 변경 금지)

ADR-004 후속 — Codex audit #1 (Top-1, High severity) 해소:

**문제**: Change Plan §8 Test Contract는 ArchitectAgent (chief author) 단독 author. 설계 시점 QA 견제 부재 — chief author가 자기 검증 (self-validation) 위험. 보안 설계가 §7으로 분리됐던 ADR-004 패턴과 동형.

**요구**: TestContractArchitectAgent 신설하여 §8 Test Contract author/입력 분담. v0.11.0 새 구조 (ArchitectPL + 4 deputy)의 5번째 deputy로 추가하거나, chief author 산하 sub-author로 분리.

**가치**:
1. shift-left QA — 설계 시점에 Test Contract 견제 → 보안 테스트·구현 테스트 lane FIX 회귀 비용 감소
2. v0.11.0 dogfooding — ADR-004 deputy 추가 패턴의 두 번째 적용으로 SSOT 정합성 검증
3. Codex #1 (Top-1 High) 해소

## §2 도메인 해석 (DomainAgent)

본 절은 CFP-18을 둘러싼 codeforge plugin 내부 도메인 사실(SSOT)과 책임 경계를 정리한다. **도메인 지식 공백 없음** — 4 입력 소스(`docs/domain-knowledge/**` + `docs/adr/**` + 도메인 코드(`agents/**`, `templates/change-plan.md`) + 사용자 원문 §1) 안에서 충분히 해석 가능.

### §2.1 §8 Test Contract — 본문·소유 라인 SSOT

- **본문 정의**: `templates/change-plan.md` §8 Test Contract 본문은 §8.1 단위·통합·인프라 테스트 명세, §8.2 경계·실패 조건, §8.3 성능 baseline(러너·메트릭·임계치)을 명문 의무로 규정한다 (templates/change-plan.md:99-118).
- **현재 chief author**: `agents/ArchitectAgent.md`가 §8을 chief author 단독 author로 규정 (ArchitectAgent.md:56, 76, 80). v0.11.0 재구조화(ADR-004) 이후에도 §8 author는 ArchitectAgent에 잔존.
- **ArchitectPLAgent 검수 4 항목**: §1-§9 섹션 누락 차단, §3 ADR 정합성, §6 리팩터링 선행, §10 FIX Ledger evidence pack 유효성(ArchitectPLAgent.md:58-66). §8은 "누락 차단"만 포함되며 **내용 타당성 deputy 입력 부재**.
- **QADev 위치**: `agents/QADeveloperAgent.md`에서 "§8 Test Contract 계약 소유자 = ArchitectAgent"(:25), "감사 책임 = ArchitectPLAgent"(:33), "§8은 스펙"(:53-56), "QADev 자체 추가 금지"(:71)로 규정. QADev는 **이행자만**이며 설계 시점 author 권한 없음.

### §2.2 ADR-004 — 도형 동형성

- ADR-004 라인 70-72는 본 plugin이 후속 적용해야 할 Codex 감사 항목으로 **#1·#2·#4-#6**을 명문화. **CFP-18은 ADR-004이 예약한 #1(Top-1, High severity) 후속 적용** 그 자체.
- ADR-004 패턴(§7 Security를 별도 SecurityArchitect deputy로 분리)와 본 사례(§8 Test Contract author 분리)는 **isomorphic** — author 비대칭 해소 mechanism 동일.

### §2.3 책임 경계 4 분리선 — TestContractArch ↔ QADev

향후 설계 lane이 어떤 Option(A/B)을 선택하든, 두 역할의 비충돌은 다음 4 차원 분리선이 보장한다.

| 차원 | TestContractArch | QADeveloperAgent |
|------|------------------|-------------------|
| **시점** | 설계 lane (§7 Change Plan 작성 시점) | 구현 lane (Phase 2 PR commit 시점) |
| **산출물 type** | 명세 텍스트 (§8 본문, assertion 코드 안 씀) | 테스트 함수 코드 + §8.5 Impl Manifest 매핑표 (§8 본문 안 씀) |
| **Clarification 경로** | ArchitectPL이 재스폰 (ADR-004 SecurityArch 패턴 동형) | ArchitectPL 경유 chief author 재스폰 (현행 유지) |
| **감사 책임** | ArchitectPLAgent가 §8 author input 통합 정합성 + chief author 채택/반박 정합성 검증 (현 4 감사 항목 → 5 항목 확장) | 현행 유지 (§8.5 매핑표 ↔ 실제 파일 일치) |

### §2.4 Option 의미 분석 (도메인 시각)

- **Option A (5번째 deputy)** — ADR-004와 **완전 isomorphic**. SecurityArch:§7 = TestContractArch:§8 도형 매칭. 비대칭 해소 mechanism이 이미 v0.11.0에서 검증됨.
- **Option B (chief author 산하 sub-author)** — perspective 다양성이 Option A의 deputy 모델보다 약함. 책임 라인이 chief author에 흡수되어 self-validation 위험이 부분적으로 잔존할 수 있음.
- **Option C (QADev 동등/산하)** — QADev SSOT(`role: qa`, `구현 lane 한정`)와 강한 충돌. 시점 분리 invariant(§2.3 1행)를 침범 → **dispreferred**.

### §2.5 도메인 권고

DomainAgent 단독 시각으로는 **Option A 권고**. 근거 4건:
1. ADR-004 동형성 (SecurityArch 패턴 직접 반영)
2. perspective 다양성 보존 (deputy = 독립 author input)
3. invariant 보존 (QADev 시점 분리 침범 없음)
4. FIX 회귀 비용 감소 가설 동형 (보안 lane 분리가 기대한 효과를 테스트 lane에서 재현)

단 최종 Option 결정은 RequirementsPL 통합 단계 또는 사용자 ESCALATE 후 설계 lane(ArchitectPL)이 수행한다. 본 §2는 도메인 사실·책임 경계만 확정한다.

## §3 ADR 정합성 + 신규 ADR 후보

### §3.1 기존 ADR 위반 여부 — 없음

- **ADR-001 (review-agent-unification)**: 본 변경은 리뷰 워커 통합 결정과 무관. 위반 없음.
- **ADR-002 (docsagent-inherit-footer-pattern)**: footer 패턴 결정과 무관. 위반 없음.
- **ADR-003 (three-layer-drift-responsibility)**: drift 책임 3 layer 분리와 무관. 위반 없음.
- **ADR-004 (architectpl-securityarch-restructure)**: 본 변경은 ADR-004이 명문화한 후속 항목 #1(Top-1, High severity)의 직접 적용. **위반 없이 후속 패턴 두 번째 적용**. DomainAgent + Researcher 양쪽이 도형 동형성(SecurityArch:§7 ≡ TestContractArch:§8) 확인.
- **ADR-005 (plugin-self-application-na-standardization)**: §8.6/§7.6 N/A 표기 표준과 정합 — TestContractArch 도입 후 §8.6 N/A 패턴 일관 유지 가능.

### §3.2 신규 ADR-006 후보 — 발행 의무

CFP-18은 **새 deputy(또는 sub-author) 역할을 도입하는 설계 결정**이다. CLAUDE.md ADR 생성 기준("에이전트 추가·삭제·역할 재정의")에 정확히 해당. 따라서:

- **ADR-006 발행 의무** — 설계 lane(ArchitectAgent)이 Change Plan §3에서 결정. 후보 제목: "ADR-006: TestContractArchitectAgent 도입 — §8 Test Contract author 견제".
- **결정 범위**:
  - Option A (5번째 deputy) vs Option B (chief author 산하 sub-author) 최종 선택
  - 책임 정의 ("test contract author" vs "QA perspective contributor"; Researcher Insight 3 경고 반영)
  - 모든 Story 필수 vs 조건부 스폰 정책 (§5에서 BLOCKING 이슈로 forward)
  - §7 ↔ §8 경계 겹침 시 author 결정 규칙
- **Status 흐름**: `Proposed` (요구사항 lane 시작 시 PMOAgent 발의 가능) → `Accepted` (설계 lane PASS 시 ArchitectAgent가 final 작성) → DocsAgent 경유 commit.
- **CODEOWNERS 강제**: `docs/adr/**`은 architect team 자동 review 대상 → ADR-006은 Phase 1 PR로 architect 결재 필수.

### §3.3 후속 ADR/문서 갱신 chain (조건부)

- ADR-006 채택 후 ADR-004 본문에 "후속 #1 = CFP-18 + ADR-006" 보충 라인 추가 검토 (DocsAgent 단순 cross-reference 갱신, lane 게이트 외).
- v0.11.0 release notes의 deputy 수(현 4) → 5로 갱신 (Option A 채택 시).

## §4 변경 영향 코드 경로

설계 lane Mapper/Refactor가 직접 읽을 SSOT 지도. 본 절은 **지도 수준**(파일 + 책임 한 줄)이며 line-level 분석은 설계 lane 영역.

### §4.1 신규 author/문서 (Option A 채택 시 기준 — Option B는 sub-section만 다름)

- **`agents/TestContractArchitectAgent.md`** (신규) — SecurityArchitectAgent.md 도형으로 작성. 책임: §8 Test Contract author input 제공, ArchitectPL 통합 대상, ArchitectAgent 채택/반박 후 §8 본문 확정.
- **`docs/adr/ADR-006-testcontract-architect.md`** (신규) — §3.2 후보. 설계 lane이 status `Accepted`로 작성.

### §4.2 기존 SSOT 갱신 대상

| 경로 | 현재 책임 요약 | 갱신 방향 |
|------|----------------|-----------|
| `agents/ArchitectAgent.md`:56,76,80 | §8 Test Contract chief author 단독 | "§8 본문은 chief author 권한, 단 TestContractArch input을 통합한 뒤 확정"으로 author 모델 보강 |
| `agents/ArchitectPLAgent.md`:58-66 | 4 검수 항목 (§1-§9 누락 / §3 ADR / §6 리팩터링 / §10 evidence) | 5번째 항목 추가: "§8 author input 통합 정합성 + chief author 채택/반박 정합성" |
| `agents/QADeveloperAgent.md`:25,33,53-56,71 | 계약 소유자 = ArchitectAgent / 감사 = ArchitectPL / §8 = 스펙 / 자체 추가 금지 | "계약 소유자 = ArchitectAgent (TestContractArch input 통합 후)"로 라인 보강. QADev 시점/금지 라인은 그대로 유지 (§2.3 invariant) |
| `agents/SecurityArchitectAgent.md` | §7 Security author input deputy SSOT | TestContractArch md 작성 시 doctrinal 참조 ("동일 도형") |
| `templates/change-plan.md`:99-118 | §8 Test Contract 본문 (§8.1-§8.3) | 본문 구조는 유지, header에 "author input: TestContractArch (deputy) → chief author 통합"을 1줄 명시 검토 (template 의미 변경이므로 Story 작성 의무 강제 대상) |
| `CLAUDE.md` 에이전트 다이어그램 | ArchitectPL + 4 deputy | 5 deputy로 갱신 (CodebaseMapper / Refactor / SecurityArch / TestContractArch / + 기존 1) — 정확한 deputy 명단은 ADR-004 인용 후 확정 |
| `docs/orchestrator-playbook.md` 스폰 시퀀스 / 토큰 예산 / Context Packet 표 | 4 deputy 가정 다수 | 5 deputy로 갱신, 새 spawn lane 추가 |
| `docs/adr/ADR-004-architectpl-securityarch-restructure.md` 라인 70-72 | "후속 #1·#2·#4-#6" 명문화 | "#1 = CFP-18 + ADR-006으로 해소"를 follow-up 라인으로 cross-reference (DocsAgent 단순 갱신) |

### §4.3 변경하지 않는 경로 (invariant 유지 명시)

- `agents/QADeveloperAgent.md` 시점 분리 라인(`role: qa`, "구현 lane 한정") — **변경 금지** (§2.3 invariant).
- `agents/QADeveloperAgent.md` "자체 추가 금지" 조항(:71) — **변경 금지** (시점 분리 invariant).
- `templates/change-plan.md` §8.1/§8.2/§8.3 본문 구조 — **변경 금지** (Test Contract 본문 의미는 유지, author/입력 모델만 변경).
- `templates/story-page-structure.md` §1-§11 구조 — **변경 금지**.
- 기타 `role: dev` agent md 일체 — 무관.

### §4.4 GitHub 워크플로우 / CI 영향

- `templates/github-workflows/` 6종 — 무관. 스폰 lane 추가는 Orchestrator 측 변경이므로 워크플로우 정의 변경 없음.
- `phase-gate-mergeable.yml` required status check — 라벨 추가 없음, 무관.
- `fix-ledger-sync.yml` — §10 스키마 무관, 무관.

### §4.5 영향 없음 확인 (negative scope)

- `src/**` 코드 변경 없음 — plugin meta 변경 only.
- `tests/**` 변경 없음.
- `presets/**` 변경 없음 (`role: dev` roster 무관).
- consumer overlay schema 변경 없음 (`docs/project-config-schema.md`).

## §5 통합 요구사항 명세서

3 perspective(DomainAgent / RequirementsAnalyst / Researcher) 결과를 dedup·상충 조정한 통합본. 설계 lane(ArchitectAgent + 4-or-5 deputy)의 단일 입력.

### §5.1 Acceptance Criteria (10건 + 책임 경계 invariant 4건)

설계 lane에서 Change Plan §3·§7·§8 작성 시 검증 가능해야 하는 조건.

| # | AC | Source |
|---|----|--------|
| AC-1 | §8 Test Contract 원저자가 chief author(ArchitectAgent) 단독에서 분리되어, 별도 author input(deputy 또는 sub-author)이 명시 author로 등록된다 | Analyst |
| AC-2 | `agents/ArchitectAgent.md`의 §8 chief author 단독 책임 라인(:56, 76, 80)이 "TestContractArch input 통합 후 확정"으로 갱신된다 | Analyst + DomainAgent §4.2 |
| AC-3 | `agents/QADeveloperAgent.md`의 "계약 소유자 = ArchitectAgent"(:25)가 새 author 모델을 반영해 갱신되되, 시점/`role: qa`/자체 추가 금지 라인은 변경되지 않는다 (§2.3 invariant) | Analyst + DomainAgent |
| AC-4 | §8.1 단위·통합·인프라 테스트 / §8.2 경계 조건 / §8.3 Perf Baseline 각 sub-section의 author input 책임 범위가 명문화된다 | Analyst |
| AC-5 | 선택된 Option(A 또는 B)이 `CLAUDE.md` 에이전트 다이어그램, `docs/orchestrator-playbook.md` 스폰 시퀀스, `templates/change-plan.md` §8 header, ADR-006 본문에 일관 반영된다 | Analyst |
| AC-6 | ArchitectPL이 TestContractArch deputy(또는 sub-author)를 스폰하는 시점이 SSOT에 명문 정의된다 (ADR-004 SecurityArch 동형) | Analyst |
| AC-7 | 새 author 모델이 self-validation 분리 검증 가능 — chief author가 §8 직접 작성 후 자기 review 하지 않음을 SSOT 라인으로 확인 가능 | Analyst + DomainAgent §2.5 |
| AC-8 | ADR-006 본문에 "ADR-004 패턴 두 번째 적용" rationale + DomainAgent 4 분리선(§2.3) 인용 + Researcher BDD/Shift-left/SWE-087 외부 정당성 인용 포함 | Analyst + DomainAgent + Researcher |
| AC-9 | `templates/change-plan.md` §8 header 의미 변경(author/입력 모델)이 Story 작성 의무 강제 대상임을 명시 (CLAUDE.md "강제 대상" 정합) | Analyst |
| AC-10 | Codex audit #1 closure 조건이 ADR-006에 명문화된다 (closure 정의는 §F BLOCKING-5 사용자 결정 후 확정) | Analyst |
| AC-INV-1 | TestContractArch 시점 = 설계 lane만, QADev 시점 = 구현 lane만 — 시점 분리 invariant | DomainAgent §2.3 |
| AC-INV-2 | TestContractArch 산출물 = 명세 텍스트(assertion 코드 안 씀), QADev 산출물 = 테스트 함수 코드(§8 본문 안 씀) — 산출물 분리 invariant | DomainAgent §2.3 |
| AC-INV-3 | TestContractArch clarification 경로 = ArchitectPL 재스폰 (SecurityArch 패턴 동형) | DomainAgent §2.3 |
| AC-INV-4 | ArchitectPL 검수 항목이 4 → 5로 확장 (§8 author input 통합 정합성 추가) | DomainAgent §2.3 + Analyst AC-2/AC-7 |

### §5.2 명문화 의무 (암묵 가정 8건)

설계 lane이 ADR-006/Change Plan에서 explicit 진술해야 하는 가정. 묵인 시 후속 FIX 회귀 위험.

1. ADR-004 핵심 = "보안만 특수"가 아니라 "자기 검증 위험 있는 전문 영역은 분리"라는 **일반 원칙** (Researcher Insight 1·3 정합)
2. §8 Test Contract도 §7 Security와 동급 전문성·견제 필요성
3. Test Contract 품질이 구현 lane 회귀 비용에 실질 영향 (가설 — 검증 KPI는 §10 FIX Ledger 추적)
4. QADev는 설계자 아닌 실행자 — 설계 시점 별도 QA author 필요
5. "author/입력 분담" = 명칭 변경 아닌 **실제 책임 분리**
6. chief author가 §8 직접 작성 회피해야 self-validation 위험 실질 완화
7. ADR-004 dogfooding은 구조적 정합성 검증에 의미
8. `templates/change-plan.md` §8 본문 구조 자체는 유지, **author/프로세스만 변경**

### §5.3 Edge cases — 설계 lane forward (8건)

설계 lane이 Change Plan §3·§7에서 명시 처리해야 할 경계 상황.

1. 성능 무관 Story → §8.3 N/A 표기 — TestContractArch도 §8.3에 한해 N/A 가능 (ADR-005 패턴)
2. 문서 전용 Story (CFP-18 자신 등) — TestContractArch 필수성 판정 (§F BLOCKING-3 forward)
3. §7 Security와 §8 Test Contract 경계 겹침 (예: 인증 흐름 테스트) — §F BLOCKING-4 forward
4. 작은 버그 수정 Story — deputy 5명 모두 스폰이 과대 가능, 조건부 스폰 정책 필요 (§F BLOCKING-3 정합)
5. 기존 Change Plan 호환 — 마이그레이션 정책 (§F BLOCKING 외 설계 lane 결정)
6. TestContractArch ↔ chief author 협업 프로토콜 (입력 형식·통합 conflict 해결)
7. "deputy 수 4" 가정이 코드/문서 곳곳에 hardcode 가능 — Option A 채택 시 일괄 검색 의무 (`grep -r "4 deputy"` 등)
8. Option B 채택 시 sub-author 독립성 확보 mechanism (chief author에 흡수 방지)

### §5.4 충돌·모순 5건 — 분류 결과

- **#1 Option 간 조직 구조 불일치**: 사용자 결정 필요 → §F BLOCKING-1
- **#2 self-validation 회피 원칙 약화 위험 (Option B)**: 사용자 결정 #1에 종속 — §F BLOCKING-1 흡수
- **#3 QADev 문서 충돌 ("계약 소유자 = ArchitectAgent")**: 설계 lane 해소 (AC-3로 명문 해결, 사용자 결정 외)
- **#4 author/owner/executor 명칭 혼재 위험**: 설계 lane 해소 (ADR-006 작성 시 용어 통일)
- **#5 ADR-004 패턴 정합성 약화 (§7=전담 vs §8=sub-author 비대칭)**: 사용자 결정 #1에 종속 — §F BLOCKING-1 흡수

### §5.5 사용자 확인 필요 (BLOCKING — Orchestrator ESCALATE 대상)

본 lane을 닫고 설계 lane 진입하기 전 반드시 사용자 결정이 필요한 5건. 미해소 상태로 ArchitectAgent 진입 금지.

- **BLOCKING-1**: Option A (5번째 deputy) vs Option B (sub-author) 우선안?
  - DomainAgent §2.5 + Researcher Insight 1·3 모두 **A 권고**, Analyst는 양쪽 ambiguity. 명시적 사용자 선택 필요.
- **BLOCKING-2**: TestContractArch 책임 정의 — "test contract author" vs "QA perspective contributor"?
  - Researcher Insight 3 경고: "test contract author"로 정의 시 Architect 영역 중복 가능, "QA perspective contributor"로 정의 시 견제 효과 명확.
- **BLOCKING-3**: 모든 Story 필수 스폰 vs 조건부?
  - Edge case #2/#4. 작은 버그 수정·문서 전용 Story에서도 항상 스폰? 또는 §8.6 N/A 패턴(§7.6 N/A 모방, ADR-005 정합)?
- **BLOCKING-4**: §7 ↔ §8 경계 겹침 시 author?
  - Edge case #3. 보안 테스트 항목(인증 흐름 등)은 SecurityArch가 §7에 쓰는가, TestContractArch가 §8에 쓰는가, 양쪽 cross-reference인가?
- **BLOCKING-5**: Codex audit #1 closure 정의 — 문서 정합 vs lane 동작 변경?
  - AC-10 종속. ADR-006 채택 + 문서 SSOT 갱신만으로 closure인지, 1개 이상 후속 Story가 새 lane으로 실제 동작 검증해야 closure인지 명시.

기타 5건(author/owner/reviewer 명칭 통일 / TestContractArch 필수 입력 4종 / ArchitectPL 스폰 시점 / SSOT 범위 — 런타임 코드까지 vs 문서만 / Perf Baseline N/A 판정자)은 **설계 lane 자체 결정 가능** → BLOCKING 아님.

### §5.6 상충·정합 분석 — 3 perspective dedup 결과

- **DomainAgent ↔ Analyst dedup**: AC-2(§4.2 갱신 대상)/AC-3(QADev 라인)/AC-7(self-validation)에서 두 perspective 동일 결론 → 1건으로 병합. AC-INV-1~4는 DomainAgent §2.3 단독 origin이지만 Analyst 충돌 #2/#3/#5와 정합 → invariant 카테고리로 보존.
- **DomainAgent ↔ Researcher dedup**: §2.4 Option A 권고 ↔ Researcher Insight 2 BDD collaborative + Insight 3 DevSecOps shift-left가 동일 결론 → §2.5 + §6에 양쪽 출처 cross-reference (출처 multi-source 기록).
- **Analyst ↔ Researcher dedup**: Analyst 암묵 가정 #1 ↔ Researcher Insight 1·3 (KEP/SWE-087 four-eyes 일반 원칙)이 동일 결론 → §5.2 #1에 양쪽 출처 인용.
- **상충 조정 (실제 충돌 0건)**: 3 perspective 모두 Option A 우호적이거나 양쪽 ambiguity. 강한 상충 없음. Researcher Insight 3 경고("test contract author"는 영역 중복 가능)는 Analyst 누락 #2/#3과 합쳐 BLOCKING-2로 forward — 상충이 아닌 **사용자 결정 의제**로 조정.
- **공백**: 본 lane에서 식별된 추가 공백 없음. clarification 재스폰 불요.

---

## §6 외부 지식 / 선행 사례 (ResearcherAgent)

### §6.1 핵심 인사이트 3건

**Insight 1 (HIGH severity for design)** — Kubernetes KEP 프로세스 / NASA SWE-087 / IEC 61508 functional safety는 모두 "**Reviewers/Approvers distinct from authors**" 원칙을 명문화. 본 plugin의 Architect ↔ DesignReviewPL 분리는 이 원칙을 이미 충족. 따라서 Option B(chief author 산하 sub-author)는 KEP-style overengineering 가능성 — 분리가 명목적일 뿐 실제 author 라인이 chief에 흡수될 위험.

**Insight 2 (HIGH severity for design)** — "Developers shouldn't test own code" 산업 anti-pattern + functional safety "author cannot test own work" + NASA SWE-087 "test plans는 peer review 의무" + BDD collaborative authorship 모델 → CFP-18의 **문제제기 자체에 강한 외부 정당성**. **Option A(5번째 deputy)가 BDD collaborative author 패턴과 정합 — 외부 정당성 최강**.

**Insight 3 (MEDIUM severity)** — ADR-004 패턴(보안 별도 deputy) = DevSecOps 산업 표준("historically Security ≠ QA"). Shift-left testing이 QA를 design phase 별도 author로 의무화 → ADR-004 패턴의 두 번째 적용은 정당. **단 주의**: TestContractArch 책임을 "test contract author"로 정의 시 Architect 영역 중복 가능성 → "**QA perspective contributor**"로 정의 시 견제 효과 명확. 본 경고는 §5.5 BLOCKING-2로 forward.

### §6.2 보조 사례 (참고)

- **BDD (Behavior-Driven Development)**: "design author = test author" 단일 author 모델을 명시적으로 거부. Three Amigos(PO + Dev + QA)가 시나리오 공동 작성. → Option A 정당성.
- **DbC (Design by Contract, Eiffel)**: supplier가 contract author도 됨 → 현 ArchitectAgent 패턴과 동형. self-validation 위험 자체 해소되지 않음 → 별도 reviewer 필요. → CFP-18 문제 진단의 외부 근거.
- **OpenAPI / Spec-driven**: QA를 spec review에 명시 포함 → CFP-18 author 단계 분리는 더 이른 시점 개입.
- **Rust shepherd / Python PEP 3-tier (author / shepherd / Tech Board)**: 다단계 author 분리가 LSP보다 견제 효과 큰 산업 사례.

### §6.3 외부 지식 종합 — 설계 lane 함의

- **Option A 권고 (외부 정당성)**: BDD collaborative + Shift-left QA + DevSecOps deputy = 3 산업 표준이 동일 방향 정당화.
- **Option B 위험 경고**: KEP-style overengineering — sub-author가 chief에 흡수되어 실효성 부족 가능.
- **TestContractArch 책임 정의 — "QA perspective contributor" 권고**: Researcher Insight 3 경고 직접 반영. Architect 영역 중복 회피.
- **closure KPI 후보**: 구현 테스트 lane FIX 회귀 비용 감소 (§5.2 가정 #3 검증). 설계 lane이 §10 FIX Ledger 모니터링으로 사후 검증 (lane 동작 기준 closure — §5.5 BLOCKING-5 입력).

### §6.4 출처 신뢰도

- HIGH (외부 표준·산업 합의): KEP / NASA SWE-087 / IEC 61508 / BDD / Shift-left
- MEDIUM (산업 관행): DevSecOps deputy / Rust shepherd / PEP 3-tier
- LOW (참고): DbC, OpenAPI spec review

본 lane 결정은 HIGH 신뢰도 출처에 한해 직접 인용, MEDIUM 이하는 보조 근거로만 사용.

## §7 Change Plan 요약 (설계 lane — 작성 완료)

→ docs/change-plans/cfp-18-test-contract-architect.md

### §1 목적
ADR-004 후속 — Codex audit #1 (Top-1, High) 해소. §8 Test Contract author input을 chief author 단독에서 deputy(TestContractArchitectAgent)로 분리. SecurityArch:§7 isomorphic 패턴.

### §3 도입할 설계 (핵심 결정 4건)
1. TestContractArchitectAgent 신설 — ArchitectPL 직속 5번째 deputy (사용자 BLOCKING-1: Option A)
2. §8 author = ArchitectAgent (chief author) 유지, TestContractArch는 author input contributor (BLOCKING-2)
3. ArchitectPL 검수 4 항목 → 메타-규칙 2 항목 압축 (Refactor STRONG ROI #1 채택)
4. §7 ↔ §8 cross-reference 규칙 명문화 (BLOCKING-4: §7 단독 + §8 cross-ref만)

### §4 API 계약
TestContractArch ↔ ArchitectPL/Architect/QADev/SecurityArch 4 인터페이스 명시 — 시점·산출물 type·cross-ref 의무.

### §7 보안 설계 (부분 N/A)
§7.6 부분 N/A — `plugin-meta-na` (ADR-005). T1 위협 (신규 agent permission model) → §7.7 min-privilege spec으로 완화 (WebSearch/WebFetch 제거, SecurityArch 대비 강화). §7.8 ADR-004 패턴 안정성 OK.

### §9 분기
Phase 1 PR (현재 — 요구사항 + 설계 + 설계리뷰) → 머지 → Phase 2 PR (구현 = 19 SSOT 갱신 + TestContractArch.md 신규 + ADR-005/004 cross-ref).

## §8 구현 결과 (Phase 2)

→ Phase 2 PR commit history

### §8.5 Impl Manifest

→ Phase 2 PR §8.5 매핑표 commit 후 자동 sub-issue 생성

## §9 리뷰·테스트 결과 (Phase 2)

(설계 리뷰 / 구현 리뷰 / 구현 테스트 / 보안 테스트 결과)

## §10 FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음**.

## §11 회고 (PMOAgent)

(머지 후 PMOAgent 스폰 시 작성)
