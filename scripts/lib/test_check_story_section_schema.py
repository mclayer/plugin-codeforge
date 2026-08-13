#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MTD-1326 — story-section-schema lint discriminating fixture 하네스 (change-plan §3.5·§8)
#
# stdlib-only (unittest + tempfile + subprocess). tmpdir 에 throwaway git repo fixture
# (base 브랜치 + PR 브랜치 시나리오)를 실구성하고 linter 를 subprocess 로 실행해
# exit code·출력을 단언한다. 각 fixture 는 "잘못된 구현이 통과할 수 없는" 판별 조건을 내장.
#
# 실행: python3 scripts/lib/test_check_story_section_schema.py
# 소비자 소유 — plugin manifest 미등재 (배포 무관). MTD-1592 로 hub selftest 워크플로
# (.github/workflows/schema-lint-selftest.yml) 배선 (MTD-1326 §3.5 "후속 판단 위임" 이행).
#
# 주의: 파일 기록은 전부 LF 명시 (Windows CRLF 함정 — Compactor Epic 교훈) +
#       fixture repo core.autocrlf=false + GIT_CONFIG_GLOBAL 격리.
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_SRC = Path(__file__).resolve().parent / "check_story_section_schema.py"
BASELINE_REL = "docs/stories/schema-baseline.txt"


def make_story(missing=(), typ=None, frontmatter=True, suffix=""):
    """strict story md 생성 — §1~§11 헤딩, missing 섹션 제외. LF only."""
    lines = []
    if frontmatter:
        lines += ["---", "story_key: FIX-TEST"]
        if typ:
            lines.append(f"type: {typ}")
        lines += ["---", "", "# fixture story", ""]
    for n in range(1, 12):
        if n in missing:
            continue
        lines += [f"## {n}. 섹션 {n}", "", "내용", ""]
    out = "\n".join(lines) + "\n"
    if suffix:
        out += suffix if suffix.endswith("\n") else suffix + "\n"
    return out


def baseline_text(entries, header=True):
    txt = "# test baseline\n" if header else ""
    return txt + "".join(e + "\n" for e in entries)


class Fixture:
    """throwaway git repo — linter 사본을 scripts/lib/ 하위에 배치해 root-anchoring 을 fixture root 로 유도."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self._tmp.name)
        (self.root / "scripts" / "lib").mkdir(parents=True)
        shutil.copy(SCRIPT_SRC, self.root / "scripts" / "lib" / "check_story_section_schema.py")
        (self.root / "docs" / "stories").mkdir(parents=True)
        # git env 격리 — 사용자 global config(autocrlf·gpgsign·hooks) 차단
        self.env = dict(os.environ)
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        self.env["GIT_CONFIG_GLOBAL"] = str(self.root / ".gitconfig-isolated-absent")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "fixture@test.local")
        self.git("config", "user.name", "fixture")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "commit.gpgsign", "false")

    def cleanup(self):
        self._tmp.cleanup()

    def git(self, *args):
        cp = subprocess.run(
            ["git", "-C", str(self.root)] + list(args),
            capture_output=True, text=True, encoding="utf-8", env=self.env,
        )
        if cp.returncode != 0:
            raise AssertionError(f"git {args} failed: {cp.stderr}")
        return cp

    def write(self, rel, content):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "--no-verify", "-m", msg)

    def checkout(self, branch, create=False):
        args = ["checkout", "-q"]
        if create:
            args.append("-b")
        args.append(branch)
        self.git(*args)

    def run_lint(self, *args):
        """linter subprocess 실행 — cwd 를 의도적으로 repo 밖(부모)에 두어 root-anchoring 검증."""
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "lib" / "check_story_section_schema.py")] + list(args),
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(self.root.parent), env=self.env,
        )


def scenario_base(fx):
    """공통 base: main = 클린 c.md + 위반 v1.md(§11 누락 1건) + v2.md(§10·§11 누락 2건) + baseline[v1,v2]."""
    fx.write("docs/stories/c.md", make_story())
    fx.write("docs/stories/v1.md", make_story(missing=(11,)))
    fx.write("docs/stories/v2.md", make_story(missing=(10, 11)))
    fx.write(BASELINE_REL, baseline_text(["docs/stories/v1.md", "docs/stories/v2.md"]))
    fx.commit("base")


class SchemaLintFixtureTests(unittest.TestCase):

    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    # ---- F1 (AC-1): 위반=미변경 baseline 파일에만 · PR=클린 파일 수정 → exit 0 ----
    def test_F1_untouched_baseline_debt_green(self):
        fx = self.fx
        scenario_base(fx)
        fx.checkout("pr", create=True)
        fx.write("docs/stories/c.md", make_story(suffix="pr 수정 — 클린 유지"))
        fx.commit("pr: clean touch")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("❌", cp.stdout)  # 전량 린트 회귀(구부채 RED) 배제

    # ---- F2 (AC-2): PR 이 §11 누락 신규 story 추가 → exit 1 + 해당 ❌ ----
    def test_F2_new_violating_story_red(self):
        fx = self.fx
        scenario_base(fx)
        fx.checkout("pr", create=True)
        fx.write("docs/stories/new.md", make_story(missing=(11,)))
        fx.commit("pr: add violating story")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        self.assertIn("❌ docs/stories/new.md", cp.stdout)
        self.assertIn("§11", cp.stdout)

    # ---- F3 (AC-4): baseline 등재 파일 touched 위반 잔존 → RED · 전체 클린화 → GREEN (pair) ----
    def test_F3_touched_baseline_file_red_then_green(self):
        fx = self.fx
        scenario_base(fx)
        fx.checkout("pr", create=True)
        # RED: touched 인데 위반 잔존 ("baseline 이면 면제" 오구현 배제)
        fx.write("docs/stories/v1.md", make_story(missing=(11,), suffix="pr 수정 — 위반 잔존"))
        fx.commit("pr: touch v1 still violating")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        self.assertIn("❌ docs/stories/v1.md", cp.stdout)
        # GREEN: 같은 파일 전체 클린화
        fx.write("docs/stories/v1.md", make_story(suffix="pr 수정 — 전체 클린"))
        fx.commit("pr: clean v1 fully")
        cp2 = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp2.returncode, 0, cp2.stdout + cp2.stderr)

    # ---- F4 (AC-7a): baseline 신규 entry 추가 → exit 1 + ratchet ❌ · entry 제거만 → exit 0 ----
    def test_F4_ratchet_new_entry_red_removal_green(self):
        fx = self.fx
        scenario_base(fx)
        fx.write("docs/stories/v3.md", make_story(missing=(11,)))  # 비-baseline 위반 파일 (base)
        fx.commit("base: add v3 (non-baseline)")
        # PR-a: baseline 에 v3 entry 추가만 → ratchet RED
        fx.checkout("pr-add", create=True)
        fx.write(BASELINE_REL, baseline_text(
            ["docs/stories/v1.md", "docs/stories/v2.md", "docs/stories/v3.md"]))
        fx.commit("pr: baseline add entry")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        self.assertIn("ratchet", cp.stdout)
        self.assertIn("docs/stories/v3.md", cp.stdout)
        # PR-b: entry 제거만 (감소 단조 합법) → GREEN
        fx.checkout("main")
        fx.checkout("pr-remove", create=True)
        fx.write(BASELINE_REL, baseline_text(["docs/stories/v1.md"]))
        fx.commit("pr: baseline remove entry")
        cp2 = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp2.returncode, 0, cp2.stdout + cp2.stderr)
        self.assertNotIn("ratchet", cp2.stdout)

    # ---- F4b (AC-7a): 최초 도입 bootstrap (merge-base 판 부재 + 경로 이력 0건) → exit 0 + notice ----
    def test_F4b_bootstrap_first_introduction_green(self):
        fx = self.fx
        fx.write("docs/stories/v1.md", make_story(missing=(11,)))
        fx.commit("base: violating, no baseline ever")
        fx.checkout("pr", create=True)
        fx.write(BASELINE_REL, baseline_text(["docs/stories/v1.md"]))
        fx.commit("pr: introduce baseline (bootstrap)")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("bootstrap", cp.stdout)

    # ---- F4c (AC-7a [FIX-2]): cross-PR 재생성 — 도입→삭제 병합 후 재생성 → exit 1 (bootstrap 재개방 배제) ----
    def test_F4c_cross_pr_recreation_red(self):
        fx = self.fx
        fx.write("docs/stories/v1.md", make_story(missing=(11,)))
        fx.write(BASELINE_REL, baseline_text(["docs/stories/v1.md"]))
        fx.commit("main: introduce baseline")
        fx.git("rm", "-q", BASELINE_REL)
        fx.commit("main: delete baseline (merged)")
        fx.checkout("pr", create=True)
        fx.write(BASELINE_REL, baseline_text(["docs/stories/v1.md"]))
        fx.commit("pr: recreate baseline")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        self.assertIn("ratchet", cp.stdout)
        self.assertNotIn("bootstrap", cp.stdout)  # 경로 이력 실재 → bootstrap 불인정

    # ---- F5 (AC-8 [FIX-1] M-변형): 기존재 위반 파일을 base 가 분기 후 수정-병합 · PR=클린만 → exit 0 ----
    def test_F5_twodot_false_red_discriminator_m_variant(self):
        fx = self.fx
        # merge-base 시점 기존재: 클린 c.md + 위반 w.md (baseline 등재)
        fx.write("docs/stories/c.md", make_story())
        fx.write("docs/stories/w.md", make_story(missing=(11,)))
        fx.write(BASELINE_REL, baseline_text(["docs/stories/w.md"]))
        fx.commit("A: merge-base")
        fx.checkout("pr", create=True)  # 분기점 = A
        # base(main) 진전: w.md 수정-병합 (위반 잔존)
        fx.checkout("main")
        fx.write("docs/stories/w.md", make_story(missing=(11,), suffix="base 진전 수정 — 위반 잔존"))
        fx.commit("B: base modifies pre-existing violating w.md")
        # PR: 클린 파일만 수정
        fx.checkout("pr")
        fx.write("docs/stories/c.md", make_story(suffix="pr 수정 — 클린 유지"))
        fx.commit("pr: clean touch only")
        # 판별 전제 자기검증: buggy two-dot(main..HEAD) 이면 w.md 가 M 으로 오귀속된다
        twodot = fx.git("diff", "--name-status", "main..HEAD").stdout
        self.assertIn("docs/stories/w.md", twodot, "fixture 전제 붕괴 — two-dot 에 w.md 미출현이면 비판별")
        # 정상 three-dot 구현 → w.md 미귀속 → exit 0
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("❌", cp.stdout)  # two-dot false RED 배제

    # ---- F5b (AC-8 보조): base 가 신규 위반 파일 추가-병합 · PR=클린만 → exit 0 + 무크래시 ----
    def test_F5b_base_adds_new_violating_file_no_crash(self):
        fx = self.fx
        fx.write("docs/stories/c.md", make_story())
        fx.commit("A: merge-base")
        fx.checkout("pr", create=True)
        fx.checkout("main")
        fx.write("docs/stories/n.md", make_story(missing=(11,)))
        fx.commit("B: base adds new violating n.md")
        fx.checkout("pr")
        fx.write("docs/stories/c.md", make_story(suffix="pr 수정"))
        fx.commit("pr: clean touch")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("Traceback", cp.stderr)  # two-dot D-귀속 경로 무크래시 보조 단언 (판별 주장 없음)

    # ---- F6 (AC-8): story 삭제 = 미린트 무크래시 · rename(위반) = 신경로 ❌ exit 1 ----
    def test_F6_delete_no_crash_rename_new_path_red(self):
        fx = self.fx
        scenario_base(fx)
        # 삭제 PR
        fx.checkout("pr-del", create=True)
        fx.git("rm", "-q", "docs/stories/v2.md")
        fx.commit("pr: delete v2")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("Traceback", cp.stderr)  # 부재 파일 lint 크래시 배제
        # rename PR (위반 내용 유지 → 신경로 target RED)
        fx.checkout("main")
        fx.checkout("pr-ren", create=True)
        fx.git("mv", "docs/stories/v1.md", "docs/stories/v1-renamed.md")
        fx.commit("pr: rename v1 (violating)")
        cp2 = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp2.returncode, 1, cp2.stdout + cp2.stderr)
        self.assertIn("❌ docs/stories/v1-renamed.md", cp2.stdout)  # rename 누락 배제

    # ---- F7 (AC-5): 무인자 전량 raw — baseline 미적용 → exit 1 + 전 위반 출력 ----
    def test_F7_no_args_full_raw_ignores_baseline(self):
        fx = self.fx
        scenario_base(fx)
        cp = fx.run_lint()
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        self.assertIn("❌ docs/stories/v1.md", cp.stdout)  # baseline 등재여도 raw 는 출력
        self.assertIn("❌ docs/stories/v2.md", cp.stdout)
        self.assertIn("errors: 3", cp.stdout)  # v1=1건 + v2=2건

    # ---- F8 (AC-6): PR 모드 출력에 baseline 잔존 실측 라인 존재 (fail-loud) ----
    def test_F8_failloud_residual_count_line(self):
        fx = self.fx
        scenario_base(fx)
        fx.checkout("pr", create=True)
        fx.write("docs/stories/c.md", make_story(suffix="pr 수정"))
        fx.commit("pr: clean touch")
        cp = fx.run_lint("--pr-base", "main")
        m = re.search(r"baseline 잔존: (\d+) 파일 / (\d+) 건 \(entry (\d+)건\)", cp.stdout)
        self.assertIsNotNone(m, cp.stdout)
        self.assertEqual((m.group(1), m.group(2), m.group(3)), ("2", "3", "2"))  # 실측 기반 (정적 카운트 아님)

    # ---- F9 (fail-safe §5.1): base ref 미해석 → degraded ::warning + 방향성 양축 ----
    def test_F9_degraded_direction_both_axes(self):
        fx = self.fx
        scenario_base(fx)
        # 축 1: 위반이 baseline 등재 파일에만 → exit 0 (구부채 false RED 재발 차단)
        cp = fx.run_lint("--pr-base", "no-such-ref")
        self.assertIn("PR diff 귀속 실패", cp.stdout)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        # 축 2: 비-baseline 위반 실재 → exit 1 (신규 검출력 보존)
        fx.write("docs/stories/nb.md", make_story(missing=(11,)))
        fx.commit("add non-baseline violating")
        cp2 = fx.run_lint("--pr-base", "no-such-ref")
        self.assertIn("PR diff 귀속 실패", cp2.stdout)
        self.assertEqual(cp2.returncode, 1, cp2.stdout + cp2.stderr)

    # ---- F10 (AC-7b): stale entry (클린/부재) → ::warning + exit 0 (advisory — RED 승격 배제) ----
    def test_F10_stale_entry_warning_not_red(self):
        fx = self.fx
        fx.write("docs/stories/c.md", make_story())
        fx.write(BASELINE_REL, baseline_text(["docs/stories/c.md", "docs/stories/ghost.md"]))
        fx.commit("base: stale baseline (clean + absent)")
        fx.checkout("pr", create=True)
        fx.write("docs/stories/c.md", make_story(suffix="pr 수정"))
        fx.commit("pr: clean touch")
        cp = fx.run_lint("--pr-base", "main")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("stale entry — docs/stories/c.md", cp.stdout)
        self.assertIn("stale entry — docs/stories/ghost.md", cp.stdout)

    # ---- F11 (회귀): 클린 전량 fixture 무인자 → summary 포맷 현행 동일 (golden) ----
    def test_F11_no_args_summary_golden_format(self):
        fx = self.fx
        fx.write("docs/stories/a.md", make_story())
        fx.write("docs/stories/b.md", make_story())
        fx.commit("clean only")
        cp = fx.run_lint()
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(cp.stdout, "\nChecked 2 story file(s) — errors: 0, warnings: 0\n")

    # ---- 보조 (AC-3 도구): --write-baseline = 실측 재생성 · 멱등 ----
    def test_write_baseline_regenerates_from_measurement(self):
        fx = self.fx
        fx.write("docs/stories/c.md", make_story())
        fx.write("docs/stories/v1.md", make_story(missing=(11,)))
        fx.write("docs/stories/v2.md", make_story(missing=(10, 11)))
        fx.commit("base without baseline")
        cp = fx.run_lint("--write-baseline")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        content = (fx.root / BASELINE_REL).read_text(encoding="utf-8")
        entries = [l for l in content.splitlines() if l and not l.startswith("#")]
        self.assertEqual(entries, ["docs/stories/v1.md", "docs/stories/v2.md"])  # sorted·클린 제외
        self.assertIn("2 파일 / 3 건", cp.stdout)
        # 멱등: 재실행 = 동일 산출
        cp2 = fx.run_lint("--write-baseline")
        self.assertEqual(cp2.returncode, 0)
        self.assertEqual(content, (fx.root / BASELINE_REL).read_text(encoding="utf-8"))


# ==== MTD-1592: F-CLR dead-code 봉합 (bare-N/A 강제 · 빈 파일 warning · --pr-base 검증) ====
import importlib.util as _ilu


def _load_module():
    spec = _ilu.spec_from_file_location("cssc_under_test", SCRIPT_SRC)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _epic_story(sec8, sec10):
    """최소 Epic story — §8/§10 첫 content line = 지정값 (N/A 검사 도달)."""
    return (
        "---\ntype: epic\n---\n\n# epic fixture\n\n"
        f"## §8. 개발 서사\n{sec8}\n\n"
        f"## §10. FIX Ledger\n{sec10}\n"
    )


class MTD1592DeadcodeTests(unittest.TestCase):
    """F-CLR-1(bare-N/A 강제) · F-CLR-2(빈 파일 warning). 기존 15 하네스와 disjoint."""

    @classmethod
    def setUpClass(cls):
        cls.m = _load_module()

    def setUp(self):
        self._d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._d, ignore_errors=True)

    def _na_errors(self, text):
        p = Path(self._d) / "e.md"
        p.write_text(text, encoding="utf-8")
        res = self.m.lint_story_file(p, "e.md")
        return [e for e in (res[0] if res else []) if "N/A 사유 누락" in e]

    def test_bare_na_predicate(self):
        # bare(사유 부재) → True · 구분자 무관. 정상 N/A·실내용 → False (오탐 0).
        for line in ["N/A", "N/A ", "N/A —", "n/a", "N/A:"]:
            self.assertTrue(self.m._bare_na(line), f"bare 미포착: {line!r}")
        for line in ["N/A — 사유", "N/A (docs-only 배포없음)", "N/A: 실사유",
                     "| iter | lane | 원인 |", "실제 구현 서사 문단"]:
            self.assertFalse(self.m._bare_na(line), f"오탐: {line!r}")

    def test_epic_bare_na_red(self):
        # §8 = bare "N/A" → N/A 사유 누락 error 1 (RED)
        self.assertEqual(len(self._na_errors(_epic_story("N/A", "N/A — 사유"))), 1)

    def test_epic_valid_na_variants_green(self):
        # 대시·괄호·실표·산문 = 오탐 0 (RR2-B blast radius 가드 · RR-1 실표 가드)
        self.assertEqual(self._na_errors(_epic_story("N/A — 사유", "N/A (docs-only)")), [])
        self.assertEqual(self._na_errors(_epic_story("| iter | lane |", "실제 문단 내용")), [])

    def test_empty_file_warning(self):
        # F-CLR-2: 빈 파일 = warning 1 · error 0 (무소음 None 제거 · exit 불변)
        p = Path(self._d) / "empty.md"
        p.write_text("", encoding="utf-8")
        res = self.m.lint_story_file(p, "empty.md")
        self.assertIsNotNone(res, "빈 파일이 여전히 무소음 None")
        self.assertEqual(res[0], [], "빈 파일이 error (exit 교란)")
        self.assertEqual(len(res[1]), 1, "빈 파일 warning 미발화")


class MTD1592ArgparseTests(unittest.TestCase):
    """F-CLR-3: --pr-base 빈/공백 REF 거부 (subprocess = 실 CLI 경로)."""

    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    def test_pr_base_empty_exit2(self):
        self.fx.write("docs/stories/a.md", make_story())
        self.fx.commit("clean")
        for ref in ("", "   "):
            cp = self.fx.run_lint("--pr-base", ref)
            self.assertEqual(cp.returncode, 2, f"--pr-base {ref!r}: {cp.stdout + cp.stderr}")
            self.assertIn("비어있을 수 없음", cp.stderr, f"--pr-base {ref!r} stderr")

    def test_empty_file_counted_in_summary(self):
        # F-CLR-2 caller 경로: 빈 파일이 checked 에 포함 + warnings 집계 (무소음 skip 제거)
        self.fx.write("docs/stories/a.md", make_story())
        self.fx.write("docs/stories/empty.md", "")
        self.fx.commit("one clean + one empty")
        cp = self.fx.run_lint()
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)   # warning 은 exit 불변
        self.assertIn("Checked 2 story file(s) — errors: 0, warnings: 1", cp.stdout)  # 빈 파일 checked 포함
        self.assertIn("빈 story 파일", cp.stdout)                    # warning 실출력


if __name__ == "__main__":
    unittest.main(verbosity=2)
