#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/_ac_marker_mutations.py — `scripts/lib/ac_pr_markers.py` mutation 공통 helper
(CFP-2659 F1 / ADR-145 Amendment 5 §8.4 — marker-parsing born-hollow 봉인 mutation-kill).

pytest(`test_ac_pr_markers.py`) 와 shell self-test(`test_check-ac-traceability-matrix.sh`) 가
**동일 변조 후보 목록**을 공유한다 (ADR-140 hygiene — 이중 정의 drift 봉인).

변조 semantic 2 축:
  decor    — 장식 tolerance(bounded `\*{0,2}`) 무력화 → `- **story_uri**: <url>` 이 **미인식(RED)** 으로
             뒤집혀야 kill. 원본은 인식(GREEN) — 대조로 vacuous 아님 입증.
  cleancap — 값-bold clean capture(lazy 캡처 / trailing `*` strip) 무력화 → `**story_uri: <url>**` 캡처가
             **dirty**(`endswith("*")`) 로 뒤집혀야 kill. 원본은 clean.

honesty 계약 (born-broken 방지 — CFP-2530/2535 계보):
  · 변조가 실제로 적용되지 않으면(diff 0) 그 후보는 yield 되지 않는다. 하나도 적용 안 되면
    호출자는 **INCONCLUSIVE → FAIL** 처리 의무 (presence-only 통과 금지).
  · 변조본이 import/compile 불가면(regex 파손 등) kill 이 아니라 **broken mutant** — yield 대상에서 제외.
    (모듈이 통째로 죽은 것을 "탐지" 로 오판하지 않는다.)

underscore prefix = pytest 미수집(테스트 아님).
"""
import argparse
import importlib.util
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

# 테스트-더블 주입점 (기존 AC_TRACE_LIB 관례 답습 — 기본 = 실 Dev 모듈)
AC_TRACE_LIB = os.environ.get("AC_TRACE_LIB", os.path.join(REPO_ROOT, "scripts", "lib"))
AC_MARKERS_PY = os.environ.get("AC_MARKERS_PY", os.path.join(AC_TRACE_LIB, "ac_pr_markers.py"))

# (desc, kind, needle, repl) — kind: "literal" | "regex". 순서 = 우선순위(구체적 → 일반적).
#   여러 인코딩(정규식 lazy-capture 방식 / rstrip 방식) 중 실제 구현이 쓴 것에 걸리도록 후보를 나열한다.
#   "같은 semantic 의 다른 표기" 를 커버하는 것이지, semantic 자체를 넓히는 것이 아니다.
CANDIDATES = {
    # 장식 tolerance 삭제 — `- **story_uri**:` 가 미인식(RED)으로 뒤집혀야 kill.
    "decor": [
        (r"marker-anchored bounded 토큰 제거 `\*{0,2}story_uri\*{0,2}` → `story_uri` (실 결정라인)",
         "literal", r"\*{0,2}story_uri\*{0,2}", "story_uri"),
        (r"bounded `\*{0,2}` 토큰 전면 제거 (인코딩 drift fallback)", "literal", r"\*{0,2}", ""),
        (r"charclass `[*]{0,2}` 토큰 제거 (인코딩 drift fallback)", "literal", "[*]{0,2}", ""),
        (r"optional `(?:\*\*)?` 토큰 제거 (인코딩 drift fallback)", "literal", r"(?:\*\*)?", ""),
    ],
    # 값-bold clean capture 삭제 — `**story_uri: url**` 캡처가 dirty(`url**`) 로 뒤집혀야 kill.
    "cleancap": [
        (r"bounded strip 상한 `_MAX_BOLD_ASTERISKS = 2` → `0` (strip loop no-op — 실 결정라인)",
         "regex", r"_MAX_BOLD_ASTERISKS\s*=\s*2", "_MAX_BOLD_ASTERISKS = 0"),
        (r'strip loop 조건 `if out.endswith("*"):` → `if False:` (실 결정라인)',
         "literal", 'if out.endswith("*"):', "if False:  # MUTATED-CLEANCAP"),
        (r"URI 경로 strip 호출 제거 `_strip_trailing_decor(m.group(1))` → `m.group(1)`",
         "regex", r"_strip_trailing_decor\(\s*m\.group\(1\)\s*\)", "m.group(1)"),
        (r"lazy 값 캡처 `\S+?` → greedy `\S+` (인코딩 drift fallback)", "literal", r"\S+?", r"\S+"),
        (r'`.rstrip("*")` 무력화 (인코딩 drift fallback)', "regex",
         r"""\.rstrip\(\s*['"][^'"]*\*[^'"]*['"]\s*\)""", ""),
    ],
}


def read_source(path=None):
    with open(path or AC_MARKERS_PY, encoding="utf-8") as fh:
        return fh.read()


def _apply(src, kind, needle, repl):
    if kind == "literal":
        if needle not in src:
            return src, 0
        return src.replace(needle, repl), src.count(needle)
    mutated, n = re.subn(needle, lambda _m: repl, src)
    return mutated, n


def load_module(path, name):
    """단일 파일 모듈 로드 (pure leaf — sibling import 없음). 실패 시 예외 전파."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # noqa: S102 — 테스트 격리 temp 사본
    return mod


def iter_mutants(kind, out_dir, src_path=None):
    """kind 축의 후보를 순회하며 **실제 적용(diff≠0) ∧ import 가능** 한 변조본만 yield.

    yield (desc, mutant_path, mutant_module).
    적용 0 건 → 아무것도 yield 되지 않음 → 호출자가 INCONCLUSIVE(FAIL) 처리.
    """
    src = read_source(src_path)
    os.makedirs(out_dir, exist_ok=True)
    for idx, (desc, mkind, needle, repl) in enumerate(CANDIDATES[kind]):
        mutated, hits = _apply(src, mkind, needle, repl)
        if hits == 0 or mutated == src:
            continue  # 미적용 — diff 0
        sub = os.path.join(out_dir, f"{kind}_{idx}")
        os.makedirs(sub, exist_ok=True)
        dst = os.path.join(sub, "ac_pr_markers.py")
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(mutated)
        try:
            mod = load_module(dst, f"_mut_{kind}_{idx}")
        except Exception as exc:  # broken mutant(regex 파손 등) — kill 로 오판 금지
            sys.stderr.write(f"[skip broken mutant] {kind}#{idx} {desc}: {exc}\n")
            continue
        yield desc, dst, mod


def _main(argv=None):
    # Windows 기본 콘솔 인코딩(cp949) 에서 desc 의 em-dash/화살표가 UnicodeEncodeError 로 죽으면
    # shell 호출부가 "변조 후보 0"(INCONCLUSIVE) 으로 오판한다 — stdout/stderr 를 UTF-8 로 고정.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):  # 비-TextIO(파이프 wrapper) — 관용
            pass

    ap = argparse.ArgumentParser(description="ac_pr_markers.py mutation builder (G-DECOR / G-CLEANCAP)")
    ap.add_argument("--kind", required=True, choices=sorted(CANDIDATES))
    ap.add_argument("--out", required=True, help="변조본 출력 dir")
    ap.add_argument("--src", default=None, help="원본 경로 override (default: $AC_MARKERS_PY)")
    args = ap.parse_args(argv)

    src_path = args.src or AC_MARKERS_PY
    if not os.path.isfile(src_path):
        sys.stderr.write(f"원본 부재: {src_path}\n")
        return 2
    count = 0
    for desc, path, _mod in iter_mutants(args.kind, args.out, src_path):
        sys.stdout.write(f"{path}\t{desc}\n")
        count += 1
    if count == 0:
        sys.stderr.write(f"INCONCLUSIVE: kind={args.kind} — 적용 가능한 변조 후보 0 (diff 0 / broken)\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
