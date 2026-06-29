#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_deferred_item_recovery.py
CFP-2470 / ADR-128 Amendment 1 — deferred follow-up 회수 게이트 (no-silent-drop, warning tier)

retro/Story 서사의 narrative-recorded deferred 각각이 완료 시점에 (추적 Issue 전환) OR
(관찰-only + 사유 명시) 중 하나로 **명시 판정**됐는지 검사한다. silent drop(판정 부재 채 누락)
**만** 차단한다. 전수 Issue 강제 전환 아님 (ADR-119 §결정 9 발견≠필요 정합).

도메인 SSOT:
  docs/domain-knowledge/domain/governance-principle/deferred-item-lifecycle.md (4-state lifecycle).
  docs/domain-knowledge/concept/deferred-followup-recovery-forcing-function.md (실패모드 calibration).

판정 로직 (dual-source AND — §3.1):
  retro.md §deferred structured 섹션(5-column table)의 각 disposition row 를 파싱:
    disposition / item / tracking(Issue link) / rationale / source
  PASS 조건 = 선언 row 존재 ∧ (
      (disposition == tracked  ∧ tracking Issue link 非공백 ∧ 실 Issue 존재 cross-validate)
    OR (disposition == observed ∧ rationale 텍스트 非공백)
  )
  WARN 조건 = 선언만 있고 backing 없음(theater) / observed 인데 rationale 누락(EC-3) /
             tracked 선언 but 실 Issue 없음(EC-4) / enum 미스(structured 위반).

enum anchored (자유텍스트 NLP 회피 — concept R-4 lexical-evasion 한계 수용):
  disposition ∈ 게이트 전용 직교 2-value {tracked, observed}.
  ⚠ ADR-045 §D-11 closure enum (CLOSE_AS_OBVIATED/CLOSE_AS_SENTINEL/PROMOTE/DEFER) 값은
  재사용하지 않는다 — closure disposition 축 ⊥ narrative deferred 판정 축 (F1 정정).
  ADR-045 §D-11 은 structured-row-over-free-text 패턴의 참조 선례로만 인용.

cross-repo + PAT graceful skip (EC-2, ADR-066 정합):
  retro 정본 = internal-docs `wrapper/retros/`. 실 tracking Issue 존재 cross-validate 는
  GitHub API 호출 필요 → CODEFORGE_CROSS_REPO_PAT (env GH_TOKEN) 부재 시
  ::warning + exit 0 (절대 hard-block 아님, fail-safe).

ReDoS-safe (ADR-061 Amd3 §결정 11 패턴):
  line-by-line scan + anchored simple regex (nested quantifier 0) + per-file scan cap.

Usage:
  python3 check_deferred_item_recovery.py <retro-file> [<retro-file> ...]
    → 각 retro 파일의 §deferred 섹션 row 를 검사, WARN 1+ 면 exit 1, WARN 0 면 exit 0.
  GH_TOKEN 부재 (cross-repo Issue cross-validate 불가) → ::warning + exit 0 (EC-2).

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (WARN 0) / graceful skip (PAT 부재)
  1 = WARN 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
  2 = SETUP error (입력 파일 전부 부재 / 읽기 실패)

ADR refs: ADR-128 Amendment 1 (carrier) / ADR-045 §D-11 (참조 선례, 값 비재사용) /
  ADR-119 §결정 9 (발견≠필요 순차직렬) / ADR-066 (cross-repo PAT graceful skip) /
  ADR-026 (cross-repo PAT scope internal-docs only) / ADR-061 (thin wrapper + Python SSOT).
"""

import os
import re
import shlex
import subprocess
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# unbounded scan 차단 (ReDoS/DoS 보호 — 대형 retro 파일 방어). per-file 라인 cap.
PER_FILE_LINE_CAP = 5000

# 게이트 전용 직교 disposition enum (closed-set, ADR-045 closure enum 값 비재사용 — F1).
_VALID_DISPOSITIONS = ("tracked", "observed")

# §deferred 섹션 헤더 (anchored, ReDoS-free — `## §deferred` 시작 라인).
_DEFERRED_SECTION_RE = re.compile(r"^\s*#{1,6}\s*§?deferred\b", re.IGNORECASE)

# 다음 H2/H3 섹션 시작 (§deferred 섹션 종료 경계 — `## ` / `### ` 헤더, deferred 제외).
_ANY_SECTION_HEADER_RE = re.compile(r"^\s*#{1,6}\s+")

# markdown table 데이터 row: `| a | b | c | d | e |` (anchored pipe-leading, ReDoS-free).
_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")

# table 구분 row: `|---|---|...` (header separator, 데이터 아님).
_TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")

# Issue link 추출: `#NNN` 형태 (anchored bounded — 1~9 digit, ReDoS-free).
_ISSUE_REF_RE = re.compile(r"#(\d{1,9})\b")


def _emit_warn(msg: str) -> None:
    """GitHub Actions ::warning:: annotation + stderr audit."""
    print(f"::warning::{msg}")
    print(f"[deferred-item-recovery] WARN: {msg}", file=sys.stderr)


def _split_table_row(inner: str) -> list:
    """`a | b | c | d | e` (양끝 pipe 제거된 inner) → cell list, trim."""
    return [c.strip() for c in inner.split("|")]


def _issue_exists(issue_num: str) -> bool:
    """실 tracking Issue 존재 cross-validate (dual-source AND 의 2번째 source).

    plugin-codeforge repo 의 Issue #N 존재 여부를 gh CLI 로 확인.
    gh 실패/미인증/네트워크 오류 = 판정 불가 → 보수적 False (theater 로 간주, WARN 유발).
      단 PAT 부재(graceful skip)는 main() 에서 호출 전 차단되므로 본 함수는 PAT 존재 전제.
    """
    # gh 바이너리 override seam (test stub 주입용 — DIR_GH_BIN env, worktree-clean 동형).
    # DIR_GH_BIN 은 단일 바이너리(`gh`) 또는 공백분리 명령(`<python> /path/gh_stub.py`) 둘 다 허용 —
    # 후자는 cross-platform test stub 주입용 (Windows 에서 .py 직접 실행 불가 회피).
    # shlex.split 으로 안전 토큰화(shell=False 유지, injection 표면 0 — env 는 신뢰 입력).
    # posix=(os.name != 'nt') — Windows 경로의 backslash 가 escape 로 소거되지 않게 (C:\... 보존).
    gh_bin = os.environ.get("DIR_GH_BIN", "gh").strip()
    gh_cmd = (
        shlex.split(gh_bin, posix=(os.name != "nt"))
        if gh_bin and gh_bin != "gh"
        else ["gh"]
    )
    try:
        result = subprocess.run(
            gh_cmd + ["issue", "view", issue_num, "--json", "number"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def _evaluate_row(cells: list) -> tuple:
    """단일 disposition row 판정 → (verdict, reason).

    verdict ∈ {"PASS", "WARN"}.
    cells = [disposition, item, tracking, rationale, source] (5-column 기대).
    """
    if len(cells) < 5:
        return ("WARN", f"structured 위반 (5-column 미충족: {len(cells)} cells)")

    disposition = cells[0].strip().lower()
    tracking = cells[2].strip()
    rationale = cells[3].strip()

    # enum anchored — {tracked, observed} 밖 = structured 위반 (TC-8).
    if disposition not in _VALID_DISPOSITIONS:
        return ("WARN", f"enum 미스 (disposition='{cells[0].strip()}' ∉ {{tracked, observed}})")

    # rationale/tracking 의 빈 셀 마커("—" / "-" / "") 정규화.
    def _is_blank(v: str) -> bool:
        return v in ("", "-", "—", "–", "N/A", "n/a")

    if disposition == "tracked":
        # tracked = tracking column 에 실 Issue link 의무 (EC-4 / TC-1 / TC-6).
        if _is_blank(tracking):
            return ("WARN", "tracked 선언이나 tracking Issue link 공백 (theater, EC-4 동류)")
        m = _ISSUE_REF_RE.search(tracking)
        if not m:
            return ("WARN", f"tracked 선언이나 tracking column 에 #NNN Issue ref 부재 (tracking='{tracking}')")
        issue_num = m.group(1)
        # dual-source AND — 실 Issue 존재 cross-validate (TC-6: #99999 부재 → WARN).
        if not _issue_exists(issue_num):
            return ("WARN", f"tracked 선언이나 실 Issue #{issue_num} 부재 (cross-validate fail, EC-4)")
        return ("PASS", f"tracked + 실 Issue #{issue_num} 확인")

    # disposition == "observed" — rationale column 에 사유 텍스트 의무 (EC-3 / TC-3 / TC-5).
    if _is_blank(rationale):
        return ("WARN", "observed 선언이나 rationale 사유 공백 (EC-3 — 사유 부재 = silent drop 동일 취급)")
    return ("PASS", f"observed + 사유 확인 ('{rationale[:40]}')")


def _scan_retro_file(path: str) -> tuple:
    """retro 파일 1개 scan → (warn_count, pass_count, deferred_section_found).

    §deferred 섹션 부재 = silent skip (deferred 0 = 판정 대상 0, WARN 아님 — EC-1 / TC-7).
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except Exception as exc:
        _emit_warn(f"retro 파일 읽기 실패: {path} ({exc})")
        return (0, 0, False)

    warn_count = 0
    pass_count = 0
    in_deferred = False
    section_found = False

    for idx, line in enumerate(lines):
        if idx >= PER_FILE_LINE_CAP:
            break

        # §deferred 섹션 진입 검출.
        if _DEFERRED_SECTION_RE.match(line):
            in_deferred = True
            section_found = True
            continue

        if not in_deferred:
            continue

        # 다음 섹션 헤더 도달 = §deferred 섹션 종료 (deferred 헤더 자신은 위에서 continue).
        if _ANY_SECTION_HEADER_RE.match(line) and not _DEFERRED_SECTION_RE.match(line):
            in_deferred = False
            continue

        # table separator row (|---|---|) = skip.
        if _TABLE_SEP_RE.match(line):
            continue

        m = _TABLE_ROW_RE.match(line)
        if not m:
            continue

        cells = _split_table_row(m.group(1))

        # header row 판별 — disposition column 이 enum 도 아니고 "disposition" 헤더면 skip.
        first = cells[0].strip().lower() if cells else ""
        if first in ("disposition", "disposition (게이트 전용)") or first.startswith("disposition"):
            continue

        # 빈 row / 전부-blank = skip (table 끝 trailing).
        if not any(c.strip() for c in cells):
            continue

        verdict, reason = _evaluate_row(cells)
        if verdict == "WARN":
            warn_count += 1
            _emit_warn(f"{os.path.basename(path)}: {reason} | row={cells[:5]}")
        else:
            pass_count += 1
            print(f"[deferred-item-recovery] PASS: {os.path.basename(path)}: {reason}")

    return (warn_count, pass_count, section_found)


def main(argv: list) -> int:
    args = argv[1:]
    if not args:
        print(
            "[deferred-item-recovery] SETUP error: retro 파일 인자 부재 "
            "(usage: check_deferred_item_recovery.py <retro-file> ...)",
            file=sys.stderr,
        )
        return 2

    # cross-repo PAT graceful skip (EC-2) — 실 Issue cross-validate 불가 시 차단 아님.
    # GH_TOKEN env (= CODEFORGE_CROSS_REPO_PAT 주입) 부재 → ::warning + exit 0.
    gh_token = os.environ.get("GH_TOKEN", "").strip()
    if not gh_token:
        _emit_warn(
            "CODEFORGE_CROSS_REPO_PAT (GH_TOKEN) 미설정 — deferred 회수 cross-validate skip "
            "(graceful, ADR-066 정합, hard-block 아님)"
        )
        return 0

    existing = [p for p in args if os.path.isfile(p)]
    if not existing:
        print(
            f"[deferred-item-recovery] SETUP error: 입력 retro 파일 전부 부재 ({args})",
            file=sys.stderr,
        )
        return 2

    total_warn = 0
    total_pass = 0
    any_section = False
    for path in existing:
        w, p, found = _scan_retro_file(path)
        total_warn += w
        total_pass += p
        any_section = any_section or found

    if not any_section:
        # EC-1: §deferred 섹션 전무 = 판정 대상 0 → silent skip (WARN 아님).
        print(
            f"[deferred-item-recovery] DONE: §deferred 섹션 부재 — 판정 대상 0 "
            f"(silent skip, EC-1) files={len(existing)}"
        )
        return 0

    print(
        f"[deferred-item-recovery] DONE: warn={total_warn} pass={total_pass} "
        f"files={len(existing)}"
    )
    return 1 if total_warn > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
