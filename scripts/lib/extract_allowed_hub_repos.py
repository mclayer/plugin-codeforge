#!/usr/bin/env python3
"""
Extract phase_gate.allowed_hub_repos[] from project.yaml.
ADR-061 compliant — external .py file, no heredoc.

Usage:
  python3 scripts/lib/extract_allowed_hub_repos.py <project_yaml_path>

Output:
  Line-separated list of allowed hub repos (one per line).
  Exit 0 with empty stdout if field not found or project.yaml absent.
  Exit 1 on YAML parse error.
"""

import sys
import yaml

def extract_allowed_hub_repos(project_yaml_path):
    """Extract phase_gate.allowed_hub_repos[] from project.yaml."""
    try:
        with open(project_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        # project.yaml absent — no-op
        sys.exit(0)
    except yaml.YAMLError as e:
        print(f"YAML parse error in {project_yaml_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if data is None or not isinstance(data, dict):
        # Empty or invalid YAML — no-op
        sys.exit(0)

    # Navigate phase_gate -> allowed_hub_repos
    phase_gate = data.get('phase_gate')
    if phase_gate is None or not isinstance(phase_gate, dict):
        # phase_gate block absent — no-op
        sys.exit(0)

    allowed_hub_repos = phase_gate.get('allowed_hub_repos')
    if allowed_hub_repos is None or not isinstance(allowed_hub_repos, list):
        # allowed_hub_repos field absent or not a list — no-op
        sys.exit(0)

    # Output each repo on separate line
    for repo in allowed_hub_repos:
        if isinstance(repo, str):
            print(repo)

    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_allowed_hub_repos.py <project_yaml_path>", file=sys.stderr)
        sys.exit(1)
    extract_allowed_hub_repos(sys.argv[1])
