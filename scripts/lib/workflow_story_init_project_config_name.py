"""
workflow_story_init_project_config_name.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #25: story-init.yml lines 77-91 (yq fallback — project_name extraction)

Usage (via workflow YAML run: block):
  project_name=$(python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_story_init_project_config_name.py")
  echo "project_name=$project_name" >> "$GITHUB_OUTPUT"

env: block must provide:
  CFG_PATH: path to project.yaml (e.g. ".claude/_overlay/project.yaml")
"""
import re
import sys
import os


def main() -> None:
    path = os.environ.get("CFG_PATH", ".claude/_overlay/project.yaml")
    in_project = False
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if re.match(r"^[A-Za-z_][\w-]*:\s*$", line):
            in_project = line.split(":", 1)[0] == "project"
            continue
        if in_project:
            m = re.match(r"^\s{2}name:\s*(.*?)\s*$", line)
            if m:
                print(m.group(1).strip().strip('"').strip("'"))
                return
    sys.exit(1)


if __name__ == "__main__":
    main()
