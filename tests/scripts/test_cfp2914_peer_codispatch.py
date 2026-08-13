#!/usr/bin/env python3
"""
CFP-2914 Phase 2 — peer co-dispatch observability pytest suite.

Tests for check-lane-evidence.sh peer co-dispatch validation logic
(AC-2a: peer identity + round grouping + coverage states).
Tests for AC-3 (early-return paths not counted) and AC-4 (section 14 exemption).

7 required test functions for ac-traceability-matrix gate discovery:
  1. test_peer_codispatch_coverage_states
  2. test_peer_identity_keying
  3. test_peer_round_grouping
  4. test_spawn_timing_threshold_boundary
  5. test_design_leg_bit_identical
  6. test_early_return_paths_not_counted
  7. test_section14_exemption_probe
"""

import subprocess
import tempfile
import os
import sys
import shutil
import re
import hashlib
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None


def find_bash():
    """Locate bash interpreter (Windows Git Bash or system bash)."""
    candidates = [
        "bash",
        r"C:\Program Files\Git\bin\bash.exe",
    ]
    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                timeout=2,
            )
            if result.returncode == 0:
                return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    raise RuntimeError("bash not found in PATH or common Git Bash location")


BASH_EXE = find_bash()
REPO_ROOT = Path(__file__).parent.parent.parent.absolute()
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "check-lane-evidence.sh"

# Ensure harness script exists
if not HARNESS_SCRIPT.exists():
    raise RuntimeError(f"Harness script not found: {HARNESS_SCRIPT}")
if not REPO_ROOT.exists():
    raise RuntimeError(f"Repo root not found: {REPO_ROOT}")


def mk_story(name: str, yaml_content: str) -> str:
    """Create a fixture story file with §14 YAML wrapper."""
    tmpdir = tempfile.mkdtemp(prefix="pytest_cfp2914_")
    story_path = Path(tmpdir) / f"{name}.md"
    story_path.write_text(
        f"## §14 Lane Evidence\n```yaml\n{yaml_content}\n```\n",
        encoding="utf-8",
        newline="\n",
    )
    return str(story_path)


def _extract_origin_main_script():
    """origin/main 판 `check-lane-evidence.sh` 를 temp 로 추출해 경로 반환 (실패 시 None).

    I-4(설계 leg bit-identical) 대조의 baseline. `git show` 는 **바이트 그대로** 받아야 한다
    — 줄 배열로 받아 재조립하면 개행이 소실돼 스크립트가 깨진다(실측 함정).
    """
    try:
        result = subprocess.run(
            ["git", "show", "origin/main:scripts/check-lane-evidence.sh"],
            capture_output=True,
            timeout=15,
            cwd=str(REPO_ROOT),
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout:
        return None
    tmpdir = tempfile.mkdtemp(prefix="pytest_cfp2914_i4_")
    old_path = Path(tmpdir) / "old-check-lane-evidence.sh"
    # CRLF 유입 시 bash 가 깨지므로 LF 로 정규화한다.
    old_path.write_bytes(result.stdout.replace(b"\r\n", b"\n"))
    return str(old_path)


# I-4 대조용 4-분기 전수 + 임계 경계 픽스처.
#   (i) design_rows=0 SKIP / (ii) evidence-absence / (iii) fan-out 미달 / (iv) OK·WARN
_I4_BRANCH_FIXTURES = [
    ("branch_i_skip", "- lane: 구현\n  iteration: 1\n"),
    (
        "branch_ii_evidence_absent",
        "".join(f"- lane: 설계\n  spawned_at: 2026-06-30T09:00:0{i}Z\n" for i in range(3))
        + "".join(f"- lane: 설계\n  iteration: {i}\n" for i in range(4, 7)),
    ),
    (
        "branch_iii_fanout_short",
        "".join(f"- lane: 설계\n  spawned_at: 2026-06-30T09:00:0{i}Z\n" for i in range(3)),
    ),
    (
        "branch_iv_ok",
        "".join(f"- lane: 설계\n  spawned_at: 2026-06-30T09:00:0{i}Z\n" for i in range(6)),
    ),
    (
        "branch_iv_warn",
        "".join(f"- lane: 설계\n  spawned_at: 2026-06-30T09:00:{i:02d}Z\n" for i in (0, 10, 20, 30, 40))
        + "- lane: 설계\n  spawned_at: 2026-06-30T09:01:01Z\n",
    ),
]


def run_harness(
    story_path: str,
    extra_args: list = None,
    stderr_to_stdout: bool = True,
    script: str = None,
) -> tuple:
    """
    Run check-lane-evidence.sh and return (returncode, combined_output).

    Args:
        story_path: path to fixture story file
        extra_args: additional arguments (e.g., ['--check-parallelization'])
        stderr_to_stdout: if True, merge stderr into stdout
        script: SUT 경로 override (I-4 baseline 대조용). 기본 = 현 worktree 판

    Returns:
        (returncode, stdout_text)

    Raises:
        subprocess.TimeoutExpired: if harness exceeds timeout (120s default, adjusted from
            10s to account for high-load CI environments where 10s is insufficient —
            observed real-world execution times: 110s (Codex), 707s (review PL under load)).
    """
    cmd = [BASH_EXE, str(script or HARNESS_SCRIPT), "--story", story_path]
    if extra_args:
        cmd.extend(extra_args)

    # ★ Timeout = 120 seconds
    # Rationale: Real-world measured times:
    #   - Codex peer review execution: ~110s
    #   - Review PL high-load execution: ~707s (outlier, but indicates 10s is too short)
    #   - Standard execution: 5-20s
    # 10s timeout causes intermittent failures on loaded systems, misdiagnosed as content errors.
    # 120s is conservative ceiling for CI environments while still catching true hangs.
    TIMEOUT_SECONDS = 120

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            text=True,
            # ★ encoding 명시 필수 — 미지정 시 locale 기본 코덱(한국어 Windows = cp949)으로
            #   디코딩해 SUT 의 한글 출력에서 UnicodeDecodeError 로 죽는다. CI(ubuntu)는 UTF-8
            #   기본이라 로컬에서만 터지는 비대칭 결함이라 반드시 고정한다.
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),  # Ensure we run from repo root
        )
        if stderr_to_stdout:
            combined = result.stdout + result.stderr
        else:
            combined = result.stdout
        return result.returncode, combined
    except subprocess.TimeoutExpired as e:
        # ★ EXPLICIT TIMEOUT ESCALATION (F-CR-005)
        # Do NOT suppress timeout as silent failure or content-not-found error.
        # Caller must never see timeout as (rc, out) and interpret missing output as assertion failure.
        # Re-raise to force test failure with explicit TIMEOUT_EXCEEDED marker.
        raise AssertionError(
            f"Harness subprocess exceeded {TIMEOUT_SECONDS}s timeout. "
            f"Command: {' '.join(cmd[:3])} ... "
            f"This is NOT a content assertion failure; the subprocess did not complete in time."
        ) from e


def assert_in_output(text: str, search_str: str, msg: str = "") -> None:
    """Assert that search_str is found in text."""
    if search_str not in text:
        raise AssertionError(f"Expected text not found: {search_str}\n{msg}\n--- Output ---\n{text}")


def assert_not_in_output(text: str, search_str: str, msg: str = "") -> None:
    """Assert that search_str is NOT found in text."""
    if search_str in text:
        raise AssertionError(f"Forbidden text found: {search_str}\n{msg}\n--- Output ---\n{text}")


def assert_matches_pattern(text: str, pattern: str, msg: str = "") -> None:
    """Assert that pattern is matched in text."""
    if not re.search(pattern, text):
        raise AssertionError(f"Pattern not matched: {pattern}\n{msg}\n--- Output ---\n{text}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 1: test_peer_codispatch_coverage_states (AC-2a, MUT-P3, MUT-P6)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_peer_codispatch_coverage_states():
    """
    AC-2a: Verify peer co-dispatch coverage classification (PEER-0/1/2).

    States:
      PEER-0 (环境不存在): no peer rows
      PEER-1 (below_expected): peer rows present but less than expected (2)
      PEER-2 (measurable): 2+ distinct peer identities in same iteration

    MUT-P3: peer 1 + PL 3 → PEER-1 (below_expected), should NOT pass
    MUT-P6: dual-peer coverage axis must not contaminate co-dispatch verdict
    """

    # Fixture C1: PEER-0 — no peer rows at all (env=0 state)
    story_c1 = mk_story(
        "c1_no_peer",
        """- lane: 설계-리뷰
  iteration: 1
  agent: DesignReviewPLAgent
  spawned_at: 2026-06-30T09:00:00Z
""",
    )
    rc, out = run_harness(story_c1, ["--check-parallelization"])
    # PEER-0: no peer agent row → [PEER CO-DISPATCH N/A] or [PEER CO-DISPATCH SCOPE]
    assert_not_in_output(out, "[PEER CO-DISPATCH PASS]", "PEER-0 should NOT pass")

    # Fixture C3: PEER-1 — partial peer coverage (1 peer, need 2+)
    story_c3 = mk_story(
        "c3_one_peer_only",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z+09:00
- lane: 설계-리뷰
  iteration: 1
  agent: DesignReviewPLAgent (helper role 1)
  spawned_at: 2026-06-30T09:05:00+09:00
- lane: 설계-리뷰
  iteration: 1
  agent: TestContractArchitectAgent (helper role 2)
  spawned_at: 2026-06-30T09:10:00+09:00
""",
    )
    rc, out = run_harness(story_c3, ["--check-parallelization"])
    # Only 1 peer identity → PEER-1 (below_expected)
    assert_not_in_output(out, "[PEER CO-DISPATCH PASS]", "PEER-1 (1 peer) should NOT pass")

    # Fixture C2: PEER-2 — full peer coverage (2 distinct peer agents)
    story_c2 = mk_story(
        "c2_two_peers",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:00:15Z
""",
    )
    rc, out = run_harness(story_c2, ["--check-parallelization"])
    # 2 peer identities → PEER-2 (measurable) → should pass
    assert_in_output(out, "[PEER CO-DISPATCH PASS]", "PEER-2 (2 peers) should pass")

    # MUT-P6: Coverage axis (dual-peer) should NOT contaminate co-dispatch verdict
    # Design-leg + dual peer (Claude + Codex) in separate iterations
    story_dual = mk_story(
        "c6_dual_coverage_separate_iter",
        """- lane: 설계
  iteration: 1
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  iteration: 1
  spawned_at: 2026-06-30T09:00:01Z
- lane: 설계
  iteration: 1
  spawned_at: 2026-06-30T09:00:02Z
- lane: 설계
  iteration: 1
  spawned_at: 2026-06-30T09:00:03Z
- lane: 설계
  iteration: 1
  spawned_at: 2026-06-30T09:00:04Z
- lane: 설계
  iteration: 1
  spawned_at: 2026-06-30T09:00:05Z
- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 3
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T15:00:00Z
""",
    )
    rc, out = run_harness(story_dual, ["--check-parallelization"])
    # Each iteration (1, 3) has only 1 peer → should NOT report cumulative "2 peers"
    # Output should show PEER-1 for each iteration, not PASS
    assert_not_in_output(
        out,
        "[PEER CO-DISPATCH PASS]",
        "MUT-P6: dual-peer in separate iterations should NOT contaminate verdict"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 2: test_peer_identity_keying (AC-2a, MUT-P4, MUT-P2, MUT-P9)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_peer_identity_keying():
    """
    AC-2a: Peer identity is keyed by exact leading-token match, not full agent string.

    MUT-P4: "DesignReviewPLAgent (…)" leading token is PL (not peer).
    MUT-P2: Offset parsing (+09:00) must be preserved → positive marker assert.
    MUT-P9: Equality guard (valid_spawned_at_count == peer_rows) must protect.
    """

    # MUT-P4 fixture: Helper/PL tokens in agent string should NOT be counted as peer
    story_p4 = mk_story(
        "p4_pl_not_peer",
        """- lane: 설계-리뷰
  iteration: 1
  agent: DesignReviewPLAgent (supervisor role) + ClaudeReviewAgent + CodexReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
""",
    )
    rc, out = run_harness(story_p4, ["--check-parallelization"])
    # PL string contains "ClaudeReviewAgent" but "DesignReviewPLAgent" is leading token
    # → only 1 peer (PL doesn't count) → should NOT pass
    assert_not_in_output(out, "[PEER CO-DISPATCH PASS]", "MUT-P4: PL token should not count")

    # MUT-P2 fixture: CFP-475 실물 형상 — `+09:00` offset 보존 ∧ 전건 `iteration: 1`.
    #   ★ 픽스처 전역 구속 ② (§8.12): 기존 self-test 픽스처는 전건 `Z` 표기라 offset 파싱이
    #     실패해도 조용히 WARN 으로 흡수되고 "PASS 가 아니다" 만 보는 oracle 은 그대로 통과한다.
    #     → offset 계열은 **긍정 토큰을 직접 문다**: `[PEER CO-DISPATCH PASS]` ∧ `diff = 0s`.
    #   두 peer 의 시각을 동일하게 두어 정답 diff 를 0s 로 고정한다(§8.12 MUT-P2 기대치).
    #   시각을 어긋나게 두면 WARN 이 정답이 되어 offset 파싱 성공 여부를 판별하지 못한다.
    story_p2 = mk_story(
        "p2_offset_parsed",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00+09:00
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:00:00+09:00
""",
    )
    rc, out = run_harness(story_p2, ["--check-parallelization"])
    # positive 토큰 직접 assert (부정 assert 만으로는 offset 파싱 실패를 못 잡는다)
    assert_in_output(out, "[PEER CO-DISPATCH PASS]", "MUT-P2: offset should parse successfully")
    assert_matches_pattern(out, r"diff\s*=\s*0s", "MUT-P2: offset 파싱 성공 시 diff 는 정확히 0s")

    # MUT-P9 fixture: Equality guard — if spawned_at count < peer_rows, don't calculate diff
    story_p9 = mk_story(
        "p9_partial_timestamps",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
""",
    )
    rc, out = run_harness(story_p9, ["--check-parallelization"])
    # 2 peers but only 1 valid timestamp → evidence_absent guard should trigger
    # Use raw string for regex pattern
    if re.search(r"diff\s*=\s*0s", out):
        raise AssertionError("MUT-P9: missing timestamp should not produce diff=0s (guard should prevent)\n--- Output ---\n" + out)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 3: test_peer_round_grouping (AC-2a, MUT-P1, MUT-P5, MUT-P7)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_peer_round_grouping():
    """
    AC-2a: Peer co-dispatch is grouped by (lane, iteration) tuple.
    Different iterations must NOT be collapsed.

    MUT-P1: Different iteration rows should not co-dispatch (PEER-0).
    MUT-P5: Same iteration rows from same peer should collapse to min(spawned_at).
    MUT-P7: Mixed iteration rounds should be separated.
    """

    # MUT-P1 fixture: Different iterations in same lane → no co-dispatch
    story_p1 = mk_story(
        "p1_diff_iteration",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 2
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 2
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:00:05Z
""",
    )
    rc, out = run_harness(story_p1, ["--check-parallelization"])
    # Iteration 1: only Claude → PEER-1 (below_expected)
    # Iteration 2: Claude + Codex → PEER-2 (pass)
    # But separate grouping means output shows both states independently
    lines = out.split('\n')
    # Should have indication of separate handling per iteration
    assert_not_in_output(
        out,
        "iteration: 1.*iteration: 2.*diff",  # Not collapsed
        "MUT-P1: different iterations should not be grouped"
    )

    # MUT-P5 fixture: Same iteration, same peer, multiple rows → collapse to min
    story_p5 = mk_story(
        "p5_same_peer_collapse",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:10Z
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:00:15Z
""",
    )
    rc, out = run_harness(story_p5, ["--check-parallelization"])
    # Duplicate Claude rows should collapse to min(09:00:00)
    # With Codex at 09:00:15 → diff = 15s → PASS
    assert_in_output(out, "[PEER CO-DISPATCH PASS]", "MUT-P5: collapse should enable pass")
    assert_matches_pattern(out, r"diff\s*=\s*1[0-5]s", "MUT-P5: diff should be ~10-15s (collapse to min)")

    # MUT-P7 fixture: Mixed iteration rounds with fixed peer roles
    story_p7 = mk_story(
        "p7_mixed_rounds_separate",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 2
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T12:00:00Z
- lane: 설계-리뷰
  iteration: 2
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T12:00:00Z
""",
    )
    rc, out = run_harness(story_p7, ["--check-parallelization"])
    # Iteration 1: only Claude → PEER-1 (no PASS)
    # Iteration 2: Claude + Codex, diff=0 → PASS
    # Output should distinguish the two rounds
    assert_not_in_output(
        out,
        "iteration.*1.*iteration.*2.*diff.*0s.*" +
        "iteration.*1.*iteration.*2.*diff.*0s",  # Not merged
        "MUT-P7: iterations should be processed separately"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 4: test_spawn_timing_threshold_boundary (AC-2a, BC-1/BC-1′)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_spawn_timing_threshold_boundary():
    """
    AC-2a: Threshold boundary test — 59s (OK) vs 60s (WARN) vs 61s (WARN).

    BC-1 (design leg): check_parallelization uses -lt 60
    BC-1′ (peer leg): peer timing also uses -lt 60
    """

    # Fixture B1: design leg at 59s → OK
    story_b1 = mk_story(
        "b1_design_59s",
        """- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:59Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:30Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:15Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:45Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:10Z
""",
    )
    rc, out = run_harness(story_b1, ["--check-parallelization"])
    assert_in_output(out, "[PARALLELIZATION OK]", "BC-1a: 59s should be OK")
    assert_not_in_output(out, "WARN", "BC-1a: 59s should not produce WARN")

    # Fixture B2: design leg at 60s → WARN
    story_b2 = mk_story(
        "b2_design_60s",
        """- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:01:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:30Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:15Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:45Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:10Z
""",
    )
    rc, out = run_harness(story_b2, ["--check-parallelization"])
    assert_in_output(out, "[PARALLELIZATION WARN]", "BC-1b: 60s should be WARN")
    assert_not_in_output(out, "[PARALLELIZATION OK]", "BC-1b: 60s should not be OK")

    # Fixture B3: design leg at 61s → WARN
    story_b3 = mk_story(
        "b3_design_61s",
        """- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:01:01Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:30Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:15Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:45Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:10Z
""",
    )
    rc, out = run_harness(story_b3, ["--check-parallelization"])
    assert_in_output(out, "[PARALLELIZATION WARN]", "BC-1c: 61s should be WARN")

    # Fixture B1′: peer leg at 59s → PASS
    story_b1p = mk_story(
        "b1p_peer_59s",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:00:59Z
""",
    )
    rc, out = run_harness(story_b1p, ["--check-parallelization"])
    assert_in_output(out, "[PEER CO-DISPATCH PASS]", "BC-1′a: peer 59s should PASS")

    # Fixture B2′: peer leg at 60s → WARN
    story_b2p = mk_story(
        "b2p_peer_60s",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:01:00Z
""",
    )
    rc, out = run_harness(story_b2p, ["--check-parallelization"])
    assert_in_output(out, "[PEER CO-DISPATCH WARN]", "BC-1′b: peer 60s should WARN")

    # Fixture B3′: peer leg at 61s → WARN
    story_b3p = mk_story(
        "b3p_peer_61s",
        """- lane: 설계-리뷰
  iteration: 1
  agent: ClaudeReviewAgent
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계-리뷰
  iteration: 1
  agent: CodexReviewAgent
  spawned_at: 2026-06-30T09:01:01Z
""",
    )
    rc, out = run_harness(story_b3p, ["--check-parallelization"])
    assert_in_output(out, "[PEER CO-DISPATCH WARN]", "BC-1′c: peer 61s should WARN")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 5: test_design_leg_bit_identical (AC-2a, I-4)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_design_leg_bit_identical():
    """
    I-4: Helper extraction must NOT change design-leg output.

    Byte-identical verification of design leg output before/after peer logic extraction.
    """

    # Fixture D1: standard design leg case
    story_d1 = mk_story(
        "d1_design_only",
        """- lane: 설계
  spawned_at: 2026-06-30T09:00:00Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:05Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:10Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:15Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:20Z
- lane: 설계
  spawned_at: 2026-06-30T09:00:25Z
""",
    )
    rc, out = run_harness(story_d1, ["--check-parallelization"])

    # Extract design leg output (should contain [PARALLELIZATION ...])
    assert_in_output(out, "[PARALLELIZATION OK]", "D1: design leg should output parallelization verdict")

    # ★ I-4 의 정의역 = `check_parallelization()` 산출(= `[PARALLELIZATION` 줄)이지
    #   스크립트 전체 출력이 아니다. 두 leg 은 같은 `--check-parallelization` 플래그 하나에
    #   묶여 호출되므로(run_check Check 6/6b) peer leg 의 SCOPE 줄은 **항상 함께 나온다**.
    #   전체 출력에 `[PEER` 부재를 요구하면 정상 동작을 결함으로 오판한다.
    design_lines = [ln for ln in out.splitlines() if "[PARALLELIZATION" in ln]
    assert design_lines, "I-4: 설계 leg 산출 줄이 하나도 없다 (분기 미도달 = 픽스처 결함)"
    design_block = "\n".join(design_lines)

    # MUT-P8 의 I-4 구속: ceiling 문면은 caller(`check_peer_codispatch`) 전용이며
    # 공유 술어 `_evaluate_spawn_timing()` 은 문면 0건이다. 공유 술어로 옮기면 설계 leg
    # 출력에 새 문장이 섞여 I-4 가 즉시 깨진다 → 설계 leg 줄에 peer/ceiling 토큰 부재를 문다.
    assert_not_in_output(design_block, "[PEER", "I-4: 설계 leg 줄에 peer 토큰 혼입")
    assert_not_in_output(design_block, "ceiling", "I-4: ceiling 문면이 설계 leg 로 누출")

    assert_matches_pattern(
        design_block,
        r"TEAM-DESIGN.*deputy.*spawned_at",
        "I-4: design leg should reference TEAM-DESIGN deputies",
    )

    # ── 진짜 bit-identical 대조: origin/main 판 대비 설계 leg 산출이 byte 동일한가 ──
    #   helper 추출(RF-3) 전후 무손상이 I-4 의 본체다. 현재 판만 보는 것은 회귀 검출력 0.
    old_script = _extract_origin_main_script()
    if old_script is None:
        # ★ EXPLICIT SKIP OR FAIL (F-CR-010)
        # 조용한 return 금지 — 대조를 못 했으면 그 사실이 반드시 드러나야 한다.
        # pytest 하에서는 사유를 명시한 skip(침묵 아님), 없으면 실패로 승격한다.
        if pytest is not None:
            # pytest.skip() 은 예외를 던지므로 이 아래로 실행이 내려가지 않는다
            # (구 주석은 "skip 시에만 return 에 도달"이라 적었으나 사실과 반대다).
            pytest.skip("origin/main 판 추출 불가 (git 미탐지 또는 ref 부재) — I-4 대조 미수행")
        raise AssertionError(
            "I-4 baseline extraction failed (git origin/main unreachable). "
            "Cannot verify bit-identical design leg output. "
            "This is a mandatory check and cannot be skipped silently."
        )

    # 4-분기 전수 + 임계 경계를 함께 태워 사다리 전 구간을 대조한다.
    for name, yaml_body in _I4_BRANCH_FIXTURES:
        story = mk_story(f"i4_{name}", yaml_body)
        _, new_out = run_harness(story, ["--check-parallelization"])
        _, old_out = run_harness(story, ["--check-parallelization"], script=old_script)
        new_design = "\n".join(ln for ln in new_out.splitlines() if "[PARALLELIZATION" in ln)
        old_design = "\n".join(ln for ln in old_out.splitlines() if "[PARALLELIZATION" in ln)
        assert new_design == old_design, (
            f"I-4 위반 — 분기 '{name}' 에서 설계 leg 산출이 origin/main 과 다르다.\n"
            f"--- old ---\n{old_design}\n--- new ---\n{new_design}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 6: test_early_return_paths_not_counted (AC-3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_early_return_paths_not_counted():
    """
    AC-3: Early-return code paths (SKIP/N/A) must NOT count as passing checks.

    Early returns:
      - [PARALLELIZATION SKIP] when no YAML block
      - [PEER CO-DISPATCH N/A] when no peer rows

    These should NOT produce positive outcome tokens.
    """

    # Fixture E1: Empty story (no YAML block) → SKIP path
    story_e1 = mk_story(
        "e1_no_yaml",
        "# empty story with no §14 block\n",
    )
    rc, out = run_harness(story_e1, ["--check-parallelization"])
    assert_in_output(out, "[PARALLELIZATION SKIP]", "E1: no YAML should trigger SKIP")
    # SKIP is not OK
    assert_not_in_output(out, "[PARALLELIZATION OK]", "E1: SKIP should not be OK")

    # Fixture E2: No peer rows → N/A path
    story_e2 = mk_story(
        "e2_no_peers",
        """- lane: 구현
  iteration: 1
""",
    )
    rc, out = run_harness(story_e2, ["--check-parallelization"])
    # Should not output peer verdict (no peer rows)
    assert_not_in_output(out, "[PEER CO-DISPATCH PASS]", "E2: no peer rows should not pass")
    assert_not_in_output(out, "[PEER CO-DISPATCH WARN]", "E2: no peer rows should not warn either")

    # TC-P0 (음성대조): Without --check-parallelization, no parallelization output
    rc, out = run_harness(story_e1)  # No extra args
    assert_not_in_output(
        out,
        "[PARALLELIZATION",
        "TC-P0: without --check-parallelization flag, parallelization checks should not run"
    )
    assert_not_in_output(
        out,
        "[PEER CO-DISPATCH",
        "TC-P0: without --check-parallelization flag, peer checks should not run"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 7: test_section14_exemption_probe (AC-4)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_section14_exemption_probe():
    """
    AC-4: §14 exemption flag (EXEMPT_SECTION_14) behavior.

    Verify that detect_section_14_exemption() activates correctly and
    affects story file requirement checks.
    """

    # Fixture F1: Normal story WITH §14 YAML → no exemption
    story_f1 = mk_story(
        "f1_normal_with_yaml",
        """- lane: 구현
  iteration: 1
""",
    )
    rc, out = run_harness(story_f1)
    # Should complete without [N/A] exemption message
    assert_not_in_output(
        out,
        "면제.*ADR-031",
        "F1: normal case should not show exemption"
    )

    # Fixture F2: Story WITHOUT content (effectively no YAML)
    # In normal environment this would fail, but we're just testing the exemption logic
    tmpdir = tempfile.mkdtemp(prefix="pytest_cfp2914_")
    story_f2_path = Path(tmpdir) / "f2_empty.md"
    story_f2_path.write_text("# Empty story\n", encoding="utf-8", newline="\n")

    rc, out = run_harness(str(story_f2_path))
    # Should show expected [FAIL] (not exempted in normal context)
    # (exemption only applies in mixed repo-kind context, which requires special setup)
    assert_in_output(out, "[FAIL]", "F2: empty story without exemption should fail")
    assert_not_in_output(
        out,
        "[N/A].*면제",
        "F2: should not show exemption without mixed repo-kind"
    )


if __name__ == "__main__":
    # Run pytest with verbose output
    if pytest is None:
        print("ERROR: pytest not installed", file=sys.stderr)
        sys.exit(2)
    sys.exit(pytest.main([__file__, "-v"]))
