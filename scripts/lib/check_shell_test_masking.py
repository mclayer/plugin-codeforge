#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_shell_test_masking.py
CFP-2635 / ADR-060 Amendment 22 (20번째 warning-tier entry) — shell-test exit-masking
  + mock-seam-무assert false-coverage 정적 lint (Layer 2).

대상 = codeforge 거버넌스 shell self-test 코퍼스 (`scripts/test-*.sh` 33 + `tests/scripts/*.sh` 37
  = 70 file). "bats" 문자 매칭 아님 (codeforge 는 bats 미사용 — Story §2.3 재편). raw `cmd || true`
  exit-masking + mock-seam env export 후 동반 assertion 부재 = false-coverage 를 정적 스캔한다.

★ anti-hollow-gate 1급 요건 (Story §4.2 / §7.3):
  naive `|| true` grep = 코퍼스 149행 대부분 오탐 → lint 자체가 hollow/noisy gate(자기모순,
  ADR-119 위반). 정당한 `|| true` 를 오탐 0 으로 제외하는 것이 설계의 1급 난제. 이를 위해:
    (1) logical-line 재구성 (backslash-continuation join) — 정밀도 keystone.
    (2) LEGIT 제외 규칙 (a) counter-backup / (b) arithmetic / (c) redirect-capture /
        (d) branch-guard + heredoc/comment 제외.
    (3) 그 외 bare `raw_cmd || true` 는 block-scope companion(하류 카운터/assert) 부재 시에만
        MASKING flag (§3.1 "하류 카운터/assertion 부재" 의 line-block-local 실현).

honesty ceiling (ADR-151 §결정7 상속 — Story §7.5):
  본 게이트는 **naive/구조적 masking 패턴만** 검출 (bare `|| true` on raw command + mock-seam
  export-무-in-scope-companion). 검출력(surviving test 가 실제 mutation 을 죽이는가)은 **미강제**
  (G3/review/QADev discriminating-case 소관). "false-coverage 완전 봉인" hard-claim 금지 —
  presence/형식 천장. false-negative(먼 assert 를 둔 masking) = 라인-블록-국소 스캔 한계 (정직 인정).

input-driven resource exhaustion safety (SecurityArch — Story §7 / Change Plan §3.3; CFP-2635 FIX SF-1):
  유일 보안-인접 vector = input-driven resource exhaustion (ReDoS = 한 subtype, DR-2635-1 명명 확장).
  완화는 아래 4 축을 모두 bound 한다. (SF-1 이전 판은 regex-backtracking 축만 커버했고 algorithmic/
  length 축은 미bound 여서 O(n²) DoS 가 실재했다 — 1.5MB 단일라인 >60s, firsthand 반증 후 정정.)
    (1) regex backtracking : 전 regex anchored + bounded quantifier(`\d+`/`{0,N}`, nested quantifier 0).
    (2) 물리라인 length    : MAX_PHYSICAL_LINE_LEN(8192) per-line truncate-scan — 라인-길이 의존
                             경로(tokenize/regex)의 총 작업량을 bound (정당 shell 코드는 미도달).
    (3) tokenize 복잡도    : _leading_token = offset-advance(index 전진, slice 재복사 0) = O(n)
                             — slice-in-loop O(n²) 제거 (prior-art check_spawn_prompt_fact_verify.py
                             index-advance 답습, DR-2635-3: `orchestrator_` 접두 없음).
    (4) read-path         : itertools.islice(f, PER_FILE_SCAN_CAP) 로 라인 count bound + per-line truncate.
  결과 = 총 작업량 <= PER_FILE_SCAN_CAP × MAX_PHYSICAL_LINE_LEN 로 유한 bound. catastrophic backtracking 0.
  정직 천장: 본 완화는 CPU/메모리 총 작업량 bound 이지 "임의 입력 무해" 가 아님 (bounded degradation).

CLI 계약 (ADR-061 house style — 고정, self-test + workflow 소비):
  bash scripts/check-shell-test-masking.sh [--repo-root DIR]
    → DIR (기본 = 자동 탐지/cwd) 하 코퍼스 스캔. glob = scripts/test-*.sh + tests/scripts/*.sh.

Exit codes (ADR-060 §결정 5 3-tier — warning tier, fail-open):
  0 = PASS (위반 0, 또는 대상 파일 부재 = honest no-op).
  1 = ≥1 masking/mock-seam 위반 (warning — workflow continue-on-error 로 PR 미차단, `::warning::` surface).
  2 = usage/parse 오류 (argparse).

remediation (T3 / DR-2635-2 — 비표준 helper 오탐 시 3택):
  ① 정당 helper 를 assert-family enum 접두(assert_/expect_/check_/require_/verify_/test_/run_)로 명명
     하거나 파일 내 function 으로 정의 (본 lint 은 파일-정의 function 호출도 counter-backup 인정).
  ② `hotfix-bypass:shell-test-exit-masking-detect` label + audit comment.
  ③ 정당 예외 라인에 redirect/capture(`2>/dev/null` / `VAR=$(...)`) 또는 근접 assertion 배치.

ADR refs: ADR-060 Amendment 22 (carrier, warning tier) / ADR-151 §결정7 (honesty ceiling 상속) /
  ADR-061 §결정1 (Python SSOT + thin wrapper) / ADR-005 (byte-identical workflow pair) /
  ADR-119 (게이트=ground-truth, 오탐 0 = proxy 오단정 차단) / ADR-127 (1 Story = 2 PR).
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

# ─────────────────────── input-driven exhaustion bounded 상수 ───────────────────
# per-file 물리 라인 스캔 cap (라인 count bound — unbounded 다행 scan 차단).
# 코퍼스 최대 파일 ~600행 실측 → 5000 = 넉넉한 상한 (의도적 truncation 아님, DoS 가드).
PER_FILE_SCAN_CAP = 5000
# per-physical-line 길이 cap (라인 length bound — count cap 과 별개 축, CFP-2635 FIX SF-1/DR-2635-1).
# 단일 물리라인이 arbitrary 길이일 때 라인-길이 의존 경로(tokenize/regex)의 총 작업량을 bound.
# 코퍼스 실측 라인 최대 수백 자 → 8192 = 넉넉한 상한 (초과분 truncate-scan, 정당 코드는 미도달).
MAX_PHYSICAL_LINE_LEN = 8192
# 논리 라인 backslash-continuation join 상한 (병리적 continuation chain 방어).
MAX_CONTINUATION_JOIN = 40
# masking candidate → block-scope companion 전방 탐색 window (논리 라인 수, bounded).
COMPANION_FORWARD_WINDOW = 14

# 스캔 대상 glob (Story §5.3 / Change Plan §3.0 — bats·Python·JS out-of-scope).
# 비-recursive shell glob → scripts/test-fixtures/** 하위 비-self-test 자산 자연 제외
# (git-pathspec `scripts/test-*.sh` 는 재귀 매칭으로 test-fixtures/ 내 fixture 1건 over-count).
CORPUS_GLOBS = ("scripts/test-*.sh", "tests/scripts/*.sh")

# self-source EXEMPT (check_spawn_prompt_fact_verify.py SELF_SOURCE 선례):
# 본 lint 자기 self-test(tests/scripts/test_check-shell-test-masking.sh)는 의도적 masking-shaped
# fixture 문자열을 담는다 — 스캔 시 expected meta-reference 오탐이므로 파일-단위 EXEMPT.
_SELF_SOURCE_TOKENS = ("shell-test-masking", "shell_test_masking")

# ─────────────────────── anchored 리터럴 패턴 (전부 bounded, ReDoS-free) ─────────
# `|| true` 존재 (리터럴 앵커 — nested quantifier 0).
_OR_TRUE = re.compile(r"\|\|\s{0,4}true\b")
# assert-family / test-runner 접두 enum (leading command token) — DR-2635-2 enum 확장:
# design §3.1 (a) 원 enum (assert_/expect_/check_/require_/verify_) + 실코퍼스 지배 counter-backup
# invocation (test_ 테스트-러너 / run_ 러너-헬퍼) 흡수 (70-file precision proof 완결성 강제).
_ASSERT_FAMILY = re.compile(
    r"^(?:assert_|expect_|check_|require_|verify_|test_|run_)[A-Za-z0-9_]{0,60}"
)
# 산술 idiom `((...)) || true` (bash 산술 0 → non-zero 반환 관용).
_ARITH = re.compile(r"\(\([^()]{0,120}\)\)\s{0,4}\|\|\s{0,4}true\b")
# 분기 guard 시작 토큰.
_BRANCH_HEAD = re.compile(r"^(?:if|elif|while|until)\s")
# `; then` / `; do` 분리 (분기 guard 판정 — || true 가 그 이전인가).
_THEN_DO = re.compile(r";\s{0,4}(?:then|do)\b")
# 조건부 대입 idiom `&& VAR=... || true` (cmd 성공 시 대입, || true 는 short-circuit guard).
_COND_ASSIGN = re.compile(r"&&\s{1,4}[A-Za-z_][A-Za-z0-9_]{0,60}=")
# value-pipeline (best-effort 값 추출) `| grep/wc/sort/head/tail/cut/sed/awk/uniq`.
_VALUE_PIPE = re.compile(r"\|\s{0,4}(?:grep|wc|sort|head|tail|cut|sed|awk|uniq)\b")
# 값-캡처 대입 `VAR=$(` (command substitution assignment).
_CAPTURE_ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,60}=\S{0,20}\$\(")
# 파일-정의 function 헤더 `foo() {` (counter-backup helper 식별).
_FUNC_DEF = re.compile(r"^([A-Za-z_][A-Za-z0-9_]{0,60})\s{0,4}\(\)\s{0,4}\{?")
# FAIL 카운터 corroborate 패턴 (`FAIL=$((FAIL...` / `FAIL_COUNT=$((`).
_FAIL_COUNTER = re.compile(r"\bFAIL(?:_COUNT)?=\$\(\(\s{0,2}FAIL")
# heredoc opener (`<<'EOF'` / `<<EOF` / `<<-EOF` / `<< "EOF"`).
_HEREDOC_OPEN = re.compile(r"<<-?\s{0,2}[\"']?([A-Za-z_][A-Za-z0-9_]{0,60})[\"']?")
# mock-seam env 토큰 (codeforge `_CFP*_MOCK*` 명명 규약, AS-5). export 또는 statement-head 대입.
_MOCK_SEAM = re.compile(
    r"^(?:export\s{1,4})?[A-Za-z_][A-Za-z0-9_]{0,60}_?MOCK[A-Za-z0-9_]{0,60}\s{0,4}="
)
# companion 신호 (하류 카운터/assert — 하나라도 있으면 exit 가 유일 oracle 아님).
_COMPANION_SIGNALS = (
    _FAIL_COUNTER,
    re.compile(r"\bPASS(?:_COUNT)?=\$\(\("),
    re.compile(r"^(?:assert_|expect_|check_|require_|verify_)[A-Za-z0-9_]{0,60}"),
    re.compile(r"\[\[?[^]]{0,200}\]\]?"),               # [ ... ] / [[ ... ]] test
    re.compile(r"\bgrep\s+-[A-Za-z]{0,4}q"),            # fail-gating grep -q
    re.compile(r"(?:PASS|FAIL|✓|✗|OK PASS|X FAIL)\b"),  # stdout sentinel
)


# ─────────────────────── logical-line 재구성 (정밀도 keystone) ──────────────────

class LogicalLine:
    __slots__ = ("lineno", "text", "in_heredoc")

    def __init__(self, lineno, text, in_heredoc):
        self.lineno = lineno          # 1-based 시작 물리 라인 번호
        self.text = text              # join + inline-comment strip 후 텍스트
        self.in_heredoc = in_heredoc  # heredoc body 여부 (스캔 제외)


def _strip_inline_comment(text):
    """따옴표 밖 첫 ` #` (공백+#) 이후를 제거 — inline 주석 내 `|| true` 오탐 차단.

    단순·안전 파서: single/double quote 상태 추적, 따옴표 밖에서 공백 뒤 `#` 를 주석 개시로 간주.
    (bash 정밀 파싱 아님 — FP-안전 방향: 불확실하면 보존하지 않고 주석 절단, 코드 축은 유지.)
    """
    in_s = in_d = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "'" and not in_d:
            in_s = not in_s
        elif c == '"' and not in_s:
            in_d = not in_d
        elif c == "#" and not in_s and not in_d and (i == 0 or text[i - 1].isspace()):
            return text[:i].rstrip()
        i += 1
    return text


def build_logical_lines(physical_lines):
    """물리 라인 → 논리 라인 재구성.

    - backslash-continuation(`\\` EOL) join → 다중행 assert 의 head token 보존 (TC-L2 keystone).
    - heredoc body 추적 → in_heredoc 마킹 (스캔 제외, TC-L6).
    - 선두 `#` 주석 라인 = 논리 라인이되 이후 `|| true` 매칭 시 무시 (leading '#' → skip).
    - inline 주석 strip.
    """
    result = []
    heredoc_delim = None
    buf = None
    buf_start = None
    join_count = 0

    for idx, raw in enumerate(physical_lines[:PER_FILE_SCAN_CAP], start=1):
        line = raw.rstrip("\n").rstrip("\r")

        # heredoc body 내부: 그대로 in_heredoc 라인으로 방출 (join 대상 아님).
        if heredoc_delim is not None:
            if line.strip() == heredoc_delim:
                heredoc_delim = None  # terminator 라인은 body 아님
            else:
                result.append(LogicalLine(idx, line, True))
                continue

        # continuation join 진행 중이 아니면 heredoc opener 검사 (join 중엔 opener 무시 — 단순화).
        if buf is None:
            m = _HEREDOC_OPEN.search(line)
            if m and not line.lstrip().startswith("#"):
                # heredoc 개시 라인 자체는 정상 논리 라인으로 방출 후 body 진입.
                result.append(LogicalLine(idx, _strip_inline_comment(line), False))
                heredoc_delim = m.group(1)
                continue

        # backslash-continuation join.
        if buf is None:
            buf = line
            buf_start = idx
            join_count = 0
        else:
            buf = buf + " " + line.strip()
            join_count += 1

        if buf.rstrip().endswith("\\") and join_count < MAX_CONTINUATION_JOIN:
            buf = buf.rstrip()[:-1]  # trailing backslash 제거 후 계속 join
            continue

        # 논리 라인 확정.
        result.append(LogicalLine(buf_start, _strip_inline_comment(buf), False))
        buf = None

    if buf is not None:
        result.append(LogicalLine(buf_start, _strip_inline_comment(buf), False))

    return result


# ─────────────────────── 분류 predicate (named helper — §3.0 ModuleArch testability) ──

# 선두 env-var 대입 prefix (`VAR=val `) — leading token 탐색 시 offset-advance 로 skip.
_ENV_ASSIGN_PREFIX = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,60}=\S{0,80}\s+(?=\S)")
_FIRST_TOKEN = re.compile(r"\S+")


def _leading_token(text):
    """논리 라인 선두 command token (env-prefix 대입 skip 후 첫 실 command).

    offset-advance(인덱스 전진)로 선두 env-var 대입(`VAR=val cmd`)을 skip — 문자열 재slice 0 → O(n).
    (구판 slice-in-loop `t = t[m.end():]` = O(n²) input-driven DoS, CFP-2635 SF-1/DR-2635-1 —
    prior-art check_spawn_prompt_fact_verify.py 의 index-advance 답습으로 제거. .match(t, pos) 는
    pos 위치에 anchored 매치라 slice 와 semantically 동일하되 재복사 없음.)
    """
    t = text.strip()
    pos = 0
    n = len(t)
    while pos < n:
        m = _ENV_ASSIGN_PREFIX.match(t, pos)
        if not m:
            break
        pos = m.end()
    m = _FIRST_TOKEN.match(t, pos)
    return m.group(0) if m else ""


def _is_comment_line(text):
    return text.lstrip().startswith("#")


def _is_counter_backup(text, defined_funcs, file_has_fail_counter):
    """(a) counter-backup — assert-family enum 접두 OR 파일-정의 function 호출 + FAIL 카운터 corroborate."""
    if not file_has_fail_counter:
        return False
    tok = _leading_token(text)
    if not tok:
        return False
    if _ASSERT_FAMILY.match(tok):
        return True
    # 파일-정의 function 호출 (예: run_test / 임의 helper) — 비표준 helper 명명 흡수 (T3 remediation).
    bare = tok.split("(")[0]
    return bare in defined_funcs


def _is_arithmetic(text):
    """(b) arithmetic `((...)) || true` idiom OR 선두 토큰이 `((` 산술."""
    if _ARITH.search(text):
        return True
    return text.lstrip().startswith("((")


def _is_redirect_capture(text):
    """(c) redirect-capture — /dev/null redirect / 2>&1 merge / VAR=$() capture / value-pipe."""
    if "/dev/null" in text:
        return True
    if "2>&1" in text:
        return True
    if "=$(" in text or _CAPTURE_ASSIGN.search(text):
        return True
    if _VALUE_PIPE.search(text):
        return True
    # `$(...)` 내부 || true (capture 종결 continuation) — 닫는 paren 동반.
    stripped = text.strip()
    if "$(" in stripped and stripped.rstrip().endswith(")"):
        return True
    if stripped.endswith(") || true") or ") ||" in stripped:
        # `... ) || true` = command-substitution 종결 or subshell 종결.
        if "$(" in stripped or stripped.startswith("(") or stripped.lstrip().startswith(")"):
            return True
    return False


def _is_branch_guard(text):
    """(d) branch-guard — if/elif/while/until 헤드 + || true 가 ; then/; do 이전, OR cond-assign."""
    if _COND_ASSIGN.search(text):
        return True
    stripped = text.strip()
    if _BRANCH_HEAD.match(stripped):
        m = _THEN_DO.search(stripped)
        pre = stripped[: m.start()] if m else stripped
        if _OR_TRUE.search(pre):
            return True
    return False


def _has_block_companion(logical_lines, start_idx):
    """masking candidate 전방 window 내 companion(하류 카운터/assert) 존재 여부.

    §3.1 "하류 카운터/assertion 부재" 의 line-block-local 실현. companion 有 → exit 가 유일
    oracle 아님(setup/side-effect) → LEGIT. window bounded (ReDoS-free). function-def 경계에서 중단.
    """
    end = min(len(logical_lines), start_idx + 1 + COMPANION_FORWARD_WINDOW)
    for j in range(start_idx + 1, end):
        ll = logical_lines[j]
        if ll.in_heredoc:
            continue
        txt = ll.text
        if not txt.strip():
            continue
        # 새 function 정의 경계 도달 → block 이탈, 중단.
        if _FUNC_DEF.match(txt.strip()) and start_idx + 1 != j:
            break
        for pat in _COMPANION_SIGNALS:
            if pat.search(txt):
                return True
    return False


# ─────────────────────── 파일 스캔 ──────────────────────────────────────────────

def _collect_defined_functions(logical_lines):
    funcs = set()
    for ll in logical_lines:
        if ll.in_heredoc:
            continue
        m = _FUNC_DEF.match(ll.text.strip())
        if m:
            funcs.add(m.group(1))
    return funcs


def scan_file(path, rel):
    """단일 파일 스캔 → (masking_findings, mockseam_findings). findings = (lineno, category, snippet)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            # read-path bound (CFP-2635 SF-1/DR-2635-1 — input-driven exhaustion 완화):
            #   라인 count = islice(PER_FILE_SCAN_CAP) → 병리적 다행 파일의 read/CPU 를 bound
            #     (구판 readlines() 는 전체 로드 후 slice — cap 前 unbounded read).
            #   라인 length = MAX_PHYSICAL_LINE_LEN truncate-scan → 단일 장문라인 총 작업량 bound.
            #     초과분 truncate 후 라인경계 보존 위해 "\n" 재부착 (full_text join / logical-line 정합).
            physical = []
            for raw in itertools.islice(f, PER_FILE_SCAN_CAP):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN] + "\n"
                physical.append(raw)
    except OSError:
        return [], []

    full_text = "".join(physical)
    file_has_fail_counter = bool(_FAIL_COUNTER.search(full_text))
    logical = build_logical_lines(physical)
    defined_funcs = _collect_defined_functions(logical)

    masking = []
    mockseam = []

    for i, ll in enumerate(logical):
        if ll.in_heredoc:
            continue
        text = ll.text
        if _is_comment_line(text):
            continue

        # ── (A) exit-masking 축 ──
        if _OR_TRUE.search(text):
            legit = (
                _is_counter_backup(text, defined_funcs, file_has_fail_counter)
                or _is_arithmetic(text)
                or _is_redirect_capture(text)
                or _is_branch_guard(text)
            )
            if not legit and not _has_block_companion(logical, i):
                masking.append((ll.lineno, "exit-masking", text.strip()[:140]))

        # ── (B) mock-seam-무assert 축 ──
        if _MOCK_SEAM.match(text.strip()):
            # command-prefix env 대입(`VAR=val cmd ...`)은 seam toggle 아님 — 뒤에 command 동반.
            head = text.strip()
            # `export X=1` / `X=1` 형태 (대입 후 command 없음) 만 seam toggle 로 간주.
            after_eq = head.split("=", 1)[1] if "=" in head else ""
            is_prefix_env = bool(re.match(r"^\S{0,80}\s+\S", after_eq.strip()))
            if not is_prefix_env and not _has_block_companion(logical, i):
                mockseam.append((ll.lineno, "mock-seam-no-assert", head[:140]))

    return masking, mockseam


def scan_corpus(repo_root):
    files = []
    for pattern in CORPUS_GLOBS:
        files.extend(glob.glob(os.path.join(repo_root, *pattern.split("/"))))
    files = sorted(set(files))

    all_masking = []
    all_mockseam = []
    scanned = 0
    for path in files:
        rel = os.path.relpath(path, repo_root).replace(os.sep, "/")
        if any(tok in rel for tok in _SELF_SOURCE_TOKENS):
            continue  # self-source EXEMPT — 자기 fixture 문자열 masking-shaped (meta-reference)
        scanned += 1
        m, s = scan_file(path, rel)
        for (ln, cat, snip) in m:
            all_masking.append((rel, ln, cat, snip))
        for (ln, cat, snip) in s:
            all_mockseam.append((rel, ln, cat, snip))
    return scanned, all_masking, all_mockseam


# ─────────────────────── 출력 (warning surface) ─────────────────────────────────

_ACTION_GUIDE = (
    "[shell-test-exit-masking-detect] warning-tier (ADR-060 Amendment 22 — PR merge 미차단, advisory):\n"
    "  exit-masking : raw `cmd || true` 로 exit 를 가려 항상 PASS 하는 test 라인 (하류 카운터/assert 부재).\n"
    "  mock-seam    : mock env export 후 동일 block 내 동반 assertion 부재 = enforcement 0 false-coverage.\n"
    "  remediation 3택: ① 정당 assert helper 명명(assert_/test_/run_ 접두 또는 파일-정의 function)\n"
    "    + FAIL 카운터 백업 / redirect·capture(`2>/dev/null`·`VAR=$(...)`) / 근접 assertion.\n"
    "    ② hotfix-bypass:shell-test-exit-masking-detect label + audit comment.\n"
    "  honesty ceiling(ADR-151 §결정7): naive/구조적 패턴만 검출 — 검출력(G3)·먼 assert masking 미강제.\n"
    "  '완전 봉인' 아님 (presence/형식 천장, false-negative 정직 인정)."
)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_shell_test_masking.py",
        description="codeforge shell self-test 코퍼스 exit-masking + mock-seam-무assert 정적 lint (warning tier).",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="스캔 루트 (기본 = scripts/lib 기준 자동 탐지, 없으면 cwd).",
    )
    # positional repo-root 도 관용 허용 (self-test/디버그 편의 — CLI 계약 초과 아님, 동일 의미).
    parser.add_argument("repo_root_pos", nargs="?", default=None, help=argparse.SUPPRESS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root or args.repo_root_pos
    if repo_root is None:
        # scripts/lib/check_shell_test_masking.py → repo root = 2 단계 상위.
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)

    scanned, masking, mockseam = scan_corpus(repo_root)

    if scanned == 0:
        # honest no-op — 대상 파일 부재 (consumer 상속 시 corpus 부재 = spurious RED 미발생).
        print("check-shell-test-masking: PASS — 대상 shell 코퍼스 부재 (honest no-op, warning tier)")
        return 0

    findings = masking + mockseam
    for (rel, ln, cat, snip) in findings:
        print(
            '::warning::check-shell-test-masking: FLAG — category=%s %s:%d snippet="%s"'
            % (cat, rel, ln, snip)
        )

    if findings:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-shell-test-masking: FLAG %d (masking=%d mock-seam=%d) over %d file — "
            "warning tier (continue-on-error 로 비차단, advisory only)"
            % (len(findings), len(masking), len(mockseam), scanned)
        )
        return 1

    print(
        "check-shell-test-masking: PASS — FLAG 0 over %d file "
        "(`|| true` precision proof 위반 0, warning tier)" % scanned
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
