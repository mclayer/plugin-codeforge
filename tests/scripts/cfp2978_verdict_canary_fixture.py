#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cfp2978_verdict_canary_fixture.py — CFP-2978 W-20 / `L-CANARY` 담지 픽스처 (AC-13 leg ③ P3).

★★ **이 파일의 테스트는 의도적으로 실패한다. 실패가 정상이고, 통과하면 그것이 결함이다.**

무엇을 재는가 (런타임 negative control)
---------------------------------------
`L-CANARY` 가 지키는 명제 **P3** = *"판정 채널(pytest 계층) 자체가 중성화되지 않았다."*

  - 판정 채널이 **정상**이면 아래 테스트는 **실패**한다 (pytest rc=1).
  - `conftest.py` 계층에서 판정을 중성화하는 변이(**`M-CANARY`** — §8.B 신 mutant 로스터
    「(5) 런타임 1」)가 들어가면 이 테스트가 **통과해 버린다** (rc=0).
  - 그 통과를 `.github/workflows/cfp2978-verdict-canary.yml` 이 **RED 로 관측**한다.

⇒ canary 는 「픽스처가 실패함」을 성공 조건으로 삼는 **역-게이트**다. 통상의 테스트와
   판정 방향이 반대이므로, 이 파일을 "깨진 테스트" 로 오인해 고치지 말 것.

왜 `tests/scripts/` 에 있는가 (배치는 편의가 아니라 계약이다)
------------------------------------------------------------
`M-CANARY` 가 심는 중성화 `conftest.py` 의 사정거리 = **그 conftest 가 놓인 디렉터리 이하**다.
본 픽스처가 `tests/scripts/` 밖에 있으면 `tests/scripts/conftest.py` 중성화를 **원리적으로
못 본다** — 검출이 성립하지 않는다. 스코프 공유가 배치 이유다 (§8.B 구현 동반 의무 5).

왜 파일명이 `test_` 로 시작하지 않는가
--------------------------------------
본 픽스처는 **의도적으로 실패**하므로, 디렉터리 일괄 수집에 걸리면 형제 스위트를 깨뜨린다.
pytest 기본 `python_files` = `test_*.py` / `*_test.py` 이므로 이 이름은 **디렉터리 수집에서
구조적으로 제외**되고, canary workflow 의 **명시 경로 지정**으로만 실행된다.

  [ⓐ firsthand @`9932fe5e4df7760886c59d448faab396fcab01b5`, pytest 9.0.3]
    · 명시 경로 지정        → 수집·실행되어 rc=1
    · `tests/scripts/` 디렉터리 수집 → 매치 0 (수집되지 않음)

  ★이 격리는 **파일명 규약에 의존**한다. 파일을 `test_*` 로 개명하거나 `python_files` 를
   넓히면 형제 스위트가 이 픽스처의 의도적 실패를 함께 흡수해 **기존 GREEN 이 깨진다.**

왜 repo 모듈을 import 하지 않는가
---------------------------------
import 실패는 pytest **rc=2/3(수집·내부 오류)** 를 내는데, 그것은 *"판정 채널이 중성화됐다"*
와 **다른 사건**이다. 의존을 0 으로 두어야 canary 의 `rc == 1` 판별이 오염되지 않는다
(§8.B — *"RED 를 검출로 읽기 전에 사유를 확인한다"*).

정직 한계
---------
`UM-1` — 본 픽스처의 **GHA 실행 관측은 [미실측]** 이다. 로컬 성립과 GHA 성립은 별 사실이며
Phase 2 첫 run 에서 관측한다. ★**미실행인 채로 P3 를 leg ③ 논리곱 항에 계상 금지.**
"""

# canary 산출 동일성 앵커 — workflow 가 이 리터럴의 **출현**으로 "그 RED" 임을 못박는다.
# (rc 만 보면 무관한 실패도 rc=1 이라 "어떤 RED" 와 "그 RED" 가 구별되지 않는다.)
CANARY_SENTINEL = "CFP2978-VERDICT-CANARY-MUST-FAIL"


def test_cfp2978_verdict_canary_must_fail():
    """★의도적 실패 — 이 실패가 **관측되는 것** 자체가 판정 채널 liveness 의 증거다.

    `assert False` 가 아니라 명시 `raise` 를 쓰는 이유: `python -O` 하에서 `assert` 는
    제거되어 테스트가 조용히 통과하고, 그것은 `M-CANARY` 와 **구별되지 않는 위양성**이 된다.
    """
    raise AssertionError(CANARY_SENTINEL)
