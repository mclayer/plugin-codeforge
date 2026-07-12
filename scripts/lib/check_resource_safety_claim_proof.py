#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_resource_safety_claim_proof.py
CFP-2646 / ADR-082 Amendment 38 §결정 16 — resource-safety claim ↔ proof-link write-time 정직 presence lint
  (write-time self-write verify super-class 의 3번째 presence-lint carrier, warning tier / Layer 2).

대상 = wrapper-self governance/보안 tooling 의 docstring·inline 주석·워크플로 YAML 주석
  (`scripts/**/*.py` + `scripts/check-*.sh` + `.github/workflows/*.yml` + `templates/github-workflows/*.yml`).
안전성-claim(자원 고갈/복잡도/DoS-guard 속성 단정)이 paired proof-reference OR honest-ceiling 문구를
  동반하는지 **presence** 만 검사한다 — claim 의 참됨(truth)은 강제하지 않는다.

★ presence ≠ truth (honesty ceiling — ADR-151 §결정7 상속):
  본 lint 은 claim-without-any-proof-link 를 **작성 시점에 좌향 노출**할 뿐이다. over-claim 을
  "봉인/완전방지" 하지 않는다(그런 hard-claim 부재). 참됨의 execution-backed 반증은 보안테스트 lane 소관.
  granularity = **file-scoped presence**(파일 단위 proof/ceiling 존재) — per-claim proof 아님.
  granularity 상향(claim-adjacent windowed)은 별 named carrier(CFP-2650) 이연. 불완전 proof 는 PASS(상한).

★ 자기참조 DoS 회피 (메타-재귀 — CFP-2635 SF-1 교훈 필수 반영, born-safe 4-axis bound):
  본 lint 도 파일 내용을 스캔한다 = CFP-2635 masking-detect 와 동일 표면. CFP-2635 는 위협 축 enumeration
  에서 algorithmic-complexity(T-2) + line-length(T-3) 축을 누락해 O(n²) DoS(1.5MB 단일라인 >60s)를 품었다.
  본 설계는 그 두 축을 명시 enumerate 하고 4-axis 를 처음부터 bound 한다. 완화는 CPU/메모리 총 작업량
  bound 이지 "임의 입력 무해" 가 아님 (bounded degradation — 정직 천장).
    (T-1) regex backtracking : claim/proof/ceiling 은 리터럴 substring 매칭(regex 최소화). 사용 regex 는
                               anchored + bounded quantifier(`{0,N}`/`\d+`), nested quantifier 0.
                               proof-ref = `tests/scripts/test_*` 회귀가드 경로(self-test PERF-2 실측).
    (T-2) tokenize 복잡도    : claim 검출 = substring `in`(C-level, O(n)) — slice-in-loop 0. index-advance
                               tokenize 는 `check_shell_test_masking.py:235-252` 답습(회귀가드 self-test PERF-2).
    (T-3) 물리라인 length    : MAX_PHYSICAL_LINE_LEN per-physical-line truncate-scan — PER_FILE_SCAN_CAP
                               count-cap 과 별개 축. CFP-2635 SF-1 이 정확히 이 축 부재로 O(n²)(회귀가드 PERF-1).
    (T-4) read-path         : itertools.islice(f, PER_FILE_SCAN_CAP) 로 라인 count bound + per-line truncate.
                               결과 = 총 작업량 <= PER_FILE_SCAN_CAP × MAX_PHYSICAL_LINE_LEN 로 유한 bound.
  이 docstring 자체가 자기 lint 을 통과한다(AC-3 self-application) — 안전성 서술 옆에 proof-reference
  (self-test 회귀가드 경로) + honest-ceiling(bounded degradation, presence ≠ truth) 동반. injection-safe.

3-단계 판정 (라인 단위, O(n)):
  1. claim 검출 (affirmative-context closed-set — `check-tier-honesty.py:8-9,57-58` 긍정-토큰 매칭 답습):
     inline code-span strip 후 `_SAFETY_CLAIM_TOKENS` 리터럴 매칭. 다음은 EXEMPT — 명시 부인
     (denial marker ±1 span: `아님`/`취약`/`not`/`금지`류), closed-set 정의부 라인(`_..._TOKENS = [`),
     remediation guide 문자열. **raw grep 금지**(정직한 부정 서술 미매칭).
  2. paired evidence presence (동일 파일, file-scoped): 비-EXEMPT 라인에 proof-reference(`_PROOF_TOKENS`
     — reproducer/wall-clock 벤치마크/복잡도 회귀 self-test 링크) OR honest-ceiling(`_CEILING_TOKENS` —
     bounded degradation/임의 입력 무해 아님/honesty ceiling/presence≠truth) 존재 여부. `issue-body-claim-
     pre-screen.py:51,54,70` EXEMPT guard + scan cap 구조 답습.
  3. grandfather subtract: (file, claim_token) 가 baseline snapshot(pre-existing legacy)에 있으면 억제
     (new-only). legacy backlog 를 동결, 신규 over-claim 만 surface.

CLI 계약 (ADR-061 house style — 고정, self-test + workflow 소비):
  bash scripts/check-resource-safety-claim-proof.sh [--repo-root DIR] [--baseline PATH]
    → DIR (기본 = 자동 탐지/cwd) 하 in-scope 코퍼스 스캔 (grandfather subtract).
  bash scripts/check-resource-safety-claim-proof.sh --repo-root DIR --files F1 F2 ...
    → 명시 파일만 스캔 (AC-3 self-application — 코퍼스 class 밖 산출물 검증용).
  bash scripts/check-resource-safety-claim-proof.sh --repo-root DIR --write-baseline
    → 현 코퍼스 FLAG 전건을 baseline 으로 동결 write (single writer, 수기 편집 금지).

Exit codes (ADR-060 §결정 5 3-tier — warning tier, fail-open):
  0 = PASS (grandfather 후 new-over-claim 0, 또는 대상 파일 부재 = honest no-op).
  1 = >=1 new-over-claim (warning — workflow continue-on-error 로 PR 미차단, `::warning::` surface).
  2 = usage/parse 오류 (argparse).

ADR refs: ADR-082 Amendment 38 §결정 16 (carrier) / ADR-151 §결정7 (honesty ceiling 상속) /
  ADR-061 §결정1 (Python SSOT + thin wrapper) / ADR-005 (byte-identical workflow pair) /
  ADR-060 §결정5 (warning tier) / ADR-119 (게이트=ground-truth, 오탐 0) / ADR-127 (1 Story = 2 PR).
"""

import argparse
import glob
import itertools
import os
import re
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability 답습).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────── input-driven exhaustion bounded 상수 (T-3/T-4) ─────────
# per-file 물리 라인 스캔 cap (라인 count bound — unbounded 다행 scan 차단, T-4).
PER_FILE_SCAN_CAP = 5000
# per-physical-line 길이 cap (라인 length bound — count cap 과 별개 축, T-3 / CFP-2635 SF-1).
# 단일 물리라인이 arbitrary 길이일 때 라인-길이 의존 경로의 총 작업량을 bound (초과분 truncate-scan).
MAX_PHYSICAL_LINE_LEN = 8192

# 스캔 대상 glob (Story §2.4 in-scope artifact class — non-recursive shell glob).
CORPUS_GLOBS = (
    "scripts/*.py",
    "scripts/lib/*.py",
    "scripts/check-*.sh",
    ".github/workflows/*.yml",
    "templates/github-workflows/*.yml",
)

# self-source EXEMPT (check_shell_test_masking.py SELF_SOURCE 선례): 본 lint 의 self-test 는 의도적
# over-claim fixture 문자열을 담아 meta-reference 오탐 가능 → 파일-단위 EXEMPT (self-test 는 corpus 밖
# tests/scripts 이나 방어적 명시). 본 lint 자기 소스(check_resource_safety_claim_proof.py)는 EXEMPT 아님 —
# 자기 docstring 이 genuine proof-ref/ceiling 동반으로 self-PASS 함을 실증(AC-3, 자기게이트 통과).
_SELF_TEST_TOKENS = ("test_check-resource-safety-claim-proof", "test_check_resource_safety_claim_proof")

# 기본 grandfather baseline 경로 (repo-root 상대).
DEFAULT_BASELINE_REL = "docs/resource-safety-claim-baseline.yaml"

# ─────────────────────── closed-set 데이터 (정의부 = 스캔 EXEMPT) ────────────────
# 안전성-claim closed-set (Story §2.4 6키워드 base 확장). inherently-affirmative phrase 우선 —
# threat-description 문맥(bare `resource exhaustion` 등)은 배제, denial marker 로 추가 EXEMPT.
_SAFETY_CLAIM_TOKENS = (
    "catastrophic backtracking 0",
    "catastrophic backtracking free",
    "catastrophic backtracking 없",
    "ReDoS-safe",
    "ReDoS safe",
    "ReDoS-free",
    "DoS-guard",
    "DoS guard",
    "DoS 가드",
    "injection-safe",
    "nested quantifier 0",
    "nested-quantifier 0",
    "resource exhaustion 방어",
    "resource exhaustion 방지",
    "resource exhaustion safe",
    "resource-exhaustion-safe",
    "총 작업량 bound",
    "총 작업량 을 bound",
    "작업량 bound",
    "scan cap = 총 작업량",
    "scan cap = bound",
    "임의 입력 무해",
)

# proof-reference 문구 (reproducer / wall-clock 벤치마크 / 복잡도 회귀 self-test 링크).
_PROOF_TOKENS = (
    "tests/scripts/",
    "회귀가드",
    "regression guard",
    "wall-clock",
    "wall clock",
    "벤치마크",
    "benchmark",
    "reproducer",
    "PERF-",
    "실측",
    "bounded-time",
    "KB=",
    "MB=",
)

# honest-ceiling 문구 (bounded degradation / 임의 입력 무해 아님 / honesty ceiling / presence ≠ truth).
_CEILING_TOKENS = (
    "bounded degradation",
    "임의 입력 무해 아님",
    "무해 아님",
    "무해가 아님",
    "honesty ceiling",
    "honesty-ceiling",
    "정직 천장",
    "천장",
    "presence ≠ truth",
    "presence != truth",
    "presence≠truth",
    "ADR-151",
)

# denial marker (affirmative-vs-denial 판별축 — §3.2). claim 토큰 라인 ±1 span 에 존재 시 EXEMPT
# (정직한 부인문·경고문은 over-claim 아님).
_DENIAL_MARKERS = (
    "아님",
    "아니다",
    "아니라",
    "않다",
    "않는다",
    "않음",
    "못 ",
    "미강제",
    "금지",
    " not ",
    "무효",
    "없음",
    "취약",
)

# ─────────────────────── inline code-span strip (issue-body-claim-pre-screen 답습) ──

def _strip_inline_code(line):
    """line 내 matched single-backtick span 을 공백 masking (docstring 예시 토큰 오탐 차단).

    좌→우 backtick pairing. 짝 못 찾으면 ambiguous → strip 생략(FP-안전, claim 보존).
    (bash 정밀 파싱 아님 — 불확실하면 검출 보존.)
    """
    if "`" not in line:
        return line
    out = list(line)
    i = 0
    n = len(line)
    while i < n:
        if out[i] == "`":
            j = i + 1
            while j < n and out[j] != "`":
                j += 1
            if j < n:  # matched pair [i..j]
                for k in range(i, j + 1):
                    out[k] = " "
                i = j + 1
                continue
            else:  # unmatched → FP-안전, 남은 부분 보존
                break
        i += 1
    return "".join(out)


# ─────────────────────── 판정 predicate (named helper — testability) ───────────

_DEF_OPEN = re.compile(r"^\s{0,80}_[A-Z][A-Z0-9_]{0,60}\s{0,4}=\s{0,4}[\[\(\{]")


def _bracket_delta(text):
    """열림 `[({` - 닫힘 `])}` (문자열 리터럴 내부 미구분 — 상수 정의 블록은 통상 balanced)."""
    opens = text.count("[") + text.count("(") + text.count("{")
    closes = text.count("]") + text.count(")") + text.count("}")
    return opens - closes


def _compute_definition_mask(texts):
    """closed-set 상수 정의 블록(`_UPPER = [ ... ]` / `_ACTION_GUIDE = ( ... )`) 라인 EXEMPT 마스크.

    definition-block(데이터/정책 열거)은 claim/evidence 판정 대상 아님 (§3.2 정의부 자기열거 EXEMPT).
    """
    mask = [False] * len(texts)
    depth = 0
    for i, t in enumerate(texts):
        if depth == 0:
            if _DEF_OPEN.search(t):
                mask[i] = True
                depth += _bracket_delta(t)
                if depth < 0:
                    depth = 0
        else:
            mask[i] = True
            depth += _bracket_delta(t)
            if depth < 0:
                depth = 0
    return mask


def _detect_claim_token(stripped_line):
    """affirmative safety-claim 토큰 검출 (substring `in` = C-level O(n), T-2 slice-in-loop 0)."""
    for tok in _SAFETY_CLAIM_TOKENS:
        if tok in stripped_line:
            return tok
    return None


def _is_denial_context(texts, idx):
    """claim 라인 ±1 span 에 denial marker 존재 여부 (정직한 부인문/경고문 EXEMPT — §3.2)."""
    for j in (idx - 1, idx, idx + 1):
        if 0 <= j < len(texts):
            if any(m in texts[j] for m in _DENIAL_MARKERS):
                return True
    return False


def _file_has_evidence(nonexempt):
    """비-EXEMPT 라인에 proof-reference OR honest-ceiling 존재 여부 (file-scoped presence, §3.1-2)."""
    for text in nonexempt:
        s = _strip_inline_code(text)
        if any(tok in s for tok in _PROOF_TOKENS):
            return True
        if any(tok in s for tok in _CEILING_TOKENS):
            return True
    return False


# ─────────────────────── 파일 스캔 ──────────────────────────────────────────────

def scan_file(path, rel):
    """단일 파일 스캔 → findings=[(rel, lineno, claim_token, snippet)] (grandfather 前 raw FLAG)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            # read-path bound (T-4): islice(PER_FILE_SCAN_CAP) 라인 count + per-line truncate(T-3).
            physical = []
            for raw in itertools.islice(f, PER_FILE_SCAN_CAP):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN] + "\n"
                physical.append(raw)
    except OSError:
        return []

    texts = [p.rstrip("\n").rstrip("\r") for p in physical]
    exempt = _compute_definition_mask(texts)
    nonexempt = [texts[i] for i in range(len(texts)) if not exempt[i]]
    file_has_evidence = _file_has_evidence(nonexempt)

    claim_hits = []
    for i, ll_text in enumerate(texts):
        if exempt[i]:
            continue
        stripped = _strip_inline_code(ll_text)
        tok = _detect_claim_token(stripped)
        if tok is None:
            continue
        if _is_denial_context(texts, i):
            continue
        lineno = i + 1
        claim_hits.append((lineno, tok, stripped))

    findings = []
    for (lineno, tok, snippet) in claim_hits:
        if not file_has_evidence:
            findings.append((rel, lineno, tok, snippet.strip()[:140]))
    return findings


def scan_corpus(repo_root, explicit_files=None):
    """explicit_files 지정 시 그 파일만, 아니면 CORPUS_GLOBS 매칭 파일 스캔. → (scanned, findings)."""
    if explicit_files:
        files = [os.path.abspath(p) for p in explicit_files]
    else:
        files = []
        for pattern in CORPUS_GLOBS:
            files.extend(glob.glob(os.path.join(repo_root, *pattern.split("/"))))
        files = sorted(set(files))

    all_findings = []
    scanned = 0
    for path in files:
        if not os.path.isfile(path):
            continue
        rel = os.path.relpath(path, repo_root).replace(os.sep, "/")
        if any(tok in rel for tok in _SELF_TEST_TOKENS):
            continue  # self-test EXEMPT — 의도적 over-claim fixture 문자열(meta-reference)
        scanned += 1
        for (r, ln, tok, snip) in scan_file(path, rel):
            all_findings.append((r, ln, tok, snip))
    return scanned, all_findings


# ─────────────────────── grandfather baseline (new-only subtract) ────────────────

_BASELINE_FILE_RE = re.compile(r"^\s*-?\s*file:\s*[\"']?([^\"'\n]+?)[\"']?\s*$")
_BASELINE_TOKEN_RE = re.compile(r"^\s*claim_token:\s*[\"']?(.+?)[\"']?\s*$")


def load_baseline(path):
    """grandfather baseline 을 (file, claim_token) 집합으로 로드 (dependency-free 라인 파서).

    부재/malformed → 빈 집합 (subtract 0, honest — consumer 상속 시 spurious 억제 미발생).
    """
    keys = set()
    if not os.path.isfile(path):
        return keys
    cur_file = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, 100000):
                m = _BASELINE_FILE_RE.match(raw)
                if m:
                    cur_file = m.group(1).strip()
                    continue
                m = _BASELINE_TOKEN_RE.match(raw)
                if m and cur_file is not None:
                    keys.add((cur_file, m.group(1).strip()))
    except OSError:
        return set()
    return keys


def subtract_baseline(findings, baseline_keys):
    """FLAG (rel, tok) 가 baseline 에 있으면 억제 (new-only). → (new_findings, grandfathered_count)."""
    new = []
    gf = 0
    for (rel, ln, tok, snip) in findings:
        if (rel, tok) in baseline_keys:
            gf += 1
        else:
            new.append((rel, ln, tok, snip))
    return new, gf


def write_baseline(path, findings):
    """현 코퍼스 FLAG 전건을 (file, claim_token) baseline 으로 동결 write (single writer, canonical LF)."""
    pairs = sorted({(rel, tok) for (rel, _ln, tok, _snip) in findings})
    lines = [
        "# docs/resource-safety-claim-baseline.yaml — GENERATED by "
        "scripts/lib/check_resource_safety_claim_proof.py --write-baseline (CFP-2646)",
        "# DO NOT EDIT BY HAND. Regenerate: bash scripts/check-resource-safety-claim-proof.sh "
        "--repo-root . --write-baseline",
        "# grandfather = 승격 시점 legacy over-claim(file, claim_token) 동결 → new-only subtract "
        "(ADR-060 §결정6 Clean-as-You-Code). new 안전성-claim 은 proof-ref/ceiling 동반 의무.",
        "schema_version: '1.0'",
        "generated_by: CFP-2646",
        "basis: ADR-082 Amendment 38 §결정 16 승격 시점 in-scope 코퍼스 over-claim(file, claim_token) 동결",
        "grandfathered_claims:",
    ]
    if not pairs:
        lines.append("[]")  # 빈 baseline 시 flow-empty (no-op subtract)
        body = "\n".join(lines[:-1]) + " []\n"
    else:
        for (rel, tok) in pairs:
            lines.append("- file: %s" % rel)
            lines.append("  claim_token: %s" % tok)
            lines.append("  reason: pre-existing (CFP-2646 baseline snapshot grandfather)")
        body = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return len(pairs)


# ─────────────────────── 출력 (warning surface) ─────────────────────────────────

_ACTION_GUIDE = (
    "[resource-safety-claim-proof-presence] warning-tier (ADR-082 Amendment 38 §결정 16 — "
    "PR merge 미차단, advisory):\n"
    "  검출 = 안전성-claim(catastrophic backtracking 0 / ReDoS-safe / DoS 가드 / nested quantifier 0 / "
    "scan cap = bound 류)이\n"
    "    동일 파일에 proof-reference(reproducer / wall-clock 벤치마크 / 복잡도 회귀 self-test 링크 "
    "tests/scripts/...) 도,\n"
    "    honest-ceiling(bounded degradation, 임의 입력 무해 아님) 도 동반하지 않음.\n"
    "  remediation 3택: (1) paired proof-reference 부착 / (2) honest-ceiling 로 downgrade / "
    "(3) 부인문(denial)으로 정직 재서술.\n"
    "  또는 hotfix-bypass:resource-safety-claim-proof-presence label + audit comment.\n"
    "  honesty ceiling(ADR-151 §결정7): presence 만 검사 — claim 의 참됨(truth) 미강제, file-scoped "
    "granularity(불완전 proof 는 PASS).\n"
    "  presence ≠ truth. bounded degradation. '완전 봉인' 아님(참됨 반증은 보안테스트 lane 소관)."
)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_resource_safety_claim_proof.py",
        description="governance/보안 tooling resource-safety claim ↔ proof-link presence lint (warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="스캔 루트 (기본 = scripts/lib 기준 자동 탐지).")
    parser.add_argument("--baseline", default=None, help="grandfather baseline 경로 override.")
    parser.add_argument("--files", nargs="*", default=None, help="명시 파일만 스캔 (AC-3 self-application).")
    parser.add_argument("--write-baseline", action="store_true", help="현 코퍼스 FLAG 를 baseline 으로 동결.")
    parser.add_argument("repo_root_pos", nargs="?", default=None, help=argparse.SUPPRESS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root or args.repo_root_pos
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)
    baseline_path = args.baseline or os.path.join(repo_root, DEFAULT_BASELINE_REL)

    # ── --write-baseline: 코퍼스 FLAG 전건 동결 (subtract 없이) ──
    if args.write_baseline:
        scanned, findings = scan_corpus(repo_root)
        n = write_baseline(baseline_path, findings)
        print(
            "check-resource-safety-claim-proof: baseline written %s — %d (file, claim_token) frozen "
            "over %d file" % (baseline_path, n, scanned)
        )
        return 0

    scanned, raw_findings = scan_corpus(repo_root, explicit_files=args.files)

    if scanned == 0:
        print("check-resource-safety-claim-proof: PASS — 대상 코퍼스 부재 (honest no-op, warning tier)")
        return 0

    baseline_keys = load_baseline(baseline_path)
    findings, grandfathered = subtract_baseline(raw_findings, baseline_keys)

    for (rel, ln, tok, snip) in findings:
        print(
            '::warning::check-resource-safety-claim-proof: FLAG — over-claim (proof-ref/ceiling 부재) '
            'claim="%s" %s:%d snippet="%s"' % (tok, rel, ln, snip)
        )

    if findings:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-resource-safety-claim-proof: FLAG %d new-over-claim over %d file "
            "(grandfathered=%d) — warning tier (continue-on-error 로 비차단, advisory only)"
            % (len(findings), scanned, grandfathered)
        )
        return 1

    print(
        "check-resource-safety-claim-proof: PASS — FLAG 0 new-over-claim over %d file "
        "(grandfathered=%d, presence proof 위반 0, warning tier)" % (scanned, grandfathered)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
