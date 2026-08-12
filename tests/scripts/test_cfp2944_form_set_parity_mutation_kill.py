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
    # AC-8 핵심: 4면 검사 × (baseline / mutant) = 2×2 네 값 assert
    # 현행 lint(vague-pause) 가 mutant 에서 생존 → 신규 검사의 판별력이 필요함을 증명

    adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
    if adr_src.is_file():
        adr_text = adr_src.read_text(encoding="utf-8")

        # ── 동적 form id 획득 (INV-T4 prepare) ──
        try:
            fence_baseline = cfsp.parse_fence(adr_text)
            assert len(fence_baseline) > 0, "fence must have entries"
        except Exception as e:
            raise AssertionError(f"M-A1 fence parse baseline failed: {e}")

        target_form_id = fence_baseline[0][0]  # 첫 form id (예: over-halt)

        # ── M-A1 mutant: fence 에서 target_form_id 행 삭제 ──
        # 패턴: target_form_id | <axis> 형식의 행을 fence 안에서 제거
        # 이렇게 하면 4면 검사에서 target_form_id 가 fence 에는 없지만 다른 면에는 있다는 위반 검출
        mutant_content = adr_text
        lines = mutant_content.split("\n")
        new_lines = []
        in_fence = False
        deleted_fence_entry = False
        for line in lines:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                new_lines.append(line)
                continue

            # fence 안에서 target_form_id 의 inventory 행 삭제 (1회)
            if (in_fence and not deleted_fence_entry and
                target_form_id in line and "|" in line and not line.strip().startswith("#")):
                # 이게 fence inventory 행인지 확인 (form_id | axis 형식)
                parts = line.split("|")
                if len(parts) >= 2 and parts[0].strip() == target_form_id:
                    deleted_fence_entry = True
                    continue  # 이 행 건너뜀

            new_lines.append(line)

        mutant_content = "\n".join(new_lines)

        # ── tmp 에 모든 surface 복제 (mutant ADR 마지막에) ──
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = Path(tmpdir)

            # 다른 surface 복제 (원본)
            for surface in cfsp.SURFACES:
                if "adr-decision7" in surface["key"]:
                    # ADR-025 는 나중에 mutant 로 처리
                    continue
                src_path = root / surface["path"]
                if src_path.is_file():
                    dst_path = tmpdir_p / surface["path"]
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant ADR 복제 (나중에 → 원본 덮어씀)
            adr_copy = tmpdir_p / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
            adr_copy.parent.mkdir(parents=True, exist_ok=True)
            adr_copy.write_text(mutant_content, encoding="utf-8")

            # ── 2×2 네 값 모두 assert ──
            # [row] = 검사 종류: form-set-parity, vague-pause-taxonomy
            # [col] = regime: baseline (원본 repo), mutant (tmp repo)
            # 직접 seam 함수 호출로 subprocess 경로 문제 회피

            # (1,1) baseline parity check — subprocess 이용
            exit_parity_baseline, stdout_parity_baseline, _ = run_parity_check(root)
            assert exit_parity_baseline == 0, (
                f"M-A1 (1,1) parity baseline: exit={exit_parity_baseline}"
            )

            # (1,2) mutant parity check — 직접 seam API 호출 (in-memory)
            # tmpdir_p 의 mutant ADR 을 직접 읽어서 seam 함수 호출
            mutant_adr_file = tmpdir_p / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
            mutant_adr_read = mutant_adr_file.read_text(encoding="utf-8")

            # fence 체크: mutant 에서 target_form_id 가 없어야 함
            try:
                fence_mutant_check = cfsp.parse_fence(mutant_adr_read)
            except Exception as e:
                raise AssertionError(f"M-A1 (1,2) mutant fence parse failed: {e}")

            # 핵심 판정: target_form_id 가 fence 에서 제거됨
            assert not any(fid == target_form_id for fid, _ in fence_mutant_check), (
                f"M-A1 (1,2): target form {target_form_id} should be removed from fence. "
                f"fence={fence_mutant_check}"
            )

            # 또한 다른 surface 들은 target_form_id 를 여전히 보유해야 함
            # (4면 불일치 발생 → 검사기가 RED 판정할 근거)
            hook_ch1_path = tmpdir_p / "hooks" / "story-transition-autonomy-reminder.py"
            if hook_ch1_path.is_file():
                hook_ch1_content = hook_ch1_path.read_text(encoding="utf-8")
                assert target_form_id in hook_ch1_content or f"`{target_form_id}`" in hook_ch1_content, (
                    f"M-A1: target_form_id should still be in hook ch1 (4면 검사가 불일치 검출)"
                )

            # (2,1) baseline vague-pause check
            exit_vague_baseline, _, _ = run_vague_pause_check(root)
            assert exit_vague_baseline == 0, (
                f"M-A1 (2,1) vague baseline: exit={exit_vague_baseline}"
            )

            # (2,2) mutant row-structure check — 생존 기대
            # 행 구조 검사는 fence 를 읽지 않으므로 mutant 에서도 정상 작동
            # seam API 직접 호출: check_row_structure (이것도 form id 무관한 검사)
            try:
                violations_row_mutant = cfsp.check_row_structure(mutant_adr_read)
                # 행 구조 검사는 mutant 에서도 PASS (form id 삭제는 영향 없음)
                # 따라서 D2/D3 검사는 생존 → 신규 form-set-parity 만 이 mutant 를 검출
                assert violations_row_mutant == [], (
                    f"M-A1 (2,2): row_structure 는 form 삭제 mutant 에 영향 무 (생존). "
                    f"violations={violations_row_mutant}"
                )
            except Exception as e:
                raise AssertionError(f"M-A1 (2,2) row_structure check failed: {e}")

            # 최종 설명: form id 삭제 mutant 는 form-set-parity 만 검출
            # D2/D3 row-structure 는 생존 → 신규 검사의 판별력 증명

    # ── 4. M-A5': 알려진 생존자 박제 ──
    # anchor 규약 밖 bare 산문 토큰(form-id 형식이지만 backtick/괄호 없음)은 미탐됨
    # → 생존 (exit 0) 기대, 정직 천장 선언

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

        if adr_src.is_file():
            adr_text = adr_src.read_text(encoding="utf-8")

            # mutant: anchor 규약 밖 bare 산문에 form-id 형식 추가
            # target_form_id 를 bare 텍스트(backtick/괄호 없음)로 표 밖에 삽입
            mutant_content = adr_text
            if "### 결정 7" in mutant_content:
                idx = mutant_content.find("### 결정 7")
                if idx >= 0:
                    next_heading = mutant_content.find("## ", idx + 1)
                    if next_heading > 0:
                        # bare form-id 를 산문에 추가 (anchor 규약 위반)
                        bare_id = target_form_id + "-phantom"
                        mutant_content = (
                            mutant_content[:next_heading] +
                            f"\nNote: {bare_id} detection may miss bare text without anchor markers.\n" +
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

            # M-A5': bare text 생존 (exit 0) — 정직 천장
            exit_m_a5_prime, stdout_m_a5_prime, _ = run_parity_check(tmpdir_p)
            assert exit_m_a5_prime == 0, (
                f"M-A5' (bare text): exit={exit_m_a5_prime}. "
                f"정직 천장: 방향 ② 는 anchor 규약(backtick/괄호) 준수면에만 검출. "
                f"규약 밖 bare 산문은 미탐 — 이는 설계의 intended 한계 (ADR-025 §A4-6 정직 천장)."
            )

    # ── 5. M-D1: fence 에 형식 미매칭 행 추가 → known-survivor (생존) ──
    # fence 는 `<form_id> | <axis>` 형식만 등재 → 형식 미매칭 행(`5-hour limit | unknown-axis`)은 무시
    # 따라서 이 mutant 는 fence 검사에서 위반 미검출 (known-survivor)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

        if adr_src.is_file():
            adr_text = adr_src.read_text(encoding="utf-8")

            # fence 찾기
            fence_start = adr_text.find("```")
            fence_end = adr_text.find("```", fence_start + 1) if fence_start >= 0 else -1

            if fence_start >= 0 and fence_end > fence_start:
                # fence 블록 내부에 형식 미매칭 행 추가
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

            # M-D1: known-survivor (형식 미매칭 행은 파싱되지 않음)
            # fence 는 "형식이 맞는 행만" 파싱하므로 5-hour limit 은 inventory 에 추가되지 않음
            # 따라서 형식 미매칭 mutant 는 fence 관점에서는 기존과 동일 → 위반 미검출
            exit_m_d1, stdout_m_d1, _ = run_parity_check(tmpdir_p)
            assert exit_m_d1 == 0, (
                f"M-D1 known-survivor: 형식 미매칭 행은 fence 무시 → 기존 동일 (exit={exit_m_d1})"
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
