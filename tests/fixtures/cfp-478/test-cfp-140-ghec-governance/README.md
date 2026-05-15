# CFP-478 fixture: test-cfp-140-ghec-governance

## Description
GHEC governance e2e fixtures

## Exit code contract
`0=pass,1=fail`

## Fixture type
`json_input`

## Files
- `input/` — sample input file(s) for regression test
- `expected/` — expected output snippet or exit code
- `README.md` — this file

## Test contract (CFP-478 AC-6)
The regression runner (`scripts/test-cfp-478-regression.sh`) verifies:
1. `scripts/test-cfp-140-ghec-governance.sh` thin wrapper exists and references `scripts/lib/` SSOT
2. Python heredoc removed from shell wrapper
3. Corresponding `scripts/lib/*.py` exists

Full per-candidate golden file tests are run by `scripts/lib/test_cfp_478_regression.py`.
