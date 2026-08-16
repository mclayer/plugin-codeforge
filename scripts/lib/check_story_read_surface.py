#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2986 / ADR-180 — Story 읽기면 게이트 엔진 (SSOT)
# ADR-061 §결정 1 — Python entry-point + thin bash wrapper (scripts/check-story-read-surface.sh)
#
# 무엇을 하는가
#   parent Story 와 그 자식 파일 사이의 구조 불변식(INV-S1/S2/S3/S6 + 앵커 3속성)을 검사하고,
#   lane 진입당 실읽기 바이트(read_cost)를 비차단 신호로 방출한다.
#
# 판정 합성 (ADR-180 §결정 7 — 효과 분리)
#   크기 축("너무 큰가")            = 비차단 SIGNAL  → rc 무영향 (ADR-058 거부 선례 회피, AC-15)
#   정보 손실 축("정보를 잃었는가")  = fail-closed    → rc=1 (EXIT_FAIL)
#   판정 불가(커버리지 미달/deferred/before-ref 부재) = rc=3 (EXIT_UNDETERMINED)
#   ★ UNDETERMINED 를 GREEN 과 같은 rc 로 뭉개지 않는다 (CP §11.5 / M-REGISTRY).
#
# 매체 규약 (CP §4.2.2a)
#   코퍼스 본문은 `git archive` 추출물(LF 고정)만 사용한다 — 작업트리 직접 스캔 금지.
#   작업트리에서 읽는 것은 게이트 자신의 선언 파일(baseline / registry)뿐이다.
#
# 정직 상한 (ADR-180 §결정 1)
#   read_cost 는 **선언된** 읽기 비용이다. `Read` 도구에 섹션 주소지정·집행면이 없으므로
#   선언과 실제 agent 거동의 일치는 기계 검증 불가 — attested, not verified.
#   "실제 읽기량을 잰다" 고 주장하지 않는다.
#
# 상세 계약: docs/story-read-surface-baseline.yaml / docs/story-read-declaration-registry.yaml
#            archive/adr/ADR-180-story-growth-axis-externalization.md
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass, asdict
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# Windows cp949 stdout encoding 차단 (ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover - 환경 의존
    print("ERROR check-story-read-surface: pyyaml missing", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# 종료 코드 — 4값 (GREEN / 정보손실 / 사용법 / 판정불가)
# ---------------------------------------------------------------------------
EXIT_PASS = 0
EXIT_FAIL = 1          # fail-closed 불변식 위반 (정보 손실 축)
EXIT_USAGE = 2
EXIT_UNDETERMINED = 3  # 판정 불가 — GREEN 과 절대 뭉개지 않는다

# 코퍼스 접근 매체 선언 (CP §4.2.2a — test_gate_uses_archive_not_worktree 대조 대상)
CORPUS_ACCESS_MEDIUM = "git_archive"

# INV-S1 digest 정규화 규약 — 선언으로 고정한다(숨은 관례 금지).
# 정규화 대상은 **말미 개행뿐**이다. 근거(firsthand 실측, internal-docs 7d075514 → a1888a93):
# 부모 Story 는 trailing newline 이 없고 자식 파일은 POSIX EOF 관행상 있어 순수 이동이 정확히
# 1 B 어긋난다 — 이 1 B 를 흡수하지 않으면 모든 정상 분할이 false RED(born-broken)다.
# 중간 공백·들여쓰기·개행·순서는 정규화하지 않는다 — 정규화 폭을 넓히면 실제 정보 손실을 놓친다.
#   ★ 위 `a1888a93` = internal-docs 브랜치 `feat/CFP-2986-phase2`(PR #3029) 전용 커밋으로
#     main 조상이 아니다 — squash-merge + 브랜치 삭제 시 도달 불가가 된다. **post-merge 에
#     머지 커밋 SHA 로 bump 할 것.** 절차 SSOT = `.github/workflows/story-read-surface-test.yml`
#     헤더 「post-merge 필수 후속」. 같은 줄의 `7d075514` 는 main 조상이라 무조치.
#     (이 SHA 는 인용 provenance 이지 fetch 대상이 아니다 — 미bump 시 손상은 게이트 차단이
#      아니라 근거 재현 불가다.)
INV_S1_CANON = "trailing_newline_only"

# INV-S2 기본 임계 (ADR-180 §결정 4 — Phase 2 에서 코퍼스 분포로 재정)
THETA_MOVE_DEFAULT = 4096

# INV-S2 강등 사유 폐쇄 enum (자유서술 금지 — AC-10)
REASON_CODE_ENUM = ("SECTION_REORG", "AUTHORED_CONSOLIDATION")

# 정량 셀 단위 어휘 — 셀ID 접미사 유도용 (섹션 정체성 아님, AC-19 무저촉)
UNIT_SUFFIX = (("%", "PCT"),)
UNIT_SUFFIX_DEFAULT = "KB"

# baseline domain 필수 키 10종 (CP §11.5 / ADR-180 §결정 4)
DOMAIN_REQUIRED_KEYS = (
    "kind", "file", "section", "span_kind", "span_anchor", "fence_aware",
    "cardinality_basis", "leg3", "expected", "status",
)
SPAN_KIND_ENUM = ("table", "line", "section")
BASIS_ENUM = ("cell_count", "id_occurrence_count")
LEG3_ENUM = ("applicable", "not_applicable")
LEG3_NA_REASON_ENUM = ("NO_VALUE_AXIS",)
STATUS_ENUM = ("enforced", "deferred")
KIND_ENUM = ("quantitative_cells", "ac_id_landing")

SPLIT_ANCHOR_RE = re.compile(r"<!--\s*cfp-split:(begin|end)\b([^>]*?)-->")
SPLIT_MARKER_RE = re.compile(r"<!--\s*cfp-split:")
ATTR_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s>]+)")
AC_ID_RE = re.compile(r"AC-\d+")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
HEADING_ANY_RE = re.compile(r"^(#{1,6})(?:\s|$)")
HEADING_NUM_RE = re.compile(
    r"^(#{1,6})\s+§?\s*([0-9][0-9A-Za-z]*(?:\.[0-9A-Za-z]+)*)\.?(?=\s|$)"
)
# 슬라이서 V1 (CP §4.2.2a 정본) — `§` optional, 마침표 또는 공백
H2_V1_RE = re.compile(r"^##\s*§?\s*(\d+)\s*[.\s]")
H2_BOUNDARY_RE = re.compile(r"^##\s")
SEPARATOR_ROW_RE = re.compile(r"^[\s|:\-]+$")
UNIT_CELL_RE = re.compile(r"^(?P<val>[^A-Za-z%]+?)\s*(?P<unit>[A-Za-z]+|%)$")


class MissingChildError(Exception):
    """분할 앵커가 있는데 자식 본문이 없다 — 조용한 skip 이 아니라 결손이다."""


@dataclass(frozen=True)
class Verdict:
    name: str            # "INV-S1" 등
    fired: bool
    status: str          # "PASS"|"RED"|"SIGNAL"|"NOT_FIRED"|"UNDETERMINED"
    detail: str
    domain: Optional[str] = None
    leg: Optional[str] = None


# ---------------------------------------------------------------------------
# 원시 유틸
# ---------------------------------------------------------------------------
def _lf(text: str) -> str:
    """CRLF/CR → LF 정규화 (매체 규약)."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def git_archive_bytes(repo_root: str, ref: str, path: str) -> bytes:
    """`git archive` 로 LF 고정 추출한다. 작업트리 직접 스캔 금지 (CP §4.2.2a 매체 규약).

    동등 명령: git -C <repo_root> archive <ref> -- <path> | tar -xO
    (파이프 대신 tarfile 로 언팩 — 외부 tar 바이너리 비의존, 매체 동일)
    실패(경로 부재·ref 부재) 시 FileNotFoundError.
    """
    proc = subprocess.run(
        ["git", "-C", repo_root, "archive", ref, "--", path],
        capture_output=True,
    )
    if proc.returncode != 0 or not proc.stdout:
        raise FileNotFoundError(
            "git archive 실패: ref=%s path=%s (%s)"
            % (ref, path, proc.stderr.decode("utf-8", "replace").strip())
        )
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tf:
        for member in tf.getmembers():
            if member.isfile():
                fh = tf.extractfile(member)
                if fh is not None:
                    return fh.read()
    raise FileNotFoundError("git archive 산출물에 파일 없음: ref=%s path=%s" % (ref, path))


def git_archive_text(repo_root: str, ref: str, path: str) -> str:
    return _lf(git_archive_bytes(repo_root, ref, path).decode("utf-8"))


def git_tree_paths(repo_root: str, ref: str) -> List[str]:
    """ref 트리의 전 파일 경로 (스캔 정의역 산출 — O5)."""
    proc = subprocess.run(
        ["git", "-C", repo_root, "ls-tree", "-r", "--name-only", ref],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise FileNotFoundError(
            "git ls-tree 실패: ref=%s (%s)"
            % (ref, proc.stderr.decode("utf-8", "replace").strip())
        )
    return [p for p in proc.stdout.decode("utf-8").split("\n") if p]


def digest(text: str) -> str:
    """sha256 hexdigest, LF 정규화 후."""
    return hashlib.sha256(_lf(text).encode("utf-8")).hexdigest()


def content_canon(text: str) -> str:
    """INV-S1 digest 정규화 (INV_S1_CANON = trailing_newline_only).

    말미 개행 시퀀스만 제거한다 — 부모(EOF 개행 없음) ↔ 자식(POSIX EOF 개행 있음)의
    구조적 1 B 차이를 흡수하기 위함이며, 그 밖의 공백·들여쓰기·줄 순서는 보존한다.
    """
    return _lf(text).rstrip("\n")


def fence_mask(text: str) -> List[bool]:
    """줄별 코드펜스 내부 여부. 펜스 구분줄 자체도 True."""
    mask: List[bool] = []
    fence: Optional[str] = None
    for line in _lf(text).split("\n"):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[:3]
                mask.append(True)
                continue
            mask.append(False)
        else:
            mask.append(True)
            if m and m.group(1)[:3] == fence:
                fence = None
    return mask


def _masked_lines(text: str, fence_aware: bool) -> List[Tuple[str, bool]]:
    lines = _lf(text).split("\n")
    if not fence_aware:
        return [(ln, False) for ln in lines]
    return list(zip(lines, fence_mask(text)))


# ---------------------------------------------------------------------------
# 앵커 (ADR-180 §결정 4 — 명시 ∧ 쌍 ∧ 유일)
# ---------------------------------------------------------------------------
def _raw_anchors(text: str, fence_aware: bool = True) -> List[Tuple[str, Optional[str], Optional[str], int]]:
    """(kind, section, id, lineno) 원시 목록. 오형식은 None 으로 남긴다(무결성 검사가 판정)."""
    out: List[Tuple[str, Optional[str], Optional[str], int]] = []
    for idx, (line, fenced) in enumerate(_masked_lines(text, fence_aware)):
        if fenced:
            continue
        for m in SPLIT_ANCHOR_RE.finditer(line):
            attrs = dict(ATTR_RE.findall(m.group(2)))
            out.append((m.group(1), attrs.get("section"), attrs.get("id"), idx + 1))
    return out


def parse_anchors(text: str, fence_aware: bool = True) -> Set[Tuple[str, str, str]]:
    """{(kind, section, id)}, kind ∈ {"begin","end"}.

    리터럴:
        <!-- cfp-split:begin section=9 id=CFP-2986-S1 -->
        <!-- cfp-split:end id=CFP-2986-S1 -->
    end 앵커는 section= 없이 id= 만 갖는다 (CP §3.4 예시 정본) — section 은 짝 begin 에서 해결한다.
    fence_aware=True 면 코드펜스 안의 앵커는 무시한다.
    """
    raw = _raw_anchors(text, fence_aware)
    begin_section: Dict[str, str] = {}
    for kind, section, aid, _ln in raw:
        if kind == "begin" and aid and section:
            begin_section[aid] = section
    out: Set[Tuple[str, str, str]] = set()
    for kind, section, aid, _ln in raw:
        rid = aid or ""
        if kind == "begin":
            out.add((kind, section or "", rid))
        else:
            out.add((kind, section or begin_section.get(rid, ""), rid))
    return out


def anchor_delta(before: str, after: str) -> Set[Tuple[str, str, str]]:
    """앵커 집합 대칭차."""
    return parse_anchors(before) ^ parse_anchors(after)


def sections_of(delta: Iterable[Tuple[str, str, str]]) -> Set[str]:
    return {section for (_kind, section, _aid) in delta if section}


def has_split_markers(text: str, fence_aware: bool = True) -> bool:
    for line, fenced in _masked_lines(text, fence_aware):
        if fenced:
            continue
        if SPLIT_MARKER_RE.search(line):
            return True
    return False


def check_anchor_integrity(text: str, label: str = "", fence_aware: bool = True) -> List[Verdict]:
    """앵커 3속성 = 명시 ∧ 쌍 ∧ 유일. 미쌍·중복·오형식 = 정보 손실 축 RED."""
    raw = _raw_anchors(text, fence_aware)
    name = "INV-ANCHOR"
    if not raw:
        return [Verdict(name, False, "NOT_FIRED", "split 앵커 없음%s" % (" (%s)" % label if label else ""))]
    verdicts: List[Verdict] = []
    begins: Dict[str, int] = {}
    ends: Dict[str, int] = {}
    for kind, section, aid, lineno in raw:
        if not aid:
            verdicts.append(Verdict(name, True, "RED", "%s:%d 오형식 — id= 누락" % (label, lineno)))
            continue
        if kind == "begin":
            if not section:
                verdicts.append(
                    Verdict(name, True, "RED", "%s:%d 오형식 — begin 에 section= 누락 (id=%s)" % (label, lineno, aid))
                )
            if aid in begins:
                verdicts.append(
                    Verdict(name, True, "RED", "%s:%d 중복 begin id=%s (유일성 위반)" % (label, lineno, aid))
                )
            begins[aid] = lineno
        else:
            if aid in ends:
                verdicts.append(
                    Verdict(name, True, "RED", "%s:%d 중복 end id=%s (유일성 위반)" % (label, lineno, aid))
                )
            ends[aid] = lineno
    for aid, lineno in sorted(begins.items()):
        if aid not in ends:
            verdicts.append(Verdict(name, True, "RED", "%s:%d 미쌍 — begin id=%s 의 end 부재" % (label, lineno, aid)))
    for aid, lineno in sorted(ends.items()):
        if aid not in begins:
            verdicts.append(Verdict(name, True, "RED", "%s:%d 미쌍 — end id=%s 의 begin 부재" % (label, lineno, aid)))
    if not verdicts:
        verdicts.append(
            Verdict(name, True, "PASS", "앵커 3속성 충족 (쌍 %d)%s" % (len(begins), " (%s)" % label if label else ""))
        )
    return verdicts


# ---------------------------------------------------------------------------
# 섹션 슬라이싱
# ---------------------------------------------------------------------------
def _section_spans(text: str, fence_aware: bool = True) -> List[Tuple[Optional[str], int, int]]:
    """(section_key|None, start_line_idx, end_line_idx) 목록. 첫 구간은 preamble(key=None)."""
    pairs = _masked_lines(text, fence_aware)
    starts: List[Tuple[Optional[str], int]] = [(None, 0)]
    for idx, (line, fenced) in enumerate(pairs):
        if fenced:
            continue
        if not H2_BOUNDARY_RE.match(line):
            continue
        m = H2_V1_RE.match(line)
        if m:
            starts.append((m.group(1), idx))
        # 미매칭 h2 = 현 섹션에 계속 귀속 (CP §4.2.2a 슬라이싱 규약)
    spans: List[Tuple[Optional[str], int, int]] = []
    for i, (key, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(pairs)
        spans.append((key, start, end))
    return spans


def split_sections(text: str, fence_aware: bool = True) -> Dict[str, str]:
    """H2 `## N.` 슬라이싱. key = 섹션 번호 문자열 (규칙은 특정 섹션을 하드코딩하지 않는다).

    각 섹션 = 자기 H2 줄부터 다음 H2 직전까지.
    fence_aware=True 면 코드펜스 안 '#' 줄을 heading 으로 오인하지 않는다.
    """
    lines = _lf(text).split("\n")
    out: Dict[str, str] = {}
    for key, start, end in _section_spans(text, fence_aware):
        if key is None:
            continue
        out[key] = "\n".join(lines[start:end])
    return out


def slice_section_by_key(text: str, section_key: str, fence_aware: bool = True) -> Optional[str]:
    """하위절 포함 절 슬라이스 ("4.2.2a" 같은 키). 종결 = 동급 이상 heading."""
    pairs = _masked_lines(text, fence_aware)
    lines = [ln for ln, _f in pairs]
    start = None
    level = 0
    for idx, (line, fenced) in enumerate(pairs):
        if fenced:
            continue
        m = HEADING_NUM_RE.match(line)
        if m and m.group(2) == section_key:
            start = idx
            level = len(m.group(1))
            break
    if start is None:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if pairs[idx][1]:
            continue
        m = HEADING_ANY_RE.match(lines[idx])
        if m and len(m.group(1)) <= level:
            end = idx
            break
    return "\n".join(lines[start:end])


# ---------------------------------------------------------------------------
# stub 제거 · 재조립 (INV-S1 / INV-S3 공용 정의역)
# ---------------------------------------------------------------------------
def strip_stub(section_text: str, fence_aware: bool = True) -> str:
    """앵커 쌍 begin..end 블록(앵커 줄 포함, 사이 stub 본문 포함)을 제거한 나머지."""
    pairs = _masked_lines(section_text, fence_aware)
    drop = [False] * len(pairs)
    open_at: Optional[int] = None
    for idx, (line, fenced) in enumerate(pairs):
        if fenced:
            continue
        for m in SPLIT_ANCHOR_RE.finditer(line):
            if m.group(1) == "begin":
                if open_at is None:
                    open_at = idx
            else:
                if open_at is not None:
                    for k in range(open_at, idx + 1):
                        drop[k] = True
                    open_at = None
                else:
                    drop[idx] = True
    if open_at is not None:  # 미쌍 begin — 앵커 줄만 제거 (무결성 검사가 별도 RED)
        drop[open_at] = True
    return "\n".join(line for idx, (line, _f) in enumerate(pairs) if not drop[idx])


def reassemble(section_text: str, child_texts: Sequence[str]) -> str:
    """strip_stub(section_text) 에 child 본문들을 결합. INV-S1/INV-S3 공용 정의역.

    재조립 정의 (자족 고정 — 3자 재구현이 갈렸던 지점):
      parts = [strip_stub(section_text)] + child_texts
      각 part 의 **말미 개행만** 제거한 뒤 개행 1개로 결합하고, 빈 part 는 버린다.
    이 정의는 stub 이 있던 자리(= 절 말미)에 자식 본문을 원순서로 되돌리며,
    stub 제거로 남는 heading 뒤 잉여 개행과 자식의 EOF 개행이 이중 개행을 만들지 않게 한다.
    """
    parts = [strip_stub(section_text)]
    parts.extend(_lf(t) for t in child_texts)
    kept = [p.rstrip("\n") for p in parts]
    return "\n".join(p for p in kept if p)


def child_body(text: str) -> str:
    """자식 파일 본문 — YAML frontmatter 제거 (운반 메타는 이동 대상 본문이 아니다)."""
    body = _lf(text)
    if body.startswith("---\n"):
        end = body.find("\n---", 3)
        if end != -1:
            nl = body.find("\n", end + 1)
            body = body[nl + 1:] if nl != -1 else ""
    return body


def _frontmatter(text: str) -> dict:
    body = _lf(text)
    if not body.startswith("---\n"):
        return {}
    end = body.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(body[4:end + 1]) or {}
    except Exception:
        return {}


def _frontmatter_field(text: str, key: str):
    return _frontmatter(text).get(key)


def child_carries(text: str) -> List[str]:
    """자식 frontmatter `carries_sections: [N]` 선언 파싱 (슬라이싱 아님).

    이 선언이 곧 자식 자격의 판별자다 — 파일명 형상은 판별자가 아니다.
    """
    raw = _frontmatter(text).get("carries_sections") or []
    if isinstance(raw, (str, int)):
        raw = [raw]
    return [str(x) for x in raw]


def reassemble_document(text: str, children_by_section: Dict[str, List[str]]) -> str:
    """문서 전체 재조립 — 앵커 보유 섹션의 stub 을 자식 본문으로 치환한다.

    앵커 보유인데 자식 미발견 = 조용한 skip 아니라 결손 → MissingChildError.
    """
    lines = _lf(text).split("\n")
    out: List[str] = []
    for key, start, end in _section_spans(text, True):
        chunk = "\n".join(lines[start:end])
        if key is not None and has_split_markers(chunk):
            kids = children_by_section.get(key)
            if not kids:
                raise MissingChildError("§%s 에 split 앵커가 있으나 자식 본문 미발견" % key)
            chunk = reassemble(chunk, kids)
        out.append(chunk)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 정의역 추출 — 정의역별 자족 선언 (R3 P0-1: 전역 단일 규칙은 born-broken)
# ---------------------------------------------------------------------------
def _split_row(line: str) -> List[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split("|")]


def _normalize_label(cell: str) -> str:
    label = cell.replace("**", "").strip()
    return label.replace("§", "S")


def _unit_suffix(part: str) -> Tuple[str, str]:
    """정량 셀 조각 → (접미사, 값문자열). 단위 어휘로만 유도 (섹션 정체성 무관)."""
    token = part.replace("**", "").strip()
    m = UNIT_CELL_RE.match(token)
    if not m:
        return (UNIT_SUFFIX_DEFAULT, token)
    unit = m.group("unit")
    for marker, suffix in UNIT_SUFFIX:
        if unit == marker:
            return (suffix, m.group("val").strip())
    return (unit.upper(), m.group("val").strip())


def _span_lines(section_text: str, domain: dict) -> List[str]:
    fence_aware = bool(domain.get("fence_aware", True))
    pairs = _masked_lines(section_text, fence_aware)
    anchor = re.compile(domain["span_anchor"])
    start = None
    for idx, (line, fenced) in enumerate(pairs):
        if fenced:
            continue
        if anchor.search(line):
            start = idx
            break
    if start is None:
        return []
    span_kind = domain["span_kind"]
    if span_kind == "line":
        return [pairs[start][0]]
    if span_kind == "section":
        return [ln for ln, _f in pairs]
    # table — 앵커 줄부터 연속 '|' 줄
    out: List[str] = []
    for idx in range(start, len(pairs)):
        line = pairs[idx][0]
        if not line.lstrip().startswith("|"):
            break
        out.append(line)
    return out


def extract_domain(domain: dict, text: str):
    """정의역별 자족 선언으로 추출한다 — 전역 단일 규칙 금지 (R3 P0-1).

    절차 (1) fence_aware 로 절 경계 슬라이스 (2) span_anchor 로 시작 줄 확정
         (3) span_kind 로 span 확정 (4) span 안의 전 토큰 추출.
    ★ span 이 좁히는 것이지 사후 필터가 좁히는 게 아니다.

    kind=='quantitative_cells' -> {셀ID: 값문자열}
    kind=='ac_id_landing'      -> {AC-ID: 출현수}
    """
    fence_aware = bool(domain.get("fence_aware", True))
    section = slice_section_by_key(text, str(domain["section"]), fence_aware)
    if section is None:
        return {}
    span = _span_lines(section, domain)
    if not span:
        return {}
    if domain["kind"] == "ac_id_landing":
        counts: Dict[str, int] = {}
        for token in AC_ID_RE.findall("\n".join(span)):
            counts[token] = counts.get(token, 0) + 1
        return counts
    cells: Dict[str, str] = {}
    rows = [_split_row(ln) for ln in span if not SEPARATOR_ROW_RE.match(ln.strip())]
    if len(rows) < 2:
        return {}
    header = [_normalize_label(c) for c in rows[0]]
    for row_idx, row in enumerate(rows[1:]):
        for col, raw_cell in enumerate(row):
            if col >= len(header) or not header[col]:
                continue
            for part in raw_cell.split("<br>"):
                if not part.strip():
                    continue
                suffix, value = _unit_suffix(part)
                key = "%s.%s" % (header[col], suffix)
                if key in cells:
                    key = "%s#%d" % (key, row_idx)
                cells[key] = value
    return cells


# ---------------------------------------------------------------------------
# 불변식
# ---------------------------------------------------------------------------
def check_inv_s1(before_text: str, after_text: str, children: Dict[str, List[str]]) -> List[Verdict]:
    """발화: anchor_delta != ∅.  판정: 섹션별 pure-move digest 보존.

    자식 미발견 = 조용한 skip 아니라 결손(RED).
    """
    name = "INV-S1"
    delta = anchor_delta(before_text, after_text)
    if not delta:
        return [Verdict(name, False, "NOT_FIRED", "anchor_delta = ∅ (분할·역분할 아님)")]
    targets = sections_of(delta)
    if not targets:
        return [Verdict(name, True, "RED", "anchor_delta 에 section 해결 불가 앵커만 존재 (오형식)")]
    before_sections = split_sections(before_text)
    after_sections = split_sections(after_text)
    verdicts: List[Verdict] = []
    for key in sorted(targets):
        b_sec = before_sections.get(key)
        a_sec = after_sections.get(key)
        if b_sec is None or a_sec is None:
            verdicts.append(
                Verdict(name, True, "RED", "§%s 이 before/after 한쪽에 부재 (결손)" % key, domain=key)
            )
            continue
        kids = children.get(key)
        b_has = has_split_markers(b_sec)
        a_has = has_split_markers(a_sec)
        if (b_has or a_has) and not kids:
            verdicts.append(
                Verdict(name, True, "RED", "§%s split 앵커 보유 — 자식 본문 미발견 (결손)" % key, domain=key)
            )
            continue
        b_norm = reassemble(b_sec, kids or []) if b_has else b_sec
        a_norm = reassemble(a_sec, kids or []) if a_has else a_sec
        b_digest = digest(content_canon(b_norm))
        a_digest = digest(content_canon(a_norm))
        if b_digest == a_digest:
            verdicts.append(
                Verdict(name, True, "PASS", "§%s pure-move digest 보존 (%s)" % (key, b_digest[:12]), domain=key)
            )
        else:
            verdicts.append(
                Verdict(
                    name, True, "RED",
                    "§%s pure-move 위반 — digest before=%s after=%s (canon=%s)"
                    % (key, b_digest[:12], a_digest[:12], INV_S1_CANON),
                    domain=key,
                )
            )
    return verdicts


def _section_byte_len(text: str) -> int:
    return len(_lf(text).encode("utf-8"))


def check_inv_s2(before_text: str, after_text: str, theta_move: int,
                 reason_code: Optional[str]) -> List[Verdict]:
    """발화: anchor_delta == ∅ (총량 조건 없음 — R2 P0-A 봉합. θ_total 상수 신설 금지).

    RED ⟺ ∃ i≠j: Δ§i <= -θ_move ∧ Δ§j >= +θ_move
    reason_code ∈ 폐쇄 enum 선언 시 status="SIGNAL" 로 강등(비차단).
    """
    name = "INV-S2"
    if anchor_delta(before_text, after_text):
        return [Verdict(name, False, "NOT_FIRED", "anchor_delta != ∅ (분할 커밋 — INV-S1 반쪽)")]
    before_sections = split_sections(before_text)
    after_sections = split_sections(after_text)
    keys = sorted(set(before_sections) | set(after_sections))
    deltas: Dict[str, int] = {}
    for key in keys:
        b = _section_byte_len(before_sections.get(key, ""))
        a = _section_byte_len(after_sections.get(key, ""))
        deltas[key] = a - b
    donors = sorted(k for k in keys if deltas[k] <= -theta_move)
    takers = sorted(k for k in keys if deltas[k] >= theta_move)
    pairs = [(i, j) for i in donors for j in takers if i != j]
    if not pairs:
        return [
            Verdict(name, True, "PASS",
                    "섹션 간 보상 이동 없음 (θ_move=%d, donors=%d takers=%d)"
                    % (theta_move, len(donors), len(takers)))
        ]
    detail = "섹션 간 보상 이동 후보 %s (θ_move=%d)" % (pairs, theta_move)
    if reason_code in REASON_CODE_ENUM:
        return [Verdict(name, True, "SIGNAL", "%s — reason_code=%s 로 신호 강등(비차단)" % (detail, reason_code))]
    if reason_code:
        return [
            Verdict(name, True, "RED",
                    "%s — reason_code=%s 는 폐쇄 enum %s 밖 (강등 불가)"
                    % (detail, reason_code, list(REASON_CODE_ENUM)))
        ]
    return [Verdict(name, True, "RED", detail)]


def _declared_card(domain: dict) -> int:
    """card 는 expected 매핑에서 유도만 한다 — 별도 정수 선언 금지 (이중 원본 = C-7 의 틈)."""
    expected = domain["expected"] or {}
    if domain["cardinality_basis"] == "cell_count":
        return len(expected)
    return sum(int(v) for v in expected.values())


def _extract_card(domain: dict, extracted) -> int:
    if domain["cardinality_basis"] == "cell_count":
        return len(extracted)
    return sum(int(v) for v in extracted.values())


def check_inv_s3(baseline: dict, resolve_file: Callable[[dict], str]) -> List[Verdict]:
    """발화 조건 없음 — 항상 실행 (R2 P0-B). 분할 커밋 한정 금지.

    status=='deferred' -> UNDETERMINED (GREEN 아님)
    status=='enforced' -> leg1 ∧ leg2 ∧ leg3 (3항 AND)
    """
    name = "INV-S3"
    verdicts: List[Verdict] = []
    for dom_name in sorted(baseline.get("domains", {})):
        domain = baseline["domains"][dom_name]
        if domain.get("status") == "deferred":
            verdicts.append(
                Verdict(name, True, "UNDETERMINED",
                        "정의역 미실체화 (reason_code=%s) — GREEN 아님"
                        % domain.get("reason_code", "UNDECLARED"),
                        domain=dom_name)
            )
            continue
        try:
            text = resolve_file(domain)
        except MissingChildError as exc:
            verdicts.append(Verdict(name, True, "RED", "재조립 결손: %s" % exc, domain=dom_name))
            continue
        except FileNotFoundError as exc:
            verdicts.append(Verdict(name, True, "RED", "정의역 파일 해결 실패: %s" % exc, domain=dom_name))
            continue
        extracted = extract_domain(domain, text)
        expected = domain["expected"] or {}
        if not extracted:
            verdicts.append(
                Verdict(name, True, "RED",
                        "추출 0건 (절 %s / span %s) — 조용한 skip 아닌 결손"
                        % (domain["section"], domain["span_kind"]),
                        domain=dom_name, leg="leg1")
            )
            continue
        # leg1 — 집합 동일성
        missing = sorted(set(expected) - set(extracted))
        extra = sorted(set(extracted) - set(expected))
        if missing or extra:
            verdicts.append(
                Verdict(name, True, "RED",
                        "집합 불일치 missing=%s extra=%s" % (missing, extra),
                        domain=dom_name, leg="leg1")
            )
        else:
            verdicts.append(
                Verdict(name, True, "PASS", "집합 동일 (%d)" % len(expected), domain=dom_name, leg="leg1")
            )
        # leg2 — 절대 cardinality (basis = 정의역이 선언, card 는 expected 에서 유도)
        want = _declared_card(domain)
        got = _extract_card(domain, extracted)
        if want == got:
            verdicts.append(
                Verdict(name, True, "PASS", "cardinality %d (basis=%s)" % (got, domain["cardinality_basis"]),
                        domain=dom_name, leg="leg2")
            )
        else:
            verdicts.append(
                Verdict(name, True, "RED",
                        "cardinality 불일치 expected=%d extracted=%d (basis=%s)"
                        % (want, got, domain["cardinality_basis"]),
                        domain=dom_name, leg="leg2")
            )
        # leg3 — per-cell 값 동일성 (적용성은 정의역이 선언 — 조용한 skip 금지)
        if domain["leg3"] == "applicable":
            bad = [
                "%s(expected=%s actual=%s)" % (k, expected[k], extracted.get(k))
                for k in sorted(expected)
                if str(extracted.get(k)) != str(expected[k])
            ]
            if bad:
                verdicts.append(
                    Verdict(name, True, "RED", "값 오염 %s" % bad, domain=dom_name, leg="leg3")
                )
            else:
                verdicts.append(
                    Verdict(name, True, "PASS", "per-cell 값 동일 (%d)" % len(expected), domain=dom_name, leg="leg3")
                )
        else:
            reason = domain.get("leg3_na_reason")
            if reason in LEG3_NA_REASON_ENUM:
                verdicts.append(
                    Verdict(name, True, "PASS", "leg3 not_applicable (%s)" % reason, domain=dom_name, leg="leg3")
                )
            else:
                verdicts.append(
                    Verdict(name, True, "RED",
                            "leg3 미실행인데 leg3_na_reason 미선언/enum 밖 (%r) — 통과 아닌 결손" % reason,
                            domain=dom_name, leg="leg3")
                )
    return verdicts


def check_inv_s6(children: dict) -> List[Verdict]:
    """자식 안 split 마커 부재 (깊이 <= 1 — AC-12)."""
    name = "INV-S6"
    if not children:
        return [Verdict(name, False, "NOT_FIRED", "자식 파일 0건")]
    verdicts: List[Verdict] = []
    for path in sorted(children):
        if has_split_markers(children[path]):
            verdicts.append(Verdict(name, True, "RED", "%s 안에 split 마커 존재 (깊이 > 1)" % path, domain=path))
        else:
            verdicts.append(Verdict(name, True, "PASS", "%s 깊이 <= 1" % path, domain=path))
    return verdicts


# ---------------------------------------------------------------------------
# 목적함수 (ADR-180 §결정 1)
# ---------------------------------------------------------------------------
def _declared_sections(entry) -> Optional[List[str]]:
    if entry is None:
        return None
    if isinstance(entry, dict):
        raw = entry.get("declares")
    else:
        raw = entry
    if raw is None:
        return None
    return [str(x) for x in raw]


def read_cost(parent_bytes: int, children: Dict[str, int],
              readers: List[str], registry: dict) -> int:
    """read_cost = Σ_r [ bytes(parent) + Σ_{c: opens(r,c)} bytes(c) ]

    opens(r,c) ⟺ r 이 registry 미등재(보수 default — 전 자식 계상)
                 ∨ declares(r) ∩ carries(c) != ∅
    ★ 파일 단위. 줄수/heading수/섹션수/자식포함총합 채택 금지 (AC-21).
    """
    readers_reg = (registry or {}).get("readers", {}) or {}
    carries_reg = (registry or {}).get("carries", {}) or {}
    total = 0
    for reader in readers:
        total += parent_bytes
        declares = _declared_sections(readers_reg.get(reader))
        for child, size in children.items():
            if declares is None:
                opens = True                       # 미등재 = 보수 default
            else:
                carried = carries_reg.get(child)
                if carried is None:
                    opens = True                   # carries 미선언 = 보수 default
                else:
                    opens = bool(set(declares) & {str(x) for x in carried})
            if opens:
                total += size
    return total


def coverage(readers: List[str], registry: dict) -> float:
    """registry 등재 reader 비율. 분모 = 폐쇄 roster (baseline 선언)."""
    if not readers:
        return 0.0
    readers_reg = (registry or {}).get("readers", {}) or {}
    hit = sum(1 for r in readers if r in readers_reg)
    return hit / float(len(readers))


# ---------------------------------------------------------------------------
# baseline / registry
# ---------------------------------------------------------------------------
DIGEST_LINE_RE = re.compile(r"^(content_digest:).*$", re.MULTILINE)


def baseline_self_digest(text: str) -> str:
    """content_digest 필드값을 비운 정규형의 sha256 (수기 편집 방지)."""
    return digest(DIGEST_LINE_RE.sub(r"\1", _lf(text)))


def load_baseline(path: str) -> dict:
    """baseline artifact 로드 + fail-closed 스키마 검증.

    필수 키 10종 = kind,file,section,span_kind,span_anchor,fence_aware,
                  cardinality_basis,leg3,expected,status
    하나라도 누락 = 배선 금지(ValueError). 단 status=='deferred' 정의역은 carve-out.
    content_digest 불일치 = 비정상 종료.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("baseline 파싱 실패: %s" % path)
    for key in ("baseline_tree_sha", "baseline_media", "content_digest", "frozen_at",
                "default_ceiling", "coverage_floor", "reader_roster", "file_map",
                "carriers", "expected_scan_set", "declared_scan_count", "scan_domain", "domains"):
        if key not in data:
            raise ValueError("baseline 필수 최상위 키 누락: %s" % key)
    declared_digest = str(data["content_digest"])
    actual_digest = baseline_self_digest(raw)
    if declared_digest != actual_digest:
        raise ValueError(
            "baseline content_digest 불일치 (수기 편집 의심): declared=%s actual=%s"
            % (declared_digest, actual_digest)
        )
    if len(data["expected_scan_set"]) != int(data["declared_scan_count"]):
        raise ValueError(
            "O5 (c) 위반 — |expected_scan_set|=%d != declared_scan_count=%d"
            % (len(data["expected_scan_set"]), int(data["declared_scan_count"]))
        )
    for name, domain in (data["domains"] or {}).items():
        if not isinstance(domain, dict):
            raise ValueError("정의역 %s 선언 형식 오류" % name)
        status = domain.get("status")
        if status not in STATUS_ENUM:
            raise ValueError("정의역 %s status 미선언/enum 밖: %r" % (name, status))
        if status == "deferred":
            # carve-out — 9키 결여 허용, UNDETERMINED 방출 (CP §11.5)
            if not domain.get("reason_code"):
                raise ValueError("정의역 %s deferred 인데 reason_code 미선언" % name)
            continue
        missing = [k for k in DOMAIN_REQUIRED_KEYS if k not in domain]
        if missing:
            raise ValueError("정의역 %s 필수 키 누락 %s — 배선 금지(fail-closed)" % (name, missing))
        if domain["kind"] not in KIND_ENUM:
            raise ValueError("정의역 %s kind enum 밖: %r" % (name, domain["kind"]))
        if domain["span_kind"] not in SPAN_KIND_ENUM:
            raise ValueError("정의역 %s span_kind enum 밖: %r" % (name, domain["span_kind"]))
        if domain["cardinality_basis"] not in BASIS_ENUM:
            raise ValueError("정의역 %s cardinality_basis enum 밖: %r" % (name, domain["cardinality_basis"]))
        if domain["leg3"] not in LEG3_ENUM:
            raise ValueError("정의역 %s leg3 enum 밖: %r" % (name, domain["leg3"]))
        if domain["leg3"] == "not_applicable" and domain.get("leg3_na_reason") not in LEG3_NA_REASON_ENUM:
            raise ValueError("정의역 %s leg3_na_reason 미선언/enum 밖" % name)
        if not isinstance(domain["expected"], dict) or not domain["expected"]:
            raise ValueError("정의역 %s expected 매핑 부재 — card 유도 불가" % name)
        if str(domain["file"]) not in (data["file_map"] or {}):
            raise ValueError("정의역 %s file=%r 이 file_map 미등재" % (name, domain["file"]))
        try:
            re.compile(domain["span_anchor"])
        except re.error as exc:
            raise ValueError("정의역 %s span_anchor 정규식 오류: %s" % (name, exc))
    return data


def load_registry(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh.read())
    if not isinstance(data, dict):
        raise ValueError("registry 파싱 실패: %s" % path)
    readers = data.get("readers")
    if not isinstance(readers, dict) or not readers:
        raise ValueError("registry readers 선언 부재 — 실읽기량 술어 정의역 없음")
    for name, entry in readers.items():
        if not isinstance(entry, dict):
            raise ValueError("registry reader %s 선언 형식 오류" % name)
        if not entry.get("source"):
            raise ValueError("registry reader %s 행별 source 인용 누락 (CP §3.1)" % name)
        if entry.get("declares") is None:
            raise ValueError("registry reader %s declares 미선언" % name)
    return data


def ceiling_for(story_key: str, baseline: dict) -> int:
    """entries[key].ceiling if 등재 else default_ceiling.

    ★ 미등재를 '제한 없음' 으로 읽는 구현 금지 (ADR-180 §결정 5).
    """
    for entry in baseline.get("entries", []) or []:
        if str(entry.get("story_key")) == str(story_key):
            return int(entry["ceiling"])
    return int(baseline["default_ceiling"])


# ---------------------------------------------------------------------------
# O5 — 스캔 정의역 3항 AND (CP §7.4a)
# ---------------------------------------------------------------------------
def _glob_to_re(pattern: str, cross_slash: bool) -> "re.Pattern[str]":
    out = ["^"]
    for ch in pattern:
        if ch == "*":
            out.append(".*" if cross_slash else "[^/]*")
        elif ch == "?":
            out.append("." if cross_slash else "[^/]")
        else:
            out.append(re.escape(ch))
    out.append("$")
    return re.compile("".join(out))


def match_pathspec(paths: Iterable[str], pattern: str) -> Set[str]:
    """git pathspec wildmatch 기본값 — `*` 가 `/` 를 넘는다 (CP §3.5 실측)."""
    rx = _glob_to_re(pattern, cross_slash=True)
    return {p for p in paths if rx.match(p)}


def match_actions_glob(paths: Iterable[str], pattern: str) -> Set[str]:
    """GitHub Actions `on.paths` 글롭 — `*` 가 `/` 를 넘지 않는다 (CP §3.5 실측)."""
    rx = _glob_to_re(pattern, cross_slash=False)
    return {p for p in paths if rx.match(p)}


def check_scan_domain(trigger_set: Set[str], scan_set: Set[str],
                      expected_set: Set[str], declared_n: int,
                      carrier_set: Optional[Set[str]] = None) -> List[Verdict]:
    """O5 3항 AND — 상대 동일성만으로는 대칭 축소에 무감하다 (CP §7.4a).

    (a) trigger_set == scan_set                 # 전 정의역 상대 동일성 (트리거 glob ↔ 검사 glob)
    (b) carrier_set == EXPECTED_SET             # carrier 정의역 절대 기대집합 대조
    (c) |EXPECTED_SET| == DECLARED_N            # 기대집합 자체의 cardinality 선언

    carrier_set 생략 시 scan_set 을 쓴다. (a) 는 두 매처(git pathspec ↔ Actions glob)의
    깊이 비대칭을 잡고, (b)(c) 는 "게이트를 통째로 끄는 변형" 이 (a) 단독을 통과하는 것을 막는다.
    """
    name = "O5"
    if carrier_set is None:
        carrier_set = scan_set
    verdicts: List[Verdict] = []
    only_trigger = sorted(trigger_set - scan_set)
    only_scan = sorted(scan_set - trigger_set)
    if only_trigger or only_scan:
        verdicts.append(
            Verdict(name, True, "RED",
                    "(a) 트리거 집합 != 검사 집합 — |trigger_only|=%d %s |scan_only|=%d %s"
                    % (len(only_trigger), only_trigger[:5], len(only_scan), only_scan[:5]), leg="a")
        )
    else:
        verdicts.append(Verdict(name, True, "PASS", "(a) 트리거 집합 == 검사 집합 (%d)" % len(scan_set), leg="a"))
    if set(expected_set) != set(carrier_set):
        verdicts.append(
            Verdict(name, True, "RED",
                    "(b) carrier 스캔 집합 != 기대집합 — missing=%s extra=%s"
                    % (sorted(set(expected_set) - set(carrier_set)),
                       sorted(set(carrier_set) - set(expected_set))),
                    leg="b")
        )
    else:
        verdicts.append(Verdict(name, True, "PASS", "(b) carrier 스캔 집합 == 기대집합 (%d)" % len(expected_set), leg="b"))
    if len(set(expected_set)) != int(declared_n):
        verdicts.append(
            Verdict(name, True, "RED",
                    "(c) |EXPECTED_SET|=%d != DECLARED_N=%d" % (len(set(expected_set)), declared_n), leg="c")
        )
    else:
        verdicts.append(Verdict(name, True, "PASS", "(c) |EXPECTED_SET| == DECLARED_N (%d)" % declared_n, leg="c"))
    return verdicts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
# fail-closed(rc=1) 축 = **정보 손실 명제**만 (ADR-180 §결정 7).
#   dangling pointer / 앵커 미쌍·중복·오형식 / pure-move 위반 / INV-S3 RED / INV-S6 위반.
# O5(스캔 정의역 관측)는 정보 손실 명제가 아니므로 차단 축에 넣지 않는다 — 넣으면 AC-15 위반이다.
#   대신 O5 RED 는 "스캔을 신뢰할 수 없음" 이므로 rc=3(UNDETERMINED)로 올린다.
#   조용히 죽이지는 않는다 — 불일치는 개수 + 목록으로 값 방출한다 (O5 의 원래 목적).
LOSS_AXIS = ("INV-S1", "INV-S3", "INV-S6", "INV-ANCHOR")
OBSERVATION_AXIS = ("O5",)


def _emit(verdict: Verdict) -> None:
    tag = {"RED": "error", "SIGNAL": "warning", "UNDETERMINED": "warning"}.get(verdict.status, "notice")
    scope = "".join(
        [" domain=%s" % verdict.domain if verdict.domain else "",
         " leg=%s" % verdict.leg if verdict.leg else ""]
    )
    print("::%s::%s %s%s — %s" % (tag, verdict.name, verdict.status, scope, verdict.detail))


def _children_of(repo_root: str, ref: str, parent_path: str, tree_paths: Sequence[str]) -> Dict[str, str]:
    """분할 자식 본문. 평면 배치(`<parent stem>-S<N>.md`) — 하위 디렉터리 금지 (CP §3.5).

    ★ 판별자는 **파일명이 아니라 frontmatter `carries_sections`** 다.
      코퍼스에는 파일명 형상만 동형인 선재 sub-Story 가 다수 존재하며(실측: 이름 매치 19건 중
      `carries_sections` 보유 1건), 파일명으로 세면 정의역이 부풀려진다.
      파일명은 후보 prefilter 로만 쓰고, 자식 자격은 선언으로 확정한다.
      선언 없는 후보는 자식이 아니며, 부모 앵커가 그것을 가리키면 dangling 으로 RED 가 난다
      (조용한 skip 아님).
    """
    stem = parent_path[:-3] if parent_path.endswith(".md") else parent_path
    rx = re.compile(r"^%s-S[0-9A-Za-z]+\.md$" % re.escape(stem))
    out: Dict[str, str] = {}
    for path in tree_paths:
        if not rx.match(path):
            continue
        text = git_archive_text(repo_root, ref, path)
        if not child_carries(text):
            continue
        declared_parent = _frontmatter_field(text, "parent_story")
        if declared_parent is not None and str(declared_parent) != parent_path:
            continue
        out[path] = text
    return out


def _children_by_section(children: Dict[str, str]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for path in sorted(children):
        for section in child_carries(children[path]):
            out.setdefault(section, []).append(child_body(children[path]))
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check-story-read-surface",
        description=(
            "CFP-2986 / ADR-180 — Story 읽기면 게이트. "
            "구조 불변식(INV-S1/S2/S3/S6 + 앵커 3속성)은 fail-closed(rc=1), "
            "크기 축은 비차단 SIGNAL, 판정 불가는 rc=3(UNDETERMINED)."
        ),
        epilog="매체 규약: 코퍼스는 git archive(LF) 추출물만 사용 — 작업트리 직접 스캔 금지.",
    )
    parser.add_argument("--repo-root", default=".", help="코퍼스 repo 루트 (default: .)")
    parser.add_argument("--after-ref", default="HEAD", help="검사 대상 ref (default: HEAD)")
    parser.add_argument("--before-ref", default=None,
                        help="비교 기준 ref. 부재 시 INV-S1/S2 는 UNDETERMINED (rc=3)")
    parser.add_argument("--baseline", default="docs/story-read-surface-baseline.yaml")
    parser.add_argument("--registry", default="docs/story-read-declaration-registry.yaml")
    parser.add_argument("--theta-move", type=int, default=THETA_MOVE_DEFAULT)
    parser.add_argument("--reason-code", default=None,
                        help="INV-S2 강등 사유 (폐쇄 enum %s)" % list(REASON_CODE_ENUM))
    parser.add_argument("--json", action="store_true", help="machine-readable 요약을 stdout 에 방출")
    return parser


def run(args: argparse.Namespace) -> Tuple[int, dict]:
    verdicts: List[Verdict] = []
    baseline = load_baseline(args.baseline)
    registry = load_registry(args.registry)
    repo_root = args.repo_root
    after_ref = args.after_ref
    tree_paths = git_tree_paths(repo_root, after_ref)

    scan_domain = baseline["scan_domain"]
    trigger_set = match_pathspec(tree_paths, scan_domain["trigger_glob"])
    scan_set = match_actions_glob(tree_paths, scan_domain["scan_glob"])
    carrier_scan = match_actions_glob(scan_set, scan_domain["carrier_glob"])
    verdicts.extend(
        check_scan_domain(trigger_set, scan_set,
                          set(baseline["expected_scan_set"]), int(baseline["declared_scan_count"]),
                          carrier_set=carrier_scan)
    )

    file_map = baseline["file_map"]
    resolved_cache: Dict[str, str] = {}
    children_all: Dict[str, str] = {}
    opened: Set[str] = set()

    def resolve_file(domain: dict) -> str:
        key = str(domain["file"])
        if key in resolved_cache:
            return resolved_cache[key]
        path = file_map[key]
        text = git_archive_text(repo_root, after_ref, path)
        opened.add(path)
        kids = _children_of(repo_root, after_ref, path, tree_paths)
        children_all.update(kids)
        opened.update(kids)
        text = reassemble_document(text, _children_by_section(kids))
        resolved_cache[key] = text
        return text

    # INV-S3 — 항상 실행 (발화 조건 없음)
    verdicts.extend(check_inv_s3(baseline, resolve_file))

    # 앵커 무결성 + INV-S1/S2 + INV-S6 + 크기 축 (carrier 별)
    metrics: List[dict] = []
    reader_roster = [str(r) for r in baseline["reader_roster"]]
    cov = coverage(reader_roster, registry)
    floor = float(baseline["coverage_floor"])
    for parent_path in sorted(baseline["carriers"]):
        after_text = git_archive_text(repo_root, after_ref, parent_path)
        opened.add(parent_path)
        kids = _children_of(repo_root, after_ref, parent_path, tree_paths)
        children_all.update(kids)
        opened.update(kids)
        verdicts.extend(check_anchor_integrity(after_text, label=parent_path))
        for path in sorted(kids):
            verdicts.extend(check_anchor_integrity(kids[path], label=path))
        # dangling / 자기 포인터
        for section, ids in _dangling_check(after_text, kids, parent_path):
            verdicts.append(Verdict("INV-S1", True, "RED", "§%s dangling pointer: %s" % (section, ids)))
        if args.before_ref:
            before_text = git_archive_text(repo_root, args.before_ref, parent_path)
            verdicts.extend(check_inv_s1(before_text, after_text, _children_by_section(kids)))
            verdicts.extend(check_inv_s2(before_text, after_text, args.theta_move, args.reason_code))
        else:
            verdicts.append(
                Verdict("INV-S1", False, "UNDETERMINED", "before-ref 부재 — 차분 축 판정 불가", domain=parent_path)
            )
            verdicts.append(
                Verdict("INV-S2", False, "UNDETERMINED", "before-ref 부재 — 차분 축 판정 불가", domain=parent_path)
            )
        # 크기 축 = 비차단 SIGNAL
        parent_bytes = len(git_archive_bytes(repo_root, after_ref, parent_path))
        child_bytes = {p: len(t.encode("utf-8")) for p, t in kids.items()}
        registry_with_carries = dict(registry)
        registry_with_carries["carries"] = {p: child_carries(t) for p, t in kids.items()}
        cost = read_cost(parent_bytes, child_bytes, reader_roster, registry_with_carries)
        story_key = _story_key_of(parent_path)
        cap = ceiling_for(story_key, baseline)
        metrics.append({
            "story_key": story_key, "path": parent_path, "parent_bytes": parent_bytes,
            "children": len(child_bytes), "read_cost": cost, "ceiling": cap,
            "readers": len(reader_roster), "coverage": cov,
        })
        if cov < floor:
            verdicts.append(
                Verdict("READ-COST", True, "UNDETERMINED",
                        "coverage %.3f < floor %.3f — 절감 주장 금지 (판정 불가, AC-5 전제조건)" % (cov, floor),
                        domain=story_key)
            )
        elif cost > cap:
            verdicts.append(
                Verdict("READ-COST", True, "SIGNAL",
                        "read_cost %d > ceiling %d — 분할 의무 신호(비차단)" % (cost, cap), domain=story_key)
            )
        else:
            verdicts.append(
                Verdict("READ-COST", True, "PASS", "read_cost %d <= ceiling %d" % (cost, cap), domain=story_key)
            )
    verdicts.extend(check_inv_s6(children_all))

    for verdict in verdicts:
        _emit(verdict)

    deferred = sum(1 for v in verdicts if v.status == "UNDETERMINED")
    violations = sum(1 for v in verdicts if v.status == "RED")
    # scanned_count = 게이트가 **실제로 연** 파일 수. exit code 만으로는 "위반 0" 과 "아무것도
    # 안 열었음" 을 구별할 수 없으므로 값으로 방출한다 (O5 의 원래 목적 — "기동" 이 아니라 "열람").
    #
    # ★ 정상 비대칭 — O5(a) 의 '검사 매치 집합' 과 scanned_count 는 **다른 양**이다.
    #   둘이 같기를 기대하면 안 된다. 정의역이 애초에 다르다.
    #     · O5(a) 검사 매치 집합 = 코퍼스 **전역 인구조사**. 정의역 = `scan_glob` 전건.
    #       construction = match_actions_glob(git_tree_paths(after_ref), scan_glob).
    #       실측 **665** [엔진 wrapper `a3d7c56bb` × 코퍼스 internal-docs `8f317f7ce`,
    #       glob `*/stories/*.md`] — O5 (a) verdict 에 별도로 인쇄된다.
    #     · scanned_count = **carrier 로 좁혀 실제로 연** 집합. 정의역 = `carrier_glob`
    #       (`wrapper/stories/CFP-2986*.md`) + `file_map` 정의역 파일.
    #       construction = |opened| = resolve_file() 이 연 file_map 파일·그 자식 ∪ carriers 루프.
    #       실측 **3** = STORY(`wrapper/stories/CFP-2986.md`) + 자식(`…-S1.md`) + CP [동 트리].
    #   ⇒ **665 vs 3 은 정상값이다.** 이 차이를 "정의역 불일치" 로 읽고 경보하면 상시 오경보다.
    #     트리거↔검사 정의역 일치 판정은 여기가 아니라 **O5 (a)** 가 단독으로 진다.
    #   ※ 아래 notice 의 `domain=` 은 scan_glob(=665 쪽 정의역) 라벨이지 scanned_count 의
    #     정의역이 아니다 — 한 줄에 두 정의역이 인접 인쇄되는 것이 오해의 원천이다.
    #   ※ baseline `corpus_n: 664` 는 **동결 트리** `7d075514` 기준 p50 산정 분모라 live 665
    #     (현 HEAD)와 달라도 정상이다 — 트리가 다르다(동결값 ⊥ 현재값).
    #
    # ★ 진짜 이상 신호는 아래 `scanned == 0` 뿐이다 (정의역 붕괴 — carrier·앵커 해결 실패).
    scanned = len(opened)
    print("::notice::story-read-cost scanned_count=%d violations=%d deferred=%d domain=%s tree=%s"
          % (scanned, violations, deferred, scan_domain["scan_glob"], baseline["baseline_tree_sha"]))
    if scanned == 0:
        print("::warning::story-read-cost scanned_count=0 — GREEN 이 아니라 조사 대상 (정의역 붕괴 의심)")

    loss_red = [v for v in verdicts if v.status == "RED" and v.name in LOSS_AXIS]
    observation_red = [v for v in verdicts if v.status == "RED" and v.name in OBSERVATION_AXIS]
    if loss_red:
        rc = EXIT_FAIL
    elif observation_red or any(v.status == "UNDETERMINED" for v in verdicts):
        rc = EXIT_UNDETERMINED
    else:
        rc = EXIT_PASS
    summary = {
        "rc": rc,
        "scanned_count": scanned,
        "violations": violations,
        "deferred": deferred,
        "coverage": cov,
        "coverage_floor": floor,
        "tree": baseline["baseline_tree_sha"],
        "metrics": metrics,
        "verdicts": [asdict(v) for v in verdicts],
    }
    return rc, summary


def _story_key_of(path: str) -> str:
    stem = path.rsplit("/", 1)[-1]
    return stem[:-3] if stem.endswith(".md") else stem


def _dangling_check(parent_text: str, children: Dict[str, str], parent_path: str):
    """stub 이 가리키는 자식 파일 부재(dangling) / 자기 포인터 검출."""
    out = []
    present = {p.rsplit("/", 1)[-1] for p in children}
    for kind, section, aid, _ln in _raw_anchors(parent_text):
        if kind != "begin" or not aid:
            continue
        target = "%s.md" % aid
        if target == parent_path.rsplit("/", 1)[-1]:
            out.append((section or "?", "자기 포인터 %s" % target))
        elif target not in present:
            out.append((section or "?", "자식 파일 부재 %s" % target))
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:  # --help / 사용법 오류
        return EXIT_PASS if exc.code == 0 else EXIT_USAGE
    try:
        rc, summary = run(args)
    except ValueError as exc:
        print("::error::story-read-surface 배선 금지 — %s" % exc)
        return EXIT_FAIL
    except FileNotFoundError as exc:
        print("::warning::story-read-surface 판정 불가 — %s" % exc)
        return EXIT_UNDETERMINED
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
