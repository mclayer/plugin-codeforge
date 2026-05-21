#!/usr/bin/env python3
# scripts/lib/walk_plan.py — CFP-1170 Phase 2
# walk + plan Python SSOT (ADR-061 외부 .py 의무)
#
# 책임 (change-plan §3.4 / §4.3):
#   (a) changelog walk — per-plugin CHANGELOG.md (from_version → to_version) 구간 entry enumerate
#   (b) min_prerequisite_version topological resolve — 7-plugin DAG topological sort + mismatch detection
#   (c) walk_result aggregate — bundle tier 7 plugin walk_result 종합 (deterministic exit code mapping)
#   (d) marker_merge — walk apply stage R-2 customization marker 보존 흡수 (reconcile-overlay.sh 흡수)
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 의무)
#   ADR-092 per-plugin self-owned CHANGELOG.md (walk source SSOT)
#   ADR-096 min_prerequisite_version manifest schema (topological resolve)
#   ADR-097 paradigm replacement (imperative walk)
#   ADR-027 §결정 7.D.3 customization marker whole-line anchored
#
# SSOT: docs/change-plans/cfp-1170-cli-walk-tier.md §3.4 / §4.3 / §11.2
# Contract: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §2.A/§2.E
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


# ──────────────────────────── WalkResult enum ─────────────────────────────────
# change-plan §4.3 / imperative-walker-protocol-v1 §2.A.1
# closed_set open_extension: false (ADR-093 §결정 2 — 5번째 enum 값 ad-hoc 확장 금지)

class WalkResult(Enum):
    """7-plugin family walk 결과 enum (4-value closed_set).

    ADR-093 §결정 2 — closed_set open_extension: false.
    5번째 값 ad-hoc 확장 금지 (별도 ADR 없이 확장 불가).
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

# topological order (ADR-096 §결정 2 DAG invariant: wrapper 먼저, 6 lane 후행)
# lane → wrapper 단방향 의존 (cycle 부재 — wrapper 최상위)
TOPOLOGICAL_ORDER = [
    "codeforge",           # wrapper (최상위, 6 lane 모두 의존)
    "codeforge-requirements",
    "codeforge-design",
    "codeforge-review",
    "codeforge-develop",
    "codeforge-test",
    "codeforge-pmo",
]


def get_topological_order() -> list[str]:
    """7-plugin family topological order 반환 (ADR-096 §결정 2 DAG invariant).

    [wrapper(codeforge), ...6 lane] — wrapper 먼저 resolve, cycle 부재.
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
    """bundle tier 7 plugin walk_result 종합 → family walk_result.

    deterministic exit code mapping (change-plan §4.3 / §4.4).

    severity ordering (고 → 저):
      FAILED > PARTIAL_FAILURE > SUCCESS_WITH_DEGRADATION > SUCCESS

    Rules:
      ANY FAILED          → FAILED (최상위 severity)
      ANY PARTIAL_FAILURE → PARTIAL_FAILURE
      ANY DEGRADATION     → SUCCESS_WITH_DEGRADATION
      ALL SUCCESS         → SUCCESS

    closed_enum open_extension: false (ADR-093 §결정 2).

    Raises:
        ValueError: per_plugin_results 가 빈 list (bundle tier = 7 plugin 전체 필수)
    """
    if not per_plugin_results:
        raise ValueError(
            "per_plugin_results 가 빈 list — bundle tier = 7 plugin 전체 walk_result 필요"
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


# ──────────────────────────── CLI entry point ─────────────────────────────────
# (참조용 — 실제 CLI 진입점은 walk-single-plugin.sh / walk-bundle-7-plugins.sh)

if __name__ == "__main__":
    # sanity check self-test (ADR-061 §결정 3 sanity check 3종 중 sample)
    print("walk_plan.py sanity check:")
    print(f"  TOPOLOGICAL_ORDER: {TOPOLOGICAL_ORDER}")
    print(f"  WalkResult values: {[r.value for r in WalkResult]}")
    print(f"  EXIT_CODE_MAP: { {k.value: v for k, v in EXIT_CODE_MAP.items()} }")

    # aggregate_walk_result sanity
    result = aggregate_walk_result([WalkResult.SUCCESS] * 7)
    assert result == WalkResult.SUCCESS, f"sanity FAIL: {result}"
    print("  aggregate_walk_result([SUCCESS]*7) = SUCCESS ✓")

    result = aggregate_walk_result([WalkResult.SUCCESS, WalkResult.FAILED])
    assert result == WalkResult.FAILED, f"sanity FAIL: {result}"
    print("  aggregate_walk_result([SUCCESS, FAILED]) = FAILED ✓")

    print("sanity check PASS")
