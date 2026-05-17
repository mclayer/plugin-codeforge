#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-894 inter-plugin-contracts-parity lint fixtures — TC-1..TC-7.

Test fixtures for check_inter_plugin_contracts_parity.py validation:
  TC-1: clean parity (MANIFEST == frontmatter) → PASS
  TC-2: parity drift (MANIFEST > frontmatter) → FAIL
  TC-3: parity drift (MANIFEST < frontmatter) → FAIL
  TC-4: frontmatter missing contract_version field → FAIL
  TC-5: Archived contract version mismatch → IGNORED (Active only)
  TC-6: MANIFEST.yaml absent → graceful skip exit 0
  TC-7: file missing (MANIFEST orphan) → skip silently (separation of concerns)

Framework: pytest (ADR-061 §결정 1 + Amendment 1 §결정 6.A)
"""
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_inter_plugin_contracts_parity.py"


def _run_lint(cwd: Path) -> tuple[int, str, str]:
    """Run parity lint with cwd, capture (exit_code, stdout, stderr)."""
    result = subprocess.run(
        ["python3", str(LINT_SCRIPT)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def _make_contracts_dir(tmp_path: Path) -> Path:
    """Create docs/inter-plugin-contracts/ directory."""
    d = tmp_path / "docs" / "inter-plugin-contracts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_manifest(contracts_dir: Path, manifest_yaml: str) -> Path:
    p = contracts_dir / "MANIFEST.yaml"
    p.write_text(manifest_yaml, encoding="utf-8")
    return p


def _write_contract_file(
    contracts_dir: Path, fname: str, contract_version: str | None
) -> Path:
    if contract_version is None:
        fm = ""
    else:
        fm = f"""---
kind: contract
contract_version: "{contract_version}"
status: Active
related_plugins:
  - codeforge
related_adrs:
  - ADR-008
authors:
  - CFP-TEST
---
"""
    body = "# Test contract\n\n## 1. 흐름 개요\n\nTest body.\n"
    (contracts_dir / fname).write_text(fm + body, encoding="utf-8")
    return contracts_dir / fname


# ─── TC-1: clean parity (MANIFEST == frontmatter) → PASS ───
class TestTC1CleanParity:
    def test_active_contract_versions_match_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: test_contract
    files:
      - { file: test-contract-v1.md, contract_version: "1.5", status: Active }
""",
            )
            _write_contract_file(d, "test-contract-v1.md", "1.5")
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, f"clean parity → exit 0 expected. stdout={stdout} stderr={stderr}"


# ─── TC-2: parity drift (MANIFEST > frontmatter) → FAIL ───
class TestTC2DriftManifestAhead:
    def test_manifest_ahead_of_frontmatter_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: test_contract
    files:
      - { file: test-contract-v1.md, contract_version: "1.5", status: Active }
""",
            )
            _write_contract_file(d, "test-contract-v1.md", "1.0")
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, "MANIFEST=1.5 vs frontmatter=1.0 → FAIL expected"
            assert "INV-1 parity drift" in stderr, f"INV-1 drift msg expected: {stderr}"
            assert "1.5" in stderr and "1.0" in stderr, f"both versions in stderr: {stderr}"


# ─── TC-3: parity drift (MANIFEST < frontmatter) → FAIL ───
class TestTC3DriftFrontmatterAhead:
    def test_frontmatter_ahead_of_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: test_contract
    files:
      - { file: test-contract-v1.md, contract_version: "1.0", status: Active }
""",
            )
            _write_contract_file(d, "test-contract-v1.md", "1.5")
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, "MANIFEST=1.0 vs frontmatter=1.5 → FAIL expected"
            assert "INV-1 parity drift" in stderr


# ─── TC-4: frontmatter missing contract_version field → FAIL ───
class TestTC4FrontmatterMissingVersion:
    def test_absent_frontmatter_version_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: test_contract
    files:
      - { file: test-contract-v1.md, contract_version: "1.0", status: Active }
""",
            )
            # Write file with frontmatter that lacks contract_version
            (d / "test-contract-v1.md").write_text(
                """---
kind: contract
status: Active
---

# Test
""",
                encoding="utf-8",
            )
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, "frontmatter contract_version 부재 → FAIL expected"
            assert "frontmatter contract_version 필드 부재" in stderr


# ─── TC-5: Archived contract version mismatch → IGNORED ───
class TestTC5ArchivedIgnored:
    def test_archived_contract_mismatch_passes(self) -> None:
        """Archived contracts MUST NOT be parity-checked (historical record)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: test_contract
    files:
      - { file: test-contract-v1.md, contract_version: "1.0", status: Archived }
      - { file: test-contract-v2.md, contract_version: "2.5", status: Active }
""",
            )
            _write_contract_file(d, "test-contract-v1.md", "9.9")  # mismatch
            _write_contract_file(d, "test-contract-v2.md", "2.5")  # match Active
            rc, stdout, _ = _run_lint(tmp_path)
            assert rc == 0, (
                f"Archived contract mismatch must be IGNORED (only Active checked). stdout={stdout}"
            )


# ─── TC-6: MANIFEST.yaml absent → graceful skip exit 0 ───
class TestTC6GracefulSkipOnMissingManifest:
    def test_no_manifest_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            _make_contracts_dir(tmp_path)
            # No MANIFEST.yaml written
            rc, _, stderr = _run_lint(tmp_path)
            assert rc == 0, "MANIFEST absent → graceful skip exit 0 expected"
            assert "SKIP" in stderr, f"SKIP message expected: {stderr}"

    def test_no_contracts_dir_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Don't create docs/inter-plugin-contracts/ at all
            rc, _, stderr = _run_lint(tmp_path)
            assert rc == 0, "contracts/ absent → graceful skip exit 0 expected"


# ─── TC-7: file missing (MANIFEST orphan) → skip silently (separation of concerns) ───
class TestTC7MissingFileSilentSkip:
    def test_orphan_manifest_entry_silently_skipped(self) -> None:
        """MANIFEST.yaml references a file that doesn't exist on disk. INV-1 parity check
        cannot evaluate parity for missing file — silently skip (separation of concerns:
        MANIFEST completeness is check_inter_plugin_contracts.py CFP-42 job, not parity job).
        Other Active contracts MUST still be checked."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: orphan_contract
    files:
      - { file: orphan-v1.md, contract_version: "1.0", status: Active }
  - name: real_contract
    files:
      - { file: real-v1.md, contract_version: "2.0", status: Active }
""",
            )
            # orphan-v1.md NOT written; real-v1.md written with matching version
            _write_contract_file(d, "real-v1.md", "2.0")
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, (
                f"orphan entry should be silently skipped + real entry PASS. "
                f"stdout={stdout} stderr={stderr}"
            )
            assert "1 Active contract file checked" in stdout, (
                f"only 1 file (real-v1.md) should be parity-checked: {stdout}"
            )


# ─── TC-7b: thin-wrapper conformance ───
class TestThinWrapperConformance:
    def test_thin_wrapper_exec_pattern(self) -> None:
        """thin wrapper sh = exec python3 lib/...py 패턴 정합 (ADR-061 §결정 1)."""
        wrapper = REPO_ROOT / "scripts" / "check-inter-plugin-contracts-parity.sh"
        assert wrapper.exists(), f"thin wrapper not found: {wrapper}"
        content = wrapper.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        assert any(
            "exec python3" in line and "check_inter_plugin_contracts_parity.py" in line
            for line in lines
        ), f"thin wrapper must contain 'exec python3 ... check_inter_plugin_contracts_parity.py'"
        assert len(lines) <= 7, f"thin wrapper ≤ 7 non-comment lines (ADR-061): {len(lines)}"
