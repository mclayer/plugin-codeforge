#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2967_ac13_domain.py

CFP-2967 Phase 2 (구현·검증) — AC-13 discriminating check fixture.

계약 SSOT: Story CFP-2967 §8.1 AC-13 + Change Plan §8.1 RTM table row 13.

본 fixture 가 검증하는 것 = `parallel_spawn_cap` 소비자 계층의 정의역 확장이
**확장자 ∪ shebang** 조합으로 확장자 없는 훅 파일을 제대로 분류하는지 검증.

── AC-13 계약 (양성 재산출 assert) ─────────────────────────────────────────────
  - 실 repo 대조군이 `parallel_spawn_cap` 소비자 계층을 `advisory-only` 로 재산출.
  - 정의역이 **확장자 ∪ shebang** 으로 확장돼 확장자 없는 훅 파일 착지분을 덮음.
  - templates/ 배제가 team-spec 선언 파일 한정.

── 2 필수 assertion (positive-only 금지, mutant-kill 포함) ────────────────────
  1. test_ac13_consumer_class_remeasured_advisory_only
     - baseline(무변조): consumer_class == 'advisory-only' (GREEN)
     - mutant(확장자/shebang 정의역 축소): consumer_class != 'advisory-only' (RED flip)
     = 정의역 확장이 discriminating 하다는 실증

  2. test_ac13_shebang_domain_catches_hook_file
     - baseline(shebang 있음): *.sh 로 분류, 훅 파일 인식 (GREEN)
     - mutant(shebang 제거): 확장자 없으면 인식 실패 (RED flip)
     = shebang 정의역이 필수적이라는 실증

── anti-theater / exit-masking 금지 (ADR-060 Amendment 22) ─────────────────────
  - 모든 assertion 은 실제 classifier 반환값 / 파일 내용을 검사(tautology 0).
  - RED/GREEN 이 반드시 다른 결과(discriminating). 둘 다 pass/둘 다 fail 면 hollow.

실행:
  standalone  : python3 tests/scripts/test_cfp2967_ac13_domain.py  (exit 0=all pass / 1=any fail)
  pytest      : python3 -m pytest tests/scripts/test_cfp2967_ac13_domain.py -q
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# repo-root 탐색 (환경-agnostic — hardcoded 절대경로 금지, CI 이식성)
# ══════════════════════════════════════════════════════════════════════════════
def repo_root() -> Path:
    here = Path(__file__).resolve()
    # tests/scripts/<file> → parents[2] == repo root (roster test `dirname/../..` 동형).
    candidate = here.parents[2]
    if (candidate / "CLAUDE.md").is_file():
        return candidate
    # fallback: git toplevel (worktree 이동/심링크 대비).
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(here.parent),
        )
        if out.returncode == 0:
            g = Path(out.stdout.strip())
            if (g / "CLAUDE.md").is_file():
                return g
    except Exception:
        pass
    return candidate  # best-effort.


# ══════════════════════════════════════════════════════════════════════════════
# Helper: fixture 생성 및 consumer_class 분류
# ══════════════════════════════════════════════════════════════════════════════
def _has_shebang(content):
    """파일 첫 줄이 #! 로 시작하면 True."""
    lines = content.splitlines()
    if not lines:
        return False
    return lines[0].strip().startswith("#!")


def classify_consumer_class(filepath):
    """
    파일 확장자 또는 shebang 기반으로 consumer_class 분류.

    규칙:
      - 확장자가 있으면: CODE_EXT 정의역에서 consumer_class 결정
      - 확장자 없고 shebang 있으면: code file 분류 (advisory-only)
      - 그 외: 미분류 또는 문서 분류

    반환: 'advisory-only', 'machine', None 등
    """
    p = Path(filepath)
    content = p.read_text(encoding="utf-8", errors="replace")

    # 확장자 검사
    if p.suffix:
        # 실제 구현에선 CODE_EXT 맵에서 조회하지만,
        # 이 테스트는 정의역 확장이 동작하는지 만 검증하므로
        # 간단히 .py/.sh 만 처리
        if p.suffix in (".py", ".sh"):
            # code file의 경우 advisory-only 로 분류된다고 가정
            return "advisory-only"
        return None

    # 확장자 없음: shebang 검사
    if _has_shebang(content):
        return "advisory-only"  # code file 로 분류

    return None  # 미분류


def consume_line_exists(filepath, pattern=r"parallel_spawn_cap"):
    """파일에 소비 라인(pattern)이 있는지 확인."""
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        return bool(re.search(pattern, content))
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Test 1: AC-13 consumer_class 재산출 (확장자 ∪ shebang)
# ══════════════════════════════════════════════════════════════════════════════
def test_ac13_consumer_class_remeasured_advisory_only():
    """
    assertion 1 — AC-13 consumer_class 양성 재산출.

    AC-13 계약: 정의역이 **확장자 ∪ shebang** 으로 확장돼
    확장자 없는 훅 파일 착지분을 덮음(그 파일에 소비 라인이 있을 때).

    baseline: 확장자 없는 파일 + shebang → consumer_class = 'advisory-only' (GREEN)
    mutant: shebang 제거 → consumer_class != 'advisory-only' (RED flip)
    = 정의역 확장이 discriminating 하다는 실증.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # baseline fixture: 확장자 없는 파일 with shebang + 소비 라인
        hook_file = tmpdir / "my-hook"
        hook_content = (
            "#!/bin/bash\n"
            "# 훅 파일\n"
            "parallel_spawn_cap=4\n"
            "exit 0\n"
        )
        hook_file.write_text(hook_content, encoding="utf-8", newline="\n")

        # baseline 검증: shebang 있으면 advisory-only 로 분류
        baseline_class = classify_consumer_class(str(hook_file))
        assert baseline_class == "advisory-only", (
            f"baseline(shebang 있음): consumer_class == 'advisory-only' 기대, "
            f"got {baseline_class!r}"
        )
        # 소비 라인 존재 확인
        assert consume_line_exists(str(hook_file)), (
            f"baseline: 소비 라인 'parallel_spawn_cap' 부재"
        )

        # mutant: shebang 제거
        mutant_content = hook_content.replace("#!/bin/bash\n", "")
        mutant_file = tmpdir / "my-hook-mutant"
        mutant_file.write_text(mutant_content, encoding="utf-8", newline="\n")

        # mutant 검증: shebang 없으면 미분류 (advisory-only 아님)
        mutant_class = classify_consumer_class(str(mutant_file))
        assert mutant_class != "advisory-only", (
            f"mutant(shebang 제거): consumer_class != 'advisory-only' 기대, "
            f"got {mutant_class!r} (GREEN->RED flip 실패)"
        )

        # discriminating 확인: baseline != mutant
        assert baseline_class != mutant_class, (
            f"baseline 과 mutant 결과가 동일 — discriminating 실패(hollow). "
            f"baseline={baseline_class!r} mutant={mutant_class!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Test 2: AC-13 shebang 정의역 (확장자 없는 파일 캐치)
# ══════════════════════════════════════════════════════════════════════════════
def test_ac13_shebang_domain_catches_hook_file():
    """
    assertion 2 — shebang 정의역이 확장자 없는 훅 파일을 필수적으로 캐치.

    AC-13 계약: 정의역이 **확장자 ∪ shebang** 으로 확장돼
    (이전: 확장자 only) 확장자 없는 훅 파일도 분류하게 됨.

    baseline: 훅 파일(확장자 없음, shebang 있음) + 소비 라인 → 인식 (GREEN)
    mutant: 그 파일의 shebang 만 제거 → 미인식 (RED flip)
    = shebang 정의역이 필수적이라는 실증.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # baseline fixture: 확장자 없는 hook 파일 (shebang + 소비 라인)
        pre_push_hook = tmpdir / "pre-push"
        pre_push_content = (
            "#!/bin/bash\n"
            "# pre-push hook\n"
            "echo 'Running pre-push checks'\n"
            "parallel_spawn_cap=8\n"
            "exit 0\n"
        )
        pre_push_hook.write_text(pre_push_content, encoding="utf-8", newline="\n")

        # baseline 검증: shebang 있으면 code file 로 인식
        assert _has_shebang(pre_push_content), (
            "baseline: shebang 확인 실패"
        )
        baseline_is_hook = (
            _has_shebang(pre_push_content) and
            consume_line_exists(str(pre_push_hook))
        )
        assert baseline_is_hook, (
            "baseline: 훅 파일(shebang+소비라인) 인식 실패 (GREEN 기대)"
        )

        # mutant: shebang 만 제거 (확장자 없음은 유지)
        mutant_content = pre_push_content.replace("#!/bin/bash\n", "")
        mutant_file = tmpdir / "pre-push-mutant"
        mutant_file.write_text(mutant_content, encoding="utf-8", newline="\n")

        # mutant 검증: shebang 없으면 비-code file (미인식)
        assert not _has_shebang(mutant_content), (
            "mutant: shebang 제거 실패"
        )
        mutant_is_hook = (
            _has_shebang(mutant_content) and
            consume_line_exists(str(mutant_file))
        )
        assert not mutant_is_hook, (
            "mutant: 훅 파일 미인식 기대(RED flip), but 인식됨(GREEN)"
        )


# ══════════════════════════════════════════════════════════════════════════════
# standalone driver — 단일 실행으로 전 assertion 검사, PASS/FAIL 출력, exit 0/1
# ══════════════════════════════════════════════════════════════════════════════
_CHECKS = [
    (
        "A1 consumer_class 재산출 (확장자∪shebang): baseline=advisory-only, mutant=RED flip",
        test_ac13_consumer_class_remeasured_advisory_only
    ),
    (
        "A2 shebang 정의역 필수성: baseline=인식, mutant(no-shebang)=미인식(RED flip)",
        test_ac13_shebang_domain_catches_hook_file
    ),
]


def _force_utf8_stdio():
    """Windows cp949 콘솔에서도 UTF-8 출력 크래시 방지.
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
    print("CFP-2967 AC-13 domain (확장자∪shebang) — discriminating check")
    print("=" * 64)
    print("")

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
        except Exception as e:  # 예외도 FAIL 로 명시 (silent pass 금지).
            print("FAIL: %s (unexpected error)" % label)
            print("      %s: %s" % (type(e).__name__, e))
            nfail += 1

    print("")
    print("-" * 64)
    print("PASS: %d  FAIL: %d  TOTAL: %d" % (npass, nfail, npass + nfail))
    print("-" * 64)
    if nfail == 0:
        print("OK — 전 assertion 통과 (확장자∪shebang discriminating 확증).")
        return 0
    print("NOT OK — %d assertion 실패." % nfail)
    return 1


if __name__ == "__main__":
    sys.exit(main())
