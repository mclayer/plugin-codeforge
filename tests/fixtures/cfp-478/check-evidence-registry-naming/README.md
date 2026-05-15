# CFP-478 fixture: check-evidence-registry-naming

## Description
Evidence registry naming convention

## Exit code contract
`0=pass,1=fail,2=error`

## Fixture type
`yaml_input`

## Files
- `input/` — sample input file(s) for regression test
- `expected/` — expected output snippet or exit code
- `README.md` — this file

## Test contract (CFP-478 AC-6)
The regression runner (`scripts/test-cfp-478-regression.sh`) verifies:
1. `scripts/check-evidence-registry-naming.sh` thin wrapper exists and references `scripts/lib/` SSOT
2. Python heredoc removed from shell wrapper
3. Corresponding `scripts/lib/*.py` exists

Full per-candidate golden file tests are run by `scripts/lib/test_cfp_478_regression.py`.
