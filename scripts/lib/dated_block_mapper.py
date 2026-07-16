#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/dated_block_mapper.py
CFP-2698 / Epic #2696 (canary artifact D6, Story A TOOL ROBUSTENING) — decision-record
문서 안에서 **dated region**(과거-스냅샷/이력 블록)에 속하는 라인 번호를 산출하는 순수 모듈.

목적:
  oracle(`decision_record_disposition.classify`) 의 tense 축(Q1)은 라인 텍스트 자체에서
  dated 신호(헤더/전이-화살표/inline-date 등)를 **line-level** 로 추론한다. 그러나 ADR 의
  `## Amendment N` 블록처럼, dated 임을 알려주는 신호가 그 라인 자체가 아니라 **frontmatter
  `amendments[].date` 필드**에만 있는 경우가 있다 — line-level 추론이 놓치는 사각.
  본 모듈은 그 **per-block(문서 구조 단위)** dated 신호를 별도로 산출해 oracle 에 추가
  근거(additive context)로 공급한다.

두 종류 dated region:
  (a) `## YYYY-MM-DD` 헤더 region — 헤더(선두 `#{1,6}` + ISO 날짜)가 열고, 동일-이하 레벨
      헤더 또는 EOF 까지 그 블록 전체(헤더 라인 포함)가 dated.
  (b) frontmatter `amendments[].date` → `## Amendment N` region — frontmatter(`---` 사이)
      안에 `amendments:` 리스트가 있고 그 원소 중 하나라도 `date:` 필드를 가지면, 본문의
      `## Amendment N` 헤더가 여는 블록(동일 규칙)도 dated 로 간주(amendment 블록은 날짜가
      inline 이 아니라 frontmatter 로 붙기 때문).

anti-overfit: 본 모듈의 어떤 함수도 파일 신원(경로/특정 라인 번호)을 하드코딩하지 않는다 —
  입력은 텍스트(또는 provider 를 통한 파일 경로 데이터)뿐이다.

resource-safety honest-ceiling (ADR-082 §결정 16):
  헤더/frontmatter 스캔은 라인-단위 순회이며 문서 길이에 선형(bounded)이다. 정규식은 전부
  bounded 형태(중첩 수량자 0)이나, 본 주석은 "임의 입력 무해(ReDoS-safe)"를 단정하지 않는다 —
  bounded degradation(정상 decision-record 문서에 대해 선형)만 주장한다. frontmatter
  amendments 탐지는 완전한 YAML 파서가 아니라 최소/견고 heuristic(PyYAML 있으면 fast-path,
  없으면 stdlib 라인-스캔 fallback)이다 — 엄밀한 YAML 문법 커버리지를 단정하지 않는다.

pure: 네트워크 0. `dated_line_numbers` 는 순수(텍스트 in → set out). 파일 I/O 는
  `make_dated_provider` 의 provider 클로저(제공된 경로만 읽음)와 CLI 층(`_main`)에 한정.
"""

import argparse
import json
import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# 정규식 (헤더 탐지 — bounded, 라인-단위)
# ─────────────────────────────────────────────────────────────────────────────
_GENERIC_HEADER_RE = re.compile(r"^\s*(#{1,6})\s")
_DATE_HEADER_RE = re.compile(r"^\s*(#{1,6})\s*\d{4}-\d{2}-\d{2}\b")
_AMENDMENT_HEADER_RE = re.compile(r"^\s*(#{1,6})\s*Amendment\s+\d+", re.IGNORECASE)
_AMENDMENTS_KEY_RE = re.compile(r"^(\s*)amendments\s*:")
_DATE_FIELD_RE = re.compile(r"\bdate\s*:")


def _region_end(lines, start_idx, level):
    """start_idx(0-indexed) 다음 줄부터 스캔해 동일-이하 레벨 헤더 또는 EOF 까지 region
    경계(0-indexed, half-open 우측 exclusive)를 반환."""
    n = len(lines)
    j = start_idx + 1
    while j < n:
        hm = _GENERIC_HEADER_RE.match(lines[j])
        if hm and len(hm.group(1)) <= level:
            break
        j += 1
    return j


def _collect_header_regions(lines, header_re):
    """header_re 에 매치하는 각 헤더 라인에서 region(0-indexed half-open [start,end)) 목록 반환."""
    regions = []
    n = len(lines)
    i = 0
    while i < n:
        m = header_re.match(lines[i])
        if m:
            level = len(m.group(1))
            end = _region_end(lines, i, level)
            regions.append((i, end))
            i = end
        else:
            i += 1
    return regions


def _split_frontmatter(text):
    """텍스트에서 frontmatter(`---` 사이) 라인 리스트를 반환 — frontmatter 없으면 None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def _has_dated_amendments_frontmatter(text):
    """frontmatter 안에 `amendments:` 리스트가 있고 그 원소 중 `date:` 필드를 가진 게 있는지.

    PyYAML 이 available 이면 fast-path 로 정식 파싱, 아니면(또는 파싱 실패 시) stdlib
    라인-스캔 fallback(엄밀 YAML 문법 파서 아님 — honest-ceiling, 상단 모듈 docstring 참조).
    """
    fm_lines = _split_frontmatter(text)
    if fm_lines is None:
        return False
    fm_text = "\n".join(fm_lines)

    try:
        import yaml  # optional fast-path — 하드 의존 아님(미설치 시 fallback)

        data = yaml.safe_load(fm_text)
        if isinstance(data, dict):
            amendments = data.get("amendments")
            if isinstance(amendments, list):
                return any(isinstance(a, dict) and "date" in a for a in amendments)
        return False
    except Exception:
        pass  # fallback 으로 진행

    # stdlib fallback: `amendments:` 키를 찾고, 그 다음부터 들여쓰기가 그 키 이상인 라인들
    # 중 `date:` 포함 여부만 본다(엄격 YAML 파싱 아님, bounded 단일-pass 라인 스캔).
    amend_indent = None
    start_at = None
    for idx, line in enumerate(fm_lines):
        m = _AMENDMENTS_KEY_RE.match(line)
        if m:
            amend_indent = len(m.group(1))
            start_at = idx + 1
            break
    if amend_indent is None:
        return False
    for line in fm_lines[start_at:]:
        if line.strip() == "":
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= amend_indent and not line.strip().startswith("-"):
            break  # amendments 블록 종료(형제/부모 키로 복귀)
        if _DATE_FIELD_RE.search(line):
            return True
    return False


def dated_line_numbers(text):
    """텍스트 안에서 dated region 에 속하는 1-indexed 라인 번호 집합 반환.

    (a) `## YYYY-MM-DD` 헤더 region — 헤더 포함, 동일-이하 레벨 헤더/EOF 까지.
    (b) frontmatter `amendments[].date` 존재 시 `## Amendment N` 헤더 region(동일 규칙).
    """
    lines = text.splitlines()
    dated = set()

    for start, end in _collect_header_regions(lines, _DATE_HEADER_RE):
        for i in range(start, end):
            dated.add(i + 1)

    if _has_dated_amendments_frontmatter(text):
        for start, end in _collect_header_regions(lines, _AMENDMENT_HEADER_RE):
            for i in range(start, end):
                dated.add(i + 1)

    return dated


def make_dated_provider(repo_root):
    """파일별 `dated_line_numbers` 를 최초 1회만 읽어 memoize 하는 provider 팩토리.

    반환 provider(path, lineno) -> Optional[bool]:
      True  — lineno 가 dated region 안(§블록/Amendment 블록).
      None  — dated 여부 판정 불가(파일 읽기 실패 포함) 또는 해당 라인이 dated region 밖.
              **never False** — per-block dated 는 ADDITIVE 근거일 뿐, 하위 `classify(..,
              dated_context=None)` 의 line-level 추론을 억제하지 않는다(제공 안 함 = 위임).
    """
    cache = {}

    def provider(path, lineno):
        if path not in cache:
            abspath = path if os.path.isabs(path) else os.path.join(repo_root, path)
            try:
                with open(abspath, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError):
                cache[path] = None
            else:
                cache[path] = dated_line_numbers(text)
        dset = cache[path]
        if dset is None:
            return None
        return True if lineno in dset else None

    return provider


# ─────────────────────────────────────────────────────────────────────────────
# CLI 층
# ─────────────────────────────────────────────────────────────────────────────
def _main(argv=None):
    ap = argparse.ArgumentParser(
        description="dated-block mapper — 라인이 dated region(과거-스냅샷/이력 블록) 안인지 판정."
    )
    ap.add_argument("--file", help="대상 파일 경로")
    ap.add_argument("--selfcheck", action="store_true", help="import/기동 sanity")
    args = ap.parse_args(argv)

    if args.selfcheck:
        print(json.dumps({"ok": True, "module": "dated_block_mapper"}, ensure_ascii=False))
        return 0

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False))
            return 1
        dated = sorted(dated_line_numbers(text))
        print(json.dumps(dated, ensure_ascii=False))
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    # DBM-2 / F5 utf-8 symmetry — Windows cp949 콘솔 UnicodeEncodeError 방지(CI ubuntu 무영향).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(_main())
