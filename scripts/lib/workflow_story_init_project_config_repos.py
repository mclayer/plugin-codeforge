#!/usr/bin/env python3
"""
Extract codeforge.stories.repos[] and component→repo mapping from project.yaml.
Fallback helper for yq (PyYAML-based).

CFP-2423 / ADR-069 Amendment 1 (Phase 2) — multi-repo component routing.

Usage:
  CFG_PATH=.claude/_overlay/project.yaml python3 workflow_story_init_project_config_repos.py
  # self-test (fixture validation):
  python3 workflow_story_init_project_config_repos.py --self-test

Output (stdout, one mapping per line):
  <component>\t<github_repo>
  ...
  Exit 0 with empty stdout if codeforge.stories.repos[] absent.
  Exit 1 on YAML parse error or self-test FAIL.

Behavior:
  - Read codeforge.stories.repos[] list
  - For each repo: iterate components[] (list of component names)
  - Output each component as-is (raw, no normalization — workflow shell normalizes during matching)
  - Output line: component\tgithub_repo_value (one mapping per line)
  - No deduplication (workflow handles multi-mapping detection)
  - Normalization (lowercase+trim) applied in workflow shell for matching consistency with yq path
  - Windows cp949 stdout protected via reconfigure(encoding="utf-8")

Environment:
  CFG_PATH: path to project.yaml (required for normal mode)
"""

import sys
import os
import yaml
import tempfile

# Windows cp949 stdout protection (must be early, before any print)
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

def extract_mappings(data: dict) -> list[str]:
    """Extract repos[].components[] → mappings from parsed YAML data.

    Returns list of "component\tgithub" strings (raw format, no normalization).
    """
    mappings = []

    if data is None or not isinstance(data, dict):
        return mappings

    # Navigate codeforge -> stories -> repos
    codeforge = data.get('codeforge')
    if codeforge is None or not isinstance(codeforge, dict):
        return mappings

    stories = codeforge.get('stories')
    if stories is None or not isinstance(stories, dict):
        return mappings

    repos = stories.get('repos')
    if repos is None or not isinstance(repos, list):
        return mappings

    # Extract repos[].github + repos[].components[] mappings
    for repo_entry in repos:
        if not isinstance(repo_entry, dict):
            continue

        github_repo = repo_entry.get('github')
        if not isinstance(github_repo, str) or not github_repo.strip():
            # github field missing or empty — skip this entry
            continue

        github_repo = github_repo.strip()

        components = repo_entry.get('components')
        if components is None or not isinstance(components, list):
            # components[] absent or not a list — skip this entry
            continue

        # For each component in the list
        for component in components:
            if not isinstance(component, str):
                continue

            # Output as-is (raw component name, no normalization)
            # Normalization (lowercase+trim) applied in workflow shell during matching
            # This ensures both yq and python paths output identical format
            component_raw = component.strip()
            if component_raw:
                # Output: component\tgithub_repo (raw format, matching yq output)
                mappings.append(f"{component_raw}\t{github_repo}")

    return mappings


def main():

    cfg_path = os.environ.get('CFG_PATH')
    if not cfg_path:
        # Silent no-op if CFG_PATH not set
        sys.exit(0)

    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        # project.yaml absent — no-op
        sys.exit(0)
    except yaml.YAMLError as e:
        print(f"YAML parse error in {cfg_path}: {e}", file=sys.stderr)
        sys.exit(1)

    mappings = extract_mappings(data)
    for mapping in mappings:
        print(mapping)

    sys.exit(0)


# Self-test truth-table (8 case — fixture validation)
SELF_TEST_TABLE = [
    # (id, yaml_content, expect_mappings, note)
    (
        "TC-HELPER-1",
        """
codeforge:
  stories:
    repos:
      - github: mclayer/mctrader-data
        components:
          - data
          - storage
""",
        ["data\tmclayer/mctrader-data", "storage\tmclayer/mctrader-data"],
        "2 components → 2 mappings",
    ),
    (
        "TC-HELPER-2",
        """
codeforge:
  stories:
    repos:
      - github: mclayer/mctrader-data
        components: []
""",
        [],
        "empty components[] → 0 mappings",
    ),
    (
        "TC-HELPER-3",
        """
codeforge:
  stories:
    repos:
      - github: mclayer/mctrader-data
        # components absent
""",
        [],
        "components absent → skip entry",
    ),
    (
        "TC-HELPER-4",
        """
codeforge:
  stories: {}
""",
        [],
        "repos absent → 0 mappings",
    ),
    (
        "TC-HELPER-5",
        """
codeforge:
  stories:
    repos:
      - github: ""
        components:
          - data
""",
        [],
        "github empty string → skip entry",
    ),
    (
        "TC-HELPER-6",
        """
codeforge:
  stories:
    repos:
      - github: mclayer/mctrader-data
        components:
          - "  data  "
""",
        ["data\tmclayer/mctrader-data"],
        "component with whitespace → trimmed in output",
    ),
    (
        "TC-HELPER-7",
        """
""",
        [],
        "empty YAML → 0 mappings",
    ),
    (
        "TC-HELPER-8",
        """
codeforge:
  stories:
    repos:
      - github: repoA
        components:
          - risk
      - github: repoB
        components:
          - risk
""",
        ["risk\trepoA", "risk\trepoB"],
        "same component in 2 repos (multi-mapping) → 2 distinct mappings output",
    ),
]


def run_self_test() -> int:
    failures = []
    for case_id, yaml_content, expect_mappings, note in SELF_TEST_TABLE:
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            print(f"[FAIL] {case_id}: YAML parse error: {e} — {note}", file=sys.stderr)
            failures.append(case_id)
            continue

        got_mappings = extract_mappings(data)

        # Compare: order-sensitive (no sort for determinism)
        if got_mappings == expect_mappings:
            status = "PASS"
        else:
            status = "FAIL"
            failures.append(case_id)

        line = (
            f"[{status}] {case_id}: expect {len(expect_mappings)} mappings, "
            f"got {len(got_mappings)} — {note}"
        )
        print(line)
        if status == "FAIL":
            print(f"  expect: {expect_mappings}", file=sys.stderr)
            print(f"  got:    {got_mappings}", file=sys.stderr)

    print(f"\n{len(SELF_TEST_TABLE) - len(failures)}/{len(SELF_TEST_TABLE)} self-test case PASS")
    if failures:
        print(f"FAIL: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    if "--self-test" in sys.argv:
        sys.exit(run_self_test())
    main()
