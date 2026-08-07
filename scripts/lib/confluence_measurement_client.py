#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confluence_measurement_client.py — 측정 전용 REST seam (CFP-2889 Change Plan §3.7 / §5 #2).

`MeasurementRESTClient(ConfluencePropertyREST)` = **additive 서브클래스** — 부모 클래스에 가하는
diff 0 (seam 축 한정 주장. production 클래스 내부는 D1~D6 로 별도 재설계됨 — "전면 0-diff" 아님).

배치 근거 (결정 4 — ModuleArch ② · Refactor 옵션2 · SecurityArch T-1 3자 합치):
  - **env-var 게이트 금지**: creds 파일 allowlist 가 `CFP2829_*` 를 env 로 통째 주입하므로
    env 스위치는 "신뢰 못할 파일이 예산 가드를 끈다" 와 동형 (T-1).
  - default-off 의 실체 = 본 모듈이 **production 경로에서 미참조** (유일 인스턴스화 지점 =
    `scripts/confluence_backward_measure.py`). grep/ast discriminating test 로 고정.
  - dependency direction = 측정 → 서브클래스 → 부모 단방향.

추가 표면 3종 (§4.1 / §3.5 / 결정 14):
  1. `write_property_unbudgeted` — pre-flight budget bypass (AC-5 over-limit payload 의 실 API 도달).
     명명 제약 = "존재하지 않는 budgeted 짝을 함의하는 이름 금지" (부모에 budgeted 짝이 존속하지
     않으므로 구 key-path 메서드명 + `_unbudgeted` 형 명명은 모순 신호 — §4.1 정정 확정치 채택).
  2. `probe_property_v1` — v1 endpoint PUT **1-call** probe (재시도·backoff 0, 429 조우 = 즉시 종결).
  3. 전 응답 HeaderCapture — `_perform_request` override 로 **응답마다 무조건** 레코드 생성
     (AC-6a normative: 레코드 생성은 자사 코드 결정론이라 헤더 존재 여부와 무관하게 강제 가능).

Security (Change Plan §7):
  - T-6: **응답 헤더 전용** 캡처 (요청 헤더 캡처 0 — `Basic <b64>` 직렬화 표면 미생성).
  - 결정 14 값 3분류: value-allow(rate family + content-type/length/date) / presence-only
    (set-cookie·authorization·www-authenticate·proxy-authenticate) / **unknown → presence-only**.
  - T-10 잔여 방어: value-allow 값도 `_scrub` 경유 후 200자 절단 (미지 secret 혼입 backstop).
  - 응답 body = 부모의 `sanitize_body_field` 재사용 (truncate ≤200B → scrub → deny-scan 원경로,
    hit 시 필드 drop). 본 모듈은 sanitization 원시함수를 **재구현하지 않는다** (rest.py = SSOT).
  - `safe_path` = **validator 강제** (자사 템플릿 경로 화이트리스트 fullmatch 실패 = ValueError,
    silent pass-through 금지 — `grouped_hex` digest 축 validator 동형). 비-템플릿 입력
    (서버 유래 `_links.next` 등 I-4 비신뢰) 은 `safe_path_or_drop` 이 **필드 drop + marker** 로
    흡수한다 (§3.9 body 축 동형) — 변환 세탁 경로 0.

보안테스트 FIX iter1 (CFP-2889 — F2 (L3) / F6):
  - F2 (L3): `probe_property_v1` 진입부 `validate_resource_id(page_id, field="page_id")` —
        측정 전용 표면도 예외 아님 (§4.1 정밀화 註 "적용 3층 전부 필수 — 하나라도 빠지면 그
        층이 우회로"). 처분 = **local-reject** (HTTP 0회 · run 계속) 이며 abort 는 L1(생성자
        host pin) 만 (§7.1 註 표: L2·L3 = local-reject / L1 = K-7 abort).
        검증 위치 = 경로 `format` · `record_write_attempt` **이전** — 본 함수는 조립한 경로를
        `_perform_request` 에 그대로 넘기며 `safe_path` 화이트리스트는 *record 표기 시점* 에만
        걸리는 표기 validator 이지 **송신 전 가드가 아니다** (가드 위치를 혼동하면 위반 id 가
        write 회계에 계상된 뒤 실제로 송신된다).
  - F6: `probe_property_v1` 의 raw `safe_path` 2 site → `safe_path_or_drop` 대칭화.
        특히 `except` 핸들러 안의 raw 호출은 비-템플릿 경로에서 `ValueError` 가 **원 예외를
        덮고 전파**해 "관측 실패도 관측 결과" 반환 자체를 파괴했다 (동 모듈이 이미 흡수 계층
        `safe_path_or_drop` 을 갖고 있는데 이 2 site 만 미사용 = 비대칭).
        반환 dict 에 `endpoint_omitted_by_validator` 추가 — `_build_header_capture` 와 동형
        (V1ProbeResult §4.2 additive 1 필드; 소비자 = `scenario_w5` 의 `probe.get(...)` +
        report passthrough 뿐이라 키 집합 확장은 무해).

D6: 내부 import = `lib.confluence_property_rest` qualified (repo 단일 참조 방법).
"""

import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# cp949 guard (Windows CI utf-8 stdout)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from lib.confluence_property_rest import (  # noqa: E402  (sys.path 배선 = 호출 진입점 소관)
    RATE_HEADER_FAMILIES,
    ConfluencePropertyREST,
    KillSwitchAbort,
    _scrub,
    sanitize_body_field,
    validate_resource_id,
)


# ── 헤더 값 정책 (결정 14) ───────────────────────────────────────────────────

#: rate family 외 value-allow (비밀 아님이 구조적으로 명백한 전송 메타).
VALUE_ALLOW_EXTRA = ("content-type", "content-length", "date")

#: 값 자체가 자격증명·세션 매개일 수 있는 이름 — 존재·길이만 (T-10).
PRESENCE_ONLY_NAMES = ("set-cookie", "authorization", "www-authenticate", "proxy-authenticate")

#: value-allow 값 절단 상한 (body 축 200B 정책과 동형).
HEADER_VALUE_MAX = 200

#: v1 content property endpoint (구 RUNBOOK·docstring 관행 경로).
#: v1 현행 상태(제거/유지)는 **확인 불가** — 제거 시도 후 rollback 이력만 존재하므로
#: 실측 1-call 이 유일 확정 수단이다 [source: community.developer.atlassian.com/t/79687 · /t/95729].
V1_PROPERTY_PATH_TEMPLATE = "/wiki/rest/api/content/{page_id}/property/{key}"


#: 자사 템플릿 경로 화이트리스트 (v2 property CRUD 2형 + v1 property 1형).
#: query string 포함 경로는 자사 템플릿 구성이 아니므로 **불허** (params 는 별도 인자로 전달된다).
_OWN_PATH_RES = (
    re.compile(r"/wiki/api/v2/pages/[A-Za-z0-9._-]{1,64}/properties(?:/[A-Za-z0-9._-]{1,64})?"),
    re.compile(r"/wiki/rest/api/content/[A-Za-z0-9._-]{1,64}/property/[A-Za-z0-9._-]{1,128}"),
    re.compile(r"/wiki/api/v2/pages/[A-Za-z0-9._-]{1,64}"),
)


def safe_path(path: str) -> str:
    """자사 템플릿 요청 경로 → 산출물 기록 표기 (`/` 를 ` / ` 로 분절, 무손실·결정론 역변환).

    이유 (구조적): deny-scan·`_scrub` 의 문자클래스 `[A-Za-z0-9+/=]` 에 **`/` 가 포함**되어
    `/wiki/api/v2/pages/<id>/properties` 같은 자사 구성 경로가 통째로 20+ run 을 형성한다 →
    emit 파이프라인 step 2(`_scrub`) 에서 경로 전체가 `***REDACTED***` 로 소실되어 캡처 레코드의
    endpoint 정보가 무의미해진다.

    **validator 강제 (grouped_hex digest 축 동형 — DR-P0-2 (a))**: 입력이 자사 템플릿 경로
    화이트리스트에 `fullmatch` 하지 않으면 **ValueError 로 변환 거부** (silent pass-through 금지).
    "비밀 아님이 구성적으로 보장된 값만 변환" 이 규율이며, 임의 문자열이 분절 경유로 20+ run 을
    쪼개는 세탁 재도입을 차단한다. 서버 유래 문자열(`_links.next` 등 I-4 비신뢰)은 정의상 이
    화이트리스트를 통과하지 못하고, 그 경우의 처분은 변환이 아니라 **필드 drop** 이다
    (`safe_path_or_drop` — §3.9 body 축 동형).

    최종 record 전체 deny-scan(K-6) 은 변환 후에도 원형 그대로 수행된다.
    """
    if not isinstance(path, str):
        raise ValueError("safe_path: 문자열 아님 — 변환 거부 (validator)")
    if not any(pattern.fullmatch(path) for pattern in _OWN_PATH_RES):
        raise ValueError("safe_path: 자사 템플릿 경로 아님 — 변환 거부 (validator, 세탁 차단)")
    return " / ".join(path.split("/"))


def safe_path_or_drop(path: str) -> Tuple[Optional[str], bool]:
    """`safe_path` 흡수 계층 — 비-템플릿 경로는 **필드 drop + marker** (§3.9 body 축 동형).

    Returns: `(safe | None, omitted_by_validator)`

    실 도달 경로: 부모 `list_properties_v2` 의 pagination 추종은 서버 응답 `_links.next` 상대경로를
    그대로 전송하므로 비신뢰 문자열이 캡처 계층에 도달한다 — 이때 run 을 깨지 않으면서(관측 계속)
    세탁도 하지 않는 처분이 drop 이다.
    """
    try:
        return safe_path(path), False
    except ValueError:
        return None, True


def classify_header_policy(name: str) -> str:
    """헤더 이름 → 값 정책 3분류 (결정 14). 미지 이름은 **presence-only** 가 기본 (fail-safe)."""
    lname = (name or "").lower()
    if lname in PRESENCE_ONLY_NAMES:
        return "presence-only"
    if lname in VALUE_ALLOW_EXTRA:
        return "value-allow"
    for family in RATE_HEADER_FAMILIES:
        if lname.startswith(family):
            return "value-allow"
    return "presence-only"


def _header_items(resp) -> List[Tuple[str, str]]:
    """응답 헤더 (이름, 값) 목록 — requests CaseInsensitiveDict / `_CIHeaders` 공통 표면."""
    headers = getattr(resp, "headers", None)
    if headers is None:
        return []
    try:
        return [(str(k), str(v)) for k, v in headers.items()]
    except Exception:
        return []


class MeasurementRESTClient(ConfluencePropertyREST):
    """측정 전용 클라이언트 — production 경로 미참조 (default-off 의 실체).

    부모 공개 표면(list/create/update/remove/upsert + store/load chunked)은 그대로 상속하고,
    측정에만 필요한 3종을 additive 로 얹는다. 부모 메서드 재정의는 `_perform_request` 1건뿐이며
    그 재정의도 **관측 부가**(super() 결과를 그대로 반환)라 전송 거동은 무변경이다.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #: AC-6a — 응답별 HeaderCapture 레코드 (mock/dry/synthetic 포함 무조건 append).
        self.header_captures: List[Dict[str, Any]] = []

    # ── 결정 14 — 전 응답 헤더 캡처 (AC-6a) ──

    def _perform_request(self, method: str, path: str, *, body_bytes: Optional[bytes] = None,
                         params: Optional[Dict[str, str]] = None, dry: bool = False,
                         timeout: int = 10):
        """부모 choke-point 를 그대로 호출하고 **응답마다** 캡처 레코드를 남긴다.

        캡처 대상 = mock(401/429 synthetic)·dry(golden-파생)·live 전부 — "레코드 생성은 자사 코드
        결정론" 이라는 AC-6a 전제를 구조적으로 보장한다 (헤더 부재 = 레코드 부재가 아님).
        예외로 응답이 없으면(세션 불가 등) 캡처 대상 자체가 없어 자연 미기록.
        """
        resp = super()._perform_request(method, path, body_bytes=body_bytes, params=params,
                                        dry=dry, timeout=timeout)
        self.header_captures.append(self._build_header_capture(method, path, resp))
        return resp

    def _build_header_capture(self, method: str, path: str, resp) -> Dict[str, Any]:
        """§4.2 HeaderCapture 조립 — 이름 전수 + 값 3분류 + rate family 존재 표기."""
        items = _header_items(resp)
        names = [name for name, _v in items]
        value_policy: Dict[str, Dict[str, Any]] = {}
        for name, value in items:
            policy = classify_header_policy(name)
            if policy == "value-allow":
                value_policy[name] = {
                    "policy": "value-allow",
                    "value": _scrub(str(value))[:HEADER_VALUE_MAX],
                }
            else:
                value_policy[name] = {"policy": "presence-only", "len": len(str(value))}
        lowered = [n.lower() for n in names]
        families = [fam for fam in RATE_HEADER_FAMILIES
                    if any(n.startswith(fam) for n in lowered)]
        endpoint, endpoint_omitted = safe_path_or_drop(path)
        return {
            "endpoint": endpoint,
            "endpoint_omitted_by_validator": endpoint_omitted,
            "verb": method,
            "http_status": getattr(resp, "status_code", None),
            "headers_name_complete": names,
            "headers_value_policy": value_policy,
            "rate_header_families_present": families,
        }

    # ── seam 1: pre-flight bypass write (AC-5) ──

    def write_property_unbudgeted(self, page_id: str, key: str, value: Any, *,
                                  ascii_mode: bool = False,
                                  probe_pair_id: Optional[str] = None,
                                  dry: Optional[bool] = None
                                  ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """pre-flight budget check 를 **끈** upsert — over-limit payload 의 실 API 도달용.

        부모 `_upsert_impl(enforce_budget=False)` 위임 (프로토콜·회계·retry 정책 전부 부모 그대로).
        keyword-only 인자 = 오호출로 예산 가드가 꺼지는 사고 방지 (T-1 보조).

        Returns: (ok, PropertyEnvelope|None, ErrorInfo|None)
        """
        return self._upsert_impl(page_id, key, value, dry=dry, enforce_budget=False,
                                 ascii_mode=ascii_mode, probe_pair_id=probe_pair_id)

    # ── seam 2: v1 1-call probe (결정 11) ──

    def _v1_probe_failure(self, path: Optional[str], exception_name: str) -> Dict[str, Any]:
        """V1ProbeResult **실패형 단일 emitter** — L3 local-reject · 전송 예외 2 arm 공용.

        같은 shape 를 2 arm 이 각자 조립하면 F6 형 드리프트(한쪽만 raw `safe_path`)가 그대로
        재생산되므로 emitter 를 하나로 모은다 (ADR-140 — 신규 중복 유입 금지).

        `path is None` = 경로가 **조립되기 전** 거부된 경우(L3) — 표기할 원본 자체가 없으므로
        endpoint drop + marker (`_build_header_capture` 의 drop 표기와 동형).
        """
        if path is None:
            endpoint: Optional[str] = None
            endpoint_omitted = True
        else:
            endpoint, endpoint_omitted = safe_path_or_drop(path)
        return {
            "endpoint": endpoint,
            "endpoint_omitted_by_validator": endpoint_omitted,
            "verb": "PUT",
            "http_status": None,
            "body_verbatim": None,
            "body_omitted_by_deny_scan": None,
            "body_length": None,
            "headers_capture_index": None,
            "headers": None,
            "classification": "other",
            "exception": exception_name,
        }

    def probe_property_v1(self, page_id: str, key: str, value: Any,
                          dry: Optional[bool] = None) -> Dict[str, Any]:
        """v1 property endpoint PUT **1-call** probe → V1ProbeResult (§4.2).

        규율:
          - **재시도·backoff 0** — `_send_write` 를 경유하지 않는다 (retry 가 붙기 때문).
            `_perform_request` 를 직접 호출한다.
          - 429 조우 = 즉시 종결 기록 (재시도 0). `rate_events` 에 관측은 append 하되
            **abort 하지 않는다** (K-4 임계 판정은 write 경로 `_observe_429` 소관).
          - self-cap 회계 편입 (§13L.6) — accounting 이 있으면 `record_write_attempt`
            (cap 초과 시 `WriteCapExceeded` 가 그대로 전파되는 것이 정상 = hard-stop).
          - body = 부모 `sanitize_body_field` 경유 (truncate → scrub → deny-scan, hit 시 drop).

        classification: 413 → "413-over-limit" / 410 → "410-gone" / 그 외 → "other".
        413·410 어느 쪽이든 유효 관측이다 (G4 — v1 현행 상태 확정이 목적).

        **L3 자원 id 검증 (F2)**: `page_id` 는 URL 경로 보간 성분이므로 진입부에서 `[0-9]{1,32}`
        fullmatch 로 검증하고 위반은 **local-reject** 한다 (HTTP 0회 · 회계 미계상 · run 계속).
        측정 전용 표면이라고 예외를 두면 그 표면이 L1/L2 의 우회로가 된다.
        local-reject 식별 시그니처 = `http_status is None` ∧ `endpoint is None`
        (`endpoint_omitted_by_validator=True`) ∧ `exception == "ValueError"` — 전송 예외 arm 과
        같은 필드 집합을 쓰되(신규 shape 0) 경로가 아예 조립되지 않은 점이 구분자다.
        `key` 는 자기 저작 합성값(`cfp2889.measure.*`)이라 본 계약 대상이 아니다.
        """
        try:
            validate_resource_id(page_id, field="page_id")
        except ValueError as e:
            # L3 local-reject — 경로 조립·`record_write_attempt` 보다 앞이라 write 회계에
            # 잡히기 전에 거부된다 (abort 아님: 이 호출 1건의 오도착 위험만 차단).
            return self._v1_probe_failure(None, type(e).__name__)

        dry = self._is_dry_run(dry)
        path = V1_PROPERTY_PATH_TEMPLATE.format(page_id=page_id, key=key)
        body_bytes = self._serialize({"key": key, "value": value})

        if self.accounting is not None:
            self.accounting.record_write_attempt(
                {"label": f"PUT v1 {key}", "key": key, "page_id": page_id, "method": "PUT",
                 "api_version": 1}
            )

        try:
            resp = self._perform_request("PUT", path, body_bytes=body_bytes, dry=dry)
        except KillSwitchAbort:   # F5 — kill-switch 는 "관측 결과" 로 강등하지 않는다
            # 본 핸들러는 *관측 실패*(연결·타임아웃·파싱)를 흡수하는 계층이다. kill-switch 계열이
            # 여기 도달하면 `{"exception": ...}` 관측 레코드로 강등돼 신호가 소멸하므로 base 로만
            # 재-raise 한다 (§3 결정 ③ — 중간 except 는 개별 타입 열거 금지).
            # **도달 경로 정직 기재 (firsthand 실측 2026-08-07)**: 401→`AuthAbortError` 승격은
            # `_send_write` 내부(rest.py)에만 있고 `_perform_request` 자체에는 없다 → live 경로의
            # 401 은 이 핸들러에 *예외로 도달하지 않는다*(status 그대로 반환·관측 기록됨).
            # 실 도달 경로 = dry 경로의 `GoldenFixtureMissingError`(KillSwitchAbort 하위).
            # 즉 본 선행절은 "401 삼킴 차단" 이 아니라 **F5 형식 invariant 준수 + dry kill-switch
            # 전파** 가 실효다 (신규 kill-switch 추가 시 이 site 를 손대지 않아도 전파 보존).
            raise
        except Exception as e:                       # noqa: BLE001 — 관측 실패도 관측 결과다
            # F6: raw `safe_path` 는 이 핸들러 안에서 `ValueError` 로 **원 예외를 덮고 전파**했다
            # (반환 소실 = 관측 결과 파괴). 흡수 계층으로 대칭화한다.
            return self._v1_probe_failure(path, type(e).__name__)

        status = getattr(resp, "status_code", None)
        if status == 429:
            # 관측만 append — 재시도 0, abort 0 (K-4 임계는 write 경로 소관).
            self.rate_429_count += 1
            self.rate_events.append({
                "status": 429,
                "retry_after_raw": resp.headers.get("Retry-After"),
                "wait_applied_seconds": None,
                "source": "v1-probe",
                "note": "1-call probe — 재시도 0, 즉시 종결 기록",
            })

        try:
            text = resp.text or ""
        except Exception:                            # noqa: BLE001
            text = ""
        body_verbatim, omitted, body_len = sanitize_body_field(text)

        if status == 413:
            classification = "413-over-limit"
        elif status == 410:
            classification = "410-gone"
        else:
            classification = "other"

        capture_index = len(self.header_captures) - 1 if self.header_captures else None
        capture = self.header_captures[capture_index] if capture_index is not None else None
        endpoint, endpoint_omitted = safe_path_or_drop(path)   # F6 — 표기 validator 흡수 대칭화
        return {
            "endpoint": endpoint,
            "endpoint_omitted_by_validator": endpoint_omitted,
            "verb": "PUT",
            "http_status": status,
            "body_verbatim": body_verbatim,
            "body_omitted_by_deny_scan": omitted,
            "body_length": body_len,
            "headers_capture_index": capture_index,
            "headers": capture,
            "classification": classification,
        }


def create_measurement_client(base_url: str, token: Optional[str], email: Optional[str],
                              accounting=None) -> MeasurementRESTClient:
    """측정 클라이언트 팩토리 — creds 는 호출자가 명시 전달 (env 판독은 진입점 1곳으로 고정).

    `create_rest_client` 의 사본이 아니다: 부모 팩토리는 production 축, 본 함수는 측정 축이며
    creds 를 env 에서 재판독하지 않고 **주입**받는다 (측정 진입점의 preflight 판정과 이중화 방지).
    """
    return MeasurementRESTClient(base_url, token, email, accounting=accounting)


__all__ = [
    "MeasurementRESTClient",
    "create_measurement_client",
    "classify_header_policy",
    "safe_path",
    "safe_path_or_drop",
    "VALUE_ALLOW_EXTRA",
    "PRESENCE_ONLY_NAMES",
    "V1_PROPERTY_PATH_TEMPLATE",
]
