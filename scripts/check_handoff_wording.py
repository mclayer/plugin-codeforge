#!/usr/bin/env python3
"""CFP-529 Wave 3 — Handoff Wording Linter.

Cross-channel consistency mechanical enforcement for handoff wording drift.
SSOT carrier for ADR-068 §결정 5 wording-ssot-grep-lint + ADR-068 Amendment 1
I-5 dimensional empirical grounding + severity-propagation-v1 contract.

Scope (5 영역, ADR-068 §결정 5 정합):
- scripts/**
- templates/**
- tests/**
- docs/**
- CLAUDE.md

Direction enum 3-way:
- forward (설계 → 구현): ADR/contract identifier verbatim 매칭 in source/tests
- backward (구현 → 설계): source/tests identifier reverse-lookup in ADR/contract
- lateral (sibling section): Story §3 ↔ §7 ↔ §8.5 cross-section diff

Drift 패턴 8종:
- Mechanical (5): synonym_substitution / unit_drift / modal_downgrade /
  boundary_inversion / scope_widening
- AI escalate stub (3): precision_loss / conditional_erasure / actor_drift

Exempt regions:
- dictionary_body (forbid-list / glossary body markers)
- verbatim_quote (lines starting with ">")
- consumer_overlay (.claude/_overlay/ paths)

Exit code (ADR-060 Amendment 2 §결정 15 tri-tier):
- 0: no violations (PASS) or warning tier (default) with findings
- 1: violations detected in strict mode
- 2: lint self-error (registry 누락 / config error / scope path 부재 등)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

# CFP-2661 F-CR-3: Windows cp949 인코딩 crash 회피 — stdout/stderr UTF-8 강제 (신규 lint
#   check_path_relocation_consistency.py 와 portability parity). D2 union 이 게이트를 non-vacuous 화
#   → 한국어 findings(em-dash `—` 등) emit → cp949 console(self-hosted Windows runner)에서
#   UnicodeEncodeError crash 위험(0-findings PASS 라인 포함). errors="replace" = fail-safe.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Constants (SSOT)
# ---------------------------------------------------------------------------

SCOPE_GLOBS: tuple[str, ...] = (
    "scripts",
    "templates",
    "tests",
    "docs",
    "CLAUDE.md",
)

# Exempt path substrings — consumer overlay must not be linted
EXEMPT_PATH_FRAGMENTS: tuple[str, ...] = (
    ".claude/_overlay/",
    "node_modules/",
    ".git/",
)

# Exempt region markers (inline)
DICTIONARY_BODY_START = re.compile(r"<!--\s*dictionary-body-start\s*-->")
DICTIONARY_BODY_END = re.compile(r"<!--\s*dictionary-body-end\s*-->")
VERBATIM_QUOTE = re.compile(r"^\s*>")

# 7-tier wording target hierarchy (forward direction propagation order)
WORDING_TIERS_7: tuple[str, ...] = (
    "ADR_decision",
    "change_plan_API_contract",
    "story_AC",
    "op_risk",
    "impl_manifest",
    "test_contract_threshold",
    "code_comment",
)

# ---------------------------------------------------------------------------
# Mechanical drift heuristics
# ---------------------------------------------------------------------------

# Pattern 1: synonym substitution — well-known semantic pairs that drift
SYNONYM_PAIRS: tuple[tuple[str, str], ...] = (
    ("error", "failure"),
    ("must", "shall"),
    ("abort", "halt"),
    ("orchestrator", "orchestration agent"),
    ("subagent", "sub-agent"),
    ("verdict", "judgement"),
)

# Pattern 2: unit drift — quantitative units that change between sections
UNIT_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(ms|s|seconds?|milliseconds?|minutes?|hours?|"
    r"MB|GB|KB|bytes?|TB)\b",
    re.IGNORECASE,
)

# Pattern 3: modal downgrade — RFC 2119 keyword sequence weakening
MODAL_RE = re.compile(
    r"\b(MUST(?:\s+NOT)?|SHOULD(?:\s+NOT)?|SHALL(?:\s+NOT)?|MAY|REQUIRED|"
    r"RECOMMENDED|OPTIONAL)\b"
)

# Modal strength rank (higher = stronger)
MODAL_RANK: dict[str, int] = {
    "MUST": 5,
    "MUST NOT": 5,
    "SHALL": 5,
    "SHALL NOT": 5,
    "REQUIRED": 5,
    "SHOULD": 3,
    "SHOULD NOT": 3,
    "RECOMMENDED": 3,
    "MAY": 1,
    "OPTIONAL": 1,
}

# Pattern 4: boundary inversion — inclusive/exclusive operator drift
BOUNDARY_RE = re.compile(
    r"(>=|<=|≥|≤|>|<|"
    r"at least|at most|less than|greater than|more than|fewer than)\s*"
    r"(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Pattern 5: scope widening — quantifier drift (single → all)
SCOPE_RE = re.compile(
    r"\b(single|one|all|every|each|any|some|none)\s+([A-Z][A-Za-z]+|"
    r"[a-z]+(?:\s+[a-z]+){0,2})",
)

# AI escalate stubs (3)
APPROX_RE = re.compile(
    r"\b(about|approximately|around|roughly|nearly|almost|~)\s*\d",
    re.IGNORECASE,
)
CONDITIONAL_RE = re.compile(
    r"\b(only when|only if|unless|except when|except if|provided that)\b",
    re.IGNORECASE,
)
ACTOR_RE = re.compile(
    r"\b(Orchestrator|ArchitectAgent|ArchitectPLAgent|DeveloperAgent|"
    r"DeveloperPLAgent|RequirementsPLAgent|DesignReviewPL|CodeReviewPL|"
    r"SecurityTestPL|PMOAgent|GitOpsAgent|ResearcherAgent|CodebaseMapperAgent|"
    r"RefactorAgent|SecurityArch|OpRiskArch|DataMigrationArch|"
    r"TestContractArch|LiveOps|LiveOrdering)\b"
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    """Handoff wording drift finding (severity-propagation-v1 정합)."""

    severity: str  # info / warning / critical
    drift_type: str  # one of 8 patterns
    direction: str  # forward / backward / lateral
    file: str
    line: int
    evidence: str
    suggestion: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LintConfig:
    """Linter runtime config."""

    root: Path
    scope: tuple[str, ...]
    direction: str  # forward / backward / lateral / all
    strict: bool
    json_out: bool
    skip_ai_stubs: bool = False


# ---------------------------------------------------------------------------
# File walkers
# ---------------------------------------------------------------------------


def is_exempt_path(path: Path) -> bool:
    """Return True if path is under exempt region (overlay / vendored)."""
    posix = path.as_posix()
    return any(frag in posix for frag in EXEMPT_PATH_FRAGMENTS)


def iter_scope_files(cfg: LintConfig) -> Iterable[Path]:
    """Yield candidate files under configured scope.

    Only `.md`, `.yml`, `.yaml`, `.sh`, `.py`, `.bats` text files considered.
    """
    text_exts = {".md", ".yml", ".yaml", ".sh", ".py", ".bats", ".json"}
    for top in cfg.scope:
        target = cfg.root / top
        if not target.exists():
            continue
        if target.is_file():
            if target.suffix in text_exts or target.name == "CLAUDE.md":
                if not is_exempt_path(target):
                    yield target
            continue
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in text_exts and path.name != "CLAUDE.md":
                continue
            if is_exempt_path(path):
                continue
            yield path


def read_lines(path: Path) -> list[str]:
    """Read file with utf-8 lenient fallback."""
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()


def strip_exempt_regions(lines: list[str]) -> list[tuple[int, str]]:
    """Return (lineno, content) tuples skipping exempt inline regions."""
    out: list[tuple[int, str]] = []
    in_dictionary = False
    for idx, line in enumerate(lines, start=1):
        if DICTIONARY_BODY_START.search(line):
            in_dictionary = True
            continue
        if DICTIONARY_BODY_END.search(line):
            in_dictionary = False
            continue
        if in_dictionary:
            continue
        if VERBATIM_QUOTE.match(line):
            continue
        out.append((idx, line))
    return out


# ---------------------------------------------------------------------------
# Mechanical pattern detectors (5)
# ---------------------------------------------------------------------------


def detect_synonym_substitution(cfg: LintConfig) -> list[Finding]:
    """Pattern 1: synonym substitution per-file co-occurrence.

    Stub heuristic: if both members of a known synonym pair appear within
    the same file, emit a single info-level finding pointing to first match.
    Full semantic drift detection deferred to AI escalate path.
    """
    findings: list[Finding] = []
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        text = "\n".join(lines).lower()
        for a, b in SYNONYM_PAIRS:
            if a in text and b in text:
                for idx, line in strip_exempt_regions(lines):
                    if a in line.lower() or b in line.lower():
                        rel = path.relative_to(cfg.root).as_posix()
                        findings.append(
                            Finding(
                                severity="info",
                                drift_type="synonym_substitution",
                                direction="lateral",
                                file=rel,
                                line=idx,
                                evidence=f"both '{a}' and '{b}' co-occur",
                                suggestion=(
                                    f"pick one term and align — keep '{a}' or '{b}'"
                                ),
                            )
                        )
                        break
                break  # one finding per file per pair scan
    return findings


def _canonicalize_unit(raw: str) -> str:
    """Map raw unit token to canonical family key."""
    lower = raw.lower()
    if lower == "ms" or lower.startswith("millisecond"):
        return "millisecond"
    if lower == "s" or lower.startswith("second"):
        return "second"
    if lower.startswith("minute"):
        return "minute"
    if lower.startswith("hour"):
        return "hour"
    if lower in {"kb"} or lower.startswith("kilobyte"):
        return "kb"
    if lower in {"mb"} or lower.startswith("megabyte"):
        return "mb"
    if lower in {"gb"} or lower.startswith("gigabyte"):
        return "gb"
    if lower in {"tb"} or lower.startswith("terabyte"):
        return "tb"
    if lower.startswith("byte"):
        return "byte"
    return lower


def detect_unit_drift(cfg: LintConfig) -> list[Finding]:
    """Pattern 2: unit drift — multiple distinct units in same file."""
    findings: list[Finding] = []
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        units_seen: dict[str, int] = {}
        first_match_line: dict[str, int] = {}
        for idx, line in strip_exempt_regions(lines):
            for match in UNIT_RE.finditer(line):
                unit = _canonicalize_unit(match.group(2))
                units_seen[unit] = units_seen.get(unit, 0) + 1
                first_match_line.setdefault(unit, idx)
        # Detect "ms" vs "s" co-existence or "MB" vs "byte" co-existence
        time_units = {"millisecond", "second", "minute", "hour"} & set(units_seen)
        size_units = {"byte", "kb", "mb", "gb", "tb"} & set(units_seen)
        if len(time_units) > 1 or len(size_units) > 1:
            rel = path.relative_to(cfg.root).as_posix()
            mixed = sorted(time_units | size_units)
            first_line = min(first_match_line[u] for u in mixed if u in first_match_line)
            findings.append(
                Finding(
                    severity="info",
                    drift_type="unit_drift",
                    direction="lateral",
                    file=rel,
                    line=first_line,
                    evidence=f"mixed units: {', '.join(mixed)}",
                    suggestion="normalize unit family (e.g., all ms or all s)",
                )
            )
    return findings


def detect_modal_downgrade(cfg: LintConfig) -> list[Finding]:
    """Pattern 3: modal downgrade RFC 2119 — adjacent MUST→SHOULD→MAY."""
    findings: list[Finding] = []
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        prev_modal: tuple[str, int] | None = None
        for idx, line in strip_exempt_regions(lines):
            for match in MODAL_RE.finditer(line):
                modal = match.group(1).upper()
                rank = MODAL_RANK.get(modal, 0)
                if prev_modal is not None:
                    prev_rank = MODAL_RANK.get(prev_modal[0], 0)
                    # downgrade: prev stronger than current and within 20 lines
                    if (
                        prev_rank > rank
                        and rank > 0
                        and (idx - prev_modal[1]) <= 20
                    ):
                        rel = path.relative_to(cfg.root).as_posix()
                        findings.append(
                            Finding(
                                severity="warning",
                                drift_type="modal_downgrade",
                                direction="lateral",
                                file=rel,
                                line=idx,
                                evidence=(
                                    f"'{prev_modal[0]}' (line {prev_modal[1]}) → "
                                    f"'{modal}' (line {idx})"
                                ),
                                suggestion=(
                                    "align modal strength or document intentional "
                                    "scope-narrowing"
                                ),
                            )
                        )
                prev_modal = (modal, idx)
    return findings


def detect_boundary_inversion(cfg: LintConfig) -> list[Finding]:
    """Pattern 4: boundary inversion — ≥3 vs >3 vs at least 3 co-occurrence."""
    findings: list[Finding] = []
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        seen_pairs: dict[str, list[tuple[str, int]]] = {}
        for idx, line in strip_exempt_regions(lines):
            for match in BOUNDARY_RE.finditer(line):
                op = match.group(1).lower()
                num = match.group(2)
                seen_pairs.setdefault(num, []).append((op, idx))
        for num, occurrences in seen_pairs.items():
            ops = {op for op, _ in occurrences}
            # Inclusive vs exclusive boundary mixing
            inclusive_ops = {">=", "<=", "≥", "≤", "at least", "at most"}
            exclusive_ops = {">", "<", "less than", "greater than", "more than", "fewer than"}
            has_inc = bool(ops & inclusive_ops)
            has_exc = bool(ops & exclusive_ops)
            if has_inc and has_exc:
                rel = path.relative_to(cfg.root).as_posix()
                first_line = occurrences[0][1]
                findings.append(
                    Finding(
                        severity="warning",
                        drift_type="boundary_inversion",
                        direction="lateral",
                        file=rel,
                        line=first_line,
                        evidence=(
                            f"boundary {num} uses both inclusive and exclusive operators: "
                            f"{sorted(ops)}"
                        ),
                        suggestion=(
                            "align inclusive/exclusive intent across all references "
                            f"to threshold {num}"
                        ),
                    )
                )
    return findings


def _canonicalize_subject(raw: str) -> str:
    """Normalize subject token for cross-quantifier comparison (de-pluralize)."""
    s = raw.lower().strip()
    if s.endswith("ies") and len(s) > 4:
        return s[:-3] + "y"
    if s.endswith("ses") and len(s) > 4:
        return s[:-2]
    if s.endswith("s") and len(s) > 3 and not s.endswith("ss"):
        return s[:-1]
    return s


def detect_scope_widening(cfg: LintConfig) -> list[Finding]:
    """Pattern 5: scope widening — single ↔ all quantifier mixing."""
    findings: list[Finding] = []
    narrow = {"single", "one"}
    broad = {"all", "every", "each"}
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        narrow_subjects: dict[str, int] = {}
        broad_subjects: dict[str, int] = {}
        for idx, line in strip_exempt_regions(lines):
            for match in SCOPE_RE.finditer(line):
                quant = match.group(1).lower()
                subject = _canonicalize_subject(match.group(2))
                if quant in narrow:
                    narrow_subjects.setdefault(subject, idx)
                elif quant in broad:
                    broad_subjects.setdefault(subject, idx)
        common = set(narrow_subjects) & set(broad_subjects)
        for subject in common:
            rel = path.relative_to(cfg.root).as_posix()
            line_no = min(narrow_subjects[subject], broad_subjects[subject])
            findings.append(
                Finding(
                    severity="warning",
                    drift_type="scope_widening",
                    direction="lateral",
                    file=rel,
                    line=line_no,
                    evidence=(
                        f"subject '{subject}' addressed as both narrow and broad scope"
                    ),
                    suggestion=(
                        f"clarify whether '{subject}' applies single or all instances"
                    ),
                )
            )
    return findings


# ---------------------------------------------------------------------------
# AI escalate stubs (3)
# ---------------------------------------------------------------------------


def stub_precision_loss(cfg: LintConfig) -> list[Finding]:
    """AI escalate stub: precision loss (approximation language near numbers)."""
    if cfg.skip_ai_stubs:
        return []
    findings: list[Finding] = []
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        for idx, line in strip_exempt_regions(lines):
            if APPROX_RE.search(line):
                rel = path.relative_to(cfg.root).as_posix()
                findings.append(
                    Finding(
                        severity="info",
                        drift_type="precision_loss",
                        direction="lateral",
                        file=rel,
                        line=idx,
                        evidence=line.strip()[:120],
                        suggestion=(
                            "replace approximation with empirical bound — "
                            "ADR-068 Amendment 1 I-5 dimensional grounding"
                        ),
                    )
                )
    return findings


def stub_conditional_erasure(cfg: LintConfig) -> list[Finding]:
    """AI escalate stub: conditional erasure (cross-section conditional drop)."""
    if cfg.skip_ai_stubs:
        return []
    findings: list[Finding] = []
    # Stub: collect lines with conditional clauses for AI review carrier.
    for path in iter_scope_files(cfg):
        lines = read_lines(path)
        for idx, line in strip_exempt_regions(lines):
            if CONDITIONAL_RE.search(line):
                # Emit only when conditional appears in design-tier files (ADR/contract)
                rel = path.relative_to(cfg.root).as_posix()
                if "adr/" in rel or "inter-plugin-contracts/" in rel:
                    findings.append(
                        Finding(
                            severity="info",
                            drift_type="conditional_erasure",
                            direction="forward",
                            file=rel,
                            line=idx,
                            evidence=line.strip()[:120],
                            suggestion=(
                                "verify conditional preserved in downstream "
                                "impl-manifest / test-contract / code"
                            ),
                        )
                    )
    return findings


def stub_actor_drift(cfg: LintConfig) -> list[Finding]:
    """AI escalate stub: actor drift (responsibility mismatch across sections)."""
    if cfg.skip_ai_stubs:
        return []
    findings: list[Finding] = []
    for path in iter_scope_files(cfg):
        rel = path.relative_to(cfg.root).as_posix()
        # Only emit on Story files where actor cross-reference 의무
        if "stories/" not in rel and "change-plans/" not in rel:
            continue
        lines = read_lines(path)
        actors_seen: dict[str, list[int]] = {}
        for idx, line in strip_exempt_regions(lines):
            for match in ACTOR_RE.finditer(line):
                actor = match.group(1)
                actors_seen.setdefault(actor, []).append(idx)
        # Stub heuristic — if ≥ 3 distinct actors in same Story, flag for AI review
        if len(actors_seen) >= 3:
            actors_list = sorted(actors_seen)
            first_line = min(min(v) for v in actors_seen.values())
            findings.append(
                Finding(
                    severity="info",
                    drift_type="actor_drift",
                    direction="lateral",
                    file=rel,
                    line=first_line,
                    evidence=f"{len(actors_seen)} actors: {', '.join(actors_list[:5])}",
                    suggestion=(
                        "AI review: verify each actor's responsibility consistent "
                        "across §3 / §7 / §8.5 sections"
                    ),
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Direction enum handlers (3)
# ---------------------------------------------------------------------------


# Identifier pattern — snake_case or kebab-case
#
# CodeQL py/redos remediation: the original pattern
#   `[a-z_][a-z0-9_]{4,}(?:_[a-z0-9_]+){1,}`
# placed `_` in both the long inner class `[a-z0-9_]{4,}` and the trailing
# repeated group `(?:_[a-z0-9_]+){1,}`, causing exponential backtracking
# (catastrophic worst case on strings like `0_0_0_…`).
# Fix: enforce disjoint character classes by alternating maximal alphanumeric
# runs (`[a-z0-9]+`) with explicit underscore runs (`_+`). Match coverage
# verified equivalent against the repo corpus (single- and multi-underscore
# identifiers both preserved); hyphenated branch unchanged.
IDENTIFIER_RE = re.compile(
    r"`("
    r"[a-z_][a-z0-9]*(?:_+[a-z0-9]+)+_*"
    r"|"
    r"[a-z][a-zA-Z0-9]+(?:-[a-zA-Z0-9]+){1,}"
    r")`"
)


def _collect_identifiers(cfg: LintConfig, scope_dir: str) -> dict[str, list[tuple[str, int]]]:
    """Collect backtick-quoted identifiers from a scope subtree."""
    seen: dict[str, list[tuple[str, int]]] = {}
    target = cfg.root / scope_dir
    if not target.exists():
        return seen
    for path in target.rglob("*.md"):
        if is_exempt_path(path):
            continue
        lines = read_lines(path)
        rel = path.relative_to(cfg.root).as_posix()
        for idx, line in strip_exempt_regions(lines):
            for match in IDENTIFIER_RE.finditer(line):
                ident = match.group(1)
                seen.setdefault(ident, []).append((rel, idx))
    return seen


def _collect_adr_identifiers(cfg: LintConfig) -> dict[str, list[tuple[str, int]]]:
    """CFP-2661 D2: union docs/adr ∪ archive/adr.

    ADR 실 위치 = archive/adr (PR #1973). docs/adr 단독은 dead-path → _collect_identifiers 가
    target.exists()==False 조기 return(빈 dict) → detect_forward/backward 가 `if not adr_idents: return`
    로 vacuous(항상 findings 0). archive/adr union 으로 실 collection(≥1269 identifier) 복구.
    consumer 정답 경로 docs/adr 는 union 보존(치환·삭제 아님).
    """
    merged: dict[str, list[tuple[str, int]]] = {}
    for scope_dir in ("docs/adr", "archive/adr"):
        for ident, locs in _collect_identifiers(cfg, scope_dir).items():
            merged.setdefault(ident, []).extend(locs)
    return merged


def detect_forward(cfg: LintConfig) -> list[Finding]:
    """Forward (설계 → 구현): ADR identifiers must appear in scripts/tests."""
    findings: list[Finding] = []
    adr_idents = _collect_adr_identifiers(cfg)
    if not adr_idents:
        return findings
    # Collect impl identifiers
    impl_text_lines: list[tuple[str, int, str]] = []
    for scope in ("scripts", "tests", "templates"):
        target = cfg.root / scope
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if not path.is_file() or is_exempt_path(path):
                continue
            if path.suffix not in {".py", ".sh", ".bats", ".yml", ".yaml"}:
                continue
            rel = path.relative_to(cfg.root).as_posix()
            try:
                for idx, line in enumerate(read_lines(path), start=1):
                    impl_text_lines.append((rel, idx, line))
            except OSError:
                continue
    # Stub: track which ADR idents lack impl reference (warning)
    impl_text_joined = "\n".join(t[2] for t in impl_text_lines)
    for ident, locations in adr_idents.items():
        # Filter — only flag identifiers that look like contract/config keys
        if not (ident.endswith("_passed") or ident.endswith("_check") or "-v" in ident):
            continue
        if ident not in impl_text_joined:
            rel, idx = locations[0]
            findings.append(
                Finding(
                    severity="info",
                    drift_type="forward_missing_impl",
                    direction="forward",
                    file=rel,
                    line=idx,
                    evidence=f"identifier `{ident}` declared in ADR but absent in impl",
                    suggestion=(
                        "add impl carrier (script/test/workflow) referencing "
                        f"`{ident}` or document deferral in change-plan"
                    ),
                )
            )
    return findings


def detect_backward(cfg: LintConfig) -> list[Finding]:
    """Backward (구현 → 설계): impl identifiers must trace to ADR/contract.

    Code identifier without ADR/contract def = Amendment trigger (ratchet self-application).
    """
    findings: list[Finding] = []
    adr_idents = _collect_adr_identifiers(cfg)  # CFP-2661 D2: union docs/adr ∪ archive/adr
    contract_idents = _collect_identifiers(cfg, "docs/inter-plugin-contracts")
    design_corpus = set(adr_idents) | set(contract_idents)
    # Note: empty design_corpus is itself a backward drift signal (impl-only
    # identifiers). We continue and emit warnings when impl idents exist.
    # Collect impl identifiers from scripts/tests
    impl_idents: dict[str, list[tuple[str, int]]] = {}
    for scope in ("scripts", "tests"):
        target = cfg.root / scope
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if not path.is_file() or is_exempt_path(path):
                continue
            if path.suffix not in {".py", ".sh", ".bats"}:
                continue
            rel = path.relative_to(cfg.root).as_posix()
            for idx, line in enumerate(read_lines(path), start=1):
                for match in IDENTIFIER_RE.finditer(line):
                    ident = match.group(1)
                    impl_idents.setdefault(ident, []).append((rel, idx))
    # Stub: report impl idents missing from design corpus (limit to clearly
    # contract-like idents to avoid false positives)
    for ident, locations in impl_idents.items():
        if not (ident.endswith("_passed") or ident.endswith("_check") or "-v" in ident):
            continue
        if ident not in design_corpus:
            rel, idx = locations[0]
            findings.append(
                Finding(
                    severity="warning",
                    drift_type="backward_missing_design",
                    direction="backward",
                    file=rel,
                    line=idx,
                    evidence=(
                        f"identifier `{ident}` used in impl but absent in ADR/contract"
                    ),
                    suggestion=(
                        "ADR Amendment 또는 rename 의무 — ADR-058/064 evidence-gated symmetric ratchet "
                        "self-application"
                    ),
                )
            )
    return findings


SECTION_RE = re.compile(r"^##\s+§?(\d+(?:\.\d+)?)\s+")


def detect_lateral(cfg: LintConfig) -> list[Finding]:
    """Lateral (sibling section): Story §3 ↔ §7 ↔ §8.5 cross-section diff.

    Walks Story files in docs/stories and checks identifier overlap across
    well-known sections (§3 / §7 / §8.5).
    """
    findings: list[Finding] = []
    story_dir = cfg.root / "docs" / "stories"
    if not story_dir.exists():
        return findings
    for path in story_dir.rglob("*.md"):
        if is_exempt_path(path):
            continue
        lines = read_lines(path)
        sections: dict[str, list[tuple[int, str]]] = {}
        current = "0"
        for idx, line in enumerate(lines, start=1):
            section_match = SECTION_RE.match(line)
            if section_match:
                current = section_match.group(1)
            sections.setdefault(current, []).append((idx, line))
        # Extract identifiers per target section
        target_sections = ("3", "7", "8.5")
        section_idents: dict[str, set[str]] = {}
        for sec in target_sections:
            idents: set[str] = set()
            for _, content in sections.get(sec, []):
                for match in IDENTIFIER_RE.finditer(content):
                    idents.add(match.group(1))
            section_idents[sec] = idents
        # Stub: flag idents present in §3 but absent in §8.5 (impl-manifest drift)
        only_in_3 = section_idents.get("3", set()) - section_idents.get("8.5", set())
        if only_in_3:
            rel = path.relative_to(cfg.root).as_posix()
            # find first line in §3 referencing one such ident
            first_line = 1
            for idx, content in sections.get("3", []):
                if any(f"`{i}`" in content for i in only_in_3):
                    first_line = idx
                    break
            sample = sorted(only_in_3)[:3]
            findings.append(
                Finding(
                    severity="info",
                    drift_type="lateral_section_drift",
                    direction="lateral",
                    file=rel,
                    line=first_line,
                    evidence=(
                        f"{len(only_in_3)} identifier(s) in §3 not present in §8.5: "
                        f"{', '.join(sample)}"
                    ),
                    suggestion=(
                        "add §8.5 impl-manifest row OR document §3-only scope "
                        "(non-impl declarative)"
                    ),
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_lint(cfg: LintConfig) -> list[Finding]:
    """Run all enabled detectors and return aggregated findings."""
    findings: list[Finding] = []

    # Mechanical (5)
    findings.extend(detect_synonym_substitution(cfg))
    findings.extend(detect_unit_drift(cfg))
    findings.extend(detect_modal_downgrade(cfg))
    findings.extend(detect_boundary_inversion(cfg))
    findings.extend(detect_scope_widening(cfg))

    # AI escalate stubs (3)
    findings.extend(stub_precision_loss(cfg))
    findings.extend(stub_conditional_erasure(cfg))
    findings.extend(stub_actor_drift(cfg))

    # Direction enum (3)
    if cfg.direction in ("forward", "all"):
        findings.extend(detect_forward(cfg))
    if cfg.direction in ("backward", "all"):
        findings.extend(detect_backward(cfg))
    if cfg.direction in ("lateral", "all"):
        findings.extend(detect_lateral(cfg))

    return findings


def format_text(findings: list[Finding]) -> str:
    """Render findings in human-readable text."""
    if not findings:
        return "[handoff-wording-check] PASS — 0 findings\n"
    lines: list[str] = [f"[handoff-wording-check] {len(findings)} finding(s):"]
    for f in findings:
        lines.append(
            f"  [{f.severity}] {f.drift_type} ({f.direction}) "
            f"{f.file}:{f.line}"
        )
        lines.append(f"      evidence:   {f.evidence}")
        lines.append(f"      suggestion: {f.suggestion}")
    return "\n".join(lines) + "\n"


def format_json(findings: list[Finding]) -> str:
    """Render findings as JSON (severity-propagation-v1 compatible)."""
    return json.dumps(
        {
            "schema": "severity-propagation-v1",
            "tool": "check_handoff_wording.py",
            "findings": [f.to_dict() for f in findings],
        },
        indent=2,
        ensure_ascii=False,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CFP-529 Wave 3 handoff wording linter (ADR-068 §결정 5)"
    )
    parser.add_argument(
        "--root", default=".", help="Repository root (default: cwd)"
    )
    parser.add_argument(
        "--scope",
        nargs="+",
        default=list(SCOPE_GLOBS),
        help="Scope paths (default: scripts templates tests docs CLAUDE.md)",
    )
    parser.add_argument(
        "--direction",
        choices=["forward", "backward", "lateral", "all"],
        default="all",
        help="Direction enum (default: all)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on any findings (default: exit 0 — warning tier)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="JSON output (severity-propagation-v1 schema)",
    )
    parser.add_argument(
        "--skip-ai-stubs",
        action="store_true",
        help="Skip 3 AI escalate stub patterns (mechanical-only run)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    if not root.exists():
        sys.stderr.write(f"[handoff-wording-check] ERROR root path absent: {root}\n")
        return 2
    cfg = LintConfig(
        root=root,
        scope=tuple(args.scope),
        direction=args.direction,
        strict=args.strict,
        json_out=args.json_out,
        skip_ai_stubs=args.skip_ai_stubs,
    )
    findings = run_lint(cfg)
    if cfg.json_out:
        sys.stdout.write(format_json(findings) + "\n")
    else:
        sys.stdout.write(format_text(findings))
    if not findings:
        return 0
    if cfg.strict:
        return 1
    sys.stderr.write(
        f"[handoff-wording-check] advisory — {len(findings)} finding(s) "
        "(warning tier, exit 0). Use --strict for CI gating.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
