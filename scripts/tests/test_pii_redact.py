#!/usr/bin/env python3
"""
Unit tests for pii_redact() HMAC logic.
Duplicates hash_val from audit-trail-fetch.sh to form a spec contract.
"""
import hmac
import hashlib
import unittest


def hash_val(v, key_bytes):
    """Mirror of hash_val inside pii_redact() in audit-trail-fetch.sh."""
    if not v:
        return v
    return "hmac256:" + hmac.new(key_bytes, v.encode(), hashlib.sha256).hexdigest()[:12]


class TestPiiRedactHmac(unittest.TestCase):
    def setUp(self):
        self.key = b"test-secret-key-32chars-for-hmac"

    def test_prefix_is_hmac256(self):
        result = hash_val("user@example.com", self.key)
        self.assertTrue(result.startswith("hmac256:"), f"Expected 'hmac256:' prefix, got: {result}")

    def test_total_length(self):
        result = hash_val("user@example.com", self.key)
        # "hmac256:" (8) + 12 hex chars = 20 total
        self.assertEqual(len(result), 20, f"Expected length 20, got: {len(result)}")

    def test_differs_from_plain_sha256(self):
        email = "user@example.com"
        plain = "sha256:" + hashlib.sha256(email.encode()).hexdigest()[:12]
        hmac_result = hash_val(email, self.key)
        self.assertNotEqual(
            plain, hmac_result,
            "HMAC result must differ from plain SHA-256"
        )

    def test_deterministic_same_key(self):
        email = "user@example.com"
        r1 = hash_val(email, self.key)
        r2 = hash_val(email, self.key)
        self.assertEqual(r1, r2, "Same key must produce same hash")

    def test_different_keys_produce_different_hashes(self):
        email = "user@example.com"
        r1 = hash_val(email, b"key-one")
        r2 = hash_val(email, b"key-two")
        self.assertNotEqual(r1, r2, "Different keys must produce different hashes")

    def test_empty_string_passthrough(self):
        self.assertEqual(hash_val("", self.key), "", "Empty string must pass through unchanged")

    def test_none_passthrough(self):
        self.assertIsNone(hash_val(None, self.key), "None must pass through unchanged")

    def test_ip_address_hashed(self):
        result = hash_val("192.168.1.100", self.key)
        self.assertTrue(result.startswith("hmac256:"))
        self.assertEqual(len(result), 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
