#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/test_cfp2699_self_gate_cardinal_delta_zero.py
CFP-2699 Phase 2 self-test — AC-13 execution-backed dogfood self-gate
(Change Plan §8.2 / §8.2.1 Test Contract SSOT 이행).

계약: C 增分(genre-doc "## 저작시점 예방(PREVENTIVE)" 절)이 landed census oracle 기준
**신규 present-normative cardinal flag 순증 0** (CFP-2697 baseline {L91,L93,L107} 대비) ∧
삽입 PREVENTIVE 블록 line 범위 안 신규 cardinal flag = 0 임을 **실 census 재실행**으로 assert.

재사용 (신규 로직 0 — AC-11 execution-backed reuse): scripts/lib/decision_record_disposition.py 의
`_census_over_files` / `classify` / `axis_cardinal_bound` / `_TUPLE_RE` 를 그대로 소비.
presence-grep 금지(false-oracle) — 실 census 함수를 import·구동한다.

판정 = baseline-relative 순증 0 (NOT whole-file exit-0 — §8.2 FIX-1 상속):
  whole-file census EXIT=1 은 baseline 부터 정직 참(teaching-content line-scanner FP —
  phantom "6-tuple invariant" 를 '기술'하는 문장 3곳). exit-code 를 oracle 로 쓰지 않는다.

★anti-hollow (self-ref 최고위험 — CFP-2697 M3/M4 discipline 상속):
  · O1 (invariant)        : 삽입 PREVENTIVE 블록 line 범위 안 census flag == 0 (C增分 순증 0 직접 증명).
  · O2 (baseline-preserve): census flag == 3 ∧ 전부 PREVENTIVE 블록 밖 teaching 라인(N-tuple 포함).
  · O3 (positive-control) : 알려진 flag 라인을 PREVENTIVE 블록 안에 주입 → census 가 그 라인을
                            블록 범위 안에서 검출 → O1 의 0-flag 이 "블록 미scan / oracle dead" 로
                            인한 vacuous PASS(항상-0 tautology) 가 아님을 반증.

tier (execution-falsified, §8.2): **V2(가변값 cardinal-embed) = execution-tier**(본 test 가 실증).
  V1(phantom-semantic)·V3(false-tombstone) = review-tier — census line-scanner 가 자연어 semantic·
  삭제된 줄을 구조적으로 미검출(정직명시, AC-14). 본 test 는 V2 축만 기계 실증하며 "재발 근절"
  hard-claim 하지 않는다(honest ceiling).
"""
import os
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "lib"))

import decision_record_disposition as D  # noqa: E402  (재사용 SSOT — 재구현 0)

GENRE_DOC = os.path.join(
    REPO_ROOT, "docs", "domain-knowledge", "domain",
    "governance-principle", "decision-record-genre-layers.md",
)
# CFP-2697 A 착지 teaching-content baseline {L91,L93,L107} (Change Plan §8.2/§8.2.1 SSOT).
# C 增分은 이 3건에 대해 순증 0 이어야 한다(신규 present-normative cardinal flag 0).
BASELINE_FLAG_COUNT = 3
PREVENTIVE_HEADER = "## 저작시점 예방 (PREVENTIVE)"
NEXT_HEADER = "## 경계"


def _read_lines():
    with open(GENRE_DOC, encoding="utf-8") as fh:
        return fh.readlines()


def _preventive_block_range(lines):
    """PREVENTIVE 절 [start, end) 1-based line 범위 — C 增분 삽입 블록 식별."""
    start = end = None
    for i, raw in enumerate(lines, start=1):
        stripped = raw.rstrip("\n")
        if stripped == PREVENTIVE_HEADER:
            start = i
        elif start is not None and stripped == NEXT_HEADER:
            end = i
            break
    assert start is not None, "PREVENTIVE 절 헤더 부재 — C 增分 미landed?"
    assert end is not None and end > start, "PREVENTIVE 절 종료(## 경계) 부재"
    return start, end


def _census_flags(paths):
    res = D._census_over_files(paths)
    return [n for n in res["needs_disposition"] if "line" in n]


def test_cfp2699_self_gate_cardinal_delta_zero():
    lines = _read_lines()
    start, end = _preventive_block_range(lines)
    flags = _census_flags([GENRE_DOC])

    # ── O1 — C增分(PREVENTIVE 블록) 안 신규 cardinal flag 0 (순증 0 직접 증명) ──
    in_block = [f for f in flags if start <= f["line"] < end]
    assert in_block == [], (
        f"PREVENTIVE 블록(line {start}-{end}) 안 census cardinal flag {len(in_block)}건 — "
        f"C 增分이 신규 cardinal zombie 를 유입했다(순증 위반): "
        f"{[(f['line'], f['text'][:60]) for f in in_block]}"
    )

    # ── O2 — baseline flag-set 보존: 총 3건 ∧ 전부 블록 밖 teaching 라인 ──
    assert len(flags) == BASELINE_FLAG_COUNT, (
        f"census cardinal flag {len(flags)}건 != baseline {BASELINE_FLAG_COUNT} — "
        f"CFP-2697 teaching-content {{L91,L93,L107}} 대비 순증/순감: "
        f"{[f['line'] for f in flags]}"
    )
    for f in flags:
        assert not (start <= f["line"] < end)  # O1 재확인 (블록 밖)
        assert D._TUPLE_RE.search(f["text"].lower()), (
            f"flag @line {f['line']} 에 \\d+-tuple 부재 — 예상 밖 flag: {f['text'][:60]}"
        )

    # ── O3 — positive-control (liveness / anti-vacuous) ──
    # 알려진 flag 라인(baseline teaching 라인)을 PREVENTIVE 블록 안(header 직후)에 주입 →
    # census 가 그 라인을 블록 범위 안에서 flag 검출함을 실증. O1 의 0-flag 이 "블록 미scan"
    # 이나 "oracle dead" 로 인한 항상-0 tautology 가 아님을 반증(discriminating case).
    poison = flags[0]["text"]  # baseline flagged 라인 원문(disposition=correct 확정)
    injected_lineno = start + 1
    poisoned_lines = lines[:start] + [poison + "\n"] + lines[start:]
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8", newline=""
    ) as tf:
        tf.write("".join(poisoned_lines))
        poisoned_path = tf.name
    try:
        pflags = _census_flags([poisoned_path])
        assert len(pflags) == BASELINE_FLAG_COUNT + 1, (
            f"positive-control 실패 — 주입한 zombie 라인이 census flag 증가로 이어지지 않음 "
            f"(oracle dead → O1 vacuous). poisoned flags={len(pflags)}"
        )
        assert any(f["line"] == injected_lineno for f in pflags), (
            f"positive-control 실패 — 주입 라인(line {injected_lineno}, 블록 내부)을 census 가 "
            f"미검출(블록 미scan → O1 vacuous). detected lines={[f['line'] for f in pflags]}"
        )
    finally:
        os.unlink(poisoned_path)


if __name__ == "__main__":
    test_cfp2699_self_gate_cardinal_delta_zero()
    print("PASS: test_cfp2699_self_gate_cardinal_delta_zero")
