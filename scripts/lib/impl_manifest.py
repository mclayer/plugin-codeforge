#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# scripts/lib/impl_manifest.py — Story §8.7 Impl Manifest **기계 생성·대조**
#
# ── 계기 (구현리뷰 iter5 F-CR5-01, 3회차 발현) ──────────────────────────────────────
#   §8.7 은 `git diff --stat` 총계 · 파일별 행수 · 테스트 수집 수 · 스위트 결과를
#   **수기 사본**으로 들고 있었다. 커밋이 하나 얹힐 때마다 사본은 stale 이 되고,
#   같은 절이 *"manifest 는 Story 의 마지막 커밋 이후 갱신한다"* 는 **행위 규율**을
#   명문화한 다음 라운드에 그 규율을 깼다(iter3 F-A → iter5 F-CR5-01).
#   ⇒ 처방은 규율 강화가 아니라 **사본 폐기**다: 수치는 기계가 생성하고, 기재와
#     불일치하면 **테스트가 RED** 가 된다.
#
# ── 축 3개 ────────────────────────────────────────────────────────────────────────
#   generate_manifest()      : git + pytest 실측 → dict            (impure)
#   parse_manifest_section() : Story §8.7 텍스트 → 선언 dict        (pure)
#   compare_manifest()       : 두 dict 대조 → 위반 목록            (pure)
#
# ── 정직 천장 (ADR-119) ───────────────────────────────────────────────────────────
#   · 본 모듈은 "선언이 실측과 같은가" 까지만 판정한다. §8.7 의 **서술**(역할 설명·
#     정직 천장 문단)이 옳은지는 판정하지 않는다 — 그 축은 리뷰 소관이다.
#   · 스위트 **실행 결과**(passed 수)는 기본 경로에서 실행하지 않는다. 대신
#     "Story 가 전건 통과를 선언하므로 declared **passed + skipped** == 수집 선택 수"
#     라는 **파생 불변식**으로 잰다(§compare ③-b). skip 은 deselected 와 달리
#     selected 에 **포함**되므로 skip 0 을 가정하면 정직한 skip-포함 선언이 구조적
#     위반이 된다 — 그 가정은 FIX6-b 에서 제거했다. 실 실행 대조가 필요하면
#     `generate --with-suite` 로 실행 축까지 채운다.
#   · 스위트를 **실 실행**하는 경로(`--with-suite`)는 pytest 의 **종료코드**와 실패-계열
#     토큰(`failed`/`error`)을 함께 읽는다. 둘 중 하나라도 비면 실패가 산출에서 조용히
#     사라진다 — FIX14 이전 판이 그 상태였고, rc=1 인 실행이 초록 줄로 기록됐다.
#     단 이 층이 세우는 것은 "실패가 **기록**된다" 까지다. 그 실패가 무엇 때문인지,
#     스위트가 옳은 것을 재는지는 판정하지 않는다.
#   · 스위트 줄이 **있는데 파서가 못 읽는** 경우(canonical 형식 이탈)는 무결이 아니라
#     **위반**이다(§compare ①). 단 canonical 이 아닌 shape 전부를 잡는다고 주장하지
#     않는다 — 탐지 정의역은 `_SUITE_SPANLIKE_RE` 주석에 명시했다.
#   · Story 파일은 **다른 repo**(codeforge-internal-docs)에 있다. 따라서 CI 에서
#     live 대조는 Story 경로가 주입될 때만 성립한다 — 그 조건부성은 아래
#     `resolve_story_path()` 의 계약이며 은폐하지 않는다.

import argparse
import os
import re
import subprocess
import sys

MANIFEST_VERSION = "impl-manifest v1"

# Story §8.7 절 헤딩 (번호 표기는 Story 관례를 따른다 — `§` 없이 `8.7`)
SECTION_HEADING = "### 8.7 Impl Manifest"

# Story 경로 주입 키 (하드코딩 금지 — 인자 > env 순)
ENV_STORY_FILE = "CFP2949_STORY_FILE"

# CI 인자 목록의 SSOT — 파일 목록을 **workflow 에서 읽는다**(제2의 수기 사본 금지).
WORKFLOW_REL = ".github/workflows/cfp2949-scheduled-task-test.yml"
CI_MARK_EXPR = "not requires_golden"

_WORKFLOW_TEST_RE = re.compile(r"(tests/[A-Za-z0-9_./-]+\.py)")

# ── §8.7 선언 리터럴 정규식 ──────────────────────────────────────────────────────
_TOTALS_RE = re.compile(
    r"\*\*(\d+)\s+files?\s+changed,\s*(\d+)\s+insertions?\(\+\),\s*(\d+)\s+deletions?\(-\)\*\*"
)
_COLLECT_HEAD_RE = re.compile(r"(\d+)\s*파일\s*\*\*(\d+)\s*건\*\*")
_COLLECT_SELECT_RE = re.compile(r"\*\*선택\s*(\d+)\s*/\s*deselected\s*(\d+)\*\*")
# 스위트 결과 선언 — **canonical 형식** = 생성기(`render_markdown`) 산출과 동형:
#   `N passed[, M skipped], K deselected`
# `skipped` 슬롯은 optional 이다(미기재 = 0) — 기존 2-슬롯 선언 **하위호환**.
# ★ 슬롯이 필요한 이유(FIX6-b 계기): `CFP2949_STORY_FILE` **미주입**(= wrapper CI 기본)
#   실행은 live 대조 층이 자기 정의역 밖을 선언하며 skip 하므로 스위트 결과가
#   `N passed, 1 skipped, K deselected` 형상이 된다. 슬롯이 없으면 그 형상을 파서가
#   **조용히 건너뛰고**, §8.7 에 stale 한 skip-포함 선언을 적어도 위반이 0 이 된다.
_SUITE_RE = re.compile(
    r"`(\d+)\s+passed(?:,\s*(\d+)\s+skipped)?,\s*(\d+)\s+deselected`"
)
# **미인식 탐지**용 느슨한 형태 — "스위트 줄처럼 생겼는데 canonical 이 아닌" span.
#   정의역 = 한 백틱 span 안에 `숫자+passed` 와 `deselected` 가 함께 있는 것.
#   ★ 이 정의역이 필요한 이유: 구판은 **미인식**과 **부재**가 같은 경로였다(둘 다
#     `suite_passed` 키 부재 → 비교 skip → 무결 통과). 아래 span 이 잡히는데 위
#     canonical 이 안 잡히면 그 자체를 위반으로 올린다.
#   ★ 정직 천장 — 정의역 밖 2종은 여전히 산문으로 남는다:
#     (a) `deselected` 토큰이 없는 결과 줄(예: `83 passed, 1 failed` — 동결 스냅샷의
#         **이력 서술**이 실물이다). (b) `passed` 단어 자체가 없는 표기(예: `113 통과`).
#     canonical 이 아닌 shape 전체를 잡는다고 주장하지 않는다.
_SUITE_SPANLIKE_RE = re.compile(r"`([^`\n]*?\d+\s*passed[^`\n]*?deselected[^`\n]*)`")
# 표 행: 첫 셀 백틱 경로 + 마지막 셀 어딘가의 `NNN행`
_ROW_PATH_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")
_ROW_LINES_RE = re.compile(r"\((\d+)\s*행")
# 수집 별칭 토큰: `ac_matrix 21` / `unit 30`
_ALIAS_RE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s+(\d+)")

# pytest 수집 요약 줄
_COLLECT_PLAIN_RE = re.compile(r"^(\d+)\s+tests?\s+collected")
_COLLECT_DESEL_RE = re.compile(r"^(\d+)/(\d+)\s+tests?\s+collected\s*\((\d+)\s+deselected\)")
# ── pytest **실행** 요약 줄 (생성 축 — 위 §8.7 **선언** 축 정규식과 별개다) ──────
#   ★ FIX14 계기 (실물 재현, 합성 아님): 구판은
#       `(\d+)\s+passed(?:,\s*(\d+)\s+skipped)?(?:,\s*(\d+)\s+deselected)?`
#     하나를 `search` 했고, `cp.returncode` 는 어디서도 보지 않았다. pytest 는 실패가
#     섞이면
#         `1 failed, 163 passed, 1 skipped, 1 deselected in 471.16s (0:07:51)`
#     를 내는데 `search` 는 선두 `1 failed,` 를 건너뛰고 `163 passed` 부터 잡는다.
#     ⇒ rc=1 인 실행에서 생성기가 `163 passed, 1 skipped, 1 deselected` 라는 **초록 줄**을
#       뱉었다. 수기 사본을 없애려고 만든 이 장치가 자기 산출에서 실패를 삼킨 형상이다.
#       동결 자료 = `tests/fixtures/cfp_2949/pytest-failing-run-tail.txt` (그 실행의 꼬리).
#   ⇒ 슬롯 열거 대신 outcome 토큰을 **화이트리스트로 전량 수확**한다. 열거식은 pytest 가
#     토큰을 하나 늘릴 때마다 조용히 눈이 머는 반면, 화이트리스트 밖 토큰은
#     `parse_suite_summary` 가 **미인식으로 올린다**(미인식 ≠ 무결 — 이 모듈의 기존 규율).
_SUITE_KNOWN_OUTCOMES = (
    "passed", "failed", "error", "errors", "skipped", "deselected",
    "xfailed", "xpassed", "warning", "warnings", "rerun", "reruns",
)
_SUITE_RESULT_RE = re.compile(
    r"(\d+)\s+(%s)\b" % "|".join(sorted(_SUITE_KNOWN_OUTCOMES, key=len, reverse=True))
)
# 요약 줄 **형상** — `N word[, N word]*[ in <초>s ...]`. 줄 전체를 앵커해 트레이스백이
#   잡히지 않게 한다: 실물 fixture 의 `... timed out after 60 seconds` 줄이 그 반례다
#   (토큰만 훑으면 `60 seconds` 를 요약으로 오인할 여지가 생긴다).
_SUITE_SUMMARY_LINE_RE = re.compile(
    r"^\d+\s+[A-Za-z][A-Za-z-]*(?:\s*,\s*\d+\s+[A-Za-z][A-Za-z-]*)*"
    r"(?:\s+in\s+[\d.]+s.*)?$"
)
# 줄 안의 `N word` 토큰 전량 (화이트리스트 판정 전 단계)
_SUITE_TOKEN_RE = re.compile(r"(\d+)\s+([A-Za-z][A-Za-z-]*)")
# 요약 줄 꼬리의 소요시간 절 — 토큰 수확 정의역에서 잘라낸다
_SUITE_ELAPSED_RE = re.compile(r"\s+in\s+[\d.]+s")
# `selected` 정의역에 계상되는 **실행** outcome.
#   `deselected` 는 selected 밖이고, `error` 는 setup/teardown 에서 같은 항목이 겹쳐
#   셀 수 있어 항등에서 뺀다 — 겹침을 항등에 넣으면 정직한 실행이 구조적 위반이 된다.
#   error 가 누락되는 것이 아니다: 비-green 판정(`compare_manifest` ⓪)이 따로 잡는다.
_SUITE_RUN_OUTCOMES = ("passed", "failed", "skipped", "xfailed", "xpassed")


# ═══════════════════════════ 공통 ═══════════════════════════════════════════════
def repo_root_from(start=None):
    """이 모듈 위치 기준 repo 루트 (scripts/lib/ 의 두 단계 위)."""
    if start:
        return os.path.abspath(start)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def resolve_story_path(cli_value=None, env=None):
    """Story 파일 경로 해소 — **인자 > env** 순. 하드코딩 경로 fallback **없음**.

    Story(§8.7 보유 문서)는 별 repo(codeforge-internal-docs)에 있으므로 wrapper CI 에는
    존재하지 않는다. 미주입 = `None` 을 돌려주고, 호출자가 그 사실을 **명시적으로**
    다루게 한다(조용한 통과 금지)."""
    env = os.environ if env is None else env
    val = cli_value or env.get(ENV_STORY_FILE) or ""
    val = val.strip()
    if not val:
        return None
    return os.path.abspath(os.path.expanduser(val))


def ci_test_files(repo_root=None):
    """CI 인자 목록을 **workflow 에서** 읽는다 (등장 순 유지, 중복 제거).

    ★ 이 목록을 파이썬 상수로 복제하면 §8.7 수기 사본과 **같은 종류의** 두 번째
      사본이 생긴다. workflow 가 실제로 도는 인자이므로 그것이 SSOT 다."""
    root = repo_root_from(repo_root)
    path = os.path.join(root, WORKFLOW_REL)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    out = []
    for m in _WORKFLOW_TEST_RE.finditer(text):
        p = m.group(1)
        if p not in out:
            out.append(p)
    return out


def alias_of(path):
    """CI 파일 경로 → 별칭 후보 (기계 유도, 수기 표 0).

    `tests/integration/test_scheduled_task_ac_matrix.py` → `ac_matrix`
    `tests/unit/test_scheduled_task_reconcile_unit.py`   → `reconcile_unit`
    별칭 매칭은 **접미 허용**이라 `unit` 이 `reconcile_unit` 에 붙는다
    (모호하면 compare 가 위반으로 올린다 — 조용한 오매칭 금지)."""
    base = os.path.basename(path)
    if base.endswith(".py"):
        base = base[:-3]
    for prefix in ("test_scheduled_task_", "test_"):
        if base.startswith(prefix):
            return base[len(prefix):]
    return base


def _match_alias(alias, files):
    """별칭 → 파일 목록 (0/1/다). 완전일치 우선, 없으면 접미(`_alias`) 매칭."""
    exact = [f for f in files if alias_of(f) == alias]
    if exact:
        return exact
    return [f for f in files if alias_of(f).endswith("_" + alias)]


# ═══════════════════════════ 생성 (impure) ═══════════════════════════════════════
def _run(cmd, cwd, timeout=600):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )


def git_diff_axis(repo_root, base_ref="origin/main"):
    """`git diff --numstat <base>...HEAD` 실측 → (총계, 파일별 변경 행수).

    §8.7 의 `N행` 은 **변경 행수(추가+삭제)** 이지 `wc -l` 이 아니다 (Story 규약).
    base 미해소(shallow clone 등) → `None` (호출자가 사유를 명시적으로 다룬다)."""
    probe = _run(["git", "rev-parse", "--verify", "--quiet", base_ref + "^{commit}"], repo_root)
    if probe.returncode != 0:
        return None
    cp = _run(["git", "diff", "--numstat", "%s...HEAD" % base_ref], repo_root)
    if cp.returncode != 0:
        return None
    per_file, ins, dele = {}, 0, 0
    for ln in (cp.stdout or "").splitlines():
        parts = ln.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        if a == "-" or d == "-":        # binary — 행수 계상 불가
            per_file[path] = None
            continue
        a, d = int(a), int(d)
        ins += a
        dele += d
        per_file[path] = a + d
    head = _run(["git", "rev-parse", "--short", "HEAD"], repo_root).stdout.strip()
    return {
        "base_ref": base_ref,
        "head": head,
        "files_changed": len(per_file),
        "insertions": ins,
        "deletions": dele,
        "file_changed_lines": per_file,
    }


def _parse_collect_summary(stdout):
    """pytest `--collect-only -q` 요약 → (total, selected, deselected)."""
    for ln in reversed([l.strip() for l in (stdout or "").splitlines() if l.strip()]):
        m = _COLLECT_DESEL_RE.match(ln)
        if m:
            return int(m.group(2)), int(m.group(1)), int(m.group(3))
        m = _COLLECT_PLAIN_RE.match(ln)
        if m:
            n = int(m.group(1))
            return n, n, 0
    return None


def collect_axis(repo_root, files, mark=CI_MARK_EXPR, python=None):
    """`pytest --collect-only -q` 실측 → 총계 + mark 적용 선택/제외 + 파일별 수집 수."""
    py = python or sys.executable
    base = [py, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"]
    all_cp = _run(base + list(files), repo_root)
    summary_all = _parse_collect_summary(all_cp.stdout)
    if summary_all is None:
        return None
    total = summary_all[0]

    mark_cp = _run(base + ["-m", mark] + list(files), repo_root)
    summary_mark = _parse_collect_summary(mark_cp.stdout)
    if summary_mark is None:
        return None
    _, selected, deselected = summary_mark

    per_file = {}
    for f in files:
        cp = _run(base + [f], repo_root)
        s = _parse_collect_summary(cp.stdout)
        per_file[f] = None if s is None else s[0]
    return {
        "ci_files": len(files),
        "collect_total": total,
        "collect_selected": selected,
        "collect_deselected": deselected,
        "collect_per_file": per_file,
    }


def parse_suite_summary(stdout):
    """pytest `-q` 산출 → `(카운트 dict, 요약 줄, 미인식 토큰 목록)` — **pure**.

    요약 줄을 못 찾으면 `(None, None, [])`. 호출자가 그 사실을 명시적으로 다룬다
    (조용한 통과 금지 — `_SUITE_SPANLIKE_RE` 가 선언 축에서 지는 규율과 같은 방향).

    ★ 순수 함수로 떼어낸 이유: 구판은 subprocess 실행과 파싱이 한 덩어리라 **파싱만**
      시험할 방법이 없었다. 그래서 "실패를 삼키는가" 를 묻는 오라클을 붙일 자리가
      없었고, 결함이 실 실행에서 산출을 오염시킨 뒤에야 드러났다.
    """
    for raw in reversed([l for l in (stdout or "").splitlines() if l.strip()]):
        line = raw.strip().strip("=").strip()
        if not _SUITE_SUMMARY_LINE_RE.match(line):
            continue
        head = _SUITE_ELAPSED_RE.split(line)[0]
        counts, unknown = {}, []
        for m in _SUITE_TOKEN_RE.finditer(head):
            n, word = int(m.group(1)), m.group(2).lower()
            if word in _SUITE_KNOWN_OUTCOMES:
                counts[word] = counts.get(word, 0) + n
            else:
                unknown.append("%d %s" % (n, word))
        if not counts and not unknown:
            continue
        return counts, line, unknown
    return None, None, []


def summarize_suite_run(stdout, returncode):
    """pytest 산출 + **종료코드** → 스위트 축 dict — **pure**.

    ★ 종료코드가 판정에 들어가는 이유: 요약 줄만 읽으면 rc≠0 인 실행이 초록으로 기록될
      수 있다. 구판이 정확히 그랬다(rc 미참조 ∧ `failed` 슬롯 부재 — 두 결손이 겹쳐
      실패가 산출에서 사라졌다).
    """
    counts, line, unknown = parse_suite_summary(stdout)
    out = {"suite_returncode": returncode}
    if counts is None:
        out["suite_axis_unavailable"] = (
            "pytest 요약 줄 미인식 (rc=%s) — 미인식은 무결이 아니다" % returncode
        )
        return out
    out["suite_summary_line"] = line
    for word in ("passed", "skipped", "deselected", "xfailed", "xpassed"):
        out["suite_" + word] = counts.get(word, 0)
    out["suite_failed"] = counts.get("failed", 0)
    out["suite_errors"] = counts.get("error", 0) + counts.get("errors", 0)
    if unknown:
        out["suite_unknown_tokens"] = unknown
    # rc≠0 인데 실패-계열 토큰이 없다 = **설명되지 않은 비정상 종료**.
    #   pytest rc 2=사용자 중단 / 3=내부 오류 / 4=사용법 오류 / 5=수집 0 이 여기 걸린다.
    if returncode not in (0, None) and not out["suite_failed"] and not out["suite_errors"]:
        out["suite_rc_unexplained"] = (
            "pytest rc=%s 인데 요약 줄에 failed/error 토큰이 없다: %r" % (returncode, line)
        )
    return out


def suite_axis(repo_root, files, mark=CI_MARK_EXPR, python=None):
    """스위트 **실 실행** 축 (opt-in). 기본 생성 경로에서는 부르지 않는다.

    ★ 반환에 **종료코드**와 실패-계열 카운트가 들어간다 — 구판은 둘 다 없어 rc=1 인
      실행을 초록 dict 로 돌려줬다(FIX14 실물).
    """
    py = python or sys.executable
    cp = _run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-m", mark] + list(files),
              repo_root, timeout=1800)
    return summarize_suite_run(cp.stdout, cp.returncode)


def generate_manifest(repo_root=None, base_ref="origin/main", with_suite=False):
    """§8.7 이 선언해야 하는 수치 전량을 실측으로 생성한다."""
    root = repo_root_from(repo_root)
    files = ci_test_files(root)
    out = {"version": MANIFEST_VERSION, "ci_test_files": files}
    git = git_diff_axis(root, base_ref)
    if git is None:
        out["git_axis_unavailable"] = "base ref 미해소: %s (shallow clone 또는 ref 부재)" % base_ref
    else:
        out.update(git)
    col = collect_axis(root, files)
    if col is None:
        out["collect_axis_unavailable"] = "pytest --collect-only 요약 파싱 실패"
    else:
        out.update(col)
    if with_suite:
        s = suite_axis(root, files)
        if s is None:
            out["suite_axis_unavailable"] = "pytest 요약 파싱 실패"
        else:
            out.update(s)
    return out


# ═══════════════════════════ 파싱 (pure) ═════════════════════════════════════════
def extract_section(text, heading=SECTION_HEADING):
    """헤딩부터 **같은 레벨 또는 상위 레벨** 헤딩 직전까지 (h2 흡수 금지).

    ★ `tests/integration/test_scheduled_task_ac_matrix.py::extract_adr_section` 이
      구현리뷰 iter5 F-CR5-02 로 정정한 것과 **같은 종료조건**이다 — 정확히 같은
      레벨만 종료로 보면 문서 꼬리 전체를 흡수한다."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if l.startswith(heading)), -1)
    if start == -1:
        return None
    level = len(heading) - len(heading.lstrip("#"))
    end_re = re.compile(r"^#{1,%d} " % max(level, 1))
    end = next((i for i in range(start + 1, len(lines)) if end_re.match(lines[i])), len(lines))
    return "".join(lines[start:end])


def parse_suite_declarations(sec):
    """§8.7 텍스트 → (canonical 선언 목록, **미인식** span 목록).

    두 목록을 **분리해서** 돌려주는 것이 이 함수의 전부다 — 구판은 미인식을 부재와
    합쳐 버려(둘 다 `suite_passed` 키 부재) 호출자가 구분할 수 없었다.

    ── 판정 정의역 (over-claim 금지) ─────────────────────────────────────────────
    · **인식 가능성**은 절 안 canonical-shaped span **전부**에 적용된다.
    · **값 정합**은 **첫** 선언에만 적용된다(호출자 `compare_manifest` 소관). §8.7 은
      기계 판독 줄을 하나만 두고, 이후 등장은 **선행 baseline 이력·대비 서술**이기
      때문이다(동결 스냅샷의 `84 passed, 1 deselected` 가 그 실물). ⇒ 두 번째 이후
      선언의 **값**은 판정하지 않는다 — 거기 모순된 수치를 적으면 이 검사기는 못 잡는다.
    """
    decls, unparsed = [], []
    for m in _SUITE_SPANLIKE_RE.finditer(sec):
        strict = _SUITE_RE.fullmatch(m.group(0))
        if strict is None:
            unparsed.append(m.group(1).strip())
            continue
        decls.append({
            "passed": int(strict.group(1)),
            "skipped": int(strict.group(2) or 0),      # 슬롯 미기재 = 0 (하위호환)
            "deselected": int(strict.group(3)),
        })
    return decls, unparsed


def parse_manifest_section(story_text, heading=SECTION_HEADING):
    """Story §8.7 → 선언 dict. 절 부재 → `None`."""
    sec = extract_section(story_text, heading)
    if sec is None:
        return None
    declared = {"section_present": True}

    m = _TOTALS_RE.search(sec)
    if m:
        declared["files_changed"] = int(m.group(1))
        declared["insertions"] = int(m.group(2))
        declared["deletions"] = int(m.group(3))

    # 표 행 — `| \`path\` | ... (N행 ...) |`
    rows = {}
    for ln in sec.splitlines():
        mp = _ROW_PATH_RE.match(ln.strip())
        if not mp:
            continue
        path = mp.group(1).strip()
        ml = _ROW_LINES_RE.search(ln)
        rows[path] = int(ml.group(1)) if ml else None
    if rows:
        declared["file_changed_lines"] = rows

    mh = _COLLECT_HEAD_RE.search(sec)
    if mh:
        declared["ci_files"] = int(mh.group(1))
        declared["collect_total"] = int(mh.group(2))
        # 별칭 토큰은 `N건 =` 뒤 같은 문단에서만 읽는다 (문서 다른 수치 오식 차단)
        tail = sec[mh.end():]
        tail = tail.split("\n\n")[0]
        eq = tail.find("=")
        if eq != -1:
            seg = tail[eq + 1:]
            seg = seg.split(". ")[0]
            declared["collect_per_alias"] = {
                a: int(n) for a, n in _ALIAS_RE.findall(seg)
            }

    ms = _COLLECT_SELECT_RE.search(sec)
    if ms:
        declared["collect_selected"] = int(ms.group(1))
        declared["collect_deselected"] = int(ms.group(2))

    decls, unparsed = parse_suite_declarations(sec)
    if decls:
        declared["suite_declarations"] = decls
        declared["suite_passed"] = decls[0]["passed"]
        declared["suite_skipped"] = decls[0]["skipped"]
        declared["suite_deselected"] = decls[0]["deselected"]
    if unparsed:
        # ★ 값이 아니라 **인식 실패 사실**을 싣는다. 비교기가 이걸 위반으로 올린다.
        declared["suite_unparsed"] = unparsed

    return declared


# ═══════════════════════════ 대조 (pure) ═════════════════════════════════════════
def _cmp(viol, field, gen, dec, note=""):
    if field not in gen or field not in dec:
        return
    if gen[field] != dec[field]:
        viol.append("%s: 선언 %r ≠ 실측 %r%s" % (field, dec[field], gen[field],
                                                (" — " + note) if note else ""))


def compare_manifest(generated, declared):
    """생성 manifest ↔ §8.7 선언 대조 → 위반 목록 (빈 목록 = 일치).

    비교 대상이 양쪽에 다 있을 때만 비교한다 — 한쪽이 없으면 별도 위반으로 올린다
    (조용한 skip 금지)."""
    viol = []
    if declared is None:
        return ["§8.7 절 부재 — Impl Manifest 를 찾지 못했다 (heading=%r)" % SECTION_HEADING]

    for f in ("files_changed", "insertions", "deletions"):
        if f in generated and f not in declared:
            viol.append("%s: 선언 부재 (§8.7 총계 줄이 없다)" % f)
        _cmp(viol, f, generated, declared)

    # 파일별 변경 행수 (표에 `N행` 이 적힌 행만 — 미기재 행은 비교 대상 밖)
    g_files = generated.get("file_changed_lines")
    d_files = declared.get("file_changed_lines")
    if g_files is not None and d_files is not None:
        for path, g_n in sorted(g_files.items()):
            if path not in d_files:
                viol.append("표 누락: %s (실측 변경 %s행인데 §8.7 표에 행이 없다)" % (path, g_n))
                continue
            d_n = d_files[path]
            if d_n is None or g_n is None:
                continue                # 행수 미기재(예: 버전 bump 행) — 계약 밖
            if d_n != g_n:
                viol.append("파일 행수 %s: 선언 %d행 ≠ 실측 %d행" % (path, d_n, g_n))
        for path in sorted(set(d_files) - set(g_files)):
            viol.append("표 잉여: %s (§8.7 에 있으나 diff 에 없다)" % path)

    for f in ("ci_files", "collect_total", "collect_selected", "collect_deselected"):
        if f in generated and f not in declared:
            viol.append("%s: 선언 부재" % f)
        _cmp(viol, f, generated, declared)

    # 파일별 수집 수 (별칭 매칭)
    d_alias = declared.get("collect_per_alias")
    g_per = generated.get("collect_per_file")
    files = generated.get("ci_test_files") or (list(g_per) if g_per else [])
    if d_alias is not None and g_per is not None:
        seen = set()
        for alias, d_n in sorted(d_alias.items()):
            hits = _match_alias(alias, files)
            if len(hits) == 0:
                viol.append("수집 별칭 미해석: %r (CI 파일 목록에 대응 파일 없음)" % alias)
                continue
            if len(hits) > 1:
                viol.append("수집 별칭 모호: %r → %r" % (alias, hits))
                continue
            path = hits[0]
            seen.add(path)
            g_n = g_per.get(path)
            if g_n is not None and g_n != d_n:
                viol.append("수집 %s(%s): 선언 %d ≠ 실측 %d" % (alias, path, d_n, g_n))
        for path in sorted(set(files) - seen):
            viol.append("수집 선언 누락: %s (CI 인자에 있으나 §8.7 별칭 목록에 없다)" % path)

    # ── 스위트 결과 — 경로 **3분할** (FIX6-b) ────────────────────────────────────
    #   ① 미인식  ② 부재  ③ 값 불일치
    #   구판은 ①과 ②가 **같은 경로**였다: 스위트 줄이 있어도 파서가 못 읽으면
    #   `suite_passed` 키가 안 생기고, 키가 없으면 비교를 통째로 건너뛰어 **무결로
    #   통과**했다. ⇒ §8.7 에 skip 을 포함한 stale 선언을 적어도 위반 0.
    # ── ⓪ 실측 스위트가 green 이 아니면 **선언과 무관하게** 위반 (FIX14) ─────────
    #   §8.7 은 실패 없는 실행을 적는 절이다. 실패를 뺀 초록 줄(`163 passed, ...`)은
    #   선언과 **일치해 버리므로** 값 대조만으로는 rc=1 인 실행이 통과한다 — FIX14 실물이
    #   그 형상이었다. 실측 쪽 비-green 은 선언 대조 이전에 잡는다.
    if generated.get("suite_failed") or generated.get("suite_errors"):
        viol.append(
            "suite_failed: 실측 스위트 비-green — failed %d · error %d [%s]"
            % (generated.get("suite_failed", 0), generated.get("suite_errors", 0),
               generated.get("suite_summary_line") or "요약 줄 미기록")
        )
    if generated.get("suite_rc_unexplained"):
        viol.append("suite_returncode: " + generated["suite_rc_unexplained"])
    if generated.get("suite_axis_unavailable"):
        viol.append("suite_axis_unavailable: " + generated["suite_axis_unavailable"])
    if generated.get("suite_unknown_tokens"):
        viol.append(
            "suite_unknown_tokens: 요약 줄에 화이트리스트 밖 토큰 %r — 계상 정의역 밖이라 "
            "실행 축 합계를 신뢰할 수 없다" % (generated["suite_unknown_tokens"],)
        )
    # ⓪-b 실행 축 ↔ 수집 축 자기정합 — 요약 줄을 **일부만** 읽었는지 잡는 독립 그물.
    #   구판 파서를 그대로 두고 이 검사만 있어도 FIX14 형상이 잡힌다(163+1 ≠ 165).
    if "suite_passed" in generated and "collect_selected" in generated:
        run_sum = sum(generated.get("suite_" + k, 0) or 0 for k in _SUITE_RUN_OUTCOMES)
        if run_sum != generated["collect_selected"]:
            viol.append(
                "suite_run_total: 실행 outcome 합 %d ≠ 수집 선택 %d — 요약 줄을 일부만 "
                "읽었거나(구판 결함 형상) 계상 정의역 밖 outcome 이 섞였다 [%s]"
                % (run_sum, generated["collect_selected"],
                   generated.get("suite_summary_line") or "요약 줄 미기록")
            )

    unparsed = declared.get("suite_unparsed") or []
    for raw in unparsed:                                                    # ①
        viol.append(
            "스위트 줄 미인식: `%s` — canonical 형식(`N passed[, M skipped], "
            "K deselected`)이 아니다 (미인식 ≠ 무결)" % raw
        )
    decls = declared.get("suite_declarations") or []
    if not decls:                                                           # ②
        if not unparsed and ("suite_passed" in generated or "collect_selected" in generated):
            viol.append("suite_passed: 선언 부재 (§8.7 에 스위트 실행 결과 줄이 없다)")
    elif "suite_passed" in generated:                                       # ③-a 실행 축 대조
        _cmp(viol, "suite_passed", generated, declared)
        _cmp(viol, "suite_skipped", generated, declared)
        _cmp(viol, "suite_deselected", generated, declared)
    elif "collect_selected" in generated:                                   # ③-b 파생 불변식
        d0 = decls[0]
        run = d0["passed"] + d0["skipped"]
        if run != generated["collect_selected"]:
            viol.append(
                "suite_passed: 선언 %d passed + %d skipped = %d ≠ 수집 선택 %d — §8.7 은 "
                "전건 통과를 선언하므로 **passed + skipped** 가 선택 수와 같아야 한다 "
                "(skipped 는 deselected 와 달리 selected 에 포함된다). 합이 **모자라면** "
                "선언이 stale 이거나 실행에 failed/error 가 있었다는 뜻이다 — 선언 축 "
                "canonical 형식에는 failed 슬롯이 없으므로 실패는 이 부족분으로 드러난다"
                % (d0["passed"], d0["skipped"], run, generated["collect_selected"])
            )
        if "collect_deselected" in generated and d0["deselected"] != generated["collect_deselected"]:
            viol.append("suite_deselected: 선언 %r ≠ 수집 제외 %r"
                        % (d0["deselected"], generated["collect_deselected"]))
    return viol


# ═══════════════════════════ 렌더 ════════════════════════════════════════════════
def render_manifest(man):
    """canonical 평문 (사람·기계 양쪽 판독). TSV — 값에 탭 없음."""
    out = ["# " + man.get("version", MANIFEST_VERSION)]
    for k in ("base_ref", "head", "files_changed", "insertions", "deletions",
              "ci_files", "collect_total", "collect_selected", "collect_deselected",
              "suite_passed", "suite_skipped", "suite_deselected",
              # ★ 실패 축을 렌더에서 빼면 TSV 를 보는 사람에게 실패가 다시 안 보인다
              "suite_failed", "suite_errors", "suite_xfailed", "suite_xpassed",
              "suite_returncode", "suite_summary_line", "suite_unknown_tokens",
              "suite_rc_unexplained",
              "git_axis_unavailable", "collect_axis_unavailable", "suite_axis_unavailable"):
        if k in man:
            out.append("%s\t%s" % (k, man[k]))
    for p, n in sorted((man.get("file_changed_lines") or {}).items()):
        out.append("file\t%s\t%s" % (p, n))
    for p, n in sorted((man.get("collect_per_file") or {}).items()):
        out.append("collect\t%s\t%s" % (p, n))
    return "\n".join(out)


def render_markdown(man):
    """§8.7 에 그대로 붙일 선언 3줄 (수기 계산 0)."""
    per = man.get("collect_per_file") or {}
    aliases = " · ".join("%s %s" % (alias_of(p), per[p]) for p in (man.get("ci_test_files") or []))
    lines = []
    if "files_changed" in man:
        lines.append(
            "**산출물 총계** (`git diff --stat %s...HEAD`, 동결 HEAD `%s` 실측): "
            "**%d files changed, %d insertions(+), %d deletions(-)**"
            % (man.get("base_ref", "origin/main"), man.get("head", "?"),
               man["files_changed"], man["insertions"], man["deletions"])
        )
    if "collect_total" in man:
        lines.append(
            "**테스트 수집** (`pytest --collect-only -q` 파일별 실측, 동결 HEAD `%s`): "
            "%d 파일 **%d건** = %s. CI 인자 `-m \"%s\"` 적용 시 **선택 %d / deselected %d**."
            % (man.get("head", "?"), man["ci_files"], man["collect_total"], aliases,
               CI_MARK_EXPR, man["collect_selected"], man["collect_deselected"])
        )
    if "suite_passed" in man:
        # skip 0 이면 슬롯을 쓰지 않는다 — 기존 2-슬롯 선언과 **byte 동형**(하위호환).
        skipped = man.get("suite_skipped", 0)
        slot = (", %d skipped" % skipped) if skipped else ""
        failed = man.get("suite_failed", 0) or 0
        errors = man.get("suite_errors", 0) or 0
        rc = man.get("suite_returncode")
        if failed or errors or (rc not in (None, 0)):
            # ★ 비-green 을 canonical 초록 줄로 렌더하지 않는다 (FIX14). 그 줄을 §8.7 에
            #   붙이면 대조가 통과하는 **거짓 초록**이 된다 — 구판이 실제로 그 줄을
            #   뱉었다. 형식도 canonical 과 다르게(백틱 span 밖) 두어, 그대로 붙여넣어도
            #   선언 파서가 초록으로 읽지 못하게 한다.
            lines.append(
                "스위트 실행: **비-green** — failed %d · error %d · rc %s "
                "(passed %d%s, deselected %d). §8.7 은 실패 없는 실행을 적는 절이므로 "
                "이것은 붙여넣을 선언이 아니라 고쳐야 할 실패다."
                % (failed, errors, rc, man["suite_passed"], slot,
                   man.get("suite_deselected", 0))
            )
        else:
            lines.append("스위트 실행: `%d passed%s, %d deselected`"
                         % (man["suite_passed"], slot, man.get("suite_deselected", 0)))
    return "\n\n".join(lines)


# ═══════════════════════════ CLI ═════════════════════════════════════════════════
def main(argv=None):
    ap = argparse.ArgumentParser(description="Story §8.7 Impl Manifest 생성·대조")
    ap.add_argument("mode", choices=("generate", "check"))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--base-ref", default="origin/main")
    ap.add_argument("--story", default=None,
                    help="§8.7 을 담은 Story 파일 (미지정 시 env %s)" % ENV_STORY_FILE)
    ap.add_argument("--with-suite", action="store_true", help="스위트 실 실행 축 포함")
    ap.add_argument("--markdown", action="store_true", help="§8.7 붙여넣기용 선언 줄 출력")
    args = ap.parse_args(argv)

    root = repo_root_from(args.repo_root)
    man = generate_manifest(root, args.base_ref, with_suite=args.with_suite)

    if args.mode == "generate":
        print(render_markdown(man) if args.markdown else render_manifest(man))
        return 0

    story = resolve_story_path(args.story)
    if story is None:
        print("[impl-manifest] Story 경로 미주입 (--story 또는 %s) — 대조 미수행"
              % ENV_STORY_FILE, file=sys.stderr)
        return 2
    if not os.path.isfile(story):
        print("[impl-manifest] Story 파일 부재: %s" % story, file=sys.stderr)
        return 2
    with open(story, encoding="utf-8") as fh:
        declared = parse_manifest_section(fh.read())
    viol = compare_manifest(man, declared)
    if not viol:
        print("[impl-manifest] 일치 — §8.7 선언 == 실측")
        return 0
    print("[impl-manifest] 불일치 %d건:" % len(viol), file=sys.stderr)
    for v in viol:
        print("  - " + v, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
