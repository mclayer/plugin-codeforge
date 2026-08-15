# CFP-2978 Fixture Manifest

## Blob SHA Verification (Immutable References)

### Wrapper Template (origin/main)
- **File**: `.github/workflows/parallel-work-sentinel-check.yml`
- **Blob SHA-1**: `8eeda0aa2f0ebdbd74ccb456c1786253a890a2c8`
- **Size**: 7307 bytes
- **Verified by**: git rev-parse origin/main -- path (2026-08-15 KST 11:31:00)

### Consumer 4-Repo Workflows

#### mctrader
- **File**: `.github/workflows/parallel-work-sentinel-check.yml`
- **Size**: 7676 bytes
- **Verified**: Present locally at `/c/workspace/mclayer/mctrader/.github/workflows/parallel-work-sentinel-check.yml`
- **Blob notes**: Contains concurrency block with MTD-1325 expression (line 37-39)

#### mctrader-backtest
- **File**: `.github/workflows/parallel-work-sentinel-check.yml`
- **Size**: 6975 bytes
- **Verified**: Present locally at `/c/workspace/mclayer/mctrader-backtest/.github/workflows/parallel-work-sentinel-check.yml`

#### mctrader-market  
- **File**: `.github/workflows/parallel-work-sentinel-check.yml`
- **Size**: 7028 bytes
- **Verified**: Present locally at `/c/workspace/mclayer/mctrader-market/.github/workflows/parallel-work-sentinel-check.yml`
- **Blob notes**: Differs from wrapper — job2 has custom `runs-on: ${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '["ubuntu-latest"]') }}` (line 104)

#### mctrader-engine
- **File**: `.github/workflows/parallel-work-sentinel-check.yml`
- **Size**: 6975 bytes
- **Verified**: Present locally at `/c/workspace/mclayer/mctrader-engine/.github/workflows/parallel-work-sentinel-check.yml`

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
- File sizes and locations: Confirmed ✓
- Consumer file presence: 4/4 repos verified ✓
