#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-785 / ADR-077 §결정 9 — ratchet 선언 grep-testable verification (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Invariant 3:
#   (1) ADR-077 frontmatter `is_transitional: false` 존재
#   (2) ADR-077 본문 §결정 9 ratchet 선언 (5 ratchet 속성)
#   (3) ADR-058 §결정 5 sunset_justification 문구
#
# Self-ref graceful (CFP-702/744 교훈): ADR-077 파일 부재 시 sys.exit(0) (sys.exit(1) 금지)
#
# Usage / exit code / semantics 상세: scripts/check-adr-077-ratchet.sh header.
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
    print("⚠ check-adr-077-ratchet: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

ADR_077_PATH = "docs/adr/ADR-077-clarification-forced-reinvestigation-propagation.md"

# grep invariant 3 (ADR-077 본문 + frontmatter)
INVARIANTS = {
    "is_transitional_false": re.compile(r"^is_transitional:\s*false\s*$", re.MULTILINE),
    "ratchet_decision_9": re.compile(
        r"§결정\s*9.*ratchet|ratchet.*§결정\s*9|5\s*ratchet\s*속성",
        re.MULTILINE | re.DOTALL
    ),
    "sunset_justification_ref": re.compile(
        r"ADR-058\s*§결정\s*5.*sunset_justification|sunset_justification.*ADR-058",
        re.MULTILINE | re.DOTALL
    ),
}

violations = []

def main() -> int:
    repo_root = Path.cwd()
    adr_path = repo_root / ADR_077_PATH

    # Self-ref graceful (CFP-702/744 교훈)
    if not adr_path.exists():
        sys.stderr.write(
            f"[adr-077-ratchet-declared] SKIP: {ADR_077_PATH} not found "
            f"(self-ref graceful — continue-on-error)\n"
        )
        return 0

    content = adr_path.read_text(encoding="utf-8")
    violations = []

    for name, pattern in INVARIANTS.items():
        if not pattern.search(content):
            violations.append(name)

    if violations:
        sys.stderr.write(
            f"[adr-077-ratchet-declared] FAIL: missing invariants: {', '.join(violations)}\n"
        )
        sys.stderr.write(
            f"  ADR-077 §결정 9 ratchet 선언 검증 실패 — "
            f"see ADR-058 §결정 5 (ratchet sunset_justification mandate)\n"
        )
        return 1

    sys.stdout.write(
        f"[adr-077-ratchet-declared] PASS: all 3 invariants present in {ADR_077_PATH}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
