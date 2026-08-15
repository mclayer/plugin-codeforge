#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""_absolute_claim_ratchet.py — 신규 절대주장 줄의 **결박 동반** 검사 (diff-scoped ratchet).

── 계기 (구현리뷰 iter1~iter6 지배 class) ────────────────────────────────────────
  6라운드가 같은 형상을 반복 지적했다: **글로 쓴 단정이 코드보다 넓다.** 새 docstring·
  헤더·문서 문장이 절대주장 어휘(아래 `TOKENS`)를 쓰는데, 그 명제를 정의역으로 삼는
  오라클이 없어 **RED 가 될 수 없는** 선언이 된다. iter6 findings 8건 중 수치 축 0 ·
  산문 축 5 였다. 직전 라운드가 수치 축을 §8.7 기계 파생으로 닫았고, 본 모듈은
  **산문 축의 신규 유입**만 막는다.

── 정의역 (좁게 고정) ──────────────────────────────────────────────────────────
  · 대상 = `origin/main...HEAD` 3-dot diff 의 **추가 줄**. 기존 재고는 대상 밖이다
    (출혈 중단이 목적 — 전수 탐색으로 넓히면 또 hollow gate 를 낳는다).
  · 비교 기준은 §8.7 생성기(`scripts/lib/impl_manifest.py:git_diff_axis`)와 **같은 축**
    을 쓴다. 두 번째 기준을 정의하지 않는다.

── 판정 (줄 단위, 우선순위 순) ─────────────────────────────────────────────────
  ① `[ceiling:]` 마커 + 사유 공백            → `empty-ceiling`    (위반)
  ② `[bound: <test-symbol>]` + 심볼 실재     → `bound`            (통과 — 강한 해소)
     같은 마커 + 심볼 미해소                  → `unresolved-bound` (위반)
  ③ `[ceiling: <사유>]` 마커 + 사유 유의미   → `ceiling`          (통과)
  ④ 마커 없음 + 같은 diff 에 `tests/**` 변경 → `test-accompanied` (통과 — 약함)
  ⑤ 그 외                                    → `unbound`          (위반)

  ①이 ④보다 **앞선다**. 빈 마커는 "천장을 선언하겠다"는 의사표시를 해놓고 내용을
  비운 것이라 미선언보다 나쁘고, 동반 완화로 씻겨나가면 ①이 사문이 된다.
  ②의 **미해소도 ④가 씻지 못한다** — 실재하지 않는 테스트 이름을 적어 넣는 것이
  가장 값싼 우회이기 때문이다.

  `[bound:]` 의 심볼 실재 판정은 `tests/**` 를 `ast` 로 파싱해 정의된 함수/클래스
  이름을 모아 대조한다. 문자열 매칭(grep)이면 주석·docstring 안 이름이 통과하므로
  쓰지 않는다. 수집기는 새로 만들지 않고 같은 문제를 이미 푼
  `scripts/lib/check_ac_traceability_matrix.py:collect_test_symbols`(Hop3 born-missing,
  ADR-136 Amd3 L3 "born-missing = ast, grep-only = false-oracle")를 import 해 쓴다.

── 정직 천장 (ADR-119 — 이 검사가 **못 하는** 것) ───────────────────────────────
  · ④는 **결박이 아니라 동반 강제**다. `tests/**` 의 *어떤* 변경이든 통과시키며,
    그 변경이 해당 명제를 정의역으로 삼는지 판정하지 않는다. Story PR 은 대개
    `tests/**` 를 건드리므로 ④ 경로에서 이 검사의 실효 판별력은 낮다. 이 사실을
    은폐하지 않기 위해 리포트는 ④로 통과한 줄도 **전량 열거**한다(무증상 GREEN 금지).
    ④를 없애지는 않았다 — 없애면 기존 저작 흐름이 막히므로, 대신 저자가 고를 수 있는
    강한 해소 경로로 ②를 뒀다.
  · ②도 **심볼이 실재하는지**까지만 본다. 그 테스트가 해당 명제를 실제로 반증하는지
    (정의역·강도)는 판정하지 않는다 — 이름만 맞는 무관한 테스트를 대면 통과한다.
    ⇒ 이 검사가 세우는 것은 "신규 선언이 오라클에 결박된다"가 **아니라**
      「천장 마커 결박 ⊕ 테스트 동반(판별력 낮음) ⊕ `[bound:]` 심볼 실재 검증」이다.
  · **패러프레이즈 우회**를 막지 못한다. `TOKENS` 는 어휘 목록이지 의미 판정기가
    아니다 — 같은 절대주장을 목록 밖 표현으로 쓰면 통과한다. 이 천장은 산문으로만
    두지 않고 `test_paraphrased_absolute_claim_is_outside_detection_domain` 이
    **assert 로 각인**한다(검사기를 의미 축으로 넓히면 그 테스트가 RED 가 되어
    천장 문서 갱신이 강제된다).
  · **use 와 mention 을 구분하지 못한다.** 토큰을 *언급*하는 줄(어휘 정의·합성
    fixture·검사 자신을 설명하는 산문)도 걸린다. 그 줄들은 ③으로 정직하게 처리한다.
  · 기존 재고(정의역 밖)와 **다른 repo**(codeforge-internal-docs 의 Story 문서)에는
    도달하지 않는다.
  · 어휘는 **한글만** 담는다. 영문 등가어(`always`/`atomic` 등)는 이 repo 에서
    오탐원이다 — `.github/workflows/**` 의 `always()` 16 site 가 실측 근거다.
  · 판정은 **커밋된 내용**(HEAD) 기준이다. 워킹트리의 미커밋 수정은 3-dot diff 에
    나타나지 않으므로 로컬 선실행은 마지막 커밋 상태를 잰다.
"""

import argparse
import os
import re
import subprocess
import sys
from collections import namedtuple

RATCHET_VERSION = "absolute-claim-ratchet v1"

# 절대주장 어휘. 문자열 **포함**(substring) 매칭이다.
# ★ 마커는 **같은 줄**에 있어야 판정에 쓰인다. 앞줄에 달아둔 마커는 그 줄을 풀어주지
#   않는다(줄 단위 판정) — 이 검사를 만들면서 저자가 먼저 걸렸던 지점이다.
TOKENS = ("손실 0", "잔여 0", "무손상", "무조건", "항상", "전건", "원자적", "불가능", "0건")  # [ceiling: 어휘 정의 리터럴 — 주장이 아니라 검사 대상 목록의 mention 이다]

# `[ceiling: <사유>]` — 대괄호 안, 콜론 뒤 전체를 사유로 본다.
CEILING_RE = re.compile(r"\[ceiling:([^\]]*)\]")
# `[bound: <test-symbol>]` — 강한 해소. 심볼이 tests/** 아래 실재해야 통과한다.
BOUND_RE = re.compile(r"\[bound:([^\]]*)\]")
# 사유 "유의미" 판정: 글자/숫자가 하나라도 있어야 한다 (`[ceiling: -]` 류 우회 차단).
_MEANINGFUL_RE = re.compile(r"[0-9A-Za-z가-힣]")
# 파이썬 식별자 — `[bound:]` 값은 심볼명 하나여야 한다.
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_DIFF_GIT_RE = re.compile(r"^diff --git ")

TEST_PATH_PREFIX = "tests/"

AddedLine = namedtuple("AddedLine", "path lineno text")
Claim = namedtuple("Claim", "path lineno text tokens disposition reason")

# 위반으로 계상하는 disposition
FAIL_DISPOSITIONS = ("empty-ceiling", "unresolved-bound", "unbound")

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_BASE_UNRESOLVED = 2


# ═══════════════════════════ 순수 파서 ═══════════════════════════════════════════
def _strip_ab_prefix(spec):
    """`b/path` · `a/path` → `path`. `/dev/null` → None."""
    spec = spec.strip()
    if spec == "/dev/null":
        return None
    for pre in ("a/", "b/"):
        if spec.startswith(pre):
            return spec[len(pre):]
    return spec or None


def parse_added_lines(diff_text):
    """unified diff → 추가 줄 목록 `[AddedLine(path, lineno, text)]`.

    ★ hunk 헤더의 **행수 카운트를 소진**하며 읽는다. `+`/`-` 접두만 보고 갈라내면
      hunk **본문**에 있는 `--- x` / `+++ y` 내용 줄을 파일 헤더로 오인한다
      (내용이 `--`/`++` 로 시작하는 추가 줄은 diff 상에서 `---`/`+++` 로 렌더된다).
      카운트 소진 방식은 헤더와 본문을 상태로 분리하므로 그 혼동이 생기지 않는다.

    삭제 줄(`-`)과 문맥 줄(` `)은 결과에 담지 않는다 — 문맥 줄은 새 파일의 행번호를
    전진시키는 역할만 한다."""
    out = []
    path = None
    new_lineno = 0
    old_rem = new_rem = 0
    in_hunk = False

    for raw in diff_text.splitlines():
        if in_hunk and (old_rem > 0 or new_rem > 0):
            if raw.startswith("\\"):            # "\ No newline at end of file"
                continue
            if raw.startswith("+"):
                if path is not None:
                    out.append(AddedLine(path, new_lineno, raw[1:]))
                new_lineno += 1
                new_rem -= 1
            elif raw.startswith("-"):
                old_rem -= 1
            else:                                # 문맥 줄 (" " 접두 또는 빈 줄)
                new_lineno += 1
                new_rem -= 1
                old_rem -= 1
            if old_rem <= 0 and new_rem <= 0:
                in_hunk = False
            continue

        in_hunk = False
        m = _HUNK_RE.match(raw)
        if m:
            new_lineno = int(m.group(3))
            old_rem = int(m.group(2)) if m.group(2) is not None else 1
            new_rem = int(m.group(4)) if m.group(4) is not None else 1
            in_hunk = old_rem > 0 or new_rem > 0
            continue
        if _DIFF_GIT_RE.match(raw):
            path = None
            continue
        if raw.startswith("+++ "):
            path = _strip_ab_prefix(raw[4:])
            continue
    return out


def changed_paths(diff_text):
    """diff 가 건드린 경로 집합 (`+++`/`---` 헤더 기준, `/dev/null` 제외).

    삭제된 파일은 `+++ /dev/null` 이라 `--- a/<path>` 쪽에서 건진다."""
    paths = set()
    prev_minus = None
    for raw in diff_text.splitlines():
        if raw.startswith("--- "):
            prev_minus = _strip_ab_prefix(raw[4:])
            continue
        if raw.startswith("+++ "):
            p = _strip_ab_prefix(raw[4:])
            if p:
                paths.add(p)
            elif prev_minus:
                paths.add(prev_minus)
            prev_minus = None
            continue
        prev_minus = None
    return paths


def ceiling_reason(text):
    """`[ceiling: <사유>]` 파싱 → 사유 문자열 / `""`(공백 사유) / `None`(마커 없음).

    마커 다중 등장 시 **유의미한 사유 하나라도** 있으면 그것을 돌려준다."""
    found = CEILING_RE.findall(text)
    if not found:
        return None
    for raw in found:
        reason = raw.strip()
        if _MEANINGFUL_RE.search(reason):
            return reason
    return ""


def bound_symbol(text):
    """`[bound: <symbol>]` 파싱 → 심볼명 / `""`(마커는 있으나 심볼로 못 읽음) / `None`.

    값이 식별자 형태가 아니면 `""` 로 접어 미해소(위반) 쪽으로 보낸다."""
    found = BOUND_RE.findall(text)
    if not found:
        return None
    for raw in found:
        sym = raw.strip()
        if _IDENT_RE.match(sym):
            return sym
    return ""


def _load_symbol_collector():
    """Hop3(born-missing)의 `ast` 수집기를 **재사용**한다 — 새로 만들지 않는다.

    같은 문제(명명 테스트가 실재하는가)를 이미 푼 구현이 있고, grep 기반 재작성은
    주석·docstring 안 이름을 통과시키는 false-oracle 이 된다(ADR-136 Amd3 L3)."""
    lib = os.path.join(repo_root_from(), "scripts", "lib")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    from check_ac_traceability_matrix import collect_test_symbols
    return collect_test_symbols


def collect_bound_symbols(repo_root=None, tests_root=None):
    """`tests/**` 아래 정의된 함수/클래스 이름 집합. 루트 부재 시 `None`(판정불가)."""
    root = repo_root_from(repo_root)
    target = tests_root or os.path.join(root, TEST_PATH_PREFIX.rstrip("/"))
    return _load_symbol_collector()(target)


def match_tokens(text, tokens=TOKENS):
    return [t for t in tokens if t in text]


# ═══════════════════════════ 판정 ═══════════════════════════════════════════════
_R_UNRESOLVED = "결박 심볼 미해소 — tests/** 아래 ast 로 확인되지 않는다"


def classify_line(text, tests_touched=False, allow_test_accompaniment=True, symbol_index=()):
    """줄 하나 → `(disposition, 사유)`. 우선순위 SSOT = 모듈 docstring §판정.

    `symbol_index` 기본값은 **빈 집합**이다 — 미제공 상태에서 `[bound:]` 를 통과시키면
    검증 없는 해소가 되므로 fail-closed 로 둔다."""
    symbols = symbol_index or ()
    reason = ceiling_reason(text)
    bound = bound_symbol(text)

    if reason is not None and not reason:
        return "empty-ceiling", "ceiling 마커 사유 공백 (빈 마커 우회 차단)"
    if bound is not None:
        if bound and bound in symbols:
            return "bound", "결박 심볼 실재 — %s" % bound
        return "unresolved-bound", "%s (%s)" % (_R_UNRESOLVED, bound or "심볼 미기재")
    if reason:
        return "ceiling", "ceiling 사유 기재 — %s" % reason
    if allow_test_accompaniment and tests_touched:
        return "test-accompanied", "같은 diff 에 tests/** 변경 동반 (동반 강제 — 결박 아님)"
    return "unbound", "결박 부재 — tests/** 변경 미동반 · 마커 없음"


def evaluate(diff_text, tokens=TOKENS, allow_test_accompaniment=True, only_prefixes=None,
             symbol_index=()):
    """diff 텍스트 → 판정 결과 dict (순수 — git 호출 없음)."""
    added = parse_added_lines(diff_text)
    touched = changed_paths(diff_text)
    tests_touched = any(p.startswith(TEST_PATH_PREFIX) for p in touched)

    claims = []
    for a in added:
        if only_prefixes and not any(a.path.startswith(p) for p in only_prefixes):
            continue
        hits = match_tokens(a.text, tokens)
        if not hits:
            continue
        disp, why = classify_line(a.text, tests_touched, allow_test_accompaniment, symbol_index)
        claims.append(Claim(a.path, a.lineno, a.text, hits, disp, why))

    return {
        "version": RATCHET_VERSION,
        "tests_touched": tests_touched,
        "changed_files": sorted(touched),
        "added_lines": len(added),
        "claims": claims,
        "violations": [c for c in claims if c.disposition in FAIL_DISPOSITIONS],
    }


def format_report(result, show_passed=True):
    """판정 결과 → 사람이 읽는 줄 목록. ③(동반 통과)도 열거해 느슨함을 드러낸다."""
    lines = []
    order = {"unbound": 0, "unresolved-bound": 1, "empty-ceiling": 2,
             "bound": 3, "ceiling": 4, "test-accompanied": 5}
    for c in sorted(result["claims"], key=lambda c: (order.get(c.disposition, 9), c.path, c.lineno)):
        fail = c.disposition in FAIL_DISPOSITIONS
        if not fail and not show_passed:
            continue
        lines.append("%-4s %s:%d  [토큰: %s]  %s"
                     % ("FAIL" if fail else "ok", c.path, c.lineno, ", ".join(c.tokens), c.reason))
    tally = {}
    for c in result["claims"]:
        tally[c.disposition] = tally.get(c.disposition, 0) + 1
    n_accomp = tally.get("test-accompanied", 0)
    lines.append("요약: 위반 %d · bound %d · ceiling %d · test-accompanied %d "
                 "(추가줄 %d 중 claim %d)"
                 % (len(result["violations"]), tally.get("bound", 0), tally.get("ceiling", 0),
                    n_accomp, result["added_lines"], len(result["claims"])))
    if n_accomp:
        lines.append("주의: test-accompanied %d 줄은 **동반 강제**로 통과했다 — 해당 명제가 "
                     "테스트 정의역에 들어갔는지 이 검사는 판정하지 않는다." % n_accomp)
    return lines


# ═══════════════════════════ git 실측 (impure) ═══════════════════════════════════
def _run(cmd, cwd, timeout=300):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def repo_root_from(start=None):
    if start:
        return os.path.abspath(start)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def diff_text_from_git(repo_root=None, base_ref="origin/main"):
    """`git diff -U0 <base>...HEAD` 원문. base 미해소 시 `None`(조용한 통과 금지).

    §8.7 생성기와 같은 3-dot 축이다. `-U0` 은 문맥 줄을 없애 스캔량을 줄일 뿐이고,
    파서는 문맥 줄이 있는 diff 도 그대로 읽는다."""
    root = repo_root_from(repo_root)
    probe = _run(["git", "rev-parse", "--verify", "--quiet", base_ref + "^{commit}"], root)
    if probe.returncode != 0:
        return None
    cp = _run(["git", "diff", "--no-color", "--no-ext-diff", "-U0", "%s...HEAD" % base_ref], root)
    if cp.returncode != 0:
        return None
    return cp.stdout or ""


# ═══════════════════════════ CLI ════════════════════════════════════════════════
def main(argv=None):
    ap = argparse.ArgumentParser(description="신규 절대주장 줄의 결박 동반 검사 (diff-scoped)")
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--base-ref", default="origin/main")
    ap.add_argument("--strict", action="store_true",
                    help="tests/** 동반 완화(③)를 끈다 — ceiling 마커만 통과 사유로 인정")
    ap.add_argument("--only", action="append", default=None,
                    help="경로 접두 필터 (반복 가능)")
    ap.add_argument("--quiet-passed", action="store_true", help="통과 줄 열거 생략")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):      # cp949 콘솔에서 한글 출력이 깨지지 않게
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    root = repo_root_from(args.repo_root)
    diff = diff_text_from_git(root, args.base_ref)
    if diff is None:
        print("[%s] base ref 미해소: %s — **미판정**으로 종료한다 "
              "(shallow clone 이면 fetch-depth: 0 필요)" % (RATCHET_VERSION, args.base_ref))
        return EXIT_BASE_UNRESOLVED

    symbols = collect_bound_symbols(root)
    if symbols is None:
        print("[%s] tests/** 루트 미해소 — `[bound:]` 판정불가라 **미판정**으로 종료한다"
              % RATCHET_VERSION)
        return EXIT_BASE_UNRESOLVED

    result = evaluate(diff, allow_test_accompaniment=not args.strict, only_prefixes=args.only,
                      symbol_index=symbols)
    head = _run(["git", "rev-parse", "--short", "HEAD"], root).stdout.strip()
    print("[%s] base=%s head=%s strict=%s tests-symbols=%d"
          % (RATCHET_VERSION, args.base_ref, head, bool(args.strict), len(symbols)))
    for ln in format_report(result, show_passed=not args.quiet_passed):
        print(ln)
    return EXIT_VIOLATION if result["violations"] else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
