"""
test_check_claude_md_amendment_ref.py — CFP-1372 regression test

scripts/lib/check_claude_md_amendment_ref.py 의 line-wide regex precision 회귀 테스트.

Bug (CFP-1372): line-wide nested-loop pairing 으로 인해 동일 line 안 다수의 ADR link
mention + 다수 Amendment claim 조합에서 cross-section mis-attribution 발생. 특히 link
text 가 "ADR-NNN" 이 아닌 설명적 link 형태 (예: "[Write-time self-write verification
mandate](docs/adr/ADR-082-...md)") 가 section divider 로 인식되지 못해, 선행 [ADR-101]
link 이 후행 ADR-082 paragraph 의 Amendment claim 까지 모두 attribute 했다.

Fix: link 의 URL target 이 ADR file 인 모든 markdown link 을 section anchor 로 인식
(link text 무관). 각 link 의 attribution scope = 그 link 다음부터 다음 link 직전까지.

본 테스트는 subprocess 패턴 (CFP-827 test 답습) 으로 fixture cwd 안에서:
  - CLAUDE.md (L282 reproducer + 단순 attribution case)
  - docs/adr/ADR-NNN-*.md (frontmatter amendment_log 길이 조작)
2 종을 임시로 구성한 뒤 script 의 stdout / exit code 를 검증한다.
"""

import subprocess
import sys
import textwrap
from pathlib import Path


_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "lib" / "check_claude_md_amendment_ref.py"


def _write_adr(adr_dir: Path, adr_num: int, amendment_count: int) -> None:
    """Build minimal ADR-NNN-stub.md with amendment_log of given length."""
    adr_dir.mkdir(parents=True, exist_ok=True)
    fm_head = (
        "---\n"
        f"id: ADR-{adr_num:03d}\n"
        f"title: Fixture ADR {adr_num}\n"
        "status: Accepted\n"
    )
    if amendment_count == 0:
        log_body = "amendment_log: []\n"
    else:
        items_lines = []
        for i in range(1, amendment_count + 1):
            items_lines.append(f"  - amendment: {i}")
            items_lines.append(f"    cfp: CFP-FIXTURE-{i}")
            items_lines.append(f"    date: 2026-01-01")
        log_body = "amendment_log:\n" + "\n".join(items_lines) + "\n"
    body = fm_head + log_body + "---\n\n" + f"# ADR-{adr_num:03d} fixture body.\n"
    (adr_dir / f"ADR-{adr_num:03d}-fixture.md").write_text(body, encoding="utf-8")


def _run_script(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--claude-md",
            str(root / "CLAUDE.md"),
            "--adr-dir",
            str(root / "docs" / "adr"),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class TestCFP1372RegexPrecision:
    """CFP-1372 — line-wide nested-loop pairing → section-split attribution 회귀."""

    def test_super_long_line_cross_section_no_false_positive(self, tmp_path):
        """TC-1 (regression): CLAUDE.md L282 reproducer — ADR-101 link 다음에 다른 ADR-082 link
        section 의 Amendment 1/2 claim 이 trailing 으로 등장.

        Fix 전: ADR-101 attribute → false-positive 2건 (ADR-101 claims Amendment 1 / 2).
        Fix 후: ADR-082 attribute (URL-target 기반 link 인식 으로 section 정확히 분리).
        """
        # ADR-101 = amendment_log 0 (실제 CLAUDE.md ADR-101 상태)
        _write_adr(tmp_path / "docs" / "adr", 101, 0)
        # ADR-082 = amendment_log 12 (실제 ADR-082 상태 모사)
        _write_adr(tmp_path / "docs" / "adr", 82, 12)

        # 실제 L282 패턴 (축약). 핵심: 한 line 안에 [ADR-101](...) link + 그 뒤에
        # [<설명적 text>](docs/adr/ADR-082-...md) link + ADR-082 Amendment 1/2 claim.
        long_line = (
            "**Verify-before-trust 4-layer governance**: "
            "[ADR-101](docs/adr/ADR-101-verify-before-trust-confluence-rest.md) "
            "(CFP-1226) = sub-domain; "
            "**(3) ADR-082** [Write-time self-write verification mandate]"
            "(docs/adr/ADR-082-write-time-self-write-verification-mandate.md) "
            "(CFP-776) — scope a-d. "
            "**Amendment 1 (CFP-841) behavioral→mechanical 전환**: scope 2(a). "
            "**Amendment 2 (CFP-1016)** = §결정 1 layer 1 verify."
        )
        (tmp_path / "CLAUDE.md").write_text(long_line + "\n", encoding="utf-8")

        result = _run_script(tmp_path)

        # ADR-101 false-positive 0 건 (root-fix invariant)
        assert "ADR-101 claims Amendment" not in result.stdout, (
            f"ADR-101 false-positive 재발 (CFP-1372 regression):\n"
            f"stdout={result.stdout}"
        )
        # ADR-082 Amendment 1, 2 attribute 됨 (둘 다 ADR-082 amendment_log 12 안에 포함 → OK)
        assert "ADR-082 Amendment 1" in result.stdout, (
            f"ADR-082 Amendment 1 attribution 누락:\nstdout={result.stdout}"
        )
        assert "ADR-082 Amendment 2" in result.stdout, (
            f"ADR-082 Amendment 2 attribution 누락:\nstdout={result.stdout}"
        )

    def test_simple_link_amendment_pair_still_works(self, tmp_path):
        """TC-2 (regression-guard): 단순 line `**[ADR-040](...) Amendment 6 (CFP-N)**` 정상 attribute.

        Fix 가 기본 same-line pairing 을 깨뜨리지 않는지 검증.
        """
        _write_adr(tmp_path / "docs" / "adr", 40, 6)

        simple_line = (
            "- **Worktree convention "
            "[ADR-040](docs/adr/ADR-040-worktree-convention.md) "
            "Amendment 6 (CFP-843)**: scope expansion."
        )
        (tmp_path / "CLAUDE.md").write_text(simple_line + "\n", encoding="utf-8")

        result = _run_script(tmp_path)
        assert result.returncode == 0, (
            f"단순 line 정상 case 가 non-zero exit:\n"
            f"exit={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "ADR-040 Amendment 6" in result.stdout, (
            f"ADR-040 Amendment 6 OK attribution 누락:\nstdout={result.stdout}"
        )
        assert "[OK]" in result.stdout, (
            f"OK marker 누락 — claim/actual mismatch 의심:\nstdout={result.stdout}"
        )

    def test_paragraph_with_cross_ref_bare_mention_preserves_attribution(self, tmp_path):
        """TC-3 (regression-guard): paragraph 안 bare-form ADR cross-ref (예: "ADR-068 정합")
        는 section divider 로 작동하지 않아야 한다. main link ADR 의 trailing Amendment claim
        이 끊기지 않고 정확히 그 main link ADR 에 attribute 되어야 함 (L275 패턴).
        """
        _write_adr(tmp_path / "docs" / "adr", 65, 4)

        paragraph_line = (
            "**Self-check 의무** = "
            "[ADR-065](docs/adr/ADR-065-architect-phase1-mechanical-self-check.md) "
            "— ArchitectAgent self-check. ADR-008 정합 정합, ADR-068 cross-ref. "
            "**+ Amendment 4 (CFP-1242)** — §결정 1 표 10th item."
        )
        (tmp_path / "CLAUDE.md").write_text(paragraph_line + "\n", encoding="utf-8")

        result = _run_script(tmp_path)
        assert "ADR-065 Amendment 4" in result.stdout, (
            f"L275 패턴 attribution 회귀 (bare cross-ref 가 section 끊음):\n"
            f"stdout={result.stdout}"
        )
        assert "[OK]" in result.stdout, (
            f"OK marker 누락:\nstdout={result.stdout}"
        )
        assert result.returncode == 0, (
            f"unexpected non-zero exit:\n"
            f"exit={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
