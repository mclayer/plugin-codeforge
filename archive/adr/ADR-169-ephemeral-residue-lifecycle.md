---
adr_number: 169
title: "세션 잔재 수명 규약 (ephemeral residue lifecycle) — worktree GC 집행 격차 해소 + 발견 스캐너 + scratch/Temp/stash 가시화"
status: Proposed
category: process
date: 2026-07-26
related_files:
  - templates/scripts/check-workspace-residue-discovery.sh
  - scripts/lib/check_workspace_residue_discovery.py
  - scripts/lib/check_orphan_worktree_classify.py
  - scripts/lib/check_stash_aging_census.py
  - scripts/lib/check_harness_temp_residue.py
  - templates/scripts/check-codeforge-scratch-ttl.sh
  - scripts/lib/check_codeforge_scratch_ttl.py
  - hooks/worktree-location-guard
  - scripts/lib/check_worktree_location_guard.py
  - templates/scripts/check-worktree-stale.sh
  - hooks/session-start
  - hooks/hooks.json
  - docs/domain-knowledge/concept/ephemeral-workspace-lifecycle-gc.md
related_stories:
  - CFP-2822
amendments: []
---

# ADR-169 — 세션 잔재 수명 규약 (ephemeral residue lifecycle)

## 상태
Proposed (CFP-2822 Phase 1)

## 컨텍스트

2026-07-23~24 실측 정리에서 잔재 22GB 회수(worktree 77개·데이터 손실 0). 축적 근본원인 = 2축:
1. **집행 격차** — 기존 표준(ADR-040 eager + backstop GC)의 배선은 전량 landed(drift 아님, `[verified: Continuity §4.3]`)이나 2-layer 설계(advisory 완료-게이트 + 보수 backstop)의 구조적 상한 실현: crash 미발화 + advisory ceiling + fail-safe 보수성 + per-repo 협소.
2. **표준 미커버 사각지대** — codeforge-scratch(TTL 0)/Temp 세션 스크래치/workspace root `_wt-*`/독립 clone/stash/방치 체크아웃 = 기존 스캔 범위 밖.

사용자 why(§1 verbatim): "찌꺼기가 쌓이지 않도록 표준을 확실하게 정립" — 생성 시점 수명 규약 + 자동 회수 + 완료 게이트 검증.

외부 표준 수렴(Researcher §6.3, 8 시스템): ① 수명은 생성 규약에 선언(systemd-tmpfiles Age) ② 트리거 {주기+시작-시점 catch-up+용량 임계} 2+ 중첩(종료-훅 단독 의존 사례 없음) ③ age = last-access ④ 보존 예외 = 명시 마커 ⑤ 용량 상한 백스톱 ⑥ 사용자 데이터 계열(stash)은 자동삭제 대신 가시화. git 사실: `git worktree prune` = metadata-only(실 dir 미삭제, F1) / stash 무만료(reflog.c expire=0, F4) / harness 자체 lazy GC 채택(F6) but Temp 는 문서 미포함(F7, #17990).

## 결정

### §결정 1 — ephemeral residue lifecycle 신규 bounded context 정립

"세션 잔재" = 작업 수행 위해 생성되고 완결 후 가치 소멸하는 파일시스템 산출물. 4분류(도구-등록형/규약-위치형/미등록 orphan/제3자-소유). 기존 "registered worktree lifecycle"(ADR-040) 와 인접하나 분리 — 신규 context 는 잔재 전반(worktree 포함 상위집합)의 발견/분류/가시화, "지워도 되는가" 최종 판정은 각 클래스 오너 위임(anti-corruption layer). concept SSOT = `docs/domain-knowledge/concept/ephemeral-workspace-lifecycle-gc.md`.

### §결정 2 — 발견(discovery) 스캐너 신설 (check-worktree-stale.sh 확장 금지)

multi-repo walk + orphan 3-분류 + scratch TTL + stash/체크아웃 census 를 **별도 신규 모듈**로 신설(ADR-061 thin-wrapper). check-worktree-stale.sh(단일 repo scoped, worktree-list iterate)에 병합 금지. 5-함수 파이프라인(discover→classify→judge→execute→report, judge/execute 분리로 INV-9 2단계를 execute flag 로 제어). 등록 worktree 축 = 기존 스크립트 subprocess 위임(재구현 금지, anti-corruption). 출력 = 별도 네임스페이스 `[residue-scan] DONE: scanned=N flagged=M`(기존 output contract 무접촉, INV-5).

### §결정 3 — orphan 3-분류 + 보존 트리거 = 상태 신호 한정 (INV-1 이식)

3축(등록여부/git존재/상태검사)은 **분류 신호로만**, 보존 트리거 = 상태 신호(dirty/unpushed/locked/pin/INCONCLUSIVE) 1+ 양성 또는 판정 불능 시 fail-safe 보존 + 메타파일 사유 기록. **등록·존재 여부 자체 ≠ 보존 사유**(AC-12). 신규 스캔 클래스(scratch/Temp/clone/stash)에도 data-loss 가드 일관 이식. mtime 단독 삭제 금지(상태신호 AND). 07/24 unpushed 2건 near-miss = (A)age-only/(B)등록-only 판정의 data-loss 리스크 실증.

### §결정 4 — 크래시 보완 트리거 = SessionStart detached lazy GC primary (ADR-040 §결정 5·ADR-128 §결정 3 단일-wire sub-claim scoped-supersede)

SessionEnd best-effort eager 유지 + SessionStart detached lazy GC 를 주 크래시-안전 경로로 추가. SessionStart hook 즉시반환 + 진짜 분리 프로세스 spawn(실 스캔 백그라운드) → ADR-128 이 SessionStart 를 배제한 "async 무시→동기 full-scan→지연 회귀" 전제를 detach 로 붕괴. detach = Windows Start-Process -WindowStyle Hidden(fd 완전분리) / POSIX setsid·nohup+disown(bash nohup 은 harness 트리 wait 시 미분리 가능 → Start-Process 권장). OS 스케줄러(ADR-110) = consumer opt-in 보조(주 트리거 아님 — Windows-only + race 최악 + persistent 보안벡터). 2차 트리거 활성화 전 mkdir lock + cooldown + 멱등 선행 의무(E10, 순서 = step0 detach 실작동 검증→step1 lock 착지→step2 double-delete 0 GREEN→step3 활성화). **detach-infeasible contingency(F-C-1)**: SessionStart detached-spawn 이 harness 트리 wait 하 실분리되는지는 설계시점 검증 불가(단일 외부기술 전제) → §5.2 step0 에서 미분리 판명 시 AC-13 primary 대체 = OS 스케줄러 wrapper-default 조건부 승격(비-Windows cron/systemd-timer) 또는 AC-13 을 best-effort catch-up tier(Orchestrator behavioral GC step)로 재정의. SessionStart 배제 재해석(무거운 동기 full-scan 한정)은 무변경, 대체 경로만 추가. **본 §결정 4 는 ADR-040 §결정 5(Amendment 9) 및 ADR-128 §결정 3 의 '단일 트리거 전용 wire → 멱등성 가정 불요' sub-claim 을 scoped-supersede 한다**(두 ADR 의 나머지 결정 무손상 — 부분 supersession, 전체 supersede 아님). 진짜 invariant = 동시 GC 실행 race 방지이며, 다중 wire(SessionEnd eager + SessionStart detached lazy)에서 mkdir 원자 lock + cooldown + 멱등 remove(E10)가 race 를 막고 멱등성이 필수다. (구 ADR-040 Amd10 / ADR-128 Amd2 페어 amendment 는 재제정-ratchet 회피 위해 폐지 — 재해석 SSOT 를 본 §결정 4 로 단일화.)

### §결정 5 — 생성위치 강제 = PreToolUse(Bash) 로컬 가드 primary (2중방어)

`git worktree add` target 이 표준 위치(`~/.claude/worktrees/`) 밖이면 warn(도입기)→block(승격기) 하는 PreToolUse(Bash) 로컬 hook(repo-confinement sibling). tier 파라미터(WORKTREE_LOCATION_GUARD_TIER=warn|block). CI-lint 편입 비채택(로컬 생성 시점 실패모드 + 클라우드러너 로컬 worktree 미접근 구조적 한계). **정직한 한계**: matcher 회피(비-Bash 경로)/명령 난독화로 완전차단 불가 — 1차 예방(best-effort, fail-open) ⊕ 2차 검출(discovery AC-11 사후 가시화) 2중방어. "기계적 차단" ≠ 완전봉인(over-claim 금지).

### §결정 6 — scratch TTL + Temp 회수 2단계 (INV-9)

codeforge-scratch 순수 loose 파일 age>TTL 자동 purge(`.git` 보유 항목 제외→orphan 회부). Temp 회수 2단계: 1단계(관측·git-aware 판정, 즉시) / 2단계(삭제, default DISABLED — self-scratchpad 배제 + 활성세션 proxy + harness GC 중복(G1) 해소 3전제 충족 후 활성화). INV-9 = 보안 불변식(제3자 소유 + 활성세션 보호). Temp 삭제 활성화 시 harness self-GC 있어도 IDEM-3(존재 재확인)이 double-delete 흡수하는 보수가정 명문화.

### §결정 7 — fail-safe 무한 잔존 방지 = 가시화 + aging 재알림 (TTL 아님)

보존 판정은 사유 + 나이 가시화 + 임계 초과 재알림 동반(INV-3). 자동 삭제 기한(TTL 강제 삭제) 신설 = 보존 원칙 역행이라 기각(stash 자동삭제 = Non-goal, git 무만료 = 의도적 사용자 데이터). 재알림 = 지수 backoff(base 7d→max 90d) + dedup(item+reason key) + 집계 리포트 1줄 + SessionStart advisory non-blocking. 상태파일 = codeforge-scratch 밖(`~/.claude/worktree-gc-state/`) self-exemption.

### §결정 8 — bypass env 3종 disjoint 예약 (INV-6)

`BYPASS_WORKTREE_LOCATION_GUARD`(①) / `BYPASS_WORKSPACE_RESIDUE_SCAN`(③④) / `BYPASS_CODEFORGE_SCRATCH_TTL`(②) 신규 예약(기존 31개 disjoint). 별도 축: `TEMP_GC_DELETE_ENABLED`(default-off, Temp 삭제 gate) / `WORKTREE_LOCATION_GUARD_TIER`(tier). 각 사용 시 audit 한 줄 + 전역 export 경고 + 본 ADR SSOT 등재. 가드-무력화 env(GC_TEMP_IGNORE_RE/GC_*_BIN) production 미노출, test-only 격리.

### §결정 9 — phase:완료 residue-clean self-check precondition (완료-게이트 형제)

완료 Story 잔재(worktree + scratch + stash + orphan)의 가시화·정리 여부를 `phase:완료` transition precondition 에 self-check 1항으로 추가한다: "완료 Story 의 잔재가 가시화·정리됐는가" — discovery 스캐너 Story-scoped 모드(`--story-key cfp-NNN`)가 생성한 리포트 확인. **자동 삭제 강제 아님**(가시화 = §결정7 INV-3, stash 자동삭제 Non-goal).

**tier 3-조합** = (a) Orchestrator behavioral precondition(playbook §9.7.1) + (b) 로컬 check(discovery `--story-key` 모드, fail-safe 4종 상속) + (c) evidence-checks-registry warning-tier + `workflow: null`(ADR-099 / ADR-122 / ADR-128 §결정2 local-only 선례).

`gate:residue-clean` label 미신설(ADR-045 §D-12 worktree-clean 답습). branch protection 8-tuple 무변경(신규 required check 0). ADR-128 §결정2 worktree-clean 완료-게이트와 **disjoint 축**(등록 worktree eager 미실행 검출 ↔ 잔재 전반 가시화). 본 §결정9 = §결정7 가시화 mechanism 의 phase:완료 wire.

## 결과

- **긍정**: 잔재 발견/가시화가 표준화(사각지대 6종 커버) + 크래시-안전 트리거 + 생성위치 예방. data-loss 가드 신규 클래스 일관 이식.
- **부정/비용(정직)**: hard-block 완전 기계화 구조적 불가(로컬 상태 클라우드 CI 미접근) → 예방+검출 2중방어가 상한. 위치 가드 완전차단 불가(matcher/난독화). Temp 2단계 삭제는 G1 미해소 시 default-off(landing≠done). SessionStart detached cross-platform 주의(bash nohup 미분리 가능).
- **INV 무손상**: INV-1~9 전건 이식 확인. required check 신설 0(branch protection 8-tuple 무변경). agent 신설 0.

## 관련 파일

- `templates/scripts/check-workspace-residue-discovery.sh` / `scripts/lib/check_workspace_residue_discovery.py` — ③ 발견 스캐너 thin-wrapper + orchestrator(5-함수 파이프라인 discover→classify→judge→execute→report)
- `scripts/lib/check_orphan_worktree_classify.py` — ③ orphan 3축 분류 순수 판정(AC-12, stray checkout census 흡수)
- `scripts/lib/check_stash_aging_census.py` — ③ multi-repo stash 집계 + aging(AC-14)
- `scripts/lib/check_harness_temp_residue.py` — ③④ Temp 관측 + git-aware(AC-6 1단계, observe-only, INV-9)
- `templates/scripts/check-codeforge-scratch-ttl.sh` / `scripts/lib/check_codeforge_scratch_ttl.py` — ② scratch TTL purge thin-wrapper + SSOT(loose-file only, `.git` 제외 → orphan 회부)
- `hooks/worktree-location-guard` / `scripts/lib/check_worktree_location_guard.py` — ① PreToolUse(Bash) 생성위치 가드 polyglot dispatcher + 위치 판정 SSOT(`worktree_base()` 최초 소비자)
- `templates/scripts/check-worktree-stale.sh` — ⑤ mkdir lock + cooldown + idempotent-remove guard + `git worktree prune` 명시 호출(빈 껍데기 회수, output contract 무손상)
- `hooks/session-start` / `hooks/hooks.json` — ⑤ SessionStart detached fork 호출 + ① PreToolUse 배열 entry 추가
- `docs/domain-knowledge/concept/ephemeral-workspace-lifecycle-gc.md` — §결정 1 concept SSOT(잔재 4분류 + 외부 표준 수렴 모델)

## 관련 ADR

- ADR-040 §결정 5(Amd9) + ADR-128 §결정 3 — 본 §결정 4 가 '단일-wire/멱등-불요' sub-claim scoped-supersede (페어 amendment 폐지, 재제정-ratchet 회피). ADR-045 §D-14 원안 = 본 ADR §결정 9 로 relocation(residue-clean 완료-게이트 owner).
- ADR-027(consumer adoption 상위 protocol) + ADR-031(7일 grace·CFP-97 manifest install prior-art 선례 — ADR-040 자인) / ADR-058(evidence-gate 정확 인용) / ADR-061(thin-wrapper) / ADR-110(Task Scheduler opt-in) / ADR-009·ADR-024·ADR-127(제약).

## 해소 기준

N/A — permanent policy (세션 잔재 수명 규약 상시 적용, is_transitional: false).
