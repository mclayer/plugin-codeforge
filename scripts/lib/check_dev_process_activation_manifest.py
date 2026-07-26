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
_PLAYBOOK_REL = os.path.join("docs", "orchestrator-playbook.md")
_APPEND_MODULE = "append_dev_process_event"
_EMIT_MODULE = "emit_dev_process_event"

# activation hook anchor — PostToolUse hook command 이 이 substring 을 포함해야 함 (HookDev
# 배선 = `posttooluse-dev-process-capture`, hyphen). underscore 변형도 관용 매칭.
_HOOK_ANCHOR_RE = re.compile(r"dev[-_]process", re.IGNORECASE)

# ─── ACT-3 (Port-B agent-emit 배선 — CFP-2817 additive) ──────────────────────────
# ★ACT-3 fail-VISIBLE 부재판별 (Port-A born-drift seal 과 대칭): Port-B 배선이 ABSENT 면 silent-skip
#   (vacuous GREEN)이 아니라 RED violation 으로 **가시화**한다 — (a) §14.7 render flow 에 emit step 부재
#   → ACT-3a RED, (b) derive_seq seq-채번 SSOT 부재 → ACT-3a RED, (c) lane plugin agent surface 로 emit
#   호출 누출 → ACT-3b RED. 부재를 침묵 통과시키지 않음(landed≠activated 위장 차단)이 본 축의 존재 이유다.
# ★ACT-3 HONESTY CEILING (over-claim 금지): ACT-3 판정은 전부 **정적**이다 — (a)=playbook anchor grep,
#   (b)=emit 모듈 import 후 derive_seq attr present, (c)=agent surface grep. 즉 "Port-B 배선 present +
#   call-site containment" 를 정적 판정할 뿐, 매 6-point 전이마다 실제 emit 되는 runtime always-on 동작
#   (무결)은 정적 증명 불가 — 실 emit 증명 = Phase 2 test lane + AC-1 실 세션 원장 실측(역할 분리).
# ACT-3a: playbook §14.7 render flow 에 dev-process Port-B emit step present anchor.
_PORTB_ANCHOR_RE = re.compile(
    r"emit_dev_process_event|dev-process(?:-event)?\s+(?:agent-)?emit", re.IGNORECASE)
# ACT-3b: lane plugin agent surface(plugins/*/agents/**) 에서 emit invocation/import/direct-call 금지
#   (Orchestrator-owned 표면 독점 — ADR-039 §결정3 / REC-1). doc file-listing(.py 뒤 주석) FP 회피 위해
#   CLI 는 subcommand/flag 동반만 매칭. helper 직접 call 5종도 deny(lane 이 emit() 우회 = policy_violation).
_EMIT_INVOCATION_RE = re.compile(
    r"emit_dev_process_event\.py\s+(?:lane-transition|verdict|defect-finding|--)"
    r"|(?:^|[^\w.])import\s+emit_dev_process_event\b"
    r"|from\s+emit_dev_process_event\s+import"
    r"|emit_(?:lane_transition|verdict|defect_finding|fix_transition|final_artifact)\s*\(",
    re.MULTILINE,
)


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
    """계약 §10.2 wrapper always-on 활성 정책 선언 present bool (always-on gate 정책 anchor)."""
    # §10(writer 권한 + telemetry 활성) 또는 §10.2 구간에 always-on + wrapper 동시 선언
    # (renumber: 구 §9 writer+telemetry→§10, CFP-2687 doc-section-schema §4=변경규칙 FIX)
    m = re.search(r"(?m)^##\s*10\.\s.*?(?=^##\s*11\.\s|\Z)", contract_body, re.S)
    section9 = m.group(0) if m else contract_body
    has_always_on = bool(re.search(r"always[-\s]?on", section9, re.IGNORECASE))
    has_wrapper = "wrapper" in section9
    return has_always_on and has_wrapper


# ─────────────────────── ACT-3: Port-B (agent-emit) 배선 판정 (CFP-2817 additive) ─────────

def import_emit_surface(repo_root, import_fn=None):
    """emit_dev_process_event import → (has_derive_seq_bool, importable_bool).

    Port-B 호출 표면(D6-a CLI + `derive_seq` seq 채번 SSOT) present 정적 확인. import 실패 → (False, False).
    honesty ceiling: import 가능 + derive_seq present = '호출 표면 배선 present'이지 runtime emit 무결 아님.
    """
    if import_fn is not None:
        return import_fn(repo_root)
    lib_dir = os.path.join(repo_root, "scripts", "lib")
    if not os.path.isdir(lib_dir):
        lib_dir = os.path.dirname(os.path.abspath(__file__))
    inserted = False
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
        inserted = True
    try:
        import importlib
        mod = importlib.import_module(_EMIT_MODULE)
        return callable(getattr(mod, "derive_seq", None)), True
    except Exception:
        return False, False
    finally:
        if inserted and lib_dir in sys.path:
            try:
                sys.path.remove(lib_dir)
            except ValueError:
                pass


def parse_portb_wiring(playbook_body):
    """playbook §14.7 render flow 에 dev-process Port-B emit step present bool (ACT-3a).

    §14.7 region(### 14.7 ~ 다음 ### 14.8) 안에 emit_dev_process_event 호출 anchor 존재 확인.
    Orchestrator 가 6-point 전이 시점에 실제로 emit 을 호출하도록 배선됐는가의 정적 증거
    (hook Port-A 의 ACT-1[hooks.json 등록]에 대응하는 Port-B 대칭). honesty ceiling: '배선 present'.
    """
    if not playbook_body:
        return False
    m = re.search(r"(?ms)^###\s*14\.7\b.*?(?=^###\s*14\.8\b|\Z)", playbook_body)
    region = m.group(0) if m else playbook_body
    return bool(_PORTB_ANCHOR_RE.search(region))


def scan_portb_containment(repo_root):
    """lane plugin agent surface(plugins/**/agents/**) 에서 Port-B emit invocation/import 정적 scan → 위반 파일 list (ACT-3b).

    emit 호출은 Orchestrator-owned 표면 독점(ADR-039 §결정3 writer monopoly / REC-1). lane plugin
    agent prompt·subagent code 에서 emit_dev_process_event 호출/import/직접 helper call 발견 = 위반.
    honesty ceiling: 정적 grep — 런타임 call-graph 아님(우회 표기 false-neg 잔여 인정).
    """
    plugins_dir = os.path.join(repo_root, "plugins")
    if not os.path.isdir(plugins_dir):
        return []
    violations = []
    for dirpath, _dirnames, filenames in os.walk(plugins_dir):
        rel_dir = "/" + os.path.relpath(dirpath, repo_root).replace("\\", "/") + "/"
        if "/agents/" not in rel_dir:
            continue
        for fn in filenames:
            if not (fn.endswith(".md") or fn.endswith(".py")):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, encoding="utf-8") as f:
                    body = f.read()
            except OSError:
                continue
            if _EMIT_INVOCATION_RE.search(body):
                violations.append(os.path.relpath(fpath, repo_root).replace("\\", "/"))
    return sorted(violations)


# ─────────────────────── check 조립 (구조 입력) ──────────────────────────────

def evaluate(contract_present, contract_body, row_keys, importable,
             hook_registered, hook_matcher, always_on_declared,
             portb_wired=None, emit_has_derive_seq=None, portb_containment_violations=None):
    """활성화 manifest 판정 → (violations, state_report dict).

    state_report = landing/activation 정직 구분 보고용.
    ACT-3(CFP-2817 additive): Port-B(agent-emit) 배선 present + call-site containment.
      기존 ACT-1(hook Port-A)/ACT-2(always-on gate) 판정 로직 무손상.
    """
    violations = []
    if portb_containment_violations is None:
        portb_containment_violations = []

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

    # ── ACT-2: always-on gate 정책 선언 (§10.2 wrapper always-on) ──
    if not always_on_declared:
        violations.append(
            "(ACT-2) 계약 §10.2 wrapper always-on 활성 정책 선언 부재 — always-on gate anchor 없음 = RED"
        )

    # ── ACT-3: Port-B (agent-emit) 배선 present + call-site containment (CFP-2817 additive) ──
    #   honesty ceiling 계승: "배선 present"(정적) 검증이지 runtime always-on emit 무결 단정 아님
    #   (실 emit 증명 = Phase 2 test lane + AC-1 실 세션 원장 실측, 역할 분리).
    #   None = ACT-3 입력 미제공(legacy caller) → ACT-3 skip(기존 ACT-1/2 판정 무손상).
    if portb_wired is not None and not portb_wired:
        violations.append(
            "(ACT-3a) playbook §14.7 render flow 에 dev-process Port-B emit step 미배선 — "
            "Orchestrator 6-point 전이 시점 emit 호출 부재 = Port-B NOT activated (§8.10 landing≠activation). "
            "fail-VISIBLE 부재판별: silent-skip(vacuous GREEN) 대신 RED 가시화 "
            "(정적 anchor 판정 — runtime always-on emit 무결 단정 아님). RED"
        )
    if emit_has_derive_seq is not None and not emit_has_derive_seq:
        violations.append(
            "(ACT-3a) %s.derive_seq (seq 채번 SSOT) 미import/부재 — Port-B 호출 표면 파손 = RED "
            "(fail-VISIBLE: import present 정적 판정, runtime 무결 아님)"
            % _EMIT_MODULE
        )
    for vf in portb_containment_violations:
        violations.append(
            "(ACT-3b) Port-B emit invocation 이 lane plugin agent surface 에 유입 — %s "
            "(call-site containment 위반: emit 호출 = Orchestrator-owned 표면 독점, ADR-039 §결정3 / REC-1; "
            "정적 surface grep 판정 — 우회 표기 false-neg 잔여 인정). RED"
            % vf
        )

    landed = contract_present and importable and bool(row_keys)
    activated = landed and hook_registered and always_on_declared
    # Port-B activation = 배선 present + seq SSOT present + lane-surface 누출 0 (Port-A activated 와 disjoint 축)
    portb_activated = (bool(portb_wired) and bool(emit_has_derive_seq)
                       and not portb_containment_violations)
    state = {
        "contract_present": contract_present,
        "impl_importable": importable,
        "row_keys_n": len(row_keys or ()),
        "hook_registered": hook_registered,
        "hook_matcher": hook_matcher,
        "always_on_declared": always_on_declared,
        "landed": landed,
        "activated": activated,
        "portb_wired": portb_wired,
        "emit_has_derive_seq": emit_has_derive_seq,
        "portb_containment_violations": list(portb_containment_violations),
        "portb_activated": portb_activated,
    }
    return violations, state


def _print_state(state):
    print("  landing   : contract_present=%s / impl_importable=%s (_ROW_KEYS=%d) → landed=%s"
          % (state["contract_present"], state["impl_importable"],
             state["row_keys_n"], state["landed"]))
    print("  activation: hook_registered=%s (matcher=%r) / always_on_declared=%s → activated=%s"
          % (state["hook_registered"], state["hook_matcher"],
             state["always_on_declared"], state["activated"]))
    if state.get("portb_wired") is not None or state.get("emit_has_derive_seq") is not None:
        print("  Port-B    : playbook §14.7 emit-wired=%s / derive_seq present=%s / "
              "lane-surface 누출=%d → portb_activated=%s (정적 배선 present, runtime 무결 아님)"
              % (state.get("portb_wired"), state.get("emit_has_derive_seq"),
                 len(state.get("portb_containment_violations") or ()), state.get("portb_activated")))


# ─────────────────────── check 진입 ──────────────────────────────────────────

def _load_inputs(repo_root, hooks_json_override=None, import_fn=None,
                 playbook_override=None, emit_surface_fn=None, containment_override=None):
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

    # ── ACT-3 inputs (CFP-2817 additive) ──
    if playbook_override is not None:
        playbook_body = playbook_override
    else:
        playbook_path = os.path.join(repo_root, _PLAYBOOK_REL)
        playbook_body = ""
        if os.path.isfile(playbook_path):
            try:
                with open(playbook_path, encoding="utf-8") as f:
                    playbook_body = f.read()
            except OSError:
                playbook_body = ""
    portb_wired = parse_portb_wiring(playbook_body)
    emit_has_derive_seq, _emit_importable = import_emit_surface(repo_root, import_fn=emit_surface_fn)
    if containment_override is not None:
        containment = list(containment_override)
    else:
        containment = scan_portb_containment(repo_root)

    return (contract_present, contract_body, row_keys, importable,
            hook_registered, hook_matcher, always_on,
            portb_wired, emit_has_derive_seq, containment)


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
          "(landed→impl importable) ∧ Port-A activated(hook 배선 + always-on gate 선언) "
          "∧ Port-B activated(§14.7 emit 배선 + derive_seq SSOT + lane-surface 누출 0). "
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

    # ── NEG-PORTB: playbook §14.7 emit 배선 부재 시뮬 → ACT-3a RED (Port-B NOT activated) ──
    np_inputs = _load_inputs(repo_root, playbook_override="### 14.7 Render flow\n(emit step 부재)\n### 14.8 x")
    np_v, np_state = evaluate(*np_inputs)
    results.append(("NEG-PORTB (§14.7 emit 배선 부재 → ACT-3a RED)", True, np_v, np_state))

    # ── NEG-CONTAINMENT: lane plugin agent surface 에 emit 호출 누출 시뮬 → ACT-3b RED ──
    nc_inputs = _load_inputs(repo_root,
                             containment_override=["plugins/codeforge-review/agents/LeakAgent.md"])
    nc_v, nc_state = evaluate(*nc_inputs)
    results.append(("NEG-CONTAINMENT (lane surface emit 누출 → ACT-3b RED)", True, nc_v, nc_state))

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
              "positive GREEN + NEG-DRIFT/NEG-HOOK/NEG-PORTB/NEG-CONTAINMENT RED "
              "(discriminating: born-drift seal + Port-A activation + Port-B 배선/containment).")
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
