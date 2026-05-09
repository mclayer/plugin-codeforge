#!/usr/bin/env bash
# CFP-295 / Issue #313 — domain-knowledge frontmatter + section schema enforcement
#
# Validates docs/domain-knowledge/**/*.md files for:
#   (1) Required frontmatter fields: title, area, created (ISO date), tags (list)
#   (2) Required sections: ## Summary  +  (## Pattern OR ## Problem)  +  ## Usage
#
# Exit 0 = all pass. Exit 1 = violations found (strict mode, PR-blocking).
#
# Usage:
#   bash scripts/check-domain-knowledge-schema.sh
#   bash scripts/check-domain-knowledge-schema.sh --files <path1> <path2> ...  (subset check)
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -c "
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
" 2>/dev/null || true

python3 -u <<'PY'
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import sys, re
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DK_ROOT = Path("docs/domain-knowledge")

# Required frontmatter scalar fields
REQUIRED_FM_SCALARS = ["title", "area", "created"]

# ISO date regex (YYYY-MM-DD)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Required section patterns — order-agnostic presence check
REQUIRED_SECTIONS = [
    (r"^## Summary\s*$", "## Summary"),
    # Pattern OR Problem — at least one must be present
    (None, "## Pattern or ## Problem"),   # handled separately below
    (r"^## Usage\s*$", "## Usage"),
]
PATTERN_OR_PROBLEM_RE = re.compile(r"^## (Pattern|Problem)\b", re.MULTILINE)
SUMMARY_RE    = re.compile(r"^## Summary\s*$", re.MULTILINE)
USAGE_RE      = re.compile(r"^## Usage\s*$", re.MULTILINE)


def parse_frontmatter(text: str):
    """Return (frontmatter_lines: list[str], body: str) or ([], text) if no FM."""
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---\n", 4)
    if end == -1:
        return [], text
    fm_block = text[4:end]
    body = text[end + 5:]   # skip '\n---\n'
    return fm_block.splitlines(), body


def check_fm_field(fm_lines: list, field: str) -> str | None:
    """Return field value string (raw) or None if absent."""
    for line in fm_lines:
        m = re.match(rf"^{re.escape(field)}\s*:\s*(.*)", line)
        if m:
            return m.group(1).strip()
    return None


def check_tags_list(fm_lines: list) -> bool:
    """Return True if `tags:` is present and followed by at least one '- <item>' entry."""
    in_tags = False
    found_entry = False
    for line in fm_lines:
        if re.match(r"^tags\s*:\s*$", line):
            in_tags = True
            continue
        if re.match(r"^tags\s*:\s*\[", line):
            # inline list e.g. tags: [foo, bar]
            return bool(re.search(r"\[.+\]", line))
        if in_tags:
            if re.match(r"^\s+-\s+\S", line):
                found_entry = True
            elif re.match(r"^\S", line):
                break  # next top-level key — stop
    return found_entry


def check_file(md_path: Path) -> list:
    fails = []
    text = md_path.read_text(encoding="utf-8")
    fm_lines, body = parse_frontmatter(text)

    # --- Frontmatter present? ---
    if not fm_lines:
        fails.append(f"{md_path}: YAML frontmatter 블록 (--- ... ---) 부재")
        return fails

    # --- Required scalar fields ---
    for field in REQUIRED_FM_SCALARS:
        val = check_fm_field(fm_lines, field)
        if val is None:
            fails.append(f"{md_path}: frontmatter 필드 누락 — `{field}`")
        elif field == "created":
            if not ISO_DATE_RE.match(val):
                fails.append(
                    f"{md_path}: frontmatter `created` 값이 ISO date (YYYY-MM-DD) 형식 아님 — '{val}'"
                )

    # --- tags field (list) ---
    if check_fm_field(fm_lines, "tags") is None and not check_tags_list(fm_lines):
        # tags key might exist as a list block
        if not any(re.match(r"^tags\s*:", l) for l in fm_lines):
            fails.append(f"{md_path}: frontmatter 필드 누락 — `tags` (list, 최소 1 항목)")
    else:
        # tags key present — check it has at least one list entry
        tags_key_val = check_fm_field(fm_lines, "tags")
        if tags_key_val is not None and tags_key_val == "":
            # bare `tags:` with no inline value — check indented list
            if not check_tags_list(fm_lines):
                fails.append(f"{md_path}: frontmatter `tags` 목록 항목 최소 1개 필요")
        elif tags_key_val is not None and tags_key_val.startswith("["):
            # inline list — must have at least one item
            if not re.search(r"\S", tags_key_val[1:tags_key_val.rfind("]")]):
                fails.append(f"{md_path}: frontmatter `tags` inline list 비어 있음")

    # --- Required sections ---
    if not SUMMARY_RE.search(body):
        fails.append(f"{md_path}: 필수 섹션 누락 — `## Summary`")

    if not PATTERN_OR_PROBLEM_RE.search(body):
        fails.append(f"{md_path}: 필수 섹션 누락 — `## Pattern` 또는 `## Problem` (둘 중 하나 필수)")

    if not USAGE_RE.search(body):
        fails.append(f"{md_path}: 필수 섹션 누락 — `## Usage`")

    return fails


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if not DK_ROOT.exists():
    print(f"::notice::check-domain-knowledge-schema: {DK_ROOT} 디렉토리 없음 — skip")
    sys.exit(0)

all_fails = []
for md in sorted(DK_ROOT.rglob("*.md")):
    if md.name.lower() in {"readme.md", "index.md"}:
        continue
    all_fails.extend(check_file(md))

if all_fails:
    print(f"::error::CFP-295 domain-knowledge schema (STRICT): {len(all_fails)} 건")
    for f in all_fails:
        print(f"  - {f}")
    print()
    print("신규 domain-knowledge 파일 작성 시 frontmatter 4 필드 (title, area, created, tags) + 섹션 3종 (## Summary, ## Pattern/Problem, ## Usage) 필수.")
    sys.exit(1)

print(f"✓ CFP-295 domain-knowledge schema: {sum(1 for _ in DK_ROOT.rglob('*.md'))} 파일 모두 frontmatter + section schema 충족")
PY

echo ""
echo "(check-domain-knowledge-schema: strict 모드 (CFP-295). frontmatter 4 필드 + 섹션 3종 위반 시 exit 1)"
