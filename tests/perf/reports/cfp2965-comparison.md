# CFP-2965 개선 전/후 비교 리포트 (Plane A run-local · 1회성)

> 산출물 성격: **1회성 run-local 리포트** — 상시 회귀 감시 채널 신설 0 (ADR-163 비발동, Change Plan §8.3).
> 기록 항목 = 훅 식별자 / 소요(ms) / exit code / 만료 여부만. **command 원문·인자 기록 0** (R-1 준수).

## 1. 측정 좌표 (AC-17 각인)

| 항목 | 값 |
|---|---|
| before 트리 | `561da632d` (S0/S1 착지 직후 — production 코드 변경 0 시점) |
| after 트리 | `b71c0c04c` (S2·S3·S4·S6·S7·S8·S10 착지, Wave 3 테스트 포함) |
| `hooks/hooks.json` sha256 (after) | `e866aef3385eb5b5aef2313309606b440f0f6aad894c492b9bfbb86dd3a6b7d2` |
| plugin 버전 (측정 시점 repo) | `6.128.2` (`.claude-plugin/plugin.json`) — 본 리포트 측정은 **repo 트리 직접 실행**(플러그인 캐시 비경유). 측정 직후 `6.129.0` 으로 bump (버전 문자열만 변경 — 측정 대상 코드 동일). Plane B after 창은 **6.129.0 캐시 반영 이후**에만 유효 |
| 측정 창 (KST) | 2026-08-14 05:45 ~ 06:15 |
| 호스트 | Intel i9-9900K / 논리 코어 16 / 프로세스 수 473 |
| Defender 실시간 보호 | **ON** (`DisableRealtimeMonitoring=False` 실측) — S1 baseline 측정 창(OFF 정황)과 상이 |
| 동시 세션 | 측정 전용 창 (외부 claude 프로세스 0 실측) |
| 부하 스냅샷 (CPU) | 부하 대리치 = 위 호스트 행의 프로세스 수 473 · 외부 claude 프로세스 0 · 전용 창 — **CPU 사용률(%) 는 본 창에서 미수집** (미기록을 수치로 대체하지 않는다) |
| bash / python | 5.2.37(1) / CPython 3.14.4 |

**AC-17 규율 적용 상태**: 본 Plane A 는 repo 트리 직접 실행이므로 플러그인 캐시 신선도와 무관(캐시 미개입).
**플러그인 캐시 경유 실세션 측정(Plane B after)은 bump → `claude plugin update` → 다음 세션 이후**에만 유효 —
현 시점 미수행이므로 아래 §6 에서 **pending 으로 선언**한다 (미확인 수치 기입 금지 규율).

**AC-17 각인 stale 선언 (CFP-2949 시점 추가)**: 위 각인은 **after 트리 `b71c0c04c` 시점의 값**이며,
그 트리에 대해서는 지금도 참이다(실측 대조 완료). 이후 CFP-2949 가 훅 정의에 `SessionStart` 엔트리
1개(`session-start-scheduled-task-watchdog`, timeout 10)를 추가해, 현 작업 트리의 `hooks/hooks.json`
실계산 해시는 `79f2173567d47f9b9e3adc33a141df90d03cb61ed3cd997fe1f94bd97735c5c3` 이다.
**재측정은 미실시**이고 **각인은 갱신하지 않는다** — 그 결과 `test_ac17_hooks_json_sha256_anchor` 는
**의도된 RED** 로 남는다(테스트 완화·앵커 축소도 하지 않았다).

- **각인을 갱신하지 않는 이유**: 각인 갱신은 §3~§7 의 수치가 현 25-엔트리 트리에서 측정된 것처럼
  보이게 만든다 — 재측정 없는 각인 교체는 수치 무변조 규율 위반이다.
- **앵커를 좁히지 않는 이유**: 각인 대상을 Bash 체인 훅 부분집합으로 축소하면 훅 정의 파일 **전체**
  변경에 대한 검출력을 잃는다 — 이는 결함 해소가 아니라 게이트 완화다.
- **관측 사실(판정 아님)**: CFP-2949 가 추가한 엔트리의 이벤트는 `SessionStart` 이고, 본 리포트가
  측정한 대상은 §2 의 Bash 체인 훅 7종(PreToolUse 6 + PostToolUse 1)이다 — 추가 엔트리는 그 7종
  목록에 없다. 이는 **정의역 관측의 기술일 뿐**이며, "그러므로 기존 수치가 여전히 유효하다" 는
  판정은 본 선언의 범위 밖이다(해당 판정 = CFP-2965 소유자·설계 lane 소관).
- **재측정 미실시 사유 (실측 근거)**:
  ① 각인 행은 "after 트리 = `b71c0c04c`" 에 종속된 값이라, 현 트리 해시를 이 행에 넣으려면
  after 트리 정의 자체를 CFP-2949 커밋으로 바꿔야 한다. 그 경우 §4 exec census(37→30)·§5 판별
  실험·§7 축 판정이 전부 `b71c0c04c` 기준 산물이므로 함께 재유도 대상이 된다 — 재측정이 아니라
  타 Story 측정 정체성의 재정의다.
  ② 측정 창 동일성 미충족 — 본 선언 시점 호스트 실측은 `claude` 프로세스 **32개** · 총 프로세스
  **528개** 로, 위 표의 "측정 전용 창(외부 claude 프로세스 0)" · "프로세스 수 473" 과 다르다.
  §9 의 "비교쌍 = 동일 창·동일 환경값에서만 유효" 선언에 따라 이 창에서 얻은 수치는 위 표에
  병기할 수 없다. (실시간 보호 상태는 `DisableRealtimeMonitoring=False` 로 위 표와 동일 실측.)
- **회부**: 재측정 또는 각인 정의역 재설계 = follow-up Issue #2982 (CFP-2949 는 각인·테스트 무변경).

## 2. 방법 (Change Plan §8.3 Plane A 프로토콜)

- **paired interleaved ABAB**, 쌍 안에서 before/after 를 인접 실행 → 시간대 변동을 공통화 (블록 순차 금지 준수).
- **n = 30 쌍** / 대상 = Bash 체인 훅 7종 + 체인 순차 wall(7종 1회 통과).
- 검정 = **쌍차 Wilcoxon 부호순위(정규근사·동점 보정·연속성 보정)** + 부호 검정 병기.
- 도구 = `tests/perf/paired-ab.py` (본 Story 산출, stdlib only). 원자료 = `tests/perf/reports/raw/*.csv`.
- 원장 오염 격리: arm 별 `CLAUDE_PROJECT_DIR` sandbox 분리 · bypass env 전부 unset · warmup 2회 폐기.
- **음성 대조군 내장**: 이번 Story 가 건드리지 않은 훅 3종(cross-repo-gh-safety / dev-process-capture 2종)이
  Δ≈0 을 보여야 측정계가 신뢰 가능 — 아래 표에서 충족 확인.
- **측정 방법 라벨 (AC-14/AC-6)**: **도구** = `tests/perf/paired-ab.py` · **표본** = 대상당 n 30 쌍
  (arm 별 warmup 2회는 측정에서 폐기) · **비교 지표** = 쌍차 median · 쌍차 p90 · p90 델타
  (단위 ms — csv 열 `diff_median` / `diff_p90` / `p90_delta`) · **계수 규칙** = §4 exec census
  계수 규칙(baseline 규칙 + 정정 규칙 병기).
- **wall-clock(실지연) 선언 (AC-5)**: 기록된 소요(ms)는 전부 **실지연(wall-clock)** 이다 —
  `time.perf_counter()` 기반 벽시계 경과라 프로세스 기동 비용과 **직렬화 대기**를 포함하며 CPU time 이 아니다.
  체인 wall 은 7종 **순차** 1회 통과 경과다.

## 3. Plane A 결과 (before `561da632d` → after `b71c0c04c`, n=30 쌍)

| 대상 | before median | after median | Δmedian | before p90 | after p90 | Δp90 | 개선/악화 쌍 | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cross-repo-gh-safety (대조) | 218.5 | 219.1 | **−0.3** | 281.8 | 247.2 | −34.6 | 15/15 | 0.622 |
| repo-confinement | 357.9 | 318.0 | **−37.8** | 370.1 | 398.7 | +28.6 | 26/4 | 0.0018 |
| git-branch-delete-merge-gate | 254.0 | 257.9 | +2.1 | 264.2 | 266.4 | +2.2 | 10/20 | 0.113 |
| worktree-location-guard | 385.4 | 342.1 | **−42.0** | 406.3 | 363.4 | −42.8 | 27/3 | 0.00015 |
| pretooluse-bash-description-inject | 885.6 | 280.9 | **−595.6** | 934.5 | 307.2 | −627.3 | 30/0 | 2e-06 |
| pretooluse-dev-process-capture (대조) | 312.8 | 311.0 | +0.5 | 331.9 | 325.6 | −6.3 | 14/16 | 0.607 |
| posttooluse-dev-process-capture (대조) | 311.2 | 310.5 | −0.3 | 319.4 | 325.7 | +6.3 | 18/12 | 0.607 |
| **CHAIN-seq7 (체인 순차 wall)** | **2845.2** | **2106.1** | **−751.9** | **2952.0** | **2176.6** | **−775.3** | **30/0** | **2e-06** |

- 체인 wall **−26.4%** (−751.9 ms), 30/30 쌍 전부 개선. 관측 max 3154 ms → 2212 ms.
- 대조군 3종 Δ ≤ |0.5| ms, p ≥ 0.6 → 측정계 편향 없음 (인과 귀속 성립).
- `git-branch-delete-merge-gate` +2.1 ms 는 미유의(p=0.11) — S6 은 gh 호출 경로에서만 발동하고 본 payload 는 비-delete 이므로 실경로 델타 0 이 기대치.
- `repo-confinement` p90 만 +28.6 ms 인 것은 tail 잡음 (median −37.8 · 26/4 개선 우세).
  중간 측정(S10 착지 전) 에서 이 훅은 **+5.6 ms (p=0.042)** 였고 이는 S7 G-6 정규화가 추가한
  `command -v python3` PATH 탐색 비용으로 귀속된다 — **정확성 수정의 선언된 대가**(성능 회귀 아님).

## 4. exec census 재계수 (AC-1)

| 훅 | before | after | 델타 근거 |
|---|---:|---:|---|
| cross-repo-gh-safety | 7 | 7 | 무변경 |
| repo-confinement | 5 | 4 | S10 `bash "${SCRIPT}"` fork 소멸 |
| git-branch-delete-merge-gate | 3 | 3 | 무변경 (S6 = 내부 예산 로직) |
| worktree-location-guard | 5 | 4 | S10 동상 |
| pretooluse-bash-description-inject | 9 | 4 | S4 (`python -c`×2 + kst bash fork + dirname + date 소멸) |
| pretooluse-dev-process-capture | 4 | 4 | 무변경 |
| posttooluse-dev-process-capture | 4 | 4 | 무변경 |
| **합계 (S1 baseline 계수 규칙)** | **37** | **30** | −7 |

**계수 규칙 불일치 정직 기록**: S1 baseline 의 정적 계수는 `dirname` exec 을 3곳 누락한다 —
`hooks/repo-confinement:47`+`scripts/check-repo-confinement.sh:17` 중 1개만 계상 /
`hooks/git-branch-delete-merge-gate:19` 미계상 / `hooks/worktree-location-guard:45`+`scripts/check-worktree-location-guard.sh:21` 중 1개만 계상.
정정 계수로는 **before 40 → after 33**. T-1b 판정은 **규칙-일관(baseline 규칙) 기준 30 ≤ 32 PASS** 로 하되,
정정 규칙을 채택할 경우 pin(≤32) 자체도 같은 규칙으로 재유도되어야 함(≤32 는 baseline 규칙 산물) — **계수 규칙 정합은 설계 회부 항목**.

**INV-S1 (subshell 비증가)**: S4 는 `$(...)` 서브셸 3개(python -c ×2 + kst fork)를 제거하고 신규 서브셸 0,
S10 은 fork 1개씩 제거 — 양 방향 모두 감소. 증가 site 0.

## 5. S10 (④a) 판별 실험 — 채택 근거

동일 provenance 트리(`git archive HEAD`) 3종으로 arm 편향 제거, n=30 쌍 paired ABAB.

| 변이 | 대상 | Δmedian | 개선/악화 쌍 | p (Wilcoxon) | 판정 |
|---|---|---:|---:|---:|---|
| `source` | repo-confinement | −46.7 | 28/2 | 2.5e-05 | 유의 |
| `source` | worktree-location-guard | −45.5 | 27/3 | 2.1e-04 | 유의 |
| `exec bash` | repo-confinement | −12.0 | 25/5 | 4.5e-03 | 유의하나 이득 1/4 |
| `exec bash` | worktree-location-guard | −10.1 | 23/7 | 6.7e-02 | **미유의** |

→ `source` 채택 (커밋 `b71c0c04c`). exit 전파(deny exit 2) 3-arm rc sanity 로 확인, `exec` 변이 폐기.

## 6. Plane B (실세션 Slow-log) — before 슬라이스 + after **pending**

| 항목 | before 창 | after 창 |
|---|---|---|
| 창 경계 (UTC) | 2026-08-13T03:39:48Z ~ 13:02:02Z | **pending** |
| Slow 이벤트 (PreToolUse·Bash) | 1207건 | **pending** |
| median / p90 / max | 15,682 / 47,750 / 129,152 ms | **pending** |
| N(>10s) / N(>60s) | 741 / 60 | **pending** |

- **after 창 미측정 선언**: 실세션 Slow-log 는 플러그인 **캐시 반영 이후**에만 유효하다
  (bump → `claude plugin update` → 다음 세션). 현 시점 캐시는 구 코드이므로 **측정 자체가 무효** →
  수치를 채우지 않는다 (허위 after 기입 금지 — §7.4.6 sentinel 규율).
- before 수치는 절단 임계 2,000 ms 를 넘긴 **생존자 분포**라 median/p90 이 실분포가 아니다
  (Plane B tail 정의역 붕괴 — CP §8.3 declare). 비율 지표(T-3a/T-3b)의 분모(창 내 총 Bash 호출 수)는
  before 창에 기록이 없어 **rate 산출 불가** → 두 축 모두 pending 사유가 2중(캐시 + 분모).

## 7. AC-21 축별 판정

| 축 | 기준 | 실측 | 판정 |
|---|---|---|---|
| T-1a | 체인 total 감소 ∧ inject ≥4 감소 | 37→30 (−7) ∧ inject 9→4 (−5) | **PASS** |
| T-1b | 체인 total ≤ 32 | 30 (baseline 규칙) / 33 (정정 규칙 — §4 회부) | **PASS (규칙-일관 기준)** |
| T-1c | INV-S1 subshell 비증가 | 감소만, 증가 0 | **PASS** |
| T-2c | Plane A 쌍차 median ≤ 0 | 체인 −751.9 (30/0, p=2e-06) | **PASS** |
| T-2d | Plane A 쌍차 p90 ≤ 0 | 체인 쌍차 p90 −610.9 / p90 델타 −775.3 | **PASS** |
| T-3a | slow-event 비율 r_after ≤ 0.5·r_before | after 창 미존재 + 분모 부재 | **pending** |
| T-3b | N(>10s)/1k calls ≥60% 감소 | 동상 | **pending** |
| T-3c | 관측 max ≤ Σ(동시 발화 훅 timeout)+마진 | Σ=105s (10+10+60+15+5+5) vs 관측 max 2.212s | **PASS (by construction)** |

**총평**: **Plane A 축 6개 전부 PASS, Plane B 축 2개 pending.** AC-21 은 AND 판정이므로
현 시점 최종 verdict = **미완(pending)** — Plane B after 창 확보(bump·캐시 반영·전용 세션) 후 재판정 대상.
(Plane A 통제면에서 인과는 확립: 체인 wall −26.4%, 30/30 쌍.)

**T-3c 부수 관측**: before 창 실세션에 N(>60s)=60건이 실재했다. 신 timeout 배선 하에서는 단일 훅 상한이
{1,5,10,15,30,60}s 이고 Bash 매칭 동시 발화 합이 105s 이므로, after 창에서 60s 초과가 잔존하면
**FAIL 이 아니라 재진단 트리거**(큐잉 가설 반증 경로) — CP §8.3 사전 선언 그대로.

## 8. SessionEnd `timeout: 1` sanity (AC-16 / §3.2 #22)

| 관측 | 값 |
|---|---|
| session-end 훅 완주 소요 (GC_DRY_RUN=1) | **2,255 ms** |
| `timeout 1` 부여 시 | 1,115 ms 시점 **kill (rc=124)** — 1s 예산이 실제로 절단함 |
| `last-run.epoch` | kill 후 **미갱신** (`1786644811` 불변) |
| catch-up 판정식 | age 10,377s > threshold 300s → **catch-up 발화 조건 충족(YES)** |
| 잔여 lock | 없음 (dry-run 경로는 lock 미취득) |

- 복구 3층 무손상 근거: `templates/scripts/check-worktree-stale.sh:358` `_gc_record_lastrun` 은
  **GC 스캔 완료 이후**에 위치 → 1s kill 은 이 지점에 도달할 수 없다 → last-run 이 stale 로 남고
  다음 SessionStart 의 `session-start-gc-catchup`(threshold 300s) 이 보상 발화한다.
- **정직 한계**: 위 실행은 `GC_DRY_RUN=1`(prune 0 보장) 경로였다. dry-run 은 lock·cooldown·last-run 기록을
  건너뛰므로 "kill 이 기록을 막았다"는 **코드 경로 + 소요시간 근거**이지 비-dry 실행의 직접 관측은 아니다
  (비-dry 1s kill 실험은 실 worktree prune 위험이 있어 미수행).

## 9. 한계·비이관 사항

1. Plane B after = pending (§6). A 개선 ⇏ B 개선 — 역할 분리 유지.
2. Defender 실시간 보호가 baseline 측정 창과 다름(ON) → **S1 baseline CSV 와의 직접 비교는 금지**,
   본 리포트의 판정은 전부 **동일 창 paired** 수치로만 수행했다.
3. exec census 계수 규칙 불일치(§4) — 설계 회부.
4. 병렬/순차 실행 모순(문서 vs 관측)은 본 리포트 범위 밖 (§8.8 판별 실험 소관). 체인 wall 은 순차 측정치.

**조건부 수치·비교쌍 유효성 선언**

- **−26.4% = Defender ON 조건부 수치** — 위 2번의 귀결이다. Defender OFF 창(S1 baseline)의 수치와
  직접 비교 금지이며, 이 값은 Defender ON 조건에서만 의미를 갖는다.
- **비교쌍 = 동일 창·동일 환경값에서만 유효** — 본 리포트의 모든 판정은 동일 창 안에서 인접 실행한
  paired(ABAB) 수치로만 수행했다. 창이 다르거나 환경값(Defender·부하)이 다른 쌍의 비교는 무효다.
