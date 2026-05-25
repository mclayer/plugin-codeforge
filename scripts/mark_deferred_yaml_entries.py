"""CFP-1584 Sub-A Phase 2 — mark the 12 unpushed playbook_split_pages entries as deferred.

Reads docs/confluence-ia-tree.yaml, finds each entry whose id is still null
(but skip the CRITICAL Step 0 which already has push_attempt_status), and appends
`push_attempt_status: deferred_to_cfp_1617_session_capacity` to that entry.

Per ADR-061: external file (not heredoc).
"""
from __future__ import annotations

import re
from pathlib import Path

YAML_PATH = Path("docs/confluence-ia-tree.yaml")

# Titles of the 12 entries that should be marked deferred (NOT including Step 0
# which already has its own push_attempt_status set).
DEFERRED_TITLES = {
    "§4 — 병렬 스폰 판단",
    "§6 — FIX 루프 상태 머신",
    "§7 — 세션 재개(resume) 복원 절차",
    "§8 — 토큰 예산 모니터링 + 세션 회고",
    "§9 — 트러블슈팅 플레이북",
    "§12 — Orchestrator 컨텍스트 패킷",
    "§13 — PMOAgent 프로젝트 관리 (Cross-cutting)",
    "§14 — §0 Live Progress (CFP-20)",
    "§15 — 4-channel observability boundary",
    "§16 — Post-merge automation flow",
    "§17 — Inter-plugin contract sibling sync 절차",
    "부록 A — 관련 문서 + 부록 B — 개정 이력",
}


def main() -> int:
    text = YAML_PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)

        # Detect entry start: '  - id: null' (or '  - id: "..."') under playbook_split_pages
        if line.startswith("  - id:"):
            # Look ahead for title line
            block_end = i + 1
            entry_title = None
            while block_end < len(lines) and not lines[block_end].startswith("  - id:") and not lines[block_end].startswith("playbook_split_pages_total"):
                if "title:" in lines[block_end] and entry_title is None:
                    m = re.search(r'title:\s*"([^"]+)"', lines[block_end])
                    if m:
                        entry_title = m.group(1)
                block_end += 1

            if entry_title and entry_title in DEFERRED_TITLES:
                # Walk through the block again, appending push_attempt_status at end
                # First emit the rest of the block normally
                for j in range(i + 1, block_end):
                    out.append(lines[j])
                # Append deferred marker (2-space indent + key)
                out.append('    push_attempt_status: "deferred_to_cfp_1617_session_capacity"\n')
                out.append('    push_failure_reason: "Single-session context capacity exhausted at 7/20 pages; remaining sections deferred to CFP-1617 follow-up carrier per ADR-076 result fidelity"\n')
                i = block_end
                continue

        i += 1

    YAML_PATH.write_text("".join(out), encoding="utf-8")
    print(f"Updated {YAML_PATH}: added deferred marker to {len(DEFERRED_TITLES)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
