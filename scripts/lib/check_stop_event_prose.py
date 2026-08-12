#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_stop_event_prose.py — NG-14 / AC-3 원장 문면 축 게이트.

CFP-2926 Story §8.0.8 (1) NG-14 행. 3-state verdict + execution-trace = `gate_verdict`,
문서 스캔 primitive(`resolve_repo_root` / `normalize_rel` / `read_lines` /
`digest_paths` / `UnparseableDocError`) = `check_fanout_subject_prose` 재사용
(둘 다 기존 공유 모듈 — 재구현 0, ADR-140 reuse-before-write).

── AC-3 은 진입점이 2개다 (본 모듈은 그중 ★문면 축★) ──────────────────────
  NG-14 (본 모듈)                     = 문면 축 — 거짓 보증문 부재 grep
  NG-15 (check_stop_event_concurrent_append.py) = 실행 축 — 동시 append 무손실(N=8)
★두 축은 합치지 않는다★ — 문면만 고치고 코드를 안 고치거나(그 반대) 한쪽만 GREEN 인
형상을 분별해야 하기 때문이다. 규칙 R 이 "진입점 2개인데 1개만 등재"를 잡아 NG-15 를
신설한 것이 정확히 이 이유다 (Story §8.0.8 (0)).

── 판정 목표 ──────────────────────────────────────────────────────────────
`scripts/lib/append_stop_event.py` 헤더에 있던 ★거짓 보증문★

    #   multi-process concurrent append 는 이 패턴으로 보장.

이 **부재**함을 판정한다. 이 문장은 거짓이다 — `os.replace` 는 rename 원자성만 보장하고
read-modify-write 구간을 보호하지 않는다. 그리고 이 문장이 W1(lost-update) 을 전파시킨
원인이다(후속 저자가 헤더를 읽고 안전하다고 믿을 근거를 제공했다). 코드만 고치고 주석을
남기면 `declared-not-bound` 의 ★거울상★(코드는 맞고 선언이 틀린 형상)이 된다
(Story §2.3 ⓑ / §5.3 AC-3 / §7 W1).

── 2 leg (한쪽만이면 hollow) ──────────────────────────────────────────────
  L-1 (제거 leg)   : `FORBIDDEN_PATTERNS` 매치 1건이라도 있으면 → RED
  L-2 (보존 leg)   : `REQUIRED_ANCHORS`(honest-ceiling 선언 + 명명된 위험) 가
                     사라지면 → RED

L-2 가 없으면 "헤더 주석을 통째로 지우는" 변경이 L-1 을 ★자동 통과★한다 — 거짓 보증문도
사라지지만 honest ceiling 선언도 함께 사라져, 다음 저자가 같은 bug 를 재도입할 근거
공백이 복원된다. L-2 는 ★additive 강화 leg★ 이며(§8.0.8 NG-14 행은 제거 leg 만 pin),
reason code 를 분리해 두어 판정 사유가 섞이지 않는다.

── empty-target 이 왜 INCONCLUSIVE 가 아니라 RED 인가 ─────────────────────
Story §8.0.8 NG-14 행은 `[154-AC-3]` empty-target 을 ★RED★ 로 pin 한다
("대상 파일 미발견 → RED — 0 매치를 '정정 완료'로 읽지 않음"). 따라서 본 모듈은
`gate_verdict.empty_target()`(= INCONCLUSIVE 생성기)을 ★쓰지 않는다★.
이유: 본 게이트의 판정은 "금지 문자열 0 매치"인데, ★경로 오타 하나로 0 매치가 만들어진다★.
0 매치를 GREEN 으로 읽으면 경로 오타가 그대로 vacuous pass 가 된다(고전형). 따라서
대상 resolve 는 매치 카운트와 ★독립적으로★ 선행 검증하고, resolve 실패 = RED 다.
(형제 NG-15 는 같은 `[154-AC-3]` 을 INCONCLUSIVE 로 이행한다 — Story 가 게이트별로
다르게 pin 했고 그 pin 을 그대로 따른다.)

── 이 게이트가 보증하지 않는 것 (정직 선언) ──────────────────────────────
  (a) "모든 거짓 보증 표현"을 잡지 않는다. `FORBIDDEN_PATTERNS` 4종 밖의 표현(새로
      지어낸 우회 문구, 표/그림 셀에 분산된 서술, 미열거 언어)은 ★미검출★이다.
      검출 완전성 주장 없음 — 이 게이트는 ★기지의 회귀★(원문 복원 + 근접 변형)를 막는다.
  (b) L-2 는 앵커 ★문자열의 존재★만 본다. 문장이 살아 있어도 주변 문맥이 뒤집혀 의미가
      무력화되는 경우는 미검출.
  (c) 문면이 참인지는 판정하지 않는다 — 코드가 실제로 무손실인지는 ★NG-15(실행 축)★
      소관이다. 본 게이트 단독 GREEN 은 "코드가 안전하다"를 의미하지 않는다.
  (d) 자원 안전성: 줄 단위 선형 스캔이고 정규식 quantifier 는 전부 bounded(`{0,N}`) 이며
      nested quantifier 를 쓰지 않는다. 이는 ★bounded degradation 선언★이지
      "임의 입력 무해(ReDoS-safe)" 단정이 ★아니다★ — 복잡도 회귀 self-test·wall-clock
      벤치마크 미동반 (ADR-168 §결정 16 honest-ceiling / ADR-151 §결정 7 상속).

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE (gate_verdict SSOT)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_verdict as gv  # noqa: E402
from check_fanout_subject_prose import (  # noqa: E402  (공유 primitive 재사용)
    UnparseableDocError,
    digest_paths,
    normalize_rel,
    read_lines,
    resolve_repo_root,
)

# Windows console(cp949) 호환 — 기존 scripts/lib 관례 답습.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-14"

# ── 스캔 대상 (AC-3 문면 축의 정본 site) ──────────────────────────────────
DEFAULT_TARGETS: Tuple[str, ...] = ("scripts/lib/append_stop_event.py",)

# ── L-1 제거 leg: 금지 문면 ────────────────────────────────────────────────
# FG-1 = Story §2.3 ⓑ 가 verbatim 인용한 `:34` 원문 (origin/main 기준 실측 확인).
# FG-2~FG-4 = 근접 변형(리워딩 회귀) 방어. 전부 bounded quantifier·non-nested.
FORBIDDEN_PATTERNS: Tuple[Tuple[str, str, str], ...] = (
    (
        "FG-1",
        r"multi-process concurrent append 는 이 패턴으로 보장",
        "Story §2.3 ⓑ 인용 거짓 보증문 원문 복원",
    ),
    (
        "FG-2",
        r"(?:동시|concurrent|multi-process)[^\n]{0,80}"
        r"보장(?:한다|된다|됨|되며|되고)?\s*[.。]?\s*$",
        "동시성 축 무조건 보장 단정 (한국어 리워딩)",
    ),
    (
        "FG-3",
        r"(?i)(?:guaranteed\s+(?:under|for|in)\s+all|no\s+data\s+loss|"
        r"100\s*%\s*atomic|race[-\s]free|fully\s+atomic|always\s+safe|never\s+loses?)",
        "무조건 안전성 단정 (영어 리워딩)",
    ),
    (
        "FG-4",
        r"(?i)atomic\s+append\s+pattern\s*\(\s*POSIX\s+guarantee\s*\)",
        "origin/main 헤더 블록 제목(POSIX guarantee) 복원",
    ),
)

# ── L-2 보존 leg: 필수 문면 앵커 (부재 시 RED) ────────────────────────────
REQUIRED_ANCHORS: Tuple[Tuple[str, str, str], ...] = (
    ("HC-1", "honest ceiling", "honest-ceiling 선언 (무조건 보증 아님 명시)"),
    ("HC-2", "lost-update", "위험 클래스 명명 (재도입 방지 근거)"),
)

_COMPILED: Tuple[Tuple[str, "re.Pattern[str]", str], ...] = tuple(
    (pid, re.compile(pat), desc) for pid, pat, desc in FORBIDDEN_PATTERNS
)


def resolve_targets(
    repo_root: Path, rel_targets: Tuple[str, ...]
) -> Tuple[List[Path], List[str]]:
    """요청 대상 경로를 resolve 한다.

    ★매치 카운트와 독립적으로 선행 실행한다★ — 경로 오타 → 0 매치 → vacuous pass 를
    막는 유일한 지점이기 때문이다.

    Returns: (resolved paths, missing rel paths)
    """
    resolved: List[Path] = []
    missing: List[str] = []
    for rel in rel_targets:
        path = Path(repo_root) / rel
        if path.is_file():
            resolved.append(path)
        else:
            missing.append(rel)
    return resolved, missing


def scan_lines(lines: List[str], rel_path: str) -> List[Dict[str, object]]:
    """금지 문면 매치 수집 (L-1)."""
    findings: List[Dict[str, object]] = []
    for idx, line in enumerate(lines, start=1):
        for pid, rx, desc in _COMPILED:
            if rx.search(line):
                findings.append(
                    {
                        "pattern_id": pid,
                        "description": desc,
                        "path": rel_path,
                        "line_no": idx,
                        "line": line.strip()[:160],
                    }
                )
    return findings


def missing_anchors(all_text_lower: str) -> List[Dict[str, str]]:
    """필수 문면 앵커 부재 수집 (L-2)."""
    missing: List[Dict[str, str]] = []
    for aid, needle, desc in REQUIRED_ANCHORS:
        if needle.lower() not in all_text_lower:
            missing.append({"anchor_id": aid, "needle": needle, "description": desc})
    return missing


def evaluate(repo_root: Path, rel_targets: Tuple[str, ...]) -> gv.GateResult:
    """NG-14 판정 본체."""
    repo_root = Path(repo_root)
    resolved, missing_paths = resolve_targets(repo_root, rel_targets)
    resolved_rel = [normalize_rel(repo_root, p) for p in resolved]

    probe: Dict[str, object] = {
        "repo_root": str(repo_root),
        "requested_targets": list(rel_targets),
        "resolved_targets": resolved_rel,
        "missing_targets": missing_paths,
        "targets_digest": digest_paths(resolved_rel),
        "forbidden_pattern_ids": [pid for pid, _, _ in FORBIDDEN_PATTERNS],
        "required_anchor_ids": [aid for aid, _, _ in REQUIRED_ANCHORS],
    }

    # ── [154-AC-3] empty-target → ★RED★ (Story NG-14 행 pin) ─────────────
    # 0 매치를 "정정 완료"로 읽지 않는다. resolve 실패는 매치 카운트를 보기 전에 끝낸다.
    if missing_paths or not resolved:
        return gv.GateResult(
            gate_id=GATE_ID,
            verdict=gv.RED,
            reason="target_file_not_found",
            trace={
                "scanned_files": len(resolved),
                "scanned_lines": 0,
                "requested_targets": len(rel_targets),
                "missing_targets": len(missing_paths),
                "forbidden_matches": 0,
                "missing_anchors": len(REQUIRED_ANCHORS),
            },
            identity_probe=probe,
        )

    # ── [154-AC-4] unknown-input → fail-closed RED ────────────────────────
    scanned_lines = 0
    findings: List[Dict[str, object]] = []
    joined_lower_parts: List[str] = []
    for path in resolved:
        rel = normalize_rel(repo_root, path)
        try:
            lines = read_lines(path, rel)
        except UnparseableDocError as exc:
            return gv.unknown_input(
                gate_id=GATE_ID,
                reason="target_unparseable: %s" % (exc,),
                trace={
                    "scanned_files": len(resolved),
                    "scanned_lines": scanned_lines,
                    "requested_targets": len(rel_targets),
                    "missing_targets": 0,
                    "forbidden_matches": len(findings),
                    "unparseable_targets": 1,
                },
                identity_probe=probe,
            )
        scanned_lines += len(lines)
        joined_lower_parts.append("\n".join(lines).lower())
        findings.extend(scan_lines(lines, rel))

    # ── [154-AC-13] 추출 0 → EXTRACTION_EMPTY fail-closed ─────────────────
    # 파일은 resolve 됐는데 읽어낸 줄이 0 = 스캔 정의역이 비었다. 0 매치가 "정정 완료"로
    # 읽히는 두 번째 경로이므로 명시 분기로 분리한다("우연히 RED" 의존 금지).
    if scanned_lines == 0:
        return gv.GateResult(
            gate_id=GATE_ID,
            verdict=gv.RED,
            reason="EXTRACTION_EMPTY",
            trace={
                "scanned_files": len(resolved),
                "scanned_lines": 0,
                "requested_targets": len(rel_targets),
                "missing_targets": 0,
                "forbidden_matches": 0,
                "missing_anchors": len(REQUIRED_ANCHORS),
            },
            identity_probe=probe,
        )

    anchors_missing = missing_anchors("\n".join(joined_lower_parts))

    trace: Dict[str, object] = {
        "scanned_files": len(resolved),
        "scanned_lines": scanned_lines,
        "requested_targets": len(rel_targets),
        "missing_targets": 0,
        "forbidden_patterns": len(FORBIDDEN_PATTERNS),
        "forbidden_matches": len(findings),
        "required_anchors": len(REQUIRED_ANCHORS),
        "missing_anchors": len(anchors_missing),
    }

    # ── L-1 제거 leg ──────────────────────────────────────────────────────
    if findings:
        probe["findings"] = findings[:12]
        return gv.GateResult(
            gate_id=GATE_ID,
            verdict=gv.RED,
            reason="false_guarantee_present",
            trace=trace,
            identity_probe=probe,
        )

    # ── L-2 보존 leg (additive anti-hollow) ───────────────────────────────
    if anchors_missing:
        probe["missing_anchor_detail"] = anchors_missing
        return gv.GateResult(
            gate_id=GATE_ID,
            verdict=gv.RED,
            reason="honest_ceiling_anchor_missing",
            trace=trace,
            identity_probe=probe,
        )

    return gv.GateResult(
        gate_id=GATE_ID,
        verdict=gv.PASS,
        reason="false_guarantee_absent_and_ceiling_declared",
        trace=trace,
        identity_probe=probe,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_stop_event_prose.py",
        description="NG-14 — AC-3 원장 문면 축 (거짓 보증문 부재 + honest ceiling 존치).",
    )
    parser.add_argument("--repo-root", default=None, help="repo root (기본: 자동 해석)")
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help="스캔 대상 repo-relative 경로 (반복 가능, 기본: %s)"
        % (", ".join(DEFAULT_TARGETS),),
    )

    args = parser.parse_args(argv[1:] if argv else [])

    repo_root = resolve_repo_root(args.repo_root)
    rel_targets = tuple(args.target) if args.target else DEFAULT_TARGETS

    result = evaluate(repo_root, rel_targets)
    return gv.emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
