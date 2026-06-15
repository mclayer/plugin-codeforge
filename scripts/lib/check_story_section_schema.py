#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-91 (CFP-84 follow-up) — Story file section schema lint
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# trap_priority: line 79 equivalent path normalization + mode_preserve (100755)
#
# Validates docs/stories/*.md against templates/story-page-structure.md schema:
# - Implementation Story (type: story OR no type field) = strict mode (§1-§13 모두 의무)
# - Epic Story (type: epic) = condensed mode allowed
#
# Usage / exit code / semantics 상세: scripts/check-story-section-schema.sh header.
import sys, re
from pathlib import Path
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 강제 섹션 (Implementation Story strict, §12+§13 optional)
# CFP-2293 fix: heading 의 § 기호는 선택적(§?). story-init renderer
#   (workflow_story_init_render_story.py) 는 `## N.`(§ 없음) 헤딩을 생성하고 기존 consumer
#   story 전부 동일 형식이므로 linter 도 `## N.` / `## §N.` 양쪽을 수용한다 (renderer↔linter
#   컨벤션 정합). § anchor 뒤 [\.\s] 가 §1 vs §10/§11 prefix 충돌을 차단한다.
STRICT_REQUIRED = [
    ("§1", r"^##\s*§?1[\.\s]"),
    ("§2", r"^##\s*§?2[\.\s]"),
    ("§3", r"^##\s*§?3[\.\s]"),
    ("§4", r"^##\s*§?4[\.\s]"),
    ("§5", r"^##\s*§?5[\.\s]"),
    ("§6", r"^##\s*§?6[\.\s]"),
    ("§7", r"^##\s*§?7[\.\s]"),
    ("§8", r"^##\s*§?8[\.\s]"),
    ("§9", r"^##\s*§?9[\.\s]"),
    ("§10", r"^##\s*§?10[\.\s]"),
    ("§11", r"^##\s*§?11[\.\s]"),
]

# Epic condensed required (의무) + 결합/N/A 의무
EPIC_REQUIRED = [
    ("§1", r"^##\s*§?1[\.\s]"),
    ("§3", r"^##\s*§?3[\.\s]"),
    ("§7", r"^##\s*§?7[\.\s]"),
    ("§11", r"^##\s*§?11[\.\s]"),
    ("§12", r"^##\s*§?12[\.\s]"),
]
EPIC_NA_REQUIRED = ["§8", "§10"]  # N/A 명시 의무

# 결합 허용 patterns (Epic only) — 예: "5-6", "§5-6", "§5-§6" (§ 선택적, CFP-2293)
COMBINED_PATTERN = re.compile(r"^##\s*§?(\d+)\s*[-–]\s*§?(\d+)[\.\s]")

# N/A first line pattern
NA_PATTERN = re.compile(r"^N/A\s*[—\-]\s*\S+")

# Frontmatter type field
TYPE_PATTERN = re.compile(r"^type:\s*(\S+)\s*$", re.MULTILINE)

errors = 0
warnings = 0
checked = 0

stories_dir = Path("docs/stories")
if not stories_dir.exists():
    print("ℹ️  docs/stories/ 부재 — lint skip (plugin repo or pre-init consumer)")
    sys.exit(0)

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
            sec_pat = re.compile(rf"^##\s*§?{sec_num}[\.\s].*?(?=^##|\Z)", re.MULTILINE | re.DOTALL)
            sec_match = sec_pat.search(text)
            if not sec_match:
                print(f"❌ {rel}: Epic Story 의 §{sec_num} N/A 명시 의무 (단순 omit 거부 — CFP-84 N/A 형식)")
                errors += 1
            else:
                content_lines = [l for l in sec_match.group(0).split("\n")[1:] if l.strip()]
                if content_lines and not NA_PATTERN.match(content_lines[0]):
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
