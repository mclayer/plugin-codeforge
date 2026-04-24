"""Tests for overlay/hooks/merge.py — core+overlay agent md merger.

Contract reference: docs/plugin-design.md §4.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

import merge

HOOKS_DIR = Path(merge.__file__).resolve().parent
MERGE_SCRIPT = HOOKS_DIR / "merge.py"


# -----------------------------------------------------------------------------
# split_frontmatter
# -----------------------------------------------------------------------------


class TestSplitFrontmatter:
    def test_no_frontmatter_returns_empty_dict_and_raw_body(self):
        raw = "# heading\n\nbody\n"
        fm, body = merge.split_frontmatter(raw)
        assert fm == {}
        assert body == raw

    def test_valid_frontmatter_parsed_and_body_preserved(self):
        raw = dedent(
            """\
            ---
            name: X
            tools: [Read, Write]
            ---

            # heading
            body line
            """
        )
        fm, body = merge.split_frontmatter(raw)
        assert fm == {"name": "X", "tools": ["Read", "Write"]}
        assert body.startswith("\n# heading\n")

    def test_malformed_frontmatter_no_closing_delimiter_exits_3(self):
        raw = "---\nname: X\n# no closing delimiter\n"
        with pytest.raises(SystemExit) as exc:
            merge.split_frontmatter(raw)
        assert exc.value.code == 3

    def test_frontmatter_non_mapping_yaml_exits_3(self):
        raw = "---\n- just\n- a list\n---\nbody\n"
        with pytest.raises(SystemExit) as exc:
            merge.split_frontmatter(raw)
        assert exc.value.code == 3

    def test_empty_frontmatter_yields_empty_dict(self):
        raw = "---\n\n---\nbody\n"
        fm, body = merge.split_frontmatter(raw)
        assert fm == {}
        assert body == "body\n"


# -----------------------------------------------------------------------------
# dedup_list
# -----------------------------------------------------------------------------


class TestDedupList:
    def test_preserves_order_and_removes_duplicates(self):
        assert merge.dedup_list(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]

    def test_empty_input(self):
        assert merge.dedup_list([]) == []

    def test_dedup_via_stringification(self):
        # {"a": 1} and dict with same repr → deduped
        a = {"a": 1}
        b = {"a": 1}
        assert merge.dedup_list([a, b]) == [a]

    def test_no_duplicates_returns_same_order(self):
        assert merge.dedup_list(["Read", "Write", "Bash"]) == ["Read", "Write", "Bash"]


# -----------------------------------------------------------------------------
# deep_merge
# -----------------------------------------------------------------------------


class TestDeepMerge:
    def test_identity_scalar_mismatch_aborts(self):
        with pytest.raises(SystemExit) as exc:
            merge.deep_merge({"name": "A"}, {"name": "B"})
        assert exc.value.code == 4

    def test_identity_scalar_match_keeps_core(self):
        out = merge.deep_merge({"name": "A"}, {"name": "A"})
        assert out == {"name": "A"}

    def test_non_identity_scalar_core_wins_silent(self):
        # 'foo' is not an identity field → core wins without abort
        out = merge.deep_merge({"foo": "core"}, {"foo": "overlay"})
        assert out == {"foo": "core"}

    def test_lists_concat_and_dedup_core_first(self):
        out = merge.deep_merge(
            {"tools": ["Read", "Write"]},
            {"tools": ["Write", "Bash"]},
        )
        assert out == {"tools": ["Read", "Write", "Bash"]}

    def test_nested_dict_recursion(self):
        out = merge.deep_merge(
            {"permissions": {"allow": ["Read"], "deny": ["Write"]}},
            {"permissions": {"allow": ["Bash"], "deny": ["Edit"]}},
        )
        assert out == {
            "permissions": {
                "allow": ["Read", "Bash"],
                "deny": ["Write", "Edit"],
            }
        }

    def test_overlay_only_key_added(self):
        out = merge.deep_merge({"name": "X"}, {"extra": "added"})
        assert out == {"name": "X", "extra": "added"}

    def test_core_only_key_preserved(self):
        out = merge.deep_merge({"name": "X", "color": "blue"}, {"name": "X"})
        assert out == {"name": "X", "color": "blue"}

    def test_all_identity_fields_enforced(self):
        for field in ("name", "description", "model", "color"):
            with pytest.raises(SystemExit) as exc:
                merge.deep_merge({field: "a"}, {field: "b"})
            assert exc.value.code == 4, f"field {field} should abort on mismatch"

    def test_nested_list_concat_inside_map(self):
        out = merge.deep_merge(
            {"a": {"b": [1, 2]}},
            {"a": {"b": [2, 3]}},
        )
        assert out == {"a": {"b": [1, 2, 3]}}


# -----------------------------------------------------------------------------
# merge_frontmatter (top-level wrapper with name pre-check)
# -----------------------------------------------------------------------------


class TestMergeFrontmatter:
    def test_name_mismatch_precheck_exits_4(self):
        with pytest.raises(SystemExit) as exc:
            merge.merge_frontmatter({"name": "Core"}, {"name": "Overlay"})
        assert exc.value.code == 4

    def test_name_only_in_core_does_not_error(self):
        out = merge.merge_frontmatter({"name": "X"}, {"tools": ["Read"]})
        assert out == {"name": "X", "tools": ["Read"]}

    def test_name_only_in_overlay_adds_key(self):
        out = merge.merge_frontmatter({}, {"name": "X"})
        assert out == {"name": "X"}


# -----------------------------------------------------------------------------
# render_frontmatter / auto_header
# -----------------------------------------------------------------------------


class TestRenderers:
    def test_render_frontmatter_empty_dict_yields_empty_string(self):
        assert merge.render_frontmatter({}) == ""

    def test_render_frontmatter_has_delimiters(self):
        out = merge.render_frontmatter({"name": "X"})
        assert out.startswith("---\n")
        assert out.rstrip().endswith("---")

    def test_auto_header_contains_paths_and_timestamp(self):
        core = Path("agents/X.md")
        overlay = Path(".claude/_overlay/agents/X.md")
        header = merge.auto_header(core, overlay)
        assert "GENERATED FROM agents/X.md + .claude/_overlay/agents/X.md" in header
        assert "DO NOT EDIT DIRECTLY" in header
        assert re.search(r"Last regenerated: \d{4}-\d{2}-\d{2}T", header)
        assert header.startswith("<!--\n")
        assert header.rstrip("\n").endswith("-->")

    def test_auto_header_no_overlay_shows_none(self):
        header = merge.auto_header(Path("agents/X.md"), None)
        assert "+ (none)" in header


# -----------------------------------------------------------------------------
# End-to-end (subprocess)
# -----------------------------------------------------------------------------


def _run_merge(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(MERGE_SCRIPT), *args],
        capture_output=True,
        text=True,
    )


@pytest.fixture
def core_file(tmp_path: Path) -> Path:
    p = tmp_path / "Core.md"
    p.write_text(
        dedent(
            """\
            ---
            name: X
            description: core description
            tools:
              - Read
              - Write
            permissions:
              allow:
                - "Read(src/**)"
            ---

            # Agent X

            Core body content.
            """
        ),
        encoding="utf-8",
    )
    return p


class TestEndToEnd:
    def test_core_only_no_overlay_arg(self, core_file: Path):
        res = _run_merge(str(core_file))
        assert res.returncode == 0, res.stderr
        assert "name: X" in res.stdout
        assert "# Agent X" in res.stdout
        assert "## Project Overlay" not in res.stdout
        assert "GENERATED FROM" in res.stdout
        assert "+ (none)" in res.stdout

    def test_core_plus_nonexistent_overlay_treated_as_core_only(
        self, core_file: Path, tmp_path: Path
    ):
        missing = tmp_path / "missing.md"
        res = _run_merge(str(core_file), str(missing))
        assert res.returncode == 0, res.stderr
        assert "## Project Overlay" not in res.stdout

    def test_core_plus_overlay_merges_frontmatter_and_appends_body(
        self, core_file: Path, tmp_path: Path
    ):
        overlay = tmp_path / "Overlay.md"
        overlay.write_text(
            dedent(
                """\
                ---
                name: X
                tools:
                  - Bash
                permissions:
                  allow:
                    - "Write(overlay/**)"
                ---

                Overlay body specific to this project.
                """
            ),
            encoding="utf-8",
        )
        res = _run_merge(str(core_file), str(overlay))
        assert res.returncode == 0, res.stderr
        # tools concat+dedup: Read, Write (core), Bash (overlay)
        assert re.search(r"tools:\s*\n\s*-\s*Read\s*\n\s*-\s*Write\s*\n\s*-\s*Bash", res.stdout)
        # permissions.allow concat
        assert "Read(src/**)" in res.stdout
        assert "Write(overlay/**)" in res.stdout
        # body append marker
        assert "## Project Overlay" in res.stdout
        assert "Overlay body specific to this project." in res.stdout
        # core body preserved
        assert "Core body content." in res.stdout

    def test_overlay_empty_body_no_project_overlay_header(
        self, core_file: Path, tmp_path: Path
    ):
        overlay = tmp_path / "Overlay.md"
        overlay.write_text(
            dedent(
                """\
                ---
                name: X
                tools:
                  - Bash
                ---
                """
            ),
            encoding="utf-8",
        )
        res = _run_merge(str(core_file), str(overlay))
        assert res.returncode == 0, res.stderr
        assert "## Project Overlay" not in res.stdout
        # frontmatter still merged
        assert "Bash" in res.stdout

    def test_name_mismatch_aborts_exit_4(
        self, core_file: Path, tmp_path: Path
    ):
        overlay = tmp_path / "Overlay.md"
        overlay.write_text(
            dedent(
                """\
                ---
                name: Different
                ---

                body
                """
            ),
            encoding="utf-8",
        )
        res = _run_merge(str(core_file), str(overlay))
        assert res.returncode == 4
        assert "mismatch" in res.stderr.lower()

    def test_description_mismatch_aborts_exit_4(
        self, core_file: Path, tmp_path: Path
    ):
        overlay = tmp_path / "Overlay.md"
        overlay.write_text(
            dedent(
                """\
                ---
                name: X
                description: overlay overrides description
                ---

                body
                """
            ),
            encoding="utf-8",
        )
        res = _run_merge(str(core_file), str(overlay))
        assert res.returncode == 4
        assert "description" in res.stderr.lower()

    def test_missing_core_exits_5(self, tmp_path: Path):
        missing = tmp_path / "nope.md"
        res = _run_merge(str(missing))
        assert res.returncode == 5
        assert "core file not found" in res.stderr.lower()

    def test_no_args_exits_1(self):
        res = _run_merge()
        assert res.returncode == 1
        assert "Usage" in res.stderr

    def test_too_many_args_exits_1(self, core_file: Path):
        res = _run_merge(str(core_file), str(core_file), str(core_file))
        assert res.returncode == 1
        assert "Usage" in res.stderr

    def test_malformed_frontmatter_exits_3(self, tmp_path: Path):
        bad = tmp_path / "Bad.md"
        bad.write_text("---\nname: X\n# no closing delimiter, just body\n", encoding="utf-8")
        res = _run_merge(str(bad))
        assert res.returncode == 3

    def test_idempotent_output_modulo_timestamp(
        self, core_file: Path, tmp_path: Path
    ):
        overlay = tmp_path / "Overlay.md"
        overlay.write_text(
            "---\nname: X\ntools: [Bash]\n---\n\noverlay body\n", encoding="utf-8"
        )
        first = _run_merge(str(core_file), str(overlay)).stdout
        second = _run_merge(str(core_file), str(overlay)).stdout
        # Strip the Last regenerated: line for comparison
        strip_ts = lambda s: re.sub(r"  Last regenerated: [^\n]+\n", "", s)
        assert strip_ts(first) == strip_ts(second)

    def test_auto_header_appears_between_frontmatter_and_body(
        self, core_file: Path
    ):
        res = _run_merge(str(core_file))
        assert res.returncode == 0
        out = res.stdout
        fm_end = out.index("---", out.index("---") + 3)  # second ---
        header_start = out.index("<!--")
        body_start = out.index("# Agent X")
        assert fm_end < header_start < body_start
