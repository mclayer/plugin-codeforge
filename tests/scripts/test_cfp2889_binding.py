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
from lib.confluence_property_rest import WriteAccounting

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
