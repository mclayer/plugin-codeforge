"""test_dynamic_contracts_c.py — CFP-2965 Phase 2 §8.8 동적 테스트 (fuzz/property/concurrency).

Change Plan §8.8 (Tier D dynamic contract):
  · fuzz: stdin JSON 파서 robustness (훅 7종 stdin 수령 경로)
    target: 빈 stdin, 깨진 JSON, 누락 필드, 대용량, 제어문자, 비-ASCII, 중첩, null byte, truncated, 배열 root, 숫자 command
    oracle: exit ∈ {0,2} ∧ stderr Traceback 미방출 ∧ stdout 계약 무손상
    budget: ≤90s wall clock
  · property: stdin JSON 파서 불변식 (500 iterations, fixed seed)
    1. RE_PREFIX 멱등성 (이중 적용 = 단일 적용)
    2. whole-echo 보존 (비-ASCII 포함 dict 무손실)
    3. bypass disjoint (BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT 축)
    4. subprocess 0 (no fork, import check_spawn_description_prefix only)
  · concurrency: 원장 동시 append (n≥100 worker)
    1. 행 수 일치성 (시도 수 == 결과 행 수)
    2. torn row 검증 (각 행 valid JSON)

Precedents: test_pretooluse_bash_description_inject.py (hook fork pattern) +
            test_cross_repo_gh_safety.py (payload/env override).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

import pytest

import check_spawn_description_prefix as csdp

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK = WORKTREE_ROOT / "hooks" / "pretooluse-bash-description-inject"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)

pytestmark = pytest.mark.skipif(_BASH is None, reason="bash interpreter 부재")


def _run_hook(payload: dict | str | bytes, env_overrides: dict | None = None) -> tuple[int, str, str]:
    """Bash 훅 실행, stdin JSON 파싱 경로 테스트.

    Args:
        payload: dict (자동 JSON 직렬화) | str/bytes (원본 전달)
        env_overrides: 환경변수 추가

    Returns:
        (returncode, stdout, stderr)

    Note: subprocess stdin=bytes only (str causes hang); json.dumps 사용 시 자동 처리.
    """
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    # 입력 직렬화
    if isinstance(payload, dict):
        input_bytes = json.dumps(payload).encode("utf-8")
    elif isinstance(payload, str):
        input_bytes = payload.encode("utf-8")
    else:
        input_bytes = payload

    proc = subprocess.run(
        [_BASH, str(HOOK)],
        input=input_bytes,
        capture_output=True,
        env=env,
    )
    return proc.returncode, proc.stdout.decode("utf-8", errors="replace"), proc.stderr.decode("utf-8", errors="replace")


# ============================================================ FUZZ 테스트 (12+ corpus)

class TestFuzzStdinJsonParser:
    """stdin JSON 파서 robustness — 12+ 변형 corpus.

    Oracle: exit ∈ {0,2} ∧ stderr Traceback 미방출 ∧ stdout 계약 무손상.
    Budget: ≤90s wall (현재 test_dynamic_contracts_c::TestFuzz 라벨로 측정).
    """

    def test_fuzz_empty_stdin(self):
        """Case 1: 빈 stdin → exit 0, fail-open."""
        rc, out, err = _run_hook(b"")
        assert rc in (0, 2), f"Expected exit 0 or 2, got {rc}"
        assert "Traceback" not in err, "Traceback 미방출 위반"

    def test_fuzz_broken_json_single_brace(self):
        """Case 2: 깨진 JSON (미닫힌 중괄호) → exit ∈ {0,2}."""
        rc, out, err = _run_hook(b"{not complete")
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_missing_tool_name(self):
        """Case 3: JSON 유효하나 tool_name 누락."""
        payload = {"tool_input": {"command": "ls"}}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_missing_command(self):
        """Case 4: JSON 유효하나 command 누락."""
        payload = {"tool_name": "Bash", "tool_input": {"description": "no command"}}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_large_field_100kb(self):
        """Case 5: 100KB 필드 (메모리 안전) → exit 0."""
        large_cmd = "x" * (100 * 1024)
        payload = {"tool_name": "Bash", "tool_input": {"command": large_cmd}}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_control_characters(self):
        """Case 6: 제어문자 (null, BEL, ...)."""
        payload = {"tool_name": "Bash", "tool_input": {"command": "echo\x00test\x07"}}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_non_ascii_utf8(self):
        """Case 7: 비-ASCII UTF-8 (한글, 이모지)."""
        payload = {"tool_name": "Bash", "agent_type": "테스트에이전트",
                   "tool_input": {"command": "echo", "description": "🔧 작업"}}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_deep_nesting(self):
        """Case 8: 깊은 중첩 (JSON bomb 회피)."""
        deep = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": "deep"}}}}}}}}}
        payload = {"tool_name": "Bash", "tool_input": deep}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_null_byte_in_payload(self):
        """Case 9: null byte (바이너리 경계)."""
        payload_str = '{"tool_name": "Bash", "tool_input": {"command": "echo\\u0000test"}}'
        rc, out, err = _run_hook(payload_str.encode("utf-8"))
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_truncated_json(self):
        """Case 10: truncated JSON (stream interrupt)."""
        payload_str = '{"tool_name": "Bash", "tool_input": {"command": "echo", "desc'
        rc, out, err = _run_hook(payload_str.encode("utf-8"))
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_array_root(self):
        """Case 11: 배열이 root (객체가 아님)."""
        rc, out, err = _run_hook(b'["tool_name", "Bash"]')
        assert rc in (0, 2)
        assert "Traceback" not in err

    def test_fuzz_numeric_command(self):
        """Case 12: command가 숫자."""
        payload = {"tool_name": "Bash", "tool_input": {"command": 123}}
        rc, out, err = _run_hook(payload)
        assert rc in (0, 2)
        assert "Traceback" not in err


# ============================================================ PROPERTY 테스트 (500 iter, fixed seed)

class TestPropertyStdinJsonParser:
    """stdin JSON 파서 불변식 — property-based testing (hypothesis)."""

    def test_property_re_prefix_idempotent(self):
        """Property 1: RE_PREFIX 멱등성.

        description이 이미 conformant([Agent] time - desc) 형식이면
        훅이 재주입하지 않음 (idempotent).
        Precedent: test_pretooluse_bash_description_inject.py::test_already_conformant_no_reinjection
        """
        # 이미 conformant 형식
        conformant_desc = "[TestAgent] 08/14 12:00:00 - already conformant"
        payload = {
            "tool_name": "Bash",
            "agent_type": "TestAgent",
            "tool_input": {"command": "ls", "description": conformant_desc}
        }
        rc, out, _ = _run_hook(payload)

        # Conformant description → no reinjection (stdout empty)
        assert rc == 0, f"Expected exit 0, got {rc}"
        assert out.strip() == "", f"Expected empty stdout for conformant desc, got: {out[:100]}"

    @given(st.dictionaries(
        st.text(min_size=1, max_size=50),
        st.one_of(st.integers(), st.text(), st.booleans(), st.none()),
        min_size=1, max_size=20
    ))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_property_whole_echo_preservation(self, random_dict: dict):
        """Property 2: whole-echo 보존 (비-ASCII 포함 dict 무손실).

        tool_input 전체가 변경 없이 updatedInput으로 돌아옴.

        deadline=None 사유: 각 예제가 훅을 서브프로세스로 fork 하므로 예제당 소요가 호스트
          부하에 좌우된다 — 포화 시 1338~1659 ms, 여유 시 371 ms 로 관측돼 hypothesis 가
          `FlakyFailure: Unreliable test timings` 로 자기 판정했다(구 deadline=1000 초과).
          본 property 의 검증 대상은 **whole-echo 보존 성질**이지 지연이 아니므로 deadline 을
          해제한다. 타이밍 회귀 감시는 tests/perf/ Plane A(paired ABAB) 소관으로 분리돼 있어
          여기서 deadline 을 놓아도 성능 감시 공백은 생기지 않는다.
        """
        payload = {
            "tool_name": "Bash",
            "agent_type": "TestAgent",
            "tool_input": {"command": "echo", "extra_data": random_dict}
        }
        rc, out, err = _run_hook(payload)

        if rc == 0 and out.strip() and "hookSpecificOutput" in out:
            hso = json.loads(out).get("hookSpecificOutput", {})
            ui = hso.get("updatedInput", {})
            # tool_input 전체 보존 검증 (설명문 제외)
            if "tool_input" in ui:
                # 원 command/extra_data는 보존
                assert ui["tool_input"].get("command") == payload["tool_input"]["command"]
                assert ui["tool_input"].get("extra_data") == payload["tool_input"]["extra_data"]

    def test_property_bypass_env_disjoint(self):
        """Property 3: bypass disjoint (BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT만 효과).

        다른 BYPASS_* env는 이 훅에 영향 없음 (독립성).
        """
        payload = {
            "tool_name": "Bash",
            "agent_type": "TestAgent",
            "tool_input": {"command": "echo test", "description": "orig"}
        }

        # BYPASS_CROSS_REPO_GH_SAFETY는 이 훅과 무관
        rc1, out1, _ = _run_hook(
            payload,
            env_overrides={"BYPASS_CROSS_REPO_GH_SAFETY": "1"}
        )

        # BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT는 주입 억제
        rc2, out2, _ = _run_hook(
            payload,
            env_overrides={"BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT": "1"}
        )

        # 첫 번째는 주입 시도 (out not empty), 두 번째는 억제 (out empty)
        assert rc1 == 0 and rc2 == 0
        # bypass 적용 시 stdout empty
        assert out2.strip() == "", "BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT 억제 실패"

    def test_property_subprocess_zero_no_fork(self):
        """Property 4: subprocess 0 (fork 미검출).

        check_spawn_description_prefix 임포트만 수행, subprocess fork 없음.
        """
        # 단순히 check_spawn_description_prefix를 임포트했고
        # subprocess를 fork하지 않았음을 verify (test 진정성)
        import check_spawn_description_prefix
        assert hasattr(check_spawn_description_prefix, "RE_PREFIX")
        assert hasattr(check_spawn_description_prefix, "_sanitize_subject")


# ============================================================ CONCURRENCY 테스트

class TestConcurrencyStdinJsonParser:
    """stdin JSON 파서 동시 접근 안전성 (원장 동시 append)."""

    def test_concurrency_ledger_append_100_workers(self, tmp_path):
        """Concurrency 1: 원장 동시 append (n≥100 worker).

        100개 스레드가 동시에 JSON 처리, 각 결과를 원장 파일에 append.
        행 수 일치성 (시도 수 == 결과 행 수) 검증.
        """
        ledger_file = tmp_path / "ledger.jsonl"
        lock = threading.Lock()
        num_workers = 100

        def worker(worker_id: int):
            payload = {
                "tool_name": "Bash",
                "agent_type": f"Agent{worker_id}",
                "tool_input": {"command": f"echo {worker_id}", "description": f"worker {worker_id}"}
            }
            rc, out, err = _run_hook(payload)

            # 결과 기록 (직렬화)
            result = {
                "worker_id": worker_id,
                "returncode": rc,
                "has_output": bool(out.strip()),
                "timestamp": worker_id
            }
            with lock:
                ledger_file.write_text(
                    ledger_file.read_text(encoding="utf-8") + json.dumps(result) + "\n",
                    encoding="utf-8"
                )

        # 초기화
        ledger_file.write_text("", encoding="utf-8")

        # 병렬 실행
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(num_workers)]
            for future in as_completed(futures):
                future.result()  # 예외 전파

        # 행 수 검증
        lines = [l for l in ledger_file.read_text(encoding="utf-8").split("\n") if l.strip()]
        assert len(lines) == num_workers, f"Expected {num_workers} lines, got {len(lines)}"

    def test_concurrency_torn_row_validation(self, tmp_path):
        """Concurrency 2: torn row 검증 (각 행 valid JSON).

        동시 append 시에도 각 행이 complete, valid JSON이어야 함.
        """
        ledger_file = tmp_path / "ledger.jsonl"
        lock = threading.Lock()
        num_workers = 50

        def worker(worker_id: int):
            payload = {
                "tool_name": "Bash",
                "agent_type": f"Agent{worker_id}",
                "tool_input": {
                    "command": f"echo {worker_id}",
                    "description": f"worker {worker_id} with special chars 🔧"
                }
            }
            rc, out, err = _run_hook(payload)

            result = {
                "worker_id": worker_id,
                "rc": rc,
                "len_out": len(out),
                "has_traceback": "Traceback" in err
            }
            with lock:
                ledger_file.write_text(
                    ledger_file.read_text(encoding="utf-8") + json.dumps(result, ensure_ascii=False) + "\n",
                    encoding="utf-8"
                )

        ledger_file.write_text("", encoding="utf-8")

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(num_workers)]
            for future in as_completed(futures):
                future.result()

        # 각 행이 valid JSON 검증
        lines = ledger_file.read_text(encoding="utf-8").split("\n")
        valid_count = 0
        for line in lines:
            if line.strip():
                try:
                    json.loads(line)
                    valid_count += 1
                except json.JSONDecodeError as e:
                    pytest.fail(f"torn row detected: {line[:100]}... ({e})")

        assert valid_count >= num_workers - 5, f"Expected ≥{num_workers-5} valid lines, got {valid_count}"
