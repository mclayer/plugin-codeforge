"""CFP-1787 — ADR-082 Amendment 33 sub-scope 1-V execution_context_reconciliation lint.

Verdict packet 안 `execution_context_state` 5 sub-field presence + schema validation.

Exit codes:
  0 — PASS (all 5 fields present + schema valid)
  1 — missing field (1+ of 5 sub-fields absent OR execution_context_state field itself absent)
  2 — schema invalid (field present but wrong type / wrong enum value)

Usage:
  python scripts/lib/check_execution_context_state.py <packet.json>

SSOT: docs/adr/ADR-082-write-time-self-write-verification-mandate.md §Amendment 33
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = {
    "working_dir_abs_path": str,
    "target_write_repo": str,
    "staged_files_required": list,
    "branch_required": str,
    "remote_sync_required": str,
}

REMOTE_SYNC_ENUM = {"pull", "fetch", "N/A"}


def check_packet(packet_path: Path) -> tuple[int, str]:
    try:
        data = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return 2, f"schema invalid: JSON parse error: {e}"

    ecs = data.get("execution_context_state")
    if ecs is None:
        return 1, "missing field: execution_context_state field itself absent"

    if not isinstance(ecs, dict):
        return 2, "schema invalid: execution_context_state must be object"

    missing = [k for k in REQUIRED_FIELDS if k not in ecs]
    if missing:
        return 1, f"missing field: {', '.join(missing)}"

    for field, expected_type in REQUIRED_FIELDS.items():
        value = ecs[field]
        if not isinstance(value, expected_type):
            return 2, (
                f"schema invalid: {field} expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    sync_value = ecs["remote_sync_required"]
    if sync_value not in REMOTE_SYNC_ENUM:
        return 2, (
            f"schema invalid: remote_sync_required must be one of "
            f"enum {sorted(REMOTE_SYNC_ENUM)}, got '{sync_value}'"
        )

    return 0, "PASS"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_execution_context_state.py <packet.json>", file=sys.stderr)
        return 2

    packet_path = Path(sys.argv[1])
    if not packet_path.exists():
        print(f"file not found: {packet_path}", file=sys.stderr)
        return 2

    code, msg = check_packet(packet_path)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
