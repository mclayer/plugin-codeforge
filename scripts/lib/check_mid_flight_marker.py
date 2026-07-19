#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_mid_flight_marker.py
CFP-2761 §5.2 / ADR-085 §결정10 — mid-flight marker ownership/freshness PR-time lint (warning tier).

작업 중(mid-flight) 산출물에 남는 소유/신선도 마커의 stale 상태를 PR 시점에 좌향 노출한다.
검사 대상 = tracked content 타입 1/2/3 (마커·N/A 선언·dispatch placeholder) + tracked anchor 타입 5
  (ADR-RESERVATION 예약 테이블 row proxy). 타입 4(hook 검사)는 본 PR-time 게이트 대상 아님.

타입 scoping (CFP-2761 구현리뷰 FIX B): 타입 1/2/3 은 Story 산출물 전용, 타입 5 는 ADR-RESERVATION
  전용 — 파일 basename 으로 상호배타 분기(scan_file). ADR-RESERVATION 예약 registry 는 Story lane
  산출물이 아니므로 타입 1/2/3 미적용(§<digit>…면제 governance prose 가 타입 2 false-positive 유발
  하던 회귀 근절). ADR-RESERVATION 아닌 파일에는 타입 5 미적용.

검사 타입 (CFP-2761 §5.2 / ADR-085 §결정10):
  타입 1 (작업초안): tracked .md/.sh/.py 안 mid-flight 마커 status ∈ {draft, provisional} AND
    kst 가 staleness threshold(기본 14일, --stale-days N) 초과 → warn.
  타입 2 (lane N/A 선언): N/A-token 존재 AND 동일 파일에 status=final 마커 부재 → warn.
  타입 3 (dispatch placeholder): placeholder-token(verdict 미기록 / dispatch pending) 존재 → warn.
  타입 5 (ADR-RESERVATION 예약 테이블 — NARROW proxy): archive/adr/ADR-RESERVATION.md 의
    "현재 예약 목록" markdown 테이블(컬럼 헤더 `| adr_number | epic | status | reserved_at |` 앵커)
    data row 중 status == reserved(대소문자 무시) AND reserved_at 선두 YYYY-MM-DD age > threshold
    → warn. reservation SSOT = md-table (YAML amendments_reserved[] 아님 — 후자는 전건 active 라
    vacuous false-negative 원천, CFP-2761 구현리뷰 F3 재구현). owner/kst 는 schema 에 없으므로
    status+age proxy 만 사용 (타입 5 narrow 보존). malformed row(bad date / missing status) →
    skip (non-fatal, TC-UNKNOWN 아님).

마커 문법 (SSOT — closed-set):
  <!-- mid-flight: owner=<git_identity>[|worktree=<path>]; kst=<YYYY-MM-DDTHH:MM:SS+09:00>;
       status=<draft|provisional|final> -->
  status closed-set = {draft, provisional, final}. 마커 부재 → provisional 취급(E1 legacy default).
  well-formed 마커의 status token 이 closed-set 밖 → TC-UNKNOWN → exit 2 (fail-closed).

토큰 문법 (§8.2):
  N/A-token (타입 2): markdown heading `§\s*\d+.*N/?A` OR registry line `applicable:\s*false`
    OR `면제` (구조적 앵커 한정 — heading line 안 OR `§\d+…면제` 절-scoped 선언; bare prose
    `면제` 는 미검출 — F4 false-positive flood 근절, CFP-2761 구현리뷰 FIX).
  placeholder-token (타입 3): `<!--\s*dispatch:\s*\S+\s+pending\s*-->` OR verdict slot value ∈
    {pending, TBD, —, placeholder}.

DoS guard (§8.6, ADR-082 Amendment 38 resource-safety): anchored bounded regex (nested/인접-무제한
  quantifier 0) + per-line length cap(MAX_PHYSICAL_LINE_LEN 초과 truncate) + per-file line count
  cap(PER_FILE_SCAN_CAP) + O(n) index-advance. 총 작업량 <= line-count-cap × per-line-cap 로 유한
  bound (~1.5MB 코퍼스 blowup 0). 완화 = bounded degradation — 임의 입력 무해가 아닌 정직 천장.

CLI 계약 (ADR-061 house style — 고정, self-test + hook 소비):
  bash scripts/check-mid-flight-marker.sh --repo-root DIR [--files F1 F2 ...] [--stale-days N]
    → default = DIR 하 SCAN_SCOPE(docs/stories/** + archive/adr/ADR-RESERVATION.md) 내 tracked
      .md/.sh/.py 만 스캔 (tests/ 배제 — 자기/fixture never-scan). 명시 --files 는 그 파일만 정확 스캔
      (scope 미적용). --stale-days 기본 14.
    F1/F4-fix (CFP-2761 구현리뷰): 구 default = 전 tracked .md/.sh/.py 스캔 → 자기 test fixture
      (status=bogus → TC-UNKNOWN self-poison, F1) + prose .md 의 `면제` bare-substring flood(F4) 유입.
      default 열거를 Story 산출물 dir + ADR-RESERVATION anchor 로 국한해 근절 (--files 명시 경로 무변경).

Exit codes (ADR-060 §결정5 tri-tier — warning tier, advisory NEVER blocks):
  0 = clean (finding 0) OR warning finding 방출 OR zero-target honest no-op.
      finding 은 STDOUT 에 `::warning::mid-flight-marker-stale: <detail>` 로 surface (advisory).
  2 = usage/argparse 오류 OR TC-UNKNOWN(closed-set 밖 status) fail-closed.
  3 = born-hollow fail-closed (repo-root 부재 / dir 아님).
  1 = strict-tier 미사용 (warning tier).
  zero-target(TC-EMPTY) = honest-degrade: exit 0 + 명시 non-silent line (silent-green 금지).

ADR refs: CFP-2761 §5.2 (carrier) / ADR-085 §결정10 (mid-flight marker owner) / ADR-073 (worktree
  self-ownership context — 타입 5 예약 proxy) / ADR-060 §결정5 (warning tri-tier) /
  ADR-082 Amendment 38 §8.6 (resource-safety DoS guard) / ADR-061 §결정1 (Python SSOT + thin wrapper).
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제 (ADR-061 portability 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

CHECK_NAME = "mid-flight-marker-stale"
DEFAULT_STALE_DAYS = 14

# ─────────────────────── input-driven exhaustion bounded 상수 (§8.6) ─────────────
# per-file 물리 라인 스캔 cap (라인 count bound). ADR-RESERVATION 등 장수명 governance doc 성장 여유.
PER_FILE_SCAN_CAP = 50000
# per-physical-line 길이 cap (라인 length bound — count cap 과 별개 축). 초과분 truncate-scan.
MAX_PHYSICAL_LINE_LEN = 8192

KST = timezone(timedelta(hours=9))

# 마커 status closed-set (SSOT). 이 밖 token = TC-UNKNOWN(exit 2 fail-closed).
STATUS_CLOSED_SET = ("draft", "provisional", "final")
# 타입 1 stale 판정 대상 status (final 은 완결 → 제외).
STATUS_INPROGRESS = ("draft", "provisional")

CANDIDATE_EXTS = (".md", ".sh", ".py")
ADR_RESERVATION_BASENAME = "ADR-RESERVATION.md"

# ── default 스캔 범위 (F1/F4-fix — CFP-2761 구현리뷰) ──
# 전 tracked 파일 스캔이 자기 test fixture(status=bogus → TC-UNKNOWN self-poison, F1) +
# prose .md 의 `면제` bare-substring flood(F4) 를 삼키던 회귀 근절. default 열거를 Story
# 산출물 dir(타입 1/2/3 마커·N/A·placeholder) + ADR-RESERVATION anchor(타입 5) 로 국한.
# --files 명시 경로는 본 scope 미적용 (self-test explicit 스캔 계약 보존).
SCAN_SCOPE_DIRS = ("docs/stories",)
SCAN_SCOPE_FILES = ("archive/adr/ADR-RESERVATION.md",)

# ─────────────────────── anchored bounded regex (nested quantifier 0) ────────────
# mid-flight 마커 — `<!-- mid-flight:` 리터럴에 anchor, 모든 quantifier bounded.
_MARKER_RE = re.compile(
    r"<!--\s{0,8}mid-flight:\s{0,8}owner=([^|;]{1,256}?)"
    r"(?:\|worktree=([^;]{0,512}?))?\s{0,8};\s{0,8}"
    r"kst=([0-9T:.+\-]{1,40})\s{0,8};\s{0,8}"
    r"status=([A-Za-z]{1,32})\s{0,8}-->"
)

# 타입 2 N/A-token: (a) heading `§<digits>...N/A` / (b) `applicable: false` /
#   (c) `면제` — 구조적 앵커 한정(heading line 안 OR `§\d+…면제` 절-scoped 선언). bare prose
#   `면제` 는 미검출 (F4 false-positive flood 근절, CFP-2761 구현리뷰 FIX).
_NA_HEADING_RE = re.compile(r"§\s{0,8}\d{1,6}[^\n]{0,300}?N/?A")
_NA_APPLICABLE_FALSE_RE = re.compile(r"applicable:\s{0,8}false", re.IGNORECASE)
_NA_LITERAL = "면제"
# `면제` 절-scoped 선언 앵커 — `§ N ... 면제` (anchored bounded, nested quantifier 0 — §8.6 DoS).
_NA_MYEONJE_RE = re.compile(r"§\s{0,8}\d{1,6}[^\n]{0,300}?면제")

# 타입 3 placeholder-token: (a) dispatch pending 주석 / (b) verdict slot value ∈ closed-set.
_PLACEHOLDER_DISPATCH_RE = re.compile(r"<!--\s{0,8}dispatch:\s{0,8}\S{1,200}\s{1,8}pending\s{0,8}-->")
_VERDICT_SLOT_RE = re.compile(
    r"verdict\s{0,8}[:=]\s{0,8}[\"'`]{0,1}\s{0,4}(pending|tbd|placeholder|—)",
    re.IGNORECASE,
)

# 타입 5 ADR-RESERVATION 예약 테이블(md-table) 파서 앵커 (F3 재구현 — YAML 파서 폐기).
# 컬럼-헤더 시그니처 `| adr_number | epic | status | reserved_at |` (섹션 heading text 는 가변 →
#   컬럼 헤더에만 anchor). surrounding whitespace 허용, anchored bounded(nested quantifier 0 — §8.6).
_RES_TABLE_HEADER_RE = re.compile(
    r"^\s{0,8}\|\s{0,8}adr_number\s{0,8}\|\s{0,8}epic\s{0,8}\|\s{0,8}"
    r"status\s{0,8}\|\s{0,8}reserved_at\s{0,8}\|\s{0,8}$"
)
# adr_number cell = plain integer (구분선 `---` row / 비-정수 cell 배제).
_RES_ADR_NUM_RE = re.compile(r"^\d{1,7}$")
# reserved_at 값에서 선두 YYYY-MM-DD 추출 (ISO8601 또는 `2026-05-24 KST`/parenthetical 형식).
_RES_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _now_kst():
    """현재 시각 (KST aware). 신선도 age 계산 기준."""
    return datetime.now(KST)


# ─────────────────────── per-file bounded read (§8.6) ────────────────────────────

def _read_lines_bounded(path):
    """파일을 라인 count cap + per-line truncate 로 bounded read. 실패 → None."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = []
            for idx, raw in enumerate(f):
                if idx >= PER_FILE_SCAN_CAP:
                    break
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN]
                lines.append(raw.rstrip("\n").rstrip("\r"))
            return lines
    except OSError:
        return None


# ─────────────────────── 마커 파싱 (타입 1/2 status=final 판정 공용) ─────────────

def _extract_markers(lines):
    """모든 mid-flight 마커 추출 → (markers, unknown_status_hits).

    markers = [(lineno, kst_raw, status_lowered)]  (status closed-set 내부만)
    unknown_status_hits = [(lineno, status_token)]  (closed-set 밖 — TC-UNKNOWN 신호)
    """
    markers = []
    unknown = []
    for i, line in enumerate(lines):
        for m in _MARKER_RE.finditer(line):
            status_token = m.group(4)
            status = status_token.lower()
            if status not in STATUS_CLOSED_SET:
                unknown.append((i + 1, status_token))
                continue
            markers.append((i + 1, m.group(3), status))
    return markers, unknown


def _parse_kst(kst_raw):
    """마커 kst 문자열 → aware datetime. 파싱 불가 → None (staleness skip, non-fatal)."""
    try:
        dt = datetime.fromisoformat(kst_raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    return dt


# ─────────────────────── 타입 2/3 토큰 검출 ──────────────────────────────────────

def _has_na_token(lines):
    """타입 2 N/A-token 존재 여부.

    - heading §N…N/A (heading line)
    - applicable: false (registry line)
    - `면제` = 구조적 앵커 한정 — heading line(선두 `#`) 안 `면제` OR `§\\d+…면제` 절-scoped
      선언(_NA_MYEONJE_RE). bare prose `면제` 는 미검출 (F4 false-positive flood 근절).
    """
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#") and _NA_HEADING_RE.search(line):
            return True
        if _NA_APPLICABLE_FALSE_RE.search(line):
            return True
        # `면제` 는 구조적 선언 context(heading OR §N-scoped)에서만 — bare substring 아님.
        if _NA_LITERAL in line and (stripped.startswith("#") or _NA_MYEONJE_RE.search(line)):
            return True
    return False


def _has_placeholder_token(lines):
    """타입 3 placeholder-token 존재 여부 (dispatch pending 주석 / verdict slot value)."""
    for line in lines:
        if _PLACEHOLDER_DISPATCH_RE.search(line):
            return True
        if _VERDICT_SLOT_RE.search(line):
            return True
    return False


# ─────────────────────── 타입 5 ADR-RESERVATION 예약 테이블(md-table) 파서 ───────────

def _parse_reservation_table(lines):
    """ADR-RESERVATION "현재 예약 목록" md-table 파싱 → [dict(adr_number, epic, status, reserved_at)].

    reservation SSOT = markdown 테이블 (YAML amendments_reserved[] 아님 — 후자는 전건 active 라
    vacuous false-negative 원천, CFP-2761 구현리뷰 F3). 컬럼-헤더 시그니처
    `| adr_number | epic | status | reserved_at |` 로 앵커(섹션 heading text 는 가변). 앵커 후
    뒤따르는 data row 수집:
      - blank line = 테이블 내 허용 (본 doc style — row 간 공백 줄) → continue
      - 비-`|` 비-blank line (다음 `### 번호 해제` heading 등) = 테이블 종료 → break
        (YAML amendments_reserved[] 블록은 heading 으로 분리되어 도달 전 종료 → 미침습)
      - 구분선 `|---|---|` row / adr_number 비-정수 cell → skip (non-fatal)
    reserved_at cell 내부 escaped `|` 포함 가능 → cell[3:] 를 `|` 로 복원(선두 date 보존).
    O(n) index-advance, per-line 은 이미 _read_lines_bounded 로 truncate (§8.6 bounded).
    """
    rows = []
    n = len(lines)
    header_idx = -1
    for i in range(n):
        if _RES_TABLE_HEADER_RE.match(lines[i]):
            header_idx = i
            break
    if header_idx < 0:
        return rows  # 헤더 부재 → 빈 결과 (파일 shape 변화 honest degrade)
    for j in range(header_idx + 1, n):
        stripped = lines[j].strip()
        if stripped == "":
            continue
        if not stripped.startswith("|"):
            break  # 테이블 종료 (다음 heading/prose)
        cells = [c.strip() for c in stripped.split("|")]
        # 감싸는 `|` 의 선두/후미 empty cell 제거.
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if len(cells) < 4:
            continue  # 구분선/malformed → skip
        adr = cells[0]
        if not _RES_ADR_NUM_RE.match(adr):
            continue  # 구분선 `---` 또는 비-정수 adr_number → skip
        rows.append({
            "adr_number": adr,
            "epic": cells[1],
            "status": cells[2],
            "reserved_at": "|".join(cells[3:]),
        })
    return rows


def _reservation_table_findings(rel, lines, stale_days, now_dt):
    """타입 5 stale reserved row → findings=[(rel, detail)].

    status == reserved (대소문자 무시) AND reserved_at 선두 YYYY-MM-DD age > threshold → warn.
    malformed row (bad date / missing status) → skip (non-fatal, TC-UNKNOWN 아님).
    """
    findings = []
    today = now_dt.date()
    for row in _parse_reservation_table(lines):
        status = (row.get("status") or "").lower()
        if status != "reserved":
            continue
        dm = _RES_DATE_RE.search(row.get("reserved_at") or "")
        if not dm:
            continue  # 날짜 결측/불량 → skip (non-fatal)
        try:
            res_date = datetime(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))).date()
        except ValueError:
            continue
        age_days = (today - res_date).days
        if age_days > stale_days:
            adr = row.get("adr_number", "?")
            epic = row.get("epic") or "?"
            findings.append((
                rel,
                "ADR-RESERVATION ADR-%s (%s): reserved %d days, status=reserved (stale reservation)"
                % (adr, epic, age_days),
            ))
    return findings


# ─────────────────────── 단일 파일 스캔 ──────────────────────────────────────────

def scan_file(path, rel, stale_days, now_dt):
    """단일 파일 → (findings, unknown_status_hits). findings=[(rel, detail)].

    타입 scoping (CFP-2761 구현리뷰 FIX B — 상호배타 분기):
      - ADR-RESERVATION.md = 예약 registry → 타입 5(md-table) 전용. 타입 1/2/3 미적용
        (Story lane 산출물이 아님 — §<digit>…면제 governance prose 가 타입 2 false-positive
        유발하던 회귀 근절). 마커 추출 안 함 → unknown_status_hits 없음.
      - 그 외 파일 = Story 산출물 → 타입 1/2/3 전용. 타입 5 미적용.
    """
    lines = _read_lines_bounded(path)
    if lines is None:
        return [], []

    # 타입 5 전용 경로 — ADR-RESERVATION 예약 테이블 (narrow proxy).
    if os.path.basename(rel) == ADR_RESERVATION_BASENAME:
        return _reservation_table_findings(rel, lines, stale_days, now_dt), []

    # 타입 1/2/3 — Story 산출물 전용.
    findings = []
    markers, unknown = _extract_markers(lines)
    has_final = any(status == "final" for (_ln, _kst, status) in markers)

    # 타입 1 — draft/provisional 마커 stale.
    for (lineno, kst_raw, status) in markers:
        if status not in STATUS_INPROGRESS:
            continue
        dt = _parse_kst(kst_raw)
        if dt is None:
            continue
        age_days = (now_dt - dt).days
        if age_days > stale_days:
            findings.append((
                rel,
                "%s: status=%s kst=%s (stale %d days)" % (rel, status, kst_raw, age_days),
            ))

    # 타입 2 — N/A-token 존재 AND status=final 마커 부재.
    if _has_na_token(lines) and not has_final:
        findings.append((rel, "%s: N/A declaration without status=final marker" % rel))

    # 타입 3 — placeholder-token 존재.
    if _has_placeholder_token(lines):
        findings.append((rel, "%s: dispatch placeholder not promoted (provisional)" % rel))

    return findings, unknown


# ─────────────────────── candidate 열거 ──────────────────────────────────────────

def _git_tracked_candidates(repo_root):
    """git ls-files 로 SCAN_SCOPE(docs/stories/** + ADR-RESERVATION) 내 tracked .md/.sh/.py
    열거. git 부재/비-repo → [] (honest no-op degrade).

    F1/F4-fix (CFP-2761 구현리뷰): pathspec 를 SCAN_SCOPE_DIRS + SCAN_SCOPE_FILES 로 국한해,
    전 tracked 파일 스캔이 자기 test fixture(status=bogus → TC-UNKNOWN self-poison, F1) +
    prose .md 의 `면제` bare-substring flood(F4) 를 삼키던 회귀를 근절한다. 추가로 tests/
    경로는 defense-in-depth 로 배제(자기/test-fixture 절대 스캔 금지 — F1 root).
    (git ls-files 출력 경로 = forward-slash 고정 → startswith/포함 검사 안전.)
    """
    pathspec = list(SCAN_SCOPE_DIRS) + list(SCAN_SCOPE_FILES)
    try:
        result = subprocess.run(
            ["git", "-C", repo_root, "ls-files", "--"] + pathspec,
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    out = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # tests/ defense-in-depth — 자기/test-fixture never-scan (F1 root).
        if line.startswith("tests/") or "/tests/" in line:
            continue
        if os.path.splitext(line)[1] not in CANDIDATE_EXTS:
            continue
        out.append(os.path.join(repo_root, line.replace("/", os.sep)))
    return out


def _collect_candidates(repo_root, explicit_files):
    """(scanned_paths). explicit_files 지정 시 그 파일만, 아니면 git tracked 후보."""
    if explicit_files:
        paths = [os.path.abspath(p) for p in explicit_files]
    else:
        paths = _git_tracked_candidates(repo_root)
    seen = []
    out = []
    for p in paths:
        if p in seen:
            continue
        seen.append(p)
        if not os.path.isfile(p):
            continue
        if os.path.splitext(p)[1] not in CANDIDATE_EXTS:
            continue
        out.append(p)
    return sorted(set(out))


# ─────────────────────── main ────────────────────────────────────────────────────

def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_mid_flight_marker.py",
        description="mid-flight marker ownership/freshness PR-time lint (warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="스캔 루트 (기본 = scripts/lib 기준 자동 탐지).")
    parser.add_argument("--files", nargs="*", default=None, help="명시 파일만 스캔 (PR-time changed set).")
    parser.add_argument(
        "--stale-days", type=int, default=DEFAULT_STALE_DAYS,
        help="staleness threshold (기본 14일). age > N 일 시 stale.",
    )
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)
    if not os.path.isdir(repo_root):
        print(
            "::error::%s: repo-root 부재 또는 dir 아님: %s (born-hollow fail-closed)"
            % (CHECK_NAME, repo_root),
            file=sys.stderr,
        )
        return 3

    stale_days = args.stale_days
    now_dt = _now_kst()

    candidates = _collect_candidates(repo_root, args.files)
    if not candidates:
        print("%s: no candidate targets scanned (honest no-op)" % CHECK_NAME)
        return 0

    all_findings = []
    unknown_hits = []
    for path in candidates:
        rel = os.path.relpath(path, repo_root).replace(os.sep, "/")
        findings, unknown = scan_file(path, rel, stale_days, now_dt)
        all_findings.extend(findings)
        for (ln, tok) in unknown:
            unknown_hits.append((rel, ln, tok))

    # TC-UNKNOWN fail-closed — closed-set 밖 status token = 신뢰 불가 입력 → exit 2.
    if unknown_hits:
        print(
            "::error::%s: TC-UNKNOWN — well-formed 마커 status token 이 closed-set "
            "{draft,provisional,final} 밖 (fail-closed):" % CHECK_NAME,
            file=sys.stderr,
        )
        for (rel, ln, tok) in unknown_hits:
            print("  - %s:%d status=%s" % (rel, ln, tok), file=sys.stderr)
        return 2

    if all_findings:
        for (_rel, detail) in all_findings:
            print("::warning::%s: %s" % (CHECK_NAME, detail))
        print(
            "%s: %d finding over %d candidate — warning tier (advisory, PR 미차단)"
            % (CHECK_NAME, len(all_findings), len(candidates))
        )
        return 0

    print(
        "%s: PASS — stale marker/reservation 0 over %d candidate (warning tier)"
        % (CHECK_NAME, len(candidates))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
