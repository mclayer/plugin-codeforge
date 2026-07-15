#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_dev_process_activation_manifest.py — dev-process 활성화 manifest (§8.10 landing≠activation)
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A / ADR-155 §결정 8 + change-plan §8.10
# SSOT: change-plan §8.2↔§8.10 상호참조 + ADR-155 「검증 채널」 (impl-ABSENT born-drift 위임 대상)
#
# ★존재 이유 (D1 이 봉인 못 하는 hole 을 봉쇄):
#   D1(check_dev_process_event_schema.py)의 계약==구현 parity self-test 는 impl-PRESENT 만
#   non-skippable — **append impl 부재 시 parity 자체가 skip → D1 이 vacuous GREEN** 되는
#   born-drift hole 이 남는다. 본 manifest 가 그 hole 을 봉쇄한다:
#     계약 landed(파일 존재) → append impl 반드시 importable(`_ROW_KEYS` present).
#     계약만 있고 impl 부재 = RED (silent-skip → failure 로 전환).
#
# ★landing ≠ activation (§8.10 dark-path — 정직 구분):
#   landed  = 파일 존재 (계약 .md + append primitive 모듈).
#   activated = hook 배선(PostToolUse dev-process capture) + always-on gate 선언.
#   본 manifest 는 두 상태를 **정직하게 구분 보고**한다 — "파일이 있으니 활성"이라는 위장 금지.
#   (파일 landing 만으로 관측이 켜졌다고 주장하지 않는다 — AC-24 gap motivation-only 정합.)
#
# ★HONESTY CEILING (over-claim 금지):
#   본 manifest 는 hook 이 hooks.json 에 **등록**됐음(정적 배선)을 확인한다. hook 이 매 tool-call
#   마다 실제 emit 하는 runtime always-on **동작**은 정적으로 증명 불가 — hook/emit 계층(HookDev)
#   소관이며 execution-backed 증명 = Phase 2 test lane. 즉 본 gate 는 "배선 present" 를 검증하지
#   "runtime 무결 always-on" 을 단정하지 않는다.
#
# 불변식: 0 API call, local read only. 3-tier exit: 0 PASS / 1 violation / 2 setup error.
#
# 사용:
#   python3 check_dev_process_activation_manifest.py [--repo-root <p>]        # check
#   python3 check_dev_process_activation_manifest.py --selftest [--repo-root <p>]  # discriminating

import argparse
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_CONTRACT_REL = os.path.join("docs", "inter-plugin-contracts", "dev-process-event-v1.md")
_HOOKS_JSON_REL = os.path.join("hooks", "hooks.json")
_APPEND_MODULE = "append_dev_process_event"

# activation hook anchor — PostToolUse hook command 이 이 substring 을 포함해야 함 (HookDev
# 배선 = `posttooluse-dev-process-capture`, hyphen). underscore 변형도 관용 매칭.
_HOOK_ANCHOR_RE = re.compile(r"dev[-_]process", re.IGNORECASE)


# ─────────────────────── code-anchor importability (born-drift seal) ──────────

def import_row_keys(repo_root):
    """append_dev_process_event._ROW_KEYS import → (tuple|None, importable_bool).

    모듈 import 실패(파일 부재/ImportError) → (None, False) = impl-ABSENT.
    import 성공하나 _ROW_KEYS 부재/공집합 → ((), True) = impl-present anchor 파손.
    """
    lib_dir = os.path.join(repo_root, "scripts", "lib")
    if not os.path.isdir(lib_dir):
        lib_dir = os.path.dirname(os.path.abspath(__file__))
    inserted = False
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
        inserted = True
    try:
        import importlib
        mod = importlib.import_module(_APPEND_MODULE)
        return tuple(getattr(mod, "_ROW_KEYS", ())), True
    except Exception:
        return None, False
    finally:
        if inserted and lib_dir in sys.path:
            try:
                sys.path.remove(lib_dir)
            except ValueError:
                pass


# ─────────────────────── hooks.json activation 배선 파싱 ──────────────────────

def find_dev_process_posttool_hook(hooks_json_obj):
    """hooks.json 객체에서 PostToolUse dev-process capture hook 등록 여부 → (bool, matcher|None).

    PostToolUse block 의 각 entry.hooks[].command 문자열에 dev[-_]process anchor 존재 시 True.
    """
    if not isinstance(hooks_json_obj, dict):
        return False, None
    hooks_root = hooks_json_obj.get("hooks")
    if not isinstance(hooks_root, dict):
        return False, None
    posttool = hooks_root.get("PostToolUse")
    if not isinstance(posttool, list):
        return False, None
    for entry in posttool:
        if not isinstance(entry, dict):
            continue
        matcher = entry.get("matcher")
        for h in entry.get("hooks", []) or []:
            cmd = (h or {}).get("command", "") if isinstance(h, dict) else ""
            if isinstance(cmd, str) and _HOOK_ANCHOR_RE.search(cmd):
                return True, matcher
    return False, None


def parse_always_on_declared(contract_body):
    """계약 §9.2 wrapper always-on 활성 정책 선언 present bool (always-on gate 정책 anchor)."""
    # §9(writer 권한 + telemetry 활성) 또는 §9.2 구간에 always-on + wrapper 동시 선언
    m = re.search(r"(?m)^##\s*9\.\s.*?(?=^##\s*10\.\s|\Z)", contract_body, re.S)
    section9 = m.group(0) if m else contract_body
    has_always_on = bool(re.search(r"always[-\s]?on", section9, re.IGNORECASE))
    has_wrapper = "wrapper" in section9
    return has_always_on and has_wrapper


# ─────────────────────── check 조립 (구조 입력) ──────────────────────────────

def evaluate(contract_present, contract_body, row_keys, importable,
             hook_registered, hook_matcher, always_on_declared):
    """활성화 manifest 판정 → (violations, state_report dict).

    state_report = landing/activation 정직 구분 보고용.
    """
    violations = []

    # ── LAND-1: 계약 landed (파일 존재) ── (fail-closed, vacuous pass 금지)
    if not contract_present:
        violations.append(
            "(LAND-1) dev-process-event-v1.md 계약 미landed — 활성화 manifest 검증 대상 부재 "
            "(fail-closed RED, vacuous pass 금지)"
        )

    # ── DRIFT (CORE — D1 이 봉인 못 하는 hole): landed → impl importable ──
    if contract_present and not importable:
        violations.append(
            "(DRIFT/CORE) 계약 landed 이나 %s import 불가 (impl-ABSENT) — "
            "★D1 parity self-test 가 봉인 못 하는 born-drift hole. landed→impl importable "
            "위반 = RED (silent-skip → failure 전환)." % _APPEND_MODULE
        )
    if contract_present and importable and not (row_keys and len(row_keys) > 0):
        violations.append(
            "(DRIFT/CORE) %s import 되나 _ROW_KEYS 공집합/부재 — code anchor 파손 = RED"
            % _APPEND_MODULE
        )

    # ── ACT-1: PostToolUse dev-process capture hook 배선 (activation evidence) ──
    if not hook_registered:
        violations.append(
            "(ACT-1) hooks.json PostToolUse dev-process capture hook 미등록 — "
            "landed 이나 NOT activated (§8.10 landing≠activation). hook 배선 부재 = RED"
        )

    # ── ACT-2: always-on gate 정책 선언 (§9.2 wrapper always-on) ──
    if not always_on_declared:
        violations.append(
            "(ACT-2) 계약 §9.2 wrapper always-on 활성 정책 선언 부재 — always-on gate anchor 없음 = RED"
        )

    landed = contract_present and importable and bool(row_keys)
    activated = landed and hook_registered and always_on_declared
    state = {
        "contract_present": contract_present,
        "impl_importable": importable,
        "row_keys_n": len(row_keys or ()),
        "hook_registered": hook_registered,
        "hook_matcher": hook_matcher,
        "always_on_declared": always_on_declared,
        "landed": landed,
        "activated": activated,
    }
    return violations, state


def _print_state(state):
    print("  landing   : contract_present=%s / impl_importable=%s (_ROW_KEYS=%d) → landed=%s"
          % (state["contract_present"], state["impl_importable"],
             state["row_keys_n"], state["landed"]))
    print("  activation: hook_registered=%s (matcher=%r) / always_on_declared=%s → activated=%s"
          % (state["hook_registered"], state["hook_matcher"],
             state["always_on_declared"], state["activated"]))


# ─────────────────────── check 진입 ──────────────────────────────────────────

def _load_inputs(repo_root, hooks_json_override=None, import_fn=None):
    """실 파일에서 manifest 입력 수집 (selftest 는 override 주입)."""
    contract_path = os.path.join(repo_root, _CONTRACT_REL)
    contract_present = os.path.isfile(contract_path)
    contract_body = ""
    if contract_present:
        try:
            with open(contract_path, encoding="utf-8") as f:
                contract_body = f.read()
        except OSError:
            contract_present = False

    if import_fn is None:
        import_fn = import_row_keys
    row_keys, importable = import_fn(repo_root)

    if hooks_json_override is not None:
        hooks_obj = hooks_json_override
    else:
        hooks_path = os.path.join(repo_root, _HOOKS_JSON_REL)
        hooks_obj = None
        if os.path.isfile(hooks_path):
            try:
                with open(hooks_path, encoding="utf-8") as f:
                    hooks_obj = json.load(f)
            except (OSError, ValueError):
                hooks_obj = None
    hook_registered, hook_matcher = find_dev_process_posttool_hook(hooks_obj)
    always_on = parse_always_on_declared(contract_body)
    return (contract_present, contract_body, row_keys, importable,
            hook_registered, hook_matcher, always_on)


def cmd_check(args):
    repo_root = args.repo_root or "."
    inputs = _load_inputs(repo_root)
    violations, state = evaluate(*inputs)

    print("[check-dev-process-activation-manifest] landing≠activation 정직 구분:")
    _print_state(state)

    if violations:
        for v in violations:
            print("::warning::check-dev-process-activation-manifest: VIOLATION — %s" % v)
        print("")
        print("check-dev-process-activation-manifest: %d violation — "
              "dev-process 활성화 manifest 위반 (§8.10 landing≠activation)." % len(violations))
        sys.exit(1)

    print("check-dev-process-activation-manifest: PASS — landed ∧ born-drift-sealed "
          "(landed→impl importable) ∧ activated(hook 배선 + always-on gate 선언). "
          "★runtime always-on 동작 증명 = test lane (본 gate = 정적 배선 present 검증, over-claim 금지).")
    sys.exit(0)


# ─────────────────────── --selftest (discriminating negative-control) ─────────

def _selftest(args):
    """실 입력 positive GREEN + 2 negative-control RED 판별 증명.

    NEG-DRIFT: impl-ABSENT 시뮬(import_fn → (None, False)), 계약 present → DRIFT RED
               (= D1 이 봉인 못 하는 hole 을 본 manifest 가 잡음).
    NEG-HOOK : hooks.json 에 dev-process PostToolUse hook 없는 상태 시뮬 → ACT-1 RED.
    """
    repo_root = args.repo_root or "."
    results = []

    # ── positive: 실 입력 → GREEN ──
    pos_inputs = _load_inputs(repo_root)
    pos_v, pos_state = evaluate(*pos_inputs)
    results.append(("POSITIVE (real inputs → GREEN)", False, pos_v, pos_state))

    # ── NEG-DRIFT: append impl 부재 시뮬 (계약 present 유지) → born-drift seal RED ──
    def _absent_import(_root):
        return None, False
    nd_inputs = _load_inputs(repo_root, import_fn=_absent_import)
    nd_v, nd_state = evaluate(*nd_inputs)
    results.append(("NEG-DRIFT (impl-ABSENT + 계약 present → DRIFT/CORE RED)", True, nd_v, nd_state))

    # ── NEG-HOOK: dev-process hook 미등록 hooks.json 시뮬 → ACT-1 RED ──
    empty_hooks = {"hooks": {"PostToolUse": [
        {"matcher": "Bash", "hooks": [
            {"type": "command", "command": "run-hook.cmd some-other-hook"}]}]}}
    nh_inputs = _load_inputs(repo_root, hooks_json_override=empty_hooks)
    nh_v, nh_state = evaluate(*nh_inputs)
    results.append(("NEG-HOOK (dev-process hook 미등록 → ACT-1 RED)", True, nh_v, nh_state))

    all_ok = True
    print("[check-dev-process-activation-manifest --selftest] discriminating negative-control")
    print("=" * 78)
    for label, expect_red, viols, state in results:
        got_red = len(viols) > 0
        ok = (got_red == expect_red)
        all_ok = all_ok and ok
        print("  [%s] %-56s → %s" % ("OK" if ok else "FAIL", label, "RED" if got_red else "GREEN"))
        _print_state(state)
        for v in viols:
            print("        · %s" % v)
    print("=" * 78)
    if all_ok:
        print("[check-dev-process-activation-manifest --selftest] PASS — "
              "positive GREEN + NEG-DRIFT/NEG-HOOK RED (discriminating: born-drift seal + activation).")
        return 0
    print("[check-dev-process-activation-manifest --selftest] FAIL — 판별성 위반.")
    return 1


def main():
    p = argparse.ArgumentParser(
        description="dev-process 활성화 manifest (CFP-2687 Phase 2 — §8.10 landing≠activation)"
    )
    p.add_argument("--selftest", action="store_true",
                   help="discriminating negative-control (NEG-DRIFT + NEG-HOOK RED 증명)")
    p.add_argument("--repo-root", default=".", help="repo root (default 현재 디렉터리)")
    p.add_argument("command", nargs="?", default="check", help=argparse.SUPPRESS)

    args = p.parse_args()
    if args.selftest:
        sys.exit(_selftest(args))
    cmd_check(args)


if __name__ == "__main__":
    main()
