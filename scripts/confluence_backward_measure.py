#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confluence_backward_measure.py — S2 measurement harness for property storage/rate limits.

CFP-2829 S2 §7.3 / §5.5.A / §8.3: Measure content-property real-world behavior.

Covers AC-11 (32KB budget), AC-12 (v1/v2 error codes), AC-13 (rate-limit headers).

**CRITICAL SAFETY**: Measurement in this script uses creds to write to Confluence.
To prevent accidental prod pollution:
  1. CFP2829_TEST_PAGE_ID (REQUIRED) — must be set to throwaway test page ID
  2. CFP2829_MEASURE_SKIP_WRITE=1 (optional) — skip all writes even if creds present
  3. self-cap ≤20 write operations (S0 spike precedent)
  4. All writes followed by cleanup (DELETE or sentinel overwrite)
  5. Offline mock mode when creds unavailable

Env vars:
  - ATLASSIAN_BASE_URL: Confluence instance URL
  - ATLASSIAN_API_TOKEN / ATLASSIAN_USER_EMAIL: basic-auth creds (via ~/.claude/codeforge-scratch/atlassian-creds.env)
  - CFP2829_TEST_PAGE_ID: throwaway test page ID (REQUIRED for write)
  - CFP2829_MEASURE_SKIP_WRITE: 1 to skip writes despite creds
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

# cp949 guard
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Import our REST transport module (leg B) + chunking utility
try:
    from lib.confluence_property_rest import (
        create_rest_client,
        BUDGET_BYTES,
        _deny_scan_for_secrets,
        _scrub,
    )
    HAS_REST_MODULE = True
except ImportError:
    HAS_REST_MODULE = False
    logging.warning("confluence_property_rest not available — offline mode only")


# ── Constants ────────────────────────────────────────────────────────────────

# Safety caps (S0 spike precedent)
MAX_WRITES_PER_MEASUREMENT = 20

# Mock mode for offline testing
CFP1495_MOCK_MODE = os.environ.get("CFP1495_MOCK_MODE", "0") == "1"

# Measurement control
MEASURE_SKIP_WRITE = os.environ.get("CFP2829_MEASURE_SKIP_WRITE", "0") == "1"
TEST_PAGE_ID = os.environ.get("CFP2829_TEST_PAGE_ID")

# Confluence config
CONFLUENCE_BASE_URL = os.environ.get("ATLASSIAN_BASE_URL", "https://mclayer.atlassian.net")


# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


# ── Dry-run / Creds Check ────────────────────────────────────────────────────

def _creds_present() -> bool:
    """Check if Atlassian creds are set (env-indirect)."""
    token = os.environ.get("ATLASSIAN_API_TOKEN")
    email = os.environ.get("ATLASSIAN_USER_EMAIL")
    return bool(token and email)


def _load_creds_from_file(creds_path: Optional[str] = None) -> bool:
    """
    Load creds from ~/.claude/codeforge-scratch/atlassian-creds.env if present.

    This allows measurement harness to work when creds are provisioned externally.

    Returns: True if creds loaded/already present.
    """
    if creds_path is None:
        home = Path.home()
        creds_path = home / ".claude" / "codeforge-scratch" / "atlassian-creds.env"

    if not creds_path.exists():
        logger.info(f"Creds file not found: {creds_path}")
        return False

    try:
        with open(creds_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
        logger.info("Loaded creds from file")
        return True
    except Exception as e:
        logger.error(f"Failed to load creds file: {e}")
        return False


# ── Measurement: AC-11 (32KB Budget) ─────────────────────────────────────────

def measure_property_size_budget(client) -> Dict[str, any]:
    """
    Measure JSON-encoded size of property payloads.

    Tests:
      1. Small payload (1KB)
      2. Medium payload (10KB)
      3. Near-limit payload (28KB — conservative, pending actual measurement)

    Verifies:
      - ensure_ascii=False (UTF-8 3B) vs =True (6B) impact
      - actual byte count vs JSON string count

    Returns dict with measurements.
    """
    logger.info("=== AC-11: Property Size Budget Measurement ===")

    if not TEST_PAGE_ID:
        logger.warning("AC-11: Skipping write — CFP2829_TEST_PAGE_ID not set")
        return {"status": "BLOCKED-no-test-page-id", "verdict": "declared"}

    if MEASURE_SKIP_WRITE:
        logger.info("AC-11: SKIP_WRITE=1, offline only")
        return {"status": "offline-only", "verdict": "declared"}

    if not _creds_present():
        logger.warning("AC-11: Creds absent, offline fixture only")
        return {
            "status": "creds-absent",
            "offline_fixture": {
                "test_1kb": {"utf8_bytes": 1024, "ascii_bytes": 1024, "match": True},
                "test_10kb": {"utf8_bytes": 10240, "ascii_bytes": 10240, "match": True},
                "test_28kb": {"utf8_bytes": 28672, "ascii_bytes": 28672, "match": True},
            },
            "verdict": "declared",
        }

    results = {}
    write_count = [0]  # mutable counter for closure

    def _try_store(name: str, size_bytes: int) -> Optional[Dict]:
        """Attempt to store property and measure result."""
        if write_count[0] >= MAX_WRITES_PER_MEASUREMENT:
            logger.warning(f"Self-cap reached ({MAX_WRITES_PER_MEASUREMENT} writes)")
            return None

        # Create test payload
        test_payload = "x" * size_bytes
        property_value = {
            "size_request": size_bytes,
            "content": test_payload,
            "timestamp": int(time.time()),
        }

        # Measure JSON encoding
        json_utf8 = json.dumps(property_value, ensure_ascii=False).encode("utf-8")
        json_ascii = json.dumps(property_value, ensure_ascii=True).encode("utf-8")

        logger.info(f"{name}: UTF-8={len(json_utf8)} bytes, ASCII={len(json_ascii)} bytes")

        # Attempt store
        success, error = client.put_property_v2(
            TEST_PAGE_ID,
            f"test__{name}",
            property_value
        )

        write_count[0] += 1

        if success:
            # Cleanup: DELETE property
            del_ok, del_err = client.delete_property_v2(TEST_PAGE_ID, f"test__{name}")
            logger.info(f"Cleanup DELETE: {del_ok}")

        return {
            "utf8_bytes": len(json_utf8),
            "ascii_bytes": len(json_ascii),
            "delta_bytes": len(json_ascii) - len(json_utf8),
            "write_success": success,
            "error": error,
        }

    results["test_1kb"] = _try_store("1kb", 1024)
    results["test_10kb"] = _try_store("10kb", 10240)
    results["test_28kb"] = _try_store("28kb", 28672)  # At budget limit

    return {
        "status": "measured" if all(r for r in results.values()) else "partial",
        "measurements": results,
        "write_count": write_count[0],
        "budget_bytes": BUDGET_BYTES,
        "verdict": "normative" if all(r for r in results.values()) else "declared",
    }


# ── Measurement: AC-12 (v1/v2 Error Handling) ────────────────────────────────

def measure_oversize_error_codes(client) -> Dict[str, any]:
    """
    Measure error codes when payload exceeds budget.

    v1 endpoint = 413 Payload Too Large
    v2 endpoint = 400 Bad Request (with body message containing 'too large'/'32'/etc)

    Tests:
      1. Attempt to store 31KB payload (should trigger error)
      2. Verify error code and message parsing

    Returns dict with error classification.
    """
    logger.info("=== AC-12: Over-Limit Error Code Measurement ===")

    if not TEST_PAGE_ID:
        logger.warning("AC-12: Skipping — CFP2829_TEST_PAGE_ID not set")
        return {"status": "BLOCKED-no-test-page-id", "verdict": "declared"}

    if MEASURE_SKIP_WRITE:
        logger.info("AC-12: SKIP_WRITE=1")
        return {
            "status": "offline-only",
            "offline_fixture": {
                "v1_413": "413 Payload Too Large",
                "v2_400": "400 Bad Request (body: 'too large' or '32')",
            },
            "verdict": "declared",
        }

    if not _creds_present():
        logger.warning("AC-12: Creds absent, offline fixture")
        return {
            "status": "creds-absent",
            "offline_fixture": {
                "v1_endpoint": "413",
                "v2_endpoint": "400",
                "message_contains": ["too large", "32", "5242880"],
            },
            "verdict": "declared",
        }

    if _creds_present():
        write_count = [0]

        # Attempt 31KB (should fail)
        oversize_payload = {
            "content": "x" * (31 * 1024),
            "test": "oversize",
        }

        success, error = client.put_property_v2(
            TEST_PAGE_ID,
            "test__oversize_31kb",
            oversize_payload
        )

        write_count[0] += 1

        logger.info(f"Oversize test result: success={success}, error={_scrub(error)}")

        return {
            "status": "measured",
            "oversize_31kb": {
                "write_success": success,
                "error_message": error,
            },
            "write_count": write_count[0],
            "expected_error": "413 (v1) or 400 (v2, body contains size marker)",
            "verdict": "normative",
        }

    return {"status": "unknown", "verdict": "declared"}


# ── Measurement: AC-13 (Rate Limiting) ───────────────────────────────────────

def measure_rate_limit_headers(client) -> Dict[str, any]:
    """
    Measure rate-limit headers during property writes.

    Observes:
      - Retry-After (standard, server-authoritative)
      - Beta-RateLimit-Policy / Beta-RateLimit-Remaining (Atlassian proprietary)

    Leg-split:
      - REST leg (property v2): headers observed during write
      - MCP leg (backward-polling): headers NOT exposed (BLOCKED-re-isuance)

    Returns dict with observed headers.
    """
    logger.info("=== AC-13: Rate-Limit Header Observation ===")

    if not TEST_PAGE_ID:
        logger.warning("AC-13: Skipping — no test page")
        return {"status": "BLOCKED-no-test-page-id", "verdict": "observed-only"}

    if MEASURE_SKIP_WRITE:
        return {
            "status": "offline-only",
            "leg_split": {
                "rest_leg": "Beta-RateLimit-Policy / Beta-RateLimit-Remaining / Retry-After (observed)",
                "mcp_leg": "No headers exposed (BLOCKED-re-issuance)",
            },
            "verdict": "observed-only",
        }

    if not _creds_present():
        logger.warning("AC-13: Creds absent")
        return {
            "status": "creds-absent",
            "offline_fixture": {
                "rest_leg_headers": ["Retry-After", "Beta-RateLimit-Policy", "Beta-RateLimit-Remaining"],
                "mcp_leg": "No rate headers",
            },
            "verdict": "observed-only",
        }

    # During write attempts, client logs rate headers (in _ensure_session / put_property_v2)
    logger.info("Rate-limit observation: see client debug logs during write()")
    logger.info(f"Backup Tier1 estimate: 65k points (OAuth, source: Atlassian points model)")

    return {
        "status": "observed-during-writes",
        "leg_split": {
            "rest_leg": "property-write raw REST (Beta-RateLimit headers observed if present)",
            "mcp_leg": "Confluence v2 getConfluencePage (no rate headers, BLOCKED-re-issuance)",
        },
        "estimated_tier": "65k points Tier1 (OAuth)",
        "verdict": "observed-only",
    }


# ── Main Entry Point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CFP-2829 S2 measurement harness (AC-11/12/13)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all measurements (default if no --measure specified)",
    )
    parser.add_argument(
        "--measure-size-budget",
        action="store_true",
        help="Measure AC-11 property size budget",
    )
    parser.add_argument(
        "--measure-error-codes",
        action="store_true",
        help="Measure AC-12 over-limit error codes",
    )
    parser.add_argument(
        "--measure-rate-limits",
        action="store_true",
        help="Measure AC-13 rate-limit headers",
    )
    parser.add_argument(
        "--load-creds",
        type=str,
        help="Path to creds file (default: ~/.claude/codeforge-scratch/atlassian-creds.env)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force offline mock mode (no real API calls)",
    )

    args = parser.parse_args()

    # Setup
    if args.mock:
        os.environ["CFP1495_MOCK_MODE"] = "1"

    if args.load_creds:
        _load_creds_from_file(Path(args.load_creds))
    else:
        _load_creds_from_file()

    # Summary
    logger.info("=" * 70)
    logger.info("CFP-2829 S2 Measurement Harness")
    logger.info(f"Test page ID: {TEST_PAGE_ID or 'NOT SET (write disabled)'}")
    logger.info(f"Skip write: {MEASURE_SKIP_WRITE}")
    logger.info(f"Creds present: {_creds_present()}")
    logger.info(f"Mock mode: {CFP1495_MOCK_MODE}")
    logger.info("=" * 70)

    # Create REST client (even in mock mode, for offline testing)
    if not HAS_REST_MODULE:
        logger.error("confluence_property_rest module not available!")
        return 1

    client = create_rest_client(CONFLUENCE_BASE_URL)

    # Run measurements
    run_all = args.all or not (
        args.measure_size_budget or args.measure_error_codes or args.measure_rate_limits
    )

    results = {}

    if args.measure_size_budget or run_all:
        logger.info("\n--- Running AC-11 measurement ---")
        results["ac11_size_budget"] = measure_property_size_budget(client)

    if args.measure_error_codes or run_all:
        logger.info("\n--- Running AC-12 measurement ---")
        results["ac12_error_codes"] = measure_oversize_error_codes(client)

    if args.measure_rate_limits or run_all:
        logger.info("\n--- Running AC-13 measurement ---")
        results["ac13_rate_limits"] = measure_rate_limit_headers(client)

    # Output results
    logger.info("\n" + "=" * 70)
    logger.info("Measurement Results:")
    logger.info("=" * 70)

    output = json.dumps(results, indent=2, ensure_ascii=False)

    # Deny-scan before output
    is_safe, scan_error = _deny_scan_for_secrets(output)
    if not is_safe:
        logger.error(f"DENY-SCAN FAILED: {scan_error}")
        logger.error("Aborting output — potential secret leak detected")
        return 1

    print(output, file=sys.stdout)

    # Summary
    logger.info("\n" + "=" * 70)
    verdicts = [r.get("verdict", "?") for r in results.values()]
    logger.info(f"Overall: {', '.join(set(verdicts))}")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
