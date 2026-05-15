"""
workflow_branch_protection_drift_check.py
CFP-478 Phase 2 sub-PR b — ADR-061 Amendment 1 §결정 1.B
Block #26: branch-protection-drift-check.yml lines 38-48
(Extract expected contexts from branch-protection-manifest.yaml, write to /tmp/expected_contexts.txt)

Usage (via workflow YAML run: block):
  python3 "${GITHUB_WORKSPACE}/scripts/lib/workflow_branch_protection_drift_check.py"

No env injection needed — reads manifest file from GITHUB_WORKSPACE directly.
"""
import sys
import os


def main() -> None:
    try:
        import yaml
    except ImportError:
        print("::error::PyYAML not available — install pyyaml", file=sys.stderr)
        sys.exit(1)

    workspace = os.environ.get("GITHUB_WORKSPACE", ".")
    manifest_path = os.path.join(workspace, "templates/branch-protection-manifest.yaml")

    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    contexts = manifest["required_status_checks"]["contexts"]
    names = sorted(c["name"] for c in contexts)

    with open("/tmp/expected_contexts.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(names) + "\n")


if __name__ == "__main__":
    main()
