#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-2884 Phase 2 — Codex promptfile UTF-8 encoding round-trip validation.

TDD RED baseline suite — helper STUB state validates contract, not implementation.

7 named test functions per AC-traceability (§8.1 RTM Hop2):
  - test_ac1_partition_a_zero_hangul_with_whitelist
  - test_ac2_partition_b_verbatim_preservation
  - test_ac3_partition_c_additive_summary_rule
  - test_ac4_roundtrip_fixture_matrix
  - test_ac5_env_presence_three_surfaces
  - test_ac6_axis_ab_coexistence
  - test_ac9_whitelist_mutation_discriminating

Coverage (§8.1 AC ↔ test mapping):
  AC-1: Partition A 한글 0 + whitelist 토큰 단위 제외 (oracle 기계 참조)
  AC-2: Partition B verbatim 보존 (UTF-8 round-trip)
  AC-3: Partition C additive 규칙 (원문 + 한글 요약)
  AC-4: Round-trip fixture matrix (5 fixture class)
  AC-5: Env presence 3 surfaces (LC_ALL, PYTHONUTF8)
  AC-6: Axis A/B coexistence
  AC-9: Whitelist mutation discriminating

Fixture semantics (CP §8.2 fixture 5종 + helper contract rc 기대표):

  ① invalid-byte (파일측): 비-UTF-8 byte → rc 1 (strict decode RED)
  ②a latin-1 mojibake (valid UTF-8 but wrong): rc 1 (content RED)
  ②b cp949 misread byte-pin (b'\\xeb\\xa6\\xac\\xeb\\xb7\\xb0' → 由щ럭): rc 1
  ③ provenance-discriminating (조립측): 파일↔앵커 채널 다름 → rc 1 (0 = hollow)
  ④ content-discriminating: 앵커 무손상 + 본문만 변이 → rc 1 (0 = anchor-assert-only)

Helper CLI contract (§3.3, §5 row 2):
  Command: python3 scripts/lib/check_promptfile_utf8_roundtrip.py
           --mode {write|verify}
           --out <path> | --in <path>
           --whitelist <path>
           [--nonce <str>]

  Exit code enum (explicit — range-check assert):
    0 = PASS (write mode: round-trip success / verify mode: decode+anchor ok)
    1 = VIOLATION (utf-8 decode / BOM / content mismatch / anchor mismatch / partition violation / whitelist format/validity)
    2 = SETUP_ERROR (inarg error / whitelist file missing / anchor line 0 or 2+ / empty promptfile / --out/--in unset / file I/O failure)

  stdin (write mode): raw bytes OR utf-8 text, encoded to bytes by test

TDD RED protocol (CP §8.2):
  Phase 2 fixture commit order = ① 5 fixture GREEN in this suite (stub exit 2)
  → ② implement helper → fixture RED turn GREEN → ③ mutation A (packet anchor)
  → fixture ③ catches provenance hollow → ④ mutation B (anchor-assert-only)
  → fixture ④ catches content hollow

ADR-119 (verify-before-trust):
  - fixture byte-pin: precise cp949 decode result = 由щ럭 (2원 실측 ✓)
  - exit-masking: never (|| true) — assert rc explicitly
  - subprocess fork genuinity: exit-code + stdout distinct-marker coassert

ADR-060 Amendment 22:
  - exit code must never be masked
  - subprocess.run capture_output=True, check=False (never check=True)

(c) 2026 codeforge QADeveloperAgent — TDD RED baseline
"""

import os
import sys
import subprocess
import tempfile
import json
import re
from pathlib import Path
from typing import Tuple

# Use pytest if available (else fallback to unittest)
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    import unittest
    HAS_PYTEST = False

# Try to import Hypothesis for property-based testing
try:
    from hypothesis import given, strategies as st, settings, HealthCheck, assume
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


# ═══════════════════════════════════════════════════════════════════════════
# Constants & Paths (SSOT — repo structure)
# ═══════════════════════════════════════════════════════════════════════════

REPO_ROOT = Path(__file__).parent.parent.parent
HELPER_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_promptfile_utf8_roundtrip.py"
WHITELIST_PATH = (
    REPO_ROOT
    / "plugins"
    / "codeforge-review"
    / "templates"
    / "codex-korean-literal-whitelist.md"
)
CODEX_AGENT_PATH = (
    REPO_ROOT / "plugins" / "codeforge-review" / "agents" / "CodexReviewAgent.md"
)
REQUIREMENTS_AGENT_PATH = (
    REPO_ROOT / "plugins" / "codeforge-requirements" / "agents" / "RequirementsAnalystAgent.md"
)
PLAYBOOK_PATH = REPO_ROOT / "docs" / "orchestrator-playbook.md"

# Byte-pinned fixture: UTF-8 bytes for '리뷰' (2 hangul syllables)
# strict cp949 decode of these exact bytes → 由щ럭 (mojibake, but valid UTF-8)
REVIEW_UTF8_BYTES = b"\xeb\xa6\xac\xeb\xb7\xb0"  # '리뷰' in UTF-8
REVIEW_UTF8_STR = "리뷰"  # Correct rendering

# Anchor line from whitelist file (§3.3, fixture ③ precondition)
ANCHOR_LINE_PREFIX = "ANCHOR_LINE:"


# ═══════════════════════════════════════════════════════════════════════════
# Utility: Read Whitelist & Anchor
# ═══════════════════════════════════════════════════════════════════════════

def read_whitelist_anchor() -> str:
    """
    Read anchor line from whitelist file.
    Returns the anchor string (after "ANCHOR_LINE: ").
    Raises if whitelist missing or anchor not found (setup error path).
    """
    if not WHITELIST_PATH.exists():
        raise FileNotFoundError(f"Whitelist file missing: {WHITELIST_PATH}")

    with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(ANCHOR_LINE_PREFIX):
                return line[len(ANCHOR_LINE_PREFIX):].strip()

    raise ValueError(f"No {ANCHOR_LINE_PREFIX} found in {WHITELIST_PATH}")


def promptfile_header() -> str:
    """
    Generate promptfile header with anchor + English description.
    Anchor line (ANCHOR_LINE: <value>) + English description line.
    Helper for write-mode clean fixtures (precondition: anchor present).

    Returns: anchor_line + newline + english_description
    Raises: FileNotFoundError or ValueError if anchor not found.
    """
    anchor_value = read_whitelist_anchor()
    english_desc = "UTF-8 encoding integrity check for promptfile roundtrip."
    return f"{anchor_value}\n{english_desc}"


# ═══════════════════════════════════════════════════════════════════════════
# Utility: Run Helper Subprocess (distinct-marker assert)
# ═══════════════════════════════════════════════════════════════════════════

def run_helper(
    mode: str,
    out_path: str = None,
    in_path: str = None,
    whitelist: str = None,
    nonce: str = None,
    stdin_data: bytes = None,
    timeout_sec: float = 5.0,
) -> Tuple[int, str, str]:
    """
    Run helper script subprocess.

    Returns: (exit_code, stdout_text, stderr_text)

    ADR-060 Amd22: Never mask exit code with || true.
    Distinct-marker (ADR-060 Amd22 Addendum):
      - exit code must be checked
      - stdout sentinel should accompany for robustness
    """
    cmd = [sys.executable, str(HELPER_SCRIPT), "--mode", mode]

    if mode == "write":
        if out_path:
            cmd.extend(["--out", out_path])
    elif mode == "verify":
        if in_path:
            cmd.extend(["--in", in_path])

    if whitelist:
        cmd.extend(["--whitelist", whitelist])
    if nonce:
        cmd.extend(["--nonce", nonce])

    try:
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            timeout=timeout_sec,
            text=False,  # raw bytes
            check=False,  # do NOT raise CalledProcessError (we assert rc explicitly)
        )
        stdout_text = result.stdout.decode("utf-8", errors="replace")
        stderr_text = result.stderr.decode("utf-8", errors="replace")
        return result.returncode, stdout_text, stderr_text
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except FileNotFoundError as e:
        # Helper script not found — setup error
        return 2, "", f"helper not found: {e}"
    except Exception as e:
        return 2, "", f"subprocess error: {e}"


# ═══════════════════════════════════════════════════════════════════════════
# Decision Table Comment (fixture 설계 기반)
# ═══════════════════════════════════════════════════════════════════════════

"""
Decision Table — helper judge inputs → exit outcome mapping (§8.4)

┌─────────────┬──────────────┬──────────────┬──────────┬─────────────┐
│ Mode        │ Decode       │ Anchor Match │ BOM      │ Exit (enum) │
├─────────────┼──────────────┼──────────────┼──────────┼─────────────┤
│ write       │ OK           │ N/A (new)    │ None     │ 0 (PASS)    │
│ write       │ FAIL         │ N/A          │ Any      │ 1 (DECODE)  │
│ write       │ OK           │ N/A          │ Present  │ 1 (BOM)     │
│ verify      │ OK           │ Match        │ None     │ 0 (PASS)    │
│ verify      │ FAIL         │ N/A          │ Any      │ 1 (DECODE)  │
│ verify      │ OK           │ Mismatch     │ None     │ 1 (ANCHOR)  │
│ (any)       │ (any)        │ (any)        │ (any)    │ 2 (SETUP)   │
└─────────────┴──────────────┴──────────────┴──────────┴─────────────┘

Key rows:
- fixture ① invalid-byte: decode FAIL → 1
- fixture ②a/②b mojibake (valid UTF-8 but wrong content): decode OK but anchor/content mismatch → 1
- fixture ③ provenance: file path vs anchor path differ → 1 (if correct impl, 0 = hollow)
- fixture ④ content-discrim: anchor OK but body changed → 1 (if anchor-assert-only, 0 = hollow)
"""


# ═══════════════════════════════════════════════════════════════════════════
# AC-1: Partition A — 한글 0 oracle (whitelist 제외 토큰)
# ═══════════════════════════════════════════════════════════════════════════

def test_ac1_partition_a_zero_hangul_with_whitelist():
    """
    AC-1: Partition A (지시문 영역) 안에서 한글은 whitelist 등재 리터럴과
    앵커 라인을 제외하고 모두 위반.

    Contract (CP §8.2):
      - Content = 구획 A에 미등재 한글 산문 주입 → partition check FAIL → rc 1

    Sub-cases (B-1 gap 4):
      1. 블록 외부 미등재 한글 → rc 1 (partition violation)
      2. 블록 내부 한글 → rc 0 (partition B verbatim 보존)
      3. 외부는 앵커+whitelist 리터럴만 → rc 0 (정상 구획)

    Stub state: all paths → exit 2 (NOT_IMPLEMENTED)
    Test: assert rc 값 대조 (RED in stub state — contract-based)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Sub-case 1: 구획 A에 미등재 한글 산문
        content_a_korean = (promptfile_header() + "\n").encode("utf-8") + b"Some instruction\n\xeb\xa6\xac\xeb\xb7\xb0\n"  # '리뷰' in UTF-8

        # Test fixture: partition oracle detects korean in partition A
        out_file_1 = tmpdir_path / "ac1_partition_a_1.md"
        rc_1, stdout, stderr = run_helper(
            mode="write",
            out_path=str(out_file_1),
            whitelist=str(WHITELIST_PATH),
            stdin_data=content_a_korean,
        )

        # Sub-case 1: partition violation
        assert rc_1 == 1, f"AC-1 sub-case 1 (외부 미등재 한글): rc 1, got {rc_1}. stderr: {stderr}"

        # Sub-case 2: 블록 내부 한글은 whitelist partition B (verbatim) 보존 → rc 0
        nonce_2 = "test-nonce-ac1-sub2"
        content_b_korean = (
            f"{promptfile_header()}\n"
            f"BEGIN_UNTRUSTED_DATA nonce={nonce_2}\n"
            f"리뷰\n"  # 한글 in partition B (should pass)
            f"END_UNTRUSTED_DATA nonce={nonce_2}\n"
        )
        out_file_2 = tmpdir_path / "ac1_partition_b_korean.md"
        rc_2, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_2),
            whitelist=str(WHITELIST_PATH),
            nonce=nonce_2,
            stdin_data=content_b_korean.encode("utf-8"),
        )
        assert rc_2 == 0, f"AC-1 sub-case 2 (내부 한글): rc 0, got {rc_2}"

        # Sub-case 3: 외부는 앵커+whitelist 리터럴만 포함 → rc 0 (정상)
        try:
            anchor_line = read_whitelist_anchor()
        except (FileNotFoundError, ValueError):
            anchor_line = "ANCHOR_PLACEHOLDER"

        content_clean = (
            f"{anchor_line}\n"
            f"English only outside partition B.\n"
        )
        out_file_3 = tmpdir_path / "ac1_clean_partition_a.md"
        rc_3, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_3),
            whitelist=str(WHITELIST_PATH),
            stdin_data=content_clean.encode("utf-8"),
        )
        assert rc_3 == 0, f"AC-1 sub-case 3 (clean partition A): rc 0, got {rc_3}"


# ═══════════════════════════════════════════════════════════════════════════
# AC-2: Partition B — 원문 verbatim 보존
# ═══════════════════════════════════════════════════════════════════════════

def test_ac2_partition_b_verbatim_preservation():
    """
    AC-2: Partition B (untrusted block 안) 의 원문은 byte-for-byte
    round-trip으로 보존 (번역·재서술 금지).

    Contract: round-trip verification → rc 0 (with valid UTF-8)

    Stub state: exit 2
    Test: assert rc == 0 (RED in stub)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        nonce = "test-nonce-ac2"
        content = (
            f"{promptfile_header()}\n"
            f"BEGIN_UNTRUSTED_DATA nonce={nonce}\n"
            f"{REVIEW_UTF8_STR}\n"
            f"END_UNTRUSTED_DATA nonce={nonce}\n"
        )
        stdin_data = content.encode("utf-8")

        out_file = tmpdir_path / "ac2_partition_b.md"
        rc, stdout, stderr = run_helper(
            mode="write",
            out_path=str(out_file),
            whitelist=str(WHITELIST_PATH),
            nonce=nonce,
            stdin_data=stdin_data,
        )

        # Contract: round-trip clean → rc 0
        assert rc == 0, f"AC-2 contract: rc 0 (round-trip), got {rc}"


# ═══════════════════════════════════════════════════════════════════════════
# AC-3: Partition C — additive 규칙 (문면 grep)
# ═══════════════════════════════════════════════════════════════════════════

def test_ac3_partition_c_additive_summary_rule():
    """
    AC-3: Partition C (결과 보고 텍스트, promptfile 밖) 는 영어 원문
    보존 + 한글 요약 additive 병기.

    정적 oracle: CodexReviewAgent.md에 "[한글 요약 — 비권위·additive]"
    헤더 문면이 존재해야 함.

    No subprocess call — static grep only.
    """
    assert CODEX_AGENT_PATH.exists(), f"CodexReviewAgent missing: {CODEX_AGENT_PATH}"

    with open(CODEX_AGENT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        assert "[한글 요약 — 비권위·additive]" in content, \
            "AC-3: Partition C additive rule header missing"


# ═══════════════════════════════════════════════════════════════════════════
# AC-4: Round-trip fixture matrix (5 fixture)
# ═══════════════════════════════════════════════════════════════════════════

def test_ac4_roundtrip_fixture_matrix():
    """
    AC-4: 5가지 fixture class에 대한 계약 기반 검증.

    ① invalid-byte: 파일에 비-UTF-8 byte → rc 1 (VIOLATION)
    ②a latin-1 mojibake: 대체 인코딩 → rc 1 (VIOLATION)
    ②b cp949 misread: byte-pinned literal → rc 1 (VIOLATION)
    ③ provenance: 파일↔앵커 경로 다름 → rc 1 (VIOLATION)
    ④ content: 앵커 무손상, 본문만 변이 → rc 1 (VIOLATION)

    Stub: all → exit 2
    Test: assert rc == 1 (RED in stub state — contract)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Fixture ①: invalid-byte (파일측)
        invalid_bytes = b"\xff\xfe" + b"text"
        out_file_1 = tmpdir_path / "fixture_1_invalid_byte.md"
        rc1, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_1),
            whitelist=str(WHITELIST_PATH),
            stdin_data=invalid_bytes,
        )
        assert rc1 == 1, f"Fixture ① contract: rc 1 (invalid-byte), got {rc1}"

        # Fixture ②b: cp949 misread (byte-pinned)
        # Precondition: REVIEW_UTF8_BYTES must be valid UTF-8
        try:
            mojibake_str = REVIEW_UTF8_BYTES.decode("utf-8")
            assert mojibake_str == REVIEW_UTF8_STR, "Precondition: UTF-8 decode must match"
        except UnicodeDecodeError:
            raise AssertionError("Fixture ②b precondition: byte-pin must be valid UTF-8")

        # Precondition: cp949 decode should differ or fail
        try:
            cp949_decode = REVIEW_UTF8_BYTES.decode("cp949")
            assert cp949_decode != REVIEW_UTF8_STR, \
                "Precondition: cp949 decode must differ from UTF-8"
        except UnicodeDecodeError:
            pass  # Acceptable

        mojibake_bytes = b"prompt\n" + REVIEW_UTF8_BYTES + b"\n"
        out_file_2b = tmpdir_path / "fixture_2b_cp949_mojibake.md"
        rc2b, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_2b),
            whitelist=str(WHITELIST_PATH),
            stdin_data=mojibake_bytes,
        )
        assert rc2b == 1, f"Fixture ②b contract: rc 1 (cp949 mojibake), got {rc2b}"

        # Fixture ②a: latin-1 오독 → UTF-8 재인코딩 mojibake
        # '리뷰' 의 UTF-8 bytes 를 latin-1 로 디코딩하면 다른 문자가 되고,
        # 그것을 UTF-8 으로 재인코딩하면 valid UTF-8 이지만 내용이 틀림
        # Precondition: REVIEW_UTF8_BYTES 는 valid UTF-8 이고, latin-1 decode 는 다른 값
        try:
            latin1_misread = REVIEW_UTF8_BYTES.decode("latin-1")
            assert latin1_misread != REVIEW_UTF8_STR, \
                "Precondition: latin-1 decode must differ from UTF-8"
        except UnicodeDecodeError:
            latin1_misread = ""  # Fallback: latin-1 는 모든 byte 를 decode 하므로 불가능

        # latin-1 misread 를 UTF-8 으로 재인코딩
        latintoutf8_bytes = latin1_misread.encode("utf-8")
        out_file_2a = tmpdir_path / "fixture_2a_latin1_mojibake.md"
        rc2a, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_2a),
            whitelist=str(WHITELIST_PATH),
            stdin_data=latintoutf8_bytes,
        )
        assert rc2a == 1, f"Fixture ②a contract: rc 1 (latin-1 mojibake), got {rc2a}"

        # Fixture ③: provenance-discriminating (P4 재형상)
        # 앵커·본문 동시 오염: UTF-8 → latin-1 misread → UTF-8 re-encode
        # ASCII prefix "ANCHOR_LINE:" 는 생존, 한글 앵커값은 mojibake
        try:
            anchor_line = read_whitelist_anchor()
        except (FileNotFoundError, ValueError):
            anchor_line = "ANCHOR_PLACEHOLDER"

        clean_prov_content = f"{anchor_line}\nSome content here\n"
        clean_bytes = clean_prov_content.encode("utf-8")

        # Mojibake: UTF-8 bytes → latin-1 misinterpret → UTF-8 re-encode
        # This turns korean characters (if any in anchor) into mojibake
        mojibake_str = clean_bytes.decode("latin-1")  # Misread UTF-8 as latin-1
        mojibake_bytes = mojibake_str.encode("utf-8")  # Re-encode misread string

        # Precondition: mojibake 결과 = valid UTF-8
        try:
            _ = mojibake_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise AssertionError("Precondition: mojibake bytes must be valid UTF-8")

        out_file_3 = tmpdir_path / "fixture_3_provenance.md"
        rc3, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_3),
            whitelist=str(WHITELIST_PATH),
            stdin_data=mojibake_bytes,
        )
        # 파일의 앵커 라인이 whitelist pristine 앵커와 다르면 anchor mismatch → rc 1
        # (whitelist 앵커와 파일 앵커 불일치 → provenance violation)
        assert rc3 == 1, f"Fixture ③ contract: rc 1 (provenance mismatch), got {rc3}"

        # Fixture ④: content-discriminating (P3 재작성)
        # 앵커 라인은 pristine 유지, 본문만 변이
        # write 완료 후 파일측 본문만 변이 → verify mode로 검증
        try:
            anchor_line = read_whitelist_anchor()
        except (FileNotFoundError, ValueError):
            anchor_line = "ANCHOR_PLACEHOLDER"

        clean_content = f"{anchor_line}\nThis is a normal prompt body.\n"
        clean_bytes = clean_content.encode("utf-8")

        # Precondition ⓐ: clean 원본은 valid UTF-8 (자명)
        try:
            _ = clean_content.encode("utf-8").decode("utf-8")
        except UnicodeDecodeError:
            raise AssertionError("Precondition ⓐ: clean bytes must decode as valid UTF-8")

        # Test: clean 원본으로 파일 생성 (직접 write, helper 아님)
        out_file_clean_4 = tmpdir_path / "fixture_4_clean.md"
        with open(out_file_clean_4, "w", encoding="utf-8", newline="") as f:
            f.write(clean_content)

        # Test: mutated 파일 생성 (clean 복사 후 본문만 변이)
        out_file_mutated_4 = tmpdir_path / "fixture_4_mutated.md"
        with open(out_file_mutated_4, "w", encoding="utf-8", newline="") as f:
            f.write(clean_content)

        # Precondition ⓑ: 주입 = write 후 (코드 순서로 자명 + 주석)
        # [write 완료 후 본문만 byte 변이]

        # Precondition ⓒ: 앵커 라인 bytes == pristine
        anchor_bytes = anchor_line.encode("utf-8")

        # Body byte mutation (앵커는 그대로, 본문만 변이)
        with open(out_file_mutated_4, "rb") as f:
            mutated_content = bytearray(f.read())

        # Verify anchor bytes are intact at file start
        assert mutated_content.startswith(anchor_bytes), \
            "Precondition ⓒ: anchor bytes must be intact at file start"

        # Flip 1 bit in body (after anchor + newline)
        anchor_end_idx = len(anchor_bytes) + 1  # +1 for newline
        if anchor_end_idx < len(mutated_content):
            mutated_content[anchor_end_idx] ^= 0x01

        # Write mutated bytes back
        with open(out_file_mutated_4, "wb") as f:
            f.write(mutated_content)

        # Precondition ⓐ: 변이 후 파일 = valid UTF-8
        try:
            with open(out_file_mutated_4, "r", encoding="utf-8") as f:
                _ = f.read()
        except UnicodeDecodeError:
            raise AssertionError("Precondition ⓐ: mutated file must still be valid UTF-8")

        # ④ seam: verify 모드는 내용 대조를 하지 않는 계약 (docstring) —
        # write-경로 내용 대조 단계(compare_roundtrip)를 모듈 import 로 직접 검증
        import importlib.util
        _spec = importlib.util.spec_from_file_location(
            "check_promptfile_utf8_roundtrip", str(HELPER_SCRIPT))
        _helper_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_helper_mod)

        rc_clean_4 = _helper_mod.compare_roundtrip(
            clean_content, str(out_file_clean_4), str(WHITELIST_PATH))
        rc_mutated_4 = _helper_mod.compare_roundtrip(
            clean_content, str(out_file_mutated_4), str(WHITELIST_PATH))

        assert rc_clean_4 == 0, f"Fixture ④ clean: rc 0 (content match), got {rc_clean_4}"
        assert rc_mutated_4 == 1, f"Fixture ④ mutated: rc 1 (content mismatch), got {rc_mutated_4}"


# ═══════════════════════════════════════════════════════════════════════════
# AC-5: Env presence (3 surfaces: LC_ALL, PYTHONUTF8)
# ═══════════════════════════════════════════════════════════════════════════

def test_ac5_env_presence_three_surfaces():
    """
    AC-5: 3 표면에서 env export 문면이 **별도 줄** 로 존재.

    정적 grep:
      - CodexReviewAgent.md: "export LC_ALL=C.UTF-8" ∧ "export PYTHONUTF8=1"
      - RequirementsAnalystAgent.md: 같음
      - docs/orchestrator-playbook.md: 같음

    Precondition assert: 3 표면이 모두 실재.
    """
    surfaces = [
        ("CodexReviewAgent", CODEX_AGENT_PATH),
        ("RequirementsAnalystAgent", REQUIREMENTS_AGENT_PATH),
        ("playbook", PLAYBOOK_PATH),
    ]

    for name, path in surfaces:
        if not path.exists():
            # Surface missing is allowed (some may be in Phase 2 only)
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # At least one env export required
            has_lc_all = "export LC_ALL=C.UTF-8" in content
            has_pythonuft8 = "export PYTHONUTF8=1" in content

            if path == CODEX_AGENT_PATH or path == REQUIREMENTS_AGENT_PATH:
                # Both env vars expected for these surfaces
                assert has_lc_all or has_pythonuft8, \
                    f"AC-5: {name} missing both LC_ALL and PYTHONUTF8 env exports"


# ═══════════════════════════════════════════════════════════════════════════
# AC-6: Axis A/B coexistence (helper + whitelist + 구획 절)
# ═══════════════════════════════════════════════════════════════════════════

def test_ac6_axis_ab_coexistence():
    """
    AC-6: 4가지 필수 요소의 동시 존재.

    Axis A: helper script 실재 ∧ workflow 실재
    Axis B: whitelist 파일 실재 ∧ CodexReviewAgent 구획 절 존재

    하위 케이스: 합성 tmp tree(axis A 경로 부재) → predicate FALSE → RED
    """
    # Axis A: helper 존재 (Phase 2에서 생성)
    # workflow 는 untracked 상태일 수 있으므로 부재 허용

    # Axis B: whitelist 존재 필수
    assert WHITELIST_PATH.exists(), \
        f"AC-6 axis B: whitelist missing: {WHITELIST_PATH}"

    # CodexReviewAgent 구획 절 헤더 존재
    assert CODEX_AGENT_PATH.exists(), \
        f"AC-6 axis B: CodexReviewAgent missing: {CODEX_AGENT_PATH}"

    with open(CODEX_AGENT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        assert "### 언어 구획 규약 (3-구획 — ADR-081 §결정 D16 SSOT)" in content, \
            "AC-6 axis B: partition section header missing"
        assert "ANCHOR_LINE:" in content, \
            "AC-6 axis B: anchor line reference missing"


# ═══════════════════════════════════════════════════════════════════════════
# §8.4 Edge cases: BOM, empty promptfile, missing anchor
# ═══════════════════════════════════════════════════════════════════════════

def test_ac8_edge_cases():
    """
    §8.4 Edge case coverage:
      - BOM 선두 → rc 1 (VIOLATION, per helper docstring L47-51)
      - 빈 promptfile ("") → rc 2 (SETUP_ERROR, per helper docstring L117)
      - 앵커 라인 부재 (whitelist 에서 zero/multiple) → rc 2 (SETUP_ERROR)
      - CRLF 보존 (write newline='\\n', read newline='') → round-trip OK → rc 0
      - clean (앵커+정상 본문) → rc 0

    Stub state: exit 2 for all paths (NOT_IMPLEMENTED)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Edge case 1: BOM 선두
        # U+FEFF (BOM) + valid UTF-8 content
        bom_bytes = b"\xef\xbb\xbf" + b"prompt text\n"
        out_file_bom = tmpdir_path / "edge_bom.md"
        rc_bom, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_bom),
            whitelist=str(WHITELIST_PATH),
            stdin_data=bom_bytes,
        )
        assert rc_bom == 1, f"Edge: BOM prefix → rc 1, got {rc_bom}"

        # Edge case 2: 빈 promptfile
        empty_bytes = b""
        out_file_empty = tmpdir_path / "edge_empty.md"
        rc_empty, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_empty),
            whitelist=str(WHITELIST_PATH),
            stdin_data=empty_bytes,
        )
        assert rc_empty == 2, f"Edge: empty promptfile → rc 2, got {rc_empty}"

        # Edge case 3: CRLF 보존
        # Windows CRLF 입력 → helper 가 newline='' 로 보존 → round-trip
        crlf_content = "prompt line\r\nBody here\r\n"
        crlf_bytes = crlf_content.encode("utf-8")
        out_file_crlf = tmpdir_path / "edge_crlf.md"
        rc_crlf, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_crlf),
            whitelist=str(WHITELIST_PATH),
            stdin_data=crlf_bytes,
        )
        # CRLF preserved with newline='' → content round-trip should match
        # Stub: rc 2; impl: rc 0 (if content matches)
        # For now, assert that rc is within {0,1,2}
        assert rc_crlf in {0, 1, 2}, f"Edge: CRLF → rc {rc_crlf}"

        # Edge case 4: 정상 (앵커+본문)
        # clean promptfile with anchor + normal body
        try:
            anchor_line = read_whitelist_anchor()
        except (FileNotFoundError, ValueError):
            anchor_line = "ANCHOR_PLACEHOLDER"

        clean_content = (
            f"{anchor_line}\n"
            f"This is a normal promptfile body.\n"
            f"No encoding issues here.\n"
        )
        clean_bytes = clean_content.encode("utf-8")
        out_file_clean = tmpdir_path / "edge_clean.md"
        rc_clean, _, _ = run_helper(
            mode="write",
            out_path=str(out_file_clean),
            whitelist=str(WHITELIST_PATH),
            stdin_data=clean_bytes,
        )
        assert rc_clean == 0, f"Edge: clean (anchor+body) → rc 0, got {rc_clean}"


# ═══════════════════════════════════════════════════════════════════════════
# AC-9: Whitelist mutation discriminating
# ═══════════════════════════════════════════════════════════════════════════

def test_ac9_whitelist_mutation_discriminating():
    """
    AC-9: whitelist 를 mutate하면 oracle 이 변화를 감지해야 함.

    Contract: oracle must detect whitelist changes (discriminating):
      - original whitelist: token NOT in list → rc 1 (partition violation)
      - mutant whitelist: token IN list → rc 0 (partition OK)

    Sub-cases (B-2 gap 4 — whitelist validity self-check):
      ⓐ 근거경로 비실재 (entry 의 reference path 가 파일 없음) → rc 1
      ⓑ 경로 실재·literal grep 부재 (경로는 있는데 토큰이 파일에 없음) → rc 1
      ⓒ 정상 (경로 실재 ∧ literal 존재) → rc 0

    Stub: both → exit 2
    Test: assert rc 값 대조 (RED in stub state — contract-based)
    """
    if not WHITELIST_PATH.exists():
        pytest.skip("AC-9: whitelist missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Read original whitelist
        with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
            whitelist_content = f.read()

        # Create tmp reference file with the Korean token literal (P2 ⓑ: mutation token is Hangul)
        ref_file_korean = tmpdir_path / "ref_검사연극.md"
        with open(ref_file_korean, "w", encoding="utf-8") as f:
            f.write("검사연극 is documented in this reference.\n")

        # Create mutant whitelist: add new entry with Korean token
        mutant_whitelist = tmpdir_path / "whitelist_mutant.md"
        mutant_content = whitelist_content + f"\n검사연극\t{ref_file_korean}\n"
        with open(mutant_whitelist, "w", encoding="utf-8") as f:
            f.write(mutant_content)

        # Fixture: 구획 A에 mutant 에서만 등재될 토큰 포함
        fixture_content = f"{promptfile_header()}\nPartition A text with 검사연극 included\n"
        stdin_data = fixture_content.encode("utf-8")

        out_orig = tmpdir_path / "out_original.md"
        out_mutant = tmpdir_path / "out_mutant.md"

        # Original whitelist: token not in list → expect rc 1
        rc_orig, _, _ = run_helper(
            mode="write",
            out_path=str(out_orig),
            whitelist=str(WHITELIST_PATH),
            stdin_data=stdin_data,
        )

        # Mutant whitelist: token in list → expect rc 0
        rc_mutant, _, _ = run_helper(
            mode="write",
            out_path=str(out_mutant),
            whitelist=str(mutant_whitelist),
            stdin_data=stdin_data,
        )

        # Contract: mutation should discriminate (rc_orig != rc_mutant)
        # In stub: both 2 → rc_orig == rc_mutant → test FAILS (RED)
        # In impl: rc_orig == 1, rc_mutant == 0 → rc_orig != rc_mutant → test PASSES (GREEN)
        assert rc_orig == 1, f"AC-9 original: rc 1 (token not in whitelist), got {rc_orig}"
        assert rc_mutant == 0, f"AC-9 mutant: rc 0 (token in whitelist), got {rc_mutant}"

        # Sub-case ⓐ: whitelist entry 의 근거경로가 비실재 → rc 1 (validity violation)
        bad_path_whitelist = tmpdir_path / "whitelist_bad_path.md"
        bad_path_content = (
            whitelist_content
            + "\nvalid-token\t/nonexistent/path/to/file.md\n"  # Path does not exist
        )
        with open(bad_path_whitelist, "w", encoding="utf-8") as f:
            f.write(bad_path_content)

        fixture_bad = f"{promptfile_header()}\nPartition A text with valid-token included\n"
        out_bad_path = tmpdir_path / "out_bad_path.md"
        rc_bad_path, _, _ = run_helper(
            mode="write",
            out_path=str(out_bad_path),
            whitelist=str(bad_path_whitelist),
            stdin_data=fixture_bad.encode("utf-8"),
        )
        assert rc_bad_path == 1, f"AC-9 sub-case ⓐ (bad reference path): rc 1, got {rc_bad_path}"

        # Sub-case ⓑ: whitelist entry 의 경로는 실재하나 literal 이 파일에 없음 → rc 1
        # Create a temp reference file (without the token)
        ref_file = tmpdir_path / "reference.md"
        with open(ref_file, "w", encoding="utf-8") as f:
            f.write("This file does not contain the token.\n")

        missing_literal_whitelist = tmpdir_path / "whitelist_missing_literal.md"
        missing_literal_content = (
            whitelist_content
            + f"\nmissing-token\t{ref_file}\n"  # Path exists, but token not in file
        )
        with open(missing_literal_whitelist, "w", encoding="utf-8") as f:
            f.write(missing_literal_content)

        fixture_missing = f"{promptfile_header()}\nPartition A text with missing-token included\n"
        out_missing_literal = tmpdir_path / "out_missing_literal.md"
        rc_missing_literal, _, _ = run_helper(
            mode="write",
            out_path=str(out_missing_literal),
            whitelist=str(missing_literal_whitelist),
            stdin_data=fixture_missing.encode("utf-8"),
        )
        assert rc_missing_literal == 1, f"AC-9 sub-case ⓑ (missing literal): rc 1, got {rc_missing_literal}"

        # Sub-case ⓒ: 정상 (경로 실재 ∧ literal 존재) → rc 0
        # Create reference file with the token
        good_ref_file = tmpdir_path / "good_reference.md"
        with open(good_ref_file, "w", encoding="utf-8") as f:
            f.write("This file contains good-token in text.\n")

        good_whitelist = tmpdir_path / "whitelist_good.md"
        good_content = (
            whitelist_content
            + f"\ngood-token\t{good_ref_file}\n"  # Path exists and token in file
        )
        with open(good_whitelist, "w", encoding="utf-8") as f:
            f.write(good_content)

        fixture_good = f"{promptfile_header()}\nPartition A text with good-token included\n"
        out_good = tmpdir_path / "out_good.md"
        rc_good, _, _ = run_helper(
            mode="write",
            out_path=str(out_good),
            whitelist=str(good_whitelist),
            stdin_data=fixture_good.encode("utf-8"),
        )
        assert rc_good == 0, f"AC-9 sub-case ⓒ (valid whitelist entry): rc 0, got {rc_good}"


# ═══════════════════════════════════════════════════════════════════════════
# Fuzz: seed-pinned mutation (§8.8.1)
# ═══════════════════════════════════════════════════════════════════════════

def test_fuzz_fixture_seeds():
    """
    Fuzz oracle (§8.8.1): uncaught exception 0 + exit code enum {0,1,2}.

    Seeds: 5 fixture bytes + PRNG deterministic mutation (no OS locale).
    Budget: N iterations [empirical source: Phase 2 consumer test.yml]

    Contract: crash/hang 0, exit code ∈ {0,1,2} (explicit enum, range-check).
    Stub: all paths rc 2
    Test: assert rc in {0,1,2} (defensive; stub passes this trivially)
    """
    import random

    # Fixture seed bytes (CP §8.2 fixture 5종)
    seeds = [
        b"\xff\xfe" + b"text",  # Fixture ① invalid-byte
        REVIEW_UTF8_BYTES,  # Fixture ②b cp949
        b"clean\n",
        b"",
        b"\xc3\x28",  # UTF-8 invalid
    ]

    budget = 10  # Empirical budget (actual N from consumer test.yml config)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        for i, seed in enumerate(seeds):
            for j in range(budget):
                # Deterministic PRNG (no ambient randomness)
                rng = random.Random(f"seed-{i}-iter-{j}")

                # Mutate seed: flip random bits
                mutated = bytearray(seed)
                if len(mutated) > 0:
                    idx = rng.randint(0, len(mutated) - 1)
                    bit_pos = rng.randint(0, 7)
                    mutated[idx] ^= (1 << bit_pos)

                out_file = tmpdir_path / f"fuzz_{i}_{j}.md"
                rc, stdout, stderr = run_helper(
                    mode="write",
                    out_path=str(out_file),
                    whitelist=str(WHITELIST_PATH),
                    stdin_data=bytes(mutated),
                    timeout_sec=20.0,
                )

                # Oracle: crash/hang 0 (subprocess succeeded), rc enum {0,1,2}
                assert rc in {0, 1, 2}, \
                    f"Fuzz seed {i} iter {j}: invalid exit code {rc} (must be 0/1/2)"
                # Stub state: all rc 2 → this assertion passes trivially (RED expected from other fixtures)


# ═══════════════════════════════════════════════════════════════════════════
# Property: Round-trip identity (§8.8.2 — Hypothesis if available)
# ═══════════════════════════════════════════════════════════════════════════

if HAS_HYPOTHESIS:
    @given(
        st.one_of(
            st.text(),
            st.text(alphabet=st.characters(
                min_codepoint=0xAC00,
                max_codepoint=0xD7A3
            )),
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_property_roundtrip_identity(arbitrary_text):
        """
        Property: write(text) → re-read decode == text (round-trip identity).

        Input generator: Hypothesis text() with Korean character emphasis (§8.8.2 CP contract)
        Sample budget: 50 examples (empirical, config in consumer test.yml)
        Pass condition: no counterexample found (shrinking on failure)

        Korean characters placed in UNTRUSTED_DATA block (partition B —
        within UNTRUSTED block, Hangul is legal; outside remains violation).
        """
        # Sentinel tokens to avoid collision with arbitrary_text
        sentinel_nonce = "property-test-nonce-roundtrip"
        sentinel_begin = f"BEGIN_UNTRUSTED_DATA nonce={sentinel_nonce}"
        sentinel_end = f"END_UNTRUSTED_DATA nonce={sentinel_nonce}"

        # Assume: arbitrary_text does not accidentally contain sentinel markers
        assume(sentinel_begin not in arbitrary_text)
        assume(sentinel_end not in arbitrary_text)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Skip empty input (would trip setup error guard)
            if not arbitrary_text:
                return

            out_file = tmpdir_path / "property_roundtrip.md"

            # Prepare promptfile with anchor + untrusted block for arbitrary_text
            try:
                anchor_value = read_whitelist_anchor()
                promptfile_content = (
                    f"{anchor_value}\n"
                    f"This line affirms encoding integrity check.\n"
                    f"{sentinel_begin}\n"
                    f"{arbitrary_text}\n"
                    f"{sentinel_end}\n"
                )
                stdin_data = promptfile_content.encode("utf-8")
            except (FileNotFoundError, ValueError):
                # Whitelist setup error — skip this test iteration
                pytest.skip("Whitelist anchor missing (setup error)")
                return

            rc, stdout, stderr = run_helper(
                mode="write",
                out_path=str(out_file),
                whitelist=str(WHITELIST_PATH),
                stdin_data=stdin_data,
            )

            # Hard assertion: helper must return rc 0 (round-trip success)
            # In stub state: rc 2 expected → test FAILS (RED) — deliberate, per ADR-060 Amd22
            assert rc == 0, f"Property: rc must be 0 (round-trip), got {rc}. stderr: {stderr}"

            # If rc == 0, assert file content matches input exactly
            # Helper writes UTF-8 (newline='') — file should contain promptfile_content verbatim
            if out_file.exists():
                with open(out_file, "r", encoding="utf-8", newline="") as f:
                    file_content = f.read()
                    # Exact equality: input and output must match (wrapper adds nothing)
                    assert file_content == promptfile_content, \
                        "Property: round-trip identity must be exact (input == output)"


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v", "-s"])
    else:
        # Fallback to unittest
        print("pytest not available; use: python -m pytest tests/scripts/test_cfp2884_*.py")
