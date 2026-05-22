#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1239 / ADR-058 Amendment 1 §결정 5 — sunset-weakening-evidence mechanical lint
# CFP-1249 — forbid-list 축소 감지 (2nd weakening pattern) 확장
# CFP-1255 — cross-file ADR-064 evidence 검증 (forbid-list 제거 + ADR-064 lockstep)
# ADR-061 §결정 1 — Python SSOT (heredoc 금지), ADR-060 §결정 5 warning-tier
#
# 검사 목적:
#   ADR-058 Amendment 1 (CFP-1149) 가 §결정 5 를 "block weakening" 에서
#   "evidence-gate" 로 재정의. 약화 방향 Amendment 는 허용하되
#   evidence (metric / 평가 / 환경 / pattern_count 등) 를 반드시 제시해야 함.
#
#   ADR-064 §self-application 은 forbid-list dictionary 축소를 "약화 방향" 으로 명시.
#
#   본 lint 는 git diff 기반 2가지 약화 패턴을 감지:
#     (A) ADR 파일: is_transitional false → true (약화) → evidence 검사
#     (B) docs/wording-dictionary.md: 카테고리 (a) forbid-list row 제거 → cross-file ADR-064 검증
#
# 검사 규칙:
#   (A) ADR is_transitional 약화:
#     (1) 약화 감지 (PRIMARY):
#         OLD is_transitional: false → NEW is_transitional: true
#         → amendment_log 의 신규/최신 entry 에 sunset_justification 이
#           evidence-bearing 이어야 함.
#         evidence-bearing 판정 기준: non-null AND not bare "N/A" AND
#           아래 키워드 중 1개 이상 포함 (case-insensitive):
#             metric / 평가 / 환경 / obsolescence / pattern_count /
#             incident / measure / 측정
#     (2) 강화 면제:
#         is_transitional true → false (ratchet 강화) = 면제 (WARN 없음)
#         "N/A — ratchet 강화" sunset_justification 정상.
#     (3) 변경 없음 = 면제 (WARN 없음)
#     (4) NEW ADR (base 에 없음) = 면제 (약화 비교 기준 없음)
#   (B) forbid-list 축소 (docs/wording-dictionary.md):
#     (5) 카테고리 (a) 표 데이터 row 가 OLD 에 존재 → NEW 에 부재 = 제거 (약화)
#         → cross-file ADR-064 evidence 검증 (CFP-1255):
#           (5a) ADR-064 가 변경 파일 목록 안에 있고 신규 entry 에 evidence-bearing
#                sunset_justification 보유 → PASS (약화가 lockstep evidence 로 정당화됨)
#           (5b) ADR-064 미변경 → WARN ("forbid-list 축소 — ADR-064 lockstep amendment 부재")
#           (5c) ADR-064 변경됐으나 신규 entry 에 evidence-bearing sunset_justification 없음
#                → WARN ("ADR-064 변경됐으나 evidence-bearing sunset_justification 부재")
#         주의: ADR-064↔어휘 1:1 semantic 매칭은 heuristic.
#               신규 evidence-bearing amendment 존재 = PASS (exact carrier matching 범위 외).
#     (6) row 추가 (강화) = 면제 (WARN 없음)
#     (7) 신규 파일 (base 에 없음) = 면제
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (yaml.safe_load 파싱 하드 오류)
#   2 — setup error (git 미설치 등)
#
# Usage:
#   python3 check_sunset_weakening_evidence.py [options] [file ...]
#   Options:
#     --repo DIR    git 레포 루트 (default: 현재 작업 디렉토리)
#     --base REF    비교 기준 git ref (default: origin/main; CI: GITHUB_BASE_REF)
#     --adr-dir DIR ADR 디렉토리 경로 (파일 목록 미지정 시 사용)

import sys
import re
import os
import subprocess
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
    print("[check-sunset-weakening] pyyaml 미설치 — skip (exit 0)", file=sys.stderr)
    sys.exit(0)

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_SUNSET_WEAKENING_EVIDENCE", "")
if BYPASS_ENV == "1":
    print("[check-sunset-weakening] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-sunset-weakening]"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# evidence-bearing 키워드 (대소문자 무시)
EVIDENCE_KEYWORDS = [
    "metric",
    "평가",
    "환경",
    "obsolescence",
    "pattern_count",
    "incident",
    "measure",
    "측정",
]

# forbid-list 파일 경로 (repo-relative, 정규화 비교용)
WORDING_DICT_REL = "docs/wording-dictionary.md"

# ADR-064 파일 경로 패턴 — forbid-list cross-file evidence 검증 대상
ADR064_NAME_RE = re.compile(r"^ADR-064-.*\.md$", re.IGNORECASE)

# 카테고리 (a) 섹션 헤더 패턴 — docs/wording-dictionary.md 의 정식 헤더 verbatim 기준
# 변경 시 wording-dictionary.md 헤더와 lockstep 갱신 의무
FORBID_CAT_A_HEADER_RE = re.compile(
    r"^##\s+카테고리\s+\(a\)\s+[—\-–].*forbid",
    re.IGNORECASE,
)
# 다음 ## 헤더 (카테고리 (b) 또는 이후 섹션) — 섹션 종료 기준
NEXT_H2_RE = re.compile(r"^##\s+")
# 표 헤더 행: "| 어휘 | lint scope |" 패턴
FORBID_TABLE_HEADER_RE = re.compile(r"^\|\s*어휘\s*\|", re.IGNORECASE)
# 표 구분선 행: "|---|---| ..." 패턴
FORBID_TABLE_SEP_RE = re.compile(r"^\|\s*[-:]+\s*\|")

# ── 인수 파싱 ─────────────────────────────────────────────────────────────────
def parse_args(argv):
    """인수에서 --repo / --base / --adr-dir 와 파일 목록 분리."""
    repo_dir = None
    base_ref = None
    adr_dir = None
    files = []
    i = 0
    while i < len(argv):
        if argv[i] == "--repo" and i + 1 < len(argv):
            repo_dir = argv[i + 1]
            i += 2
        elif argv[i] == "--base" and i + 1 < len(argv):
            base_ref = argv[i + 1]
            i += 2
        elif argv[i] == "--adr-dir" and i + 1 < len(argv):
            adr_dir = argv[i + 1]
            i += 2
        else:
            files.append(argv[i])
            i += 1
    return repo_dir, base_ref, adr_dir, files

# ── frontmatter 파싱 ──────────────────────────────────────────────────────────
def parse_frontmatter(text, filepath):
    """
    frontmatter YAML 파싱.
    반환: (fm_dict or None, body_text)
    파싱 실패 시 [WARN] 출력 + None 반환 (crash 금지 — fail-soft).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text

    fm_raw = m.group(1)
    body = text[m.end():]
    try:
        fm = yaml.safe_load(fm_raw)
        if not isinstance(fm, dict):
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: frontmatter 가 dict 아님 — skip",
                file=sys.stderr,
            )
            return None, body
        return fm, body
    except yaml.YAMLError as e:
        print(
            f"{SCRIPT_NAME} [WARN] {filepath}: frontmatter YAML 파싱 실패 ({e}) — skip",
            file=sys.stderr,
        )
        return None, body

# ── git show 로 OLD frontmatter 조회 ─────────────────────────────────────────
def get_old_text(repo_dir, base_ref, filepath):
    """
    git show <base_ref>:<filepath> 로 OLD 파일 내용 조회.
    파일이 base 에 없으면 None 반환 (신규 파일 = 약화 비교 불가).
    """
    # filepath 를 repo_dir 기준 상대 경로로 변환
    try:
        rel = Path(filepath).resolve().relative_to(Path(repo_dir).resolve())
        rel_str = str(rel).replace("\\", "/")
    except ValueError:
        # resolve 실패 또는 repo 외부 경로 — 원본 경로 사용
        rel_str = str(filepath).replace("\\", "/")

    cmd = ["git", "-C", str(repo_dir), "show", f"{base_ref}:{rel_str}"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            # 파일이 base 에 없음 (신규 파일)
            return None
        return result.stdout
    except FileNotFoundError:
        print(f"{SCRIPT_NAME} ERROR: git 명령 없음 (setup error)", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(
            f"{SCRIPT_NAME} [WARN] {filepath}: git show 실패 ({e}) — skip",
            file=sys.stderr,
        )
        return None

# ── is_transitional 값 추출 ───────────────────────────────────────────────────
def get_is_transitional(fm):
    """
    frontmatter dict 에서 is_transitional 값 반환.
    미선언 시 None 반환.
    """
    val = fm.get("is_transitional")
    if val is None:
        return None
    return bool(val)

# ── evidence-bearing 판정 ─────────────────────────────────────────────────────
def is_evidence_bearing(value):
    """
    sunset_justification 값이 evidence-bearing 인지 판정.
    기준:
      - non-null
      - not bare "N/A" (대소문자 무시, 공백 strip 후)
      - EVIDENCE_KEYWORDS 중 1개 이상 포함
    """
    if not value:
        return False
    stripped = str(value).strip()
    if not stripped:
        return False
    # bare "N/A" 패턴 (대소문자, 하이픈/슬래시 허용 — "N/A", "n/a", "N/A — ratchet 강화" 등)
    # 단 "N/A — ratchet 강화" 는 강화 방향에서만 쓰임 → 약화 감지 후 호출되므로 evidence 부족
    # → 이 함수는 약화 감지 후에만 호출, "N/A" 계열 = evidence 미보유
    na_pattern = re.compile(r"^n/a", re.IGNORECASE)
    if na_pattern.match(stripped):
        return False
    # 키워드 검사
    text_lower = stripped.lower()
    for kw in EVIDENCE_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False

# ── amendment_log 에서 sunset_justification 조회 ──────────────────────────────
def find_latest_sunset_justification(fm):
    """
    amendment_log 목록의 마지막 entry 에서 sunset_justification 반환.
    amendment_log 미존재 또는 빈 목록 → None.
    """
    al = fm.get("amendment_log")
    if not isinstance(al, list) or len(al) == 0:
        return None
    last_entry = al[-1]
    if not isinstance(last_entry, dict):
        return None
    return last_entry.get("sunset_justification")

# ── 단일 ADR 파일 검사 ────────────────────────────────────────────────────────
def check_adr_file(filepath, repo_dir, base_ref):
    """
    단일 ADR 파일에 대해 약화 감지 + evidence 검사.
    반환: warn_count (int)
    """
    path = Path(filepath)
    if not path.exists():
        print(f"{SCRIPT_NAME} [WARN] {filepath}: 파일 없음 — skip", file=sys.stderr)
        return 0

    # NEW (현재) frontmatter 파싱
    new_text = path.read_text(encoding="utf-8", errors="replace")
    new_fm, _ = parse_frontmatter(new_text, filepath)
    if new_fm is None:
        # 파싱 실패 — 이미 WARN 출력 완료, crash 방지
        return 0

    new_transitional = get_is_transitional(new_fm)

    # OLD (base) frontmatter 조회
    old_text = get_old_text(repo_dir, base_ref, filepath)
    if old_text is None:
        # 신규 파일 — OLD 없음 → 약화 비교 불가 → PASS
        print(
            f"{SCRIPT_NAME} OK (신규 파일): {filepath}",
            file=sys.stderr,
        )
        return 0

    old_fm, _ = parse_frontmatter(old_text, filepath)
    if old_fm is None:
        # OLD 파싱 실패 — skip
        return 0

    old_transitional = get_is_transitional(old_fm)

    # 약화 감지: false → true
    if old_transitional is False and new_transitional is True:
        # 약화 방향 → evidence 확인
        sj = find_latest_sunset_justification(new_fm)
        if is_evidence_bearing(sj):
            print(
                f"{SCRIPT_NAME} OK (약화 + evidence 확인됨): {filepath}",
                file=sys.stderr,
            )
            return 0
        else:
            # evidence 미보유 → WARN
            sj_display = repr(sj) if sj is not None else "null"
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: is_transitional false→true (약화) 감지, "
                f"but amendment_log 최신 entry 의 sunset_justification 이 evidence-bearing 아님 "
                f"(값: {sj_display}). "
                f"ADR-058 Amendment 1 §결정 5 evidence-gate: metric / 평가 / 환경 / "
                f"pattern_count / incident / measure / 측정 중 1개 이상 포함 의무.",
                file=sys.stderr,
            )
            return 1

    # 강화 감지: true → false (면제)
    if old_transitional is True and new_transitional is False:
        print(
            f"{SCRIPT_NAME} OK (강화 방향 — evidence-gate 면제): {filepath}",
            file=sys.stderr,
        )
        return 0

    # 변경 없음 (면제)
    print(f"{SCRIPT_NAME} OK: {filepath}", file=sys.stderr)
    return 0

# ── 카테고리 (a) forbid-list row 파싱 ────────────────────────────────────────
def parse_forbid_list_rows(text):
    """
    docs/wording-dictionary.md 본문에서 카테고리 (a) 섹션의
    표 데이터 row 목록 반환 (헤더 행 + 구분선 행 제외).

    반환: set of str (각 row 를 strip 한 문자열)

    섹션 경계:
      - 시작: FORBID_CAT_A_HEADER_RE 매칭 줄 다음부터
      - 종료: 다음 ## 헤더 줄 (NEXT_H2_RE) 또는 EOF
    """
    rows = set()
    in_cat_a = False

    for line in text.splitlines():
        stripped = line.strip()

        # 카테고리 (a) 섹션 시작 감지
        if not in_cat_a:
            if FORBID_CAT_A_HEADER_RE.match(stripped):
                in_cat_a = True
            continue

        # 카테고리 (a) 섹션 안 — 다음 ## 헤더가 나오면 종료
        if NEXT_H2_RE.match(stripped):
            break

        # 표 행 필터링: | 로 시작하는 행
        if not stripped.startswith("|"):
            continue

        # 헤더 행 (| 어휘 | ...) 제외
        if FORBID_TABLE_HEADER_RE.match(stripped):
            continue

        # 구분선 행 (|---|---| ...) 제외
        if FORBID_TABLE_SEP_RE.match(stripped):
            continue

        # 데이터 row 수집
        rows.add(stripped)

    return rows


# ── ADR-064 파일 경로 판별 ────────────────────────────────────────────────────
def is_adr064_file(filepath):
    """
    filepath 가 ADR-064-*.md 인지 판별 (이름 기반).
    절대 경로 / 상대 경로 모두 지원.
    """
    name = Path(filepath).name
    return bool(ADR064_NAME_RE.match(name))


# ── amendment_log 의 신규 추가된 entry 목록 추출 ──────────────────────────────
def get_amendment_log_entries(fm):
    """
    frontmatter dict 에서 amendment_log 목록 반환.
    amendment_log 미존재 또는 비-list → 빈 list 반환.
    각 entry 는 dict 라고 가정.
    """
    al = fm.get("amendment_log")
    if not isinstance(al, list):
        return []
    return [e for e in al if isinstance(e, dict)]


def get_amendment_id(entry):
    """
    amendment_log entry 의 고유 식별자 반환.
    ADR-064 는 'version: "Amendment 1"' 또는 'amendment: 2' 2가지 형식 혼재.
    두 형식 모두 지원 — str 로 정규화하여 반환.
    식별자 없으면 None 반환.
    """
    # 'amendment' 필드 (int 또는 str)
    val = entry.get("amendment")
    if val is not None:
        return str(val).strip()
    # 'version' 필드 (str, 예: "Amendment 1")
    val = entry.get("version")
    if val is not None:
        return str(val).strip()
    # 'amendment_id' 필드 (int 또는 str — fixture 에서 사용)
    val = entry.get("amendment_id")
    if val is not None:
        return str(val).strip()
    return None


def find_new_amendment_entries(old_fm, new_fm):
    """
    OLD 에 없고 NEW 에 있는 amendment_log entry 목록 반환.

    식별자(amendment / version / amendment_id) 기반 비교.
    식별자 없는 entry 는 내용 기반 fallback 비교 (old list 에 없으면 신규로 처리).

    반환: list of dict (신규 entry 목록)
    """
    old_entries = get_amendment_log_entries(old_fm)
    new_entries = get_amendment_log_entries(new_fm)

    # OLD id set 수집
    old_ids = set()
    for e in old_entries:
        eid = get_amendment_id(e)
        if eid is not None:
            old_ids.add(eid)

    new_items = []
    for e in new_entries:
        eid = get_amendment_id(e)
        if eid is not None:
            if eid not in old_ids:
                # 식별자 기반 신규 entry
                new_items.append(e)
        else:
            # 식별자 없음 — 내용 기반 fallback: OLD 에 동일 dict 없으면 신규
            if e not in old_entries:
                new_items.append(e)

    return new_items


def check_adr064_crossfile_evidence(adr064_filepath, repo_dir, base_ref):
    """
    ADR-064 파일에서 신규 추가된 amendment_log entry 에
    evidence-bearing sunset_justification 이 있는지 검사.

    반환:
      "evidence_found"   — 신규 entry 중 1개 이상 evidence-bearing
      "no_new_entries"   — 신규 entry 없음 (OLD == NEW 또는 파싱 실패)
      "no_evidence"      — 신규 entry 존재하나 evidence-bearing 없음
      "parse_error"      — 파싱 실패 (fail-soft — WARN 후 계속)

    주의: ADR-064↔어휘 1:1 semantic 매칭은 heuristic.
    신규 evidence-bearing amendment 존재 = PASS (exact carrier matching 범위 외).
    """
    path = Path(adr064_filepath)
    if not path.exists():
        print(
            f"{SCRIPT_NAME} [WARN] ADR-064 파일 없음 ({adr064_filepath}) — "
            f"cross-file 검사 skip (fail-soft)",
            file=sys.stderr,
        )
        return "parse_error"

    new_text = path.read_text(encoding="utf-8", errors="replace")
    new_fm, _ = parse_frontmatter(new_text, adr064_filepath)
    if new_fm is None:
        print(
            f"{SCRIPT_NAME} [WARN] ADR-064 frontmatter 파싱 실패 — "
            f"cross-file 검사 skip (fail-soft)",
            file=sys.stderr,
        )
        return "parse_error"

    old_text = get_old_text(repo_dir, base_ref, adr064_filepath)
    if old_text is None:
        # ADR-064 가 신규 파일인 경우 — OLD 없음 → 신규 entry 가 모두 신규
        old_fm = {"amendment_log": []}
    else:
        old_fm, _ = parse_frontmatter(old_text, adr064_filepath)
        if old_fm is None:
            print(
                f"{SCRIPT_NAME} [WARN] ADR-064 OLD frontmatter 파싱 실패 — "
                f"cross-file 검사 skip (fail-soft)",
                file=sys.stderr,
            )
            return "parse_error"

    new_entries = find_new_amendment_entries(old_fm, new_fm)

    if not new_entries:
        return "no_new_entries"

    # 신규 entry 중 evidence-bearing 이 하나라도 있으면 PASS
    for entry in new_entries:
        sj = entry.get("sunset_justification")
        if is_evidence_bearing(sj):
            return "evidence_found"

    return "no_evidence"


# ── 단일 wording-dictionary.md 파일 검사 ─────────────────────────────────────
def check_wording_dict_file(filepath, repo_dir, base_ref, adr064_files=None):
    """
    docs/wording-dictionary.md 에 대해 카테고리 (a) forbid-list row 제거 (약화) 감지.
    row 제거 감지 시 cross-file ADR-064 evidence 검증 수행 (CFP-1255).

    반환: warn_count (int)

    cross-file evidence 검증 3-verdict (CFP-1255 D1):
      (5a) ADR-064 변경 + 신규 entry evidence-bearing → PASS (WARN 없음)
      (5b) ADR-064 미변경 (adr064_files 에 없음) → WARN
      (5c) ADR-064 변경됐으나 신규 entry evidence-bearing 없음 → WARN

    주의: ADR-064↔어휘 1:1 semantic 매칭은 heuristic.
    신규 evidence-bearing amendment 존재 = PASS (exact carrier matching 범위 외).
    """
    if adr064_files is None:
        adr064_files = []

    path = Path(filepath)
    if not path.exists():
        print(
            f"{SCRIPT_NAME} [WARN] {filepath}: 파일 없음 — skip",
            file=sys.stderr,
        )
        return 0

    # NEW (현재) 본문 파싱
    new_text = path.read_text(encoding="utf-8", errors="replace")
    new_rows = parse_forbid_list_rows(new_text)

    # OLD (base) 본문 조회
    old_text = get_old_text(repo_dir, base_ref, filepath)
    if old_text is None:
        # 신규 파일 — OLD 없음 → 비교 불가 → PASS
        print(
            f"{SCRIPT_NAME} OK (신규 파일): {filepath}",
            file=sys.stderr,
        )
        return 0

    old_rows = parse_forbid_list_rows(old_text)

    # 제거된 row = OLD 에 있고 NEW 에 없는 것
    removed_rows = old_rows - new_rows

    if not removed_rows:
        print(
            f"{SCRIPT_NAME} OK (forbid-list 축소 없음): {filepath}",
            file=sys.stderr,
        )
        return 0

    # ── forbid-list row 제거 감지 → cross-file ADR-064 evidence 검증 ────────
    # CFP-1255: adr064_files 목록에서 ADR-064-*.md 파일 탐색
    adr064_path = None
    for f in adr064_files:
        if is_adr064_file(f):
            adr064_path = f
            break

    warn_count = 0

    if adr064_path is not None:
        # ADR-064 가 변경 파일 목록 안에 있음 → cross-file evidence 검증 수행
        crossfile_result = check_adr064_crossfile_evidence(
            adr064_path, repo_dir, base_ref
        )
        if crossfile_result == "evidence_found":
            # 신규 evidence-bearing amendment 존재 → PASS (weakening justified)
            print(
                f"{SCRIPT_NAME} OK (forbid-list 축소 + ADR-064 lockstep evidence 확인됨): "
                f"{filepath}",
                file=sys.stderr,
            )
            return 0
        elif crossfile_result == "no_evidence":
            # ADR-064 변경됐으나 evidence-bearing 신규 entry 없음 → WARN (5c)
            for row in sorted(removed_rows):
                print(
                    f"{SCRIPT_NAME} [WARN] {filepath}: "
                    f"카테고리 (a) forbid-list row 제거 (weakening) 감지 — "
                    f"ADR-064 변경됐으나 evidence-bearing sunset_justification 부재. "
                    f"ADR-058 §결정 5 evidence-gate 미충족. "
                    f"제거된 row: {row}",
                    file=sys.stderr,
                )
                warn_count += 1
            return warn_count
        else:
            # parse_error 또는 no_new_entries — fall through to (5b) WARN
            for row in sorted(removed_rows):
                print(
                    f"{SCRIPT_NAME} [WARN] {filepath}: "
                    f"카테고리 (a) forbid-list row 제거 (weakening) 감지 — "
                    f"ADR-064 변경됐으나 신규 amendment_log entry 없음 또는 파싱 실패. "
                    f"ADR-058 §결정 5 evidence-gate: "
                    f"ADR-064 lockstep amendment sunset_justification evidence 동반 필요. "
                    f"제거된 row: {row}",
                    file=sys.stderr,
                )
                warn_count += 1
            return warn_count
    else:
        # ADR-064 미변경 (5b) → WARN
        for row in sorted(removed_rows):
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: "
                f"카테고리 (a) forbid-list row 제거 (weakening) 감지 — "
                f"ADR-064 lockstep amendment evidence 부재. "
                f"ADR-058 §결정 5 evidence-gate: "
                f"ADR-064 amendment sunset_justification evidence 동반 필요. "
                f"제거된 row: {row}",
                file=sys.stderr,
            )
            warn_count += 1

    return warn_count


# ── repo-relative 경로 정규화 (wording-dictionary.md 판별) ────────────────────
def is_wording_dict_file(filepath, repo_dir):
    """
    filepath 가 docs/wording-dictionary.md (repo-relative) 인지 판별.
    절대 경로 / 상대 경로 모두 지원.
    """
    try:
        rel = Path(filepath).resolve().relative_to(Path(repo_dir).resolve())
        rel_str = str(rel).replace("\\", "/")
        return rel_str == WORDING_DICT_REL
    except ValueError:
        # resolve 실패 — 이름 기반 fallback
        name = Path(filepath).name
        return name == "wording-dictionary.md"


# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    repo_arg, base_arg, adr_dir_arg, files = parse_args(sys.argv[1:])

    # repo_dir 결정
    if repo_arg:
        repo_dir = Path(repo_arg)
    else:
        repo_dir = Path.cwd()

    # base_ref 결정 (CI: GITHUB_BASE_REF, 로컬: HEAD~1 fallback)
    if base_arg:
        base_ref = base_arg
    else:
        env_base = os.environ.get("GITHUB_BASE_REF", "")
        if env_base:
            base_ref = f"origin/{env_base}"
        else:
            base_ref = "HEAD~1"

    # ADR 디렉토리 결정 (파일 미지정 시 전체 scan)
    if adr_dir_arg:
        adr_dir = Path(adr_dir_arg)
    else:
        script_dir = Path(__file__).parent
        candidate = script_dir.parent.parent / "docs" / "adr"
        if candidate.is_dir():
            adr_dir = candidate
        else:
            adr_dir = repo_dir / "docs" / "adr"

    # 검사 대상 파일 수집
    # ADR 파일 목록 (is_transitional 약화 검사 대상)
    adr_files = []
    # wording-dictionary.md 경로 (forbid-list 축소 검사 대상)
    wording_dict_files = []
    # ADR-064-*.md 경로 목록 (forbid-list cross-file evidence 검증용)
    adr064_files = []

    if files:
        # 명시된 파일: ADR 패턴 vs wording-dictionary.md 분류
        for f in files:
            name = Path(f).name
            if re.match(r"ADR-\d+", name) and name.endswith(".md"):
                adr_files.append(f)
                # ADR-064 는 별도 cross-file 검증 목록에도 수집
                if is_adr064_file(f):
                    adr064_files.append(f)
            elif is_wording_dict_file(f, str(repo_dir)):
                wording_dict_files.append(f)
            # 그 외 파일 (ADR 아닌 일반 docs 등) = skip
    else:
        # 파일 미지정 → adr_dir 전체 scan + wording-dictionary.md 자동 포함
        if adr_dir.is_dir():
            for adr_file in sorted(adr_dir.glob("ADR-*.md")):
                adr_files.append(str(adr_file))
                if is_adr064_file(str(adr_file)):
                    adr064_files.append(str(adr_file))
        else:
            print(
                f"{SCRIPT_NAME} INFO: ADR dir 없음 ({adr_dir}) — skip",
                file=sys.stderr,
            )
        # wording-dictionary.md 자동 추가 (repo-relative 경로)
        wd_path = repo_dir / "docs" / "wording-dictionary.md"
        if wd_path.exists():
            wording_dict_files.append(str(wd_path))

    total_warns = 0

    # (A) ADR is_transitional 약화 검사
    for f in adr_files:
        total_warns += check_adr_file(f, str(repo_dir), base_ref)

    # (B) forbid-list 축소 검사 (CFP-1255: adr064_files 로 cross-file evidence 검증)
    for f in wording_dict_files:
        total_warns += check_wording_dict_file(f, str(repo_dir), base_ref, adr064_files)

    # warning-tier — 경고 수에 무관하게 exit 0 (PR merge 미차단)
    if total_warns > 0:
        print(
            f"{SCRIPT_NAME} WARN: {total_warns}건 경고 감지 "
            f"(warning-tier — PR merge 미차단)",
            file=sys.stderr,
        )
    else:
        print(f"{SCRIPT_NAME} PASS: 경고 0건", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
