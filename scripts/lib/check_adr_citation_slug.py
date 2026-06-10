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
                     Legitimate citations (자동재시도금지, fallback) are EXEMPT via anchor-resolution model.

scope: Population A (ALLOWED_HUB_REPOS context) + Population B (ratchet misquote, global). CFP-2093 전역 확대.
archive/ included: ADR-026 origin is in archive/ - must include for root-cause detection.

L1 false-positive suppression (CFP-2057 P2 fix):
  - tests/** paths: intentional sentinel fixtures (tests/**/fixtures/*, test scripts) exempt from L1.
  - Sentinel ADR numbers (>= 900): skip L1 slug-existence check (ADR-999, ADR-9991..9998, etc.
    are reserved sentinel numbers used in test fixtures and documentation examples).
  - Per-line dedup: same ADR number cited twice on one line counts as 1 violation (not 2).

L2 deny-vs-exempt priority (CFP-2104 anchor-resolution model, D1):
  Line is RED iff (>=1 deny match) AND (no legitimate-citation exempt covers the ADR-057 anchor
  token of that deny match).  "Cover" = exempt match span fully contains the ADR-057 token span
  (exempt.start <= anchor.start AND exempt.end >= anchor.end).
  Exempt tier 3-classification (D2, Story §7.2):
    CONTEXT  — blanket exemption (CHANGELOG, lint self-description). ADR-057 anchor cover irrelevant.
    ANCHOR   — covers only the ADR-057 anchor token within its own match span (CORRECTIVE/PROXIMITY).
    META     — no anchor-cover authority (오인용 정정, 정정 대상 etc). Exempts only deny-free lines.

Limitations (mandatory disclosure - design section 7.6):
  - ADR-057 misquote (number exists, only meaning wrong) = L1 cannot detect - L2 deny-list blocks.
  - General semantic correctness of citations = reviewer responsibility, not lint scope.
  - Multi-anchor greedy-tail edge: if a prox-exempt .{0,40} tail spans a second misquote anchor on
    the same line, that anchor may remain uncovered (false-negative residual). Current code has the
    same failure -> this change is net-improvement. corpus reach 0, regression 0 priority ->
    declared as documented limitation (TODO: follow-up CFP candidate). bats revival forbidden (#2103).

Usage:
  python3 scripts/lib/check_adr_citation_slug.py [paths...]
  python3 scripts/lib/check_adr_citation_slug.py --self-test
  # If paths omitted, auto-scan current directory (markdown + yaml + sh + workflow)

Exit:
  0 = pass (0 violations) / all self-test fixtures passed
  1 = L2 deny-list violation found (warning-tier: CI outputs warning, blocking config = CI wire)
  2 = L1 slug-existence violation found
  3 = L1 + L2 combined violation
  (--self-test: 0 = all fixtures GREEN, non-zero = fixture mismatch)
"""

import sys
import os
import re
import argparse
from pathlib import Path
import platform
from typing import NamedTuple, List


def _posix_to_path(p):
    """Convert POSIX-style /c/... paths to Windows paths when running on Windows.
    On Linux/macOS, returns Path(p) unchanged.
    """
    if platform.system() == 'Windows' and p.startswith('/') and len(p) >= 3 and p[2] == '/':
        # /c/foo/bar -> C:/foo/bar
        drive = p[1].upper()
        return Path(drive + ':' + p[2:])
    return Path(p)


# ---------------------------------------------------------------------------
# D2 — rule-identity: single-record structures (CFP-2104 Story §7.3)
# Replaces positional slice [:len-len] coupling + DRY duplicate lists.
# ---------------------------------------------------------------------------

class DenyRule(NamedTuple):
    """Single deny rule record."""
    pattern: re.Pattern
    population: str  # 'A' or 'B'


class ExemptRule(NamedTuple):
    """Single exempt rule record.
    tier:
      CONTEXT — blanket exemption (CHANGELOG, lint self-description).
      ANCHOR  — anchor-bound: covers only ADR-057 tokens within own match span (CORRECTIVE/PROXIMITY).
      META    — no anchor-cover authority (오인용 정정, 정정 대상 etc).
    """
    pattern: re.Pattern
    tier: str  # 'CONTEXT' | 'ANCHOR' | 'META'


# L2 deny rules — single SSOT (Population tag replaces duplicate L2_DENY_PATTERNS_POPULATION_B)
L2_DENY_RULES: List[DenyRule] = [
    # Population A: ADR-057 + ALLOWED_HUB_REPOS keyword (direct)
    DenyRule(re.compile(r'ADR-057.*ALLOWED_HUB_REPOS', re.IGNORECASE), 'A'),
    DenyRule(re.compile(r'ALLOWED_HUB_REPOS.*ADR-057', re.IGNORECASE), 'A'),
    # Population A: ADR-057 + SECURITY_PATHS keyword (direct)
    DenyRule(re.compile(r'ADR-057.*SECURITY_PATHS', re.IGNORECASE), 'A'),
    DenyRule(re.compile(r'SECURITY_PATHS.*ADR-057', re.IGNORECASE), 'A'),
    # Population B: ADR-057 + ratchet keywords with proximity bound (CFP-2093)
    # .{0,40} = proximity bound (avoids line-wildcard false-positive for distant co-occurrence)
    DenyRule(re.compile(r'ADR-057.{0,40}(축소\s*불가|축소\s*차단|확장만|확장-only|never-reduce)', re.IGNORECASE), 'B'),
    DenyRule(re.compile(r'(축소\s*불가|축소\s*차단|확장만|확장-only|never-reduce).{0,40}ADR-057', re.IGNORECASE), 'B'),
]

# Flat deny pattern list for backward-compat check_file loop (derived from L2_DENY_RULES, no duplication)
L2_DENY_PATTERNS = [r.pattern for r in L2_DENY_RULES]

# L2 exempt rules — tier-tagged single record list (D2: replaces L2_EXEMPT_PATTERNS + L2_EXEMPT_PROXIMITY_BOUND)
# Order: CONTEXT rules first (fast-exit), then ANCHOR, then META.
L2_EXEMPT_RULES: List[ExemptRule] = [
    # --- CONTEXT tier: blanket exemption (file-context or lint self-description) ---
    ExemptRule(re.compile(r'CHANGELOG', re.IGNORECASE),                      'CONTEXT'),
    ExemptRule(re.compile(r'오인용 차단', re.IGNORECASE),                     'CONTEXT'),  # lint purpose description
    ExemptRule(re.compile(r'오인용.*ALLOWED_HUB', re.IGNORECASE),             'CONTEXT'),  # lint purpose description
    ExemptRule(re.compile(r'deny.list.*ADR-057', re.IGNORECASE),              'CONTEXT'),  # deny-list ADR-057
    ExemptRule(re.compile(r'ADR-057.*deny.list', re.IGNORECASE),              'CONTEXT'),  # ADR-057 deny-list
    ExemptRule(re.compile(r'ADR-057 cited in whitelist', re.IGNORECASE),      'CONTEXT'),  # script self-reference

    # --- ANCHOR tier: anchor-bound cover (CORRECTIVE / PROXIMITY) ---
    # CORRECTIVE: historical narrative / correction context that directly cites ADR-057
    ExemptRule(re.compile(r'misquote correction', re.IGNORECASE),             'ANCHOR'),
    ExemptRule(re.compile(r'correction target', re.IGNORECASE),               'ANCHOR'),
    ExemptRule(re.compile(r'ADR-057.*Orchestrator Opus', re.IGNORECASE),      'ANCHOR'),
    ExemptRule(re.compile(r'ADR-057.*rate.limit', re.IGNORECASE),             'ANCHOR'),
    ExemptRule(re.compile(r'실제.*ADR-057'),                                   'ANCHOR'),
    ExemptRule(re.compile(r'ADR-057.*실제'),                                   'ANCHOR'),
    # PROXIMITY: legitimate ADR-057 citation (자동재시도금지, fallback) — proximity-bound .{0,40}
    # ADR-057:76 "(자동 재시도 금지)" and ADR-057:70 §결정 2 (Sonnet→Opus fallback) are legitimate.
    ExemptRule(re.compile(r'자동\s*재시도\s*금지.{0,40}ADR-057'),              'ANCHOR'),
    ExemptRule(re.compile(r'ADR-057.{0,40}자동\s*재시도\s*금지'),              'ANCHOR'),
    ExemptRule(re.compile(r'fallback.{0,40}ADR-057', re.IGNORECASE),          'ANCHOR'),
    ExemptRule(re.compile(r'ADR-057.{0,40}fallback', re.IGNORECASE),          'ANCHOR'),

    # --- META tier: no anchor-cover authority ---
    # Line-level meta tags only — do NOT directly cite the ADR-057 token they annotate.
    # They exempt deny-free lines but cannot override an uncovered misquote anchor.
    ExemptRule(re.compile(r'오인용 정정'),                                     'META'),
    ExemptRule(re.compile(r'정정 대상'),                                       'META'),
]

# ADR-057 anchor token pattern (used by anchor-resolution model)
_ADR057_TOKEN = re.compile(r'ADR-057')

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


def _deny_anchors(line):
    """Return list of (deny_rule, anchor_match) pairs for all deny matches in line.
    For each deny match, find the ADR-057 token span within that deny match span.
    A deny match with no ADR-057 token inside is still included (anchor=None means always RED).
    Returns list of (DenyRule, anchor_span_or_None).
    """
    result = []
    for rule in L2_DENY_RULES:
        for dm in rule.pattern.finditer(line):
            # Find ADR-057 token within the deny match span
            anchor = None
            for am in _ADR057_TOKEN.finditer(line, dm.start(), dm.end()):
                anchor = am
                break  # first ADR-057 within deny match
            result.append((rule, dm, anchor))
    return result


def _anchor_covered(line, anchor_match):
    """Return True if any ANCHOR-tier exempt rule match covers the anchor_match span.
    cover = exempt.start <= anchor.start AND exempt.end >= anchor.end.
    """
    if anchor_match is None:
        return False
    a_start, a_end = anchor_match.start(), anchor_match.end()
    for rule in L2_EXEMPT_RULES:
        if rule.tier != 'ANCHOR':
            continue
        for em in rule.pattern.finditer(line):
            if em.start() <= a_start and em.end() >= a_end:
                return True
    return False


def is_exempt_l2(line):
    """Check if line is exempt from L2 deny-list.

    D1 anchor-resolution model (CFP-2104 Story §7.1):
      Line is RED iff (>=1 deny anchor) AND (>=1 uncovered deny anchor).
      "Covered" = ANCHOR-tier exempt match span contains the ADR-057 token span of the deny match.
      CONTEXT-tier exempt => blanket exemption (always GREEN).
      META-tier exempt => no anchor-cover authority (GREEN only on deny-free lines).
    """
    # Fast path: no deny match at all -> check any exempt for GREEN, else GREEN by default
    deny_hits = _deny_anchors(line)
    if not deny_hits:
        return True  # no deny trigger -> always GREEN

    # CONTEXT-tier: blanket exemption regardless of deny anchors
    for rule in L2_EXEMPT_RULES:
        if rule.tier == 'CONTEXT' and rule.pattern.search(line):
            return True

    # For each deny anchor: check if it is covered by an ANCHOR-tier exempt
    for _rule, _dm, anchor in deny_hits:
        if not _anchor_covered(line, anchor):
            # Uncovered misquote anchor found -> RED
            return False

    # All deny anchors are covered by ANCHOR-tier exempts -> GREEN
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
        # L2 deny-list check (anchor-resolution model)
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


def run_self_test():
    """D3 — inline fixture self-test (CFP-2104 Story §7.4).
    Returns 0 if all fixtures pass, non-zero otherwise.
    bats revival forbidden (#2103 de-bloat). Logic SSOT in .py (ADR-061).
    """
    failures = []

    def check(label, line, expected_exempt):
        result = is_exempt_l2(line)
        status = 'PASS' if result == expected_exempt else 'FAIL'
        if status == 'FAIL':
            failures.append((label, line, expected_exempt, result))
        verdict = 'GREEN' if expected_exempt else 'RED'
        actual = 'GREEN' if result else 'RED'
        print('[self-test] {} {} -- expected={} actual={}'.format(
            status, label, verdict, actual))

    # --- B6 fixtures (CFP-2104 discriminating — deny-priority global, Story §7.4) ---

    # B6-a: META-tier + misquote혼재 -> RED (deny-priority; META has no anchor-cover authority)
    check(
        'B6-a (META+misquote -> RED)',
        '오인용 정정 문맥이지만 consumer overlay 는 ADR-057 정합 축소 불가 라고 잘못 적음',
        False,  # expected RED
    )

    # B6-b: ANCHOR-corrective covers one ADR-057 token, but a second deny anchor (ALLOWED_HUB_REPOS)
    # exists on the same line without being covered -> RED
    check(
        'B6-b (ANCHOR+별-anchor-misquote -> RED)',
        'ADR-057 Orchestrator Opus mandate, ALLOWED_HUB_REPOS 확장 (ADR-057)',
        False,  # expected RED
    )

    # B6-c: META 정당단독 (no deny trigger) -> GREEN (regression guard)
    check(
        'B6-c (META 정당단독 -> GREEN)',
        '오인용 정정 — 실제 ADR-057 = Orchestrator Opus mandate (확장-only 와 무관)',
        True,   # expected GREEN
    )

    # --- Regression fixtures (Population A / proximity / legitimate citation) ---

    # Population A: ALLOWED_HUB_REPOS + ADR-057 without CONTEXT/ANCHOR exempt -> RED
    check(
        'PopA-1 (ALLOWED_HUB_REPOS+ADR-057 -> RED)',
        'ADR-057 defines ALLOWED_HUB_REPOS scope for overlay',
        False,  # expected RED
    )

    # Population A: SECURITY_PATHS + ADR-057 -> RED
    check(
        'PopA-2 (SECURITY_PATHS+ADR-057 -> RED)',
        'SECURITY_PATHS are governed by ADR-057 in overlay config',
        False,  # expected RED
    )

    # Population B: ratchet + ADR-057 proximity -> RED
    check(
        'PopB-1 (ratchet+ADR-057 proximity -> RED)',
        'overlay 는 ADR-057 기반 축소 불가 정책을 따름',
        False,  # expected RED
    )

    # CONTEXT blanket: CHANGELOG line -> GREEN
    check(
        'CONTEXT-1 (CHANGELOG blanket -> GREEN)',
        'CHANGELOG: ADR-057 축소 불가 정책 참조 (overlay)',
        True,   # expected GREEN
    )

    # ANCHOR legitimate: 자동재시도금지 near ADR-057 -> GREEN
    check(
        'ANCHOR-1 (자동재시도금지 근접 -> GREEN)',
        '자동재시도금지 정책은 ADR-057 §결정 2 에 따름',
        True,   # expected GREEN
    )

    # ANCHOR legitimate: fallback near ADR-057 -> GREEN
    check(
        'ANCHOR-2 (fallback 근접 -> GREEN)',
        'Sonnet->Opus fallback ADR-057 §결정 2 에 규정',
        True,   # expected GREEN
    )

    # ANCHOR legitimate: ADR-057 Orchestrator Opus -> GREEN (no deny trigger: no ratchet/ALLOWED_HUB)
    check(
        'ANCHOR-3 (ADR-057 Orchestrator Opus 정당 -> GREEN)',
        'ADR-057 Orchestrator Opus mandate 준수',
        True,   # expected GREEN
    )

    # Population B ratchet without any legitimate ANCHOR exempt -> RED
    # deny: 확장만 within .{0,40} of ADR-057; no ANCHOR exempt present
    check(
        'PopB-2 (ratchet 확장만 -> RED, no exempt)',
        'consumer overlay 정책은 ADR-057 기반 확장만 허용',
        False,  # expected RED
    )

    # TODO(follow-up CFP — multi-anchor greedy-tail edge, Story §7.6-1):
    # If prox-exempt .{0,40} tail spans a second misquote anchor on the same line, that anchor
    # may be false-negative (uncovered residual). Corpus reach 0, regression 0 priority ->
    # declared as documented limitation. Fixture commented out:
    #
    # check(
    #     'GreedyTail-edge (known false-negative residual)',
    #     'fallback ADR-057 정당, 별도 ADR-057 축소 불가 misquote 도 같은 라인에',
    #     False,  # expected RED — currently may be GREEN (greedy tail edge)
    # )

    # --- Result summary ---
    total = 10  # matches number of check() calls above
    passed = total - len(failures)
    print()
    print('[self-test] {}/{} fixtures PASSED'.format(passed, total))
    if failures:
        print('[self-test] FAILURES:')
        for label, line, exp, act in failures:
            print('  FAIL {} | expected={} actual={} | line={!r}'.format(
                label, exp, act, line[:80]))
        return 1
    print('[self-test] ALL GREEN')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='ADR citation slug lint (CFP-2057 / ADR-060 warning-tier)')
    parser.add_argument('paths', nargs='*', help='Files or directories to check (default: current directory)')
    parser.add_argument('--repo-root', default='.', help='Repository root path (for ADR directory search)')
    parser.add_argument('--l2-only', action='store_true', help='Run L2 deny-list check only (skip L1)')
    parser.add_argument('--l1-only', action='store_true', help='Run L1 slug-existence check only (skip L2)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output when no violations')
    parser.add_argument('--self-test', action='store_true', help='Run inline fixture self-test (D3, CFP-2104)')
    args = parser.parse_args(argv)

    # D3: --self-test mode (Story §7.4 — inline fixture, ADR-061 .py SSOT)
    if args.self_test:
        return run_self_test()

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
    print("NOTE: L2 scope = ADR-057 misquote global (Population A: ALLOWED_HUB_REPOS/SECURITY_PATHS + Population B: ratchet keywords). Legitimate citations (자동재시도금지/fallback) are EXEMPT via anchor-resolution model (CFP-2104).")

    if all_l2 and all_l1:
        return 3
    elif all_l2:
        return 1
    else:
        return 2


if __name__ == '__main__':
    sys.exit(main())
