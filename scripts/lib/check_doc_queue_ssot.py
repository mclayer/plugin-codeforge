#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_doc_queue_ssot.py — CFP-2926 NG-4 / AC-8 쓰기 소유권 5-SSOT 교차 스캐너.

Story §7.9 "AC-8 — 쓰기 소유권: doc-queue ★정식화★" + 그 직후 blockquote
"★신규 발견 — AC-8 스캐너의 5번째 대조 site★" 가 규격 SSOT.
3-state verdict = `gate_verdict` 재사용 (신규 verdict 체계 발명 0).

── 판정 목표 ────────────────────────────────────────────────────────────────
AC-8 = "**write queue 두-주인이 해소된다**" — 즉 쓰기 소유권 서술이 **단일 방향**
으로 확정되고 site 간 **상호 모순 0** 이다. 본 게이트는 ★5개 SSOT site★ 각각에서
**방향(direction)** 을 독립 판정한 뒤 **교차 대조**한다:

    direction ∈ { resolved | two_master | undetermined }

  - 5 site 전건 `resolved` → PASS
  - 1 site 라도 `two_master`(역전 문면 실재) → RED  `ssot_direction_conflict`
  - 1 site 라도 `undetermined`(방향 선언 자체 부재) → RED  `ssot_direction_undetermined`

★**대조 site < 5 → non-GREEN**★ ([154-AC-3]) — ★**4 site 만 읽고 통과 금지**★.
경로 오타·파일 삭제·glob 미매치로 site 가 하나라도 resolve 되지 않으면 **내용 판정
이전에** `site_count_shortfall` INCONCLUSIVE(exit 3) 로 끊는다. "resolve 된 것만 보고
전부 통과" 는 vacuous pass 고전형이며, 본 게이트에서 가장 잡고 싶은 형상이다.

── 5 site (Story firsthand 실측 근거) ──────────────────────────────────────
| site | 경로 | 축 | Story 근거 |
|---|---|---|---|
| S1 | `docs/orchestrator-playbook.md`             | doc-queue 존폐(두 축 분리) | §5.3 AC-8 `playbook(:3233·:3560)` / §2.2 F5 |
| S2 | `plugins/codeforge-requirements/CLAUDE.md`  | lane 제출 규약 = live      | §5.3 AC-8 `lane CLAUDE.md(:22-24)` |
| S3 | `templates/story-page-structure.md`         | owner 표 drain 선언 + §11.A 정의 | §5.3 AC-8 `:702` / §7.9 처분 |
| S4 | `plugins/*/agents/*.md`                     | doc-queue permission 군    | §5.3 AC-8 `agent md 군` |
| S5 | `plugins/codeforge-design/CLAUDE.md`        | §11 소유 부모-자식 정합    | ★§7.9 5번째 site★ (`:27` §11 → §11.A) |

S1~S4 = 종전 4-SSOT, S5 = §7.9 가 추가한 **5번째** site ("AC-8 스캐너 대상 = 4-SSOT
→ 5-SSOT"). S3·S5 는 서로 다른 파일이며, S3 안의 `§11.A` require 는 S5(design 측
주장)의 **짝(counter-site)** 이다 — 편도 한쪽만 고치면 두-주인이 유지되므로 양쪽을
같은 게이트가 본다.

── 이 스캐너가 보증하지 않는 것 (정직 선언 / over-claim 금지) ──────────────
  (a) "모든 오독 가능 서술을 잡는다"가 아니라 ★열거된 패턴이 0 임을 보증★한다.
      `_ABOLITION_TOKENS` 밖의 새 표현(영어 전용 신규 문구, 표 셀에 분산된 서술,
      그림/코드블록 안 서술)은 **미검출**이다.
  (b) 면제(exempt) 판정은 ★같은 줄★ 안의 scope 한정어 유무만 본다. 한정어가 앞 줄에
      있고 abolition 이 다음 줄에 있으면 **오탐(false RED)** 이 날 수 있고, 반대로
      한정어를 장식으로 끼워 넣으면 **미탐(false GREEN)** 이 난다.
  (c) S4 는 permission **문자열 presence** 만 센다 — 그 권한이 실제로 행사되는지,
      parity 검사가 실제로 required 인지는 **본 게이트 밖**(invariant-check 소관).
  (d) direction 이 `resolved` 라는 것은 "문면이 단일 방향으로 선언돼 있다"이지
      "그 방향이 옳다"가 아니다. 방향 자체의 타당성은 리뷰 판정 축이다.

exit codes: 0 = PASS / 1 = RED / 3 = INCONCLUSIVE
"""

from __future__ import annotations

import argparse
import glob as _glob
import os
import re
import sys

from gate_verdict import (  # noqa: E402
    GateResult,
    PASS,
    RED,
    emit,
    empty_target,
    unknown_input,
)

# Windows cp949 stdout/stderr 차단 — UTF-8 강제 (기존 모듈 패턴 답습)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-4"

# ★[154-AC-3] 핵심 상수★ — 대조 site 가 이 수에 미달하면 내용 판정 이전에 non-GREEN.
EXPECTED_SITE_COUNT = 5

# S4 agent md 군 최소 보유 수. 실측(2026-08-12) = 29 파일.
# 하한을 20 으로 둔 이유: "약 30개" 라는 Story 서술의 오차를 흡수하되, 권한이 대량
# 소거되는 회귀(예: 절반 삭제)는 잡는다. 정확 개수 pin 은 roster 변동마다 false RED
# 를 내므로 채택하지 않는다 (하한 pin = 의도된 느슨함, 정직 declare).
MIN_AGENT_MD_WITH_QUEUE_PERMISSION = 20

_AGENT_MD_QUEUE_PERMISSION = re.compile(r"Write\(\.claude-work/doc-queue/\*\*\)")

# ── 역전(two-master) 검출 패턴 ──────────────────────────────────────────────
# 한 줄 안에 (queue 지시어) ∧ (폐기 어휘) 가 함께 있고, scope 한정어가 **없으면**
# "무조건적 폐기 선언" = 역전으로 본다.
_QUEUE_TOKENS = re.compile(r"doc-queue|write\s*queue|writequeue|write-queue", re.IGNORECASE)
_ABOLITION_TOKENS = re.compile(
    r"폐기|사용\s*안\s*함|사용하지\s*않|쓰지\s*않|미사용|deprecat|abolish", re.IGNORECASE
)
# scope 한정어 — 이 중 하나라도 같은 줄에 있으면 "축 한정 서술"로 면제.
#   - wrapper-self / wrapper repo 자신 : "wrapper 자신은 안 쓴다"(존폐와 disjoint, §7.9 근거 4)
#   - 두 축 / ≠ / 폐기하지 않          : 두 축 분리 declare 자체
#   - pre-CFP-32                       : ★queue **type** 축★(adr-draft·change-plan 등 구 type 의
#                                        사용 중단)은 doc-queue **존폐** 축과 disjoint.
#                                        실측 오탐 2건(playbook:3243·:3532)이 정확히 이 축이었다.
_SCOPE_QUALIFIERS = re.compile(
    r"wrapper-self|wrapper-side|wrapper\s*repo\s*자신|wrapper\s*자신|두\s*축|≠"
    r"|폐기하지\s*않|폐기가\s*아니|pre-CFP-32",
    re.IGNORECASE,
)


class SiteSpec:
    """5-SSOT 각 site 의 판정 규격.

    Attributes:
        site_id: S1~S5
        axis: 이 site 가 증언하는 소유권 축(사람용 라벨 — probe echo 대상)
        patterns: repo_root 기준 glob 패턴 목록. **전부** ≥1 파일로 resolve 돼야 site 성립.
        min_files: site 성립 최소 파일 수(S4 만 >1)
        require: [(label, compiled_regex)] — site 파일 전체에서 각각 ≥1 매치 필수
        detect_reverse: 역전 패턴 스캔 적용 여부
    """

    def __init__(self, site_id, axis, patterns, require, min_files=1, detect_reverse=True):
        self.site_id = site_id
        self.axis = axis
        self.patterns = patterns
        self.require = require
        self.min_files = min_files
        self.detect_reverse = detect_reverse


SITES = [
    SiteSpec(
        site_id="S1",
        axis="playbook — doc-queue 존폐 = 두 축 분리(wrapper-self 미사용 ≠ 폐기)",
        patterns=["docs/orchestrator-playbook.md"],
        require=[
            ("submission_convention_live", re.compile(r"제출\s*규약은?\s*\**\s*live", re.IGNORECASE)),
            ("queue_path_referenced", re.compile(r"\.claude-work/doc-queue")),
        ],
    ),
    SiteSpec(
        site_id="S2",
        axis="lane CLAUDE.md — §4.1/4.2/4.3 drain row + doc-queue 규약 = live",
        patterns=["plugins/codeforge-requirements/CLAUDE.md"],
        require=[
            ("queue_convention_live", re.compile(r"doc-queue\s*규약\s*=\s*live")),
            ("drain_mechanism_row", re.compile(r"\.claude-work/doc-queue/")),
        ],
    ),
    SiteSpec(
        site_id="S3",
        axis="story-page-structure — owner 표 write queue drain + §11.A subsection 정의",
        patterns=["templates/story-page-structure.md"],
        require=[
            ("drain_owner_row", re.compile(r"write\s*queue\s*drain")),
            ("section_11a_defined", re.compile(r"§11\.A")),
        ],
    ),
    SiteSpec(
        site_id="S4",
        axis="agent md 군 — Write(.claude-work/doc-queue/**) permission 보유",
        patterns=["plugins/*/agents/*.md"],
        require=[("agent_md_queue_permission", _AGENT_MD_QUEUE_PERMISSION)],
        min_files=MIN_AGENT_MD_WITH_QUEUE_PERMISSION,
        detect_reverse=False,
    ),
    SiteSpec(
        site_id="S5",
        axis="design CLAUDE.md — §11 소유 부모-자식 정합(design 은 §11.A 만 주장)",
        patterns=["plugins/codeforge-design/CLAUDE.md"],
        require=[
            ("section_11a_scoped", re.compile(r"§11\.A")),
            ("parent_child_declared", re.compile(r"§11\s*자체")),
        ],
    ),
]

# S5 전용 역전 패턴 — design 이 §11 **전체**를 마이그레이션 소유로 재주장하면 두-주인 부활.
_S5_BARE_SECTION11_CLAIM = re.compile(r"§11(?!\.)\s*데이터\s*마이그레이션")


class UnparseableDoc(Exception):
    """[154-AC-4] unknown-input — 읽기/디코드 실패는 조용히 제외하지 않고 올린다."""

    def __init__(self, path, detail):
        super().__init__(detail)
        self.path = path
        self.detail = detail


def _read_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().splitlines()
    except UnicodeDecodeError as exc:
        raise UnparseableDoc(path, "utf8_decode_error: %s" % (str(exc)[:80],))
    except OSError as exc:
        raise UnparseableDoc(path, "read_error: %s" % (str(exc)[:80],))


def _resolve(repo_root, pattern):
    """glob 패턴 → 정렬된 상대경로 목록 (파일만)."""
    abs_pattern = os.path.join(repo_root, pattern.replace("/", os.sep))
    hits = [p for p in _glob.glob(abs_pattern, recursive=True) if os.path.isfile(p)]
    return sorted(os.path.relpath(p, repo_root).replace(os.sep, "/") for p in hits)


def _reverse_hits(site, rel_path, lines):
    """역전(무조건적 폐기 선언) 줄 검출. 반환 = [(rel_path, lineno, snippet)]."""
    hits = []
    if not site.detect_reverse:
        return hits
    for idx, line in enumerate(lines, start=1):
        if _SCOPE_QUALIFIERS.search(line):
            continue  # scope 한정 서술 = 축 한정이라 역전 아님
        if _QUEUE_TOKENS.search(line) and _ABOLITION_TOKENS.search(line):
            hits.append((rel_path, idx, line.strip()[:120]))
        if site.site_id == "S5" and _S5_BARE_SECTION11_CLAIM.search(line):
            hits.append((rel_path, idx, line.strip()[:120]))
    return hits


def _judge_site(repo_root, site):
    """단일 site 판정.

    Returns: dict(site_id, axis, resolved(bool), paths, files, direction,
                  missing_require, reverse_hits, lines_scanned)
    Raises: UnparseableDoc
    """
    paths = []
    for pattern in site.patterns:
        paths.extend(_resolve(repo_root, pattern))
    paths = sorted(set(paths))

    info = {
        "site_id": site.site_id,
        "axis": site.axis,
        "paths": paths,
        "files": len(paths),
        "min_files": site.min_files,
        "resolved": len(paths) >= site.min_files,
        "direction": "unresolved",
        "missing_require": [],
        "reverse_hits": [],
        "lines_scanned": 0,
    }
    if not info["resolved"]:
        return info

    matched_labels = set()
    reverse_hits = []
    lines_scanned = 0
    for rel_path in paths:
        lines = _read_lines(os.path.join(repo_root, rel_path.replace("/", os.sep)))
        lines_scanned += len(lines)
        blob = "\n".join(lines)
        for label, pattern in site.require:
            if label not in matched_labels and pattern.search(blob):
                matched_labels.add(label)
        reverse_hits.extend(_reverse_hits(site, rel_path, lines))

    info["lines_scanned"] = lines_scanned
    info["reverse_hits"] = reverse_hits
    info["missing_require"] = [
        label for label, _ in site.require if label not in matched_labels
    ]

    if reverse_hits:
        info["direction"] = "two_master"
    elif info["missing_require"]:
        info["direction"] = "undetermined"
    else:
        info["direction"] = "resolved"
    return info


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_doc_queue_ssot.py",
        description="NG-4 / AC-8 쓰기 소유권 5-SSOT 교차 스캐너 (3-state verdict).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: cwd)")
    args = parser.parse_args(list(argv[1:]) if argv else [])

    repo_root = os.path.abspath(args.repo_root)

    # ── site 판정 (unknown-input 은 즉시 fail-closed RED) ────────────────────
    infos = []
    for site in SITES:
        try:
            infos.append(_judge_site(repo_root, site))
        except UnparseableDoc as exc:
            return emit(
                unknown_input(
                    gate_id=GATE_ID,
                    reason="unparseable_doc",
                    trace={
                        "sites_declared": EXPECTED_SITE_COUNT,
                        "sites_compared": len(infos),
                        "failed_site": site.site_id,
                    },
                    identity_probe={
                        "repo_root": repo_root,
                        "unparseable_path": exc.path,
                        "detail": exc.detail,
                    },
                )
            )

    resolved = [i for i in infos if i["resolved"]]
    resolved_paths = {i["site_id"]: i["paths"] for i in resolved}
    unresolved = [i for i in infos if not i["resolved"]]
    files_scanned = sum(i["files"] for i in resolved)
    lines_scanned = sum(i["lines_scanned"] for i in resolved)

    base_trace = {
        "sites_declared": EXPECTED_SITE_COUNT,
        "sites_compared": len(resolved),
        "files_scanned": files_scanned,
        "lines_scanned": lines_scanned,
        "require_checks": sum(len(s.require) for s in SITES),
    }
    base_probe = {
        "repo_root": repo_root,
        "expected_site_count": EXPECTED_SITE_COUNT,
        "resolved_site_paths": resolved_paths,
        "site_axes": {i["site_id"]: i["axis"] for i in infos},
    }

    # ── [154-AC-13] identity probe — 추출 0 이면 fail-closed ─────────────────
    if lines_scanned == 0 and resolved:
        return emit(
            unknown_input(
                gate_id=GATE_ID,
                reason="EXTRACTION_EMPTY",
                trace=base_trace,
                identity_probe=base_probe,
            )
        )

    # ── [154-AC-3] ★대조 site < 5 → non-GREEN★ (명시 분기, 내용 판정 이전) ──
    if len(resolved) < EXPECTED_SITE_COUNT:
        probe = dict(base_probe)
        probe["unresolved_sites"] = [
            {
                "site_id": i["site_id"],
                "patterns": SITES[idx].patterns,
                "files_found": i["files"],
                "min_files": i["min_files"],
            }
            for idx, i in enumerate(infos)
            if not i["resolved"]
        ]
        return emit(
            empty_target(
                gate_id=GATE_ID,
                reason="site_count_shortfall",
                trace=base_trace,
                identity_probe=probe,
            )
        )

    # ── 교차 대조 ────────────────────────────────────────────────────────────
    conflicts = [i for i in resolved if i["direction"] == "two_master"]
    if conflicts:
        trace = dict(base_trace)
        trace["conflicting_sites"] = len(conflicts)
        trace["reverse_hit_lines"] = sum(len(i["reverse_hits"]) for i in conflicts)
        probe = dict(base_probe)
        probe["reverse_hits"] = [
            {"site_id": i["site_id"], "path": h[0], "line": h[1], "text": h[2]}
            for i in conflicts
            for h in i["reverse_hits"][:3]
        ]
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="ssot_direction_conflict",
                trace=trace,
                identity_probe=probe,
            )
        )

    undetermined = [i for i in resolved if i["direction"] == "undetermined"]
    if undetermined:
        trace = dict(base_trace)
        trace["undetermined_sites"] = len(undetermined)
        probe = dict(base_probe)
        probe["missing_require"] = {
            i["site_id"]: i["missing_require"] for i in undetermined
        }
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="ssot_direction_undetermined",
                trace=trace,
                identity_probe=probe,
            )
        )

    trace = dict(base_trace)
    trace["directions_resolved"] = len(resolved)
    probe = dict(base_probe)
    probe["directions"] = {i["site_id"]: i["direction"] for i in resolved}
    return emit(
        GateResult(
            gate_id=GATE_ID,
            verdict=PASS,
            reason="five_ssot_single_direction",
            trace=trace,
            identity_probe=probe,
        )
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
