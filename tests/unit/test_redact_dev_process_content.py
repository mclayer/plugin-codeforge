"""test_redact_dev_process_content.py — capture-time redaction (INV-8 floor) suite.

CFP-2687 Phase 2. Change Plan §7.2/§7.3/§7.5 + Story §5.3 AC-12/13/14 + §5.4.
Under test: scripts/lib/redact_dev_process_content.py

불변식:
  · deny-pattern (AC-13): token/key/Authorization/Cookie/절대·home 경로/email/github-pat REDACT.
  · repo-relative path PRESERVED (§5.4 noise false-negative 회피 — diff 진단 신호 public).
  · env dump / 자격증명 subprocess 출력 = whole-content 제외.
  · session_id → sha256(hex12) (raw 미저장, T-DPE-6).
  · audit(T-DPE-8): rule-name + count 만, 매칭 secret 원문/hash 절대 미기록.
  · idempotent: redact(redact(x)) == redact(x).
  · byte/line-cap bound: over-cap → 절단 마커 (★"ReDoS-safe" 단정 금지 — bounded 만 assert).
"""

from __future__ import annotations

import hashlib
import json

import pytest

import redact_dev_process_content as rd


# ══════════════════════════════════════════════════════════════════════════════
# § deny-pattern (AC-13)
# ══════════════════════════════════════════════════════════════════════════════
class TestDenyPatterns:
    def test_api_key_token_redacted(self):
        raw = "token=ABCDEFGHIJKLMNOP1234 rest"
        red, audit = rd.redact(raw)
        assert "ABCDEFGHIJKLMNOP1234" not in red
        assert audit["redaction_applied"] is True
        assert rd.RULE_API_KEY in audit["redaction_rules_fired"]

    def test_github_pat_redacted(self):
        raw = "here is ghp_" + "A" * 36 + " token"
        red, audit = rd.redact(raw)
        assert "ghp_" + "A" * 36 not in red
        assert rd.RULE_GITHUB_PAT in audit["redaction_rules_fired"]

    def test_authorization_header_redacted(self):
        raw = "Authorization: Bearer abcdef0123456789XYZ"
        red, audit = rd.redact(raw)
        assert "abcdef0123456789XYZ" not in red
        assert rd.RULE_AUTH_HEADER in audit["redaction_rules_fired"]

    def test_cookie_header_redacted(self):
        raw = "Cookie: sid=supersecretcookievalue123"
        red, audit = rd.redact(raw)
        assert "supersecretcookievalue123" not in red
        assert rd.RULE_COOKIE_HEADER in audit["redaction_rules_fired"]

    def test_email_redacted(self):
        raw = "contact developer@mclayer.it now"
        red, audit = rd.redact(raw)
        assert "developer@mclayer.it" not in red
        assert rd.RULE_EMAIL in audit["redaction_rules_fired"]

    @pytest.mark.parametrize("abs_path", [
        "/home/mccho/.ssh/id_rsa",
        "C:\\Users\\mccho\\secret.txt",
        "/Users/mccho/creds",
        "/c/Users/mccho/token.txt",
    ])
    def test_absolute_and_home_paths_redacted(self, abs_path):
        raw = "opened file " + abs_path + " done"
        red, audit = rd.redact(raw)
        assert abs_path not in red, f"절대/home 경로 미redact: {abs_path}"
        assert rd.RULE_ABS_PATH in audit["redaction_rules_fired"]

    def test_repo_relative_path_PRESERVED(self):
        """repo-relative 경로는 진단 신호(public)이므로 보존 — 무차별 redact 금지 (§5.4)."""
        raw = "edited scripts/lib/foo.py and tests/unit/bar.py"
        red, audit = rd.redact(raw)
        assert "scripts/lib/foo.py" in red, "repo-relative 경로가 잘못 redact 됨"
        assert "tests/unit/bar.py" in red
        assert rd.RULE_ABS_PATH not in audit["redaction_rules_fired"]

    def test_negative_control_preserved_path_would_fail_if_redacted(self):
        """[negative control] repo-relative 보존 검사는 discriminating.

        만약 impl 이 이 경로를 redact 했다면 위 test 의 `in red` 가 RED 가 된다 — 즉
        보존 검사가 실제 값 존재에 의존함을 명시."""
        red, _ = rd.redact("scripts/lib/foo.py")
        assert "scripts/lib/foo.py" in red  # 보존 (redact 되면 이 라인이 실패)


# ══════════════════════════════════════════════════════════════════════════════
# § whole-content 제외
# ══════════════════════════════════════════════════════════════════════════════
class TestWholeContentExclusion:
    def test_env_dump_excluded_wholesale(self):
        lines = "\n".join("VAR%d=value%d" % (i, i) for i in range(12))
        red, audit = rd.redact(lines)
        assert red == rd._ph(rd.RULE_ENV_DUMP)
        assert rd.RULE_ENV_DUMP in audit["redaction_rules_fired"]
        assert "value1" not in red

    def test_credential_subprocess_excluded_wholesale(self):
        raw = "aws_secret_access_key = AKIAIOSFODNN7EXAMPLEKEY\nregion = us-east-1"
        red, audit = rd.redact(raw)
        assert red == rd._ph(rd.RULE_CRED_SUBPROC)
        assert rd.RULE_CRED_SUBPROC in audit["redaction_rules_fired"]
        assert "AKIAIOSFODNN7EXAMPLEKEY" not in red


# ══════════════════════════════════════════════════════════════════════════════
# § session_id → sha256 (T-DPE-6)
# ══════════════════════════════════════════════════════════════════════════════
class TestSessionIdHashed:
    def test_session_id_hashed_not_raw(self):
        raw = "session_id=abc123def456ghi789"
        red, audit = rd.redact(raw)
        assert "abc123def456ghi789" not in red
        assert "[REDACTED-SESSION:" in red
        assert rd.RULE_SESSION_ID in audit["redaction_rules_fired"]

    def test_session_hash_is_deterministic_truncated(self):
        raw = "session_id=abc123def456ghi789"
        red1, _ = rd.redact(raw)
        red2, _ = rd.redact(raw)
        assert red1 == red2  # 결정적
        expect = hashlib.sha256(b"abc123def456ghi789").hexdigest()[:12]
        assert expect in red1


# ══════════════════════════════════════════════════════════════════════════════
# § audit 정직 (T-DPE-8) — 매칭 secret 원문/hash 절대 미기록
# ══════════════════════════════════════════════════════════════════════════════
class TestAuditNoSecretPlaintext:
    def test_audit_has_rulenames_and_count_no_secret(self):
        secret = "ABCDEFGHIJKLMNOP1234"
        raw = "token=" + secret
        _, audit = rd.redact(raw)
        assert audit["redaction_count"] >= 1
        assert len(audit["redaction_rules_fired"]) >= 1
        blob = json.dumps(audit, ensure_ascii=False)
        # 원문도, 그 sha256 도 audit 에 없어야 함 (audit-oracle 역전 차단)
        assert secret not in blob
        assert hashlib.sha256(secret.encode()).hexdigest() not in blob

    def test_audit_rules_are_closed_enum(self):
        _, audit = rd.redact("token=ABCDEFGHIJKLMNOP1234 and dev@x.com")
        for rule in audit["redaction_rules_fired"]:
            assert rule in rd.RULE_NAMES, f"미등재 rule 이름 유입: {rule}"

    def test_no_redaction_audit_flag_false(self):
        _, audit = rd.redact("just a normal harmless sentence")
        assert audit["redaction_applied"] is False
        assert audit["redaction_count"] == 0
        assert audit["redaction_rules_fired"] == []


# ══════════════════════════════════════════════════════════════════════════════
# § idempotent — redact(redact(x)) == redact(x)
# ══════════════════════════════════════════════════════════════════════════════
class TestIdempotent:
    @pytest.mark.parametrize("raw", [
        "token=ABCDEFGHIJKLMNOP1234",
        "Authorization: Bearer abcdef0123456789XYZ",
        "opened /home/mccho/.ssh/id_rsa",
        "email dev@example.com here",
        "session_id=abc123def456ghi789",
        "ghp_" + "B" * 36,
        "\n".join("VAR%d=v%d" % (i, i) for i in range(12)),
        "plain harmless text with scripts/lib/foo.py preserved",
    ])
    def test_double_redact_is_fixed_point(self, raw):
        once, _ = rd.redact(raw)
        twice, _ = rd.redact(once)
        assert twice == once, "redact 가 idempotent 아님 (재매칭 발생)"


# ══════════════════════════════════════════════════════════════════════════════
# § bounded cap (★"ReDoS-safe" 단정 금지 — 절단만 assert, honest-ceiling)
# ══════════════════════════════════════════════════════════════════════════════
class TestBoundedCap:
    def test_byte_cap_truncates_with_marker(self, monkeypatch):
        """byte-cap 초과 → 절단 마커 + 원본보다 짧음. cap 을 낮춰 truncation 로직만 검증
        (1 MiB 실입력은 impl 이 capped bytes 를 전량 스캔 = bounded-but-not-fast honest-ceiling
        이라 CI 시간 낭비 — 무해성/속도 단정 없이 '절단'만 assert)."""
        monkeypatch.setattr(rd, "BYTE_CAP", 200)
        raw = "x" * 500  # cap(200) 초과
        red, _ = rd.redact(raw)
        assert "[REDACT-BOUND:truncated]" in red
        # 절단으로 원본보다 짧음 (bounded degradation — 무해성 단정 아님)
        assert len(red.encode("utf-8")) < len(raw.encode("utf-8"))

    def test_line_cap_truncates_with_marker(self, monkeypatch):
        monkeypatch.setattr(rd, "LINE_CAP", 50)
        raw = "\n".join("line%d" % i for i in range(200))  # 50 라인 초과
        red, _ = rd.redact(raw)
        assert "[REDACT-BOUND:truncated]" in red
        assert red.count("\n") <= 50 + 5
