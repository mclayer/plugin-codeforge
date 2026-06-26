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


def evaluate(mapping_text: str, component: str) -> dict:
    """Evaluate component routing.

    Returns:
      {
        "decision": "route" | "fallback" | "escalate",
        "target_repo": str | None,       # AC-1 route case 만
        "matching_repos": list[str],     # distinct repos (sort -u dedup)
        "note": str
      }
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
            "note": "empty component after normalization",
        }

    if not mapping_text or not mapping_text.strip():
        # Empty mapping (repos[] absent or backward-compat)
        return {
            "decision": "fallback",
            "target_repo": None,
            "matching_repos": [],
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
            "note": f"no mapping for component '{component}' (normalized='{component_normalized}')",
        }
    elif matching_count == 1:
        # AC-1: 1:1 mapping
        return {
            "decision": "route",
            "target_repo": distinct_repos[0],
            "matching_repos": distinct_repos,
            "note": f"1:1 mapping: component '{component}' → {distinct_repos[0]}",
        }
    else:
        # AC-4: N≥2 mapping (multiple distinct repos)
        return {
            "decision": "escalate",
            "target_repo": None,
            "matching_repos": distinct_repos,
            "note": f"multi-mapping (AC-4): component '{component}' claimed by {matching_count} repos: {', '.join(distinct_repos)}",
        }


# 8 truth-table case — AC-1~4 + dedup + trim + case-insensitive
# 각 case: (id, mapping_text, component, expect_decision, expect_target_repo, note)
TRUTH_TABLE = [
    # --- AC-1 (1:1 mapping) ---
    (
        "TC-ROUTE-1",
        "data\tmclayer/mctrader-data",
        "data",
        "route",
        "mclayer/mctrader-data",
        "AC-1: exact match",
    ),
    (
        "TC-ROUTE-2",
        "Data\tmclayer/mctrader-data",
        "DATA",
        "route",
        "mclayer/mctrader-data",
        "AC-1: case-insensitive (raw='Data' + input='DATA' → both normalize to 'data')",
    ),
    # --- AC-3 (no mapping) ---
    (
        "TC-ROUTE-3",
        "data\tmclayer/mctrader-data",
        "nonexistent",
        "fallback",
        None,
        "AC-3: unmapped component",
    ),
    (
        "TC-ROUTE-4",
        "data\tmclayer/mctrader-data",
        "",
        "fallback",
        None,
        "AC-3: empty component",
    ),
    # --- AC-4 (multi-mapping) ---
    (
        "TC-ROUTE-5",
        "risk\trepoA\nrisk\trepoB",
        "risk",
        "escalate",
        None,
        "AC-4: 2 distinct repos (repoA, repoB) — escalate",
    ),
    # --- dedup invariant (same repo claimed twice by same component ≠ escalate) ---
    (
        "TC-ROUTE-6",
        "risk\trepoA\nrisk\trepoA",
        "risk",
        "route",
        "repoA",
        "AC-1 dedup: same repo twice (sort -u) → 1 distinct → route NOT escalate",
    ),
    # --- backward-compat: empty repos[] mapping ---
    (
        "TC-ROUTE-7",
        "",
        "anything",
        "fallback",
        None,
        "backward-compat: empty repos mapping (repos[] absent) → fallback",
    ),
    # --- trim invariant ---
    (
        "TC-ROUTE-8",
        "  data  \tmclayer/mctrader-data",
        "  data  ",
        "route",
        "mclayer/mctrader-data",
        "trim: both component_raw and input trimmed during normalization",
    ),
]


def run_self_test() -> int:
    failures = []
    for case_id, mapping, component, expect_decision, expect_repo, note in TRUTH_TABLE:
        result = evaluate(mapping, component)
        decision = result["decision"]
        target_repo = result["target_repo"]

        status = "PASS" if (decision == expect_decision and target_repo == expect_repo) else "FAIL"
        line = (
            f"[{status}] {case_id}: expect_decision={expect_decision} got={decision}, "
            f"expect_repo={expect_repo} got={target_repo} — {note}"
        )
        print(line)
        if decision != expect_decision or target_repo != expect_repo:
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

    result = evaluate(mapping, component)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return run_self_test()
    return run_single()


if __name__ == "__main__":
    sys.exit(main())
