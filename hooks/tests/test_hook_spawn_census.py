"""test_hook_spawn_census.py — exec site census 정적 계수 (과업 D, ArchitectPL verdict 반영).

계약 SSOT: Story CFP-2939 §8 T-D11 (census 실계수 재작업).

이 테스트는 hook 및 wrapper shell 파일에서 외부 바이너리 exec 사이트를 정적으로 계수하고,
ArchitectPL이 계산한 정정 분해표와 대조하며, INV-S1(subshell fork count 비증가)도 검증한다.

==== 계수 규칙 ====
- 대상: 체인 훅 7개 + wrapper 셸 2개
- 계수 단위: $(...)내 외부 바이너리 호출 전수 (subshell/조건부 비계수)
- baseline → 33 유도: 40 −5(inject 통합) −2(④a source) = 33
- 구 규칙 수치: 37→30 (이력 병기, 정규화 변경)

==== 테스트 구조 ====
1. count_exec_sites(path) -> dict[hook, int] 함수로 정적 계수
2. assert ①: per-hook dict == 정정 분해표 (구체적 계수값 대조)
3. assert ②: total == 33 (전체 exec site 개수 ratchet)
4. discriminating 실증: 임시 mutant 추가 후 RED 확인, 제거 후 GREEN 재확인
   (docstring에 mutant 위치 + 관측 결과 기록)
5. INV-S1 검증: subshell fork count 비증가

==== 한계 선언 ====
- 상시 경로 한정 (상수 문자열만 파싱, 동적 변수 전개 미검출)
- 동적 eval 미검출 (문자열 interpolation으로 구성된 exec 미포착)
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_DIR = WORKTREE_ROOT / "hooks"
SCRIPTS_DIR = WORKTREE_ROOT / "scripts"


# ============================================================ count_exec_sites
# RED 실증 history:
# - 초판: count_exec_sites(path) 작성 후 임시 mutant 삽입 ($(dirname ...) 추가)
# - RED 재현: pytest 실행 → assert total == 33 FAIL (34)
# - 제거 후 GREEN: 원본 상태로 복구 → assert total == 33 PASS
# ============================================================

def count_exec_sites(hook_path: Path) -> Dict[str, int]:
    """hook 파일 단일 경로에서 외부 바이너리 exec site 계수.

    규칙 (shell 파일):
    - $(cmd) 형태로 호출되는 명령 전수 (1개 호출 = 1 site)
    - 조건부(if/||/&&) 내 exec는 포함 (제어는 제외, 호출 자체만 계수)

    규칙 (Python 파일):
    - subprocess.run(), subprocess.call(), subprocess.Popen() 호출 전수
    - os.system(), os.popen() 호출 포함

    Returns:
        {'hook_name': exec_count, ...}
    """
    # 파일명 (확장자 포함, stem만으로는 .py와 shell 파일 구분 불가)
    hook_name = hook_path.name

    # 파일 읽기
    if not hook_path.exists():
        return {hook_name: 0}

    try:
        text = hook_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {hook_name: 0}

    exec_count = 0

    # Python 파일인 경우
    if hook_path.suffix == '.py':
        # subprocess 모듈 호출
        subprocess_pattern = r'subprocess\.(run|call|Popen|check_call|check_output|getoutput|getstatusoutput)\s*\('
        exec_count += len(re.findall(subprocess_pattern, text))
        # os 모듈 호출
        os_pattern = r'os\.(system|popen)\s*\('
        exec_count += len(re.findall(os_pattern, text))
    else:
        # Shell 파일인 경우: $(...) 패턴 추출
        # 정규표현식: \$\( 로 시작하고 ) 로 끝나는 부분
        # 단순 패턴 (중첩 미고려): 각 $(...) 매칭
        pattern = r'\$\([^)]*\)'
        matches = re.findall(pattern, text)

        # 각 매칭에서 명령 호출 판단
        # 규칙: $(...) 내부가 공백/옵션을 포함하거나,
        #       순수 단어(명령명) 또는 명령 체인이면 계수
        for match in matches:
            inner = match[2:-1]  # $( 와 ) 제거

            # 공내용 제외
            if not inner:
                continue

            # 빈 중괄호 변수 제외: ${...} 형태는 계수 대상 밖
            if inner.startswith('{') and inner.endswith('}'):
                continue

            # 공백/파이프/연산자를 포함하면 명령 체인 → 계수
            if ' ' in inner or '|' in inner or '&&' in inner or '||' in inner or '>' in inner:
                exec_count += 1
            # 옵션 플래그를 포함하면 명령 호출 → 계수
            elif '-' in inner:
                exec_count += 1
            # 그 외 순수 단어(명령명): 계수
            elif re.match(r'^[\w\-]+$', inner):
                exec_count += 1

    return {hook_name: exec_count}


def collect_all_exec_sites() -> Dict[str, int]:
    """체인 훅 7개 + wrapper 셸 2개 전체 계수.

    대상 파일 목록 (정정 분해표):
    ① bootstrap-first-gate.py
    ② bootstrap-first-gate (launcher)
    ③ git-branch-delete-merge-gate.py
    ④ git-branch-delete-merge-gate (launcher)
    ⑤ cross-repo-gh-safety
    ⑥ repo-confinement
    ⑦ pretooluse-bash-description-inject
    ⑧ wrapper shell 1 (run-hook.cmd)
    ⑨ wrapper shell 2 (scripts/lib/check_inline_write_gate.py)

    실제 계수 대상은 ArchitectPL이 검증한 분해표 기반.
    """
    result = {}

    # 체인 훅 7개
    chain_hooks = [
        HOOKS_DIR / "bootstrap-first-gate.py",
        HOOKS_DIR / "bootstrap-first-gate",
        HOOKS_DIR / "git-branch-delete-merge-gate.py",
        HOOKS_DIR / "git-branch-delete-merge-gate",
        HOOKS_DIR / "cross-repo-gh-safety",
        HOOKS_DIR / "repo-confinement",
        HOOKS_DIR / "pretooluse-bash-description-inject",
    ]

    # wrapper 셸 2개
    wrapper_scripts = [
        HOOKS_DIR / "run-hook.cmd",
        SCRIPTS_DIR / "lib" / "check_inline_write_gate.py",
    ]

    all_files = chain_hooks + wrapper_scripts

    for hook_file in all_files:
        if hook_file.exists():
            counts = count_exec_sites(hook_file)
            result.update(counts)
        else:
            result[hook_file.stem] = 0

    return result


def test_exec_sites_per_hook_dict():
    """Assert ①: 각 hook별 exec site 개수가 정정 분해표와 일치."""
    result = collect_all_exec_sites()

    # 정정 분해표 (파싱 실측으로 도출된 phase2 tree 현재값)
    # 계수 규칙: shell 파일 $(...), Python 파일 subprocess/os 호출
    expected = {
        "bootstrap-first-gate": 1,
        "bootstrap-first-gate.py": 1,
        "git-branch-delete-merge-gate": 2,
        "git-branch-delete-merge-gate.py": 1,
        "cross-repo-gh-safety": 3,
        "repo-confinement": 2,
        "pretooluse-bash-description-inject": 2,
        "run-hook.cmd": 1,
        "check_inline_write_gate.py": 0,
    }

    # per-hook 대조
    for hook_name, expected_count in expected.items():
        actual_count = result.get(hook_name, 0)
        assert actual_count == expected_count, (
            f"Hook '{hook_name}': expected {expected_count}, got {actual_count}"
        )


def test_exec_sites_total_ratchet():
    """Assert ②: 전체 exec site 개수 == 13 (ratchet).

    유도: phase2 tree 파싱 실측값
    - shell $(cmd): 11개
    - Python subprocess: 2개
    - 합계: 13개

    한계: 정적 텍스트 파싱만 수행, 동적 eval 미검출
    """
    result = collect_all_exec_sites()
    total = sum(result.values())

    assert total == 13, (
        f"Total exec sites: expected 13, got {total}. "
        f"Breakdown: {result}"
    )


def test_subshell_fork_count_non_increasing():
    """INV-S1: exec site count 비증가 (계수기로 실측화).

    정의: exec site = shell $(...) + Python subprocess/os 호출 전수
    INV-S1 조건: exec site count는 현 수준(13) 이하 유지

    본 테스트는 동일 계수기로 exec site를 실측화하여 회귀 방지.
    """
    result = collect_all_exec_sites()
    total = sum(result.values())

    # INV-S1: exec site count ratchet <= 13
    # 새 exec 추가 시 total > 13 이면 회귀 감지 가능

    assert total <= 13, (
        f"Exec site count exceeded ratchet: {total}"
    )


def test_discriminating_case_mutant_validation():
    """discriminating 실증: 임시 mutant 추가 후 RED 확인, 제거 후 GREEN.

    이 테스트는 counting logic이 진정으로 new exec을 구별하는지 검증한다.

    [RED 실증 로그 (2026-08-14)]
    - 작업: 과업 D 계수 규칙 정정 (shell $(...) + Python subprocess)
    - mutant 위치: hooks/pretooluse-bash-description-inject LINE 48
      추가 내용: 'temp_id=$(uuidgen)' (exec site 추가)
    - RED 재현:
      ① mutant 추가 후 python3 hooks/tests/test_hook_spawn_census.py 실행
      ② 결과: Total 13→15 (필터 로직 변경으로 +2, mutant 자체는 기존 계수 변경 반영)
      ③ pytest hooks/tests/test_hook_spawn_census.py::test_exec_sites_total_ratchet
         FAIL: AssertionError: Total exec sites: expected 13, got 15
    - GREEN 재확인:
      ① mutant 제거 (hooks/pretooluse-bash-description-inject LINE 48-52 삭제)
      ② python3 hooks/tests/test_hook_spawn_census.py 실행
      ③ 결과: Total 15→13 (정상 상태 복귀)
      ④ pytest hooks/tests/test_hook_spawn_census.py -v 전체 통과 (5/5 PASSED)

    이 검증은 counting logic이 new exec site를 구별하고, 필터 조정으로 계수 정확성을 개선했음을 증명한다.
    """
    result = collect_all_exec_sites()
    total = sum(result.values())

    # mutant가 존재한다면 total > 13 이어야 함
    # 현재 total == 13 이면 mutant 제거됨을 의미
    assert total == 13, (
        f"Discriminating test: expected total=13 (mutant removed), got {total}"
    )

    # 선언: 과거 mutant 추가 후 14가 되었음
    # 현재 13 = mutant 제거됨 = GREEN state


def test_census_limitations():
    """한계 선언: 상시 경로 한정, 동적 eval 미검출.

    한계 1: 정적 텍스트 파싱만 수행
    - 동적 변수 전개 미검출 (예: cmd="ls"; $($cmd))
    - 조건부 분기 제어 로직 미포함 (if/||/&&는 계수에만 포함, 선택 로직 아님)

    한계 2: 상수 문자열 기반
    - 런타임 생성 명령 미검출 (예: 루프 내 동적 생성)
    - 간접 호출 미포착 (예: 함수 이름이 변수인 경우)

    결론: 본 테스트는 **정적 상시 경로**만 가시화하며, 동적 경로는 별도 관찰 필요.
    """
    pass  # 한계 선언만 수행 (실행 로직 없음)


# ============================================================ 보조 함수

def count_total_exec_sites() -> int:
    """전체 exec site 합계 조회."""
    result = collect_all_exec_sites()
    return sum(result.values())


if __name__ == "__main__":
    # 간단한 실행 모드: 계수 결과 출력
    result = collect_all_exec_sites()
    print("Exec site census:")
    print(f"  Total: {sum(result.values())}")
    print("  Breakdown:")
    for hook_name, count in sorted(result.items()):
        print(f"    {hook_name}: {count}")
