---
adr_number: 128
title: "완료 단계 정식화 — phase:완료 worktree-clean 게이트 + backstop 자동 트리거 복원 + wrap-up 4-트리거 수렴 SSOT"
status: Accepted
category: governance
date: 2026-06-20
carrier_story: CFP-2377
parent_epic: null
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-2377  # 본 ADR 신설 carrier (완료 단계 정식화)
related_adrs:
  - ADR-040   # Amendment 9 동반 — backstop SessionEnd async dispatch 자동 트리거 복원 + worktree-clean cleanup invariant 편입
  - ADR-045   # Amendment 13 동반 — phase:완료 precondition 에 worktree-clean self-check 추가 (2-gate AND → 2-gate + self-check)
  - ADR-026   # post-merge automation 4 action (갭 B 4-트리거 중 클라우드 측 1 — post-merge-followup.yml)
  - ADR-024   # Amendment 19 §B required-6-tuple-skip bypass 신설 금지 invariant — 본 ADR 게이트가 required check 신설 안 함 정합
  - ADR-127   # 모든 면제·단축경로 폐지 (forcing function 추가 방향 ratchet 정합 — process-skip 채널 신설 0)
  - ADR-005   # N/A 표준화 — 갭 C 유예 (산출물 target 부재 N/A vs 단축 구분) + change-plan 면제 anchor
  - ADR-060   # evidence-enforceable framework — worktree-clean local-only check 의 warning-tier 등록 (workflow:null)
  - ADR-068   # boundary completeness invariants — 게이트 차원(검증대상/timing/evidence/tier) 정합
  - ADR-099   # workflow:null local-only check 선례 (CI 미wire — standalone/세션-개시 호출, verified)
  - ADR-112   # Living Architecture per-Epic update gate — 갭 C owner (수렴 SSOT pointer 대상)
  - ADR-111   # Confluence mirror classification — 갭 C owner (Living Architecture 변경 시 mirror SLA)
  - ADR-119   # 검증-후-단언 + 제안 필요성 3문 게이트 — 갭 C 유예 판정 근거
related_files:
  - archive/adr/ADR-040-worktree-convention.md
  - archive/adr/ADR-045-story-retro-mandatory-trigger.md
  - docs/orchestrator-playbook.md
  - skills/worktree-lifecycle/SKILL.md
  - skills/post-merge-closure/SKILL.md
  - hooks/hooks.json
  - templates/scripts/check-worktree-stale.sh
  - docs/evidence-checks-registry.yaml
  - plugins/codeforge-pmo/agents/GitOpsAgent.md
  - templates/github-workflows/post-merge-followup.yml
  - templates/github-workflows/retro-mandatory.yml
mechanical_enforcement_actions:
  # 본 ADR = 완료 단계 정식화 umbrella. worktree-clean 완료-게이트 = 로컬-only check (클라우드 러너 worktree 미접근)
  # → required CI check 불가 (AC-2/AC-12). evidence-checks-registry 등록 = warning-tier + workflow:null (ADR-099 선례).
  # 갭 A backstop 자동 트리거 복원 = SessionEnd async dispatch (mechanical wire = Phase 2). 갭 B 수렴 = 절차 명문화 (mechanical 게이트 신설 0, AC-9).
  - action: worktree-clean-completion-gate
    status: deferred-followup     # Wave 1 declarative (본 Phase 1 ADR + playbook §9.7.1 precondition + skill SSOT). actual local check 스크립트 + evidence-registry workflow:null entry = Phase 2 PR scope.
    progress_note: "phase:완료 transition precondition 의 worktree-clean self-check (eager 미실행 검출 게이트). backstop(age 7d+)과 disjoint — 완료 worktree 는 0일령. 로컬-only (workflow:null, ADR-099/ADR-122 선례). required check 신설 금지 (AC-12 / ADR-024 Amd19 §B). fail-safe 4종 상속 (ADR-040 Amendment 9 §결정 9.A.4). Phase 2 = scripts/check-worktree-completion-clean.sh + evidence-registry warning-tier entry."
    target_section: §결정 2
related_carrier_issues:
  - 608   # OPEN sentinel #5 — Phase 1→2 boundary worktree sync (§결정 6 해소: 본 ADR 와 axis disjoint, 충돌 0)
  - 549   # OPEN type:story doc-only-fast-path — ADR-026 vs ADR-040 enum 결정 (§결정 6 해소: ADR-127 supersede 로 전제 stale, 흡수 권고)
  - 772   # OPEN adr-candidate — close-event auto-reopen 일반화 (§결정 6 해소: EC-5 정합, 본 게이트 ⊥ close lifecycle)
is_transitional: false
---

# ADR-128: 완료 단계 정식화

## 상태

Accepted (2026-06-20 KST, CFP-2377 carrier). `is_transitional: false` — 영구 정책. 본 ADR 은 **forcing function 추가(ratchet 강화) 방향** — 기존 "마무리(wrap-up)" 의 자율준수 의존을 줄이고 완료 단계를 정식 분류로 고정한다. 약화 방향이 아니므로 ADR-058 §결정 5 sunset_justification 의무 비대상.

## 본질 선언

> **merge 직후 "마무리(wrap-up)" 를 정식 "완료 단계" 로 격상한다. (A) worktree 정리가 정상 완료 경로에서 누락되지 않도록 `phase:완료` 전제조건에 worktree-clean self-check 를 추가하고, 비정상 종료 orphan 을 잡는 backstop GC 의 자동 트리거를 복원한다. (B) 4개로 흩어진 wrap-up 트리거의 수렴·종결을 단일 SSOT 로 명문화한다. 신규 lane 은 만들지 않고, 기존 게이트형 완료 단계(`gate:retro-complete` 패턴)를 확장한다.**

## 컨텍스트

### 사용자 directive (Story §1 = Issue #2377)

사용자 결정 = **신규 lane 신설 안 함**, 기존 게이트형 완료 단계를 확장해 "완료 단계" 정식화. 요구사항리뷰 lane PASS (2026-06-20T03:43:34+09:00) 확정 외부사실을 입력으로 한다.

### 두 약점 (실측 검증된 갭)

| 갭 | 본질 | 실측 근거 |
|---|---|---|
| **갭 A** | worktree 정리가 자율준수에만 의존 — 기계적 게이트 0 + backstop 자동트리거 0 | `hooks/hooks.json` SessionStart = `session-start`/`stale-local-main-checkout`/`stray-scratch-leak` 3개만, `check-worktree-stale` 호출 0건 `[verified]` (hooks.json:3-24). playbook §0a-prime/skill §4 는 "주기 backstop" 을 명시하나 실배선 부재 = 문서-실배선 drift. 2026-06-12 GC 캠페인 stale worktree 약 230개 (4.3G→192M) `[user-input]` = 갭 실증. |
| **갭 B** | 4개 독립 wrap-up 트리거의 수렴·종결 단일 SSOT 부재 | (1) `post-merge-followup.yml` 클라우드 (2) `retro-mandatory.yml` 클라우드 (3) GitOpsAgent worktree eager teardown 로컬 (4) Orchestrator `phase:완료` transition 로컬 — 두 실행평면(클라우드/로컬) 물리 분리. 수렴 확인 단일 SSOT 없음 `[verified]`. |
| **갭 C** | 완료 시 문서 재정합(Living Architecture / Confluence mirror) | **유예** — 이미 owner 존재 (§결정 5). |

핵심 통찰 = 갭 A 는 새 정책이 아니라 **문서-실배선 drift 복원**이며, 갭 B 의 단일-자동-수렴-검증기 불가능성은 갭 A 의 backstop-CI-불가와 **동근원**(클라우드 러너가 로컬 worktree 에 접근 못 함)이다.

### 확정 외부사실 (요구사항리뷰 PASS — 재논의 금지)

요구사항리뷰 lane 이 공식 문서(https://code.claude.com/docs/en/hooks.md "Run hooks in the background")를 firsthand 재검증해 확정한 외부사실:

1. **backstop GC 자동 트리거 = `SessionEnd` async dispatch 단일 wire 가 1순위** — SessionEnd = 세션당 1회 종료 발화 → backstop 의 7일 GC cadence 와 빈도 정합. async 지원 event. 대안 = `Stop` async(매 turn → throttle 필수). **SessionStart 는 async/동기 모두 금지** (async:true 는 무시되고 동기 실행 = 지연 회귀, 공식 문서 verbatim "SessionStart and Setup hooks do not support async or asyncRewake; the fields are ignored if set").
2. **async hook caveat** — stdout/stderr/exit/JSON 무시 (asyncRewake:true + exit 2 제외), 세션 조기 종료 시 미완 프로세스 termination.
3. **GitHub Actions cron = 구조적 배제** — 클라우드 러너가 로컬 worktree 미접근.

## 결정

### §결정 1 — 신규 lane 0 / 기존 게이트형 완료 단계 확장 (no new lane)

완료 단계 정식화 = 신규 lane 신설 0. `phase:완료` transition (기존 lane 시퀀스의 terminal) 을 정식 분류로 확장한다. 본 ADR umbrella + ADR-040 Amendment 9(backstop) + ADR-045 Amendment 13(precondition) 3-부분 묶음으로 codify (ADR-127 의 umbrella+amendment 구조 답습).

### §결정 2 — 갭 A: phase:완료 worktree-clean 게이트 (로컬-only, required CI 불가)

`phase:완료` transition 전제조건에 **"완료 Story 의 worktree 가 eager 정리됐는가" self-check** 1항을 추가한다. AS-IS = 2-gate AND (terminal gate + `gate:retro-complete`, playbook §9.7.1 line 2858) → TO-BE = 2-gate AND + worktree-clean self-check.

**게이트 tier (비협상 — AC-2 / AC-12)**:

`phase:완료` transition 은 Orchestrator self-write(로컬)이고 worktree 는 클라우드 러너 미접근 `[verified]`(playbook §0a-prime line 162; GitOpsAgent §5). 따라서 worktree-clean 게이트는 **GitHub Actions required CI check 불가**. 3-조합으로 기계화:

1. **(a) Orchestrator behavioral precondition** — playbook §9.7.1 `phase:완료` precondition 행에 worktree-clean self-check 1항 추가 (ADR-045 Amendment 13 §결정 13.A).
2. **(b) 로컬 check 스크립트** — `scripts/check-worktree-completion-clean.sh` (Phase 2). 완료 Story 의 worktree 가 잔존하는지 검출 (eager 미실행 게이트).
3. **(c) evidence-checks-registry 등록 = warning-tier + `workflow: null`** — 로컬 전용. `workflow: null` = CI 미wire 의도적 선언 (ADR-099 §결정 3 / ADR-122 회귀 방지 gate 선례 — `# CI 미wire — standalone manual / 세션-개시 호출` marker 동형). dead-check 가드 면제 = `detect_command` live + workflow:null marker (de-bloat 기준 "detect_command·workflow 모두 부재 = dead" 와 disjoint — `detect_command` live 인 local-only check 는 dead 아님).

**branch protection 6-tuple 무변경** — required check 신설 0 (ADR-024 Amendment 19 §B "required 6-tuple check 에 bypass escape valve 신설 금지" invariant 정합 — 신규 required check 자체를 안 만들어 우회 채널 신설 문제 원천 회피).

### §결정 3 — 갭 A: backstop GC 자동 트리거 복원 (SessionEnd async dispatch 단일 wire)

backstop GC(`templates/scripts/check-worktree-stale.sh`)의 자동 트리거가 복원된다 (현재 트리거 0 → 자동 발화). **스크립트 로직 자체는 무변경** — 트리거만 복원 (ADR-040 Amendment 9 §결정 9.B carrier).

- **자동 트리거 = `SessionEnd` async dispatch 단일 wire (1순위, 비협상)** — 확정 외부사실 1. 세션당 1회 → 7일 GC cadence 정합 + termination race 노출 최소.
- **대안 = `Stop` async dispatch** — repo 에 live 비차단 Stop hook 존재(`hooks/stop`, `trap 'exit 0' ERR`, exit 0 항상 `[verified]` stop:37-47). 매 turn 발화 → throttle(timestamp 파일 + N시간 쿨다운) 필수. SessionEnd 채택 불가 시(PoC fail) fallback.
- **배제(확정)** — SessionStart async:true(무시·동기 실행 = 지연 회귀) / SessionStart 동기(90+ worktree 스캔 시작 지연 재발) / GitHub Actions cron(클라우드 러너 로컬 worktree 미접근).
- **트리거 단일화 invariant (race 1순위 안전장치)** — SessionEnd + Stop 동시 wire **금지**. 단일 트리거면 동시 GC 실행 race 자체 미발생 → 멱등성 가정 불요 (EC-4 정정 정합).

### §결정 4 — 갭 B: 통합 wrap-up 수렴 SSOT (절차 명문화 + 텔레메트리 관찰, 신규 SSOT 신설 0)

4개 wrap-up 트리거의 수렴 확인·종결을 한 곳에서 cross-ref 하는 단일 SSOT 를 명문화한다. **별도 신규 SSOT 신설 금지** — 기존 `post-merge-closure` skill + playbook "완료 단계" 섹션 확장으로 수렴점을 명문화 (Continuity dup 회피).

| # | 트리거 | 실행평면 | 완료 시점 확인 방법 |
|---|---|---|---|
| 1 | `post-merge-followup.yml` (phase label 전환 / Story §9 write / carrier close) | 클라우드 | post-merge OUTCOME 텔레메트리 관찰 (`post-merge-counters.jsonl` outcome) |
| 2 | `retro-mandatory.yml` (`gate:retro-complete` + close-blocking auto-reopen) | 클라우드 | `gate:retro-complete` label 부착 + retro write 확인 |
| 3 | GitOpsAgent worktree eager teardown | 로컬 | worktree-clean self-check (§결정 2) — Orchestrator 완료 시점 확인 |
| 4 | Orchestrator `phase:완료` transition | 로컬 | precondition 3-조합 통과 확인 |

**수렴 검증 = 절차 명문화 + 기존 텔레메트리 관찰 조합** (AC-9). 단일 자동 수렴 검증기 불가 (클라우드↔로컬 비대칭). 로컬 self-write 가능 트리거(3·4) 상태는 완료 시점에 Orchestrator 가 한 곳에서 확인, 클라우드 측(1·2)은 post-merge OUTCOME 텔레메트리 관찰. **"기계 게이트 신설" 과설계 금지** — ArchitectAgent 가 단일 자동 수렴 검증기를 만들려 하면 클라우드-로컬 비대칭으로 구조적 불가.

### §결정 5 — 갭 C: 유예 (이미 owner 존재 — 수렴 SSOT 에 pointer 1줄만)

완료 시 문서 재정합(Living Architecture / Confluence mirror) = **본 Story 범위 제외(유예), 신규 체크포인트 신설 0**. 갭 B 수렴 SSOT 에 cross-ref pointer 1줄만 추가한다.

**유예 근거 (ADR-119 §결정 9 3문 게이트)**:
- **깨졌나?** No — 이미 owner 존재: ADR-112(Living Architecture per-Epic mandatory update gate, status: Accepted)의 trigger = Epic close 직전 + ADR-111 §결정 5 Confluence mirror SLA.
- **이득>비용?** No — 포함 시 (1) ADR-112/111/078 영역으로 scope 폭증 (2) per-Epic 게이트(ADR-112)와 per-Story 완료 게이트(본 ADR)의 granularity 축 충돌 (3) Confluence mirror sync = 별 lane(confluence-migration skill) owner.
- **안 봐도 할 일?** No.

→ **유예가 정답.** 단 갭 B 수렴 SSOT 에 "Living Architecture 재정합 = ADR-112 per-Epic 게이트가 담당(Epic 완료 시)" 1줄 cross-ref 를 넣어 수렴 SSOT 가 갭 C 영역을 인지(awareness)하게 한다 (신규 체크포인트 아닌 pointer).

### §결정 6 — 인접 충돌 3건 해소 방향

| Issue | 상태 | 본 ADR 과의 관계 | 해소 방향 |
|---|---|---|---|
| **#608** ("Sentinel #5" Phase 1→2 boundary worktree sync) | OPEN, `codeforge-improvement`/`from-cfp-597-retro` (sentinel, type:story 아님) `[verified]` | ADR-040 §결정 5 amendment 와 force-push 충돌 우려 | **axis disjoint — 충돌 0.** #608 = Phase 1↔Phase 2 PR **경계** worktree 동기화 sentinel(monitor-only). 본 ADR Amendment 9 = backstop **트리거** 복원 + 완료 worktree-clean. ADR-040 §결정 5 본문 무변경(트리거만 추가) → force-push 충돌 surface 0. #608 은 sentinel 로 유지(별 carrier). |
| **#549** (ADR-026 category vs ADR-040 enum, doc-only-fast-path label) | OPEN, `type:story`/`phase:요구사항`/`doc-only-fast-path`/`parent:CFP-543` `[verified]` | ADR-127 이 doc-only fast-path 폐지 → #549 의 "doc-only fast-path 자격" 전제 stale | **흡수/정정.** #549 의 `doc-only-fast-path` label 전제 = ADR-127 §결정 2 supersede 로 무효. 본 ADR 은 ADR-026 category enum 을 변경하지 않으므로 #549 의 미결 enum 결정과 충돌 0. **권고 = #549 를 ADR-127 supersede 반영해 retitle(doc-only fast-path 제거) 후 정식 full-flow Story 로 재발의하거나, scope 잔존 가치 미달 시 CLOSE_AS_OBVIATED**(별 closure batch). 본 Story 가 #549 결정을 떠맡지 않음(scope unitary). |
| **#772** (close-event auto-reopen 일반화 forcing function) | OPEN, `type:adr-candidate`/`priority:high`/`from-cfp-699-retro` `[verified]` | 새 worktree-clean 게이트가 close lifecycle 과 상호작용(EC-5) | **정합 확인 — 충돌 0.** 본 ADR 의 worktree-clean self-check 는 `phase:완료` **transition precondition**(label attach 직전)이지 Issue **close 차단**이 아니다. `retro-mandatory.yml` 의 close-blocking auto-reopen(`gate:retro-complete` 부재 시)과 axis disjoint — worktree-clean 은 reopen trigger 아님. #772(close-event auto-reopen 일반화)는 별 ADR-candidate 로 유지. 본 ADR §결정 2 게이트가 close lifecycle 에 새 reopen 경로를 추가하지 않음을 명시(중복 reopen 회피). |

### §결정 7 — ADR-127 면제폐지 정합 (forcing function 추가 방향, process-skip 채널 0)

본 ADR 은 forcing function **추가** 방향(ADR-127 ratchet 정합)이며 process-skip/생략 채널을 신설하지 않는다.

- `BYPASS_WORKTREE_GC=1` env = debugging/offline fail-safe(required check 우회 아님)라 ADR-127 §결정 1·2(process-derived fast-pass / skip-offer 폐지) 대상과 **별 범주** `[verified]`(ADR-127 §결정 1·2 = process-derived fast-pass 폐지; BYPASS_WORKTREE_GC 미열거). 본 env 는 origin 접촉 차단 환경·false-positive stale 의심·consumer opt-out 용 — lane/Story 생략 채널이 아니다.
- worktree-clean self-check 는 **eager 정리 검증 게이트**(정리 실행은 GitOpsAgent eager 가 owner, 본 게이트는 검증만 — 가정 1). 게이트가 통과 못 해도 정식 처리 = 정리 실행 후 재확인이지 "생략 후 진행" 이 아니다.

### §결정 8 — change-plan 면제 판정 (ADR-carrier = §3 설계 SSOT)

본 Story(CFP-2377)는 **별도 change-plan doc 면제** — 본 ADR-128 + ADR-040 Amendment 9 + ADR-045 Amendment 13 묶음이 §3 도입 설계 SSOT 역할을 충족한다 (ADR-013 dogfood-out 정합, ADR-127 §결정 2 단서 "ADR 가 §3 설계 SSOT 충족 시 change-plan 면제 = lane 생략 아님, 산출물 SSOT 통합"). story-epic-flow-preflight 정합. 이는 §결정 5 의 "N/A vs 단축" 구분상 산출물 SSOT 통합이지 노력 절감 skip 이 아니다.

### §결정 9 — N/A 분류 (ADR-127 §결정 5 3축 적용)

본 Story = src 0 인 wrapper-self governance codify. lane N/A 판정 (ADR-127 §결정 5 3축 AND):
- 설계 lane = ADR/skill/playbook 편집 = real target 있음(정식).
- 구현 lane(Phase 2) = playbook/skill/hooks/script/registry 편집 = real target 있음(정식, doc-only 생략 대상 아님).
- 통합테스트 lane = wrapper-self runtime behavior 부재 = N/A(정식 분류, plugin-meta-na).
- 보안테스트 = trust boundary 변경 0(hook 트리거 복원 = 로컬 GC, 외부 API/auth 비접촉 — ADR-040 §결정 5 보안 면제 cross-ref) = N/A.
- 배포/배포리뷰 = wrapper-self deploy target 부재 = N/A.

## 결과

- 완료 단계 = 정식 분류 (no new lane). `phase:완료` precondition 에 worktree-clean self-check 추가 → 정상 완료 경로 eager 누락 검출.
- backstop GC 자동 트리거 복원(SessionEnd async 단일 wire) → 비정상 종료 orphan 안전망 재활성 (2026-06-12 누적 230개 재발 차단).
- 갭 B 4-트리거 수렴 SSOT 명문화(기존 skill+playbook 확장, 신규 SSOT 0) → 클라우드↔로컬 비대칭을 절차+텔레메트리 조합으로 인지.
- 갭 C 유예 + pointer 1줄 → scope 폭증 회피, owner(ADR-112/111) awareness 유지.
- required CI check 신설 0 / branch protection 6-tuple 무변경 / process-skip 채널 0 → ADR-127 ratchet 정합.

## 비용 (정직 고지)

- worktree-clean 완료-게이트 = warning-tier advisory + behavioral precondition (로컬-only, CI 강제 불가) → Orchestrator 자율준수 의존이 0 으로 떨어지지 않는다. CI hard-block 으로 만들 수 없는 구조적 한계(worktree 클라우드 미접근)를 받아들인다. mitigation = local check 스크립트 + evidence-registry 등록으로 behavioral compliance 보조.
- backstop async hook 은 stdout/exit 무시 → 사용자-가시 로그(`DONE: pruned=N`)가 async 경로에서 안 보임. mitigation = asyncRewake(실패 시만) 또는 별도 로그 파일 (설계 권고, Phase 2).
- 부분 GC(termination race) 잔여 가능성 — check-worktree-stale.sh record-unit 독립평가·always exit 0 로 부분 실행도 안전 추정(`[hypothesis]`, 구현 lane 실측).

## 해소 기준

N/A — `is_transitional: false` (영구 정책, 강화 방향 ratchet).

## 관련

- [ADR-040](ADR-040-worktree-convention.md) — Amendment 9 (backstop SessionEnd async 트리거 복원 + cleanup invariant worktree-clean 편입)
- [ADR-045](ADR-045-story-retro-mandatory-trigger.md) — Amendment 13 (phase:완료 precondition worktree-clean self-check 추가)
- [ADR-026](ADR-026-post-merge-automation.md) — post-merge automation 4 action (갭 B 트리거 1)
- [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) — 면제·단축 폐지 (본 ADR ratchet 정합)
- [ADR-112](ADR-112-living-architecture-update-gate.md) — Living Architecture per-Epic gate (갭 C owner)
- [ADR-111](ADR-111-confluence-mirror-classification-policy.md) — Confluence mirror SLA (갭 C owner)
- [ADR-099](ADR-099-atlassian-allow-redefinition.md) — workflow:null local-only check 선례
- CFP-2377 — 본 ADR carrier Story
