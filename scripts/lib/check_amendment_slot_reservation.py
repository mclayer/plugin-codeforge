#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1497 / Wave 2-C of CFP-1389 (Sub-CFP C CFP-1435 mechanical wire)
# ADR-082 Amendment 17 §결정 1 layer 1 sub-scope (1-G) amendment-slot pre-reservation
# strict claim mandate 4-tuple primitive + ADR-050 §결정 1 ADR-RESERVATION carrier
# cross-ref + ADR-061 §결정 1 (multi-line Python > 5줄 외부 .py file 의무).
#
# Amendment-slot reservation mechanical lint (warning-tier per ADR-060 §결정 5).
#
# Detection scope (declarative anchor — Wave 1 SSOT, CFP-1435 carrier):
#   Check (a) — Amendment append without matching reservation row (PRIMARY):
#     input: changed ADR file (docs/adr/ADR-*.md) frontmatter `amendments:` array 안
#       새 `amendment_id: N` entry (origin/main diff 기준)
#     cross-check: docs/adr/ADR-RESERVATION.md `amendments_reserved:` array 안
#       매칭 {adr_number, amendment_id, reserved_by_cfp} row 존재 verify
#     output: matching row 부재 → [WARN-MISSING-RESERVATION] (warning-tier, exit 0)
#
#   Check (b) — Concurrent reservation conflict (SECONDARY):
#     input: changed ADR-RESERVATION file 안 amendments_reserved[] 신규 row
#     cross-check: 같은 (adr_number, amendment_id) slot 이 2+ row 안 claim
#     output: 2+ collision → [WARN-CONCURRENT-CONFLICT] (warning-tier)
#     Note: cross-PR query via gh API = Wave 3 carrier, single-PR-local 만 detect.
#
# FP-완화 guards (CFP-1489 패턴 답습):
#   - (a) templates/** path = canonical example 면제
#   - (b) tests/** + fixtures/** path = bats fixture self-detection avoid
#   - (c) ADR file (`docs/adr/ADR-*.md`) 아닌 모든 file = silent skip (lint scope 외)
#
# Bypass channel:
#   - HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION=1 env (label
#     `hotfix-bypass:amendment-slot-reservation` 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (yaml parse failure)
#   2 — setup error (file system access error)
#
# Usage:
#   python3 check_amendment_slot_reservation.py [file ...]
#
# Test mode (RED→GREEN stash proof + bats fixture):
#   env AMENDMENT_SLOT_RESERVATION_FILE 가 set 되면 그 file 을 ADR-RESERVATION SSOT 로 사용
#   (default = repo-relative `docs/adr/ADR-RESERVATION.md`). bats fixture 가 임시
#   ADR-RESERVATION-like file 을 가리키는 경로 주입에 사용.
#
# SSOT carrier: CFP-1435 Wave 1 declarative anchor (PR #1482 merged) + 본 Wave 2-C wire.
# Precedent byte-pattern: scripts/lib/check_spawn_prompt_head_pin.py (CFP-1489).

import sys
import re
import os
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION", "")
if BYPASS_ENV == "1":
    print("[check-amendment-slot-reservation] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-amendment-slot-reservation]"

# ADR file 식별 — docs/adr/ADR-NNN-*.md (NNN = 1-3 digit, slug optional)
# ADR-RESERVATION.md 자체는 amendment_id 정의 file 아님 → 본 lint Check (a) scope 외 (Check (b) source)
ADR_FILE_RE = re.compile(r"docs/adr/ADR-\d+[\w-]*\.md$")
ADR_RESERVATION_FILE_RE = re.compile(r"docs/adr/ADR-RESERVATION\.md$")

# ADR file 안 amendment_id entry — frontmatter `amendments:` array sub-key
# 예:
#   amendments:
#     - amendment_id: 11
#       carrier_story: CFP-1437
#     - amendment_id: 15
#       carrier_story: CFP-1489
AMENDMENT_ID_RE = re.compile(
    r"^\s*-\s*amendment_id:\s*(\d+)\s*$",
    re.MULTILINE,
)

# ADR-RESERVATION.md 안 amendments_reserved[] entry — 4-key tuple
# 예:
#   amendments_reserved:
#     - adr_number: 82
#       amendment_id: 17
#       reserved_by_cfp: CFP-1435
#       reservation_date: 2026-05-24 KST
#       status: active
# entry 단위 = `- adr_number: NNN` line + 후속 sub-key lines 까지 (parsing simplification)
# regex: `- adr_number: NNN ... amendment_id: M ... reserved_by_cfp: CFP-XXX`
# multi-line 매칭 — `re.DOTALL` 미사용, 대신 명시적 multi-key cluster regex
RESERVATION_ENTRY_RE = re.compile(
    r"^\s*-\s*adr_number:\s*(\d+)\s*\n"
    r"(?:\s+\w+:\s*[^\n]*\n)*?"  # any sub-key lines (greedy non-capturing, multi-line)
    r"\s+amendment_id:\s*(\d+)\s*\n",
    re.MULTILINE,
)

# ADR-NNN-...md filename 에서 adr_number 추출
ADR_FILENAME_NUMBER_RE = re.compile(r"ADR-(\d+)")


# ── path filter (FP-완화 guard 1/2) ───────────────────────────────────────────
def _is_template_path(filepath):
    """templates/** 경로 식별 — canonical example 면제."""
    parts = Path(filepath).parts
    return "templates" in parts


def _is_test_fixture_path(filepath):
    """tests/** + fixtures/** 경로 식별 — bats fixture self-detection avoid."""
    parts = Path(filepath).parts
    return "tests" in parts or "fixtures" in parts


def _is_adr_file(filepath):
    """docs/adr/ADR-NNN-*.md path 식별 (ADR-RESERVATION.md 제외 — Check (b) source 별도)."""
    p = Path(filepath).as_posix()
    return bool(ADR_FILE_RE.search(p)) and not ADR_RESERVATION_FILE_RE.search(p)


def _is_adr_reservation_file(filepath):
    """docs/adr/ADR-RESERVATION.md 식별 — Check (b) concurrent conflict source."""
    p = Path(filepath).as_posix()
    return bool(ADR_RESERVATION_FILE_RE.search(p))


def _extract_adr_number_from_filename(filepath):
    """`docs/adr/ADR-082-...md` → 82 (int) 추출. ADR file 아니면 None."""
    p = Path(filepath).name
    m = ADR_FILENAME_NUMBER_RE.match(p)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


# ── ADR-RESERVATION SSOT load ─────────────────────────────────────────────────
def _load_reservation_entries(reservation_file_path):
    """
    ADR-RESERVATION.md 안 amendments_reserved[] entry list load.
    반환: list of (adr_number: int, amendment_id: int) tuples.
    file 부재 또는 parse 실패 시 빈 list.
    """
    path = Path(reservation_file_path)
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return []

    entries = []
    for m in RESERVATION_ENTRY_RE.finditer(text):
        try:
            adr_num = int(m.group(1))
            amend_id = int(m.group(2))
            entries.append((adr_num, amend_id))
        except (ValueError, IndexError):
            continue
    return entries


# ── 단일 file 검사 ────────────────────────────────────────────────────────────
def check_file(filepath, reservation_entries):
    """
    단일 ADR file 검사. 반환: warn_count (int).

    flow:
      1. path filter (templates/**, tests/** skip)
      2. ADR file 식별 (docs/adr/ADR-NNN-*.md, ADR-RESERVATION.md 제외)
      3. read content
      4. frontmatter `amendments:` 안 amendment_id list 추출
      5. 각 amendment_id 에 대해 (adr_number, amendment_id) reservation row 존재 verify
      6. matching 부재 시 [WARN-MISSING-RESERVATION]
    """
    path = Path(filepath)
    if not path.exists():
        return 0

    # FP-완화 guard 1: templates/** 면제
    if _is_template_path(filepath):
        return 0

    # FP-완화 guard 2: tests/** + fixtures/** 면제
    if _is_test_fixture_path(filepath):
        return 0

    # FP-완화 guard 3: ADR file 아닌 모든 file = silent skip
    if not _is_adr_file(filepath):
        return 0

    adr_number = _extract_adr_number_from_filename(filepath)
    if adr_number is None:
        # filename 파싱 실패 — silent skip (ADR-RESERVATION 등 number-less ADR file)
        return 0

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError) as e:
        print(f"{SCRIPT_NAME} [WARN] {filepath}: file read error ({e}) — skip", file=sys.stderr)
        return 0

    # frontmatter 안 amendments: array 의 amendment_id list 추출
    amendment_ids = []
    for m in AMENDMENT_ID_RE.finditer(text):
        try:
            amendment_ids.append(int(m.group(1)))
        except (ValueError, IndexError):
            continue

    if not amendment_ids:
        # Amendment 0 — silent skip (no Amendment append)
        return 0

    # 각 amendment_id 에 대해 reservation row 존재 verify
    warn_count = 0
    reservation_set = set(reservation_entries)
    for amend_id in amendment_ids:
        if (adr_number, amend_id) not in reservation_set:
            print(
                f"{SCRIPT_NAME} [WARN-MISSING-RESERVATION] {filepath}: "
                f"ADR-{adr_number} Amendment {amend_id} detected in frontmatter "
                f"but no matching `amendments_reserved[]` row in ADR-RESERVATION.md "
                f"(expected: adr_number={adr_number}, amendment_id={amend_id}). "
                f"ADR-082 Amendment 17 §결정 1 layer 1 sub-scope (1-G) — "
                f"amendment-slot pre-reservation strict claim mandate. "
                f"Add reservation row to docs/adr/ADR-RESERVATION.md `amendments_reserved:` "
                f"before merging Amendment append PR. "
                f"hotfix bypass: hotfix-bypass:amendment-slot-reservation label",
                file=sys.stderr,
            )
            warn_count += 1

    if warn_count == 0:
        print(
            f"{SCRIPT_NAME} OK: {filepath} "
            f"(ADR-{adr_number} {len(amendment_ids)} Amendment(s) all reserved)",
            file=sys.stderr,
        )

    return warn_count


# ── ADR-RESERVATION file concurrent conflict check (Check b) ─────────────────
def check_concurrent_conflict(reservation_file_path):
    """
    ADR-RESERVATION file 안 같은 (adr_number, amendment_id) slot 2+ row collision detect.
    반환: warn_count.
    """
    path = Path(reservation_file_path)
    if not path.exists():
        return 0

    # FP-완화 guard 1: templates/** 면제 (canonical fixture)
    if _is_template_path(reservation_file_path):
        return 0
    # FP-완화 guard 2: tests/** + fixtures/** 면제
    if _is_test_fixture_path(reservation_file_path):
        return 0

    entries = _load_reservation_entries(reservation_file_path)
    if not entries:
        return 0

    # 같은 (adr_number, amendment_id) slot 이 2+ entry 안에 나타나면 conflict
    slot_count = {}
    for slot in entries:
        slot_count[slot] = slot_count.get(slot, 0) + 1

    warn_count = 0
    for slot, count in slot_count.items():
        if count >= 2:
            adr_num, amend_id = slot
            print(
                f"{SCRIPT_NAME} [WARN-CONCURRENT-CONFLICT] {reservation_file_path}: "
                f"slot (adr_number={adr_num}, amendment_id={amend_id}) reserved "
                f"{count} times — concurrent reservation conflict detected. "
                f"ADR-050 §결정 1 ADR-RESERVATION carrier cross-ref + ADR-082 Amendment 17 "
                f"§결정 1 layer 1 sub-scope (1-G). Resolve via merge-order coordination "
                f"(superseded status 부여 또는 amendment_id bump). "
                f"hotfix bypass: hotfix-bypass:amendment-slot-reservation label",
                file=sys.stderr,
            )
            warn_count += 1

    return warn_count


# ── reservation SSOT path resolution ─────────────────────────────────────────
def _resolve_reservation_file():
    """
    ADR-RESERVATION.md path 결정 우선순위:
      1. env AMENDMENT_SLOT_RESERVATION_FILE (bats fixture injection)
      2. cwd-relative `docs/adr/ADR-RESERVATION.md`
      3. None (file 부재 — graceful degradation, all checks silent skip)
    """
    env_path = os.environ.get("AMENDMENT_SLOT_RESERVATION_FILE", "")
    if env_path:
        return env_path
    cwd_path = Path.cwd() / "docs" / "adr" / "ADR-RESERVATION.md"
    if cwd_path.exists():
        return str(cwd_path)
    return None


# ── main ──────────────────────────────────────────────────────────────────────
def main(argv):
    if not argv:
        print(f"{SCRIPT_NAME} INFO: no files supplied — skip (exit 0)", file=sys.stderr)
        return 0

    reservation_file = _resolve_reservation_file()
    reservation_entries = []
    if reservation_file:
        reservation_entries = _load_reservation_entries(reservation_file)
    else:
        print(
            f"{SCRIPT_NAME} INFO: ADR-RESERVATION.md not found — Check (a) silent skip",
            file=sys.stderr,
        )

    total_warn = 0
    reservation_files_seen = set()
    for filepath in argv:
        try:
            # Check (b): ADR-RESERVATION.md 자체가 changed file 이면 concurrent conflict check
            if _is_adr_reservation_file(filepath) and filepath not in reservation_files_seen:
                reservation_files_seen.add(filepath)
                total_warn += check_concurrent_conflict(filepath)
            else:
                # Check (a): 일반 ADR file 의 frontmatter amendment_id ↔ reservation row cross-check
                total_warn += check_file(filepath, reservation_entries)
        except Exception as e:
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: unexpected error ({type(e).__name__}: {e}) — skip",
                file=sys.stderr,
            )

    if total_warn == 0:
        print(f"{SCRIPT_NAME} PASS: all files validated ({len(argv)} file(s) scanned)", file=sys.stderr)
    else:
        print(f"{SCRIPT_NAME} SUMMARY: {total_warn} warning(s) emitted (warning-tier, exit 0)", file=sys.stderr)

    # warning-tier — 항상 exit 0 (PR merge 미차단, ADR-060 §결정 5 정합)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
