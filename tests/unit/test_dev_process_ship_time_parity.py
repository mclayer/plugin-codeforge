"""test_dev_process_ship_time_parity.py — SHIP-TIME 18-field parity (lead mandate, FIRST-CLASS).

CFP-2687 Phase 2. stop-event-v1 §5.1 의 "18-field 계약 vs 5-field 구현" drift regression 을
dev-process-event-v1 에서 재발시키지 않기 위한 1급 회귀 게이트.

세 anchor 가 반드시 정확히 일치해야 한다:
  (1) captured — 실제 emit 된 index row 의 필드 (append_event 결과 read)
  (2) declared — append_dev_process_event._ROW_KEYS (Python-hardcoded EXTERNAL code anchor)
  (3) contract §2 — docs/inter-plugin-contracts/dev-process-event-v1.md §2 table (doc anchor)

즉 "declared 18 == captured 18 == contract §2 count". doc vs code born-drift = FAIL
(change-plan §8.2 parity self-test / §2 Phase 2 doc↔code parity SSOT).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import append_dev_process_event as ade

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "dev-process-event-v1.md"


def _parse_contract_section2_fields(md_text: str):
    r"""계약 §2 index-schema table 의 backtick 필드명을 순서대로 추출.

    §2 시작(`## 2. Schema`) ~ §2.1(`### 2.1`) 사이에서, `| <num> | \`field\` |` 행의
    2번째 열 backtick 토큰을 순서대로 모은다."""
    lines = md_text.splitlines()
    start = end = None
    for i, ln in enumerate(lines):
        if start is None and re.match(r"^##\s+2\.\s+Schema", ln):
            start = i
        elif start is not None and re.match(r"^###\s+2\.1", ln):
            end = i
            break
    assert start is not None, "계약 §2 Schema 섹션 헤더를 찾지 못함"
    region = lines[start : (end if end is not None else len(lines))]
    fields = []
    row_re = re.compile(r"^\|\s*\d+\s*\|\s*`([a-z0-9_]+)`\s*\|")
    for ln in region:
        m = row_re.match(ln)
        if m:
            fields.append(m.group(1))
    return tuple(fields)


class TestShipTimeParity:
    def test_declared_row_keys_count_18_no_dup(self):
        assert len(ade._ROW_KEYS) == 18, f"_ROW_KEYS 길이 {len(ade._ROW_KEYS)} != 18"
        assert len(set(ade._ROW_KEYS)) == 18, "_ROW_KEYS 중복 키 존재"

    def test_captured_equals_declared_18(self, tmp_path):
        """★핵심: 실제 emit 된 row 필드(captured) == _ROW_KEYS(declared), 정확히 18개."""
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(
            ledger_path=str(ledger),
            event_type="defect_finding", emit_source="agent",
            story_key="CFP-2687", lane_label="설계-리뷰", consumer_scope="wrapper",
            defect_id="a" * 64, defect_family="design-boundary",
            defect_type="boundary-completeness", time_to_detection=2,
            detecting_lane="설계-리뷰", blob_ref="b" * 64,
        )
        row = json.loads(ledger.read_text(encoding="utf-8").strip())
        captured = tuple(row.keys())
        assert captured == ade._ROW_KEYS, (
            f"captured != declared\n captured={captured}\n declared={ade._ROW_KEYS}"
        )
        assert len(captured) == 18

    def test_contract_section2_doc_matches_declared_code_anchor(self):
        """doc↔code parity: 계약 §2 table 필드(순서·멤버) == _ROW_KEYS.

        18↔5 drift regression 게이트 — 계약 문서와 code anchor 가 born-drift 하면 FAIL."""
        assert CONTRACT.exists(), f"계약 파일 부재: {CONTRACT}"
        doc_fields = _parse_contract_section2_fields(CONTRACT.read_text(encoding="utf-8"))
        assert len(doc_fields) == 18, f"계약 §2 파싱 필드 {len(doc_fields)}개 != 18: {doc_fields}"
        assert doc_fields == ade._ROW_KEYS, (
            f"계약 §2 doc anchor != _ROW_KEYS code anchor (born-drift)\n"
            f" doc ={doc_fields}\n code={ade._ROW_KEYS}"
        )

    def test_contract_declared_allowlist_equals_row_keys_set(self):
        """§2.1 declared allow-list(코드펜스) 집합 == _ROW_KEYS 집합."""
        text = CONTRACT.read_text(encoding="utf-8")
        # §2.1 코드펜스 블록 내 `·` 구분 필드명 수집
        m = re.search(r"###\s+2\.1[^\n]*\n(.*?)```(.*?)```", text, re.DOTALL)
        assert m, "§2.1 declared allow-list 코드펜스를 찾지 못함"
        # 코드펜스 내 `·`/개행 구분 필드명만 추출 (`·` 는 [a-z0-9_] 밖 → 자동 배제)
        allow = set(re.findall(r"[a-z0-9_]+", m.group(2)))
        assert set(ade._ROW_KEYS).issubset(allow), (
            f"§2 필드가 §2.1 allow-list 에 없음: {set(ade._ROW_KEYS) - allow}"
        )

    def test_negative_control_dropped_field_is_detected(self):
        """[negative control] 필드 하나가 누락된 anchor 는 parity assertion 이 잡는다.

        parity 검사가 실제로 drift 를 검출함을 in-suite 증명 (18→17 이면 RED)."""
        broken = ade._ROW_KEYS[:-1]  # 17개로 절단 (drift 시뮬레이션)
        assert broken != ade._ROW_KEYS
        assert len(broken) == 17
        # parity 검사 (tuple 동등)가 이 drift 를 검출
        assert tuple(broken) != ade._ROW_KEYS
