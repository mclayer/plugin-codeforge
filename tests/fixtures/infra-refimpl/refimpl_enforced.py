#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tests/fixtures/infra-refimpl/refimpl_enforced.py
CFP-2700 G3 / ADR-157 §결정2 — AC-19 discriminating fixture **refimpl-enforced**.

D2 startup fail-closed 4계약을 **준수**하는 실행단위 모사: 첫 business 동작 이전 startup 단계에서
  infra_startup_validator(reference-impl)를 호출하고, non-zero 를 **그대로 전파**한다(exit-masking
  금지). business 진입은 `BUSINESS_OP_REACHED` 센티넬로 표시 — required 자원 미설정 시 이 센티넬이
  **절대 출력되지 않아야**(startup-stage exit) 계약 준수다. 센티넬이 출력된 뒤 크래시하면 그것은
  지연 크래시(late-crash) = 계약 위반 형상(refimpl_unenforced.py 참조)이다.

판정 계약 (self-test 가 소비): 선언O + startup대조O → 미설정 시 exit 78(EX_CONFIG) + 센티넬 부재
  = PASS 형상 / 자원 설정 시 exit 0 + 센티넬 출력.

usage: python3 refimpl_enforced.py [manifest_path] [unit]
  (기본 manifest = 동일 디렉터리 manifest.yaml, 기본 unit = collector)
env REFIMPL_LIB_DIR = validator 모듈 디렉터리 override (mutation self-test 주입 seam — 기본
  repo `scripts/lib`). 조회는 main() 내부에서만 (lazy — import-time env deref 0).
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))

SENTINEL = "BUSINESS_OP_REACHED"


def main(argv):
    manifest = argv[1] if len(argv) > 1 else os.path.join(_HERE, "manifest.yaml")
    unit = argv[2] if len(argv) > 2 else "collector"

    # ── startup 단계: 첫 business 동작 이전 대조 (D2 계약의 핵심 위치) ──
    lib_dir = os.environ.get("REFIMPL_LIB_DIR") or os.path.join(_REPO_ROOT, "scripts", "lib")
    sys.path.insert(0, lib_dir)
    from infra_startup_validator import validate_startup  # lazy import (env deref 도 함수 내부만)

    code, lines = validate_startup(manifest, unit)
    for line in lines:
        print(line)
    if code != 0:
        # 계약 (2) exit-masking 금지: non-zero 그대로 전파 — business 미진입 (센티넬 미출력).
        return code

    # ── business 동작 (startup PASS 이후에만 도달) ──
    print(SENTINEL)
    url = os.environ["RAW_NAS_URL"]  # startup 이 이미 설정을 보증 — 여기서 크래시 불가
    print("business write to %s" % url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
