#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_platform_inherent_prose.py — NG-3 / AC-6 `platform inherent` 스캐너 + frozen 내용 앵커.

CFP-2926 Story §8.0.8 (1) NG-3. 3-state verdict = `gate_verdict`, frozen 앵커 해석 =
`frozen_anchor`, active-doc 순회 primitive = `check_fanout_subject_prose` (전부 재사용).

── 판정 목표 ──────────────────────────────────────────────────────────────
active-doc 에서 "재귀 spawn 불가 = platform inherent / platform 제약" 취지 서술 = 0 건.
동시에 frozen 앵커 **A-1(ADR-044) ∧ A-2(ADR-064) 두 개 전건**을 resolve 한다.

  ★A-2 단독 실행 금지★ — A-2 만 돌리면 `grep -F` 부재 같은 앵커 해석 규격 결함이
  드러나지 않는다(A-1 은 `[...]`·`§` 등 정규식 메타문자를 품은 줄이라 -F 부재 시
  해석이 달라진다). 그래서 두 앵커를 항상 함께 돌리고, 어느 하나라도 `ANCHOR_OK` 가
  아니면 RED 이며 `reason` 에 status 를 그대로 싣는다.

── 후보 판별 = 두 토큰의 **동시 출현** ────────────────────────────────────
  candidate(line) := platform-claim 토큰 ∈ line  AND  recursive-spawn 토큰 ∈ line

이 co-occurrence 규칙이 다음을 **규칙 자체로** 배제한다 (특례 하드코딩 0):
  - `templates/.git-hooks/pre-checkout.sample` "git platform inherent"
    → platform 토큰만 있고 spawn 토큰 없음 → 후보 아님.
  - `docs/.../spawn-default.md` "subagent 는 one-shot 이라 dialog 불가능 (…'플랫폼 제약')"
    → dialog 능력 서술이지 spawn 서술 아님 → 후보 아님.
    ★Story 정찰 목록은 이 파일을 2 site 로 셌으나 본 게이트는 1 site 만 후보로 본다 —
    dialog 축은 NG-3 의 판정 목표(재귀 spawn = platform inherent)와 disjoint.★

── 부정 문맥 판별 (3-state, ±1행 창) ──────────────────────────────────────
  same-line 부정 토큰      → `negated`  : 이미 정정된 서술 → 위반 아님
  ±1행 이웃만 부정 토큰    → `ambiguous`: ★INCONCLUSIVE★ (자동 통과 흡수 금지)
  둘 다 없음               → `violation`: RED

  ★"이웃 줄에 부정 토큰이 있으니 통과"로 흡수하지 않는다.★ 이웃 부정은 판별 불가
  신호이지 무죄 증거가 아니다 — 실측으로도 `RefactorAgent.md` 의 실제 위반 줄이 이웃
  줄의 부정 토큰 때문에 blunt ±1 창에서 통째로 침묵 통과했다(그 관측이 이 3-state
  분기의 직접 근거다).

── 이 스캐너가 보증하는 것 ────────────────────────────────────────────────
  (1) 아래 두 토큰 목록의 동시 출현 줄 중 `violation` 분류가 0 건임.
  (2) frozen 앵커 A-1 ∧ A-2 가 내용 기반으로 유일 resolve 되고 sha256 이 일치함.

── 이 스캐너가 보증하지 않는 것 (정직 선언) ──────────────────────────────
  (a) 토큰 목록 밖 표현은 미검출. "플랫폼이 원래 그렇다" 같은 우회 서술, 표/그림으로
      쪼개진 서술, 여러 줄에 걸쳐 성립하는 주장은 잡지 못한다(줄 단위 스캔).
  (b) 부정 문맥 판별은 **토큰 presence** 휴리스틱이다. "…아님"이 그 문장의 진짜 부정인지,
      다른 절의 부정인지 구별하지 않는다 → same-line 부정 토큰 하나로 무죄 방면되는
      **오통과(false negative)가 구조적으로 가능**하다. 이 스캐너는 그 갭을 닫지 않는다.
  (c) ±1행 창 밖(±2행 이상)의 정정 문맥은 보지 않는다 → `violation` 오검출 가능(fail-closed
      방향이라 침묵 통과보다는 낫지만, 오검출 0 주장 아님).
  (d) 자원 안전성: 줄 단위 선형 스캔 · anchored bounded-quantifier 정규식. 이는
      **bounded degradation 선언**이지 "임의 입력 무해(ReDoS-safe)" 단정이 아니다 —
      복잡도 회귀 self-test·wall-clock 벤치마크 미동반 (ADR-168 §결정 16 honest-ceiling).
  (e) frozen leg 은 앵커 **줄의 존재·유일성·해시**만 본다. 그 줄을 둘러싼 문맥이
      의미를 뒤집는 경우는 미검출.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_verdict as gv  # noqa: E402
import frozen_anchor as fa  # noqa: E402
import check_fanout_subject_prose as fanout  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-3:AC-6-platform-inherent-prose"

REQUIRED_FROZEN_ANCHORS = ("A-1", "A-2")

PLATFORM_CLAIM = re.compile(
    r"platform[- ]inherent|platform 제약|플랫폼 제약|platform 강제|"
    r"platform 재귀|플랫폼 재귀|platform-강제"
)
RECURSIVE_SPAWN = re.compile(
    r"재귀 ?spawn|재귀 ?스폰|recursive[_ ]spawn|재귀 ?가드|nested spawn|재귀 subagent"
)
# 이미 정정된 서술을 가리키는 토큰 (부정·메타 서술 양쪽).
NEGATION = re.compile(r"아님|아니다|아니라|오단정|정정|삭제|허용")

NEIGHBOR_WINDOW = 1

CLS_VIOLATION = "violation"
CLS_AMBIGUOUS = "ambiguous"
CLS_NEGATED = "negated"


def classify_line(lines: List[str], index: int) -> str:
    """same-line 부정 → negated / 이웃만 부정 → ambiguous / 없음 → violation."""
    if NEGATION.search(lines[index]):
        return CLS_NEGATED
    lo = max(0, index - NEIGHBOR_WINDOW)
    hi = min(len(lines), index + NEIGHBOR_WINDOW + 1)
    neighbors = lines[lo:index] + lines[index + 1 : hi]
    if any(NEGATION.search(line) for line in neighbors):
        return CLS_AMBIGUOUS
    return CLS_VIOLATION


def scan(repo_root: Path, excluded=()):
    """(findings, scanned_rel_paths) 반환. UnparseableDocError 는 호출자가 fail-closed 처리."""
    findings: List[Dict[str, object]] = []
    scanned: List[str] = []
    for path in fanout.iter_active_docs(repo_root, excluded):
        rel = fanout.normalize_rel(repo_root, path)
        lines = fanout.read_lines(path, rel)
        scanned.append(rel)
        for index, line in enumerate(lines):
            if not (PLATFORM_CLAIM.search(line) and RECURSIVE_SPAWN.search(line)):
                continue
            findings.append(
                {
                    "file": rel,
                    "line": index + 1,
                    "classification": classify_line(lines, index),
                    "text": line.strip()[:200],
                }
            )
    return findings, scanned


def check_frozen(repo_root: Path):
    """A-1 ∧ A-2 전건 실행. (status_map, failed_ids)."""
    statuses: Dict[str, object] = {}
    failed: List[str] = []
    for anchor_id in REQUIRED_FROZEN_ANCHORS:
        resolution = fa.verify_anchor(repo_root, anchor_id)
        statuses[anchor_id] = {
            "status": resolution.status,
            "path": fa.REGISTERED_ANCHORS[anchor_id]["path"],
            "line_numbers": resolution.line_numbers,
            "match_count": resolution.match_count,
            "grep_exit": resolution.grep_exit,
        }
        if resolution.status != fa.ANCHOR_OK:
            failed.append("%s=%s" % (anchor_id, resolution.status))
    return statuses, failed


def evaluate(repo_root: Path, excluded=()) -> gv.GateResult:
    identity_probe = {
        "channel": "active-doc 집합 + frozen 앵커 resolved-target",
        "active_doc_roots": list(fanout.ACTIVE_DOC_ROOTS),
        "frozen_excluded": ["archive/**"],
        "required_frozen_anchors": list(REQUIRED_FROZEN_ANCHORS),
        "repo_root": str(repo_root).replace("\\", "/"),
    }

    try:
        findings, scanned = scan(repo_root, excluded)
    except fanout.UnparseableDocError as exc:
        return gv.unknown_input(
            GATE_ID,
            "active-doc 파싱 불가 (fail-closed): %s" % (exc,),
            trace={"unparseable_file": exc.rel_path},
            identity_probe=identity_probe,
        )

    frozen_statuses, frozen_failed = check_frozen(repo_root)
    identity_probe["frozen_resolved_target"] = frozen_statuses
    identity_probe["scanned_file_digest_sha256"] = fanout.digest_paths(scanned)
    identity_probe["candidate_files"] = sorted({str(f["file"]) for f in findings})

    violations = [f for f in findings if f["classification"] == CLS_VIOLATION]
    ambiguous = [f for f in findings if f["classification"] == CLS_AMBIGUOUS]
    negated = [f for f in findings if f["classification"] == CLS_NEGATED]

    trace = {
        "files_scanned": len(scanned),
        "candidate_lines": len(findings),
        "violations": len(violations),
        "ambiguous": len(ambiguous),
        "negated": len(negated),
        "frozen_anchors_required": len(REQUIRED_FROZEN_ANCHORS),
        "frozen_anchors_ok": len(REQUIRED_FROZEN_ANCHORS) - len(frozen_failed),
        "frozen_anchor_status": {k: v["status"] for k, v in frozen_statuses.items()},
    }

    # [154-AC-3] empty-target — 스캔 대상 0 ∧ 앵커 미발견은 각각 non-GREEN.
    if not scanned:
        return gv.empty_target(
            GATE_ID,
            "스캔 대상 active-doc 0 파일 — vacuous pass 금지",
            trace=trace,
            identity_probe=identity_probe,
        )

    if frozen_failed:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "frozen 앵커 해석 실패: %s" % (", ".join(frozen_failed),),
            trace=trace,
            identity_probe=identity_probe,
        )

    if violations:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "platform-inherent 오단정 문면 %d 건 잔존: %s"
            % (len(violations), _fmt(violations)),
            trace=trace,
            identity_probe=identity_probe,
        )

    if ambiguous:
        return gv.GateResult(
            GATE_ID,
            gv.INCONCLUSIVE,
            "부정 문맥이 이웃 줄에만 존재해 판별 불가 %d 건 (자동 통과 금지): %s"
            % (len(ambiguous), _fmt(ambiguous)),
            trace=trace,
            identity_probe=identity_probe,
        )

    return gv.GateResult(
        GATE_ID,
        gv.PASS,
        "platform-inherent 오단정 0 건 ∧ frozen 앵커 %d/%d ANCHOR_OK"
        % (len(REQUIRED_FROZEN_ANCHORS), len(REQUIRED_FROZEN_ANCHORS)),
        trace=trace,
        identity_probe=identity_probe,
    )


def _fmt(findings: List[Dict[str, object]], limit: int = 12) -> str:
    head = findings[:limit]
    rendered = "; ".join("%s:%s" % (f["file"], f["line"]) for f in head)
    if len(findings) > limit:
        rendered += " (외 %d 건)" % (len(findings) - limit,)
    return rendered


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="NG-3 / AC-6 platform-inherent 문면 스캐너")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args(argv)

    repo_root = fanout.resolve_repo_root(args.repo_root)
    return gv.emit(evaluate(repo_root))


if __name__ == "__main__":
    sys.exit(main())
