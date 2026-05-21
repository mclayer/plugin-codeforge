#!/usr/bin/env python3
# tests/scripts/cfp-1155/validate_walk_result_schema.py
# CFP-1155 — walk-result-schema.json Python json.load 파싱 + 구조 검증
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
#
# Usage: python3 validate_walk_result_schema.py <path-to-walk-result-schema.json>
# Exit 0: 파싱 + 구조 검증 PASS
# Exit 1: 파싱 실패 또는 구조 검증 FAIL

import json
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_walk_result_schema.py <json_path>", file=sys.stderr)
        sys.exit(1)

    json_path = sys.argv[1]

    if not os.path.isfile(json_path):
        print(f"File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    # 1. JSON 파싱
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"File read error: {e}", file=sys.stderr)
        sys.exit(1)

    errors = []

    # 2. top-level 필드 존재 검증
    required_top = ["schema_version", "carrier", "contract_ref", "walk_result", "layers", "invariants", "test_cases"]
    for field in required_top:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    # 3. walk_result enum 4-value 검증
    walk_result = data.get("walk_result", {})
    enum_values = walk_result.get("enum", [])
    expected_enum = ["SUCCESS", "SUCCESS_WITH_DEGRADATION", "PARTIAL_FAILURE", "FAILED"]
    for v in expected_enum:
        if v not in enum_values:
            errors.append(f"Missing walk_result enum value: {v}")
    if walk_result.get("open_extension") is not False:
        errors.append("walk_result.open_extension must be false")

    # 4. layers 2-layer 구조 검증
    layers = data.get("layers", {})
    if "external_report" not in layers:
        errors.append("Missing layers.external_report")
    if "internal_schema" not in layers:
        errors.append("Missing layers.internal_schema")

    external_fields = layers.get("external_report", {}).get("fields", [])
    required_external = ["from_version", "to_version", "target_version_release_date", "key_changes_summary"]
    for f in required_external:
        if f not in external_fields:
            errors.append(f"Missing external_report field: {f}")

    internal_fields = layers.get("internal_schema", {}).get("fields", [])
    required_internal = ["touched_files", "atomic_invariants", "verify_via", "lane_outcomes"]
    for f in required_internal:
        if f not in internal_fields:
            errors.append(f"Missing internal_schema field: {f}")

    # 5. invariants 검증
    invariants = data.get("invariants", {})
    if invariants.get("enum_closed") is not True:
        errors.append("invariants.enum_closed must be true")
    if invariants.get("layer_disjoint") is not True:
        errors.append("invariants.layer_disjoint must be true")
    if invariants.get("exit_code_deterministic") is not True:
        errors.append("invariants.exit_code_deterministic must be true")
    if invariants.get("silent_success_forbidden") is not True:
        errors.append("invariants.silent_success_forbidden must be true")

    # 6. test_cases TC-1~TC-8 존재 검증
    test_cases = data.get("test_cases", {})
    for tc in [f"TC-{i}" for i in range(1, 9)]:
        if tc not in test_cases:
            errors.append(f"Missing test_case: {tc}")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        sys.exit(1)

    print(f"PASS: walk-result-schema.json validation OK ({len(expected_enum)} enum values, 2 layers, 8 TCs)")
    sys.exit(0)


if __name__ == "__main__":
    main()
