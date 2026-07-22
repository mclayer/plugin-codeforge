#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/sweep_executor.py
CFP-2698 / Epic #2696 (canary artifact D6, Story A TOOL ROBUSTENING) — decision-record
정정/효력박탈/삭제 **일괄 적용** 엔진(plan → apply).

목적:
  census manifest({file, line} 목록 — 조치-필요 라인들)를 받아,
    ① `plan()`  — oracle(`classify`) 재확인 + guard(`run_guard`) 안전성 검증을 거쳐
                  action(correct/strip/delete/skip)+rationale 을 산출(편집 없음).
    ② `apply()` — plan 산출물을 **파일 단위 배치**로 실제 편집(batch-by-file) +
                  배치마다 구조 무결성 재검증(guard-per-batch).
  본 모듈은 순수 판정 로직(plan)과 파일 I/O(apply)를 분리 유지한다 — plan() 자체는
  대상 라인 read 외 편집 없음.

action 별 편집 semantics(apply):
  correct → 라인의 stale `\d+-tuple` 토큰을 `<live_count>-tuple` 로 치환(나머지 바이트 보존).
  strip   → byte-preserving moot-mark — 원본 바이트 불변 + 라인 끝에 효력박탈 마커 append.
  delete  → guard delete-path(has_semantic 포함) 재확인 통과 시에만 라인 제거; 불통과 시
            strip 으로 downgrade(그 strip 마저 guard 불통과면 fail-closed skip + surfaced 기록).
  skip    → 무편집(historical_falsehood/no_action, 또는 idempotent 재실행).

idempotency: 이미 마커가 붙었거나 이미 `<live_count>-tuple` 로 정정된 라인은 재-편집하지
  않는다(재실행 안전).

anti-overfit: 본 엔진은 target["file"]/target["line"] 를 **데이터**로만 다루며, fixture
  신원을 코드에 하드코딩하지 않는다. 특정 파일/라인 exclusion 은 caller(CLI)가 manifest 를
  필터링해 넘기는 방식으로만 이뤄진다(엔진 내부 hardcode 0).

resource-safety honest-ceiling (ADR-082 §결정 16):
  치환 정규식(`_TUPLE_RE`, oracle 재사용)은 bounded(중첩 수량자 0)이고 라인-단위로만
  쓰인다. 본 주석은 "임의 입력 무해"를 단정하지 않는다 — bounded degradation(정상
  decision-record 라인에 대해 선형)만 주장한다.

I/O 경계: `plan()` 은 대상 라인 read 만 수행(호출자가 넘긴 manifest 의 file:line 을 읽음).
  `apply()` 는 실제 파일 write 를 수행 — 전부 `encoding="utf-8", newline="\n"` 로 고정.
"""

import os
import re
import sys

_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

from decision_record_disposition import (  # noqa: E402
    classify,
    DISPOSITION_CORRECT,
    DISPOSITION_STRIP,
    DISPOSITION_DELETE,
    DISPOSITION_HISTORICAL_FALSEHOOD,
    DISPOSITION_NO_ACTION,
    _TUPLE_RE,
)
from reference_integrity_guard import run_guard, check_structural_integrity  # noqa: E402

# 효력박탈(moot-mark) 마커 — bytes 보존(원본 값 불변) + normativity 만 무효화.
_MOOT_MARKER = (
    " [효력박탈:CFP-2698 — 불변 주장이 실변경으로 반증(현행 SSOT=CLAUDE.md 브랜치 보호 §)]"
)

# CFP-2799 (gray-zone 완결) — death-marker strip 마커(별도 상수, `_MOOT_MARKER` 재인코딩 아님).
#   죽은 규칙 잔재(death-marker) 효력박탈용 — bytes 보존 + normativity 무효화. self-reflag-exempt
#   idempotency key(§11.6): 이 마커 보유 라인은 census 후보 아님 + 재편집 skip(T2 완화 수렴).
_DEATH_MARKER = (
    " [효력박탈:CFP-2799 — 죽은 규칙 잔재(death-marker) 효력 상실, 원본 bytes 보존]"
)


def _has_death_or_moot_marker(body):
    """(CFP-2799) 라인이 효력박탈 마커(`_MOOT_MARKER` 또는 `_DEATH_MARKER`)를 이미 보유하는지.
    self-reflag-exempt + delete-path idempotency 봉합의 단일 판정(§7.6 T2 / §11.6)."""
    return _MOOT_MARKER in body or _DEATH_MARKER in body

# disposition(5-enum) → sweep action(4종) 매핑.
_ACTION_MAP = {
    DISPOSITION_CORRECT: "correct",
    DISPOSITION_STRIP: "strip",
    DISPOSITION_DELETE: "delete",
    DISPOSITION_HISTORICAL_FALSEHOOD: "skip",
    DISPOSITION_NO_ACTION: "skip",
}

# action → run_guard() 에 넘길 disposition 문자열(guard 가 필요한 action 만 key 로 존재).
_GUARD_DISPOSITION_MAP = {
    "correct": "correct",
    "strip": "strip_normativity",
    "delete": "delete",
}


def _read_line_text(repo_root, file_rel, lineno):
    """repo_root/file_rel 의 lineno(1-indexed) 라인 텍스트 반환 — 읽기 실패/범위 밖이면 None."""
    abspath = os.path.join(repo_root, file_rel)
    try:
        with open(abspath, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeDecodeError):
        return None
    idx = lineno - 1
    if 0 <= idx < len(lines):
        return lines[idx].rstrip("\n")
    return None


def plan(manifest, *, repo_root, live_required_contexts=None, dated_provider=None):
    """census manifest({file, line} 목록)를 조치 계획으로 변환(편집 없음).

    각 항목마다: line_text 재-read → classify() 로 disposition 재확인 → action 매핑 →
    (correct/strip/delete 인 경우) run_guard() 로 안전성 검증. 반환 레코드는
    {file, line, disposition, guard_pass, rationale, action} — rationale 은 항상 비어있지
    않다(AC-5, classify reason + guard 요약 결합).

    action 은 이 단계에서 downgrade 하지 않는다(순수 보고) — delete guard 불통과 시의
    strip 으로의 downgrade 는 `apply()` 가 편집 시점에 수행한다(그때 재-guard 하여 strip 마저
    불통과면 fail-closed skip 하는 cascade 가 있기 때문 — plan 은 그 cascade 이전 상태를 보고).
    """
    records = []
    for item in manifest:
        file_rel = item["file"]
        lineno = item["line"]
        line_text = _read_line_text(repo_root, file_rel, lineno)
        if line_text is None:
            records.append(
                {
                    "file": file_rel,
                    "line": lineno,
                    "disposition": None,
                    "guard_pass": None,
                    "rationale": "라인 읽기 실패(파일 부재/범위 밖/인코딩 오류) — skip",
                    "action": "skip",
                }
            )
            continue

        dated = dated_provider(file_rel, lineno) if dated_provider is not None else None
        disp_res = classify(
            line_text, live_required_contexts=live_required_contexts, dated_context=dated
        )
        disposition = disp_res["disposition"]
        reason = disp_res["reason"]
        action = _ACTION_MAP.get(disposition, "skip")

        guard_pass = None
        rationale = reason
        if action in _GUARD_DISPOSITION_MAP:
            guard_disp = _GUARD_DISPOSITION_MAP[action]
            target = {"file": file_rel, "row": lineno}
            guard = run_guard(target, guard_disp, repo_root=repo_root)
            guard_pass = guard.get("pass")
            if guard_pass:
                rationale = reason + " | guard: pass"
            else:
                note = guard.get("recommend_reason") or guard.get("fail_reason") or "guard 불통과"
                rationale = reason + " | guard: " + note

        records.append(
            {
                "file": file_rel,
                "line": lineno,
                "disposition": disposition,
                "guard_pass": guard_pass,
                "rationale": rationale,
                "action": action,
            }
        )
    return records


def _already_corrected(body, live_count):
    """(idempotency) 이 라인이 이미 `<live_count>-tuple` 로 정정돼 있는지."""
    m = _TUPLE_RE.search(body.lower())
    return bool(m) and m.group(1) == str(live_count)


def apply(plan_records, *, repo_root, live_count):
    """plan() 산출 레코드를 파일별 배치로 실제 편집(batch-by-file, AC-18) + 배치별
    구조 무결성 재검증(guard-per-batch, AC-19).

    Returns
    -------
    dict : {"applied": {action: count}, "batches": [...], "surfaced": [...], "skipped": int}
    """
    by_file = {}
    order = []
    for rec in plan_records:
        f = rec["file"]
        if f not in by_file:
            by_file[f] = []
            order.append(f)
        by_file[f].append(rec)

    counts = {"correct": 0, "strip": 0, "delete": 0, "skip": 0}
    surfaced = []
    batches = []

    for file_rel in order:
        recs = by_file[file_rel]
        abspath = os.path.join(repo_root, file_rel)
        try:
            with open(abspath, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
        except (OSError, UnicodeDecodeError) as exc:
            for rec in recs:
                surfaced.append(
                    {"file": file_rel, "line": rec.get("line"), "reason": "파일 읽기 실패: %s" % exc}
                )
                counts["skip"] += 1
            batches.append({"file": file_rel, "edits": 0, "guard_pass": None, "note": "파일 읽기 실패"})
            continue

        # 라인번호 내림차순 — delete 로 라인이 사라져도 처리 전 후행 라인 인덱스가 안전.
        recs_sorted = sorted(recs, key=lambda r: r.get("line") or 0, reverse=True)
        edits = 0
        for rec in recs_sorted:
            lineno = rec.get("line")
            action = rec.get("action")
            idx = (lineno - 1) if lineno is not None else None

            if action == "skip" or idx is None or not (0 <= idx < len(lines)):
                counts["skip"] += 1
                continue

            original = lines[idx]
            body = original.rstrip("\n")

            if action == "correct":
                if _has_death_or_moot_marker(body) or _already_corrected(body, live_count):
                    counts["skip"] += 1  # idempotent — 재실행 안전
                    continue
                if not rec.get("guard_pass"):
                    surfaced.append(
                        {"file": file_rel, "line": lineno, "action": action,
                         "reason": "guard 불통과 — edit skip(fail-closed)"}
                    )
                    counts["skip"] += 1
                    continue
                new_body = _TUPLE_RE.sub("%d-tuple" % live_count, body, count=1)
                lines[idx] = new_body + "\n"
                edits += 1
                counts["correct"] += 1
                continue

            if action == "strip":
                if _has_death_or_moot_marker(body):
                    counts["skip"] += 1  # idempotent
                    continue
                if not rec.get("guard_pass"):
                    surfaced.append(
                        {"file": file_rel, "line": lineno, "action": action,
                         "reason": "guard 불통과 — edit skip(fail-closed)"}
                    )
                    counts["skip"] += 1
                    continue
                lines[idx] = body + _MOOT_MARKER + "\n"
                edits += 1
                counts["strip"] += 1
                continue

            if action == "delete":
                # ★CFP-2799 SecurityArch P1 seal — delete guard-pass 분기 marker-gap 봉합.
                #   marker 보유 라인(이미 효력박탈된 death/moot)을 guard_pass 여부와 무관하게
                #   재삭제하지 않는다(self-reflag→delete 승격 차단, idempotent). strip/downgrade
                #   분기와 동형 — 이전엔 delete guard-pass 경로만 이 체크가 없었다(latent T2).
                if _has_death_or_moot_marker(body):
                    counts["skip"] += 1  # idempotent — marker-bearing 라인 재삭제 방지
                    continue
                if rec.get("guard_pass"):
                    del lines[idx]
                    edits += 1
                    counts["delete"] += 1
                    continue
                # delete guard 불통과 → strip 으로 downgrade(그 자체도 guard 재확인, fail-closed).
                if _has_death_or_moot_marker(body):
                    counts["skip"] += 1  # idempotent
                    continue
                strip_guard = run_guard(
                    {"file": file_rel, "row": lineno}, "strip_normativity", repo_root=repo_root
                )
                if strip_guard.get("pass"):
                    lines[idx] = body + _MOOT_MARKER + "\n"
                    edits += 1
                    counts["strip"] += 1
                else:
                    surfaced.append(
                        {"file": file_rel, "line": lineno, "action": "delete",
                         "reason": "delete guard 불통과 + strip guard 도 불통과 — fail-closed skip"}
                    )
                    counts["skip"] += 1
                continue

            counts["skip"] += 1

        if edits > 0:
            with open(abspath, "w", encoding="utf-8", newline="\n") as fh:
                fh.writelines(lines)

        batch_check = check_structural_integrity({"file": file_rel}, "strip", repo_root)
        batches.append(
            {
                "file": file_rel,
                "edits": edits,
                "guard_pass": batch_check.get("structure_intact"),
            }
        )

    return {"applied": counts, "batches": batches, "surfaced": surfaced, "skipped": counts["skip"]}
