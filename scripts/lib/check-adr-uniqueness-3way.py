#!/usr/bin/env python3
# scripts/lib/check-adr-uniqueness-3way.py
# CFP-2563 / ADR-133 Amendment 2 (A2-6) — ADR 번호 3-way uniqueness lint (facet ③, warning tier).
#
# SSOT 근거:
#   - ADR-133 Amendment 2 A2-6 — file명 ↔ frontmatter adr_number ↔ RESERVATION row 3-way uniqueness lint.
#         OCC(§결정2) = 발급-시점 1차 차단 / 본 lint = 사후 2차 안전망(defense-in-depth). warning tier
#         이므로 branch protection 고정 6-tuple 무변경(ADR-060 warning-tier framework 정합).
#   - Change Plan §3.3 — dual-key(filename ∧ frontmatter) + mismatch flag + 구조적 파싱 + numeric 정규화.
#   - Change Plan §8.1/§8.2 invariant:
#         INV-8  dual-key(filename∧frontmatter) 둘 다 검사 (filename-only 는 frontmatter-collision 누락)
#         INV-9  filename↔frontmatter mismatch flag
#         INV-10 구조적 파싱 (RESERVATION 첫 열 slot number + filename regex + frontmatter parse.
#                row 본문 문자열 grep 금지 — ADR cross-ref noise 오탐 회피, EC-6)
#         INV-11 numeric 정규화 (zero-pad `ADR-72` vs `073` + quoted-string `"005"` 를 int 로 정규화)
#         INV-12 file↔row lapse (file 존재 ∧ RESERVATION row 부재 = lapse)
#
# 판정: finding 1건 이상이면 exit 1 (findings 를 type 별 그룹으로 출력). warning-tier semantics —
#       WORKFLOW(adr-uniqueness-check.yml) 은 non-required(InfraEngineer 배선)이나, 스크립트 자체는
#       finding 시 exit 1 (테스트가 RED→GREEN 관측 가능). merge 차단은 워크플로 tier 가 결정.
#
# firsthand 기존 결함 (lint 은 검출만 — 정정은 별 Story 소관):
#   - filename-collision : ADR-042 (2 파일) —
#         **CFP-2566 renumber 진행 대상**(잔여 1쌍 — C1 이 ADR-047 gitops-agent → ADR-160, C2 가 ADR-056 domain-concept → ADR-161, C3 가 ADR-048 ghec-governance → ADR-162 이동으로 해소).
#         C0 shared-infra + C1(047) + C2(056) + C3(048) merge 후 real archive/adr 에 1쌍 잔존(이후 C4 per-pair child 가 042 해소).
#   - zero-pad drift : ADR-72 (2-digit token, 관례 3-digit) — OOS(CFP-676 이 2-digit canonical 확정, 사용자 결정 대기)
#   - file-row-lapse : ADR-144/156/157/158/159 (RESERVATION row 부재) — OOS(별 finding class, 중복쌍 무관)
#   - quoted-string : ADR-005 fm=`"005"` → 정규화 5 (mismatch 아님 — 정규화가 false-positive 차단)
# NOTE: 구 frontmatter-collision(ADR-043+ADR-045 fm=43 / ADR-061+ADR-062 fm=61) + filename↔frontmatter
#       mismatch(ADR-045 45≠43 / ADR-062 62≠61) = CFP-2759(2026-07-19 merged)로 정정 완료 → 잔여 finding 아님.
#
# Usage:
#   python3 scripts/lib/check-adr-uniqueness-3way.py \
#       [--adr-dir archive/adr] \
#       [--reservation-path archive/adr/ADR-RESERVATION.md] \
#       [--lapse-scope-min 113]
#
# exit 0 = finding 0 / exit 1 = finding 1+ (또는 입력 오류).

import argparse
import glob
import os
import re
import sys

# Windows cp949 stdout 차단 (ADR-061 표준 — neighbor check_doc_frontmatter.py 정합)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# RESERVATION 레지스트리 파일 자체(adr_number: null) 는 ADR decision 파일이 아님 — 정확 basename 으로만 제외.
# ⚠ substring "reservation" 제외 금지: ADR-133-adr-*reservation*-atomic-claim.md / ADR-036-*-atomic-*reservation*.md
#   가 basename 에 "reservation" 을 포함 → substring 제외 시 실 ADR 2건 누락(firsthand 확인된 함정).
RESERVATION_BASENAME = "ADR-RESERVATION.md"

# 관례 zero-pad 폭 (ADR-NNN 3-digit). token 이 이 폭과 다르면 zero-pad drift(문자열 sort vs 숫자 sort 발산).
CANONICAL_PAD_WIDTH = 3

# file↔row lapse 판정 범위 하한 (Change Plan §2 "113+" / §11.4 "15 → 0" / §3.4 "15행 lapse").
# 레지스트리 modern-era 실 유지 범위 = ADR-113 이후. 그 이전(pre-registry) ADR 은 non-goal(§5) — lapse 대상 외.
DEFAULT_LAPSE_SCOPE_MIN = 113


def normalize_number(raw):
    """token/frontmatter 값을 numeric int 로 정규화 (INV-11).

    zero-pad(`72`,`073`,`005`) + quoted-string(`"005"`,`'5'`) 흡수. 정수 아님 → None.
    """
    if raw is None:
        return None
    s = str(raw).strip().strip('"').strip("'").strip()
    m = re.fullmatch(r"0*(\d+)", s)
    return int(m.group(1)) if m else None


def read_frontmatter_field(text, field):
    """frontmatter block 에서 단일 field 값 추출 (regex — pyyaml 의존 없이 결정적).

    frontmatter 관례 = neighbor check_doc_frontmatter.py 와 동일 split (`\\n---\\n` 경계).
    """
    if not text.startswith("---\n"):
        return None
    fm_text = text.split("\n---\n", 1)[0][4:]
    m = re.search(rf"^{re.escape(field)}:\s*(.+?)\s*$", fm_text, re.M)
    return m.group(1).strip() if m else None


def collect_adr_files(adr_dir):
    """ADR decision 파일 스캔 → [(basename, filename_token, filename_num, frontmatter_num)].

    filename 측 = filename regex `ADR-0*(\\d+)-` (INV-10 구조적). frontmatter 측 = frontmatter parse.
    """
    records = []
    for path in sorted(glob.glob(os.path.join(adr_dir, "ADR-*.md"))):
        base = os.path.basename(path)
        if base == RESERVATION_BASENAME:
            continue
        m = re.match(r"ADR-(\d+)-", base)
        if not m:
            # 번호 없는 ADR 파일명 (관례 위반) — 검사 대상 표시 위해 기록하되 번호 None.
            records.append((base, None, None, None))
            continue
        token = m.group(1)
        fname_num = normalize_number(token)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"::error::ADR 파일 읽기 실패: {path} ({e})", file=sys.stderr)
            fm_num = None
        else:
            fm_num = normalize_number(read_frontmatter_field(text, "adr_number"))
        records.append((base, token, fname_num, fm_num))
    return records


def collect_reservation_slots(reservation_path):
    """RESERVATION.md markdown 표의 첫 열 slot number 집합 (INV-10 구조적 — row 본문 grep 금지).

    판정 = 각 표 row 의 **첫 열** 정수만. `| 113 | ... |` → 113. YAML amendments_reserved[] 블록
    (`- adr_number: N`) · row 본문 cross-ref("ADR-137 참조") 는 첫-열 정규식 밖 → 오탐 0.
    """
    slots = set()
    try:
        text = open(reservation_path, encoding="utf-8").read()
    except OSError as e:
        print(f"::error::RESERVATION 파일 읽기 실패: {reservation_path} ({e})", file=sys.stderr)
        return None
    for line in text.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|", line)
        if m:
            slots.add(normalize_number(m.group(1)))
    return slots


def compute_findings(records, slots, lapse_scope_min):
    findings = {
        "filename-collision": [],
        "frontmatter-collision": [],
        "filename-frontmatter-mismatch": [],
        "zero-pad-normalized-collision": [],
        "file-row-lapse": [],
    }

    # ── filename-collision (INV-8, filename-key) ──
    by_fname = {}
    for base, token, fname_num, fm_num in records:
        if fname_num is not None:
            by_fname.setdefault(fname_num, []).append(base)
    for num in sorted(k for k, v in by_fname.items() if len(v) > 1):
        files = sorted(by_fname[num])
        findings["filename-collision"].append(f"ADR 번호 {num}: {len(files)} 파일 — {', '.join(files)}")

    # ── frontmatter-collision (INV-8, frontmatter-key — filename-only 는 누락) ──
    by_fm = {}
    for base, token, fname_num, fm_num in records:
        if fm_num is not None:
            by_fm.setdefault(fm_num, []).append(base)
    for num in sorted(k for k, v in by_fm.items() if len(v) > 1):
        files = sorted(by_fm[num])
        findings["frontmatter-collision"].append(
            f"frontmatter adr_number {num}: {len(files)} 파일 — {', '.join(files)}")

    # ── filename ↔ frontmatter mismatch (INV-9) ──
    for base, token, fname_num, fm_num in records:
        if fname_num is not None and fm_num is not None and fname_num != fm_num:
            findings["filename-frontmatter-mismatch"].append(
                f"{base}: filename 번호 {fname_num} ≠ frontmatter adr_number {fm_num}")

    # ── zero-pad drift (INV-11 — 문자열 sort vs 숫자 sort 발산) ──
    for base, token, fname_num, fm_num in records:
        if token is not None and fname_num is not None:
            canonical = f"{fname_num:0{CANONICAL_PAD_WIDTH}d}"
            if token != canonical:
                findings["zero-pad-normalized-collision"].append(
                    f"{base}: filename token '{token}' 관례 zero-pad('{canonical}') 불일치 "
                    f"(정규화 slot {fname_num})")

    # ── file ↔ row lapse (INV-12 — modern-window 범위, Change Plan §2 "113+") ──
    if slots is not None:
        seen = set()
        for base, token, fname_num, fm_num in records:
            if fname_num is None or fname_num in seen:
                continue
            seen.add(fname_num)
            if fname_num >= lapse_scope_min and fname_num not in slots:
                findings["file-row-lapse"].append(
                    f"ADR-{fname_num:0{CANONICAL_PAD_WIDTH}d} ({base}): 파일 존재 ∧ RESERVATION row 부재 (lapse)")

    return findings


def main(argv=None):
    p = argparse.ArgumentParser(
        description="ADR 번호 3-way uniqueness lint (file명 ↔ frontmatter ↔ RESERVATION row, ADR-133 A2-6 warning tier)")
    p.add_argument("--adr-dir", default="archive/adr", help="ADR 파일 디렉터리 (default: archive/adr)")
    p.add_argument("--reservation-path", default="archive/adr/ADR-RESERVATION.md",
                   help="RESERVATION 레지스트리 경로")
    p.add_argument("--lapse-scope-min", type=int, default=DEFAULT_LAPSE_SCOPE_MIN,
                   help=f"file↔row lapse 판정 하한 (default {DEFAULT_LAPSE_SCOPE_MIN} — Change Plan §2 '113+')")
    args = p.parse_args(argv)

    records = collect_adr_files(args.adr_dir)
    slots = collect_reservation_slots(args.reservation_path)
    if slots is None:
        return 1

    findings = compute_findings(records, slots, args.lapse_scope_min)
    total = sum(len(v) for v in findings.values())

    if total == 0:
        print("✓ ADR 3-way uniqueness: file명 ↔ frontmatter ↔ RESERVATION row 정합 (finding 0)")
        return 0

    print(f"::error::ADR 3-way uniqueness lint — {total} finding (warning tier, ADR-133 A2-6)")
    for ftype in ("filename-collision", "frontmatter-collision", "filename-frontmatter-mismatch",
                  "zero-pad-normalized-collision", "file-row-lapse"):
        items = findings[ftype]
        if not items:
            continue
        print(f"\n[{ftype}] ({len(items)})")
        for it in items:
            print(f"  - {it}")
    print("\n(참고: OCC claim = 발급-시점 1차 차단 / 본 lint = 사후 2차 안전망. "
          "중복·mismatch 정정은 별도 follow-up Story — 본 lint 는 검출만, Change Plan §5 non-goal.)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
