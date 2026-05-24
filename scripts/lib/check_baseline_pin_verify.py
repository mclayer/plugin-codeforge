"""
scripts/lib/check_baseline_pin_verify.py
CFP-1410 Phase 2 / ADR-073 Amendment 9 — baseline_pin field presence + freshness check SSOT

기능:
  spawn prompt 파일 또는 Story file 을 입력으로 받아
  baseline_pin_verified_at + baseline_pin_sha 필드 존재 + freshness (30분 이내) 검사.
  필드 부재 또는 stale(≥30분) 시 warning exit 1 (non-blocking 권고).
  bypass: BYPASS_BASELINE_PIN_VERIFY=1

Exit-code:
  0: PASS (필드 존재 + freshness OK)
  1: WARNING (필드 부재 또는 stale — advisory, non-blocking 의도)
  2: SETUP error (파일 없음 또는 인수 부재)

환경 변수:
  BYPASS_BASELINE_PIN_VERIFY     — bypass flag
  BASELINE_PIN_STALE_MINUTES     — stale 판정 임계값 분 (default: 30)

Test seam:
  BASELINE_PIN_MOCK_NOW_EPOCH=<Unix timestamp> — 현재 시각 mock
"""

import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import Optional

# Windows cp949 stdout encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_baseline_pin_verify"
BYPASS_ENV = "BYPASS_BASELINE_PIN_VERIFY"
DEFAULT_STALE_MINUTES = 30

MOCK_NOW_ENV = "BASELINE_PIN_MOCK_NOW_EPOCH"

# 필드 패턴 (YAML frontmatter 또는 prose 블록 내)
RE_VERIFIED_AT = re.compile(
    r"baseline_pin_verified_at\s*:\s*(\S+)"
)
RE_PIN_SHA = re.compile(
    r"baseline_pin_sha\s*:\s*([0-9a-f]{6,40})",
    re.IGNORECASE,
)

# ISO 8601 datetime 파싱용 패턴 (Z 또는 +HH:MM 허용)
RE_ISO8601 = re.compile(
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(Z|[+-]\d{2}:\d{2})"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_stale_minutes() -> int:
    """BASELINE_PIN_STALE_MINUTES 환경 변수 (default 30)."""
    raw = os.environ.get("BASELINE_PIN_STALE_MINUTES", str(DEFAULT_STALE_MINUTES))
    try:
        val = int(raw)
        return val if val >= 1 else DEFAULT_STALE_MINUTES
    except ValueError:
        return DEFAULT_STALE_MINUTES


def _get_now_epoch() -> float:
    """현재 UTC epoch. Test seam: BASELINE_PIN_MOCK_NOW_EPOCH."""
    mock_val = os.environ.get(MOCK_NOW_ENV)
    if mock_val is not None:
        try:
            return float(mock_val)
        except ValueError:
            pass
    return time.time()


def _parse_iso8601(ts_str: str) -> Optional[float]:
    """ISO 8601 문자열을 UTC epoch float으로 변환. 파싱 실패 시 None."""
    m = RE_ISO8601.match(ts_str.strip())
    if not m:
        return None
    dt_part, tz_part = m.group(1), m.group(2)
    try:
        if tz_part == "Z":
            tz_offset_sec = 0
        else:
            sign = 1 if tz_part[0] == "+" else -1
            hh, mm = int(tz_part[1:3]), int(tz_part[4:6])
            tz_offset_sec = sign * (hh * 3600 + mm * 60)
        naive_dt = datetime.strptime(dt_part, "%Y-%m-%dT%H:%M:%S")
        utc_epoch = naive_dt.replace(tzinfo=timezone.utc).timestamp() - tz_offset_sec
        return utc_epoch
    except (ValueError, OverflowError):
        return None


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Bypass check
    if os.environ.get(BYPASS_ENV) == "1":
        audit_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(
            f"[{SCRIPT_NAME}] {BYPASS_ENV}=1 — baseline pin verify skipped at {audit_ts}",
            file=sys.stderr,
        )
        sys.exit(0)

    # 2. 인수 확인
    if len(sys.argv) < 2:
        print(
            f"[{SCRIPT_NAME}] WARNING: no file path provided — skipping baseline pin check",
            file=sys.stderr,
        )
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(
            f"[{SCRIPT_NAME}] SETUP ERROR: file not found: {file_path}",
            file=sys.stderr,
        )
        sys.exit(2)

    # 3. 파일 읽기
    try:
        content = open(file_path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        print(f"[{SCRIPT_NAME}] SETUP ERROR: cannot read file: {exc}", file=sys.stderr)
        sys.exit(2)

    # 4. 필드 존재 검사
    sha_match = RE_PIN_SHA.search(content)
    ts_match = RE_VERIFIED_AT.search(content)

    if not sha_match or not ts_match:
        missing = []
        if not sha_match:
            missing.append("baseline_pin_sha")
        if not ts_match:
            missing.append("baseline_pin_verified_at")
        print(
            f"[{SCRIPT_NAME}] WARNING: missing field(s) in {file_path}: {', '.join(missing)}"
        )
        print(
            f"[{SCRIPT_NAME}] Add baseline_pin_sha and baseline_pin_verified_at fields "
            f"to confirm origin/main was verified before lane spawn (ADR-073 Amendment 9)."
        )
        sys.exit(1)

    # 5. freshness 검사
    stale_minutes = _get_stale_minutes()
    ts_str = ts_match.group(1)
    pin_epoch = _parse_iso8601(ts_str)

    if pin_epoch is None:
        print(
            f"[{SCRIPT_NAME}] WARNING: cannot parse baseline_pin_verified_at timestamp: {ts_str!r}"
        )
        sys.exit(1)

    now_epoch = _get_now_epoch()
    age_minutes = (now_epoch - pin_epoch) / 60.0

    if age_minutes >= stale_minutes:
        print(
            f"[{SCRIPT_NAME}] WARNING: baseline_pin_verified_at is {age_minutes:.1f} minutes old "
            f"(threshold={stale_minutes}min) — re-verify origin/main before lane spawn."
        )
        print(
            f"[{SCRIPT_NAME}] Run: git fetch origin && git show origin/main --format='%H %s' -s"
        )
        sys.exit(1)

    # 6. PASS
    sys.exit(0)


if __name__ == "__main__":
    main()
