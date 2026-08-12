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

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[form-record-structure] PASS|FAIL|…`
"""
import sys
import subprocess
import importlib.util
from pathlib import Path


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
    # over-halt 행에서 첫 셀 anchor "(over-halt" 제거 → violations 발생
    mutant_b1 = adr_text.replace(
        "| 잔여작업 有인데 **무발화**로 정지 (over-halt",
        "| 무발화 정지 (축 A2"  # over-halt 제거
    )
    violations_b1 = cfsp.check_row_structure(mutant_b1)
    assert violations_b1, (
        f"M-B1: 첫 셀 anchor 제거 후에도 violations 비어있음. violations={violations_b1}"
    )
    assert any("자기 행 부재" in v for v in violations_b1), (
        f"M-B1: 예상된 '자기 행 부재' 메시지 없음. violations={violations_b1}"
    )

    # ── M-N1 mutant: 산문만 변경 → violations 여전히 빈 리스트 ──
    # 표 밖 heading 만 수정
    mutant_n1 = adr_text.replace(
        "### 결정 7 — 불법 stop 패턴 명시",
        "### 결정 7 — 불법 stop 패턴 명시 (2024년 정정)"
    )
    violations_n1 = cfsp.check_row_structure(mutant_n1)
    assert violations_n1 == [], (
        f"M-N1: 산문만 변경했는데 violations 발생 (오탐). violations={violations_n1}"
    )

    print("[form-record-structure] PASS — D2/D3 구조 검증 및 mutant 판별 완료")


if __name__ == "__main__":
    test_form_record_structure()
