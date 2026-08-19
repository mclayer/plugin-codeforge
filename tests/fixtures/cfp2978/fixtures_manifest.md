# CFP-2978 Fixture Manifest

## Blob SHA Verification (Immutable References)

### Wrapper Template (origin/main)
- **File**: `.github/workflows/parallel-work-sentinel-check.yml`
- **Blob SHA-1**: `8eeda0aa2f0ebdbd74ccb456c1786253a890a2c8`
- **Size**: 7307 bytes
- **Verified by**: git rev-parse origin/main -- path (2026-08-15 KST 11:31:00)

### Consumer 4-Repo Workflows — ★세대 = consumer **HEAD** (post-backfill)

**★구현 FIX iter 1 재스냅샷 (2026-08-15)**: 초판 fixture 4건은 consumer **origin/main = PRE-backfill** 세대였다. 즉 **오라클이 본 Story 가 바꾸는 산출물을 보지 않았다**. 4건 전부 consumer PR head(`cfp-2978-sentinel-propagation`) blob 으로 재스냅샷했다.

또한 초판 기재 size 4건이 **전건 off-by-one**(7676/6975/7028/6975 vs 당시 실측 7677/6976/7029/6976)이라 재현이 불가능했다 — 아래는 **재스냅샷 후 실측값**이다.

| repo | consumer HEAD blob SHA-1 | size (B) | fixture 파일 |
|---|---|---|---|
| mctrader | `8868b4478f027a3327c7b83e8c1ae454c911db0d` | 7644 | `mctrader-sentinel.yml` |
| mctrader-backtest | `a945b757f11d05bcd521e38a6527a139c65b6d41` | 6943 | `mctrader-backtest.yml` |
| mctrader-market | `a72ebb6d262863420ac21b1e1458549d24ae0057` | 6996 | `mctrader-market.yml` |
| mctrader-engine | `a945b757f11d05bcd521e38a6527a139c65b6d41` | 6943 | `mctrader-engine.yml` |

- **획득**: `gh api "repos/mclayer/<repo>/contents/.github/workflows/parallel-work-sentinel-check.yml?ref=cfp-2978-sentinel-propagation"`
- **검증**: 각 fixture 에 `git hash-object -t blob --no-filters` → 위 SHA 와 **4/4 일치** (byte-exact)
- **세대 확인**: `STORY_KEY_PREFIX="CFP"` 잔존 = **4/4 전건 0** (PRE 세대에는 있었다)
- backtest 와 engine 은 blob 이 **동일**하다 (내용 일치)
- market 만 job2 에 로컬 개조 `runs-on: ${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '["ubuntu-latest"]') }}` 보유 (E8 판정 대상)

**★재스냅샷의 파급 = shape verdict 불변 (정직 기재)**: 재스냅샷 후 `test_cfp2978_workflow_shape.py` = **61 passed** 로 변동 0. 제거된 `STORY_KEY_PREFIX="CFP"` 가 YAML `env:` 키가 아니라 **`run:` 블록 안 셸 대입**이라 W-13 의 `env_keys` 정의역 **밖**이기 때문이다 (`PIN_ENV_KEYS` = workflow `SENTINEL_TIER` + run step `PR_TITLE`/`GH_TOKEN`). 이는 **AC-1b 가 이미 declared 한 공백**("shell 대입 채널 … 본 PR 미배치")이지 신규 결함이 아니다.
⇒ 본 재스냅샷이 고친 것은 **속성이 아니라 증거 사슬**이다. "파급 0 = 문제 없음"으로 읽지 말 것.

**★임박 false-RED 위험 (관찰됨·본 Story 범위 밖)**: Change Plan L118 이 인용하는 `reconcile-overlay.sh` 는 `.github/workflows` 를 **wholesale cp** 한다. 다음 reconcile 이 현 wrapper template(job2 **6 step**)을 consumer 로 밀면, fixture(job2 **3 step**) 기준의 `PIN_STEP_IF`·`PIN_STEP_SHELL`·step 앵커가 **mutant 검출과 무관한 이유로 RED** 가 된다. 그 RED 를 오라클 결함으로 오독하지 말 것.

### Vendor Fixture — §8.3 D-2 구세대 대조군

| 파일 | blob SHA-1 | size (B) | 출처 · 용도 |
|---|---|---|---|
| `sentinel-old-07d1127a.py.txt` | `07d1127a021280f49dc3b66ef7c848cd59dccea3` | 17814 | wrapper 역사 blob (CFP-2451 consumer 동결 세대). §8.3 **D-2** 구세대 대조군 |

- **왜 벤더링했나**: `.github/workflows/parallel-work-sentinel-check.yml` 의 `actions/checkout` 이 `fetch-depth` 미지정 = **depth 1 shallow** 라 역사 blob 이 CI 에 **없다**. `git cat-file` 로 읽으면 born-broken RED 가 된다.
- **무결성 leg**: `test_consumer_asset_currency.py` 가 `git hash-object -t blob --no-filters` 로 위 SHA 동일성을 assert 한다 (fixture 훼손 시 즉시 RED, skip 없음).
- 대응 신세대 = `scripts/lib/check_parallel_work_sentinel.py` 현재 내용 = blob `c372d0521db5d996ea9288bd362b83486e1e2553` (35718 B, `HEAD` = `origin/main`) — 벤더링 불요.

## Pin Literals (AC-10 Elements)

### PIN_MCTRADER_GROUP
**Value**: `${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.event.pull_request.number || github.run_id }}`

**Location**: mctrader/.github/workflows/parallel-work-sentinel-check.yml line 38 (`concurrency.group`)

**Immutable ref**: Direct read from local file at `/c/workspace/mclayer/mctrader/.github/workflows/parallel-work-sentinel-check.yml`

**Note**: This is the actual MTD-1325 form, differs from wrapper template which has `github.ref` instead of `github.run_id`

### CANON_RUNS_ON (Template job1)
**Value**: `${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '["ubuntu-latest"]') }}`

**Location**: wrapper template `.github/workflows/parallel-work-sentinel-check.yml` line 53 (`jobs.parallel-work-sentinel.runs-on`)

**Immutable ref**: Blob `8eeda0aa2f0ebdbd74ccb456c1786253a890a2c8`

## AC-10 Preservation Elements Reference

See Change Plan §8.A for full E1-E8 element definitions. Fixture values enable:

- **E1**: top-level `concurrency` existence check
- **E2**: mctrader `group == PIN_MCTRADER_GROUP` (string equality, NOT regex/substring)
- **E3**: wrapper group expression (template) **absent** from mctrader (positive + NOT AND)
- **E4**: mctrader `jobs.*.concurrency` absent (0 job-level keys)
- **E5**: mctrader `timeout-minutes: 10` exactly **2 occurrences** at job-level (`parallel-work-sentinel` + `parallel-work-sentinel-test`)
- **E6**: backtest/engine/market top-level `concurrency` **absent** (0 keys)
- **E7**: backtest/engine/market `jobs.*.concurrency` **absent** (0 keys)
- **E8**: market job2 `runs-on == ${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || ... }}` (custom value, verified line 104)

## Verification Inventory

- PIN_MCTRADER_GROUP: Extracted from mctrader local file ✓
- CANON_RUNS_ON: Extracted from wrapper template blob ✓
- Consumer HEAD blob SHA 4건 + 실측 size: git hash-object 4/4 일치 ✓ (구 off-by-one 기재 정정)
- Vendor fixture sentinel-old-07d1127a: blob SHA 자기검증 leg 보유 ✓
- Consumer file presence: 4/4 repos verified ✓ (세대 = consumer HEAD, PRE 아님)
