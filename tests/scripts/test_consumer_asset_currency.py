#!/usr/bin/env python3
"""
CFP-2978 AC-5 currency gate test — W-12

[결속 선언]
본 파일의 모든 leg 은 `scripts/lib/check_consumer_asset_currency.py` 를 **실행**해
그 산출(stdout/stderr/rc) 위에서만 판정한다. 리터럴 dict 자기assert 0.

테스트는 아래 3가지 방식 중 하나로만 진행한다:
  (A) subprocess.run() 실행 후 rc/stdout/stderr 파싱 (메인 경로)
  (B) importlib 로 모듈 로드 후 실함수 호출 (D-1 in-process 허용, HTTP boundary monkeypatch)
  (C) static analysis (D-3, workflow shape 검증)

D-2 짝 관측 (핵심):
  C-1 GREEN (신세대 blob in-sync) + D-2 RED (구세대 blob drifted) 를 같은 임시 repo 에서
  연속 관측하여 게이트 판정력 증명. 기존 리터럴 dict assert 는 hollow oracle 이라 미검증.

벤더 fixture:
  - 경로: tests/fixtures/cfp2978/sentinel-old-07d1127a.py.txt
  - 크기: 17814 바이트
  - sha: 07d1127a021280f49dc3b66ef7c848cd59dccea3 (git hash-object -t blob --no-filters 검증)
  - 출처: wrapper 역사 blob (CFP-2451 consumer 동결 상태)
  - 용도: §8.3 D-2 구세대 blob 대조군
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple, Dict, Any
import importlib.util


# 게이트 절대경로
GATE_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "lib" / "check_consumer_asset_currency.py"
)

# 신세대 blob (worktree 현재 HEAD:scripts/lib/check_parallel_work_sentinel.py)
BLOB_CURRENT = "c372d0521db5d996ea9288bd362b83486e1e2553"

# 구세대 blob (벤더 fixture 기반)
BLOB_OLD = "07d1127a021280f49dc3b66ef7c848cd59dccea3"

# 벤더 fixture 경로
FIXTURE_OLD = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "cfp2978" / "sentinel-old-07d1127a.py.txt"

# asset 경로 (실제)
ASSET_PATH = "scripts/lib/check_parallel_work_sentinel.py"

# 상수 (production 코드 값공간)
VERDICTS = ("in-sync", "drifted", "not-applicable", "fetch-failed")
SETUP_ERROR_KINDS = ("pin_missing", "pin_schema_invalid", "empty_assets_without_ssot_role",
                     "not_a_git_repo", "internal")
DEGRADATION_LABELS = ("api_quota_exceeded", "upstream_unreachable", "upstream_payload_invalid")


# ============================================================================
# F-0: Oracle 결속 메타 leg (결속이 깨지면 RED)
# ============================================================================
def test_f0_oracle_bound_to_gate_binary():
    """
    F-0 (결속 메타): 게이트 판정을 **실제로 읽는지** 반증.

    형태: drifted scenario 를 정상 게이트 vs 변이 게이트(무조건 in-sync)로 각각 실행.
    결과가 다르면(drifted vs in-sync) 테스트가 게이트 산출을 읽는 증거.

    변이 게이트는 tmpfile 에 생성 → 테스트 후 정리. 원본은 무변경.
    """
    import shutil

    repo = create_temp_git_repo()
    try:
        # === Setup: drifted scenario (구세대 blob, pin 은 신세대) ===
        assert FIXTURE_OLD.exists(), f"Fixture missing: {FIXTURE_OLD}"
        with open(FIXTURE_OLD, "rb") as f:
            old_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, old_content)

        old_sha = get_blob_sha(repo, ASSET_PATH)
        assert old_sha == BLOB_OLD

        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": BLOB_CURRENT,  # pin points to current, repo has old
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        # === Phase 1: Normal gate ===
        rc_normal, marker_normal, _, _ = run_gate_and_parse(pin_file, repo, offline=True)
        assert rc_normal == 0
        assert marker_normal.get("verdict") == "drifted", \
            f"Normal gate should detect drifted, got {marker_normal.get('verdict')}"

        print(f"\n[F-0 Phase 1: Normal gate]")
        print(f"  Verdict: {marker_normal.get('verdict')}")

        # === Phase 2: Mutated gate ===
        # 게이트 소스를 tmpfile 에 복제
        mutant_fd, mutant_path = tempfile.mkstemp(suffix=".py")
        try:
            with open(GATE_PATH, "r", encoding="utf-8") as f:
                original_code = f.read()

            # 변이: aggregate_verdict 함수가 항상 "in-sync" 반환하도록 변경
            mutated_code = original_code.replace(
                'def aggregate_verdict(assets_out, degraded: bool) -> str:',
                'def aggregate_verdict(assets_out, degraded: bool) -> str:\n    return "in-sync"  # MUTANT: force in-sync'
            )

            # 변이 적중 확인 (변이가 실제로 삽입됐는지)
            assert "MUTANT: force in-sync" in mutated_code, \
                "Mutant injection failed: aggregate_verdict not found"

            # 파일에 쓰고 즉시 close (subprocess 실행 전)
            os.write(mutant_fd, mutated_code.encode("utf-8"))
            os.close(mutant_fd)

            # 변이 게이트로 실행
            cmd = [sys.executable, mutant_path, "--pin-file", pin_file, "--offline"]
            proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)

            rc_mutant = proc.returncode
            marker_mutant = {}
            if proc.stdout.strip():
                try:
                    marker_mutant = parse_marker(proc.stdout.strip().split("\n")[0])
                except ValueError:
                    pass

            assert rc_mutant == 0
            assert marker_mutant.get("verdict") == "in-sync", \
                f"Mutated gate should force in-sync, got {marker_mutant.get('verdict')}"

            print(f"\n[F-0 Phase 2: Mutated gate]")
            print(f"  Verdict: {marker_mutant.get('verdict')}")

            # === Assertion: Discriminating case ===
            assert marker_normal.get("verdict") != marker_mutant.get("verdict"), \
                f"Binding failed: normal={marker_normal.get('verdict')}, mutant={marker_mutant.get('verdict')} (should differ)"

            print(f"\n[F-0 Binding CONFIRMED]")
            print(f"  Normal verdict: {marker_normal.get('verdict')} (q1=mismatch detected)")
            print(f"  Mutant verdict: {marker_mutant.get('verdict')} (injected in-sync)")
            print(f"  Verdicts differ: {marker_normal.get('verdict') != marker_mutant.get('verdict')} [PASS]")
        finally:
            # 변이 사본 정리 (파일이 잠긴 상태면 무시)
            try:
                if os.path.exists(mutant_path):
                    os.unlink(mutant_path)
            except (OSError, PermissionError):
                pass

    finally:
        shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# Helper: subprocess 실행 + 파싱
# ============================================================================
def run_gate(
    pin_file: str,
    cwd: str,
    offline: bool = False,
) -> Tuple[int, str, str]:
    """게이트 서브프로세스 실행. (rc, stdout, stderr) 반환."""
    # ★Windows PATH 처리: absolute path 사용, 쌍슬래시 회피
    gate_abs = str(GATE_PATH.resolve())
    cmd = [sys.executable, gate_abs, "--pin-file", pin_file]
    if offline:
        cmd.append("--offline")

    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def parse_marker(marker_line: str) -> Dict[str, Any]:
    """marker 줄 파싱. 예: `[consumer-asset-currency] determined=true verdict=in-sync assets=1`"""
    # ★verdict 에 하이픈이 있을 수 있음 (in-sync, not-applicable 등)
    # 따라서 \w+ 가 아니라 [\w-]+ 또는 \S+ 를 써야 한다.
    match = re.search(
        r"\[consumer-asset-currency\] determined=(true|false) verdict=([\w-]+) assets=(\d+)",
        marker_line,
    )
    if not match:
        raise ValueError(f"Invalid marker format: {marker_line}")
    return {
        "determined": match.group(1) == "true",
        "verdict": match.group(2),
        "assets": int(match.group(3)),
    }


def run_gate_and_parse(
    pin_file: str,
    cwd: str,
    offline: bool = False,
) -> Tuple[int, Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """게이트 실행 후 stdout/stderr 파싱. (rc, marker_dict, payload_dict, stderr_data) 반환."""
    rc, stdout, stderr = run_gate(pin_file, cwd, offline)

    # stderr JSON (SETUP error) 또는 빈 dict
    stderr_data = {}
    if stderr.strip():
        try:
            stderr_data = json.loads(stderr.strip())
        except json.JSONDecodeError:
            pass

    # stdout 파싱 (성공/degrade 또는 빈 dict)
    marker_dict = {}
    payload_dict = {}
    if stdout.strip():
        lines = stdout.strip().split("\n")
        if len(lines) >= 1:
            try:
                marker_dict = parse_marker(lines[0])
            except ValueError:
                pass
        if len(lines) >= 2:
            try:
                payload_dict = json.loads(lines[1])
            except json.JSONDecodeError:
                pass

    # 우선순위: marker_dict (파싱 성공) > stderr_data (설정 에러) > 빈 dict
    final_marker = marker_dict if marker_dict else stderr_data
    return rc, final_marker, payload_dict, stderr_data


# ============================================================================
# Helper: 임시 git repo 생성
# ============================================================================
def create_temp_git_repo() -> str:
    """임시 git repo 생성. 경로 반환."""
    tmpdir = tempfile.mkdtemp()
    subprocess.run(["git", "init"], cwd=tmpdir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
    # ★Windows blob sha 무결성: CRLF 오염 방지
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=tmpdir, check=True)
    return tmpdir


def write_asset_to_repo(repo_path: str, asset_path: str, content: bytes) -> None:
    """repo 에 asset 을 바이너리로 기록."""
    full_path = Path(repo_path) / asset_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)
    subprocess.run(["git", "add", asset_path], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", f"Add {asset_path}"], cwd=repo_path, check=True)


def get_blob_sha(repo_path: str, asset_path: str) -> str:
    """repo 에서 asset 의 blob sha 조회."""
    proc = subprocess.run(
        ["git", "rev-parse", f"HEAD:{asset_path}"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


# ============================================================================
# C-1: GREEN (신세대 blob, offline Q1 only)
# ============================================================================
def test_c1_currency_match_current_blob():
    """
    C-1 (AC-5): 신세대 blob 으로 in-sync ∧ determined=true ∧ rc=0

    임시 repo 에 현재 worktree 의 asset 내용을 복사 → pin 작성 → 게이트 --offline 실행
    """
    repo = create_temp_git_repo()
    try:
        # 신세대 바이트를 repo 에 기록
        with open(Path(__file__).resolve().parents[2] / ASSET_PATH, "rb") as f:
            current_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, current_content)

        # blob sha 확인
        actual_sha = get_blob_sha(repo, ASSET_PATH)
        assert actual_sha == BLOB_CURRENT, f"Expected {BLOB_CURRENT}, got {actual_sha}"

        # pin 작성
        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": BLOB_CURRENT,
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        # 게이트 실행 (--offline: Q1 only)
        rc, marker, payload, _ = run_gate_and_parse(pin_file, repo, offline=True)

        # 검증
        assert rc == 0, f"C-1 failed: rc should be 0, got {rc}"
        assert marker.get("determined") is True, "C-1 failed: determined should be true"
        assert marker.get("verdict") == "in-sync", f"C-1 failed: verdict should be in-sync, got {marker.get('verdict')}"
        assert payload.get("determined") is True, "C-1 payload: determined should be True"
        assert payload.get("verdict") == "in-sync"

        print("\n[C-1 GREEN] Current blob matches pin:")
        print(f"  Marker: {marker}")
        print(f"  Payload: {json.dumps(payload, indent=2)}")
    finally:
        # cleanup
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# D-2: RED 짝 관측 (가장 중요 — 같은 repo 에서 C-1 green + D-2 red)
# ============================================================================
def test_d2_born_broken_old_blob_paired_observation():
    """
    D-2 (AC-5): C-1 (신세대 in-sync) 과 D-2 (구세대 drifted) 를 같은 임시 repo 에서 연속 관측.

    이것이 게이트의 판정력을 증명하는 핵심이다. 리터럴 dict assert 는 hollow oracle.

    절차:
      1. repo 에 신세대 바이트 기록 → C-1 실행 (green in-sync)
      2. 같은 repo 에서 구세대 바이트로 덮어씀 → D-2 재실행 (red drifted)
      3. blob sha 가 변했고, 판정이 changed 했음을 assert
    """
    repo = create_temp_git_repo()
    try:
        # === Phase 1: C-1 setup (신세대) ===
        with open(Path(__file__).resolve().parents[2] / ASSET_PATH, "rb") as f:
            current_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, current_content)

        current_sha = get_blob_sha(repo, ASSET_PATH)
        assert current_sha == BLOB_CURRENT

        # pin 작성 (신세대 sha 기록)
        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": BLOB_CURRENT,
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        # C-1 GREEN 실행
        rc_c1, marker_c1, payload_c1, _ = run_gate_and_parse(pin_file, repo, offline=True)
        assert rc_c1 == 0, "C-1 phase failed"
        assert marker_c1.get("verdict") == "in-sync"

        print("\n[D-2 Phase 1: C-1 GREEN]")
        print(f"  Blob SHA: {current_sha}")
        print(f"  Verdict: {marker_c1.get('verdict')}")
        print(f"  Payload q1: {payload_c1.get('assets', [{}])[0].get('q1') if payload_c1.get('assets') else 'N/A'}")
        print(f"  Full payload:\n{json.dumps(payload_c1, indent=4)}")

        # === Phase 2: D-2 setup (구세대로 덮어씀) ===
        assert FIXTURE_OLD.exists(), f"Fixture missing: {FIXTURE_OLD}"
        with open(FIXTURE_OLD, "rb") as f:
            old_content = f.read()

        # 같은 경로에 구세대 바이트 기록
        full_path = Path(repo) / ASSET_PATH
        with open(full_path, "wb") as f:
            f.write(old_content)
        subprocess.run(["git", "add", ASSET_PATH], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "Revert to old blob"], cwd=repo, check=True)

        old_sha = get_blob_sha(repo, ASSET_PATH)
        assert old_sha == BLOB_OLD, f"Expected {BLOB_OLD}, got {old_sha}"

        # pin 은 여전히 신세대 sha 를 가리킴 (변경 안 함)
        # → q1=mismatch (local_sha=old != pin_sha=current) → verdict=drifted

        # D-2 RED 실행
        rc_d2, marker_d2, payload_d2, _ = run_gate_and_parse(pin_file, repo, offline=True)
        assert rc_d2 == 0, "D-2 phase failed"
        assert marker_d2.get("verdict") == "drifted", f"D-2 should be drifted, got {marker_d2.get('verdict')}"

        print("\n[D-2 Phase 2: D-2 RED]")
        print(f"  Blob SHA: {old_sha}")
        print(f"  Verdict: {marker_d2.get('verdict')}")
        print(f"  Payload q1: {payload_d2.get('assets', [{}])[0].get('q1') if payload_d2.get('assets') else 'N/A'}")
        print(f"  Full payload:\n{json.dumps(payload_d2, indent=4)}")

        # === Assertion: C-1 green != D-2 red ===
        assert marker_c1.get("verdict") != marker_d2.get("verdict"), \
            "Paired oracle failed: C-1 and D-2 verdicts must differ"
        assert payload_c1.get("assets", [{}])[0].get("q1") == "match"
        assert payload_d2.get("assets", [{}])[0].get("q1") == "mismatch"

        print("\n[D-2 Paired Observation SUCCESS]")
        print(f"  C-1: {marker_c1.get('verdict')} (q1={payload_c1.get('assets', [{}])[0].get('q1')})")
        print(f"  D-2: {marker_d2.get('verdict')} (q1={payload_d2.get('assets', [{}])[0].get('q1')})")

    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# C-2: 구세대 blob (독립 실행)
# ============================================================================
def test_c2_currency_mismatch_old_blob():
    """
    C-2 (AC-5): 구세대 blob 으로 drifted (독립 실행)

    pin 은 신세대 sha, repo 에는 구세대 바이트 → q1=mismatch → verdict=drifted
    """
    repo = create_temp_git_repo()
    try:
        # 구세대 바이트 기록
        assert FIXTURE_OLD.exists()
        with open(FIXTURE_OLD, "rb") as f:
            old_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, old_content)

        old_sha = get_blob_sha(repo, ASSET_PATH)
        assert old_sha == BLOB_OLD

        # pin 은 신세대 sha 기록
        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": BLOB_CURRENT,  # pin points to current, repo has old
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        rc, marker, payload, _ = run_gate_and_parse(pin_file, repo, offline=True)

        assert rc == 0
        assert marker.get("verdict") == "drifted"
        assert payload.get("verdict") == "drifted"
        assert payload.get("assets", [{}])[0].get("q1") == "mismatch"

        print(f"\n[C-2] Old blob detected as drifted:")
        print(f"  Local: {old_sha}, Pin: {BLOB_CURRENT}")
        print(f"  Verdict: {marker.get('verdict')}")
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# D-1: Degrade (in-process HTTP monkeypatch)
# ============================================================================
def test_d1_degrade_quota_exceeded_with_contrast():
    """
    D-1 (AC-5): HTTP 429 quota → determined absent + degradation=api_quota_exceeded ∧ rc=0

    in-process monkeypatch 는 이 test 만 허용. HTTP 함수만 mock 하고 하류는 실코드.

    ★대조군 필수: 같은 test 안에서 정상 response (determined 존재) 도 assert.
    미 대조군 = 판별력 없음 (hollow oracle).
    """
    # 게이트 모듈 로드
    spec = importlib.util.spec_from_file_location("check_consumer_asset_currency", GATE_PATH)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    repo = create_temp_git_repo()
    try:
        # repo setup (신세대)
        with open(Path(__file__).resolve().parents[2] / ASSET_PATH, "rb") as f:
            current_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, current_content)

        current_sha = get_blob_sha(repo, ASSET_PATH)

        # pin 작성
        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": current_sha,
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        # load pin
        pin_raw = gate.load_pin(pin_file)
        pin = gate.validate_pin(pin_raw)
        root = repo

        # === Stub 1: 429 quota ===
        original_http_get = gate._http_get_listing

        def stub_quota(*args, **kwargs):
            return {
                "entries": None,
                "degradation": "api_quota_exceeded",
                "status_code": 429,
                "ratelimit_reset": "1692057600",
                "auth_rejected": False,
            }

        gate._http_get_listing = stub_quota
        result_degrade = gate.evaluate(pin, root, offline=False)
        payload_degrade = result_degrade["payload"]

        assert "determined" not in payload_degrade, "Degrade: determined key must be absent"
        assert payload_degrade.get("degradation") == "api_quota_exceeded"
        assert payload_degrade.get("verdict") == "fetch-failed"
        assert payload_degrade.get("status_code") == 429

        print(f"\n[D-1 Stub Quota]")
        print(f"  Degradation: {payload_degrade.get('degradation')}")
        print(f"  Verdict: {payload_degrade.get('verdict')}")
        print(f"  determined absent: {'determined' not in payload_degrade}")
        print(f"  Payload:\n{json.dumps(payload_degrade, indent=4)}")

        # === Contrast: Normal response ===
        def stub_normal(*args, **kwargs):
            # 정상 listing response mock (구조만, 실제 content 없어도 된다)
            return {
                "entries": [
                    {
                        "sha": current_sha,
                        "name": "check_parallel_work_sentinel.py",
                        "path": ASSET_PATH,
                        "type": "file",
                    }
                ],
                "degradation": None,
                "status_code": 200,
                "ratelimit_reset": None,
                "auth_rejected": False,
            }

        gate._http_get_listing = stub_normal
        result_normal = gate.evaluate(pin, root, offline=False)
        payload_normal = result_normal["payload"]

        assert payload_normal.get("determined") is True, "Normal: determined should be True"
        assert payload_normal.get("verdict") == "in-sync"

        print(f"\n[D-1 Contrast Normal]")
        print(f"  Verdict: {payload_normal.get('verdict')}")
        print(f"  determined present: {payload_normal.get('determined')}")
        print(f"  Payload:\n{json.dumps(payload_normal, indent=4)}")

        # Restore
        gate._http_get_listing = original_http_get

    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# Setup errors
# ============================================================================
def test_failure_pin_missing():
    """pin 파일 부재 → rc=2, error_kind=pin_missing"""
    repo = create_temp_git_repo()
    try:
        # pin 파일을 의도적으로 만들지 않음
        pin_file = os.path.join(repo, ".nonexistent-pin.json")

        rc, _, _, stderr_data = run_gate_and_parse(pin_file, repo)

        assert rc == 2, f"rc should be 2, got {rc}"
        assert stderr_data.get("error_kind") == "pin_missing"

        print(f"\n[pin_missing] rc={rc}, error_kind={stderr_data.get('error_kind')}")
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


def test_failure_pin_schema_invalid():
    """Invalid pin schemas → rc=2, error_kind=pin_schema_invalid"""
    invalid_schemas = [
        {},  # missing schema_version
        {"schema_version": 1},  # missing role
        {"schema_version": 1, "role": "consumer"},  # missing assets
        {"schema_version": 1, "role": "invalid_role", "assets": []},  # invalid role
        {"schema_version": 1, "role": "consumer", "assets": "not_list"},  # assets not list
        {
            "schema_version": 1,
            "role": "consumer",
            "assets": [{"path": "test.txt", "blob_sha": "invalid"}],
        },  # bad blob_sha
    ]

    repo = create_temp_git_repo()
    try:
        for i, invalid_pin in enumerate(invalid_schemas):
            pin_file = os.path.join(repo, f"invalid_pin_{i}.json")
            with open(pin_file, "w") as f:
                json.dump(invalid_pin, f)

            rc, _, _, stderr_data = run_gate_and_parse(pin_file, repo)
            assert rc == 2, f"Schema {i}: rc should be 2"
            assert stderr_data.get("error_kind") == "pin_schema_invalid"

        print(f"\n[pin_schema_invalid] {len(invalid_schemas)} invalid schemas detected")
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


def test_failure_empty_assets_without_ssot_role():
    """role=consumer 인데 assets=[] → rc=2, error_kind=empty_assets_without_ssot_role"""
    repo = create_temp_git_repo()
    try:
        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "assets": [],  # consumer 인데 assets 비어있음
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        rc, _, _, stderr_data = run_gate_and_parse(pin_file, repo)

        assert rc == 2
        assert stderr_data.get("error_kind") == "empty_assets_without_ssot_role"

        print(f"\n[empty_assets_without_ssot_role] rc={rc}")
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


def test_failure_not_a_git_repo():
    """비-git 디렉토리에서 실행 → rc=2, error_kind=not_a_git_repo"""
    tmpdir = tempfile.mkdtemp()
    try:
        # git init 하지 않음
        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": "dummy.txt",
                    "blob_sha": "c372d0521db5d996ea9288bd362b83486e1e2553",
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(tmpdir, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        rc, _, _, stderr_data = run_gate_and_parse(pin_file, tmpdir)

        assert rc == 2
        assert stderr_data.get("error_kind") == "not_a_git_repo"

        print(f"\n[not_a_git_repo] rc={rc}")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


# ============================================================================
# Not-applicable (wrapper self-app)
# ============================================================================
def test_gate_not_applicable_wrapper_ssot():
    """role=ssot ∧ assets=[] → verdict=not-applicable ∧ rc=0 ∧ determined=True"""
    repo = create_temp_git_repo()
    try:
        pin_data = {
            "schema_version": 1,
            "role": "ssot",
            "assets": [],  # ssot 는 assets 비어도 OK
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        rc, marker, payload, _ = run_gate_and_parse(pin_file, repo)

        assert rc == 0
        assert marker.get("verdict") == "not-applicable"
        assert payload.get("verdict") == "not-applicable"
        assert payload.get("determined") is True
        assert payload.get("assets_checked") == 0

        print(f"\n[not-applicable] wrapper ssot: rc={rc}, verdict={marker.get('verdict')}")
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# D-3: Static shape analysis (workflow 구조 검증)
# ============================================================================
def test_d3_consumer_execution_gate_static_shape():
    """
    D-3 (AC-5): 게이트가 consumer CI 에서 실행됨을 static 검증.

    존재-lint 는 금지. 대신:
      1. workflow YAML 파싱
      2. job_id, step_if, job_if 구조 검증
      3. currency job 이 조건부 실행 없음 확인
    """
    from scripts.lib import workflow_shape

    workflow_path = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "consumer-asset-currency-check.yml"
    )

    assert workflow_path.exists(), f"Workflow not found: {workflow_path}"

    # workflow 로드 (WorkflowShape dataclass)
    shape = workflow_shape.load_workflow_shape(str(workflow_path))

    # 게이트 job 을 찾는다
    gate_job_found = False
    for job_id in shape.job_ids:
        if "currency" in job_id:
            gate_job_found = True
            # job 이 조건부 실행 없어야 한다 (job_if[job_id] == None)
            assert shape.job_if.get(job_id) is None, \
                f"Job {job_id} should not have job-level if condition"

            # step 수준 if 도 없어야 한다
            # shape.step_if[job_id] 는 list of step if 값들
            step_ifs = shape.step_if.get(job_id, [])
            for i, step_if_value in enumerate(step_ifs):
                assert step_if_value is None, \
                    f"Job {job_id} step[{i}] should not have if condition, got {step_if_value}"

            break

    assert gate_job_found, f"Currency gate job not found in workflow. Available: {shape.job_ids}"
    print(f"\n[D-3 Static] Currency gate job found in workflow shape")
    print(f"  Job IDs: {shape.job_ids}")


# ============================================================================
# 출력 필드 구조 검증 (실행 기반)
# ============================================================================
def test_output_field_structure_success():
    """성공 verdict (in-sync/drifted/not-applicable) 의 필드 구조 검증"""
    repo = create_temp_git_repo()
    try:
        # 신세대 setup
        with open(Path(__file__).resolve().parents[2] / ASSET_PATH, "rb") as f:
            current_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, current_content)

        current_sha = get_blob_sha(repo, ASSET_PATH)

        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": current_sha,
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        rc, marker, payload, _ = run_gate_and_parse(pin_file, repo, offline=True)

        # in-sync 필드 구조 검증
        assert "determined" in payload
        assert "verdict" in payload
        assert "role" in payload
        assert "assets_checked" in payload
        assert "assets" in payload
        assert isinstance(payload["assets"], list)

        if payload["assets"]:
            asset = payload["assets"][0]
            assert "path" in asset
            assert "local_sha" in asset
            assert "pin_sha" in asset
            assert "remote_sha" in asset
            assert "q1" in asset
            assert "q2" in asset

        print(f"\n[Field Structure] Success payload validated")
        print(f"  Keys: {list(payload.keys())}")
        print(f"  Asset keys: {list(payload['assets'][0].keys()) if payload['assets'] else 'empty'}")
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


def test_output_field_structure_degrade():
    """degrade 시 필드 구조 검증"""
    spec = importlib.util.spec_from_file_location("check_consumer_asset_currency", GATE_PATH)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    repo = create_temp_git_repo()
    try:
        with open(Path(__file__).resolve().parents[2] / ASSET_PATH, "rb") as f:
            current_content = f.read()
        write_asset_to_repo(repo, ASSET_PATH, current_content)

        current_sha = get_blob_sha(repo, ASSET_PATH)

        pin_data = {
            "schema_version": 1,
            "role": "consumer",
            "source_repo": "wrapper/plugin-codeforge",
            "assets": [
                {
                    "path": ASSET_PATH,
                    "blob_sha": current_sha,
                    "pinned_at": "2026-08-15T00:00:00Z",
                    "pinned_by_story": "CFP-2978",
                }
            ],
        }
        pin_file = os.path.join(repo, ".codeforge-asset-pins.json")
        with open(pin_file, "w") as f:
            json.dump(pin_data, f)

        pin_raw = gate.load_pin(pin_file)
        pin = gate.validate_pin(pin_raw)
        root = repo

        # stub degrade
        original = gate._http_get_listing
        gate._http_get_listing = lambda *a, **k: {
            "entries": None,
            "degradation": "upstream_unreachable",
            "status_code": 500,
            "ratelimit_reset": None,
            "auth_rejected": False,
        }

        result = gate.evaluate(pin, root, offline=False)
        payload = result["payload"]

        # degrade 필드 구조
        assert "determined" not in payload, "Degrade: determined must be absent"
        assert "degradation" in payload
        assert "status_code" in payload
        assert payload["degradation"] in ("api_quota_exceeded", "upstream_unreachable", "upstream_payload_invalid")

        print(f"\n[Field Structure] Degrade payload validated")
        print(f"  Keys: {list(payload.keys())}")
        print(f"  determined absent: {'determined' not in payload}")

        gate._http_get_listing = original
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
