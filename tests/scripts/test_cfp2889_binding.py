#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_cfp2889_binding.py — CFP-2889 D-14 결박(binding) 계열 (Change Plan §8.1.D-14).

**계열 신설 사유**: 기존 D-1~D-13 은 전부 negative 계열(가드가 *틀린 값*을 잡는가 / mutant 가
RED 인가)이고 **positive 결박 계열이 0** 이었다. 그 결과 "가드 함수를 만들면 계약 이행" 이
성립했고, 동일 형상(`declared-not-bound` — 선언은 있으나 실 경로 결박이 없음)이 구현리뷰 iter1
→ iter2 → 보안 iter1 로 **3연속 재발**(인스턴스 1 → 1 → 5)했다. D-14 는 "가드가 **실 경로에
붙어 있는가**" 만을 묻는다.

**계열 공통 규율 4항**:
  ① 오라클 = **side-effect 의 발생/부재** (전송이 일어났는가 · 원장 행이 남았는가 · exit code).
     예외 타입·에러 문자열 존재 assert 금지 — 그건 "가드가 호출됐다"가 아니라 "존재한다"의
     재확인이고, 보안 findings 6건이 정확히 그 사각에서 났다.
  ② crucial experiment 짝 의무 — 가드 neuter 시 RED / 원복 시 GREEN (기록 = Story §8.4.D-14).
  ③ 호출 시작점 = **실 진입점** (`main` / `run_live` / `run_plan` / 공개 메서드).
     **가드 함수(validator·pin·`reconcile` 등) 직접 호출 테스트는 D-14 미계상** — 직접 호출은
     "함수가 동작한다"를 보일 뿐 "경로가 그 함수를 지난다"를 못 보인다 = 결박의 반대.
  ④ 공통 fixture = transport spy — **`PreparedRequest` 가 실재하는 계층에서 가로채** 기록하고
     **prepared URL 로 assert**(f-string 결과 금지). 정규화는 `requests`/`urllib3` 에서
     일어나므로 소스 문자열 대조는 이번 결함(`X?y=` 가 서버에 다른 경로로 도달)을 그대로
     재통과시킨다.

**실행 transport**: 실 `requests.Session` + fake `HTTPAdapter` mount — 네트워크 0 · write 0 ·
golden 미접촉. dry/mock transport 사용 금지 (`_perform_request` 가 mock401/mock429/dry 를
`_ensure_session()` *이전* short-circuit 하고 `_SyntheticResponse` 에 `.request` 가 없어 규율 ④
이행 불가 / dry 는 golden 강제 로드라 suite-A 와 충돌 / dry list 는 `_links.next` 를 pop 해
D-14c 21페이지 체인 구성 불가).

**mount prefix = `http://` ∧ `https://` 루트 전부** (재량 아님 — "네트워크 0"의 성립 조건):
pin 대상 host 에만 mount 하면 D-14a mutant arm 의 `http://`·타 host 요청이 미mount 라 실
네트워크로 나가고 spy 는 0건이 되어 **mutant 가 생존(GREEN 오판)** 한다.

**suite 귀속 = 전건 suite-A** (`requires_golden` 마커 부착 금지 — 붙이면 bootstrap 순환이
재생기고 "실측 전 결박 확인" 이라는 본 계열의 목적이 무너진다).

**계상 규율(over-claim 금지)**: 본 4 sub 는 자기가 커버하는 축(host pin · resource-id ·
partial · kill-switch 전파)에 한해 유효하다. 그 밖의 게이트(page 신원 deny-set · emit
choke-point 등)의 결박은 여전히 구현 이행 전제이며 "결박 계열로 완전 봉인" 은 주장하지 않는다.

저작: DeveloperPLAgent (보안테스트 FIX iter1)
"""

import json
import pathlib
import re
import sys
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlsplit

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
import requests
from requests.adapters import HTTPAdapter
from requests.models import PreparedRequest, Response

# conftest 가 scripts/ + scripts/lib/ 를 sys.path 주입
import confluence_backward_measure as measure
from lib.confluence_measurement_client import MeasurementRESTClient
# 신원 패턴 SSOT — production 상수를 직접 참조한다 (3자 단일 출처: body 마스킹 ·
# 커밋 golden 스캔 · 본 emit 채널 결박). 로컬 리터럴 복제는 한쪽 약화를 은폐한다 (iter2 N7).
from lib.confluence_property_rest import (
    F3_PII_PATTERNS,
    WriteAccounting,
    _deny_scan_for_secrets,
    mask_identity_tokens,
    sanitize_body_field,
)

TEST_PAGE = "21430273"
SENTINEL_TITLE = "CFP-2889-THROWAWAY-binding-suite"


# ════════════════════════════════════════════════════════════════════════════
# 공통 fixture — transport spy (규율 ④)
# ════════════════════════════════════════════════════════════════════════════

def _json_response(request: PreparedRequest, status: int, payload: Any) -> Response:
    """fake adapter 합성 응답 — `.request` 를 실재시켜 규율 ④(prepared URL assert)를 성립시킨다."""
    resp = Response()
    resp.status_code = status
    resp.url = request.url
    resp.request = request
    resp.encoding = "utf-8"
    resp.headers["Content-Type"] = "application/json"
    resp._content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return resp


class _Capture:
    """수신 1건 — prepared URL 에서 **정규화가 이미 끝난** path/query 를 보관."""

    __slots__ = ("method", "path", "query", "url")

    def __init__(self, request: PreparedRequest):
        parts = urlsplit(request.url)
        self.method = request.method
        self.path = parts.path
        self.query = parts.query
        self.url = request.url

    def __repr__(self) -> str:                       # pragma: no cover - 진단 표기용
        return f"{self.method} {self.path}" + (f"?{self.query}" if self.query else "")


class BindingSpy:
    """4 sub 공용 spy — 어댑터 클래스를 sub 마다 복붙하지 않고 `responder` 만 갈아끼운다."""

    def __init__(self) -> None:
        self.captures: List[_Capture] = []
        self.responder: Callable[[PreparedRequest], Response] = self._default_responder

    @staticmethod
    def _default_responder(request: PreparedRequest) -> Response:
        return _json_response(request, 200, {"results": [], "_links": {}})

    def mount_on(self, session: Optional[requests.Session]) -> None:
        """`http://` ∧ `https://` **루트 전부** mount — 미mount 요청이 존재하지 않게 한다."""
        assert session is not None, "세션 미성립 — stub creds 로 세션을 먼저 성립시켜야 한다"
        adapter = _SpyAdapter(self)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    # 편의 조회 (오라클 표현용)
    def writes(self) -> List[_Capture]:
        return [c for c in self.captures if c.method in ("POST", "PUT")]

    def paths_outside(self, page_id: str) -> List[_Capture]:
        """**일반형 술어**: prepared path 가 *투입한 id 와 다른 자원을 지목*하는 요청.

        `/properties` 세그먼트 유무로 판정하지 않는다 — 실측상 `page_id=<id>/../x` 는
        `/properties` 를 유지한 채 page 만 바뀌므로 그 술어는 3 arm 중 1개를 못 덮는다.
        """
        prefix = f"/wiki/api/v2/pages/{page_id}"
        return [c for c in self.captures if not c.path.startswith(prefix)]


class _SpyAdapter(HTTPAdapter):
    def __init__(self, spy: BindingSpy):
        super().__init__()
        self._spy = spy

    def send(self, request: PreparedRequest, **kwargs) -> Response:   # noqa: D102
        self._spy.captures.append(_Capture(request))
        return self._spy.responder(request)


@pytest.fixture
def binding_spy() -> BindingSpy:
    return BindingSpy()


# ── 진입점 도달 보조 (신규 seam 0 — 기존 모듈-레벨 팩토리를 감싼다) ──

def _mounting_factory(spy: BindingSpy):
    """`create_measurement_client` 대체 wrapper — 실 팩토리로 client 생성 후 그 세션에 mount.

    **patch 대상 네임스페이스 = `confluence_backward_measure.create_measurement_client`** —
    measure.py 가 from-import 로 심볼을 자기 네임스페이스에 바인딩하므로 정의 모듈
    (`lib.confluence_measurement_client`) 쪽을 패치하면 **no-op** 이다.

    생성자에서 abort 하는 경우(D-14a)에는 client 자체가 만들어지지 않아 mount 도 일어나지
    않고 spy 수신 0건이 성립한다 — mutant(pin 제거)에서는 client 가 생성돼 요청이 잡힌다.
    """
    real = measure.create_measurement_client

    def _factory(base_url, token, email, accounting=None):
        client = real(base_url, token, email, accounting=accounting)
        spy.mount_on(client._ensure_session())
        return client

    return _factory


def _abort_rows(events_path) -> List[Dict[str, Any]]:
    """원장 NDJSON 에서 `abort` 이벤트 행만 — 오라클 ⓑ 의 관측면."""
    if not events_path.exists():
        return []
    rows = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("event") == "abort":
            rows.append(rec)
    return rows


def _stub_env(monkeypatch, tmp_path, spy: BindingSpy, *, base_url: str, page_id: str) -> None:
    """실 진입점(`main`) 실행 전제 — stub creds · scratch 격리 · 팩토리 wrapper.

    stub creds 는 세션 *성립 조건*(`HAS_REQUESTS ∧ token ∧ email`)을 만족시키기 위한 것이고
    네트워크는 adapter 가 가로채므로 실 자격증명 불요·실 송신 0 이다.
    """
    monkeypatch.setattr(measure, "scratch_dir", lambda: tmp_path)
    monkeypatch.setattr(measure, "create_measurement_client", _mounting_factory(spy))
    monkeypatch.setenv("ATLASSIAN_API_TOKEN", "stub-token-not-real")
    monkeypatch.setenv("ATLASSIAN_USER_EMAIL", "stub@example.invalid")
    monkeypatch.setenv("CONFLUENCE_BASE_URL", base_url)
    monkeypatch.setenv(measure.TEST_PAGE_ID_ENV, page_id)
    monkeypatch.delenv(measure.SKIP_WRITE_ENV, raising=False)


def _main_no_live(tmp_path, run_id: str) -> int:
    """`main` 호출 — **`--confirm-live-write` 를 절대 넘기지 않는다**(4-AND 게이트 미개방)."""
    return measure.main(["--run-id", run_id, "--load-creds", str(tmp_path / "absent-creds.env")])


def _ledger_path(tmp_path, run_id: str):
    """원장 파일 경로 — run_id 는 `normalize_run_id`(비허용 문자 치환 + **16자 상한**)를 거친다.

    테스트가 파일명을 직접 조립하면 그 상한을 놓쳐 "행 0" 을 결함으로 오판한다 (실측 확인:
    `d14a-plaintext-http` → `d14a-plaintext-h`). production 함수를 그대로 태워 조립한다.
    """
    return tmp_path / f"cfp2889-run-{measure.normalize_run_id(run_id)}.ndjson"


# ════════════════════════════════════════════════════════════════════════════
# D-14a — host pin ↔ 생성자 결박 (진입점 = main)
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("bad_base,arm", [
    ("http://mclayer.atlassian.net", "plaintext-http"),
    ("https://other.atlassian.net", "other-host"),
])
def test_d14a_host_pin_blocks_before_transport(binding_spy, monkeypatch, tmp_path,
                                               bad_base, arm):
    """D-14a: 비-pin base_url 로 **실 진입점** 실행 → 자격증명이 단 1회도 송신되지 않는다.

    오라클 ⓐ spy 수신 0건 / ⓑ `abort` 원장 1행(K-7 · `endpoint-preflight`) / ⓒ exit≠0.
    mutant: 생성자 pin 배선 제거 → 타 host 요청이 spy 에 수신(RED).
    """
    _stub_env(monkeypatch, tmp_path, binding_spy, base_url=bad_base, page_id=TEST_PAGE)

    exit_code = _main_no_live(tmp_path, f"d14a-{arm}")

    assert exit_code != 0, f"[{arm}] endpoint-preflight 실패가 exit≠0 로 귀결하지 않음"
    assert binding_spy.captures == [], (
        f"[{arm}] 비-pin host 로 요청이 나감 — 생성자 pin 미결박 (자격증명 오도착)")
    aborts = _abort_rows(_ledger_path(tmp_path, f"d14a-{arm}"))
    assert len(aborts) == 1, f"[{arm}] abort 원장 행 수 = {len(aborts)} (기대 1 — 원장 없는 종료 금지)"
    assert aborts[0].get("kill_switch") == "K-7"
    assert "endpoint-preflight" in aborts[0].get("reason", "")


# ════════════════════════════════════════════════════════════════════════════
# D-14b — resource-id 검증 ↔ CRUD 전 경로 결박 (층 판별 2 arm)
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("bad_page_id,arm", [
    ("1867943/../x", "dot-segment"),
    ("1867943?y=", "query-inject"),
    ("1 2", "whitespace"),
    ("9" * 33, "over-length"),
])
def test_d14b_page_id_l1_env_abort(binding_spy, monkeypatch, tmp_path, bad_page_id, arm):
    """D-14b **b-L1**: 위반 `page_id` 를 **env 경유** 투입 → run 미개시 (write 0회).

    오라클 ⓐ spy 수신 0건 / ⓑ `abort` 1행 / ⓒ exit≠0.
    L1 미구현 시 run 이 계속돼 **local-reject 로만 끝난다**(abort 0행·exit 0) = RED —
    즉 본 arm 이 L1 과 L2 를 오라클로 구별한다.
    """
    _stub_env(monkeypatch, tmp_path, binding_spy,
              base_url=f"https://{measure.EXPECTED_HOST}", page_id=bad_page_id)

    exit_code = _main_no_live(tmp_path, f"d14b-{arm}")

    assert exit_code != 0, f"[{arm}] 문법 위반 page_id 로 run 이 정상 종료됨 (L1 미결박)"
    assert binding_spy.captures == [], f"[{arm}] 위반 page_id 상태로 요청이 나감: {binding_spy.captures}"
    aborts = _abort_rows(_ledger_path(tmp_path, f"d14b-{arm}"))
    assert len(aborts) == 1, f"[{arm}] abort 원장 행 수 = {len(aborts)} (기대 1)"
    assert aborts[0].get("kill_switch") == "K-7"


def test_d14b_property_id_l2_tainted_never_reaches_wire(binding_spy):
    """D-14b **b-L2**: 오염 `property_id` 를 **서버 응답 유래**로 투입 → 재삽입 차단.

    오라클 = **오염 값이 prepared path 에 포함된 요청 0건** ∧ abort 없음 ∧ run 계속.
    ★"총 수신 0건" 은 구성상 자기모순이다 — 오염 응답을 받으려면 그 응답을 반환한 GET
    resolve 가 **이미 spy 에 수신돼 있어야** 하므로 총 0건은 정의상 성립 불가.

    mutant: `update_property_v2` 의 `property_id` 검증 제거 → 오염 id 가 wire path 에 등장(RED).
    """
    tainted_id = "../../../pages/1867943"

    def responder(request: PreparedRequest) -> Response:
        # GET resolve 응답의 `results[0].id` 를 오염값으로 반환 (I-4 비신뢰 진입점 모사)
        if request.method == "GET":
            return _json_response(request, 200, {
                "results": [{"id": tainted_id, "key": "cfp2889.bind",
                             "value": {"v": 0}, "version": {"number": 7}}],
                "_links": {},
            })
        return _json_response(request, 200, {"id": tainted_id, "key": "cfp2889.bind",
                                             "value": {"v": 1}, "version": {"number": 8}})

    binding_spy.responder = responder
    client = MeasurementRESTClient(f"https://{measure.EXPECTED_HOST}", "stub-token", "s@x.invalid",
                                   accounting=WriteAccounting(cap=20))
    binding_spy.mount_on(client._ensure_session())

    ok, env, err = client.upsert_property_v2(TEST_PAGE, "cfp2889.bind", {"v": 1}, dry=False)

    # run 계속 — 시나리오 실패로 기록되되 abort 아님
    assert ok is False
    assert err is not None and err.get("origin") == "local-reject"
    # 구성 전제: GET resolve 는 실제로 수신됐다 (총 0건 술어가 성립 불가함의 실측 근거)
    assert len(binding_spy.captures) >= 1
    # 본 sub 의 판정 오라클 — 오염 값이 지목하는 자원으로 나간 요청이 0건
    assert binding_spy.paths_outside(TEST_PAGE) == [], (
        f"오염 property_id 가 wire 에 재삽입됨: {binding_spy.paths_outside(TEST_PAGE)}")


# ════════════════════════════════════════════════════════════════════════════
# D-14c — partial 신호 ↔ verdict 결박 (진입점 = run_live)
# ════════════════════════════════════════════════════════════════════════════

def _paginated_responder(total_pages: int):
    """`_links.next` 체인 응답기 — 현행 추종 상한(`pages_followed < 20`) 초과 구성.

    **cursor 결정론**: 페이지 번호를 요청 query 의 `cursor` 에서 **유도**한다(호출 카운터 금지).
    카운터를 쓰면 baseline 열거와 actual 열거가 서로 다른 key 집합을 받아 `residual ≠ ∅` 이 되고
    **`DRIFT` 가 우선 적용**돼(설계 §3.10 註 ② — 이미 관측된 잔여는 부분성이 약화하지 않는다)
    본 sub 가 겨냥한 `reconcile_partial` 축이 가려진다. 즉 이 결정론은 오라클의 성립 조건이다.
    """

    def responder(request: PreparedRequest) -> Response:
        parts = urlsplit(request.url)
        # K-5 page 신원 GET (properties 하위가 아닌 page 자원)
        if parts.path.endswith(f"/pages/{TEST_PAGE}"):
            return _json_response(request, 200, {"id": TEST_PAGE, "title": SENTINEL_TITLE})
        cursor = ""
        for pair in parts.query.split("&"):
            if pair.startswith("cursor="):
                cursor = pair[len("cursor="):]
        idx = int(cursor[1:]) if cursor.startswith("p") and cursor[1:].isdigit() else 0
        body: Dict[str, Any] = {
            "results": [{"id": str(900000 + idx), "key": f"cfp2889.p{idx}",
                         "value": {}, "version": {"number": 1}}],
            "_links": {},
        }
        if idx + 1 < total_pages:
            body["_links"]["next"] = f"/wiki/api/v2/pages/{TEST_PAGE}/properties?cursor=p{idx + 1}"
        return _json_response(request, 200, body)

    return responder


def test_d14c_pagination_cap_binds_partial_to_verdict(binding_spy, tmp_path):
    """D-14c: 추종 상한 초과(21페이지 체인) → 부분 열거가 **verdict 까지** 전달된다.

    판정 오라클 = ⓑ `reconcile.status == "reconcile_partial"` ∧ ⓒ 운영 verdict `PARTIAL`
    (≠`RECONCILED`) — 산출물에 남는 관측 결과.
    ⓐ `last_list_partial` 은 **보조 신호**로만 표기한다 (내부 상태 assert 라 규율 ① 정의역 밖 —
    ⓐ 단독 GREEN 을 계약 이행으로 계상하지 않는다).

    mutant: cap 소진 arm 의 `last_list_partial = True` 제거 → `RECONCILED` 오판(RED).
    """
    # 체인 길이 註 (off-by-one 실측 정정): cap arm 은 `next 존재 ∧ pages_followed >= 20` 동시
    # 충족에서만 발화한다. 총 21페이지면 추종 20회 뒤 21번째 응답에 `next` 가 없어 **정상 종료
    # arm**(전량 열거·partial 미설정)으로 빠져 cap arm 을 밟지 못한다 — 설계 문언의 "21페이지"
    # 는 상한 초과 *의도*의 표기이며, 그 의도를 실제로 발화시키는 최소 구성은 22페이지 이상이다.
    # 여유를 둬 25로 잡는다 (mutant 판별력은 cap arm 발화 여부에 걸려 있다).
    binding_spy.responder = _paginated_responder(total_pages=25)
    ctx = measure.RunContext(run_id="d14c", cap=20, events_path=tmp_path / "d14c.ndjson")
    client = MeasurementRESTClient(f"https://{measure.EXPECTED_HOST}", "stub-token", "s@x.invalid",
                                   accounting=ctx.accounting)
    binding_spy.mount_on(client._ensure_session())

    exit_code, results = measure.run_live(
        client, ctx, TEST_PAGE, {"size_budget": False, "error_codes": False})

    assert results["reconcile"]["status"] == "reconcile_partial", (
        f'부분 열거가 reconcile 에 미결박 — status={results["reconcile"]["status"]}')
    assert results["operational_verdict"] == "PARTIAL", (
        f'부분 열거가 운영 verdict 에 미결박 — verdict={results["operational_verdict"]}')
    # 보조 신호 (계약 이행 계상 대상 아님)
    assert client.last_list_partial is True


# ════════════════════════════════════════════════════════════════════════════
# D-14d — kill-switch ↔ 전파 결박 (진입점 = run_live)
# ════════════════════════════════════════════════════════════════════════════

def _k1_responder(binding_spy: BindingSpy, *, unauthorized_list_calls: int):
    """properties list GET 중 **앞의 N회만** 401 — 그 뒤는 정상 200.

    ★**자극의 1회성이 D-14d 판별력의 성립 조건이다** (M-D14d 생존 실측, 08/07):
    401 을 *상시* 반환하면 mutant(삼킴) arm 에서도 **바로 다음 GET**
    (`capture_list_golden` → `_perform_request`, `confluence_backward_measure.py:1412`)이
    401 을 재발화하고 그 지점의 `except KillSwitchAbort: raise`(L1416)가 다시 전파시킨다
    → 두 arm 의 관측면(exit≠0 · abort 행 · write 0)이 **동일**해져 mutant 가 생존한다.
    401 을 1회로 한정해야 "삼킴 → run 계속 → 후속 write" 경로가 mutant arm 에서 실제로 열린다.

    `unauthorized_list_calls=0` = 자극 없음 = **계측기 유효성 대조 arm**(write 가 실제로 관측
    가능함을 같은 구성에서 증명 — writes()==[] 가 spy 무능의 산물이 아님을 보증).
    """
    state = {"list_calls": 0}

    def responder(request: PreparedRequest) -> Response:
        parts = urlsplit(request.url)
        if parts.path.endswith(f"/pages/{TEST_PAGE}"):
            return _json_response(request, 200, {"id": TEST_PAGE, "title": SENTINEL_TITLE})
        if request.method == "GET" and parts.path.endswith("/properties"):
            state["list_calls"] += 1
            if state["list_calls"] <= unauthorized_list_calls:
                return _json_response(request, 401, {"message": "Unauthorized"})
            return _json_response(request, 200, {"results": [], "_links": {}})
        if request.method in ("POST", "PUT"):
            return _json_response(request, 200, {
                "id": "900001", "key": "cfp2889.bind", "value": {},
                "version": {"number": 1}})
        return _json_response(request, 200, {"results": [], "_links": {}})

    binding_spy.responder = responder
    return state


def _run_live_with(binding_spy: BindingSpy, tmp_path, run_id: str):
    ctx = measure.RunContext(run_id=run_id, cap=20, events_path=tmp_path / f"{run_id}.ndjson")
    client = MeasurementRESTClient(f"https://{measure.EXPECTED_HOST}", "stub-token", "s@x.invalid",
                                   accounting=ctx.accounting)
    binding_spy.mount_on(client._ensure_session())
    exit_code, results = measure.run_live(
        client, ctx, TEST_PAGE, {"size_budget": True, "error_codes": True})
    return ctx, exit_code, results


def test_d14d_instrument_control_write_is_observable(binding_spy, tmp_path):
    """D-14d **계측기 유효성 대조** — 자극(401) 없이 같은 구성으로 돌리면 write 가 실제로 잡힌다.

    본 대조가 없으면 D-14d 의 `writes() == []` 는 "전파가 멈췄다" 가 아니라 "spy 가 애초에
    write 를 못 본다" 로도 성립한다(hollow). 자극 arm 과 **동일한 responder·동일한 mount·동일한
    진입점**에서 write 가 관측됨을 먼저 보인 뒤에만 부재를 근거로 쓴다.
    """
    _k1_responder(binding_spy, unauthorized_list_calls=0)

    _ctx, _exit_code, _results = _run_live_with(binding_spy, tmp_path, "d14d-control")

    assert len(binding_spy.writes()) >= 1, (
        "자극 없는 arm 에서도 write 가 0건 — spy 가 write 를 관측하지 못함 "
        "(이 상태에서는 D-14d 의 '후속 write 0건' 오라클이 무의미하다)")


def test_d14d_kill_switch_k1_halts_and_leaves_ledger(binding_spy, tmp_path):
    """D-14d: 실 경로 중간에서 K-1(401) 발생 → run 중단 · 원장 1행 · 후속 write 0건.

    자극 = baseline 열거(`enumerate_property_keys`) 의 list GET **1회만** 401.
    mutant: `enumerate_property_keys` 의 `except KillSwitchAbort: raise` 선행절 제거
    (= 광역 `except Exception` 만 남김) → 401 이 삼켜져 run 이 계속되고 후속 write 발생(RED).
    """
    _k1_responder(binding_spy, unauthorized_list_calls=1)

    ctx, exit_code, _results = _run_live_with(binding_spy, tmp_path, "d14d")

    assert exit_code != 0, "K-1 이 전파되지 않아 run 이 정상 종료됨 (kill-switch 미결박)"
    aborts = _abort_rows(ctx.events_path)
    assert len(aborts) >= 1, "abort 원장 행 0 — 원장 없는 종료 금지 (§3.10)"
    assert binding_spy.writes() == [], (
        f"kill-switch 이후 write 가 발생 — 전파 미결박: {binding_spy.writes()}")


def test_d14d_cleanup_swallowed_kill_switch_promotes_to_verdict(binding_spy, tmp_path):
    """D-14d **cleanup 승격 arm** (iter2 N1): 회수 경로가 흡수한 kill-switch 가 결과 축에 반영된다.

    자극 = **DELETE 만 401**(read/delete 권한 분리 모사) — GET/POST/PUT 는 정상 200 이라
    본문 시나리오는 완주하고 kill-switch 는 **cleanup 루프 안에서만** 발생한다.

    구 거동(iter1): cleanup 광역 `except` 가 흡수하며 `abort` 이벤트만 남기고 `abort_exc` 를
    세우지 않아 → `exit_code=0` · `operational_verdict=RECONCILED` 인데 **원장에는 K-1 abort 행**
    이 있는 상호모순 산출물. "흡수는 *중단*의 예외이지 *결과 반영*의 예외가 아니다" (§7.4).

    오라클 = ⓐ exit≠0 ⓑ `operational_verdict == "ABORTED"` ⓒ **`abort` 원장 정확히 1행**
    (승격 후 최종 1행으로 통일 — cleanup 내부 `emit_abort` 를 제거했다. 2행이면 중복 회귀)
    ⓓ 회수 루프는 **완주**했다(§3.10 무손상 — `attempted` 가 cleanup 대상 전건).
    mutant: 승격 2줄(`abort_exc = ctx.cleanup_kill_switch`) 제거 → ⓐⓑ RED /
            cleanup 내부 `emit_abort` 복원 → ⓒ RED(2행).
    """
    def responder(request: PreparedRequest) -> Response:
        parts = urlsplit(request.url)
        if parts.path.endswith(f"/pages/{TEST_PAGE}"):
            return _json_response(request, 200, {"id": TEST_PAGE, "title": SENTINEL_TITLE})
        if request.method == "DELETE":
            return _json_response(request, 401, {"message": "Unauthorized"})
        if request.method in ("POST", "PUT"):
            return _json_response(request, 200, {
                "id": "900001", "key": "cfp2889.bind", "value": {}, "version": {"number": 1}})
        return _json_response(request, 200, {"results": [], "_links": {}})

    binding_spy.responder = responder
    ctx, exit_code, results = _run_live_with(binding_spy, tmp_path, "n1-promote")

    cleanup = results.get("cleanup", {})
    # 구성 전제 — kill-switch 가 실제로 cleanup 안에서 흡수됐다 (오라클이 공허하지 않음)
    assert cleanup.get("kill_switch_ids"), (
        f"cleanup 이 kill-switch 를 흡수하지 않음 — 자극 미도달: {cleanup}")
    assert exit_code != 0, "cleanup 이 흡수한 kill-switch 가 exit code 에 미반영 (신호 소멸)"
    assert results.get("operational_verdict") == "ABORTED", (
        f'verdict 미승격 — {results.get("operational_verdict")} '
        f'(원장은 kill-switch 를 기록했는데 verdict 는 정상 종료를 말한다)')
    aborts = _abort_rows(ctx.events_path)
    assert len(aborts) == 1, (
        f"abort 원장 행 = {len(aborts)} (기대 정확히 1 — 승격 전 cleanup 내부 emit 이 남으면 2행)")
    # ⓓ §3.10 무손상 — 승격은 회수를 중단시키지 않는다
    assert cleanup.get("attempted", 0) >= len(cleanup.get("kill_switch_ids", [])), (
        "회수 루프가 첫 kill-switch 에서 중단됨 — §3.10 '회수는 계속' 위반")
    # 산출물 직렬화 가능 (예외 객체가 results 로 새지 않았다)
    assert isinstance(measure.emit_record(results), str)


def test_d14d_plain_cleanup_failure_does_not_promote(binding_spy, tmp_path):
    """D-14d **승격 경계 arm** (iter2 판정 (ii)): 일반 DELETE 실패는 승격 대상이 **아니다**.

    kill-switch 가 아닌 평범한 실패(404 등)는 `reconcile` 판정에 위임한다 — 경계가 흐려져
    `failed > 0` 만으로 승격하면 §7.4.1 상태 A(회수 완료) 회수 규범과 충돌한다.
    본 arm 이 없으면 "전부 승격" 이라는 과잉 처방이 GREEN 으로 통과한다.
    """
    def responder(request: PreparedRequest) -> Response:
        parts = urlsplit(request.url)
        if parts.path.endswith(f"/pages/{TEST_PAGE}"):
            return _json_response(request, 200, {"id": TEST_PAGE, "title": SENTINEL_TITLE})
        if request.method == "DELETE":
            # 500 = kill-switch 아닌 평범한 실패. 404 는 쓰지 않는다 — production 이 404 를
            # "이미 부재" 로 **성공 처리**(idempotent 회수)하므로 `failed` 가 0 이 되어 본 arm 의
            # 구성 전제 자체가 성립하지 않는다 (실측 확인).
            return _json_response(request, 500, {"message": "Internal Server Error"})
        if request.method in ("POST", "PUT"):
            return _json_response(request, 200, {
                "id": "900001", "key": "cfp2889.bind", "value": {}, "version": {"number": 1}})
        return _json_response(request, 200, {"results": [], "_links": {}})

    binding_spy.responder = responder
    ctx, _exit_code, results = _run_live_with(binding_spy, tmp_path, "n1-boundary")

    cleanup = results.get("cleanup", {})
    assert cleanup.get("failed", 0) > 0, f"구성 전제 미충족 — DELETE 실패 0: {cleanup}"
    assert not cleanup.get("kill_switch_ids"), "404 가 kill-switch 로 분류됨 (경계 오염)"
    assert results.get("operational_verdict") != "ABORTED", (
        "일반 DELETE 실패가 ABORTED 로 승격됨 — 승격 조건이 kill-switch 계열을 넘어 확장됐다")
    assert _abort_rows(ctx.events_path) == [], "kill-switch 아닌 실패에 abort 행이 남음"
def test_n9_preflight_does_not_declare_unverified_host_static():
    """N9(iter2) — **정적 backstop** (D-14 계상 대상 아님, 계상 규율 준수).

    결함: `preflight(stage=env)` 이벤트가 `base_url_host_declared=True` 를 host 검증
    (`create_client_or_abort`) **이전**에 기록하면, pin 실패 run 의 같은 원장에 `true` 행과
    K-7 abort 행이 공존하는 자기모순 원장이 된다.

    ★ **동적 결박 불가 — 정직 기재 (PL firsthand 실측 2026-08-07)**: 이 preflight 이벤트는
    `live = confirm_live_write ∧ creds ∧ page_id ∧ ¬skip_write` 4-AND 를 통과한 **live 경로
    전용**이다. plan 모드(4-AND 미충족)는 이 emit 을 지나지 않으므로, `--confirm-live-write`
    를 금지하는 본 suite 는 fake adapter 로도 해당 원장 행에 도달할 수 없다(실측: pin 실패
    arm 의 원장에는 abort 1행만 남고 preflight 행이 아예 없다). 따라서 오라클을 산출물
    side-effect 로 세울 수 없어 **소스 텍스트 검사로 강등**한다.

    본 테스트는 값싼 backstop 이며 D-14 결박 계열로 **계상하지 않는다** — 정적 검사는 죽은
    분기를 잡지 못한다는 계상 규율(§8.1.D-14)을 그대로 승계한다.
    mutant: preflight emit 에 필드를 되살림 → RED.
    """
    source = (pathlib.Path(measure.__file__)).read_text(encoding="utf-8")
    assert "base_url_host_declared" not in source, (
        "host 검증 이전 emit 되는 preflight 이벤트에 `base_url_host_declared` 단정이 남아 있음 "
        "(pin 실패 run 에서 `true` 행 ↔ K-7 abort 행 공존 = 자기모순 원장)")


# ════════════════════════════════════════════════════════════════════════════
# D-14e — 값-축 allowlist ↔ emit 채널 결박 (진입점 = run_live · iter2 NEW-1)
# ════════════════════════════════════════════════════════════════════════════

_TAINTED_AUTHOR_ID = "000000:aaaaaaaa-1111-2222-3333-444444444444"
_TAINTED_TENANT_BASE = f"https://{measure.EXPECTED_HOST}/wiki"


def test_d14e_emit_channel_carries_no_server_identity(binding_spy, tmp_path):
    """D-14e: 값-축 allowlist 가 golden 빌더뿐 아니라 **emit 채널**에도 걸려 있는가.

    §3.9 는 서버 유래 신원값의 차단층이 값-축 allowlist **하나**라고 선언한다. 그런데 그 선언이
    참이려면 서버 원본 envelope 가 **산출 채널로 새는 경로 자체가 없어야** 한다. 구 구현은
    `scenario_w3` 가 원본 envelope 를 반환 dict 에 실었고, 유출 차단이 호출부의 `pop` 한 줄에
    걸려 있었다 — **차단이 계약이 아니라 우연**이었다(그 줄이 지워지면 즉시 stdout 유출).

    오라클 = 문서 문언이 아니라 **실 산출물 바이트**: `emit_record(results)` 문자열에 서버 유래
    신원 패턴(account-id 형 · tenant host 형) 매치 **0건**. 패턴은 F3 스캐너 상수를 공유한다.
    mutant: `envelope_sample` 을 `results` 에 남긴 채 emit → RED.
    """
    def responder(request: PreparedRequest) -> Response:
        parts = urlsplit(request.url)
        if parts.path.endswith(f"/pages/{TEST_PAGE}"):
            return _json_response(request, 200, {"id": TEST_PAGE, "title": SENTINEL_TITLE})
        # v1 probe(`/wiki/rest/api/content/...`) 응답은 **깨끗한 body** 로 둔다 — 자극 축 분리.
        # 이 응답의 body 원문은 `W5.probe.body_verbatim` 으로 산출물에 **그대로 실린다**(관측
        # 충실도 목적, deny-scan 이 유일 필터). 그 축은 §3.9 값-축 allowlist 의 정의역이 아니라
        # **body 축(§7.1 step 1 truncate→scrub→drop)** 소관이라 본 sub 의 판정 대상이 아니다.
        # 여기 신원값을 넣으면 본 sub 가 envelope 축이 아니라 body 축 결함으로 RED 가 되어
        # mutant 판별 대상이 흐려진다 (PL firsthand 실측 — 별건 finding 으로 회부).
        if "/rest/api/content/" in parts.path:
            return _json_response(request, 200, {"id": "v1", "key": "cfp2889.bind"})
        # 서버가 신원 필드를 실어 보내는 상황 (I-4 비신뢰 진입점) — envelope 축 자극
        tainted = {"id": "900001", "key": "cfp2889.bind", "value": {"d": 1},
                   "version": {"number": 1, "authorId": _TAINTED_AUTHOR_ID},
                   "_links": {"base": _TAINTED_TENANT_BASE}}
        if request.method in ("POST", "PUT"):
            return _json_response(request, 200, tainted)
        return _json_response(request, 200, {"results": [], "_links": {}})

    binding_spy.responder = responder
    _ctx, _exit_code, results = _run_live_with(binding_spy, tmp_path, "d14e")

    emitted = measure.emit_record(results)
    # 구성 전제 — 오염 응답이 실제로 소비됐다 (오라클이 "미도달" 로 공허하게 성립하지 않음)
    assert binding_spy.writes(), "write 응답이 없어 오염 envelope 가 산출 경로에 진입하지 못했다"
    for label, pattern in F3_PII_PATTERNS:
        matches = re.findall(pattern, emitted)
        assert not matches, (
            f"emit 채널 산출 문자열에 서버 유래 {label} 유출 — {matches[:3]} "
            f"(값-축 allowlist 가 emit 채널에 미결박)")


def test_d14e_emit_channel_masks_identity_in_probe_body(binding_spy, tmp_path):
    """D-14e **body 축 arm** (iter2 연장): probe 응답 **body** 경유 신원값도 산출 채널에 안 남는다.

    envelope arm(위)과 **자극 축이 다르다**: 여기서 오염되는 것은 서버 응답 body 원문이며,
    그 값은 `W4`/`W5` probe 의 `body_verbatim` 필드로 산출물에 실린다. 이 축은 §3.9 값-축
    allowlist 의 정의역이 **아니라** body 축(§7.1 step 1) 소관이고, deny-scan 은 account-id 형을
    구조적으로 못 잡는다(`:`·`-` 분절로 20+ run 미형성) — 따라서 `mask_identity_tokens` 가
    이 축의 유일 차단층이다.

    오라클 = ⓐ `emit_record(results)` 산출 문자열에 신원 패턴 매치 0 (F3 SSOT 상수 공유)
    ⓑ **진단 문언은 verbatim 잔존**(over-limit 시그니처 `too large`·`32768`) — 마스킹이
    진단 가치를 훼손하지 않음을 같은 산출물에서 확인한다. ⓑ 가 없으면 "body 를 통째로 지워도
    GREEN" 이 되어 §4.2(실문언 = AC-12 1차 출처) 파괴안이 통과한다.

    mutant: `sanitize_body_field` 의 `mask_identity_tokens` 호출 제거 → ⓐ RED.

    ★ 정직 한계: body 마스킹은 **denylist = fail-open** 이라 미열거 신원 형식은 통과한다
    (envelope 축 allowlist 의 fail-closed 와 보증 수준이 다르다). 본 arm 은 열거된 패턴에
    한해 결박을 증명할 뿐 "body 축이 envelope 축과 같은 수준으로 막혔다" 를 증명하지 않는다.
    """
    over_limit_phrase = "The value is too large; maximum size is 32768 bytes"

    def responder(request: PreparedRequest) -> Response:
        parts = urlsplit(request.url)
        if parts.path.endswith(f"/pages/{TEST_PAGE}"):
            return _json_response(request, 200, {"id": TEST_PAGE, "title": SENTINEL_TITLE})
        # probe 경로(v1/v2)의 **에러 body** 에 진단 문언 + 신원값을 함께 실어 보낸다
        if "/rest/api/content/" in parts.path or request.method in ("POST", "PUT"):
            return _json_response(request, 400, {
                "message": over_limit_phrase,
                "authorId": _TAINTED_AUTHOR_ID,
                "base": _TAINTED_TENANT_BASE,
            })
        return _json_response(request, 200, {"results": [], "_links": {}})

    binding_spy.responder = responder
    _ctx, _exit_code, results = _run_live_with(binding_spy, tmp_path, "d14e-body")

    emitted = measure.emit_record(results)
    # 구성 전제 — body 가 실제로 산출물에 실렸다 (오라클이 "미도달" 로 공허하지 않음)
    assert "body_verbatim" in emitted, "probe body 필드가 산출물에 없어 자극이 도달하지 않았다"
    for label, pattern in F3_PII_PATTERNS:
        matches = re.findall(pattern, emitted)
        assert not matches, (
            f"probe body 경유 서버 유래 {label} 유출 — {matches[:3]} (body 축 마스킹 미결박)")
    # ⓑ 진단 가치 보존 — 신원 토큰만 지워지고 over-limit 시그니처는 남는다
    assert "too large" in emitted and "32768" in emitted, (
        "마스킹이 진단 문언까지 제거했다 — §4.2 실문언(AC-12 1차 출처) 파괴")


def test_d14e_scrub_precedes_deny_scan_witness():
    """D-14e **순서 witness arm**: `_scrub` 선행 ∧ 마스킹 후행 불변식을 산출 문자열로 결박.

    ★ **본 arm 이 존재하는 이유 = 앞선 "정의역 disjoint 실증" 이 판별력 0 이었기 때문**이다.
    그 실험은 신원 witness ∧ 20+ `[A-Za-z0-9+/=]` run 을 **동시에** 만족하는 입력을 쓰지 않아
    검증 대상 속성에 **비민감**했고(M9·M9b 양쪽 GREEN), 그 위에서 "두 층은 겹치지 않는다" 는
    거짓 명제가 실증된 것처럼 기록됐다. 여기서는 **양 속성을 동시에 만족하는 witness** 를 쓴다.

    witness = `aaaa…(24자)@acme.co.kr` — email 신원 패턴에 매치되면서 local part 가 20+ run 을
    형성한다(실측: `_deny_scan_for_secrets` 가 hit). 곧 두 층의 정의역은 **겹친다**.

    오라클 = **산출 문자열이 `***REDACTED***` 를 보유할 것** (= `_scrub` 이 20+ run 에 *먼저*
    발화한 증거). 실측 대조:
      - 현 조립(`_scrub`→deny→mask)              → `'***REDACTED***@acme.co.kr'`  (GREEN)
      - M9 (mask 를 deny 앞으로, `_scrub` 유지)   → `'***REDACTED***@acme.co.kr'`  (GREEN)
      - M9b(M9 ∧ `_scrub` 제거)                  → `'[identity-redacted]'`        (**RED**)

    ★ `omitted is True` 오라클은 **판별 불가**라 쓰지 않는다 — 현 조립도 M9b 도 `omitted=False`
    다(`_scrub` 이 20+ run 을 지워 deny 가 애초에 발화하지 않거나, 마스킹이 먼저 지워 같은 결과).
    판별은 **어느 층이 먼저 손댔는지가 남는 산출 문자열**에서만 선다.

    ★ **M9 단독이 GREEN 인 것은 정상이며 검출 대상이 아니다** — `_scrub` 이 선행하는 한 deny
    판정 입력에는 이미 20+ run 이 없으므로 마스킹을 판정 앞에 둬도 실제로 안전하다. 본 arm 이
    지키는 불변식은 "마스킹이 `_scrub` 보다 앞서지 않을 것" 이고, 그 위반(M9b)만 RED 다.
    """
    witness = '{"m":"too large 32768","e":"' + "a" * 24 + '@acme.co.kr"}'

    # 구성 전제 ① — witness 가 신원 패턴에 실제로 매치된다
    assert mask_identity_tokens(witness) != witness, "witness 가 신원 패턴에 매치되지 않음"
    # 구성 전제 ② — witness 가 20+ run 을 형성한다 (두 층 정의역이 겹친다는 실측 근거)
    ok, _err = _deny_scan_for_secrets("a" * 24 + "@acme.co.kr")
    assert ok is False, "witness 가 20+ run 을 형성하지 않음 — 교차 전제 미충족"

    out, _omitted, _length = sanitize_body_field(witness)

    assert "***REDACTED***" in out, (
        f"산출물에 `_scrub` 발화 흔적이 없음 — 마스킹이 `_scrub` 보다 먼저 실행돼 deny 대상을 "
        f"선소거했다(K-6 hollow 경로): {out!r}")
    # 진단 문언은 여전히 verbatim (마스킹·scrub 이 시그니처를 훼손하지 않음)
    assert "too large" in out and "32768" in out

