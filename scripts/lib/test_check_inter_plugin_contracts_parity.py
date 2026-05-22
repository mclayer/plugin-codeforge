#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-894 / CFP-1242 inter-plugin-contracts-parity lint fixtures — TC-1..TC-12.

Test fixtures for check_inter_plugin_contracts_parity.py validation:
  TC-1: clean parity (MANIFEST == frontmatter) → PASS
  TC-2: parity drift (MANIFEST > frontmatter) → FAIL
  TC-3: parity drift (MANIFEST < frontmatter) → FAIL
  TC-4: frontmatter missing contract_version field → FAIL
  TC-5: Archived contract version mismatch → IGNORED (Active only)
  TC-6: MANIFEST.yaml absent → graceful skip exit 0
  TC-7: file missing (MANIFEST orphan) → skip silently (separation of concerns)

CFP-1242 — INV-1 parity scope expansion to kind:registry (`registries` section,
`version` field). MANIFEST `registries` 섹션은 그동안 lint iteration gap 으로 무방비
(label_registry 7-row 누적 parallel-session append drift 가 S4 에서 human review 까지 도달):
  TC-8: registries clean parity (frontmatter version ∈ Active MANIFEST rows) → PASS
  TC-9: registries drift (frontmatter version absent from Active rows) → FAIL  ← live label_registry 결함 재현
  TC-10: registries multi-Active membership (frontmatter version IS one of N Active rows) → PASS
  TC-11: registries Sunsetted/Archived rows ignored (non-Active) → PASS
  TC-12: registries frontmatter missing `version` field → FAIL

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


def _write_registry_file(
    contracts_dir: Path, fname: str, version: str | None, status: str = "Active"
) -> Path:
    """Write a kind:registry doc — uses `version` frontmatter field (NOT contract_version)."""
    if version is None:
        fm = f"""---
kind: registry
status: {status}
---
"""
    else:
        fm = f"""---
kind: registry
version: "{version}"
status: {status}
related_plugins:
  - codeforge
related_adrs:
  - ADR-010
authors:
  - CFP-TEST
---
"""
    body = "# Test registry\n\n## 1. 개요\n\nTest registry body.\n"
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
            assert "1 Active file checked" in stdout, (
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


# ═══════════════════════════════════════════════════════════════════════════
# CFP-1242 — INV-1 parity scope expansion to kind:registry (`registries` section)
# ═══════════════════════════════════════════════════════════════════════════


# ─── TC-8: registries clean parity (frontmatter version == Active MANIFEST row) → PASS ───
class TestTC8RegistryCleanParity:
    def test_active_registry_version_match_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """registries:
  - name: test_registry
    files:
      - { file: test-registry-v1.md, version: "2.50", status: Active }
""",
            )
            _write_registry_file(d, "test-registry-v1.md", "2.50")
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, f"clean registry parity → exit 0. stdout={stdout} stderr={stderr}"


# ─── TC-9: registries drift (frontmatter version absent from Active rows) → FAIL ───
#         (label_registry live defect 재현: file=2.50 but MANIFEST Active rows = 2.43..2.49)
class TestTC9RegistryDriftLiveDefect:
    def test_frontmatter_version_absent_from_active_rows_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            # 7 mis-ordered Active rows (parallel-session append drift), 2.50 ABSENT
            _write_manifest(
                d,
                """registries:
  - name: label_registry
    files:
      - { file: label-registry-v1.md, version: "1.5", status: Archived }
      - { file: label-registry-v2.md, version: "2.43", status: Active }
      - { file: label-registry-v2.md, version: "2.44", status: Active }
      - { file: label-registry-v2.md, version: "2.45", status: Active }
      - { file: label-registry-v2.md, version: "2.49", status: Active }
      - { file: label-registry-v2.md, version: "2.48", status: Active }
      - { file: label-registry-v2.md, version: "2.47", status: Active }
      - { file: label-registry-v2.md, version: "2.46", status: Active }
""",
            )
            _write_registry_file(d, "label-registry-v2.md", "2.50")
            _write_registry_file(d, "label-registry-v1.md", "1.5", status="Archived")
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, "frontmatter=2.50 absent from Active MANIFEST rows → FAIL expected"
            assert "INV-1 parity drift" in stderr, f"INV-1 drift msg expected: {stderr}"
            assert "2.50" in stderr, f"frontmatter version 2.50 in stderr: {stderr}"


# ─── TC-10: registries multi-Active membership (frontmatter version IS one of N Active rows) → PASS ───
class TestTC10RegistryMultiActiveMembership:
    def test_frontmatter_version_member_of_active_rows_passes(self) -> None:
        """Membership semantic: when MANIFEST has multiple Active rows for a file, the
        frontmatter version need only APPEAR among them (parallel-append tolerant)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """registries:
  - name: label_registry
    files:
      - { file: label-registry-v2.md, version: "2.48", status: Active }
      - { file: label-registry-v2.md, version: "2.49", status: Active }
      - { file: label-registry-v2.md, version: "2.50", status: Active }
""",
            )
            _write_registry_file(d, "label-registry-v2.md", "2.50")  # IS a member
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, (
                f"frontmatter 2.50 ∈ {{2.48,2.49,2.50}} Active rows → PASS. "
                f"stdout={stdout} stderr={stderr}"
            )


# ─── TC-11: registries non-Active rows (Sunsetted/Archived) ignored ───
class TestTC11RegistryNonActiveIgnored:
    def test_sunsetted_and_archived_registry_rows_ignored(self) -> None:
        """Sunsetted/Archived registry rows MUST NOT be parity-checked (mirrors contracts TC-5).
        reconcile-protocol-v1 (Sunsetted) + label-registry-v1 (Archived) live precedent."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """registries:
  - name: reconcile_protocol
    files:
      - { file: reconcile-protocol-v1.md, version: "1.14", status: Sunsetted }
  - name: legacy_registry
    files:
      - { file: legacy-v1.md, version: "1.0", status: Archived }
  - name: active_registry
    files:
      - { file: active-v1.md, version: "3.0", status: Active }
""",
            )
            _write_registry_file(d, "reconcile-protocol-v1.md", "9.9", status="Sunsetted")  # mismatch
            _write_registry_file(d, "legacy-v1.md", "8.8", status="Archived")  # mismatch
            _write_registry_file(d, "active-v1.md", "3.0", status="Active")  # match
            rc, stdout, _ = _run_lint(tmp_path)
            assert rc == 0, (
                f"Sunsetted/Archived registry mismatch must be IGNORED (only Active checked). "
                f"stdout={stdout}"
            )


# ─── TC-12: registries frontmatter missing `version` field → FAIL ───
class TestTC12RegistryMissingVersionField:
    def test_absent_registry_version_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """registries:
  - name: test_registry
    files:
      - { file: test-registry-v1.md, version: "1.0", status: Active }
""",
            )
            _write_registry_file(d, "test-registry-v1.md", None)  # no version field
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, "registry frontmatter version 부재 → FAIL expected"
            assert "version 필드 부재" in stderr, f"missing version field msg expected: {stderr}"


# ─── TC-13: contracts + registries both checked (no contract regression) ───
class TestTC13ContractsAndRegistriesCoexist:
    def test_both_sections_checked_no_regression(self) -> None:
        """A MANIFEST with BOTH contracts and registries: both clean → PASS, count reflects both."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            d = _make_contracts_dir(tmp_path)
            _write_manifest(
                d,
                """contracts:
  - name: test_contract
    files:
      - { file: test-contract-v1.md, contract_version: "1.5", status: Active }
registries:
  - name: test_registry
    files:
      - { file: test-registry-v1.md, version: "2.50", status: Active }
""",
            )
            _write_contract_file(d, "test-contract-v1.md", "1.5")
            _write_registry_file(d, "test-registry-v1.md", "2.50")
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, f"both clean → PASS. stdout={stdout} stderr={stderr}"
