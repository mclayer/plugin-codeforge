#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-410 — Story §9 sub-section yaml block schema validation
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# trap_priority: line 58 equivalent — set -uo pipefail (non-strict error handling preserved)
#
# Tier: warning (ADR-060 §결정 5 — 첫 도입 = warning mode).
# Usage / exit code / semantics 상세: scripts/check-story-section-9-typed.sh header.
import sys, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("warning pyyaml not installed - skip (install: pip install pyyaml)")
    sys.exit(0)

REQUIRED_FIELDS = {"contract", "lane", "story_key", "iteration", "pl_recommendation"}
LANE_VALUES = {"design", "code", "security"}
PL_VALUES = {"PASS", "FIX", "FIX_DISCRETIONARY", "ESCALATE_PACKET_INCOMPLETE"}
CONTRACT_VALUE = "review-verdict-v4"

SECTION_9_PATTERN = re.compile(r"^###\s*§9\.[1-4]\b", re.MULTILINE)
YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)

warnings = 0
checked_stories = 0
checked_blocks = 0

stories_dir = Path("docs/stories")
if not stories_dir.exists():
    print("info docs/stories not present - skip")
    sys.exit(0)

for f in sorted(stories_dir.glob("*.md")):
    if f.name == ".gitkeep":
        continue
    text = f.read_text(encoding="utf-8")
    if not text.strip():
        continue
    checked_stories += 1
    rel = str(f).replace("\\", "/")

    lines = text.split("\n")
    in_section_9 = False
    current_section = None
    section_blocks = []  # list of (section_name, yaml_text, line_start)
    block_buffer = []
    in_yaml_block = False
    yaml_start_line = 0

    for i, line in enumerate(lines, 1):
        m = re.match(r"^###\s*§9\.([1-4])\b", line)
        if m:
            in_section_9 = True
            current_section = f"§9.{m.group(1)}"
            continue
        if in_section_9 and (re.match(r"^##\s", line) or re.match(r"^###\s*§(?!9\.)", line)):
            in_section_9 = False
            current_section = None
            continue

        if in_section_9:
            if line.strip().startswith("```yaml"):
                in_yaml_block = True
                block_buffer = []
                yaml_start_line = i
                continue
            if in_yaml_block and line.strip() == "```":
                section_blocks.append((current_section, "\n".join(block_buffer), yaml_start_line))
                in_yaml_block = False
                block_buffer = []
                continue
            if in_yaml_block:
                block_buffer.append(line)

    if not section_blocks:
        continue  # backward compat — no yaml block = OK

    for section, yaml_text, line_no in section_blocks:
        checked_blocks += 1
        try:
            data = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            print(f"warning {rel}:{line_no} {section} yaml parse error: {e}")
            warnings += 1
            continue
        if not isinstance(data, dict):
            print(f"warning {rel}:{line_no} {section} yaml not a mapping")
            warnings += 1
            continue

        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            print(f"warning {rel}:{line_no} {section} missing required fields: {sorted(missing)}")
            warnings += 1
            continue

        if data.get("contract") != CONTRACT_VALUE:
            print(f"warning {rel}:{line_no} {section} contract must be '{CONTRACT_VALUE}' (got {data.get('contract')!r})")
            warnings += 1
        if data.get("lane") not in LANE_VALUES:
            print(f"warning {rel}:{line_no} {section} lane must be one of {sorted(LANE_VALUES)} (got {data.get('lane')!r})")
            warnings += 1
        if data.get("pl_recommendation") not in PL_VALUES:
            print(f"warning {rel}:{line_no} {section} pl_recommendation must be one of {sorted(PL_VALUES)} (got {data.get('pl_recommendation')!r})")
            warnings += 1
        if not isinstance(data.get("iteration"), int):
            print(f"warning {rel}:{line_no} {section} iteration must be int (got {type(data.get('iteration')).__name__})")
            warnings += 1
        wdr = data.get("worker_dialog_rounds")
        if wdr is not None and (not isinstance(wdr, int) or wdr < 0):
            print(f"warning {rel}:{line_no} {section} worker_dialog_rounds must be int >= 0 (got {wdr!r})")
            warnings += 1

print(f"check-story-section-9-typed: stories_scanned={checked_stories} yaml_blocks_validated={checked_blocks} warnings={warnings}")

# Warning tier — never fail (ADR-060 §결정 5)
sys.exit(0)
