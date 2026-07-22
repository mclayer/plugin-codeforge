---
adr_number: 134
title: "병렬 적격성 판정 (정적 disjoint 5조건 + merge-time 동적 재검증 2단) + Orchestrator per-Story dispatch 운영절차 (Epic CFP-2481 Phase A E1)"
status: Proposed
category: orchestration-discipline
date: 2026-06-30
carrier_story: CFP-2488
parent_epic: CFP-2481
supersedes: null
amends: null
related_adrs:
  - ADR-050  # Parallel Epic Conflict Coordination — 직접 조상 (사람-세션-간 → 단일-lead-내 extends, supersede 아님)
  - ADR-039  # Orchestrator subagent default — §결정 19 (Amendment 7) spawn-권한 layer sibling carrier
  - ADR-085  # Multi-session collaboration protocol — session-level 충돌 layer (3-layer disjoint 명시)
  - ADR-036  # Project-key atomic reservation — atomic-claim 선례 (ADR 번호 직렬화는 E3a 격상)
  - ADR-040  # Worktree convention — teammate 격리 + lifecycle hooks 기반
  - ADR-009  # wrapper-only decomposition — Orchestrator 단일 spawn 권위 근원
  - ADR-064  # Decision principle mandate — sequential 강제 3 사유 (직렬화 5지점 normative 분류 축)
  - ADR-063  # Marketplace atomic invariant — version-bump disjoint (조건 3) 근거
  - ADR-073  # Orchestrator verify-before-assert — sentinel / merge-time 재검증 정합
  - ADR-109  # in-process 429 mitigation — 동시 Story cap resource-aware scheduling cross-ref
  - ADR-044  # team-spec / parallel_spawn_cap — concurrency limit cross-ref
related_files:
  - archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md
  - archive/adr/ADR-050-parallel-epic-conflict-coordination.md
  - archive/adr/ADR-RESERVATION.md
  - docs/orchestrator-playbook.md
  - docs/parallel-work/section-ownership.yaml
  - templates/github-workflows/parallel-epic-conflict-check.yml
mechanical_enforcement_actions: []
is_transitional: false
sunset_justification: "N/A — permanent orchestration-discipline policy. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 방향 — 병렬 적격성·merge-time 재검증·dispatch 운영절차 codify, 약화 0). ADR-050 supersede 아님 (extends — 적용 vector disjoint: 사람-세션-간 vs 단일-lead-내). 약화 방향 (적격성 5조건 AND→OR 완화 / merge-time 재검증 생략 / 사용자 병렬불가 표기 override / teammate→teammate 무한 재귀 허용) 발의 차단."
---

# ADR-134: 병렬 적격성 판정 + merge-time 동적 재검증 + Orchestrator per-Story dispatch

## 상태

`Proposed` (2026-06-30). Epic CFP-2481 (Epic 병렬 실행 정형화) Phase A 의 E1 (선행 root — 다른 child 가 본 기준을 인용). 본 ADR 은 **정책 정의** SSOT — merge-time 동적 재검증의 기계 wire / sentinel blocking / ADR 번호 atomic claim 등 **enforcement 코드는 sibling Story (E2 / E3a / E3b) 가 분산 소유**한다. Phase A 자신이 가드 부재 상태의 첫 병렬 dogfood 대상 (E1·E3a 동시 실행) — 사람 수동 감독 + ADR 번호 사전 예약으로 위험 흡수.

본 ADR 의 spawn-권한 layer = ADR-039 §결정 19 (Amendment 7) — Story-teammate = lead 위임 per-Story Orchestrator. 두 ADR 은 CFP-2488 안 paired carrier (axis disjoint).

## 컨텍스트

### 사용자 요구사항 (Story §1 verbatim)

Epic 병렬 실행 정형화의 E1 (Epic CFP-2481 하위, Phase A root):
- 신규 ADR (번호 134 예약): 병렬 적격성 판정 = 정적 pre-screen disjoint 5조건 (① 파일 ② ADR ③ version-bump ④ inter-plugin-contract ⑤ data-dependency disjoint) + **merge-time 동적 재검증 2단** (정적 disjoint 여도 main churn·공유 직렬자원으로 coupled 될 수 있음) + Orchestrator per-Story dispatch 운영절차.
- ADR-039 amendment: Story-teammate = lead 위임 per-Story Orchestrator (2-level 토폴로지).
- playbook 병렬 dispatch 섹션 + (제안 필요성 게이트 통과 시) 적격성 5조건 lookup skill.

### codeforge 의 세 종류 병렬 (도메인 구분 — Story §2.1)

| 병렬 종류 | 단위 | 주체 | 기존 거버넌스 | E1 관계 |
|---|---|---|---|---|
| (A) lane 내부 fan-out | 한 Story·한 lane 안 sub-agent | lane PL | playbook §4.1 병렬 가능 조건 (AND 3) | 포화 |
| (B) 복수 사람-Orchestrator 세션 | 서로 다른 Epic, 두 Claude 창 | 사람 2명 | ADR-050 / ADR-085 + ADR-RESERVATION | **직접 조상** — E1 이 단일-lead 로 확장 |
| (C) **단일-lead teammate 병렬** (E1 신규) | 같은 Epic 안 독립 Story | 1 Orchestrator(lead) → N teammate | **부재** — 본 ADR 가 codify | 신규 ADR-134 |

E1 은 "병렬을 처음 만드는 일"이 아니라 **(B) 의 인간-세션-간 충돌 조율 모델을 (C) 의 단일-lead-내 자동 dispatch 로 정합 확장**한다. ADR-050 이 "두 세션은 직접 통신 불가 → GitHub 가 유일 공유 채널"을 전제했다면, (C) 는 lead 가 모든 teammate 를 보므로 **직접 통신 가능한 lead** 가 조율 주체가 된다.

### Gap

1. **Story-level 적격성 판정 부재** — playbook §4.1 은 lane-level 3조건 (경로/입력독립/완료대기) 만 정의. Story 입도의 disjoint 판정 + codeforge 특유 공유 자원 (ADR 번호 / version bump / 계약 frontmatter) 축이 미정의.
2. **merge-time drift 차단 부재** — 정적 disjoint 판정은 dispatch 시점 스냅샷. main churn 으로 coupled 될 수 있으나 재검증 절차 미정의 (ABA 문제 동형).
3. **per-Story dispatch 운영절차 부재** — 단일-lead 가 적격 Story 들을 배치/감독/회수하는 절차 + stall 마찰 처리 책임 미정의.
4. **spawn-권한 위임 미정의** — teammate 가 자기 Story scope 안에서 lane PL 을 spawn 하는 권한이 ADR-039 Orchestrator-only 불변식과 정합하는지 미codify (→ ADR-039 §결정 19 carrier).

## 결정 (7)

### 결정 1 — 정적 disjoint 5조건 (AND, dispatch 시점 pre-screen)

두 Story 가 동시에 가도 서로를 깨뜨리지 않음의 **사전 증명** = codeforge 공유 자원 5축에 대한 교집합 0 검사. **5조건 모두 disjoint (AND)** 여야 safe-parallel 적격 — 하나라도 교집합 ≠ 0 이면 순차.

| # | 조건 | 의미 | codeforge hotspot 대응 |
|---|---|---|---|
| ① | **파일 disjoint** | 두 Story 의 touched path 교집합 0 | git merge conflict 회피. playbook §4.1 (1) "경로 분리"의 Story-level 승격. |
| ② | **ADR disjoint** | ADR 번호·본문 동시 점유 0 | ADR-050 충돌유형 1 (ADR 번호 충돌). serial-append 직렬화 지점 (E3a 가 atomic 격상). |
| ③ | **version-bump disjoint** | `plugin.json` 버전 동시 bump 0 | marketplace atomic sync (ADR-063) 깨짐 회피. |
| ④ | **inter-plugin-contract disjoint** | 계약 frontmatter 3-location (version / bumped_at / amendments) 동시 수정 0 | ADR-050 Amendment 1 (CFP-534) sentinel evidence 가 입증한 실 사고 패턴. |
| ⑤ | **data-dependency disjoint** | 한 Story 산출물을 다른 Story 가 입력으로 요구 0 | playbook §4.1 (2) "입력 독립"의 Story-level 승격. |

**5조건 = playbook §4.1 lane-level 3조건의 Story-level superset** — E1 은 새 판정 체계를 발명하는 게 아니라 기존 lane-level 판정을 Story 입도로 끌어올리고, codeforge 특유 공유 자원 (ADR 번호 / version bump / 계약 frontmatter) 을 명시 축으로 추가한다. 판정 입력 = 각 Story 의 planned scope (scope_manifest — ADR-050 §결정 재사용).

### 결정 2 — merge-time 동적 재검증 2단 (정적 판정의 stale 차단)

"정적으로 disjoint 여도 시간이 지나면 coupled 될 수 있다" (§1 user-input "정적 disjoint 여도 main churn·공유 직렬자원으로 coupled 될 수 있음"). 정적 판정은 **dispatch 시점 스냅샷** 이므로 merge 직전 2단 재검증으로 보완한다.

- **2단-(1) 실제 변경 delta 재교차** — Story 가 dispatch 시점에 선언한 planned scope 와 실제 작성된 diff 가 drift 할 수 있다 (scope_manifest 정확도 의존 — ADR-050 §부정). merge 직전 **실제 diff** 로 5조건 재교차.
- **2단-(2) base (origin/main) 갱신 후 충돌 재확인** — A Story 가 merge 되며 origin/main 이 churn → B Story 의 정적 판정이 stale. merge 직전 현재 origin/main SHA 로 충돌 재확인.

**ABA 문제 대응의 codeforge 판본** (Story §6.2 [verified] WebSearch): 정적 disjoint 판정이 "dispatch 시점 base = N (origin/main SHA)"을 읽고, merge 시점에 base 가 N→N'→... churn 했는데도 "정적으로 disjoint 였으니 안전"이라 오판하면 정확히 ABA 함정 (값만 보고 변경 이력 안 봄). **2단-(2) 는 ABA 해법의 버전 stamp 재검사와 동형** — origin/main SHA 자체가 version stamp 역할. ADR-036 §결정 1 (Story KEY 충돌을 GitHub Issue numbering 의 atomic·monotonic·immutable 보장에 위임해 race-window-0) 의 "원자 보장을 외부 권위에 위임" 패턴과 정합.

**경계**: 본 ADR 은 2단 **정책 정의** 만 소유. 기계 wire (실제 재교차 워크플로) = E2 / E3b 가 기존 `parallel-epic-conflict-check.yml` (PR overlap → `conflict:*` 라벨) 재사용 우선 (신규 워크플로 최소화 — Story §5.5 D-2).

### 결정 3 — Orchestrator per-Story dispatch 운영절차 (배치 / 감독 / 회수)

적격 Story 들을 per-Story teammate 로 **배치 (dispatch) → 감독 (supervise) → 회수 (reclaim)**. ADR-050 의 "merge-order 라벨 + GitOpsAgent 조율" (사람-세션-간 비동기 GitHub 라벨) 을 **lead 직접 감독** 으로 대체·보강한다 — 단일 lead 는 teammate return 을 직접 수신하므로 회수·순차화 결정을 즉시 내린다.

**운영절차** (playbook §4.5 가 본 ADR 을 SSOT 참조 — 중복 정책 금지, lookup mirror):

1. **배치 (dispatch)** — Epic 분해 후 적격 Story (§결정 1 5조건 AND PASS) 들을 per-Story background-Agent (Story-runner, SendMessage-addressable) 로 spawn. dispatch 메커니즘 = ADR-039 §결정 19 (background-Agent-as-Story-runner, 검증된 경로 — dogfood 실증).
2. **동시 Story cap = 2~4** — quota (Anthropic API rate limit) 선형 소비 주의. resource-aware scheduling (Story §6.3 [verified] — over-spawning 방지 concurrency limit) — ADR-109 (429 mitigation) / ADR-044 (parallel_spawn_cap) cross-ref. 경합 시 cap 축소.
3. **감독 (supervise) + stall 처리** — lead 가 dispatch 한 모든 teammate 진행을 **능동 모니터**. **stall 마찰** (ADR-039 §결정 19): child (손자 = teammate 가 spawn 한 lane PL 의 SubAgent) 완료 통지가 parent (lane PL) 아닌 lead (main) 로 surface → parent 무한대기. lead 가 stall 검출 시 **force-resume (SendMessage 로 parent 깨우기) 또는 TaskStop (회수)** 책임 (의무 단계 — 마찰 은폐 금지, ADR-119 검사연극 금지).
4. **회수 (reclaim) + 순차화** — teammate return 시 merge-time 2단 재검증 (§결정 2) → PASS 면 merge, drift 검출 시 충돌 Story 순차화. data-dependency 가 실행 중 드러나면 (AC-3) 재분석 트리거 → 충돌 Story 회수.
5. **사용자 병렬불가 표기 우선** (§결정 5) — 정적 5조건 통과 여부와 무관하게 순차 fallback.

### 결정 4 — 직렬화 5지점 명시 (Amdahl 임계 구역 = 병렬 speedup 상한 선언)

병렬화로 줄일 수 있는 시간에는 **수학적 상한** 이 있다 (Amdahl 법칙 — 직렬 비율 `f` 면 P→∞ 일 때 speedup `1/f` 수렴, 임계 구역은 한 번에 하나만 실행, Story §6.1 [verified]). codeforge 의 **직렬화 5지점** 은 정확히 Amdahl 의 임계 구역 (`f`) 이며, 병렬 Story 가 N 개여도 본질적으로 직렬이어야 한다 (공유 자원·순서 불변식):

1. **sentinel polling** — parallel-work sentinel (CFP-967 / ADR-073 Amd2) 3-mode detection 채널.
2. **ADR 번호 append** — ADR-RESERVATION sequential-append (GitOpsAgent 전용, 동시 append → positional conflict → re-sort). E3a 가 atomic 격상.
3. **version-bump merge-order** — plugin.json 버전 bump + marketplace atomic sync (ADR-063). 동시 bump = atomic invariant 깨짐.
4. **inter-plugin-contract frontmatter** — 계약 version / bumped_at / amendments 3-location.
5. **FIX-ledger Orchestrator 독점** — Story §10 FIX Ledger row append (fix-event-v1 contract, Orchestrator monopoly).

**함의**: 본 ADR 이 직렬화 5지점을 박제하는 것은 단순 문서화가 아니라 **"이 영역은 병렬화로 줄일 수 없다"는 상한 선언** 이다. 적격성 5조건이 노리는 speedup 은 임계 구역을 제외한 `(1−f)` 영역에서만 발생한다. 직렬화 지점을 줄이려는 E3a/E3b 노력 (예: ADR 번호 append 를 atomic 으로) 은 Amdahl 의 `f` 자체를 줄여 speedup 상한을 끌어올리는 시도다.

### 결정 5 — 사용자 "병렬불가" 표기는 적격성 판정을 override

사용자가 특정 Story 를 "병렬불가" 표기하면, 정적 5조건 (§결정 1) 통과 여부와 **무관하게 순차 강제** (표기 무시 금지). 적격성 판정은 자동 disjoint 검사일 뿐, 사용자의 명시적 순차 의도를 덮어쓰지 못한다. dispatch (§결정 3) 는 이 표기를 first-class 입력으로 받아 순차 fallback 한다.

### 결정 6 — ADR-050 / ADR-085 와 3-layer disjoint (extends, supersede 아님)

병렬 충돌 조율은 **적용 vector 가 다른 3 layer** 로 분리되며, ADR-134 는 ADR-050 / ADR-085 를 **인용·확장 (extends)** 한다 (supersede 아님 — 둘 다 active 유지). ADR-085 가 ADR-050 과 axis disjoint 신규 ADR 을 채택한 선례와 동형.

| Layer | ADR | 적용 vector | 주체 | 시점 |
|---|---|---|---|---|
| PR-level 사후 조율 | **ADR-050** | 복수 Orchestrator 세션 (서로 다른 Epic) 의 PR 충돌 4유형 | 사람 2+ 세션 | post-hoc (PR open 후 라벨 자동) |
| session-level 협업 | **ADR-085** | multi-session collaboration protocol (세션 간 조율) | 사람 다세션 | session-level |
| **Story-slot 단일-lead** | **ADR-134** | 같은 Epic 안 독립 Story 의 단일-lead-내 dispatch | 1 lead → N teammate | pre-hoc (dispatch 시점 5조건) + merge-time 재검증 |

**disjoint 근거**: ADR-050 = 주체가 **다른** (사람-세션-간, 직접 통신 불가 → GitHub 가 유일 채널). ADR-134 = 주체가 **같은** (단일-lead, teammate 를 직접 보고 즉시 회수). 적용 vector 가 disjoint 하므로 ADR-134 가 ADR-050 §결정 1 (사후 re-sort) / §결정 3 (non-blocking) 을 **약화하지 않고 1차 방어 layer 를 추가** (ratchet 보존). ADR-050 의 ADR-RESERVATION / scope_manifest / section-ownership.yaml / merge-order 라벨 = ADR-134 정적 5조건·dispatch 의 **재사용 가능 기반**.

### 결정 7 — ADR 번호 134 사전 예약 + Phase A 가드 부재 위험 흡수

신규 ADR 번호 **134** = Phase A 진입 전 사전 예약 (ADR-RESERVATION row append). **사전 예약 동기 = race/lapse 의 현재 LIVE 사례**: spec 작성 시점에 "132 = E1" 로 예약됐으나 그 사이 CFP-2469 (#2485 MERGED) 가 ADR-132 를 소비 (ADR-RESERVATION row 누락 lapse) → E1 이 **134** 로 재예약, E3a = 133. 이 132-row-lapse 자체가 본 Epic 이 잡으려는 race/lapse 의 현재 증거다 (ADR-RESERVATION 2-writer 공존 + 무 lock = 진원, E3a 가 atomic claim 으로 격상).

**Phase A 위험 흡수**: E1·E3a 가 race-guard (E2 sentinel blocking / E3a·E3b atomic claim) 없이 병렬 실행되므로 — **사람 수동 감독 + ADR 번호 (133/134) 사전 예약** 으로 위험 흡수. 본 Story 자신이 이 dogfood 의 산 증거 (E1·E3a disjoint 분리 = 파일·ADR 번호 disjoint 가 실제로 충돌 0 인지 retro 가 검증).

## go/no-go 결론 (teammate-spawn 실증)

요구사항-리뷰 §9 advisory 가 "agent-teams teammate 가 일반 subagent (lane PL) 를 spawn 가능?"을 **공식문서 UNVERIFIABLE** 로 판정 (teammate→teammate 금지만 명시). FAIL 시 dispatch 모델 재설계 (요구사항 lane 재진입) 조건이었으나 —

**재평가 (PASS)**: 본 Epic dogfood 세션이 **background-Agent (SendMessage-addressable) → 자기 sub-agent spawn** 을 실증 (Orchestrator → PL → sub-agent depth 0 → 1 → 2 실작동). 따라서:
- 본 ADR 은 dispatch 메커니즘을 **"background-Agent-as-Story-runner" (검증된 경로) 로 확정** 하고, 공식문서가 침묵하는 agent-teams "teammate" 특정 경로에 의존하지 않음을 명시 (over-claim 차단, ADR-119 검증-후-단언).
- **stall 마찰 명문화** (검사연극 금지): child 완료 통지가 lead 로 surface → parent 무한대기 구조적 한계를 §결정 3 dispatch 운영절차가 lead 능동 모니터 + force-resume/TaskStop 으로 흡수.

spawn-권한 codify = ADR-039 §결정 19 (Amendment 7) carrier.

## 회피된 대안

### 대안 A — ADR-050 supersede (중복 ADR 회피 목적)

ADR-050 이 이미 4 충돌유형을 다루므로 ADR-134 를 만들지 말고 ADR-050 을 supersede / 확장.

**거부 이유**: ADR-050 = 사람-세션-간 (주체 다름, GitHub 가 유일 채널), ADR-134 = 단일-lead-내 (주체 같음, lead 직접 감독). 적용 vector disjoint 라 supersede 는 ADR-050 의 사람-세션-간 조율을 부당 폐기. ADR-085 가 ADR-050 과 axis disjoint 신규 ADR 채택한 선례 정합. 채택 = §결정 6 extends (3-layer disjoint).

### 대안 B — merge-time 재검증 생략 (정적 판정만 신뢰)

정적 disjoint 5조건만으로 충분하다고 보고 merge-time 재검증 생략.

**거부 이유**: ABA 문제 (Story §6.2) — 정적 판정이 dispatch 시점 base 스냅샷을 읽고 merge 시점 churn 을 오판. scope_manifest drift (ADR-050 §부정) + main churn 으로 coupled 가능. 채택 = §결정 2 merge-time 2단.

### 대안 C — 신규 merge-time 워크플로 발명

merge-time 2단 재검증을 위한 전용 신규 워크플로 신설.

**거부 이유**: 기존 `parallel-epic-conflict-check.yml` (PR overlap → `conflict:*` 라벨, ADR-050 §결정 3) 재사용으로 충분 (신규 워크플로 최소화 — Story §5.5 D-2). 본 ADR = 정책 정의, 기계 wire = E2/E3b. 채택 = 정책 ADR-134 정의 + 기계 wire sibling 재사용.

## 결과

### 영향 (wrapper repo)

- `archive/adr/ADR-134-parallel-eligibility-dispatch.md` (본 file, 신규)
- `archive/adr/ADR-039-...md` §결정 19 (Amendment 7 — spawn-권한 layer, 동반)
- `archive/adr/ADR-RESERVATION.md` row 134 append
- `docs/orchestrator-playbook.md` §4.5 병렬 dispatch 섹션 신설 (본 ADR SSOT 참조 — Phase 2 구현 lane / E1 산출)
- (조건부) 적격성 5조건 lookup skill — 제안 필요성 3문 게이트 (ADR-119 §결정 9) 통과 시만. 미통과 시 playbook §4.5 로 충분 (Change Plan §3 미작성 사유 1줄 기록).

### 비-영향 (disjoint 보장 — sibling 소유)

- **ADR 번호 atomic claim 구현** = E3a (ADR-133) + E3b. #724 흡수는 E3a 몫. 본 ADR 은 "ADR 번호 append = 직렬화 지점" 명시만.
- **sentinel mechanical wire / force-push HEAD-pin** = E2. #1027 흡수는 E2 몫. 본 ADR 은 가드 부재 인지 + Phase A 수동 감독 흡수만.
- src/** production 코드 변경 0 (E1 = doc/ADR 중심).
- version-bump / inter-plugin-contract 수정 0 (marketplace sync = Epic 마무리 carrier).
- lane plugin / 6 SubAgent / inter-plugin contract 변경 0 (ADR-039 §결정 5 무손상).

### Reversibility

- Yes — 본 ADR `status: Deprecated` 전환 + playbook §4.5 revert 시 ADR-050 / ADR-039 기존 강도 복원. ADR-050 active 유지 (extends 라 supersede revert 불요).

## Out-of-scope

- merge-time 2단 기계 enforcement wire — E2 / E3b (정책 정의만 본 ADR)
- ADR 번호 atomic claim primitive (#724) — E3a (ADR-133)
- force-push HEAD-pin gate (#1027) — E2
- sentinel blocking wire (CFP-967/991 non-blocking → blocking) — E2
- consumer adoption — 별도 follow-on

## 관련 ADR

- **ADR-050** (Parallel Epic Conflict Coordination) — **직접 조상, extends**. 4 충돌유형 + ADR-RESERVATION + scope_manifest + section-ownership.yaml + merge-order 라벨 = 본 ADR 정적 5조건·dispatch 의 재사용 기반. 사람-세션-간 → 단일-lead-내 정합 확장 (§결정 6, supersede 아님).
- **ADR-085** (Multi-session collaboration protocol) — session-level 충돌 layer. 3-layer disjoint 의 두 번째 layer (§결정 6). ADR-050 과 axis disjoint 신규 ADR 채택 선례.
- **ADR-039** (Orchestrator subagent default) — **§결정 19 (Amendment 7) spawn-권한 layer sibling carrier**. Story-teammate = lead 위임 per-Story Orchestrator (2-level bounded 토폴로지). 본 ADR = 적격성·merge-time·dispatch, ADR-039 §결정 19 = spawn 권한 위임 (axis disjoint, CFP-2488 paired).
- **ADR-036** (Project-key atomic reservation) — atomic-claim 선례 (KEY=Issue# race-window-0). ADR 번호 직렬화는 미적용 (serial-append) → E3a (ADR-133) 격상.
- **ADR-040** (Worktree convention) — teammate 격리 (per-session worktree + lifecycle hooks) 기반.
- **ADR-009** (wrapper-only decomposition) — Orchestrator 단일 spawn 권위 근원. 2-level 위임이 이 원칙과 정합 (lead = 위임 단일 권위).
- **ADR-064** (Decision principle mandate) — sequential 강제 3 사유 (state dependency / shared resource / ordering invariant) = 직렬화 5지점 normative 분류 축.
- **ADR-063** (Marketplace atomic invariant) — version-bump disjoint (조건 ③) 근거.
- **ADR-073** (Orchestrator verify-before-assert) — sentinel (CFP-967/ADR-073 Amd2) carrier + merge-time 재검증 verify-before-trust 정합.
- **ADR-109** (in-process 429 mitigation) / **ADR-044** (parallel_spawn_cap) — 동시 Story cap resource-aware scheduling cross-ref.

## 해소 기준

N/A — permanent policy

## 관련 파일

- `archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` (§결정 19, Amendment 7)
- `archive/adr/ADR-050-parallel-epic-conflict-coordination.md` (extends 기반)
- `archive/adr/ADR-085-multi-session-collaboration-protocol.md` (3-layer disjoint)
- `archive/adr/ADR-RESERVATION.md` (row 134)
- `docs/orchestrator-playbook.md` (§4.5 신설 — Phase 2 / E1 산출)
- `docs/parallel-work/section-ownership.yaml` (ADR-050 §결정 4 섹션 정책)
- `templates/github-workflows/parallel-epic-conflict-check.yml` (merge-time 2단 재사용 대상)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-2488.md`
