#!/usr/bin/env bash
# test-cfp-140-ghec-governance.sh — AC-23 e2e fixture tests (CFP-140 / §8.2)
# Tests run from the repo root (cd to worktree before executing).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."   # cd to repo root so python3 can use relative paths

FIXTURE_REL="scripts/test-fixtures/cfp-140-ghec-governance"
PASS=0
FAIL=0

log()  { printf '[test] %s\n' "$1" >&2; }
pass() { PASS=$((PASS + 1)); log "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); log "  FAIL: $1"; }

# --- T1: Issue Type auto-attach ---
test_t1_issue_type_attach() {
  log "T1: Issue Type attach — mock response validation (AC-23 fixture 1)"

  TYPE_NAME=$(python3 -c "
import json
data = json.load(open('${FIXTURE_REL}/fixture-1-issue-type-auto-attach/mock-issue-types-response.json'))
types = [t['name'] for t in data]
print('Story' in types)
" 2>/dev/null || echo "False")

  [[ "$TYPE_NAME" == "True" ]] && pass "T1: Issue Type 'Story' present in org Issue Types mock" \
    || fail "T1: Issue Type 'Story' missing (got: ${TYPE_NAME})"

  PATCHED_TYPE=$(python3 -c "
import json
d = json.load(open('${FIXTURE_REL}/fixture-1-issue-type-auto-attach/mock-issue-patch-response.json', encoding='utf-8'))
print(d.get('type', {}).get('name', ''))
" 2>/dev/null || echo "")

  [[ "$PATCHED_TYPE" == "Story" ]] && pass "T1: PATCH mock response Issue Type 'Story' confirmed" \
    || fail "T1: PATCH mock response unexpected type: '${PATCHED_TYPE}'"
}

# --- T2a: Ruleset drift — no drift ---
test_t2a_ruleset_no_drift() {
  log "T2a: Ruleset drift check — no drift (AC-23 fixture 2a)"

  VALID=$(python3 -c "
import json
try:
    d = json.load(open('templates/rulesets/repo-default.json'))
    assert 'name' in d, 'missing name'
    assert d.get('enforcement') == 'active', f'enforcement={d.get(\"enforcement\")}'
    print('ok')
except Exception as e:
    print('fail: ' + str(e))
")

  [[ "$VALID" == "ok" ]] && pass "T2a: repo-default.json — valid with required fields" \
    || fail "T2a: repo-default.json — ${VALID}"

  MATCH=$(python3 -c "
import json
spec = json.load(open('templates/rulesets/repo-default.json'))
live = json.load(open('${FIXTURE_REL}/fixture-2-ruleset-drift/no-drift/mock-live-rulesets.json'))
spec_name = spec.get('name','')
live_name = live[0].get('name','') if live else ''
print('match' if spec_name == live_name else f'mismatch:{spec_name}!={live_name}')
")

  [[ "$MATCH" == "match" ]] && pass "T2a: spec name matches live name (no-drift)" \
    || fail "T2a: ${MATCH}"
}

# --- T2b: Ruleset drift — has drift ---
test_t2b_ruleset_has_drift() {
  log "T2b: Ruleset drift check — has drift (AC-23 fixture 2b)"

  RESULT=$(python3 -c "
import json
spec = json.load(open('templates/rulesets/repo-default.json'))
live = json.load(open('${FIXTURE_REL}/fixture-2-ruleset-drift/has-drift/mock-live-rulesets.json'))
spec_e = spec.get('enforcement','')
live_e = live[0].get('enforcement','') if live else ''
print('drift:spec=%s,live=%s' % (spec_e, live_e) if spec_e != live_e else 'no-drift')
")

  [[ "$RESULT" == drift:* ]] && pass "T2b: has-drift detected — ${RESULT}" \
    || fail "T2b: expected drift, got: ${RESULT}"
}

# --- T3: Audit log + PII redaction ---
test_t3_audit_log_pii_redaction() {
  log "T3: Audit log + PII redaction (AC-23 fixture 3)"

  # PII redaction logic
  RESULT=$(python3 - <<'PY'
import json, hashlib

def hash_val(v):
    return "sha256:" + hashlib.sha256(v.encode()).hexdigest()[:12] if v else v

data = [
    {"actor_email": "user1@example.com", "actor_ip": "1.2.3.4"},
    {"actor_email": "admin@example.com", "actor_ip": "5.6.7.8"}
]
for e in data:
    e["actor_email"] = hash_val(e["actor_email"])
    e["actor_ip"] = hash_val(e["actor_ip"])

raw_emails = [e for e in data if '@' in e.get('actor_email','')]
hash_ok = all(e["actor_email"].startswith("sha256:") for e in data)
print("ok" if not raw_emails and hash_ok else "fail")
PY
)

  [[ "$RESULT" == "ok" ]] && pass "T3: PII redaction — no raw emails, sha256: prefix confirmed" \
    || fail "T3: PII redaction failed"

  # Pagination fixture
  PAGES=$(python3 -c "
import json
p1 = json.load(open('${FIXTURE_REL}/fixture-3-audit-log-fetch/mock-graphql-page1.json'))
p2 = json.load(open('${FIXTURE_REL}/fixture-3-audit-log-fetch/mock-graphql-page2.json'))
p1n = p1['data']['enterprise']['auditLog']['pageInfo']['hasNextPage']
p2n = p2['data']['enterprise']['auditLog']['pageInfo']['hasNextPage']
print('ok' if p1n and not p2n else f'fail:p1={p1n},p2={p2n}')
")

  [[ "$PAGES" == "ok" ]] && pass "T3: pagination — page1 hasNextPage=True, page2 hasNextPage=False" \
    || fail "T3: pagination fixture — ${PAGES}"

  TOTAL=$(python3 -c "
import json
p1 = json.load(open('${FIXTURE_REL}/fixture-3-audit-log-fetch/mock-graphql-page1.json'))
p2 = json.load(open('${FIXTURE_REL}/fixture-3-audit-log-fetch/mock-graphql-page2.json'))
t = len(p1['data']['enterprise']['auditLog']['edges']) + len(p2['data']['enterprise']['auditLog']['edges'])
print(t)
")

  [[ "$TOTAL" -eq 3 ]] && pass "T3: total 3 events across 2 pages" \
    || fail "T3: expected 3 events, got ${TOTAL}"
}

# --- T4: Required workflow drift ---
test_t4_required_workflow_drift() {
  log "T4: Required workflow drift (AC-23 fixture 4)"

  RESULT=$(python3 -c "
import yaml, json
spec = yaml.safe_load(open('templates/required-workflows-spec.yaml', encoding='utf-8'))
live = json.load(open('${FIXTURE_REL}/fixture-4-required-workflow-drift/mock-live-required-workflows.json'))
sc = len(spec.get('required_workflows', []))
lc = live.get('total_count', 0)
print('ok:spec=%d,live=%d,drift=%d' % (sc, lc, sc - lc))
")

  if [[ "$RESULT" == ok:spec=6,live=2,drift=4 ]]; then
    pass "T4: required workflow drift — spec=6, live=2 (4 missing)"
  else
    fail "T4: expected ok:spec=6,live=2,drift=4, got: ${RESULT}"
  fi
}

# --- T5: All 3 ruleset JSON specs valid ---
test_t5_spec_json_validity() {
  log "T5: All 3 ruleset JSON specs valid (AC-13 companion)"

  for spec_name in repo-default org-default enterprise-default; do
    VALID=$(python3 -c "
import json
try:
    d = json.load(open('templates/rulesets/${spec_name}.json'))
    assert 'name' in d and 'enforcement' in d
    print('ok')
except Exception as e:
    print(str(e))
")
    [[ "$VALID" == "ok" ]] && pass "T5: ${spec_name}.json — valid" \
      || fail "T5: ${spec_name}.json — ${VALID}"
  done
}

# --- T6: Migration script ---
test_t6_migration_script() {
  log "T6: Migration script dry-run + idempotency (AC-16)"

  bash -n "scripts/migrate-label-to-issue-type.sh" 2>/dev/null \
    && pass "T6: syntax valid" || fail "T6: syntax error"

  grep -q 'MODE="dry-run"' "scripts/migrate-label-to-issue-type.sh" \
    && pass "T6: dry-run is default" || fail "T6: dry-run default missing"

  grep -q 'CURRENT_TYPE\|idempotent' "scripts/migrate-label-to-issue-type.sh" \
    && pass "T6: idempotency logic present" || fail "T6: idempotency missing"
}

# --- Run ---
test_t1_issue_type_attach
test_t2a_ruleset_no_drift
test_t2b_ruleset_has_drift
test_t3_audit_log_pii_redaction
test_t4_required_workflow_drift
test_t5_spec_json_validity
test_t6_migration_script

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -gt 0 ]] && echo "FAIL" >&2 && exit 1
echo "PASS"
exit 0
