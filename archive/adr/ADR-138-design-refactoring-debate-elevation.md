---
adr_number: 138
title: 설계 리팩터링 결정 방식 Codex↔Claude debate 격상
status: Accepted
category: governance
date: 2026-07-01
carrier_story: CFP-2543
supersedes: []
related_adrs:
  - ADR-137  # (구현 리팩터링 triage — axis-disjoint 대조, non-goal carrier)
  - ADR-059  # (debate 엔진 SSOT — Amendment 4 enum sibling)
  - ADR-039  # (§결정18/19 dispatch 재귀가드 재인용)
  - ADR-042
  - ADR-119
  - ADR-008
related_concepts:
  - refactoring-activity-taxonomy
is_transitional: false
---

# ADR-138 — 설계 리팩터링 결정 방식 Codex↔Claude debate 격상

## 상태
Accepted (2026-07-01) — CFP-2543 carrier. 설계 리팩터링(구조 3축 + repo-분해 escalation) 결정 방식의 Codex↔Claude adversarial debate 격상 governance SSOT.

## 컨텍스트

설계 lane `RefactorAgent`(origin `plugins/codeforge-design/agents/RefactorAgent.md`, model:sonnet)는 구조 리팩터링 3축 (a)decoupling · (b)pattern · (c)interface-separation + repo-분해 escalation 을 advocacy 로 제출한다. AS-IS 에서 이 advocacy 의 **반박·수용 판정(결정 방식)** 은 RefactorAgent.md L142-148 `## 대립 해소 프로토콜 (병렬 모델, 3-way)` verbatim **"반박·수용 판정은 ArchitectAgent (chief author) 통합 단계에서 수행"** — Claude 단독 inline 통합 판정이다.

대칭 활동인 **구현 리팩터링**(중복·재사용 축)은 CFP-2533/ADR-137 로 이미 **Epic-close Codex↔Claude execute-and-falsify triage(debate)** 로 격상됐다. 두 리팩터링 활동의 결정 방식이 비대칭이다:
- 구현 리팩터링(실코드 중복 축) = Codex↔Claude debate (ADR-137, LIVE)
- 설계 리팩터링(구조 축) = Claude 단독 inline 통합 (AS-IS)

origin `docs/domain-knowledge/domain/governance-principle/refactoring-activity-taxonomy.md` 표는 "발화 주체"/"메커니즘" 행은 있으나 **"결정 방식(decision mechanism)" 행이 미기재 = GAP** — 이 비대칭을 codify 못 한 채 방치.

결정적으로 **ADR-137 §비대상(origin line ~86)이 "설계 리팩터링 Codex 상시 격상 (RefactorAgent 설계-lane inline 존치)" 를 명시적 non-goal 로 선언**했다. 본 ADR = 그 deferred non-goal 을 여는 carrier.

## 결정

설계 리팩터링(구조 3축 + repo-분해 escalation)의 결정 방식을 **Claude 단독 inline advocacy → ArchitectAgent chief 통합 → Codex(발제/proponent)↔Claude(반대/opponent) min-3/max-5 debate + 3분기 verdict(now/defer/drop)** 로 격상한다. 설계-time per-Story, Orchestrator top-level inline dispatch. 구현 리팩터링(ADR-137) 무변경.

### 결정 1 (H1) — ADR 형태 = 신규 ADR-138 (본 ADR)
- 본 Story = 설계-time 구조 리팩터링 debate. ADR-137 = Epic-close 구현 중복 triage. 시점·대상·verdict judge·착지 모두 axis-disjoint(§axis-disjoint 논증 참조).
- ADR-137 §비대상이 "설계 리팩터링 Codex 상시 격상" 을 명시적 non-goal 선언 → ADR-137 amendment 로 흡수 시 **ADR-137 자기 non-goal 과 자기모순** → 신규 ADR-138 carrier.
- ADR-059 amendment 도 아님(ADR-059 = debate 엔진 SSOT). 엔진 enum 추가는 ADR-059 Amendment 4(sibling), **정책 신설(격상 결정)은 본 ADR-138 이 carrier**.
- max ADR = 137(origin/main 실측) → 138 free.

### 결정 2 (H2) — dispatch mode = 신규 enum `blanket_designrefactor` + role_assignment + debate-protocol v1.3→v1.4 MINOR
- 기존 enum 재사용 불가 근거:
  - `blanket_cross_module_designlane` = **대칭**(role_assignment 없음) + cross-module Story 전체(Change Plan §3/ADR/§7/§11) 대상 → codex-proponent 방향 배정 부적합.
  - `blanket_refactor` = **refactor lane(구현-리팩터링)** 전용 + Epic-close cadence → 설계-lane per-Story 구조 축과 disjoint.
- **신규 enum `blanket_designrefactor`**: role_assignment={codex:proponent, claude:opponent}(기존 optional 필드 재사용, 신규 필드 0), trigger = 설계 lane RefactorAgent 구조 리팩터 활동(per-Story 무조건 발동, cross_module_signal block 불요 — blanket_refactor 선례 동형), divergence_type `structural` 재사용(per-lane keying 3-way 변별: DesignLane blanket=설계 산출물 structural / blanket_refactor=실코드 중복 structural / **blanket_designrefactor=설계 리팩터 구조 축 structural**).
- **bump = MINOR (v1.3→v1.4)**: additive enum(기존 enum 값·필드 의미 변경 0) = strengthening(ADR-008 §결정2). blanket_refactor v1.2→v1.3 선례 정합.
  - **ADR-137 §결정6 대비 차이 명시**: ADR-137 은 MINOR bump 불요였음 — 당시 blanket_refactor enum 이 **이미 존재**(CFP-2534 v1.3 에서 신설 완료)했기 때문. 본 ADR 은 **신규 enum** blanket_designrefactor 추가라 MINOR bump 필요. 이 차이가 두 ADR 의 bump 정책 divergence 를 설명.
- ADR-059 Amendment 4 동반(sibling — version_history v1.4 row).

### 결정 3 (H3) — verdict judge = ArchitectAgent chief + dispatch 분리 재귀가드
- **dispatch = Orchestrator top-level inline**: ADR-039 §결정18(merge-time Codex adversarial dispatch = Orchestrator top-level inline 전용 whitelist 6번째 entry, subagent 는 재귀가드 `subagent_recursion_blocked` silent skip) + §결정19(lead 위임 per-Story dispatch topology). RefactorAgent/ArchitectPL self-spawn 불가.
- **verdict judge 주체 = ArchitectAgent chief author**: Change Plan §3 착지 author 이자 multi-source synthesizer. ArchitectPL 아님(ArchitectPL = supervisor 검수). RefactorAgent = **구조 advocacy input provider (verdict 주체 아님)** — 요구사항리뷰 P2 #2 정합.
- **producer/consumer 분리 동형(vs ADR-137)**: PMOAgent(ADR-137)·ArchitectAgent(ADR-138) 모두 self-spawn 불가 → producer(verdict judge, transcript 수신·판정) / consumer(Orchestrator inline dispatch) 분리 동형. ADR-137 은 Epic-close 산출물 owner=PMOAgent 라 PMOAgent 가 judge, 본 ADR 은 설계-time 산출물 owner=ArchitectAgent chief(Change Plan §3) 라 chief 가 judge. **주체만 교체(PMOAgent→ArchitectAgent), 배선 논리 동일.**

### 결정 4 (H4) — 3분기 verdict 착지 + anchor scope per-Story
- 설계-time = 실코드 없음 → anchor = 구조 리팩터 지점(설계 스케치 macro/module boundary anchor), `<설계 요소>::<구조 축>` 형식 (실코드 `<file>:<line>` 아님 — 설계-time 은 line 없음).
- 3분기 verdict 착지:
  - **now** → 이번 Story Change Plan §3 반영(설계 결정 착지).
  - **defer** → 후속 Story(deferred-item-lifecycle narrative-recorded, 회수 강제).
  - **drop** → ADR-119 §결정9 3문 게이트 기각("관찰됨·미조치" 1줄).
- **anchor scope = per-Story**(Story §9 debate transcript 내 anchor-recurrence ≥2 escalation, debate-protocol §3.4 원본 scope 그대로). **cross-Epic drop-ledger 불요** — 그건 ADR-137 Epic-close 실코드 중복 전용(content-hash cross-Epic 영속). 설계-time per-Story 는 매 Story 신규 설계라 cross-Epic 재발 개념 부적합. **이 disjoint 를 명시 — ADR-137 cross-Epic 배선과 혼동 금지.**

## axis-disjoint 논증 (vs ADR-137 — 자기모순 회피 근거)

> **표 구성 = 5 disjoint 축 + 2 정책 divergence 행** (검수 카운트 명료화): 상단 5행(시점/대상/verdict-judge/착지/anchor)이 **disjoint 축**(둘이 겹치지 않는 orthogonal 차원). 하단 2행(dispatch-enum/bump)은 disjoint 축이 **아니라** 두 ADR 의 **정책 divergence 설명 행**(같은 debate 엔진을 쓰되 enum·bump 정책이 갈리는 이유 기록). 마지막 열: 상단 5행 = ✅(disjoint), 하단 2행 = "divergence 설명".

| 축 / 행 | ADR-137 (구현 리팩터링 triage) | ADR-138 (설계 리팩터링 debate) | 구분 |
|---|---|---|---|
| **① 시점** (disjoint 축) | Epic-close (1회 batch) | 설계-time per-Story | ✅ disjoint |
| **② 대상** (disjoint 축) | 실코드 중복·재사용(머지된 코드) | 설계 구조 축(a/b/c + repo-분해 escalation), 설계 스케치 | ✅ disjoint |
| **③ verdict judge** (disjoint 축) | PMOAgent(Epic 산출물 owner) | ArchitectAgent chief(Change Plan §3 owner) | ✅ disjoint |
| **④ 착지** (disjoint 축) | EPIC-RESULTS §deferred / cross-Epic drop-ledger | Change Plan §3 / 후속 Story / "관찰됨·미조치" 1줄 | ✅ disjoint |
| **⑤ anchor** (disjoint 축) | `<file>:<line>` content-hash, cross-Epic 영속 | `<설계 요소>::<구조 축>`, per-Story scope | ✅ disjoint |
| dispatch enum (divergence 행) | blanket_refactor (기존) | blanket_designrefactor (신규) | 정책 divergence 설명 |
| bump (divergence 행) | MINOR 불요(enum 기존) | MINOR 필요(enum 신규) | 정책 divergence 설명 |

**5 disjoint 축(①-⑤) 전부 통과** → ADR-137 non-goal 과 자기모순 회피, 신규 ADR-138 정당. dispatch-enum/bump 2 divergence 행은 disjoint 카운트에 미포함(정책 갈림 기록만).

## 결과 (P2 #1 정직 framing 반영)

### 긍정
- **거버넌스 대칭성**: 구현 리팩터링(debate) ↔ 설계 리팩터링(단독 inline) 비대칭 GAP 해소. taxonomy 결정 방식 행 대칭화.
- **편향 축소 방향성**: 단일 모델 단독 판정 → 2-model adversarial(Codex proponent ↔ Claude opponent). 방향상 우월(ADR-059 §결과 편향 축소 근거 상속).
- **비용 cap 상속**: max 5 라운드 token cap(~50K) + AskUserQuestion escalation(ADR-059 상속, 신규 cap 도입 0).

### 외부근거 정직 framing (P2 #1 — origin ADR-059:276 반대 caveat 2건)
본 ADR 의 debate 격상은 origin ADR-059 §결과(L276 region)의 외부근거를 상속한다. 그 인용원이 자기 안에 담은 **반대 caveat 2건**을 정직하게 반영한다 (신규 외부조사 불요 — caveat 는 내부 인용원에 이미 상주):

- **(a) anchor 유형 불일치**: 코드 도메인 최근접 prior-art anchor = **PD³ (arXiv 2505.17492)** = origin ADR-059:276 verbatim "project/code duplication 에 adapted multi-agent debate 적용 — **단 협력형**(collaborative/fair-competition)". 본 격상은 **adversarial** → anchor 유형 불일치. 최근접 prior-art 조차 협력형이라 adversarial 전이는 추가 확장.
- **(b) 코드 도메인 debate 저일관성**: origin ADR-059:276 verbatim "코드 도메인 debate 는 일관성이 낮다는 보고도 있으며(**MAD, arXiv 2503.12029**)". 일반 추론·번역·산술 편향 축소 실증(Du et al. 2023 = arXiv 2305.14325 / Liang et al. 2023 = arXiv 2305.19118)과 코드 도메인 일관성 저하 보고가 상충.

**정직 framing 결론**: 설계 리팩터링(구조 축)으로의 전이는 origin ADR-059 §6.1 프레임(구현 리팩터링 = "약한 확장 가정")보다 **더 약하다**:
1. 구현 리팩터링(ADR-137)조차 "약한 확장 가정"(실증 미확보). 그 anchor(PD³)는 코드 중복 대상.
2. 설계 리팩터링(구조 축)은 코드 중복이 아닌 설계 스케치 구조 판단 대상 → PD³ anchor 에서 한 단계 더 멀다(코드→설계 추상화 gap).
3. anchor 유형(협력형)·도메인 일관성(저하 보고) 2 caveat 모두 격상 방향에 불리.

→ **"약한 확장 가정" 을 "한 단계 더 약한 확장 가정" 으로 정직 하향 표기**하되, ratchet↑ 방향(단독→adversarial) + 거버넌스 대칭성 + 비용 cap 상속으로 채택. refactoring 특정·설계 구조 특정 유효성은 별도 실증 미확보 명시.

### 부정 / 비용
- 발동 빈도↑(per-Story, Epic-close batch 대비). 완화 = 설계 lane 진입 자체가 per-Story 이므로 추가 비용 = 설계 lane 당 1회 debate(bounded) + token cap 상속.
- 외부 유효성 미확보(위 정직 framing). 완화 = ratchet↑ 방향이라 회귀 위험 없음, 후속 실증 시 강화 가능.

## 비대상 (out-of-scope)
- **구현 리팩터링(중복 축 Epic-close batch, ADR-137) 무변경** — blanket_refactor enum·verdict judge(PMOAgent)·cross-Epic drop-ledger 무변경.
- **RefactorAgent (d)측정축 이관(origin RefactorAgent.md L48 out-of-mandate 절, ADR-042 Amendment 18/CFP-2539) 무변경** — 실코드 관측 의존이라 설계-time falsifiable 아님.
- **debate 엔진(라운드 정책·termination·anti-sycophancy·reasoning carryover·convergence_quality_invariant) 무변경** — 재사용만.
- **ADR-039 §결정18/19 무변경** — 재인용만(기존 조항이 blanket_designrefactor dispatch 커버).
- src/** 코드 0. schema 0. trust boundary 0.

## 거절된 대안 (Rejected alternatives)

본문 분산 논거를 집약 (H1-H2 결정 근거의 대칭 negative):

- **(a) ADR-137 amendment 흡수** — 거절. ADR-137 §비대상(origin line ~86)이 "설계 리팩터링 Codex 상시 격상 (RefactorAgent 설계-lane inline 존치)" 를 **명시적 non-goal 선언**. amendment 로 흡수하면 ADR-137 이 자기 non-goal 을 뒤집는 자기모순 → 신규 carrier(ADR-138) 로 분리. (§결정1 근거)
- **(b) ADR-059 단독 amendment (신규 ADR 없이)** — 거절. ADR-059 = **debate 엔진 SSOT**(protocol schema·라운드·termination·anti-sycophancy). enum 추가는 엔진 갱신이라 ADR-059 Amendment 4 가 sibling 으로 맞으나, **정책 신설(설계 리팩터링 결정 방식 격상)의 carrier 는 엔진 ADR 이 아님** — 정책 결정 기록은 별도 ADR 필요. → ADR-138 carrier + ADR-059 Amd4 sibling 분리. (§결정1 근거)
- **(c) 대칭 enum(blanket_cross_module_designlane) 재사용** — 거절. 해당 enum = **대칭(role_assignment 없음)** + cross-module Story 전체(Change Plan §3/ADR/§7/§11) 대상. 본 Story 는 Codex=proponent/Claude=opponent **방향 배정 필요**(role_assignment) + 구조 축 per-Story 대상 → 방향배정·scope 양면 부정합. `blanket_refactor`(refactor lane 전용·Epic-close cadence)도 lane·cadence 부정합. → 신규 `blanket_designrefactor` enum. (§결정2 근거)

## 해소 기준
N/A — permanent policy (상시 강화, sunset 대상 아님). 설계 리팩터링 결정 방식의 상시 거버넌스 조항 — 시한부 전환(transitional) 아님. 후속 실증 확보 시 강화(ratchet↑) 가능하나 약화 경로 없음.

## 관련 파일
- `plugins/codeforge-design/agents/RefactorAgent.md` — 대립 해소 프로토콜 debate 격상 + advocacy input provider 재정의 + anti-recursion 상속
- `docs/inter-plugin-contracts/debate-protocol-v1.md` — v1.3→v1.4 (blanket_designrefactor dispatch enum 추가)
- `plugins/codeforge-design/CLAUDE.md` — fan-out/대립 절 debate 매개 + blanket_designrefactor disjoint from blanket_cross_module_designlane
- `skills/deputy-mandate/SKILL.md` — RefactorAgent advocacy 표 debate 매개 note
- `docs/orchestrator-playbook.md` — blanket_designrefactor 6-step dispatch 절(verdict judge=ArchitectAgent chief)
- `docs/domain-knowledge/domain/governance-principle/refactoring-activity-taxonomy.md` — "설계 리팩터링" 열 결정 방식=debate(GAP fill)
- **cross-ref**: `archive/adr/ADR-059-debate-protocol-v1.md` (Amendment 4 sibling — enum 추가) / `archive/adr/ADR-137-epic-close-implementation-refactor-triage.md` (axis-disjoint 대조, non-goal carrier) / `archive/adr/ADR-039` (§결정18/19 dispatch 재귀가드 재인용)

## ratchet / sunset
강화 방향(ratchet↑) — 설계 리팩터링 거버넌스 신설, 약화 0. `is_transitional: false` → `sunset_justification: N/A`. 어떤 기존 조항도 약화·완화하지 않음(단독 inline → adversarial debate 는 순수 강화).
