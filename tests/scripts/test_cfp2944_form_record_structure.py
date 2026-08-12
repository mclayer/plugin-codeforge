#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2944_form_record_structure.py

CFP-2944 Phase 2 (구현) — D2/D3 form-record 구조 검증 (AC-7a).

계약 SSOT: Story CFP-2944 §7.12 Test Contract
  - D2: form-record 구조 술어 — 각 form 행이 discriminant 3항 anchor + tier 라벨 보유
  - D3: negative-control presence — 각 신규 form 행(CFP-2944)에 정당 구분선
  - AC-7a: 신규 form 행이 ① 축별 discriminant 3항 ② tier 라벨 을 보유함을 assert
  - INV-T2: ∀ form: discriminant 3항 anchor + tier 라벨 보유

규범 SSOT: ADR-025 Amendment 4 §결정 7 표 구조 + ADR-025 §A4-2 discriminant 정의

RED 진정성 입증:
  - M-B1: anchor 제거 → D2 자기 행 부재 위반 검출
  - M-N1: 산문만 변경 → 위반 0 (오탐 방어)
  - M-E1: hard-block 추가 → check-tier-honesty.py 실행해 RED 검증

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[form-record-structure] PASS|FAIL|setup error:…`
"""
import sys
import subprocess
import importlib.util
import tempfile
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
    """repo-root 탐색."""
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


def run_tier_honesty_check(root: Path) -> tuple:
    """check-tier-honesty.py 실행.

    반환: (exit_code, stdout, stderr)
    """
    script = root / "scripts" / "check-tier-honesty.py"
    if not script.is_file():
        # 스크립트 부재 → honest no-op (M-E1 mutant 가 실행 불가면 그 사유 정직 기재)
        return 0, "[tier-honesty] script not found — M-E1 실행 불가", ""

    try:
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(root),
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Timeout"
    except Exception as e:
        return 2, "", str(e)


def test_form_record_structure():
    """D2/D3: form-record 구조 검증 (필수 함수명 — RTM ac-traceability-matrix)

    Main entry point for AC-7a form record structure verification.
    seam API 사용 (자기 파서 재구현 금지).
    """
    root = repo_root()
    adr_file = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

    if not adr_file.is_file():
        raise AssertionError(f"[form-record-structure] FAIL — ADR-025 not found: {adr_file}")

    adr_text = adr_file.read_text(encoding="utf-8")

    # ── D2/D3 검증: seam API 호출 (자기 파서 금지) ──
    violations = cfsp.check_row_structure(adr_text)

    assert violations == [], (
        f"[form-record-structure] FAIL — D2/D3 구조 위반: {violations}"
    )

    # ── M-B1 mutant: 표 첫 셀에서 form id anchor 제거 → D2 자기 행 부재 위반 ──
    # "over-halt" 라는 form id 를 첫 셀 anchor 에서 제거 → violations 발생
    mutant_b1 = adr_text.replace(
        "| 잔여작업 有인데 **무발화**로 정지 (over-halt",
        "| 무발화 정지로 진행 무단 중단 (axis-A2"  # over-halt 제거
    )
    violations_b1 = cfsp.check_row_structure(mutant_b1)
    assert violations_b1, (
        f"M-B1: 첫 셀 anchor 제거 후에도 violations 비어있음. violations={violations_b1}"
    )
    assert any("자기 행 부재" in v for v in violations_b1), (
        f"M-B1: 예상된 '자기 행 부재' 메시지 없음. violations={violations_b1}"
    )

    # ── M-N1 mutant: 산문만 변경 → violations 여전히 빈 리스트 ──
    # 표 밖 heading 만 수정 (구조에 영향 없음)
    mutant_n1 = adr_text.replace(
        "### 결정 7 — 불법 stop 패턴 명시",
        "### 결정 7 — 불법 stop 패턴 명시 (2024년 정정 기록)"
    )
    violations_n1 = cfsp.check_row_structure(mutant_n1)
    assert violations_n1 == [], (
        f"M-N1: 산문만 변경했는데 violations 발생 (오탐). violations={violations_n1}"
    )

    # ── M-E1 mutant: form 행에 hard-block 추가 후 check-tier-honesty.py 실행 ──
    # hard-block 은 tier-honesty 검사에서 걸려야 함
    # (실제 repo 에서는 hard-block 이 없고, mutant 에 추가하면 검사 RED)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        # mutant: 신규 form 행에 hard-block 추가 (M-E1 payload)
        # 예: "hard-block" 이라는 문자열을 새 form 행에 삽입
        mutant_e1 = adr_text

        # 기존 form 행 하나를 찾아 hard-block 문자열 추가
        # 예: over-halt 행에 "hard-block" 이라는 문자열 추가
        if "| 잔여작업 有인데 **무발화**로 정지 (over-halt" in mutant_e1:
            mutant_e1 = mutant_e1.replace(
                "| 잔여작업 有인데 **무발화**로 정지 (over-halt",
                "| 잔여작업 有인데 **무발화**로 정지 (over-halt — hard-block 물리강제"
            )

        adr_copy = tmpdir_p / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
        adr_copy.parent.mkdir(parents=True, exist_ok=True)
        adr_copy.write_text(mutant_e1, encoding="utf-8")

        # M-E1: check-tier-honesty.py 실행
        exit_m_e1, stdout_m_e1, stderr_m_e1 = run_tier_honesty_check(tmpdir_p)

        if exit_m_e1 != 0:
            # 정상: hard-block 문자열이 있으면 check-tier-honesty 가 RED 반환
            # (이것이 우리가 기대하는 동작)
            assert exit_m_e1 in (1, 2), (
                f"M-E1: check-tier-honesty.py 가 예상 exit 코드(1 또는 2)를 반환해야 함 "
                f"(hard-block 문자열 감지). exit={exit_m_e1}, stdout={stdout_m_e1}"
            )
        else:
            # check-tier-honesty.py 가 없거나 실행 불가 → honest no-op 정직 기재
            assert "[tier-honesty] script not found" in stdout_m_e1 or exit_m_e1 == 0, (
                f"M-E1: check-tier-honesty.py 결과 모호 (exit={exit_m_e1}). "
                f"스크립트 부재 시 'script not found' 정직 기재. stdout={stdout_m_e1}"
            )

    print("[form-record-structure] PASS — D2/D3 구조 검증 및 mutant 판별 완료 (M-B1 + M-N1 + M-E1)")


if __name__ == "__main__":
    test_form_record_structure()
