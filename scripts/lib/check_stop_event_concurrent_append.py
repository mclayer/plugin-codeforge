#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_stop_event_concurrent_append.py — NG-15 / AC-3 실행 축 게이트.

CFP-2926 Story §8.0.8 (1) NG-15 행 (규칙 R 산출 — peer 열거로는 못 잡힌 2건 중 하나).
3-state verdict + execution-trace = `gate_verdict` 재사용(신규 verdict 체계 발명 0).

── AC-3 은 진입점이 2개다 (본 모듈은 그중 ★실행 축★) ──────────────────────
  NG-14 (check_stop_event_prose.py)  = 문면 축 — `:34` 거짓 보증문 부재 grep
  NG-15 (본 모듈)                     = 실행 축 — 동시 append 무손실(N=8)
★두 축은 합치지 않는다★. NG-14 는 "선언이 정직한가", NG-15 는 "코드가 실제로 무손실인가"
를 묻는다. 한 모듈로 합치면 둘 중 하나만 깨진 형상(코드는 맞고 선언이 틀린 ★거울상★,
또는 그 반대)에서 판정 사유가 섞여 분별이 사라진다.

── 판정 목표 ──────────────────────────────────────────────────────────────
N(기본 8) 개 writer 프로세스가 ★동시에★ `append_stop_event.py` 로 stop-event 원장에
1행씩 append 했을 때, 원장 행 수 == N 이고 손실 0 임을 판정한다.

왜 행 수 대조인가: lost-update 는 ★예외를 던지지 않는다★. 각 writer 가 자기 관점에서
read→write→replace 를 정상 완주하고 exit 0 을 반환하며, 소실은 마지막 `os.replace` 가
앞 writer 의 결과를 덮으면서 발생한다. ⇒ 에러 로그 기반 탐지가 ★원리적으로 불가능★
하므로 검출 수단은 행 수 대조뿐이다 (Story §2.3 ⓐ / §7 W1).

── `[154-AC-3]` empty-target 이 왜 INCONCLUSIVE 인가 (F-6′ 형판) ──────────
기대 writer 수 0 ∨ 관측 행 0 → ★INCONCLUSIVE★. `0 == 0` 이면 "손실 0" 이 산술적으로
참이 되어 ★무손실로 오독★된다 — 정확히 F-6′(전량 0행) 형판이 막는 형상이다.
특히 ★원장 경로 오타 → 0행 → vacuous pass★ 는 고전형이므로 `identity_probe` 가
resolve 된 원장 경로를 echo 한다(무엇을 실제로 봤는가).
(형제 NG-14 는 같은 `[154-AC-3]` 을 RED 로 이행한다 — Story 가 게이트별로 다르게
pin 했고 그 pin 을 그대로 따른다. 둘 다 non-GREEN 이라는 점은 동일.)

── `[154-AC-4]` unknown-input = 파싱 불가 원장 행 → exit 1 ────────────────
★행을 조용히 제외하고 통과하지 않는다★. 원장의 비어있지 않은 줄은 전부 JSON object
여야 하며, ① JSON 파싱 실패 ② object 아님 ③ stop-event-v1 판별 필드(`hook_source`)
부재 중 하나라도 있으면 RED(exit 1). ③ 을 넣는 이유 = 다른 이벤트 타입의 원장을 겨눠도
행 수만 맞으면 통과하는 ★채널 오지정★ 형상을 막기 위함.

── 두 실행 모드 ───────────────────────────────────────────────────────────
  run(기본)      : 깨끗한 원장에 N writer 를 동시 실행 → 원장 읽어 대조.
                   `--ledger-path` 미지정 시 tmpdir 에 생성(작업 트리 무오염).
  analyze-only   : writer 실행 없이 기존 원장을 읽어 `--writers` 기대치와 대조.
                   CI/사후 감사용. ★경로 오타 mutant 가 실증되는 지점★.

── 이 게이트가 보증하지 않는 것 (정직 선언) ──────────────────────────────
  (a) 관측 행 0 은 "전량 손실"과 "harness 미실행(스크립트 경로 오타·기동 실패)"을
      ★분별하지 못한다★ — 그래서 RED 가 아니라 INCONCLUSIVE 다. 분별 없이 RED 를
      내면 환경 문제를 결함으로 오귀속하고, GREEN 을 내면 vacuous pass 다.
  (b) 무손실 판정 범위는 primitive 천장을 승계한다 — local NTFS/POSIX 정규파일 +
      row 당 단일-write 한정. network share(SMB/NFS)·redirected volume 은 대상 밖이며
      torn(multi-sector interleave) 축은 아무것도 주장하지 않는다.
  (c) 동시성 재현은 ★확률적★이다. N writer 가 실제로 시간상 겹쳤는지는 본 게이트가
      직접 관측하지 않는다(겹치지 않은 실행에서도 GREEN 이 나온다). 즉 GREEN 은
      "이 실행에서 손실이 없었다"이지 "어떤 스케줄에서도 손실이 없다"가 아니다.
      RED 는 결정적 증거(손실 실측)이고 GREEN 은 반증 실패다 — 비대칭을 명시한다.
  (d) analyze-only 모드에서 공유·누적 원장을 겨누면 surplus 로 RED 가 난다(설계된
      동작 — 깨끗한 실험 채널을 요구한다). 상시 원장 감사용이 아니다.

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE (gate_verdict SSOT)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_verdict as gv  # noqa: E402
from check_fanout_subject_prose import resolve_repo_root  # noqa: E402 (공유 primitive)

# Windows console(cp949) 호환 — 기존 scripts/lib 관례 답습.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-15"

DEFAULT_WRITERS = 8
DEFAULT_SCRIPT_REL = "scripts/lib/append_stop_event.py"
DEFAULT_TIMEOUT_SEC = 60

# stop-event-v1 판별 필드 — 채널 오지정(다른 이벤트 원장) 차단용.
DISCRIMINATING_FIELD = "hook_source"


def parse_ledger(ledger_path: Path) -> Tuple[int, List[Dict[str, object]]]:
    """원장을 읽어 (유효 행 수, 파싱 불가 행 목록) 을 반환한다.

    ★파싱 불가 행을 조용히 제외하지 않는다★ — 호출자가 fail-closed RED 로 사상한다.
    파일 부재 = (0, []) — 이는 empty-target 경로(INCONCLUSIVE)로 흘러간다.
    """
    if not ledger_path.is_file():
        return 0, []

    try:
        raw = ledger_path.read_bytes()
    except OSError as exc:
        return 0, [{"line_no": 0, "reason": "ledger_read_failed: %s" % (exc,)}]

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return 0, [{"line_no": 0, "reason": "ledger_utf8_decode_failed: %s" % (exc,)}]

    valid = 0
    bad: List[Dict[str, object]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (ValueError, TypeError):
            bad.append({"line_no": idx, "reason": "ledger_row_not_json"})
            continue
        if not isinstance(row, dict):
            bad.append({"line_no": idx, "reason": "ledger_row_not_object"})
            continue
        if DISCRIMINATING_FIELD not in row:
            bad.append(
                {"line_no": idx, "reason": "ledger_row_missing_%s" % DISCRIMINATING_FIELD}
            )
            continue
        valid += 1
    return valid, bad


def run_concurrent_writers(
    script_path: Path,
    ledger_path: Path,
    writers: int,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> Tuple[List[int], List[str]]:
    """writers 개 프로세스를 동시에 띄워 각 1행씩 append 시킨다.

    Returns: (returncode 목록, 오류 문자열 목록)
    """
    errors: List[str] = []

    def _one(idx: int) -> int:
        cmd = [
            sys.executable,
            str(script_path),
            "--hook-source",
            "stop",
            "--stop-reason",
            "ng15-concurrent-probe-%d" % idx,
            "--session-id",
            "ng15-writer-%d" % idx,
            "--ledger-path",
            str(ledger_path),
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_sec,
            )
        except subprocess.TimeoutExpired:
            errors.append("writer_%d_timeout" % idx)
            return -1
        except OSError as exc:
            errors.append("writer_%d_spawn_failed: %s" % (idx, exc))
            return -1
        if proc.returncode != 0:
            errors.append(
                "writer_%d_rc=%d stderr=%s"
                % (idx, proc.returncode, (proc.stderr or "").strip()[:120])
            )
        return proc.returncode

    with ThreadPoolExecutor(max_workers=writers) as pool:
        rcs = list(pool.map(_one, range(writers)))

    return rcs, errors


def evaluate(
    expected_writers: int,
    ledger_path: Path,
    script_path: Optional[Path],
    analyze_only: bool,
    repo_root: Path,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> gv.GateResult:
    """NG-15 판정 본체."""
    ledger_path = Path(ledger_path)
    mode = "analyze" if analyze_only else "run"

    probe: Dict[str, object] = {
        "repo_root": str(repo_root),
        "mode": mode,
        # ★채널 echo★ — 무엇을 실제로 봤는가. 경로 오타 vacuous pass 의 유일 감식 지점.
        "ledger_path": str(ledger_path),
        "ledger_exists": ledger_path.is_file(),
        "script_path": str(script_path) if script_path is not None else None,
        "script_exists": bool(script_path is not None and script_path.is_file()),
        "discriminating_field": DISCRIMINATING_FIELD,
    }

    def _trace(observed: int, lost: int, unparseable: int, nonzero_rc: int) -> Dict[str, object]:
        return {
            "expected_writers": expected_writers,
            "observed_rows": observed,
            "lost_rows": lost,
            "unparseable_rows": unparseable,
            "writer_nonzero_rc": nonzero_rc,
        }

    # ── [154-AC-3] leg 1: 기대 writer 수 0 → INCONCLUSIVE ────────────────
    # `0 == 0` 을 "무손실"로 읽지 않는다 (F-6′ 형판).
    if expected_writers <= 0:
        return gv.empty_target(
            gate_id=GATE_ID,
            reason="expected_writers_zero",
            trace=_trace(0, 0, 0, 0),
            identity_probe=probe,
        )

    nonzero_rc = 0
    if not analyze_only:
        if script_path is None or not script_path.is_file():
            # 관측 자체가 성립 불가 — 0행을 "무손실"로 읽지 않고 정직하게 미판정.
            return gv.empty_target(
                gate_id=GATE_ID,
                reason="script_not_found",
                trace=_trace(0, 0, 0, 0),
                identity_probe=probe,
            )
        # 깨끗한 채널 요구 — 선재 행이 있으면 대조가 오염된다.
        pre_rows, _pre_bad = parse_ledger(ledger_path)
        if pre_rows:
            return gv.GateResult(
                gate_id=GATE_ID,
                verdict=gv.RED,
                reason="ledger_not_clean_before_run",
                trace=_trace(pre_rows, 0, 0, 0),
                identity_probe=probe,
            )
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        rcs, errors = run_concurrent_writers(
            script_path, ledger_path, expected_writers, timeout_sec
        )
        nonzero_rc = sum(1 for rc in rcs if rc != 0)
        probe["ledger_exists"] = ledger_path.is_file()
        if errors:
            probe["writer_errors"] = errors[:8]
        if nonzero_rc:
            # append_stop_event 는 계약상 항상 exit 0 — 비0 은 harness 파손 = fail-closed.
            return gv.GateResult(
                gate_id=GATE_ID,
                verdict=gv.RED,
                reason="writer_process_nonzero_rc",
                trace=_trace(0, 0, 0, nonzero_rc),
                identity_probe=probe,
            )

    observed_rows, bad_rows = parse_ledger(ledger_path)
    probe["ledger_exists"] = ledger_path.is_file()

    # ── [154-AC-4] unknown-input → fail-closed RED (exit 1) ───────────────
    # ★empty 분기보다 먼저★ — 전량이 파싱 불가면 유효 행이 0 이 되는데, 그걸
    # INCONCLUSIVE 로 흘리면 "조용히 제외 후 미판정"이 되어 fail-closed 가 무너진다.
    if bad_rows:
        probe["unparseable_detail"] = bad_rows[:8]
        return gv.unknown_input(
            gate_id=GATE_ID,
            reason="ledger_row_unparseable",
            trace=_trace(observed_rows, 0, len(bad_rows), nonzero_rc),
            identity_probe=probe,
        )

    # ── [154-AC-3] leg 2: 관측 행 0 → INCONCLUSIVE ────────────────────────
    # ★경로 오타 → 0행 → vacuous pass★ 고전형을 여기서 끊는다.
    if observed_rows == 0:
        return gv.empty_target(
            gate_id=GATE_ID,
            reason="observed_rows_zero",
            trace=_trace(0, 0, 0, nonzero_rc),
            identity_probe=probe,
        )

    lost = expected_writers - observed_rows

    if lost > 0:
        return gv.GateResult(
            gate_id=GATE_ID,
            verdict=gv.RED,
            reason="concurrent_append_row_loss",
            trace=_trace(observed_rows, lost, 0, nonzero_rc),
            identity_probe=probe,
        )

    if lost < 0:
        return gv.GateResult(
            gate_id=GATE_ID,
            verdict=gv.RED,
            reason="ledger_row_surplus",
            trace=_trace(observed_rows, lost, 0, nonzero_rc),
            identity_probe=probe,
        )

    return gv.GateResult(
        gate_id=GATE_ID,
        verdict=gv.PASS,
        reason="concurrent_append_no_loss",
        trace=_trace(observed_rows, 0, 0, nonzero_rc),
        identity_probe=probe,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_stop_event_concurrent_append.py",
        description="NG-15 — AC-3 실행 축 (동시 append 무손실 N=8).",
    )
    parser.add_argument("--repo-root", default=None, help="repo root (기본: 자동 해석)")
    parser.add_argument(
        "--writers",
        type=int,
        default=DEFAULT_WRITERS,
        help="기대 writer 수 N (기본 %d)" % DEFAULT_WRITERS,
    )
    parser.add_argument(
        "--script",
        default=None,
        help="append 스크립트 경로 (기본: <repo-root>/%s)" % DEFAULT_SCRIPT_REL,
    )
    parser.add_argument(
        "--ledger-path",
        default=None,
        help="원장 경로. run 모드 미지정 시 tmpdir 생성 / analyze-only 시 필수",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="writer 실행 없이 기존 원장만 대조",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SEC,
        help="writer 프로세스 timeout(초, 기본 %d)" % DEFAULT_TIMEOUT_SEC,
    )

    args = parser.parse_args(argv[1:] if argv else [])

    repo_root = resolve_repo_root(args.repo_root)
    script_path = (
        Path(args.script) if args.script else Path(repo_root) / DEFAULT_SCRIPT_REL
    )

    if args.analyze_only:
        if not args.ledger_path:
            result = gv.empty_target(
                gate_id=GATE_ID,
                reason="ledger_path_not_provided",
                trace={
                    "expected_writers": args.writers,
                    "observed_rows": 0,
                    "lost_rows": 0,
                    "unparseable_rows": 0,
                    "writer_nonzero_rc": 0,
                },
                identity_probe={
                    "repo_root": str(repo_root),
                    "mode": "analyze",
                    "ledger_path": None,
                },
            )
            return gv.emit(result)
        result = evaluate(
            expected_writers=args.writers,
            ledger_path=Path(args.ledger_path),
            script_path=script_path,
            analyze_only=True,
            repo_root=Path(repo_root),
            timeout_sec=args.timeout,
        )
        return gv.emit(result)

    if args.ledger_path:
        result = evaluate(
            expected_writers=args.writers,
            ledger_path=Path(args.ledger_path),
            script_path=script_path,
            analyze_only=False,
            repo_root=Path(repo_root),
            timeout_sec=args.timeout,
        )
        return gv.emit(result)

    # 기본: tmpdir 안 깨끗한 원장 (작업 트리 무오염)
    with tempfile.TemporaryDirectory(prefix="ng15-stop-event-") as tmpdir:
        result = evaluate(
            expected_writers=args.writers,
            ledger_path=Path(tmpdir) / "stop-event.jsonl",
            script_path=script_path,
            analyze_only=False,
            repo_root=Path(repo_root),
            timeout_sec=args.timeout,
        )
        return gv.emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
