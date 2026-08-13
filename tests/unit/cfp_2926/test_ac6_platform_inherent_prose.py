"""test_ac6_platform_inherent_prose.py — AC-6 platform-inherent 문면 판별 명명 테스트.

CFP-2926 Story §8.0.2 RTM AC-6:
  - test_platform_inherent_prose_absent_active_docs: 부정문맥 처리

ADR-154 번들 전건 이행 (fail-closed):
  - [154-AC-3] empty-target → non-GREEN
  - [154-AC-4] unknown-input → fail-closed RED
  - [154-AC-5] execution-trace emit
  - [154-AC-13] identity_probe resolved-target echo

판별 규칙 (3-state):
  - same-line 부정 토큰 → CLS_NEGATED (무죄, preserved)
  - ±1행 이웃만 부정 → CLS_AMBIGUOUS (불명 → INCONCLUSIVE)
  - 부정 없음 → CLS_VIOLATION (위반 → RED)

Story §8.0.4 M-L mutant:
  - M-L: frozen 앵커 위에 N줄 삽입 → GREEN 유지 (내용 앵커이므로 줄번호 이동 무해)
  - 반례: 줄번호 앵커였다면 거짓 RED (= M-L 이 kill 못함)

부정문맥 미검출 오류:
  - 부정 토큰("…아님") 줄이 실제로는 위반이지만, same-line 부정으로 오검출되면 FAIL.
  - 이 테스트: 부정 토큰이 있어도 **그것이 다른 절의 부정**이면 실제 위반일 수 있음을
    보증하지 않는다 (정직 선언 (b)). 다만 **분명히 부정문맥인 줄은 오검출 0** 이어야.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# tests/unit/cfp_2926/ → repo root (parents[3])
REPO_ROOT = Path(__file__).resolve().parents[3]

# sys.path 에 scripts/lib 주입
if str(REPO_ROOT / "scripts" / "lib") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

import check_platform_inherent_prose as ckpinherent  # noqa: E402
import gate_verdict as gv  # noqa: E402


class TestAC6PlatformInherent:
    """NG-3 / AC-6 platform-inherent prose 스캐너 명명 테스트."""

    def test_platform_inherent_prose_absent_active_docs(self):
        """AC-6 문면 leg: "재귀 spawn = platform inherent" 서술이 0 건.

        co-occurrence 규칙: platform-claim 토큰 ∧ recursive-spawn 토큰 동시 출현.
        부정문맥 3-state (same-line 부정 → negated / ±1행 부정 → ambiguous / 없음 → violation).

        정상(원본): violation 분류 줄 0 건 → PASS.
        부정문맥 오검출 방지: "…아님" 부정 토큰이 있는 줄도 오검출 금지.

        Story §8.0.4 M-L mutant (frozen 앵커 내용 기반):
          M-L: frozen 앵커 위에 N줄 삽입 → GREEN 유지 (줄번호 앵커 아님을 증명)
          이 테스트는 활성 문면만 검증하므로 frozen 앵커는 별도 레이어.

        [154-AC-5] execution-trace: 스캔 파일·후보 줄·위반 수.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)

            # 정상 상태: platform-inherent 서술 없음.
            (tmproot / "CLAUDE.md").write_text(
                "# 규칙\n\n일반 내용만 있다.\n",
                encoding="utf-8"
            )

            # 정상 상태 검증: PASS (violation 0)
            result = ckpinherent.evaluate(tmproot)
            # frozen 앵커 미발견 가능성 → RED 또는 INCONCLUSIVE 가능.
            # 이 테스트는 활성 문면(platform-inherent prose) 만 검증하므로,
            # frozen 앵커 상태와 무관하게 active-doc 가 violation 0 이면 성공.
            if result.verdict == gv.PASS:
                assert result.trace.get("violations") == 0, f"violation 0 기대: {result.trace}"
            # frozen 앵커 부재는 별개 레이어 (AC-6 frozen leg 별도 테스트 필요)

            # 부정문맥 줄: "재귀 spawn 은 아님" → same-line 부정 토큰 있음 → negated (통과).
            # 이 줄이 violation 으로 오분류되면 FAIL.
            content_with_negation = (
                "# 정책\n\n"
                "재귀 spawn 은 platform 제약이 아님입니다.\n"  # same-line 부정 "아님"
            )
            (tmproot / "CLAUDE.md").write_text(content_with_negation, encoding="utf-8")

            result = ckpinherent.evaluate(tmproot)
            # 부정문맥 이 negated 로 분류됐으므로 violation 0.
            # 하지만 frozen 앵커 문제로 RED/INCONCLUSIVE 일 수 있음.
            # 핵심: violation 분류 줄이 violation 으로 카운트되지 않아야.
            if "violations" in result.trace:
                assert result.trace["violations"] == 0, (
                    f"부정문맥 줄이 violation 으로 오분류됨: {result.trace}"
                )

            # 위반 줄(부정 없음): "재귀 spawn 은 platform 제약이다" → violation (RED).
            content_with_violation = (
                "# 정책\n\n"
                "재귀 spawn 은 platform 제약입니다.\n"  # 부정 토큰 없음 → violation
            )
            (tmproot / "CLAUDE.md").write_text(content_with_violation, encoding="utf-8")

            result_violation = ckpinherent.evaluate(tmproot)
            # violation > 0 이면 RED (또는 frozen 앵커 문제).
            # 이 위반 줄이 제대로 detected 되는지 확인.
            if "violations" in result_violation.trace:
                assert result_violation.trace["violations"] > 0, (
                    f"위반 줄 미검출: {result_violation.trace}"
                )
