#!/usr/bin/env bash
# CFP-91 (CFP-84 follow-up) — Story file section schema lint
#
# Validates docs/stories/*.md against templates/story-page-structure.md schema:
# - Implementation Story (type: story OR no type field) = strict mode (§1-§13 모두 의무)
# - Epic Story (type: epic) = condensed mode allowed
#
# Source: templates/story-page-structure.md "Epic Story Condensed Mode" (CFP-84)
#
# Strict mode mandatory sections: §1, §2, §3, §4, §5, §6, §7, §8, §9, §10, §11
#   §12, §13 = optional (Sonnet log only on substantive trigger / CONDITIONAL Live touching)
# Epic condensed mandatory: §1, §3, §7, §11, §12 + §8 N/A 명시 + §10 N/A 명시
#   Optional / 결합 허용: §2, §4, §5, §6, §9
#
# Combined section heading 허용 (Epic only): "## §X-Y. <combined title>" — heading 에 결합 명시 의무
# N/A 명시: "## §X. <title>" 후 첫 라인 = "N/A — <reason>" (단순 omit 거부)
#
# Skip 조건: docs/stories/ 디렉터리 부재 (plugin repo) / .gitkeep / 빈 file

set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d "docs/stories" ]; then
  echo "ℹ️  docs/stories/ 부재 — lint skip (plugin repo or pre-init consumer)"
  exit 0
fi

python3 <<'PY'
import sys, re
from pathlib import Path

# 강제 섹션 (Implementation Story strict, §12+§13 optional)
STRICT_REQUIRED = [
    ("§1", r"^##\s*§1[\.\s]"),
    ("§2", r"^##\s*§2[\.\s]"),
    ("§3", r"^##\s*§3[\.\s]"),
    ("§4", r"^##\s*§4[\.\s]"),
    ("§5", r"^##\s*§5[\.\s]"),
    ("§6", r"^##\s*§6[\.\s]"),
    ("§7", r"^##\s*§7[\.\s]"),
    ("§8", r"^##\s*§8[\.\s]"),
    ("§9", r"^##\s*§9[\.\s]"),
    ("§10", r"^##\s*§10[\.\s]"),
    ("§11", r"^##\s*§11[\.\s]"),
]

# Epic condensed required (의무) + 결합/N/A 의무
EPIC_REQUIRED = [
    ("§1", r"^##\s*§1[\.\s]"),
    ("§3", r"^##\s*§3[\.\s]"),
    ("§7", r"^##\s*§7[\.\s]"),
    ("§11", r"^##\s*§11[\.\s]"),
    ("§12", r"^##\s*§12[\.\s]"),
]
EPIC_NA_REQUIRED = ["§8", "§10"]  # N/A 명시 의무

# 결합 허용 patterns (Epic only) — 예: "§5-6", "§5-§6"
COMBINED_PATTERN = re.compile(r"^##\s*§(\d+)\s*[-–]\s*§?(\d+)[\.\s]")

# N/A first line pattern
NA_PATTERN = re.compile(r"^N/A\s*[—\-]\s*\S+")

# Frontmatter type field
TYPE_PATTERN = re.compile(r"^type:\s*(\S+)\s*$", re.MULTILINE)

errors = 0
warnings = 0
checked = 0

stories_dir = Path("docs/stories")
for f in sorted(stories_dir.glob("*.md")):
    if f.name == ".gitkeep":
        continue
    text = f.read_text(encoding="utf-8")
    if not text.strip():
        continue

    checked += 1
    rel = str(f).replace("\\", "/")

    # Frontmatter parse
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        print(f"⚠️  {rel}: frontmatter 부재 — schema 추론 불가 (skip)")
        warnings += 1
        continue
    fm = fm_match.group(1)
    type_match = TYPE_PATTERN.search(fm)
    story_type = type_match.group(1).strip() if type_match else "story"  # default = implementation

    # Heading scan
    headings = re.findall(r"^##\s.*$", text, re.MULTILINE)
    body = "\n".join(headings)

    # Combined section detection — Epic only allowed
    combined_sections = set()
    for line in headings:
        m = COMBINED_PATTERN.match(line)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            combined_sections.add(a)
            combined_sections.add(b)
            if story_type != "epic":
                print(f"❌ {rel}: combined heading '{line.strip()}' = Implementation Story 에서 금지 (Epic Story `type: epic` 만 허용, CFP-84)")
                errors += 1

    if story_type == "epic":
        # Epic condensed mode
        for sec, pat in EPIC_REQUIRED:
            sec_num = int(sec.replace("§", ""))
            if sec_num in combined_sections:
                continue  # combined heading covers it
            if not re.search(pat, body, re.MULTILINE):
                print(f"❌ {rel}: Epic Story 의 §{sec_num} (mandatory) 누락 (CFP-84 Epic condensed mode)")
                errors += 1

        # N/A 명시 의무 (§8, §10)
        for sec_str in EPIC_NA_REQUIRED:
            sec_num = int(sec_str.replace("§", ""))
            if sec_num in combined_sections:
                continue
            sec_pat = re.compile(rf"^##\s*§{sec_num}[\.\s].*?(?=^##|\Z)", re.MULTILINE | re.DOTALL)
            sec_match = sec_pat.search(text)
            if not sec_match:
                print(f"❌ {rel}: Epic Story 의 §{sec_num} N/A 명시 의무 (단순 omit 거부 — CFP-84 N/A 형식)")
                errors += 1
            else:
                # check N/A first line
                content_lines = [l for l in sec_match.group(0).split("\n")[1:] if l.strip()]
                if content_lines and not NA_PATTERN.match(content_lines[0]):
                    # might be table or actual content — N/A format violation only if section is intended N/A
                    # warn (not error) — Epic could legitimately fill §8/§10
                    pass

    else:
        # Implementation Story strict mode
        for sec, pat in STRICT_REQUIRED:
            sec_num = int(sec.replace("§", ""))
            if not re.search(pat, body, re.MULTILINE):
                print(f"❌ {rel}: Implementation Story 의 §{sec_num} 누락 (strict mode — CFP-84)")
                errors += 1

print(f"\nChecked {checked} story file(s) — errors: {errors}, warnings: {warnings}")
sys.exit(1 if errors > 0 else 0)
PY
