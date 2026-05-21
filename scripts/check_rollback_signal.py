#!/usr/bin/env python3
"""
scripts/check_rollback_signal.py
CFP-1193 — rollback signal monitor: 임계 감지 + 안전장치 4 AND + signature 생성

ADR-061 (multi-line Python > 5줄 → 외부 .py 의무):
  burn rate = error budget 소진율/window 산술 = multi-line 로직

§3.3 안전장치 4 AND:
  safety_1: 에러율 OR burn_rate 임계 초과 (정량 — 모달 어휘 금지, ADR-064)
  safety_2: 보존 기간 내 (기존 hook check_within_retention 위임 — 본 스크립트 미평가)
  safety_3: 사후 알림 mechanism 존재 = monitor 활성 = 항상 true
  safety_4: kill-switch off (filesystem flag 부재 AND config disabled 아님)
  trigger = safety_1 AND safety_2 AND safety_3 AND safety_4

§3.4 kill-switch OR disable (보수적):
  filesystem flag: .codeforge/auto-rollback.disabled (기본 경로)
  config flag: deploy.auto_rollback.enabled=false

signature: sha256("<signal_type>|<measured>|<window>") | head -c 16
  (check-channel-drift.sh 답습 — §8.1 TC-9)

§7.4 empirical-source:
  에러율 임계 구체값: consumer SLO (overlay) — 본 스크립트 = 형식+비교만
  burn_rate 임계 1.0 (dimension: rate): consumer SLO — 형식만 제공
  window 3600s (1h) default (dimension: lifecycle): 측정 rolling window

출력 포맷 (stdout — bash orchestration 이 파싱):
  signal_detected=<true|false>
  signal_type=<error_rate|burn_rate|none>
  measured=<float>
  threshold=<float>
  window=<int>
  safety_1=<true|false>
  safety_3=<true|false>
  safety_4=<true|false>
  kill_switch_active=<true|false>
  signature=<16-char hex>

exit codes (ADR-060 §결정 15 3-tier):
  0 = 정상 (임계 미초과 또는 임계 초과 + 신호 감지 완료)
  1 = reserved (current scope 미사용)
  2 = SETUP error (의존성 부재 / yaml parse error / 인수 오류)
"""

import argparse
import hashlib
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="CFP-1193 rollback signal monitor — 임계 감지 + 안전장치 평가"
    )
    p.add_argument("--error-rate", type=str, default="0.0",
                   help="현재 에러율 (예: 0.05 = 5%%)")
    p.add_argument("--error-rate-threshold", type=str, default="",
                   help="에러율 임계 (빈 문자열 = 미정의 → safety_1=false)")
    p.add_argument("--burn-rate", type=str, default="0.0",
                   help="현재 latency burn rate")
    p.add_argument("--burn-rate-threshold", type=str, default="",
                   help="burn rate 임계 (빈 문자열 = 미정의 → safety_1=false)")
    p.add_argument("--window", type=str, default="3600",
                   help="측정 window (초, default 3600=1h)")
    p.add_argument("--kill-switch-flag", type=str, default="",
                   help="filesystem kill-switch flag 경로 (존재 시 kill-switch 활성)")
    p.add_argument("--config-disabled", type=str, default="false",
                   help="config 설정 (deploy.auto_rollback.enabled=false 시 'true')")
    return p.parse_args()


def check_safety_1(
    error_rate: float | None,
    error_rate_threshold: float | None,
    burn_rate: float | None,
    burn_rate_threshold: float | None,
) -> tuple[bool, str, float, float]:
    """
    안전장치 1: 숫자 임계 초과 (정량 — 모달 어휘 금지)
    임계 미정의 = false (보수적)
    반환: (safety_1, signal_type, measured, threshold)
    """
    # 에러율 임계 체크
    if error_rate_threshold is not None and error_rate is not None:
        if error_rate >= error_rate_threshold:
            return True, "error_rate", error_rate, error_rate_threshold

    # burn rate 임계 체크 (error budget 소진율/window 산술)
    if burn_rate_threshold is not None and burn_rate is not None:
        if burn_rate >= burn_rate_threshold:
            return True, "burn_rate", burn_rate, burn_rate_threshold

    # 임계 미초과 또는 미정의
    measured_val = error_rate if error_rate is not None else 0.0
    threshold_val = error_rate_threshold if error_rate_threshold is not None else 0.0
    return False, "none", measured_val, threshold_val


def check_safety_4(kill_switch_flag: str, config_disabled: bool) -> tuple[bool, bool]:
    """
    안전장치 4: kill-switch off
    OR disable 보수적 (둘 중 하나라도 disable = kill-switch 활성)
    반환: (safety_4, kill_switch_active)
    """
    import os
    # filesystem flag 체크 (primary, 0 API call — ADR-104 §결정 3)
    flag_active = False
    if kill_switch_flag:
        flag_active = os.path.exists(kill_switch_flag)

    # config flag 체크 (secondary)
    config_active = config_disabled

    # OR disable (보수적 — EC-2 kill-switch 우선)
    kill_switch_active = flag_active or config_active
    safety_4 = not kill_switch_active
    return safety_4, kill_switch_active


def compute_signature(signal_type: str, measured: float, window: int) -> str:
    """
    signature = sha256("<signal_type>|<measured>|<window>") | head -c 16
    (check-channel-drift.sh §3 답습 — TC-9)
    """
    raw = f"{signal_type}|{measured}|{window}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return digest[:16]


def safe_float(val: str) -> float | None:
    """문자열 → float, 빈 문자열/변환 불가 = None (미정의)"""
    if not val.strip():
        return None
    try:
        return float(val)
    except ValueError:
        return None


def safe_int(val: str) -> int:
    """문자열 → int, 변환 불가 = default 3600"""
    try:
        return int(val)
    except ValueError:
        return 3600


def main() -> int:
    args = parse_args()

    # 인수 파싱
    error_rate = safe_float(args.error_rate)
    error_rate_threshold = safe_float(args.error_rate_threshold)
    burn_rate = safe_float(args.burn_rate)
    burn_rate_threshold = safe_float(args.burn_rate_threshold)
    window = safe_int(args.window)
    config_disabled = args.config_disabled.lower() in ("true", "1", "yes")

    # 안전장치 4 (kill-switch) — 가장 먼저 평가 (§3.3 kill-switch 우선)
    safety_4, kill_switch_active = check_safety_4(
        args.kill_switch_flag, config_disabled
    )

    # 안전장치 1 (숫자 임계)
    safety_1, signal_type, measured, threshold = check_safety_1(
        error_rate, error_rate_threshold, burn_rate, burn_rate_threshold
    )

    # 안전장치 3 = monitor 활성 = 항상 true (§3.3)
    safety_3 = True

    # 안전장치 2 (보존 기간) = 기존 hook 위임 (본 스크립트 미평가 — shell 이 hook 결과 수신)
    # 본 스크립트 출력: safety_2 는 포함하지 않음 (hook 위임 명시)

    # signature 계산
    sig_measured = measured if signal_type != "none" else 0.0
    signature = compute_signature(signal_type, sig_measured, window)

    # 신호 감지 여부 (safety_1 기준 — safety_2 는 hook 위임)
    signal_detected = safety_1

    # 출력 (bash orchestration 파싱용)
    print(f"signal_detected={str(signal_detected).lower()}")
    print(f"signal_type={signal_type}")
    print(f"measured={measured:.6f}")
    print(f"threshold={threshold:.6f}")
    print(f"window={window}")
    print(f"safety_1={str(safety_1).lower()}")
    print(f"safety_3={str(safety_3).lower()}")
    print(f"safety_4={str(safety_4).lower()}")
    print(f"kill_switch_active={str(kill_switch_active).lower()}")
    print(f"signature={signature}")

    # §3.7 exit 0 (SETUP error = caller bash 가 exit 2 처리)
    return 0


if __name__ == "__main__":
    sys.exit(main())
