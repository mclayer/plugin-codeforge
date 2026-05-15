#!/usr/bin/env python3
# sync_required_workflows.py — CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A
# SSOT extracted from sync-required-workflows.sh parse_spec() heredoc.
#
# Purpose: Parse required-workflows-spec.yaml and print TSV rows for each workflow.
# Format:  <enterprise_slug>\t<source_repo>\t<wf_id>\t<source_workflow>\t<target>
#
# Usage:   python3 scripts/lib/sync_required_workflows.py <spec_file>
# Args:    spec_file — path to required-workflows-spec.yaml
# Exit:    0=ok, 1=error (file not found, parse error), 2=no pyyaml.
import sys

try:
    import yaml
except ImportError:
    print("sync_required_workflows: pyyaml 미설치", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <spec_file>", file=sys.stderr)
        return 1

    spec_file = sys.argv[1]
    try:
        with open(spec_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: spec file not found: {spec_file}", file=sys.stderr)
        return 1
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error: {exc}", file=sys.stderr)
        return 1

    enterprise = data.get("enterprise_slug", "")
    source_repo = data.get("source_repo", "")
    for wf in data.get("required_workflows", []):
        print(
            f"{enterprise}\t{source_repo}\t{wf['id']}\t{wf['source_workflow']}\t{wf['target']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
