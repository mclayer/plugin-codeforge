#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_lane_count_ssot.py
CFP-2426 / ADR-060 Amendment 19 §결정 33 — lane-count SSOT consistency 게이트 (warning tier)

canonical 작업레인(lane) 수 = 10 (ADR-125 Amendment 1 / CFP-2341) 이 governance 문서
전반에서 단조 유지되는지 grep-기반 mechanical lint 로 검출. 현재-상태 lane-count 단언
(N 레인 / N번째 lane / 레인 N개, N≠10 = N∈{5,6,7,8,9}) 가 canonical=10 과 어긋나면 FLAG.
5축 allowlist (within-line 이중토큰 / negation / history / path / counterfactual) 가
false-positive 를 channel(line-prefix key) 단위로 차단.

배경 (33.A — 메우는 갭): ADR-125 Amendment 1 이 canonical=10 을 정본 SSOT 로 박았으나
(registration), 분산 governance 문서 사본이 그 사실에 단조 유지되도록 강제하는 mechanical
enforcement 부재 → stale `N 레인`/`N번째 lane`(N≠10) drift 가 2 Story 연속(CFP-2341 →
CFP-2376) leak. "registration 완료 ≠ enforcement 실효" 전형.

Usage:
  python3 check_lane_count_ssot.py check [--repo-root <path>] [--paths <glob> ...]
    → in-scope 경로 전수 scan, FLAG 1+ 면 exit 1 (warning), FLAG 0 면 exit 0

Exit codes (ADR-060 §결정 15 3-tier — warning tier):
  0 = PASS (FLAG 0)
  1 = FLAG 1+ (`::warning::check-lane-count-ssot: FLAG ...` emit — workflow 의 continue-on-error
       로 비차단, advisory only)
  2 = SETUP error (검사 경로 부재 / python3 미설치 / 파일 read 실패)

검출 1급 firing 조건 (33.B):
  flag(line) := stale_token_match(line) AND NOT allowlist_match(line)

ReDoS-safe (ADR-061 Amd3 CodeQL guard):
  - line-by-line scan (multi-line backtracking regex 0).
  - anchored bounded-quantifier regex (nested quantifier 0).
  - amendment_log span(③-b) = line-local boolean toggle `in_amendment_span` 1개
    (multi-line regex 아님 — O(lines) bounded). enter(헤더 key)~exit(dedent·다음 top-level key).
    선례 = scripts/lib/check_issue_body_claim_pre_screen.py 의 in_fence toggle
    (check_decision_principle_vocabulary.py 답습).

N-range = canonical-10 특정값 detection (33.B / §7.B9 D4 documented-limitation):
  현 정규식 N∈{5,6,7,8,9} 하드코딩은 canonical=10 기준. 미래 lane 증감(canonical→11) 시
  `11 레인` 류를 silent 미검출(false-negative)하며 self-test({5..9} fixture)도 이 갭 미검출.
  → lane count canonical 값을 바꾸는 미래 ADR-125 Amendment 는 본 lint 의 N-range 정규식 갱신
  (+ self-test fixture range 확장)을 그 Amendment 의 REQUIRED mechanical-sync carrier 항으로
  포함해야 한다 (구조 재설계 불요 — 범위 갱신만).

Prior art (worktree 실존 확인 — ADR-119):
  scripts/lib/check_issue_body_claim_pre_screen.py  (line-by-line in_fence boolean toggle masking)
  scripts/lib/check_governance_drift.py             (git ls-files path walk + ::warning:: + advisory exit)
  scripts/check-deferred-followup-reconcile.sh      (ADR-061 thin wrapper)

ADR refs: ADR-060 Amendment 19 §결정 33 / ADR-125 Amendment 1 / ADR-061 / ADR-104 / ADR-127
"""

import argparse
import os
import re
import subprocess
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────── 검사 / 제외 경로 (§7.B2 A1 / 축④) ──────────────────────

# 검사 대상 경로 glob (git ls-files 인자). docs/·CLAUDE.md·plugins/·scripts/·templates/·plugin.json.
DEFAULT_SCAN_GLOBS = [
    "docs",
    "CLAUDE.md",
    "plugins",
    "scripts",
    "templates",
    ".claude-plugin/plugin.json",
]

# 제외 경로 prefix (축④ — ADR 원기록 history / 역사 스냅샷). path-prefix match.
EXCLUDE_PATH_PREFIXES = (
    "archive/adr/",
    "docs/cross-repo-patches/",
)

# 본 lint 자기 자신(검출 토큰 예시 보유 — 자기 검출 회피, Amd19 §33.D).
SELF_EXCLUDE_PATHS = (
    "scripts/lib/check_lane_count_ssot.py",
    "scripts/check-lane-count-ssot.sh",
    "scripts/test-check-lane-count-ssot.sh",
    ".github/workflows/lane-count-ssot.yml",
)


# ─────────────────────── 검출 정규식 (§7.B2 — STALE 토큰, ReDoS-safe) ─────────────
# N∈{5,6,7,8,9} (canonical=10 외 현 surface 실측 등장 정수). bounded quantifier, nested 0.

# 한글 lane 표기: `9 레인`·`8 레인` (앞에 숫자 비인접 — `18 에이전트` 등 오매칭 회피는 history 축에서)
_RE_HANGUL_LANE = re.compile(r"(?<![0-9])([6-9])\s{0,3}레인")
# 한글 lane 표기 (개-form): `레인 5개`·`레인 8개`
_RE_HANGUL_LANE_GAE = re.compile(r"레인\s{0,3}([5-9])개")
# 영문 표기: `9번째 lane` (앞에 숫자 비인접 — `16번째 lane`/`26번째 lane` 류 leading-digit
#   false-FLAG 차단, 한글형 `_RE_HANGUL_LANE` 가드 대칭화. F-CR-2426-P2)
_RE_ENG_ORDINAL_LANE = re.compile(r"(?<![0-9])([6-9])번째\s{0,3}lane")

_DETECT_PATTERNS = [_RE_HANGUL_LANE, _RE_HANGUL_LANE_GAE, _RE_ENG_ORDINAL_LANE]


def stale_token_match(line):
    """line 에 STALE lane-count 토큰(N≠10)이 등장하면 매치 객체 반환, 없으면 None."""
    for pat in _DETECT_PATTERNS:
        m = pat.search(line)
        if m:
            return m
    return None


# ─────────────────────── allowlist 5축 (§7.B3 — load-bearing) ────────────────────
# 면제 단위 = syntactic channel(line-prefix key) 또는 counterfactual 마커, 토큰 자체 아님.

# 축① within-line 이중토큰: 같은 라인에 `N lane plugin` (plugin-count) 인접 →
#   그 토큰만 면제 (라인 전체 면제 아님 — 잔여 stale 은 §7.B3 라인-단위라 잔여 stale_token_match 가 별 라인이면 검출).
#   `8 lane plugin`·`6 lane plugin`·`8개 lane plugin`. detect 정규식(레인/lane)과 분리 채널.
_RE_AXIS1_DUAL_TOKEN = re.compile(r"([6-9])\s{0,3}개?\s{0,3}lane plugin")

# 축② negation: `N번째 lane (이|은|는)? 아(니|님|닌)` (부정 토큰 인접) → 면제.
_RE_AXIS2_NEGATION = re.compile(r"([6-9])번째\s{0,3}lane\s{0,3}(?:이|은|는)?\s{0,3}아(?:니|님|닌)")

# 축③-a date행: frontmatter `date:` 또는 ISO 날짜 선두.
_RE_AXIS3A_DATE = re.compile(r"^\s{0,8}date:\s|^\s{0,8}-?\s{0,3}\d{4}-\d{2}-\d{2}")

# 축③-b history — 2 sub-rule (§7.B3 ③-b + §7.B5 borderline):
#   (i) amendment_log span (multi-line block, line-local boolean toggle — multi-line regex 아님):
#       enter/exit 규칙 = update_amendment_span() (헤더 anchor + sibling list / dedent exit).
#   이벤트동사 (change-record 신호) — line-local 토큰-인접(sub-rule ii) 시 history 면제.
_RE_AXIS3B_EVENT_VERB = re.compile(r"신설|추가|확장|전이|supersede")
#   (ii) line-local 토큰-인접 (§7.B5 — `9번째 lane 추가`/`9번째 lane (additive enum 확장`):
#        STALE 토큰 직후 window 안 이벤트동사 = "추가했다/신설했다" 변경기록 (현재-상태 count 단언 아님).
#        ★ over-broad 금지 (channel-split): window 를 짧게(=20) 잡아 live `description:`/`section:` 의
#        먼 위치 이벤트동사(다른 절)가 STALE 단언을 silent 면제하지 않도록. genuine STALE 검증:
#        label-registry desc / base-labels / section-ownership = 토큰 직후 `,`·`FIX`·`·` (verb 부재) → 검출 유지.
_AXIS3B_EVENT_VERB_WINDOW = 20

# 축③-c source_section / 인용: `source_section:` key 또는 따옴표 감싼 과거 section title 인용.
#   live `section:` key 값은 제외(channel 갈림) — 본 정규식은 source_section / 주석 내 인용만.
_RE_AXIS3C_SOURCE_SECTION = re.compile(r"^\s{0,8}source_section:")
#   주석(`#`) 라인 안 따옴표 인용 (section-ownership L459 형). live `section:` value 와 분리.
_RE_AXIS3C_COMMENT_QUOTE = re.compile(r"^\s{0,8}#.*\"[^\"]*(?:[6-9]\s{0,3}레인|레인\s{0,3}[5-9]개|[6-9]번째\s{0,3}lane)[^\"]*\"")

# 축③-d 버전이력 표: 숫자 전이(`6→8`/`9→10`) 또는 `(N 에이전트 · M 레인)` 과거 baseline 패턴.
#   ★ over-broad 금지 (§5.3/§7.B3 ③-d): 면제는 STALE 토큰 자체가 *숫자 전이*(N→M)의 일부일 때만.
#   prose 의 무관한 `→`(예: phase:요구사항 → phase:설계, 6.31.0 → 6.32.0) 가 live `description:`
#   라인 전체를 silent 면제하면 = same-file channel-split false-negative (AC-8). 따라서 전이 면제는
#   STALE lane-count 토큰에 화살표가 *인접*(N→M, M→N)할 때로 한정. 단독 `9 레인` + 무관 `→` = 검출.
#   숫자-화살표-숫자 인접: `[0-9]\s*→\s*[0-9]` (lane 전이 `6→8`·`9→10` 표기).
_RE_AXIS3D_NUMERIC_TRANSITION = re.compile(r"[0-9]\s{0,3}→\s{0,3}[0-9]")
_RE_AXIS3D_VERSION_HISTORY = re.compile(r"\d+\s{0,3}에이전트\s{0,3}·\s{0,3}\d+\s{0,3}레인")

# 축⑤ counterfactual: 같은 라인 가정 조건절 마커 `만약` + lane-count 토큰 + 가상 귀결동사
#   (신설|충돌|된다|무너) 가 lane 토큰 뒤. 진짜 counterfactual 구조만 면제 (`만약` 부재 단독 STALE = RED).
_RE_AXIS5_COUNTERFACTUAL = re.compile(
    r"만약.*([6-9])번째\s{0,3}lane.*(?:신설|충돌|된다|무너)"
)


# 전이 화살표가 STALE 토큰에 인접(±window)했는지 — §5.3 `9→10` vs 단독 `9 레인` 구분.
_TRANSITION_ADJ_WINDOW = 6


def _is_transition_adjacent(line, stale_match):
    """
    STALE 토큰 매치가 숫자 전이(N→M)의 일부인지 (화살표가 토큰 ±window 안 인접) 판정.

    §5.3/§7.B3 ③-d: `9→10`(정당 전이) 면제 vs `9 레인`(단독 stale, 무관 prose `→`) 검출.
    line 전체에 무관한 `→`(phase 전이 / 버전 전이 prose)가 있어도, STALE 토큰에 인접하지
    않으면 면제 안 함 — same-file channel-split false-negative(AC-8) 방지.
    """
    s, e = stale_match.start(), stale_match.end()
    lo = max(0, s - _TRANSITION_ADJ_WINDOW)
    hi = min(len(line), e + _TRANSITION_ADJ_WINDOW)
    window = line[lo:hi]
    return _RE_AXIS3D_NUMERIC_TRANSITION.search(window) is not None


def _is_event_verb_adjacent(line, stale_match):
    """
    STALE 토큰 직후 window 안에 change-record 이벤트동사(신설/추가/확장/전이/supersede)가
    인접하는지 (§7.B3 ③-b sub-rule ii / §7.B5) 판정.

    `9번째 lane 추가` / `9번째 lane (additive enum 확장` = 변경기록 (history) → 면제.
    over-broad 금지: window 짧게(=20) — live `description:` 의 먼 절 이벤트동사가 STALE 단언을
    silent 면제하지 않도록 (channel-split AC-8). 토큰 직후만 본다(앞 window 무관).
    """
    e = stale_match.end()
    window = line[e:e + _AXIS3B_EVENT_VERB_WINDOW]
    return _RE_AXIS3B_EVENT_VERB.search(window) is not None


def allowlist_match(line, in_amendment_span, stale_match=None):
    """
    line 이 5축 allowlist 중 1+ 에 해당하면 면제 사유 문자열 반환, 아니면 None.

    면제 단위 = syntactic channel(line-prefix key) 또는 counterfactual 마커.
    in_amendment_span = ③-b boolean toggle 현재 상태 (scan loop 가 enter/exit 관리).
    stale_match = detect 매치 객체 (axis③-d 전이 인접 판정용 — None 이면 line-wide fallback).
    """
    # 축② negation (정탐 면제)
    if _RE_AXIS2_NEGATION.search(line):
        return "axis2-negation (부정 토큰 인접 — 개수 단언 아님)"

    # 축⑤ counterfactual (가정 조건절 — 현재-상태 count 단언 아님)
    if _RE_AXIS5_COUNTERFACTUAL.search(line):
        return "axis5-counterfactual (가정 조건절 '만약 ... 신설하면 ... 충돌')"

    # 축③-a date행
    if _RE_AXIS3A_DATE.search(line):
        return "axis3a-date (frontmatter date / ISO 날짜 선두 — history)"

    # 축③-b (i) amendment_log span 내부 (multi-line block — span 경계가 history channel 확립)
    #   span 멤버십 자체가 면제 기준 (enter~exit toggle 가 block 경계 산정). span 밖 sibling
    #   live `description:`/`section:` 는 toggle=False = 검출 (F-CHANNEL-1 / Mutation-3 kill 의 핵심:
    #   span exit over-broaden → sibling `description:` 가 span 안으로 삼켜져 silent 면제 → RED flip).
    if in_amendment_span:
        return "axis3b-amendment-span (amendment_log block 내부 — history channel)"
    # 축③-b (ii) line-local 토큰-인접 이벤트동사 (§7.B5 — `9번째 lane 추가/확장`, change-record)
    if stale_match is not None and _is_event_verb_adjacent(line, stale_match):
        return "axis3b-event-verb-adjacent (STALE 토큰 직후 이벤트동사 — change-record history)"

    # 축③-c source_section / 주석 내 인용
    if _RE_AXIS3C_SOURCE_SECTION.search(line):
        return "axis3c-source-section (역사 인용 key)"
    if _RE_AXIS3C_COMMENT_QUOTE.search(line):
        return "axis3c-comment-quote (주석 내 따옴표 인용 — history)"

    # 축③-d 버전이력 표 (★전이 화살표는 STALE 토큰에 인접할 때만 — over-broad 금지 §5.3/AC-8)
    if stale_match is not None and _is_transition_adjacent(line, stale_match):
        return "axis3d-transition (숫자 전이 N→M 인접 — history)"
    if _RE_AXIS3D_VERSION_HISTORY.search(line):
        return "axis3d-version-history (N 에이전트 · M 레인 과거 baseline)"

    # 축① within-line 이중토큰: plugin-count `N lane plugin` 인접 시,
    #   그 토큰만 면제. 라인의 STALE 토큰이 dual-token 자체이면 면제 (잔여 stale 은 별 라인이라 검출).
    if _RE_AXIS1_DUAL_TOKEN.search(line):
        # 라인의 STALE 토큰 위치가 dual-token 외부에 또 있는가? — §7.B3 over-broad 금지.
        # detect 토큰을 dual-token 매치 구간으로 masking 후 잔여 stale 재검사.
        masked = _RE_AXIS1_DUAL_TOKEN.sub(lambda mo: " " * len(mo.group(0)), line)
        if stale_token_match(masked) is None:
            return "axis1-dual-token (N lane plugin — plugin-count 별 축, ADR-023)"
        # 잔여 stale 존재 → 면제 아님 (dual-token 만으론 라인 전체 면제 금지)

    return None


# ─────────────────────── span toggle 갱신 (③-b enter/exit) ───────────────────────

def _enter_span_indent(line):
    """amendment_log/changelog 헤더 key 라인의 들여쓰기(선행 공백 수) 반환."""
    return len(line) - len(line.lstrip(" "))


# 헤더형 span enter (amendment_log:/changelog: 헤더 key) — 들여쓰기 기준점 anchor.
_RE_AXIS3B_SPAN_HEADER = re.compile(r"^(\s{0,8})(?:amendment_log|changelog):\s*$")
# 헤더 없는 amendment entry 선두 (`- amendment:`) — 헤더 없이 시작하는 amendment 목록.
_RE_AXIS3B_AMENDMENT_ENTRY = re.compile(r"^(\s{0,8})-\s{0,3}amendment:")
# 임의 list item 선두 + 그 key 추출 (`- name:` / `- amendment:` / `- { ... }`).
_RE_LIST_ITEM_KEY = re.compile(r"^\s*-\s*([A-Za-z_][\w-]*)?\s*[:{]")


def update_amendment_span(line, in_span, span_enter_indent):
    """
    line 을 보고 in_amendment_span boolean toggle 을 갱신.

    enter: amendment_log/changelog 헤더 key 라인(`^\\s*amendment_log:$`) 또는 헤더 없는
           `- amendment:` 선두 → True. span_enter_indent = 헤더(또는 entry) 들여쓰기 anchor.
    exit:  (i) 다음 top-level key (들여쓰기 ≤ enter indent 의 비-dash scalar/mapping key)
           OR (ii) sibling list item 인데 key 가 `amendment` 아님 (예: `- name:` 라벨 entry)
                   → amendment_log block 이탈.

    Returns: (new_in_span, new_span_enter_indent)
    multi-line backtracking regex 아님 — 단일 boolean + int (O(lines), ReDoS-safe).
    """
    if not in_span:
        if _RE_AXIS3B_SPAN_HEADER.search(line) or _RE_AXIS3B_AMENDMENT_ENTRY.search(line):
            return True, _enter_span_indent(line)
        return False, span_enter_indent

    # in_span == True — exit 조건 검사 (빈 줄은 span 유지)
    if line.strip() == "":
        return True, span_enter_indent

    cur_indent = len(line) - len(line.lstrip(" "))

    # list item (`- ...`) — key 가 amendment 면 span 유지, 아니면(예: `- name:`) exit.
    li = _RE_LIST_ITEM_KEY.match(line)
    if li is not None:
        key = li.group(1)
        if key == "amendment" or (key is None):
            # `- amendment:` 또는 `- { ... }`(inline mapping, MANIFEST 형) = amendment entry → 유지
            return True, span_enter_indent
        # `- name:` 등 다른 sibling list = amendment_log block 이탈 → exit
        return False, span_enter_indent

    # (ii) 다음 top-level/낮은 indent scalar·mapping key (dash 아님) — enter indent 이하 dedent → exit.
    if cur_indent <= span_enter_indent and re.match(r"^\s*[A-Za-z_]", line):
        return False, span_enter_indent

    # 그 외 (enter indent 보다 깊은 들여쓴 amendment 내용) = span 유지
    return True, span_enter_indent


# ─────────────────────── 단일 파일 scan ──────────────────────────────────────────

def scan_file(abs_path, rel_path):
    """
    파일 1개를 line-by-line scan. (flag(line) := stale AND NOT allowlist)

    Returns: list of (rel_path, line_num, stale_token, context_excerpt)
    Raises: OSError (read 실패 → 호출부가 SETUP exit 2 처리)
    """
    findings = []
    in_span = False
    span_enter_indent = 0

    with open(abs_path, encoding="utf-8", errors="replace") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")

            # span toggle 먼저 갱신 (현재 라인이 span 내부인지 판정에 사용)
            in_span, span_enter_indent = update_amendment_span(
                line, in_span, span_enter_indent
            )

            m = stale_token_match(line)
            if m is None:
                continue

            reason = allowlist_match(line, in_span, stale_match=m)
            if reason is not None:
                continue  # 면제

            stale_tok = m.group(0).strip()
            ctx = line.strip()
            if len(ctx) > 100:
                ctx = ctx[:97] + "..."
            findings.append((rel_path, line_num, stale_tok, ctx))

    return findings


# ─────────────────────── 경로 수집 (git ls-files) ───────────────────────────────

def collect_files(repo_root, globs):
    """
    git ls-files <globs...> 결과에서 제외 경로/self 제외 후 검사 대상 파일 목록 반환.
    git 미가용 시 os.walk fallback.
    """
    rel_paths = _git_ls_files(repo_root, globs)
    if rel_paths is None:
        rel_paths = _walk_files(repo_root, globs)

    out = []
    for rp in rel_paths:
        rp_norm = rp.replace("\\", "/")
        if any(rp_norm.startswith(pfx) for pfx in EXCLUDE_PATH_PREFIXES):
            continue
        if rp_norm in SELF_EXCLUDE_PATHS:
            continue
        # 텍스트 후보 확장자만 (바이너리 회피) — .md/.yaml/.yml/.tsv/.json/.sh/.py/.txt 및 CLAUDE.md
        if not _is_text_candidate(rp_norm):
            continue
        out.append(rp_norm)
    return sorted(set(out))


def _is_text_candidate(rel_path):
    text_suffixes = (
        ".md", ".yaml", ".yml", ".tsv", ".json", ".sh", ".py", ".txt", ".mjs"
    )
    base = os.path.basename(rel_path)
    if base == "CLAUDE.md":
        return True
    return rel_path.endswith(text_suffixes)


def _git_ls_files(repo_root, globs):
    """git ls-files <globs> 결과 목록 반환. git 실패 시 None."""
    try:
        result = subprocess.run(
            ["git", "ls-files"] + list(globs),
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return [l.strip() for l in result.stdout.splitlines() if l.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _walk_files(repo_root, globs):
    """git 미가용 fallback — globs 를 디렉터리/파일 prefix 로 해석해 os.walk."""
    collected = []
    for g in globs:
        target = os.path.join(repo_root, g)
        if os.path.isfile(target):
            collected.append(g.replace("\\", "/"))
            continue
        if os.path.isdir(target):
            for dirpath, _dirnames, filenames in os.walk(target):
                for fn in filenames:
                    abs_p = os.path.join(dirpath, fn)
                    rel_p = os.path.relpath(abs_p, repo_root).replace("\\", "/")
                    collected.append(rel_p)
    return collected


# ─────────────────────── 출력 (deferred-followup `::warning::` 답습) ──────────────

def _emit_flag(item):
    rel_path, line_num, stale_tok, ctx = item
    print(
        "::warning::check-lane-count-ssot: FLAG — "
        "%s:%d / stale-token=\"%s\" / context=\"%s\""
        % (rel_path, line_num, stale_tok, ctx)
    )


_ACTION_GUIDE = (
    "[lane-count-ssot] canonical 작업레인 수 = 10 (ADR-125 Amendment 1). "
    "현재-상태 lane-count 단언이 10 과 어긋남 (warning mode — merge 비차단, advisory):\n"
    "  ① 현재-상태 단언이면 `10 레인`/`10번째 lane` 으로 정정\n"
    "  ② history(전이/changelog/amendment_log/date/source_section) 면 해당 channel 로 표기\n"
    "     (전이는 `9→10` 화살표 / amendment_log 는 block 내부 이벤트동사 동반)\n"
    "  ③ plugin-count 면 `N lane plugin` 이중토큰 형태 유지 (별 축, ADR-023)\n"
    "  ④ hotfix-bypass:lane-count-ssot-consistency label + audit comment\n"
    "근거: ADR-060 Amendment 19 §결정 33 (CFP-2426) — canonical lane 수(10) SSOT "
    "mechanical consistency enforcement."
)


# ─────────────────────── 서브커맨드: check ───────────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    globs = args.paths if args.paths else DEFAULT_SCAN_GLOBS

    files = collect_files(repo_root, globs)
    if not files:
        print(
            "[codeforge-lane-count-ssot-infra-error] check-lane-count-ssot: "
            "검사 경로 0개 (in-scope glob 매칭 파일 부재) — repo-root/glob 확인",
            file=sys.stderr,
        )
        return 2

    all_findings = []
    for rel_path in files:
        abs_path = os.path.join(repo_root, rel_path)
        try:
            all_findings.extend(scan_file(abs_path, rel_path))
        except OSError as exc:
            print(
                "[codeforge-lane-count-ssot-infra-error] check-lane-count-ssot: "
                "파일 read 실패: %s (%s)" % (rel_path, exc),
                file=sys.stderr,
            )
            return 2

    for item in all_findings:
        _emit_flag(item)

    if all_findings:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-lane-count-ssot: FLAG %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)"
            % len(all_findings)
        )
        return 1

    print(
        "check-lane-count-ssot: PASS — FLAG 0 across %d file(s) (warning tier)"
        % len(files)
    )
    return 0


# ─────────────────────── main ────────────────────────────────────────────────────

def main(argv):
    parser = argparse.ArgumentParser(
        description="lane-count SSOT consistency 게이트 (CFP-2426 / ADR-060 Amd19 §결정 33)"
    )
    subparsers = parser.add_subparsers(dest="command")

    check_p = subparsers.add_parser("check", help="in-scope 경로 전수 scan")
    check_p.add_argument(
        "--repo-root", default=".",
        help="git repo root 경로 (default: 현재 디렉터리)",
    )
    check_p.add_argument(
        "--paths", nargs="*", default=None,
        help="검사 대상 glob 재정의 (default: docs/·CLAUDE.md·plugins/·scripts/·templates/·plugin.json)",
    )

    args = parser.parse_args(argv[1:])

    # 인자 없으면 check default (thin wrapper 가 보장하나 이중 안전)
    if args.command is None:
        args.command = "check"
        args.repo_root = "."
        args.paths = None

    if args.command == "check":
        return cmd_check(args)

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
