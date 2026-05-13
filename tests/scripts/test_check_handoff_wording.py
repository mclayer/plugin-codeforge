#!/usr/bin/env python3
"""Tests for scripts/check_handoff_wording.py (CFP-529 Wave 3 Phase 2).

Unittest framework — mechanical patterns + direction enum + exit code +
exempt regions. Stub framework (Phase 2 first iteration); pattern accuracy
ratchet is follow-up CFP scope.
"""

from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Import the script under test
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_handoff_wording as linter  # noqa: E402


class _FixtureMixin:
    """Provide a temporary repo root with minimal docs/scripts scaffolding."""

    def _make_repo(self) -> Path:
        tmpdir = Path(tempfile.mkdtemp(prefix="cfp529-hw-"))
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)
        for sub in ("scripts", "templates", "tests", "docs", "docs/adr",
                    "docs/inter-plugin-contracts", "docs/stories"):
            (tmpdir / sub).mkdir(parents=True, exist_ok=True)
        return tmpdir

    def _write(self, root: Path, rel: str, content: str) -> Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _cfg(self, root: Path, **overrides) -> linter.LintConfig:
        defaults = {
            "root": root,
            "scope": linter.SCOPE_GLOBS,
            "direction": "all",
            "strict": False,
            "json_out": False,
            "skip_ai_stubs": False,
        }
        defaults.update(overrides)
        return linter.LintConfig(**defaults)


class TestMechanicalPatterns(_FixtureMixin, unittest.TestCase):
    """5 mechanical pre-screen patterns."""

    def test_synonym_substitution_detected(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "We MUST handle every error gracefully.\n"
            "On failure, retry once and abort.\n",
        )
        findings = linter.detect_synonym_substitution(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "synonym_substitution" for f in findings),
            f"expected synonym finding, got {findings}",
        )

    def test_unit_drift_detected(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Timeout is 500 ms for fast path.\n"
            "Total budget is 30 seconds for full run.\n",
        )
        findings = linter.detect_unit_drift(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "unit_drift" for f in findings),
            f"expected unit_drift finding, got {findings}",
        )

    def test_modal_downgrade_detected(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Implementations MUST handle errors.\n"
            "Callers SHOULD retry on transient failure.\n",
        )
        findings = linter.detect_modal_downgrade(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "modal_downgrade" for f in findings),
            f"expected modal_downgrade finding, got {findings}",
        )

    def test_boundary_inversion_detected(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Round count must be ≥3 to converge.\n"
            "Reject when count >3 for max gating.\n",
        )
        findings = linter.detect_boundary_inversion(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "boundary_inversion" for f in findings),
            f"expected boundary_inversion finding, got {findings}",
        )

    def test_scope_widening_detected(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Applies to a single Story only.\n"
            "Then we extend to all Stories at once.\n",
        )
        findings = linter.detect_scope_widening(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "scope_widening" for f in findings),
            f"expected scope_widening finding, got {findings}",
        )


class TestAIEscalateStubs(_FixtureMixin, unittest.TestCase):
    """3 AI escalate stub patterns."""

    def test_precision_loss_emits_when_approx_present(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Estimated latency is approximately 30 ms.\n",
        )
        findings = linter.stub_precision_loss(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "precision_loss" for f in findings),
            f"expected precision_loss finding, got {findings}",
        )

    def test_skip_ai_stubs_flag_disables_emission(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Estimated latency is approximately 30 ms.\n",
        )
        cfg = self._cfg(root, skip_ai_stubs=True)
        self.assertEqual(linter.stub_precision_loss(cfg), [])
        self.assertEqual(linter.stub_conditional_erasure(cfg), [])
        self.assertEqual(linter.stub_actor_drift(cfg), [])

    def test_conditional_erasure_only_in_design_paths(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/adr/ADR-999-test.md",
            "FIX is allowed only when severity is critical.\n",
        )
        # Non-design path should not emit conditional_erasure
        self._write(
            root,
            "scripts/example.sh",
            "echo 'run only when ready'\n",
        )
        findings = linter.stub_conditional_erasure(self._cfg(root))
        adr_findings = [f for f in findings if "adr/" in f.file]
        non_adr_findings = [f for f in findings if "scripts/" in f.file]
        self.assertTrue(adr_findings, "expected conditional_erasure on ADR file")
        self.assertFalse(non_adr_findings, "should not flag conditional in scripts")

    def test_actor_drift_emits_on_story_with_many_actors(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/stories/CFP-X.md",
            "## §3\n"
            "Orchestrator spawns ArchitectAgent and DeveloperAgent and PMOAgent.\n",
        )
        findings = linter.stub_actor_drift(self._cfg(root))
        self.assertTrue(
            any(f.drift_type == "actor_drift" for f in findings),
            f"expected actor_drift finding, got {findings}",
        )


class TestDirectionEnum(_FixtureMixin, unittest.TestCase):
    """3-direction enum handlers (forward / backward / lateral)."""

    def test_forward_missing_impl_detected(self):
        root = self._make_repo()
        # ADR declares a contract-like identifier
        self._write(
            root,
            "docs/adr/ADR-999.md",
            "Self-check field `something_brand_new_check` introduced.\n",
        )
        # Impl files exist but do not reference identifier
        self._write(root, "scripts/example.sh", "#!/bin/bash\necho hi\n")
        findings = linter.detect_forward(self._cfg(root, direction="forward"))
        self.assertTrue(
            any(f.drift_type == "forward_missing_impl" for f in findings),
            f"expected forward_missing_impl finding, got {findings}",
        )

    def test_backward_missing_design_detected(self):
        root = self._make_repo()
        # Impl declares contract-like identifier without ADR/contract def
        self._write(
            root,
            "scripts/example.sh",
            "# `orphan_identifier_check` exists only here.\n",
        )
        # ADR present but unrelated
        self._write(root, "docs/adr/ADR-001.md", "Unrelated content.\n")
        findings = linter.detect_backward(self._cfg(root, direction="backward"))
        self.assertTrue(
            any(f.drift_type == "backward_missing_design" for f in findings),
            f"expected backward_missing_design finding, got {findings}",
        )

    def test_lateral_story_section_drift_detected(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/stories/CFP-X.md",
            "## §3 design\n"
            "Field `new_field_check` defined.\n"
            "## §8.5 impl manifest\n"
            "No reference here.\n",
        )
        findings = linter.detect_lateral(self._cfg(root, direction="lateral"))
        self.assertTrue(
            any(f.drift_type == "lateral_section_drift" for f in findings),
            f"expected lateral_section_drift, got {findings}",
        )


class TestExitCode(_FixtureMixin, unittest.TestCase):
    """Exit code tri-tier (ADR-060 Amendment 2 §결정 15)."""

    def _run_main(self, root: Path, *extra_args: str) -> tuple[int, str, str]:
        """Run main() with isolated stdout/stderr capture."""
        argv = ["--root", str(root), *extra_args]
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = linter.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_exit_0_no_violations(self):
        root = self._make_repo()
        # Empty repo (no scope files with content) → 0 findings
        code, out, err = self._run_main(root)
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_exit_1_strict_mode_with_findings(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "MUST handle errors.\nSHOULD retry on failure.\n",
        )
        code, out, err = self._run_main(root, "--strict")
        self.assertEqual(code, 1)

    def test_exit_0_warning_mode_with_findings(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "MUST handle errors.\nSHOULD retry on failure.\n",
        )
        code, out, err = self._run_main(root)
        self.assertEqual(code, 0, f"warning tier should exit 0, got {code}")
        self.assertIn("advisory", err)

    def test_exit_2_root_path_absent(self):
        argv = ["--root", "/no/such/path/exists/here/cfp529"]
        code = linter.main(argv)
        self.assertEqual(code, 2)


class TestExemptRegions(_FixtureMixin, unittest.TestCase):
    """Exempt region handling: dictionary body / verbatim quote / overlay."""

    def test_dictionary_body_exempt(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "Normal content.\n"
            "<!-- dictionary-body-start -->\n"
            "MUST do this.\n"
            "SHOULD also do that.\n"
            "<!-- dictionary-body-end -->\n",
        )
        # Modal downgrade detector should skip dictionary body
        findings = linter.detect_modal_downgrade(self._cfg(root))
        # The MUST→SHOULD inside dictionary block should be skipped
        self.assertFalse(
            any(f.drift_type == "modal_downgrade" for f in findings),
            f"dictionary body should be exempt, got {findings}",
        )

    def test_verbatim_quote_exempt(self):
        root = self._make_repo()
        self._write(
            root,
            "docs/sample.md",
            "> MUST handle this.\n"
            "> SHOULD also do that.\n",
        )
        findings = linter.detect_modal_downgrade(self._cfg(root))
        self.assertFalse(
            any(f.drift_type == "modal_downgrade" for f in findings),
            f"quote lines should be exempt, got {findings}",
        )

    def test_consumer_overlay_exempt(self):
        root = self._make_repo()
        overlay_file = root / ".claude" / "_overlay" / "CLAUDE.md"
        overlay_file.parent.mkdir(parents=True, exist_ok=True)
        overlay_file.write_text(
            "MUST do this.\nSHOULD also do that.\n", encoding="utf-8"
        )
        # is_exempt_path should treat overlay as exempt
        self.assertTrue(linter.is_exempt_path(overlay_file))


class TestArgParse(unittest.TestCase):
    """CLI arg parsing surface."""

    def test_default_args(self):
        ns = linter.parse_args([])
        self.assertEqual(ns.direction, "all")
        self.assertFalse(ns.strict)
        self.assertFalse(ns.json_out)
        self.assertFalse(ns.skip_ai_stubs)

    def test_direction_choices(self):
        for direction in ("forward", "backward", "lateral", "all"):
            ns = linter.parse_args(["--direction", direction])
            self.assertEqual(ns.direction, direction)

    def test_strict_flag(self):
        ns = linter.parse_args(["--strict"])
        self.assertTrue(ns.strict)

    def test_json_flag(self):
        ns = linter.parse_args(["--json"])
        self.assertTrue(ns.json_out)


class TestFormatters(unittest.TestCase):
    """Text and JSON output formatters."""

    def _sample_finding(self) -> linter.Finding:
        return linter.Finding(
            severity="warning",
            drift_type="modal_downgrade",
            direction="lateral",
            file="docs/sample.md",
            line=3,
            evidence="MUST → SHOULD",
            suggestion="align modal strength",
        )

    def test_text_format_pass(self):
        out = linter.format_text([])
        self.assertIn("PASS", out)

    def test_text_format_findings(self):
        out = linter.format_text([self._sample_finding()])
        self.assertIn("modal_downgrade", out)
        self.assertIn("evidence", out)
        self.assertIn("suggestion", out)

    def test_json_format_schema(self):
        import json as _json
        out = linter.format_json([self._sample_finding()])
        data = _json.loads(out)
        self.assertEqual(data["schema"], "severity-propagation-v1")
        self.assertEqual(data["tool"], "check_handoff_wording.py")
        self.assertEqual(len(data["findings"]), 1)
        self.assertEqual(data["findings"][0]["drift_type"], "modal_downgrade")


if __name__ == "__main__":
    unittest.main()
