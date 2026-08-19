#!/usr/bin/env python3
"""
scripts/lib/check_consumer_asset_currency.py
CFP-2978 / ADR-176 — consumer 배포 자산 currency(최신성) 검출 게이트 SSOT

목적:
  consumer repo 에 vendoring 된 wrapper 소유 자산이 정본(SSOT) 대비 뒤처졌는지를
  **서로 직교하는 두 질의**로 판정한다 (Change Plan §3.4 "질의 분할").

    Q1 (로컬 · 네트워크 0)   : pin 의 blob_sha  ↔  `git rev-parse HEAD:<path>`
    Q2 (상류 · 디렉토리 1콜) : pin 의 blob_sha  ↔  wrapper PUBLIC repo 의 정본 blob sha

  상류 도달이 실패해도 Q1 검출력은 무조건 생존한다. 부분 적용(사본만 갱신 /
  pin 만 갱신)은 Q1 만으로 로컬에서 완결 판정된다.

런타임 전제 (consumer self-hosted 러너 배포면 — Change Plan §3.3, 비협상):
  python3 (하한 3.10) **stdlib only** + git + curl.
  PyYAML / gh / yq / uv / 그 밖 서드파티 **금지** — 러너 이미지에 부재.

비교자 (Change Plan §3.4):
  `git rev-parse HEAD:<path>` = 커밋 트리 직독 → checkout 필터(CRLF) 무관이며
  REST contents 응답의 `.sha` 와 **동일 git blob SHA-1**.
  ★`git hash-object` 금지 — 필터 의존이라 `.gitattributes` 없는 consumer 에서 불안정.
  ★scope 한계 (정직 기재): HEAD(커밋 상태) 기준이므로 **미커밋 로컬 수정은 미검출**이다.
    CI 는 커밋 상태를 체크아웃하므로 CI 정의역에서는 무해하나, 로컬 수동 실행 시
    작업트리 편집분은 이 게이트의 관측면 밖이다.

상류 채널 (Change Plan §3.3 — SecurityArch E-3/E-4):
  **디렉토리-listing contents API 단일 채널**. 파일-단위 채널 금지.
  파일 단위 응답은 `content`(base64 전문)를 반드시 포함하므로 "실행 안 함"이 *정책*에
  그친다. 디렉토리 listing entry 에는 `content` 키 자체가 부재하므로
  **"받지 않은 것은 실행될 수 없다"가 구조적 사실**이 된다.
  본 파일은 그 사실을 정책이 아니라 **코드 형태**로 못박는다 — `_project_entry()` 가
  파싱 직후 4키(`sha`/`name`/`path`/`type`)만 투영하고 나머지 전량을 폐기한다.

공급망 금지 7항 (Change Plan §7.3 — 리뷰 grep 대상) 준수 형태:
  ① `content`/`download_url`/`git_url`/`_links` 키 미소비 → `_project_entry()` 4키 투영
  ② 응답 바이트를 파일로 write 하지 않음 (tempfile 포함 — 본 파일에 write 경로 0)
  ③ exec/eval/compile/importlib/subprocess 인자에 원격 유래 값 금지
     (subprocess 인자는 pin 유래 로컬 경로뿐이며 그조차 `_asset_path_ok()` 통과분)
  ④ 원격 `sha` 를 경로·명령 성분으로 쓰지 않음 (비교 대상 문자열로만 소비)
  ⑤ 소비 직전 `^[0-9a-f]{40}$` 검증 후에만 사용, 불일치 = UNDECIDABLE(degrade)
  ⑥ raw.githubusercontent.com / download_url 2차 요청 금지 (요청 사이트 1곳)
  ⑦ 리다이렉트 비추종 — `_NoRedirect` 핸들러
  ⇒ 원격 → 프로세스 총 유입 = 40-hex 문자열 N개 + 파일명 문자열이며 그 값 공간에
    실행 가능한 형태가 없다.

출력 유출 통제 (Change Plan §7.5 L-1~L-5):
  L-1 stdout = **고정 스키마 whitelist**. 원격 응답 본문·에러 본문 free-text 를
      출력 경로에 태우지 않는다 (마스킹이 필요 없도록 값 공간을 좁히는 정공법).
  L-2 예외는 잡아서 enum 으로 강등 — traceback·예외 메시지를 stderr 로 흘리지 않는다.
  L-3 자격증명을 URL 에 넣지 않는다 (header-only).
  L-4 요청 헤더 echo / verbose dump 없음.
  ★`x-ratelimit-reset` 은 원격 통제 문자열이므로 `^[0-9]{1,12}$` 통과분만 emit 한다.

exit 계약 (2-tier — 센티널 관례 답습, 신규 의미 발명 0):
  0 : 판정 완료(`in-sync` / `drifted` / `not-applicable`) **또는** honest-degrade
  2 : SETUP error — stderr JSON `error_kind`
      pin_missing / pin_schema_invalid / empty_assets_without_ssot_role /
      not_a_git_repo / internal(§7.5 L-2 강등 종착 — traceback 유출 차단)
  ★drift 를 exit 로 표현하지 않는다. verdict 는 payload 에 싣는다.
    warning-tier 라 exit 는 어차피 흡수되며, exit 에 실으면 §4.1 E1(rc 단독 판정 금지)
    위반이다.

run-marker (Change Plan §4.2 P-3 결속):
  stdout **첫 줄** = `[consumer-asset-currency] determined=<bool> verdict=<enum> assets=<int>`
  workflow 는 별 step 에서 이 마커 **부재를 FAIL** 로 판정한다 → 사본 삭제·조기 exit 0 이
  초록이 아니라 마커부재 FAIL 이 된다 (fail-open → fail-closed).
  ★해석 declare (계약 문면의 애매점 2건 — 발명이 아니라 문면 적용 규칙):
    (a) exit 2(SETUP error) 경로에는 마커를 내지 않는다. 마커 문법이 verdict enum 을
        요구하는데 SETUP error 는 verdict 이전에 종결하며, 여기서 마커를 내면
        "마커 존재 = 건강"으로 읽혀 rc=2 가 흡수될 수 있다. 마커 부재 → assert step
        FAIL → RED 가 정확한 fail-closed 방향이다 (INV-5: "읽지 못함"의 종결은
        exit 0 이 아니다).
    (b) degrade 경로의 마커는 `determined=false` 로 표기한다. payload 의
        **`determined` 키 부재**(기계 계약 — INV-1 통행증은 `determined == true` 뿐)와
        모순이 아니다: 마커는 상태 전역에서 전사(total)여야 하는 사람/CI 1줄 렌더이고,
        `determined=false` 역시 통행증이 아니다. payload 키 부재는 grep 정의역이
        다르다(`"determined":` vs `determined=`).

verdict / q1 / q2 값공간:
  verdict : in-sync / drifted / not-applicable / fetch-failed
            (앞 3종 = §4.2 · fetch-failed = §8.5 ST-1 상태 — 신규 발명 아님)
  q1      : match / mismatch          (pin_sha ↔ local_sha)
  q2      : current / stale / undetermined  (pin_sha ↔ remote_sha)
  ★drift 우선 규칙: 로컬만으로 이미 확정된 drift(q1=mismatch)는 상류 degrade 가
    발생해도 verdict=`drifted` 로 남는다 — 확정된 결함 신호를 `fetch-failed` 로
    강등해 감추지 않는다. 단 degrade 이므로 `determined` 키는 여전히 부재다.

degradation 어휘 (Change Plan §3.3 InfraOp D-6):
  degrade **형상**은 정본 `scripts/lib/check_parallel_work_sentinel.py` 를 그대로 재사용한다
  — 필드명 `degradation` + 닫힌 라벨 enum + `marker` + `determined` 키 부재 + reset 병기.
  라벨 값은 3종이며 출처가 갈린다:
    api_quota_exceeded      — 정본 DEGRADATION_LABELS **verbatim 재사용**
                              (403/429 · x-ratelimit-remaining: 0)
    upstream_unreachable    — 신규 (network/DNS/TLS/timeout/기타 HTTP status)
    upstream_payload_invalid— 신규 (JSON 파싱 불능 / 형 불일치 / sha 형식 위반 / 상한 초과)
  ★신규 2종을 둔 이유 (정직 기재): 정본의 잔여 3라벨은
    `gh_command_failed` / `gh_payload_invalid` / `git_fetch_failed` 로 **채널명이 박혀**
    있는데 본 게이트의 채널은 gh 도 git fetch 도 아닌 urllib REST 다. verbatim 재사용은
    "gh 를 호출했다"는 **거짓 채널 귀속**을 CI 로그에 남긴다. 어휘 재사용 지시와
    채널 정직성이 충돌하는 지점이라 형상은 재사용하고 라벨은 채널 중립으로 두었다.
    (DeveloperPL 경유 Architect 확인 대상으로 보고서에 declare 함.)

BYPASS env: **미도입** (Change Plan §3.4). 우회로를 만들지 않는다.
상류 응답 주입 seam(mock) 도 두지 않는다 — 응답 주입 seam 은 "in-sync 로 보이게 만드는"
사실상의 bypass 표면이다. 실패 주입은 pin 의 `source_repo` 를 부재 repo 로 두는
방식(§8.3 D-1 "상류 경로를 존재하지 않는 값으로 치환")으로 외부에서 달성한다.

read-only: bump PR·코멘트·label write 없음 → 증명할 상태가 없어 구조적 멱등.
재시도·backoff: 없음 (§3.3 InfraOp D-9 — primary rate limit 에 retry-after 부재 +
  synchronize 트리거가 다음 push 를 자연 재시도로 만듦 + 공유 IP 예산 조기 소진).
  단 "인증 거부 → 익명 1회" 는 §7.4.1 행동표가 명시한 **인증 사다리 강하**이며
  동일 자격 재시도가 아니다.

외부 호출 timeout: git·HTTP 전 호출에 명시 timeout (Change Plan §8.6 — 신규 코드에만
  INV-8 적용, 정본의 timeout 비대칭 상속 금지).

Usage:
  python3 scripts/lib/check_consumer_asset_currency.py [--pin-file <path>] [--offline]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# 상수 — 값공간 SSOT
# ---------------------------------------------------------------------------
MARKER_PREFIX = "[consumer-asset-currency]"
DEFAULT_PIN_FILENAME = ".codeforge-asset-pins.json"
SCHEMA_VERSION = 1

ROLES = ("consumer", "ssot")
VERDICTS = ("in-sync", "drifted", "not-applicable", "fetch-failed")
Q1_VALUES = ("match", "mismatch")
Q2_VALUES = ("current", "stale", "undetermined")

SETUP_ERROR_KINDS = (
    "pin_missing",
    "pin_schema_invalid",
    "empty_assets_without_ssot_role",
    "not_a_git_repo",
    "internal",
)

# degrade 라벨 — 형상은 정본 DEGRADATION_LABELS 재사용, 값은 상단 docstring 참조.
DEGRADATION_LABELS = (
    "api_quota_exceeded",
    "upstream_unreachable",
    "upstream_payload_invalid",
)

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REPO_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}/[A-Za-z0-9._-]{1,100}$")
# 선두 `.` 허용 — `.github/workflows/*.yml` 류가 정당한 repo-상대 자산 경로다.
# 상위참조(`..`)·절대경로·빈 세그먼트는 `asset_path_ok()` 의 세그먼트 검사가 거부한다.
_ASSET_PATH_RE = re.compile(r"^[A-Za-z0-9._-][A-Za-z0-9._/-]{0,199}$")
_RATELIMIT_RESET_RE = re.compile(r"^[0-9]{1,12}$")

API_ROOT = "https://api.github.com"
HTTP_TIMEOUT_SEC = 15
GIT_TIMEOUT_SEC = 15
USER_AGENT = "codeforge-consumer-asset-currency"

# 응답 read 상한. **honest-ceiling**: bounded degradation 이며 "임의 입력 무해"를 뜻하지
# 않는다 (ADR-151 §결정 7 / ADR-168 §결정 16 — 무증거 resource-safety 단정 금지).
# 상한 초과 시 판정을 포기하고 degrade 한다.
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class SetupError(Exception):
    """exit 2 SETUP error 반송체. kind ∈ SETUP_ERROR_KINDS."""

    def __init__(self, message: str, kind: str) -> None:
        super().__init__(message)
        self.message = message
        self.kind = kind


# ---------------------------------------------------------------------------
# 순수 leaf — I/O · env · exit 0
# ---------------------------------------------------------------------------
def sha_ok(value) -> bool:
    """git blob SHA-1 형식 검증 (금지 7항 ⑤ — 소비 직전 게이트)."""
    return isinstance(value, str) and bool(_SHA_RE.match(value))


def repo_slug_ok(value) -> bool:
    """`owner/repo` 형식 검증 — URL 성분 주입 차단."""
    return isinstance(value, str) and bool(_REPO_SLUG_RE.match(value))


def asset_path_ok(value) -> bool:
    """repo-상대 자산 경로 검증 — 절대경로 · 상위참조 · 이상 문자 거부."""
    if not isinstance(value, str) or not _ASSET_PATH_RE.match(value):
        return False
    segments = value.split("/")
    if any(seg in ("", ".", "..") for seg in segments):
        return False
    return True


def dir_of(path: str) -> str:
    """자산 경로의 디렉토리 성분 (repo 루트 직속이면 빈 문자열)."""
    return path.rsplit("/", 1)[0] if "/" in path else ""


def marker_line(determined: bool, verdict: str, assets: int) -> str:
    """run-marker 1줄 — stdout 첫 줄 고정 문법 (§4.2 P-3)."""
    return "%s determined=%s verdict=%s assets=%d" % (
        MARKER_PREFIX,
        "true" if determined else "false",
        verdict,
        assets,
    )


def aggregate_verdict(assets_out, degraded: bool) -> str:
    """자산별 q1/q2 → 전역 verdict.

    drift 우선: 로컬로 확정된 mismatch 나 상류 대비 stale 이 하나라도 있으면
    degrade 여부와 무관하게 `drifted` 다 (확정 결함을 fetch-failed 로 감추지 않는다).
    """
    for asset in assets_out:
        if asset.get("q1") == "mismatch" or asset.get("q2") == "stale":
            return "drifted"
    if degraded:
        return "fetch-failed"
    return "in-sync"


def _project_entry(raw) -> dict:
    """상류 listing entry 를 **4키로 투영**하고 나머지 전량 폐기 (금지 7항 ①).

    `content` / `download_url` / `git_url` / `_links` 는 이 함수를 통과하지 못하므로
    프로세스 내부에 애초에 존재하지 않는다 — 정책이 아니라 형태로 봉인.
    """
    if not isinstance(raw, dict):
        return {}
    return {k: raw.get(k) for k in ("sha", "name", "path", "type")}


# ---------------------------------------------------------------------------
# 종료 helper
# ---------------------------------------------------------------------------
def _exit_setup_error(message: str, kind: str) -> None:
    """exit 2 — stderr JSON. 정본 `_exit_setup_error` 형상 답습."""
    print(
        json.dumps({"error": message, "error_kind": kind, "exit_code": 2}),
        file=sys.stderr,
    )
    sys.exit(2)


def _emit_verdict(payload: dict, marker: str) -> None:
    """exit 0 — stdout 첫 줄 = run-marker, 둘째 줄 = 고정 스키마 JSON (DR-c)."""
    print(marker)
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


# ---------------------------------------------------------------------------
# Q1 — 로컬 (네트워크 0)
# ---------------------------------------------------------------------------
def repo_root():
    """git toplevel. 비-git repo / git 부재 → None."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SEC,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
    out = proc.stdout.strip()
    return out if proc.returncode == 0 and out else None


def local_blob_sha(root: str, path: str):
    """HEAD 커밋 트리의 blob sha. 부재·실패 → None.

    `git rev-parse HEAD:<path>` = 커밋 트리 직독이라 checkout 필터(CRLF) 무관.
    파일이 HEAD 에 없으면 rc != 0 → None → 호출부에서 q1=mismatch (fail-closed 방향:
    사본 삭제가 GREEN 이 될 수 없다).
    """
    try:
        proc = subprocess.run(
            ["git", "-C", root, "rev-parse", "HEAD:%s" % path],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SEC,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
    out = proc.stdout.strip()
    if proc.returncode != 0 or not sha_ok(out):
        return None
    return out


# ---------------------------------------------------------------------------
# Q2 — 상류 (디렉토리 listing 1콜)
# ---------------------------------------------------------------------------
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """금지 7항 ⑦ — 리다이렉트 비추종. None 반환 시 urllib 이 HTTPError 로 종결."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _header_reset(headers) -> str:
    """`x-ratelimit-reset` — 원격 통제 문자열이므로 숫자 형식 통과분만 emit."""
    try:
        raw = headers.get("x-ratelimit-reset")
    except AttributeError:
        return None
    if isinstance(raw, str) and _RATELIMIT_RESET_RE.match(raw.strip()):
        return raw.strip()
    return None


def _is_quota(status: int, headers) -> bool:
    """quota 소진 판정 — 429 또는 (403 ∧ remaining == 0)."""
    if status == 429:
        return True
    if status != 403:
        return False
    try:
        remaining = headers.get("x-ratelimit-remaining")
    except AttributeError:
        remaining = None
    return isinstance(remaining, str) and remaining.strip() == "0"


def _http_get_listing(url: str, token):
    """디렉토리 listing 1회 요청. 결과 dict 반환 (예외 비전파 — §7.5 L-2 enum 강등).

    반환 키: entries(list|None) · degradation(str|None) · status_code(int|None)
             · ratelimit_reset(str|None) · auth_rejected(bool)
    """
    result = {
        "entries": None,
        "degradation": None,
        "status_code": None,
        "ratelimit_reset": None,
        "auth_rejected": False,
    }
    request = urllib.request.Request(url, method="GET")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", USER_AGENT)
    if token:
        # L-3 — 자격증명은 header-only. URL 에 넣지 않는다.
        request.add_header("Authorization", "Bearer %s" % token)

    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=HTTP_TIMEOUT_SEC) as response:
            result["status_code"] = int(getattr(response, "status", 0) or 0)
            result["ratelimit_reset"] = _header_reset(response.headers)
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as err:
        status = int(getattr(err, "code", 0) or 0)
        headers = getattr(err, "headers", None)
        result["status_code"] = status
        result["ratelimit_reset"] = _header_reset(headers)
        if _is_quota(status, headers):
            result["degradation"] = "api_quota_exceeded"
        else:
            result["degradation"] = "upstream_unreachable"
            # 401 = 자격 거부, 403(비-quota) = 자격 유래 거부 가능 → 사다리 강하 후보
            result["auth_rejected"] = status in (401, 403)
        return result
    except Exception:
        # network / DNS / TLS / timeout / redirect 차단 — 예외 본문 미전파 (L-2)
        result["degradation"] = "upstream_unreachable"
        return result

    if len(body) > MAX_RESPONSE_BYTES:
        result["degradation"] = "upstream_payload_invalid"
        return result
    try:
        parsed = json.loads(body.decode("utf-8"))
    except Exception:
        result["degradation"] = "upstream_payload_invalid"
        return result
    if not isinstance(parsed, list):
        # 디렉토리가 아닌 응답(파일 단위 dict 등) = 계약 밖 → 판정 포기.
        result["degradation"] = "upstream_payload_invalid"
        return result
    result["entries"] = [_project_entry(e) for e in parsed]
    return result


def fetch_dir_listing(repo_slug: str, dir_path: str):
    """인증 3단 사다리 — 자기 GITHUB_TOKEN → 익명 → degrade (§3.3).

    동일 자격 재시도·backoff 없음 (§3.3 InfraOp D-9). 자격 거부일 때만 1단 강하한다.
    """
    url = "%s/repos/%s/contents/%s" % (API_ROOT, repo_slug, dir_path) if dir_path \
        else "%s/repos/%s/contents" % (API_ROOT, repo_slug)

    token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    ladder = ([token] if token else []) + [None]
    result = None
    for index, credential in enumerate(ladder):
        result = _http_get_listing(url, credential)
        if result["degradation"] is None:
            return result
        if result["auth_rejected"] and index + 1 < len(ladder):
            continue  # §7.4.1 "인증 거부 → 익명 재시도 → degrade"
        return result
    return result


def remote_sha_from(entries, filename: str):
    """listing 에서 파일명 일치 entry 의 blob sha 추출.

    반환 (sha|None, invalid: bool):
      (sha, False)   정상
      (None, False)  상류에 그 파일이 **없음** — 판정 가능(= stale). degrade 아님.
      (None, True)   entry 는 있으나 sha 가 40-hex 아님 — UNDECIDABLE (금지 7항 ⑤)
    """
    for entry in entries or []:
        if entry.get("name") != filename:
            continue
        if entry.get("type") not in (None, "file"):
            continue
        sha = entry.get("sha")
        if sha_ok(sha):
            return sha, False
        return None, True
    return None, False


# ---------------------------------------------------------------------------
# pin 로드 · 스키마 검증 (전제 fail-closed — §4.3)
# ---------------------------------------------------------------------------
def load_pin(pin_path: str) -> dict:
    """pin 파일 로드. 위반 = SetupError(exit 2)."""
    if not os.path.isfile(pin_path):
        raise SetupError("asset pin file not found: %s" % pin_path, "pin_missing")
    try:
        with open(pin_path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, ValueError):
        raise SetupError("asset pin file is not readable JSON", "pin_schema_invalid")
    if not isinstance(raw, dict):
        raise SetupError("asset pin root is not an object", "pin_schema_invalid")
    return raw


def validate_pin(raw: dict) -> dict:
    """§4.3 스키마 + 불변식 검증. 위반 = SetupError(exit 2).

    반환 = {"role": str, "source_repo": str|None, "assets": [ {path, blob_sha}, ... ]}
    """
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise SetupError("schema_version must be %d" % SCHEMA_VERSION, "pin_schema_invalid")

    role = raw.get("role")
    if role not in ROLES:
        raise SetupError("role must be one of %s" % (ROLES,), "pin_schema_invalid")

    assets = raw.get("assets")
    if not isinstance(assets, list):
        raise SetupError("assets must be an array", "pin_schema_invalid")

    # ★분모 0 fail-closed — "분모 0 → PASS" 는 이 조직의 반복 결함 class 다.
    if role == "consumer" and not assets:
        raise SetupError(
            "consumer role declares zero pinned assets",
            "empty_assets_without_ssot_role",
        )

    source_repo = raw.get("source_repo")
    if assets:
        # source_repo 는 Q2 URL 성분이므로 자산이 있을 때 필수 + 형식 강제.
        if not repo_slug_ok(source_repo):
            raise SetupError("source_repo must be '<owner>/<repo>'", "pin_schema_invalid")
    elif source_repo is not None and not repo_slug_ok(source_repo):
        raise SetupError("source_repo must be '<owner>/<repo>'", "pin_schema_invalid")

    normalized = []
    for asset in assets:
        if not isinstance(asset, dict):
            raise SetupError("assets[] element is not an object", "pin_schema_invalid")
        path = asset.get("path")
        if not asset_path_ok(path):
            raise SetupError("assets[].path is not a valid repo-relative path",
                             "pin_schema_invalid")
        blob_sha = asset.get("blob_sha")
        if not sha_ok(blob_sha):
            raise SetupError("assets[].blob_sha must match ^[0-9a-f]{40}$",
                             "pin_schema_invalid")
        for field in ("pinned_at", "pinned_by_story"):
            value = asset.get(field)
            if not isinstance(value, str) or not value.strip():
                raise SetupError("assets[].%s must be a non-empty string" % field,
                                 "pin_schema_invalid")
        normalized.append({"path": path, "blob_sha": blob_sha})

    return {"role": role, "source_repo": source_repo, "assets": normalized}


# ---------------------------------------------------------------------------
# 판정
# ---------------------------------------------------------------------------
def evaluate(pin: dict, root: str, offline: bool) -> dict:
    """Q1 ⊥ Q2 수행 후 payload 조립. 반환 = {"payload": dict, "marker": str}."""
    assets_out = []
    degradation = None
    status_code = None
    ratelimit_reset = None
    listing_cache = {}

    for asset in pin["assets"]:
        path = asset["path"]
        pin_sha = asset["blob_sha"]
        local_sha = local_blob_sha(root, path)

        remote_sha = None
        q2 = "undetermined"
        if not offline:
            directory = dir_of(path)
            if directory not in listing_cache:
                listing_cache[directory] = fetch_dir_listing(pin["source_repo"], directory)
            fetched = listing_cache[directory]
            if fetched["degradation"] is not None:
                if degradation is None:
                    degradation = fetched["degradation"]
                    status_code = fetched["status_code"]
                    ratelimit_reset = fetched["ratelimit_reset"]
            else:
                filename = path.rsplit("/", 1)[-1]
                remote_sha, invalid = remote_sha_from(fetched["entries"], filename)
                if invalid:
                    # sha 형식 위반 = UNDECIDABLE (금지 7항 ⑤) — GREEN 으로 흡수 금지
                    if degradation is None:
                        degradation = "upstream_payload_invalid"
                        status_code = fetched["status_code"]
                        ratelimit_reset = fetched["ratelimit_reset"]
                else:
                    # 상류에 파일이 부재해도 그것은 **판정 가능한 사실**(stale)이다.
                    q2 = "current" if remote_sha == pin_sha else "stale"

        assets_out.append({
            "path": path,
            "local_sha": local_sha,
            "pin_sha": pin_sha,
            "remote_sha": remote_sha,
            "q1": "match" if local_sha == pin_sha else "mismatch",
            "q2": q2,
        })

    degraded = degradation is not None
    verdict = aggregate_verdict(assets_out, degraded)
    marker = marker_line(not degraded, verdict, len(assets_out))

    payload = {
        "marker": marker,
        "role": pin["role"],
        "verdict": verdict,
        "assets_checked": len(assets_out),
        "assets": assets_out,
    }
    if degraded:
        # ★degrade payload = `determined` 키 **부재** + degradation 어휘 + reset 병기.
        #   "못 읽었다"를 "같다"로 흡수하지 않는다 (INV-5 / T-B2).
        payload["degradation"] = degradation
        payload["status_code"] = status_code
        payload["ratelimit_reset"] = ratelimit_reset
    else:
        payload["determined"] = True

    return {"payload": payload, "marker": marker}


def _not_applicable_result(role: str) -> dict:
    """wrapper self-app — `role: ssot` ∧ assets 0 (§3.4).

    positive 선언으로만 도달한다: pin 을 삭제하면 `pin_missing` exit 2 다.
    """
    marker = marker_line(True, "not-applicable", 0)
    payload = {
        "marker": marker,
        "determined": True,
        "role": role,
        "verdict": "not-applicable",
        "assets_checked": 0,
        "assets": [],
    }
    return {"payload": payload, "marker": marker}


# ---------------------------------------------------------------------------
# entrypoint
# ---------------------------------------------------------------------------
def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="check_consumer_asset_currency",
        description="CFP-2978 / ADR-176 consumer asset currency gate (Q1 local ⊥ Q2 upstream)",
    )
    parser.add_argument(
        "--pin-file",
        default=None,
        help="asset pin path (default: <repo root>/%s)" % DEFAULT_PIN_FILENAME,
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Q1 only — 상류 질의(Q2) 생략. 각 자산 q2 는 undetermined 로 남는다",
    )
    args = parser.parse_args(argv)

    root = repo_root()

    if args.pin_file:
        pin_path = args.pin_file
    else:
        pin_path = os.path.join(root or os.getcwd(), DEFAULT_PIN_FILENAME)

    raw = load_pin(pin_path)
    pin = validate_pin(raw)

    if not pin["assets"]:
        # 여기 도달 = role == "ssot" (consumer ∧ 0 자산은 validate_pin 이 exit 2 로 막았다)
        result = _not_applicable_result(pin["role"])
        _emit_verdict(result["payload"], result["marker"])

    if not root:
        # ★INV-5 — 대조 대상을 읽을 수 없는 상태의 종결은 exit 2 이지 exit 0 이 아니다.
        raise SetupError("not inside a git work tree", "not_a_git_repo")

    result = evaluate(pin, root, args.offline)
    _emit_verdict(result["payload"], result["marker"])


if __name__ == "__main__":
    try:
        main()
    except SetupError as setup_error:
        _exit_setup_error(setup_error.message, setup_error.kind)
    except Exception as unexpected:  # §7.5 L-2 — traceback 유출 차단 후 fail-closed
        _exit_setup_error(
            "unexpected internal failure: %s" % type(unexpected).__name__,
            "internal",
        )
