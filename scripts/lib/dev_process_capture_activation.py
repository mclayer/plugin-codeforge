#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# dev_process_capture_activation.py — dev-process-event-v1 always-on α 활성화 게이트 (단일 진입점)
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A — dev-process observability substrate
# 설계 SSOT: ADR-155 §결정 8(always-on 비대칭 α) + change-plan 2026-07-15-cfp-2687 §7.4(env-isolation P0)
#           + §7.5(always-on 4중 bound) + ADR-064 §결정 7(consumer opt-in-false extend-only, 무약화)
#           + §7.1 T-DPE-9(consumer floor 하방 override 불가 / always-on = checkout-identity 파생).
#
# 책임 (SRP = 활성 판정 ONLY — capture/redaction/append 미수행):
#   - dev_process_capture_enabled() = 모든 capture 경로(hook Port A / agent-emit Port B)가
#     write 前에 consult 하는 **단일 활성화 게이트**. §8.10 activation-manifest 가 inspect 하는
#     named symbol.
#   - α 비대칭 (ADR-155 §결정 8):
#       · wrapper-self checkout = **always-on** — checkout-identity 파생(user-settable bool 아님).
#         wrapper 경로에서는 어떤 env 도 consult 하지 않는다 (T-DPE-9: 상속/override 로 끌 수 없음).
#       · consumer 배포 = **opt-in default-false** (ADR-064 extend-only). 명시 opt-in env 시에만 ON.
#         consumer 는 wrapper always-on 을 상속하지 못한다 (silent telemetry 차단).
#
# ★비책임 (floor 무약화 — 별 축):
#   - capture-time redaction floor(INV-8)는 활성 여부와 **무관하게** 항상 선행한다 —
#     redaction 은 capture_blob(dev_process_blob_store) 가 무조건 수행. 본 게이트는 "기록할까"만
#     판정하고, "무엇을 어떻게 안전 처리할까"(redaction/blob-order INV-8a/8b)는 blob store 소관.
#     ∴ consumer opt-in 이 ON 이어도 privacy floor 는 하방 override 되지 않는다(다른 축).
#
# scope 단일 권위 (SoT 이중화 회피):
#   consumer_scope 판정은 append_dev_process_event._norm_consumer_scope 를 **재사용**한다
#   (index row 의 consumer_scope 필드와 게이트 판정이 동일 authority 를 공유 → 불일치 0).
#
# 정직 천장(ADR-119): checkout-identity 파생은 CLAUDE_PROJECT_DIR basename 휴리스틱(wave-1 SSOT)
#   에 의존한다 — 완전 무오류 탐지를 단정하지 않는다. env 미설정 시 wave-1 default(wrapper)를 그대로
#   상속한다(본 모듈이 competing 탐지를 신설하지 않음 — 단일 authority 유지).

import os
import sys

# Windows cp949 회피(ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# consumer_scope 단일 authority 재사용 (reuse-before-write — ADR-140 hygiene).
try:
    from append_dev_process_event import _norm_consumer_scope
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from append_dev_process_event import _norm_consumer_scope


# consumer opt-in env (default-false). truthy 값에서만 consumer capture 활성.
# wrapper 경로는 이 env 를 **consult 하지 않는다**(always-on = user-settable 아님, T-DPE-9).
CONSUMER_OPT_IN_ENV = "CODEFORGE_DEV_PROCESS_CAPTURE"
_TRUTHY = frozenset({"1", "true", "yes", "on"})


def resolve_consumer_scope(consumer_scope=None):
    """checkout-identity → 'wrapper' | 'consumer'.

    명시 인자 우선(caller 가 이미 판정한 scope 재사용). 미지정 시 append_dev_process_event
    의 _norm_consumer_scope(단일 authority) 로 CLAUDE_PROJECT_DIR basename 휴리스틱 재사용.
    """
    if consumer_scope in ("wrapper", "consumer"):
        return consumer_scope
    return _norm_consumer_scope(None)


def _consumer_opt_in(environ=None):
    """consumer opt-in 판정 — CONSUMER_OPT_IN_ENV 가 truthy 일 때만 True (default False)."""
    env = os.environ if environ is None else environ
    return str(env.get(CONSUMER_OPT_IN_ENV, "")).strip().lower() in _TRUTHY


def dev_process_capture_enabled(consumer_scope=None, environ=None):
    """dev-process capture 활성 여부 — 모든 capture 경로가 write 前 consult 하는 단일 게이트.

    반환 True 규칙 (ADR-155 §결정 8 α 비대칭):
      · wrapper-self  → 무조건 True (always-on, checkout-identity 파생, env 미consult).
      · consumer      → CONSUMER_OPT_IN_ENV truthy 시에만 True (opt-in default-false).

    non-blocking: 어떤 판정 오류도 raise 하지 않는다 — 예외 시 보수적으로 False(미기록) 반환
    (capture 실패가 원 흐름 차단 금지 — ADR-115 record-only).
    """
    try:
        scope = resolve_consumer_scope(consumer_scope)
        if scope == "wrapper":
            return True  # always-on dogfood — user-settable 아님 (T-DPE-9)
        return _consumer_opt_in(environ)  # consumer: opt-in, default False
    except Exception:  # pragma: no cover — graceful degrade → 미기록(보수적)
        return False


# ─────────────────────── self-test (execution-backed) ───────────────────────
def _self_test():
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # wrapper = always-on (env 무관)
    check(dev_process_capture_enabled(consumer_scope="wrapper", environ={}) is True,
          "[a1] wrapper always-on 아님")
    check(dev_process_capture_enabled(consumer_scope="wrapper",
                                      environ={CONSUMER_OPT_IN_ENV: "0"}) is True,
          "[a2] wrapper 가 env=0 에 의해 꺼짐 (user-settable 위반 — T-DPE-9)")

    # consumer = opt-in default-false
    check(dev_process_capture_enabled(consumer_scope="consumer", environ={}) is False,
          "[a3] consumer default-false 아님")
    check(dev_process_capture_enabled(consumer_scope="consumer",
                                      environ={CONSUMER_OPT_IN_ENV: "1"}) is True,
          "[a4] consumer opt-in(env=1) 미활성")
    check(dev_process_capture_enabled(consumer_scope="consumer",
                                      environ={CONSUMER_OPT_IN_ENV: "true"}) is True,
          "[a5] consumer opt-in(env=true) 미활성")
    check(dev_process_capture_enabled(consumer_scope="consumer",
                                      environ={CONSUMER_OPT_IN_ENV: "nope"}) is False,
          "[a6] consumer non-truthy env 가 활성됨")

    # scope resolution passthrough
    check(resolve_consumer_scope("wrapper") == "wrapper", "[a7] scope wrapper passthrough 실패")
    check(resolve_consumer_scope("consumer") == "consumer", "[a8] scope consumer passthrough 실패")

    if failures:
        print("[dev_process_capture_activation --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1
    print("[dev_process_capture_activation --self-test] PASS "
          "(wrapper always-on env-immune; consumer opt-in default-false; scope passthrough)")
    return 0


def main():
    import argparse
    p = argparse.ArgumentParser(description="dev-process capture 활성 게이트 (CFP-2687 Phase 2)")
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    p.add_argument("--check", action="store_true",
                   help="현재 환경 활성 여부 출력 (enabled/disabled)")
    args = p.parse_args()
    if args.self_test:
        return _self_test()
    if args.check:
        print("enabled" if dev_process_capture_enabled() else "disabled")
        return 0
    print("enabled" if dev_process_capture_enabled() else "disabled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
