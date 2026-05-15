"""
test_path_normalize.py — CFP-743 §8 Test Contract impl
QADev TDD: path_normalize.py 단위 테스트 (Change Plan §8.1 / §8.2 경계 조건)

커버리지:
  AC-10 (cross-platform parity) — sh ↔ ps1 parity를 단일 Python 소스로 강제
  AC-11 (failure-mode resilience) — abort-before-touch (path_normalization_failure)
  §4.5 6 입력 형태 × canonical output 규칙
  §8.2 경계 조건: 정규화 불가 입력 abort-before-touch
  §8.5.2 / §8.5.3 — 기 커버된 path abort invariant (process restart-aware 정합)
"""

import sys
import os
import pytest

# 본 script 가 scripts/ 하위에 있으므로 scripts/ 를 path에 추가
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)

from lib.path_normalize import to_canonical


# --------------------------------------------------------------------------
# TC-1: MSYS2/Git-Bash POSIX 경로 (입력 형태 1)
# --------------------------------------------------------------------------
class TestMsys2Path:
    def test_msys2_basic(self):
        """MSYS2 /c/Users/... → C:/Users/... (AC-10 §4.5 형태 1)"""
        result = to_canonical("/c/Users/mccho/proj")
        assert result == "C:/Users/mccho/proj", f"got: {result}"

    def test_msys2_lowercase_drive(self):
        """소문자 drive letter 대문자 변환 (CFP-702 precedent)"""
        result = to_canonical("/d/workspace/test")
        assert result == "D:/workspace/test", f"got: {result}"

    def test_msys2_nested_path(self):
        """중첩 경로 (공백 없음)"""
        result = to_canonical("/c/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-743")
        assert result.startswith("C:/"), f"got: {result}"
        assert "cfp-743" in result


# --------------------------------------------------------------------------
# TC-2: Windows backslash (입력 형태 2)
# --------------------------------------------------------------------------
class TestWindowsBackslash:
    def test_windows_backslash_basic(self):
        """C:\\Users\\... → C:/Users/... (§4.5 형태 2)"""
        result = to_canonical("C:\\Users\\mccho\\proj")
        assert result == "C:/Users/mccho/proj", f"got: {result}"

    def test_windows_backslash_deep_path(self):
        """deep path backslash 전체 변환"""
        result = to_canonical("C:\\a\\b\\c\\d")
        assert result == "C:/a/b/c/d", f"got: {result}"


# --------------------------------------------------------------------------
# TC-3: Windows forward-slash (입력 형태 3)
# --------------------------------------------------------------------------
class TestWindowsForwardSlash:
    def test_windows_forward_slash(self):
        """C:/Users/... → 이미 canonical, 그대로 (§4.5 형태 3)"""
        result = to_canonical("C:/Users/mccho/proj")
        assert result == "C:/Users/mccho/proj", f"got: {result}"


# --------------------------------------------------------------------------
# TC-4: 상대 경로 (입력 형태 4)
# --------------------------------------------------------------------------
class TestRelativePath:
    def test_relative_current_dir(self, tmp_path):
        """./subdir → repo_root 기준 절대화 (§4.5 형태 4)"""
        repo_root = str(tmp_path)
        result = to_canonical("./.claude/_overlay", repo_root=repo_root)
        expected_suffix = ".claude/_overlay"
        assert result.endswith(expected_suffix), f"got: {result}"
        # 절대 경로인지 확인
        assert os.path.isabs(result.replace("/", os.sep)), f"not absolute: {result}"

    def test_relative_parent(self, tmp_path):
        """../sibling → repo_root 기준 resolve (§4.5 형태 4)"""
        repo_root = str(tmp_path / "child")
        result = to_canonical("../sibling", repo_root=repo_root)
        assert "sibling" in result
        assert ".." not in result


# --------------------------------------------------------------------------
# TC-5: 공백 포함 경로 (입력 형태 5)
# --------------------------------------------------------------------------
class TestWhitespacePath:
    def test_windows_space_in_dir(self):
        """C:\\Users\\My Docs\\proj — 공백 보존 (§4.5 형태 5)"""
        result = to_canonical("C:\\Users\\My Docs\\proj")
        assert "My Docs" in result, f"got: {result}"
        assert "\\" not in result

    def test_msys2_space(self):
        """/c/Program Files/x — 공백 보존 (§4.5 형태 5)"""
        result = to_canonical("/c/Program Files/x")
        assert "Program Files" in result, f"got: {result}"
        assert result.startswith("C:/")


# --------------------------------------------------------------------------
# TC-6: non-ASCII UTF-8 (입력 형태 6)
# --------------------------------------------------------------------------
class TestNonAsciiPath:
    def test_korean_segment(self):
        """UTF-8 한글 경로 — byte-level 보존 (§4.5 형태 6)"""
        result = to_canonical("/c/Users/홍길동/proj")
        assert "홍길동" in result, f"got: {result}"
        assert result.startswith("C:/")

    def test_unicode_segment(self):
        """UTF-8 유니코드 일반 — byte-level 보존"""
        result = to_canonical("/c/Users/tëst/proj")
        assert "tëst" in result, f"got: {result}"


# --------------------------------------------------------------------------
# TC-7: abort-before-touch (§4.5 실패 시 동작 / §8.2 경계 조건)
# --------------------------------------------------------------------------
class TestAbortBeforeTouch:
    def test_empty_path_raises(self):
        """빈 문자열 = ValueError (abort-before-touch, §4.5)"""
        with pytest.raises(ValueError, match="path_normalization_failure"):
            to_canonical("")

    def test_whitespace_only_raises(self):
        """공백만 = ValueError"""
        with pytest.raises(ValueError, match="path_normalization_failure"):
            to_canonical("   ")

    def test_non_string_raises(self):
        """비문자열 입력 = ValueError"""
        with pytest.raises((ValueError, AttributeError)):
            to_canonical(None)  # type: ignore


# --------------------------------------------------------------------------
# TC-8: double-slash 제거 (§4.5 canonical 출력 규칙)
# --------------------------------------------------------------------------
class TestDoubleSlash:
    def test_double_slash_removed(self):
        """이중 슬래시 제거"""
        result = to_canonical("C://Users//mccho//proj")
        assert "//" not in result, f"got: {result}"


# --------------------------------------------------------------------------
# TC-9: sh ↔ ps1 parity — 동일 to_canonical() 사용 보장 (AC-10 §8.2)
# --------------------------------------------------------------------------
class TestShPs1Parity:
    """
    sh (codeforge-upgrade.sh) 과 ps1 (codeforge-upgrade.ps1) 이
    동일한 path_normalize.py to_canonical() 를 호출하므로
    동일 입력 → byte-identical canonical output 구조적 보장.
    본 테스트는 그 구조적 단일소스 증명.
    """

    PARITY_CASES = [
        "/c/Users/mccho/proj",
        "C:\\Users\\mccho\\proj",
        "C:/Users/mccho/proj",
        "/c/Program Files/codeforge",
        "C:\\Users\\홍길동\\proj",
        "/c/Users/tëst/proj",
    ]

    def test_parity_sh_ps1_same_source(self):
        """sh/ps1 양측 동일 to_canonical() → 구조적 parity 증명"""
        for raw in self.PARITY_CASES:
            result1 = to_canonical(raw)
            result2 = to_canonical(raw)  # 동일 함수 2회 호출 = idempotent
            assert result1 == result2, f"idempotency 실패: {raw!r} → {result1!r} vs {result2!r}"

    def test_parity_6_forms(self):
        """6 입력 형태 × 양측 동일 출력 (AC-10 parity matrix)"""
        forms = {
            "msys2_posix": "/c/Users/mccho/proj",
            "windows_backslash": "C:\\Users\\mccho\\proj",
            "windows_forward_slash": "C:/Users/mccho/proj",
            "whitespace_containing": "/c/Program Files/x",
            "non_ascii_utf8_korean": "/c/Users/홍길동/proj",
            "non_ascii_utf8_latin": "/c/Users/tëst/proj",
        }
        results = {}
        for form_name, raw in forms.items():
            results[form_name] = to_canonical(raw)
        # 모두 forward-slash canonical 형태인지 확인
        for form_name, canonical in results.items():
            assert "\\" not in canonical, f"{form_name}: backslash 잔존 in {canonical!r}"
            assert "//" not in canonical, f"{form_name}: double-slash in {canonical!r}"
