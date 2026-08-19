#!/usr/bin/env python3
"""
429 incident aggregator — Story §14 marker 축 ∪ event log 축 → docs/kpi/429-incident.json.

★ write ownership (CFP-2967 Change Plan §3.1 / §11.2 M-1 · ADR-109 §결정 8.2 `:159-160`)

  | 파일                                    | tier      | 본 스크립트의 권한 |
  |-----------------------------------------|-----------|--------------------|
  | `docs/kpi/429-incident-history.jsonl`   | event     | **READ-ONLY**      |
  | `docs/kpi/429-incident.json`            | aggregate | **단독 writer**    |

  종전 구현은 event log 에 주간 요약행을 덧붙이고, 동주 요약행을 "마지막 줄 제거" 로 지우고,
  파일 전체를 잘라낸 뒤 재기록했다 (ADR-109 자기계약 3중 위반 V-1·V-2·V-3). 본 개정은 그
  파괴적 write 경로를 **제거**한다 — single-writer invariant(INV-1) + append-only
  invariant(INV-2)의 집계기 측 이행이다.

  ★ 무증거 안전성 단정 금지 — 위 "제거했다" 는 아래 재현 명령으로 반증 가능한 형태로만
    주장한다(정적 presence 검사이며 런타임 전수 증명이 아니다):
      grep -nE 'truncate|seek\\(0\\)|open\\([^)]*["'"'"'](w|a|r\\+)' scripts/lib/measure_429_incident.py
    기대 산출 = `_atomic_write_text` 안 tmp 파일 write 1건뿐이며 그 대상은 aggregate tier 다.
    event log 를 여는 유일 지점은 `read_event_log()` 의 `Path.read_text` (읽기 전용)다.

  ★ 회전(retention)은 본 스크립트의 책임이 아니다 (Change Plan §11.3 R-1) — 회전 주체는
  producer 도 aggregator 도 아닌 **제3 actor** 다. "어차피 다시 읽는 김에" 로 축출 로직을
  여기에 접붙이면 INV-2 가 되살아난다.

★ 가산항 3종 분리 노출 (Change Plan §3.4)

  `marker_incident_count` (P1, §14 마커) · `event_incident_count` (P2, event log) ·
  합 `weekly_incident_count`. 합 안에 조용히 흡수되면 두 모집단의 기여를 사후에 분리할 수
  없다. **모집단이 상호배타**(마커 = 턴 생존 후 모델 수기 / event = `StopFailure` 턴 사망)
  이므로 합집합은 해상도가 호환되는 주간 집계에서만 성립한다.

★ fail-visible (Change Plan §11.7) — 스캔 대상이 없으면 `0` 을 쓰지 않는다

  스캔 디렉터리 부재·0파일이면 `marker_incident_count: null` + `uncomputable_reason`.
  event 축도 같은 규율을 받는다(파일 부재 / DATA 행 0 / 전 행 malformed = 미판정).
  "관측 결과 한산함" 과 "관측 자체가 없음" 을 구별 불가하게 만드는 silent-zero 는 본 Story 가
  고치러 온 결함 class 이며, event 축을 고치면서 aggregate 축에 그것을 재생산하지 않는다.

★ idempotency (Change Plan §11.6)

  집계기는 event log 를 읽기만 하고 `429-incident.json` 을 **전면 재계산**하므로 N회 실행 =
  1회와 동일하다(파괴 없이 구조적으로 성립). 정의역 = (입력 파일 집합, `--as-of`) 고정.
  `measured_at` 은 계수 결과가 아니라 관측 시각이므로 `--as-of` 미고정 시 실행마다 달라진다 —
  결정적 대조가 필요하면 `--as-of` 를 고정하라.
  ★ `history_lines[-1]` 류 "마지막 줄" 단축을 부활시키지 말 것 (§8.2 B-6 정렬 가정 금지).

CLI:
  --week         ISO week YYYY-W## (default: --as-of/now 의 UTC ISO week)
  --as-of        ISO 8601 date/datetime override ("now" 고정 — 결정적 재현용)
  --out          aggregate JSON 출력 경로 (default: docs/kpi/429-incident.json)
  --history-in   event log 입력 경로 (READ-ONLY, default: docs/kpi/429-incident-history.jsonl)
  --repo-root    repository root (default: ".")
  --stories-dir  §14 마커 스캔 디렉터리. **복수 지정 가능** (반복 지정 = 합집합).
                 미지정 시 <repo-root>/docs/stories. internal-docs 체크아웃 지목 가능.
                 경로 구성요소에 `retros` 가 있는 파일은 **제외** — ADR-109 §결정 9 가
                 "429 incident marker = §14 only" 로 못박으므로 retro 는 §14 Lane Evidence 가
                 아니며 포함 시 과다계수다.

Schema (docs/kpi/429-incident.json, schema_version 1.1):
  schema_version / history_file / measured_at / week / window_weeks /
  marker_incident_count / event_incident_count / weekly_incident_count /
  cascade_incidents / max_cascade_depth / gate_status /
  marker_malformed_count / marker_files_scanned / event_row_count_total /
  event_malformed_count / event_unparseable_timestamp_count / event_clock_anomaly_count /
  uncomputable_reason / schema_note
"""

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

SCHEMA_VERSION = "1.1"
DEFAULT_WINDOW_WEEKS = 4

# 경로 구성요소가 이 이름이면 마커 스캔에서 제외 (ADR-109 §결정 9 — §14 only)
EXCLUDED_PATH_PARTS = ("retros",)


# A1 (#1458) — collector secret redaction defense-in-depth
# 마커 regex 는 설계상 count-only(\d+) + 폐쇄 enum 이지만, 방어 심층화로 추출 스칼라를
# 전부 _coerce_int / _coerce_str_safe 로 통과시킨다. 미래에 마커 스키마가 넓어져도
# 내용이 무검증 유출되지 않는다.
_SAFE_STR_RE = re.compile(r"^[0-9A-Za-z_\-:\.]{0,128}$")

# ── 마커 계약 정본 (skills/rate-limit-429-mitigation/SKILL.md "Telemetry write" 절) ──
#   [429-auto-retry: count=<N>, final_status=<success|failed>]
#   [429-cascade: depth=<N>]
# strict = 계약 형태. loose = 접두 토큰만 (조임의 부작용을 계수하기 위한 상계).
# ★ 조임의 부작용 차단 (Change Plan §11.7): strict 로 조이면 느슨 regex 에만 걸리던 마커가
#   탈락한다. 탈락을 침묵시키면 **regex 수정 자체가 새 under-count** 다 ⇒ loose − strict 를
#   marker_malformed_count 로 계수해 보고한다(현 corpus 영향 0건이나 계수 없이 조이면
#   미래 마커에서 조용히 새기 시작한다).
_MARKER_STRICT_RE = re.compile(r"\[429-auto-retry:\s*count=(\d+),\s*final_status=(success|failed)\]")
_MARKER_LOOSE_RE = re.compile(r"\[429-auto-retry:")
_CASCADE_STRICT_RE = re.compile(r"\[429-cascade:\s*depth=(\d+)\]")
_CASCADE_LOOSE_RE = re.compile(r"\[429-cascade:")


def _coerce_int(raw, *, field):
    """Coerce regex-captured value to int; raise on non-digit (no silent fail)."""
    if not isinstance(raw, str) or not raw.isdigit():
        raise ValueError(f"[A1-guard] non-numeric value rejected for field={field!r}: {raw!r}")
    value = int(raw)
    if value < 0 or value > 10_000_000:
        raise ValueError(f"[A1-guard] out-of-range value for field={field!r}: {value}")
    return value


def _coerce_str_safe(raw, *, field):
    """Whitelist-validate string scalars — reject if any char outside [A-Za-z0-9_\\-:.]."""
    if not isinstance(raw, str) or not _SAFE_STR_RE.match(raw):
        raise ValueError(f"[A1-guard] unsafe string rejected for field={field!r}: {raw!r}")
    return raw


def _atomic_write_text(path: Path, content: str) -> None:
    """A2 (#1459) — atomic write via tmp file + os.replace (rename is atomic on same FS).

    적용 대상 = aggregate tier(`429-incident.json`) **단독**. event log 는 본 스크립트의
    write 정의역이 아니다.

    ★ 종전 `_ExclusiveFileLock`(fcntl/msvcrt) 은 제거됐다 — 그 락의 유일한 보호 대상이
      event log 의 read-modify-write 재기록 경로였고, 그 경로 자체가 제거됐기 때문이다
      (락이 남으면 "여기서 무언가를 잠그며 쓴다" 는 잘못된 신호를 남긴다).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _parse_aware(value):
    """ISO 8601 offset-aware 파싱. naive·비문자열·파싱 실패 = None (§8.2 B-2).

    naive 를 임의 tz 로 승격하지 않는다 — event log 계약(§4.1)이 offset-aware 를
    REQUIRED 로 두므로 naive 는 **계약 위반 행**이지 관용 대상이 아니다.
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


def _iso_week(dt) -> str:
    """UTC 기준 ISO week 라벨 (YYYY-W##). 행 timestamp 의 offset 이 무엇이든 동일 기준."""
    utc = dt.astimezone(timezone.utc)
    iso_year, iso_week, _ = utc.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _is_excluded(path: Path) -> bool:
    """경로 구성요소에 제외 이름(retros)이 있으면 True."""
    return any(part in EXCLUDED_PATH_PARTS for part in path.parts)


# ─────────────────────────────── marker 축 (P1) ───────────────────────────────

def scan_markers(story_dirs):
    """§14 Lane Evidence 마커 스캔 (읽기 전용).

    Returns dict:
      dirs_present / dirs_missing / files_scanned /
      incident_count / cascade_incidents / max_cascade_depth / malformed_count

    files_scanned == 0 이면 계수값은 **의미가 없다** — 호출자가 fail-visible 처리한다.
    """
    dirs_present, dirs_missing = [], []
    for d in story_dirs:
        (dirs_present if d.is_dir() else dirs_missing).append(str(d))

    seen = set()
    files = []
    for d in story_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            if _is_excluded(p):
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            files.append(p)

    incident_count = 0
    cascade_incidents = 0
    max_cascade_depth = 0
    malformed = 0

    for story_file in files:
        try:
            content = story_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            malformed += 1
            print(f"[fail-visible] unreadable story file skipped: {story_file}", file=sys.stderr)
            continue

        strict_markers = _MARKER_STRICT_RE.findall(content)
        for count_raw, status_raw in strict_markers:
            try:
                incident_count += _coerce_int(count_raw, field="429-auto-retry.count")
                _coerce_str_safe(status_raw, field="429-auto-retry.final_status")
            except ValueError as exc:
                malformed += 1
                print(f"[A1-guard] skip malformed marker in {story_file.name}: {exc}", file=sys.stderr)
        loose_hits = len(_MARKER_LOOSE_RE.findall(content))
        if loose_hits > len(strict_markers):
            delta = loose_hits - len(strict_markers)
            malformed += delta
            print(
                f"[fail-visible] {story_file.name}: 계약 형태 미달 429-auto-retry 마커 {delta}건 "
                f"(strict={len(strict_markers)} loose={loose_hits}) — 계수 제외, malformed 로 보고",
                file=sys.stderr,
            )

        strict_cascade = _CASCADE_STRICT_RE.findall(content)
        for depth_raw in strict_cascade:
            try:
                depth = _coerce_int(depth_raw, field="429-cascade.depth")
            except ValueError as exc:
                malformed += 1
                print(f"[A1-guard] skip malformed marker in {story_file.name}: {exc}", file=sys.stderr)
                continue
            cascade_incidents += 1
            max_cascade_depth = max(max_cascade_depth, depth)
        loose_cascade = len(_CASCADE_LOOSE_RE.findall(content))
        if loose_cascade > len(strict_cascade):
            delta = loose_cascade - len(strict_cascade)
            malformed += delta
            print(
                f"[fail-visible] {story_file.name}: 계약 형태 미달 429-cascade 마커 {delta}건 "
                f"(strict={len(strict_cascade)} loose={loose_cascade}) — 계수 제외, malformed 로 보고",
                file=sys.stderr,
            )

    return {
        "dirs_present": dirs_present,
        "dirs_missing": dirs_missing,
        "files_scanned": len(files),
        "incident_count": incident_count,
        "cascade_incidents": cascade_incidents,
        "max_cascade_depth": max_cascade_depth,
        "malformed_count": malformed,
    }


# ─────────────────────────────── event 축 (P2) ────────────────────────────────

def read_event_log(path: Path, *, now=None):
    """event log(JSONL)를 **읽기만** 한다. 파일 handle 은 read 모드로만 열린다.

    Returns dict:
      present / readable / data_row_count / weeks (list[str]) /
      malformed_count / json_error_count / missing_timestamp_count /
      unparseable_timestamp_count / clock_anomaly_count

    · 주석(`#`) 행과 빈 행은 DATA 행이 아니다 (§8.2 B-7).
    · 파싱 실패 행은 skip + 계수 (§8.2 B-3) — 침묵 drop 금지.
    · 미래 timestamp 는 계수만 하고 주간 집계에는 포함한다(주간 tier 는 30분 window 가 아니다);
      window 축 제외 규정(§8.2 B-5)은 소비자(intensity 분기) 정의역이다.
    · 정렬 가정 없음 (§8.2 B-6) — 전 행을 훑는다.
    """
    result = {
        "present": path.exists(),
        "readable": False,
        "data_row_count": 0,
        "weeks": [],
        "malformed_count": 0,
        "json_error_count": 0,
        "missing_timestamp_count": 0,
        "unparseable_timestamp_count": 0,
        "clock_anomaly_count": 0,
    }
    if not result["present"]:
        return result
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[fail-visible] event log unreadable: {path} ({exc})", file=sys.stderr)
        return result
    result["readable"] = True

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        result["data_row_count"] += 1
        try:
            row = json.loads(line)
        except ValueError:
            result["json_error_count"] += 1
            continue
        if not isinstance(row, dict) or "timestamp" not in row:
            result["missing_timestamp_count"] += 1
            continue
        dt = _parse_aware(row.get("timestamp"))
        if dt is None:
            result["unparseable_timestamp_count"] += 1
            continue
        if now is not None and dt > now:
            result["clock_anomaly_count"] += 1
        result["weeks"].append(_iso_week(dt))

    result["malformed_count"] = (
        result["json_error_count"]
        + result["missing_timestamp_count"]
        + result["unparseable_timestamp_count"]
    )
    return result


# ─────────────────────────────── payload 구성 ─────────────────────────────────

def build_payload(*, week, measured_at_iso, history_file_label, window_weeks,
                  marker_scan, event_scan):
    """두 축의 스캔 결과 → aggregate 페이로드. 계산 불가 축은 null + 사유."""
    uncomputable = {}

    # marker 축 — 스캔 디렉터리 부재 · 0파일이면 0 을 쓰지 않는다 (§11.7)
    if not marker_scan["dirs_present"]:
        marker_count = None
        cascade_incidents = None
        max_cascade_depth = None
        uncomputable["marker_incident_count"] = (
            "story scan directory 부재 — 지목된 경로: "
            + (", ".join(marker_scan["dirs_missing"]) or "(없음)")
        )
    elif marker_scan["files_scanned"] == 0:
        marker_count = None
        cascade_incidents = None
        max_cascade_depth = None
        uncomputable["marker_incident_count"] = (
            "story scan directory 는 실재하나 스캔 대상 .md 0개 — "
            + ", ".join(marker_scan["dirs_present"])
        )
    else:
        marker_count = marker_scan["incident_count"]
        cascade_incidents = marker_scan["cascade_incidents"]
        max_cascade_depth = marker_scan["max_cascade_depth"]

    # event 축 — 부재 / DATA 행 0 / 전 행 malformed = 미판정 (소비자 부재 정규화와 동형)
    if not event_scan["present"]:
        event_count = None
        uncomputable["event_incident_count"] = "event log 파일 부재"
    elif not event_scan["readable"]:
        event_count = None
        uncomputable["event_incident_count"] = "event log 판독 실패"
    elif event_scan["data_row_count"] == 0:
        event_count = None
        uncomputable["event_incident_count"] = "event log DATA 행 0 (주석·빈 행 제외 후)"
    elif not event_scan["weeks"]:
        event_count = None
        uncomputable["event_incident_count"] = (
            f"event log 전 DATA 행 malformed ({event_scan['malformed_count']}행) — 유효 timestamp 0"
        )
    else:
        event_count = sum(1 for w in event_scan["weeks"] if w == week)

    if marker_count is None or event_count is None:
        weekly = None
        uncomputable["weekly_incident_count"] = (
            "가산항 중 미판정이 있어 합을 낼 수 없다 (null 을 0 으로 취급 금지)"
        )
        gate_status = "uncomputable"
    else:
        weekly = marker_count + event_count
        if (cascade_incidents or 0) > 0 or weekly >= 20:
            gate_status = "alert"
        elif weekly >= 10:
            gate_status = "warning"
        else:
            gate_status = "operational"

    return {
        "schema_version": SCHEMA_VERSION,
        "history_file": history_file_label,
        "measured_at": measured_at_iso,
        "week": week,
        "window_weeks": window_weeks,
        "marker_incident_count": marker_count,
        "event_incident_count": event_count,
        "weekly_incident_count": weekly,
        "cascade_incidents": cascade_incidents,
        "max_cascade_depth": max_cascade_depth,
        "gate_status": gate_status,
        "marker_malformed_count": marker_scan["malformed_count"],
        "marker_files_scanned": marker_scan["files_scanned"],
        "event_row_count_total": event_scan["data_row_count"],
        "event_malformed_count": event_scan["malformed_count"],
        "event_unparseable_timestamp_count": event_scan["unparseable_timestamp_count"],
        "event_clock_anomaly_count": event_scan["clock_anomaly_count"],
        "uncomputable_reason": uncomputable or None,
        "schema_note": (
            "marker 축은 [429-auto-retry: count=N] 의 N 합(재시도 횟수 합)이고 event 축은 사건 행 "
            "수다 — 단위가 다르므로 weekly_incident_count 를 exact incident count 로 인용하지 "
            "말 것. 완전중복 행도 별 사건으로 계수한다(편향 방향 = 과다 = fail-safe)."
        ),
    }


def _label_for(path: Path, repo_root: Path) -> str:
    """repo-root 상대 경로 라벨 (밖이면 원 경로 문자열)."""
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def main():
    parser = argparse.ArgumentParser(
        description="Measure 429 incidents (§14 markers ∪ event log) — event log READ-ONLY"
    )
    parser.add_argument("--week", default=None, help="ISO week YYYY-W##")
    parser.add_argument("--as-of", default=None, help="ISO 8601 date override (YYYY-MM-DD)")
    parser.add_argument("--out", default=None, help="Aggregate JSON output path (단독 write target)")
    parser.add_argument("--history-in", default=None, help="Event log JSONL input path (READ-ONLY)")
    parser.add_argument(
        "--history-out",
        default=None,
        help="DEPRECATED — event log 는 더 이상 이 스크립트의 write target 이 아니다. "
             "지정 시 --history-in 으로 해석하고 경고를 낸다.",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument(
        "--stories-dir",
        action="append",
        default=None,
        dest="stories_dirs",
        help="§14 마커 스캔 디렉터리 (반복 지정 가능 = 합집합). retros 경로는 제외.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root)

    if args.as_of:
        try:
            now = datetime.strptime(args.as_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            now = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
    else:
        now = datetime.now(timezone.utc)

    week = args.week if args.week else _iso_week(now)

    out_file = Path(args.out) if args.out else repo_root / "docs" / "kpi" / "429-incident.json"

    history_in = args.history_in
    if args.history_out and not history_in:
        print(
            "[deprecated] --history-out 은 write target 이 아니다 (event log = read-only). "
            "--history-in 으로 해석한다.",
            file=sys.stderr,
        )
        history_in = args.history_out
    history_file = (
        Path(history_in) if history_in
        else repo_root / "docs" / "kpi" / "429-incident-history.jsonl"
    )

    if args.stories_dirs:
        story_dirs = [Path(d) for d in args.stories_dirs]
    else:
        story_dirs = [repo_root / "docs" / "stories"]

    marker_scan = scan_markers(story_dirs)
    event_scan = read_event_log(history_file, now=now)

    window_weeks = DEFAULT_WINDOW_WEEKS
    history_label = _label_for(history_file, repo_root)
    if out_file.exists():
        try:
            with open(out_file, encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, dict) and "window_weeks" in existing:
                window_weeks = existing["window_weeks"]
            if isinstance(existing, dict) and "history_file" in existing and not history_in:
                history_label = existing["history_file"]
        except (OSError, json.JSONDecodeError):
            pass

    payload = build_payload(
        week=week,
        measured_at_iso=now.isoformat(),
        history_file_label=history_label,
        window_weeks=window_weeks,
        marker_scan=marker_scan,
        event_scan=event_scan,
    )

    # 단독 write target — aggregate tier 뿐이다. event log 는 위에서 읽기만 했다.
    _atomic_write_text(out_file, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    def _fmt(v):
        return "null" if v is None else v

    print(
        f"[measure-429-incident] week={week} "
        f"marker={_fmt(payload['marker_incident_count'])} "
        f"event={_fmt(payload['event_incident_count'])} "
        f"weekly={_fmt(payload['weekly_incident_count'])} "
        f"cascade={_fmt(payload['cascade_incidents'])} "
        f"max_depth={_fmt(payload['max_cascade_depth'])} "
        f"gate={payload['gate_status']} "
        f"marker_malformed={payload['marker_malformed_count']} "
        f"event_rows={payload['event_row_count_total']}"
    )
    if payload["uncomputable_reason"]:
        for field, reason in payload["uncomputable_reason"].items():
            print(f"[fail-visible] {field}=null — {reason}", file=sys.stderr)


if __name__ == "__main__":
    main()
