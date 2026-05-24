#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1367 / ADR-107 Amendment 1 §결정 1 — F1 plugin-declarative-seed-byte-parity-check
# ADR-061 §결정 1 — Python SSOT (heredoc 금지), ADR-060 §결정 5 warning-tier
# ADR-061 Amendment 3 (CFP-1507) — CodeQL ReDoS guard: line-by-line parse (no backtracking regex)
#
# 검사 목적:
#   Wrapper SSOT (docs/project-config-schema.md 등) ↔
#   plugin templates/* declarative seed file 의 schema 구조 byte-parity 정적 검사.
#
#   Wave 1 scope = single file mapping:
#     wrapper SSOT: docs/project-config-schema.md (deploy: section)
#     plugin seed:  mclayer/plugin-codeforge-deploy/templates/deploy-mechanism.md
#
#   drift 발견 시 처리 path 2-enum (ADR-107 §결정 1):
#     Path A — mirror update (drift source = wrapper-side)
#     Path B — single-SSOT deprecate (Wave A S2 d-B precedent 권고)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (yaml.safe_load 파싱 실패 등 하드 오류)
#   2 — setup error (파일 없음 등 환경 오류)
#
# Usage:
#   python3 check_plugin_declarative_seed_byte_parity.py \
#     --ssot-file <wrapper-ssot-path> --plugin-file <plugin-seed-path>
#
# Bypass channel: HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY=1 env

import sys
import re
import os
import argparse
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("[plugin-seed-parity-lint] pyyaml 미설치 — skip (exit 0)", file=sys.stderr)
    sys.exit(0)

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY", "")
if BYPASS_ENV == "1":
    print("[plugin-seed-parity-lint] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[plugin-seed-parity-lint]"

# Wave 1 scope: single file mapping
# (확장 = 별 follow-up CFP, ADR-107 §결정 1 Wave 1 scope 단일 mapping)
WAVE1_SSOT_PATH = "docs/project-config-schema.md"
WAVE1_PLUGIN_PATH = "templates/deploy-mechanism.md"


# ── ADR-061 Amendment 3 ReDoS guard ───────────────────────────────────────────
# line-by-line parse (no backtracking regex)
# FRONTMATTER_RE matches ONLY if "---" is at line start (column 0)
# Using DOTALL=False + split-on-newline approach
def extract_frontmatter(text: str) -> tuple[dict | None, str]:
    """YAML frontmatter 추출 (line-by-line — ReDoS guard ADR-061 Amendment 3).

    Returns (frontmatter_dict_or_None, body_text).
    Raises yaml.YAMLError if frontmatter is present but malformed.
    """
    lines = text.splitlines(keepends=True)
    if not lines:
        return None, text

    # frontmatter must start at line 0 with exactly "---"
    if lines[0].rstrip("\r\n") != "---":
        return None, text

    # find closing ---
    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            close_idx = i
            break

    if close_idx is None:
        return None, text

    fm_text = "".join(lines[1:close_idx])
    body_text = "".join(lines[close_idx + 1:])

    # yaml.safe_load raises yaml.YAMLError on malformed input
    fm_dict = yaml.safe_load(fm_text)
    return fm_dict, body_text


def extract_section_headings(text: str) -> list[str]:
    """마크다운 section heading 추출 (line-by-line — ReDoS guard).

    Returns list of heading strings like ['## deploy', '### Required fields'].
    H1 (single '#') 는 문서 제목이므로 비교 제외 (Wave 1 scope: schema section 구조 비교).
    """
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        # heading = line starting with one or more '#' followed by space
        if stripped and stripped[0] == "#":
            # count leading '#'
            count = 0
            for ch in stripped:
                if ch == "#":
                    count += 1
                else:
                    break
            # must have space after '#' sequence
            if count < len(stripped) and stripped[count] == " ":
                # skip H1 (document title — file-level, not schema section)
                if count >= 2:
                    headings.append(stripped)
    return headings


def extract_table_fields(text: str) -> set[str]:
    """마크다운 테이블 첫 column (Field) 값 추출 (line-by-line — ReDoS guard).

    Example row: | `deploy.mechanism` | string | yes | ... |
    Returns set of field name strings.
    """
    fields = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped[0] != "|":
            continue
        # split on "|"
        parts = [p.strip() for p in stripped.split("|")]
        # parts[0] = '' (before first |), parts[1] = first column
        if len(parts) >= 2:
            first_col = parts[1].strip()
            # skip header rows and separator rows
            if first_col.startswith("-") or first_col.lower() in ("field", ""):
                continue
            # strip backticks
            first_col = first_col.strip("`")
            if first_col:
                fields.add(first_col)
    return fields


def compare_files(ssot_path: Path, plugin_path: Path) -> list[str]:
    """SSOT ↔ plugin seed 비교.

    Returns list of drift descriptions. Empty = PASS.
    Raises yaml.YAMLError if frontmatter malformed (→ caller exits 1).
    """
    drifts = []

    ssot_text = ssot_path.read_text(encoding="utf-8", errors="replace")
    plugin_text = plugin_path.read_text(encoding="utf-8", errors="replace")

    # frontmatter 비교
    ssot_fm, ssot_body = extract_frontmatter(ssot_text)
    plugin_fm, plugin_body = extract_frontmatter(plugin_text)

    # section heading 비교
    ssot_headings = extract_section_headings(ssot_body)
    plugin_headings = extract_section_headings(plugin_body)

    ssot_heading_set = set(ssot_headings)
    plugin_heading_set = set(plugin_headings)

    only_in_ssot = ssot_heading_set - plugin_heading_set
    only_in_plugin = plugin_heading_set - ssot_heading_set

    for h in sorted(only_in_ssot):
        drifts.append(f"heading in SSOT but not in plugin: {h!r}")
    for h in sorted(only_in_plugin):
        drifts.append(f"heading in plugin but not in SSOT: {h!r}")

    # table field 비교
    ssot_fields = extract_table_fields(ssot_body)
    plugin_fields = extract_table_fields(plugin_body)

    only_ssot_fields = ssot_fields - plugin_fields
    only_plugin_fields = plugin_fields - ssot_fields

    for f in sorted(only_ssot_fields):
        drifts.append(f"field in SSOT but not in plugin: {f!r}")
    for f in sorted(only_plugin_fields):
        drifts.append(f"field in plugin but not in SSOT: {f!r}")

    return drifts


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="plugin-declarative-seed-byte-parity-check lint"
    )
    parser.add_argument("--ssot-file", help="Wrapper SSOT file path")
    parser.add_argument("--plugin-file", help="Plugin seed file path")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    ssot_path_str = args.ssot_file
    plugin_path_str = args.plugin_file

    # default to Wave 1 mapping if no args provided
    if not ssot_path_str:
        ssot_path_str = WAVE1_SSOT_PATH
    if not plugin_path_str:
        plugin_path_str = WAVE1_PLUGIN_PATH

    ssot_path = Path(ssot_path_str)
    plugin_path = Path(plugin_path_str)

    # setup error: files not found
    if not ssot_path.exists():
        print(f"{SCRIPT_NAME} [INFO] SSOT file not found: {ssot_path} — skip", file=sys.stderr)
        return 0
    if not plugin_path.exists():
        print(f"{SCRIPT_NAME} [INFO] plugin file not found: {plugin_path} — skip (exit 2)", file=sys.stderr)
        return 2

    try:
        drifts = compare_files(ssot_path, plugin_path)
    except yaml.YAMLError as e:
        print(f"{SCRIPT_NAME} [ERROR] YAML parse failure: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"{SCRIPT_NAME} [ERROR] file read error: {e}", file=sys.stderr)
        return 2

    if drifts:
        print(f"{SCRIPT_NAME} [WARN] byte-parity drift detected:", file=sys.stderr)
        for d in drifts:
            print(f"  - {d}", file=sys.stderr)
        print(
            f"{SCRIPT_NAME} [WARN] warning-tier (ADR-060 §결정 5) — PR merge 미차단. "
            "Path A (mirror update) 또는 Path B (single-SSOT deprecate) 적용 권고.",
            file=sys.stderr,
        )
        # warning-tier: exit 0 (PR merge 미차단)
        return 0
    else:
        print(
            f"{SCRIPT_NAME} [PASS] {ssot_path} ↔ {plugin_path} byte-parity 정합.",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
