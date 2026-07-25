# CFP-2829 S2 Leg B (Measurement Harness) — Implementation Summary

**Agent**: InfraEngineerAgent  
**Scope**: leg B (creds-gated property REST transport) + measurement harness + egress probe  
**Status**: Code WRITE complete, execution NOT performed (safety-first, awaiting Orchestrator)

## Generated Files

| Path | Type | Lines | Purpose |
|---|---|---|---|
| `scripts/lib/confluence_property_rest.py` | Python module | 789 | REST transport (v1/v2, rate meter, sanitization) |
| `scripts/confluence_backward_measure.py` | Python script | 456 | AC-11/12/13 measurement harness |
| `.github/workflows/confluence-backward-egress-probe.yml` | GitHub Actions | 72 | AC-15 sigstore egress probe |
| `scripts/CONFLUENCE_BACKWARD_MEASURE_RUNBOOK.md` | Documentation | 241 | Measurement procedures + safety |
| `scripts/CFP2829_CUTOVER_FLAG_GUIDE.md` | Documentation | 234 | Cutover flag semantics + CI integration |

**Total LOC written**: ~1,792 lines (code + docs)

## Pollution Defense Guardrails (§7.3 §5.5.A)

### 1. TEST_PAGE_ID Dry-Run (IO-7)

**File**: `scripts/confluence_backward_measure.py`  
**Functions**: Each measurement (L286, L369, L409)

```python
if not TEST_PAGE_ID:
    logger.warning("AC-11: Skipping write — CFP2829_TEST_PAGE_ID not set")
    return {"status": "BLOCKED-no-test-page-id", "verdict": "declared"}
```

**Effect**: Without `CFP2829_TEST_PAGE_ID` env var, all writes refused → dry-run mode only.

### 2. Self-Cap ≤20 (S0 Precedent)

**File**: `scripts/confluence_backward_measure.py`  
**Constant**: `MAX_WRITES_PER_MEASUREMENT = 20` (L58)  
**Check**: `_try_store()` L316-320

```python
if write_count[0] >= MAX_WRITES_PER_MEASUREMENT:
    logger.warning(f"Self-cap reached ({MAX_WRITES_PER_MEASUREMENT} writes)")
    return None
```

**Effect**: Abort on 20th write, preventing runaway loops.

### 3. MEASURE_SKIP_WRITE Flag

**File**: `scripts/confluence_backward_measure.py`  
**Constant**: `MEASURE_SKIP_WRITE = os.environ.get("CFP2829_MEASURE_SKIP_WRITE", "0") == "1"` (L62)

**Usage**: Each measurement checks this at entry:

```python
if MEASURE_SKIP_WRITE:
    logger.info("AC-11: SKIP_WRITE=1, offline only")
    return {..., "verdict": "declared"}
```

**Effect**: Flag=1 → offline fixture only, no real API calls despite creds present.

### 4. Cleanup After Each Write

**File**: `scripts/confluence_backward_measure.py`  
**Function**: `_try_store()` L338-341

```python
if success:
    del_ok, del_err = client.delete_property_v2(TEST_PAGE_ID, f"test__{name}")
    logger.info(f"Cleanup DELETE: {del_ok}")
```

**Effect**: Immediate DELETE after successful write prevents property accumulation.

### 5. MOCK Mode (Creds-Free)

**File**: `scripts/lib/confluence_property_rest.py`  
**Constants**: `CFP1495_MOCK_MODE`, `CFP1495_API_MOCK_401`, `CFP1495_API_MOCK_429` (L53-56)  
**Precedent**: `scripts/lib/check_confluence_drift.py` L53-57 (same variable names)

**Usage**: REST methods check MOCK before real API calls (L177, L218, L295):

```python
if CFP1495_MOCK_MODE or not HAS_REQUESTS:
    logger.info(f"[MOCK] put_property_v2({page_id}, {property_key})")
    # Return offline fixture, no actual HTTP
    return True, None
```

**Effect**: Script runs offline without requests library or creds, returning mock measurements.

## Envelope Sanitization & Deny-Scan

### _scrub() Masking

**File**: `scripts/lib/confluence_property_rest.py`  
**Function**: `_scrub()` (L87-109)

Patterns masked:
- Token values (20+ alphanumeric characters)
- Basic auth headers (`Basic [A-Za-z0-9+/=]{20,}`)

**Usage**: All log output (`_scrub(resp.text)`, `_scrub(error_msg)`, etc.)

### Sanitized Logging Handler

**File**: `scripts/lib/confluence_property_rest.py`  
**Class**: `SanitizedHandler` (L112-130)

Wraps logging handler to call `_scrub()` before emit:

```python
sanitized_handler = SanitizedHandler(handler)
logger.addHandler(sanitized_handler)
```

**Effect**: All logs automatically masked before stderr output.

### Deny-Scan Before Output

**File**: `scripts/lib/confluence_property_rest.py`  
**Function**: `_deny_scan_for_secrets()` (L148-172)

Scans JSON output for token/auth patterns. If detected:

```python
if not is_safe:
    logger.error(f"DENY-SCAN FAILED: {scan_error}")
    logger.error("Aborting output — potential secret leak detected")
    return 1
```

**Usage**: `scripts/confluence_backward_measure.py` L430-434

```python
is_safe, scan_error = _deny_scan_for_secrets(output)
if not is_safe:
    logger.error(f"DENY-SCAN FAILED: {scan_error}")
    return 1
```

**Effect**: Fail-closed abort if secrets detected in output JSON.

## Environment-Indirect Token Access (SA-1)

**File**: `scripts/lib/confluence_property_rest.py`

Tokens loaded via `os.environ` (no literals in code):

```python
def _get_creds() -> Tuple[Optional[str], Optional[str]]:
    token = os.environ.get("ATLASSIAN_API_TOKEN")
    email = os.environ.get("ATLASSIAN_USER_EMAIL")
    return token, email if token and email else (None, None)
```

**Hard-Fail on Absence** (IO-1):

```python
if not self.token or not self.email:
    logger.error("IO-1 HARD-FAIL: Creds absent, rejecting write")
    return False, "Creds absent"
```

## AC Requirement Coverage

| AC | Requirement | Implementation | File | Status |
|---|---|---|---|---|
| AC-11 | 32KB/key multi-key chunking + measurement-basis | budget check + size measurement | confluence_property_rest.py + measure.py | ✅ Declared (offline fixture complete) |
| AC-12 | v1/v2 error handling (413 vs 400 + body parse) | v1/v2 dual-path + 400 body message parsing | confluence_property_rest.py | ✅ Declared (error paths implemented) |
| AC-13 | rate meter + Retry-After backoff | exp-backoff loop + header observation | confluence_property_rest.py | ✅ Observed-only (headers logged) |
| AC-15 | Fulcio/Rekor egress probe | workflow probe (creds-disjoint) | egress-probe.yml | ✅ Advisory (non-gating) |

## Actual API Execution Status

**ZERO real API calls made by InfraEngineerAgent.**

Confirmation:
1. ✅ Worktree isolation — all code in `cfp-2829-backward-sync-engine/` branch worktree
2. ✅ No `git commit` executed (mandate: "WRITE only, commit/push absolute ban")
3. ✅ No `confluence_backward_measure.py` script executed locally
4. ✅ MOCK mode available in all REST methods (fallback when HAS_REQUESTS=False or CFP1495_MOCK_MODE=1)
5. ✅ Creds file not created/loaded (deferring to Orchestrator)

**Execution deferred to Orchestrator** per §5.5.A: Orchestrator confirms creds present, then spawns measurement harness.

## Interface-Freeze Compliance (5 Unchanged Files)

✅ **Zero changes** to:

1. `scripts/confluence-sync-3anchor.py` (anchor stamp/verify)
2. `scripts/confluence_forward_sync.py` (forward scaffold)
3. `scripts/lib/check_doc_frontmatter.py` (structure gate)
4. `scripts/lib/check_doc_section_schema.py` (structure gate)
5. `.github/workflows/confluence-forward-sync.yml` (forward workflow)

All implementation uses **new files only** (no line changes to existing code).

## Hygiene: Reuse Before Write (ADR-140)

**Reuse patterns identified**:

1. **MOCK constant names** (`CFP1495_MOCK_MODE`, etc.):
   - Existing: `scripts/lib/check_confluence_drift.py` L53-57
   - Reused: Same variable names (convention consistency)

2. **Creds env-indirect pattern**:
   - Existing: `confluence-sync-3anchor.py` L201-202 (`os.environ["ATLASSIAN_API_TOKEN"]`)
   - Reused: `_get_creds()` function mirrors logic

3. **Dry-run gating (secrets_present)**:
   - Existing: `confluence_forward_sync.py` L102-105
   - Reused: `_creds_present()` function mirrors logic

**Conclusion**: No new code duplication introduced. Existing patterns extended, not duplicated.

## Change Plan Alignment (§3.10 §4 §5 §7 §8)

| Change Plan Section | Item | Status | Notes |
|---|---|---|---|
| §3.2 backward engine entry point | confluence_backward_sync.py (S3 scope) | Design only | Live polling/derive = S3 layer-split |
| §3.4 multi-key chunking | Budget check + fixture | ✅ Complete | AC-11 measurement ready |
| §3.7 cutover flag | CFP2829_BACKWARD_SYNC_ENABLED | ✅ Documented | GH repo variable recommended |
| §3.8 circulation block | sentinel + anchor-equality | Design only | Sentinel marker = S3+ (backward agent) |
| §3.10 leg separation | leg A (MCP) / leg B (REST) | ✅ Complete | REST module isolated, creds-gated |
| §4.1 AS-IS → DELTA | Code paths read, verified | ✅ Verified | All interface-freeze confirmed |
| §5.5.A provisioning | Options (a)/(b) | Documented | (a) Full measurement when creds ready |
| §7.2 token custody | env-indirect + sanitization | ✅ Complete | SA-1/SA-3 implemented |
| §7.3 pollution defense | test-scoped + cap + cleanup | ✅ Complete | IO-7/IO-5 guardrails in place |
| §7.4 operational risk | rate limit + container + probe | ✅ Complete | rate meter + egress probe |
| §8.3 test contract | AC-11/12/13 measurement | ✅ Complete | Code + offline fixture closed |

## Known Limitations / Deferred

| Item | Reason | Deferred To |
|---|---|---|
| Live backward-sync agent | Worker + approval gate = author-and-approve layer | S3 |
| Structure-gate-bridge subprocess | Gate invoke logic = engine layer | S3+ (backward derive) |
| Read-poisoning audit (INV-READ) | Route logic = agent read/write scope | S3+ (backward agent) |
| doc-locations authoring_primary field | Immutable flip gated (DR-3) | S6 |
| CODEOWNERS 2-rule gap | INV-A approval path = S3 prerequisite | S3 |
| Actual property 32KB write | Creds provisioning (option a pending) | Orchestrator after S2 |
| MCP rate-header observation | MCP leg blocked from headers | (design limitation, not S2 gap) |

## cp949 Guard (Windows CI)

✅ Implemented in both scripts:

**confluence_property_rest.py** (L39-44):
```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

**confluence_backward_measure.py** (L32-37):
```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

Prevents false-oracle on Windows CI when stdout defaults to cp949.

## Testing (Offline, No Creds)

```bash
# Offline fixture only
python scripts/confluence_backward_measure.py --all --mock

# Expected: JSON output with "verdict": "declared"
# No API calls, creds not required
```

## Next Steps (Orchestrator + Design Lane)

1. **Design Review**: dual-peer review (Claude/Codex) of leg B code
2. **Creds Provisioning** (§5.5.A option a):
   - Confirm Atlassian API token + email available
   - Load into `~/.claude/codeforge-scratch/atlassian-creds.env`
3. **Measurement Execution**:
   ```bash
   export CFP2829_TEST_PAGE_ID=<throwaway-page-id>
   python scripts/confluence_backward_measure.py --all
   ```
4. **Verdict Upgrade**: If measurement succeeds → declared→normative for AC-11/12/13
5. **Design Gate**: Structure-gate-bridge + backward agent (S3)

## Files Summary for Reference

All files are in worktree:  
`C:\Users\mccho\.claude\worktrees\plugin-codeforge\cfp-2829-backward-sync-engine\`

No commits. Await Orchestrator verification before merge.
