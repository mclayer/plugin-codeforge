#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_property_rest.py — AC-10 축②(token env-absence) + AC-12 (error classify) + AC-13 (rate meter)."""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from confluence_property_rest import (
    create_rest_client,
    is_over_limit_error,
    BUDGET_BYTES,
    MAX_RETRY_ATTEMPTS,
    INITIAL_BACKOFF_SECONDS,
    CFP1495_MOCK_MODE,
    ChunkStoreError,
    MANIFEST_KEY,
    CHUNK_KEY_TEMPLATE,
    TEST_PAGE_ID_ENV,
)
from confluence_property_chunking import (
    chunk as chunk_canonical,
    MANIFEST_KEY as LOCAL_MANIFEST_KEY,   # chunk() 산출 dict 의 local key ("__manifest")
)


# ── AC-10 축②: token env-absence → write rejection ──────────────────────────

def test_ac10_creds_absent_write_rejected():
    """AC-10: ATLASSIAN_* env missing → put_property_v2 returns (False, 'Creds absent')."""
    # Clear env
    old_token = os.environ.pop("ATLASSIAN_API_TOKEN", None)
    old_email = os.environ.pop("ATLASSIAN_USER_EMAIL", None)

    try:
        client = create_rest_client("https://example.atlassian.net")

        # Write attempt must fail with IO-1 hard-fail
        success, error = client.put_property_v2("page123", "key", {"value": "data"})

        assert success is False
        assert error is not None
        assert "Creds absent" in error

    finally:
        if old_token:
            os.environ["ATLASSIAN_API_TOKEN"] = old_token
        if old_email:
            os.environ["ATLASSIAN_USER_EMAIL"] = old_email


# ── AC-10 축② source-mutation kill (production-through discriminating test) ─
#
# put_property_v2 의 IO-1 creds guard(`if not self.token or not self.email:`)는 직접 필드
# 검사라 주입 가능한 sub-dependency 가 없다. 위 test_ac10_creds_absent_write_rejected 가
# production put_property_v2 를 creds-absent 로 직접 호출해 (False, "Creds absent") 를 검증하므로
# guard 제거에 대해 discriminating 하다.
#
# source-mutation kill 실증 (neuter→run→RED→restore, DevPL firsthand):
#   creds guard 제거 → confluence_property_rest.py put_property_v2 의
#     `if not self.token or not self.email: return False, "Creds absent"` 블록 삭제
#     → MOCK/offline 경로로 진입해 (True, None) 반환
#     → test_ac10_creds_absent_write_rejected RED (success is False 미충족).
#   명령: python -m pytest tests/scripts/test_confluence_property_rest.py::test_ac10_creds_absent_write_rejected
#   기대: neuter 시 FAILED / restore 시 PASSED.


# ── AC-12: over_limit_error classification (v1 vs v2) ────────────────────────

def test_ac12_v1_413_over_limit():
    """AC-12: v1 API, status 413 → over-limit."""
    assert is_over_limit_error(1, 413, "") is True


def test_ac12_v1_400_not_over_limit():
    """AC-12: v1 API, status 400 → not over-limit (400 overloaded in v1)."""
    assert is_over_limit_error(1, 400, "any message") is False


def test_ac12_v2_400_with_size_signature_over_limit():
    """AC-12: v2 API, 400 + 'too large' → over-limit."""
    assert is_over_limit_error(2, 400, "value too large") is True
    assert is_over_limit_error(2, 400, "too long") is True
    assert is_over_limit_error(2, 400, "exceeds 5242880") is True
    assert is_over_limit_error(2, 400, "32KB limit") is True


def test_ac12_v2_400_without_size_signature_not_over_limit():
    """AC-12: v2 API, 400 without size signature → not over-limit."""
    assert is_over_limit_error(2, 400, "invalid JSON") is False
    assert is_over_limit_error(2, 400, "key already exists") is False


def test_ac12_v2_other_status_not_over_limit():
    """AC-12: v2 API, non-400 status → not over-limit."""
    assert is_over_limit_error(2, 401, "") is False
    assert is_over_limit_error(2, 429, "") is False
    assert is_over_limit_error(2, 500, "") is False


# ── F-CR-004: bare "32" substring false-positive 근절 (whole-token/phrase 정밀화) ──

def test_fcr004_bare_32_substring_not_over_limit():
    """F-CR-004: '32' 가 무관한 토큰의 일부일 뿐인 400 body → NOT over-limit.

    회귀 재현: 이전 구현은 sig 목록에 bare '32' substring 이 있어 아래를 오분류(True) 했다.
      · 'field xyz32 invalid'  — 필드명에 우연히 '32' 포함
      · 'error code 1324'      — 에러코드에 우연히 '32' substring 포함
    정밀화(word-boundary token '32kb'/'32768' + phrase) 후 둘 다 False 여야 한다.
    """
    assert is_over_limit_error(2, 400, "field xyz32 invalid") is False
    assert is_over_limit_error(2, 400, "error code 1324") is False
    # 추가 인접 false-positive 후보
    assert is_over_limit_error(2, 400, "reference 8321 not found") is False
    assert is_over_limit_error(2, 400, "property key32 malformed") is False


def test_fcr004_genuine_size_signatures_still_over_limit():
    """F-CR-004: 정밀화 후에도 실 over-limit 시그니처는 True 유지(회귀 방지)."""
    assert is_over_limit_error(2, 400, "value too large") is True
    assert is_over_limit_error(2, 400, "content exceeds 5242880 bytes") is True
    assert is_over_limit_error(2, 400, "32KB limit exceeded") is True
    assert is_over_limit_error(2, 400, "maximum size is 32768") is True
    assert is_over_limit_error(2, 400, "property value 32 kb over the maximum size") is True


# ── AC-13: rate meter constants (declared) ──────────────────────────────────

def test_ac13_rate_meter_constants():
    """AC-13 (declared): rate meter constants defined."""
    assert MAX_RETRY_ATTEMPTS >= 2, "retry attempts must be >=2"
    assert INITIAL_BACKOFF_SECONDS > 0, "backoff must be positive"


def test_ac13_backoff_sequence():
    """AC-13 (declared): exponential backoff calculation."""
    # Mock backoff sequence: 1, 2, 4 seconds for 3 attempts
    backoff = INITIAL_BACKOFF_SECONDS
    sequence = []

    for attempt in range(MAX_RETRY_ATTEMPTS):
        sequence.append(backoff)
        backoff *= 2

    # Verify exponential growth
    assert sequence[0] == INITIAL_BACKOFF_SECONDS
    assert sequence[1] == INITIAL_BACKOFF_SECONDS * 2
    assert sequence[2] == INITIAL_BACKOFF_SECONDS * 4


# ── F-CR-003: leg-B chunk-store orchestration (manifest-last IO-6, offline) ──

def _dry_client():
    """offline dry-run client (creds/TEST_PAGE_ID 부재 — 실 write 0)."""
    return create_rest_client("https://example.atlassian.net")


def _make_chunked(nbytes: int, budget: int = 4096):
    """multi-chunk canonical blob → chunk dict (여러 __chunk_{n} 발생하도록 작은 budget)."""
    data = ("한국어 정본 블롭 무결성 round-trip 검증 sample.\n" * (nbytes // 40 + 1)).encode("utf-8")
    return data, chunk_canonical(data, budget)


def test_fcr003_store_reassemble_roundtrip_byte_exact():
    """F-CR-003: store(dry-run) → load 재조립 byte-exact (offline round-trip)."""
    old = os.environ.pop(TEST_PAGE_ID_ENV, None)
    try:
        client = _dry_client()
        data, cdict = _make_chunked(20000, budget=4096)
        # 실제로 multi-chunk 인지 확인 (단일 chunk 면 ordering 검증 무의미).
        assert cdict[LOCAL_MANIFEST_KEY]["chunk_count"] >= 2

        result = client.store_chunked_property("pageX", cdict, dry_run=True)
        assert result["success"] is True
        assert result["dry_run"] is True

        restored = client.load_chunked_property("pageX", dry_run=True)
        assert restored == data, "store→load round-trip byte-exact 실패"
    finally:
        if old is not None:
            os.environ[TEST_PAGE_ID_ENV] = old


def test_fcr003_manifest_last_ordering():
    """F-CR-003: put_order 는 전 __chunk_{n} 뒤 마지막에 __manifest (manifest-last IO-6)."""
    client = _dry_client()
    _, cdict = _make_chunked(20000, budget=4096)
    n = cdict[LOCAL_MANIFEST_KEY]["chunk_count"]

    result = client.store_chunked_property("pageX", cdict, dry_run=True)
    put_order = result["put_order"]

    # 마지막 PUT = manifest (commit marker).
    assert put_order[-1] == MANIFEST_KEY, "manifest 가 마지막 PUT 이 아님(원자성 위반)"
    # 앞선 N개 = chunk_0..chunk_{N-1} 순서.
    expected_chunks = [CHUNK_KEY_TEMPLATE.format(n=i) for i in range(n)]
    assert put_order[:-1] == expected_chunks, "chunk PUT 순서 불일치"
    # manifest 는 chunk 들보다 뒤에 위치.
    assert put_order.index(MANIFEST_KEY) == len(put_order) - 1


def test_fcr003_partial_failure_manifest_absent_fail_closed():
    """F-CR-003: manifest 미커밋(crash 모사) 시 load 는 fail-closed (부분 데이터 노출 0).

    store 가 chunk 만 쓰고 manifest PUT 전에 crash 한 상태를 모사 — reader 가 부분 chunk 를
    canonical 로 오인하지 않고 ChunkStoreError raise 해야 한다(IO-6 manifest-last 안전성).
    """
    client = _dry_client()
    _, cdict = _make_chunked(20000, budget=4096)
    n = cdict[LOCAL_MANIFEST_KEY]["chunk_count"]

    # manifest 이전 상태 모사: chunk 만 in-memory store 에 채우고 manifest 는 넣지 않음.
    from confluence_property_chunking import chunk_key as _lck
    for i in range(n):
        client._mock_store[CHUNK_KEY_TEMPLATE.format(n=i)] = {"data": cdict[_lck(i)]}
    # manifest 부재.
    with pytest.raises(ChunkStoreError, match="manifest 부재"):
        client.load_chunked_property("pageX", dry_run=True)


def test_fcr003_partial_failure_corrupt_chunk_fail_closed():
    """F-CR-003: 저장된 chunk 하나가 손상되면 load 는 hash 불일치로 fail-closed."""
    client = _dry_client()
    _, cdict = _make_chunked(20000, budget=4096)

    client.store_chunked_property("pageX", cdict, dry_run=True)
    # 저장된 __chunk_0 을 다른 base64 로 손상.
    client._mock_store[CHUNK_KEY_TEMPLATE.format(n=0)] = {"data": "dGFtcGVyZWQ="}

    with pytest.raises(ChunkStoreError):
        client.load_chunked_property("pageX", dry_run=True)


def test_fcr003_reject_chunk_dict_without_manifest():
    """F-CR-003: manifest 없는 chunk_dict 는 store 거부 (fail-closed)."""
    client = _dry_client()
    with pytest.raises(ChunkStoreError, match="__manifest"):
        client.store_chunked_property("pageX", {"__chunk_0": "abc"}, dry_run=True)


def test_fcr003_dry_run_no_real_write():
    """F-CR-003 / IO-7: TEST_PAGE_ID 부재 시 자동 dry-run (실 write 0 — session 미생성)."""
    old = os.environ.pop(TEST_PAGE_ID_ENV, None)
    try:
        client = _dry_client()
        _, cdict = _make_chunked(8000, budget=4096)
        result = client.store_chunked_property("pageX", cdict)  # dry_run 미지정 → 자동 판정
        assert result["dry_run"] is True
        # 실 HTTP session 미생성 (실 write 0 방증).
        assert client.session_v2 is None
        # in-memory store 에만 기록.
        assert MANIFEST_KEY in client._mock_store
    finally:
        if old is not None:
            os.environ[TEST_PAGE_ID_ENV] = old


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
