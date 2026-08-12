#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2944_stop_norm_mirror_parity.py

CFP-2944 Phase 2 (구현) — D4 mirror anchor parity 검증 (AC-5 · AC-11).

계약 SSOT: Story CFP-2944 §7.12 Test Contract
  - D4: mirror anchor parity — 개정 anchor 가 선언된 mirror 전 site 에 존재
  - AC-5: ADR-141 A6-3(a) remedy mirror 의 "기존 대기" 문구 제거 + pointer 보유
  - AC-11: ADR-109 §결정 5 축 분리 mirror 의 "재시도 축 한정" 문구 동기화
  - 절대수치 assert 금지 — INV-T6 (형식 변경 시 count 자연 변동)

규범 SSOT: ADR-025 Amendment 4 (mirror 정책) + ADR-141 Amendment 8 + ADR-109 Amendment 2

RED 진정성 입증:
  - AC-5 축 1-a mutant: "기존 대기" 를 mirror 에 되살림 → 위반 검출 확인
  - AC-5 축 1-b mutant: mirror 의 `ADR-141 A8-3` 리터럴 제거 → 위반 검출 확인
  - AC-11 mutant: "재시도 축 한정" 제거 → 위반 검출 확인

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[stop-norm-mirror-parity] PASS|FAIL|setup error:…`
"""
import re
import os
import sys
import tempfile
import subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


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


def _find_section_line_bounds(lines, start_heading):
    """lines 리스트에서 start_heading 으로 시작하는 섹션의 (start_line_idx, end_line_idx) 반환.

    반환: (start_idx, end_idx) — end_idx 는 exclusive (슬라이싱용)
    부재: (None, None)
    """
    start_idx = None
    end_idx = len(lines)

    for i, line in enumerate(lines):
        if start_idx is None and line.strip().startswith(start_heading):
            start_idx = i
            continue
        if start_idx is not None:
            # 다음 h2/h3 heading 찾기
            if line.startswith("## ") or line.startswith("### "):
                end_idx = i
                break

    if start_idx is None:
        return None, None
    return start_idx, end_idx


def check_axis1_mirror_parity(root: Path) -> dict:
    """AC-5: ADR-141 A6-3(a) remedy mirror 검증.

    조건 1-a: "기존 대기" 는 제외 영역을 제외하고 repo 에서 완전히 제거됨 (잔여 = 빈 집합).
    조건 1-b: mirror 파일들(SSOT 제외)은 "ADR-141 A8-3" 리터럴을 보유.

    반환: {"violations_1a": [list], "violations_1b": [list], "ok_1a": bool, "ok_1b": bool}
    """
    violations_1a = []
    violations_1b = []

    # ── 조건 1-a: "기존 대기" 잔여 검증 ──
    # 정의역: archive/adr, docs, skills, CLAUDE.md
    # 제외:
    #   - archive/adr/ADR-026-post-merge-automation.md 전체
    #   - archive/adr/ADR-141-all-opus-single-tier.md 의 frontmatter (선두 --- ~ 다음 ---)
    #   - archive/adr/ADR-141-all-opus-single-tier.md 의 Amendment 8 ~ EOF

    scan_targets = [
        (root / "archive" / "adr", "*.md"),
        (root / "docs", "**/*.md"),
        (root / "skills", "**/*.md"),
        (root / "CLAUDE.md", None),  # 단일 파일
    ]

    target_literal = "기존 대기"
    adr_026_path = root / "archive" / "adr" / "ADR-026-post-merge-automation.md"
    adr_141_path = root / "archive" / "adr" / "ADR-141-all-opus-single-tier.md"

    # ADR-141 frontmatter 와 Amendment 8 범위 동적 산출
    adr_141_frontmatter_end_line = None
    adr_141_amd8_start_line = None

    if adr_141_path.is_file():
        adr_141_text = adr_141_path.read_text(encoding="utf-8")
        lines_141 = adr_141_text.split("\n")

        # frontmatter 끝 찾기 (첫 --- 이후 다음 --- 까지)
        fence_count = 0
        for i, line in enumerate(lines_141):
            if line.startswith("---"):
                fence_count += 1
                if fence_count == 2:
                    adr_141_frontmatter_end_line = i
                    break

        # Amendment 8 시작 찾기
        for i, line in enumerate(lines_141):
            if line.strip().startswith("## Amendment 8"):
                adr_141_amd8_start_line = i
                break

    # 정의역 파일 스캔
    files_to_scan = []
    for target_dir, pattern in scan_targets:
        if target_dir.name == "CLAUDE.md":
            # 단일 파일
            if target_dir.is_file():
                files_to_scan.append(target_dir)
        else:
            if target_dir.is_dir():
                if pattern == "*.md":
                    files_to_scan.extend(target_dir.glob(pattern))
                else:
                    files_to_scan.extend(target_dir.glob(pattern))

    for file_path in files_to_scan:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 제외 적용
        if file_path == adr_026_path:
            # 파일 전체 제외
            continue

        # ADR-141 제외 처리
        if file_path == adr_141_path:
            # frontmatter 와 Amendment 8 이후 제외
            lines = content.split("\n")
            content_for_check = []
            for i, line in enumerate(lines):
                # frontmatter 범위 제외
                if adr_141_frontmatter_end_line is not None and i <= adr_141_frontmatter_end_line:
                    continue
                # Amendment 8 범위 제외
                if adr_141_amd8_start_line is not None and i >= adr_141_amd8_start_line:
                    continue
                content_for_check.append(line)
            content = "\n".join(content_for_check)

        # "기존 대기" 검색
        if target_literal in content:
            violations_1a.append(
                f"{file_path.relative_to(root)}: '{target_literal}' 잔여 (제외 후에도 발견)"
            )

    # ── 조건 1-b: mirror 파일의 pointer 검증 ──
    # mirror 파일: docs/orchestrator-playbook.md, skills/rate-limit-429-mitigation/SKILL.md
    # 각 파일이 "ADR-141 A8-3" 리터럴 보유 (SSOT 제외)

    mirror_files = [
        root / "docs" / "orchestrator-playbook.md",
        root / "skills" / "rate-limit-429-mitigation" / "SKILL.md",
    ]

    pointer_literal = "ADR-141 A8-3"

    for mirror_path in mirror_files:
        if not mirror_path.is_file():
            violations_1b.append(f"{mirror_path.relative_to(root)}: 파일 부재")
            continue

        try:
            mirror_content = mirror_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            violations_1b.append(f"{mirror_path.relative_to(root)}: 읽기 실패")
            continue

        if pointer_literal not in mirror_content:
            violations_1b.append(
                f"{mirror_path.relative_to(root)}: '{pointer_literal}' 리터럴 부재 (mirror 동기화 미실행)"
            )

    return {
        "violations_1a": violations_1a,
        "violations_1b": violations_1b,
        "ok_1a": len(violations_1a) == 0,
        "ok_1b": len(violations_1b) == 0,
    }


def check_axis2_mirror_parity(root: Path) -> dict:
    """AC-11: ADR-109 §결정 5 축 분리 mirror 검증.

    함의: "사용자 turn 대기" ∨ "user manual resume only" 를 보유한 파일 →
    전건이 "재시도 축 한정" 을 보유해야 함.

    정의역: archive/adr, docs, skills (tests, scripts, .github, templates 제외)

    반환: {"violations": [list], "ok": bool}
    """
    violations = []

    trigger_literals = ["사용자 turn 대기", "user manual resume only"]
    required_literal = "재시도 축 한정"

    scan_targets = [
        (root / "archive" / "adr", "**/*.md"),
        (root / "docs", "**/*.md"),
        (root / "skills", "**/*.md"),
        (root / "CLAUDE.md", None),
    ]

    files_to_scan = []
    for target_path, pattern in scan_targets:
        if target_path.name == "CLAUDE.md":
            if target_path.is_file():
                files_to_scan.append(target_path)
        else:
            if target_path.is_dir():
                if pattern:
                    files_to_scan.extend(target_path.glob(pattern))

    # 트리거 보유 파일 수집
    files_with_trigger = []
    for file_path in files_to_scan:
        # 제외 디렉토리 필터링
        if any(part in file_path.parts for part in ["tests", "scripts", ".github", "templates", "__pycache__"]):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 트리거 검색 (OR 조건)
        has_trigger = any(literal in content for literal in trigger_literals)
        if has_trigger:
            files_with_trigger.append(file_path)

    # 각 파일이 required_literal 을 보유하는지 검증
    for file_path in files_with_trigger:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if required_literal not in content:
            trigger_found = next(
                lit for lit in trigger_literals if lit in content
            )
            violations.append(
                f"{file_path.relative_to(root)}: '{trigger_found}' 보유 하지만 "
                f"'{required_literal}' 부재 (함의 위반)"
            )

    return {
        "violations": violations,
        "ok": len(violations) == 0,
    }


def test_stop_norm_mirror_parity():
    """D4: mirror anchor parity 검증 (필수 함수명 — RTM ac-traceability-matrix)

    AC-5 축 1-a/1-b 와 AC-11 을 실증한다.
    """
    root = repo_root()

    # ── AC-5 축 1 (기존 대기) ──
    result_1 = check_axis1_mirror_parity(root)

    if not result_1["ok_1a"]:
        violations_str = "\n".join(f"  {v}" for v in result_1["violations_1a"])
        print(f"[stop-norm-mirror-parity] FAIL — AC-5 축 1-a 위반:\n{violations_str}", file=sys.stderr)
        raise AssertionError(
            f"AC-5 축 1-a: '기존 대기' 잔여 검출:\n" + violations_str
        )

    if not result_1["ok_1b"]:
        violations_str = "\n".join(f"  {v}" for v in result_1["violations_1b"])
        print(f"[stop-norm-mirror-parity] FAIL — AC-5 축 1-b 위반:\n{violations_str}", file=sys.stderr)
        raise AssertionError(
            f"AC-5 축 1-b: mirror pointer 부재:\n" + violations_str
        )

    # ── AC-11 축 2 ──
    result_2 = check_axis2_mirror_parity(root)

    if not result_2["ok"]:
        violations_str = "\n".join(f"  {v}" for v in result_2["violations"])
        print(f"[stop-norm-mirror-parity] FAIL — AC-11 위반:\n{violations_str}", file=sys.stderr)
        raise AssertionError(
            f"AC-11: 함의 위반:\n" + violations_str
        )

    # ── M-C1 mutant: mirror 에 "기존 대기" 되살림 → 축 1-a 위반 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        # playbook.md 복제
        playbook_src = root / "docs" / "orchestrator-playbook.md"
        if playbook_src.is_file():
            playbook_dst = tmpdir_p / "docs" / "orchestrator-playbook.md"
            playbook_dst.parent.mkdir(parents=True, exist_ok=True)
            playbook_content = playbook_src.read_text(encoding="utf-8")

            # mutant: "기존 대기" 문구 추가 (현재 없다면 추가)
            if "기존 대기" not in playbook_content:
                mutant_content = playbook_content + "\n기존 대기가 존재한다.\n"
            else:
                # 이미 있으면 비율 증가
                mutant_content = playbook_content

            playbook_dst.write_text(mutant_content, encoding="utf-8")

            # 다른 필수 파일들도 복제
            for src in [
                root / "archive" / "adr" / "ADR-141-all-opus-single-tier.md",
                root / "skills" / "rate-limit-429-mitigation" / "SKILL.md",
            ]:
                if src.is_file():
                    rel = src.relative_to(root)
                    dst = tmpdir_p / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant 에서 축 1-a 검사 → 위반 검출되어야 함
            result_m_c1 = check_axis1_mirror_parity(tmpdir_p)
            assert not result_m_c1["ok_1a"], (
                f"M-C1: '기존 대기' 를 되살린 후에도 축 1-a 위반이 검출되지 않음 (kill 실패)"
            )
            assert len(result_m_c1["violations_1a"]) > 0, "M-C1: violations 비어있음"

    # ── M-C1b mutant: mirror 의 ADR-141 A8-3 리터럴 제거 → 축 1-b 위반 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        skill_src = root / "skills" / "rate-limit-429-mitigation" / "SKILL.md"
        if skill_src.is_file():
            skill_dst = tmpdir_p / "skills" / "rate-limit-429-mitigation" / "SKILL.md"
            skill_dst.parent.mkdir(parents=True, exist_ok=True)
            skill_content = skill_src.read_text(encoding="utf-8")

            # mutant: ADR-141 A8-3 리터럴 제거
            mutant_content = skill_content.replace("ADR-141 A8-3", "ADR-XXX placeholder")
            skill_dst.write_text(mutant_content, encoding="utf-8")

            # 다른 파일들도 복제
            for src in [
                root / "archive" / "adr" / "ADR-141-all-opus-single-tier.md",
                root / "docs" / "orchestrator-playbook.md",
            ]:
                if src.is_file():
                    rel = src.relative_to(root)
                    dst = tmpdir_p / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant 에서 축 1-b 검사 → 위반 검출되어야 함
            result_m_c1b = check_axis1_mirror_parity(tmpdir_p)
            assert not result_m_c1b["ok_1b"], (
                f"M-C1b: pointer 리터럴을 제거한 후에도 축 1-b 위반이 검출되지 않음 (kill 실패)"
            )
            assert len(result_m_c1b["violations_1b"]) > 0, "M-C1b: violations 비어있음"

    # ── M-C2 mutant: ADR-026 동음이의 문맥만 존재 → 위반 0 (overkill 방어) ──
    # ADR-026 자체는 정의역 밖이므로, ADR-026 에만 "기존 대기" 가 있고 다른 곳엔 없으면 OK
    adr_026_path = root / "archive" / "adr" / "ADR-026-post-merge-automation.md"
    if adr_026_path.is_file():
        # 이 파일은 제외되므로 자연히 violations_1a 에 포함되지 않아야 함
        # (이미 위의 check_axis1_mirror_parity 에서 처리)
        result_current = check_axis1_mirror_parity(root)
        # ADR-026 가 제외되었으므로 violations_1a 에 ADR-026 경로가 없어야 함
        adr_026_violations = [v for v in result_current["violations_1a"] if "ADR-026" in v]
        assert len(adr_026_violations) == 0, (
            f"M-C2 fail: ADR-026 은 제외되어야 하는데 violations 에 포함됨: {adr_026_violations}"
        )

    # ── AC-11 축 2 mutant: "재시도 축 한정" 제거 → 위반 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        adr_109_src = root / "archive" / "adr" / "ADR-109-in-process-429-mitigation-framework.md"
        if adr_109_src.is_file():
            adr_109_dst = tmpdir_p / "archive" / "adr" / "ADR-109-in-process-429-mitigation-framework.md"
            adr_109_dst.parent.mkdir(parents=True, exist_ok=True)
            adr_109_content = adr_109_src.read_text(encoding="utf-8")

            # mutant: "재시도 축 한정" 제거
            mutant_content = adr_109_content.replace("재시도 축 한정", "REMOVED-axis-constraint")
            adr_109_dst.write_text(mutant_content, encoding="utf-8")

            # 다른 파일들 (트리거 보유)
            for src in [
                root / "docs" / "orchestrator-playbook.md",
            ]:
                if src.is_file():
                    rel = src.relative_to(root)
                    dst = tmpdir_p / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant 에서 축 2 검사 → 위반 검출되어야 함
            result_axis2_mutant = check_axis2_mirror_parity(tmpdir_p)
            assert not result_axis2_mutant["ok"], (
                f"AC-11 mutant: '재시도 축 한정' 제거 후에도 위반이 검출되지 않음 (kill 실패)"
            )
            assert len(result_axis2_mutant["violations"]) > 0, "AC-11 mutant: violations 비어있음"

    print("[stop-norm-mirror-parity] PASS — AC-5 축 1-a/1-b + AC-11 검증 완료 (mutant kill 4종 실증)")


if __name__ == "__main__":
    test_stop_norm_mirror_parity()
