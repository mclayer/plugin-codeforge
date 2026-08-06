#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confluence_property_rest.py — creds-gated property REST transport (leg B).

CFP-2829 S2 원판 → CFP-2889 재설계 (Change Plan §3/§4/§5 #1):
  - D1: v2 id-기반 CRUD 정합 — upsert 프로토콜
        (`GET ?key=` resolve → 부재 POST / 존재 PUT by property-id + version n+1 / DELETE by id).
        기존 key-path public 3메서드(get/put/delete_property_v2)는 삭제 (internal-only breaking —
        제3 production 소비자 0 실측, Change Plan §4.1 처분 표).
  - D2: CR-C2 근본 봉인 — 2-layer DTO (transport envelope ⊥ application value) +
        `_unwrap_property` SSOT (live·dry 동일 함수 통과) + dry 경로 = captured-golden 파생
        mock transport (golden 부재 시 GoldenFixtureMissingError 명시 에러 — skip 금지).
  - D3: 예산 계약 단일화 — `WRAP_OVERHEAD_BYTES` SSOT (wrap 소유 모듈 = 본 모듈) +
        `effective_chunk_budget()`. chunking.py 는 무변경 (순수성 보존).
  - D6: 내부 import = `lib.confluence_property_chunking` qualified 통일.
  - D7 (P0-a/b/c): Retry-After 파싱은 status dispatch 뒤 429 분기 안에서만 수행
        (HTTP-date 형 = RFC 9110 §10.2.3 합법 — 기준은 응답 `Date` 헤더, 로컬 clock 아님).
        write retry = 429 한정 1회 (예외·타임아웃 재전송 금지 — 도달 불확정 재-PUT = 오염 증폭).
        단건 wait 60s clamp · 누적 120s 초과 시 재시도 포기. 401 = AuthAbortError 즉시 전역 abort.
        429 누적 >=3 = RateAbortError (K-4 — 의도적 유발 실험 근접 회피).
  - 전역 write 회계: `WriteAccounting` 주입 (measure.py 생성·소유, 수명 = run 1회) —
        증가 지점 = transport HTTP 시도 직전 (retry loop 내부). cap 도달 = WriteCapExceeded
        hard-stop (silent False 금지). DELETE 는 cap 밖 별도 집계 (soft-ceiling 40). GET 별도.

Security (Change Plan §7):
  - SA-1: env-indirect token (ATLASSIAN_API_TOKEN / ATLASSIAN_USER_EMAIL)
  - T-4/T-4b: `_scrub` = exact-value redaction 1순위 (token·email·b64(email:token) 파생형)
              + 휴리스틱 backstop (미지 형태는 heuristic 의존 — 정직 잔여)
  - T-11 digest 축: `grouped_hex` — 64-hex validator 강제 (비정합 입력 = ValueError,
              silent pass-through 금지). body 축은 grouping 비적용 (`sanitize_body_field`
              — truncate ≤200B → scrub → deny-scan 원경로, hit 시 필드 drop).
  - T-5: `normalize_base_url` — host pin + https 강제 통과 후 `/wiki` 접미 중복 제거 (EC-12).
  - deny-scan 원형 유지 (20+ base64-유사 무조건 abort — 완화 0).
  - write 경로 `allow_redirects=False` (cross-host Authorization 유출 방어 보조).
"""

import base64
import copy
import json
import logging
import os
import re
import sys
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# cp949 guard (Windows CI utf-8 stdout)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Conditional import for requests (offline dry/plan 경로는 requests 불요)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Constants ────────────────────────────────────────────────────────────────

PROPERTY_KEY_PREFIX = "codeforge.sync.canonical"
MANIFEST_KEY = f"{PROPERTY_KEY_PREFIX}.__manifest"
CHUNK_KEY_TEMPLATE = f"{PROPERTY_KEY_PREFIX}.__chunk_{{n}}"

# Budget: 28KB conservative (32KB - 4KB safety margin) — AC-4 실측 후 근거 기록 (조정 집행 = Non-goal)
BUDGET_BYTES = 28 * 1024

# D3 예산 계약 SSOT — wrap(`{"data": ...}`) 을 만드는 모듈이 overhead 도 소유 (캡슐화 정합).
# 정의 = wrap-인코딩 − bare-인코딩 증분 (json.dumps 기본 separator `": "` 기준):
#   bare  = `"<b64>"`            = len(b64) + 2
#   wrap  = `{"data": "<b64>"}`  = len(b64) + 12
#   ⇒ overhead = 10B (산술 — Change Plan §3.6. compact separator 구현 시 9B 이나 본 구현은
#     기본 separator 로 직렬화·전송하므로 10B 가 wire-정확).
# [empirical-source: 2026-08-06T06:02:00+09:00, run_id=20260806T060155 — AC-4 ③ 확정: 로컬 인코딩
#   산술 실측 10B (서버 관측 아님 — basis golden budget_basis.wrap_overhead_bytes_local_measured=10,
#   갱신은 실 재측정 시에만 §3.9)]
WRAP_OVERHEAD_BYTES = 10


def effective_chunk_budget() -> int:
    """chunk() 에 명시 전달할 유효 예산 = BUDGET_BYTES − WRAP_OVERHEAD_BYTES.

    불변식 (§8 D-5): json_encoded_size(wrap(chunk_i)) ≤ BUDGET_BYTES ∀ i.
    chunking default(CONSERVATIVE_BUDGET) 의존 금지 — 항상 본 함수 값을 명시 전달 (D3).
    """
    return BUDGET_BYTES - WRAP_OVERHEAD_BYTES


# Retry 정책 (D7 — Change Plan §3.10. 수치는 실측치가 아닌 설계 보수 파라미터:
#   60s = 단건 대기 상한 재량, 120s = 2×. [empirical-source: TBD → AC-13 관측 후 조정 가능])
MAX_RETRY_ATTEMPTS = 2          # write HTTP 시도 상한 = 최초 1 + 429-한정 재시도 1
INITIAL_BACKOFF_SECONDS = 1.0   # 서버 Retry-After 부재·파싱 불가 시 fallback backoff
RETRY_AFTER_CLAMP_SECONDS = 60.0
RETRY_TOTAL_WAIT_ABORT_SECONDS = 120.0
RATE_429_ABORT_THRESHOLD = 3    # K-4: run 내 429 누적 >=3 → abort

# DELETE soft-ceiling (cap 밖 별도 집계 — write-cap 20 의 2배: chunk+manifest 회수 여유)
DELETE_SOFT_CEILING = 40

# IO-7: 실 저장 대상 page id (부재 시 dry-run — 실 write 0).
TEST_PAGE_ID_ENV = "CFP2829_TEST_PAGE_ID"

# captured-golden fixture 위치 (D2 — mock transport 의 envelope/list 골격 1차 출처 = 실 capture 뿐)
GOLDEN_DIR_ENV = "CFP2889_GOLDEN_DIR"
SHAPE_GOLDEN_FILENAME = "property_envelope_shape_golden.json"
LIST_GOLDEN_FILENAME = "property_list_shape_golden.json"

# rate 관련 헤더 전 계열 (§4.2 RATE_HEADER_FAMILIES — enforcement 후 무-prefix 형 포함)
RATE_HEADER_FAMILIES = ("retry-after", "x-ratelimit-", "ratelimit-", "beta-", "x-beta-")


class ChunkStoreError(RuntimeError):
    """leg-B chunk-store orchestration 무결성 위반 (manifest 부재 / 부분 저장 / reassemble 실패)
    — fail-closed 신호 (부분 데이터 노출 0, IO-6)."""


class GoldenFixtureMissingError(RuntimeError):
    """captured-golden fixture 부재/형식 미달 — dry round-trip 은 명시 에러 (skip 금지, §3.3).

    mock 이 실측 없이 임의 형상을 fabricate 하는 것을 구조적으로 차단한다 (D-13 negative-control 대상)."""


class AuthAbortError(RuntimeError):
    """401 Unauthorized — K-1 전역 abort (재시도 0, refresh 신설 금지)."""


class RateAbortError(RuntimeError):
    """429 누적 >= RATE_429_ABORT_THRESHOLD — K-4 abort (의도적 유발 실험 근접 회피)."""


class WriteCapExceeded(RuntimeError):
    """self-cap 도달 — K-2 hard-stop (silent False 금지). cleanup(DELETE) 은 cap 밖이라 계속."""


class PropertyResolveError(RuntimeError):
    """key→id resolve 실패 (list 비-200 / 응답 형상 미지) — 추정치 PUT 금지 (fail-closed, 결정 12)."""


# ── MOCK env flags (call-time 판독 — 테스트 runtime toggle 정합) ─────────────

def _mock_401_active() -> bool:
    return os.environ.get("CFP1495_API_MOCK_401", "0") == "1"


def _mock_429_active() -> bool:
    return os.environ.get("CFP1495_API_MOCK_429", "0") == "1"


# ── Logging & Sanitization ──────────────────────────────────────────────────

def _known_secret_values() -> List[str]:
    """exact-value redaction 1순위 대상 (T-4/T-4b): token·email·b64(email:token) 파생형.

    env 를 call-time 판독 (테스트 env 조작 정합). 짧은 값(<4)은 과잉 마스킹 방지 위해 제외.
    """
    out: List[str] = []
    token = os.environ.get("ATLASSIAN_API_TOKEN") or ""
    email = os.environ.get("ATLASSIAN_USER_EMAIL") or ""
    if len(token) >= 4:
        out.append(token)
    if len(email) >= 4:
        out.append(email)
    if len(token) >= 4 and len(email) >= 4:
        derived = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
        out.append(derived)
    return out


def _scrub(text: str) -> str:
    """Mask sensitive values in text.

    순서 (Change Plan §7.1 gate D step 2):
      1) exact-value redaction 1순위 — token / email / b64(email:token) 파생형 (T-4b:
         email 은 `@`·`.` 로 20+ run 이 분절되어 휴리스틱이 못 잡는다 — exact-match 필수).
      2) 휴리스틱 backstop — 20+ base64-유사 시퀀스 / Basic auth 헤더 (미지 형태 비밀은
         본 backstop 의존 — 전축 "구조적 0" 주장 아님, 정직 잔여 T-4).
    """
    if not isinstance(text, str):
        text = str(text)

    for secret in _known_secret_values():
        if secret in text:
            text = text.replace(secret, "***REDACTED***")

    # heuristic backstop: 20+ alphanumeric/+/= chars
    text = re.sub(r'([A-Za-z0-9+/=]{20,})', r'***REDACTED***', text)
    # Basic auth header
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
            record.msg = sanitized
            record.args = ()
            self.base_handler.emit(record)
        except Exception:
            self.handleError(record)


def _setup_sanitized_logging() -> logging.Logger:
    logger = logging.getLogger("confluence_property_rest")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(SanitizedHandler(handler))
    return logger


logger = _setup_sanitized_logging()


# ── Envelope Sanitization & Deny-Scan (원형 유지 — 완화 0) ────────────────────

def _deny_scan_for_secrets(text: str) -> Tuple[bool, Optional[str]]:
    """
    Scan text for potential token/auth leaks before emission.

    Returns: (is_safe, error_message)
    """
    if not isinstance(text, str):
        return True, None

    if re.search(r'Basic [A-Za-z0-9+/=]{20,}', text):
        return False, "Detected Basic auth header in output — aborting"

    # F-SEC-03: 20+ [A-Za-z0-9+/=] 시퀀스는 무조건 abort (fail-closed). CFP-2889 에서도
    # 원형 유지 — grouped-hex(digest 축)·필드 drop(body 축) 이 앞단 흡수 계층이고 본 스캔이
    # 최종 방어선 (K-6).
    if re.search(r'[A-Za-z0-9+/=]{20,}', text):
        return False, "Detected potential token/secret (20+ base64-like sequence) in output — aborting"

    return True, None


# ── digest 축: grouped-hex (T-11 — 64-hex validator 강제) ────────────────────

_HEX64_RE = re.compile(r"[0-9a-f]{64}")


def grouped_hex(digest: str) -> str:
    """sha256 hex digest → 8자-하이픈 grouped 표기 (deny-scan 양립 — 20+ run 미형성).

    validator 강제: 64-hex lowercase fullmatch 실패 = ValueError (변환 거부 — silent
    pass-through 금지. 임의 문자열이 grouping 경유로 20+ run 을 분절하는 세탁 재도입 차단,
    DR-P0-2 (a) / D-10c). 비밀 아님이 구성적으로 보장된 값만 변환.
    """
    if not isinstance(digest, str) or not _HEX64_RE.fullmatch(digest):
        raise ValueError("grouped_hex: 입력이 64-hex lowercase digest 가 아님 — 변환 거부 (T-11 validator)")
    return "-".join(digest[i:i + 8] for i in range(0, 64, 8))


def ungroup_hex(grouped: str) -> str:
    """grouped-hex → 원 64-hex (무손실·결정론 역변환)."""
    parts = grouped.split("-")
    if len(parts) != 8 or any(not re.fullmatch(r"[0-9a-f]{8}", p) for p in parts):
        raise ValueError("ungroup_hex: grouped-hex 형식 아님")
    return "".join(parts)


# ── body 축: 비신뢰 응답 body 필드 정책 (§3.9 — grouping 전면 비적용) ─────────

def sanitize_body_field(text: Optional[str]) -> Tuple[Optional[str], bool, int]:
    """응답 body verbatim 필드 정책: truncate ≤200B → scrub → deny-scan 원경로.

    hit 시 = 필드 drop (`body_omitted_by_deny_scan: true` — 원문은 어떤 채널에도 미기록,
    run 은 계속. "우회" 가 아니라 "drop", DR-P0-2 (b)).

    Returns: (body_verbatim | None, omitted_by_deny_scan, body_length_bytes)
    """
    if text is None:
        return None, False, 0
    raw = text.encode("utf-8", errors="replace")
    raw_len = len(raw)
    truncated = raw[:200].decode("utf-8", errors="replace")
    scrubbed = _scrub(truncated)
    ok, _err = _deny_scan_for_secrets(scrubbed)
    if not ok:
        return None, True, raw_len
    return scrubbed, False, raw_len


# ── Error Classification (AC-12 — 순수함수 계약 유지) ────────────────────────

_OVER_LIMIT_V2_PHRASES = (
    "too large",
    "too long",
    "maximum size",
    "size limit",
    "exceeds",
    "exceed the",
    "payload too large",
    "request entity too large",
)
# 크기 수치 토큰 — word-boundary 로 정밀화 (bare "32" 오매칭 방지: "xyz32"/"1324" 는 boundary 불충족).
_OVER_LIMIT_V2_TOKEN_RE = re.compile(r"\b(?:32\s?kb|32768|5242880)\b", re.IGNORECASE)


def is_over_limit_error(version: int, status_code: int, body_text: str = "") -> bool:
    """
    Classify over-limit errors disjointly across v1 and v2 APIs (AC-12).

    Rules:
      - v1: status_code == 413 (Payload Too Large) → True
      - v2: status_code == 400 AND body contains size signature (whole-phrase / boundary token) → True
      - All other cases → False

    실문언 보정은 실측 golden body 로 회귀 고정 (suite-B replay — §4.2).
    """
    if version == 1:
        return status_code == 413

    if version == 2:
        if status_code != 400:
            return False
        body = body_text or ""
        body_lower = body.lower()
        if any(sig in body_lower for sig in _OVER_LIMIT_V2_PHRASES):
            return True
        return bool(_OVER_LIMIT_V2_TOKEN_RE.search(body))

    return False


# ── Creds I/O (env-indirect, IO-1) ──────────────────────────────────────────

def _get_creds() -> Tuple[Optional[str], Optional[str]]:
    token = os.environ.get("ATLASSIAN_API_TOKEN")
    email = os.environ.get("ATLASSIAN_USER_EMAIL")
    if token and email:
        logger.debug("Creds loaded (env-indirect)")
        return token, email
    logger.warning("ATLASSIAN_API_TOKEN/USER_EMAIL not set — REST write will fail")
    return None, None


def _basic_auth_header(email: str, token: str) -> str:
    credential = f"{email}:{token}"
    encoded = base64.b64encode(credential.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


# ── base_url 정규화 (T-5 + EC-12) ───────────────────────────────────────────

def normalize_base_url(base_url: str, expected_host: Optional[str] = None) -> str:
    """base_url 정규화 — host pin + https 강제 통과 **후** `/wiki` 접미 중복 제거.

    보안 축(T-5: 자격증명 수신 호스트 결정)과 정합성 축(EC-12: overlay SSOT 가 `/wiki` 접미
    포함이어도 `/wiki/wiki/...` 이중 경로 미발생)을 분리 적용한다. fail-closed (ValueError).
    """
    p = urlparse((base_url or "").strip())
    if p.scheme != "https":
        raise ValueError("base_url: https 강제 (T-5) — 다른 scheme 불허")
    if not p.hostname:
        raise ValueError("base_url: host 부재")
    if expected_host is not None and p.hostname != expected_host:
        raise ValueError(
            f"base_url host pin 불일치 — 기대 {expected_host!r} (자격증명 오도착 차단, T-5)"
        )
    path = (p.path or "").rstrip("/")
    if path.endswith("/wiki"):
        path = path[: -len("/wiki")]
    if path:
        raise ValueError(f"base_url: 미지 경로 성분 {path!r} — `/wiki` 접미 외 불허 (fail-closed)")
    return f"{p.scheme}://{p.netloc.rstrip('/')}".rstrip("/")


# ── captured-golden 파생 mock transport 골격 (D2) ────────────────────────────

def _golden_dir() -> Path:
    override = os.environ.get(GOLDEN_DIR_ENV)
    if override:
        return Path(override)
    # scripts/lib/ → repo root → tests/fixtures/cfp_2889
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "cfp_2889"


def _load_golden_json(filename: str) -> Any:
    path = _golden_dir() / filename
    if not path.exists():
        raise GoldenFixtureMissingError(
            f"captured-golden 부재: {filename} — dry round-trip 은 golden 없이는 명시 에러다 "
            f"(skip 금지, §3.3. golden 은 실측(§9 step 4-6) 산출물이며 합성 생성 금지)"
        )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise GoldenFixtureMissingError(f"captured-golden 파싱 실패: {filename} — {e}") from e


def load_shape_golden() -> Dict[str, Any]:
    """단건 PropertyEnvelope shape golden — 키 집합의 1차 출처 = 실 capture 뿐 (F-2 렌더 절단)."""
    tmpl = _load_golden_json(SHAPE_GOLDEN_FILENAME)
    if not isinstance(tmpl, dict) or not {"id", "key", "value", "version"}.issubset(tmpl.keys()) \
            or not isinstance(tmpl.get("version"), dict) or "number" not in tmpl["version"]:
        raise GoldenFixtureMissingError(
            f"{SHAPE_GOLDEN_FILENAME}: envelope 골격 미달 (id/key/value/version.number 필수)"
        )
    return tmpl


def load_list_golden() -> Dict[str, Any]:
    """list 응답 wrapper shape golden (`results[]` 골격·pagination 필드 유무 — DR-P1-5)."""
    tmpl = _load_golden_json(LIST_GOLDEN_FILENAME)
    if not isinstance(tmpl, dict) or "results" not in tmpl or not isinstance(tmpl["results"], list):
        raise GoldenFixtureMissingError(f"{LIST_GOLDEN_FILENAME}: list 골격 미달 (`results` list 필수)")
    return tmpl


# ── Write 회계 (§3.10 tie-break: measure.py 생성·소유 → client 주입) ─────────

class WriteAccounting:
    """전역 단일 write 카운터 — 수명 = run 1회 (client 재생성 시 리셋 위험 차단).

    계상 (해석 A — 사용자 확정): cap = POST·PUT HTTP **시도** 합산 (retry 포함) ≤ cap.
    DELETE = cap 밖 별도 집계 (soft-ceiling — 초과 시 경고, 회수는 계속).
    GET = cap 밖 별도 집계 (rate 관측 집계에는 포함).
    cap 도달 = WriteCapExceeded raise (hard-stop, silent False 금지 — K-2).
    """

    def __init__(self, cap: int = 20, delete_soft_ceiling: int = DELETE_SOFT_CEILING):
        self.cap = cap
        self.delete_soft_ceiling = delete_soft_ceiling
        self.write_attempts = 0
        self.delete_attempts = 0
        self.get_count = 0
        self.write_log: List[str] = []
        # 증가 직전 훅 (write-ahead intent 기록용 — measure.py 가 배선; HTTP 시도 이전 보장)
        self.on_write_attempt = None  # Optional[Callable[[dict], None]]

    def record_write_attempt(self, intent: Optional[Dict[str, Any]] = None) -> None:
        if self.write_attempts >= self.cap:
            raise WriteCapExceeded(
                f"self-cap {self.cap} 도달 — write hard-stop (K-2). cleanup DELETE 는 cap 밖이라 계속"
            )
        if self.on_write_attempt is not None:
            self.on_write_attempt(dict(intent or {}, attempt_no=self.write_attempts + 1))
        self.write_attempts += 1
        label = (intent or {}).get("label", "")
        self.write_log.append(label)

    def record_delete_attempt(self, label: str = "") -> None:
        self.delete_attempts += 1
        if self.delete_attempts > self.delete_soft_ceiling:
            logger.warning(
                f"DELETE soft-ceiling({self.delete_soft_ceiling}) 초과 — 회수는 계속 (cap 밖)"
            )

    def record_get(self) -> None:
        self.get_count += 1

    def snapshot(self) -> Dict[str, int]:
        return {
            "cap": self.cap,
            "write_attempts": self.write_attempts,
            "delete_attempts": self.delete_attempts,
            "get_count": self.get_count,
            "remaining": self.cap - self.write_attempts,
        }


# ── DTO helpers (§4.2) ──────────────────────────────────────────────────────

def _error_info(origin: str, *, http_status: Optional[int] = None,
                body_text: Optional[str] = None, classified_as: Optional[str] = None,
                probe_pair_id: Optional[str] = None,
                message: Optional[str] = None) -> Dict[str, Any]:
    """ErrorInfo 조립 — origin ∈ {local-reject, server-response, exception} 은
    AC-7 verdict ground-truth 의 시그니처-층위 전제 (local-reject ≠ server-observed)."""
    if body_text is not None:
        body_verbatim, omitted, body_len = sanitize_body_field(body_text)
    else:
        body_verbatim, omitted, body_len = None, None, None
    return {
        "origin": origin,
        "http_status": http_status,
        "body_verbatim": body_verbatim,
        "body_omitted_by_deny_scan": omitted,
        "body_length": body_len,
        "classified_as": classified_as,
        "probe_pair_id": probe_pair_id,
        "message": message,
    }


def _unwrap_property(envelope: Dict[str, Any]) -> Any:
    """CR-C2 unwrap SSOT — live·dry 양 경로가 본 함수 하나를 통과한다 (D2).

    Layer 1 (transport envelope) `{id, key, value, version}` → Layer 2 (application value).
    """
    if not isinstance(envelope, dict) or "value" not in envelope:
        raise ChunkStoreError("envelope 형식 오류 — 'value' 부재 (CR-C2 unwrap fail-closed)")
    return envelope["value"]


# ── 응답 객체 (synthetic — mock flag / dry transport 공용) ───────────────────

class _CIHeaders:
    """case-insensitive 헤더 dict (requests CaseInsensitiveDict 최소 등가)."""

    def __init__(self, items: Optional[Dict[str, str]] = None):
        self._store: Dict[str, Tuple[str, str]] = {}
        for k, v in (items or {}).items():
            self._store[k.lower()] = (k, str(v))

    def get(self, name: str, default=None):
        hit = self._store.get(name.lower())
        return hit[1] if hit else default

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._store

    def keys(self) -> List[str]:
        return [orig for (orig, _v) in self._store.values()]

    def items(self):
        return [(orig, v) for (orig, v) in self._store.values()]


class _SyntheticResponse:
    def __init__(self, status_code: int, headers: Optional[Dict[str, str]] = None,
                 body_text: str = ""):
        self.status_code = status_code
        self.headers = _CIHeaders(headers)
        self.text = body_text

    def json(self):
        return json.loads(self.text)


# ── REST Transport (leg B, creds-gated) ──────────────────────────────────────

_PROP_LIST_PATH_RE = re.compile(r"^/wiki/api/v2/pages/(?P<page>[^/]+)/properties/?$")
_PROP_ID_PATH_RE = re.compile(r"^/wiki/api/v2/pages/(?P<page>[^/]+)/properties/(?P<pid>[^/]+)$")


class ConfluencePropertyREST:
    """
    Property REST transport (v2 id-기반 CRUD — CFP-2889 D1).

    공개 v2 표면 (§4.1): list_properties_v2 / create_property_v2 / update_property_v2 /
    remove_property_v2 / upsert_property_v2. 구 key-path 3메서드는 삭제됨.
    store_chunked_property / load_chunked_property 공개 시그니처는 무변경 (소비자 파급 0).
    """

    def __init__(self, base_url: str, token: Optional[str], email: Optional[str],
                 accounting: Optional[WriteAccounting] = None):
        self.base_url = (base_url or "").rstrip("/")
        self.token = token
        self.email = email
        self.accounting = accounting
        self._session = None
        # K-4: run 내 429 누적 관측
        self.rate_429_count = 0
        self.rate_events: List[Dict[str, Any]] = []
        # 최근 list 열거의 pagination 정직 표기 (step R — §14 #5)
        self.last_list_partial = False
        # dry-run mock transport 상태 (golden-파생 envelope 저장소: key → envelope)
        self._mock_store: Dict[str, Dict[str, Any]] = {}
        self._mock_next_id = 1001

    # ── session ──

    def _ensure_session(self):
        if not HAS_REQUESTS:
            return None
        if self._session is None and self.token and self.email:
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": _basic_auth_header(self.email, self.token),
                "Content-Type": "application/json",
            })
        return self._session

    # ── dry-run 판정 (IO-7) ──

    def _is_dry_run(self, dry_run: Optional[bool]) -> bool:
        """dry-run 판정 — 명시 인자 우선, 미지정 시 IO-7(TEST_PAGE_ID 부재 → dry-run)."""
        if dry_run is not None:
            return dry_run
        return not os.environ.get(TEST_PAGE_ID_ENV)

    # ── 단일 HTTP choke-point ──

    def _perform_request(self, method: str, path: str, *, body_bytes: Optional[bytes] = None,
                         params: Optional[Dict[str, str]] = None, dry: bool = False,
                         timeout: int = 10):
        """모든 HTTP 가 지나는 단일 지점. mock env flag → synthetic / dry → golden-mock /
        그 외 실 세션. `allow_redirects=False` (redirect 추종 0 — 관측 충실도 + T-5 보조)."""
        if _mock_401_active():
            return _SyntheticResponse(401, {}, "")
        if _mock_429_active():
            # dark-path D-12: production retry 루프를 실제로 행사시키는 synthetic 429.
            return _SyntheticResponse(429, {"Retry-After": "0"}, "")
        if dry:
            return self._mock_transport(method, path, body_bytes=body_bytes, params=params)

        session = self._ensure_session()
        if session is None:
            raise PropertyResolveError("세션 불가 (requests 미설치 또는 creds 부재)")
        url = f"{self.base_url}{path}"
        return session.request(
            method, url, data=body_bytes, params=params, timeout=timeout,
            allow_redirects=False,
        )

    # ── golden-파생 mock transport (dry 전용 — D2/DR-P1-5) ──

    def _mock_transport(self, method: str, path: str, *, body_bytes: Optional[bytes],
                        params: Optional[Dict[str, str]]):
        """dry 경로 HTTP 등가 처리 — envelope/list 골격은 captured-golden 파생 (부재 = 명시 에러).

        dynamic version counter: PUT 은 `version.number == 현재+1` 강제 (409 시뮬레이션) →
        "resolve n+1 항상 송신" (결정 12) 이 dry 에서도 행사된다.
        """
        m_list = _PROP_LIST_PATH_RE.match(path)
        m_id = _PROP_ID_PATH_RE.match(path)

        if method == "GET" and m_list:
            list_tmpl = load_list_golden()
            key_filter = (params or {}).get("key")
            results = [copy.deepcopy(env) for env in self._mock_store.values()
                       if key_filter is None or env.get("key") == key_filter]
            body = copy.deepcopy(list_tmpl)
            body["results"] = results
            # pagination 필드는 golden 골격 그대로 유지 (mock 은 단일 페이지)
            if isinstance(body.get("_links"), dict):
                body["_links"].pop("next", None)
            return _SyntheticResponse(200, {"Content-Type": "application/json"},
                                      json.dumps(body, ensure_ascii=False))

        if method == "POST" and m_list:
            payload = json.loads((body_bytes or b"{}").decode("utf-8"))
            key = payload.get("key")
            if key in self._mock_store:
                return _SyntheticResponse(
                    400, {"Content-Type": "application/json"},
                    json.dumps({"message": "mock-duplicate: property already exists for key"}))
            env = self._golden_envelope(key, payload.get("value"), version_number=1)
            self._mock_store[key] = env
            return _SyntheticResponse(200, {"Content-Type": "application/json"},
                                      json.dumps(env, ensure_ascii=False))

        if m_id:
            pid = m_id.group("pid")
            hit_key = None
            for k, env in self._mock_store.items():
                if str(env.get("id")) == str(pid):
                    hit_key = k
                    break
            if method == "DELETE":
                if hit_key is None:
                    return _SyntheticResponse(404, {}, "")
                del self._mock_store[hit_key]
                return _SyntheticResponse(204, {}, "")
            if method == "PUT":
                if hit_key is None:
                    return _SyntheticResponse(404, {}, "")
                payload = json.loads((body_bytes or b"{}").decode("utf-8"))
                current = self._mock_store[hit_key]["version"]["number"]
                sent = ((payload.get("version") or {}).get("number"))
                if sent != current + 1:
                    return _SyntheticResponse(
                        409, {"Content-Type": "application/json"},
                        json.dumps({"message": f"mock-version-conflict: expected {current + 1}"}))
                env = self._mock_store[hit_key]
                env["value"] = payload.get("value")
                env["version"]["number"] = sent
                return _SyntheticResponse(200, {"Content-Type": "application/json"},
                                          json.dumps(env, ensure_ascii=False))
            if method == "GET":
                if hit_key is None:
                    return _SyntheticResponse(404, {}, "")
                return _SyntheticResponse(200, {"Content-Type": "application/json"},
                                          json.dumps(self._mock_store[hit_key], ensure_ascii=False))

        return _SyntheticResponse(404, {}, "")

    def _golden_envelope(self, key: str, value: Any, version_number: int) -> Dict[str, Any]:
        """captured-golden envelope template 에 value 를 끼워 mock envelope 생성 (tie-break 확정
        — mock 이 임의 형상을 fabricate 하지 않게 골격의 1차 출처를 실 capture 로 고정)."""
        tmpl = load_shape_golden()
        env = copy.deepcopy(tmpl)
        id_type = type(tmpl["id"])
        pid = self._mock_next_id
        self._mock_next_id += 1
        env["id"] = id_type(pid) if id_type in (int, str) else pid
        env["key"] = key
        env["value"] = value
        env["version"]["number"] = version_number
        return env

    # ── retry 정책 (D7 — 429 한정 1회, status dispatch 뒤 Retry-After 파싱) ──

    def _retry_after_seconds(self, resp) -> Optional[float]:
        """Retry-After 파싱 — **status dispatch 뒤 429 분기 안에서만 호출** (P0-a).

        integer-seconds 형 우선. HTTP-date 형 (RFC 9110 §10.2.3 합법) 은 응답 `Date` 헤더
        기준으로 차분 계산 (로컬 clock 아님 — §7.4.3 clock 축). 파싱 불가 = None (fallback)."""
        raw = resp.headers.get("Retry-After")
        if raw is None:
            return None
        raw = str(raw).strip()
        if re.fullmatch(r"\d+", raw):
            return float(raw)
        try:
            target = parsedate_to_datetime(raw)
            date_hdr = resp.headers.get("Date")
            if not date_hdr:
                return None
            base = parsedate_to_datetime(str(date_hdr))
            return max(0.0, (target - base).total_seconds())
        except Exception:
            return None

    def _observe_429(self, resp, waited: Optional[float]) -> None:
        self.rate_429_count += 1
        self.rate_events.append({
            "status": 429,
            "retry_after_raw": resp.headers.get("Retry-After"),
            "wait_applied_seconds": waited,
        })
        if self.rate_429_count >= RATE_429_ABORT_THRESHOLD:
            raise RateAbortError(
                f"429 누적 {self.rate_429_count} >= {RATE_429_ABORT_THRESHOLD} — K-4 abort "
                f"(의도적 유발 실험 근접 회피)"
            )

    def _send_write(self, method: str, path: str, body_bytes: bytes, *, dry: bool,
                    intent: Optional[Dict[str, Any]] = None, kind: str = "write"):
        """write 계열 전송 (POST/PUT/DELETE) — 회계 증가는 HTTP 시도 직전 (retry loop 내부).

        retry = **429 한정 1회** (예외·타임아웃 재전송 금지 — 도달 불확정 재-PUT = 오염 증폭).
        401 = AuthAbortError 즉시 전역 abort (K-1). 429 누적 >=3 = RateAbortError (K-4)."""
        total_wait = 0.0
        attempt = 0
        while True:
            attempt += 1
            if self.accounting is not None:
                if kind == "write":
                    self.accounting.record_write_attempt(dict(intent or {}, method=method))
                else:
                    self.accounting.record_delete_attempt((intent or {}).get("label", ""))
            resp = self._perform_request(method, path, body_bytes=body_bytes, dry=dry)

            # ── status dispatch 먼저 — Retry-After 파싱은 429 분기 안에서만 (P0-a) ──
            if resp.status_code == 429:
                if attempt >= MAX_RETRY_ATTEMPTS:
                    self._observe_429(resp, waited=None)
                    return resp
                wait = self._retry_after_seconds(resp)  # 서버 Retry-After 우선 (P0-b)
                if wait is None:
                    wait = INITIAL_BACKOFF_SECONDS      # fallback 고정 backoff
                wait = min(wait, RETRY_AFTER_CLAMP_SECONDS)
                if total_wait + wait > RETRY_TOTAL_WAIT_ABORT_SECONDS:
                    self._observe_429(resp, waited=None)
                    logger.warning("429 누적 대기 상한 초과 — 재시도 포기 (도달 불확정 재전송 없음)")
                    return resp
                self._observe_429(resp, waited=wait)
                logger.info(f"429 — 서버 지시 대기 {wait}s 후 1회 재시도")
                time.sleep(wait)
                total_wait += wait
                continue

            if resp.status_code == 401:
                raise AuthAbortError("401 Unauthorized — K-1 전역 abort (재시도 0, refresh 금지)")

            return resp

    # ── 직렬화 (pre-flight 와 wire 를 동일 바이트로 고정) ──

    @staticmethod
    def _serialize(obj: Any, ascii_mode: bool = False) -> bytes:
        """요청 body 직렬화 — 기본 separator (WRAP_OVERHEAD_BYTES 산술과 짝). ascii_mode 는
        AC-4 ensure_ascii lever 측정 전용 (measurement client 경유)."""
        return json.dumps(obj, ensure_ascii=ascii_mode).encode("utf-8")

    # ── v2 public 5메서드 (§4.1) ──

    def list_properties_v2(self, page_id: str, key: Optional[str] = None,
                           dry: Optional[bool] = None) -> List[Dict[str, Any]]:
        """key resolve (`?key=`) + no-filter 전량 열거 (step R 겸용).

        pagination: `_links.next` 관측 시 추종 (상한 20 page). 추종 실패 = 부분 열거 —
        `self.last_list_partial = True` 정직 표기 (§14 #5). 실패 = PropertyResolveError
        (fail-closed — 추정치 PUT 금지, 결정 12)."""
        dry = self._is_dry_run(dry)
        self.last_list_partial = False
        params = {"key": key} if key is not None else None
        if self.accounting is not None:
            self.accounting.record_get()
        resp = self._perform_request("GET", f"/wiki/api/v2/pages/{page_id}/properties",
                                     params=params, dry=dry)
        if resp.status_code == 401:
            raise AuthAbortError("401 Unauthorized — K-1 전역 abort")
        if resp.status_code != 200:
            raise PropertyResolveError(f"property list 실패 — HTTP {resp.status_code} (fail-closed)")

        results, partial = self._parse_list_response(resp)

        # pagination 추종 (실측 확정 대상 — §14 #5): _links.next 상대경로 추종, 상한 20.
        pages_followed = 0
        body = self._safe_json(resp)
        while isinstance(body, dict) and isinstance(body.get("_links"), dict) \
                and body["_links"].get("next") and pages_followed < 20:
            next_path = body["_links"]["next"]
            if not isinstance(next_path, str) or not next_path.startswith("/"):
                self.last_list_partial = True
                break
            if self.accounting is not None:
                self.accounting.record_get()
            resp = self._perform_request("GET", next_path, dry=dry)
            if resp.status_code != 200:
                self.last_list_partial = True
                break
            more, partial2 = self._parse_list_response(resp)
            results.extend(more)
            partial = partial or partial2
            body = self._safe_json(resp)
            pages_followed += 1

        self.last_list_partial = self.last_list_partial or partial
        return results

    @staticmethod
    def _safe_json(resp) -> Any:
        try:
            return resp.json()
        except Exception:
            return None

    def _parse_list_response(self, resp) -> Tuple[List[Dict[str, Any]], bool]:
        body = self._safe_json(resp)
        if isinstance(body, dict) and isinstance(body.get("results"), list):
            return list(body["results"]), False
        if isinstance(body, list):
            return list(body), False
        raise PropertyResolveError("property list 응답 형상 미지 — fail-closed (실형상 = 실측 확정)")

    def create_property_v2(self, page_id: str, key: str, value: Any,
                           dry: Optional[bool] = None, *, enforce_budget: bool = True,
                           ascii_mode: bool = False, probe_pair_id: Optional[str] = None
                           ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """POST — version 미송신 (결정 12)."""
        dry = self._is_dry_run(dry)
        if not dry and (not self.token or not self.email):
            return False, None, _error_info("local-reject", message="Creds absent — IO-1 hard-fail")
        reject = self._budget_reject(value, enforce_budget, ascii_mode)
        if reject is not None:
            return False, None, reject
        body_bytes = self._serialize({"key": key, "value": value}, ascii_mode)
        try:
            resp = self._send_write("POST", f"/wiki/api/v2/pages/{page_id}/properties",
                                    body_bytes, dry=dry,
                                    intent={"label": f"POST {key}", "key": key, "page_id": page_id})
        except (AuthAbortError, RateAbortError, WriteCapExceeded, GoldenFixtureMissingError):
            raise
        except Exception as e:
            return False, None, _error_info("exception",
                                            message=f"{type(e).__name__}: 도달 불확정 — 재전송 금지")
        if resp.status_code in (200, 201):
            env = self._safe_json(resp)
            if not isinstance(env, dict):
                return False, None, _error_info("server-response", http_status=resp.status_code,
                                                message="성공 status 이나 envelope 파싱 불가")
            return True, env, None
        return False, None, self._error_from_response(resp, probe_pair_id)

    def update_property_v2(self, page_id: str, property_id: Any, key: str, value: Any,
                           version_number: int, dry: Optional[bool] = None, *,
                           enforce_budget: bool = True, ascii_mode: bool = False,
                           probe_pair_id: Optional[str] = None
                           ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """PUT by property-id — resolve 된 version n+1 항상 송신 (결정 12, optional 이어도 무해)."""
        dry = self._is_dry_run(dry)
        if not dry and (not self.token or not self.email):
            return False, None, _error_info("local-reject", message="Creds absent — IO-1 hard-fail")
        reject = self._budget_reject(value, enforce_budget, ascii_mode)
        if reject is not None:
            return False, None, reject
        body_bytes = self._serialize(
            {"key": key, "value": value, "version": {"number": version_number}}, ascii_mode)
        try:
            resp = self._send_write(
                "PUT", f"/wiki/api/v2/pages/{page_id}/properties/{property_id}",
                body_bytes, dry=dry,
                intent={"label": f"PUT {key}", "key": key, "page_id": page_id})
        except (AuthAbortError, RateAbortError, WriteCapExceeded, GoldenFixtureMissingError):
            raise
        except Exception as e:
            return False, None, _error_info("exception",
                                            message=f"{type(e).__name__}: 도달 불확정 — 재전송 금지")
        if resp.status_code == 200:
            env = self._safe_json(resp)
            if not isinstance(env, dict):
                return False, None, _error_info("server-response", http_status=resp.status_code,
                                                message="성공 status 이나 envelope 파싱 불가")
            return True, env, None
        return False, None, self._error_from_response(resp, probe_pair_id)

    def remove_property_v2(self, page_id: str, property_id: Any,
                           dry: Optional[bool] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """DELETE by property-id (cleanup — cap 밖 별도 집계, 404 = already gone 성공 처리)."""
        dry = self._is_dry_run(dry)
        if not dry and (not self.token or not self.email):
            return False, _error_info("local-reject", message="Creds absent — IO-1 hard-fail")
        try:
            resp = self._send_write(
                "DELETE", f"/wiki/api/v2/pages/{page_id}/properties/{property_id}",
                b"", dry=dry, intent={"label": f"DELETE id={property_id}"}, kind="delete")
        except (AuthAbortError, RateAbortError, GoldenFixtureMissingError):
            raise
        except Exception as e:
            return False, _error_info("exception", message=f"{type(e).__name__}")
        if resp.status_code in (200, 204, 404):
            return True, None
        return False, self._error_from_response(resp)

    def upsert_property_v2(self, page_id: str, key: str, value: Any,
                           dry: Optional[bool] = None
                           ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """upsert 오케스트레이터 (§3.2 flow) — GET ?key= resolve → 부재 POST / 존재 PUT n+1."""
        return self._upsert_impl(page_id, key, value, dry=dry)

    def _upsert_impl(self, page_id: str, key: str, value: Any, *, dry: Optional[bool] = None,
                     enforce_budget: bool = True, ascii_mode: bool = False,
                     probe_pair_id: Optional[str] = None
                     ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        dry = self._is_dry_run(dry)
        if not dry and (not self.token or not self.email):
            # IO-1: hard-fail on creds absence (HTTP 0회 — origin 은 반드시 local-reject)
            logger.error("IO-1 HARD-FAIL: Creds absent, rejecting write")
            return False, None, _error_info("local-reject", message="Creds absent — IO-1 hard-fail")

        # resolve (실패 = 추정치 PUT 금지 fail-closed — 결정 12)
        try:
            envs = self.list_properties_v2(page_id, key=key, dry=dry)
        except (AuthAbortError, RateAbortError, GoldenFixtureMissingError):
            raise
        except PropertyResolveError as e:
            return False, None, _error_info("server-response",
                                            message=f"resolve 실패 — PUT 거부 (fail-closed): {e}")
        except Exception as e:
            return False, None, _error_info("exception",
                                            message=f"resolve 실패 — PUT 거부 (fail-closed): {type(e).__name__}")

        if len(envs) == 0:
            return self.create_property_v2(page_id, key, value, dry=dry,
                                           enforce_budget=enforce_budget, ascii_mode=ascii_mode,
                                           probe_pair_id=probe_pair_id)
        if len(envs) > 1:
            return False, None, _error_info(
                "server-response",
                message=f"key resolve 다중({len(envs)}) — fail-closed (중복 생성 방지)")

        env = envs[0]
        version = ((env.get("version") or {}).get("number"))
        if not isinstance(version, int):
            return False, None, _error_info(
                "server-response", message="resolve envelope 에 version.number 부재 — 추정치 PUT 금지")
        ok, new_env, err = self.update_property_v2(
            page_id, env.get("id"), key, value, version_number=version + 1, dry=dry,
            enforce_budget=enforce_budget, ascii_mode=ascii_mode, probe_pair_id=probe_pair_id)

        # version 충돌 시 재-resolve 1회 후 실패면 종결 (재시도 storm 금지 — 결정 12)
        if not ok and err is not None and err.get("http_status") == 409:
            try:
                envs2 = self.list_properties_v2(page_id, key=key, dry=dry)
            except Exception:
                return False, None, err
            if len(envs2) == 1:
                env2 = envs2[0]
                version2 = ((env2.get("version") or {}).get("number"))
                if isinstance(version2, int):
                    return self.update_property_v2(
                        page_id, env2.get("id"), key, value, version_number=version2 + 1,
                        dry=dry, enforce_budget=enforce_budget, ascii_mode=ascii_mode,
                        probe_pair_id=probe_pair_id)
            return False, None, err

        return ok, new_env, err

    # ── 내부 helpers ──

    def _budget_reject(self, value: Any, enforce_budget: bool,
                       ascii_mode: bool) -> Optional[Dict[str, Any]]:
        if not enforce_budget:
            return None
        try:
            encoded = self._serialize(value, ascii_mode)
        except Exception as e:
            return _error_info("local-reject", message=f"JSON encode 실패: {type(e).__name__}")
        if len(encoded) > BUDGET_BYTES:
            return _error_info("local-reject", classified_as="over-limit",
                               message=f"Over budget ({len(encoded)} > {BUDGET_BYTES}) — pre-flight")
        return None

    def _error_from_response(self, resp, probe_pair_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            text = resp.text or ""
        except Exception:
            text = ""
        status = resp.status_code
        if is_over_limit_error(2, status, text):
            classified = "over-limit"
        elif status == 400:
            classified = "malformed"
        else:
            classified = "other"
        return _error_info("server-response", http_status=status, body_text=text,
                           classified_as=classified, probe_pair_id=probe_pair_id)

    # ── leg-B chunk-store orchestration (manifest-last 원자성, IO-6) ──

    def _put_one(self, page_id: str, remote_key: str, value: Any,
                 dry: bool) -> Tuple[bool, Optional[str]]:
        """단일 property upsert — live·dry 동일 오케스트레이션 (dry 는 golden-mock transport 경유
        — GET-resolve 분기·version n+1 이 dry 에서도 실제 행사됨, DR-P1-5)."""
        ok, _env, err = self._upsert_impl(page_id, remote_key, value, dry=dry)
        if ok:
            return True, None
        return False, (err or {}).get("message") or f"HTTP {(err or {}).get('http_status')}"

    def _get_one(self, page_id: str, remote_key: str, dry: bool) -> Optional[Any]:
        """단일 property 조회 → `_unwrap_property` SSOT 통과 (live·dry 공통 — CR-C2)."""
        envs = self.list_properties_v2(page_id, key=remote_key, dry=dry)
        if len(envs) == 0:
            return None
        if len(envs) > 1:
            raise ChunkStoreError(f"key resolve 다중({len(envs)}) — {remote_key} (fail-closed)")
        return _unwrap_property(envs[0])

    def _purge_stale_chunks(self, page_id: str, new_chunk_count: int, dry: bool) -> List[str]:
        """store 진입 전 stale-chunk 선소거 (I-1) — `codeforge.sync.canonical.__chunk_k`
        (k >= 신 chunk_count) 잔존분 DELETE (유령 chunk 오염 차단). 실패 = fail-closed."""
        chunk_prefix = f"{PROPERTY_KEY_PREFIX}.__chunk_"
        try:
            envs = self.list_properties_v2(page_id, dry=dry)
        except (AuthAbortError, RateAbortError, GoldenFixtureMissingError):
            raise
        except Exception as e:
            raise ChunkStoreError(f"stale-chunk 열거 실패 — store 거부 (유령 chunk 위험): {e}") from e
        purged: List[str] = []
        for env in envs:
            key = env.get("key") or ""
            if not key.startswith(chunk_prefix):
                continue
            suffix = key[len(chunk_prefix):]
            if not suffix.isdigit():
                continue
            if int(suffix) >= new_chunk_count:
                ok, err = self.remove_property_v2(page_id, env.get("id"), dry=dry)
                if not ok:
                    raise ChunkStoreError(f"stale-chunk 소거 실패 — {key}: {err} (fail-closed)")
                purged.append(key)
        return purged

    def store_chunked_property(self, page_id: str, chunk_dict: Dict[str, Any],
                               dry_run: Optional[bool] = None) -> Dict[str, Any]:
        """chunk dict 를 leg-B 로 저장 — **전 __chunk_{n} upsert 후 마지막에 __manifest upsert**
        (manifest-last commit-marker 원자성, IO-6). 공개 시그니처 = CFP-2829 원판 무변경.

        입력 chunk_dict = confluence_property_chunking.chunk() 산출이며, 예산 계약(D3)상
        chunk() 는 `budget=effective_chunk_budget()` 로 호출돼 있어야 한다 (wrap 후에도
        BUDGET_BYTES 이내 — 불변식은 D-5 산술 테스트가 고정).

        dry_run: None → IO-7(TEST_PAGE_ID 부재 시 dry-run). dry 경로는 golden-mock transport
        경유라 captured-golden 부재 시 GoldenFixtureMissingError (명시 에러 — skip 금지).
        return: {"success", "dry_run", "put_order", "chunk_count", "stale_purged"}
        raise: ChunkStoreError — chunk 누락 / upsert 실패 (부분 저장 방지, fail-closed).
        """
        from lib.confluence_property_chunking import (
            MANIFEST_KEY as _LOCAL_MANIFEST_KEY, chunk_key as _local_chunk_key,
        )

        if not isinstance(chunk_dict, dict) or _LOCAL_MANIFEST_KEY not in chunk_dict:
            raise ChunkStoreError(
                f"chunk_dict 에 {_LOCAL_MANIFEST_KEY} 부재 — store 거부 (fail-closed)"
            )
        manifest = chunk_dict[_LOCAL_MANIFEST_KEY]
        if not isinstance(manifest, dict) or "chunk_count" not in manifest:
            raise ChunkStoreError("manifest 형식 오류 (chunk_count 부재) — store 거부 (fail-closed)")
        chunk_count = manifest["chunk_count"]

        dry = self._is_dry_run(dry_run)

        # 0) stale-chunk 선소거 (I-1 — 유령 chunk 오염 차단)
        stale_purged = self._purge_stale_chunks(page_id, chunk_count, dry)

        put_order: List[str] = []

        # 1) 전 __chunk_{n} upsert (0-based ordered) — manifest 이전에 모두 완료.
        for n in range(chunk_count):
            lkey = _local_chunk_key(n)
            if lkey not in chunk_dict:
                raise ChunkStoreError(f"chunk 누락 — {lkey} (부분 store 방지, fail-closed)")
            remote_key = CHUNK_KEY_TEMPLATE.format(n=n)
            ok, err = self._put_one(page_id, remote_key, {"data": chunk_dict[lkey]}, dry)
            if not ok:
                raise ChunkStoreError(
                    f"chunk PUT 실패 — {remote_key}: {err} (manifest 미커밋 상태 유지, reader fail-closed)"
                )
            put_order.append(remote_key)

        # 2) 마지막에 __manifest upsert — commit marker (IO-6 manifest-last 원자성).
        ok, err = self._put_one(page_id, MANIFEST_KEY, manifest, dry)
        if not ok:
            raise ChunkStoreError(
                f"manifest PUT 실패 — {err} (chunk orphaned; manifest 부재로 reader fail-closed 유지)"
            )
        put_order.append(MANIFEST_KEY)

        return {
            "success": True,
            "dry_run": dry,
            "put_order": put_order,
            "chunk_count": chunk_count,
            "stale_purged": stale_purged,
        }

    def load_chunked_property(self, page_id: str,
                              dry_run: Optional[bool] = None) -> bytes:
        """leg-B 저장 property 를 조회해 canonical bytes 로 재조립 (fail-closed, IO-6).

        __manifest resolve → chunk_count 만큼 __chunk_{n} resolve → local dict 재구성 →
        confluence_property_chunking.reassemble() 위임 (per-chunk sha256 + total_sha256 전수 검증).
        전 조회가 envelope → `_unwrap_property` SSOT 를 통과한다 (CR-C2 — live·dry 동일 경로).
        """
        from lib.confluence_property_chunking import (
            MANIFEST_KEY as _LOCAL_MANIFEST_KEY, chunk_key as _local_chunk_key,
            reassemble as _reassemble, ChunkIntegrityError as _ChunkIntegrityError,
        )

        dry = self._is_dry_run(dry_run)

        manifest = self._get_one(page_id, MANIFEST_KEY, dry)
        if manifest is None:
            raise ChunkStoreError(
                "manifest 부재 (__manifest) — 부분 데이터 재조립 거부, 노출 0 (IO-6 fail-closed)"
            )
        if not isinstance(manifest, dict) or not isinstance(manifest.get("chunk_count"), int):
            raise ChunkStoreError("manifest 형식 오류 (chunk_count) — fail-closed")
        chunk_count = manifest["chunk_count"]

        local: Dict[str, Any] = {_LOCAL_MANIFEST_KEY: manifest}
        for n in range(chunk_count):
            remote_key = CHUNK_KEY_TEMPLATE.format(n=n)
            stored = self._get_one(page_id, remote_key, dry)
            if stored is None or not isinstance(stored, dict) or "data" not in stored:
                raise ChunkStoreError(f"chunk 부재/형식 오류 — {remote_key} (부분 데이터, fail-closed)")
            local[_local_chunk_key(n)] = stored["data"]

        try:
            return _reassemble(local)   # chunking 모듈 전수 무결성 검증 (fail-closed 위임)
        except _ChunkIntegrityError as e:
            raise ChunkStoreError(f"reassemble 무결성 실패 — {e} (fail-closed)") from e


# ── Public API (leg B) ───────────────────────────────────────────────────────

def create_rest_client(base_url: str,
                       accounting: Optional[WriteAccounting] = None) -> ConfluencePropertyREST:
    """
    Factory: create REST client with env-loaded creds.

    accounting: measure.py 소유 WriteAccounting 주입 (없으면 회계 미집계 — 측정 run 은 필수 주입).
    """
    token, email = _get_creds()
    return ConfluencePropertyREST(base_url, token, email, accounting=accounting)
