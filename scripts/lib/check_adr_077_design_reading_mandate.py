#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-785 / ADR-077 §결정 3 — design-reading 깊이 강화 mandate grep-testable verification (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Invariant 3:
#   (1) ADR-077 본문 §결정 3 "skim 금지" 문구 존재
#   (2) ADR-077 본문 §결정 3 "의도" + "근거" 표현 존재 (의도/근거 파악)
#   (3) 적용 3 agent verbatim: ChangeImpactAgent, FeasibilityAgent, ContinuityAgent 전부 등장 (AND)
#
# Self-ref graceful (CFP-702/744 교훈): ADR-077 파일 부재 시 sys.exit(0) (sys.exit(1) 금지)
#
# Usage / exit code / semantics 상세: scripts/check-adr-077-design-reading-mandate.sh header.
import sys
import re
import os
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("⚠ check-adr-077-design-reading-mandate: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

ADR_077_PATH = "docs/adr/ADR-077-clarification-forced-reinvestigation-propagation.md"

# grep invariant 3 (ADR-077 본문 §결정 3 design-reading mandate)
INVARIANTS = {
    "skim_prohibition": re.compile(r"skim\s*금지", re.MULTILINE),
    "intent_rationale": re.compile(r"의도.*근거|근거.*의도", re.MULTILINE | re.DOTALL),
}

APPLIED_AGENTS = ["ChangeImpactAgent", "FeasibilityAgent", "ContinuityAgent"]

violations = []


def main() -> int:
    repo_root = Path.cwd()
    adr_path = repo_root / ADR_077_PATH

    # Self-ref graceful (CFP-702/744 교훈)
    if not adr_path.exists():
        sys.stderr.write(
            f"[adr-077-design-reading-mandate-declared] SKIP: {ADR_077_PATH} not found "
            f"(self-ref graceful)\n"
        )
        return 0

    content = adr_path.read_text(encoding="utf-8")
    violations = []

    # Invariant (1)/(2) — pattern search
    for name, pattern in INVARIANTS.items():
        if not pattern.search(content):
            violations.append(name)

    # Invariant (3) — 3 agent AND 조건
    missing_agents = [a for a in APPLIED_AGENTS if a not in content]
    if missing_agents:
        violations.append(f"applied_agents_missing: {', '.join(missing_agents)}")

    if violations:
        sys.stderr.write(
            f"[adr-077-design-reading-mandate-declared] FAIL: missing: {', '.join(violations)}\n"
        )
        sys.stderr.write(
            f"  ADR-077 §결정 3 design-reading mandate 검증 실패 "
            f"(skim 금지 + 의도/근거 + 3 agent verbatim)\n"
        )
        return 1

    sys.stdout.write(
        f"[adr-077-design-reading-mandate-declared] PASS: all invariants + "
        f"3 agent identifiers present in {ADR_077_PATH}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
