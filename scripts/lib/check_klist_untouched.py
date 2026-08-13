#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_klist_untouched.py — NG-20 / AC-9 K-list 무접촉 스캐너.

CFP-2926 Story §8.0.8 (1) NG-20. 3-state verdict + execution-trace = `gate_verdict`,
active-doc 순회 primitive(`iter_active_docs` / `read_lines` / `resolve_repo_root` /
`normalize_rel` / `digest_paths`) = `check_fanout_subject_prose` **import 재사용**
(그 모듈 docstring 이 NG-3·NG-20 의 재사용 진입점임을 명시 — 중복 구현 0).

── 판정 목표 (AC-9) ───────────────────────────────────────────────────────
본 Story 산출물이 **K-1·K-2·K-5·K-6·K-7·K-8·K-10·K-11·K-12 (9 항)** 를 재논의·완화
하지 않는다. ★K-3·K-4 는 U-1 확정에 의한 **명시 개정 대상**이라 AC-9 무침범 범위에서
제외★, ★K-9(직렬화 5지점 목록)는 Story §4.3 D 가 **추가/제거 재논의 가능**으로 열어둔
유일 항목이라 제외★ ⇒ 12 - 3 = **9 항**.

두 leg 을 ★둘 다★ 판정한다 (한쪽만이면 hollow):

  leg-W (완화 문면 검출) : 각 K 항목 topic 근방에 **완화·재제안 행위 문면**이 있으면 RED
  leg-A (기결정 앵커)    : 각 K 항목의 **결정 문면 앵커**가 소실되면 RED

leg-A 가 없으면 "K-list 를 통째로 삭제하는" 변경이 leg-W 를 조용히 통과한다(완화 문면이
없어지므로). 특히 AC-9 이 명시 요구하는 ★K-1(nested TEAMS 금지) teams 축 무접촉 assert★
는 leg-A 가 진다.

── 판별 3-state (topic 근방 창 기준) ──────────────────────────────────────
후보 = `topic` 매치 줄. 매치 **위치 기준 좌우 `TOPIC_WINDOW` 문자 창** 안에서:

  weaken ∧ ¬uphold  → `weakening` : RED
  weaken ∧ uphold   → `ambiguous` : ★INCONCLUSIVE★ (자동 통과 흡수 금지)
  ¬weaken           → `mention`   : 후보 아님 (K 항목 **언급 자체는 위반이 아니다** —
                                    수십 개 문서가 K 항목을 인용·준수 서술한다)

★줄 전체가 아니라 창을 보는 이유★: `재귀 spawn 금지 · nested team 금지 ·
one-team-per-lead` 처럼 여러 규범이 한 줄에 나열되는 문서가 많아, 줄 단위로 보면
옆 규범의 동사가 엉뚱한 K 항목에 귀속된다(오검출·오통과 양방향).

── 4항목 이행 (ADR-154 번들) ──────────────────────────────────────────────
  `[154-AC-3]` empty-target : 스캔 대상 **0 파일 → RED** (`EMPTY_SCAN_TARGET`).
                             ★Story §8.0.8 NG-20 행이 empty 처분을 `RED` 로 명시★
                             하므로 `empty_target()`(INCONCLUSIVE) 대신 RED —
                             non-GREEN floor 보다 **엄격한 방향**이다.
                             경로 오지정 → 0 파일 → GREEN 은 vacuous pass 고전형.
  `[154-AC-4]` unknown-input: 문서 UTF-8 디코드·read 실패 → **fail-closed RED(exit 1)**.
                             조용한 파일 제외 0.
  `[154-AC-5]` trace        : `files_scanned`(numeric) · `k_items_compared`(=9) ·
                             `anchors_checked`(=9) · `topic_mentions` · `weakening` ·
                             `ambiguous`
  `[154-AC-13]` identity_probe: resolved-target echo — K 항목 9 id + 각 topic 패턴 +
                             앵커 target 경로 + 스캔 root/suffix + 스캔 파일 digest.
                             ★채널 = "K-list 9항 정의 + 스캔 경로 집합" 그 자체★.

── 이 스캐너가 보증하지 않는 것 (정직 선언) ──────────────────────────────
  (a) **열거된 topic 정규식 밖 표현은 미검출**이다. K 항목을 이름·용어 없이 우회 서술
      하거나(예: 개념만 풀어 쓴 새 문장), 표/그림 셀에 쪼개 놓거나, 여러 줄에 걸쳐
      성립시키는 완화는 잡지 못한다. 검출 완전성 주장 없음.
  (b) `weaken ∧ uphold` 를 `ambiguous`(INCONCLUSIVE)로 내리는 것은 **판별 불가 신고**
      이지 무죄·유죄 판정이 아니다. 반대로 창 안에 uphold 토큰이 우연히 섞인 진짜
      완화 문면은 RED 가 아니라 INCONCLUSIVE 로 **강도가 낮아진다**(구조적 한계).
  (c) leg-A 는 앵커 **문자열의 존재**만 본다. 문장이 살아있어도 주변 문맥이 뒤집혀
      의미가 무력화되는 경우는 미검출(NG-2 preserve leg 과 동일 한계).
  (d) 앵커는 **repo 내 1 site 씩 pin** 이다. 같은 결정이 다른 파일로 옮겨가면
      (정당한 re-home) leg-A 가 RED 를 낸다 — 그때는 앵커 갱신이 정답이며, 이는
      **의도된 마찰**(무접촉 대상이 움직였다는 사실 자체를 리뷰에 올린다)이다.
  (e) 판정 대상은 **wrapper repo active-doc + 앵커 파일**이다. Story 본문(내부-docs
      repo)·PR 코멘트·대화 로그에서의 재제안은 관측면 밖 — 그 축은 리뷰 lane 소관.
  (f) 자원 안전성: 줄 단위 선형 스캔 · anchored·bounded quantifier 정규식. 이는
      **bounded degradation 선언**이지 "임의 입력 무해(ReDoS-safe)" 단정이 아니다 —
      복잡도 회귀 self-test·wall-clock 벤치마크 미동반 (ADR-168 §결정 16
      honest-ceiling).
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
import check_fanout_subject_prose as fanout  # noqa: E402

# Windows console(cp949) 호환 — 기존 scripts/lib 관례 답습.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-20:AC-9-klist-untouched"

# reason 접두 (테스트·리뷰가 분기 식별에 쓰는 안정 토큰).
R_EMPTY_SCAN = "EMPTY_SCAN_TARGET"
R_UNPARSEABLE = "UNPARSEABLE_DOC"
R_ANCHOR_MISSING = "KLIST_ANCHOR_MISSING"
R_WEAKENED = "KLIST_WEAKENED"
R_AMBIGUOUS = "KLIST_CLASSIFICATION_AMBIGUOUS"

# topic 매치 좌우 창(문자). 창 밖 동사는 미검출 — 위 (a) 정직 선언 참조.
TOPIC_WINDOW = 40

# ── 완화·재제안 행위 토큰 (= 위반 방향) ───────────────────────────────────
# ★행위 동사/명사만★ — 단순 언급(`허용`, `가능` 같은 상태 서술)은 넣지 않는다.
# 넣으면 K 항목을 정확히 설명하는 기존 문장 수십 개가 후보로 들어와 신호가 죽는다.
WEAKEN = re.compile(
    r"재제안|재논의|재검토|완화|해제한다|해제하고|철회|폐지|축소|면제|생략|되살|부활|"
    r"재도입|도입한다|채택한다|승격한다|열어준다|허용한다|허용으로|무효화한다|풀어준다"
)

# ── 기결정 유지 토큰 (= 무침범 방향) ──────────────────────────────────────
UPHOLD = re.compile(
    r"금지|불가|불변|유지|보존|고정|의무|필수|강제|DEFER|위반|미구현|무효|"
    r"재논의 금지|재제안 금지|비협상|무접촉|무손상"
)

# ── ★부정된 완화 토큰★ (= 완화 행위를 **금지하는** 서술) ─────────────────
# `재제안 금지` / `도입 불가` / `완화하지 않는다` 처럼 완화 동사 바로 뒤에 금지어가
# 붙으면 그것은 위반이 아니라 **기결정을 재확인하는 문장**이다. 이 구문을 걸러내지
# 않으면 K-list 를 지키라고 쓴 문장 자체가 K-list 위반으로 잡힌다
# (실측 반례: `review-pl-base.md:634` = "env=1 auto-wake-parent dispatcher 재제안 금지").
_PROHIBITION_TAIL = re.compile(
    r"^[\s*`\"'()\[\]·,:은는를을이가]{0,6}"
    r"(?:금지|불가|않는다|하지 ?않|안 ?함|없다|0\s?건|무효|미허용|아님|아니다)"
)
# 완화 토큰 뒤 최대 몇 문자까지 금지어를 탐색할지 (bounded — 문장 경계 넘김 방지).
NEGATION_TAIL_WINDOW = 14

# ── K-list 9 항 (Story §4.3 D — K-3·K-4 개정 대상 / K-9 재논의 허용 → 제외) ──
K_ITEMS: Tuple[Dict[str, object], ...] = (
    {
        "id": "K-1",
        "summary": "nested TEAMS 금지 (env=1 teammate→teammate spawn) — platform 물리 제약",
        "topic": re.compile(r"nested TEAMS|nested team|teammate\s{0,3}(?:→|->)\s{0,3}teammate"),
        "anchor_path": "docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md",
        "anchor_text": "nested TEAMS (teammate→teammate spawn) 금지 (platform 강제",
    },
    {
        "id": "K-2",
        "summary": "one-team-per-lead",
        "topic": re.compile(r"one-team-per-lead|one team per lead"),
        "anchor_path": "docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md",
        "anchor_text": "one-team-per-lead 강제",
    },
    {
        "id": "K-5",
        "summary": "리뷰 floor = ≥1 independent peer(SoD). self-audit verdict = 무효",
        "topic": re.compile(
            r"independent peer|self-audit verdict|peer floor|리뷰 floor|검증 floor"
        ),
        "anchor_path": "plugins/codeforge-review/templates/review-pl-base.md",
        "anchor_text": "검증 floor = **≥1 independent peer (SoD: implementer ≠ certifier)**",
    },
    {
        "id": "K-6",
        "summary": "spawn-then-blind-wait 금지 / 미도달 = honest INCONCLUSIVE",
        "topic": re.compile(r"spawn-then-blind-wait|blind-wait|blind wait"),
        "anchor_path": "plugins/codeforge-review/templates/review-pl-base.md",
        "anchor_text": "spawn-then-blind-wait 금지",
    },
    {
        "id": "K-7",
        "summary": "env=1 auto-wake-parent dispatcher = DEFER, 재제안 금지",
        "topic": re.compile(r"auto-wake-parent|auto-wake parent|auto wake parent"),
        "anchor_path": "docs/orchestrator-playbook.md",
        "anchor_text": "full auto-wake-parent dispatcher(env=1)는 구현 금지",
    },
    {
        "id": "K-8",
        "summary": "collect blocking 물리강제 = ADR-115 C2 위반 → record-only",
        "topic": re.compile(r"collect[ -]blocking|blocking collect|물리강제"),
        "anchor_path": "docs/inter-plugin-contracts/stop-event-v1.md",
        "anchor_text": "ADR-115 §결정 2 block 금지 binding constraint",
    },
    {
        "id": "K-10",
        "summary": "§10 FIX Ledger = Orchestrator 단독 write",
        # ★단순 `FIX Ledger` 언급이 아니라 **writer 독점 축**만 후보로 잡는다★ —
        # 전자는 231 줄(실측)이라 신호가 죽고, 옆 문장의 동사가 오귀속된다.
        "topic": re.compile(
            r"[Ww]riter monopoly"
            r"|(?:FIX Ledger|§10)[^\n]{0,40}?(?:단독|독점|monopoly)"
            r"|(?:단독|독점|monopoly)[^\n]{0,40}?(?:FIX Ledger|§10)"
        ),
        "anchor_path": "docs/inter-plugin-contracts/fix-event-v1.md",
        "anchor_text": "**Writer monopoly v1**: Orchestrator 단독.",
    },
    {
        "id": "K-11",
        "summary": "신규 check = warning 출생, required 승격 = 3-AND + evidence",
        "topic": re.compile(r"warning[- ]tier 등록|warning 출생|required 승격|3-AND"),
        "anchor_path": "archive/adr/ADR-171-evidence-enforceable-promotion-framework.md",
        "anchor_text": "선언(declaration) → warning(비차단 관측) → enforce(차단) 점진 승격",
    },
    {
        "id": "K-12",
        "summary": "6 sequential 의무 enum close-set (확장 = ADR amendment 의무)",
        "topic": re.compile(r"close-set|6 순차 의무|sequential mandate enum|6 sequential"),
        "anchor_path": "docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md",
        "anchor_text": "### 6 순차 의무 영역 Enum (close-set)",
    },
)

EXPECTED_K_COUNT = 9

CLS_WEAKENING = "weakening"
CLS_AMBIGUOUS = "ambiguous"
CLS_MENTION = "mention"


def _is_negated_weaken(window: str, match: "re.Match") -> bool:
    """완화 토큰 직후에 금지어가 붙어 있으면 `완화 금지` 서술 = 위반 아님."""
    tail = window[match.end() : match.end() + NEGATION_TAIL_WINDOW]
    return bool(_PROHIBITION_TAIL.match(tail))


def classify_window(line: str, start: int, end: int) -> Tuple[str, str]:
    """topic 매치 [start,end) 근방 창을 3-state 로 분류. (classification, window)."""
    lo = max(0, start - TOPIC_WINDOW)
    hi = min(len(line), end + TOPIC_WINDOW)
    window = line[lo:hi]
    live = [m for m in WEAKEN.finditer(window) if not _is_negated_weaken(window, m)]
    if not live:
        # 완화 토큰 부재 ∨ 전건 `…금지` 부정형 → 기결정 재확인 서술.
        return CLS_MENTION, window
    if UPHOLD.search(window):
        return CLS_AMBIGUOUS, window
    return CLS_WEAKENING, window


def scan(repo_root: Path, excluded: Tuple[str, ...] = ()):
    """active-doc 전수 스캔. (findings, scanned_rel_paths).

    `UnparseableDocError` 는 **호출자가 fail-closed 처리** — 여기서 삼키지 않는다.
    """
    findings: List[Dict[str, object]] = []
    scanned: List[str] = []
    for path in fanout.iter_active_docs(repo_root, excluded):
        rel = fanout.normalize_rel(repo_root, path)
        lines = fanout.read_lines(path, rel)
        scanned.append(rel)
        for num, line in enumerate(lines, start=1):
            for item in K_ITEMS:
                match = item["topic"].search(line)  # type: ignore[union-attr]
                if not match:
                    continue
                classification, window = classify_window(line, match.start(), match.end())
                findings.append(
                    {
                        "k_id": item["id"],
                        "file": rel,
                        "line": num,
                        "classification": classification,
                        "window": window.strip()[:160],
                        "text": line.strip()[:200],
                    }
                )
    return findings, scanned


def check_anchors(repo_root: Path) -> Tuple[List[Dict[str, object]], List[str]]:
    """K 항목별 기결정 앵커 존재 판정. (결과, 소실 id 목록).

    `UnparseableDocError` 는 호출자가 fail-closed 처리한다.
    """
    results: List[Dict[str, object]] = []
    missing: List[str] = []
    for item in K_ITEMS:
        rel = str(item["anchor_path"])
        path = Path(repo_root) / rel
        if not path.is_file():
            results.append({"k_id": item["id"], "path": rel, "status": "FILE_MISSING"})
            missing.append("%s(FILE_MISSING)" % (item["id"],))
            continue
        lines = fanout.read_lines(path, rel)
        hits = [num for num, line in enumerate(lines, start=1) if str(item["anchor_text"]) in line]
        if not hits:
            results.append({"k_id": item["id"], "path": rel, "status": "ANCHOR_NOT_FOUND"})
            missing.append("%s(ANCHOR_NOT_FOUND)" % (item["id"],))
        else:
            results.append(
                {"k_id": item["id"], "path": rel, "status": "OK", "line_numbers": hits}
            )
    return results, missing


def evaluate(repo_root: Path, excluded: Tuple[str, ...] = ()) -> gv.GateResult:
    identity_probe = {
        "channel": "K-list 9항 정의 + 스캔 경로 집합",
        "k_item_ids": [str(i["id"]) for i in K_ITEMS],
        "k_item_topics": {str(i["id"]): i["topic"].pattern for i in K_ITEMS},  # type: ignore[union-attr]
        "k_excluded_from_ac9": ["K-3", "K-4", "K-9"],
        "anchor_targets": {str(i["id"]): str(i["anchor_path"]) for i in K_ITEMS},
        "active_doc_roots": list(fanout.ACTIVE_DOC_ROOTS),
        "active_doc_suffixes": list(fanout.ACTIVE_DOC_SUFFIXES),
        "topic_window_chars": TOPIC_WINDOW,
        "repo_root": str(repo_root).replace("\\", "/"),
    }
    trace = {
        "files_scanned": 0,
        "k_items_compared": len(K_ITEMS),
        "anchors_checked": 0,
        "topic_mentions": 0,
        "weakening": 0,
        "ambiguous": 0,
    }

    # ★자기 규격 self-check★ — K 항목 수가 9 가 아니면 규격 자체가 어긋난 것.
    if len(K_ITEMS) != EXPECTED_K_COUNT:  # pragma: no cover - 상수 붕괴 방어
        return gv.unknown_input(
            GATE_ID,
            "K 항목 수 %d ≠ 규격 %d (Story §4.3 D / §8.0.8 NG-20)"
            % (len(K_ITEMS), EXPECTED_K_COUNT),
            trace=trace,
            identity_probe=identity_probe,
        )

    # [154-AC-4] 문서 파싱 불가 → fail-closed RED.
    try:
        findings, scanned = scan(repo_root, excluded)
    except fanout.UnparseableDocError as exc:
        return gv.unknown_input(
            GATE_ID,
            "%s — active-doc 파싱 불가 (fail-closed): %s" % (R_UNPARSEABLE, exc),
            trace=trace,
            identity_probe=identity_probe,
        )

    trace["files_scanned"] = len(scanned)
    identity_probe["scanned_file_digest_sha256"] = fanout.digest_paths(scanned)

    # ★[154-AC-3] empty-target — 0 파일 = RED (명시 분기, 경로 오지정 vacuous pass 차단).★
    if not scanned:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "%s — 스캔 대상 0 파일 (roots=%s under %s). 0 파일에서의 '위반 0' 은 "
            "검사를 한 적이 없다는 뜻이므로 통과시키지 않는다"
            % (R_EMPTY_SCAN, ",".join(fanout.ACTIVE_DOC_ROOTS), identity_probe["repo_root"]),
            trace=trace,
            identity_probe=identity_probe,
        )

    # leg-A — 기결정 앵커 존재 판정.
    try:
        anchor_results, anchor_missing = check_anchors(repo_root)
    except fanout.UnparseableDocError as exc:
        return gv.unknown_input(
            GATE_ID,
            "%s — 앵커 파일 파싱 불가 (fail-closed): %s" % (R_UNPARSEABLE, exc),
            trace=trace,
            identity_probe=identity_probe,
        )

    trace["anchors_checked"] = len(anchor_results)
    trace["anchor_detail"] = anchor_results

    weakening = [f for f in findings if f["classification"] == CLS_WEAKENING]
    ambiguous = [f for f in findings if f["classification"] == CLS_AMBIGUOUS]
    mentions = [f for f in findings if f["classification"] == CLS_MENTION]

    per_item: Dict[str, Dict[str, int]] = {}
    for item in K_ITEMS:
        k_id = str(item["id"])
        per_item[k_id] = {
            "mentions": sum(1 for f in mentions if f["k_id"] == k_id),
            "weakening": sum(1 for f in weakening if f["k_id"] == k_id),
            "ambiguous": sum(1 for f in ambiguous if f["k_id"] == k_id),
        }
    trace["topic_mentions"] = len(mentions)
    trace["weakening"] = len(weakening)
    trace["ambiguous"] = len(ambiguous)
    trace["per_k_item"] = per_item
    identity_probe["candidate_files"] = sorted(
        {str(f["file"]) for f in findings if f["classification"] != CLS_MENTION}
    )

    if anchor_missing:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "%s — 기결정 앵커 소실 (leg-A): %s" % (R_ANCHOR_MISSING, ", ".join(anchor_missing)),
            trace=trace,
            identity_probe=identity_probe,
        )

    if weakening:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "%s — K-list 완화·재제안 문면 %d 건 (leg-W): %s"
            % (R_WEAKENED, len(weakening), _fmt(weakening)),
            trace=trace,
            identity_probe=identity_probe,
        )

    if ambiguous:
        return gv.GateResult(
            GATE_ID,
            gv.INCONCLUSIVE,
            "%s — 완화 토큰과 유지 토큰이 같은 창에 공존해 판별 불가 %d 건 "
            "(자동 통과 금지): %s" % (R_AMBIGUOUS, len(ambiguous), _fmt(ambiguous)),
            trace=trace,
            identity_probe=identity_probe,
        )

    return gv.GateResult(
        GATE_ID,
        gv.PASS,
        "K 항목 %d 항 대조 — 완화 문면 0 건 ∧ 기결정 앵커 %d/%d resolve (스캔 %d 파일, 언급 %d 건)"
        % (len(K_ITEMS), len(anchor_results), len(K_ITEMS), len(scanned), len(mentions)),
        trace=trace,
        identity_probe=identity_probe,
    )


def _fmt(findings: List[Dict[str, object]], limit: int = 12) -> str:
    head = findings[:limit]
    rendered = "; ".join(
        "%s@%s:%s" % (f["k_id"], f["file"], f["line"]) for f in head
    )
    if len(findings) > limit:
        rendered += " (외 %d 건)" % (len(findings) - limit,)
    return rendered


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="NG-20 / AC-9 K-list 무접촉 스캐너")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="스캔 제외 repo-relative 경로 (반복 가능)",
    )
    args = parser.parse_args(argv)

    repo_root = fanout.resolve_repo_root(args.repo_root)
    excluded = tuple(p.replace("\\", "/") for p in args.exclude)
    return gv.emit(evaluate(repo_root, excluded))


if __name__ == "__main__":
    sys.exit(main())
