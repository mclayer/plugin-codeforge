# CFP-2829 Backward-Sync Cutover Flag Guide

**Flag**: `CFP2829_BACKWARD_SYNC_ENABLED`

**Purpose**: Gate backward-sync engine activation. When OFF (default), existing forward-sync path operates unchanged.

## Flag Semantics

| Flag State | Backward Engine | Forward Path | Description |
|---|---|---|---|
| **OFF** (default, `0` or unset) | Disabled | Active (unchanged) | Production baseline — no backward-sync |
| **ON** (`1`) | Active (flag-gated) | Active (unchanged) | S2 capability live — backward PRs proposed, forward unchanged |

**Design**: additive (flag-ON does not disable forward), immutable (forward never blocked).

## Storage Location

**Recommendation (§5.5.B #4 design confirmation)**: GitHub repository variable

### Option A: GitHub Repository Variable (Recommended)

**Pros**:
- Visible in repo settings UI
- Per-branch capable (if using `if:` conditions)
- Auditable in GitHub audit log
- Easy per-tenant override (e.g., mclayer vs consumer)

**Setup** (Orchestrator / Admin):

1. Navigate to repo Settings → Variables → Repository variables
2. Add new variable:
   - **Name**: `CFP2829_BACKWARD_SYNC_ENABLED`
   - **Value**: `0` (OFF by default)
   - **Scope**: Available to all workflows

3. In workflow YAML, reference as:
   ```yaml
   env:
     CFP2829_BACKWARD_SYNC_ENABLED: ${{ vars.CFP2829_BACKWARD_SYNC_ENABLED }}
   ```

### Option B: Environment Variable (Script-Only)

**Pros**:
- No repo mutation
- CLI-friendly for local testing

**Setup**:

```bash
export CFP2829_BACKWARD_SYNC_ENABLED=1
python scripts/confluence_backward_sync.py --detect
```

### Option C: project.yaml (Rejected)

**Rationale**: 
- Lint exposure (`doc schema check` would parse this key)
- Over-design for feature flag
- Prefer external configuration (GH variable) over code

## Migration Path (Flag: OFF → ON)

**Phase 1 (Current S2)**: Flag OFF (default)
- Forward-sync active
- Backward engine built but dormant
- RC-1 oracle online, anchor-verify ready
- No new PRs generated

**Phase 2 (S3 / S4)**:
- Set flag ON via GH variable
- Backward agent spawned for detected changes
- PR proposals begin
- CODEOWNERS review gates INV-A compliance

## Script Usage Patterns

### Inline Flag Check (confluence_backward_sync.py)

```python
backward_enabled = os.environ.get("CFP2829_BACKWARD_SYNC_ENABLED", "0") == "1"

if not backward_enabled:
    logger.info("Backward-sync disabled (flag OFF)")
    sys.exit(0)  # Early exit, forward unaffected
```

**Precedent**: `confluence_forward_sync.py` L102-105 secret-presence pattern

### Measurement Harness

```bash
# Offline measurement (works regardless of flag)
python scripts/confluence_backward_measure.py --all --mock

# Actual measurement (flag-independent, creds-gated)
CFP2829_TEST_PAGE_ID=12345 python scripts/confluence_backward_measure.py --all
```

## Workflow Integration

### Forward-Sync Workflow (unchanged)

`.github/workflows/confluence-forward-sync.yml` — continues to run on push, **flag-agnostic**.

### Backward-Sync Workflow (future, S3+)

(Pseudocode — actual implementation S3 scope)

```yaml
name: confluence-backward-sync

on:
  schedule:
    - cron: '0 * * * *'  # Hourly polling (configurable)
  workflow_dispatch:

jobs:
  backward-detect-and-propose:
    runs-on: ubuntu-latest
    if: ${{ vars.CFP2829_BACKWARD_SYNC_ENABLED == '1' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Detect Confluence changes
        run: python scripts/confluence_backward_sync.py --detect
      
      - name: Propose PRs
        run: python scripts/confluence_backward_sync.py --propose
```

**Key**: `if: ${{ vars.CFP2829_BACKWARD_SYNC_ENABLED == '1' }}` gates entire job.

## Testing

### Test Flag Disabled (Current S2)

```bash
# Simulate flag OFF (default)
unset CFP2829_BACKWARD_SYNC_ENABLED
python scripts/confluence_backward_sync.py --detect
# Expect: early exit, forward-sync mock continues
```

### Test Flag Enabled (Readiness)

```bash
# Simulate flag ON (future)
export CFP2829_BACKWARD_SYNC_ENABLED=1
python scripts/confluence_backward_sync.py --detect --mock
# Expect: polling mock runs, no real API calls (offline)
```

## Operational Notes

### Disable Backward-Sync (Emergency)

If backward-sync causes issues:

1. Set flag OFF (immediately):
   ```bash
   gh variable set CFP2829_BACKWARD_SYNC_ENABLED -b value:0
   ```

2. In-flight PRs:
   - Auto-created PRs remain (git PR objects, not workflow-managed)
   - Manual close/abandon as needed
   - Flag OFF stops new PR generation

3. Resume:
   - Set flag ON, re-run workflow
   - Polling resumes from last known version

### Audit Trail

- GitHub variable changes logged in org audit log
- Each backward-sync PR has `[confluence-backward-substrate]` trailer (audit marker)
- Commit metadata includes source page URL + editor (E-2 enrichment)

## Related Flags

| Flag | Purpose | Scope |
|---|---|---|
| `CFP2829_BACKWARD_SYNC_ENABLED` | Gate backward-sync engine | S2+ |
| `CFP2829_TEST_PAGE_ID` | Measurement test page | Harness only |
| `CFP2829_MEASURE_SKIP_WRITE` | Skip property writes in measurement | Harness only |
| `CFP1495_MOCK_MODE` | Offline fixture mode | Harness + tests |

## Security Considerations

- **Flag value visibility**: Public (GitHub UI visible to all with repo access)
  - Rationale: ON/OFF state is not sensitive
- **Credentials**: Separate (GitHub Actions secrets)
  - Token/email loaded from GH secret, not this flag
- **Audit**: Flag changes in org audit log (immutable)

## FAQ

**Q: Can we use feature branch + flag?**
A: Yes — CI can check branch name and override flag for feature branches:
```yaml
if: ${{ (github.ref_name == 'main' && vars.CFP2829_BACKWARD_SYNC_ENABLED == '1') || (github.ref_name == 'cfp-2829-*') }}
```

**Q: What if flag is set but credentials missing?**
A: Backward-sync fails gracefully (no PR generated). Logs indicate missing creds.

**Q: Can we schedule backward polling independent of flag?**
A: Yes — polling job can run always, PRs only generated if flag ON.

**Q: Who can toggle the flag?**
A: Repo admins (GitHub variable permissions). Recommend CODEOWNERS sync (ADR-103 §결정2).

## References

- **Change Plan**: CFP-2829.md §3.7 (cutover flag design)
- **Forward Precedent**: `confluence_forward_sync.py` L102-105 (secrets_present pattern)
- **ADR-103 §결정7-E**: default-off flag semantics
