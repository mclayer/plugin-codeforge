#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_return_envelope_handle.py — CFP-2926 NG-13 return-envelope-v1.md artifact handle check.

return_envelope 컨트랙트 필수 artifact handle 검증:
  - handle = artifact path (실제 산출물 파일 경로) + rerun command (재실행 커맨드)
  - 둘 다 필수: handle 부재 = RED
  - INCONCLUSIVE: envelope 형식 자체가 부재하거나 empty

Payload 내부에서 artifact handle 정보 확인:
  - envelope.meta.evidence_ref 배열이 존재하고 최소 1개 이상의 path:line 포인터 포함
  - return_envelope.meta.artifact_path (optional but recommended)
  - return_envelope.meta.rerun_command (optional but recommended)

필수 조건:
  1. evidence_ref 배열 존재 (1개 이상)
  2. artifact_path 또는 rerun_command 명시 (둘 중 최소 1개)

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import json
import os
import sys
import yaml

from gate_verdict import GateResult, emit, RED, PASS, INCONCLUSIVE, empty_target

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-13"


def _check_handle(envelope_data):
    """return_envelope artifact handle 검증.

    Returns: (is_valid, reason, trace)
    """
    if not isinstance(envelope_data, dict):
        return False, "envelope_data_not_dict", {}

    # envelope.meta 확인
    meta = envelope_data.get("meta", {})
    if not isinstance(meta, dict):
        return False, "envelope_meta_not_dict", {}

    # evidence_ref 배열 확인 (최소 1개)
    evidence_ref = meta.get("evidence_ref", [])
    if not isinstance(evidence_ref, list):
        return False, "evidence_ref_not_list", {}

    if len(evidence_ref) == 0:
        return False, "evidence_ref_empty", {}

    trace = {"evidence_ref_count": len(evidence_ref)}

    # artifact handle: path + command 둘 다 또는 둘 중 하나
    # 권장: artifact_path 또는 rerun_command 명시
    artifact_path = meta.get("artifact_path")
    rerun_command = meta.get("rerun_command")

    # 둘 다 부재 시 = 위험 신호, 하지만 evidence_ref 만으로도 추적 가능
    # ADR-119: hollow-gate 차단 — "handle 부재"는 명확한 신호여야 함
    # 최소 조건: evidence_ref 존재 + (artifact_path 또는 rerun_command 명시)

    has_artifact_path = isinstance(artifact_path, str) and len(artifact_path) > 0
    has_rerun_command = isinstance(rerun_command, str) and len(rerun_command) > 0

    if not (has_artifact_path or has_rerun_command):
        # evidence_ref 만으로는 부족 — artifact handle 미정의
        return False, "artifact_handle_missing", trace

    trace["artifact_path_present"] = has_artifact_path
    trace["rerun_command_present"] = has_rerun_command

    return True, "artifact_handle_valid", trace


def main(argv=None):
    """Main entry point.

    CLI:
      python check_return_envelope_handle.py --envelope <path.yaml|path.json>

    Exit codes:
      0 = PASS
      1 = RED (validation fail)
      3 = INCONCLUSIVE (empty target)
    """
    parser = argparse.ArgumentParser(
        prog="check_return_envelope_handle.py",
        description="return-envelope-v1.md artifact handle validation.",
    )
    parser.add_argument(
        "--envelope",
        required=True,
        help="Path to return envelope YAML or JSON file.",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    envelope_path = args.envelope

    # 파일 존재 확인
    if not os.path.isfile(envelope_path):
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="envelope_file_not_found",
            identity_probe={"envelope_path": envelope_path},
        )
        return emit(result)

    # 파일 로드 (YAML 또는 JSON)
    try:
        with open(envelope_path, "r", encoding="utf-8") as f:
            if envelope_path.endswith(".json"):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
    except Exception as e:
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason=f"parse_error: {str(e)[:80]}",
            identity_probe={"envelope_path": envelope_path},
        )
        return emit(result)

    if data is None:
        result = empty_target(
            gate_id=GATE_ID,
            reason="envelope_file_empty",
            identity_probe={"envelope_path": envelope_path},
        )
        return emit(result)

    # return_envelope 키 또는 top-level 확인
    envelope_obj = data.get("return_envelope", {}) or data.get("envelope", {}) or data

    if not envelope_obj:
        result = empty_target(
            gate_id=GATE_ID,
            reason="no_envelope_structure",
            identity_probe={"envelope_path": envelope_path},
        )
        return emit(result)

    # handle 검증
    is_valid, reason, trace = _check_handle(envelope_obj)

    if not is_valid:
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason=reason,
            trace=trace,
            identity_probe={"envelope_path": envelope_path},
        )
        return emit(result)

    # PASS
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="artifact_handle_present",
        trace=trace,
        identity_probe={"envelope_path": envelope_path},
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
