#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): AC-18 measurement channel ∩ 피개선물 = ∅.

목적 (AC-18):
  계측 채널 (tests/perf/**) 과 피개선물 (hooks/**, scripts/**) 의
  무교집합 검증 + driver 가 훅 파일 write 하지 않음 확인

범위:
  - tests/perf/** = 벤치마크·baseline 계측 (읽기만)
  - hooks/** = 훅 구현 (쓰기 대상)
  - scripts/** = 스크립트 (쓰기 대상)
  - driver.sh = S1 benchmark driver (읽기만, 파일 create/modify 금지)

테스트:
  1. tests/perf/** 파일이 hooks/**, scripts/** 를 수정하지 않음
  2. driver.sh 가 훅·스크립트 파일을 write 하지 않음
  3. 계측과 피개선물 경로 disjoint 확인
"""

from __future__ import annotations

from pathlib import Path
import re


def test_perf_driver_no_write_hooks():
    """AC-18: driver.sh 가 hooks/** 파일을 원본 위치에서 수정·쓰지 않음.

    (reads from hooks/** for copy/compare 는 허용 — 피개선물 원본 무수정)
    """
    driver_path = Path(__file__).parent.parent.parent / "tests" / "perf" / "driver.sh"

    if not driver_path.exists():
        # driver.sh 없으면 skip (Wave 2 기준)
        return

    with open(driver_path, encoding="utf-8") as f:
        driver_content = f.read()

    # write 명령 검출: hooks/** 원본 위치에서의 수정 (> redirect / sed -i 등)
    # 예: "sed -i 's/foo/bar/' hooks/file.py" 는 금지
    #     "cp hooks/file.py other/" 는 허용 (읽기)
    write_patterns = [
        r">\s*['\"]?[^/\s]*hooks/",  # redirect to hooks path (> hooks/... or >> hooks/...)
        r"sed\s+-i[^;]*hooks/",  # sed -i ... hooks/
        r"cat\s+[^>]*>\s*hooks/",  # cat ... > hooks/
        r"echo.*>\s*['\"]?[^/\s]*hooks/",  # echo ... > hooks/
        r">>\s*['\"]?[^/\s]*hooks/",  # append to hooks/
    ]

    violations = []
    for pattern in write_patterns:
        if re.search(pattern, driver_content):
            violations.append(f"Found write pattern: {pattern}")

    assert not violations, (
        f"driver.sh should not modify hooks/** files in-place (AC-18):\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


def test_perf_driver_no_write_scripts():
    """AC-18: driver.sh 가 scripts/** 파일을 write 하지 않음."""
    driver_path = Path(__file__).parent.parent.parent / "tests" / "perf" / "driver.sh"

    if not driver_path.exists():
        return

    with open(driver_path, encoding="utf-8") as f:
        driver_content = f.read()

    # write 명령 검출
    write_patterns = [
        r">\s*scripts/",
        r"tee\s+scripts/",
        r"sed\s+-i.*scripts/",
        r"cp\s+.*scripts/",
        r"mv\s+.*scripts/",
        r"echo.*>\s*scripts/",
    ]

    violations = []
    for pattern in write_patterns:
        if re.search(pattern, driver_content):
            violations.append(f"Found write pattern: {pattern}")

    assert not violations, (
        f"driver.sh should not write scripts/** files (AC-18):\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


def test_measurement_paths_disjoint():
    """AC-18: tests/perf/** ∩ {hooks/**, scripts/**} = ∅."""
    perf_path = Path(__file__).parent.parent.parent / "tests" / "perf"
    hooks_path = Path(__file__).parent.parent
    scripts_path = Path(__file__).parent.parent.parent / "scripts"

    if not perf_path.exists():
        # tests/perf 없으면 skip
        return

    # 경로 문자열 비교 (절대 경로 정규화)
    perf_files = set(p.relative_to(perf_path.parent) for p in perf_path.rglob("*") if p.is_file())
    hooks_files = set(p.relative_to(hooks_path.parent) for p in hooks_path.rglob("*") if p.is_file() and "tests/" not in str(p))
    scripts_files = set(p.relative_to(scripts_path.parent) for p in scripts_path.rglob("*") if p.is_file()) if scripts_path.exists() else set()

    # intersection 은 empty 여야 함
    perf_hooks_intersection = perf_files & hooks_files
    perf_scripts_intersection = perf_files & scripts_files

    assert not perf_hooks_intersection, (
        f"Measurement (tests/perf/**) should not contain hooks/** files:\n"
        + "\n".join(f"  - {f}" for f in perf_hooks_intersection)
    )

    assert not perf_scripts_intersection, (
        f"Measurement (tests/perf/**) should not contain scripts/** files:\n"
        + "\n".join(f"  - {f}" for f in perf_scripts_intersection)
    )
