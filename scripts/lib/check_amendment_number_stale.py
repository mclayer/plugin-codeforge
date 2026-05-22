#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1216 / ADR-082 Amendment 6 §결정 9 — amendment-number-frontmatter-verify mechanical lint
# ADR-061 §결정 1 — Python SSOT (heredoc 금지), ADR-060 §결정 5 warning-tier
#
# 두 가지 검사 (warning-tier — exit 0 항상 for warnings):
#
#   Check (a) — ADR frontmatter self-consistency (PRIMARY):
#     각 docs/adr/ADR-*.md 파일에 대해:
#     1. YAML frontmatter 의 amendment id 목록 추출
#        (amendment_log: [{amendment_id: N}] 또는 amendments: [{amendment_id: N}] 또는
#         amendments: [{amendment: N}] 또는 amendments: ["ADR-NNN-Amendment-M-CFP-XXX"] 등)
#     2. 중복 id → [WARN]
#     3. gap → [WARN] advisory (exit 0, 의도적 gap 허용)
#     4. frontmatter max id ≠ body `## Amendment N` 헤더 max → [WARN]
#
#   Check (b) — cross-doc citation forward-staleness (SECONDARY):
#     변경된 non-ADR docs/** 파일에서 "ADR-NNN Amendment M" 패턴 grep.
#     대상 ADR frontmatter max id 조회 → M > max+1 이면 [WARN] (clearly-forward citation만)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (yaml.safe_load 파싱 실패 등 하드 오류)
#   2 — setup error (환경 오류)
#
# Usage:
#   python3 check_amendment_number_stale.py [options] [file ...]
#   Options:
#     --adr-dir DIR   ADR 조회 기준 디렉토리 (default: docs/adr — 스크립트 위치 기준 ../../docs/adr)

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

try:
    import yaml
except ImportError:
    print("[check-amendment-stale] pyyaml 미설치 — skip (exit 0)", file=sys.stderr)
    sys.exit(0)

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_AMENDMENT_NUMBER_STALE", "")
if BYPASS_ENV == "1":
    print("[check-amendment-stale] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-amendment-stale]"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# body 의 "## Amendment N" 헤더 패턴
BODY_AMENDMENT_RE = re.compile(r"^##\s+Amendment\s+(\d+)", re.MULTILINE)
# cross-doc citation 패턴: "ADR-NNN Amendment M" 또는 "ADR-NNN Amd M"
CITATION_RE = re.compile(r"ADR-(\d+)\s+(?:Amendment|Amd)\s+(\d+)", re.IGNORECASE)

# ── 인수 파싱 ─────────────────────────────────────────────────────────────────
def parse_args(argv):
    """인수에서 --adr-dir 와 파일 목록 분리."""
    adr_dir = None
    files = []
    i = 0
    while i < len(argv):
        if argv[i] == "--adr-dir" and i + 1 < len(argv):
            adr_dir = argv[i + 1]
            i += 2
        else:
            files.append(argv[i])
            i += 1
    return adr_dir, files

# ── ADR 디렉토리 해석 ─────────────────────────────────────────────────────────
def resolve_adr_dir(adr_dir_arg):
    """adr_dir_arg 가 None 이면 스크립트 위치 기준 ../../docs/adr fallback."""
    if adr_dir_arg:
        return Path(adr_dir_arg)
    # scripts/lib/ 기준 → scripts/ → repo root → docs/adr
    script_dir = Path(__file__).parent
    candidate = script_dir.parent.parent / "docs" / "adr"
    if candidate.is_dir():
        return candidate
    # 현재 작업 디렉토리 기준 fallback
    return Path("docs/adr")

# ── frontmatter 파싱 ──────────────────────────────────────────────────────────
def parse_frontmatter(text, filepath):
    """
    frontmatter YAML 파싱.
    반환: (fm_dict or None, body_text)
    파싱 실패 시 [WARN] + None 반환 (crash 금지).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text

    fm_raw = m.group(1)
    body = text[m.end():]
    try:
        fm = yaml.safe_load(fm_raw)
        if not isinstance(fm, dict):
            print(f"{SCRIPT_NAME} [WARN] {filepath}: frontmatter 가 dict 아님 — skip", file=sys.stderr)
            return None, body
        return fm, body
    except yaml.YAMLError as e:
        print(f"{SCRIPT_NAME} [WARN] {filepath}: frontmatter YAML 파싱 실패 ({e}) — skip", file=sys.stderr)
        return None, body

# ── amendment id 목록 추출 ────────────────────────────────────────────────────
def extract_amendment_ids(fm):
    """
    frontmatter dict 에서 amendment id 정수 목록 추출.
    지원하는 shape 3종:
      (A) amendment_log: [{amendment_id: N, ...}, ...]   (ADR-082 등)
      (B) amendments: [{amendment_id: N, ...}, ...]       (ADR-082 amendments 목록)
      (C) amendments: [{amendment: N, ...}, ...]          (ADR-063 등)
      (D) amendments: ["ADR-NNN-Amendment-M-CFP-XXX", ...] (ADR-027 등)
    여러 shape 가 공존할 수 있음 (amendment_log + amendments 모두 보유 시 합산).
    정수 변환 불가 항목은 skip (경고 없이).
    """
    def _try_int(val):
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    def _from_list(lst):
        result = []
        for item in lst:
            if isinstance(item, dict):
                # shape (A)/(B): amendment_id 키
                v = item.get("amendment_id")
                n = _try_int(v)
                if n is not None:
                    result.append(n)
                    continue
                # shape (C): amendment 키
                v = item.get("amendment")
                n = _try_int(v)
                if n is not None:
                    result.append(n)
                    continue
            elif isinstance(item, str):
                # shape (D): "ADR-NNN-Amendment-M-CFP-XXX" 문자열
                m = re.search(r"Amendment[-_](\d+)", item, re.IGNORECASE)
                if m:
                    n = _try_int(m.group(1))
                    if n is not None:
                        result.append(n)
        return result

    # amendment_log 와 amendments 는 동일 ADR 안에서 mirror 역할로 공존하는 경우가 있음
    # (ADR-082 등). 중복 집계 방지: 두 목록을 각각 파싱 후 set-union (per-source 내부 중복만 감지)
    al_ids = []
    al = fm.get("amendment_log")
    if isinstance(al, list):
        al_ids = _from_list(al)

    amd_ids = []
    amds = fm.get("amendments")
    if isinstance(amds, list):
        amd_ids = _from_list(amds)

    # set-union: amendment_log 와 amendments 간 교집합은 mirror 중복 (정상) — per-source 내 중복만 검사
    # 단, 두 소스 모두 보유 시 합산하면 false-duplicate 발생 → per-source 체크 후 union 반환
    # 실제 중복 검사는 각 source 별로 수행 (아래 check_adr_file 에서)
    # 반환값 = union (중복 제거) — max/gap 계산용
    all_ids_for_max = sorted(set(al_ids) | set(amd_ids))

    # 중복 검사용: 실제 중복이 있는 쪽 확인
    # (같은 id 가 amendment_log 에도, amendments 에도 있는 것은 mirror = 정상)
    # per-source 중 실제 중복 있는 id 만 반환
    seen_al = {}
    for n in al_ids:
        seen_al[n] = seen_al.get(n, 0) + 1
    seen_amd = {}
    for n in amd_ids:
        seen_amd[n] = seen_amd.get(n, 0) + 1

    dup_ids_per_source = []
    for n, cnt in seen_al.items():
        if cnt > 1:
            dup_ids_per_source.append(n)
    for n, cnt in seen_amd.items():
        if cnt > 1 and n not in dup_ids_per_source:
            dup_ids_per_source.append(n)

    # 반환 구조: (unique_ids_for_max_gap, dup_ids)
    # extract_amendment_ids 는 (ids, dup_ids) 튜플 반환으로 변경
    return all_ids_for_max, dup_ids_per_source

# ── Check (a): ADR frontmatter self-consistency ───────────────────────────────
def check_adr_file(filepath):
    """
    단일 ADR 파일 검사.
    반환: warn_count (int) — 경고 발생 횟수
    """
    path = Path(filepath)
    if not path.exists():
        print(f"{SCRIPT_NAME} [WARN] {filepath}: 파일 없음 — skip", file=sys.stderr)
        return 0

    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text, filepath)
    if fm is None:
        # 파싱 실패 — 이미 WARN 출력 완료
        return 0

    ids, dup_ids = extract_amendment_ids(fm)

    if not ids and not dup_ids:
        # amendment 없는 ADR — 검사 불필요
        return 0

    warn_count = 0

    # 1. 중복 id 검사 (per-source 중복만 — mirror 공존은 정상)
    if dup_ids:
        print(
            f"{SCRIPT_NAME} [WARN] {filepath}: amendment id duplicate 감지 (per-source) — {sorted(dup_ids)}",
            file=sys.stderr,
        )
        warn_count += 1

    # 2. gap 검사 (의도적 gap advisory)
    unique_ids = sorted(ids)
    if unique_ids:
        expected = list(range(unique_ids[0], unique_ids[-1] + 1))
        id_set = set(unique_ids)
        gaps = [n for n in expected if n not in id_set]
        for g in gaps:
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: amendment_log id gap — missing {g} (advisory, 의도적 gap 허용)",
                file=sys.stderr,
            )
        if gaps:
            warn_count += 1

    # 3. frontmatter max ≠ body max 검사
    fm_max = max(ids) if ids else None
    body_amendments = [int(m) for m in BODY_AMENDMENT_RE.findall(body)]
    body_max = max(body_amendments) if body_amendments else None

    if fm_max is not None and body_max is not None and fm_max != body_max:
        print(
            f"{SCRIPT_NAME} [WARN] {filepath}: frontmatter max amendment {fm_max} != body max Amendment {body_max}",
            file=sys.stderr,
        )
        warn_count += 1

    if warn_count == 0:
        print(f"{SCRIPT_NAME} OK: {filepath}", file=sys.stderr)

    return warn_count

# ── ADR number → max amendment id 조회 ───────────────────────────────────────
def build_adr_max_cache(adr_dir):
    """
    adr_dir 안의 ADR-*.md 파일을 scan 하여 {adr_number: max_amendment_id} dict 반환.
    """
    cache = {}
    adr_path = Path(adr_dir)
    if not adr_path.is_dir():
        return cache

    for adr_file in adr_path.glob("ADR-*.md"):
        # ADR number 파일명에서 추출
        m = re.match(r"ADR-(\d+)", adr_file.name)
        if not m:
            continue
        adr_num = int(m.group(1))

        text = adr_file.read_text(encoding="utf-8", errors="replace")
        fm, _ = parse_frontmatter(text, adr_file)
        if fm is None:
            continue
        ids, _ = extract_amendment_ids(fm)
        if ids:
            cache[adr_num] = max(ids)

    return cache

# ── Check (b): cross-doc citation forward-staleness ───────────────────────────
def check_doc_citations(filepath, adr_max_cache):
    """
    non-ADR docs/** 파일에서 "ADR-NNN Amendment M" 패턴 검색.
    M > max+1 이면 forward citation [WARN].
    반환: warn_count (int)
    """
    path = Path(filepath)
    if not path.exists():
        return 0

    text = path.read_text(encoding="utf-8", errors="replace")
    warn_count = 0

    for match in CITATION_RE.finditer(text):
        adr_num = int(match.group(1))
        cited_m = int(match.group(2))
        max_id = adr_max_cache.get(adr_num)
        if max_id is None:
            # 대상 ADR 파일 없음 — skip
            continue
        if cited_m > max_id + 1:
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: ADR-{adr_num} Amendment {cited_m} 인용 "
                f"but ADR-{adr_num} max = {max_id} (next = {max_id + 1}) — "
                f"possible stale-forward citation",
                file=sys.stderr,
            )
            warn_count += 1

    return warn_count

# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    adr_dir_arg, files = parse_args(sys.argv[1:])
    adr_dir = resolve_adr_dir(adr_dir_arg)

    total_warns = 0
    adr_files = []
    non_adr_files = []

    # 파일 분류: ADR 파일 vs non-ADR docs 파일
    for f in files:
        p = Path(f)
        name = p.name
        if re.match(r"ADR-\d+", name) and name.endswith(".md"):
            adr_files.append(f)
        else:
            non_adr_files.append(f)

    # Check (a): ADR 파일 self-consistency
    for adr_file in adr_files:
        total_warns += check_adr_file(adr_file)

    # Check (b): non-ADR docs citation forward-staleness
    if non_adr_files:
        cache = build_adr_max_cache(adr_dir)
        for doc_file in non_adr_files:
            total_warns += check_doc_citations(doc_file, cache)

    # 파일 미지정 시: adr_dir 전체 scan (Check (a) only)
    if not files:
        if adr_dir.is_dir():
            for adr_file in sorted(adr_dir.glob("ADR-*.md")):
                total_warns += check_adr_file(str(adr_file))
        else:
            print(f"{SCRIPT_NAME} INFO: ADR dir 없음 ({adr_dir}) — skip", file=sys.stderr)

    # warning-tier — 경고 수에 무관하게 exit 0 (PR merge 미차단)
    # exit 1 = 하드 오류 (yaml 파싱 실패 등) — 현재 구조에서는 WARN 처리 후 continue 이므로 도달 안 함
    if total_warns > 0:
        print(f"{SCRIPT_NAME} WARN: {total_warns}건 경고 감지 (warning-tier — PR merge 미차단)", file=sys.stderr)
    else:
        print(f"{SCRIPT_NAME} PASS: 경고 0건", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
