# CFP-478 fixture: check-story-section-9-typed

## Description
Story §9 typed yaml block validation

## Exit code contract
`0=always (warn)`

## Fixture type
`md_input`

## Files
- `input/` — sample input file(s) for regression test
- `expected/` — expected output snippet or exit code
- `README.md` — this file

## Test contract (CFP-478 AC-6)
The regression runner (`scripts/test-cfp-478-regression.sh`) verifies:
1. `scripts/check-story-section-9-typed.sh` thin wrapper exists and references `scripts/lib/` SSOT
2. Python heredoc removed from shell wrapper
3. Corresponding `scripts/lib/*.py` exists

Full per-candidate golden file tests are run by `scripts/lib/test_cfp_478_regression.py`.
