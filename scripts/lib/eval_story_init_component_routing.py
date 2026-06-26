#!/usr/bin/env python3
"""
eval_story_init_component_routing.py
CFP-2423 / ADR-069 Amendment 1 (Phase 2) — component routing logic truth-table harness.

목적:
  story-init.yml 의 component_routing step (awk 스크립트, L424-478) 는 정규화(lowercase+trim)
  + mapping 매칭 + count-based 분기(0/1/N≥2) 로직을 구현한다. 본 harness 는 이 로직을
  Python 으로 재구현해 truth-table 로 검증한다 (역할 분리: workflow = shell awk / 본 harness = Python).

  정규화 위치:
  1. REPOS_MAPPING (helper/yq 출력): component\tgithub (raw component name, no norm)
  2. COMPONENT (Issue body): raw value, workflow 에서 normalize
  3. awk script: 매칭 시점에 양쪽 normalize (lowercase+trim)
  4. sort -u dedup: distinct repo 카운트 (같은 repo 중복 제거)

  분기 로직:
  - MATCHING_COUNT == 0: fallback (AC-3)
  - MATCHING_COUNT == 1: route to owner_repo (AC-1)
      └─ AC-5/AC-6 토폴로지 SSOT 대조 (CFP-2423 F-CR-2423-P1-2):
         repo_topology.applicable==true 시 owner_repo ↔ responsibilities[].owner_repo 집합 cross-check.
           일치 → match / 불일치 → mismatch-surfaced(surface only, route 불변) / 미주입·비활성 → skip.
  - MATCHING_COUNT ≥ 2: escalate (AC-4)

scope:
  story-init.yml 의 component_routing step 라우팅 로직 재구현:
  - 정규화(normalize_component): lowercase + trim
  - 매핑 파싱(parse_repos_mapping): component\tgithub format
  - 매칭(evaluate): COMPONENT_NORMALIZED 과 각 mapping 의 normalized component 비교
  - 중복 제거(sort -u): distinct repo 카운트
  - 분기(decide): count 기반 AC-1/3/4 판정

Usage:
  # self-test (8 truth-table case — TC-ROUTE-1~8):
  python3 scripts/lib/eval_story_init_component_routing.py --self-test
  # single fixture (JSON on stdin):
  echo '{"mapping": "data\tmclayer/mctrader-data", "component": "data"}' \
    | python3 scripts/lib/eval_story_init_component_routing.py

exit code: 0 = (self-test PASS) 또는 (단일 평가 정상) / 1 = self-test FAIL 또는 입력 오류.
"""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def normalize_component(comp: str) -> str:
    """Normalize component: lowercase + trim."""
    if not isinstance(comp, str):
        return ""
    return comp.strip().lower()


def parse_repos_mapping(mapping_text: str) -> list[tuple[str, str]]:
    """Parse REPOS_MAPPING (component\tgithub format) into list of (component_raw, github)."""
    if not mapping_text or not isinstance(mapping_text, str):
        return []
    lines = mapping_text.split('\n')
    pairs = []
    for line in lines:
        line = line.strip()
        if not line or '\t' not in line:
            continue
        parts = line.split('\t', 1)
        if len(parts) != 2:
            continue
        component_raw, github = parts
        component_raw = component_raw.strip()
        github = github.strip()
        if component_raw and github:
            pairs.append((component_raw, github))
    return pairs


def parse_topology_owner_repos(owners_text: str) -> list[str]:
    """Parse REPO_TOPOLOGY_OWNER_REPOS (newline-separated owner_repo set) into list.

    Mirrors workflow project_config step output:
      repo_topology.responsibilities[].owner_repo, newline-separated, blank lines stripped.
    """
    if not owners_text or not isinstance(owners_text, str):
        return []
    return [line.strip() for line in owners_text.split('\n') if line.strip()]


def topology_crosscheck(owner_repo: str, applicable: bool, owner_repos: list[str]) -> str:
    """AC-5/AC-6 topology SSOT cross-check (ADR-131 토폴로지 SSOT).

    workflow component_routing step (AC-1 route 직후) 의 대조 분기 1:1 재구현:
      - applicable != true OR owner_repos 빈집합(미주입) → "skip" (AC-6 PASS, 대조 비활성)
      - applicable == true:
          owner_repo ∈ owner_repos → "match"               (AC-5 정합, surface 없음)
          owner_repo ∉ owner_repos → "mismatch-surfaced"   (AC-5 불일치 surface, hard-block 아님)

    검사연극 금지 (ADR-131 §결정4 / ADR-119): 불일치는 surface 만 — 라우팅 decision 은 불변(route 유지).
    """
    if not applicable or not owner_repos:
        return "skip"
    if owner_repo in owner_repos:
        return "match"
    return "mismatch-surfaced"


def evaluate(
    mapping_text: str,
    component: str,
    topology_applicable: bool = False,
    topology_owner_repos_text: str = "",
) -> dict:
    """Evaluate component routing (+ AC-5/AC-6 topology cross-check).

    Args:
      mapping_text: REPOS_MAPPING (component\tgithub per line).
      component: Issue body `### Component` raw value.
      topology_applicable: repo_topology.applicable (AC-5 활성 조건).
      topology_owner_repos_text: repo_topology.responsibilities[].owner_repo (newline-separated).

    Returns:
      {
        "decision": "route" | "fallback" | "escalate",
        "target_repo": str | None,            # AC-1 route case 만
        "matching_repos": list[str],          # distinct repos (sort -u dedup)
        "topology_check": "match" | "mismatch-surfaced" | "skip" | "n/a",
                                              # AC-5/AC-6. route case 외엔 "n/a" (대조 미수행).
        "note": str
      }

    topology_check invariant (검사연극 금지 — ADR-131 §결정4 / ADR-119):
      mismatch-surfaced 여도 decision 은 "route" 불변 (surface only, hard-block 아님).
    """
    # Parse REPOS_MAPPING
    mapping_pairs = parse_repos_mapping(mapping_text)

    # Normalize component input
    component_normalized = normalize_component(component)

    if not component_normalized:
        # Empty or whitespace-only component
        return {
            "decision": "fallback",
            "target_repo": None,
            "matching_repos": [],
            "topology_check": "n/a",
            "note": "empty component after normalization",
        }

    if not mapping_text or not mapping_text.strip():
        # Empty mapping (repos[] absent or backward-compat)
        return {
            "decision": "fallback",
            "target_repo": None,
            "matching_repos": [],
            "topology_check": "n/a",
            "note": "empty repos mapping",
        }

    # Match component against each mapping entry
    # Each entry: (component_raw, github)
    # Normalize component_raw, compare with component_normalized, collect github
    matching_repos_list = []
    for component_raw, github in mapping_pairs:
        component_raw_normalized = normalize_component(component_raw)
        if component_raw_normalized == component_normalized:
            matching_repos_list.append(github)

    # Dedup: sort -u (distinct repos)
    distinct_repos = sorted(set(matching_repos_list))
    matching_count = len(distinct_repos)

    if matching_count == 0:
        # AC-3: no mapping
        return {
            "decision": "fallback",
            "target_repo": None,
            "matching_repos": [],
            "topology_check": "n/a",
            "note": f"no mapping for component '{component}' (normalized='{component_normalized}')",
        }
    elif matching_count == 1:
        # AC-1: 1:1 mapping → owner_repo. AC-5/AC-6 topology cross-check (route 직후).
        owner_repo = distinct_repos[0]
        topo_owner_repos = parse_topology_owner_repos(topology_owner_repos_text)
        topo_check = topology_crosscheck(owner_repo, topology_applicable, topo_owner_repos)
        if topo_check == "match":
            note = f"1:1 mapping: component '{component}' → {owner_repo} (topology match)"
        elif topo_check == "mismatch-surfaced":
            note = (
                f"1:1 mapping: component '{component}' → {owner_repo} "
                f"(AC-5 topology mismatch SURFACED — owner_repo ∉ responsibilities[].owner_repo; "
                f"hard-block 아님, route 유지)"
            )
        else:  # skip
            note = f"1:1 mapping: component '{component}' → {owner_repo} (topology skip, AC-6)"
        return {
            "decision": "route",          # invariant: mismatch 여도 route 불변 (surface only)
            "target_repo": owner_repo,
            "matching_repos": distinct_repos,
            "topology_check": topo_check,
            "note": note,
        }
    else:
        # AC-4: N≥2 mapping (multiple distinct repos)
        return {
            "decision": "escalate",
            "target_repo": None,
            "matching_repos": distinct_repos,
            "topology_check": "n/a",
            "note": f"multi-mapping (AC-4): component '{component}' claimed by {matching_count} repos: {', '.join(distinct_repos)}",
        }


# truth-table case — AC-1~6 + dedup + trim + case-insensitive + topology cross-check.
# 각 case: (id, mapping_text, component, topology_applicable, topology_owner_repos_text,
#           expect_decision, expect_target_repo, expect_topology_check, note)
# 기존 TC-ROUTE-1~8 = topology 미주입 (applicable=False, owners="") → expect topology_check:
#   route case = "skip" (AC-6 degrade), 비-route case = "n/a".
TRUTH_TABLE = [
    # --- AC-1 (1:1 mapping) ---
    (
        "TC-ROUTE-1",
        "data\tmclayer/mctrader-data",
        "data",
        False,
        "",
        "route",
        "mclayer/mctrader-data",
        "skip",
        "AC-1: exact match (topology 미주입 → skip)",
    ),
    (
        "TC-ROUTE-2",
        "Data\tmclayer/mctrader-data",
        "DATA",
        False,
        "",
        "route",
        "mclayer/mctrader-data",
        "skip",
        "AC-1: case-insensitive (raw='Data' + input='DATA' → both normalize to 'data')",
    ),
    # --- AC-3 (no mapping) ---
    (
        "TC-ROUTE-3",
        "data\tmclayer/mctrader-data",
        "nonexistent",
        False,
        "",
        "fallback",
        None,
        "n/a",
        "AC-3: unmapped component",
    ),
    (
        "TC-ROUTE-4",
        "data\tmclayer/mctrader-data",
        "",
        False,
        "",
        "fallback",
        None,
        "n/a",
        "AC-3: empty component",
    ),
    # --- AC-4 (multi-mapping) ---
    (
        "TC-ROUTE-5",
        "risk\trepoA\nrisk\trepoB",
        "risk",
        False,
        "",
        "escalate",
        None,
        "n/a",
        "AC-4: 2 distinct repos (repoA, repoB) — escalate",
    ),
    # --- dedup invariant (same repo claimed twice by same component ≠ escalate) ---
    (
        "TC-ROUTE-6",
        "risk\trepoA\nrisk\trepoA",
        "risk",
        False,
        "",
        "route",
        "repoA",
        "skip",
        "AC-1 dedup: same repo twice (sort -u) → 1 distinct → route NOT escalate",
    ),
    # --- backward-compat: empty repos[] mapping ---
    (
        "TC-ROUTE-7",
        "",
        "anything",
        False,
        "",
        "fallback",
        None,
        "n/a",
        "backward-compat: empty repos mapping (repos[] absent) → fallback",
    ),
    # --- trim invariant ---
    (
        "TC-ROUTE-8",
        "  data  \tmclayer/mctrader-data",
        "  data  ",
        False,
        "",
        "route",
        "mclayer/mctrader-data",
        "skip",
        "trim: both component_raw and input trimmed during normalization",
    ),
    # === AC-5/AC-6 topology SSOT cross-check (CFP-2423 F-CR-2423-P1-2) ===
    # discriminating: 대조 dead-code 였던 버그 재발 시 RED (skip/match/mismatch-surfaced 구별).
    # --- AC-5 일치: 라우팅 owner_repo ∈ responsibilities[].owner_repo 집합 ---
    (
        "TC-ROUTE-9",
        "data\tmclayer/mctrader-data",
        "data",
        True,
        "mclayer/mctrader-data\nmclayer/mctrader-engine",
        "route",
        "mclayer/mctrader-data",
        "match",
        "AC-5 match: applicable=true + owner_repo ∈ topology owner_repos → match (surface 없음)",
    ),
    # --- AC-5 불일치: 라우팅 owner_repo ∉ topology 집합 → surface, decision 은 route 불변 (hard-block 아님) ---
    (
        "TC-ROUTE-10",
        "data\tmclayer/mctrader-data",
        "data",
        True,
        "mclayer/mctrader-engine\nmclayer/mctrader-ui",
        "route",
        "mclayer/mctrader-data",
        "mismatch-surfaced",
        "AC-5 mismatch SURFACE: owner_repo ∉ topology owner_repos → warning surface, decision=route 불변 (검사연극 금지)",
    ),
    # --- AC-6 skip: applicable=false (맵 주입돼도 비활성) → 대조 skip ---
    (
        "TC-ROUTE-11",
        "data\tmclayer/mctrader-data",
        "data",
        False,
        "mclayer/mctrader-engine",
        "route",
        "mclayer/mctrader-data",
        "skip",
        "AC-6 skip: applicable=false → 대조 비활성 (owners 주입돼도 무시, mismatch 발화 0)",
    ),
    # --- AC-6 skip: applicable=true 이나 responsibilities 미주입(빈 owners) → 대조 skip ---
    (
        "TC-ROUTE-12",
        "data\tmclayer/mctrader-data",
        "data",
        True,
        "",
        "route",
        "mclayer/mctrader-data",
        "skip",
        "AC-6 skip: applicable=true + responsibilities 빈집합 → 대조 skip (PASS, 메타불변식 layer 분리)",
    ),
    # --- AC-5 일치 (정규화 무관 — owner_repo 는 exact-match, repo 이름 대소문자 보존) ---
    (
        "TC-ROUTE-13",
        "Risk\tmclayer/mctrader-engine",
        "RISK",
        True,
        "mclayer/mctrader-engine",
        "route",
        "mclayer/mctrader-engine",
        "match",
        "AC-5 match + case-insensitive component routing: 라우팅 후 owner_repo exact-match in topology",
    ),
]


def run_self_test() -> int:
    failures = []
    for (
        case_id,
        mapping,
        component,
        topo_applicable,
        topo_owners,
        expect_decision,
        expect_repo,
        expect_topo_check,
        note,
    ) in TRUTH_TABLE:
        result = evaluate(mapping, component, topo_applicable, topo_owners)
        decision = result["decision"]
        target_repo = result["target_repo"]
        topo_check = result["topology_check"]

        ok = (
            decision == expect_decision
            and target_repo == expect_repo
            and topo_check == expect_topo_check
        )
        status = "PASS" if ok else "FAIL"
        line = (
            f"[{status}] {case_id}: expect_decision={expect_decision} got={decision}, "
            f"expect_repo={expect_repo} got={target_repo}, "
            f"expect_topology={expect_topo_check} got={topo_check} — {note}"
        )
        print(line)
        if not ok:
            failures.append(case_id)

    print(f"\n{len(TRUTH_TABLE) - len(failures)}/{len(TRUTH_TABLE)} truth-table case PASS")
    if failures:
        print(f"FAIL: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


def run_single() -> int:
    """Single evaluation from stdin (JSON)."""
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass
    raw = sys.stdin.read().strip()
    if not raw:
        print("::error::빈 입력 — JSON fixture 또는 --self-test 필요", file=sys.stderr)
        return 1
    try:
        fixture = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"::error::JSON parse 실패: {e}", file=sys.stderr)
        return 1

    mapping = fixture.get("mapping", "")
    component = fixture.get("component", "")
    # AC-5/AC-6 optional topology cross-check inputs (미주입 시 skip 경로)
    topology_applicable = bool(fixture.get("topology_applicable", False))
    topology_owner_repos = fixture.get("topology_owner_repos", "")

    result = evaluate(mapping, component, topology_applicable, topology_owner_repos)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return run_self_test()
    return run_single()


if __name__ == "__main__":
    sys.exit(main())
