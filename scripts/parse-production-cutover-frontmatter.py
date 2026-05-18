#!/usr/bin/env python3
"""parse-production-cutover-frontmatter.py — Story frontmatter yaml.safe_load parser.

CFP-954 / ADR-061 §결정 1 정합 (multi-line Python > 5줄 = 외부 .py 의무 + heredoc 금지).
CFP-699 CR-821-6 strict-verify YAML-parse-not-grep lineage (grep parse 금지).

Usage:
    python3 scripts/parse-production-cutover-frontmatter.py <story-file> <jq-like-path>

Args:
    story-file : Story markdown file path (frontmatter `--- ... ---` block 보유)
    jq-like-path : `.live_touching` / `.production_cutover_touching` / `.section_8_5_active` 등

Exit code:
    0 = field value printed (stdout, bool/str/null)
    1 = field absent in frontmatter
    2 = SETUP error (file not found / yaml parse failure / invalid path syntax)
"""
import sys
from pathlib import Path


def _extract_frontmatter(content: str) -> str:
    """Extract `--- ... ---` frontmatter block from markdown content.

    Returns:
        yaml block string (without `---` delimiters), or empty string if absent.
    """
    if not content.startswith("---"):
        return ""
    lines = content.split("\n")
    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return ""
    return "\n".join(lines[1:end_idx])


def _resolve_path(data: dict, dotted_path: str):
    """Resolve `.field.nested` style path against parsed yaml dict.

    Returns:
        Resolved value, or KeyError-equivalent (caller exits 1).
    """
    if not dotted_path.startswith("."):
        raise ValueError(f"path must start with '.': got {dotted_path!r}")
    parts = [p for p in dotted_path[1:].split(".") if p]
    cur = data
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            raise KeyError(p)
        cur = cur[p]
    return cur


def main(argv):
    if len(argv) != 3:
        print(
            "USAGE: parse-production-cutover-frontmatter.py <story-file> <.field.path>",
            file=sys.stderr,
        )
        return 2

    story_path = Path(argv[1])
    dotted_path = argv[2]

    if not story_path.is_file():
        print(f"PARSE_ERROR: story file not found: {story_path}", file=sys.stderr)
        return 2

    try:
        import yaml  # PyYAML 의무 (ADR-061 §결정 5 + CFP-699 CR-821-6)
    except ImportError:
        print(
            "PARSE_ERROR: PyYAML 미설치 ('pip install pyyaml' 후 재실행).",
            file=sys.stderr,
        )
        return 2

    try:
        content = story_path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 (file IO genuine fail)
        print(f"PARSE_ERROR: read fail: {exc}", file=sys.stderr)
        return 2

    fm_block = _extract_frontmatter(content)
    if not fm_block:
        # frontmatter block absent = field absent (exit 1, not SETUP error)
        # Covers: plain YAML files (.yaml), markdown with no frontmatter block.
        return 1

    try:
        data = yaml.safe_load(fm_block)  # CR-821-6 strict mandate
    except yaml.YAMLError as exc:
        print(f"PARSE_ERROR: yaml.safe_load failure: {exc}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print(
            f"PARSE_ERROR: frontmatter root must be mapping (got {type(data).__name__})",
            file=sys.stderr,
        )
        return 2

    try:
        value = _resolve_path(data, dotted_path)
    except ValueError as exc:
        print(f"PARSE_ERROR: invalid path: {exc}", file=sys.stderr)
        return 2
    except KeyError:
        # Field absent — graceful exit 1 (caller distinguishes missing vs error)
        return 1

    # Print bool as `true`/`false` (yaml convention), None as `null`, else str.
    if value is True:
        print("true")
    elif value is False:
        print("false")
    elif value is None:
        print("null")
    else:
        print(str(value))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
