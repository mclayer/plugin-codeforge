#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_lane_dispatch_packet.py — CFP-2926 NG-5 lane-dispatch-packet-v1.md §2 schema validation.

lane_dispatch_packet contract 필수 필드 8개 검증:
  1. contract_version (문자열)
  2. lane (enum: 10개 lane label)
  3. role (agent_type, 필수)
  4. story_key (CFP-XXXX 형식)
  5. snapshot_sha (40자 hex)
  6. scope_globs (list)
  7. output_section (§N.M 형식)
  8. allowed_spawn_roster (list, depth-1 leaf = [])

필수 필드 누락 시: verdict=RED + reason=ESCALATE_PACKET_INCOMPLETE
unknown-input(packet 형식 자체 오류): verdict=RED + reason=UNKNOWN_INPUT
정상: verdict=PASS

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE (gate_verdict.py 3-state 값공간 — 이 셋 밖의 값 없음)
  - `--help` 등 argparse 성공 종료 = 0 (검사 미수행 정상 종료)
  - argparse 사용법 오류(필수 인자 누락·unknown flag) = [154-AC-4] unknown-input → RED(1)
"""

import argparse
import json
import os
import re
import sys
import yaml

from gate_verdict import GateResult, emit, RED, PASS, INCONCLUSIVE, unknown_input, empty_target

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-5"

# 10개 lane label enum (label-registry-v2)
VALID_LANES = {
    "요구사항",
    "요구사항-리뷰",
    "설계",
    "설계-리뷰",
    "구현",
    "구현-리뷰",
    "구현-테스트",
    "보안-테스트",
    "배포",
    "배포-리뷰",
    "없음",
}

# 필수 필드 리스트 (§2 Schema)
REQUIRED_FIELDS = [
    "contract_version",
    "lane",
    "role",
    "story_key",
    "snapshot_sha",
    "scope_globs",
    "output_section",
    "allowed_spawn_roster",
]


def _is_valid_sha(value):
    """snapshot_sha = 40자 hex 검증."""
    if not isinstance(value, str):
        return False
    if len(value) != 40:
        return False
    return re.match(r"^[a-f0-9]{40}$", value) is not None


def _validate_packet(packet_data):
    """lane_dispatch_packet 필드 검증.

    Returns: (is_valid, missing_fields, error_reason)
    """
    if not isinstance(packet_data, dict):
        return False, [], "packet is not a dict"

    missing = []
    for field in REQUIRED_FIELDS:
        if field not in packet_data:
            missing.append(field)
        elif packet_data[field] is None:
            missing.append(field)

    if missing:
        return False, missing, "ESCALATE_PACKET_INCOMPLETE"

    # 각 필드 타입/값 검증
    trace = {}

    # contract_version: string
    if not isinstance(packet_data.get("contract_version"), str):
        return False, [], "contract_version must be string"
    trace["contract_version"] = packet_data["contract_version"]

    # lane: enum (VALID_LANES)
    lane = packet_data.get("lane")
    if lane not in VALID_LANES:
        return False, [], f"lane not in valid enum: {lane}"
    trace["lane"] = lane

    # role: string (agent_type)
    if not isinstance(packet_data.get("role"), str):
        return False, [], "role must be string (agent_type)"
    trace["role"] = packet_data["role"]

    # story_key: string (e.g., CFP-2926)
    story_key = packet_data.get("story_key")
    if not isinstance(story_key, str):
        return False, [], "story_key must be string"
    trace["story_key"] = story_key

    # snapshot_sha: 40-hex
    snapshot_sha = packet_data.get("snapshot_sha")
    if not _is_valid_sha(snapshot_sha):
        return False, [], f"snapshot_sha must be 40-char hex (got: {snapshot_sha})"
    trace["snapshot_sha"] = snapshot_sha

    # scope_globs: list
    scope_globs = packet_data.get("scope_globs")
    if not isinstance(scope_globs, list):
        return False, [], "scope_globs must be list"
    trace["scope_globs_count"] = len(scope_globs)

    # output_section: string (§N or §N.M format)
    output_section = packet_data.get("output_section")
    if not isinstance(output_section, str):
        return False, [], "output_section must be string"
    if not re.match(r"^§\d+(\.\d+)*$", output_section):
        return False, [], f"output_section must be §N or §N.M format (got: {output_section})"
    trace["output_section"] = output_section

    # allowed_spawn_roster: list
    roster = packet_data.get("allowed_spawn_roster")
    if not isinstance(roster, list):
        return False, [], "allowed_spawn_roster must be list"
    trace["allowed_spawn_roster_count"] = len(roster)

    return True, [], trace


def main(argv=None):
    """Main entry point.

    CLI:
      python check_lane_dispatch_packet.py --packet <path.yaml>

    Exit codes:
      0 = PASS (또는 `--help` 등 argparse 성공 종료 — 검사 미수행 정상 종료)
      1 = RED (validation fail / argparse 사용법 오류 = unknown-input fail-closed)
      3 = INCONCLUSIVE (empty target)

    ★반환값은 {0, 1, 3} 밖으로 나가지 않는다★ — gate_verdict.py 3-state 값공간.
    """
    parser = argparse.ArgumentParser(
        prog="check_lane_dispatch_packet.py",
        description="lane-dispatch-packet-v1.md §2 schema validation.",
    )
    parser.add_argument("--packet", required=True, help="Path to dispatch packet YAML file.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")

    cli_args = list(argv[1:]) if argv else []
    try:
        args = parser.parse_args(cli_args)
    except SystemExit as exc:
        # argparse 는 `--help` 성공 종료도 SystemExit(0) 으로 raise 한다.
        # 이를 오류와 싸잡아 2 로 변환하면 게이트 3-state 값공간 {0,1,3} 밖으로 샌다.
        argparse_code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
        if argparse_code == 0:
            # `--help` / 정상 종료 — 검사 미수행, 값공간 안의 0 으로 통과.
            return 0
        # 사용법 오류(필수 인자 누락·unknown flag) = 호출자 입력 오류
        # = [154-AC-4] unknown-input → fail-closed RED(1). 값공간 밖 2 를 반환하지 않는다.
        result = unknown_input(
            gate_id=GATE_ID,
            reason="argparse_usage_error",
            trace={"argparse_exit_code": argparse_code, "argv_count": len(cli_args)},
            identity_probe={"argv": cli_args},
        )
        return emit(result)

    packet_path = args.packet
    repo_root = os.path.abspath(args.repo_root)

    # 패킷 파일 존재 확인
    if not os.path.isfile(packet_path):
        result = unknown_input(
            gate_id=GATE_ID,
            reason="packet_file_not_found",
            identity_probe={"packet_path": packet_path},
        )
        return emit(result)

    # YAML 파싱
    try:
        with open(packet_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=f"yaml_parse_error: {str(e)[:100]}",
            identity_probe={"packet_path": packet_path},
        )
        return emit(result)

    if data is None:
        result = empty_target(
            gate_id=GATE_ID,
            reason="packet_yaml_empty",
            identity_probe={"packet_path": packet_path},
        )
        return emit(result)

    # lane_dispatch_packet 키 추출
    packet_obj = data.get("lane_dispatch_packet", data)

    # 검증 실행
    is_valid, missing_fields, error_or_trace = _validate_packet(packet_obj)

    if not is_valid:
        # error_or_trace 는 문자열(오류 메시지)
        reason = error_or_trace
        if error_or_trace == "ESCALATE_PACKET_INCOMPLETE":
            identity_probe = {"missing_fields": missing_fields}
        else:
            identity_probe = {}

        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason=reason,
            trace={"packet_fields": len(packet_obj) if isinstance(packet_obj, dict) else 0},
            identity_probe=identity_probe,
        )
        return emit(result)

    # PASS
    trace = error_or_trace  # 유효한 경우 trace dict
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="lane_dispatch_packet_v1_schema_valid",
        trace=trace,
        identity_probe={"story_key": packet_obj.get("story_key"), "lane": packet_obj.get("lane")},
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
