#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_mid_flight_marker.py
CFP-2761 §5.2 / ADR-085 §결정10 — mid-flight marker ownership/freshness PR-time lint (warning tier).

작업 중(mid-flight) 산출물에 남는 소유/신선도 마커의 stale 상태를 PR 시점에 좌향 노출한다.
검사 대상 = tracked content 타입 1/2/3 (마커·N/A 선언·dispatch placeholder) + tracked anchor 타입 5
  (ADR-RESERVATION 예약 row proxy). 타입 4(hook 검사)는 본 PR-time 게이트 대상 아님.

검사 타입 (CFP-2761 §5.2 / ADR-085 §결정10):
  타입 1 (작업초안): tracked .md/.sh/.py 안 mid-flight 마커 status ∈ {draft, provisional} AND
    kst 가 staleness threshold(기본 14일, --stale-days N) 초과 → warn.
  타입 2 (lane N/A 선언): N/A-token 존재 AND 동일 파일에 status=final 마커 부재 → warn.
  타입 3 (dispatch placeholder): placeholder-token(verdict 미기록 / dispatch pending) 존재 → warn.
  타입 5 (untracked ADR draft — NARROW proxy): archive/adr/ADR-RESERVATION.md 의
    amendments_reserved[] / reservations[] row 중 status: reserved AND reserved_at/
    reservation_date age > threshold → warn. owner/kst 는 schema 에 없으므로 status+age proxy 만
    사용 (untracked ADR draft 파일 직접 grep 금지 — coverage 위조 금지, pre-reservation window 미커버).

마커 문법 (SSOT — closed-set):
  <!-- mid-flight: owner=<git_identity>[|worktree=<path>]; kst=<YYYY-MM-DDTHH:MM:SS+09:00>;
       status=<draft|provisional|final> -->
  status closed-set = {draft, provisional, final}. 마커 부재 → provisional 취급(E1 legacy default).
  well-formed 마커의 status token 이 closed-set 밖 → TC-UNKNOWN → exit 2 (fail-closed).

토큰 문법 (§8.2):
  N/A-token (타입 2): markdown heading `§\s*\d+.*N/?A` OR registry line `applicable:\s*false`
    OR 리터럴 `면제`.
  placeholder-token (타입 3): `<!--\s*dispatch:\s*\S+\s+pending\s*-->` OR verdict slot value ∈
    {pending, TBD, —, placeholder}.

DoS guard (§8.6, ADR-082 Amendment 38 resource-safety): anchored bounded regex (nested/인접-무제한
  quantifier 0) + per-line length cap(MAX_PHYSICAL_LINE_LEN 초과 truncate) + per-file line count
  cap(PER_FILE_SCAN_CAP) + O(n) index-advance. 총 작업량 <= line-count-cap × per-line-cap 로 유한
  bound (~1.5MB 코퍼스 blowup 0). 완화 = bounded degradation — 임의 입력 무해가 아닌 정직 천장.

CLI 계약 (ADR-061 house style — 고정, self-test + hook 소비):
  bash scripts/check-mid-flight-marker.sh --repo-root DIR [--files F1 F2 ...] [--stale-days N]
    → DIR 하 tracked .md/.sh/.py (default) 또는 명시 --files 만 스캔. --stale-days 기본 14.

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

# ─────────────────────── anchored bounded regex (nested quantifier 0) ────────────
# mid-flight 마커 — `<!-- mid-flight:` 리터럴에 anchor, 모든 quantifier bounded.
_MARKER_RE = re.compile(
    r"<!--\s{0,8}mid-flight:\s{0,8}owner=([^|;]{1,256}?)"
    r"(?:\|worktree=([^;]{0,512}?))?\s{0,8};\s{0,8}"
    r"kst=([0-9T:.+\-]{1,40})\s{0,8};\s{0,8}"
    r"status=([A-Za-z]{1,32})\s{0,8}-->"
)

# 타입 2 N/A-token: (a) heading `§<digits>...N/A` / (b) `applicable: false` / (c) 리터럴 `면제`.
_NA_HEADING_RE = re.compile(r"§\s{0,8}\d{1,6}[^\n]{0,300}?N/?A")
_NA_APPLICABLE_FALSE_RE = re.compile(r"applicable:\s{0,8}false", re.IGNORECASE)
_NA_LITERAL = "면제"

# 타입 3 placeholder-token: (a) dispatch pending 주석 / (b) verdict slot value ∈ closed-set.
_PLACEHOLDER_DISPATCH_RE = re.compile(r"<!--\s{0,8}dispatch:\s{0,8}\S{1,200}\s{1,8}pending\s{0,8}-->")
_VERDICT_SLOT_RE = re.compile(
    r"verdict\s{0,8}[:=]\s{0,8}[\"'`]{0,1}\s{0,4}(pending|tbd|placeholder|—)",
    re.IGNORECASE,
)

# 타입 5 ADR-RESERVATION row 파서 (YAML list row — dependency-free 라인 파서).
_RES_ROW_START_RE = re.compile(r"^(\s{0,80})-\s{1,8}adr_number:\s{0,8}(\d{1,7})\s{0,8}$")
_RES_KEY_RE = re.compile(r"^(\s{0,80})([A-Za-z_]{1,40}):\s{0,8}(.{0,4096})$")
# reserved_at / reservation_date 값에서 선두 YYYY-MM-DD 추출 (ISO8601 또는 `2026-05-24 KST` 형식).
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
    """타입 2 N/A-token 존재 여부 (heading §N...N/A / applicable: false / 리터럴 면제)."""
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#") and _NA_HEADING_RE.search(line):
            return True
        if _NA_APPLICABLE_FALSE_RE.search(line):
            return True
        if _NA_LITERAL in line:
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


# ─────────────────────── 타입 5 ADR-RESERVATION row 파서 ─────────────────────────

def _parse_reservation_rows(lines):
    """ADR-RESERVATION YAML list row 파싱 → [dict(adr_number, [amendment_id], status, date)].

    `- adr_number: N` (uncommented list item) 이 row 시작. 주석(`# - adr_number:`)은 미매칭
    (선두 `#` 로 `^\\s*-` anchor 실패). 뒤따르는 dedent 초과 key: value 라인을 row 로 수집.
    reservations[] 는 reserved_at, amendments_reserved[] 는 reservation_date 필드 사용.
    """
    rows = []
    n = len(lines)
    i = 0
    while i < n:
        m = _RES_ROW_START_RE.match(lines[i])
        if not m:
            i += 1
            continue
        dash_indent = len(m.group(1))
        row = {"adr_number": m.group(2)}
        j = i + 1
        while j < n:
            line = lines[j]
            if _RES_ROW_START_RE.match(line):
                break
            km = _RES_KEY_RE.match(line)
            if km is None:
                stripped = line.strip()
                # blank / fenced-block 경계 / dash-indent 이하 dedent = row 종료.
                indent = len(line) - len(line.lstrip())
                if stripped == "" or stripped.startswith("```") or indent <= dash_indent:
                    break
                j += 1
                continue
            key_indent = len(km.group(1))
            if key_indent <= dash_indent:
                break  # dedent — row 종료
            key = km.group(2)
            val = km.group(3).split("#", 1)[0].strip().strip('"').strip("'")
            if key not in row:
                row[key] = val
            j += 1
        rows.append(row)
        i = j if j > i else i + 1
    return rows


def _reservation_findings(rel, lines, stale_days, now_dt):
    """타입 5 stale reserved row → findings=[(rel, detail)]."""
    findings = []
    today = now_dt.date()
    for row in _parse_reservation_rows(lines):
        status = (row.get("status") or "").lower()
        if status != "reserved":
            continue
        date_raw = row.get("reserved_at") or row.get("reservation_date")
        if not date_raw:
            continue
        dm = _RES_DATE_RE.search(date_raw)
        if not dm:
            continue
        try:
            res_date = datetime(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))).date()
        except ValueError:
            continue
        age_days = (today - res_date).days
        if age_days > stale_days:
            adr = row.get("adr_number", "?")
            amd = row.get("amendment_id")
            label = "%s/%s" % (adr, amd) if amd else str(adr)
            findings.append((
                rel,
                "ADR-RESERVATION %s: reserved %d days, status=reserved (stale reservation)"
                % (label, age_days),
            ))
    return findings


# ─────────────────────── 단일 파일 스캔 ──────────────────────────────────────────

def scan_file(path, rel, stale_days, now_dt):
    """단일 파일 → (findings, unknown_status_hits). findings=[(rel, detail)]."""
    lines = _read_lines_bounded(path)
    if lines is None:
        return [], []

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

    # 타입 5 — ADR-RESERVATION anchor (narrow proxy).
    if os.path.basename(rel) == ADR_RESERVATION_BASENAME:
        findings.extend(_reservation_findings(rel, lines, stale_days, now_dt))

    return findings, unknown


# ─────────────────────── candidate 열거 ──────────────────────────────────────────

def _git_tracked_candidates(repo_root):
    """git ls-files 로 tracked .md/.sh/.py 열거. git 부재/비-repo → [] (honest no-op degrade)."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_root, "ls-files", "--", "*.md", "*.sh", "*.py"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    out = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line:
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
