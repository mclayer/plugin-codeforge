#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# append_429_incident.py — 429-incident event tier producer (Change Plan §3.1 / §5 #2)
#
# Carrier: CFP-2967 Phase 2 (구현) — ADR-109 §결정 8.2 / ADR-043 Amendment 7 bound (2').
#
# 책임:
#   `StopFailure`(matcher rate_limit) 훅이 발화할 때 event tier 원장
#   `docs/kpi/429-incident-history.jsonl` 에 **상수 1행**을 append 한다. 그 밖 책임 0
#   (집계·판정·회전·읽기 전부 타 컴포넌트 소유 — INV-1 single-writer).
#
# ★ 이 producer 는 stdin(hook payload)을 파싱하지 않는다 — Change Plan §3.1 / §7.3 bound (2')
#   착지 행은 `timestamp` 를 제외한 전 필드가 **컴파일 시점 열거 가능한 상수**다. 따라서
#   payload 에서 읽을 값이 **0개**이며, transcript_path·cwd·session_id·prompt_id·
#   permission_mode·agent_id·에러 원문은 "필터로 막는" 것이 아니라 **도달 경로 자체가 없다**.
#   whole-object 직렬화 금지(INV-4)도 파싱 부재로 자동 성립한다. 이 파일에 sys.stdin 판독
#   경로를 추가하는 순간 bound (2') 가 깨진다 — 추가 금지.
#
# 왜 내용 봉쇄인가 (§7.0 P0): 착지면이 **공개 repo** 다(mclayer/plugin-codeforge = PUBLIC).
#   기존 telemetry 4채널은 host-local(.claude/ledger/**)이라 "host 미이탈"(bound 2)로 막았지만
#   본 채널은 git push 로 공표 경계 B3 를 넘는다. 위치 봉쇄가 불가하므로 **나갈 수 있는 것이
#   애초에 상수뿐**이라는 내용 봉쇄로 상쇄한다.
#
# 처리 순서 (비협상 — Change Plan §7.2 말미):
#   allow-list projection → 폐쇄 값공간 validate → deny-list(no-op assertion) → write
#   deny-list 매치는 "redact 성공"이 아니라 **projection 결함 신호**다(값공간이 상수뿐이므로
#   매치는 원리적으로 발생 불가). 발화 = 설계 위반이며 알림 대상 + write 중단(프라이버시 축).
#
# fail 방향 비대칭 (Change Plan §7.4):
#   - 가용성 축(기록 유실) = **fail-open** — 어떤 예외도 exit 0. 훅은 record-only 이며 게이트가
#     아니다. 실손실 = 미기록 incident 1건.
#   - 프라이버시 축(scope 판별 불능 · validate 실패 · deny 매치) = **fail-closed** — write 미수행.
#
# 제약 (Change Plan §5 #2):
#   stdlib only ∧ repo walk 0 ∧ 네트워크 0 ∧ 3rd-party import 0 ∧ subprocess 0 ∧ 동적 import 0.
#   write primitive = `append_spawn_event._append_jsonl_row` **import 재사용**(ADR-140
#   reuse-before-write, 선례 2건: append_dev_process_event.py:71,74 /
#   append_self_context_event.py:71-89). `append_stop_event.py::_atomic_append`(lock 없는
#   read-modify-write = lost-update bug) 복사 금지 — append_spawn_event.py:26-27 이 이미 이름으로
#   지목해 금지 중이다. 본 채널의 표적 시나리오가 **다수 서브에이전트 동시 429 버스트**라
#   동시 append 경합은 예외가 아니라 모달 케이스이며, lost-update 는 사건이 가장 몰릴 때
#   계수를 깎아 intensity 를 낮추는 방향으로 정확히 틀린다.

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows cp949 인코딩 회피: stdout/stderr UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── O_APPEND primitive 재사용 (ADR-140 hygiene: reuse-before-write) ──
# append_spawn_event._append_jsonl_row = cross-platform kernel-atomic single-row append
# (POSIX O_APPEND 단일-write / Windows FILE_APPEND_DATA). read-modify-write 재구현 금지.
try:
    from append_spawn_event import _append_jsonl_row
    _IMPORT_ERROR = None
except Exception:  # pragma: no cover — import path fallback
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from append_spawn_event import _append_jsonl_row
        _IMPORT_ERROR = None
    except Exception as _exc:  # write primitive 부재 = 기록 불가 (가용성 축 → fail-open)
        _append_jsonl_row = None
        _IMPORT_ERROR = _exc

# ── 429 전용 scope 판별자 재사용 (§7.3 P0) ──
# resolve_consumer_scope() 재사용 금지 — 그 판정식은 CLAUDE_PROJECT_DIR basename 휴리스틱이다.
try:
    from consumer_scope_429 import SCOPE_WRAPPER, resolve_429_scope
    _SCOPE_IMPORT_ERROR = None
except Exception:  # pragma: no cover — import path fallback
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from consumer_scope_429 import SCOPE_WRAPPER, resolve_429_scope
        _SCOPE_IMPORT_ERROR = None
    except Exception as _exc2:  # 판별 불능 = 프라이버시 축 → fail-CLOSED (write 미수행)
        SCOPE_WRAPPER = "wrapper"
        resolve_429_scope = None
        _SCOPE_IMPORT_ERROR = _exc2

_MARKER = "[codeforge-429-incident-record]"

# ── write target = 하드코딩 (T-4 path traversal 봉쇄) ─────────────────────────
# repo 루트 **아래** 이 상대 경로 단독. payload 유래 경로 사용 0 (payload 미판독).
_TARGET_RELPATH = ("docs", "kpi", "429-incident-history.jsonl")

# ── 착지 행 스키마 = 7필드 allow-list ONLY (ADR-109 §결정 8.2 / Change Plan §4.1) ──
# 키 순서는 원장 자기 헤더(:3) 선언 순서 그대로. 미상 필드는 **null 명시**, 생략 금지
# (생략은 "스키마에 없던 필드"와 "값 미상"을 구별 불가하게 만든다).
_FIELD_ORDER = (
    "timestamp",
    "lane",
    "agent_role",
    "retry_count",
    "final_status",
    "cascade_depth",
    "error_pattern",
)

# timestamp 를 제외한 전 필드의 **컴파일 시점 상수**(bound 2' 의 실체).
#   final_status = "failed" — 성공 사건은 이 채널(턴 사망 훅)에 원리적으로 미도달.
#   lane / agent_role / retry_count / cascade_depth = **항구적 null** — producer 가 신뢰성 있게
#     유도할 수 없고, 유도를 시도하면 payload 판독이 부활한다.
#   error_pattern = "rate_limit" — StopFailure matcher 토큰. ★기록 어휘 != 감지 어휘
#     (Change Plan §4.2): 이 값은 ADR-109 §결정 1 **감지집합의 원소가 아니며**, 여기 쓴다고
#     감지집합에 원소가 추가되지도 않는다(NG-2 무저촉). 감지 literal(공백 포함 자유문)을
#     producer 가 쓸 일이 없으므로 §7.5 안전 문자열 가드 충돌이 정의역에서 소거된다.
_CONSTANT_FIELDS = {
    "lane": None,
    "agent_role": None,
    "retry_count": None,
    "final_status": "failed",
    "cascade_depth": None,
    "error_pattern": "rate_limit",
}

# 폐쇄 값공간 (validate 단계). 단일 원소 CLOSED set — 확장은 계약 개정 사항이다.
_FINAL_STATUS_CLOSED = frozenset({"failed"})
_ERROR_PATTERN_CLOSED = frozenset({"rate_limit"})
_NULL_FIELDS = ("lane", "agent_role", "retry_count", "cascade_depth")

# timestamp = UTC Z strict (Change Plan §7.4.3): offset-aware, naive 금지.
#   docs/kpi/** 는 ADR-079 KST scope 밖이며, 형제 훅 subagent-stop:229 도 이미 `date -u`.
#   `TZ=Asia/Seoul date` 가 이 호스트에서 UTC 를 내는 함정을 UTC 고정이 구조적으로 회피한다.
#   기존 `+09:00` seed 2행은 **재작성 금지**(과거 행 변조 = 계약 위반, 정확성 손실 0).
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# ── deny-list = 영구 no-op assertion (Change Plan §7.2) ──────────────────────
# 값공간이 상수뿐이라 이 목록은 **한 번도 매치되지 않아야 한다**. 매치 = 필터가 일한 것이
# 아니라 **projection 이 새고 있다는 증거**이므로 write 를 중단하고 표면화한다.
# (이 목록은 redaction 층이 아니다 — redaction 을 신뢰하는 설계로 퇴행 금지.)
_DENY_PATTERNS = (
    ("payload-key", re.compile(
        r"transcript_path|session_id|prompt_id|permission_mode|hook_event_name|agent_id|cwd",
        re.IGNORECASE)),
    ("win-abs-path", re.compile(r"[A-Za-z]:[\\/]")),
    ("unc-or-backslash-path", re.compile(r"\\\\")),
    ("posix-path", re.compile(r"/[A-Za-z0-9_.\-]+/")),
    ("file-suffix", re.compile(r"\.(?:jsonl|json|md|py|txt|log|sh)\b", re.IGNORECASE)),
    ("uuid", re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-")),
    ("long-hex", re.compile(r"[0-9a-fA-F]{32,}")),
    ("credential", re.compile(r"sk-[A-Za-z0-9]|bearer\s|api[_-]?key|secret|token|password",
                              re.IGNORECASE)),
    ("home-marker", re.compile(r"~[\\/]|\$HOME|%USERPROFILE%", re.IGNORECASE)),
)


def _warn(message):
    """stderr 경고 — silent-success 금지(fail-VISIBLE). 훅 exit code 에는 영향 0."""
    sys.stderr.write("%s %s\n" % (_MARKER, message))


def _utc_now_z():
    """UTC Z strict timestamp. offset-aware 로 취득해 naive 경로를 원천 제거."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_row():
    """① allow-list projection — 7 키를 **명시 구성**한다.

    입력이 없다. payload 도 argv 도 이 dict 에 들어오지 않으며, 유일한 가변 값은
    프로세스 clock 이 낸 UTC timestamp 다. `json.dumps(payload)` 류 whole-object
    직렬화 경로 0 (INV-4) — 직렬화할 payload 객체 자체가 존재하지 않는다.
    """
    row = {"timestamp": _utc_now_z()}
    row.update(_CONSTANT_FIELDS)
    # 선언 키 순서 고정 (원장 헤더 :3 순서). 누락·초과 키는 validate 가 잡는다.
    return {key: row[key] for key in _FIELD_ORDER}


def validate_row(row):
    """② 폐쇄 값공간 validate — 위반 사유 목록 반환(빈 목록 = 통과)."""
    violations = []

    if not isinstance(row, dict):
        return ["row 가 dict 아님: %s" % type(row).__name__]

    keys = tuple(row.keys())
    if set(keys) != set(_FIELD_ORDER):
        missing = sorted(set(_FIELD_ORDER) - set(keys))
        extra = sorted(set(keys) - set(_FIELD_ORDER))
        violations.append("allow-list 이탈 — 누락=%s 초과=%s" % (missing, extra))
    elif keys != _FIELD_ORDER:
        violations.append("키 순서 이탈 — 선언 순서 %s, 실제 %s" % (list(_FIELD_ORDER), list(keys)))

    ts = row.get("timestamp")
    if not isinstance(ts, str) or not _TIMESTAMP_RE.match(ts):
        violations.append("timestamp 가 UTC Z strict 아님: %r" % (ts,))

    if row.get("final_status") not in _FINAL_STATUS_CLOSED:
        violations.append("final_status 폐쇄 값공간 이탈: %r" % (row.get("final_status"),))
    if row.get("error_pattern") not in _ERROR_PATTERN_CLOSED:
        violations.append("error_pattern 폐쇄 값공간 이탈: %r" % (row.get("error_pattern"),))
    for field in _NULL_FIELDS:
        if row.get(field, "sentinel") is not None:
            violations.append("%s 는 항구적 null 이어야 한다: %r" % (field, row.get(field)))

    return violations


def deny_scan(row):
    """③ deny-list no-op assertion — 매치 패턴명 목록 반환(빈 목록 = 정상).

    비어있지 않으면 그것은 **projection 결함 신호**다(§7.2). 상수 행에서는 원리적으로
    발생하지 않으므로 발화 시 write 를 중단하고 표면화한다.
    """
    try:
        serialized = json.dumps(row, ensure_ascii=False)
    except Exception as exc:
        return ["serialize-failed:%s" % exc.__class__.__name__]
    return [name for name, pattern in _DENY_PATTERNS if pattern.search(serialized)]


def _resolve_repo_root(explicit_root):
    """착지 후보 repo 루트 해석 — **위치 해석**이지 scope 판정이 아니다.

    우선순위: 명시 인자 > CLAUDE_PROJECT_DIR > cwd.
    ★ env 는 후보 위치를 *찾는* 데만 쓰이고 **판정에는 일절 쓰이지 않는다** — 판정은
    consumer_scope_429 가 그 루트의 파일시스템 신원 사실만으로 수행한다(§7.3). basename
    문자열 검사 0. 위조된 CLAUDE_PROJECT_DIR 은 신원 자산이 없는 디렉터리를 가리키므로
    consumer floor 로 낙하한다(= 위조로 게이트를 열 수 없다).
    """
    if explicit_root:
        return Path(explicit_root)
    env_root = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if env_root.strip():
        return Path(env_root)
    return Path.cwd()


def _build_parser():
    parser = argparse.ArgumentParser(
        description="429-incident event tier producer (CFP-2967 Phase 2). stdin 미판독."
    )
    # --repo-root = 착지 루트 **명시 지정** (테스트·명시 호출 전용). 훅은 인자를 전달하지 않는다.
    # hook payload 유래 값이 아니다(payload 는 stdin 이며 본 파일이 읽지 않는다) — T-4 무저촉.
    parser.add_argument("--repo-root", default=None,
                        help="착지 repo 루트 (미지정 → CLAUDE_PROJECT_DIR → cwd)")
    return parser


def main(argv=None):
    """항상 0 을 반환한다 (record-only — 게이트 아님, block 금지)."""
    try:
        args = _build_parser().parse_args(argv)
    except SystemExit:
        return 0  # argparse 오류도 훅을 죽이지 않는다 (가용성 축 fail-open)

    try:
        root = _resolve_repo_root(args.repo_root)

        # ── 프라이버시 축 fail-CLOSED: scope 판별 불능 = write 미수행 ──
        if resolve_429_scope is None:
            _warn("scope 판별자 import 실패 — tracked write 미수행 (fail-closed): %s"
                  % (_SCOPE_IMPORT_ERROR,))
            return 0
        scope = resolve_429_scope(root)
        if scope != SCOPE_WRAPPER:
            # consumer 착지면 floor (§7.3) — opt-in 이 켜져 있어도 tracked 경로에 쓰지 않는다.
            _warn("consumer scope 판정 — tracked write 미수행 (착지면 floor). root=%s" % (root,))
            return 0

        row = build_row()                                   # ① allow-list projection

        violations = validate_row(row)                      # ② 폐쇄 값공간 validate
        if violations:
            _warn("행 validate 실패 — write 미수행: %s" % ("; ".join(violations),))
            return 0

        denied = deny_scan(row)                             # ③ deny-list no-op assertion
        if denied:
            _warn("★ deny-list 발화 = projection 결함 신호(redact 성공 아님) — write 미수행. "
                  "매치 패턴: %s" % (", ".join(denied),))
            return 0

        if _append_jsonl_row is None:                       # ④ write
            _warn("write primitive import 실패 — 기록 생략 (fail-open): %s" % (_IMPORT_ERROR,))
            return 0
        _append_jsonl_row(root.joinpath(*_TARGET_RELPATH), row)
    except Exception as exc:  # 어떤 예외도 훅을 죽이지 않는다 (graceful degradation)
        _warn("기록 실패 — 훅은 계속 진행 (fail-open): %s: %s" % (exc.__class__.__name__, exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
