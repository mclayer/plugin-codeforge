#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""scripts/lib/check_adr178_forbidden_form_presence.py
CFP-2966 Phase 2 / ADR-178 §결정 7 — negative-control presence lint (금지 form 재유입 검사).
tier: [measurement]  (warning-first — ADR-171 §결정 5 / ADR-178 §결정 12. blocking 으로 태어나지 않음)

ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-adr178-forbidden-form-presence.sh).

목적:
  ADR-178 §결정 7 은 "진행 커밋(progress-commit)은 정지 사유가 아니다" 를 negative control 로 두고,
  네 가지 금지 form (① 한도 임박 trigger / ② 커밋 후 정지 / ③ 신호 반응형 저장 / ④ 종료-시점 저장)이
  규범으로 재유입되는 것을 금지한다. 본 lint 은 그 금지 form 의 **부재**를 정적으로 검사한다.

검사 계약 (ADR-178 §결정 7 "Phase 2 lint 계약" 문단이 정본):
  1. 검사 정의역 = `<!-- progress-commit-normative-region:start -->` ~ `:end` 구간
                   **빼기** `<!-- forbidden-form-quotation:start -->` ~ `:end` 블록.
     인용 절(금지 form 을 "이런 조항은 없다" 라고 박제한 절)을 정의역에서 제외해야 self-RED 함정
     (인용 자체를 위반으로 오판)을 회피한다. 마커명 = ADR 본문에 고정된 위 두 리터럴.
  2. 금지 토큰 = ADR 인용 절 내부의 `FORBIDDEN_TOKENS` 배열(closed set 4 리터럴)을 **런타임 파싱**해
     사용한다. 배열이 SSOT 이며 본 lint 은 토큰 리터럴을 하드코딩하지 않는다 (drift 차단).
     의미 기반 확장·정규화·유사도 매칭 금지 — 리터럴 substring 매칭만 한다.
  3. 판정: 정의역 내 토큰 출현 >=1 → exit 1 (출현 위치 열거) / 출현 0 → exit 0.
     구조 실패 → exit 2 + 별도 메시지. 구조 실패 축 (CFP-2966 구현리뷰 Iter1 F-1 로 2축 추가):
       (i) 마커 부재·중복·역순  (ii) 배열 파싱 실패·토큰 수 != 4
       (iii) **포함관계 파괴** — 인용 절이 정의역 내부가 아님
       (iv) **정의역 0행 (vacuous-domain)** — 마커를 지우지 않고 **재배치**해 인용 절이 정의역
            전체를 덮으면 감산 결과가 공허해져 실 금지 조항이 있어도 "출현 0" 으로 PASS 한다.
     구조 실패를 exit 0 으로 흡수하지 않는다 (지우는 경로 + **옮기는 경로** 모두 차단).
     축별 검출력 정직 구분: (iv) 는 **조용한** 실패(vacuous GREEN)를 막는 축이고,
       (iii) 은 가드 부재 시에도 exit 1 로 시끄럽게 실패하던 것을 **올바른 사유**의 구조 실패로
       승격하는 정밀도 축이다 (신규 검출이 아님 — falsify 실측: 가드 제거 시 (iv)=exit 0 생존 /
       (iii)=exit 1 오사유). 과대 선언 금지.

정직 한계 (ADR-151 §결정 7 상속 — 모든 출력에 1줄 동반):
  closed set 4 리터럴 밖의 자연어 회피 표현(같은 뜻 다른 문장)은 미검출이다. 본 lint 은
  "금지 form 이 기계적으로 봉인된다" 를 주장하지 않는다 — presence ≠ truth.

자원 사용 (bounded degradation — 임의 입력 무해 아님, ADR-151 §결정 7 정직 천장):
  per-file 라인 cap(PER_FILE_SCAN_CAP) x per-line 길이 truncate(MAX_PHYSICAL_LINE_LEN) 로 총 작업량을
  유계화하고, 토큰 매칭은 리터럴 substring `in`(O(n)) 만 쓴다. 사용 regex 3종은 전부 bounded
  quantifier(`{0,N}`)라 nested/인접-무제한 quantifier 가 0 이다. **anchored 는 그중 1종**
  (`_BLOCKQUOTE_PREFIX_RE` 의 `^`)이고 `_ARRAY_OPEN_RE`·`_QUOTED_RE` 는 비anchored 리터럴 탐색이다
  (bound 의 근거는 anchor 가 아니라 quantifier 상한 — "3종 anchored" 로 뭉뚱그리지 않는다).
  라인 cap 초과로 마커가 잘리면
  구조 실패(exit 2) 로 착지한다(fail-closed). 실측 회귀가드 배선 = tests/scripts/ (QADev 소관).

Usage:
  check_adr178_forbidden_form_presence.py                # repo root 기준 default ADR 경로 스캔
  check_adr178_forbidden_form_presence.py <path> [...]   # 명시 파일 경로만 스캔 (argv = 파일 경로 전용)
  check_adr178_forbidden_form_presence.py --self-test    # inline fixture mutation oracle (CI/QADev)

  ★ 입력면 = 파일 경로만. PR body / Issue body / 커밋 메시지 등 외부 통제 텍스트를 소비하지 않는다
    (외부 입력 소비 시 재판정 trigger — CFP-2966 Change Plan §8.9).

Exit code:
  0 = PASS (정의역 내 금지 토큰 0) 또는 honest no-op (default 대상 ADR 부재 = consumer degradation)
  1 = 위반 (정의역 내 금지 토큰 출현 >=1)
  2 = 구조 실패 (마커/배열 계약 위반) 또는 setup error (명시 인자 경로 미존재)

ADR refs: ADR-178 §결정 7·12 (carrier) / ADR-171 (warning-first) / ADR-151 §결정 7 (honesty ceiling) /
  ADR-061 §결정 1 (Python SSOT + thin wrapper) / ADR-005 (byte-identical workflow pair) / ADR-119.
"""

import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TAG = "[adr178-forbidden-form]"

# ── 스캔 대상 default (repo root 상대) ─────────────────────────────────────────────
DEFAULT_TARGET = os.path.join(
    "archive", "adr", "ADR-178-subagent-progress-commit-preservation.md")

# ── 마커 리터럴 (ADR-178 §결정 7 이 고정한 이름 — 변경 시 ADR 문면과 동시 변경) ──────────
REGION_START = "<!-- progress-commit-normative-region:start -->"
REGION_END = "<!-- progress-commit-normative-region:end -->"
QUOTE_START = "<!-- forbidden-form-quotation:start -->"
QUOTE_END = "<!-- forbidden-form-quotation:end -->"

# ── closed set 크기 계약 (ADR-178 §결정 7 — 4 리터럴. 토큰 값 자체는 ADR 파싱이 SSOT) ────
EXPECTED_TOKEN_COUNT = 4

# ── 자원 상한 (bounded) ────────────────────────────────────────────────────────────
PER_FILE_SCAN_CAP = 20000   # 라인 count bound
MAX_PHYSICAL_LINE_LEN = 8192  # per-physical-line 길이 bound (count cap 과 별개 축)
MAX_TOKEN_LEN = 200         # 배열 원소 리터럴 길이 bound

# ── regex 3종 (전부 bounded quantifier — nested quantifier 0 / anchored 는 그중 1종) ──
#   bound 의 근거는 anchor 가 아니라 quantifier 상한이다 (docstring "자원 사용" 절과 동일 문면).
_BLOCKQUOTE_PREFIX_RE = re.compile(r"^\s{0,80}>\s{0,4}")
_ARRAY_OPEN_RE = re.compile(r"FORBIDDEN_TOKENS\s{0,4}=\s{0,4}\[")
_QUOTED_RE = re.compile(r'"([^"\n]{1,%d})"' % MAX_TOKEN_LEN)

HONEST_LIMIT_LINE = (
    f"{TAG} 정직 한계: closed set 밖 자연어 회피 표현은 미검출 — "
    "본 lint 은 금지 form 의 기계적 봉인을 주장하지 않는다 (presence ≠ truth, ADR-151 §결정 7 상속).")


def _read_lines(path):
    """파일을 라인 리스트로 읽는다 (count cap + per-line 길이 truncate). (lines, err) 반환."""
    lines = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for i, raw in enumerate(fh):
                if i >= PER_FILE_SCAN_CAP:
                    break
                raw = raw.rstrip("\n").rstrip("\r")
                lines.append(raw if len(raw) <= MAX_PHYSICAL_LINE_LEN
                             else raw[:MAX_PHYSICAL_LINE_LEN])
    except (OSError, UnicodeDecodeError) as e:
        return None, f"read error: {path}: {e}"
    return lines, None


def collect_domain_lines(lines):
    """검사 정의역 라인 수집 = normative-region 내부 - forbidden-form-quotation 블록.

    (domain_lines, quote_lines, structural_errors) 반환.
      domain_lines / quote_lines = [(lineno, text)] (마커 라인 자체는 양쪽 모두 제외)
    """
    errors = []
    counts = {
        REGION_START: 0, REGION_END: 0, QUOTE_START: 0, QUOTE_END: 0,
    }
    first_idx = {}
    for i, line in enumerate(lines, start=1):
        for marker in counts:
            if marker in line:
                counts[marker] += 1
                first_idx.setdefault(marker, i)

    for marker, label in (
            (REGION_START, "정의역 시작"), (REGION_END, "정의역 끝"),
            (QUOTE_START, "인용 절 시작"), (QUOTE_END, "인용 절 끝")):
        if counts[marker] == 0:
            errors.append(
                f"구조 실패 — {label} 마커 부재: `{marker}`. "
                "마커가 사라지면 검사 정의역이 소멸해 lint 이 조용히 무력화된다 (ADR-178 §결정 7).")
        elif counts[marker] > 1:
            errors.append(
                f"구조 실패 — {label} 마커 {counts[marker]}회 중복: `{marker}` (정확히 1회여야 정의역이 유일하다).")

    if not errors:
        if first_idx[REGION_END] <= first_idx[REGION_START]:
            errors.append("구조 실패 — 정의역 end 마커가 start 마커보다 앞선다 (region 역순).")
        if first_idx[QUOTE_END] <= first_idx[QUOTE_START]:
            errors.append("구조 실패 — 인용 절 end 마커가 start 마커보다 앞선다 (quotation 역순).")
        # 포함관계 축 (CFP-2966 구현리뷰 Iter1 F-1 / CP §8.2.5(a)) — 인용 절은 정의역 **내부**여야
        # 한다. 밖으로 나가면 감산 대상이 어긋나 정의역 의미가 바뀐다 (마커 개수·순서는 정상인 채).
        if not (first_idx[REGION_START] < first_idx[QUOTE_START]
                and first_idx[QUOTE_END] < first_idx[REGION_END]):
            errors.append(
                "구조 실패 — 인용 절이 정의역 내부에 포함되지 않는다 (포함관계 파괴: "
                f"region {first_idx[REGION_START]}~{first_idx[REGION_END]} vs "
                f"quotation {first_idx[QUOTE_START]}~{first_idx[QUOTE_END]}).")
    if errors:
        return [], [], errors

    domain_lines = []
    quote_lines = []
    in_region = False
    in_quote = False
    for i, line in enumerate(lines, start=1):
        if REGION_START in line:
            in_region = True
            continue
        if REGION_END in line:
            in_region = False
            continue
        if QUOTE_START in line:
            in_quote = True
            continue
        if QUOTE_END in line:
            in_quote = False
            continue
        if in_quote:
            quote_lines.append((i, line))
        elif in_region:
            domain_lines.append((i, line))

    # ── vacuous-domain 가드 (CFP-2966 구현리뷰 Iter1 F-1 / CP §8.2.5(a) ①) ──────────────
    # 마커를 **지우지 않고 재배치**해 인용 절이 정의역 전체를 덮으면 domain_lines == 0 이 되고,
    # 그러면 실 금지 조항이 규범에 실재해도 "출현 0" 으로 PASS 한다 (lint + 계약 테스트 동시
    # vacuous GREEN — 리뷰·DevPL 이중 재현). 부재·중복·역순 가드와 **동렬**로 구조 실패 처리한다.
    # 정직 상한: 정의역에 비공백 1행만 남기는 축소는 본 가드를 통과한다 (임계 N 은 임의수라
    #   도입하지 않는다 — 숫자 게이트 연극 회피). "정의역 붕괴가 봉인된다" 를 주장하지 않는다.
    if not any(text.strip() for _, text in domain_lines):
        errors.append(
            "구조 실패 — 검사 정의역(normative-region − quotation)에 비공백 라인이 0행이다. "
            "마커 개수·순서가 정상이어도 인용 절 재배치로 정의역이 덮이면 모든 금지 form 이 "
            "감산돼 vacuous GREEN 이 된다 (ADR-178 §결정 7 negative control 무력화).")
        return [], quote_lines, errors
    return domain_lines, quote_lines, errors


def parse_forbidden_tokens(quote_lines):
    """인용 절 내부 `FORBIDDEN_TOKENS` 배열을 파싱한다 (배열 = SSOT, 하드코딩 0).

    markdown blockquote(`> `) prefix 를 벗긴 뒤 배열 리터럴 span 안의 큰따옴표 원소만 추출.
    (tokens, structural_errors) 반환.
    """
    stripped = [_BLOCKQUOTE_PREFIX_RE.sub("", text) for _, text in quote_lines]
    joined = "\n".join(stripped)
    m = _ARRAY_OPEN_RE.search(joined)
    if not m:
        return [], ["구조 실패 — 인용 절 안에서 `FORBIDDEN_TOKENS = [` 배열 열림을 찾지 못했다 "
                    "(ADR-178 §결정 7 의 closed-set SSOT 배열 소실/변형)."]
    close = joined.find("]", m.end())
    if close == -1:
        return [], ["구조 실패 — `FORBIDDEN_TOKENS` 배열 닫힘 `]` 부재 (배열 파싱 불가)."]
    tokens = [t for t in _QUOTED_RE.findall(joined[m.end():close]) if t.strip()]

    errors = []
    if len(tokens) != EXPECTED_TOKEN_COUNT:
        errors.append(
            f"구조 실패 — `FORBIDDEN_TOKENS` 원소 수 {len(tokens)} != {EXPECTED_TOKEN_COUNT} "
            "(ADR-178 §결정 7 closed set 4 리터럴 계약 위반 — 축소는 검사력 침식, 확대는 ADR 문면 동반 변경 필요).")
    if len(set(tokens)) != len(tokens):
        errors.append("구조 실패 — `FORBIDDEN_TOKENS` 에 중복 원소 존재 (closed set 아님).")
    return tokens, errors


def scan_text(text, filename):
    """텍스트 1건 검사. (violations, structural_errors, tokens) 반환.

    self-test 및 외부 테스트가 직접 호출하는 공개 API (execution-backed oracle 용).
    """
    lines = []
    for i, raw in enumerate(text.splitlines()):
        if i >= PER_FILE_SCAN_CAP:
            break
        lines.append(raw if len(raw) <= MAX_PHYSICAL_LINE_LEN else raw[:MAX_PHYSICAL_LINE_LEN])

    domain_lines, quote_lines, errors = collect_domain_lines(lines)
    if errors:
        return [], errors, []
    tokens, token_errors = parse_forbidden_tokens(quote_lines)
    if token_errors:
        return [], token_errors, tokens

    violations = []
    for lineno, line in domain_lines:
        for tok in tokens:
            if tok in line:
                excerpt = line.strip()
                if len(excerpt) > 160:
                    excerpt = excerpt[:160] + "…"
                violations.append(
                    f"{filename}:{lineno}: 금지 form 토큰 '{tok}' 출현 — {excerpt}")
    return violations, [], tokens


def scan_file(path):
    """단일 파일 검사 후 exit code 반환 (0 PASS / 1 위반 / 2 구조 실패)."""
    lines, read_err = _read_lines(path)
    if read_err is not None:
        print(f"{TAG} {read_err}", file=sys.stderr)
        print(HONEST_LIMIT_LINE)
        return 2

    violations, errors, tokens = scan_text("\n".join(lines), path)

    if errors:
        print(f"{TAG} STRUCTURAL FAIL — 검사 계약 자체가 깨졌다 (위반 판정 불가, ADR-178 §결정 7):")
        for e in errors:
            print("  " + e)
        print(HONEST_LIMIT_LINE)
        return 2

    if violations:
        print(f"{TAG} FAIL — 규범 정의역 안에 금지 form 토큰 출현 (ADR-178 §결정 7 negative control 위반):")
        for v in violations:
            print("  " + v)
        print(f"{TAG} 정의역 = progress-commit-normative-region − forbidden-form-quotation "
              f"(closed set {len(tokens)} 리터럴, ADR 배열 파싱).")
        print(HONEST_LIMIT_LINE)
        return 1

    print(f"{TAG} PASS — {path}: 정의역(normative-region − quotation) 내 "
          f"closed set {len(tokens)} 토큰 출현 0.")
    print(HONEST_LIMIT_LINE)
    return 0


# ── self-test (inline fixture mutation oracle — 실 scan_text 호출, presence-grep oracle 금지) ──
def _fixture(domain_extra="", token_count=EXPECTED_TOKEN_COUNT,
             region_start=True, quote_start=True, layout="normal"):
    """합성 fixture 생성. 금지 토큰 리터럴은 fixture 자체가 선언(합성 토큰) — 실 ADR 토큰 하드코딩 0.

    layout (CFP-2966 F-1 — 마커 **삭제 0·개수 1·짝 정상** 인 채 배치만 바꾸는 축):
      "normal"      = 인용 절이 정의역 내부의 일부 (정상)
      "quote_wraps" = 인용 절이 정의역 전체를 감쌈 → 정의역 0행 (vacuous-domain)
      "quote_outside" = 인용 절이 정의역 밖에 위치 → 포함관계 파괴
    """
    synth = [f"금지형-{n}" for n in ("A", "B", "C", "D", "E")][:token_count]
    array_body = "\n".join(f'>     "{t}",  # 합성' for t in synth)
    quote_block = [
        "> 다음 형태는 규범으로 존재하지 않는다 (인용 절 — 정의역 제외):",
        ">", "> ```", "> FORBIDDEN_TOKENS = [", array_body, "> ]", "> ```",
    ]
    parts = []
    parts.append("# fixture 서두 (정의역 밖 — 여기 토큰이 있어도 위반 아님)")
    parts.append(f"{synth[0]} (정의역 밖 출현 — 무시되어야 한다)")

    if layout == "quote_outside":
        # 인용 절을 정의역 **앞**에 통째로 배치 (마커 4개 각 1회·짝 정상 유지)
        parts.append(QUOTE_START)
        parts.extend(quote_block)
        parts.append(QUOTE_END)
        parts.append(REGION_START)
        parts.append("### 규범 본체 — 정의역 안 정상 문면")
        if domain_extra:
            parts.append(domain_extra)
        parts.append(REGION_END)
        parts.append("# fixture 말미")
        return "\n".join(parts) + "\n", synth

    if region_start:
        parts.append(REGION_START)
    if layout == "quote_wraps":
        # 정의역 시작 직후 인용 절 시작 / 정의역 끝 직전 인용 절 끝 → 감산 후 0행
        parts.append(QUOTE_START)
    parts.append("### 규범 본체 — 정의역 안 정상 문면")
    if domain_extra:
        parts.append(domain_extra)
    if layout != "quote_wraps":
        if quote_start:
            parts.append(QUOTE_START)
        parts.extend(quote_block)
        parts.append(QUOTE_END)
        parts.append("### 정의역 잔여 문면")
    else:
        parts.extend(quote_block)
        parts.append(QUOTE_END)
    parts.append(REGION_END)
    parts.append("# fixture 말미")
    return "\n".join(parts) + "\n", synth


def self_test():
    cases = []

    green_text, synth = _fixture()
    cases.append(("GREEN: 토큰이 인용 절 안에만 존재 (self-RED 함정 회피)", green_text, 0))

    red_text, _ = _fixture(domain_extra=f"규범 문면에 {synth[1]} 조항이 재유입되었다.")
    cases.append(("RED: 정의역 내부(인용 절 밖)에 금지 토큰 주입", red_text, 1))

    near_text, _ = _fixture(domain_extra="금지형 A 와 유사하나 리터럴이 다른 회피 표현 (미검출 = 선언된 상한).")
    cases.append(("GREEN: closed set 밖 자연어 회피 표현 미검출 (정직 상한 실증)", near_text, 0))

    nostart_text, _ = _fixture(quote_start=False)
    cases.append(("STRUCT: 인용 절 start 마커 제거 → 구조 실패", nostart_text, 2))

    noregion_text, _ = _fixture(region_start=False)
    cases.append(("STRUCT: 정의역 start 마커 제거 → 구조 실패", noregion_text, 2))

    short_text, _ = _fixture(token_count=3)
    cases.append(("STRUCT: FORBIDDEN_TOKENS 원소 3개 (!=4) → 구조 실패", short_text, 2))

    long_text, _ = _fixture(token_count=5)
    cases.append(("STRUCT: FORBIDDEN_TOKENS 원소 5개 (!=4) → 구조 실패", long_text, 2))

    noarray_text = green_text.replace("FORBIDDEN_TOKENS = [", "TOKENS_LIST = [")
    cases.append(("STRUCT: 배열 이름 변형 (파싱 실패) → 구조 실패", noarray_text, 2))

    # ── CFP-2966 구현리뷰 Iter1 F-1 / CP §8.2.5(a) — 마커 삭제 0·개수 1·짝 정상 인 채 **재배치** ──
    # 두 케이스 모두 실 금지 토큰을 규범 문면에 주입한 상태다. 가드가 없으면 감산 결과가
    # 공허해져 exit 0(vacuous GREEN)으로 생존한다 — 즉 expect 2 는 가드가 살아있을 때만 성립.
    wrap_text, wsynth = _fixture(
        domain_extra="규범 문면에 금지 조항이 실재한다.", layout="quote_wraps")
    wrap_text = wrap_text.replace("규범 문면에 금지 조항이 실재한다.",
                                  f"규범 문면에 {wsynth[1]} 조항이 실재한다.")
    cases.append(("STRUCT: 인용 절이 정의역 전체를 감쌈 → 정의역 0행 vacuous 차단 "
                  "(가드 제거 시 exit 0 으로 생존 = falsify 앵커)", wrap_text, 2))

    outside_text, osynth = _fixture(
        domain_extra="규범 문면에 금지 조항이 실재한다.", layout="quote_outside")
    outside_text = outside_text.replace("규범 문면에 금지 조항이 실재한다.",
                                        f"규범 문면에 {osynth[1]} 조항이 실재한다.")
    cases.append(("STRUCT: 인용 절이 정의역 밖에 위치 → 포함관계 파괴 차단", outside_text, 2))

    failed = []
    for name, text, expect in cases:
        violations, errors, _tokens = scan_text(text, "<fixture>")
        got = 2 if errors else (1 if violations else 0)
        status = "OK" if got == expect else "MISMATCH"
        if got != expect:
            failed.append((name, expect, got))
        print(f"  [{status}] {name} (expect exit {expect}, got {got})")

    if failed:
        print(f"[self-test] FAIL — {len(failed)} case mismatch")
        return 1
    print(f"[self-test] PASS — {len(cases)}/{len(cases)} case "
          "(정의역 주입 RED / 인용 절 GREEN / 마커 제거·배열 변형·원소 수 불일치 STRUCT / "
          "마커 재배치 2축 [정의역 0행·포함관계 파괴] STRUCT discriminating).")
    print(HONEST_LIMIT_LINE)
    return 0


def main(argv):
    args = argv[1:]
    if "--self-test" in args:
        return self_test()
    flags = [a for a in args if a.startswith("-")]
    if flags:
        print(f"{TAG} setup error: 미지원 인자 {flags} — argv 는 파일 경로만 받는다 "
              "(외부 통제 텍스트 소비 금지).", file=sys.stderr)
        return 2

    paths = list(args)
    if not paths:
        if not os.path.exists(DEFAULT_TARGET):
            print(f"{TAG} 대상 ADR({DEFAULT_TARGET}) 부재 — honest no-op (PASS, consumer degradation).")
            print(HONEST_LIMIT_LINE)
            return 0
        paths = [DEFAULT_TARGET]
    else:
        for p in paths:
            if not os.path.isfile(p):
                print(f"{TAG} setup error: 파일 미존재: {p}", file=sys.stderr)
                return 2

    worst = 0
    for p in paths:
        rc = scan_file(p)
        if rc == 2:
            worst = 2
        elif rc == 1 and worst != 2:
            worst = 1
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
