"""AC-3 & Contract Parity — spawn-event / dev-process-event schema location parity.

Change Plan §8 AC-3 (stop_time_source 필드 기대 = AC-2b 선행조건 P) +
contract parity (Story §11.A.2 4-location / §11.A.3 5-location 정합).

★재배선 (Phase 2 구현)★ — 종전 본 파일은 계약 문서 텍스트에 대해 `field in doc_text`
substring 검사만 했다. 그 형상은 (a) 계약 문서 **어디에** 있는지 무관(주석·amendment_log
문면에만 있어도 통과) (b) `_ROW_KEYS`·§2.1 allow-list·heading 선언 수 같은 **나머지
location 을 아예 보지 않음** 이라, 정확히 본 Story 가 추적하는 "부분 착지 = born-broken"
을 통과시킨다. ⇒ 검사를 게이트 모듈 2종 경유로 재배선한다:
    scripts/lib/check_spawn_event_location_parity.py       (NG-10, 4 location)
    scripts/lib/check_dev_process_event_location_parity.py (NG-11, 5 location)

★`first_write` / `last_write` 기대 철회 (PL 판정)★ — 종전 dev-process 테스트는 이 둘을
계약 필드로 요구해 FAIL 이었다. 그러나 설계는 ★additive 2필드★(`writer_key` ·
`artifact_key`)이며 `first_write`/`last_write` 는 **계약 필드가 아니라 P2 술어의 파생 구간
끝점**이다 — Story §7.5.3 P2 정의 "`(writer_key, artifact_key)` 별 `[first_write,
last_write)` 반개구간" = timestamp 열을 `(writer_key, artifact_key)` 로 group 해 **산출**하는
값. 근거 3중: §7.5.3 "additive 2필드"(표 2행) / §11.A.3 #3 "2 row 추가 (`#19` `writer_key`
/ `#20` `artifact_key`)" / §11.A.3 #2 "18 필드 → 20 필드". ⇒ 테스트가 과잉명세였고, 기대
필드 집합을 2개로 정정한다 (계약 문서는 미접촉 — 테스트를 통과시키려 계약을 고치지 않음).

각 parity 테스트는 ★양성 1 + 음성 2★ 로 구성해 자기 판별력을 담보한다:
  - 양성: 실 repo → PASS ∧ resolve 수 = 기대 location 수
  - 음성 ①: tmpdir 사본에 location 1개 되돌림(mutant) → RED (작업 트리 무오염)
  - 음성 ②: 경로 오타 → resolve 0 → RED (★vacuous pass 고전형 차단★)

Carrier: CFP-2926 Phase 2 (구현) / Story NG-10·NG-11 + RTM §8.0.2
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# tests/conftest.py 가 scripts/lib 를 sys.path 에 주입 → 게이트 모듈 직접 import
import check_dev_process_event_location_parity as ng11
import check_spawn_event_location_parity as ng10

REPO_ROOT = Path(__file__).resolve().parents[3]
APPEND_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_spawn_event.py"
DEV_APPEND_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_dev_process_event.py"
SPAWN_CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "spawn-event-v1.md"
DEV_CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "dev-process-event-v1.md"

# AC-3 선행조건 P — spawn-event Amendment 5 additive 3 필드 (Story §11.A.1)
_SPAWN_ADDITIVE = ("agent_start_at", "agent_stop_at", "stop_time_source")
# dev-process Amendment 1 additive 2 필드 (Story §7.5.3 — first_write/last_write 는 파생값)
_DEV_ADDITIVE = ("writer_key", "artifact_key")


def _mutate_copy(src: Path, dst: Path, old: str, new: str) -> Path:
    """계약 문서 tmpdir 사본에 문자열 치환 mutant 주입 (작업 트리 무오염).

    치환이 실제로 일어났는지 assert — 앵커가 바뀌어 치환이 no-op 이면 mutant 없는
    "음성 대조"가 되어 검사 자체가 hollow 해진다.
    """
    text = src.read_text(encoding="utf-8")
    assert old in text, f"mutant anchor 부재 (문서 형상 변경?): {old!r}"
    dst.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    return dst


def test_spawn_event_schema_has_stop_time_fields(tmp_path, capture_output):
    """AC-3 전제조건 P: spawn-event 3 필드 presence 검증.

    schema contract: agent_start_at, agent_stop_at, stop_time_source 필드 존재.
    ★계약 §2 표(doc) ∧ `_ROW_KEYS`(code) 양쪽에서 firsthand 확인★ — 종전처럼
    "원장 파일이 생기면 본다" 조건부 assert 는 원장 미생성 시 vacuous pass 가 된다.

    [Discriminating: 필드 부재 → 산출 불가능 (AC-2b 연쇄 실패)]
    """
    # (1) 계약 §2 표 실파싱 — doc 축
    body = SPAWN_CONTRACT.read_text(encoding="utf-8")
    doc_fields = {name for name, _type in ng10.ses.parse_section2_fields(body)}
    assert doc_fields, "spawn-event §2 표 파싱 0행 — EXTRACTION_EMPTY (vacuous pass 차단)"
    for field in _SPAWN_ADDITIVE:
        assert field in doc_fields, f"contract §2 표에 `{field}` 미착지"

    # (2) `_ROW_KEYS` code anchor — code 축
    row_keys, status = ng10._load_row_keys(str(APPEND_SCRIPT))
    assert status == "ok", f"append_spawn_event._ROW_KEYS 미해석: {status}"
    for field in _SPAWN_ADDITIVE:
        assert field in row_keys, f"_ROW_KEYS 에 `{field}` 미착지"

    # (3) append 경로 실행 — row 가 실제로 나면 schema 정합까지 확인
    ledger = tmp_path / "test-spawn.jsonl"
    capture_output(
        [
            sys.executable,
            str(APPEND_SCRIPT),
            "--ledger-path",
            str(ledger),
            "--story-key",
            "CFP-2926",
            "--lane-label",
            "구현",
            "--agent-type",
            "QADeveloperAgent",
            "--session-id",
            "sess-ac3-test",
            "--agent-id",
            "agent-ac3",
            "--spawn-seq",
            "1",
            "--attribution-confidence",
            "attributed",
        ]
    )

    # 원장 검증 (부재 가능 — append 미활성 옵션. (1)(2) 가 이미 non-vacuous)
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                assert (
                    "agent_start_at" in row or "stop_time_source" in row
                ), "schema must declare timestamp fields"


def test_spawn_event_schema_4location_parity(tmp_path):
    """contract parity: spawn-event schema 4-location 정합 (NG-10 모듈 경유).

    Story §11.A.2 표 — frontmatter version / §2 heading 선언 수 / §2 필드 표 3 row /
    `append_spawn_event._ROW_KEYS` (+ 비계수 `amendment_log`).

    [Mutant: 필드 누락/오명명/version 미bump → RED]
    [Discriminating: 양성 PASS ∧ mutant RED ∧ 경로 오타 RED — 3자 대조]
    """
    # ── 양성: 실 repo 4 location 전건 착지 ──────────────────────────────────
    result = ng10.evaluate(str(SPAWN_CONTRACT), str(APPEND_SCRIPT))
    assert result.verdict == "PASS", (
        f"spawn-event 4-location parity 실패: {result.reason}"
    )
    assert result.trace["locations_compared"] == 4, "계수 규약 = amendment_log 제외 4"
    assert result.trace["locations_resolved"] == 4, "resolve 된 location < 4"
    assert result.trace["locations_matched"] == 4
    assert result.trace["amendment_log_matched"] == 1, "amendment_log 비계수 검사 실패"
    assert result.trace["section2_rows_parsed"] == 26
    assert result.trace["row_keys_count"] == 26
    assert result.exit_code == 0

    # ── 음성 ①: location 1개(frontmatter version) 되돌림 → RED ─────────────
    mutant = _mutate_copy(
        SPAWN_CONTRACT, tmp_path / "spawn-mutant.md",
        'version: "1.3.0"', 'version: "1.2.1"',
    )
    mres = ng10.evaluate(str(mutant), str(APPEND_SCRIPT))
    assert mres.verdict == "RED", "version 미bump mutant 가 생존 (게이트 판별력 0)"
    assert mres.exit_code == 1
    assert "L1_frontmatter_version" in mres.reason

    # ── 음성 ②: 경로 오타 → resolve 0 → RED (vacuous pass 차단) ────────────
    typo = ng10.evaluate(
        str(SPAWN_CONTRACT).replace("spawn-event-v1.md", "spawn-event-v1-typo.md"),
        str(APPEND_SCRIPT),
    )
    assert typo.verdict == "RED", "경로 오타가 GREEN — 게이트가 아니라 장식"
    assert typo.trace["locations_resolved"] < 4
    assert typo.exit_code == 1


def test_dev_process_event_5location_parity(tmp_path):
    """contract parity: dev-process-event schema 5-location 정합 (NG-11 모듈 경유).

    Story §11.A.3 표 — frontmatter version / §2 heading 선언 수 / §2 필드 표 2 row
    (`#19` `writer_key` / `#20` `artifact_key`, sha256) / ★§2.1 declared allow-list
    코드블록★ / `append_dev_process_event._ROW_KEYS` (+ 비계수 `amendment_log`).

    ★기대 필드 = `writer_key` · `artifact_key` 2개★ — `first_write`/`last_write` 는
    계약 필드가 아니라 P2 술어의 파생 구간 끝점 (§7.5.3, 본 파일 모듈 docstring).

    [Mutant: schema 필드 변경 미반영 / allow-list 미전파 → RED]
    [Discriminating: doc ↔ §2.1 allow-list ↔ code anchor 3자 정합 + 경로 오타 RED]
    """
    # ── 양성: 실 repo 5 location 전건 착지 ──────────────────────────────────
    result = ng11.evaluate(str(DEV_CONTRACT), str(DEV_APPEND_SCRIPT))
    assert result.verdict == "PASS", (
        f"dev-process-event 5-location parity 실패: {result.reason}"
    )
    assert result.trace["locations_compared"] == 5, "계수 규약 = amendment_log 제외 5"
    assert result.trace["locations_resolved"] == 5, "resolve 된 location < 5"
    assert result.trace["locations_matched"] == 5
    assert result.trace["amendment_log_matched"] == 1, "amendment_log 비계수 검사 실패"
    assert result.trace["section2_rows_parsed"] == 20
    assert result.trace["declared_allowlist_size"] == 20
    assert result.trace["row_keys_count"] == 20
    assert result.identity_probe["additive_fields_expected"] == list(_DEV_ADDITIVE)
    assert result.exit_code == 0

    # ── 음성 ①: ★브리핑이 놓쳤던 location #4★ (§2.1 allow-list) 되돌림 → RED ─
    mutant = _mutate_copy(
        DEV_CONTRACT, tmp_path / "dev-mutant.md",
        "writer_key · artifact_key", "",
    )
    mres = ng11.evaluate(str(mutant), str(DEV_APPEND_SCRIPT))
    assert mres.verdict == "RED", (
        "§2.1 allow-list 미전파 mutant 가 생존 — 3-location 착시 재현"
    )
    assert mres.exit_code == 1
    assert "L4_declared_allowlist" in mres.reason

    # ── 음성 ②: 경로 오타 → resolve 0 → RED (vacuous pass 차단) ────────────
    typo = ng11.evaluate(
        str(DEV_CONTRACT).replace(
            "dev-process-event-v1.md", "dev-process-event-v1-typo.md"
        ),
        str(DEV_APPEND_SCRIPT),
    )
    assert typo.verdict == "RED", "경로 오타가 GREEN — 게이트가 아니라 장식"
    assert typo.trace["locations_resolved"] < 5
    assert typo.exit_code == 1
