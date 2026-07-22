#!/usr/bin/env python3
"""
scripts/check_operational_regression.py
CFP-1194 — regression/smoke·health monitor: baseline 대비 metric % 비교 + health 이진 FAIL 감지
              + flap 흡수 3-layer (N-tick for-clause + hysteresis recovery margin + signature dedup)

ADR-061 (multi-line Python > 5줄 → 외부 .py 의무):
  regression %악화 비교 = float division + 부호 의존 비교 → multi-line
  flap N-tick for-clause = cross-tick state file I/O + 카운터 → multi-line

§3.2 책임 분리 (Change Plan SSOT):
  thin bash (check-operational-regression.sh) — orchestration / wrapper fast-pass / dedup / Issue 발의
  본 Python — regression % 비교 산술 + health 이진 FAIL + flap for-clause + hysteresis + signature

§3.3 health 0 API call 경계 (D3):
  primary: 로컬 filesystem metric 파일 파싱 (.codeforge/health-status.json)
  secondary: Actions-internal probe (overlay exception declare 시에만 — 본 스크립트는 결과 파싱만)
  anti-pattern: webhook push / 외부 metric API → 금지 (measurement-channel.md)

§3.4 flap 흡수 3-layer (D4):
  (a) N-tick for-clause: cross-tick state file (.codeforge/operational-flap-state.json) 누적
  (b) hysteresis recovery margin: regression recovery threshold 미만까지 미해소
  (c) signature dedup: 동일 signature open Issue → bash 조율 (본 스크립트 = flap_suppressed 출력)

§7.4 empirical-source:
  24h cron rate: CFP-1193 S4 monitor 패턴 답습 (dimension: rate)
  flap N-tick (dimension: count): Grafana/Prometheus 'for' clause 산업 표준; 구체 N = consumer overlay
  hysteresis margin (dimension: rate): Datadog hysteresis; 구체 margin = consumer overlay
  regression 임계 구체값: consumer SLO (overlay) — 본 스크립트 = 형식+비교 로직만

출력 포맷 (stdout — bash orchestration 이 파싱):
  signal_detected=<true|false>
  signal_type=<regression|smoke_health|none>
  measured=<float>
  baseline=<float>
  threshold=<float>
  window=<int>
  flap_suppressed=<true|false>
  signature=<16-char hex>

exit codes (ADR-060 §결정 15 3-tier):
  0 = 정상 (임계 미초과 / 신호 감지 완료 / flap 억제 / baseline bootstrap)
  1 = reserved (current scope 미사용)
  2 = SETUP error (의존성 부재 / metric source 불가 / yaml parse error / 인수 오류)

Mock seam (bats TDD):
  _CFP1194_MOCK_BASELINE_FILE=<path>       — baseline JSON 파일 경로 override
  _CFP1194_MOCK_CURRENT_METRIC_FILE=<path> — 현재 metric JSON 파일 경로 override
  _CFP1194_MOCK_HEALTH_FILE=<path>         — health-status JSON 파일 경로 override
  _CFP1194_MOCK_FLAP_STATE_FILE=<path>     — flap state JSON 파일 경로 override
  _CFP1194_MOCK_METRIC_UNAVAILABLE=1       — metric source 불가 시뮬레이션 (EC-2, exit 2)
  _CFP1194_MOCK_FLAP_N=<int>              — N-tick 임계 override (default: 2)
  _CFP1194_MOCK_RECOVERY_MARGIN=<float>   — hysteresis recovery margin override (default: 0.5)
"""

import argparse
import hashlib
import json
import os
import sys
from typing import Optional, Tuple


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="CFP-1194 regression/smoke·health monitor — metric 비교 + flap 흡수 + signature"
    )
    p.add_argument("--signal-type", type=str, default="auto",
                   choices=["auto", "regression", "smoke_health"],
                   help="신호 유형 (auto = 양자 모두 평가, regression = 배포 전후 비교, smoke_health = 이진 FAIL)")
    p.add_argument("--metric-name", type=str, default="error_rate",
                   help="regression 측정 metric 이름 (예: error_rate, latency_p99, throughput, accuracy)")
    p.add_argument("--regression-threshold", type=str, default="",
                   help="regression 임계 (악화 pct, 예: 10.0 = 10pct 이상 악화 시 신호). 빈 문자열 = 미정의 → 신호 0 (보수적)")
    p.add_argument("--flap-n", type=str, default="2",
                   help="N-tick for-clause (default: 2 -- 연속 2 tick FAIL 시 신호)")
    p.add_argument("--recovery-margin", type=str, default="0.5",
                   help="hysteresis recovery margin (default: 0.5 -- regression 이 임계 - margin pct 미만까지 복귀해야 해소)")
    p.add_argument("--window", type=str, default="86400",
                   help="측정 window (초, default 86400=24h cron 주기)")
    p.add_argument("--baseline-file", type=str, default="",
                   help="baseline JSON 파일 경로 (.codeforge/operational-baseline.json). 부재 시 bootstrap (EC-1)")
    p.add_argument("--current-metric-file", type=str, default="",
                   help="현재 metric JSON 파일 경로 (.codeforge/current-metric.json). 부재 시 exit 2 (EC-2)")
    p.add_argument("--health-file", type=str, default="",
                   help="health-status JSON 파일 경로 (.codeforge/health-status.json). smoke_health 신호 전용")
    p.add_argument("--flap-state-file", type=str, default="",
                   help="flap state JSON 파일 경로 (.codeforge/operational-flap-state.json). cross-tick 카운터")
    return p.parse_args()


def make_signature(signal_type: str, measured: float, window: int) -> str:
    """
    sha256("<signal_type>|<measured>|<window>")[:16]
    S4 signal signature sha256 공식 verbatim (ADR-106 / Change Plan §3.5 SSOT — S4 producer 는 CFP-2782 로 제거)
    """
    raw = f"{signal_type}|{measured}|{window}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_json_file(path: str, description: str) -> Optional[dict]:
    """
    JSON 파일 로드. 부재 시 None 반환 (SETUP error 판단은 caller).
    yaml.safe_load 불필요 (JSON 전용 — ADR-070 grep 금지 원칙 동형 적용).
    """
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"[ERROR] {description} 파일 형식 오류: dict 아님 ({path})", file=sys.stderr)
            sys.exit(2)
        return data
    except json.JSONDecodeError as e:
        print(f"[ERROR] {description} JSON parse 실패: {e} ({path})", file=sys.stderr)
        sys.exit(2)


def write_json_file(path: str, data: dict) -> None:
    """JSON 파일 write (baseline bootstrap / flap state 갱신)."""
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[WARN] JSON write 실패: {e} ({path})", file=sys.stderr)


def evaluate_regression(
    baseline_file: str,
    current_metric_file: str,
    metric_name: str,
    regression_threshold_str: str,
    recovery_margin_str: str,
    flap_n: int,
    flap_state_file: str,
) -> Tuple[bool, float, float, float, bool]:
    """
    regression 신호 평가 (배포 전후 metric 비교).

    반환: (signal_detected, measured_pct, baseline_val, threshold, flap_suppressed)
    """
    # regression 임계 미정의 = 신호 미감지 (보수적, Change Plan §3.2 D-4 invariant)
    if not regression_threshold_str.strip():
        print("[INFO] regression 임계 미정의 — 신호 미감지 (보수적, I-3 unconditional guard)")
        return False, 0.0, 0.0, 0.0, False

    try:
        threshold = float(regression_threshold_str)
    except ValueError:
        print(f"[ERROR] regression-threshold 파싱 실패: '{regression_threshold_str}'", file=sys.stderr)
        sys.exit(2)

    try:
        recovery_margin = float(recovery_margin_str)
    except ValueError:
        recovery_margin = 0.5

    # mock seam: _CFP1194_MOCK_METRIC_UNAVAILABLE=1 → exit 2
    if os.environ.get("_CFP1194_MOCK_METRIC_UNAVAILABLE", "0") == "1":
        print("[ERROR] metric source 불가 (_CFP1194_MOCK_METRIC_UNAVAILABLE=1) — exit 2 (EC-2)", file=sys.stderr)
        sys.exit(2)

    # mock seam: baseline / current metric file 경로 override
    baseline_path = os.environ.get("_CFP1194_MOCK_BASELINE_FILE", baseline_file)
    current_path = os.environ.get("_CFP1194_MOCK_CURRENT_METRIC_FILE", current_metric_file)

    # 현재 metric 로드 (부재 = EC-2 SETUP error)
    if not current_path or not os.path.exists(current_path):
        print(f"[ERROR] 현재 metric 파일 부재 — EC-2 SETUP error (path: {current_path})", file=sys.stderr)
        sys.exit(2)
    current_data = load_json_file(current_path, "현재 metric")
    if current_data is None:
        print(f"[ERROR] 현재 metric 파일 부재 — EC-2 SETUP error (path: {current_path})", file=sys.stderr)
        sys.exit(2)

    current_val = current_data.get(metric_name)
    if current_val is None:
        print(f"[ERROR] metric '{metric_name}' 현재 파일 부재 — EC-2", file=sys.stderr)
        sys.exit(2)
    try:
        current_val = float(current_val)
    except (TypeError, ValueError):
        print(f"[ERROR] metric '{metric_name}' 값 float 변환 실패: {current_val}", file=sys.stderr)
        sys.exit(2)

    # baseline 로드 (부재 = EC-1 bootstrap)
    baseline_data = load_json_file(baseline_path, "baseline") if baseline_path else None
    if baseline_data is None:
        # EC-1: 첫 배포 — 현재값을 baseline으로 기록 후 신호 미감지
        print(f"[INFO] baseline 부재 (EC-1) — 현재 metric 을 baseline 으로 기록: {metric_name}={current_val}")
        bootstrap_data = {metric_name: current_val, "_bootstrapped": True}
        if baseline_path:
            write_json_file(baseline_path, bootstrap_data)
        # 출력
        print("signal_detected=false")
        print("signal_type=none")
        print(f"measured=0.0")
        print(f"baseline={current_val}")
        print(f"threshold={threshold}")
        print(f"window=86400")
        print("flap_suppressed=false")
        print(f"signature={make_signature('none', 0.0, 86400)}")
        sys.exit(0)

    baseline_val = baseline_data.get(metric_name)
    if baseline_val is None:
        print(f"[ERROR] metric '{metric_name}' baseline 파일 부재 — EC-2", file=sys.stderr)
        sys.exit(2)
    try:
        baseline_val = float(baseline_val)
    except (TypeError, ValueError):
        print(f"[ERROR] metric '{metric_name}' baseline 값 float 변환 실패: {baseline_val}", file=sys.stderr)
        sys.exit(2)

    # regression % 악화 계산
    # 부호 처리: error_rate/latency = 높을수록 악화 (+%). throughput/accuracy = 낮을수록 악화 (-%).
    # metric_name prefix 기반 부호 판정 (보수적 — 높을수록 악화 default)
    inverted_metrics = {"throughput", "accuracy", "success_rate"}
    metric_key = metric_name.split(".")[-1].lower()

    if baseline_val == 0.0:
        # baseline=0 → division by zero 회피: current>0 = infinite regression (임계 초과)
        if current_val > 0:
            pct_change = float("inf")
        else:
            pct_change = 0.0
    elif metric_key in inverted_metrics:
        # 낮을수록 악화: (baseline - current) / baseline * 100
        pct_change = (baseline_val - current_val) / abs(baseline_val) * 100.0
    else:
        # 높을수록 악화: (current - baseline) / baseline * 100
        pct_change = (current_val - baseline_val) / abs(baseline_val) * 100.0

    print(f"[INFO] regression %변화: {metric_name} = {pct_change:.2f}% (current={current_val}, baseline={baseline_val})")

    # 임계 비교
    signal_raw = pct_change >= threshold

    if not signal_raw:
        # 정상 범위 — flap state 리셋 (hysteresis: FAIL→OK 복귀 시 recovery margin 확인)
        flap_state = load_json_file(
            os.environ.get("_CFP1194_MOCK_FLAP_STATE_FILE", flap_state_file),
            "flap state"
        ) or {}
        key = f"regression_{metric_name}"
        if key in flap_state:
            # hysteresis: recovery_margin 이하까지 복귀해야 해소
            resolve_threshold = threshold - recovery_margin
            if pct_change < resolve_threshold:
                # 완전 복귀 — 카운터 리셋
                flap_state.pop(key, None)
                _write_flap_state(
                    os.environ.get("_CFP1194_MOCK_FLAP_STATE_FILE", flap_state_file),
                    flap_state
                )
                print(f"[INFO] hysteresis: regression 완전 복귀 ({pct_change:.2f}% < resolve={resolve_threshold:.2f}%) — flap 리셋")
            else:
                # hysteresis 미해소: threshold 미만이나 resolve_threshold 이상 → 신호 유지
                print(f"[INFO] hysteresis: resolve_threshold({resolve_threshold:.2f}%) 미도달 — 신호 유지")
                return True, pct_change, baseline_val, threshold, False
        return False, pct_change, baseline_val, threshold, False

    # 임계 초과 — flap N-tick for-clause 평가
    flap_state_path = os.environ.get("_CFP1194_MOCK_FLAP_STATE_FILE", flap_state_file)
    flap_state = load_json_file(flap_state_path, "flap state") or {}
    key = f"regression_{metric_name}"
    count = flap_state.get(key, 0) + 1
    flap_state[key] = count
    _write_flap_state(flap_state_path, flap_state)

    if count < flap_n:
        print(f"[INFO] flap N-tick (a): regression tick={count}/{flap_n} 미달 — 억제")
        return signal_raw, pct_change, baseline_val, threshold, True  # flap_suppressed=True

    print(f"[INFO] flap N-tick (a): regression tick={count}/{flap_n} 도달 — 신호 발의")
    return True, pct_change, baseline_val, threshold, False


def evaluate_health(
    health_file: str,
    flap_n: int,
    flap_state_file: str,
) -> Tuple[bool, float, float, float, bool]:
    """
    smoke·health 이진 FAIL 감지 + flap N-tick for-clause.

    반환: (signal_detected, measured(1.0=FAIL/0.0=OK), baseline(0.0=OK expected), threshold(1.0), flap_suppressed)
    """
    # mock seam: _CFP1194_MOCK_METRIC_UNAVAILABLE=1 → exit 2
    if os.environ.get("_CFP1194_MOCK_METRIC_UNAVAILABLE", "0") == "1":
        print("[ERROR] metric source 불가 (_CFP1194_MOCK_METRIC_UNAVAILABLE=1) — exit 2 (EC-2)", file=sys.stderr)
        sys.exit(2)

    health_path = os.environ.get("_CFP1194_MOCK_HEALTH_FILE", health_file)

    if not health_path or not os.path.exists(health_path):
        print(f"[INFO] health-status 파일 부재 — 신호 미감지 (D3: filesystem primary, probe declare 필요)")
        return False, 0.0, 0.0, 1.0, False

    health_data = load_json_file(health_path, "health-status")
    if health_data is None:
        return False, 0.0, 0.0, 1.0, False

    # health-status.json 형식: {"status": "ok"/"fail"/"degraded", ...}
    status = str(health_data.get("status", "ok")).lower()
    is_fail = status in {"fail", "failed", "unhealthy", "degraded", "error"}
    measured = 1.0 if is_fail else 0.0

    print(f"[INFO] health 상태: status={status} is_fail={is_fail}")

    if not is_fail:
        # 정상 — flap 카운터 리셋
        flap_state_path = os.environ.get("_CFP1194_MOCK_FLAP_STATE_FILE", flap_state_file)
        flap_state = load_json_file(flap_state_path, "flap state") or {}
        if "health" in flap_state:
            flap_state.pop("health", None)
            _write_flap_state(flap_state_path, flap_state)
            print("[INFO] health 정상 — flap 카운터 리셋")
        return False, measured, 0.0, 1.0, False

    # FAIL — flap N-tick for-clause 평가
    flap_state_path = os.environ.get("_CFP1194_MOCK_FLAP_STATE_FILE", flap_state_file)
    flap_state = load_json_file(flap_state_path, "flap state") or {}
    count = flap_state.get("health", 0) + 1
    flap_state["health"] = count
    _write_flap_state(flap_state_path, flap_state)

    if count < flap_n:
        print(f"[INFO] flap N-tick (a): health FAIL tick={count}/{flap_n} 미달 — 억제")
        return True, measured, 0.0, 1.0, True  # flap_suppressed=True

    print(f"[INFO] flap N-tick (a): health FAIL tick={count}/{flap_n} 도달 — 신호 발의")
    return True, measured, 0.0, 1.0, False


def _write_flap_state(path: str, state: dict) -> None:
    """flap state JSON file write."""
    if path:
        write_json_file(path, state)


def main() -> None:
    args = parse_args()

    try:
        flap_n = int(os.environ.get("_CFP1194_MOCK_FLAP_N", args.flap_n))
    except ValueError:
        flap_n = 2

    try:
        window = int(args.window)
    except ValueError:
        window = 86400

    recovery_margin_str = os.environ.get("_CFP1194_MOCK_RECOVERY_MARGIN", args.recovery_margin)

    # 기본 파일 경로 (worktree root 기준 — bash 가 절대 경로 주입)
    baseline_file = args.baseline_file
    current_metric_file = args.current_metric_file
    health_file = args.health_file
    flap_state_file = args.flap_state_file

    signal_detected = False
    signal_type = "none"
    measured = 0.0
    baseline_val = 0.0
    threshold = 0.0
    flap_suppressed = False

    if args.signal_type in ("auto", "regression"):
        sig, meas, base, thr, flap_sup = evaluate_regression(
            baseline_file=baseline_file,
            current_metric_file=current_metric_file,
            metric_name=args.metric_name,
            regression_threshold_str=args.regression_threshold,
            recovery_margin_str=recovery_margin_str,
            flap_n=flap_n,
            flap_state_file=flap_state_file,
        )
        if sig:
            signal_detected = True
            signal_type = "regression"
            measured = meas
            baseline_val = base
            threshold = thr
            flap_suppressed = flap_sup

    if args.signal_type in ("auto", "smoke_health") and not signal_detected:
        sig_h, meas_h, base_h, thr_h, flap_sup_h = evaluate_health(
            health_file=health_file,
            flap_n=flap_n,
            flap_state_file=flap_state_file,
        )
        if sig_h:
            signal_detected = True
            signal_type = "smoke_health"
            measured = meas_h
            baseline_val = base_h
            threshold = thr_h
            flap_suppressed = flap_sup_h

    # flap_suppressed=True 시 신호 억제 (bash 조율용 출력 유지)
    if flap_suppressed:
        signal_detected = False

    # signature 계산 (S4 공식 verbatim)
    sig_hex = make_signature(signal_type, measured, window)

    # stdout 출력 (bash orchestration 이 파싱)
    print(f"signal_detected={'true' if signal_detected else 'false'}")
    print(f"signal_type={signal_type}")
    print(f"measured={measured}")
    print(f"baseline={baseline_val}")
    print(f"threshold={threshold}")
    print(f"window={window}")
    print(f"flap_suppressed={'true' if flap_suppressed else 'false'}")
    print(f"signature={sig_hex}")

    sys.exit(0)


if __name__ == "__main__":
    main()
