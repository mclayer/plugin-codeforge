---
adr_number: 164
title: Parallel-branch liveness heartbeat + external watchdog (new-sibling, non-amendment)
date: 2026-07-20
status: Active
category: orchestration-discipline
carrier_story: CFP-2772
supersedes: null
amends: null  # new-sibling — dev-process-event-v1 / jira-progress-mirror(Arc B) 무변경 (§결정 1 non-amendment 판정). 기존 계약 supersede 0.
related_adrs:
  - ADR-139  # background-wait liveness gate — 가장 가까운 선행. liveness ⊥ granularity / INV-L1(max-wait 상한)·INV-L2(fail-open 금지 stall≠PASS)·detection≠recovery·INV-L4(observer=lead 고정). 본 ADR 은 observer-death 케이스로 확장(외부 관측자)
  - ADR-155  # dev-process observability substrate — heartbeat 가 재사용하는 CODE/PATTERN(agent-emit 스타일·2-layer local-SoT+projection)의 출처. 단 SCHEMA 는 미접촉(§결정 1)
  - ADR-163  # measurement channel architecture — dev-process = 9th Tier-3 channel. event_type/필드 추가 = amendment 의무. 본 ADR 은 그 amendment 를 유발하지 않음(non-amendment)
  - ADR-043  # telemetry privacy — capture-time redaction floor(14 rule) 상속. heartbeat egress 도 우회 불가(AC-8)
  - ADR-099  # atlassian allow redefinition — Jira write = addCommentToJiraIssue 1종 narrow-allow. per-branch=코멘트 본문(createJiraIssue deny 회피), watchdog verdict=GitHub(Jira-write 미신설) → §A1-1 무약화(AC-11)
  - ADR-100  # confluence/jira doc SSOT recognition — control project 코멘트 채널 정합
  - ADR-115  # runtime hook enforcement — record-only·non-blocking·exit0 상속(AC-8)
  - ADR-038  # progress visualization — jira-progress-mirror Arc B 확장 대상. 6-point marker ≠ liveness(ADR-139 재확인)
  - ADR-157  # infra-resource-manifest drift gate — watchdog credential/workflow = infra-resource-baseline.yaml 선언 의무(미선언 = fail-closed FAIL)
  - ADR-119  # research-before-claims — 정직 천장(임계·seq 결정론 over-claim 금지 / 무증거 안전 단정 금지 / 필요성 게이트)
  - ADR-127  # 정식 full 10-lane + Phase 1/2 PR 분리 무조건
related_stories:
  - CFP-2772
related_cfps:
  - CFP-2772  # carrier — 병렬 에이전트 stale 감지(coarse per-branch heartbeat + 외부 watchdog)
  - CFP-2687  # ADR-155 dev-process substrate carrier (CODE/PATTERN 재사용 출처)
  - CFP-2285  # jira-progress-mirror(Arc B) carrier — 확장 대상
  - CFP-2700  # infra-resource-manifest drift gate carrier — watchdog credential 선언 의무 근거
related_files:
  - docs/change-plans/cfp-2772-parallel-branch-heartbeat-watchdog.md  # internal-docs SSOT (ADR-013 dogfood-out) — 실 설계 상세
  - skills/jira-progress-mirror/SKILL.md  # Arc B-2 heartbeat relay 확장 대상(Phase 2)
  - scripts/jira-channel/deny-scan.sh  # egress backstop 재사용(PII gap 주의 — §결정 6)
  - scripts/jira-channel/echo-guard.sh  # sentinel SSOT(⟦cf-orch⟧) 재사용 — HEARTBEAT 토큰 신설
  - scripts/jira-channel/progress-format.sh  # heartbeat-format.sh 형제 선례
  - .github/workflows/confluence-forward-sync.yml  # watchdog credential 패턴 선례(Atlassian token as GH secret / secret-absent=dry-run / continue-on-error / ubuntu-latest)
  - docs/infra-resource-baseline.yaml  # watchdog workflow + credential 선언 대상(Phase 2 — ADR-157 drift gate)
  - docs/architecture/codeforge-family.md  # boundary + data_flow 갱신(경계 Y / 데이터흐름 Y)
is_transitional: false
mechanical_enforcement_actions: []  # Phase 1 = 설계 SSOT. 실 emit/watchdog/format/workflow 배선 + lint/self-test + AC-7 discriminating fixture = Phase 2(본 Story §8-§11). ADR-082 §결정 6 retain pattern.
---

# ADR-164: Parallel-branch liveness heartbeat + external watchdog (new-sibling, non-amendment)

## 상태

**Active (2026-07-20 KST)** — carrier_story = CFP-2772 (wrapper-self dogfood). Phase 1 = 설계 SSOT (본 ADR + change-plan + Story §3/§7 + 아키텍처 doc). **실 heartbeat emit 모듈 + Jira relay 확장(Arc B-2) + 외부 watchdog(GitHub Actions cron) + 3-state 로직 + lane 임계 baseline + AC-7 discriminating fixture + credential 선언 = Phase 2**(본 Story §8-§11). recovery(재개/kill/alert routing) = out-of-scope(detection layer only, NG-3).

번호 발급 = **로컬 main 21-commit stale 확인 후 origin/main 실측**(`git ls-tree -r --name-only origin/main archive/adr/` numeric max = ADR-163, 149 orphan gap, 164 collision-free, 2026-07-20 KST origin/main 680bd0ff). dual-key 3-leg 정합: filename `ADR-164-parallel-branch-liveness-heartbeat-watchdog.md` ∧ frontmatter `adr_number: 164` ∧ ADR-RESERVATION row 164.

## 컨텍스트

CFP-2772 §1(CODEOWNERS-locked verbatim): 백그라운드·병렬로 도는 여러 에이전트·작업의 **생존(살아있나·멈췄나)** 을 세션 밖에서 파악한다. 특히 **병렬 브랜치 중 하나만 hung** 되면 감지가 안 된다. Jira 에 coarse(집계) 타임스탬프 heartbeat 로 남겨, per-agent 세밀 telemetry 없이 stale 을 감지한다. D1 heartbeat emit / D2 외부 watchdog / D3 write-path 3-state / D4 단계별 baseline.

요구사항리뷰(iter1) PASS + Orchestrator firsthand 로 확정된 5 제약(전부 firsthand 검증됨 — 설계 입력으로 수용):

1. **F-1 관측자-사망 불변식**: 자기 자신의 사망은 자기가 보고할 수 없다(ADR-139 INV-L4 의 in-session observer 는 세션과 함께 죽는다). ∴ D2 는 세션·호스트와 **장애 독립(fault-independent)** 인 외부 관측자여야 한다. Erlang OTP `heart` / K8s liveness probe 동형(ADR-139 already-cited).
2. **F-3 substrate 실상**: dev-process-event substrate(29,842+ events 실측) = agent-emit(Port B) **0건**(전부 hook-source) / story_key 빈값 88% / 18-field allow-list 에 `seq`·`branch`·`agent_type` **미저장** / event_type CLOSED-8(heartbeat 없음). §1 의 "agent_type stamp 재활용" 전제는 **문자 그대로 성립하지 않는다**(Story §4.3 이 재해석을 설계 lane 에 위임).
3. **per-branch 표면 필수**: Jira 이슈 `updated` = 이슈당 단일 last-modified. 단일 mirror 이슈에 N 브랜치 heartbeat 시 1개만 alive 여도 `updated` fresh → `updated<-Nm` JQL 은 **total-stall 만 감지, partial-hang(AC-7) 은폐**.
4. **외부한도(cited)**: GitHub Actions schedule cron = 최소 5분 + jitter 5~30분(피크 시간 단위, self-hosted 우회 불가 — 큐잉이 GitHub측). Jira Automation = 스케줄+JQL 가용, Standard 1,700 exec/월. → D4 stale 임계 하한 = poller jitter 이상. `source: github.com/orgs/community/discussions/156282, cronbuilder.dev/blog/github-actions-cron-schedule.html (Story §6.3 cited)`.
5. **fail-open 금지 상속(ADR-139 INV-L2)**: stale 판정 fail-open 금지 — 미상(unknown)을 정상(PASS)으로 자동승격 금지.

설계 lane 위임 결정: C1(watchdog 구현) / C2(per-branch 식별) / C3(stale surface) / D3(monotonic seq 3-state). 6 deputy(InfraOperationalArch·SecurityArch·TestContractArch·ModuleArch·APIContractArch·CodebaseMapper) 병렬 산출물 synthesis.

## 결정

### §결정 1 — heartbeat liveness = new-sibling, NOT dev-process-event-v1 amendment (핵심 판정)

**heartbeat 를 dev-process-event-v1 계약(SCHEMA)에 얹지 않는다.** 대신 `dev-process-event` substrate 의 **CODE/PATTERN 만 재사용**한다 — agent-emit 스타일 dispatch(브랜치가 자기 정체를 아는 지점), deny-scan/echo-guard/sentinel util, "local-SoT + external-projection" 2-layer 패턴. 이는 §1 의 "substrate 재활용" 전제를 **§4.3 위임 하에 CODE/PATTERN 재사용으로 재해석**한 것이다(§1 verbatim 무변경).

**근거 (adversarial deputy 분열 adjudication — ModuleArch(반대 amendment) vs APIContract(amendment MINOR 가능) 종합)**:

- **liveness ⊥ granularity (Story §2.1 자기 명제)**: dev-process-event-v1 §1 정체 = "10-lane 개발 *과정* 증거"(lane 전이·verdict·결점·diff — **granularity/content** 축). heartbeat = **liveness** 축. Story §2.1 이 이 두 축을 **직교 도메인**으로 명문화(ADR-139:53-58 재확인). heartbeat 를 dev-process-event schema 에 병합하면 **Story 자신의 orthogonality 명제를 위반**한다.
- **new-sibling 선례**: stop-event / spawn-event / fix-event / dev-process-event 는 전부 서로 **new-sibling**(supersede 0, 의미 축 분리). heartbeat 도 같은 선례를 따른다.
- **필요성 게이트(ADR-119 §결정 9)**: dev-process substrate 는 **host-local + gitignored**(`.gitignore:38` `.claude/ledger/`) → GitHub Actions checkout 에 **존재 자체가 없다**. ∴ substrate amendment 는 **외부 watchdog 경로에 도달하지 못하는 LOCAL 기록만** 추가한다 — Story 핵심 목표(외부 감지)에 load-bearing 아님. 이득<비용.
- **freeze 보존**: `branch_key` 를 신규 상관 ID 로 넣으면 §5.1 "4 상관 ID freeze 변경 = amendment 의무" + §4 "필수 field 추가 = MAJOR". amendment cascade(ADR-163/155/043 + _ROW_KEYS 18→20 parity + self-test assert + §9 mining filter + dormant Port B 활성 + heartbeat-전용 seq-MUST invariant)를 유발하나, 얻는 것은 도달-불가 LOCAL 기록뿐.

**귀결**: F-2 의 (a)amendment / (b)코멘트-인코딩 이분법을 **초월** — dev-process-event 계약 **무변경**(AC-13 조건부 "선택 시" vacuously 충족). 계약 SCHEMA 표면 오염 0.

### §결정 2 — C1 watchdog = GitHub Actions cron poller (Option B), ubuntu-latest hosted

**외부 watchdog = GitHub Actions scheduled workflow**(신규 `.github/workflows/branch-liveness-watchdog.yml` + thin wrapper `scripts/check-branch-liveness.sh` → Python SSOT `scripts/lib/check_branch_liveness.py`, ADR-061 관례).

**HARD 제약 (설계리뷰 YAML 검증 의무)**: `runs-on: ubuntu-latest`(GitHub-**hosted**), **NOT self-hosted `MCCHO-DESKTOP`**(Windows). self-hosted 러너는 로컬 호스트와 **동일 장애 도메인** → Orchestrator co-death → **F-1 위반**. hosted 러너는 git/gh/network 만 접근(로컬 무의존) → fault-independent.

**선례(firsthand)**: `.github/workflows/` 에 이미 6+ 동형 cron 감시 워크플로(rollback-signal-monitor / regression-smoke-health-monitor / canary-auto-promote / governance-remeasure-cron / adr-reservation-stale-reclaim / marketplace-lag-detect) — `schedule` + `workflow_dispatch` + `permissions:` 최소 + `continue-on-error`. wrapper-active cron 이 이례적 아님. → repo-분해 macro-boundary pressure 없음(routine 모듈 추가).

**Option A(Jira Automation JQL) 기각**:
1. **per-branch 불가**: JQL 은 issue-level(`updated<-Nm`) → total-stall 만. partial-hang(AC-7) 미감지(제약 3). 코멘트 본문 내부 구조를 필드처럼 질의 불가.
2. **audit-opacity**: 판정 규칙이 Atlassian UI 에 비버전관리·비audit·deny-scan 밖 상주 → wrapper-self dogfood 부적합.
3. **fail-open 금지 self-test 표면 부재**: execution-backed self-test(sentinel honest-degrade 선례)를 못 붙인다.

**KU1(Atlassian 플랜별 정밀 quota) = NON-BLOCKING → research-request-gate 미요청**: 결정-무관(decision-irrelevant) — Option B 는 Automation quota 에 의존하지 않고, cited 1,700/월 worst-case 만으로도 A 기각 충분. 정밀도가 verdict 를 뒤집지 못함(ADR-126 shallow/deep 문턱 = 결정-무관으로 해소, 검사 연극 회피).

### §결정 3 — C2 per-branch 식별 = per-branch pinned COMMENTS (branch→commentId map), NOT per-branch issue

**per-branch = 단일 기존 mirror 이슈 위의 브랜치별 pinned 코멘트**(jira-progress-mirror §3 의 단일 `ACTIVITY_COMMENT_ID` 를 **branch→commentId map** 으로 일반화 — 같은 `addCommentToJiraIssue`, 같은 `mirror_issue_key`, N개 pinned 코멘트). `branch_key` = `git rev-parse --abbrev-ref HEAD` short-name 파생 **slug charset `[a-z0-9-]`** (기계 도출, caller free-text override 미수용).

**per-branch 이슈(createJiraIssue) 기각 = P0 보안 판정(SecurityArch)**: `createJiraIssue` = ADR-099 §A1-1 **deny**. 열려면 ADR-099 Amendment(Layer 1 ratchet-weakening + sunset 3-tuple) 선행 + createIssue blast(org-wide 임의 이슈 대량생성) 감수 → **AC-11(allow-list 무약화) 정면 위반**. per-branch granularity 는 per-branch pinned **코멘트**로 addComment 범위 내 달성 가능하므로 createJiraIssue 불필요.

이것이 **AC-7 partial-hang 은폐의 근원 결함**(단일 mirror 이슈의 단일 pinned 코멘트 → 이슈 `updated`=최근 writer)을 해소한다 — watchdog 는 **브랜치별 코멘트 본문**을 파싱(이슈 `updated` 아님).

**heartbeat relay comment-body 마이크로포맷(emitter↔watchdog 파싱 계약)**:
```
⟦cf-orch⟧ HEARTBEAT branch=<branch_key> seq=<N> story=<KEY> lane=<lane> ts=<UTC ISO8601> — alive
```
- 선두 sentinel `⟦cf-orch⟧` = `echo-guard.sh` `CF_ORCH_SENTINEL` byte-동일 재사용(Arc A 결정폴러 cross-echo 차단).
- `HEARTBEAT` 토큰 = `MIRROR`(Arc B-1 진행미러)와 분별(watchdog 파서가 자기 것만 골라냄).
- 포맷 SSOT = 신규 `scripts/jira-channel/heartbeat-format.sh`(progress-format.sh 형제, ADR-140 reuse-before-write). 스키마·버전 규칙 = Change Plan §11 co-locate(별도 SemVer 트랙 불요, 포맷 변경 = 본 ADR amendment 의무 1줄).

### §결정 4 — C3 stale surface = GitHub durable verdict (CI-native) + Jira human-visibility

**watchdog verdict(stale flag) = GitHub durable 표면**(tracking 이슈 코멘트 / commit status, **CI-native `GITHUB_TOKEN`**). ∴ **Jira-write credential 을 CI 에 신설하지 않는다** → **ADR-099 §A1-1 무변경(AC-11 충족)**. Jira write 는 Orchestrator-alive addComment(narrow-allow) 로만 유지.

**Jira = 인간 가시성 표면**: 브랜치별 pinned 코멘트가 heartbeat tick(생존)과 정체(코멘트 age)를 사람에게 보여준다(§1 "Jira 에 남겨" + U1 Jira 보드/모바일 관측 충족). watchdog 의 **판정**은 GitHub, heartbeat 의 **가시화**는 Jira — 두 표면 역할 분리.

**watchdog READ 표면 + credential(SecurityArch consult)**: watchdog 는 Jira 브랜치별 코멘트를 **read-only** 로 파싱해 staleness 판정. **read-only 스코프 Jira token**(confluence-forward-sync.yml 선례 firsthand: Atlassian token as GH secret / **secret-absent = dry-run**(실호출 0) / `permissions: contents: read` / `continue-on-error` / ubuntu-latest). org-wide-read accepted-risk 는 **명시 disclosure**(ADR-099 Amd2 §A2-0 패턴 — 암묵 위임 금지). token = **infra-resource-baseline.yaml 선언 의무**(ADR-157/CFP-2700 drift-scan fail-closed — 미선언 = 정당 FAIL).
- **credential-zero 대안(설계리뷰 감사)**: watchdog READ 표면을 git 전용 heartbeat 표면(dedicated ref/file, `.claude/ledger` 아님 — gitignored)으로 두면 GITHUB_TOKEN 만으로 0-credential. 단 git-push heartbeat 기계장치 신설 대가. §1 "Jira" 지향 + jira-progress-mirror 재사용 + read-only 선례 감안 → **Jira-read(Path β) 를 primary, git-source(Path α)를 대안**으로 남긴다.

### §결정 5 — D3 write-path 3-state = monotonic seq (clock-independent) + watchdog-own-clock threshold + fail-open 금지

각 heartbeat = `{branch_key, seq(per-branch strictly-monotonic int), state_tag, ts(advisory), lane}`. **seq = 1차 진행 신호, ts = 표시 전용**. watchdog = ack cursor `(branch, last_seq, observed_at)`.

| state | 판별(watchdog receive-time) | verdict |
|---|---|---|
| **신선(fresh)** | `seq_new > last_seq`(strict advance) | live — 진행이 **seq 로 증명**, clock-무관 |
| **정체(stalled)** | `seq` unchanged ≥2 연속 poll **AND** observer-elapsed(last seq-advance 이후) > lane 임계 | stalled |
| **미상(unknown)** | heartbeat 부재/판독불가/malformed/write-실패/poller-자체실패 | **fresh 로 자동승격 금지**(F-6/INV-L2) — 명시 `unknown` |

**clock 기준(F-5 해소)**: 임계 비교 = watchdog **자기 수신 시각**(observer-elapsed / 연속-poll count) — `now − emitter_ts` cross-host diff 는 **절대 계산 안 함**(F-5 skew trap). host clock 조정 단독으로 verdict 조작 불가: backward step 은 seq 를 되돌리지 않고, forward step 은 seq 를 진행시키지 않으며, stalled 는 `seq unchanged` **AND** `elapsed>임계` 둘 다 필요. seq = 진행 카운터(Lamport 논리시계 / K8s "check target progress, not wall time", ADR-139 결정 2 앵커).

**seq 내구성**: `seq = durable-read-back-last + 1`(restart 넘어 monotonic 유지, §8.5.2). read-back 실패 → `unknown`-tagged emit, **NOT seq=0**(F-6). regress(`seq_new < last_seq`) = anomaly → `unknown`(not fresh).

### §결정 6 — D4 lane별 stale 임계 baseline (수치 전부 proposal) + 예상-idle ≠ hung

**임계 하한 = poller jitter 이상**: GH cron 5분 base + peak jitter 15~30분 → 최속 lane 실용 하한 ≈ 2× poll-interval-upper-bound ≈ **30~60분**(proposal). 임계보다 촘촘한 poll 은 quota 낭비.

| lane class | expected active span | stale 임계(proposal) |
|---|---|---|
| short/mechanical(commit·bump·single-file) | minutes | ~30–45분 |
| medium(구현·설계 authoring) | tens-of-min ~ 1–2h | ~2–3h |
| long review(설계리뷰·구현리뷰·보안테스트 dual-peer·deep-research·Codex adversarial) | 1–3h+ 정당 quiet | ~3–4h |

**예상-idle ≠ hung(A3/E1, ADR-139 결정 3 idle-timeout vs total-deadline 2축)**: `state_tag ∈ {active | waiting-external:<reason> | idle-yield}`. 외부 대기(CI green-wait / admin-merge / ADR-109 429-backoff / Arc-A decision grace) = 예상 idle → idle-timeout 완화. **단 절대 total-deadline ceiling 은 유지(INV-L1 — 무한 면제 금지)**: `waiting-external` 는 idle 창을 완화하나 절대 max-wait 를 비활성화하지 않음 → 무한 외부대기도 결국 `unknown` 으로 표면화. seq-advance = idle 창 reset 트리거.

**정직 천장(ADR-119)**: 30~60분/2~3h/3~4h = **proposal** — lock-in 금지, Phase 2 empirical calibration(ADR-139 도 max-wait 수치 empirical 미실증 인정).

### §결정 7 — 관측자 장애독립성(1급) + meta-observer 무한후퇴 종결

dead-man's-switch 를 coarse/human tier 에서 종결(또 다른 자동 감시자 무한후퇴 금지):
- **Tier 0(observed)**: 브랜치가 heartbeat(seq) emit.
- **Tier 1(watchdog)**: GitHub-hosted cron — 세션 AND 로컬 호스트와 fault-independent(hosted, NOT self-hosted).
- **Tier 2(meta, fail-safe inversion)**: watchdog 가 **자기 last-run liveness 마커**를 매 run 기록. 마커 **부재**(>2× cron interval)가 **곧 경보**(침묵=의심, F-6) → watchdog 사망 = "watchdog `unknown`" = non-PASS.
- **regress 종결**: Tier 2 = **인간**(Jira/GitHub/모바일 glance) 또는 최대-coarse 외부(GitHub 자체 "scheduled workflow disabled" 통지)가 소비. Tier 3+ 자동 감시자 미신설. Erlang OTP `heart`(외부 OS 프로그램이 노드 ping — pinger 는 dead-simple) / K8s(kubelet↔pod, kubelet 은 node OS/human 감독) 동형. `source: erlang.org/doc/system/design_principles.html, kubernetes.io/docs/concepts/workloads/pods/probes/ (ADR-139 already-cited)`.

### §결정 8 — 보안 floor: bounded 3-tuple construction + 14-rule redaction 상속 (deny-scan PII gap)

heartbeat egress(→ Jira 코멘트)의 coarse invariant 는 **scan-time 희망이 아니라 construction-time 보장**: formatter 가 오직 `(branch-slug[a-z0-9-], iso8601-ts, monotonic-int)` **bounded 3-tuple** 만 수용(free-form 미수용) → 경로·이메일·자격증명 인코딩 **구조적 불능**.
- **deny-scan.sh PII gap 명시(SecurityArch firsthand)**: deny-scan.sh 는 secret/절대경로 는 차단하나 **email·한국 주민번호(RRN)는 미커버**(반면 `redact_dev_process_content.RULE_NAMES` 14-rule 은 포함). ∴ deny-scan 을 heartbeat 의 **유일 방어로 삼지 않는다** — AC-8 대로 **14-rule redaction floor 상속** 명시 + bounded 3-tuple construction 이 1차 방어, deny-scan 은 backstop.
- **honest-ceiling(ADR-119)**: heartbeat emit·watchdog parse hot-path 에 "ReDoS-safe / DoS-proof / 임의입력 무해" 단정 금지. 명시 가능 = born-safe bound(byte/line-cap + parse-timeout + non-blocking exit0 + 단일-pinned-코멘트-update egress volume bound)만. **proof = Phase 2 SecurityTest(execution-backed)**.

## 결과

- **AC 매핑**: AC-1(§결정3 emit) / AC-2·AC-8(§결정8) / AC-3(§결정4 Jira reach) / AC-4·§결정7(observer-death) / AC-5·§결정5(3-state) / AC-6·§결정6(lane 임계) / **AC-7·§결정3(per-branch pinned 코멘트 → discriminating)** / AC-9·§결정5(fail-open 금지) / AC-10(consumer opt-in-false 무약화 — NG-4) / AC-11(§결정4 Jira-write 무신설) / AC-12(detection only, NG-3) / AC-13(§결정1 non-amendment → 조건부 vacuous).
- **dev-process-event-v1 / ADR-163/155/043 = 무변경**(§결정 1 non-amendment). MANIFEST kind:contract/registry entry 신설 0.
- **codeforge-family.md**: 경계 Y(신규 watchdog credential 표면 — infra-resource-baseline.yaml 선언 의무) + 데이터흐름 Y(브랜치 heartbeat → Arc B-2 relay → 외부 watchdog cron → 3-state) 갱신.
- **Phase 2 residual(설계리뷰 감사)**: (1) watchdog YAML = ubuntu-latest hosted 검증(self-hosted = F-1 위반). (2) watchdog credential = infra-resource-baseline.yaml 선언(ADR-157 drift gate). (3) Path β(Jira-read) vs Path α(git-source, 0-credential) 최종. (4) `waiting-external` self-attestation 이 total-deadline ceiling 을 비활성화하지 않음 검증(INV-L1). (5) §8.7 Jira getComments ordering/pagination 2차 은폐 벡터 = captured-golden(TestContractArch). (6) 임계 수치 = Phase 2 empirical calibration.
- **Epic 아님 — 단일 Story**: D1~D4 는 한 feature(emit↔relay↔watchdog↔3-state↔임계)의 tightly-coupled 양단(AC-7 검증에 양단 필요). Phase 1(설계) + Phase 2(구현) 2-PR 구조로 충분(ADR-127). Phase 2 과대 시 D1+D2 core / D3+D4 refinement 분할 여지만 residual 표기.

## 해소 기준

N/A — permanent policy. (관측성 heartbeat/watchdog 능력 결정 + new-sibling 경계 판정 = 영속. 수치 임계는 Phase 2 empirical calibration 대상이나 결정 자체는 sunset 대상 아님. `is_transitional: false`.)

## 정직성 (ADR-119)

- 외부한도(GH cron jitter / Jira quota) = Story §6.3 cited, 재검 불필요.
- 임계 수치 = proposal(empirical 미실증). 완전탐지·안전 단정 0.
- watchdog 정규식 ReDoS-safe 미단정 — born-safe bound 만. proof = Phase 2 SecurityTest.
- KU1(Atlassian 정밀 quota) = 확인 불가지만 결정-무관(§결정 2) → research-request-gate 미요청.
