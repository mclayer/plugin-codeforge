#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1117-S3 / ADR-091 §결정 5 + §결정 6 — DDD pattern frontmatter mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# === 목적 ===
# ArchitectLane agent file frontmatter 의 DDD governance field 2종 검증:
#   (a) `bounded_context` field presence + value = codeforge-governance (또는 허용 BC enum)
#   (b) `ddd_pattern` field presence + sub-classification enum membership
# ADR-091 §결정 5 의 vocabulary theater 차단 forcing function (INV-5) mechanical wire.
#
# === scope rationale (별 repo cross-plugin lint) ===
# codeforge-design plugin agent file = 별 repo (wrapper = 0 core agent, ADR-009).
# wrapper repo CI 가 design agent file 을 직접 검사 불가 → 본 lint 는 path-parameterized:
#   - design plugin CI 가 `bash <wrapper>/scripts/check-ddd-pattern-frontmatter.sh agents/*.md` 로 호출
#   - 또는 wrapper workflow 가 design repo clone 후 clone 경로 agent file 인자 전달
# 인자 미제공 시 default glob = sibling design plugin clone (`../plugin-codeforge-design/agents/*.md`)
# 시도 (CI 환경에서는 명시 path 인자 권장).
#
# === enum (sub-classification 허용 — S2 비자명 #3 carrier) ===
# ddd_pattern 은 §결정 1 의 3 base role (Authority Pair / Domain Service / Subdomain Specialist)
# 보다 구체적인 sub-classification 을 허용. S2 (#1119) 가 14 agent frontmatter 에 채운
# sub-pattern 6종 + base role 모두 허용 (drift 차단 + 표현력 보존 양립).
#
# === exit code (adr-sunset-criteria.py 패턴 답습 — warning mode 는 workflow continue-on-error 가 보장) ===
#   0 = PASS (violation 0건)
#   1 = violation 감지 (field 누락 / enum mismatch / malformed) — fail signal emit.
#       INV-5 (vocabulary theater 차단) forcing function: 실제 fail signal 을 emit 해야
#       mechanical enforce (단순 nominal 아님). warning tier = workflow `continue-on-error: true`
#       가 PR merge 미차단 보장 (ADR-091 §결정 6 Template lint tier / ADR-058 warning).
#
# === Usage ===
#   python3 scripts/lib/check_ddd_pattern_frontmatter.py [agent_file ...]
#   인자 = agent file path list (미제공 시 default glob)
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

# === field 추출 = top-level line-based 정규식 (전체 YAML 파싱 회피) ===
# 근거: agent frontmatter description 은 멀티라인 + 콜론 (`aggregate_arch.applicable: bool`)
# 빈번 → `yaml.safe_load` 전체 파싱이 깨짐 (mapping values not allowed). 본 lint 는
# `bounded_context` + `ddd_pattern` 2 top-level scalar field 만 필요하므로 line-based
# 정규식 추출 = robust (nested/멀티라인 영역 무시, top-level key 만 매칭).
# top-level key = 들여쓰기 0 (라인 시작 비공백) + `key: value` 형태.
_FIELD_RE_CACHE = {}


def extract_top_level_field(fm_text: str, key: str):
    """frontmatter 본문에서 top-level scalar field value 추출 (없으면 None)."""
    pat = _FIELD_RE_CACHE.get(key)
    if pat is None:
        pat = re.compile(
            rf"^{re.escape(key)}\s*:\s*(.+?)\s*$",
            re.MULTILINE,
        )
        _FIELD_RE_CACHE[key] = pat
    m = pat.search(fm_text)
    if not m:
        return None
    val = m.group(1).strip().strip("\"'`")
    return val

# ADR-091 §결정 5 — bounded_context 허용 enum (codeforge governance BC = ArchitectLane agent default)
BOUNDED_CONTEXT_ENUM = {
    "codeforge-governance",
    "application-bc",        # downstream consumer (mctrader 등) — 별 SSOT
    "shared-kernel",         # inter-plugin contracts 영역
}

# ddd_pattern enum — §결정 1 base role 3종 + S2 sub-classification 6종 (S2 비자명 #3 carrier).
# sub-classification 허용 = 표현력 보존 (false precision 회피, ADR-091 §결정 1 rationale 정합).
DDD_PATTERN_BASE_ROLES = {
    "Authority Pair",
    "Domain Service",
    "Subdomain Specialist",
}
DDD_PATTERN_SUB_CLASSIFICATIONS = {
    # Authority Pair sub-classifications (PL supervisor + chief author)
    "authority-pair-aggregate-root",       # ArchitectPLAgent — supervised authority cluster (Aggregate Root metaphor)
    "authority-pair-chief-author",         # ArchitectAgent — multi-source synthesizer (real Aggregate author)
    # Domain Service sub-classifications (permanent SubAgent + sub-tuple)
    "domain-service",                      # SecurityArch / InfraOpArch / TestContractArch / APIContractArch
    "domain-service-boundary-axis-unified",# ModuleArch (CFP-1126 unified mandate — module + aggregate boundary)
    "domain-service-sub-tuple",            # CodebaseMapper / Refactor / ArchitectAnalyst (4-tuple sub-tuple)
    # Subdomain Specialist sub-classification (CONDITIONAL deputy)
    "subdomain-specialist",                # LiveOps / LiveOrdering / ProductionEvidence (which subdomain under threat)
}
DDD_PATTERN_ENUM = DDD_PATTERN_BASE_ROLES | DDD_PATTERN_SUB_CLASSIFICATIONS


def default_agent_files():
    """인자 미제공 시 sibling design plugin clone agents/ glob 시도."""
    candidates = [
        Path("../plugin-codeforge-design/agents"),
        Path("plugin-codeforge-design/agents"),
        Path("agents"),  # design plugin repo 내부 호출 (cwd = plugin root)
    ]
    for c in candidates:
        if c.is_dir():
            return sorted(str(p) for p in c.glob("*.md"))
    return []


def main():
    paths = sys.argv[1:]
    if not paths:
        paths = default_agent_files()

    if not paths:
        # design plugin agent file 미발견 = scope 부재 (cross-plugin lint 한계) — warning, not fail.
        print(
            "⚠ check-ddd-pattern-frontmatter: ArchitectLane agent file 미발견 "
            "(design plugin clone 부재 — path 인자 명시 또는 design repo clone 후 호출). "
            "scope: codeforge-design plugin agents/*.md (별 repo, ADR-091 §결정 6 cross-plugin lint).",
            file=sys.stderr,
        )
        sys.exit(0)

    violations = []   # field 누락 / enum mismatch (vocabulary theater 차단 INV-5 대상)
    malformed = []    # structural error (frontmatter 부재 / YAML 파싱 실패)
    files_checked = 0

    for p in paths:
        path = Path(p)
        if not path.exists():
            # unexpanded glob literal (shell nullglob off 시 `dir/*.md` 그대로 전달) 또는
            # clone 부재 path = graceful skip (cross-plugin lint 환경 — malformed 아님).
            # design plugin clone 실패 시 workflow 가 step 자체를 skip 하므로, lint 까지
            # 도달한 부재 path 는 환경 noise → warning 으로 격하 (PR merge 미차단).
            if "*" in p or "?" in p:
                continue  # unexpanded glob — silent skip
            print(f"⚠ check-ddd-pattern-frontmatter: {p} file 부재 — skip (cross-plugin clone 부재 가능)", file=sys.stderr)
            continue
        if not path.name.endswith(".md"):
            continue
        text = path.read_text(encoding="utf-8")
        files_checked += 1

        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not fm_match:
            malformed.append(f"{p}: frontmatter 부재")
            continue
        fm_text = fm_match.group(1)

        # (a) bounded_context field presence + enum (line-based 추출 — 전체 YAML 파싱 회피)
        bc = extract_top_level_field(fm_text, "bounded_context")
        if bc is None:
            violations.append(
                f"{p}: frontmatter `bounded_context` field 미선언 "
                f"(ADR-091 §결정 5 — 허용 enum: {sorted(BOUNDED_CONTEXT_ENUM)})"
            )
        elif bc not in BOUNDED_CONTEXT_ENUM:
            violations.append(
                f"{p}: `bounded_context: {bc!r}` enum membership 위반 "
                f"(ADR-091 §결정 5 — 허용: {sorted(BOUNDED_CONTEXT_ENUM)})"
            )

        # (b) ddd_pattern field presence + enum (sub-classification 허용)
        pattern = extract_top_level_field(fm_text, "ddd_pattern")
        if pattern is None:
            violations.append(
                f"{p}: frontmatter `ddd_pattern` field 미선언 "
                f"(ADR-091 §결정 5 — base role {sorted(DDD_PATTERN_BASE_ROLES)} "
                f"또는 sub-classification {sorted(DDD_PATTERN_SUB_CLASSIFICATIONS)})"
            )
        elif pattern not in DDD_PATTERN_ENUM:
            violations.append(
                f"{p}: `ddd_pattern: {pattern!r}` enum membership 위반 "
                f"(ADR-091 §결정 1 base role 3종 + S2 sub-classification 6종 허용). "
                f"허용 enum: {sorted(DDD_PATTERN_ENUM)}"
            )

    print(f"check-ddd-pattern-frontmatter: {files_checked} ArchitectLane agent file 검증")

    all_issues = malformed + violations
    if all_issues:
        if malformed:
            print(f"\n✗ malformed {len(malformed)}건 (structural error):", file=sys.stderr)
            for m in malformed:
                print(f"  - {m}", file=sys.stderr)
        if violations:
            print(f"\n⚠ violation {len(violations)}건 (DDD pattern frontmatter — INV-5 vocabulary theater 차단 대상):", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
        # warning mode = workflow `continue-on-error: true` 가 PR merge 미차단 보장.
        # 본 lint 는 fail signal (exit 1) 을 emit 해야 mechanical enforce (INV-5 정합).
        sys.exit(1)

    if files_checked == 0:
        # 모든 인자가 부재 path (cross-plugin clone 부재) — graceful skip (PR merge 미차단).
        print("⚠ check-ddd-pattern-frontmatter: 검증 대상 agent file 0건 — skip (cross-plugin clone 부재 가능)", file=sys.stderr)
        sys.exit(0)

    print("✓ violation 0건 — DDD pattern frontmatter mechanical check PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
