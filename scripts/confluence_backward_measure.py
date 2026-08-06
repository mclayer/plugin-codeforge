#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confluence_backward_measure.py — CFP-2829 잔여 4건 live 실측 harness (CFP-2889 전면 재작성).

원판(CFP-2829 S2)은 born-broken 이었다 — verdict 하드코딩(L304-313)·AC-13 4분기가 HTTP 0회
상태에서 **tier enum 비소속 산문 토큰**을 고정 반환(L341/350/361/375)·basic-auth 에 비적용인
**추정 tier 수치 필드** 각인(L374)·구 key-path 3메서드 호출·HTTP 0회 상태의 `(observed)` 각인.
본 파일은 그 구조를 **전면 재작성**한다 (Change Plan §5 #3).

핵심 구조 (테스트 가능성 = 컴포넌트 분리):
  1. **순수 verdict 3종** (`verdict_storage_axis` / `verdict_over_limit_axis` / `verdict_rate_axis`)
     — 관측 dict 입력만, I/O 0. 반환 직전 `lib.ac_id.TIER_ENUM` 대조 assert (비소속 토큰 =
     즉시 AssertionError = fail-loud). 원판의 enum 비소속 산문 토큰·추정 tier 필드는 본 파일에
     식별자·리터럴 어느 형태로도 잔존하지 않는다 (grep 으로 반증 가능한 형태의 단언).
  2. **결정론 fixture** (`build_w1_fixture` / `build_boundary_payload`) — `time.time()` 0
     (결정 16: byte-exact 정의역 = 동일 실행 내 store→load).
  3. **PageIdentityGate** (K-5) — `docs/confluence-ia-tree.yaml` runtime 파싱 deny-set
     (건수 박제 금지) + sentinel 양성 확인 + fail-closed.
  4. **RunContext** — WriteAccounting(cap=20) 소유 + write-ahead orphan registry +
     10-event NDJSON (`~/.claude/codeforge-scratch/`).
  5. **단일 emit choke-point** `emit_record` (T-12) — stdout·NDJSON·golden-후보 전 채널 공통.
  6. **kill-switch 7종** + try/finally cleanup 결박(P0-c) + step R reconcile.

운영 규율 (§3.10 / §13L):
  - live 실행 4-AND: `--confirm-live-write` ∧ creds ∧ `CFP2829_TEST_PAGE_ID` ∧ ¬SKIP_WRITE.
  - flag 부재 = **plan 모드** (회계표 출력 후 exit 0 — 실 write 0. HTTP 0회 원칙, 단
    creds ∧ page-id 존재 시 page 신원 GET 1회 read-only 확인만 허용).
  - self-cap ≤20 = POST·PUT HTTP **시도** 합산(retry 포함). DELETE 는 cap 밖 (soft-ceiling 40).
  - 실행 위치 = **개발자 로컬 셸** (CI 배선 금지 — §7.4.5/§7.4.6 N/A 유지 조건).
  - **page-destructive REST 메서드 신설 금지** invariant (§13L.3 — page 생성은 MCP 만).

Env vars:
  - CONFLUENCE_BASE_URL        : Confluence instance URL (host pin 대상 — T-5)
  - ATLASSIAN_API_TOKEN / ATLASSIAN_USER_EMAIL : basic-auth creds (env-indirect, SA-1)
  - CFP2829_TEST_PAGE_ID       : throwaway test page id (write 필수 조건)
  - CFP2829_MEASURE_SKIP_WRITE : 1 이면 creds 가 있어도 write 0
  - CFP2889_TEST_PAUSE_AFTER_INTENT : **test-only** — write_intent 기록 직후 sleep(초).
                                 §8.5.2 subprocess fork-and-kill 테스트 seam (지연만, 거동 변경 0)
"""

import argparse
import copy
import datetime
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# cp949 guard (Windows utf-8 stdout)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── sys.path 배선 (scripts/ + scripts/lib/) — D6 ────────────────────────────
# sibling `confluence_backward_sync.py` L45-50 동형. 이 배선이 없으면 measure.py 단독 실행 시
# rest.py 의 지연 import(`lib.confluence_property_chunking`)가 find_spec None 으로 실패한다
# (pytest 는 conftest 가 우회해 GREEN 이 결함을 은폐 — 진짜 오라클 = subprocess 단독 실행 D-11).
_SCRIPTS_DIR = Path(__file__).resolve().parent
_LIB_DIR = _SCRIPTS_DIR / "lib"
for _p in (str(_SCRIPTS_DIR), str(_LIB_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lib.ac_id import TIER_ENUM                                    # noqa: E402
from lib.confluence_measurement_client import (                    # noqa: E402
    MeasurementRESTClient, create_measurement_client, safe_path_or_drop,
)
from lib.confluence_property_chunking import (                     # noqa: E402
    MANIFEST_KEY as LOCAL_MANIFEST_KEY, chunk, chunk_key as local_chunk_key,
    json_encoded_size,
)
from lib.confluence_property_rest import (                         # noqa: E402
    BUDGET_BYTES, CHUNK_KEY_TEMPLATE, DELETE_SOFT_CEILING, EXPECTED_HOST, MANIFEST_KEY,
    PROPERTY_KEY_PREFIX, WRAP_OVERHEAD_BYTES,
    AuthAbortError, ChunkStoreError, KillSwitchAbort, PropertyResolveError, RateAbortError,
    SanitizedHandler, WriteAccounting, WriteCapExceeded,
    _deny_scan_for_secrets, _scrub, _unwrap_property,
    effective_chunk_budget, grouped_hex, sanitize_body_field, validate_resource_id,
)


# ── 상수 ─────────────────────────────────────────────────────────────────────

#: self-cap (해석 A — 사용자 확정): POST·PUT HTTP 시도 합산(retry 포함) ≤ 20.
WRITE_CAP = 20

#: K-3 — 연속 write 실패 임계 (기대-400 probe 는 `probe_pair_id` 오라클 분리로 제외).
CONSECUTIVE_FAILURE_ABORT = 3

#: NDJSON 10-event enum (§13L.11) — 이 외 event type 기록 금지.
EVENT_TYPES = (
    "approval", "preflight", "write_intent", "write_result",
    "cleanup_intent", "cleanup_result", "cap_state", "abort",
    "reconcile_snapshot", "reconcile_verdict",
)

#: 측정 전용 property key namespace (운영 key 와 disjoint — 회수 식별 용이).
MEASURE_KEY_PREFIX = "cfp2889.measure"

#: throwaway page 양성 sentinel (제목 포함 필수 — K-5).
PAGE_SENTINEL_PREFIX = "CFP-2889-THROWAWAY-"

KST = datetime.timezone(datetime.timedelta(hours=9))

TEST_PAGE_ID_ENV = "CFP2829_TEST_PAGE_ID"
SKIP_WRITE_ENV = "CFP2829_MEASURE_SKIP_WRITE"
TEST_PAUSE_ENV = "CFP2889_TEST_PAUSE_AFTER_INTENT"
CBL_SKIP_ISSUE_CREATE_ENV = "CBL_SKIP_ISSUE_CREATE"

CONFLUENCE_BASE_URL_ENV = "CONFLUENCE_BASE_URL"

#: 기본 base_url — host pin SSOT(`EXPECTED_HOST`, rest.py)에서 **파생**한다 (상수 2벌 금지).
#: 리터럴을 따로 두면 한쪽만 갱신됐을 때 "기본값이 자기 pin 을 통과하지 못하는" born-broken 이 된다.
DEFAULT_BASE_URL = f"https://{EXPECTED_HOST}"

logger = logging.getLogger("confluence_backward_measure")


# ── kill-switch 예외 (K-3 / K-5 / K-6 / K-7 — 나머지는 rest.py 소유) ─────────

class MeasureAbort(KillSwitchAbort):
    """측정 run abort 기반 클래스 — 모든 abort 는 `abort` 이벤트 기록 후 exit≠0.

    base = rest.py 의 `KillSwitchAbort` (F5). 하위 4종(K-3/K-5/K-6/K-7)이 kill-switch 표식을
    자동 상속하므로 중간 `except` 의 `except KillSwitchAbort: raise` 선행절 하나가 rest.py 소유
    kill-switch(K-1/K-2/K-4)와 본 모듈 소유 kill-switch를 **함께** 결박한다 (site 별 타입 열거
    드리프트 0).

    의존 방향은 무역전이다 — base 는 부모 모듈이 소유하고 rest.py 는 measure.py 를 import 하지
    않는다 (측정 → 부모 단방향).
    """
    kill_switch = "K-?"


class ConsecutiveWriteFailure(MeasureAbort):
    """K-3 — 연속 write 실패 >= 3 (probe 기대-400 은 오라클 분리로 카운트 제외)."""
    kill_switch = "K-3"


class PageIdentityAbort(MeasureAbort):
    """K-5 — page 신원 게이트 실패 (deny-set hit / sentinel 부재 / GET·파싱 실패 = fail-closed)."""
    kill_switch = "K-5"


class EmitDenyScanAbort(MeasureAbort):
    """K-6 — emit choke-point 최종 deny-scan hit (원문은 어떤 채널에도 기록하지 않는다)."""
    kill_switch = "K-6"


class CredsPreflightAbort(MeasureAbort):
    """K-7 — **creds·endpoint preflight** 실패 (creds 부재 / base_url host pin·형식 거부 /
    대상 자원 id 문법 위반).

    정의 확장 (§3.10 註 ④ — FIX iter1 F1): 원 정의는 "creds preflight" 였으나, 생성자 host pin
    (F1)과 L1 자원 id 검증(F2)이 던지는 실패도 **run 을 시작하기 전 전제가 붕괴** 라는 동일
    성질이라 K-7 이 자연 수용한다. **신규 K-8 은 신설하지 않는다** — kill-switch 개수 표기
    ("7종")가 §13L.7·§8.5.2·runbook 3면에 박혀 있어 신설은 3면 동시 개정을 요구하고, 그 비용이
    분류 이득을 넘는다.

    K-5 와 disjoint (번호 오독 차단):
      - **K-5** = 문법은 맞으나 deny-set 소속이거나 sentinel 이 없는 **page 신원** 실패.
      - **K-7** = **문법 자체가 틀린** resource-id / endpoint preflight 실패.
    한쪽이 다른 쪽을 포섭하지 않는다 (K-7 통과가 K-5 를 면제하지 않고, 그 역도 아니다).
    """
    kill_switch = "K-7"


_KILL_SWITCH_BY_TYPE = (
    (AuthAbortError, "K-1"),
    (WriteCapExceeded, "K-2"),
    (ConsecutiveWriteFailure, "K-3"),
    (RateAbortError, "K-4"),
    (PageIdentityAbort, "K-5"),
    (EmitDenyScanAbort, "K-6"),
    (CredsPreflightAbort, "K-7"),
)


def kill_switch_id(exc: BaseException) -> str:
    for exc_type, kid in _KILL_SWITCH_BY_TYPE:
        if isinstance(exc, exc_type):
            return kid
    if isinstance(exc, KeyboardInterrupt):
        return "operator-interrupt"
    return "unclassified"


# ── 시각·경로 helper ────────────────────────────────────────────────────────

def kst_now_iso() -> str:
    """KST ISO 8601 (`+09:00`) — 산출물 provenance 표기용.

    재사용 탐색 결과(hygiene): `scripts/lib/kst_render_stamp.py` = CLI `main()` 전용
    (`MM/DD HH:MM:SS` 렌더 문자열), `check_kst_timestamp.py` = validator regex,
    `append_spawn_event._utc_z_now` = UTC-Z(사양상 KST 아님)·private — **ISO8601 KST 를
    산출하는 import 가능 helper 는 repo 에 부재**하므로 본 3줄만 지역 정의한다.
    """
    return datetime.datetime.now(KST).isoformat(timespec="seconds")


def scratch_dir() -> Path:
    """`~/.claude/codeforge-scratch/` — repo 밖 임시 산출물 유일 허용 위치 (ADR-169)."""
    return Path.home() / ".claude" / "codeforge-scratch"


def normalize_run_id(raw: Optional[str]) -> str:
    """run_id 정규화 — `[A-Za-z0-9-]` 외 문자는 `-` 로 치환, 16자 상한.

    상한 근거: provenance 문자열 `run_id=<id>` 가 emit deny-scan 의 20+ `[A-Za-z0-9+/=]` run 을
    형성하지 않게 하는 구조적 여유 (`_` 뒤 `id=` 3자 + 16자 = 19 < 20). 임의 길이 run_id 를
    허용하면 정상 산출물이 K-6 로 abort 되는 EC-11 재발.
    """
    default = datetime.datetime.now(KST).strftime("%Y%m%dT%H%M%S")
    if not raw:
        return default
    cleaned = re.sub(r"[^A-Za-z0-9-]", "-", str(raw)).strip("-")
    return (cleaned[:16] or default)


def provenance(method_endpoint: str, status: Any, run_id: str) -> str:
    """`[empirical-source: <KST ISO8601>, <method+endpoint>, <status>, tenant=redacted, run_id=…]`

    갱신은 **실 재측정 시에만** (합성 편집 금지 — §3.9).
    """
    return (f"[empirical-source: {kst_now_iso()}, {method_endpoint}, {status}, "
            f"tenant=redacted, run_id={run_id}]")


def digest_grouped(data: bytes) -> str:
    """sha256 → grouped-hex (T-11 digest 축 — `grouped_hex` validator 강제 경유).

    원문 64-hex 는 record 에 싣지 않는다 (deny-scan 20+ run 회피는 **부수 효과**이고, 1차 목적은
    "비밀 아님이 구성적으로 보장된 값만 변환" 규율 준수).
    """
    return grouped_hex(hashlib.sha256(data).hexdigest())


def redact_payload(value: Any) -> str:
    """golden 산출물의 payload 치환 표기 — `"<b64:len=N,sha8=xxxxxxxx>"` (원문 미수록, §3.9)."""
    encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
    return f"<b64:len={len(encoded)},sha8={hashlib.sha256(encoded).hexdigest()[:8]}>"


# ── 단일 emit choke-point (T-12 / §7.1 gate D) ──────────────────────────────

def emit_record(obj: Any) -> str:
    """stdout·NDJSON·golden-후보 **전 채널 공통** 최종 관문.

    단계 (§7.1 gate D):
      1. (필드 생성 시점 — 호출자 책임) digest 는 `digest_grouped`, body 는 `sanitize_body_field`
         를 이미 통과했어야 한다. 본 함수는 원시 64-hex·미가공 body 를 정상화하지 않는다.
      2. **조립 직후(pre-scrub) deny-scan — hit = K-6 abort**.
      3. `_scrub` — exact-value redaction(token·email·b64 파생형) 1순위 + 휴리스틱 backstop.
      4. 최종 전체 `_deny_scan_for_secrets` 재수행 (§7.1 step 4 문언 그대로 — 최종 방어선).

    **step 2 배치 근거 (구현 lane 관측 — 설계 §7.1 문언은 scrub→deny-scan 순서만 명시)**:
    `_scrub` 의 휴리스틱(`[A-Za-z0-9+/=]{20,}` → REDACT)은 deny-scan 의 탐지 패턴과 **동일
    문자클래스의 상위집합**이라, scrub 을 먼저 걸면 deny-scan 이 볼 20+ run 이 남지 않는다 →
    K-6 은 구조적으로 발화 불가(hollow gate)가 되고, 산출물에 원문 hash 를 주입해도 abort 대신
    `***REDACTED***` 로 **조용히 소실**된다. 이는 설계 자신의 discriminating 계약
    **D-10a("산출물 원문 hash 주입 → deny-scan RED")** 와 정면 충돌한다. 따라서 abort 판정은
    pre-scrub 텍스트로 하고(§3.9 의 grouped-hex·값 비기록 규율이 여기서 실제 의미를 가진다),
    §7.1 step 4 의 최종 재수행은 그대로 남긴다. body 축은 이미 필드 생성 시점에 drop 되므로
    (D-10b) 비신뢰 응답이 pre-scrub 판정을 오발동시키지 않는다.

    dict/list 는 JSON 직렬화, str 은 그대로 통과 (사람 가독 회계표도 동일 관문을 지나게).
    """
    if isinstance(obj, str):
        text = obj
    else:
        text = json.dumps(obj, ensure_ascii=False, indent=2)

    # step 2 — 조립 원문 판정 (K-6 primary). 검출 상세(=잠재 secret)는 로그·예외 메시지에
    # 싣지 않는다 (CodeQL clear-text logging 정합).
    ok, _err = _deny_scan_for_secrets(text)
    if not ok:
        raise EmitDenyScanAbort("emit deny-scan hit (조립 원문) — 산출물 방출 중단 (K-6, 상세 억제)")

    text = _scrub(text)

    # step 4 — 최종 방어선 재수행 (scrub 이 새 패턴을 만들지 않음을 확인).
    ok, _err = _deny_scan_for_secrets(text)
    if not ok:
        raise EmitDenyScanAbort("emit deny-scan hit (최종) — 산출물 방출 중단 (K-6, 상세 억제)")
    return text


# ── 순수 verdict 3종 (D4 — 관측 outcome ground-truth 만) ─────────────────────

def _tier(value: str) -> str:
    """반환 직전 기계 SSOT 대조 — TIER_ENUM 비소속 토큰은 즉시 AssertionError (fail-loud).

    enum 비소속 산문 수식어가 tier 값으로 새는 경로를 구조적으로 차단한다
    (원판 L341/350/361/375 결함의 재발 방지 — D-3).
    """
    if value not in TIER_ENUM:
        raise AssertionError(
            f"tier 토큰 {value!r} 은 기계 SSOT TIER_ENUM{TIER_ENUM} 비소속 — 유효 판정 불가"
        )
    return value


def verdict_storage_axis(scenarios: List[Dict[str, Any]]) -> str:
    """저장 축 (CFP-2829 AC-11 계보) — 전 시나리오가 write 성공 **∧** read-back byte-exact 일 때만 상향.

    입력: `[{"write_success": bool, "readback_byte_exact": bool}, ...]`
    반환: 시나리오 ≥1 ∧ 전건 양 True → `"normative"` / 그 외 전부 → `"declared"`.

    `is True` 엄격 비교 — 원판의 dict-truthy 판정(L230/L234: 결과 dict 가 있기만 하면 normative)
    재발 차단 (D-1).
    """
    if not isinstance(scenarios, list) or len(scenarios) == 0:
        return _tier("declared")
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            return _tier("declared")
        if scenario.get("write_success") is not True:
            return _tier("declared")
        if scenario.get("readback_byte_exact") is not True:
            return _tier("declared")
    return _tier("normative")


def verdict_over_limit_axis(observations: List[Dict[str, Any]]) -> str:
    """over-limit 축 (AC-12 계보) — **서버가 응답한** over-limit 분류 + 대조군 쌍 성립 시에만 상향.

    입력: `[{"origin": str, "http_status": int|None, "classified_as": str|None,
             "control_pair_ok": bool}, ...]`
    반환: `origin == "server-response"` ∧ `classified_as == "over-limit"` ∧ `control_pair_ok is True`
    인 관측 ≥1 → `"normative"` / 그 외 → `"declared"`.

    **`origin == "local-reject"` 는 어떤 조합에서도 normative 불가** — pre-flight 로컬 차단은
    서버 관측이 아니다 (ErrorInfo.origin 이 시그니처 층위에서 이를 분리한다, §4.2).
    """
    if not isinstance(observations, list):
        return _tier("declared")
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        if (obs.get("origin") == "server-response"
                and obs.get("classified_as") == "over-limit"
                and obs.get("control_pair_ok") is True):
            return _tier("normative")
    return _tier("declared")


def verdict_rate_axis(capture_records: List[Dict[str, Any]]) -> str:
    """rate 축 (AC-13a 계보) — 응답 헤더 캡처 레코드 존재 여부에만 결박.

    반환: 레코드 ≥1 → `"advisory"` (실측 도달 = 비-게이팅 관측축) / 0건 → `"declared"`.

    헤더 **존재 여부**는 외부 서버 소관이라 판정 입력이 아니다 (basic-auth 는 points model
    비적용이라 Beta-* 부재가 정상일 수 있음). 판정 입력 = "HTTP 응답을 실제로 받아 레코드를
    만들었는가" — 자사 코드 결정론 (AC-6a). 0건 = HTTP 0회 = 실측 미도달 (D-2).
    """
    if isinstance(capture_records, list) and len(capture_records) >= 1:
        return _tier("advisory")
    return _tier("declared")


# ── 결정론 fixture (결정 16 — timestamp 0) ──────────────────────────────────

_W1_LINE = "CFP-2889 정본 블롭 결정론 fixture — 한글 포함 무결성 검증 라인\n"


def build_w1_fixture() -> bytes:
    """W1 round-trip fixture — 결정론(한글 포함, raw > 32768B → chunk 2개).

    `time.time()`·timestamp·난수 0 — byte-exact 정의역은 **동일 실행 내 store→load** 이며
    (I-3 / 결정 16), 재실행 교차 sha256 대조는 계약이 아니다. 그럼에도 결정론으로 두는 이유는
    회계표(plan)와 실행(live)이 **동일 chunk_count** 를 산출해야 승인 대상 회계가 ground-truth
    이기 때문이다.
    """
    parts: List[bytes] = []
    total = 0
    index = 0
    while total <= 32768:
        encoded = f"{index:05d} {_W1_LINE}".encode("utf-8")
        parts.append(encoded)
        total += len(encoded)
        index += 1
    fixture = b"".join(parts)
    if len(fixture) <= 32768:
        raise AssertionError("build_w1_fixture: raw > 32768B 불변식 위반")
    return fixture


def build_boundary_payload(target_json_encoded_bytes: int) -> str:
    """`json.dumps(v, ensure_ascii=False).encode()` 길이가 **정확히** target 인 ASCII 문자열.

    ASCII 영숫자만 쓰면 JSON escape 가 발생하지 않으므로 인코딩 길이 = len(s) + 2 (양끝 quote).
    32767 / 32769 2-point probe (W2) 용. self-assert 포함 (산출 실패 = 즉시 예외).
    """
    if not isinstance(target_json_encoded_bytes, int) or target_json_encoded_bytes < 3:
        raise ValueError("target_json_encoded_bytes 는 3 이상 정수여야 한다 (quote 2B + 최소 1자)")
    payload = "a" * (target_json_encoded_bytes - 2)
    actual = json_encoded_size(payload)
    if actual != target_json_encoded_bytes:
        raise AssertionError(
            f"build_boundary_payload self-assert 실패 — 기대 {target_json_encoded_bytes}, 실제 {actual}"
        )
    return payload


_W3_KOREAN_FIXTURE = (
    "한글 인코딩 lever 측정 fixture — ensure_ascii False/True 델타 관측용. "
    "ASCII-only 는 델타 정의상 0 이라 부적격(AC-4). 결정론 고정 문자열, timestamp 0."
)


def build_w3_fixture() -> str:
    """W3 인코딩 lever fixture — 비-ASCII(한글) 필수 (ASCII-only 는 delta 0 이라 부적격)."""
    return _W3_KOREAN_FIXTURE


# ── K-5: page 신원 기계 게이트 ──────────────────────────────────────────────

_IA_PAGE_ID_RE = re.compile(r"page_id:\s*[\"']?(\d+)")
_IA_ROOT_ID_RE = re.compile(r"root_homepage_id:\s*[\"']?(\d+)")


class PageIdentityGate:
    """운영 mirror page 오기입(T-8) 기계 3중 차단 — deny-set / sentinel / fail-closed.

    deny-set = `docs/confluence-ia-tree.yaml` **runtime 파싱**으로 얻은 전 `page_id` 값 집합
    (+ `root_homepage_id`). **건수 박제 금지** — 파일이 커지든 줄든 게이트는 값 집합으로만 판정한다.
    PyYAML 이 있으면 구조 파싱, `ImportError` 면 regex fallback (어느 쪽이든 동일 값 집합 목표).
    """

    def __init__(self, ia_tree_path: Optional[Path] = None):
        self.ia_tree_path = ia_tree_path or (_SCRIPTS_DIR.parent / "docs" / "confluence-ia-tree.yaml")
        self.deny_ids, self.parse_mode = self._load_deny_ids(self.ia_tree_path)

    @staticmethod
    def _collect_ids_from_yaml(node: Any, out: set) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("page_id", "root_homepage_id") and isinstance(value, (str, int)):
                    out.add(str(value).strip())
                else:
                    PageIdentityGate._collect_ids_from_yaml(value, out)
        elif isinstance(node, list):
            for item in node:
                PageIdentityGate._collect_ids_from_yaml(item, out)

    @classmethod
    def _load_deny_ids(cls, path: Path) -> Tuple[set, str]:
        if not path.exists():
            raise PageIdentityAbort(
                f"page 신원 게이트 원천 부재 — ia-tree yaml 을 읽을 수 없어 fail-closed abort (K-5)"
            )
        text = path.read_text(encoding="utf-8")
        ids: set = set()
        mode = "regex-fallback"
        try:
            import yaml  # noqa: PLC0415 — 선택 의존 (부재 시 regex fallback)
            parsed = yaml.safe_load(text)
            cls._collect_ids_from_yaml(parsed, ids)
            mode = "pyyaml"
        except ImportError:
            pass
        except Exception:
            # 구조 파싱 실패(문법 오류 등) 도 regex fallback 으로 계속 — 단 mode 를 정직 표기.
            ids = set()
            mode = "regex-fallback-after-yaml-error"
        if mode.startswith("regex"):
            ids.update(_IA_PAGE_ID_RE.findall(text))
            ids.update(_IA_ROOT_ID_RE.findall(text))
        if not ids:
            raise PageIdentityAbort("ia-tree 에서 page id 를 하나도 파싱하지 못함 — fail-closed (K-5)")
        return ids, mode

    def verify(self, page_id: str, client, dry: bool) -> Dict[str, Any]:
        """deny-set 대조 + sentinel 양성 확인. 판정 결과 dict 반환 (abort 결정은 호출자 몫).

        결과: `{ok, deny_hit, sentinel_ok, title_verbatim, reason, deny_set_size, parse_mode}`
        — GET 실패·파싱 실패는 `ok=False` (fail-closed. "확인 못 함" ≠ "안전함").
        """
        result: Dict[str, Any] = {
            "ok": False,
            "deny_hit": False,
            "sentinel_ok": False,
            "title_verbatim": None,
            "reason": "",
            "deny_set_size": len(self.deny_ids),
            "parse_mode": self.parse_mode,
        }
        target = str(page_id).strip()
        if target in self.deny_ids:
            result["deny_hit"] = True
            result["reason"] = "대상 page id 가 ia-tree deny-set 소속 (운영 mirror page) — abort"
            return result

        try:
            if getattr(client, "accounting", None) is not None:
                client.accounting.record_get()
            resp = client._perform_request("GET", f"/wiki/api/v2/pages/{target}", dry=dry)
        except KillSwitchAbort:                      # F5 — kill-switch 를 K-5 로 오분류하지 않는다
            # **도달 경로 정직 기재 (firsthand 실측 2026-08-07)**: 401→`AuthAbortError` 승격은
            # `_send_write` 내부 한정이라 이 GET(`_perform_request` 직접 호출)에서 401 은 예외가
            # 아니라 status 로 돌아온다(비-200 분기가 처리) → 본 선행절은 401 축이 아니라 dry 경로
            # `GoldenFixtureMissingError` 등 kill-switch 계열이 "page 신원 GET 실패(K-5)" 로
            # 재분류되는 것을 막는다. F5 형식 invariant(중간 except 는 base 로만 재-raise) 준수.
            raise
        except Exception as e:                       # noqa: BLE001
            result["reason"] = f"page 신원 GET 실패 ({type(e).__name__}) — fail-closed"
            return result

        status = getattr(resp, "status_code", None)
        if status != 200:
            result["reason"] = f"page 신원 GET 비-200 (HTTP {status}) — fail-closed"
            return result
        try:
            body = resp.json()
            title = body.get("title") if isinstance(body, dict) else None
        except Exception:                            # noqa: BLE001
            result["reason"] = "page 신원 응답 파싱 실패 — fail-closed"
            return result
        if not isinstance(title, str):
            result["reason"] = "page 신원 응답에 title 부재 — fail-closed"
            return result

        safe_title, _omitted, _length = sanitize_body_field(title)
        result["title_verbatim"] = safe_title
        if PAGE_SENTINEL_PREFIX not in title:
            result["reason"] = (f"title 에 양성 sentinel `{PAGE_SENTINEL_PREFIX}` 부재 "
                                f"— throwaway page 확증 불가, fail-closed")
            return result

        result["sentinel_ok"] = True
        result["ok"] = True
        result["reason"] = "deny-set 미소속 ∧ 양성 sentinel 확인"
        return result


# ── RunContext (회계 · write-ahead registry · 10-event NDJSON) ───────────────

class RunContext:
    """run 1회 수명의 상태 소유자 — WriteAccounting·orphan registry·이벤트 NDJSON.

    write-ahead 보장: `WriteAccounting.on_write_attempt` 훅이 **HTTP 시도 이전**에 호출되므로
    `write_intent` 이벤트와 orphan 등록이 전송보다 먼저 영속화된다 (§7.4.1 상태 C 구조적 차단).
    """

    def __init__(self, run_id: str, cap: int = WRITE_CAP, events_path: Optional[Path] = None):
        self.run_id = run_id
        self.accounting = WriteAccounting(cap=cap)
        self.accounting.on_write_attempt = self._on_write_attempt
        self.orphans: Dict[str, Dict[str, Any]] = {}
        self.consecutive_failures = 0
        self.events_path = events_path or (scratch_dir() / f"cfp2889-run-{run_id}.ndjson")
        self.emitted_events = 0
        # 신호 전파 (§7.4, 보안 FIX iter2 N1) — 회수 경로가 흡수한 첫 kill-switch **예외 객체**.
        # `results` 가 아니라 ctx 에 두는 이유: results 는 `emit_record` 로 직렬화되므로 예외
        # 객체를 실을 수 없고, 반환 dict 에 실었다가 호출부가 pop 하는 형태는 "차단이 계약이
        # 아니라 한 줄의 우연" 이 되어 NEW-1 과 같은 함정을 재생산한다.
        self.cleanup_kill_switch: Optional[BaseException] = None
        self._ensure_events_dir()

    def _ensure_events_dir(self) -> None:
        self.events_path.parent.mkdir(parents=True, exist_ok=True)

    # ── 이벤트 ──

    def emit_event(self, event_type: str, **fields: Any) -> Dict[str, Any]:
        """10-event enum 검증 후 emit choke-point 경유 NDJSON append."""
        if event_type not in EVENT_TYPES:
            raise ValueError(f"미등록 event type {event_type!r} — 허용 집합 {EVENT_TYPES}")
        record: Dict[str, Any] = {"run_id": self.run_id, "ts_kst": kst_now_iso(), "event": event_type}
        record.update(fields)
        line = emit_record(record)
        with open(self.events_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line.replace("\n", " ") + "\n")
        self.emitted_events += 1
        return record

    def emit_abort(self, exc: BaseException) -> None:
        """abort 이벤트 — 사유 + kill-switch id + 직전 성공 write + **orphan registry 전량**.

        orphan snapshot 을 abort 이벤트 자체에 싣는 이유: scratch TTL(ADR-169) 이 registry 를
        purge 해도 회수 목록이 영속되게 하기 위함 (§3.9 abort 경로 영속화).
        """
        payload = {
            "kill_switch": kill_switch_id(exc),
            "reason": f"{type(exc).__name__}: {exc}",
            "last_successful_write": self.accounting.write_log[-1] if self.accounting.write_log else None,
            "accounting": self.accounting.snapshot(),
            "orphan_registry": self.orphan_snapshot(),
        }
        try:
            self.emit_event("abort", **payload)
        except EmitDenyScanAbort:
            # abort 기록 자체가 deny-scan 에 걸리는 경우 — 정적 최소 레코드로 강등 (기록 누락 금지).
            minimal = {"run_id": self.run_id, "ts_kst": kst_now_iso(), "event": "abort",
                       "kill_switch": "K-6", "reason": "emit deny-scan (상세 억제)",
                       "orphan_count": len(self.orphans)}
            with open(self.events_path, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(minimal, ensure_ascii=False) + "\n")

    # ── write-ahead 훅 ──

    def _on_write_attempt(self, intent: Dict[str, Any]) -> None:
        key = intent.get("key")
        if key:
            self.register_orphan(str(key))
        self.emit_event(
            "write_intent",
            key=key,
            label=intent.get("label"),
            method=intent.get("method"),
            attempt_no=intent.get("attempt_no"),
            api_version=intent.get("api_version", 2),
            page_id=intent.get("page_id"),
        )
        self._test_pause()

    @staticmethod
    def _test_pause() -> None:
        """**test-only seam** — `CFP2889_TEST_PAUSE_AFTER_INTENT` 초 만큼 지연.

        §8.5.2 subprocess fork-and-kill 테스트가 "intent 기록됨 ∧ result 미기록" 상태를
        결정적으로 포착하기 위한 **지연 전용** 장치다. 동작 변경 0 (분기·상태 전이 없음),
        기본값 0 (미설정 = no-op). dark-path 아님 — 켜도 관측 대상 거동은 동일하다.
        """
        raw = os.environ.get(TEST_PAUSE_ENV, "")
        if not raw:
            return
        try:
            seconds = float(raw)
        except ValueError:
            return
        if seconds > 0:
            time.sleep(seconds)

    def record_write_outcome(self, ok: bool, *, label: str = "",
                             probe_pair_id: Optional[str] = None,
                             http_status: Optional[int] = None) -> None:
        """write 결과 기록 + K-3 연속 실패 감시.

        `probe_pair_id` 가 있는 호출(= 기대-400 probe)은 **연속 실패 카운터에서 제외**한다 —
        의도된 실패를 kill-switch 로 오인하면 AC-5 측정 자체가 불가능해진다 (오라클 분리).
        """
        self.emit_event("write_result", ok=bool(ok), label=label,
                        probe_pair_id=probe_pair_id, http_status=http_status)
        if probe_pair_id is not None:
            return
        if ok:
            self.consecutive_failures = 0
            return
        self.consecutive_failures += 1
        if self.consecutive_failures >= CONSECUTIVE_FAILURE_ABORT:
            raise ConsecutiveWriteFailure(
                f"연속 write 실패 {self.consecutive_failures} >= {CONSECUTIVE_FAILURE_ABORT} — K-3 abort"
            )

    # ── orphan registry ──

    def register_orphan(self, key: str, property_id: Any = None,
                        status: Optional[str] = None) -> None:
        entry = self.orphans.setdefault(
            key, {"key": key, "property_id": None, "status": "unknown"})
        if property_id is not None:
            entry["property_id"] = property_id
        if status is not None:
            entry["status"] = status

    def orphan_snapshot(self) -> List[Dict[str, Any]]:
        return [dict(entry) for entry in self.orphans.values()]

    def emit_cap_state(self, phase: str) -> None:
        self.emit_event("cap_state", phase=phase, **self.accounting.snapshot())


# ── plan 모드 회계 (순수 — ground-truth 재산출) ─────────────────────────────

def client_surface_evidence() -> Dict[str, Any]:
    """§13L.5 — 파괴 표면 부재 증명 (client 공개 메서드 열거 + page-destructive 부재 확인)."""
    surface = sorted(name for name in dir(MeasurementRESTClient) if not name.startswith("_"))
    destructive_patterns = ("delete_page", "deleteconfluencepage", "remove_page",
                            "archive_page", "trash_page", "purge_page")
    hits = [name for name in surface
            if any(pattern in name.lower() for pattern in destructive_patterns)]
    return {
        "public_methods": surface,
        "page_destructive_methods": hits,
        "invariant_ok": len(hits) == 0,
        "note": "page 생성·삭제는 MCP 전용 — 측정 코드에 page-destructive REST 표면 신설 금지 (§13L.3)",
    }


def plan_accounting(cap: int = WRITE_CAP) -> Dict[str, Any]:
    """실행 전 회계표 ground-truth 재산출 (순수 — HTTP 0회).

    W1 은 **실제 `build_w1_fixture()` 를 `chunk(…, effective_chunk_budget())` 로 chunk** 해
    chunk_count 를 산출한다 (설계 추계 승계 금지 — 승인 대상은 본 산출치다).
    """
    canonical = build_w1_fixture()
    chunk_dict = chunk(canonical, budget=effective_chunk_budget())
    manifest = chunk_dict[LOCAL_MANIFEST_KEY]
    chunk_count = manifest["chunk_count"]

    # wrap overhead 로컬 실측 (서버 관측 아님 — 정직 라벨): wrap 인코딩 − bare 인코딩 증분.
    sample_b64 = chunk_dict[local_chunk_key(0)]
    wrap_overhead_measured = (json_encoded_size({"data": sample_b64})
                              - json_encoded_size(sample_b64))

    scenarios = [
        {"id": "W1", "desc": "32KB multi-key chunk round-trip (chunk N + manifest)",
         "logical_writes": chunk_count + 1, "expected_deletes": chunk_count + 1},
        {"id": "W2", "desc": "measurement-basis 경계 2-point (32768±1, seam unbudgeted)",
         "logical_writes": 2, "expected_deletes": 2},
        {"id": "W3", "desc": "ensure_ascii 2-인코딩 probe (한글 fixture — utf8 / ascii)",
         "logical_writes": 2, "expected_deletes": 2},
        {"id": "W4", "desc": "v2 over-limit probe + 정상 대조군 (probe_pair_id 쌍)",
         "logical_writes": 2, "expected_deletes": 1},
        {"id": "W5", "desc": "v1 endpoint 1-call probe (재시도 0)",
         "logical_writes": 1, "expected_deletes": 0},
    ]
    logical_total = sum(s["logical_writes"] for s in scenarios)
    worst_case_attempts = min(logical_total * 2, cap)   # 최악 = write 당 429 재시도 1회 (cap clamp)
    expected_deletes = sum(s["expected_deletes"] for s in scenarios)

    return {
        "run_kind": "plan",
        "cap": cap,
        "scenarios": scenarios,
        "logical_write_total": logical_total,
        "worst_case_write_attempts": worst_case_attempts,
        "worst_case_note": "최악 = write 당 429-한정 재시도 1회 (×2), cap clamp 적용",
        "cap_headroom": cap - worst_case_attempts,
        "expected_delete_total": expected_deletes,
        "delete_soft_ceiling": DELETE_SOFT_CEILING,
        "budget_bytes": BUDGET_BYTES,
        "wrap_overhead_bytes_declared": WRAP_OVERHEAD_BYTES,
        "wrap_overhead_bytes_local_measured": wrap_overhead_measured,
        "effective_chunk_budget": effective_chunk_budget(),
        "w1_raw_bytes": len(canonical),
        "w1_chunk_count": chunk_count,
        "w1_total_sha256_grouped": grouped_hex(manifest["total_sha256"]),
        "client_surface": client_surface_evidence(),
    }


def render_plan_table(plan: Dict[str, Any]) -> str:
    """회계표 사람 가독 렌더 (승인 대상 표면)."""
    lines: List[str] = []
    lines.append("-" * 74)
    lines.append("CFP-2889 measurement plan (실 write 0 — 승인 전 사전 회계표)")
    lines.append("-" * 74)
    lines.append(f"self-cap                 : {plan['cap']} (POST·PUT HTTP 시도 합산, retry 포함)")
    lines.append(f"논리 write 합             : {plan['logical_write_total']}")
    lines.append(f"최악 write 시도 (429 재시도): {plan['worst_case_write_attempts']} "
                 f"(cap 여유 {plan['cap_headroom']})")
    lines.append(f"예상 DELETE (cap 밖)      : {plan['expected_delete_total']} "
                 f"(soft-ceiling {plan['delete_soft_ceiling']})")
    lines.append(f"BUDGET_BYTES             : {plan['budget_bytes']}")
    lines.append(f"WRAP_OVERHEAD_BYTES      : 선언 {plan['wrap_overhead_bytes_declared']} / "
                 f"로컬 실측 {plan['wrap_overhead_bytes_local_measured']}")
    lines.append(f"유효 chunk 예산           : {plan['effective_chunk_budget']}")
    lines.append(f"W1 fixture               : raw {plan['w1_raw_bytes']}B → "
                 f"chunk {plan['w1_chunk_count']}개 (+manifest 1)")
    lines.append("-" * 74)
    lines.append(f"{'시나리오':<6}{'논리 write':>10}{'예상 DELETE':>12}  설명")
    for scenario in plan["scenarios"]:
        lines.append(f"{scenario['id']:<6}{scenario['logical_writes']:>10}"
                     f"{scenario['expected_deletes']:>12}  {scenario['desc']}")
    lines.append("-" * 74)
    surface = plan["client_surface"]
    lines.append(f"파괴 표면 부재 증명 (§13L.5): page-destructive 메서드 "
                 f"{len(surface['page_destructive_methods'])}건 / 공개 메서드 "
                 f"{len(surface['public_methods'])}건 → invariant "
                 f"{'OK' if surface['invariant_ok'] else 'VIOLATED'}")
    identity = plan.get("page_identity") or {}
    lines.append(f"page 신원 확인            : {identity.get('summary', '미확인 — creds/page-id 부재')}")
    lines.append(f"환경 게이트               : {plan.get('gate_summary', '')}")
    lines.append("-" * 74)
    lines.append("live 실행 조건 4-AND: --confirm-live-write ∧ creds ∧ CFP2829_TEST_PAGE_ID "
                 "∧ ¬CFP2829_MEASURE_SKIP_WRITE")
    return "\n".join(lines)


# ── creds / env preflight ───────────────────────────────────────────────────

def default_creds_path() -> Path:
    return scratch_dir() / "atlassian-creds.env"


def creds_present() -> bool:
    return bool(os.environ.get("ATLASSIAN_API_TOKEN") and os.environ.get("ATLASSIAN_USER_EMAIL"))


def load_creds_from_file(creds_path: Optional[Path] = None) -> bool:
    """creds 파일 → process env (allowlist `ATLASSIAN_*` / `CFP2829_*` 만 — F-SEC-05 유지).

    신뢰 못할 파일이 임의 env(PATH·LD_PRELOAD 등)를 주입해 환경을 오염시키는 것을 차단한다.
    파일 경로·값은 어떤 산출물에도 기록하지 않는다 (§7.5 — creds 절대경로 비노출).
    """
    path = Path(creds_path) if creds_path is not None else default_creds_path()
    if not path.exists():
        logger.info("creds 파일 부재 — env 에 이미 주입돼 있지 않으면 write 불가")
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not (key.startswith("ATLASSIAN_") or key.startswith("CFP2829_")):
                    logger.debug("비-allowlist creds 키 무시 (allowlist: ATLASSIAN_*/CFP2829_*)")
                    continue
                os.environ[key] = value
        logger.info("creds 파일 로드 완료 (값·경로 미기록)")
        return True
    except Exception as e:                           # noqa: BLE001
        logger.error(f"creds 파일 로드 실패: {type(e).__name__}")
        return False


def creds_preflight(creds_file_found: bool) -> None:
    """K-7 — creds preflight. 파일 부재 사유에 ADR-169 TTL purge 가능성을 명시한다."""
    if creds_present():
        return
    raise CredsPreflightAbort(
        "creds preflight 실패 — ATLASSIAN_API_TOKEN/USER_EMAIL 부재 "
        f"(creds 파일 발견={creds_file_found}). scratch 상주 creds 파일은 ADR-169 TTL 자동 "
        "purge 정의역이라 사라졌을 수 있다 — 1Password 에서 재프로비저닝 후 재실행 (K-7). "
        "전역 BYPASS export 금지."
    )


def abort_with_ledger(exc: BaseException, run_id: str,
                      ctx: Optional["RunContext"] = None) -> int:
    """abort 원장 **1행** 을 보장한 뒤 exit code 1 을 돌려준다 (§3.10 — 원장 없는 종료 금지).

    preflight abort 는 `RunContext` 가 아직 없는 시점(진입점 초입·plan 모드)에 발화할 수 있다.
    그 경우 여기서 최소 context 를 만들어 **기존** `RunContext.emit_abort` 를 그대로 재사용한다
    — abort 기록 경로를 2벌 작성하면 한쪽만 갱신되는 드리프트가 생긴다 (재사용 선행, ADR-140).
    """
    context = ctx if ctx is not None else RunContext(run_id=run_id, cap=WRITE_CAP)
    context.emit_abort(exc)
    logger.error(f"abort — {kill_switch_id(exc)} / {type(exc).__name__} (원장 1행 기록)")
    return 1


def create_client_or_abort(base_url: str, token: Optional[str], email: Optional[str],
                           accounting: Optional[WriteAccounting] = None) -> MeasurementRESTClient:
    """측정 client 생성 — 생성자 L1 host pin 의 `ValueError` 를 **K-7 preflight abort 로 승격**.

    승격이 필요한 이유 (F1 조건 (a)/(b)): pin 집행 지점은 `ConfluencePropertyREST.__init__` 이고
    거기서 나오는 `ValueError` 는 `emit_abort` 결박 **밖**이다. 그대로 두면 "원장 미기록 종료" 가
    되어 §3.10("모든 abort = `abort` 이벤트 기록 후 exit≠0")을 위반한다. 승격 지점은 client 를
    만드는 **모든** 진입점(`main` live 경로 · `run_plan`)이며, 특히 plan 경로에서는 뒤따르는
    `PageIdentityGate.verify(dry=False)` 가 자격증명을 실은 실 HTTP GET 을 발사하므로 승격이
    그보다 앞서야 한다.

    사유 문자열에 `endpoint-preflight` 를 남겨 creds 축(K-7)과 원장에서 분별 가능하게 한다.
    """
    try:
        return create_measurement_client(base_url, token, email, accounting=accounting)
    except ValueError as e:
        raise CredsPreflightAbort(
            f"endpoint-preflight 실패 (base_url host pin·형식) — {e}. "
            f"{CONFLUENCE_BASE_URL_ENV} 를 정정한 뒤 재실행 (K-7 — 자격증명 오도착 차단, "
            f"HTTP 0회)"
        ) from e


def validate_page_id_or_abort(raw: str) -> str:
    """L1 층 대상 자원 id preflight — 위반 = **K-7 abort** (write 0회, run 미개시).

    처분이 L2 의 local-reject 가 아니라 abort 인 이유: 여기서 깨진 것은 호출 1건이 아니라
    **실행 전제**(측정 대상 page 지목) 그 자체다. "잘못된 page_id 로 run 을 시작하지 않는다" 가
    회수 불가 오염을 0 으로 만드는 유일한 처분이다.

    배치 순서 = **검증 → K-5 deny 대조 → sentinel**. 검증이 선행해야 deny-set 대조가 성립한다 —
    deny-set 대조는 canonical id 문자열 비교(`str(page_id).strip() in self.deny_ids`)이므로
    `1867943/../x` 는 대조를 통과하면서 실제 요청 경로는 `/pages/1867943/...` 로 수렴한다
    (= 운영 mirror page 지목). 정규화가 아니라 거부여야 하는 이유도 같다 (`validate_resource_id`).
    """
    try:
        return validate_resource_id(raw, field=TEST_PAGE_ID_ENV)
    except ValueError as e:
        raise CredsPreflightAbort(
            f"endpoint-preflight 실패 (resource-id 문법) — {e}. 대상 page id 를 정정한 뒤 "
            f"재실행 (K-7 — 잘못된 대상으로 run 을 시작하지 않는다, write 0회)"
        ) from e


# ── 측정 시나리오 (W1~W5) ───────────────────────────────────────────────────

def _measure_key(suffix: str) -> str:
    return f"{MEASURE_KEY_PREFIX}.{suffix}"


def scenario_w1(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
                dry: bool) -> Dict[str, Any]:
    """W1 — 32KB multi-key chunk round-trip (store → load → byte-exact 검증).

    read-back 은 `load_chunked_property` (manifest·per-chunk sha256 전수 검증 위임) 로 수행하며,
    그 위에 **원본 canonical 과의 byte 동일성**을 별도 확인한다 (검증 오라클 이중화).
    """
    canonical = build_w1_fixture()
    chunk_dict = chunk(canonical, budget=effective_chunk_budget())
    chunk_count = chunk_dict[LOCAL_MANIFEST_KEY]["chunk_count"]

    result: Dict[str, Any] = {
        "scenario": "W1",
        "raw_bytes": len(canonical),
        "chunk_count": chunk_count,
        "source_sha256_grouped": digest_grouped(canonical),
        "write_success": False,
        "readback_byte_exact": False,
        "error": None,
    }

    try:
        store = client.store_chunked_property(page_id, chunk_dict, dry_run=dry)
        result["write_success"] = store.get("success") is True
        result["stale_purged"] = store.get("stale_purged", [])
        ctx.record_write_outcome(result["write_success"], label="W1 store_chunked_property")
    except ChunkStoreError as e:
        result["error"] = f"ChunkStoreError: {e}"
        ctx.record_write_outcome(False, label="W1 store_chunked_property")
        return result

    for index in range(chunk_count):
        ctx.register_orphan(CHUNK_KEY_TEMPLATE.format(n=index), status="created")
    ctx.register_orphan(MANIFEST_KEY, status="created")

    try:
        restored = client.load_chunked_property(page_id, dry_run=dry)
    except ChunkStoreError as e:
        result["error"] = f"read-back 실패 — ChunkStoreError: {e}"
        return result

    result["readback_bytes"] = len(restored)
    result["readback_sha256_grouped"] = digest_grouped(restored)
    result["readback_byte_exact"] = (restored == canonical)
    return result


def scenario_w2(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
                dry: bool) -> Dict[str, Any]:
    """W2 — measurement-basis 경계 2-point (32768−1 / 32768+1), pre-flight bypass seam 경유.

    두 point 는 서로의 대조군이므로 공통 `probe_pair_id` 를 부여한다 (기대-실패 point 가
    K-3 연속 실패 카운터를 오염시키지 않게 — 오라클 분리).
    """
    pair_id = "w2-boundary"
    points: List[Dict[str, Any]] = []
    for target in (32767, 32769):
        key = _measure_key(f"boundary-{target}")
        payload = build_boundary_payload(target)
        ok, envelope, err = client.write_property_unbudgeted(
            page_id, key, payload, probe_pair_id=pair_id, dry=dry)
        status = (err or {}).get("http_status")
        ctx.record_write_outcome(ok, label=f"W2 {target}", probe_pair_id=pair_id,
                                 http_status=status)
        if ok and isinstance(envelope, dict):
            ctx.register_orphan(key, property_id=envelope.get("id"), status="created")
        points.append({
            "json_encoded_bytes": target,
            "key": key,
            "write_success": ok,
            "http_status": status,
            "origin": (err or {}).get("origin"),
            "classified_as": (err or {}).get("classified_as"),
            "body_verbatim": (err or {}).get("body_verbatim"),
            "body_omitted_by_deny_scan": (err or {}).get("body_omitted_by_deny_scan"),
            "body_length": (err or {}).get("body_length"),
        })
    below, above = points[0], points[1]
    return {
        "scenario": "W2",
        "probe_pair_id": pair_id,
        "points": points,
        "boundary_discriminating": (below["write_success"] is True
                                    and above["write_success"] is False),
        "note": "below 성공 ∧ above 실패 일 때만 32768 경계가 관측으로 확정된다",
    }


def scenario_w3(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
                dry: bool) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """W3 — ensure_ascii lever 2-인코딩 probe (한글 fixture) + read-back 재정규화 관측.

    반환 = `(관측 dict, envelope_sample)` **2-tuple**. `envelope_sample`(서버 원본 envelope)은
    golden 빌더 전용이며 `results` 로 흘러가면 안 되므로 관측 dict 밖으로 분리한다 (NEW-1).
    """
    value = build_w3_fixture()
    utf8_bytes = len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
    ascii_bytes = len(json.dumps(value, ensure_ascii=True).encode("utf-8"))

    encodings: List[Dict[str, Any]] = []
    envelope_sample: Optional[Dict[str, Any]] = None
    for label, ascii_mode in (("utf8", False), ("ascii", True)):
        key = _measure_key(f"enc-{label}")
        ok, envelope, err = client.write_property_unbudgeted(
            page_id, key, value, ascii_mode=ascii_mode, dry=dry)
        ctx.record_write_outcome(ok, label=f"W3 {label}",
                                 http_status=(err or {}).get("http_status"))
        if ok and isinstance(envelope, dict):
            ctx.register_orphan(key, property_id=envelope.get("id"), status="created")
            if envelope_sample is None:
                envelope_sample = envelope

        readback_identical = None
        readback_value = None
        if ok:
            try:
                envs = client.list_properties_v2(page_id, key=key, dry=dry)
                if len(envs) == 1:
                    readback_value = _unwrap_property(envs[0])
                    readback_identical = (readback_value == value)
            except (PropertyResolveError, ChunkStoreError) as e:
                readback_identical = None
                readback_value = f"<read-back 실패: {type(e).__name__}>"

        encodings.append({
            "encoding": label,
            "ensure_ascii": ascii_mode,
            "key": key,
            "write_success": ok,
            "http_status": (err or {}).get("http_status"),
            "readback_identical_to_sent": readback_identical,
            "readback_sha256_grouped": (
                digest_grouped(json.dumps(readback_value, ensure_ascii=False).encode("utf-8"))
                if isinstance(readback_value, str) else None),
        })

    # NEW-1(iter2): `envelope_sample` 은 **반환 dict 에 싣지 않는다**. 이 값은 서버 원본
    # envelope(신원 필드 포함)이고 소비처는 golden 빌더 단 하나인데, 반환 dict 에 실으면
    # `results` 유입 차단이 호출부의 `pop` 한 줄에 걸린 **우연**이 된다 (그 줄이 사라지면
    # 즉시 stdout 유출). 별도 반환값으로 분리해 **구조적으로** 도달 불가하게 만든다.
    # "반환 시점 sanitize" 는 채택하지 않는다 — 빌더가 원문 골격을 요구하므로 이중 sanitize 가
    # §3.3 "1차 출처 = 실 capture" 추적을 흐린다.
    return {
        "scenario": "W3",
        "utf8_bytes": utf8_bytes,
        "ascii_bytes": ascii_bytes,
        "delta_bytes": ascii_bytes - utf8_bytes,
        "encodings": encodings,
        "note": "readback_identical_to_sent=False 는 서버 재정규화 관측 (G5)",
    }, envelope_sample


def scenario_w4(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
                dry: bool) -> Dict[str, Any]:
    """W4 — v2 over-limit probe + 정상 크기 대조군 (`probe_pair_id` 쌍, 오라클 분리).

    분류: 대조군 성공 ∧ probe over-limit → over-limit 확정 / 양쪽 실패 → malformed 재분류.
    """
    pair_id = "w4-overlimit"
    control_key = _measure_key("overlimit-control")
    probe_key = _measure_key("overlimit-probe")

    control_ok, control_env, control_err = client.write_property_unbudgeted(
        page_id, control_key, build_boundary_payload(1024), probe_pair_id=pair_id, dry=dry)
    ctx.record_write_outcome(control_ok, label="W4 control", probe_pair_id=pair_id,
                             http_status=(control_err or {}).get("http_status"))
    if control_ok and isinstance(control_env, dict):
        ctx.register_orphan(control_key, property_id=control_env.get("id"), status="created")

    over_payload = build_boundary_payload(33 * 1024)   # 33792B — 32768 초과 확보
    probe_ok, probe_env, probe_err = client.write_property_unbudgeted(
        page_id, probe_key, over_payload, probe_pair_id=pair_id, dry=dry)
    ctx.record_write_outcome(probe_ok, label="W4 probe", probe_pair_id=pair_id,
                             http_status=(probe_err or {}).get("http_status"))
    if probe_ok and isinstance(probe_env, dict):
        ctx.register_orphan(probe_key, property_id=probe_env.get("id"), status="created")

    err = probe_err or {}
    observation = {
        "origin": err.get("origin"),
        "http_status": err.get("http_status"),
        "classified_as": err.get("classified_as"),
        "control_pair_ok": control_ok is True,
        "probe_pair_id": pair_id,
    }
    if control_ok and err.get("classified_as") == "over-limit":
        adjudication = "over-limit 확정 (대조군 성공 ∧ probe over-limit 분류)"
    elif not control_ok and err.get("http_status") == 400:
        adjudication = "malformed 재분류 (대조군도 400 — over-limit 근거 불성립)"
    elif probe_ok:
        adjudication = "probe 가 성공함 — over-limit 관측 미성립 (한계 미도달 또는 서버 수용)"
    else:
        adjudication = "미확정 (대조군·probe 조합이 over-limit 판정 조건 미충족)"

    return {
        "scenario": "W4",
        "probe_pair_id": pair_id,
        "over_payload_json_encoded_bytes": 33 * 1024,
        "control": {"key": control_key, "write_success": control_ok,
                    "http_status": (control_err or {}).get("http_status")},
        "probe": {"key": probe_key, "write_success": probe_ok,
                  "http_status": err.get("http_status"),
                  "classified_as": err.get("classified_as"),
                  "origin": err.get("origin"),
                  "body_verbatim": err.get("body_verbatim"),
                  "body_omitted_by_deny_scan": err.get("body_omitted_by_deny_scan"),
                  "body_length": err.get("body_length")},
        "observation": observation,
        "adjudication": adjudication,
    }


def scenario_w5(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
                dry: bool) -> Dict[str, Any]:
    """W5 — v1 endpoint 1-call probe (413 / 410 / 그 외 — 어느 쪽이든 유효 관측)."""
    key = _measure_key("v1-probe")
    probe = client.probe_property_v1(page_id, key, build_boundary_payload(33 * 1024), dry=dry)
    ctx.record_write_outcome(probe.get("http_status") in (200, 201),
                             label="W5 v1 probe", probe_pair_id="w5-v1",
                             http_status=probe.get("http_status"))
    if probe.get("http_status") in (200, 201):
        ctx.register_orphan(key, status="created")
    interpretation = {
        "413-over-limit": "v1 현행 유지 + over-limit 413 확정",
        "410-gone": "v1 제거됨 — 재현-불가 종결 (정직 기록)",
    }.get(probe.get("classification"), "v1 현행 상태 미확정 — 관측 status 그대로 기록")
    return {"scenario": "W5", "probe": probe, "interpretation": interpretation}


# ── step R (reconcile) + cleanup ────────────────────────────────────────────

def enumerate_property_keys(client: MeasurementRESTClient, page_id: str,
                            dry: bool) -> Tuple[Optional[List[str]], bool, Optional[str]]:
    """no-filter 전량 열거 → (keys | None, partial, error). 실패 = None (reconcile_unknown 근거).

    kill-switch 는 삼키지 않는다 (F5): 본 함수의 광역 `except` 는 **실 K-1(401) 삼킴 지점**
    이었다 — 인증 실패가 여기서 흡수되면 401 신호가 소멸한 채 run 이 계속된다.
    """
    try:
        envs = client.list_properties_v2(page_id, dry=dry)
    except KillSwitchAbort:                          # F5 — kill-switch 단일 base 재-raise 선행절
        raise
    except Exception as e:                           # noqa: BLE001
        return None, False, type(e).__name__
    keys = sorted(str(env.get("key")) for env in envs if isinstance(env, dict))
    return keys, bool(getattr(client, "last_list_partial", False)), None


def cleanup_order(keys: List[str]) -> List[str]:
    """회수 순서 = **manifest 최우선** → chunk 역순 → 기타 (I-2).

    manifest 를 먼저 지우면 reader 가 즉시 fail-closed 로 회복된다 (store 의 manifest-last 와 대칭).
    """
    manifest = [k for k in keys if k == MANIFEST_KEY or k.endswith("__manifest")]
    chunk_prefix = f"{PROPERTY_KEY_PREFIX}.__chunk_"

    def chunk_index(key: str) -> int:
        suffix = key[len(chunk_prefix):]
        return int(suffix) if suffix.isdigit() else -1

    chunks = sorted([k for k in keys if k.startswith(chunk_prefix) and chunk_index(k) >= 0],
                    key=chunk_index, reverse=True)
    handled = set(manifest) | set(chunks)
    others = sorted(k for k in keys if k not in handled)
    return manifest + chunks + others


def cleanup_properties(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
                       dry: bool) -> Dict[str, Any]:
    """try/finally 로 결박되는 회수 루틴 — DELETE 는 cap 밖이라 K-2 이후에도 계속 수행된다.

    **광역 `except` 의 명시 예외 (F5 — "예외를 예외로 declare")**: 본 루프의 `except Exception`
    은 kill-switch 결박 규범(`except KillSwitchAbort: raise`)의 **의도된 예외로 존치**한다 —
    여기서 결박하면 첫 kill-switch 에 회수가 중단되어 §7.4.1 상태 B/C(회수 목록 미확보 = 운영
    page 에 orphan 잔존)가 재발한다. 예외를 예외로 명시하지 않으면 그 자체가 다음 번
    `declared-not-bound`(선언만 있고 결박은 없는 규범)이 되므로 여기 1줄로 declare 한다.

    단 **침묵 흡수는 금지**: 삼킨 예외가 kill-switch 계열이면 `cleanup_result` 에
    `kill_switch_id` 를 덧붙이고 `abort` 이벤트 1행을 원장에 남긴다 (중단은 하지 않는다 — 기록만).
    """
    outcome: Dict[str, Any] = {"attempted": 0, "deleted": 0, "failed": 0,
                               "kill_switch_ids": [], "details": []}
    for key in cleanup_order(list(ctx.orphans.keys())):
        entry = ctx.orphans.get(key, {})
        if entry.get("status") == "deleted":
            continue
        outcome["attempted"] += 1
        ctx.emit_event("cleanup_intent", key=key, property_id=entry.get("property_id"))
        property_id = entry.get("property_id")
        detail: Dict[str, Any] = {"key": key, "resolved": property_id is not None}
        try:
            if property_id is None:
                envs = client.list_properties_v2(page_id, key=key, dry=dry)
                if len(envs) == 0:
                    ctx.register_orphan(key, status="deleted")
                    detail["result"] = "부재 (이미 회수됨 또는 미생성)"
                    outcome["deleted"] += 1
                    outcome["details"].append(detail)
                    ctx.emit_event("cleanup_result", key=key, ok=True, note="absent")
                    continue
                property_id = envs[0].get("id")
                ctx.register_orphan(key, property_id=property_id)
            ok, err = client.remove_property_v2(page_id, property_id, dry=dry)
            if ok:
                ctx.register_orphan(key, status="deleted")
                outcome["deleted"] += 1
                detail["result"] = "deleted"
            else:
                ctx.register_orphan(key, status="unknown")
                outcome["failed"] += 1
                detail["result"] = f"실패 — {(err or {}).get('message') or (err or {}).get('http_status')}"
            ctx.emit_event("cleanup_result", key=key, ok=bool(ok),
                           property_id=property_id)
        except Exception as e:                       # noqa: BLE001 — 회수는 어떤 예외로도 멈추지 않는다
            # ↑ kill-switch 결박 규범의 **명시 예외** (docstring 참조). 흡수하되 침묵하지 않는다.
            ctx.register_orphan(key, status="unknown")
            outcome["failed"] += 1
            detail["result"] = f"예외 — {type(e).__name__}"
            swallowed_kill_switch = isinstance(e, KillSwitchAbort)
            if swallowed_kill_switch:
                detail["kill_switch_id"] = kill_switch_id(e)
                outcome["kill_switch_ids"].append(kill_switch_id(e))
                # 흡수는 *중단*의 예외이지 *결과 반영*의 예외가 아니다 (§7.4 신호 전파 정책).
                # 첫 예외 **객체**를 ctx 에 보존해 회수 완주 후 run_live 가 승격한다.
                if ctx.cleanup_kill_switch is None:
                    ctx.cleanup_kill_switch = e
            try:
                extra = ({"kill_switch_id": kill_switch_id(e)}
                         if swallowed_kill_switch else {})
                ctx.emit_event("cleanup_result", key=key, ok=False,
                               error=type(e).__name__, **extra)
            except Exception:                        # noqa: BLE001
                pass
            # ※ 여기서 `emit_abort` 를 호출하지 **않는다** (iter2 판정 (i)): 승격된 신호를
            #   run_live 가 최종 1행으로 남기므로 여기서도 남기면 **원장 abort 2행**이 된다.
            #   흡수 사실 자체는 위 `cleanup_result` 의 `kill_switch_id` 로 원장에 보존되므로
            #   신호 손실은 0 이다.
        outcome["details"].append(detail)
    return outcome


def reconcile(baseline: Optional[List[str]], actual: Optional[List[str]],
              baseline_partial: bool, actual_partial: bool) -> Dict[str, Any]:
    """step R 불변식 — `S_actual ∖ S_baseline == ∅` + **부분 열거 신호 결박** (F4).

    4 인자 전부 **positional 필수** 다 (default 금지). default 를 두면 partial 을 전달하지 않는
    기존 호출부가 조용히 통과해 누락이 드러나지 않는다 — 호출부를 강제로 깨뜨리는 것이 목적이다.

    status 4종:
      - `reconcile_unknown` — 열거 **실패**(None). 아무것도 세지 못했다.
      - `reconcile_partial` — 부분 열거(`baseline_partial ∨ actual_partial`) ∧ 잔여 ∅.
        `reconcile_unknown` 과 **다른 상태**다: "확인 못 함" ≠ "일부만 확인". 두 상태를 한 토큰에
        뭉개면 운영자가 재시도(열거 실패)와 범위 확대(부분 열거)를 구별할 수 없다.
      - `DRIFT` — 잔여 ≠ ∅. **부분 열거보다 우선한다** — 부분 열거로 *이미 관측된* 잔여는 확정
        사실이고, 더 셌다면 잔여가 늘 뿐이라 부분성이 그 사실을 약화시키지 않는다.
      - `RECONCILED` — 전량 열거 ∧ 잔여 ∅ (유일하게 "깨끗함" 을 단정할 수 있는 상태).
    """
    flags = {"baseline_partial": bool(baseline_partial),
             "actual_partial": bool(actual_partial)}
    if baseline is None or actual is None:
        return {"status": "reconcile_unknown", "residual": None, **flags,
                "note": "열거 실패 — 깨끗함을 단정할 수 없음 (fail-closed)"}
    residual = sorted(set(actual) - set(baseline))
    if residual:
        return {"status": "DRIFT", "residual": residual, **flags}
    if flags["baseline_partial"] or flags["actual_partial"]:
        return {"status": "reconcile_partial", "residual": [], **flags,
                "note": "부분 열거 — 관측 범위 안에서는 잔여 0 이나 전량 확인은 아님"}
    return {"status": "RECONCILED", "residual": [], **flags}


# ── captured-golden 후보 산출 (§3.9 — scratch 생성, repo 커밋은 operator 몫) ──

def write_golden_candidate(run_id: str, name: str, payload: Any) -> Path:
    path = scratch_dir() / f"cfp2889-{name}-{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(emit_record(payload) + "\n")
    return path


# ── golden 값-축 3분류 (F3 — §3.9 정밀화 · 결정 14 헤더 값 3분류의 envelope 축 동형 확장) ──
#
# **allowlist 는 경로 기준**이다 — bare key name 매칭은 중첩 깊이마다 재등장하는
# `key`/`number`/`id` 때문에 `results[*].version.number` 류를 의도치 않게 통과시킨다.
#
# **경로 표현 = typed segment 튜플** (보안 FIX iter2 N2). 구 구현은 경로를 `f"{path}.{key}"`
# 로 **문자열 연결**했는데, 그 표현은 키 내용에 대해 **injective 하지 않다**: 서버가 리터럴
# dotted key(`{"version.number": ...}`)를 돌려주면 경로 문자열이 `version.number` 와 충돌해
# 미지 필드가 value-allow 로 **verbatim 복사**된다 (실증: account-id 형 값 원문 누출).
# 튜플은 세그먼트 경계가 값이 아니라 **구조**로 표현되므로 키에 `.`·`[` 가 있어도 충돌 0 이다.
# 문자열 이스케이프는 채택하지 않는다 — "이스케이프가 injective 함" 이라는 증명 부담을 새로
# 만드는, 같은 클래스의 함정이다.

class _ListIndex:
    """list 원소 세그먼트 sentinel — dict 키(항상 `str`)와 **타입으로** 분별된다."""

    __slots__ = ()

    def __repr__(self) -> str:                       # pragma: no cover - 진단 표기용
        return "[*]"


LIST_INDEX = _ListIndex()

#: (i) value-allow — verbatim 보존 (단건 envelope golden 기준 typed 경로).
SHAPE_GOLDEN_VALUE_ALLOW = (
    # `id` 등재 근거 3: ① 실측 id 가 `[0-9]{1,32}` 라 §4.1 문법 계약을 자연 충족한다
    # (placeholder 로 지우면 그 golden 을 replay 하는 mock 이 공급하는 `property_id` 가 문법
    # 계약을 통과하지 못한다) ② §7.5 가 page/property id 를 Internal(기록 허용)로 분류한다
    # ③ §4.2 정정 註 ①("id 는 int 가 아니라 숫자 문자열")의 실측 근거가 바로 이 golden 이라
    # 지우면 그 註의 근거가 소멸한다.
    ("id",),
    ("key",),
    ("version", "number"),
    ("empirical_source",),               # wrapper 자기저작 (측정 harness 산출)
    ("endpoint_omitted_by_validator",),  # wrapper 자기저작
)

#: list golden — `results[*]` 하위에 동일 규칙 + wrapper 자기저작 필드(root).
LIST_GOLDEN_VALUE_ALLOW = (
    ("results", LIST_INDEX, "id"),
    ("results", LIST_INDEX, "key"),
    ("results", LIST_INDEX, "version", "number"),
    ("empirical_source",),
    ("endpoint_omitted_by_validator",),
)

#: (ii) payload 축 — b64 digest 치환 (`redact_payload` 재사용, 무변경).
SHAPE_GOLDEN_PAYLOAD_PATHS = (("value",),)
LIST_GOLDEN_PAYLOAD_PATHS = ((("results", LIST_INDEX, "value")),)

#: (iii) 타입 placeholder — bool 을 int 보다 먼저 검사한다 (`isinstance(True, int)` 는 True).
_TYPE_PLACEHOLDERS = ((bool, "<bool>"), (int, "<int>"), (float, "<float>"), (str, "<str>"))


def _type_placeholder(value: Any) -> str:
    """값 → 타입만 남긴 placeholder 토큰 (원문 미수록)."""
    if value is None:
        return "<null>"
    for py_type, token in _TYPE_PLACEHOLDERS:
        if isinstance(value, py_type):
            return token
    return "<unknown>"


def sanitize_golden_values(node: Any, *, value_allow: Tuple[Tuple[Any, ...], ...],
                           payload_paths: Tuple[Tuple[Any, ...], ...],
                           path: Tuple[Any, ...] = ()) -> Any:
    """golden 값-축 3분류 — 키·중첩 구조·타입은 **전수 보존**, 값만 처분한다 (F3).

    분류 (§3.9 정밀화 = 결정 14 헤더 값 3분류의 envelope 축 동형):
      (i)   `value_allow` 경로(typed segment 튜플) 소속 → **verbatim**
      (ii)  payload 축(`value`) → `redact_payload` b64 digest 치환 (기존 정책 무변경)
      (iii) **그 외 전부 + 미지 필드** → 타입 placeholder (`<str>`/`<int>`/`<bool>`/… 원문 미수록)

    필드를 **drop 하지 않는** 이유: 미지 필드의 *존재·타입 자체* 가 shape 발견의 측정 가치다
    (서버가 무엇을 돌려주는가). 그래서 처분은 삭제가 아니라 값 치환이다.

    (iii) 이 default 라는 점이 **fail-closed** 다 — 열거되지 않은 신규 서버 필드는 정의상 이
    분기로 떨어진다. `version.authorId`·`createdAt`·`message`·`minorEdit` 과 `_links.base`
    (tenant 호스트)가 여기서 막힌다. 구 구현은 `json.loads(json.dumps(...))` deep-copy 뒤
    `value`·`key` 만 치환해 **미지 필드를 무제한 통과**시켰고, 그 결과 커밋된 golden 2파일에
    서버 유래 `authorId` 가 유입됐다 (repo PUBLIC).

    **정직 한계 (over-claim 금지)**: 이 클래스의 유출은 emit 파이프라인 step 2/4 deny-scan 이
    잡지 못한다 — account-id 형(`<digits>:<uuid>`)은 `:`·`-` 로 분절돼 20+ `[A-Za-z0-9+/=]` run 을 형성하지
    않아 원경로를 그대로 통과한다 (보안테스트 실측). 즉 **본 allowlist 가 이 축의 유일 차단층**
    이고 deny-scan 은 이 축의 backstop 이 **아니다**. 반대로 "allowlist 로 완전 차단" 도 아니다 —
    value-allow 에 사람이 민감 필드를 등재하면 그대로 통과하는 사람-경로 잔여가 존치한다.

    적용 계층 = §7.1 emit 파이프라인 **step 1(필드 생성 시점) per-field 처리** — digest
    grouped-hex 변환·body truncate/scrub/drop 과 동일 단계의 **세 번째 disjoint per-field 규칙**
    이다. step 2-4(record 조립 후 deny-scan abort/scrub/backstop)는 무손상.
    """
    if path in payload_paths:
        return redact_payload(node)
    if path in value_allow:
        return copy.deepcopy(node)                    # verbatim (참조 공유 회피)
    if isinstance(node, dict):
        # 경로는 **튜플 append** 로 누적한다 — 키 문자열을 구분자로 잇지 않으므로 키가
        # `.` 을 포함해도 상위 경로와 충돌하지 않는다 (N2).
        return {key: sanitize_golden_values(
                    value, value_allow=value_allow, payload_paths=payload_paths,
                    path=path + (str(key),))
                for key, value in node.items()}
    if isinstance(node, list):
        child = path + (LIST_INDEX,)
        return [sanitize_golden_values(item, value_allow=value_allow,
                                       payload_paths=payload_paths, path=child)
                for item in node]
    return _type_placeholder(node)


def build_shape_golden(envelope: Dict[str, Any], run_id: str, page_id: str,
                       status: Any) -> Dict[str, Any]:
    """단건 PropertyEnvelope shape golden — 골격(키·중첩·타입) 보존 + **값-축 3분류** 처분.

    provenance endpoint 는 **실제 자사 템플릿 경로**로 재구성한다 (`safe_path` validator 통과 —
    `<id>` 류 플레이스홀더 문자열은 화이트리스트 불일치라 변환 거부 대상이다).

    **갱신 트리거 정정 (§3.9 정밀화 — FIX iter1 F3)**: 기captured golden 의 갱신 트리거는
    ① 실 재측정 **또는** ② 값-축 sanitize 규칙의 소급 적용이다. ②는 "합성 편집 금지"(= 측정치
    변조 금지, anti-fabrication 축) 위반이 **아니다** — 허용 조건은 **키·중첩·타입·수치 불변**
    이며, 소급 적용 시 치환한 필드명 목록을 병기할 의무가 따른다. 구 주석의 "기captured golden 은
    무편집 — 갱신은 실 재측정 시에만" 문언은 이 정밀화로 정정된다.
    """
    golden = sanitize_golden_values(envelope, value_allow=SHAPE_GOLDEN_VALUE_ALLOW,
                                    payload_paths=SHAPE_GOLDEN_PAYLOAD_PATHS)
    property_id = envelope.get("id")
    path = f"/wiki/api/v2/pages/{page_id}/properties"
    if property_id is not None:
        path = f"{path}/{property_id}"
    endpoint, omitted = safe_path_or_drop(path)
    # FIX iter1 F-CR-03: list golden(`GET {endpoint}`)과 대칭 — method 프리픽스 명기.
    # (갱신 트리거 = 실 재측정 **또는** 값-축 sanitize 규칙의 소급 적용 — docstring §3.9 정밀화.)
    golden["empirical_source"] = provenance(f"PUT {endpoint}" if endpoint
                                            else "PUT v2 property (endpoint 표기 drop)",
                                            status, run_id)
    golden["endpoint_omitted_by_validator"] = omitted
    return golden


def build_list_golden(body: Dict[str, Any], run_id: str, endpoint: str,
                      status: Any) -> Dict[str, Any]:
    """list 응답 wrapper golden — `results` 골격 1건 + **값-축 3분류** 처분 (pagination 필드 보존).

    `sanitize_golden_values` 공유 (shape 빌더와 같은 헬퍼 1개 — allowlist 로직 복붙 0). 두 빌더의
    차이는 dotted path prefix(`results[*].`) 뿐이다.

    `_links.base`(= tenant 호스트 `https://…atlassian.net/wiki`)는 value-allow 비소속이라
    (iii) 타입 placeholder 로 떨어진다 — provenance 의 `tenant=redacted` 규약과 list golden
    실물 사이의 **기존 자기모순**도 여기서 함께 해소된다.
    """
    golden = sanitize_golden_values(body, value_allow=LIST_GOLDEN_VALUE_ALLOW,
                                    payload_paths=LIST_GOLDEN_PAYLOAD_PATHS)
    results = golden.get("results") if isinstance(golden, dict) else None
    if isinstance(results, list) and results:
        skeleton = results[0]
        # `key` 는 value-allow(verbatim)라 wrapper 자기저작 값으로 덮어써도 규칙 충돌이 없다.
        if isinstance(skeleton, dict) and "key" in skeleton:
            skeleton["key"] = f"{MEASURE_KEY_PREFIX}.golden-skeleton"
        golden["results"] = [skeleton]
    else:
        golden["results"] = []
    golden["empirical_source"] = provenance(endpoint, status, run_id)
    return golden


def capture_list_golden(client: MeasurementRESTClient, page_id: str, run_id: str,
                        dry: bool) -> Optional[Dict[str, Any]]:
    """step R 열거 wrapper 원형 캡처 (GET 1회 — cap 밖). 실패 시 None (정직 미기록)."""
    path = f"/wiki/api/v2/pages/{page_id}/properties"
    try:
        if client.accounting is not None:
            client.accounting.record_get()
        resp = client._perform_request("GET", path, dry=dry)
        if getattr(resp, "status_code", None) != 200:
            return None
        body = resp.json()
    except KillSwitchAbort:                          # F5 — kill-switch 는 "미캡처" 로 삼키지 않는다
        raise
    except Exception:                                # noqa: BLE001
        return None
    if not isinstance(body, dict):
        return None
    endpoint, _omitted = safe_path_or_drop(path)
    return build_list_golden(body, run_id, f"GET {endpoint or 'v2 properties list'}", 200)


# ── live run ────────────────────────────────────────────────────────────────

def run_live(client: MeasurementRESTClient, ctx: RunContext, page_id: str,
             selected: Dict[str, bool]) -> Tuple[int, Dict[str, Any]]:
    """live 측정 실행 — kill-switch 7종 + try/finally cleanup + step R.

    반환: (exit_code, results)
    """
    dry = False
    results: Dict[str, Any] = {"run_kind": "live", "run_id": ctx.run_id,
                               "scenarios": {}, "events_path_name": ctx.events_path.name}
    storage_scenarios: List[Dict[str, Any]] = []
    over_limit_observations: List[Dict[str, Any]] = []
    abort_exc: Optional[BaseException] = None
    baseline: Optional[List[str]] = None
    # F4: partial 신호는 abort 조기 이탈(K-5 등) 시에도 reconcile 로 전달돼야 하므로 try 밖에서
    # 선-초기화한다 (try 안에서만 바인딩하면 조기 이탈 경로가 미바인딩 참조로 깨진다).
    baseline_partial: bool = False
    envelope_sample: Optional[Dict[str, Any]] = None
    list_golden: Optional[Dict[str, Any]] = None

    ctx.emit_event("approval", confirm_live_write=True,
                   note="operator 1회 승인 — 1 run 1 승인 (재사용 금지)")

    try:
        # K-5 page 신원 (write 이전 — deny-set + sentinel, fail-closed)
        gate = PageIdentityGate()
        identity = gate.verify(page_id, client, dry=dry)
        ctx.emit_event("preflight", stage="page-identity", **identity)
        results["page_identity"] = identity
        if not identity["ok"]:
            raise PageIdentityAbort(f"page 신원 게이트 실패 — {identity['reason']} (K-5)")

        # step R baseline (읽기 전용 · cap 무관)
        baseline, baseline_partial, enum_err = enumerate_property_keys(client, page_id, dry)
        ctx.emit_event("reconcile_snapshot", phase="baseline", keys=baseline,
                       partial=baseline_partial, error=enum_err)
        results["baseline_partial"] = baseline_partial
        list_golden = capture_list_golden(client, page_id, ctx.run_id, dry)

        if selected["size_budget"]:
            w1 = scenario_w1(client, ctx, page_id, dry)
            results["scenarios"]["W1"] = w1
            storage_scenarios.append({"write_success": w1["write_success"],
                                      "readback_byte_exact": w1["readback_byte_exact"]})
            ctx.emit_cap_state("after-W1")

            results["scenarios"]["W2"] = scenario_w2(client, ctx, page_id, dry)
            ctx.emit_cap_state("after-W2")

            w3, envelope_sample = scenario_w3(client, ctx, page_id, dry)
            results["scenarios"]["W3"] = w3
            ctx.emit_cap_state("after-W3")

        if selected["error_codes"]:
            w4 = scenario_w4(client, ctx, page_id, dry)
            results["scenarios"]["W4"] = w4
            over_limit_observations.append(w4["observation"])
            ctx.emit_cap_state("after-W4")

            results["scenarios"]["W5"] = scenario_w5(client, ctx, page_id, dry)
            ctx.emit_cap_state("after-W5")

    except (KeyboardInterrupt, Exception) as e:      # noqa: BLE001 — 전 abort 경로 결박 (P0-c)
        abort_exc = e
        logger.error(f"abort — {kill_switch_id(e)} / {type(e).__name__}")
    finally:
        try:
            results["cleanup"] = cleanup_properties(client, ctx, page_id, dry)
        except Exception as e:                       # noqa: BLE001
            results["cleanup"] = {"error": type(e).__name__}

    # ── 신호 전파 (§7.4 — 보안 FIX iter2 N1) ────────────────────────────────
    # 회수 루프는 **이미 완주**했고(§3.10 "cleanup 은 cap 이후에도 계속" 무손상) 그 *뒤에*
    # 흡수된 kill-switch 를 결과 축으로 승격한다. 승격 대상 = **kill-switch 계열 한정**
    # (판정 (ii)): 일반 DELETE 실패(`failed > 0`)는 승격하지 않고 reconcile 판정에 위임한다
    # — 경계가 흐려지면 §7.4.1 상태 A(회수 완료) 회수 규범과 충돌한다.
    # cleanup 실패 신호와 reconcile 결과는 **독립 신호**이며, 상충 시 reconcile 단독으로
    # "깨끗함" 을 단정할 수 없다 (§7.4.1 註).
    if abort_exc is None and ctx.cleanup_kill_switch is not None:
        abort_exc = ctx.cleanup_kill_switch

    # step R actual (cleanup 이후 — abort 여부와 무관하게 시도)
    actual_partial = False
    try:
        actual, actual_partial, actual_err = enumerate_property_keys(client, page_id, dry)
    except KillSwitchAbort as e:
        # F5 결과 결박: 열거는 더 이상 kill-switch 를 삼키지 않는다. 다만 이 호출은 try/finally
        # **밖**이라 그대로 전파하면 §3.10 의 "원장 기록 후 exit≠0" 이 깨진다(traceback 종료 =
        # abort 이벤트 0행). 따라서 삼키지 않되 abort 로 승격해 아래 `emit_abort` 가 1행을 남기고
        # exit≠0 로 종결하게 한다 (신호 소멸 0 ∧ 원장 누락 0).
        actual, actual_err = None, type(e).__name__
        if abort_exc is None:
            abort_exc = e
        logger.error(f"step R actual 열거 중 kill-switch — {kill_switch_id(e)}")
    ctx.emit_event("reconcile_snapshot", phase="actual", keys=actual,
                   partial=actual_partial, error=actual_err)
    reconcile_result = reconcile(baseline, actual, baseline_partial, actual_partial)
    results["reconcile"] = reconcile_result
    results["actual_partial"] = actual_partial

    # 측정 tier (관측 outcome ground-truth) ⊥ 운영 verdict (2축 분리 — §3.10)
    measurement_tiers = {
        "storage_axis": verdict_storage_axis(storage_scenarios),
        "over_limit_axis": verdict_over_limit_axis(over_limit_observations),
        "rate_axis": verdict_rate_axis(client.header_captures),
    }
    if abort_exc is not None:
        operational_verdict = "ABORTED"
    elif reconcile_result["status"] == "RECONCILED":
        operational_verdict = "RECONCILED"
    elif reconcile_result["status"] == "DRIFT":
        operational_verdict = "DRIFT"
    elif reconcile_result["status"] == "reconcile_partial":
        # bare 토큰 — `APPROVED-` 접두는 확산 금지 (아래 `APPROVED-UNRECONCILED` 는 리네임 파급
        # 3면[산출물 JSON·커밋된 golden/events fixture·테스트 assert] 비용 때문에 legacy 1건 잔존).
        operational_verdict = "PARTIAL"
    else:
        operational_verdict = "APPROVED-UNRECONCILED"

    results["measurement_tiers"] = measurement_tiers
    results["operational_verdict"] = operational_verdict
    results["accounting"] = ctx.accounting.snapshot()
    results["header_captures"] = client.header_captures
    results["rate_events"] = client.rate_events
    results["orphan_registry"] = ctx.orphan_snapshot()

    ctx.emit_event("reconcile_verdict", operational_verdict=operational_verdict,
                   reconcile_status=reconcile_result["status"],
                   residual=reconcile_result.get("residual"),
                   measurement_tiers=measurement_tiers)

    # captured-golden 후보 (실측 산출물 — repo 커밋은 operator 몫)
    golden_files: List[str] = []
    if envelope_sample is not None:
        shape = build_shape_golden(envelope_sample, ctx.run_id, page_id, 200)
        golden_files.append(write_golden_candidate(ctx.run_id, "shape-golden", shape).name)
    if list_golden is not None:
        golden_files.append(write_golden_candidate(ctx.run_id, "list-golden", list_golden).name)
    basis = build_basis_golden(results, client, ctx.run_id)
    golden_files.append(write_golden_candidate(ctx.run_id, "basis-golden", basis).name)
    results["golden_candidates"] = golden_files

    if abort_exc is not None:
        ctx.emit_abort(abort_exc)
        return 1, results
    if reconcile_result["status"] != "RECONCILED":
        return 1, results
    return 0, results


def build_basis_golden(results: Dict[str, Any], client: MeasurementRESTClient,
                       run_id: str) -> Dict[str, Any]:
    """basis golden — 수치만 (utf8/ascii/delta · status · 헤더명 세트 · 경계 결과 · WRAP_OVERHEAD)."""
    scenarios = results.get("scenarios", {})
    w2 = scenarios.get("W2", {})
    w3 = scenarios.get("W3", {})
    w4 = scenarios.get("W4", {})
    w5 = scenarios.get("W5", {})
    header_names = sorted({name
                           for capture in client.header_captures
                           for name in capture.get("headers_name_complete", [])})
    canonical = build_w1_fixture()
    chunk_dict = chunk(canonical, budget=effective_chunk_budget())
    sample_b64 = chunk_dict[local_chunk_key(0)]
    return {
        "run_id": run_id,
        "empirical_source": provenance("v2 property CRUD (measure run)",
                                       results.get("operational_verdict"), run_id),
        "encoding_basis": {
            "utf8_bytes": w3.get("utf8_bytes"),
            "ascii_bytes": w3.get("ascii_bytes"),
            "delta_bytes": w3.get("delta_bytes"),
        },
        "boundary_basis": {
            "points": [{"json_encoded_bytes": p.get("json_encoded_bytes"),
                        "write_success": p.get("write_success"),
                        "http_status": p.get("http_status")}
                       for p in w2.get("points", [])],
            "discriminating": w2.get("boundary_discriminating"),
        },
        "over_limit_basis": {
            "v2_probe_status": (w4.get("probe") or {}).get("http_status"),
            "v2_probe_classified_as": (w4.get("probe") or {}).get("classified_as"),
            "v2_control_status": (w4.get("control") or {}).get("http_status"),
            # FIX iter1 F-CL-07: null(성공 경로 status 미기록) ↔ 미실행 다의성 해소 — future-run 부터
            # write_success 동반 기록 (기captured golden 무편집 — §3.9).
            "v2_control_write_success": (w4.get("control") or {}).get("write_success"),
            "v1_probe_status": (w5.get("probe") or {}).get("http_status"),
            "v1_classification": (w5.get("probe") or {}).get("classification"),
        },
        "header_name_set": header_names,
        "header_capture_count": len(client.header_captures),
        "budget_basis": {
            "budget_bytes": BUDGET_BYTES,
            "wrap_overhead_bytes_declared": WRAP_OVERHEAD_BYTES,
            "wrap_overhead_bytes_local_measured": (json_encoded_size({"data": sample_b64})
                                                   - json_encoded_size(sample_b64)),
            "effective_chunk_budget": effective_chunk_budget(),
            "measurement_note": "wrap overhead 는 로컬 인코딩 산술 실측 — 서버 관측 아님",
        },
        "measurement_tiers": results.get("measurement_tiers"),
    }


# ── plan 모드 ───────────────────────────────────────────────────────────────

def run_plan(args, base_url: str, page_id: Optional[str], gate_summary: str) -> int:
    """flag 부재 = plan 모드 — 회계표 출력 후 exit 0 (실 write 0, HTTP 0회 원칙).

    예외 1건: creds ∧ page-id 가 모두 있으면 page 신원 GET **1회 read-only** 확인을 허용한다
    (승인 판단 재료). 부재 시 "미확인 — creds/page-id 부재" 로 정직 표기한다.

    K-7 endpoint preflight 는 이 GET **보다 앞선다** (F1): 아래 `gate.verify(..., dry=False)` 가
    자격증명을 실은 실 HTTP GET 을 4-AND 승인 이전에 발사하므로, client 생성의 host pin 위반을
    광역 `except` 가 "미확인" 으로 삼키면 오도착 위험이 조용히 넘어간다. 승격된
    `CredsPreflightAbort` 는 호출자(`main`)가 원장 1행 + exit≠0 로 종결한다.
    """
    plan = plan_accounting(cap=WRITE_CAP)
    plan["run_id"] = normalize_run_id(args.run_id)
    plan["gate_summary"] = gate_summary

    identity: Dict[str, Any] = {"checked": False,
                                "summary": "미확인 — creds/page-id 부재"}
    if creds_present() and page_id:
        # ↓ try 밖 — endpoint preflight 실패는 "미확인" 이 아니라 abort 다 (HTTP 0회 유지).
        accounting = WriteAccounting(cap=WRITE_CAP)
        client = create_client_or_abort(base_url, os.environ.get("ATLASSIAN_API_TOKEN"),
                                        os.environ.get("ATLASSIAN_USER_EMAIL"),
                                        accounting=accounting)
        try:
            gate = PageIdentityGate()
            verdict = gate.verify(page_id, client, dry=False)
            identity = {"checked": True, "summary":
                        ("OK — " if verdict["ok"] else "차단 — ") + verdict["reason"]}
            identity.update({k: v for k, v in verdict.items() if k != "title_verbatim"})
        except PageIdentityAbort as e:
            # K-5 전용 arm — KillSwitchAbort 선행절보다 **앞**에 둔다 (기존 처분 유지: plan 모드는
            # 신원 차단을 회계표에 표기하고 exit 0 으로 승인 판단 재료를 남긴다).
            identity = {"checked": True, "summary": f"차단 — {e}"}
        except KillSwitchAbort:                      # F5 — kill-switch 는 "미확인" 으로 삼키지 않는다
            raise
        except Exception as e:                       # noqa: BLE001
            identity = {"checked": True, "summary": f"미확인 — 확인 시도 실패 ({type(e).__name__})"}
    plan["page_identity"] = identity

    print(emit_record(render_plan_table(plan)), file=sys.stdout)
    print(emit_record(plan), file=sys.stdout)
    return 0


# ── main ────────────────────────────────────────────────────────────────────

def setup_logging() -> None:
    """T-3 — root logger 에 SanitizedHandler 부착 (rest.py 의 sanitizer 재사용).

    import 시점이 아니라 `main()` 에서만 호출한다 (모듈 import 부작용 0 — verdict 함수 순수성).

    formatter 배치 주의 (rest.py 무수정 제약 하 이중 prefix 회피): `SanitizedHandler.emit` 은
    자기 formatter 로 1회 format → scrub → `record.msg` 치환 → base handler 가 **다시** format
    한다. 따라서 base 에 full format 을 주면 `TS [INFO] TS [INFO] msg` 로 prefix 가 겹친다.
    배치 = base 는 `%(message)s`(pass-through), wrapper 가 full format 을 소유 (생성자가
    base.formatter 를 복사하므로 **생성 후** 재지정해야 한다).
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    base = logging.StreamHandler(sys.stderr)
    base.setFormatter(logging.Formatter("%(message)s"))
    handler = SanitizedHandler(base)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    root.handlers = [handler]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="confluence_backward_measure.py",
        description="CFP-2889 live 실측 harness (AC-11/12/13 정산). flag 부재 = plan 모드.",
    )
    parser.add_argument("--all", action="store_true", help="전 측정 시나리오 실행")
    parser.add_argument("--measure-size-budget", action="store_true",
                        help="W1~W3 (32KB round-trip · 경계 · 인코딩)")
    parser.add_argument("--measure-error-codes", action="store_true",
                        help="W4~W5 (v2 over-limit · v1 probe)")
    parser.add_argument("--measure-rate-limits", action="store_true",
                        help="rate 헤더 관측 (전 응답 캡처는 항상 축적 — 별도 write 0)")
    parser.add_argument("--load-creds", type=str, default=None,
                        help="creds 파일 경로 (기본: ~/.claude/codeforge-scratch/atlassian-creds.env)")
    parser.add_argument("--confirm-live-write", action="store_true",
                        help="**승인 게이트** — 실 API write 실행 (1 run 1 승인, 재사용 금지)")
    parser.add_argument("--run-id", type=str, default=None,
                        help="run 식별자 (기본 = KST timestamp 파생)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging()

    run_id = normalize_run_id(args.run_id)
    creds_file_found = load_creds_from_file(Path(args.load_creds) if args.load_creds else None)

    page_id = os.environ.get(TEST_PAGE_ID_ENV)
    # L1 자원 id preflight (F2) — **K-5 deny 대조·sentinel 보다 앞선다**. 값이 있을 때만 검사하며
    # 미설정(정상 dry 경로)은 기존 거동 그대로다. 위반 = K-7 abort (write 0회, run 미개시).
    if page_id:
        try:
            page_id = validate_page_id_or_abort(page_id)
        except CredsPreflightAbort as e:
            return abort_with_ledger(e, run_id)

    skip_write = os.environ.get(SKIP_WRITE_ENV, "0") == "1"
    base_url = os.environ.get(CONFLUENCE_BASE_URL_ENV, DEFAULT_BASE_URL)
    cbl_skip = os.environ.get(CBL_SKIP_ISSUE_CREATE_ENV)

    # §7.4.5 재정의 — measure.py 에 Issue-create 경로 자체가 0 (vacuous-true). 설정 여부만 1줄 기록.
    logger.info(f"{CBL_SKIP_ISSUE_CREATE_ENV} 설정 여부={bool(cbl_skip)} "
                f"(본 harness 는 Issue-create 경로 0 — vacuous-true, 준수 주장 아님)")

    gate_summary = (f"confirm_live_write={args.confirm_live_write} · creds={creds_present()} · "
                    f"test_page_id={'set' if page_id else 'unset'} · skip_write={skip_write}")
    logger.info(f"게이트 상태: {gate_summary}")

    live = bool(args.confirm_live_write) and creds_present() and bool(page_id) and not skip_write
    if not live:
        if args.confirm_live_write:
            logger.warning("--confirm-live-write 가 있으나 4-AND 미충족 — plan 모드로 강등")
        try:
            return run_plan(args, base_url, page_id, gate_summary)
        except KillSwitchAbort as e:
            # plan 경로도 **원장 없는 종료를 만들지 않는다** (§3.10). run_plan 은 RunContext 를
            # 소유하지 않으므로 여기서 최소 context 로 abort 1행을 남기고 exit≠0 로 종결한다.
            # 포착 범위 = `MeasureAbort` 가 아니라 상위 `KillSwitchAbort` 다 — run_plan 의 F5
            # 재-raise 절은 rest.py 소유 kill-switch(K-1/K-2/K-4)도 올려보내므로, 좁게 잡으면
            # 그쪽이 원장 없는 traceback 으로 빠져나간다.
            return abort_with_ledger(e, run_id)

    selected = {
        "size_budget": bool(args.all or args.measure_size_budget
                            or not (args.measure_size_budget or args.measure_error_codes
                                    or args.measure_rate_limits)),
        "error_codes": bool(args.all or args.measure_error_codes
                            or not (args.measure_size_budget or args.measure_error_codes
                                    or args.measure_rate_limits)),
    }

    ctx = RunContext(run_id=run_id, cap=WRITE_CAP)
    try:
        creds_preflight(creds_file_found)            # K-7 (creds 축)
    except CredsPreflightAbort as e:
        return abort_with_ledger(e, run_id, ctx)

    # N9(iter2): host-선언 필드(구 `base_url_host_...` 계열) 제거 — 본 이벤트는 host 검증
    #   ※ 필드명 리터럴을 주석에도 남기지 않는다: 정적 backstop 이 소스 텍스트를 검사하므로
    #     주석 잔존만으로 false RED 가 난다 (실측 확인).
    # (`create_client_or_abort`) **이전**에 기록되므로, pin 실패 run 의 원장에 `true` 행과
    # K-7 abort 행이 공존하는 **자기모순 원장**이 된다. pin 성공 사실은 client 생성 성공이,
    # 실패 사실은 K-7 abort 행이 각각 증명하므로 본 필드는 잉여다.
    ctx.emit_event("preflight", stage="env",
                   cap=WRITE_CAP,
                   cbl_skip_issue_create_set=bool(cbl_skip),
                   creds_file_found=creds_file_found,
                   # FIX iter1 F-CL-11: mock seam flag 상태를 원장에 기록 (future-run —
                   # 기captured NDJSON 무편집).
                   mock_429_env_set=(os.environ.get("CFP1495_API_MOCK_429", "0") == "1"),
                   mock_401_env_set=(os.environ.get("CFP1495_API_MOCK_401", "0") == "1"),
                   note="creds 파일 경로·값은 기록하지 않는다 (§7.5)")

    try:
        # K-7 (endpoint 축) — 생성자 host pin 의 ValueError 를 승격해 원장에 결박한다 (F1).
        client = create_client_or_abort(base_url, os.environ.get("ATLASSIAN_API_TOKEN"),
                                        os.environ.get("ATLASSIAN_USER_EMAIL"),
                                        accounting=ctx.accounting)
    except CredsPreflightAbort as e:
        return abort_with_ledger(e, run_id, ctx)

    exit_code, results = run_live(client, ctx, page_id, selected)
    print(emit_record(results), file=sys.stdout)
    logger.info(f"운영 verdict={results.get('operational_verdict')} · "
                f"측정 tier={results.get('measurement_tiers')} · "
                f"events={ctx.events_path.name}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
