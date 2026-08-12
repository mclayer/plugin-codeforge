"""Contract parity + Envelope/DispatchPacket tests.

Change Plan §8 contract SSOT 이행.
  - NG-5 / AC-10: lane_dispatch_packet snapshot_sha (40자 hex) 강제
  - NG-13: return_envelope artifact handle (meta.evidence_ref + artifact_path|rerun_command)

★검증면 규율★: 아래 게이트 테스트는 **게이트 스크립트를 subprocess 로 실제 호출**한다.
자기가 쓴 dict 를 자기가 다시 읽어 필드 presence 를 확인하는 동어반복(tautology)은
게이트를 통째로 무력화해도 통과하므로 검증면이 될 수 없다 (CFP-2926 hollow-gate 봉합).
`.github/workflows/cfp-2926-phase2-gates.yml` 의 NG-5·NG-13 스텝이 "실 검증면"으로
지목하는 대상이 바로 이 파일의 테스트들이다 — 그 지목이 참이어야 한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

# gate_verdict.py 3-state 값공간 — 게이트 모듈은 이 밖의 exit code 를 내지 않는다.
VALID_GATE_EXIT_CODES = {0, 1, 3}

# check_lane_dispatch_packet._is_valid_sha 계약 = 40자 소문자 hex.
VALID_SNAPSHOT_SHA = "3f6a1c9e0b7d248a5f13e6c802b94d7a1e5c0f83"

# 필드 자체를 패킷에서 제거하기 위한 sentinel (None 은 "필드 존재 + null" 과 구별되어야 한다).
_OMIT = object()


def _run_gate(capture_output, repo_root, script_name, *args):
    """게이트 스크립트를 subprocess 로 실행 → (returncode, verdict JSON dict).

    stdout 마지막 비어있지 않은 줄 = gate_verdict 단일 라인 JSON.
    """
    script = repo_root / "scripts" / "lib" / script_name
    assert script.is_file(), f"gate module not found: {script}"

    proc = capture_output([sys.executable, str(script), *args])
    assert proc.returncode in VALID_GATE_EXIT_CODES, (
        f"{script_name} exit code {proc.returncode} ∉ {sorted(VALID_GATE_EXIT_CODES)} "
        f"(args={args}) — gate 3-state 값공간 위반\nstderr: {proc.stderr[-500:]}"
    )

    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert lines, (
        f"{script_name} 가 verdict JSON 을 emit 하지 않았다 (rc={proc.returncode})"
        f"\nstderr: {proc.stderr[-500:]}"
    )
    return proc.returncode, json.loads(lines[-1])


def _write_yaml(path, payload):
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return str(path)


def _dispatch_packet(**overrides):
    """lane-dispatch-packet-v1 §2 필수 8 필드 유효 패킷 (override 로 결함 주입)."""
    packet = {
        "contract_version": "lane-dispatch-packet-v1",
        "lane": "구현",
        "role": "DeveloperAgent",
        "story_key": "CFP-2926",
        "snapshot_sha": VALID_SNAPSHOT_SHA,
        "scope_globs": ["scripts/lib/**"],
        "output_section": "§8.1",
        "allowed_spawn_roster": [],
    }
    packet.update(overrides)
    return {k: v for k, v in packet.items() if v is not _OMIT}


def _return_envelope(**meta_overrides):
    """return-envelope-v1 유효 envelope (meta override 로 결함 주입)."""
    meta = {
        "evidence_ref": ["scripts/lib/check_return_envelope_handle.py:40"],
        "artifact_path": "docs/stories/CFP-2926.md",
        "rerun_command": "python -m pytest tests/unit/cfp_2926/ -q",
    }
    meta.update(meta_overrides)
    return {"meta": {k: v for k, v in meta.items() if v is not _OMIT}}


def test_return_envelope_requires_handle(tmp_path, repo_root, capture_output):
    """NG-13: 게이트가 return_envelope artifact handle 을 실제로 강제한다.

    ★check_return_envelope_handle.py 를 subprocess 로 호출한다★ — 이전 판본은 자기가 쓴
    `{"handle": "ret-001"}` 을 자기가 다시 읽어 `assert "handle" in row` 하는 동어반복이었고,
    게다가 검사하던 필드명 `handle` 은 스크립트가 실제로 보는 필드
    (`meta.evidence_ref` / `meta.artifact_path` / `meta.rerun_command`)와 아예 달랐다.
    그래서 `_check_handle` 을 통째로 무력화해도 통과했다 (CFP-2926 hollow-gate 봉합).

    [Mutant: `_check_handle` 을 무조건 valid 로 무력화 → 이 테스트 RED]
    [Discriminating: 양성 대조(PASS) + evidence_ref 공백(RED) + artifact handle 2종 부재(RED)]
    """
    # ⓐ 양성 대조 — 유효 envelope 는 PASS(0). (게이트가 항상 RED 여서 통과하는 상황 배제)
    ok_path = _write_yaml(tmp_path / "envelope-ok.yaml", _return_envelope())
    rc, payload = _run_gate(
        capture_output, repo_root, "check_return_envelope_handle.py", "--envelope", ok_path
    )
    assert rc == 0 and payload["verdict"] == "PASS", (
        f"유효 envelope 가 PASS 가 아니다: rc={rc} payload={payload}"
    )
    assert payload["gate_id"] == "NG-13", f"gate_id mismatch: {payload}"

    # ⓑ meta.evidence_ref 가 비어 있으면 RED(1) — reason=evidence_ref_empty
    empty_ref_path = _write_yaml(
        tmp_path / "envelope-no-evidence.yaml", _return_envelope(evidence_ref=[])
    )
    rc, payload = _run_gate(
        capture_output, repo_root, "check_return_envelope_handle.py", "--envelope", empty_ref_path
    )
    assert rc == 1 and payload["verdict"] == "RED", (
        f"evidence_ref 공백이 RED 가 아니다 (검사 무력화 의심): rc={rc} payload={payload}"
    )
    assert payload["reason"] == "evidence_ref_empty", (
        f"reason 이 evidence_ref 축이 아니다 (다른 사유로 우연히 RED): {payload}"
    )

    # ⓒ artifact handle 2종(artifact_path·rerun_command) 전부 부재면 RED(1)
    no_handle_path = _write_yaml(
        tmp_path / "envelope-no-handle.yaml",
        _return_envelope(artifact_path=_OMIT, rerun_command=_OMIT),
    )
    rc, payload = _run_gate(
        capture_output, repo_root, "check_return_envelope_handle.py", "--envelope", no_handle_path
    )
    assert rc == 1 and payload["verdict"] == "RED", (
        f"artifact handle 전무가 RED 가 아니다 (검사 무력화 의심): rc={rc} payload={payload}"
    )
    assert payload["reason"] == "artifact_handle_missing", (
        f"reason 이 artifact handle 축이 아니다: {payload}"
    )

    # ⓓ 2종 중 하나만 있어도 계약 충족 (§17 "둘 중 최소 1개") — 과잉 RED 방지 대조
    for kept, dropped in (("artifact_path", "rerun_command"), ("rerun_command", "artifact_path")):
        one_path = _write_yaml(
            tmp_path / f"envelope-only-{kept}.yaml",
            _return_envelope(**{dropped: _OMIT}),
        )
        rc, payload = _run_gate(
            capture_output, repo_root, "check_return_envelope_handle.py", "--envelope", one_path
        )
        assert rc == 0 and payload["verdict"] == "PASS", (
            f"{kept} 단독 envelope 가 PASS 가 아니다: rc={rc} payload={payload}"
        )


def test_dispatch_packet_requires_snapshot_sha(tmp_path, repo_root, capture_output):
    """AC-10 / NG-5: 게이트가 snapshot_sha 를 실제로 강제한다.

    ★check_lane_dispatch_packet.py 를 subprocess 로 호출한다★ — 이전 판본은 자기가 쓴
    dict 를 tmp JSONL 로 썼다가 다시 읽어 `assert "snapshot_sha" in row` 하는 동어반복이라
    게이트에서 snapshot_sha 요구·검증을 전부 제거해도 통과했다 (CFP-2926 hollow-gate 봉합).
    부수적으로 그 fixture 의 sha 기준은 `len>=6` 이고 값(`xyz789uvw012`)은 hex 도 아니어서
    게이트의 40자 hex 계약과 상충했다 — 이제 fixture 도 40자 hex 실값을 쓴다.

    [Mutant: REQUIRED_FIELDS 의 snapshot_sha 제거 + _is_valid_sha 검사 삭제 → 이 테스트 RED]
    [Discriminating: 양성 대조(PASS) + 필드 누락(RED) + 형식 위반 3종(RED)]
    """
    # ⓐ 양성 대조 — 유효 패킷은 PASS(0). (게이트가 항상 RED 여서 통과하는 상황 배제)
    ok_path = _write_yaml(
        tmp_path / "packet-ok.yaml", {"lane_dispatch_packet": _dispatch_packet()}
    )
    rc, payload = _run_gate(
        capture_output, repo_root, "check_lane_dispatch_packet.py", "--packet", ok_path
    )
    assert rc == 0 and payload["verdict"] == "PASS", (
        f"유효 패킷이 PASS 가 아니다: rc={rc} payload={payload}"
    )
    assert payload["gate_id"] == "NG-5", f"gate_id mismatch: {payload}"

    # ⓑ snapshot_sha 필드 누락 → RED(1) + ESCALATE_PACKET_INCOMPLETE
    missing_path = _write_yaml(
        tmp_path / "packet-missing-sha.yaml",
        {"lane_dispatch_packet": _dispatch_packet(snapshot_sha=_OMIT)},
    )
    rc, payload = _run_gate(
        capture_output, repo_root, "check_lane_dispatch_packet.py", "--packet", missing_path
    )
    assert rc == 1 and payload["verdict"] == "RED", (
        f"snapshot_sha 누락이 RED 가 아니다 (요구 자체가 소실): rc={rc} payload={payload}"
    )
    assert payload["reason"] == "ESCALATE_PACKET_INCOMPLETE", (
        f"reason 이 필수필드 누락 축이 아니다: {payload}"
    )
    assert "snapshot_sha" in payload["identity_probe"].get("missing_fields", []), (
        f"missing_fields 가 snapshot_sha 를 지목하지 않았다: {payload}"
    )

    # ⓒ 40자 hex 계약 위반 3종 → 전부 RED(1) + reason 이 snapshot_sha 축을 지목
    bad_shas = {
        "짧은 비-hex 12자 (구 fixture 값)": "xyz789uvw012",
        "39자 hex (1자 부족)": VALID_SNAPSHOT_SHA[:-1],
        "40자지만 비-hex": "z" * 40,
    }
    for label, bad in bad_shas.items():
        bad_path = _write_yaml(
            tmp_path / f"packet-bad-{len(bad)}-{bad[:3]}.yaml",
            {"lane_dispatch_packet": _dispatch_packet(snapshot_sha=bad)},
        )
        rc, payload = _run_gate(
            capture_output, repo_root, "check_lane_dispatch_packet.py", "--packet", bad_path
        )
        assert rc == 1 and payload["verdict"] == "RED", (
            f"[{label}] snapshot_sha={bad!r} 가 RED 가 아니다 (형식 검증 소실): "
            f"rc={rc} payload={payload}"
        )
        assert "snapshot_sha" in payload["reason"], (
            f"[{label}] reason 이 snapshot_sha 축이 아니다 (다른 사유로 우연히 RED): {payload}"
        )


def test_dispatch_packet_gate_exit_code_domain(repo_root, capture_output):
    """NG-5 게이트 exit code 가 3-state 값공간 {0,1,3} 안에 머문다.

    gate_verdict.py 계약: PASS=0 / RED=1 / INCONCLUSIVE=3. argparse 의 SystemExit 을
    성공 종료까지 싸잡아 `return 2` 하면 값공간 **밖**(rc=2)으로 샌다 —
    `--help` 가 2 를 내던 결함(CFP-2926 NG-5 정정)의 회귀 가드.

    [Mutant: `except SystemExit: return 2` 복원 → --help rc=2 ∉ {0,1,3} → 이 테스트 RED]
    [Discriminating: rc 값공간 + `--help`=0 / 인자 없음=1 + RED 경로의 verdict JSON 실체]
    """
    script = repo_root / "scripts" / "lib" / "check_lane_dispatch_packet.py"
    assert script.is_file(), f"gate module not found: {script}"

    # (인자, 기대 rc, 사유)
    cases = [
        (["--help"], 0, "--help = argparse 성공 종료 → 값공간 안의 0"),
        ([], 1, "필수 인자(--packet) 누락 = unknown-input fail-closed → RED(1)"),
    ]

    for extra_args, expected_rc, why in cases:
        proc = capture_output([sys.executable, str(script), *extra_args])
        assert proc.returncode in VALID_GATE_EXIT_CODES, (
            f"exit code {proc.returncode} ∉ {sorted(VALID_GATE_EXIT_CODES)} "
            f"(args={extra_args}) — gate 3-state 값공간 위반"
        )
        assert proc.returncode == expected_rc, (
            f"args={extra_args}: expected rc={expected_rc} ({why}), got {proc.returncode}"
        )

    # RED 경로는 rc 만이 아니라 gate_verdict JSON 실체를 내야 한다 (조용한 rc=1 과 구별).
    red_proc = capture_output([sys.executable, str(script)])
    stdout_lines = [ln for ln in red_proc.stdout.splitlines() if ln.strip()]
    assert stdout_lines, "argparse 오류 경로가 gate_verdict JSON 을 emit 하지 않았다"
    payload = json.loads(stdout_lines[-1])
    assert payload["gate_id"] == "NG-5", f"gate_id mismatch: {payload}"
    assert payload["verdict"] == "RED", f"argparse 오류는 fail-closed RED 여야 한다: {payload}"


def test_envelope_schema_consistency(tmp_path):
    """contract: envelope row 개별 스키마 일관성.

    모든 행이 공통 필드 보유: handle, timestamp, source_agent.
    """
    envelope_ledger = tmp_path / "envelope-test.jsonl"

    rows = [
        {
            "handle": "h1",
            "timestamp": 1692374400000,
            "source_agent": "Orchestrator",
            "payload": "test-data",
        },
    ]

    envelope_ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    lines = envelope_ledger.read_text(encoding="utf-8").splitlines()
    required_fields = {"handle", "timestamp", "source_agent"}

    for line in lines:
        if line.strip():
            row = json.loads(line)
            missing = required_fields - set(row.keys())
            assert not missing, f"envelope row missing fields: {missing}"
