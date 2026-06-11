#!/usr/bin/env python3
# scripts/lib/walk_plan.py — CFP-1170 Phase 2 + CFP-1173 Phase 2
# walk + plan Python SSOT (ADR-061 외부 .py 의무)
#
# 책임 (change-plan §3.4 / §4.3):
#   (a) changelog walk — per-plugin CHANGELOG.md (from_version → to_version) 구간 entry enumerate
#   (b) min_prerequisite_version topological resolve — 9-plugin DAG topological sort + mismatch detection
#   (c) walk_result aggregate — bundle tier 9 plugin walk_result 종합 (deterministic exit code mapping)
#   (d) marker_merge — walk apply stage R-2 customization marker 보존 흡수 (reconcile-overlay.sh 흡수)
#   (e) importance_score hook — plan stage 각 entry blast-radius importance_score 계산 (CFP-1173)
#       Story-5 placeholder → importance_score.py 실 wire
#       brainstorming 결정 4: 3-tuple (touched_lanes + breaking + contract_major) weighted_sum
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 의무)
#   ADR-092 per-plugin self-owned CHANGELOG.md (walk source SSOT)
#   ADR-096 min_prerequisite_version manifest schema (topological resolve)
#   ADR-097 paradigm replacement (imperative walk)
#   ADR-027 §결정 7.D.3 customization marker whole-line anchored
#
# SSOT: docs/change-plans/cfp-1170-cli-walk-tier.md §3.4 / §4.3 / §11.2
#       docs/change-plans/cfp-1173-blast-radius-parallel.md §3 importance_score hook
# Contract: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §2.A/§2.E/§중요도
#
# sanity check 3종 (ADR-061 의무):
#   1. diff inspection — 구현 직후 reviewer가 수행
#   2. lint re-run — flake8/ruff (CI)
#   3. sample file Read — 본 파일 상단 직접 확인
#
# Sandbox env: CBL_SKIP_ISSUE_CREATE=1

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ──────────────────────────── WalkResult enum ─────────────────────────────────
# change-plan §4.3 / imperative-walker-protocol-v1 §2.A.1
# closed_set open_extension: false (ADR-093 §결정 2 — 5번째 enum 값 ad-hoc 확장 금지)

class WalkResult(Enum):
    """9-plugin family walk 결과 enum (4-value closed_set).

    ADR-093 §결정 2 — closed_set open_extension: false.
    5번째 값 ad-hoc 확장 금지 (별도 ADR 없이 확장 불가).
    CFP-1199 F1: 9-plugin family 확장 (ADR-087/088) — enum 값 자체는 변경 없음.
    """
    SUCCESS = "SUCCESS"
    SUCCESS_WITH_DEGRADATION = "SUCCESS_WITH_DEGRADATION"
    PARTIAL_FAILURE = "PARTIAL_FAILURE"
    FAILED = "FAILED"

    def to_exit_code(self) -> int:
        """exit code → walk_result deterministic mapping (silent false SUCCESS 차단).

        change-plan §4.1 / imperative-walker-protocol-v1 §2.A.1 exit_code_mapping:
          SUCCESS                  → 0 (완전 성공)
          SUCCESS_WITH_DEGRADATION → 1 (경고 — grace window 안 degraded, 가시화 의무)
          PARTIAL_FAILURE          → 2 (일부 실패 + per-family rollback 완료)
          FAILED                   → 3 (전체 실패)

        ADR-093 §결정 1 silent false SUCCESS 차단:
          exit 비-0 → SUCCESS hardcode 금지 (SUCCESS_WITH_DEGRADATION ≠ exit 0).
        """
        _MAP = {
            WalkResult.SUCCESS: 0,
            WalkResult.SUCCESS_WITH_DEGRADATION: 1,
            WalkResult.PARTIAL_FAILURE: 2,
            WalkResult.FAILED: 3,
        }
        return _MAP[self]


# exit code map (참조용 상수 — WalkResult.to_exit_code() 와 동기화 유지)
EXIT_CODE_MAP = {
    WalkResult.SUCCESS: 0,
    WalkResult.SUCCESS_WITH_DEGRADATION: 1,
    WalkResult.PARTIAL_FAILURE: 2,
    WalkResult.FAILED: 3,
}

# topological order (ADR-096 §결정 2 DAG invariant: wrapper 먼저, 8 lane 후행)
# lane → wrapper 단방향 의존 (cycle 부재 — wrapper 최상위)
# CFP-1199 F1: 7 → 9 plugin 확장 (ADR-087 codeforge-deploy + ADR-088 codeforge-deploy-review)
TOPOLOGICAL_ORDER = [
    "codeforge",           # wrapper (최상위, 8 lane 모두 의존)
    "codeforge-requirements",
    "codeforge-design",
    "codeforge-review",
    "codeforge-develop",
    "codeforge-test",
    "codeforge-pmo",
    "codeforge-deploy",          # ADR-087 신설 — deploy lane (wrapper 의존, pmo 이후 보수 lifecycle 순서)
    "codeforge-deploy-review",   # ADR-088 신설 — deploy-review lane (wrapper 의존, deploy 이후)
]


def get_topological_order() -> list[str]:
    """9-plugin family topological order 반환 (ADR-096 §결정 2 DAG invariant).

    [wrapper(codeforge), ...8 lane] — wrapper 먼저 resolve, cycle 부재.
    CFP-1199 F1: codeforge-deploy (ADR-087) + codeforge-deploy-review (ADR-088) 추가.
    """
    return list(TOPOLOGICAL_ORDER)


# ──────────────────────────── 예외 클래스 ─────────────────────────────────────

class ChangelogParseError(Exception):
    """CHANGELOG.md 파싱 실패 (malformed 또는 파일 미존재).

    abort-before-touch: filesystem touch 0 보장 상태 abort (change-plan §7.3).
    """


class VersionRangeError(Exception):
    """잘못된 version range (from > to 또는 invalid semver).

    raise → abort-before-touch (walk 중단, filesystem touch 0).
    """


# ──────────────────────────── 데이터 클래스 ───────────────────────────────────

@dataclass
class ChangelogEntry:
    """단일 changelog entry (version + content)."""
    version: str
    content: str


@dataclass
class PrereqMismatch:
    """min_prerequisite_version mismatch 감지 결과.

    detection only — 처리 (degraded/grace/hard fail) = UpgradeAgent §consumer-fallback 위임
    (ADR-094 SSOT). change-plan §4.3 / §4.4.
    """
    plugin: str          # mismatch 발생 plugin 이름
    required_range: str  # plugin 이 요구하는 min_prereq semver range (예: ">=5.5.0")
    actual: str          # consumer 가 실제 설치한 버전


# ──────────────────────────── semver 유틸 ────────────────────────────────────

_SEMVER_RE = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)(?:[.-].*)?$"
)


def _parse_semver(version: str) -> tuple[int, int, int]:
    """semver 문자열 → (major, minor, patch) 튜플.

    raise VersionRangeError if not valid semver.
    """
    m = _SEMVER_RE.match(version.strip())
    if not m:
        raise VersionRangeError(
            f"잘못된 semver 형식: '{version}' — 예: 5.3.0 / v5.3.0"
        )
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _semver_gt(a: str, b: str) -> bool:
    """a > b 이면 True (both valid semver, raise VersionRangeError if invalid)."""
    return _parse_semver(a) > _parse_semver(b)


def _semver_ge(a: str, b: str) -> bool:
    """a >= b 이면 True."""
    return _parse_semver(a) >= _parse_semver(b)


def _semver_le(a: str, b: str) -> bool:
    """a <= b 이면 True."""
    return _parse_semver(a) <= _parse_semver(b)


# ──────────────────────────── (a) changelog walk ─────────────────────────────

# CHANGELOG.md 버전 헤더 패턴 (## [5.3.0] 또는 ## 5.3.0 형태)
_CHANGELOG_VERSION_RE = re.compile(
    r"^##\s+\[?v?(\d+\.\d+\.\d+[^\]]*)\]?",
    re.MULTILINE,
)


def walk_changelog(
    plugin: str,
    from_version: str,
    to_version: str,
    changelog_path: str,
) -> list[ChangelogEntry]:
    """per-plugin CHANGELOG.md (from_version → to_version) 구간 entry enumerate.

    ADR-092 정합 — per-plugin self-owned CHANGELOG.md 가 walk source SSOT.

    Args:
        plugin: plugin 이름 (검증용, walk source SSOT = changelog_path)
        from_version: consumer installed 버전 (enumerate 제외 — exclusive)
        to_version: changelog latest 버전 (enumerate 포함 — inclusive)
        changelog_path: per-plugin CHANGELOG.md 파일 경로

    Returns:
        applicable changelog entries (구간 평탄화, from 제외 to 포함)
        빈 list = from == to (already up-to-date, idempotent no-op)

    Raises:
        ChangelogParseError: malformed CHANGELOG 또는 파일 미존재
        VersionRangeError: from > to 또는 invalid semver (abort-before-touch)
    """
    # 1. semver 검증 (abort-before-touch — invalid semver 즉시 raise)
    try:
        from_tuple = _parse_semver(from_version)
        to_tuple = _parse_semver(to_version)
    except VersionRangeError:
        raise

    # 2. range 검증 (from > to → VersionRangeError)
    if from_tuple > to_tuple:
        raise VersionRangeError(
            f"from_version ({from_version}) > to_version ({to_version}) — "
            f"plugin: {plugin}. 역방향 walk 금지 (downgrade는 --rollback 사용)."
        )

    # 3. from == to → empty (already up-to-date, idempotent)
    if from_tuple == to_tuple:
        return []

    # 4. CHANGELOG.md 읽기 (파일 미존재 → ChangelogParseError)
    try:
        with open(changelog_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise ChangelogParseError(
            f"CHANGELOG.md 미존재: {changelog_path} — plugin: {plugin}. "
            "abort-before-touch (ADR-092 per-plugin CHANGELOG.md 필수)."
        )
    except Exception as e:
        raise ChangelogParseError(
            f"CHANGELOG.md 읽기 오류: {changelog_path} — {e}"
        )

    # 5. 버전 헤더 파싱
    matches = list(_CHANGELOG_VERSION_RE.finditer(content))
    if not matches:
        raise ChangelogParseError(
            f"CHANGELOG.md 형식 오류: 버전 헤더(## [X.Y.Z]) 없음 — {changelog_path}. "
            "ADR-092 per-plugin CHANGELOG.md 형식 필요."
        )

    # 6. 구간 추출 (from 제외, to 포함)
    entries: list[ChangelogEntry] = []
    for i, match in enumerate(matches):
        version_str = match.group(1).strip()

        # semver 파싱 실패 = 건너뜀 (malformed header 무시 — 하지만 valid header 0건이면 위에서 이미 에러)
        try:
            v_tuple = _parse_semver(version_str)
        except VersionRangeError:
            continue

        # 구간 필터: from_version < v <= to_version
        if not (from_tuple < v_tuple <= to_tuple):
            continue

        # 해당 버전의 content 추출 (다음 헤더 전까지)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        entry_content = content[start:end].strip()

        entries.append(ChangelogEntry(version=version_str, content=entry_content))

    # 7. 버전 순서 정렬 (ascending — apply 순서, 낮은 버전 먼저)
    entries.sort(key=lambda e: _parse_semver(e.version))

    return entries


# ──────────────────────────── (b) min_prereq topological resolve ──────────────

def _parse_semver_range(semver_range: str) -> tuple[str, tuple[int, int, int]]:
    """semver range 문자열 파싱 → (operator, version_tuple).

    지원 형식: ">=5.5.0" / ">=5.0.0" / "5.0.0" (no operator = ">=")
    """
    semver_range = semver_range.strip()
    for op in (">=", ">", "<=", "<", "==", "="):
        if semver_range.startswith(op):
            version_str = semver_range[len(op):].strip()
            return op, _parse_semver(version_str)
    # operator 없음 = exact match (>=)
    return ">=", _parse_semver(semver_range)


def _satisfies_range(version: str, semver_range: str) -> bool:
    """version 이 semver_range 를 만족하는지 확인.

    raise VersionRangeError if invalid.
    """
    op, required_tuple = _parse_semver_range(semver_range)
    actual_tuple = _parse_semver(version)

    if op in (">=", "="):
        return actual_tuple >= required_tuple
    elif op == ">":
        return actual_tuple > required_tuple
    elif op == "<=":
        return actual_tuple <= required_tuple
    elif op == "<":
        return actual_tuple < required_tuple
    elif op == "==":
        return actual_tuple == required_tuple
    return False


def resolve_min_prereq_topological(
    family_min_prereq: dict[str, dict[str, str]],
    consumer_pin: dict[str, str],
) -> list[PrereqMismatch]:
    """7-plugin DAG topological resolve + min_prerequisite_version mismatch detection.

    ADR-096 §결정 1/2 dual carrier + topological resolve.

    Args:
        family_min_prereq: plugin → {dependency_plugin: semver_range}
            예: {"codeforge-requirements": {"codeforge": ">=5.5.0"}}
        consumer_pin: plugin → installed semver
            예: {"codeforge": "5.3.0", "codeforge-requirements": "5.3.0"}

    Returns:
        PrereqMismatch list (consumer_pin < plugin_min 인 (plugin, required_range, actual) tuple)
        empty list = all satisfied (PASS)
        detection only — 처리 (degraded/grace/hard fail) = UpgradeAgent §consumer-fallback 위임

    Topological order = [wrapper(codeforge), ...6 lane] (DAG invariant, ADR-096 §결정 2)
    cycle 부재 보장 — lane → wrapper 단방향, wrapper → lane 의존 없음.
    """
    mismatches: list[PrereqMismatch] = []

    # topological order로 순회 (wrapper 먼저)
    for plugin in TOPOLOGICAL_ORDER:
        plugin_prereqs = family_min_prereq.get(plugin, {})
        for dep_plugin, min_range in plugin_prereqs.items():
            actual_version = consumer_pin.get(dep_plugin, "")
            if not actual_version:
                # dep_plugin 버전 미설정 = mismatch (미설치 취급)
                mismatches.append(PrereqMismatch(
                    plugin=plugin,
                    required_range=min_range,
                    actual="(미설치)",
                ))
                continue

            try:
                satisfied = _satisfies_range(actual_version, min_range)
            except (VersionRangeError, Exception):
                # parse 실패 = mismatch 취급 (fallback trigger)
                mismatches.append(PrereqMismatch(
                    plugin=plugin,
                    required_range=min_range,
                    actual=actual_version,
                ))
                continue

            if not satisfied:
                mismatches.append(PrereqMismatch(
                    plugin=plugin,
                    required_range=min_range,
                    actual=actual_version,
                ))

    return mismatches


# ──────────────────────────── (c) walk_result aggregate ──────────────────────

def aggregate_walk_result(per_plugin_results: list[WalkResult]) -> WalkResult:
    """bundle tier 9 plugin walk_result 종합 → family walk_result.

    deterministic exit code mapping (change-plan §4.3 / §4.4).
    CFP-1199 F1: 9-plugin family 확장 (codeforge-deploy + codeforge-deploy-review, ADR-087/088).

    severity ordering (고 → 저):
      FAILED > PARTIAL_FAILURE > SUCCESS_WITH_DEGRADATION > SUCCESS

    Rules:
      ANY FAILED          → FAILED (최상위 severity)
      ANY PARTIAL_FAILURE → PARTIAL_FAILURE
      ANY DEGRADATION     → SUCCESS_WITH_DEGRADATION
      ALL SUCCESS         → SUCCESS

    closed_enum open_extension: false (ADR-093 §결정 2).

    Raises:
        ValueError: per_plugin_results 가 빈 list (bundle tier = 9 plugin 전체 필수)
    """
    if not per_plugin_results:
        raise ValueError(
            "per_plugin_results 가 빈 list — bundle tier = 9 plugin 전체 walk_result 필요"
        )

    # ANY FAILED → FAILED (최상위 severity, per-family rollback 완료 후 FAILED 보고)
    if any(r == WalkResult.FAILED for r in per_plugin_results):
        return WalkResult.FAILED

    # ANY PARTIAL_FAILURE → PARTIAL_FAILURE
    if any(r == WalkResult.PARTIAL_FAILURE for r in per_plugin_results):
        return WalkResult.PARTIAL_FAILURE

    # ANY DEGRADATION (no fail/partial) → SUCCESS_WITH_DEGRADATION
    if any(r == WalkResult.SUCCESS_WITH_DEGRADATION for r in per_plugin_results):
        return WalkResult.SUCCESS_WITH_DEGRADATION

    # ALL SUCCESS
    return WalkResult.SUCCESS


# ──────────────────────────── (d) marker_merge (R-2 흡수) ────────────────────
# reconcile-overlay.sh 3-way merge customization marker 보존 logic 흡수
# ADR-027 §결정 7.C (MARKER_NONE = wholesale + loss report) / §결정 7.D.3 (whole-line anchored)
# change-plan §11.2 R-2 흡수 설계 SSOT

_MARKER_BEGIN_RE = re.compile(
    r"^#\s*BEGIN\s+wrapper-managed\s*$",
    re.MULTILINE,
)
_MARKER_END_RE = re.compile(
    r"^#\s*END\s+wrapper-managed\s*$",
    re.MULTILINE,
)

# 마커 패턴 상수 (whole-line anchored — ADR-027 §결정 7.D.3)
MARKER_BEGIN = "# BEGIN wrapper-managed"
MARKER_END = "# END wrapper-managed"


def _has_marker(content: str) -> bool:
    """content 에 customization marker BEGIN+END 쌍이 있는지 확인."""
    return bool(_MARKER_BEGIN_RE.search(content) and _MARKER_END_RE.search(content))


def merge_with_marker(
    base_content: str,
    wrapper_content: str,
    consumer_content: str,
) -> tuple[str, bool, str]:
    """R-2 customization marker 보존 3-way merge.

    change-plan §11.2 R-2 흡수 설계:
    - BASE_OK + MARKER_VALID = 3-way merge (marker 안 wrapper wins, 밖 consumer preserve)
    - BASE_ABSENT + MARKER_VALID = 2-way first-reconcile (marker 안 wrapper, 밖 consumer)
    - MARKER_NONE = wholesale mirror + loss report (silent overwrite 0 — EPIC-AC-4)

    Args:
        base_content: 이전 wrapper SSOT (비교 기준 — empty = BASE_ABSENT)
        wrapper_content: 신규 wrapper SSOT (apply 대상)
        consumer_content: 현재 consumer overlay 내용

    Returns:
        (merged_content, loss_occurred, loss_report)
        - merged_content: 3-way merge 결과
        - loss_occurred: True if consumer customization 손실 (loss_report 필요)
        - loss_report: 손실 발생 시 user-visible 보고 문자열

    Invariants:
        - marker 안 = wrapper_content wins (SSOT)
        - marker 밖 = consumer_content preserve (byte-identical)
        - integrity fingerprint check 의무 (호출자 책임)
        - MARKER_NONE → wholesale wrapper_content + loss_report
    """
    has_consumer_marker = _has_marker(consumer_content)

    # MARKER_NONE — wholesale + loss report (silent overwrite 0, EPIC-AC-4)
    if not has_consumer_marker:
        loss_report = (
            "[R-2 loss_report] MARKER_NONE detected — consumer overlay에 "
            f"customization marker ({MARKER_BEGIN} / {MARKER_END}) 없음. "
            "wholesale wrapper 내용으로 대체 (consumer customization 손실 가능). "
            "ADR-027 §결정 7.C — 사용자 확인 필요 (silent overwrite 0)."
        )
        return wrapper_content, True, loss_report

    # MARKER_VALID — 3-way merge (marker 안 wrapper wins, 밖 consumer preserve)
    # marker 안 = wrapper_content 의 marker 블록 내용 추출
    wrapper_inner = _extract_marker_inner(wrapper_content)
    consumer_outer_before, consumer_outer_after = _split_consumer_outer(consumer_content)

    # 3-way merge 구성 (marker 안 wrapper, 밖 consumer preserve)
    merged_lines = []
    merged_lines.append(consumer_outer_before)
    merged_lines.append(MARKER_BEGIN)
    if wrapper_inner:
        merged_lines.append(wrapper_inner)
    merged_lines.append(MARKER_END)
    merged_lines.append(consumer_outer_after)

    merged = "\n".join(filter(lambda x: x is not None, merged_lines))
    return merged, False, ""


def _extract_marker_inner(content: str) -> str:
    """content 에서 marker 블록 안(BEGIN~END 사이) 내용 추출."""
    begin_m = _MARKER_BEGIN_RE.search(content)
    end_m = _MARKER_END_RE.search(content)
    if not begin_m or not end_m:
        return ""
    inner = content[begin_m.end():end_m.start()].strip()
    return inner


def _split_consumer_outer(content: str) -> tuple[str, str]:
    """consumer content 에서 marker 블록 바깥 부분을 앞/뒤로 분리.

    consumer preserve (byte-identical — integrity fingerprint check 의무).
    """
    begin_m = _MARKER_BEGIN_RE.search(content)
    end_m = _MARKER_END_RE.search(content)
    if not begin_m or not end_m:
        return content, ""

    before = content[:begin_m.start()].rstrip("\n")
    after = content[end_m.end():].lstrip("\n")
    return before, after


# ──────────────────────────── (f) apply_overlay_file (CFP-1177) ───────────────
# consumer overlay 파일에 customization marker 보존 3-way merge 를 안전하게 적용하는
# orchestration 함수 (D1 — ADR-027 Amendment 9 패러다임 무관 preserved layer).
#
# SSOT: docs/adr/ADR-027-consumer-adoption-protocol.md Amendment 9
# 관련: merge_with_marker (위 §d — 이 함수가 호출하는 primitive)
#       reconcile-overlay.sh §7.4.1(g) abort-before-touch analog (filesystem 0)
#
# 책임 분리:
#   - 본 함수 = 순수 함수 (문자열 입력 → OverlayApplyResult 출력, filesystem 접촉 0)
#   - filesystem write + loss-report 표면화 = 호출자 책임 (.sh dispatcher)
#   이는 reconcile-overlay.sh 의 분리 패턴 (shell 오케스트레이션 / python 계산) 답습.


@dataclass(frozen=True)
class OverlayApplyResult:
    """apply_overlay_file 결과 frozen dataclass (5 필드 — ADR-027 Amendment 9).

    Fields:
        merged_content:             3-way merge 결과 문자열 (integrity 위반 시 consumer_content 원본)
        loss_occurred:              True = consumer customization 손실 (MARKER_NONE 경로)
        loss_report:                손실 발생 시 user-visible 보고 문자열 (silent overwrite 0 — EPIC-AC-4)
        integrity_ok:               True = marker 밖 영역 byte-identical 보존 검증 통과 / MARKER_NONE N/A
        integrity_violation_reason: integrity 위반 시 사유 문자열 (정상 경로 = "")
    """
    merged_content: str
    loss_occurred: bool
    loss_report: str
    integrity_ok: bool
    integrity_violation_reason: str


def apply_overlay_file(
    wrapper_content: str,
    consumer_content: str,
    base_content: str = "",
) -> OverlayApplyResult:
    """consumer overlay 파일에 customization marker 보존 3-way merge 적용 (순수 함수).

    ADR-027 Amendment 9 — paradigm-agnostic preserved layer invariant:
      - MARKER_VALID 경로: marker 안 = wrapper SSOT wins (무조건), 밖 = consumer byte-identical 보존
      - MARKER_NONE 경로: wholesale wrapper mirror + loss_report (silent overwrite 0 — EPIC-AC-4)
      - integrity fingerprint check 의무 (merge_with_marker docstring 의 "호출자 책임" 이행)

    Args:
        wrapper_content:  신규 wrapper SSOT 내용 (apply 대상)
        consumer_content: 현재 consumer overlay 내용
        base_content:     이전 wrapper SSOT (비교 기준 — 기본값 "" = BASE_ABSENT).
                          NOTE: marker 안 = wrapper_content unconditionally wins.
                          base_content 는 marker 안 merge 에 사용되지 않는다 (by-design).
                          reconcile-protocol-v1 시그니처 호환성 유지 목적으로만 보존.

    Returns:
        OverlayApplyResult:
          - MARKER_VALID 정상: merged_content=merge 결과, loss_occurred=False,
                               loss_report="", integrity_ok=True, integrity_violation_reason=""
          - MARKER_NONE:       merged_content=wrapper_content, loss_occurred=True,
                               loss_report=<보고>, integrity_ok=True, integrity_violation_reason=""
          - INTEGRITY 위반:    merged_content=consumer_content (fallback),
                               integrity_ok=False, integrity_violation_reason=<사유>

    DRY 준수: merge_with_marker primitive 재사용 (marker logic 재구현 금지 — ADR-027 §결정 7.B).
    filesystem 접촉 0 — 순수 함수 invariant.
    """
    # Step 1: merge_with_marker primitive 호출
    merged, loss_occurred, loss_report = merge_with_marker(
        base_content, wrapper_content, consumer_content
    )

    # Step 2: MARKER_NONE 경로 — integrity check N/A (wholesale overwrite 이미 완료)
    if not _has_marker(consumer_content):
        return OverlayApplyResult(
            merged_content=merged,
            loss_occurred=loss_occurred,
            loss_report=loss_report,
            integrity_ok=True,
            integrity_violation_reason="",
        )

    # Step 3: MARKER_VALID 경로 — integrity fingerprint check
    # consumer marker-outside 원본과 merge 결과의 marker-outside 를 byte-identical 비교.
    # merge_with_marker docstring 이 위임한 "호출자 책임" 영역 이행.
    consumer_before, consumer_after = _split_consumer_outer(consumer_content)
    merged_before, merged_after = _split_consumer_outer(merged)

    outside_preserved = (
        merged_before == consumer_before and merged_after == consumer_after
    )

    if not outside_preserved:
        # abort-before-touch analog (reconcile-overlay.sh §7.4.1(g)):
        # corrupted merge 는 절대 내보내지 않는다 → consumer_content 원본 fallback.
        reason_parts = []
        if merged_before != consumer_before:
            reason_parts.append(
                f"marker 앞 영역 불일치 (before: 기대 {len(consumer_before)}자, "
                f"실제 {len(merged_before)}자)"
            )
        if merged_after != consumer_after:
            reason_parts.append(
                f"marker 뒤 영역 불일치 (after: 기대 {len(consumer_after)}자, "
                f"실제 {len(merged_after)}자)"
            )
        violation_reason = (
            "[integrity-check-FAIL] marker 밖 영역 byte-identical 보존 실패. "
            + " / ".join(reason_parts)
            + " — abort-before-touch: consumer_content 원본 유지 (ADR-027 Amendment 9)."
        )
        return OverlayApplyResult(
            merged_content=consumer_content,  # fallback to original
            loss_occurred=False,
            loss_report="",
            integrity_ok=False,
            integrity_violation_reason=violation_reason,
        )

    # integrity OK — 정상 반환
    return OverlayApplyResult(
        merged_content=merged,
        loss_occurred=loss_occurred,
        loss_report=loss_report,
        integrity_ok=True,
        integrity_violation_reason="",
    )


# ──────────────────────────── (g) tier classification (CFP-1179) ─────────────
# ADR-063 Amendment 8 §결정 19 — Tier 분리 (marketplace atomic invariant Tier scope 명확화)
# Tier 1 (wrapper bundle): codeforge wrapper — 3-file atomic (plugin.json + CHANGELOG.md + marketplace.json)
#   + family atomic 의무 (bundle walk = walk-bundle-7-plugins.sh)
# Tier 2 (lane per-walk): lane plugin — 2-file atomic (plugin.json + marketplace.json)
#   + family atomic 없음 (per-plugin 독립 walk = walk-single-plugin.sh)
# fail-closed-unknown: 알 수 없는 plugin → ValueError (ADR-083 fail-closed-unknown 선례 정합)
#
# family roster SSOT = TOPOLOGICAL_ORDER (위 §b — 현 walk-infra family roster, ADR-096 §결정 2).
#   LANE_PLUGINS 는 TOPOLOGICAL_ORDER 에서 derive (dual-roster drift 차단 — single SSOT).
# CFP-1059 9-plugin 정합 (realized in CFP-1199): ADR-063 Amendment 7 §결정 18 이 family scope 를
#   7 → 9 plugin (codeforge-deploy + codeforge-deploy-review, ADR-087/088 Accepted) 확장.
#   CFP-1199 F1 — TOPOLOGICAL_ORDER 9-plugin 확장 완료: deploy lane 의존성 결정 (wrapper 단방향,
#   pmo 이후 보수 lifecycle 순서) + TOPOLOGICAL_ORDER 2 entry 추가. LANE_PLUGINS 가
#   TOPOLOGICAL_ORDER 에서 derive 하므로 roster 자동 정합 (수동 동기화 0, §결정 19 참조).
# MAJOR-atomic 비약화: Amendment 7 §결정 18 의 "MAJOR bump 시 family 전체 동시 atomic" invariant 는
#   Tier 분리로 약화되지 않음 — MAJOR bump 은 Tier 1 bundle (family_atomic) 강제,
#   Tier 2 per-walk 독립성은 MINOR / PATCH bump 영역에만 적용 (§결정 19 참조).

# Tier 상수 (str 값 — WalkResult Enum 스타일과 달리 str 직접 사용, 호출자 비교 단순화)
TIER_1_WRAPPER = "tier_1_wrapper"
TIER_2_LANE = "tier_2_lane"

# codeforge family plugin 이름 상수 — TOPOLOGICAL_ORDER 에서 derive (single roster SSOT)
WRAPPER_PLUGIN = "codeforge"
# LANE_PLUGINS = TOPOLOGICAL_ORDER 의 wrapper 외 전체 (drift 차단 — 확장 시 자동 정합)
LANE_PLUGINS: frozenset = frozenset(TOPOLOGICAL_ORDER) - {WRAPPER_PLUGIN}


@dataclass(frozen=True)
class AtomicScope:
    """Tier 별 atomic coordination scope.

    ADR-063 §결정 19 — Tier 분리 규칙:
      Tier 1 (wrapper): files = 3-tuple (plugin.json + CHANGELOG.md + marketplace.json)
                        family_atomic = True  (family bundle walk 의무)
      Tier 2 (lane):    files = 2-tuple (plugin.json + marketplace.json)
                        family_atomic = False (per-plugin 독립 walk 허용 — MINOR/PATCH only)

    MAJOR-atomic 비약화 (Amendment 7 §결정 18): MAJOR bump 은 Tier 무관 family 전체 atomic 강제 —
      MAJOR bump 시 Tier 2 도 Tier 1 bundle (family_atomic) 경로로 강제 routing (§결정 19).
      본 helper 의 per-tier base scope = MINOR/PATCH bump 영역 (per-plugin sibling sync 보존).

    참조: TOPOLOGICAL_ORDER / walk-bundle-7-plugins.sh / walk-single-plugin.sh
    """
    files: tuple  # atomic coordination 대상 파일명 tuple
    family_atomic: bool  # True = family bundle 동시 bump 의무 / False = per-plugin 독립 허용


def classify_tier(plugin_name: str) -> str:
    """plugin 이름 → Tier 분류 (ADR-063 §결정 19).

    Args:
        plugin_name: plugin 이름 (예: "codeforge", "codeforge-design")

    Returns:
        TIER_1_WRAPPER ("tier_1_wrapper") — wrapper plugin
        TIER_2_LANE    ("tier_2_lane")    — lane plugin (TOPOLOGICAL_ORDER 의 wrapper 외 전체)

    Raises:
        ValueError: 알 수 없는 plugin (fail-closed — ADR-083 fail-closed-unknown 선례 정합)
                    silent default 금지 (unknown = 분류 불가, 호출자 오류 즉시 표면화)
    """
    if plugin_name == WRAPPER_PLUGIN:
        return TIER_1_WRAPPER
    if plugin_name in LANE_PLUGINS:
        return TIER_2_LANE
    raise ValueError(
        f"알 수 없는 plugin: '{plugin_name}' — "
        f"codeforge family {1 + len(LANE_PLUGINS)}종 ({WRAPPER_PLUGIN} + {sorted(LANE_PLUGINS)}) 에 없음. "
        "fail-closed (ADR-083 §결정 3 fail-closed-unknown 정합, silent default 금지)."
    )


def atomic_scope_for_tier(tier: str) -> AtomicScope:
    """Tier → atomic coordination scope 반환 (ADR-063 §결정 19).

    Tier 1 (wrapper bundle):
      - files = ("plugin.json", "CHANGELOG.md", "marketplace.json")
      - family_atomic = True
      - 근거: §결정 1 3-file atomic invariant + ADR-016 family-scope atomic bundle (현 TOPOLOGICAL_ORDER roster)

    Tier 2 (lane per-walk):
      - files = ("plugin.json", "marketplace.json")
      - family_atomic = False
      - 근거: per-plugin 독립 walk 허용 — 단, 자기 plugin.json + marketplace.json 2-file atomic 유지
      - cross-Tier 의존 = resolve_min_prereq_topological() 재사용 (재구현 금지)

    Args:
        tier: TIER_1_WRAPPER 또는 TIER_2_LANE

    Returns:
        AtomicScope(files=..., family_atomic=...)

    Raises:
        ValueError: 알 수 없는 tier 값 (fail-closed)
    """
    if tier == TIER_1_WRAPPER:
        return AtomicScope(
            files=("plugin.json", "CHANGELOG.md", "marketplace.json"),
            family_atomic=True,
        )
    if tier == TIER_2_LANE:
        return AtomicScope(
            files=("plugin.json", "marketplace.json"),
            family_atomic=False,
        )
    raise ValueError(
        f"알 수 없는 tier: '{tier}' — TIER_1_WRAPPER({TIER_1_WRAPPER!r}) 또는 "
        f"TIER_2_LANE({TIER_2_LANE!r}) 만 허용. fail-closed."
    )


# ──────────────────────────── (e) importance_score hook (CFP-1173) ────────────
# Story-5 placeholder → importance_score.py 실 wire (brainstorming 결정 4)
# plan stage 각 entry blast-radius importance_score 계산
# SSOT: docs/change-plans/cfp-1173-blast-radius-parallel.md §3

def _import_importance_score_module() -> Optional[object]:
    """importance_score 모듈 lazy import (circular import 방지).

    Returns:
        importance_score 모듈 (성공) / None (미설치 — graceful degradation)
    """
    import importlib
    import os as _os

    # 같은 lib/ 디렉토리 우선
    _lib_dir = _os.path.dirname(_os.path.abspath(__file__))
    import sys as _sys
    if _lib_dir not in _sys.path:
        _sys.path.insert(0, _lib_dir)

    try:
        return importlib.import_module("importance_score")
    except ImportError:
        return None


def calc_entry_importance_score(
    touched_lanes_count: int,
    breaking_change_marker: bool = False,
    contract_major_bump: int = 0,
) -> int:
    """plan stage entry blast-radius importance_score 계산 hook.

    importance_score.py SSOT 위임 (CFP-1173 실 wire).
    Story-5 walk plan stage 에서 호출 — 각 changelog entry 에 score 부여.

    Args:
        touched_lanes_count: 영향받는 lane 수 (0~7)
        breaking_change_marker: BREAKING CHANGE 마커 여부 (기본 False)
        contract_major_bump: inter-plugin contract MAJOR bump 수 (기본 0)

    Returns:
        importance_score (int, 0 이상) — 높을수록 blast radius 높음.
        importance_score.py 미설치 시 fallback = touched_lanes_count × 3 (graceful degradation).

    Contract: imperative-walker-protocol-v1 §중요도 순서 (blast-radius 3-tuple)
    SSOT: scripts/lib/importance_score.py (ADR-061 Python SSOT)
    """
    mod = _import_importance_score_module()
    if mod is not None:
        # importance_score.py 실 wire (CFP-1173 Story-5 placeholder 해소)
        entry = mod.BlastRadiusTuple(
            touched_lanes_count=touched_lanes_count,
            breaking_change_marker=breaking_change_marker,
            contract_major_bump=contract_major_bump,
        )
        return mod.calc_importance_score(entry)

    # graceful degradation (importance_score.py 미설치 — touched_lanes × WEIGHT_LANES=3)
    _FALLBACK_WEIGHT = 3
    return touched_lanes_count * _FALLBACK_WEIGHT


# ──────────────────────────── (f) walk_report hook (CFP-1175) ────────────────
# walk_report.py 연동 (4-field 완료 보고 + TodoWrite 4-marker visualization)
# graceful degradation: walk_report 미설치 시 ImportError 무시 (no-op hook)
# SSOT: docs/change-plans/cfp-1175-walk-visualization.md §3
# ADR-093 completion report 4-field / ADR-038 TodoWrite 4-marker

def _import_walk_report_module() -> Optional[object]:
    """walk_report 모듈 lazy import (circular import 방지).

    Returns:
        walk_report 모듈 (성공) / None (미설치 — graceful degradation)
    """
    import importlib
    import os as _os

    _lib_dir = _os.path.dirname(_os.path.abspath(__file__))
    import sys as _sys
    if _lib_dir not in _sys.path:
        _sys.path.insert(0, _lib_dir)

    try:
        return importlib.import_module("walk_report")
    except ImportError:
        return None


def build_walk_completion_report(
    walk_result: WalkResult,
    from_version: str,
    to_version: str,
    target_version_release_date: str,
    changelog_entries: list,
) -> Optional[object]:
    """walk 완료 보고 CompletionReport 생성 hook (walk_report.py 위임).

    walk_plan.py 에서 호출 가능한 completion report 생성 facade.
    walk_report.py 가 설치되지 않은 경우 None 반환 (graceful degradation).

    Args:
        walk_result: WalkResult enum (4-value closed-set)
        from_version: consumer installed 버전 (업그레이드 전)
        to_version: 업그레이드 후 버전 (changelog latest)
        target_version_release_date: target 버전 release 일자 (ISO 8601 date)
        changelog_entries: ChangelogEntry list (walk_changelog() 결과)

    Returns:
        CompletionReport (walk_report.build_completion_report()) / None (미설치)

    ADR-093 §결정 1 4-field:
      from_version / to_version / target_version_release_date / key_changes_summary
    """
    mod = _import_walk_report_module()
    if mod is None:
        return None
    return mod.build_completion_report(
        walk_result=walk_result,
        from_version=from_version,
        to_version=to_version,
        target_version_release_date=target_version_release_date,
        changelog_entries=changelog_entries,
    )


def render_walk_progress_items(steps: list) -> list[str]:
    """walk step 리스트 → TodoWrite 4-marker render 문자열 리스트 hook.

    walk_report.py render_walk_todo_items() 위임.
    walk_report 미설치 시 빈 리스트 반환 (graceful degradation).

    Args:
        steps: WalkStep list (walk_report.WalkStep 객체 — walk_report 모듈 import 필요)

    Returns:
        list[str] — 각 원소 = "{marker} {name}" (TodoWrite content 형태)
        walk_report 미설치 = [] (graceful degradation)

    ADR-038 §결정 2 4-marker (Amendment 4 vocab):
      ⬜ PENDING / ⏳ IN_PROGRESS / ✅ COMPLETED / 🔄 FIX_DETECTED
    """
    mod = _import_walk_report_module()
    if mod is None:
        return []
    return mod.render_walk_todo_items(steps)


# ──────────────────────────── (h) consumer-applicability filter (CFP-1293) ────
# ADR-083 Amendment 3 §결정 5 — walker apply Stage D consumer-applicability filter
#
# 책임:
#   - FilterDecision frozen dataclass: 4-way enum filter 결과 (immutable)
#   - apply_consumer_applicability_filter(): 순수 함수 (whitelist read only, filesystem-only)
#   - invoke_detect_repo_kind(): detect-repo-kind.py subprocess wrapper
#
# 설계 결정 (Change Plan §3.4 / §3.5 / §3.6):
#   - apply_overlay_file() 순수 함수 invariant 보존 (signature 변경 0건)
#   - caller 영역 (apply_changelog_entry 함수) 에 hook insertion
#   - subprocess call = ADR-005 self-app exemption + ADR-009 wrapper-only boundary 보존
#
# CFP-899 reconcile-overlay.sh §4.12 hook pattern 답습 (DRY 준수)
# SSOT: docs/change-plans/cfp-1293-walker-filter-wire.md §3.4/§3.5/§3.6


import subprocess as _subprocess


@dataclass(frozen=True)
class FilterDecision:
    """ADR-083 consumer-applicability filter 결정 결과 (immutable frozen dataclass).

    CFP-1293 Phase 2 — walker apply Stage D per-entry filter hook 결과 캡슐화.

    Fields:
        decision:      enum "proceed" | "skip" | "abort"
                       - proceed: 해당 workflow 파일 cp 진행
                       - skip:    consumer 분류 + whitelist miss → cp bypass
                       - abort:   unknown / whitelist 읽기 실패 → fail-closed abort
        repo_kind:     detect-repo-kind.py 반환 enum
                       "plugin" | "consumer" | "mixed" | "unknown"
        reason:        결정 사유 (skip / abort 시 의무, proceed 시 "" 가능)
        skip_filename: skip 결정 시 대상 basename (proceed / abort 시 "")

    ADR-083 §결정 5 4-way truth-table:
        plugin / mixed → proceed (full workflow set, 0 file skip)
        consumer + whitelist match → proceed
        consumer + whitelist miss  → skip + skip_filename + reason
        unknown (or whitelist fail) → abort (fail-closed, ADR-068 I-3)

    DRY 준수: reconcile-overlay.sh §4.12 hook bash case statement 의 Python translate.
    """
    decision: str       # enum: "proceed" | "skip" | "abort"
    repo_kind: str      # enum: "plugin" | "consumer" | "mixed" | "unknown"
    reason: str         # 결정 사유 (skip/abort 의무, proceed="" 가능)
    skip_filename: str  # skip 시 file basename (proceed/abort = "")


def apply_consumer_applicability_filter(
    filename: str,
    repo_kind: str,
    whitelist_path: "Path",
) -> FilterDecision:
    """ADR-083 §결정 5 4-way enum filter (순수 함수, whitelist filesystem read only).

    Args:
        filename:       workflow yml basename (예: "story-init.yml")
        repo_kind:      detect-repo-kind.py 반환 enum
                        "plugin" | "consumer" | "mixed" | "unknown"
        whitelist_path: consumer_applicable_workflows.txt absolute path (Path-like)

    Returns:
        FilterDecision — decision + repo_kind + reason + skip_filename

    Decision rules (ADR-083 §결정 5 4-way truth-table):
        plugin / mixed → FilterDecision(decision="proceed", ...)
        consumer:
            whitelist match → FilterDecision(decision="proceed", ...)
            whitelist miss  → FilterDecision(decision="skip", skip_filename=filename, ...)
            whitelist read fail → FilterDecision(decision="abort", ...)
        unknown → FilterDecision(decision="abort", ...)
        비-enum value → FilterDecision(decision="abort", ...) [defensive]

    DRY 준수: apply_overlay_file() signature 변경 0건 (순수 함수 invariant 보존 — CFP-1177 D1).
    filesystem read: whitelist 파일 1건만 (network 0 invariant — ADR-083 §결정 2).
    """
    from pathlib import Path as _Path

    # plugin / mixed: full workflow set (filter skip 0, wrapper self-app exemption)
    if repo_kind in ("plugin", "mixed"):
        return FilterDecision(
            decision="proceed",
            repo_kind=repo_kind,
            reason=f"full workflow set (repo_kind={repo_kind})",
            skip_filename="",
        )

    # consumer: positive whitelist grep
    if repo_kind == "consumer":
        try:
            wl_path = _Path(whitelist_path)
            content = wl_path.read_text(encoding="utf-8")
            entries = {
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.strip().startswith("#")
            }
        except (FileNotFoundError, OSError) as exc:
            # whitelist 부재 / read fail → fail-closed (abort, unknown 동형 처리)
            return FilterDecision(
                decision="abort",
                repo_kind="unknown",
                reason=f"whitelist read fail: {exc}",
                skip_filename="",
            )
        if filename in entries:
            return FilterDecision(
                decision="proceed",
                repo_kind="consumer",
                reason="whitelist match",
                skip_filename="",
            )
        return FilterDecision(
            decision="skip",
            repo_kind="consumer",
            reason=f"whitelist miss (consumer-non-applicable)",
            skip_filename=filename,
        )

    # unknown → fail-closed unconditional (ADR-083 §결정 4, ADR-068 I-3)
    if repo_kind == "unknown":
        return FilterDecision(
            decision="abort",
            repo_kind="unknown",
            reason="repo_kind=unknown — fail-closed (ADR-083 §결정 4)",
            skip_filename="",
        )

    # 비-enum value (defensive fail-closed)
    return FilterDecision(
        decision="abort",
        repo_kind="unknown",
        reason=f"unknown repo_kind enum value '{repo_kind}' — fail-closed",
        skip_filename="",
    )


def invoke_detect_repo_kind(
    consumer_root: "Path",
    detect_repo_kind_py: "Path | None" = None,
) -> str:
    """detect-repo-kind.py subprocess call (ADR-061 외부 .py + ADR-005 self-app exemption).

    Args:
        consumer_root:       target repo root (Path-like 또는 str)
        detect_repo_kind_py: templates/scripts/detect-repo-kind.py absolute path (Path-like)

    Returns:
        enum str: "plugin" | "consumer" | "mixed" | "unknown"

    Decision:
        - subprocess stdout = enum literal → 반환
        - subprocess crash / timeout / 비-enum exit → "unknown" (fail-closed fallback)
        - timeout default = 5s (DoS 보호 — §9 보안 평가 정합)

    Invariants (ADR-083 §결정 2 filesystem-only):
        - subprocess.run capture_output=True (network 0 invariant — detect-repo-kind.py 자체)
        - timeout=5 (DoS 보호)
        - check=False (exit code 자체가 enum 정보 — subprocess.CalledProcessError 불필요)

    CFP-899 reconcile-overlay.sh §4.12 hook pattern 답습 (subprocess call paradigm).
    ADR-005 §결정 1 self-app exemption: templates/scripts/ 는 consumer-distributable →
      wrapper scripts/lib/ 안 직접 import 금지 → subprocess call boundary 보존.
    """
    from pathlib import Path as _Path

    _VALID_KINDS = ("plugin", "consumer", "mixed", "unknown")

    try:
        result = _subprocess.run(
            ["python3", str(_Path(detect_repo_kind_py)), "--repo-root", str(_Path(consumer_root))],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (_subprocess.TimeoutExpired, OSError):
        return "unknown"

    output = result.stdout.strip()
    if output in _VALID_KINDS:
        return output
    return "unknown"


# ──────────────────────────── (i) apply_changelog_entry — Stage D caller (CFP-1293) ─────────
# walker apply Stage D 진입점: consumer-applicability filter (R-3) + overlay apply (R-2) 통합.
# Change Plan §3.4 / §3.5 / §3.6 — 2-layer (Step A preflight 1회 + Step D per-entry hook).
#
# 설계 결정:
#   - apply_overlay_file() 순수 함수 invariant 보존 (signature 변경 0건 — CFP-1177 D1)
#   - Step A preflight: invoke_detect_repo_kind() 1회 호출 → repo_kind cache
#     unknown → WalkStageAbortError raise (abort-before-touch, filesystem touch 0)
#   - Step D per-entry: apply_consumer_applicability_filter() per-entry whitelist check
#     skip → filter_skip_report append + skip log (apply_overlay_file 미호출)
#     abort → WalkStageAbortError raise
#     proceed → apply_overlay_file() call (기존 R-2 marker_merge 경로)
#
# ADR refs:
#   ADR-083 §결정 5 — 4-way truth-table (wire location SSOT)
#   ADR-027 Amendment 9 — apply_overlay_file 순수 함수 invariant (no signature change)
#   ADR-061 — Python script-writing convention
#   Change Plan §3.4 Decision 4 / §3.5 Decision 5
#
# F-CR-001 (CodeReview iter 1) — caller 영역 hook insertion: walker apply Stage D 영역에서
#   apply_consumer_applicability_filter + invoke_detect_repo_kind 실 호출 0 grep match drift 해소.
#   walker contract §2.E.4 status=walker_apply_stage_d_wire_active 선언 ↔ 실 wire 정합.


class WalkStageAbortError(Exception):
    """walker apply Stage D abort 예외 (fail-closed — filesystem touch 0 상태 abort).

    UpgradeAgent.md Stage A.1 abort-before-touch 영역 + Stage D abort decision 공용.
    reason 필드: FilterDecision.reason verbatim carry-over (audit trail 의무).
    """

    def __init__(self, reason: str, repo_kind: str = "unknown"):
        super().__init__(reason)
        self.reason = reason
        self.repo_kind = repo_kind


@dataclass
class ApplyChangelogEntryResult:
    """apply_changelog_entry 단일 entry 적용 결과.

    walker apply Stage D per-entry 적용 결과 캡슐화.

    Fields:
        applied:            True = overlay apply 완료 (R-2 3-way merge 포함)
        skipped:            True = consumer-non-applicable filter skip (R-3)
        loss_occurred:      True = MARKER_NONE 경로 (wholesale mirror + loss_report 발화)
        loss_report:        MARKER_NONE 시 user-visible 보고 문자열
        integrity_ok:       True = marker 밖 영역 byte-identical 보존 검증 통과
        integrity_violation_reason: integrity 위반 사유 (정상 "" — abort-before-touch signal)
        filter_reason:      skip 시 FilterDecision.reason verbatim (proceed 시 "")
    """
    applied: bool
    skipped: bool
    loss_occurred: bool
    loss_report: str
    integrity_ok: bool
    integrity_violation_reason: str
    filter_reason: str


def apply_changelog_entry(
    filename: str,
    wrapper_content: str,
    consumer_content: str,
    repo_kind: str,
    whitelist_path: "Path",
    base_content: str = "",
) -> ApplyChangelogEntryResult:
    """walker apply Stage D per-entry 적용 — consumer-applicability filter (R-3) + overlay apply (R-2).

    Change Plan §3.4 Decision 4 / §3.5 Decision 5 — 2-layer hook:
      Step D.1: apply_consumer_applicability_filter (per-entry whitelist check)
      Step D.2: apply_overlay_file (R-2 customization marker 3-way merge — filter proceed 시만)

    Args:
        filename:         workflow yml basename (예: "story-init.yml")
        wrapper_content:  신규 wrapper SSOT 내용 (apply 대상)
        consumer_content: 현재 consumer overlay 내용
        repo_kind:        Step A preflight detect 결과 cache (invoke_detect_repo_kind() 반환값)
                          "plugin" | "consumer" | "mixed" — "unknown" = WalkStageAbortError 발생 (Step A abort-before-touch 후 도달 불가 원칙, 방어적 abort 보장)
        whitelist_path:   consumer_applicable_workflows.txt absolute path (Path-like)
        base_content:     이전 wrapper SSOT (비교 기준 — 기본값 "" = BASE_ABSENT)

    Returns:
        ApplyChangelogEntryResult:
          - applied=True:  proceed 경로 (overlay apply 완료, R-2 3-way merge 포함)
          - skipped=True:  consumer-non-applicable skip (R-3 — apply_overlay_file 미호출)
          - applied=False + skipped=False: abort 경로 없음 (WalkStageAbortError raise)

    Raises:
        WalkStageAbortError: filter decision = "abort" (fail-closed — filesystem touch 0 보장 상태 abort)
                             repo_kind = "unknown" 도달 시 동일 (Step A 에서 이미 차단 원칙이나 방어적 보장)

    Invariants:
        - apply_overlay_file() 순수 함수 invariant 보존 (signature 변경 0건 — CFP-1177 D1)
        - filter_skip_report 누적은 호출자 책임 (본 함수 = 단일 entry 한정 순수 함수 인터페이스)
        - abort-before-touch: abort 결정 시 consumer filesystem 미변경 보장
        - DRY 준수: apply_overlay_file / apply_consumer_applicability_filter 재사용 (재구현 0건)

    ADR refs:
        ADR-083 §결정 5 — 4-way truth-table (filter decision logic SSOT)
        ADR-027 Amendment 9 — apply_overlay_file signature 0건 변경 보장
        Change Plan §3.4 Decision 4 — filter hook insertion point
        Change Plan §3.5 Decision 5 — 2-layer (Step A preflight + Step D per-entry)
    """
    # Step D.1 — consumer-applicability filter (R-3 hook, CFP-1293 / ADR-083 Amd 3)
    filter_decision = apply_consumer_applicability_filter(
        filename=filename,
        repo_kind=repo_kind,
        whitelist_path=whitelist_path,
    )

    if filter_decision.decision == "abort":
        # fail-closed abort (unknown repo_kind / whitelist read fail → abort-before-touch)
        raise WalkStageAbortError(
            reason=filter_decision.reason,
            repo_kind=filter_decision.repo_kind,
        )

    if filter_decision.decision == "skip":
        # consumer-non-applicable: apply_overlay_file 미호출 (filesystem touch 0)
        return ApplyChangelogEntryResult(
            applied=False,
            skipped=True,
            loss_occurred=False,
            loss_report="",
            integrity_ok=True,
            integrity_violation_reason="",
            filter_reason=filter_decision.reason,
        )

    # filter_decision.decision == "proceed" → 정상 apply (R-2 customization marker 3-way merge)
    # Step D.2 — apply_overlay_file (순수 함수, signature 변경 0건 — CFP-1177 D1)
    overlay_result = apply_overlay_file(
        wrapper_content=wrapper_content,
        consumer_content=consumer_content,
        base_content=base_content,
    )

    return ApplyChangelogEntryResult(
        applied=True,
        skipped=False,
        loss_occurred=overlay_result.loss_occurred,
        loss_report=overlay_result.loss_report,
        integrity_ok=overlay_result.integrity_ok,
        integrity_violation_reason=overlay_result.integrity_violation_reason,
        filter_reason="",
    )


# ──────────────────────────── CLI entry point ─────────────────────────────────
# (참조용 — 실제 CLI 진입점은 walk-single-plugin.sh / walk-bundle-7-plugins.sh)

if __name__ == "__main__":
    # sanity check self-test (ADR-061 §결정 3 sanity check 3종 중 sample)
    print("walk_plan.py sanity check:")
    print(f"  TOPOLOGICAL_ORDER: {TOPOLOGICAL_ORDER}")
    print(f"  WalkResult values: {[r.value for r in WalkResult]}")
    print(f"  EXIT_CODE_MAP: { {k.value: v for k, v in EXIT_CODE_MAP.items()} }")

    # D7 동결 assert (ADR-118 / CFP-2170) — 9-tuple 순서값 정확 list 동등 비교
    # (entry 1개 swap / 추가 / 삭제 모두 FAIL — 단순 phrasing 아닌 검증 분기)
    _EXPECTED_TOPOLOGICAL_ORDER = [
        "codeforge", "codeforge-requirements", "codeforge-design",
        "codeforge-review", "codeforge-develop", "codeforge-test",
        "codeforge-pmo", "codeforge-deploy", "codeforge-deploy-review",
    ]
    assert TOPOLOGICAL_ORDER == _EXPECTED_TOPOLOGICAL_ORDER, (
        f"D7 violation (ADR-118): TOPOLOGICAL_ORDER 순서값 변경 감지: {TOPOLOGICAL_ORDER}"
    )
    assert get_topological_order() == _EXPECTED_TOPOLOGICAL_ORDER
    print("  TOPOLOGICAL_ORDER == _EXPECTED_TOPOLOGICAL_ORDER (D7 동결, 9-tuple) ✓")

    # aggregate_walk_result sanity
    result = aggregate_walk_result([WalkResult.SUCCESS] * 9)
    assert result == WalkResult.SUCCESS, f"sanity FAIL: {result}"
    print("  aggregate_walk_result([SUCCESS]*9) = SUCCESS ✓")

    result = aggregate_walk_result([WalkResult.SUCCESS, WalkResult.FAILED])
    assert result == WalkResult.FAILED, f"sanity FAIL: {result}"
    print("  aggregate_walk_result([SUCCESS, FAILED]) = FAILED ✓")

    # importance_score hook sanity (CFP-1173)
    score_zero = calc_entry_importance_score(0, False, 0)
    assert score_zero == 0, f"sanity FAIL importance_score(0,False,0): {score_zero}"
    print(f"  calc_entry_importance_score(0, False, 0) = 0 ✓")

    score_basic = calc_entry_importance_score(2, False, 0)
    assert score_basic > 0, f"sanity FAIL importance_score(2,False,0): {score_basic}"
    print(f"  calc_entry_importance_score(2, False, 0) = {score_basic} ✓")

    score_break = calc_entry_importance_score(2, True, 0)
    assert score_break > score_basic, f"sanity FAIL breaking > basic: {score_break} <= {score_basic}"
    print(f"  calc_entry_importance_score(2, True, 0) = {score_break} > {score_basic} ✓")

    # walk_report hook sanity (CFP-1175)
    report = build_walk_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    if report is not None:
        assert report.walk_result == WalkResult.SUCCESS, f"sanity FAIL walk_report hook: {report}"
        print("  build_walk_completion_report() hook = SUCCESS ✓")
    else:
        print("  build_walk_completion_report() hook = None (walk_report 미설치, graceful degradation) ✓")

    print("sanity check PASS")
