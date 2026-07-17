"""
scripts/lib/check_parallel_work_sentinel.py
CFP-967 / ADR-073 Amendment 2 — Parallel work sentinel 3 polling mode SSOT

기능:
  3 polling mode dispatch — parallel race detection mechanical wire.
  memory rule 6 (title-based search, CFP-953 incident) + rule 7 (Epic state poll,
  CFP-946 incident) + HEAD compare sibling commits (self-demo lane evidence).

Mode enum (argparse --mode):
  title-search:
    Input:  env CFP_CONTEXT (예: "CFP-967") + optional --epic-id
    Output: exit 0 + stdout JSON {"matches": [{"number": int, "title": str, "labels": [...]}]}
  epic-state-poll:
    Input:  --epic-id (required)
    Output: exit 0 + stdout JSON {"epic_state": str, "siblings": [...], "freshness_age_sec": int}
  head-compare-sibling-commits:
    Input:  env CFP_PRIOR_SHA (required) + optional --branch (default origin/main)
    Output: exit 0 + stdout JSON {"delta_commits": [...], "parallel_detected": bool}

BYPASS:
  BYPASS_PARALLEL_WORK_SENTINEL=1 — unconditional skip, exit 0 + audit marker

Graceful degradation fail-mode (DEGRADATION_LABELS 상수 렌더 — 어휘 단일 SSOT, CFP-2723):
  api_quota_exceeded:  _is_quota_evidence 단일 predicate 2채널 — rc!=0 stderr 의 앵커드
                       rate-limit 패턴(QUOTA_STDERR_PATTERNS) 매칭 또는 rc==0 payload
                       error-dict status 403/429. title→git-log fallback / epic→UNKNOWN,
                       + stderr marker + stderr_excerpt 보존
  gh_command_failed:   그 외 gh 실패 (rc!=0, 비-quota stderr) + stderr_excerpt 보존
  gh_payload_invalid:  rc==0 이나 빈/파싱불능/형 불일치/필수키 결핍 payload
  git_fetch_failed:    head-compare inline git fetch/log 실패 (본 모드 전용 — 등재만)
  (advisory tier — degradation 필드값 아님) stale_label_grace: 5min grace 경계 stderr 마커

Exit-code 2-tier (로컬 계약):
  0: PASS 또는 honest-degrade (stdout JSON degradation 필드로 식별)
  2: SETUP error (stderr JSON error_kind: gh_not_installed / gh_not_authenticated / setup)
  2 (argparse native): usage 오류 (무효 --mode 등) — stderr = argparse usage 텍스트,
     error_kind JSON 부재 (exit 2 내부 판별 = stderr 의 error_kind JSON 유무)

Test seam:
  CFP967_GH_MOCK_RESPONSE=<fixture path> — gh CLI stdout mock
  CFP967_GH_MOCK_RC=<int>                — gh CLI mock returncode (기본 "0")
  CFP967_GH_MOCK_STDERR=<str>            — gh CLI mock stderr (기본 "")
  CFP967_GH_AUTH_MOCK=fail               — _check_gh_auth 미인증 강제 (mock 모드)
  CFP967_GIT_LOG_MOCK=<fixture path>     — git log mock
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Optional

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_parallel_work_sentinel"
# Story KEY prefix 파라미터화 (CFP-2451) — consumer 전파 wire 가 동작하려면
# prefix 가 하드코딩되면 안 됨 (consumer prefix 가 "CFP" 가 아닌 곳에서 inert 검사).
# workflow 가 .claude/_overlay/project.yaml github.story_key_prefix 를 STORY_KEY_PREFIX
# env 로 주입. 미주입(wrapper self-app / overlay 부재) 시 기본값 "CFP" → wrapper 동작 무변경(하위호환).
_PREFIX = os.environ.get("STORY_KEY_PREFIX", "CFP")
KEY_PATTERN = re.compile(rf"\b{re.escape(_PREFIX)}-\d+\b")
BYPASS_ENV = "BYPASS_PARALLEL_WORK_SENTINEL"
GH_MOCK_ENV = "CFP967_GH_MOCK_RESPONSE"
GIT_LOG_MOCK_ENV = "CFP967_GIT_LOG_MOCK"
STALE_GRACE_SEC = 300  # 5min — ADR-073 §결정 1-C sustained polling

# --- CFP-2723: gh mock seam env (test-only, 신규 3종 — 기존 env 이름 6종 불변) ---
GH_MOCK_RC_ENV = "CFP967_GH_MOCK_RC"          # gh mock returncode (기본 "0")
GH_MOCK_STDERR_ENV = "CFP967_GH_MOCK_STDERR"  # gh mock stderr (기본 "")
GH_AUTH_MOCK_ENV = "CFP967_GH_AUTH_MOCK"      # "fail" → _check_gh_auth 미인증 강제

# --- CFP-2723: gh --json 필드셋 (module 상수 = (c) 검증층 python-import 추출 표면, D0) ---
GH_FIELDS_TITLE_SEARCH = "number,title,labels,closedAt"   # 무변경 (유효 필드)
GH_FIELDS_EPIC_STATE_POLL = "state,body"                  # closedBy 제거 — 실소비 2필드

# --- CFP-2723: degradation / quota 어휘 단일 선언 (docstring fail-mode 표 = 이 상수 렌더) ---
DEGRADATION_LABELS = ("api_quota_exceeded", "gh_command_failed", "gh_payload_invalid", "git_fetch_failed")
QUOTA_STDERR_PATTERNS = ("rate limit exceeded", "secondary rate limit")  # 앵커드 (AC-3 "rate limit" narrowing)
QUOTA_STATUS_CODES = ("403", "429")
MARKER_API_FAILED = "[parallel-work-sentinel-api-failed]"  # 값 불변 (기존 4사이트 산재 문자열 추출)

# D7 — gh stderr 토큰 마스킹 정규식 (classic gh[pousr]_ / fine-grained github_pat_ prefix).
#   양 branch 고정 prefix + 단순 문자 클래스. best-effort (honest-ceiling: 공식 prefix 형식 외
#   비정형 비밀 미커버 — _stderr_excerpt docstring 참조).
_TOKEN_MASK_RE = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{36,})")


# ---------------------------------------------------------------------------
# Exit helpers
# ---------------------------------------------------------------------------
def _exit_pass(payload: dict) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def _exit_setup_error(msg: str, kind: str = "setup") -> None:
    print(json.dumps({"error": msg, "error_kind": kind, "exit_code": 2}), file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Functional core — pure leaves (I/O·exit·env 0). CFP-2723 §3.1
#   의존 방향 (단방향): 분류기·파서 → _is_quota_evidence (최심 leaf). builder 호출 금지.
# ---------------------------------------------------------------------------
def _is_quota_evidence(*, stderr: str = "", payload: Any = None) -> bool:
    """quota 판정 단일 predicate — 2 evidence 채널 단일 사이트 수렴 (drift 봉인).

    ⓐ 텍스트 채널: QUOTA_STDERR_PATTERNS case-insensitive 부분문자열 매칭.
    ⓑ 구조 채널:  isinstance(payload, dict) ∧ str(payload.get("status")) ∈ QUOTA_STATUS_CODES.
    """
    if stderr:
        low = stderr.lower()
        for pat in QUOTA_STDERR_PATTERNS:
            if pat in low:
                return True
    if isinstance(payload, dict) and str(payload.get("status")) in QUOTA_STATUS_CODES:
        return True
    return False


def _classify_gh_failure(stderr: str) -> str:
    """rc!=0 경로 한정 분류 (V-4ⓐ — rc==0 텍스트 매칭 금지).

    앵커드 rate-limit 증거 → api_quota_exceeded, 그 외 → gh_command_failed (보수 default).
    """
    if _is_quota_evidence(stderr=stderr):
        return "api_quota_exceeded"
    return "gh_command_failed"


def _parse_gh_payload(
    raw: str, expect: type, required_keys: tuple[str, ...] = ()
) -> tuple[Any, Optional[str]]:
    """gh stdout 파서 (모드 간 대칭). 반환 (payload, None) 성공 / (None, defect_label).

    판정 순서: ① 빈/공백 → gh_payload_invalid ② JSONDecodeError → gh_payload_invalid
      ③ error-dict sniff (_is_quota_evidence 구조 채널) → api_quota_exceeded [F-CR-967-1 보존 이동]
      ④ not isinstance(payload, expect) → gh_payload_invalid
      ⑤ required_keys 결핍 → gh_payload_invalid ⑥ 성공.
    """
    if not raw or not raw.strip():
        return None, "gh_payload_invalid"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None, "gh_payload_invalid"
    if _is_quota_evidence(payload=payload):
        return None, "api_quota_exceeded"
    if not isinstance(payload, expect):
        return None, "gh_payload_invalid"
    for key in required_keys:
        if key not in payload:
            return None, "gh_payload_invalid"
    return payload, None


def _stderr_excerpt(stderr: str) -> str:
    """gh stderr 발췌 (D7) — 토큰 마스킹 선행 → cap 후행.

    마스킹: 공식 토큰 prefix 형식(classic gh[pousr]_ / fine-grained github_pat_) best-effort 치환.
      honest-ceiling (ADR-082 §결정 16 / ADR-151 §결정 7): best-effort defense-in-depth —
      임의 stderr 무해성 단정 아님, 공식 prefix 형식 외 비정형 비밀은 미커버 잔존 (bounded degradation).
    cap: 첫 8줄 ∧ 1024B 중 먼저 도달 (출력 payload bound).
    순서(마스킹→cap): cap 선행 시 절단 경계 토큰 분할 → 정규식 미포착 leak → 마스킹 선행이 구조적 봉인
      (검증 = self-test split-token RED 채널).
    """
    if not stderr:
        return ""
    masked = _TOKEN_MASK_RE.sub("[REDACTED]", stderr)
    capped = "\n".join(masked.splitlines()[:8])  # 첫 8줄
    encoded = capped.encode("utf-8")
    if len(encoded) > 1024:                       # 1024B cap (byte-safe decode)
        capped = encoded[:1024].decode("utf-8", errors="ignore")
    return capped


# ---------------------------------------------------------------------------
# gh CLI / git invocation helpers
# ---------------------------------------------------------------------------
def _run_gh(args: list[str], mock_env: str = GH_MOCK_ENV) -> tuple[int, str, str]:
    """Run gh CLI → (rc, stdout, stderr). CFP-2723 D6 — 3-tuple (union 선택 로직 0).

    실경로: FileNotFoundError → gh_not_installed setup error (exit 2, traceback 무노출).
    mock 경로 (CFP967_GH_MOCK_RESPONSE 존재): 3값 각각 독립 pass-through —
      rc = int(CFP967_GH_MOCK_RC, 기본 "0"; 파싱 실패 = setup error fail-loud) /
      stdout = fixture 파일 내용 / stderr = CFP967_GH_MOCK_STDERR (기본 "").
    """
    mock_path = os.environ.get(mock_env)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                stdout = f.read()
        except FileNotFoundError:
            return 2, "", json.dumps({"error": f"mock file not found: {mock_path}"})
        rc_raw = os.environ.get(GH_MOCK_RC_ENV, "0")
        try:
            rc = int(rc_raw)
        except ValueError:
            _exit_setup_error(f"invalid {GH_MOCK_RC_ENV}={rc_raw!r} (int 파싱 실패)", kind="setup")
        stderr = os.environ.get(GH_MOCK_STDERR_ENV, "")
        return rc, stdout, stderr
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        _exit_setup_error("gh CLI not installed — install: https://cli.github.com", kind="gh_not_installed")
    return result.returncode, result.stdout, result.stderr


def _run_git_log(prior_sha: str, branch: str = "origin/main") -> tuple[int, str]:
    """Run git log or return mock fixture."""
    mock_path = os.environ.get(GIT_LOG_MOCK_ENV)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                return 0, f.read()
        except FileNotFoundError:
            return 2, f"mock file not found: {mock_path}"
    # git fetch origin first (sustained polling §결정 1-C)
    subprocess.run(["git", "fetch", "origin"], capture_output=True)
    result = subprocess.run(
        ["git", "log", "--format=%H %ci %s", f"{prior_sha}..{branch}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout


def _check_gh_auth() -> Optional[str]:
    """gh CLI auth 확인. None=OK / "gh_not_installed" / "gh_not_authenticated". CFP-2723 §3.1.

    mock (CFP967_GH_MOCK_RESPONSE 존재): CFP967_GH_AUTH_MOCK=="fail" → "gh_not_authenticated",
      그 외 None (기존 skip 동작 보존). 실경로: FileNotFoundError → "gh_not_installed" / rc!=0 →
      "gh_not_authenticated". 출력(stdout/stderr)은 기존대로 폐기 (§7.3 — auth status 비보존).
    """
    if os.environ.get(GH_MOCK_ENV):
        if os.environ.get(GH_AUTH_MOCK_ENV) == "fail":
            return "gh_not_authenticated"
        return None
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return "gh_not_installed"
    if result.returncode != 0:
        return "gh_not_authenticated"
    return None


# ---------------------------------------------------------------------------
# Mode: title-search (memory rule 6 — CFP-953 incident carrier)
# ---------------------------------------------------------------------------
def mode_title_search(epic_id: Optional[str] = None) -> None:
    """
    title-search mode: gh issue list --search in:title + whole-word CFP regex filter.
    Carrier: memory rule 6 (title-based search 의무, CFP-953 label-based search miss incident).
    """
    err = _check_gh_auth()
    if err:
        _exit_setup_error(
            "gh CLI not installed — install: https://cli.github.com" if err == "gh_not_installed"
            else "gh CLI not authenticated — run: gh auth login",
            kind=err,
        )

    cfp_context = os.environ.get("CFP_CONTEXT", "")
    search_fragment = cfp_context if cfp_context else ""

    # Build gh issue list args
    gh_args = [
        "issue", "list",
        "--search", f'"{search_fragment}" in:title' if search_fragment else f"{_PREFIX}- in:title",
        "--state", "all",
        "--json", GH_FIELDS_TITLE_SEARCH,
        "--limit", "50",
    ]

    rc, stdout, stderr = _run_gh(gh_args)

    if rc != 0:
        _degrade_title_search(_classify_gh_failure(stderr), search_fragment, _stderr_excerpt(stderr))
        return

    payload, defect = _parse_gh_payload(stdout, list)
    if defect:
        # 의도적 동작 변경 1건: non-list/비-error-dict payload 의 침묵 빈 matches → degrade (성공 위장 해소).
        # error-dict(status 403/429)는 _parse_gh_payload 가 api_quota_exceeded 로 sniff (F-CR-967-1 보존 이동).
        _degrade_title_search(defect, search_fragment, _stderr_excerpt(stderr))
        return
    issues = payload

    # whole-word regex filter (CFP-953 false-positive 차단)
    matches = []
    for issue in issues:
        title = issue.get("title", "")
        number = issue.get("number", 0)
        labels = [lbl.get("name", "") if isinstance(lbl, dict) else str(lbl) for lbl in issue.get("labels", [])]
        if search_fragment and not KEY_PATTERN.search(title):
            # If context given, ensure title has a <PREFIX>-\d+ pattern
            continue
        matches.append({"number": number, "title": title, "labels": labels})

    _exit_pass({"matches": matches})


# ---------------------------------------------------------------------------
# Mode: epic-state-poll (memory rule 7 — CFP-946 incident carrier)
# ---------------------------------------------------------------------------
def mode_epic_state_poll(epic_id: str) -> None:
    """
    epic-state-poll mode: fetch Epic state + siblings from scope_manifest.
    Carrier: memory rule 7 (Epic 진행 중 polling 의무, CFP-946 Epic close miss incident).
    """
    err = _check_gh_auth()
    if err:
        _exit_setup_error(
            "gh CLI not installed — install: https://cli.github.com" if err == "gh_not_installed"
            else "gh CLI not authenticated — run: gh auth login",
            kind=err,
        )

    gh_args = [
        "issue", "view", str(epic_id),
        "--json", GH_FIELDS_EPIC_STATE_POLL,
    ]

    rc, stdout, stderr = _run_gh(gh_args)
    context = f"epic#{epic_id}"

    if rc != 0:
        _degrade_epic_state_poll(_classify_gh_failure(stderr), context, _stderr_excerpt(stderr))
        return

    payload, defect = _parse_gh_payload(stdout, dict, required_keys=("state",))
    if defect:
        # error-dict(status 403/429)는 _parse_gh_payload 가 api_quota_exceeded 로 sniff (title 대칭).
        # list/non-JSON/빈/필수키 결핍 → gh_payload_invalid (AttributeError·성공 위장 봉인).
        _degrade_epic_state_poll(defect, context, _stderr_excerpt(stderr))
        return

    epic_state = payload.get("state", "UNKNOWN")
    body = payload.get("body") or ""  # present-null 정규화 (F-CR-2723-1): "body": null → None → "" (findall(None) TypeError 봉인, INV-4)

    # Parse scope_manifest from Epic body (<!-- scope_manifest --> block)
    siblings = _parse_siblings_from_body(body)

    # Freshness: current time vs last fetch (session cache stale assumption §결정 1-C)
    freshness_age_sec = 0  # real-time fetch — age = 0

    _exit_pass({
        "epic_state": epic_state,
        "siblings": siblings,
        "freshness_age_sec": freshness_age_sec,
    })


def _parse_siblings_from_body(body: str) -> list[dict]:
    """Extract sibling Story references from Epic body scope_manifest block."""
    siblings = []
    # Look for <!-- scope_manifest --> block or plain <PREFIX>-\d+ references
    cfp_matches = KEY_PATTERN.findall(body)
    seen = set()
    for cfp_ref in cfp_matches:
        if cfp_ref not in seen:
            seen.add(cfp_ref)
            siblings.append({"cfp": cfp_ref})
    return siblings


# ---------------------------------------------------------------------------
# Mode: head-compare-sibling-commits (self-demo lane evidence)
# ---------------------------------------------------------------------------
def mode_head_compare(branch: str = "origin/main") -> None:
    """
    head-compare-sibling-commits mode: git log delta + parallel branch detection.
    """
    prior_sha = os.environ.get("CFP_PRIOR_SHA", "")
    if not prior_sha:
        _exit_setup_error(
            "CFP_PRIOR_SHA env var required for head-compare-sibling-commits mode"
        )

    rc, raw = _run_git_log(prior_sha, branch)

    if rc != 0:
        # git fetch/log failure — graceful degradation
        print(
            json.dumps({
                "delta_commits": [],
                "parallel_detected": False,
                "degradation": "git_fetch_failed",
                "marker": "[parallel-work-sentinel-api-failed]",
            })
        )
        sys.exit(0)

    delta_commits = []
    parallel_detected = False

    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split(" ", 2)
        sha = parts[0] if len(parts) > 0 else ""
        ci = parts[1] if len(parts) > 1 else ""
        msg = parts[2] if len(parts) > 2 else ""
        delta_commits.append({"sha": sha, "time": ci, "msg": msg})
        # parallel detection: any commit message containing <PREFIX>-\d+ pattern
        if KEY_PATTERN.search(msg):
            parallel_detected = True

    # stale_label_grace: check if prior_sha is older than STALE_GRACE_SEC
    _check_stale_grace(prior_sha)

    _exit_pass({
        "delta_commits": delta_commits,
        "parallel_detected": parallel_detected,
    })


def _check_stale_grace(prior_sha: str) -> None:
    """Check if prior_sha timestamp is older than STALE_GRACE_SEC — emit marker if stale."""
    # F-CR-967-2: skip stale check in mock-context (CFP967_GIT_LOG_MOCK set) to prevent
    # fixture SHA age false-positive stderr pollution (existing mock seam pattern — ADR-061).
    if os.environ.get(GIT_LOG_MOCK_ENV):
        return None
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ci", "-1", prior_sha],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0 or not result.stdout.strip():
            return
        # timestamp check via python datetime
        from datetime import datetime, timezone
        ts_str = result.stdout.strip()
        # git log format: "2026-05-19 01:00:00 +0900"
        # normalize to parseable format
        ts_str_norm = ts_str.replace(" +", "+").replace(" -", "-")
        parts = ts_str.rsplit(" ", 1)
        if len(parts) == 2:
            dt_str, tz_str = parts
            # simple epoch via git show --format=%ct
            result2 = subprocess.run(
                ["git", "log", "--format=%ct", "-1", prior_sha],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result2.returncode == 0 and result2.stdout.strip():
                commit_epoch = int(result2.stdout.strip())
                now_epoch = int(time.time())
                age_sec = now_epoch - commit_epoch
                if age_sec > STALE_GRACE_SEC:
                    print(
                        f"[parallel-work-poll-freshness-mismatch] prior_sha={prior_sha} "
                        f"age={age_sec}s > {STALE_GRACE_SEC}s grace — verify-before-trust step required",
                        file=sys.stderr,
                    )
    except Exception:
        pass  # graceful — stale check advisory only


# ---------------------------------------------------------------------------
# Graceful degradation builders (mode-owned, side-effectful). CFP-2723 §3.1
# ---------------------------------------------------------------------------
def _emit_degrade_marker(mode: str, context: str) -> None:
    """degrade 2줄 stderr 마커 공용 발화 (WARNING + MARKER_API_FAILED, 값 불변)."""
    print(
        f"[parallel-work-sentinel] WARNING: gh API call failed for mode={mode} context={context}.",
        file=sys.stderr,
    )
    print(MARKER_API_FAILED, file=sys.stderr)


def _degrade_title_search(label: str, context: str, stderr_excerpt: str = "") -> None:
    """title-search honest-degrade — 마커 → git-log -50 fallback → matches 스키마 보존 → exit 0."""
    _emit_degrade_marker("title-search", context)
    # Local fallback: git log -50 | grep <PREFIX>-\d+ (KEY_PATTERN 경유 유지 = CFP-2451)
    try:
        result = subprocess.run(
            ["git", "log", "-50", "--format=%s"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            cfp_refs = []
            for line in result.stdout.splitlines():
                cfp_refs.extend(KEY_PATTERN.findall(line))
            print(
                json.dumps({
                    "matches": [{"cfp": ref} for ref in set(cfp_refs)],
                    "degradation": label,
                    "marker": MARKER_API_FAILED,
                    "fallback": "local git log -50 grep",
                    "stderr_excerpt": stderr_excerpt,
                })
            )
            sys.exit(0)
    except Exception:
        pass  # graceful — git 부재/오류 시 last-resort 로 fall-through (traceback 무노출)

    # Last resort — empty response, non-blocking
    print(
        json.dumps({
            "matches": [],
            "degradation": label,
            "marker": MARKER_API_FAILED,
            "fallback": "unavailable",
            "stderr_excerpt": stderr_excerpt,
        })
    )
    sys.exit(0)


def _degrade_epic_state_poll(label: str, context: str, stderr_excerpt: str = "") -> None:
    """epic-state-poll honest-degrade — 마커 → subprocess 0 (git-log 미실행, AC-6 무관 CFP 비주입) →
    계약 3키(epic_state UNKNOWN / siblings [] / freshness_age_sec 0) payload → exit 0."""
    _emit_degrade_marker("epic-state-poll", context)
    print(
        json.dumps({
            "epic_state": "UNKNOWN",
            "siblings": [],
            "freshness_age_sec": 0,
            "degradation": label,
            "marker": MARKER_API_FAILED,
            "stderr_excerpt": stderr_excerpt,
        })
    )
    sys.exit(0)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (ADR-024 hotfix-bypass family, audit-trailed)
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            json.dumps({
                "bypass": True,
                "marker": "[hotfix-bypass] BYPASS_PARALLEL_WORK_SENTINEL=1 invoked",
                "audit_comment": "bypass invoked",
            })
        )
        print("bypass invoked")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="CFP-967 parallel work sentinel polling (ADR-073 Amendment 2)",
        prog="check_parallel_work_sentinel",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["title-search", "epic-state-poll", "head-compare-sibling-commits"],
        help="Polling mode (ADR-073 Amendment 2 §결정 1-A transition trigger enum)",
    )
    parser.add_argument(
        "--epic-id",
        default=None,
        help="Epic issue number (required for epic-state-poll mode)",
    )
    parser.add_argument(
        "--branch",
        default="origin/main",
        help="Branch for head-compare mode (default: origin/main)",
    )

    args = parser.parse_args()

    if args.mode == "title-search":
        mode_title_search(epic_id=args.epic_id)
    elif args.mode == "epic-state-poll":
        if not args.epic_id:
            _exit_setup_error("--epic-id is required for epic-state-poll mode")
        mode_epic_state_poll(epic_id=args.epic_id)
    elif args.mode == "head-compare-sibling-commits":
        mode_head_compare(branch=args.branch)
    else:
        _exit_setup_error(f"unknown mode: {args.mode}")


if __name__ == "__main__":
    main()
