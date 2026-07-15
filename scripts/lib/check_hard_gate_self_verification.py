#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_hard_gate_self_verification.py
CFP-2684 / ADR-154 — hard-gate self-verification 메타-게이트 pure core.

super-class "게이트 green ≠ 검출 보증"(hard-gate self-verification)을 도메인 불변식으로 강제한다.
신규 hard gate 가 self-verification 번들(positive-control self-test + empty-target/unknown-input
fail-closed + execution-trace + internal-control identity-probe + honest-ceiling 선언 + silent-green≠
silent-fallback≠honest-degrade 3-way taxonomy)을 갖췄는지 **정적 presence/shape** 로 fail-closed
검사한다. `scripts/lib/check_selftest_execution_liveness.py`(ADR-151 메타-게이트) house style 답습
(offline-first / read-only / argparse / pathlib). subject disjoint(ADR-151 = self-test 코퍼스 execution
채널 alive / 본 게이트 = 임의 hard-gate self-test 의 검출-integrity 번들 presence).

━━ 정직 천장 (honest-ceiling, ADR-154 §결정4 / INV-5 P0 불가침) ━━
  본 메타-게이트는 다음 까지만 강제한다: presence / shape / format / fail-closed. **강제 안 함(정직
  공개)**: 검출 sufficiency(대표 결함류 실제 kill = L3)는 원리상 undecidable(equivalent-mutant =
  halting 동치 + oracle problem) → review-tier(AC-9) + honest-ceiling. **presence ≠ truth** — green 은
  "번들이 형식상 존재"이지 "결함을 실제 죽인다"가 아니다. "universal detection 완전 봉인" framing 은
  하지 않는다(그런 hard-claim 부재 = 검사연극·위양성, ADR-119 §결정6). game-able residual 정직 공개:
  (a) AC-2 2-exit shape 는 tautological same-path(inline hand-copy 위장)에 완전 봉인 불가,
  (b) AC-13 열거 완결성은 self-declared 의존이라 미선언 게이트 semantic 재분류 불가 — 둘 다 review-tier
  cross-ref(AC-9) + tautology-smell grep loop-closure(ADR-082 §11.A).

━━ SCOPE disjoint (ADR-154 §결과 경계) ━━
  ⊥ L3 detection-power(검출 sufficiency, review-tier) / ⊥ ADR-151(self-test 채널 alive = execution-
  liveness) / ⊥ ADR-060(검사 등급/승격) / ⊥ runtime soak(G2)/DAST(G5)/real-render(§8.7).

━━ input-driven resource-safety (SecurityArch §7 — CFP-2635/2646 born-safe 4-axis REUSE, 신규 방어 아님) ━━
  유일 보안-인접 vector = repo-local 파일 body(untrusted) parse. 완화는 아래를 모두 bound 한다:
    (1) regex backtracking : 전 regex anchored + bounded quantifier(`{0,N}`, nested/lazy quantifier 0).
                             claim/probe/taxonomy 매칭은 리터럴 substring `in`(C-level, O(n)) 우선.
    (2) 물리라인 length    : MAX_PHYSICAL_LINE_LEN(8192) per-physical-line truncate-scan.
    (3) read-path          : itertools.islice(f, PER_FILE_SCAN_CAP) 라인 count bound + per-line truncate.
    (4) T-TRAVERSE(유일 신규 가드): subject/concept-doc open 시 (repo_root/rel).resolve() 후
                             is_relative_to(repo_root) — escape/symlink-out → fail-closed reject.
  결과 = 총 작업량 <= PER_FILE_SCAN_CAP × MAX_PHYSICAL_LINE_LEN 로 유한 bound, nested quantifier 0.
  proof-ref: tests/scripts/test_check-hard-gate-self-verification.sh (PERF DoS 회귀가드 — 실측 wall-clock).
  정직 천장: 본 완화는 CPU/메모리 총 작업량 bound 이지 "임의 입력 무해"가 아니다 (bounded degradation,
  presence ≠ truth, ADR-151 §결정7 상속). 무증거 안전-claim 금지 — 위 서술은 self-test 회귀가드 동반.

━━ §7.7 self-parse 비대칭 (both — 혼동 금지) ━━
  (1) content-scan 자기 self-source EXEMPT(`_SELF_SOURCE_TOKENS`): 메타-게이트 자기 self-test 파일이
      의도적 mutant fixture 를 담으므로 subject 발견에서 제외(FP 회피).
  (2) inventory enrollment(ADR-151 인벤토리 1행) = disjoint 채널 — selftest-execution-liveness 소관.
  두 표면은 disjoint (스캔 제외 ≠ 인벤토리 등재). conflate 금지.

━━ mutation-kill sentinel (QADev sed mutation 대상 표식 — M1~M6) ━━
  각 fail-closed 분기에 `# MUTATION-SENTINEL Mn` 주석 배치. self-test(tests/scripts/...)가 real gate copy
  에 sed 로 해당 분기를 제거해 positive-leak(`KILLED ⟺ original(kill-fixture)=exit1 AND mutated=exit0`)
  를 실증. M6(2-exit shape→string-scan degrade)이 axis-ii FN seal.

CLI 계약 (고정 — QADev self-test + workflow 소비; 임의 변경 금지 — fixture 는 이 계약에 맞춰 build):
  python3 check_hard_gate_self_verification.py [--repo-root DIR]
    --repo-root  (optional) repo 루트 (기본 = __file__ parents[2]). 모든 검사는 이 DIR 상대.
                 subject 발견 = <DIR>/tests/scripts/*.sh 중 inline enrollment marker
                 ('hard-gate-self-verification: enrolled' | 'hgsv-enroll') 보유 파일.
                 concept-doc = <DIR>/docs/domain-knowledge/concept/hard-gate-self-verification.md.

Exit codes (fail-closed):
  0 = 전 fail-closed AC 통과 (enrolled 0 = honest-degrade no-op 포함 — concept-doc AC-6/8/12 은 항시 검사).
  1 = ≥1 fail-closed 위반 OR unknown/unreadable input (fail-closed).
  2 = usage/parse 오류 (argparse) 전용.

관측 계약 (RTM §8.2.1 — 어느 AC 를 어느 검사가 관측하는가):
  AC-1  positive-control presence           → _check_subject (M1)
  AC-2  2-exit-differ SHAPE                  → _has_two_exit_shape (M6, structural — NOT string-scan)
  AC-3  empty-target honest-degrade / unparseable fail-closed → run() enrolled==0 emit + _discover_subjects
  AC-4  unknown-input fail-closed            → run() repo-root 검증 (M3) + _discover_subjects unreadable
  AC-5  execution-trace emit                 → run() (M4)
  AC-6  concept-doc 3-way taxonomy presence  → _check_concept_doc (M2)
  AC-7  self-application (self-test+inventory row) = 본 .py core self-scan 아님 (QADev/inventory 소관)
  AC-8  honest-ceiling presence + over-claim → _check_concept_doc
  AC-9  검출 sufficiency (review-tier)        = 기계강제 아님 (SKILL checklist, honest-ceiling)
  AC-12 named cross-ref no-dup               → _check_concept_doc
  AC-13 self-declared identity_bearing probe → _check_subject (M5)

ADR refs: ADR-154 (결정 SSOT — super-class/3-way taxonomy/2-control/honest-ceiling) /
  ADR-151 (execution-liveness 인벤토리 REUSE + honest-ceiling §결정7 상속) / ADR-152 (discriminating-A/B) /
  ADR-082 §11.A (red-green-stash-proof REUSE) / ADR-061 §결정1 (Python entry + thin bash wrapper) /
  ADR-119 (게이트=ground-truth, honest-ceiling) / ADR-060 (warning-tier 등록).
"""

import argparse
import itertools
import re
import sys
from pathlib import Path

# 출력 인코딩 robust 화 (Windows cp949 등 비-UTF-8 locale 에서 한글·기호 print 차단 — ADR-061 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

EXIT_PASS = 0  # 전 fail-closed AC 통과
EXIT_FAIL = 1  # ≥1 위반 OR unknown/unreadable input (fail-closed)
# EXIT 2 = argparse usage 전용.

# ── input-driven exhaustion bound (CFP-2635/2646 born-safe REUSE — 신규 방어 아님) ──
PER_FILE_SCAN_CAP = 5000          # per-file 라인 count bound (islice)
MAX_PHYSICAL_LINE_LEN = 8192      # per-physical-line length bound (truncate-scan)

# ── enrollment marker (subject opt-in — self-declared, 결정론적 selector) ──────────
_ENROLL_MARKERS = ("hard-gate-self-verification: enrolled", "hgsv-enroll")

# ── self-source EXEMPT (§7.7(1) — 자기 self-test 의도적 mutant fixture FP 회피) ──────
_SELF_SOURCE_TOKENS = ("hard-gate-self-verification", "hard_gate_self_verification")

# ── concept-doc conventional path (repo-root 상대) ────────────────────────────────
_CONCEPT_DOC_REL = "docs/domain-knowledge/concept/hard-gate-self-verification.md"

# ── AC-1 positive-control anchor (subject 가 결정적 mutant→RED 를 상시 증명) ─────────
_POSITIVE_CONTROL_ANCHORS = (
    "positive-control", "positive control", "sanity mutant", "mutant→RED", "mutant->RED",
)

# ── AC-2 2-exit-differ SHAPE (structural — 순수 string-scan 아님; anchored bounded) ──
# exit-capture site (`rc=$?` / `status=$?`) — ≥2 = 두 outcome 관측.
_EXIT_CAPTURE_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,40}=\$\?")
# clean expectation (exit 0 기대) — bash test/arith 앵커.
_CLEAN_EXPECT_RE = re.compile(r"-eq\s{1,4}0\b|==\s{0,4}0\b")
# mutant expectation (non-zero / 1 기대).
_MUTANT_EXPECT_RE = re.compile(r"-ne\s{1,4}0\b|-eq\s{1,4}1\b|!=\s{0,4}0\b|==\s{0,4}1\b")

# ── AC-13 identity-probe (self-declared selector + probe presence) ────────────────
_IDENTITY_BEARING_DECL = ("identity_bearing: true", "identity_bearing:true", "identity-bearing: true")
_PROBE_ANCHORS = (
    "internal-control", "identity-probe", "원문대조", "resolved-target",
    "unknown-input negative", "known-answer",
)

# ── AC-6 3-way taxonomy + honest-degrade 예외 (concept doc) ───────────────────────
_TAXONOMY_TOKENS = ("silent-green", "silent-fallback", "honest-degrade")
_HONEST_DEGRADE_EXCEPTION = ("결함 아님",)

# ── AC-8 honest-ceiling presence + over-claim (concept doc) ───────────────────────
_CEILING_TOKENS = ("undecidable", "정직 천장", "honest-ceiling", "honest ceiling")
_PRESENCE_TRUTH_TOKENS = ("presence ≠ truth", "presence != truth", "presence≠truth")
_OVERCLAIM_TOKENS = ("완전 봉인", "universal detection")
_DENIAL_MARKERS = ("아님", "아니다", "않", "없", "금지", "못", " not ", "불가")

# ── AC-12 named cross-ref (≥6) + 신규 정의 3영역 + 재codify 금지 (concept doc) ───────
_NAMED_CONCEPTS = (
    "red-green-stash-proof", "vacuous-pass", "execution-liveness",
    "discriminating-fixture", "discriminating-A/B", "mutation-hollow-gate", "honest-degrade",
)
_NEW_DEF_AREAS = ("super-class", "taxonomy", "identity-probe")
_NAMED_CROSSREF_MIN = 6


def _error(ac_id, msg):
    """위반 1건을 stderr 에 AC-id prefix + 1행 출력 (fail-closed 계약)."""
    print(f"::error::[{ac_id}] {msg}", file=sys.stderr)


# ── adapter: bounded read + T-TRAVERSE ────────────────────────────────────────────
def _safe_resolve(repo_root, rel):
    """(repo_root/rel).resolve() 후 repo_root 내부 여부 검사 (T-TRAVERSE — escape/symlink-out reject).

    repo_root 는 이미 resolve() 됨. 반환 = 안전 Path 또는 None(escape).
    """
    target = (repo_root / rel).resolve()
    try:
        if not target.is_relative_to(repo_root):
            return None
    except AttributeError:  # <3.9 fallback (실 런타임 3.12 — 방어적)
        try:
            target.relative_to(repo_root)
        except ValueError:
            return None
    return target


def _read_lines(path):
    """bounded read → 라인 리스트 (islice count-cap + per-line length truncate). OSError → None."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            out = []
            for raw in itertools.islice(f, PER_FILE_SCAN_CAP):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN] + "\n"
                out.append(raw.rstrip("\n").rstrip("\r"))
            return out
    except OSError:
        return None


def _is_denial_context(lines, idx):
    """over-claim 라인 ±1 span 에 denial marker 존재 여부 (정직한 부인문 EXEMPT)."""
    for j in (idx - 1, idx, idx + 1):
        if 0 <= j < len(lines):
            if any(m in lines[j] for m in _DENIAL_MARKERS):
                return True
    return False


# ── per-subject 검사 (AC-1 / AC-2 / AC-13) ────────────────────────────────────────
def _has_two_exit_shape(lines):
    """AC-2 2-exit-differ SHAPE (structural): ≥2 exit-capture + clean(exit0) + mutant(non-zero) 기대.

    순수 string-scan 아님 — 실제 두 outcome capture(`X=$?` ≥2)를 관측하고 clean/mutant 양 기대를
    구조로 요구한다. string-scan 으로 degrade(예: 'exit 0'/'exit 1' substring 만 확인)하면 shape-부재
    fixture 가 FN 으로 새므로 M6 self-test 가 RED (axis-ii FN seal).
    """
    captures = 0
    clean = False
    mutant = False
    for ln in lines:
        if _EXIT_CAPTURE_RE.search(ln):
            captures += 1
        if _CLEAN_EXPECT_RE.search(ln):
            clean = True
        if _MUTANT_EXPECT_RE.search(ln):
            mutant = True
    return captures >= 2 and clean and mutant


def _check_subject(violations, rel, lines):
    """1 enrolled subject 의 self-verification 번들 presence/shape 검사 (AC-1/2/13)."""
    text = "\n".join(lines)

    # AC-1 positive-control presence.
    # MUTATION-SENTINEL M1: positive-control presence 분기.
    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):
        _error("AC-1", f"{rel}: positive-control self-test anchor 부재 "
                        f"(positive-control / sanity mutant / mutant→RED 中 1+ 필요).")
        violations.append(1)

    # AC-2 2-exit-differ SHAPE.
    # MUTATION-SENTINEL M6: 2-exit-differ SHAPE (structural, NOT string-scan degrade).
    if not _has_two_exit_shape(lines):
        _error("AC-2", f"{rel}: 2-exit-differ shape 부재 — ≥2 exit-capture(X=$?) + clean(-eq 0) + "
                       f"mutant(-ne 0 / -eq 1) 구조 필요 (clean GREEN ≠ mutant RED 관측·비교).")
        violations.append(1)

    # AC-13 identity-probe (self-declared selector — 미선언=미대상 정직 no-op).
    # MUTATION-SENTINEL M5: identity_bearing self-declared → internal-control probe presence.
    if any(d in text for d in _IDENTITY_BEARING_DECL):
        if not any(a in text for a in _PROBE_ANCHORS):
            _error("AC-13", f"{rel}: identity_bearing: true 선언이나 internal-control probe anchor 부재 "
                            f"(원문대조 / resolved-target / unknown-input negative / known-answer 中 1+ 필요).")
            violations.append(1)


# ── 전역 검사: concept-doc (AC-6 / AC-8 / AC-12) ──────────────────────────────────
def _detect_overclaim(lines):
    """over-claim(완전 봉인 / universal detection)이 denial 문맥 없이 등장하는 첫 라인 (AC-8 / INV-5)."""
    for i, ln in enumerate(lines):
        for oc in _OVERCLAIM_TOKENS:
            if oc in ln and not _is_denial_context(lines, i):
                return (i + 1, oc)
    return None


def _detect_recodify(lines):
    """기존 named 개념이 정의-대입 shape(`^ [*|`] concept [*|`] (=|:=|란) `)로 등장 = 재codify (AC-12).

    cross-ref only 계약 위반. anchored + bounded quantifier (ReDoS-safe).
    """
    for concept in _NAMED_CONCEPTS:
        pat = re.compile(
            r"^\s{0,8}(?:[-*]\s{0,3})?\*{0,2}`?"
            + re.escape(concept)
            + r"`?\*{0,2}\s{0,4}(?::=|=|란\s)"
        )
        for ln in lines:
            if pat.match(ln):
                return concept
    return None


def _check_concept_doc(violations, repo_root):
    """concept doc 3-way taxonomy(AC-6) + honest-ceiling(AC-8) + named cross-ref no-dup(AC-12).

    concept doc 부재/읽기불가 → fail-closed (판정불가는 silent-pass 아님). 전 run 마다 검사(honest
    no-op 이라도 메타-게이트 자기 governance 산출물은 항시 verify — vacuous green 방지).
    """
    safe = _safe_resolve(repo_root, _CONCEPT_DOC_REL)
    if safe is None:
        _error("T-TRAVERSE", f"{_CONCEPT_DOC_REL}: repo-root escape/symlink-out — fail-closed reject.")
        violations.append(1)
        return
    if not safe.is_file():
        _error("AC-6", f"{_CONCEPT_DOC_REL}: concept doc 부재 — 3-way taxonomy/ceiling/cross-ref 판정불가, fail-closed.")
        violations.append(1)
        return
    lines = _read_lines(safe)
    if lines is None:
        _error("AC-6", f"{_CONCEPT_DOC_REL}: concept doc 읽기 불가 — fail-closed (silent skip 금지).")
        violations.append(1)
        return
    text = "\n".join(lines)

    # AC-6 — 3-way taxonomy 3 토큰 + honest-degrade 예외.
    missing_tax = [t for t in _TAXONOMY_TOKENS if t not in text]
    if missing_tax:
        _error("AC-6", f"{_CONCEPT_DOC_REL}: 3-way taxonomy 토큰 부재 {missing_tax} "
                       f"(silent-green ≠ silent-fallback ≠ honest-degrade).")
        violations.append(1)
    # MUTATION-SENTINEL M2: honest-degrade 예외('결함 아님') presence — empty-target 침묵 GREEN 방어 축.
    if not any(e in text for e in _HONEST_DEGRADE_EXCEPTION):
        _error("AC-6", f"{_CONCEPT_DOC_REL}: honest-degrade 예외('결함 아님') 명시 부재 "
                       f"(honest-degrade 오탐 방지 codify 누락 = silent-fallback 방어 불완전).")
        violations.append(1)

    # AC-8 — honest-ceiling presence + over-claim 부재.
    if not any(c in text for c in _CEILING_TOKENS):
        _error("AC-8", f"{_CONCEPT_DOC_REL}: honest-ceiling 문구 부재 (undecidable / 정직 천장 / honest-ceiling).")
        violations.append(1)
    if not any(p in text for p in _PRESENCE_TRUTH_TOKENS):
        _error("AC-8", f"{_CONCEPT_DOC_REL}: 'presence ≠ truth' 문구 부재 (검출 sufficiency 미보증 정직 공개 누락).")
        violations.append(1)
    oc = _detect_overclaim(lines)
    if oc is not None:
        _error("AC-8", f"{_CONCEPT_DOC_REL}:{oc[0]}: over-claim '{oc[1]}' denial 문맥 없이 등장 "
                       f"(INV-5 위반 — 'universal detection 완전 봉인' hard-claim 금지).")
        violations.append(1)

    # AC-12 — named cross-ref ≥6 + 신규 정의 3영역 + 재codify 금지.
    present_named = [n for n in _NAMED_CONCEPTS if n in text]
    if len(present_named) < _NAMED_CROSSREF_MIN:
        _error("AC-12", f"{_CONCEPT_DOC_REL}: named 개념 cross-ref {len(present_named)} < {_NAMED_CROSSREF_MIN} "
                        f"(present={present_named}).")
        violations.append(1)
    missing_area = [a for a in _NEW_DEF_AREAS if a not in text]
    if missing_area:
        _error("AC-12", f"{_CONCEPT_DOC_REL}: 신규 정의 3영역 토큰 부재 {missing_area} "
                        f"(super-class 명명 / silent-fallback taxonomy / identity-probe).")
        violations.append(1)
    rec = _detect_recodify(lines)
    if rec is not None:
        _error("AC-12", f"{_CONCEPT_DOC_REL}: 기존 named 개념 '{rec}' 재codify(정의-대입 shape) — "
                        f"cross-ref only 위반(중복 정의 금지).")
        violations.append(1)


# ── enrollment (subject 발견) ─────────────────────────────────────────────────────
def _is_enrolled(lines):
    text = "\n".join(lines)
    return any(marker in text for marker in _ENROLL_MARKERS)


def _discover_subjects(violations, repo_root):
    """<repo>/tests/scripts/*.sh 중 enrollment marker 보유 파일 = subject. self-source EXEMPT.

    unreadable(OSError) subject-candidate = AC-4 fail-closed (silent skip 금지, `2>/dev/null` masking 금지).
    반환 = [(rel, lines)].
    """
    subjects = []
    tests_dir = repo_root / "tests" / "scripts"
    if not tests_dir.is_dir():
        return subjects  # tests/scripts 부재 = enrolled 0 (후속 honest-degrade no-op)
    for p in sorted(tests_dir.glob("*.sh")):
        rel = f"tests/scripts/{p.name}"
        if any(tok in rel for tok in _SELF_SOURCE_TOKENS):
            continue  # §7.7(1) self-source EXEMPT
        safe = _safe_resolve(repo_root, rel)
        if safe is None:
            _error("T-TRAVERSE", f"{rel}: repo-root escape/symlink-out — fail-closed reject.")
            violations.append(1)
            continue
        lines = _read_lines(safe)
        if lines is None:
            # MUTATION-SENTINEL M3(공유): unknown/unreadable input → fail-closed (default 실행/skip 금지).
            _error("AC-4", f"{rel}: 파일 읽기 불가(unreadable/unparseable) — fail-closed exit1 (silent skip 금지).")
            violations.append(1)
            continue
        if _is_enrolled(lines):
            subjects.append((rel, lines))
    return subjects


# ── 오케스트레이션 ────────────────────────────────────────────────────────────────
def run(repo_root_arg):
    root = Path(repo_root_arg)
    # MUTATION-SENTINEL M3: unknown-input fail-closed (repo-root 미존재/비-dir → exit1, silent-fallback 금지).
    if not root.exists() or not root.is_dir():
        _error("AC-4", f"--repo-root '{repo_root_arg}' 미존재/비-디렉터리 — unknown-input fail-closed exit1 "
                       f"(default 실행 = silent-fallback 금지).")
        return EXIT_FAIL
    repo_root = root.resolve()

    violations = []
    _check_concept_doc(violations, repo_root)  # AC-6 / AC-8 / AC-12 (전 run 검사)
    subjects = _discover_subjects(violations, repo_root)  # AC-4 unreadable fail-closed
    for rel, lines in subjects:
        _check_subject(violations, rel, lines)  # AC-1 / AC-2 / AC-13

    enrolled = len(subjects)

    if violations:
        _error("SUMMARY", f"hard-gate self-verification 메타-게이트 FAIL — 위반 {len(violations)}건 "
                          f"(fail-closed, exit1). 천장: presence/shape/format/fail-closed 까지만 — "
                          f"검출 sufficiency=undecidable(review-tier, AC-9). presence ≠ truth "
                          f"(ADR-154 §결정4 honest-ceiling, '완전 봉인' hard-claim 부재).")
        return EXIT_FAIL

    # AC-5 execution-trace emit + AC-3 empty-target honest-degrade 선언.
    # MUTATION-SENTINEL M4: execution-trace / honest-degrade 선언 emit (count-emission).
    if enrolled == 0:
        print("✓ check-hard-gate-self-verification: honest-degrade — enrolled=0 subject "
              "(opt-in marker 부재), honest no-op. concept-doc/taxonomy/ceiling/cross-ref(AC-6/8/12) verified. "
              "presence/shape 천장 — 검출 sufficiency=undecidable (review-tier, AC-9). presence ≠ truth.")
    else:
        print(f"✓ check-hard-gate-self-verification: enrolled={enrolled} subject scanned "
              f"(AC-1/2/13 presence/shape) + concept-doc AC-6/8/12 통과. "
              f"presence/shape 천장 — 검출 sufficiency=undecidable (review-tier, AC-9). presence ≠ truth.")
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_hard_gate_self_verification.py",
        description=(
            "hard-gate self-verification 메타-게이트 (정적 lint, presence/shape fail-closed). "
            "신규 hard gate 의 self-verification 번들 presence/shape 강제 — 검출 sufficiency=undecidable "
            "(review-tier honest-ceiling, ADR-154). presence ≠ truth."
        ),
    )
    default_root = Path(__file__).resolve().parents[2]  # scripts/lib → scripts → repo-root
    parser.add_argument(
        "--repo-root", default=str(default_root),
        help="repo 루트 (기본 = __file__ parents[2]). concept-doc·subject(tests/scripts/*.sh) 발견 기준.",
    )
    args = parser.parse_args(argv)
    return run(args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
