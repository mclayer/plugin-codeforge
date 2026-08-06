#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_property_rest.py — CFP-2889 discriminating suite D-1~D-13 (Change Plan §8).

Suite 2-분할 (§3.3 bootstrap 순환 절단):
  - suite-A (golden-비의존): D-1~D-6 + D-8~D-13 + 경계 tier A + Decision Table tier B
    — §9 step 1 gate. 고정 커맨드 `pytest tests/scripts/test_confluence_property_rest.py
    -m "not requires_golden" -q` (기본 호출에 마커 필터 금지 규범은 pytest.ini 주석 참조).
  - suite-B (`@pytest.mark.requires_golden`): D-7 + dry round-trip 계열
    — golden 커밋 후 step 6 gate. golden 부재 상태에서 실행되면 **명시 fail** (skip 금지,
    D-13 negative-control 이 그 거동 자체를 검증).

기존 16 함수 처분 census (Change Plan §5 #5):
  - 순수함수 분류기 7 (`test_ac12_*` 5 + `test_fcr004_*` 2) + 상수 1 (`test_ac13_rate_meter_constants`)
    + AC-10 재작성 1 = 9 존치/재작성
  - `test_ac13_backoff_sequence` = 폐기 (production 미행사 tautology — D-12 가 대체)
  - dry 경로 6 (fcr003 계열) = suite-B 재작성 5 (`requires_golden`) + manifest-reject 1 (suite-A —
    transport 미도달)

import 계보: production (measure.py·measurement_client)이 전건 `lib.` qualified 이므로 본 파일도
동일 계보로 import 한다 (bare/qualified 이중 import 는 모듈 인스턴스 2개 = 예외 클래스 identity
불일치 함정 — D6 주의 사항).

저작: QADeveloperAgent 1·2차 + DeveloperPL 인수 마감 (hollow 6곳 실구현 전환 — Orchestrator 지시).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest

# conftest 가 scripts/ + scripts/lib/ 를 sys.path 주입 — production 과 동일한 lib. 계보 사용.
from lib.ac_id import TIER_ENUM
from lib.confluence_property_rest import (
    BUDGET_BYTES,
    CHUNK_KEY_TEMPLATE,
    ChunkStoreError,
    ConfluencePropertyREST,
    GOLDEN_DIR_ENV,
    GoldenFixtureMissingError,
    INITIAL_BACKOFF_SECONDS,
    MANIFEST_KEY,
    MAX_RETRY_ATTEMPTS,
    PROPERTY_KEY_PREFIX,
    RATE_429_ABORT_THRESHOLD,
    RateAbortError,
    TEST_PAGE_ID_ENV,
    WRAP_OVERHEAD_BYTES,
    WriteAccounting,
    WriteCapExceeded,
    _SyntheticResponse,
    effective_chunk_budget,
    grouped_hex,
    sanitize_body_field,
    ungroup_hex,
)
from lib.confluence_property_chunking import (
    CONSERVATIVE_BUDGET,
    MANIFEST_KEY as LOCAL_MANIFEST_KEY,
    chunk as chunk_canonical,
    chunk_key as local_chunk_key,
    json_encoded_size,
)
from lib.confluence_measurement_client import (
    MeasurementRESTClient,
    safe_path,
    safe_path_or_drop,
)
import lib.confluence_property_rest as rest_module
import confluence_backward_measure as measure

REPO_ROOT = Path(__file__).resolve().parents[2]


# ════════════════════════════════════════════════════════════════════════════
# 존치 9 — 순수함수 분류기 7 + rate-meter 상수 1 (+ AC-10 은 하단 재작성)
# ════════════════════════════════════════════════════════════════════════════

def test_ac12_v1_413_over_limit():
    """AC-12: v1 API, status 413 → over-limit."""
    assert rest_module.is_over_limit_error(1, 413, "") is True


def test_ac12_v1_400_not_over_limit():
    """AC-12: v1 API, status 400 → not over-limit."""
    assert rest_module.is_over_limit_error(1, 400, "any message") is False


def test_ac12_v2_400_with_size_signature_over_limit():
    """AC-12: v2 API, 400 + size signature → over-limit."""
    assert rest_module.is_over_limit_error(2, 400, "value too large") is True
    assert rest_module.is_over_limit_error(2, 400, "too long") is True
    assert rest_module.is_over_limit_error(2, 400, "exceeds 5242880") is True
    assert rest_module.is_over_limit_error(2, 400, "32KB limit") is True


def test_ac12_v2_400_without_size_signature_not_over_limit():
    """AC-12: v2 API, 400 without size signature → not over-limit."""
    assert rest_module.is_over_limit_error(2, 400, "invalid JSON") is False
    assert rest_module.is_over_limit_error(2, 400, "key already exists") is False


def test_ac12_v2_other_status_not_over_limit():
    """AC-12: v2 API, non-400 status → not over-limit."""
    assert rest_module.is_over_limit_error(2, 401, "") is False
    assert rest_module.is_over_limit_error(2, 429, "") is False
    assert rest_module.is_over_limit_error(2, 500, "") is False


def test_fcr004_bare_32_substring_not_over_limit():
    """D-4 / F-CR-004: bare '32' substring false-positive 근절 회귀."""
    assert rest_module.is_over_limit_error(2, 400, "field xyz32 invalid") is False
    assert rest_module.is_over_limit_error(2, 400, "error code 1324") is False
    assert rest_module.is_over_limit_error(2, 400, "reference 8321 not found") is False
    assert rest_module.is_over_limit_error(2, 400, "property key32 malformed") is False


def test_fcr004_genuine_size_signatures_still_over_limit():
    """D-4 / F-CR-004: word-boundary 정밀화 후에도 실 시그니처는 True."""
    assert rest_module.is_over_limit_error(2, 400, "value too large") is True
    assert rest_module.is_over_limit_error(2, 400, "content exceeds 5242880 bytes") is True
    assert rest_module.is_over_limit_error(2, 400, "32KB limit exceeded") is True
    assert rest_module.is_over_limit_error(2, 400, "maximum size is 32768") is True
    assert rest_module.is_over_limit_error(2, 400, "property value 32 kb over the maximum size") is True


def test_ac13_rate_meter_constants():
    """AC-13: rate meter 상수 (retry = 최초 1 + 429-한정 1)."""
    assert MAX_RETRY_ATTEMPTS == 2
    assert INITIAL_BACKOFF_SECONDS > 0


# ════════════════════════════════════════════════════════════════════════════
# AC-10 재작성 — creds-absent live-path 거부 + IO-1 순서 오라클
# ════════════════════════════════════════════════════════════════════════════

def test_ac10_creds_absent_write_rejected(monkeypatch):
    """AC-10: creds 부재 + dry=False(live 경로) → local-reject, HTTP 0회·golden 0회.

    IO-1 순서 판정 (Orchestrator 질문의 답): `_upsert_impl` 은 creds 검사를
    `list_properties_v2`(transport·golden 로더) **이전**에 수행한다 — 순서 결함 아님.
    선행 라운드의 RED 는 테스트가 dry=False 를 누락해 auto-dry(mock transport) 경로로
    빠진 것이 원인 (dry-run 은 HTTP 0 이라 creds 요구 자체가 없다 — 설계 정합).

    순서 오라클: MeasurementRESTClient 는 `_perform_request` 마다 무조건 캡처 레코드를
    남기므로, creds 거부가 transport 이후라면 header_captures ≥ 1 이 된다 → == 0 단언이
    "transport 이전 거부" 를 기계적으로 판별한다 (mutant: creds 검사를 resolve 뒤로
    옮기면 GoldenFixtureMissingError 또는 captures ≥ 1 로 RED).
    """
    monkeypatch.delenv("ATLASSIAN_API_TOKEN", raising=False)
    monkeypatch.delenv("ATLASSIAN_USER_EMAIL", raising=False)
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)

    client = MeasurementRESTClient("https://example.atlassian.net", None, None)
    ok, envelope, err = client.upsert_property_v2("page123", "key", {"v": 1}, dry=False)

    assert ok is False
    assert envelope is None
    assert err is not None and err["origin"] == "local-reject"
    assert "Creds absent" in (err.get("message") or "")
    assert client.header_captures == [], "creds 거부가 transport 이후 — IO-1 순서 결함"


# ════════════════════════════════════════════════════════════════════════════
# D-1 / D-2: verdict 순수함수 (정직화 축 — 실호출)
# ════════════════════════════════════════════════════════════════════════════

def test_d1_verdict_storage_axis_empty():
    """D-1: 시나리오 0건 → declared (dict-truthy 회귀 mutant → RED)."""
    assert measure.verdict_storage_axis([]) == "declared"


def test_d1_verdict_storage_axis_write_success_false():
    """D-1: write_success=False 주입 → declared (구 L230 truthy 결함 재발 시 RED)."""
    assert measure.verdict_storage_axis(
        [{"write_success": False, "readback_byte_exact": True}]) == "declared"


def test_d1_verdict_storage_axis_readback_false():
    """D-1: read-back 불일치 주입 → declared (write 성공만으로 승격 금지)."""
    assert measure.verdict_storage_axis(
        [{"write_success": True, "readback_byte_exact": False}]) == "declared"


def test_d1_verdict_storage_axis_all_true():
    """D-1: 전 시나리오 GREEN → normative (관측 기반 승격 경로 실재)."""
    assert measure.verdict_storage_axis([
        {"write_success": True, "readback_byte_exact": True},
        {"write_success": True, "readback_byte_exact": True},
    ]) == "normative"


def test_d2_verdict_over_limit_server_observed_normative():
    """D-2: server-response ∧ over-limit ∧ 대조군 GREEN → normative."""
    assert measure.verdict_over_limit_axis([{
        "origin": "server-response", "http_status": 400,
        "classified_as": "over-limit", "control_pair_ok": True,
    }]) == "normative"


def test_d2_verdict_over_limit_local_reject_never_normative():
    """D-2: local-reject 는 어떤 조합에서도 normative 불가 (HTTP 0회 승격 = 구 결함 셀)."""
    assert measure.verdict_over_limit_axis([{
        "origin": "local-reject", "http_status": None,
        "classified_as": "over-limit", "control_pair_ok": True,
    }]) == "declared"


def test_d2_verdict_rate_axis_zero_records_declared():
    """D-2: 캡처 레코드 0건 → declared (구 AC-13 4분기 'observed-only' 대체 계약)."""
    assert measure.verdict_rate_axis([]) == "declared"


def test_d2_verdict_rate_axis_records_present_advisory():
    """D-2: 캡처 레코드 ≥1 → advisory (13a 실측-도달 if-then — §3.8)."""
    assert measure.verdict_rate_axis(
        [{"endpoint": "x", "http_status": 200}]) == "advisory"


# ════════════════════════════════════════════════════════════════════════════
# D-3: tier 기계 enum 결박 (fail-loud)
# ════════════════════════════════════════════════════════════════════════════

def test_d3_tier_enum_membership_exhaustive():
    """D-3: 3 verdict 함수의 출력 전건 ∈ TIER_ENUM ('observed-only' 재도입 mutant → RED)."""
    assert TIER_ENUM == ("normative", "declared", "advisory")
    outputs = set()
    for scenarios in ([], [{"write_success": True, "readback_byte_exact": True}],
                      [{"write_success": False, "readback_byte_exact": False}]):
        outputs.add(measure.verdict_storage_axis(scenarios))
    for obs in ([], [{"origin": "server-response", "classified_as": "over-limit",
                      "control_pair_ok": True}],
                [{"origin": "local-reject", "classified_as": None, "control_pair_ok": False}]):
        outputs.add(measure.verdict_over_limit_axis(obs))
    for records in ([], [{"h": 1}]):
        outputs.add(measure.verdict_rate_axis(records))
    assert outputs <= set(TIER_ENUM)
    assert "observed-only" not in outputs


def test_d3_tier_guard_fail_loud():
    """D-3: `_tier` 는 TIER_ENUM 비소속 토큰에 AssertionError (silent 통과 = RED)."""
    with pytest.raises(AssertionError, match="TIER_ENUM"):
        measure._tier("observed-only")


# ════════════════════════════════════════════════════════════════════════════
# D-5: 예산 계약 산술 (양방향 — 구 경로 위반 canary + 신 경로 준수)
# ════════════════════════════════════════════════════════════════════════════

def _wrap_size(b64_value: str) -> int:
    """store 가 전송하는 wrap(`{"data": <b64>}`) 의 JSON-encoded byte."""
    return json_encoded_size({"data": b64_value})


def test_d5_wrap_overhead_is_measured_not_declared():
    """D-5: WRAP_OVERHEAD_BYTES(선언 10) == 실측 wrap 증분 (선언-실측 괴리 mutant → RED)."""
    bare = json_encoded_size("x" * 100)
    wrap = _wrap_size("x" * 100)
    assert wrap - bare == WRAP_OVERHEAD_BYTES == 10


def test_d5_effective_budget_arithmetic():
    """D-5: effective_chunk_budget() == BUDGET_BYTES - WRAP_OVERHEAD_BYTES == 28662."""
    assert effective_chunk_budget() == BUDGET_BYTES - WRAP_OVERHEAD_BYTES == 28662


def test_d5_old_budget_violation_canary():
    """D-5 canary: 구 경로(CONSERVATIVE_BUDGET 직접 사용)는 wrap 후 +8B 위반 — 최초 RED 가
    정상이었던 결함의 재현 고정 (위반이 사라지면 서버/산술 전제가 바뀐 것 = 재검토 신호)."""
    data = ("한국어 검증 payload X" * 4000).encode("utf-8")
    old = chunk_canonical(data, CONSERVATIVE_BUDGET)
    old_max = max(_wrap_size(v) for k, v in old.items() if k.startswith("__chunk_"))
    assert old_max == BUDGET_BYTES + 8, "구 경로 +8B 위반 전제가 변했다 — D3 재검토"


def test_d5_new_budget_invariant_all_chunks():
    """D-5 불변식: chunk(x, effective_chunk_budget()) 전 chunk 가 wrap 후 ≤ BUDGET_BYTES."""
    data = ("한국어 검증 payload X" * 4000).encode("utf-8")
    new = chunk_canonical(data, effective_chunk_budget())
    for k, v in new.items():
        if k.startswith("__chunk_"):
            assert _wrap_size(v) <= BUDGET_BYTES


# ════════════════════════════════════════════════════════════════════════════
# D-6: upsert 프로토콜 orchestration (+ §8.5.3 replay·stale purge)
#   — 합성 최소 envelope = 로직 시뮬레이션 (shape-claim 아님. shape 검증 = suite-B golden)
# ════════════════════════════════════════════════════════════════════════════

class _FakeTransport:
    """`_perform_request` 대체 — 호출 기록 + 스크립트된 응답 (golden 불요 orchestration 오라클)."""

    def __init__(self, list_envelopes=None):
        self.calls = []
        self.list_envelopes = dict(list_envelopes or {})
        self.next_id = 500

    def __call__(self, method, path, *, body_bytes=None, params=None, dry=False, timeout=10):
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else None
        self.calls.append({"method": method, "path": path, "params": params, "body": body})
        if method == "GET":
            key = (params or {}).get("key")
            if key is None:
                results = [env for envs in self.list_envelopes.values() for env in envs]
            else:
                results = self.list_envelopes.get(key, [])
            return _SyntheticResponse(200, {}, json.dumps({"results": results}))
        if method == "POST":
            env = {"id": self.next_id, "key": body["key"], "value": body["value"],
                   "version": {"number": 1}}
            self.next_id += 1
            self.list_envelopes[body["key"]] = [env]
            return _SyntheticResponse(200, {}, json.dumps(env))
        if method == "PUT":
            return _SyntheticResponse(200, {}, json.dumps(
                {"id": 7, "key": body["key"], "value": body["value"],
                 "version": {"number": body["version"]["number"]}}))
        if method == "DELETE":
            return _SyntheticResponse(204, {}, "")
        return _SyntheticResponse(404, {}, "")

    def method_calls(self, method):
        return [c for c in self.calls if c["method"] == method]


def _harness_client(list_envelopes=None):
    client = ConfluencePropertyREST("https://example.atlassian.net", "tok-fake", "e@x.io")
    fake = _FakeTransport(list_envelopes)
    client._perform_request = fake          # 인스턴스 속성 shadow — production 오케스트레이션 그대로
    return client, fake


def test_d6_upsert_existing_key_put_version_n_plus_1():
    """D-6: resolve 1건 존재 → POST 0 ∧ PUT by id ∧ version n+1 송신 (n+1 제거 mutant → RED)."""
    envelope = {"id": 7, "key": "k", "value": 0, "version": {"number": 4}}
    client, fake = _harness_client({"k": [envelope]})
    ok, env, err = client.upsert_property_v2("p1", "k", {"v": 2}, dry=False)
    assert ok is True and err is None
    assert fake.method_calls("POST") == [], "기존 key 에 POST 발생 — upsert 프로토콜 위반"
    puts = fake.method_calls("PUT")
    assert len(puts) == 1
    assert puts[0]["path"].endswith("/properties/7")
    assert puts[0]["body"]["version"]["number"] == 5


def test_d6_upsert_absent_key_post():
    """D-6: resolve 0건 → POST (version 미송신 — 결정 12)."""
    client, fake = _harness_client({})
    ok, env, err = client.upsert_property_v2("p1", "k-new", {"v": 1}, dry=False)
    assert ok is True and err is None
    posts = fake.method_calls("POST")
    assert len(posts) == 1
    assert "version" not in posts[0]["body"]
    assert fake.method_calls("PUT") == []


def test_d6_upsert_multi_resolve_fail_closed():
    """D-6: resolve 다중 → fail-closed (중복 생성 방지 — POST·PUT 0)."""
    dup = [{"id": 1, "key": "k", "value": 0, "version": {"number": 1}},
           {"id": 2, "key": "k", "value": 0, "version": {"number": 1}}]
    client, fake = _harness_client({"k": dup})
    ok, env, err = client.upsert_property_v2("p1", "k", {"v": 1}, dry=False)
    assert ok is False and err is not None
    assert "다중" in (err.get("message") or "")
    assert fake.method_calls("POST") == [] and fake.method_calls("PUT") == []


def test_d6_replay_reupsert_no_duplicate_post():
    """§8.5.3 replay ①②: 동일 key 재-upsert → POST 재발생 0 (orphan 잔존 재실행 수렴)."""
    client, fake = _harness_client({})
    client.upsert_property_v2("p1", "k", {"v": 1}, dry=False)     # 최초 = POST
    assert len(fake.method_calls("POST")) == 1
    ok, _env, _err = client.upsert_property_v2("p1", "k", {"v": 2}, dry=False)  # 재실행 = PUT
    assert ok is True
    assert len(fake.method_calls("POST")) == 1, "재-upsert 가 POST 중복 생성 — 멱등 위반"
    assert len(fake.method_calls("PUT")) == 1


def test_d6_replay_stale_chunk_purge():
    """§8.5.3 replay ③: 구 chunk_count 3 잔존 → 신 chunk_count 2 저장 전 __chunk_2 선소거 (I-1)."""
    chunk_prefix = f"{PROPERTY_KEY_PREFIX}.__chunk_"
    stale = {f"{chunk_prefix}{i}": [{"id": 100 + i, "key": f"{chunk_prefix}{i}",
                                     "value": {"data": "old"}, "version": {"number": 1}}]
             for i in range(3)}
    client, fake = _harness_client(stale)
    purged = client._purge_stale_chunks("p1", new_chunk_count=2, dry=False)
    assert purged == [f"{chunk_prefix}2"]
    deletes = fake.method_calls("DELETE")
    assert len(deletes) == 1 and deletes[0]["path"].endswith("/properties/102")


# ════════════════════════════════════════════════════════════════════════════
# D-7: golden-파생 dry round-trip (suite-B — 기존 dry 6함수 중 5 재작성분)
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.requires_golden
def test_d7_dry_round_trip_byte_exact(monkeypatch):
    """D-7: golden-파생 mock 경유 store→load byte-exact (mock bare-value 회귀 → RED)."""
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    data = measure.build_w1_fixture()
    cdict = chunk_canonical(data, effective_chunk_budget())
    result = client.store_chunked_property("pageX", cdict, dry_run=True)
    assert result["success"] is True
    assert client.load_chunked_property("pageX", dry_run=True) == data


@pytest.mark.requires_golden
def test_d7_manifest_last_ordering(monkeypatch):
    """D-7: put_order = 전 chunk 뒤 manifest (IO-6 원자성)."""
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    data = measure.build_w1_fixture()
    cdict = chunk_canonical(data, effective_chunk_budget())
    n = cdict[LOCAL_MANIFEST_KEY]["chunk_count"]
    put_order = client.store_chunked_property("pageX", cdict, dry_run=True)["put_order"]
    assert put_order[-1] == MANIFEST_KEY
    assert put_order[:-1] == [CHUNK_KEY_TEMPLATE.format(n=i) for i in range(n)]


@pytest.mark.requires_golden
def test_d7_manifest_absent_fail_closed(monkeypatch):
    """D-7: manifest 미커밋(crash 모사) → load fail-closed (부분 데이터 노출 0)."""
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    data = measure.build_w1_fixture()
    cdict = chunk_canonical(data, effective_chunk_budget())
    n = cdict[LOCAL_MANIFEST_KEY]["chunk_count"]
    for i in range(n):
        env = client._golden_envelope(CHUNK_KEY_TEMPLATE.format(n=i),
                                      {"data": cdict[local_chunk_key(i)]}, 1)
        client._mock_store[CHUNK_KEY_TEMPLATE.format(n=i)] = env
    with pytest.raises(ChunkStoreError, match="manifest"):
        client.load_chunked_property("pageX", dry_run=True)


@pytest.mark.requires_golden
def test_d7_corrupt_chunk_fail_closed(monkeypatch):
    """D-7: 저장 chunk 손상 → sha256 불일치 fail-closed."""
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    data = measure.build_w1_fixture()
    client.store_chunked_property("pageX", chunk_canonical(data, effective_chunk_budget()),
                                  dry_run=True)
    corrupt = client._mock_store[CHUNK_KEY_TEMPLATE.format(n=0)]
    corrupt["value"] = {"data": "dGFtcGVyZWQ="}
    with pytest.raises(ChunkStoreError):
        client.load_chunked_property("pageX", dry_run=True)


@pytest.mark.requires_golden
def test_d7_auto_dry_run_no_session(monkeypatch):
    """D-7 / IO-7: TEST_PAGE_ID 부재 → 자동 dry-run + 실 HTTP session 미생성."""
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    data = measure.build_w1_fixture()
    result = client.store_chunked_property("pageX", chunk_canonical(data, effective_chunk_budget()))
    assert result["dry_run"] is True
    assert client._session is None


def test_d7_manifest_reject_transport_free():
    """suite-A 존치분: manifest 없는 chunk_dict 는 transport 도달 전 거부 (golden 불요)."""
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    with pytest.raises(ChunkStoreError, match="__manifest"):
        client.store_chunked_property("pageX", {"__chunk_0": "abc"}, dry_run=True)


# ════════════════════════════════════════════════════════════════════════════
# D-8: 전역 write cap 경계 19/20/21
# ════════════════════════════════════════════════════════════════════════════

def test_d8_cap_boundary_19_20_ok():
    """D-8: 19·20번째 시도 = 통과 (경계 off-by-one 회귀 방어)."""
    acc = WriteAccounting(cap=20)
    for i in range(20):
        acc.record_write_attempt({"label": f"w{i}"})
    assert acc.write_attempts == 20
    assert acc.snapshot()["remaining"] == 0


def test_d8_cap_boundary_21_hard_stop():
    """D-8: 21번째 시도 → WriteCapExceeded raise (silent False = 함수-로컬 회귀 mutant → RED)."""
    acc = WriteAccounting(cap=20)
    for i in range(20):
        acc.record_write_attempt({"label": f"w{i}"})
    with pytest.raises(WriteCapExceeded):
        acc.record_write_attempt({"label": "w21"})


def test_d8_delete_outside_cap():
    """D-8 보조: DELETE 는 cap 밖 별도 집계 (soft-ceiling — 회수는 계속)."""
    acc = WriteAccounting(cap=1, delete_soft_ceiling=2)
    acc.record_write_attempt({"label": "w0"})
    for i in range(5):
        acc.record_delete_attempt(f"d{i}")           # cap 초과 없이 계속
    assert acc.delete_attempts == 5
    assert acc.write_attempts == 1


# ════════════════════════════════════════════════════════════════════════════
# D-9: run_live try/finally cleanup 결박 (production 경로 실행)
# ════════════════════════════════════════════════════════════════════════════

class _FakeLiveClient:
    """run_live 결박용 fake client — page 신원 GET(200+sentinel)·열거·DELETE 기록."""

    def __init__(self, accounting):
        self.accounting = accounting
        self.header_captures = []
        self.rate_events = []
        self.removed = []
        self.last_list_partial = False

    def _perform_request(self, method, path, *, body_bytes=None, params=None,
                         dry=False, timeout=10):
        return _SyntheticResponse(200, {}, json.dumps(
            {"title": "CFP-2889-THROWAWAY-d9", "results": []}))

    def list_properties_v2(self, page_id, key=None, dry=None):
        return []

    def remove_property_v2(self, page_id, property_id, dry=None):
        self.removed.append(property_id)
        return True, None


def _run_live_with_injected(monkeypatch, tmp_path, exc):
    """scenario_w1 에 예외 주입 → run_live 의 finally cleanup·abort 기록을 관측."""
    monkeypatch.setattr(measure, "scratch_dir", lambda: tmp_path)   # golden 후보 잔재 격리
    ctx = measure.RunContext("d9test", events_path=tmp_path / "events.ndjson")
    client = _FakeLiveClient(ctx.accounting)
    orphan_key = f"{PROPERTY_KEY_PREFIX}.__d9probe"

    def fake_scenario_w1(client_, ctx_, page_id_, dry_):
        ctx_.register_orphan(orphan_key, property_id=101)
        raise exc

    monkeypatch.setattr(measure, "scenario_w1", fake_scenario_w1)
    exit_code, results = measure.run_live(
        client, ctx, "99999999999", {"size_budget": True, "error_codes": False})
    events = [json.loads(line) for line in
              (tmp_path / "events.ndjson").read_text(encoding="utf-8").splitlines()]
    return exit_code, results, events, client


def test_d9_exception_injection_cleanup_still_runs(monkeypatch, tmp_path):
    """D-9: 측정 도중 예외 → finally 가 cleanup_properties 를 실행 (DELETE 미호출 mutant → RED).

    production `run_live` 를 직접 실행한다 — cleanup 이 finally 밖으로 이동하거나
    cleanup_properties 호출이 제거되면 removed==[] · cleanup_intent 부재로 RED.
    """
    exit_code, results, events, client = _run_live_with_injected(
        monkeypatch, tmp_path, ValueError("주입 결함 — D-9"))
    assert exit_code == 1
    assert client.removed == [101], "예외 경로에서 cleanup DELETE 미실행 (P0-c 회귀)"
    types = [e["event"] for e in events]
    assert "cleanup_intent" in types and "cleanup_result" in types
    abort_events = [e for e in events if e["event"] == "abort"]
    assert len(abort_events) == 1
    assert any(o["key"].endswith("__d9probe") for o in abort_events[0]["orphan_registry"]), \
        "abort 이벤트에 orphan registry snapshot 부재 (§3.9 영속화 회귀)"


def test_d9_operational_verdict_aborted(monkeypatch, tmp_path):
    """D-9 보조: abort run 의 운영 verdict = ABORTED (측정 tier 와 2축 분리 — §3.10)."""
    _exit, results, _events, _client = _run_live_with_injected(
        monkeypatch, tmp_path, ValueError("주입"))
    assert results["operational_verdict"] == "ABORTED"
    assert results["measurement_tiers"]["storage_axis"] == "declared"


# ════════════════════════════════════════════════════════════════════════════
# D-10a: emit deny-scan 양방향 + grouped_hex validator
# ════════════════════════════════════════════════════════════════════════════

def test_d10a_emit_abort_on_raw_hex():
    """D-10a: 원문 64-hex 를 record 에 실으면 emit choke-point 가 K-6 abort."""
    with pytest.raises(measure.EmitDenyScanAbort):
        measure.emit_record({"digest": "a" * 64})


def test_d10a_emit_pass_on_grouped_hex():
    """D-10a 양방향: grouped-hex 표기는 non-abort 통과 (정상 golden 산출 경로)."""
    text = measure.emit_record({"digest": grouped_hex("a" * 64)})
    assert grouped_hex("a" * 64) in text
    assert "a" * 64 not in text


def test_d10a_grouped_hex_roundtrip():
    """D-10a: grouped-hex 무손실 결정론 역변환."""
    digest = "0123456789abcdef" * 4
    assert ungroup_hex(grouped_hex(digest)) == digest


def test_d10c_grouped_hex_validator_rejects():
    """D-10c: 비-64-hex 입력 → ValueError (silent pass-through = 세탁 재도입 mutant → RED)."""
    for bad in ("invalid", "A" * 64, "a" * 63, "a" * 65, "z" * 64, ""):
        with pytest.raises(ValueError):
            grouped_hex(bad)


# ════════════════════════════════════════════════════════════════════════════
# D-10b: body 축 — scrub redact + 약화 시 deny-scan drop (흡수 계층 discriminating)
# ════════════════════════════════════════════════════════════════════════════

def test_d10b_body_short_passthrough():
    """D-10b: 무해 짧은 body = 원문 유지·비-drop."""
    body, omitted, length = sanitize_body_field("short body")
    assert body == "short body" and omitted is False and length == len("short body")


def test_d10b_body_20plus_run_never_survives():
    """D-10b 세탁-부재: 20+ b64-유사 run 주입 → 원문이 출력에 잔존하면 RED (scrub redact)."""
    secret_like = "A1b2C3d4E5f6G7h8I9j0K1L2M3"
    body, omitted, length = sanitize_body_field(f"prefix {secret_like} suffix")
    assert secret_like not in (body or "")
    assert length == len(f"prefix {secret_like} suffix".encode("utf-8"))


def test_d10b_body_truncate_200():
    """D-10b: 200B truncate — body_length 는 원문 길이 정직 기록."""
    long_body = "x " * 300                            # 공백 포함 — 20+ run 미형성
    body, omitted, length = sanitize_body_field(long_body)
    assert length == len(long_body.encode("utf-8"))
    assert body is not None and len(body.encode("utf-8")) <= 200


def test_d10b_weakened_scrub_deny_scan_drops(monkeypatch):
    """D-10b 흡수 계층: `_scrub` 이 약화(회귀)돼도 deny-scan 이 필드 drop 으로 차단.

    scrub 휴리스틱은 deny-scan 패턴의 상위집합이라 정상 상태에선 drop 경로가 후순위다 —
    본 테스트는 scrub 을 identity 로 무력화(회귀 모사)했을 때 deny-scan 원경로가
    `body_omitted_by_deny_scan=True` 로 원문 유출을 차단함을 판별한다 (계층 제거 mutant → RED).
    """
    monkeypatch.setattr(rest_module, "_scrub", lambda t: t)
    secret_like = "A1b2C3d4E5f6G7h8I9j0K1L2M3"
    body, omitted, length = sanitize_body_field(f"prefix {secret_like} suffix")
    assert omitted is True and body is None


# ════════════════════════════════════════════════════════════════════════════
# D-10d: safe_path 입력 정의역 validator (grouped-hex 동형 — 세탁 primitive 차단)
# ════════════════════════════════════════════════════════════════════════════

def test_d10d_safe_path_accepts_own_templates():
    """D-10d: 자사 템플릿 경로 2형(v2·v1) = 정상 변환 (무손실 ` / ` 분절)."""
    v2 = safe_path("/wiki/api/v2/pages/12345/properties/678")
    assert v2.replace(" / ", "/") == "/wiki/api/v2/pages/12345/properties/678"
    v1 = safe_path("/wiki/rest/api/content/12345/property/codeforge.sync.canonical.__manifest")
    assert "property" in v1


def test_d10d_safe_path_rejects_non_template():
    """D-10d: 임의 문자열·body 유사·query 포함 경로 → ValueError (silent 변환 = 세탁 mutant → RED)."""
    for bad in ("A1b2C3d4E5f6G7h8I9j0K1L2M3",
                "/wiki/api/v2/pages/1/properties?cursor=abcdefghijklmnopqrstuv",
                "/etc/passwd", "", "not a path at all"):
        with pytest.raises(ValueError):
            safe_path(bad)


def test_d10d_safe_path_or_drop_marker():
    """D-10d: 비-템플릿(서버 유래 등) → (None, True) 필드 drop marker (body 축 동형)."""
    endpoint, omitted = safe_path_or_drop("/server/injected/opaque-next-token-abcdefghij")
    assert endpoint is None and omitted is True
    endpoint2, omitted2 = safe_path_or_drop("/wiki/api/v2/pages/1/properties")
    assert endpoint2 is not None and omitted2 is False


# ════════════════════════════════════════════════════════════════════════════
# D-11: subprocess 단독 실행 스모크 (conftest 우회 불가 오라클 — D6 import 검증)
# ════════════════════════════════════════════════════════════════════════════

def test_d11_subprocess_plan_mode_smoke():
    """D-11: 깨끗한 env 로 measure.py 단독 실행 → exit 0 ∧ plan 회계표 marker 실재."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("ATLASSIAN_", "CFP2829_", "CFP2889_", "CFP1495_"))}
    env["PYTHONIOENCODING"] = "utf-8"
    env["HOME"] = str(Path.home())                    # creds 파일 로드 경로 (값 미검증 — plan 은 HTTP 0)
    result = subprocess.run(
        [sys.executable, "scripts/confluence_backward_measure.py"],
        cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
    )
    assert result.returncode == 0, f"단독 실행 실패 — stderr tail: {result.stderr[-400:]}"
    assert '"run_kind": "plan"' in result.stdout, "plan 회계표 JSON marker 부재"


# ════════════════════════════════════════════════════════════════════════════
# D-12: MOCK_429 → production retry 루프 실행사 (dark-path 활성 계약)
# ════════════════════════════════════════════════════════════════════════════

def test_d12_mock_429_exercises_retry_loop(monkeypatch):
    """D-12: MOCK_429 ON — 429-한정 1회 재시도 (attempts=2) + rate 관측 기록.

    OFF 면 동일 assert 가 실패한다 (attempts=1·rate_events 0) = crucial experiment.
    """
    monkeypatch.setenv("CFP1495_API_MOCK_429", "1")
    acc = WriteAccounting(cap=20)
    client = ConfluencePropertyREST("https://example.atlassian.net", "tok-fake", "e@x.io",
                                    accounting=acc)
    ok, env, err = client.create_property_v2("p1", "k1", {"v": 1}, dry=False)
    assert ok is False
    assert acc.write_attempts == 2, "429-한정 1회 재시도 미실행 (retry 루프 미행사)"
    assert len(client.rate_events) == 2
    assert err is not None and err["origin"] == "server-response"


def test_d12_rate_429_accumulation_aborts(monkeypatch):
    """D-12 / K-4: run 내 429 누적 3 → RateAbortError (의도적 유발 근접 회피)."""
    monkeypatch.setenv("CFP1495_API_MOCK_429", "1")
    client = ConfluencePropertyREST("https://example.atlassian.net", "tok-fake", "e@x.io",
                                    accounting=WriteAccounting(cap=20))
    client.create_property_v2("p1", "k1", {"v": 1}, dry=False)    # 429 관측 2
    with pytest.raises(RateAbortError):
        client.create_property_v2("p1", "k2", {"v": 2}, dry=False)  # 3번째 관측 → abort
    assert RATE_429_ABORT_THRESHOLD == 3


# ════════════════════════════════════════════════════════════════════════════
# D-13: golden-부재 negative-control (skip 금지 — 명시 fail 거동 고정)
# ════════════════════════════════════════════════════════════════════════════

def test_d13_golden_missing_loader_explicit_error(monkeypatch, tmp_path):
    """D-13: golden 부재 → 로더가 GoldenFixtureMissingError (silent 기본값 mutant → RED)."""
    monkeypatch.setenv(GOLDEN_DIR_ENV, str(tmp_path))
    with pytest.raises(GoldenFixtureMissingError):
        rest_module.load_shape_golden()
    with pytest.raises(GoldenFixtureMissingError):
        rest_module.load_list_golden()


def test_d13_golden_missing_dry_roundtrip_fails(monkeypatch, tmp_path):
    """D-13: golden 부재 상태의 dry round-trip = 명시 fail 전파 (suite-B 실행-시-fail 거동)."""
    monkeypatch.setenv(GOLDEN_DIR_ENV, str(tmp_path))
    monkeypatch.delenv(TEST_PAGE_ID_ENV, raising=False)
    client = ConfluencePropertyREST("https://example.atlassian.net", None, None)
    data = measure.build_w1_fixture()
    with pytest.raises(GoldenFixtureMissingError):
        client.store_chunked_property("pageX", chunk_canonical(data, effective_chunk_budget()),
                                      dry_run=True)


def test_d13_no_silent_skip_in_source():
    """D-13: 본 파일·restart 파일 소스에 skip 호출 0 (조용한 GREEN 구조적 부재).

    needle 을 연접으로 구성해 본 검사 자체는 오탐하지 않는다.
    """
    needle = "pytest" + ".skip"
    marker_needle = "skip" + "if"
    # FIX iter1 F-CL-08: marker 계열 skip 데코레이터 회피 봉인 (연접 구성 — 자기 오탐 0).
    mark_needle = "mark" + ".skip"
    for name in ("test_confluence_property_rest.py", "test_cfp2889_restart_recovery.py"):
        src = (Path(__file__).parent / name).read_text(encoding="utf-8")
        assert needle not in src, f"{name}: {needle} 검출 — D-13 위반"
        assert marker_needle not in src, f"{name}: {marker_needle} 검출 — 플랫폼 분기는 명시 분기로"
        assert mark_needle not in src, f"{name}: {mark_needle} 검출 — D-13 위반 (marker skip)"


# ════════════════════════════════════════════════════════════════════════════
# 경계 tier A (Change Plan §8.1-§8.2)
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("target", [32767, 32768, 32769])
def test_boundary_payload_exact_size(target):
    """tier A: build_boundary_payload — JSON-encoded byte 정확 산출 (32768±1 probe 전제)."""
    payload = measure.build_boundary_payload(target)
    assert json_encoded_size(payload) == target


@pytest.mark.parametrize("size,rejected", [(28671, False), (28672, False), (28673, True)])
def test_boundary_budget_reject(size, rejected):
    """tier A: pre-flight budget 경계 28671/28672 통과·28673 reject (local-reject 분류)."""
    client = ConfluencePropertyREST("https://example.atlassian.net", "t", "e")
    value = measure.build_boundary_payload(size)
    result = client._budget_reject(value, enforce_budget=True, ascii_mode=False)
    if rejected:
        assert result is not None and result["origin"] == "local-reject" \
            and result["classified_as"] == "over-limit"
    else:
        assert result is None


@pytest.mark.parametrize("raw,expected_chunks", [(21495, 1), (21496, 2)])
def test_boundary_chunk_transition(raw, expected_chunks):
    """tier A: effective budget(28662) 기준 raw 21495↔21496 chunk 전환 경계."""
    cdict = chunk_canonical(b"a" * raw, effective_chunk_budget())
    assert cdict[LOCAL_MANIFEST_KEY]["chunk_count"] == expected_chunks


# ════════════════════════════════════════════════════════════════════════════
# Decision Table tier B — verdict grid ("local-reject 인데 normative" 셀 부재 exhaustive)
# ════════════════════════════════════════════════════════════════════════════

def test_decision_table_over_limit_exhaustive():
    """tier B: origin × classified × control 전 셀 — normative ⇔ (server ∧ over-limit ∧ control)."""
    for origin in ("local-reject", "server-response", "exception"):
        for classified in ("over-limit", "malformed", None):
            for control in (True, False):
                verdict = measure.verdict_over_limit_axis([{
                    "origin": origin, "http_status": 400,
                    "classified_as": classified, "control_pair_ok": control,
                }])
                expected = "normative" if (origin == "server-response"
                                           and classified == "over-limit"
                                           and control) else "declared"
                assert verdict == expected, f"결함 셀: {origin}/{classified}/{control} → {verdict}"
                assert verdict in TIER_ENUM


def test_decision_table_storage_exhaustive():
    """tier B: write_success × readback 전 셀 — normative ⇔ (True ∧ True)."""
    for ws in (True, False):
        for rb in (True, False):
            verdict = measure.verdict_storage_axis(
                [{"write_success": ws, "readback_byte_exact": rb}])
            assert verdict == ("normative" if (ws and rb) else "declared")


# ════════════════════════════════════════════════════════════════════════════
# K-5: PageIdentityGate (deny-set·sentinel·fail-closed — 건수 박제 금지)
# ════════════════════════════════════════════════════════════════════════════

class _GateClientStub:
    accounting = None

    def __init__(self, response=None, raise_exc=False):
        self._response = response
        self._raise = raise_exc

    def _perform_request(self, method, path, *, body_bytes=None, params=None,
                         dry=False, timeout=10):
        if self._raise:
            raise ConnectionError("gate GET 실패 모사")
        return self._response


def test_k5_deny_set_hit_root_homepage():
    """K-5: ia-tree root_homepage_id(1867943) 는 deny-set 소속 → 즉시 차단 (GET 0회)."""
    gate = measure.PageIdentityGate()
    result = gate.verify("1867943", _GateClientStub(raise_exc=True), dry=True)
    assert result["deny_hit"] is True and result["ok"] is False
    assert result["deny_set_size"] >= 1                # 건수 박제 금지 — 존재만


def test_k5_get_failure_fail_closed():
    """K-5: page GET 실패 = fail-closed ('확인 못 함' ≠ '안전함')."""
    gate = measure.PageIdentityGate()
    result = gate.verify("999999999999", _GateClientStub(raise_exc=True), dry=True)
    assert result["ok"] is False and "GET 실패" in result["reason"]


def test_k5_sentinel_positive_pass():
    """K-5: deny-set 미소속 ∧ 양성 sentinel 제목 → 통과 / sentinel 부재 제목 → 차단."""
    gate = measure.PageIdentityGate()
    ok_resp = _SyntheticResponse(200, {}, json.dumps({"title": "CFP-2889-THROWAWAY-20260806"}))
    result = gate.verify("999999999999", _GateClientStub(response=ok_resp), dry=True)
    assert result["ok"] is True and result["sentinel_ok"] is True

    bad_resp = _SyntheticResponse(200, {}, json.dumps({"title": "운영 mirror page"}))
    result2 = gate.verify("999999999999", _GateClientStub(response=bad_resp), dry=True)
    assert result2["ok"] is False and result2["sentinel_ok"] is False


# ════════════════════════════════════════════════════════════════════════════
# seam default-off: production 경로 미참조 (grep discriminating)
# ════════════════════════════════════════════════════════════════════════════

def test_seam_not_referenced_from_production():
    """seam default-off 실체: measure.py 외 production 코드에 측정 client 참조 0 (§3.7)."""
    needles = ("confluence_measurement_client", "MeasurementRESTClient",
               "write_property_unbudgeted")
    offenders = []
    for py in list((REPO_ROOT / "scripts").glob("*.py")) + \
            list((REPO_ROOT / "scripts" / "lib").glob("*.py")):
        if py.name in ("confluence_backward_measure.py", "confluence_measurement_client.py"):
            continue
        src = py.read_text(encoding="utf-8", errors="replace")
        for needle in needles:
            if needle in src:
                offenders.append(f"{py.name}:{needle}")
    assert offenders == [], f"production 경로에서 seam 참조 검출: {offenders}"


# ════════════════════════════════════════════════════════════════════════════
# §8.8 동적 테스트 로스터 (FIX iter1 F-CR-01 — Change Plan §8.8.1 fuzz / §8.8.2 property)
#   - suite-A 소속 (golden 비의존 — 전 대상 순수함수, live API 0. requests session 미생성).
#   - corpus = tests/fixtures/cfp_2889/fuzz_corpus/ (synthetic seed, not captured —
#     §3.9 captured-golden 규약 비적용. 실 400 body 원문은 §3.9 body drop 정책으로
#     run 산출물에 미보존 → 합성 seed 한정, 정직 이월).
# ════════════════════════════════════════════════════════════════════════════

import random

# FIX iter2 F-CL2-01: 선례 동형 fail-loud 가드 (test_cfp2813_living_arch.py L29-34) —
# 부재 시 원시 traceback 대신 조치 안내 + 결정론 exit 2 (진단층. 부재 근본 처치 =
# requirements.txt `hypothesis` 선언 — 가드는 전멸을 막지 않는다).
try:
    from hypothesis import example, given, settings
    from hypothesis import strategies as st
except ImportError:
    print("[codeforge-error] hypothesis not installed — pip install --user hypothesis",
          file=sys.stderr)
    sys.exit(2)

from lib.confluence_property_chunking import reassemble

FUZZ_CORPUS_DIR = REPO_ROOT / "tests" / "fixtures" / "cfp_2889" / "fuzz_corpus"
# §8.8.1 execution_budget — corpus 결정론 변이 iterations (실측 = Story §8.4 기록).
FUZZ_ITERATIONS = 3000


def _load_fuzz_corpus():
    files = sorted(FUZZ_CORPUS_DIR.glob("seed_*.txt"))
    assert files, (
        f"fuzz corpus 부재: {FUZZ_CORPUS_DIR}/seed_*.txt — §8.8.1 seed_or_corpus 계약 (명시 fail)")
    return [f.read_text(encoding="utf-8", errors="replace") for f in files]


def _mutate(rng: random.Random, s: str) -> str:
    """결정론 변이 6종 — 절단·제어문자·비-UTF8 decode 잡음·중복 팽창·case 반전·역순."""
    if not s:
        s = "x"
    op = rng.randrange(6)
    if op == 0:
        return s[:rng.randrange(len(s) + 1)]
    if op == 1:
        pos = rng.randrange(len(s) + 1)
        return s[:pos] + chr(rng.randrange(0, 32)) + s[pos:]
    if op == 2:
        noise = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 16)))
        return s + noise.decode("latin-1")
    if op == 3:
        return s * rng.randrange(1, 4)
    if op == 4:
        return s.swapcase()
    return s[::-1]


def test_fuzz_is_over_limit_error_corpus_mutation_crash_zero():
    """§8.8.1 fuzz: corpus seed × 결정론 변이 — uncaught 예외 0 ∧ bool 불변 ∧ fail-safe 축 불변식.

    oracle (분류기 재구현 아닌 축 불변식 — tautology 회피):
      - 반환 타입 bool (crash/panic 0)
      - v1: body 무관 `status == 413` 에만 True (body-독립 불변)
      - v2: status != 400 → 무조건 False (fail-safe — over-limit 오인 없음)
      - version ∉ {1, 2} → 무조건 False (fail-safe)
    """
    rng = random.Random(0x2889)
    seeds = _load_fuzz_corpus()
    statuses = (400, 413, 404, 200, 500, 429, 0, -1)
    versions = (1, 2, 0, 3, -1)
    for i in range(FUZZ_ITERATIONS):
        body = _mutate(rng, seeds[i % len(seeds)])
        version = versions[rng.randrange(len(versions))]
        status = statuses[rng.randrange(len(statuses))]
        result = rest_module.is_over_limit_error(version, status, body)
        assert isinstance(result, bool), f"iter {i}: 반환 타입 {type(result)} — bool 불변 위반"
        if version == 1:
            assert result is (status == 413), f"iter {i}: v1 body-독립 불변 위반"
        elif version == 2 and status != 400:
            assert result is False, f"iter {i}: v2 status!=400 fail-safe 위반"
        elif version not in (1, 2):
            assert result is False, f"iter {i}: 미지 version fail-safe 위반"


@settings(max_examples=200, deadline=None)
@given(version=st.integers(min_value=-2, max_value=4),
       status=st.integers(min_value=-1, max_value=600),
       body=st.one_of(st.text(max_size=300),
                      st.binary(max_size=300).map(lambda b: b.decode("latin-1"))))
@example(version=2, status=400, body="")
@example(version=1, status=413, body="\x00")
@example(version=1, status=400, body="value too large")   # v1 완화 mutant 결정론 판별 pin
@example(version=2, status=413, body="too long")          # v2 status!=400 fail-safe 판별 pin
@example(version=3, status=413, body="too long")          # 미지 version fail-safe 판별 pin
def test_fuzz_is_over_limit_error_hypothesis_arbitrary(version, status, body):
    """§8.8.1 fuzz (Hypothesis 축): 임의 (version, status, body) — crash 0 + fail-safe 불변."""
    result = rest_module.is_over_limit_error(version, status, body)
    assert isinstance(result, bool)
    if version not in (1, 2):
        assert result is False
    if version == 2 and status != 400:
        assert result is False
    if version == 1:
        assert result is (status == 413)


# §8.8.2 sample_budget — Hypothesis examples (실측 = Story §8.4 기록).
_PROP_MAX_EXAMPLES = 120


@settings(max_examples=_PROP_MAX_EXAMPLES, deadline=None)
@given(data=st.binary(min_size=0, max_size=2048),
       budget=st.integers(min_value=6, max_value=30000))
@example(data=b"", budget=6)
@example(data=b"\x00", budget=6)
@example(data=("한글 라인 무결성\n" * 200).encode("utf-8"), budget=200)
def test_prop_chunk_reassemble_roundtrip(data, budget):
    """§8.8.2 property ①: reassemble(chunk(b, budget)) == b (∀ bytes b, 유효 budget ≥ 6)."""
    assert reassemble(chunk_canonical(data, budget)) == data


@settings(max_examples=_PROP_MAX_EXAMPLES, deadline=None)
@given(data=st.binary(min_size=0, max_size=2048),
       budget=st.integers(min_value=6, max_value=28662))
@example(data=b"\xff" * 2048, budget=6)
def test_prop_wrap_budget_invariant(data, budget):
    """§8.8.2 property ②: json_encoded_size(wrap(chunk_i)) ≤ budget + WRAP_OVERHEAD ≤ BUDGET_BYTES."""
    props = chunk_canonical(data, budget)
    for key, val in props.items():
        if key == LOCAL_MANIFEST_KEY:
            continue
        wrapped = json_encoded_size({"data": val})
        assert wrapped <= budget + WRAP_OVERHEAD_BYTES
        assert wrapped <= BUDGET_BYTES


def test_prop_wrap_budget_strategy_bound_is_effective_budget():
    """§8.8.2 전략 상한 28662 = effective_chunk_budget() 결박 (상수 드리프트 시 본 테스트 RED)."""
    assert effective_chunk_budget() == 28662 == BUDGET_BYTES - WRAP_OVERHEAD_BYTES


def test_prop_wrap_budget_invariant_at_effective_budget_full_chunk():
    """§8.8.2 경계 pin: effective budget 가득 찬 chunk 도 wrap 후 BUDGET_BYTES 이하 (D-5 ∀-형)."""
    budget = effective_chunk_budget()
    props = chunk_canonical(b"\xa5" * 43000, budget)   # raw_budget=21495 → chunk 3개 (첫 2개 가득)
    payload_keys = [k for k in props if k != LOCAL_MANIFEST_KEY]
    assert len(payload_keys) >= 2
    for k in payload_keys:
        assert json_encoded_size({"data": props[k]}) <= BUDGET_BYTES


# ════════════════════════════════════════════════════════════════════════════
# basis golden 결박 suite (FIX iter1 F-CL-06/07 — Change Plan §8.1–§8.2 basis 결선 이행)
#   read-only: golden·NDJSON 은 읽기만 한다 (§3.9 — 갱신은 실 재측정 시에만).
#   결박 상대 = scripts/ production 상수·verdict 함수 (golden 을 읽지 않는 함수 — tautology 차단).
# ════════════════════════════════════════════════════════════════════════════

FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "cfp_2889"
BASIS_GOLDEN_PATH = FIXTURES_DIR / "measurement_basis_golden.json"
RUN_NDJSON_PATH = FIXTURES_DIR / "run-20260806T060155.ndjson"


def _load_basis():
    if not BASIS_GOLDEN_PATH.exists():
        pytest.fail(f"basis golden 부재: {BASIS_GOLDEN_PATH} (D-13 — skip 금지, 명시 fail)")
    return json.loads(BASIS_GOLDEN_PATH.read_text(encoding="utf-8"))


@pytest.mark.requires_golden
def test_ac11_replay_basis_boundary_32768():
    """AC-11 replay: 경계 관측 32767 성공 / 32769 → 400 + discriminating 결박 (Change Plan §8.1–§8.2)."""
    basis = _load_basis()
    points = {p["json_encoded_bytes"]: p for p in basis["boundary_basis"]["points"]}
    assert points[32767]["write_success"] is True
    assert points[32769]["write_success"] is False
    assert points[32769]["http_status"] == 400
    assert basis["boundary_basis"]["discriminating"] is True


@pytest.mark.requires_golden
def test_ac11_replay_basis_budget_constants_binding():
    """AC-4/AC-11: basis golden budget_basis ↔ 코드 상수 SSOT 결박 (드리프트 = RED)."""
    bb = _load_basis()["budget_basis"]
    assert bb["budget_bytes"] == BUDGET_BYTES
    assert bb["wrap_overhead_bytes_declared"] == WRAP_OVERHEAD_BYTES
    assert bb["wrap_overhead_bytes_local_measured"] == WRAP_OVERHEAD_BYTES
    assert bb["effective_chunk_budget"] == effective_chunk_budget()


@pytest.mark.requires_golden
def test_ac12_replay_basis_over_limit_tier_binding():
    """AC-12 replay: 관측(v2 400 malformed 미분별·v1 404) → production verdict 함수 = declared 결박."""
    basis = _load_basis()
    olb = basis["over_limit_basis"]
    assert olb["v2_probe_status"] == 400
    assert olb["v2_probe_classified_as"] == "malformed"
    assert olb["v1_probe_status"] == 404
    observation = {"origin": "server-response",
                   "http_status": olb["v2_probe_status"],
                   "classified_as": olb["v2_probe_classified_as"],
                   "control_pair_ok": True}
    tier = measure.verdict_over_limit_axis([observation])
    assert tier == basis["measurement_tiers"]["over_limit_axis"] == "declared"


@pytest.mark.requires_golden
def test_ac13_replay_captured_headers_verdict():
    """AC-13a replay: rate 계열 헤더 전 부재(유효 negative) + 42건 캡처 → production verdict = advisory."""
    basis = _load_basis()
    lowered = {n.lower() for n in basis["header_name_set"]}
    assert "retry-after" not in lowered
    assert not any(n.startswith(("x-ratelimit-", "ratelimit-", "beta-", "x-beta-"))
                   for n in lowered)
    count = basis["header_capture_count"]
    assert count == 42 and count >= 1
    tier = measure.verdict_rate_axis([{"idx": i} for i in range(count)])
    assert tier == basis["measurement_tiers"]["rate_axis"] == "advisory"


@pytest.mark.requires_golden
def test_basis_measurement_tiers_enum_membership():
    """basis golden 3축 tier 전건 TIER_ENUM 소속 + storage 축 normative (D-3 확장 결박)."""
    tiers = _load_basis()["measurement_tiers"]
    assert set(tiers.keys()) == {"storage_axis", "over_limit_axis", "rate_axis"}
    for value in tiers.values():
        assert value in TIER_ENUM
    assert tiers["storage_axis"] == "normative"


@pytest.mark.requires_golden
def test_basis_control_status_null_disambiguated_by_ndjson():
    """F-CL-07: `v2_control_status: null` = control write 성공 경로 status 미기록 — NDJSON 교차 결박.

    committed run NDJSON 의 overlimit-control cleanup_result(ok ∧ property_id 실재)가 control
    write 실행+성공을 증거한다 (null ≠ 미실행). future-run 은 emit 이 `v2_control_write_success`
    필드를 동반 기록한다 (기captured golden·NDJSON 무편집 — §3.9).
    """
    if not RUN_NDJSON_PATH.exists():
        pytest.fail(f"run NDJSON 부재: {RUN_NDJSON_PATH} (D-13 — skip 금지, 명시 fail)")
    assert _load_basis()["over_limit_basis"]["v2_control_status"] is None
    control_cleanup = None
    for line in RUN_NDJSON_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if (rec.get("event") == "cleanup_result"
                and str(rec.get("key", "")).endswith("overlimit-control")):
            control_cleanup = rec
    assert control_cleanup is not None, "overlimit-control cleanup_result 미발견"
    assert control_cleanup.get("ok") is True
    assert control_cleanup.get("property_id"), "property_id 부재 — control write 성공 증거 불성립"


# ════════════════════════════════════════════════════════════════════════════
# golden builder pin (FIX iter2 F-CL2-02 — FIX iter1 emit 수정 경로 회귀 net)
#   suite-A 소속: builder = dict 입력 순수함수 (기golden 무편집·live 0 — future-run emit 계약 고정).
# ════════════════════════════════════════════════════════════════════════════

import types


def test_build_shape_golden_provenance_put_prefix():
    """F-CR-03 회귀 net: shape golden empirical_source = `PUT <endpoint>` (list golden GET 대칭)."""
    envelope = {"id": "999001", "key": "cfp2889.pin", "value": "pin-payload",
                "version": {"number": 3}}
    golden = measure.build_shape_golden(envelope, run_id="pin-run", page_id="21430273",
                                        status=200)
    src = golden["empirical_source"]
    # safe_path 실 계약 = 공백-분리 세그먼트 표기 (deny-scan 20+run 회피 무관 결정론 변환).
    assert ", PUT " in src, src   # method 프리픽스 실재 (F-CR-03 — list golden GET 대칭)
    assert "/ wiki / api / v2 / pages / 21430273 / properties / 999001" in src, src
    assert golden["endpoint_omitted_by_validator"] is False
    assert golden["value"].startswith("<b64:len=")   # payload 원문 미수록 (§3.9 치환 유지)


def test_build_basis_golden_control_write_success_field():
    """F-CL-07 회귀 net: basis golden 이 `v2_control_write_success` 를 W4 control 에서 전달."""
    results = {
        "scenarios": {
            "W2": {"points": [], "boundary_discriminating": True},
            "W3": {"utf8_bytes": 1, "ascii_bytes": 2, "delta_bytes": 1},
            "W4": {"control": {"write_success": True, "http_status": None},
                   "probe": {"http_status": 400, "classified_as": "malformed"}},
            "W5": {"probe": {"http_status": 404, "classification": "other"}},
        },
        "operational_verdict": "RECONCILED",
        "measurement_tiers": {"storage_axis": "normative",
                              "over_limit_axis": "declared", "rate_axis": "advisory"},
    }
    stub_client = types.SimpleNamespace(header_captures=[])
    basis = measure.build_basis_golden(results, stub_client, run_id="pin-run")
    olb = basis["over_limit_basis"]
    assert olb["v2_control_write_success"] is True
    assert olb["v2_control_status"] is None   # null = 성공 경로 status 미기록 (F-CL-07 의미 고정)
    assert olb["v2_probe_classified_as"] == "malformed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
