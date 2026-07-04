#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2574 / ADR-143 §결정 3 — KST render-line 시각원 (UTC+9 고정 산술) Python SSOT
#
# 목적: Agent 액션 렌더 줄 프리픽스 `[에이전트명] MM/DD HH:MM - 내용` 의 컴팩트 KST 시각
#       `MM/DD HH:MM` 를 산출. harness 는 system context 로 날짜만 주입하고 시각(HH:MM)은
#       미주입 [source: anthropics/claude-code #34530 Closed not-planned + 실측] → 실시계 read 로만 확보.
#
# TZ-invariant 보장 (ADR-143 §결정 3):
#   - dt = 절대시각(UTC aware) → 목표 tz = fixed +9 offset → machine-local tz·tzdata 무의존.
#   - machine-local `date`·`TZ=Asia/Seoul` 금지 (Windows Git Bash 는 TZ=Asia/Seoul 무시하고 +0000 반환).
#     Korea 고정 offset·DST 영구 부재 invariant 로 UTC+9 고정 산술만 정당.
#   - datetime.utcnow() 금지 (Python 3.12+ deprecated) — datetime.now(timezone.utc) / fromtimestamp(tz=utc) 사용.
#
# Entry-point:
#   python3 kst_render_stamp.py [--epoch <unix_seconds>]
#     --epoch 주면 그 UTC 시각, 없으면 현재 시각.
#   stdout: 정확히 `MM/DD HH:MM\n` 만 (성공 시 stderr 완전히 비어야 함 — 경고 격리).
#   exit 0: 성공 / exit 2: usage·인자 오류(stderr 메시지).
#
# -W error 하 무경고 보장: argparse 미사용(argv 수동 파싱), DeprecationWarning 유발 코드 0,
#   import 는 datetime · sys 만.
#
# SSOT carrier: CFP-2574 Phase 2 (ADR-143 §결정 3)

import datetime
import sys

# Windows cp949 방지 — UTF-8 강제 (scripts/lib/*.py 관례 답습, reconfigure 는 경고 미발생)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# KST = fixed +9 offset (tzdata 무의존, Korea 고정 offset·DST 영구 부재 invariant)
KST = datetime.timezone(datetime.timedelta(hours=9))

# 컴팩트 포맷 — offset·연도·초·KST 라벨 전부 미표기 (ADR-143 §결정 2)
RENDER_FMT = "%m/%d %H:%M"


def main(argv):
    epoch = None

    # argv 수동 파싱 (argparse 미사용 — -W error 무경고)
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--epoch":
            if i + 1 >= len(argv):
                sys.stderr.write("[kst-render-stamp] ERROR: --epoch requires a value\n")
                return 2
            raw = argv[i + 1]
            i += 2
        elif arg.startswith("--epoch="):
            raw = arg[len("--epoch="):]
            i += 1
        else:
            sys.stderr.write(
                "[kst-render-stamp] ERROR: unknown arg '%s'. "
                "Usage: kst_render_stamp.py [--epoch <unix_seconds>]\n" % arg
            )
            return 2
        try:
            epoch = float(raw)
        except ValueError:
            sys.stderr.write(
                "[kst-render-stamp] ERROR: --epoch must be a number, got '%s'\n" % raw
            )
            return 2

    if epoch is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    else:
        dt = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc)

    # 절대시각 → KST 고정 offset 변환 → 컴팩트 포맷 (print 가 trailing \n 부가)
    print(dt.astimezone(KST).strftime(RENDER_FMT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
