#!/usr/bin/env python3
"""
reconcile_json_sidecar.py — CFP-745 Wave 2 Story-5
JSON marker-incapable 영역 sidecar manifest 기반 reconcile helper.

동작:
  - consumer JSON 에서 sidecar managed_paths (RFC 6901 JSON Pointer) 영역만 wrapper 값으로 교체
  - 그 외 key = consumer-current preserve (byte-identical)
  - managed_paths 밖 영역은 wrapper 값 미사용 (consumer 보존)

ADR-027 §결정 7.A.1 carrier 실현 (json marker-incapable sidecar manifest)
reconcile-protocol-v1 §4.7 sidecar_manifest_schema SSOT
ADR-061 정합 — multi-line Python = 외부 .py 의무 (heredoc 금지)
"""

import argparse
import json
import sys
from copy import deepcopy


def _get_pointer(obj, pointer_str):
    """RFC 6901 JSON Pointer get (root-relative, simple implementation)."""
    if pointer_str == "":
        return obj
    parts = pointer_str.lstrip("/").split("/")
    current = obj
    for part in parts:
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current


def _set_pointer(obj, pointer_str, value):
    """RFC 6901 JSON Pointer set (root-relative, simple implementation)."""
    if pointer_str == "":
        return value
    parts = pointer_str.lstrip("/").split("/")
    current = obj
    for part in parts[:-1]:
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if part not in current:
                current[part] = {}
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                raise KeyError(f"Invalid JSON Pointer path: {pointer_str}")
        else:
            raise KeyError(f"Invalid JSON Pointer path: {pointer_str}")

    last = parts[-1].replace("~1", "/").replace("~0", "~")
    if isinstance(current, dict):
        current[last] = value
    elif isinstance(current, list):
        try:
            idx = int(last)
            if idx == len(current):
                current.append(value)
            else:
                current[idx] = value
        except (ValueError, IndexError):
            raise KeyError(f"Invalid JSON Pointer array index: {last}")
    return obj


def reconcile_json(consumer_data, wrapper_data, managed_paths):
    """
    consumer JSON 에 wrapper 의 managed_paths 값을 merge.
    managed_paths 밖 = consumer preserve.
    managed_paths 안 = wrapper value 채택.
    """
    result = deepcopy(consumer_data)
    for ptr in managed_paths:
        wrapper_val = _get_pointer(wrapper_data, ptr)
        if wrapper_val is not None:
            result = _set_pointer(result, ptr, deepcopy(wrapper_val))
    return result


def main():
    parser = argparse.ArgumentParser(
        description="CFP-745: JSON sidecar manifest 기반 reconcile helper"
    )
    parser.add_argument("--consumer", required=True, help="consumer overlay JSON 파일")
    parser.add_argument("--wrapper", required=True, help="wrapper SSOT JSON 파일")
    parser.add_argument("--sidecar", required=True, help="sidecar manifest JSON 파일")
    parser.add_argument("--output", required=True, help="출력 파일 경로")
    args = parser.parse_args()

    # Load sidecar
    try:
        with open(args.sidecar, "r", encoding="utf-8") as f:
            sidecar = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"[reconcile_json_sidecar] sidecar parse error: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate sidecar schema
    if "schema_version" not in sidecar or "managed_paths" not in sidecar:
        print("[reconcile_json_sidecar] sidecar schema invalid: schema_version or managed_paths missing",
              file=sys.stderr)
        sys.exit(1)
    if not isinstance(sidecar["managed_paths"], list):
        print("[reconcile_json_sidecar] sidecar managed_paths must be a list", file=sys.stderr)
        sys.exit(1)

    managed_paths = sidecar["managed_paths"]

    # Load consumer JSON
    try:
        with open(args.consumer, "r", encoding="utf-8") as f:
            consumer_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"[reconcile_json_sidecar] consumer JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    # Load wrapper JSON
    try:
        with open(args.wrapper, "r", encoding="utf-8") as f:
            wrapper_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"[reconcile_json_sidecar] wrapper JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    # Reconcile
    result = reconcile_json(consumer_data, wrapper_data, managed_paths)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[reconcile_json_sidecar] JSON reconcile 완료: {len(managed_paths)}개 managed_paths 적용")
    sys.exit(0)


if __name__ == "__main__":
    main()
