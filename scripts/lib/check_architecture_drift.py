#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-923 / ADR-078 P-S4 mechanism — architecture-drift mechanical lint (warning mode)
# ADR-061 §결정 1 — heredoc Python 외부 .py split (thin wrapper: scripts/check-architecture-drift.sh)
#
# Lint scope: docs/architecture/**/*.md  (architecture_doc kind)
# Detection class 3 active (Story §5.2):
#   (a) module enumeration parity: wrapper + 6 lane plugin name in `## 모듈` section text body
#   (b) inter-plugin-contracts enumeration parity: MANIFEST.yaml 7 kind:contract in `## 인터페이스 계약`
#   (d) anti-scope guard violation detection: class/def/import/signature line patterns
#       + H2 외 H2 (4 H2 closed-enum 외 H2 heading) detected anywhere in doc body
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
            + len(result["anti_scope_guard"])
        )
        if file_total > 0:
            file_violations.append((p, result))
            total_findings += file_total

    print(
        f"check-architecture-drift: {files_checked} files 검증 "
        f"(scope: docs/architecture/**/*.md, ADR-078 §결정 1 4 H2 closed-enum + 3 detection class)"
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
