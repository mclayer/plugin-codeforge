#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_failover_detection_classifier.py

CFP-2823 Phase 2 (구현) — AC-4 discriminating check fixture.

계약 SSOT: Story CFP-2823 §5.3 AC-4 + §7.7 "AC-4 discriminating check (상설화)".
규범 SSOT: archive/adr/ADR-109 §결정1 Amendment 1 (c) enum single-SSOT (G1).

본 fixture 가 검증하는 것 = fable-리밋 opus failover 의 "리밋 계열 감지 classifier" 판별력.
classifier semantics = ADR-109 §결정1 closed-set literal-substring any-match
  (no regex wildcard) — §9 reproducer `sys.exit(0 if any(p in s for p in pats) else 1)` 동형.

── G1 (enum single-SSOT, 하드코딩 금지) ─────────────────────────────────────────
  - 감지 enum(6 literal) = ADR-109 (b) 절 code-fence(L293-300) 를 **파싱**해 사용.
    하드코딩 사본 = 설계리뷰 명시 Phase 2 결함(fixture-vs-SSOT drift). _EXPECTED_ENUM
    상수는 **파싱 검증 oracle** 로만 쓰이며 classifier enum 으로 절대 쓰이지 않는다
    (classifier 는 PARSED list 만 소비 — 아래 classify_exit 호출부 전부 ENUM slice).
  - golden 실관측 문자열 = ADR-109 (a) 절 code-fence(L283-285) 를 **파싱**(합성 금지 —
    captured-golden = 2026-07-24 실관측 세션 리밋 task-notification).
  - (a) fence 는 문장(따옴표 literal 아님), (b) fence 는 quoted-literal — `^"[^"]+"$`
    라인 필터로 구분. §결정1 base-4 fence(L113-118)는 (b) heading 이전이라 section-scope
    로 자연 배제.

── 5 필수 assertion (positive-only 금지, negative 포함) ────────────────────────
  1. RED→GREEN: base-only(앞 4) vs golden → exit 1(RED); base+session(앞 5) → exit 0(GREEN);
     full 6 → GREEN. 각 결정론 재현(RED/GREEN 명확 구분).
  2. M1 mutation-kill: enum 에서 `session limit` 제거 → golden 에 대해 RED flip(GREEN→RED)
     = classifier 판별력(session limit = discriminating literal) 실증.
  3. negative — `usage limit` 무기여: enum 에서 `usage limit` 제거해도 verdict = GREEN 불변
     (usage limit 실관측 0건·discriminating 무기여).
  4. negative — 529: `API Error: 529 overloaded` → 6-literal 감지집합 RED(NOT-IN);
     `429` literal 이 `529` 문자열에 substring 매칭 안 됨 병행 확인.
  5. negative — 진짜 미분류: `ImportError: no module named foo` → RED.
  + parse sanity(S1/S2): 파싱 enum == 예상 6(순서 포함) / golden 실관측 property — 파싱 실패 시 RED.

── anti-theater / exit-masking 금지 (ADR-060 Amendment 22) ─────────────────────
  - bare `cmd || true` exit-masking 0건. 모든 assertion 은 classifier 실 반환값 / 파싱 실
    내용을 검사(tautology 0). mock-seam env export 0(실관측 golden 직접 검증).
  - RED/GREEN 가 반드시 다른 결과(discriminating). 둘 다 pass/둘 다 fail 면 hollow.

── classifier semantics note (in-process, subprocess fork 아님) ────────────────
  classify_exit 는 **in-process 함수** — 외부 script fork 아님이므로 distinct-marker
  subsection(interpreter exit-code 우연일치 hazard) 비대상. 함수 반환값(0/1)을 직접 assert
  하므로 interpreter exit-code 충돌 false-positive 위험 원천 부재.

실행:
  standalone  : python3 tests/scripts/test_failover_detection_classifier.py  (exit 0=all pass / 1=any fail)
  pytest      : python3 -m pytest tests/scripts/test_failover_detection_classifier.py -q
"""
import re
import subprocess
import sys
from pathlib import Path

ADR_REL = "archive/adr/ADR-109-in-process-429-mitigation-framework.md"

# ── 파싱 검증 oracle (G1: classifier enum 아님 — 파싱 drift 검출용 상수) ──
# 순서 = ADR-109 (b) fence L294-299 정렬. base 4-tuple + class 2(session/usage limit).
_EXPECTED_ENUM = [
    "rate limit",
    "quota exceeded",
    "429",
    "Server is temporarily limiting",
    "session limit",
    "usage limit",
]


# ══════════════════════════════════════════════════════════════════════════════
# repo-root 탐색 (환경-agnostic — hardcoded 절대경로 금지, CI 이식성)
# ══════════════════════════════════════════════════════════════════════════════
def repo_root() -> Path:
    here = Path(__file__).resolve()
    # tests/scripts/<file> → parents[2] == repo root (roster test `dirname/../..` 동형).
    candidate = here.parents[2]
    if (candidate / ADR_REL).is_file():
        return candidate
    # fallback: git toplevel (worktree 이동/심링크 대비).
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(here.parent),
        )
        if out.returncode == 0:
            g = Path(out.stdout.strip())
            if (g / ADR_REL).is_file():
                return g
    except Exception:
        pass
    return candidate  # best-effort; adr109_text 가 명시 에러로 RED.


def adr109_text() -> str:
    p = repo_root() / ADR_REL
    if not p.is_file():
        raise FileNotFoundError(
            "ADR-109 SSOT not found at %s (repo-root discovery failed)" % p
        )
    return p.read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# markdown section / code-fence 파싱 helper
# ══════════════════════════════════════════════════════════════════════════════
def _section_lines(lines, heading_prefix):
    """heading_prefix 로 시작하는 라인 다음부터 다음 `### `/`## ` heading 직전까지."""
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith(heading_prefix):
            start = i + 1
            break
    if start is None:
        raise ValueError("heading %r not found in ADR-109" % heading_prefix)
    end = len(lines)
    for j in range(start, len(lines)):
        s = lines[j].strip()
        if s.startswith("### ") or s.startswith("## "):
            end = j
            break
    return lines[start:end]


def _first_fenced_block(section_lines):
    """section 안 첫 code-fence(```) 내부 라인들. 언어 annotation fence 도 허용."""
    inside = False
    opened = False
    block = []
    for ln in section_lines:
        if ln.strip().startswith("```"):
            if not inside:
                inside = True
                opened = True
                continue
            break  # 닫는 fence.
        if inside:
            block.append(ln)
    if not opened:
        raise ValueError("no code-fence found in section")
    return block


def parse_detection_enum(text):
    """ADR-109 (b) 절 code-fence 에서 quoted-literal 6개를 파싱(하드코딩 금지, G1)."""
    sec = _section_lines(text.splitlines(), "### (b)")
    block = _first_fenced_block(sec)
    lits = []
    for ln in block:
        m = re.match(r'^"([^"]+)"$', ln.strip())
        if m:
            lits.append(m.group(1))
    return lits


def parse_golden_string(text):
    """ADR-109 (a) 절 code-fence 에서 실관측 golden 문자열(단일 라인)을 파싱(합성 금지)."""
    sec = _section_lines(text.splitlines(), "### (a)")
    block = _first_fenced_block(sec)
    content = [ln.strip() for ln in block if ln.strip()]
    if len(content) != 1:
        raise ValueError(
            "expected exactly 1 golden line in (a) fence, got %d: %r" % (len(content), content)
        )
    return content[0]


# ══════════════════════════════════════════════════════════════════════════════
# AC-4 classifier — ADR-109 §결정1 closed-set literal-substring any-match.
#   반환 = exit-code semantics (0 = GREEN/리밋 감지, 1 = RED/미감지). §9 reproducer 동형.
# ══════════════════════════════════════════════════════════════════════════════
def classify_exit(text, enum):
    return 0 if any(lit in text for lit in enum) else 1


# ── SSOT load (import 시점 — 파싱 실패 = import 실패 = RED, hollow-green 차단) ──
_TEXT = adr109_text()
ENUM = parse_detection_enum(_TEXT)
GOLDEN = parse_golden_string(_TEXT)


# ══════════════════════════════════════════════════════════════════════════════
# 검증 (pytest-native assert — standalone driver 도 동일 함수 호출)
# ══════════════════════════════════════════════════════════════════════════════
def test_parse_sanity_enum():
    """S1 — 파싱 enum 이 예상 6 literal(순서 포함)과 일치. 파싱 drift = RED."""
    assert ENUM == _EXPECTED_ENUM, (
        "ADR-109 (b) fence 파싱 결과가 예상 6 literal 과 불일치: got=%r expected=%r" % (ENUM, _EXPECTED_ENUM)
    )


def test_parse_sanity_golden():
    """S2 — 파싱 golden 이 실관측 property 보유(session limit 有 / usage limit·429 無)."""
    assert GOLDEN.startswith("Agent terminated early"), (
        "golden 파싱 실패 — 실관측 task-notification 형태 아님: %r" % GOLDEN
    )
    assert "session limit" in GOLDEN, "golden 에 discriminating literal 'session limit' 부재: %r" % GOLDEN
    assert "usage limit" not in GOLDEN, "golden 에 'usage limit' 존재 — 무기여 전제 위반: %r" % GOLDEN
    assert "429" not in GOLDEN, "golden 에 '429' 존재 — base-4 미커버 전제 위반: %r" % GOLDEN


def test_ac4_redgreen_deterministic():
    """assertion 1 — base4=RED / base+session=GREEN / full6=GREEN, 각 결정론 재현."""
    base4 = ENUM[:4]
    base5 = ENUM[:5]  # + session limit
    full6 = ENUM[:6]
    # RED: base-only 는 golden 을 놓친다 (결정론 2회).
    r1 = classify_exit(GOLDEN, base4)
    r2 = classify_exit(GOLDEN, base4)
    assert r1 == 1 and r2 == 1, "base-only vs golden 은 exit 1(RED) 이어야 함 (got %d,%d)" % (r1, r2)
    # GREEN: session limit 추가 시 감지 (결정론 2회).
    g1 = classify_exit(GOLDEN, base5)
    g2 = classify_exit(GOLDEN, base5)
    assert g1 == 0 and g2 == 0, "base+session vs golden 은 exit 0(GREEN) 이어야 함 (got %d,%d)" % (g1, g2)
    # full 6 도 GREEN.
    assert classify_exit(GOLDEN, full6) == 0, "full 6-literal vs golden 은 exit 0(GREEN) 이어야 함"
    # discriminating: RED != GREEN (hollow 아님).
    assert r1 != g1, "RED(base4) 와 GREEN(base5) 결과가 동일 — discriminating 실패(hollow)"


def test_ac4_mutation_kill_session_limit():
    """assertion 2 — M1: enum 에서 session limit 제거 → GREEN→RED flip(판별력 실증)."""
    full6 = ENUM[:6]
    mutant = [p for p in full6 if p != "session limit"]
    assert len(mutant) == 5, "mutation 이 정확히 1 literal 제거해야 함 (got %d)" % len(mutant)
    baseline = classify_exit(GOLDEN, full6)
    mutated = classify_exit(GOLDEN, mutant)
    assert baseline == 0, "full 6 baseline 은 GREEN(0) 이어야 함 (got %d)" % baseline
    assert mutated == 1, "session limit 제거 시 golden 은 RED(1) flip 이어야 함 (got %d)" % mutated


def test_ac4_usage_limit_noncontributing():
    """assertion 3 — negative: usage limit 제거해도 verdict = GREEN 불변(무기여)."""
    full6 = ENUM[:6]
    mutant = [p for p in full6 if p != "usage limit"]
    assert len(mutant) == 5, "usage limit 정확히 1개 제거해야 함 (got %d)" % len(mutant)
    baseline = classify_exit(GOLDEN, full6)
    mutated = classify_exit(GOLDEN, mutant)
    assert baseline == 0 and mutated == 0, (
        "usage limit 제거는 verdict 를 바꾸면 안 됨(무기여): baseline=%d mutated=%d" % (baseline, mutated)
    )


def test_ac4_negative_529():
    """assertion 4 — negative: 529 overloaded = 감지집합 NOT-IN(RED) + 429 substring 무충돌."""
    s = "API Error: 529 overloaded"
    verdict = classify_exit(s, ENUM[:6])
    assert verdict == 1, "529 문자열은 6-literal 감지집합에 대해 RED(1) 이어야 함 (got %d)" % verdict
    assert "429" not in s, "'429' literal 이 '529' 문자열에 substring 매칭됨 — 오탐 hazard"


def test_ac4_negative_unclassified():
    """assertion 5 — negative: 리밋 무관 문자열 = 진짜 미분류(RED)."""
    s = "ImportError: no module named foo"
    verdict = classify_exit(s, ENUM[:6])
    assert verdict == 1, "리밋 무관 문자열은 RED(1) 이어야 함 (got %d)" % verdict


# ══════════════════════════════════════════════════════════════════════════════
# standalone driver — 단일 실행으로 전 assertion 검사, PASS/FAIL 출력, exit 0/1
# ══════════════════════════════════════════════════════════════════════════════
_CHECKS = [
    ("S1 parse-sanity-enum (파싱 6 literal == 예상, 순서 포함)", test_parse_sanity_enum),
    ("S2 parse-sanity-golden (실관측 golden property)", test_parse_sanity_golden),
    ("A1 RED->GREEN deterministic (base4=RED / base+session=GREEN / full6=GREEN)", test_ac4_redgreen_deterministic),
    ("A2 M1 mutation-kill (session limit 제거 → GREEN->RED flip)", test_ac4_mutation_kill_session_limit),
    ("A3 negative: usage limit 무기여 (제거해도 GREEN 불변)", test_ac4_usage_limit_noncontributing),
    ("A4 negative: 529 = 감지집합 NOT-IN (RED) + 429 substring 무충돌", test_ac4_negative_529),
    ("A5 negative: 진짜 미분류 (ImportError → RED)", test_ac4_negative_unclassified),
]


def _print_evidence():
    base4, base5, full6 = ENUM[:4], ENUM[:5], ENUM[:6]
    mut_no_session = [p for p in full6 if p != "session limit"]
    mut_no_usage = [p for p in full6 if p != "usage limit"]
    print("── discriminating evidence (classifier exit-code: 0=GREEN 감지 / 1=RED 미감지) ──")
    print("  parsed ENUM (from ADR-109 (b) fence) = %r" % ENUM)
    print("  golden (from ADR-109 (a) fence)       = %r" % GOLDEN)
    print("  base-only (앞4)          vs golden → exit %d (기대 1 RED)" % classify_exit(GOLDEN, base4))
    print("  base+session (앞5)       vs golden → exit %d (기대 0 GREEN)" % classify_exit(GOLDEN, base5))
    print("  full 6                   vs golden → exit %d (기대 0 GREEN)" % classify_exit(GOLDEN, full6))
    print("  M1 mutant (-session)     vs golden → exit %d (기대 1 RED flip)" % classify_exit(GOLDEN, mut_no_session))
    print("  negative mutant(-usage)  vs golden → exit %d (기대 0 GREEN 불변)" % classify_exit(GOLDEN, mut_no_usage))
    print("  full 6      vs '529 overloaded'    → exit %d (기대 1 RED)" % classify_exit("API Error: 529 overloaded", full6))
    print("  full 6      vs 'ImportError...'     → exit %d (기대 1 RED)" % classify_exit("ImportError: no module named foo", full6))
    print("")


def _force_utf8_stdio():
    """Windows cp949 콘솔에서도 UTF-8 출력(golden 의 `·`·arrow·한글) 크래시 방지.
    Linux CI(이미 UTF-8) 에서는 no-op. 파싱/assert 는 stdout 인코딩과 무관."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        reconf = getattr(stream, "reconfigure", None)
        if reconf is not None:
            try:
                reconf(encoding="utf-8", errors="backslashreplace")
            except Exception:
                pass


def main():
    _force_utf8_stdio()
    print("=" * 64)
    print("CFP-2823 AC-4 failover detection classifier — discriminating check")
    print("=" * 64)
    _print_evidence()

    npass = 0
    nfail = 0
    for label, fn in _CHECKS:
        try:
            fn()
            print("PASS: %s" % label)
            npass += 1
        except AssertionError as e:
            print("FAIL: %s" % label)
            print("      %s" % e)
            nfail += 1
        except Exception as e:  # 파싱/환경 오류도 FAIL 로 명시 (silent pass 금지).
            print("FAIL: %s (unexpected error)" % label)
            print("      %s: %s" % (type(e).__name__, e))
            nfail += 1

    print("")
    print("-" * 64)
    print("PASS: %d  FAIL: %d  TOTAL: %d" % (npass, nfail, npass + nfail))
    print("-" * 64)
    if nfail == 0:
        print("OK — 전 assertion 통과 (RED/GREEN discriminating 확증).")
        return 0
    print("NOT OK — %d assertion 실패." % nfail)
    return 1


if __name__ == "__main__":
    sys.exit(main())
