#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tests/fixtures/infra-refimpl/refimpl_unenforced.py
CFP-2700 G3 / ADR-157 §결정2 — AC-19 discriminating fixture **refimpl-unenforced**.

죽은 proto-D2 의 4중 결함을 **의도적으로 체현**한 실행단위 모사 (ADR-157 §결정2 결함 목록 동형):
  (a) exit-masking     — 키 누락을 `MISSING:` echo 만 하고 exit 비전파 (`grep -q || echo` 동형).
  (b) `.env` 파일 grep — **프로세스 env 가 아닌** .env 파일 텍스트를 봄 (실행단위가 실제 보는
                          환경과 무관한 표면 검사).
  (c) 빈 값 통과       — `KEY=` 프리픽스 존재만 봄 (set-but-empty 통과).
  (d) fail-open        — .env 파일 부재 시 감지 자체를 조용히 생략 ("미정의 시 감지 비활성").

∴ required 자원 미설정이어도 business 에 **도달**(`BUSINESS_OP_REACHED` 센티넬 출력)하고, 첫 자원
  소비 시점에 **지연 크래시**(late-crash — 원 사고 `DerivedBackendNotConfiguredError` 동형)한다.
  self-test 의 판정 계약: 센티넬 출력 + 사후 non-zero = "선언O + startup대조X" = **FAIL 형상**
  (startup-stage exit 인 refimpl_enforced.py 와의 판별 = AC-19 discriminating pair).

경고: 본 파일은 결함 재현 fixture 다 — consumer 는 절대 이 형상을 채택하지 말 것
  (올바른 형 = refimpl_enforced.py + scripts/lib/infra_startup_validator.py).

usage: python3 refimpl_unenforced.py [env_file_path]
  (기본 .env = 동일 디렉터리 .env — 통상 부재 = 결함 (d) 경로)
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))

SENTINEL = "BUSINESS_OP_REACHED"
REQUIRED_KEYS = ("RAW_NAS_URL",)


def proto_env_check(env_file, required_keys):
    """proto-D2 4중 결함 재현 (의도적 — 올바른 형이 아님)."""
    try:
        text = open(env_file, encoding="utf-8").read()  # (b) .env 파일 grep — 프로세스 env 아님
    except OSError:
        return  # (d) fail-open — 파일 부재 = 감지 조용히 비활성
    for key in required_keys:
        present = any(line.startswith(key + "=") for line in text.splitlines())  # (c) 빈 값 통과
        if not present:
            print("MISSING: %s" % key)  # (a) echo 만 — exit 비전파 (masking)


def main(argv):
    env_file = argv[1] if len(argv) > 1 else os.path.join(_HERE, ".env")
    proto_env_check(env_file, REQUIRED_KEYS)

    # startup 대조 없이 business 진입 — 여기가 결함의 핵심 (지연 크래시 예약).
    print(SENTINEL)
    url = os.environ["RAW_NAS_URL"]  # 미설정이면 여기서 KeyError = late-crash (원 사고 동형)
    print("business write to %s" % url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
