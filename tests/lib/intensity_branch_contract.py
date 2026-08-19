#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/lib/intensity_branch_contract.py — intensity 분기 계약 **단일 SUT**.

CFP-2967 Phase 2 / Change Plan §5 #6 · §3.2 · §3.3 · §8.2.

★ 이 파일은 `tests/` 아래 있지만 **테스트가 아니라 SUT(피시험 대상) 모듈**이다.
  `skills/rate-limit-429-mitigation/SKILL.md` 의 Decision tree 가 지시하는 판정 계약을
  **실행 가능한 형태로 단일 추출**한 것이다 (현재 그 구현이 repo 에 부재하며 문서 안
  의사코드로만 존재한다 — 계약이 여러 테스트 파일에 각자 복사되면 갈라진다).
  명명 테스트(AC-9 등)는 **이 모듈을 import 해서** 친다.

────────────────────────────────────────────────────────────────────────────────
판정 4축 + 분기 순서 (§3.3) — **순서가 결과를 바꾸므로 순서까지 계약의 일부다**

    absent  →  stale  →  count

  | bucket                      | 조건                                              |
  |-----------------------------|---------------------------------------------------|
  | `unknown_absent_datasource` | 파일없음 ∨ 빈파일 ∨ DATA행 0 ∨ 전 행 파싱 실패     |
  | `unknown_stale_datasource`  | `¬(A ∧ B)` ∨ `malformed > 0`                      |
  | low / medium / high         | window 내 사건 수 0 / 1 / ≥2                      |

  ★ 값 3-tuple(cap/stagger/mode)의 **정본은 SKILL.md intensity 트리 단독**이며 이 모듈은
    값을 리터럴로 재기재하지 않는다 — `load_bucket_values()` 가 그 정본을 파싱해 돌려준다.
    (CFP-2914(PR #2956)가 같은 값을 바꾸는 중이라 갈라짐은 가설이 아니라 진행 중인 사실.)
  ★ stale 의 값 3-tuple 은 absent 와 **같지만 bucket 이름은 분리**한다. 이름까지 같으면
    "부재 축 제거 mutant" 와 "신선도 축 제거 mutant" 가 같은 산출을 내어 판별력이 죽는다.

────────────────────────────────────────────────────────────────────────────────
신선도 = `A ∧ B` 2-conjunct (§3.2)

  A — 설치 attestation : `hooks/hooks.json` 에 `StopFailure` → producer 등록 **실재**
                         (= 채널이 배선돼 있다)
  B — dispatch liveness: `.claude/ledger/stop-event.jsonl` 의 `max(timestamp_kst)` 가
                         `T_h` 이내 (= turn-end hook 계열이 지금 발화 중)

  B 단독 = born-hollow (429 producer 가 없는 오늘도 fresh) / A 단독 = 회귀 검출 불가.
  `T_h` = **소비자 window 와 동일 값 재사용**(`WINDOW_SECONDS`) — 신규 상수 도입 0.
  ★ 생존 신호를 event log 안에 두지 않는다 — heartbeat 행을 event log 에 쓰면 DATA 행이
    영구히 ≥1 이 되어 부재 가드가 다시는 발화하지 못한다. A·B 모두 **신규 writer 0 ·
    신규 파일 0** 이며 이 모듈은 어떤 파일도 **쓰지 않는다**(읽기 전용).

────────────────────────────────────────────────────────────────────────────────
경계 조건 (§8.2)

  B-1 window = 반열림 `(now − WINDOW_SECONDS, now]`. 정확히 경계값은 **제외**.
  B-2 timestamp = offset-aware 절대 순간 비교. **naive = 파싱 실패**(임의 tz 승격 금지).
  B-3 파싱 실패 행 = skip + 계수(`unparseable_timestamp_count`). 침묵 drop 금지.
  B-4 전 행 파싱 실패 = DATA 행 0 과 동치 ⇒ 부재.
  B-5 미래 timestamp = window 제외 + `clock_anomaly_count` 계수. (포함이 fail-safe 로
      보이나 손상된 far-future 행 1건이 intensity 를 영구 High 로 고정해 가용성을 파괴)
  B-6 정렬 가정 **금지** — tail-N·"마지막 행" 단축 없음. 전 행을 훑는다.
  B-7 주석-only 파일 = 부재의 4번째 형태 — DATA 행 0 으로 정규화.
  B-8 완전중복 행 = v1 은 별 사건으로 계수(편향 = 과다 = fail-safe). **"exact-count"
      주장 금지** — `IntensityDecision.exact_count_claim` 이 상시 False 로 이를 못박는다.

주입(injection): A·B·데이터원을 전부 **인자로 주입 가능**하다. 기본값은 실 경로이며,
fixture 는 경로를 갈아끼우거나(`FreshnessAttestation` 직접 주입) 임의 상태를 먹일 수 있다.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# tests/lib/ → tests/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SKILL_PATH = REPO_ROOT / "skills" / "rate-limit-429-mitigation" / "SKILL.md"
DEFAULT_EVENT_LOG_PATH = REPO_ROOT / "docs" / "kpi" / "429-incident-history.jsonl"
DEFAULT_HOOKS_JSON_PATH = REPO_ROOT / "hooks" / "hooks.json"
DEFAULT_STOP_EVENT_LEDGER = REPO_ROOT / ".claude" / "ledger" / "stop-event.jsonl"

# 소비자 window = 직전 30분. T_h(신선도 임계)는 **이 값을 재사용**한다 (§3.2 — 신규 상수 0).
WINDOW_SECONDS = 1800

# conjunct A 가 지목하는 site (hooks/hooks.json 안 이벤트 키 + producer 실체 토큰)
STOPFAILURE_EVENT_KEY = "StopFailure"
PRODUCER_HOOK_TOKEN = "stopfailure-429-incident-record"

# conjunct B 데이터원의 timestamp 필드명
#   실측 근거: scripts/lib/aggregate_stop_event.py 가 `row.get("timestamp_kst")` 로 읽는다.
STOP_EVENT_TIMESTAMP_FIELD = "timestamp_kst"

# bucket 이름 (값이 아니라 **이름** — 값 정본은 SKILL.md)
BUCKET_ABSENT = "unknown_absent_datasource"
BUCKET_STALE = "unknown_stale_datasource"
BUCKET_LOW = "low"
BUCKET_MEDIUM = "medium"
BUCKET_HIGH = "high"

VALUE_KEYS = ("parallel_spawn_cap", "spawn_stagger_ms", "fallback_mode")


class IntensityContractError(RuntimeError):
    """계약 정본을 판독할 수 없을 때 (fail-closed — 조용한 기본값으로 낙하하지 않는다)."""


# ══════════════════════════════════════════════════════════════════════════════
# 공통 — 엄격 timestamp 파서
# ══════════════════════════════════════════════════════════════════════════════

def parse_aware_timestamp(value):
    """ISO 8601 **offset-aware** 파싱. naive·비문자열·파싱 실패 = None (B-2).

    ★ 재사용 탐색 결과 (ADR-140): `scripts/lib/aggregate_stop_event.py::_parse_iso_aware`
      와 `scripts/lib/append_dev_process_event.py` 에 유사 헬퍼가 있으나 둘 다 **naive 를
      KST/UTC 로 승격**한다. B-2 는 정확히 그 승격을 금지하므로(승격하면 계약 위반 행이
      유효 행으로 둔갑) 의미론이 반대다 — 재사용하면 경계 조건이 깨진다. 그래서 이름을
      공개(`parse_aware_timestamp`)해 두고 **이 모듈이 단일 정의처**가 되게 한다.
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt


def _read_text(path):
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


# ══════════════════════════════════════════════════════════════════════════════
# 신선도 — A ∧ B
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FreshnessAttestation:
    """`A ∧ B`. 두 conjunct 를 **따로 보존**한다 — 합만 남기면 어느 축이 죽었는지 못 본다."""

    installed: bool          # A — producer 가 hooks.json 에 등록돼 있는가
    live: bool               # B — turn-end hook 계열이 T_h 이내에 발화했는가
    detail: dict = field(default_factory=dict)

    @property
    def fresh(self) -> bool:
        return bool(self.installed and self.live)


def attest_producer_installed(
    hooks_json_path=DEFAULT_HOOKS_JSON_PATH,
    *,
    event_key: str = STOPFAILURE_EVENT_KEY,
    producer_token: str = PRODUCER_HOOK_TOKEN,
):
    """conjunct A — `hooks.json` 에 `StopFailure` → producer 등록이 **실재**하는가.

    판정: 이벤트 키가 있고 그 아래 등록된 command 중 **producer 실체를 지목**하는 것이
    하나 이상. `true` 같은 no-op 치환은 토큰을 잃으므로 False 가 된다.
    판독 실패(파일 부재·JSON 오류·형태 이탈) = **False**(fail-closed) — 판독 못 했다는
    사실이 "배선돼 있다" 로 승격되지 않는다.

    Returns: (installed: bool, detail: dict)
    """
    detail = {"path": str(hooks_json_path), "event_key": event_key, "reason": None}
    text = _read_text(hooks_json_path)
    if text is None:
        detail["reason"] = "hooks.json 판독 불가(부재 또는 읽기 실패)"
        return False, detail
    try:
        doc = json.loads(text)
    except ValueError as exc:
        detail["reason"] = f"hooks.json JSON 파싱 실패: {exc}"
        return False, detail
    if not isinstance(doc, dict):
        detail["reason"] = "hooks.json 최상위가 object 가 아니다"
        return False, detail

    events = doc.get("hooks") if isinstance(doc.get("hooks"), dict) else doc
    entries = events.get(event_key) if isinstance(events, dict) else None
    if not isinstance(entries, list) or not entries:
        detail["reason"] = f"{event_key} 이벤트 키 부재"
        return False, detail

    commands = []
    for group in entries:
        if not isinstance(group, dict):
            continue
        for hook in group.get("hooks", []) or []:
            if isinstance(hook, dict) and isinstance(hook.get("command"), str):
                commands.append(hook["command"])
    detail["commands"] = commands
    if not commands:
        detail["reason"] = f"{event_key} 아래 command 0건"
        return False, detail
    if not any(producer_token in cmd for cmd in commands):
        detail["reason"] = f"등록된 command 가 producer({producer_token})를 지목하지 않는다"
        return False, detail
    return True, detail


def attest_dispatch_liveness(
    stop_event_log_path=DEFAULT_STOP_EVENT_LEDGER,
    *,
    now=None,
    horizon_seconds: int = WINDOW_SECONDS,
    timestamp_field: str = STOP_EVENT_TIMESTAMP_FIELD,
    text=None,
):
    """conjunct B — turn-end hook 계열이 `T_h` 이내에 발화했는가.

    · 정렬 가정 없음 — 전 행을 훑어 `max(timestamp)` 를 구한다 (B-6).
    · **미래 행은 생존 신호로 인정하지 않는다** — 손상된 far-future 행 1건이 채널을
      영구히 "살아있음" 으로 위조하는 것을 막는다 (B-5 와 같은 fail-safe 방향).
    · 판독 실패 = False (fail-closed).

    Returns: (live: bool, detail: dict)
    """
    now = now or datetime.now(timezone.utc)
    detail = {"path": str(stop_event_log_path), "horizon_seconds": horizon_seconds,
              "latest": None, "rows_seen": 0, "future_rows": 0, "reason": None}
    body = text if text is not None else _read_text(stop_event_log_path)
    if body is None:
        detail["reason"] = "stop-event 원장 판독 불가(부재 또는 읽기 실패)"
        return False, detail

    latest = None
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        detail["rows_seen"] += 1
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        ts = parse_aware_timestamp(row.get(timestamp_field))
        if ts is None:
            continue
        if ts > now:
            detail["future_rows"] += 1
            continue
        if latest is None or ts > latest:
            latest = ts

    if latest is None:
        detail["reason"] = "유효 timestamp 보유 행 0"
        return False, detail
    detail["latest"] = latest.isoformat()
    live = (now - latest) <= timedelta(seconds=horizon_seconds)
    if not live:
        detail["reason"] = f"최신 발화가 T_h({horizon_seconds}s) 밖"
    return live, detail


def attest_freshness(
    *,
    hooks_json_path=DEFAULT_HOOKS_JSON_PATH,
    stop_event_log_path=DEFAULT_STOP_EVENT_LEDGER,
    now=None,
    horizon_seconds: int = WINDOW_SECONDS,
    stop_event_text=None,
) -> FreshnessAttestation:
    """`A ∧ B` 를 실 데이터원에서 산출. 두 conjunct 사유를 detail 에 보존한다."""
    now = now or datetime.now(timezone.utc)
    installed, a_detail = attest_producer_installed(hooks_json_path)
    live, b_detail = attest_dispatch_liveness(
        stop_event_log_path, now=now, horizon_seconds=horizon_seconds, text=stop_event_text
    )
    return FreshnessAttestation(installed=installed, live=live,
                                detail={"A": a_detail, "B": b_detail})


# ══════════════════════════════════════════════════════════════════════════════
# 데이터원 스캔
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EventLogScan:
    present: bool
    data_row_count: int
    in_window_count: int
    out_of_window_count: int
    json_error_count: int
    missing_timestamp_count: int
    unparseable_timestamp_count: int
    clock_anomaly_count: int

    @property
    def malformed_count(self) -> int:
        """행 파싱 실패 총계 (JSON 오류 + timestamp 키 부재 + naive/파싱 실패)."""
        return (self.json_error_count
                + self.missing_timestamp_count
                + self.unparseable_timestamp_count)

    @property
    def valid_row_count(self) -> int:
        return self.data_row_count - self.malformed_count


def scan_event_log(text, *, now, window_seconds: int = WINDOW_SECONDS) -> EventLogScan:
    """event log 본문 → 스캔 결과. **읽기만** 하며 어떤 파일도 쓰지 않는다.

    window = 반열림 `(now − window_seconds, now]` (B-1). 정확히 경계값은 제외.
    """
    if text is None:
        return EventLogScan(False, 0, 0, 0, 0, 0, 0, 0)

    lower = now - timedelta(seconds=window_seconds)
    data_rows = 0
    in_window = out_window = 0
    json_err = missing_ts = bad_ts = anomaly = 0

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):      # B-7 주석 행은 DATA 행이 아니다
            continue
        data_rows += 1
        try:
            row = json.loads(line)
        except ValueError:
            json_err += 1
            continue
        if not isinstance(row, dict) or "timestamp" not in row:
            missing_ts += 1
            continue
        ts = parse_aware_timestamp(row.get("timestamp"))
        if ts is None:                             # B-2 naive 포함 = 파싱 실패
            bad_ts += 1
            continue
        if ts > now:                               # B-5 미래 = 계수 후 window 제외
            anomaly += 1
            out_window += 1
            continue
        if lower < ts <= now:                      # B-1 반열림
            in_window += 1
        else:
            out_window += 1

    return EventLogScan(
        present=True,
        data_row_count=data_rows,
        in_window_count=in_window,
        out_of_window_count=out_window,
        json_error_count=json_err,
        missing_timestamp_count=missing_ts,
        unparseable_timestamp_count=bad_ts,
        clock_anomaly_count=anomaly,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 판정
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IntensityDecision:
    bucket: str
    reported: bool                 # 미판정 bucket 은 **명시 보고 의무** (silent 금지)
    report_message: str
    incident_count: int = None     # 미판정 bucket 에서는 None (0 이 아니다)
    absent_form: str = None
    stale_reason: str = None
    scan: EventLogScan = None
    freshness: FreshnessAttestation = None
    exact_count_claim: bool = False   # B-8 — 완전중복 행을 별 사건으로 세므로 exact 아님

    @property
    def unknown(self) -> bool:
        return self.bucket in (BUCKET_ABSENT, BUCKET_STALE)


def classify(
    *,
    event_log_path=DEFAULT_EVENT_LOG_PATH,
    event_log_text=None,
    freshness: FreshnessAttestation = None,
    hooks_json_path=DEFAULT_HOOKS_JSON_PATH,
    stop_event_log_path=DEFAULT_STOP_EVENT_LEDGER,
    stop_event_text=None,
    now=None,
    window_seconds: int = WINDOW_SECONDS,
) -> IntensityDecision:
    """분기 순서 `absent → stale → count` 를 그대로 실행한다 (§3.3).

    주입:
      · `event_log_text` 를 주면 파일 대신 그 본문을 데이터원으로 쓴다.
      · `freshness` 를 주면 A·B 실측을 건너뛰고 그 attestation 을 쓴다
        (property 테스트가 (T,T)/(T,F)/(F,T)/(F,F) 4조합을 전수로 돌 수 있게 하는 통로).
      · `now` 미지정 시 실제 현재시각. 결정적 테스트는 반드시 고정할 것.
    """
    now = now or datetime.now(timezone.utc)
    text = event_log_text if event_log_text is not None else _read_text(event_log_path)
    scan = scan_event_log(text, now=now, window_seconds=window_seconds)

    # ── 1축: 부재 (4형태) — 신선도보다 **먼저** 본다 ──────────────────────────
    absent_form = None
    if not scan.present:
        absent_form = "missing_file"
    elif text.strip() == "":
        absent_form = "empty_file"
    elif scan.data_row_count == 0:
        absent_form = "no_data_rows"            # 주석-only 포함 (B-7)
    elif scan.valid_row_count == 0:
        absent_form = "all_rows_malformed"      # B-4
    if absent_form:
        return IntensityDecision(
            bucket=BUCKET_ABSENT,
            reported=True,
            report_message=f"429 telemetry 데이터원 부재({absent_form}) — intensity 미판정",
            incident_count=None,
            absent_form=absent_form,
            scan=scan,
            freshness=freshness,
        )

    # ── 2축: 신선도 + malformed ─────────────────────────────────────────────
    if freshness is None:
        freshness = attest_freshness(
            hooks_json_path=hooks_json_path,
            stop_event_log_path=stop_event_log_path,
            now=now,
            horizon_seconds=window_seconds,       # T_h = 소비자 window 재사용
            stop_event_text=stop_event_text,
        )
    stale_reason = None
    if not freshness.fresh:
        stale_reason = (
            "신선도 미충족 — A(설치 attestation)=%s ∧ B(dispatch liveness)=%s"
            % (freshness.installed, freshness.live)
        )
    elif scan.malformed_count > 0:
        stale_reason = f"malformed 행 {scan.malformed_count}건 — 계수 신뢰 불가"
    if stale_reason:
        return IntensityDecision(
            bucket=BUCKET_STALE,
            reported=True,
            report_message=f"429 telemetry 데이터원 신선도 미판정 — {stale_reason}",
            incident_count=None,
            stale_reason=stale_reason,
            scan=scan,
            freshness=freshness,
        )

    # ── 3축: 계수 ────────────────────────────────────────────────────────────
    n = scan.in_window_count
    bucket = BUCKET_LOW if n == 0 else (BUCKET_MEDIUM if n == 1 else BUCKET_HIGH)
    return IntensityDecision(
        bucket=bucket,
        reported=False,
        report_message="",
        incident_count=n,
        scan=scan,
        freshness=freshness,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 값 정본 판독 — SKILL.md intensity 트리 단독 (코드에 값 리터럴 0)
# ══════════════════════════════════════════════════════════════════════════════

_SECTION_RE = re.compile(r"^## Decision tree.*?(?=^## |\Z)", re.M | re.S)
_FENCE_RE = re.compile(r"^```\s*$\n(.*?)^```\s*$", re.M | re.S)
_BRANCH_RE = re.compile(r"^\s*(if|elif|else)\b(.*)$")
_BUCKET_ASSIGN_RE = re.compile(r"^\s*bucket\s*=\s*[\"']([A-Za-z0-9_]+)[\"']")
_VALUE_ASSIGN_RE = re.compile(
    r"^\s*(parallel_spawn_cap|spawn_stagger_ms|fallback_mode)\s*=\s*([^#\n]+?)\s*(?:#.*)?$"
)
# 분기 헤더 주석이 지목하는 기존 bucket (문서가 `bucket = ` 대입을 두지 않는 3분기)
_COMMENT_BUCKET_HINTS = ((r"\bLow\b", BUCKET_LOW),
                         (r"\bMedium\b", BUCKET_MEDIUM),
                         (r"\bHigh\b", BUCKET_HIGH))


def _coerce_value(raw: str):
    token = raw.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    try:
        return int(token)
    except ValueError:
        return token


def load_bucket_values(skill_path=DEFAULT_SKILL_PATH) -> dict:
    """SKILL.md intensity 트리에서 bucket → 값 3-tuple 을 **파싱**한다.

    이 모듈이 값을 리터럴로 들지 않는 이유: 값 정본이 두 곳이 되는 순간 갈라진다
    (§3.3 F-8). 문서가 값을 바꾸면 이 함수의 산출이 따라 바뀌고, 문서에서 bucket 이
    사라지면 **조용한 기본값이 아니라 예외**가 난다(fail-closed).
    """
    text = _read_text(skill_path)
    if text is None:
        raise IntensityContractError(f"값 정본 판독 불가: {skill_path}")
    section = _SECTION_RE.search(text)
    if not section:
        raise IntensityContractError("`## Decision tree` 절 부재 — 값 정본 정의역 소실")
    fence = _FENCE_RE.search(section.group(0))
    if not fence:
        raise IntensityContractError("Decision tree 절에 분기 코드 블록 부재")

    values, current, orphans = {}, None, []
    for line in fence.group(1).splitlines():
        branch = _BRANCH_RE.match(line)
        if branch:
            current = None
            tail = branch.group(2)
            for pattern, name in _COMMENT_BUCKET_HINTS:
                if re.search(pattern, tail):
                    current = name
                    break
            continue
        assigned = _BUCKET_ASSIGN_RE.match(line)
        if assigned:
            current = assigned.group(1)
            continue
        value = _VALUE_ASSIGN_RE.match(line)
        if value:
            if current is None:
                orphans.append(line.strip())
                continue
            values.setdefault(current, {})[value.group(1)] = _coerce_value(value.group(2))

    if orphans:
        raise IntensityContractError(
            "어느 bucket 에도 귀속되지 않는 값 대입 발견 (분기 구조 파손): %r" % orphans
        )
    missing = {b: [k for k in VALUE_KEYS if k not in values.get(b, {})]
               for b in (BUCKET_ABSENT, BUCKET_STALE, BUCKET_LOW, BUCKET_MEDIUM, BUCKET_HIGH)}
    missing = {b: ks for b, ks in missing.items() if ks}
    if missing:
        raise IntensityContractError("값 정본에서 누락된 bucket/키: %r" % missing)
    return values


def resolve_values(bucket: str, skill_path=DEFAULT_SKILL_PATH) -> dict:
    """bucket → `{parallel_spawn_cap, spawn_stagger_ms, fallback_mode}` (정본 판독)."""
    table = load_bucket_values(skill_path)
    if bucket not in table:
        raise IntensityContractError(f"값 정본에 없는 bucket: {bucket!r}")
    return table[bucket]
