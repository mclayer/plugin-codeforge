# Confluence Backward-Sync Measurement Runbook

**Script**: `confluence_backward_measure.py`

**Purpose**: Measure real-world Confluence content-property behavior (AC-11/AC-12/AC-13) for backward-sync engine validation.

## Safety-First Approach

This measurement harness **writes to Confluence** using basic-auth credentials. To prevent accidental production pollution, follow these precautions:

### Prerequisites

1. **Dedicated throwaway test page** in mclayer.atlassian.net
   - Create manually via Confluence UI
   - Note the page ID (visible in URL: `/wiki/pages/viewpage.action?pageId=12345`)
   - This page will be used for all measurement writes

2. **Credentials file** (`~/.claude/codeforge-scratch/atlassian-creds.env`)
   - Create locally (NOT in repo)
   - Content:
     ```
     ATLASSIAN_API_TOKEN=<your-token>
     ATLASSIAN_USER_EMAIL=<your-email>
     ```
   - Never commit to git

3. **Environment variable** to gate actual writes
   - `export CFP2829_TEST_PAGE_ID=<throwaway-page-id>`
   - Without this, script will refuse to write

## Running Measurements

### Offline Mode (No Creds)

Run all measurements with mock data (offline, no API calls):

```bash
python scripts/confluence_backward_measure.py --all --mock
```

Output:
- AC-11: Mock size measurements (1KB, 10KB, 28KB)
- AC-12: Mock error code expectations (v1=413, v2=400)
- AC-13: Mock rate-limit header inventory

**Verdict**: `declared` (code + offline fixture, no real API)

### Measurement Mode (With Creds)

Set environment, then run:

```bash
export CFP2829_TEST_PAGE_ID=<your-test-page-id>
python scripts/confluence_backward_measure.py --all
```

**Automatic Cleanup**:
- After each successful write, script deletes the property immediately
- This prevents accumulation of test properties

**Output JSON**:
- `status`: `measured`, `partial`, `creds-absent`, etc.
- `measurements`: AC-11/12/13 results
- `verdict`: `normative` (creds OK + writes succeeded) or `declared` (offline/blocked)

**Expected Results**:

| Measurement | Expected Output |
|---|---|
| AC-11 Size Budget | `utf8_bytes`, `ascii_bytes`, delta showing `ensure_ascii=False` saves ~50% for Korean text |
| AC-12 Error Codes | Oversize 31KB write → error code (413 if v1, 400 if v2), message parsing confirmed |
| AC-13 Rate Limits | Observed headers (Retry-After, Beta-RateLimit-*) logged during writes |

### Skip-Write Mode (Creds Present, No Writes)

Test integration without touching Confluence:

```bash
export CFP2829_TEST_PAGE_ID=<any-value>
export CFP2829_MEASURE_SKIP_WRITE=1
python scripts/confluence_backward_measure.py --all
```

**Use case**: Verify script logic + offline fixtures without creds.

**Verdict**: `declared` (code validated, no actual measurement)

## Selective Measurements

Run individual AC suites:

```bash
# AC-11 size budget only
python scripts/confluence_backward_measure.py --measure-size-budget

# AC-12 error codes only
python scripts/confluence_backward_measure.py --measure-error-codes

# AC-13 rate limits only
python scripts/confluence_backward_measure.py --measure-rate-limits
```

## Safety Guardrails

### Write Cap (Self-Imposed)

- **Max 20 writes per harness run** (S0 spike precedent)
- Script aborts if cap exceeded
- Each write is immediately followed by cleanup (DELETE)

### Test Page Isolation

- `CFP2829_TEST_PAGE_ID` (REQUIRED) prevents accidental writes to production docs
- Without this env var, all write operations are refused
- Only throwaway page can be touched

### Creds Validation

- `ATLASSIAN_API_TOKEN` + `ATLASSIAN_USER_EMAIL` required for real writes
- Env-indirect access only (no literals in code)
- Absence triggers graceful fallback to offline fixture

### Deny-Scan

- Before outputting results, script scans JSON for token/auth leaks
- If leaked secrets detected → abort with error
- Sanitization (`_scrub`) masks Basic auth headers in all logs

## Manual Cleanup (If Needed)

If script is interrupted and properties are left orphaned:

1. Go to test page in Confluence UI
2. List properties to identify IDs (v2 API uses property-id, not key):
   ```bash
   curl -X GET \
     "https://mclayer.atlassian.net/wiki/api/v2/pages/<page-id>/properties?key=codeforge.sync.canonical" \
     -H "Authorization: Basic $(echo -n 'email:token' | base64)"
   ```
3. Extract property-id from response, then delete by ID:
   ```bash
   curl -X DELETE \
     "https://mclayer.atlassian.net/wiki/api/v2/pages/<page-id>/properties/<property-id>" \
     -H "Authorization: Basic $(echo -n 'email:token' | base64)"
   ```
   (Repeat for each property-id in the results above)

## Interpretation

### AC-11: Size Budget

- **Expect**: UTF-8 encoding (ensure_ascii=False) saves ~3x bandwidth for Korean text
- **32KB limit**: JSON-encoded byte count (not character count)
- **Measurement basis**: Confirm in real API response; if 32KB is actually character-based, chunking window narrows

### AC-12: Error Codes

- **v1 endpoint** (`/wiki/rest/api/content/{id}/property/{key}`):
  - Over-limit → HTTP 413 Payload Too Large
- **v2 endpoint** (`/wiki/api/v2/pages/{id}/properties`):
  - Over-limit → HTTP 400 Bad Request
  - Message body contains 'too large', 'too long', '32', or '5242880' (5MB)

### AC-13: Rate Limits

- **Property write leg** (raw REST, basic-auth):
  - Attempts to capture all response header names + rate-limit family headers (Retry-After, X-RateLimit-*, RateLimit-*, Beta-*, X-Beta-*)
  - Note: basic-auth does not use points-model rate limiting (RFC compliant basic-auth requests may not receive Beta-* headers — header absence does not indicate failure, and is normal per Atlassian documentation)
  - Applies backoff on 429 with server Retry-After priority
- **Backward-polling leg** (MCP, OAuth):
  - No rate headers exposed → **BLOCKED-re-issuance** (S2 cannot measure MCP rate)

## Troubleshooting

| Issue | Solution |
|---|---|
| `CFP2829_TEST_PAGE_ID not set` | Export `CFP2829_TEST_PAGE_ID=<your-page-id>` |
| `401 Unauthorized` | Check token/email in creds file; verify basic-auth encoding |
| `400 Bad Request (over-limit)` | Payload likely >32KB; check JSON byte count (not char count) |
| `404 Not Found` | Test page deleted or ID incorrect |
| Script aborts on 20th write | This is intentional (self-cap); re-run if needed |
| Secrets detected in output | Check if token leaked; investigate sanitization |

## CI Integration (Future)

**Status**: S2 measurement is **manual-gated** (not in CI required checks).

**Future S3 consideration**:
- Establish separate CI pipeline with sanitized secret injection
- Integrate into gated S2 → S6 transition validation
- Measure ~1x per release cycle (not on every commit)

## Test Page Lifecycle

**Important**: Confluence test page created during measurement **persists after script completion**.

- **Reason**: MCP tool set lacks page deletion capability (Atlassian API limitation)
- **Operator action required**: Manual deletion via Confluence UI after measurement complete
- **Rationale**: Automation cannot guarantee safe cleanup of test page; human judgment required for throwaway page retention or deletion
- **Tracking**: Refer to operationally-maintained test page log to identify old test pages for periodic UI cleanup

## References

- **Change Plan**: CFP-2829.md §7.3 (operation risk) / §5.5.A (provisioning)
- **Live Measurement Runbook (CFP-2889)**: `docs/runbooks/cfp-2889-live-measurement-runbook.md` (full operator-gated execution guide)
- **Atlassian Docs**: developer.atlassian.com confluence-entity-properties (v2 properties CRUD)
- **Related Scripts**: `confluence_property_rest.py` (REST transport layer)
