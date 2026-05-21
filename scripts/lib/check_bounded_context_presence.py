#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1117-S3 / ADR-091 §결정 5 + §결정 6 — Bounded Context presence mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# === 목적 ===
# document-level bounded_context 명시 presence 검증. ADR-091 §결정 4 (Published Language 분리)
# + §결정 5 (Bounded Context governance) 의 vocabulary theater 차단 forcing function (INV-5):
# DDD 영역을 touching 하는 governance document (Story §ubiquitous_language / DDD-touching ADR /
# Change Plan) 가 어느 BC 안에서 작동하는지 explicit declare 의무.
#
# === scope (ddd-pattern-frontmatter-check 와 disjoint axis) ===
#   - ddd-pattern-frontmatter-check = design plugin agent file frontmatter 2 field (별 repo, cross-plugin)
#   - 본 bounded-context-presence-check = wrapper-local document 안 bounded_context declaration:
#       (a) Story file §ubiquitous_language block 안 `bounded_context:` (DDD 영역 touching 시)
#       (b) DDD-touching ADR / Change Plan 안 bounded_context 명시 (heuristic — DDD term 사용 시)
#   wrapper-local 자족 — 별 repo clone 의존 0.
#
# === DDD touching 판정 (heuristic) ===
# document 본문 안 DDD term (Bounded Context / Aggregate / Domain Service / Ubiquitous Language /
# Anti-Corruption Layer / Open Host Service 등 glossary anchor 어휘) 사용 시 = DDD touching.
# touching 시 bounded_context declaration presence 의무. 비-touching = 면제 (false positive 회피).
#
# === bounded_context 허용 enum ===
#   codeforge-governance | application-bc | shared-kernel (ADR-091 §결정 4/§결정 5)
#
# === exit code (adr-sunset-criteria.py 패턴 답습) ===
#   0 = PASS (violation 0건)
#   1 = violation 감지 (DDD touching 인데 bounded_context declaration 부재) — fail signal.
#       warning mode = workflow `continue-on-error: true` 가 PR merge 미차단 보장.
#
# === Usage ===
#   python3 scripts/lib/check_bounded_context_presence.py [file ...]
#   인자 = 검사 대상 file path list (미제공 시 default = docs/stories/*.md + docs/change-plans/*.md
#          + docs/adr/ADR-*.md glob)
import sys
import re
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BOUNDED_CONTEXT_ENUM = {
    "codeforge-governance",
    "application-bc",
    "shared-kernel",
}

# DDD term anchor (glossary SSOT 어휘) — document 본문 안 사용 시 DDD touching 판정.
# anti-pattern term (Big Ball of Mud 등) 은 DDD touching 판정에서 제외 (after-the-fact 분석 허용).
DDD_TERM_ANCHORS = [
    "Bounded Context",
    "Ubiquitous Language",
    "Published Language",
    "Anti-Corruption Layer",
    "Open Host Service",
    "Aggregate Root",
    "Domain Service",
    "Subdomain Specialist",
    "Strategic Design",
    "Tactical Design",
    "Shared Kernel",
    "Context Map",
]

# bounded_context declaration 정규식 — yaml block / inline / prose 모두 포착.
# 예: `bounded_context: codeforge-governance` / `bounded_context = codeforge-governance`
BC_DECLARATION_RE = re.compile(
    r"bounded[_\s-]?context\s*[:=]\s*[`\"']?([A-Za-z][\w-]*)",
    re.IGNORECASE,
)

# ADR-091 자체 + glossary SSOT + DDD concept domain-knowledge = governance vocabulary SSOT file,
# bounded_context declaration 의무 면제 (BC 정의 file 자체 — meta level).
# ADR-RESERVATION.md = ADR governance 레지스트리 (real ADR 아님 — ADR title 인용 시 anchor false
# positive). adr-sunset-criteria.py EXEMPT_PATHS 정합.
EXEMPT_BASENAMES = {
    "ADR-091-architectlane-ddd-vocabulary-governance.md",
    "ADR-RESERVATION.md",
    "glossary.md",
}
EXEMPT_PATH_SUBSTRINGS = (
    "docs/domain-knowledge/concept/",  # bounded-context.md / ubiquitous-language.md 등 BC 정의 file
)


def default_files():
    out = []
    for pattern_dir, glob in (
        ("docs/stories", "*.md"),
        ("docs/change-plans", "*.md"),
        ("docs/adr", "ADR-*.md"),
    ):
        d = Path(pattern_dir)
        if d.is_dir():
            out.extend(sorted(str(p) for p in d.glob(glob)))
    return out


def is_exempt(path: Path) -> bool:
    if path.name in EXEMPT_BASENAMES:
        return True
    posix = path.as_posix()
    return any(sub in posix for sub in EXEMPT_PATH_SUBSTRINGS)


def main():
    paths = sys.argv[1:]
    if not paths:
        paths = default_files()

    if not paths:
        print(
            "⚠ check-bounded-context-presence: 검사 대상 file 미발견 "
            "(docs/stories / docs/change-plans / docs/adr glob 비어있음) — skip",
            file=sys.stderr,
        )
        sys.exit(0)

    violations = []
    files_checked = 0
    files_ddd_touching = 0

    for p in paths:
        path = Path(p)
        if not path.exists():
            # file 부재 = 검사 대상 외 (warning, not fail — git diff 인자 환경 정합)
            continue
        if not path.name.endswith(".md"):
            continue
        if is_exempt(path):
            continue
        text = path.read_text(encoding="utf-8")
        files_checked += 1

        # DDD touching 판정 — DDD term anchor 1+ 사용 시
        touching = any(anchor in text for anchor in DDD_TERM_ANCHORS)
        if not touching:
            continue
        files_ddd_touching += 1

        # bounded_context declaration presence
        if not BC_DECLARATION_RE.search(text):
            violations.append(
                f"{p}: DDD term touching (글로서리 anchor 사용) 인데 "
                f"`bounded_context:` declaration 부재 (ADR-091 §결정 5 — 허용 enum: "
                f"{sorted(BOUNDED_CONTEXT_ENUM)}). Story = §ubiquitous_language block / "
                f"ADR·Change Plan = 본문 bounded_context 명시 의무."
            )
        else:
            # declaration 존재 시 enum membership 검증
            for m in BC_DECLARATION_RE.finditer(text):
                bc = m.group(1)
                if bc not in BOUNDED_CONTEXT_ENUM:
                    violations.append(
                        f"{p}: `bounded_context: {bc!r}` enum membership 위반 "
                        f"(ADR-091 §결정 5 — 허용: {sorted(BOUNDED_CONTEXT_ENUM)})"
                    )
                    break  # 1 file 당 1 violation row (noise 회피)

    print(
        f"check-bounded-context-presence: {files_checked} file 검증 "
        f"({files_ddd_touching} DDD touching)"
    )

    if violations:
        print(f"\n⚠ violation {len(violations)}건 (Bounded Context presence — INV-5 vocabulary theater 차단 대상):", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        # warning mode = workflow continue-on-error 가 PR merge 미차단 보장.
        sys.exit(1)

    print("✓ violation 0건 — Bounded Context presence mechanical check PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
