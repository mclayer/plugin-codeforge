#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADR cross-ref consistency lint — CFP-2478 / ADR-068 Amendment 7 layer A.
ADR-061 준수 — 외부 .py SSOT, no heredoc.

5 검사 (closed set — Change Plan §3.1 layer A a-e):
  (a) cross-ADR cross-ref 번호 존재 — ADR-NNN 인용 → archive/adr/ADR-NNN-*.md 실존.
      (b) phantom 전제 전용: sentinel>=900 + tests/** skip, (a) 단독 finding = 파일 부재 시만)
  (b) phantom ID ownership — ADR-NNN <ID> 인용 시 해당 ADR 이 <ID> 를 실 소유하는지.
      정의 grep = 행두∪list∪heading∪table∪bold prefix (P2-1 정정, 비협상).
  (c) enum SSOT 대조 — 정본 SSOT 명확 enum 한정 (ADR-052 touchpoint + ADR-039 inline-whitelist).
  (d) 버전 표기 parity — 기본 비활성 (--check-version opt-in). 자리표시.
  (e) content-anchor 대조 — 큰따옴표 인용구(>=8 chars) + (path)/(path:line) 인접 시 grep 실재.

exit code:
  0 = PASS (위반 0) / --self-test 전 fixture GREEN
  1 = 위반 검출 (warning-tier: CI continue-on-error)
  2 = SETUP/ENV error
  --self-test: 0 = 전 fixture 기대 verdict 일치, 비0 = fixture mismatch

ReDoS 안전: line-by-line, anchored simple regex, per-file 2000줄 cap.

Usage:
  python3 scripts/lib/check_adr_cross_ref_consistency.py [paths...]
  python3 scripts/lib/check_adr_cross_ref_consistency.py --self-test
  # paths 생략 시 현재 디렉터리 auto-scan
"""

import sys
import os
import re
import argparse
from pathlib import Path
import platform

# cross-platform stdout/stderr UTF-8 강제 (Windows cp949 콘솔에서 한글/em-dash UnicodeEncodeError 회피).
# CI(Linux)=이미 utf-8 → no-op. 로컬 Windows 콘솔 직접 출력 시 crash 방지 (errors=replace fail-safe).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass  # 일부 환경(파이프 래핑 등)에서 reconfigure 불가 — 무시 (fail-open)

# ---------------------------------------------------------------------------
# 플랫폼 경로 변환
# ---------------------------------------------------------------------------

def _posix_to_path(p):
    """POSIX /c/... 경로를 Windows 경로로 변환. Linux/macOS 는 그대로."""
    if platform.system() == 'Windows' and isinstance(p, str) and p.startswith('/') and len(p) >= 3 and p[2] == '/':
        drive = p[1].upper()
        return Path(drive + ':' + p[2:])
    return Path(p)


def _resolve_anchor_path(path_only, base_dir=None):
    """(e) content-anchor 의 본문-박힌 path 를 OS 실경로로 cross-platform 해석.

    본문 텍스트에 박힌 경로는 argv 가 아니므로 MSYS path-conversion 미적용 →
    Windows native python 이 직접 해석해야 한다. 3 케이스:
      1. POSIX 드라이브-레터 형태 (/c/foo) → _posix_to_path 변환.
      2. MSYS 가상 절대경로 (/tmp/..., /home/...) → Windows 에서 단순 Path() 는
         현재 드라이브 루트(C:\\tmp\\..)로 오해석 → tempfile.gettempdir() 기반 /tmp 매핑 보정.
      3. 상대경로 (archive/adr/..) → base_dir (스캔 파일 위치) 기준 해석 (production 경로 형태).
    반환 = 실재하는 첫 후보 Path, 없으면 마지막 후보.
    """
    candidates = []
    # 1. /c/ 드라이브-레터 형태
    p1 = _posix_to_path(path_only)
    candidates.append(p1)
    # 2. MSYS 가상 절대경로 보정 (Windows 한정)
    if platform.system() == 'Windows' and isinstance(path_only, str) and path_only.startswith('/'):
        import tempfile
        tmp_root = path_only
        # /tmp 접두 → 실 tempdir 로 치환 (fixture 환경)
        if tmp_root.startswith('/tmp/') or tmp_root == '/tmp':
            mapped = tempfile.gettempdir() + tmp_root[len('/tmp'):].replace('/', os.sep)
            candidates.append(Path(mapped))
    # 3. 상대경로 → base_dir 기준 (production 본문은 repo-상대 경로 인용)
    if base_dir is not None and not os.path.isabs(path_only) and not (isinstance(path_only, str) and path_only.startswith('/')):
        candidates.append(Path(base_dir) / path_only)
    for c in candidates:
        try:
            if c.is_file():
                return c
        except OSError:
            continue
    return candidates[-1]

# ---------------------------------------------------------------------------
# 스캔 설정
# ---------------------------------------------------------------------------

SCAN_EXTENSIONS = {'.md', '.yml', '.yaml'}

EXCLUDE_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv'}

# 자기 제외
EXCLUDE_FILES = {'check_adr_cross_ref_consistency.py'}

# sentinel ADR 번호 임계 (>=900 = 테스트 픽스처 예약)
L1_SENTINEL_THRESHOLD = 900

# tests/** 경로 제외 (L1 중복 완화)
L1_EXEMPT_PATH_PARTS = ('tests',)

# ADR 디렉터리 후보
ADR_DIR_CANDIDATES = ['archive/adr', 'docs/adr']

# per-file 줄 스캔 cap (ReDoS 안전)
PER_FILE_LINE_CAP = 2000

# ---------------------------------------------------------------------------
# (b) phantom ID 정의 grep 패턴 (P2-1 정정 — 행두∪list∪heading∪table∪bold prefix)
# 실 ADR 본문은 ID 정의를 **I-N: ...** bold prefix 로 적는다 (ADR-068 I-1~I-8).
# 행두-only 면 실소유 ID 미색인 → phantom 오판(false-positive cry-wolf, CE-1).
# §결정 N: heading 형태 = "### 결정 N — ..." (§기호 없이 "결정 N"), bold 형태 = "**§결정 N:**"
# citation 은 "ADR-NNN §결정 N" 으로 §기호 포함. 소유 탐지는 양 형태를 모두 색인.
# ---------------------------------------------------------------------------

# I-N: bold/list/heading/table prefix 형태
_I_DEFINE_PATTERN = re.compile(
    r'^\s*(?:[-*]\s+|#{1,6}\s+|\|\s*|\*\*)?(I-\d+)\b'
)

# §결정 N: bold/inline "**§결정 N**" 또는 "§결정 N:" 형태
_KETSUJYO_DEFINE_PATTERN = re.compile(
    r'^\s*(?:[-*]\s+|\|\s*|\*\*)?§결정\s+(\d+)\b'
)

# heading 형태 다종:
# "### 결정 N — ..." (§기호 없음, ADR-113 스타일)
# "### §결정 N — ..." (§기호 포함, ADR-119 스타일)
# "### N. title" (구형 숫자-only heading, ADR-008 등 — "§결정 N" citation 대응)
_HEADING_KETSUJYO_PATTERN = re.compile(
    r'^#+\s+§?결정\s+(\d+)\b'
)
# 구형 ADR 숫자-only heading: "### N. title" → owned 에 "§결정 N" 추가
_HEADING_NUMERIC_PATTERN = re.compile(
    r'^#+\s+(\d+)\.\s+\S'
)

# (b) 인용 탐지: "ADR-NNN §결정 M" 또는 "ADR-NNN I-M"
_CITATION_PATTERN = re.compile(
    r'\bADR-(\d+)\s+(I-\d+|§결정\s*\d+)\b'
)

# (a) ADR-NNN 단순 인용
_ADR_REF_PATTERN = re.compile(r'\bADR-(\d+)\b')

# (b)/(e) case-reference 면제 (CE-1 over-extraction 차단 — "드리프트 *케이스를 서술*" ≠ "드리프트를 *범함*").
# 감사기 자신/concept/ADR 가 phantom-ID·content-anchor 드리프트 *케이스* 를 예시·규칙으로 서술하면
# 그 줄에 "ADR-077 I-4" 같은 케이스-예시 인용이 나타난다 — 이는 live 오인용이 아니라 케이스 문서화.
# check_adr_citation_slug.py 의 META-tier 면제 (오인용 정정 / 정정 대상) precedent 답습.
# 정밀도 우선 closed-set 마커 (FP 재유발 방지) — 케이스 서술임을 강하게 시사하는 키워드만.
_CASE_REFERENCE_MARKERS = re.compile(
    r'phantom'
    r'|fact-check marker'
    r'|mis-?cite'
    r'|drift 케이스'
    r'|regression fixture'
    r'|distinct.{0,4}fixture'
    r'|실제 ADR-\d+ 소유'
    r'|실제 \*\*ADR-\d+\*\*'
    r'|줄번호 오기'
    r'|무검증 승격 금지'
    r'|verify-before-trust = ADR-\d+ I-\d+'
)

# ---------------------------------------------------------------------------
# (c) enum SSOT — Python dict 상수
# key = 식별자, value = 정본 enum 문자열 (정규식이 아닌 비교 대상 리터럴)
# ---------------------------------------------------------------------------

ENUM_SSOT = {
    # ADR-052 touchpoint 정본 = "<1|2|3|4|5|6|7|8>" (ADR-052 본문 content-anchor SSOT)
    'adr052_touchpoint': '<1|2|3|4|5|6|7|8>',
    # ADR-039 inline whitelist closed 4-entry
    # TC-1: 본문 "N번째 entry"(N>4) 인용 시 finding
    'adr039_inline_whitelist_count': 4,
}

# ADR-052 touchpoint 패턴 탐지: "touchpoint: <...>" 또는 "touchpoint <...>"
_TOUCHPOINT_PATTERN = re.compile(
    r'\btouchpoint[:\s]+(<[^>]+>)'
)
# 정본 SSOT 자기 정의 줄 skip — ADR-052 본문 내 literal (자기 대조 FAIL 방지)
_TOUCHPOINT_SSOT_VALUE = '<1|2|3|4|5|6|7|8>'

# ADR-039 ordinal: "N번째 entry" 패턴
_ORDINAL_ENTRY_PATTERN = re.compile(
    r'\bADR-039[^`\n]*?(\d+)번째\s+entry\b'
)

# ---------------------------------------------------------------------------
# (e) content-anchor 패턴
# 큰따옴표 인용구 + (path) 또는 (path:line) 같은 줄/인접
# ---------------------------------------------------------------------------

_QUOTED_TEXT_PATTERN = re.compile(r'"([^"]{8,})"')
_PATH_REF_PATTERN = re.compile(r'\(([^)]+?(?:\.md|\.yml|\.yaml|\.py|\.sh)[^)]*?)\)')
# markdown 링크 `[text](path)` 의 (path) 는 *링크 타깃* 이지 content-anchor 인용 아님 →
# (e) 검사 제외 (CE-1 FP 차단 — 링크 앞 텍스트는 prose, 링크된 파일에서 인용한 것 아님).
# `](` 직전 패턴으로 markdown 링크 타깃을 판별.
_MD_LINK_PATH_PATTERN = re.compile(r'\]\(([^)]+?(?:\.md|\.yml|\.yaml|\.py|\.sh)[^)]*?)\)')

# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def find_adr_dir(repo_root):
    for candidate in ADR_DIR_CANDIDATES:
        adr_dir = repo_root / candidate
        if adr_dir.is_dir():
            return adr_dir
    return None


def load_existing_adrs(adr_dir):
    """ADR-NNN -> filename 매핑 로드."""
    adrs = {}
    for path in adr_dir.glob('ADR-*-*.md'):
        m = re.match(r'ADR-(\d+)-(.+)\.md', path.name)
        if m:
            num = int(m.group(1))
            adrs[num] = path
    return adrs


def _is_l1_path_exempt(file_path):
    return any(part in L1_EXEMPT_PATH_PARTS for part in file_path.parts)


def _load_adr_owned_ids(adr_path):
    """대상 ADR 파일에서 self-소유 ID set 추출.
    정의 grep = 행두∪list∪heading∪table∪bold prefix (P2-1).
    I-N 과 §결정 N 양 형태 색인:
      - I-N: bold prefix "**I-N:**" / list "- I-N:" / heading
      - §결정 N: bold "**§결정 N**" / heading "### 결정 N —" (§기호 없음)
    """
    owned = set()
    try:
        content = adr_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return owned
    for line in content.splitlines():
        # I-N 형태 — group(1) 은 "I-7" 전체 (prefix 제외 capture group)
        m = _I_DEFINE_PATTERN.match(line)
        if m:
            owned.add(m.group(1))  # 이미 "I-N" 형태

        # §결정 N 형태 (§기호 포함 inline) — group(1) 은 숫자만
        m2 = _KETSUJYO_DEFINE_PATTERN.match(line)
        if m2:
            owned.add(f'§결정 {m2.group(1)}')

        # heading 형태: "### 결정 N" / "### §결정 N" — group(1) 은 숫자만
        m3 = _HEADING_KETSUJYO_PATTERN.match(line)
        if m3:
            owned.add(f'§결정 {m3.group(1)}')

        # 구형 ADR 숫자-only heading: "### N. title" → "§결정 N" 대응
        m4 = _HEADING_NUMERIC_PATTERN.match(line)
        if m4:
            owned.add(f'§결정 {m4.group(1)}')
    return owned

# ---------------------------------------------------------------------------
# 파일 검사
# ---------------------------------------------------------------------------

def check_file(file_path, existing_adrs, adr_dir, check_version=False):
    """단일 파일 검사. findings 리스트 반환."""
    findings = []
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return findings

    lines = content.splitlines()
    # ReDoS 안전: per-file 2000줄 cap
    if len(lines) > PER_FILE_LINE_CAP:
        lines = lines[:PER_FILE_LINE_CAP]

    l1_path_exempt = _is_l1_path_exempt(file_path)
    # 파일 경로를 문자열로 (리포트용)
    file_str = str(file_path)

    # (b) phantom ID: 파일 내 인용된 (ADR num, ID) 쌍 → 대상 ADR owned set 캐시
    _adr_owned_cache = {}

    # (e) content-anchor: 다음 줄을 위해 현재 줄 보존
    prev_line = ''
    prev_lineno = 0

    for lineno, line in enumerate(lines, 1):
        stripped = line.rstrip()

        # (a) cross-ADR 번호 존재 검사 (phantom 전제 전용)
        # sentinel/tests/** skip — (a) 단독 finding = ADR 파일 부재 시만
        if not l1_path_exempt and existing_adrs is not None:
            seen_on_line = set()
            for m in _ADR_REF_PATTERN.finditer(line):
                adr_num = int(m.group(1))
                if adr_num >= L1_SENTINEL_THRESHOLD:
                    continue
                if adr_num in seen_on_line:
                    continue
                seen_on_line.add(adr_num)
                if adr_num not in existing_adrs:
                    findings.append({
                        'file': file_str,
                        'line': lineno,
                        'check': 'a',
                        'content': stripped,
                        'reason': f'ADR-{adr_num:03d} 파일 부재 (archive/adr/ADR-{adr_num:03d}-*.md 미존재)',
                    })

        # (b) phantom ID ownership
        for m in _CITATION_PATTERN.finditer(line):
            adr_num = int(m.group(1))
            id_raw = m.group(2).strip()
            # §결정 공백 정규화
            id_str = re.sub(r'§결정\s+', '§결정 ', id_raw)

            if adr_num >= L1_SENTINEL_THRESHOLD:
                continue
            if l1_path_exempt:
                continue

            # 자기 정의 줄 skip: 같은 줄에 ADR-NNN 없이 <ID> 단독 행두/prefix → 인용 아님
            # (인용 = 한 줄에 ADR-NNN 과 ID 가 같이 나옴 → 이미 _CITATION_PATTERN 이 잡음)
            # 단, 이 줄 자체가 해당 ADR 이 소유한 ID 의 정의 줄이면 skip
            # → 대상 ADR num 과 현재 파일의 ADR num 이 일치할 때만 self-정의 가능
            # (현재 파일 = archive/adr/ADR-NNN-*.md 이고 NNN == adr_num 이면 자기 파일)
            is_self_definition = False
            if existing_adrs and adr_num in existing_adrs:
                self_adr_path = existing_adrs[adr_num]
                if file_path.resolve() == self_adr_path.resolve():
                    # 이 줄이 그 ID 의 정의 줄인지 확인 (I-N 또는 §결정/heading 결정)
                    if (_I_DEFINE_PATTERN.match(line) or
                            _KETSUJYO_DEFINE_PATTERN.match(line) or
                            _HEADING_KETSUJYO_PATTERN.match(line)):
                        is_self_definition = True

            if is_self_definition:
                continue

            # case-reference 면제 (CE-1): 이 줄이 phantom-ID 드리프트 *케이스를 서술* 하면 skip
            # (live 오인용 아님 — 감사기/concept/ADR 자기 케이스 문서화). over-extraction 차단.
            if _CASE_REFERENCE_MARKERS.search(line):
                continue

            # 대상 ADR owned ID set 로드 (캐시)
            if adr_num not in _adr_owned_cache:
                if existing_adrs and adr_num in existing_adrs:
                    _adr_owned_cache[adr_num] = _load_adr_owned_ids(existing_adrs[adr_num])
                else:
                    _adr_owned_cache[adr_num] = set()

            owned_set = _adr_owned_cache[adr_num]
            if id_str not in owned_set:
                findings.append({
                    'file': file_str,
                    'line': lineno,
                    'check': 'b',
                    'content': stripped,
                    'reason': f'phantom ID: ADR-{adr_num:03d} 는 "{id_str}" 을 소유하지 않음 (owned={sorted(owned_set)[:5]})',
                })

        # (c) enum SSOT 대조

        # (c-1) ADR-052 touchpoint enum
        for m in _TOUCHPOINT_PATTERN.finditer(line):
            token = m.group(1)
            if token == _TOUCHPOINT_SSOT_VALUE:
                # 정본 SSOT 자기 정의 줄 skip
                continue
            findings.append({
                'file': file_str,
                'line': lineno,
                'check': 'c',
                'content': stripped,
                'reason': f'ADR-052 touchpoint enum stale: "{token}" ≠ 정본 "{_TOUCHPOINT_SSOT_VALUE}"',
            })

        # (c-2) ADR-039 inline whitelist ordinal-vs-length (TC-1)
        for m in _ORDINAL_ENTRY_PATTERN.finditer(line):
            ordinal = int(m.group(1))
            closed_count = ENUM_SSOT['adr039_inline_whitelist_count']
            if ordinal > closed_count:
                findings.append({
                    'file': file_str,
                    'line': lineno,
                    'check': 'c',
                    'content': stripped,
                    'reason': f'ADR-039 inline whitelist ordinal drift: "{ordinal}번째 entry" > closed {closed_count}-entry',
                })

        # (e) content-anchor 대조
        # 현재 줄 또는 인접 줄(prev)에 (path) 참조가 있을 때 큰따옴표 인용구를 대상 파일에서 grep
        _check_content_anchor(line, lineno, stripped, file_str, findings, file_path.parent)
        # 이전 줄에 인용구가 있고 현재 줄에 path ref 가 있을 때도 체크
        if prev_line:
            _check_content_anchor_adjacent(prev_line, prev_lineno, line, file_str, findings, file_path.parent)

        prev_line = line
        prev_lineno = lineno

    return findings


def _strip_line_number(path_ref):
    """path:N 형식에서 trailing :N 을 제거. Windows 드라이브 레터(C:) 는 보존.
    예: 'archive/adr/ADR-068.md:155' → 'archive/adr/ADR-068.md'
        'C:\\path\\to\\file.md:42' → 'C:\\path\\to\\file.md'
        '/home/user/file.md' → '/home/user/file.md'
    """
    # trailing :<digits> 만 제거 (숫자 전용 suffix)
    stripped = re.sub(r':\d+$', '', path_ref.strip())
    return stripped


def _quotes_outside_backtick(line):
    """(e) 면제 (CE-1): backtick 코드 span 안의 큰따옴표 인용은 *코드 리터럴* (예:
    `findings[].type: "boundary-completeness"`) — '소스에서 인용한 텍스트' 아님 →
    content-anchor 대조 대상 제외. backtick span 밖 quote 만 반환.
    ReDoS 안전: 단순 char 스캔.
    """
    # backtick span 영역 마스킹: ` ... ` 쌍 안을 제거 후 quote 추출하면 span 안 quote 누락
    # → span 영역 char index set 을 구해 quote match 위치가 span 안이면 제외.
    spans = []  # (start, end) of backtick code spans
    idx = 0
    n = len(line)
    while idx < n:
        if line[idx] == '`':
            end = line.find('`', idx + 1)
            if end == -1:
                break  # dangling backtick — 이후 미처리 (안전: 면제 안 함)
            spans.append((idx, end))
            idx = end + 1
        else:
            idx += 1

    def _in_span(pos):
        return any(s <= pos <= e for s, e in spans)

    result = []
    for m in _QUOTED_TEXT_PATTERN.finditer(line):
        if not _in_span(m.start()):
            result.append(m.group(1))
    return result


def _path_refs_excluding_md_links(line):
    """(e) path-ref 중 markdown 링크 타깃 `[text](path)` 제외 (CE-1 FP 차단).
    링크 타깃은 '인용한 텍스트의 출처' 가 아니라 '링크 목적지' — content-anchor 대상 아님.
    """
    md_link_targets = set(_MD_LINK_PATH_PATTERN.findall(line))
    return [p for p in _PATH_REF_PATTERN.findall(line) if p not in md_link_targets]


def _check_content_anchor(line, lineno, stripped, file_str, findings, base_dir=None):
    """(e) 같은 줄: 큰따옴표 인용구 + (path) 참조 → 대상 파일 grep."""
    path_refs = _path_refs_excluding_md_links(line)
    if not path_refs:
        return
    # backtick 코드 리터럴 안 quote 는 content-anchor 대상 아님 (CE-1 면제)
    quotes = _quotes_outside_backtick(line)
    if not quotes:
        return
    for path_ref in path_refs:
        # line-number 무시: path:N suffix 만 제거, 드라이브 레터 보존
        path_only = _strip_line_number(path_ref)
        # cross-platform: 본문에 박힌 POSIX/MSYS/상대 경로를 OS 실경로로 해석
        # (Windows native pathlib 직접 변환 시 false-negative 회피 — _resolve_anchor_path)
        target = _resolve_anchor_path(path_only, base_dir)
        if not target.is_file():
            continue
        for quote_text in quotes:
            if not _text_exists_in_file(target, quote_text):
                findings.append({
                    'file': file_str,
                    'line': lineno,
                    'check': 'e',
                    'content': stripped,
                    'reason': f'content-anchor 미존재: "{quote_text[:40]}" 가 {path_only} 에서 발견 안 됨',
                })


def _check_content_anchor_adjacent(prev_line, prev_lineno, curr_line, file_str, findings, base_dir=None):
    """(e) 인접 줄: 이전 줄에 인용구, 현재 줄에 (path) 참조."""
    prev_quotes = _quotes_outside_backtick(prev_line)
    if not prev_quotes:
        return
    curr_path_refs = _path_refs_excluding_md_links(curr_line)
    if not curr_path_refs:
        return
    for path_ref in curr_path_refs:
        path_only = _strip_line_number(path_ref)
        # cross-platform 경로 해석 (Windows false-negative 회피 — _resolve_anchor_path)
        target = _resolve_anchor_path(path_only, base_dir)
        if not target.is_file():
            continue
        for quote_text in prev_quotes:
            if not _text_exists_in_file(target, quote_text):
                findings.append({
                    'file': file_str,
                    'line': prev_lineno,
                    'check': 'e',
                    'content': prev_line.rstrip(),
                    'reason': f'content-anchor 미존재(인접): "{quote_text[:40]}" 가 {path_only} 에서 발견 안 됨',
                })


def _text_exists_in_file(file_path, text):
    """텍스트가 파일 내에 존재하는지 (grep 대체). line-number 무시."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
        return text in content
    except OSError:
        return False

# ---------------------------------------------------------------------------
# 파일 수집
# ---------------------------------------------------------------------------

def collect_files(paths, repo_root):
    files = []
    for p in paths:
        target = _posix_to_path(str(p))
        if target.is_file():
            if target.name not in EXCLUDE_FILES:
                files.append(target)
        elif target.is_dir():
            for f in target.rglob('*'):
                if f.is_file() and f.suffix in SCAN_EXTENSIONS:
                    if not any(excl in f.parts for excl in EXCLUDE_DIRS):
                        if f.name not in EXCLUDE_FILES:
                            files.append(f)
    return sorted(set(files))

# ---------------------------------------------------------------------------
# --self-test (inline fixture)
# (a)(b)(c)(e) RED+GREEN 각 변별 최소 검증
# ---------------------------------------------------------------------------

def run_self_test():
    """inline fixture self-test. 0 = all GREEN, 비0 = mismatch."""
    failures = []

    def assert_finding(label, check_id, findings_list, expect_finding):
        matched = [f for f in findings_list if f['check'] == check_id]
        found = len(matched) > 0
        status = 'PASS' if found == expect_finding else 'FAIL'
        verdict = 'RED' if expect_finding else 'GREEN'
        actual = 'RED' if found else 'GREEN'
        print(f'[self-test] {status} {label} -- expected={verdict} actual={actual}')
        if status == 'FAIL':
            failures.append((label, expect_finding, found))

    import tempfile
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # ADR 디렉터리 픽스처
        adr_dir = tmp / 'archive' / 'adr'
        adr_dir.mkdir(parents=True)

        # ADR-068 픽스처: I-1~I-8 bold prefix 정의 포함
        adr068 = adr_dir / 'ADR-068-boundary-completeness-invariants.md'
        adr068.write_text(
            "# ADR-068\n"
            "**I-1:** API contract\n"
            "**I-2:** Cross-module\n"
            "**I-3:** Guard\n"
            "**I-4:** Wording SSOT\n"
            "**I-5:** Empirical\n"
            "**I-6:** Audit-gate\n"
            "**I-7:** Cross-ADR claim\n"
            "**I-8:** Standing surface\n",
            encoding='utf-8'
        )

        # ADR-039 픽스처: §결정 1~4 만 포함 (closed 4-entry)
        adr039 = adr_dir / 'ADR-039-orchestrator-spawn-constraints.md'
        adr039.write_text(
            "# ADR-039\n"
            "**§결정 1:** entry 1\n"
            "**§결정 2:** entry 2\n"
            "**§결정 3:** entry 3\n"
            "**§결정 4:** entry 4\n",
            encoding='utf-8'
        )

        # ADR-052 픽스처
        adr052 = adr_dir / 'ADR-052-codex-proactive-touchpoint.md'
        adr052.write_text(
            "# ADR-052\n"
            "touchpoint: <1|2|3|4|5|6|7|8>\n",
            encoding='utf-8'
        )

        existing_adrs = load_existing_adrs(adr_dir)

        # ---------------------------------------------------------------
        # (a) RED: ADR-999 은 sentinel → skip, ADR-001 은 파일 없음 → finding
        # ---------------------------------------------------------------
        doc_a_red = tmp / 'doc_a_red.md'
        doc_a_red.write_text("ADR-001 은 존재하지 않는 ADR 입니다.\n", encoding='utf-8')
        findings_a_red = check_file(doc_a_red, existing_adrs, adr_dir)
        assert_finding('(a) RED: 존재하지 않는 ADR-001', 'a', findings_a_red, True)

        # (a) GREEN: ADR-068 은 존재 → finding 없음
        doc_a_green = tmp / 'doc_a_green.md'
        doc_a_green.write_text("ADR-068 boundary completeness 참조.\n", encoding='utf-8')
        findings_a_green = check_file(doc_a_green, existing_adrs, adr_dir)
        assert_finding('(a) GREEN: 존재하는 ADR-068', 'a', findings_a_green, False)

        # ---------------------------------------------------------------
        # (b) RED: ADR-039 I-5 인용 (ADR-039 는 §결정만 소유, I-* 소유 0)
        # ---------------------------------------------------------------
        doc_b_red = tmp / 'doc_b_red.md'
        doc_b_red.write_text(
            "ADR-039 I-5 를 참조한다 (ADR-039 는 I-* 없음).\n",
            encoding='utf-8'
        )
        findings_b_red = check_file(doc_b_red, existing_adrs, adr_dir)
        assert_finding('(b) RED: ADR-039 I-5 phantom', 'b', findings_b_red, True)

        # (b) RED (TC-3): ADR-077 은 픽스처에 없음 → (a) finding. I-4 phantom 도 있어야
        # → ADR-077 파일 없으면 owned=set() → I-4 ∉ set() → (b) RED
        doc_b_red2 = tmp / 'doc_b_red2.md'
        doc_b_red2.write_text(
            "ADR-077 I-4 참조한다 (ADR-077 미존재).\n",
            encoding='utf-8'
        )
        findings_b_red2 = check_file(doc_b_red2, existing_adrs, adr_dir)
        assert_finding('(b) RED (TC-3): ADR-077 I-4 phantom', 'b', findings_b_red2, True)

        # (b) GREEN (TC-3b): ADR-068 I-7 인용 (bold prefix 로 정의된 실 소유 ID)
        doc_b_green = tmp / 'doc_b_green.md'
        doc_b_green.write_text(
            "ADR-068 I-7 cross-ADR claim consistency 를 참조한다.\n",
            encoding='utf-8'
        )
        findings_b_green = check_file(doc_b_green, existing_adrs, adr_dir)
        assert_finding('(b) GREEN (TC-3b): ADR-068 I-7 prefix-form 실소유', 'b', findings_b_green, False)

        # ---------------------------------------------------------------
        # (c) RED: touchpoint enum stale
        # ---------------------------------------------------------------
        doc_c_red = tmp / 'doc_c_red.md'
        doc_c_red.write_text(
            "touchpoint: <1..6> 는 stale 형태입니다.\n",
            encoding='utf-8'
        )
        findings_c_red = check_file(doc_c_red, existing_adrs, adr_dir)
        assert_finding('(c) RED: touchpoint enum stale', 'c', findings_c_red, True)

        # (c) GREEN: 정본과 일치
        doc_c_green = tmp / 'doc_c_green.md'
        doc_c_green.write_text(
            "touchpoint: <1|2|3|4|5|6|7|8> 정본.\n",
            encoding='utf-8'
        )
        findings_c_green = check_file(doc_c_green, existing_adrs, adr_dir)
        assert_finding('(c) GREEN: touchpoint 정본 일치', 'c', findings_c_green, False)

        # (c) RED (TC-1): ADR-039 ordinal drift
        doc_c_tc1 = tmp / 'doc_c_tc1.md'
        doc_c_tc1.write_text(
            "ADR-039 §결정 2 inline whitelist 의 5번째 entry 를 참조한다.\n",
            encoding='utf-8'
        )
        findings_c_tc1 = check_file(doc_c_tc1, existing_adrs, adr_dir)
        assert_finding('(c) RED (TC-1): ADR-039 5번째 entry > closed 4', 'c', findings_c_tc1, True)

        # ---------------------------------------------------------------
        # (e) RED: content-anchor 인용구 대상 파일 미존재
        # ---------------------------------------------------------------
        # 실재하는 파일 생성
        anchor_file = tmp / 'anchor_target.md'
        anchor_file.write_text("이 파일에는 실재하는 텍스트입니다.\n", encoding='utf-8')

        doc_e_red = tmp / 'doc_e_red.md'
        doc_e_red.write_text(
            f'"이 텍스트는 대상 파일에 없음" ({anchor_file})\n',
            encoding='utf-8'
        )
        findings_e_red = check_file(doc_e_red, existing_adrs, adr_dir)
        assert_finding('(e) RED: content-anchor 미존재', 'e', findings_e_red, True)

        # (e) GREEN: 인용구가 대상 파일에 실재
        doc_e_green = tmp / 'doc_e_green.md'
        doc_e_green.write_text(
            f'"이 파일에는 실재하는 텍스트입니다" ({anchor_file})\n',
            encoding='utf-8'
        )
        findings_e_green = check_file(doc_e_green, existing_adrs, adr_dir)
        assert_finding('(e) GREEN: content-anchor 실재', 'e', findings_e_green, False)

    total = 10
    passed = total - len(failures)
    print()
    print(f'[self-test] {passed}/{total} fixtures PASSED')
    if failures:
        print('[self-test] FAILURES:')
        for label, exp, act in failures:
            print(f'  FAIL {label} | expected={exp} actual={act}')
        return 1
    print('[self-test] ALL GREEN')
    return 0

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description='ADR cross-ref consistency lint (CFP-2478 / ADR-068 Amendment 7 layer A)'
    )
    parser.add_argument('paths', nargs='*', help='검사할 파일 또는 디렉터리 (기본: 현재 디렉터리)')
    parser.add_argument('--repo-root', default='.', help='저장소 루트 경로')
    parser.add_argument('--self-test', action='store_true', help='inline fixture self-test 실행')
    parser.add_argument('--check-version', action='store_true',
                        help='(d) 버전 표기 parity 검사 활성화 (기본 비활성 — high-FP)')
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    repo_root = _posix_to_path(args.repo_root).resolve()
    scan_paths = args.paths if args.paths else [str(repo_root)]

    # ADR 디렉터리 로드
    adr_dir = find_adr_dir(repo_root)
    if adr_dir is None:
        print(f"WARN: ADR 디렉터리 미발견 ({', '.join(ADR_DIR_CANDIDATES)}) — (a)(b) 검사 skip",
              file=sys.stderr)
        existing_adrs = None
    else:
        existing_adrs = load_existing_adrs(adr_dir)

    files = collect_files(scan_paths, repo_root)

    all_findings = []
    for f in files:
        findings = check_file(f, existing_adrs, adr_dir, check_version=args.check_version)
        all_findings.extend(findings)

    if not all_findings:
        print(f'[adr-cross-ref-consistency] PASS — 위반 0 ({len(files)} 파일 검사)')
        return 0

    # 위반 보고
    by_check = {}
    for f in all_findings:
        by_check.setdefault(f['check'], []).append(f)

    total = len(all_findings)
    counts = {k: len(v) for k, v in by_check.items()}
    print(f'[adr-cross-ref-consistency] 위반: {total} ({counts}):')

    for check_id in sorted(by_check.keys()):
        for v in by_check[check_id]:
            print(f'  ({check_id.upper()})  {v["file"]}:{v["line"]}: {v["reason"]}')
            print(f'       {v["content"][:120].encode("ascii", "replace").decode("ascii")}')

    print()
    print('NOTE: warning-tier (ADR-060 §결정 5) -- CI continue-on-error, PR merge 차단 아님.')
    print('NOTE: bypass = hotfix-bypass:boundary-wording label 부착.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
