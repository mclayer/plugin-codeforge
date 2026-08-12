"""AC-3 stop-event — 문면 축(NG-14) · 실행 축(NG-15) 게이트 경유 검증.

CFP-2926 Story §5.3 AC-3 / §8.0.2 RTM / §8.0.8 (1) NG-14·NG-15.

★AC-3 은 진입점이 2개다★ — 규칙 R 이 "진입점 2개인데 1개만 등재"를 잡아 NG-15 를
신설했다(Story `:2030`). 본 파일도 두 축을 섞지 않는다:

  문면 축 = `check_stop_event_prose`              (NG-14)
  실행 축 = `check_stop_event_concurrent_append`  (NG-15)

RTM 명명 테스트 2종은 ★production 대상 그대로★ 판정한다(= production 을 mutate 하면
이 두 테스트가 죽는다). 게이트 자신의 판별력 실증은 별도 mutant 테스트가 담당한다 —
tmpdir 사본에만 주입하므로 작업 트리는 오염되지 않는다.

종전 구현의 결함 2건(본 회차 교체 사유, 정직 기록):
  (1) `test_stop_event_concurrent_append_no_loss` 가 `if ledger.exists():` 로 감싸여
      있어 ★원장이 안 생기면 무언 통과★했다 — 정확히 `0 == 0` 오독 형상.
  (2) `test_stop_event_header_false_guarantee_absent` 가 영어 문구
      (`guaranteed` 등)만 찾았는데, 실제 거짓 보증문은 한국어
      (`multi-process concurrent append 는 이 패턴으로 보장.`) 라 ★원문을 복원해도
      GREEN★ 이었다(mutant 무력).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import check_stop_event_concurrent_append as ng15
import check_stop_event_prose as ng14
import gate_verdict as gv

REPO_ROOT = Path(__file__).resolve().parents[3]
STOP_EVENT_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_stop_event.py"

# Story §2.3 ⓑ 인용 원문 (origin/main `scripts/lib/append_stop_event.py:34` verbatim).
FALSE_GUARANTEE_LINE = "#   multi-process concurrent append 는 이 패턴으로 보장."

# 동시성 재현은 확률적 — mutant kill 은 bounded 재시도로 실측한다(무한 재시도 금지).
MUTANT_KILL_ATTEMPTS = 5


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _make_prose_target(tmp_path: Path, text: str) -> Path:
    """tmpdir 안에 repo 형상(scripts/lib/append_stop_event.py)을 만든다."""
    repo = tmp_path / "repo"
    _write(repo / "scripts" / "lib" / "append_stop_event.py", text)
    return repo


def _build_read_modify_write_mutant(tmp_path: Path) -> Path:
    """M-C — `_atomic_append` 를 origin/main 의 read-modify-write 로 revert 한 사본.

    ★production 파일은 건드리지 않는다★ — tmpdir 사본에만 주입한다.
    """
    real = STOP_EVENT_SCRIPT.read_text(encoding="utf-8")

    head, sep, tail = real.partition(
        "def _atomic_append(ledger_path: Path, row: dict) -> None:"
    )
    assert sep, "anchor `def _atomic_append` 미발견 — mutant 구성 불가"
    _old_body, sep2, rest = tail.partition("def main() -> None:")
    assert sep2, "anchor `def main` 미발견 — mutant 구성 불가"

    rmw = '''def _atomic_append(ledger_path: Path, row: dict) -> None:
    """[MUTANT M-C] read-modify-write revert — lost-update 재도입."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if ledger_path.exists():
        existing = ledger_path.read_text(encoding="utf-8")
    new_line = json.dumps(row, ensure_ascii=False)
    if existing and not existing.endswith("\\n"):
        new_content = existing + "\\n" + new_line + "\\n"
    else:
        new_content = existing + new_line + "\\n"
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=str(ledger_path.parent), prefix=".stop-event-tmp-", suffix=".jsonl"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp_f:
            tmp_f.write(new_content)
        os.replace(tmp_path, str(ledger_path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


'''
    mutated = head + rmw + sep2 + rest
    assert "import argparse\n" in mutated
    mutated = mutated.replace(
        "import argparse\n", "import argparse\nimport json\nimport tempfile\n", 1
    )

    script = tmp_path / "mutant" / "append_stop_event.py"
    _write(script, mutated)
    return script


def _ledger_with_rows(path: Path, count: int) -> Path:
    """stop-event-v1 형상의 유효 행 count 개를 가진 원장을 만든다."""
    rows = [
        json.dumps(
            {
                "timestamp_kst": "2026-08-12T15:00:0%d+09:00" % (i % 10),
                "hook_source": "stop",
                "hook_decision": "record-only",
                "session_id": "sess-%d" % i,
                "stop_reason": "fixture",
            },
            ensure_ascii=False,
        )
        for i in range(count)
    ]
    _write(path, "\n".join(rows) + ("\n" if rows else ""))
    return path


# ══════════════════════════════════════════════════════════════════════════
# 실행 축 — NG-15
# ══════════════════════════════════════════════════════════════════════════


def test_stop_event_concurrent_append_no_loss(tmp_path):
    """AC-3 실행 축 (RTM 명명 테스트) — N=8 동시 append 시 행 손실 0.

    NG-15 게이트를 ★production `append_stop_event.py` 그대로★ 겨눠 실행한다.
    `_atomic_append` 를 read-modify-write 로 revert 하면 이 테스트가 죽는다
    (Story §8.0.2 RTM mutant M-C). 판별력 실증은
    `test_stop_event_concurrent_append_gate_kills_read_modify_write_mutant`.

    ★종전 구현의 `if ledger.exists():` 조건부 assert 를 제거했다★ — 원장 미생성 시
    무언 통과하던 경로가 곧 `0 == 0` 오독이다. 이제 관측 행 0 은 게이트가
    INCONCLUSIVE 로 낸다.
    """
    ledger = tmp_path / "stop-event.jsonl"

    result = ng15.evaluate(
        expected_writers=8,
        ledger_path=ledger,
        script_path=STOP_EVENT_SCRIPT,
        analyze_only=False,
        repo_root=REPO_ROOT,
    )

    assert result.verdict == gv.PASS, (
        "NG-15 non-GREEN: reason=%s trace=%s" % (result.reason, result.trace)
    )
    assert result.exit_code == 0
    assert result.trace["expected_writers"] == 8
    assert result.trace["observed_rows"] == 8, "행 손실 — trace=%s" % (result.trace,)
    assert result.trace["lost_rows"] == 0
    # identity_probe = resolved-target echo ([154-AC-13]) — 무엇을 실제로 봤는가.
    assert result.identity_probe["ledger_path"] == str(ledger)
    assert result.identity_probe["ledger_exists"] is True


def test_stop_event_concurrent_append_gate_kills_read_modify_write_mutant(tmp_path):
    """판별력 실증 — `_atomic_append` read-modify-write revert 사본 → RED.

    동시 스케줄 의존이라 kill 은 확률적이다. bounded 재시도(`MUTANT_KILL_ATTEMPTS`)
    안에서 ★실제 손실을 실측★해야 통과한다. 한 번도 손실이 안 나면 이 게이트는 mutant 를
    못 죽이는 것이므로 실패시키는 것이 옳다.
    """
    mutant_script = _build_read_modify_write_mutant(tmp_path)

    killed = None
    for attempt in range(MUTANT_KILL_ATTEMPTS):
        result = ng15.evaluate(
            expected_writers=8,
            ledger_path=tmp_path / ("mut-ledger-%d.jsonl" % attempt),
            script_path=mutant_script,
            analyze_only=False,
            repo_root=REPO_ROOT,
        )
        if result.verdict == gv.RED:
            killed = result
            break

    assert killed is not None, (
        "mutant 미검출 — %d 회 시도에서 손실 0 (게이트 판별력 없음)"
        % (MUTANT_KILL_ATTEMPTS,)
    )
    assert killed.exit_code == 1
    assert killed.reason == "concurrent_append_row_loss"
    assert killed.trace["lost_rows"] > 0
    assert killed.trace["observed_rows"] < 8


@pytest.mark.parametrize(
    "expected_writers,rows,reason",
    [
        (8, 0, "observed_rows_zero"),  # 원장 경로 오타 → 0행 (vacuous pass 고전형)
        (0, 8, "expected_writers_zero"),  # 기대 writer 0
    ],
)
def test_stop_event_concurrent_append_gate_empty_is_inconclusive(
    tmp_path, expected_writers, rows, reason
):
    """`[154-AC-3]` F-6′ — `0 == 0` 을 "무손실"로 읽지 않는다 (INCONCLUSIVE, exit 3)."""
    ledger = tmp_path / "stop-event.jsonl"
    if rows:
        _ledger_with_rows(ledger, rows)
    # rows == 0 이면 파일 자체를 만들지 않는다 = 경로 오타 형상.

    result = ng15.evaluate(
        expected_writers=expected_writers,
        ledger_path=ledger,
        script_path=STOP_EVENT_SCRIPT,
        analyze_only=True,
        repo_root=REPO_ROOT,
    )

    assert result.verdict == gv.INCONCLUSIVE
    assert result.exit_code == 3, "★INCONCLUSIVE 는 절대 exit 0 이 아니다★"
    assert result.reason == reason


def test_stop_event_concurrent_append_gate_unparseable_row_is_red(tmp_path):
    """`[154-AC-4]` — 파싱 불가 원장 행은 ★조용히 제외하지 않고★ fail-closed RED(exit 1)."""
    ledger = _ledger_with_rows(tmp_path / "stop-event.jsonl", 8)
    with open(ledger, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("{ this is not json\n")

    result = ng15.evaluate(
        expected_writers=8,
        ledger_path=ledger,
        script_path=STOP_EVENT_SCRIPT,
        analyze_only=True,
        repo_root=REPO_ROOT,
    )

    assert result.verdict == gv.RED
    assert result.exit_code == 1
    assert result.reason == "ledger_row_unparseable"
    assert result.trace["unparseable_rows"] == 1


def test_stop_event_concurrent_append_gate_cli_exit_code(tmp_path):
    """CLI 진입점 왕복 — main(argv) 이 verdict 별 exit code 를 그대로 반환한다."""
    ledger = _ledger_with_rows(tmp_path / "stop-event.jsonl", 8)

    rc_pass = ng15.main(
        ["prog", "--analyze-only", "--writers", "8", "--ledger-path", str(ledger)]
    )
    rc_incon = ng15.main(
        [
            "prog",
            "--analyze-only",
            "--writers",
            "8",
            "--ledger-path",
            str(tmp_path / "stop-event-TYPO.jsonl"),
        ]
    )

    assert rc_pass == 0
    assert rc_incon == 3


# ══════════════════════════════════════════════════════════════════════════
# 문면 축 — NG-14
# ══════════════════════════════════════════════════════════════════════════


def test_stop_event_header_false_guarantee_absent():
    """AC-3 문면 축 (RTM 명명 테스트) — `:34` 거짓 보증문 부재.

    NG-14 게이트를 ★production repo 그대로★ 겨눈다. `:34` 보증문을 복원하면 이
    테스트가 죽는다(Story §8.0.2 RTM mutant M-D). 판별력 실증은
    `test_stop_event_prose_gate_kills_restored_false_guarantee`.
    """
    result = ng14.evaluate(REPO_ROOT, ng14.DEFAULT_TARGETS)

    assert result.verdict == gv.PASS, (
        "NG-14 non-GREEN: reason=%s probe=%s"
        % (result.reason, result.identity_probe.get("findings"))
    )
    assert result.exit_code == 0
    # ★0 매치가 "대상을 실제로 읽어서 나온 0" 임을 함께 확인★ — 경로 오타 vacuous pass 차단.
    assert result.trace["scanned_files"] == 1
    assert result.trace["scanned_lines"] > 0
    assert result.trace["forbidden_matches"] == 0
    assert result.trace["missing_anchors"] == 0
    assert result.identity_probe["resolved_targets"] == [
        "scripts/lib/append_stop_event.py"
    ]


def test_stop_event_prose_gate_kills_restored_false_guarantee(tmp_path):
    """판별력 실증 — `:34` 거짓 보증문 원문을 복원한 사본 → RED (왕복)."""
    real = STOP_EVENT_SCRIPT.read_text(encoding="utf-8")

    clean_repo = _make_prose_target(tmp_path, real)
    before = ng14.evaluate(clean_repo, ng14.DEFAULT_TARGETS)
    assert before.verdict == gv.PASS, "negative control 실패 — 사본 자체가 RED"

    lines = real.split("\n")
    mutated = "\n".join(lines[:33] + [FALSE_GUARANTEE_LINE] + lines[33:])
    mut_repo = _make_prose_target(tmp_path / "mut", mutated)

    after = ng14.evaluate(mut_repo, ng14.DEFAULT_TARGETS)
    assert after.verdict == gv.RED
    assert after.exit_code == 1
    assert after.reason == "false_guarantee_present"
    assert after.trace["forbidden_matches"] >= 1


def test_stop_event_prose_gate_kills_honest_ceiling_removal(tmp_path):
    """판별력 실증 (L-2 보존 leg) — honest-ceiling 앵커를 통째로 지우면 RED.

    제거 leg 단독이면 "헤더 주석 전삭제"가 자동 통과한다(hollow). L-2 가 그 경로를 막는다.
    """
    real = STOP_EVENT_SCRIPT.read_text(encoding="utf-8")
    stripped = "\n".join(
        ln
        for ln in real.split("\n")
        if "honest ceiling" not in ln.lower() and "lost-update" not in ln.lower()
    )
    repo = _make_prose_target(tmp_path, stripped)

    result = ng14.evaluate(repo, ng14.DEFAULT_TARGETS)

    assert result.verdict == gv.RED
    assert result.exit_code == 1
    assert result.reason == "honest_ceiling_anchor_missing"
    assert result.trace["missing_anchors"] == 2


def test_stop_event_prose_gate_missing_target_is_red():
    """`[154-AC-3]` NG-14 pin — 대상 파일 미발견은 ★RED★ (0 매치를 '정정 완료'로 읽지 않음).

    ★형제 NG-15 와 다른 처분★: Story §8.0.8 이 게이트별로 다르게 pin 했다
    (NG-14 = RED / NG-15 = INCONCLUSIVE). 둘 다 non-GREEN 인 점은 동일.
    """
    result = ng14.evaluate(REPO_ROOT, ("scripts/lib/append_stop_event_TYPO.py",))

    assert result.verdict == gv.RED
    assert result.exit_code == 1, "경로 오타가 exit 0 이면 vacuous pass"
    assert result.reason == "target_file_not_found"
    assert result.trace["scanned_files"] == 0
    assert result.identity_probe["missing_targets"] == [
        "scripts/lib/append_stop_event_TYPO.py"
    ]


def test_stop_event_prose_gate_extraction_empty_is_red(tmp_path):
    """`[154-AC-13]` — 대상은 resolve 됐는데 읽은 줄이 0 → EXTRACTION_EMPTY RED.

    "합/매치가 우연히 0이라 RED" 가 아니라 ★명시 분기★ 로 분리돼 있는지 확인한다.
    """
    repo = _make_prose_target(tmp_path, "")

    result = ng14.evaluate(repo, ng14.DEFAULT_TARGETS)

    assert result.verdict == gv.RED
    assert result.exit_code == 1
    assert result.reason == "EXTRACTION_EMPTY"
    assert result.trace["scanned_files"] == 1
    assert result.trace["scanned_lines"] == 0
