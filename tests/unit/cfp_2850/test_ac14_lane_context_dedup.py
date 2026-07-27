"""AC-14 — lane-context writer → §14↔spawn-event non-vacuous reconcile + dedup meaningful.

Change Plan §8.1.1 RTM AC-14 (2 named test). phase2 (OQ-5 leg a).
  - lane-context(실 story_key + 비-'없음' lane_label) 주입 시 dedup_section14 reconcile 이
    'vacuous'(판정 불가) 아닌 meaningful 상태(consistent/mismatch)로 판정.
  - lane_label 이 실 label 이면 dedup 이 meaningful(comparable lane set 非공백 + event_id dedup).

production 로직 재구현 금지 — 실제 dedup_section14_spawn_event.reconcile 직접 호출.
lane-context 부재(story_key='' 또는 lane_label='없음') 대조군으로 vacuous 판정력 실증
(detector 非-vacuous).
"""

from __future__ import annotations

from pathlib import Path

import dedup_section14_spawn_event as dedup  # 실 production reconcile 모듈


def _write_story_with_lanes(dir_path, lanes):
    """§14 Lane Evidence YAML block 을 가진 Story file 작성 (basename → story_key CFP-2850).

    dedup 의 _extract_section14_yaml_block(## §14 heading + ```yaml block) + _infer_story_key
    (basename 정규식) 실 파싱 대상. 반환 = story file path.
    """
    story = dir_path / "CFP-2850.md"
    lane_lines = "\n".join("  - lane: %s" % l for l in lanes)
    story.write_text(
        "# Story CFP-2850\n\n"
        "## §14 Lane Evidence\n\n"
        "```yaml\n"
        "lanes:\n"
        "%s\n"
        "```\n"
        "\n## §15 후속\n" % lane_lines,
        encoding="utf-8",
    )
    return story


def test_ac14_lane_context_writer_non_vacuous_reconcile(tmp_path, run_append):
    """lane-context(실 story_key + 실 lane_label) → reconcile 이 vacuous 아님(meaningful).

    lane-context writer 가 story_key='CFP-2850' + lane_label='구현' 을 주입 → reconcile 이
    comparable lane {구현} 을 §14 와 실제 대조 → status 'consistent'(vacuous 아님).
    대조군(lane-context 부재, lane_label→'없음') = 'vacuous'(판정 불가) 로 판정력 실증.
    """
    story = _write_story_with_lanes(tmp_path, ["구현"])
    ledger = tmp_path / "spawn-event.jsonl"

    # lane-context 주입 row (실 story_key + 실 lane_label)
    run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-lanectx", agent_id="agent-lanectx", spawn_seq="1",
    )
    result = dedup.reconcile(str(story), str(ledger), str(tmp_path))
    # 측정 assertion: lane-context 주입 → non-vacuous meaningful(consistent)
    assert result["status"] == "consistent", (
        f"lane-context(실 story_key+lane) 주입 시 non-vacuous consistent 여야 함, got {result}"
    )
    assert result["status"] != "vacuous", "lane-context 주입인데 vacuous 로 판정 (leg a 미실현)"
    assert "구현" in result["ledger_lanes"], "실 lane_label 이 comparable 로 반영돼야 함"

    # ── 대조군(detector 非-vacuous 실증): lane-context 부재 → vacuous ──
    ledger_bare = tmp_path / "spawn-event-bare.jsonl"
    run_append(  # lane_label 생략 → '없음' fallback (hook-shaped, lane-context 부재)
        ledger_bare, story_key="CFP-2850", agent_type="DeveloperAgent",
        session_id="s-bare", agent_id="a-bare", spawn_seq="1",
    )
    bare = dedup.reconcile(str(story), str(ledger_bare), str(tmp_path))
    # 측정 assertion: lane-context 부재(물리 row 有, comparable 0) → vacuous (판정력 실증)
    assert bare["status"] == "vacuous", (
        f"lane-context 부재(lane_label='없음') 는 vacuous 여야 함(reconcile 판정력 실증), got {bare}"
    )


def test_ac14_dedup_meaningful_with_lane_label(tmp_path, run_append, read_rows):
    """lane_label 실 label → dedup 이 meaningful (event_id dedup + comparable lane set 非공백).

    물리 3행(동일 identity 2 = dup event_id + distinct 1) → read-time dedup 2행,
    comparable lane {구현, 설계} 非공백 = meaningful reconcile.
    mutation: dedup 이 event_id 이중계산(collapse 실패)하면 row_count 3 → RED /
      lane_label 없이(all '없음') 이면 comparable 0 = 무의미(vacuous).
    """
    story = _write_story_with_lanes(tmp_path, ["구현", "설계"])
    ledger = tmp_path / "spawn-event.jsonl"

    for _ in range(2):  # 동일 identity 재append → dup event_id (구현)
        run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id="sess-m", agent_id="agent-m", spawn_seq="9",
        )
    run_append(  # distinct identity, 별 lane (설계)
        ledger, story_key="CFP-2850", lane_label="설계", agent_type="ArchitectAgent",
        session_id="sess-m", agent_id="agent-m2", spawn_seq="10",
    )
    assert len(read_rows(ledger)) == 3, "물리 3행 append 기대(dedup 前)"

    result = dedup.reconcile(str(story), str(ledger), str(tmp_path))
    # 측정 assertion (a): read-time dedup → 물리 3 → 2 (dup event_id collapse) = meaningful dedup
    assert result["ledger_row_count"] == 2, (
        f"dup event_id read-time dedup → row_count 2 이어야 함(3 물리행 collapse), "
        f"got {result['ledger_row_count']}"
    )
    # (b): comparable lane set 非공백 {구현, 설계} → lane_label 이 dedup 을 meaningful 하게 함
    assert set(result["ledger_lanes"]) == {"구현", "설계"}, (
        f"실 lane_label → comparable lane set 非공백(meaningful), got {result['ledger_lanes']}"
    )
    assert result["status"] == "consistent", "§14 {구현,설계} ↔ ledger {구현,설계} 정합(meaningful)"
