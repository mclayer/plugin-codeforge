#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-449 / ADR-060 / ADR-064 — Decision principle forbid-list vocabulary mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# trap_priority: line 90 replace("\\","/") path normalization — preserved verbatim.
#
# Usage / exit code / semantics 상세: scripts/check-decision-principle-vocabulary.sh header.
import sys, os, re
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── Dictionary SSOT (ADR-064 §결정 2 verbatim mirror — 8 entry) ───
FORBID_DICTIONARY = [
    "임시",
    "단계적",
    "일단",
    "우선",
    "잠정",
    "가벼운",
    "minimal viable",
    "quick win",
]

# ─── 5 scope glob (ADR-064 §결정 2 verbatim — broad coverage anchor) ───
SCOPE_GLOBS = [
    "docs/adr/ADR-*.md",
    "archive/adr/ADR-*.md",
    "docs/change-plans/**/*.md",
    "CLAUDE.md",
    "docs/orchestrator-playbook.md",
    "templates/**/*.md",
    "templates/**/*.yml",
    "templates/**/*.yaml",
    "templates/**/*.sh",
]

# ─── Exempt 영역 ───
# CFP-2661 D11: ADR 실 위치 archive/adr union (PR #1973 이동). SCOPE_GLOBS 는 이미 dual(docs/adr ∪
#   archive/adr)이라 archive/adr/ADR-064(어휘 정의 본문)·ADR-RESERVATION 가 스캔되는데 EXEMPT 는 구
#   docs/adr 형만 → 미매치 → false-RED(ADR-064 29건). docs/adr 형은 consumer 정답 경로라 union 보존.
EXEMPT_PATHS = {
    "docs/adr/ADR-RESERVATION.md",
    "docs/adr/ADR-064-decision-principle-mandate.md",
    "archive/adr/ADR-RESERVATION.md",
    "archive/adr/ADR-064-decision-principle-mandate.md",
    "docs/evidence-checks-registry.yaml",
    "scripts/check-decision-principle-vocabulary.sh",
    "tests/scripts/test-check-decision-principle-vocabulary.bats",
}


def normalize_path(p):
    """Path separator OS independence (Windows backslash → forward slash)."""
    return str(p).replace("\\", "/")


def collect_scope_files():
    """5 scope glob 으로 wrapper repo file 수집. EXEMPT_PATHS filter.

    CFP-2661 D11: (files, scope_considered) 반환 — scope_considered = glob 매치 in-scope 파일 수
    (exempt 前, anti-vacuity floor). 구경로 docs/adr 만이면 archive/adr scope 는 dead → considered 낮음.
    """
    out = []
    considered = set()
    for pattern in SCOPE_GLOBS:
        for path in Path(".").glob(pattern):
            if not path.is_file():
                continue
            norm = normalize_path(path)
            considered.add(norm)
            if norm in EXEMPT_PATHS:
                continue
            out.append(norm)
    return sorted(set(out)), len(considered)


def in_scope(p):
    """argv path 가 5 scope 안에 있는지 검사. False = scope 외 → exit 0 처리."""
    norm = normalize_path(p)
    path = Path(norm)
    for pattern in SCOPE_GLOBS:
        if path.match(pattern):
            return True
        prefix = pattern.split("**", 1)[0].rstrip("/")
        if prefix and norm.startswith(prefix + "/"):
            suffixes = pattern.rsplit(".", 1)
            if len(suffixes) == 2 and norm.endswith("." + suffixes[1]):
                return True
    return norm in {"CLAUDE.md", "docs/orchestrator-playbook.md"}


def scan_file(p):
    """File 본문을 line-by-line state machine 으로 scan."""
    findings = []
    try:
        text = Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise
    in_fence = False
    fence_marker = None
    for line_num, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.lstrip()
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
        if stripped.startswith(">"):
            continue
        line_lower = raw_line.lower()
        for word in FORBID_DICTIONARY:
            if word.lower() in line_lower:
                findings.append((line_num, raw_line.rstrip(), word))
    return findings


def main(argv):
    paths = argv[1:]
    # CFP-2661 D11 census: scope_considered = in-scope 파일 수 (exempt 前, anti-vacuity floor — AC-11).
    #   exempt 파일(ADR-064)을 argv 로 줘도 in-scope 로 집계 → "scope 살아있음" 관측 (dead-scope vs exempt 구별).
    scope_considered = 0
    if not paths:
        paths, scope_considered = collect_scope_files()
    else:
        filtered = []
        for p in paths:
            norm = normalize_path(p)
            if in_scope(norm):
                scope_considered += 1
            if norm in EXEMPT_PATHS:
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
            print(f"check-decision-principle-vocabulary: path 부재 (skip): {p}", file=sys.stderr)
            continue
        files_checked += 1
        try:
            findings = scan_file(p)
        except OSError as exc:
            print(f"check-decision-principle-vocabulary: file read error {p}: {exc}", file=sys.stderr)
            sys.exit(2)
        if findings:
            file_violations.append((p, findings))
            total_findings += len(findings)

    # CFP-2661 D11 census (AC-11 — anti-vacuity floor). scope_considered = in-scope surface (exempt 포함).
    print(
        f"check-decision-principle-vocabulary: census scope_considered={scope_considered} "
        f"files_checked={files_checked} exempt_skipped={max(0, scope_considered - files_checked)}"
    )
    print(f"check-decision-principle-vocabulary: {files_checked} files 검증 (5 scope, ADR-064 §결정 2 dictionary mirror)")

    if total_findings == 0:
        print("OK violation 0건 — decision principle vocabulary lint PASS")
        sys.exit(0)

    print(f"\nWARN violation {total_findings}건 in {len(file_violations)} files:", file=sys.stderr)
    for fpath, findings in file_violations:
        print(f"  {fpath}:", file=sys.stderr)
        for line_num, content, word in findings:
            print(f"    L{line_num} [{word}]: {content}", file=sys.stderr)
    print(
        "\nADR-064 §결정 2 forbid-list dictionary 위반. 대체 어휘 (ADR-064 §결정 1 4 어휘 운영적 정의):",
        file=sys.stderr,
    )
    print("  best-effort / broad coverage / full-scope / active amendment", file=sys.stderr)
    print(
        "\nBypass (운영 hotfix 한정): `hotfix-bypass:decision-principle-vocab` label + PR description `### Bypass reason` 본문 (ADR-024 Amendment 3 §결정 6.A).",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"check-decision-principle-vocabulary: unexpected error: {exc}", file=sys.stderr)
        sys.exit(2)
