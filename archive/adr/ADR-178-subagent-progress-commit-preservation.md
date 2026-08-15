---
adr_number: 178
title: 서브에이전트 진행 산출물 선행 적재(progress-commit) 규범 — 종료-원인 불문 zero-notice 보존
date: 2026-08-15
status: Proposed
category: orchestration-discipline
carrier_story: CFP-2966
supersedes: null
amends: null  # 순수 additive — 기존 ADR override/supersede 0 (Story §4.3 총평: 충돌 판정 0건)
related_adrs:
  - ADR-109  # (+Amd2) 침범 금지선 — (j)2 가 축 C 를 명시 OOS 로 비워둔 문면 근거. 판별식 D·R1 사다리와 trigger disjoint (§결정 7)
  - ADR-025  # (+Amd4) 침범 금지선 — limit-signal-halt form fence. §결정 6 whitelist 5종 무접촉 (§결정 7)
  - ADR-141  # (+Amd6/8) fresh-spawn only = 인계 프로토콜 제약 (§결정 5). failover ⊥ 보존 축 분리
  - ADR-170  # §결정 19(lead 생존 정의역 — 본 ADR 대상 밖) / §결정 20 INV-L2 (inconclusive 취급 근거, §결정 5)
  - ADR-169  # 잔재 수명 규약 — dirty/unpushed = 보존 트리거·GC 구조적 면제 (§결정 10 관할 경계)
  - ADR-040  # worktree-first + sequential merge + §7.K 완료-게이트 정의역 경계 (§결정 10)
  - ADR-039  # Orchestrator inline whitelist closed — 커밋 주체 = agent 소유 (§결정 2)
  - ADR-115  # hook "block 금지 + exit 0" — hook 을 강제 lever 로 설계 금지. Phase 2 신규 entry 시 Amd2 3규칙 판정 의무 (§결정 12)
  - ADR-143  # SubagentStart additionalContext 채널 선례 + advisory ceiling 정직 라벨 형식 답습 (§결정 8/12)
  - ADR-171  # warning-first — 기계 검사는 blocking 으로 태어나지 않음 (§결정 11/12)
  - ADR-172  # 세션-독립 잔재 관측 — 관측층 계약 상속 (사실 3-tuple·verdict 어휘 금지, §결정 11)
  - ADR-110  # 축 C 재개(세션 부활) 경로 — 본 ADR(산출물 보존)과 disjoint. 재개 세션 = 발견 채널의 재개자 실현체 (§결정 5)
  - ADR-071  # :1237 'checkpoint' 동음이의 — 본 ADR 명명 회피 근거. §결정 24 세션 사망 후 재개 인접 disjoint
  - ADR-119  # 검증 후 단언 — over-claim 금지·[hypothesis] 유지 저작 규율
  - ADR-133  # ADR 번호 OCC atomic claim — 본 번호(178) 예약 mechanism
is_transitional: false
related_stories:
  - CFP-2966
related_cfps:
  - CFP-2966  # carrier
  - CFP-2944  # 전제 — 한도 도달 시 자동 중단 금지 (축 A). 본 ADR 은 그 결정 위의 상보 축 C
  - CFP-2946  # disjoint — 살아있는 에이전트 재개 (축 B). §결정 13 later-lands-reconciles
  - CFP-2965  # 비용 실측 공급원 (훅 체인 지연세) + 세션 한도 사건 실증 (a-1/a-2)
related_files:
  - docs/orchestrator-playbook.md  # §3.5 step 3 — I-3 (커밋 트리거 return 종속) 공백의 문면 위치, Phase 2 정정 대상
  - hooks/hooks.json  # SubagentStart 채널 — Phase 2 priming entry 후보 (ADR-115 Amd2 3규칙 판정 동반)
  - skills/session-recovery/SKILL.md  # 축 C 회수 절차 pointer 착지 대상 (Phase 2) — 현행 salvage 관련 0-hit
  - scripts/lib/check_workspace_residue_discovery.py  # 발견 술어 `dirty|unpushed-N` — 관측층 (c′) git census 의 기존 표면
  - scripts/check-tier-honesty.py  # Phase 2 — advisory ceiling 라벨 registry 1행 등재 대상 (AC-11 기계 커버)
mechanical_enforcement_actions: []  # Phase 2 이행 — negative-control presence lint (기존 orchestrator-autonomy-stop-taxonomy-check.yml step 추가, bounded region + closed set) + check-tier-honesty registry 1행 + §8 RTM 명명 테스트 (normative 18). 본 ADR = 결정 SSOT.
---

# ADR-178: 서브에이전트 진행 산출물 선행 적재(progress-commit) 규범 — 종료-원인 불문 zero-notice 보존

## 상태

Proposed (2026-08-15) — CFP-2966 Phase 1(설계) carrier. ArchitectPL 검수 + 설계리뷰 PASS 후 Accepted 전환.

## 컨텍스트

세션 한도 도달 시 서브에이전트는 **강제 종료**되며, 이때 미적재 진행분이 소실된다 (축 C — 비의지적 종료 후 산출물 잔존·회수). in-repo 실증: 2026-08-13 서브에이전트 13개 동시 강제 종료·약 148분 소실 [verified — CFP-2965.md:17] / CodebaseMapper 초회 세션한도 강제종료·산출 0·전량 재수행 [verified — CFP-2965.md:620] / 유일 성공 salvage(커밋 `bd1acf992`)조차 규범면·감사면 기록 0 [verified — CFP-2966 Story §4.3 b-1/b-2].

구조 원인 2가지:
1. **커밋 트리거가 return 에 종속** — playbook §3.5 step 3 은 "sub-agent **return 후** 커밋"만 규정하여, return 이 없는 종료(강제 종료)에서 커밋 트리거가 정의되지 않는다 (I-3 공백).
2. **현행 산출 계약의 default = 최종 메시지(C6)** — durability 0 인 유일 채널이며 강제 종료가 정확히 파괴하는 것이 C6 이다 (INV-D1). 소실 취약성은 우발 결함이 아니라 산출 계약의 구조적 귀결이다.

기존 정책 지형에서 이 자리는 **명시적으로 비어 있다**: ADR-109 Amd2 (j)2 가 "비의지적 종료 = OOS" 로, ADR-025 Amd4 negative control 이 축 C 를 정당 구분선으로 각각 비워두었고, ADR-110 은 축 C 의 **세션 재개** 경로만 커버한다 (산출물 보존 결정문 0 — Story Iter1 P1-3 전문 판독). 인접 규범 전수 grep 에서 "작업 중 진행분 커밋 적재" 규범 = 0-hit [verified — Story §4.3 d].

**명명**: ADR-071:1237 의 "lane 경계 checkpoint 금지" (정지점 의미) 와의 동음이의를 피해, 본 ADR 의 용어는 **진행 커밋(progress-commit)** = "작업 중 의미 단위 경계마다의 진행 산출물 선행 적재" 로 한다. `checkpoint` 단독 사용을 회피한다.

## 결정

<!-- progress-commit-normative-region:start -->

### §결정 1 — 정의역: 종료-원인 불문 + 축 C 한정

본 규범의 문제 정식화: *"`termination_cause=timeout` 인 spawn 에서 `outcome` 이 `failure`(전량 소실)로 붕괴하지 않고 `partial`(부분 회수)로 착지하도록, 종료 **이전** 시점에 산출물을 durable 착지면으로 미리 옮기는 규율."* (기존 spawn-event-v1 어휘 재사용 — 신규 enum·계약 채널 신설 0.)

정의역 = **종료 원인 불문**. 사전 선행 적재는 종료 원인과 독립으로 성립하므로 (사용자 sign-off 골격 ②) 규범 본체(§결정 2)는 전 원인 공통이다. 종료 유형별 분류 (`termination_cause` enum 전수 — 신규 어휘 없음):

| termination_cause | 본 규범(사전 적재) | 사후 회수 절차(§결정 5) | 비고 |
|---|---|---|---|
| `timeout` | 포함 (주 대상) | 발동 | 세션 한도 = budget/credit-exhaustion 통합 상위 [spawn-event-v1:94]. context limit·tool timeout 도 이 값 공간 |
| `error` | 포함 | 발동 | crash·API error 계열 |
| `cancelled` | 포함 | 발동 (재개자가 취소 의도 확인 후 salvage 여부 판정) | user abort — 사전 적재분은 이미 durable |
| `zero_output` | 포함 | 발동 (산출 0 의 분해 검증 — 파일 미생성 vs 미커밋 vs 미보고) | G-2 분해의 관측 입력 |
| `normal` | 포함 (작업 중 규율은 동일) | **비발동** — 정상 return 경로 = playbook §3.5 step 3 기존 규약 소관 | 추후 재분류 대상 0 |

축 경계: 축 A (정지 적법성 — ADR-025/109/141, CFP-2944) 와 축 B (liveness·재개 — ADR-139/170 §19·20, CFP-2946) 는 무접촉. 본 ADR 은 축 C 의 **산출물 보존 sub-axis** 만 신설한다 (재개 sub-axis = ADR-110·ADR-071 §결정 24 기존 소관).

### §결정 2 — 규범 본체: 작업 중 상시 선행 적재 (워커 자기-적재)

1. **보존 최소 인정 단위 = local git commit (P0).** working tree·stash·scratch 파일·최종 메시지는 보존 단위로 인정하지 않는다 (stash = push 불가, scratch = TTL 회수, 최종 메시지 = durability 0). 보존 단위의 정의는 이 한 줄이 SSOT 다.
2. **시점 = atomic 의미 단위 경계** (시간 주기 아님). 운영 가능 표현 (택1 이상 충족 시 1회): (a) 파일군 1개 완결 — 한 관심사의 파일 집합이 서로 모순 없는 상태 도달 (b) AC 1개 대응분 완결 (c) 조사 축 1개 결론 확정 (D2 계열은 §결정 4 cheap tier 로 수행).
3. **주체 = 산출 주체 자신 (워커 자기-적재).** 한도 도달은 lead 포함 tree 동시 사망일 수 있어 (2026-08-13 13개 동시 [verified]) Orchestrator-사후수습 모델이 불성립하고, Orchestrator inline 대행은 ADR-039 whitelist 밖이다. 실행 형태는 워크스페이스 조건에 따라 분기한다:
   - **(가) 자기 sub-worktree 보유 워커** → 직접 `git -C <자기 worktree 절대경로> add -A -- <경로> && git -C <...> commit` — **단일 Bash 호출 1회** (add/commit/status 분리 호출 금지 — 훅 체인 세금이 호출 수만큼 배증). 사전 `git status` 확인 호출 금지 — 무변경 판정은 커밋 실패로 대신한다.
   - **(나) checkout 공유 워커** (sub-worktree 부재 시 자동 적용) → 워커는 **자기 전용 파일에 Write (cheap tier, §결정 4)** 로 자기-적재하고, 커밋 승격은 lane PL 이 배치 수행한다 (index.lock 경합 0 — 커밋 주체 1인화). durability 를 발생시키는 행위(파일 write)는 여전히 워커 자신의 것이므로 자기-적재 원칙은 훼손되지 않는다 — 배치 커밋은 tier 승격이지 보존의 필요조건이 아니다.
4. **self-consistent 조건 (생산 시 상태 조건)**: 각 진행 커밋은 의미 단위 완결 상태 — 그 커밋만 회수해도 내적 모순이 없는 상태 — 여야 한다. half-written 상태의 커밋은 "보존된 쓰레기" 다 (소비 시 취급은 §결정 5 inconclusive 규약이 담당 — 생산/소비 이원 규정).
5. **무변경 커밋 = 정상**: 변경 0 상태에서 `git commit` 은 실패(비-0 exit)하며, 이 실패는 정상이고 보존 미충족이 아니다. `|| true` 로 삼키는 것도 금지한다 (성공/무변경/실패가 구분 불가해져 보존 연극이 된다).
6. **물리 위치**: worktree-first (ADR-040) — 모든 git 호출은 `git -C <worktree 절대경로>` 로 결박한다 (harness 의 bash 호출 간 cwd reset 으로 인한 오착지 방지 — 기존 directive 재인용).

### §결정 3 — 내구 계층 P0/P1/P2 + 강등 규칙 + PUBLIC repo 비가역 축

| tier | 판정 술어 | 달성 조건 |
|---|---|---|
| **P0 durable-local** | 호스트 생존 시 회수 가능 | local commit (또는 `.git` 보유) — **default 판정선** |
| **P1 durable-remote** | 호스트 소실에도 회수 가능 | origin push — **opt-in** (아래 3조건) |
| **P2 landable** | 리뷰·머지 경로 위 | PR 반영 브랜치 또는 Story file — 보존 축이 아닌 반영 축 |

1. **강등 규칙 (tier-downgrade)**: 하위 tier 성공은 상위 tier 실패에 의해 취소되지 않는다. P1(push) 시도가 실패해도 P0(local commit) 이 잔존하면 **보존 성공**이다. 근거: push 거부는 원격 측 거부이며 로컬 저장소 상태를 변경하지 않는다 [source: git-push(1) — https://git-scm.com/docs/git-push].
2. **복구 조작 금지 (강등 규칙의 필수 짝)**: push 거부 시 `git pull --rebase` · `git reset` · `git push --force`(및 `--force-with-lease`) 를 시도하지 않는다. 실패 시 요구되는 행위는 **기록 후 작업 계속**뿐이다. P0 를 파괴할 수 있는 유일한 현실 경로가 "push 실패를 고치려는 복구 조작"이며, 이 금지 없이 강등 규칙만 두면 규범이 보존을 위해 파괴를 유도한다. rebase 는 SHA 를 바꿔 re-push 멱등성도 깨뜨린다.
3. **push 재시도 상한**: transient (네트워크·DNS·TLS) = ≤1회 즉시 재시도 (backoff 루프 금지) / non-fast-forward·ref 거부 = 0회 / 인증·권한 거부 = 0회. 분류는 원격 응답으로 판정한다 (추측 금지). 이 재시도는 ADR-109 판별식 D·R1 사다리와 **무관한 별도 축**이다 (§결정 7).
4. **P1 승격 3조건 (전건 충족 시만)**: (a) 내용 목적지 일치 — 어차피 공개 PR 로 갈 내용 (b) secret 선행 배제 — §결정 6 판정 1회 통과분만 (c) repo 라우팅 — D2(분석·조사 텍스트)의 P1 은 PRIVATE repo(internal-docs)로, PUBLIC wrapper 로의 P1 은 D1(코드·문서 diff) 한정. 근거: `plugin-codeforge` = **PUBLIC** [verified — `isPrivate:false` 실측] 이므로 P1 오적재 = **비가역 공개 게시** — 브랜치 삭제·히스토리 수정 후에도 커밋은 SHA·fork·PR 참조로 잔존한다 [source: GitHub Docs — Removing sensitive data from a repository]. 노출 시 1순위 처방 = 자격 회전(revoke/rotate).
5. **ephemeral 환경 경계조건**: P0 의 전제 = 산출 주체와 동일한 호스트의 영속 파일시스템이 프로세스보다 오래 산다는 것. 실행 환경이 ephemeral(컨테이너 러너·remote 격리 세션 등)이면 프로세스 사망과 파일시스템 소멸이 동시에 일어나 P0 가 0 으로 붕괴하며, 그 정의역에서는 **P1 이 최소 tier** 가 된다 (visibility 라우팅 (c) 는 동일 적용).

### §결정 4 — D2(분석·조사 텍스트) 처분: 2-speed 적재

최대 소실원 = D2 (분석·조사 텍스트 — 현행 착지면 구조적 부재, INV-D2). 보존 경로를 다음과 같이 정의한다:

| tier | 수단 | 도달 내구 | 용도 |
|---|---|---|---|
| **cheap (상시)** | `Write`/`Edit` — 워커 전용 파일 append (파일-per-워커: `<story>-<agent>.md` 형식, 공유 파일 직접 편집 금지) | working-tree dirty = 호스트 생존 시 잔존 + ADR-169 GC 구조적 면제 (dirty = 보존 트리거) | D2 분석 텍스트·중간 결론 — Bash 훅 체인 세금 0 |
| **commit (배치)** | Bash 단일 호출 (§결정 2-3) | P0 durable-local | 의미 단위 경계 |

1. cheap tier 는 **durability 만 사는 tier** 다 — 커밋 원자성 없음 (self-consistent 조건은 commit tier 에만 적용) + landability 는 경로에 의존. 정직 명명을 유지한다.
2. **landable 승격 경로 (기존 2면 — 신규 경로 신설 기각)**: (i) internal-docs 의 `.claude-work/doc-queue/<story>-<agent>.md` 는 `.gitignore` 비대상 [verified — check-ignore rc=1 실측] 이므로 lane PL 배치 커밋으로 P0·landable 동시 승격 가능 (ii) wrapper repo 의 `.claude-work/` 는 gitignore 대상 — durability-only 로 정직 잔존하고, landable 필요분은 정식 문서 경로(Change Plan·Story owned 섹션·retros)로 옮겨 커밋한다. `.gitignore` 배제면은 본 규범의 상위다 — 보존을 이유로 한 `git add -f`·경로 우회를 금지한다 (§결정 6-3).
3. 커버 불가 영역이 남으면 검토 후보·기각 사유를 동반해 선언한다 — 본 절의 검토 이력: 신규 landable 경로(`work-logs/` 계열) 신설 = **기각** (사유: internal-docs doc-queue 가 이미 trackable 하여 이득 중복 + 신규 doc type = doc-locations row·잔재 축 확대 비용).

### §결정 5 — 발견·인계: reachability 채널 + 미완 표식 + 병렬 집계

durability 단독으로는 회수가 보장되지 않는다 ("커밋은 됐는데 아무도 그 브랜치를 모른다" — F8). 발견 채널과 인계 프로토콜을 규범의 일부로 동반한다.

1. **발견 채널 (최소 1개 의무 — 3중)**: ① **브랜치 네임스페이스** — 진행 커밋은 기존 값공간 `cfp-NNN[-slug]` / `cfp-NNN/<lane>/<sub>` 브랜치 위에만 적재한다 (신규 명명 확장 금지 — 값공간 폐쇄가 곧 통제). 신규 세션 재개자(전원 공멸 케이스)는 Story KEY 만으로 `git for-each-ref --sort=-committerdate 'refs/heads/cfp-NNN*'` 전 열거 가능 ② 잔재 발견 스캐너의 `dirty`·`unpushed-N` 술어 [verified — check_workspace_residue_discovery.py:99] ③ ADR-172 세션-독립 스케줄 관측 (전원 공멸 후에도 도는 유일 축).
2. **미완 표식 규약 (리터럴)**: 진행 커밋의 subject = `[CFP-NNN][WIP] <의미 단위 요약 1줄>` — **`[WIP]` 토큰이 미완 표식**이며, 잔여 작업은 본문 1줄 `Remaining: <추상 요약>` 로 기록한다 (값공간 = §결정 6-4 폐쇄 집합). 의미 단위가 최종 완결된 커밋만 `[WIP]` 를 제거한다.
3. **inconclusive 취급 (소비 시)**: 후속 주체가 진행 커밋 부분 산출물을 소비할 때 그것은 **inconclusive** 로 취급한다 — PASS·완료로 자동 승격 금지 (ADR-170 §결정 20 INV-L2 정합). `[WIP]` 표식 존재 = inconclusive 의 기계 앵커.
4. **인계 프로토콜 (3-step runbook — 세션 사망 후)**: step 1 **census** — 해당 Story 브랜치·worktree 에서 `git -C <wt> log --oneline @{u}..` + 스캐너 술어로 미push 커밋·dirty 파일 열거 / step 2 **무결성 판정** — 각 진행 커밋을 inconclusive 로 전제하고 `[WIP]` 표식·자기서술 메시지로 판정 / step 3 **인계** — fresh 재스폰 packet 에 (브랜치명 · 마지막 진행 커밋 SHA · 미완 표식 요약) 3-tuple 주입 (ADR-141 Amd6 fresh-spawn only 정합 — SendMessage resume 금지 경로와 무충돌). ADR-110 이 재개한 신규 세션이 이 runbook 의 "신규 세션 재개자" 실현체다. 절차 pointer 1줄을 `skills/session-recovery/SKILL.md` 에 두는 배선 = Phase 2 (현행 스킬에 salvage·미커밋 절차 0-hit [verified — firsthand grep]).
5. **병렬 워커 집계 (identity · ordering · 충돌해소)**: identity = 브랜치 네임스페이스 + 커밋 trailer `Agent: <agent_type>` (roster 실명 verbatim) / ordering = committerdate / 충돌해소 = 자동 병합 금지 (Story Non-goal) — lane PL 또는 재개자의 판정 사항. 워커별 브랜치·파일-per-워커 네임스페이스가 중복 없는 식별의 1차 기구다.
6. **lead 집계 정합**: lead 생존 케이스의 통지 라우팅은 ADR-170 §결정 19 소관이며 본 규범은 그것과 모순 없이 결합한다 — 워커의 진행 커밋 SHA·`[WIP]` 상태는 lead 가 능동 모니터로 집계 가능한 git 관측 사실이고, 통지 채널 신설·변경은 0 이다. lead 동시 사망 케이스는 본 §결정 5-1/5-4 의 재개자 경로가 담당한다 (ADR-170 §19 정의역 밖 — "이미 커버" 오귀속 금지).

### §결정 6 — secret 예외: span 단위 배제 + 마스킹 1급 + 메시지 값공간 폐쇄

1. **span 단위 원칙**: 보존 의무의 예외는 "secret 포함 산출물 전체" 가 아니라 **secret 포함 구간(span)** 이다. 전량 배제 규정은 보존 압력 하에서 "그냥 커밋" 을 실무 기본값으로 만들어 착지 확률을 오히려 높인다 (배제 규범의 역설). **마스킹 후 적재가 1급 경로**다 — span 마스킹(`***REDACTED***`)·파일 분리 후 나머지를 적재한다.
2. **표면별 비대칭 default**: S-A 커밋 내용 = span 제외·마스킹 / S-B 커밋 메시지 = 추상화 (아래 4) / S-C 브랜치명 = 값공간 폐쇄 (`cfp-NNN[-slug]` — 확장 금지) / S-D tier = P0 유지 + P1 조건부 (§결정 3-4 — P1 승격 precondition = 본 절 판정 1회, P0 는 불요: 통제를 비가역 경계에만 배치).
3. **우회 금지**: `.gitignore` 배제면은 본 규범의 상위다 — 보존을 이유로 한 `git add -f`·경로 우회를 금지한다. D2 보존 경로는 추적면 위에서만 성립한다 (§결정 4-2).
4. **커밋 메시지 값공간 폐쇄**: Story key + lane·agent_type (roster enum) + 의미 단위 요약 1줄 (추상) + 미완 표식(`[WIP]`). 금지 = 절대경로 · session_uuid 원문 · 한도 신호 원문 · org_id (redaction 분류 = ADR-109 §결정 10 matrix 그대로 상속 — 신규 분류표 0).
5. **정직 한계**: GitHub push protection 은 provider secret 패턴 검출기이며 절대경로·내부 식별자·한도 신호 커버는 미확인이다 — 커버를 가정한 설계를 금지한다. 완화 전건 = 저작 규율 (기계 강제 0).

### §결정 7 — negative control: 진행 커밋은 정지 사유가 아니다 (zero-notice 가정)

1. **진행 커밋은 정지 사유가 아니다.** 진행 커밋을 이유로 작업을 멈추거나 보류하는 행위는 본 규범이 요구하는 바가 아니며, 한도 신호를 진행 커밋의 trigger 로 삼는 규범 문면을 두지 않는다 — 그런 문면은 ADR-025 `limit-signal-halt` form fence 의 뒷문 재도입이다. 진행 커밋 trigger 는 ADR-109 판별식 D 와 disjoint 하다 (신호-무관 상시 규범).
2. **zero-notice 가정**: 본 규범은 종료 시점에 수행되는 어떤 행위도 요구하지 않는다. 종료 통지·유예 창의 존재를 규범 성립 조건으로 삼지 않으며, 그런 창이 없다는 가정(zero-notice) 위에서 완전하게 성립한다. 근거: 한도류 종료의 관측 경로(StopFailure)는 문서화되어 있으나 **observe-only** ("Output and exit code are ignored" [source: https://code.claude.com/docs/en/hooks]) 라 저장 기회가 없고, 훅은 에이전트에게 도구를 실행시킬 수 없다.
3. **future-work (opportunistic 보조 경로)**: 유예 창의 실재가 후일 실측되면, 발화 시 이득만 있고 미발화 시 규범 미충족이 되지 않는 opportunistic 보조 경로를 additive 로 추가할 수 있다. 그 경로는 primary(사전 상시 적재)를 대체하지 못한다.
4. **재시도 실패의 귀결 = 기록 후 계속** — 규범 문면에 "실패 시 중단·보류" 어휘를 두지 않는다.

**금지 form 인용 (본 인용 절에 한정 — lint 정의역 밖)**: 다음 형태의 조항은 본 ADR 어디에도 규범으로 존재하지 않으며, 발견 시 위반이다.

<!-- forbidden-form-quotation:start -->
> ① "한도 임박 시 커밋 (후 정지)" 형 — 한도 신호를 trigger 로 결박 = `limit-signal-halt` 재도입 + ADR-109 축 혼선. ② "커밋 후 정지" 형 — 정지 선택지화 = ADR-025 whitelist 간접 확대. ③ "한도 신호 수신 시 저장" 형 — 반응형 의존 = zero-notice 위반 (신호 도착은 보장되지 않음). ④ "종료 시점에 저장한다" 형 — 종료-시점 의존 조항 = F4 born-broken (in-flight 즉사 구간에서 정의 불가).
>
> **closed-set 금지 토큰 배열 (본 배열 = Phase 2 lint 의 SSOT — 검사 정의역은 이 리터럴 4개가 전부이며 의미 기반 확장 금지)**:
>
> ```
> FORBIDDEN_TOKENS = [
>     "한도 임박 시 커밋",      # ①형
>     "커밋 후 정지",           # ②형
>     "한도 신호 수신 시 저장",  # ③형
>     "종료 시점에 저장한다",    # ④형
> ]
> ```
<!-- forbidden-form-quotation:end -->

Phase 2 lint 계약: 위 `FORBIDDEN_TOKENS` 배열(closed set 4 리터럴)의 부재 검사 정의역 = `progress-commit-normative-region` 마커 내부 **−** `forbidden-form-quotation` 마커 블록 (인용 절·배열 박제 자체 = 정의역 제외 — self-RED 함정 회피. 제외 규칙의 마커명 = `forbidden-form-quotation` 로 본 절에 고정). 정의역 내 4 토큰 출현 = **0 [실측 — 본 커밋 시점 grep: 전 출현이 quotation 블록 내부]**. closed set 밖 자연어 회피 표현은 미검출 — "기계적으로 봉인된다" 는 주장을 금지한다.

### §결정 8 — advisory ceiling 정직 라벨 + 권한 선언면 판정

1. **tier = advisory (ceiling).** 본 규범의 준수는 저작 규율이며, 규범 문구 presence 는 prompt-mandate (grep testable) 이나 실준수는 비-PR-enforceable 이다.
2. 근거 3층: (a) **경로 불일치** — 한도류 종료 경로(StopFailure)는 observe-only 라 저장-유발 lever 부재 (b) **자체 정책** — ADR-115 "block 금지 + exit 0" 이 hook 강제 lever 화를 이미 금지 (c) **권한 선언면 비집행** — agent frontmatter allow 선언은 `defaultMode: bypassPermissions` 하에서 discipline SSOT 일 뿐 gate 가 아니다 [verified — ADR-099:352]. "100% 기계강제" · "hard-gate" 를 표방하는 서술을 금지한다 (ADR-141 Amd7 · ADR-143 동형). "규범 도입 = 소실 0" over-claim 도 금지한다 — 마지막 의미 단위 경계 이후분은 구조적으로 미완충이다.
3. **권한 선언면 판정 (P6 갈림길 — 무판정 통과 금지 의무의 이행)**: **판정 = 41 agent 파일 `git commit` allow 선언 추가 기각 + 무접촉, non-bypass consumer 환경은 disclosed residual 로 명시 선언.** 근거: 선언면은 비집행이라 (위 (c)) 선언 추가 = 집행력 0 인 drift 표면 41개 신설이고, 현행 wrapper 실행 환경(`defaultMode: bypassPermissions` [verified — ADR-099:352])에서는 현행 그대로 작동한다. **disclosed residual (폭 정직 확대)**: Write/Edit 도 Bash 와 동일한 권한 선언 표면이다 (agent allow 선언에 `Write(...)` 패턴 실재 [verified — plugins/codeforge-test/agents/IntegrationTestAgent.md 의 `Write(tests/integration/**)`]) — non-bypass consumer 세션에서는 commit tier(Bash)뿐 아니라 **cheap tier(Write, §결정 4)도 영향권일 수 있고**, 그 환경에서의 Write 실동작 = [fact-check-pending]. 따라서 "최소 보존 경로 잔존" 주장의 근거는 **현행 wrapper bypassPermissions 실측에 한정**하며, non-bypass consumer 의 보존 경로 성립 여부와 해소는 consumer overlay 의 권한 정책 소관으로 명시 이관한다. 이 residual 은 결함 은폐가 아니라 정직 선언이다.
4. Phase 2 에서 본 라벨을 `scripts/check-tier-honesty.py` lever REGISTRY 에 1행 등재한다 (Axis1 라벨 presence + Axis2 enforcement 토큰 금지 — 기존 mutation oracle 로 AC-11 기계 커버).

### §결정 9 — 비용 계상: latency ⊥ quota 2축 분리 + 빈도 상한

1. **2축 분리 의무**: 진행 커밋 1회의 비용은 축이 다르다 —
   | 축 | marginal | 측정 상태 |
   |---|---|---|
   | latency (지연 예산) | 훅 체인 1회 ≈ **2,106.1 ms** (after median) | [empirical-source: tests/perf/reports/cfp2965-comparison.md:53 — **Defender ON 조건부** (:161), 인용 시 조건 표기 의무] |
   | usage quota (한도 예산) | 도구 호출 + 결과 텍스트 수십~수백 토큰 | 미측정 — 경과 wall-clock 자체가 한도를 소비한다는 문서 근거 부재 [source: support.claude.com/en/articles/14552983 + 11647753. 5시간 창의 측정 기준 명시 문면 = 미발견 — 단정 금지] |
   "진행 커밋이 한도 소진을 가속한다" 는 단정을 금지한다 — 인과 (지연세→한도 소진) 는 [hypothesis] 유지 (CFP-2965 self-declare 상속).
2. **잠식 정량 (latency 축)**: 현실적 진행 커밋 수(Story 당 20~75회)는 CFP-2965 감축 이득의 **13~28 % 를 잠식** (손익분기 N = 179~374 의 11~42 % 구간) [empirical-source: dev-process-event 원장 183,767 rows B_est 실측 — story_key 귀속률 12 % 라 하한(보수적·과대추정 방향), CFP-2966 CP §7.4 인용]. 자기잠식(F3)은 실재하되 부분적·정량 유계다.
3. **빈도 상한**: `N ≤ 0.357 × B` 는 [hypothesis — empirical-source: TBD, 원장 story_key 귀속률 개선 후 재산출. 확정값 lock-in 금지]. 참고 상한(규범 아님) = 워커당 커밋 ≤ Bash 호출/10 — 초과는 금지가 아니라 재검토 신호.
4. **비용 규율 2건**: 진행 커밋 1회 = 단일 Bash 호출 1회 (§결정 2-3 — 분리 호출 = 세금 2~3배) / "이미 발생하는 커밋에 규율 부여 (시점 앞당김)" 문구의 정의역 = D1 계열 lane 한정 — D2 계열은 커밋 표면 0 이라 신규 호출이 실제 추가되므로 §결정 4 non-Bash 경로로 우회한다. "비용 중립" 은 방향 목표이지 보장 아님.
5. 부수 이득 (Consequences 계상): 빈도를 의미 단위로 정의한 선택이 clock-sync 축(타이머 신뢰성·세션 간 시각원)을 구조적으로 소거한다 — 시간 주기형이었다면 §7.4.3 대상이 됐다.

### §결정 10 — 관할 경계: ADR-169 / ADR-040 / ADR-039 (GC 가 진행 커밋을 회수하지 않는 조건)

1. **ADR-169 (잔재 수명 규약)**: 진행 커밋·dirty 파일은 ADR-169 §결정 3 의 보존 트리거 (dirty / unpushed) 에 정확히 해당하여 **GC 구조적 면제** 대상이다 — GC 가 진행 커밋을 회수하지 않는 조건 = "미push 커밋 또는 dirty 상태 보유" (`.git` 보유 항목 purge 제외 = §결정 6 INV-1 동일). 미머지 진행 커밋 브랜치의 누적(F6)은 ADR-169 §결정 7 가시화 + aging 이 흡수 경로다 — 본 ADR 은 수명 규범을 신설하지 않고 그 경로를 인용한다.
2. **ADR-040 (worktree)**: 물리 위치 = worktree-first (§결정 2-6), sequential merge (§결정 3) 무손상 — 본 규범은 커밋 시점만 다루고 merge 순서를 건드리지 않는다. §7.K 완료-게이트의 정의역 = "완료 Story" 이므로 미완 진행 커밋은 애초 그 정의역 밖이다 (경계 cross-ref — 확장 아님).
3. **ADR-039**: 커밋 주체 = agent 소유 (§결정 2-3) — Orchestrator inline 대행 금지의 재확인.

### §결정 11 — 관측층: git census (기존 표면 재사용 — 신규 채널 0)

1. **채택 = (c′) git census.** 진행 커밋은 정의상 커밋이므로 자기 기록적(self-recording)이다 — 관측면 = git 자체 + 기존 술어 (`dirty`·`unpushed-N`) + ADR-172 세션-독립 스케줄 관측. 신규 이벤트 채널·신규 표면 = 0.
2. **기각 2건 (근거 명시)**: (a) stop-event-v1 필드 확장 — 계약 = 18-field Allow-list ONLY, 추가 field = BREAKING (ADR-163 §결정 2 + ADR-043 §결정 2 이중 amendment 의무) 이며 런타임은 `outcome` 을 한 번도 기록한 적 없다 (0/15,398 [empirical-source: `.claude/ledger/stop-event.jsonl` 원장 전수 스캔 — InfraOp deputy firsthand, 2026-08-15]). "재사용 = 신규 표면 0" 은 거짓 — write-path 신규 구현 + 선언된 3-way drift 정합 판정을 동반한다. (b) StopFailure record-only hooks.json entry — 현행 0 entry [verified] 이고, 답하는 질문("세션이 죽었나")이 보존 질문("무엇이 남았나")과 오정렬이며, 신설 시 ADR-115 Amd2 3규칙 판정 비용을 동반한다. 지금 신설하지 않는 것이 그 판정 비용도 회피한다.
3. **계약 상속**: 관측 산출 = `선언값 · 실측값 · 불일치` 사실 3-tuple — `PASS`/`FAIL`/`OK` 등 verdict 어휘 금지, 주 트리거·required 승격은 ADR-169 §결정 4 판례 재검토 선행 (ADR-172 §결정 1·7 그대로 상속). 관측층은 **사후 발견** 층이며 소실 창 축소 기여 = 0 이다 — "예방" 프레이밍을 금지한다.
4. 보조층 (조건부): dev-process-event-v1 `final_artifact` (closed enum 기존 원소) — 단 Port-B emit = Orchestrator(-owned delegate) 독점이라 생존자가 있을 때만 발화 가능. 동시 전멸 시 무발화 = 정직 한계로 명기하고 보존 판정의 근거로 삼지 않는다.

### §결정 12 — 전파 채널: 다층 (Phase 1/2 분배)

| 채널 | 판정 | Phase | 근거 |
|---|---|---|---|
| 본 ADR (SSOT) + Story §3/§7 + Change Plan | 채택 | **1** | 규범 문면의 단일 원본 |
| CLAUDE.md `## 작업 규칙` bullet 1줄 | 채택 | 2 | Orchestrator 매턴 자기검열면 (ADR-169 인용 형식 동형). CFP-2944 Phase 2 와 편집면 인접 — 선착 순서 확인 후 additive |
| playbook §3.5 step 3 정정 | 채택 | 2 | I-3 공백의 문면 위치 직접 수정 — "return 후 커밋" 에 "작업 중 의미 단위 경계 progress-commit (ADR-178)" 병기 |
| SubagentStart hooks.json **2번째 entry** (신규 스크립트, pointer-only priming) | 채택 (조건부) | 2 | 서브에이전트·consumer 세션 도달 유일 축 (ADR-143 선례). 기존 `subagent-start-render-discipline` 스크립트는 one-channel rule marker 보유 [verified — :26-27] 라 **스크립트 통합 기각** — 별도 entry 로 관심사 분리. 신설 시 ADR-115 Amd2 3규칙 (timeout 하한 불변식·fail-open 계상·차등 tier) 판정 동반 의무 + 절차 0줄 pointer-only (ADR-172 §결정 2 동형) |
| spawn packet prose (lane PL 저작) | 채택 | 2 (저작 규율) | 커밋 표면 0 인 lane (요구사항 등) 의 유일 작동형 |
| 41 agent 파일 개별 pointer | **기각** | — | shared-base 편집 = INEFFECTIVE [verified — ADR-143:219] + 38+3 파일 개별 수정 = drift 표면 신설 |

기계 검사 (Phase 2): negative-control presence lint = 기존 `orchestrator-autonomy-stop-taxonomy-check.yml` 에 step 추가 (신규 workflow 0, `continue-on-error: true` — warning-first, 8-tuple 무변경) + check-tier-honesty registry 1행 (§결정 8-4). blocking 계열로 태어나는 entry 는 없다 (ADR-171 §결정 5).

### §결정 13 — 인접 작업 경계 (later-lands-reconciles)

- **CFP-2946 (살아있는 에이전트 재개, 축 B)**: 본 ADR 과 disjoint — 그쪽 처방(SendMessage force-resume)은 수신자 생존 시만 정의되고, 본 규범 처방(사전 적재 + 사후 발견)은 생존자에게 불필요하다. 단 CFP-2946 Story 착지본은 본 설계 시점 부재 [verified — internal-docs origin/main 재대조 불가 지속] — **CFP-2946 설계가 "중간 산출 상태 보존/재주입" 을 비용 절감 수단으로 채택하는 경우, 그쪽 설계 lane 이 본 ADR 과의 경계를 재대조할 의무를 진다** (later-lands-reconciles).
- **CFP-2944 (축 A)**: 전제 — 본 ADR 은 그 결정 위의 상보 축 (창의 시작·길이는 불변, 창 안에서 잃는 양을 줄임). 침범 금지선 = §결정 7.
- **ADR-110 / ADR-071 §결정 24 (축 C 재개 sub-axis)**: disjoint cross-ref — 세션 부활 vs 산출물 잔존. 접점은 §결정 5-4 (재개 세션 = runbook 실현체) 뿐이다.

<!-- progress-commit-normative-region:end -->

## 결과 (Consequences)

**긍정**: ① 강제 종료 창 안에서 잃는 양이 "마지막 의미 단위 경계 이후분" 으로 유계화 ② 발견 채널 동반으로 durability 가 reachability 로 이어짐 (F8 차단) ③ 의미 단위 빈도 채택이 clock 축을 구조적으로 소거 (§결정 9-5) ④ git census 의 자기 기록성 — 신규 관측 표면 0.

**부정·잔여 위험 (정직 표기)**: ① advisory ceiling — 마지막 의미 단위 경계 이후분 = 구조적 미완충, 준수는 기계 강제되지 않음 ② latency 잠식 13~28 % [empirical-source: §결정 9-2] — CFP-2965 이득의 부분 소비 ③ closed-set 금지 토큰 검사는 자연어 회피 표현에 우회 가능 ④ 미머지 브랜치 누적 (F6) — ADR-169 §결정 7 흡수 경로 의존 ⑤ non-bypass consumer 세션의 commit tier(Bash)·cheap tier(Write) 영향권 = disclosed residual (§결정 8-3 — Write 도 동일 선언 표면, 실동작 [fact-check-pending]) ⑥ 호스트 소실 시나리오는 in-repo 사례 기록 0 [fact-check-pending 승계] — P1 조건부 판단은 그 저빈도 가정 위 ⑦ SubagentStop 의 한도-경로 발화 여부 = 미해소 잔존 — 본 규범은 전 조항이 그 답에 의존하지 않도록 구성됨 (zero-notice 완결).

## 해소 기준

N/A — permanent policy (is_transitional: false). future-work 재개 조건: §결정 7-3 (유예 창 실측 시 opportunistic 보조 경로 additive) / §결정 9-3 (B 실측 후 빈도 상한 재산출).

## 관련 파일

- `docs/orchestrator-playbook.md` — §3.5 step 3: I-3 (커밋 트리거 return 종속) 공백의 문면 위치, Phase 2 정정 대상 (실측 앵커 = :1296 [worktree 8eeda0aa2 기준 — Story 저작 기준 ecfe62d63 에서도 :1296. 구 표기 :1286 = 저작 시점 표기 오류])
- `hooks/hooks.json` — SubagentStart 채널: Phase 2 priming 2번째 entry 후보 (ADR-115 Amd2 3규칙 판정 동반, §결정 12)
- `skills/session-recovery/SKILL.md` — 축 C 회수 3-step runbook pointer 착지 대상 (Phase 2) — 현행 salvage·미커밋 관련 0-hit (§결정 5-4)
- `scripts/lib/check_workspace_residue_discovery.py` — 발견 술어 `dirty|unpushed-N` (§결정 5-1 / §결정 11 git census 기존 표면)
- `scripts/check-tier-honesty.py` — Phase 2 lever REGISTRY 1행 등재 대상 (AC-11 기계 커버, §결정 8-4)
