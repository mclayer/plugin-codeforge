#!/usr/bin/env python3
"""Generate fixture YAML files for CFP-476 test harness"""
import os

fixtures_dir = "tests/fixtures/post-merge-followup"

fixtures_data = [
    ("cfp-391-false-positive", "CFP-391 #396 false-positive - missing keyword", "UC-1 / EC-9", 400, "#396", 396, False, "skip_no_close_keyword"),
    ("cfp-412-false-positive", "CFP-412 #412 false-positive - missing keyword", "UC-1 / EC-9", 421, "#412", 412, False, "skip_no_close_keyword"),
    ("cfp-455-phase1-skip", "Phase 1 PR - mid-phase block", "UC-2 / EC-1", 460, "#455", 455, False, "skip_phase1"),
    ("cfp-455-phase2-success", "Phase 2 happy path", "UC-3 / AC-2", 461, "#455", 455, True, "success"),
    ("terminal-phase-success", "security_ai=false variant", "UC-2.5 / AC-3", 500, "#500", 500, True, "success"),
    ("dual-source-mismatch", "Source A present, Source B empty", "UC-4 / AC-4", 502, "#502", 502, False, "skip_dual_source_mismatch"),
    ("multi-issue-warning-skip", "Multiple issues detected", "EC-4 / AC-5", 505, "#505+#506", 505, False, "skip_multi_issue"),
    ("qualified-syntax-same-repo", "Qualified same-repo ref", "AC-6", 510, "mclayer/plugin-codeforge#510", 510, True, "success"),
    ("qualified-syntax-cross-repo-skip", "Cross-repo ref", "EC-3 / AC-7", 515, "other-org/other-repo#999", 515, False, "skip_cross_repo_unsupported"),
    ("mid-phase-blocked", "Mid-phase gate block", "UC-2 / EC-1", 520, "#520", 520, False, "skip_phase1"),
    ("chore-pr-skip", "Chore PR guard", "UC-1", 525, "#999", 999, False, "skip_chore"),
    ("multi-cfp-aggregating-skip", "Multi-CFP guard", "UC-1", 530, "#450+#451", 450, False, "skip_multi_cfp"),
    ("source-b-lazy-sync", "Lazy eventual consistency", "UC-6 / AC-15", 535, "#535", 535, True, "success"),
    ("pr-title-with-singlequote", "T2 mitigation - single quote", "AC-16", 540, "#540", 540, True, "success"),
    ("idempotency-probe-dedupe", "AC-17 idempotency", "AC-17", 545, "#545", 545, False, "skip_already_audited"),
]

for idx, (key, desc, mapping, pr_num, closes_ref, issue_num, has_source_b, outcome) in enumerate(fixtures_data, 1):
    fname = f"0{idx}" if idx < 10 else str(idx)
    filename = os.path.join(fixtures_dir, f"{fname}-{key}.yml")

    # Determine phase based on scenario
    if "phase1" in key or "phase-1" in key.lower():
        phase = "phase:설계-리뷰"
    elif "success" in key or "matched" in key or "source-b" in key:
        phase = "phase:보안-테스트"
    elif "security_ai=false" in desc or "false" in key:
        phase = "phase:구현-테스트"
    elif "multi-issue" in key:
        phase = "phase:보안-테스트"
    elif "chore" in key:
        phase = "phase:보안-테스트"
    elif "multi-cfp" in key:
        phase = "phase:보안-테스트"
    else:
        phase = "phase:보안-테스트"

    # Build closes body
    if "+" in closes_ref:
        closes_body = "\n".join([f"Closes {ref}" for ref in closes_ref.split("+")])
    else:
        closes_body = f"Closes {closes_ref}"

    # Determine security_ai
    security_ai = "false"
    if "false" in key or "security_ai=false" in desc:
        security_ai = "false"
    else:
        security_ai = "true"

    # Build PR body
    pr_body_content = f"Implementation details.\n\n{closes_body}"

    # Build closed_by_pull_requests_references
    if has_source_b:
        closed_refs = [pr_num]
    else:
        closed_refs = []

    content = f"""---
description: "{desc}"
fixture_key: "{key}"
story_mapping: "{mapping}"
pr:
  number: {pr_num}
  title: "[CFP-476] Phase 2 - {key}"
  body: |
    {pr_body_content}
  labels:
    - "{phase}"
    - "type:feature"
issue:
  number: {issue_num}
  closed_by_pull_requests_references: {closed_refs}
consumer_config:
  lanes:
    security_ai: {security_ai}
expected_outcome: "{outcome}"
expected_audit_marker: null
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Created {filename}")

print(f"\nTotal: {len(fixtures_data)} fixtures created")
