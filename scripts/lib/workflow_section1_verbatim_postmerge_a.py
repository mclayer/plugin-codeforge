"""
workflow_section1_verbatim_postmerge_a.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #18: section-1-verbatim-postmerge.yml lines 93-116
(Extract Story §1 section from story file, write to /tmp/story-section-1.txt)

Writes "skip=true" or "skip=false" to $GITHUB_OUTPUT.
Writes section text to /tmp/story-section-1.txt when found.

Usage (via workflow YAML run: block):
  python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_section1_verbatim_postmerge_a.py"

env: block must provide:
  KEY: ${{ steps.key.outputs.key }}
  GITHUB_OUTPUT: (auto-set by GitHub Actions runner)
"""
import sys
import re
import os
from pathlib import Path

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> None:
    key = os.environ["KEY"]
    story_file = Path(f"docs/stories/{key}.md")
    content = story_file.read_text(encoding="utf-8")

    # §1 섹션 추출 (## 1. 이후 ~ 다음 ## 이전)
    m = re.search(
        r'^##\s+1\.[^\n]*\n(.*?)(?=^##\s|\Z)',
        content, re.MULTILINE | re.DOTALL
    )
    if not m:
        print("::notice::Story §1 섹션 부재 — skip")
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write("skip=true\n")
        sys.exit(0)

    section_text = m.group(1).strip()
    # 임시 파일에 저장 (shell injection 차단 — printf '%s' 패턴)
    with open("/tmp/story-section-1.txt", "w", encoding="utf-8") as f:
        f.write(section_text)
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write("skip=false\n")


if __name__ == "__main__":
    main()
