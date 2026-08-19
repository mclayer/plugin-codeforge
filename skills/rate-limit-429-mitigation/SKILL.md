---
name: rate-limit-429-mitigation
description: in-process Anthropic infra 429 surgical mitigation procedure SSOT. Use when Orchestrator detects Anthropic API rate limit response (HTTP 429 / "Server is temporarily limiting" / "rate limit" / "quota exceeded") during codeforge lane spawn or consumer project work, before parallel-burst contexts (Phase 0 brainstorm 7-agent spawn / debate round N+1 / deputy 6+3+1 fan-out). Provides 3-step procedure (detection set — ADR-109 §결정 1 + Amendment 1, exp-backoff curve, retry sequential composition + fable-리밋 opus failover branch) + decision tree (low/medium/high intensity bucket → cap lookup). ADR-109 §결정 1-§결정 7 + §결정 1 Amendment 1 binding. Orchestrator inline whitelist closed 4-entry (ADR-039 §결정 2) 무손상 — retry primitive 위치 = 본 skill body.
---

# codeforge:rate-limit-429-mitigation

ADR-109 SSOT 정합 in-process Anthropic infra 429 mitigation procedure. Claude Code session alive context (Orchestrator 직접 제어 영역). Sibling Story B (#1355) OS-level external session auto-resume disjoint axis.

## When to invoke

본 skill 호출 trigger 3 종 (Orchestrator + chief author + RequirementsPL 모두 적용):

1. **Detection trigger** — Anthropic API response 안 다음 4 pattern any-match (closed-set, ADR-109 §결정 1):
   - `"rate limit"`
   - `"quota exceeded"`
   - `"429"`
   - `"Server is temporarily limiting"`
   > **확장 감지집합 (session/usage-limit class 편입 = 6 literal 총합)**: 위 base 4-tuple 에 `session limit` + `usage limit` 2 literal 을 더한 6 literal any-match 가 완전 감지집합이다. **authoritative SSOT = ADR-109 §결정 1 Amendment 1 code-fence** — 본 skill 은 base 4-tuple 만 참조 편의로 나열하고 확장 2 literal 은 **cross-ref only (중복 정의 금지, G1)**. fable-리밋 opus failover(Step 3.3) trigger 도 이 6 literal 감지집합을 쓴다.
2. **Pre-burst preventive trigger** — parallel-burst context 진입 직전:
   - `codeforge:codeforge-brainstorm` skill 호출 직후 (7-agent Phase 0 spawn 직전)
   - DesignReview lane blanket debate round N+1 진입 직전 (debate-protocol-v1 v1.2)
   - ArchitectPLAgent 6+3+1 deputy + 4-tuple sub-tuple 단일-메시지 multi-tool spawn 직전
3. **Cascade detection trigger** — `docs/kpi/429-incident-history.jsonl` 직전 30분 누적 incident count ≥ 1건 시 (medium/high intensity bucket 진입)

## 3-step procedure

### Step 1 — 탐지 (Detection)

ADR-109 §결정 1 4-tuple any-match. detection enum closed-set (no regex wildcard).

```
detected = "rate limit" in response_body
        OR "quota exceeded" in response_body
        OR "429" in response_status
        OR "Server is temporarily limiting" in response_body
```

- **확장 감지집합 cross-ref (G1 — 중복 정의 0)**: session/usage-limit 계열 포함 완전 감지집합 = base 4-tuple + `session limit` + `usage limit` = 6 literal (closed-set, no regex wildcard invariant 승계). **authoritative SSOT = ADR-109 §결정 1 Amendment 1 code-fence** — 위 pseudo 는 base 4-tuple 만 나열, 확장 2 literal 재열거 금지(단일 SSOT).
- **False-positive 차단**: regex wildcard 0 (closed-set only). user prompt body verbatim match 차단 (response source verify, TLS layer). fable-리밋 failover 감지 scope = error/termination notification 표면 한정 (subagent substantive output 본문 NOT — false-positive hazard, ADR-141 A6-1).
- **529 disjoint** (ADR-109 §결정 6): HTTP 529 status code = retry 무의미 영역 — 본 skill 영역 외 (longer cooldown 60s base max 300s separate axis). 529 = failover 감지집합 NOT-IN (pool-agnostic overload, ADR-109 §결정1 Amendment 1 (e)).

#### Step 1.1 — 산출 고정 (대기 진입 **전** — ADR-179 §결정 7)

탐지 직후 · **대기 진입 전**에 부분 산출을 먼저 고정한다. 대기·재시도는 그 다음이다.

- 고정 대상·형식 = [ADR-179](../../archive/adr/ADR-179-agent-salvage-bundle-handoff.md) §결정 2 salvage 번들(reference-first 얇은 인덱스). 본 skill 은 **착지 시점만** 규정하고 번들 스키마를 재정의하지 않는다 (pointer only).
- 고정 실패 시 degrade = ADR-179 §결정 8 사다리(primary → F1 → F2 → F3). **degrade 경로에 §결정 2 backoff 재적용 금지** — 회수는 재시도 축이 아니다 (ADR-179 §결정 6).
- 회수 자체의 **재시도 예산 = 0**. 사다리의 재시도 예산은 본 절차 소관 (ADR-179 §결정 7 표 `429 계열` 행).

### Step 2 — 대기 (Backoff)

ADR-109 §결정 2 exp-backoff curve full jitter (Marc Brooker AWS Architecture Blog 2015 verbatim).

#### Step 2.1 — 대기원 헤더 (wait source)

대기원 = **`retry-after` 한정**(초 단위 상대값). `anthropic-ratelimit-*-reset` 계열은 **RFC 3339 절대시각**이라 대기원이 **아니다** — 잔여 창 계산 정보로만 쓴다. 근거·SSOT = [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) §결정 2 (Amendment 3 정정).

**헤더 의미 클래스표 (정본 — 대조 대상, 하드코딩 사본 금지)**

```header-semantic-class
# [source: https://platform.claude.com/docs/en/api/rate-limits]
# <header token> | <semantic class> | <대기원 자격>
retry-after | relative-seconds | eligible
anthropic-ratelimit-*-reset | absolute-rfc3339 | ineligible
```

```
wait_seconds = parse_retry_after_header(response.headers)   # 입력 = retry-after 만
# retry-after 부재 → header 유래 대기 산출 0 (reset 계열로 대체 산출 금지)
```

#### Step 2.2 — Exp-backoff curve (header 부재 시)

곡선·파라미터의 **수치는 본 문서에 기재하지 않는다.** 단일 SSOT = [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) §결정 2 (Amendment 3 "Single SSOT — backoff 파라미터"). formula · base · single-attempt cap · max attempts · nominal 계열 · 누적 budget **전건**을 그 절에서 읽어 적용한다.

- **재기재 금지 사유 (사변 아님 — 관측된 divergence)**: 구 사본은 cap 을 상한 **안**(`min(...)`)으로 옮겨 SSOT 가 열어둔 자유도를 사본이 결정했다. 두 문서를 읽은 두 사람이 서로 다른 구현을 얻었다. 사본을 지우는 것이 정정이다.
- **jitter rationale**: no-overlap retry distribution (contention avoidance proven) — empirical-source 인용은 ADR-109 §결정 2 소재.

### Step 3 — 재시도 (Retry sequential composition)

ADR-109 §결정 3 sequential composition (within-model timing axis → cross-model substitution axis disjoint cross-ref).

```
attempt 1: same-model timing 경로 (경로 키 `same-model-timing`) — SSOT = ADR-109 §결정 3 step1 + §결정 2
  ├── success → §14 Lane Evidence marker write [429-auto-retry: count=1, final_status=success] → return
  └── failure → attempt 2

attempt 2: cross-model substitution (step2 slot) — 현 tenant = ADR-141 Amendment 6
           (fable-리밋 → opus failover, max 1회 per-spawn-attempt, cross-model axis cross-ref)
           prior tenant: ADR-057 §결정 2 (Sonnet → Opus) — ADR-141 로 moot/dead (dead-mark 보존)
  ├── success → §14 marker [429-auto-retry: count=2, final_status=success] → return
  └── failure (opus 도 리밋) → attempts 3..N (soak)

attempts 3..N: soak (경로 키 `soak`) — SSOT = ADR-109 §결정 3 step3 + §결정 2 max attempts
  ├── any success → §14 marker → return
  └── all fail → ADR-109 §결정 4 circuit breaker open → ADR-109 §결정 5 user manual resume only
                 (경로 키 `manual-resume`, SSOT = ADR-109 §결정 3 step4)
```

> `N` = ADR-109 §결정 2 max attempts. 본 문서는 그 수치를 재기재하지 않는다 (Step 2.2 pointer 규율).

#### Step 3.0 — 재시도 사다리 레지스트리 (native ∪ codeforge 통합)

본 표 = **재시도를 발행하는 단계**의 통합 레지스트리다. codeforge 사다리만 담으면 `distinct(층) = {codeforge}` 가 되어 **공집합 위 항진**(구조적 항상-GREEN)이므로, **네이티브 행 등재가 필요조건**이다.

- **`층` 값공간 (본 표가 유일 정의 site)** = `native` 또는 `codeforge`. 미기재·값공간 밖 = **fail-closed**.
- **`slot` ordinal 1..4 = frozen** — SSOT = ADR-109 §결정 3 "slot ordinal frozen". 번호를 당기면 ADR-141 A6-2 의 "step1 bypass → step2 직행" 이 *"soak 을 bypass 하고 soak 으로 직행"* 이라는 자기모순이 된다. **dead 인 것은 tenant 이지 slot 이 아니다.** 네이티브 행은 §결정 3 ordinal 을 갖지 않으므로 `-`.
- **`대상 클래스` 값공간 = ADR-109 §결정 1 Amendment 1 (b) code-fence 6 literal.** 본 표는 그 fence 를 **참조**하며 재열거하지 않는다 (하드코딩 사본 금지 · 단일 SSOT).
- **`층` 은 선언인 동시에 검사 대상** — 검사는 `SSOT`·`mechanism_ref` 열에서 층을 **독립 도출**해 선언 라벨과 교차검증한다. 불일치 = fail-closed.

**네이티브 커버 정본 앵커 (closed set — 앵커 의무·유일성·클래스 정합의 대조 정본)**

```native-cover-anchor
# <anchor> | <axis> | <커버 클래스 (6-literal 중)>
# 출처: Story CFP-2984 §6.3.2 커버 경계 표(835 / 836 / 837 / 854) + §6.3.3 승수(855).
CHANGELOG:835 | non-retry | rate limit, quota exceeded, 429, Server is temporarily limiting
CHANGELOG:836 | non-retry | rate limit, quota exceeded, 429, Server is temporarily limiting
CHANGELOG:837 | non-retry | usage limit, session limit
CHANGELOG:854 | retry | rate limit, quota exceeded, 429, Server is temporarily limiting
CHANGELOG:855 | retry | rate limit, quota exceeded, 429, Server is temporarily limiting
```

- `층=native` 행은 **`axis: retry` 앵커만** 인용할 수 있다 — 본 레지스트리 정의역 = 재시도 **발행**. `non-retry` 앵커(부분 산출 반환 · 오분류 보고)를 인용해 네이티브를 참칭하는 경로를 닫는다.
- **앵커 유일성**: 한 앵커를 2개 이상의 `층=native` 행이 주장할 수 없다.
- `CLAUDE_CODE_RETRY_WATCHDOG` 와 `CLAUDE_CODE_MAX_RETRIES` 는 **같은 CHANGELOG 조항(`855`) 한 변경**이라 앵커 유일성 하에서 2 행으로 분리할 수 없다 — 1 행에 두 env 를 tenant 로 병기한다 (없는 앵커를 지어내지 않는다).

| slot | 경로 키 | 층 | 대상 클래스 | tenant | SSOT | mechanism_ref |
|---|---|---|---|---|---|---|
| - | `native-transient-retry` | native | rate limit, quota exceeded, 429, Server is temporarily limiting | harness 자동 backoff 재시도 | harness CHANGELOG | CHANGELOG:854 |
| - | `native-retry-multiplier` | native | rate limit, quota exceeded, 429, Server is temporarily limiting | `CLAUDE_CODE_MAX_RETRIES` 기본 상한 + `CLAUDE_CODE_RETRY_WATCHDOG` 활성 시 상향 | harness CHANGELOG | CHANGELOG:855 |
| 1 | `same-model-timing` | codeforge | session limit, usage limit | ADR-109 §결정 2 backoff (한도 계열 진입 대기) | ADR-109 §결정 3 step1 | - |
| 2 | `cross-model-substitution` | codeforge | session limit, usage limit | ADR-141 Amendment 6 fable→opus fresh re-spawn | ADR-141 Amendment 6 | - |
| 3 | `soak` | codeforge | session limit, usage limit | ADR-109 §결정 2 max attempts soak | ADR-109 §결정 3 step3 | - |
| 4 | `manual-resume` | codeforge | session limit, usage limit | ADR-109 §결정 5 user manual resume only | ADR-109 §결정 3 step4 | - |

> **중첩 금지 — 실제 중첩 제거의 결과**: transient 429 계열(base 4-tuple)의 재시도 **발행은 네이티브 전담**이다. codeforge 사다리는 네이티브가 재시도하지 **않는** 한도 계열(`session limit` / `usage limit`)만 발행한다. 두 층의 대상 클래스 교집합 = **공집합**. 구 문면은 attempt 1 이 transient 429 를 대상으로 삼아 네이티브 승수 × codeforge 사다리 **중첩을 지시**하고 있었고, 그것이 retry amplification 의 자기생산이었다.
>
> **정직 천장 (over-claim 금지)**: 위 fail-closed 검사가 닫는 것은 **중복형 오라벨**(진짜 codeforge 단계를 유효 앵커 복사로 native 위장)뿐이다. **치환형**(네이티브 행 자체가 없고 codeforge 동작 서술 하나만 `native` 로 적힌 경우)은 "이 서술의 행위 주체가 누구인가" 라는 자연어 의미 판정으로 환원되어 **잔여**이며, **사람 검토(advisory)** 에 귀속된다. 본 절을 "층 오라벨 완전 봉쇄" 로 서술하지 말 것.

#### Step 3.0b — 네이티브 재시도 승수에 대한 명시 입장

증폭식 `N x M` 의 **N**(네이티브 승수)에 대한 codeforge 의 입장을 구조화 필드로 고정한다. **미기재 = 검사 실패(fail-closed).**

```native-multiplier-stance
# stance 값공간 (closed 3-enum) = 수용 | 상한 재설정 | 관측만
# <multiplier> | <값> | <발동 조건> | <stance>
dominant: CLAUDE_CODE_MAX_RETRIES
CLAUDE_CODE_MAX_RETRIES | 기본 상한 15 | 상시 (현 지배 승수) | 수용
CLAUDE_CODE_RETRY_WATCHDOG | 활성 시 300 (15 cap 해제) | watchdog 활성일 때만 — 호스트 env·settings 둘 다 미설정 실측 | 관측만
```

- **`300` 은 현행값이 아니다** — 상류 문면 verbatim = "watchdog **now raises** … to 300 **and lifts the cap of 15**" 이므로 **watchdog 활성이 전제**다. 현 지배 승수 = `CLAUDE_CODE_MAX_RETRIES` 기본 상한 **15**. `300` 을 현행으로 인용하면 위험을 20배 과장한다.
- **`수용` 의 뜻** = codeforge 가 N 을 낮추지 않는다는 것이지 `N x M` 을 방치한다는 뜻이 아니다. M 측 통제는 Step 3.0 레지스트리의 중첩 금지(대상 클래스 교집합 = 공집합)가 담당한다.
- **`관측만` 의 뜻** = watchdog 을 켜지 않는 현 상태의 기록이며, 켜면 N 이 300 으로 올라 증폭식이 바뀐다는 사실의 가시화다. 켜는 결정은 본 skill 밖.

#### Step 3.1 — Circuit breaker open (ADR-109 §결정 4 3-window AND)

3 window 모두 충족 시 circuit breaker open:

| Window | Threshold | Source |
|---|---|---|
| Fast | 5건 / 1min | `docs/kpi/429-incident-history.jsonl` rolling window |
| Medium | 10건 / 5min | 동상 |
| Slow | 3건 / 1 week | `docs/kpi/429-incident.json` weekly aggregate |

#### Step 3.2 — Cascade depth ≥ 2 → user manual resume only (ADR-109 §결정 5)

`cascade_depth` = 단일 user request 안 retry sequence nested cascade level. depth ≥ 2 (예: same-model 429 → Opus fallback → Opus 429 → 2차 retry burst) 시:

- **자동 재시도 금지** (ADR-057 §결정 2 invariant verbatim 답습)
- **`AskUserQuestion` escalation** 또는 **사용자 turn 대기**
- §14 marker `[429-auto-retry: count=N, final_status=failed]` write + KPI JSONL append-only event log row write (cascade_depth field)

#### Step 3.3 — fable-리밋 branch (opus failover — ADR-141 Amendment 6)

fable 배정 subagent(ADR-141 Amendment 4 carve-out 10 역할 — 6 lane PL + ArchitectAgent + ResearcherAgent + PMOAgent + IntegrationTestAgent) spawn 이 리밋 계열 신호(위 6 literal 확장 감지집합 any-match)로 실패/mid-run 조기종료 시 — 위 attempt 1-6 same-model soak 과 **별 경로**(Option A 즉시전환). 실행 주체 = Orchestrator(ADR-039 spawn monopoly, lane PL 자가-재spawn 불가):

```
fable subagent 리밋 감지 (error/termination notification 표면 한정)
  → §결정 3 step1 (fable same-model exp-backoff soak) BYPASS      # Option A 즉시전환
  → step2 (fable→opus): 즉시 fresh re-spawn — 새 Agent + model:opus override (동일 입력 패킷)
       · SendMessage resume 금지 (원본 frontmatter model:fable 재해석 재실패 = CFP-2236 root cause)
       · per-spawn 1회 독립 카운터 (재진입/FIX 재spawn 시 시도마다 리셋 — 무한 failover 차단)
       · §14 marker [rate-limit-failover:fable→opus] write (Telemetry 절)
  ├── opus 성공 → return
  └── opus 도 리밋 → cascade_depth=1 착지 → 여기서부터 §결정 2 exp-backoff same-model soak (opus)
         └── soak 소진 후에도 리밋 → cascade ≥ 2 → §결정 5 user manual resume only
```

- **step1 bypass 근거 3층** (ADR-141 A6-2): reset long-horizon(실관측 `resets 10:20pm` ≫ §결정 2 backoff budget) / fable·opus **별 pool** / Retry-After trap(§결정 2 Retry-After-우선이 reset hint 존중 시 fable ~3h 대기 = "fable full-soak 대기 금지" 위반 → Option A 만 회피).
- **cascade count-in** = fable→opus hop = `cascade_depth` **1(COUNTS)**. opus 착지 후 opus 자기 within-model soak 미증가. disjoint 카운터 금지("1-hop then manual" semantics 강제).
- **비대상 3종**(failover 미발동) = Orchestrator 세션 자체 리밋(launch 고정 → 기존 대기/수동 handoff) / refusal(`stop_reason: refusal` — 수동 opus 재spawn 방어, CFP-2803) / 비-fable tier(haiku 7 / sonnet 10 / opus) subagent 리밋. 상세 = playbook §3.0.12b / ADR-141 A6-3.
- **감지집합 cross-ref (G1 — 중복 enum 정의 0)**: 이 branch trigger 감지집합 = base 4-tuple + `session limit` + `usage limit` = 6 literal. authoritative SSOT = ADR-109 §결정 1 Amendment 1 code-fence — 본 skill 재열거 금지.
- **dead slot re-tenant (부활 아님)**: step2 slot 은 구 ADR-057 §결정 2(sonnet rate-limit→opus)를 cross-ref 했으나 ADR-141 로 moot/dead 라 구조적으로 비어 있다. fable 브랜치가 신규 trigger(fable 리밋)·신규 SSOT(ADR-141 Amendment 6)로 re-tenant — ADR-057 Superseded 유지, sonnet fallback machinery 부활 아님.

## Decision tree — Intensity bucket → Cap lookup

Phase 0 brainstorm 7-agent burst + debate round + deputy fan-out 진입 직전 cap lookup. `docs/kpi/429-incident-history.jsonl` 직전 30분 window incident count 기준:

```
src = load("docs/kpi/429-incident-history.jsonl")

# 데이터원 부재 3형태(파일 없음 / 빈 파일 / DATA 행 0)는 모두 "부재" 로 정규화한다.
# 부재를 intensity == 0 (Low) 으로 삼키는 것 = silent-zero → 금지 (ADR-109 §결정 4 Amendment 3).
if datasource_absent(src):
    report("429 telemetry 데이터원 부재 — intensity 미판정")   # 명시 보고 의무
    bucket = "unknown_absent_datasource"    # Low 로 낙하 금지 (부재 != 0건)
    parallel_spawn_cap = 4
    spawn_stagger_ms = 5000
    fallback_mode = "sequential_2batch"
    return

intensity = count_429_incidents_last_30min(src)

if intensity == 0:  # Low intensity
    parallel_spawn_cap = 13  # default (parallel-dispatch-protocol-v1 v1.2 §6.2 worker_count_max — CFP-2914)
    # ★ 13 은 '검증된 안전값'이 아니다 — 아래 두 단서를 반드시 함께 읽는다.
    #  ① 경험칙 초과 사실: CFP-2914 Story §6.1 F-14 = "동시 3~5 우세, 병렬 호출 5~10 cap 후
    #     concurrency limiter" (확신도 '추정(강)', 1차 규격 아님). 13 은 이 경험칙을 넘는다.
    #     본 배정은 1차 규격(계약 정의 + roster 산술: 9 deputy + 4-tuple sub-tuple 4)을 택했고
    #     경험칙을 채택하지 않았다. 갈림 기록 = Change Plan §3.4.4 / Story §7 R-3.
    #  ② 429 관측 의무: 발생 시 ADR-109 exp-backoff + `Retry-After` 준수 + §10 FIX Ledger 또는
    #     Story 관측 기록에 남긴다. **재시도 실패를 이유로 peer·deputy 를 빼는 것은 C-4·C-5 위반**이다.
    #     (acceleration limits 축은 조회 불가 = 미판정 — '안전/문제 없음'으로 서술 금지, Change Plan §3.5.)
    spawn_stagger_ms = 0    # no stagger
    fallback_mode = "parallel"

elif intensity == 1:  # Medium intensity
    parallel_spawn_cap = 4  # sequential 2-batch (4-agent → 3-agent)
    spawn_stagger_ms = 5000  # 5s inter-batch wait
    fallback_mode = "sequential_2batch"

else:  # High intensity (>= 2)
    parallel_spawn_cap = 1  # fully sequential
    spawn_stagger_ms = 10000  # 10s inter-agent wait
    fallback_mode = "fully_sequential"
```

- **Phase 0 brainstorm 7-agent spawn** (`codeforge:codeforge-brainstorm`): low/medium/high intensity bucket 적용
- **Debate round N+1**: round-level cascade detection (직전 2 round 누적 429 ≥ 2건 → `pause_reason: 429_cascade_throttle` + `AskUserQuestion`)
- **Deputy 6+3+1 + 4-tuple fan-out**: ArchitectPLAgent 단일-메시지 multi-tool spawn 직전 동일 lookup 적용
- **★ 데이터원 부재 = 침묵 금지**: `docs/kpi/429-incident-history.jsonl` 의 기계 append 경로가 0건이라 count 는 항구적으로 0 이다 (ADR-109 §결정 4 Amendment 3 telemetry-gated 재선언). 부재를 Low 로 낙하시키면 "관측 결과 한산함" 과 "관측 자체가 없음" 이 구분 불가해진다 — 위 `unknown_absent_datasource` 분기가 그 구분을 강제한다.

## Anti-pattern guard (RefactorAgent 권고 정합)

본 skill body = **3-step procedure 수준만** codify. 다음 영역 = **skill body 영역 외**:

- Jitter algorithm 세부 구현 (full jitter vs decorrelated jitter vs equal jitter) — Dev 실행 시점 결정 영역
- HTTP header parsing 세부 (`Retry-After` delta-seconds vs HTTP-date format edge case) — Dev 실행 시점 결정 영역
- Anthropic SDK 또는 HTTP client 의존성 (concrete library 선택) — runtime cover, skill body 영역 외
- Per-tier rate limit threshold tuning (per-org / per-API-key adaptive threshold) — Phase 2 telemetry post-deploy refine 영역 (ADR-068 I-5 dimensional empirical grounding 정합)

**rationale**: skill body 과세분화 시 (1) 변경 surface ↑ (2) ADR-064 §결정 5 CFP scope unitary 위반 risk (3) RefactorAgent decoupling 권고 위반 (skill body = procedure SSOT only, implementation detail = Dev 영역).

## Telemetry write (§14 Lane Evidence marker)

Retry sequence 종료 (success / failed / abort) 시점 의무 marker write:

```yaml
# Story §14 lane_evidence[] entry 안 transcript 필드
transcript: "<lane evidence narrative> [429-auto-retry: count=<N>, final_status=<success|failed>]"
```

- regex (mechanical lint `429-retry-evidence-presence` warning tier, ADR-109 §결정 8.1):

```
\[429-auto-retry: count=\d+, final_status=(success|failed)\]
```

- **§10 FIX Ledger row append 금지** (ADR-109 §결정 9 boundary): 429 retry = 운영 phase telemetry axis (ADR-104 정합), governance FIX 영역 외. fix:* label 미부착, ADR-067 RESET counter 영향 0.

### fable-리밋 failover marker (§14 전용 — ADR-141 Amendment 6)

fable→opus failover(Step 3.3) 발동 시 §14 Lane Evidence transcript 에 **별 태그** 기록:

```yaml
# Story §14 lane_evidence[] entry 안 transcript 필드
transcript: "<lane evidence narrative> [rate-limit-failover:fable→opus]"
```

- **§10 FIX Ledger row append 금지** (ADR-109 §결정 9 / ADR-057 §결정 4 격리): failover = 운영 telemetry axis ≠ governance FIX. fix:* label 미부착, ADR-067 RESET counter 영향 0.
- **비합산·별 measurement**: 위 `[429-auto-retry: ...]`(same-model within-model retry) 및 dead 태그 `[rate-limit-fallback:sonnet→opus]`(sonnet 축, dead)·`[model-unavailable-fallback:fable→opus]`(model-unavailable 축, dead)와 **별 이름·별 measurement**("failover" token 이 "fallback" 과 분별) — KPI 분모/분자 오염 0.
- **matched detection literal 기록 권고** (auditability — false-positive[특히 `usage limit` negated-context] post-hoc audit). secret 금지(ADR-109 §결정 10 redaction matrix — account_id/org_id 임베드 금지; reset time KST 는 비밀 아님).

## KPI JSONL append-only event log

`docs/kpi/429-incident-history.jsonl` 동시 append (ADR-109 §결정 8.2 + §결정 10 redaction matrix 정합):

```jsonl
{"timestamp": "<KST +09:00 ISO 8601>", "lane": "<요구사항|설계|...>", "agent_role": "<PL|deputy|worker>", "retry_count": <int>, "final_status": "<success|failed>", "cascade_depth": <int>, "error_pattern": "<4-tuple enum>"}
```

- **Secret redaction matrix** (ADR-109 §결정 10 unconditional invariant ADR-068 I-3):
  - `org_id` / `account_id` = **strip (collection-time)** (수집 자체 금지)
  - `session_uuid` = hash (SHA-256 truncated 8-byte)
  - `api_endpoint` = mask (domain only, path strip)
  - user prompt body / lane agent prompt body = 수집 금지

## Cross-references

- [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) — 본 skill body SSOT (§결정 1-§결정 10)
- [ADR-039](../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 2 inline whitelist closed 4-entry 보호 + §결정 9 carryover (Amendment N)
- [ADR-044](../../archive/adr/ADR-044-phase-scoped-sequential-team.md) — Amendment N team-spec yaml `parallel_spawn_cap` + `spawn_stagger_ms` + `cascade_circuit_breaker` 3 field 신설
- [ADR-057](../../archive/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — §결정 2 cross-model substitution axis (sequential composition cross-ref)
- [ADR-141](../../archive/adr/ADR-141-all-opus-single-tier.md) — Amendment 6 fable-리밋 opus failover 규범 SSOT (Step 3.3 fable-branch · §14 `[rate-limit-failover:fable→opus]` 태그) + §결정 1 Amendment 1 감지집합 확장 (session/usage-limit class = 6 literal, detection enum authoritative SSOT)
- [ADR-064](../../archive/adr/ADR-064-decision-principle-mandate.md) — §결정 4 Trace 4 Amendment N (surgical exception channel)
- [ADR-067](../../archive/adr/ADR-067-fix-ledger-implementability-escalation.md) — RESET contamination 차단 cross-ref
- [ADR-104](../../archive/adr/ADR-104-operational-phase-definition.md) — 운영 phase 1st-class 정의
- [ADR-106](../../archive/adr/ADR-106-operational-signal-pmo-input-circuit.md) — 운영 metric → PMOAgent input 회로
- `mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1354-in-process-429-mitigation.md` — Phase 1 Change Plan carrier (dogfood-out per ADR-013)
