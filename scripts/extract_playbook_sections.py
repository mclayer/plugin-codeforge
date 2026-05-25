"""CFP-1584 Sub-A Phase 2 — extract 20 playbook.md sections by heading anchor.

Reads docs/orchestrator-playbook.md, parses by '## ' heading boundaries,
and writes each section into scripts/cfp-1584-sections/<slug>.md.

Special handling:
- "## 부록 A. 관련 문서 + ## 부록 B. 개정 이력" -> concat both sections
- Output filenames numbered 01..20 for deterministic ordering.

Per ADR-061: this is an external file, not a heredoc. Run with:
    python scripts/extract_playbook_sections.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PLAYBOOK = Path("docs/orchestrator-playbook.md")
OUT_DIR = Path("scripts/cfp-1584-sections")

# (order, slug, source_section anchor, title-for-yaml)
# Order matches playbook_split_pages[] in confluence-ia-tree.yaml exactly.
ENTRIES = [
    (1,  "01_section1",  "## 1. 세션 생명주기"),
    (2,  "02_section2",  "## 2. 사용자(Human) 상호작용 규약"),
    (3,  "03_section3",  "## 3. 스폰 시퀀스 + 프롬프트 템플릿"),
    (4,  "04_critical_step0", "## CRITICAL Step 0 — pre-spawn-pin (mandatory, ADR-039 §결정 14)"),
    (5,  "05_section3B", "## 3B. Preflight 체크 (lane 진입 직전)"),
    (6,  "06_section4",  "## 4. 병렬 스폰 판단"),
    (7,  "07_section5",  "## 5. docs/stories file 동기화"),
    (8,  "08_section6",  "## 6. FIX 루프 상태 머신"),
    (9,  "09_section7",  "## 7. 세션 재개(resume) 복원 절차"),
    (10, "10_section8",  "## 8. 토큰 예산 모니터링 + 세션 회고"),
    (11, "11_section9",  "## 9. 트러블슈팅 플레이북"),
    (12, "12_section10", "## 10. Hotfix 경로 (운영 장애 대응)"),
    (13, "13_section11", "## 11. Cross-agent write coordination"),
    (14, "14_section12", "## 12. Orchestrator 컨텍스트 패킷 (Story file 섹션 캐시)"),
    (15, "15_section13", "## 13. PMOAgent 프로젝트 관리 (Cross-cutting)"),
    (16, "16_section14", "## 14. §0 Live Progress (CFP-20)"),
    (17, "17_section15", "## 15. 4-channel observability boundary (ADR-042 §결정 1, CFP-283)"),
    (18, "18_section16", "## 16. Post-merge automation flow (ADR-026 + CFP-74)"),
    (19, "19_section17", "## 17. Inter-plugin contract sibling sync 절차 (CFP-408 / ADR-010 Amendment 3)"),
    (20, "20_appendix_AB", None),  # special: combines 부록 A + B
]


def find_header_line(lines: list[str], header: str) -> int:
    """Find the index of the line matching `header` exactly (trailing newline stripped)."""
    for i, line in enumerate(lines):
        if line.rstrip("\n") == header:
            return i
    raise SystemExit(f"ERROR: header not found: {header!r}")


def main() -> int:
    if not PLAYBOOK.exists():
        print(f"ERROR: {PLAYBOOK} not found (cwd={os.getcwd()})", file=sys.stderr)
        return 1

    text = PLAYBOOK.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    print(f"Loaded {PLAYBOOK}: {len(lines)} lines, {len(text)} bytes")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Resolve start line for each entry first (anchored at known headers).
    # End for entry N = start of entry N+1 (except for entry 20 which spans up to EOF).
    # Entry 20 is special (부록 A + 부록 B concat).
    starts: dict[int, int] = {}
    for order, slug, header in ENTRIES:
        if order == 20:
            # 부록 A 시작점만 기록 (B는 별도로 처리)
            starts[order] = find_header_line(lines, "## 부록 A. 관련 문서")
        else:
            starts[order] = find_header_line(lines, header)

    # Verify monotonic increasing
    sorted_orders = sorted(starts.keys())
    for k in range(1, len(sorted_orders)):
        if starts[sorted_orders[k]] <= starts[sorted_orders[k-1]]:
            print(f"WARN: non-monotonic anchors: order {sorted_orders[k-1]} at line {starts[sorted_orders[k-1]]+1} >= order {sorted_orders[k]} at line {starts[sorted_orders[k]]+1}", file=sys.stderr)

    report = []
    for idx, (order, slug, header) in enumerate(ENTRIES):
        s = starts[order]
        if order < 20:
            # End = start of next entry
            next_order = ENTRIES[idx + 1][0]
            e = starts[next_order]
            content = "".join(lines[s:e])
            line_range = (s + 1, e)
        else:
            # Entry 20: 부록 A starts at s, runs to start of 부록 B,
            # then 부록 B runs to EOF.
            b_start = find_header_line(lines, "## 부록 B. 개정 이력")
            content = "".join(lines[s:b_start]) + "".join(lines[b_start:])
            line_range = (s + 1, len(lines))

        outfile = OUT_DIR / f"{slug}.md"
        outfile.write_text(content, encoding="utf-8")
        byte_size = len(content.encode("utf-8"))
        line_count = content.count("\n")
        report.append((order, slug, line_range, line_count, byte_size, header))
        print(f"  [{order:02d}] {slug}.md  lines={line_count:5d}  bytes={byte_size:7d}  range={line_range}")

    print(f"\nTotal sections extracted: {len(ENTRIES)}")
    print(f"Total bytes: {sum(r[4] for r in report)}")
    print(f"Output dir: {OUT_DIR.resolve()}")

    # Sanity check: total bytes should be close to playbook total minus frontmatter+preamble
    total_extracted = sum(r[4] for r in report)
    print(f"Playbook total bytes: {len(text)}  Extracted: {total_extracted}  Gap: {len(text) - total_extracted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
