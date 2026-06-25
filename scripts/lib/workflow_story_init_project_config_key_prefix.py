"""
workflow_story_init_project_config_key_prefix.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #24: story-init.yml lines 61-75 (yq fallback — story_key_prefix extraction)

Usage (via workflow YAML run: block):
  story_key_prefix=$(python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_story_init_project_config_key_prefix.py")
  echo "story_key_prefix=$story_key_prefix" >> "$GITHUB_OUTPUT"

env: block must provide:
  CFG_PATH: path to project.yaml (e.g. ".claude/_overlay/project.yaml")
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
    path = os.environ.get("CFG_PATH", ".claude/_overlay/project.yaml")
    in_github = False
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if re.match(r"^[A-Za-z_][\w-]*:\s*$", line):
            in_github = line.split(":", 1)[0] == "github"
            continue
        if in_github:
            m = re.match(r"^\s{2}story_key_prefix:\s*(.*?)\s*$", line)
            if m:
                print(m.group(1).strip().strip('"').strip("'"))
                return
    sys.exit(1)


if __name__ == "__main__":
    main()
