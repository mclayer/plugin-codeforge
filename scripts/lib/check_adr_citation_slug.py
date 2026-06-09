#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADR citation slug lint - CFP-2057 / ADR-060 warning-tier evidence-checks-registry entry.
ADR-061 compliant - external .py SSOT, no heredoc.

2-layer validation:
  L1 slug-existence: ADR-NNN citation in docs -> archive/adr/ADR-NNN-<slug>.md existence check.
  L2 deny-list:      ADR-057 + (ALLOWED_HUB_REPOS/SECURITY_PATHS/whitelist context) OR
                     (ratchet keywords: 축소불가/확장만/never-reduce with proximity) = FAIL.
                     (ADR-057 actual = Orchestrator Opus mandate - unrelated to whitelist/ratchet policy)
                     Legitimate citations (자동재시도금지, fallback) are EXEMPT via proximity-bound patterns.

scope: Population A (ALLOWED_HUB_REPOS context) + Population B (ratchet misquote, global). CFP-2093 전역 확대.
archive/ included: ADR-026 origin is in archive/ - must include for root-cause detection.

L1 false-positive suppression (CFP-2057 P2 fix):
  - tests/** paths: intentional sentinel fixtures (tests/**/fixtures/*, test scripts) exempt from L1.
  - Sentinel ADR numbers (>= 900): skip L1 slug-existence check (ADR-999, ADR-9991..9998, etc.
    are reserved sentinel numbers used in test fixtures and documentation examples).
  - Per-line dedup: same ADR number cited twice on one line counts as 1 violation (not 2).

Limitations (mandatory disclosure - design section 7.6 AC-5):
  - ADR-057 misquote (number exists, only meaning wrong) = L1 cannot detect - L2 deny-list blocks.
  - General semantic correctness of citations = reviewer responsibility, not lint scope.

Usage:
  python3 scripts/lib/check_adr_citation_slug.py [paths...]
  # If paths omitted, auto-scan current directory (markdown + yaml + sh + workflow)

Exit:
  0 = pass (0 violations)
  1 = L2 deny-list violation found (warning-tier: CI outputs warning, blocking config = CI wire)
  2 = L1 slug-existence violation found
  3 = L1 + L2 combined violation
"""

import sys
import os
import re
import argparse
from pathlib import Path
import platform


def _posix_to_path(p):
    """Convert POSIX-style /c/... paths to Windows paths when running on Windows.
    On Linux/macOS, returns Path(p) unchanged.
    """
    if platform.system() == 'Windows' and p.startswith('/') and len(p) >= 3 and p[2] == '/':
        # /c/foo/bar -> C:/foo/bar
        drive = p[1].upper()
        return Path(drive + ':' + p[2:])
    return Path(p)


# L2 deny-list: ADR-057 misquote patterns
# Population A: ADR-057 + ALLOWED_HUB_REPOS/SECURITY_PATHS context (original scope)
# Population B: ADR-057 + ratchet keywords (축소 불가/확장만/never-reduce) global (CFP-2093 전역 확대)
# Note: Population B = included (CFP-2093 전역 확대 — 정당 인용은 EXEMPT 으로 보호).
L2_DENY_PATTERNS = [
    # ADR-057 + ALLOWED_HUB_REPOS keyword (direct) — Population A
    re.compile(r'ADR-057.*ALLOWED_HUB_REPOS', re.IGNORECASE),
    re.compile(r'ALLOWED_HUB_REPOS.*ADR-057', re.IGNORECASE),
    # ADR-057 + SECURITY_PATHS keyword (direct) — Population A
    re.compile(r'ADR-057.*SECURITY_PATHS', re.IGNORECASE),
    re.compile(r'SECURITY_PATHS.*ADR-057', re.IGNORECASE),
    # ADR-057 + ratchet keywords with proximity bound — Population B (CFP-2093)
    # .{0,40} = proximity bound (avoids line-wildcard false-positive for distant co-occurrence)
    re.compile(r'ADR-057.{0,40}(축소\s*불가|축소\s*차단|확장만|확장-only|never-reduce)', re.IGNORECASE),
    re.compile(r'(축소\s*불가|축소\s*차단|확장만|확장-only|never-reduce).{0,40}ADR-057', re.IGNORECASE),
]

# Exempt patterns for legitimate ADR-057 citations and historical narrative.
# Priority rule: deny match takes precedence over exempt.
# Proximity-bound exempts (자동재시도/fallback) require ADR-057 within .{0,40}
# to avoid over-exempting lines where ratchet-misquote co-exists near ADR-057.
L2_EXEMPT_PATTERNS = [
    re.compile(r'CHANGELOG', re.IGNORECASE),
    re.compile(r'misquote correction', re.IGNORECASE),
    re.compile(r'correction target', re.IGNORECASE),
    re.compile(r'ADR-057.*Orchestrator Opus', re.IGNORECASE),
    re.compile(r'ADR-057.*rate.limit', re.IGNORECASE),
    # Lint self-description / deny-list purpose description
    re.compile(r'오인용 차단', re.IGNORECASE),      # lint purpose: "oinyong chadan" (misquote block)
    re.compile(r'오인용.*ALLOWED_HUB', re.IGNORECASE),   # "ADR-057 oinyong(ALLOWED_HUB...)"
    re.compile(r'deny.list.*ADR-057', re.IGNORECASE),  # deny-list ADR-057
    re.compile(r'ADR-057.*deny.list', re.IGNORECASE),  # ADR-057 deny-list
    # Script self-reference (check_adr_citation_slug.py pattern description)
    re.compile(r'ADR-057 cited in whitelist', re.IGNORECASE),
    # Korean exemption patterns (historical/correction context)
    re.compile(r'오인용 정정'),     # 오인용 정정
    re.compile(r'정정 대상'),            # 정정 대상
    re.compile(r'실제.*ADR-057'),                # 실제 ADR-057
    re.compile(r'ADR-057.*실제'),                # ADR-057 실제
    # Proximity-bound: legitimate ADR-057 citation (자동 재시도 금지, fallback) — CFP-2093 Population B
    # ADR-057:76 "(자동 재시도 금지)" and ADR-057:70 §결정 2 (Sonnet→Opus fallback) are legitimate.
    # Exempt ONLY when the legitimate keyword is near ADR-057 (.{0,40}).
    re.compile(r'자동\s*재시도\s*금지.{0,40}ADR-057'),
    re.compile(r'ADR-057.{0,40}자동\s*재시도\s*금지'),
    re.compile(r'fallback.{0,40}ADR-057', re.IGNORECASE),
    re.compile(r'ADR-057.{0,40}fallback', re.IGNORECASE),
]

# Population B deny patterns (ratchet keywords) — used for deny-vs-exempt priority logic
# When a line matches a Population B deny pattern AND a proximity-bound exempt pattern,
# deny takes precedence (RED). This prevents a mixed line (misquote + legitimate citation)
# from being incorrectly exempted by the legitimate part.
L2_DENY_PATTERNS_POPULATION_B = [
    re.compile(r'ADR-057.{0,40}(축소\s*불가|축소\s*차단|확장만|확장-only|never-reduce)', re.IGNORECASE),
    re.compile(r'(축소\s*불가|축소\s*차단|확장만|확장-only|never-reduce).{0,40}ADR-057', re.IGNORECASE),
]

# Proximity-bound exempt patterns (자동재시도/fallback) — these are subject to deny-priority
L2_EXEMPT_PROXIMITY_BOUND = [
    re.compile(r'자동\s*재시도\s*금지.{0,40}ADR-057'),
    re.compile(r'ADR-057.{0,40}자동\s*재시도\s*금지'),
    re.compile(r'fallback.{0,40}ADR-057', re.IGNORECASE),
    re.compile(r'ADR-057.{0,40}fallback', re.IGNORECASE),
]

# ADR-NNN pattern (L1 slug-existence)
ADR_REF_PATTERN = re.compile(r'\bADR-(\d+)\b')

# Scan extensions
SCAN_EXTENSIONS = {'.md', '.yml', '.yaml', '.sh', '.py', '.txt'}

# Excluded directories (archive/ is INCLUDED - ADR-026 origin is there)
EXCLUDE_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv'}

# Excluded files (lint script self-exclusion to avoid self-referential false-positive)
EXCLUDE_FILES = {'check_adr_citation_slug.py'}

# L1 sentinel ADR number threshold: ADR numbers >= this value are reserved for test
# fixtures / documentation examples and are intentionally not real ADRs.
# Covers: ADR-999, ADR-9991..9999, ADR-9992, ADR-9993..9998, etc.
L1_SENTINEL_THRESHOLD = 900

# L1 path prefix exempt from slug-existence check: test fixtures / test scripts
# use intentional sentinel ADR numbers that must not trigger L1 violations.
L1_EXEMPT_PATH_PARTS = ('tests',)

# ADR directory candidates
ADR_DIR_CANDIDATES = [
    'archive/adr',
    'docs/adr',
]


def find_adr_dir(repo_root):
    """Find the ADR directory in repo."""
    for candidate in ADR_DIR_CANDIDATES:
        adr_dir = repo_root / candidate
        if adr_dir.is_dir():
            return adr_dir
    return None


def load_existing_adrs(adr_dir):
    """Load ADR-NNN -> slug mapping from ADR directory."""
    adrs = {}
    for path in adr_dir.glob('ADR-*-*.md'):
        m = re.match(r'ADR-(\d+)-(.+)\.md', path.name)
        if m:
            num = int(m.group(1))
            adrs[num] = path.name
    return adrs


def is_exempt_l2(line):
    """Check if line is exempt from L2 deny-list.

    Priority rule (CFP-2093 §7.3 deny-vs-exempt):
    - Population A (ALLOWED_HUB_REPOS/SECURITY_PATHS): standard exempt (any exempt match = skip).
    - Population B (ratchet keywords): if the line matches a Population B deny pattern AND
      proximity-bound exempt is present, deny takes priority (RED).
      Only non-proximity-bound exempts (CHANGELOG, Orchestrator Opus, etc.) can fully exempt.
    """
    # Check if any non-proximity-bound exempt matches (these always win)
    non_proximity_exempts = L2_EXEMPT_PATTERNS[:len(L2_EXEMPT_PATTERNS) - len(L2_EXEMPT_PROXIMITY_BOUND)]
    if any(p.search(line) for p in non_proximity_exempts):
        return True

    # Check if proximity-bound exempt matches
    proximity_match = any(p.search(line) for p in L2_EXEMPT_PROXIMITY_BOUND)
    if not proximity_match:
        return False

    # Proximity-bound exempt matches — but deny takes priority if Population B deny also matches
    population_b_deny = any(p.search(line) for p in L2_DENY_PATTERNS_POPULATION_B)
    if population_b_deny:
        # Deny takes priority: ratchet-misquote co-exists with legitimate citation
        return False
    return True


def _is_l1_path_exempt(file_path):
    """Return True if file is in a path exempt from L1 slug-existence check.
    tests/** paths contain intentional sentinel fixtures - exempt from L1.
    """
    return any(part in L1_EXEMPT_PATH_PARTS for part in file_path.parts)


def check_file(file_path, existing_adrs, adr_dir_exists):
    """Check one file. Returns (l1_violations, l2_violations)."""
    l1_violations = []
    l2_violations = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return l1_violations, l2_violations

    # L1 path-level exemption: tests/** are intentional fixture files
    l1_path_exempt = _is_l1_path_exempt(file_path)

    for lineno, line in enumerate(content.splitlines(), 1):
        # L2 deny-list check (exempt first)
        if not is_exempt_l2(line):
            for pattern in L2_DENY_PATTERNS:
                if pattern.search(line):
                    l2_violations.append({
                        'file': str(file_path),
                        'line': lineno,
                        'content': line.rstrip(),
                        'layer': 'L2',
                        'reason': 'ADR-057 misquote (whitelist/ratchet context - actual ADR-057 = Orchestrator Opus mandate, not overlay ratchet policy)',
                    })
                    break  # report once per line

        # L1 slug-existence check
        if adr_dir_exists and not l1_path_exempt:
            # Dedup: collect unique ADR numbers per line (F-CR-2057-2)
            seen_on_line = set()
            for m in ADR_REF_PATTERN.finditer(line):
                adr_num = int(m.group(1))
                # Skip sentinel numbers (>= L1_SENTINEL_THRESHOLD): test fixtures /
                # documentation placeholder examples (ADR-999, ADR-9991..9998, etc.)
                if adr_num >= L1_SENTINEL_THRESHOLD:
                    continue
                if adr_num in seen_on_line:
                    continue  # dedup: same number already reported for this line
                seen_on_line.add(adr_num)
                if adr_num not in existing_adrs:
                    l1_violations.append({
                        'file': str(file_path),
                        'line': lineno,
                        'content': line.rstrip(),
                        'layer': 'L1',
                        'reason': 'ADR-{:03d} slug file missing (archive/adr/ADR-{:03d}-<slug>.md not found)'.format(adr_num, adr_num),
                        'adr_num': adr_num,
                    })

    return l1_violations, l2_violations


def collect_files(paths, repo_root):
    """Collect list of files to scan."""
    files = []
    for p in paths:
        target = _posix_to_path(p)
        if target.is_file():
            if target.name not in EXCLUDE_FILES:
                files.append(target)
        elif target.is_dir():
            for f in target.rglob('*'):
                if f.is_file() and f.suffix in SCAN_EXTENSIONS:
                    if not any(excl in f.parts for excl in EXCLUDE_DIRS):
                        if f.name not in EXCLUDE_FILES:
                            files.append(f)
    return sorted(set(files))


def main(argv=None):
    parser = argparse.ArgumentParser(description='ADR citation slug lint (CFP-2057 / ADR-060 warning-tier)')
    parser.add_argument('paths', nargs='*', help='Files or directories to check (default: current directory)')
    parser.add_argument('--repo-root', default='.', help='Repository root path (for ADR directory search)')
    parser.add_argument('--l2-only', action='store_true', help='Run L2 deny-list check only (skip L1)')
    parser.add_argument('--l1-only', action='store_true', help='Run L1 slug-existence check only (skip L2)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output when no violations')
    args = parser.parse_args(argv)

    repo_root = _posix_to_path(args.repo_root).resolve()
    scan_paths = args.paths if args.paths else [str(repo_root)]

    # Load ADR directory
    adr_dir = find_adr_dir(repo_root)
    if adr_dir is None:
        print("WARN: ADR directory not found ({}) - L1 slug-existence check skipped".format(', '.join(ADR_DIR_CANDIDATES)), file=sys.stderr)
        adr_dir_exists = False
        existing_adrs = {}
    else:
        adr_dir_exists = True
        existing_adrs = load_existing_adrs(adr_dir)

    files = collect_files(scan_paths, repo_root)

    all_l1 = []
    all_l2 = []

    for f in files:
        l1, l2 = check_file(f, existing_adrs, adr_dir_exists and not args.l2_only)
        if not args.l2_only:
            all_l1.extend(l1)
        if not args.l1_only:
            all_l2.extend(l2)

    # Report
    total = len(all_l1) + len(all_l2)
    if total == 0:
        if not args.quiet:
            print("[adr-citation-slug] PASS - violations: 0 ({} files checked)".format(len(files)))
        return 0

    print("[adr-citation-slug] violations: {} ({} L2-deny / {} L1-slug):".format(total, len(all_l2), len(all_l1)))

    for v in all_l2:
        print("  L2-DENY  {}:{}: {}".format(v['file'], v['line'], v['reason']))
        print("           {}".format(v['content'][:120].encode('ascii', 'replace').decode('ascii')))

    for v in all_l1:
        print("  L1-SLUG  {}:{}: {}".format(v['file'], v['line'], v['reason']))
        print("           {}".format(v['content'][:120].encode('ascii', 'replace').decode('ascii')))

    # Limitations disclosure (AC-5)
    print()
    print("NOTE: L1 detects ADR number/slug existence mismatch only. Semantic correctness = reviewer responsibility.")
    print("NOTE: L2 scope = ADR-057 misquote global (Population A: ALLOWED_HUB_REPOS/SECURITY_PATHS + Population B: ratchet keywords). Legitimate citations (자동재시도금지/fallback) are EXEMPT.")

    if all_l2 and all_l1:
        return 3
    elif all_l2:
        return 1
    else:
        return 2


if __name__ == '__main__':
    sys.exit(main())
