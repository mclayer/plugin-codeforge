#!/usr/bin/env bash
# CFP-449 / ADR-060 / ADR-064 — Decision principle forbid-list vocabulary mechanical lint (warning mode)
#
# 검증 대상 (ADR-064 §결정 2 verbatim):
#   8 forbid-list 어휘 detection in 5 scope 영역 (ADR / change-plans / CLAUDE.md / playbook / templates)
#
# Forbid-list dictionary v1.0 (ADR-064 §결정 2 SSOT — 8 어휘 — 본문 내 dictionary 인용 영역 self-exempt):
#   [본 영역은 dictionary 정의 영역 = exempt 처리됨, 본 file path 자체가 EXEMPT_PATHS 등록]
#   임시 / 단계적 / 일단 / 우선 / 잠정 / 가벼운 / minimal viable / quick win
#
# Exempt 영역 (false positive 회피):
#   - markdown blockquote (line 이 `>` prefix 로 시작)
#   - fenced code block (` ``` ` 사이 영역, line-by-line state machine)
#   - dictionary 본문 자체 영역 (ADR-064 §결정 2 표 / registry yaml description / 본 script 자체 / bats fixture self)
#   - 사용자 발화 verbatim invariant 영역 (Story §1) — Story file 은 internal-docs repo 영역이므로 wrapper repo lint scope 외 자연 처리
#
# Exit code:
#   - 0: violation 0건 (PASS, warning mode 또는 future enforce mode)
#   - 1: violation 1건 이상 (warning mode continue-on-error / future enforce PR block)
#   - 2: meta-error (pyyaml/python3 미설치 등 환경 결격) — ADR-060 Amendment 2 §결정 15 정합
#
# 인자:
#   $@ : 검증 대상 file path list (없으면 5 scope glob)
#
# 명령 라인:
#   $ bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-064-decision-principle-mandate.md
#   $ bash scripts/check-decision-principle-vocabulary.sh    # all 5 scope
#
# carrier: ADR-060 §결정 5 (warning mode), ADR-064 §결정 2 (dictionary SSOT)
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null 2>&1; then
    echo "check-decision-principle-vocabulary: python3 미설치 (meta-error)" >&2
    exit 2
fi

python3 - "$@" <<'PY'
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
# 본 list 자체가 dictionary 영역 — 본 script path 는 EXEMPT_PATHS 등록, self-detection 회피.
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
    "docs/change-plans/**/*.md",
    "CLAUDE.md",
    "docs/orchestrator-playbook.md",
    "templates/**/*.md",
    "templates/**/*.yml",
    "templates/**/*.yaml",
    "templates/**/*.sh",
]

# ─── Exempt 영역 ───
# (1) Dictionary SSOT 본문 영역 — verbatim mirror file path set
# (2) Registry yaml description 영역 (entry 본문이 8 어휘 verbatim 포함)
# (3) 본 lint script self + bats fixture self (test code 가 fixture 로 forbid 어휘 포함)
EXEMPT_PATHS = {
    "docs/adr/ADR-RESERVATION.md",
    "docs/adr/ADR-064-decision-principle-mandate.md",
    "docs/evidence-checks-registry.yaml",
    "scripts/check-decision-principle-vocabulary.sh",
    "tests/scripts/test-check-decision-principle-vocabulary.bats",
}


def normalize_path(p):
    """Path separator OS independence (Windows backslash → forward slash)."""
    return str(p).replace("\\", "/")


def collect_scope_files():
    """5 scope glob 으로 wrapper repo file 수집. EXEMPT_PATHS filter."""
    out = []
    for pattern in SCOPE_GLOBS:
        for path in Path(".").glob(pattern):
            if not path.is_file():
                continue
            norm = normalize_path(path)
            if norm in EXEMPT_PATHS:
                continue
            out.append(norm)
    return sorted(set(out))


def in_scope(p):
    """argv path 가 5 scope 안에 있는지 검사. False = scope 외 → exit 0 처리."""
    norm = normalize_path(p)
    path = Path(norm)
    # scope glob match
    for pattern in SCOPE_GLOBS:
        if path.match(pattern):
            return True
        # Path.match 가 ** 처리 한계 — 보조 prefix match
        prefix = pattern.split("**", 1)[0].rstrip("/")
        if prefix and norm.startswith(prefix + "/"):
            # suffix 확장자 정합
            suffixes = pattern.rsplit(".", 1)
            if len(suffixes) == 2 and norm.endswith("." + suffixes[1]):
                return True
    # exact match (CLAUDE.md / playbook)
    return norm in {"CLAUDE.md", "docs/orchestrator-playbook.md"}


def scan_file(p):
    """File 본문을 line-by-line state machine 으로 scan.
    blockquote (`>` prefix) + fenced code block (``` 사이) 영역 = exempt.
    Returns list of (line_num, line_content, matched_word) tuples.
    """
    findings = []
    try:
        text = Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        # caller 에서 처리
        raise
    in_fence = False
    fence_marker = None
    for line_num, raw_line in enumerate(text.splitlines(), start=1):
        # Fenced code block detection (``` 또는 ~~~)
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
        # Blockquote detection (line 이 `>` prefix)
        if stripped.startswith(">"):
            continue
        # Dictionary detection
        line_lower = raw_line.lower()
        for word in FORBID_DICTIONARY:
            if word.lower() in line_lower:
                findings.append((line_num, raw_line.rstrip(), word))
    return findings


def main(argv):
    paths = argv[1:]
    if not paths:
        paths = collect_scope_files()
    else:
        # argv mode — scope 외 file 은 skip (exit 0 처리)
        filtered = []
        for p in paths:
            norm = normalize_path(p)
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
            # missing path — soft warn (exit 0 처리)
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


try:
    main(sys.argv)
except SystemExit:
    raise
except Exception as exc:
    print(f"check-decision-principle-vocabulary: unexpected error: {exc}", file=sys.stderr)
    sys.exit(2)
PY
