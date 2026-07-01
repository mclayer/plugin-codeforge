---
adr_number: 137
title: Epic-close 구현-리팩터링 triage governance
status: Accepted
category: governance
date: 2026-07-01
carrier_story: CFP-2541
supersedes: []
related_adrs:
  - ADR-059  # debate-protocol-v1 — 엔진 (§결정11 blanket_refactor + role_assignment, triage=Story C 소유 경계). ADR-137 = 소비 governance, ADR-059 = 엔진 계약
  - ADR-045  # §D-11 retro batch closure — Epic-close sibling (같은 시점·PMOAgent owner) but 모집단·enum axis-disjoint (동일시 금지)
  - ADR-119  # §결정9 발견≠필요 3문 게이트 — drop 분기 filter 축
  - ADR-042  # Amendment 18 — (d)reusability 측정 축 RefactorAgent→구현 리팩터링 triage 소관 이동. ADR-137 = 그 종착지
  - ADR-039  # §결정18 merge-time Codex adversarial dispatch Orchestrator inline 전용 (재귀 가드) + §결정19 lead 위임 — producer/consumer 분리 hard constraint 원천
related_concepts:
  - deferred-item-lifecycle  # defer 분기 연동 (narrative-recorded state), 게이트 전용 직교 enum {tracked, observed} 선례 답습
  - refactoring-activity-taxonomy  # 구현 리팩터링 (d) Reusability 정의
is_transitional: false
---

# ADR-137 — Epic-close 구현-리팩터링 triage governance

## 상태
Accepted (2026-07-01) — Epic CFP-2533 Story C carrier. debate-protocol-v1(ADR-059) 엔진 위 구현-리팩터링 Epic-close triage governance SSOT.

## 컨텍스트

Epic CFP-2533 은 "리팩터링"을 관측 시점으로 2활동 분리했다 (refactoring-activity-taxonomy):
- **설계 리팩터링** = RefactorAgent 설계-lane inline advocacy (매 Story, (a)decoupling/(b)pattern/(c)interface + repo-분해 escalation).
- **구현 리팩터링** = 실코드 위 중복·재사용 측정 ((d) Reusability). **실코드가 생겨야 관측 가능** → 설계-시점 falsifiable 계측 물리 불가.

ADR-042 Amendment 18(Story B)이 (d) 측정 축을 RefactorAgent out-of-mandate → 구현 리팩터링 triage in-scope 로 소관 이동. 본 ADR = 그 triage 의 governance SSOT.

**hard constraint (Feasibility 장벽1 실측)**: PMOAgent 는 직접 subagent spawn 불가(PMOAgent.md L288) + ADR-039 §결정18 이 merge-time Codex adversarial dispatch 를 Orchestrator top-level inline 전용으로 못박음(subagent owner → `subagent_recursion_blocked` silent skip = 게이트 연극화). PMOAgent 를 debate producer 로 두면 silent fail.

## 결정

### 결정 1 — Epic-close 구현-리팩터링 triage 신설 (§D-11 sibling, axis-disjoint)

Epic-close 수렴 시점(Epic 하위 전 Story merged, playbook §9.7.2 Orchestrator 판정)에 구현-리팩터링 triage 1회 배치 발동. debate-protocol-v1 `blanket_refactor` dispatch(role_assignment={codex:proponent, claude:opponent}, min-3/max-5) 로 실머지 코드 중복·재사용 anchor 를 Codex execute-and-falsify 실측.

**§D-11(ADR-045) axis-disjoint (동일시 금지 invariant)**:

| | ADR-045 §D-11 | ADR-137 triage |
|---|---|---|
| 발동 시점 | Epic-close (동일) | Epic-close (동일) |
| owner | PMOAgent (동일) | PMOAgent (동일) |
| **대상 모집단** | 누적 retro follow-up **Issue**(≥3) | 실머지 **코드 duplication anchor** |
| **결정 enum** | CLOSE_AS_OBVIATED/SENTINEL/PROMOTE/DEFER | now/defer/drop |

§D-11 5-column structured-row 는 **패턴 참조 선례로만** 인용 — closure enum **값 비재사용**. deferred-item-lifecycle 이 §D-11 과 별 enum `{tracked, observed}` 를 신설한 선례를 답습(disposition 축 ⊥ narrative 판정 축). ADR-059 §결정11 이 "triage=Story C 소유"로 경계를 그었으므로 §결정12 흡수는 자기모순.

### 결정 2 — 3분기 triage verdict (now / defer / drop)

각 duplication anchor 별 ∀-전칭 판정:

- **now** — 별도 리팩터 Story 정식 10레인 발의. 조건 = debate 합의 "지금 리팩터" + ADR-119 3문 전부 YES. safety guard 1(결정 3) 상속.
- **defer** — 이연 + forcing-function. deferred-item-lifecycle **narrative-recorded** state 진입 → `check-deferred-item-recovery.sh` 회수 강제. **triage-defer verdict → §deferred structured 5-column row 변환 append = 본 ADR 배선 의무**(dead-path 방지). **착지 파일 = `EPIC-RESULTS-<EPIC_KEY>.md` 의 `## §deferred` 섹션**(PMOAgent self-write, Epic-close artifact) — 그 파일이 `check-deferred-item-recovery.sh` 인자 목록(playbook §9.7.2 self-check)에 등록돼 `_scan_retro_file` 도달 보장. row 의 **기존 `source` column**(origin `_evaluate_row` L135 `cells=[disposition,item,tracking,rationale,source]` — 이미 5번째 상주, CFP-2470/W2)에 값 `triage-defer` 를 명시(column 신규 추가 아님 — 값 도메인 확장; retro-narrative 와 변별, 경계혼합 방지).
- **drop** — ADR-119 §결정9 3문(깨졌나·강제요인 / 이득>비용·리스크 / 관찰자 없어도 할 일) 중 1+ NO → 기각. "관찰됨·미조치" 1줄 + cross-Epic drop-ledger row(결정 4).

**quantifier invariant**: ∀ a ∈ A: verdict(a) ∈ {now,defer,drop}. |A|=0 = triage skip(vacuously true) + "triage skipped: no anchors" 기록.

### 결정 3 — safety guard 1: behavior-preserving (INV-BP)

now-발의 리팩터 Story §8 Test Contract 에 INV-BP = **P1(기존 test 파일 git-diff 무변경) AND P2(기존 suite 전부 GREEN)** 강제(source: Fowler DefinitionOfRefactoring — observable behavior 불변). precondition = 대상 anchor 기존 coverage>0. coverage=0 → P2 vacuous → characterization test 선작성 OR now→defer 강등.

### 결정 4 — safety guard 2: anchor-recurrence cross-Epic (anti-recursion)

debate-protocol §3.4 anchor-recurrence(≥2 escalation) 상속하되 키잉 scope 를 **cross-Epic** 로 확장(§3.4 원본 = per-Story §9 count 로 cross-Epic 재발 미포착). drop verdict anchor → **cross-Epic append-only drop-ledger `docs/refactor-triage/drop-ledger.md`** 영속화(EPIC-RESULTS 는 per-Epic 이라 cross-Epic 재발 state 미보유 → 전용 파일 필수). escalation = `count(drop-ledger rows WHERE anchor_stable=X) >= 2` → AskUserQuestion. **count 실행 = PMOAgent verdict judge @ 매 Epic-close triage**(drop-ledger read → 신규 anchor_stable 매치 count; 신규 스캐너 0, recovery 스크립트와 disjoint — drop-ledger 는 §deferred 아님). `anchor_stable` = `file::Sym.method` OR content-hash(line-independent — `<file>:<line>` 은 리팩터 후 붕괴). semantic-equivalence = PL judgment(EC-7 상속).

### 결정 5 — producer/consumer 분리 (재귀 가드 회피)

- **PMOAgent** = triage **verdict judge**(owner) — self-spawn 불가(L288)라 debate 실발동 안 함. verdict 3분기 판정만.
- **Orchestrator top-level inline** = debate 실 dispatch(ADR-039 §결정18 merge-time Codex adversarial 전용).
- **lead 위임**(§결정19) = per-Story dispatch topology enabler.
- **RefactorAgent** = debate transcript consumer(debate-protocol consumer L41).

debate-protocol producer L36 placeholder → `PMOAgent = blanket_refactor triage verdict judge (dispatch ≠ PMOAgent, = Orchestrator inline §결정18)`.

### 결정 6 — 엔진 재사용, MINOR bump 불요

debate-protocol-v1 v1.3 스키마 완비(blanket_refactor + role_assignment). cadence(Epic-close 1회)=producer 배선(schema 밖, ADR-059 L246). 신규 dispatch enum·필드 0 → **MINOR bump 불요**(producer/consumer 문구 실배선만).

## 비대상 (out-of-scope)

- 매 Story blanket debate (Epic-close 배치로 비용 한정).
- 설계 리팩터링 Codex 상시 격상 (RefactorAgent 설계-lane inline 존치).
- deferred-item-lifecycle / check-deferred-*.sh 자체 **로직 변경 0** (재사용 — 기존 5-column 스캔이 `source=triage-defer` row 를 파싱, enum 값 무관). `source` column 은 origin 상주(신규 추가 아님); 값 도메인에 `triage-defer` 명시만.

## 결과

- 강화 방향(ratchet ↑) — 구현-리팩터링 거버넌스 신설, 약화 0. is_transitional false → sunset_justification N/A.
- **ADR-086 5-checklist**: #1 axis-disjoint(§D-11 모집단·enum ⊥) / #2 cost(신규 spawn 0, Epic-close 1회 배치) / #3 consumer carrier(defer→deferred-item-lifecycle 재사용) / #4 sibling align(Epic CFP-2533 Story A/B cross-ref) / #5 deferred trigger(Phase 2 실배선).
- **cross-ref 양방향(ADR-082 §결정9)**: ADR-045 §D-11 ↔ ADR-137 / ADR-059 §결정11 ↔ ADR-137.

## 관련 파일

- `docs/inter-plugin-contracts/debate-protocol-v1.md` — 엔진 (blanket_refactor dispatch + role_assignment), producer/consumer 실배선
- `plugins/codeforge-pmo/agents/PMOAgent.md` — triage verdict judge mandate (Epic-close)
- `docs/refactor-triage/drop-ledger.md` — cross-Epic append-only drop-ledger (PMOAgent read/count ≥2 escalation)
- `templates/epic-results.md` — §deferred 5-column 착지 섹션 (triage-defer)
- `docs/orchestrator-playbook.md` §9.7.2 — Epic-close convergence triage step + recovery self-check EPIC-RESULTS 등록
- `scripts/check-deferred-item-recovery.sh` + lib — 로직 무변경 재사용 (source=triage-defer row 수용)
- `docs/domain-knowledge/concept/deferred-item-lifecycle.md` — defer 분기 narrative-recorded state 연동
