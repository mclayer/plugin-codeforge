#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_story_read_surface_fixtures.py — CFP-2986 Phase 2 §8 Test Contract fixture / mutant 하네스.

Change Plan `cfp-2986-story-growth-axis-externalization.md` §8.1 RTM · §8.2 mutant 로스터 ·
§8.3 경계 조건 · §8.4 무결성 불변식 · §11.5 baseline artifact 를 실행 가능한 fixture 로 고정한다.

QADev 경계: 본 파일 + tests/scripts/** 만 작성. production 코드(scripts/**) READ-ONLY —
본 하네스는 엔진의 **실제 시그니처에 맞춘다** (엔진을 테스트에 맞추지 않는다).

설계 규율 (§8.2 자기 규율 — 비협상):
  · 각 mutant 는 "주입 시 RED ∧ 미주입 대조군 GREEN" 을 **실행**으로 증명한 뒤에만 검출 선언.
  · 대조군이 이미 RED = 등가 mutant → admission rule 미충족 → 계상 금지.
  · 판정은 boolean 단독 금지 — **위반 개수(count) ∧ per-domain/leg 판정 벡터**로 한다 (C-6).
  · 전역 스칼라·전역 집합 대조 금지 — (셀ID → 값) 매핑을 **정의역별로** 대조 (C-7 / C-13).

정량 5-tuple 규약 (§8 C-28): 모든 수치 주장 = {값, 기준 트리 SHA, 매체(LF), 정의역(분모), construction}.
`construction` = 어느 바이트 구간을 어떻게 구성했는가. 설계리뷰 최종 라운드에서 이 필드 부재로
peer 2명이 임의 줄정렬 suffix 를 못 보고 오판했다 — 그래서 필수 필드다.

매체 규약 (§4.2.2a): 추출은 `git archive`(LF 고정)만. 작업트리 직접 스캔 금지.
본 하네스의 fixture 는 **합성(synthetic)** 이므로 기준 트리 SHA 자리에 `synthetic:sha256:<12>` 를
쓰고, repo 사실을 인용하는 자리에서만 실 git tree SHA 를 쓴다 (허구 SHA 기입 금지).
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

# tests/scripts/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = REPO_ROOT / "scripts" / "lib" / "check_story_read_surface.py"
WRAPPER_SH = REPO_ROOT / "scripts" / "check-story-read-surface.sh"

MEDIA = "LF"

# 엔진이 export 해야 하는 심볼 (Change Plan §8 전제 + 실 엔진 실측 API)
REQUIRED_ENGINE_SYMBOLS = (
    "EXIT_PASS", "EXIT_FAIL", "EXIT_USAGE", "EXIT_UNDETERMINED",
    "Verdict",
    "git_archive_bytes", "digest", "content_canon",
    "parse_anchors", "anchor_delta", "sections_of", "check_anchor_integrity",
    "split_sections", "slice_section_by_key", "strip_stub",
    "reassemble", "reassemble_document", "child_body", "child_carries",
    "check_inv_s1", "check_inv_s2", "check_inv_s3", "check_inv_s6",
    "extract_domain", "read_cost", "coverage",
    "load_baseline", "load_registry", "ceiling_for", "check_scan_domain",
    "main", "build_parser",
)


class EngineMissing(RuntimeError):
    """엔진 미착지 / API 미충족 — RED. skip 이 아니라 명시 실패로 드러낸다."""


# ---------------------------------------------------------------------------
# 0. 엔진 로딩 (M-SUTURE 를 위해 임의 소스 경로에서 로드 가능해야 한다)
# ---------------------------------------------------------------------------

_ENGINE_CACHE: dict = {}


def engine_source() -> str:
    if not ENGINE_PATH.exists():
        raise EngineMissing(
            f"엔진 미착지: {ENGINE_PATH}\n"
            "  Change Plan §5 Phase 2 = scripts/lib/check_story_read_surface.py 신규.\n"
            "  본 suite 는 그 계약의 테스트이므로 엔진 착지 전에는 실패가 정상이다."
        )
    return ENGINE_PATH.read_text(encoding="utf-8")


def load_engine(source_path=None, tag: str = "pristine"):
    """엔진 모듈 로드. `source_path` 지정 시 그 사본을 로드한다 (mutant 주입용)."""
    path = Path(source_path) if source_path else ENGINE_PATH
    key = f"{tag}:{path}"
    if key in _ENGINE_CACHE:
        return _ENGINE_CACHE[key]
    if not path.exists():
        raise EngineMissing(f"엔진 미착지: {path}")
    modname = f"_cfp2986_engine_{tag}_{abs(hash(key)) % 10 ** 8}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # `@dataclass` 는 정의 시점에 `sys.modules[cls.__module__]` 를 조회하므로
    # exec_module **전에** 등록해야 한다 (미등록 시 AttributeError: NoneType).
    sys.modules[modname] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(modname, None)
        raise
    missing = [s for s in REQUIRED_ENGINE_SYMBOLS if not hasattr(mod, s)]
    if missing:
        raise EngineMissing(f"엔진 API 미충족 — 누락 심볼 {missing}")
    _ENGINE_CACHE[key] = mod
    return mod


def write_engine_variant(tmpdir, source: str, name: str) -> Path:
    """엔진 소스 변형본을 LF 고정으로 기록한다 (Windows CRLF 오염 차단)."""
    p = Path(tmpdir) / f"{name}.py"
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(source)
    return p


# ---------------------------------------------------------------------------
# 1. 매체 / 증거 유틸
# ---------------------------------------------------------------------------

def count_cr(data) -> int:
    r"""raw CR 계수 — `grep -cU $'\r'` 는 거짓 양성이므로 Python b'\r' 카운트로 센다."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return data.count(b"\r")


def synthetic_sha(*texts: str) -> str:
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
    return "synthetic:sha256:" + h.hexdigest()[:12]


def repo_head_sha() -> str:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:  # noqa: BLE001 - 측정 실패는 값 위조보다 낫다
        pass
    return "unavailable"


def write_lf(path, text: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return p


# ---------------------------------------------------------------------------
# 2. 문서 fixture — Story / Change Plan 합성본
#    §11.5 domains 선언이 그대로 성립하도록 구조를 실물과 동형으로 만든다.
# ---------------------------------------------------------------------------

# §4.2.2a 귀속표 (실물 CFP-2986.md:369-371 과 동형) — 헤더 11열 × 데이터 1행 × {KB, PCT} = 22셀.
# raw_rows(물리 데이터 행) = 1 이라 전역 행-기준 cardinality 가 여기서 born-broken 을 드러낸다.
CORPUS_CELLS = [
    ("9", "12.71", "21.0"), ("4", "12.29", "20.3"), ("7", "10.33", "17.1"),
    ("5", "7.51", "12.4"), ("8", "6.68", "11.0"), ("2", "5.69", "9.4"),
    ("6", "4.39", "7.2"), ("10", "2.54", "4.2"), ("3", "0.89", "1.5"),
    ("1", "0.58", "1.0"), ("14", "−2.18", "−3.6"),   # U+2212 MINUS SIGN — 실물 표기 그대로
]

# §8.1 RTM 정본 15 명명 테스트 (AC → named test)
RTM_NAMED = [
    ("AC-1", "test_read_surface_not_increased"),
    ("AC-2", "test_pure_move_digest_preserved"),
    ("AC-4", "test_sections_1_to_11_headers_present"),
    ("AC-5", "test_read_surface_reduction_measured"),
    ("AC-7", "test_append_heavy_section_externalized"),
    ("AC-8", "test_grandfather_baseline_stable_key"),
    ("AC-10", "test_self_application_carrier_passes"),
    ("AC-11", "test_derived_view_regenerable_and_not_sole_source"),
    ("AC-12", "test_index_depth_not_exceeding_one"),
    ("AC-15", "test_size_verdict_is_signal_not_block"),
    ("AC-17", "test_mutant_red_and_control_green"),
    ("AC-18", "test_sibling_site_no_regression"),
    ("AC-19", "test_rule_has_no_section_hardcoding"),
    ("AC-20", "test_violation_fixture_exits_nonzero"),
    ("AC-21", "test_metric_unit_matches_declared_quantity"),
]
RTM_DECLARED_ROW = ["AC-3", "AC-6", "AC-9", "AC-13", "AC-14", "AC-16"]

# CP §1 산문 한 줄에 착지하는 AC 매핑 13종 (표 아님 — 전역 table_cells_only 가 born-broken 인 지점)
CP_S1_IDS = ["AC-1", "AC-2", "AC-5", "AC-7", "AC-8", "AC-10", "AC-12",
             "AC-15", "AC-17", "AC-18", "AC-19", "AC-20", "AC-21"]
ALL_AC = [f"AC-{i}" for i in range(1, 22)]

STORY_PATH = "wrapper/stories/CFP-2986.md"
CP_PATH = "wrapper/change-plans/cfp-2986.md"
SPLIT_ID = "CFP-2986-S1"
SPLIT_ID_S10 = "CFP-2986-S2"
SPLIT_ID_S4 = "CFP-2986-S3"
CHILD_DIR = "wrapper/stories"

READER_ROSTER = ["orchestrator", "requirements", "requirements-review", "design",
                 "design-review", "develop", "code-review", "integration-test"]

_STUB_LINE = "*(본문은 {child}.md 로 이동 — 순수 이동, 정보 삭제 0)*"


def child_path(split_id: str) -> str:
    return f"{CHILD_DIR}/{split_id}.md"


def _anchor_block(section: str, split_id: str) -> str:
    """§3.4 앵커 쌍 — 3속성(명시 ∧ 쌍 ∧ 유일). stub 은 non-empty 여야 한다."""
    return (
        f"<!-- cfp-split:begin section={section} id={split_id} -->\n"
        + _STUB_LINE.format(child=split_id) + "\n"
        f"<!-- cfp-split:end id={split_id} -->\n"
    )


def _corpus_table(cells=None) -> str:
    r"""CORPUS 귀속표. span_anchor `^\|\s*§9\s*\|\s*§4\s*\|` 가 정확히 이 헤더에 걸린다."""
    cells = cells if cells is not None else CORPUS_CELLS
    head = "| " + " | ".join(f"§{s}" for s, _, _ in cells) + " |"
    sep = "|" + "---:|" * len(cells)
    row = "| " + " | ".join(f"{kb} KB<br>{pct}%" for _, kb, pct in cells) + " |"
    return "\n".join([head, sep, row])


def _slicing_convention_table() -> str:
    r"""§4.2.2a 안 **첫 번째** 표 — M-ANCHOR-LOOSE(`^\|` 로 느슨화)가 잘못 무는 미끼."""
    return (
        "| 요소 | 정의 |\n"
        "|---|---|\n"
        "| 슬라이서 V1 (정본) | h2 번호 매칭 |\n"
        "| h2 경계 | 다음 h2 직전까지 |\n"
        "| 매체 | archive(LF) 추출물 |\n"
    )


def _fix_axis_table() -> str:
    """§4.2.2a 안 **두 번째** 표 — 다중 표 상황을 실물과 동형으로 만든다."""
    return (
        "| 버킷 | n | 파일 전체 |\n"
        "|---|---:|---:|\n"
        "| 0행 | 348 | 25.47 |\n"
        "| 6행+ | 6 | 120.43 |\n"
    )


def build_section_4(*, fence_inner_line: bool = True, fence_inject_heading: bool = False,
                    corpus_cells=None, heading: bool = True) -> str:
    """§4 본문. §4.2.2a 안에 코드펜스 + 표 3개(첫 표 = 앵커 미끼, 셋째 표 = CORPUS)."""
    fence_lines = ["```bash"]
    if fence_inner_line:
        # 실물 CFP-2986.md:348 — 펜스 안 `# 인자: TREE = …`.
        # fence-aware 미적용 슬라이서는 이 줄을 heading 으로 오인해 절을 조기 종결한다.
        fence_lines.append("# 인자: TREE = 기준 트리 SHA")
    if fence_inject_heading:
        # M-FENCE-INJECT 주입 축 — 펜스 안 `## 5.` phantom heading.
        fence_lines.append("## 5. phantom heading (펜스 안)")
    fence_lines += ["TREE=4ce40368", 'git archive "$TREE" wrapper/stories | tar -x', "```"]

    # ★ heading 다음에 빈 줄을 두지 않는다 — 엔진 `reassemble` 은 부분들을 rstrip 후
    #   개행 1개로 결합하므로, 빈 줄이 있으면 재조립본이 원문과 바이트 불일치가 된다.
    head = ["## §4. 하위 분석"] if heading else []
    return "\n".join([
        *head,
        "성장축 귀속은 아래 절이 정본이다.",
        "",
        "#### 4.2.2a 귀속표 재현 절차 (정본)",
        "",
        "산출 스크립트가 커밋돼 있지 않으므로 슬라이싱 규약을 문면에 고정한다.",
        "",
        "\n".join(fence_lines),
        "",
        "**슬라이싱 규약**",
        "",
        _slicing_convention_table(),
        "**FIX-축 코호트 재현 결과**",
        "",
        _fix_axis_table(),
        "**PL firsthand 재현 결과** (`4ce40368`, n=576)",
        "",
        _corpus_table(corpus_cells),
        "",
        "보조 레버 2종 = 중복 서술 제거 / 생성 시점 저작 규율.",
        "",
    ])


def build_section_5(*, ac_rows=None, stubbed: bool = False, pad: bool = True) -> str:
    """§5. §5.3 AC 표(21행) + 표 **밖** 산문 22 출현 ⇒ 절 슬라이스 전체 = 43 (표 span 이 판별자)."""
    if stubbed:
        # M-SEC5 — §5 를 stub 화 (`AC-\d+` 토큰 0)
        return "\n".join(["## §5. 수용 기준", "", "*(내용 생략)*", ""])

    rows = ac_rows if ac_rows is not None else ALL_AC
    # ★ statement 셀에 AC-ID 를 재기재하지 않는다 — 재기재하면 행당 출현이 2가 되어
    #   id_occurrence_count 가 21 이 아니라 42 가 되고, `M-GLOBAL`(치환)의 leg2 독립성이 깨진다.
    if pad:
        body = [f"| {ac} | 수용 기준 서술 | normative | 2 |" for ac in rows]
    else:
        # M-EQUIV 표기 등가변형 축 ② — 데이터 행 셀 padding 제거
        body = [f"|{ac}|수용 기준 서술|normative|2|" for ac in rows]

    prose = " ".join(ALL_AC[:11])
    return "\n".join([
        "## §5. 수용 기준", "",
        "### 5.3 AC 표", "",
        f"관련 AC — {prose}",
        f"관련 AC — {prose}",
        "",
        "| id | statement | tier | phase |",
        "|---|---|---|---|",
        *body,
        "",
    ])


def build_story(*, split_9: bool = False, split_10: bool = False, split_4: bool = False,
                section_9_body=None, section_4_kwargs=None, section_5_kwargs=None,
                section_7_extra: str = "", section_9_extra: str = "",
                heading_demote_9: bool = False) -> str:
    """Story 합성본 — §1..§11 + preamble. 분할 여부·섹션 변형을 파라미터로 받는다."""
    s4 = build_section_4(**(section_4_kwargs or {}))
    s5 = build_section_5(**(section_5_kwargs or {}))
    body9 = section_9_body if section_9_body is not None else SECTION_9_BODY

    parts = [
        "---", "title: Story 성장축 외부화 (fixture)", "story: CFP-2986", "---", "",
        "# Story: 성장축 외부화 (fixture)", "",
        "## §1. 요구 원문", "", "읽기 단가를 구조로 절단한다. 정보 삭제 0.", "",
        "## §2. 배경", "", "`## 2.` 인용이 본문에 존재한다 (E-3 정상 저작 경계).", "",
        "## §3. 도입할 설계", "", "목적함수 = lane 진입당 실읽기 바이트.", "",
    ]
    if split_4:
        parts += ["## §4. 하위 분석\n" + _anchor_block("4", SPLIT_ID_S4)]
    else:
        parts += [s4]
    parts += [s5]
    parts += ["## §6. 리팩토링 선행 작업", "", "없음.", ""]
    # ★ §7·§9 는 **단일 문자열 원소**로 조립한다 — 리스트 원소로 쪼개 join 하면
    #   삽입할 때마다 구분 개행 1~2 B 가 따라붙어 "총량 Δ = 0"(E-4) 구성이 무너진다.
    parts += ["## §7. 보안 설계\n\n신규 신뢰경계 0.\n" + section_7_extra]
    parts += ["## §8. Test Contract", "", "Phase 2 이행 계약.", ""]

    heading9 = "### §9. 분기 선택" if heading_demote_9 else "## §9. 분기 선택"
    body_or_stub = _anchor_block("9", SPLIT_ID) if split_9 else body9
    parts += [heading9 + "\n" + body_or_stub + section_9_extra]

    body10_or_stub = _anchor_block("10", SPLIT_ID_S10) if split_10 else SECTION_10_BODY
    parts += ["## §10. FIX 원장\n" + body10_or_stub]
    parts += ["## §11. 데이터 마이그레이션", "", "문서 코퍼스 — RDB N/A.", ""]
    return "\n".join(parts)


def _filler(tag: str, n: int) -> str:
    """결정적 filler — 바이트 구간을 construction 필드로 정확히 기술할 수 있게 한다."""
    line = f"{tag} 서술 행 — 결정적 filler."
    return "\n".join(f"{line} #{i:04d}" for i in range(n)) + "\n"


SECTION_9_BODY = "채택 = 성장축 외부화 + 실읽기량 목적함수.\n\n" + _filler("§9 verdict", 400)
SECTION_10_BODY = ("| Iter | 사유 | 처분 |\n|---:|---|---|\n| 1 | 공백 | FIX |\n\n"
                   + _filler("§10 원장", 120))


def build_child(section: str, split_id: str, body: str, *, nested_marker: bool = False,
                carries=None) -> str:
    """자식 파일. `carries_sections` 가 **자식 자격의 판별자**다 (파일명 형상 아님)."""
    carries = carries if carries is not None else [section]
    fm = "\n".join([
        "---",
        f"parent_story: {STORY_PATH}",
        f"carries_sections: [{', '.join(str(c) for c in carries)}]",
        f"split_id: {split_id}",
        "---", "",
    ])
    nested = _anchor_block("99", "CFP-2986-S9") if nested_marker else ""
    return fm + nested + body


# ---------------------------------------------------------------------------
# 3. baseline artifact (§11.5) — 정의역별 자족 선언
# ---------------------------------------------------------------------------

def _corpus_expected() -> dict:
    out = {}
    for sec, kb, pct in CORPUS_CELLS:
        out[f"S{sec}.KB"] = kb
        out[f"S{sec}.PCT"] = pct
    return out


CORPUS_EXPECTED = _corpus_expected()          # 22셀
CP_S1_EXPECTED = {ac: 1 for ac in CP_S1_IDS}  # 13
CP_S81_EXPECTED = {ac: 1 for ac in ALL_AC}    # 21
S53_EXPECTED = {ac: 1 for ac in ALL_AC}       # 21

DECLARED_CARDINALITY = {
    "CORPUS": 22, "CP_S1_MAPPING": 13, "CP_S81_RTM": 21, "STORY_S53_AC_TABLE": 21,
}
ENFORCED_DOMAINS = tuple(DECLARED_CARDINALITY)
DEFERRED_DOMAINS = ("SELF", "BASE", "AUTHOR", "LEGC")
# §8.4 정의역 양화 표 — 정량 셀 계열 기대 cardinality (합 104)
QUANT_DECLARED = {"CORPUS": 22, "SELF": 30, "BASE": 18, "AUTHOR": 10, "LEGC": 24}

# §8.4a ③ 검출 정의역 비축소의 **두 축**을 나란히 선언한다.
#   (b) 정의역 로스터 축 = 바로 위 `DECLARED_CARDINALITY`
#   (a) mutant 로스터 축 = 아래 `DECLARED_MUTANT_IDS` — `run_battery` 가 산출해야 하는
#       mutant 전건. 등록 자체를 지우면 개별 mutant assert 는 전부 통과한 채 배터리만
#       조용히 줄어든다(무검출 회피 경로). 그 축소를 잡는 유일한 측정면이 이 상수다.
#       ※ 정직한 한계: `_` 접두 키는 메타(`_tree` 등)라 로스터 대조에서 제외한다.
DECLARED_MUTANT_IDS = frozenset({
    "M-ANCHOR-DUP", "M-ANCHOR-DUPEND", "M-ANCHOR-LOOSE", "M-ANCHOR-MALFORMED",
    "M-ANCHOR-NOSECTION", "M-ANCHOR-UNPAIRED",
    "M-APPEND-CTL-1000", "M-APPEND-CTL-50000", "M-BASIS-RAW",
    "M-CARD-CROSS", "M-CARD-IN", "M-CARD-VALUE",
    "M-DANGLING", "M-DEPTH2", "M-DOMAIN", "M-DUP-ROW",
    "M-E1", "M-E2", "M-E3", "M-E4", "M-EQUIV",
    "M-FENCE-INJECT", "M-GLOBAL", "M-GLOBALRULE", "M-MARGIN", "M-MIX-min",
    "M-PREEXIST", "M-REASON-FREEFORM", "M-S3-NOSPLIT",
    "M-SCAN-ASYM", "M-SCAN-CARD", "M-SCANGLOB", "M-SEC5", "M-SELFPTR", "M-STRAYEND",
})

DEFAULT_CEILING = 400000
CARRIER_CEILING = 400000


def _enforced_domains() -> dict:
    return {
        "CORPUS": {
            "kind": "quantitative_cells", "file": "STORY", "section": "4.2.2a",
            "status": "enforced", "span_kind": "table",
            "span_anchor": r"^\|\s*§9\s*\|\s*§4\s*\|",
            "fence_aware": True, "cardinality_basis": "cell_count",
            "leg3": "applicable", "expected": dict(CORPUS_EXPECTED),
        },
        "CP_S1_MAPPING": {
            "kind": "ac_id_landing", "file": "CP", "section": "1",
            "status": "enforced", "span_kind": "line",
            "span_anchor": r"^\*\*수용 기준 \(AC 매핑\)\*\*",
            "fence_aware": True, "cardinality_basis": "id_occurrence_count",
            "leg3": "not_applicable", "leg3_na_reason": "NO_VALUE_AXIS",
            "expected": dict(CP_S1_EXPECTED),
        },
        "CP_S81_RTM": {
            "kind": "ac_id_landing", "file": "CP", "section": "8.1",
            "status": "enforced", "span_kind": "table",
            "span_anchor": r"^\|\s*AC\s*\|\s*tier\s*\|",
            "fence_aware": True, "cardinality_basis": "id_occurrence_count",
            "leg3": "not_applicable", "leg3_na_reason": "NO_VALUE_AXIS",
            "expected": dict(CP_S81_EXPECTED),
        },
        "STORY_S53_AC_TABLE": {
            "kind": "ac_id_landing", "file": "STORY", "section": "5.3",
            "status": "enforced", "span_kind": "table",
            "span_anchor": r"^\|\s*id\s*\|\s*statement\s*\|",
            "fence_aware": True, "cardinality_basis": "id_occurrence_count",
            "leg3": "not_applicable", "leg3_na_reason": "NO_VALUE_AXIS",
            "expected": dict(S53_EXPECTED),
        },
    }


def build_baseline(*, deferred: bool = True, children: bool = True, **overrides) -> dict:
    """§11.5 baseline. 필수 최상위 키 전건 — 하나라도 누락 = 배선 금지(fail-closed)."""
    domains = _enforced_domains()
    if deferred:
        for name in DEFERRED_DOMAINS:
            domains[name] = {"kind": "quantitative_cells", "status": "deferred",
                             "reason_code": "DEFERRED_NOT_MATERIALIZED"}
    scan_set = [STORY_PATH] + ([child_path(SPLIT_ID), child_path(SPLIT_ID_S10)] if children else [])
    base = {
        "schema_version": 1,
        "introduced_by": "CFP-2986",
        "carrier_story": "CFP-2986",
        "adr": "ADR-180",
        "baseline_tree_sha": "0" * 40,
        "baseline_media": "LF",
        "content_digest": "",
        "frozen_at": "2026-08-16T18:02:00+09:00",
        "reader_roster": list(READER_ROSTER),
        "default_ceiling": DEFAULT_CEILING,
        "coverage_floor": 1.0,
        "file_map": {"STORY": STORY_PATH, "CP": CP_PATH},
        "scan_domain": {"trigger_glob": "*/stories/*.md",
                        "scan_glob": "*/stories/*.md",
                        "carrier_glob": "wrapper/stories/CFP-2986*.md"},
        "carriers": [STORY_PATH],
        "expected_scan_set": list(scan_set),
        "declared_scan_count": len(scan_set),
        "domain_schema": {
            "required_keys": ["kind", "file", "section", "span_kind", "span_anchor",
                              "fence_aware", "cardinality_basis", "leg3", "expected", "status"],
            "kind_enum": ["quantitative_cells", "ac_id_landing"],
            "span_kind_enum": ["table", "line", "section"],
            "basis_enum": ["cell_count", "id_occurrence_count"],
            "leg3_enum": ["applicable", "not_applicable"],
            "leg3_na_reason_enum": ["NO_VALUE_AXIS"],
            "status_enum": ["enforced", "deferred"],
        },
        "domains": domains,
        "entries": [{"story_key": "CFP-2986", "ceiling": CARRIER_CEILING}],
    }
    base.update(overrides)
    return base


def build_registry(declared=None, *, carries=None) -> dict:
    """read-declaration registry — 행별 `source` 인용 의무 (CP §3.1)."""
    declared = declared if declared is not None else {r: ["5"] for r in READER_ROSTER}
    readers = {r: {"declares": list(secs), "source": "CP §3.1 fixture"}
               for r, secs in declared.items()}
    return {"readers": readers, "carries": dict(carries or {})}


def build_cp(*, rtm_rows=None, declared_row=None, s1_ids=None,
             rtm_header: str = "| AC | tier | named test |", rtm_pad: bool = True) -> str:
    """Change Plan 합성본 — §1 산문 AC 매핑(13) + §8.1 RTM(21 출현 / 물리 16행)."""
    rtm_rows = rtm_rows if rtm_rows is not None else [ac for ac, _ in RTM_NAMED]
    declared_row = declared_row if declared_row is not None else list(RTM_DECLARED_ROW)
    s1_ids = s1_ids if s1_ids is not None else list(CP_S1_IDS)

    named = dict(RTM_NAMED)
    if rtm_pad:
        rows = [f"| {ac} | normative | `{named.get(ac, 'test_unmapped')}` |" for ac in rtm_rows]
    else:
        rows = [f"|{ac}|normative|`{named.get(ac, 'test_unmapped')}`|" for ac in rtm_rows]
    if declared_row:
        rows.append("| " + " / ".join(declared_row) + " | declared | 기계 판정자 부재 |")

    s1_line = "**수용 기준 (AC 매핑)**: " + " / ".join(f"{ac}(요건)" for ac in s1_ids)
    prose = " ".join(ALL_AC[:11])
    return "\n".join([
        "---", "title: Change Plan (fixture)", "story: CFP-2986", "---", "",
        "# Change Plan (fixture)", "",
        "## §1. 목적", "", "목적 = 읽기 단가 절단.", "", s1_line, "",
        "## §2. 현재 구조 분석", "", "as-is.", "",
        "## §8. Test Contract", "",
        "### §8.1 AC → named test 매핑 (RTM, zero-drop)", "",
        rtm_header, "|---|---|---|", *rows, "",
        "### §8.2 mutant 로스터", "",
        "| ID | mutant | 기대 |", "|---|---|---|",
        "| M-GLOBAL | 전 정의역 치환 (형제 site) → AC-99 혼입 | RED |", "",
        f"관련 AC — {prose}", f"관련 AC — {prose}", "",
    ])


# ---------------------------------------------------------------------------
# 4. read_cost fixture (§8.2 M-UNIT 특칙 — 등가 mutant 회피)
# ---------------------------------------------------------------------------

class ReadCostFixture(dict):
    def __init__(self, name, parent_bytes, children, readers, registry, construction):
        super().__init__(name=name, parent_bytes=parent_bytes, children=children,
                         readers=readers, registry=registry, construction=construction)


def fx_split() -> ReadCostFixture:
    """FX-SPLIT (필수) — parent 1,000 B + child 50,000 B, N=8, d=1 ⇒ read_cost 58,000."""
    child = child_path(SPLIT_ID)
    declared = {r: (["9"] if r == "orchestrator" else ["5"]) for r in READER_ROSTER}
    registry = build_registry(declared, carries={child: ["9"]})
    return ReadCostFixture(
        "FX-SPLIT", 1000, {child: 50000}, list(READER_ROSTER), registry,
        "parent stub 1,000 B (§9 본문 제외) + child 50,000 B(§9 전문), "
        "readers N=8 전원 registry 등재, 이 중 orchestrator 만 §9 선언 ⇒ opener d=1. "
        "read_cost = 8×1,000 + 1×50,000 = 58,000 B",
    )


def fx_flat() -> ReadCostFixture:
    """FX-FLAT (부적격) — parent 51,000 B, 자식 없음, N=8 ⇒ read_cost 408,000 (단조 배수)."""
    return ReadCostFixture(
        "FX-FLAT", 51000, {}, list(READER_ROSTER), build_registry(),
        "parent 51,000 B 단일 파일(자식 0), readers N=8 전원 등재. "
        "read_cost = 8×51,000 = 408,000 B = 8 × 자식포함총합 ⇒ 단조 배수",
    )


def total_including_children(fx) -> int:
    """M-UNIT 치환 술어 ① — `bytes(parent) + Σ bytes(children)` (자식 포함 총합)."""
    return fx["parent_bytes"] + sum(fx["children"].values())


def line_count_metric(fx, bytes_per_line: int = 50) -> int:
    """M-UNIT 치환 술어 ② — 줄수. 바이트를 고정 줄길이로 환산한 대리 단위."""
    return total_including_children(fx) // bytes_per_line


def engine_read_cost(engine, fx) -> int:
    return engine.read_cost(fx["parent_bytes"], fx["children"], fx["readers"], fx["registry"])


# ---------------------------------------------------------------------------
# 5. 판정 컨텍스트 / 실행기
# ---------------------------------------------------------------------------

class Ctx(dict):
    """한 판정 실행의 전 입력 — before/after Story, CP, children(path→text), baseline."""

    def __init__(self, story_before, story_after, cp_after, children, baseline,
                 construction="", cp_before=None):
        super().__init__(
            story_before=story_before, story_after=story_after,
            cp_before=cp_before if cp_before is not None else cp_after,
            cp_after=cp_after, children=dict(children), baseline=baseline,
            construction=construction)

    def copy_with(self, **kw):
        d = dict(self)
        d.update(kw)
        return Ctx(d["story_before"], d["story_after"], d["cp_after"], d["children"],
                   d["baseline"], d.get("construction", ""), d.get("cp_before"))


def children_by_section(engine, ctx) -> dict:
    """{섹션: [자식 본문]} — 판별자는 파일명이 아니라 frontmatter `carries_sections`."""
    out = {}
    for path in sorted(ctx["children"]):
        text = ctx["children"][path]
        for sec in engine.child_carries(text):
            out.setdefault(sec, []).append(engine.child_body(text))
    return out


def canonical_ctx(**kw) -> Ctx:
    """대조군 M0 — 무변경 정본(§8.4a ④ 최소 통과선). before == after, 분할 없음."""
    story = build_story(**kw)
    return Ctx(story, story, build_cp(), {}, build_baseline(),
               "무변경 정본 — story_before == story_after, split anchor 0쌍, CP 무변경")


def split_ctx(*, split_4: bool = False) -> Ctx:
    """분할 커밋 — §9·§10(옵션 §4) 순수 이동. anchor_delta ≠ ∅."""
    before = build_story()
    after = build_story(split_9=True, split_10=True, split_4=split_4)
    children = {
        child_path(SPLIT_ID): build_child("9", SPLIT_ID, SECTION_9_BODY),
        child_path(SPLIT_ID_S10): build_child("10", SPLIT_ID_S10, SECTION_10_BODY),
    }
    if split_4:
        children[child_path(SPLIT_ID_S4)] = build_child(
            "4", SPLIT_ID_S4, build_section_4(heading=False))
    con = ("§9·§10" + ("·§4" if split_4 else "")
           + " 순수 이동 — parent 구간을 앵커 쌍 + stub 1줄로 치환, "
             "본문 바이트는 자식 파일로 무손실 이전")
    return Ctx(before, after, build_cp(), children, build_baseline(), con)


def resolve_file_factory(engine, ctx, *, include_children: bool = True):
    """INV-S3 정의역 = `strip_stub(after.§n) ∪ children[n]` (§8.4 R3 P2).

    엔진 계약: `resolve_file(domain: dict) -> str`.
    `include_children=False` 는 M-DOMAIN — 자식 파일을 정의역에서 제외한 변형이다.
    """
    kids = children_by_section(engine, ctx) if include_children else {}

    def resolve(domain) -> str:
        key = str(domain["file"])
        text = ctx["cp_after"] if key == "CP" else ctx["story_after"]
        return engine.reassemble_document(text, kids)
    return resolve


def run_inv_s3(engine, ctx, *, include_children: bool = True):
    return engine.check_inv_s3(
        ctx["baseline"], resolve_file_factory(engine, ctx, include_children=include_children))


def run_inv_s1(engine, ctx):
    return engine.check_inv_s1(ctx["story_before"], ctx["story_after"],
                               children_by_section(engine, ctx))


def run_inv_s2(engine, ctx, theta_move: int = 4096, reason_code=None):
    return engine.check_inv_s2(ctx["story_before"], ctx["story_after"], theta_move, reason_code)


def run_inv_s6(engine, ctx):
    return engine.check_inv_s6(dict(ctx["children"]))


def run_anchor(engine, ctx):
    out = list(engine.check_anchor_integrity(ctx["story_after"], label=STORY_PATH))
    for path in sorted(ctx["children"]):
        out.extend(engine.check_anchor_integrity(ctx["children"][path], label=path))
    return out


def _leg(v):
    leg = getattr(v, "leg", None)
    return leg if leg else "-"


def _dom(v):
    dom = getattr(v, "domain", None)
    return dom if dom else "-"


def red_vector(verdicts) -> frozenset:
    """(정의역, leg) 단위 RED 벡터 — 전역 스칼라 금지 (C-7 / C-13)."""
    return frozenset((_dom(v), _leg(v)) for v in verdicts
                     if getattr(v, "status", None) == "RED")


def red_domains(verdicts) -> frozenset:
    return frozenset(_dom(v) for v in verdicts if getattr(v, "status", None) == "RED")


def status_vector(verdicts) -> tuple:
    """전 verdict 의 (name, domain, leg, fired, status) 정렬 벡터 — boolean 단독 금지."""
    return tuple(sorted(
        (str(getattr(v, "name", "")), _dom(v), _leg(v),
         bool(getattr(v, "fired", False)), str(getattr(v, "status", "")))
        for v in verdicts))


def red_count(verdicts) -> int:
    return sum(1 for v in verdicts if getattr(v, "status", None) == "RED")


def undetermined_domains(verdicts) -> frozenset:
    return frozenset(_dom(v) for v in verdicts
                     if getattr(v, "status", None) == "UNDETERMINED")


# ---------------------------------------------------------------------------
# 6. mutant 구성기 (§8.2)
# ---------------------------------------------------------------------------

def ctx_card_in() -> Ctx:
    """M-CARD-IN — 정의역 **내** 보상 쌍: RTM 의 AC-12 → AC-2 치환.
    출현수 21 불변(leg2 GREEN) ∧ 집합 21→20(leg1 RED). leg1 의 독립 falsifier."""
    rows = ["AC-2" if ac == "AC-12" else ac for ac, _ in RTM_NAMED]
    return canonical_ctx().copy_with(cp_after=build_cp(rtm_rows=rows))


def ctx_card_value() -> Ctx:
    """M-CARD-VALUE — CORPUS 값만 오염(S4.KB 12.29 → 9.85). ID·개수 온전, leg3 단독 RED."""
    cells = [(s, ("9.85" if s == "4" else kb), pct) for s, kb, pct in CORPUS_CELLS]
    return canonical_ctx().copy_with(
        story_after=build_story(section_4_kwargs={"corpus_cells": cells}))


def ctx_card_cross() -> Ctx:
    """M-S3-NOSPLIT — 정의역 **간** 상쇄를 **분할 없는 일반 편집**으로 주입."""
    rows = [ac for ac, _ in RTM_NAMED if ac != "AC-7"]
    return canonical_ctx().copy_with(cp_after=build_cp(rtm_rows=rows))


def ctx_card_cross_split() -> Ctx:
    """M-CARD-CROSS — 같은 상쇄 주입을 **분할 커밋**(anchor_delta ≠ ∅) 위에서."""
    rows = [ac for ac, _ in RTM_NAMED if ac != "AC-7"]
    return split_ctx().copy_with(cp_after=build_cp(rtm_rows=rows))


def ctx_dup_row() -> Ctx:
    """M-DUP-ROW — RTM 기존 AC-2 행 정확 복제. 집합 불변 ∧ 출현수 21→22. leg2 유일 falsifier."""
    rows = [ac for ac, _ in RTM_NAMED]
    rows.insert(rows.index("AC-2") + 1, "AC-2")
    return canonical_ctx().copy_with(cp_after=build_cp(rtm_rows=rows))


def ctx_equiv() -> Ctx:
    """M-EQUIV — 표기 등가변형 2계열: RTM 헤더 셀 공백 변형 ∧ §5.3 데이터 행 padding 제거."""
    return canonical_ctx().copy_with(
        cp_after=build_cp(rtm_header="|AC|tier|named test|", rtm_pad=False),
        story_after=build_story(section_5_kwargs={"pad": False}))


def ctx_sec5_stub() -> Ctx:
    r"""M-SEC5 — §5 stub 화 (`AC-\d+` 토큰 0). 현행 게이트는 rc=0 조용한 PASS 였다."""
    return canonical_ctx().copy_with(
        story_after=build_story(section_5_kwargs={"stubbed": True}))


def ctx_global_sibling() -> Ctx:
    """M-GLOBAL — 전 정의역 AC-11 → AC-99 (형제 site 양쪽에서 검출돼야 한다)."""
    rows = ["AC-99" if ac == "AC-11" else ac for ac, _ in RTM_NAMED]
    story_rows = ["AC-99" if ac == "AC-11" else ac for ac in ALL_AC]
    return canonical_ctx().copy_with(
        cp_after=build_cp(rtm_rows=rows),
        story_after=build_story(section_5_kwargs={"ac_rows": story_rows}))


def baseline_anchor_loose() -> dict:
    r"""M-ANCHOR-LOOSE — span_anchor 를 `^\|`(절의 첫 표)로 느슨화 (제거 축)."""
    bl = build_baseline()
    for name in ("CORPUS", "STORY_S53_AC_TABLE", "CP_S81_RTM"):
        bl["domains"][name]["span_anchor"] = r"^\|"
    return bl


def baseline_global_rule() -> dict:
    """M-GLOBALRULE — 정의역 선언을 R2 의 전역 표-앵커 규칙으로 회귀.

    실 회귀 형상 = 산문 줄 앵커를 표 앵커로 되돌린다 (CP §1 은 `|` 시작 줄이 0개).
    """
    bl = build_baseline()
    bl["domains"]["CP_S1_MAPPING"]["span_kind"] = "table"
    bl["domains"]["CP_S1_MAPPING"]["span_anchor"] = r"^\|"
    return bl


def baseline_basis_global() -> dict:
    """M-BASIS-RAW — cardinality_basis 를 전역 `cell_count` 로 회귀.

    AC-ID 착지면에 정량 셀 기준을 적용하면 출현수가 아니라 **중복제거 집합 크기**가 되어
    `M-DUP-ROW`(집합 불변 ∧ 출현수 +1) 를 leg2 가 놓친다 — 기준 전역화의 실 피해.
    """
    bl = build_baseline()
    for name in ENFORCED_DOMAINS:
        bl["domains"][name]["cardinality_basis"] = "cell_count"
    return bl


def ctx_fence(*, fence_aware: bool, inject: bool) -> Ctx:
    """M-FENCE-INJECT (R4 재구성본 — 주입 축).

    대조군 = 펜스 안 기존 `# 인자: TREE = …` 줄을 **제거한** fixture. 그 위에 `## 5.` 를 주입한다.
    종전 정의(정본 위 주입)는 대조군이 이미 RED 라 **등가 mutant** 였다.
    """
    story = build_story(section_4_kwargs={"fence_inner_line": False,
                                          "fence_inject_heading": inject})
    bl = build_baseline()
    for name in ENFORCED_DOMAINS:
        bl["domains"][name]["fence_aware"] = fence_aware
    return Ctx(story, story, build_cp(), {}, bl,
               f"펜스 내 `# 인자` 줄 제거 fixture + inject={inject} + fence_aware={fence_aware}")


def ctx_preexist_pr2():
    """M-PREEXIST — PR1 오염 착지 → PR2 정상 편집(오염 잔존).

    차분면(before/after)은 PR2 에서 **GREEN(영구 무장해제)**, baseline 면은 **RED 지속**.
    """
    cells = [(s, ("9.85" if s == "4" else kb), pct) for s, kb, pct in CORPUS_CELLS]
    polluted = build_story(section_4_kwargs={"corpus_cells": cells})
    polluted_pr2 = build_story(section_4_kwargs={"corpus_cells": cells},
                               section_7_extra="정상 산문 편집 1줄 추가 (PR2).\n")
    ctx = Ctx(polluted, polluted_pr2, build_cp(), {}, build_baseline(),
              "PR1 오염 착지(S4.KB 12.29→9.85) → PR2 §7 산문 1줄 append, "
              "오염은 before·after 양쪽에 동일 잔존")
    return ctx, (polluted, polluted_pr2)


def ctx_e1_heading_demote() -> Ctx:
    """M-E1 — `## §9.` → `### §9.` 강등(+1 B). 섹션 로스터에서 §9 소실 ⇒ 결손(RED)."""
    return split_ctx().copy_with(
        story_after=build_story(split_9=True, split_10=True, heading_demote_9=True))


def ctx_e2_zwsp() -> Ctx:
    """M-E2 — 자식 본문에 U+200B 3 B 삽입. digest 불일치 → INV-S1 RED."""
    ctx = split_ctx()
    ch = dict(ctx["children"])
    ch[child_path(SPLIT_ID)] = build_child(
        "9", SPLIT_ID, SECTION_9_BODY.replace("채택", "채​택", 1))
    return ctx.copy_with(children=ch)


def ctx_e3_fence_phantom() -> Ctx:
    """M-E3 — 자식 본문에 코드펜스 phantom heading 65 B 주입. digest 불일치 → INV-S1 RED."""
    ctx = split_ctx()
    phantom = "```text\n## §9. phantom heading — 펜스 안 위장 구간\n```\n"
    ch = dict(ctx["children"])
    ch[child_path(SPLIT_ID)] = build_child("9", SPLIT_ID, SECTION_9_BODY + phantom)
    return ctx.copy_with(children=ch)


def ctx_anchor_malformed() -> Ctx:
    """§8.3 행 2 — 앵커 오형식(`id=` 누락). 3속성 중 '명시' 위반."""
    ctx = split_ctx()
    bad = ctx["story_after"].replace(
        f"<!-- cfp-split:begin section=9 id={SPLIT_ID} -->",
        "<!-- cfp-split:begin section=9 -->", 1)
    return ctx.copy_with(story_after=bad)


def ctx_anchor_unpaired() -> Ctx:
    """§8.3 행 2 — 앵커 미쌍(end 제거). 3속성 중 '쌍' 위반."""
    ctx = split_ctx()
    bad = ctx["story_after"].replace(f"<!-- cfp-split:end id={SPLIT_ID} -->\n", "", 1)
    return ctx.copy_with(story_after=bad)


def ctx_anchor_duplicate() -> Ctx:
    """§8.3 행 2 — 앵커 중복(같은 id 의 begin 2회). 3속성 중 '유일' 위반."""
    ctx = split_ctx()
    beg = f"<!-- cfp-split:begin section=9 id={SPLIT_ID} -->"
    return ctx.copy_with(story_after=ctx["story_after"].replace(beg, beg + "\n" + beg, 1))


def ctx_anchor_no_section() -> Ctx:
    """§8.3 행 2 — begin 앵커에 `section=` 누락 (오형식 2형). 강제 진입 fixture."""
    ctx = split_ctx()
    bad = ctx["story_after"].replace(
        f"<!-- cfp-split:begin section=9 id={SPLIT_ID} -->",
        f"<!-- cfp-split:begin id={SPLIT_ID} -->", 1)
    return ctx.copy_with(story_after=bad)


def ctx_anchor_dup_end() -> Ctx:
    """§8.3 행 2 — 같은 id 의 end 앵커 2회 (유일성 위반, end 측). 강제 진입 fixture."""
    ctx = split_ctx()
    end = f"<!-- cfp-split:end id={SPLIT_ID} -->"
    return ctx.copy_with(story_after=ctx["story_after"].replace(end, end + "\n" + end, 1))


def ctx_stray_end_only() -> Ctx:
    """anchor_delta 에 section 해결 불가 앵커(end)만 존재 — 강제 진입 fixture.

    end 앵커는 `section=` 을 갖지 않으므로 `sections_of(delta) = ∅` 이 되고,
    검사 대상 섹션이 하나도 없는 채로 발화한다 (조용한 통과로 빠지면 결함).
    """
    story = build_story()
    stray = story.replace("## §11. 데이터 마이그레이션",
                          f"<!-- cfp-split:end id={SPLIT_ID} -->\n\n## §11. 데이터 마이그레이션", 1)
    return Ctx(story, stray, build_cp(), {}, build_baseline(),
               "정본 말미에 짝 없는 end 앵커 1줄만 추가 — anchor_delta 는 비지 않으나 "
               "section 해결 가능한 앵커가 0")


def _move_bytes_9_to_7(n_lines: int, *, extra_append_bytes: int = 0) -> Ctx:
    """E-4 보상 이동 — §9 에서 n_lines 를 떼어 §7 로 옮긴다. 총량 Δ = extra_append_bytes."""
    lines = SECTION_9_BODY.split("\n")
    head, moved = lines[:-(n_lines + 1)], lines[-(n_lines + 1):-1]
    body9 = "\n".join(head) + "\n"
    moved_text = "\n".join(moved) + "\n"
    # 총량 Δ 를 정확히 extra_append_bytes 로 맞춘다 (마지막 1 B 는 개행).
    extra = ("x" * (extra_append_bytes - 1) + "\n") if extra_append_bytes else ""
    before = build_story()
    after = build_story(section_9_body=body9, section_7_extra=moved_text + extra)
    return Ctx(before, after, build_cp(), {}, build_baseline(),
               f"§9 말미 {n_lines}줄({len(moved_text.encode('utf-8'))} B)을 §7 로 이동, "
               f"추가 append {extra_append_bytes} B ⇒ 총량 Δ = {extra_append_bytes} B")


def ctx_e4_compensating_move() -> Ctx:
    """M-E4 — 보상 이동(0 B, 총량 보존). anchor_delta = ∅ ⇒ INV-S2 전담, INV-S1 정의상 미발화."""
    return _move_bytes_9_to_7(160)


def ctx_mix_min() -> Ctx:
    """M-MIX-min — 섹션 간 이동 + append **65 B**. θ_total conjunct 부재 확인 (R2 P0-A)."""
    return _move_bytes_9_to_7(160, extra_append_bytes=65)


def ctx_append_ctl(n_bytes: int) -> Ctx:
    """M-APPEND-CTL — 순수 정상 append. INV-S2 **발화 후 통과**(미발화를 통과로 계상 금지)."""
    before = build_story()
    after = build_story(section_9_extra="y" * n_bytes)
    return Ctx(before, after, build_cp(), {}, build_baseline(),
               f"§9 말미에 {n_bytes} B 순수 append, 감소 섹션 0")


def ctx_margin(n_lines: int = 12) -> Ctx:
    """M-MARGIN — 구간 내부 무관 N줄 삽입. GREEN 유지 (positive control 페어링 필수)."""
    before = build_story()
    after = build_story(section_7_extra=_filler("§7 무관", n_lines))
    return Ctx(before, after, build_cp(), {}, build_baseline(),
               f"§7 구간 내부에 무관 {n_lines}줄 삽입 (감소 섹션 0, 앵커 변화 0)")


def ctx_nested_child() -> Ctx:
    """AC-12 / INV-S6 — 자식 안에 split 마커가 있으면 깊이 2 ⇒ RED."""
    ctx = split_ctx()
    ch = dict(ctx["children"])
    ch[child_path(SPLIT_ID)] = build_child("9", SPLIT_ID, SECTION_9_BODY, nested_marker=True)
    return ctx.copy_with(children=ch)


def ctx_dangling() -> Ctx:
    """§8.3 행 5 — dangling pointer(자식 파일 부재). 정보 손실 축 ⇒ fail-closed."""
    ctx = split_ctx()
    keep = child_path(SPLIT_ID_S10)
    return ctx.copy_with(children={keep: ctx["children"][keep]})


def ctx_self_pointer() -> Ctx:
    """§8.3 행 5 — 자기 포인터(child == parent) ⇒ 분할 없음으로 환원."""
    ctx = split_ctx()
    ch = dict(ctx["children"])
    ch[child_path(SPLIT_ID)] = build_child("9", SPLIT_ID, ctx["story_after"])
    return ctx.copy_with(children=ch)


# ---------------------------------------------------------------------------
# 7. M-SUTURE / dark-path probe — 엔진 판정 줄 소스 변형
# ---------------------------------------------------------------------------

def _is_check_fn(name) -> bool:
    return bool(name) and name.startswith("check_")


def _contains_red(node) -> bool:
    import ast
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and sub.value == "RED":
            return True
    return False


def suture_sites(source: str) -> list:
    """RED 를 방출하는 `if` 판정 줄을 열거한다 (`check_*` 함수 안). 각 site = 봉합 지점."""
    import ast
    tree = ast.parse(source)
    sites = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or not _is_check_fn(fn.name):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.If) and _contains_red(node):
                sites.append((fn.name, node.lineno))
    return sorted(set(sites))


PROBE_PROLOGUE = (
    "_CFP_PROBE = {}\n"
    "def _cfp_probe(site, value):\n"
    "    hit, tot = _CFP_PROBE.get(site, (0, 0))\n"
    "    _CFP_PROBE[site] = (hit + (1 if value else 0), tot + 1)\n"
    "    return value\n"
)


def _insert_after_header(tree, nodes):
    """docstring · `from __future__` 뒤에 삽입 (선두 삽입 시 SyntaxError)."""
    import ast
    at = 0
    for i, node in enumerate(tree.body):
        is_doc = (i == 0 and isinstance(node, ast.Expr)
                  and isinstance(node.value, ast.Constant)
                  and isinstance(node.value.value, str))
        is_future = isinstance(node, ast.ImportFrom) and node.module == "__future__"
        if is_doc or is_future:
            at = i + 1
        else:
            break
    tree.body[at:at] = nodes
    return tree


def make_probed_source(source: str) -> str:
    """§8.10 dark-path 술어 — 각 판정 site 의 조건이 **참이 된 적이 있는가** 를 계측한다.

    한 번도 참이 안 된 site = 강제 진입 fixture 부재 = dark path. 미실행을 GREEN 으로 계상 금지.
    """
    import ast

    class Probe(ast.NodeTransformer):
        def __init__(self):
            self._fn = None

        def visit_FunctionDef(self, node):  # noqa: N802 - ast API
            prev, self._fn = self._fn, node.name
            self.generic_visit(node)
            self._fn = prev
            return node

        def visit_If(self, node):  # noqa: N802 - ast API
            self.generic_visit(node)
            if _is_check_fn(self._fn) and _contains_red(node):
                node.test = ast.Call(
                    func=ast.Name(id="_cfp_probe", ctx=ast.Load()),
                    args=[ast.Constant(value=f"{self._fn}:{node.lineno}"), node.test],
                    keywords=[])
            return node

    tree = Probe().visit(ast.parse(source))
    tree = _insert_after_header(tree, ast.parse(PROBE_PROLOGUE).body)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def make_sutured_source(source: str, target=None) -> str:
    """지정 site(또는 전체)의 `if <test>:` 를 `if False:` 로 치환한 소스를 반환한다."""
    import ast

    class Suture(ast.NodeTransformer):
        def __init__(self):
            self.applied = 0
            self._fn = None

        def visit_FunctionDef(self, node):  # noqa: N802 - ast API
            prev, self._fn = self._fn, node.name
            self.generic_visit(node)
            self._fn = prev
            return node

        def visit_If(self, node):  # noqa: N802 - ast API
            self.generic_visit(node)
            if _is_check_fn(self._fn) and _contains_red(node):
                if target is None or (self._fn, node.lineno) == target:
                    node.test = ast.Constant(value=False)
                    self.applied += 1
            return node

    tree = ast.parse(source)
    tr = Suture()
    tree = tr.visit(tree)
    ast.fix_missing_locations(tree)
    if tr.applied == 0:
        raise AssertionError(f"M-SUTURE 주입 지점 0 — target={target}")
    return ast.unparse(tree)


# ---------------------------------------------------------------------------
# 8. 배터리 — per-mutant 판정 벡터 (boolean 단독 금지)
# ---------------------------------------------------------------------------

class MutantResult(dict):
    def __init__(self, mid, axis, control, injected, verdict, control_red, injected_red,
                 vector, construction, tree_sha, domain, note=""):
        super().__init__(
            id=mid, axis=axis, control=control, injected=injected, verdict=verdict,
            control_red_count=control_red, injected_red_count=injected_red,
            vector=sorted(f"{d}:{l}" for d, l in vector) if vector else [],
            domains=sorted({d for d, _l in vector}) if vector else [],
            construction=construction, tree_sha=tree_sha, media=MEDIA,
            domain=domain, note=note)


def _verdict_word(red: int) -> str:
    return "RED" if red else "GREEN"


def _match(ctl_red, inj_red, inj_vec, *, expect_red, exact_vec=None, exact_domains=None) -> str:
    if ctl_red != 0:
        return "등가 mutant(대조군 RED)"
    if expect_red and inj_red == 0:
        return "불일치(주입 GREEN)"
    if not expect_red and inj_red != 0:
        return "불일치(false RED)"
    if exact_vec is not None and frozenset(inj_vec) != frozenset(exact_vec):
        return "불일치(leg 벡터)"
    if exact_domains is not None and {d for d, _l in inj_vec} != set(exact_domains):
        return "불일치(정의역)"
    return "기대일치"


def run_battery(engine) -> dict:
    """전 mutant 를 대조군/주입 쌍으로 실행해 5-tuple 레코드를 산출한다.

    반환 = {mutant_id: MutantResult}. 판정은 **개수 + (정의역, leg) 벡터** — boolean 단독 금지.
    """
    out = {}
    ctl_ctx = canonical_ctx()
    split_base = split_ctx()

    def add(mid, axis, ctl_verdicts, inj_verdicts, construction, tree, domain, *,
            expect_red=True, exact_vec=None, exact_domains=None, note=""):
        cr, ir = red_count(ctl_verdicts), red_count(inj_verdicts)
        iv = red_vector(inj_verdicts)
        out[mid] = MutantResult(
            mid, axis, _verdict_word(cr), _verdict_word(ir),
            _match(cr, ir, iv, expect_red=expect_red, exact_vec=exact_vec,
                   exact_domains=exact_domains),
            cr, ir, iv, construction, tree, domain, note)

    # --- INV-S3 축 ---------------------------------------------------------
    s3_ctl = run_inv_s3(engine, ctl_ctx)

    def add_s3(mid, ctx_inj, construction, *, ctl_ctx_=None, include_children=True, **kw):
        ctl_v = s3_ctl if ctl_ctx_ is None else run_inv_s3(engine, ctl_ctx_)
        inj_v = run_inv_s3(engine, ctx_inj, include_children=include_children)
        add(mid, "INV-S3", ctl_v, inj_v, construction,
            synthetic_sha(ctx_inj["story_after"], ctx_inj["cp_after"]),
            "INV-S3 4 정의역 × 3 leg", **kw)

    add_s3("M-CARD-IN", ctx_card_in(),
           "RTM 15 normative 행 중 `AC-12` 셀을 `AC-2` 로 치환 — 출현수 21 불변 ∧ 집합 21→20",
           exact_vec={("CP_S81_RTM", "leg1")})
    add_s3("M-CARD-VALUE", ctx_card_value(),
           "§4.2.2a 귀속표 데이터 1행의 §4 셀 `12.29 KB` → `9.85 KB` — 셀ID·개수 온전, 값만 오염",
           exact_vec={("CORPUS", "leg3")})
    add_s3("M-DUP-ROW", ctx_dup_row(),
           "RTM 기존 `AC-2` 행을 정확 복제해 바로 아래에 삽입 — 집합 불변 ∧ 출현수 21→22",
           exact_vec={("CP_S81_RTM", "leg2")})
    add_s3("M-CARD-CROSS", ctx_card_cross_split(),
           "**분할 커밋**(§9·§10 앵커 2쌍, anchor_delta ≠ ∅) 위에서 RTM 의 `AC-7` 행만 삭제 "
           "— CP §1 산문에는 잔존하므로 전역 집합은 불변",
           ctl_ctx_=split_base, exact_vec={("CP_S81_RTM", "leg1"), ("CP_S81_RTM", "leg2")})
    add_s3("M-S3-NOSPLIT", ctx_card_cross(),
           "동일 상쇄 주입을 **분할 없는 일반 편집**으로(앵커 0쌍, anchor_delta = ∅) "
           "— 발화 조건이 분할 커밋 전용이면 여기서 NOT_FIRED 로 빠져나간다",
           exact_vec={("CP_S81_RTM", "leg1"), ("CP_S81_RTM", "leg2")})
    add_s3("M-EQUIV", ctx_equiv(),
           "표기 등가변형 2계열 — RTM 헤더 셀 공백 제거(`|AC|tier|`) ∧ §5.3 데이터 행 padding 제거",
           expect_red=False)
    add_s3("M-SEC5", ctx_sec5_stub(),
           r"§5 전체를 `*(내용 생략)*` stub 으로 치환 — `AC-\d+` 토큰 0",
           exact_domains={"STORY_S53_AC_TABLE"})
    add_s3("M-GLOBAL", ctx_global_sibling(),
           "전 정의역에서 `AC-11` → `AC-99` 치환 (RTM ∧ Story §5.3 형제 site 동시)",
           exact_domains={"CP_S81_RTM", "STORY_S53_AC_TABLE"})
    add_s3("M-ANCHOR-LOOSE", ctl_ctx.copy_with(baseline=baseline_anchor_loose()),
           r"span_anchor 를 `^\|`(절의 첫 표)로 느슨화 — §4.2.2a 는 표 3개라 "
           "첫 표(슬라이싱 규약표)를 문다. §5.3 은 표가 하나뿐이라 vacuous",
           exact_domains={"CORPUS"})
    add_s3("M-GLOBALRULE", ctl_ctx.copy_with(baseline=baseline_global_rule()),
           "CP §1 정의역 선언을 산문 줄 앵커에서 전역 표 앵커(`table` + `^\\|`)로 회귀 "
           "— CP §1 은 `|` 시작 줄이 0개",
           exact_domains={"CP_S1_MAPPING"})
    add_s3("M-BASIS-RAW", ctx_dup_row().copy_with(baseline=baseline_basis_global()),
           "cardinality_basis 를 전역 `cell_count` 로 회귀한 뒤 M-DUP-ROW 주입 "
           "— 출현수 대신 중복제거 집합을 세므로 leg2 가 복제 행을 놓친다",
           expect_red=False,
           note="기준 전역화의 실 피해 = **검출 상실**. 정의역별 basis 선언에서는 "
                "같은 주입이 CP_S81_RTM:leg2 RED 다 (M-DUP-ROW 참조)")

    # M-DOMAIN — 자식 파일 제외. §4 분할 fixture 위에서만 판별력이 생긴다.
    ctx4 = split_ctx(split_4=True)
    add("M-DOMAIN", "INV-S3", run_inv_s3(engine, ctx4),
        run_inv_s3(engine, ctx4, include_children=False),
        "§4를 자식으로 분할한 fixture 에서 resolve_file 이 children 을 제외 "
        "⇒ CORPUS 재조립이 결손 (조용한 skip 아님)",
        synthetic_sha(ctx4["story_after"]), "INV-S3 CORPUS")

    # M-FENCE-INJECT — 4셀 매트릭스 (fence_aware × inject)
    fence = {}
    for fa in (False, True):
        for inj in (False, True):
            v = run_inv_s3(engine, ctx_fence(fence_aware=fa, inject=inj))
            fence[(fa, inj)] = (red_count(v), red_vector(v))
    add("M-FENCE-INJECT", "INV-S3", [], [],
        "대조군 = §4.2.2a 펜스 안 기존 `# 인자: TREE = …` 줄을 **제거한** fixture"
        "(정본 위 주입은 대조군이 이미 RED 라 등가 mutant 였다). "
        "주입 = 그 펜스 안에 `## 5. phantom heading` 1줄 추가 ⇒ 절 종결점이 주입줄로 이동",
        synthetic_sha(ctx_fence(fence_aware=False, inject=True)["story_after"]),
        "INV-S3 CORPUS")
    out["M-FENCE-INJECT"].update(
        control_red_count=fence[(False, False)][0],
        injected_red_count=fence[(False, True)][0],
        control=_verdict_word(fence[(False, False)][0]),
        injected=_verdict_word(fence[(False, True)][0]),
        vector=sorted(f"{d}:{l}" for d, l in fence[(False, True)][1]),
        domains=sorted({d for d, _l in fence[(False, True)][1]}),
        verdict=("기대일치" if (fence[(False, False)][0] == 0 and fence[(False, True)][0] > 0
                            and fence[(True, False)][0] == 0 and fence[(True, True)][0] == 0)
                 else "불일치"),
        fence_matrix={f"fence_aware={fa},inject={inj}": _verdict_word(r)
                      for (fa, inj), (r, _v) in fence.items()})

    # M-PREEXIST — 판정면이 baseline 임을 반증
    pre_ctx, (pr1_text, pr2_text) = ctx_preexist_pr2()
    diff_green = _diff_surface_green(engine, pr1_text, pr2_text)
    add("M-PREEXIST", "판정면", s3_ctl, run_inv_s3(engine, pre_ctx),
        pre_ctx["construction"], synthetic_sha(pr2_text), "INV-S3 CORPUS",
        exact_vec={("CORPUS", "leg3")},
        note=f"차분면(before/after) PR2 판정 = {'GREEN(영구 무장해제)' if diff_green else 'RED'}")

    # --- 앵커 3속성 축 (check_anchor_integrity) ----------------------------
    anchor_ctl = run_anchor(engine, split_base)
    for mid, ctx_fn, con in (
        ("M-ANCHOR-MALFORMED", ctx_anchor_malformed,
         "§9 begin 앵커에서 `id=CFP-2986-S1` 을 제거 (오형식) — 3속성 '명시' 위반"),
        ("M-ANCHOR-UNPAIRED", ctx_anchor_unpaired,
         "§9 end 앵커 줄 전체 삭제 (미쌍) — 3속성 '쌍' 위반"),
        ("M-ANCHOR-DUP", ctx_anchor_duplicate,
         "§9 begin 앵커를 같은 id 로 1줄 복제 (중복) — 3속성 '유일' 위반"),
        ("M-ANCHOR-NOSECTION", ctx_anchor_no_section,
         "§9 begin 앵커에서 `section=9` 만 제거 (id 는 유지) — 오형식 2형"),
        ("M-ANCHOR-DUPEND", ctx_anchor_dup_end,
         "§9 end 앵커를 같은 id 로 1줄 복제 — 유일성 위반(end 측)"),
    ):
        add(mid, "INV-ANCHOR", anchor_ctl, run_anchor(engine, ctx_fn()), con,
            synthetic_sha(split_base["story_after"]), "INV-ANCHOR parent+children")

    # --- INV-S1 축 ---------------------------------------------------------
    s1_ctl = run_inv_s1(engine, split_base)
    for mid, ctx_fn, con in (
        ("M-E1", ctx_e1_heading_demote,
         "분할 커밋 parent 의 `## §9. 분기 선택` → `### §9. 분기 선택` (+1 B) "
         "— 섹션 로스터에서 §9 소실"),
        ("M-E2", ctx_e2_zwsp,
         "자식 본문 첫 단어 사이에 U+200B(3 B) 삽입 — 재조립 digest 불일치"),
        ("M-E3", ctx_e3_fence_phantom,
         "자식 말미에 코드펜스 phantom heading 블록(65 B) 추가 — 재조립 digest 불일치"),
        ("M-DANGLING", ctx_dangling,
         "분할 커밋에서 §9 자식만 제거(dangling pointer) — §10 은 잔존"),
        ("M-SELFPTR", ctx_self_pointer,
         "§9 자식 파일 본문을 parent 전문으로 치환 (child == parent) — E-7 자기 포인터"),
    ):
        add(mid, "INV-S1", s1_ctl, run_inv_s1(engine, ctx_fn()), con,
            synthetic_sha(split_base["story_after"]), "INV-S1 §9 재조립 digest")

    # --- INV-S2 축 ---------------------------------------------------------
    add("M-STRAYEND", "INV-S1", s1_ctl, run_inv_s1(engine, ctx_stray_end_only()),
        ctx_stray_end_only()["construction"],
        synthetic_sha(split_base["story_after"]), "INV-S1 anchor_delta")

    s2_ctl = run_inv_s2(engine, ctx_append_ctl(1000))
    for mid, ctx_obj in (("M-E4", ctx_e4_compensating_move()), ("M-MIX-min", ctx_mix_min())):
        add(mid, "INV-S2", s2_ctl, run_inv_s2(engine, ctx_obj), ctx_obj["construction"],
            synthetic_sha(ctx_obj["story_after"]), "INV-S2 §9↔§7 페어")

    for n in (1000, 50000):
        ctx_a = ctx_append_ctl(n)
        v = run_inv_s2(engine, ctx_a)
        add(f"M-APPEND-CTL-{n}", "INV-S2", s2_ctl, v, ctx_a["construction"],
            synthetic_sha(ctx_a["story_after"]), "INV-S2", expect_red=False,
            note=f"fired={any(getattr(x, 'fired', False) for x in v)} "
                 "(발화 후 통과여야 함 — 미발화를 통과로 계상 금지)")

    # 폐쇄 enum 밖 자유서술 reason_code 는 강등되지 않는다 (자기선언 무력화 차단)
    free_ctx = ctx_e4_compensating_move()
    add("M-REASON-FREEFORM", "INV-S2", s2_ctl,
        run_inv_s2(engine, free_ctx, reason_code="그냥 정리했음"),
        free_ctx["construction"] + " + `reason_code` 를 폐쇄 enum 밖 자유서술로 선언",
        synthetic_sha(free_ctx["story_after"]), "INV-S2",
        note="폐쇄 enum(SECTION_REORG / AUTHORED_CONSOLIDATION) 선언 시에만 SIGNAL 강등")

    # M-MARGIN — positive control 페어링 (짝의 RED 없으면 판정 불가)
    m_ctx = ctx_margin()
    mv = run_inv_s2(engine, m_ctx)
    paired_red = out["M-E4"]["injected_red_count"]
    out["M-MARGIN"] = MutantResult(
        "M-MARGIN", "INV-S2", "GREEN", _verdict_word(red_count(mv)),
        ("기대일치" if (red_count(mv) == 0 and paired_red > 0)
         else ("판정 불가(짝의 RED 부재)" if paired_red == 0 else "불일치")),
        0, red_count(mv), red_vector(mv), m_ctx["construction"],
        synthetic_sha(m_ctx["story_after"]), "INV-S2",
        note=f"paired positive control = M-E4 (RED {paired_red}건)")

    # --- INV-S6 축 ---------------------------------------------------------
    add("M-DEPTH2", "INV-S6", run_inv_s6(engine, split_base),
        run_inv_s6(engine, ctx_nested_child()),
        "자식 파일 선두에 `cfp-split:begin section=99` 앵커 쌍 추가 (깊이 2)",
        synthetic_sha(split_base["story_after"]), "INV-S6 children")

    # --- O5 스캔 정의역 축 (check_scan_domain) -----------------------------
    expected_set = {STORY_PATH, child_path(SPLIT_ID)}
    ctl_o5 = engine.check_scan_domain(set(expected_set), set(expected_set),
                                      set(expected_set), len(expected_set),
                                      carrier_set=set(expected_set))
    narrowed = {STORY_PATH}
    inj_o5 = engine.check_scan_domain(set(narrowed), set(narrowed), set(expected_set),
                                      len(expected_set), carrier_set=set(narrowed))
    add("M-SCANGLOB", "O5", ctl_o5, inj_o5,
        "트리거·검사·carrier glob 을 **같이** 좁혀 자식 경로를 스캔 집합에서 제외 "
        "(trigger_set == scan_set 은 유지 ⇒ (a) 는 통과) — 대칭 축소라 "
        "상대 동일성만으로는 무감하고 (b) 절대 기대집합 대조만이 잡는다",
        synthetic_sha(STORY_PATH), "O5 scan_set", exact_vec={("-", "b")})

    asym = engine.check_scan_domain({STORY_PATH, child_path(SPLIT_ID)}, {STORY_PATH},
                                    set(expected_set), len(expected_set),
                                    carrier_set=set(expected_set))
    add("M-SCAN-ASYM", "O5", ctl_o5, asym,
        "트리거 glob 은 자식을 매치하는데 검사 glob 은 못 매치하도록 **깊이 비대칭** 주입 "
        "(git pathspec 은 `*` 가 `/` 를 넘고 Actions glob 은 안 넘는 실물 형상 — CP §3.5)",
        synthetic_sha(STORY_PATH), "O5 scan_set", exact_vec={("-", "a")})

    card = engine.check_scan_domain(set(expected_set), set(expected_set),
                                    set(expected_set), len(expected_set) + 1,
                                    carrier_set=set(expected_set))
    add("M-SCAN-CARD", "O5", ctl_o5, card,
        "기대집합 자체의 cardinality 선언(`declared_scan_count`)만 1 어긋나게 주입 "
        "— (a)(b) 는 통과하므로 (c) 만이 잡는다",
        synthetic_sha(STORY_PATH), "O5 scan_set", exact_vec={("-", "c")})

    out["_tree"] = synthetic_sha(ctl_ctx["story_after"], ctl_ctx["cp_after"])
    return out


def _diff_surface_green(engine, before_text, after_text) -> bool:
    """차분면(before/after) 판정 대리 — 오염이 양쪽에 동일 존재하면 차분 0 ⇒ GREEN."""
    dom = build_baseline()["domains"]["CORPUS"]
    try:
        return engine.extract_domain(dom, before_text) == engine.extract_domain(dom, after_text)
    except Exception:  # noqa: BLE001 - 대리 판정 실패는 값 위조보다 낫다
        return False


def format_report(results: dict) -> str:
    """5-tuple(construction 포함) 레코드를 사람이 읽는 표로 인쇄한다 (C-28)."""
    lines = ["", "=" * 100,
             "[CFP-2986 mutant 배터리 실행 확인 — 5-tuple "
             "{값, 기준 트리 SHA, 매체, 정의역, construction}]",
             "=" * 100]
    for mid, r in results.items():
        if mid.startswith("_"):
            continue
        lines.append(f"{mid:<20} 축={r['axis']:<10} 대조군={r['control']:<6} "
                     f"주입={r['injected']:<6} 판정={r['verdict']}")
        lines.append(f"  값: 대조군 RED {r['control_red_count']} / 주입 RED "
                     f"{r['injected_red_count']} | 벡터 {r['vector']}")
        lines.append(f"  tree={r['tree_sha']} | 매체={r['media']} | 정의역={r['domain']}")
        lines.append(f"  construction: {r['construction']}")
        if r.get("note"):
            lines.append(f"  note: {r['note']}")
        if r.get("fence_matrix"):
            lines.append(f"  fence_matrix: {r['fence_matrix']}")
    lines.append("=" * 100)
    return "\n".join(lines)
