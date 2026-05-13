#!/usr/bin/env python3
"""CFP-582 Phase 2 — Debate Convergence Quality Lint.

ADR-059 Amendment 2 §결정 8 convergence_quality_invariant 의 mechanical enforcement.
Story §9 debate transcript 내 3 marker pattern presence 검증.

Markers (debate-protocol-v1 v1.2 schema 정합):
- [COUNTERARGUMENT]       — Round 1+ 매 라운드 per worker 출력 의무
- [ALTERNATIVE_PROPOSED]  — debate cumulative >= 1 의무
- [DEBATE_PURPOSE_STATEMENT] — Round 0 only 의무

Transcript section 탐지:
  ### Debate transcript: <anchor_id>

CLI:
  python scripts/check_debate_convergence_quality.py <story_file_path>

Exit code (ADR-060 Amendment 2 §결정 15 tri-tier):
  0 = PASS (3 marker 모두 present, 또는 transcript section 자체 없음 = not applicable)
  1 = WARNING (1+ marker missing — warning tier, continue-on-error 정합)
  2 = ERROR (파일 미존재 / parse error 등)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRANSCRIPT_SECTION_RE = re.compile(
    r"^###\s+Debate\s+transcript:\s+(.+)$",
    re.MULTILINE | re.IGNORECASE,
)

MARKER_COUNTERARGUMENT = re.compile(r"\[COUNTERARGUMENT\]")
MARKER_ALTERNATIVE_PROPOSED = re.compile(r"\[ALTERNATIVE_PROPOSED\]")
MARKER_DEBATE_PURPOSE_STATEMENT = re.compile(r"\[DEBATE_PURPOSE_STATEMENT\]")

REQUIRED_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("COUNTERARGUMENT", MARKER_COUNTERARGUMENT),
    ("ALTERNATIVE_PROPOSED", MARKER_ALTERNATIVE_PROPOSED),
    ("DEBATE_PURPOSE_STATEMENT", MARKER_DEBATE_PURPOSE_STATEMENT),
)

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _extract_transcript_blocks(content: str) -> list[tuple[str, str]]:
    """Story 파일 내 debate transcript block 목록 반환.

    Returns:
        list of (anchor_id, block_text) — 각 transcript 섹션의 텍스트.
        transcript 섹션이 없으면 빈 list 반환.
    """
    matches = list(TRANSCRIPT_SECTION_RE.finditer(content))
    if not matches:
        return []

    blocks: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        anchor_id = match.group(1).strip()
        start = match.start()
        # 다음 transcript section 직전까지 또는 파일 끝까지
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)
        block_text = content[start:end]
        blocks.append((anchor_id, block_text))
    return blocks


def _check_transcript_block(anchor_id: str, block_text: str) -> list[str]:
    """transcript block 내 3 marker presence 검사.

    Returns:
        list of missing marker names. 모두 present 면 빈 list.
    """
    missing: list[str] = []
    for name, pattern in REQUIRED_MARKERS:
        if not pattern.search(block_text):
            missing.append(name)
    return missing


# ---------------------------------------------------------------------------
# Main checker function
# ---------------------------------------------------------------------------


def check_file(file_path: str) -> int:
    """Story 파일 단일 대상 검사.

    Args:
        file_path: 검사할 Story .md 파일 경로 (str 또는 Path-like).

    Returns:
        0 = PASS (violation 없음 또는 transcript section 없음)
        1 = WARNING (1+ marker missing)
        2 = ERROR (파일 미존재 / 읽기 실패)
    """
    path = Path(file_path)
    if not path.exists():
        sys.stderr.write(
            f"[debate-convergence-quality] ERROR 파일 미존재: {file_path}\n"
        )
        return 2

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        sys.stderr.write(
            f"[debate-convergence-quality] ERROR 파일 읽기 실패: {file_path}: {exc}\n"
        )
        return 2

    blocks = _extract_transcript_blocks(content)
    if not blocks:
        # transcript section 없음 = not applicable → PASS
        sys.stdout.write(
            f"[debate-convergence-quality] PASS (not applicable — transcript section 없음): {file_path}\n"
        )
        return 0

    total_violations: list[str] = []
    for anchor_id, block_text in blocks:
        missing = _check_transcript_block(anchor_id, block_text)
        if missing:
            for marker_name in missing:
                violation_msg = (
                    f"  [{anchor_id}] [{marker_name}] marker 누락"
                )
                total_violations.append(violation_msg)
                sys.stderr.write(
                    f"[debate-convergence-quality] WARNING {violation_msg}\n"
                )

    if total_violations:
        sys.stderr.write(
            f"[debate-convergence-quality] WARNING {len(total_violations)} violation(s) in {file_path}\n"
        )
        return 1

    sys.stdout.write(
        f"[debate-convergence-quality] PASS ({len(blocks)} transcript(s) checked): {file_path}\n"
    )
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI: python scripts/check_debate_convergence_quality.py <story_file_path>."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        sys.stderr.write(
            "Usage: python scripts/check_debate_convergence_quality.py <story_file_path>\n"
        )
        return 2

    file_path = args[0]
    return check_file(file_path)


if __name__ == "__main__":
    sys.exit(main())
