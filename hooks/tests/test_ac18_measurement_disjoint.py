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

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DRIVER = _REPO_ROOT / "tests" / "perf" / "driver.sh"


def _resolved_files(root: Path, exclude_parts: tuple[str, ...] = ()) -> set[Path]:
    """root 아래 파일들의 **실경로**(resolve) 집합 — 두 집합의 공통 base.

    (1) 동일 base 정규화: 구 코드는 계측 집합을 `tests/` 상대, 피개선물 집합을
        repo root 상대로 만들었다. 같은 파일조차 `perf/x` vs `hooks/x` 로 서로 다른
        원소가 되어 교집합이 **구조적으로 항상 ∅** — 무엇을 넣어도 통과하는
        공허한 assert 였다. resolve() 절대경로로 통일해 실제로 만날 수 있게 한다
        (symlink/junction 로 피개선물이 계측 채널에 끌어들여진 경우도 여기서 만난다).

    (2) 필터 판정을 Path.parts 로: 구 코드의 `"tests/" not in str(p)` 는 Windows 에서
        str(p) 가 백슬래시 구분자라 **한 번도 매치되지 않았다** (실측 2026-08-14:
        hooks/** 109 파일 중 제외 대상 69건, 구 필터 매치 0건 = 필터 완전 무효).
    """
    if not root.exists():
        return set()
    out: set[Path] = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rp = p.resolve()
        if "__pycache__" in rp.parts:
            continue  # 빌드 산출물 — 소유·판정 대상 아님 (양 집합 공통 제외)
        if exclude_parts and any(part in exclude_parts for part in rp.parts):
            continue
        out.add(rp)
    return out


def _disjoint_violations(measurement: set[Path], target: set[Path]) -> set[Path]:
    """계측 채널 ∩ 피개선물 — AC-18 은 이 교집합이 ∅ 임을 요구한다."""
    return measurement & target


def test_perf_driver_no_write_hooks():
    """AC-18: driver.sh 가 hooks/** 파일을 원본 위치에서 수정·쓰지 않음.

    (reads from hooks/** for copy/compare 는 허용 — 피개선물 원본 무수정)
    """
    driver_path = _DRIVER

    # 구 코드는 부재 시 bare return 이라 driver.sh 가 사라지면 **조용히 통과**했다.
    # driver.sh 는 커밋된 실물이므로 부재 자체를 실패로 본다 (판정 대상 소실 검출).
    assert driver_path.exists(), f"계측 driver 부재 — 판정 대상 소실: {driver_path}"

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
    driver_path = _DRIVER

    assert driver_path.exists(), f"계측 driver 부재 — 판정 대상 소실: {driver_path}"

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
    """AC-18: tests/perf/** ∩ {hooks/**, scripts/**} = ∅ (실경로 기준)."""
    perf_path = _REPO_ROOT / "tests" / "perf"
    if not perf_path.exists():
        pytest.skip("tests/perf 부재 — 계측 채널 미배선")

    perf_files = _resolved_files(perf_path)
    hooks_files = _resolved_files(_REPO_ROOT / "hooks", exclude_parts=("tests",))
    scripts_files = _resolved_files(_REPO_ROOT / "scripts")

    # 정의역 비공허 — 양쪽이 비면 교집합 ∅ 는 아무것도 말하지 않는다.
    assert perf_files, "계측 채널(tests/perf/**) 이 비었다 — 판정 대상 0"
    assert hooks_files, "피개선물(hooks/**, tests 제외) 이 비었다 — 판정 대상 0"
    assert scripts_files, "피개선물(scripts/**) 이 비었다 — 판정 대상 0"

    perf_hooks = _disjoint_violations(perf_files, hooks_files)
    perf_scripts = _disjoint_violations(perf_files, scripts_files)

    assert not perf_hooks, (
        "계측 채널(tests/perf/**) 이 피개선물 hooks/** 를 품고 있다 (AC-18):\n"
        + "\n".join(f"  - {f}" for f in sorted(perf_hooks))
    )
    assert not perf_scripts, (
        "계측 채널(tests/perf/**) 이 피개선물 scripts/** 를 품고 있다 (AC-18):\n"
        + "\n".join(f"  - {f}" for f in sorted(perf_scripts))
    )


def test_hooks_tests_exclusion_filter_is_effective():
    """제외 필터가 실제로 작동하는가 (구 필터는 Windows 에서 완전 무효였다).

    구 `"tests/" not in str(p)` 는 백슬래시 구분자에서 매치 0 — hooks/tests/** 69건이
    피개선물 집합에 그대로 섞였다. Path.parts 판정으로 전환한 결과를 고정한다.
    """
    hooks_root = _REPO_ROOT / "hooks"
    all_files = _resolved_files(hooks_root)
    filtered = _resolved_files(hooks_root, exclude_parts=("tests",))

    excluded = all_files - filtered
    assert excluded, "제외된 파일이 0건 — 필터가 무효 (구 회귀)"
    assert all("tests" in p.parts for p in excluded), "tests 밖 파일이 잘못 제외됨"
    assert not any("tests" in p.parts for p in filtered), (
        "필터 통과 집합에 hooks/tests/** 잔존 — 필터 무효"
    )


def test_disjoint_check_has_teeth():
    """판별력 실증 (mutant 상설화 — CFP-2965 F5-3).

    피개선물 경로를 계측 집합에 강제 주입하면 반드시 검출된다.
    1회 실행 실증(2026-08-14 firsthand): test_measurement_paths_disjoint 의
    perf_files 에 hooks/** 실경로 1건을 주입하니 FAIL
    ("계측 채널이 피개선물 hooks/** 를 품고 있다") — 주입 원복 확인.
    구 구현에서는 **같은 주입이 검출되지 않았다** (아래 대조 참조).
    """
    hooks_files = _resolved_files(_REPO_ROOT / "hooks", exclude_parts=("tests",))
    assert hooks_files, "피개선물 집합이 비었다 — 실증 불가"

    injected = {sorted(hooks_files)[0]}
    assert _disjoint_violations(injected, hooks_files) == injected, (
        "주입한 피개선물 경로가 검출되지 않았다 — 교집합 판정이 무력"
    )

    # 대조 (구 base 재현): 같은 파일이 계측 측에서는 `perf/x`, 피개선물 측에서는
    # `hooks/x` 로 표현돼 결코 만나지 않는다 = 구조적 항상-∅.
    legacy_measurement = {Path("perf") / "x.py"}
    legacy_target = {Path("hooks") / "x.py"}
    assert not (legacy_measurement & legacy_target), (
        "구 base 재현이 교집합을 냈다 — 대조 논거 재확인 필요"
    )
