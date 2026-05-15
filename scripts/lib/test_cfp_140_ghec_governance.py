#!/usr/bin/env python3
# test_cfp_140_ghec_governance.py — CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A
# SSOT extracted from test-cfp-140-ghec-governance.sh T3 PII redaction heredoc.
#
# Purpose: Test fixture PII redaction logic (sha256 prefix, no raw emails).
#          Used by T3 audit log + PII redaction test case.
#
# Usage:   python3 scripts/lib/test_cfp_140_ghec_governance.py
# Output:  "ok" or "fail" to stdout
# Exit:    0=ok, 1=fail
import hashlib
import sys


def hash_val(v: str) -> str:
    return "sha256:" + hashlib.sha256(v.encode()).hexdigest()[:12] if v else v


def run_pii_redaction_test() -> str:
    data = [
        {"actor_email": "user1@example.com", "actor_ip": "1.2.3.4"},
        {"actor_email": "admin@example.com", "actor_ip": "5.6.7.8"},
    ]
    for e in data:
        e["actor_email"] = hash_val(e["actor_email"])
        e["actor_ip"] = hash_val(e["actor_ip"])

    raw_emails = [e for e in data if "@" in e.get("actor_email", "")]
    hash_ok = all(e["actor_email"].startswith("sha256:") for e in data)

    if not raw_emails and hash_ok:
        return "ok"
    return "fail"


def main() -> int:
    result = run_pii_redaction_test()
    print(result)
    return 0 if result == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
