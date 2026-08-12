#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_fanout_subject_prose.py — NG-2 / AC-5 fan-out 주체 문면 스캐너.

CFP-2926 Story §8.0.8 (1) NG-2. 3-state verdict + execution-trace = `gate_verdict`,
frozen 앵커 해석 = `frozen_anchor` (둘 다 기존 공유 모듈 재사용 — 재구현 0).

── 판정 목표 ──────────────────────────────────────────────────────────────
active-doc 전수에서 **주어가 PL 인** spawn-금지 서술(= "PL 은 sub-agent 를 spawn 할 수
없다" 취지) 이 0 건임을 판정한다. 동시에 **preserve 대상 문면(P-1~P-5)이 살아있음**도
판정한다. 두 leg 을 ★둘 다★ RED 로 낸다 (한쪽만이면 hollow):

  M-A (제거 leg)   : 제거된 PL-축 문면 1개를 되살리면 → RED
  M-B (preserve leg): P-1(`plugins/codeforge-review/CLAUDE.md` "워커는 직접 다른
                      subagent 스폰 불가") 을 삭제하면 → RED

M-B 가 없으면 "모든 spawn-금지 문면을 통째로 지우는" 변경이 M-A 를 통과하고, AC-5 ⓐ 와
AC-9(K-list 무침범) 가 동시에 GREEN 인 채 ADR-139 INV-L4 가 파괴된다.

── 이 스캐너가 보증하는 것 ────────────────────────────────────────────────
  (1) 아래 `SPAWN_PROHIBITION_PREDICATES` 6종 정규식에 매치하는 줄 중, 주어 축이
      `pl` 로 분류된 줄이 0 건임.
  (2) `PRESERVE_ALLOWLIST` 4 site + frozen 앵커 A-1/A-2 가 **내용 앵커**로 resolve 됨.
  (3) 주어 축이 자동 분류 불가(`unknown`)인 줄은 attestation 파일에 수동 분류가
      있어야 하며, 없으면 INCONCLUSIVE (자동 GREEN 흡수 0).

── 이 스캐너가 보증하지 않는 것 (정직 선언) ──────────────────────────────
  (a) "모든 오독 가능 서술"을 잡지 않는다. 열거된 6 predicate 밖의 표현(예: 완전히
      새로 지어낸 우회 문구, 그림/표 셀에 분산된 서술, 영어 전용 신규 표현)은
      **미검출**이다. 검출 완전성 주장 없음.
  (b) 주어 축 분류는 **휴리스틱**이다 — 한국어 주제격 조사(`은`/`는`) 우선 → CamelCase
      에이전트명 → 축 토큰 fallback 순. 한 줄에 주어와 목적어가 함께 나오면 오귀속할 수
      있다(관측된 실례: `PMOAgent 는 ... subagent spawn 아님` 은 좌측 창의 `subagent`
      토큰 때문에 `worker` 로 분류된다 — disposition 은 양쪽 다 preserve 라 판정은
      불변이나 축 라벨은 틀렸다). 축 라벨 자체를 신뢰 근거로 쓰지 말 것.
  (c) attestation 은 **자기신고**다. 신고 내용의 진위는 기계 검사 불가 — 리뷰 판정 축.
      단 `pl` 축 site 를 `preserve` 로 신고하는 whitelist 남용은 기계 거부한다
      (`attestation_cannot_whitelist_pl_axis`).
  (d) preserve leg 은 **앵커 문자열의 존재**만 본다. 문장이 살아있어도 주변 문맥이
      뒤집혀 의미가 무력화되는 경우는 미검출.
  (e) 자원 안전성: 줄 단위 선형 스캔이며 정규식은 anchored·bounded quantifier 다.
      이는 **bounded degradation 선언**이지 "임의 입력 무해(ReDoS-safe)" 단정이 아니다
      — 복잡도 회귀 self-test·wall-clock 벤치마크 미동반 (ADR-168 §결정 16 honest-ceiling).

── 사이드 역할 (형제 게이트 재사용 진입점) ───────────────────────────────
본 모듈은 active-doc 집합 순회 primitive(`iter_active_docs` / `read_lines` /
`resolve_repo_root` / `normalize_rel`) 를 노출한다. NG-3(`check_platform_inherent_prose`)
와 NG-20(`check_klist_untouched`) 이 이를 import 해 재사용한다 (중복 구현 0).
"""

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_verdict as gv  # noqa: E402
import frozen_anchor as fa  # noqa: E402

# Windows console(cp949) 호환 — 기존 scripts/lib 관례 답습.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-2:AC-5-fanout-subject-prose"

# ── active-doc 정의 (★archive/** = frozen, 스캔 제외★) ────────────────────
ACTIVE_DOC_ROOTS = ("CLAUDE.md", "docs", "plugins", "templates", "hooks")
ACTIVE_DOC_SUFFIXES = (".md", ".json", ".yaml", ".yml", ".sh", ".sample")

DEFAULT_ATTESTATION_REL = "docs/cfp2926-prose-axis-attestation.yaml"

# ── 축 상수 ───────────────────────────────────────────────────────────────
AXIS_WORKER = "worker"
AXIS_TEAMMATE = "teammate"
AXIS_TEAM = "team"
AXIS_PL = "pl"
AXIS_AGENT_SPECIFIC = "agent_specific"
AXIS_NOT_APPLICABLE = "not_applicable"
AXIS_UNKNOWN = "unknown"

ATTESTABLE_AXES = (
    AXIS_WORKER,
    AXIS_TEAMMATE,
    AXIS_TEAM,
    AXIS_PL,
    AXIS_AGENT_SPECIFIC,
    AXIS_NOT_APPLICABLE,
)
DISPOSITIONS = ("preserve", "remove")

# preserve 로 취급하는 자동 분류 축 (= 위반 아님).
PRESERVE_AXES = (AXIS_WORKER, AXIS_TEAMMATE, AXIS_TEAM)

# ── 후보 predicate (self-spawn family) ────────────────────────────────────
# ★재귀 spawn 금지 · nested team 금지 boilerplate 는 의도적으로 제외★ — 그 축은
# NG-3(platform-inherent) / NG-20(K-list) 관할이고, 여기 넣으면 40+ preserve 줄이
# 전부 후보로 들어와 unknown 폭증(신호 소실)한다.
SPAWN_PROHIBITION_PREDICATES = (
    ("self-spawn", re.compile(r"self[- ]spawn\s*(?:금지|불가)")),
    ("자가-spawn", re.compile(r"자가-?재?spawn\s*(?:금지|불가)")),
    ("스스로-spawn", re.compile(r"스스로\s{0,3}spawn\s{0,3}(?:할 수 없|금지|불가)")),
    ("spawns-workers", re.compile(r"spawns?\s{1,3}workers?")),
    (
        "직접-스폰-불가",
        re.compile(
            r"직접\s{0,3}(?:다른\s{0,3})?"
            r"(?:sub-?agent|subagent|서브에이전트)?\s{0,3}"
            r"(?:스폰|spawn)\s{0,3}(?:불가|금지)"
        ),
    ),
    ("teammate-spawn-불가", re.compile(r"teammate\s{0,3}(?:→|->)\s{0,3}teammate\s{0,3}spawn\s{0,3}불가")),
)

# 주어 추출 좌측 창 (문자). 창 밖 주어는 미검출 — 위 (b) 정직 선언 참조.
SUBJECT_WINDOW = 45

# markdown 강조·따옴표·괄호 등 주어 뒤에 붙는 장식 문자 (우측에서 벗겨낸다).
_DECORATION_TRAILING = "*`\"'“”‘’()[]{}<> \t"

# 한국어 주제격 조사로 표시된 주어. 첫 매치를 문법 주어로 채택.
_TOPIC_SUBJECT = re.compile(r"([\w가-힣·\-]{1,32})\s{0,2}(?:은|는)\s")
# CamelCase 에이전트명 (…Agent / …PL). 좌측 창 끝에 붙은 것을 채택.
_CAMEL_AGENT = re.compile(r"([A-Z][A-Za-z0-9]{0,40}(?:Agent|PL))\s*$")
# 좌측 창 끝의 단어 토큰. 구분자(`(`, `·`, `—` 등)를 넘어 마지막 낱말만 집는다
# — `유지(lane` 같은 붙임 형태에서 주어 `lane` 을 놓치지 않기 위함.
_TAIL_TOKEN = re.compile(r"([A-Za-z가-힣][\w가-힣\-]{0,31})\s*$")

_PL_SUBJECT_TOKENS = ("lane-pl", "lane pl", "pl", "lane", "관리자 에이전트")
_WORKER_TOKENS = ("워커", "worker", "서브에이전트", "sub-agent", "subagent")
_TEAMMATE_TOKENS = ("teammate",)
_TEAM_TOKENS = ("team",)

# ── preserve allow-list (스캐너 1급 입력 — ★내용 앵커, 줄번호 금지★) ──────
PRESERVE_ALLOWLIST = (
    {
        "id": "P-1",
        "path": "plugins/codeforge-review/CLAUDE.md",
        "anchor": "워커는 **직접 다른 subagent 스폰 불가**",
        "axis": AXIS_WORKER,
        "note": "canonical SSOT — ADR-139 INV-L4 가 인용하는 원본",
    },
    {
        "id": "P-2",
        "path": "archive/adr/ADR-139-background-wait-liveness-gate.md",
        "anchor": "INV-L4 (게이트 소유 = Orchestrator/lead 고정)",
        "axis": AXIS_WORKER,
        "note": "worker 축 + 게이트 소유 불변식",
    },
    {
        "id": "P-4",
        "path": "archive/adr/ADR-170-orchestrator-subagent-default-inline-whitelist.md",
        "anchor": "teammate → teammate spawn 불가 (lead 고정)",
        "axis": AXIS_TEAMMATE,
        "note": "ADR-170 §결정 19 — teammate 축",
    },
    {
        "id": "P-5",
        "path": "docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md",
        "anchor": "nested TEAMS (teammate→teammate spawn) 금지 (platform 강제",
        "axis": AXIS_TEAM,
        "note": "K-1 nested TEAMS 금지 = platform 강제",
    },
)
# P-3 = frozen 앵커 A-1(ADR-044) / A-2(ADR-064) — frozen_anchor 위임.
PRESERVE_FROZEN_ANCHOR_IDS = ("A-1", "A-2")


class UnparseableDocError(Exception):
    """[154-AC-4] 문서 파싱 불가 — fail-closed 로 사상하기 위한 예외."""

    def __init__(self, rel_path: str, detail: str) -> None:
        super().__init__("%s: %s" % (rel_path, detail))
        self.rel_path = rel_path
        self.detail = detail


# ── 공용 primitive (형제 게이트가 import 해 재사용) ────────────────────────
def resolve_repo_root(explicit: Optional[str] = None) -> Path:
    """--repo-root 우선, 없으면 scripts/lib/<this>.py 기준 2 단계 상위."""
    if explicit:
        return Path(explicit).resolve()
    return Path(os.path.abspath(__file__)).parents[2]


def normalize_rel(repo_root: Path, path: Path) -> str:
    """repo-relative posix 경로 (OS separator 비의존)."""
    try:
        rel = path.resolve().relative_to(Path(repo_root).resolve())
    except ValueError:
        rel = path
    return str(rel).replace("\\", "/")


def read_lines(path: Path, rel_path: str) -> List[str]:
    """UTF-8 strict 읽기. ★errors='replace' 금지★ — 깨진 입력을 조용히 통과시키지 않는다."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise UnparseableDocError(rel_path, "read 실패: %s" % (exc,))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UnparseableDocError(rel_path, "UTF-8 디코드 실패: %s" % (exc,))
    return text.splitlines()


def iter_active_docs(repo_root: Path, excluded: Tuple[str, ...] = ()) -> List[Path]:
    """active-doc 집합 순회. archive/** 는 root 목록에 없으므로 구조적으로 제외.

    `excluded` = repo-relative posix 경로 집합. 자기참조 오염 차단용 —
    attestation 파일은 자기가 분류하는 문면을 verbatim 인용하므로 스캔하면
    자기 인용이 새 후보로 잡혀 unknown 이 무한 증식한다.
    """
    excluded_set = set(excluded)
    found: List[Path] = []
    for root_name in ACTIVE_DOC_ROOTS:
        target = Path(repo_root) / root_name
        if target.is_file():
            if target.suffix in ACTIVE_DOC_SUFFIXES:
                found.append(target)
            continue
        if not target.is_dir():
            continue
        for path in target.rglob("*"):
            if path.is_file() and path.suffix in ACTIVE_DOC_SUFFIXES:
                found.append(path)
    return sorted(
        p for p in set(found) if normalize_rel(Path(repo_root), p) not in excluded_set
    )


def digest_paths(rel_paths: List[str]) -> str:
    """resolved-target echo 용 안정 digest ([154-AC-13] identity_probe)."""
    joined = "\n".join(sorted(rel_paths))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


# ── 주어 축 분류 ──────────────────────────────────────────────────────────
def classify_axis(left_context: str) -> str:
    """predicate 좌측 창에서 주어 토큰을 추출해 축을 분류한다.

    우선순위: 한국어 주제격 조사 주어 → CamelCase 에이전트명 → 축 토큰 fallback.
    분류 불가는 ★자동 preserve 로 흡수하지 않고★ `unknown` 을 반환한다.
    """
    stripped = left_context.rstrip(_DECORATION_TRAILING)

    topic = _TOPIC_SUBJECT.search(left_context)
    if topic:
        axis = _axis_of_token(topic.group(1))
        if axis != AXIS_UNKNOWN:
            return axis

    camel = _CAMEL_AGENT.search(stripped)
    if camel:
        return AXIS_AGENT_SPECIFIC

    tail_match = _TAIL_TOKEN.search(stripped)
    if tail_match:
        axis = _axis_of_token(tail_match.group(1))
        if axis != AXIS_UNKNOWN:
            return axis

    lowered = left_context.lower()
    if any(tok in lowered for tok in _WORKER_TOKENS):
        return AXIS_WORKER
    if any(tok in lowered for tok in _TEAMMATE_TOKENS):
        return AXIS_TEAMMATE
    if any(tok in lowered for tok in _TEAM_TOKENS):
        return AXIS_TEAM
    return AXIS_UNKNOWN


def _axis_of_token(token: str) -> str:
    """단일 주어 토큰 → 축. bare `PL` 과 CamelCase `ArchitectPL` 을 구별한다."""
    cleaned = token.strip(_DECORATION_TRAILING + "·,.")
    if not cleaned:
        return AXIS_UNKNOWN
    if _CAMEL_AGENT.match(cleaned):
        return AXIS_AGENT_SPECIFIC
    lowered = cleaned.lower()
    if lowered in _PL_SUBJECT_TOKENS:
        return AXIS_PL
    if lowered in _WORKER_TOKENS:
        return AXIS_WORKER
    if lowered in _TEAMMATE_TOKENS:
        return AXIS_TEAMMATE
    if lowered in _TEAM_TOKENS:
        return AXIS_TEAM
    return AXIS_UNKNOWN


# ── attestation 로드 ──────────────────────────────────────────────────────
def load_attestations(path: Path, rel_path: str) -> List[Dict[str, str]]:
    """attestation yaml 로드 + 스키마 검사. 위반은 전부 UnparseableDocError(fail-closed)."""
    try:
        import yaml  # 지연 import — 파일 부재 경로에서는 의존 자체가 불필요.
    except ImportError as exc:  # pragma: no cover - 환경 의존
        raise UnparseableDocError(rel_path, "PyYAML 미설치: %s" % (exc,))

    raw = read_lines(path, rel_path)
    try:
        doc = yaml.safe_load("\n".join(raw))
    except Exception as exc:
        raise UnparseableDocError(rel_path, "YAML 파싱 실패: %s" % (exc,))

    if not isinstance(doc, dict):
        raise UnparseableDocError(rel_path, "최상위가 mapping 아님")
    entries = doc.get("attestations")
    if entries is None:
        entries = []
    if not isinstance(entries, list):
        raise UnparseableDocError(rel_path, "attestations 가 list 아님")

    out: List[Dict[str, str]] = []
    for index, entry in enumerate(entries):
        where = "attestations[%d]" % (index,)
        if not isinstance(entry, dict):
            raise UnparseableDocError(rel_path, "%s 가 mapping 아님" % (where,))
        for field in ("file", "anchor", "axis", "disposition", "rationale"):
            if field not in entry:
                raise UnparseableDocError(rel_path, "%s 필수 필드 누락: %s" % (where, field))
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise UnparseableDocError(rel_path, "%s.%s 가 비어있음" % (where, field))
        if entry["axis"] not in ATTESTABLE_AXES:
            raise UnparseableDocError(
                rel_path, "%s.axis 값 공간 밖: %r" % (where, entry["axis"])
            )
        if entry["disposition"] not in DISPOSITIONS:
            raise UnparseableDocError(
                rel_path, "%s.disposition 값 공간 밖: %r" % (where, entry["disposition"])
            )
        out.append(
            {
                "file": entry["file"].replace("\\", "/"),
                "anchor": entry["anchor"],
                "axis": entry["axis"],
                "disposition": entry["disposition"],
                "rationale": entry["rationale"],
            }
        )
    return out


def match_attestation(
    attestations: List[Dict[str, str]], rel_path: str, line: str
) -> Optional[Dict[str, str]]:
    """(file, anchor 부분문자열) 로 매칭. ★줄번호 미사용★."""
    for entry in attestations:
        if entry["file"] == rel_path and entry["anchor"] in line:
            return entry
    return None


# ── preserve leg ──────────────────────────────────────────────────────────
def check_preserve(repo_root: Path) -> Tuple[List[Dict[str, object]], List[str]]:
    """PRESERVE_ALLOWLIST + frozen 앵커 A-1/A-2 존재 판정. (결과, 소실 id 목록)."""
    results: List[Dict[str, object]] = []
    missing: List[str] = []

    for entry in PRESERVE_ALLOWLIST:
        path = Path(repo_root) / entry["path"]
        if not path.is_file():
            results.append({"id": entry["id"], "path": entry["path"], "status": "FILE_MISSING"})
            missing.append(entry["id"])
            continue
        try:
            lines = read_lines(path, entry["path"])
        except UnparseableDocError as exc:
            results.append(
                {"id": entry["id"], "path": entry["path"], "status": "UNPARSEABLE", "detail": exc.detail}
            )
            missing.append(entry["id"])
            continue
        hits = [num for num, line in enumerate(lines, start=1) if entry["anchor"] in line]
        if not hits:
            results.append({"id": entry["id"], "path": entry["path"], "status": "ANCHOR_NOT_FOUND"})
            missing.append(entry["id"])
        else:
            results.append(
                {
                    "id": entry["id"],
                    "path": entry["path"],
                    "status": "OK",
                    "line_numbers": hits,
                    "axis": entry["axis"],
                }
            )

    for anchor_id in PRESERVE_FROZEN_ANCHOR_IDS:
        resolution = fa.verify_anchor(repo_root, anchor_id)
        entry_path = fa.REGISTERED_ANCHORS[anchor_id]["path"]
        results.append(
            {
                "id": "P-3/%s" % (anchor_id,),
                "path": entry_path,
                "status": resolution.status,
                "line_numbers": resolution.line_numbers,
            }
        )
        if resolution.status != fa.ANCHOR_OK:
            missing.append("P-3/%s" % (anchor_id,))

    return results, missing


# ── 스캔 ──────────────────────────────────────────────────────────────────
def scan(
    repo_root: Path,
    attestations: List[Dict[str, str]],
    excluded: Tuple[str, ...] = (),
):
    """active-doc 전수 스캔. (findings, scanned_rel_paths) 반환."""
    findings: List[Dict[str, object]] = []
    scanned: List[str] = []
    for path in iter_active_docs(repo_root, excluded):
        rel = normalize_rel(repo_root, path)
        lines = read_lines(path, rel)  # UnparseableDocError 는 호출자가 fail-closed 처리
        scanned.append(rel)
        for num, line in enumerate(lines, start=1):
            for pred_name, pattern in SPAWN_PROHIBITION_PREDICATES:
                match = pattern.search(line)
                if not match:
                    continue
                left = line[max(0, match.start() - SUBJECT_WINDOW) : match.start()]
                auto_axis = classify_axis(left)
                attested = match_attestation(attestations, rel, line)
                findings.append(
                    {
                        "file": rel,
                        "line": num,
                        "predicate": pred_name,
                        "auto_axis": auto_axis,
                        "attested": attested,
                        "text": line.strip()[:200],
                    }
                )
                break  # 한 줄 1 finding — predicate 중복 매치로 이중 계수하지 않는다.
    return findings, scanned


def _effective(finding: Dict[str, object]) -> Tuple[str, str, bool]:
    """(축, disposition, 자동축-오버라이드 여부)."""
    auto_axis = str(finding["auto_axis"])
    attested = finding["attested"]
    if attested is None:
        disposition = "remove" if auto_axis == AXIS_PL else "preserve"
        return auto_axis, disposition, False
    axis = str(attested["axis"])  # type: ignore[index]
    disposition = str(attested["disposition"])  # type: ignore[index]
    overridden = auto_axis != AXIS_UNKNOWN and axis != auto_axis
    return axis, disposition, overridden


def evaluate(repo_root: Path, attestation_rel: str) -> gv.GateResult:
    attestation_path = Path(repo_root) / attestation_rel
    identity_probe = {
        "channel": "active-doc 집합",
        "active_doc_roots": list(ACTIVE_DOC_ROOTS),
        "active_doc_suffixes": list(ACTIVE_DOC_SUFFIXES),
        "frozen_excluded": ["archive/**"],
        "attestation_path": attestation_rel,
        "repo_root": str(repo_root).replace("\\", "/"),
    }

    # [154-AC-4] unknown-input → fail-closed RED.
    attestations: List[Dict[str, str]] = []
    if attestation_path.is_file():
        try:
            attestations = load_attestations(attestation_path, attestation_rel)
        except UnparseableDocError as exc:
            return gv.unknown_input(
                GATE_ID,
                "attestation 파싱 불가 (fail-closed): %s" % (exc,),
                trace={"attestation_path": attestation_rel},
                identity_probe=identity_probe,
            )
    identity_probe["attestation_present"] = attestation_path.is_file()

    # 자기참조 오염 차단 — attestation 파일은 자기가 분류하는 문면을 verbatim 인용한다.
    identity_probe["self_excluded"] = [attestation_rel]
    try:
        findings, scanned = scan(repo_root, attestations, excluded=(attestation_rel,))
    except UnparseableDocError as exc:
        return gv.unknown_input(
            GATE_ID,
            "active-doc 파싱 불가 (fail-closed): %s" % (exc,),
            trace={"unparseable_file": exc.rel_path},
            identity_probe=identity_probe,
        )

    identity_probe["scanned_file_digest_sha256"] = digest_paths(scanned)
    identity_probe["candidate_files"] = sorted({str(f["file"]) for f in findings})

    axis_counts: Dict[str, int] = {}
    violations: List[Dict[str, object]] = []
    unknown_unattested: List[Dict[str, object]] = []
    overrides = 0
    whitelist_abuse: List[Dict[str, object]] = []

    for finding in findings:
        axis, disposition, overridden = _effective(finding)
        axis_counts[axis] = axis_counts.get(axis, 0) + 1
        if overridden:
            overrides += 1
        if (
            finding["attested"] is not None
            and finding["auto_axis"] == AXIS_PL
            and disposition == "preserve"
        ):
            whitelist_abuse.append(finding)
        if axis == AXIS_UNKNOWN and finding["attested"] is None:
            unknown_unattested.append(finding)
            continue
        if disposition == "remove":
            violations.append(finding)

    preserve_results, preserve_missing = check_preserve(repo_root)

    trace = {
        "files_scanned": len(scanned),
        "candidate_lines": len(findings),
        "axis_counts": axis_counts,
        "violations": len(violations),
        "unknown_unattested": len(unknown_unattested),
        "attestations_loaded": len(attestations),
        "attestations_matched": sum(1 for f in findings if f["attested"] is not None),
        "axis_overrides": overrides,
        "preserve_checked": len(preserve_results),
        "preserve_missing": len(preserve_missing),
        "preserve_detail": preserve_results,
    }

    # [154-AC-3] empty-target → non-GREEN (INCONCLUSIVE).
    if not scanned:
        return gv.empty_target(
            GATE_ID,
            "스캔 대상 active-doc 0 파일 — vacuous pass 금지",
            trace=trace,
            identity_probe=identity_probe,
        )

    if whitelist_abuse:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "attestation_cannot_whitelist_pl_axis — pl 축 site 를 preserve 로 신고: %s"
            % (_fmt(whitelist_abuse),),
            trace=trace,
            identity_probe=identity_probe,
        )

    # M-B (preserve leg) — allow-list 문면 소실 검출.
    if preserve_missing:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "preserve allow-list 문면 소실 (M-B leg): %s" % (", ".join(preserve_missing),),
            trace=trace,
            identity_probe=identity_probe,
        )

    # M-A (제거 leg) — PL 축 문면 잔존 검출.
    if violations:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "PL 축 spawn-금지 문면 %d 건 잔존 (M-A leg): %s"
            % (len(violations), _fmt(violations)),
            trace=trace,
            identity_probe=identity_probe,
        )

    if unknown_unattested:
        return gv.GateResult(
            GATE_ID,
            gv.INCONCLUSIVE,
            "축 불명 %d 건 — attestation 미등재 (자동 제거·자동 통과 둘 다 금지): %s"
            % (len(unknown_unattested), _fmt(unknown_unattested)),
            trace=trace,
            identity_probe=identity_probe,
        )

    return gv.GateResult(
        GATE_ID,
        gv.PASS,
        "PL 축 문면 0 건 ∧ preserve allow-list %d site 전건 resolve" % (len(preserve_results),),
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
    parser = argparse.ArgumentParser(description="NG-2 / AC-5 fan-out 주체 문면 스캐너")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--attestation", default=DEFAULT_ATTESTATION_REL)
    args = parser.parse_args(argv)

    repo_root = resolve_repo_root(args.repo_root)
    result = evaluate(repo_root, args.attestation.replace("\\", "/"))
    return gv.emit(result)


if __name__ == "__main__":
    sys.exit(main())
