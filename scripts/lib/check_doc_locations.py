#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-276 — Doc Location Registry validator (issue #276)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# byte_exempt: datetime.now time source — Last regen timestamp differs per run.
#
# Modes:
#   default  — validation only (6 checks)
#   --regen  — regenerate docs/doc-location-registry.md from docs/doc-locations.yaml
#   --check-freshness — round-trip diff (regen to /tmp + diff against committed)
#   --full   — validation + freshness check (CI default)
#
# SSOT: docs/doc-locations.yaml + ADR-038
#
# Usage / exit code / semantics 상세: scripts/check-doc-locations.sh header.
import sys, os, re, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("WARN check-doc-locations: pyyaml missing, skip", file=sys.stderr)
    sys.exit(0)

YAML_PATH = Path("docs/doc-locations.yaml")
REGISTRY_PATH = Path("docs/doc-location-registry.md")

if not YAML_PATH.exists():
    print("OK check-doc-locations: docs/doc-locations.yaml absent, skip", file=sys.stderr)
    sys.exit(0)

TOP_LEVEL_REQUIRED = ["schema_version", "introduced_by", "last_updated",
                      "allowed_variants", "allowed_placeholders",
                      "dogfood_scope", "doc_types"]
DOC_TYPE_REQUIRED = ["name", "variants", "owner_agent", "introduced_by"]
PLACEHOLDER_RE = re.compile(r"<[A-Za-z_-]+>")

errors = []


def get_mode():
    args = sys.argv[1:]
    if not args:
        return os.environ.get("DOC_LOC_MODE", "default")
    return args[0]


mode_arg = get_mode()

try:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
except Exception as e:
    print(f"::error::doc-locations.yaml parse failure: {e}", file=sys.stderr)
    sys.exit(1)

if not isinstance(data, dict):
    print("::error::top-level must be a mapping", file=sys.stderr)
    sys.exit(1)

# [1/7] top-level shape
for key in TOP_LEVEL_REQUIRED:
    if key not in data:
        errors.append(f"[1/7] top-level missing required key: '{key}'")

if not isinstance(data.get("doc_types"), list):
    errors.append("[1/7] doc_types must be a list")

if errors:
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    sys.exit(1)

print(f"OK [1/7] top-level shape ({len(data['doc_types'])} doc_types)", file=sys.stderr)

# [2/7] per-doc-type required fields
for i, dt in enumerate(data.get("doc_types", [])):
    if not isinstance(dt, dict):
        errors.append(f"[2/7] doc_types[{i}] must be a mapping")
        continue
    for f in DOC_TYPE_REQUIRED:
        if f not in dt:
            errors.append(f"[2/7] doc_types[{i}] missing required field: '{f}'")
    variants = dt.get("variants", {})
    if not isinstance(variants, dict) or all(v is None for v in variants.values()):
        errors.append(f"[2/7] doc_types[{i}] '{dt.get('name','?')}' must have at least one non-null variant")

if errors:
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    sys.exit(1)

print("OK [2/7] per-doc-type required fields", file=sys.stderr)

# [3/7] variant key allowlist
allowed_variants = set(data.get("allowed_variants", []))
for i, dt in enumerate(data.get("doc_types", [])):
    name = dt.get("name", "?")
    for vk in (dt.get("variants") or {}).keys():
        if vk not in allowed_variants:
            errors.append(f"[3/7] doc_types[{i}] '{name}': variant key '{vk}' not in allowed_variants {sorted(allowed_variants)}")

if errors:
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    sys.exit(1)

print("OK [3/7] variant key allowlist", file=sys.stderr)

# [4/7] placeholder allowlist
allowed_placeholders = set(data.get("allowed_placeholders", []))
for i, dt in enumerate(data.get("doc_types", [])):
    name = dt.get("name", "?")
    for vk, vpath in (dt.get("variants") or {}).items():
        if vpath is None:
            continue
        for ph in PLACEHOLDER_RE.findall(str(vpath)):
            if ph not in allowed_placeholders:
                errors.append(f"[4/7] doc_types[{i}] '{name}'.{vk}: placeholder '{ph}' not in allowed_placeholders")

if errors:
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    sys.exit(1)

print("OK [4/7] placeholder allowlist", file=sys.stderr)

# [5/7] no absolute paths
# 예외: placeholder (<...>) 를 포함한 URL template 은 실 절대 URL 이 아님 (confluence variant 등)
for i, dt in enumerate(data.get("doc_types", [])):
    name = dt.get("name", "?")
    for vk, vpath in (dt.get("variants") or {}).items():
        if vpath is None:
            continue
        s = str(vpath)
        has_placeholder = bool(PLACEHOLDER_RE.search(s))
        if (s.startswith("/") or s.startswith("https://") or s.startswith("http://")) and not has_placeholder:
            errors.append(f"[5/7] doc_types[{i}] '{name}'.{vk}: absolute path forbidden ('{s[:60]}...')")

if errors:
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    sys.exit(1)

print("OK [5/7] no absolute paths", file=sys.stderr)

# [6/7] doc_type name uniqueness
seen_names = set()
for i, dt in enumerate(data.get("doc_types", [])):
    name = dt.get("name", "")
    if name in seen_names:
        errors.append(f"[6/7] duplicate doc_type name: '{name}' (index {i})")
    seen_names.add(name)

if errors:
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    sys.exit(1)

print("OK [6/7] doc_type name uniqueness", file=sys.stderr)


def render_markdown(d):
    lines = []
    lines.append("<!-- DO NOT EDIT - auto-generated from docs/doc-locations.yaml -->")
    lines.append("<!-- Regenerate: ./scripts/check-doc-locations.sh --regen -->")
    lines.append("")
    lines.append("# Doc Location Registry (auto-generated)")
    lines.append("")
    lines.append(f"**Source SSOT**: [`docs/doc-locations.yaml`](doc-locations.yaml)  ")
    lines.append(f"**schema_version**: {d.get('schema_version')}  ")
    lines.append(f"**Last regen**: {datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None).isoformat()}Z  ")
    lines.append(f"**Registered doc types**: {len(d.get('doc_types', []))}")
    lines.append("")
    lines.append("## Summary table")
    lines.append("")
    lines.append("| # | doc_type | variants | owner | introduced_by |")
    lines.append("|---|---|---|---|---|")
    for i, dt in enumerate(d.get("doc_types", []), 1):
        variants = " / ".join(sorted((dt.get("variants") or {}).keys()))
        lines.append(f"| {i} | `{dt.get('name')}` | {variants} | `{dt.get('owner_agent')}` | {dt.get('introduced_by')} |")
    lines.append("")
    lines.append("## Per-doc-type details")
    lines.append("")
    for dt in d.get("doc_types", []):
        lines.append(f"### `{dt.get('name')}`")
        lines.append("")
        for vk, vpath in (dt.get("variants") or {}).items():
            lines.append(f"- **{vk}**: `{vpath}`")
        lines.append(f"- **owner_agent**: `{dt.get('owner_agent')}`")
        lines.append(f"- **introduced_by**: {dt.get('introduced_by')}")
        if dt.get("naming_pattern"):
            lines.append(f"- **naming_pattern**: `{dt['naming_pattern']}`")
        lines.append(f"- **frontmatter_required**: {dt.get('frontmatter_required')}")
        examples = dt.get("examples") or []
        if examples:
            lines.append("- **examples**:")
            for ex in examples:
                lines.append(f"  - {ex}")
        notes = dt.get("notes")
        if notes:
            lines.append("")
            lines.append("  **notes**:")
            for nl in str(notes).strip().split("\n"):
                lines.append(f"  > {nl}")
        lines.append("")
    return "\n".join(lines) + "\n"


if mode_arg == "--regen":
    md = render_markdown(data)
    REGISTRY_PATH.write_text(md, encoding="utf-8")
    print(f"OK regenerated {REGISTRY_PATH} ({len(data.get('doc_types', []))} doc types)", file=sys.stderr)
    sys.exit(0)

if mode_arg in ("--check-freshness", "--full"):
    expected_md = render_markdown(data)
    actual_md = REGISTRY_PATH.read_text(encoding="utf-8") if REGISTRY_PATH.exists() else ""
    norm_re = re.compile(r"\*\*Last regen\*\*: [^\n]+")
    if norm_re.sub("**Last regen**: <NORMALIZED>", expected_md) != norm_re.sub("**Last regen**: <NORMALIZED>", actual_md):
        print("::error::[7/7] doc-location-registry.md stale - regenerate via: ./scripts/check-doc-locations.sh --regen", file=sys.stderr)
        sys.exit(1)
    print("OK [7/7] doc-location-registry.md freshness", file=sys.stderr)

print("OK check-doc-locations: validation passed", file=sys.stderr)
