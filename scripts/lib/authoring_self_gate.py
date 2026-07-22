#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tier: [orchestration-discipline]
# authoring_self_gate.py — author-time self-gate forcing function (shift-left runner)
#
# Carrier: CFP-2689 Phase 2 (구현) / Epic #2686 Story C — 저작시점 self-gate.
# 설계 SSOT: ADR-158 (author-time self-gate forcing function, 결정 1~9)
#           + change-plan 2026-07-16-cfp-2689 §3(설계) / §4(API 계약) / §5(파일 단위 변경).
#
# 정체 (ADR-158 §동기 / change-plan §1):
#   이미 required 인 기계 게이트(ac-traceability / doc-section-schema / doc-frontmatter-schema /
#   RTM format header signature)를 **리뷰 lane 진입 前(저작 완료 직후)** 그 Story 자기 산출물에
#   shift-left 선실행해, 구조/위치 conformance 결점을 저작 시점에 잡는다(리뷰를 그물이 아니라
#   예방으로). 검출 결점은 A dev-process-event ledger 로 emit(defect_finding) → B 가 집계.
#
# ★재사용 (reuse-before-write, ADR-140 / ADR-158 결정 2 — narrow re-implementation 금지):
#   대상 게이트의 **실 로직**을 정확 Phase 모드로 invoke 한다(게이트 로직 재구현 절대 금지).
#     - ac-traceability-matrix : 실 CLI 를 subprocess 로 호출(--phase/--ac-source/--rtm/--tests-root).
#     - rtm-format-signature   : check_ac_traceability_matrix.resolve_rtm_location / parse_rtm_table
#                                (실 파서 함수 import — pure parsing, 재구현 아님).
#     - doc-section-schema     : 실 게이트 script 를 per-artifact 격리 tmpdir(owner-prefix 배치)에서
#                                subprocess 실행(repo-wide 스캔 노이즈 없이 내 아티팩트만 CI-parity).
#     - doc-frontmatter-schema : 동형 격리 subprocess(+ docs/confluence-ia-tree.yaml 동반 복사 =
#                                category closed_enum 실검사).
#   검출 결점 emit = emit_dev_process_event.emit_defect_finding **소비만**(A/B 계약 0 수정).
#
# ★★정직 천장 (ADR-119 §결정4 2 판정면 / ADR-158 결정 6):
#   저작시점 self-gate = 예방 층(preventive forcing function). 검출 축 = 구조/위치 conformance
#   (RTM format / doc-section 위치 / AC header signature / frontmatter category). 미검출 축 =
#   semantic claim-accuracy(의미 정확성) — review-tier 잔여(기계 게이트 비강제). self-gate PASS =
#   실 게이트 실행 outcome(ground-truth) 이지 internal proxy 아님. 천장: 검출 완비를 보장하지
#   않으며(예방적 층), detecting_lane 은 저작 lane_label 근사(honest-degrade), defect_id 는
#   best-effort content-addressed(normalized-location 안정성·identity 유일성 무보장). landing ≠
#   activation("self-gate 실행" ≠ "결점 ledger emit 성공" — always-on α / 포트 가용성 의존).
#
# ★record-only non-blocking (ADR-115): 어떤 emit 실패도 self-gate 흐름을 block 하지 않는다
#   (graceful None). emit 포트 미가용/inactive-α → 게이트 검사는 실행·보고하되 emit=None.

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field

# Windows cp949 회피(ADR-061 portability — emit port 선례 답습)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

_GATE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_GATE_DIR))  # scripts/lib → scripts → repo root
_AC_GATE = os.path.join(_GATE_DIR, "check_ac_traceability_matrix.py")
_SECTION_GATE = os.path.join(_GATE_DIR, "check_doc_section_schema.py")
_FRONTMATTER_GATE = os.path.join(_GATE_DIR, "check_doc_frontmatter.py")

# ── 실 파서 함수 재사용 (rtm-format-signature = ac-traceability 파서 subset, 재구현 금지) ──
try:
    from check_ac_traceability_matrix import resolve_rtm_location, parse_rtm_table
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, _GATE_DIR)
    from check_ac_traceability_matrix import resolve_rtm_location, parse_rtm_table

# ── A emit port 소비만 (A/B 계약 0 수정). 미가용 → graceful (emit=None, non-crash) ──
try:
    from emit_dev_process_event import emit_defect_finding as _emit_defect_finding
    _EMIT_PORT_AVAILABLE = True
except Exception:  # pragma: no cover — 포트 미착지/미가용 = honest-degrade(측정≠emit)
    try:
        sys.path.insert(0, _GATE_DIR)
        from emit_dev_process_event import emit_defect_finding as _emit_defect_finding
        _EMIT_PORT_AVAILABLE = True
    except Exception:
        _emit_defect_finding = None
        _EMIT_PORT_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# 대상 게이트 집합(closed) + runnable/defer 정직 분류 (ADR-158 결정 1 / change-plan §3.5, AC-2/17)
#   저작시점 로컬 결정론 실행 = runnable-now. cross-repo state/runtime measurement/CI-only env 종속 =
#   deferred-to-CI(저작시점 실행 불가 → silent-covered 주장 금지). C 대상 4 게이트는 전부 runnable-now
#   — "deferred-to-CI" 분류는 정직 공개용 카테고리(C 대상 집합에 concrete member 없음, 자연 공집합).
# ─────────────────────────────────────────────────────────────────────────────
GATE_RUNNABILITY = {
    "ac-traceability-matrix": "runnable-now",   # 로컬 Python invoke (Phase-2 Hop3 = test symbol 실재 후)
    "doc-section-schema": "runnable-now",       # 로컬 실행
    "doc-frontmatter-schema": "runnable-now",   # 로컬 실행
    "rtm-format-signature": "runnable-now",     # pure 파싱
    "cross-repo-state | runtime-measurement | ci-only-env": "deferred-to-CI",  # capability boundary 공개
}

# per-artifact applicability: doc-section-schema / doc-frontmatter-schema 는 wrapper-path-scoped
#   (owner-prefix 하위 md 만). ★R1(설계리뷰): internal-docs Change Plan(`wrapper/change-plans/`,
#   `## §N`)엔 비적용 — wrapper `docs/change-plans/`(`### §N`) owner-prefix 미매칭 → false-positive 회피.
_DOC_SECTION_OWNER_PREFIXES = (
    "archive/adr", "docs/adr", "docs/change-plans", "docs/domain-knowledge",
    "docs/retros", "docs/inter-plugin-contracts", "docs/stories",
)
_DOC_FRONTMATTER_OWNER_PREFIXES = (
    "archive/adr", "docs/adr", "docs/change-plans", "docs/domain-knowledge/domain",
    "docs/domain-knowledge/concept", "docs/retros", "docs/inter-plugin-contracts",
)

# CLOSED-7 defect_family (append_dev_process_event._DEFECT_FAMILIES 정합 — 새 family 발명 금지, AC-15)
_CLOSED_7 = frozenset({
    "correctness", "security", "performance", "design-boundary",
    "test-gap", "doc-integrity", "process-discipline",
})

# 저작 lane_label CLOSED enum(9값) — detecting_lane honest-degrade(AC-4). 비-멤버("authoring-self-gate")
#   emit 금지(append `_norm_enum(...,None)` → null coerce 신호소실 회피). 저작시점 성격 = time_to_detection.
_LANE_LABELS = frozenset({
    "요구사항", "요구사항-리뷰", "설계", "설계-리뷰", "구현", "구현-리뷰",
    "구현-테스트", "보안-테스트", "없음",
})

# ★정직 천장 공개(ADR-119 / ADR-158 결정 6). AC-13 over-claim wording 미사용:
#   완전-방지/정확-검출/정밀-lane/유일성-보장 류 positive 단정 어휘를 본 소스에 담지 않는다
#   (금지 어휘를 verbatim 나열하면 over-claim 스캔이 자기 코드에서 자기-트립하는 CFP-2646/2684
#   self-referential 함정 — 그 함정 회피 위해 금지 문자열 자체를 인용하지 않고 정책만 서술).
CEILING_NOTE = (
    "저작시점 self-gate = 예방 층(preventive forcing function): 검출 축 = 구조/위치 conformance "
    "(RTM format / doc-section 위치 / AC header signature / frontmatter category). 미검출 축 = "
    "semantic claim-accuracy(의미 정확성) — review-tier 잔여(기계 게이트 비강제). self-gate PASS = "
    "실 게이트 실행 outcome(ground-truth) 이지 internal proxy 아님(ADR-119 2 판정면). 천장: 검출 완비를 "
    "보장하지 않으며(예방적 층), detecting_lane 은 저작 lane_label 근사(honest-degrade), defect_id 는 "
    "best-effort content-addressed(normalized-location 안정성·identity 유일성 무보장). "
    "landing ≠ activation('self-gate 실행' ≠ '결점 ledger emit 성공')."
)


# ─────────────────────────────────────────────────────────────────────────────
# 결과 구조 (change-plan §4.1 그대로)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Defect:
    """self-gate 검출 결점 (emit → defect_finding shape, B compute_selfref_recurrence 호환)."""
    gate: str                       # 검출 게이트명 (ran_gates 소속)
    defect_family: str              # CLOSED-7 (append _DEFECT_FAMILIES 정합, AC-15)
    defect_type: str                # semi-open ∪ 'unknown-type'
    detecting_lane: str             # 저작 lane_label(유효 enum 멤버) — honest-degrade(AC-4)
    time_to_detection: int          # ordinal 근사(저작시점 = 0 = 조기)
    defect_id: str                  # sha256(family‖type‖normalized-location) best-effort(AC-18)
    location: str                   # normalized-location(artifact + anchor)
    summary: str                    # 정직 요약(실 게이트 출력에서)
    honesty_note: str = ""          # honest-degrade / caveat


@dataclass
class SelfGateResult:
    """run_authoring_self_gate 반환 (change-plan §4.1).

    ran_gates       = 실행한 (게이트, 아티팩트) 항목 (정직 보고).
    passed          = 통과한 항목 (ran_gates ⊇ passed).
    failed          = 검출 결점 list[Defect].
    emitted         = emit 성공/None (측정≠emit 구분 — event_id 또는 None). len == len(failed).
    skipped_ci_defer= deferred-to-CI / 저작시점 실행불가(capability boundary, AC-17). silent-covered 금지.
    """
    ran_gates: list = field(default_factory=list)
    passed: list = field(default_factory=list)
    failed: list = field(default_factory=list)      # list[Defect]
    emitted: list = field(default_factory=list)     # list[event_id|None]
    skipped_ci_defer: list = field(default_factory=list)

    # 정직 measurement 축 (AC-11: "self-gate 실행됨" vs "ledger emit 성공(event_id non-None)" 구분)
    emit_port_available: bool = _EMIT_PORT_AVAILABLE
    emit_attempted: bool = False

    def stats(self):
        """측정≠emit 정직 구분 stats (AC-11/13)."""
        emit_success = sum(1 for e in self.emitted if e is not None)
        return {
            "self_gate_ran": len(self.ran_gates) > 0,     # 게이트 실행 여부(측정)
            "ran_gate_count": len(self.ran_gates),
            "passed_count": len(self.passed),
            "defect_count": len(self.failed),
            "emit_attempted": self.emit_attempted,
            "emit_port_available": self.emit_port_available,
            "emit_success_count": emit_success,           # ledger emit 성공(event_id non-None)
            "emit_none_count": len(self.emitted) - emit_success,
            "skipped_ci_defer_count": len(self.skipped_ci_defer),
            "measurement_note": (
                "self_gate_ran(게이트 실행) ≠ emit_success_count(ledger emit 성공). "
                "always-on α 비활성/포트 미가용 → 게이트 실행+보고하되 emit=None(측정≠emit)."
            ),
            "ceiling": CEILING_NOTE,
        }


# ─────────────────────────────────────────────────────────────────────────────
# helper
# ─────────────────────────────────────────────────────────────────────────────
def _match_owner_prefix(artifact_path, prefixes):
    """artifact_path 가 owner-prefix(연속 path 세그먼트) 하위인지 판정 → 매칭 prefix 또는 None.

    ★R1: `wrapper/change-plans/…` 는 `docs/change-plans` 세그먼트 미포함 → None(비적용). false-positive 회피.
    """
    segs = artifact_path.replace("\\", "/").strip("/").split("/")
    best = None
    for pfx in prefixes:
        p = pfx.split("/")
        for i in range(len(segs) - len(p) + 1):
            if segs[i:i + len(p)] == p:
                if best is None or len(p) > len(best.split("/")):
                    best = pfx
    return best


def _compute_defect_id(defect_family, defect_type, normalized_location):
    """defect_id = sha256(family‖type‖normalized-location) best-effort (AC-18, A 정직 천장 상속).

    normalized-location 안정성 무보장(honesty note 동반) — identity 유일성 주장하지 않음.
    """
    payload = "%s‖%s‖%s" % (defect_family, defect_type, normalized_location)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _lane_from_phase(phase):
    """저작 lane_label honest-degrade (AC-4) — phase → 유효 lane_label enum 멤버.

    시그니처가 producing lane 을 받지 않으므로 phase 로 근사(비-멤버 'authoring-self-gate' 절대 미emit):
      phase 1 = 저작시점 conformance 산출물(RTM/AC 표/doc-section) 저작 lane = '설계'.
      phase 2 = 구현 저작 lane = '구현'.
    ★근사(정밀 lane 아님) — honest-degrade. detecting_lane 은 저작 lane_label 근사.
    """
    lane = "구현" if phase == 2 else "설계"
    assert lane in _LANE_LABELS  # invalid enum emit 구조적 차단(AC-4)
    return lane


def _derive_story_key(ac_source, story_artifacts):
    """story_key best-effort 파생 — ac_source frontmatter `story_key:` 우선, 아니면 파일명 CFP 토큰."""
    candidates = [p for p in ([ac_source] + list(story_artifacts or [])) if p]
    for path in candidates:
        try:
            with open(path, encoding="utf-8") as fh:
                head = fh.read(4096)
            m = re.search(r"^story_key:\s*([A-Za-z]+-\d+)", head, re.MULTILINE)
            if m:
                return m.group(1)
        except Exception:
            pass
    for path in candidates:
        m = re.search(r"(CFP-\d+)", os.path.basename(path), re.IGNORECASE)
        if m:
            return m.group(1).upper()
    return None


def _run_subprocess(argv, cwd=None):
    """실 게이트 subprocess 실행 → (returncode, combined_output). timeout/오류 = graceful(non-crash)."""
    try:
        proc = subprocess.run(
            argv, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except Exception as exc:  # subprocess 미기동(python 부재 등) = invocation error(fail-open 방향)
        return None, "[authoring-self-gate] subprocess 실행 오류: %s" % exc


def _extract_error_lines(output, artifact_basename=None):
    """게이트 stdout 에서 결점 요약 라인 추출(::error:: + 관련 '  - ' 라인). 길이 bound."""
    lines = []
    for ln in output.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("::error::") or s.startswith("- ") or "필수 섹션 누락" in s or \
           "Hop1" in s or "Hop2" in s or "Hop3" in s or "미해결" in s or "누락" in s or \
           "∉ closed_enum" in s or "frontmatter" in s:
            if artifact_basename is None or artifact_basename in ln or "::error::" in ln or \
               "Hop" in ln or "미해결" in ln:
                lines.append(s)
        if len(lines) >= 12:
            break
    return " | ".join(lines) if lines else output.strip()[:600]


# ─────────────────────────────────────────────────────────────────────────────
# 게이트별 invoke (실 로직 재사용 — re-impl 금지)
# ─────────────────────────────────────────────────────────────────────────────
def gate_ac_traceability(ac_source, rtm, phase, tests_root=None):
    """ac-traceability-matrix 실 CLI 를 정확 Phase 모드로 subprocess invoke (AC-7, CI-parity).

    Returns (verdict, detail): verdict ∈ {'PASS','FAIL','DEFER','ERROR'}.
    ★phase 2 & tests_root 부재 → Hop3(born-missing) 저작시점 실행불가 → phase-1(Hop1+2) 로 실행 +
      Hop3 는 skipped_ci_defer 로 정직 공개(AC-17, silent-covered 금지).
    """
    if ac_source is None or rtm is None:
        return "ERROR", "ac-traceability: ac_source/rtm 경로 부재 — invoke 불가"

    effective_phase = phase
    deferred = None
    if phase == 2 and not tests_root:
        # Hop3(§8↔실 symbol born-missing)는 test symbol 실재 후 = 저작시점 실행불가 → 정직 defer.
        effective_phase = 1
        deferred = {
            "gate": "ac-traceability-matrix",
            "hop": "Hop3",
            "runnability": "deferred-to-CI",
            "reason": "tests_root 부재 — §8↔실 symbol born-missing 은 test 저작 후(CI/Phase-2)에만 판정 가능",
        }

    argv = [sys.executable, _AC_GATE, "--phase", str(effective_phase),
            "--ac-source", ac_source, "--rtm", rtm]
    if effective_phase == 2 and tests_root:
        argv += ["--tests-root", tests_root]

    rc, out = _run_subprocess(argv)
    if rc == 0:
        return "PASS", (out.strip()[:400], deferred)
    if rc == 1:
        return "FAIL", (_extract_error_lines(out), deferred)
    # rc == 2(argparse) / None(미기동) / 기타 = invocation error(정직 보고, 결점 위장 금지)
    return "ERROR", ("ac-traceability invocation error (rc=%s): %s" % (rc, out.strip()[:300]), deferred)


def gate_rtm_format_signature(rtm):
    """RTM format header signature — 실 파서(resolve_rtm_location/parse_rtm_table) 재사용(재구현 금지).

    §8 resolve + AC 컬럼 ∧ 테스트 컬럼 ∧ 백틱 test_* 심볼 존재 확인. B late-catch 클래스(§8.1.1 gate-parseable 아님).
    Returns (verdict, detail): verdict ∈ {'PASS','FAIL','ERROR'}.
    """
    if rtm is None:
        return "ERROR", "rtm 경로 부재 — invoke 불가"
    try:
        with open(rtm, encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:
        return "ERROR", "rtm 읽기 실패: %s" % exc
    section, note = resolve_rtm_location(text)
    if section is None:
        return "FAIL", "RTM 위치 미해결 — %s" % note
    mapping, _tier = parse_rtm_table(section)
    if not mapping:
        return "FAIL", "RTM 표 파싱 실패 — AC↔명명 테스트 매핑 미발견(gate-parseable 아님)"
    if not any(tests for tests in mapping.values()):
        return "FAIL", "RTM 표에 백틱 명명 테스트(test_*) 심볼 0 — header signature gate-parseable 아님"
    return "PASS", "RTM header signature resolved (%d AC 매핑, %s)" % (len(mapping), note)


def _run_isolated_doc_gate(gate_script, artifact_path, owner_prefix, extra_copies=()):
    """doc-section/doc-frontmatter 실 게이트 script 를 per-artifact 격리 tmpdir 에서 subprocess 실행.

    아티팩트를 owner-prefix 하위에 배치(그 외 owner 경로 부재 → 내 아티팩트만 검사, repo-wide 노이즈 0).
    extra_copies = (repo-root 상대 경로,) — category closed_enum 실검사용 confluence-ia-tree.yaml 등.
    """
    tmp = tempfile.mkdtemp(prefix="authoring-self-gate-")
    try:
        dest_dir = os.path.join(tmp, *owner_prefix.split("/"))
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copyfile(artifact_path, os.path.join(dest_dir, os.path.basename(artifact_path)))
        for rel in extra_copies:
            src = os.path.join(_REPO_ROOT, *rel.split("/"))
            if os.path.isfile(src):
                dst = os.path.join(tmp, *rel.split("/"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
        return _run_subprocess([sys.executable, gate_script], cwd=tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gate_doc_section_schema(artifact_path):
    """doc-section-schema 실 게이트를 per-artifact(owner-prefix scoped) invoke.

    Returns (verdict, detail): verdict ∈ {'PASS','FAIL','N/A','ERROR'}. N/A = wrapper owner-prefix 미매칭
    (★R1 — internal-docs Change Plan 등 비적용, false-positive 회피).
    """
    owner = _match_owner_prefix(artifact_path, _DOC_SECTION_OWNER_PREFIXES)
    if owner is None:
        return "N/A", "doc-section-schema 비적용 — wrapper owner-prefix 미매칭(R1 path-aware)"
    if not os.path.isfile(artifact_path):
        return "ERROR", "artifact 부재: %s" % artifact_path
    rc, out = _run_isolated_doc_gate(_SECTION_GATE, artifact_path, owner)
    if rc == 0:
        return "PASS", "doc-section-schema PASS (owner=%s)" % owner
    if rc == 1:
        return "FAIL", _extract_error_lines(out, os.path.basename(artifact_path))
    return "ERROR", "doc-section-schema invocation error (rc=%s): %s" % (rc, out.strip()[:300])


def gate_doc_frontmatter_schema(artifact_path):
    """doc-frontmatter-schema 실 게이트를 per-artifact(owner-prefix scoped) invoke.

    confluence-ia-tree.yaml 동반 복사 → category closed_enum 실검사. pyyaml 부재 시 게이트가 exit 0(skip)
    → PASS(정직: category/필드 검사 skip). Returns (verdict, detail).
    """
    owner = _match_owner_prefix(artifact_path, _DOC_FRONTMATTER_OWNER_PREFIXES)
    if owner is None:
        return "N/A", "doc-frontmatter-schema 비적용 — wrapper owner-prefix 미매칭(R1 path-aware)"
    if not os.path.isfile(artifact_path):
        return "ERROR", "artifact 부재: %s" % artifact_path
    rc, out = _run_isolated_doc_gate(
        _FRONTMATTER_GATE, artifact_path, owner,
        extra_copies=("docs/confluence-ia-tree.yaml",),
    )
    if rc == 0:
        return "PASS", "doc-frontmatter-schema PASS (owner=%s)" % owner
    if rc == 1:
        return "FAIL", _extract_error_lines(out, os.path.basename(artifact_path))
    return "ERROR", "doc-frontmatter-schema invocation error (rc=%s): %s" % (rc, out.strip()[:300])


# ─────────────────────────────────────────────────────────────────────────────
# 결점 → defect_family 분류 (CLOSED-7, 새 family 발명 금지 — AC-15)
# ─────────────────────────────────────────────────────────────────────────────
def _classify_family(gate, detail):
    """검출 결점 → CLOSED-7 defect_family (근접 정직 매핑 + honesty note, AC-15).

    구조/위치 conformance(doc-section/frontmatter/RTM format/Hop1 malformed) → doc-integrity.
    test 매핑/커버리지(ac-traceability Hop2/Hop3) → test-gap. 분류 불가 → 근접 정직 family + note.
    """
    text = detail if isinstance(detail, str) else str(detail)
    if gate in ("doc-section-schema", "doc-frontmatter-schema", "rtm-format-signature"):
        return "doc-integrity", ""
    if gate == "ac-traceability-matrix":
        if "Hop2" in text or "Hop3" in text or "born-missing" in text or "명명 테스트" in text or "미커버" in text:
            return "test-gap", ""
        if "Hop1" in text or "malformed" in text or "RTM" in text or "판정불가" in text or "AC 표" in text:
            return "doc-integrity", ""
        # 분류 불가 → 근접 정직 family(traceability 는 test↔AC 축) + honesty note(AC-15)
        return "test-gap", "family 근접 매핑(분류 불가 결점 → 근접 정직 family, 새 family 발명 금지)"
    return "doc-integrity", "family 근접 매핑(미상 게이트 → 근접 정직 family, 새 family 발명 금지)"


# ─────────────────────────────────────────────────────────────────────────────
# 오케스트레이션 (change-plan §4.1 시그니처 그대로)
# ─────────────────────────────────────────────────────────────────────────────
def run_authoring_self_gate(story_artifacts, ac_source, rtm, phase, tests_root=None,
                            emit=True, consumer_scope=None):
    """저작 완료 직후 대상 기계 게이트를 현 Story 실 아티팩트에 shift-left invoke → SelfGateResult.

    Args:
      story_artifacts : doc-section/frontmatter 대상 아티팩트 경로 list(ADR/Change Plan/Story 등).
                        owner-prefix 미매칭(internal-docs 등) = per-gate N/A(R1).
      ac_source       : ac-traceability --ac-source(§5 AC 표 문서, 보통 Story).
      rtm             : ac-traceability --rtm / rtm-format 대상(§8 Test Contract, 보통 Change Plan).
      phase           : EXPLICIT 1|2 (ac-traceability Phase 모드 — diff 추론 금지, AC-7).
      tests_root      : Phase-2 born-missing 해석 루트(부재 시 Hop3 → skipped_ci_defer, AC-17).
      emit            : True → 검출 결점 defect_finding emit(A ledger). False → emit 미시도(dogfood/self-test).
      consumer_scope  : 'wrapper'|'consumer'(emit α gate 전달 — 미지정 시 gate 가 checkout-identity 파생).

    non-blocking: 어떤 emit 실패/포트 미가용도 흐름 무차단(graceful None, ADR-115). self-gate PASS =
    실 게이트 실행 outcome ground-truth(proxy 아님). 검출 완비 미보장(예방적 층, CEILING_NOTE).
    """
    result = SelfGateResult()
    story_artifacts = list(story_artifacts or [])

    # ── 1. ac-traceability-matrix (primary — A/B late-catch 클래스, 정확 Phase 모드) ──
    if ac_source and rtm:
        label = "ac-traceability-matrix (phase=%s)" % phase
        result.ran_gates.append(label)
        verdict, payload = gate_ac_traceability(ac_source, rtm, phase, tests_root)
        detail, deferred = payload if isinstance(payload, tuple) else (payload, None)
        if deferred:
            result.skipped_ci_defer.append(deferred)
        if verdict == "PASS":
            result.passed.append(label)
        elif verdict == "FAIL":
            fam, note = _classify_family("ac-traceability-matrix", detail)
            result.failed.append(_mk_defect("ac-traceability-matrix", fam, ac_source, rtm, detail, phase, note))
        else:  # ERROR — 정직 보고(결점 위장 금지), non-blocking
            result.skipped_ci_defer.append({
                "gate": "ac-traceability-matrix", "runnability": "invocation-error",
                "reason": str(detail),
            })

    # ── 2. rtm-format-signature (실 파서 재사용, gate-parseable 확인) ──
    if rtm:
        label = "rtm-format-signature"
        result.ran_gates.append(label)
        verdict, detail = gate_rtm_format_signature(rtm)
        if verdict == "PASS":
            result.passed.append(label)
        elif verdict == "FAIL":
            fam, note = _classify_family("rtm-format-signature", detail)
            result.failed.append(_mk_defect("rtm-format-signature", fam, rtm, rtm, detail, phase, note))
        else:
            result.skipped_ci_defer.append({
                "gate": "rtm-format-signature", "runnability": "invocation-error", "reason": str(detail),
            })

    # ── 3. doc-section-schema / doc-frontmatter-schema (per-artifact, R1 path-aware) ──
    for artifact in story_artifacts:
        for gate_name, gate_fn in (
            ("doc-section-schema", gate_doc_section_schema),
            ("doc-frontmatter-schema", gate_doc_frontmatter_schema),
        ):
            verdict, detail = gate_fn(artifact)
            if verdict == "N/A":
                continue  # R1 비적용 — silent-covered 아님(적용 대상만 ran_gates 등재)
            label = "%s:%s" % (gate_name, os.path.basename(artifact))
            result.ran_gates.append(label)
            if verdict == "PASS":
                result.passed.append(label)
            elif verdict == "FAIL":
                fam, note = _classify_family(gate_name, detail)
                result.failed.append(_mk_defect(gate_name, fam, artifact, artifact, detail, phase, note))
            else:
                result.skipped_ci_defer.append({
                    "gate": gate_name, "artifact": artifact,
                    "runnability": "invocation-error", "reason": str(detail),
                })

    # ── 4. 검출 결점 emit (A emit port 소비만; 측정≠emit — AC-9/10/11) ──
    if emit and result.failed:
        result.emit_attempted = True
        story_key = _derive_story_key(ac_source, story_artifacts)
        emit_lane = _lane_from_phase(phase)  # 저작 lane_label(honest-degrade)
        for d in result.failed:
            eid = _emit_one(d, story_key, emit_lane, consumer_scope)
            result.emitted.append(eid)

    return result


def _mk_defect(gate, family, primary_path, ref_path, detail, phase, extra_note=""):
    """Defect 구성 — B-compatible shape(family/type/detecting_lane/ttd/defect_id)."""
    normalized_location = "%s::%s" % (_normalize_loc(primary_path), gate)
    defect_type = "unknown-type"  # semi-open ∪ unknown-type — review-verdict-v4 type 무검증 → 정직 fallback
    detecting_lane = _lane_from_phase(phase)
    defect_id = _compute_defect_id(family, defect_type, normalized_location)
    honesty = (
        "detecting_lane=저작 lane_label 근사(honest-degrade, AC-4) / defect_type=unknown-type"
        "(review-verdict-v4 type 무검증 정직 fallback) / defect_id=best-effort(normalized-location "
        "안정성 무보장, AC-18)."
    )
    if extra_note:
        honesty = extra_note + " | " + honesty
    return Defect(
        gate=gate,
        defect_family=family,
        defect_type=defect_type,
        detecting_lane=detecting_lane,
        time_to_detection=0,  # 저작시점 = 조기 ordinal(리뷰 lane 진입 前 = 0)
        defect_id=defect_id,
        location=normalized_location,
        summary=str(detail)[:600],
        honesty_note=honesty,
    )


def _normalize_loc(path):
    """normalized-location — repo-root 상대화 best-effort(안정성 무보장, AC-18 caveat 상속)."""
    p = os.path.abspath(path).replace("\\", "/")
    root = _REPO_ROOT.replace("\\", "/")
    if p.startswith(root + "/"):
        return p[len(root) + 1:]
    return os.path.basename(p)


def _emit_one(defect, story_key, emit_lane, consumer_scope):
    """단일 결점 emit → event_id | None (graceful, non-blocking — AC-10)."""
    if not _EMIT_PORT_AVAILABLE or _emit_defect_finding is None:
        return None
    try:
        return _emit_defect_finding(
            story_key, emit_lane,
            defect_id=defect.defect_id,
            defect_family=defect.defect_family,
            defect_type=defect.defect_type,
            detecting_lane=defect.detecting_lane,   # 유효 lane_label(honest-degrade)
            time_to_detection=defect.time_to_detection,
            content=("[authoring-self-gate] %s: %s" % (defect.gate, defect.summary)),
            consumer_scope=consumer_scope,
        )
    except Exception:  # record-only exit-0 (ADR-115) — 어떤 emit 실패도 흐름 무차단
        return None


# ─────────────────────────────────────────────────────────────────────────────
# self-test (execution-backed, 독립 oracle + 대칭 fail-closed — ADR-158 결정 5, AC-14)
#   distinct-marker sentinel: known-good→GREEN ∧ known-bad→RED 양방향(present-null 비대칭 금지).
#   사전-고정 독립 fixture(자기 계산 self-match 금지 — CFP-2673 X⊆X tautology 회피).
# ─────────────────────────────────────────────────────────────────────────────
_FX_GOOD_STORY = """---
story_key: CFP-9999
---
# Fixture Story
## 5. 요구사항 확장 해석
### 5.3 Acceptance Criteria
| id | statement | source | tier |
|---|---|---|---|
| AC-1 | do X correctly | user | normative |
"""

_FX_GOOD_RTM = """# Fixture Change Plan
## §8. Test Contract
### §8.1.1 RTM
| AC | tier | 명명 테스트 |
|---|---|---|
| AC-1 | normative | `test_ac1_x` |
"""

# known-bad: normative AC-1 이 RTM 에 미매핑(row 누락) → ac-traceability Hop2 RED.
_FX_BAD_RTM_MISSING_ROW = """# Fixture Change Plan
## §8. Test Contract
### §8.1.1 RTM
| AC | tier | 명명 테스트 |
|---|---|---|
| AC-2 | normative | `test_ac2_y` |
"""

# known-bad: §8 자체 부재 → rtm-format-signature RED(위치 미해결).
_FX_BAD_RTM_NO_SECTION = """# Fixture Change Plan
## §7. 보안
내용.
"""

# known-bad: §5 에 AC 선언(산문 AC-1) 있으나 parseable 표 부재 → ac-traceability UNDECIDABLE RED(AC header 손상).
_FX_BAD_STORY_CORRUPT_HEADER = """---
story_key: CFP-9999
---
# Fixture Story
## 5. 요구사항 확장 해석
### 5.3 Acceptance Criteria
AC-1 은 X 를 해야 한다(표 없이 산문만 — header 손상).
"""

_FX_GOOD_ADR = """---
adr_number: 9999
title: Fixture ADR
status: Active
category: orchestration-discipline
date: 2026-07-16
---
# ADR-9999 — Fixture
## 상태
Active.
## 컨텍스트
context.
## 결정
decision.
## 결과
result.
## 관련 파일
files.
"""

# known-bad: `## 결정` 섹션 부재 → doc-section-schema RED(§4 위치/필수 섹션 위반 동형).
_FX_BAD_ADR_MISSING_SECTION = """---
adr_number: 9999
title: Fixture ADR
status: Active
category: orchestration-discipline
date: 2026-07-16
---
# ADR-9999 — Fixture
## 상태
Active.
## 컨텍스트
context.
## 결과
result.
## 관련 파일
files.
"""

# known-bad: 필수 frontmatter 필드 `date` 부재 → doc-frontmatter-schema RED(pyyaml 필요).
_FX_BAD_ADR_MISSING_FIELD = """---
adr_number: 9999
title: Fixture ADR
status: Active
category: orchestration-discipline
---
# ADR-9999 — Fixture
## 상태
Active.
## 컨텍스트
context.
## 결정
decision.
## 결과
result.
## 관련 파일
files.
"""

# known-bad: category invalid(closed_enum 밖) → doc-frontmatter-schema RED(confluence-ia-tree.yaml 필요).
_FX_BAD_ADR_INVALID_CATEGORY = """---
adr_number: 9999
title: Fixture ADR
status: Active
category: totally-not-a-real-category-xyz
date: 2026-07-16
---
# ADR-9999 — Fixture
## 상태
Active.
## 컨텍스트
context.
## 결정
decision.
## 결과
result.
## 관련 파일
files.
"""


def _write_fixture(directory, name, content):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:  # CRLF 금지(Windows)
        fh.write(content)
    return path


def _yaml_available():
    try:
        import yaml  # noqa: F401
        return True
    except Exception:
        return False


def _self_test():
    """독립 fixture oracle + 대칭 fail-closed(known-good→GREEN ∧ known-bad→RED) 양방향 검증."""
    print("═══ authoring-self-gate self-test (독립 oracle + 대칭 fail-closed) ═══")
    failures = []
    fx = tempfile.mkdtemp(prefix="authoring-self-gate-selftest-")
    try:
        good_story = _write_fixture(fx, "good_story.md", _FX_GOOD_STORY)
        good_rtm = _write_fixture(fx, "good_rtm.md", _FX_GOOD_RTM)
        bad_rtm_row = _write_fixture(fx, "bad_rtm_missing_row.md", _FX_BAD_RTM_MISSING_ROW)
        bad_rtm_nosec = _write_fixture(fx, "bad_rtm_no_section.md", _FX_BAD_RTM_NO_SECTION)
        bad_story_hdr = _write_fixture(fx, "bad_story_corrupt_header.md", _FX_BAD_STORY_CORRUPT_HEADER)
        # doc 게이트 fixture 는 owner-prefix(archive/adr) 하위에 배치 → per-artifact invoke 매칭.
        adr_dir = os.path.join(fx, "archive", "adr")
        os.makedirs(adr_dir, exist_ok=True)
        good_adr = _write_fixture(adr_dir, "ADR-9999-good.md", _FX_GOOD_ADR)
        bad_adr_sec = _write_fixture(adr_dir, "ADR-9999-missing-section.md", _FX_BAD_ADR_MISSING_SECTION)
        bad_adr_field = _write_fixture(adr_dir, "ADR-9999-missing-field.md", _FX_BAD_ADR_MISSING_FIELD)
        bad_adr_cat = _write_fixture(adr_dir, "ADR-9999-invalid-category.md", _FX_BAD_ADR_INVALID_CATEGORY)

        def expect_v(marker, actual_verdict, expected_verdict):
            # verdict 문자열 직접 대조(독립 oracle — 사전-고정 기대값, self-match 아님).
            ok = (actual_verdict == expected_verdict)
            print("  SELFTEST[%s]=%s (기대 %s) %s"
                  % (marker, actual_verdict, expected_verdict, "OK" if ok else "MISMATCH"))
            if not ok:
                failures.append("%s: 기대 %s 실측 %s" % (marker, expected_verdict, actual_verdict))

        def expect_b(marker, actual_bool, expected_bool):
            ok = (bool(actual_bool) == bool(expected_bool))
            print("  SELFTEST[%s]=%s (기대 %s) %s"
                  % (marker, bool(actual_bool), bool(expected_bool), "OK" if ok else "MISMATCH"))
            if not ok:
                failures.append("%s: 기대 %s 실측 %s" % (marker, bool(expected_bool), bool(actual_bool)))

        # ── 축 a 독립 oracle + 축 b 대칭 fail-closed: ac-traceability(known-good→PASS ∧ known-bad→FAIL) ──
        v, _ = gate_ac_traceability(good_story, good_rtm, phase=1)
        expect_v("ac-good", v, "PASS")                    # known-good → GREEN
        v, _ = gate_ac_traceability(good_story, bad_rtm_row, phase=1)
        expect_v("ac-bad-rtm-row", v, "FAIL")            # RTM row 누락(normative AC-1 미매핑) → RED
        v, _ = gate_ac_traceability(bad_story_hdr, good_rtm, phase=1)
        expect_v("ac-header-corrupt", v, "FAIL")         # AC header 손상(표 부재 산문선언) → RED

        # ── rtm-format-signature ──
        v, _ = gate_rtm_format_signature(good_rtm)
        expect_v("rtm-format-good", v, "PASS")
        v, _ = gate_rtm_format_signature(bad_rtm_nosec)
        expect_v("rtm-format-bad", v, "FAIL")            # §8 부재 → RED

        # ── doc-section-schema ──
        v, _ = gate_doc_section_schema(good_adr)
        expect_v("docsec-good", v, "PASS")
        v, _ = gate_doc_section_schema(bad_adr_sec)
        expect_v("docsec-bad", v, "FAIL")                # 필수 섹션(## 결정) 누락 → RED
        # ★R1: wrapper owner-prefix 미매칭 경로 → N/A(false-positive 회피)
        na_path = os.path.join(fx, "wrapper", "change-plans", "cp.md")
        os.makedirs(os.path.dirname(na_path), exist_ok=True)
        _write_fixture(os.path.dirname(na_path), "cp.md", "## §1 x\n")
        v, _ = gate_doc_section_schema(na_path)
        expect_v("docsec-R1-na", v, "N/A")               # internal-docs 형 경로 → 비적용

        # ── doc-frontmatter-schema (pyyaml 필요 — 부재 시 정직 SKIP) ──
        if _yaml_available():
            v, _ = gate_doc_frontmatter_schema(good_adr)
            expect_v("frontmatter-good", v, "PASS")
            v, _ = gate_doc_frontmatter_schema(bad_adr_field)
            expect_v("frontmatter-bad-field", v, "FAIL")   # 필수 필드(date) 누락 → RED
            # invalid category = confluence-ia-tree.yaml 실재 시에만 검사(격리 tmp 동반 복사).
            if os.path.isfile(os.path.join(_REPO_ROOT, "docs", "confluence-ia-tree.yaml")):
                v, _ = gate_doc_frontmatter_schema(bad_adr_cat)
                expect_v("frontmatter-bad-category", v, "FAIL")  # closed_enum 밖 → RED
            else:
                print("  SELFTEST[frontmatter-bad-category]=SKIP (confluence-ia-tree.yaml 부재)")
        else:
            print("  SELFTEST[frontmatter-*]=SKIP (pyyaml 부재 — doc-frontmatter 게이트 자체 skip)")

        # ── run_authoring_self_gate e2e: 대칭(good→0 defect / bad→≥1 defect), emit=False ──
        r_good = run_authoring_self_gate(
            [good_adr], ac_source=good_story, rtm=good_rtm, phase=1, emit=False)
        expect_b("e2e-good-0defect", len(r_good.failed) == 0, True)
        expect_b("e2e-good-ran", len(r_good.ran_gates) > 0, True)
        r_bad = run_authoring_self_gate(
            [bad_adr_sec], ac_source=good_story, rtm=bad_rtm_row, phase=1, emit=False)
        expect_b("e2e-bad-detect", len(r_bad.failed) >= 1, True)   # 대칭 fail-closed
        # 측정≠emit 정직 구분(AC-11): emit=False → emit_success_count 0, self_gate_ran True
        st = r_bad.stats()
        expect_b("e2e-stats-ran-not-emit", st["self_gate_ran"] and st["emit_success_count"] == 0, True)
        # detecting_lane 은 항상 유효 enum 멤버(invalid emit 구조적 차단, AC-4)
        expect_b("detecting-lane-valid-enum",
                 all(d.detecting_lane in _LANE_LABELS for d in r_bad.failed), True)
        # defect_family 항상 CLOSED-7(새 family 발명 금지, AC-15)
        expect_b("defect-family-closed7",
                 all(d.defect_family in _CLOSED_7 for d in r_bad.failed), True)
    finally:
        shutil.rmtree(fx, ignore_errors=True)

    print("─" * 60)
    if failures:
        print("authoring-self-gate self-test: FAIL (%d 건)" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("authoring-self-gate self-test: PASS (독립 oracle + 대칭 fail-closed 양방향 + "
          "R1 path-aware N/A + 측정≠emit 구분 + valid-enum/CLOSED-7 봉인)")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# CLI — advisory lane-exit self-check 진입점(§3.2 advisory wiring) + --self-test
# ─────────────────────────────────────────────────────────────────────────────
def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "author-time self-gate (shift-left) — 대상 기계 게이트를 리뷰 lane 진입 前 자기 산출물에 "
            "선실행(ADR-158). advisory lane-exit self-check. 검출 완비 미보장(예방적 층, CEILING_NOTE)."
        )
    )
    parser.add_argument("--self-test", action="store_true",
                        help="execution-backed self-test(독립 oracle + 대칭 fail-closed).")
    parser.add_argument("--story-artifacts", nargs="*", default=[],
                        help="doc-section/frontmatter 대상 아티팩트(ADR/Change Plan/Story). owner-prefix "
                             "미매칭(internal-docs 등) = per-gate N/A(R1).")
    parser.add_argument("--ac-source", default=None,
                        help="ac-traceability --ac-source(§5 AC 표 문서, 보통 Story).")
    parser.add_argument("--rtm", default=None,
                        help="ac-traceability --rtm / rtm-format 대상(§8 Test Contract, 보통 Change Plan).")
    parser.add_argument("--phase", type=int, choices=(1, 2), default=None,
                        help="EXPLICIT ac-traceability Phase 모드(diff 추론 금지, AC-7).")
    parser.add_argument("--tests-root", default=None,
                        help="Phase-2 born-missing 해석 루트(부재 시 Hop3 → skipped_ci_defer, AC-17).")
    parser.add_argument("--no-emit", action="store_true",
                        help="검출 결점 emit 미시도(dogfood/self-application 시 ledger 미기록).")
    parser.add_argument("--consumer-scope", default=None, choices=("wrapper", "consumer"),
                        help="emit α gate scope(미지정 시 checkout-identity 파생).")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.phase is None:
        parser.error("--phase (1|2) 필수 (self-gate 실행 시). EXPLICIT — diff 추론 금지(AC-7).")

    result = run_authoring_self_gate(
        story_artifacts=args.story_artifacts,
        ac_source=args.ac_source,
        rtm=args.rtm,
        phase=args.phase,
        tests_root=args.tests_root,
        emit=(not args.no_emit),
        consumer_scope=args.consumer_scope,
    )

    print("═══ author-time self-gate (phase=%s) ═══" % args.phase)
    print("실행 게이트(ran): %s" % (result.ran_gates or "(없음)"))
    print("통과(passed): %d/%d" % (len(result.passed), len(result.ran_gates)))
    if result.skipped_ci_defer:
        print("deferred-to-CI / invocation-error (silent-covered 아님, AC-17):")
        for d in result.skipped_ci_defer:
            print("  - %s" % d)
    if result.failed:
        print("검출 결점(defect_finding, %d 건):" % len(result.failed))
        for d in result.failed:
            print("  - [%s] family=%s type=%s lane=%s id=%s"
                  % (d.gate, d.defect_family, d.defect_type, d.detecting_lane, d.defect_id[:12]))
            print("      %s" % d.summary)
    else:
        print("검출 결점: 0 (self-gate PASS — 실 게이트 실행 outcome)")
    st = result.stats()
    print("stats(측정≠emit): self_gate_ran=%s emit_attempted=%s emit_success=%d/%d port_available=%s"
          % (st["self_gate_ran"], st["emit_attempted"], st["emit_success_count"],
             len(result.emitted), st["emit_port_available"]))
    print("CEILING: %s" % CEILING_NOTE)
    # advisory verdict signal(비-blocking): 결점 → non-zero(저작자 alert). merge-gate 가 fail-closed backstop.
    return 1 if result.failed else 0


if __name__ == "__main__":
    sys.exit(main())
