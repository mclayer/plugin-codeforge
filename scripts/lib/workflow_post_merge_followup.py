"""
workflow_post_merge_followup.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #23: post-merge-followup.yml lines 174-190
(consumer config — lanes.security_ai read via yq fallback Python)

Reads lanes.security_ai from project.yaml.
Prints "true" or "false" to stdout.

Usage (via workflow YAML run: block):
  SECURITY_AI=$(python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_post_merge_followup.py")

env: block must provide:
  CFG_PATH: path to project.yaml (e.g. ".claude/_overlay/project.yaml" or ".codeforge/project.yaml")
"""
import re
import sys
import os


def main() -> None:
    path = os.environ.get("CFG_PATH", ".claude/_overlay/project.yaml")
    in_lanes = False
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if re.match(r"^[A-Za-z_][\w-]*:\s*$", line):
            in_lanes = line.split(":", 1)[0] == "lanes"
            continue
        if in_lanes:
            m = re.match(r"^\s{2}security_ai:\s*(.*?)\s*$", line)
            if m:
                val = m.group(1).strip().strip('"').strip("'").lower()
                print("true" if val == "true" else "false")
                sys.exit(0)
    print("false")


if __name__ == "__main__":
    main()
