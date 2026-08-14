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
#     "Story 가 전건 통과를 선언하므로 declared passed == 수집 선택 수" 라는
#     **파생 불변식**으로 잰다(§compare 규칙 7). 실 실행 대조가 필요하면
#     `generate --with-suite` 로 실행 축까지 채운다.
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
_SUITE_RE = re.compile(r"`(\d+)\s+passed,\s*(\d+)\s+deselected`")
# 표 행: 첫 셀 백틱 경로 + 마지막 셀 어딘가의 `NNN행`
_ROW_PATH_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")
_ROW_LINES_RE = re.compile(r"\((\d+)\s*행")
# 수집 별칭 토큰: `ac_matrix 21` / `unit 30`
_ALIAS_RE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s+(\d+)")

# pytest 수집 요약 줄
_COLLECT_PLAIN_RE = re.compile(r"^(\d+)\s+tests?\s+collected")
_COLLECT_DESEL_RE = re.compile(r"^(\d+)/(\d+)\s+tests?\s+collected\s*\((\d+)\s+deselected\)")
_SUITE_RESULT_RE = re.compile(r"(\d+)\s+passed(?:,\s*(\d+)\s+deselected)?")


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


def suite_axis(repo_root, files, mark=CI_MARK_EXPR, python=None):
    """스위트 **실 실행** 축 (opt-in). 기본 생성 경로에서는 부르지 않는다."""
    py = python or sys.executable
    cp = _run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-m", mark] + list(files),
              repo_root, timeout=1800)
    m = None
    for ln in reversed([l.strip() for l in (cp.stdout or "").splitlines() if l.strip()]):
        m = _SUITE_RESULT_RE.search(ln)
        if m:
            break
    if not m:
        return None
    return {
        "suite_passed": int(m.group(1)),
        "suite_deselected": int(m.group(2) or 0),
    }


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

    mu = _SUITE_RE.search(sec)
    if mu:
        declared["suite_passed"] = int(mu.group(1))
        declared["suite_deselected"] = int(mu.group(2))

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

    # 스위트 결과 — 실행 축이 없으면 **파생 불변식**으로 잰다.
    if "suite_passed" in declared:
        if "suite_passed" in generated:
            _cmp(viol, "suite_passed", generated, declared)
            _cmp(viol, "suite_deselected", generated, declared)
        elif "collect_selected" in generated:
            if declared["suite_passed"] != generated["collect_selected"]:
                viol.append(
                    "suite_passed: 선언 %d ≠ 수집 선택 %d — §8.7 은 전건 통과를 "
                    "선언하므로 passed 는 선택 수와 같아야 한다"
                    % (declared["suite_passed"], generated["collect_selected"])
                )
            if "collect_deselected" in generated and \
                    declared.get("suite_deselected") != generated["collect_deselected"]:
                viol.append("suite_deselected: 선언 %r ≠ 수집 제외 %r"
                            % (declared.get("suite_deselected"), generated["collect_deselected"]))
    return viol


# ═══════════════════════════ 렌더 ════════════════════════════════════════════════
def render_manifest(man):
    """canonical 평문 (사람·기계 양쪽 판독). TSV — 값에 탭 없음."""
    out = ["# " + man.get("version", MANIFEST_VERSION)]
    for k in ("base_ref", "head", "files_changed", "insertions", "deletions",
              "ci_files", "collect_total", "collect_selected", "collect_deselected",
              "suite_passed", "suite_deselected",
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
        lines.append("스위트 실행: `%d passed, %d deselected`"
                     % (man["suite_passed"], man["suite_deselected"]))
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
