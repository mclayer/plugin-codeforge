#!/usr/bin/env python3
# scripts/lib/adr-reservation-backfill.py
# CFP-2563 / ADR-133 Amendment 2 — ADR-RESERVATION.md lapse row 소급 backfill (facet ②, M3).
#
# SSOT 근거:
#   - Change Plan §11.2/§11.5 — idempotent one-shot backfill. 결정적 재구성(frontmatter 기반, 비-grep).
#   - Change Plan §3.4 / M3 — 발급≠기록 gap(레지스트리 lapse) 소급 기록.
#   - Change Plan §8.1/§8.2 + §11.4 invariant:
#         INV-13 append-only (기존 row 변형/삭제 0 — byte-identical)
#         INV-14 idempotent (재실행 = no-op. guard = row 이미 존재 slot skip, conditional I-3)
#         INV-15 결정적 재구성 (대상 = git ls-tree filename 집합 ∖ RESERVATION 첫-열 slot 집합, 구조적 비-grep)
#         INV-16 slot ↔ file 1:1 (filename 번호 ↔ frontmatter adr_number cross-check, mismatch flag/skip)
#
# 대상(firsthand 확정, Change Plan §11.5): 114,116,117,118,119,122,123,124,125,128,132,135,136,139,140 (15).
#   141 제외 = row 이미 존재(CFP-2560). 구조적 결정 = modern-window(§2 "113+") 안 file-존재 ∧ row-부재.
#   pre-registry lapse(<113: 1-53 등) = non-goal(§5) — scope-min 하한으로 제외.
#
# row 재구성 (Change Plan §11.2): 컬럼 = `adr_number | epic | status | reserved_at` (schema_version 1.1).
#   epic = frontmatter carrier_story / status = active(파일 존재 = committed) /
#   reserved_at = frontmatter date + " (CFP-2563 backfill — lapse 소급 기록)".
#
# Usage:
#   python3 scripts/lib/adr-reservation-backfill.py \
#       [--reservation-path archive/adr/ADR-RESERVATION.md] [--adr-dir archive/adr] \
#       [--scope-min 113] [--dry-run]
#
# 기본 = in-place append. --dry-run = 미리보기(파일 미변경). exit 0 = 정상(no-op 포함) / 1 = 오류.

import argparse
import glob
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

RESERVATION_BASENAME = "ADR-RESERVATION.md"
# modern-window 하한 (Change Plan §2 "113+" / §11.5). pre-registry lapse(<113) = non-goal(§5).
DEFAULT_SCOPE_MIN = 113
BACKFILL_NOTE = "(CFP-2563 backfill — lapse 소급 기록)"


def normalize_number(raw):
    """int 정규화 (zero-pad / quoted-string 흡수). 정수 아님 → None."""
    if raw is None:
        return None
    s = str(raw).strip().strip('"').strip("'").strip()
    m = re.fullmatch(r"0*(\d+)", s)
    return int(m.group(1)) if m else None


def read_frontmatter_field(text, field):
    """frontmatter block 단일 field 추출 (regex, pyyaml 무의존 — neighbor 정합 `\\n---\\n` split)."""
    if not text.startswith("---\n"):
        return None
    fm_text = text.split("\n---\n", 1)[0][4:]
    m = re.search(rf"^{re.escape(field)}:\s*(.+?)\s*$", fm_text, re.M)
    return m.group(1).strip() if m else None


def collect_reservation_slots(text):
    """markdown 표 첫-열 slot 집합 (구조적 — row 본문 grep 금지, INV-15)."""
    slots = set()
    for line in text.split("\n"):
        m = re.match(r"^\|\s*(\d+)\s*\|", line)
        if m:
            slots.add(normalize_number(m.group(1)))
    return slots


def index_adr_files(adr_dir):
    """filename 번호 → (basename, frontmatter adr_number, carrier_story, date) 매핑.

    ⚠ RESERVATION 파일만 정확 basename 제외 (substring "reservation" 제외 금지 — ADR-133/ADR-036 누락 함정).
    """
    by_num = {}
    for path in sorted(glob.glob(os.path.join(adr_dir, "ADR-*.md"))):
        base = os.path.basename(path)
        if base == RESERVATION_BASENAME:
            continue
        m = re.match(r"ADR-(\d+)-", base)
        if not m:
            continue
        fnum = normalize_number(m.group(1))
        if fnum is None:
            continue
        text = open(path, encoding="utf-8").read()
        fm_num = normalize_number(read_frontmatter_field(text, "adr_number"))
        carrier = read_frontmatter_field(text, "carrier_story")
        date = read_frontmatter_field(text, "date")
        # 동일 filename 번호 중복(collision) 시 첫 파일만 index (backfill 대상 15 는 collision 무해당).
        by_num.setdefault(fnum, (base, fm_num, carrier, date))
    return by_num


def build_row(num, epic, date):
    """RESERVATION 표 row 문자열 (기존 row 컬럼 style 정합 — `| N | epic | active | reserved_at |`)."""
    reserved_at = f"{date} {BACKFILL_NOTE}"
    return f"| {num} | {epic} | active | {reserved_at} |"


def compute_plan(text, adr_index, slots, scope_min):
    """backfill 계획 산출 → (targets_appended, skipped, mismatches).

    targets = { fnum : file 존재 ∧ fnum >= scope_min ∧ fnum ∉ slots }  (INV-15 구조적 결정).
    INV-14: 이미 row 존재(fnum ∈ slots) slot 은 자동 제외 → 재실행 no-op.
    INV-16: filename 번호 ↔ frontmatter adr_number mismatch slot 은 skip + flag (잘못된 row 방지).
    """
    appended = []   # (num, row_str)
    skipped = []    # (num, reason)  — 이미 row 존재(no-op) 등
    mismatches = []  # (num, base, fm_num)

    candidates = sorted(n for n in adr_index if n >= scope_min and n not in slots)
    for num in candidates:
        base, fm_num, carrier, date = adr_index[num]
        if fm_num is not None and fm_num != num:
            mismatches.append((num, base, fm_num))
            continue
        if not carrier or not date:
            skipped.append((num, f"frontmatter carrier_story/date 부재 ({base})"))
            continue
        appended.append((num, build_row(num, carrier, date)))
    return appended, skipped, mismatches


def apply_backfill(text, appended):
    """마지막 표 row 뒤에 신규 row 삽입 (INV-13 append-only — 기존 line byte-identical).

    삽입점 = 마지막 `| N | ...` 표 row line 직후. 표 밖(archived heading 등) 무영향.
    """
    lines = text.split("\n")
    tbl_indices = [i for i, l in enumerate(lines) if re.match(r"^\|\s*\d+\s*\|", l)]
    if not tbl_indices:
        raise ValueError("RESERVATION 표 row 를 찾지 못함 — 삽입점 부재")
    last = tbl_indices[-1]
    new_rows = [row for _, row in appended]
    out = lines[:last + 1] + new_rows + lines[last + 1:]
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="ADR-RESERVATION lapse row idempotent backfill (CFP-2563 / ADR-133 A2, facet ②)")
    p.add_argument("--reservation-path", default="archive/adr/ADR-RESERVATION.md")
    p.add_argument("--adr-dir", default="archive/adr")
    p.add_argument("--scope-min", type=int, default=DEFAULT_SCOPE_MIN,
                   help=f"modern-window 하한 (default {DEFAULT_SCOPE_MIN} — Change Plan §2 '113+')")
    p.add_argument("--dry-run", action="store_true", help="미리보기만 (파일 미변경)")
    args = p.parse_args(argv)

    try:
        text = open(args.reservation_path, encoding="utf-8").read()
    except OSError as e:
        print(f"::error::RESERVATION 읽기 실패: {e}", file=sys.stderr)
        return 1

    slots = collect_reservation_slots(text)
    adr_index = index_adr_files(args.adr_dir)
    appended, skipped, mismatches = compute_plan(text, adr_index, slots, args.scope_min)

    print(f"[backfill 계획] scope-min={args.scope_min} / 기존 표 row {len(slots)}개")
    if mismatches:
        print(f"::warning::INV-16 slot↔file mismatch {len(mismatches)}건 (skip):")
        for num, base, fm in mismatches:
            print(f"  - slot {num}: {base} frontmatter adr_number={fm} (filename≠frontmatter, row 미생성)")
    if skipped:
        for num, reason in skipped:
            print(f"  - skip slot {num}: {reason}")

    if not appended:
        print("append 대상 0 — no-op (재실행 idempotent, INV-14).")
        return 0

    print(f"append 대상 {len(appended)}건: {', '.join(str(n) for n, _ in appended)}")
    for num, row in appended:
        print(f"  + {row}")

    if args.dry_run:
        print("\n[--dry-run] 파일 미변경.")
        return 0

    new_text = apply_backfill(text, appended)
    with open(args.reservation_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    print(f"\n✓ {len(appended)} row append 완료 → {args.reservation_path} (INV-13 append-only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
