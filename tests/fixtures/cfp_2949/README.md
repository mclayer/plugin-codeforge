# CFP-2949 Test Fixtures

## AC-1 Live Measurement Evidence

**Status**: Blocked — Claude Desktop app not installed in test environment.

**Evidence Location**: `live-run-<run_id>/` (would contain):
- `manifest.json` — session metadata with `orchestrator_session_closed_at`, `run_started_at`, `landing_ref.comment_id`
- `report-body.md` — GitHub issue comment body (append log)
- `README.md` — run procedure documentation

**Collection Procedure** (when Claude Desktop is available):
1. Start Claude Desktop application
2. Configure scheduled task to run daily via native OS scheduler (launchd/Task Scheduler)
3. Run scheduled task once manually: `python scripts/lib/scheduled_task_reconcile.py --repo-root . --channel owner/repo#N --task-name daily-gc`
4. Capture output directory structure and store as fixture
5. Record session closure timestamp in manifest for assertion `orchestrator_session_closed_at < run_started_at`

## Fuzz Corpus

**File**: `fuzz-corpus/paths.txt`

7 input surface classes with fixed seed 2949:
- UNC paths (`\\?\` and `\\server\share`)
- Unicode (NFC/NFD, combining, surrogate pairs)
- Embedded username
- Drive letters
- Symlink traversal
- Length 260+
- Control characters

Deterministic reproduction: `random.Random(2949)` seed in test.

## AC-1 Measurement Declaration

**File**: `ac1-measurement-declaration.json`

Declares `measured: false` due to missing Claude Desktop in test environment.

```json
{
  "ac": "AC-1",
  "measured": false,
  "reason": "Claude Desktop not installed — operator action required",
  "as_of": "2026-08-13T12:40:45+09:00",
  "blocking_precondition": "Install Claude Desktop + run scheduled task once"
}
```

**Important**: This is an honest declaration that AC-1 is not measurable in current environment.
Tests with `@pytest.mark.requires_golden` will fail (skip is forbidden) until evidence is collected.
