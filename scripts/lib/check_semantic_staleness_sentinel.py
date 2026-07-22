"""
scripts/lib/check_semantic_staleness_sentinel.py
CFP-2786 / Epic #2783 Child B — Semantic staleness sentinel SSOT (독립 재구현, stdlib-only)

기능:
  현재 PR 이 governance/policy carrier surface(ADR / CLAUDE.md / 계약 registry / template 등)의
  의미를 바꾸는지 1차 필터하고, 그 carrier 를 참조하는 in-flight open PR(작업 중 산출물)을
  cross-match 해 "재검토 필요" 신호를 stdout JSON 으로 방출한다. 본 sentinel 은 관측·표면화만
  수행하며 어떤 mutation 도 스스로 실행하지 않는다(read-only — NEGATIVE GUARD AC-5).

  위상축(commit-count-behind) sentinel 과 4-way disjoint(subject / surface / primitive /
  trigger-origin) — 본 축은 "재검토 필요" 단일 신호이며 tier 카탈로그를 방출하지 않는다(AC-7).

honest ceiling (필수 — presence != truth):
  - carrier touch = candidate surface 이지 verdict 아님. touch != 의미변경.
    2차 diff-content 판정(current_tier flip / §결정 신설 / required-context 증감)은 사람 몫.
  - "모든 의미 의존 검출" hard-claim 금지 — 의미 의존은 undecidable. 본 게이트는 완전 검출을
    단정하지 않는다.
  - recall >> precision 방향(비용 비대칭 + 하류 사람 게이트) — 수치 SLA 0, invariant-only
    (INV-RECALL-FIRST 방향). recall/precision 회귀 수치 target 부재.
  - PR-centric self-check honest ceiling: 마지막 push 이후 착지 정책 merge 는 다음 push 까지
    미재검(per-push snapshot). push 사이 window 는 본 게이트 미커버.

Mode enum (argparse --mode):
  carrier-cross-match (유일 유효 mode):
    Input:  optional --base-sha (없으면 merge-base HEAD..origin/main 사용)
    Output: exit 0 + stdout JSON (아래 출력 계약 참조)

BYPASS:
  BYPASS_SEMANTIC_STALENESS_SENTINEL=1 — unconditional skip, exit 0 + audit marker(argparse 선행).

Exit-code 2-tier (로컬 계약):
  0: PASS / self-carve-out / silent-pass / honest-degrade (stdout JSON degradation 필드로 식별)
  2: SETUP error — git/gh/python3 미설치(handled → error_kind JSON, Traceback 무노출) /
     무효 --base-sha / 무효 --mode(argparse native)

Test seam (test-only — self-test discriminating forcing-function, 정확히 이 env 노출):
  SEMANTIC_CARRIER_TOUCH_MOCK  — newline-separated touched paths 주입 (실 git diff 우회)
  SEMANTIC_INFLIGHT_MOCK       — gh pr list JSON fixture 파일경로 주입
  SEMANTIC_GH_MOCK_RC          — gh returncode 주입 (degrade 경로)
  SEMANTIC_GH_MOCK_STDERR      — gh stderr 주입 (degrade payload stderr_excerpt)
  SEMANTIC_GIT_MOCK_RC         — git returncode 주입 (degrade 경로)
  SEMANTIC_GIT_MOCK_STDERR     — git stderr 주입
  SEMANTIC_SELF_IDENTITY_MOCK  — self manifest paths 주입 (self-carve-out override)
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

# Windows cp949 stdout encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_semantic_staleness_sentinel"
BYPASS_ENV = "BYPASS_SEMANTIC_STALENESS_SENTINEL"          # 독립 BYPASS (AC-7 4-way 1:1)
MARKER_API_FAILED = "[semantic-staleness-sentinel-api-failed]"

# degrade 4-class ALL HOT (전부 active). 5th label 발명 금지.
DEGRADATION_LABELS = ("api_quota_exceeded", "gh_command_failed", "gh_payload_invalid", "git_fetch_failed")
QUOTA_STDERR_PATTERNS = ("rate limit exceeded", "secondary rate limit")
QUOTA_STATUS_CODES = ("403", "429")
_TOKEN_MASK_RE = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{36,})")

# anchor 패턴 — bounded regex (B-M2 ReDoS bound: nesting 0, overlap-alternation 0, 선형)
_PREFIX = os.environ.get("STORY_KEY_PREFIX", "CFP")   # CFP-2451 prefix-parametric (하드코딩 금지)
KEY_PATTERN = re.compile(rf"\b{re.escape(_PREFIX)}-[0-9]{{1,5}}\b")
ADR_PATTERN = re.compile(r"\bADR-[0-9]{1,4}\b")

# 입력 cap (B-M2 / B-M10 DoS bound)
BODY_LEN_CAP = 65536      # PR body 당 anchor-scan 전 절단
PR_COUNT_CAP = 500        # gh pr list pagination cap
BASE_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")   # B-M1 40-hex 검증

# workitem body 내 경로 토큰 추출 (non-capturing group → findall = full-match)
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_./-]+\.(?:py|md|ya?ml|sh)")
# lane 토큰 추출 (plugins/<lane>/ 폴더명 — carrier/workitem 공통 lane 축)
LANE_DIR_RE = re.compile(r"(?:^|/)plugins/([A-Za-z0-9_-]+)/")
# evidence-checks-registry.yaml 의 workflow: 라인 (라인 기반 parse — PyYAML 금지)
_WORKFLOW_LINE_RE = re.compile(r"^\s*workflow:\s*(.+?)\s*$")

# mock seam env keys (test-only — 정확히 이 env 노출)
CARRIER_TOUCH_MOCK_ENV = "SEMANTIC_CARRIER_TOUCH_MOCK"   # newline-separated touched paths 주입
INFLIGHT_MOCK_ENV = "SEMANTIC_INFLIGHT_MOCK"             # gh pr list JSON fixture 파일경로
GH_MOCK_RC_ENV = "SEMANTIC_GH_MOCK_RC"                   # gh returncode 주입 (degrade)
GH_MOCK_STDERR_ENV = "SEMANTIC_GH_MOCK_STDERR"           # gh stderr 주입
GIT_MOCK_RC_ENV = "SEMANTIC_GIT_MOCK_RC"                 # git returncode 주입 (degrade)
GIT_MOCK_STDERR_ENV = "SEMANTIC_GIT_MOCK_STDERR"         # git stderr 주입
SELF_IDENTITY_MOCK_ENV = "SEMANTIC_SELF_IDENTITY_MOCK"   # self manifest paths 주입 (self-carve-out)

# self manifest — 본 sentinel 자기 파일 set (발행자 != 수신자, AC-8)
SELF_MANIFEST = [
    "scripts/lib/check_semantic_staleness_sentinel.py",
    "scripts/check-semantic-staleness-sentinel.sh",
    "templates/github-workflows/semantic-staleness-detection.yml",
    ".github/workflows/semantic-staleness-detection.yml",
    "tests/scripts/test_check-semantic-staleness-sentinel.sh",
    "docs/domain-knowledge/domain/governance-principle/semantics-change-sentinel.md",
]

# repo 루트 (scripts/lib/<file>.py → 3-up). workflow checkout cwd 와 동일하나 __file__ 기반이 견고.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Functional core — 3 pure leaves (부작용 0, stdlib-only)
# ---------------------------------------------------------------------------
def _classify_carrier_touch(touched_paths: List[str], surface: List[Tuple[str, str]]) -> List[str]:
    """touched path 중 carrier surface 에 속하는 것만 반환 (filter). 비-정책 touch 는 미분류.

    AC-1 / INV-1 — carrier touch = candidate 1차 필터 (touch != 의미변경, 2차 판정=사람).
    """
    matched: List[str] = []
    for p in touched_paths:
        for kind, val in surface:
            if kind == "exact" and p == val:
                matched.append(p)
                break
            if kind == "prefix" and p.startswith(val):
                matched.append(p)
                break
            if kind == "glob" and fnmatch.fnmatch(p, val):
                matched.append(p)
                break
    return matched


def _extract_anchors(text: str, key_pattern=KEY_PATTERN, adr_pattern=ADR_PATTERN) -> set:
    """PR title/body/Story §3(또는 carrier path 문자열)에서 anchor(ADR/CFP) 추출.

    AC-3 / INV-3 — body cap 선행(B-M2 DoS bound). 빈 text → 빈 set.
    """
    if not text:
        return set()
    capped = text[:BODY_LEN_CAP]
    return set(adr_pattern.findall(capped)) | set(key_pattern.findall(capped))


def _cross_match(carrier_anchors, workitem_anchors, carrier_paths, workitem_paths,
                 carrier_lanes, workitem_lanes) -> Dict[str, Any]:
    """SEPARATE-OR-top: 방향별 overlap 을 각각 독립 산출 후 top-level OR.

    AC-3 / INV-3 / Q6 multi-signal OR. anchor_overlap(primary recall signal) /
    path_overlap(recall floor) / lane_overlap(recall floor) 를 각각 분리 산출 →
    matched = OR(셋). "OR→AND"(M3a) / "narrowing 제거→all-in-flight"(M3b) discriminating.
    """
    anchor_overlap = sorted(set(carrier_anchors) & set(workitem_anchors))
    path_overlap = sorted(set(carrier_paths) & set(workitem_paths))
    lane_overlap = sorted(set(carrier_lanes) & set(workitem_lanes))
    return {
        "anchor_overlap": anchor_overlap,      # primary recall signal
        "path_overlap": path_overlap,          # recall floor
        "lane_overlap": lane_overlap,          # recall floor
        "matched": bool(anchor_overlap) or bool(path_overlap) or bool(lane_overlap),
    }


# ---------------------------------------------------------------------------
# is_self_touch short-circuit (AC-8 / INV-4 — carrier-classify BEFORE 위치)
# ---------------------------------------------------------------------------
def is_self_touch(changed_files: List[str], self_manifest: List[str]) -> bool:
    """PR 이 touch 한 carrier 파일이 전부 sentinel 자기 파일이면 True (발행자 != 수신자).

    빈 changed_files → False (touch 없음 = self-touch 아님).
    """
    if not changed_files:
        return False
    sm = set(self_manifest)
    return all(f in sm for f in changed_files)


# ---------------------------------------------------------------------------
# carrier-surface 파생 (Q2 — live SSOT, 하드코딩 list 0)
# ---------------------------------------------------------------------------
def _derive_carrier_surface(repo_root: str) -> Tuple[List[Tuple[str, str]], List[str]]:
    """carrier surface 를 live SSOT 파일에서 파생 (drift 부채 회피 — 하드코딩 정책 list 금지).

    carrier-surface = candidate 1차 필터, touch != 의미변경(2차 diff-content 판정=사람,
    honest ceiling presence != truth). 반환 (surface, gaps): surface = (kind, value) list,
    kind in {"exact","prefix","glob"}. gaps = honest 미커버 source note list.
    """
    surface: List[Tuple[str, str]] = []
    gaps: List[str] = []

    # 1. doc-locations.yaml 파생 (live) — archive/adr/ dogfood adr path prefix
    doc_loc = os.path.join(repo_root, "docs", "doc-locations.yaml")
    adr_prefix_found = False
    try:
        with open(doc_loc, "r", encoding="utf-8") as f:
            for line in f:
                if "archive/adr/" in line:
                    adr_prefix_found = True
                    break
    except OSError:
        gaps.append("doc-locations adr glob 파싱 실패 — fallback prefix archive/adr/")
    if not adr_prefix_found and "doc-locations adr glob 파싱 실패 — fallback prefix archive/adr/" not in gaps:
        gaps.append("doc-locations adr glob 파싱 실패 — fallback prefix archive/adr/")
    surface.append(("prefix", "archive/adr/"))   # live 발견 또는 fallback (양자 동일 prefix)

    # 2. evidence-checks-registry.yaml 파생 (live) — 각 workflow: 값 → exact
    reg = os.path.join(repo_root, "docs", "evidence-checks-registry.yaml")
    try:
        with open(reg, "r", encoding="utf-8") as f:
            for line in f:
                m = _WORKFLOW_LINE_RE.match(line)
                if not m:
                    continue
                val = m.group(1).split("#", 1)[0].strip()   # trailing 주석 제거
                if val and val not in ("null", "~"):
                    surface.append(("exact", val))
        surface.append(("exact", "docs/evidence-checks-registry.yaml"))   # current_tier flip = 의미변경
    except OSError:
        gaps.append("evidence-checks-registry workflow 파싱 실패 — registry surface 미커버")

    # 3. structural governance anchors (repo-structural 경로 anchor — 디렉토리 존재 자체가 live signal)
    surface.extend([
        ("exact", "CLAUDE.md"),
        ("glob", "plugins/*/CLAUDE.md"),
        ("prefix", "docs/inter-plugin-contracts/"),
        ("prefix", "templates/"),
        ("prefix", "docs/domain-knowledge/domain/governance-principle/"),
        ("exact", "docs/wording-dictionary.md"),
        ("exact", "docs/security/branch-protection-audit.md"),
        ("exact", "docs/doc-locations.yaml"),
    ])

    # 4. gap honest — clean machine-enumerable 아님
    gaps.append(
        "wording-dictionary/category-enum per-ADR embedded — best-effort, "
        "semantic 판정 사람 몫(honest ceiling)"
    )

    # dedup (순서 보존)
    seen = set()
    deduped: List[Tuple[str, str]] = []
    for item in surface:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped, gaps


# ---------------------------------------------------------------------------
# degrade helper (parallel-work 구조 복제 — import 아님)
# ---------------------------------------------------------------------------
def _stderr_excerpt(stderr: str) -> str:
    """stderr 발췌 — 토큰 마스킹 선행 → cap 후행 (첫 8줄 ∧ 1024B 중 먼저 도달).

    마스킹→cap 순서: cap 선행 시 절단 경계 토큰 분할로 정규식 미포착 leak → 마스킹 선행이 구조적 봉인.
    best-effort (honest ceiling): 공식 prefix 형식(gh[pousr]_ / github_pat_) 외 비정형 비밀 미커버.
    """
    if not stderr:
        return ""
    masked = _TOKEN_MASK_RE.sub("[REDACTED]", stderr)
    capped = "\n".join(masked.splitlines()[:8])
    encoded = capped.encode("utf-8")
    if len(encoded) > 1024:
        capped = encoded[:1024].decode("utf-8", errors="ignore")
    return capped


def _is_quota_evidence(*, stderr: str = "", payload: Any = None) -> bool:
    """quota 판정 단일 predicate — 2 evidence 채널.

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
    """rc!=0 경로 한정 분류 — 앵커드 rate-limit → api_quota_exceeded, 그 외 → gh_command_failed."""
    if _is_quota_evidence(stderr=stderr):
        return "api_quota_exceeded"
    return "gh_command_failed"


def _parse_gh_payload(raw: str, expect: type, required_keys: Tuple[str, ...] = ()) -> Tuple[Any, Optional[str]]:
    """gh stdout 파서. 반환 (payload, None) 성공 / (None, defect_label).

    판정 순서: ① 빈/공백 → gh_payload_invalid ② JSONDecodeError → gh_payload_invalid
      ③ error-dict sniff(구조 채널) → api_quota_exceeded ④ not isinstance → gh_payload_invalid
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


# ---------------------------------------------------------------------------
# lane 토큰 (carrier/workitem 공통 축)
# ---------------------------------------------------------------------------
def _lanes(label_names: List[str], paths: List[str]) -> set:
    """lane 토큰 산출 — phase: label + plugins/<lane>/ 폴더명(paths 파생). recall floor 축."""
    lanes: set = set()
    for lbl in label_names:
        if lbl.startswith("phase:"):
            lanes.add(lbl)
    for p in paths:
        for m in LANE_DIR_RE.findall(p):
            lanes.add(m)
    return lanes


# ---------------------------------------------------------------------------
# git 원시연산 (read-only — NEGATIVE GUARD AC-5)
# ---------------------------------------------------------------------------
def _get_touched_paths(base_sha: Optional[str]) -> Tuple[Optional[List[str]], Optional[str], str]:
    """origin/main 이 divergence 이후 착지시킨 carrier-후보 경로 산출 → (paths, degrade, stderr_excerpt).

    B-M1: git argv = HEAD/origin/main 상수 + merge-base 산출 SHA + 검증된 base_sha(BASE_SHA_RE)만.
      PR title/body/head_ref 는 git argv 미주입. pathspec `--` 사용.
    FileNotFoundError(git 미설치)는 catch 하지 않고 상위(main)로 전파 → exit 2 SETUP.
    """
    # 1. carrier-touch mock — newline-split 주입 (실 git 우회)
    mock = os.environ.get(CARRIER_TOUCH_MOCK_ENV)
    if mock is not None:
        paths = [ln.strip() for ln in mock.splitlines() if ln.strip()]
        return paths, None, ""

    # 2. git mock rc — rc!=0 → degrade
    rc_mock = os.environ.get(GIT_MOCK_RC_ENV)
    if rc_mock is not None:
        try:
            rc = int(rc_mock)
        except ValueError:
            rc = 0
        if rc != 0:
            stderr = os.environ.get(GIT_MOCK_STDERR_ENV, "")
            return None, "git_fetch_failed", _stderr_excerpt(stderr)

    # 3. 실 경로 — fetch(best-effort) → left(base_sha 또는 merge-base) → diff --name-only
    subprocess.run(["git", "fetch", "origin", "main"], capture_output=True)
    if base_sha:
        left = base_sha
    else:
        mb = subprocess.run(
            ["git", "merge-base", "HEAD", "origin/main"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if mb.returncode != 0:
            return None, "git_fetch_failed", _stderr_excerpt(mb.stderr)
        left = mb.stdout.strip()
        if not BASE_SHA_RE.match(left):
            return None, "git_fetch_failed", _stderr_excerpt("merge-base output invalid")
    diff = subprocess.run(
        ["git", "diff", "--name-only", left, "origin/main", "--"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if diff.returncode != 0:
        return None, "git_fetch_failed", _stderr_excerpt(diff.stderr)
    paths = [ln.strip() for ln in diff.stdout.splitlines() if ln.strip()]
    return paths, None, ""


# ---------------------------------------------------------------------------
# in-flight 열거 (gh read-only — AC-2)
# ---------------------------------------------------------------------------
def _enumerate_inflight() -> Tuple[Optional[List[dict]], Optional[str], str]:
    """open PR(작업 중 산출물) 열거 → (prs, degrade, stderr_excerpt).

    AC-2: open PR 만 (state open). FileNotFoundError(gh 미설치)는 상위 전파 → exit 2 SETUP.
    """
    # 1. inflight mock — fixture 파일 read → list parse
    mock = os.environ.get(INFLIGHT_MOCK_ENV)
    if mock is not None:
        try:
            with open(mock, "r", encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            return None, "gh_payload_invalid", _stderr_excerpt(f"inflight mock not found: {mock}")
        payload, defect = _parse_gh_payload(raw, list)
        if defect:
            return None, defect, ""
        return payload, None, ""

    # 2. gh mock rc — rc!=0 → degrade
    rc_mock = os.environ.get(GH_MOCK_RC_ENV)
    if rc_mock is not None:
        try:
            rc = int(rc_mock)
        except ValueError:
            rc = 0
        if rc != 0:
            stderr = os.environ.get(GH_MOCK_STDERR_ENV, "")
            return None, _classify_gh_failure(stderr), _stderr_excerpt(stderr)

    # 3. 실 경로 — gh pr list --state open (read-only)
    result = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--json", "number,title,body,labels",
         "--limit", str(PR_COUNT_CAP)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        return None, _classify_gh_failure(result.stderr), _stderr_excerpt(result.stderr)
    payload, defect = _parse_gh_payload(result.stdout, list)
    if defect:
        return None, defect, _stderr_excerpt(result.stderr)
    return payload, None, ""


# ---------------------------------------------------------------------------
# snapshot provenance (AC-13 — non-blocking)
# ---------------------------------------------------------------------------
def _snapshot_provenance() -> Dict[str, Any]:
    """per-push snapshot provenance (AC-13, non-blocking). mock 모드 = 실 git 우회(hermetic)."""
    if os.environ.get(CARRIER_TOUCH_MOCK_ENV) is not None:
        return {"origin_main_sha": None, "wall_clock": "mock-snapshot"}
    sha = None
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0 and r.stdout.strip():
            sha = r.stdout.strip()
    except FileNotFoundError:
        sha = None
    return {"origin_main_sha": sha, "wall_clock": "push-snapshot"}


# ---------------------------------------------------------------------------
# Emit helpers
# ---------------------------------------------------------------------------
def _exit_pass(payload: dict) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def _emit_degrade(label: str, stderr_excerpt: str) -> None:
    """honest-degrade — stderr 2줄(WARNING + MARKER) + stdout 계약 payload + exit 0."""
    print(
        f"[semantic-staleness-sentinel] WARNING: carrier/in-flight 관측 실패 — "
        f"의미축 재검토 신호 undetermined (degrade={label}).",
        file=sys.stderr,
    )
    print(MARKER_API_FAILED, file=sys.stderr)
    print(
        json.dumps({
            "carrier_touched": None,
            "inflight_candidates": [],
            "degradation": label,
            "marker": MARKER_API_FAILED,
            "stderr_excerpt": stderr_excerpt,
        })
    )
    sys.exit(0)


def _exit_setup(msg: str, kind: str) -> None:
    """SETUP error handled — Traceback 무노출, stderr JSON + exit 2."""
    print(
        json.dumps({"error": msg, "error_kind": kind, "exit_code": 2}),
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (hotfix-bypass family, audit-trailed). argparse 선행.
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            json.dumps({
                "bypass": True,
                "marker": "[hotfix-bypass] BYPASS_SEMANTIC_STALENESS_SENTINEL=1 invoked",
                "audit_comment": "bypass invoked",
            })
        )
        print("bypass invoked")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="CFP-2786 semantic staleness sentinel (Epic #2783 Child B)",
        prog="check_semantic_staleness_sentinel",
    )
    parser.add_argument(
        "--mode",
        default="carrier-cross-match",
        choices=["carrier-cross-match"],
        help="Sentinel mode (단일 유효 mode: carrier-cross-match)",
    )
    parser.add_argument(
        "--base-sha",
        default=None,
        help="Base SHA (없으면 merge-base HEAD..origin/main 사용). 주어지면 40-hex 검증.",
    )
    args = parser.parse_args()

    # --base-sha 검증 (B-M1)
    if args.base_sha is not None and not BASE_SHA_RE.match(args.base_sha):
        _exit_setup(f"invalid --base-sha={args.base_sha!r} (expect 7-40 hex)", kind="setup")

    # carrier surface 파생 (live SSOT)
    surface, gaps = _derive_carrier_surface(_REPO_ROOT)

    # touched paths (read-only git)
    try:
        touched, degrade, excerpt = _get_touched_paths(args.base_sha)
    except FileNotFoundError:
        _exit_setup("git not installed — install: https://git-scm.com", kind="git_not_installed")
        return  # unreachable (sys.exit)

    if degrade:
        _emit_degrade(degrade, excerpt)
        return  # unreachable

    # carrier-classify (candidate 1차 필터)
    carrier_touched = _classify_carrier_touch(touched or [], surface)

    # is_self_touch short-circuit (AC-8 / INV-4 — carrier-classify BEFORE, in-flight 매칭 이전)
    self_manifest = SELF_MANIFEST
    ident_mock = os.environ.get(SELF_IDENTITY_MOCK_ENV)
    if ident_mock is not None:
        self_manifest = [ln.strip() for ln in ident_mock.splitlines() if ln.strip()]
    if is_self_touch(carrier_touched, self_manifest):
        _exit_pass({
            "carrier_touched": carrier_touched,
            "self_touch": True,
            "inflight_candidates": [],
            "carve_out": "self-application (발행자 != 수신자, AC-8)",
            "degradation": None,
        })
        return  # unreachable

    # carrier 없음 → silent pass (R4)
    if not carrier_touched:
        _exit_pass({
            "carrier_touched": [],
            "inflight_candidates": [],
            "degradation": None,
        })
        return  # unreachable

    # carrier anchors/lanes/paths (carrier_touched 파생 — 별도 carrier-text source 부재)
    carrier_paths = carrier_touched
    carrier_anchors = _extract_anchors("\n".join(carrier_touched))
    carrier_lanes = _lanes([], carrier_touched)

    # in-flight 열거 (read-only gh)
    try:
        inflight, gh_degrade, gh_excerpt = _enumerate_inflight()
    except FileNotFoundError:
        _exit_setup("gh CLI not installed — install: https://cli.github.com", kind="gh_not_installed")
        return  # unreachable

    if gh_degrade:
        _emit_degrade(gh_degrade, gh_excerpt)
        return  # unreachable

    inflight = inflight or []
    truncated = len(inflight) >= PR_COUNT_CAP   # B-M10 silent truncation 금지 (honest flag)

    candidates: List[Dict[str, Any]] = []
    for pr in inflight:
        # AC-2 defensive open filter (mock fixture 에 state 필드 있으면 open 만 통과)
        state = pr.get("state")
        if state is not None and str(state).lower() != "open":
            continue
        number = pr.get("number", 0)
        title = pr.get("title", "")
        body = pr.get("body") or ""
        capped_body = body[:BODY_LEN_CAP]
        workitem_anchors = _extract_anchors(title + "\n" + capped_body)
        label_names = [
            lbl.get("name", "") if isinstance(lbl, dict) else str(lbl)
            for lbl in pr.get("labels", [])
        ]
        workitem_paths = sorted(set(PATH_TOKEN_RE.findall(capped_body)))
        workitem_lanes = _lanes(label_names, workitem_paths)
        overlap = _cross_match(
            carrier_anchors, workitem_anchors,
            carrier_paths, workitem_paths,
            carrier_lanes, workitem_lanes,
        )
        if overlap["matched"]:   # recall-first narrowing — matched=true 인 것만 candidate
            candidates.append({"number": number, "title": title, "overlap": overlap})

    out: Dict[str, Any] = {
        "carrier_touched": carrier_touched,
        "self_touch": False,
        "inflight_candidates": candidates,
        "carrier_anchors": sorted(carrier_anchors),
        "surface_gaps": gaps,
        "snapshot_provenance": _snapshot_provenance(),
        "degradation": None,
    }
    if truncated:
        out["truncated"] = True   # honest — PR_COUNT_CAP 도달 부분열거
    _exit_pass(out)


if __name__ == "__main__":
    main()
