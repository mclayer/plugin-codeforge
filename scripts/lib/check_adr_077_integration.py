#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-848 / ADR-077 §결정 8 — stale 게이트·envelope·4-layer disjoint runtime integration lint
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
# CFP-897 — regex_overmatch precision (negation lookahead + table-row-only + code-block strip)
#
# Grep surface G-1..G-5 (Change Plan §3 D5 / Story §7.2):
#   G-1: stale-gate 진입 차단 declare 존재 (Story file §9.0 or cross-ref)
#   G-2: 재조사 카운터 ↔ §10 disjoint (negative grep on §10 표 row data only — CFP-897 prose excl)
#   G-3: ESCALATE escape valve class (escalation_class:scope_redefinition_required + failure/abort 미동반)
#        — CFP-897: negation marker exclude (NOT failure / abort 아님 / 미동반 등 정상 declare 차단)
#   G-4: 4-layer disjoint 무손상 (negative grep on §10 표 헤더/row data only — CFP-897 prose excl)
#   G-5: cross-Story 통합 일관성 checklist 존재
#
# Target: wrapper/stories/CFP-*.md (Story files) — disjoint from ADR-doc lint paths
# Self-ref graceful (CFP-702/744 교훈): Story file 부재 시 sys.exit(0)
# Code-block strip (CFP-897): ``` fenced 또는 inline `code` 안 lint spec 인용 self-ref FP 차단
#
# Usage / exit code / semantics: scripts/check-adr-077-integration.sh header.
import sys
import re
import glob
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
    print("⚠ check-adr-077-integration: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

# Story file target glob (internal-docs path OR wrapper-local stories)
STORY_GLOB_PATTERNS = [
    "wrapper/stories/CFP-*.md",
    "docs/stories/CFP-*.md",
]

# ─── G-1: stale-gate 진입 차단 declare (positive grep) ───
# "stale 마킹 ↔ phase:설계 진입 차단" 또는 "재조사 완료 전 차단" 또는 ADR-077 §결정 8 cross-ref
G1_STALE_GATE = re.compile(
    r"stale.{0,30}(마킹|gate|게이트).{0,80}(차단|block|precondition)"
    r"|재조사.{0,30}완료.{0,30}전.{0,30}차단"
    r"|ADR-077.*§결정\s*8"
    r"|§결정\s*8.*ADR-077",
    re.MULTILINE | re.DOTALL,
)

# ─── G-2: 재조사 카운터 ↔ §10 disjoint (positive declare + negative cross-pollinate) ───
# Positive: §10 FIX Ledger 와 disjoint 선언 문구
G2_DISJOINT_DECLARE = re.compile(
    r"(disjoint|물리.{0,10}분리|분리.{0,10}disjoint|§10.{0,30}합산.{0,20}금지"
    r"|합산.{0,30}금지.{0,30}§10|recheck.{0,30}disjoint|cross-pollinate.{0,30}0)",
    re.MULTILINE | re.DOTALL,
)

# ─── G-3: ESCALATE escape valve ───
# ESCALATE 출현 시 escalation_class:scope_redefinition_required 동반 의무
G3_ESCALATE_PATTERN = re.compile(r"ESCALATE", re.MULTILINE)
G3_ESCALATION_CLASS = re.compile(
    r"escalation_class\s*:\s*scope_redefinition_required",
    re.MULTILINE,
)
# Forbidden: failure/abort 동반 (§10 기록 = FIX Ledger, ESCALATE 는 §10 무기록)
G3_FORBIDDEN = re.compile(
    r"ESCALATE.{0,200}(?:failure|abort)",
    re.MULTILINE | re.DOTALL,
)
# CFP-897: negation markers — 정상 "NOT failure" / "abort 아님" / "failure/abort 미동반" declare 차단
# matched span 안 본 패턴 존재 시 G-3 forbidden 발화 skip
G3_NEGATION_MARKERS = re.compile(
    r"NOT\s+(?:failure|abort)"               # "NOT failure" / "NOT abort"
    r"|(?:failure|abort)\s*(?:아님|미동반)"   # "failure 아님" / "abort 미동반"
    r"|단순\s*(?:failure|abort)"              # "단순 failure" / "단순 abort"
    r"|(?:failure|abort)[/]abort\s*(?:아님|미동반)"  # "failure/abort 아님"
    r"|NOT\s+failure\s*[/]\s*abort"           # "NOT failure/abort"
    r"|failure\s*[/]\s*abort\s*(?:아님|미동반)",  # "failure/abort 미동반"
    re.IGNORECASE,
)

# ─── G-4: 4-layer disjoint 무손상 (negative grep on §10 FIX Ledger section) ───
# §10 FIX Ledger 표 헤더/row 에 recheck_counter / 재조사 카운터 토큰 부재
G4_LEDGER_SECTION = re.compile(
    r"##\s*§?10[.\s].*?(?=\n##\s*§?1[1-9]|\Z)",
    re.MULTILINE | re.DOTALL,
)
G4_RECHECK_TOKEN = re.compile(
    r"recheck_counter|재조사\s*카운터",
    re.MULTILINE,
)

# ─── G-5: cross-Story 통합 일관성 checklist 존재 ───
# Story §7 / Change Plan 에 Epic A 5-layer consistency 표 또는 체크리스트 존재
G5_CHECKLIST = re.compile(
    r"(Story-1.*Story-2.*Story-3|CFP-759.*CFP-778.*CFP-785"
    r"|layer.{0,30}consistency|cross.{0,10}Story.{0,30}layer"
    r"|통합.{0,20}검증.{0,40}layer|4-layer.{0,30}disjoint.{0,30}무손상"
    r"|Epic A.{0,30}5.{0,10}Story)",
    re.MULTILINE | re.DOTALL,
)


def find_story_files(repo_root: Path):
    """Find Story files matching target glob patterns."""
    found = []
    for pattern in STORY_GLOB_PATTERNS:
        found.extend(repo_root.glob(pattern))
    return found


# CFP-897: code-block strip — ``` fenced 또는 inline `code` 영역 안 lint spec 인용 self-ref FP 차단
_FENCED_CODE_BLOCK = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_INLINE_CODE_SPAN = re.compile(r"`[^`\n]*`")


def _strip_code_blocks(content: str) -> str:
    """Remove fenced code blocks + inline code spans from markdown content.

    CFP-897: lint spec 인용 (regex pattern in code) 이 self-ref FP 트리거하지 않도록 strip.
    """
    stripped = _FENCED_CODE_BLOCK.sub("", content)
    stripped = _INLINE_CODE_SPAN.sub("", stripped)
    return stripped


def _extract_table_rows(section: str) -> str:
    """Extract only markdown table rows (lines starting with `|`) from a section.

    CFP-897: G-2/G-4 negative grep 을 §10 표 row data only 로 제한
    (prose paragraphs 안 정합성 declaration 인용 FP 차단).
    """
    lines = section.split("\n")
    table_lines = [line for line in lines if line.strip().startswith("|")]
    return "\n".join(table_lines)


def check_g2_negative_cross_pollinate(content: str, filepath: Path) -> list:
    """G-2/G-4 negative grep: §10 FIX Ledger **table rows** must not contain recheck tokens.

    CFP-897 precision: prose paragraphs (disjoint declaration 등) 는 exclude — 표 row data only.
    """
    violations = []
    ledger_match = G4_LEDGER_SECTION.search(content)
    if ledger_match:
        ledger_section = ledger_match.group(0)
        # CFP-897: strip code blocks (self-ref lint spec 인용 차단), then extract table rows only
        ledger_no_code = _strip_code_blocks(ledger_section)
        table_data = _extract_table_rows(ledger_no_code)
        if G4_RECHECK_TOKEN.search(table_data):
            violations.append(
                f"G-2/G-4 §10 FIX Ledger 표 row data 에 recheck_counter/재조사 카운터 토큰 발견 "
                f"(cross-pollinate 위반) — {filepath.name}"
            )
    return violations


def check_g3_forbidden_with_negation(content_no_code: str) -> bool:
    """G-3 forbidden check with CFP-897 negation marker exclusion.

    Returns True if at least one ESCALATE+failure/abort match exists WITHOUT negation context.
    Returns False if all matches contain negation markers (i.e. normal declarations like
    "NOT failure / NOT abort", "failure/abort 아님", "단순 abort 아님", "failure 미동반" 등).

    CFP-897: extended span (matched + 30 char lookahead) — G3_FORBIDDEN regex matches stop at
    "failure"/"abort" literal; trailing negation marker (e.g. "failure 아님", "abort 미동반")
    appears OUTSIDE the match span. Extended lookahead allows post-match negation detection.
    """
    for m in G3_FORBIDDEN.finditer(content_no_code):
        start = m.start()
        end = min(len(content_no_code), m.end() + 30)
        extended_span = content_no_code[start:end]
        if not G3_NEGATION_MARKERS.search(extended_span):
            return True
    return False


def check_story_file(filepath: Path) -> list:
    """Check a single Story file for G-1..G-5 invariants."""
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"[adr-077-integration] WARN: {filepath} 읽기 실패: {e}\n")
        return violations

    name = filepath.name

    # CFP-897: strip code blocks first — lint spec 인용 (markdown ``` 또는 `inline code`) 안
    # regex pattern literal 이 self-ref FP 트리거하지 않도록 차단. positive declares (G-1/G-2/G-5)
    # 도 code block 안 인용으로 충족 불가하므로 strip 후 검사 (prose declare 의무 강제).
    content_no_code = _strip_code_blocks(content)

    # G-1: stale-gate declare 존재
    if not G1_STALE_GATE.search(content_no_code):
        violations.append(
            f"G-1: stale-gate 진입 차단 declare 부재 "
            f"(ADR-077 §결정 8 cross-ref 또는 stale 차단 문구 필요) — {name}"
        )

    # G-2: disjoint 선언 문구 존재
    if not G2_DISJOINT_DECLARE.search(content_no_code):
        violations.append(
            f"G-2: 재조사 카운터 ↔ §10 FIX Ledger disjoint 선언 문구 부재 — {name}"
        )

    # G-2/G-4 negative cross-pollinate check (§10 표 row data only — CFP-897)
    violations.extend(check_g2_negative_cross_pollinate(content, filepath))

    # G-3: ESCALATE escape valve (CFP-897 negation marker exclusion)
    if G3_ESCALATE_PATTERN.search(content_no_code):
        if not G3_ESCALATION_CLASS.search(content_no_code):
            violations.append(
                f"G-3: ESCALATE 출현 but escalation_class:scope_redefinition_required 부재 — {name}"
            )
        if check_g3_forbidden_with_negation(content_no_code):
            violations.append(
                f"G-3: ESCALATE + failure/abort 동반 위반 (§10 무기록 invariant) — {name}"
            )

    # G-5: cross-Story 통합 일관성 checklist
    if not G5_CHECKLIST.search(content_no_code):
        violations.append(
            f"G-5: cross-Story 통합 일관성 checklist/표 부재 "
            f"(Epic A 5-layer consistency 확인 필요) — {name}"
        )

    return violations


def main() -> int:
    repo_root = Path.cwd()
    story_files = find_story_files(repo_root)

    # Self-ref graceful: Story file 부재 시 sys.exit(0)
    if not story_files:
        sys.stderr.write(
            "[adr-077-integration] SKIP: Story file 부재 "
            "(wrapper/stories/CFP-*.md 또는 docs/stories/CFP-*.md not found) "
            "— self-ref graceful (continue-on-error)\n"
        )
        return 0

    all_violations = []
    checked = []

    for filepath in sorted(story_files):
        viols = check_story_file(filepath)
        all_violations.extend(viols)
        checked.append(filepath.name)

    if all_violations:
        sys.stderr.write(
            f"[adr-077-integration] FAIL: {len(all_violations)} violation(s) detected "
            f"in {len(checked)} Story file(s):\n"
        )
        for v in all_violations:
            sys.stderr.write(f"  • {v}\n")
        sys.stderr.write(
            "  ADR-077 §결정 8 stale 게이트·envelope·4-layer disjoint integrity 검증 실패\n"
            "  (warning mode — ADR-060 §결정 5 / CFP-848 carrier)\n"
        )
        return 1

    sys.stdout.write(
        f"[adr-077-integration] PASS: G-1..G-5 invariants OK "
        f"({len(checked)} Story file(s) checked)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
