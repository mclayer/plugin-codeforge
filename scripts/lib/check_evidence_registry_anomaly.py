#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-442 / ADR-060 Amendment 11 §결정 25 — evidence-registry inventory anomaly lint
# CFP-455 prior art mirror (scripts/lib/check_evidence_registry.py) + ADR-061 §결정 1 정합
#
# 검증 대상 (Change Plan §3 + ADR-060 Amendment 11 §결정 25 verbatim):
#   sub-check 1: docs/evidence-checks-registry.yaml entries[] ↔
#                ADR-060 §결정 13 표 Group A 18 entry 1:1 inventory parity.
#                status=Retired entry skip (EC-6 정합). marketplace-sync retired 예외.
#   sub-check 2: scripts/check-*.sh + .github/workflows/*.yml +
#                templates/github-workflows/*.yml 4-criteria AND static analysis
#                후보 식별 + registry 미등록 감지.
#                4-criteria: (a) detect_command / (b) workflow trigger / (c) owner_adr ADR-NNN /
#                            (d) tier signal (continue-on-error)
#                Group C prefix 제외 + ALLOWLIST 4-path self-exempt.
#
# ALLOWLIST 4-path — 2-purpose serving (ADR-068 I-3 guard placement intent 정합):
#   purpose (a) candidate exclude (3 paths):
#     scripts/check-evidence-registry-anomaly.sh
#     templates/github-workflows/evidence-registry-anomaly-check.yml
#     .github/workflows/evidence-registry-anomaly-check.yml
#   purpose (b) start-up assertion (4 paths, 위 3 + Python helper 본체):
#     scripts/lib/check_evidence_registry_anomaly.py
#
# Exit code 3-tier (Amendment 2 §결정 15 정합):
#   exit 0 = PASS (sub-check 1 mismatch 0 AND sub-check 2 candidate 0)
#   exit 1 = anomaly DETECTED (sub-check 1 OR sub-check 2 violation 1+)
#   exit 2 = META-ERROR — 4 분기:
#     (a) pyyaml 미설치 / Python lib import 실패
#     (b) registry yaml 파싱 실패 (yaml.YAMLError) — file:line:col 메시지
#     (c) ADR-060 §결정 13 표 parse 실패 — heading-mismatch / table-row-malformed / table-missing
#     (d) ALLOWLIST 4-path 부재 (EC-9 drift) — ALLOWLIST file 부재 메시지
#
# 인자:
#   sys.argv[1:] 없으면 default paths (docs/evidence-checks-registry.yaml 등) 사용
#
# 호출 패턴 (thin bash wrapper 경유):
#   $ bash scripts/check-evidence-registry-anomaly.sh
#   $ bash scripts/check-evidence-registry-anomaly.sh docs/evidence-checks-registry.yaml
#   $ bash scripts/check-evidence-registry-anomaly.sh tests/scripts/.../fixtures/01-positive-current-state.yaml
#
# carrier: ADR-060 Amendment 11 §결정 25 / CFP-442 Phase 2
import sys
import re
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제 (CFP-455 prior art)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Exit code 3-tier (Amendment 2 §결정 15 정합)
EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 1
EXIT_META_ERROR = 2

# pyyaml 미설치 = meta-error (exit 2)
try:
    import yaml
except ImportError:
    print("META-ERROR: pyyaml 미설치 — `python3 -m pip install --user pyyaml`", file=sys.stderr)
    sys.exit(EXIT_META_ERROR)

# ──────────────────────────────────────────────────────────────────────────────
# ALLOWLIST 4-path hardcode — 2-purpose serving
# (a) candidate exclude: 3 paths (scripts/.sh + 2 workflow .yml) — collect_*_candidates() exclude
# (b) start-up assertion: 4 paths 전체 — assert_allowlist_files() 에서 검증 의무
# ──────────────────────────────────────────────────────────────────────────────
ALLOWLIST_4_PATH = [
    "scripts/check-evidence-registry-anomaly.sh",
    "scripts/lib/check_evidence_registry_anomaly.py",
    "templates/github-workflows/evidence-registry-anomaly-check.yml",
    ".github/workflows/evidence-registry-anomaly-check.yml",
]

# candidate exclude 용 3-path subset (scripts/lib/*.py = sub-check 2 glob scripts/check-*.sh 외)
ALLOWLIST_CANDIDATE_EXCLUDE = {
    "scripts/check-evidence-registry-anomaly.sh",
    "templates/github-workflows/evidence-registry-anomaly-check.yml",
    ".github/workflows/evidence-registry-anomaly-check.yml",
}

# Group C prefix filter — 4-criteria 미충족 ad-hoc utility (ADR-060 Amendment 11 §결정 25 SSOT)
GROUP_C_PREFIXES = [
    "bootstrap-",
    "test-",
    "audit-trail-",
    "migrate-",
    "post-merge-",
    "sync-",
    "helper-",
]

# Default paths
DEFAULT_REGISTRY = "docs/evidence-checks-registry.yaml"
DEFAULT_ADR_060 = "docs/adr/ADR-060-evidence-enforceable-promotion-framework.md"
DEFAULT_SCRIPTS_DIR = Path("scripts")
DEFAULT_WORKFLOW_DIRS = [
    Path(".github/workflows"),
    Path("templates/github-workflows"),
]

# ADR-060 §결정 13 표 inventory parse anchor — bold heading 탐색 (frontmatter 영역 제외)
# 본문 안 **그룹 A — 18 entry SSOT** 패턴 매칭 (frontmatter YAML 안 inline text 와 구분)
GROUP_A_HEADING_RE = re.compile(r"\*\*그룹\s*A.*18\s*entry", re.IGNORECASE)
# table row pattern: | N | `name` | ...  (backtick-quoted name in 2nd column)
TABLE_NAME_RE = re.compile(r"^\|\s*(?:~~)?\s*\d+\s*(?:~~)?\s*\|\s*(?:~~)?`([^`]+)`(?:~~)?")

# retired entry names — sub-check 1 에서 skip 허용 (EC-6 정합)
RETIRED_NAMES = {"marketplace-sync"}

# ADR-NNN regex (owner_adr / carrier_adr cross-ref 용)
ADR_REF_RE = re.compile(r"\bADR-\d+\b")

# owner_adr 포함 script header / workflow comment 매칭 regex
OWNER_ADR_IN_FILE_RE = re.compile(r"ADR-\d+")

# continue-on-error tier signal regex (sub-check 2 criterion d)
TIER_SIGNAL_RE = re.compile(r"continue-on-error\s*:", re.IGNORECASE)

# detect_command signal: scripts/check-*.sh 참조 or "detect_command" 키워드 등
DETECT_COMMAND_RE = re.compile(r"detect_command|check-\w+\.sh|scripts/check")


def assert_allowlist_files() -> None:
    """Start-up time assertion — ALLOWLIST 4-path 전체 존재 확인 (purpose b).
    1+ 부재 시 exit 2 META-ERROR (EC-9 drift detection forcing function).
    """
    for rel_path in ALLOWLIST_4_PATH:
        p = Path(rel_path)
        if not p.exists():
            print(
                f"META-ERROR: ALLOWLIST file 부재 — {rel_path}",
                file=sys.stderr,
            )
            sys.exit(EXIT_META_ERROR)


def load_registry(path: Path) -> dict:
    """YAML safe_load + META-ERROR catch (EC-7: yaml.YAMLError → exit 2)."""
    if not path.exists():
        print(f"META-ERROR: registry yaml file 부재 — {path}", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        # file:line:col 메시지 (Amendment 11 §결정 25 SSOT)
        if hasattr(e, "problem_mark") and e.problem_mark is not None:
            m = e.problem_mark
            loc = f"{path}:{m.line + 1}:{m.column + 1}"
        else:
            loc = str(path)
        print(
            f"META-ERROR: registry yaml parse failed — {loc} {e}",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)
    except OSError as e:
        print(f"META-ERROR: registry yaml read 실패 ({e})", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)
    if not isinstance(data, dict):
        print(
            f"META-ERROR: registry yaml root 가 mapping 아님 (type={type(data).__name__})",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)
    return data


def parse_adr060_inventory_table(adr_path: Path) -> list:
    """ADR-060 §결정 13 표 Group A 18 entry name 추출.

    3 분기 META-ERROR (EC-8):
      - heading-mismatch: 그룹 A 18 entry heading 미발견
      - table-missing: heading 발견 후 table row 0건
      - table-row-malformed: backtick-quoted name 추출 실패
    Returns list[str] — entry name list.
    """
    if not adr_path.exists():
        print(
            f"META-ERROR: ADR-060 §결정 13 inventory table unparseable"
            f" — heading-mismatch at {adr_path} (file 부재)",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)

    try:
        lines = adr_path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print(
            f"META-ERROR: ADR-060 §결정 13 inventory table unparseable"
            f" — heading-mismatch at {adr_path} ({e})",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)

    # 1) heading 탐색
    heading_idx = None
    for i, line in enumerate(lines):
        if GROUP_A_HEADING_RE.search(line):
            heading_idx = i
            break

    if heading_idx is None:
        print(
            f"META-ERROR: ADR-060 §결정 13 inventory table unparseable"
            f" — heading-mismatch at {adr_path}:0",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)

    # 2) table row 추출 (heading 이후 첫 번째 빈 줄 또는 non-table 줄까지)
    names = []
    in_table = False
    for line in lines[heading_idx + 1:]:
        stripped = line.strip()
        if not stripped:
            if in_table:
                break
            continue
        if stripped.startswith("|"):
            in_table = True
            m = TABLE_NAME_RE.match(stripped)
            if m:
                names.append(m.group(1))
        else:
            if in_table:
                break

    if not names:
        print(
            f"META-ERROR: ADR-060 §결정 13 inventory table unparseable"
            f" — table-missing at {adr_path}:{heading_idx + 1}",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)

    return names


def collect_script_candidates(scripts_dir: Path) -> list:
    """scripts/check-*.sh glob — Group C prefix filter — ALLOWLIST exclude.

    ALLOWLIST purpose (a): candidate exclude 3 paths 중 scripts/ 1 path 적용.
    scripts/lib/*.py = sub-check 2 glob 외 — candidate 후보 아님 (ALLOWLIST purpose b 만 적용).
    """
    candidates = []
    if not scripts_dir.exists():
        return candidates
    for p in sorted(scripts_dir.glob("check-*.sh")):
        rel = str(p).replace("\\", "/")
        # ALLOWLIST purpose (a) exclude
        if rel in ALLOWLIST_CANDIDATE_EXCLUDE:
            continue
        # Group C prefix filter
        stem = p.stem  # check-<name>
        name_part = stem[len("check-"):]  # strip leading "check-"
        if any(name_part.startswith(pfx) for pfx in GROUP_C_PREFIXES):
            continue
        candidates.append(p)
    return candidates


def collect_workflow_candidates(workflow_dirs: list) -> list:
    """*.github/workflows/*.yml + templates/github-workflows/*.yml glob — ALLOWLIST exclude."""
    candidates = []
    for d in workflow_dirs:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.yml")):
            rel = str(p).replace("\\", "/")
            if rel in ALLOWLIST_CANDIDATE_EXCLUDE:
                continue
            candidates.append(p)
    return candidates


def score_candidate(file_path: Path, workflow_dirs: list) -> bool:
    """4-criteria AND static analysis (deterministic, LLM judgment 미사용).

    (a) detect_command signal (script 본문 안 detect_command 키워드 OR scripts/check-*.sh 참조)
    (b) workflow GitHub Actions trigger 존재 (on: 또는 script 쪽에서 paired workflow 존재)
    (c) owner_adr 포함 (ADR-NNN regex script header OR workflow comment 매칭)
    (d) tier signal: continue-on-error field 추출

    script 파일: (a)(c)(d) 검사 + (b) paired workflow 존재 여부 (stem name → workflow 탐색)
    workflow 파일: (b)(c)(d) 검사 + (a) detect_command 키워드 or script 참조
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    is_script = file_path.suffix == ".sh"
    is_workflow = file_path.suffix == ".yml"

    # (c) owner_adr: ADR-NNN pattern in file
    crit_c = bool(OWNER_ADR_IN_FILE_RE.search(text))

    # (d) tier signal: continue-on-error 키워드
    crit_d = bool(TIER_SIGNAL_RE.search(text))

    if is_script:
        # (a) detect_command signal: script 자체가 check-*.sh 이면 참 (이름 이미 필터됨)
        crit_a = True  # glob "check-*.sh" 자체가 detect_command signal
        # (b) paired workflow 존재 — stem 에서 workflow 이름 파생 탐색
        script_stem = file_path.stem  # e.g. check-adr-sunset-criteria
        # workflow name candidates: <script_stem>*.yml or <script_stem>-check.yml 등
        crit_b = False
        for d in workflow_dirs:
            if not d.exists():
                continue
            # stem match: workflow file 이름이 script stem 의 substring 포함 시 paired
            for wf in d.glob("*.yml"):
                wf_stem = wf.stem
                # check-foo-bar → foo-bar, workflow: foo-bar-check.yml / foo-bar.yml
                script_core = script_stem[len("check-"):] if script_stem.startswith("check-") else script_stem
                if script_core in wf_stem or wf_stem in script_core:
                    crit_b = True
                    break
            if crit_b:
                break
        return crit_a and crit_b and crit_c and crit_d

    if is_workflow:
        # (a) detect_command: workflow 안 detect_command 키워드 OR scripts/check 참조
        crit_a = bool(DETECT_COMMAND_RE.search(text))
        # (b) workflow 자체가 GitHub Actions trigger (on: field) 보유
        crit_b = bool(re.search(r"^on\s*:", text, re.MULTILINE))
        return crit_a and crit_b and crit_c and crit_d

    return False


def check_subcheck1(
    registry_entries: list,
    inventory_names: list,
) -> list:
    """sub-check 1: registry ↔ ADR-060 §결정 13 표 Group A 18 entry 1:1 정합.

    retired entry (status=Retired OR name in RETIRED_NAMES) skip (EC-6).
    Returns violation list (message strings).
    """
    violations = []

    # registry 에서 Active/non-retired entry name set 추출
    registry_active = set()
    for entry in registry_entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        status = entry.get("status", "")
        if not name:
            continue
        # status=Retired skip
        if isinstance(status, str) and status.lower() == "retired":
            continue
        if name in RETIRED_NAMES:
            continue
        registry_active.add(name)

    # inventory Group A set (retired 이름 제외)
    inventory_set = set(n for n in inventory_names if n not in RETIRED_NAMES)

    # registry 에 표 entry 누락 (표 → registry 방향)
    for name in sorted(inventory_set):
        if name not in registry_active:
            violations.append(
                f"[sub-check 1] ADR-060 §결정 13 표 Group A entry '{name}'"
                f" 가 registry yaml 에 미등록 (status!=Retired entry 기준)"
            )

    # 표 에 registry entry 누락은 별도 체크 불필요 (sub-check 2 가 신규 후보 감지)
    # 단, 비-inventory registry entry 중 inventory에 없는 것 = sub-check 2 영역

    return violations


def _name_registered(inferred_name: str, stem: str, registry_all: set) -> bool:
    """entry name ↔ 후보 파일 이름 정합 판정.

    CFP-508 §결정 20 partial match 허용 (Conservative no-rename policy):
    - exact match: inferred_name OR stem 이 registry_all 에 있음
    - substring match: registry entry name 이 inferred_name 또는 stem 의 substring 포함
      (예: registry 'wording-ssot-grep-lint' ↔ inferred 'wording-ssot' → partial match PASS)
    - 역방향: inferred_name 이 registry entry name 의 substring
    """
    if inferred_name in registry_all or stem in registry_all:
        return True
    # substring match (양방향 — CFP-508 §결정 20 정합)
    for reg_name in registry_all:
        if inferred_name in reg_name or reg_name in inferred_name:
            return True
        if stem in reg_name or reg_name in stem:
            return True
    return False


def check_subcheck2(
    script_candidates: list,
    workflow_candidates: list,
    registry_entries: list,
    workflow_dirs: list,
) -> list:
    """sub-check 2: 4-criteria AND 후보 식별 + registry 미등록 감지.

    CFP-508 §결정 20 partial match 허용 — entry name ↔ workflow basename substring 정합.
    Returns violation list (message strings).
    """
    violations = []

    # registry 등록 entry name set (retired 포함 전체 — 미등록 감지 기준)
    # enforcement_workflow_phase_2 / enforcement_script_phase_2 등 auxiliary field 경로도 수집
    registry_all = set()
    for entry in registry_entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("name"):
            registry_all.add(entry["name"])
        # auxiliary workflow/script path 추출 — stem 을 registry_all 에 추가
        for aux_field in ("enforcement_workflow_phase_2", "enforcement_script_phase_2",
                          "workflow", "detect_command"):
            val = entry.get(aux_field)
            if isinstance(val, str) and "/" in val:
                # path 에서 basename stem 추출 (extension 제거)
                aux_stem = re.sub(r"\.(yml|sh|py)$", "", val.split("/")[-1])
                if aux_stem:
                    registry_all.add(aux_stem)

    # script 후보 score
    for p in script_candidates:
        if not score_candidate(p, workflow_dirs):
            continue
        # 4-criteria PASS — registry 등록 여부 확인 (partial match 포함)
        stem = p.stem
        inferred_name = stem[len("check-"):] if stem.startswith("check-") else stem
        if not _name_registered(inferred_name, stem, registry_all):
            violations.append(
                f"[sub-check 2] script '{p}' — 4-criteria PASS"
                f" but inferred name '{inferred_name}' registry 미등록 (partial match 없음)"
            )

    # workflow 후보 score
    for p in workflow_candidates:
        if not score_candidate(p, workflow_dirs):
            continue
        # workflow: entry name 추론 — workflow stem 에서 -check suffix 제거
        stem = p.stem
        inferred_name = re.sub(r"-check$", "", stem)
        if not _name_registered(inferred_name, stem, registry_all):
            violations.append(
                f"[sub-check 2] workflow '{p}' — 4-criteria PASS"
                f" but inferred name '{inferred_name}' (stem '{stem}') registry 미등록 (partial match 없음)"
            )

    return violations


def main() -> None:
    args = sys.argv[1:]

    # 인자가 있으면 첫 번째 = registry yaml path 오버라이드
    registry_path = Path(args[0]) if args else Path(DEFAULT_REGISTRY)
    adr_path = Path(DEFAULT_ADR_060)
    scripts_dir = Path(DEFAULT_SCRIPTS_DIR)
    workflow_dirs = DEFAULT_WORKFLOW_DIRS

    # ─── start-up assertion: ALLOWLIST 4-path 존재 확인 (purpose b, unconditional) ───
    assert_allowlist_files()

    # ─── registry 로드 ───
    data = load_registry(registry_path)
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        print(
            f"META-ERROR: registry yaml `entries` 가 list 아님"
            f" (type={type(entries).__name__})",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)

    # ─── ADR-060 §결정 13 표 parse ───
    inventory_names = parse_adr060_inventory_table(adr_path)

    # ─── candidate 수집 ───
    script_candidates = collect_script_candidates(scripts_dir)
    workflow_candidates = collect_workflow_candidates(workflow_dirs)

    # ─── sub-check 1 ───
    violations_1 = check_subcheck1(entries, inventory_names)

    # ─── sub-check 2 ───
    violations_2 = check_subcheck2(
        script_candidates, workflow_candidates, entries, workflow_dirs
    )

    all_violations = violations_1 + violations_2

    # ─── 결과 출력 ───
    inv_count = len(inventory_names)
    entry_count = len(entries)
    script_count = len(script_candidates)
    wf_count = len(workflow_candidates)

    print(
        f"check-evidence-registry-anomaly: registry={registry_path}"
        f" ({entry_count} entries) | ADR-060 inventory={inv_count} names"
        f" | scripts={script_count} candidates | workflows={wf_count} candidates"
    )

    if all_violations:
        print(
            f"\n[ANOMALY] violation {len(all_violations)}건 검출:", file=sys.stderr
        )
        for v in all_violations:
            print(f"  - {v}", file=sys.stderr)
        if violations_1:
            print(
                f"\n  sub-check 1 (inventory parity): {len(violations_1)}건",
                file=sys.stderr,
            )
        if violations_2:
            print(
                f"  sub-check 2 (4-criteria candidates): {len(violations_2)}건",
                file=sys.stderr,
            )
        sys.exit(EXIT_VALIDATION_FAIL)
    else:
        print(
            f"[PASS] anomaly 0건 — sub-check 1 inventory parity + sub-check 2 4-criteria"
            f" all clear. ADR-060 Amendment 11 §결정 25 정합."
        )
        sys.exit(EXIT_PASS)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(
            f"META-ERROR: unexpected exception ({type(e).__name__}: {e})",
            file=sys.stderr,
        )
        sys.exit(EXIT_META_ERROR)
