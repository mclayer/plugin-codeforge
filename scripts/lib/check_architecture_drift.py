#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-923 / ADR-078 P-S4 mechanism — architecture-drift mechanical lint (warning mode)
# ADR-061 §결정 1 — heredoc Python 외부 .py split (thin wrapper: scripts/check-architecture-drift.sh)
#
# Lint scope: docs/architecture/**/*.md  (architecture_doc kind)
# Detection class 5 active (Story §5.2 + CFP-948 activation of deferred c+e):
#   (a) module enumeration parity: wrapper + 6 lane plugin name in `## 모듈` section text body
#   (b) inter-plugin-contracts enumeration parity: MANIFEST.yaml 7 kind:contract in `## 인터페이스 계약`
#   (c) MANIFEST cross-ref strict bidirectional (CFP-948 activation): doc body 의 contract token
#       이 MANIFEST.yaml `contracts:` 명단 안에 존재해야 함 (stale reference 감지)
#   (d) anti-scope guard violation detection: class/def/import/signature line patterns
#       + H2 외 H2 (4 H2 closed-enum 외 H2 heading) detected anywhere in doc body
#   (e) dataflow stage propagation completeness (CFP-948 activation): `## 데이터 흐름` body 가
#       stage 어휘 + propagation entity 어휘 양쪽 ≥1 보유 검증 (lightweight tier)
#
# 4-guard FP 완화 (CFP-841 corpus-claim-verify §결정 4/6 EC-3 prior art):
#   (1) scope guard: docs/architecture/**/*.md 만 scan
#   (2) citation≠assertion exemption: fenced code (``` / ~~~) + blockquote (>) skip
#   (3) forward-only effective-date: workflow paths trigger
#   (4) self-referential exemption: Story/Change-Plan/ADR 본문 = scope guard 로 자연 면제
#
# Exit codes: 0 = PASS / 1 = WARN (violation 검출, warning mode) / 2 = ERROR
#
# INV-DM-2 정합: detect-only read-only — file 변경 0, autofix 채널 금지.
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCOPE_DIR = "docs/architecture"

# 4 H2 closed-enum SSOT (ADR-078 §결정 1 verbatim)
ALLOWED_H2 = {"## 모듈", "## 경계", "## 인터페이스 계약", "## 데이터 흐름"}

# (a) 7 module names
EXPECTED_MODULES = [
    "codeforge",
    "codeforge-requirements",
    "codeforge-design",
    "codeforge-review",
    "codeforge-develop",
    "codeforge-test",
    "codeforge-pmo",
]

# (b) 7 kind:contract names
EXPECTED_CONTRACTS = [
    "review_verdict",
    "requirements_output",
    "design_output",
    "develop_output",
    "test_verdict",
    "pmo_output",
    "git_ops_event",
]

# (d) anti-scope guard line patterns
ANTI_SCOPE_PATTERNS = [
    (re.compile(r"^\s*class\s+[A-Z]\w+\s*[:(\{]"), "class definition (line-level)"),
    (re.compile(r"^\s*def\s+\w+\s*\("), "def signature (line-level)"),
    (re.compile(r"^\s*function\s+\w+\s*\("), "function signature (line-level)"),
    (re.compile(r"^\s*import\s+[\w\.]+"), "import statement (line-level)"),
    (re.compile(r"^\s*from\s+[\w\.]+\s+import\s+"), "from-import statement (line-level)"),
    (re.compile(r"\w+\s*\([^)]*\)\s*->\s*\w+"), "function signature with return type (line-level)"),
]

# (c) MANIFEST.yaml SSOT for strict bidirectional cross-ref (CFP-948 activation)
MANIFEST_PATH = "docs/inter-plugin-contracts/MANIFEST.yaml"
# Pattern to detect contract-like tokens in §인터페이스 계약 body
# Matches snake_case identifiers ending in _verdict / _output / _event (codeforge family convention)
CONTRACT_TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9_-])([a-z][a-z0-9_]*_(?:verdict|output|event))(?![A-Za-z0-9_-])")

# (e) dataflow stage propagation keywords (CFP-948 activation, lightweight stage check)
# §데이터 흐름 body 안 stage 어휘 + propagation entity 어휘 양쪽 최소 1개씩 존재 검증
DATAFLOW_STAGE_KEYWORDS = ("input", "transform", "output", "흐름", "propagation")
DATAFLOW_PROPAGATION_KEYWORDS = ("lane", "event", "artifact", "spawn", "verdict", "contract")


def normalize_path(p):
    return str(p).replace("\\", "/")


def in_scope(p):
    norm = normalize_path(p)
    return norm.startswith(SCOPE_DIR + "/") and norm.endswith(".md")


def collect_scope_files():
    out = []
    base = Path(SCOPE_DIR)
    if not base.is_dir():
        return out
    for path in base.rglob("*.md"):
        if path.is_file():
            out.append(normalize_path(path))
    return sorted(set(out))


def parse_h2_sections(text):
    """Extract H2 sections (fenced code + inline content). Returns dict {heading: body}."""
    sections = {}
    current_h2 = None
    current_body = []
    in_fence = False
    fence_marker = None

    for raw_line in text.splitlines():
        stripped = raw_line.lstrip()

        if not in_fence:
            for marker in ("```", "~~~"):
                if stripped.startswith(marker):
                    in_fence = True
                    fence_marker = marker
                    break
            if in_fence:
                if current_h2 is not None:
                    current_body.append(raw_line)
                continue
        else:
            if fence_marker and stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = None
            if current_h2 is not None:
                current_body.append(raw_line)
            continue

        if raw_line.startswith("## ") and not raw_line.startswith("### "):
            if current_h2 is not None:
                sections[current_h2] = "\n".join(current_body)
            heading = raw_line.rstrip()
            heading = re.sub(r"\s*\{#[^}]+\}\s*$", "", heading)
            current_h2 = heading
            current_body = []
        else:
            if current_h2 is not None:
                current_body.append(raw_line)

    if current_h2 is not None:
        sections[current_h2] = "\n".join(current_body)

    return sections


def detect_h2_closed_enum(sections):
    findings = []
    for heading in sections.keys():
        if heading not in ALLOWED_H2:
            findings.append((heading, "H2 closed-enum 위반 — 4 영역 외 H2 발견 (ADR-078 §결정 1 anti-scope guard)"))
    return findings


def detect_module_parity(sections):
    findings = []
    body = sections.get("## 모듈", "")
    if not body:
        return [("module-parity", "`## 모듈` 섹션 부재 또는 빈 본문")]
    for module in EXPECTED_MODULES:
        if module == "codeforge":
            pattern = re.compile(r"(?<![A-Za-z0-9\-])codeforge(?![A-Za-z0-9\-])")
        else:
            pattern = re.compile(rf"(?<![A-Za-z0-9\-]){re.escape(module)}(?![A-Za-z0-9\-])")
        if not pattern.search(body):
            findings.append((module, f"module name 부재 — `## 모듈` 섹션에 `{module}` 미언급 (parity FAIL)"))
    return findings


def detect_contract_parity(sections):
    findings = []
    body = sections.get("## 인터페이스 계약", "")
    if not body:
        return [("contract-parity", "`## 인터페이스 계약` 섹션 부재 또는 빈 본문")]
    for contract in EXPECTED_CONTRACTS:
        pattern = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(contract)}(?![A-Za-z0-9_-])")
        if not pattern.search(body):
            findings.append((contract, f"contract name 부재 — `## 인터페이스 계약` 섹션에 `{contract}` 미언급 (parity FAIL)"))
    return findings


def _load_manifest_contract_names():
    """Read MANIFEST.yaml `contracts:` list and return set of `name:` values.

    Returns empty set if MANIFEST missing or yaml unavailable — caller treats as
    skip (not a violation). CFP-948 / Story-4 detection class (c) activation.
    """
    try:
        import yaml  # PyYAML; available in CI runner per existing lint scripts
    except ImportError:
        return None  # signal: skip class (c) — dependency missing
    p = Path(MANIFEST_PATH)
    if not p.exists():
        return None
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return set()
    contracts = data.get("contracts", [])
    if not isinstance(contracts, list):
        return set()
    names = set()
    for entry in contracts:
        if isinstance(entry, dict) and "name" in entry:
            names.add(str(entry["name"]))
    return names


def detect_contract_manifest_strict(sections):
    """Class (c) — Bidirectional cross-ref strict between §인터페이스 계약 H2 and MANIFEST.yaml.

    Forward direction (MANIFEST → doc) is covered by class (b) detect_contract_parity (soft).
    This function covers REVERSE direction (doc → MANIFEST): every contract-like token
    in §인터페이스 계약 body must exist in MANIFEST `contracts:` list. Catches stale
    references to deprecated/removed contracts.

    CFP-948 / Story-4 deferred-followup activation.
    """
    findings = []
    body = sections.get("## 인터페이스 계약", "")
    if not body:
        return []  # class (b) already reports missing section — avoid double-counting
    manifest_names = _load_manifest_contract_names()
    if manifest_names is None:
        return []  # PyYAML or MANIFEST missing — soft skip (not a doc-drift violation)
    # Strip fenced code blocks + blockquotes from body to avoid false positives in examples
    body_filtered = []
    in_fence = False
    for line in body.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith(">"):
            continue  # blockquote exempt
        body_filtered.append(line)
    body_text = "\n".join(body_filtered)
    seen_tokens = set()
    for match in CONTRACT_TOKEN_PATTERN.finditer(body_text):
        tok = match.group(1)
        if tok in seen_tokens:
            continue
        seen_tokens.add(tok)
        if tok not in manifest_names:
            findings.append((tok, f"contract token `{tok}` 가 §인터페이스 계약 body 에 등장하나 MANIFEST.yaml `contracts:` 명단 부재 — stale reference 또는 typo (class (c) bidirectional strict)"))
    return findings


def detect_dataflow_stage_propagation(sections):
    """Class (e) — §데이터 흐름 H2 body 가 stage 어휘 + propagation entity 어휘 양쪽 보유 검증.

    Light heuristic — input/transform/output 류 stage 어휘 ≥1개 AND lane/event/artifact
    류 propagation entity 어휘 ≥1개. 둘 다 부재 시 본 H2 가 빈 prose 또는 무관 내용
    가능성 → drift signal.

    CFP-948 / Story-4 deferred-followup activation. Light tier — Story §6 design
    granularity 영역과 disjoint scope.
    """
    findings = []
    body = sections.get("## 데이터 흐름", "")
    if not body or not body.strip():
        return [("dataflow-empty", "`## 데이터 흐름` 섹션 부재 또는 빈 본문 (class (e) propagation completeness)")]
    body_lower = body.lower()
    has_stage = any(kw in body_lower for kw in DATAFLOW_STAGE_KEYWORDS)
    has_prop = any(kw in body_lower for kw in DATAFLOW_PROPAGATION_KEYWORDS)
    if not has_stage:
        findings.append(("dataflow-stage", f"`## 데이터 흐름` 본문에 stage 어휘 부재 (기대: {'/'.join(DATAFLOW_STAGE_KEYWORDS)} 중 ≥1) — class (e) propagation completeness"))
    if not has_prop:
        findings.append(("dataflow-propagation", f"`## 데이터 흐름` 본문에 propagation entity 어휘 부재 (기대: {'/'.join(DATAFLOW_PROPAGATION_KEYWORDS)} 중 ≥1) — class (e) propagation completeness"))
    return findings


def detect_anti_scope_guard(text):
    findings = []
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
        if raw_line.startswith("## "):
            continue

        for pattern, description in ANTI_SCOPE_PATTERNS:
            if pattern.search(raw_line):
                findings.append((line_num, raw_line.rstrip(), description))
                break

    return findings


def scan_file(p):
    text = Path(p).read_text(encoding="utf-8", errors="replace")
    sections = parse_h2_sections(text)
    return {
        "h2_closed_enum": detect_h2_closed_enum(sections),
        "module_parity": detect_module_parity(sections),
        "contract_parity": detect_contract_parity(sections),
        "contract_manifest_strict": detect_contract_manifest_strict(sections),  # class (c) CFP-948
        "dataflow_stage_propagation": detect_dataflow_stage_propagation(sections),  # class (e) CFP-948
        "anti_scope_guard": detect_anti_scope_guard(text),
    }


def main(argv):
    paths = argv[1:]
    if not paths:
        paths = collect_scope_files()
    else:
        filtered = []
        for p in paths:
            norm = normalize_path(p)
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
            print(f"check-architecture-drift: path 부재 (skip): {p}", file=sys.stderr)
            continue
        files_checked += 1
        try:
            result = scan_file(p)
        except OSError as exc:
            print(f"check-architecture-drift: file read error {p}: {exc}", file=sys.stderr)
            sys.exit(2)

        file_total = (
            len(result["h2_closed_enum"])
            + len(result["module_parity"])
            + len(result["contract_parity"])
            + len(result["contract_manifest_strict"])  # class (c) CFP-948
            + len(result["dataflow_stage_propagation"])  # class (e) CFP-948
            + len(result["anti_scope_guard"])
        )
        if file_total > 0:
            file_violations.append((p, result))
            total_findings += file_total

    print(
        f"check-architecture-drift: {files_checked} files 검증 "
        f"(scope: docs/architecture/**/*.md, ADR-078 §결정 1 4 H2 closed-enum + 5 detection class — CFP-948 c+e 활성화)"
    )

    if total_findings == 0:
        print("OK violation 0건 — architecture drift lint PASS")
        sys.exit(0)

    print(f"\nWARN violation {total_findings}건 in {len(file_violations)} files:", file=sys.stderr)
    for fpath, result in file_violations:
        print(f"  {fpath}:", file=sys.stderr)
        for heading, msg in result["h2_closed_enum"]:
            print(f"    [H2-closed-enum] {heading} — {msg}", file=sys.stderr)
        for token, msg in result["module_parity"]:
            print(f"    [module-parity]  {msg}", file=sys.stderr)
        for token, msg in result["contract_parity"]:
            print(f"    [contract-parity] {msg}", file=sys.stderr)
        for token, msg in result["contract_manifest_strict"]:
            print(f"    [contract-manifest-strict] {msg}", file=sys.stderr)
        for token, msg in result["dataflow_stage_propagation"]:
            print(f"    [dataflow-propagation] {msg}", file=sys.stderr)
        for line_num, content, description in result["anti_scope_guard"]:
            print(f"    [anti-scope] L{line_num} ({description}): {content}", file=sys.stderr)

    print(
        "\nADR-078 §결정 1 architecture_doc invariant: 4 H2 closed-enum + 7 module + 7 contract parity + anti-scope guard.",
        file=sys.stderr,
    )
    print("Bypass: `hotfix-bypass:architecture-drift` label (ADR-024 Amendment 3 §결정 6.A).", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"check-architecture-drift: unexpected error: {exc}", file=sys.stderr)
        sys.exit(2)
