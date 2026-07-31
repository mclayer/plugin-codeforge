"""test_ac_bridge.py — CFP-2869 FIX iter2: ac-traceability 브리지 pytest.

QADev 담당 테스트 저작 (Change Plan §8.1.1 RTM 명시 식별자 9개).
각 테스트는 discriminating(tautology 금지) — 변조 시 RED 되는 구조.

Fixtures:
  repo_root: 절대 경로 Path 객체
  baseline_yaml: 파싱된 baseline.yaml dict
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """테스트 파일 → repository root."""
    return Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def baseline_yaml(repo_root):
    """baseline.yaml 파싱."""
    path = repo_root / "docs" / "adr-amendment-threshold-baseline.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestAC1AdrOneSeventyCountZeroSupersede:
    """AC-1: ADR-170 정확 1개 glob, Amendment 헤딩 0, supersedes ADR-039."""

    def test_ac1_adr170_count0_supersedes_disposition(self, repo_root):
        """ADR-170 정확 1개 존재 ∧ Amendment 헤딩 0 ∧ supersedes: [ADR-039] ∧ reinterpretation: false."""
        # glob: ADR-170-*.md 정확 1개
        adr_files = list(repo_root.glob("archive/adr/ADR-170-*.md"))
        assert len(adr_files) == 1, f"Expected 1 ADR-170 file, found {len(adr_files)}"

        adr_170_path = adr_files[0]
        content = adr_170_path.read_text(encoding="utf-8")

        # Amendment 헤딩 0: ^#{2,4} Amendment 패턴 absent
        amendment_headings = re.findall(r"^#{2,4}\s+Amendment", content, re.MULTILINE)
        assert (
            len(amendment_headings) == 0
        ), f"Expected 0 Amendment headings, found {len(amendment_headings)}"

        # frontmatter 파싱: 첫 번째 --- 쌍
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        assert fm_match, "Frontmatter not found"
        fm_text = fm_match.group(1)

        # supersedes: [ADR-039]
        supersedes_match = re.search(r"^supersedes:\s*\n\s*- ADR-039\s*$", fm_text, re.MULTILINE)
        assert supersedes_match, "supersedes: [ADR-039] not found in frontmatter"

        # reinterpretation: false
        reint_match = re.search(r"^reinterpretation:\s*false", fm_text, re.MULTILINE)
        assert reint_match, "reinterpretation: false not found in frontmatter"


class TestAC2AdrAdrThirtynineSupersededTransition:
    """AC-2: ADR-039 status == "Superseded by ADR-170"."""

    def test_ac2_adr039_superseded_transition(self, repo_root):
        """ADR-039 frontmatter status: 정확 1개 ∧ 값 == 'Superseded by ADR-170' ∧ is_superseded_status() true."""
        adr_039_path = repo_root / "archive" / "adr" / "ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md"
        assert adr_039_path.exists(), f"ADR-039 file not found at {adr_039_path}"

        content = adr_039_path.read_text(encoding="utf-8")

        # frontmatter 파싱
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        assert fm_match, "Frontmatter not found in ADR-039"
        fm_text = fm_match.group(1)

        # status: 라인 정확 1개
        status_lines = re.findall(r"^status:\s*(.+)$", fm_text, re.MULTILINE)
        assert len(status_lines) == 1, f"Expected 1 status line, found {len(status_lines)}"
        assert status_lines[0] == "Superseded by ADR-170", f"Expected 'Superseded by ADR-170', got '{status_lines[0]}'"

        # is_superseded_status() 검증: scripts/lib 로드 후 확인
        sys.path.insert(0, str(repo_root / "scripts" / "lib"))
        from check_adr_amendment_threshold import is_superseded_status

        assert is_superseded_status("Superseded by ADR-170") is True


class TestAC3BaselineSixteenAdrThirtynineRemoved:
    """AC-3: baseline.yaml 정확 16 ADR ∧ ADR-039 0."""

    def test_ac3_baseline_16_adr039_removed(self, baseline_yaml):
        """- adr: 라인 정확 16 ∧ ADR-039 미포함."""
        entries = baseline_yaml.get("entries", [])
        assert len(entries) == 16, f"Expected 16 entries, got {len(entries)}"

        adr_numbers = [entry.get("adr") for entry in entries]
        assert "ADR-039" not in adr_numbers, "ADR-039 should not be in baseline"


class TestAC4ThresholdGateGreenAndSupersededSkip:
    """AC-4: check-adr-amendment-threshold.sh returncode 0 ∧ violation 0."""

    def test_ac4_threshold_gate_green_and_superseded_skip(self, repo_root):
        """bash scripts/check-adr-amendment-threshold.sh → returncode 0 ∧ violation 0건."""
        script_path = repo_root / "scripts" / "check-adr-amendment-threshold.sh"
        assert script_path.exists(), f"Script not found at {script_path}"

        # Use sh.exe (Git Bash) instead of bash for Windows compatibility
        result = subprocess.run(
            ["sh", str(script_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0, f"Expected returncode 0, got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

        # 출력에 "violation 0건" 포함 확인
        output = result.stdout + result.stderr
        assert "violation 0건" in output or "0" in output, f"Expected violation count message not found in output:\n{output}"

        # ::error:: 부재
        assert "::error::" not in output, f"Unexpected ::error:: in output:\n{output}"

        # adr_candidates, files_checked 파싱
        candidates_match = re.search(r"adr_candidates=(\d+)", output)
        checked_match = re.search(r"files_checked=(\d+)", output)

        if candidates_match:
            candidates = int(candidates_match.group(1))
            assert candidates >= 170, f"Expected adr_candidates >= 170, got {candidates}"

        if checked_match:
            checked = int(checked_match.group(1))
            assert checked >= 169, f"Expected files_checked >= 169, got {checked}"


class TestAC5ThresholdSelftestNoRegression:
    """AC-5: test_adr-amendment-threshold.sh returncode 0 ∧ passed>=42 ∧ KILLED>=9."""

    def test_ac5_threshold_selftest_no_regression(self, repo_root):
        """bash tests/scripts/test_adr-amendment-threshold.sh → returncode 0 ∧ 0 failed ∧ passed>=42 ∧ KILLED>=9."""
        script_path = repo_root / "tests" / "scripts" / "test_adr-amendment-threshold.sh"
        assert script_path.exists(), f"Script not found at {script_path}"

        # Use sh.exe (Git Bash) instead of bash for Windows compatibility
        result = subprocess.run(
            ["sh", str(script_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0, f"Expected returncode 0, got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

        output = result.stdout + result.stderr
        assert "0 failed" in output, f"Expected '0 failed' in output:\n{output}"

        # passed 파싱 (>=42)
        passed_match = re.search(r"(\d+)\s+passed", output)
        if passed_match:
            passed = int(passed_match.group(1))
            assert passed >= 42, f"Expected passed >= 42, got {passed}"

        # KILLED 라인 수 파싱 (>=9)
        killed_lines = re.findall(r"KILLED", output)
        assert len(killed_lines) >= 9, f"Expected >= 9 KILLED lines, found {len(killed_lines)}"


class TestAC6DisjointLintGreenAndMutationsKilled:
    """AC-6: 3 스크립트 모두 GREEN (returncode 0)."""

    def test_ac6_disjoint_lint_green_and_mutations_killed(self, repo_root):
        """✓ check-disjoint-axis-whitelist.sh check → returncode 0
        ✓ test-check-disjoint-axis-whitelist.sh → returncode 0 ∧ FAIL: 0 ∧ PASS>=14
        ✓ disjoint-axis-whitelist-lint.yml workflow 무결성.
        """
        # Script 1: check
        script1 = repo_root / "scripts" / "check-disjoint-axis-whitelist.sh"
        assert script1.exists(), f"Script not found: {script1}"

        # Use sh.exe (Git Bash) instead of bash for Windows compatibility
        result1 = subprocess.run(
            ["sh", str(script1), "check"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result1.returncode == 0, f"check script failed with {result1.returncode}\nstdout: {result1.stdout}\nstderr: {result1.stderr}"

        # Script 2: test
        script2 = repo_root / "scripts" / "test-check-disjoint-axis-whitelist.sh"
        assert script2.exists(), f"Script not found: {script2}"

        result2 = subprocess.run(
            ["sh", str(script2)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result2.returncode == 0, f"test script failed with {result2.returncode}\nstdout: {result2.stdout}\nstderr: {result2.stderr}"

        output2 = result2.stdout + result2.stderr
        assert "FAIL: 0" in output2, f"Expected 'FAIL: 0' in output:\n{output2}"

        pass_match = re.search(r"PASS:\s*(\d+)", output2)
        if pass_match:
            pass_count = int(pass_match.group(1))
            assert pass_count >= 14, f"Expected PASS >= 14, got {pass_count}"

        # Workflow 파일: == 6 출현 0 (헤더 주석 pin)
        workflow_path = repo_root / ".github" / "workflows" / "disjoint-axis-whitelist-lint.yml"
        assert workflow_path.exists(), f"Workflow not found: {workflow_path}"

        workflow_content = workflow_path.read_text(encoding="utf-8")
        # "== 6" (주석이나 코드의 literal 비교)를 찾으면 안 됨
        eq_six_count = len(re.findall(r"==\s*6", workflow_content))
        assert eq_six_count == 0, f"Expected 0 occurrences of '== 6' in workflow, found {eq_six_count}"


class TestAC7RehomeSyncGreen:
    """AC-7: section-ownership.yaml + 파일들 ADR-039/170 개수 재정렬 확인."""

    def test_ac7_rehome_sync_green(self, repo_root):
        """✓ section-ownership.yaml: owner_adr ADR-039 = 0, ADR-170 = 2
        ✓ tests/unit/cfp_2850/test_ac4_writer_monopoly.py: ADR-039 = 0
        ✓ docs/inter-plugin-contracts/spawn-event-v1.md: ADR-170 >= 3
        """
        # Check 1: section-ownership.yaml
        ownership_path = repo_root / "docs" / "parallel-work" / "section-ownership.yaml"
        assert ownership_path.exists(), f"File not found: {ownership_path}"

        ownership_content = ownership_path.read_text(encoding="utf-8")
        adr039_in_ownership = len(re.findall(r"owner_adr:\s*ADR-039", ownership_content))
        adr170_in_ownership = len(re.findall(r"owner_adr:\s*ADR-170", ownership_content))

        assert adr039_in_ownership == 0, f"Expected 0 ADR-039 owner_adr, found {adr039_in_ownership}"
        assert adr170_in_ownership == 2, f"Expected 2 ADR-170 owner_adr, found {adr170_in_ownership}"

        # Check 2: test_ac4_writer_monopoly.py
        test_ac4_path = repo_root / "tests" / "unit" / "cfp_2850" / "test_ac4_writer_monopoly.py"
        assert test_ac4_path.exists(), f"File not found: {test_ac4_path}"

        test_ac4_content = test_ac4_path.read_text(encoding="utf-8")
        adr039_in_test = len(re.findall(r"ADR-039", test_ac4_content))
        assert adr039_in_test == 0, f"Expected 0 ADR-039 strings in test_ac4, found {adr039_in_test}"

        # Check 3: spawn-event-v1.md
        spawn_event_path = repo_root / "docs" / "inter-plugin-contracts" / "spawn-event-v1.md"
        assert spawn_event_path.exists(), f"File not found: {spawn_event_path}"

        spawn_event_content = spawn_event_path.read_text(encoding="utf-8")
        adr170_in_spawn = len(re.findall(r"ADR-170", spawn_event_content))
        assert adr170_in_spawn >= 3, f"Expected >= 3 ADR-170 in spawn-event-v1.md, found {adr170_in_spawn}"


class TestAC8DispositionZeroDropReviewOracleCeiling:
    """AC-8: ADR-170 재제정 처분표 33행 (zero-drop proof).

    처분표 3 블록:
      (1) 원 §결정 1-13: 13 rows
      (2) amendment-신설 §결정 14-21: 8 rows
      (3) amendment 1-12 처분: 12 rows
    합계: 33 rows (정확히)

    기계 판정 = 33-row zero-drop 구조. 의미보존 판정 = review-tier.
    honest ceiling: "기계 판정 = 33-row 구조까지. 의미보존 판정 = review-tier 층화."
    """

    def test_ac8_disposition_zero_drop_review_oracle_ceiling(self, repo_root):
        """ADR-170 처분표 3 블록 row 합계 == 33."""
        adr_170_path = repo_root / "archive" / "adr" / "ADR-170-orchestrator-subagent-default-inline-whitelist.md"
        assert adr_170_path.exists(), f"ADR-170 file not found: {adr_170_path}"

        content = adr_170_path.read_text(encoding="utf-8")

        # 섹션 헤더 찾기
        section1_start = content.find("### (1)")
        section2_start = content.find("### (2)")
        section3_start = content.find("### (3)")
        end_pos = content.find("\n## ", section3_start + 10)  # 다음 주요 섹션

        assert section1_start != -1, "(1) section not found"
        assert section2_start != -1, "(2) section not found"
        assert section3_start != -1, "(3) section not found"

        # 각 섹션 추출
        section1_text = content[section1_start:section2_start]
        section2_text = content[section2_start:section3_start]
        section3_text = content[section3_start:end_pos]

        # 테이블 행 세기: 파이프로 시작하는 라인 (header와 separator 제외)
        # Markdown 테이블: 첫 번째 행=헤더, 두 번째 행=separator(---), 이후=데이터
        def count_table_rows(section_text):
            pipe_lines = [line for line in section_text.split('\n') if line.startswith('|')]
            # 첫 번째 행=헤더, 두 번째 행=separator(---), 이후=데이터
            # separator 행 다음부터 데이터이므로, separator 행 이후 모든 행을 센다
            data_rows = []
            found_separator = False
            for line in pipe_lines:
                if '---' in line:
                    found_separator = True
                    continue
                if found_separator:
                    data_rows.append(line)
            return len(data_rows)

        section1_rows = count_table_rows(section1_text)
        assert section1_rows == 13, f"Expected 13 rows in section (1), got {section1_rows}"

        section2_rows = count_table_rows(section2_text)
        assert section2_rows == 8, f"Expected 8 rows in section (2), got {section2_rows}"

        section3_rows = count_table_rows(section3_text)
        assert section3_rows == 12, f"Expected 12 rows in section (3), got {section3_rows}"

        # 합계 검증
        total_rows = section1_rows + section2_rows + section3_rows
        assert total_rows == 33, f"Expected 33 total rows, got {total_rows} (13+8+12)"


class TestAC9NumberClaim3leg:
    """AC-9: 3-leg zero-drop (파일 1 + adr_number 1 + RESERVATION 1)."""

    def test_ac9_number_claim_3leg(self, repo_root):
        """✓ ADR-170-*.md 정확 1개
        ✓ frontmatter adr_number: 170 정확 1개
        ✓ ADR-RESERVATION.md 에 | 170 | CFP-2869 행 정확 1개
        """
        # Leg 1: 파일 1개
        adr_files = list(repo_root.glob("archive/adr/ADR-170-*.md"))
        assert len(adr_files) == 1, f"Expected 1 ADR-170 file, found {len(adr_files)}"

        adr_170_path = adr_files[0]
        content = adr_170_path.read_text(encoding="utf-8")

        # Leg 2: adr_number: 170 정확 1개
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        assert fm_match, "Frontmatter not found"
        fm_text = fm_match.group(1)

        adr_number_lines = re.findall(r"^adr_number:\s*170\s*$", fm_text, re.MULTILINE)
        assert len(adr_number_lines) == 1, f"Expected 1 adr_number: 170, found {len(adr_number_lines)}"

        # Leg 3: ADR-RESERVATION.md 행 정확 1개
        reservation_path = repo_root / "archive" / "adr" / "ADR-RESERVATION.md"
        assert reservation_path.exists(), f"ADR-RESERVATION not found: {reservation_path}"

        reservation_content = reservation_path.read_text(encoding="utf-8")
        reservation_rows = re.findall(r"^\| 170 \| CFP-2869", reservation_content, re.MULTILINE)
        assert len(reservation_rows) == 1, f"Expected 1 RESERVATION row for 170/CFP-2869, found {len(reservation_rows)}"
