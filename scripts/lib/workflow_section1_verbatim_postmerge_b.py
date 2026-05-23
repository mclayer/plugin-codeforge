"""
workflow_section1_verbatim_postmerge_b.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #21: section-1-verbatim-postmerge.yml lines 149-167
(Extract Issue body §1 section, write to /tmp/issue-section-1.txt)

Reads Issue body from /tmp/issue-body.txt (pre-written by shell step).
Writes "skip=true" or "skip=false" to $GITHUB_OUTPUT.
Writes section text to /tmp/issue-section-1.txt when found.

Usage (via workflow YAML run: block):
  printf '%s' "$ISSUE_BODY" > /tmp/issue-body.txt
  python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_section1_verbatim_postmerge_b.py"

env: block must provide:
  GITHUB_OUTPUT: (auto-set by GitHub Actions runner)
  (reads /tmp/issue-body.txt written by calling shell step)
"""
import re
import sys
import os

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> None:
    content = open("/tmp/issue-body.txt", encoding="utf-8").read()

    # ### 사용자 요구사항 ~ 다음 ### 이전
    m = re.search(
        r'^###\s+사용자 요구사항[^\n]*\n(.*?)(?=^###\s|\Z)',
        content, re.MULTILINE | re.DOTALL
    )
    if not m:
        print("::notice::Issue body 에서 사용자 요구사항 섹션 부재 — skip")
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write("skip=true\n")
        sys.exit(0)

    section_text = m.group(1).strip()
    with open("/tmp/issue-section-1.txt", "w", encoding="utf-8") as f:
        f.write(section_text)
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write("skip=false\n")


if __name__ == "__main__":
    main()
