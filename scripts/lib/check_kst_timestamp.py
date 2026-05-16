#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-771 / ADR-079 Amendment 1 — KST timestamp display mechanical lint (warning mode)
# ADR-061 §결정 1 — heredoc Python 외부 .py split (thin wrapper: scripts/check-kst-timestamp.sh)
#
# Lint scope: PR 변경 paths ∩ SCOPE_GLOBS 5 영역
# KST_TS_RE: RFC 3339 §5.6 colon-offset, anchor + backtracking-free
#
# Exit codes:
#   0 = PASS (violation 0 or scope 외 or bypass)
#   1 = WARN (violation 검출, warning mode — PR merge 미차단)
#   2 = ERROR (file read 실패 등 unexpected)
#
# INV-DM-2: detect-only read-only grep — file 변경 0. autofix 채널 절대 금지.
# §7.4 N/A: datetime.now() / zoneinfo import / GitHub API 호출 0건.
import sys, os, re
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── KST timestamp regex (RFC 3339 §5.6, Story §3.3 결정 3 verbatim) ───
# Match ISO 8601 dateTime with timezone offset, anchored to word boundary.
# Pattern matches +HH:MM / -HH:MM / Z offsets.
# Violation = offset present AND offset != '+09:00'.
# Bare datetime (no offset group) = unmatched → undetected (display layer prose 한정, E-1).
KST_TS_RE = re.compile(
    r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(Z|[+-]\d{2}:\d{2})'
)

# E-7: KST parenthetical 패턴 — `(HH:MM KST)` 또는 `(HH:MM:SS KST)` 형식
# E-8 옵션 A adjacency: KST-paren 직전 인접 timestamp 만 exempt (token-level)
KST_PAREN_RE = re.compile(r'\((\d{1,2}:\d{2}(?::\d{2})?)\s+KST\)')

EXPECTED_OFFSET = '+09:00'

# ─── 5 scope glob (Story §3.3 결정 1 verbatim) ───
SCOPE_GLOBS = [
    "CLAUDE.md",
    "docs/orchestrator-playbook.md",
    "docs/adr/ADR-*.md",
    "wrapper/retros/**/*.md",       # internal-docs path (이 repo 에서는 docs/retros/ 매핑)
    "docs/retros/**/*.md",          # wrapper repo 실제 경로 (consumer overlay 정합)
]

# ─── Exempt 영역 (Story §3.3 결정 2 verbatim) ───
EXEMPT_PREFIXES = [
    "docs/inter-plugin-contracts/",  # contract field layer, UTC strict 0건 변경 invariant
]

# Story §14 spawned_at / returned_at schema (machine-layer) — line pattern 기반 guard
MACHINE_LAYER_FIELDS_RE = re.compile(
    r'^\s*(spawned_at|returned_at)\s*[:=]'
)

# ADR frontmatter date-only line guard (^date: line — KST 일자 의미, ISO 8601 offset 미부착 정상)
# date: 2026-05-16 형식은 KST_TS_RE 에 미매칭 (T 없음) → 자연 면제. 별도 guard 불필요.
# 단, date: 2026-05-16T... 형식이 frontmatter 에 있으면 검출 대상.
ADR_FRONTMATTER_DATE_LINE_RE = re.compile(r'^date:\s*\d{4}-\d{2}-\d{2}\s*$')

EXEMPT_EXACT = {
    "scripts/check-kst-timestamp.sh",
    "scripts/lib/check_kst_timestamp.py",
    "tests/scripts/test-check-kst-timestamp.bats",
    "docs/evidence-checks-registry.yaml",
}


def normalize_path(p):
    """Path separator OS independence (Windows backslash → forward slash)."""
    return str(p).replace("\\", "/")


def in_exempt(p):
    """Exempt 여부 검사. EXEMPT_PREFIXES + EXEMPT_EXACT + docs/inter-plugin-contracts/."""
    norm = normalize_path(p)
    for prefix in EXEMPT_PREFIXES:
        if norm.startswith(prefix):
            return True
    return norm in EXEMPT_EXACT


def collect_scope_files():
    """5 scope glob 으로 wrapper repo file 수집. EXEMPT filter."""
    out = []
    for pattern in SCOPE_GLOBS:
        for path in Path(".").glob(pattern):
            if not path.is_file():
                continue
            norm = normalize_path(path)
            if in_exempt(norm):
                continue
            out.append(norm)
    # flat CLAUDE.md + playbook 직접 포함 (glob 매핑 외 위치)
    for direct in ["CLAUDE.md", "docs/orchestrator-playbook.md"]:
        if Path(direct).is_file() and not in_exempt(direct):
            out.append(direct)
    return sorted(set(out))


def in_scope(p):
    """argv path 가 5 scope 안에 있는지 검사."""
    norm = normalize_path(p)
    path = Path(norm)
    if norm in {"CLAUDE.md", "docs/orchestrator-playbook.md"}:
        return True
    # ADR files
    if path.match("docs/adr/ADR-*.md"):
        return True
    # retros
    if norm.startswith("wrapper/retros/") and norm.endswith(".md"):
        return True
    if norm.startswith("docs/retros/") and norm.endswith(".md"):
        return True
    return False


def scan_file(p):
    """File 본문을 line-by-line scan. 위반 = KST_TS_RE 매칭 AND offset != +09:00."""
    findings = []
    try:
        text = Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise

    in_fence = False
    fence_marker = None

    for line_num, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.lstrip()

        # fenced code block skip (review + violation 제외)
        if not in_fence:
            for marker in ("```", "~~~"):
                if stripped.startswith(marker):
                    in_fence = True
                    fence_marker = marker
                    break
            if in_fence:
                continue
        else:
            if fence_marker and stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = None
            continue

        # blockquote skip
        if stripped.startswith(">"):
            continue

        # machine-layer field skip (spawned_at / returned_at)
        if MACHINE_LAYER_FIELDS_RE.match(raw_line):
            continue

        # ADR frontmatter date-only line skip (date: YYYY-MM-DD — no offset, already unmatched)
        # 명시적 guard: offset 없는 date-only 라인은 KST_TS_RE 미매칭으로 자연 면제
        if ADR_FRONTMATTER_DATE_LINE_RE.match(raw_line):
            continue

        # KST_TS_RE scan — 한 라인에 복수 timestamp 가능
        # E-8 옵션 A: KST-paren 직전 인접 timestamp 만 exempt (token-level adjacency guard)
        kst_paren_matches = list(KST_PAREN_RE.finditer(raw_line))
        for m in KST_TS_RE.finditer(raw_line):
            # 인접성 검사: m 이 어떤 kst_paren 의 직전 token 인가?
            is_adjacent_to_kst_paren = False
            for kp in kst_paren_matches:
                # m.end() ≤ kp.start() (m 이 kp 앞에 위치) + 사이가 whitespace 만
                if m.end() <= kp.start():
                    gap = raw_line[m.end():kp.start()]
                    if gap.strip() == "":  # whitespace only
                        is_adjacent_to_kst_paren = True
                        break
            if is_adjacent_to_kst_paren:
                continue  # KST-paren 인접 exempt
            offset = m.group(1)
            if offset != EXPECTED_OFFSET:
                findings.append((line_num, raw_line.rstrip(), m.group(0), offset))

    return findings


def main(argv):
    paths = argv[1:]
    if not paths:
        paths = collect_scope_files()
    else:
        filtered = []
        for p in paths:
            norm = normalize_path(p)
            if in_exempt(norm):
                continue
            if not in_scope(norm):
                continue
            filtered.append(norm)
        paths = filtered

    total_findings = 0
    files_checked = 0
    file_violations = []

    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"check-kst-timestamp: path 부재 (skip): {p}", file=sys.stderr)
            continue
        files_checked += 1
        try:
            findings = scan_file(p)
        except OSError as exc:
            print(f"check-kst-timestamp: file read error {p}: {exc}", file=sys.stderr)
            sys.exit(2)
        if findings:
            file_violations.append((p, findings))
            total_findings += len(findings)

    print(f"check-kst-timestamp: {files_checked} files 검증 (5 scope, ADR-079 Amendment 1 KST display layer lint)")

    if total_findings == 0:
        print("OK violation 0건 — KST timestamp display lint PASS")
        sys.exit(0)

    print(f"\nWARN violation {total_findings}건 in {len(file_violations)} files:", file=sys.stderr)
    for fpath, findings in file_violations:
        print(f"  {fpath}:", file=sys.stderr)
        for line_num, content, matched_ts, offset in findings:
            print(f"    L{line_num} [offset={offset}]: {content}", file=sys.stderr)
    print(
        "\nADR-079 §결정 1 KST display layer 위반: timestamp offset 은 `+09:00` 사용 필수.",
        file=sys.stderr,
    )
    print(
        "  위반 예시: 2026-05-16T18:50:50Z → 수정: 2026-05-16T18:50:50+09:00",
        file=sys.stderr,
    )
    print(
        "\nBypass (운영 hotfix 한정): `hotfix-bypass:kst-timestamp-display` label + PR description `### Bypass reason` 본문 (ADR-024 Amendment 3 §결정 6.A).",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"check-kst-timestamp: unexpected error: {exc}", file=sys.stderr)
        sys.exit(2)
