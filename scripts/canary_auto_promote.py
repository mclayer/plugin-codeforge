#!/usr/bin/env python3
"""
scripts/canary_auto_promote.py
CFP-1196 — canary auto-promote: criteria 4-tuple 집계 + 안전장치 4 AND + signature 생성

ADR-061 (multi-line Python > 5줄 → 외부 .py 의무):
  criteria 4-tuple gate_state 집계 = multi-line 로직

S7 = S4 (check_rollback_signal.py) 의 mirror — trigger 방향만 반대.
  S4: 임계 위반 → rollback trigger
  S7: criteria 충족 → promote trigger

§3.3 안전장치 4 AND:
  safety_1: criteria 4-tuple all pass OR (pass + n_a) = 1+ fail 시 false (보수적)
  safety_2: 보존 window 내 (기존 hook check_within_retention 위임 — 본 스크립트 미평가)
  safety_3: 사후 알림 가용성 (promote 전 GH_TOKEN / gh CLI 존재 확인, pre-promote check)
  safety_4: kill-switch off (filesystem flag 부재 AND config auto_promote_enabled=true)
  promote = safety_1 AND safety_2 AND safety_3 AND safety_4

§3.7 kill-switch OR disable (보수적):
  filesystem flag: .codeforge/auto-promote.disabled (file 존재 = disable)
  config flag: deploy.canary.auto_promote_enabled=false

§3.3 aggregation (CFP-991 promotion-criteria-4tuple.md verbatim 재사용 — CX-1196-3):
  criteria_met = ALL(sub.gate_state IN {pass, n_a}) AND ANY(sub.gate_state == pass)
  1+ fail     => criteria_met = false (promote abort, EC-1 보수적 정지)
  all n_a     => criteria_met = false (pass 필수)

signature: sha256("<signal>|<measured>|<window>") | head -c 16
  (check-rollback-signal.py 답습 — TC-16)

§7.4 empirical-source:
  보존 window 3h: ADR-087 §결정 5 (dimension: lifecycle)
  host 수: consumer overlay deploy.canary.subset (dimension: count, default=1)
  rate: 사후 알림 1회/배포 (dimension: rate)

출력 포맷 (stdout — bash orchestration 이 파싱):
  criteria_met=<true|false>
  gate_states=<functional:pass|fail|n_a,security:pass|fail|n_a,...>
  safety_1=<true|false>
  safety_3=<true|false>
  safety_4=<true|false>
  kill_switch_active=<true|false>
  notification_available=<true|false>
  signature=<16-char hex>

exit codes (ADR-060 §결정 15 3-tier):
  0 = 정상 (criteria 집계 완료 — promote/정지 결정은 bash orchestration)
  1 = reserved (current scope 미사용)
  2 = SETUP error (의존성 부재 / yaml parse error / 인수 오류)
"""

import argparse
import hashlib
import os
import shutil
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="CFP-1196 canary auto-promote — criteria 4-tuple 집계 + 안전장치 평가"
    )
    # criteria gate_state (4-tuple — L1 helper 재사용 결과 전달)
    p.add_argument("--functional", type=str, default="n_a",
                   help="functional gate_state: pass | fail | n_a")
    p.add_argument("--security", type=str, default="n_a",
                   help="security gate_state: pass | fail | n_a")
    p.add_argument("--monitoring", type=str, default="n_a",
                   help="monitoring gate_state (filesystem-only, 0 API call): pass | fail | n_a")
    p.add_argument("--testing", type=str, default="n_a",
                   help="testing gate_state: pass | fail | n_a")
    # 안전장치 관련
    p.add_argument("--kill-switch-flag", type=str, default="",
                   help="filesystem kill-switch flag 경로 (존재 시 kill-switch 활성)")
    p.add_argument("--config-disabled", type=str, default="false",
                   help="config auto_promote_enabled=false 시 'true' (yaml.safe_load 결과)")
    p.add_argument("--config-yaml-path", type=str, default="",
                   help="project.yaml 경로 (.claude/_overlay/project.yaml)")
    # 서명용 context
    p.add_argument("--window", type=str, default="10800",
                   help="보존 window (초, default 10800=3h) [empirical-source: ADR-087 §결정 5]")
    # test override
    p.add_argument("--mock-notification-available", type=str, default="",
                   help="test override: 'true'|'false' — safety_3 pre-promote check mock")
    return p.parse_args()


def read_config_disabled(config_yaml_path: str) -> bool:
    """
    project.yaml (.claude/_overlay/project.yaml) 의 deploy.canary.auto_promote_enabled 읽기.
    yaml.safe_load 사용 (ADR-070 — grep 금지).

    반환: True = config kill-switch 활성 (auto_promote_enabled=false), False = enabled
    - 파일 부재 시 False (default enabled)
    - key 부재 시 False (default enabled)
    - auto_promote_enabled=false 명시 시 True (kill-switch)
    - yaml.safe_load 실패 시 exit 2 (SETUP error, fail-loud)
    """
    if not config_yaml_path or not os.path.exists(config_yaml_path):
        return False

    try:
        import yaml  # PyYAML (pyyaml) — CI 환경 표준 의존성
        with open(config_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        print("[ERROR] PyYAML 미설치 — config yaml 읽기 불가 (pip install pyyaml)", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"[ERROR] project.yaml yaml.safe_load 실패: {e}", file=sys.stderr)
        sys.exit(2)
    except (OSError, UnicodeError) as e:
        print(f"[ERROR] project.yaml 읽기 실패 (OSError/UnicodeError): {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, dict):
        return False

    deploy_block = data.get("deploy", {})
    if not isinstance(deploy_block, dict):
        return False

    canary_block = deploy_block.get("canary", {})
    if not isinstance(canary_block, dict):
        return False

    # auto_promote_enabled=false 명시 시만 disabled=True
    enabled = canary_block.get("auto_promote_enabled", True)
    if isinstance(enabled, bool):
        return not enabled
    return False


def validate_gate_state(val: str, field: str) -> str:
    """gate_state 값 검증 — pass | fail | n_a 만 허용"""
    val = val.strip().lower()
    if val not in ("pass", "fail", "n_a"):
        print(
            f"[ERROR] --{field} 값 '{val}' 유효하지 않음 — pass | fail | n_a 만 허용",
            file=sys.stderr,
        )
        sys.exit(2)
    return val


def check_safety_1(
    functional: str,
    security: str,
    monitoring: str,
    testing: str,
) -> tuple[bool, dict[str, str]]:
    """
    안전장치 1: criteria 4-tuple all pass OR (pass + n_a)
    aggregation (CFP-991 promotion-criteria-4tuple.md verbatim 재사용 — CX-1196-3):
      criteria_met = ALL(gate_state IN {pass, n_a}) AND ANY(gate_state == pass)
      1+ fail => criteria_met = false (보수적 정지)
      all n_a => criteria_met = false (pass 최소 1개 필수)

    반환: (safety_1, gate_states_dict)
    """
    gate_states = {
        "functional": functional,
        "security": security,
        "monitoring": monitoring,
        "testing": testing,
    }

    # 1+ fail 시 즉시 false
    if any(v == "fail" for v in gate_states.values()):
        return False, gate_states

    # all pass or n_a + at least 1 pass
    has_pass = any(v == "pass" for v in gate_states.values())
    all_valid = all(v in ("pass", "n_a") for v in gate_states.values())

    return (all_valid and has_pass), gate_states


def check_safety_3(mock_override: str) -> bool:
    """
    안전장치 3 (pre-promote check, F-1196-3 — I-1 unconditional guard):
    promote 실행 전 notification mechanism 가용성 확인 의무.
      - GH_TOKEN 환경변수 존재 (token presence, 0 API call)
      - gh CLI 존재 확인 (shutil.which)
    알림 unavailable → safety_3=false → promote 금지 (무음 promote 차단)

    S4 safety_3("monitor 활성=항상 true") 와 disjoint:
      S4: 사후 rollback 알림 (rollback 이후 보고) = mechanism presence 로 충족
      S7: 사전 promote gate (확대 전 가용성 확인 — 확대 후 무음 = 거버넌스 신뢰 위반)

    test override: --mock-notification-available='true'|'false'
    """
    if mock_override.strip().lower() == "true":
        return True
    if mock_override.strip().lower() == "false":
        return False

    # 실 환경: GH_TOKEN presence + gh CLI presence (0 API call)
    gh_token = os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    gh_cli_present = shutil.which("gh") is not None

    return bool(gh_token) and gh_cli_present


def check_safety_4(kill_switch_flag: str, config_disabled: bool) -> tuple[bool, bool]:
    """
    안전장치 4: kill-switch off
    OR disable 보수적 (둘 중 하나라도 disable = kill-switch 활성)
    반환: (safety_4, kill_switch_active)
    """
    flag_active = False
    if kill_switch_flag:
        flag_active = os.path.exists(kill_switch_flag)

    config_active = config_disabled

    kill_switch_active = flag_active or config_active
    safety_4 = not kill_switch_active
    return safety_4, kill_switch_active


def compute_signature(functional: str, security: str, monitoring: str, testing: str, window: int) -> str:
    """
    signature = sha256("<signal>|<measured>|<window>") | head -c 16
    (check_rollback_signal.py 답습 — TC-16)
    signal = "canary_promote"
    measured = gate_states 문자열
    """
    measured = f"{functional},{security},{monitoring},{testing}"
    raw = f"canary_promote|{measured}|{window}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return digest[:16]


def safe_int(val: str, default: int) -> int:
    try:
        return int(val)
    except ValueError:
        return default


def main() -> int:
    args = parse_args()

    # gate_state 파싱 + 검증
    functional = validate_gate_state(args.functional, "functional")
    security = validate_gate_state(args.security, "security")
    monitoring = validate_gate_state(args.monitoring, "monitoring")
    testing = validate_gate_state(args.testing, "testing")

    window = safe_int(args.window, 10800)

    # config kill-switch: --config-disabled 명시적 "true" = override (test mock)
    config_disabled_override = args.config_disabled.lower() in ("true", "1", "yes")
    if config_disabled_override:
        config_disabled = True
    else:
        config_disabled = read_config_disabled(args.config_yaml_path)

    # 안전장치 4 (kill-switch) — 가장 먼저 평가 (§3.7 kill-switch 우선, fast-skip)
    safety_4, kill_switch_active = check_safety_4(
        args.kill_switch_flag, config_disabled
    )

    # 안전장치 3 (pre-promote notification availability check, F-1196-3)
    notification_available = check_safety_3(args.mock_notification_available)
    safety_3 = notification_available

    # 안전장치 1 (criteria 4-tuple aggregation — CFP-991 verbatim 재사용)
    safety_1, gate_states = check_safety_1(functional, security, monitoring, testing)

    # criteria_met = 안전장치 1 결과 (safety_2 = hook 위임, 본 스크립트 미평가)
    criteria_met = safety_1

    # signature 계산
    signature = compute_signature(functional, security, monitoring, testing, window)

    # gate_states 문자열 (bash 파싱용)
    gate_states_str = ",".join(f"{k}:{v}" for k, v in gate_states.items())

    # 출력 (bash orchestration 파싱용)
    print(f"criteria_met={str(criteria_met).lower()}")
    print(f"gate_states={gate_states_str}")
    print(f"safety_1={str(safety_1).lower()}")
    print(f"safety_3={str(safety_3).lower()}")
    print(f"safety_4={str(safety_4).lower()}")
    print(f"kill_switch_active={str(kill_switch_active).lower()}")
    print(f"notification_available={str(notification_available).lower()}")
    print(f"signature={signature}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
