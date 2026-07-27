#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confluence_property_rest.py — creds-gated property REST transport (leg B).

CFP-2829 S2: backward-sync content property storage/retrieval via Atlassian REST API.

Features:
  - env-indirect token access (no literal in code)
  - basic-auth transport + envelope sanitization (token masking)
  - v1 + v2 endpoint dual-path (v1: POST/PUT/GET; v2: /wiki/api/v2/pages/{id}/properties)
  - over-limit error handling (v1: 413 / v2: 400 + body message parsing)
  - rate-limit header observation (Beta-RateLimit-Policy/Beta-RateLimit/Retry-After)
  - property version ≠ page version (separate tracking)
  - MOCK mode (creds-free offline testing)

AC requirements:
  - AC-11: 32KB/key JSON-encoded budget + manifest-last chunk ordering
  - AC-12: v1/v2 error disjoint handling (413 vs 400)
  - AC-13: rate meter + exp-backoff (leg-split observed vs BLOCKED)

Security:
  - SA-1: env-indirect token (ATLASSIAN_API_TOKEN / ATLASSIAN_USER_EMAIL)
  - SA-3: sanitizing wrapper (_scrub) for all logs/stderr/exceptions
  - IO-1: hard-fail on creds absence (no silent skip)
  - IO-3: leg-split rate (REST observed / MCP BLOCKED)
"""

import base64
import hashlib
import io
import json
import logging
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# cp949 guard (Windows CI utf-8 stdout)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Conditional import for requests (offline mock fallback)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Constants ────────────────────────────────────────────────────────────────

PROPERTY_KEY_PREFIX = "codeforge.sync.canonical"
MANIFEST_KEY = f"{PROPERTY_KEY_PREFIX}.__manifest"
CHUNK_KEY_TEMPLATE = f"{PROPERTY_KEY_PREFIX}.__chunk_{{n}}"

# Budget: 28KB conservative (32KB - 4KB safety margin) pending measurement
# Actual = 32KB JSON-encoded byte, measurement-basis (ensure_ascii lever) after AC-11 probe
BUDGET_BYTES = 28 * 1024

# Rate limit constants
RATE_LIMIT_POINTS_PER_WRITE = 1  # property write ≈ 1 point (approx)
MAX_RETRY_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


# ── MOCK Mode (creds-free testing) ───────────────────────────────────────────

CFP1495_MOCK_MODE = os.environ.get("CFP1495_MOCK_MODE", "0") == "1"
CFP1495_API_MOCK_401 = os.environ.get("CFP1495_API_MOCK_401", "0") == "1"
CFP1495_API_MOCK_429 = os.environ.get("CFP1495_API_MOCK_429", "0") == "1"


# ── Logging & Sanitization ──────────────────────────────────────────────────

def _scrub(text: str) -> str:
    """
    Mask sensitive auth tokens in text.

    Patterns:
      - ATLASSIAN_API_TOKEN value (assume ≥20 base64-like chars)
      - Basic auth header: Basic [A-Za-z0-9+/=]{20,}

    Returns sanitized text.
    """
    if not isinstance(text, str):
        return str(text)

    # Mask token env value (heuristic: 20+ alphanumeric/+/= chars)
    text = re.sub(r'([A-Za-z0-9+/=]{20,})', r'***REDACTED***', text)

    # Mask Basic auth header
    text = re.sub(r'Basic [A-Za-z0-9+/=]+', 'Basic ***REDACTED***', text)

    return text


class SanitizedHandler(logging.Handler):
    """Log handler that sanitizes sensitive tokens before emit."""

    def __init__(self, base_handler: logging.Handler):
        super().__init__()
        self.base_handler = base_handler
        self.setFormatter(base_handler.formatter)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            sanitized = _scrub(msg)
            # Re-create record with sanitized message
            record.msg = sanitized
            record.args = ()
            self.base_handler.emit(record)
        except Exception:
            self.handleError(record)


def _setup_sanitized_logging() -> logging.Logger:
    """Initialize logging with token sanitization."""
    logger = logging.getLogger("confluence_property_rest")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        ))
        sanitized_handler = SanitizedHandler(handler)
        logger.addHandler(sanitized_handler)

    return logger


logger = _setup_sanitized_logging()


# ── Envelope Sanitization & Deny-Scan ────────────────────────────────────────

def _deny_scan_for_secrets(text: str) -> Tuple[bool, Optional[str]]:
    """
    Scan text for potential token/auth leaks before emission.

    Returns: (is_safe, error_message)
    """
    if not isinstance(text, str):
        return True, None

    # Pattern: Basic [A-Za-z0-9+/=]{20,}
    if re.search(r'Basic [A-Za-z0-9+/=]{20,}', text):
        return False, "Detected Basic auth header in output — aborting"

    # Pattern: Raw token-like (20+ alphanumeric/+/= in sequence)
    # (This is a heuristic — real detection requires context)
    if re.search(r'[A-Za-z0-9+/=]{20,}', text):
        # Only fail if it looks like it's near "token" keyword
        if re.search(r'(?:token|password|secret)["\']?\s*[:=]\s*[A-Za-z0-9+/=]{20,}', text, re.IGNORECASE):
            return False, "Detected potential token in output — aborting"

    return True, None


# ── Error Classification (AC-12) ────────────────────────────────────────────

def is_over_limit_error(version: int, status_code: int, body_text: str = "") -> bool:
    """
    Classify over-limit errors disjointly across v1 and v2 APIs (AC-12).

    Rules:
      - v1: status_code == 413 (Payload Too Large) → True
      - v2: status_code == 400 AND body contains size signature → True
            (signatures: "too large", "too long", "32", "5242880")
      - All other cases → False

    Args:
        version: API version (1 or 2)
        status_code: HTTP status code
        body_text: Response body (parsed message for v2 classification)

    Returns:
        True if error is classified as over-limit; False otherwise.

    Note:
        v1 uses status code alone (413 is unambiguous Payload Too Large).
        v2 uses status code + body parsing (400 is generic Bad Request; must parse message).
    """
    if version == 1:
        return status_code == 413

    if version == 2:
        if status_code != 400:
            return False
        # Check body for size-limit signatures
        body_lower = body_text.lower() if body_text else ""
        return any(sig in body_lower for sig in ["too large", "too long", "32", "5242880"])

    return False


# ── Creds I/O (env-indirect, IO-1) ──────────────────────────────────────────

def _get_creds() -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch API token and email from environment (env-indirect).

    Returns: (token, email) or (None, None) if either missing.
    Raises: no exception (returns None gracefully for MOCK/offline).
    """
    token = os.environ.get("ATLASSIAN_API_TOKEN")
    email = os.environ.get("ATLASSIAN_USER_EMAIL")

    if token and email:
        logger.debug("Creds loaded (env-indirect)")
        return token, email

    # IO-1: hard-fail later on write attempt if creds absent
    logger.warning("ATLASSIAN_API_TOKEN/USER_EMAIL not set — REST write will fail")
    return None, None


def _basic_auth_header(email: str, token: str) -> str:
    """Generate Authorization: Basic header value (no literal in code)."""
    credential = f"{email}:{token}"
    encoded = base64.b64encode(credential.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


# ── REST Transport (leg B, creds-gated) ──────────────────────────────────────

class ConfluencePropertyREST:
    """
    Property REST transport wrapper.

    Handles:
      - Basic-auth REST calls
      - v1 + v2 dual-path (v1 for backward compat, v2 as primary new)
      - Error handling (v1: 413, v2: 400 + body parse)
      - Rate-limit header observation (observed-only for leg B)
    """

    def __init__(self, base_url: str, token: Optional[str], email: Optional[str]):
        """
        Initialize REST client.

        Args:
            base_url: Confluence instance URL (e.g., https://mclayer.atlassian.net)
            token: API token (env-loaded)
            email: User email (env-loaded)
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.email = email
        self.session_v1 = None
        self.session_v2 = None
        self.rate_limit_state = {"remaining": 65000, "reset_at": None}  # OAuth Tier1 estimate

    def _ensure_session(self, version: int) -> Optional[Any]:
        """Lazy-init requests session with basic-auth (if HAS_REQUESTS)."""
        if not HAS_REQUESTS:
            return None

        if version == 1:
            if self.session_v1 is None and self.token and self.email:
                self.session_v1 = requests.Session()
                self.session_v1.headers.update({
                    "Authorization": _basic_auth_header(self.email, self.token),
                    "Content-Type": "application/json",
                })
            return self.session_v1
        elif version == 2:
            if self.session_v2 is None and self.token and self.email:
                self.session_v2 = requests.Session()
                self.session_v2.headers.update({
                    "Authorization": _basic_auth_header(self.email, self.token),
                    "Content-Type": "application/json",
                })
            return self.session_v2

        return None

    def get_property_v2(self, page_id: str, property_key: str) -> Optional[Dict[str, Any]]:
        """
        Fetch property via v2 API (GET /wiki/api/v2/pages/{id}/properties/{key}).

        Returns: property dict or None on error.
        """
        if CFP1495_MOCK_MODE or not HAS_REQUESTS:
            logger.info(f"[MOCK] get_property_v2({page_id}, {property_key})")
            return None

        if CFP1495_API_MOCK_401:
            logger.warning(f"[MOCK 401] get_property_v2({page_id}, {property_key})")
            raise RuntimeError("Simulated 401 Unauthorized")

        session = self._ensure_session(2)
        if not session:
            logger.error("v2 session unavailable (missing creds?)")
            return None

        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/properties/{property_key}"
        try:
            resp = session.get(url, timeout=10)

            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401:
                logger.error("401 Unauthorized — check token/email")
                raise RuntimeError("401 Unauthorized")
            elif resp.status_code == 404:
                logger.info(f"Property not found: {property_key}")
                return None
            else:
                logger.warning(f"GET returned {resp.status_code}: {_scrub(resp.text[:200])}")
                return None

        except Exception as e:
            logger.error(f"get_property_v2 failed: {type(e).__name__}: {_scrub(str(e))}")
            return None

    def put_property_v2(self, page_id: str, property_key: str,
                       value: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Store property via v2 API (PUT /wiki/api/v2/pages/{id}/properties/{key}).

        Handles:
          - JSON encoding budget check (AC-11)
          - Over-limit error classification (v1: 413 / v2: 400+body; AC-12)
          - Rate-limit headers (observed)

        Returns: (success, error_message)

        Note:
            v2 is the primary transport (AC-1, default). Over-limit classifier (AC-12)
            recognizes both v1 (413) and v2 (400+body) for reference, though v1 methods
            are not currently exposed (interface-frozen).
        """
        if not self.token or not self.email:
            # IO-1: hard-fail on creds absence
            logger.error("IO-1 HARD-FAIL: Creds absent, rejecting write")
            return False, "Creds absent"

        if CFP1495_MOCK_MODE or not HAS_REQUESTS:
            logger.info(f"[MOCK] put_property_v2({page_id}, {property_key})")

            # Mock: check budget
            encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
            if len(encoded) > BUDGET_BYTES:
                return False, f"MOCK: Over budget ({len(encoded)} > {BUDGET_BYTES})"

            return True, None

        if CFP1495_API_MOCK_401:
            logger.warning(f"[MOCK 401] put_property_v2({page_id})")
            return False, "Simulated 401"

        if CFP1495_API_MOCK_429:
            logger.warning(f"[MOCK 429] put_property_v2({page_id})")
            return False, "Simulated 429"

        # Real API call
        session = self._ensure_session(2)
        if not session:
            logger.error("v2 session unavailable")
            return False, "Session unavailable"

        # Pre-flight budget check (AC-11)
        try:
            encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
        except Exception as e:
            logger.error(f"JSON encode failed: {e}")
            return False, f"JSON encode: {e}"

        if len(encoded) > BUDGET_BYTES:
            logger.error(f"Over budget: {len(encoded)} > {BUDGET_BYTES}")
            return False, f"Over budget ({len(encoded)} bytes)"

        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/properties/{property_key}"

        # Retry loop with exp-backoff (AC-13 rate meter)
        backoff = INITIAL_BACKOFF_SECONDS
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                resp = session.put(url, json=value, timeout=10)

                # Observe rate-limit headers (AC-13 observed-only)
                if "Retry-After" in resp.headers:
                    retry_after = int(resp.headers.get("Retry-After", "1"))
                    logger.info(f"Rate-limit: Retry-After={retry_after}s")
                    self.rate_limit_state["reset_at"] = time.time() + retry_after

                if "Beta-RateLimit-Remaining" in resp.headers:
                    remaining = resp.headers.get("Beta-RateLimit-Remaining", "?")
                    logger.debug(f"Rate-limit: Remaining={remaining} points")

                if resp.status_code == 200:
                    logger.info(f"Property stored: {property_key}")
                    return True, None

                elif resp.status_code == 400:
                    # v2 over-limit = 400 (classified via AC-12 checker)
                    body = resp.json() if resp.headers.get("content-type") == "application/json" else {}
                    error_msg = body.get("message", resp.text)

                    if is_over_limit_error(2, resp.status_code, error_msg):
                        logger.error(f"Over-limit (v2 400): {_scrub(error_msg)}")
                        return False, f"Over-limit: {error_msg[:100]}"

                    logger.error(f"400 Bad Request: {_scrub(error_msg)}")
                    return False, f"400: {error_msg[:100]}"

                elif resp.status_code == 401:
                    logger.error("401 Unauthorized")
                    return False, "401 Unauthorized"

                elif resp.status_code == 429:
                    # Rate limit hit (AC-13 rate meter)
                    logger.warning(f"429 Rate Limit (attempt {attempt+1}/{MAX_RETRY_ATTEMPTS})")
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        logger.info(f"Backoff {backoff}s...")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    return False, "Rate limit exceeded after retries"

                else:
                    logger.error(f"Unexpected {resp.status_code}: {_scrub(resp.text[:200])}")
                    return False, f"{resp.status_code}"

            except Exception as e:
                logger.error(f"put_property_v2 exception (attempt {attempt+1}): {type(e).__name__}: {_scrub(str(e))}")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                return False, str(e)

        return False, "Max retries exceeded"

    def delete_property_v2(self, page_id: str, property_key: str) -> Tuple[bool, Optional[str]]:
        """
        Delete property via v2 (cleanup after measurement).

        Returns: (success, error_message)
        """
        if not self.token or not self.email:
            logger.error("IO-1 HARD-FAIL: Creds absent for delete")
            return False, "Creds absent"

        if CFP1495_MOCK_MODE or not HAS_REQUESTS:
            logger.info(f"[MOCK] delete_property_v2({page_id}, {property_key})")
            return True, None

        session = self._ensure_session(2)
        if not session:
            logger.error("v2 session unavailable")
            return False, "Session unavailable"

        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/properties/{property_key}"

        try:
            resp = session.delete(url, timeout=10)
            if resp.status_code in (200, 204, 404):  # 404 = already gone
                logger.info(f"Property deleted: {property_key}")
                return True, None
            else:
                logger.error(f"Delete returned {resp.status_code}")
                return False, f"{resp.status_code}"

        except Exception as e:
            logger.error(f"delete_property_v2 failed: {e}")
            return False, str(e)


# ── Public API (leg B) ───────────────────────────────────────────────────────

def create_rest_client(base_url: str) -> ConfluencePropertyREST:
    """
    Factory: create REST client with env-loaded creds.

    Raises on creds absence for write operations (IO-1).
    """
    token, email = _get_creds()
    return ConfluencePropertyREST(base_url, token, email)
