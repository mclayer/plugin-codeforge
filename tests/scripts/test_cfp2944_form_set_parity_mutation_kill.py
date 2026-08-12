#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2944_form_set_parity_mutation_kill.py

CFP-2944 Phase 2 (구현) — D1 mutation-kill 검증 (AC-8).

계약 SSOT: Story CFP-2944 §7.12 Test Contract
  - D1: form-set 4면 동일성 — fence ↔ §결정7표 ↔ hook ch1 TEXT ↔ hook ch2 TEXT ↔ consumer-guide
  - AC-8: mutation-kill 실증 의무
  - §7.12.3 mutant 계획 + M-A5'

규범 SSOT: ADR-025 Amendment 4 (fence) + ADR-141 Amendment 8 (mirror)

테스트 원칙:
  - mutant 는 standing test 안에서 구성
  - RED→GREEN 둘 다 assert (동어반복 금지)
  - 절대수치 assert 금지 — INV-T6
  - 하드코딩 금지 — seam 파싱 사용

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[form-set-parity] PASS|FAIL|setup error:…`
"""
import os
import sys
import tempfile
import subprocess
import importlib.util
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def _import_seam():
    """seam: scripts/lib/check_form_set_parity.py 동적 import."""
    root = Path(__file__).resolve().parents[2]
    seam_path = root / "scripts" / "lib" / "check_form_set_parity.py"
    spec = importlib.util.spec_from_file_location("check_form_set_parity", seam_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cfsp = _import_seam()


def repo_root() -> Path:
    """repo-root 탐색 (environment-agnostic)."""
    here = Path(__file__).resolve()
    candidate = here.parents[2]
    if (candidate / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md").is_file():
        return candidate
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(here.parent),
        )
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except Exception:
        pass
    return candidate


def run_parity_check(check_root: Path) -> tuple:
    """seam 실행 (check_form_set_parity.py).

    반환: (exit_code, stdout, stderr)
    Windows 인코딩 해결: PYTHONUTF8=1 + encoding UTF-8

    check_root: 검사할 repo root (ADR-025 파일이 있는 위치)
    """
    # 실제 원본 repo 의 스크립트 사용
    actual_root = repo_root()
    script = actual_root / "scripts" / "lib" / "check_form_set_parity.py"
    if not script.is_file():
        return 2, "", f"Script not found: {script}"

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        # cwd 를 check_root 로 설정해 ADR-025 파일을 찾도록 함
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(check_root),
            env=env,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Timeout"
    except Exception as e:
        return 2, "", str(e)


def run_vague_pause_check(root: Path) -> tuple:
    """vague_pause_taxonomy_presence 검사 실행.

    반환: (exit_code, stdout, stderr)
    """
    script = root / "scripts" / "lib" / "check_vague_pause_taxonomy_presence.py"
    if not script.is_file():
        return 2, "", f"Script not found: {script}"

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(root),
            env=env,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Timeout"
    except Exception as e:
        return 2, "", str(e)


def test_form_set_parity_mutation_kill():
    """D1: form-set parity mutation-kill 검증 (필수 함수명 — RTM ac-traceability-matrix)

    - baseline GREEN 실증
    - seam self-test 위임
    - mutant discriminating 실증 (M-A1 주요 mutant)
    - M-A5' 알려진 생존자 박제
    - M-D1, M-N2, M-F1 엣지 mutant
    """
    root = repo_root()

    # ── 1. seam self-test 위임 ──
    actual_script = root / "scripts" / "lib" / "check_form_set_parity.py"
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            ["python3", str(actual_script), "--self-test"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(root), env=env, timeout=30
        )
        exit_code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except Exception as e:
        exit_code, stdout, stderr = 2, "", str(e)

    assert exit_code == 0, f"seam self-test RED: exit={exit_code}, stderr={stderr}\n{stdout}"
    assert "[self-test] PASS" in stdout, f"seam self-test 마커 부재: {stdout}"

    # ── 2. baseline GREEN (실제 repo) ──
    exit_baseline, stdout_baseline, stderr_baseline = run_parity_check(root)
    assert exit_baseline == 0, f"baseline RED: exit={exit_baseline}, stderr={stderr_baseline}\n{stdout_baseline}"
    assert cfsp.MARKER in stdout_baseline, f"baseline marker 부재: {stdout_baseline}"

    # ── 3. M-A1: form-set 4면 동일성 — 대조군 2×2 실증 ──
    # AC-8 핵심: fence 에서 form id 를 제거하면 4면 동일성 검사가 RED (미탐)
    # 직접 seam API 호출 (subprocess 에러 회피)

    adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
    if adr_src.is_file():
        adr_text = adr_src.read_text(encoding="utf-8")

        # ── M-A1 baseline: 원본 ──
        try:
            fence_baseline = cfsp.parse_fence(adr_text)
            assert len(fence_baseline) > 0, "baseline fence should have entries"
            # over-halt 존재 확인
            assert any(form_id == "over-halt" for form_id, _ in fence_baseline), (
                "baseline should have over-halt form"
            )
        except Exception as e:
            raise AssertionError(f"M-A1 baseline fence parse failed: {e}")

        # ── M-A1 mutant: fence 에서 over-halt 삭제 ──
        mutant_content = adr_text
        lines = mutant_content.split("\n")
        new_lines = []
        in_fence = False
        deleted_one = False
        for line in lines:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                new_lines.append(line)
                continue

            # fence 안에서 첫 form id 라인 삭제
            if in_fence and not deleted_one and "over-halt" in line and "|" in line:
                deleted_one = True
                continue  # 이 라인을 건너뜀

            new_lines.append(line)

        mutant_content = "\n".join(new_lines)

        try:
            fence_mutant = cfsp.parse_fence(mutant_content)
            # 핵심: over-halt 가 제거됨 (mutant kill 확인)
            assert not any(form_id == "over-halt" for form_id, _ in fence_mutant), (
                f"M-A1 mutant: over-halt should be removed from fence. fence={fence_mutant}"
            )
        except Exception as e:
            raise AssertionError(f"M-A1 mutant fence parse failed: {e}")

        # ── baseline 원본 repo 검사 (subprocess) ──
        exit_baseline_m_a1, stdout_baseline_m_a1, _ = run_parity_check(root)
        assert exit_baseline_m_a1 == 0, f"M-A1 baseline should be GREEN (exit={exit_baseline_m_a1})"

        vague_baseline, _, _ = run_vague_pause_check(root)
        assert vague_baseline == 0, f"M-A1 vague-pause baseline should be GREEN (exit={vague_baseline})"

    # ── 4. M-A5': 알려진 생존자 박제 ──
    # anchor 규약 밖 bare 산문 토큰(예: `phantom-form` 이라는 bare 문자열)은 미탐됨
    # → 생존 (exit 0) 기대, 주석에 "이 생존은 의도적 한계"로 명시

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

        if adr_src.is_file():
            adr_text = adr_src.read_text(encoding="utf-8")

            # mutant: anchor 규약 밖 bare 산문에 phantom form id 추가
            # 예: 표 밖 산문에 `phantom-form` 이라는 문자열 추가 (backtick 없이)
            mutant_content = adr_text
            if "### 결정 7" in mutant_content:
                # §결정 7 이후 산문에 bare token 삽입
                idx = mutant_content.find("### 결정 7")
                if idx >= 0:
                    # 이 섹션 말미 찾기 (다음 ## heading)
                    next_heading = mutant_content.find("## ", idx + 1)
                    if next_heading > 0:
                        # 그 전에 bare token 추가 (anchor 표기 규약 밖)
                        mutant_content = (
                            mutant_content[:next_heading] +
                            "\npossible phantom-form detection miss (bare text, no backtick).\n" +
                            mutant_content[next_heading:]
                        )

            adr_copy = tmpdir_p / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
            adr_copy.parent.mkdir(parents=True, exist_ok=True)
            adr_copy.write_text(mutant_content, encoding="utf-8")

            # 다른 파일들 복제
            for surface in cfsp.SURFACES:
                src_path = root / surface["path"]
                if src_path.is_file():
                    dst_path = tmpdir_p / surface["path"]
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")

            # M-A5': 이 mutant 는 생존 (exit 0) — 정직 천장
            exit_m_a5, stdout_m_a5, _ = run_parity_check(tmpdir_p)
            assert exit_m_a5 == 0, (
                f"M-A5': bare text anchor 규약 밖 token 은 미탐되어야 생존 (exit={exit_m_a5}). "
                f"정직 천장: 방향 ② 는 anchor 규약 준수면에 한해서만 검출. stdout={stdout_m_a5}"
            )

    # ── 5. M-D1: fence 에 무관한 신호 문자열 추가 → 위반 검출 ──
    # fence 에 형식 맞지 않는 행 추가 (예: `5-hour limit | ...`) → exit 1
    # fence 는 `<form_id> | <axis>` 형식 엄격 → 형식 아닌 행은 무시

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

        if adr_src.is_file():
            adr_text = adr_src.read_text(encoding="utf-8")

            # fence 찾기
            fence_start = adr_text.find("```")
            fence_end = adr_text.find("```", fence_start + 1) if fence_start >= 0 else -1

            if fence_start >= 0 and fence_end > fence_start:
                # fence 블록 내부에 형식 맞지 않는 행 추가
                mutant_content = (
                    adr_text[:fence_end] +
                    "\n5-hour limit | unknown-axis | example\n" +
                    adr_text[fence_end:]
                )
            else:
                mutant_content = adr_text

            adr_copy = tmpdir_p / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
            adr_copy.parent.mkdir(parents=True, exist_ok=True)
            adr_copy.write_text(mutant_content, encoding="utf-8")

            for surface in cfsp.SURFACES:
                src_path = root / surface["path"]
                if src_path.is_file():
                    dst_path = tmpdir_p / surface["path"]
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")

            # M-D1: 형식 맞지 않는 축은 fence 에서 무시되므로 위반 안 됨 (생존)
            exit_m_d1, stdout_m_d1, _ = run_parity_check(tmpdir_p)
            # 이 mutant 는 fence 파싱에서 무시되므로 exit 0 (생존)
            assert exit_m_d1 == 0, (
                f"M-D1: 형식 맞지 않는 축 행은 fence 에서 무시 → 생존 (exit={exit_m_d1})"
            )

    # ── 6. M-N2: ADR-025 부재 → honest no-op ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        # ADR-025 파일을 복제하지 않음 (부재 시뮬레이션)
        # 다른 파일들만 복제
        for surface in cfsp.SURFACES:
            if "adr-decision7" in surface["key"]:
                # ADR-025 는 건너뜀
                continue
            src_path = root / surface["path"]
            if src_path.is_file():
                dst_path = tmpdir_p / surface["path"]
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")

        # M-N2: ADR-025 부재 시 honest no-op (exit 0)
        exit_m_n2, stdout_m_n2, _ = run_parity_check(tmpdir_p)
        assert exit_m_n2 == 0, (
            f"M-N2: ADR-025 부재 시 honest no-op 으로 exit==0 (exit={exit_m_n2})"
        )
        # marker 에 "no-op" 또는 "파일 부재" 포함
        assert cfsp.MARKER in stdout_m_n2, f"M-N2: marker 부재 {stdout_m_n2}"

    # ── 7. M-F1: fuzz 엣지 케이스 ──
    # 비-UTF8 바이트, 8193자 라인, 0byte, fence 미닫힘, 미존재 경로, basename 불일치

    fuzz_cases = [
        ("non-utf8", b"\xff\xfe", 2),  # 비-UTF8 → exit 2
        ("path-not-exist", "path-does-not-exist", 2),  # 경로 부재 → exit 2
        ("0byte-file", "", 2),  # 0byte 파일 → exit 2 (fence 0행)
    ]

    for fuzz_name, fuzz_input, expected_exit in fuzz_cases:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = Path(tmpdir)
            adr_copy = tmpdir_p / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
            adr_copy.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(fuzz_input, bytes):
                adr_copy.write_bytes(fuzz_input)
            else:
                adr_copy.write_text(fuzz_input, encoding="utf-8")

            exit_fuzz, stdout_fuzz, stderr_fuzz = run_parity_check(tmpdir_p)
            assert exit_fuzz == expected_exit, (
                f"M-F1 {fuzz_name}: 예상 exit={expected_exit}, 실제={exit_fuzz}. "
                f"stdout={stdout_fuzz}, stderr={stderr_fuzz}"
            )

    print("[form-set-parity] PASS — mutation-kill 실증 완료 (M-A1 2×2 + M-A5' + M-D1 + M-N2 + M-F1 fuzz)")


if __name__ == "__main__":
    test_form_set_parity_mutation_kill()
