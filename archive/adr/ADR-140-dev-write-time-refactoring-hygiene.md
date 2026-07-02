---
adr_number: 140
title: 구현 lane dev roster 작성-시점 리팩터링 hygiene 의무 — 예방 층 신설
status: Accepted
category: governance
date: 2026-07-02
carrier_story: CFP-2557
supersedes: []
related_adrs:
  - ADR-137  # (Epic-close 구현-리팩터링 triage — 검출/정리 층, disjoint 대조 C3)
  - ADR-138  # (설계 리팩터링 debate — 검출/판정 제1층, 제6축 대조 C4 + §결정 1 신규-ADR carrier 선례)
  - ADR-042  # (agent model selection policy — Amd18 측정-이관 무반전 C2 + §결정 2 tier invariant 동반 점검)
  - ADR-039  # (dev 설계 금지 경계 — §결정 7 authority 무변경 invariant)
  - ADR-119  # (research-before-claims — §결정 6 검사연극 회피 2단 구조)
  - ADR-082  # (declaration-only Wave 1 — mechanical_enforcement_actions:[] known-limitation 동형)
  - ADR-063  # (marketplace atomic invariant — Phase 2 codeforge-develop MINOR bump sync)
  - ADR-013  # (dogfood-out — 본 ADR 이 Story §3 설계 SSOT 역할, change-plan 면제 정합 ADR-127 :115)
related_concepts:
  - refactoring-activity-taxonomy
is_transitional: false
---

# ADR-140 — 구현 lane dev roster 작성-시점 리팩터링 hygiene 의무 (예방 층 신설)

## 상태

Accepted (2026-07-02 KST) — CFP-2557 carrier. 구현 lane role:dev roster 의 작성-시점(write-time) 리팩터링 hygiene 의무 명문화 governance SSOT. 강화(ratchet↑) 방향 — 기존 검출/판정 3층 무변경 위에 예방 층 1개 추가, 약화 surface 0.

## 컨텍스트

품질 검출 층은 이미 3층 상시 동작한다: ① 설계-time 구조 debate (ADR-138, per-Story) ② 구현리뷰 `dup-local`/`dup-boundary` P1 검출 (매 PR — `plugins/codeforge-review/templates/review-checklists/code.md:43-44`) ③ Epic-close 구현-리팩터링 triage (ADR-137, 배치). 그러나 **예방 층이 공백**이다 — 구현 lane role:dev 에이전트 md 전체에서 재사용·중복·응집/결합·리팩터링 hygiene 의무 언급 = 유효 hit 0건 (origin/main 40519af5 grep 실측, Story CFP-2557 §1/§9.0.1 `[verified]`). 품질이 사후 검출→반려→재작업 FIX 루프에만 의존한다.

외부 배경(Story §6 인용 재사용 — 신규 외부 단정 없음): LLM 코딩 에이전트의 중복 유입은 컨텍스트-윈도 한계로 인한 rediscovery/재작성이 근인으로 보고된 known 실패 모드이며(GitClear 벤더 보고서 계열 — 방향성 신호, 벤더 caveat 하), 대응 선행사례 = "탐색을 작성-전 필수 절차로 승격"(reuse-before-write). 동시에 성급한 추상화(over-DRY)가 역효과라는 균형추(Sandi Metz "the wrong abstraction" / rule-of-three 의 본래 기능 = 성급 추출 억제)가 확립되어 있다.

사용자 원문 "디자인패턴이나 중복방지와 응집도를 높이고 결합도를 낮추는 수준의 리팩터링은 상시로 진행되어야" 의 본질 = Fowler refactoring(behavior-preserving 사후 변환)이 아니라 **prevention(작성 시점에 처음부터 잘 쓰기)** 이다 (Story §2.1 도메인 판정). "상시" = 작성 매 순간의 인라인 규율이지 백그라운드 스캔 채널이 아니다 (§2.4 polysemy 해소).

## 결정

구현 lane role:dev roster 에 **작성-시점 리팩터링 hygiene 4항 의무**(재사용 탐색 선행 / 신규 중복 유입 금지 / 응집·결합 Change Plan 지침 내 준수 / 임의 구조 재설계 금지 상한)를 명문화한다. 착지 = $DEVSET 6 agent md(주 소유층) + DeveloperPL spawn packet(전파층), 개념 = refactoring-activity-taxonomy 제3 dimension.

### 결정 1 — 예방 층 신설 + taxonomy 제3 dimension 편입 (RQ1)

- **예방 층(prevention layer) ≠ Fowler refactoring**: Fowler 정의 = observable behavior 불변 **사후 변환**(변환할 코드가 이미 존재해야 성립 — ADR-137 §결정 3 INV-BP). 예방은 코드를 처음 쓰는 순간 재사용 탐색·중복 회피·응집/결합 준수로 **입력 자체를 깨끗하게** 하는 행위 — 변환 대상 코드가 아직 없다. ∴ **INV-BP(behavior-preserving invariant) 비적용** — 예방 층은 behavior-preserving 변환이 아니므로 ADR-137 §결정 3 과 정의상 disjoint.
- **taxonomy 제3 dimension 편입**: `refactoring-activity-taxonomy.md` 의 2활동(설계 리팩터링/구현 리팩터링)은 둘 다 *검출/판정*(발동 시점 축: 설계-time vs 구현-완료-후)이다. 예방은 판정 대상이 아직 생성되지 않은 시점(작성 그 순간)에 개입 → 하위 분류가 아닌 **직교 신규 dimension** (Story §2.3 판정 — Domain·Researcher·Continuity 3자 독립 수렴). taxonomy 표에 제3 열로 편입하되 **"리팩터링 활동" 이 아닌 "예방 dimension"** 으로 명명 — 2활동 분류 자체는 무변경. 편입 방식 = CFP-2543 "결정 방식 행 신설" 동형 선례(표 dimension 확장).
- 계층 분리: **개념 SSOT = taxonomy 문서** / **실행 SSOT = $DEVSET agent md + packet** (§결정 3).

### 결정 2 — ADR 형태 = 신규 ADR-140 (RQ2)

- **ADR-137 amendment 흡수 기각**: ADR-137 §비대상(`:86-87`)이 "매 Story blanket"·"설계 리팩터링 상시 격상" 을 자기 non-goal 로 선언 — Epic-close 배치 scope 인 ADR-137 에 작성-매-순간(per-write 상시) 예방 층을 흡수하면 자기 non-goal 과 자기모순.
- **ADR-138 amendment 흡수 기각**: ADR-138 §비대상(`:110-115`)이 설계-time debate 전용 scope 를 자기 선언 — 작성-시점 층 흡수 시 동일 자기모순. **ADR-138 §결정 1 이 동일 사유(ADR-137 non-goal 자기모순 회피)로 신규 ADR 를 채택한 선례를 직접 적용**한다.
- **ADR-042 amendment 기각**: ADR-042 = agent **model selection** 정책. 예방 층은 model-tier 범주 밖 행위 규율 — amendment 로 얹으면 정책 스코프 왜곡. tier 정합은 §결정 5 동반 점검으로만 접점.
- 번호 140 = origin/main(40519af5) `git ls-tree` max = ADR-139 + ADR-RESERVATION 점유 max = 136 실측 → 가용 확인 후 점유 (CFP-702 교훈 — max+1 실측 후 점유, ADR-133 atomic claim).

### 결정 3 — 배치 = Hybrid: agent md 주 소유층 + DeveloperPL packet 전파층 (debate 결과)

ADR-138 `blanket_designrefactor` debate 4라운드(R0 Codex 발제 / R1 Claude 반박 / R1b Codex counter / R2 Claude 수렴, convergence 3-tuple 통과, verdict judge = ArchitectAgent chief) 합의 4항 + 잔존 1건 chief 판정 (Story CFP-2557 §7.5 이력 SSOT):

1. **md = 주 소유층 ($DEVSET 6 md 고정 열거)**: `plugins/codeforge-develop/agents/{Developer,DataEngineer,InfraEngineer}Agent.md` + `plugins/codeforge-develop/presets/webapp/agents/{Backend,Frontend}DeveloperAgent.md` + `plugins/codeforge-develop/presets/backend-service/agents/ServiceDeveloperAgent.md`. 각 md 기존 원칙 섹션 말미에 **동일 6줄 hygiene 블록**(도입 1줄 + anchor 4-bullet + vacuous 면제 note 1줄, `<탐색 범위>` 주석만 md별 치환) append — md별 통합 편집 (기계 치환 금지: 6 md 섹션 구조 이질 실측 / 공용 문안 파일 폐기: `regen-agents.sh` L22-32 가 `agents/*.md` 만 iterate → 렌더 붕괴 실측). QADeveloperAgent(role:qa) = 대상 외.
2. **packet = 전파층**: DeveloperPLAgent 가 role:dev spawn packet 에 hygiene anchor 4구를 **md 와 동일 문자열**로 주입 (기존 "외부 지식 인용 packet 주입" 관행 연장). **overlay 커스텀 role:dev 에는 packet 이 유일 규범 표면** (agent md 미상속 실측).
3. **잔존 판정 (packet 문안 길이) = 4-bullet compact 채택 + anchor 동일-문자열 공유 synthesis**: hygiene 4항 = 독립 의무 4개라 1~2문장 압축 시 falsifiable 커버 탈락 → 4-bullet. 이중 소유 우려(Codex)는 anchor phrase 4구를 md·packet 이 동일 문자열로 공유함으로써 해소 — **단일 문안의 두 표면**이며 drift 는 `grep -F` 동일성으로 검증 가능. packet 은 anchor + 최소 한정어만 (본문 블록 복제 금지, md 주 소유 보존).
4. **anchor phrase 4구 (고정 문자열)**: `재사용 탐색 선행` / `신규 중복 유입 금지` / `응집·결합 Change Plan 지침 내 준수` / `임의 구조 재설계 금지`.
5. **doc-only vacuous 면제 default**: src delta=0 작업은 hygiene 실행 대상 없음 — vacuous 자연 면제 (별도 스캔 채널 없음).

> **preset 전파 한계 (DR-1 서술 보정)**: preset 3 md 는 consumer 가 수동 복사해 소유하는 자산이라 본 결정의 md 변경은 기복사 consumer 에 미전파 — packet 전파층(항목 2)이 이를 커버한다. `regen-agents.sh` 렌더 붕괴 논거는 `agents/*.md` iterate 대상인 core 3 에 한정.

### 결정 4 — rule-of-three 방향 번역 (RQ3)

- 예방 층에서 rule-of-three = **"reuse-before-write 탐색 습관 + over-DRY 금지 균형"** 으로 번역한다. **정량 임계(3회)의 기계적 전진배치 금지** — 게이트화 금지.
- **검출-트리거 용법과 분리**: taxonomy 기존 정의(`:78`)의 rule-of-three = "3회 이상 반복 시 공통화 *제안 트리거*"(검출 방향, 실코드 계측 후 발동). 예방 층 용법 = "2번째 작성 시 1번째 존재를 *탐색*해 공통화 가치를 *판단*(추출 강제 아님)"(억제 방향). 같은 용어의 정반대 방향 — taxonomy 관련 용어 절에 이중 용법 note 로 분리 명시 (C1 배선).
- 근거 = Story §6 caveat verbatim 재사용: rule-of-three 는 출처상 detection-time 규칙이며 3회 임계 자체가 성급 추출 억제 장치 — 임계를 작성-시점에 강제하면 (a) 3회 미만이라 예방 미발동 또는 (b) over-DRY 역효과. 정직한 번역 = 임계가 아닌 탐색 습관의 이식.

### 결정 5 — tier-safe 문안 invariant

- hygiene 문안은 **어느 model tier 에서도 mechanical 준수 가능한 깊이로 한정**한다: 경로-scoped 2종(DataEngineer = adapters/storage·adapters/sources·schemas / InfraEngineer = deploy·config·scripts·Docker 자산)은 **담당 경로 내 탐색 + Change Plan 지침 내 준수** 한정, full-scope 4종(Developer/Backend/Frontend/Service)은 소유 경로 + 인접 읽기 범위.
- 응집/결합의 **심층 설계 판단은 설계 lane 소관** — dev 는 Change Plan §3·ADR 레이어 계약이 이미 정한 방향의 *준수*만 수행. 문안이 dev 에게 자율 cohesion 설계 판단을 요구하면 ADR-042 §결정 2 invariant(role 재정의 시그널) 위반 — **본 ADR 채택 문안은 준수·탐색 한정으로 invariant 동반 점검 통과** (Story §4.2 tier 판정). **model명은 규범문에 불기재** (tier 분기 기준 = 담당 경로 범위이지 model 이 아님 — tier 원복·변경에 문안이 종속되지 않게).

### 결정 6 — enforcement = declaration-only Wave 1

- `mechanical_enforcement_actions: []` — **known-limitation rationale**: 예방 의무는 작성-시점 행위 규율이라 PR-time 정적 lint 로 행위 자체를 계측 불가(작성 직전 falsifiable 측정 불가 — Story §6 Gap 1)하고, 리뷰 lane 확장이 Out-of-Scope 라 검사 표면 신설도 배제된다 (ADR-082 §결정 6 declaration-only Wave 1 + ADR-060 동형).
- **검사연극 회피 2단 구조 (ADR-119 §결정 6)**: ① dev 가 반환 보고에 hygiene 이행 declaration(재사용 탐색 수행 여부 1줄) — DeveloperPL 수집 (develop-output-v1 contract field 신설 아님, prose) ② 기존 구현리뷰 `dup-local`/`dup-boundary` P1 검출이 declaration 을 **사후 falsify** (검출 층 재사용 — 리뷰 체크리스트 확장 0).
- **lint 승격 조건**: anchor phrase drift 또는 hygiene 위반 재발 evidence 확보 시 후속 CFP 로 조건부 승격 (Wave 2). 신규 lint 는 본 ADR 에서 0.

### 결정 7 — authority 무변경 invariant

- hygiene 의무의 **상한(ceiling) clause = "임의 구조 재설계 금지"**: 임의 구조 재설계·새 파일·시그니처 변경 = 기존 금지 존치 (`DeveloperAgent.md:32-34` "설계 금지, 구현 집중 / 계획서 범위 밖 결정 금지"). hygiene 을 구실로 한 §3 밖 재설계(scope creep)를 차단한다.
- **에스컬레이션 경로 유지**: 구조 변경 필요 시 자의 결정 대신 DeveloperPL 경유 Architect 에스컬레이션 (현행 authority 체계 무변경 — ADR-039 dev 설계 금지 경계 정합). 재사용 탐색·중복 회피·응집/결합 준수는 전부 "Change Plan §3 를 코드로 옮기는 방식"의 규율이지 §3 자체를 바꾸는 권한이 아니다 — **dev authority 경계 무변경**.

## 결과

- **layered defense 완성**: 예방(작성-시점 유입 차단, 본 ADR) → 검출(리뷰 dup P1 + 설계 debate) → 정리(Epic-close triage) — 3층이 발동 시점에서 disjoint 하게 연쇄. Amd18 falsifiability premise("중복은 실코드가 생겨야 관측")와 무모순 — 예방은 계측하지 않는 행위 규율이다 (Story §4.3.4 논증).
- 강화 방향(ratchet↑) — 기존 층 폐지·축소 0, 신규 층 추가만. `is_transitional: false` → sunset_justification N/A (ADR-058 §결정 5 강화 방향 면제).
- **ADR-086 = lens-only**: 본 ADR 은 develop lane dev roster mandate 확장 — ADR-086 적용 lane(design lane deputy only, `:112`) 정의상 FULL self-application 밖. axis-disjoint 검증(예방 ⊥ 검출 ⊥ 정리)은 참조 lens 로만 차용 (C6).
- 비용: 신규 spawn 0 / 신규 게이트 0 / 신규 파일(정책 문서 외) 0. dev 작성 전 탐색 step 의 토큰 비용만 추가 — 사후 FIX 루프(검출→반려→재작업) 비용 절감이 상쇄 방향.

## 비대상 (out-of-scope)

- **ADR-137 / ADR-138 / ADR-042 Amd18 무변경** — 검출/판정/정리 3층 + RefactorAgent mandate 현행 유지 (본 ADR 은 cross-ref 단방향만, 상대 ADR 파일 편집 0).
- **리뷰 lane 체크리스트 무확장** — `review-checklists/code.md` diff 0 (검출 층 현행 유지).
- **백그라운드 전체 코드 스캔 채널 0** — 신규 워크플로/스크립트/잡 0.
- **QADeveloperAgent(role:qa) 미강제** — 대상 = role:dev 한정.
- **src/** production 코드 0** — wrapper-only 정책 문서 변경.
- develop-output-v1 · review-verdict contract 스키마 무변경 (prose mandate only).

## 해소 기준

N/A — permanent policy (상시 강화, sunset 대상 아님). 예방 층은 구현 lane 의 상시 행위 규율 조항 — 시한부 전환 아님. lint 승격(Wave 2)은 조건부 후속 CFP 로 강화(ratchet↑)만 가능, 약화 경로 없음.

## 관련 파일

- `plugins/codeforge-develop/agents/DeveloperAgent.md` / `DataEngineerAgent.md` / `InfraEngineerAgent.md` — $DEVSET core 3 (hygiene 블록 착지, Phase 2)
- `plugins/codeforge-develop/presets/webapp/agents/BackendDeveloperAgent.md` / `FrontendDeveloperAgent.md` + `presets/backend-service/agents/ServiceDeveloperAgent.md` — $DEVSET preset 3 (Phase 2)
- `plugins/codeforge-develop/agents/DeveloperPLAgent.md` — packet 주입 절 신설 (Phase 2)
- `plugins/codeforge-develop/.claude-plugin/plugin.json` — 0.14.0 → 0.15.0 MINOR + marketplace sync (ADR-063, Phase 2)
- `docs/domain-knowledge/domain/governance-principle/refactoring-activity-taxonomy.md` — 제3 dimension 열 + rule-of-three 이중 용법 note (Phase 1)
- **cross-ref (단방향 — 본 ADR 에서만 배선, 상대 파일 무편집)**: C1 taxonomy 제3 dimension / C2 ADR-042 Amd18 측정-이관("실코드 관측 의존") 무반전 — 예방은 계측 없는 행위 규율이라 이관 결정과 disjoint / C3 ADR-137 Epic-close triage 와 disjoint (사후 계측 ⊥ 사전 억제) / C4 ADR-138 axis-disjoint 5축 표에 대한 제6축(작성-시점) 대조 — 시점·대상·주체·착지·anchor 전부 non-overlap / C5 $DEVSET dev md 착지 (Story §7.1 삽입 지점 표) / C6 ADR-086 lens-only (FULL self-application 미적용, `:112` design lane only)
