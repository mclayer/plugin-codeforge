#!/usr/bin/env python3
# audit_trail_pii_redact.py — CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A
# SSOT extracted from audit-trail-fetch.sh §7.5 pii_redact() heredoc.
#
# Purpose: Hash actor_email, actor_ip, @ip fields in audit log JSON using HMAC-SHA256.
# Input:   JSON array read from stdin.
# Output:  JSON array with PII fields replaced by "hmac256:<hex12>".
# Env:     AUDIT_PII_KEY — HMAC key (required; validated by caller audit-trail-fetch.sh).
# Exit:    0=ok, 1=error (invalid JSON or missing key).
#
# Usage (called by pii_redact() bash function):
#   AUDIT_PII_KEY="..." json_data | python3 scripts/lib/audit_trail_pii_redact.py
import json
import sys
import hashlib
import hmac
import os

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def hash_val(v, key_bytes):
    if not v:
        return v
    return "hmac256:" + hmac.new(key_bytes, v.encode(), hashlib.sha256).hexdigest()[:12]


def main():
    key_raw = os.environ.get('AUDIT_PII_KEY', '')
    if not key_raw:
        print("ERROR: AUDIT_PII_KEY not set", file=sys.stderr)
        sys.exit(1)

    key_bytes = key_raw.encode()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON input: {exc}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                if 'actor_email' in entry:
                    entry['actor_email'] = hash_val(entry.get('actor_email', ''), key_bytes)
                if 'actor_ip' in entry:
                    entry['actor_ip'] = hash_val(entry.get('actor_ip', ''), key_bytes)
                if '@ip' in entry:
                    entry['@ip'] = hash_val(entry.get('@ip', ''), key_bytes)

    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
