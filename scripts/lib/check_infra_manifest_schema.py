#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_infra_manifest_schema.py
CFP-2700 (Epic) G3 / ADR-157 §결정1 — infra_resources manifest schema validator (AC-2).

manifest(`.claude/_overlay/project.yaml` `infra_resources:` block)의 **4 필수 필드**를 저작 시점에
  검증한다 (ADR-157 §결정1: "각 resource 는 `id` · `canonical_env` · `aliases`(빈 집합 허용) 표현,
  각 execution_unit 은 `required[]` 표현. 필드별 누락 = negative fixture 로 non-zero exit(AC-2)"):

  S1  resource `id` 누락            → exit 1 + "필수 필드 누락: id"
  S2  resource `canonical_env` 누락 → exit 1 + "필수 필드 누락: canonical_env"
  S3  resource `aliases` 누락       → exit 1 + "필수 필드 누락: aliases" (빈 집합 표현은 허용 —
        `aliases:` bare / `accepted: []` 전부 유효. 누락과 빈 집합은 다르다: 누락 = "별칭이 없다는
        선언조차 없음" = alias drift 판정 불능, 빈 집합 = "별칭 없음"의 명시 선언.)
  S4  execution_unit `required` 누락 → exit 1 + "필수 필드 누락: required" (`required: []` 는 유효 —
        요구 자원 0 의 명시 선언.)

  + D2 소비처가 의존하는 스키마 계약 3종 (ADR-157 §결정1 EDGE / F-CLA-004):
  S5  `resource_modes` 값 enum 위반 (∈ {required, optional_degradable}; `_degraded_behavior` suffix
        키는 mode 엔트리 아닌 metadata — F-CLA-004 파서 계약, enum 검사 제외)
  S6  `optional_degradable` 인데 `<rid>_degraded_behavior` 선언 부재 (no-silent-degrade — §결정1)
  S7  `required[]` 가 plane A 에 없는 resource-id 참조 (dangling — ID-only 참조 무결성. D2 startup
        validator 는 dangling rid 를 fail-closed(미충족) 처리하나, 저작 시점에 여기서 먼저 잡는다.)

  + `resources: none` sentinel 은 `reason` 동반 시 유효한 비적용 선언(exit 0) — reason 부재 = exit 1
    (none-disguise 저작 시점 대칭, D3 스캔 시점 검출과 이중 안전망).

★ 파서 재사용 (AC-9 parity 정합): block 탐지·라인 read·주석 strip·inline list 파싱은
  `check_infra_resource_drift.py` (G2, D3 스캐너) 의 primitive 를 import 재사용한다 — 재구현 금지.
  단 S1(id 누락) 검출은 관용 파서(parse_manifest)가 id-없는 항목을 **조용히 drop** 하는 구조라
  (파서는 `- id:` 라인에서만 항목을 연다), 필드-존재 판정만큼은 본 validator 의 구조 pass 가 담당한다
  — 관용 파서(스캔 fitness) 와 엄격 검증(저작 게이트) 의 역할 분리이지 allow-set 재구현이 아니다.
  S5/S6/S7 은 공유 파서의 plane B 출력(execution_units)을 그대로 소비한다.

★ 정직 천장 (은폐 금지 — ADR-157 §결정8 상속):
  - 라인 파서 상한: 하우스 yaml 컨벤션(2-space 정렬, `- ` list marker)을 가정한 indentation 구조
    pass 다 — 임의 yaml 방언(flow mapping 중첩 등)의 완전 파싱을 주장하지 않는다(dependency-free
    trade-off, G2 파서 동형).
  - R6(deprecated alias 기한 필드 deprecated_since/remove_after) 검증 = 본 validator **미포함**
    (4 필수 필드 + D2 의존 계약 한정 — R6 강제는 소비처 착지 시 test 동반 추가).
  - 본 validator 는 wrapper CI 에서 wrapper-self manifest 를 dogfood 검증할 뿐, consumer manifest 를
    물리 강제하지 못한다(I-5 채택-bounded — ADR-157 §결정2 동형).

★ born-safe: 입력 bound 는 재사용한 G2 primitive 의 bound(PER_FILE_SCAN_CAP / MAX_PHYSICAL_LINE_LEN /
  MAX_BLOCK_SPAN)를 그대로 상속. 전 regex anchored + bounded quantifier, nested quantifier 0.
  No eval/exec/yaml.safe_load. 스캔 대상 = 인자로 받은 manifest 1 파일만(path-traversal 면 0).

CLI 계약 (ADR-061 house style):
  python3 scripts/lib/check_infra_manifest_schema.py [--manifest PATH] [--repo-root DIR]

Exit codes:
  0 = PASS (4 필수 필드 + S5/S6/S7 전건 충족, 또는 유효한 `resources: none` + reason 선언).
  1 = SCHEMA 위반 ≥1 (위반별 누락 필드명/locus 출력).
  2 = usage 오류 / manifest 파일 부재·unreadable / `infra_resources:` block 부재 (검증 대상 부재 —
      block 유무 자체의 anti-hollow 판정은 D3 스캐너 none-disguise 소관, 본 validator 는 "존재하는
      block 의 필드 완전성" 게이트라 대상 부재 = 위반 아닌 usage-tier).

ADR refs: ADR-157 §결정1 (4 필수 필드 / EDGE mode / no-silent-degrade) / ADR-061 §결정1 (Python SSOT) /
  ADR-119 (게이트 = ground-truth) / F-CLA-004 (docs/project-config-schema.md `resource_modes` 파서 계약).
"""

import argparse
import os
import re
import sys

# Windows cp949 인코딩 문제 회피 (ADR-061 portability 답습).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# G2 파서 primitive 재사용 (sibling import — 재구현 금지, AC-9 parity 정합).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_infra_resource_drift as drift  # noqa: E402

_MODE_ENUM = ("required", "optional_degradable")
_DEGRADED_SUFFIX = "_degraded_behavior"

# item 내부 top-level key: `key:` (값 유무 무관). anchored + bounded.
_RE_ITEM_KEY = re.compile(r"^([A-Za-z0-9_]{1,64}):")
# resources 항목 시작: `- key:` — 첫 key 가 무엇이든 새 항목 (id-없는 항목도 관측해야 S1 성립).
_RE_ITEM_START = re.compile(r"^-\s{1,4}([A-Za-z0-9_]{1,64}):")
# 실행단위 이름: `<name>:` 값 없음.
_RE_UNIT_NAME = re.compile(r"^([A-Za-z0-9._-]{1,128}):\s*$")


def _structural_pass(block):
    """block 라인들을 구조 pass — (res_items, units) 반환.

    res_items = [{"lineno": n(block-상대 1-based), "keys": set, "id": str|None, "key_indent": int}]
    units     = [{"lineno": n, "name": str, "keys": set}]
    관용 파서(parse_manifest)가 id-없는 항목을 drop 하므로 필드-존재 판정은 여기서 수행 (header ★ 참조).
    """
    section = None
    res_items = []
    units = []
    cur_item = None
    cur_unit = None
    unit_indent = None
    res_item_indent = None  # 첫 항목의 indent 로 고정 — 하위 sub-list(`deprecated: - name:`)의
    #   `- key:` 라인이 새 resource 항목으로 오인되는 것을 차단.

    for offset, line in enumerate(block[1:], start=2):
        code = drift._strip_hash_comment(line)
        stripped = code.strip()
        if not stripped:
            continue
        indent = drift._indent_of(code)

        if indent <= 2:
            if re.match(r"^resources:\s*$", stripped):
                section = "resources"
                cur_item = None
                continue
            if re.match(r"^execution_units:\s*$", stripped):
                section = "units"
                cur_unit = None
                unit_indent = None
                continue
            if re.match(r"^startup_validation:\s*$", stripped):
                section = "sv"
                continue
            if indent == 0:
                section = None
                continue

        if section == "resources":
            mm = _RE_ITEM_START.match(stripped)
            if mm and (res_item_indent is None or indent == res_item_indent):
                res_item_indent = indent if res_item_indent is None else res_item_indent
                cur_item = {"lineno": offset, "keys": {mm.group(1)}, "id": None,
                            "key_indent": indent + 2}
                if mm.group(1) == "id":
                    rest = stripped[mm.end():].strip().strip('"').strip("'")
                    cur_item["id"] = rest or None
                res_items.append(cur_item)
                continue
            if cur_item is not None and indent == cur_item["key_indent"]:
                mm = _RE_ITEM_KEY.match(stripped)
                if mm:
                    cur_item["keys"].add(mm.group(1))
                    if mm.group(1) == "id" and cur_item["id"] is None:
                        rest = stripped[mm.end():].strip().strip('"').strip("'")
                        cur_item["id"] = rest or None
            continue

        if section == "units":
            if unit_indent is None and _RE_UNIT_NAME.match(stripped):
                unit_indent = indent
            if unit_indent is not None and indent == unit_indent:
                mm = _RE_UNIT_NAME.match(stripped)
                if mm:
                    cur_unit = {"lineno": offset, "name": mm.group(1), "keys": set()}
                    units.append(cur_unit)
                    continue
            if cur_unit is not None and unit_indent is not None and indent == unit_indent + 2:
                mm = _RE_ITEM_KEY.match(stripped)
                if mm:
                    cur_unit["keys"].add(mm.group(1))
            continue

    return res_items, units


def validate_schema(manifest_path):
    """manifest 스키마 검증 → (exit_code, [violation 메시지], summary dict).

    pure 판정 함수 — 출력 부작용 0 (호출자가 render). exit_code ∈ {0, 1, 2}.
    """
    physical = drift._read_physical(manifest_path)
    if physical is None:
        return (2, ["manifest 파일 부재/unreadable — %s" % manifest_path], {})
    span = drift._find_infra_block(physical)
    if span is None:
        return (2, ["`infra_resources:` block 부재 — 검증 대상 없음 (%s). block 유무 anti-hollow "
                    "판정은 D3 스캐너(none-disguise) 소관." % manifest_path], {})

    m = drift.parse_manifest(manifest_path)
    start, end = span
    block = physical[start:end]
    res_items, units = _structural_pass(block)

    violations = []

    # ── `resources: none` sentinel 경로 (비적용 유효 선언 vs reason 누락) ──
    if m.none_sentinel and not res_items:
        if m.has_reason:
            return (0, [], {"none_declared": True, "resources": 0, "units": len(units)})
        violations.append("resources: none 선언인데 사유(reason) 부재 — 필수 필드 누락: reason "
                          "(none-disguise 저작 시점 차단)")
        return (1, violations, {"none_declared": True, "resources": 0, "units": len(units)})

    # ── S1/S2/S3: resource 4 필수 필드 중 3 (id / canonical_env / aliases) ──
    for idx, item in enumerate(res_items):
        locus = "resources[%d]%s(block+%d행)" % (
            idx, (" id=%s " % item["id"]) if item["id"] else " ", item["lineno"])
        if "id" not in item["keys"] or not item["id"]:
            violations.append("%s 필수 필드 누락: id" % locus)
        if "canonical_env" not in item["keys"]:
            violations.append("%s 필수 필드 누락: canonical_env" % locus)
        if "aliases" not in item["keys"]:
            violations.append("%s 필수 필드 누락: aliases (빈 집합 표현 `aliases:` + `accepted: []` 로 "
                              "명시 — ADR-157 §결정1 4 필수 필드)" % locus)

    # ── S4: execution_unit `required` 표현 ──
    for u in units:
        if "required" not in u["keys"]:
            violations.append("execution_units.%s(block+%d행) 필수 필드 누락: required "
                              "(`required: []` = 요구 자원 0 의 명시 선언으로 유효)" % (u["name"], u["lineno"]))

    # ── S5/S6/S7: 공유 파서 plane B 출력 소비 (mode enum / no-silent-degrade / dangling rid) ──
    known_ids = set(m.all_keys_by_resource.keys())
    for name, unit in m.execution_units.items():
        for rid, mode in unit["modes"].items():
            if mode not in _MODE_ENUM:
                violations.append("execution_units.%s resource_modes 값 위반: %s=%s "
                                  "(enum {required, optional_degradable}; `%s` suffix 키는 metadata — "
                                  "F-CLA-004)" % (name, rid, mode, _DEGRADED_SUFFIX))
            if mode == "optional_degradable" and rid not in unit["degraded_behavior"]:
                violations.append("execution_units.%s optional_degradable 자원 %s 의 "
                                  "%s%s 선언 부재 (no-silent-degrade — ADR-157 §결정1)"
                                  % (name, rid, rid, _DEGRADED_SUFFIX))
        for rid in unit["required"]:
            if rid not in known_ids:
                violations.append("execution_units.%s.required 참조 자원 미정의: %s "
                                  "(plane A resources[].id 부재 — dangling ID 참조)" % (name, rid))

    summary = {"none_declared": False, "resources": len(res_items), "units": len(units)}
    return ((1 if violations else 0), violations, summary)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_infra_manifest_schema.py",
        description="infra_resources manifest 4-필수-필드 schema validator (AC-2 / ADR-157 §결정1).",
    )
    parser.add_argument("--manifest", default=None, help="manifest(project.yaml) 경로 override.")
    parser.add_argument("--repo-root", default=None, help="repo 루트 (기본 = scripts/lib 기준 자동 탐지).")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    manifest_path = args.manifest or os.path.join(repo_root, drift.DEFAULT_MANIFEST_REL)

    code, violations, summary = validate_schema(manifest_path)
    if code == 2:
        print("::error::check-infra-manifest-schema: %s" % "; ".join(violations))
        return 2
    for v in violations:
        print("::error::check-infra-manifest-schema: SCHEMA — %s" % v)
    if code == 1:
        print("check-infra-manifest-schema: FAIL — %d violation(s) (4 필수 필드: id·canonical_env·"
              "aliases·required — ADR-157 §결정1 / AC-2)" % len(violations))
        return 1
    if summary.get("none_declared"):
        print("check-infra-manifest-schema: PASS — resources: none + reason (유효한 비적용 선언)")
        return 0
    print("check-infra-manifest-schema: PASS — resources=%d execution_units=%d "
          "(4 필수 필드 + mode enum + no-silent-degrade + required 참조 무결성)"
          % (summary["resources"], summary["units"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
